"""語料面：測試共用件 `tmprepo` 的環境隔離自證（LL-00012 同源）——臨時 repo 面剝 `GIT_*`、真 repo 面沿用呼叫端環境。

pre-commit 期間 git 匯出 `GIT_INDEX_FILE`（一般 commit＝相對 `.git/index`；`commit -a`／部分 commit＝外層 lock index 的絕對路徑）。
以不存在的哨兵路徑模擬之：臨時 repo 的 add／commit／閘讀取若沿用它，哨兵會被建出、或 Ctx 讀到空暫存區。"""
import ast
import inspect
import os
import shutil
import tempfile
import textwrap
import unittest
import unittest.mock

from docsync import common, gates, ROOT
from docsync.tests import tmprepo

CONSISTENCY = "ADR-00052 決定 1"   # GT-12 一致性腿全部訊息共有的出處字面


def _methods(cls_node):
    return {f.name: f for f in cls_node.body if isinstance(f, ast.FunctionDef)}


def _subprocess_refs(node):
    return [n for n in ast.walk(node)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "subprocess"]


def _wraps_stripped(fn):
    return any(isinstance(n, ast.With) and any(isinstance(i.context_expr, ast.Call) and isinstance(i.context_expr.func, ast.Name)
                                               and i.context_expr.func.id == "_stripped" for i in n.items)
               for n in ast.walk(fn))


def _override_gaps(common_src):
    """common 原文 → 覆寫面缺口訊息 list（空＝完備）；覆寫側取 `tmprepo.Ctx` 現檔。
    須覆寫集＝`Ctx` 方法體內直寫 `subprocess.` 者（會發 git 的底層）。★此口徑的前提＝起行程只經 Ctx 方法體內直寫：
    模組層 helper 起行程、由 Ctx 方法呼叫者，方法體直寫口徑看不到＝覆寫面漏網。前提以「common 全模組之 `subprocess.`
    引用皆落在 Ctx 方法體內」斷言（前提失效即紅）；不採呼叫圖閉包——閉包須另判間接呼叫（別名、getattr、經他類方法），
    本身又是一道會過窄的前提，全模組禁令嚴格包含之，且 common 現況即零例。"""
    mod = ast.parse(common_src)
    gaps = []
    imports = [(type(n).__name__, getattr(n, "module", None), [(a.name, a.asname) for a in n.names])
               for n in ast.walk(mod) if isinstance(n, (ast.Import, ast.ImportFrom))
               and ("subprocess" in [a.name for a in n.names] or getattr(n, "module", None) == "subprocess")]
    if imports != [("Import", None, [("subprocess", None)])]:
        gaps.append(f"前提失效：common 引入 subprocess 之形為 {imports}（只認 `import subprocess`；別名／from 形會讓掃描漏網）")
    ctx = next(n for n in mod.body if isinstance(n, ast.ClassDef) and n.name == "Ctx")
    inside = {id(n) for f in _methods(ctx).values() for n in _subprocess_refs(f)}
    for n in _subprocess_refs(mod):
        if id(n) not in inside:
            gaps.append(f"前提失效：common 第 {n.lineno} 行於 Ctx 方法體外引用 subprocess.{n.attr}（模組層函式、他類或 Ctx 類層"
                        "非方法）——經它起行程者不在覆寫面；移入 Ctx 方法體（並於 tmprepo.Ctx 覆寫）或擴本對賬")
    spawning = sorted(name for name, f in _methods(ctx).items() if _subprocess_refs(f))
    if not spawning:
        gaps.append("受守面空集合：common.Ctx 零個直起 subprocess 的方法——掃描口徑失效（RL-0067）")
    mine = _methods(ast.parse(textwrap.dedent(inspect.getsource(tmprepo.Ctx))).body[0])
    for name in spawning:
        if name not in mine:
            gaps.append(f"common.Ctx.{name} 直起 subprocess、tmprepo.Ctx 未覆寫——臨時 repo 面會沿用呼叫端 GIT_*")
        elif not _wraps_stripped(mine[name]):
            gaps.append(f"tmprepo.Ctx.{name} 覆寫體未以 `with _stripped()` 包住呼叫")
    return gaps


