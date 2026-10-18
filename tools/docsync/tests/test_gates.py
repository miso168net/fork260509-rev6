"""語料面：gates 名冊同源（區塊／錨形／ROSTER）、Day-1 到期即紅、GT-07 樣式與值比對、GT-09 對賬、GT-12 波標記與預算、run_lint 末行。
機密樣本一律執行期串接構造。"""
import json
import os
import re
import tempfile
import unittest
import unittest.mock

from docsync import gates, common, ROOT, RULES, NOTES, CONSTITUTION
from docsync.tests import tmprepo
from docsync.tests.test_book_ids import stub, errs, RULES_TEXT
from docsync.tests.tmprepo import make_repo


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
            # 本案只驗 run_lint 尾端的 Day-1 到期迴圈：閘名冊換空（整趟真 repo 閘另由 real_lint() 承擔；drvfs 上一趟約 25 秒）
            with unittest.mock.patch.object(gates, "ROSTER", ()):
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
            fs = gates.gt_07(tmprepo.Ctx(root))
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
            fs = gates.gt_07(tmprepo.Ctx(root))
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
        fs = errs(gates.gt_09(tmprepo.Ctx(root)))
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
        fs = gates.gt_09(tmprepo.Ctx(root))
        self.assertEqual([f for f in errs(fs) if "deploy/sops.sh" in f[2] or "tools/" in f[2]], [])
        # 000-r2 修單：Day-1 型 SKIP 退場為 ERROR（.githooks／README 今日全在、分支已死）
        self.assertTrue(any(f[0] == "ERROR" and ".githooks" in f[3] and "缺席" in f[3] for f in fs), fs)
        self.assertFalse(any(f[0] == "SKIP" for f in fs))
        fs2 = gates.gt_09(tmprepo.Ctx(make_repo({"tools/x.py": "1\n"})))
        self.assertTrue(any(f[0] == "ERROR" and "README" in f[3] and "缺席" in f[3] for f in fs2), fs2)
        self.assertFalse(any(f[0] == "SKIP" for f in fs2))


