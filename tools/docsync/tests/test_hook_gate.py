"""語料面：PreToolUse(Workflow) hook 對賬——zh-TW 字面＋RULES-VERSION 缺／錯／對；name 式預存 workflow 放行。以 subprocess 實跑 hook。"""
import json
import os
import subprocess
import unittest

from docsync import ROOT, RULES, rules

HOOK = os.path.join(ROOT, ".claude", "hooks", "pre-workflow-gate.py")


def run_hook(payload):
    p = subprocess.run(["python3", HOOK], input=json.dumps(payload), capture_output=True, text=True, cwd=ROOT)
    return p.returncode, p.stderr


class TestHookGate(unittest.TestCase):
    def setUp(self):
        self.ver = rules.rules_version(open(os.path.join(ROOT, RULES), encoding="utf-8").read())

    def test_missing_zh_tw_blocked(self):
        rc, err = run_hook({"tool_input": {"script": "const RULES = `x\\nRULES-VERSION: " + self.ver + "`;"}})
        self.assertEqual(rc, 2)
        self.assertIn("zh-TW", err)

    def test_missing_rules_version_blocked(self):
        rc, err = run_hook({"tool_input": {"script": "const RULES = `一律 zh-TW`;"}})
        self.assertEqual(rc, 2)
        self.assertIn("RULES-VERSION", err)

    def test_wrong_version_blocked_with_regen_hint(self):
        rc, err = run_hook({"tool_input": {"script": "一律 zh-TW\\nRULES-VERSION: 000000000000\\n"}})
        self.assertEqual(rc, 2)
        self.assertIn("RULES-VERSION", err)
        self.assertIn("generate", err)

    def test_correct_passes(self):
        rc, err = run_hook({"tool_input": {"script": "一律 zh-TW\\nRULES-VERSION: " + self.ver + "\\n"}})
        self.assertEqual(rc, 0, err)

    def test_generated_sk_rules_passes(self):
        sk = open(os.path.join(ROOT, "tools", "orchestration", "_sk_rules.js"), encoding="utf-8").read()
        rc, err = run_hook({"tool_input": {"script": sk}})
        self.assertEqual(rc, 0, err)

    def test_named_workflow_passes(self):
        rc, _ = run_hook({"tool_input": {"name": "review-changes"}})
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
