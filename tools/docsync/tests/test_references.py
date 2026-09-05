"""語料面：references 的正反自證（ports 解析、STATE 空值、check 三分支、generate 冪等）。"""
import json
import os
import subprocess
import tempfile
import unittest

from docsync import references, common, book, events as ev_mod, ROOT, EVENTS, RULES, NOTES, CONSTITUTION, ADR_DIR, LESSONS_DIR
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
        self.assertIn("| 閘數 | ", out)
        self.assertRegex(out, r"\| docsync 行數 \| \d+ \| 4000 \| [內超] \|")   # BL-00012：SC-007 目標入表、非閘
        self.assertNotIn("| BACKLOG 開放 | ", out)          # ADR-00011：觀測值不入預算對賬表
        self.assertIn("- BACKLOG 開放：", out)               # 仍在帳面統計段報現值


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
        w(references.ROUTER_SOURCE, TestRoutes.ROUTES_TEXT)   # router.rs＝reference/routes.md 的存在前提（同樣缺席 fail-loud）：合成 repo 補樁、與 TestRoutes 共用同一份語料
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


class TestMilestonesEventFieldRendering(unittest.TestCase):
    """001 刀 U5（BL-00005 四處渲染）：misc.workflow／feature_close.kind／spec_supersessions／非 perf 型 notes 附錄節，各一正一反。"""

    @staticmethod
    def _fc(date, summary, **extra):
        return {"type": "feature_close", "date": date, "feature": "001-schema-baseline", "summary": summary, "merge": "a" * 40,
                "pins": {"web": "b" * 40, "api": "c" * 40}, "adrs": [], "arch_impact": [], "backlog_add": [], "backlog_done": [], "window": 1, **extra}

    def test_misc_workflow_renders_in_target_column(self):
        ev = [{"type": "misc", "date": "2026-09-03", "summary": "無 workflow", "category": "governance", "backlog_add": []},
              {"type": "misc", "date": "2026-09-03", "summary": "有 workflow", "category": "governance", "backlog_add": [], "workflow": "000-w1-governance-tooling"}]
        out = references.gen_milestones(ev)
        self.assertIn("| misc | governance｜000-w1-governance-tooling | 有 workflow |", out)
        self.assertIn("| misc | governance | 無 workflow |", out)
        self.assertEqual(out.count("｜000-w1-governance-tooling"), 1)

    def test_feature_close_kind_renders_in_type_column(self):
        ev = [self._fc("2026-09-05", "無 kind"), self._fc("2026-09-05", "有 kind", kind="vertical")]
        out = references.gen_milestones(ev)
        self.assertIn("| 2026-09-05 | feature_close｜vertical | 001-schema-baseline | 有 kind |", out)
        self.assertIn("| 2026-09-05 | feature_close | 001-schema-baseline | 無 kind |", out)
        out3 = references.gen_milestones([self._fc("2026-09-05", "帶 notes", kind="vertical", notes="n")])
        self.assertIn("\n### 2026-09-05｜feature_close｜vertical｜001-schema-baseline\n", out3)   # 附錄標題 type 與表列同形（含 kind）

    def test_spec_supersessions_appended_to_summary(self):
        ss = [{"feature": "001-schema-baseline", "item": "FR-012", "note": "改走 ADR"}, {"feature": "002-xxx", "item": "FR-003", "note": ""}]
        out = references.gen_milestones([self._fc("2026-09-05", "收刀", spec_supersessions=ss)])
        self.assertIn("| 收刀；翻案：001-schema-baseline/FR-012（改走 ADR）、002-xxx/FR-003 |", out)
        out2 = references.gen_milestones([self._fc("2026-09-05", "空陣列", spec_supersessions=[]), self._fc("2026-09-05", "無欄")])
        self.assertNotIn("翻案", out2)
        self.assertIn("| 空陣列 |", out2); self.assertIn("| 無欄 |", out2)

    def test_notes_appendix_lists_non_perf_events_with_notes_only(self):
        ev = [{"type": "misc", "date": "2026-09-03", "summary": "s", "category": "governance", "backlog_add": [], "notes": "第一行\n第二行全文"},
              {"type": "perf", "date": "2026-09-03", "kind": "close_bookkeeping", "wall_s": 1.0, "rc": 0, "notes": "perf 備註不入"},
              {"type": "review", "date": "2026-09-03", "scope": "sc", "report": "docs/reviews/x.md",
               "findings": {"total": 0, "fixed": 0, "to_backlog": [], "wontfix_adr": []}}]
        out = references.gen_milestones(ev)
        self.assertIn("| s | — | — | — |\n\n## 備註（notes）\n\n### 2026-09-03｜misc｜governance\n\n第一行\n第二行全文\n", out)
        self.assertEqual(out.count("\n### "), 1)
        self.assertNotIn("perf 備註不入", out)
        self.assertNotIn("｜review｜", out)
        self.assertTrue(out.endswith("第二行全文\n"))

    def test_notes_appendix_absent_when_no_notes_and_ordered_newest_first(self):
        base = {"type": "misc", "category": "governance", "backlog_add": []}
        out = references.gen_milestones([{**base, "date": "2026-09-03", "summary": "a"},
                                         {**base, "date": "2026-09-03", "summary": "b"}])
        self.assertNotIn("備註", out)
        self.assertTrue(out.endswith("| b | — | — | — |\n| 2026-09-03 | misc | governance | a | — | — | — |\n"))
        out2 = references.gen_milestones([{**base, "date": "2026-09-03", "summary": "a", "notes": "A 註"},
                                          {**base, "date": "2026-09-04", "summary": "b", "notes": "B 註", "workflow": "000-w1-x"},
                                          {**base, "date": "2026-09-03", "summary": "c", "notes": "C 註"}])
        heads = [ln for ln in out2.split("\n") if ln.startswith("### ")]
        self.assertEqual(heads, ["### 2026-09-04｜misc｜governance｜000-w1-x", "### 2026-09-03｜misc｜governance", "### 2026-09-03｜misc｜governance"])
        self.assertLess(out2.index("B 註"), out2.index("C 註")); self.assertLess(out2.index("C 註"), out2.index("A 註"))   # 同日後 append 在前

    def test_real_repo_appendix_matches_events_and_workflow_target(self):
        events, errs = ev_mod.parse_events(common.Ctx(ROOT).text(EVENTS))
        self.assertEqual(errs, [])
        out = references.gen_milestones(events)
        heads = [ln for ln in out.split("\n") if ln.startswith("### ")]
        expected = [e for e in events if e.get("type") != "perf" and e.get("notes")]
        self.assertEqual(len(heads), len(expected))   # 期望自事件源現算（append-only 帳本不釘常數、收刀 append 不連動轉紅）
        self.assertGreaterEqual(len(expected), 9)     # 001 刀收單時實資料 misc 7＋review 2 為下限
        self.assertEqual(sum("｜misc｜" in h for h in heads), sum(e["type"] == "misc" for e in expected))
        self.assertEqual(sum("｜review｜" in h for h in heads), sum(e["type"] == "review" for e in expected))
        self.assertIn("| misc | governance｜000-r1-doc-governance |", out)
        self.assertIn("| misc | governance｜000-w1-governance-tooling |", out)


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
    """rev5 藍本對照表（ADR-00006）：frontmatter rev5_blueprint → 表；缺／重複／未知鍵／形制只排列、不拋錯；名冊長度由 test_roster_fourteen 釘。"""

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

    def test_roster_fifteen(self):
        self.assertEqual(len(references.GENERATED_FILES), 15)
        for rel in ("docs/generated/reference/rev5-blueprint-map.md", "docs/generated/reference/agents.md", "docs/generated/reference/routes.md"):
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


