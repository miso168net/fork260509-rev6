"""語料面：adr 的正反自證（GT-04 不可變／對稱／禁刪除／撞號、DECISIONS-INDEX、superseded_by 回填）。"""
import os
import subprocess
import tempfile
import unittest

from docsync import adr, common, ADR_DIR


def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", cwd, *args],
                          check=True, capture_output=True, text=True).stdout.strip()


def adr_text(id, status="accepted", supersedes="[]", superseded_by="[]", body="## 背景\n\n本文。\n"):
    return (f'---\nid: "{id}"\ntitle: t {id}\ndate: 2026-09-03\nstatus: {status}\n'
            f'supersedes: {supersedes}\nsuperseded_by: {superseded_by}\ntags: [x]\n---\n\n{body}')


class Repo(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        _git(self.root, "init", "-q", "-b", "main")
        os.makedirs(os.path.join(self.root, ADR_DIR))

    def write(self, fn, text):
        with open(os.path.join(self.root, ADR_DIR, fn), "w", encoding="utf-8") as f:
            f.write(text)

    def commit(self):
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "c")

    def errors(self):
        return [f for f in adr.gt_04(common.Ctx(self.root)) if f[0] == "ERROR"]


class TestGt04(Repo):
    def test_empty_face_is_red(self):
        self.assertTrue(any("空集合" in f[3] for f in self.errors()))

    def test_accepted_body_immutable_then_supersede_ok(self):
        self.write("ADR-00001-a.md", adr_text("ADR-00001"))
        self.commit()
        self.assertEqual(self.errors(), [])
        self.write("ADR-00001-a.md", adr_text("ADR-00001", body="## 背景\n\n改了。\n"))
        self.assertTrue(any("body 不可變" in f[3] for f in self.errors()))
        self.write("ADR-00001-a.md", adr_text("ADR-00001", status="superseded", superseded_by="[ADR-00002]"))
        self.write("ADR-00002-b.md", adr_text("ADR-00002", supersedes="[ADR-00001]"))
        self.assertEqual(self.errors(), [])
        self.write("ADR-00001-a.md", adr_text("ADR-00001", status="proposed", superseded_by="[ADR-00002]"))
        self.assertTrue(any("僅可轉 superseded" in f[3] for f in self.errors()))

    def test_delete_forbidden(self):
        self.write("ADR-00001-a.md", adr_text("ADR-00001"))
        self.commit()
        os.remove(os.path.join(self.root, ADR_DIR, "ADR-00001-a.md"))
        self.assertTrue(any("禁刪除" in f[3] for f in self.errors()))

    def test_supersede_symmetry_and_status(self):
        self.write("ADR-00001-a.md", adr_text("ADR-00001"))
        self.write("ADR-00002-b.md", adr_text("ADR-00002", supersedes="[ADR-00001]"))
        msgs = [f[3] for f in self.errors()]
        self.assertTrue(any("對稱" in m for m in msgs) and any("須為 superseded" in m for m in msgs))
        self.write("ADR-00003-c.md", adr_text("ADR-00003", supersedes="[ADR-00009]"))
        self.assertTrue(any("不存在" in m for m in [f[3] for f in self.errors()]))

    def test_filename_id_and_duplicates(self):
        self.write("ADR-00003-c.md", adr_text("ADR-00004"))
        self.assertTrue(any("檔名" in f[3] for f in self.errors()))
        self.write("ADR-00004-d.md", adr_text("ADR-00004"))
        self.assertTrue(any("重複配號" in f[3] for f in self.errors()))
        self.write("bad.md", adr_text("ADR-00005"))
        self.assertTrue(any("ADR-NNNNN-<slug>.md" in f[3] for f in self.errors()))


