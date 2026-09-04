"""語料面：events 的正反自證（schema、空行、window、三指標、GT-02 SHA 實證／pin 互證、GT-03 收刀完整性）。"""
import inspect
import json
import os
import subprocess
import tempfile
import unittest

from docsync import common, events


def ev(**k):
    return json.dumps(k, ensure_ascii=False)


MISC = ev(type="misc", date="2026-09-03", summary="s", category="governance", backlog_add=[])


def _git(cwd, *args):
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", cwd, *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def make_repo():
    """外層 repo（兩顆 commit）＋兩子 repo 各一顆、以 gitlink 掛進外層 index。回 (root, sha1, sha2, {web, api})。"""
    root = tempfile.mkdtemp()
    _git(root, "init", "-q", "-b", "main")
    subs = {}
    for key, sub in (("web", "base-web"), ("api", "rust-api")):
        d = os.path.join(root, sub)
        os.makedirs(d)
        _git(d, "init", "-q", "-b", "main")
        with open(os.path.join(d, "f"), "w") as f:
            f.write("x\n")
        _git(d, "add", "f")
        _git(d, "commit", "-qm", "sub")
        subs[key] = _git(d, "rev-parse", "HEAD")
        _git(root, "update-index", "--add", "--cacheinfo", f"160000,{subs[key]},{sub}")
    with open(os.path.join(root, "a.md"), "w") as f:
        f.write("A\n")
    _git(root, "add", "a.md")
    _git(root, "commit", "-qm", "one")
    sha1 = _git(root, "rev-parse", "HEAD")
    with open(os.path.join(root, "a.md"), "a") as f:
        f.write("B\n")
    _git(root, "commit", "-qam", "two")
    sha2 = _git(root, "rev-parse", "HEAD")
    return root, sha1, sha2, subs


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


class TestSchema(unittest.TestCase):
    def test_good_misc(self):
        evs, errs = events.parse_events(MISC + "\n")
        self.assertEqual(errs, [])
        self.assertEqual(evs[0]["category"], "governance")

    def test_misc_requires_category_and_backlog_add(self):
        _, errs = events.parse_events(ev(type="misc", date="2026-09-03", summary="s") + "\n")
        self.assertTrue(any("category" in m for _, m in errs) and any("backlog_add" in m for _, m in errs))

    def test_feature_close_window_and_ids(self):
        fc = ev(type="feature_close", date="2026-09-03", feature="001-x", summary="s", merge="a" * 40,
                pins={"web": "b" * 40, "api": "c" * 40}, adrs=["ADR-00001"], arch_impact="none",
                backlog_add=["BL-00001"], backlog_done=[], window=1)
        self.assertEqual(events.parse_events(fc + "\n")[1], [])
        bad = fc.replace("BL-00001", "B-001").replace('"window": 1', '"window": 0')
        msgs = [m for _, m in events.parse_events(bad + "\n")[1]]
        self.assertTrue(any("BL-NNNNN" in m for m in msgs) and any("window" in m for m in msgs))

    def test_blank_line_and_unknown_type(self):
        _, errs = events.parse_events(MISC + "\n\n" + ev(type="zzz", date="2026-09-03") + "\n")
        self.assertTrue(any("空行" in m for _, m in errs) and any("未知 type" in m for _, m in errs))

    def test_summary_limit_and_review_conservation(self):
        long = ev(type="misc", date="2026-09-03", summary="x" * 301, category="product", backlog_add=[])
        self.assertTrue(any("300" in m for _, m in events.parse_events(long + "\n")[1]))
        rv = ev(type="review", date="2026-09-03", scope="s", report="docs/reviews/x.md",
                findings={"total": 3, "fixed": 1, "to_backlog": ["BL-00001"], "wontfix_adr": []})
        self.assertTrue(any("守恆" in m for _, m in events.parse_events(rv + "\n")[1]))


