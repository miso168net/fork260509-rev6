#!/usr/bin/env python3
"""PreToolUse(AskUserQuestion) 閘：送出前把工具參數與最新擬稿逐欄比對，不符 → 擋下（exit 2、stderr 指名欄位與首差字元碼位）。

來由（LL-00099）：出題參數偶發錯成鄰近碼位（例：「銜」送成「銃」），送出後解碼核對抓得到、但 user 已看到錯字；
「刻意直寫」之文字守法擋不住＝同根第三次以上再犯 → user 2026-10-23 裁定改由送出前比對擋下（008 刀 U0）。
擬稿＝repo 根下 gitignored 工作區（tmp）內、相對路徑含 `auq` 之 *.json 中 mtime 最新者；內容＝題目陣列（形同參數 questions）。
比對欄：題數；各題 header／question／multiSelect（缺＝false）／選項數；各選項 label／description／preview（缺＝無）。
無擬稿或擬稿讀不成題目陣列 → 擋（先寫擬稿再送）；stdin 非 JSON、或參數無 questions → 放行（fail-open：本閘是兜底、非唯一防線）。
擬稿本身之錯字（含簡體字）不在射程：擬稿仍須自核。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, "tmp")
MISSING = object()
CTX = 8          # 首差字元前後各取幾字作上下文
MAX_LINES = 20   # stderr 最多逐欄列幾筆（其餘只報筆數）


def latest_draft():
    found = []
    for dirpath, _dirs, files in os.walk(WORK):
        for fn in files:
            path = os.path.join(dirpath, fn)
            if fn.endswith(".json") and "auq" in os.path.relpath(path, WORK):
                try:
                    found.append((os.path.getmtime(path), path))
                except OSError:
                    continue
    return max(found)[1] if found else None


def fields(qs):
    """題目陣列攤平成 [(欄名, 值)]；題數與選項數亦入欄，結構差異同樣逐欄報。"""
    out = [("題數", len(qs))]
    for n, q in enumerate(qs, 1):
        opts = q.get("options") or []
        out += [(f"q{n}.header", q.get("header")), (f"q{n}.question", q.get("question")),
                (f"q{n}.multiSelect", bool(q.get("multiSelect", False))), (f"q{n}.選項數", len(opts))]
        for i, o in enumerate(opts, 1):
            out += [(f"q{n}.opt{i}.{k}", o.get(k)) for k in ("label", "description", "preview")]
    return out


def show(v):
    if v is MISSING:
        return "無此欄"
    if v is None:
        return "無"
    if isinstance(v, str):
        s = v.replace("\n", "⏎")
        return f"「{s[:30]}{'…' if len(s) > 30 else ''}」（{len(v)} 字）"
    return repr(v)


def describe(a, b):
    """兩側皆字串＝首差字元位置、兩側碼位與上下文；其餘＝兩側值。"""
    if not (isinstance(a, str) and isinstance(b, str)):
        return f"擬稿 {show(a)}｜送出 {show(b)}"
    k = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))

    def at(s):
        if k >= len(s):
            return "（已到字尾）"
        c = s[k]
        frag = s[max(0, k - CTX):k + CTX + 1].replace("\n", "⏎")
        return f"U+{ord(c):04X}{'「' + c + '」' if c.isprintable() else ''}　…{frag}…"
    return f"第 {k + 1} 字起不同｜擬稿 {at(a)}｜送出 {at(b)}"


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    sent = (data.get("tool_input") or {}).get("questions")
    if not isinstance(sent, list) or not sent:
        return 0
    try:
        got = dict(fields(sent))
    except Exception:
        return 0
    path = latest_draft()
    if path is None:
        sys.stderr.write(
            "[pre-auq-draft-gate] 找不到擬稿：每題送出前先把題目陣列（形同本工具參數 questions）寫成 JSON，"
            "存於 repo 根下工作區 tmp 內、相對路徑含 auq 之 .json（取 mtime 最新者比對）；寫完再送。"
        )
        return 2
    rel = os.path.relpath(path, ROOT)
    try:
        with open(path, encoding="utf-8") as f:
            want = dict(fields(json.load(f)))
    except Exception as ex:
        sys.stderr.write(f"[pre-auq-draft-gate] 擬稿 {rel} 讀不成題目陣列（{type(ex).__name__}: {ex}）——改正擬稿後再送。")
        return 2
    diffs = [(k, want.get(k, MISSING), got.get(k, MISSING)) for k in dict.fromkeys([*want, *got])
             if want.get(k, MISSING) != got.get(k, MISSING)]
    if not diffs:
        return 0
    lines = [f"- {k}：{describe(a, b)}" for k, a, b in diffs[:MAX_LINES]]
    if len(diffs) > MAX_LINES:
        lines.append(f"- …另 {len(diffs) - MAX_LINES} 欄")
    sys.stderr.write(
        f"[pre-auq-draft-gate] AskUserQuestion 參數與擬稿 {rel} 不符 {len(diffs)} 欄——依擬稿逐字改正參數後重送"
        "（擬稿本身有誤＝先改擬稿再送）：\n" + "\n".join(lines)
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
