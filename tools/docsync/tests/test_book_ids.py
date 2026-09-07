"""語料面：GT-05 ID 家族（next／唯一／單調／不回收）、跨代裸編號（面×提及×刀集）、子庫碼面；GT-08 LESSONS 側。"""
import os
import re
import subprocess
import tempfile
import unittest

from docsync import book, common, rules, BACKLOG, CONSTITUTION, LESSONS_DIR, RULES, ROOT

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

    def test_ledgers_absent_is_red_and_submodule_absent_is_named_env_skip(self):
        """000-r2 修單：Day-1 型 SKIP（帳本缺席）退場為 ERROR——其面今日全在、分支已死；
        環境型（子庫不在工作樹）仍留 SKIP，但改 ADR-00019 具名跳過形（「⤳ 跳過：」起頭＋命中謂詞、無「Day-1」字樣）。"""
        fs = book.gt_05(stub({RULES: RULES_TEXT}))
        self.assertTrue(any(f[0] == "ERROR" and "帳本" in f[3] and "缺席" in f[3] and "空集合" in f[3] for f in fs), fs)
        self.assertFalse(any("GT-05.ledgers-absent" in f[3] for f in fs))
        skips = [f for f in fs if f[0] == "SKIP"]
        self.assertTrue(skips)
        for f in skips:
            self.assertTrue(f[3].startswith("⤳ 跳過："), f)
            self.assertIn("GT-05.submodule-absent", f[3])
            self.assertNotIn("Day-1", f[3])
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
        self.assertTrue(any(f[0] == "ERROR" and "LESSONS" in f[3] and "缺席" in f[3] and "空集合" in f[3] for f in fs), fs)
        self.assertFalse(any(f[0] == "SKIP" for f in fs))


class TestSubScanFiveForms(unittest.TestCase):
    """GT-05 子庫 pin 樹腿對齊外層五形＋共用 rev6 刀集豁免（BL-00017）。
    ★只對齊正則不共用豁免會讓自家刀名整批誤紅——實測 rust-api 六處命中全是 `001-schema-baseline`。"""

    SUB = re.compile(book.SUB_SCAN)

    def _judge(self, content, knives=frozenset()):
        """精判＝外層同一套：MENTION 剝提及形 → BARE_REV5 → rev6 刀集豁免。回報紅 token 清單。"""
        out = []
        for m in book.BARE_REV5.finditer(book.MENTION.sub("", content)):
            tok = m.group(1)
            if book.RE_KNIFE.match(tok) and (tok.startswith("000-") or tok in knives):
                continue
            out.append(tok)
        return out

    def test_prefilter_covers_five_forms(self):
        for txt in ("承 B-065 之形", "見 L-015", "承 ADR 0057 拍板", "參 Lint24 契約", "隨 004-ip-trust-anchor 進場"):
            self.assertTrue(self.SUB.search(txt), txt)
        self.assertIsNone(self.SUB.search("m0001 與 RL-0052 皆非本腿射程"))

    def test_five_forms_all_red_without_prefix(self):
        for txt, tok in (("承 B-065 之形", "B-065"), ("見 L-015", "L-015"), ("承 ADR 0057 拍板", "ADR 0057"),
                         ("參 Lint24 契約", "Lint24"), ("隨 004-ip-trust-anchor 進場", "004-ip-trust-anchor")):
            self.assertEqual(self._judge(txt), [tok], txt)

    def test_prefixed_and_mention_forms_green(self):
        for txt in ("承 rev5:B-065 之形", "承 `B-065` 之形", "承「L-015」之形", "承 rev4:ADR 0057"):
            self.assertEqual(self._judge(txt), [], txt)

    def test_rev6_knife_names_exempt_like_outer_leg(self):
        """反例：豁免拿掉即紅——正是 BL-00017 所防的「對齊正則卻不共用豁免」。"""
        line = "//! 承 001-schema-baseline 之 m0001 逐位元"
        self.assertEqual(self._judge(line, knives={"001-schema-baseline"}), [])
        self.assertEqual(self._judge(line, knives=frozenset()), ["001-schema-baseline"])
        self.assertEqual(self._judge("計畫 000-w1-governance-tooling"), [])   # 000- 創世家族恆豁免


ADR3 = 'docs/arc42/decisions/ADR-00003-x.md'
LL1 = LESSONS_DIR + '/LL-00001-x.md'


