#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/view-render-guard.py — 碼面閘：管理頁目錄零原始 HTML 注入寫法（004 刀 U8；spec FR-052、`docs/ops/reference-src/code-gate-contracts.md` §3①；
承 rev5:tools/view-render-guard.py 新寫；名冊＝RUNBOOK §12 碼面閘表）＋管理頁表頭 prop 形正面錨（005 刀 U13 起 IP 規則頁：BL-00117、
`specs/005-role-menu-crud/spec.md` FR-062；007 刀 U18 擴為 [`ANCHORS`] 所列各頁：`specs/007-user-password-admin/spec.md` FR-048）

子命令：
  check   （預設）兩腿皆跑：①逐行掃 base-web/src/views/manage/** 之 `.vue`／`.ts`／`.tsx`／`.js`／`.jsx`；命中 [`FORBIDDEN`] 任一條即 rc 1、
          逐處指名檔:行 ②[`ANCHORS`] 所列各錨檔之表頭正面錨（見下）；不成立即 rc 1、逐處指名檔:行
  test    離線 self-test（暫存樹、毫秒級、零 docker）

守什麼：
  ①管理頁的自由文字欄（IP 規則備註為首例）承載使用者可寫的原文。預設插值會逸出標記字元；改成原始 HTML 注入寫法後，
    欄值是純文字時畫面完全相同，型別檢查（皆 string）與畫面比對都分不出來——只有掃原文擋得住。
  ②[`ANCHORS`] 所列各頁表頭的寫入口由共用表頭元件之兩布林 prop 控制（新增鈕與批刪鈕各綁該頁之按鈕碼或模式條件、值見該表）。
    呼叫端一旦改回覆寫 default 插槽，覆寫內容就不受兩 prop 控制；覆寫成空時 Vue 還會改渲染元件自帶的備援按鈕——無權帳號反而看見
    寫入口。prop 缺漏或插槽覆寫型別檢查都照綠，而「有頁面權限、無寫入按鈕碼」的帳號未必在 seed 裡、瀏覽器走查未必觸得到，
    故以模板靜態斷言守。
不變式：
  · 腿①逐行比對原文、不分註解與碼、不解析語法：判定面沒有可錯位的 tokenizer；代價＝射程內連註解都不得寫出被禁字面（本檔不在射程內）。
  · 腿②正面錨三條、皆對各錨檔原文判（註解內字面同計）：
    (a) 每個 `<TableHeaderOperation` 開標籤都帶該檔於 [`ANCHORS`] 之兩屬性且值逐字相符（錨值逐檔各用各的、不跨檔通用）；
    (b) 該標籤自閉合，或標籤體內只有具名插槽 template 子節點（指令＝[`NAMED_SLOTS`]：`#prefix`／`#suffix`／`v-slot:prefix`／
        `v-slot:suffix`）、空白與 HTML 註解——共用表頭元件的這兩個插槽沒有備援內容。其他任何子節點都是 default 插槽內容、即紅；
        逐形列舉：元件或元素、純文字、插值、未帶插槽指令之 template、`v-slot` 無引數、其他插槽名、動態插槽名、
        同一 template 帶兩個以上插槽指令（含具名 prefix／suffix 與他名並列）、
        `#default`／`v-slot:default` 之 template（此形 (c) 亦紅）。標籤體之區段界＝對應之 `</TableHeaderOperation>`（其後之兄弟節點不入判、
        不取到檔尾）；缺閉合標籤（延伸到檔尾）、具名插槽 template 未閉合亦紅；具名插槽內之內層 template 以深度計、其內 HTML 註解整段跳過；
    (c) 檔內零 [`DEFAULT_SLOT`] 字面（`#default`／`v-slot:default`）。
    錨檔內零個該開標籤＝不成立（正面錨無實例不算綠）。開標籤之終點以引號外第一個 `>` 判（屬性值內的 `>` 不誤斷）。
    射程外（機器守不及；逐項附承載）：
      · 同名 prop 之其他繫結寫法（靜態屬性、`v-bind` 物件展開、camelCase 別名）與錨屬性並存時之覆蓋序——承載＝審查兜底；
      · kebab-case 標籤名之第二個表頭——承載＝審查兜底；
      · 具名 prefix／suffix 插槽內之內容（放什麼鈕、鈕是否依按鈕碼顯隱都不判；自測釘此形照綠）——常駐承載＝審查兜底；一次性承載＝
        007 刀 U18 出口之按鈕碼 grep 斷言（IP 規則頁 `hasAuth('ipRule:unlock')` 恰 1）與瀏覽器走查（`specs/007-user-password-admin/quickstart.md`
        §10 IP 規則頁列：不持碼者不見）；兩者皆非常駐閘——其後拔該鈕之顯隱條件，本閘照綠。
  · 腿①掃到零檔、腿②任一錨檔缺席＝rc 2、不是綠：射程目錄或錨檔被搬走或改名時，只會「找不到違規」的掃描器即恆綠（RL-0051）。
    [`ANCHORS`] 刪一列＝該頁表頭失守而 `check` 照綠，故錨表逐列逐值由自測釘住。
  · base-web 工作樹缺席＝rc 2 fail-loud、工具與 pre-commit 段皆不設跳過（ADR-00019 決定 4：tracked 面缺席不類推環境缺席）。
退出碼：0 綠／1 命中（任一腿）／2 工作樹、射程或任一錨檔缺席、零受掃檔／64 用法錯。
接線：pre-commit view-render-guard 段（`base-web` pin bump 或本檔 staged 時 `check`）、`for` 自測迴圈與 bootstrap 名冊（`test`）、
  README 樹、RUNBOOK §12 兩表。self-test 不隨 `check` 連帶跑（入迴圈者由迴圈承擔、不重複）。
"""
import contextlib
import io
import os
import re
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKTREE_REL = os.path.join("base-web", "src")
SCAN_REL = os.path.join(WORKTREE_REL, "views", "manage")
SCAN_EXTS = (".vue", ".ts", ".tsx", ".js", ".jsx")   # 現況射程內零 .js／.jsx；仍列入＝該類檔日後落入時不致靜默不掃
TAG = "[view-render-guard]"
USAGE = "用法：tools/view-render-guard.py [check|test]"

# 被禁字面：(正則, 說明)。每條都是「把字串當標記交給瀏覽器解析」的入口；增列須同批在 [`COUNTEREXAMPLES`] 配反例（self-test 鍵集對賬）。
# rev5 同表另有 React 式 prop 與 Vue 2 式 prop 兩條——在 Vue 3 皆不構成注入入口（只會落成一般屬性），不帶入。
FORBIDDEN = (
    (re.compile(r"\bv-html\b"), "Vue 模板之原始 HTML 指令"),
    (re.compile(r"\binnerHTML\b"), "DOM innerHTML（含 JSX／render 函式之同名 prop）"),
    (re.compile(r"\bouterHTML\b"), "DOM outerHTML"),
    (re.compile(r"\binsertAdjacentHTML\b"), "DOM insertAdjacentHTML"),
    # `(?:ln)?` 不可省：`write` 與 `ln` 之間無詞界，少了它 `document.writeln` 不命中。
    (re.compile(r"\bdocument\.write(?:ln)?\b"), "document.write／writeln 直寫文件流"),
)


# 腿②：管理頁表頭正面錨（005 刀 U13 起 IP 規則頁＝BL-00117；007 刀 U18 擴為逐頁具名表）。鍵＝錨檔路徑（相對 repo 根）、
# 值＝該頁表頭之兩錨屬性（屬性名, 雙引號值）、逐字比對且逐檔各用各的（改寫法或增刪錨頁＝同批改本常數與自測之錨表釘值）。
ANCHORS = {
    os.path.join(SCAN_REL, "ip-rule", "index.vue"): ((":show-add", "hasAuth('ipRule:add')"), (":show-delete", "false")),
    os.path.join(SCAN_REL, "user", "index.vue"): ((":show-add", "!showDeleted && hasAuth('user:add')"),
                                                  (":show-delete", "!showDeleted && hasAuth('user:delete')")),
}
ANCHOR_TAG = re.compile(r"<TableHeaderOperation(?=[\s/>])")
ANCHOR_CLOSE = re.compile(r"</TableHeaderOperation\s*>")
# 標籤體內唯一放行之插槽指令（縮寫與 `v-slot:` 長形）；共用表頭元件的這兩個插槽沒有備援內容、不牽動兩 prop 所控之寫入口。
NAMED_SLOTS = frozenset(("#prefix", "#suffix", "v-slot:prefix", "v-slot:suffix"))
DEFAULT_SLOT = re.compile(r"#default\b|\bv-slot:default\b")
# 屬性名＋可選之引號值；單引號值也吃掉，免得其內的雙引號錯配後續屬性。
_ATTR = re.compile(r"""([^\s"'<>/=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'))?""")
_SPACE = re.compile(r"\s*")
_TEMPLATE_OPEN = re.compile(r"<template(?=[\s/>])")
_TEMPLATE_CLOSE = re.compile(r"</template\s*>")


class ScopeError(Exception):
    """工作樹或射程缺席、零受掃檔（rc 2）：訊息即輸出行。"""


def _say(msg, err=False):
    print(msg, file=sys.stderr if err else sys.stdout, flush=True)


def scan_tree(root):
    """掃一棵樹 → (findings, 受掃檔數)；findings＝[(相對路徑, 行號, 說明, 該行去頭尾空白之原文)]。零受掃檔＝ScopeError。"""
    findings, count = [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            if not name.endswith(SCAN_EXTS):
                continue
            count += 1
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            with open(path, encoding="utf-8", errors="replace") as fh:
                for lineno, line in enumerate(fh, 1):
                    findings += [(rel, lineno, why, line.strip()) for pattern, why in FORBIDDEN if pattern.search(line)]
    if not count:
        raise ScopeError(f"{root} 底下零受掃檔（{'／'.join(SCAN_EXTS)}）")
    return findings, count


def _line_of(text, index):
    return text.count("\n", 0, index) + 1


def _tag_end(text, i):
    """自 `i` 起找引號外第一個 `>` → 其索引；缺終點＝`len(text)`（標籤延伸到檔尾）。"""
    quote = None
    while i < len(text):
        ch = text[i]
        if quote:
            quote = None if ch == quote else quote
        elif ch in "\"'":
            quote = ch
        elif ch == ">":
            return i
        i += 1
    return i


def _open_tags(text):
    """錨檔原文 → [(行號, {(屬性名, 雙引號值)}, 開標籤終點索引, 是否自閉合)]；缺終點即延伸到檔尾（視為非自閉合）。"""
    tags = []
    for m in ANCHOR_TAG.finditer(text):
        end = _tag_end(text, m.end())
        body = text[m.end():end]
        closed = end < len(text) and body.rstrip().endswith("/")
        tags.append((_line_of(text, m.start()), {(name, dq) for name, dq, _ in _ATTR.findall(body)}, end, closed))
    return tags


def _skip_template(text, pos):
    """`pos`＝某 template 開標籤之後 → 其對應 `</template>` 之後的索引（內層 template 計深度、HTML 註解整段跳過）；未閉合＝None。"""
    depth = 1
    while depth:
        nxt = min((i for i in (text.find("<!--", pos), text.find("<template", pos), text.find("</template", pos)) if i >= 0),
                  default=-1)
        if nxt < 0:
            return None
        if text.startswith("<!--", nxt):
            end = text.find("-->", nxt + 4)
            if end < 0:
                return None
            pos = end + 3
        elif (close := _TEMPLATE_CLOSE.match(text, nxt)) is not None:
            depth -= 1
            pos = close.end()
        elif (inner := _TEMPLATE_OPEN.match(text, nxt)) is not None:
            end = _tag_end(text, inner.end())
            depth += not text[inner.end():end].rstrip().endswith("/")
            pos = end + 1
        else:   # `<templateX`、`</templateX` 一類非標籤字面：跳過續找
            pos = nxt + 1
    return pos


def _body_problem(text, pos):
    """非自閉合表頭之標籤體（自 `pos` 起）→ None（合規）或 (行號, 說明)。只放行 [`NAMED_SLOTS`] 之具名插槽 template、
    空白與 HTML 註解；區段界＝對應之 `</TableHeaderOperation>`（不取到檔尾）；首個違規子節點即回、不續判其後。"""
    while True:
        pos = _SPACE.match(text, pos).end()
        if pos >= len(text):
            return (_line_of(text, pos), "缺 </TableHeaderOperation> 閉合標籤——標籤體延伸到檔尾")
        if ANCHOR_CLOSE.match(text, pos):
            return None
        if text.startswith("<!--", pos):
            end = text.find("-->", pos + 4)
            if end < 0:
                return (_line_of(text, pos), "標籤體內 HTML 註解未閉合")
            pos = end + 3
            continue
        tmpl = _TEMPLATE_OPEN.match(text, pos)
        if tmpl:
            end = _tag_end(text, tmpl.end())
            head = text[tmpl.end():end]
            slots = {name for name, _, _ in _ATTR.findall(head) if name.startswith(("#", "v-slot"))}
            if len(slots) == 1 and slots <= NAMED_SLOTS:
                after = end + 1 if head.rstrip().endswith("/") else _skip_template(text, end + 1)
                if after is None:
                    return (_line_of(text, pos), f"具名插槽 template 未閉合：{text[pos:end + 1].strip()}")
                pos = after
                continue
        excerpt = text[pos:].split("\n", 1)[0].strip()
        return (_line_of(text, pos), f"標籤體內有具名 prefix／suffix 插槽以外之子節點——即 default 插槽內容、不受兩 prop 控制：{excerpt}")


def check_anchor(text, attrs):
    """腿②判定（`attrs`＝該錨檔於 [`ANCHORS`] 之兩錨屬性）→ [(行號, 說明)]（空＝錨成立）。三條各自出列，互不遮蔽。"""
    problems = []
    tags = _open_tags(text)
    if not tags:
        problems.append((1, "零個 <TableHeaderOperation 開標籤——正面錨無實例"))
    for lineno, found, end, closed in tags:
        problems += [(lineno, f'缺 {name}="{value}"（屬性名與值逐字比對）') for name, value in attrs if (name, value) not in found]
        if not closed and (bad := _body_problem(text, end + 1)) is not None:
            problems.append(bad)
    for lineno, line in enumerate(text.splitlines(), 1):
        if DEFAULT_SLOT.search(line):
            problems.append((lineno, f"default 插槽覆寫字面：{line.strip()}"))
    return sorted(problems)


def run_check(repo_root):
    """→ (rc, 輸出行清單)。四種 rc 2 各自具名（補救動作不同：建工作樹／查射程搬移／查副檔名／查錨檔搬移）；兩腿之違規合併列出、rc 1。"""
    scan_rel = SCAN_REL.replace(os.sep, "/")
    if not os.path.isdir(os.path.join(repo_root, WORKTREE_REL)):
        return 2, [f"{TAG} ✗ base-web 工作樹缺席（{WORKTREE_REL.replace(os.sep, '/')}/ 不在）——跑 bash tools/bootstrap.sh 建置"]
    root = os.path.join(repo_root, SCAN_REL)
    if not os.path.isdir(root):
        return 2, [f"{TAG} ✗ 射程目錄缺席：{scan_rel}/——被搬走或改名？本閘在該情形不得靜默放行（射程＝本檔 SCAN_REL）"]
    try:
        findings, count = scan_tree(root)
    except ScopeError as ex:
        return 2, [f"{TAG} ✗ {ex}——掃描面為空不算綠（RL-0051）"]
    missing = [rel.replace(os.sep, "/") for rel in ANCHORS if not os.path.isfile(os.path.join(repo_root, rel))]
    if missing:
        return 2, [f"{TAG} ✗ 表頭錨檔缺席：{rel}——被搬走或改名？正面錨無標的不得靜默放行（錨檔＝本檔 ANCHORS）" for rel in missing]
    anchored, problems = [], []
    for rel, attrs in ANCHORS.items():
        with open(os.path.join(repo_root, rel), encoding="utf-8", errors="replace") as fh:
            anchor_text = fh.read()
        anchor_rel = rel.replace(os.sep, "/")
        anchored.append((anchor_rel, len(_open_tags(anchor_text))))
        problems += [(anchor_rel, lineno, why) for lineno, why in check_anchor(anchor_text, attrs)]
    lines = []
    if findings:
        lines += [f"{TAG} ✗ 管理頁出現原始 HTML 注入寫法 {len(findings)} 處（specs/004-ip-trust-anchor/spec.md FR-052：自由文字欄一律純文字插值；註解內字面同計）："]
        lines += [f"  {scan_rel}/{rel}:{lineno}  {why}\n      {text}" for rel, lineno, why, text in findings]
        lines.append("  補救：改回預設插值（模板 `{{ }}`／render 函式回字串）；確有原始標記需求＝拍板級、走 ADR")
    if problems:
        lines.append(f"{TAG} ✗ 管理頁表頭脫離 prop 形 {len(problems)} 處（BL-00117；specs/005-role-menu-crud/spec.md FR-062、"
                     "specs/007-user-password-admin/spec.md FR-048；註解內字面同計）：")
        lines += [f"  {rel}:{lineno}  {why}" for rel, lineno, why in problems]
        lines.append("  補救：表頭以兩布林 prop 控制寫入口（各錨檔之屬性與值＝本檔 ANCHORS）、標籤體內只放具名 prefix／suffix 插槽 template、"
                     "不覆寫 default 插槽——覆寫內容不受兩 prop 控制、無權帳號會看見寫入口")
    if lines:
        return 1, lines
    return 0, ([f"{TAG} ✓ {scan_rel}/** 零原始 HTML 注入寫法（受掃 {count} 檔、{len(FORBIDDEN)} 條被禁字面）"]
               + [f"{TAG} ✓ {rel} 表頭 prop 形錨成立（{n} 個開標籤皆帶兩錨屬性、自閉合或標籤體只含具名 prefix／suffix 插槽、"
                  "零 default 插槽覆寫字面）" for rel, n in anchored])


# ── self-test（離線；一律實跑上方生產函式）────────────────────────────────────

CLEAN_VUE = ("<script setup lang=\"ts\">\nconst memo = 'plain';\n</script>\n\n"
             "<template>\n  <span>{{ memo }}</span>\n</template>\n")
IP_REL = os.path.join(SCAN_REL, "ip-rule", "index.vue")
IP_ATTRS = ANCHORS[IP_REL]
# 腿②正案：自閉合正形之縮影（錨值取 `ANCHORS` 之 IP 規則頁列；多行開標籤、兩錨屬性夾在其他屬性之間、自閉合）；第 6 行同 CLEAN_VUE（腿①命中案沿用行號）。
ANCHORED_VUE = ("<script setup lang=\"ts\">\nconst memo = 'plain';\n</script>\n\n"
                "<template>\n  <span>{{ memo }}</span>\n"
                "  <TableHeaderOperation\n    v-model:columns=\"columnChecks\"\n    :loading=\"loading\"\n"
                "    :show-add=\"hasAuth('ipRule:add')\"\n    :show-delete=\"false\"\n    @add=\"handleAdd\"\n"
                "    @refresh=\"getData\"\n  />\n</template>\n")
_IP_ATTR_LINES = "    :show-add=\"hasAuth('ipRule:add')\"\n    :show-delete=\"false\"\n"
# 改回覆寫插槽之形（004 刀 as-built 表頭之縮影）：非自閉合＋default 插槽 template、兩錨屬性皆缺。
OVERRIDE_VUE = ANCHORED_VUE.replace(_IP_ATTR_LINES + "    @add=\"handleAdd\"\n", "").replace(
    "    @refresh=\"getData\"\n  />\n",
    "    @refresh=\"getData\"\n  >\n    <template #default>\n      <NButton @click=\"handleAdd\">add</NButton>\n"
    "    </template>\n  </TableHeaderOperation>\n")
# 錨頁現行之具名前綴插槽形（IP 規則頁表頭之縮影）：對標籤、體內只有一個 `#prefix` template（內含受按鈕碼顯隱之鈕）。
_PREFIX_BODY = ("    <template #prefix>\n"
                "      <NButton v-if=\"hasAuth('ipRule:unlock')\" @click=\"openUnlock\">unlock</NButton>\n"
                "    </template>\n")
PREFIX_VUE = ANCHORED_VUE.replace("    @refresh=\"getData\"\n  />\n",
                                  "    @refresh=\"getData\"\n  >\n" + _PREFIX_BODY + "  </TableHeaderOperation>\n")
# 鍵＝該條正則原文；值＝植入片段，★每一非空行皆須被該條抓到（同族變體逐行列；只驗「有一行紅」則規則被改窄仍綠）。
COUNTEREXAMPLES = (
    (r"\bv-html\b", '<template><span v-html="memo"></span></template>\n'),
    (r"\binnerHTML\b", "el.innerHTML = memo;\nh('span', { innerHTML: memo });\n"),
    (r"\bouterHTML\b", "el.outerHTML = memo;\n"),
    (r"\binsertAdjacentHTML\b", "el.insertAdjacentHTML('beforeend', memo);\n"),
    (r"\bdocument\.write(?:ln)?\b", "document.write(memo);\ndocument.writeln(memo);\n"),
)


def _with_body(body):
    """PREFIX_VUE 之標籤體換成 `body`（開標籤之 `>` 與閉合標籤不動）。"""
    return PREFIX_VUE.replace(_PREFIX_BODY, body)


def _anchored_for(attrs):
    """自閉合正形、兩錨屬性換成 `attrs`（[`ANCHORS`] 之一列）。"""
    text = ANCHORED_VUE.replace(_IP_ATTR_LINES, "".join(f'    {name}="{value}"\n' for name, value in attrs))
    assert attrs == IP_ATTRS or text != ANCHORED_VUE, "錨屬性替換未生效"
    return text


def _anchor_files(overrides=None):
    """[`ANCHORS`] 每一錨檔之正形（{相對 SCAN_REL 之路徑: 內容}）；`overrides` 同鍵覆寫、值 None＝不寫該檔。"""
    files = {os.path.relpath(rel, SCAN_REL).replace(os.sep, "/"): _anchored_for(attrs) for rel, attrs in ANCHORS.items()}
    files.update(overrides or {})
    return {rel: content for rel, content in files.items() if content is not None}


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _fake_repo(tmp, files):
    """合成 repo 根：`files`＝{相對 SCAN_REL 之路徑: 內容}；回根路徑。"""
    for rel, content in files.items():
        _write(os.path.join(tmp, SCAN_REL, *rel.split("/")), content)
    return tmp


class TestScan(unittest.TestCase):
    def test_clean_tree_is_green_and_counts_nested_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fake_repo(tmp, {"ip-rule/index.vue": CLEAN_VUE, "ip-rule/modules/search.vue": CLEAN_VUE,
                                    "ip-rule/shared.ts": "export const a = 1;\n", "ip-rule/cell.tsx": "export const b = 2;\n",
                                    "ip-rule/legacy.js": "export const c = 3;\n", "ip-rule/cell2.jsx": "export const d = 4;\n",
                                    "ip-rule/notes.md": "不在射程內之副檔名、不計\n"})
            found, count = scan_tree(os.path.join(root, SCAN_REL))
        self.assertEqual(found, [])
        self.assertEqual(count, 6)

    def test_counterexample_table_matches_forbidden_one_to_one(self):
        rules = [p.pattern for p, _ in FORBIDDEN]
        keys = [k for k, _ in COUNTEREXAMPLES]
        self.assertEqual(len(rules), len(set(rules)), "FORBIDDEN 有重複正則")
        self.assertEqual(len(keys), len(set(keys)), "反例表有重複鍵（某條湊數、另一條無反例）")
        self.assertEqual(set(keys), set(rules), "有規則沒反例＝該條從未被證明會紅")

    def test_every_counterexample_line_is_caught_by_its_own_rule(self):
        by_source = {p.pattern: why for p, why in FORBIDDEN}
        for idx, (source, snippet) in enumerate(COUNTEREXAMPLES):
            with tempfile.TemporaryDirectory() as tmp:
                root = _fake_repo(tmp, {"ip-rule/index.vue": CLEAN_VUE, f"ip-rule/evil{idx}.vue": snippet})
                found, _ = scan_tree(os.path.join(root, SCAN_REL))
            caught = {ln for rel, ln, why, _ in found if rel == f"ip-rule/evil{idx}.vue" and why == by_source[source]}
            want = {n for n, text in enumerate(snippet.splitlines(), 1) if text.strip()}
            self.assertEqual(want - caught, set(), f"{source}：第 {sorted(want - caught)} 行未被該條抓到，實得 {found}")

    def test_literal_inside_comment_is_still_red(self):
        """不變式「不分註解與碼」：HTML 註解與 `//` 註解內之被禁字面照紅（改成剝註解後再判＝本案紅）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = _fake_repo(tmp, {"ip-rule/index.vue": "<!-- 勿用 v-html -->\n" + CLEAN_VUE,
                                    "ip-rule/util.ts": "// el.outerHTML 不可用\nexport {};\n"})
            found, _ = scan_tree(os.path.join(root, SCAN_REL))
        self.assertEqual([(rel, ln) for rel, ln, _, _ in found], [("ip-rule/index.vue", 1), ("ip-rule/util.ts", 1)])

    def test_out_of_scope_extension_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fake_repo(tmp, {"ip-rule/index.vue": CLEAN_VUE, "ip-rule/NOTE.md": '<span v-html="x"></span>\n'})
            found, count = scan_tree(os.path.join(root, SCAN_REL))
        self.assertEqual((found, count), ([], 1))


class TestAnchorRoster(unittest.TestCase):
    def test_anchor_roster_is_pinned_row_by_row(self):
        """錨表逐列逐值釘：刪一列＝該頁表頭失守而 `check` 照綠（少判一檔不會紅）、改一值＝錨檔現形對不上——兩者都只有本案擋得住。
        增刪錨頁或改錨值＝同批改 [`ANCHORS`] 與本表。"""
        got = {os.path.relpath(rel, SCAN_REL).replace(os.sep, "/"): attrs for rel, attrs in ANCHORS.items()}
        self.assertEqual(got, {
            "ip-rule/index.vue": ((":show-add", "hasAuth('ipRule:add')"), (":show-delete", "false")),
            "user/index.vue": ((":show-add", "!showDeleted && hasAuth('user:add')"),
                               (":show-delete", "!showDeleted && hasAuth('user:delete')")),
        })


class TestAnchor(unittest.TestCase):
    """腿②：正案綠（自閉合、具名 prefix／suffix 插槽）；三條判準各有獨占反例（互不遮蔽）＋零實例＋引號內 `>` 不誤斷標籤終點。"""

    def _lines(self, text):
        return [ln for ln, _ in check_anchor(text, IP_ATTRS)]

    def _whys(self, text):
        return [why for _, why in check_anchor(text, IP_ATTRS)]

    def test_anchored_form_is_green(self):
        self.assertEqual(check_anchor(ANCHORED_VUE, IP_ATTRS), [])
        self.assertEqual(len(_open_tags(ANCHORED_VUE)), 1)

    def test_missing_show_add_is_red(self):
        found = check_anchor(ANCHORED_VUE.replace("    :show-add=\"hasAuth('ipRule:add')\"\n", ""), IP_ATTRS)
        self.assertEqual([why for _, why in found], ['缺 :show-add="hasAuth(\'ipRule:add\')"（屬性名與值逐字比對）'])
        self.assertEqual(found[0][0], 7)

    def test_missing_or_altered_show_delete_and_altered_show_add_are_red(self):
        for old, new in ((":show-delete=\"false\"", ""), (":show-delete=\"false\"", ":show-delete=\"true\""),
                         ("hasAuth('ipRule:add')", "true"), ("hasAuth('ipRule:add')", "hasAuth('ipRule:edit')"),
                         (":show-add=", "show-add=")):
            found = check_anchor(ANCHORED_VUE.replace(old, new), IP_ATTRS)
            self.assertEqual(len(found), 1, (old, new, found))
            self.assertIn("缺 :show-", found[0][1])

    def test_anchor_values_are_per_file_not_shared(self):
        """錨值逐檔各用各的：IP 規則頁之正形拿使用者頁之錨值判＝兩屬性皆缺（不是任一錨頁之值都放行）。"""
        user_attrs = ANCHORS[os.path.join(SCAN_REL, "user", "index.vue")]
        self.assertEqual(sum("缺 :show-" in why for _, why in check_anchor(ANCHORED_VUE, user_attrs)), 2)
        self.assertEqual(check_anchor(_anchored_for(user_attrs), user_attrs), [])

    def test_reverting_to_default_slot_override_is_red(self):
        whys = self._whys(OVERRIDE_VUE)
        self.assertTrue(any("具名 prefix／suffix 插槽以外之子節點" in w and "<template #default>" in w for w in whys), whys)
        self.assertTrue(any("default 插槽覆寫字面" in w and "<template #default>" in w for w in whys), whys)
        self.assertEqual(sum("缺 :show-" in w for w in whys), 2, whys)

    def test_named_prefix_slot_is_green(self):
        self.assertEqual(check_anchor(PREFIX_VUE, IP_ATTRS), [])

    def test_named_slot_forms_whitespace_and_comments_are_green(self):
        """(b) 放行面逐形：`#prefix`／`#suffix`／`v-slot:prefix`／`v-slot:suffix`、兩插槽並列、插槽間與插槽內之 HTML 註解、
        插槽內之內層 template（深度計）、空白與空標籤體。"""
        for body in ("    <template #suffix><NButton>x</NButton></template>\n",
                     "    <template v-slot:prefix><span>a</span></template>\n",
                     "    <template v-slot:suffix>\n      <span>a</span>\n    </template>\n",
                     "    <!-- 前綴放解鎖鈕 -->\n" + _PREFIX_BODY + "    <!-- 後綴 -->\n    <template #suffix><i /></template>\n",
                     "    <template #prefix>\n      <NButton>\n        <template #icon><i /></template>\n"
                     "        <!-- 內層 <template> 字面不影響深度 -->\n        x\n      </NButton>\n    </template>\n",
                     "\n    \n",
                     ""):
            self.assertEqual(check_anchor(_with_body(body), IP_ATTRS), [], body)

    def test_node_beside_named_slot_is_red(self):
        found = check_anchor(_with_body(_PREFIX_BODY + "    <NButton @click=\"handleAdd\">add</NButton>\n"), IP_ATTRS)
        self.assertEqual(len(found), 1, found)
        self.assertEqual(found[0][0], 18)
        self.assertIn("具名 prefix／suffix 插槽以外之子節點", found[0][1])
        self.assertIn("<NButton @click=\"handleAdd\">add</NButton>", found[0][1])

    def test_every_other_child_form_is_red_by_body_rule_alone(self):
        """(b) 紅面逐形（皆不含 `#default` 字面＝(c) 不連帶、(b) 獨占）：元件、純文字、插值、未帶插槽指令之 template、
        `v-slot` 無引數、其他插槽名、動態插槽名、同一 template 帶兩個插槽指令、具名插槽前置一節點。"""
        for body in ("    <NButton>add</NButton>\n", "    add\n", "    {{ label }}\n",
                     "    <template><NButton>add</NButton></template>\n",
                     "    <template v-slot><NButton>add</NButton></template>\n",
                     "    <template #header><NButton>add</NButton></template>\n",
                     "    <template #[slotName]><NButton>add</NButton></template>\n",
                     "    <template #prefix #header><NButton>add</NButton></template>\n",
                     "    <div />\n" + _PREFIX_BODY):
            whys = self._whys(_with_body(body))
            self.assertEqual(len(whys), 1, (body, whys))
            self.assertIn("具名 prefix／suffix 插槽以外之子節點", whys[0])

    def test_default_slot_template_in_body_is_red_by_both_body_and_literal_rules(self):
        for form in ("#default", "v-slot:default"):
            whys = self._whys(_with_body(_PREFIX_BODY + f"    <template {form}><NButton>add</NButton></template>\n"))
            self.assertEqual(len(whys), 2, (form, whys))
            self.assertTrue(any("具名 prefix／suffix 插槽以外之子節點" in w for w in whys), whys)
            self.assertTrue(any("default 插槽覆寫字面" in w for w in whys), whys)

    def test_body_boundary_is_the_closing_tag_not_end_of_file(self):
        """區段界截到 `</TableHeaderOperation>`：其後之兄弟節點不入判；缺閉合標籤＝延伸到檔尾即紅；具名插槽 template 未閉合即紅。"""
        after = PREFIX_VUE.replace("  </TableHeaderOperation>\n", "  </TableHeaderOperation>\n  <NButton>sibling</NButton>\n")
        self.assertEqual(check_anchor(after, IP_ATTRS), [])
        unclosed = PREFIX_VUE[:PREFIX_VUE.index("  </TableHeaderOperation>")]
        self.assertEqual(len(self._whys(unclosed)), 1)
        self.assertIn("缺 </TableHeaderOperation> 閉合標籤", self._whys(unclosed)[0])
        open_slot = PREFIX_VUE[:PREFIX_VUE.index("    </template>\n  </TableHeaderOperation>")]
        self.assertEqual(len(self._whys(open_slot)), 1)
        self.assertIn("具名插槽 template 未閉合", self._whys(open_slot)[0])

    def test_content_inside_named_slot_is_out_of_scope(self):
        """射程外（docstring 列）：具名插槽內放什麼都不判——此處植入寫入口鈕照綠。"""
        self.assertEqual(check_anchor(_with_body("    <template #prefix><NButton @click=\"handleAdd\">add</NButton></template>\n"),
                                      IP_ATTRS), [])

    def test_default_slot_literal_anywhere_in_file_is_red_including_long_form_and_comments(self):
        text = ANCHORED_VUE.replace("</template>\n",
                                    "  <NCard><template #default>x</template></NCard>\n  <NCard v-slot:default>y</NCard>\n"
                                    "  <!-- 勿改回 #default 覆寫 -->\n</template>\n")
        self.assertEqual(self._lines(text), [15, 16, 17])

    def test_zero_tag_is_red(self):
        self.assertEqual(self._lines(CLEAN_VUE), [1])
        self.assertIn("正面錨無實例", check_anchor(CLEAN_VUE, IP_ATTRS)[0][1])

    def test_every_tag_is_checked(self):
        text = ANCHORED_VUE.replace("</template>\n", "  <TableHeaderOperation :loading=\"loading\" />\n</template>\n")
        self.assertEqual(self._lines(text), [15, 15])

    def test_gt_inside_quoted_value_does_not_end_the_tag(self):
        text = ANCHORED_VUE.replace("    :loading=\"loading\"\n", "    :loading=\"a > b\"\n    :title='x > \"y\"'\n")
        self.assertEqual(check_anchor(text, IP_ATTRS), [])
        self.assertEqual(check_anchor(text.replace("  />\n", "  >\n" + _PREFIX_BODY + "  </TableHeaderOperation>\n"),
                                      IP_ATTRS), [])


class TestRunCheck(unittest.TestCase):
    def test_green_names_scanned_count_and_every_anchor_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, _anchor_files()))
        joined = "\n".join(lines)
        self.assertEqual(rc, 0, lines)
        self.assertIn(f"受掃 {len(ANCHORS)} 檔", joined)
        for rel in ANCHORS:
            self.assertIn(f"{rel.replace(os.sep, '/')} 表頭 prop 形錨成立（1 個開標籤", joined)

    def test_hit_is_rc1_with_file_and_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, _anchor_files({"ip-rule/index.vue": ANCHORED_VUE.replace(
                "<span>{{ memo }}</span>", '<span v-html="memo"></span>')})))
        self.assertEqual(rc, 1, lines)
        self.assertIn("base-web/src/views/manage/ip-rule/index.vue:6", "\n".join(lines))

    def test_anchor_break_is_rc1_with_file_and_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, _anchor_files({"ip-rule/index.vue": OVERRIDE_VUE})))
        self.assertEqual(rc, 1, lines)
        joined = "\n".join(lines)
        self.assertIn("管理頁表頭脫離 prop 形", joined)
        self.assertIn("base-web/src/views/manage/ip-rule/index.vue:7", joined)
        self.assertNotIn("原始 HTML 注入寫法", joined)

    def test_each_anchor_file_is_judged_with_its_own_values(self):
        """兩錨檔內容互換＝各自拿對方之錨值、兩檔皆紅（逐檔用各自之列、非聯集）。"""
        files = _anchor_files()
        swapped = {"ip-rule/index.vue": files["user/index.vue"], "user/index.vue": files["ip-rule/index.vue"]}
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, _anchor_files(swapped)))
        joined = "\n".join(lines)
        self.assertEqual(rc, 1, lines)
        self.assertIn("base-web/src/views/manage/ip-rule/index.vue:7", joined)
        self.assertIn("base-web/src/views/manage/user/index.vue:7", joined)

    def test_absent_anchor_file_is_rc2_and_named_for_each_anchor(self):
        for rel in ANCHORS:
            key = os.path.relpath(rel, SCAN_REL).replace(os.sep, "/")
            with tempfile.TemporaryDirectory() as tmp:
                rc, lines = run_check(_fake_repo(tmp, _anchor_files({key: None, "moved/index.vue": ANCHORED_VUE})))
            self.assertEqual(rc, 2, (key, lines))
            self.assertEqual(lines, [f"{TAG} ✗ 表頭錨檔缺席：{rel.replace(os.sep, '/')}——被搬走或改名？正面錨無標的不得靜默放行"
                                     "（錨檔＝本檔 ANCHORS）"])

    def test_absent_worktree_absent_scope_and_empty_scope_are_rc2_and_distinguishable(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc_wt, wt = run_check(tmp)
            os.makedirs(os.path.join(tmp, WORKTREE_REL))
            rc_scope, scope = run_check(tmp)
            _write(os.path.join(tmp, SCAN_REL, "ip-rule", "NOTE.md"), "x\n")
            rc_empty, empty = run_check(tmp)
        self.assertEqual((rc_wt, rc_scope, rc_empty), (2, 2, 2), (wt, scope, empty))
        self.assertIn("工作樹缺席", "\n".join(wt))
        self.assertIn("射程目錄缺席", "\n".join(scope))
        self.assertIn("零受掃檔", "\n".join(empty))


class TestUsage(unittest.TestCase):
    def test_unknown_subcommand_is_rc64(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = main(["tools/view-render-guard.py", "nope"])
        self.assertEqual(rc, 64)
        self.assertIn("用法：", err.getvalue())


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "test" and len(argv) == 2:
        ok = unittest.main(argv=[argv[0]], exit=False, verbosity=1).result.wasSuccessful()
        if ok:
            _say(f"{TAG} ✓ self-test 過（FORBIDDEN {len(FORBIDDEN)} 條逐條逐行反例／註解內字面照紅／錨表逐列釘值／"
                 f"表頭錨三條判準各有獨占反例〔標籤體放行面與紅面逐形、區段界〕・錨值逐檔・零實例・引號內 `>`／"
                 f"工作樹・射程・各錨檔缺席與零受掃檔 rc 2／用法守衛）")
        return 0 if ok else 1
    if cmd != "check" or len(argv) > 2:
        _say(USAGE, err=True)
        return 64
    rc, lines = run_check(REPO_ROOT)
    for ln in lines:
        _say(ln, err=bool(rc))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