class TestRoutes(unittest.TestCase):
    """reference/routes（002 刀 U1；contracts/code-gates.md §4）：合成 ROUTES 四條→四列且序＝宣告序（正）；缺精確開頭／未知
    HttpMethod／未知 Protection／缺欄／頂層多餘行／來源缺席→各 raise（反）；真 repo 恰兩列 health／metrics。"""

    @staticmethod
    def _entry(path, method, handler, case_key, env, prot, tail="},"):
        return (f"    RouteDef {{\n        path: \"{path}\",\n        method: HttpMethod::{method},\n        handler: || {handler},\n"
                f"        case_key: \"{case_key}\",\n        envelope_exception: {env},\n        protection: Protection::{prot},\n    {tail}\n")

    ROUTES_TEXT = ("use axum::Router;\n"
                   "pub struct RouteDef {\n    pub path: &'static str,\n}\n"   # ROUTES block 外的 RouteDef 出現處：不碰
                   "pub const ROUTES: &[RouteDef] = &[\n"
                   "    // block 頂層允許 // 註解與空行\n"
                   + _entry.__func__("/zeta", "Get", "get(zeta)", "zeta", "true", "Public")
                   + _entry.__func__("/alpha", "Post", "post(alpha)", "alpha", "false", "Policy")
                   + "\n"
                   + _entry.__func__("/beta", "Delete", "delete(beta)", "beta", "false", "Authed")
                   + _entry.__func__("/gamma", "Get", "get(gamma).layer(x)", "gamma", "false", "Policy", tail="}")
                   + "];\n"
                   "pub const ROUTES_COUNT: usize = 4;\n")

    def _gen(self, text):
        return references.gen_reference_routes(stub({references.ROUTER_SOURCE: text}))

    def test_synthetic_four_rows_in_declaration_order(self):
        rows = references.parse_router_routes(self.ROUTES_TEXT, references.ROUTER_SOURCE)
        self.assertEqual(rows, [("/zeta", "GET", "Public", "zeta", True), ("/alpha", "POST", "Policy", "alpha", False),
                                ("/beta", "DELETE", "Authed", "beta", False), ("/gamma", "GET", "Policy", "gamma", False)])
        out = self._gen(self.ROUTES_TEXT)
        self.assertTrue(out.startswith(common.GENERATED_HEADER))
        self.assertIn("來源＝rust-api/server/src/router.rs 的 ROUTES const（generate 重算；handler 閉包不入表）", out)
        table = [ln for ln in out.split("\n") if ln.startswith("| /")]
        self.assertEqual(table, ["| /zeta | GET | Public | zeta | 是 |", "| /alpha | POST | Policy | alpha | 否 |",
                                 "| /beta | DELETE | Authed | beta | 否 |", "| /gamma | GET | Policy | gamma | 否 |"])   # 宣告序、非 path 排序
        self.assertNotIn("get(zeta)", out)   # handler 閉包不入表

    def test_missing_exact_opener_raises(self):
        bent = self.ROUTES_TEXT.replace("pub const ROUTES: &[RouteDef] = &[\n", "pub const ROUTES: &[RouteDef] = &[ // 尾註\n")
        with self.assertRaisesRegex(references.RouterRoutesError, "找不到"):
            references.parse_router_routes(bent, "x.rs")

    def test_unknown_method_variant_raises(self):
        with self.assertRaisesRegex(references.RouterRoutesError, "HttpMethod::Put"):
            references.parse_router_routes(self.ROUTES_TEXT.replace("HttpMethod::Post", "HttpMethod::Put"), "x.rs")

    def test_unknown_protection_variant_raises(self):
        with self.assertRaisesRegex(references.RouterRoutesError, "Protection::Admin"):
            references.parse_router_routes(self.ROUTES_TEXT.replace("Protection::Authed", "Protection::Admin"), "x.rs")

    def test_missing_field_raises(self):
        with self.assertRaisesRegex(references.RouterRoutesError, "缺欄.*case_key"):
            references.parse_router_routes(self.ROUTES_TEXT.replace('        case_key: "zeta",\n', ""), "x.rs")

    def test_top_level_stray_line_raises(self):
        bent = self.ROUTES_TEXT.replace("    // block 頂層允許 // 註解與空行\n", "    let stray = 1;\n")
        with self.assertRaisesRegex(references.RouterRoutesError, "頂層不認得的行"):
            references.parse_router_routes(bent, "x.rs")
        unclosed = self.ROUTES_TEXT[:self.ROUTES_TEXT.index("];\n")]   # 檔案在收尾前截斷（半解析）
        with self.assertRaisesRegex(references.RouterRoutesError, "未見收尾"):
            references.parse_router_routes(unclosed, "x.rs")

    def test_source_absent_raises(self):
        with self.assertRaisesRegex(references.RouterRoutesError, "router.rs"):
            references.gen_reference_routes(stub({}))

    # 回填點＝002 刀 T029（U3）／T033（U4）：ROUTES 掛上業務兩條（getSystemSettings／updateSystemSetting）時，本測之真 repo
    # 釘值須同批增列。★釘值形刻意保留——「真表首算＝恰兩列」是 002 刀 U1 的驗收面，不以「非空＋包含」弱化。
    # ★本檔已納 U3／U4 允許檔面（research R12 表；限定＝只准增列本測釘值）；回填條＝tasks T029／T033。
    # ★紅而不自明的窗口：pre-commit 只在 staged 含 tools/docsync/ 時才跑 selftest-docsync（.githooks/pre-commit 同段），
    #   而 GT-01 漂移在 U3 跑過 generate 後即消——故本測不同批改＝一路綠燈到有人跑 docsync test／bootstrap 才浮出。
    def test_real_repo_two_rows_health_metrics(self):
        ctx = common.Ctx(ROOT)
        rows = references.parse_router_routes(ctx.text(references.ROUTER_SOURCE), references.ROUTER_SOURCE)
        self.assertEqual(rows, [("/health", "GET", "Public", "health", True), ("/metrics", "GET", "Public", "metrics", True)])
        out = references.gen_reference_routes(ctx)
        self.assertEqual([ln for ln in out.split("\n") if ln.startswith("| /")],
                         ["| /health | GET | Public | health | 是 |", "| /metrics | GET | Public | metrics | 是 |"])
        self.assertIn("docs/generated/reference/routes.md", references.compute_generated(ctx))
