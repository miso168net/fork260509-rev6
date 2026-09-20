#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/view-render-guard.py — 碼面閘：管理頁目錄零原始 HTML 注入寫法（004 刀 U8；spec FR-052、`docs/ops/reference-src/code-gate-contracts.md` §3①；
承 rev5:tools/view-render-guard.py 新寫；名冊＝RUNBOOK §12 碼面閘表）

子命令：
  check   （預設）逐行掃 base-web/src/views/manage/** 之 `.vue`／`.ts`／`.tsx`／`.js`／`.jsx`；命中 [`FORBIDDEN`] 任一條即 rc 1、逐處指名檔:行
  test    離線 self-test（暫存樹、毫秒級、零 docker）

守什麼：管理頁的自由文字欄（IP 規則備註為首例）承載使用者可寫的原文。預設插值會逸出標記字元；改成原始 HTML 注入寫法後，
  欄值是純文字時畫面完全相同，型別檢查（皆 string）與畫面比對都分不出來——只有掃原文擋得住。
不變式：
  · 逐行比對原文、不分註解與碼、不解析語法：判定面沒有可錯位的 tokenizer；代價＝射程內連註解都不得寫出被禁字面（本檔不在射程內）。
  · 掃到零檔＝rc 2、不是綠：射程目錄被搬走或改名時，只會「找不到違規」的掃描器即恆綠（RL-0051）。
  · base-web 工作樹缺席＝rc 2 fail-loud、工具與 pre-commit 段皆不設跳過（ADR-00019 決定 4：tracked 面缺席不類推環境缺席）。
退出碼：0 綠／1 命中／2 工作樹或射程缺席、零受掃檔／64 用法錯。
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


def run_check(repo_root):
    """→ (rc, 輸出行清單)。三種 rc 2 各自具名（補救動作不同：建工作樹／查射程搬移／查副檔名）。"""
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
    if findings:
        lines = [f"{TAG} ✗ 管理頁出現原始 HTML 注入寫法 {len(findings)} 處（specs/004-ip-trust-anchor/spec.md FR-052：自由文字欄一律純文字插值；註解內字面同計）："]
        lines += [f"  {scan_rel}/{rel}:{lineno}  {why}\n      {text}" for rel, lineno, why, text in findings]
        lines.append("  補救：改回預設插值（模板 `{{ }}`／render 函式回字串）；確有原始標記需求＝拍板級、走 ADR")
        return 1, lines
    return 0, [f"{TAG} ✓ {scan_rel}/** 零原始 HTML 注入寫法（受掃 {count} 檔、{len(FORBIDDEN)} 條被禁字面）"]


# ── self-test（離線；一律實跑上方生產函式）────────────────────────────────────

CLEAN_VUE = ("<script setup lang=\"ts\">\nconst memo = 'plain';\n</script>\n\n"
             "<template>\n  <span>{{ memo }}</span>\n</template>\n")
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


class TestRunCheck(unittest.TestCase):
    def test_green_names_scanned_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, {"ip-rule/index.vue": CLEAN_VUE}))
        self.assertEqual(rc, 0, lines)
        self.assertIn("受掃 1 檔", "\n".join(lines))

    def test_hit_is_rc1_with_file_and_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, lines = run_check(_fake_repo(tmp, {"ip-rule/index.vue": CLEAN_VUE.replace("<span>{{ memo }}</span>",
                                                                                         '<span v-html="memo"></span>')}))
        self.assertEqual(rc, 1, lines)
        self.assertIn("base-web/src/views/manage/ip-rule/index.vue:6", "\n".join(lines))

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
                 f"工作樹・射程缺席與零受掃檔 rc 2／用法守衛）")
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
