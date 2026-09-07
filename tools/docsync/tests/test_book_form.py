"""語料面：GT-10 形制閘七腿（佔位／TODO(波 k)／類比張力／rad_ai_map 子項／Annex IV 23 鍵／mermaid⊆表／C4-L2⊇compose）。
正則字面以字串串接構造，避免規則定義文自撞。"""
import unittest

from docsync import book, NOTES
from docsync.tests.test_book_ids import stub, errs

NOTES1 = "<!-- wave: 1 -->\n# NOTES\n"
BOOK = "docs/arc42/01-introduction-and-goals.md"
COMPOSE = {"docker-compose.yml": "services:\n  postgres:\n    image: x\n  redis:\n    image: y\nvolumes:\n  pg: {}\n",
           "docker-compose.dev.yml": "services:\n  mailpit:\n    image: z\n", "docker-compose.example.yml": "services:\n  example-dev:\n    image: e\n"}
C4L2 = "docs/c4/C4-L2-container.md"


def run(files, notes=NOTES1):
    files = dict(files)
    if notes is not None:
        files.setdefault(NOTES, notes)
    files.setdefault(BOOK, "# 1\n\n目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。\n")
    return book.gt_10(stub(files))


class TestPlaceholders(unittest.TestCase):
    def test_three_legs_and_bare_bracket(self):
        star = "*" + "[待填]"
        under = "_" * 6
        box = "- " + "[ ]" + " 待辦"
        for bad in (star, under, box, "Owner: " + "[" + "Owner" + "]"):
            self.assertTrue(any("佔位" in f[3] for f in errs(run({BOOK: f"# 1\n\n{bad}\n"}))), bad)
        self.assertEqual(errs(run({BOOK: "# 1\n\n見 [連結](x.md) 與 [x] 不算。\n"})), [])
        self.assertEqual(errs(run({"docs/ops/x.md": "*[待填]\n"})), [])


class TestWaveTodo(unittest.TestCase):
    def test_todo_expiry(self):
        self.assertEqual(errs(run({BOOK: "# 1\n\nTODO(波 1) 與 TODO(波 3)\n"})), [])
        self.assertTrue(any("到期" in f[3] for f in errs(run({BOOK: "# 1\n\nTODO(波 1)\n"}, notes="<!-- wave: 2 -->\n"))))
        self.assertTrue(any("波標記缺席" in f[3] for f in errs(run({BOOK: "# 1\n"}, notes=None))))
        self.assertTrue(any("波標記缺席" in f[3] for f in errs(run({BOOK: "# 1\n"}, notes="# NOTES 無標記\n"))))


class TestProcessAndSubsections(unittest.TestCase):
    def test_process_tension_sentence(self):
        p = "docs/process/P-E1-boundary.md"
        self.assertTrue(any("類比張力" in f[3] for f in errs(run({p: "# P-E1\n\n### 清冊\n\n直接寫。\n"}))))
        self.assertEqual(errs(run({p: "# P-E1\n\n### 清冊\n\n類比張力：對得上。\n\n### 邊界\n類比張力：硬套。\n"})), [])

    def test_rad_ai_map_keys(self):
        fm = "---\nsection: 13\nrad_ai: [E8]\nrad_ai_map:\n  Monitoring: 監測\n  Retraining Policy: 再訓練政策\n  Deployment Strategy: 部署策略\n  Rollback Policy: 回滾政策\n---\n"
        f = "docs/arc42/13-operational-ai-view.md"
        fs = errs(run({f: fm + "# 13\n\n## 監測\n"}))
        self.assertTrue(any("Incident Response" in x[3] for x in fs))
        full = fm.replace("  Rollback Policy: 回滾政策\n", "  Rollback Policy: 回滾政策\n  Incident Response: 事故應變\n")
        h3 = "# 13\n\n### 監測\n\n### 再訓練政策\n\n### 部署策略\n\n### 回滾政策\n\n### 事故應變\n"
        self.assertEqual(errs(run({f: full + h3})), [])
        no_map = "---\nsection: 13\nrad_ai: [E8]\n---\n"
        self.assertEqual(errs(run({f: no_map + "# 13\n\n目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。\n"})), [])

    def test_rad_ai_map_values_must_be_h3_headings(self):
        """第八腿（波 2 grill Q4）：有 map 的檔，每個 map 值必為同檔某 ### 標題字面；兩鍵同值只需一個標題；反向不要求。"""
        p = "docs/process/P-E1-boundary.md"
        fm = "---\nrad_ai: [E1]\nrad_ai_map:\n  AI Components Inventory: 甲\n  System Boundary Diagram: 乙\n  Four-Part Boundary Contract: 乙\n  Failure Modes: 丙\n  External AI Dependencies: 丁\n---\n"
        body = "# P\n\n### 甲\n\n類比張力：x\n\n### 乙\n\n類比張力：x\n\n### 丙\n\n類比張力：x\n\n### 戊\n\n類比張力：額外標題可有。\n"
        fs = errs(run({p: fm + body}))
        self.assertTrue(any("無對應 ### 標題" in x[3] and "丁" in x[3] for x in fs), fs)
        self.assertFalse(any("乙" in x[3] or "戊" in x[3] for x in fs), fs)
        self.assertEqual(errs(run({p: fm + body + "\n### 丁\n\n類比張力：x\n"})), [])


