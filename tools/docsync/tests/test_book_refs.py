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

    def test_tmp_named_path(self):
        """RL-0077 腿：現在式面禁 tmp 具名路徑；形制句／史料面／凍結面不入射程。"""
        fs = errs(self._run({"docs/ops/a.md": "見 `tmp/003-u11-walk2b.mjs` 形\n", "tools/x.py": "# 自 tmp/001-assemble.py 入庫\n"}))
        self.assertEqual(len(fs), 2, fs)
        self.assertTrue(all("tmp/ 具名路徑" in f[3] for f in fs), fs)
        self.assertEqual(errs(self._run({"docs/ops/b.md": "`tmp/walkthrough-<刀>.json`；`tmp/004-u*`；/tmp/commit-msg.txt；工件住 tmp/\n"})), [])
        self.assertEqual(errs(self._run({
            "docs/brainstorms/x.md": "`tmp/rev5-adr-digest.md`\n",
            "specs/001-a/tasks.md": "`tmp/001-u1.py`\n",
            "docs/arc42/decisions/ADR-00001-x.md": "`tmp/constitution-1.0.0.diff`\n",
            "docs/ops/events.jsonl": '{"notes": "tmp/check-backlog.md"}\n',
            "docs/generated/MILESTONES.md": "`tmp/001-assemble.py`\n"})), [])

    def test_spec_contract_ref(self):
        """ADR-00041 腿：現在式面禁引 specs/**/contracts/**；史料面與 ADR／generated／events 豁免。"""
        fs = errs(self._run({"docs/ops/a.md": "契約＝`specs/001-schema-baseline/contracts/gates.md` §5\n",
                             "tools/x.py": "# 形＝specs/002-system-settings/contracts/wire-settings.md §4\n"}))
        self.assertEqual(len(fs), 2, fs)
        self.assertTrue(all("spec 契約檔" in f[3] for f in fs), fs)
        self.assertEqual(errs(self._run({
            "docs/brainstorms/x.md": "`specs/001-a/contracts/gates.md`\n",
            "specs/001-a/tasks.md": "`specs/001-a/contracts/gates.md`\n",
            "docs/arc42/decisions/ADR-00001-x.md": "provenance 引 `specs/001-a/contracts/gates.md`\n",
            "docs/generated/MILESTONES.md": "`specs/001-a/contracts/gates.md`\n",
            "docs/ops/events.jsonl": '{"notes": "specs/001-a/contracts/gates.md"}\n'})), [])
        self.assertEqual(errs(self._run({"docs/ops/b.md": "活體契約＝`docs/ops/reference-src/schema-gates.md`\n"})), [])
        # 裸相對形（repo 主流寫法）同樣入射程——只認絕對形＝該腿在最常見書寫形上 vacuous
        fs = errs(self._run({"tools/g.py": "# 契約＝contracts/gates.md §5\n",
                             "docs/ops/c.md": "形＝contracts/schema-evolution.md §2\n"}))
        self.assertEqual(len(fs), 2, fs)
        self.assertTrue(all("裸相對形" in f[3] for f in fs), fs)
        # 前代引用與非名冊內檔名不入射程
        self.assertEqual(errs(self._run({"docs/ops/d.md": "承 `rev5:contracts/gates.md` 改座標；另見 contracts/other.md\n"})), [])
        # 具名豁免：唯有 reference-src 的活體檔、以 `> 凍結存證＝` 起首之行
        self.assertEqual(errs(self._run({
            "docs/ops/reference-src/x.md": "> 凍結存證＝`specs/001-a/contracts/gates.md`（不再前進）\n"})), [])
        self.assertTrue(errs(self._run({
            "docs/ops/reference-src/y.md": "> 權威＝`specs/001-a/contracts/gates.md`\n"})))
        # 濫用形：同行寫「凍結存證」但不在 reference-src／不是引言行起首＝不豁免
        self.assertTrue(errs(self._run({
            "docs/ops/z.md": "凍結存證 見 `specs/001-a/contracts/gates.md` §5\n"})), "非 reference-src 不得豁免")
        self.assertTrue(errs(self._run({
            "docs/ops/reference-src/w.md": "權威＝`specs/001-a/contracts/gates.md`（凍結存證另存）\n"})), "非引言行起首不得豁免")

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


class TestGt06WrappedContractRef(unittest.TestCase):
    """BL-00114：GT-06 spec 契約腿的折行形——目錄前綴留在行尾、檔名在下一行，兩形逐行皆漏、lint 恆綠。
    判準＝行尾路徑尾段（以 / 收尾）＋下一行剝註解記號後的路徑首段拼接、再過同兩形；豁免與逐行同源（該行豁免即不拼）。"""

    def _run(self, files):
        files = dict(files)
        files.setdefault(BOOK, "# 1\n\n目前無。\n")
        return book.gt_06(stub(files))

    def test_wrapped_after_contracts_dir_is_red_with_joined_path(self):
        fs = errs(self._run({"deploy/x.toml": "# 契約＝specs/004-ip-trust-anchor/contracts/\n#    trust-model-config.md 之「dev 交付形」\n"}))
        self.assertEqual(len(fs), 1, fs)
        self.assertIn("specs/004-ip-trust-anchor/contracts/trust-model-config.md", fs[0][3])
        self.assertEqual(fs[0][2], "deploy/x.toml:1")

    def test_wrapped_after_knife_dir_names_joined_absolute_form(self):
        """spec-compliance-004 L1-1 的原形（deploy/trust-model.dev.toml 於 004 收刀時的檔頭）：逐行只有裸相對形那半紅、
        修的人只改第二行、第一行的目錄前綴殘留無聲——拼接後須另指名完整絕對形、定位在第一行。"""
        fs = errs(self._run({"deploy/x.toml": "# 契約＝specs/004-ip-trust-anchor/\n#    contracts/trust-model-config.md 之「dev 交付形」\n"}))
        self.assertTrue(any("specs/004-ip-trust-anchor/contracts/trust-model-config.md" in f[3] and f[2] == "deploy/x.toml:1" for f in fs), fs)

    def test_wrapped_bare_form_is_red(self):
        fs = errs(self._run({"docs/ops/a.md": "見 contracts/\ngates.md §5\n"}))
        self.assertEqual(len(fs), 1, fs)
        self.assertIn("contracts/gates.md", fs[0][3])

    def test_wrapped_non_contract_and_rev5_prefixed_are_green(self):
        self.assertEqual(errs(self._run({"docs/ops/a.md": "凍結存證住 specs/004-ip-trust-anchor/\nspec.md 與 plan.md\n",
                                         "docs/ops/b.md": "前代 rev5:contracts/\ngates.md 不算\n",
                                         "docs/ops/c.md": "活體 docs/ops/reference-src/\ngates.md\n"})), [])

    def test_wrapped_exempt_line_is_green(self):
        self.assertEqual(errs(self._run({"docs/ops/reference-src/x.md": "> 凍結存證＝`specs/001-a/contracts/\n> gates.md`（不再前進）\n"})), [])

