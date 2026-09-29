"""語料面：閘取值口徑（ADR-00052）——HEAD 版讀取口徑（決定 2／3）與「工作樹＝暫存區」一致性腿（決定 1）。

★本檔的臨時 repo 一律經 `tmprepo` 建立與讀取：其 git 在剝掉 `GIT_*` 的環境下跑——pre-commit 期間 git 匯出 `GIT_INDEX_FILE`，
`commit -a`／部分 commit 時其值為外層 lock index 的絕對路徑，不剝即對外層 index 讀寫（LL-00012 同源；機制與自證見 `tmprepo`／`test_tmprepo`）。"""
import os
import shutil
import unittest
import unittest.mock

from docsync import adr, book, common, events, gates, ADR_DIR, BACKLOG, EVENTS
from docsync.tests import tmprepo
from docsync.tests.tmprepo import git as _git, write as _write


def _drop_blob(root, rel):
    """刪 HEAD 版該檔的 loose blob：樹物件照列此路徑（ls-tree 正常）、`git show HEAD:<rel>` 失敗＝「在 HEAD 樹卻讀不到」。"""
    sha = _git(root, "rev-parse", f"HEAD:{rel}")
    os.remove(os.path.join(root, ".git", "objects", sha[:2], sha[2:]))


class _TmpRepoCase(unittest.TestCase):
    def repo(self, files, commit=True):
        """臨時 repo（`tmprepo.make_repo`、含 core.quotePath 釘值）＋測後清除；commit=False＝HEAD 未誕生（暫存區非空）。"""
        root = tmprepo.make_repo(files, commit=commit)
        self.addCleanup(shutil.rmtree, root, True)
        return root


ADR_REL = f"{ADR_DIR}/ADR-00001-x.md"
ADR_TEXT = ('---\nid: "ADR-00001"\ntitle: t\ndate: 2026-09-29\nstatus: accepted\nsupersedes: []\nsuperseded_by: []\n---\n'
            "\n## 決定\n\n原文。\n")
READ_FAIL = "HEAD 版讀取失敗"


class TestHeadText(_TmpRepoCase):
    """決定 2：HEAD 未誕生或路徑不在 HEAD 樹＝None（新檔、比對面空）；在樹卻讀不到＝GitError（fail-loud）。"""

    def test_unborn_head_is_none(self):
        ctx = tmprepo.Ctx(self.repo({"a.md": "A\n"}, commit=False))
        self.assertIsNone(ctx.head_text("a.md"))
        self.assertEqual(ctx.head_paths(), frozenset())

    def test_absent_from_head_tree_is_none_and_present_is_text(self):
        root = self.repo({"a.md": "A\n"})
        _write(root, "b.md", "B\n")
        _git(root, "add", "b.md")
        ctx = tmprepo.Ctx(root)
        self.assertIsNone(ctx.head_text("b.md"))
        self.assertEqual(ctx.head_text("a.md"), "A\n")
        self.assertEqual(ctx.head_paths(), frozenset({"a.md"}))

    ODD_PATHS = {"中文檔.md": "甲\n", "docs/新 檔案.md": "乙\n", "sp ace.md": "丙\n"}

    def test_non_ascii_and_space_paths_listed_verbatim(self):
        """HEAD 樹清單以 -z 切分、路徑原樣入集。不帶 -z 時 ls-tree 把非 ASCII 路徑轉義成 `"\\344…"` 字面——
        「路徑在 HEAD」恆判否、head_text 回 None＝被當新檔靜默放行（決定 2 要消滅的與通過同形）。"""
        ctx = tmprepo.Ctx(self.repo(self.ODD_PATHS))
        self.assertEqual(ctx.head_paths(), frozenset(self.ODD_PATHS))
        for rel, text in self.ODD_PATHS.items():
            self.assertEqual(ctx.head_text(rel), text, rel)

    def test_in_head_tree_but_unreadable_raises_naming_path(self):
        root = self.repo({"a.md": "A\n"})
        _drop_blob(root, "a.md")
        with self.assertRaises(common.GitError) as cm:
            tmprepo.Ctx(root).head_text("a.md")
        self.assertIn("a.md", str(cm.exception))

    def test_head_tree_listing_failure_is_not_unborn(self):
        """HEAD 解析得到、樹卻列不出（ref 指向不存在的物件）＝真失敗、不得當「未誕生」放行。"""
        root = self.repo({"a.md": "A\n"})
        with open(os.path.join(root, ".git", "refs", "heads", "main"), "w") as f:
            f.write("0" * 39 + "1\n")
        with self.assertRaises(common.GitError):
            tmprepo.Ctx(root).head_text("a.md")


