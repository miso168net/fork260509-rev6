#!/usr/bin/env python3
"""msg key 跨端閘（003 刀 U9；spec FR-027、contracts/code-gates.md §2、research R9；碼面閘＝RUNBOOK §12 碼面閘表列、GT-12 腿對賬）。

用法：
  python3 tools/msg-key-gate.py [check] [--rust <error.rs>] [--locales <dir>] [--src <dir>]   左源 ⇔ 三檔 backend 子樹逐檔雙向全等＋Biz 構造點守衛＋前端 msg 字面消費點名冊
  python3 tools/msg-key-gate.py test                                                           離線 self-test（契約七案＋判準補強三案＋真 repo 左源綠案＋斷言 3 八案；零 docker）
左源（`--rust`，預設 rust-api/server/src/error.rs）兩段解析——實碼形＝常數表＋常數引用陣列、零第二份字面：
  ①`pub mod msg_key { pub const NAME: &str = "字面"; … }` 建 名稱→字面 映射；
  ②`pub const MSG_KEYS: [&str; N] = [ msg_key::NAME, … ];` 逐元素經映射解回字面（亦容直寫 "字面"）；元素數≠N、任一元素解不出（含常數表缺該名）＝rc 2。
右源（`--locales`，預設 base-web/src/locales/langs）＝ en-us.ts／zh-cn.ts／zh-tw.ts 各自的 `backend: {` 區塊：錨＝獨佔一行（允許前置空白）、
  brace 配對取塊；剝 `//`／`/* */` 註解與字串值後，巢狀鍵以 `.` 串接攤平（`backend.common.success` ⇒ `common.success`）。
斷言 1：三檔各自 set(backend) == set(MSG_KEYS)（逐檔、雙向）；不等＝rc 1、逐檔指名「缺：…」「多：…」。
斷言 2（Biz 構造點守衛）：`<error.rs 所在目錄>/**/*.rs` 生產區間——`#[cfg(test)]` 所附項目（mod／impl／fn…）以 brace 配對整段排除——
  每處 `AppError::Biz(` MUST 緊接 `Cow::Borrowed(` 且引數為 ①字串字面 或 ②`msg_key::NAME`（經映射解回），解出之鍵 ∈ MSG_KEYS；
  動態構造（變數／`format!`／函式回傳）＝rc 1 指名檔:行。match 樣式（`AppError::Biz(_) =>`／`AppError::Biz(k) =>`／`… if`／`= …`）
  非構造、不計。生產區間內 Biz 構造點零處＝比對面為空（rc 2）——排除過度或掃描根有誤時不得回綠。
斷言 3（前端 msg 字面消費點名冊；BL-00063）：`--src`（預設 base-web/src）下 `*.ts`／`*.vue`／`*.tsx`（排除頂層 `locales/`）剝註解（`//`、
  `/* */` 含 JSDoc；`.vue` 之 `<script>` 塊外只剝 `<!-- -->`；再同步判準＝`<script>` 開標籤認引號屬性、`'`／`"` 字串不跨行、regex literal
  整段跳過——引號配對錯位即註解與字串整塊互換、假紅假綠皆有）後之字串字面，凡 ①恰等於 MSG_KEYS 成員、或 ②為 wire 形（`.` 串接之識別字段）
  且首段 ∈ 安全前綴者＝消費點。安全前綴不寫死＝MSG_KEYS 頂層前綴集 − 三檔 locale 之 backend 同層兄弟鍵集（程式現算：前端 i18n 已用之頂層
  命名空間不當 wire 形判）。實掃 {(檔, 鍵): 次數} 須與本檔 `FRONTEND_MSG_CONSUMERS` 名冊逐項雙向全等且每鍵 ∈ MSG_KEYS——未登記、名冊項
  消失、次數不等、鍵不在 MSG_KEYS＝rc 1 指名檔:行；掃描根缺席或零源檔＝比對面為空（rc 2）。動態拼接（`'biz.auth.' + x`、含 `${…}` 之
  模板字面）不成 wire 形字面、不在射程；★反引號模板不解析 `${…}` 內之巢狀模板——巢狀內層含 `//` 時，內層反引號被當外層收尾、其後
  `//` 被當行註解遮到行尾，同行其後之真消費點漏計（射程外已知態）。
退出碼：0 綠／1 違規（鍵集不等、動態 Biz 構造、解出鍵不在名冊、前端消費點與名冊不等）／2 結構異常（檔缺席、常數表或 MSG_KEYS 解析失敗、
  backend 節缺席或 brace 不配對、比對面為空〔含斷言 3 掃描根缺席或零源檔〕；self-test 案敗亦 2）／64 用法錯。
依賴：Python 3 標準庫、零 docker。接線：pre-commit `msg-key-gate` 段（staged 含 rust-api／base-web pin bump 或本檔即跑 `check`）、
  pre-commit `for t in …` 自測迴圈與 bootstrap `run_tool_test`（`test`）、README 樹、RUNBOOK §12 碼面閘表。
"""
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RUST = os.path.join("rust-api", "server", "src", "error.rs")
DEFAULT_LOCALES = os.path.join("base-web", "src", "locales", "langs")
LOCALE_FILES = ("en-us.ts", "zh-cn.ts", "zh-tw.ts")
DEFAULT_SRC = os.path.join("base-web", "src")
FRONTEND_EXTS = (".ts", ".vue", ".tsx")
FRONTEND_EXCLUDE = "locales"
TAG = "[msg-key-gate]"
USAGE = "用法：tools/msg-key-gate.py [check|test] [--rust <error.rs>] [--locales <dir>] [--src <dir>]"
RC_OK, RC_VIOLATION, RC_STRUCT, RC_USAGE = 0, 1, 2, 64

RE_CONST = re.compile(r'pub const (\w+): &str = "([^"]+)";')
RE_MSG_KEYS = re.compile(r"pub const MSG_KEYS:\s*\[&str;\s*(\d+)\]\s*=\s*\[(.*?)\];", re.S)
RE_ELEM_CONST = re.compile(r"^msg_key::(\w+)$")
RE_ELEM_LIT = re.compile(r'^"([^"]+)"$')
RE_BACKEND_ANCHOR = re.compile(r"^[ \t]*backend:[ \t]*\{[ \t]*$", re.M)
RE_TS_KEY = re.compile(r"(?<![\w$])([A-Za-z_$][\w$]*)[ \t]*:(?!:)")
RE_BIZ = re.compile(r"AppError::Biz\(")
RE_BORROWED = re.compile(r'^\s*Cow::Borrowed\(\s*(?:"([^"]+)"|msg_key::(\w+))\s*\)\s*$')
RE_CFG_TEST = re.compile(r"#\[cfg\(test\)\]")
RE_RAW_STR = re.compile(r'r(#*)"')
RE_WIRE_LITERAL = re.compile(r"(['\"`])([A-Za-z_$][\w$]*(?:\.[\w$]+)+)\1")
# 開標籤認引號屬性：屬性值內之 `>`（如 `generic="T extends Record<string, unknown>"`）不收尾。
RE_SCRIPT_OPEN = re.compile(r"""<script\b(?:[^>"']|"[^"]*"|'[^']*')*>""", re.I)
# regex literal 語境（斷言 3 視圖）：`/` 前一個有效碼字元屬此集（"" 為檔首、"=>" 為箭頭）或前一詞屬關鍵字時，`/` 起 regex 而非除號。
# `)`／`]`／`}`／識別字／數字後照除號；`<`／`>` 不納（tsx 之 `</span>` 不得誤判成 regex）。
TS_REGEX_PREV = frozenset(["", "=>", *"(,=:[!&|?{;+-*%~^"])
TS_REGEX_PREV_WORDS = frozenset(["return", "typeof", "case", "do", "else", "in", "of", "new", "delete", "void", "throw",
                                 "instanceof", "yield", "await"])

