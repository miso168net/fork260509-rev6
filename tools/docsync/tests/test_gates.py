"""語料面：gates 名冊同源（區塊／錨形／ROSTER）、Day-1 到期即紅、GT-07 樣式與值比對、GT-09 對賬、GT-12 波標記與預算、run_lint 末行。
機密樣本一律執行期串接構造。"""
import json
import os
import re
import subprocess
import tempfile
import unittest
import unittest.mock

from docsync import gates, common, ROOT, RULES, NOTES, CONSTITUTION
from docsync.tests.test_book_ids import stub, errs, RULES_TEXT


def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", cwd, *args],
                          check=True, capture_output=True, text=True).stdout.strip()


def make_repo(files, exec_paths=()):
    root = tempfile.mkdtemp()
    _git(root, "init", "-q", "-b", "main")
    for rel, text in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p) or root, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
    _git(root, "add", "-A")
    for rel in exec_paths:
        _git(root, "update-index", "--chmod=+x", rel)
    _git(root, "commit", "-qm", "x")
    return root


_REAL_LINT = []


def real_lint():
    """真 repo `run_lint` 結果在模組層算一次、多個**純讀**案共用（各自對同一份 findings 下斷言、強度不變）。
    ★會改 `DAY1_EXEMPTIONS` 的案不得共用（那是另一組輸入、必須自己跑），故本函式只給不改模組狀態者。
    理由＝docsync 自測是 pre-commit 最長路徑（`.githooks/pre-commit` 檔頭 45 s WARN／90 s FAIL 錨、門檻調整走 ADR）；
    同一趟真 repo lint 跑三遍純屬重複。"""
    if not _REAL_LINT:
        _REAL_LINT.append(gates.run_lint(common.Ctx(ROOT)))
    return _REAL_LINT[0]


class TestRoster(unittest.TestCase):
    def test_blocks_anchors_roster_on_real_package(self):
        src = gates.package_sources()
        blocks = gates.parse_gate_blocks("\n".join(src.values()))
        self.assertEqual(sorted(blocks), [f"GT-{i:02d}" for i in range(1, 13)])
        for gid, b in blocks.items():
            self.assertEqual(sorted(b), sorted(gates.GATE_KEYS), gid)
        anchors = gates.derive_anchor_codes("\n".join(src.values()))
        self.assertTrue(anchors <= set(blocks))
        self.assertEqual(len(gates.ROSTER), 12)
        self.assertEqual({gates.gate_id(g) for g in gates.ROSTER}, set(blocks))

    def test_gate_id_survives_docstring_dedent(self):
        """區塊 regex 對「行首零空白」也須成立：Python ≥3.13 編譯期剝掉 docstring 共同縮排，
        上一個測案在 3.12 上恆綠、抓不到這面；本案以合成 __doc__ 釘死行為、與跑測的 python 版本無關。"""
        def g(ctx):
            pass
        g.__doc__ = "GATE:\nid=GT-42\nrule=RL-0000\n"
        self.assertEqual(gates.gate_id(g), "GT-42")
        self.assertEqual(sorted(gates.parse_gate_blocks("GATE:\n  id=GT-43\n")), ["GT-43"])

    def test_foreign_anchor_is_red(self):
        extra = "def x(ctx):\n    return [" + "finding(" + 'ERROR, "GT-' + '13", "w", "m")]\n'
        fs = gates.gt_12(stub({RULES: RULES_TEXT, NOTES: "<!-- wave: 1 -->\n"}), extra_sources={"x.py": extra})
        self.assertTrue(any("錨形" in f[3] and "GT-13" in f[3] for f in errs(fs)))


