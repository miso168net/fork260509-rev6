#!/usr/bin/env python3
"""rev5↔rev6 註解逐字重疊核（憲法 §I.5 第 3 款「註解一律重寫」／RL-0065／RL-0076 的機器證據）。

用法：
  python3 tools/comment-overlap.py [--min N] [--max-pct P] <rev6 檔 …>   逐檔對 rev5 對應檔比對；任一檔超標＝rc 1
  python3 tools/comment-overlap.py test                                  合成樣本自證（搬運判超標／改寫判零重疊／解析四形正例與射程外反例／
                                                                         `rev6-`↔`rev5-` 映射一正二反／base-web 三型豁免各一正一反〔含落在塊註解與
                                                                         HTML 註解內〕／碼面豁免 span 與圍欄各正反〔span 含 base-web 路徑與三型豁免
                                                                         同檔〕／rust-api 零三型豁免不讀源倉／
                                                                         比對面為空 rc 2 一正一反；pre-commit 於本檔 staged 時跑）
★解析面自 BL-00080 起含 `.py`／`.sh`／`.bash` 的 `#` 行註解與 docstring；但「隨遷工具」（RULES 名詞段：啟動書 D10／§4.5 授權自
  rev5 整檔搬運者）逐字承襲本就允許、不適用 RL-0076 的 rc 0 要求——對它們量到高重疊是預期、不是違紀。
rev5 對應檔＝`../fork260509-rev5/<同相對路徑>`（凍結 worktree；本工具只讀、絕不寫入）；同相對路徑缺席且檔名 `rev6-` 起首者，改找同目錄
  `rev5-` 接其後同名之檔（承 rev5-* 改名而來之 rev6-* 檔；輸出行明示映射來源）；仍缺席＝該檔無可比、報 n/a 不計超標；非 `rev6-` 起首之檔不映射。
解析（單一解析器：rev6 檔、rev5 對應檔、源倉基線一律同一套，副檔名以受比 rev6 路徑為準）＝四形聯集：
  ①lstrip 後 `//`／`///`／`//!` 起首之行；②lstrip 後 `/*` 起首之塊註解至 `*/` 止（含單行 `/** … */`；首行與續行剝一個前導 `*` 與其後一個空白）；
  ③`.vue` 檔 lstrip 後 `<!--` 起首之 HTML 註解至 `-->` 止（其他副檔名不解析 `<!--`——`.ts` 之模板字面可含之）。
  射程外：碼行之行尾 `//`、行中 `/* */` 與行中 `<!-- -->`、`*/` 或 `-->` 之後同行之碼；巢狀塊註解（`/* … /* … */ … */`）於第一個 `*/` 收尾、其後續行不量。
  行首 `/*`／`<!--` 開啟後至檔尾仍未閉合（實務上只見於字串或模板字面內以之起首之行）＝其後各行照註解收至檔尾、輸出不另指名（碼行混入分母、重疊比偏低）。
手法：去註解標記並壓掉全部空白，相鄰註解行併成一段；逐段對 rev5 註解全文找長度 ≥ min 的極大共同子字串，命中字元合計／本檔註解總字元＝重疊比。
  識別字、SQL 片段、路徑與 doctest 碼行本就兩代共用、門檻 25 字元下仍佔識別字密集檔 10%～12%，故預設門檻 40 字元／上限 5%：實測逐字搬運檔落
  18%～45%、改寫後 ≤4.1%，兩態不相接（校準時期＝只解析 `//` 行之 rust-api 面；三形解析後之 base-web 搬運檔另見 16% 級、仍遠高於上限）。
base-web 路徑（repo 根相對首段 `base-web`）三型豁免後再量——帶 fork-delta 標記之既有檔含兩代共享之強制字面、不豁免即結構性必紅而散文命中被淹沒：
  ①`[rev6-inline …]` 標記 token 本身（方括號整段；與 rev5 同軌道同刀名、只差前綴——同行其餘我方散文照計）；
  ②upstream 基線原有之註解行整行（源倉 `fork260509-soybean-admin-base` 之 `example` 分支同相對路徑檔、壓白後全等；基線無此檔＝我方新檔、本型不豁免）；
  ③`原行:` 起至行尾（憲法 §III 修改型契約強制逐字；其前之我方散文照計）。
  三型不論落在 `//` 行、塊註解或 HTML 註解內同判；豁免字元既不入分子也不入分母、逐檔輸出附三型豁免行數；rust-api 與其餘路徑零三型豁免、不讀源倉。
碼面豁免（全路徑同一邏輯、接在三型豁免之後；rev5 文本不豁免、保留全文供子字串比對）：
  ①行內 code span＝同一註解行內成對反引號包夾之非空段——移除處換成原始碼不含之切斷符，命中不得跨越 span 把前後散文接成一段；
    跨註解行之 span 不支援（逐行配對：奇數反引號之行可錯配、其間散文被當 span 或 span 內字面照計，誤差雙向且極小）；
  ②``` 圍欄＝doc 註（`///`／`//!`）或塊註解內，註解文本 lstrip 後以三個反引號起首之行開啟、同一註解（行號連續之註解行、空白註解行計入）內
    下一個同形行關閉——標記行與其間各行整行豁免；到註解邊界仍未關閉＝未閉合、該開啟行起照計（寧紅勿漏）並於輸出指名開啟行號。
  兩者皆不入分子也不入分母、逐檔輸出附 code span 段數／圍欄行數。
退出碼：0 綠／1 任一檔超標／2 rev6 檔缺席或不在 repo、base-web 路徑之源倉或 `example` 分支不可讀、比對面為空（本次引數之 rev5 對應檔
  全缺席〔映射後仍缺席者同計〕，或受比檔全體零可解析註解〔以四形解析、豁免前計：豁免後零字元是判定結果、非掃描面空〕）；argparse 用法錯亦 2。
"""
import argparse
import ast
import contextlib
import io
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import tokenize

ROOT = pathlib.Path(__file__).resolve().parents[1]
REV5 = ROOT.parent / "fork260509-rev5"
# base-web 基線座標與 `原行:` regex 同 tools/fork-delta-lint.py 之 FORK／BASELINE／MARKER（連字檔名不可 import、此處同形宣告）；
# TOKEN＝標記 token 方括號整段（fork-delta-lint 之 TRACK 只錨到軌道名、豁免須剝到 `]`；未同行收 `]` 者不豁免＝照計、寧紅勿漏）。
FORK = ROOT / "fork260509-soybean-admin-base"
BASELINE = "example"
BASEWEB = "base-web"
# 承 rev5-* 改名而來之 rev6-* 檔（憲法強制改名形）：同相對路徑缺席時改找同目錄 `rev5-` 接其後同名之檔。
REV6_PREFIX, REV5_PREFIX = "rev6-", "rev5-"
MARKER = re.compile(r"原行:\s*(.*\S)\s*$")
TOKEN = re.compile(r"\[rev6-inline\s[^\]]*\]")
EXEMPT_KINDS = ("標記 token", "基線原有", "原行載荷")
DEFAULT_MIN = 40
DEFAULT_MAX_PCT = 5.0
WS = re.compile(r"\s+")
MARK = re.compile(r"^\s*(///|//!|//)\s?")
BLOCK_LEAD = re.compile(r"^\s*\*\s?")
# `#` 行註解與 docstring 解析面（BL-00080）：承 rev5 之 python／shell 隨遷工具以此形寫註解，
# 不解析＝RL-0076 的量尺對它們恆回「比對面為空」rc 2、量不到逐字重疊。
PY_SUFFIX = {".py"}
SH_SUFFIX = {".sh", ".bash"}
DOCSTR = re.compile(r"^[rRbBuUfF]{0,2}(\"{3}|'{3})")
# 碼面豁免：SPAN＝同一註解行內成對反引號包夾之非空段（不成圍欄之 ``` 行不當空 span）；SEP＝span 移除處之切斷符（原始碼文本不含 NUL＝
# 命中不得跨越）；FENCE＝圍欄記號。
SPAN = re.compile(r"`[^`]+`")
SEP = "\x00"
FENCE = "```"


