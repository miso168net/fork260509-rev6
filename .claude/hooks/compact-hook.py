#!/usr/bin/env python3
"""context 壓縮 hook 三模式（`.claude/settings.json` 掛 PreCompact／SessionStart(matcher=compact)／PostToolUse 三處；BL-00126 自本機工作區入版控）。

  precompact：PreCompact——stdout 併入壓縮指示（auto／manual 皆然）。輸出＝主線限定句＋`tools/orchestration/compact-rules.md` 之 A＋B
             圍欄規則＋hook 當下機器快照（座標、本 session 最近四支 workflow run、近 6 小時背景 task）＋進度表 ③⑦⑧＋依觸發方式之收尾句；
             §C（壓縮備忘檔之 `## C.` 節）只在手動觸發且該檔 30 分鐘內改過時才附。
  rehydrate：SessionStart(matcher=compact)——壓完後回灌主線限定句、壓縮備忘檔「用法備忘」指針、近期 workflow run／背景 task、進度表 ⑧。
  remind：PostToolUse（每次工具呼叫後）——自 transcript 末筆主線實 usage（跳過 `<synthetic>` 與零 usage 列）算 context；過 600k 起每 50k 一級距提醒一次
          （additionalContext 回灌主線＋systemMessage 給 user）；級距記於本 session 暫存目錄、壓縮後回落即歸零。

工作區兩檔的定位（受版控檔不寫工作區路徑；RL-0077）：transcript 之主線工具呼叫輸入中出現過、且現存之檔，各取 mtime 最新——
  進度表＝`*progress*.md`、壓縮備忘檔＝`*compact-prompt*.md`；本 session 未碰過＝不附、並明講。兩檔內容約定＝compact-rules.md 檔頭。
  認檔字面＝路徑鍵（file_path／path／notebook_path）整值、引號內整段、其餘以空白／shell 分隔字元／全形標點斷詞；相對路徑一律以 repo
  根解析。認不到：未加引號而含空白之路徑、緊鄰 CJK 字的路徑、非 repo 根 cwd 下的相對路徑、`~` 與 `$VAR` 形——以 Read／Edit／Write
  或 repo 根相對路徑觸碰即可。
★主線限定（Claude Code 2.1.283／2.1.284 執行檔實證；LL-00040）：只有 PostToolUse 輸入於 subagent 內觸發時帶 `agent_id`（＝靜默；
  三模式同判、防未來版本補欄）。PreCompact 與 SessionStart(compact) 的輸入都**不帶** `agent_id`，workflow agent 自身壓縮時兩者照跑、
  stdout 照樣併入該 agent，且 hook 收到的 session_id／transcript_path 與主線同值——輸入面無從分辨，故 precompact 與 rehydrate 一律
  於文首放主線限定句、由摘要者自判。★刻意不設「主線 context 過小即靜默」一類數值門檻：`<synthetic>` 零 usage 列、PCT 覆寫、伺服器端
  預壓比例與 usage 落後都可能讓主線真壓縮落在門檻下，而誤靜默主線（丟失全部注入）遠比誤注入 agent（有限定句兜底）嚴重。
視窗＝`CLAUDE_CODE_AUTO_COMPACT_WINDOW`（純數字才認）→ `.claude/settings.local.json` → `.claude/settings.json` 之 `autoCompactWindow`；
只用於提醒字面（實效另受模型視窗夾限、以 /context 為準）。恆 exit 0（exit 2 會擋下壓縮）：各段自帶 try、單段失敗只印一行錯誤；
stdout 一律 utf-8（不可編碼字元以替代字元輸出）。
手動試跑：echo '{"trigger":"manual","transcript_path":"<session>.jsonl","session_id":"<id>","scratchpad_dir":"<scratchpad>"}' | python3 .claude/hooks/compact-hook.py precompact
"""
import fnmatch, glob, json, os, re, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


REPO = Path(__file__).resolve().parent.parent.parent
RULES_MD = REPO / "tools" / "orchestration" / "compact-rules.md"
LEDGER_GLOB, NOTES_GLOB = "*progress*.md", "*compact-prompt*.md"
C_FRESH_SECS = 1800
TMP_FALLBACK = "/tmp"   # 暫存根末位候選（測試可換樁）
REMIND_FROM = env_int("COMPACT_REMIND_FROM", 600_000)
REMIND_STEP = 50_000
SCOPE = ("★本段僅適用於主線 session（與 user 對話、派發 workflow 的那一方）；若本對話是被派發任務的 workflow／subagent"
         "（implementer、review、fix、lens 等），忽略本段全部內容、照預設格式摘要你自己的任務。")