class TestDay1(unittest.TestCase):
    def test_released_but_still_registered_is_red(self):
        key = "GT-99.fake"
        gates.DAY1_EXEMPTIONS[key] = common.Day1Exemption(key, "樁", lambda ctx: True, "2026-09-03")
        try:
            fs, _ = gates.run_lint(common.Ctx(ROOT))
            self.assertTrue(any(key in f[3] and "到期" in f[3] for f in errs(fs)))
        finally:
            del gates.DAY1_EXEMPTIONS[key]

    def test_every_exemption_has_release_predicate_and_registered_date(self):
        for key, ex in gates.DAY1_EXEMPTIONS.items():
            self.assertTrue(callable(ex.released) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", ex.registered), key)
            self.assertTrue(key.startswith("GT-") and "." in key, key)


class TestGt07(unittest.TestCase):
    def test_selftest_patterns_and_value_compare(self):
        val = "s3cr3t" + "V4lue" + "XYZ"
        pem = "-----BEGIN " + "PRIVATE KEY-----"
        root = make_repo({"docs/a.md": "見 " + val + " 與 " + pem + "\n", "docs/b.md": "乾淨\n"})
        sdir = tempfile.mkdtemp()
        with open(os.path.join(sdir, "x.txt"), "w") as f:
            f.write(val + "\n")
        with open(os.path.join(sdir, "y.txt"), "w") as f:
            f.write("CHANGE-ME-" + "placeholder-1234\n")
        with open(os.path.join(sdir, "z.txt"), "w") as f:
            f.write("short\n")
        old = os.environ.get("SECRETS_DIR")
        os.environ["SECRETS_DIR"] = sdir
        try:
            fs = gates.gt_07(common.Ctx(root))
        finally:
            if old is None:
                del os.environ["SECRETS_DIR"]
            else:
                os.environ["SECRETS_DIR"] = old
        msgs = [f for f in errs(fs)]
        self.assertTrue(any("x" == f[3].split("「")[1].split("」")[0] and "docs/a.md" in f[2] for f in msgs if "機密現值" in f[3]))
        self.assertTrue(any("樣式" in f[3] and "docs/a.md" in f[2] for f in msgs))
        self.assertFalse(any(val in f[3] for f in fs))
        self.assertFalse(any("docs/b.md" in f[2] for f in msgs))
        self.assertFalse(any("「y」" in f[3] or "「z」" in f[3] for f in msgs))

    def test_secrets_dir_absent_is_named_skip(self):
        root = make_repo({"docs/a.md": "x\n"})
        old = os.environ.get("SECRETS_DIR")
        os.environ["SECRETS_DIR"] = os.path.join(root, "nope")
        try:
            fs = gates.gt_07(common.Ctx(root))
        finally:
            if old is None:
                del os.environ["SECRETS_DIR"]
            else:
                os.environ["SECRETS_DIR"] = old
        skips = [f for f in fs if f[0] == "SKIP"]
        self.assertTrue(skips and all(f[3].startswith("⤳ 跳過：") for f in skips), skips)
        self.assertTrue(any("GT-07.secrets-absent" in f[3] and "Day-1" not in f[3] for f in skips), skips)


class TestGt09(unittest.TestCase):
    SETTINGS = json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "sh .claude/hooks/s.sh"}]}]}})

    def test_readme_tree_two_way_exec_and_settings(self):
        readme = "# R\n\n```text\n.\n├── tools/\n│   ├── x.py\n│   └── z.py\n├── deploy/\n│   └── sops.sh\n└── .claude/\n    └── hooks/\n        └── s.sh\n```\n"
        root = make_repo({"README.md": readme, "tools/x.py": "1\n", "tools/y.py": "2\n", "deploy/sops.sh": "#!/bin/sh\n",
                          ".claude/settings.json": self.SETTINGS, ".claude/hooks/s.sh": "#!/bin/sh\n", ".claude/hooks/orphan.py": "1\n"})
        fs = errs(gates.gt_09(common.Ctx(root)))
        msgs = " ".join(f[3] + f[2] for f in fs)
        self.assertIn("tools/y.py", msgs)
        self.assertIn("tools/z.py", msgs)
        self.assertIn("deploy/sops.sh", msgs)
        self.assertIn("orphan.py", msgs)
        self.assertTrue(any("100755" in f[3] for f in fs))

    def test_green_and_hooks_absent_red(self):
        readme = "# R\n\n```text\n├── tools/\n├── deploy/\n└── .claude/\n    ├── settings.json\n    └── hooks/\n```\n"
        execs = ["deploy/sops.sh", "deploy/generate-age-key.sh", "deploy/generate-dev-cert.sh", "tools/bootstrap.sh"]
        files = {"README.md": readme, "tools/x.py": "1\n", ".claude/settings.json": self.SETTINGS, ".claude/hooks/s.sh": "#!/bin/sh\n"}
        files.update({e: "#!/bin/sh\n" for e in execs})
        root = make_repo(files, exec_paths=execs)
        fs = gates.gt_09(common.Ctx(root))
        self.assertEqual([f for f in errs(fs) if "deploy/sops.sh" in f[2] or "tools/" in f[2]], [])
        # 000-r2 修單：Day-1 型 SKIP 退場為 ERROR（.githooks／README 今日全在、分支已死）
        self.assertTrue(any(f[0] == "ERROR" and ".githooks" in f[3] and "缺席" in f[3] for f in fs), fs)
        self.assertFalse(any(f[0] == "SKIP" for f in fs))
        fs2 = gates.gt_09(common.Ctx(make_repo({"tools/x.py": "1\n"})))
        self.assertTrue(any(f[0] == "ERROR" and "README" in f[3] and "缺席" in f[3] for f in fs2), fs2)
        self.assertFalse(any(f[0] == "SKIP" for f in fs2))


class TestGt09OrchestrationRoster(unittest.TestCase):
    """GT-09 之編排骨架子名冊腿（ADR-00020）：tools/orchestration/ 頂層 tracked 檔集（README.md 除外）⇔ tools/orchestration/README.md
    檔表首欄反引號集、雙向差集即紅；零 orchestration 檔＝腿不跑；表缺席／零列＝掃描面空集合即紅（RL-0051）。"""
    README = "# R\n\n```text\n├── tools/\n│   └── orchestration/\n└── .claude/\n```\n"
    TABLE = "# orch\n\n| 檔 | 內容 |\n|---|---|\n| `_sk_head.js` | 首段 |\n| `assemble.py` | 組裝器 |\n"

    def _msgs(self, files):
        return [f for f in errs(gates.gt_09(common.Ctx(make_repo(files)))) if "檔表" in f[3]]

    def test_green_two_way(self):
        files = {"README.md": self.README, "tools/orchestration/README.md": self.TABLE,
                 "tools/orchestration/_sk_head.js": "1\n", "tools/orchestration/assemble.py": "1\n"}
        self.assertEqual(self._msgs(files), [])

    def test_missing_and_ghost_rows_red(self):
        table = self.TABLE.replace("| `assemble.py` | 組裝器 |\n", "| `ghost.mjs` | 幽靈 |\n")
        files = {"README.md": self.README, "tools/orchestration/README.md": table,
                 "tools/orchestration/_sk_head.js": "1\n", "tools/orchestration/assemble.py": "1\n"}
        msgs = " ".join(f[3] + " " + f[2] for f in self._msgs(files))
        self.assertIn("ghost.mjs", msgs)
        self.assertIn("幽靈列", msgs)
        self.assertIn("tools/orchestration/assemble.py", msgs)

    def test_table_absent_or_empty_red_and_no_files_silent(self):
        absent = {"README.md": self.README, "tools/orchestration/_sk_head.js": "1\n"}
        self.assertTrue(any("缺席" in f[3] for f in self._msgs(absent)))
        empty = {"README.md": self.README, "tools/orchestration/README.md": "# orch\n只有散文\n", "tools/orchestration/_sk_head.js": "1\n"}
        self.assertTrue(any("零列" in f[3] for f in self._msgs(empty)))
        self.assertEqual(self._msgs({"README.md": self.README, "tools/x.py": "1\n"}), [])