class TestIdReferenceExistence(unittest.TestCase):
    """GT-05 之「ID 引用存在性」腿（BL-00003③c2、user 停點① 拍板：補既有閘腿、不占閘數）：
    現在式面 md（排除 docs/brainstorms／docs/reviews／specs）與 tools/** 之 RL／GT／ADR／LL 引用須在真源存在。
    ★BL 方向由 GT-03 的 events-only 不變式承擔、本腿不重複。"""

    BASE = {RULES: RULES_TEXT, ADR3: '---\nid: "ADR-00003"\n---\n', LL1: "x\n"}

    def _msgs(self, rel, line, head=None):
        files = dict(self.BASE, **{rel: line + "\n"})
        return [f[2] + "｜" + f[3] for f in errs(book.gt_05(stub(files, head=head))) if "引用存在性" in f[3]]

    def test_green_existing_ids(self):
        self.assertEqual(self._msgs("docs/ops/x.md", "見 RL-0001、ADR-00003、GT-05、LL-00001"), [])

    def test_each_family_missing_is_red(self):
        for line, tok in (("見 RL-9999", "RL-9999"), ("見 ADR-09999", "ADR-09999"),
                          ("見 GT-99", "GT-99"), ("見 LL-09999", "LL-09999")):
            msgs = self._msgs("docs/ops/x.md", line)
            self.assertTrue(any(tok in m for m in msgs), (line, msgs))

    def test_tools_face_scanned_and_history_face_not(self):
        self.assertTrue(self._msgs("tools/x.py", "# 承 RL-9999"))
        self.assertEqual(self._msgs("docs/brainstorms/x.md", "見 RL-9999"), [])
        self.assertEqual(self._msgs("specs/001-x/spec.md", "見 RL-9999"), [])
        self.assertEqual(self._msgs("tools/docsync/tests/x.py", "RL-9999"), [])

    def test_next_id_header_is_not_a_reference(self):
        """配號指標（`<!-- next: RL-NNNN -->`）指向尚未配出的號、本質不是引用。"""
        self.assertEqual(self._msgs("docs/ops/x.md", "<!-- next: RL-9999 -->"), [])

    def test_no_ascii_boundary_before_or_after_is_still_scanned(self):
        """★Python 的 `\\b` 是 Unicode-aware：漢字與圈號（①②③）都算 \\w，故「承RL-9999」「③RL-9999」
        「（RL-9999⑤）」這類無空白書寫形前後一律沒有字界——舊形整批靜默略過（000-r2 修-CQ1 實測真 repo 四處）。"""
        for line in ("見③RL-9999 標", "承RL-9999 之形", "比較（RL-9999⑤）之集合",
                     "承ADR-09999", "①GT-99 補腿", "承LL-09999 之坑"):
            self.assertTrue(self._msgs("docs/ops/x.md", line), line)

    def test_id_like_neighbours_are_not_false_red(self):
        """反方向：左右接英數即非該 ID——不得因放寬字界而誤紅。"""
        for green in ("RL-9999x 不是 ID", "ARL-9999 不是 ID", "RL-99991 不是 ID", "xGT-99 不是 ID"):
            self.assertEqual(self._msgs("docs/ops/x.md", green), [], green)

    def test_filename_form_reference_is_scanned(self):
        """檔名形（`ADR-NNNNN-<slug>.md`）是真引用——尾端連字號不得把它排出射程。"""
        self.assertTrue(self._msgs("tools/x.py", "# 見 docs/arc42/decisions/ADR-09999-x.md"))

    def test_unfixable_and_vendored_faces_are_out_of_range(self):
        """不可改面處置與同批形制腿共用（見 ID_FORM_SKIP_FACE／ID_FORM_FROZEN_FACE 檔頭註解）：
        ①生成鏡像整檔不掃——其列由 append-only 事件現算、鏡像側修不了（GT-01 又要求它等於重算）；
        ②accepted ADR body 以「該行逐字在 HEAD」存量豁免——body 依 GT-04 不可變，真源退役一個號即成永久紅；
        ③vendored 第三方面（skills／spec-kit 模板）整批不掃——本 repo 不編輯、升級即整批換。
        人寫現在式面照紅。"""
        self.assertEqual(self._msgs("docs/generated/MILESTONES.md", "見 RL-9999"), [])
        self.assertEqual(self._msgs(".claude/skills/x/SKILL.md", "見 RL-9999"), [])
        self.assertEqual(self._msgs(".specify/templates/x.md", "見 RL-9999"), [])
        adr = "docs/arc42/decisions/ADR-00014-x.md"
        self.assertEqual(self._msgs(adr, "見 RL-9999", head={adr: "見 RL-9999\n"}), [])
        self.assertTrue(self._msgs(adr, "見 RL-9999"))
        self.assertTrue(self._msgs("docs/ops/x.md", "見 RL-9999"))

    def test_constitution_is_scanned_though_the_rest_of_specify_is_not(self):
        """權威鏈頂端的憲法住 `.specify/memory/`，但面分類真源 `face_of` 明列它為現在式面、優先於 `.specify/` 第三方面；
        同批的兩支形制腿走 `_text_files(ctx, "present")`＝該真源、本腿也必須同面（000-r2 修-CQ2）。
        與下一行的 `.specify/templates/` 綠案成對，釘出「第三方面不掃、但憲法照掃」這條分界。"""
        self.assertTrue(self._msgs(CONSTITUTION, "承 ADR-09999、RL-9999。"))
        self.assertEqual(self._msgs(".specify/templates/x.md", "承 ADR-09999、RL-9999。"), [])

    def test_binary_file_on_tools_face_is_skipped(self):
        """面選擇改走 `_text_files` 後，前 8KB 含 NUL 的檔一併跳過——否則 `ctx.text` 的 utf-8 open
        會讓整趟 lint 以 UnicodeDecodeError 崩（000-r2 修-CQ2 附帶項）。"""
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "tools"))
        with open(os.path.join(root, "tools", "blob.bin"), "wb") as f:
            f.write(b"RL-9999\x00\xff\xfe")
        c = stub({RULES: RULES_TEXT}, tracked=[RULES, "tools/blob.bin"])
        c.root = root
        self.assertEqual([rel for rel, _, _ in book._id_ref_face(c)], [RULES])

    def test_real_repo_zero(self):
        self.assertEqual([f for f in errs(book.gt_05(common.Ctx(ROOT))) if "引用存在性" in f[3]], [])