class TestTmpRepoGitEnv(unittest.TestCase):
    """本類不經任何 setUp 剝環境：helper 須逐呼叫自行剝除，模組層與 setUpClass 期呼叫才同樣安全。"""

    def sentinel(self, name="hook-index"):
        """暫存目錄下一個不存在的路徑（測後整目錄清除）。"""
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        return os.path.join(d, name)

    def test_hook_index_env_does_not_leak_into_tmp_repo_or_its_ctx(self):
        """反例形＝哨兵 `GIT_INDEX_FILE`：helper 建 repo 並 commit、對其建 Ctx 跑 GT-12——哨兵不得被建出，
        Ctx 須讀到該 repo 自己的暫存區（tracked 全在、暫存區＝HEAD 故一致性腿整腿不跑）。
        ★拿掉 helper 的剝除＝`git add` 建出哨兵；只拿掉 Ctx 的剝除＝tracked 為空、一致性腿報未追蹤——兩者各自轉紅。"""
        hook_index = self.sentinel()
        with unittest.mock.patch.dict(os.environ, {"GIT_INDEX_FILE": hook_index}):
            root = tmprepo.make_repo({"a.md": "A\n", "docs/b.md": "B\n"})
            self.addCleanup(shutil.rmtree, root, True)
            ctx = tmprepo.Ctx(root)
            fs = gates.gt_12(ctx)
            self.assertEqual(os.environ["GIT_INDEX_FILE"], hook_index)   # 逐呼叫剝除、不留下行程環境的改動
        self.assertFalse(os.path.exists(hook_index), "臨時 repo 的 git 讀寫了呼叫端 GIT_INDEX_FILE")
        self.assertEqual(ctx.tracked, ["a.md", "docs/b.md"])
        self.assertEqual([f for f in fs if CONSISTENCY in f[3]], [])

    def test_ctx_subprocess_primitives_all_overridden_with_strip(self):
        """名冊對賬（RL-0026：處數由測試釘、不靠 docstring 枚舉——LL-00034）：`common.Ctx` 方法體內直接起 `subprocess.` 者
        ＝會發 git 的底層，須全數在 `tmprepo.Ctx` 本類覆寫、且覆寫體以 `with _stripped()` 包住呼叫。集合由 AST 現取、不寫死：
        common.Ctx 日後新增直起 subprocess 的底層（例：以 `cat-file --batch` 改寫 HEAD 讀取）而本件未跟上＝本案轉紅，
        不再靜默沿用呼叫端 `GIT_*`（LL-00012 同源）。前提兩條一併斷言：common 只以 `import subprocess` 引入（別名／from 形
        會讓掃描漏網）、全模組之 `subprocess.` 引用皆在 Ctx 方法體內（模組層 helper 起行程者方法體直寫口徑看不到；見 `_override_gaps`）。"""
        self.assertEqual(_override_gaps(inspect.getsource(common)), [])

    # 植入物：模組層起行程之 helper＋由 Ctx 新方法呼叫之（方法體內不直寫 `subprocess.`）
    PLANT_HELPER = "def _spawn(*args):\n    return subprocess.run(args)\n\n\n"
    PLANT_METHOD = "    def cat(self):\n        return _spawn(\"git\", \"cat-file\")\n\n"

    def test_module_level_spawner_called_from_ctx_is_red(self):
        """記憶體內反例（不改 common.py 真檔）：common 植入模組層起行程之 helper、由 `Ctx` 新方法呼叫——覆寫面對賬須報。"""
        src = inspect.getsource(common)
        mutated = src.replace("\nclass Ctx:\n", "\n" + self.PLANT_HELPER + "class Ctx:\n" + self.PLANT_METHOD, 1)
        self.assertNotEqual(mutated, src)   # 植入點存在
        gaps = _override_gaps(mutated)
        self.assertTrue(any("Ctx 方法體外引用 subprocess.run" in g for g in gaps), gaps)   # 模組層 helper 起行程、Ctx 方法經它發 git

    def test_each_ctx_git_primitive_strips_env(self):
        """`tmprepo.Ctx` 現有底層逐支實呼叫、驗剝除確實生效（名冊完備性由上一案對賬）：以指向不存在處的
        `GIT_DIR` 當反例形——任一支沿用呼叫端環境即讀不到臨時 repo（建構失敗、rc≠0 或 commit 存在性 memo 不入）。"""
        root = tmprepo.make_repo({"a.md": "A\n"})
        self.addCleanup(shutil.rmtree, root, True)
        head = tmprepo.git(root, "rev-parse", "HEAD")
        with unittest.mock.patch.dict(os.environ, {"GIT_DIR": self.sentinel("no-such-git-dir")}):
            ctx = tmprepo.Ctx(root)                                               # _git_raw（rev-parse／ls-files）
            self.assertEqual(ctx.tracked, ["a.md"])
            self.assertEqual(ctx.git_try("rev-parse", "--verify", "-q", "HEAD"), (0, head + "\n"))   # git_try
            ctx.prefetch_commits([head])                                          # prefetch_commits（批次失敗＝memo 不入）
            self.assertIs(ctx._commits.get((None, head)), True)

    def test_real_repo_ctx_keeps_caller_env(self):
        """真 repo（ROOT）面照用 `common.Ctx`、沿用呼叫端環境：hook 期之 `GIT_INDEX_FILE`＝本次 commit 的暫存區＝一致性腿正確取值面。
        用過 helper 之後，行程環境的 `GIT_INDEX_FILE` 仍在、`common.Ctx(ROOT)` 仍讀它（此處指向不存在檔＝空暫存區）。
        ★helper 若改成剝行程級 `os.environ`（一剝了之），本案轉紅。"""
        self.assertTrue(common.Ctx(ROOT).tracked)   # 對照：未設哨兵時真 repo 名冊非空
        hook_index = self.sentinel()
        with unittest.mock.patch.dict(os.environ, {"GIT_INDEX_FILE": hook_index}):
            root = tmprepo.make_repo({"a.md": "A\n"})
            self.addCleanup(shutil.rmtree, root, True)
            self.assertEqual(tmprepo.Ctx(root).tracked, ["a.md"])
            self.assertEqual(os.environ.get("GIT_INDEX_FILE"), hook_index)
            self.assertEqual(common.Ctx(ROOT).tracked, [])
        self.assertFalse(os.path.exists(hook_index))


if __name__ == "__main__":
    unittest.main()