PATH_KEYS = ("file_path", "path", "notebook_path")
# 工具呼叫輸入中的 .md 路徑字面：路徑鍵整值與引號內整段另收；其餘遇空白、引號、shell 分隔字元、全形標點（U+3000～303F、U+FF00～FFEF）即斷
_FULLWIDTH = "".join(f"{chr(a)}-{chr(b)}" for a, b in ((0x3000, 0x303F), (0xFF00, 0xFFEF)))
RE_MD = re.compile(r"[^\s\"'`<>|;&(){}=," + _FULLWIDTH + r"]+\.md")
RE_QUOTED_MD = re.compile(r"""(["'])([^"'\n]+?\.md)\1""")


def sh(*args, cwd=REPO):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=10)
        return r.stdout.rstrip("\n") if r.returncode == 0 else f"(rc={r.returncode} {r.stderr.strip()[:120]})"
    except Exception as e:  # noqa: BLE001
        return f"(err {e})"


def section(text, heading_prefix):
    """取 `## <prefix>` 起至下一個 `## ` 前之段落。"""
    m = re.search(rf"^## {re.escape(heading_prefix)}.*?(?=^## |\Z)", text, re.S | re.M)
    return m.group(0).rstrip() if m else ""


def fenced(sec):
    m = re.search(r"^```\n(.*?)^```", sec, re.S | re.M)
    return m.group(1).rstrip() if m else ""


def cap(s, n, tail=True):
    return s if len(s) <= n else (("…（前略）\n" + s[-n:]) if tail else (s[:n] + "\n…（後略）"))


def text(p):
    return p.read_text(encoding="utf-8", errors="replace")


def rel(p):
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def window():
    """自動壓縮視窗設定值（同 CC 解析序：env → 本機設定 → 專案設定）；未設＝None（auto）。"""
    env = os.environ.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW", "")
    if env.isdigit():
        return int(env)
    for name in ("settings.local.json", "settings.json"):
        try:
            v = json.loads((REPO / ".claude" / name).read_text(encoding="utf-8")).get("autoCompactWindow")
        except Exception:  # noqa: BLE001
            continue
        if isinstance(v, int) and v > 0:
            return v
    return None


def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)


def mentions(inp):
    """工具呼叫輸入中的 .md 路徑字面（路徑鍵整值＋引號內整段＋斷詞）。"""
    toks = set()
    if isinstance(inp, dict):
        toks.update(v for k in PATH_KEYS if isinstance(v := inp.get(k), str) and v.endswith(".md"))
    for s in strings(inp):
        toks.update(m.group(2) for m in RE_QUOTED_MD.finditer(s))
        toks.update(RE_MD.findall(s))
    return toks


def session_files(data):
    """{glob: 本 session 主線工具呼叫輸入中出現過、且現存之檔（mtime 升冪）}；transcript 為證、sidechain 不計。"""
    globs = (LEDGER_GLOB, NOTES_GLOB)
    keys = tuple(g.strip("*").split("*")[0] for g in globs)
    found = {g: set() for g in globs}
    tp = data.get("transcript_path")
    if tp and os.path.isfile(tp):
        with open(tp, encoding="utf-8", errors="replace") as f:
            for line in f:
                if '"tool_use"' not in line or not any(k in line for k in keys):
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(d, dict) or d.get("type") != "assistant" or d.get("isSidechain"):
                    continue
                for c in (d.get("message") or {}).get("content") or []:
                    if not (isinstance(c, dict) and c.get("type") == "tool_use"):
                        continue
                    for tok in mentions(c.get("input")):
                        for g in globs:
                            if fnmatch.fnmatch(os.path.basename(tok), g):
                                found[g].add(tok)
    out = {}
    for g, toks in found.items():
        paths = {(Path(t) if os.path.isabs(t) else REPO / t).resolve() for t in toks}
        out[g] = sorted((p for p in paths if p.is_file()), key=lambda p: p.stat().st_mtime)
    return out