class TestHeadReadCallSites(_TmpRepoCase):
    """決定 3 射程：HEAD 版讀取失敗一律轉該閘 ERROR finding（指名檔＋錯誤摘要），不得靜默放行、不得 traceback；
    HEAD 缺席（新檔）照常通過、不印 SKIP。"""

    def test_gt02_append_only_unreadable_head_is_error(self):
        root = self.repo({EVENTS: "{}\n"})
        _drop_blob(root, EVENTS)
        fs = events._append_only_leg(tmprepo.Ctx(root), "{}\n{}\n")
        self.assertEqual([f[:3] for f in fs], [("ERROR", "GT-02", EVENTS)], fs)
        self.assertIn(READ_FAIL, fs[0][3])

    def test_gt02_append_only_new_file_passes_without_skip(self):
        self.assertEqual(events._append_only_leg(tmprepo.Ctx(self.repo({"a.md": "A\n"})), "{}\n"), [])
        self.assertEqual(events._append_only_leg(tmprepo.Ctx(self.repo({EVENTS: "{}\n"}, commit=False)), "{}\n"), [])

    def test_gt04_unreadable_head_is_error_naming_file(self):
        root = self.repo({ADR_REL: ADR_TEXT})
        _drop_blob(root, ADR_REL)
        _write(root, ADR_REL, ADR_TEXT.replace("原文", "改寫"))   # 與 HEAD 相同者以工作樹代之、不讀 HEAD 版——須改動才進讀取面
        fs = [f for f in adr.gt_04(tmprepo.Ctx(root)) if f[0] == "ERROR" and READ_FAIL in f[3]]
        self.assertEqual(len(fs), 1, fs)
        self.assertIn("ADR-00001-x.md", fs[0][3])

    def test_gt04_unborn_head_is_empty_face(self):
        root = self.repo({ADR_REL: ADR_TEXT}, commit=False)
        self.assertEqual(adr._files(tmprepo.Ctx(root), head=True), {})
        self.assertEqual([f for f in adr.gt_04(tmprepo.Ctx(root)) if f[0] != "WARN"], [])

    def test_gt05_next_id_head_unreadable_is_error(self):
        root = self.repo({BACKLOG: "<!-- next: BL-00002 -->\n- BL-00001｜a\n"})
        _drop_blob(root, BACKLOG)
        fs = [f for f in book.gt_05(tmprepo.Ctx(root)) if READ_FAIL in f[3]]
        self.assertEqual([f[:3] for f in fs], [("ERROR", "GT-05", BACKLOG)], fs)

    def test_gt05_next_id_head_absent_passes(self):
        """BACKLOG 不在 HEAD（首次建帳）＝單調腿無基準、正常通過。"""
        root = self.repo({"a.md": "A\n"})
        _write(root, BACKLOG, "<!-- next: BL-00002 -->\n- BL-00001｜a\n")
        fs = book.gt_05(tmprepo.Ctx(root))
        self.assertEqual([f for f in fs if READ_FAIL in f[3] or "單調" in f[3] or "回收" in f[3]], [])

    FROZEN_TEXT = "引用 RL-9999。\n縮寫 ADR-00022／00023。\n"

    def test_gt05_frozen_exemption_unreadable_head_is_error_and_hits_still_reported(self):
        """兩處「該行逐字在 HEAD」存量豁免：HEAD 版讀不到＝豁免基準不明——指名 ERROR，命中照「HEAD 無檔＝全報」。"""
        root = self.repo({ADR_REL: self.FROZEN_TEXT})
        _drop_blob(root, ADR_REL)
        ctx = tmprepo.Ctx(root)
        for leg in (book._id_reference_legs, book._id_form_legs):
            fs = leg(ctx)
            self.assertEqual([f[:3] for f in fs if READ_FAIL in f[3]], [("ERROR", "GT-05", ADR_REL)], (leg.__name__, fs))
            self.assertTrue([f for f in fs if READ_FAIL not in f[3]], (leg.__name__, fs))

    def test_gt05_frozen_exemption_readable_head_exempts_verbatim_lines(self):
        ctx = tmprepo.Ctx(self.repo({ADR_REL: self.FROZEN_TEXT}))
        self.assertEqual(book._id_reference_legs(ctx), [])
        self.assertEqual(book._id_form_legs(ctx), [])


