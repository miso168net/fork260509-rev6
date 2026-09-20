"""守 RL-0055：事件帳逐型 schema 與 SHA 實證；收刀與 review 事件完整性、BL 引用存在性。

events.py：parse_events（jsonl、行界只認 \\n）、EVENT_SCHEMAS（rev6 欄位：五碼 ID、feature_close.window、misc.category）、
gt_02（schema／SHA 實證／pin 互證／window 序號）、gt_03（specs／ADR／report 存在＋BL 引用存在性）、metrics（§4.3 三指標＋ADR-00021 檢索性第四指標）。
"""
import json
import os
import re

from . import EVENTS, ADR_DIR, BACKLOG, BACKLOG_DEFERRED
from .common import ERROR, WARN, SKIP, finding, GitError

RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_FEATURE = re.compile(r"^\d{3}-[a-z0-9][a-z0-9-]*$")
RE_SHA = re.compile(r"^[0-9a-f]{40}$")
RE_SECTION = re.compile(r"^§\d{1,2}$")
RE_ADR = re.compile(r"^ADR-\d{5}$")
RE_BID = re.compile(r"^BL-\d{5}$")
SUMMARY_CHAR_LIMIT = 300
PIN_KEYS = (("web", "base-web"), ("api", "rust-api"))
PERF_KINDS = ("close_bookkeeping", "precommit_chain")
ERRATUM_FIELDS = ("merge", "pins.web", "pins.api", "commit", "adrs", "probe")
ERRATUM_SHA_FIELDS = ("merge", "pins.web", "pins.api", "commit")   # 其餘欄之 corrected 依欄別分型
CATEGORIES = ("product", "governance")
# review.report 形（RL-0073 承載處①②）：舊形只驗 endswith(".md")、訊息卻宣稱完整路徑形（000-r2 L3-09）
RE_REPORT = re.compile(r"^docs/reviews/\d{8}-[a-z0-9][a-z0-9-]*\.md$")
PROBE_KEYS = ("questions", "found", "detour", "not_found", "wrong", "avg_min_hops")   # ADR-00021：review 事件 probe 欄（冷啟動探針一組；negative＝否定對照題同形、可缺席）

