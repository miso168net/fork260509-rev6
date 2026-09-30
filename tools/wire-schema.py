#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/wire-schema.py — 契約機器化：typings→JSON Schema 快照抽取（python 標準庫、單檔、自帶測試）

隨遷工具（承 rev5:tools/wire-schema.py 逐字承襲、座標同名核對零改：compose 兩檔名／`base-web` 服務名／
`-w /app`／快照路徑／TYPINGS_GLOB／TSJS 釘版；RULES 名詞段「隨遷工具」）。rev6 拍板＝002 刀 clarify Q5、
ADR-00019「容器依賴型碼面閘之環境缺席語意＝具名跳過、工具缺席＝fail-loud」（名冊＝RUNBOOK §12 碼面閘表）。

子命令：
  extract   base-web 容器內 npx 抽取 typings → draft-07 JSON Schema 快照，
            原子替換寫 rust-api/server/tests/fixtures/wire-schema.json（需 stack 在跑）
  check     先跑跨子庫純讀檔錨兩腿（BL-00109 qs 前提；ADR-00044 決定 8 保留路由名對賬）——無條件、
            先於收窄與容器探測、不觸 docker／git，任一違規＝2；再重抽 typings 至暫存路徑、與工作樹
            快照 byte 比對（rev4:B-128 drift 閘；絕不覆寫快照）。--staged-gate＝pre-commit 專用收窄：
            兩側 pin 區間皆零變動才跳過重抽比對（base-web 區間零 typings 變動＋rust-api 區間零快照
            變動）。容器不可用＝警告＋0 放行；容器可用但重抽失敗／不一致＝2
  test      跑自帶測試（unittest、離線可跑）

失敗語意：stack 不在／抽取工具非零退出＝非零退出（2）＋stderr 提示啟動命令；抽取輸出
非合法 JSON＝不寫檔（防部分結果）；原子替換＝同目錄 temp 寫入後 os.replace；輸出確定性
（無產生時點欄位、同源重抽 byte 一致）。唯讀鐵則：npx 一次性、不碰 base-web 工作樹／
package.json／pnpm lock；前端 porcelain 前後皆空。用法錯誤走 exit 64（EX_USAGE）。

