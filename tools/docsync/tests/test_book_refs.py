"""語料面：GT-06 引用健康（連結／行號／deep-link／per-machine 路徑／活書時態）、GT-11 bash 面、errata。"""
import os
import subprocess
import tempfile
import unittest

from docsync import book, common, RULES
from docsync.tests.test_book_ids import stub, errs


def warns(fs):
    return [f for f in fs if f[0] == "WARN"]


BOOK = "docs/arc42/01-introduction-and-goals.md"


class TestGt06(unittest.TestCase):
    def _run(self, files):
        files = dict(files)
        files.setdefault(BOOK, "# 1\n\n目前無。\n")
        return book.gt_06(stub(files))

    def test_links(self):
        self.assertEqual(errs(self._run({"docs/ops/a.md": "見 [b](b.md) 與 [外](https://x) 與 [錨](#h)\n", "docs/ops/b.md": "b\n"})), [])
        self.assertTrue(any("不存在" in f[3] for f in errs(self._run({"docs/ops/a.md": "見 [c](c.md)\n"}))))
        self.assertEqual(errs(self._run({"docs/ops/a.md": "```\n[c](c.md)\n```\n見 `[c](c.md)`\n"})), [])
        self.assertEqual(errs(self._run({"docs/ops/a.md": "見 [上層](../brainstorms/x.md#s)\n", "docs/brainstorms/x.md": "x\n"})), [])

    def test_lineno_deeplink_home(self):
        fs = errs(self._run({"docs/ops/a.md": "見 x.md:12 與 BACKLOG.md#a 與 /home/u/.claude/x 與 ~/.claude/y\n"}))
        msgs = " ".join(f[3] for f in fs)
        self.assertIn("行號", msgs)
        self.assertIn("deep-link", msgs)
        self.assertIn("per-machine", msgs)
        self.assertEqual(len(fs), 4)
        self.assertEqual(errs(self._run({"docs/ops/a.md": "```\nx.md:12 BACKLOG.md#a /home/u/.claude/x\n```\n"})), [])

    def test_tense_only_on_book_face(self):
        fs = self._run({BOOK: "# 1\n\n下一步再說；日後補。\n"})
        self.assertTrue(any("下一步" in f[3] for f in errs(fs)) and any("日後" in f[3] for f in warns(fs)))
        self.assertEqual(errs(self._run({"docs/brainstorms/x.md": "下一步\n", "docs/ops/NOTES.md": "下一步\n"})), [])
        self.assertEqual(errs(self._run({"docs/arc42/decisions/ADR-00001-x.md": "下一步\n"})), [])

    def test_book_absent_skip(self):
        fs = book.gt_06(stub({"docs/ops/a.md": "a\n"}))
        self.assertTrue(any(f[0] == "ERROR" and "活書家族" in f[3] and "缺席" in f[3] and "空集合" in f[3] for f in fs), fs)
        self.assertFalse(any(f[0] == "SKIP" for f in fs))
        self.assertTrue(any("不存在" in f[3] for f in errs(book.gt_06(stub({"docs/ops/a.md": "[c](c.md)\n"})))))


class TestGt11(unittest.TestCase):
    def test_glue_and_shebang(self):
        self.assertTrue(any("黏" in f[3] for f in errs(book.gt_11(stub({"deploy/x.sh": '#!/usr/bin/env bash\necho "$VAR全形"\n'})))))
        self.assertEqual(errs(book.gt_11(stub({"deploy/x.sh": '#!/usr/bin/env bash\necho "${VAR}全形" "$VAR"\n'}))), [])
        self.assertTrue(any("shebang" in f[3] for f in errs(book.gt_11(stub({"deploy/x.sh": "#!/usr/bin/python3\nprint(1)\n"})))))
        self.assertEqual(errs(book.gt_11(stub({".githooks/pre-commit": "#!/bin/sh\necho ok\n", ".githooks/lib/x.sh": 'a="$B"\n'}))), [])
        self.assertTrue(any("空集合" in f[3] for f in errs(book.gt_11(stub({"x.ps1": '#!/usr/bin/env pwsh\n$a全\n'})))))


class TestErrata(unittest.TestCase):
    def test_outer_and_submodule_hits(self):
        root = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
        with open(os.path.join(root, "a.md"), "w", encoding="utf-8") as f:
            f.write("第一行\n含 Foo 的行\n")
        subprocess.run(["git", "-C", root, "add", "a.md"], check=True)
        sub = os.path.join(root, "base-web")
        os.makedirs(sub)
        subprocess.run(["git", "init", "-q", "-b", "main", sub], check=True)
        with open(os.path.join(sub, "s.ts"), "w", encoding="utf-8") as f:
            f.write("// foo here\n")
        subprocess.run(["git", "-C", sub, "add", "s.ts"], check=True)
        subprocess.run(["git", "-C", sub, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], check=True)
        hits = book.errata_scan(common.Ctx(root), "foo")
        self.assertIn(("a.md", 2, "含 Foo 的行"), hits)
        self.assertTrue(any(h[0] == "base-web/s.ts" and h[1] == 1 for h in hits))
        self.assertEqual(book.errata_scan(common.Ctx(root), "zzz"), [])


if __name__ == "__main__":
    unittest.main()