# 斷言 3 名冊：前端 msg 字面消費點——(檔＝相對 base-web/src 之 `/` 路徑, 鍵) → 剝註解後之出現次數。
# 新增、改寫或移除消費點（含後端鍵改名）須同批改本表；逐項附其消費語意。
FRONTEND_MSG_CONSUMERS = {
    # 登入軟區判斷：同碼 2222 之拒因只靠 msg 分，收到本鍵即顯驗證碼欄並取題（003 刀 U8）
    ("views/_builtin/login/modules/pwd-login.vue", "biz.auth.captchaRequired"): 1,
}


class StructuralError(Exception):
    """結構異常（rc 2）：訊息即輸出行。"""


# ─── 視圖：同長度遮罩（行號與位移存活）───

def _mask(seg):
    return "".join(c if c == "\n" else " " for c in seg)


def blank_view(text, ts, strings):
    """回與 `text` 同長度的字串：`//`／`/* */` 註解整段遮成空白（換行保留）；`strings=True` 時字串常值內容亦遮、引號保留。
    rust（`ts=False`）另認 raw string（`r#"…"#`、`br"…"`）與字元常值（`'a'`／`'\\n'`；lifetime／label 不誤判）；
    ts（`ts=True`）認 `'…'`／`"…"`／`` `…` `` 三種引號。★遮字串的用途＝brace 配對與錨定位（常值內的 `{`／`//` 不得騙過結構掃描）；
    讀字面（msg key）時另取只遮註解的視圖，兩視圖等長、位移互通。"""
    out, i, n = [], 0, len(text)
    while i < n:
        c, two = text[i], text[i:i + 2]
        if two == "//":
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(_mask(text[i:j]))
            i = j
            continue
        if two == "/*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(_mask(text[i:j]))
            i = j
            continue
        if not ts and c == "r":
            m = RE_RAW_STR.match(text, i)
            prev_ident = i > 0 and (text[i - 1].isalnum() or text[i - 1] == "_") and text[i - 1] != "b"
            if m and not prev_ident:
                close = '"' + m.group(1)
                j = text.find(close, m.end())
                j = n if j < 0 else j + len(close)
                out.append(_mask(text[i:j]) if strings else text[i:j])
                i = j
                continue
        if c == '"' or (ts and c in "'`"):
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
            out.append(c + _mask(text[i + 1:j - 1]) + text[j - 1:j] if strings else text[i:j])
            i = j
            continue
        if not ts and c == "'" and i + 2 < n and (text[i + 2] == "'" or text[i + 1] == "\\"):
            j = i + 3 if text[i + 1] == "\\" and text[i + 2] == "'" else i + 2
            k = text.find("'", j)
            k = n if k < 0 else k + 1
            out.append(text[i:k] if not strings else "'" + _mask(text[i + 1:k - 1]) + "'")
            i = k
            continue
        out.append(c)
        i += 1
    return "".join(out)


def match_brace(view, open_idx):
    """自 `open_idx`（指向 `{`）配對到對應 `}`、回其索引；不配對回 -1。"""
    depth = 0
    for j in range(open_idx, len(view)):
        if view[j] == "{":
            depth += 1
        elif view[j] == "}":
            depth -= 1
            if depth == 0:
                return j
    return -1


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


# ─── 左源 ───

def parse_left(text):
    """error.rs 文字 → (常數表 dict, MSG_KEYS 字面 list)；解不出即 StructuralError。"""
    bv = blank_view(text, ts=False, strings=True)
    cv = blank_view(text, ts=False, strings=False)
    m = re.search(r"pub mod msg_key\s*\{", bv)
    if not m:
        raise StructuralError("左源缺 `pub mod msg_key { … }` 常數表")
    end = match_brace(bv, m.end() - 1)
    if end < 0:
        raise StructuralError("左源 `pub mod msg_key` brace 不配對")
    const_map = dict(RE_CONST.findall(cv[m.end():end]))
    if not const_map:
        raise StructuralError("左源常數表零常數（`pub const NAME: &str = \"字面\";` 一條都沒有）")
    mk = RE_MSG_KEYS.search(cv)
    if not mk:
        raise StructuralError("左源缺 `pub const MSG_KEYS: [&str; N] = [ … ];` 陣列")
    declared = int(mk.group(1))
    elems = [e.strip() for e in mk.group(2).split(",")]
    elems = [e for e in elems if e]
    keys = []
    for e in elems:
        mc, ml = RE_ELEM_CONST.match(e), RE_ELEM_LIT.match(e)
        if mc:
            if mc.group(1) not in const_map:
                raise StructuralError(f"MSG_KEYS 元素 `msg_key::{mc.group(1)}` 於常數表解不出（常數表缺該名）")
            keys.append(const_map[mc.group(1)])
        elif ml:
            keys.append(ml.group(1))
        else:
            raise StructuralError(f"MSG_KEYS 元素解不出：`{e}`（只容 `msg_key::NAME` 或直寫字面）")
    if len(keys) != declared:
        raise StructuralError(f"MSG_KEYS 宣告 [&str; {declared}] 但元素 {len(keys)} 個")
    return const_map, keys


# ─── 右源 ───

def parse_backend_keys(text, label):
    """locale 檔文字 → backend 子樹攤平鍵集（相對 backend、`.` 串接）；節缺席／brace 不配對／零鍵即 StructuralError。"""
    bv = blank_view(text, ts=True, strings=True)
    m = RE_BACKEND_ANCHOR.search(bv)
    if not m:
        raise StructuralError(f"{label}：backend 節缺席（錨＝獨佔一行 `backend: {{`）")
    open_idx = bv.index("{", m.start())
    end = match_brace(bv, open_idx)
    if end < 0:
        raise StructuralError(f"{label}：backend 節 brace 不配對")
    inner = bv[open_idx + 1:end]
    events = [(k.start(), "key", k) for k in RE_TS_KEY.finditer(inner)]
    events += [(i, ch, None) for i, ch in enumerate(inner) if ch in "{}"]
    events.sort(key=lambda t: t[0])
    path, pending, keys = [], None, set()
    for pos, kind, k in events:
        if kind == "key":
            after = inner[k.end():].lstrip()
            if after.startswith("{"):
                pending = k.group(1)
            else:
                keys.add(".".join(path + [k.group(1)]))
        elif kind == "{":
            path.append(pending if pending is not None else "?")
            pending = None
        else:
            if path:
                path.pop()
    if not keys:
        raise StructuralError(f"{label}：backend 節零鍵（比對面為空）")
    return keys