class TestIndexConsistencyLeg(_TmpRepoCase):
    """決定 1（掛 GT-12）：暫存區≠HEAD（有 commit 在準備）時，外層 tracked 檔工作樹≠暫存區（gitlink 除外）與
    未追蹤未 ignore 檔逐檔 ERROR；暫存區＝HEAD 時整腿不跑（手動 lint 不誤報）；git 失敗＝ERROR。"""

    def leg(self, root_or_ctx):
        ctx = root_or_ctx if isinstance(root_or_ctx, common.Ctx) else tmprepo.Ctx(root_or_ctx)
        return gates._index_consistency_leg(ctx)

    def test_index_equals_head_does_not_run(self):
        root = self.repo({"a.md": "A\n"})
        _write(root, "a.md", "A2\n")
        _write(root, "new.md", "N\n")
        self.assertEqual(self.leg(root), [])

    def test_all_staged_is_green(self):
        root = self.repo({"a.md": "A\n"})
        _write(root, "a.md", "A2\n")
        _write(root, "new.md", "N\n")
        _git(root, "add", "-A")
        self.assertEqual(self.leg(root), [])

    def test_unstaged_tracked_edits_are_error_per_file(self):
        root = self.repo({"a.md": "A\n", "b.md": "B\n", "c.md": "C\n"})
        _write(root, "a.md", "A2\n")
        _git(root, "add", "a.md")
        _write(root, "a.md", "A3\n")        # 先 add 改寫版、再改工作樹
        _write(root, "b.md", "B2\n")        # 另一 tracked 檔未暫存
        os.remove(os.path.join(root, "c.md"))   # 工作樹刪、暫存區仍在
        fs = self.leg(root)
        self.assertEqual(sorted(f[:3] for f in fs), [("ERROR", "GT-12", r) for r in ("a.md", "b.md", "c.md")], fs)
        self.assertTrue(all("工作樹≠暫存區" in f[3] and "git add" in f[3] for f in fs), fs)

    def test_untracked_not_ignored_is_error_ignored_is_not(self):
        root = self.repo({"a.md": "A\n", ".gitignore": "*.log\n"})
        _write(root, "a.md", "A2\n")
        _git(root, "add", "a.md")
        _write(root, "docs/new.md", "N\n")
        _write(root, "x.log", "L\n")
        fs = self.leg(root)
        self.assertEqual([f[:3] for f in fs], [("ERROR", "GT-12", "docs/new.md")], fs)
        self.assertIn("未追蹤", fs[0][3])

    def test_non_ascii_and_space_paths_named_verbatim(self):
        """status 以 -z 切分：finding 指名原樣路徑。不帶 -z 時 porcelain 把非 ASCII／含空白路徑包成 C 字串轉義字面、指名失準。"""
        root = self.repo({"a.md": "A\n", "中文檔.md": "甲\n", "sp ace.md": "乙\n"})
        _write(root, "a.md", "A2\n")
        _git(root, "add", "a.md")
        _write(root, "中文檔.md", "甲2\n")
        _write(root, "sp ace.md", "乙2\n")
        _write(root, "docs/未追蹤 檔.md", "U\n")
        fs = self.leg(root)
        self.assertEqual(sorted((f[:3], "未追蹤" in f[3]) for f in fs),
                         [(("ERROR", "GT-12", "docs/未追蹤 檔.md"), True),
                          (("ERROR", "GT-12", "sp ace.md"), False),
                          (("ERROR", "GT-12", "中文檔.md"), False)], fs)

    def test_gitlink_is_excluded(self):
        root = self.repo({"a.md": "A\n"})
        sub = os.path.join(root, "sub")
        os.makedirs(sub)
        _git(sub, "init", "-q", "-b", "main")
        _write(sub, "f", "x\n")
        _git(sub, "add", "f")
        _git(sub, "commit", "-qm", "s")
        _git(root, "update-index", "--add", "--cacheinfo", f"160000,{_git(sub, 'rev-parse', 'HEAD')},sub")
        _git(root, "commit", "-qm", "gitlink")
        _write(sub, "f", "y\n")
        _git(sub, "commit", "-qam", "drift")          # 子庫 HEAD 前進＝工作樹側 gitlink≠暫存區
        _write(sub, "g", "u\n")                       # 子庫內未追蹤檔
        _write(root, "a.md", "A2\n")
        _git(root, "add", "a.md")
        self.assertEqual(self.leg(root), [])

    def test_unborn_head_with_nonempty_index_runs(self):
        root = self.repo({"a.md": "A\n"}, commit=False)
        self.assertEqual(self.leg(root), [])
        _write(root, "a.md", "A2\n")
        self.assertEqual([f[:3] for f in self.leg(root)], [("ERROR", "GT-12", "a.md")])

    def test_staged_diff_probe_failure_is_error(self):
        """探測本身失敗＝ERROR、指名 `diff --cached`（不得靜默 return []、不得落到 status 分支）。
        造法＝刪 HEAD commit 的樹物件：`git diff --cached --quiet` 真回 rc 128（git 2.43 實測）。
        ★HEAD ref 指向不存在物件（dangling）造不出此分支——diff --cached 對它回 rc 1、ERROR 實由 status 支產出。"""
        root = self.repo({"a.md": "A\n"})
        tree = _git(root, "rev-parse", "HEAD^{tree}")
        os.remove(os.path.join(root, ".git", "objects", tree[:2], tree[2:]))
        fs = self.leg(root)
        self.assertEqual([f[:3] for f in fs], [("ERROR", "GT-12", "（外層 repo）")], fs)
        self.assertIn("git diff --cached --quiet rc=128", fs[0][3])

    def test_status_failure_is_error(self):
        root = self.repo({"a.md": "A\n"})
        _write(root, "a.md", "A2\n")
        _git(root, "add", "a.md")
        ctx = tmprepo.Ctx(root)
        real = ctx.git_try
        ctx.git_try = lambda *a, cwd=None: (128, "") if "status" in a else real(*a, cwd=cwd)
        fs = self.leg(ctx)
        self.assertTrue(fs and all(f[:2] == ("ERROR", "GT-12") and "rc=128" in f[3] for f in fs), fs)

    def test_caller_git_index_file_is_the_judged_index(self):
        """沿用呼叫端 `GIT_INDEX_FILE`（hook 期＝本次 commit 的暫存區）：以 `common.Ctx`（真 repo 面所用之類、非 `tmprepo.Ctx`）
        在 `GIT_INDEX_FILE=<alt>` 下跑，findings 依 alt 判。alt＝`.git/index` 收 a.md 改寫版後的複本，其後 `.git/index` 還原為 HEAD：
        alt 已收 a.md→不報；b.md 未暫存改動、new.md 未追蹤→照報。對照：同一 repo 以 `.git/index`（＝HEAD）判則整腿不跑。
        ★`git_try` 若剝 `GIT_*`（讀回 `.git/index`＝HEAD、整腿不跑）＝本案紅。"""
        root = self.repo({"a.md": "A\n", "b.md": "B\n"})
        _write(root, "a.md", "A2\n")
        _git(root, "add", "a.md")
        alt = os.path.join(root, ".git", "alt-index")
        shutil.copyfile(os.path.join(root, ".git", "index"), alt)
        _git(root, "reset", "-q")                   # .git/index 回 HEAD；alt 仍收 a.md 改寫版（alt≠HEAD）
        _write(root, "b.md", "B2\n")
        _write(root, "new.md", "N\n")
        self.assertEqual(self.leg(root), [])        # 對照：以 .git/index 判＝暫存區＝HEAD、整腿不跑
        with unittest.mock.patch.dict(os.environ, {**tmprepo.clean_env(), "GIT_INDEX_FILE": alt}, clear=True):
            fs = gates._index_consistency_leg(common.Ctx(root))
        self.assertEqual(sorted((f[:3], "未追蹤" in f[3]) for f in fs),
                         [(("ERROR", "GT-12", "b.md"), False), (("ERROR", "GT-12", "new.md"), True)], fs)

    def test_leg_leaves_index_bytes_intact(self):
        """唯讀（LL-00047）：暫存區≠HEAD（整腿會跑到 status）且另一檔 stat 髒而內容不變時，腿前後 `.git/index` 位元相同。
        ★status 拿掉 `--no-optional-locks`＝刷新 stat 快取後回寫 index＝本案紅。"""
        root = self.repo({"a.md": "A\n", "b.md": "B\n"})
        _write(root, "a.md", "A2\n")
        _git(root, "add", "a.md")
        p = os.path.join(root, "b.md")
        t = os.stat(p).st_mtime - 1000
        os.utime(p, (t, t))                          # stat 髒、內容不變
        # 前提：確入受檢面——plumbing diff-files 不刷新 stat 快取、只憑 stat 判，故列出 b.md
        self.assertIn("b.md", _git(root, "diff-files", "--name-only").split("\n"))
        idx = os.path.join(root, ".git", "index")
        with open(idx, "rb") as f:
            before = f.read()
        fs = self.leg(root)
        with open(idx, "rb") as f:
            self.assertEqual(f.read(), before, "一致性腿回寫了 .git/index")
        self.assertEqual(fs, [])                     # 內容未變＝不報；a.md 已全數暫存

    RENAME_TEXT = "改名偵測以內容相同判定、本行供比對。\n"

    def _renamed(self):
        """old.md 以 `git mv` 改名為 new.md（全暫存）。status.renames 釘 true：機器全域若關改名偵測，拿掉 `--no-renames`
        的變異即失牙齒（同 core.quotePath 釘值之理）。"""
        root = self.repo({"a.md": "A\n", "old.md": self.RENAME_TEXT})
        _git(root, "config", "status.renames", "true")
        _git(root, "mv", "old.md", "new.md")
        return root

    def test_staged_rename_alone_is_green(self):
        """`git mv` 全暫存＝零 finding。★拿掉 `--no-renames`：status 以 `R  <新>\\0<舊>\\0` 兩欄列改名項、-z 單欄切分把舊路徑
        當成一筆（xy 取其前兩字）＝誤報＝本案紅。"""
        self.assertEqual(self.leg(self._renamed()), [])

    def test_renamed_then_edited_names_new_path_once(self):
        """`git mv` 後再改新檔＝恰一筆、指名新路徑（舊路徑為已暫存刪除、不報）。★拿掉 `--no-renames`＝多出舊路徑殘段一筆＝本案紅。"""
        root = self._renamed()
        _write(root, "new.md", self.RENAME_TEXT + "改了。\n")
        fs = self.leg(root)
        self.assertEqual([f[:3] for f in fs], [("ERROR", "GT-12", "new.md")], fs)
        self.assertIn("工作樹≠暫存區", fs[0][3])

    def test_wired_into_gt12(self):
        root = self.repo({"a.md": "A\n"})
        _write(root, "a.md", "A2\n")
        _git(root, "add", "a.md")
        _write(root, "a.md", "A3\n")
        self.assertTrue(any(f[:3] == ("ERROR", "GT-12", "a.md") and "工作樹≠暫存區" in f[3]
                            for f in gates.gt_12(tmprepo.Ctx(root))))


if __name__ == "__main__":
    unittest.main()
