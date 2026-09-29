"""語料面：common 的正反自證（front-matter 解析、Ctx 讀檔、finding 形）。"""
import os
import tempfile
import unittest

from docsync import common
from docsync.tests import tmprepo


class TestFrontMatter(unittest.TestCase):
    def test_parses_scalar_and_list(self):
        meta, body = common.parse_front_matter(
            '---\nid: "ADR-00001"\ntags: [a, b]\nsupersedes: []\n---\n\n## 背景\n'
        )
        self.assertEqual(meta["id"], "ADR-00001")
        self.assertEqual(meta["tags"], ["a", "b"])
        self.assertEqual(meta["supersedes"], [])
        self.assertTrue(body.startswith("\n## 背景"))

    def test_nested_map_one_level(self):
        meta, _ = common.parse_front_matter('---\nsection: 3\nrad_ai: [E1]\nrad_ai_map:\n  AI Components Inventory: AI 元件清冊\n  Failure Modes: 失效模式\nprocess: P-E1-boundary.md\n---\nx\n')
        self.assertEqual(meta["rad_ai"], ["E1"])
        self.assertEqual(meta["rad_ai_map"], {"AI Components Inventory": "AI 元件清冊", "Failure Modes": "失效模式"})
        self.assertEqual(meta["process"], "P-E1-boundary.md")

    def test_no_front_matter(self):
        self.assertEqual(common.parse_front_matter("# x\n"), ({}, "# x\n"))


class TestCtx(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        tmprepo.git(self.d, "init", "-q", "-b", "main")
        with open(os.path.join(self.d, "a.md"), "w", encoding="utf-8") as f:
            f.write("A\n")
        tmprepo.git(self.d, "add", "a.md")
        tmprepo.git(self.d, "commit", "-qm", "x")

    def test_tracked_text_head(self):
        ctx = tmprepo.Ctx(self.d)
        self.assertEqual(ctx.tracked, ["a.md"])
        self.assertEqual(ctx.text("a.md"), "A\n")
        self.assertEqual(ctx.head_text("a.md"), "A\n")
        self.assertIsNone(ctx.text("nope.md"))
        self.assertEqual(ctx.md_texts(("a",)), {"a.md": "A\n"})

    def test_commit_prefetch_matches_single_and_fills_memo(self):
        """批次預取與逐個查同判（commit 真／假 SHA 假／tree 物件不算 commit）；memo 須由批次填入——批次若壞、退路會默默兜住結果而慢回原樣。"""
        ctx = tmprepo.Ctx(self.d)
        head, tree, fake = ctx.git("rev-parse", "HEAD"), ctx.git("rev-parse", "HEAD^{tree}"), "0" * 40
        ctx.prefetch_commits([head, head[:7], tree, fake, "a b"])
        self.assertEqual({s: ctx._commits.get((None, s)) for s in (head, head[:7], tree, fake)},
                         {head: True, head[:7]: True, tree: False, fake: False})
        self.assertNotIn((None, "a b"), ctx._commits)  # 含空白＝不入批次、改走逐個查
        fresh = tmprepo.Ctx(self.d)
        self.assertEqual([fresh.commit_exists(s) for s in (head, tree, fake, "a b")], [True, False, False, False])

    def test_finding_shape(self):
        self.assertEqual(
            common.finding(common.ERROR, "GT-01", "x", "y"), ("ERROR", "GT-01", "x", "y")
        )


if __name__ == "__main__":
    unittest.main()