def parse_top_level_keys(text, label):
    """locale 檔文字 → backend 節之同層兄弟鍵集（不含 backend）＝前端 i18n 已用之頂層命名空間。錨同 parse_backend_keys；
    外層物件＝錨前最近之未配對 `{`、brace 配對取塊，塊內 brace 深度 0 之鍵即兄弟鍵。"""
    bv = blank_view(text, ts=True, strings=True)
    m = RE_BACKEND_ANCHOR.search(bv)
    if not m:
        raise StructuralError(f"{label}：backend 節缺席（錨＝獨佔一行 `backend: {{`）")
    depth, j = 0, m.start() - 1
    while j >= 0:
        if bv[j] == "}":
            depth += 1
        elif bv[j] == "{":
            if depth == 0:
                break
            depth -= 1
        j -= 1
    end = match_brace(bv, j) if j >= 0 else -1
    if end < 0:
        raise StructuralError(f"{label}：backend 節之外層物件缺席或 brace 不配對（頂層鍵無從取）")
    inner = bv[j + 1:end]
    events = [(k.start(), "key", k.group(1)) for k in RE_TS_KEY.finditer(inner)]
    events += [(i, ch, None) for i, ch in enumerate(inner) if ch in "{}"]
    events.sort(key=lambda t: t[0])
    keys, depth = set(), 0
    for _pos, kind, name in events:
        if kind == "{":
            depth += 1
        elif kind == "}":
            depth -= 1
        elif depth == 0:
            keys.add(name)
    keys.discard("backend")
    return keys


# ─── 斷言 2：Biz 構造點守衛 ───

def test_spans(bv):
    """`#[cfg(test)]` 所附項目的排除區間 [(start, end)]：屬性後掃到首個收界字元——
    `{`（項目本體：mod／fn／impl／struct…）＝brace 配對整段；`;`（宣告形）＝到該 `;`；
    ★`,`／`}`（欄位與 enum variant 形，如 `#[cfg(test)] pub probe: u8,`）＝到該欄位止。
    欄位形若照「首個 `{`／`;`」收界，指標會一路衝到其後第一支生產函式的本體、整支被當測試區排除
    （斷言 2 對該檔以下靜默失守、回包仍綠）。`(`／`[` 內的收界字元不算——
    `#[cfg(test)] fn f(a: u8, b: u8) {` 的參數逗號不收界、仍取整個函式本體。"""
    spans = []
    for m in RE_CFG_TEST.finditer(bv):
        j, depth, end = m.end(), 0, None
        while j < len(bv):
            c = bv[j]
            if c in "([":
                depth += 1
            elif c in ")]":
                depth -= 1
            elif depth <= 0 and c == "{":
                k = match_brace(bv, j)
                end = len(bv) if k < 0 else k + 1
                break
            elif depth <= 0 and c in ";,":
                end = j + 1
                break
            elif depth <= 0 and c == "}":
                end = j
                break
            j += 1
        spans.append((m.start(), len(bv) if end is None else end))
    return spans


def is_pattern_use(bv, close_idx):
    """`AppError::Biz(…)` 之 `)` 後的語境是否為 match／if-let 樣式（非構造）：跳過空白與外層 `)` 後見 `=>`／`|`／`if `／單一 `=`。"""
    j = close_idx + 1
    while j < len(bv) and (bv[j].isspace() or bv[j] == ")"):
        j += 1
    rest = bv[j:j + 3]
    return rest.startswith("=>") or rest.startswith("|") or re.match(r"if\b", rest) is not None or (
        rest.startswith("=") and not rest.startswith("=="))


def scan_biz_text(text, rel, const_map, keys):
    """單檔掃描 → (構造點數, findings)；生產區間內每處構造點驗 `Cow::Borrowed(字面|msg_key::NAME)` 且鍵 ∈ keys。"""
    bv = blank_view(text, ts=False, strings=True)
    cv = blank_view(text, ts=False, strings=False)
    excluded = test_spans(bv)
    count, findings = 0, []
    for m in RE_BIZ.finditer(bv):
        if any(a <= m.start() < b for a, b in excluded):
            continue
        depth, close = 0, -1
        for j in range(m.end() - 1, len(bv)):
            if bv[j] == "(":
                depth += 1
            elif bv[j] == ")":
                depth -= 1
                if depth == 0:
                    close = j
                    break
        line = line_of(text, m.start())
        if close < 0:
            findings.append(f"{rel}:{line}：`AppError::Biz(` 括號不配對")
            continue
        inner_bv = bv[m.end():close].strip()
        if inner_bv == "_" or is_pattern_use(bv, close):
            continue
        count += 1
        mb = RE_BORROWED.match(cv[m.end():close])
        if not mb:
            findings.append(f"{rel}:{line}：Biz 動態構造 `{cv[m.start():close + 1].strip()}`——須 `Cow::Borrowed(\"字面\")` 或 `Cow::Borrowed(msg_key::NAME)`")
            continue
        if mb.group(2):
            if mb.group(2) not in const_map:
                findings.append(f"{rel}:{line}：Biz 構造引用 `msg_key::{mb.group(2)}` 於常數表解不出")
                continue
            key = const_map[mb.group(2)]
        else:
            key = mb.group(1)
        if key not in keys:
            findings.append(f"{rel}:{line}：Biz 構造鍵 `{key}` 不在 MSG_KEYS 名冊")
    return count, findings


