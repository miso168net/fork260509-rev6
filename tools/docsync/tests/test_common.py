"""語料面：common 的正反自證（front-matter 解析、Ctx 讀檔、finding 形）。"""
import os
import subprocess
import tempfile
import unittest

from docsync import common


class TestFrontMatter(unittest.TestCase):
    def test_parses_scalar_and_list(self):
        meta, body = common.parse_front_matter(
            '---\nid: "ADR-00001"\ntags: [a, b]\nsupersedes: []\n---\n\n## 背景\n'
        )
        self.assertEqual(meta["id"], "ADR-00001")
        self.assertEqual(meta["tags"], ["a", "b"])
        self.assertEqual(meta["supersedes"], [])
        self.assertTrue(body.startswith("\n## 背景"))

    def test_no_front_matter(self):
        self.assertEqual(common.parse_front_matter("# x\n"), ({}, "# x\n"))


class TestCtx(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", "-b", "main", self.d], check=True)
        with open(os.path.join(self.d, "a.md"), "w", encoding="utf-8") as f:
            f.write("A\n")
        subprocess.run(["git", "-C", self.d, "add", "a.md"], check=True)
        subprocess.run(
            ["git", "-C", self.d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"],
            check=True,
        )

    def test_tracked_text_head(self):
        ctx = common.Ctx(self.d)
        self.assertEqual(ctx.tracked, ["a.md"])
        self.assertEqual(ctx.text("a.md"), "A\n")
        self.assertEqual(ctx.head_text("a.md"), "A\n")
        self.assertIsNone(ctx.text("nope.md"))
        self.assertEqual(ctx.md_texts(("a",)), {"a.md": "A\n"})

    def test_finding_shape(self):
        self.assertEqual(
            common.finding(common.ERROR, "GT-01", "x", "y"), ("ERROR", "GT-01", "x", "y")
        )


if __name__ == "__main__":
    unittest.main()
