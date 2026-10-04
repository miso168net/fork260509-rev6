"""語料面：context 壓縮 hook（`.claude/hooks/compact-hook.py`；BL-00126）——三模式以 subprocess 實跑，transcript／進度表／壓縮備忘檔皆為暫存目錄合成樣本。
守：①規則源＝`tools/orchestration/compact-rules.md` 之 A／B 圍欄全文注入 ②進度表與壓縮備忘檔只取本 session 主線工具呼叫碰過者
（未碰過之較新檔不取、sidechain 不算、不存在與萬用字元形不算；路徑鍵整值、引號內整段、全形標點斷詞皆認得），碰過者取 mtime 最新
③§C 只在手動觸發且備忘檔 30 分鐘內改過時附、備忘檔非 UTF-8 亦不丟整段注入 ④precompact 與 rehydrate 文首帶主線限定句，auto 觸發
不因主線 context 小而靜默（PreCompact／SessionStart 輸入不帶 agent_id、刻意不設數值門檻）⑤帶 agent_id＝三模式皆靜默
⑥remind 級距：未達不報、跨級一報、同級不重報、回落歸零後再報、只計主線實 usage（sidechain、`<synthetic>` 與零 usage 列不算）
⑦任何輸入恆 exit 0（exit 2 會擋下壓縮；含壞環境變數與不可編碼 stdout）⑧座標段 porcelain 首行前導空白（XY 欄）不被吃掉。
★precompact 之座標段跑 git status（drvfs 上一次約 4 秒）——本檔不跑真 git：precompact 案於行程內載入 hook 模組、座標段換樁，
座標段本身另以查表樁驗命令參數與字面（docsync test 全套已逾 pre-commit 警戒秒數）；選檔邏輯走不碰 git 的 rehydrate 模式以 subprocess 驗。"""
import contextlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from docsync import ROOT

HOOK = os.path.join(ROOT, ".claude", "hooks", "compact-hook.py")
_spec = importlib.util.spec_from_file_location("compact_hook", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)
RULES_MD = os.path.join(ROOT, "tools", "orchestration", "compact-rules.md")
LEDGER = "# 表\n\n## ① 一眼\n\n- 甲\n\n## ③ run 帳\n\n- {m}-run\n\n## ⑦ Rulings\n\n- {m}-rule\n\n## ⑧ 下一步\n\n- {m}-next\n"
NOTES = "# 備忘\n\n## 用法備忘\n\n- 讀我\n\n## C. 本 session 套用值\n\n- {m}-snapshot\n"


def fence(heading):
    """規則檔 `## <heading>` 節下第一對圍欄的內文（hook 注入的正是這段）。"""
    with open(RULES_MD, encoding="utf-8") as f:
        text = f.read()
    sec = re.search(rf"^## {re.escape(heading)}.*?(?=^## |\Z)", text, re.S | re.M).group(0)
    return re.search(r"^```\n(.*?)^```", sec, re.S | re.M).group(1).rstrip()


def tool_line(inp, name="Bash", sidechain=False):
    return json.dumps({"type": "assistant", "isSidechain": sidechain, "message": {
        "role": "assistant", "content": [{"type": "tool_use", "id": "t", "name": name, "input": inp}]}}, ensure_ascii=False)


def usage_line(n, sidechain=False, model="claude-opus-5-5"):
    """實機形：主量落在 cache_read_input_tokens（n=0＝零 usage 列，配 model="<synthetic>" 即 API 錯誤／No response requested. 形）。"""
    return json.dumps({"type": "assistant", "isSidechain": sidechain, "message": {
        "role": "assistant", "model": model, "content": [{"type": "text", "text": "…"}],
        "usage": {"input_tokens": min(n, 2), "cache_creation_input_tokens": 0, "cache_read_input_tokens": max(n - 2, 0),
                  "output_tokens": 0}}})


