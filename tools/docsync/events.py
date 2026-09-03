"""守 RL-0055／RL-0053：事件帳逐型 schema 與 SHA 實證；收刀與 review 事件完整性。

events.py：parse_events（jsonl、行界只認 \\n）、EVENT_SCHEMAS（rev6 欄位：五碼 ID、feature_close.window、misc.category）、
gt_02（schema／SHA 實證／pin 互證／window 序號）、gt_03（specs／ADR／report 存在）、metrics（§4.3 三指標）。
"""
import json
import os
import re

from . import EVENTS, ADR_DIR
from .common import ERROR, SKIP, finding, GitError

RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_FEATURE = re.compile(r"^\d{3}-[a-z0-9][a-z0-9-]*$")
RE_SHA = re.compile(r"^[0-9a-f]{40}$")
RE_SECTION = re.compile(r"^§\d{1,2}$")
RE_ADR = re.compile(r"^ADR-\d{5}$")
RE_BID = re.compile(r"^BL-\d{5}$")
RE_LID = re.compile(r"^LL-\d{5}$")
SUMMARY_CHAR_LIMIT = 300
PIN_KEYS = (("web", "base-web"), ("api", "rust-api"))
PERF_KINDS = ("close_bookkeeping", "precommit_chain")
ERRATUM_FIELDS = ("merge", "pins.web", "pins.api", "commit")
CATEGORIES = ("product", "governance")

EVENT_SCHEMAS = {
    "feature_close": {
        "required": ("type", "date", "feature", "summary", "merge", "pins", "adrs", "arch_impact",
                     "backlog_add", "backlog_done", "window"),
        "optional": ("notes", "kind", "spec_supersessions"),
    },
    "misc": {
        "required": ("type", "date", "summary", "category", "backlog_add"),
        "optional": ("notes", "backlog_done", "merge", "workflow"),
    },
    "review": {
        "required": ("type", "date", "scope", "report", "findings"),
        "optional": ("feature", "notes"),
    },
    "erratum": {
        "required": ("type", "date", "target_line", "field", "corrected", "reason"),
        "optional": ("notes",),
    },
    "perf": {
        "required": ("type", "date", "kind", "wall_s", "notes"),
        "optional": ("rc", "commit"),
    },
}


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _id_list_ok(v, pattern):
    return isinstance(v, list) and all(isinstance(x, str) and pattern.fullmatch(x) for x in v)


