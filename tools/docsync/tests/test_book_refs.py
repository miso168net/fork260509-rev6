"""語料面：GT-06 引用健康（連結／行號／deep-link／per-machine 路徑／活書時態／tmp 具名路徑／spec 契約檔引用／NOTES 下一步收單句）、GT-11 bash 面、errata。"""
import os
import tempfile
import unittest

from docsync import book, RULES, ROOT
from docsync.tests import tmprepo
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
        self.assertTrue(any("下一步" in f[3] for f in errs(fs)) and any("日後" in f[3] for f in errs(fs)))
        self.assertEqual(warns(fs), [])   # BL-00036③：時態不留 WARN 分級（RL-0015 carrier=lint）
        self.assertEqual(errs(self._run({"docs/brainstorms/x.md": "下一步\n", "docs/ops/NOTES.md": "## 下一步\n下一步\n"})), [])
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
        tmprepo.git(root, "init", "-q", "-b", "main")
        with open(os.path.join(root, "a.md"), "w", encoding="utf-8") as f:
            f.write("第一行\n含 Foo 的行\n")
        tmprepo.git(root, "add", "a.md")
        sub = os.path.join(root, "base-web")
        os.makedirs(sub)
        tmprepo.git(sub, "init", "-q", "-b", "main")
        with open(os.path.join(sub, "s.ts"), "w", encoding="utf-8") as f:
            f.write("// foo here\n")
        tmprepo.git(sub, "add", "s.ts")
        tmprepo.git(sub, "commit", "-qm", "x")
        hits = book.errata_scan(tmprepo.Ctx(root), "foo")
        self.assertIn(("a.md", 2, "含 Foo 的行"), hits)
        self.assertTrue(any(h[0] == "base-web/s.ts" and h[1] == 1 for h in hits))
        self.assertEqual(book.errata_scan(tmprepo.Ctx(root), "zzz"), [])


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
        self.assertEqual(errs(self._run({"docs/ops/a.md": "凍結存證住 `specs/004-ip-trust-anchor/`\n`spec.md` 與 plan.md\n",
                                         "docs/ops/b.md": "前代 rev5:contracts/\ngates.md 不算\n",
                                         "docs/ops/c.md": "活體 docs/ops/reference-src/\ngates.md\n"})), [])

    def test_wrapped_exempt_line_is_green(self):
        self.assertEqual(errs(self._run({"docs/ops/reference-src/x.md": "> 凍結存證＝`specs/001-a/contracts/\n> gates.md`（不再前進）\n"})), [])

    def test_crlf_and_trailing_spaces_still_wrap(self):
        """尾段的 `\\s*$` 是判準的一部分（CRLF 之 CR、markdown 硬換行的行尾雙空白）——釘住，讓拿掉它的變異有案可擋（review L1-5）。"""
        fs = errs(self._run({"docs/ops/a.md": "見 contracts/  \r\ngates.md\r\n", "docs/ops/b.md": "見 specs/001-a/contracts/  \ngates.md\n"}))
        self.assertEqual(sorted(f[2] for f in fs), ["docs/ops/a.md:1", "docs/ops/b.md:1"], fs)

    def test_backticked_wrap_is_red(self):
        """repo 主流寫法把路徑包在反引號裡：行尾 `/` 後接收尾反引號、下一行以反引號起首，同樣拼接（review L1-6 形 (a)）。"""
        fs = errs(self._run({"docs/ops/a.md": "契約＝`specs/004-ip-trust-anchor/contracts/`\n`trust-model-config.md` 之「dev 交付形」\n"}))
        self.assertEqual(len(fs), 1, fs)
        self.assertIn("specs/004-ip-trust-anchor/contracts/trust-model-config.md", fs[0][3])

    def test_dangling_prefix_after_half_fix_is_red(self):
        """BL-00114 立案所引的真實殘留態（review L1-1）：折行指針只改了第二行、目錄前綴懸在第一行行尾——
        拼接腿對此零命中（下一行已不是契約名），須由懸空前綴腿另抓。"""
        fs = errs(self._run({"deploy/x.toml": "# 契約＝specs/004-ip-trust-anchor/\n#    `docs/ops/reference-src/trust-model-config.md` 之「dev 交付形」\n",
                             "docs/ops/a.md": "見 specs/004-ip-trust-anchor/contracts/\n（下一行是散文）\n"}))
        self.assertEqual(sorted(f[2] for f in fs), ["deploy/x.toml:1", "docs/ops/a.md:1"], fs)
        self.assertTrue(all("懸空" in f[3] for f in fs), fs)

    def test_dangling_is_not_double_reported_when_wrap_hits(self):
        fs = errs(self._run({"deploy/x.toml": "# 契約＝specs/004-ip-trust-anchor/\n#    contracts/trust-model-config.md 之「dev 交付形」\n"}))
        self.assertEqual(sorted(f[2] for f in fs), ["deploy/x.toml:1", "deploy/x.toml:2"], fs)
        self.assertFalse(any("懸空" in f[3] for f in fs), fs)

    def test_raw_dangling_before_non_contract_wrap_is_still_red(self):
        """嚴格形（刻意）：裸露的目錄前綴懸在行尾一律紅，即使下一行接的是 `spec.md` 這種非契約檔——repo 路徑一律反引號、
        裸露前綴只在半修殘留時出現；要寫合法折行請把路徑收進反引號（上一案的綠形）。"""
        fs = errs(self._run({"docs/ops/a.md": "凍結存證住 specs/004-ip-trust-anchor/\nspec.md 與 plan.md\n"}))
        self.assertEqual([f[2] for f in fs], ["docs/ops/a.md:1"], fs)
        self.assertIn("懸空", fs[0][3])

    def test_dangling_negatives_are_green(self):
        self.assertEqual(errs(self._run({"docs/ops/a.md": "凍結存證住 `specs/004-ip-trust-anchor/`\n",
                                         "docs/ops/b.md": "見 specs/004-ip-trust-anchor/spec.md\n",
                                         "docs/ops/reference-src/x.md": "> 凍結存證＝specs/001-a/contracts/\n"})), [])



