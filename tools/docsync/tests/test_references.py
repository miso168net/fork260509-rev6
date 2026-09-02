"""語料面：references 的正反自證（ports 解析、STATE 空值、check 三分支、generate 冪等）。"""
import json
import os
import subprocess
import tempfile
import unittest

from docsync import references, common, ROOT, EVENTS, RULES, NOTES, CONSTITUTION, ADR_DIR
from docsync.tests.test_book_ids import stub, RULES_TEXT


class TestPorts(unittest.TestCase):
    def test_real_repo_twelve_rows_all_3xxxx(self):
        rows = references.parse_ports(common.Ctx(ROOT))
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(str(r["host"]).startswith("3") for r in rows))
        self.assertIn({"service": "front-nginx", "host": 32080, "container": 80, "file": "docker-compose.dev.yml"}, rows)

    def test_synthetic_old_generation_flagged(self):
        files = {"docker-compose.yml": 'services:\n  web:\n    ports:\n      - "127.0.0.1:22080:80"\n      - "32081:81"\n  db:\n    image: x\n'}
        rows = references.parse_ports(stub(files))
        self.assertEqual([(r["service"], r["host"]) for r in rows], [("web", 22080), ("web", 32081)])
        out = references.gen_reference_ports(stub(files))
        self.assertIn("★非本代世代", out)
        self.assertIn("| web | 22080 | 80 | docker-compose.yml |", out)


class TestStateAndCheck(unittest.TestCase):
    def test_state_na_and_unbuilt(self):
        misc = json.dumps({"type": "misc", "date": "2026-09-03", "summary": "s", "category": "governance", "backlog_add": []})
        files = {RULES: RULES_TEXT, EVENTS: misc + "\n", NOTES: "<!-- wave: 1 -->\n", CONSTITUTION: "x\n\n**Version**: 1.0.0 | **Ratified**: 2026-09-03\n",
                 "CLAUDE.md": "a\nb\n", "docs/arc42/decisions/ADR-00003-x.md": '---\nid: "ADR-00003"\ntitle: t\ndate: 2026-09-03\nstatus: accepted\n---\n'}
        out = references.gen_state(stub(files))
        for label in ("治理批對 feature 比", "LESSONS 重複率", "BACKLOG 淨流量"):
            self.assertTrue(any(label in ln and "n/a" in ln for ln in out.split("\n")), label)
        self.assertIn("未建", out)
        self.assertIn("版本：1.0.0", out)
        self.assertIn("波：1", out)
        self.assertIn("CLAUDE.md 行數：2", out)

    def test_check_three_branches(self):
        computed = {"docs/generated/STATE.md": "S\n"}
        self.assertTrue(any("缺" in f[3] for f in references.check_generated(stub({}), computed)))
        self.assertTrue(any("漂移" in f[3] for f in references.check_generated(stub({"docs/generated/STATE.md": "T\n"}), computed)))
        self.assertTrue(any("名冊外" in f[3] for f in references.check_generated(stub({"docs/generated/STATE.md": "S\n", "docs/generated/extra.md": "e\n"}), computed)))
        self.assertEqual(references.check_generated(stub({"docs/generated/STATE.md": "S\n"}), computed), [])


class TestGenerateIdempotent(unittest.TestCase):
    def test_generate_twice_same_bytes_and_check_green(self):
        root = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
        def w(rel, text):
            p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f: f.write(text)
        w(RULES, RULES_TEXT)
        w(EVENTS, json.dumps({"type": "misc", "date": "2026-09-03", "summary": "創世", "category": "governance", "backlog_add": []}) + "\n"
          + json.dumps({"type": "perf", "date": "2026-09-03", "kind": "close_bookkeeping", "wall_s": 1.5, "notes": "n\n多行"}) + "\n")
        w(NOTES, "<!-- wave: 1 -->\n")
        w(CONSTITUTION, "**Version**: 1.0.0 |\n")
        w("CLAUDE.md", "x\n")
        w("docker-compose.yml", 'services:\n  web:\n    ports:\n      - "127.0.0.1:32080:80"\n')
        w(f"{ADR_DIR}/ADR-00001-a.md", '---\nid: "ADR-00001"\ntitle: t\ndate: 2026-09-03\nstatus: superseded\nsupersedes: []\nsuperseded_by: []\n---\nb\n')
        w(f"{ADR_DIR}/ADR-00002-b.md", '---\nid: "ADR-00002"\ntitle: t2\ndate: 2026-09-03\nstatus: accepted\nsupersedes: [ADR-00001]\nsuperseded_by: []\n---\nb\n')
        subprocess.run(["git", "-C", root, "add", "-A"], check=True)
        written = references.cmd_generate(common.Ctx(root))
        self.assertIn(f"{ADR_DIR}/ADR-00001-a.md", written)  # 對稱回填
        first = {rel: open(os.path.join(root, rel), encoding="utf-8").read() for rel in references.compute_generated(common.Ctx(root))}
        subprocess.run(["git", "-C", root, "add", "-A"], check=True)
        references.cmd_generate(common.Ctx(root))
        second = {rel: open(os.path.join(root, rel), encoding="utf-8").read() for rel in first}
        self.assertEqual(first, second)
        ctx = common.Ctx(root)
        self.assertEqual(references.check_generated(ctx, references.compute_generated(ctx)), [])
        self.assertTrue(all(t.startswith(common.GENERATED_HEADER) or t.startswith("// 機器生成") for t in first.values()))


if __name__ == "__main__":
    unittest.main()