class TestGt09GeneratedMembers(unittest.TestCase):
    """GT-09 之 docs/generated 成員行對賬腿（BL-00009）：ROSTER_PREFIXES 不含 docs/，
    名冊 12→14 時該行歷來只能人工同刀改齊——001 刀 U3 連兩支審查 run 被此類漏改打回（LL-00002）。"""

    LINE = ("├── docs/generated/                  機器生成、嚴禁手改：STATE／MILESTONES／DECISIONS-INDEX／GATES"
            "／RAD-AI-MAP／reference/{ports,perf,rev5-blueprint-map,agents,schema,accounts}")

    def _parse(self, line):
        return gates.readme_generated_members("```text\n" + line + "\n```\n")

    def test_real_readme_matches_roster(self):
        from docsync import references, ROOT
        from docsync.common import Ctx
        declared = gates.readme_generated_members(Ctx(ROOT).text("README.md"))
        actual = {r[len("docs/generated/"):-3] for r in references.GENERATED_FILES
                  if r.startswith("docs/generated/") and r.endswith(".md")}
        self.assertEqual(declared, actual)

    def test_brace_expansion_and_slash_split(self):
        self.assertEqual(self._parse(self.LINE),
                         {"STATE", "MILESTONES", "DECISIONS-INDEX", "GATES", "RAD-AI-MAP",
                          "reference/ports", "reference/perf", "reference/rev5-blueprint-map",
                          "reference/agents", "reference/schema", "reference/accounts"})

    def test_missing_member_red(self):
        got = self._parse(self.LINE.replace("agents,", ""))
        self.assertNotIn("reference/agents", got)

    def test_ghost_member_and_absent_line(self):
        self.assertIn("GHOST", self._parse(self.LINE + "／GHOST"))
        self.assertIsNone(gates.readme_generated_members("```text\n├── tools/  x\n```\n"))


class TestGt12(unittest.TestCase):
    def _files(self, wave, rules_text=RULES_TEXT, extra=None):
        files = {RULES: rules_text, NOTES: f"<!-- wave: {wave} -->\n"}
        files.update(extra or {})
        return files

    def test_wave_lag_and_missing_wave_still_error(self):
        """波標記兩腿與預算無關、維持 ERROR（ADR-00011 只改預算腿嚴厲度）。"""
        fs = gates.gt_12(stub(self._files(5, extra={"specs/001-x/spec.md": "s\n"})))
        self.assertTrue(any("波標記落後" in f[3] for f in errs(fs)))
        self.assertTrue(any("波標記缺席" in f[3] for f in errs(gates.gt_12(stub({RULES: RULES_TEXT})))))

    def test_rules_budget_is_warn_only_at_any_wave(self):
        """ADR-00011：RULES per-scope 超上限一律 WARN、不再隨波轉 ERROR（波 6 為分界舊值）。"""
        over = RULES_TEXT.replace("上限（D8）：總 3", "上限（D8）：總 1")
        for wave in (1, 6, 9):
            fs = gates.gt_12(stub(self._files(wave, over)))
            self.assertTrue(any("RULES 總" in f[3] for f in fs if f[0] == "WARN"), wave)
            self.assertFalse(any("RULES 總" in f[3] for f in errs(fs)), wave)

    def test_gate_count_over_cap_is_warn_and_not_structural_error(self):
        """ADR-00011：閘數超上限只 WARN；結構斷言不再混入數量（舊碼以 len != BUDGET_GATES 無條件 ERROR）。"""
        with unittest.mock.patch.object(gates, "BUDGET_GATES", len(gates.ROSTER) - 1):
            fs = gates.gt_12(stub(self._files(6)))
        self.assertTrue(any("閘數" in f[3] and "超上限" in f[3] for f in fs if f[0] == "WARN"))
        self.assertFalse(any("區塊集合" in f[3] or "閘數 ≠" in f[3] for f in errs(fs)))

    def test_backlog_open_has_no_cap_leg(self):
        """ADR-00011：BACKLOG 開放為觀測值、不設上限——任何條數都不出 finding。"""
        from docsync import BACKLOG
        many = "<!-- next: BL-00099 -->\n" + "".join(f"- BL-{i:05d}｜governance｜x｜觸發：t\n" for i in range(1, 41))
        fs = gates.gt_12(stub(self._files(6, extra={BACKLOG: many})))
        self.assertEqual([f for f in fs if "BACKLOG 開放" in f[3]], [])
        self.assertFalse(hasattr(gates, "BUDGET_BACKLOG_OPEN"))

    def test_three_sources_red_when_absent_and_when_mismatch(self):
        fs = gates.gt_12(stub(self._files(1)))
        self.assertEqual([f for f in fs if f[0] == "SKIP"], [])   # 000-r2 修單：Day-1 型 SKIP 退場為 ERROR
        msgs0 = [f[3] for f in errs(fs)]
        self.assertTrue(any("pre-commit" in m and "缺席" in m and "空集合" in m for m in msgs0), msgs0)
        self.assertTrue(any("RUNBOOK" in m and "缺席" in m and "空集合" in m for m in msgs0), msgs0)
        bad = self._files(1, extra={".githooks/pre-commit": "#!/bin/sh\n# lint（GT-01～GT-11）\n", "docs/ops/RUNBOOK.md": "| GT-01 | x |\n"})
        msgs = [f[3] for f in errs(gates.gt_12(stub(bad)))]
        self.assertTrue(any("pre-commit" in m for m in msgs) and any("RUNBOOK" in m for m in msgs))
        # 002 刀 U0 起 RUNBOOK 多一腿（碼面閘表 ⇔ tools/ 頂層 *.py）：good 合成 RUNBOOK 須帶一張表、stub tracked 帶同一支工具，否則新腿判表缺席即紅
        good = self._files(1, extra={".githooks/pre-commit": "#!/bin/sh\n# lint（GT-01～GT-12）\n",
                                     "docs/ops/RUNBOOK.md": "| `lint` | GT-01～GT-12 |\n\n" + CODEGATE_TABLE_HEAD + "| `tools/x-gate.py` | x | y | z |\n"})
        self.assertEqual([f for f in errs(gates.gt_12(stub(good, tracked=list(good) + ["tools/x-gate.py"]))) if "pre-commit" in f[3] or "RUNBOOK" in f[3]], [])


