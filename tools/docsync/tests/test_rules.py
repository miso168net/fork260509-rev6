"""語料面：rules 的正反自證（解析、上限、source 形、emit、RULES-VERSION、GT-08 RULES 側）。"""
import unittest

from docsync import rules, common

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


class TestGt08RulesSide(unittest.TestCase):
    def _ctx(self, text):
        c = common.Ctx.__new__(common.Ctx)
        c.root = "/nonexistent"
        c.tracked = ["docs/ops/RULES.md"]
        c._cache = {"docs/ops/RULES.md": text}
        c.exists = lambda rel: rel in ("docs/ops/RULES.md", "docs/arc42/decisions/ADR-00003-x.md")
        return c

    def test_green(self):
        self.assertEqual([f for f in rules.gt_08(self._ctx(GOOD)) if f[0] == "ERROR"], [])

    def test_bad_source_and_budget_counts(self):
        bad = GOOD.replace("rev5:L-003", "L-003")
        self.assertTrue(any("source 形制" in f[3] for f in rules.gt_08(self._ctx(bad))))
        counts, caps = rules.budget_counts(GOOD.replace("總 3", "總 1"))
        self.assertEqual((counts["總"], counts["implementer"], caps["總"]), (2, 2, 1))

    def test_empty_face_is_red(self):
        c = self._ctx("")
        c.exists = lambda rel: False
        self.assertTrue(any("掃描面空集合" in f[3] for f in rules.gt_08(c)))


if __name__ == "__main__":
    unittest.main()