def scan_biz(root, const_map, keys):
    """`root/**/*.rs` 逐檔 → (檔數, 構造點總數, findings)。"""
    files, total, findings = 0, 0, []
    for dirpath, _dirs, names in os.walk(root):
        for name in sorted(names):
            if not name.endswith(".rs"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            n, f = scan_biz_text(text, rel, const_map, keys)
            files += 1
            total += n
            findings.extend(f)
    return files, total, findings


# ─── 斷言 3：前端 msg 字面消費點名冊 ───

def ts_code_view(text):
    """斷言 3 之 TS 剝註解視圖：回與 `text` 同長度的字串，`//`／`/* */` 註解遮成空白（換行保留），字串與 regex literal 保留原文。
    與斷言 1／2 共用之 `blank_view` 分立（該二斷言零改），另加兩條再同步判準——前端源檔之引號配對一旦錯位，其後「註解遮蔽」與
    「字串保留」整塊互換（假紅：註解內字面被計；假綠：字串內 `//` 落到字串外、遮掉同行真消費點）：
      ①`'`／`"` 字串依 TS 語法不得跨行：遇未跳脫換行即收尾（JSX 文字之撇號等未識別結構，錯位止於該行；反引號模板照舊可跨行）；
      ②regex literal：`/` 處於 `TS_REGEX_PREV`（運算子／開括號／分隔符／`=>`）或 `TS_REGEX_PREV_WORDS`（`return` 等）語境時，掃到同行內、
        字元類 `[…]` 外之未跳脫 `/`＋旗標，整段保留原文、其內引號不開字串（`/"/g`）；同行找不到收尾＝非 regex、照除號處理。"""
    out, i, n = [], 0, len(text)
    prev, word = "", ""  # 前一個有效碼字元（註解與空白不算；`=>` 記為一個）、以其結尾之識別字（空白不打斷、其餘字元清空）
    while i < n:
        c, two = text[i], text[i:i + 2]
        if two == "//":
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(_mask(text[i:j]))
            i = j
            continue
        if two == "/*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(_mask(text[i:j]))
            i = j
            continue
        if c in "'\"`":
            j = i + 1
            while j < n and text[j] != c and (c == "`" or text[j] != "\n"):
                j += 2 if text[j] == "\\" else 1
            j = j + 1 if j < n and text[j] == c else min(j, n)
            out.append(text[i:j])
            prev, word, i = c, "", j
            continue
        if c == "/" and (prev in TS_REGEX_PREV or word in TS_REGEX_PREV_WORDS):
            eol = text.find("\n", i)
            eol, j, in_class = (n if eol < 0 else eol), i + 1, False
            while j < eol and (in_class or text[j] != "/"):
                if text[j] == "\\":
                    j += 1
                elif text[j] == "[":
                    in_class = True
                elif text[j] == "]":
                    in_class = False
                j += 1
            if j < eol and text[j] == "/":
                j += 1
                while j < n and (text[j].isalnum() or text[j] in "_$"):
                    j += 1
                out.append(text[i:j])
                prev, word, i = "/", "", j
                continue
        out.append(c)
        if not c.isspace():
            ident = c.isalnum() or c in "_$"
            word = (word + c if i > 0 and (text[i - 1].isalnum() or text[i - 1] in "_$") else c) if ident else ""
            prev = "=>" if c == ">" and prev == "=" else c
        i += 1
    return "".join(out)


def frontend_code_view(text, vue):
    """回與 `text` 同長度、註解遮成空白之視圖（字串保留；剝法見 `ts_code_view`）：`.ts`／`.tsx` 整檔剝 `//`／`/* */`（含 JSDoc）；
    `.vue` 之 `<script>` 塊（開標籤認引號屬性、見 `RE_SCRIPT_OPEN`）內同上、塊外（template／style）只剝 `<!-- -->`——template 文字
    不當 TS 掃（文案中的撇號會被誤當字串起點）。"""
    if not vue:
        return ts_code_view(text)
    out, i, n = [], 0, len(text)
    while i < n:
        c = text.find("<!--", i)
        s = RE_SCRIPT_OPEN.search(text, i)
        if c < 0 and s is None:
            out.append(text[i:])
            break
        if c >= 0 and (s is None or c < s.start()):
            j = text.find("-->", c + 4)
            j = n if j < 0 else j + 3
            out.append(text[i:c] + _mask(text[c:j]))
        else:
            j = text.find("</script>", s.end())
            j = n if j < 0 else j
            out.append(text[i:s.end()] + ts_code_view(text[s.end():j]))
        i = j
    return "".join(out)


def scan_frontend(src_dir, keyset, safe):
    """`src_dir/**/*.{ts,vue,tsx}`（排除頂層 `locales/`）剝註解後之字串字面 → (檔數, {(相對路徑, 鍵): [行號…]})。
    消費點＝①字面恰等於 MSG_KEYS 成員 或 ②字面為 wire 形（`.` 串接之識別字段）且首段 ∈ `safe`。"""
    files, points = 0, {}
    for dirpath, dirs, names in os.walk(src_dir):
        if os.path.abspath(dirpath) == os.path.abspath(src_dir) and FRONTEND_EXCLUDE in dirs:
            dirs.remove(FRONTEND_EXCLUDE)
        dirs.sort()
        for name in sorted(names):
            if not name.endswith(FRONTEND_EXTS):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            view = frontend_code_view(text, name.endswith(".vue"))
            rel = os.path.relpath(path, src_dir).replace(os.sep, "/")
            files += 1
            for m in RE_WIRE_LITERAL.finditer(view):
                key = m.group(2)
                if key in keyset or key.split(".", 1)[0] in safe:
                    points.setdefault((rel, key), []).append(line_of(view, m.start()))
    return files, points


def frontend_findings(points, roster, keyset):
    """實掃 ⇔ 名冊逐項雙向全等（含次數）且每鍵 ∈ MSG_KEYS；回 findings（空＝綠）。"""
    out = []
    for (rel, key), lines in sorted(points.items()):
        want, locs = roster.get((rel, key)), "、".join(f"{rel}:{ln}" for ln in lines)
        if want is None:
            out.append(f"前端 msg 字面消費點未登記名冊：{locs} `{key}`（新增消費點須同批登記 FRONTEND_MSG_CONSUMERS）")
        elif want != len(lines):
            out.append(f"前端 msg 字面消費點次數不等：{rel} `{key}` 名冊 {want} 處、實掃 {len(lines)} 處（{locs}）")
    for (rel, key), want in sorted(roster.items()):
        if (rel, key) not in points:
            out.append(f"前端 msg 字面消費點名冊項消失：{rel} `{key}`（名冊 {want} 處、實掃 0 處——消費點改寫或移除須同批更新名冊）")
    for key in sorted({k for _, k in points} | {k for _, k in roster}):
        if key in keyset:
            continue
        where = [f"{r}:{ln}" for (r, k), lns in sorted(points.items()) if k == key for ln in lns]
        where = where or [f"{r}（名冊）" for (r, k) in sorted(roster) if k == key]
        out.append(f"前端 msg 字面 `{key}` 不在 MSG_KEYS：{'、'.join(where)}（後端鍵改名或刪除而前端消費點未跟＝該分支靜默失效）")
    return out


# ─── check ───

def run_check(rust_path, locales_dir, src_dir, roster):
    """回 (rc, 輸出行清單)。結構異常先於違規：任一 rc 2 即整體 rc 2（仍列出已查到的其餘問題）。"""
    lines, structural, violations = [], [], []
    try:
        if not os.path.isfile(rust_path):
            raise StructuralError(f"左源檔缺席：{rust_path}")
        with open(rust_path, encoding="utf-8") as fh:
            const_map, keys = parse_left(fh.read())
    except StructuralError as e:
        return RC_STRUCT, [f"{TAG} ✗ {e}"]
    keyset, top_keys = set(keys), set()
    for name in LOCALE_FILES:
        path = os.path.join(locales_dir, name)
        if not os.path.isfile(path):
            structural.append(f"{name}：檔缺席（{path}）")
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            have = parse_backend_keys(text, name)
            top_keys |= parse_top_level_keys(text, name)
        except StructuralError as e:
            structural.append(str(e))
            continue
        missing, extra = sorted(keyset - have), sorted(have - keyset)
        if missing or extra:
            violations.append(f"{name}：backend 子樹與 MSG_KEYS 不等——缺：{missing or '無'}；多：{extra or '無'}")
    files, points, biz_findings = scan_biz(os.path.dirname(os.path.abspath(rust_path)), const_map, keyset)
    violations.extend(biz_findings)
    if points == 0:
        structural.append(f"斷言 2 比對面為空：掃 {files} 檔生產區間、Biz 構造點零處"
                          "（掃描根有誤或 `#[cfg(test)]` 排除過度——守衛無實際比對面即假綠）")
    # 斷言 3：安全前綴不寫死＝MSG_KEYS 頂層前綴 − 三檔 locale 頂層鍵（i18n 已用之命名空間不當 wire 形判）。
    safe = sorted({k.split(".", 1)[0] for k in keyset} - top_keys)
    fe_files, fe_points = 0, {}
    if not os.path.isdir(src_dir):
        structural.append(f"斷言 3 前端掃描根缺席：{src_dir}")
    else:
        fe_files, fe_points = scan_frontend(src_dir, keyset, set(safe))
        if fe_files == 0:
            structural.append(f"斷言 3 比對面為空：{src_dir} 下（排除 {FRONTEND_EXCLUDE}/）零 {'／'.join(FRONTEND_EXTS)} 源檔——掃描根有誤時不得回綠")
        violations.extend(frontend_findings(fe_points, roster, keyset))
    for s in structural:
        lines.append(f"{TAG} ✗ 結構異常：{s}")
    for v in violations:
        lines.append(f"{TAG} ✗ {v}")
    if structural:
        return RC_STRUCT, lines
    if violations:
        return RC_VIOLATION, lines
    lines.append(f"{TAG} ✓ MSG_KEYS {len(keys)} 鍵 ⇔ {'／'.join(LOCALE_FILES)} backend 子樹逐檔雙向全等；Biz 構造點 {points} 處"
                 f"（掃 {files} 檔生產區間）皆字面／常數形且在名冊")
    lines.append(f"{TAG} ✓ 前端 msg 字面消費點 {sum(len(v) for v in fe_points.values())} 處（掃 {fe_files} 檔、排除 {FRONTEND_EXCLUDE}/；"
                 f"安全前綴 {safe}＝MSG_KEYS 頂層前綴 − locale 頂層鍵）⇔ 名冊 {len(roster)} 項逐項全等、每鍵在 MSG_KEYS")
    return RC_OK, lines


def check(rust_path, locales_dir, src_dir):
    rc, lines = run_check(rust_path, locales_dir, src_dir, FRONTEND_MSG_CONSUMERS)
    for ln in lines:
        print(ln, file=sys.stderr if rc else sys.stdout, flush=True)
    return rc


# ─── self-test ───

SYN_CONSTS = (("A", "common.success"), ("B", "system.internal"), ("C", "biz.auth.locked"))


def write_rust(d, elems, declared=None, biz=True, extra_rs=None):
    consts = "".join(f'    pub const {n}: &str = "{v}";\n' for n, v in SYN_CONSTS)
    body = ",\n".join(f"    {e}" for e in elems)
    n = len(elems) if declared is None else declared
    # 合法構造點一處＝斷言 2 的比對面（`biz=False` 造「比對面為空」反例、`declared` 造宣告數≠元素數反例）。
    ctor = "pub fn ok_biz() -> AppError { AppError::Biz(Cow::Borrowed(msg_key::C)) }\n" if biz else ""
    src = ("//! 合成 error.rs（字串內含 { 與 // 用來騙結構掃描）\n"
           f"pub mod msg_key {{\n{consts}}}\n\n"
           f"pub const MSG_KEYS: [&str; {n}] = [\n{body},\n];\n"
           'const DECOY: &str = "{ // }";\n'
           f"{ctor}")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "error.rs"), "w", encoding="utf-8") as fh:
        fh.write(src)
    if extra_rs is not None:
        with open(os.path.join(d, "handler.rs"), "w", encoding="utf-8") as fh:
            fh.write(extra_rs)
    return os.path.join(d, "error.rs")