CODEGATE_TABLE_HEAD = "| 工具檔 | 守什麼 | 觸發時機（含環境缺席語意） | 根據 ADR |\n|---|---|---|---|\n"
CODEGATE_TOOLS = ["tools/schema-gate.py", "tools/entity-drift-gate.py", "tools/rust-fmt-gate.py", "tools/wire-schema.py", "tools/fork-delta-lint.py"]


class TestGt12CodeGateTable(unittest.TestCase):
    """GT-12 碼面閘表腿（002 刀 U0；contracts/code-gates.md §3）：S_tools＝tools/ 頂層 tracked *.py − NON_GATE_TOOLS ⇔ S_table＝RUNBOOK 碼面閘表首欄反引號路徑集。
    每案問「把被守的那行改壞會不會紅」：斷言針對訊息字面（工具路徑＋方向）。"""

    def _runbook(self, tools=CODEGATE_TOOLS, note_row=True, table=True):
        rb = "| `lint` | GT-01～GT-12 |\n\n"
        if table:
            rb += CODEGATE_TABLE_HEAD
            for t in tools:
                rb += f"| `{t}` | 守 | 觸發 | ADR |\n"
            if note_row:
                rb += "| msg key 跨端閘 | 註記列（非路徑） | 延前端 i18n 刀 | ADR |\n"
        return rb

    def _run(self, rb, tracked_tools):
        files = {RULES: RULES_TEXT, NOTES: "<!-- wave: 6 -->\n", ".githooks/pre-commit": "#!/bin/sh\n# lint（GT-01～GT-12）\n", "docs/ops/RUNBOOK.md": rb}
        tracked = list(files) + list(tracked_tools) + ["tools/docsync/gates.py", "tools/orchestration/x.mjs", "tools/bootstrap.sh"]
        return [f[3] for f in errs(gates.gt_12(stub(files, tracked=tracked))) if "碼面閘" in f[3]]

    def test_five_rows_five_tools_plus_non_gate_is_green(self):
        msgs = self._run(self._runbook(), CODEGATE_TOOLS + list(gates.NON_GATE_TOOLS))
        self.assertEqual(msgs, [])
        self.assertIn("tools/wf-watchdog.py", gates.NON_GATE_TOOLS)

    def test_missing_row_is_red_and_names_tool(self):
        rows = [t for t in CODEGATE_TOOLS if t != "tools/wire-schema.py"]
        msgs = self._run(self._runbook(tools=rows), CODEGATE_TOOLS + list(gates.NON_GATE_TOOLS))
        self.assertTrue(any("tools/wire-schema.py" in m and "未列" in m for m in msgs), msgs)
        self.assertFalse(any("tools/schema-gate.py" in m for m in msgs), msgs)

    def test_ghost_row_is_red_and_names_tool(self):
        msgs = self._run(self._runbook(tools=CODEGATE_TOOLS + ["tools/ghost-gate.py"]), CODEGATE_TOOLS + list(gates.NON_GATE_TOOLS))
        self.assertTrue(any("tools/ghost-gate.py" in m and "幽靈" in m for m in msgs), msgs)

    def test_table_absent_is_red(self):
        msgs = self._run(self._runbook(table=False), CODEGATE_TOOLS)
        self.assertTrue(any("碼面閘表" in m and "缺席" in m for m in msgs), msgs)

    def test_table_with_zero_path_rows_is_red(self):
        msgs = self._run(self._runbook(tools=[]), CODEGATE_TOOLS)
        self.assertTrue(any("零" in m and "空集合" in m for m in msgs), msgs)

    def test_non_gate_constant_is_load_bearing(self):
        """NON_GATE_TOOLS 被清空→wf-watchdog 立刻被判「未列」；常數就是那條被守的線。"""
        with unittest.mock.patch.object(gates, "NON_GATE_TOOLS", ()):
            msgs = self._run(self._runbook(), CODEGATE_TOOLS + ["tools/wf-watchdog.py"])
        self.assertTrue(any("tools/wf-watchdog.py" in m and "未列" in m for m in msgs), msgs)

    def test_walkthrough_baseline_is_non_gate_and_green_without_table_row(self):
        """003 刀 U10a：走查對賬工具 tools/walkthrough-baseline.py（隨遷、非碼面閘）進 NON_GATE_TOOLS——
        真 repo 常數含它＋合成 tracked 含它＋RUNBOOK 碼面閘表不列它＝綠（列進表反而是幽靈列、見 ghost 案）。"""
        self.assertIn("tools/walkthrough-baseline.py", gates.NON_GATE_TOOLS)
        msgs = self._run(self._runbook(), CODEGATE_TOOLS + ["tools/walkthrough-baseline.py"])
        self.assertEqual(msgs, [])

    def test_walkthrough_baseline_dropped_from_non_gate_is_red_and_names_it(self):
        """反例：常數抽掉該檔（只剩 wf-watchdog）→GT-12 判該檔「未列於碼面閘表」、訊息指名；未被抽的成員不誤紅。"""
        with unittest.mock.patch.object(gates, "NON_GATE_TOOLS", ("tools/wf-watchdog.py",)):
            msgs = self._run(self._runbook(), CODEGATE_TOOLS + ["tools/walkthrough-baseline.py", "tools/wf-watchdog.py"])
        self.assertTrue(any("tools/walkthrough-baseline.py" in m and "未列" in m for m in msgs), msgs)
        self.assertFalse(any("tools/wf-watchdog.py" in m for m in msgs), msgs)

    def test_nested_and_non_py_tools_not_counted(self):
        """tools/docsync/*.py、tools/orchestration/*、tools/bootstrap.sh 皆非頂層 *.py——不進 S_tools、不誤紅。"""
        msgs = self._run(self._runbook(), CODEGATE_TOOLS + list(gates.NON_GATE_TOOLS) + ["tools/docsync/book.py", "tools/orchestration/_sk_core.js"])
        self.assertEqual(msgs, [])

    def test_real_runbook_table_matches_tracked_tools(self):
        """真 repo：RUNBOOK 碼面閘表首欄集 ＝ git ls-files tools/*.py − NON_GATE_TOOLS（U0 收尾＝五支）。"""
        ctx = common.Ctx(ROOT)
        s_tools = {p for p in ctx.tracked if p.startswith("tools/") and p.count("/") == 1 and p.endswith(".py")} - set(gates.NON_GATE_TOOLS)
        self.assertEqual(gates.runbook_codegate_tools(ctx.text("docs/ops/RUNBOOK.md")), s_tools)
        self.assertGreaterEqual(len(s_tools), 5)