lineage：rev4:003-wire-foundation（契約＝contracts/contract-machinery.md §1、機器基準＝data-model.md §3、
抽取工具實測與釘版＝research.md R1）→ rev5:002-system-settings U7（`--strictNullChecks`）→ rev6 002 刀
（docs/ops/reference-src/code-gate-contracts.md §1、§2；rc 慣例＝RUNBOOK §12）→ rev6 005 刀 U11（check 前置之跨子庫
錨兩腿；該刀 spec FR-057、research R10）。
"""
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 抽取工具釘版（rev4:research R1；npx 一次性、不進任何 manifest）。
TSJS_VERSION = "0.67.4"
# typings 抽取檔集（rev4:research R1：api 四檔＋common.d.ts 的 utility 命名空間）。
TYPINGS_GLOB = "src/typings/{common,api/*}.d.ts"
# 抽取型別選擇（全型別）與旗標（容忍 .d.ts 單編噪音＋required 欄完整＋nullability 忠實）。
# ★--strictNullChecks 不可省（rev5:002-system-settings U7 實證、rev4→rev5 差異點）：不帶它時
# typescript-json-schema 會把 `string | null` 這類聯合型的 **null 分支整個吃掉**，
# 產出 {"type": "string"}——快照遂對「null 是合法值」一律低報。rev5 實測影響面不限該刀新型：
# 補上旗標後 7 個 definition 改變，含 upstream 既有 typings 的 Api.Common.CommonRecord、
# Api.SystemManage.{Menu,Role,RoleSearchParams,User,UserSearchParams}（例：RoleSearchParams
# 的 current／roleName 由 "string" 變 ["null","string"]）。快照是契約測試的裁判基準，
# 基準對 nullability 說謊，rust 側就得為每個 nullable 欄手工豁免、機器化的價值即打折。
# ★rev4:tools/wire-schema.py 同樣未帶此旗標——屬承襲缺陷、rev5 於其 002 刀修正（rev5:ADR 0019
# 防回歸條款的反向適用：rev4 的形不是只能照抄，查出是缺陷就改，並記為差異點）；rev6 照 rev5 形承襲。
TSJS_TYPE = "*"
TSJS_FLAGS = ["--ignoreErrors", "--required", "--strictNullChecks"]

# base-web 容器內執行前綴：dev stack 的 base-web 服務、cwd＝/app。
COMPOSE = ["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.dev.yml"]
BASE_WEB_EXEC = COMPOSE + ["exec", "-T", "-w", "/app", "base-web"]

# 快照輸出路徑（追蹤、隨 rust-api worktree；rev6 002 刀 `docs/ops/reference-src/code-gate-contracts.md` §2；
# 首抽已隨 002 刀 U3 之 base-web typings 新檔落地；base-web 容器可用而快照缺席時 check 走 rc 2 fail-loud——
# 容器不可用先具名跳過 rc 0、不讀快照＝ADR-00019 決定 2）。
OUTPUT_PATH = os.path.join("rust-api", "server", "tests", "fixtures", "wire-schema.json")

# stack 啟動提示（fail-loud 補救命令）。
START_HINT = "docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d"


class ExtractError(Exception):
    """抽取失敗（stack 不在／docker 缺／npx 非零）——走非零退出、絕不寫部分結果。"""


def build_npx_command():
    """組裝容器內 npx 抽取命令字串（釘版、檔集、型別、旗標——rev4:research R1 逐字）。"""
    return (
        f'npx -y typescript-json-schema@{TSJS_VERSION} '
        f'"{TYPINGS_GLOB}" "{TSJS_TYPE}" ' + " ".join(TSJS_FLAGS)
    )


def build_extract_argv():
    """完整 docker compose exec argv：base-web 容器 /app cwd 跑 `sh -c '<npx>'`。"""
    return BASE_WEB_EXEC + ["sh", "-c", build_npx_command()]


def _run_capture(argv):
    """跑 argv、capture stdout/stderr（text）；回 subprocess.CompletedProcess。"""
    return subprocess.run(argv, capture_output=True, text=True, cwd=REPO_ROOT)


def extract_schema(run=_run_capture, hint=None):
    """跑容器內抽取 → 回 JSON Schema 文字（stdout）。

    失敗（docker 缺＝OSError／stack 不在＝非零退出）＝raise ExtractError（附補救提示）；
    絕不回部分結果。`run` 可注入（離線測試用）；`hint` 可覆寫提示尾巴——check 分支
    probe 已證容器可用、預設「起 stack」提示對其為無效補救、須換自屬句。"""
    argv = build_extract_argv()
    try:
        proc = run(argv)
    except OSError as ex:
        tail = hint or f"dev stack 未啟動？請先跑：{START_HINT}"
        raise ExtractError(f"無法執行 docker（{ex}）——{tail}")
    if proc.returncode != 0:
        reason = (proc.stderr or proc.stdout or "").strip() or f"退出碼 {proc.returncode}"
        tail = hint or f"確認 dev stack 在跑：{START_HINT}"
        raise ExtractError(f"typings 抽取失敗（{reason}）——{tail}")
    return proc.stdout


def atomic_write(path, content):
    """原子替換：同目錄 temp 寫入後 os.replace——絕不留部分結果／temp 殘留。"""
    abs_path = path if os.path.isabs(path) else os.path.join(REPO_ROOT, path)
    directory = os.path.dirname(abs_path)
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".wire-schema.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        os.replace(tmp, abs_path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def cmd_extract():
    """extract 子命令：抽取 → 驗合法 JSON → 原子替換寫 OUTPUT_PATH。

    成功 0；stack 不在／npx 非零／輸出非 JSON＝2＋stderr 指名原因與補救命令。"""
    try:
        schema_text = extract_schema()
    except ExtractError as ex:
        print(f"[extract] {ex}", file=sys.stderr)
        return 2
    try:
        parsed = json.loads(schema_text)
    except json.JSONDecodeError as ex:
        print(f"[extract] 抽取輸出非合法 JSON（{ex}）——不寫檔（防部分結果）", file=sys.stderr)
        return 2
    definitions = parsed.get("definitions") if isinstance(parsed, dict) else None
    if not isinstance(definitions, dict) or not definitions:
        print("[extract] 抽取輸出缺非空 definitions 節（draft-07 快照結構異常）——不寫檔",
              file=sys.stderr)
        return 2
    atomic_write(OUTPUT_PATH, schema_text)
    print(f"[extract] 快照已寫入 {OUTPUT_PATH}（{len(definitions)} definitions）")
    return 0


# ---------------------------------------------------------------------------
# check 子命令（rev4:B-128 快照 drift 閘）
# ---------------------------------------------------------------------------

# --staged-gate 收窄的兩側 pathspec：typings 側住 base-web（＝TYPINGS_GLOB 對應）、
# 快照側住 rust-api worktree（＝OUTPUT_PATH 去掉子庫名；BL-00037③）。
TYPINGS_PATHSPECS = ["src/typings/common.d.ts", "src/typings/api"]
SNAPSHOT_PATHSPECS = ["server/tests/fixtures/wire-schema.json"]


def snapshots_match(fresh_bytes, snapshot_bytes):
    """byte 比對純函式（check 核心）——抽成純函式使入口 self-test 能餵相同／相異兩組
    合成 bytes、證紅綠俱可達（防恆綠）。"""
    return fresh_bytes == snapshot_bytes


def check_self_test():
    """check 入口無條件合成 self-test：相同 bytes 必判一致、相異必判不一致——失敗即
    比對邏輯壞（照 tools/fork-delta-lint.py main() 無條件 self_test 模式）。"""
    same = b'{"definitions":{"A":{"type":"object"}}}'
    other = b'{"definitions":{"B":{"type":"object"}}}'
    if not snapshots_match(same, same):
        raise AssertionError("相同 bytes 被誤判為不一致")
    if snapshots_match(same, other):
        raise AssertionError("相異 bytes 被誤判為一致")


# ---------------------------------------------------------------------------
# 跨子庫純讀檔錨兩腿（005 刀 U11 T070；spec FR-057、research R10）
# ---------------------------------------------------------------------------
# ★位置即語意：兩腿在 cmd_check 合成 self-test 之後、staged-gate 短路與容器探測之前**無條件**執行——只讀工作樹檔、不觸
# docker／git，故「pin 區間有無 typings／快照變動」「stack 有無在跑」都不能讓它跳過。收窄 pathspec（TYPINGS_PATHSPECS／
# SNAPSHOT_PATHSPECS）刻意不擴：擴了即牽動 pre-commit submodule-sync 段；觸發面沿用 pre-commit 既有 wire-schema 段（任一子庫
# pin bump 即跑 check）。★裁判力邊界：兩腿讀工作樹（與本工具重抽比對同一讀面）、不讀 pin 樹。

# BL-00109 qs 前提腿：base-web 查詢串序列化器＝`createAxiosConfig` 之 `paramsSerializer: params => stringify(params)`
# （`stringify` from qs；qs 預設 `strictNullHandling: false` ⇒ null 渲染成 `k=` 空值）＋axios 包之 qs 釘版。
# rust-api/server/tests/wire_schema.rs 的真串常數皆以此前提於 base-web 容器實跑產出；前提一改（序列化器傳選項、拿掉序列化器
# 回 axios 預設〔null 欄整個丟掉〕、換 qs 版）常數即不再是前端真送的串、而該檔照綠——本腿把前提釘成機器面。
# ★讀面只及這兩檔：呼叫端經 `createAxiosConfig(config)` 之 `Object.assign` 覆寫序列化器不在本腿讀面。
AXIOS_OPTIONS_TS = "base-web/packages/axios/src/options.ts"
AXIOS_PACKAGE_JSON = "base-web/packages/axios/package.json"
QS_PINNED_VERSION = "6.15.1"

# ADR-00044 決定 8 保留路由名對賬腿：rust `sys_menu::RESERVED_ROUTE_NAMES`＝前端 `createStaticRoutes` 實際常量組成——index.ts 之
# customRoutes 與 routes.ts 兩陣列中 `meta.constant: true` 之路由名集——∪ builtin.ts 之路由名集（新增 view 頁、customRoutes 增常量路由或
# upstream rebase 動到內建常量路由／內建根路由之名集時由本腿攔下）。★index.ts 讀面限 customRoutes 陣列字面（同檔其餘碼不讀、
# createStaticRoutes 之併列組成不在讀面）：陣列字面找不到＝解析失準即紅；陣列在而零常量路由屬正常（現況）。
SYS_MENU_RS = "rust-api/server/src/model/facade/sys_menu.rs"
ELEGANT_ROUTES_TS = "base-web/src/router/elegant/routes.ts"
CUSTOM_ROUTES_TS = "base-web/src/router/routes/index.ts"
BUILTIN_ROUTES_TS = "base-web/src/router/routes/builtin.ts"

ANCHOR_FILES = (AXIOS_OPTIONS_TS, AXIOS_PACKAGE_JSON, SYS_MENU_RS, ELEGANT_ROUTES_TS, CUSTOM_ROUTES_TS,
                BUILTIN_ROUTES_TS)


QS_REMEDY = ("補救：前提改動須同批於 base-web 容器以新前提實跑、重取 rust-api/server/tests/wire_schema.rs 之各真串常數，"
             "再改本工具之前提釘值（BL-00109）")
RESERVED_REMEDY = ("補救：同批改 rust-api/server/src/model/facade/sys_menu.rs 之 RESERVED_ROUTE_NAMES（ADR-00044 決定 8）"
                   "或還原前端路由定義，使兩側名集相等")


def strip_ts_comments(text):
    """去 TS 註解（`//` 至行尾、`/* */` 區塊）、字串字面（'…'／"…"／`…`）原樣保留——註解掉的碼不得被當成生效碼。
    regex 字面不特判。"""
    out = []
    i, n = 0, len(text)
    quote = None
    while i < n:
        c = text[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
        elif c in "'\"`":
            quote = c
            out.append(c)
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j == -1 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
            out.append(" ")
        else:
            out.append(c)
            i += 1
    return "".join(out)


_QS_IMPORT = re.compile(r"^import\s*\{\s*stringify\s*\}\s*from\s*['\"]qs['\"]\s*;?\s*$", re.M)
_SERIALIZER_TOKEN = re.compile(r"\bparamsSerializer\b")
# 去空白後比對：屬性值恰為無選項之 `params => stringify(params)`（區塊體或表達式體皆可）。
_SERIALIZER_FORM = re.compile(
    r"paramsSerializer:\(?params\)?=>(?:\{returnstringify\(params\);?\}|stringify\(params\))[,}]")


def qs_premise_problems(options_ts, package_json):
    """BL-00109 qs 前提腿判準（純函式）：回違規說明清單、空＝通過。
    ①`stringify` 恰以 `import { stringify } from 'qs'` 匯入一次 ②去註解後 `paramsSerializer` 恰一處、且為無選項
    `params => stringify(params)` ③axios 包 `dependencies.qs` 恰為 QS_PINNED_VERSION。"""
    problems = []
    code = strip_ts_comments(options_ts)
    if len(_QS_IMPORT.findall(code)) != 1:
        problems.append(f"{AXIOS_OPTIONS_TS}：`stringify` 須恰以 `import {{ stringify }} from 'qs'` 匯入一次——{QS_REMEDY}")
    occurrences = len(_SERIALIZER_TOKEN.findall(code))
    if occurrences != 1 or not _SERIALIZER_FORM.search(re.sub(r"\s+", "", code)):
        problems.append(f"{AXIOS_OPTIONS_TS}：`paramsSerializer` 須恰一處生效碼、且為無選項 `params => stringify(params)`"
                        f"（實得生效碼 {occurrences} 處）——{QS_REMEDY}")
    try:
        deps = json.loads(package_json).get("dependencies") or {}
    except (json.JSONDecodeError, AttributeError):
        deps = {}
    qs = deps.get("qs") if isinstance(deps, dict) else None
    if qs != QS_PINNED_VERSION:
        problems.append(f"{AXIOS_PACKAGE_JSON}：dependencies.qs 須為 {QS_PINNED_VERSION}（實得 {qs!r}）——{QS_REMEDY}")
    return problems


_RESERVED_DECL = re.compile(
    r"\bconst\s+RESERVED_ROUTE_NAMES\s*:\s*\[\s*&\s*(?:'static\s+)?str\s*;\s*\d+\s*\]\s*=\s*\[([^\]]*)\]\s*;")
_RUST_STR = re.compile(r'"((?:[^"\\]|\\.)*)"')
_TS_TOKEN = re.compile(
    r"""(?P<space>\s+)|(?P<str>'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*"|`(?:[^`\\]|\\.)*`)"""
    r"""|(?P<ident>[A-Za-z_$][\w$]*)|(?P<punct>[{}\[\]():,;])|(?P<other>.)""", re.S)
_CLOSERS = {"}": "{", "]": "[", ")": "("}


_RUST_RAW_STR = re.compile(r'b?r(#*)"')
_RUST_CHAR = re.compile(r"'(?:\\(?:u\{[0-9A-Fa-f]{1,6}\}|x[0-9A-Fa-f]{2}|.)|[^'\\\n])'")


