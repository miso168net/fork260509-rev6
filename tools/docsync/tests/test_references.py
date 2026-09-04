"""語料面：references 的正反自證（ports 解析、STATE 空值、check 三分支、generate 冪等）。"""
import json
import os
import subprocess
import tempfile
import unittest

from docsync import references, common, book, ROOT, EVENTS, RULES, NOTES, CONSTITUTION, ADR_DIR, LESSONS_DIR
from docsync.tests.test_book_ids import stub, RULES_TEXT
from docsync.tests import test_snapshot


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


class TestMilestonesAndStateRendering(unittest.TestCase):
    def test_same_day_events_render_newest_first_and_review_summary_is_zh(self):
        ev = [{"type": "misc", "date": "2026-09-03", "summary": "第一筆", "category": "governance", "backlog_add": []},
              {"type": "misc", "date": "2026-09-03", "summary": "第二筆", "category": "governance", "backlog_add": []},
              {"type": "review", "date": "2026-09-03", "scope": "s", "report": "docs/reviews/x.md",
               "findings": {"total": 3, "fixed": 1, "to_backlog": ["BL-00009"], "wontfix_adr": ["ADR-00009"]}}]
        out = references.gen_milestones(ev)
        rows = [ln for ln in out.split("\n") if ln.startswith("| 2026")]
        self.assertIn("review", rows[0]); self.assertIn("第二筆", rows[1]); self.assertIn("第一筆", rows[2])   # 同日：後 append 者在前
        self.assertIn("findings 3（修 1／BL 1／ADR 1）；BL-00009、ADR-00009", rows[0])
        self.assertNotIn("{'total'", out)

    def test_state_recent_events_render_perf_and_review(self):
        misc = json.dumps({"type": "misc", "date": "2026-09-03", "summary": "s", "category": "governance", "backlog_add": []})
        perf = json.dumps({"type": "perf", "date": "2026-09-03", "kind": "close_bookkeeping", "wall_s": 6.5, "rc": 0, "notes": "n"})
        rev = json.dumps({"type": "review", "date": "2026-09-03", "scope": "sc", "report": "docs/reviews/x.md",
                          "findings": {"total": 0, "fixed": 0, "to_backlog": [], "wontfix_adr": []}})
        files = {RULES: RULES_TEXT, EVENTS: misc + "\n" + rev + "\n" + perf + "\n", NOTES: "<!-- wave: 1 -->\n", CONSTITUTION: "**Version**: 1.0.0 |\n", "CLAUDE.md": "a\n"}
        out = references.gen_state(stub(files))
        self.assertIn("｜perf｜close_bookkeeping｜close_bookkeeping 6.5 秒 rc=0", out)
        self.assertIn("｜review｜sc｜findings 0（修 0／BL 0／ADR 0）", out)
        self.assertIn("| 閘數 | ", out); self.assertIn("| BACKLOG 開放 | ", out)


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
        for rel, text in test_snapshot.src_files().items():   # reference-src 三檔＝reference/schema.md／accounts.md 的存在前提（缺席 fail-loud、不設 stub）
            w(rel, text)
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


class TestGeneratedIndexes(unittest.TestCase):
    """三個例外註冊／對照生成物（ADR-00005）：LESSONS 索引 next＝max＋1、ARCHITECTURE 索引、RAD-AI-MAP 兩層填實計數。"""
    LL1 = '---\nid: "LL-00001"\nrule_id: RL-0001\npromotion_surface: rules\n---\nLL-00001｜坑一\n'
    LL3 = '---\nid: "LL-00003"\nrule_id: none：理由\npromotion_surface: none\n---\nLL-00003｜坑三\n'

    def test_lessons_index_next_is_max_plus_one_and_rows_are_table(self):
        out = references.gen_lessons_index(stub({f"{LESSONS_DIR}/LL-00001-a.md": self.LL1, f"{LESSONS_DIR}/LL-00003-c.md": self.LL3}))
        self.assertTrue(out.startswith(common.GENERATED_HEADER))
        self.assertIn("<!-- next: LL-00004 -->", out)
        self.assertIn("| LL-00001 | 坑一 | RL-0001 | rules | [LL-00001-a.md](LESSONS/LL-00001-a.md) |", out)
        self.assertIn("| LL-00003 | 坑三 | none：理由 | none | [LL-00003-c.md](LESSONS/LL-00003-c.md) |", out)
        self.assertEqual(book.RE_ENTRY["LL"].findall(out), [])          # 零雙計數：索引列不合 RE_ENTRY
        self.assertIn("<!-- next: LL-00001 -->", references.gen_lessons_index(stub({})))

    def test_architecture_index_sorted_title_and_process_join(self):
        files = {"docs/arc42/03-context-and-scope.md": "---\nsection: 3\nsummary: 脈絡\nrad_ai: [E1]\n---\n# §3 脈絡與範圍\n",
                 "docs/arc42/01-introduction-and-goals.md": "---\nsection: 1\nsummary: 目標\n---\n# §1 簡介與目標\n",
                 "docs/arc42/decisions/ADR-00001-x.md": "---\nid: \"ADR-00001\"\n---\n# 不入索引\n",
                 "docs/process/P-E1-boundary.md": "---\nrad_ai: [E1]\n---\n# P-E1\n"}
        out = references.gen_architecture_index(stub(files))
        rows = [l for l in out.split("\n") if l.startswith("| §")]
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[0].startswith("| §1 | [簡介與目標](01-introduction-and-goals.md) | 目標 | — | — |"), rows[0])
        self.assertIn("| §3 | [脈絡與範圍](03-context-and-scope.md) | 脈絡 | E1 | [P-E1-boundary.md](../process/P-E1-boundary.md) |", out)

    def test_rad_ai_map_status_and_two_layer_columns(self):
        pmap = "".join(f"  {k}: 中文{i}\n" for i, k in enumerate(book.E_SUBSECTIONS["E1"]))
        files = {"docs/arc42/03-context-and-scope.md": "---\nsection: 3\nrad_ai: [E1]\nrad_ai_stage: 1\n---\n# §3\n\n目前無 AI 元件（截至 2026-09-03）。\n",
                 "docs/process/P-E1-boundary.md": f"---\nrad_ai: [E1]\nrad_ai_map:\n{pmap}---\n# P-E1\n"}
        out = references.gen_rad_ai_map(stub(files))
        self.assertIn("| E1 | [03-context-and-scope.md](../arc42/03-context-and-scope.md) | 目前無 | [P-E1-boundary.md](../process/P-E1-boundary.md) | 0/5 | 1 |", out)
        self.assertIn("| E2 | — | — | — | — | — |", out)
        self.assertIn("| ANNEX-IV | — | — | — | — | — |", out)

    def test_rad_ai_map_counts_filled_subsections_only(self):
        keys = book.E_SUBSECTIONS["E1"]
        pmap = "".join(f"  {k}: 中文{i}\n" for i, k in enumerate(keys))
        body = "# P-E1\n\n### 中文0\n\n類比張力：真句。\n\n### 中文1\n\n類比張力：TODO(波 3)\n\n### 中文2\n\n類比張力：真句。\n\n## 其他\n\nTODO(波 3)\n"
        out = references.gen_rad_ai_map(stub({"docs/process/P-E1-boundary.md": f"---\nrad_ai: [E1]\nrad_ai_map:\n{pmap}---\n{body}"}))
        self.assertIn("| E1 | — | — | [P-E1-boundary.md](../process/P-E1-boundary.md) | 2/5 | — |", out)

    def test_compute_has_generated_index_keys(self):
        for rel in ("docs/ops/LESSONS.md", "docs/arc42/ARCHITECTURE.md", "docs/generated/RAD-AI-MAP.md"):
            self.assertIn(rel, references.GENERATED_FILES)


