"""守 RL-0049／RL-0052：generated 只由真源重算、零漂移（GT-01 本體）；數量預算對賬入 STATE。

references.py：parse_ports／gen_reference_ports（compose 三檔）、gen_reference_perf、gen_milestones、gen_state（git／波／憲法／帳面／四指標／預算／尾 3 事件）、
gen_lessons_index（例外註冊；next＝檔集最大號＋1、ADR-00005）、gen_architecture_index（例外註冊；arc42 節檔 frontmatter）、gen_rad_ai_map（兩層填實計數）、
gen_rev5_blueprint_map（rev5 藍本對照表；frontmatter rev5_blueprint 對 20 列名冊、缺列可見不斷言、ADR-00006）、gen_reference_agents（編排 script 的 *_OPTS 名冊）、
parse_router_routes／gen_reference_routes（rust-api/server/src/router.rs 之 ROUTES const 全量表；窄假設行級解析、偏離即 raise、列序＝宣告序；002 刀 U1）、
compute_generated（名冊→內容；reference/schema.md／accounts.md 兩鍵委給 snapshot.gen_reference_*；名冊 ⇔ 計算面對賬、缺鍵即 raise）、
check_generated（缺／漂移／名冊外／*_OPTS 掃描面空集合警示）、cmd_generate（先回填 ADR 對稱、冪等寫檔）。
"""
import os
import re

from . import (EVENTS, RULES, BACKLOG, BACKLOG_DEFERRED, LESSONS_DIR, GENERATED_DIR, CONSTITUTION, DEFAULT_BRANCH,
               SUBMODULES, COMPOSE_FILES, NOTES)
from .common import ERROR, WARN, GENERATED_HEADER, GitError, finding, parse_front_matter
from . import events as ev_mod
from . import adr as adr_mod
from . import rules as rules_mod
from . import book as book_mod
from . import snapshot as snapshot_mod

GENERATED_FILES = (
    "docs/generated/STATE.md", "docs/generated/MILESTONES.md", "docs/generated/DECISIONS-INDEX.md", "docs/generated/GATES.md",
    "docs/generated/RAD-AI-MAP.md", "docs/generated/reference/ports.md", "docs/generated/reference/perf.md", "tools/orchestration/_sk_rules.js",
    "docs/arc42/ARCHITECTURE.md", "docs/ops/LESSONS.md",  # 例外註冊兩件（啟動書 §3.1；ADR-00005）
    "docs/generated/reference/rev5-blueprint-map.md", "docs/generated/reference/agents.md",  # 波 3（ADR-00006；啟動書 §3.2 P-E2）
    "docs/generated/reference/schema.md", "docs/generated/reference/accounts.md",  # 001-schema-baseline（ADR-00010；真源＝reference-src 快照＋archetype-map）
    "docs/generated/reference/routes.md",  # 002 刀 U1（`docs/ops/reference-src/code-gate-contracts.md` §6；真源＝rust-api/server/src/router.rs ROUTES const、無 Day-1 豁免）
)
RE_CHAPTER = re.compile(r"^docs/arc42/(\d{2})-[a-z0-9-]+\.md$")
RE_H1 = re.compile(r"^#\s+(?:§\s*\d+\s+)?(.+?)\s*$", re.M)
RE_ANY_HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$")
RAD_AI_ITEMS = tuple(f"E{i}" for i in range(1, 9)) + ("C4-E1", "C4-E2", "C4-E3", "ANNEX-IV")
RE_PORT = re.compile(r'^\s+-\s+"?(?:(\d{1,3}(?:\.\d{1,3}){3}):)?(\d+):(\d+)(?:/(?:tcp|udp))?"?\s*$')
RE_VERSION = re.compile(r"\*\*Version\*\*:\s*([0-9.]+)")
PORT_GENERATION_PREFIX = "3"
REV5_BLUEPRINT = (  # rev5 活書標題名冊（凍結 SHA 7eab28a；欄＝字面｜層｜所屬 §N）；字面對 rev5 檔的一次性核對見 ADR-00006 證據段
    ("§1 簡介與目標", "##", 1), ("§2 約束", "##", 2), ("§3 系統脈絡", "##", 3), ("§4 解法策略", "##", 4),
    ("§5 Building blocks", "##", 5), ("§6 Runtime", "##", 6),
    ("信任錨與 IP 存取閘", "###", 6), ("會話狀態機（sys_token）", "###", 6),
    ("登入失敗節流三區（帳號維＋來源維）", "###", 6), ("使用者域斷權與密碼三入口（007 落地）", "###", 6),
    ("§7 部署", "##", 7), ("§8 橫切概念", "##", 8),
    ("fork-delta 接線現況（base-web）", "###", 8), ("資料慣例", "###", 8), ("API 慣例", "###", 8), ("授權慣例", "###", 8),
    ("§9 架構決策", "##", 9), ("§10 品質要求", "##", 10), ("§11 風險與技術債", "##", 11), ("§12 名詞表", "##", 12),
)
BLUEPRINT_DISPOSITIONS = ("承襲", "隨刀：", "不承襲：")
BLUEPRINT_DIR = "docs/generated/reference"
RE_OPTS = re.compile(r"^const ([A-Z][A-Z0-9_]*_OPTS)\s*=\s*\{\s*model:\s*'([^']*)'\s*,\s*effort:\s*'([^']*)'\s*\}", re.M)


