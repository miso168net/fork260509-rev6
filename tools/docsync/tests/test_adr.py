"""語料面：adr 的正反自證（GT-04 不可變／對稱／禁刪除／撞號／前代出處、HEAD 側讀取唯讀、DECISIONS-INDEX、superseded_by 回填）。"""
import os
import shutil
import tempfile
import unittest

from docsync import adr, common, ADR_DIR, ROOT
from docsync.tests import tmprepo
from docsync.tests.tmprepo import git as _git


def adr_text(id, status="accepted", supersedes="[]", superseded_by="[]", body="## 背景\n\n本文。\n", provenance=None):
    prov = "" if provenance is None else f"provenance: {provenance}\n"
    return (f'---\nid: "{id}"\ntitle: t {id}\ndate: 2026-09-03\nstatus: {status}\n'
            f'supersedes: {supersedes}\nsuperseded_by: {superseded_by}\n{prov}tags: [x]\n---\n\n{body}')


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
        return [f for f in adr.gt_04(tmprepo.Ctx(self.root)) if f[0] == "ERROR"]


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


PROV_LEG = "RL-0081"   # 前代出處腿訊息的共有字面（GT-04 其他腿不引此號）


class TestPredecessorProvenance(Repo):
    """RL-0081（LL-00046）：ADR-00052 起之 ADR 的 provenance 須含 `rev5:`／`rev4:` 前代出處（冒號後緊接非空白字元）
    或「前代無對應：<理由>」（冒號後緊接非空白字元），否則 ERROR 指名檔；ADR-00051 以前一律不查（已 accepted 者不回改）；不分 status。"""

    def prov_errors(self):
        return [f for f in self.errors() if PROV_LEG in f[3]]

    def test_from_52_without_predecessor_is_red_naming_file(self):
        red = {
            "ADR-00052-a.md": adr_text("ADR-00052"),                                        # 缺欄（門檻本號）
            "ADR-00053-b.md": adr_text("ADR-00053", provenance='""'),                       # 空字串
            "ADR-00054-c.md": adr_text("ADR-00054", provenance='"前代無對應："'),           # 理由空
            "ADR-00055-d.md": adr_text("ADR-00055", provenance='"前代無對應：  "'),         # 理由只有空白
            "ADR-00056-e.md": adr_text("ADR-00056", provenance='"前代出處：rev5: 空白後才有字"'),   # 冒號後非緊接
            "ADR-00057-f.md": adr_text("ADR-00057", provenance='"user 裁定；rev6 自家設計"'),   # 無前代字面
            "ADR-00058-g.md": adr_text("ADR-00058", status="proposed", provenance='"user 裁定"'),   # 不分 status
        }
        for fn, text in red.items():
            self.write(fn, text)
        fs = self.prov_errors()
        self.assertEqual(sorted(f[2] for f in fs), sorted(f"{ADR_DIR}/{fn}" for fn in red), fs)
        for f in fs:
            self.assertIn("前代無對應：<理由>", f[3])   # 附補救
            self.assertIn("provenance", f[3])

    def test_from_52_with_predecessor_or_named_reason_is_green(self):
        self.write("ADR-00052-a.md", adr_text("ADR-00052", provenance='"BL-00001；前代出處：rev5:ADR 0012"'))
        self.write("ADR-00053-b.md", adr_text("ADR-00053", provenance='"承 rev4:L-003"'))
        self.write("ADR-00054-c.md", adr_text("ADR-00054", provenance='"user 裁定；前代無對應：rev6 新設的取值口徑"'))
        self.write("ADR-00055-d.md", adr_text("ADR-00055", status="proposed", provenance='"rev5:B-160"'))
        self.assertEqual(self.prov_errors(), [])

    def test_before_52_not_checked(self):
        self.write("ADR-00001-a.md", adr_text("ADR-00001"))
        self.write("ADR-00051-b.md", adr_text("ADR-00051", provenance='"user 裁定"'))
        self.assertEqual(self.prov_errors(), [])

    def test_real_repo_face_non_empty_and_zero_hits(self):
        """真 repo：門檻起之 ADR 已有實例（受檢面非空＝RL-0067 前提）、且現行全數帶前代出處（零命中）。"""
        ctx = common.Ctx(ROOT)
        face = [a for a in adr.load_adrs(ctx).values() if isinstance(a.id, str) and int(a.id[4:]) >= adr.PREDECESSOR_FROM]
        self.assertTrue(face)
        self.assertEqual([f for f in adr.gt_04(ctx) if PROV_LEG in f[3]], [])


