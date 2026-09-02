"""語料面：GT-05 ID 家族（next／唯一／單調／不回收）、跨代裸編號（面×提及×刀集）、子庫碼面；GT-08 LESSONS 側。"""
import os
import subprocess
import tempfile
import unittest

from docsync import book, common, rules, BACKLOG, LESSONS_DIR, RULES

RULES_TEXT = """<!-- next: RL-0003 -->
# RULES
上限（D8）：總 3｜implementer 2｜主線 2。

| id | 規則 | scope | carrier | source |
|---|---|---|---|---|
| RL-0001 | 先查紀錄。 | 主線,implementer | prompt | rev5:L-003 |
| RL-0002 | 只讀不寫。 | implementer | prompt | ADR-00003 |
"""


def stub(files, head=None, tracked=None):
    """假 Ctx：text／head_text 讀 dict、exists 看鍵或目錄前綴、git 一律 GitError（無子庫）。"""
    c = common.Ctx.__new__(common.Ctx)
    c.root = "/nonexistent"
    c._cache = dict(files)
    c.tracked = list(tracked if tracked is not None else files)
    head = head or {}
    c.head_text = lambda rel: head.get(rel)
    c.exists = lambda rel: rel in files or any(k.startswith(rel.rstrip("/") + "/") for k in files)
    def _git(*a, cwd=None):
        raise common.GitError("no git")
    c.git = _git
    c.git_try = lambda *a, cwd=None: (128, "")
    return c


def errs(fs):
    return [f for f in fs if f[0] == "ERROR"]


class TestFamilies(unittest.TestCase):
    def test_green_dup_over_next(self):
        good = {RULES: RULES_TEXT, BACKLOG: "<!-- next: BL-00003 -->\n- BL-00001｜a\n- BL-00002｜b\n"}
        self.assertEqual([f for f in errs(book.gt_05(stub(good))) if "BL" in f[3] or "BACKLOG" in f[2]], [])
        dup = dict(good, **{BACKLOG: "<!-- next: BL-00003 -->\n- BL-00001｜a\n- BL-00001｜b\n"})
        self.assertTrue(any("重複" in f[3] for f in errs(book.gt_05(stub(dup)))))
        over = dict(good, **{BACKLOG: "<!-- next: BL-00003 -->\n- BL-00005｜a\n"})
        self.assertTrue(any("next" in f[3] for f in errs(book.gt_05(stub(over)))))
        nonext = dict(good, **{BACKLOG: "- BL-00001｜a\n"})
        self.assertTrue(any("next-id" in f[3] for f in errs(book.gt_05(stub(nonext)))))

    def test_next_monotonic_and_no_recycle_vs_head(self):
        cur = {RULES: RULES_TEXT, BACKLOG: "<!-- next: BL-00003 -->\n- BL-00001｜a\n- BL-00002｜b\n"}
        head = {BACKLOG: "<!-- next: BL-00004 -->\n- BL-00001｜a\n- BL-00003｜c\n"}
        msgs = [f[3] for f in errs(book.gt_05(stub(cur, head=head)))]
        self.assertTrue(any("單調" in m for m in msgs) and any("回收" in m for m in msgs))

    def test_ledgers_absent_skip_and_rules_absent_red(self):
        fs = book.gt_05(stub({RULES: RULES_TEXT}))
        self.assertEqual(sorted({f[3].split("：")[0] for f in fs if f[0] == "SKIP"}), ["GT-05.ledgers-absent", "GT-05.submodule-absent"])
        self.assertTrue(any("RULES" in f[2] and "空集合" in f[3] for f in errs(book.gt_05(stub({})))))


