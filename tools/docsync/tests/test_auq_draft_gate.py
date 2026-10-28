"""語料面：PreToolUse(AskUserQuestion) hook（`.claude/hooks/pre-auq-draft-gate.py`；LL-00099）——送出前逐欄比對最新擬稿。
hook 自 `__file__` 推 repo 根、讀根下工作區之擬稿；為不碰真工作區（真擬稿以 mtime 取最新、測試寫入即搶位），每案把 hook 原檔
複製進暫存目錄之同構位置、擬稿寫進暫存目錄之工作區，再以 subprocess 實跑複本。"""
import copy
import json
import os
import shutil
import subprocess
import tempfile
import unittest

from docsync import ROOT

HOOK = os.path.join(ROOT, ".claude", "hooks", "pre-auq-draft-gate.py")
QS = [{"header": "銜接字面", "question": "銜接 diff 要怎麼定稿？", "multiSelect": False,
       "options": [{"label": "照 diff 定稿（建議）", "description": "銜接字面照預覽落地。", "preview": "+ 上列十島\n- 上列九島"},
                   {"label": "拉出逐款問", "description": "逐款再問一次。"}]}]


class TestAuqDraftGate(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = self._td.name
        os.makedirs(os.path.join(self.root, ".claude", "hooks"))
        self.hook = shutil.copy(HOOK, os.path.join(self.root, ".claude", "hooks"))

    def tearDown(self):
        self._td.cleanup()

    def draft(self, rel, qs, mtime=None):
        path = os.path.join(self.root, "tmp", rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(qs, f, ensure_ascii=False)
        if mtime is not None:
            os.utime(path, (mtime, mtime))
        return path

    def run_hook(self, payload):
        stdin = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        p = subprocess.run(["python3", self.hook], input=stdin, capture_output=True, text=True, encoding="utf-8", cwd=self.root)
        return p.returncode, p.stderr

    def test_identical_passes_and_missing_multiselect_means_false(self):
        self.draft(os.path.join("x-auq", "q1.json"), QS)
        sent = copy.deepcopy(QS)
        del sent[0]["multiSelect"]
        rc, err = self.run_hook({"tool_input": {"questions": sent}})
        self.assertEqual(rc, 0, err)

    def test_single_codepoint_drift_blocked_with_field_and_codepoints(self):
        self.draft(os.path.join("x-auq", "q1.json"), QS)
        sent = copy.deepcopy(QS)
        sent[0]["header"] = "銃接字面"
        sent[0]["options"][0]["preview"] = "+ 上列十鳥\n- 上列九島"
        rc, err = self.run_hook({"tool_input": {"questions": sent}})
        self.assertEqual(rc, 2)
        self.assertIn("不符 2 欄", err)
        self.assertIn(os.path.join("tmp", "x-auq", "q1.json"), err)
        for lit in ("q1.header", f"U+{ord('銜'):04X}", f"U+{ord('銃'):04X}",
                    "q1.opt1.preview", f"U+{ord('島'):04X}", f"U+{ord('鳥'):04X}", "第 6 字起不同"):
            self.assertIn(lit, err)

    def test_structure_diff_blocked(self):
        self.draft(os.path.join("x-auq", "q1.json"), QS)
        sent = copy.deepcopy(QS)
        sent[0]["options"].append({"label": "多一項", "description": "擬稿無此項。"})
        rc, err = self.run_hook({"tool_input": {"questions": sent}})
        self.assertEqual(rc, 2)
        self.assertIn("q1.選項數", err)
        self.assertIn("q1.opt3.label：擬稿 無此欄", err)

    def test_latest_auq_draft_wins_and_non_auq_paths_ignored(self):
        other = copy.deepcopy(QS)
        other[0]["question"] = "另一題？"
        self.draft(os.path.join("x-auq", "old.json"), QS, mtime=1_000_000)
        newer = self.draft(os.path.join("x-auq", "new.json"), other, mtime=2_000_000)
        self.draft(os.path.join("plain", "newest.json"), QS, mtime=3_000_000)   # 路徑不含 auq：不入候選
        rc, err = self.run_hook({"tool_input": {"questions": QS}})
        self.assertEqual(rc, 2)
        self.assertIn("new.json", err)
        self.assertIn("q1.question", err)
        os.utime(newer, (500_000, 500_000))
        rc, err = self.run_hook({"tool_input": {"questions": QS}})
        self.assertEqual(rc, 0, err)

    def test_no_draft_blocked(self):
        rc, err = self.run_hook({"tool_input": {"questions": QS}})
        self.assertEqual(rc, 2)
        self.assertIn("找不到擬稿", err)

    def test_malformed_draft_blocked(self):
        self.draft(os.path.join("x-auq", "q1.json"), {"questions": QS})   # 多包一層＝非題目陣列
        rc, err = self.run_hook({"tool_input": {"questions": QS}})
        self.assertEqual(rc, 2)
        self.assertIn("讀不成題目陣列", err)

    def test_non_json_or_no_questions_passes(self):
        self.assertEqual(self.run_hook("not json")[0], 0)
        self.assertEqual(self.run_hook({"tool_input": {}})[0], 0)


if __name__ == "__main__":
    unittest.main()
