#!/usr/bin/env python3
"""rev5↔rev6 註解逐字重疊核（憲法 §I.5 第 3 款「註解一律重寫」／RL-0065／RL-0076 的機器證據）。

用法：
  python3 tools/comment-overlap.py [--min N] [--max-pct P] <rev6 檔 …>   逐檔對 rev5 同相對路徑檔比對；任一檔超標＝rc 1
  python3 tools/comment-overlap.py test                                  合成樣本自證（逐字搬運判紅、改寫判綠；pre-commit 於本檔 staged 時跑）
rev5 對應檔＝`../fork260509-rev5/<同相對路徑>`（凍結 worktree；本工具只讀、絕不寫入）；對應檔缺席＝該檔無可比、報 n/a 不計超標。
手法：抽出 `///`／`//!`／`//` 三型註解行、去標記並壓掉全部空白，相鄰註解行併成一段；逐段對 rev5 註解全文找長度 ≥ min
的極大共同子字串，命中字元合計／本檔註解總字元＝重疊比。識別字、SQL 片段、路徑與 doctest 碼行本就兩代共用、門檻 25 字元下仍佔
識別字密集檔 10%～12%，故預設門檻 40 字元／上限 5%：實測逐字搬運檔落 18%～45%、改寫後 ≤4.1%，兩態不相接。
"""
import argparse
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
REV5 = ROOT.parent / "fork260509-rev5"
DEFAULT_MIN = 40
DEFAULT_MAX_PCT = 5.0
WS = re.compile(r"\s+")
MARK = re.compile(r"^\s*(///|//!|//)\s?")


def comment_units(path):
    """回 [(行號, 去標記壓白後文字)]，只收非空註解行。"""
    out = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            s = line.lstrip()
            if s.startswith("//"):
                text = WS.sub("", MARK.sub("", line.rstrip("\n")))
                if text:
                    out.append((i, text))
    return out


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


def compare(p6, p5, minlen):
    """回 (重疊比 %, [(行號, 長度, 片段)], 本檔註解總字元)。"""
    theirs = "".join(t for _, t in comment_units(p5))
    units = comment_units(p6)
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


def run(files, minlen, max_pct):
    rc = 0
    for arg in files:
        p6 = pathlib.Path(arg).resolve()
        if not p6.is_file():
            print(f"!! {arg}：rev6 檔不存在")
            return 2
        try:
            rel = p6.relative_to(ROOT)
        except ValueError:
            print(f"!! {arg}：不在 repo 內")
            return 2
        p5 = REV5 / rel
        if not p5.is_file():
            print(f"== {rel}：rev5 無對應檔（n/a）")
            continue
        pct, hits, total = compare(p6, p5, minlen)
        verdict = "超標" if pct >= max_pct else "ok"
        print(f"== {rel}：{len(hits)} 段逐字重疊、佔本檔註解量 {pct:.1f}%（註解總量 {total}；門檻 {minlen} 字元／上限 {max_pct:g}%）→ {verdict}")
        for ln, length, frag in hits:
            print(f"   L{ln}（{length} 字元）：{frag[:110]}")
        if pct >= max_pct:
            rc = 1
    return rc


def self_test():
    """合成樣本：同一段散文逐字搬運須判超標、改寫後須判 ok；識別字級短片段不計。"""
    with tempfile.TemporaryDirectory() as d:
        base = pathlib.Path(d)
        prose = "//! 這一段是刻意寫得夠長的模組說明散文，用來讓逐字搬運的比對結果超過四十字元的門檻並被本工具當場抓到而不是漏過去。\n"
        (base / "r5.rs").write_text(prose + "/// 次要說明：fn find_by_hash_for_update 走 FOR UPDATE。\npub fn a() {}\n", encoding="utf-8")
        (base / "copied.rs").write_text(prose + "pub fn a() {}\n", encoding="utf-8")
        (base / "rewritten.rs").write_text("//! 重寫過的說明：語意相同、用字不同。\n/// find_by_hash_for_update\npub fn a() {}\n", encoding="utf-8")
        pct_c, hits_c, _ = compare(base / "copied.rs", base / "r5.rs", DEFAULT_MIN)
        pct_r, hits_r, _ = compare(base / "rewritten.rs", base / "r5.rs", DEFAULT_MIN)
    assert pct_c >= DEFAULT_MAX_PCT and len(hits_c) == 1, f"搬運樣本應判超標：{pct_c:.1f}%／{len(hits_c)} 段"
    assert pct_r == 0.0 and not hits_r, f"改寫樣本應判零重疊：{pct_r:.1f}%／{len(hits_r)} 段"
    print("comment-overlap test：ok（搬運判超標、改寫判零重疊）")
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