# ─── 合成 locale 樣本：右源判準的反例誘餌 ───
# 右源四條判準（錨須獨佔一行／剝 `/* */`／剝 `//`／剝字串值）各配一個「判準被拿掉就當場紅」的誘餌，
# 使案①（三檔全等綠）兼任四條的反例載體（RL-0051 一正一反；誘餌互不遮蔽、單獨拿掉任一判準即失守）：
#   ①行內假錨 `system: { …, backend: { inlineDecoy: 1 } }`——錨若放寬成任意位置，此塊位置更前、先被命中 ⇒ ①④ 紅
#   ②區塊註解內的獨佔一行假錨——`/* */` 遮罩若關掉，該假塊位置更前、先被命中 ⇒ ①④ 紅
#   ③真 backend 塊內的行註解（假鍵＋單邊右括號）——`//` 遮罩若關掉，塊提前閉合且多出 lineCommentDecoy ⇒ ① 紅
#   ④譯文字串值內的假鍵與單邊右括號（見 LEAF_VALUE）——字串遮罩若關掉，塊提前閉合且多出 Note ⇒ ① 紅
LEAF_VALUE = "'Note: 尚未就緒 } 說明'"
LOCALE_PRELUDE = (
    "const local = {\n"
    "  system: { title: 'x { backend: { y: 1 } }', backend: { inlineDecoy: 1 } },\n"
    "  /* 區塊註解內的假錨（獨佔一行、零縮排）：\n"
    "backend: {\n"
    "  blockCommentDecoy: 1\n"
    "}\n"
    "  */\n"
)
LOCALE_BACKEND_HEAD = (
    "  // [rev6-inline …] backend 樹\n"
    "  backend: {\n"
    "    // 行註解內的假鍵與單邊右括號：lineCommentDecoy: 'x' }\n"
)
LOCALE_TAIL = "  common: { ok: 'ok' }\n};\nexport default local;\n"

