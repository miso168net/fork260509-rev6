#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/seed-view-gate.py — 碼面閘：後端 seed 選單所綁之頁 ⊆ base-web 實有之頁（006 刀 U14；ADR-00071、BL-00045；
承 rev5:tools/seed-view-gate.py 之 rev5:006 原始版（rev5 commit `9d709d4`、豁免表恰兩列）重打字新寫；行為契約＝docs/ops/reference-src/code-gate-contracts.md 之 seed-view-gate 節；
名冊＝RUNBOOK §12 碼面閘表）

子命令：
  check   （預設）讀 seed 檔、views 樹、imports.ts 三面後判定；綠時逐列印出仍生效之具名豁免
  test    離線 self-test（暫存目錄合成 fixtures＋對本檔自身之豁免表四釘；零 docker、零網路、不讀真 repo）

守什麼：
  sys_menu 列之 component 欄（`view.<鍵>`；帶佈局者 `layout.base$view.<鍵>`）是側欄項找到前端頁面的唯一憑據，兩端之間卻沒有任何
  型別或編譯關聯——seed 指向不存在之頁、或頁目錄被搬走改名而 seed 未跟，型別檢查、測試與其餘碼面閘一律照綠，症狀只在瀏覽器現形
  （側欄點擊無反應、直打網址 404、標題顯路由裸鍵；BL-00045）。本閘把這條斷裂改成 commit 級訊號。

判準（三個集合、兩條腿）：
  seed 集＝[`SEED_REL`] 內行首 `const SEED_SYS_MENU: &str = r#"` 之後、至其第一個 `"#` 為止之 raw 字串區間中，全部 `view.<鍵>` 字面去重
    （帶佈局形照收）；區間外——其他 seed 常數、反向 SQL、doc 註解、收尾符同一行之後——一律不收。每鍵記下 seed 檔行號與該行 sys_menu 列 id。
  views 集＝[`VIEWS_REL`] 依 elegant-router 0.3.8 預設頁檔規則導出（base-web/build/plugins/router.ts 未覆寫 pageDir、pagePatterns、
    pageExcludePatterns 與 routeNameTransformer；下列各條逐一對照 base-web 依賴樹中 @elegant-router/core 之 dist 原碼實查）：
      · 頁檔＝檔名恰為 `index.vue`，或 `[<識別字>].vue`（參數頁；參數只進路徑、鍵取所在目錄）；modules 下元件、.ts 等不產鍵
      · 任一層目錄名為 `components` 者整棵排除（頂層亦同）
      · 頁檔須至少有一層上層目錄，且每層目錄名合 [`RE_DIR_NAME`]（ASCII）——外掛對不合者只警告、不產路由
      · 鍵＝各層目錄名中不以 `_` 起首者以 `_` 串接後轉小寫（`_builtin` 這類分組層不入鍵）
  imports 集＝[`IMPORTS_REL`] 之 `export const views … = {` 塊內各列 `<鍵>: () => import(` 之鍵（裸鍵或雙引號鍵；layouts 塊不收）。
  ①缺 view 腿：seed 集 − views 集 − 具名豁免 ≠ ∅ ⇒ 紅，逐鍵指名 seed 檔行號與列 id。方向是單向包含——頁面有而 seed 無
    （例 login、未上選單之頁）屬合法不對稱。
  ②結構腿：views 集 ≠ imports 集 ⇒ 紅，兩向差集分向指名。本檔導出規則與外掛實跑脫節、或頁目錄已動而產物未重算，都在此現形；
    兩腿互不遮蔽（頁目錄被搬走而產物未重算＝兩腿同報）。
  射程只及 seed 檔：超管經選單管理自建之選單、m0003 起之 delta migration 所寫選單列都不在內（ADR-00071）。

具名豁免（[`EXEMPT`]）：
  恰兩列＝seed 列 9 與列 77 之兩鍵，各附 BL-00045 與解除謂詞；表是模組常數之唯讀檢視，不接受 args、env 或讀檔來源。
  到期即紅＝被豁免之鍵已出現在 views 集（頁已交付而列未摘）；幽靈亦紅＝被豁免之鍵已不在 seed 集。兩者都逼人同批摘列——表只會縮。
  self-test 對本檔自身打四根釘、各封一條繞道、互不覆蓋：
    鍵集恆定——表恰為那兩鍵、每列含指針與解除謂詞（多養一列＝當場紅；要養就得同批改斷言、在 diff 現形＝拍板級可見）；
    呼叫點原封傳入——run_check 內唯一的 judge 呼叫以 EXEMPT 本名為末實參（先併一份外來表再傳＝紅）；
    判定函式零外部取值形——三支解析函式與 judge 之原文不得出現讀檔、環境變數、命令列、stdin、json 之取值字面（run_check 只准讀檔）；
    呼叫端零就地改表——EXEMPT 為唯讀檢視、全檔恰一處綁定且無 global 宣告、測試類以外恰一處引用（即上述末實參；judge 或 main 另行直讀即多一處）。
  ★射程自陳：四釘守的是字面形與佈線；刻意繞開字面者（反射、動態拼名）仍靠人審，不是形式證明。