def coords():
    sys.path.insert(0, str(REPO / "tools"))
    from docsync import DEFAULT_BRANCH, NOTES, SUBMODULES  # noqa: E402
    out = []
    branch = sh("git", "branch", "--show-current")
    out.append(f"- 分支 `{branch}` HEAD `{sh('git', 'rev-parse', '--short=7', 'HEAD')}`｜default `{DEFAULT_BRANCH}` "
               f"`{sh('git', 'rev-parse', '--short=7', DEFAULT_BRANCH)}`")
    lr = sh("git", "rev-list", "--left-right", "--count", f"origin/{branch}...HEAD")
    if not lr.startswith("("):
        behind, ahead = lr.split()
        out.append(f"- 對 origin/{branch}：領先 {ahead}／落後 {behind}（push 需 user 當次同意）")
    for sub in SUBMODULES:
        pin = sh("git", "rev-parse", f"HEAD:{sub}")[:7]
        wt = sh("git", "-C", sub, "rev-parse", "--short=7", "HEAD")
        relation = "＝" if pin == wt else "≠（worktree 在前＝回外層 git add 子庫 bump pin；pin 在前＝worktree 內 merge --ff-only；先機判方向）"
        out.append(f"- pin {sub} `{pin}` {relation} worktree `{wt}`")
    # drvfs 上 status 以秒計：三支並行；外層略過子庫工作樹掃描（子庫髒檔逐庫另報，新 commit 與 staged gitlink 照報）
    names = ("外層", *SUBMODULES)
    cmds = (("git", "status", "--porcelain", "--ignore-submodules=dirty"),
            *(("git", "-C", sub, "status", "--porcelain") for sub in SUBMODULES))
    with ThreadPoolExecutor(len(cmds)) as ex:
        statuses = list(ex.map(lambda a: sh(*a), cmds))
    for name, p in zip(names, statuses):
        lines = p.splitlines()
        out.append(f"- porcelain {name}：" + ("乾淨" if not p else "｜".join(lines[:20]) + ("｜…" if len(lines) > 20 else "")))
    try:
        wave = (REPO / NOTES).read_text(encoding="utf-8").splitlines()[0]
        rv = re.search(r"RULES-VERSION: ([0-9a-f]+)", (REPO / "tools/orchestration/_sk_rules.js").read_text(encoding="utf-8"))
        out.append(f"- NOTES 首行 {wave}｜RULES-VERSION `{rv.group(1) if rv else '?'}`")
    except Exception as e:  # noqa: BLE001
        out.append(f"- (NOTES／RULES-VERSION 讀取失敗 {e})")
    return "\n".join(out)


def workflow_runs(data, limit=4):
    tp = data.get("transcript_path")
    if not tp:
        return "- （hook 輸入無 transcript_path）"
    runs = sorted(glob.glob(str(Path(tp).with_suffix("")) + "/subagents/workflows/wf_*/journal.jsonl"),
                  key=os.path.getmtime)[-limit:]
    if not runs:
        return "- （本 session 無 workflow run）"
    out = []
    for j in runs:
        starts, results, last_label, last_status = 0, 0, "", ""
        try:
            with open(j, encoding="utf-8") as fh:
                for line in fh:
                    d = json.loads(line)
                    if "label" in d:
                        starts, last_label, last_status = starts + 1, d["label"], "已起未回（在跑或已被停；以對話為準）"
                    elif isinstance(d.get("result"), dict):
                        results += 1
                        r = d["result"]
                        last_status = r.get("status") or r.get("agentStatus") or "done"
        except Exception as e:  # noqa: BLE001
            last_status = f"(journal 讀取失敗 {e})"
        age = int((time.time() - os.path.getmtime(j)) / 60)
        out.append(f"- `{Path(j).parent.name}`：起 {starts}／回 {results}｜末支「{last_label}」→{last_status}｜journal {age} 分鐘前")
    return "\n".join(out)


def tasks_dir(data):
    """背景 task 輸出目錄＝本 session 暫存目錄之 `tasks/`（輸入帶 scratchpad_dir 時為其同層；否則在候選暫存根中取實存者）。
    候選序＝CLAUDE_CODE_TMPDIR → 平台暫存根（gettempdir；CC 未設前者時取 os.tmpdir＝TMPDIR／TMP／TEMP／/tmp）→ TMP_FALLBACK；
    不寫死單一根：macOS 曾實測 CC 用 /tmp（＝/private/tmp）而 hook 之 gettempdir 為 /var/folders/…/T（BL-00137），設 TMPDIR 之環境則相反；
    皆不存在時取首候選。"""
    sp = data.get("scratchpad_dir")
    if sp:
        return Path(sp).parent / "tasks"
    tp, sid = data.get("transcript_path"), data.get("session_id")
    if not (tp and sid):
        return None
    tail = Path(f"claude-{os.getuid()}") / Path(tp).parent.name / sid / "tasks"
    roots = dict.fromkeys(r for r in (os.environ.get("CLAUDE_CODE_TMPDIR"), tempfile.gettempdir(), TMP_FALLBACK) if r)
    cands = [Path(r) / tail for r in roots]
    return next((c for c in cands if c.is_dir()), cands[0])