# ─── 合成前端源樣本：斷言 3 的正例與反例誘餌 ───
# 合成 locale 之頂層鍵＝system／common（backend 除外）、SYN_CONSTS 頂層前綴＝common／system／biz ⇒ 安全前綴＝{biz}。
# 真消費點九處：login.vue L5（規則②安全前綴形）、L11（template 屬性值內之字面）、api.ts L3（規則①恰等於成員、common 非安全前綴）、
# 以及下列三組再同步誘餌檔內之 generic.vue L1／L4、cols.vue L4、strip.ts L2／L3／L4。
# 誘餌（判準被拿掉即多計、名冊對不上當場紅）：`//`／`/** */`／`<!-- -->` 三形註解內字面（`.vue` script 塊與 `.ts` 各置一組）、i18n `system.title`／`common.ok`（前綴非安全、
# 亦非成員）、`locales/` 下之字面、非源檔副檔名（.md）內之字面。
# 再同步誘餌（引號配對一旦錯位，其後「註解遮蔽」與「字串保留」整塊互換；三條判準各配一檔、單獨拿掉任一即當場紅）：
#   generic.vue＝`<script>` 開標籤認引號屬性：generic 屬性值含 `>`（真 repo table-column-setting.vue 同形）且開標籤與首行碼同行——
#     開標籤若在屬性值內之 `>` 提前收尾，殘段 `">` 的引號與 URL 內 `//` 會遮掉 L1 同行真消費點（行尾再同步救不到同行）⇒ 少計；
#   cols.vue＝`'`／`"` 字串不跨行：tsx 之 JSX 文字撇號 `Don't` 若一路配到下一行，L3 註解內字面被計 ⇒ 多計；
#   strip.ts＝regex literal 整段跳過：regex 內引號若開字串，同行 URL 內 `//` 落到字串外而遮掉同行 `common.success` ⇒ 少計，
#     或同行註解內 `biz.auth.locked` 被計 ⇒ 多計；regex 判準每條一行：L1 `(` 語境＋`/"/g`（真 repo config-operation.vue 同形）、
#     L2 `=>` 語境、L3 關鍵字 `return` 語境＋跳脫 `\/`、L4 字元類內之 `/`、L5 `n-- /` 同行無收尾＝除號（regex 掃描若跨行，
#     會一路吞到 L6 `//` 而使其後註解內字面被計）。
SYN_VUE_GENERIC = (
    '<script setup lang="ts" generic="T extends Record<string, unknown>, K = never">'
    "const home = \"https://x.test\"; if (msg === 'biz.auth.locked') go(home);\n"
    'import { go } from "./go";\n'
    "// 收到 'biz.auth.locked' 時轉頁（註解內字面不計）\n"
    "const u = \"https://x.test\"; if (msg === 'biz.auth.locked') go(u);\n"
    "</script>\n"
    "<template><div /></template>\n")
SYN_VUE_TSX = (
    '<script setup lang="tsx">\n'
    "const hint = () => <span>Don't retry</span>;\n"
    "// 註解內字面不計：'biz.auth.locked'\n"
    "const u = \"https://x.test\"; if (msg === 'biz.auth.locked') go(u);\n"
    "</script>\n")
SYN_TS_REGEX = (
    "export const strip = (s: string) => s.replace(/\"/g, ''); // 註解內字面不計：'biz.auth.locked'\n"
    "export const hasQuote = (s: string) => /\"/.test(s) || s === \"https://x.test\" || s === 'common.success';\n"
    "export function unquote(s: string) { return /\\/\"/.test(s) ? \"https://x.test\" : 'common.success'; }\n"
    "export const unslash = (s: string) => s.replace(/[/\"]/g, \"\") === \"https://x.test\" || s === 'common.success';\n"
    "export const half = (n: number) => n-- / 2;\n"
    "// 註解內字面不計：'biz.auth.locked'\n")
SYN_VUE_HEAD = (
    '<script setup lang="ts">\n'
    "// 行註解內字面不計：'biz.auth.locked'\n"
    "/** JSDoc 內字面不計：`common.success` */\n"
    "const msg = await login();\n")
SYN_VUE_I18N = (
    "const title = $t('system.title'); // i18n system.*\n"
    "const hint = $t('common.ok'); /* i18n common.* */\n"
    "</script>\n"
    "<template>\n"
    "  <!-- HTML 註解內字面不計：'biz.auth.locked' -->\n")
SYN_SRC = {
    "views/login.vue": (SYN_VUE_HEAD
                        + "if (msg === 'biz.auth.locked') lock();\n"
                        + SYN_VUE_I18N
                        + "  <p :class=\"state === 'biz.auth.locked' ? 'on' : 'off'\">{{ $t('page.login.title') }}</p>\n"
                        + "</template>\n"),
    "service/api.ts": ("// 規則①：恰等於 MSG_KEYS 成員即消費點；.ts 行註解內字面不計：'biz.auth.locked'\n"
                       "/** .ts JSDoc 內字面不計：`common.success` */\n"
                       "export const OK_MSG = \"common.success\";\n"),
    "components/generic.vue": SYN_VUE_GENERIC,
    "components/cols.vue": SYN_VUE_TSX,
    "utils/strip.ts": SYN_TS_REGEX,
    "locales/langs/extra.ts": "export const decoy = 'biz.auth.locked';\n",
    "views/notes.md": "'biz.auth.locked'\n",
}
SYN_ROSTER = {("views/login.vue", "biz.auth.locked"): 2, ("service/api.ts", "common.success"): 1,
              ("components/generic.vue", "biz.auth.locked"): 2, ("components/cols.vue", "biz.auth.locked"): 1,
              ("utils/strip.ts", "common.success"): 3}