def _check_event(e):
    """單筆事件的欄位驗證；回錯誤訊息 list（形承 rev5 docs-sync、正則換 rev6 五碼）。"""
    if not isinstance(e, dict):
        return ["事件須為 JSON object（一行一事件）"]
    errs = []
    etype = e.get("type")
    schema = EVENT_SCHEMAS.get(etype)
    if schema is None:
        return [f"未知 type「{etype}」（合法：{'/'.join(EVENT_SCHEMAS)}）"]
    for k in schema["required"]:
        if k not in e:
            errs.append(f"缺必填欄位「{k}」")
    allowed = set(schema["required"]) | set(schema["optional"])
    for k in e:
        if k not in allowed:
            errs.append(f"未知欄位「{k}」")
    if errs:
        return errs
    if not RE_DATE.fullmatch(str(e["date"])):
        errs.append(f"date 格式須為 YYYY-MM-DD：{e['date']!r}")
    if "summary" in e:
        s = e["summary"]
        if not isinstance(s, str) or "\n" in s or "\r" in s:
            errs.append("summary 須為單行字串（多段敘述移 notes）")
        elif len(s) > SUMMARY_CHAR_LIMIT:
            errs.append(f"summary {len(s)} 字超出單筆上限 {SUMMARY_CHAR_LIMIT}——細節移 notes／報告檔／LESSONS")
    if etype == "feature_close":
        if not RE_FEATURE.fullmatch(str(e["feature"])):
            errs.append(f"feature 格式須為 NNN-slug：{e['feature']!r}")
        if not RE_SHA.fullmatch(str(e["merge"])):
            errs.append(f"merge 須為 40 位 hex SHA：{e['merge']!r}")
        pins = e["pins"]
        if not (isinstance(pins, dict) and set(pins) == {"web", "api"} and all(RE_SHA.fullmatch(str(v)) for v in pins.values())):
            errs.append('pins 須為 {"web": SHA, "api": SHA}')
        if not _id_list_ok(e["adrs"], RE_ADR):
            errs.append("adrs 須為 ADR-NNNNN 字串 list（可空）")
        ai = e["arch_impact"]
        if not (ai == "none" or (isinstance(ai, list) and ai and all(isinstance(x, str) and RE_SECTION.fullmatch(x) for x in ai))):
            errs.append('arch_impact 須為 ["§N", …] 或 "none"')
        for k in ("backlog_add", "backlog_done"):
            if not _id_list_ok(e[k], RE_BID):
                errs.append(f"{k} 須為 BL-NNNNN 字串 list（可空）")
        if not (_is_int(e["window"]) and e["window"] >= 1):
            errs.append(f"window 須為正整數（第 k 筆 feature_close 之序號）：{e['window']!r}")
        if "kind" in e and e["kind"] not in ("vertical", "horizontal"):
            errs.append('kind 須為 "vertical"|"horizontal"')
        if "spec_supersessions" in e:
            ss = e["spec_supersessions"]
            if not (isinstance(ss, list) and all(isinstance(x, dict) and set(x) == {"feature", "item", "note"} for x in ss)):
                errs.append("spec_supersessions 須為 [{feature,item,note},…]")
    elif etype == "misc":
        if e["category"] not in CATEGORIES:
            errs.append(f"category 須為 {'/'.join(CATEGORIES)} 之一：{e['category']!r}")
        if not _id_list_ok(e["backlog_add"], RE_BID):
            errs.append("backlog_add 須為 BL-NNNNN 字串 list（可空）")
        if "backlog_done" in e and not _id_list_ok(e["backlog_done"], RE_BID):
            errs.append("backlog_done 須為 BL-NNNNN 字串 list（可空）")
        if "merge" in e and not (isinstance(e["merge"], str) and RE_SHA.fullmatch(e["merge"])):
            errs.append(f"merge 須為 40 位 hex SHA：{e['merge']!r}")
        if "workflow" in e and not (isinstance(e["workflow"], str) and e["workflow"].strip()):
            errs.append("workflow 須為非空字串")
    elif etype == "review":
        if not (isinstance(e["scope"], str) and e["scope"].strip()):
            errs.append("scope 須為非空字串")
        if not (isinstance(e["report"], str) and e["report"].endswith(".md")):
            errs.append("report 須為 .md 路徑（docs/reviews/YYYYMMDD-<scope>.md）")
        if "feature" in e and not RE_FEATURE.fullmatch(str(e["feature"])):
            errs.append(f"feature 格式須為 NNN-slug：{e['feature']!r}")
        fd = e["findings"]
        if not (isinstance(fd, dict) and set(fd) == {"total", "fixed", "to_backlog", "wontfix_adr"}
                and _is_int(fd.get("total")) and fd["total"] >= 0 and _is_int(fd.get("fixed")) and fd["fixed"] >= 0
                and _id_list_ok(fd.get("to_backlog"), RE_BID) and _id_list_ok(fd.get("wontfix_adr"), RE_ADR)):
            errs.append("findings 須為 {total≥0, fixed≥0, to_backlog[BL-NNNNN…], wontfix_adr[ADR-NNNNN…]}")
        elif fd["fixed"] + len(fd["to_backlog"]) + len(fd["wontfix_adr"]) != fd["total"]:
            errs.append("findings 分流不守恆：fixed＋len(to_backlog)＋len(wontfix_adr) 須＝total")
    elif etype == "erratum":
        if not (_is_int(e["target_line"]) and e["target_line"] >= 1):
            errs.append(f"target_line 須為正整數（events.jsonl 行號）：{e['target_line']!r}")
        if e["field"] not in ERRATUM_FIELDS:
            errs.append(f"field 須為 {'/'.join(ERRATUM_FIELDS)} 之一：{e['field']!r}")
        if not (isinstance(e["corrected"], str) and RE_SHA.fullmatch(e["corrected"])):
            errs.append(f"corrected 須為 40 位 hex SHA：{e['corrected']!r}")
        r = e["reason"]
        if not (isinstance(r, str) and r.strip() and "\n" not in r and "\r" not in r):
            errs.append("reason 須為非空單行字串")
    elif etype == "perf":
        if e["kind"] not in PERF_KINDS:
            errs.append(f"kind 須為 {'/'.join(PERF_KINDS)} 之一：{e['kind']!r}")
        w = e["wall_s"]
        if not (isinstance(w, (int, float)) and not isinstance(w, bool) and w > 0):
            errs.append(f"wall_s 須為正數（秒）：{w!r}")
        if "rc" in e and not (_is_int(e["rc"]) and e["rc"] >= 0):
            errs.append(f"rc 須為非負整數：{e['rc']!r}")
        if "commit" in e and not (isinstance(e["commit"], str) and RE_SHA.fullmatch(e["commit"])):
            errs.append(f"commit 須為 40 位 hex SHA：{e['commit']!r}")
        if not (isinstance(e["notes"], str) and e["notes"].strip()):
            errs.append("notes 須為非空字串")
    return errs