def strip_rust_comments(text):
    """去 rust 註解（`//` 至行尾〔含 doc 註解〕、`/* */` 區塊〔可巢狀〕）；字串字面（`"…"`、raw 字串 `r#"…"#`）與字元字面
    （`'x'`）原樣保留、生命週期號（`'static`）之 `'` 不是字面起點——同 strip_ts_comments 之旨：註解掉的碼不得被當成生效碼。"""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        raw = (_RUST_RAW_STR.match(text, i)
               if c in "br" and not (i and (text[i - 1].isalnum() or text[i - 1] == "_")) else None)
        if raw:
            end = text.find('"' + raw.group(1), raw.end())
            j = n if end == -1 else end + 1 + len(raw.group(1))
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
        elif c == "'":
            char = _RUST_CHAR.match(text, i)
            j = char.end() if char else i + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j == -1 else j
            continue
        elif text.startswith("/*", i):
            depth, j = 1, i + 2
            while j < n and depth:
                step = text[j:j + 2]
                depth += (step == "/*") - (step == "*/")
                j += 2 if step in ("/*", "*/") else 1
            out.append(" ")
            i = j
            continue
        else:
            j = i + 1
        out.append(text[i:j])
        i = j
    return "".join(out)


def rust_reserved_route_names(sys_menu_rs):
    """sys_menu.rs → (RESERVED_ROUTE_NAMES 成員集, 違規清單)。先經 strip_rust_comments 去註解（行尾 `//`、`/* */` 內之名不計）；
    宣告須恰一處。"""
    code = strip_rust_comments(sys_menu_rs)
    decls = _RESERVED_DECL.findall(code)
    if len(decls) != 1:
        return set(), [f"{SYS_MENU_RS}：`const RESERVED_ROUTE_NAMES: [&str; N] = [...];` 宣告須恰一處（實得 {len(decls)} 處）"]
    return set(_RUST_STR.findall(decls[0])), []


def ts_route_names(text, rel):
    """TS 路由定義檔 → (全部路由名集, `meta.constant: true` 之路由名集, 違規清單)。
    路由物件＝直屬 `name: '<字串>'` 屬性之物件字面；常量性＝其直屬 `meta: { … }` 內之 `constant: true`。"""
    tokens = [(m.lastgroup, m.group()) for m in _TS_TOKEN.finditer(strip_ts_comments(text))
              if m.lastgroup != "space"]
    stack = []   # 每層：[開括號, 屬性鍵, 路由名, 常量性]
    names, constants = set(), set()
    for i, (kind, tok) in enumerate(tokens):
        prev = tokens[i - 1][1] if i else ""
        if tok in ("{", "[", "("):
            key = tokens[i - 2][1] if prev == ":" and i >= 2 and tokens[i - 2][0] == "ident" else None
            stack.append([tok, key, None, False])
        elif tok in _CLOSERS:
            if not stack or stack[-1][0] != _CLOSERS[tok]:
                return names, constants, [f"{rel}：括號不成對（解析失準）"]
            opener, _, name, constant = stack.pop()
            if opener == "{" and name is not None:
                names.add(name)
                if constant:
                    constants.add(name)
            elif constant:
                return names, constants, [f"{rel}：`meta.constant: true` 所屬物件缺 `name`（解析失準）"]
        elif (kind == "ident" and prev in ("{", ",") and i + 2 < len(tokens) and tokens[i + 1][1] == ":"
              and stack and stack[-1][0] == "{"):
            value_kind, value = tokens[i + 2]
            if tok == "name" and value_kind == "str":
                stack[-1][2] = value[1:-1]
            elif (tok == "constant" and value == "true" and stack[-1][1] == "meta"
                  and len(stack) >= 2 and stack[-2][0] == "{"):
                stack[-2][3] = True
    if stack:
        return names, constants, [f"{rel}：括號不成對（解析失準）"]
    return names, constants, []


_CUSTOM_ROUTES_DECL = re.compile(r"\bconst\s+customRoutes\b[^=;]*=\s*\[")


def custom_routes_literal(index_ts):
    """index.ts → (customRoutes 陣列字面〔去註解後、含首尾方括號〕, 違規清單)。宣告須恰一處、陣列方括號須配對
    （字串字面內之括號不計）；任一不成＝解析失準、違規一條。"""
    code = strip_ts_comments(index_ts)
    decls = list(_CUSTOM_ROUTES_DECL.finditer(code))
    if len(decls) != 1:
        return "", [f"{CUSTOM_ROUTES_TS}：`const customRoutes … = [...]` 陣列字面須恰一處（實得 {len(decls)} 處；解析失準）"]
    start = decls[0].end() - 1
    depth = 0
    for m in _TS_TOKEN.finditer(code, start):
        if m.lastgroup == "punct":
            depth += (m.group() in "[{(") - (m.group() in "]})")
            if depth == 0:
                return code[start:m.end()], []
    return "", [f"{CUSTOM_ROUTES_TS}：customRoutes 陣列方括號不成對（解析失準）"]


def reserved_route_names_problems(sys_menu_rs, routes_ts, custom_ts, builtin_ts):
    """ADR-00044 決定 8 保留路由名對賬腿判準（純函式）：回違規說明清單、空＝通過。
    rust 成員集須恰等於 routes.ts 與 index.ts customRoutes 之常量路由名集 ∪ builtin.ts 之路由名集；rust、routes.ts 常量路由、
    builtin.ts 任一側零成員＝解析面空、即紅（customRoutes 零常量路由屬正常，其解析失準由陣列字面定位判）。"""
    rust, problems = rust_reserved_route_names(sys_menu_rs)
    _, constant_routes, p_routes = ts_route_names(routes_ts, ELEGANT_ROUTES_TS)
    custom_literal, p_custom = custom_routes_literal(custom_ts)
    _, custom_constants, p_custom_parse = ts_route_names(custom_literal, CUSTOM_ROUTES_TS)
    builtin_routes, _, p_builtin = ts_route_names(builtin_ts, BUILTIN_ROUTES_TS)
    problems += p_routes + p_custom + p_custom_parse + p_builtin
    if problems:
        return problems
    for label, found in (("rust RESERVED_ROUTE_NAMES", rust), (f"{ELEGANT_ROUTES_TS} 常量路由", constant_routes),
                         (f"{BUILTIN_ROUTES_TS} 路由", builtin_routes)):
        if not found:
            problems.append(f"{label} 零成員＝解析面空（判準失準或檔形改變）")
    frontend = constant_routes | custom_constants | builtin_routes
    if not problems and rust != frontend:
        problems.append(f"保留路由名集不一致：rust 多出 {sorted(rust - frontend)}、前端三源多出 {sorted(frontend - rust)}"
                        f"——{RESERVED_REMEDY}")
    return problems


def anchor_problems(root=REPO_ROOT):
    """讀 `root` 下兩腿六檔、跑兩支判準；檔缺席或讀不了＝違規一條（fail-loud、不當跳過）。"""
    texts = {}
    problems = []
    for rel in ANCHOR_FILES:
        try:
            with open(os.path.join(root, *rel.split("/")), encoding="utf-8") as fh:
                texts[rel] = fh.read()
        except OSError as ex:
            problems.append(f"錨檔讀不了：{rel}（{ex}）——子庫工作樹缺席或損壞、跑 bash tools/bootstrap.sh 檢修")
    if problems:
        return problems
    return (qs_premise_problems(texts[AXIOS_OPTIONS_TS], texts[AXIOS_PACKAGE_JSON])
            + reserved_route_names_problems(texts[SYS_MENU_RS], texts[ELEGANT_ROUTES_TS],
                                            texts[CUSTOM_ROUTES_TS], texts[BUILTIN_ROUTES_TS]))


def run_anchor_legs(root=REPO_ROOT):
    """跑兩腿並印結果（違規逐條走 stderr）；回 True＝通過。"""
    problems = anchor_problems(root)
    for problem in problems:
        print(f"[check] ✗ {problem}", file=sys.stderr)
    if problems:
        return False
    print("[check] ✓ 跨子庫錨兩腿通過（BL-00109 qs 前提；ADR-00044 決定 8 保留路由名對賬）")
    return True


def _clean_git_env(environ):
    """清掉 GIT_* env：git hook 會把外層 repo 的 GIT_DIR/GIT_INDEX_FILE 洩漏給子行程，
    害對 base-web worktree（.git 為檔）跑 git 抓錯 index（.git/index: Not a directory）
    ——照 tools/fork-delta-lint.py 現成模式。★僅用於對 base-web 的 git；外層
    git diff --cached 必須保留 env（commit -a 時 GIT_INDEX_FILE 指向暫時 index）。"""
    return {k: v for k, v in environ.items() if not k.startswith("GIT_")}


def _run_git_sub(argv):
    """對子庫跑 git（清 GIT_* env、cwd＝REPO_ROOT、-C 由 argv 自帶）——base-web 與 rust-api 兩側共用。"""
    return subprocess.run(argv, capture_output=True, text=True, cwd=REPO_ROOT,
                          env=_clean_git_env(os.environ))