class TestRunLint(unittest.TestCase):
    def test_real_repo_zero_errors_and_summary_format(self):
        fs, summary = real_lint()
        self.assertRegex(summary, r"^lint：\d+ 錯誤／\d+ 警告／\d+ 閘跳過$")
        self.assertEqual(errs(fs), [])

    def test_gates_md_prints_predicate_text_per_exemption(self):
        key = "GT-99.fake"
        gates.DAY1_EXEMPTIONS[key] = common.Day1Exemption(key, "樁", lambda ctx: False, "2026-09-03", "樁謂詞字面")
        try:
            out = gates.gen_gates_md(common.Ctx(ROOT))
            self.assertIn("| GT-99.fake | 樁 | 樁謂詞字面 | 2026-09-03 |", out)
            self.assertNotIn("檔／事件存在（見 gates.py）", out)
        finally:
            del gates.DAY1_EXEMPTIONS[key]

    def test_gates_md_has_roster_and_header(self):
        out = gates.gen_gates_md(common.Ctx(ROOT))
        self.assertTrue(out.startswith(common.GENERATED_HEADER))
        self.assertEqual(re.findall(r"^\| (GT-\d{2}) \|", out, re.M), [f"GT-{i:02d}" for i in range(1, 13)])

    def test_gt_01_self_description_covers_the_opts_scan_face(self):
        """gt_01 的 `face=` 是 GATES.md「掃描面」欄的唯一來源：check_generated 的第四腿掃的是
        tracked `tools/orchestration` 之 `*_OPTS` 字面，那批檔（`_sk_head.js`、`EXAMPLE-*.mjs`）除
        `_sk_rules.js` 外都不在 GENERATED_FILES 名冊——自述只寫名冊＝讀 GATES.md 的人無從得知
        改掉字面形會靜默縮小 GT-01 的掃描面，而那正是該腿要治的病（000-r2 修-CQ2）。"""
        b = gates.parse_gate_blocks(gates.gt_01.__doc__)["GT-01"]
        self.assertIn("_OPTS", b["face"])
        self.assertIn("_OPTS", b["breaks-if-removed"])
        self.assertIn("掃描面", b["drift"])
        self.assertIn("_OPTS", gates.gen_gates_md(common.Ctx(ROOT)))


class TestEnvSkipRegistry(unittest.TestCase):
    """000-r2 修單（BL-00003②）：SKIP 分支二分——Day-1 型退場為 ERROR、環境型留 SKIP 但登記 ENV_SKIPS（ADR-00019 具名跳過 rc 0）；
    GT-12 新腿斷言原始碼全部 SKIP 錨形鍵 ⊆ DAY1_EXEMPTIONS ∪ ENV_SKIPS。"""

    def test_env_skips_shape(self):
        self.assertEqual(sorted(gates.ENV_SKIPS), ["GT-02.submodule-absent", "GT-05.submodule-absent", "GT-07.secrets-absent", "GT-12.submodule-absent"])
        for k, v in gates.ENV_SKIPS.items():
            self.assertRegex(k, r"^GT-\d{2}\.[a-z0-9-]+$")
            self.assertEqual(len(v), 2)
            self.assertTrue(all(isinstance(x, str) and x.strip() for x in v), k)

    def test_all_source_skip_keys_are_registered(self):
        """正：真 package 原始碼的 SKIP 錨形鍵集恰＝三筆環境型、且全數登記。"""
        keys, anchorless = gates.derive_skip_keys("\n".join(gates.package_sources().values()))
        self.assertEqual(anchorless, 0)
        self.assertEqual(keys, set(gates.ENV_SKIPS))
        self.assertTrue(keys <= set(gates.DAY1_EXEMPTIONS) | set(gates.ENV_SKIPS))

    def test_unregistered_skip_key_is_red(self):
        """反：合成一支帶未登記 SKIP 鍵的原始碼→GT-12 指名該鍵。"""
        extra = ('def z(ctx):\n    return [' + 'finding(' + 'SKIP, "GT-05", "w", "GT-05.made-up-key：樁")]\n')
        fs = gates.gt_12(stub({RULES: RULES_TEXT, NOTES: "<!-- wave: 1 -->\n"}), extra_sources={"z.py": extra})
        self.assertTrue(any("GT-05.made-up-key" in f[3] and "未登記" in f[3] for f in errs(fs)), errs(fs))

    def test_skip_anchor_without_key_is_red(self):
        extra = ('def z(ctx):\n    return [' + 'finding(' + 'SKIP, "GT-05", "w", "沒有鍵的跳過")]\n')
        fs = gates.gt_12(stub({RULES: RULES_TEXT, NOTES: "<!-- wave: 1 -->\n"}), extra_sources={"z.py": extra})
        self.assertTrue(any("無 GT-NN.slug 鍵" in f[3] for f in errs(fs)), errs(fs))

    def test_run_lint_reports_no_unregistered_skip_on_real_repo(self):
        fs, _ = real_lint()
        self.assertEqual([f for f in fs if "未登記的 SKIP 鍵" in f[3]], [])

    def test_gates_md_has_no_bare_html_placeholder(self):
        """登記表的謂詞字面直接渲染進 GATES.md：裸角括號佔位符（如 <sub>）會被 GFM 當原生 HTML 標籤
        （`sub` 屬允許標籤、此處永不閉合，其後儲存格內容整段被當下標渲染）——佔位符一律反引號包或寫實名。"""
        out = gates.gen_gates_md(common.Ctx(ROOT))
        bare = [l for l in out.split("\n") if re.search(r"(?:^|[^`])<[a-zA-Z][a-zA-Z0-9]*>", l)]
        self.assertEqual(bare, [])

    def test_gates_md_has_env_skip_table(self):
        out = gates.gen_gates_md(common.Ctx(ROOT))
        self.assertIn("## 環境型跳過登記（鍵｜命中謂詞｜理由）", out)
        for k, (pred, reason) in gates.ENV_SKIPS.items():
            self.assertIn(f"| {k} | {pred} | {reason} |", out)