讀面型（ADR-00055 決定 3；本閘為首例）：
  (a) base-web `src/views/**` 與 `src/router/elegant/imports.ts`＝pre-commit submodule-sync 段之 base-web 閘面內＝延後偵測：外層單獨 commit 時
      可能判到工作樹，下一次 pin bump 時該段要求閘面乾淨、屆時補抓。
  (b) rust-api `migration/src/m0002_baseline_seeds.rs`＝閘面外、無兜底：該檔有未 commit 改動時本閘判的是工作樹（pin bump 時亦同）。
      不擴閘面——該檔程式內容依憲法 §I.5 例外② 鎖定（ADR-00009），任何改動本身即越例外射程、須另立 ADR 翻案。
退出碼：0 綠／1 紅（缺 view、豁免到期或幽靈、views 集≠imports 集；合併列出）／2 結構異常（seed 檔、SEED_SYS_MENU 塊、views 目錄、
  imports.ts 或其 views 塊任一缺席，或任一側掃得空集——只會「找不到缺漏」的對賬器一側空掉即恆綠；RL-0051）／64 用法錯。
  tracked 面缺席一律 rc 2，工具與 pre-commit 段皆不設具名跳過（ADR-00019 決定 4）；兩子庫工作樹在場由 bootstrap 斷言。
check 不連帶跑 self-test（ADR-00071 決定 6②）：自測只吃合成 fixtures、結果只隨本檔而變，本檔 staged 時 pre-commit `for` 自測迴圈必跑其
  test、bootstrap 體檢亦跑，check 內再跑屬重複。此為與 rev5 藍本之刻意分岔——藍本於 check 內連帶跑，是為換取不入自測迴圈之具名豁免，
  該豁免機制 rev6 不存在。
依賴：Python 3 標準庫、零 docker、零網路。接線：pre-commit seed-view-gate 段（base-web／rust-api pin bump 或本檔 staged 時跑 check）、
  `for` 自測迴圈與 bootstrap 名冊（test）、README 樹、RUNBOOK §12 兩表。