class TestHeadFilesReadOnly(unittest.TestCase):
    """`_files(head=True)` 以「工作樹與 HEAD 內容相同者用工作樹內容代之」省逐檔 `git show`——該判定 MUST 唯讀：
    `git diff`（工作樹側）遇 stat 髒而內容不變之檔會回寫 index 的 stat 快取（`--no-optional-locks` 擋不住），
    hook 期即改寫本次 commit 的暫存區檔（GIT_INDEX_FILE）。比對面不減：內容改動之檔（未暫存或已暫存）仍讀 HEAD 版。"""

    A, B = f"{ADR_DIR}/ADR-00001-a.md", f"{ADR_DIR}/ADR-00002-b.md"

    def repo(self):
        root = tmprepo.make_repo({self.A: adr_text("ADR-00001"), self.B: adr_text("ADR-00002")})
        self.addCleanup(shutil.rmtree, root, True)
        return root

    @staticmethod
    def index_bytes(root):
        with open(os.path.join(root, ".git", "index"), "rb") as f:
            return f.read()

    def test_stat_dirty_unchanged_file_leaves_index_bytes_intact(self):
        root = self.repo()
        p = os.path.join(root, self.A)
        t = os.stat(p).st_mtime - 1000
        os.utime(p, (t, t))                                     # stat 髒、內容不變
        # 前提：確入受檢面——plumbing diff-index 不刷新 stat 快取、只憑 stat 判，故列出該檔
        self.assertEqual(_git(root, "diff-index", "--name-only", "HEAD", "--", ADR_DIR), self.A)
        before = self.index_bytes(root)
        got = adr._files(tmprepo.Ctx(root), head=True)
        self.assertEqual(self.index_bytes(root), before, "_files(head=True) 回寫了 .git/index")
        adr.gt_04(tmprepo.Ctx(root))
        self.assertEqual(self.index_bytes(root), before, "gt_04 回寫了 .git/index")
        self.assertEqual(got, {"ADR-00001-a.md": adr_text("ADR-00001"), "ADR-00002-b.md": adr_text("ADR-00002")})

    def test_content_changed_file_still_read_from_head(self):
        """A＝未暫存改動（status 首欄為空白、排首筆）、B＝已暫存改動：兩者皆回 HEAD 版、不以工作樹代之。"""
        root = self.repo()
        tmprepo.write(root, self.A, adr_text("ADR-00001", body="## 背景\n\n工作樹改了。\n"))
        tmprepo.write(root, self.B, adr_text("ADR-00002", body="## 背景\n\n暫存了。\n"))
        _git(root, "add", self.B)
        got = adr._files(tmprepo.Ctx(root), head=True)
        self.assertEqual(got, {"ADR-00001-a.md": adr_text("ADR-00001"), "ADR-00002-b.md": adr_text("ADR-00002")})


class TestIndexAndBackfill(Repo):
    def test_gen_decisions_index(self):
        self.write("ADR-00001-a.md", adr_text("ADR-00001"))
        self.write("ADR-00002-b.md", adr_text("ADR-00002", status="proposed"))
        adrs = adr.load_adrs(tmprepo.Ctx(self.root))
        events = [{"type": "feature_close", "feature": "001-x", "adrs": ["ADR-00001"]}]
        out = adr.gen_decisions_index(adrs, events)
        self.assertTrue(out.startswith(common.GENERATED_HEADER + "\n"))
        self.assertIn("| ADR-00001 | accepted | 2026-09-03 | t ADR-00001 | 001-x | — | — |", out)
        self.assertIn("| ADR-00002 | proposed | 2026-09-03 | t ADR-00002 | — | — | — |", out)   # 000-r2 L1-04：查無出身＝中性「—」、不硬編「輕量軌」

    def test_backfill_superseded_by(self):
        self.write("ADR-00001-a.md", adr_text("ADR-00001", status="superseded"))
        self.write("ADR-00002-b.md", adr_text("ADR-00002", supersedes="[ADR-00001]"))
        self.assertTrue(any("對稱" in f[3] for f in self.errors()))
        changed = adr.backfill_superseded_by(tmprepo.Ctx(self.root))
        self.assertEqual(changed, [f"{ADR_DIR}/ADR-00001-a.md"])
        self.assertEqual(self.errors(), [])
        self.assertEqual(adr.backfill_superseded_by(tmprepo.Ctx(self.root)), [])


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