class TestChecklist(unittest.TestCase):
    def _rows(self, keys, evidence="See `docs/arc42/01-introduction-and-goals.md`, `品質目標表` — 見該表"):
        head = "# Annex IV\n\n| AIV 鍵 | 要求 | 原列號 | 十類號 | rev6 承載 | Evidence | 自評 |\n|---|---|---|---|---|---|---|\n"
        return head + "".join(f"| **{k}** | r | — | — | x | {evidence} | ok |\n" for k in keys)

    def test_keys_and_evidence(self):
        c = "docs/compliance/annex-iv-checklist.md"
        book_ok = {BOOK: "# 1\n\n目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。\n\n### 品質目標表\n"}
        keys = list(book.AIV_KEYS)
        self.assertEqual(len(keys), 23)
        self.assertEqual(errs(run({c: self._rows(keys), **book_ok})), [])
        self.assertTrue(any("AIV-2h" in f[3] for f in errs(run({c: self._rows([k for k in keys if k != "AIV-2h"]), **book_ok}))))
        self.assertTrue(any("佔位" in f[3] for f in errs(run({c: self._rows(keys, evidence="—"), **book_ok}))))
        self.assertTrue(any("不存在" in f[3] for f in errs(run({c: self._rows(keys, evidence="See `docs/arc42/99-x.md`, `t`"), **book_ok}))))
        self.assertTrue(any("具名表" in f[3] for f in errs(run({c: self._rows(keys, evidence="See `docs/arc42/01-introduction-and-goals.md`, `不存在的表`"), **book_ok}))))
        self.assertEqual(errs(run({c: self._rows(keys, evidence="不適用：文件框架不承載、屬合規程序"), **book_ok})), [])


class TestDiagrams(unittest.TestCase):
    def test_mermaid_nodes_subset_of_table(self):
        f = "docs/arc42/03-context-and-scope.md"
        good = "# L1\n\n```mermaid\ngraph LR\n  U[使用者] --> W[web]\n```\n\n| 節點 | 說明 |\n|---|---|\n| 使用者 | 人 |\n| web | 前端 |\n"
        self.assertEqual(errs(run({f: good})), [])
        self.assertTrue(any("節點" in x[3] and "db" in x[3] for x in errs(run({f: good.replace("W[web]", "W[web] --> D[db]")}))))

    def test_c4_l2_covers_compose_services(self):
        mk = lambda nodes: "# L2\n\n```mermaid\ngraph TB\n" + "\n".join(f"  {n.replace('-', '_')}[{n}]" for n in nodes) + "\n```\n\n| 節點 | 說明 |\n|---|---|\n" + "".join(f"| {n} | s |\n" for n in nodes)
        full = ["postgres", "redis", "mailpit", "example-dev"]
        self.assertEqual(errs(run({C4L2: mk(full), **COMPOSE})), [])
        self.assertTrue(any("redis" in x[3] for x in errs(run({C4L2: mk(["postgres", "mailpit", "example-dev"]), **COMPOSE}))))
        self.assertTrue(any("C4-L2" in x[3] for x in errs(run({"docs/c4/C4-L1-system-context.md": "# L1\n", **COMPOSE}))))


class TestFaceAbsent(unittest.TestCase):
    def test_book_face_absent_is_red(self):
        """000-r2 修單：活書家族全缺原為自稱 Day-1 的 SKIP、其面今日全在＝分支已死；改 ERROR（RL-0051 掃描面空集合即紅）。"""
        fs = book.gt_10(stub({NOTES: NOTES1, "docs/ops/x.md": "x\n"}))
        self.assertTrue(any(f[0] == "ERROR" and "活書家族" in f[3] and "缺席" in f[3] and "空集合" in f[3] for f in fs), fs)
        self.assertFalse(any(f[0] == "SKIP" for f in fs))


if __name__ == "__main__":
    unittest.main()