class OverlapError(Exception):
    """結構／環境異常（rc 2）：訊息即輸出行。"""


def kind_of(path):
    """解析方言（副檔名一律取受比〔rev6〕路徑）：vue＝另解 `<!--` HTML 註解（`.ts` 等之模板字面可含 `<!--` 起首行、故不通用）；
    py＝`.py`，以 `tokenize`＋`ast` 取 `#` 行註解與**真** docstring（模組／類別／函式的首個字串陳述）；
    sh＝`.sh`／`.bash`，只取行首 `#`；其餘＝空字串，只解 `//` 家族與 `/* */`。"""
    suffix = pathlib.PurePath(path).suffix
    if suffix == ".vue":
        return "vue"
    return "py" if suffix in PY_SUFFIX else ("sh" if suffix in SH_SUFFIX else "")


def _py_rows(src):
    """`.py` 專用：`#` 行註解取自 tokenize 的 COMMENT token（只取整行即註解者，同「行首」契約）、
    docstring 取自 ast（模組／類別／函式的首個字串陳述）——★不以「行首三引號」猜，否則一般三引號字串的
    **收尾行**會被當成 docstring 開啟、其後碼行整段吞進量測面（mb4t review L1-2 實測：一支工具 97.4% 的
    重疊裡 40% 是碼）。語法不合本直譯器＝回 None，由呼叫端退回只取 `#`（寧漏勿吞）。"""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None
    lines = src.split("\n")
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = getattr(node, "body", None)
        if not body or not isinstance(body[0], ast.Expr):
            continue
        val = body[0].value
        if not (isinstance(val, ast.Constant) and isinstance(val.value, str)):
            continue
        for i in range(val.lineno, (val.end_lineno or val.lineno) + 1):
            raw = lines[i - 1]
            if i == val.lineno:
                mk = DOCSTR.match(raw.lstrip())
                raw = raw.lstrip()[mk.end():] if mk else raw
            if i == (val.end_lineno or val.lineno):
                stripped = raw.rstrip()
                for q in ('"' * 3, "'" * 3):
                    if stripped.endswith(q):
                        raw = stripped[:-3]
                        break
            rows.append((i, raw, True))
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type != tokenize.COMMENT:
                continue
            ln = tok.start[0]
            if not lines[ln - 1].lstrip().startswith("#"):
                continue                      # 行尾註解不收（同 `//` 之「行首」契約）
            if ln == 1 and tok.string.startswith("#!"):
                continue                      # shebang：兩代恆同字面、計入只會虛增重疊
            rows.append((ln, tok.string[1:], False))
    except (tokenize.TokenError, IndentationError):
        return None
    return sorted(rows, key=lambda r: r[0])


def comment_rows(lines, kind=""):
    """單一解析器 → [(行號, 去註解標記之原文, 是否 doc 註或塊註解)]，含去標記後空白之註解行（圍欄以行號連續之註解行定註解邊界）。四形聯集：
    ①lstrip 後 `//`／`///`／`//!` 起首之行（`///`／`//!`＝doc 註）；②lstrip 後 `/*` 起首之塊註解至 `*/` 止（單行 `/** … */` 同收；首行與
    續行剝一個前導 `*` 與其後一個空白）；③kind＝vue 時，lstrip 後 `<!--` 起首之 HTML 註解至 `-->` 止；④kind＝sh 時，lstrip 後 `#` 起首之行
    （★首行 shebang 不收——兩代恆同字面、計入只會虛增重疊）。★kind＝py 走 [`_py_rows`]（tokenize＋ast），不入本迴圈。
    收尾記號之後同行之碼不收；註解內之行不再判起首。"""
    if kind == "py":
        src = "".join(l if l.endswith("\n") else l + "\n" for l in lines)
        rows = _py_rows(src)
        if rows is not None:
            return rows
        kind = "sh"        # 語法不合＝退回只取行首 `#`（寧漏勿吞：絕不把碼行當註解）
    out, close = [], None  # close＝跨行註解之收尾記號（None＝不在塊／HTML 註解內）
    for i, line in enumerate(lines, 1):
        line = line.rstrip("\n")
        if close is None:
            s = line.lstrip()
            if s.startswith("//"):
                mk = MARK.match(line)
                out.append((i, line[mk.end():], mk.group(1) != "//"))
                continue
            if s.startswith("/*"):
                close, body = "*/", s[2:]
            elif kind == "vue" and s.startswith("<!--"):
                close, body = "-->", s[4:]
            elif kind == "sh" and s.startswith("#"):
                if i == 1 and s.startswith("#!"):
                    continue                      # shebang：兩代恆同字面、非重疊訊號
                out.append((i, s[1:], False))
                continue
            else:
                continue
        else:
            body = line
        end = body.find(close)
        if end >= 0:
            body = body[:end]
        if close == "*/":
            body = BLOCK_LEAD.sub("", body, count=1)
        out.append((i, body, close != "-->"))
        if end >= 0:
            close = None
    return out


def comment_lines(lines, kind=""):
    """回 [(行號, 去註解標記之原文)]，只收去標記後非空白之註解行（未壓白——標記判定要看原字距）。"""
    return [(i, raw) for i, raw, _doc in comment_rows(lines, kind) if WS.sub("", raw)]


def comment_units(path, kind=""):
    """回 [(行號, 去標記壓白後文字)]，只收非空註解行。"""
    with open(path, encoding="utf-8") as fh:
        return [(i, WS.sub("", raw)) for i, raw in comment_lines(fh, kind)]


def segments(units):
    """相鄰註解行併段（doc 常跨行、逐行比會漏掉接縫）。"""
    segs, cur, prev = [], [], None
    for ln, text in units:
        if prev is not None and ln != prev + 1:
            segs.append(cur)
            cur = []
        cur.append((ln, text))
        prev = ln
    if cur:
        segs.append(cur)
    return segs


def maximal_hits(mine, theirs, minlen):
    """自左而右貪婪：每個位置以二分找最長仍為 theirs 子字串的前綴，命中即跳過該段。"""
    hits, i, n = [], 0, len(mine)
    while i + minlen <= n:
        lo, hi, best = minlen, n - i, 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if mine[i:i + mid] in theirs:
                best, lo = mid, mid + 1
            else:
                hi = mid - 1
        if best:
            hits.append((i, mine[i:i + best]))
            i += best
        else:
            i += 1
    return hits


def compare(p6, p5, minlen, units=None):
    """回 (重疊比 %, [(行號, 長度, 片段)], 本檔註解總字元)；`units` 缺省＝p6 全部註解行（不豁免）。
    rev5 文本以 p6 之副檔名解析（受比路徑為準）。"""
    kind = kind_of(p6)
    theirs = "".join(t for _, t in comment_units(p5, kind))
    units = comment_units(p6, kind) if units is None else units
    total = sum(len(t) - t.count(SEP) for _, t in units)
    file_hits = []
    for seg in segments(units):
        joined = "".join(t for _, t in seg)
        marks, off = [], 0
        for ln, t in seg:
            marks.append((off, ln))
            off += len(t)
        for pos, frag in maximal_hits(joined, theirs, minlen):
            ln = next(l for o, l in reversed(marks) if o <= pos)
            file_hits.append((ln, len(frag), frag))
    hit_len = sum(h[1] for h in file_hits)
    pct = (hit_len * 100.0 / total) if total else 0.0
    return pct, file_hits, total


