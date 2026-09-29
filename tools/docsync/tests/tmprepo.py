"""測試共用：臨時 git repo 的建立與讀取（單一家；各測試檔不另抄 git 呼叫與環境處置）。

★臨時 repo 的一切 git——本模組的 subprocess、與「對臨時 repo 建的 Ctx」所發者——一律在剝掉 `GIT_*` 的環境下跑：
pre-commit 期間 git 匯出 `GIT_INDEX_FILE`（一般 commit＝相對 `.git/index`；`commit -a`／部分 commit＝外層 lock index
的絕對路徑）等，不剝即對外層 index 讀寫（LL-00012 同源）。剝除逐呼叫進行、不留下行程 `os.environ` 的改動（`git()` 以
`env=` 傳剝除副本；Ctx 底層於呼叫期間以 `patch.dict` 暫換行程環境、返回即還原），故模組層與 setUpClass 期的呼叫同樣適用。
★真 repo（ROOT）面照用 `common.Ctx`、沿用呼叫端環境：hook 期之 `GIT_INDEX_FILE` 即本次 commit 的暫存區＝一致性腿
（ADR-00052 決定 1）的正確取值面，不得因本模組而改變。兩面由 `test_tmprepo` 自證。"""
import contextlib
import os
import subprocess
import tempfile
import unittest.mock

from docsync import common


def clean_env():
    """行程環境去掉一切 `GIT_*` 的副本。"""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


@contextlib.contextmanager
def _stripped():
    with unittest.mock.patch.dict(os.environ, clean_env(), clear=True):
        yield


def git(cwd, *args):
    """臨時 repo 的 git：剝 `GIT_*`、帶測試身分、check=True、回去首尾空白的 stdout。"""
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", cwd, *args],
                          check=True, capture_output=True, text=True, env=clean_env()).stdout.strip()


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def make_repo(files, commit=True, exec_paths=()):
    """臨時 repo：files 全數 add、exec_paths 以 index 落 100755；commit=False＝HEAD 未誕生（暫存區非空）。回 root。
    core.quotePath 釘回 git 預設 true：機器全域若設 false，不帶 -z 的輸出也不轉義非 ASCII，-z 切分守門案即失去牙齒。"""
    root = tempfile.mkdtemp()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "core.quotePath", "true")
    for rel, text in files.items():
        write(root, rel, text)
    git(root, "add", "-A")
    for rel in exec_paths:
        git(root, "update-index", "--chmod=+x", rel)
    if commit:
        git(root, "commit", "-qm", "x")
    return root


class Ctx(common.Ctx):
    """對臨時 repo 建的 Ctx：`common.Ctx` 一切直接起 subprocess 的底層皆於本類覆寫、改在剝除環境下跑（其餘方法經這些底層發 git）；
    讀取邏輯一概沿用。覆寫面完備與否由 test_tmprepo 以 AST 對 `common.Ctx` 現取集合對賬、不在此枚舉（LL-00034）。"""

    def _git_raw(self, *args, cwd=None):
        with _stripped():
            return super()._git_raw(*args, cwd=cwd)

    def git_try(self, *args, cwd=None):
        with _stripped():
            return super().git_try(*args, cwd=cwd)

    def prefetch_commits(self, shas, cwd=None):
        with _stripped():
            return super().prefetch_commits(shas, cwd=cwd)
