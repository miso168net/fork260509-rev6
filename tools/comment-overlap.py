#!/usr/bin/env python3
"""rev5↔rev6 註解逐字重疊核（憲法 §I.5 第 3 款「註解一律重寫」／RL-0065／RL-0076 的機器證據）。

用法：
  python3 tools/comment-overlap.py [--min N] [--max-pct P] <rev6 檔 …>   逐檔對 rev5 同相對路徑檔比對；任一檔超標＝rc 1
  python3 tools/comment-overlap.py test                                  合成樣本自證（搬運判超標／改寫判零重疊／base-web 三型豁免各一正一反與
                                                                         rust-api 零豁免／比對面為空 rc 2 一正一反；pre-commit 於本檔 staged 時跑）
rev5 對應檔＝`../fork260509-rev5/<同相對路徑>`（凍結 worktree；本工具只讀、絕不寫入）；對應檔缺席＝該檔無可比、報 n/a 不計超標。
手法：抽出 `///`／`//!`／`//` 三型註解行、去標記並壓掉全部空白，相鄰註解行併成一段；逐段對 rev5 註解全文找長度 ≥ min
的極大共同子字串，命中字元合計／本檔註解總字元＝重疊比。識別字、SQL 片段、路徑與 doctest 碼行本就兩代共用、門檻 25 字元下仍佔
識別字密集檔 10%～12%，故預設門檻 40 字元／上限 5%：實測逐字搬運檔落 18%～45%、改寫後 ≤4.1%，兩態不相接。
base-web 路徑（repo 根相對首段 `base-web`）三型豁免後再量——帶 fork-delta 標記之既有檔含兩代共享之強制字面、不豁免即結構性必紅而散文命中被淹沒：
  ①含 `[rev6-inline …]` 標記之行整行（標記 token 與 rev5 同軌道同刀名、只差前綴）；
  ②upstream 基線原有之註解行整行（源倉 `fork260509-soybean-admin-base` 之 `example` 分支同相對路徑檔、壓白後全等；基線無此檔＝我方新檔、本型不豁免）；
  ③`原行:` 起至行尾（憲法 §III 修改型契約強制逐字；其前之我方散文照計）。
  豁免字元既不入分子也不入分母、逐檔輸出附三型豁免行數；rust-api 與其餘路徑零豁免、不讀源倉。
退出碼：0 綠／1 任一檔超標／2 rev6 檔缺席或不在 repo、base-web 路徑之源倉或 `example` 分支不可讀、比對面為空（本次引數之 rev5 對應檔
  全缺席，或受比檔全體零可解析註解〔以豁免前計：豁免後零字元是判定結果、非掃描面空〕）；argparse 用法錯亦 2。
"""
import argparse
import contextlib
import io
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
REV5 = ROOT.parent / "fork260509-rev5"
# base-web 基線座標與兩支標記 regex 同 tools/fork-delta-lint.py 之 FORK／BASELINE／MARKER／TRACK（連字檔名不可 import、此處同形宣告）。
FORK = ROOT / "fork260509-soybean-admin-base"
BASELINE = "example"
BASEWEB = "base-web"
MARKER = re.compile(r"原行:\s*(.*\S)\s*$")
TRACK = re.compile(r"\[rev6-inline\s+([A-Z][A-Z0-9-]*)(?:\(([a-z]+)\))?")
EXEMPT_KINDS = ("標記行", "基線原有", "原行載荷")
DEFAULT_MIN = 40
DEFAULT_MAX_PCT = 5.0
WS = re.compile(r"\s+")
MARK = re.compile(r"^\s*(///|//!|//)\s?")


class OverlapError(Exception):
    """結構／環境異常（rc 2）：訊息即輸出行。"""


def comment_lines(lines):
    """回 [(行號, 去註解標記之原文)]，只收 `//` 起首且去標記後非空白之行（未壓白——標記判定要看原字距）。"""
    out = []
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("//"):
            raw = MARK.sub("", line.rstrip("\n"))
            if WS.sub("", raw):
                out.append((i, raw))
    return out