class TestMetrics(unittest.TestCase):
    def test_na_without_feature_close(self):
        m = events.metrics([json.loads(MISC)], lessons=[])
        self.assertEqual(m["gov_ratio"], "n/a")
        self.assertEqual(m["backlog_net"], "n/a")
        self.assertEqual(m["lessons_dup_rate"], "n/a")

    def test_values(self):
        fc = json.loads(ev(type="feature_close", date="2026-09-03", feature="001-x", summary="s", merge="a" * 40,
                           pins={"web": "b" * 40, "api": "c" * 40}, adrs=[], arch_impact="none",
                           backlog_add=["BL-00001", "BL-00002"], backlog_done=["BL-00001"], window=1))
        m = events.metrics([json.loads(MISC), fc], lessons=[{"recurrence_of": "RL-0001"}, {"recurrence_of": ""}], min_window=1)
        self.assertEqual(m["gov_ratio"], 1.0)
        self.assertEqual(m["backlog_net"], 1)
        self.assertEqual(m["lessons_dup_rate"], 0.5)

    def test_backlog_net_needs_min_window(self):
        fc = json.loads(ev(type="feature_close", date="2026-09-03", feature="001-x", summary="s", merge="a" * 40,
                           pins={"web": "b" * 40, "api": "c" * 40}, adrs=[], arch_impact="none",
                           backlog_add=["BL-00001"], backlog_done=[], window=1))
        self.assertEqual(events.metrics([fc], lessons=[], min_window=3)["backlog_net"], "n/a")


class TestGt02(unittest.TestCase):
    def setUp(self):
        self.root, self.sha1, self.sha2, self.subs = make_repo()

    def _fc(self, **over):
        base = dict(type="feature_close", date="2026-09-03", feature="001-x", summary="s", merge=self.sha1,
                    pins={"web": self.subs["web"], "api": self.subs["api"]}, adrs=[], arch_impact="none",
                    backlog_add=[], backlog_done=[], window=1)
        base.update(over)
        return json.dumps(base)

    def test_empty_face_is_red(self):
        c = common.Ctx(self.root)
        self.assertTrue(any(f[0] == "ERROR" and "空集合" in f[3] for f in events.gt_02(c)))

    def test_true_sha_green_fake_sha_red(self):
        write(self.root, "docs/ops/events.jsonl", MISC + "\n" + self._fc() + "\n")
        self.assertEqual([f for f in events.gt_02(common.Ctx(self.root)) if f[0] == "ERROR"], [])
        write(self.root, "docs/ops/events.jsonl", self._fc(merge="d" * 40) + "\n")
        self.assertTrue(any("merge" in f[3] and "實證" in f[3] for f in events.gt_02(common.Ctx(self.root))))
        write(self.root, "docs/ops/events.jsonl", self._fc(pins={"web": "e" * 40, "api": self.subs["api"]}) + "\n")
        self.assertTrue(any("pins.web" in f[3] for f in events.gt_02(common.Ctx(self.root))))

    def test_window_must_be_ordinal(self):
        write(self.root, "docs/ops/events.jsonl", self._fc(window=1) + "\n" + self._fc(feature="002-y", merge=self.sha2, window=3) + "\n")
        self.assertTrue(any("window" in f[3] and "2" in f[3] for f in events.gt_02(common.Ctx(self.root))))

    def test_erratum_corrects_target(self):
        bad = self._fc(merge="d" * 40)
        err = ev(type="erratum", date="2026-09-03", target_line=1, field="merge", corrected=self.sha1, reason="短 SHA 誤植")
        write(self.root, "docs/ops/events.jsonl", bad + "\n" + err + "\n")
        self.assertEqual([f for f in events.gt_02(common.Ctx(self.root)) if f[0] == "ERROR"], [])
        err2 = ev(type="erratum", date="2026-09-03", target_line=9, field="merge", corrected=self.sha1, reason="r")
        write(self.root, "docs/ops/events.jsonl", bad + "\n" + err2 + "\n")
        self.assertTrue(any("target_line" in f[3] for f in events.gt_02(common.Ctx(self.root))))

    def test_pin_drift_red(self):
        write(self.root, "docs/ops/events.jsonl", MISC + "\n")
        sub = os.path.join(self.root, "base-web")
        with open(os.path.join(sub, "f"), "a") as f:
            f.write("y\n")
        _git(sub, "commit", "-qam", "drift")
        self.assertTrue(any("pin" in f[3] and "base-web" in f[3] for f in events.gt_02(common.Ctx(self.root))))