def bg_tasks(data, hours=6):
    d = tasks_dir(data)
    if d is None:
        return "- （hook 輸入無 session 座標）"
    files = [f for f in d.glob("*.output") if time.time() - f.stat().st_mtime < hours * 3600] if d.is_dir() else []
    if not files:
        return f"- （近 {hours} 小時無背景 task 輸出）"
    files.sort(key=lambda f: f.stat().st_mtime)
    return "\n".join(f"- task `{f.stem}`｜{f.stat().st_size} bytes｜{int((time.time() - f.stat().st_mtime) / 60)} 分鐘前"
                     for f in files[-10:])


def context_tokens(tp):
    """transcript 末筆主線 assistant 之實 usage 總量（≈ 當下 context）；`<synthetic>`（API 錯誤、No response requested.）與零 usage 列
    不算、續往前找；找不到回 None。"""
    if not tp or not os.path.isfile(tp):
        return None
    path = Path(tp)
    size = path.stat().st_size
    for back in (2_000_000, 8_000_000, size):
        with open(path, "rb") as f:
            f.seek(max(0, size - back))
            lines = f.read().decode("utf-8", "replace").splitlines()
        for line in reversed(lines):
            if '"usage"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            m = d.get("message") if isinstance(d, dict) else None
            if (d.get("type") == "assistant" and isinstance(m, dict) and m.get("usage") and not d.get("isSidechain")
                    and m.get("model") != "<synthetic>"):
                u = m["usage"]
                n = sum(u.get(k, 0) or 0 for k in ("input_tokens", "cache_creation_input_tokens",
                                                    "cache_read_input_tokens", "output_tokens"))
                if n:
                    return n
        if back >= size:
            break
    return None


def precompact(data):
    trig = data.get("trigger", "?")
    try:
        rules = text(RULES_MD)
    except Exception:  # noqa: BLE001
        rules = ""
    a, b = fenced(section(rules, "A.")), fenced(section(rules, "B."))
    parts = [f"【壓縮指示｜PreCompact hook 注入｜trigger={trig}｜{time.strftime('%Y-%m-%d %H:%M:%S')}】", SCOPE,
             "摘要一律 zh-TW，以下規則取代預設摘要格式。",
             a or "（A 規則抽取失敗——照「換手後不必重讀對話就能繼續幹活」保留具體值）", b]
    parts.append("\n## 機器快照（hook 執行當下；與對話衝突時以對話中較新者為準；摘要須照抄其中之 SHA、runId、task id、髒檔清單）")
    for title, fn in (("座標", coords), ("workflow run（本 session 最近四支）", lambda: workflow_runs(data)),
                      ("背景 task", lambda: bg_tasks(data))):
        try:
            parts.append(f"### {title}\n{fn()}")
        except Exception as e:  # noqa: BLE001
            parts.append(f"### {title}\n- (失敗 {e})")
    try:
        files = session_files(data)
    except Exception as e:  # noqa: BLE001
        files = {}
        parts.append(f"(工作區檔定位失敗 {e})")
    ledger = (files.get(LEDGER_GLOB) or [None])[-1]
    notes = (files.get(NOTES_GLOB) or [None])[-1]
    if ledger:
        try:
            t = text(ledger)
            parts.append(f"\n## 進度表摘錄（`{rel(ledger)}`；壓後以該檔為接手依據）")
            for pre, n in (("③", 3000), ("⑦", 5000), ("⑧", 4000)):
                parts.append(cap(section(t, pre), n))
        except Exception as e:  # noqa: BLE001
            parts.append(f"(進度表讀取失敗 {e})")
    else:
        parts.append("\n（本 session 尚未觸及任何 `*progress*.md` 進度表——摘要以對話為準。）")
    try:
        fresh = notes is not None and time.time() - notes.stat().st_mtime < C_FRESH_SECS
        if trig == "manual" and fresh:
            parts.append(f"\n## §C（`{rel(notes)}`；手動觸發、30 分鐘內寫過＝附上）\n"
                         + cap(section(text(notes), "C."), 15000, tail=False))
        else:
            parts.append("\n（§C 未附：非手動觸發、本 session 未觸及壓縮備忘檔、或逾 30 分鐘未更新——以對話與本快照為準、勿引用舊 §C。）")
    except Exception as e:  # noqa: BLE001
        parts.append(f"\n(§C 讀取失敗 {e}——以對話與本快照為準)")
    if trig == "auto":
        parts.append("\n★本次為**自動觸發**（主線工作可能停在中段）：摘要末段寫明「壓完直接接續被打斷的那一步、不等 user」，"
                     "並列出下一個具體動作（命令級）與其前置檢查（六步序第幾步、在飛 run 勿重發射）。")
    else:
        parts.append("\n★本次為**手動觸發**：壓縮不是停點（停點唯三＝CLAUDE.md §2；user 2026-10-03 糾正）——摘要末段寫明「壓完直接接續"
                     "進度表 ⑧ 的下一步、不等 user」，並列出下一個具體動作（命令級）與其前置檢查（六步序第幾步、在飛 run 勿重發射）。")
    print("\n".join(p for p in parts if p))


