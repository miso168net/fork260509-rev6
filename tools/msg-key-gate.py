#!/usr/bin/env python3
"""msg key 跨端閘（003 刀 U9；spec FR-027、contracts/code-gates.md §2、research R9；碼面閘＝RUNBOOK §12 碼面閘表列、GT-12 腿對賬）。

用法：
  python3 tools/msg-key-gate.py [check] [--rust <error.rs>] [--locales <dir>]   左源 ⇔ 三檔 backend 子樹逐檔雙向全等＋Biz 構造點守衛
  python3 tools/msg-key-gate.py test                                             離線 self-test（契約七案＋判準補強三案＋真 repo 左源綠案；零 docker）
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
退出碼：0 綠／1 違規（鍵集不等、動態 Biz 構造、解出鍵不在名冊）／2 結構異常（檔缺席、常數表或 MSG_KEYS 解析失敗、backend 節缺席或
  brace 不配對、比對面為空；self-test 案敗亦 2）／64 用法錯。
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
TAG = "[msg-key-gate]"
USAGE = "用法：tools/msg-key-gate.py [check|test] [--rust <error.rs>] [--locales <dir>]"
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


# ─── check ───

def run_check(rust_path, locales_dir):
    """回 (rc, 輸出行清單)。結構異常先於違規：任一 rc 2 即整體 rc 2（仍列出已查到的其餘問題）。"""
    lines, structural, violations = [], [], []
    try:
        if not os.path.isfile(rust_path):
            raise StructuralError(f"左源檔缺席：{rust_path}")
        with open(rust_path, encoding="utf-8") as fh:
            const_map, keys = parse_left(fh.read())
    except StructuralError as e:
        return RC_STRUCT, [f"{TAG} ✗ {e}"]
    keyset = set(keys)
    for name in LOCALE_FILES:
        path = os.path.join(locales_dir, name)
        if not os.path.isfile(path):
            structural.append(f"{name}：檔缺席（{path}）")
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                have = parse_backend_keys(fh.read(), name)
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
    return RC_OK, lines


def check(rust_path, locales_dir):
    rc, lines = run_check(rust_path, locales_dir)
    for ln in lines:
        print(ln, file=sys.stderr if rc else sys.stdout)
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


def write_locales(d, per_file, backend=True):
    os.makedirs(d, exist_ok=True)
    for name in LOCALE_FILES:
        keys = per_file.get(name, per_file.get("*"))
        has_backend = backend.get(name, True) if isinstance(backend, dict) else backend
        block = (LOCALE_BACKEND_HEAD + ts_tree(keys) + "  },\n") if has_backend else ""
        src = LOCALE_PRELUDE + block + LOCALE_TAIL
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            fh.write(src)


def self_test():
    """契約七案（code-gates.md §2 self-test 列）＋判準補強三案（斷言 2 比對面為空／`MSG_KEYS` 宣告數≠元素數／
    Biz 構造鍵之名冊歸屬兩分支）＋真 repo 左源綠案；任一案敗＝rc 2、指名案號。"""
    all_keys = [v for _, v in SYN_CONSTS]
    cases = []
    with tempfile.TemporaryDirectory() as tmp:
        def scenario(tag, elems, per_file, backend=True, extra_rs=None, biz=True, declared=None):
            base = os.path.join(tmp, tag)
            rust = write_rust(os.path.join(base, "src"), elems, declared=declared, biz=biz, extra_rs=extra_rs)
            write_locales(os.path.join(base, "langs"), per_file, backend)
            return run_check(rust, os.path.join(base, "langs"))

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
        rc, out = run_check(rust5, os.path.join(tmp, "c5", "langs"))
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
            rc, out = run_check(real_rust, os.path.join(tmp, "real", "langs"))
            _f, points, _fd = scan_biz(os.path.dirname(real_rust), real_const, set(keys))
            ok_real = rc == RC_OK and len(keys) == len(set(keys)) and points >= 1
        cases.append((f"⑪真 repo 左源綠案（error.rs 解出 {len(keys)} 鍵、Biz 構造點皆常數形）", ok_real, rc, out))
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
    rust, locales = os.path.join(ROOT, DEFAULT_RUST), os.path.join(ROOT, DEFAULT_LOCALES)
    while args:
        a = args.pop(0)
        if a == "--rust" and args:
            rust = args.pop(0)
        elif a == "--locales" and args:
            locales = args.pop(0)
        else:
            print(f"{TAG} ✗ {USAGE}", file=sys.stderr)
            return RC_USAGE
    if cmd == "test":
        return self_test()
    return check(rust, locales)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
