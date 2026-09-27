#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/view-render-guard.py — 碼面閘：管理頁目錄零原始 HTML 注入寫法（004 刀 U8；spec FR-052、`docs/ops/reference-src/code-gate-contracts.md` §3①；
承 rev5:tools/view-render-guard.py 新寫；名冊＝RUNBOOK §12 碼面閘表）＋IP 規則頁表頭 prop 形正面錨（005 刀 U13；BL-00117、
`specs/005-role-menu-crud/spec.md` FR-062）

子命令：
  check   （預設）兩腿皆跑：①逐行掃 base-web/src/views/manage/** 之 `.vue`／`.ts`／`.tsx`／`.js`／`.jsx`；命中 [`FORBIDDEN`] 任一條即 rc 1、
          逐處指名檔:行 ②[`ANCHOR_REL`] 之表頭正面錨（見下）；不成立即 rc 1、逐處指名檔:行
  test    離線 self-test（暫存樹、毫秒級、零 docker）

守什麼：
  ①管理頁的自由文字欄（IP 規則備註為首例）承載使用者可寫的原文。預設插值會逸出標記字元；改成原始 HTML 注入寫法後，
    欄值是純文字時畫面完全相同，型別檢查（皆 string）與畫面比對都分不出來——只有掃原文擋得住。
  ②IP 規則頁表頭的寫入口由共用表頭元件之兩布林 prop 控制：新增鈕綁新增按鈕碼權限、批刪鈕恆關。呼叫端一旦改回覆寫 default 插槽，
    覆寫內容就不受兩 prop 控制；覆寫成空時 Vue 還會改渲染元件自帶的備援按鈕——無權帳號反而看見寫入口。prop 缺漏或插槽覆寫
    型別檢查都照綠，而 seed 下沒有「有頁面權限、無新增權限」的帳號、瀏覽器走查觸不到，故以模板靜態斷言守。
不變式：
  · 腿①逐行比對原文、不分註解與碼、不解析語法：判定面沒有可錯位的 tokenizer；代價＝射程內連註解都不得寫出被禁字面（本檔不在射程內）。
  · 腿②正面錨三條、皆對錨檔原文判（註解內字面同計）：(a) 每個 `<TableHeaderOperation` 開標籤都帶 [`ANCHOR_ATTRS`] 兩屬性且值逐字相符；
    (b) 該標籤自閉合——標籤體內任何內容（具名 template 以外的子節點）都會成為 default 插槽內容，自閉合即結構上無從覆寫；
    (c) 檔內零 [`DEFAULT_SLOT`] 字面（`#default`／`v-slot:default`）。錨檔內零個該開標籤＝不成立（正面錨無實例不算綠）。
    開標籤之終點以引號外第一個 `>` 判（屬性值內的 `>` 不誤斷）。射程外（機器守不及）：同名 prop 之其他繫結寫法
    （靜態屬性、`v-bind` 物件展開、camelCase 別名）與錨屬性並存時之覆蓋序、kebab-case 標籤名之第二個表頭。
    確需具名插槽（`#prefix`／`#suffix`）時 (b) 須同批改判準。
  · 腿①掃到零檔、腿②錨檔缺席＝rc 2、不是綠：射程目錄或錨檔被搬走或改名時，只會「找不到違規」的掃描器即恆綠（RL-0051）。
  · base-web 工作樹缺席＝rc 2 fail-loud、工具與 pre-commit 段皆不設跳過（ADR-00019 決定 4：tracked 面缺席不類推環境缺席）。
退出碼：0 綠／1 命中（任一腿）／2 工作樹、射程或錨檔缺席、零受掃檔／64 用法錯。
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


# 腿②：IP 規則頁表頭正面錨（BL-00117；spec FR-062）。錨檔路徑相對 repo 根；屬性值逐字比對（改寫法＝同批改本常數）。
ANCHOR_REL = os.path.join(SCAN_REL, "ip-rule", "index.vue")
ANCHOR_TAG = re.compile(r"<TableHeaderOperation(?=[\s/>])")
ANCHOR_ATTRS = ((":show-add", "hasAuth('ipRule:add')"), (":show-delete", "false"))
DEFAULT_SLOT = re.compile(r"#default\b|\bv-slot:default\b")
# 屬性名＋可選之引號值；單引號值也吃掉，免得其內的雙引號錯配後續屬性。
_ATTR = re.compile(r"""([^\s"'<>/=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'))?""")


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


def _open_tags(text):
    """錨檔原文 → [(行號, {(屬性名, 雙引號值)}, 是否自閉合)]；標籤終點＝引號外第一個 `>`，缺終點即延伸到檔尾（視為非自閉合）。"""
    tags = []
    for m in ANCHOR_TAG.finditer(text):
        quote, i = None, m.end()
        while i < len(text):
            ch = text[i]
            if quote:
                quote = None if ch == quote else quote
            elif ch in "\"'":
                quote = ch
            elif ch == ">":
                break
            i += 1
        body = text[m.end():i]
        closed = i < len(text) and body.rstrip().endswith("/")
        tags.append((text.count("\n", 0, m.start()) + 1, {(name, dq) for name, dq, _ in _ATTR.findall(body)}, closed))
    return tags


def check_anchor(text):
    """腿②判定 → [(行號, 說明)]（空＝錨成立）。三條各自出列，互不遮蔽。"""
    problems = []
    tags = _open_tags(text)
    if not tags:
        problems.append((1, "零個 <TableHeaderOperation 開標籤——正面錨無實例"))
    for lineno, attrs, closed in tags:
        problems += [(lineno, f'缺 {name}="{value}"（屬性名與值逐字比對）') for name, value in ANCHOR_ATTRS
                     if (name, value) not in attrs]
        if not closed:
            problems.append((lineno, "標籤非自閉合——標籤體內容即 default 插槽覆寫、不受兩 prop 控制"))
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
    anchor_rel = ANCHOR_REL.replace(os.sep, "/")
    anchor_path = os.path.join(repo_root, ANCHOR_REL)
    if not os.path.isfile(anchor_path):
        return 2, [f"{TAG} ✗ 表頭錨檔缺席：{anchor_rel}——被搬走或改名？正面錨無標的不得靜默放行（錨檔＝本檔 ANCHOR_REL）"]
    with open(anchor_path, encoding="utf-8", errors="replace") as fh:
        anchor_text = fh.read()
    problems = check_anchor(anchor_text)
    lines = []
    if findings:
        lines += [f"{TAG} ✗ 管理頁出現原始 HTML 注入寫法 {len(findings)} 處（specs/004-ip-trust-anchor/spec.md FR-052：自由文字欄一律純文字插值；註解內字面同計）："]
        lines += [f"  {scan_rel}/{rel}:{lineno}  {why}\n      {text}" for rel, lineno, why, text in findings]
        lines.append("  補救：改回預設插值（模板 `{{ }}`／render 函式回字串）；確有原始標記需求＝拍板級、走 ADR")
    if problems:
        lines.append(f"{TAG} ✗ IP 規則頁表頭脫離 prop 形 {len(problems)} 處（BL-00117；specs/005-role-menu-crud/spec.md FR-062；註解內字面同計）：")
        lines += [f"  {anchor_rel}:{lineno}  {why}" for lineno, why in problems]
        lines.append("  補救：表頭以 prop 控制寫入口（" + "、".join(f'{n}="{v}"' for n, v in ANCHOR_ATTRS)
                     + "）、標籤自閉合、不覆寫 default 插槽——覆寫內容不受兩 prop 控制、無權帳號會看見寫入口")
    if lines:
        return 1, lines
    return 0, [f"{TAG} ✓ {scan_rel}/** 零原始 HTML 注入寫法（受掃 {count} 檔、{len(FORBIDDEN)} 條被禁字面）",
               f"{TAG} ✓ {anchor_rel} 表頭 prop 形錨成立（{len(_open_tags(anchor_text))} 個開標籤皆自閉合且帶兩錨屬性、零 default 插槽覆寫字面）"]


# ── self-test（離線；一律實跑上方生產函式）────────────────────────────────────

CLEAN_VUE = ("<script setup lang=\"ts\">\nconst memo = 'plain';\n</script>\n\n"
             "<template>\n  <span>{{ memo }}</span>\n</template>\n")
# 腿②正案：錨檔現行形之縮影（多行開標籤、兩錨屬性夾在其他屬性之間、自閉合）；第 6 行同 CLEAN_VUE（腿①命中案沿用行號）。
ANCHORED_VUE = ("<script setup lang=\"ts\">\nconst memo = 'plain';\n</script>\n\n"
                "<template>\n  <span>{{ memo }}</span>\n"
                "  <TableHeaderOperation\n    v-model:columns=\"columnChecks\"\n    :loading=\"loading\"\n"
                "    :show-add=\"hasAuth('ipRule:add')\"\n    :show-delete=\"false\"\n    @add=\"handleAdd\"\n"
                "    @refresh=\"getData\"\n  />\n</template>\n")
# 改回覆寫插槽之形（004 刀 as-built 表頭之縮影）：非自閉合＋default 插槽 template、兩錨屬性皆缺。
OVERRIDE_VUE = ANCHORED_VUE.replace(
    "    :show-add=\"hasAuth('ipRule:add')\"\n    :show-delete=\"false\"\n    @add=\"handleAdd\"\n", "").replace(
    "    @refresh=\"getData\"\n  />\n",
    "    @refresh=\"getData\"\n  >\n    <template #default>\n      <NButton @click=\"handleAdd\">add</NButton>\n"
    "    </template>\n  </TableHeaderOperation>\n")
# 鍵＝該條正則原文；值＝植入片段，★每一非空行皆須被該條抓到（同族變體逐行列；只驗「有一行紅」則規則被改窄仍綠）。
COUNTEREXAMPLES = (
    (r"\bv-html\b", '<template><span v-html="memo"></span></template>\n'),
    (r"\binnerHTML\b", "el.innerHTML = memo;\nh('span', { innerHTML: memo });\n"),
    (r"\bouterHTML\b", "el.outerHTML = memo;\n"),
    (r"\binsertAdjacentHTML\b", "el.insertAdjacentHTML('beforeend', memo);\n"),
    (r"\bdocument\.write(?:ln)?\b", "document.write(memo);\ndocument.writeln(memo);\n"),
)


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


class TestAnchor(unittest.TestCase):
    """腿②：正案綠；三條判準各一反（互不遮蔽）＋零實例＋引號內 `>` 不誤斷標籤終點。"""

    def _lines(self, text):
        return [ln for ln, _ in check_anchor(text)]

    def test_anchored_form_is_green(self):
        self.assertEqual(check_anchor(ANCHORED_VUE), [])
        self.assertEqual(len(_open_tags(ANCHORED_VUE)), 1)

    def test_missing_show_add_is_red(self):
        found = check_anchor(ANCHORED_VUE.replace("    :show-add=\"hasAuth('ipRule:add')\"\n", ""))
        self.assertEqual([why for _, why in found], ['缺 :show-add="hasAuth(\'ipRule:add\')"（屬性名與值逐字比對）'])
        self.assertEqual(found[0][0], 7)

    def test_missing_or_altered_show_delete_and_altered_show_add_are_red(self):
        for old, new in ((":show-delete=\"false\"", ""), (":show-delete=\"false\"", ":show-delete=\"true\""),
                         ("hasAuth('ipRule:add')", "true"), ("hasAuth('ipRule:add')", "hasAuth('ipRule:edit')"),
                         (":show-add=", "show-add=")):
            found = check_anchor(ANCHORED_VUE.replace(old, new))
            self.assertEqual(len(found), 1, (old, new, found))
            self.assertIn("缺 :show-", found[0][1])

    def test_reverting_to_default_slot_override_is_red(self):
        whys = [why for _, why in check_anchor(OVERRIDE_VUE)]
        self.assertTrue(any("非自閉合" in w for w in whys), whys)
        self.assertTrue(any("default 插槽覆寫字面" in w and "<template #default>" in w for w in whys), whys)
        self.assertEqual(sum("缺 :show-" in w for w in whys), 2, whys)

    def test_bare_children_without_default_literal_is_red_by_self_closing_rule(self):
        text = ANCHORED_VUE.replace("    @refresh=\"getData\"\n  />\n",
                                    "    @refresh=\"getData\"\n  >\n    <NButton>add</NButton>\n  </TableHeaderOperation>\n")
        self.assertEqual([why for _, why in check_anchor(text)],
                         ["標籤非自閉合——標籤體內容即 default 插槽覆寫、不受兩 prop 控制"])

    def test_default_slot_literal_anywhere_in_file_is_red_including_long_form_and_comments(self):
        text = ANCHORED_VUE.replace("</template>\n",
                                    "  <NCard><template #default>x</template></NCard>\n  <NCard v-slot:default>y</NCard>\n"
                                    "  <!-- 勿改回 #default 覆寫 -->\n</template>\n")
        self.assertEqual(self._lines(text), [15, 16, 17])

    def test_zero_tag_is_red(self):
        self.assertEqual(self._lines(CLEAN_VUE), [1])
        self.assertIn("正面錨無實例", check_anchor(CLEAN_VUE)[0][1])

    def test_every_tag_is_checked(self):
        text = ANCHORED_VUE.replace("</template>\n", "  <TableHeaderOperation :loading=\"loading\" />\n</template>\n")
        self.assertEqual(self._lines(text), [15, 15])

    def test_gt_inside_quoted_value_does_not_end_the_tag(self):
        text = ANCHORED_VUE.replace("    :loading=\"loading\"\n", "    :loading=\"a > b\"\n    :title='x > \"y\"'\n")
        self.assertEqual(check_anchor(text), [])


class TestRunCheck(unittest.TestCase):
    def test_green_names_scanned_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, {"ip-rule/index.vue": ANCHORED_VUE}))
        self.assertEqual(rc, 0, lines)
        self.assertIn("受掃 1 檔", "\n".join(lines))
        self.assertIn("表頭 prop 形錨成立（1 個開標籤", "\n".join(lines))

    def test_hit_is_rc1_with_file_and_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, {"ip-rule/index.vue": ANCHORED_VUE.replace("<span>{{ memo }}</span>",
                                                                                            '<span v-html="memo"></span>')}))
        self.assertEqual(rc, 1, lines)
        self.assertIn("base-web/src/views/manage/ip-rule/index.vue:6", "\n".join(lines))

    def test_anchor_break_is_rc1_with_file_and_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, {"ip-rule/index.vue": OVERRIDE_VUE}))
        self.assertEqual(rc, 1, lines)
        joined = "\n".join(lines)
        self.assertIn("IP 規則頁表頭脫離 prop 形", joined)
        self.assertIn("base-web/src/views/manage/ip-rule/index.vue:7", joined)
        self.assertNotIn("原始 HTML 注入寫法", joined)

    def test_absent_anchor_file_is_rc2_and_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, {"ip-rule-moved/index.vue": ANCHORED_VUE}))
        self.assertEqual(rc, 2, lines)
        self.assertIn("表頭錨檔缺席", "\n".join(lines))

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
            _say(f"{TAG} ✓ self-test 過（FORBIDDEN {len(FORBIDDEN)} 條逐條逐行反例／註解內字面照紅／"
                 f"表頭錨三條判準各一反・零實例・引號內 `>`／工作樹・射程・錨檔缺席與零受掃檔 rc 2／用法守衛）")
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