EVENT_SCHEMAS = {
    "feature_close": {
        "required": ("type", "date", "feature", "summary", "merge", "pins", "adrs", "arch_impact",
                     "backlog_add", "backlog_done", "window"),
        "optional": ("notes", "kind", "spec_supersessions"),
    },
    "misc": {
        "required": ("type", "date", "summary", "category", "backlog_add"),
        "optional": ("notes", "backlog_done", "merge", "workflow", "adrs"),
    },
    "review": {
        "required": ("type", "date", "scope", "report", "findings"),
        "optional": ("feature", "notes", "probe"),
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


def _check_probe(p, label="probe"):
    """ADR-00021 probe 欄形檢：鍵集固定、四計數守恆＝questions、avg_min_hops 非負數；negative（否定對照題）同形且不再巢套。只存計數、比例由 metrics 現算。"""
    if not isinstance(p, dict):
        return [f"{label} 須為物件 {{questions, found, detour, not_found, wrong, avg_min_hops[, negative]}}"]
    extra = set(p) - set(PROBE_KEYS) - ({"negative"} if label == "probe" else set())
    missing = set(PROBE_KEYS) - set(p)
    if extra or missing:
        return [f"{label} 鍵集須為 {'/'.join(PROBE_KEYS)}" + ("（另可帶 negative）" if label == "probe" else "") + f"：多 {sorted(extra)}、缺 {sorted(missing)}"]
    errs = []
    counts = [p[k] for k in PROBE_KEYS[:5]]
    if not all(_is_int(v) and v >= 0 for v in counts) or p["questions"] < 1:
        errs.append(f"{label} 計數須為非負整數且 questions ≥1")
    elif sum(counts[1:]) != counts[0]:
        errs.append(f"{label} 四值不守恆：found＋detour＋not_found＋wrong 須＝questions")
    h = p["avg_min_hops"]
    if not (isinstance(h, (int, float)) and not isinstance(h, bool) and h >= 0):
        errs.append(f"{label}.avg_min_hops 須為非負數（grader 最短 hops 平均）")
    if "negative" in p:
        errs += _check_probe(p["negative"], "probe.negative")
    return errs


def notes_gt06_risks(text):
    """notes 全文會原樣進 MILESTONES 附錄（BL-00005 拍板：不截斷不轉義），因而落入 GT-06 掃描面
    （face＝全部 tracked md、含 GENERATED_FILES）。事件源 append-only、寫進去即無乾淨補救——故在**真源側**先擋（BL-00013）。
    四腿正則自 `book.py` 取用、不另抄一份（判準單一家）。回錯誤訊息 list。"""
    from . import book as book_mod
    errs = []
    for m in book_mod.RE_LINENO.finditer(text):
        errs.append(f"notes 含行號形引用「{m.group(0)}」——會讓 MILESTONES 觸 GT-06；改用節名或整檔")
    for m in book_mod.RE_DEEP.finditer(text):
        errs.append(f"notes 含帳本 deep-link「{m.group(0)}」——BACKLOG／NOTES／STATE 只可整檔引用")
    for m in book_mod.RE_HOME.finditer(text):
        errs.append(f"notes 含 per-machine 路徑「{m.group(0)}」——repo 文件不引用本機 .claude 路徑")
    for m in book_mod.LINK.finditer(text):
        t = m.group(1)
        if not t.startswith(("http://", "https://", "mailto:", "#")):
            errs.append(f"notes 含相對 markdown 連結「{t}」——渲染後基準為 docs/generated/、GT-06 連結腿必紅；改寫成純路徑文字")
    return errs


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
    if isinstance(e.get("notes"), str):
        errs += notes_gt06_risks(e["notes"])
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
        if "adrs" in e and not _id_list_ok(e["adrs"], RE_ADR):
            errs.append("adrs 須為 ADR-NNNNN 字串 list（收單即立 ADR 的維護批用；DECISIONS-INDEX 反查左源）")
    elif etype == "review":
        if not (isinstance(e["scope"], str) and e["scope"].strip()):
            errs.append("scope 須為非空字串")
        if not (isinstance(e["report"], str) and RE_REPORT.fullmatch(e["report"])):
            errs.append(f"report 須為 docs/reviews/YYYYMMDD-<scope>.md：{e['report']!r}")
        if "feature" in e and not RE_FEATURE.fullmatch(str(e["feature"])):
            errs.append(f"feature 格式須為 NNN-slug：{e['feature']!r}")
        fd = e["findings"]
        if not (isinstance(fd, dict) and set(fd) == {"total", "fixed", "to_backlog", "wontfix_adr"}
                and _is_int(fd.get("total")) and fd["total"] >= 0 and _is_int(fd.get("fixed")) and fd["fixed"] >= 0
                and _id_list_ok(fd.get("to_backlog"), RE_BID) and _id_list_ok(fd.get("wontfix_adr"), RE_ADR)):
            errs.append("findings 須為 {total≥0, fixed≥0, to_backlog[BL-NNNNN…], wontfix_adr[ADR-NNNNN…]}")
        elif fd["fixed"] + len(fd["to_backlog"]) + len(fd["wontfix_adr"]) != fd["total"]:
            errs.append("findings 分流不守恆：fixed＋len(to_backlog)＋len(wontfix_adr) 須＝total")
        if "probe" in e:
            errs += _check_probe(e["probe"])
    elif etype == "erratum":
        if not (_is_int(e["target_line"]) and e["target_line"] >= 1):
            errs.append(f"target_line 須為正整數（events.jsonl 行號）：{e['target_line']!r}")
        if e["field"] not in ERRATUM_FIELDS:
            errs.append(f"field 須為 {'/'.join(ERRATUM_FIELDS)} 之一：{e['field']!r}")
        if e["field"] in ERRATUM_SHA_FIELDS:
            if not (isinstance(e["corrected"], str) and RE_SHA.fullmatch(e["corrected"])):
                errs.append(f"corrected 須為 40 位 hex SHA：{e['corrected']!r}")
        elif e["field"] == "adrs":
            if not _id_list_ok(e["corrected"], RE_ADR):
                errs.append("field=adrs 之 corrected 須為 ADR-NNNNN 字串 list")
        elif e["field"] == "probe":
            errs += _check_probe(e["corrected"])
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


def events_view(text):
    """人讀面用的**更正後視圖**（BL-00004／000-r1 R1-003）：事件源 append-only、原列永不改；
    本函式把每筆 erratum 的 `corrected` 套到 `target_line` 指向那列的 `field` 上，回 (events, errors)。
    `pins.web`／`pins.api` 寫進巢狀 `pins` 子鍵；套不上（行號越界、該列非事件、欄不在該型 schema）＝回一筆 error、不靜默。
    ★渲染面（MILESTONES／perf／STATE／DECISIONS-INDEX）一律吃本視圖；驗證面吃 parse_events 原值。"""
    rows = list(_parse_lines(text))
    by_line = {ln: e for ln, e, _ in rows if e is not None}
    events = [e for _, e, _ in rows if e is not None]
    errors = [(ln, m) for ln, _, errs in rows for m in errs]
    import copy
    view = copy.deepcopy(events)
    idx = {id(o): v for o, v in zip(events, view)}
    for ln, e, _ in rows:
        if e is None or e.get("type") != "erratum":
            continue
        tgt = by_line.get(e["target_line"])
        if tgt is None:
            errors.append((ln, f"erratum target_line {e['target_line']} 不指向任何合法事件列"))
            continue
        v, f = idx[id(tgt)], e["field"]
        allowed = EVENT_SCHEMAS[tgt["type"]]
        if f.split(".")[0] not in set(allowed["required"]) | set(allowed["optional"]):
            errors.append((ln, f"erratum 欄「{f}」不在 {tgt['type']} 事件的欄集"))
            continue
        if "." in f:
            top, sub = f.split(".", 1)
            v.setdefault(top, {})[sub] = e["corrected"]
        else:
            v[f] = e["corrected"]
    return view, errors


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
            # adrs：補「當時 schema 尚無此欄」的漏記，故不要求該欄已在（BL-00004）
            or (field == "adrs" and t.get("type") in ("feature_close", "misc"))
            # probe：同理——ADR-00021 前的 review 事件無此欄、回填以 erratum 補（000-r1）
            or (field == "probe" and t.get("type") == "review")
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


def _append_only_leg(ctx, text):
    """BL-00035②：events.jsonl 自稱 append 型單一事實源，但既有列可被靜默改寫——erratum 機制
    （更正只能新增一筆 erratum、不得回頭改）的整個前提在機器面原本零守。
    形制承 GT-04 的 HEAD 對比腿：HEAD 版須為現版的逐行前綴，只准在尾端新增。
    檔尚未入 HEAD（創世首顆、或該檔剛被建）＝無可對比、不報。"""
    head = ctx.head_text(EVENTS)
    if head is None:
        return []
    hl = head.rstrip("\n").split("\n")
    cl = text.rstrip("\n").split("\n")
    if len(cl) < len(hl):
        return [finding(ERROR, "GT-02", EVENTS,
                        f"append-only 違反：HEAD 版 {len(hl)} 列、現版 {len(cl)} 列＝既有列被刪"
                        "——本帳只准尾端新增，更正一律 append 一筆 erratum 事件")]
    for i, (h, c) in enumerate(zip(hl, cl), 1):
        if h != c:
            return [finding(ERROR, "GT-02", f"{EVENTS}:{i}",
                            f"append-only 違反：第 {i} 列與 HEAD 版不同——本帳既有列不得改寫"
                            "（erratum 機制的前提），更正一律 append 一筆 erratum 事件")]
    return []


def gt_02(ctx):
    """GATE:
      id=GT-02
      rule=RL-0055
      source=rev5:ADR 0012
      drift=事件帳形制、SHA 實證、pin↔worktree、既有列被改寫
      face=docs/ops/events.jsonl；外層 index gitlink；兩 worktree HEAD
      trigger=pre-commit
      rc=1
      breaks-if-removed=事件帳可寫入任意形、假 SHA 入帳不察、pin 漂移靜默、既有列可被靜默改寫（erratum 機制前提失守）
    """
    out = []
    text = ctx.text(EVENTS)
    if not text or not text.strip():
        return [finding(ERROR, "GT-02", EVENTS, "掃描面空集合：events.jsonl 缺席或空檔——創世 misc 事件必須存在")]
    out += _append_only_leg(ctx, text)
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
            if field in e and t != "erratum" or (field == "corrected" and t == "erratum"
                                                 and e["field"] in ERRATUM_SHA_FIELDS and not e["field"].startswith("pins.")):
                if not _sha_exists(ctx, e[field]):
                    out.append(finding(ERROR, "GT-02", where, f"{field} {e[field][:12]} 外層 git 實證失敗（無此 commit）"))
        if t == "feature_close" or (t == "erratum" and e["field"].startswith("pins.")):
            pins = e["pins"] if t == "feature_close" else {e["field"].split(".", 1)[1]: e["corrected"]}
            for key, sub in PIN_KEYS:
                if key not in pins:
                    continue
                if not sub_present[sub]:
                    out.append(finding(SKIP, "GT-02", where, f"⤳ 跳過：{sub} 不在工作樹（命中謂詞＝{sub}/.git 不存在；GT-02.submodule-absent）"
                                                       f"——pins.{key} 未實證；ADR-00019 環境缺席具名跳過 rc 0"))
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


BL_LEDGERS = (BACKLOG, BACKLOG_DEFERRED)
_BL_UNBORN = ("{bid} 未經事件 backlog_add 誕生（來源：{src}）——BL 只經事件誕生"
              "（啟動書 §4.3 淨流量前提；ADR-00025 記 ADR 方向刻意不同形）")
_BL_INFLIGHT = ("{bid} 已在帳本但事件尚無 backlog_add（來源：{src}）——在途落帳窗口："
                "配號已發、收單事件補上 backlog_add 即消（簿記排在 merge 之後＝RL-0053）")


def _bl_num(bid):
    return int(bid.rsplit("-", 1)[1])


def _bl_born(events):
    """S＝全部事件 backlog_add 之 BL 號聯集（誕生集）。"""
    born = set()
    for e in events:
        for b in e.get("backlog_add") or []:
            born.add(b)
    return born


def _bl_existence(ctx, evs):
    """BL-00003①：事件側（backlog_done、review.findings.to_backlog）與帳本兩卷之每個 BL 號皆須 ∈ 誕生集。
    ★帳本側與 review.findings.to_backlog 側分兩態：號 ≤ max(誕生集)＝憑空號或回收號、ERROR；號 > max(誕生集)＝配號已發而收單尚未落帳的
    在途窗口、WARN（一輪之內帳本先 append、事件於收單才寫，兩者恆有時間差；把在途也判 ERROR 會讓該輪
    自身的收尾 commit 全被 pre-commit 擋死）。ADR 方向刻意不設同型反向不變式＝ADR-00025。

    ★★此兩態＝**偏離 000-r2 §4.7 條文 A**（該條文只寫「帳本列號 ∉ S 即 ERROR」、且期望「現帳零 finding」）。
    偏離理由與殘留破口已於本輪 fix 第 1 輪升級主線、待裁定（改條文／立 ADR／改回單態三擇一）：
      · 理由：條文 A 與 RL-0053（簿記排在 merge 之後）在同一輪內互斥——本輪自身的 BL-00035～00042 由
        BACKLOG append 先落地、其 backlog_add 要到收單事件才寫，單態 ERROR 會讓本輪收尾 commit 全被擋死。
      · 殘留破口（窄但真實）：落在 (max(誕生集), 帳本 next-id) 半開區間的憑空號／打錯號只出 WARN、不擋
        commit；該區間**之外**由 GT-05 的 next 單調腿接手（號 ≥ next 即 ERROR）。條文 A 明令「不讀 git 史」，
        故在該區間內「在途」與「打錯」在機器面不可分——破口不可再收窄，只能靠改條文或放行讀史消除。"""
    born = _bl_born(evs)
    top = max((_bl_num(b) for b in born), default=0)
    out = []
    for e in evs:
        where = f"{EVENTS}｜{e.get('date')}｜{e.get('type')}"
        for b in e.get("backlog_done") or []:
            if b not in born:
                out.append(finding(ERROR, "GT-03", where, "GT-03：" + _BL_UNBORN.format(bid=b, src="backlog_done")))
        if e.get("type") == "review":
            rw = f"{EVENTS}｜review {e.get('date')} {e.get('scope')}"
            for b in (e.get("findings") or {}).get("to_backlog") or []:
                if b in born:
                    continue
                # to_backlog＝該輪的分流結果，其誕生事件（收單 misc 之 backlog_add）依 RL-0053 排在 merge 之後、
                # 與 review 事件同輪但更晚；故與帳本側同判兩態，不然 review 事件一 append 就把自己的收尾擋死。
                # backlog_done 不適用（收掉一個從未誕生的號恆為錯），維持單態 ERROR。
                if _bl_num(b) <= top:
                    out.append(finding(ERROR, "GT-03", rw, "GT-03：" + _BL_UNBORN.format(bid=b, src="findings.to_backlog")))
                else:
                    out.append(finding(WARN, "GT-03", rw, "GT-03：" + _BL_INFLIGHT.format(bid=b, src="findings.to_backlog")))
    from . import book as book_mod   # 帳本列形＝家族真源（判準單一家、不另抄一份正則）
    for rel in BL_LEDGERS:
        text = ctx.text(rel)
        if text is None:
            continue
        for i, line in enumerate(text.split("\n"), 1):
            m = book_mod.RE_ENTRY["BL"].match(line)
            if m is None or m.group(1) in born:
                continue
            bid, src = m.group(1), f"{rel}:{i}"
            if _bl_num(bid) <= top:
                out.append(finding(ERROR, "GT-03", src, "GT-03：" + _BL_UNBORN.format(bid=bid, src=rel)))
            else:
                out.append(finding(WARN, "GT-03", src, "GT-03：" + _BL_INFLIGHT.format(bid=bid, src=rel)))
    return out


def gt_03(ctx):
    """GATE:
      id=GT-03
      rule=RL-0055
      source=rev5:ADR 0075
      drift=收刀與 review 事件完整性、BL 引用存在性、無效事件被續判
      face=docs/ops/events.jsonl；specs/*/spec.md；docs/arc42/decisions；docs/reviews；docs/ops/BACKLOG.md；docs/ops/BACKLOG-DEFERRED.md
      trigger=pre-commit
      rc=1
      breaks-if-removed=收刀可指向不存在的 spec／ADR／報告、分流引用斷鏈、BL 號可憑空出現、無效事件觸發整片假在途
    """
    out = []
    evs, perrs = parse_events(ctx.text(EVENTS))
    if perrs:
        # BL-00035④：無效列被 parse_events 丟棄⇒下游對「不存在的事件」續判會產生整片假報
        # （003 刀簿記實證：summary 超 300 字使整筆無效、GT-03 隨之假報在途 27 筆）。
        # 指名該筆、當場中止；根因由 GT-02 的 schema 腿逐筆報。
        lns = "／".join(str(ln) for ln, _ in perrs[:5])
        more = f"（另 {len(perrs) - 5} 筆）" if len(perrs) > 5 else ""
        return [finding(ERROR, "GT-03", f"{EVENTS}:{perrs[0][0]}",
                        f"下游判讀中止：第 {lns} 列未過 schema{more}（逐筆原因見 GT-02）"
                        "——無效事件不入帳，對其續作在途／完整性判讀＝整片假報；先修該筆再看本閘")]
    out += _bl_existence(ctx, evs)
    closes = [e for e in evs if e["type"] in ("feature_close", "review")]
    if not closes:
        out.append(finding(ERROR, "GT-03", EVENTS, "掃描面空集合：零 feature_close／review 事件——文件創世驗收 review 事件必須存在"))
        return out
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


def _probe_retrieval(events):
    """ADR-00021：最近一筆帶 probe 的 review 事件→{scope, le3_ratio（found/questions＝≤3 跳且答對）, hit_ratio（(found＋detour)/questions）, not_found, wrong,
    avg_min_hops（grader 最短 hops 平均；000-r2 L1-05 前該鍵受形檢卻無渲染面）, negative_wrong（否定對照題答錯；缺席＝"—"）}；無＝"n/a"。"""
    for e in reversed(events):
        p = e.get("probe") if e.get("type") == "review" else None
        if isinstance(p, dict) and not _check_probe(p):
            q, neg = p["questions"], p.get("negative")
            return {"scope": e["scope"], "le3_ratio": round(p["found"] / q, 2), "hit_ratio": round((p["found"] + p["detour"]) / q, 2),
                    "not_found": p["not_found"], "wrong": p["wrong"], "avg_min_hops": p["avg_min_hops"],
                    "negative_wrong": neg["wrong"] if neg else "—"}
    return "n/a"


def metrics(events, lessons, min_window=3):
    """§4.3 三指標＋ADR-00021 檢索性：gov_ratio（全期）、lessons_dup_rate（全期）、backlog_net（最近 min_window 個 feature_close 自然窗）、
    probe_retrieval（最近一筆帶 probe 之 review 事件、比例自計數現算）；空值一律 "n/a"。"""
    fcs = [e for e in events if e.get("type") == "feature_close"]
    gov = sum(1 for e in events if e.get("type") == "misc" and e.get("category") == "governance")
    out = {"gov_ratio": round(gov / len(fcs), 2) if fcs else "n/a", "probe_retrieval": _probe_retrieval(events)}
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