class TestGt03(unittest.TestCase):
    def setUp(self):
        self.root, self.sha1, self.sha2, self.subs = make_repo()

    def _fc(self, **over):
        base = dict(type="feature_close", date="2026-09-03", feature="001-x", summary="s", merge=self.sha1,
                    pins={"web": self.subs["web"], "api": self.subs["api"]}, adrs=["ADR-00001"], arch_impact="none",
                    backlog_add=[], backlog_done=[], window=1)
        base.update(over)
        return json.dumps(base)

    def test_error_when_no_close_events(self):
        write(self.root, "docs/ops/events.jsonl", MISC + "\n")
        fs = events.gt_03(common.Ctx(self.root))
        self.assertTrue(any(f[0] == "ERROR" and "掃描面空集合" in f[3] for f in fs))

    def test_close_completeness(self):
        write(self.root, "docs/ops/events.jsonl", self._fc() + "\n")
        fs = events.gt_03(common.Ctx(self.root))
        self.assertTrue(any("spec.md" in f[3] for f in fs) and any("ADR-00001" in f[3] for f in fs))
        write(self.root, "specs/001-x/spec.md", "# spec\n")
        write(self.root, "docs/arc42/decisions/ADR-00001-x.md", "---\nid: \"ADR-00001\"\n---\n")
        self.assertEqual([f for f in events.gt_03(common.Ctx(self.root)) if f[0] == "ERROR"], [])

    def test_review_report_and_wontfix_adr(self):
        rv = ev(type="review", date="2026-09-03", scope="s", report="docs/reviews/20260903-s.md",
                findings={"total": 1, "fixed": 0, "to_backlog": [], "wontfix_adr": ["ADR-00002"]})
        write(self.root, "docs/ops/events.jsonl", rv + "\n")
        fs = events.gt_03(common.Ctx(self.root))
        self.assertTrue(any("report" in f[3] for f in fs) and any("ADR-00002" in f[3] for f in fs))


class TestNotesGt06Guard(unittest.TestCase):
    """notes 全文入 MILESTONES 附錄後落進 GT-06 掃描面；事件源 append-only、寫進去無乾淨補救，
    故在真源側先擋（BL-00013）。四腿正則自 book.py 取用、不另抄——本組同時釘住「不另抄」這件事。"""

    def test_four_legs_each_red(self):
        for text, needle in (("見 docs/ops/RULES.md:12", "行號形"),
                             ("見 BACKLOG.md#bl-00001", "deep-link"),
                             ("鑰在 ~/.claude/hooks/x.sh", "per-machine"),
                             ("詳見 [報告](../docs/reviews/a.md)", "相對 markdown 連結")):
            self.assertTrue(any(needle in x for x in events.notes_gt06_risks(text)), text)

    def test_safe_notes_green(self):
        for text in ("出口驗收：docsync test 134 綠、lint 0 錯；報告見 docs/reviews/20260904-spec-compliance-001.md",
                     "外連 [規格](https://example.invalid/spec) 與錨點 [節](#a) 不擋"):
            self.assertEqual(events.notes_gt06_risks(text), [], text)

    def test_wired_into_check_event(self):
        """整合面：帶危險 notes 的事件必須被 parse 擋下、不是只有 helper 會叫。"""
        e = {"type": "misc", "date": "2026-09-05", "summary": "s", "category": "governance",
             "backlog_add": [], "notes": "見 STATE.md#git"}
        self.assertTrue(any("deep-link" in x for x in events._check_event(e)))

    def test_regexes_are_not_re_copied(self):
        """判準單一家：events 用的就是 book 那四支物件本身。"""
        from docsync import book
        src = inspect.getsource(events.notes_gt06_risks)
        self.assertIn("book_mod.RE_LINENO", src)
        self.assertIn("book_mod.LINK", src)
        self.assertNotIn("re.compile", src)


