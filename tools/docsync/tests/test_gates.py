"""語料面：gates 名冊同源（區塊／錨形／ROSTER）、Day-1 到期即紅、GT-07 樣式與值比對、GT-09 對賬、GT-12 波標記與預算、run_lint 末行。
機密樣本一律執行期串接構造。"""
import json
import os
import re
import subprocess
import tempfile
import unittest
import unittest.mock

from docsync import gates, common, ROOT, RULES, NOTES
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
        self.assertTrue(any(f[0] == "SKIP" and "GT-07.secrets-absent" in f[3] for f in fs))


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

    def test_green_and_hooks_absent_skip(self):
        readme = "# R\n\n```text\n├── tools/\n├── deploy/\n└── .claude/\n    ├── settings.json\n    └── hooks/\n```\n"
        execs = ["deploy/sops.sh", "deploy/generate-age-key.sh", "deploy/generate-dev-cert.sh", "tools/bootstrap.sh"]
        files = {"README.md": readme, "tools/x.py": "1\n", ".claude/settings.json": self.SETTINGS, ".claude/hooks/s.sh": "#!/bin/sh\n"}
        files.update({e: "#!/bin/sh\n" for e in execs})
        root = make_repo(files, exec_paths=execs)
        fs = gates.gt_09(common.Ctx(root))
        self.assertEqual([f for f in errs(fs) if "deploy/sops.sh" in f[2] or "tools/" in f[2] or "hooks" in f[2]], [])
        self.assertTrue(any(f[0] == "SKIP" and "GT-09.hooks-absent" in f[3] for f in fs))
        fs2 = gates.gt_09(common.Ctx(make_repo({"tools/x.py": "1\n"})))
        self.assertTrue(any(f[0] == "SKIP" and "GT-09.readme-absent" in f[3] for f in fs2))


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

    def test_three_sources_skip_when_absent_and_red_when_mismatch(self):
        fs = gates.gt_12(stub(self._files(1)))
        keys = {f[3].split("：")[0] for f in fs if f[0] == "SKIP"}
        self.assertEqual(keys, {"GT-12.runbook-absent", "GT-12.precommit-absent"})
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
        fs, summary = gates.run_lint(common.Ctx(ROOT))
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


if __name__ == "__main__":
    unittest.main()