CLAUDE_STUB = ("★編排：fix 迴圈 for 上限 ≤3 輪；TDD 執行單元 agent 總數保險絲 ≤20 支、review 形每 run ≤24 支（＝25 減 1）。\n"
               "基線＝upstream `example` tip `8be6f9ba`；源倉 main `32c5254`。\n"
               "rev5 凍結 SHA：外層 `7eab28a`／base-web `9833308`／rust-api `92919b9`。\n")
# 憲法側樁比照真檔措辭（錨形認語境不認值：措辭走樣＝該處無人對賬，由槽外殘留腿指名）
CONST_STUB = "憲法：base-web 基線 SHA＝`8be6f9ba`、自源倉 main `32c5254` 起；rev5 樹凍結於 SHA `7eab28a`。\n"
BOOT_STUB = ('BASELINE_BRANCH="example";  BASEWEB_BASE_SHA="8be6f9ba"\n'
             'RUSTAPI_BASE_BRANCH="main"; RUSTAPI_BASE_SHA="32c5254"\n'
             'REV5_FROZEN=".:7eab28a base-web:9833308 rust-api:92919b9"\n')
SKHEAD_STUB = "const MAX_FIX_ROUNDS = 3\nconst MAX_AGENTS_PER_RUN = 24\n  AGENT_FUSE = Math.min(20, WORST + 1)\n"


class TestGt12ClaimReconcile(unittest.TestCase):
    """GT-12 之「數值／SHA 主張 ⇄ 工具常數」腿（BL-00003③、user 停點① 拍板：補既有閘腿、不占閘數）。
    ★兩側值一律唯讀讀檔＋正則取：不 import 編排骨架、不執行 js。"""

    def _files(self, claude=None, boot=None, head=None):
        return {RULES: RULES_TEXT, NOTES: "<!-- wave: 6 -->\n",
                "CLAUDE.md": CLAUDE_STUB if claude is None else claude,
                CONSTITUTION: CONST_STUB,
                "tools/bootstrap.sh": BOOT_STUB if boot is None else boot,
                "tools/orchestration/_sk_head.js": SKHEAD_STUB if head is None else head}

    def _msgs(self, **kw):
        return [f[2] + "｜" + f[3] for f in errs(gates.gt_12(stub(self._files(**kw)))) if "主張對賬" in f[3]]

    def test_green_synthetic(self):
        self.assertEqual(self._msgs(), [])

    def test_real_repo_claims_reconcile(self):
        self.assertEqual([f for f in errs(gates.gt_12(common.Ctx(ROOT))) if "主張對賬" in f[3]], [])

    def test_tool_side_sha_change_names_both_sides(self):
        bad = BOOT_STUB.replace('BASEWEB_BASE_SHA="8be6f9ba"', 'BASEWEB_BASE_SHA="deadbee1"')
        msgs = self._msgs(boot=bad)
        self.assertTrue(any("8be6f9ba" in m and "CLAUDE.md:2" in m for m in msgs), msgs)

    def test_tool_side_cap_change_names_both_sides(self):
        msgs = self._msgs(head=SKHEAD_STUB.replace("MAX_FIX_ROUNDS = 3", "MAX_FIX_ROUNDS = 5"))
        self.assertTrue(any("MAX_FIX_ROUNDS" in m and "≤3" in m and "5" in m for m in msgs), msgs)

    def test_missing_anchor_is_empty_face_red(self):
        msgs = self._msgs(claude="沒有任何主張字面。\n")
        self.assertTrue(any("空集合" in m for m in msgs), msgs)

    def test_swapped_pair_is_red_in_both_slots(self):
        """對調：base-web／rust-api 兩處凍結 SHA 互換——五值集合成員判定全綠，逐槽比值兩槽同時紅。"""
        msgs = self._msgs(claude=CLAUDE_STUB.replace("base-web `9833308`／rust-api `92919b9`",
                                                     "base-web `92919b9`／rust-api `9833308`"))
        self.assertTrue(any("rev5 base-web 凍結" in m and "`92919b9`" in m and "`9833308`" in m for m in msgs), msgs)
        self.assertTrue(any("rev5 rust-api 凍結" in m and "`9833308`" in m and "`92919b9`" in m for m in msgs), msgs)

    def test_deleted_claim_line_is_red_per_slot(self):
        """整行刪除：凍結主張整行拿掉——人寫面兩檔合計仍有 SHA 主張（舊腿只在合計為零時才紅），逐槽零命中才判得出來。"""
        claude = "\n".join(l for l in CLAUDE_STUB.split("\n") if "凍結 SHA" not in l)
        msgs = self._msgs(claude=claude)
        for slot in ("rev5 base-web 凍結", "rev5 rust-api 凍結"):
            self.assertTrue(any(slot in m and "零命中" in m for m in msgs), (slot, msgs))

    def test_wrong_slot_value_is_red(self):
        """張冠李戴：base-web 基線寫成 rev5 外層凍結 SHA——值仍在五值集內、集合判定全綠，逐槽指名兩側值。"""
        msgs = self._msgs(claude=CLAUDE_STUB.replace("tip `8be6f9ba`", "tip `7eab28a`"))
        self.assertTrue(any("base-web 基線" in m and "`7eab28a`" in m and "`8be6f9ba`" in m and "CLAUDE.md:2" in m for m in msgs), msgs)

    def test_reworded_claim_out_of_slot_is_red(self):
        """措辭改到錨形外＝該處無人對賬；槽外殘留腿指名（錨形隨人寫面演化的保命腿）。"""
        msgs = self._msgs(claude=CLAUDE_STUB.replace("基線＝upstream `example` tip", "基線＝上游最新之"))
        self.assertTrue(any("錨形外" in m and "`8be6f9ba`" in m for m in msgs), msgs)

    def test_non_claim_hex_literal_is_not_red(self):
        """反方向：非那五個值的反引號 hex（RULES-VERSION 值、commit SHA）不是基線／凍結主張、不得誤紅。"""
        self.assertEqual(self._msgs(claude=CLAUDE_STUB + "附註：RULES-VERSION `89ec0586d6a9`、commit `deadbeef1234`。\n"), [])

    def test_bootstrap_constant_set_must_match_slots(self):
        msgs = self._msgs(boot=BOOT_STUB.replace(" rust-api:92919b9", ""))
        self.assertTrue(any("REV5_FROZEN[rust-api]" in m and "不對應" in m for m in msgs), msgs)

    def test_every_slot_hits_the_real_face(self):
        """逐槽在真人寫面至少一命中——槽形與真檔措辭同步（零命中腿的正向自證）。"""
        ctx = common.Ctx(ROOT)
        texts = [t for t in (ctx.text(rel) for rel in gates.CLAIM_FACE) if t]
        for name, rx, const_name in gates.SHA_CLAIMS:
            self.assertTrue(any(rx.search(t) for t in texts), name)

    def test_fuse_slot_anchor_is_bound_to_the_constant_name(self):
        """保險絲槽以常數名為錨：`_sk_head.js` 在保險絲行之前多出任一個無關的 `Math.min(` 時，
        取值仍須落在 AGENT_FUSE 那行。★認「第一個 Math.min」＝與被控常數零語境綁定，
        與同檔自陳「錨形只認語境、不認值」矛盾（000-r2 修-CQ1）。"""
        noisy = "  const CHUNK = Math.min(3, xs.length)\n" + SKHEAD_STUB
        self.assertEqual(self._msgs(head=noisy), [])
        msgs = self._msgs(head=noisy.replace("Math.min(20, WORST + 1)", "Math.min(12, WORST + 1)"))
        self.assertTrue(any("保險絲" in m and "≤20" in m or "保險絲" in m and "12" in m for m in msgs), msgs)

    def test_fuse_slot_anchor_absent_is_red(self):
        """常數名錨形整個不在（改名／刪除）＝無對賬基準、照紅。"""
        msgs = self._msgs(head=SKHEAD_STUB.replace("AGENT_FUSE = Math.min(20,", "FUSE2 = Math.min(20,"))
        self.assertTrue(any("取不到" in m and "AGENT_FUSE" in m for m in msgs), msgs)

    def test_tool_file_absent_is_red(self):
        files = self._files()
        del files["tools/orchestration/_sk_head.js"]
        msgs = [f[2] + "｜" + f[3] for f in errs(gates.gt_12(stub(files))) if "主張對賬" in f[3]]
        self.assertTrue(any("_sk_head.js" in m for m in msgs), msgs)