def probe_base_web(run=_run_capture):
    """base-web 容器可用性探測（容器內跑 true、廉價）。OSError／非零＝不可用。"""
    try:
        proc = run(BASE_WEB_EXEC + ["true"])
    except OSError:
        return False
    return proc.returncode == 0


def _pin_range_verdict(sub, pathspecs, run_outer, run_sub):
    """單側 pin 區間收窄判定（判定放 python、sh 只做粗判；兩側共用）。

    回四值：not-staged＝該子庫 gitlink 未 staged（無事可查）；no-change＝staged 區間零
    pathspecs 變動；changed＝有變動；unknown＝無法判定（保守走完整比對）。"""
    proc = run_outer(["git", "diff", "--cached", "--raw", "--no-abbrev", "--", sub])
    if proc.returncode != 0:
        return "unknown"
    line = (proc.stdout or "").strip()
    if not line:
        return "not-staged"
    parts = line.split()
    if len(parts) < 4:
        return "unknown"
    old, new = parts[2], parts[3]
    if set(old) == {"0"} or set(new) == {"0"}:
        return "unknown"  # gitlink 新增／刪除——無區間可縮、走完整比對
    diff = run_sub(["git", "-C", sub, "diff", "--name-only", old, new, "--"] + pathspecs)
    if diff.returncode != 0:
        return "unknown"
    return "changed" if (diff.stdout or "").strip() else "no-change"


def staged_typings_verdict(run_outer=_run_capture, run_baseweb=_run_git_sub):
    """typings 側（base-web pin 區間 × TYPINGS_PATHSPECS）收窄判定。

    回傳四值沿用歷史命名：not-staged／no-typings／typings-changed／unknown。"""
    v = _pin_range_verdict("base-web", TYPINGS_PATHSPECS, run_outer, run_baseweb)
    return {"no-change": "no-typings", "changed": "typings-changed"}.get(v, v)


def staged_snapshot_verdict(run_outer=_run_capture, run_rustapi=_run_git_sub):
    """快照側（rust-api pin 區間 × SNAPSHOT_PATHSPECS）收窄判定（BL-00037③）。

    ★快照住 rust-api worktree 內，外層 staged 面永遠只看得到 `rust-api` gitlink——
    故快照側的觸發訊號是 pin bump，區間細判在此（對稱於 entity-drift 的雙側觸發）。
    回四值：not-staged／no-change／changed／unknown。"""
    return _pin_range_verdict("rust-api", SNAPSHOT_PATHSPECS, run_outer, run_rustapi)


def cmd_check(staged_gate=False, run=_run_capture, run_outer=_run_capture,
              run_baseweb=_run_git_sub, run_rustapi=_run_git_sub,
              output_path=OUTPUT_PATH, anchor_root=REPO_ROOT):
    """check 子命令：跨子庫純讀檔錨兩腿＋重抽 typings 至暫存路徑、與工作樹快照 byte 比對（rev4:B-128 drift 閘）。

    絕不覆寫 OUTPUT_PATH；比對工作樹檔、勿讀 git blob（快照剛改未 commit 的中間態會誤紅）。
    fail 語意（rev5 user 親決 2026-08-01；rev6 002 刀 clarify Q5 同向拍板）：容器不可用→警告＋0 放行；
    容器可用但重抽失敗→2。錨兩腿任一違規→2（無條件、不看收窄與容器）。"""
    # ① 無條件合成 self-test（防恆綠）。
    try:
        check_self_test()
    except AssertionError as ex:
        print(f"[check] ✗ self-test 失敗（check 比對邏輯壞）：{ex}", file=sys.stderr)
        return 2
    # ①′ 跨子庫純讀檔錨兩腿（BL-00109 qs 前提／ADR-00044 決定 8 保留路由名）：無條件執行、先於下方收窄與容器探測。
    if not run_anchor_legs(anchor_root):
        return 2
    # ② hook 專用收窄：**兩側** pin 區間皆零變動才跳過（省 npx 秒數）。
    # ★BL-00037③：原只判 base-web 側，rust-api pin bump 帶進的快照改動零觸發——sh 段補了
    #   `-e 'rust-api'` 觸發字面卻在此被 not-staged 一路跳過，等於假腿；快照側須自判區間。
    if staged_gate:
        typ = staged_typings_verdict(run_outer=run_outer, run_baseweb=run_baseweb)
        snap = staged_snapshot_verdict(run_outer=run_outer, run_rustapi=run_rustapi)
        if typ in ("not-staged", "no-typings") and snap in ("not-staged", "no-change"):
            print(f"[check] staged 兩側 pin 區間零變動（typings 側 {typ}"
                  f"〔src/typings/common.d.ts＋src/typings/api/〕／快照側 {snap}"
                  f"〔{SNAPSHOT_PATHSPECS[0]}〕）——跳過重抽比對")
            return 0
        # 任一側 changed／unknown → 續跑完整比對。
    # ③ 容器探測：不可用＝警告＋放行（dev stack 未起不該擋無關 commit）。
    if not probe_base_web(run=run):
        print(f"[check] ⚠ base-web 容器不可用（stack 未起）——wire-schema check 跳過、放行；"
              f"要跑實比對先起 stack：{START_HINT}")
        return 0
    # ④ 重抽（容器宣稱可用、失敗即異常＝fail-loud，靜默跳過會成恆綠洞）。
    # ★提示尾巴自屬（勿沿用 extract 的「起 stack」句——probe 剛證容器可用、照打無效）：
    # 真因在容器內 npx 取件／typescript-json-schema 執行，補救＝手動重現抽取命令定位。
    check_hint = ("容器內手動重現抽取定位真因："
                  + " ".join(BASE_WEB_EXEC)
                  + f" sh -c '{build_npx_command()}'"
                  "；npm 取件失敗時檢查容器對 npm registry 連線")
    try:
        schema_text = extract_schema(run=run, hint=check_hint)
    except ExtractError as ex:
        print(f"[check] ✗ 容器可用但重抽失敗：{ex}", file=sys.stderr)
        return 2
    try:
        parsed = json.loads(schema_text)
    except json.JSONDecodeError as ex:
        print(f"[check] ✗ 容器可用但重抽輸出非合法 JSON（{ex}）", file=sys.stderr)
        return 2
    definitions = parsed.get("definitions") if isinstance(parsed, dict) else None
    if not isinstance(definitions, dict) or not definitions:
        print("[check] ✗ 重抽輸出缺非空 definitions 節（快照結構異常）", file=sys.stderr)
        return 2
    # ⑤ 暫存路徑落地（與 extract 同一 atomic_write 寫入路徑＝byte 語意一致）＋比對。
    tmp_dir = tempfile.mkdtemp(prefix="wire-schema-check.")
    try:
        tmp_path = os.path.join(tmp_dir, "wire-schema.json")
        atomic_write(tmp_path, schema_text)
        with open(tmp_path, "rb") as fh:
            fresh = fh.read()
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    snap_abs = output_path if os.path.isabs(output_path) else os.path.join(REPO_ROOT, output_path)
    try:
        with open(snap_abs, "rb") as fh:
            on_disk = fh.read()
    except FileNotFoundError:
        print(f"[check] ✗ 快照檔缺席（{output_path}）——補救：python3 tools/wire-schema.py extract",
              file=sys.stderr)
        return 2
    if snapshots_match(fresh, on_disk):
        print(f"[check] ✓ 快照與 typings 重抽 byte 一致（{len(definitions)} definitions）")
        return 0
    # ★補救程序照兩段式 commit 真實走法寫（快照住 rust-api worktree、typings 住 base-web
    # worktree、分屬不同 repo——「同一 commit 提交兩者」跨 submodule 不可能照做；本閘正是
    # 為「pin 進了、快照沒進」而立，補救文字本身就是防復發教材）。
    print(f"[check] ✗ 快照與 typings 重抽不一致（{output_path}）——補救：先跑 "
          "python3 tools/wire-schema.py extract 重抽、rust-api worktree 內 commit 快照，"
          "再回外層同一 commit 一併 bump base-web 與 rust-api 兩支 pin",
          file=sys.stderr)
    return 2


# ---------------------------------------------------------------------------
# 自帶測試（unittest、離線可跑——不觸 docker）
# ---------------------------------------------------------------------------

# 既有 check 流程案（探測／重抽比對／收窄）只驗各自語意：錨兩腿以「恆通過」替身隔離，免其紅綠繫於本 repo 兩子庫工作樹現況。
# 兩腿本身的紅綠由 TestAnchorLegs（真檔副本字串構造）與 TestCheckAnchorsUnconditional（接進 cmd_check 之位置）承擔。
_ANCHORS_PASS = unittest.mock.patch.dict(globals(), {"run_anchor_legs": lambda root: True})


