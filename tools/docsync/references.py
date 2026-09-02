"""守 RL-0049／RL-0052：generated 只由真源重算、零漂移（GT-01 本體）；數量預算對賬入 STATE。

references.py：parse_ports／gen_reference_ports（compose 三檔）、gen_reference_perf、gen_milestones、gen_state（git／波／憲法／帳面／三指標／預算／尾 3 事件）、
compute_generated（名冊→內容）、check_generated（缺／漂移／名冊外）、cmd_generate（先回填 ADR 對稱、冪等寫檔）。
"""
import os
import re

from . import (EVENTS, RULES, BACKLOG, BACKLOG_DEFERRED, LESSONS_DIR, GENERATED_DIR, CONSTITUTION, DEFAULT_BRANCH,
               SUBMODULES, COMPOSE_FILES, NOTES)
from .common import ERROR, GENERATED_HEADER, GitError, finding, parse_front_matter
from . import events as ev_mod
from . import adr as adr_mod
from . import rules as rules_mod
from . import book as book_mod

GENERATED_FILES = (
    "docs/generated/STATE.md", "docs/generated/MILESTONES.md", "docs/generated/DECISIONS-INDEX.md", "docs/generated/GATES.md",
    "docs/generated/reference/ports.md", "docs/generated/reference/perf.md", "tools/orchestration/_sk_rules.js",
)
RE_PORT = re.compile(r'^\s+-\s+"?(?:(\d{1,3}(?:\.\d{1,3}){3}):)?(\d+):(\d+)(?:/(?:tcp|udp))?"?\s*$')
RE_VERSION = re.compile(r"\*\*Version\*\*:\s*([0-9.]+)")
PORT_GENERATION_PREFIX = "3"
BUDGET_GATES, BUDGET_BACKLOG_OPEN = 12, 25


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


def gen_reference_perf(events):
    lines = [GENERATED_HEADER, "# reference/perf — 收刀簿記與 pre-commit 效能資料點", "",
             "來源＝docs/ops/events.jsonl 的 perf 事件（generate 重算；kind＝close_bookkeeping／precommit_chain、量測法承 rev5:RUNBOOK §12.1）。", "",
             "| date | kind | wall_s | rc | commit | notes |", "|---|---|---|---|---|---|"]
    for e in events:
        if e.get("type") != "perf":
            continue
        notes = (e.get("notes") or "").split("\n", 1)[0]
        lines.append(f"| {e['date']} | {e['kind']} | {e['wall_s']} | {e.get('rc', '—')} | {str(e.get('commit', '—'))[:7]} | {notes} |")
    return "\n".join(lines) + "\n"


def _target(e):
    return e.get("feature") or e.get("scope") or e.get("category") or (f"行 {e['target_line']}" if e.get("type") == "erratum" else "—")


def gen_milestones(events):
    lines = [GENERATED_HEADER, "# MILESTONES — 事件表（新在前）——perf 型另居 reference/perf.md", "",
             "| date | type | 標的 | summary | merge | adrs | arch |", "|---|---|---|---|---|---|---|"]
    rows = [e for e in events if e.get("type") != "perf"]
    for e in sorted(rows, key=lambda e: e["date"], reverse=True):
        summary = e.get("summary") or e.get("reason") or (str(e.get("findings")) if e.get("type") == "review" else "")
        merge = str(e.get("merge") or e.get("corrected") or "")[:7] or "—"
        lines.append(f"| {e['date']} | {e['type']} | {_target(e)} | {summary} | {merge} | {'、'.join(e.get('adrs', []) or []) or '—'} | "
                     f"{'、'.join(e['arch_impact']) if isinstance(e.get('arch_impact'), list) else e.get('arch_impact', '—')} |")
    return "\n".join(lines) + "\n"


def _pin(ctx, sub):
    try:
        parts = ctx.git("ls-files", "-s", sub).split()
        return parts[1][:7] if len(parts) >= 2 and parts[0] == "160000" else "未掛"
    except GitError:
        return "未掛"


def _lessons(ctx):
    names = sorted(n for n in set(os.path.basename(p) for p in ctx.tracked if p.startswith(LESSONS_DIR + "/")) if book_mod.RE_LL_FILE.match(n))
    out = []
    for n in names:
        meta, _ = parse_front_matter(ctx.text(f"{LESSONS_DIR}/{n}") or "")
        out.append(meta)
    return out


def _budget_rows(ctx, counts, caps, backlog_open):
    rows = []
    try:
        from . import gates
        n_gates = len(gates.ROSTER)
    except Exception:
        n_gates = "n/a"
    rows.append(("閘數", n_gates, BUDGET_GATES))
    for k in ("總",) + rules_mod.SCOPES:
        if k in counts:
            rows.append((f"RULES {k}", counts[k], caps.get(k, "—")))
    rows.append(("BACKLOG 開放", backlog_open, BUDGET_BACKLOG_OPEN))
    lines = ["| 項目 | 現值 | 上限 | 狀態 |", "|---|---|---|---|"]
    for name, val, cap in rows:
        status = "—" if not isinstance(val, int) or not isinstance(cap, int) else ("內" if val <= cap else "超")
        lines.append(f"| {name} | {val} | {cap} | {status} |")
    return lines


def gen_state(ctx):
    events, _ = ev_mod.parse_events(ctx.text(EVENTS))
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
             f"- default branch：{DEFAULT_BRANCH}",
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
             "## 三指標（啟動書 §4.3）", "| 指標 | 值 | 目標 |", "|---|---|---|",
             f"| 治理批對 feature 比 | {m['gov_ratio']} | ≤1 |", f"| LESSONS 重複率 | {m['lessons_dup_rate']} | 0 |",
             f"| BACKLOG 淨流量（rolling 3 刀） | {m['backlog_net']} | ≤0 |", "",
             "## 數量預算對賬（D8；級別由 GT-12 定）"] + _budget_rows(ctx, counts, caps, backlog_open) + ["", "## 最近事件（尾 3 筆、新在前）"]
    for e in list(reversed(events))[:3]:
        lines.append(f"- {e['date']}｜{e['type']}｜{_target(e)}｜{(e.get('summary') or e.get('reason') or '')[:80]}")
    return "\n".join(lines) + "\n"


def compute_generated(ctx):
    """名冊→內容。GATES.md 由 gates.gen_gates_md 產（gates 模組缺席時暫不入計算面）。"""
    events, _ = ev_mod.parse_events(ctx.text(EVENTS))
    out = {
        "docs/generated/STATE.md": gen_state(ctx),
        "docs/generated/MILESTONES.md": gen_milestones(events),
        "docs/generated/DECISIONS-INDEX.md": adr_mod.gen_decisions_index(adr_mod.load_adrs(ctx), events),
        "docs/generated/reference/ports.md": gen_reference_ports(ctx),
        "docs/generated/reference/perf.md": gen_reference_perf(events),
        "tools/orchestration/_sk_rules.js": rules_mod.emit_js(ctx.text(RULES) or ""),
    }
    try:
        from . import gates
        out["docs/generated/GATES.md"] = gates.gen_gates_md(ctx)
    except ImportError:
        pass
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
