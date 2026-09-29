"""語料面：rules 的正反自證（解析、上限、source 形、emit、RULES-VERSION、GT-08 RULES 側）。"""
import unittest

from docsync import rules, common, book, EVENTS, ROOT

GOOD = """<!-- next: RL-0003 -->
# RULES
上限（D8）：總 3｜implementer 2｜主線 2。

| id | 規則 | scope | carrier | source |
|---|---|---|---|---|
| RL-0001 | 先查紀錄。 | 主線,implementer | prompt | rev5:L-003 |
| RL-0002 | 只讀不寫。 | implementer | prompt | ADR-00003 |
"""


class TestParse(unittest.TestCase):
    def test_rows_and_caps(self):
        hdr, rows = rules.parse_rules(GOOD)
        self.assertEqual(hdr["next"], 3)
        self.assertEqual(hdr["caps"]["總"], 3)
        self.assertEqual(hdr["caps"]["implementer"], 2)
        self.assertEqual([r.id for r in rows], ["RL-0001", "RL-0002"])
        self.assertEqual(rows[0].scopes, {"主線", "implementer"})

    def test_caps_line_with_trailing_sentence(self):
        text = GOOD.replace("上限（D8）：總 3｜implementer 2｜主線 2。", "上限（D8）：總 3｜implementer 2｜主線 2。scope 可多值、逗號分隔。")
        self.assertEqual(rules.parse_rules(text)[0]["caps"], {"總": 3, "implementer": 2, "主線": 2})

    def test_emit_scope_and_version(self):
        out = rules.emit(GOOD, "implementer")
        self.assertIn("RL-0001｜先查紀錄。", out)
        self.assertIn("RL-0002｜只讀不寫。", out)
        self.assertTrue(out.rstrip().endswith("RULES-VERSION: " + rules.rules_version(GOOD)))
        self.assertNotIn("RL-0002", rules.emit(GOOD, "主線"))
        self.assertEqual(len(rules.rules_version(GOOD)), 12)

    def test_js_format(self):
        js = rules.emit_js(GOOD)
        self.assertTrue(js.startswith("// 機器生成：python3 tools/docsync generate"))
        for name in ("const RULES = `", "const RULES_REVIEW = `", "const RULES_FIX = `"):
            self.assertIn(name, js)
        self.assertEqual(js.count("RULES-VERSION: " + rules.rules_version(GOOD)), 3)


LESSON = '---\nid: "LL-00001"\nrule_id: RL-0001\npromotion_surface: rules\n---\n\nLL-00001｜坑名\n\n本文。\n'


class TestGt08RulesSide(unittest.TestCase):
    def _ctx(self, text, lessons=True):
        c = common.Ctx.__new__(common.Ctx)
        c.root = "/nonexistent"
        c.tracked = ["docs/ops/RULES.md"] + (["docs/ops/LESSONS/LL-00001-x.md"] if lessons else [])
        c._cache = {"docs/ops/RULES.md": text}
        if lessons:
            c._cache["docs/ops/LESSONS/LL-00001-x.md"] = LESSON
        c.exists = lambda rel: rel in ("docs/ops/RULES.md", "docs/arc42/decisions/ADR-00003-x.md") or (lessons and rel == "docs/ops/LESSONS")
        return c

    def test_green(self):
        self.assertEqual([f for f in rules.gt_08(self._ctx(GOOD)) if f[0] == "ERROR"], [])

    def test_lessons_dir_absent_is_red_not_skip(self):
        """000-r2 修單：GT-08.lessons-absent 這支自稱 Day-1 的 SKIP 退場為 ERROR（首條 LL 早於 2026-09-04 落地、分支已死）。"""
        fs = rules.gt_08(self._ctx(GOOD, lessons=False))
        self.assertTrue(any(f[0] == "ERROR" and "LESSONS" in f[3] and "空集合" in f[3] for f in fs), fs)
        self.assertFalse(any(f[0] == "SKIP" for f in fs))

    def test_bad_source_and_budget_counts(self):
        bad = GOOD.replace("rev5:L-003", "L-003")
        self.assertTrue(any("source 形制" in f[3] for f in rules.gt_08(self._ctx(bad))))
        counts, caps = rules.budget_counts(GOOD.replace("總 3", "總 1"))
        self.assertEqual((counts["總"], counts["implementer"], caps["總"]), (2, 2, 1))

    def test_empty_face_is_red(self):
        c = self._ctx("")
        c.exists = lambda rel: False
        self.assertTrue(any("掃描面空集合" in f[3] for f in rules.gt_08(c)))