def comment_units(path):
    """回 [(行號, 去標記壓白後文字)]，只收非空註解行。"""
    with open(path, encoding="utf-8") as fh:
        return [(i, WS.sub("", raw)) for i, raw in comment_lines(fh)]


def segments(units):
    """相鄰註解行併段（doc 常跨行、逐行比會漏掉接縫）。"""
    segs, cur, prev = [], [], None
    for ln, text in units:
        if prev is not None and ln != prev + 1:
            segs.append(cur)
            cur = []
        cur.append((ln, text))
        prev = ln
    if cur:
        segs.append(cur)
    return segs


def maximal_hits(mine, theirs, minlen):
    """自左而右貪婪：每個位置以二分找最長仍為 theirs 子字串的前綴，命中即跳過該段。"""
    hits, i, n = [], 0, len(mine)
    while i + minlen <= n:
        lo, hi, best = minlen, n - i, 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if mine[i:i + mid] in theirs:
                best, lo = mid, mid + 1
            else:
                hi = mid - 1
        if best:
            hits.append((i, mine[i:i + best]))
            i += best
        else:
            i += 1
    return hits


def compare(p6, p5, minlen, units=None):
    """回 (重疊比 %, [(行號, 長度, 片段)], 本檔註解總字元)；`units` 缺省＝p6 全部註解行（不豁免）。"""
    theirs = "".join(t for _, t in comment_units(p5))
    units = comment_units(p6) if units is None else units
    total = sum(len(t) for _, t in units)
    file_hits = []
    for seg in segments(units):
        joined = "".join(t for _, t in seg)
        marks, off = [], 0
        for ln, t in seg:
            marks.append((off, ln))
            off += len(t)
        for pos, frag in maximal_hits(joined, theirs, minlen):
            ln = next(l for o, l in reversed(marks) if o <= pos)
            file_hits.append((ln, len(frag), frag))
    hit_len = sum(h[1] for h in file_hits)
    pct = (hit_len * 100.0 / total) if total else 0.0
    return pct, file_hits, total


def git_env():
    """LL-00012：pre-commit 期間 git 匯出外層 GIT_DIR／GIT_INDEX_FILE 等——對源倉下 git 前一律剝 `GIT_*`（未剝＝讀錯 repo）。"""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def read_baseline(fork, rel):
    """回源倉 `example` 分支同相對路徑（base-web 根相對）檔全文；基線無此檔（我方新檔）回 None；源倉或分支不可讀＝OverlapError。"""
    def git(*args):
        return subprocess.run(["git", "-C", str(fork), *args], capture_output=True, text=True, encoding="utf-8", env=git_env())

    if git("rev-parse", "--verify", "-q", f"{BASELINE}^{{commit}}").returncode != 0:
        raise OverlapError(f"源倉 {fork} 缺席或無 `{BASELINE}` 分支——base-web 基線原有註解之豁免無從定界（跑 bash tools/bootstrap.sh 檢修）")
    if git("cat-file", "-e", f"{BASELINE}:{rel}").returncode != 0:
        return None
    shown = git("show", f"{BASELINE}:{rel}")
    if shown.returncode != 0:
        raise OverlapError(f"源倉 `git show {BASELINE}:{rel}` 失敗：{shown.stderr.strip()}")
    return shown.stdout


def exempt_units(path, baseline_text):
    """base-web 檔三型豁免 → (保留之 units, {型: 行數})。判定序＝標記行（整行）→ 基線原有（整行；壓白後全等於基線任一註解行）
    → 原行載荷（只截 `原行:` 起至行尾、其前之我方散文照計）。`baseline_text` 為 None＝基線無此檔、第二型不豁免。"""
    base = set() if baseline_text is None else {WS.sub("", raw) for _, raw in comment_lines(baseline_text.splitlines())}
    kept, stats = [], dict.fromkeys(EXEMPT_KINDS, 0)
    with open(path, encoding="utf-8") as fh:
        rows = comment_lines(fh)
    for ln, raw in rows:
        text = WS.sub("", raw)
        if TRACK.search(raw):
            stats["標記行"] += 1
            continue
        if text in base:
            stats["基線原有"] += 1
            continue
        hit = MARKER.search(raw)
        if hit:
            stats["原行載荷"] += 1
            text = WS.sub("", raw[:hit.start()])
            if not text:
                continue
        kept.append((ln, text))
    return kept, stats