class TestCommandAssembly(unittest.TestCase):
    def test_npx_command_pins_version_fileset_type_flags(self):
        cmd = build_npx_command()
        self.assertIn(f"typescript-json-schema@{TSJS_VERSION}", cmd)
        self.assertIn(f'"{TYPINGS_GLOB}"', cmd)
        self.assertIn(f'"{TSJS_TYPE}"', cmd)
        self.assertIn("--ignoreErrors", cmd)
        self.assertIn("--required", cmd)
        # 完整逐字（釘版契約＝rev4:research R1 實測命令形）。
        self.assertEqual(
            cmd,
            'npx -y typescript-json-schema@0.67.4 '
            '"src/typings/{common,api/*}.d.ts" "*" '
            '--ignoreErrors --required --strictNullChecks',
        )

    def test_extract_argv_targets_base_web_app_cwd(self):
        argv = build_extract_argv()
        self.assertEqual(argv[: len(BASE_WEB_EXEC)], BASE_WEB_EXEC)
        self.assertIn("-w", argv)
        self.assertIn("/app", argv)
        self.assertIn("base-web", argv)
        # 容器內以 sh -c 執行組裝好的 npx 命令。
        self.assertEqual(argv[-3:], ["sh", "-c", build_npx_command()])


class TestOutputPath(unittest.TestCase):
    def test_output_path_is_fixtures_wire_schema_json(self):
        self.assertEqual(
            OUTPUT_PATH,
            os.path.join("rust-api", "server", "tests", "fixtures", "wire-schema.json"),
        )


class TestExtractFailLoud(unittest.TestCase):
    def test_missing_stack_nonzero_raises_with_start_hint(self):
        def fake_run(argv):
            return subprocess.CompletedProcess(
                argv, returncode=1, stdout="",
                stderr="service \"base-web\" is not running",
            )

        with self.assertRaises(ExtractError) as cm:
            extract_schema(run=fake_run)
        self.assertIn("up", str(cm.exception))  # 提示啟動命令

    def test_docker_missing_oserror_raises_with_start_hint(self):
        def fake_run(argv):
            raise FileNotFoundError("docker")

        with self.assertRaises(ExtractError) as cm:
            extract_schema(run=fake_run)
        self.assertIn("docker", str(cm.exception))

    def test_success_returns_stdout_verbatim(self):
        payload = '{"$schema":"http://json-schema.org/draft-07/schema#","definitions":{}}'

        def fake_run(argv):
            return subprocess.CompletedProcess(
                argv, returncode=0, stdout=payload, stderr="npm warn ...",
            )

        self.assertEqual(extract_schema(run=fake_run), payload)


class TestAtomicWrite(unittest.TestCase):
    def test_atomic_write_creates_replaces_and_leaves_no_temp(self):
        with tempfile.TemporaryDirectory() as root:
            target = os.path.join(root, "sub", "wire-schema.json")
            atomic_write(target, "hello")
            with open(target, encoding="utf-8") as fh:
                self.assertEqual(fh.read(), "hello")
            # 覆寫既有檔。
            atomic_write(target, "world")
            with open(target, encoding="utf-8") as fh:
                self.assertEqual(fh.read(), "world")
            # 無 .tmp 殘留（原子替換乾淨）。
            leftovers = [f for f in os.listdir(os.path.dirname(target)) if f.endswith(".tmp")]
            self.assertEqual(leftovers, [])


class TestSnapshotsMatch(unittest.TestCase):
    """check 比對純函式紅綠（rev4:B-128；亦為入口合成 self-test 的直接對象）。"""

    def test_identical_bytes_match(self):
        payload = b'{"definitions":{"A":{}}}'
        self.assertTrue(snapshots_match(payload, payload))

    def test_different_bytes_mismatch(self):
        self.assertFalse(snapshots_match(
            b'{"definitions":{"A":{}}}', b'{"definitions":{"B":{}}}'))

    def test_check_self_test_passes_on_healthy_logic(self):
        check_self_test()  # 邏輯健康＝不 raise

    def test_check_self_test_failure_rc2(self):
        """★紅證另一半（防恆綠機制自身）：比對邏輯壞（恆回一致）時 check 入口
        self-test 必擋——rc 2、指名 check 比對邏輯壞、不觸任何子行程（與
        fork-delta-lint 同款無條件 self-test 對齊）。"""
        def boom(argv):
            raise AssertionError("self-test 失敗即 return 2、不得觸發任何子行程")

        err = io.StringIO()
        with unittest.mock.patch.object(
                sys.modules[__name__], "snapshots_match", lambda a, b: True):
            with contextlib.redirect_stderr(err):
                rc = cmd_check(run=boom, run_outer=boom, run_baseweb=boom)
        self.assertEqual(rc, 2)
        self.assertIn("self-test 失敗", err.getvalue())
        self.assertIn("比對邏輯壞", err.getvalue())


class TestCleanGitEnv(unittest.TestCase):
    """對 base-web 跑 git 前清 GIT_*（hook 洩漏外層 GIT_DIR/GIT_INDEX_FILE 撞 worktree index）。"""

    def test_strips_git_vars_keeps_rest(self):
        env = {"GIT_DIR": "/x/.git", "GIT_INDEX_FILE": "/x/idx",
               "GIT_WORK_TREE": "/x", "PATH": "/usr/bin", "HOME": "/home/u"}
        self.assertEqual(_clean_git_env(env), {"PATH": "/usr/bin", "HOME": "/home/u"})


@_ANCHORS_PASS
class TestCheckFailOpen(unittest.TestCase):
    """容器不可用（stack 未起）＝警告＋rc 0 放行（rev5 user 親決 2026-08-01；rev6 002 刀 clarify Q5 同向）。"""

    def test_container_unavailable_warns_and_passes(self):
        def fake_run(argv):
            return subprocess.CompletedProcess(
                argv, returncode=1, stdout="",
                stderr='service "base-web" is not running')

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cmd_check(run=fake_run)
        self.assertEqual(rc, 0)
        self.assertIn("wire-schema check 跳過", out.getvalue())
        self.assertIn("stack 未起", out.getvalue())

    def test_docker_missing_oserror_warns_and_passes(self):
        def fake_run(argv):
            raise FileNotFoundError("docker")

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cmd_check(run=fake_run)
        self.assertEqual(rc, 0)
        self.assertIn("wire-schema check 跳過", out.getvalue())