def rehydrate(data):
    parts = ["=== 壓縮後回灌（compact hook）===", SCOPE]
    try:
        files = session_files(data)
    except Exception as e:  # noqa: BLE001
        files = {}
        parts.append(f"(工作區檔定位失敗 {e})")
    ledger = (files.get(LEDGER_GLOB) or [None])[-1]
    notes = (files.get(NOTES_GLOB) or [None])[-1]
    if notes:
        parts.append(f"先讀：`{rel(notes)}`「用法備忘」與進度表 ⑧；在飛 run 勿重發射（以 runId 看 journal）。")
    else:
        parts.append("先讀：進度表 ⑧（下方）與 `docs/ops/NOTES.md`「下一步」；在飛 run 勿重發射（以 runId 看 journal）。"
                     "（本 session 未觸及壓縮備忘檔）")
    for title, fn in (("workflow run", lambda: workflow_runs(data, 3)), ("背景 task", lambda: bg_tasks(data, 3))):
        try:
            parts.append(f"[{title}]\n{fn()}")
        except Exception as e:  # noqa: BLE001
            parts.append(f"[{title}] (失敗 {e})")
    if ledger:
        try:
            parts.append(f"[進度表 `{rel(ledger)}` ⑧]\n" + cap(section(text(ledger), "⑧"), 3000))
        except Exception as e:  # noqa: BLE001
            parts.append(f"(進度表讀取失敗 {e})")
    else:
        parts.append("（本 session 尚未觸及任何 `*progress*.md` 進度表）")
    print("\n".join(parts))


def remind_state(data):
    sp = data.get("scratchpad_dir")
    if sp:
        return Path(sp) / "compact-remind.json"
    return Path(tempfile.gettempdir()) / f"compact-remind-{data.get('session_id', 'unknown')}.json"


def remind(data):
    n = context_tokens(data.get("transcript_path"))
    if n is None:
        return
    st = remind_state(data)
    try:
        last = json.loads(st.read_text(encoding="utf-8")).get("band", 0)
    except Exception:  # noqa: BLE001
        last = 0
    band = 0 if n < REMIND_FROM else REMIND_FROM + (n - REMIND_FROM) // REMIND_STEP * REMIND_STEP
    if band == last:
        return
    st.parent.mkdir(parents=True, exist_ok=True)
    st.write_text(json.dumps({"band": band}), encoding="utf-8")
    if band < last or band == 0:  # 壓縮後回落＝只歸零、不提醒
        return
    w = window()
    wtxt = f"{w // 1000}k 視窗" if w else "auto 視窗"
    k = n // 1000
    print(json.dumps({
        "systemMessage": f"context 約 {k}k（≥{band // 1000}k）：單元邊界可手動 /compact（不帶參數）；{wtxt}扣緩衝後自動壓縮",
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"【context 提醒】主線 context 約 {k}k（已過 {band // 1000}k 級距；自動壓縮＝{wtxt}扣緩衝、/context 顯示為準）。"
                "①進度表 ③⑦⑧ 須已是最新（隨做隨記；自動壓縮可能落在任何一步）"
                "②若此刻在單元邊界（上一支六步序⑥已落、下一支未發射），回覆中提醒 user 可手動 `/compact`（不帶參數、hook 自動注入規則）；"
                "否則照常續跑、不自行暫停（單元間不自設暫停）。"),
        },
    }, ensure_ascii=False))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    mode = sys.argv[1] if len(sys.argv) > 1 else "precompact"
    try:
        raw = "" if sys.stdin.isatty() else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:  # noqa: BLE001
        data = {}
    if not isinstance(data, dict):
        data = {}
    if data.get("agent_id"):  # subagent 內觸發（PostToolUse 等帶此欄者）＝不作用
        sys.exit(0)
    try:
        {"rehydrate": rehydrate, "remind": remind}.get(mode, precompact)(data)
    except Exception as e:  # noqa: BLE001
        try:
            print(f"(compact-hook 失敗 {e}；以對話為準)")
        except Exception:  # noqa: BLE001
            pass
    sys.exit(0)


if __name__ == "__main__":
    main()