class TestGt09PrefixAndTreeParsing(unittest.TestCase):
    """000-r2 L3-07（hooks_absent 前綴缺尾斜線、連帶豁免 .githooks-submodule/* 的 EXEC_REQUIRED）
    ／L3-08（README 樹「、」多檔行於深度 0 失去目錄前綴）。"""

    def test_hooks_absent_does_not_exempt_githooks_submodule(self):
        """`.githooks` 前綴會把 `.githooks-submodule/*` 一併吃掉，與同筆訊息「其餘 EXEC_REQUIRED 照驗」矛盾。"""
        fs = errs(gates.gt_09(common.Ctx(make_repo({"tools/x.py": "1\n"}))))
        named = " ".join(f[2] for f in fs if "EXEC_REQUIRED" in f[3])
        self.assertIn(".githooks-submodule/pre-commit", named)
        self.assertIn(".githooks-submodule/pre-push", named)
        self.assertNotIn(".githooks/pre-commit", named.replace(".githooks-submodule/pre-commit", ""))

    def test_depth_zero_multi_file_line_inherits_dir_prefix(self):
        tree = ("```text\n"
                "├── docs/ops/BACKLOG.md、BACKLOG-DEFERRED.md   兩卷\n"
                "├── docs/ops/LESSONS.md、LESSONS/   索引與一坑一檔\n"
                "├── docs/arc42/、docs/c4/、docs/compliance/   活書家族\n"
                "└── base-web/、rust-api/   兩 worktree\n"
                "```\n")
        paths, leaf_dirs = gates.readme_tree_paths(tree)
        self.assertIn("docs/ops/BACKLOG-DEFERRED.md", paths)
        self.assertNotIn("BACKLOG-DEFERRED.md", paths)
        self.assertIn("docs/ops/LESSONS/", paths)
        self.assertNotIn("LESSONS/", leaf_dirs)
        for d in ("docs/arc42/", "docs/c4/", "docs/compliance/", "base-web/", "rust-api/"):
            self.assertIn(d, paths, d)

    def test_real_readme_two_way_still_green(self):
        self.assertEqual([f for f in errs(gates.gt_09(common.Ctx(ROOT)))], [])


if __name__ == "__main__":
    unittest.main()


