"""語料面：gates 名冊同源（區塊／錨形／ROSTER）、Day-1 到期即紅、GT-07 樣式與值比對、GT-09 對賬、GT-12 波標記與預算、run_lint 末行。
機密樣本一律執行期串接構造。"""
import json
import os
import re
import subprocess
import tempfile
import unittest

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


class TestGt12(unittest.TestCase):
    def _files(self, wave, rules_text=RULES_TEXT, extra=None):
        files = {RULES: rules_text, NOTES: f"<!-- wave: {wave} -->\n"}
        files.update(extra or {})
        return files

    def test_wave_lag_and_budget_levels(self):
        fs = gates.gt_12(stub(self._files(5, extra={"specs/001-x/spec.md": "s\n"})))
        self.assertTrue(any("波標記落後" in f[3] for f in errs(fs)))
        over = RULES_TEXT.replace("上限（D8）：總 3", "上限（D8）：總 1")
        self.assertTrue(any("RULES 總" in f[3] for f in errs(gates.gt_12(stub(self._files(6, over))))))
        fs1 = gates.gt_12(stub(self._files(1, over)))
        self.assertTrue(any("RULES 總" in f[3] for f in fs1 if f[0] == "WARN"))
        self.assertFalse(any("RULES 總" in f[3] for f in errs(fs1)))
        self.assertTrue(any("波標記缺席" in f[3] for f in errs(gates.gt_12(stub({RULES: RULES_TEXT})))))

    def test_three_sources_skip_when_absent_and_red_when_mismatch(self):
        fs = gates.gt_12(stub(self._files(1)))
        keys = {f[3].split("：")[0] for f in fs if f[0] == "SKIP"}
        self.assertEqual(keys, {"GT-12.runbook-absent", "GT-12.precommit-absent"})
        bad = self._files(1, extra={".githooks/pre-commit": "#!/bin/sh\n# lint（GT-01～GT-11）\n", "docs/ops/RUNBOOK.md": "| GT-01 | x |\n"})
        msgs = [f[3] for f in errs(gates.gt_12(stub(bad)))]
        self.assertTrue(any("pre-commit" in m for m in msgs) and any("RUNBOOK" in m for m in msgs))
        good = self._files(1, extra={".githooks/pre-commit": "#!/bin/sh\n# lint（GT-01～GT-12）\n", "docs/ops/RUNBOOK.md": "| `lint` | GT-01～GT-12 |\n"})
        self.assertEqual([f for f in errs(gates.gt_12(stub(good))) if "pre-commit" in f[3] or "RUNBOOK" in f[3]], [])


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