class TestIndexAndBackfill(Repo):
    def test_gen_decisions_index(self):
        self.write("ADR-00001-a.md", adr_text("ADR-00001"))
        self.write("ADR-00002-b.md", adr_text("ADR-00002", status="proposed"))
        adrs = adr.load_adrs(common.Ctx(self.root))
        events = [{"type": "feature_close", "feature": "001-x", "adrs": ["ADR-00001"]}]
        out = adr.gen_decisions_index(adrs, events)
        self.assertTrue(out.startswith(common.GENERATED_HEADER + "\n"))
        self.assertIn("| ADR-00001 | accepted | 2026-09-03 | t ADR-00001 | 001-x | — | — |", out)
        self.assertIn("| ADR-00002 | proposed | 2026-09-03 | t ADR-00002 | — | — | — |", out)   # 000-r2 L1-04：查無出身＝中性「—」、不硬編「輕量軌」

    def test_backfill_superseded_by(self):
        self.write("ADR-00001-a.md", adr_text("ADR-00001", status="superseded"))
        self.write("ADR-00002-b.md", adr_text("ADR-00002", supersedes="[ADR-00001]"))
        self.assertTrue(any("對稱" in f[3] for f in self.errors()))
        changed = adr.backfill_superseded_by(common.Ctx(self.root))
        self.assertEqual(changed, [f"{ADR_DIR}/ADR-00001-a.md"])
        self.assertEqual(self.errors(), [])
        self.assertEqual(adr.backfill_superseded_by(common.Ctx(self.root)), [])


class TestDecisionsIndexProvenance(unittest.TestCase):
    """000-r2 L1-03／L1-04：①review 事件之 findings.wontfix_adr 亦是 ADR 出身（won't-fix 立 ADR＝RL-0073），
    舊版三輪反查缺這一輪、ADR-00008 查無來源 ②查無時硬編「輕量軌」＝生成面憑空斷言，改中性「—」。"""

    class _A:
        def __init__(self, aid):
            self.id, self.status, self.date, self.title = aid, "accepted", "2026-09-03", "t"
            self.supersedes, self.superseded_by = [], []

    def _index(self, events, ids=("ADR-00001",)):
        return adr.gen_decisions_index({i: self._A(i) for i in ids}, events)

    def test_wontfix_adr_from_review_prints_independent_round(self):
        out = self._index([{"type": "review", "date": "2026-09-04", "scope": "doc-governance",
                            "findings": {"total": 1, "fixed": 0, "to_backlog": [], "wontfix_adr": ["ADR-00001"]}}])
        self.assertIn("| 獨立輪｜doc-governance |", out)

    def test_feature_close_wins_over_review_and_misc(self):
        evs = [{"type": "feature_close", "feature": "001-x", "adrs": ["ADR-00001"]},
               {"type": "misc", "date": "2026-09-04", "adrs": ["ADR-00001"], "workflow": "maint-x"},
               {"type": "review", "date": "2026-09-04", "scope": "s",
                "findings": {"total": 1, "fixed": 0, "to_backlog": [], "wontfix_adr": ["ADR-00001"]}}]
        self.assertIn("| 001-x |", self._index(evs))

    def test_unknown_provenance_is_neutral_dash(self):
        out = self._index([])
        self.assertIn("| — | — | — |", out)
        self.assertNotIn("輕量軌", out)

    def test_real_repo_wontfix_adr_gets_round_and_no_bare_lightweight(self):
        from docsync import ROOT, EVENTS, events as ev_mod
        ctx = common.Ctx(ROOT)
        view, _ = ev_mod.events_view(ctx.text(EVENTS))
        out = adr.gen_decisions_index(adr.load_adrs(ctx), view)
        self.assertIn("| ADR-00008 | ", out)
        self.assertTrue(any(ln.startswith("| ADR-00008 |") and "獨立輪｜doc-governance" in ln for ln in out.split("\n")), out)
        self.assertEqual([ln for ln in out.split("\n") if "| 輕量軌 |" in ln], [])   # 裸「輕量軌」歸零


if __name__ == "__main__":
    unittest.main()