class TestSkipRegistrySingleAuthority(unittest.TestCase):
    """000-r2 修-CQ3：具名跳過的「登記集合」與「鍵抽取口徑」各只有一份權威——
    gt_12（靜態掃原始碼錨形）與 run_lint（執行期掃 SKIP 訊息）兩腿同取，不得各寫一份。"""

    def test_registered_skip_keys_is_the_union(self):
        self.assertEqual(gates.registered_skip_keys(), set(gates.DAY1_EXEMPTIONS) | set(gates.ENV_SKIPS))

    def test_both_legs_consume_the_single_registry(self):
        """把單一權威換掉（多登記一個鍵）→ 靜態腿與執行期腿**同時**閉嘴；
        任一腿仍自寫一份 `DAY1_EXEMPTIONS ∪ ENV_SKIPS` 即在此紅（日後加第三本登記時的靜默分叉）。"""
        fake = "GT-05.made-up-key"
        extra = {"z.py": 'def z(ctx):\n    return [' + 'finding(' + f'SKIP, "GT-05", "w", "{fake}：樁")]\n'}
        skip_f = [common.finding(common.SKIP, "GT-05", "w", f"{fake}：樁")]
        with unittest.mock.patch.object(gates, "registered_skip_keys",
                                        lambda: set(gates.DAY1_EXEMPTIONS) | set(gates.ENV_SKIPS) | {fake}):
            fs = gates.gt_12(stub({RULES: RULES_TEXT, NOTES: "<!-- wave: 1 -->\n"}), extra_sources=extra)
            self.assertEqual([f for f in errs(fs) if fake in f[3]], [])
            self.assertEqual(gates.unregistered_skip_warnings(skip_f), [])
        # 還原後兩腿都該重新指名（證明上面的靜默不是因為腿本身失效）
        fs = gates.gt_12(stub({RULES: RULES_TEXT, NOTES: "<!-- wave: 1 -->\n"}), extra_sources=extra)
        self.assertTrue([f for f in errs(fs) if fake in f[3]], errs(fs))
        self.assertTrue(gates.unregistered_skip_warnings(skip_f))

    def test_both_legs_pick_the_same_key_when_message_carries_two(self):
        """訊息交叉引用他閘跳過鍵（「同上：…」寫法的下一步）時，兩腿必取到同一鍵——
        取到不同鍵＝一個判已登記、一個判未登記，方向相反。"""
        msg = "GT-05.env-a：樁（同上：GT-07.env-b 亦跳過）"
        src = 'def z(ctx):\n    return [' + 'finding(' + f'SKIP, "GT-05", "w", "{msg}")]\n'
        keys, anchorless = gates.derive_skip_keys(src)
        self.assertEqual((keys, anchorless), ({"GT-05.env-a"}, 0))
        self.assertEqual(gates.skip_key_of(msg), "GT-05.env-a")
        warns = gates.unregistered_skip_warnings([common.finding(common.SKIP, "GT-05", "w", msg)])
        self.assertEqual([w[3] for w in warns], ["未登記的 SKIP 鍵 GT-05.env-a（須登記 DAY1_EXEMPTIONS 或 ENV_SKIPS）"])

    def test_window_cap_does_not_truncate_any_real_skip_site(self):
        """靜態面多一道 300 字元視窗（執行期面是訊息全文）：某支 SKIP 訊息一旦長到把鍵推出視窗，
        gt_12 判「錨形無鍵」而 run_lint 照樣找得到鍵。本案釘住真 package 現況零截斷。"""
        text = "\n".join(gates.package_sources().values())
        n = 0
        for m in gates.RE_SKIP_ANCHOR.finditer(text):
            n += 1
            nxt = text.find("finding(", m.end())
            stmt_end = len(text) if nxt < 0 else nxt
            capped = gates.skip_key_of(text, m.end(), min(stmt_end, m.end() + 300))
            whole = gates.skip_key_of(text, m.end(), stmt_end)
            self.assertEqual(capped, whole, f"視窗截斷：錨形 @{m.start()} 之鍵落在 300 字元外（{whole}）")
        self.assertEqual(n, len(gates.ENV_SKIPS))


class TestGt12Doorbell(unittest.TestCase):
    """BL-00121：門鈴頻道字面跨子庫同源腿——外層走查工具 tools/walkthrough-baseline.py 之 IPGATE_CHANNEL ⇔ rust-api
    server/src/ipgate/mod.rs 之 IPGATE_INVALIDATE_CHANNEL（子庫側取 HEAD 樹）。★落 GT-12（每 commit 必跑）而非該工具 self-test
    （只在工具本體 staged 時跑、rust 側改名時不跑＝假腿）；兩側值唯讀讀文＋正則取、不 import 工具。"""
    OUTER = 'X = 1\nIPGATE_CHANNEL = "ipgate:invalidate"\n'
    RUST = '/// 門鈴\npub const IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:invalidate";\n'

    def test_equal_is_green(self):
        self.assertEqual(gates._doorbell_findings(self.OUTER, self.RUST), [])

    def test_mismatch_names_both_values(self):
        fs = errs(gates._doorbell_findings(self.OUTER, self.RUST.replace("ipgate:invalidate", "ipgate:reload")))
        self.assertEqual(len(fs), 1, fs)
        self.assertTrue("ipgate:invalidate" in fs[0][3] and "ipgate:reload" in fs[0][3], fs)

    def test_missing_anchor_on_either_side_is_red(self):
        self.assertTrue(any("命中 0 處" in f[3] for f in errs(gates._doorbell_findings("X = 1\n", self.RUST))))
        self.assertTrue(any("命中 0 處" in f[3] for f in errs(gates._doorbell_findings(self.OUTER, "// moved\n"))))

    def test_outer_absent_is_red_and_submodule_absent_is_named_skip(self):
        base = {RULES: RULES_TEXT, NOTES: "<!-- wave: 6 -->\n"}
        self.assertTrue(any("walkthrough-baseline.py 缺席" in f[3] for f in errs(gates.gt_12(stub(base)))))
        fs = gates.gt_12(stub(dict(base, **{"tools/walkthrough-baseline.py": self.OUTER})))
        self.assertTrue(any(f[0] == "SKIP" and "GT-12.submodule-absent" in f[3] for f in fs), fs)

    def test_real_repo_doorbell_reconciles(self):
        self.assertEqual([f for f in errs(gates.gt_12(common.Ctx(ROOT))) if "門鈴字面對賬" in f[3]], [])

