"""語料面：events 的正反自證（schema、空行、window、三指標、GT-02 SHA 實證／pin 互證、GT-03 收刀完整性）。"""
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

    def test_skip_named_when_no_close_events(self):
        write(self.root, "docs/ops/events.jsonl", MISC + "\n")
        fs = events.gt_03(common.Ctx(self.root))
        self.assertTrue(any(f[0] == "SKIP" and "GT-03.no-close-events" in f[3] for f in fs))

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


if __name__ == "__main__":
    unittest.main()