def measure(p6, p5, rel, minlen, fork):
    """單檔量測 → (重疊比 %, 命中, 計量註解總字元, 豁免前註解行數, 豁免統計｜None)。
    `rel`（repo 根相對）首段為 base-web 者三型豁免後量、其餘路徑零豁免（亦不讀源倉）。"""
    raw = comment_units(p6)
    if rel.parts[0] != BASEWEB:
        pct, hits, total = compare(p6, p5, minlen, raw)
        return pct, hits, total, len(raw), None
    units, stats = exempt_units(p6, read_baseline(fork, pathlib.PurePosixPath(*rel.parts[1:]).as_posix()))
    pct, hits, total = compare(p6, p5, minlen, units)
    return pct, hits, total, len(raw), stats


def run(files, minlen, max_pct, root=ROOT, rev5=REV5, fork=FORK):
    rc, compared, parsed = 0, 0, 0
    for arg in files:
        p6 = pathlib.Path(arg).resolve()
        if not p6.is_file():
            print(f"!! {arg}：rev6 檔不存在", flush=True)
            return 2
        try:
            rel = p6.relative_to(root)
        except ValueError:
            print(f"!! {arg}：不在 repo 內", flush=True)
            return 2
        p5 = rev5 / rel
        if not p5.is_file():
            print(f"== {rel}：rev5 無對應檔（n/a）", flush=True)
            continue
        try:
            pct, hits, total, n_raw, stats = measure(p6, p5, rel, minlen, fork)
        except OverlapError as e:
            print(f"!! {rel}：{e}", flush=True)
            return 2
        compared += 1
        parsed += n_raw
        exempt = "" if stats is None else "；豁免 " + "／".join(f"{k} {v} 行" for k, v in stats.items())
        verdict = "超標" if pct >= max_pct else "ok"
        print(f"== {rel}：{len(hits)} 段逐字重疊、佔本檔註解量 {pct:.1f}%（註解總量 {total}{exempt}；門檻 {minlen} 字元／上限 {max_pct:g}%）→ {verdict}", flush=True)
        for ln, length, frag in hits:
            print(f"   L{ln}（{length} 字元）：{frag[:110]}", flush=True)
        if pct >= max_pct:
            rc = 1
    # RL-0051：掃描面空集合即紅——量不到任何東西的「全 ok」是假綠（引數錯檔、或檔型不在本工具之 `//` 解析面）。
    if compared == 0:
        print(f"!! 比對面為空：本次 {len(files)} 檔之 rev5 對應檔全缺席（全 n/a）——無一檔可比、不得回綠", flush=True)
        return 2
    if parsed == 0:
        print(f"!! 比對面為空：受比 {compared} 檔全體零可解析註解（本工具只解析 `//`／`///`／`//!` 起首之行）——無一字可量、不得回綠", flush=True)
        return 2
    return rc


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture_git(repo, *args):
    """合成基線 repo 之 git：剝 `GIT_*`（同 read_baseline）＋壓掉全域 hooksPath／excludesFile／gpgsign（同 tools/fork-delta-lint.py 自測 fixture 形）。"""
    r = subprocess.run(["git", "-C", str(repo), "-c", "core.hooksPath=.git/no-hooks", "-c", "core.excludesFile=",
                        "-c", "commit.gpgsign=false", *args], capture_output=True, text=True, encoding="utf-8", env=git_env())
    if r.returncode != 0:
        raise OverlapError(f"合成基線 git {' '.join(args)} 失敗：{r.stderr.strip()}")


