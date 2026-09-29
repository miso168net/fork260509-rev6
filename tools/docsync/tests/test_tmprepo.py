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
        不再靜默沿用呼叫端 `GIT_*`（LL-00012 同源）。前提＝common 只以 `import subprocess` 引入（別名／from 形會讓掃描漏網、一併斷言）。"""
        mod = ast.parse(inspect.getsource(common))
        imports = [(type(n).__name__, getattr(n, "module", None), [(a.name, a.asname) for a in n.names])
                   for n in ast.walk(mod) if isinstance(n, (ast.Import, ast.ImportFrom))
                   and ("subprocess" in [a.name for a in n.names] or getattr(n, "module", None) == "subprocess")]
        self.assertEqual(imports, [("Import", None, [("subprocess", None)])])

        def methods(cls):
            node = ast.parse(textwrap.dedent(inspect.getsource(cls))).body[0]
            return {f.name: f for f in node.body if isinstance(f, ast.FunctionDef)}

        spawning = {name for name, f in methods(common.Ctx).items()
                    if any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "subprocess"
                           for n in ast.walk(f))}
        self.assertTrue(spawning)   # 受守面非空（RL-0067）：掃描口徑失效即紅、不空轉
        mine = methods(tmprepo.Ctx)
        for name in sorted(spawning):
            self.assertIn(name, mine, f"common.Ctx.{name} 直起 subprocess、tmprepo.Ctx 未覆寫——臨時 repo 面會沿用呼叫端 GIT_*")
            self.assertTrue(any(isinstance(n, ast.With) and any(isinstance(i.context_expr, ast.Call)
                                                                and isinstance(i.context_expr.func, ast.Name)
                                                                and i.context_expr.func.id == "_stripped" for i in n.items)
                                for n in ast.walk(mine[name])),
                            f"tmprepo.Ctx.{name} 覆寫體未以 `with _stripped()` 包住呼叫")

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