class TestErrataViewAndMiscAdrs(unittest.TestCase):
    """erratum 更正視圖套用到人讀四面 ＋ misc 收單即立 ADR 的 DECISIONS-INDEX 反查（BL-00004／000-r1 R1-003／R1-008）。
    ★事件源 append-only：原列永不改，更正只活在 `events_view` 的視圖裡。"""

    MISC = ('{"type":"misc","date":"2026-09-05","summary":"s","category":"governance",'
            '"backlog_add":[],"merge":"%s"}' % ("a" * 40))
    PERF = '{"type":"perf","date":"2026-09-05","kind":"close_bookkeeping","wall_s":1.0,"commit":"%s","notes":"n"}' % ("b" * 40)

    def _view(self, *lines):
        return events.events_view("\n".join(lines) + "\n")

    def test_sha_field_corrected_in_view_only(self):
        err = ('{"type":"erratum","date":"2026-09-05","target_line":1,"field":"merge",'
               '"corrected":"%s","reason":"打錯"}' % ("c" * 40))
        view, errs = self._view(self.MISC, err)
        self.assertEqual(errs, [])
        self.assertEqual(view[0]["merge"], "c" * 40)                      # 視圖已更正
        raw, _ = events.parse_events(self.MISC + "\n" + err + "\n")
        self.assertEqual(raw[0]["merge"], "a" * 40)                       # 原值不動（append-only）

    def test_adrs_field_can_add_absent_key(self):
        """adrs 型 erratum 補的是「當時 schema 尚無此欄」的漏記，故容許目標列原無該欄。"""
        err = ('{"type":"erratum","date":"2026-09-05","target_line":1,"field":"adrs",'
               '"corrected":["ADR-00011"],"reason":"補漏記"}')
        view, errs = self._view(self.MISC, err)
        self.assertEqual(errs, [])
        self.assertEqual(view[0]["adrs"], ["ADR-00011"])

    def test_bad_target_and_bad_field_are_loud(self):
        for err, needle in ((('{"type":"erratum","date":"2026-09-05","target_line":9,"field":"merge",'
                              '"corrected":"%s","reason":"r"}' % ("c" * 40)), "不指向任何合法事件列"),
                            (('{"type":"erratum","date":"2026-09-05","target_line":1,"field":"commit",'
                              '"corrected":"%s","reason":"r"}' % ("c" * 40)), "不在 misc 事件的欄集")):
            _, errs = self._view(self.MISC, err)
            self.assertTrue(any(needle in m for _, m in errs), (needle, errs))

    def test_corrected_typing_by_field(self):
        base = '{"type":"erratum","date":"2026-09-05","target_line":1,"field":"%s","corrected":%s,"reason":"r"}'
        self.assertTrue(any("ADR-NNNNN" in x for x in events._check_event(json.loads(base % ("adrs", '"notalist"')))))
        self.assertTrue(any("40 位 hex" in x for x in events._check_event(json.loads(base % ("merge", '"short"')))))

    def test_decisions_index_reverse_lookup_from_misc(self):
        from docsync import adr as adr_mod

        class _A:
            def __init__(self):
                self.id, self.status, self.date, self.title = "ADR-00011", "accepted", "2026-09-04", "t"
                self.supersedes, self.superseded_by = [], []
        view, _ = self._view(self.MISC.replace('"backlog_add":[]', '"backlog_add":[],"adrs":["ADR-00011"]'))
        out = adr_mod.gen_decisions_index({"ADR-00011": _A()}, view)
        self.assertIn("輕量軌｜2026-09-05", out)
        self.assertNotIn("| 輕量軌 |", out)


if __name__ == "__main__":
    unittest.main()