"""
import ast
import contextlib
import inspect
import io
import os
import re
import sys
import tempfile
import types
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_REL = os.path.join("rust-api", "migration", "src", "m0002_baseline_seeds.rs")
VIEWS_REL = os.path.join("base-web", "src", "views")
IMPORTS_REL = os.path.join("base-web", "src", "router", "elegant", "imports.ts")
TAG = "[seed-view-gate]"
USAGE = "用法：tools/seed-view-gate.py [check|test]"

# seed 側：塊頭須在行首（doc 註解裡抄出的同形字串不算）；塊尾＝塊頭之後第一個 raw 字串收尾符。
RE_SEED_HEAD = re.compile(r'^const SEED_SYS_MENU: &str = r#"', re.M)
RAW_STR_END = '"#'
RE_VIEW_TOKEN = re.compile(r"\bview\.([A-Za-z0-9_-]+)")
RE_ROW_ID = re.compile(r"^\((\d+),")

# views 側：elegant-router 0.3.8 預設頁檔規則（出處見檔頭）；兩支正則皆 ASCII 語意、與外掛之 JS 正則同義。
PAGE_INDEX = "index.vue"
RE_PAGE_PARAM = re.compile(r"\[\w+\]\.vue", re.A)
RE_DIR_NAME = re.compile(r"[\w-]+[0-9a-zA-Z]+", re.A)
EXCLUDED_DIR = "components"
GROUP_PREFIX = "_"
KEY_JOIN = "_"

# imports 側：只取 views 匯出塊（layouts 塊即使有懶載入列也不收）；塊尾＝行首之 `};`。
RE_VIEWS_BLOCK = re.compile(r"^export const views\b[^\n]*\{\n(.*?)^\};", re.M | re.S)
RE_IMPORT_KEY = re.compile(r'^\s*(?:"([^"]+)"|([A-Za-z0-9_$]+))\s*:\s*\(\)\s*=>\s*import\(', re.M)

# 具名豁免（ADR-00071 決定 2）：鍵＝seed component 字面；值＝指針與解除謂詞。唯讀檢視＝執行期無從就地增列；
# 「恰兩列、各含 BL-00045 與解除謂詞」由 self-test TestExemptInvariants 釘死（語意與四釘見檔頭）。
EXEMPT = types.MappingProxyType({
    "view.manage_system-settings": "BL-00045（seed 列 9 之系統設定頁尚未交付）；解除謂詞＝本鍵之 view 出現於導出集即到期、同批摘列",
    "view.manage_audit": "BL-00045（seed 列 77 之稽核頁尚未交付）；解除謂詞＝本鍵之 view 出現於導出集即到期、同批摘列",
})


class StructuralError(Exception):
    """讀面缺席或任一側掃得空集（rc 2）：訊息即輸出行之主體。"""


def parse_seed(text):
    """seed 檔全文 → {`view.<鍵>`: [(檔內行號, sys_menu 列 id 或 None), …]}。塊缺席、未收尾或塊內零字面＝StructuralError。"""
    head = RE_SEED_HEAD.search(text)
    if head is None:
        raise StructuralError("seed 檔內找不到行首 `const SEED_SYS_MENU: &str = r#\"` 之塊")
    end = text.find(RAW_STR_END, head.end())
    if end < 0:
        raise StructuralError("SEED_SYS_MENU 塊未收尾（塊頭之後找不到 raw 字串收尾符）")
    first_line = text.count("\n", 0, head.end()) + 1
    found = {}
    for offset, line in enumerate(text[head.end():end].split("\n")):
        row = RE_ROW_ID.match(line)
        for key in RE_VIEW_TOKEN.findall(line):
            found.setdefault("view." + key, []).append((first_line + offset, int(row.group(1)) if row else None))
    if not found:
        raise StructuralError("SEED_SYS_MENU 塊內零個 view.<鍵> 字面（seed 側空集）")
    return found


def derive_views(root):
    """views 樹根 → {路由鍵: 頁檔相對路徑（/ 分隔）}。零頁檔＝StructuralError。"""
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d != EXCLUDED_DIR)
        rel = os.path.relpath(dirpath, root)
        parts = [] if rel == os.curdir else rel.split(os.sep)
        if not parts or not all(RE_DIR_NAME.fullmatch(p) for p in parts):
            continue
        key = KEY_JOIN.join(p for p in parts if not p.startswith(GROUP_PREFIX)).lower()
        for name in sorted(filenames):
            if name == PAGE_INDEX or RE_PAGE_PARAM.fullmatch(name):
                found[key] = "/".join(parts + [name])
    if not found:
        raise StructuralError("views 樹下零頁檔（index.vue／[參數].vue；views 側空集）")
    return found


def parse_imports(text):
    """imports.ts 全文 → views 匯出塊之鍵集。塊缺席或零鍵＝StructuralError。"""
    block = RE_VIEWS_BLOCK.search(text)
    if block is None:
        raise StructuralError("imports.ts 內找不到行首 `export const views … = {` 匯出塊")
    keys = {quoted or bare for quoted, bare in RE_IMPORT_KEY.findall(block.group(1))}
    if not keys:
        raise StructuralError("imports.ts views 匯出塊內零個 `() => import(` 鍵（imports 側空集）")
    return keys


def judge(seed, views, imports_keys, exempt):
    """純判定 → (rc, 輸出行)：rc 0 綠／1 紅。四個實參皆由呼叫端備妥；本函式不碰檔案、環境與模組級豁免表。"""
    seed_posix = SEED_REL.replace(os.sep, "/")
    imports_posix = IMPORTS_REL.replace(os.sep, "/")
    derived = set(views)
    present = {"view." + k for k in derived}
    lines = []
    only_derived = sorted(derived - imports_keys)
    only_imports = sorted(imports_keys - derived)
    if only_derived or only_imports:
        lines.append(f"{TAG} ✗ views 導出集 ≠ {imports_posix} views 鍵集（導出規則與外掛脫節，或頁目錄已動而產物未重算）：")
        lines += [f"  導出有、imports.ts 無：{k}（{views[k]}）——頁已加而外掛未重算、或產物未 commit？" for k in only_derived]
        lines += [f"  imports.ts 有、導出無：{k}——頁目錄已搬走或改名、或本檔導出規則與外掛脫節？" for k in only_imports]
    missing = sorted(k for k in seed if k not in present and k not in exempt)
    if missing:
        lines.append(f"{TAG} ✗ seed 選單 component 有 {len(missing)} 鍵在 base-web 找不到頁（側欄點擊無反應、直打網址 404）：")
        for k in missing:
            where = "、".join(f"{seed_posix}:{ln}（列 {rid}）" if rid is not None else f"{seed_posix}:{ln}" for ln, rid in seed[k])
            lines.append(f"  {k}  ←  {where}")
        lines.append("  補救：補上該頁（外掛重算之產物同 commit）；改 seed 越憲法 §I.5 例外②、須另立 ADR；暫容＝拍板級、走 BACKLOG 指針進本檔 EXEMPT")
    lines += [f"{TAG} ✗ 豁免到期：{k} 的頁已存在——自 EXEMPT 摘列（{exempt[k]}）" for k in sorted(exempt) if k in present]
    lines += [f"{TAG} ✗ 幽靈豁免：{k} 已不在 seed 選單 component——自 EXEMPT 摘列（{exempt[k]}）" for k in sorted(exempt) if k not in seed]
    if lines:
        return 1, lines
    exempted = sorted(exempt)
    lines.append(f"{TAG} ✓ seed 選單 view 鍵 {len(seed)} 個中 {len(seed) - len(exempted)} 個皆有頁、{len(exempted)} 個在具名豁免內"
                 f"（views 導出 {len(derived)} 鍵＝imports.ts views 鍵集）")
    lines += [f"{TAG}   豁免仍生效：{k}——{exempt[k]}" for k in exempted]
    return 0, lines


def run_check(repo_root):
    """讀真檔三面 → (rc, 輸出行)。讀面缺席與各側空集＝rc 2（逐面指名）；其餘交 judge，豁免表原封傳入。"""
    seed_path = os.path.join(repo_root, SEED_REL)
    views_root = os.path.join(repo_root, VIEWS_REL)
    imports_path = os.path.join(repo_root, IMPORTS_REL)
    absent = [rel.replace(os.sep, "/") for rel, path, exists in ((SEED_REL, seed_path, os.path.isfile),
                                                                 (VIEWS_REL, views_root, os.path.isdir),
                                                                 (IMPORTS_REL, imports_path, os.path.isfile)) if not exists(path)]
    if absent:
        return 2, [f"{TAG} ✗ 讀面缺席：{'、'.join(absent)}——tracked 面缺席不設跳過（ADR-00019 決定 4）；子庫工作樹未就位跑 bash tools/bootstrap.sh"]
    try:
        with open(seed_path, encoding="utf-8") as fh:
            seed = parse_seed(fh.read())
        views = derive_views(views_root)
        with open(imports_path, encoding="utf-8") as fh:
            imports_keys = parse_imports(fh.read())
    except StructuralError as ex:
        return 2, [f"{TAG} ✗ 結構異常：{ex}——掃描面為空或形制已變不算綠（RL-0051）"]
    return judge(seed, views, imports_keys, EXEMPT)


def _say(msg, err=False):
    print(msg, file=sys.stderr if err else sys.stdout, flush=True)


# ── self-test（離線；暫存目錄合成 fixtures，一律實跑上方生產函式）────────────────────

SEED_POSIX = SEED_REL.replace(os.sep, "/")
IMPORTS_POSIX = IMPORTS_REL.replace(os.sep, "/")
VIEWS_POSIX = VIEWS_REL.replace(os.sep, "/")


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _seed_text(rows, before="", after=""):
    """合成 seed 檔：rows＝[(列 id, component 欄值)]；before 夾在塊前、after 接在收尾符同一行之後（兩者皆塊外誘餌）。"""
    head = 'const SEED_SYS_MENU: &str = r#"INSERT INTO "sys_menu" ("id", "route_name", "component") VALUES\n'
    body = ",\n".join(f"({rid}, 'r{rid}', '{comp}')" for rid, comp in rows)
    return before + head + body + ';"#;' + after + "\n"


def _views_tree(root, pages):
    for rel in pages:
        _write(os.path.join(root, *rel.split("/")), "<template><div /></template>\n")
    return root


def _imports_text(keys):
    """合成 imports.ts（外掛產物形）：layouts 塊在前且含一列懶載入誘餌（`blank`），views 塊在後；需引號之鍵加雙引號。"""
    out = ["/* eslint-disable */", "// Generated by elegant-router", "",
           "export const layouts: Record<RouteLayout, RouteComponent | (() => Promise<RouteComponent>)> = {",
           "  base: BaseLayout,", '  blank: () => import("@/layouts/blank-layout/index.vue"),', "};", "",
           "export const views: Record<LastLevelRouteKey, RouteComponent | (() => Promise<RouteComponent>)> = {"]
    for key in sorted(keys):
        lit = key if re.fullmatch(r"[A-Za-z0-9_$]+", key) else f'"{key}"'
        out.append(f'  {lit}: () => import("@/views/{key}/index.vue"),')
    return "\n".join(out + ["};"]) + "\n"


def _fake_repo(tmp, rows, pages, import_keys, skip=()):
    """合成 repo 根：seed 檔、views 樹、imports.ts 三面；skip 內之面不建（缺席案）。"""
    if "seed" not in skip:
        _write(os.path.join(tmp, SEED_REL), _seed_text(rows))
    if "views" not in skip:
        _views_tree(os.path.join(tmp, VIEWS_REL), pages)
    if "imports" not in skip:
        _write(os.path.join(tmp, IMPORTS_REL), _imports_text(import_keys))
    return tmp


class TestParseSeed(unittest.TestCase):
    """seed 集：只收 SEED_SYS_MENU raw 字串區間內之字面；行號以檔為基準、列 id 取該行開頭。"""

    def test_block_only_tokens_with_file_line_and_row_id(self):
        """塊內同鍵多列各記一筆、帶佈局形照收；塊外五處誘餌（doc 註解、行首非 const 之假塊頭、他常數前後、收尾符同行之後）皆不收"""
        text = _seed_text([(10, "view.alpha_one"), (12, "view.alpha_one"), (13, "layout.base$view.beta_two"), (14, "layout.base")],
                          before=('/// 塊外 doc 註解：view.in_doc\n'
                                  '/// const SEED_SYS_MENU: &str = r#"view.fake_head\n'
                                  'const UNSEED_SYS_MENU: &str = r#"view.before_block"#;\n'),
                          after=' // view.after_tail\nconst OTHER: &str = r#"view.other_block"#;')
        got = parse_seed(text)
        self.assertEqual(got, {"view.alpha_one": [(5, 10), (6, 12)], "view.beta_two": [(7, 13)]})

    def test_absent_unterminated_or_tokenless_block_raises(self):
        """塊頭缺席、只在註解內出現、塊未收尾、塊內零 view 字面——四者皆結構異常"""
        row = "(1, 'r1', 'view.alpha_one')"
        for label, text in (
                ("塊頭缺席", 'const OTHER: &str = r#"' + row + '"#;\n'),
                ("塊頭只在註解內", '/// const SEED_SYS_MENU: &str = r#"' + row + '"#;\n'),
                ("塊未收尾", 'const SEED_SYS_MENU: &str = r#"INSERT\n' + row + ";\n"),
                ("塊內零 view 字面", _seed_text([(2, "layout.base")]))):
            with self.subTest(label), self.assertRaises(StructuralError):
                parse_seed(text)


class TestDeriveViews(unittest.TestCase):
    """views 集：elegant-router 0.3.8 預設頁檔規則逐形（規則出處見檔頭）。"""

    def test_default_page_rules_each_form(self):
        """分組層剝除／參數頁鍵取所在目錄／modules 與 .ts 非頁／components 整棵排除（含頂層）／根層頁與不合法目錄名略過／檔名大小寫敏感／鍵轉小寫"""
        pages = ["_builtin/login/index.vue", "_builtin/iframe-page/[url].vue", "home/index.vue",
                 "manage/user-detail/[id].vue", "manage/ip-rule/index.vue", "manage/ip-rule/modules/ip-rule-search.vue",
                 "manage/menu/modules/shared.ts", "multi-menu/first_child/index.vue", "Gallery/Photo/index.vue",
                 "plugin/charts/components/index.vue", "components/widget/index.vue", "index.vue", "x/index.vue",
                 "trailing-/index.vue", "notes/Index.vue", "report/[a-b].vue", "about/index.vue"]
        with tempfile.TemporaryDirectory() as tmp:
            got = derive_views(_views_tree(os.path.join(tmp, "views"), pages))
        self.assertEqual(got, {"login": "_builtin/login/index.vue", "iframe-page": "_builtin/iframe-page/[url].vue",
                               "home": "home/index.vue", "manage_user-detail": "manage/user-detail/[id].vue",
                               "manage_ip-rule": "manage/ip-rule/index.vue", "multi-menu_first_child": "multi-menu/first_child/index.vue",
                               "gallery_photo": "Gallery/Photo/index.vue", "about": "about/index.vue"})

    def test_zero_pages_raises(self):
        """樹內只有非頁檔與被排除之頁＝空集、結構異常"""
        with tempfile.TemporaryDirectory() as tmp:
            root = _views_tree(os.path.join(tmp, "views"), ["manage/role/modules/role-search.vue", "plugin/components/index.vue"])
            with self.assertRaises(StructuralError):
                derive_views(root)


class TestParseImports(unittest.TestCase):
    """imports 集：只收 views 匯出塊；裸鍵、雙引號鍵、數字鍵皆收。"""

    def test_key_forms_and_views_block_only(self):
        """layouts 塊內之懶載入列（blank）不收"""
        got = parse_imports(_imports_text(["403", "manage_menu", "manage_ip-rule", "iframe-page"]))
        self.assertEqual(got, {"403", "manage_menu", "manage_ip-rule", "iframe-page"})

    def test_absent_or_empty_views_block_raises(self):
        """views 塊缺席（只剩 layouts）與 views 塊零鍵——兩者皆結構異常"""
        full = _imports_text(["home"])
        for label, text in (("views 塊缺席", full[:full.index("export const views")]),
                            ("views 塊零鍵", _imports_text([]))):
            with self.subTest(label), self.assertRaises(StructuralError):
                parse_imports(text)


class TestJudge(unittest.TestCase):
    """判定本體（純函式、合成集合）：兩腿與豁免語意各一正一反；兩向差集拆成兩組單向案。"""

    def _run(self, seed, views, imports_keys, exempt):
        rc, lines = judge(seed, views, imports_keys, exempt)
        return rc, "\n".join(lines)

    def test_missing_view_is_red_and_names_key_line_and_row(self):
        """缺 view：逐鍵指名 seed 檔行號與列 id（同鍵多列全列）；在場之鍵不被點名"""
        rc, text = self._run({"view.alpha_one": [(5, 3)], "view.beta_two": [(7, 5), (9, 8)]},
                             {"alpha_one": "alpha/one/index.vue"}, {"alpha_one"}, {})
        self.assertEqual(rc, 1, text)
        for frag in ("view.beta_two", f"{SEED_POSIX}:7（列 5）", f"{SEED_POSIX}:9（列 8）"):
            self.assertIn(frag, text)
        self.assertNotIn("view.alpha_one", text)

    def test_all_present_is_green_and_one_way(self):
        """全在＝綠；頁面有而 seed 無（login）不紅＝單向包含"""
        views = {"alpha_one": "alpha/one/index.vue", "beta_two": "beta/two/index.vue", "login": "_builtin/login/index.vue"}
        rc, text = self._run({"view.alpha_one": [(5, 3)], "view.beta_two": [(6, 4)]}, views, set(views), {})
        self.assertEqual(rc, 0, text)
        self.assertNotIn("✗", text)

    def test_exemption_masks_missing_and_is_listed(self):
        """豁免生效：缺頁之鍵在豁免表＝綠，綠訊息列出該鍵與其指針"""
        rc, text = self._run({"view.alpha_one": [(5, 3)], "view.gamma_three": [(9, 9)]},
                             {"alpha_one": "alpha/one/index.vue"}, {"alpha_one"}, {"view.gamma_three": "合成指針"})
        self.assertEqual(rc, 0, text)
        self.assertIn("view.gamma_three", text)
        self.assertIn("合成指針", text)

    def test_expired_exemption_is_red(self):
        """豁免到期：被豁免之鍵已有頁＝紅並指名"""
        views = {"alpha_one": "alpha/one/index.vue", "gamma_three": "gamma/three/index.vue"}
        rc, text = self._run({"view.alpha_one": [(5, 3)], "view.gamma_three": [(9, 9)]}, views, set(views),
                             {"view.gamma_three": "合成指針"})
        self.assertEqual(rc, 1, text)
        self.assertIn("豁免到期：view.gamma_three", text)

    def test_ghost_exemption_is_red(self):
        """幽靈豁免：被豁免之鍵已不在 seed 集＝紅並指名"""
        rc, text = self._run({"view.alpha_one": [(5, 3)]}, {"alpha_one": "alpha/one/index.vue"}, {"alpha_one"},
                             {"view.zeta_nine": "合成指針"})
        self.assertEqual(rc, 1, text)
        self.assertIn("幽靈豁免：view.zeta_nine", text)

    def test_derived_extra_is_red_and_only_that_direction(self):
        """結構腿（導出多出向＝加了頁而產物未重算）：只報該向"""
        views = {"alpha_one": "alpha/one/index.vue", "beta_two": "beta/two/index.vue"}
        rc, text = self._run({"view.alpha_one": [(5, 3)]}, views, {"alpha_one"}, {})
        self.assertEqual(rc, 1, text)
        self.assertIn("導出有、imports.ts 無：beta_two", text)
        self.assertNotIn("imports.ts 有、導出無", text)

    def test_imports_extra_is_red_and_only_that_direction(self):
        """結構腿（imports 多出向＝頁已搬走或導出規則與外掛脫節）：只報該向"""
        rc, text = self._run({"view.alpha_one": [(5, 3)]}, {"alpha_one": "alpha/one/index.vue"}, {"alpha_one", "delta_four"}, {})
        self.assertEqual(rc, 1, text)
        self.assertIn("imports.ts 有、導出無：delta_four", text)
        self.assertNotIn("導出有、imports.ts 無", text)

    def test_moved_page_without_regen_reports_both_legs(self):
        """頁目錄被搬走而產物未重算：缺 view 腿與結構腿同報、互不遮蔽"""
        rc, text = self._run({"view.alpha_one": [(5, 3)], "view.beta_two": [(6, 11)]}, {"alpha_one": "alpha/one/index.vue"},
                             {"alpha_one", "beta_two"}, {})
        self.assertEqual(rc, 1, text)
        self.assertIn(f"view.beta_two  ←  {SEED_POSIX}:6（列 11）", text)
        self.assertIn("imports.ts 有、導出無：beta_two", text)


class TestRunCheck(unittest.TestCase):
    """check 全鏈（合成 repo 根）：真豁免表經 run_check 生效；三面缺席與各側空集皆 rc 2。"""

    ROWS = [(3, "view.manage_user"), (9, "view.manage_system-settings"), (11, "layout.base$view.about"), (77, "view.manage_audit")]
    PAGES = ["manage/user/index.vue", "about/index.vue", "_builtin/login/index.vue"]
    KEYS = {"manage_user", "about", "login"}

    def test_green_lists_both_real_exemptions(self):
        """真豁免表兩鍵缺頁＝綠，輸出逐列印出兩鍵與 BL-00045"""
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, self.ROWS, self.PAGES, self.KEYS))
        text = "\n".join(lines)
        self.assertEqual(rc, 0, text)
        for key in ("view.manage_system-settings", "view.manage_audit"):
            self.assertTrue(any(key in ln and "BL-00045" in ln for ln in lines), text)

    def test_real_table_expires_through_check(self):
        """稽核頁交付而豁免未摘＝經 run_check 到期即紅"""
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, self.ROWS, self.PAGES + ["manage/audit/index.vue"], self.KEYS | {"manage_audit"}))
        text = "\n".join(lines)
        self.assertEqual(rc, 1, text)
        self.assertIn("豁免到期：view.manage_audit", text)

    def test_absent_read_face_is_rc2_and_named(self):
        """seed 檔、views 目錄、imports.ts 任一缺席＝rc 2、指名該面"""
        for face, rel in (("seed", SEED_POSIX), ("views", VIEWS_POSIX), ("imports", IMPORTS_POSIX)):
            with self.subTest(face), tempfile.TemporaryDirectory() as tmp:
                rc, lines = run_check(_fake_repo(tmp, self.ROWS, self.PAGES, self.KEYS, skip=(face,)))
                self.assertEqual(rc, 2, lines)
                self.assertIn(rel, "\n".join(lines))

    def test_empty_side_is_rc2(self):
        """seed 塊零 view 字面、views 樹零頁檔、imports views 塊零鍵——各側空集皆 rc 2"""
        for label, rows, pages, keys in (("seed 側空集", [(2, "layout.base")], self.PAGES, self.KEYS),
                                         ("views 側空集", self.ROWS, ["manage/role/modules/role-search.vue"], self.KEYS),
                                         ("imports 側空集", self.ROWS, self.PAGES, set())):
            with self.subTest(label), tempfile.TemporaryDirectory() as tmp:
                rc, lines = run_check(_fake_repo(tmp, rows, pages, keys))
                self.assertEqual(rc, 2, lines)


class TestExemptInvariants(unittest.TestCase):
    """豁免表四釘：對本檔自身之常數與原文判，各封一條摘紅燈的繞道、互不覆蓋（射程自陳見檔頭）。"""

    BANNED_JUDGE = ("open(", "read_text", "read_bytes", "environ", "getenv", "argv", "stdin", "input(", "json")
    BANNED_CALLER = ("environ", "getenv", "argv", "stdin", "input(", "json")

    @staticmethod
    def _module_tree():
        return ast.parse(inspect.getsource(sys.modules[__name__]))

    def test_table_is_exactly_two_rows_with_pointer_and_predicate(self):
        """鍵集恆定：恰為 seed 列 9／列 77 兩鍵，且每列含 BL-00045 與解除謂詞"""
        self.assertEqual(set(EXEMPT), {"view.manage_system-settings", "view.manage_audit"},
                         "豁免表增減列屬拍板級——須同批改本斷言（ADR-00071 決定 2）")
        for key, why in EXEMPT.items():
            self.assertIn("BL-00045", why, key)
            self.assertIn("解除謂詞", why, key)

    def test_check_passes_table_verbatim(self):
        """呼叫點原封傳入：run_check 內恰一處 judge 呼叫，四個位置實參、末實參為 EXEMPT 本名"""
        fn = next(n for n in ast.walk(self._module_tree()) if isinstance(n, ast.FunctionDef) and n.name == "run_check")
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "judge"]
        self.assertEqual(len(calls), 1, "run_check 內 judge 呼叫須恰一處")
        call = calls[0]
        self.assertEqual((len(call.args), call.keywords), (4, []), ast.dump(call))
        self.assertTrue(isinstance(call.args[-1], ast.Name) and call.args[-1].id == "EXEMPT", ast.dump(call.args[-1]))

    def test_judgement_path_has_no_external_input_forms(self):
        """判定函式零外部取值形：解析三支與 judge 不得出現讀檔／環境／命令列／stdin／json 字面；run_check 只准讀檔"""
        for fn in (parse_seed, derive_views, parse_imports, judge):
            src = inspect.getsource(fn)
            for tok in self.BANNED_JUDGE:
                self.assertNotIn(tok, src, f"{fn.__name__}() 出現 {tok!r}")
        src = inspect.getsource(run_check)
        for tok in self.BANNED_CALLER:
            self.assertNotIn(tok, src, f"run_check() 出現 {tok!r}")

    def test_callers_never_mutate_or_rebind_table(self):
        """呼叫端零就地改表：唯讀檢視、全檔恰一處綁定且無 global 宣告、測試類以外恰一處引用（judge 或 main 直讀即多一處）"""
        self.assertIsInstance(EXEMPT, types.MappingProxyType)
        tree = self._module_tree()
        stores = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "EXEMPT" and not isinstance(n.ctx, ast.Load)]
        self.assertEqual(len(stores), 1, "EXEMPT 綁定處須恰一（模組層定義）")
        self.assertFalse([n for n in ast.walk(tree) if isinstance(n, (ast.Global, ast.Nonlocal)) and "EXEMPT" in n.names])
        loads = [n for top in tree.body if not isinstance(top, ast.ClassDef)
                 for n in ast.walk(top) if isinstance(n, ast.Name) and n.id == "EXEMPT" and isinstance(n.ctx, ast.Load)]
        self.assertEqual(len(loads), 1, f"測試類以外 EXEMPT 引用 {len(loads)} 處（應恰 1＝傳進 judge 之末實參）")


class TestUsage(unittest.TestCase):
    def test_unknown_subcommand_or_extra_args_is_rc64(self):
        for argv in (["seed-view-gate.py", "nope"], ["seed-view-gate.py", "check", "x"], ["seed-view-gate.py", "test", "x"]):
            err = io.StringIO()
            with self.subTest(argv=argv[1:]), contextlib.redirect_stderr(err):
                self.assertEqual(main(argv), 64)
            self.assertIn("用法：", err.getvalue())


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    if len(argv) > 2 or cmd not in ("check", "test"):
        _say(USAGE, err=True)
        return 64
    if cmd == "test":
        ok = unittest.main(argv=[argv[0]], exit=False, verbosity=1).result.wasSuccessful()
        if ok:
            _say(f"{TAG} ✓ self-test 過（seed 塊內解析與塊外誘餌／導出規則逐形／imports 只收 views 塊／缺 view・豁免生效・到期・幽靈・"
                 f"結構腿兩向各自單向・兩腿同報／check 全鏈經真豁免表綠與到期・三面缺席與三側空集 rc 2／豁免表四釘／用法守衛）")
        return 0 if ok else 1
    rc, lines = run_check(REPO_ROOT)
    for ln in lines:
        _say(ln, err=bool(rc))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