class TestBlueprintMap(unittest.TestCase):
    """rev5 藍本對照表（ADR-00006）：frontmatter rev5_blueprint → 表；缺／重複／未知鍵／形制只排列、不拋錯；名冊 12。"""

    def test_map_lists_defects_and_never_raises(self):
        files = {"docs/arc42/01-introduction-and-goals.md": "---\nsection: 1\nrev5_blueprint:\n  §1 簡介與目標: 承襲（一句）\n---\n# §1\n",
                 "docs/arc42/06-runtime-view.md": "---\nsection: 6\nrev5_blueprint:\n  信任錨與 IP 存取閘: 隨刀：憲法 §I.7 島 F 進場刀\n  資料慣例: 亂寫\n  不存在的標題: 承襲（x）\n---\n# §6\n",
                 "docs/arc42/08-crosscutting-concepts.md": "---\nsection: 8\nrev5_blueprint:\n  §1 簡介與目標: 承襲（重複宣告）\n---\n# §8\n"}
        out = references.gen_rev5_blueprint_map(stub(files))
        l01 = references._link("docs/arc42/01-introduction-and-goals.md", references.BLUEPRINT_DIR)
        l06 = references._link("docs/arc42/06-runtime-view.md", references.BLUEPRINT_DIR)
        self.assertTrue(out.startswith(common.GENERATED_HEADER))
        self.assertIn("| §2 約束 | ## | 缺 | 缺 |", out)
        self.assertIn(f"| 信任錨與 IP 存取閘 | ### §6 | {l06} | 隨刀：憲法 §I.7 島 F 進場刀 |", out)
        self.assertIn(f"| 資料慣例 | ### §8 | {l06} | 形制：亂寫 |", out)
        self.assertIn(f"| §1 簡介與目標 | ## | {l01} | 重複：承襲（一句） |", out)
        self.assertIn(f"| 不存在的標題 | 未知鍵 | {l06} | 未知鍵 |", out)
        self.assertTrue(out.rstrip().endswith("缺：17｜重複：1｜未知鍵：1｜形制：1"), out[-120:])
        self.assertTrue(references.gen_rev5_blueprint_map(stub({})).rstrip().endswith("缺：20｜重複：0｜未知鍵：0｜形制：0"))

    def test_roster_fourteen(self):
        self.assertEqual(len(references.GENERATED_FILES), 14)
        for rel in ("docs/generated/reference/rev5-blueprint-map.md", "docs/generated/reference/agents.md"):
            self.assertIn(rel, references.GENERATED_FILES)


class TestAgentsTable(unittest.TestCase):
    """reference/agents：tracked 編排 script 的 *_OPTS 字面→表；名冊內生成物 _sk_rules.js 不入掃描面；零命中＝一列「—」。"""

    def test_agents_rows_from_opts_and_skip_generated(self):
        files = {"tools/orchestration/EXAMPLE-x.mjs": "const IMPL_OPTS = { model: 'fable[1m]', effort: 'xhigh' }\nconst REVIEW_OPTS = { model: 'opus[1m]', effort: 'high' }\n",
                 "tools/orchestration/_sk_rules.js": "const FAKE_OPTS = { model: 'x', effort: 'y' }\n"}
        out = references.gen_reference_agents(stub(files))
        self.assertTrue(out.startswith(common.GENERATED_HEADER))
        self.assertIn("| EXAMPLE-x.mjs | IMPL_OPTS | fable[1m] | xhigh |", out)
        self.assertIn("| EXAMPLE-x.mjs | REVIEW_OPTS | opus[1m] | high |", out)
        self.assertNotIn("FAKE_OPTS", out)
        self.assertIn("| — | — | — | — |", references.gen_reference_agents(stub({})))