class TestBareKnifeNumberAndAbbrevIdForm(unittest.TestCase):
    """GT-05 兩腿（000-r2 L5-02＋C3-2）：①裸三碼前代刀號（`rev5 002` 缺冒號前綴）②縮寫 ID 形（`X-NNNNN／NNNNN`）。
    ★兩腿共用「不可改面」處置：docs/generated/** 整檔不掃（機器生成鏡像、真源＝append-only 事件的 summary／notes、鏡像側修不了）；
    docs/arc42/decisions/ 與 docs/ops/events.jsonl 以「該行逐字在 HEAD」為存量豁免（accepted body 不可變＝GT-04、事件源 append-only＝RL-0055）。"""

    BASE = {RULES: RULES_TEXT}

    def _msgs(self, rel, line, needle, head=None):
        files = dict(self.BASE, **{rel: line + "\n"})
        return [f[2] + "｜" + f[3] for f in errs(book.gt_05(stub(files, head=head))) if needle in f[3]]

    def test_bare_prev_gen_knife_number_red_and_prefixed_green(self):
        self.assertTrue(self._msgs("docs/ops/x.md", "承 rev5 002 收刀坑", "裸前代刀號"))
        self.assertTrue(self._msgs("tools/x.py", "# 承 rev4 001 之形", "裸前代刀號"))
        for green in ("承 rev5:002-system-settings 之形", "承「rev5 002」之形", "承 `rev5 002` 之形",
                      "rev6 002 刀是自家刀", "日期 2026-09-07 與版本 1.10.0", "rev5 002-system-settings"):
            self.assertEqual(self._msgs("docs/ops/x.md", green, "裸前代刀號"), [], green)

    def test_abbrev_id_form_red_and_full_form_green(self):
        for bad in ("憲法 1.2.0＝ADR-00022／00023／00024", "承 RL-0043／0044", "閘 GT-01／07",
                    "憲法＝ADR-00022／00023 三筆", "承RL-0043／0044 之形"):
            self.assertTrue(self._msgs("docs/ops/x.md", bad, "縮寫 ID 形"), bad)
        for green in ("ADR-00022／ADR-00023", "BL-00004／000-r1 R1-003", "RULES 73／92", "上限 12／12"):
            self.assertEqual(self._msgs("docs/ops/x.md", green, "縮寫 ID 形"), [], green)

    def test_unfixable_faces(self):
        gen = "docs/generated/MILESTONES.md"
        self.assertEqual(self._msgs(gen, "承 ADR-00001／00002 與 rev5 002", "縮寫 ID 形"), [])
        self.assertEqual(self._msgs(gen, "承 ADR-00001／00002 與 rev5 002", "裸前代刀號"), [])
        adr = "docs/arc42/decisions/ADR-00014-x.md"
        line = "provenance: rev5:ADR 0022（rev5 002 刀 M4）"
        self.assertEqual(self._msgs(adr, line, "裸前代刀號", head={adr: line + "\n"}), [])   # 存量凍結：該行逐字在 HEAD
        self.assertTrue(self._msgs(adr, line, "裸前代刀號"))                                   # 新寫的照擋（HEAD 無此行）


if __name__ == "__main__":
    unittest.main()