class TestGt08KnifeNameLeg(unittest.TestCase):
    """BL-00101：規則句跨刀存活、一律不帶刀名（出處住 source 欄）；剝提及形後掃刀名形，rev6 自家刀名不豁免。
    樣式集＝repo 現存刀名書寫形之機器枚舉（book.KNIFE_NAME 檔頭註）；空轉的「≤2 行」腿同批刪除。"""

    # (規則句內寫法, 訊息應指名的刀名 token)
    RED = (("001-schema-baseline", "001-schema-baseline"), ("specs/003-auth-session/", "003-auth-session"),
           ("rev5:012-menu-perm", "rev5:012"), ("000-r2", "000-r2"), ("003 刀", "003 刀"), ("002刀", "002刀"),
           ("第五刀", "第五刀"), ("rev5:002", "rev5:002"), ("rev4:019", "rev4:019"), ("rev5 002", "rev5 002"),
           ("maint-backlog-35", "maint-backlog-35"), ("maint-orchestration-opus-all", "maint-orchestration-opus-all"),
           ("mb35", "mb35"), ("spec-compliance-004", "spec-compliance-004"),
           ("docs/reviews/20260922-spec-compliance-004.md", "spec-compliance-004"),   # 日期前綴報告路徑：左界不排除連字號
           ("006 前", "006"), ("007 落地", "007"), ("015 前", "015"), ("029 落地", "029"),   # 裸刀號值域 000～029 之 01x／02x 段與上端
           ("specs/002 史料面", "002"), ("specs/003/spec.md", "003"), ("005-final", "005"), ("specs/003-uN.py", "003"))
    GREEN = ("`001-schema-baseline`", "「001 刀 U2」", "256-bit 與 404-page", "rolling 3 刀", "本刀／各刀／跨刀／收刀",
             "ADR-00052-gate-read-face", "2026-09-29", "summary ≤300 字", "rev5:ADR 0019 與 rev5:L-011", "rev6 自家",
             "umask 077 與 HTTP 404", "0.001 與 1,000", "權限 0755", "ADR-00022/00023 與 RL-0043/0044", "010-1234",
             "030 前")   # 值域上界外（精度優先之射程界；刀號達 030 起須同批擴值域——見 TestGt08KnifeRangeExpiry）

    # rev6 自家刀集（book._rev6_knives 兩條來源各植：specs/ 目錄＋events 的 feature 欄）且涵蓋 RED 表內的自家刀名——
    # 刀集空時誤植 GT-05 式 `_rev6_knives` 豁免照樣全綠，「不豁免」判準即無牙齒。
    OWN_KNIVES = {"001-schema-baseline", "003-auth-session", "000-r2"}

    def _ctx(self, rule):
        c = TestGt08RulesSide._ctx(None, GOOD.replace("只讀不寫。", rule))
        c.tracked = c.tracked + ["specs/001-schema-baseline/spec.md"]
        c._cache[EVENTS] = '{"feature": "003-auth-session"}\n{"feature": "000-r2"}\n'
        return c

    def _fs(self, rule):
        return [f for f in rules.gt_08(self._ctx(rule)) if f[0] == "ERROR"]

    def test_knife_names_red_including_rev6_own(self):
        self.assertLessEqual(self.OWN_KNIVES, book._rev6_knives(self._ctx("x。")))   # 前提：刀集非空、含 RED 自家刀名
        for text, tok in self.RED:
            fs = self._fs(f"寫法見 {text} 之處置。")
            self.assertTrue(any(f[2].endswith("RL-0002") and f"刀名「{tok}」" in f[3] for f in fs), (text, fs))

    def test_mentions_and_lookalikes_green(self):
        for text in self.GREEN:
            self.assertEqual(self._fs(f"寫法見 {text} 之處置。"), [], text)

    def test_maint_name_containing_review_round_reported_once(self):
        """spec-compliance 分支左界不排除連字號後，維護批名內含審查輪名者仍只報一筆（maint 分支自左起整段先吃、不重疊再報）。"""
        fs = [f for f in self._fs("寫法見 maint-spec-compliance-004 之處置。") if f[2].endswith("RL-0002")]
        self.assertEqual(len(fs), 1, fs)
        self.assertIn("刀名「maint-spec-compliance-004」", fs[0][3])

    def test_knife_pattern_single_home(self):
        """刀名樣式單一家住 book.py：gt_08 取用 book 的物件本身、BARE_REV5 與 KNIFE_NAME 共用同一 slug 片段。"""
        import inspect
        src = inspect.getsource(rules.gt_08)
        self.assertIn("book.KNIFE_NAME", src)
        self.assertIn("book.MENTION", src)
        self.assertNotIn("re.compile", src)
        self.assertIn(book.KNIFE_SLUG, book.BARE_REV5.pattern)
        self.assertIn(book.KNIFE_SLUG, book.KNIFE_NAME.pattern)