@_ANCHORS_PASS
class TestCheckFailLoud(unittest.TestCase):
    """容器可用但重抽失敗＝rc 2（環境宣稱可用時失敗即異常、靜默跳過＝恆綠洞）。"""

    @staticmethod
    def _probe_ok_extract(returncode, stdout="", stderr=""):
        def fake_run(argv):
            if argv[-1] == "true":  # 可用性探測
                return subprocess.CompletedProcess(argv, 0, "", "")
            return subprocess.CompletedProcess(argv, returncode, stdout, stderr)
        return fake_run

    def test_extract_nonzero_rc2(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            rc = cmd_check(run=self._probe_ok_extract(1, stderr="npx 非零退出"))
        self.assertEqual(rc, 2)
        self.assertIn("重抽失敗", err.getvalue())
        # ★提示自屬（勿夾帶 extract 的「起 stack」句——probe 剛證容器可用、自相矛盾）：
        # 補救＝容器內手動重現抽取命令。
        self.assertNotIn(START_HINT, err.getvalue())
        self.assertIn(build_npx_command(), err.getvalue())

    def test_extract_invalid_json_rc2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            rc = cmd_check(run=self._probe_ok_extract(0, stdout="not json"))
        self.assertEqual(rc, 2)

    def test_extract_empty_definitions_rc2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            rc = cmd_check(run=self._probe_ok_extract(0, stdout='{"definitions":{}}'))
        self.assertEqual(rc, 2)


@_ANCHORS_PASS
class TestCheckCompare(unittest.TestCase):
    """重抽落暫存路徑 vs 工作樹快照 byte 比對——絕不覆寫快照、不一致指名補救命令。"""

    PAYLOAD = '{"$schema":"http://json-schema.org/draft-07/schema#","definitions":{"A":{}}}'

    def _fake_run(self, payload):
        def fake_run(argv):
            if argv[-1] == "true":
                return subprocess.CompletedProcess(argv, 0, "", "")
            return subprocess.CompletedProcess(argv, 0, payload, "")
        return fake_run

    def test_matching_snapshot_rc0_and_snapshot_untouched(self):
        with tempfile.TemporaryDirectory() as root:
            snap = os.path.join(root, "wire-schema.json")
            atomic_write(snap, self.PAYLOAD)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = cmd_check(run=self._fake_run(self.PAYLOAD), output_path=snap)
            self.assertEqual(rc, 0)
            with open(snap, encoding="utf-8") as fh:  # 快照原封不動
                self.assertEqual(fh.read(), self.PAYLOAD)

    def test_drifted_snapshot_rc2_names_remedy(self):
        with tempfile.TemporaryDirectory() as root:
            snap = os.path.join(root, "wire-schema.json")
            atomic_write(snap, self.PAYLOAD.replace('"A"', '"Z"'))
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = cmd_check(run=self._fake_run(self.PAYLOAD), output_path=snap)
            self.assertEqual(rc, 2)
            self.assertIn("python3 tools/wire-schema.py extract", err.getvalue())
            # 補救＝可照打的兩段式程序（快照與 typings 分屬兩 worktree、不可能同一
            # commit——正確走法：rust-api worktree commit 快照→外層一併 bump 兩支 pin）。
            self.assertIn("rust-api worktree 內 commit", err.getvalue())
            self.assertIn("bump base-web 與 rust-api 兩支 pin", err.getvalue())
            with open(snap, encoding="utf-8") as fh:  # 不一致也不得覆寫
                self.assertEqual(fh.read(), self.PAYLOAD.replace('"A"', '"Z"'))

    def test_missing_snapshot_rc2(self):
        with tempfile.TemporaryDirectory() as root:
            snap = os.path.join(root, "missing.json")
            with contextlib.redirect_stderr(io.StringIO()):
                rc = cmd_check(run=self._fake_run(self.PAYLOAD), output_path=snap)
            self.assertEqual(rc, 2)


_RAW_GITLINK = ":160000 160000 " + "a" * 40 + " " + "b" * 40 + " M\tbase-web\n"
_RAW_GITLINK_RA = ":160000 160000 " + "c" * 40 + " " + "d" * 40 + " M\trust-api\n"


@_ANCHORS_PASS
class TestCheckStagedGate(unittest.TestCase):
    """--staged-gate 收窄（hook 專用）：**兩側** pin 區間皆零變動＝跳過 rc 0、不觸容器；
    任一側（typings 側 base-web／快照側 rust-api）有變動＝走完整比對（BL-00037③ 雙側觸發）。"""

    @staticmethod
    def _boom_run(argv):
        raise AssertionError("收窄應跳過、不得觸發容器探測／重抽")

    @staticmethod
    def _fixed(stdout, returncode=0):
        def fake(argv):
            return subprocess.CompletedProcess(argv, returncode, stdout, "")
        return fake

    @staticmethod
    def _by_sub(baseweb="", rustapi=""):
        """外層 `git diff --cached --raw … -- <sub>` 的 fake：依 argv 末項（子庫名）分回——
        兩側收窄各查各的 gitlink，同一 seam 回同一串會讓另一側誤判。"""
        def fake(argv):
            return subprocess.CompletedProcess(
                argv, 0, rustapi if argv[-1] == "rust-api" else baseweb, "")
        return fake

    def test_gitlink_not_staged_skips_rc0(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cmd_check(staged_gate=True, run=self._boom_run,
                           run_outer=self._fixed(""), run_baseweb=self._boom_run)
        self.assertEqual(rc, 0)
        self.assertIn("跳過", out.getvalue())

    def test_zero_typings_change_skips_rc0(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cmd_check(staged_gate=True, run=self._boom_run,
                           run_outer=self._by_sub(baseweb=_RAW_GITLINK),
                           run_baseweb=self._fixed(""), run_rustapi=self._boom_run)
        self.assertEqual(rc, 0)
        self.assertIn("跳過", out.getvalue())

    def test_typings_changed_runs_full_compare(self):
        payload = '{"definitions":{"A":{}}}'
        container_calls = []

        def spy_run(argv):
            container_calls.append(argv)
            if argv[-1] == "true":
                return subprocess.CompletedProcess(argv, 0, "", "")
            return subprocess.CompletedProcess(argv, 0, payload, "")

        with tempfile.TemporaryDirectory() as root:
            snap = os.path.join(root, "wire-schema.json")
            atomic_write(snap, payload)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = cmd_check(staged_gate=True, run=spy_run,
                               run_outer=self._by_sub(baseweb=_RAW_GITLINK),
                               run_baseweb=self._fixed("src/typings/api/system.d.ts\n"),
                               run_rustapi=self._boom_run, output_path=snap)
        self.assertEqual(rc, 0)
        # ★可辨識斷言（跳過路徑 rc 同為 0、只驗 rc 釘不住正向面）：容器 seam 確被呼叫
        # （探測＋重抽共 2 次）、stdout 是完整比對的一致訊息而非跳過訊息。
        self.assertEqual(len(container_calls), 2)
        self.assertIn("byte 一致", out.getvalue())
        self.assertNotIn("跳過", out.getvalue())

    def test_snapshot_pathspec_matches_output_path(self):
        """★快照側 pathspec 打錯＝區間 diff 恆空＝恆判 no-change＝假腿；此案把它釘在 OUTPUT_PATH 上。"""
        self.assertEqual(os.path.join("rust-api", *SNAPSHOT_PATHSPECS[0].split("/")),
                         OUTPUT_PATH)

    def test_snapshot_changed_runs_full_compare(self):
        """快照側正例（BL-00037③）：base-web 未 staged、rust-api pin 區間動到快照 → 走完整比對。"""
        payload = '{"definitions":{"A":{}}}'
        container_calls = []
        sub_argvs = []

        def spy_run(argv):
            container_calls.append(argv)
            if argv[-1] == "true":
                return subprocess.CompletedProcess(argv, 0, "", "")
            return subprocess.CompletedProcess(argv, 0, payload, "")

        def spy_rustapi(argv):
            sub_argvs.append(argv)
            return subprocess.CompletedProcess(argv, 0, SNAPSHOT_PATHSPECS[0] + "\n", "")

        with tempfile.TemporaryDirectory() as root:
            snap = os.path.join(root, "wire-schema.json")
            atomic_write(snap, payload)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = cmd_check(staged_gate=True, run=spy_run,
                               run_outer=self._by_sub(rustapi=_RAW_GITLINK_RA),
                               run_baseweb=self._boom_run, run_rustapi=spy_rustapi,
                               output_path=snap)
        self.assertEqual(rc, 0)
        self.assertEqual(len(container_calls), 2)   # 探測＋重抽＝確實沒被收窄跳過
        self.assertIn("byte 一致", out.getvalue())
        self.assertNotIn("跳過", out.getvalue())
        self.assertIn(SNAPSHOT_PATHSPECS[0], sub_argvs[0])   # 區間 diff 帶了快照 pathspec

    def test_both_sides_staged_zero_change_skips_rc0(self):
        """快照側反例：兩側皆 pin bump 但各自區間零變動 → 仍跳過 rc 0、不觸容器。"""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cmd_check(staged_gate=True, run=self._boom_run,
                           run_outer=self._by_sub(baseweb=_RAW_GITLINK,
                                                  rustapi=_RAW_GITLINK_RA),
                           run_baseweb=self._fixed(""), run_rustapi=self._fixed(""))
        self.assertEqual(rc, 0)
        self.assertIn("跳過", out.getvalue())

    def test_snapshot_verdict_values(self):
        self.assertEqual(
            staged_snapshot_verdict(run_outer=self._fixed(""),
                                    run_rustapi=self._boom_run), "not-staged")
        self.assertEqual(
            staged_snapshot_verdict(run_outer=self._fixed(_RAW_GITLINK_RA),
                                    run_rustapi=self._fixed("")), "no-change")
        self.assertEqual(
            staged_snapshot_verdict(run_outer=self._fixed(_RAW_GITLINK_RA),
                                    run_rustapi=self._fixed(SNAPSHOT_PATHSPECS[0])),
            "changed")
        self.assertEqual(
            staged_snapshot_verdict(run_outer=self._fixed(_RAW_GITLINK_RA),
                                    run_rustapi=self._fixed("", returncode=1)), "unknown")

    def test_zero_old_sha_verdict_unknown(self):
        raw = ":000000 160000 " + "0" * 40 + " " + "b" * 40 + " A\tbase-web\n"
        self.assertEqual(
            staged_typings_verdict(run_outer=self._fixed(raw),
                                   run_baseweb=self._boom_run),
            "unknown")

    def test_baseweb_diff_failure_verdict_unknown(self):
        self.assertEqual(
            staged_typings_verdict(run_outer=self._fixed(_RAW_GITLINK),
                                   run_baseweb=self._fixed("", returncode=128)),
            "unknown")

    def test_typings_pathspec_scopes_common_and_api(self):
        seen = {}

        def spy_baseweb(argv):
            seen["argv"] = argv
            return subprocess.CompletedProcess(argv, 0, "", "")

        staged_typings_verdict(run_outer=self._fixed(_RAW_GITLINK),
                               run_baseweb=spy_baseweb)
        self.assertIn("src/typings/common.d.ts", seen["argv"])
        self.assertIn("src/typings/api", seen["argv"])
        self.assertIn("base-web", seen["argv"])


def _real_anchor_texts():
    """六支錨檔之真檔內容（副本字串的出發點；反例一律改副本、不改真檔）。"""
    texts = {}
    for rel in ANCHOR_FILES:
        with open(os.path.join(REPO_ROOT, *rel.split("/")), encoding="utf-8") as fh:
            texts[rel] = fh.read()
    return texts


def _replace_once(text, old, new):
    """副本字串內恰一處替換——出發形不在或不唯一即 AssertionError（反例打偏＝測試自身失準、不得靜默綠）。"""
    if text.count(old) != 1:
        raise AssertionError(f"反例出發形須恰一處：{old!r}（實得 {text.count(old)} 處）")
    return text.replace(old, new)


def _write_anchor_tree(root, texts):
    for rel, text in texts.items():
        path = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)


# 反例參數名 → 錨檔（TestAnchorLegs._problems 用）。
ANCHOR_KEYS = {"options": AXIOS_OPTIONS_TS, "package": AXIOS_PACKAGE_JSON, "rust": SYS_MENU_RS,
               "routes": ELEGANT_ROUTES_TS, "custom": CUSTOM_ROUTES_TS, "builtin": BUILTIN_ROUTES_TS}


class TestAnchorLegs(unittest.TestCase):
    """兩腿判準紅綠（BL-00109 qs 前提；ADR-00044 決定 8 保留路由名）：以真檔副本為出發形、逐一植入反例——
    改序列化器選項／拿掉或註解掉序列化器／改 qs 版本；rust 側與前端 routes.ts、builtin.ts 各增刪一名、rust 側註解掉一名、
    rust 側宣告多出一處；routes.ts 常量路由缺 `name` 紅；customRoutes 增一常量路由（rust 未跟紅、同批跟上綠）、增非常量路由綠、
    陣列字面找不到／宣告多出一處／方括號不成對／常量路由缺 `name` 紅。"""

    def setUp(self):
        self.real = _real_anchor_texts()

    def _problems(self, **mutated):
        texts = dict(self.real)
        texts.update({ANCHOR_KEYS[k]: v for k, v in mutated.items()})
        with tempfile.TemporaryDirectory() as root:
            _write_anchor_tree(root, texts)
            return anchor_problems(root)

    def _assert_red(self, needle, **mutated):
        problems = self._problems(**mutated)
        self.assertTrue(problems, "植入反例須紅")
        self.assertTrue(any(needle in p for p in problems),
                        f"紅須指名 {needle!r}；實得 {problems}")

    def test_real_file_copies_pass(self):
        self.assertEqual(self._problems(), [])

    # ── BL-00109 qs 前提腿 ──
    def test_serializer_with_options_red(self):
        self._assert_red("paramsSerializer", options=_replace_once(
            self.real[AXIOS_OPTIONS_TS], "return stringify(params);",
            "return stringify(params, { strictNullHandling: true });"))

    def test_serializer_removed_red(self):
        self._assert_red("paramsSerializer", options=_replace_once(
            self.real[AXIOS_OPTIONS_TS],
            "    paramsSerializer: params => {\n      return stringify(params);\n    }\n", ""))

    def test_serializer_commented_out_red(self):
        """註解掉的序列化器不是生效碼（axios 回預設＝null 欄整個丟掉）——判準去註解後才比對。兩形：逐行 `//`；以及
        `/* … */` 包住的單行表達式體——後者去空白後字面仍合判準形，只有去註解擋得住。"""
        serializer = "    paramsSerializer: params => {\n      return stringify(params);\n    }\n"
        for commented in ("    // paramsSerializer: params => {\n    //   return stringify(params);\n    // }\n",
                          "    /* paramsSerializer: params => stringify(params), */\n"):
            self._assert_red("paramsSerializer", options=_replace_once(
                self.real[AXIOS_OPTIONS_TS], serializer, commented))

    def test_stringify_not_from_qs_red(self):
        self._assert_red("from 'qs'", options=_replace_once(
            self.real[AXIOS_OPTIONS_TS], "import { stringify } from 'qs';",
            "import { stringify } from 'query-string';"))

    def test_qs_version_changed_red(self):
        pkg = json.loads(self.real[AXIOS_PACKAGE_JSON])
        self.assertEqual(pkg["dependencies"]["qs"], QS_PINNED_VERSION, "出發形須為釘版")
        pkg["dependencies"]["qs"] = "6.14.0"
        self._assert_red("6.14.0", package=json.dumps(pkg))

    # ── ADR-00044 決定 8 保留路由名對賬腿 ──
    RUST_DECL = ('pub const RESERVED_ROUTE_NAMES: [&str; 7] =\n'
                 '    ["403", "404", "500", "iframe-page", "login", "root", "not-found"];')

    def test_rust_side_add_one_red(self):
        self._assert_red("about", rust=_replace_once(
            self.real[SYS_MENU_RS], self.RUST_DECL,
            'pub const RESERVED_ROUTE_NAMES: [&str; 8] =\n'
            '    ["403", "404", "500", "iframe-page", "login", "root", "not-found", "about"];'))

    def test_rust_side_remove_one_red(self):
        self._assert_red("login", rust=_replace_once(
            self.real[SYS_MENU_RS], self.RUST_DECL,
            'pub const RESERVED_ROUTE_NAMES: [&str; 6] =\n'
            '    ["403", "404", "500", "iframe-page", "root", "not-found"];'))

    def test_rust_side_name_commented_out_red(self):
        """註解掉的成員不是生效碼（常數真少了該名、新增寫端放得過）——rust 側判準去註解後才比對。兩形：行尾 `//` 註掉一名
        （多行陣列）；`/* */` 註掉一名，且宣告型別寫 `&'static str`——生命週期號 `'` 不得被當成字串起點而把註解連帶保留。"""
        for commented in ('pub const RESERVED_ROUTE_NAMES: [&str; 6] = [\n'
                          '    "403", "404", "500", "iframe-page", "login", "not-found", // "root",\n];',
                          "pub const RESERVED_ROUTE_NAMES: [&'static str; 6] =\n"
                          '    ["403", "404", "500", "iframe-page", "login", /* "root", */ "not-found"];'):
            self._assert_red("root", rust=_replace_once(self.real[SYS_MENU_RS], self.RUST_DECL, commented))

    def test_rust_side_decl_duplicated_red(self):
        """rust 側宣告多出一處（檔尾模組內另宣告同名常數、多一名）＝紅——「恰一處」之上界自證：不得靜默取第一處。"""
        extra = ("\nmod legacy {\n    pub const RESERVED_ROUTE_NAMES: [&str; 8] =\n"
                 '        ["403", "404", "500", "iframe-page", "login", "root", "not-found", "shadow"];\n}\n')
        self._assert_red("宣告須恰一處（實得 2 處", rust=self.real[SYS_MENU_RS] + extra)

    def test_routes_constant_add_one_red(self):
        self._assert_red("about", routes=_replace_once(
            self.real[ELEGANT_ROUTES_TS], "      title: 'about',\n",
            "      title: 'about',\n      constant: true,\n"))

    def test_routes_constant_remove_one_red(self):
        self._assert_red("login", routes=_replace_once(
            self.real[ELEGANT_ROUTES_TS], "      i18nKey: 'route.login',\n      constant: true,\n",
            "      i18nKey: 'route.login',\n"))

    def test_routes_constant_nameless_red(self):
        """routes.ts 增一條 `name` 非字串字面之常量路由（名集不變）＝解析失準即紅、不因集合相等放行。"""
        decl = "export const generatedRoutes: GeneratedRoute[] = [\n"
        self._assert_red(f"{ELEGANT_ROUTES_TS}：`meta.constant: true` 所屬物件缺 `name`", routes=_replace_once(
            self.real[ELEGANT_ROUTES_TS], decl,
            decl + _replace_once(self.CUSTOM_EXTRA, "name: 'extra-custom'", "name: EXTRA_NAME")))

    CUSTOM_DECL = "const customRoutes: CustomRoute[] = [\n"
    CUSTOM_EXTRA = ("  {\n    name: 'extra-custom',\n    path: '/extra-custom',\n"
                    "    component: 'layout.blank$view.404',\n"
                    "    meta: {\n      title: 'extra-custom',\n      constant: true\n    }\n  },\n")

    def test_custom_routes_real_literal_parsed(self):
        """讀面進入自證（真檔）：customRoutes 陣列字面止於其配對方括號（不溢到 createStaticRoutes）、解析得路由名、
        現值零常量路由（潛伏面、綠）。"""
        literal, problems = custom_routes_literal(self.real[CUSTOM_ROUTES_TS])
        self.assertEqual(problems, [])
        self.assertTrue(literal.startswith("[") and literal.endswith("]"), literal[:40])
        self.assertNotIn("createStaticRoutes", literal)
        names, constants, parse_problems = ts_route_names(literal, CUSTOM_ROUTES_TS)
        self.assertEqual(parse_problems, [])
        self.assertTrue({"exception", "exception_403", "document", "document_vue"} <= names, names)
        self.assertEqual(constants, set())

    def test_custom_routes_constant_add_one_red(self):
        """customRoutes 新增一條 `meta.constant: true` 路由而 rust 常數未跟＝紅（createStaticRoutes 會把它併入常量路由）。"""
        self._assert_red("extra-custom", custom=_replace_once(
            self.real[CUSTOM_ROUTES_TS], self.CUSTOM_DECL, self.CUSTOM_DECL + self.CUSTOM_EXTRA))

    def test_custom_routes_constant_add_with_rust_follow_green(self):
        """對應綠案：同一植入、rust 常數同批跟上＝綠（判準是集合相等、非「customRoutes 一改即紅」）。"""
        problems = self._problems(
            custom=_replace_once(self.real[CUSTOM_ROUTES_TS], self.CUSTOM_DECL,
                                 self.CUSTOM_DECL + self.CUSTOM_EXTRA),
            rust=_replace_once(self.real[SYS_MENU_RS], self.RUST_DECL,
                               'pub const RESERVED_ROUTE_NAMES: [&str; 8] =\n'
                               '    ["403", "404", "500", "iframe-page", "login", "root", "not-found",'
                               ' "extra-custom"];'))
        self.assertEqual(problems, [])

    def test_custom_routes_nonconstant_add_green(self):
        """customRoutes 新增非常量路由＝綠（createStaticRoutes 將其歸 authRoutes、不入保留集）。"""
        extra = self.CUSTOM_EXTRA.replace(",\n      constant: true\n", "\n")
        self.assertNotIn("constant", extra)
        self.assertEqual(self._problems(custom=_replace_once(
            self.real[CUSTOM_ROUTES_TS], self.CUSTOM_DECL, self.CUSTOM_DECL + extra)), [])

    def test_custom_routes_array_missing_red(self):
        """customRoutes 陣列字面找不到（改名／改形）＝解析失準即紅、不當零常量放行。"""
        self._assert_red("customRoutes", custom=_replace_once(
            self.real[CUSTOM_ROUTES_TS], self.CUSTOM_DECL, "const extraRoutes: CustomRoute[] = [\n"))

    def test_custom_routes_array_duplicated_red(self):
        """customRoutes 宣告多出一處（檔尾函式內另宣告同名陣列、帶一條常量路由）＝解析失準即紅——
        「恰一處」之上界自證：不得靜默取第一處字面、讓第二處之常量路由漏出對賬。"""
        extra = ("\nexport function legacyRoutes() {\n  " + self.CUSTOM_DECL
                 + _replace_once(self.CUSTOM_EXTRA, "name: 'extra-custom'", "name: 'shadow'")
                 + "  ];\n  return customRoutes;\n}\n")
        self._assert_red("陣列字面須恰一處（實得 2 處", custom=self.real[CUSTOM_ROUTES_TS] + extra)

    def test_custom_routes_constant_nameless_red(self):
        """customRoutes 常量路由之 `name` 非字串字面（解析不出名）＝解析失準即紅、不當零常量放行
        （customRoutes 無零成員守衛、此違規即唯一防線）。"""
        self._assert_red(f"{CUSTOM_ROUTES_TS}：`meta.constant: true` 所屬物件缺 `name`", custom=_replace_once(
            self.real[CUSTOM_ROUTES_TS], self.CUSTOM_DECL,
            self.CUSTOM_DECL + _replace_once(self.CUSTOM_EXTRA, "name: 'extra-custom'", "name: EXTRA_NAME")))

    def test_custom_routes_array_unbalanced_red(self):
        """customRoutes 陣列收尾 `];` 缺（方括號不成對）＝解析失準即紅、不當零常量放行。"""
        self._assert_red("customRoutes 陣列方括號不成對", custom=_replace_once(
            self.real[CUSTOM_ROUTES_TS], "  }\n];\n\n/** create routes when the auth route mode is static */",
            "  }\n\n/** create routes when the auth route mode is static */"))

    def test_builtin_add_one_red(self):
        self._assert_red("extra-builtin", builtin=_replace_once(
            self.real[BUILTIN_ROUTES_TS], "/** builtin routes",
            "const EXTRA_ROUTE: CustomRoute = {\n  name: 'extra-builtin',\n  path: '/extra',\n"
            "  meta: {\n    title: 'extra',\n    constant: true\n  }\n};\n\n/** builtin routes"))

    def test_builtin_remove_one_red(self):
        start = self.real[BUILTIN_ROUTES_TS].index("const NOT_FOUND_ROUTE")
        end = self.real[BUILTIN_ROUTES_TS].index("};\n", start) + len("};\n")
        text = _replace_once(self.real[BUILTIN_ROUTES_TS], self.real[BUILTIN_ROUTES_TS][start:end], "")
        text = _replace_once(text, "[ROOT_ROUTE, NOT_FOUND_ROUTE]", "[ROOT_ROUTE]")
        self._assert_red("not-found", builtin=text)

    def test_missing_anchor_file_red_not_skip(self):
        for missing in (BUILTIN_ROUTES_TS, CUSTOM_ROUTES_TS):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as root:
                texts = dict(self.real)
                del texts[missing]
                _write_anchor_tree(root, texts)
                problems = anchor_problems(root)
                self.assertTrue(any(missing in p for p in problems), problems)



class TestCheckAnchorsUnconditional(unittest.TestCase):
    """兩腿在 cmd_check 的位置：合成 self-test 之後、staged-gate 短路與容器探測之前**無條件**執行——
    staged-gate 判跳過、容器不可用，兩腿都照跑；違規 rc 2 且不觸任何容器／git 子行程。"""

    @staticmethod
    def _boom(argv):
        raise AssertionError("錨腿違規即 return 2、不得觸發容器探測／重抽／git")

    @staticmethod
    def _unstaged(argv):
        return subprocess.CompletedProcess(argv, 0, "", "")   # 兩側 gitlink 皆未 staged＝收窄判跳過

    def _tree(self, root, qs_version=QS_PINNED_VERSION):
        texts = _real_anchor_texts()
        pkg = json.loads(texts[AXIOS_PACKAGE_JSON])
        pkg["dependencies"]["qs"] = qs_version
        texts[AXIOS_PACKAGE_JSON] = json.dumps(pkg)
        _write_anchor_tree(root, texts)

    def test_staged_gate_skip_still_runs_legs_healthy(self):
        """正向：收窄判跳過時，錨腿先跑且通過、才輪到跳過訊息（位置先於短路）。"""
        with tempfile.TemporaryDirectory() as root:
            self._tree(root)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = cmd_check(staged_gate=True, run=self._boom, run_outer=self._unstaged,
                               run_baseweb=self._boom, run_rustapi=self._boom, anchor_root=root)
        self.assertEqual(rc, 0)
        text = out.getvalue()
        self.assertIn("跨子庫錨兩腿通過", text)
        self.assertIn("跳過", text)
        self.assertLess(text.index("跨子庫錨兩腿通過"), text.index("跳過"))

    def test_staged_gate_skip_still_runs_legs_red(self):
        """反向：收窄本會判跳過，錨腿違規照樣 rc 2（不被短路吞掉）。"""
        with tempfile.TemporaryDirectory() as root:
            self._tree(root, qs_version="6.14.0")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = cmd_check(staged_gate=True, run=self._boom, run_outer=self._unstaged,
                               run_baseweb=self._boom, run_rustapi=self._boom, anchor_root=root)
        self.assertEqual(rc, 2)
        self.assertIn("6.14.0", err.getvalue())
        self.assertNotIn("跳過", out.getvalue())

    def test_container_unavailable_still_runs_legs_red(self):
        """容器不可用本會具名跳過 rc 0；錨腿違規先一步 rc 2（位置先於容器探測、純讀檔不觸容器）。"""
        with tempfile.TemporaryDirectory() as root:
            self._tree(root, qs_version="6.14.0")
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                rc = cmd_check(run=self._boom, anchor_root=root)
        self.assertEqual(rc, 2)


class TestCheckUsage(unittest.TestCase):
    def test_check_rejects_unknown_flag_exit64(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["wire-schema.py", "check", "--bogus"]), 64)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def usage(msg=None):
    """用法錯誤：usage 走 stderr、exit 64（EX_USAGE）。"""
    if msg:
        print(msg, file=sys.stderr)
    print(__doc__, file=sys.stderr)
    return 64


def main(argv):
    if len(argv) < 2:
        return usage()
    cmd = argv[1]
    if cmd == "test":
        result = unittest.main(argv=[argv[0]], exit=False, verbosity=1).result
        return 0 if result.wasSuccessful() else 1
    if cmd == "extract":
        if argv[2:]:
            return usage(f"extract：不收參數（見 {' '.join(argv[2:])}）")
        return cmd_extract()
    if cmd == "check":
        extra = [a for a in argv[2:] if a != "--staged-gate"]
        if extra:
            return usage(f"check：僅收 --staged-gate（見 {' '.join(extra)}）")
        return cmd_check(staged_gate="--staged-gate" in argv[2:])
    return usage(f"未知子命令：{cmd}")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