TENSE = "時態禁詞"   # 時態腿全部訊息共有的字面


def _bp(key, val, top="rev5_blueprint"):
    """活書 frontmatter 樁：`<top>:` 一層巢狀對映、單一子鍵（ADR-00006 決定 1 之 rev5_blueprint 形）。"""
    return f"---\nsection: 6\n{top}:\n  {key}: {val}\n---\n# 6\n\n目前無。\n"


class TestGt06Tense(unittest.TestCase):
    """RL-0015 承載（BL-00036③）：活書家族未來式同義集——待決／TBD／⏳／已完成／下一步＋屆時／日後／將由＋「隨…進場」與「尚無」——
    詞表單一家、一律 ERROR（RL-0015 carrier=lint、無 ADR 定 WARN）；提及形口徑＝現行 `strip_code`（程式碼剝除、「」不剝）。
    唯一豁免＝ADR-00006 決定 1 之值形：活書 frontmatter `rev5_blueprint:` 子鍵中以「隨刀：」起頭之值，只免該值內「隨…進場」形。"""

    def _run(self, text, rel=BOOK):
        return book.gt_06(stub({rel: text}))

    def tense(self, fs):
        return [f for f in fs if TENSE in f[3]]

    def test_all_synonyms_are_error_without_warn_tier(self):
        """反：兩新形與三舊預告詞各一行→逐行 ERROR（訊息引 RL-0015、附補救）、零 WARN；詞表不再分 WARN 級。"""
        fs = self._run("# 1\n\n甲隨各域刀進場。\n乙系統層尚無實例。\n丙屆時補。\n丁日後補。\n戊將由某刀補。\n")
        tense = self.tense(fs)
        self.assertEqual(sorted(f[2] for f in tense), [f"{BOOK}:{i}" for i in (3, 4, 5, 6, 7)], tense)
        self.assertTrue(all(f[0] == "ERROR" and "RL-0015" in f[3] and "補救" in f[3] for f in tense), tense)
        self.assertEqual(warns(fs), [])
        self.assertFalse(hasattr(book, "TENSE_WARN"))

    def test_present_tense_and_code_mentions_are_green(self):
        """正：現在式、行內程式碼與 fenced 內之同義詞（提及形）不判；「隨…、…進場」跨句讀標點不成形。"""
        text = ("# 1\n\n目前無實例（理由：系統本體無此元件）。\n見 `隨刀進場`、`尚無` 與 `日後` 三形。\n"
                "```\n隨各域刀進場；尚無；屆時\n```\n隨機抽樣、進場檢查分屬兩事。\n")
        self.assertEqual(self.tense(self._run(text)), [])

    def test_follow_form_is_bounded_and_stops_at_clause_punctuation(self):
        """「隨…進場」間隔上界 25 字（全 repo 實掃：真命中最長 25、跨子句誤併最短 29）、不跨句讀標點與表格欄界；
        「：」刻意不當界——ADR-00006 值形 `隨刀：<…>` 以之分隔，當界即讓正文同形漏網。"""
        self.assertEqual(len(self.tense(self._run("# 1\n\n隨" + "甲" * 25 + "進場\n"))), 1)
        self.assertEqual(self.tense(self._run("# 1\n\n隨" + "甲" * 26 + "進場\n")), [])
        for sep in "。，、；！？,;!?|｜":
            self.assertEqual(self.tense(self._run(f"# 1\n\n隨島{sep}另案進場\n")), [], sep)
        self.assertEqual(len(self.tense(self._run("# 1\n\n隨刀：憲法 §I.7 島 X 進場刀\n"))), 1)

    def test_adr00006_follow_value_exempts_only_its_follow_form(self):
        """正：rev5_blueprint 子鍵值以「隨刀：」起頭（含引號值）→ 該值內「隨…進場」免判；
        反：同值他詞（尚無）照判、只指該詞；鍵字面內之「隨…進場」照判。"""
        self.assertEqual(self.tense(self._run(_bp("使用者域斷權", "隨刀：憲法 §I.7 島 I 進場刀（使用者域）"))), [])
        self.assertEqual(self.tense(self._run(_bp("k", '"隨刀：憲法 §I.7 島 I 進場刀"'))), [])
        fs = self.tense(self._run(_bp("k", "隨刀：島 I 進場刀；尚無內容")))
        self.assertTrue(len(fs) == 1 and "「尚無」" in fs[0][3] and fs[0][2] == f"{BOOK}:4", fs)
        fs = self.tense(self._run(_bp("隨島進場之節", "隨刀：島 I 進場刀")))
        self.assertTrue(len(fs) == 1 and "「隨島進場」" in fs[0][3], fs)

    def test_other_frontmatter_and_body_are_judged(self):
        """反：非「隨刀：」起頭之 rev5_blueprint 值、非 rev5_blueprint 之欄（含他巢狀對映）同值形、正文同形——逐一照判。"""
        for text in (_bp("§6", "承襲（方針段）；情境隨島進場"),
                     _bp("§3", "不承襲：rev5 空節（該節自述尚無內容）"),
                     "---\nsection: 6\nsummary: 隨刀：島 I 進場刀\n---\n# 6\n",
                     _bp("k", "隨刀：島 I 進場刀", top="other"),
                     "---\nsection: 6\n---\n# 6\n\n  k: 隨刀：島 I 進場刀\n"):
            self.assertEqual(len(self.tense(self._run(text))), 1, text)

    def test_follow_value_exemption_is_bounded_to_frontmatter(self):
        """反：豁免只在 frontmatter 界內（檔首 `---` 起、首個閉合 `---` 止）——界外即使帶完整 `rev5_blueprint:` 鍵行＋
        「隨刀：」子行也照判。①frontmatter 閉合後的正文 ②檔首非 `---`（無 frontmatter）、後文水平線 `---` 之前——各恰 1 筆、指該子行。
        ★判準變異：拿掉 frontmatter 界（逐行掃全檔）→①②皆轉紅；只拿掉「檔首須為 `---`」→②轉紅。"""
        for text, line in (("---\nsection: 6\n---\n# 6\n\nrev5_blueprint:\n  k: 隨刀：島 I 進場刀\n", 7),
                           ("# 6\n\nrev5_blueprint:\n  k: 隨刀：島 I 進場刀\n\n---\n", 4)):
            fs = self.tense(self._run(text))
            self.assertEqual([f[2] for f in fs], [f"{BOOK}:{line}"], text)

    def test_real_book_face_zero_hits_and_exemption_has_real_instance(self):
        """真 repo：活書家族時態零命中；豁免的受守面有實例時、其中確有「隨…進場」被免（RL-0067）。
        受守面＝活書家族全檔 frontmatter 之 `隨刀：` 值；零實例＝紅證 vacuous（豁免機制由上列合成語料之正反案守）——
        007 刀島 I 進場後活書家族已無 `隨刀：` 值；任一活書再出現該值即自動恢復實例斷言。"""
        from docsync import common
        from docsync.tests.test_gates import real_lint
        fs, _ = real_lint()
        self.assertEqual([f for f in fs if TENSE in f[3]], [])
        hits = {}
        for rel in common.Ctx(ROOT).tracked:
            if not (rel.endswith(".md") and book.is_book(rel)):
                continue
            with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
                lines = book.strip_code(fh.read()).split("\n")
            for i, c in book._blueprint_follow_cols(lines).items():
                hits[f"{rel}:{i}"] = bool(book.RE_TENSE_ENTER.search(lines[i - 1], c))
        if hits:
            self.assertTrue(any(hits.values()), hits)