def git_env():
    """LL-00012：pre-commit 期間 git 匯出外層 GIT_DIR／GIT_INDEX_FILE 等——對源倉下 git 前一律剝 `GIT_*`（未剝＝讀錯 repo）。"""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def read_baseline(fork, rel):
    """回源倉 `example` 分支同相對路徑（base-web 根相對）檔全文；基線無此檔（我方新檔）回 None；源倉或分支不可讀＝OverlapError。"""
    def git(*args):
        return subprocess.run(["git", "-C", str(fork), *args], capture_output=True, text=True, encoding="utf-8", env=git_env())

    if git("rev-parse", "--verify", "-q", f"{BASELINE}^{{commit}}").returncode != 0:
        raise OverlapError(f"源倉 {fork} 缺席或無 `{BASELINE}` 分支——base-web 基線原有註解之豁免無從定界（跑 bash tools/bootstrap.sh 檢修）")
    if git("cat-file", "-e", f"{BASELINE}:{rel}").returncode != 0:
        return None
    shown = git("show", f"{BASELINE}:{rel}")
    if shown.returncode != 0:
        raise OverlapError(f"源倉 `git show {BASELINE}:{rel}` 失敗：{shown.stderr.strip()}")
    return shown.stdout


def exempt_units(path, baseline_text, kind=""):
    """base-web 檔三型豁免 → (保留之 units, {型: 行數})。判定序＝標記 token（只剝方括號整段、同行其餘照計；含 token 之行不比基線）
    → 基線原有（整行；壓白後全等於基線任一註解行）→ 原行載荷（只截 `原行:` 起至行尾、其前之我方散文照計）。
    `baseline_text` 為 None＝基線無此檔、第二型不豁免；基線與本檔經同一解析器取註解。"""
    base = set() if baseline_text is None else {WS.sub("", raw) for _, raw in comment_lines(baseline_text.splitlines(), kind)}
    kept, stats = [], dict.fromkeys(EXEMPT_KINDS, 0)
    with open(path, encoding="utf-8") as fh:
        rows = comment_lines(fh, kind)
    for ln, raw in rows:
        token = TOKEN.search(raw)
        if token:
            stats["標記 token"] += 1
            raw = raw[:token.start()] + raw[token.end():]
        elif WS.sub("", raw) in base:
            stats["基線原有"] += 1
            continue
        hit = MARKER.search(raw)
        if hit:
            stats["原行載荷"] += 1
            raw = raw[:hit.start()]
        text = WS.sub("", raw)
        if text:
            kept.append((ln, text))
    return kept, stats


def code_exempt(path, units, kind=""):
    """碼面豁免（全路徑同一邏輯、接在三型豁免之後）→ (保留之 units, {"span": 段數, "圍欄": 行數, "未閉合": [開啟行號]})。
    ①``` 圍欄（限 doc 註與塊註解）：註解文本 lstrip 後以三個反引號起首之行開啟、同一註解內（行號連續之註解行、空白註解行計入）下一個
      同形行關閉——標記行與其間各行整行不入分子分母；到註解邊界仍未關閉＝未閉合、該開啟行起照計並回報行號（寧紅勿漏）。
    ②行內 code span：同一註解行內成對反引號包夾之非空段換成 SEP——不入分子分母、命中亦不得跨 span 接起前後散文。"""
    with open(path, encoding="utf-8") as fh:
        rows = comment_rows(fh, kind)
    fenced, unclosed, start, prev = set(), [], None, None
    for ln, raw, doc in rows:
        if start is not None and ln != prev + 1:
            unclosed.append(start)
            start = None
        prev = ln
        if doc and raw.lstrip().startswith(FENCE):
            if start is None:
                start = ln
            else:
                fenced.update(range(start, ln + 1))
                start = None
    if start is not None:
        unclosed.append(start)
    kept, stats = [], {"span": 0, "圍欄": 0, "未閉合": unclosed}
    for ln, text in units:
        if ln in fenced:
            stats["圍欄"] += 1
            continue
        text, n = SPAN.subn(SEP, text)
        stats["span"] += n
        kept.append((ln, text))
    return kept, stats


def measure(p6, p5, rel, minlen, fork):
    """單檔量測 → (重疊比 %, 命中, 計量註解總字元, 豁免前註解行數, 三型豁免統計｜None, 碼面豁免統計)。
    `rel`（repo 根相對）首段為 base-web 者先三型豁免、其餘路徑零三型豁免（亦不讀源倉）；碼面豁免全路徑、在三型豁免之後套用。"""
    kind = kind_of(rel)
    raw = comment_units(p6, kind)
    if rel.parts[0] != BASEWEB:
        units, stats = raw, None
    else:
        units, stats = exempt_units(p6, read_baseline(fork, pathlib.PurePosixPath(*rel.parts[1:]).as_posix()), kind)
    units, code = code_exempt(p6, units, kind)
    pct, hits, total = compare(p6, p5, minlen, units)
    return pct, hits, total, len(raw), stats, code


def run(files, minlen, max_pct, root=ROOT, rev5=REV5, fork=FORK):
    rc, compared, parsed = 0, 0, 0
    for arg in files:
        p6 = pathlib.Path(arg).resolve()
        if not p6.is_file():
            print(f"!! {arg}：rev6 檔不存在", flush=True)
            return 2
        try:
            rel = p6.relative_to(root)
        except ValueError:
            print(f"!! {arg}：不在 repo 內", flush=True)
            return 2
        p5, via = rev5 / rel, ""
        if not p5.is_file() and rel.name.startswith(REV6_PREFIX):
            alt = rel.with_name(REV5_PREFIX + rel.name[len(REV6_PREFIX):])
            if (rev5 / alt).is_file():
                p5, via = rev5 / alt, f"（rev5 對應檔映射＝{alt.as_posix()}）"
            else:
                print(f"== {rel}：rev5 無對應檔（同相對路徑與 `{REV5_PREFIX}` 檔名映射皆缺席；n/a）", flush=True)
                continue
        if not p5.is_file():
            print(f"== {rel}：rev5 無對應檔（n/a）", flush=True)
            continue
        try:
            pct, hits, total, n_raw, stats, code = measure(p6, p5, rel, minlen, fork)
        except OverlapError as e:
            print(f"!! {rel}：{e}", flush=True)
            return 2
        compared += 1
        parsed += n_raw
        exempt = "" if stats is None else "；豁免 " + "／".join(f"{k} {v} 行" for k, v in stats.items())
        exempt += f"；碼面豁免 code span {code['span']} 段／圍欄 {code['圍欄']} 行"
        if code["未閉合"]:
            exempt += "；未閉合圍欄 " + "、".join(f"L{ln}" for ln in code["未閉合"]) + "（照計）"
        verdict = "超標" if pct >= max_pct else "ok"
        print(f"== {rel}{via}：{len(hits)} 段逐字重疊、佔本檔註解量 {pct:.1f}%（註解總量 {total}{exempt}；門檻 {minlen} 字元／上限 {max_pct:g}%）→ {verdict}", flush=True)
        for ln, length, frag in hits:
            print(f"   L{ln}（{length} 字元）：{frag[:110]}", flush=True)
        if pct >= max_pct:
            rc = 1
    # RL-0051：掃描面空集合即紅——量不到任何東西的「全 ok」是假綠（引數錯檔、或檔型不在本工具之四形解析面〔行首 `//` 類／行首 `/*` 塊註解／`.vue` 行首 `<!--`〕）。
    if compared == 0:
        print(f"!! 比對面為空：本次 {len(files)} 檔之 rev5 對應檔全缺席（全 n/a）——無一檔可比、不得回綠", flush=True)
        return 2
    if parsed == 0:
        print(f"!! 比對面為空：受比 {compared} 檔全體零可解析註解（本工具解析行首 `//`／`///`／`//!`、行首 `/*` 塊註解、`.vue` 行首 `<!--` HTML 註解，與 `.py`／`.sh`／`.bash` 之行首 `#` 與 docstring）——無一字可量、不得回綠", flush=True)
        return 2
    return rc


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture_git(repo, *args):
    """合成基線 repo 之 git：剝 `GIT_*`（同 read_baseline）＋壓掉全域 hooksPath／excludesFile／gpgsign（同 tools/fork-delta-lint.py 自測 fixture 形）。"""
    r = subprocess.run(["git", "-C", str(repo), "-c", "core.hooksPath=.git/no-hooks", "-c", "core.excludesFile=",
                        "-c", "commit.gpgsign=false", *args], capture_output=True, text=True, encoding="utf-8", env=git_env())
    if r.returncode != 0:
        raise OverlapError(f"合成基線 git {' '.join(args)} 失敗：{r.stderr.strip()}")