def parse_ports(ctx):
    """回 [{service, host, container, ip, file}]（依 compose 三檔出現序）。"""
    rows = []
    for rel in COMPOSE_FILES:
        text = ctx.text(rel)
        if text is None:
            continue
        in_services, svc, in_ports = False, None, False
        for line in text.split("\n"):
            if line.startswith("services:"):
                in_services = True
                continue
            if in_services and line and not line.startswith(" "):
                in_services = False
            if not in_services:
                continue
            m = re.match(r"^  ([A-Za-z0-9_.-]+):\s*$", line)
            if m:
                svc, in_ports = m.group(1), False
                continue
            if re.match(r"^    ports:\s*$", line):
                in_ports = True
                continue
            if in_ports:
                pm = RE_PORT.match(line)
                if pm:
                    rows.append({"service": svc, "host": int(pm.group(2)), "container": int(pm.group(3)), "file": rel, **({"ip": pm.group(1)} if pm.group(1) else {})})
                elif line.strip() and not line.startswith("      "):
                    in_ports = False
    return [{k: v for k, v in r.items() if k != "ip"} for r in rows]


def gen_reference_ports(ctx):
    rows = parse_ports(ctx)
    lines = [GENERATED_HEADER, "# reference/ports — host 埠正典表", "",
             "來源＝docker-compose.yml＋docker-compose.dev.yml＋docker-compose.example.yml 的 ports: 段（generate 重算；配號紀律＝ADR-00001、世代 3xxxx）。", "",
             "| 服務 | host | 容器內側 | 檔 |", "|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["service"], r["host"])):
        lines.append(f"| {r['service']} | {r['host']} | {r['container']} | {r['file']} |")
    foreign = [r for r in rows if not str(r["host"]).startswith(PORT_GENERATION_PREFIX)]
    if foreign:
        lines += ["", "★非本代世代（首碼非 3；由 tools/bootstrap.sh 斷言擋、本表只列）：" + "、".join(f"{r['service']}={r['host']}" for r in foreign)]
    return "\n".join(lines) + "\n"


def _cell(v):
    """表格 cell 逸脫（000-r2 L1-02）：半形直槓會把列撐成多欄，殘留換行同理——兩者一律處理。
    ★只服務表列；附錄節（notes 全文）維持原樣不轉義＝BL-00005 拍板（保留換行、不截斷、不轉義）。"""
    return str(v).replace("|", "\\|").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")


def _merge_cell(e):
    """merge 欄（000-r2 L1-01）：只在該列真有 SHA 時渲染——feature_close／misc 的 merge、
    或 erratum 且欄別 ∈ ERRATUM_SHA_FIELDS 之 corrected；其餘（adrs／probe 型 erratum）印「—」，
    否則會把 Python 字面（`['ADR-0`、`{'quest`）切成七字印進表。"""
    if e.get("type") in ("feature_close", "misc") and e.get("merge"):
        return str(e["merge"])[:7]
    if e.get("type") == "erratum" and e.get("field") in ev_mod.ERRATUM_SHA_FIELDS and e.get("corrected"):
        return str(e["corrected"])[:7]
    return "—"


def gen_reference_perf(events):
    lines = [GENERATED_HEADER, "# reference/perf — 收刀簿記與 pre-commit 效能資料點", "",
             "來源＝docs/ops/events.jsonl 的 perf 事件（generate 重算；kind＝close_bookkeeping／precommit_chain、量測法＝RUNBOOK §12b）。", "",
             "| date | kind | wall_s | rc | commit | notes |", "|---|---|---|---|---|---|"]
    # BL-00103：依 date 穩定排序（同日保檔內序）——遲到的 close_bookkeeping 事件人讀面仍按時序，事件帳本身維持 append-only。
    for e in sorted((e for e in events if e.get("type") == "perf"), key=lambda e: e["date"]):
        notes = (e.get("notes") or "").split("\n", 1)[0]
        lines.append("| " + " | ".join(_cell(x) for x in (e["date"], e["kind"], e["wall_s"], e.get("rc", "—"),
                                                          str(e.get("commit", "—"))[:7], notes)) + " |")
    return "\n".join(lines) + "\n"


def _type_cell(e):
    """type 欄：feature_close 帶 kind 者組字「feature_close｜<kind>」（BL-00005）；表列與附錄標題共用、不改 e["type"]。"""
    return f"{e['type']}｜{e['kind']}" if e.get("type") == "feature_close" and e.get("kind") else e["type"]


def _target(e):
    """標的欄：feature／scope／category／kind／erratum 行號；misc 帶 workflow 者附「｜<workflow>」（BL-00005）。"""
    if e.get("type") == "misc" and e.get("category") and e.get("workflow"):
        return f"{e['category']}｜{e['workflow']}"
    return e.get("feature") or e.get("scope") or e.get("category") or e.get("kind") or (f"行 {e['target_line']}" if e.get("type") == "erratum" else "—")


def _event_summary(e):
    """人讀摘要：summary／reason 直出（feature_close 帶非空 spec_supersessions 者尾附「；翻案：<feature>/<item>（note）」、多筆頓號連接；BL-00005）；
    review 型渲染 findings 三分流 zh-TW 摘要（不印 dict 字面）；perf 型渲染 kind／wall_s／rc。"""
    if e.get("summary") or e.get("reason"):
        s = e.get("summary") or e.get("reason")
        ss = e.get("spec_supersessions") if e.get("type") == "feature_close" else None
        if isinstance(ss, list) and ss:
            s += "；翻案：" + "、".join(f"{x.get('feature')}/{x.get('item')}" + (f"（{x['note']}）" if x.get("note") else "") for x in ss)
        return s
    if e.get("type") == "review" and isinstance(e.get("findings"), dict):
        fd = e["findings"]; bl = fd.get("to_backlog") or []; adr = fd.get("wontfix_adr") or []
        s = f"findings {fd.get('total', 0)}（修 {fd.get('fixed', 0)}／BL {len(bl)}／ADR {len(adr)}）"
        return s + (f"；{'、'.join(bl + adr)}" if bl or adr else "")
    if e.get("type") == "perf":
        return f"{e.get('kind', '')} {e.get('wall_s', '')} 秒 rc={e.get('rc', '—')}"
    return ""


def _notes_appendix(ordered):
    """非 perf 型帶 notes 事件的附錄節（BL-00005）：表後空一行、`## 備註（notes）`、每筆 `### <date>｜<type>｜<標的>`＋空行＋notes 全文（保留換行、不截斷、不轉義）；
    順序＝表列同序（已排序的 ordered 直用）；零筆帶 notes 時回空 list（連標題都不出）。perf 型 notes 住 reference/perf.md、不入。"""
    noted = [e for e in ordered if e.get("notes")]
    if not noted:
        return []
    lines = ["", "## 備註（notes）"]
    for e in noted:
        lines += ["", f"### {e['date']}｜{_type_cell(e)}｜{_target(e)}", "", str(e["notes"])]
    return lines


def gen_milestones(events):
    lines = [GENERATED_HEADER, "# MILESTONES — 事件表（新在前）——perf 型另居 reference/perf.md", "",
             "| date | type | 標的 | summary | merge | adrs | arch |", "|---|---|---|---|---|---|---|"]
    rows = [e for e in events if e.get("type") != "perf"]
    ordered = [e for _, e in sorted(enumerate(rows), key=lambda t: (t[1]["date"], t[0]), reverse=True)]   # 同日依檔內序、新（後 append）在前
    for e in ordered:
        arch = "、".join(e["arch_impact"]) if isinstance(e.get("arch_impact"), list) else e.get("arch_impact", "—")
        cells = (e["date"], _type_cell(e), _target(e), _event_summary(e), _merge_cell(e),
                 "、".join(e.get("adrs", []) or []) or "—", arch)
        lines.append("| " + " | ".join(_cell(x) for x in cells) + " |")
    return "\n".join(lines + _notes_appendix(ordered)) + "\n"


def _pin(ctx, sub):
    try:
        parts = ctx.git("ls-files", "-s", sub).split()
        return parts[1][:7] if len(parts) >= 2 and parts[0] == "160000" else "未掛"
    except GitError:
        return "未掛"


def _lesson_files(ctx):
    """LESSONS/ 檔名集＝tracked ∪ 工作樹（與 book._family_state 同口徑）；只取合 RE_LL_FILE 者、依名排序。"""
    names = {os.path.basename(p) for p in ctx.tracked if p.startswith(LESSONS_DIR + "/")}
    d = os.path.join(ctx.root, LESSONS_DIR)
    if os.path.isdir(d):
        names |= set(os.listdir(d))
    return sorted(n for n in names if book_mod.RE_LL_FILE.match(n))


def _lessons(ctx):
    return [parse_front_matter(ctx.text(f"{LESSONS_DIR}/{n}") or "")[0] for n in _lesson_files(ctx)]


def gen_lessons_index(ctx):
    """例外註冊：索引全生成、檔頭 next＝檔集最大號＋1（永不回收靠 GT-05 單調腿）；列為表格形、不合 RE_ENTRY（零雙計數）。"""
    rows, top = [], 0
    for n in _lesson_files(ctx):
        id_ = book_mod.RE_LL_FILE.match(n).group(1)
        top = max(top, int(id_.rsplit("-", 1)[1]))
        meta, body = parse_front_matter(ctx.text(f"{LESSONS_DIR}/{n}") or "")
        first = next((l for l in body.split("\n") if l.strip()), "")
        title = first.split("｜", 1)[1].strip() if "｜" in first else "（正文首行缺「LL-NNNNN｜坑名」）"
        rows.append(f"| {id_} | {title} | {meta.get('rule_id', '—')} | {meta.get('promotion_surface', '—')} | [{n}](LESSONS/{n}) |")
    lines = [GENERATED_HEADER, f"<!-- next: LL-{top + 1:05d} -->",
             "# LESSONS — 教訓索引（機器生成；一坑一檔住 LESSONS/LL-NNNNN-<slug>.md）", "",
             "配號＝本檔頭 next（自檔集最大號＋1 推導；ADR-00005）→ 建檔 → `python3 tools/docsync generate`。"
             "條目檔 frontmatter：`id`、`rule_id`（RL-NNNN 或 none：理由）、`promotion_surface`（rules／gate／code／none）、選填 `recurrence_of`；"
             "正文首行 `LL-NNNNN｜坑名`（GT-08 對賬）。", "",
             "| LL | 坑名 | rule_id | promotion_surface | 檔 |", "|---|---|---|---|---|"] + rows
    return "\n".join(lines) + "\n"


def _book_meta(ctx, prefix):
    out = []
    for rel in sorted(set(ctx.tracked)):
        if rel.startswith(prefix) and rel.endswith(".md"):
            text = ctx.text(rel)
            if text is not None:
                meta, body = parse_front_matter(text)
                out.append((rel, meta, body))
    return out


def _rad_list(meta):
    v = meta.get("rad_ai")
    return list(v) if isinstance(v, list) else ([v] if isinstance(v, str) and v else [])


def _link(rel, base):
    """自 base 目錄指向 rel 的相對 Markdown 連結（檔名為文字）。"""
    return f"[{os.path.basename(rel)}]({os.path.relpath(rel, base)})"


def gen_architecture_index(ctx):
    """例外註冊：arc42 節檔（NN-*.md）索引——節號＝section、標題＝H1（剝 §N）、摘要＝summary、掛載 E＝rad_ai、流程層檔＝process 中 rad_ai 同值者。"""
    procs = [(rel, _rad_list(meta)) for rel, meta, _ in _book_meta(ctx, "docs/process/")]
    rows = []
    for rel, meta, body in _book_meta(ctx, "docs/arc42/"):
        m = RE_CHAPTER.match(rel)
        if not m:
            continue
        sec = str(meta.get("section") or int(m.group(1)))
        h1 = RE_H1.search(body)
        es = _rad_list(meta)
        joined = "、".join(_link(p, "docs/arc42") for p, pe in procs if set(pe) & set(es)) or "—"
        rows.append((int(sec), f"| §{sec} | [{h1.group(1) if h1 else '（無 H1）'}]({os.path.basename(rel)}) | {meta.get('summary') or '—'} | {'、'.join(es) or '—'} | {joined} |"))
    lines = [GENERATED_HEADER, "# ARCHITECTURE — 活書索引（機器生成、例外註冊）", "",
             "節檔＝`NN-<arc42 英文節名>.md`；標題取各檔 H1、摘要取 frontmatter `summary`、掛載 E 取 `rad_ai`、流程層檔＝`docs/process/` 中 `rad_ai` 同值之檔。"
             "決策住 `decisions/`（索引＝`docs/generated/DECISIONS-INDEX.md`）。", "",
             "| 節 | 檔 | 摘要 | 掛載 E | 流程層檔 |", "|---|---|---|---|---|"] + [r for _, r in sorted(rows)]
    return "\n".join(lines) + "\n"


def _filled(meta, body, item):
    """已填實/N（Q3）：### 標題 ∈ map 值、且子節正文（到下一任意標題前）零 TODO(波 k)；兩鍵同值＝同一標題、逐鍵計。"""
    total = len(book_mod.E_SUBSECTIONS.get(item, ()))
    if not total:
        return "—"
    amap = meta.get("rad_ai_map")
    if not isinstance(amap, dict):
        return f"0/{total}"
    values, done, cur, buf = set(amap.values()), set(), None, []

    def close():
        if cur is not None and not any(book_mod.RE_TODO_WAVE.search(l) for l in buf):
            done.add(cur)
    for line in book_mod.strip_code(body).split("\n"):
        hm = RE_ANY_HEADING.match(line)
        if hm:
            close()
            cur = hm.group(1) if line.startswith("### ") and hm.group(1) in values else None
            buf = []
        else:
            buf.append(line)
    close()
    return f"{sum(1 for v in amap.values() if v in done)}/{total}"


def gen_rad_ai_map(ctx):
    """RAD-AI 項目對照總表（啟動書 §3.3 機器版）：系統層檔／流程層檔各自的填實計數；系統層含「目前無 AI 元件」句→「目前無」。"""
    sysf, procf = {}, {}
    for rel, meta, body in _book_meta(ctx, "docs/"):
        if not book_mod.is_book(rel):
            continue
        for item in _rad_list(meta):
            (procf if rel.startswith("docs/process/") else sysf).setdefault(item, []).append((rel, meta, body))
    lines = [GENERATED_HEADER, "# RAD-AI-MAP — RAD-AI 項目對照總表（啟動書 §3.3 的機器版；DoD A1 驗收面）", "",
             "列＝RAD-AI 項目；系統層檔＝arc42／c4／compliance 中 frontmatter `rad_ai` 含該項目者、流程層檔＝`docs/process/` 同；"
             "子節欄＝`已填實/N`（`###` 標題 ∈ `rad_ai_map` 值且正文零 `TODO(波 k)`；N＝reference 子節數）、系統層含「目前無 AI 元件」句即顯示「目前無」；採用階段取系統層檔 `rad_ai_stage`。", "",
             "| RAD-AI 項目 | 系統層檔 | 系統層子節 | 流程層檔 | 流程層子節 | 採用階段 |", "|---|---|---|---|---|---|"]
    for item in RAD_AI_ITEMS:
        s, p = sysf.get(item, []), procf.get(item, [])
        if not s:
            sys_sub = "—"
        elif any(book_mod.NO_AI_SENTENCE in b for _, _, b in s):
            sys_sub = "目前無"
        else:
            sys_sub = "、".join(_filled(m, b, item) for _, m, b in s)
        stage = "、".join(dict.fromkeys(str(m["rad_ai_stage"]) for _, m, _ in s if m.get("rad_ai_stage"))) or "—"  # 去重、保序
        lines.append(f"| {item} | {'、'.join(_link(r, GENERATED_DIR) for r, _, _ in s) or '—'} | {sys_sub} | "
                     f"{'、'.join(_link(r, GENERATED_DIR) for r, _, _ in p) or '—'} | {'、'.join(_filled(m, b, item) for _, m, b in p) or '—'} | {stage} |")
    return "\n".join(lines) + "\n"


def gen_rev5_blueprint_map(ctx):
    """rev5 藍本對照表（ADR-00006）：frontmatter rev5_blueprint 對 REV5_BLUEPRINT 名冊；缺／重複／未知鍵／形制只排列、永不拋錯（R2-F19 非常駐閘）。"""
    decl = {}
    for rel, meta, _ in _book_meta(ctx, "docs/arc42/"):
        bp = meta.get("rev5_blueprint") if RE_CHAPTER.match(rel) else None
        if isinstance(bp, dict):
            for k, v in bp.items():
                decl.setdefault(k, []).append((rel, str(v)))
    n = {"缺": 0, "重複": 0, "未知鍵": 0, "形制": 0}
    rows = []
    for h, lvl, sec in REV5_BLUEPRINT:
        layer = "##" if lvl == "##" else f"### §{sec}"
        ds = decl.get(h, [])
        if not ds:
            n["缺"] += 1
            rows.append(f"| {h} | {layer} | 缺 | 缺 |")
            continue
        if len(ds) > 1:
            n["重複"] += 1
        for rel, v in ds:
            bad = not v.startswith(BLUEPRINT_DISPOSITIONS)
            n["形制"] += bad
            tag = "重複：" if len(ds) > 1 else ("形制：" if bad else "")
            rows.append(f"| {h} | {layer} | {_link(rel, BLUEPRINT_DIR)} | {tag}{v} |")
    for h in sorted(set(decl) - {h for h, _, _ in REV5_BLUEPRINT}):
        n["未知鍵"] += 1
        rows.append(f"| {h} | 未知鍵 | {'、'.join(_link(r, BLUEPRINT_DIR) for r, _ in decl[h])} | 未知鍵 |")
    lines = [GENERATED_HEADER, "# reference/rev5-blueprint-map — rev5 活書藍本對照表（一次性 migrate-audit 面；ADR-00006）", "",
             "名冊＝rev5 活書 `../fork260509-rev5/docs/arc42/ARCHITECTURE.md`（凍結 SHA 7eab28a）的 12 個 `##`＋8 個 `###`（`references.REV5_BLUEPRINT`）；"
             "去處＝`docs/arc42/NN-*.md` frontmatter `rev5_blueprint`（鍵＝rev5 標題字面、值＝承襲（…）／隨刀：…／不承襲：…）。"
             "未宣告列「缺」、多檔宣告標「重複」、鍵不在名冊列「未知鍵」、值不以三詞起頭標「形制」；四項皆零＝藍本對照表零缺（波 3 出口判準、非常駐閘）。", "",
             "| rev5 標題 | 層 | rev6 去處 | 處置 |", "|---|---|---|---|"] + rows + \
            ["", f"缺：{n['缺']}｜重複：{n['重複']}｜未知鍵：{n['未知鍵']}｜形制：{n['形制']}"]
    return "\n".join(lines) + "\n"


AGENTS_MD = "docs/generated/reference/agents.md"
AGENTS_EMPTY = "**目前無**：tracked `tools/orchestration/*.js`／`*.mjs` 中零 `*_OPTS` 字面——掃描面空集合（RL-0051；check 同時回一筆警示）。"


def _agents_rows(ctx):
    """*_OPTS 名冊列（000-r2 L4-08：字面形一改即靜默縮小掃描面，故零命中須明說並警示）。"""
    rows = []
    for rel in sorted(set(ctx.tracked)):
        if rel.startswith("tools/orchestration/") and rel.endswith((".js", ".mjs")) and rel not in GENERATED_FILES:
            for m in RE_OPTS.finditer(ctx.text(rel) or ""):
                rows.append(f"| {os.path.basename(rel)} | {m.group(1)} | {m.group(2)} | {m.group(3)} |")
    return rows


def gen_reference_agents(ctx):
    """編排 script 的模型與 effort 名冊（啟動書 §3.2 P-E2）：tracked tools/orchestration/*.js|*.mjs 的 `const X_OPTS = { model, effort }` 字面；名冊內生成物不入掃描面。"""
    rows = _agents_rows(ctx)
    lines = [GENERATED_HEADER, "# reference/agents — 編排 script 的模型與 effort 名冊", "",
             "來源＝tracked `tools/orchestration/*.js`／`*.mjs`（名冊內生成物 `_sk_rules.js` 除外）的 `const <NAME>_OPTS = { model, effort }` 字面；★`EXAMPLE-*.mjs` 列＝組裝當時的成品快照，換模真源恆為 `_sk_head.js`（generate 重算）；"
             "角色×刻板型×產物進哪道閘＝`docs/process/P-E2-agent-registry.md`（人寫）；換模史＝git。", "",
             "| script | 常數 | model | effort |", "|---|---|---|---|"] + rows
    if not rows:
        lines += ["", AGENTS_EMPTY]
    return "\n".join(lines) + "\n"


# ─── reference/routes：rust-api/server/src/router.rs 之 ROUTES const 全量表（002 刀 U1；契約＝`docs/ops/reference-src/code-gate-contracts.md` §6） ───
# 窄假設行級解析（標準庫、不 parse Rust）＝data-model §4 機器契約：只認 router.rs 現行實際使用的字面形；任一偏離
# 即 RouterRoutesError（fail-loud、generate 非零、GT-01 連帶紅）——寧可擋下、絕不靜默漏列一條 route。
ROUTER_SOURCE = "rust-api/server/src/router.rs"
ROUTE_METHODS = {"Get": "GET", "Post": "POST", "Delete": "DELETE"}   # HttpMethod variant → casbin act 字面（全集；新增 variant 即紅逼同步）
ROUTE_PROTECTIONS = ("Public", "Authed", "Policy")                     # Protection 三態（全集）
ROUTE_REQUIRED_FIELDS = ("path", "method", "case_key", "envelope_exception", "protection")   # handler 識形後不入表
RE_ROUTES_CONST_OPEN = re.compile(r"^pub const ROUTES:\s*&\[RouteDef\]\s*=\s*&\[$")
RE_ROUTE_FIELD_PATH = re.compile(r'^path:\s*"([^"]*)",$')
RE_ROUTE_FIELD_METHOD = re.compile(r"^method:\s*HttpMethod::(\w+),$")
RE_ROUTE_FIELD_HANDLER = re.compile(r"^handler:\s*\|\|\s*(?:get|post|delete)\(.+\),$")
RE_ROUTE_FIELD_CASE_KEY = re.compile(r'^case_key:\s*"([^"]*)",$')
RE_ROUTE_FIELD_ENVELOPE = re.compile(r"^envelope_exception:\s*(true|false),$")
RE_ROUTE_FIELD_PROTECTION = re.compile(r"^protection:\s*Protection::(\w+),$")


class RouterRoutesError(Exception):
    """router.rs ROUTES 解析失敗（fail-loud：來源缺席／字面形偏離／未知 variant 一律拋、不設 Day-1 豁免）。"""


def _parse_route_field(stripped, rel, n):
    """RouteDef 條目內單行欄位 → (key, value)；handler 閉包識形後回 (None, None)（不入表）。
    不認得的欄／形、未知 HttpMethod／Protection variant → RouterRoutesError 指名 rel:行。"""
    m = RE_ROUTE_FIELD_PATH.fullmatch(stripped)
    if m:
        return "path", m.group(1)
    m = RE_ROUTE_FIELD_CASE_KEY.fullmatch(stripped)
    if m:
        return "case_key", m.group(1)
    m = RE_ROUTE_FIELD_ENVELOPE.fullmatch(stripped)
    if m:
        return "envelope_exception", m.group(1) == "true"
    m = RE_ROUTE_FIELD_METHOD.fullmatch(stripped)
    if m:
        if m.group(1) not in ROUTE_METHODS:
            raise RouterRoutesError(f"{rel}:行 {n}｜未知 HttpMethod::{m.group(1)}（已知：{'／'.join(ROUTE_METHODS)}；router.rs 新增動詞須同步擴充本解析器）")
        return "method", ROUTE_METHODS[m.group(1)]
    m = RE_ROUTE_FIELD_PROTECTION.fullmatch(stripped)
    if m:
        if m.group(1) not in ROUTE_PROTECTIONS:
            raise RouterRoutesError(f"{rel}:行 {n}｜未知 Protection::{m.group(1)}（已知：{'／'.join(ROUTE_PROTECTIONS)}；router.rs 新增授權態須同步擴充本解析器）")
        return "protection", m.group(1)
    if RE_ROUTE_FIELD_HANDLER.fullmatch(stripped):
        return None, None
    raise RouterRoutesError(f"{rel}:行 {n}｜RouteDef 內不認得的欄/形「{stripped}」（僅支援 path／method／handler／case_key／envelope_exception／protection 六欄、每欄一行 `key: value,`；router.rs 改寫法須同步擴充本解析器）")


def parse_router_routes(text, rel):
    """解析 router.rs 的 `pub const ROUTES: &[RouteDef] = &[` … `];` block → [(path, method, protection, case_key, envelope_exception)]，列序＝宣告序。
    block 頂層只認 `RouteDef {`（起條目）／`}`、`},`（收條目）／`];`（收尾）／空行／`//` 註解；條目內每欄一行、handler 識形後略過；
    缺欄／重複欄／未知欄或 variant／找不到精確開頭／block 未收尾 → RouterRoutesError 指名 rel:行。const 外一律不碰（struct 定義、build 迭代、doc 註解）。"""
    rows, entry, entry_line, found, in_block = [], None, None, False, False
    for n, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not in_block:
            if RE_ROUTES_CONST_OPEN.fullmatch(stripped):
                found = in_block = True
            continue
        if not stripped or stripped.startswith("//"):
            continue
        if entry is None:
            if stripped == "];":
                in_block = False
                break
            if stripped == "RouteDef {":
                entry, entry_line = {}, n
                continue
            raise RouterRoutesError(f"{rel}:行 {n}｜ROUTES block 頂層不認得的行「{stripped}」（頂層只准 RouteDef 條目、// 註解與收尾 ];）")
        if stripped in ("}", "},"):
            missing = [f for f in ROUTE_REQUIRED_FIELDS if f not in entry]
            if missing:
                raise RouterRoutesError(f"{rel}:行 {entry_line}｜RouteDef 條目缺欄 {missing}")
            rows.append((entry["path"], entry["method"], entry["protection"], entry["case_key"], entry["envelope_exception"]))
            entry = None
            continue
        key, value = _parse_route_field(stripped, rel, n)
        if key is None:
            continue
        if key in entry:
            raise RouterRoutesError(f"{rel}:行 {n}｜RouteDef 條目重複欄「{key}」")
        entry[key] = value
    if not found:
        raise RouterRoutesError(f"{rel}｜找不到精確開頭 `pub const ROUTES: &[RouteDef] = &[`——routes 真表無法重算")
    if in_block:
        raise RouterRoutesError(f"{rel}｜ROUTES block 未見收尾 ];（防半解析漏列）")
    return rows


def gen_reference_routes(ctx):
    """reference/routes ← router.rs ROUTES const 全量表（來源缺席＝raise；列序＝ROUTES 宣告序、不排序）。"""
    text = ctx.text(ROUTER_SOURCE)
    if text is None:
        raise RouterRoutesError(f"{ROUTER_SOURCE}｜router 來源檔缺席——routes 真表無法重算（002 刀 U1 起永不缺席、無 Day-1 豁免）")
    lines = [GENERATED_HEADER, "# reference/routes — 全量正典表", "",
             f"來源＝{ROUTER_SOURCE} 的 ROUTES const（generate 重算；handler 閉包不入表）。", "",
             "| path | method | protection | case_key | envelope 例外 |", "|---|---|---|---|---|"]
    for path, method, protection, case_key, env in parse_router_routes(text, ROUTER_SOURCE):
        lines.append(f"| {path} | {method} | {protection} | {case_key} | {'是' if env else '否'} |")
    return "\n".join(lines) + "\n"


def _docsync_lines(ctx):
    """docsync package 行數（wc -l 口徑＝`cat tools/docsync/*.py | wc -l`；不含 tests/ 語料面，與 CLAUDE.md 行數同法）。"""
    return sum((ctx.text(rel) or "").count("\n") for rel in ctx.tracked
               if rel.startswith("tools/docsync/") and rel.endswith(".py") and rel.count("/") == 2)


def _budget_rows(ctx, counts, caps):
    rows = []
    try:
        from . import gates
        n_gates, cap_gates = len(gates.ROSTER), gates.BUDGET_GATES   # 上限單一家＝gates.py（GT-12 執行用同一常數）
    except Exception:
        n_gates = cap_gates = "n/a"
    rows.append(("閘數", n_gates, cap_gates))
    for k in ("總",) + rules_mod.SCOPES:
        if k in counts:
            rows.append((f"RULES {k}", counts[k], caps.get(k, "—")))
    rows.append(("docsync 行數", _docsync_lines(ctx), 4000))   # 啟動書 §4.3／spec SC-007＝目標非閘（GT-12 不加腿；BL-00012）
    lines = ["| 項目 | 現值 | 上限 | 狀態 |", "|---|---|---|---|"]
    for name, val, cap in rows:
        status = "—" if not isinstance(val, int) or not isinstance(cap, int) else ("內" if val <= cap else "超")
        lines.append(f"| {name} | {val} | {cap} | {status} |")
    return lines


def _ellipsize(s, n):
    """截斷補「…」（000-r2 L1-11）：舊形 `[:80]` 無記號、句子中斷且括號不成對。
    ★Python str 以碼位索引、不可能切在多位元組字元中間（byte 級切割才會）。"""
    s = str(s)
    return s if len(s) <= n else s[:n - 1] + "…"


# 治理指標的目標與達標判準（000-r2 L1-10：舊表只有值與自由文字目標，7.5 對 ≤1 與達標列渲染完全相同）
METRIC_GOALS = (
    ("治理批對 feature 比", "gov_ratio", "≤1", lambda v: v <= 1),
    ("LESSONS 重複率", "lessons_dup_rate", "0", lambda v: v == 0),
    ("BACKLOG 淨流量（rolling 3 刀）", "backlog_net", "≤0", lambda v: v <= 0),
)


def _metric_status(v, ok):
    """達標／超標；n/a 等無值者印「—」（無值可判、不等於達標）。"""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return "—"
    return "達標" if ok(v) else "超標"


def _metric_rows(m):
    return [f"| {label} | {m[key]} | {goal} | {_metric_status(m[key], ok)} |" for label, key, goal, ok in METRIC_GOALS]


def _probe_row(pr):
    """ADR-00021 檢索性列：最近一筆帶 probe 之 review 事件、比例現算；目標＝找不到＋答錯＝0、≤3 跳比例輪間不降。
    ★狀態欄只判得動前半（找不到＋答錯＝0）；「輪間不降」需前一筆 probe 才可判、本列以「—（需前輪值）」明示。"""
    goal = "找不到＋答錯＝0；≤3 跳比例輪間不降"
    if pr == "n/a":
        return f"| 檢索性（最近獨立輪探針） | n/a | {goal} | — |"
    status = _metric_status(pr["not_found"] + pr["wrong"], lambda v: v == 0) + "；輪間不降 —（需前輪值）"
    return (f"| 檢索性（最近獨立輪 {pr['scope']}） | ≤3 跳 {pr['le3_ratio']}／答對 {pr['hit_ratio']}／找不到 {pr['not_found']}／答錯 {pr['wrong']}"
            f"（否定對照答錯 {pr['negative_wrong']}）；平均最短 hops {pr['avg_min_hops']} | {goal} | {status} |")


def gen_state(ctx):
    events, _ = ev_mod.events_view(ctx.text(EVENTS))   # 人讀面吃更正視圖（BL-00004）
    adrs = adr_mod.load_adrs(ctx)
    by_status = {}
    for a in adrs.values():
        by_status[a.status] = by_status.get(a.status, 0) + 1
    counts, caps = rules_mod.budget_counts(ctx.text(RULES) or "")
    bl_text = ctx.text(BACKLOG)
    backlog_open = len(book_mod.RE_ENTRY["BL"].findall(bl_text)) if bl_text is not None else "未建"
    deferred = ctx.text(BACKLOG_DEFERRED)
    lessons = _lessons(ctx)
    wave = book_mod.current_wave(ctx)
    ver = RE_VERSION.search(ctx.text(CONSTITUTION) or "")
    ev_counts = {}
    for e in events:
        ev_counts[e["type"]] = ev_counts.get(e["type"], 0) + 1
    m = ev_mod.metrics(events, lessons)
    claude = ctx.text("CLAUDE.md")
    lines = [GENERATED_HEADER, "# STATE — 現況機器帳", "", "## git",
             f"- default branch：{DEFAULT_BRANCH}（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）",
             "- pins：" + "｜".join(f"{sub}={_pin(ctx, sub)}" for sub in SUBMODULES), "",
             "## 現在波", f"- 波：{wave if wave is not None else '未標記'}（docs/ops/NOTES.md 首行標記）", "",
             "## constitution", f"- 版本：{ver.group(1) if ver else '未定版'}", "",
             "## 帳面統計",
             f"- ADR：{len(adrs)}（" + "、".join(f"{s} {by_status.get(s, 0)}" for s in adr_mod.ADR_STATUSES) + "）",
             f"- RULES：{counts['總']} 條／上限 {caps.get('總', '—')}（" + "、".join(f"{s} {counts[s]}/{caps.get(s, '—')}" for s in rules_mod.SCOPES) + "）",
             f"- BACKLOG 開放：{backlog_open}" + (f"｜滯後：{len(book_mod.RE_ENTRY['BL'].findall(deferred))}" if deferred is not None else "｜滯後：未建"),
             f"- LESSONS：{len(lessons)} 筆" + ("" if lessons else "（未建）"),
             f"- events：{len(events)} 筆（" + "、".join(f"{t} {n}" for t, n in sorted(ev_counts.items())) + "）",
             f"- CLAUDE.md 行數：{len(claude.split(chr(10))) - (1 if claude.endswith(chr(10)) else 0) if claude else 0}（只報表、不擋）", "",
             "## 治理指標（啟動書 §4.3 三項＋ADR-00021 檢索性）", "| 指標 | 值 | 目標 | 狀態 |", "|---|---|---|---|",
             ] + _metric_rows(m) + [_probe_row(m["probe_retrieval"]), "",
             "## 數量預算對賬（D8；ADR-00011：超限只警告、不擋）"] + _budget_rows(ctx, counts, caps) + ["", "## 最近事件（尾 3 筆、新在前）"]
    for e in list(reversed(events))[:3]:
        lines.append(f"- {e['date']}｜{e['type']}｜{_target(e)}｜{_ellipsize(_event_summary(e), 80)}")
    return "\n".join(lines) + "\n"


def compute_generated(ctx):
    """名冊→內容；GATES.md 由 gates.gen_gates_md 產（遲載避循環、匯入失敗不吞＝fail-loud）。
    回傳前對賬 GENERATED_FILES 名冊 ⇔ 計算面，缺任一鍵即 raise（000-r2 L3-10：靜默退出計算面會讓 check 仍報零漂移）。"""
    events, _ = ev_mod.events_view(ctx.text(EVENTS))   # 人讀面吃更正視圖（BL-00004）
    out = {
        "docs/generated/STATE.md": gen_state(ctx),
        "docs/generated/MILESTONES.md": gen_milestones(events),
        "docs/generated/DECISIONS-INDEX.md": adr_mod.gen_decisions_index(adr_mod.load_adrs(ctx), events),
        "docs/generated/reference/ports.md": gen_reference_ports(ctx),
        "docs/generated/reference/perf.md": gen_reference_perf(events),
        "tools/orchestration/_sk_rules.js": rules_mod.emit_js(ctx.text(RULES) or ""),
        "docs/generated/RAD-AI-MAP.md": gen_rad_ai_map(ctx),
        "docs/arc42/ARCHITECTURE.md": gen_architecture_index(ctx),
        "docs/ops/LESSONS.md": gen_lessons_index(ctx),
        "docs/generated/reference/rev5-blueprint-map.md": gen_rev5_blueprint_map(ctx),
        "docs/generated/reference/agents.md": gen_reference_agents(ctx),
        "docs/generated/reference/schema.md": snapshot_mod.gen_reference_schema(ctx),
        "docs/generated/reference/accounts.md": snapshot_mod.gen_reference_accounts(ctx),
        "docs/generated/reference/routes.md": gen_reference_routes(ctx),
    }
    from . import gates   # 遲載避循環；★不吞 ImportError（000-r2 L3-10）：GATES.md 靜默退出計算面會讓 check 仍報零漂移
    out["docs/generated/GATES.md"] = gates.gen_gates_md(ctx)
    missing = [rel for rel in GENERATED_FILES if rel not in out]
    if missing:
        raise RuntimeError(f"compute_generated 計算面缺 {missing}——GT-01「零漂移」會對這些檔靜默失真（名冊 ⇔ 計算面須同批改齊）")
    return out


def check_generated(ctx, computed):
    """GT-01 本體：缺（名冊有、樹無）／漂移（內容不等）／名冊外（docs/generated/** tracked 但不在名冊）。"""
    out = []
    for rel, text in computed.items():
        cur = ctx.text(rel)
        if cur is None:
            out.append(finding(ERROR, "GT-01", rel, "生成檔缺席——跑 python3 tools/docsync generate"))
        elif cur != text:
            out.append(finding(ERROR, "GT-01", rel, "生成檔漂移（與真源重算不等）——禁手改；跑 python3 tools/docsync generate"))
    for rel in ctx.tracked:
        if rel.startswith(GENERATED_DIR + "/") and rel not in GENERATED_FILES:
            out.append(finding(ERROR, "GT-01", rel, "名冊外生成檔——docs/generated/** 只可含 GENERATED_FILES 名冊所列"))
    if not _agents_rows(ctx):   # 000-r2 L4-08：真源掃描面空集合＝警示，不是一張看起來正常的空表
        out.append(finding(WARN, "GT-01", AGENTS_MD, "掃描面空集合：tools/orchestration 之 *_OPTS 字面零命中（字面形改動會靜默縮小掃描面；RL-0051）"))
    return out


def cmd_generate(ctx):
    """先回填 ADR supersede 對稱、再依名冊寫檔；回實際寫入（內容有變或新建）的 rel 清單。"""
    written = adr_mod.backfill_superseded_by(ctx)
    ctx._cache.clear()
    for rel, text in compute_generated(ctx).items():
        p = os.path.join(ctx.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        old = ctx.text(rel)
        if old != text:
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            written.append(rel)
        ctx._cache.pop(rel, None)
    return written


def cmd_check(ctx):
    return check_generated(ctx, compute_generated(ctx))