def write_src(d, files):
    os.makedirs(d, exist_ok=True)
    for rel, text in files.items():
        path = os.path.join(d, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    return d


def ts_tree(keys):
    tree = {}
    for k in keys:
        node = tree
        parts = k.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = LEAF_VALUE
    def emit(node, indent):
        out = []
        for k, v in node.items():
            if isinstance(v, dict):
                out.append(f"{indent}{k}: {{\n" + emit(v, indent + "  ") + f"{indent}}},\n")
            else:
                out.append(f"{indent}{k}: {v},\n")
        return "".join(out)
    return emit(tree, "    ")


def write_locales(d, per_file, backend=True, tail=LOCALE_TAIL):
    os.makedirs(d, exist_ok=True)
    for name in LOCALE_FILES:
        keys = per_file.get(name, per_file.get("*"))
        has_backend = backend.get(name, True) if isinstance(backend, dict) else backend
        block = (LOCALE_BACKEND_HEAD + ts_tree(keys) + "  },\n") if has_backend else ""
        src = LOCALE_PRELUDE + block + tail
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            fh.write(src)


def self_test():
    """契約七案（code-gates.md §2 self-test 列）＋判準補強三案（斷言 2 比對面為空／`MSG_KEYS` 宣告數≠元素數／
    Biz 構造鍵之名冊歸屬兩分支）＋真 repo 左源綠案＋斷言 3 八案（綠／鍵改名／未登記／名冊項消失／次數不等／註解與 i18n 不誤紅／
    安全前綴隨 locale 頂層鍵變動／比對面為空）；任一案敗＝rc 2、指名案號。"""
    all_keys = [v for _, v in SYN_CONSTS]
    cases = []
    with tempfile.TemporaryDirectory() as tmp:
        def scenario(tag, elems, per_file, backend=True, extra_rs=None, biz=True, declared=None, src=None, roster=None, tail=LOCALE_TAIL):
            base = os.path.join(tmp, tag)
            rust = write_rust(os.path.join(base, "src"), elems, declared=declared, biz=biz, extra_rs=extra_rs)
            write_locales(os.path.join(base, "langs"), per_file, backend, tail=tail)
            web = write_src(os.path.join(base, "web"), SYN_SRC if src is None else src)
            return run_check(rust, os.path.join(base, "langs"), web, SYN_ROSTER if roster is None else roster)

        lit = [f'"{k}"' for k in all_keys]
        rc, out = scenario("c1", lit, {"*": all_keys})
        cases.append(("①三檔全等綠", rc == RC_OK and any("逐檔雙向全等" in ln for ln in out), rc, out))
        rc, out = scenario("c2", lit, {"*": all_keys, "zh-cn.ts": all_keys[:-1]})
        cases.append(("②某檔缺一鍵 rc 1 指名", rc == RC_VIOLATION and any("zh-cn.ts" in ln and "缺：['biz.auth.locked']" in ln for ln in out), rc, out))
        rc, out = scenario("c3", lit, {"*": all_keys, "en-us.ts": all_keys + ["biz.auth.extra"]})
        cases.append(("③某檔多一鍵 rc 1 指名", rc == RC_VIOLATION and any("en-us.ts" in ln and "多：['biz.auth.extra']" in ln for ln in out), rc, out))
        rc, out = scenario("c4", lit, {"*": all_keys}, backend={"zh-tw.ts": False})
        cases.append(("④某檔缺 backend 節 rc 2", rc == RC_STRUCT and any("zh-tw.ts" in ln and "backend 節缺席" in ln for ln in out), rc, out))
        rust5 = write_rust(os.path.join(tmp, "c5", "src"), [f"msg_key::{n}" for n, _ in SYN_CONSTS])
        with open(rust5, encoding="utf-8") as fh:
            const_map, keys = parse_left(fh.read())
        write_locales(os.path.join(tmp, "c5", "langs"), {"*": all_keys})
        web5 = write_src(os.path.join(tmp, "c5", "web"), SYN_SRC)
        rc, out = run_check(rust5, os.path.join(tmp, "c5", "langs"), web5, SYN_ROSTER)
        cases.append(("⑤常數間接形解析成功", keys == all_keys and len(const_map) == 3 and rc == RC_OK, rc, out))
        rc, out = scenario("c6", ["msg_key::A", "msg_key::B", "msg_key::MISSING"], {"*": all_keys})
        cases.append(("⑥常數表缺該名 rc 2", rc == RC_STRUCT and any("msg_key::MISSING" in ln for ln in out), rc, out))
        # 排除區間收界的兩個誘餌（各自對應一條收界判準、拿掉即當場失守）：L5 的欄位形屬性若照「首個 `{`」收界，
        # 會吞掉緊鄰其後的 L6 動態構造（flagged 只剩一筆）；L9 的帶參數測試函式則證參數逗號不得提前收界（否則多報一筆）。
        handler = (
            "use std::borrow::Cow;\nuse crate::error::{AppError, msg_key};\n"
            "pub fn good() -> AppError { AppError::Biz(Cow::Borrowed(msg_key::C)) }\n"           # L3 合法常數形
            "pub fn good_lit() -> AppError { AppError::Biz(Cow::Borrowed(\"common.success\")) }\n"  # L4 合法字面形
            "pub struct Cfg { #[cfg(test)] pub probe: u8, pub real: u8, #[cfg(test)] pub last: u8 }\n"  # L5 欄位形屬性（`,`／`}` 收界；緊鄰其後的 L6 動態構造即失守面）
            "pub fn bad_fmt() -> AppError { AppError::Biz(Cow::Owned(format!(\"x{}\", 1))) }\n"    # L6 動態
            "pub fn bad_var(k: Cow<'static, str>) -> Result<(), AppError> { return Err(AppError::Biz(k)); }\n"  # L7 動態
            "pub fn code(e: &AppError) -> &str { match e { AppError::Biz(_) => \"2222\", AppError::Biz(k) if k.is_empty() => \"\", _ => \"\" } }\n"  # L8 樣式
            "#[cfg(test)]\nfn helper(a: u8, b: u8) -> AppError { let _ = (a, b); AppError::Biz(Cow::Owned(String::new())) }\n"  # L9 測試區（參數逗號不收界）
            "#[cfg(test)]\nmod tests {\n    use super::*;\n"
            "    fn t() -> AppError { AppError::Biz(Cow::Owned(String::new())) }\n"              # 測試區、排除
            "}\n")
        rc, out = scenario("c7", lit, {"*": all_keys}, extra_rs=handler)
        flagged = [ln for ln in out if "handler.rs" in ln]
        ok7 = (rc == RC_VIOLATION and len(flagged) == 2 and any("handler.rs:6" in ln for ln in flagged)
               and any("handler.rs:7" in ln for ln in flagged))
        cases.append(("⑦動態 Biz 構造 rc 1（L6 format!／L7 變數；L3／L4 合法、L8 樣式與測試區不計；"
                      "L5 欄位形屬性不吞其後生產函式、L9 參數逗號不提前收界）", ok7, rc, out))
        rc, out = scenario("c8", lit, {"*": all_keys}, biz=False)
        cases.append(("⑧斷言 2 比對面為空 rc 2（生產區間零 Biz 構造點）",
                      rc == RC_STRUCT and any("比對面為空" in ln for ln in out), rc, out))
        rc, out = scenario("c9", lit, {"*": all_keys}, declared=len(lit) + 1)
        cases.append(("⑨MSG_KEYS 宣告數≠元素數 rc 2",
                      rc == RC_STRUCT and any(f"宣告 [&str; {len(lit) + 1}] 但元素 {len(lit)} 個" in ln for ln in out), rc, out))
        # 斷言 2 的「名冊歸屬」半條＝`scan_biz_text` 兩條分支（鍵不在 MSG_KEYS／`msg_key::X` 常數表解不出）。
        # 案⑦只打「形不合」（動態構造）那半條——形合但鍵不對者若無反例，兩條判準被變異掉仍全案綠（守衛靜默失守）。
        roster = (
            "use std::borrow::Cow;\nuse crate::error::{AppError, msg_key};\n"
            'pub fn ghost_lit() -> AppError { AppError::Biz(Cow::Borrowed("biz.auth.ghost")) }\n'     # L3 字面解得出、不在名冊
            "pub fn ghost_const() -> AppError { AppError::Biz(Cow::Borrowed(msg_key::UNKNOWN)) }\n"   # L4 常數表無此名
            "pub fn good() -> AppError { AppError::Biz(Cow::Borrowed(msg_key::A)) }\n")               # L5 合法常數形（收界誘餌：不得誤報）
        rc, out = scenario("c10", lit, {"*": all_keys}, extra_rs=roster)
        flagged = [ln for ln in out if "handler.rs" in ln]
        ok10 = (rc == RC_VIOLATION and len(flagged) == 2
                and any("handler.rs:3" in ln and "不在 MSG_KEYS 名冊" in ln for ln in flagged)
                and any("handler.rs:4" in ln and "於常數表解不出" in ln for ln in flagged))
        cases.append(("⑩Biz 構造鍵之名冊歸屬 rc 1（L3 字面不在 MSG_KEYS 名冊／L4 `msg_key::UNKNOWN` 常數表解不出；"
                      "L5 合法常數形不誤報）", ok10, rc, out))
        # 真 repo 左源綠案：現行 error.rs 常數形解得出、Biz 構造點皆常數／字面形；右源以解出鍵集合成（三檔實體＝check 的事、pre-commit 段跑）。
        real_rust = os.path.join(ROOT, DEFAULT_RUST)
        ok_real, rc, out, keys = False, None, [], []
        if os.path.isfile(real_rust):
            with open(real_rust, encoding="utf-8") as fh:
                real_const, keys = parse_left(fh.read())
            write_locales(os.path.join(tmp, "real", "langs"), {"*": keys})
            # 前端面以「真鍵集中任一 biz.* 鍵」合成單一消費點（本案只驗左源；三檔實體與真前端面＝check 的事）
            real_key = next((k for k in keys if k.startswith("biz.")), keys[0] if keys else "biz.none")
            web_real = write_src(os.path.join(tmp, "real", "web"), {"views/x.ts": f"export const K = '{real_key}';\n"})
            rc, out = run_check(real_rust, os.path.join(tmp, "real", "langs"), web_real, {("views/x.ts", real_key): 1})
            _f, points, _fd = scan_biz(os.path.dirname(real_rust), real_const, set(keys))
            ok_real = rc == RC_OK and len(keys) == len(set(keys)) and points >= 1
        cases.append((f"⑪真 repo 左源綠案（error.rs 解出 {len(keys)} 鍵、Biz 構造點皆常數形）", ok_real, rc, out))

        # ── 斷言 3：前端 msg 字面消費點名冊（誘餌與真消費點見 SYN_SRC 上方註）──
        rc, out = scenario("c12", lit, {"*": all_keys})
        cases.append(("⑫斷言 3 綠：名冊⇔實掃逐項全等（規則①非安全前綴之成員／規則②安全前綴形／template 屬性值內字面；"
                      "三形註解、i18n system.*／common.*、locales/、非源檔副檔名皆不計；再同步三誘餌＝開標籤屬性值含 `>`／"
                      "JSX 撇號不跨行／regex literal 內引號）",
                      rc == RC_OK and any("前端 msg 字面消費點 9 處" in ln and "安全前綴 ['biz']" in ln for ln in out), rc, out))
        renamed = [k.replace("biz.auth.locked", "biz.auth.lockedOut") for k in all_keys]
        rc, out = scenario("c13", [f'"{k}"' for k in renamed], {"*": renamed})
        cases.append(("⑬後端鍵改名、前端消費點未跟 rc 1 指名檔:行",
                      rc == RC_VIOLATION and any("`biz.auth.locked` 不在 MSG_KEYS" in ln and "views/login.vue:5" in ln
                                                 and "views/login.vue:11" in ln for ln in out), rc, out))
        rc, out = scenario("c14", lit, {"*": all_keys},
                           src={**SYN_SRC, "store/auth.ts": "export function isLocked(m: string) {\n  return m === 'biz.auth.locked';\n}\n"})
        cases.append(("⑭新增未登記消費點 rc 1 指名檔:行",
                      rc == RC_VIOLATION and any("未登記" in ln and "store/auth.ts:2" in ln for ln in out), rc, out))
        rc, out = scenario("c15", lit, {"*": all_keys}, roster={**SYN_ROSTER, ("views/gone.vue", "biz.auth.locked"): 1})
        cases.append(("⑮名冊項消失 rc 1 指名",
                      rc == RC_VIOLATION and any("名冊項消失" in ln and "views/gone.vue" in ln for ln in out), rc, out))
        rc, out = scenario("c16", lit, {"*": all_keys}, roster={**SYN_ROSTER, ("views/login.vue", "biz.auth.locked"): 1})
        cases.append(("⑯出現次數與名冊不等 rc 1 指名檔:行",
                      rc == RC_VIOLATION and any("次數不等" in ln and "views/login.vue:5" in ln and "views/login.vue:11" in ln
                                                 for ln in out), rc, out))
        quiet = {"views/quiet.vue": SYN_VUE_HEAD + SYN_VUE_I18N + "</template>\n"}
        rc, out = scenario("c17", lit, {"*": all_keys}, src=quiet, roster={})
        cases.append(("⑰三形註解內字面與 i18n system.*／common.* 不誤紅（名冊空、消費點 0 處仍綠）",
                      rc == RC_OK and any("前端 msg 字面消費點 0 處" in ln for ln in out), rc, out))
        ghost = {"views/ghost.ts": "export const G = 'biz.auth.ghost';\n"}
        rc_a, out_a = scenario("c18a", lit, {"*": all_keys}, src=ghost, roster={})
        rc_b, out_b = scenario("c18b", lit, {"*": all_keys}, src=ghost, roster={}, tail="  biz: { hint: 'x' },\n" + LOCALE_TAIL)
        cases.append(("⑱安全前綴＝MSG_KEYS 頂層前綴 − locale 頂層鍵、隨後者變動（biz 安全時 `biz.auth.ghost` 紅；locale 增頂層 biz 後不計）",
                      rc_a == RC_VIOLATION and any("views/ghost.ts:1" in ln for ln in out_a)
                      and rc_b == RC_OK and any("安全前綴 []" in ln and "消費點 0 處" in ln for ln in out_b), rc_b, out_a + out_b))
        rc_a, out_a = scenario("c19", lit, {"*": all_keys}, roster={},
                               src={"locales/langs/x.ts": "export const d = 'biz.auth.locked';\n", "views/notes.md": "'biz.auth.locked'\n"})
        rc_b, out_b = run_check(os.path.join(tmp, "c19", "src", "error.rs"), os.path.join(tmp, "c19", "langs"),
                                os.path.join(tmp, "c19", "no-such-web"), {})
        cases.append(("⑲斷言 3 比對面為空 rc 2（掃描根內零源檔／掃描根缺席）",
                      rc_a == RC_STRUCT and any("斷言 3 比對面為空" in ln for ln in out_a)
                      and rc_b == RC_STRUCT and any("掃描根缺席" in ln for ln in out_b), rc_b, out_a + out_b))
    failed = [c for c in cases if not c[1]]
    for name, ok, rc, out in cases:
        print(f"{TAG} {'✓' if ok else '✗'} self-test {name}（rc={rc}）")
        if not ok:
            for ln in out:
                print(f"    {ln}")
    if failed:
        print(f"{TAG} ✗ self-test {len(failed)} 案敗", file=sys.stderr)
        return RC_STRUCT
    print(f"{TAG} ✓ self-test {len(cases)} 案全綠")
    return RC_OK


def main(argv):
    args = list(argv[1:])
    cmd = "check"
    if args and args[0] in ("check", "test"):
        cmd = args.pop(0)
    rust, locales, src = os.path.join(ROOT, DEFAULT_RUST), os.path.join(ROOT, DEFAULT_LOCALES), os.path.join(ROOT, DEFAULT_SRC)
    while args:
        a = args.pop(0)
        if a == "--rust" and args:
            rust = args.pop(0)
        elif a == "--locales" and args:
            locales = args.pop(0)
        elif a == "--src" and args:
            src = args.pop(0)
        else:
            print(f"{TAG} ✗ {USAGE}", file=sys.stderr, flush=True)
            return RC_USAGE
    if cmd == "test":
        return self_test()
    return check(rust, locales, src)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