def _run_quiet(files, **roots):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = run(files, DEFAULT_MIN, DEFAULT_MAX_PCT, **roots)
    return rc, buf.getvalue()


def self_test():
    """合成樣本逐案自證；任一案敗＝rc 1、指名案名與實得值。
    量尺本體：同一段散文逐字搬運須判超標、改寫後須判 ok；識別字級短片段不計。
    base-web 三型豁免（樣本＝token＋散文＋`原行:` 同行之修改型真形）：全豁免正例一支＋「只拿掉一型之形」反例四支（其餘兩型照豁免、命中恰為
    被拿掉那型）＋標記行同行散文與 rev5 同文照計反例一支＋三型落在塊註解／HTML 註解內仍生效各一支；rust-api 同內容零三型豁免、碼面豁免照套
    且不讀源倉；LL-00012 洩漏 env 下仍讀得到基線；源倉不可讀 rc 2。比對面為空：全 n/a／全體零可解析註解 rc 2 各配一反例；豁免後零字元不算空面。
    解析四形：塊註解搬運超標／改寫 ok、單行 `/** */`、`.vue` HTML 註解搬運超標、`.py` 之 `#` 與真 docstring（BL-00080）；反例＝`.ts` 之 `<!--` 起首行、碼行內行中 `/*`。
    映射：`rev6-x`↔`rev5-x` 量得；反例＝無 `rev5-` 對應檔 n/a、非 `rev6-` 起首不映射（樣本剝前綴後恰對上在場之 `rev5-` 檔）。
    碼面豁免：span 豁免 ok／去反引號超標、span 不跨接、圍欄豁免（`///`／`//!` 與 JSDoc）、一般 `//` 與 `.vue` HTML 註解不成圍欄、未閉合圍欄照計並指名行號
    （其後另有註解行／檔內末段註解兩落點各一）；
    base-web 路徑 span 與三型豁免同檔（碼面豁免接其後：基線原有行與 `原行:` 載荷內之 span 不計）；
    塊註解內以 `//` 起首之續行不再判起首（雙斜線字元照收入量測面）。"""
    cases = []

    def case(name, ok, detail):
        cases.append((name, bool(ok), detail))

    with tempfile.TemporaryDirectory() as d:
        base = pathlib.Path(d).resolve()
        prose = "//! 這一段是刻意寫得夠長的模組說明散文，用來讓逐字搬運的比對結果超過四十字元的門檻並被本工具當場抓到而不是漏過去。\n"
        (base / "r5.rs").write_text(prose + "/// 次要說明：fn find_by_hash_for_update 走 FOR UPDATE。\npub fn a() {}\n", encoding="utf-8")
        (base / "copied.rs").write_text(prose + "pub fn a() {}\n", encoding="utf-8")
        (base / "rewritten.rs").write_text("//! 重寫過的說明：語意相同、用字不同。\n/// find_by_hash_for_update\npub fn a() {}\n", encoding="utf-8")
        pct_c, hits_c, _ = compare(base / "copied.rs", base / "r5.rs", DEFAULT_MIN)
        pct_r, hits_r, _ = compare(base / "rewritten.rs", base / "r5.rs", DEFAULT_MIN)
        case("搬運樣本判超標", pct_c >= DEFAULT_MAX_PCT and len(hits_c) == 1, f"{pct_c:.1f}%／{len(hits_c)} 段")
        case("改寫樣本判零重疊（識別字級短片段不計）", pct_r == 0.0 and not hits_r, f"{pct_r:.1f}%／{len(hits_r)} 段")

        # ── base-web 三型豁免 ──
        # rev6 樣本三行註解：我方散文／upstream 原註（基線有）／修改型標記行真形＝token＋我方散文＋`原行:` 載荷同一行（fork-delta-lint
        # 規定 `原行:` 與 token 同行）；rev5 同位標記行帶同軌道 token、前代散文與同載荷。
        root, r5root, fork = base / "rev6", base / "rev5", base / "fork"
        up = "// when the backend response code is in modalLogoutCodes, it means the user will be logged out by a modal"
        code = "const { data: loginToken, error } = await fetchLoginWithCaptcha(userName, password, captcha);"
        tok5 = "// [rev5-inline BASE-WEB-LOGIN-CAPTCHA-WIRING+ 003-auth-session START]"
        mine, lead = "// 我方重寫之說明：軟區附掛驗證碼欄。", "改呼 wrapper（我方散文）；"
        shared = "這段標記行上的前代散文刻意寫得超過四十字元門檻、且被逐字搬進 rev6 同一標記行，收窄後的豁免須照計判超標。"
        r5 = (f"{up}\n{tok5}\n// [rev5-inline BASE-WEB-LOGIN-CAPTCHA-WIRING(i) 003-auth-session] {shared}原行: {code}\n"
              "export const a = 1;\n")

        def rev6(track="[rev6-inline", payload="原行:", note=lead):
            return (f"{mine}\n{up}\n// {track} BASE-WEB-LOGIN-CAPTCHA-WIRING(i) 003-auth-session] {note}{payload} {code}\n"
                    "export const a = 1;\n")

        with_up = f"{up}\n{code}\n"
        # 三型豁免落在塊註解／HTML 註解內：同一組三行（我方散文／upstream 原註／token＋散文＋`原行:` 同行）改寫成 `/* */` 與 `.vue` `<!-- -->` 形，
        # 基線亦以同形承載 upstream 原註（基線經同一解析器取註解）。
        mine_txt, up_txt = mine[3:], up[3:]
        tok_line = f"[rev6-inline BASE-WEB-LOGIN-CAPTCHA-WIRING(i) 003-auth-session] {lead}原行: {code}"
        blk6 = f"/** {mine_txt} */\n/**\n * {up_txt}\n */\n/* {tok_line} */\nexport const a = 1;\n"
        htm6 = f"<template>\n  <!-- {mine_txt} -->\n  <!--\n    {up_txt}\n  -->\n  <!-- {tok_line} -->\n</template>\n"
        variants = {  # 檔名 → (rev6 內容, 基線內容｜None＝基線無此檔)
            "pos.ts": (rev6(), with_up),
            "neg_track.ts": (rev6(track="rev6-inline"), with_up),   # 缺 `[`＝不合 TOKEN
            "neg_payload.ts": (rev6(payload="參照:"), with_up),     # 非 `原行:`
            "neg_base.ts": (rev6(), f"{code}\n"),                   # 基線檔無該註解行（碼行同文不算）
            "neg_nofile.ts": (rev6(), None),                        # 基線無此檔（我方新檔）
            "neg_prose.ts": (rev6(note=shared), with_up),           # 標記行同行散文與 rev5 同文（三型照豁免）
            "allexempt.ts": (f"{up}\n{tok5.replace('[rev5-inline', '[rev6-inline')}\n", with_up),
            "pos_block.ts": (blk6, f"/**\n * {up_txt}\n */\n{code}\n"),
            "pos_html.vue": (htm6, f"<template>\n  <!-- {up_txt} -->\n</template>\n"),
        }
        for name, (text6, text_base) in variants.items():
            _write(root / BASEWEB / "src" / name, text6)
            _write(r5root / BASEWEB / "src" / name, r5)
            if text_base is not None:
                _write(fork / "src" / name, text_base)
        # base-web 碼面豁免與三型豁免同檔（碼面豁免接在三型豁免之後）：upstream 原註行（基線有）與 `原行:` 載荷各帶一段 code span、
        # 先被三型豁免剝掉＝其 span 不計；我方散文行之 span 照豁免（rev5 同位散文只差反引號內長識別字、不豁免即命中）。
        p1, p2 = "登入流程先呼叫", "取回會話列、再比對指紋與到期時間。"
        id5, id6 = "resolve_session_token_with_refresh_rotation_v5", "resolve_session_token_with_refresh_rotation_v6"
        up_span = "// the `fetchGetUserInfo` result is cached in the auth store until the token is refreshed"
        code_span = "const label = `${prefix}:${name}`;"
        _write(root / BASEWEB / "src" / "pos_span.ts",
               f"{up_span}\n// {p1}`{id6}`{p2}\n// [rev6-inline BASE-WEB-LOGIN-CAPTCHA-WIRING(i) 003-auth-session] {lead}原行: {code_span}\n"
               "export const a = 1;\n")
        _write(r5root / BASEWEB / "src" / "pos_span.ts", f"{up_span}\n// {p1}`{id5}`{p2}\n")
        _write(fork / "src" / "pos_span.ts", f"{up_span}\n{code}\n")
        _fixture_git(fork, "init", "-q")
        _fixture_git(fork, "checkout", "-q", "-b", BASELINE)
        _fixture_git(fork, "add", "-A")
        _fixture_git(fork, "-c", "user.name=co", "-c", "user.email=co@local", "commit", "-qm", "baseline")

        def m(name, top=BASEWEB, fork_path=fork):
            rel = pathlib.Path(top, "src", name)
            return measure(root / rel, r5root / rel, rel, DEFAULT_MIN, fork_path)

        all_one = dict.fromkeys(EXEMPT_KINDS, 1)
        pct, hits, total, n_raw, stats = m("pos.ts")[:5]
        want_total = len(WS.sub("", MARK.sub("", mine))) + len(WS.sub("", lead))
        case("base-web 三型全豁免→零重疊、豁免字元不入分母、標記行同行我方散文入分母",
             not hits and pct == 0.0 and total == want_total and n_raw == 3 and stats == all_one,
             f"{pct:.1f}%／{len(hits)} 段／總量 {total}（應 {want_total}）／豁免前 {n_raw} 行／豁免 {stats}")
        pct, hits, _t, _n, stats = m("neg_prose.ts")[:5]
        case("標記行同行散文反例：與 rev5 同文→照計判超標（token 與 `原行:` 載荷照豁免）",
             pct >= DEFAULT_MAX_PCT and hits and all("逐字搬進" in h[2] for h in hits) and stats == all_one,
             f"{pct:.1f}%／命中 {[h[2][:48] for h in hits]}／豁免 {stats}")
        for name, kind, needle, label in (
            ("neg_track.ts", "標記 token", "BASE-WEB-LOGIN-CAPTCHA-WIRING", "標記 token 反例：缺 `[` 之 token 不合 TOKEN→照計"),
            ("neg_payload.ts", "原行載荷", "fetchLoginWithCaptcha", "原行載荷反例：`參照:` 非 `原行:`→照計"),
            ("neg_base.ts", "基線原有", "modalLogoutCodes", "基線原有反例：基線檔無該註解行→照計"),
            ("neg_nofile.ts", "基線原有", "modalLogoutCodes", "基線原有反例：基線無此檔（我方新檔）→照計"),
        ):
            pct, hits, _t, _n, stats = m(name)[:5]
            want = {k: 0 if k == kind else 1 for k in EXEMPT_KINDS}
            case(label, pct >= DEFAULT_MAX_PCT and hits and all(needle in h[2] for h in hits) and stats == want,
                 f"{pct:.1f}%／命中 {[h[2][:48] for h in hits]}／豁免 {stats}（應 {want}）")

        # rust-api 樣本＝base-web 全豁免正例同內容＋一行帶 code span 之註解：三型一型都不豁免（命中與不豁免量測逐段全等）、
        # 碼面豁免照套（總量恰少 span 字元）；源倉路徑指向不存在處、讀了即 OverlapError。
        rel_rs, span_rs = pathlib.Path("rust-api", "src", "pos.rs"), "`find_by_hash_for_update`"
        _write(root / rel_rs, rev6() + f"// 取列走 {span_rs}。\n")
        _write(r5root / rel_rs, r5)
        try:
            got = measure(root / rel_rs, r5root / rel_rs, rel_rs, DEFAULT_MIN, base / "no-such-fork")
        except OverlapError as e:  # 讀了源倉＝本案失守（記為案敗、不讓例外吞掉其餘各案）
            got = (0.0, None, None, None, f"OverlapError：{e}")
        plain = compare(root / rel_rs, r5root / rel_rs, DEFAULT_MIN)
        want_code = {"span": 1, "圍欄": 0, "未閉合": []}
        case("rust-api 零三型豁免（命中與不豁免量測全等）、碼面豁免照套（總量恰少 span 字元）、不讀源倉（源倉不在場亦不報錯）",
             got[4] is None and got[1] == plain[1] and got[2] == plain[2] - len(span_rs) and got[5:] == (want_code,)
             and got[0] >= DEFAULT_MAX_PCT,
             f"實得 {got[0]:.1f}%／總量 {got[2]}（應 {plain[2] - len(span_rs)}）／三型 {got[4]}／碼面 {got[5:]}；不豁免 {plain[0]:.1f}%")

        saved = {k: os.environ.get(k) for k in ("GIT_DIR", "GIT_INDEX_FILE")}
        os.environ["GIT_DIR"], os.environ["GIT_INDEX_FILE"] = str(base / "leaked.git"), str(base / "leaked.index")
        try:
            leaked_rc = subprocess.run(["git", "-C", str(fork), "rev-parse", "--verify", "-q", BASELINE],
                                       capture_output=True, text=True).returncode
            try:
                leaked = m("pos.ts")[4]
            except OverlapError as e:  # 讀不到基線＝本案失守（記為案敗）
                leaked = f"OverlapError：{e}"
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        case("LL-00012：外層 GIT_DIR／GIT_INDEX_FILE 洩漏下仍讀得到基線（同 env 未剝之 git 讀不到）",
             leaked_rc != 0 and leaked == all_one, f"未剝 rc {leaked_rc}／豁免 {leaked}")

        roots = {"root": root, "rev5": r5root, "fork": fork}
        rc, out = _run_quiet([str(root / BASEWEB / "src" / "pos.ts")], root=root, rev5=r5root, fork=base / "no-such-fork")
        case("base-web 路徑源倉不可讀→rc 2 指名（不退回不豁免量測）", rc == 2 and "源倉" in out, out.strip())

        # ── 比對面為空 ──
        _write(root / BASEWEB / "src" / "newonly.ts", f"{mine}\n")  # rev5 無對應檔
        for rel, text6, text5 in (("rust-api/src/clean.rs", "//! 重寫過的說明：語意相同、用字不同。\npub fn a() {}\n", prose),
                                  ("rust-api/src/bare.rs", "pub fn a() {}\n", "pub fn a() {}\n")):
            _write(root / rel, text6)
            _write(r5root / rel, text5)

        def rc_of(*rels):
            return _run_quiet([str(root / r) for r in rels], **roots)

        # ── `#` 行註解與 docstring 解析（BL-00080）──
        shared = "這段說明兩代逐字相同、長度足以越過四十字元門檻、用來證明量尺真的量得到 python 註解面。"
        py6 = ('#!/usr/bin/env python3\n'
               '# ' + shared + '\n'
               'def f():\n'
               '    ' + '"' * 3 + shared + '"' * 3 + '\n'
               '    return 1\n')
        py5 = ('#!/usr/bin/env python3\n'
               '# ' + shared + '\n'
               'def f():\n'
               '    ' + '"' * 3 + shared + '"' * 3 + '\n'
               '    return 2\n')
        _write(root / "tools/hash.py", py6)
        _write(r5root / "tools/hash.py", py5)
        rc, out = rc_of("tools/hash.py")
        case("BL-00080：`.py` 之 `#` 行註解與 docstring 入量測面（不再回「比對面為空」）、逐字重疊真的量到",
             rc == 1 and "比對面為空" not in out and "100" in out, out.strip())

        # shebang 不收：兩代恆同字面，計入只會虛增重疊
        py6b = '#!/usr/bin/env python3\n# 本檔說明與前代完全不同、無任何逐字重疊可言、純為驗證 shebang 不計入。\ndef g():\n    return 1\n'
        py5b = '#!/usr/bin/env python3\n# 前代寫的是另一套字句、刻意與現行版零共用片段、用以確認量尺不虛報。\ndef g():\n    return 2\n'
        _write(root / "tools/hashb.py", py6b)
        _write(r5root / "tools/hashb.py", py5b)
        rc, out = rc_of("tools/hashb.py")
        # ★判準打在唯一會動的量：shebang（24 字元）若被收入，註解總字元會多 24（mb4t review L1-3）
        units = comment_units(str(root / "tools/hashb.py"), "py")
        total = sum(len(t) for _, t in units)
        case("BL-00080 反例：首行 shebang 不收（註解總字元不含 shebang；收入即多 24 字元）",
             rc == 0 and "比對面為空" not in out and total == 37 and
             all("usr/bin/env" not in t for _, t in units), f"rc {rc}／總字元 {total}／{units}")

        # ★吞碼反例（mb4t review L1-2）：一般三引號字串的**收尾行**不得被當 docstring 開啟，
        # 否則其後碼行整段被吞入量測面直到下一個三引號或檔尾（實測曾使一支工具虛報 97.4%）
        swallow = ['SQL = ' + '"' * 3, 'SELECT 1', '"' * 3, 'TOKEN = 1', 'def f(): pass']
        case("BL-00080 反例：非 docstring 之三引號收尾行不開啟註解、其後碼行不入量測面",
             comment_rows(swallow, "py") == [], repr(comment_rows(swallow, "py")))
        # 正例：真 docstring（模組／函式首個字串陳述）照收
        real_doc = ['"' * 3 + '模組說明' + '"' * 3, 'def f():', '    ' + '"' * 3 + '函式說明' + '"' * 3, '    return 1']
        got = [(ln, t) for ln, t, _ in comment_rows(real_doc, "py")]
        case("BL-00080 正例：模組與函式的真 docstring 照收（行號與去界符後文字）",
             got == [(1, "模組說明"), (3, "函式說明")], repr(got))   # 前導空白同 `//` 家族一併剝除
        # 語法不合本直譯器＝退回只取行首 `#`（寧漏勿吞）
        broken = ['# 說明行', 'def f(:', '    ' + '"' * 3 + '不該被吞' + '"' * 3]
        case("BL-00080：`.py` 語法不合時退回只取行首 `#`（絕不把碼行當註解）",
             comment_rows(broken, "py") == [(1, " 說明行", False)], repr(comment_rows(broken, "py")))

        # 方言隔離：非 .py／.sh 之 `#` 起首行不當註解
        ts6 = "# " + shared + "\nexport const a = 1;\n"
        _write(root / "rust-api/src/hashlike.ts", ts6)
        _write(r5root / "rust-api/src/hashlike.ts", ts6)
        rc, out = rc_of("rust-api/src/hashlike.ts")
        case("BL-00080 反例：`.ts` 之 `#` 起首行不當註解（方言隔離）→零可解析註解、rc 2 比對面為空",
             rc == 2 and "比對面為空" in out, out.strip())

        rc, out = rc_of("base-web/src/newonly.ts")
        case("比對面為空：本次引數之 rev5 對應檔全缺席→rc 2", rc == 2 and "比對面為空" in out and "全缺席" in out, out.strip())
        rc, out = rc_of("base-web/src/newonly.ts", "rust-api/src/clean.rs")
        case("反例：n/a 檔旁有一檔可比→rc 0（單檔 n/a 照舊不計超標）", rc == 0 and "n/a" in out and "比對面為空" not in out, out.strip())
        rc, out = rc_of("rust-api/src/bare.rs")
        case("比對面為空：受比檔全體零可解析註解→rc 2", rc == 2 and "比對面為空" in out and "零可解析註解" in out, out.strip())
        rc, out = rc_of("rust-api/src/bare.rs", "rust-api/src/clean.rs")
        case("反例：零註解檔旁有一檔有註解→rc 0", rc == 0 and "比對面為空" not in out, out.strip())
        rc, out = rc_of("base-web/src/allexempt.ts")
        case("豁免後零字元不算空面（豁免前有可解析註解）→rc 0", rc == 0 and "註解總量 0" in out and "比對面為空" not in out, out.strip())

        # 新案一律經 guard：受測物拋例外記為該案敗、不中斷其餘各案。
        def guard(name, fn):
            try:
                ok, detail = fn()
            except Exception as e:  # noqa: BLE001——自測收斂點：例外即案敗、指名型別
                ok, detail = False, f"例外 {type(e).__name__}：{e}"
            case(name, ok, detail)

        def cmp_pair(name6, text6, text5):
            p6, p5 = base / "parse" / name6, base / "parse" / ("r5-" + name6)
            _write(p6, text6)
            _write(p5, text5)
            return compare(p6, p5, DEFAULT_MIN)

        def z(text):
            return WS.sub("", text)

        # ── 解析面四形之前三形：塊註解（含單行 `/** */`）／`.vue` HTML 註解；射程外反例（第四形＝`.py`／`.sh` 之 `#` 與 docstring，見下段）──
        blk = ("這段塊註解散文刻意寫得超過四十字元門檻，跨兩行以星號續寫，", "逐字搬運時須被量尺當場抓到判超標、不得因星號續行而漏量。")
        blk5 = f"/**\n * {blk[0]}\n * {blk[1]}\n */\nexport const a = 1;\n"

        def t_block_copied():
            pct, hits, total = cmp_pair("blk.ts", blk5, blk5)
            return (pct >= DEFAULT_MAX_PCT and len(hits) == 1 and total == len(z("".join(blk)))
                    and "*" not in hits[0][2]), f"{pct:.1f}%／{len(hits)} 段／總量 {total}（應 {len(z(''.join(blk)))}）"

        def t_block_rewritten():
            pct, hits, total = cmp_pair("blk_rw.ts", "/**\n * 改寫後的說明：語意相同、用字不同。\n */\nexport const a = 1;\n", blk5)
            return pct == 0.0 and not hits and total == len(z("改寫後的說明：語意相同、用字不同。")), f"{pct:.1f}%／{len(hits)} 段／總量 {total}"

        one, tail = ("單行塊註解之散文同樣刻意寫得超過四十字元門檻，收尾記號之後同行的碼一律不入量測面。",
                     "這句只在收尾記號後之碼字面裡出現、若被誤收即改變註解總量並多出一段命中。")

        def t_single_line():
            pct, hits, total = cmp_pair("one.ts", f"  /** {one} */ export const s = '{tail}';\n", f"// {one}\n// {tail}\n")
            return (pct == 100.0 and len(hits) == 1 and hits[0][2] == z(one) and total == len(z(one))), \
                f"{pct:.1f}%／命中 {[h[2][:40] for h in hits]}／總量 {total}（應 {len(z(one))}）"

        htm = ("樣板內之單行 HTML 註解散文刻意寫得超過四十字元門檻、逐字搬運時須被量尺判超標。", "多行 HTML 註解之第一行散文，",
               "與第二行接起來同樣刻意超過四十字元門檻、逐字搬運時也須被量到。")
        vue5 = f"<template>\n  <!-- {htm[0]} -->\n  <div>\n    <!--\n      {htm[1]}\n      {htm[2]}\n    -->\n  </div>\n</template>\n"

        def t_vue_html():
            pct, hits, total = cmp_pair("tpl.vue", vue5, vue5)
            return (pct >= DEFAULT_MAX_PCT and len(hits) == 2 and total == len(z("".join(htm)))), \
                f"{pct:.1f}%／{len(hits)} 段／總量 {total}（應 {len(z(''.join(htm)))}）"

        def t_ts_no_html():
            pct, hits, total = cmp_pair("tpl.ts", f"const html = `\n  <!-- {htm[0]} -->\n`;\n// 短註。\n", f"// {htm[0]}\n")
            return not hits and total == len("短註。"), f"{pct:.1f}%／命中 {[h[2][:40] for h in hits]}／總量 {total}（應 3）"

        def t_inline_block():
            pct, hits, total = cmp_pair("inline.ts", f"const a = 1; /* {one} */\nfoo(/** {one} */ 1);\n// 短註。\n", f"// {one}\n")
            return not hits and total == len("短註。"), f"{pct:.1f}%／命中 {[h[2][:40] for h in hits]}／總量 {total}（應 3）"

        guard("塊註解（多行、星號續行）逐字搬運判超標：星號與首尾記號不入量測面", t_block_copied)
        guard("塊註解改寫判 ok", t_block_rewritten)
        guard("單行 `/** */` 收進量測面、`*/` 之後同行碼不收", t_single_line)
        guard("`.vue` HTML 註解（單行＋多行）逐字搬運判超標", t_vue_html)
        guard("反例：`.ts` 內 `<!--` 起首行不解析", t_ts_no_html)
        guard("反例：碼行之行中 `/*`／`/** */` 不解析", t_inline_block)

        def t_exempt_in(name, want_raw):
            def fn():
                pct, hits, total, n_raw, stats = m(name)[:5]
                want_total = len(z(mine_txt)) + len(z(lead))
                return (not hits and pct == 0.0 and total == want_total and n_raw == want_raw and stats == all_one), \
                    f"{pct:.1f}%／{len(hits)} 段／總量 {total}（應 {want_total}）／豁免前 {n_raw} 行（應 {want_raw}）／豁免 {stats}"
            return fn

        guard("base-web 三型豁免落在塊註解內仍生效（基線亦以塊註解承載 upstream 原註）", t_exempt_in("pos_block.ts", 3))
        guard("base-web 三型豁免落在 `.vue` HTML 註解內仍生效（基線亦以 HTML 註解承載 upstream 原註）", t_exempt_in("pos_html.vue", 3))

        # ── rev5 對應檔映射：同相對路徑缺席且檔名 `rev6-` 起首→同目錄 `rev5-` 接其後同名 ──
        copied = f"// {blk[0]}{blk[1]}\n"
        # 非 `rev6-` 起首之反例樣本須剝前綴後恰對上在場之 `rev5-auth.ts`：`rev7-auth.ts`（同長度他前綴）／`rev6_auth.ts`（缺連字號）——
        # 前綴閘拿掉或放寬即被錯映而量得；剝不出在場檔名之樣本（如 `auth.ts`→`rev5-ts`）閘拿掉照樣 n/a、測不到閘。
        for rel, text6, text5 in (("rev6-x.ts", copied, "rev5-x.ts"), ("rev6-y.ts", copied, None),
                                  ("rev7-auth.ts", copied, "rev5-auth.ts"), ("rev6_auth.ts", copied, None)):
            _write(root / BASEWEB / "src" / "api" / rel, text6)
            if text5:
                _write(r5root / BASEWEB / "src" / "api" / text5, copied)

        def t_map(names, want_rc, must, must_not):
            def fn():
                rc, out = rc_of(*(f"base-web/src/api/{n}" for n in names))
                return rc == want_rc and all(s in out for s in must) and not any(s in out for s in must_not), f"rc {rc}：{out.strip()}"
            return fn

        guard("映射正例：`rev6-x.ts` 同路徑缺席→量 `rev5-x.ts`（非 n/a、輸出明示映射來源）",
              t_map(("rev6-x.ts",), 1, ("base-web/src/api/rev5-x.ts", "映射", "超標"), ("n/a",)))
        guard("映射反例：`rev6-y.ts` 無 `rev5-y.ts`→n/a（全缺席 rc 2 照舊）", t_map(("rev6-y.ts",), 2, ("n/a", "全缺席"), ("映射＝",)))
        guard("映射反例：非 `rev6-` 起首之 `rev7-auth.ts`／`rev6_auth.ts` 不映射（剝前綴恰對上之 `rev5-auth.ts` 在場亦 n/a）",
              t_map(("rev7-auth.ts", "rev6_auth.ts"), 2, ("n/a", "全缺席"), ("rev5-auth.ts", "映射＝")))

        # ── 碼面豁免（全路徑；rev5 文本不豁免）：行內 code span／註解內 ``` 圍欄 ──
        def rs(name, text6, text5):
            rel = pathlib.Path("rust-api", "src", name)
            _write(root / rel, text6)
            _write(r5root / rel, text5)
            return measure(root / rel, r5root / rel, rel, DEFAULT_MIN, base / "no-such-fork")

        span5 = f"/// {p1}`{id5}`{p2}\npub fn a() {{}}\n"

        def t_span_ok():
            pct, hits, total, _n, _s, code = rs("span_ok.rs", f"/// {p1}`{id6}`{p2}\npub fn a() {{}}\n", span5)
            return (pct == 0.0 and not hits and total == len(z(p1 + p2)) and code["span"] == 1), \
                f"{pct:.1f}%／命中 {[h[2][:48] for h in hits]}／總量 {total}（應 {len(z(p1 + p2))}）／碼面 {code}"

        def t_span_bare():
            pct, hits, total, _n, _s, code = rs("span_bare.rs", f"/// {p1}{id6}{p2}\npub fn a() {{}}\n", span5)
            return pct >= DEFAULT_MAX_PCT and hits and code["span"] == 0, f"{pct:.1f}%／命中 {[h[2][:48] for h in hits]}／碼面 {code}"

        q1, q2 = "跨接反例之前半段散文刻意壓在門檻以內，", "後半段接上去合起來才超過門檻、且與前代逐字同文。"

        def t_span_no_bridge():
            pct, hits, total, _n, _s, code = rs("bridge.rs", f"/// {q1}`x`{q2}\npub fn a() {{}}\n", f"/// {q1}{q2}\n")
            return (len(z(q1)) < DEFAULT_MIN and len(z(q2)) < DEFAULT_MIN and len(z(q1 + q2)) >= DEFAULT_MIN and not hits
                    and total == len(z(q1 + q2)) and code["span"] == 1), \
                f"{pct:.1f}%／命中 {[h[2][:48] for h in hits]}／總量 {total}／前後段 {len(z(q1))}＋{len(z(q2))}／碼面 {code}"

        code1 = 'let bogus = server::envelope::Res::<()> { data: None, code: "9999".to_string() };'
        code2 = 'assert_eq!(ctx.real_ip(), "203.0.113.7", "合法 X-Real-IP 須原樣取回");'
        fence5 = f"/// ```compile_fail\n/// {code1}\n/// {code2}\n/// ```\n"

        def t_fence():
            text6 = f"/// 以下為編譯失敗示例。\n/// ```compile_fail\n/// {code1}\n///\n/// {code2}\n/// ```\npub fn a() {{}}\n"
            pct, hits, total, _n, _s, code = rs("fence.rs", text6, fence5)
            jsdoc = f"/**\n * 用法示例：\n *   ```ts\n *   {code1}\n *   ```\n */\nexport const a = 1;\n"
            pct_j, hits_j, total_j, _n, _s, code_j = rs("fence.ts", jsdoc, fence5)
            # `//!`（inner doc）圍欄：doc 註判定拿掉 `//!` 即不成圍欄、碼行照計命中。
            inner = f"//! 模組層示例：\n//! ```\n//! {code1}\n//! ```\npub fn a() {{}}\n"
            pct_i, hits_i, total_i, _n, _s, code_i = rs("fence_inner.rs", inner, fence5)
            return (not hits and total == len(z("以下為編譯失敗示例。")) and code == {"span": 0, "圍欄": 4, "未閉合": []}
                    and not hits_j and total_j == len(z("用法示例：")) and code_j == {"span": 0, "圍欄": 3, "未閉合": []}
                    and not hits_i and total_i == len(z("模組層示例：")) and code_i == {"span": 0, "圍欄": 3, "未閉合": []}), \
                (f"`///` {pct:.1f}%／命中 {len(hits)}／總量 {total}／碼面 {code}；JSDoc {pct_j:.1f}%／命中 {len(hits_j)}／總量 {total_j}／碼面 {code_j}；"
                 f"`//!` {pct_i:.1f}%／命中 {len(hits_i)}／總量 {total_i}／碼面 {code_i}")

        def t_fence_plain():
            pct, hits, total, _n, _s, code = rs("fence_plain.rs", f"// 一般註解。\n// ```\n// {code1}\n// ```\npub fn a() {{}}\n", fence5)
            return (pct >= DEFAULT_MAX_PCT and any(h[2] in z(code1) for h in hits) and code == {"span": 0, "圍欄": 0, "未閉合": []}), \
                f"{pct:.1f}%／命中 {[h[2][:48] for h in hits]}／碼面 {code}"

        # 未閉合圍欄兩個落點：L2＝其後另有註解行（由下一段註解之邊界判出）；L10＝檔內末段註解（其後再無註解行、只剩碼行——
        # 由迴圈收尾判出，不必是字面 EOF）。
        unclosed6 = (f"/// 未閉合示例的開頭說明。\n/// ```\n/// {code1}\npub fn a() {{}}\n"
                     "/// ```\n/// 第二段註解的圍欄內文。\n/// ```\npub fn b() {}\n"
                     f"/// 檔內末段註解的說明。\n/// ```\n/// {code2}\npub fn c() {{}}\n")

        def t_fence_unclosed():
            pct, hits, total, _n, _s, code = rs("unclosed.rs", unclosed6, fence5)
            rc, out = rc_of("rust-api/src/unclosed.rs")
            return (pct >= DEFAULT_MAX_PCT and any(h[2] in z(code1) for h in hits) and any(h[2] in z(code2) for h in hits)
                    and code == {"span": 0, "圍欄": 3, "未閉合": [2, 10]}
                    and "未閉合圍欄 L2、L10" in out and "碼面豁免" in out and rc == 1), \
                f"{pct:.1f}%／命中 {[h[2][:48] for h in hits]}／碼面 {code}／rc {rc}：{out.strip()}"

        guard("code span 豁免：與 rev5 同文、差異只在反引號內長識別字→ok（span 不入分子分母）", t_span_ok)
        guard("code span 反例：同一文本去反引號→超標（rev5 文本不做碼面豁免）", t_span_bare)
        guard("code span 不跨接：兩段各 <40 字元散文經 span 相隔、合起來與 rev5 同文仍不命中", t_span_no_bridge)
        guard("``` 圍欄豁免（`///`、`//!` 與 JSDoc 塊註解各一）：標記行與其間各行不入分子分母（圍欄內空白註解行不斷註解邊界）", t_fence)
        guard("反例：一般 `//` 註解內之 ``` 不成圍欄（圍欄限 doc 註與塊註解）→照計", t_fence_plain)
        guard("未閉合圍欄不豁免（其後另有註解與檔內末段註解兩落點各一；照計判超標、輸出指名開啟行號）；圍欄不跨註解邊界配對", t_fence_unclosed)

        def t_fence_html():
            text6 = f"<template>\n  <!-- 樣板示例：\n  ```\n  {code1}\n  ```\n  -->\n</template>\n"
            pct, hits, total, _n, _s, code = rs("fence_html.vue", text6, fence5)
            return (pct >= DEFAULT_MAX_PCT and any(h[2] in z(code1) for h in hits) and code == {"span": 0, "圍欄": 0, "未閉合": []}), \
                f"{pct:.1f}%／命中 {[h[2][:48] for h in hits]}／碼面 {code}"

        guard("反例：`.vue` HTML 註解內之 ``` 不成圍欄（圍欄限 doc 註與塊註解）→照計", t_fence_html)

        def t_bw_span():
            pct, hits, total, n_raw, stats, code = m("pos_span.ts")
            want_total = len(z(p1 + p2)) + len(z(lead))
            return (not hits and pct == 0.0 and total == want_total and n_raw == 3 and stats == all_one
                    and code == {"span": 1, "圍欄": 0, "未閉合": []}), \
                f"{pct:.1f}%／命中 {[h[2][:48] for h in hits]}／總量 {total}（應 {want_total}）／豁免前 {n_raw} 行／三型 {stats}／碼面 {code}"

        guard("base-web 路徑碼面豁免照套且接在三型豁免之後（span 豁免→零命中；基線原有行與 `原行:` 載荷內之 span 先被三型剝掉、不計段數）",
              t_bw_span)

        # 塊註解內之行不再判起首：續行以 `//` 起首時仍是塊註解內文（不剝雙斜線、不改 doc 判定）——重判起首即少收兩字元。
        inner_slash = "塊註解內之續行以雙斜線起首時仍屬塊註解內文、不再重判起首，雙斜線字元照收入量測面。"

        def t_block_inner_slash():
            pct, hits, total = cmp_pair("blk_slash.ts", f"/*\n// {inner_slash}\n*/\nexport const a = 1;\n", "// 無關之前代說明。\n")
            want = len(z("//" + inner_slash))
            return (not hits and total == want), f"{pct:.1f}%／命中 {len(hits)}／總量 {total}（應 {want}）"

        guard("塊註解內以 `//` 起首之續行不再判起首（雙斜線字元照收入量測面）", t_block_inner_slash)

    failed = [c for c in cases if not c[1]]
    for i, (name, ok, detail) in enumerate(cases, 1):
        print(f"comment-overlap test {'✓' if ok else '✗'} 案{i} {name}", flush=True)
        if not ok:
            print(f"    實得：{detail}", flush=True)
    if failed:
        print(f"comment-overlap test：{len(failed)}／{len(cases)} 案敗", flush=True)
        return 1
    print(f"comment-overlap test：ok（{len(cases)} 案全綠）", flush=True)
    return 0


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "test":
        return self_test()
    ap = argparse.ArgumentParser(description="rev5↔rev6 註解逐字重疊核")
    ap.add_argument("files", nargs="+", help="rev6 檔路徑（相對 repo 根或絕對）")
    ap.add_argument("--min", type=int, default=DEFAULT_MIN, help=f"共同子字串門檻字元數（預設 {DEFAULT_MIN}）")
    ap.add_argument("--max-pct", type=float, default=DEFAULT_MAX_PCT, help=f"逐檔重疊比上限 %%（預設 {DEFAULT_MAX_PCT:g}）")
    a = ap.parse_args()
    return run(a.files, a.min, a.max_pct)


if __name__ == "__main__":
    sys.exit(main())