class _Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.d = self._td.name
        self.tp = os.path.join(self.d, "sess.jsonl")
        self.scratch = os.path.join(self.d, "sess-tmp", "scratchpad")
        os.makedirs(self.scratch)

    def tearDown(self):
        self._td.cleanup()

    def put(self, name, text, age=0):
        p = os.path.join(self.d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        if age:
            t = time.time() - age
            os.utime(p, (t, t))
        return p

    def transcript(self, *lines):
        with open(self.tp, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def payload(self, extra=None):
        return {"transcript_path": self.tp, "session_id": "sess", "scratchpad_dir": self.scratch, **(extra or {})}

    def run_hook(self, mode, payload=None, raw=None, env=None):
        data = raw if raw is not None else json.dumps(self.payload(payload))
        e = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_CODE_AUTO_COMPACT_WINDOW", "COMPACT_REMIND_FROM")}
        e.update(env or {})
        p = subprocess.run(["python3", HOOK, mode], input=data, capture_output=True, encoding="utf-8", errors="replace",
                           cwd=ROOT, env=e, timeout=60)
        return p.returncode, p.stdout, p.stderr

    def run_inproc(self, mode, payload=None, raw=None, env=None):
        """行程內跑 main()（座標段換樁、不碰 git）；回傳 (exit code, stdout)。"""
        buf = io.StringIO()
        stdin = io.StringIO(raw if raw is not None else json.dumps(self.payload(payload)))
        with mock.patch.object(hook, "coords", lambda: "- (座標樁)"), mock.patch.object(sys, "argv", ["compact-hook.py", mode]), \
                mock.patch.object(sys, "stdin", stdin), mock.patch.dict(os.environ), contextlib.redirect_stdout(buf):
            os.environ.pop("CLAUDE_CODE_AUTO_COMPACT_WINDOW", None)
            os.environ.update(env or {})
            with self.assertRaises(SystemExit) as cm:
                hook.main()
        return cm.exception.code, buf.getvalue()


class TestSessionFiles(_Base):
    """選檔：本 session 主線碰過且現存者取 mtime 最新（rehydrate 模式驗、不碰 git）。"""

    def test_only_mentioned_files_newest_mtime_wins(self):
        old = self.put("a-progress.md", LEDGER.format(m="OLD"), age=600)
        new = self.put("b-progress.md", LEDGER.format(m="NEW"), age=60)
        self.put("z-progress.md", LEDGER.format(m="UNSEEN"))  # 全目錄最新、但本 session 未碰
        notes = self.put("x-compact-prompt.md", NOTES.format(m="N"))
        self.transcript(tool_line({"command": f"cat >> {old} <<'EOF'\n- x\nEOF"}),
                        tool_line({"file_path": new, "old_string": "a", "new_string": "b"}, name="Edit"),
                        tool_line({"command": f"python3 - <<'EOF'\np='{notes}'\nEOF"}))
        rc, out, _ = self.run_hook("rehydrate")
        self.assertEqual(rc, 0)
        self.assertIn("NEW-next", out)
        self.assertNotIn("OLD-next", out)
        self.assertNotIn("UNSEEN", out)
        self.assertIn(notes, out)
        self.assertIn("用法備忘", out)
        self.assertIn("僅適用於主線", out)

    def test_path_key_quoted_and_fullwidth_forms_recognized(self):
        spaced = os.path.join(self.d, "with space")
        os.makedirs(spaced)
        a = os.path.join(spaced, "a-progress.md")
        q = os.path.join(spaced, "q-progress.md")
        for path, m in ((a, "PATHKEY"), (q, "QUOTED")):
            with open(path, "w", encoding="utf-8") as f:
                f.write(LEDGER.format(m=m))
        fw = self.put("f-progress.md", LEDGER.format(m="FULLWIDTH"))
        cases = (("PATHKEY", tool_line({"file_path": a, "content": "x"}, name="Write")),
                 ("QUOTED", tool_line({"command": f'cat >> "{q}" <<\'EOF\'\n- x\nEOF'})),
                 ("FULLWIDTH", tool_line({"command": f"echo 見（{fw}）與「{fw}」"})))
        for m, line in cases:
            with self.subTest(m):
                self.transcript(line)
                rc, out, _ = self.run_hook("rehydrate")
                self.assertEqual(rc, 0)
                self.assertIn(f"{m}-next", out)

    def test_sidechain_missing_and_glob_tokens_not_counted(self):
        side = self.put("s-progress.md", LEDGER.format(m="SIDE"))
        self.put("t-compact-prompt.md", NOTES.format(m="N"))
        self.transcript(tool_line({"command": f"cat {side}"}, sidechain=True),
                        tool_line({"command": f"ls {self.d}/*progress*.md {self.d}/*compact-prompt*.md; cat {self.d}/gone-progress.md"}))
        rc, out, _ = self.run_hook("rehydrate")
        self.assertEqual(rc, 0)
        self.assertNotIn("SIDE", out)
        self.assertIn("尚未觸及任何", out)
        self.assertIn("未觸及壓縮備忘檔", out)


class TestPrecompact(_Base):
    def scene(self, notes_age=0, main_tokens=300_000):
        led = self.put("m-progress.md", LEDGER.format(m="MAN"))
        notes = self.put("x-compact-prompt.md", NOTES.format(m="CSNAP"), age=notes_age)
        wf = os.path.join(self.d, "sess", "subagents", "workflows", "wf_demo-001")
        os.makedirs(wf)
        with open(os.path.join(wf, "journal.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"label": "impl-1"}) + "\n")
        tasks = os.path.join(self.d, "sess-tmp", "tasks")
        os.makedirs(tasks)
        open(os.path.join(tasks, "bgtask42.output"), "w").close()
        self.transcript(usage_line(main_tokens), tool_line({"command": f"cat >> {led}"}), tool_line({"command": f"vi {notes}"}))

    def test_manual_fresh_injects_scope_rules_snapshot_ledger_and_c(self):
        self.scene()
        rc, out = self.run_inproc("precompact", {"trigger": "manual"})
        self.assertEqual(rc, 0)
        for s in ("僅適用於主線", fence("A."), fence("B."), "機器快照", "座標樁",
                  "MAN-run", "MAN-rule", "MAN-next", "wf_demo-001", "impl-1", "bgtask42", "CSNAP-snapshot", "手動觸發"):
            self.assertIn(s, out)


    def test_manual_stale_c_not_attached(self):
        self.scene(notes_age=3600)
        rc, out = self.run_inproc("precompact", {"trigger": "manual"})
        self.assertEqual(rc, 0)
        self.assertIn("MAN-next", out)
        self.assertNotIn("CSNAP-snapshot", out)
        self.assertIn("§C 未附", out)

    def test_auto_large_main_context_injects_without_c(self):
        self.scene(main_tokens=700_000)
        rc, out = self.run_inproc("precompact", {"trigger": "auto"})
        self.assertEqual(rc, 0)
        self.assertIn(fence("A."), out)
        self.assertIn("自動觸發", out)
        self.assertNotIn("CSNAP-snapshot", out)

    def test_auto_small_main_context_still_injects(self):
        """刻意不設「主線 context 過小即靜默」門檻：誤靜默主線（丟失全部注入）遠比誤注入 agent（有限定句兜底）嚴重。"""
        self.scene(main_tokens=50_000)
        rc, out = self.run_inproc("precompact", {"trigger": "auto"})
        self.assertEqual(rc, 0)
        self.assertIn("僅適用於主線", out)
        self.assertIn(fence("A."), out)

    def test_non_utf8_notes_keeps_rest_of_injection(self):
        self.scene()
        with open(os.path.join(self.d, "x-compact-prompt.md"), "wb") as f:
            f.write(b"## C. snap\n\xff\xfe bad \x80\n")
        rc, out = self.run_inproc("precompact", {"trigger": "manual"})
        self.assertEqual(rc, 0)
        for s in (fence("A."), "MAN-next", "## §C"):
            self.assertIn(s, out)


class TestCoords(unittest.TestCase):
    """座標段：命令參數寫死於查表樁（外層 status 少了 `--ignore-submodules=dirty` 即查無而紅）、pin 兩向關係與 porcelain 字面。"""
    TABLE = {
        ("git", "branch", "--show-current"): "feat-x",
        ("git", "rev-parse", "--short=7", "HEAD"): "aaaaaaa",
        ("git", "rev-parse", "--short=7", "rev6-admin-root"): "bbbbbbb",
        ("git", "rev-list", "--left-right", "--count", "origin/feat-x...HEAD"): "0\t2",
        ("git", "rev-parse", "HEAD:base-web"): "1111111aaaa",
        ("git", "-C", "base-web", "rev-parse", "--short=7", "HEAD"): "1111111",
        ("git", "rev-parse", "HEAD:rust-api"): "2222222bbbb",
        ("git", "-C", "rust-api", "rev-parse", "--short=7", "HEAD"): "3333333",
        ("git", "status", "--porcelain", "--ignore-submodules=dirty"): "",
        ("git", "-C", "base-web", "status", "--porcelain"): "M  src/a.ts\n?? src/b.ts",
        ("git", "-C", "rust-api", "status", "--porcelain"): "",
    }

    def test_coords_format_and_pin_relation(self):
        with mock.patch.object(hook, "sh", lambda *a, cwd=None: self.TABLE.get(a, f"(rc=1 樁查無 {a})")):
            out = hook.coords()
        for s in ("分支 `feat-x` HEAD `aaaaaaa`｜default `rev6-admin-root` `bbbbbbb`", "領先 2／落後 0",
                  "pin base-web `1111111` ＝ worktree `1111111`", "pin rust-api `2222222` ≠", "porcelain 外層：乾淨",
                  "porcelain base-web：M  src/a.ts｜?? src/b.ts", "porcelain rust-api：乾淨", "NOTES 首行 <!-- wave:", "RULES-VERSION `"):
            self.assertIn(s, out)
        self.assertNotIn("樁查無", out)

    def test_sh_keeps_leading_space_of_porcelain(self):
        self.assertEqual(hook.sh("printf", " M a\\n?? b\\n"), " M a\n?? b")


class TestTasksDir(unittest.TestCase):
    def test_scratchpad_sibling_then_tmpdir_fallback(self):
        self.assertEqual(hook.tasks_dir({"scratchpad_dir": "/x/sess/scratchpad"}), hook.Path("/x/sess/tasks"))
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"CLAUDE_CODE_TMPDIR": d}):
            data = {"transcript_path": os.path.join(d, "proj-slug", "sid.jsonl"), "session_id": "sid"}
            want = os.path.join(d, f"claude-{os.getuid()}", "proj-slug", "sid", "tasks")
            self.assertEqual(str(hook.tasks_dir(data)), want)
            os.makedirs(want)
            open(os.path.join(want, "bgfallback7.output"), "w").close()
            self.assertIn("bgfallback7", hook.bg_tasks(data))

    def test_no_env_probes_platform_root_then_tmp_fallback(self):
        # BL-00137：CC 暫存根依環境而異（macOS 曾實測 /private/tmp、設 TMPDIR 者為 $TMPDIR）——取實存之候選根、皆無取首候選；
        # TMPDIR／TMP／TEMP 釘成不存在值，使「直接讀環境變數」之變異在任何 runner 皆轉紅
        on = lambda root: hook.Path(root) / f"claude-{os.getuid()}" / "proj-slug" / "sid" / "tasks"
        data = {"transcript_path": "/x/proj-slug/sid.jsonl", "session_id": "sid"}
        pinned = {"TMPDIR": "/nonexistent-tmpdir-7q", "TMP": "/nonexistent-tmp-7q", "TEMP": "/nonexistent-temp-7q"}
        with tempfile.TemporaryDirectory() as plat, tempfile.TemporaryDirectory() as fb, mock.patch.dict(os.environ, pinned), \
                mock.patch.object(hook.tempfile, "gettempdir", return_value=plat), mock.patch.object(hook, "TMP_FALLBACK", fb):
            os.environ.pop("CLAUDE_CODE_TMPDIR", None)
            self.assertEqual(hook.tasks_dir(data), on(plat))   # 皆不存在：取首候選（平台根）
            os.makedirs(on(fb))
            self.assertEqual(hook.tasks_dir(data), on(fb))     # 只末位根實存（macOS /private/tmp 形）
            os.makedirs(on(plat))
            self.assertEqual(hook.tasks_dir(data), on(plat))   # 兩者皆實存：依候選序


class TestMainOnlyAndExitCode(_Base):
    def test_agent_id_silences_all_modes(self):
        self.transcript(usage_line(900_000))
        for mode in ("precompact", "rehydrate", "remind"):
            rc, out, _ = self.run_hook(mode, {"agent_id": "a1", "trigger": "manual"})
            self.assertEqual((rc, out), (0, ""), mode)

    def test_garbage_input_exit_zero(self):
        for raw in ("不是 JSON", "[1, 2]"):
            rc, out = self.run_inproc("precompact", raw=raw)
            self.assertEqual(rc, 0, raw)
            self.assertIn("僅適用於主線", out)
            for mode in ("rehydrate", "remind"):
                rc, _, err = self.run_hook(mode, raw=raw)
                self.assertEqual(rc, 0, (mode, raw, err))

    def test_bad_env_and_unencodable_stdout_exit_zero(self):
        for mode in ("precompact", "rehydrate", "remind"):  # 帶 agent_id＝模組載入後即早退：驗的是模組層解析
            rc, _, err = self.run_hook(mode, {"agent_id": "a1"}, env={"COMPACT_REMIND_FROM": "600k"})
            self.assertEqual(rc, 0, (mode, err))
        rc, out, err = self.run_hook("rehydrate", env={"PYTHONIOENCODING": "ascii"})
        self.assertEqual(rc, 0, err)
        self.assertIn("壓縮後回灌", out)


class TestRemind(_Base):
    def seq(self, *lines_per_call, env=None):
        outs = []
        for lines in lines_per_call:
            self.transcript(*lines)
            rc, out, _ = self.run_hook("remind", env=env)
            self.assertEqual(rc, 0)
            outs.append(out)
        return outs

    def test_band_crossing_once_per_band_and_reset_after_drop(self):
        o = self.seq(*[[usage_line(n)] for n in (590_000, 610_000, 620_000, 655_000, 90_000, 612_000)])
        self.assertEqual(o[0], "")
        j = json.loads(o[1])
        self.assertIn("610k", j["systemMessage"])
        self.assertIn("進度表", j["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(o[2], "")
        self.assertIn("650k", json.loads(o[3])["systemMessage"])
        self.assertEqual(o[4], "")
        self.assertTrue(o[5])

    def test_synthetic_and_zero_usage_rows_skipped(self):
        self.transcript(usage_line(700_000), usage_line(0, model="<synthetic>"), usage_line(0))
        self.assertEqual(hook.context_tokens(self.tp), 700_000)
        self.transcript(usage_line(700_000), usage_line(5, model="<synthetic>"))  # synthetic 即使帶數也不算
        self.assertEqual(hook.context_tokens(self.tp), 700_000)
        o = self.seq([usage_line(610_000)], [usage_line(610_000), usage_line(0, model="<synthetic>")],
                     [usage_line(610_000), usage_line(0)], [usage_line(610_000)])
        self.assertTrue(o[0])
        self.assertEqual(o[1:], ["", "", ""])  # 零 usage 列不致歸零、不重複提醒

    def test_sidechain_usage_ignored_and_window_text(self):
        o = self.seq([usage_line(610_000), usage_line(10_000, sidechain=True)],
                     env={"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "500000"})
        self.assertIn("500k", json.loads(o[0])["systemMessage"])

    def test_window_text_read_from_settings(self):
        want = None
        for name in ("settings.local.json", "settings.json"):
            try:
                with open(os.path.join(ROOT, ".claude", name), encoding="utf-8") as f:
                    v = json.load(f).get("autoCompactWindow")
            except (OSError, ValueError):
                continue
            if isinstance(v, int) and v > 0:
                want = f"{v // 1000}k"
                break
        o = self.seq([usage_line(610_000)])
        self.assertIn(want or "auto", json.loads(o[0])["systemMessage"])


if __name__ == "__main__":
    unittest.main()