def _run_quiet(files, **roots):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = run(files, DEFAULT_MIN, DEFAULT_MAX_PCT, **roots)
    return rc, buf.getvalue()


def self_test():
    """合成樣本逐案自證；任一案敗＝rc 1、指名案名與實得值。
    量尺本體：同一段散文逐字搬運須判超標、改寫後須判 ok；識別字級短片段不計。
    base-web 三型豁免：全豁免正例一支＋「只拿掉一型之形」反例四支（其餘兩型照豁免、命中恰為被拿掉那型）；rust-api 同內容零豁免且不讀源倉；
    LL-00012 洩漏 env 下仍讀得到基線；源倉不可讀 rc 2。比對面為空：全 n/a／全體零可解析註解 rc 2 各配一反例；豁免後零字元不算空面。"""
    cases = []

    def case(name, ok, detail):
        cases.append((name, bool(ok), detail))

    with tempfile.TemporaryDirectory() as d:
        base = pathlib.Path(d).resolve()
        prose = "//! 這一段是刻意寫得夠長的模組說明散文，用來讓逐字搬運的比對結果超過四十字元的門檻並被本工具當場抓到而不是漏過去。\n"
        (base / "r5.rs").write_text(prose + "/// 次要說明：fn find_by_hash_for_update 走 FOR UPDATE。\npub fn a() {}\n", encoding="utf-8")
        (base / "copied.rs").write_text(prose + "pub fn a() {}\n", encoding="utf-8")
        (base / "rewritten.rs").write_text("//! 重寫過的說明：語意相同、用字不同。\n/// find_by_hash_for_update\npub fn a() {}\n", encoding="utf-8")
        pct_c, hits_c, _ = compare(base / "copied.rs", base / "r5.rs", DEFAULT_MIN)
        pct_r, hits_r, _ = compare(base / "rewritten.rs", base / "r5.rs", DEFAULT_MIN)
        case("搬運樣本判超標", pct_c >= DEFAULT_MAX_PCT and len(hits_c) == 1, f"{pct_c:.1f}%／{len(hits_c)} 段")
        case("改寫樣本判零重疊（識別字級短片段不計）", pct_r == 0.0 and not hits_r, f"{pct_r:.1f}%／{len(hits_r)} 段")

        # ── base-web 三型豁免 ──
        # rev6 樣本四行註解：我方散文／upstream 原註（基線有）／標記行（token 與 rev5 只差前綴）／我方散文＋`原行:` 載荷（rev5 同載荷）。
        root, r5root, fork = base / "rev6", base / "rev5", base / "fork"
        up = "// when the backend response code is in modalLogoutCodes, it means the user will be logged out by a modal"
        code = "const { data: loginToken, error } = await fetchLoginWithCaptcha(userName, password, captcha);"
        tok5 = "// [rev5-inline BASE-WEB-LOGIN-CAPTCHA-WIRING+ 003-auth-session START]"
        mine, lead = "// 我方重寫之說明：軟區附掛驗證碼欄。", "// 改呼 wrapper（我方散文）；"
        r5 = f"{up}\n{tok5}\n// [rev5-inline BASE-WEB-LOGIN-CAPTCHA-WIRING(i) 003-auth-session] 前代說明；原行: {code}\nexport const a = 1;\n"

        def rev6(track="[rev6-inline", payload="原行:"):
            return f"{mine}\n{up}\n{tok5.replace('[rev5-inline', track)}\n{lead}{payload} {code}\nexport const a = 1;\n"

        with_up = f"{up}\n{code}\n"
        variants = {  # 檔名 → (rev6 內容, 基線內容｜None＝基線無此檔)
            "pos.ts": (rev6(), with_up),
            "neg_track.ts": (rev6(track="rev6-inline"), with_up),   # 缺 `[`＝不合 TRACK
            "neg_payload.ts": (rev6(payload="參照:"), with_up),     # 非 `原行:`
            "neg_base.ts": (rev6(), f"{code}\n"),                   # 基線檔無該註解行（碼行同文不算）
            "neg_nofile.ts": (rev6(), None),                        # 基線無此檔（我方新檔）
            "allexempt.ts": (f"{up}\n{tok5.replace('[rev5-inline', '[rev6-inline')}\n", with_up),
        }
        for name, (text6, text_base) in variants.items():
            _write(root / BASEWEB / "src" / name, text6)
            _write(r5root / BASEWEB / "src" / name, r5)
            if text_base is not None:
                _write(fork / "src" / name, text_base)
        _fixture_git(fork, "init", "-q")
        _fixture_git(fork, "checkout", "-q", "-b", BASELINE)
        _fixture_git(fork, "add", "-A")
        _fixture_git(fork, "-c", "user.name=co", "-c", "user.email=co@local", "commit", "-qm", "baseline")

        def m(name, top=BASEWEB, fork_path=fork):
            rel = pathlib.Path(top, "src", name)
            return measure(root / rel, r5root / rel, rel, DEFAULT_MIN, fork_path)

        all_one = dict.fromkeys(EXEMPT_KINDS, 1)
        pct, hits, total, n_raw, stats = m("pos.ts")
        want_total = len(WS.sub("", MARK.sub("", mine))) + len(WS.sub("", MARK.sub("", lead)))
        case("base-web 三型全豁免→零重疊、豁免字元不入分母",
             not hits and pct == 0.0 and total == want_total and n_raw == 4 and stats == all_one,
             f"{pct:.1f}%／{len(hits)} 段／總量 {total}（應 {want_total}）／豁免前 {n_raw} 行／豁免 {stats}")
        for name, kind, needle, label in (
            ("neg_track.ts", "標記行", "BASE-WEB-LOGIN-CAPTCHA-WIRING", "標記行反例：缺 `[` 之 token 不合 TRACK→照計"),
            ("neg_payload.ts", "原行載荷", "fetchLoginWithCaptcha", "原行載荷反例：`參照:` 非 `原行:`→照計"),
            ("neg_base.ts", "基線原有", "modalLogoutCodes", "基線原有反例：基線檔無該註解行→照計"),
            ("neg_nofile.ts", "基線原有", "modalLogoutCodes", "基線原有反例：基線無此檔（我方新檔）→照計"),
        ):
            pct, hits, _t, _n, stats = m(name)
            want = {k: 0 if k == kind else 1 for k in EXEMPT_KINDS}
            case(label, pct >= DEFAULT_MAX_PCT and hits and all(needle in h[2] for h in hits) and stats == want,
                 f"{pct:.1f}%／命中 {[h[2][:48] for h in hits]}／豁免 {stats}（應 {want}）")

        rel_rs = pathlib.Path("rust-api", "src", "pos.rs")
        _write(root / rel_rs, rev6())
        _write(r5root / rel_rs, r5)
        try:
            got = measure(root / rel_rs, r5root / rel_rs, rel_rs, DEFAULT_MIN, base / "no-such-fork")
        except OverlapError as e:  # 讀了源倉＝本案失守（記為案敗、不讓例外吞掉其餘各案）
            got = (0.0, None, None, None, f"OverlapError：{e}")
        plain = compare(root / rel_rs, r5root / rel_rs, DEFAULT_MIN)
        case("rust-api 同內容零豁免：與不豁免量測全等、不讀源倉（源倉不在場亦不報錯）",
             got[4] is None and got[:3] == plain and plain[0] >= DEFAULT_MAX_PCT, f"實得 {got[0]:.1f}%／{got[4]}；不豁免 {plain[0]:.1f}%")

        saved = {k: os.environ.get(k) for k in ("GIT_DIR", "GIT_INDEX_FILE")}
        os.environ["GIT_DIR"], os.environ["GIT_INDEX_FILE"] = str(base / "leaked.git"), str(base / "leaked.index")
        try:
            leaked_rc = subprocess.run(["git", "-C", str(fork), "rev-parse", "--verify", "-q", BASELINE],
                                       capture_output=True, text=True).returncode
            try:
                leaked = m("pos.ts")[4]
            except OverlapError as e:  # 讀不到基線＝本案失守（記為案敗）
                leaked = f"OverlapError：{e}"
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        case("LL-00012：外層 GIT_DIR／GIT_INDEX_FILE 洩漏下仍讀得到基線（同 env 未剝之 git 讀不到）",
             leaked_rc != 0 and leaked == all_one, f"未剝 rc {leaked_rc}／豁免 {leaked}")

        roots = {"root": root, "rev5": r5root, "fork": fork}
        rc, out = _run_quiet([str(root / BASEWEB / "src" / "pos.ts")], root=root, rev5=r5root, fork=base / "no-such-fork")
        case("base-web 路徑源倉不可讀→rc 2 指名（不退回不豁免量測）", rc == 2 and "源倉" in out, out.strip())

        # ── 比對面為空 ──
        _write(root / BASEWEB / "src" / "newonly.ts", f"{mine}\n")  # rev5 無對應檔
        for rel, text6, text5 in (("rust-api/src/clean.rs", "//! 重寫過的說明：語意相同、用字不同。\npub fn a() {}\n", prose),
                                  ("rust-api/src/bare.rs", "pub fn a() {}\n", "pub fn a() {}\n")):
            _write(root / rel, text6)
            _write(r5root / rel, text5)

        def rc_of(*rels):
            return _run_quiet([str(root / r) for r in rels], **roots)

        rc, out = rc_of("base-web/src/newonly.ts")
        case("比對面為空：本次引數之 rev5 對應檔全缺席→rc 2", rc == 2 and "比對面為空" in out and "全缺席" in out, out.strip())
        rc, out = rc_of("base-web/src/newonly.ts", "rust-api/src/clean.rs")
        case("反例：n/a 檔旁有一檔可比→rc 0（單檔 n/a 照舊不計超標）", rc == 0 and "n/a" in out and "比對面為空" not in out, out.strip())
        rc, out = rc_of("rust-api/src/bare.rs")
        case("比對面為空：受比檔全體零可解析註解→rc 2", rc == 2 and "比對面為空" in out and "零可解析註解" in out, out.strip())
        rc, out = rc_of("rust-api/src/bare.rs", "rust-api/src/clean.rs")
        case("反例：零註解檔旁有一檔有註解→rc 0", rc == 0 and "比對面為空" not in out, out.strip())
        rc, out = rc_of("base-web/src/allexempt.ts")
        case("豁免後零字元不算空面（豁免前有可解析註解）→rc 0", rc == 0 and "註解總量 0" in out and "比對面為空" not in out, out.strip())

    failed = [c for c in cases if not c[1]]
    for i, (name, ok, detail) in enumerate(cases, 1):
        print(f"comment-overlap test {'✓' if ok else '✗'} 案{i} {name}", flush=True)
        if not ok:
            print(f"    實得：{detail}", flush=True)
    if failed:
        print(f"comment-overlap test：{len(failed)}／{len(cases)} 案敗", flush=True)
        return 1
    print(f"comment-overlap test：ok（{len(cases)} 案全綠）", flush=True)
    return 0


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "test":
        return self_test()
    ap = argparse.ArgumentParser(description="rev5↔rev6 註解逐字重疊核")
    ap.add_argument("files", nargs="+", help="rev6 檔路徑（相對 repo 根或絕對）")
    ap.add_argument("--min", type=int, default=DEFAULT_MIN, help=f"共同子字串門檻字元數（預設 {DEFAULT_MIN}）")
    ap.add_argument("--max-pct", type=float, default=DEFAULT_MAX_PCT, help=f"逐檔重疊比上限 %%（預設 {DEFAULT_MAX_PCT:g}）")
    a = ap.parse_args()
    return run(a.files, a.min, a.max_pct)


if __name__ == "__main__":
    sys.exit(main())