def _bare_knife_coverage(knives):
    """刀集 → (刀號集, 裸形漏網刀號)：刀號之裸形 `NNN 前` 須被 KNIFE_NAME 恰認為該刀號。值域取自正則本身、不另寫死一份上界——
    擴值域後本判準自動跟上。"""
    nums = sorted({int(k[:3]) for k in knives if book.RE_KNIFE.match(k)})
    return nums, [n for n in nums if [m.group(0) for m in book.KNIFE_NAME.finditer(f"見 {n:03d} 前")] != [f"{n:03d}"]]


class TestGt08KnifeRangeExpiry(unittest.TestCase):
    """裸刀號分支值域寫死 000～029（精度優先）：刀號達 030 起，規則句裡的 `030 前` 之類裸形靜默漏網。
    到期即紅（RL-0051）：rev6 刀集（`book._rev6_knives`＝specs/ 目錄＋events 的 feature 欄）任一刀號之裸形不被認出即紅——
    第 030 刀之 specs 目錄或事件一出現即紅，逼同批擴 `book.KNIFE_NAME` 值域並補 TestGt08KnifeNameLeg 的 RED／GREEN 兩端樣本。"""

    def test_real_rev6_knives_bare_forms_all_covered(self):
        nums, uncovered = _bare_knife_coverage(book._rev6_knives(common.Ctx(ROOT)))
        self.assertTrue(nums)   # 受守面非空（RL-0067）：刀集取值失效即紅、不空轉
        self.assertEqual(uncovered, [], "rev6 刀號越出 KNIFE_NAME 裸刀號分支值域——同批擴值域並補 RED／GREEN 兩端樣本")

    def test_knife_030_in_set_is_red(self):
        """記憶體內反例：刀集含 030 即報、上界內（029）不報——判準非 vacuous；030 經 specs 目錄或事件 feature 欄任一條進刀集皆報。"""
        self.assertEqual(_bare_knife_coverage({"001-schema-baseline", "030-x"}), ([1, 30], [30]))
        self.assertEqual(_bare_knife_coverage({"001-schema-baseline", "029-x"}), ([1, 29], []))
        via_specs = TestGt08RulesSide._ctx(None, GOOD)
        via_specs.tracked = via_specs.tracked + ["specs/030-x/spec.md"]
        via_specs._cache[EVENTS] = '{"feature": "001-schema-baseline"}\n'
        via_events = TestGt08RulesSide._ctx(None, GOOD)
        via_events._cache[EVENTS] = '{"feature": "001-schema-baseline"}\n{"feature": "030-x"}\n'
        for ctx in (via_specs, via_events):
            self.assertEqual(_bare_knife_coverage(book._rev6_knives(ctx)), ([1, 30], [30]))


if __name__ == "__main__":
    unittest.main()