class TestBareRev5(unittest.TestCase):
    def _run(self, rel, line, extra=None):
        files = {RULES: RULES_TEXT, rel: line + "\n"}
        files.update(extra or {})
        return [f for f in errs(book.gt_05(stub(files))) if f[2].startswith(rel)]

    def test_faces_and_mentions(self):
        self.assertTrue(self._run("docs/ops/x.md", "見 L-011 條"))
        self.assertTrue(self._run("tools/x.py", "# 承 B-042"))
        self.assertEqual(self._run("docs/brainstorms/x.md", "見 L-011 條"), [])
        self.assertEqual(self._run(".claude/skills/x/SKILL.md", "見 L-011 條"), [])
        self.assertEqual(self._run("tools/docsync/tests/x.py", "L-011"), [])
        self.assertEqual(self._run("docs/ops/x.md", "見 rev5:L-011 條"), [])
        self.assertEqual(self._run("docs/ops/x.md", "見 `L-011` 條"), [])
        self.assertEqual(self._run("docs/ops/x.md", "見「L-011」條"), [])
        self.assertTrue(self._run("docs/ops/x.md", "承 ADR 0012 與 Lint25"))

    def test_knife_names(self):
        self.assertTrue(self._run("docs/ops/x.md", "刀 001-foo-bar 收刀"))
        self.assertEqual(self._run("docs/ops/x.md", "刀 001-foo-bar 收刀", extra={"specs/001-foo-bar/spec.md": "# s\n"}), [])
        self.assertEqual(self._run("docs/ops/x.md", "單段 001-foo 不在射程（正則要求兩段以上、避 256-bit 誤中）"), [])
        self.assertEqual(self._run("docs/ops/x.md", "見 000-x-y 啟動書"), [])
        self.assertEqual(self._run("docs/ops/x.md", "見 rev5:008-audit-settings-pages"), [])


class TestSubmoduleScan(unittest.TestCase):
    def test_hit_in_submodule_is_red(self):
        root = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
        with open(os.path.join(root, "RULES.md"), "w") as f:
            f.write("x")
        sub = os.path.join(root, "base-web")
        os.makedirs(sub)
        subprocess.run(["git", "init", "-q", "-b", "main", sub], check=True)
        with open(os.path.join(sub, "a.ts"), "w", encoding="utf-8") as f:
            f.write("// see L-011 and B-042\n")
        subprocess.run(["git", "-C", sub, "add", "a.ts"], check=True)
        subprocess.run(["git", "-C", sub, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], check=True)
        fs = book.gt_05(common.Ctx(root))
        self.assertTrue(any(f[0] == "ERROR" and "base-web" in f[2] for f in fs))
        self.assertTrue(any(f[0] == "SKIP" and "rust-api" in f[3] for f in fs))


class TestGt08LessonsSide(unittest.TestCase):
    def _lesson(self, rule_id="RL-0001", surface="rules", recurrence=None, first="LL-00001｜坑名"):
        fm = f'---\nid: "LL-00001"\nrule_id: {rule_id}\npromotion_surface: {surface}\n'
        if recurrence is not None:
            fm += f"recurrence_of: {recurrence}\n"
        return fm + f"---\n\n{first}\n\n本文。\n"

    def test_green_bad_rule_and_absent(self):
        rel = f"{LESSONS_DIR}/LL-00001-x.md"
        RULES_TEXT_ = RULES_TEXT
        base = {RULES: RULES_TEXT_, "docs/arc42/decisions/ADR-00003-x.md": "---\nid: \"ADR-00003\"\n---\n"}
        stub_ = lambda files: stub(dict(base, **files))
        self.assertEqual(errs(rules.gt_08(stub_({rel: self._lesson()}))), [])
        self.assertTrue(any("rule_id" in f[3] for f in errs(rules.gt_08(stub_({rel: self._lesson(rule_id="RL-9999")})))))
        self.assertTrue(any("promotion_surface" in f[3] for f in errs(rules.gt_08(stub_({rel: self._lesson(surface="zzz")})))))
        self.assertTrue(any("首行" in f[3] for f in errs(rules.gt_08(stub_({rel: self._lesson(first="LL-00002｜錯")})))))
        self.assertTrue(any("recurrence_of" in f[3] for f in errs(rules.gt_08(stub_({rel: self._lesson(recurrence="LL-00009")})))))
        self.assertEqual(errs(rules.gt_08(stub_({rel: self._lesson(rule_id="none：尚無規則位", surface="none", recurrence="RL-0002")}))), [])
        fs = rules.gt_08(stub_({}))
        self.assertTrue(any(f[0] == "SKIP" and "GT-08.lessons-absent" in f[3] for f in fs))


if __name__ == "__main__":
    unittest.main()