class TestGt09OrchestrationRoster(unittest.TestCase):
    """GT-09 之編排骨架子名冊腿（ADR-00020）：tools/orchestration/ 頂層 tracked 檔集（README.md 除外）⇔ tools/orchestration/README.md
    檔表首欄反引號集、雙向差集即紅；零 orchestration 檔＝腿不跑；表缺席／零列＝掃描面空集合即紅（RL-0051）。"""
    README = "# R\n\n```text\n├── tools/\n│   └── orchestration/\n└── .claude/\n```\n"
    TABLE = "# orch\n\n| 檔 | 內容 |\n|---|---|\n| `_sk_head.js` | 首段 |\n| `assemble.py` | 組裝器 |\n"

    def _msgs(self, files):
        return [f for f in errs(gates.gt_09(tmprepo.Ctx(make_repo(files)))) if "檔表" in f[3]]

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
        fs = errs(gates.gt_09(tmprepo.Ctx(make_repo({"tools/x.py": "1\n"}))))
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
    （只在工具本體 staged 時跑、rust 側改名時不跑＝假腿）；兩側值唯讀讀文＋正則取、不 import 工具。
    子庫在場之兩案（`_sub_ctx` 樁）：判定依 HEAD 樹而非工作樹（兩面取值相反、改讀工作樹即紅）；HEAD 樹取不到＝紅、指名子庫檔路徑。
    兩錨之行首判準與值字元類排除 `"` 一案；名字面、名界、`=` 判準（兩側各釘）、rust 收尾 `";` 與值非空一案；兩錨必含字面逐 token
    刪一之誘餌（任一字面改為可省即紅）一案；外層錨 `=` 兩側 `\\s*` 之零空白照取與容換行一案；rust 側宣告改寫（無可見性、`pub(crate)`、
    `pub static`、`&'static str`）＝錨形零命中＝紅一案（錨形放寬即轉綠）。"""
    OUTER = 'X = 1\nIPGATE_CHANNEL = "ipgate:invalidate"\n'
    RUST = '/// 門鈴\npub const IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:invalidate";\n'

    @staticmethod
    def _sub_ctx(outer, rel, head, work):
        """rust-api 在場之樁（`rust-api/.git` 存在＝exists 成立）：`git show HEAD:<rel>`（cwd＝子庫）回 (0, head)，head 為 None 則沿樁
        預設 (128, "")；工作樹面 `rust-api/<rel>` 讀 work。兩類共用。"""
        c = stub({gates.WALKTHROUGH: outer, "rust-api/.git": "gitdir: x\n", f"rust-api/{rel}": work})
        base = c.git_try

        def git_try(*a, cwd=None):
            if head is not None and a == ("show", f"HEAD:{rel}") and cwd == os.path.join(c.root, "rust-api"):
                return 0, head
            return base(*a, cwd=cwd)
        c.git_try = git_try
        return c

    def test_equal_is_green(self):
        self.assertEqual(gates._doorbell_findings(self.OUTER, self.RUST), [])

    def test_mismatch_names_both_values(self):
        fs = errs(gates._doorbell_findings(self.OUTER, self.RUST.replace("ipgate:invalidate", "ipgate:reload")))
        self.assertEqual(len(fs), 1, fs)
        self.assertTrue("ipgate:invalidate" in fs[0][3] and "ipgate:reload" in fs[0][3], fs)

    def test_missing_anchor_on_either_side_is_red(self):
        self.assertTrue(any("命中 0 處" in f[3] for f in errs(gates._doorbell_findings("X = 1\n", self.RUST))))
        self.assertTrue(any("命中 0 處" in f[3] for f in errs(gates._doorbell_findings(self.OUTER, "// moved\n"))))

    def test_multiple_anchors_on_either_side_is_red(self):
        """「多命中皆 ERROR」那格的自證（review L1-3）：把判準削成只擋零命中，本案須紅。"""
        self.assertTrue(any("命中 2 處" in f[3] for f in errs(gates._doorbell_findings(self.OUTER + 'IPGATE_CHANNEL = "x"\n', self.RUST))))
        self.assertTrue(any("命中 2 處" in f[3] for f in errs(gates._doorbell_findings(self.OUTER, self.RUST * 2))))

    def test_outer_absent_is_red_and_submodule_absent_is_named_skip(self):
        base = {RULES: RULES_TEXT, NOTES: "<!-- wave: 6 -->\n"}
        self.assertTrue(any("門鈴字面對賬：tools/walkthrough-baseline.py 缺席" in f[3] for f in errs(gates.gt_12(stub(base)))))
        fs = gates.gt_12(stub(dict(base, **{"tools/walkthrough-baseline.py": self.OUTER})))
        self.assertTrue(any(f[0] == "SKIP" and "GT-12.submodule-absent" in f[3] for f in fs), fs)

    def test_anchor_line_start_and_value_quote_exclusion(self):
        """兩錨之行首判準與值字元類排除 `"`：不計＝外層縮排之區域賦值與屬性賦值、rust 側註解行與縮排宣告（行首判準擋）；
        值取首對引號之間——行尾註解另帶引號者照取正值（字元類排除 `"` 擋貪婪吞到註解）。"""
        for outer in (self.OUTER + '    IPGATE_CHANNEL = "x"\n', self.OUTER + 'wb.IPGATE_CHANNEL = "x"\n',
                      'IPGATE_CHANNEL = "ipgate:invalidate"  # 舊值 "ipgate:reload"\n'):
            with self.subTest(outer=outer):
                self.assertEqual(gates._doorbell_findings(outer, self.RUST), [])
        for rust in (self.RUST + '// pub const IPGATE_INVALIDATE_CHANNEL: &str = "x";\n',
                     self.RUST + 'mod m {\n    pub const IPGATE_INVALIDATE_CHANNEL: &str = "x";\n}\n',
                     'pub const IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:invalidate"; // 舊值 "ipgate:reload";\n'):
            with self.subTest(rust=rust):
                self.assertEqual(gates._doorbell_findings(self.OUTER, rust), [])

    def test_anchor_name_boundary_terminator_and_nonempty(self):
        """兩錨之名字面、名界、`=` 判準、rust 收尾 `";` 與值非空：不計（皆照綠）＝他名常數（`NOTIFY_CHANNEL`；名字面擋）、
        同前綴之他名（`IPGATE_CHANNEL_OLD`、`IPGATE_INVALIDATE_CHANNEL_OLD`；名界擋＝名後不得接字元）、行首名後不接 `=` 之文字
        （外層三引號字串內 `IPGATE_CHANNEL "ipgate:reload"`、rust 區塊註解內 `IPGATE_INVALIDATE_CHANNEL: &str  "ipgate:reload";`；
        `=` 判準擋——單停分兩途徑：可省＝計成第二錨、命中 2 處；刪去＝基準錨失配、誘餌成唯一錨而落值不符，兩途徑皆紅）、
        區塊註解內無 `;` 收尾之殘句（收尾 `";` 擋）；
        值為空字串＝該側錨形零命中＝紅（不落成值不符之訊息）。"""
        for outer in (self.OUTER + 'NOTIFY_CHANNEL = "ipgate:reload"\n', self.OUTER + 'IPGATE_CHANNEL_OLD = "ipgate:reload"\n',
                      self.OUTER + '"""\nIPGATE_CHANNEL "ipgate:reload" 為舊頻道\n"""\n'):
            with self.subTest(outer=outer):
                self.assertEqual(gates._doorbell_findings(outer, self.RUST), [])
        for rust in (self.RUST + 'pub const NOTIFY_CHANNEL: &str = "ipgate:reload";\n',
                     self.RUST + 'pub const IPGATE_INVALIDATE_CHANNEL_OLD: &str = "ipgate:reload";\n',
                     self.RUST + '/*\npub const IPGATE_INVALIDATE_CHANNEL: &str  "ipgate:reload";\n*/\n',
                     self.RUST + '/*\npub const IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:reload" 為舊值\n*/\n'):
            with self.subTest(rust=rust):
                self.assertEqual(gates._doorbell_findings(self.OUTER, rust), [])
        for outer, rust, want in (('IPGATE_CHANNEL = ""\n', self.RUST, "門鈴字面對賬：IPGATE_CHANNEL 錨形命中 0 處"),
                                  (self.OUTER, 'pub const IPGATE_INVALIDATE_CHANNEL: &str = "";\n',
                                   "門鈴字面對賬：IPGATE_INVALIDATE_CHANNEL 錨形命中 0 處")):
            with self.subTest(outer=outer, rust=rust):
                fs = errs(gates._doorbell_findings(outer, rust))
                self.assertEqual(len(fs), 1, fs)
                self.assertIn(want, fs[0][3])

    def test_anchor_required_tokens_deleted_one_at_a_time(self):
        """兩錨必含字面逐 token 刪一之誘餌＝不計（皆照綠）；任一字面改為可省即誘餌計成第二錨、命中 2 處＝紅。
        外層（三引號字串內、置於檔尾——值字元類 `[^"]` 跨行，誘餌之後不得再有引號）：名字面、值首引號、值閉引號各刪一
        （`=` 刪去之誘餌住 test_anchor_name_boundary_terminator_and_nonempty；值刪去＝空字串、零命中案同住該案；`=` 兩側空白屬 `\\s*`、
        刪去仍合錨形＝非必含）。
        rust（區塊註解內）：`pub const IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:reload";` 之 16 個 token（字詞、各單一空格、`:`、`&`、
        `=`、兩引號、值、`;`）逐一刪去，另 `pub `、`const `、`pub const `、`: &str` 四段整段刪去（可見性、`const`、兩者合段與型別註記
        可省之途徑）。"""
        for outer in (' = "ipgate:reload"', 'IPGATE_CHANNEL = ipgate:reload"', 'IPGATE_CHANNEL = "ipgate:reload'):
            with self.subTest(outer=outer):
                self.assertEqual(gates._doorbell_findings(self.OUTER + "'''\n" + outer + "\n'''\n", self.RUST), [])
        toks = ("pub", " ", "const", " ", "IPGATE_INVALIDATE_CHANNEL", ":", " ", "&", "str", " ", "=", " ", '"', "ipgate:reload", '"', ";")
        decoys = ["".join(toks[:i] + toks[i + 1:]) for i in range(len(toks))]
        decoys += ['const IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:reload";', 'pub IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:reload";',
                   'IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:reload";', 'pub const IPGATE_INVALIDATE_CHANNEL = "ipgate:reload";']
        self.assertEqual(len(set(decoys)), 20)
        for rust in decoys:
            with self.subTest(rust=rust):
                self.assertEqual(gates._doorbell_findings(self.OUTER, self.RUST + "/*\n" + rust + "\n*/\n"), [])

    def test_rust_declaration_rewritten_is_red(self):
        """rust 側宣告改寫＝錨形命中 0 處＝紅、恰一筆、帶腿標籤（rust 側形變須同批改本腿；錨形放寬即轉綠）：無可見性（`const`）、
        `pub(crate)`、`pub static`、`&'static str`。"""
        for rust in ('const IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:invalidate";\n',
                     'pub(crate) const IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:invalidate";\n',
                     'pub static IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:invalidate";\n',
                     "pub const IPGATE_INVALIDATE_CHANNEL: &'static str = \"ipgate:invalidate\";\n"):
            with self.subTest(rust=rust):
                fs = errs(gates._doorbell_findings(self.OUTER, rust))
                self.assertEqual(len(fs), 1, fs)
                self.assertIn("門鈴字面對賬：IPGATE_INVALIDATE_CHANNEL 錨形命中 0 處", fs[0][3])

    def test_outer_equals_whitespace_zero_and_line_break(self):
        """外層錨 `=` 兩側之 `\\s*`：零空白（`IPGATE_CHANNEL="…"`）照取＝綠——任一側改為恰一個空白類字元即錨形零命中＝紅；
        容換行——三引號字串內名與 `=` 之間、或 `=` 與值之間折行之句照計成第二錨＝命中 2 處（只會誤紅、遮不掉真值；任一側收窄成
        `[ \\t]*` 即不計而轉綠）。"""
        self.assertEqual(gates._doorbell_findings('IPGATE_CHANNEL="ipgate:invalidate"\n', self.RUST), [])
        for decoy in ('IPGATE_CHANNEL\n= "ipgate:reload"', 'IPGATE_CHANNEL =\n"ipgate:reload"'):
            with self.subTest(decoy=decoy):
                fs = errs(gates._doorbell_findings(self.OUTER + '"""\n' + decoy + '\n"""\n', self.RUST))
                self.assertEqual(len(fs), 1, fs)
                self.assertIn("門鈴字面對賬：IPGATE_CHANNEL 錨形命中 2 處", fs[0][3])

    def test_submodule_present_judges_head_tree_not_worktree(self):
        """子庫在場＝判 HEAD 樹、未 commit 改動不入判：HEAD 樹值與外層不符而工作樹相符＝紅（指名 HEAD 樹之值）；反之 HEAD 相符而
        工作樹不符＝綠。實作改讀工作樹＝兩向皆翻。"""
        reload = self.RUST.replace("ipgate:invalidate", "ipgate:reload")
        fs = errs(gates._doorbell_leg(self._sub_ctx(self.OUTER, gates.DOORBELL_RUST, head=reload, work=self.RUST)))
        self.assertEqual(len(fs), 1, fs)
        self.assertIn("門鈴字面對賬：外層 IPGATE_CHANNEL＝「ipgate:invalidate」≠ rust-api IPGATE_INVALIDATE_CHANNEL＝「ipgate:reload」", fs[0][3])
        self.assertEqual(gates._doorbell_leg(self._sub_ctx(self.OUTER, gates.DOORBELL_RUST, head=self.RUST, work=reload)), [])

    def test_submodule_head_tree_unreadable_is_red_naming_path(self):
        """子庫在場而 `git show HEAD:<檔>` rc≠0＝紅、恰一筆、指名子庫檔路徑與 rc（不得落成錨形零命中之訊息）。"""
        fs = errs(gates._doorbell_leg(self._sub_ctx(self.OUTER, gates.DOORBELL_RUST, head=None, work=self.RUST)))
        self.assertEqual(len(fs), 1, fs)
        self.assertEqual(fs[0][2], f"rust-api/{gates.DOORBELL_RUST}")
        self.assertIn(f"門鈴字面對賬：子庫 HEAD 樹取不到 {gates.DOORBELL_RUST}（git show rc=128）", fs[0][3])

    def test_real_repo_doorbell_reconciles(self):
        self.assertEqual([f for f in errs(gates.gt_12(common.Ctx(ROOT))) if "門鈴字面對賬" in f[3]], [])


REDIS_TAG = "redis 前綴對賬"   # 本腿全部訊息共有的字面


class TestGt12RedisPrefixes(unittest.TestCase):
    """redis 清理前綴名冊跨子庫同源腿——外層走查工具 tools/walkthrough-baseline.py 之 RESTORE_REDIS_PREFIXES ⇔ rust-api
    server/src/cache/mod.rs 之鍵前綴（鍵字面首段＋`*_PREFIX` 常數首段；子庫側取 HEAD 樹）。形同門鈴腿：落 GT-12、兩側唯讀讀文＋正則取。
    子庫在場之兩案同門鈴腿（共用 `TestGt12Doorbell._sub_ctx` 樁）：判定依 HEAD 樹而非工作樹；HEAD 樹取不到＝紅、指名子庫檔路徑。
    外層錨之元組字串字元類排除逐條（重複段與末段各釘）、左右括號分釘、元素間逗號、名界、`=` 判準與其兩側不容換行、行尾註解不跨行
    一案；rust 兩錨首段字元類排除逐條與首段非空一案；rust 兩錨必含字面逐 token 刪一之誘餌、`format!` 非圓括號定界與 `!` 後帶空白、
    常數值不以 `"` 起首（皆不取）一案；`*_PREFIX` 名界（`_PREFIX` 後須接 `:`）與名字元類
    （數字照取、`_PREFIX` 之前可空；小寫、非 ASCII、`r#` 不取）釘於 rust 錨形一案；常數宣告於 `=` 之前
    折行之途徑一案、同行空格／tab 異於錨形之途徑一案、同行空白判準之多空格／tab／零空白照取一案；外層錨空白判準之零空白、tab、
    元素閉引號後折行（重複段與末段）與右括號後 tab 照取一案；外層元組元素首尾引號（重複段與末段）缺一之誘餌一案。
    射程外釘兩案：外層錨形行恰一處而模組層另有不合錨形之再綁定（非字面與不合錨形之字面）＝照綠；錨形行為單元素而無尾逗號
    （Python 實值為字串）照計＝照綠（皆判不出）。"""
    OUTER = 'X = 1\nRESTORE_REDIS_PREFIXES = ("session", "throttle", "cpwd")\n'
    RUST = ('//! 鍵族：`session:denylist:{sid}`／`cpwd:{uid}`；本檔是全 crate 唯一的鍵渲染點、他處不得自 `format!` 拼鍵\n'
            'fn denylist_key(sid: &str) -> String {\n    format!("session:denylist:{sid}")\n}\n'
            'fn last_activity_key(sid: &str) -> String {\n    format!("session:{sid}:last_activity")\n}\n'
            'pub fn throttle_unlock_ip_key(bucket: IpNetwork) -> String {\n'
            '    format!("throttle:unlock:{}:{bucket}", crate::throttle::DIM_IP)\n}\n'
            'pub const CHANGE_PWD_KEY_PREFIX: &str = "cpwd:";\n'
            'pub fn change_pwd_key(uid: i64) -> String {\n    format!("{CHANGE_PWD_KEY_PREFIX}{uid}")\n}\n'
            '#[cfg(test)]\nmod tests {\n    fn t() {\n        let k = format!("{}:gs", uniq_prefix());\n'
            '        let h = format!("cmdstat_{command}:calls=");\n    }\n}\n')

    def _one(self, outer, rust):
        fs = errs(gates._redis_prefix_findings(outer, rust))
        self.assertEqual(len(fs), 1, fs)
        self.assertIn(REDIS_TAG, fs[0][3])
        return fs[0]

    def test_current_three_prefixes_is_green(self):
        self.assertEqual(gates._rust_redis_prefixes(self.RUST), {"session", "throttle", "cpwd"})
        self.assertEqual(gates._redis_prefix_findings(self.OUTER, self.RUST), [])

    def test_rust_prefix_renamed_is_red_naming_both_sides_and_diff(self):
        f = self._one(self.OUTER, self.RUST.replace('"cpwd:"', '"pwd:"'))
        self.assertEqual(f[2], "tools/walkthrough-baseline.py")
        for part in ("RESTORE_REDIS_PREFIXES", "server/src/cache/mod.rs", "外層多 ['cpwd']", "rust 多 ['pwd']"):
            self.assertIn(part, f[3])

    def test_rust_new_key_family_is_red(self):
        f = self._one(self.OUTER, self.RUST + 'pub fn lock_key(x: &str) -> String {\n    format!("lock:{x}")\n}\n')
        self.assertIn("外層多 []、rust 多 ['lock']", f[3])

    def test_outer_extra_prefix_is_red(self):
        f = self._one(self.OUTER.replace('"cpwd")', '"cpwd", "captcha")'), self.RUST)
        self.assertIn("外層多 ['captcha']、rust 多 []", f[3])

    def test_anchor_vanish_on_either_side_is_red(self):
        f = self._one("X = 1\n", self.RUST)
        self.assertEqual(f[2], "tools/walkthrough-baseline.py")
        self.assertIn("命中 0 處", f[3])
        f = self._one(self.OUTER, "// moved\n")
        self.assertEqual(f[2], "rust-api/server/src/cache/mod.rs")
        self.assertIn("零命中", f[3])

    def test_outer_multiple_anchors_is_red(self):
        self.assertIn("命中 2 處", self._one(self.OUTER + 'RESTORE_REDIS_PREFIXES = ("session",)\n', self.RUST)[3])

    def test_outer_string_char_classes_delimiters_and_name_boundary(self):
        """外層錨之元組字串字元類排除逐條（`"`／反斜線／換行；重複段與末段各釘）、左右括號分釘、元素間逗號、名字面與名界、`=` 判準與
        其兩側不容換行（`[ \\t]`）、行尾註解不跨行：
        紅（錨形零命中）＝含反斜線轉義（`"c\\x70wd"`，首位與末位）、隱式拼接（`"session" "throttle"`，非末位與末位；Python 實值已非
        逐元素前綴）、無括號之裸元組（左右括號皆停才計）、多行元組之收尾行另帶內容（`) if FULL else ("session",)`、`)[:1]`）與末元素非
        字面（`EXTRA,`）——右括號判準擋：單停即於末字串元素行尾收錨、取三前綴照比而判綠，而 Python 實值已非該字面（FULL 為假時
        ＝`("session",)`，seed 模式 restore 留 throttle／cpwd 殘鍵）；
        綠（不計）＝三引號字串內被折斷之錨形句（字串元素不跨行；末位與非末位）、他名元組（`OTHER_PREFIXES`；名字面擋）、同前綴之他名
        （`RESTORE_REDIS_PREFIXES_DOC`；名界擋）、跨行呼叫內行首之關鍵字引數（`dict(\\nRESTORE_REDIS_PREFIXES = "x")`；左括號判準擋——
        單停即以外層呼叫之右括號收錨）、三引號字串內行首名後不接 `=` 之文字（`RESTORE_REDIS_PREFIXES ("x",)`；`=` 判準擋——單停分兩
        途徑：可省＝計成第二錨、命中 2 處；刪去＝基準錨失配、誘餌成唯一錨而落值不符）、跨行呼叫內 `=` 之前或之後折行之關鍵字引數（`=` 兩側之
        `[ \\t]` 不容換行各擋一形——任一側放寬成 `\\s` 即計成第二錨）；以上綠形之單停變異除 `=` 刪去途徑外皆落成命中 2 處。行尾註解之後
        另起一行之第二錨形照計＝命中 2 處。"""
        multi = 'RESTORE_REDIS_PREFIXES = (\n    "session",\n    "throttle",\n    "cpwd",\n'
        for bad in ('RESTORE_REDIS_PREFIXES = ("session", "throttle", "c\\x70wd")\n',
                    'RESTORE_REDIS_PREFIXES = ("c\\x70wd", "session", "throttle")\n',
                    'RESTORE_REDIS_PREFIXES = ("session" "throttle", "cpwd")\n',
                    'RESTORE_REDIS_PREFIXES = ("session", "throttle" "cpwd")\n',
                    'RESTORE_REDIS_PREFIXES = "session", "throttle", "cpwd"\n',
                    multi + ') if FULL else ("session",)\n', multi + ')[:1]\n', multi + '    EXTRA,\n)\n'):
            with self.subTest(bad=bad):
                self.assertIn("命中 0 處", self._one(bad, self.RUST)[3])
        for extra in ('"""\nRESTORE_REDIS_PREFIXES = ("x\n")\n"""\n', '"""\nRESTORE_REDIS_PREFIXES = ("x\n", "y")\n"""\n',
                      'OTHER_PREFIXES = ("x",)\n', 'RESTORE_REDIS_PREFIXES_DOC = ("x",)\n',
                      'd = dict(\nRESTORE_REDIS_PREFIXES = "x")\n', '"""\nRESTORE_REDIS_PREFIXES ("x",)\n"""\n',
                      'd = dict(\nRESTORE_REDIS_PREFIXES\n= ("x",)\n)\n', 'd = dict(\nRESTORE_REDIS_PREFIXES =\n("x",)\n)\n'):
            with self.subTest(extra=extra):
                self.assertEqual(gates._redis_prefix_findings(self.OUTER + extra, self.RUST), [])
        two = 'RESTORE_REDIS_PREFIXES = ("session", "throttle", "cpwd")  # 現值\nRESTORE_REDIS_PREFIXES = ("x",)\n'
        self.assertIn("命中 2 處", self._one(two, self.RUST)[3])

    def test_rust_segment_char_classes_and_nonempty(self):
        """rust 兩錨首段字元類排除逐條與首段非空：`format!(` 首段——含空白者（非鍵之訊息字串 `"redis error: {x}"`）、閉引號後緊接 `:`
        者（`format!("a")::b:`；首段不跨引號）、含反斜線跳脫者（`"a\\\\b:{x}"`）、以 `{` 起首而其後緊接 `:` 者（`format!("{:?}", e)`；
        `{` 排除擋——單停即取成 `{`）、含 `}` 者（`format!("a}}:{x}")`；`}` 排除擋——單停即取成 `a}}`）、首段為空者（`":{x}"`）皆不取，
        非 `format!` 之巨集（`concat!`＝射程外）不取；`*_PREFIX` 常數值——以 `{` 起首（`"{t}:"`；`{` 排除擋——單停即取成 `{t`）或
        為空（`":"`）者不取、首段截至首個 `{`、`}`、反斜線或空白（`"a{b}:"`、`"a}b:"`、`"a\\\\b:"`、`"a b:"`→a；`"a}b:"` 由 `}` 排除擋
        ——單停即取成 `a}b`）、同行非首項之宣告不取（錨行首）、可見性 `pub(…)` 內折行者不取（`=` 之前其餘折行途徑釘於
        test_rust_const_line_break_before_equals_paths）。
        腿層一併釘：各形併入 RUST、外層補其應取之前綴＝綠。"""
        cases = (('fn e(x: &str) -> String {\n    format!("redis error: {x}")\n}\n', set()),
                 ('// format!("a")::b:\n', set()),
                 ('fn k(x: &str) -> String {\n    format!("a\\\\b:{x}")\n}\n', set()),
                 ('fn d(e: E) -> String {\n    format!("{:?}", e)\n}\n', set()),
                 ('fn k(x: &str) -> String {\n    format!("a}}:{x}")\n}\n', set()),
                 ('fn k(x: &str) -> String {\n    format!(":{x}")\n}\n', set()),
                 ('const K: &str = concat!("lock:", "x");\n', set()),
                 ('pub const T_PREFIX: &str = "{t}:";\n', set()),
                 ('pub const E_PREFIX: &str = ":";\n', set()),
                 ('pub const B_PREFIX: &str = "a{b}:";\n', {"a"}),
                 ('pub const A_PREFIX: &str = "a}b:";\n', {"a"}),
                 ('pub const Y_PREFIX: &str = "a\\\\b:";\n', {"a"}),
                 ('pub const Z_PREFIX: &str = "a b:";\n', {"a"}),
                 ('pub(crate) fn f() -> u8 { 0 } pub(crate) const K_PREFIX: &str = "k:";\n', set()),
                 ('pub(\n    crate\n) const K_PREFIX: &str = "k:";\n', set()))
        for extra, want in cases:
            with self.subTest(extra=extra):
                self.assertEqual(gates._rust_redis_prefixes(extra), want)
                outer = self.OUTER.replace('"cpwd")', '"cpwd"' + "".join(f', "{p}"' for p in sorted(want)) + ")")
                self.assertEqual(gates._redis_prefix_findings(outer, self.RUST + extra), [])

    def test_rust_anchor_required_tokens_deleted_one_at_a_time(self):
        """rust 兩錨必含字面逐 token 刪一之誘餌＝不取（腿層併入 RUST 照綠）；任一字面改為可省即多取一前綴＝紅。
        `format!(` 錨：`format!("lock:{x}")` 之 `format`、`!`、`(`、首引號、首段後 `:` 各刪一（`!` 刪去取合法 Rust 之同名函式呼叫
        `my::format(…)`，餘置 `//` 註解內——①無行首限制、註解內錨形照計；首段刪成空之 `":{x}"` 住
        test_rust_segment_char_classes_and_nonempty；插值、閉引號與 `)` 刪去仍合錨形＝非必含）；射程外之定界形（`format![…]`、
        `format!{…}`、`format! (…)`；合法 Rust、`_rust_redis_prefixes` docstring 射程外例示）不取——圓括號判準放寬成容 `[`／`{`
        或 `!` 後容空白即取 lock。
        `*_PREFIX` 常數錨（區塊註解內獨立成行＝②之照計面）：`pub const K_PREFIX: &str = "k:";` 之 `pub` 與 `const` 間空格、`const`、
        其後空格、`_PREFIX`、`:`、`&`、`str`、`=`、值首引號各刪一，另型別註記 `: &str` 整段刪去（值首段刪成空之 `":"` 住
        test_rust_segment_char_classes_and_nonempty；
        `pub`、名前段 `K`、`:` 後與 `=` 兩側之空格、值尾 `:`、閉引號與 `;` 刪去仍合錨形＝非必含）；`pub static K_PREFIX: &'static str = "k:";`
        之生命週期 `'`、`static` 字、其後空格各刪一；`pub(crate) const K_PREFIX: &str = "k:";` 之 `pub`、`(`、`)` 各刪一（`crate` 刪去
        仍合錨形；`)` 後空格刪去之 `pub(crate)const` 住 test_rust_const_same_line_whitespace_paths）；值不以 `"` 起首者
        （非字串字面 `concat!("k", ":")`、raw string `r"k:"`；皆合法 Rust、射程外）不取——值首引號改為可省即取成 `concat!(`／`r`。"""
        fmt = ('fn k(x: &str) -> String {\n    my::format("lock:{x}")\n}\n', '// !("lock:{x}")\n', '// format!"lock:{x}"\n',
               '// format!(lock:{x}")\n', '// format!("lock{x}")\n',
               'fn k(x: &str) -> String {\n    format!["lock:{x}"]\n}\n', 'fn k(x: &str) -> String {\n    format!{"lock:{x}"}\n}\n',
               'fn k(x: &str) -> String {\n    format! ("lock:{x}")\n}\n')
        const = ('pubconst K_PREFIX: &str = "k:";', 'pub  K_PREFIX: &str = "k:";', 'pub constK_PREFIX: &str = "k:";', 'pub const K: &str = "k:";',
                 'pub const K_PREFIX &str = "k:";', 'pub const K_PREFIX: str = "k:";', 'pub const K_PREFIX: & = "k:";',
                 'pub const K_PREFIX: &str "k:";', 'pub const K_PREFIX: &str = k:";', 'pub const K_PREFIX = "k:";',
                 'pub static K_PREFIX: &static str = "k:";', "pub static K_PREFIX: &' str = \"k:\";",
                 "pub static K_PREFIX: &'staticstr = \"k:\";",
                 '(crate) const K_PREFIX: &str = "k:";', 'pubcrate) const K_PREFIX: &str = "k:";',
                 'pub(crate const K_PREFIX: &str = "k:";')
        for extra in fmt + tuple("/*\n" + c + "\n*/\n" for c in const) + ('pub const K_PREFIX: &str = concat!("k", ":");\n',
                                                                          'pub const K_PREFIX: &str = r"k:";\n'):
            with self.subTest(extra=extra):
                self.assertEqual(gates._rust_redis_prefixes(extra), set())
                self.assertEqual(gates._redis_prefix_findings(self.OUTER, self.RUST + extra), [])

    def test_rust_const_line_break_before_equals_paths(self):
        """`*_PREFIX` 常數宣告於 `=` 之前折行之途徑（`_rust_redis_prefixes` docstring 射程外句）：不取＝`pub` 與 `(` 之間、`const`／
        `static` 與名稱之間、名稱至 `=` 之間（名稱與 `:` 之間、`:` 與 `&` 之間、型別註記內〔`&` 之後、`'static` 與 `str` 之間〕、型別
        註記與 `=` 之間）——各處皆不容換行，放寬成容 `\\s` 即取 k；`pub(…)` 括號內之途徑釘於 test_rust_segment_char_classes_and_nonempty。
        照取＝可見性與 `const`／`static` 之間折行（次行自成無可見性之錨形；可見性內另有折行亦同〔`pub` 與 `(` 之間、括號內〕；可見性改為
        必要即不取）。同行空格／tab 之途徑釘於 test_rust_const_same_line_whitespace_paths。"""
        cases = (('pub\n(crate) const K_PREFIX: &str = "k:";\n', set()),
                 ('pub const\n    K_PREFIX: &str = "k:";\n', set()),
                 ('pub const K_PREFIX\n    : &str = "k:";\n', set()),
                 ('pub const K_PREFIX:\n    &str = "k:";\n', set()),
                 ('pub const K_PREFIX: &\n    str = "k:";\n', set()),
                 ("pub static K_PREFIX: &\n    'static str = \"k:\";\n", set()),
                 ("pub static K_PREFIX: &'static\n    str = \"k:\";\n", set()),
                 ('pub const K_PREFIX: &str\n    = "k:";\n', set()),
                 ('pub\nconst K_PREFIX: &str = "k:";\n', {"k"}),
                 ('pub(crate)\n    const K_PREFIX: &str = "k:";\n', {"k"}),
                 ('pub\n(crate)\nconst K_PREFIX: &str = "k:";\n', {"k"}),
                 ('pub(\n    crate\n)\n    const K_PREFIX: &str = "k:";\n', {"k"}))
        for text, want in cases:
            with self.subTest(text=text):
                self.assertEqual(gates._rust_redis_prefixes(text), want)

    def test_rust_const_same_line_whitespace_paths(self):
        """`*_PREFIX` 常數宣告於 `=` 之前同行之空格／tab 異於錨形之途徑（`_rust_redis_prefixes` docstring 射程外句）皆不取：`pub` 與
        `(` 之間帶空格或 tab（`pub (crate)`；該處放寬成容 `[ \\t]*` 即取 k）、`&` 之後帶空格（`& str`、`& 'static str`；同）、
        `pub(…)` 與 `const`／`static` 緊貼（`pub(crate)const`；該處 `[ \\t]+` 放寬成 `[ \\t]*` 即取 k）。"""
        for text in ('pub (crate) const K_PREFIX: &str = "k:";\n', 'pub\t(crate) const K_PREFIX: &str = "k:";\n',
                     'pub const K_PREFIX: & str = "k:";\n', "pub static K_PREFIX: & 'static str = \"k:\";\n",
                     'pub(crate)const K_PREFIX: &str = "k:";\n'):
            with self.subTest(text=text):
                self.assertEqual(gates._rust_redis_prefixes(text), set())

    def test_rust_const_whitespace_runs_tabs_and_zero_taken(self):
        """`*_PREFIX` 常數錨同行空白判準逐處照取（皆取得該前綴）：行首縮排為 tab（拿掉 tab 即不取）；可見性與 `const`／`static` 之間、
        `const`／`static` 與名稱之間、`'static` 與 `str` 之間各為兩個空格與 tab（該處 `[ \\t]+` 改為恰一個即不取兩空格形、拿掉 tab 即不取
        tab 形）；名稱與 `:` 之間為空格與 tab、`:` 與 `&` 之間與 `str` 與 `=` 之間為零空白與 tab（該處 `[ \\t]*` 改為恰一個即不取零空白形、
        拿掉空格或 tab 即不取該形）。"""
        cases = (('\tconst T_PREFIX: &str = "t:";\n', "t"),
                 ('pub  const A_PREFIX: &str = "a:";\n', "a"), ('pub\tconst B_PREFIX: &str = "b:";\n', "b"),
                 ('const  C_PREFIX: &str = "c:";\n', "c"), ('const\tD_PREFIX: &str = "d:";\n', "d"),
                 ('const E_PREFIX : &str = "e:";\n', "e"), ('const F_PREFIX\t: &str = "f:";\n', "f"),
                 ('const G_PREFIX:&str = "g:";\n', "g"), ('const H_PREFIX:\t&str = "h:";\n', "h"),
                 ("static I_PREFIX: &'static  str = \"i:\";\n", "i"), ("static J_PREFIX: &'static\tstr = \"j:\";\n", "j"),
                 ('const K_PREFIX: &str= "k:";\n', "k"), ('const L_PREFIX: &str\t= "l:";\n', "l"))
        for text, want in cases:
            with self.subTest(text=text):
                self.assertEqual(gates._rust_redis_prefixes(text), {want})

    def test_outer_anchor_whitespace_and_line_break_forms_taken(self):
        """外層錨之空白判準逐處照取（合法 Python、皆綠——錨形零命中即紅）：名與 `=` 之間及 `=` 與 `(` 之間零空白
        （`RESTORE_REDIS_PREFIXES=(…)`；任一處 `[ \\t]*` 改為恰一個即零命中）與 tab（`\\t=\\t(`；任一處拿掉 tab 即零命中）；元素閉引號與其後
        逗號之間折行——重複段（逗號前置之多行元組）與末段（末元素後之尾逗號另起一行）各一（該處 `\\s*` 收窄成 `[ \\t]*` 即零命中）；
        右括號後以 tab 隔開之行尾註解（拿掉 tab 即零命中）。"""
        for line in ('RESTORE_REDIS_PREFIXES=("session", "throttle", "cpwd")\n',
                     'RESTORE_REDIS_PREFIXES\t=\t("session", "throttle", "cpwd")\n',
                     'RESTORE_REDIS_PREFIXES = ("session"\n    , "throttle"\n    , "cpwd")\n',
                     'RESTORE_REDIS_PREFIXES = ("session", "throttle", "cpwd"\n,)\n',
                     'RESTORE_REDIS_PREFIXES = ("session", "throttle", "cpwd")\t# 清理前綴\n'):
            with self.subTest(line=line):
                self.assertEqual(gates._redis_prefix_findings("X = 1\n" + line, self.RUST), [])

    def test_outer_element_quotes_required_decoys(self):
        """外層錨元組元素之首尾引號（重複段與末段各釘）：三引號字串內缺其一之錨形句不計（皆綠）——缺重複段首引號 `(x", "y")`、
        缺重複段閉引號 `("x, "y")`、缺末段首引號 `("x", y")`、缺末段閉引號 `("x", "y)`；任一引號改為可省即計成第二錨＝命中 2 處。"""
        for decoy in ('(x", "y")', '("x, "y")', '("x", y")', '("x", "y)'):
            with self.subTest(decoy=decoy):
                outer = self.OUTER + '"""\nRESTORE_REDIS_PREFIXES = ' + decoy + '\n"""\n'
                self.assertEqual(gates._redis_prefix_findings(outer, self.RUST), [])

    def test_out_of_range_anchor_once_plus_non_anchor_rebind_stays_green(self):
        """射程外釘（`_redis_prefix_findings` docstring ①）：外層錨形行恰一處、模組層另有不合錨形之再綁定——非字面（自身拼接、
        `tuple(…)`、增量賦值）與不合錨形之字面（單引號、型別註記、縮排於模組層區塊內、條件式、隱式拼接、空元組）：再綁定行不計、
        錨數仍 1，照比錨形行之字面值；有效值已與 rust 不符（多 x 或少 cpwd 等）而本腿照綠。"""
        for rebind in ('RESTORE_REDIS_PREFIXES = RESTORE_REDIS_PREFIXES + ("x",)\n',
                       'RESTORE_REDIS_PREFIXES = tuple(p for p in RESTORE_REDIS_PREFIXES if p != "cpwd")\n',
                       'RESTORE_REDIS_PREFIXES += ("x",)\n',
                       "RESTORE_REDIS_PREFIXES = ('session', 'throttle')\n",
                       'RESTORE_REDIS_PREFIXES: tuple = ("session", "throttle")\n',
                       'if True:\n    RESTORE_REDIS_PREFIXES = ("session",)\n',
                       'RESTORE_REDIS_PREFIXES = ("session", "throttle") if True else ()\n',
                       'RESTORE_REDIS_PREFIXES = ("session", "thr" "ottle")\n',
                       'RESTORE_REDIS_PREFIXES = ()\n'):
            with self.subTest(rebind=rebind):
                self.assertEqual(len(gates.RE_REDIS_PREFIXES_OUTER.findall(self.OUTER + rebind)), 1)
                self.assertEqual(gates._redis_prefix_findings(self.OUTER + rebind, self.RUST), [])

    def test_out_of_range_single_element_without_trailing_comma_counts(self):
        """射程外釘（`_redis_prefix_findings` docstring ②）：錨形行為單元素而無尾逗號（`("session")`——Python 實值為字串而非元組）
        照計、照比其字面值——rust 側恰為該前綴時本腿照綠。"""
        outer, rust = 'RESTORE_REDIS_PREFIXES = ("session")\n', 'fn k(s: &str) -> String {\n    format!("session:{s}")\n}\n'
        self.assertEqual(len(gates.RE_REDIS_PREFIXES_OUTER.findall(outer)), 1)
        self.assertEqual(gates._redis_prefix_findings(outer, rust), [])

    def test_submodule_present_judges_head_tree_not_worktree(self):
        """子庫在場＝判 HEAD 樹、未 commit 改動不入判：HEAD 樹前綴與外層不符而工作樹相符＝紅（差集取自 HEAD 樹）；反之＝綠。"""
        renamed = self.RUST.replace('"cpwd:"', '"pwd:"')
        sub = TestGt12Doorbell._sub_ctx
        fs = errs(gates._redis_prefix_leg(sub(self.OUTER, gates.REDIS_KEYS_RUST, head=renamed, work=self.RUST)))
        self.assertEqual(len(fs), 1, fs)
        self.assertIn(f"{REDIS_TAG}：外層 RESTORE_REDIS_PREFIXES＝", fs[0][3])
        self.assertIn("外層多 ['cpwd']、rust 多 ['pwd']", fs[0][3])
        self.assertEqual(gates._redis_prefix_leg(sub(self.OUTER, gates.REDIS_KEYS_RUST, head=self.RUST, work=renamed)), [])

    def test_submodule_head_tree_unreadable_is_red_naming_path(self):
        """子庫在場而 `git show HEAD:<檔>` rc≠0＝紅、恰一筆、指名子庫檔路徑與 rc（不得落成 rust 側錨形零命中之訊息）。"""
        fs = errs(gates._redis_prefix_leg(TestGt12Doorbell._sub_ctx(self.OUTER, gates.REDIS_KEYS_RUST, head=None, work=self.RUST)))
        self.assertEqual(len(fs), 1, fs)
        self.assertEqual(fs[0][2], f"rust-api/{gates.REDIS_KEYS_RUST}")
        self.assertIn(f"{REDIS_TAG}：子庫 HEAD 樹取不到 {gates.REDIS_KEYS_RUST}（git show rc=128）", fs[0][3])

    def test_outer_anchor_forms(self):
        """外層錨＝行首 `RESTORE_REDIS_PREFIXES = (…)`、元組只含雙引號字串字面（可跨行、可帶尾逗號與行尾註解）；非純字面元組
        （名稱拼接、空元組）＝錨形零命中＝紅。不計之形逐途徑：①名稱非緊貼行首之賦值（屬性賦值 `wb.RESTORE_REDIS_PREFIXES = (…)`、
        縮排之區域賦值）——行首判準擋；②名稱非行首且其後接 `,` 之引用（自測斷言 `assertEqual(RESTORE_REDIS_PREFIXES, …)`）——行首判準
        與 `=` 判準兩重擋、單停任一照綠（本形不作任一判準之證；`=` 判準之殺案住 test_outer_string_char_classes_delimiters_and_name_boundary）。"""
        multi = 'RESTORE_REDIS_PREFIXES = (\n    "session",\n    "throttle",\n    "cpwd",\n)  # 清理前綴\n'
        for other in ('wb.RESTORE_REDIS_PREFIXES = ("x",)\n', '    RESTORE_REDIS_PREFIXES = ("x",)\n',
                      '    self.assertEqual(RESTORE_REDIS_PREFIXES, ("x",))\n'):
            with self.subTest(other=other):
                self.assertEqual(gates._redis_prefix_findings(multi + other, self.RUST), [])
        for bad in ('RESTORE_REDIS_PREFIXES = BASE + ("x",)\n', 'RESTORE_REDIS_PREFIXES = ("session", "throttle") + EXTRA\n',
                    "RESTORE_REDIS_PREFIXES = ()\n", "RESTORE_REDIS_PREFIXES = ('session', 'throttle', 'cpwd')\n"):
            with self.subTest(bad=bad):
                self.assertIn("命中 0 處", self._one(bad, self.RUST)[3])

    def test_rust_anchor_forms(self):
        """rust 錨兩形逐途徑：①`format!(` 首引號後之字面首段（單行、rustfmt 折行）②`*_PREFIX` 常數字面首段（pub／pub(crate)／無可見性、
        const／static、值有無尾 `:`、值於 `=` 後折行；名於 `_PREFIX` 之前含數字〔`V2_KEY_PREFIX`；名字元類收窄去數字即不取〕或為空
        〔`_PREFIX`；改為必要即不取〕照取）；不計＝首段為插值（`{}`、`{常數}`、`cmdstat_{command}:` 形）、`format!(` 字面無 `:`
        （`pwdlock{uid}`、`pwdreset-{u}` 形＝射程外）、常數名非 `_PREFIX` 結尾（含名中帶 `_PREFIX` 而其後另接字元者 `KEY_PREFIX_V2`——
        `_PREFIX` 後須接 `:` 之名界擋；放寬即多取 v2）、常數名於 `_PREFIX` 之前含大寫 ASCII 字母、數字與底線以外之字元者（射程外；名字元類
        `[A-Z0-9_]` 擋——小寫字母 `Lock_PREFIX`〔放寬成容小寫即取 lock〕、非 ASCII 字母 `Ä_PREFIX`〔放寬成 `\\w` 即取 ae〕、raw
        identifier `r#LOCK_PREFIX`〔放寬成容 `r#` 即取 rlock〕）、
        以 `///`／`//`／`/*` 起首之註解行內之常數形（②錨行首）；照計＝`//` 註解內之 `format!(` 錨形（①無行首限制）、跨行區塊註解內
        獨立成行之常數形（只會多出前綴＝誤紅、遮不掉新增前綴）。"""
        cases = (('format!("session:denylist:{sid}")', {"session"}),
                 ('format!(\n        "throttle:unlock:{}:{bucket}",\n        crate::throttle::DIM_IP\n    )', {"throttle"}),
                 ('pub const CHANGE_PWD_KEY_PREFIX: &str = "cpwd:";', {"cpwd"}),
                 ('    pub const SOME_VERY_LONG_KEY_FAMILY_PREFIX: &str =\n        "h:";', {"h"}),
                 ('pub(crate) const A_PREFIX: &str = "a:";', {"a"}),
                 ('    const B_PREFIX: &str = "b";', {"b"}),
                 ("pub static C_PREFIX: &'static str = \"c:\";", {"c"}),
                 ('format!("{}:gs", uniq_prefix())', set()),
                 ('format!("{CHANGE_PWD_KEY_PREFIX}{uid}")', set()),
                 ('format!("cmdstat_{command}:calls=")', set()),
                 ('format!("pwdlock{uid}")', set()),
                 ('format!("pwdreset-{u}")', set()),
                 ('pub const IPGATE_INVALIDATE_CHANNEL: &str = "ipgate:invalidate";', set()),
                 ('pub const KEY_PREFIX_V2: &str = "v2:";', set()),
                 ('pub const V2_KEY_PREFIX: &str = "v2:";', {"v2"}),
                 ('pub const _PREFIX: &str = "u:";', {"u"}),
                 ('pub const Lock_PREFIX: &str = "lock:";', set()),
                 ('pub const Ä_PREFIX: &str = "ae:";', set()),
                 ('pub const r#LOCK_PREFIX: &str = "rlock:";', set()),
                 ('/// pub const D_PREFIX: &str = "d:";', set()),
                 ('// pub const E_PREFIX: &str = "e:";', set()),
                 ('/* pub const F_PREFIX: &str = "f:"; */', set()),
                 ('/*\npub const G_PREFIX: &str = "g:";\n*/', {"g"}),
                 ('// 舊寫法 format!("old:{x}")', {"old"}))
        for text, want in cases:
            with self.subTest(text=text):
                self.assertEqual(gates._rust_redis_prefixes(text), want)

    def test_outer_absent_is_red_and_submodule_absent_shares_doorbell_skip(self):
        """外層缺席＝紅、gt_12 兩腿各出恰一筆、訊息首段各帶腿標籤（本腿接線不得吞掉或頂替門鈴腿那筆：任一腿那筆被拿掉、或改出
        對方腿之訊息皆紅——兩腿缺席訊息同含「walkthrough-baseline.py 缺席」、不分腿之斷言對此失明）；rust-api 缺席＝本腿不另出列、
        由門鈴腿之具名跳過（GT-12.submodule-absent）承載——gt_12 恰一筆該鍵 SKIP，
        該行與 ENV_SKIPS 該鍵理由（GATES.md 環境跳過表同源）皆指名本腿（ADR-00019 決定 3：跳過與通過可辨；只名門鈴＝本腿未對賬而無名）。"""
        base = {RULES: RULES_TEXT, NOTES: "<!-- wave: 6 -->\n"}
        absent = [f[3] for f in errs(gates.gt_12(stub(base))) if "walkthrough-baseline.py 缺席" in f[3]]
        self.assertEqual(sorted(m.split("——", 1)[0] for m in absent),
                         sorted([f"{REDIS_TAG}：tools/walkthrough-baseline.py 缺席", "門鈴字面對賬：tools/walkthrough-baseline.py 缺席"]), absent)
        fs = gates.gt_12(stub(dict(base, **{"tools/walkthrough-baseline.py": self.OUTER})))
        self.assertEqual([f for f in fs if REDIS_TAG in f[3]], [])
        skips = [f for f in fs if f[0] == "SKIP" and "GT-12.submodule-absent" in f[3]]
        self.assertEqual(len(skips), 1, fs)
        for part in ("門鈴字面", "redis 前綴名冊", "未對賬"):
            self.assertIn(part, skips[0][3])
        reason = gates.ENV_SKIPS["GT-12.submodule-absent"][1]
        for part in (gates.DOORBELL_RUST, gates.REDIS_KEYS_RUST):
            self.assertIn(part, reason)

    def test_real_repo_redis_prefixes_reconcile(self):
        """真 repo：本腿零 finding，且兩側錨形皆有命中（非空集合對賬、不是兩邊都抓空）。"""
        ctx = common.Ctx(ROOT)
        self.assertEqual([f for f in gates.gt_12(ctx) if REDIS_TAG in f[3]], [])
        if ctx.exists("rust-api/.git"):
            rc, rust = ctx.git_try("show", f"HEAD:{gates.REDIS_KEYS_RUST}", cwd=os.path.join(ROOT, "rust-api"))
            self.assertEqual(rc, 0)
            outer = gates.RE_REDIS_PREFIXES_OUTER.findall(ctx.text("tools/walkthrough-baseline.py"))
            self.assertEqual(len(outer), 1)
            self.assertTrue(gates._rust_redis_prefixes(rust))
            self.assertEqual(set(gates.RE_DQ_STR.findall(outer[0])), gates._rust_redis_prefixes(rust))



RECON = "閘↔規則對賬"   # 對賬腿全部訊息共有的字面
RECON_RULES = """<!-- next: RL-0005 -->
| id | 規則 | scope | carrier | source |
|---|---|---|---|---|
| RL-0001 | 甲。 | implementer | lint | rev5:L-003 |
| RL-0002 | 乙。 | implementer | lint | rev5:L-003 |
| RL-0003 | 丙。 | implementer | prompt | rev5:L-003 |
| RL-0004 | 丁。 | 主線 | checklist | rev5:L-003 |
"""


class TestGt12RuleReconcile(unittest.TestCase):
    """BL-00036①：閘 GATE 區塊 `rule=` ⇔ RULES carrier=lint 雙向對賬（掛 GT-12、不新增閘）。
    `rule=` 多值以「、」分隔、解析只一處（`gates.rule_values`；對賬腿與 GATES.md 渲染同取）；每值須為 RL-NNNN／ADR-NNNNN 形；
    carrier=lint 之 RL 皆須被至少一閘指名、`rule=` 所列 RL 皆須在 RULES 且 carrier=lint；ADR 值照舊允許、不驗 carrier。"""

    def leg(self, rules, rules_text=RECON_RULES):
        blocks = {gid: {"id": gid, "rule": r} for gid, r in rules.items()}
        return errs(gates._rule_reconcile_leg(blocks, rules_text, {gid: f"tools/docsync/{gid}.py" for gid in blocks}))

    def test_every_lint_rule_named_is_green(self):
        """正：每條 lint 規則皆有閘指名、所列 RL 皆 lint、ADR 值混列——零 finding。"""
        self.assertEqual(self.leg({"GT-01": "RL-0001", "GT-02": "RL-0002、ADR-00006"}), [])

    def test_lint_rule_named_by_no_gate_is_red(self):
        """反①：RL-0002（carrier=lint）無閘指名→恰一筆、指名該 RL 並附補救；已指名的 RL-0001 不報。"""
        fs = self.leg({"GT-01": "RL-0001"})
        self.assertEqual([f[2] for f in fs], [f"{RULES}｜RL-0002"], fs)
        self.assertTrue(RECON in fs[0][3] and "RL-0002" in fs[0][3] and "carrier=lint" in fs[0][3] and "補救" in fs[0][3], fs)

    def test_rule_naming_non_lint_or_absent_rl_is_red(self):
        """反②：`rule=` 列 carrier=prompt／checklist 之 RL 與 RULES 查無之 RL→各一筆、指名閘與 RL、where＝該閘所在檔。"""
        fs = self.leg({"GT-01": "RL-0001、RL-0003、RL-0004、RL-0009", "GT-02": "RL-0002"})
        self.assertEqual(len(fs), 3, fs)
        self.assertTrue(all(f[2] == "tools/docsync/GT-01.py" and "GT-01" in f[3] and "補救" in f[3] for f in fs), fs)
        by = {rid: [f[3] for f in fs if rid in f[3]] for rid in ("RL-0003", "RL-0004", "RL-0009")}
        self.assertTrue(len(by["RL-0003"]) == 1 and "carrier=prompt" in by["RL-0003"][0], by)
        self.assertTrue(len(by["RL-0004"]) == 1 and "carrier=checklist" in by["RL-0004"][0], by)
        self.assertTrue(len(by["RL-0009"]) == 1 and "查無" in by["RL-0009"][0], by)
        # RULES 零列（掃描面空集合）：每個 RL 值皆「查無」即紅、不因對賬面空而靜默
        fs = self.leg({"GT-01": "RL-0001"}, rules_text="")
        self.assertTrue(len(fs) == 1 and "查無" in fs[0][3] and "RL-0001" in fs[0][3], fs)

    def test_malformed_values_are_red(self):
        """反③：每值須為 RL-NNNN 或 ADR-NNNNN（半形數字）、多值只認「、」——他形逐值指名。"""
        for bad in ("RL-15", "RL-00015", "rl-0001", "RL-" + "００１５", "ADR-0006", "GT-01",
                    "RL-0001,RL-0002", "RL-0001／RL-0002", "RL-0001 RL-0002", ""):
            fs = self.leg({"GT-01": bad, "GT-02": "RL-0001、RL-0002"})
            self.assertTrue(len(fs) == 1 and "形制" in fs[0][3] and f"「{bad}」" in fs[0][3] and "GT-01" in fs[0][3], (bad, fs))
        fs = self.leg({"GT-01": "RL-0001、", "GT-02": "RL-0002"})   # 尾隨分隔＝多出一個空值
        self.assertTrue(len(fs) == 1 and "「」" in fs[0][3], fs)

    def test_multi_value_parse_single_source(self):
        """多值解析：以「、」切、逐值去空白、缺鍵＝空清單（缺鍵由缺鍵腿指名、此處不重報）；對賬逐值計入指名。"""
        self.assertEqual(gates.rule_values({"rule": "RL-0001、 RL-0002 、ADR-00006"}), ["RL-0001", "RL-0002", "ADR-00006"])
        self.assertEqual(gates.rule_values({"rule": "RL-0001"}), ["RL-0001"])
        self.assertEqual(gates.rule_values({"id": "GT-01"}), [])
        self.assertEqual(self.leg({"GT-01": "RL-0002 、RL-0001"}), [])

    def test_adr_value_is_allowed_without_carrier_check(self):
        """ADR 值照舊允許、不驗 carrier 與存在（ADR 引用存在性歸 GT-05 引用腿）：RULES 零 lint 列時純 ADR 值零 finding。"""
        no_lint = RECON_RULES.replace("| lint |", "| prompt |")
        self.assertEqual(self.leg({"GT-01": "ADR-00099"}, rules_text=no_lint), [])
        self.assertEqual(self.leg({"GT-01": "ADR-00099、RL-0001", "GT-02": "RL-0002"}), [])

    def test_wired_into_gt12_with_gate_source_as_where(self):
        """接線：gt_12 以真 package 各閘區塊對 RULES 現文對賬——樁 RULES 兩列皆 prompt，故真閘所列 RL 一律「查無」、
        where＝該閘所在檔（GT-12 在 gates.py、GT-04 在 adr.py）。"""
        fs = [f for f in errs(gates.gt_12(stub({RULES: RULES_TEXT, NOTES: "<!-- wave: 1 -->\n"}))) if RECON in f[3]]
        self.assertTrue(any(f[2] == "tools/docsync/gates.py" and "GT-12" in f[3] and "RL-0052" in f[3] for f in fs), fs)
        self.assertTrue(any(f[2] == "tools/docsync/adr.py" and "GT-04" in f[3] and "RL-0081" in f[3] for f in fs), fs)

    def test_real_repo_zero_hits_on_non_empty_face(self):
        """真 repo：對賬零命中；前提＝受檢面非空（carrier=lint 列 ≥1、每閘 rule= ≥1 值；RL-0067）。"""
        fs, _ = real_lint()
        self.assertEqual([f for f in fs if RECON in f[3]], [])
        from docsync import rules as rules_mod
        with open(os.path.join(ROOT, RULES), encoding="utf-8") as fh:
            lint = {r.id for r in rules_mod.parse_rules(fh.read())[1] if r.carrier == "lint"}
        blocks = gates.parse_gate_blocks("\n".join(gates.package_sources().values()))
        self.assertTrue(lint)
        self.assertTrue(all(gates.rule_values(b) for b in blocks.values()), blocks)
        self.assertTrue(lint <= {v for b in blocks.values() for v in gates.rule_values(b)})

    def test_gates_md_renders_rule_via_single_parser(self):
        """同源：GATES.md「守哪條 RULES／ADR」欄經 `rule_values` 渲染——把它換掉即見替身值；真值多值以「、」連。"""
        with unittest.mock.patch.object(gates, "rule_values", lambda b: ["RL-9999"]):
            self.assertIn("| GT-01 | RL-9999 |", gates.gen_gates_md(stub({})))
        out = gates.gen_gates_md(stub({}))
        self.assertIn("| GT-12 | RL-0052、RL-0051 |", out)
        self.assertIn("| GT-06 | RL-0048、RL-0015、RL-0077 |", out)