NOTES = book.NOTES
NOTES_LEG = "「## 下一步」節"   # 收單句腿全部訊息共有的字面


def _notes(*next_lines, now="- 現況一句。", pending="- 未決一句。", tail=True):
    """NOTES 樁：波標記＋現況／下一步／未決三節（tail=False＝下一步為末節、至檔尾止）；回 (text, 下一步節首行之行號)。"""
    head = ["<!-- wave: 6 -->", "# NOTES", "", "## 現況", "", now, "", "## 下一步", ""]
    rest = ["", "## 未決", "", pending, ""] if tail else [""]
    return "\n".join(head + list(next_lines) + rest), len(head) + 1


class TestGt06NotesDone(unittest.TestCase):
    """RL-0048 完成即刪、git 即史：NOTES「## 下一步」節不留整刀／整批／整輪之收單句——只掃該節、先剝程式碼（提及原則）；
    刀內進度句（裸「已收」接標點、「已完成」「已定稿」）與合法現在式／未來式照寫。掃描面＝該節：NOTES 在 tracked 而缺節即紅
    （RL-0051）；NOTES 不在 tracked 或讀不到＝本腿不另報，兜底逐途徑見 `_notes_done_leg` docstring 與途徑①③、途徑②兩案。
    ★判準變異：拿掉樣式任一分支→對應收單形轉綠（本類紅）；節界改掃全檔→節外案紅；拿掉空面判→缺節案紅；
    不剝程式碼→提及案紅；樣式加入裸「已收」→刀內進度案紅；拿掉「的」修飾形排除→修飾形案紅；每行只報首筆→同行多處案紅；
    拿掉 tracked 閘（改讀磁碟）→途徑②案紅。"""

    def _run(self, notes, extra=None):
        files = {BOOK: "# 1\n\n目前無。\n", NOTES: notes}
        files.update(extra or {})
        return book.gt_06(stub(files))

    def leg(self, fs):
        return [f for f in fs if NOTES_LEG in f[3]]

    def test_closure_forms_in_next_section_are_red_per_occurrence(self):
        """反：實見收單形逐行一筆 ERROR、指該行並帶命中字面、附依據與補救；「已全數收單」「三支皆已收單」各只一筆（不重複計）。"""
        forms = [("- 已收刀＝001 schema 基線（波 6 首刀）、002 system-settings（波 6 第二刀）。", "已收刀"),
                 ("- **006 已收刀**：逐單元交付、merge SHA、ADR 清單。", "已收刀"),
                 ("- **時區裁定施作（user 逐題裁定）＝已收單**：DB 伺服器時區固定。", "已收單"),
                 ("- **005 前維護批（七支輕量軌）＝已全數收單**：逐支交付查 MILESTONES。", "已全數收單"),
                 ("- **006 前 BACKLOG 體檢 v5＝三支皆已收單**：逐支交付。", "已收單"),
                 ("- **七支全數收單後＝005 role-menu-crud**。", "全數收單"),
                 ("- 規格對照審查五輪（RL-0073 ②）皆已收：002 刀與 003 刀。", "皆已收"),
                 ("- 003 刀收刀後兩支維護批甲、乙皆已收（逐條見 MILESTONES）。", "皆已收"),
                 ("- 002 刀之規格對照輪兩輪皆已收", "皆已收")]
        text, first = _notes(*(line for line, _ in forms))
        fs = self.leg(self._run(text))
        self.assertEqual([(f[0], f[2]) for f in fs], [("ERROR", f"{NOTES}:{first + k}") for k in range(len(forms))], fs)
        for f, (_, w) in zip(fs, forms):
            self.assertIn(f"「{w}」", f[3])
            self.assertTrue(all(s in f[3] for s in ("收單句", "RL-0048", "完成即刪", "整段刪除", "docs/generated/MILESTONES.md")), f)

    def test_multiple_hits_on_one_line_are_one_finding_each(self):
        """判準＝節內每處一筆、非每行一筆：同一行多處收單字樣（實見形＝一行逐支列「（已收單）」）→同一行號逐處一筆 ERROR、
        各帶其命中字面（同字面重複亦逐處計）。★變異：每行只報首筆＝本案紅。"""
        text, first = _notes("- 甲", "- 順序＝甲（已收單）→ 乙（已收單）→ 丙＝三支全數收單")
        fs = self.leg(self._run(text))
        self.assertEqual([(f[0], f[2]) for f in fs], [("ERROR", f"{NOTES}:{first + 1}")] * 3, fs)
        self.assertEqual([f[3].split("收單句「", 1)[1].split("」", 1)[0] for f in fs], ["已收單", "已收單", "全數收單"], fs)

    def test_progress_and_legit_forms_are_green(self):
        """正：刀內進度句（裸「已收」後接標點——無反引號亦不中）、「已完成」「已完」「已定稿」與合法現在式／未來式零命中。"""
        text, _ = _notes("- **TDD 進行中**：U0 已收（ADR-00026 accepted）；U1 進行中。",
                         "- `/speckit-clarify` 已收（`bf30d03`；三題皆採建議）→ 下一步 plan。",
                         "- specify、clarify 已完成（分支同名）；SDD 五步已完（含 analyze）。",
                         "- 階段 0 brainstorm 已定稿（見 brainstorm 檔）。",
                         "- 候選已收錄、爭點皆已收斂、射程已收窄；BL-00045 已附密碼政策投影快取連動之評估點。",
                         "- 每次獨立輪收單隨 review 事件 probe 欄更新；每支帶 migration 的刀收刀前必跑三步；兩批收單後由 user 手動發起。")
        self.assertEqual(errs(self._run(text)), [])

    def test_declared_out_of_reach_forms_are_green(self):
        """射程外（樣式常數旁註解逐條列名）：①裸「已收」接標點（刀內進度共用此形，整批／整輪偶用者一併漏網）
        ②「已收刀的」「已收單的」修飾形（指稱已收之刀類、非收單句）③「已由某批收」從句形與「收於」形——皆零命中。"""
        text, _ = _notes("- 維護批甲已收（逐條見 MILESTONES）；002 刀之輪已收（報告見 reviews）。",
                         "- schema 定稿權威住 reference-src——不再回頭改已收刀的 spec 目錄；已收單的批不再重開。",
                         "- 該條已由下條維護批收；本批收於某顆。")
        self.assertEqual(self.leg(self._run(text)), [])

    def test_out_of_section_and_code_mentions_are_green(self):
        """正：「## 現況」「## 未決」節與他檔之收單形不在射程；節內反引號與 fenced 內之提及不算。"""
        text, _ = _notes("- 收單句字樣之提及：`006 已收刀`、`＝已收單`、`皆已收：`。", "```", "- 007 已收刀", "```",
                         now="- 006 已收刀（現況節不在射程）。", pending="- 某批＝已收單（未決節不在射程）。")
        self.assertEqual(errs(self._run(text, extra={"docs/ops/x.md": "## 下一步\n\n- 006 已收刀；某批＝已收單\n"})), [])

    def test_section_bounds(self):
        """節界：起＝rstrip 後恰為 `## 下一步` 之行（容行尾空白／CR）、子節 `### ` 仍在節內、止於下一個 `## ` 行（不含）或檔尾。"""
        text = "<!-- wave: 6 -->\n## 下一步  \r\n\n### 細項\n- 006 已收刀\n## 未決\n- 007 已收刀\n"
        self.assertEqual([f[2] for f in self.leg(self._run(text))], [f"{NOTES}:5"])
        text, first = _notes("- 甲", "- **006 已收刀**", tail=False)
        self.assertEqual([f[2] for f in self.leg(self._run(text))], [f"{NOTES}:{first + 1}"])

    def test_missing_next_section_is_red(self):
        """空面（RL-0051）：NOTES 在 tracked 而無「## 下一步」節（缺節、改名、少了 `## `）→恰一筆 ERROR、指名缺節與補救；
        改名節下之收單形不入射程、不另報。"""
        for text in ("<!-- wave: 6 -->\n## 現況\n\n- x\n\n## 未決\n\n- y\n",
                     "<!-- wave: 6 -->\n## 下一步（舊稿）\n\n- 006 已收刀\n",
                     "<!-- wave: 6 -->\n下一步\n\n- 006 已收刀\n"):
            fs = self.leg(self._run(text))
            self.assertEqual(len(fs), 1, (text, fs))
            self.assertEqual((fs[0][0], fs[0][2]), ("ERROR", NOTES), fs)
            self.assertTrue(all(s in fs[0][3] for s in ("缺席", "RL-0051", "空集合", "恢復", "節標題")), fs)

    def test_absent_notes_is_silent_and_gt10_backstops(self):
        """兜底途徑①（不在 tracked、不在磁碟）與③（在 tracked、工作樹讀不到）：本腿零筆；兜底之實證＝同一樁上 gt_10
        波標記缺席腿為 ERROR（current_wave 讀磁碟、讀不到即缺席）。途徑②見下一案。"""
        files = {BOOK: "# 1\n\n目前無。\n"}
        for tracked in ([BOOK], [BOOK, NOTES]):    # ①、③（樁無 NOTES 內容＝讀不到）
            ctx = stub(files, tracked=tracked)
            self.assertEqual(self.leg(book.gt_06(ctx)), [], tracked)
            self.assertTrue(any(f[0] == "ERROR" and "波標記缺席" in f[3] for f in book.gt_10(ctx)), tracked)

    def test_untracked_on_disk_notes_backstop_is_gt12_index_leg(self):
        """兜底途徑②（在磁碟而未入 tracked，如 `git rm --cached`）：射程以 tracked 為準＝本腿零筆、不讀其內容；gt_10 讀磁碟照見
        波標記＝零筆（非此途徑之兜底）。兜底＝GT-12 工作樹⇔暫存區一致性腿：暫存區≠HEAD 時報該檔未追蹤 ERROR。
        據實釘住兩處無兜底：該檔被 ignore、或暫存區＝HEAD（無 commit 在準備）時該腿零筆。"""
        import shutil
        from docsync import gates
        root = tmprepo.make_repo({BOOK: "# 1\n\n目前無。\n", NOTES: "<!-- wave: 6 -->\n## 下一步\n\n- **006 已收刀**\n"})
        self.addCleanup(shutil.rmtree, root, True)
        tmprepo.git(root, "rm", "-q", "--cached", NOTES)       # 暫存區刪、磁碟仍在＝暫存區≠HEAD
        ctx = tmprepo.Ctx(root)
        self.assertNotIn(NOTES, ctx.tracked)
        self.assertEqual(self.leg(book.gt_06(ctx)), [])
        self.assertEqual([f for f in book.gt_10(ctx) if "波標記缺席" in f[3]], [])
        fs = gates._index_consistency_leg(ctx)
        self.assertEqual([f[:3] for f in fs if "未追蹤" in f[3]], [("ERROR", "GT-12", NOTES)], fs)
        exclude = os.path.join(root, ".git", "info", "exclude")
        os.makedirs(os.path.dirname(exclude), exist_ok=True)
        with open(exclude, "a", encoding="utf-8") as fh:
            fh.write(f"\n{NOTES}\n")
        self.assertEqual(gates._index_consistency_leg(tmprepo.Ctx(root)), [])     # 被 ignore：無兜底
        tmprepo.git(root, "commit", "-qm", "y")
        os.remove(exclude)
        self.assertEqual(gates._index_consistency_leg(tmprepo.Ctx(root)), [])     # 暫存區＝HEAD：整腿不跑、無兜底

    def test_real_notes_face_nonempty_and_zero_hits(self):
        """真 repo：NOTES 之「## 下一步」節有條目（RL-0067 被守面有實例）且本腿零命中。"""
        from docsync.tests.test_gates import real_lint
        fs, _ = real_lint()
        self.assertEqual([f for f in fs if NOTES_LEG in f[3]], [])
        with open(os.path.join(ROOT, NOTES), encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        start = [i for i, line in enumerate(lines) if line.rstrip() == "## 下一步"]
        self.assertEqual(len(start), 1, start)
        body = []
        for line in lines[start[0] + 1:]:
            if line.startswith("## "):
                break
            body.append(line)
        self.assertTrue(any(line.startswith("- ") for line in body), body)