def _parse_lines(text):
    """逐行解析；回 [(lineno, event|None, [err…])]。行界只認 \\n（splitlines 會在 U+2028 誤切）；檔尾換行不算空行。"""
    lines = (text or "").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    out = []
    for i, raw in enumerate(lines, 1):
        if raw.strip() == "":
            out.append((i, None, ["空行（jsonl 一行一事件、不得留空行）"]))
            continue
        try:
            e = json.loads(raw)
        except ValueError as ex:
            out.append((i, None, [f"JSON 解析失敗：{ex}"]))
            continue
        errs = _check_event(e)
        out.append((i, e if not errs else None, errs))
    return out


def parse_events(text):
    """回 (events, errors)；errors＝[(lineno, msg)]；schema 不合的列不入 events。"""
    events, errors = [], []
    for lineno, e, errs in _parse_lines(text):
        if e is not None:
            events.append(e)
        errors.extend((lineno, m) for m in errs)
    return events, errors


def _sha_exists(ctx, sha, cwd=None):
    try:
        ctx.git("cat-file", "-e", f"{sha}^{{commit}}", cwd=cwd)
        return True
    except GitError:
        return False


def _erratum_view(rows):
    """套用 erratum：回 (viewed_rows, errs)；viewed_rows＝[(lineno, event 副本)]，target 列該欄以 corrected 覆寫。"""
    by_line = {ln: dict(e) for ln, e, _ in rows if e is not None}
    errs = []
    for ln, e, _ in rows:
        if e is None or e.get("type") != "erratum":
            continue
        t = by_line.get(e["target_line"])
        field = e["field"]
        ok = t is not None and (
            (field == "merge" and t.get("type") in ("feature_close", "misc") and "merge" in t)
            or (field.startswith("pins.") and t.get("type") == "feature_close")
            or (field == "commit" and t.get("type") == "perf" and "commit" in t)
        )
        if not ok:
            errs.append((ln, f"erratum target_line {e['target_line']} 無可更正之欄「{field}」（列不存在、型不符或該欄缺席）"))
            continue
        if field.startswith("pins."):
            t["pins"] = dict(t["pins"])
            t["pins"][field.split(".", 1)[1]] = e["corrected"]
        else:
            t[field] = e["corrected"]
    return sorted(by_line.items()), errs


def gt_02(ctx):
    """GATE:
      id=GT-02
      rule=RL-0055
      source=rev5:ADR 0012
      drift=事件帳形制、SHA 實證、pin↔worktree
      face=docs/ops/events.jsonl；外層 index gitlink；兩 worktree HEAD
      trigger=pre-commit
      rc=1
      breaks-if-removed=事件帳可寫入任意形、假 SHA 入帳不察、pin 漂移靜默
    """
    out = []
    text = ctx.text(EVENTS)
    if not text or not text.strip():
        return [finding(ERROR, "GT-02", EVENTS, "掃描面空集合：events.jsonl 缺席或空檔——創世 misc 事件必須存在")]
    rows = _parse_lines(text)
    for ln, _, errs in rows:
        for m in errs:
            out.append(finding(ERROR, "GT-02", f"{EVENTS}:{ln}", m))
    k = 0
    for ln, e, _ in rows:
        if e is not None and e.get("type") == "feature_close":
            k += 1
            if e["window"] != k:
                out.append(finding(ERROR, "GT-02", f"{EVENTS}:{ln}", f"window {e['window']} 須為本筆 feature_close 之序號 {k}"))
    viewed, verrs = _erratum_view(rows)
    for ln, m in verrs:
        out.append(finding(ERROR, "GT-02", f"{EVENTS}:{ln}", m))
    sub_present = {sub: ctx.exists(os.path.join(sub, ".git")) for _, sub in PIN_KEYS}
    for ln, e in viewed:
        where = f"{EVENTS}:{ln}"
        t = e.get("type")
        for field in ("merge", "commit", "corrected"):
            if field in e and t != "erratum" or (field == "corrected" and t == "erratum" and not e["field"].startswith("pins.")):
                if not _sha_exists(ctx, e[field]):
                    out.append(finding(ERROR, "GT-02", where, f"{field} {e[field][:12]} 外層 git 實證失敗（無此 commit）"))
        if t == "feature_close" or (t == "erratum" and e["field"].startswith("pins.")):
            pins = e["pins"] if t == "feature_close" else {e["field"].split(".", 1)[1]: e["corrected"]}
            for key, sub in PIN_KEYS:
                if key not in pins:
                    continue
                if not sub_present[sub]:
                    out.append(finding(SKIP, "GT-02", where, f"GT-02.submodule-absent：{sub} 不在工作樹、pins.{key} 未實證"))
                    continue
                if not _sha_exists(ctx, pins[key], cwd=os.path.join(ctx.root, sub)):
                    out.append(finding(ERROR, "GT-02", where, f"pins.{key} {pins[key][:12]} 於 {sub} 實證失敗（無此 commit）"))
    for key, sub in PIN_KEYS:
        if not sub_present[sub]:
            continue
        try:
            entry = ctx.git("ls-files", "-s", sub)
        except GitError:
            entry = ""
        parts = entry.split()
        gitlink = parts[1] if len(parts) >= 2 and parts[0] == "160000" else None
        if gitlink is None:
            out.append(finding(ERROR, "GT-02", sub, f"外層 index 無 {sub} 的 gitlink（pin 互證無基準）"))
            continue
        try:
            head = ctx.git("rev-parse", "HEAD", cwd=os.path.join(ctx.root, sub))
        except GitError:
            head = None
        if head != gitlink:
            out.append(finding(ERROR, "GT-02", sub, f"pin 漂移：外層 index gitlink {gitlink[:12]} ≠ {sub} HEAD {str(head)[:12]}（收尾序：子庫 commit 後 git add <子庫>）"))
    return out


def _adr_exists(ctx, adr_id):
    if any(p.startswith(f"{ADR_DIR}/{adr_id}-") for p in ctx.tracked):
        return True
    d = os.path.join(ctx.root, ADR_DIR)
    return os.path.isdir(d) and any(n.startswith(adr_id + "-") for n in os.listdir(d))


def gt_03(ctx):
    """GATE:
      id=GT-03
      rule=RL-0053
      source=rev5:ADR 0075
      drift=收刀與 review 事件完整性
      face=docs/ops/events.jsonl；specs/*/spec.md；docs/arc42/decisions；docs/reviews
      trigger=pre-commit
      rc=1
      breaks-if-removed=收刀可指向不存在的 spec／ADR／報告、分流引用斷鏈
    """
    out = []
    evs, _ = parse_events(ctx.text(EVENTS))
    closes = [e for e in evs if e["type"] in ("feature_close", "review")]
    if not closes:
        return [finding(ERROR, "GT-03", EVENTS, "掃描面空集合：零 feature_close／review 事件——文件創世驗收 review 事件必須存在")]
    for e in closes:
        if e["type"] == "feature_close":
            where = f"{EVENTS}｜{e['feature']}"
            spec = f"specs/{e['feature']}/spec.md"
            if not ctx.exists(spec):
                out.append(finding(ERROR, "GT-03", where, f"收刀事件指向的 {spec} 不存在"))
            for adr in e["adrs"]:
                if not _adr_exists(ctx, adr):
                    out.append(finding(ERROR, "GT-03", where, f"adrs 引用 {adr} 但 {ADR_DIR}/ 無對應檔"))
        else:
            where = f"{EVENTS}｜review {e['date']} {e['scope']}"
            if not ctx.exists(e["report"]):
                out.append(finding(ERROR, "GT-03", where, f"review 事件的 report {e['report']} 不存在"))
            for adr in e["findings"]["wontfix_adr"]:
                if not _adr_exists(ctx, adr):
                    out.append(finding(ERROR, "GT-03", where, f"wontfix_adr 引用 {adr} 但 {ADR_DIR}/ 無對應檔"))
    return out


def metrics(events, lessons, min_window=3):
    """§4.3 三指標：gov_ratio（全期）、lessons_dup_rate（全期）、backlog_net（最近 min_window 個 feature_close 自然窗）；空值一律 "n/a"。"""
    fcs = [e for e in events if e.get("type") == "feature_close"]
    gov = sum(1 for e in events if e.get("type") == "misc" and e.get("category") == "governance")
    out = {"gov_ratio": round(gov / len(fcs), 2) if fcs else "n/a"}
    out["lessons_dup_rate"] = round(sum(1 for l in lessons if l.get("recurrence_of")) / len(lessons), 2) if lessons else "n/a"
    if len(fcs) < min_window:
        out["backlog_net"] = "n/a"
        return out
    windows, cur = [], []
    for e in events:
        if e.get("type") not in ("feature_close", "misc"):
            continue
        cur.append(e)
        if e["type"] == "feature_close":
            windows.append(cur)
            cur = []
    net = 0
    for w in windows[-min_window:]:
        for e in w:
            net += len(e.get("backlog_add", []) or []) - len(e.get("backlog_done", []) or [])
    out["backlog_net"] = net
    return out
