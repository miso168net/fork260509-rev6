"""守 RL-0047／RL-0050：ADR accepted 後不可變、翻案走 supersede 對稱；編號永不重用、禁刪除。

adr.py：load_adrs（工作樹或 HEAD）、gt_04（形制／不可變／對稱／禁刪除／撞號）、gen_decisions_index、backfill_superseded_by。
"""
import os
import re

from . import ADR_DIR
from .common import ERROR, GENERATED_HEADER, GitError, finding, parse_front_matter

RE_ADR_FILENAME = re.compile(r"^(ADR-\d{5})-[a-z0-9][a-z0-9.-]*\.md$")
RE_ADR_ID = re.compile(r"^ADR-\d{5}$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ADR_STATUSES = ("proposed", "accepted", "superseded")
ADR_REQUIRED = ("id", "title", "date", "status")
ADR_MUTABLE_AFTER_ACCEPT = ("superseded_by",)


class Adr:
    def __init__(self, rel, meta, body):
        self.rel, self.meta, self.body = rel, meta, body
        self.id = meta.get("id")
        self.title = meta.get("title")
        self.date = meta.get("date")
        self.status = meta.get("status")
        self.supersedes = _as_list(meta.get("supersedes", []))
        self.superseded_by = _as_list(meta.get("superseded_by", []))
        self.provenance = meta.get("provenance")
        self.tags = _as_list(meta.get("tags", []))
        self.rev5_id = meta.get("rev5_id")
        self.rad_ai = meta.get("rad_ai")


def _as_list(v):
    if v is None or v == "":
        return []
    return list(v) if isinstance(v, list) else [v]


def _files(ctx, head=False):
    """{filename: text}；head=True 讀 git HEAD 樹（無 HEAD／無目錄→{}）。只收 *.md。"""
    if head:
        try:
            names = ctx.git("ls-tree", "--name-only", "HEAD", f"{ADR_DIR}/").split("\n")
        except GitError:
            return {}
        out = {}
        for p in names:
            fn = os.path.basename(p)
            if fn.endswith(".md"):
                t = ctx.head_text(f"{ADR_DIR}/{fn}")
                if t is not None:
                    out[fn] = t
        return out
    d = os.path.join(ctx.root, ADR_DIR)
    if not os.path.isdir(d):
        return {}
    return {fn: ctx.text(f"{ADR_DIR}/{fn}") for fn in sorted(os.listdir(d)) if fn.endswith(".md")}


def load_adrs(ctx, head=False):
    """回 {id: Adr}（id 不合形者以檔名為鍵）。"""
    out = {}
    for fn, text in _files(ctx, head).items():
        meta, body = parse_front_matter(text)
        a = Adr(f"{ADR_DIR}/{fn}", meta, body)
        out[a.id if isinstance(a.id, str) and RE_ADR_ID.fullmatch(a.id) else fn] = a
    return out


def gt_04(ctx):
    """GATE:
      id=GT-04
      rule=RL-0074
      source=rev5:ADR 0012
      drift=ADR 不可變與 supersede 對稱
      face=docs/arc42/decisions/*.md
      trigger=pre-commit
      rc=1
      breaks-if-removed=拍板全文可被改寫、翻案可單向
    """
    out = []
    cur, head = _files(ctx), _files(ctx, head=True)
    for fn in sorted(head):
        if fn not in cur:
            out.append(finding(ERROR, "GT-04", f"{ADR_DIR}/{fn}", "ADR 禁刪除（編號永不重用；翻案＝新檔 supersedes）"))
    if not cur:
        out.append(finding(ERROR, "GT-04", ADR_DIR, "掃描面空集合：docs/arc42/decisions/ 無 ADR——創世 ADR 必須存在"))
        return out
    metas = {}
    for fn, text in sorted(cur.items()):
        where = f"{ADR_DIR}/{fn}"
        meta, body = parse_front_matter(text)
        metas[fn] = (meta, body)
        m = RE_ADR_FILENAME.fullmatch(fn)
        if not m:
            out.append(finding(ERROR, "GT-04", where, "檔名須為 ADR-NNNNN-<slug>.md"))
        for k in ADR_REQUIRED:
            if k not in meta:
                out.append(finding(ERROR, "GT-04", where, f"front-matter 缺必填欄「{k}」"))
        status = meta.get("status")
        if status is not None and status not in ADR_STATUSES:
            out.append(finding(ERROR, "GT-04", where, f"status 須為 {'|'.join(ADR_STATUSES)}：{status!r}"))
        mid = meta.get("id")
        valid_id = isinstance(mid, str) and RE_ADR_ID.fullmatch(mid)
        if "id" in meta and not valid_id:
            out.append(finding(ERROR, "GT-04", where, f"id 須為 ADR-NNNNN：{mid!r}"))
        if m and valid_id and mid != m.group(1):
            out.append(finding(ERROR, "GT-04", where, f"id「{mid}」與檔名編號「{m.group(1)}」不一致（編號＝檔名）"))
        if "date" in meta and not RE_DATE.fullmatch(str(meta["date"])):
            out.append(finding(ERROR, "GT-04", where, f"date 格式須為 YYYY-MM-DD：{meta['date']!r}"))
        for k in ("supersedes", "superseded_by"):
            v = meta.get(k, [])
            if not (isinstance(v, list) and all(isinstance(x, str) and RE_ADR_ID.fullmatch(x) for x in v)):
                out.append(finding(ERROR, "GT-04", where, f"{k} 須為 ADR-NNNNN list（可空 []）"))
        if "tags" in meta and not isinstance(meta["tags"], list):
            out.append(finding(ERROR, "GT-04", where, "tags 須為 list"))
        if "provenance" in meta and not isinstance(meta["provenance"], str):
            out.append(finding(ERROR, "GT-04", where, "provenance 須為字串"))
    seen = {}
    for fn, (meta, _) in sorted(metas.items()):
        i = meta.get("id")
        if isinstance(i, str) and RE_ADR_ID.fullmatch(i):
            if i in seen:
                out.append(finding(ERROR, "GT-04", f"{ADR_DIR}/{fn}", f"id「{i}」與 {seen[i]} 重複配號（編號永不重用）"))
            else:
                seen[i] = fn
    by_id = {meta["id"]: (fn, meta) for fn, (meta, _) in metas.items() if isinstance(meta.get("id"), str) and RE_ADR_ID.fullmatch(meta["id"])}
    for fn, (meta, _) in sorted(metas.items()):
        where = f"{ADR_DIR}/{fn}"
        my = meta.get("id")
        for x in _as_list(meta.get("supersedes", [])):
            if x not in by_id:
                out.append(finding(ERROR, "GT-04", where, f"supersedes 指向不存在的 ADR「{x}」"))
                continue
            tmeta = by_id[x][1]
            if my and my not in _as_list(tmeta.get("superseded_by", [])):
                out.append(finding(ERROR, "GT-04", where, f"supersedes 對稱缺口：{x} 的 superseded_by 未回填「{my}」（python3 tools/docsync generate 回填）"))
            if tmeta.get("status") != "superseded":
                out.append(finding(ERROR, "GT-04", where, f"被翻案的 {x} status 須為 superseded"))
        for x in _as_list(meta.get("superseded_by", [])):
            if x not in by_id:
                out.append(finding(ERROR, "GT-04", where, f"superseded_by 指向不存在的 ADR「{x}」"))
            elif my and my not in _as_list(by_id[x][1].get("supersedes", [])):
                out.append(finding(ERROR, "GT-04", where, f"superseded_by 對稱缺口：{x} 未宣告 supersedes「{my}」"))
    for fn, htext in sorted(head.items()):
        if fn not in metas:
            continue
        hmeta, hbody = parse_front_matter(htext)
        hstatus = hmeta.get("status")
        if hstatus not in ("accepted", "superseded"):
            continue
        where = f"{ADR_DIR}/{fn}"
        cmeta, cbody = metas[fn]
        if cbody != hbody:
            out.append(finding(ERROR, "GT-04", where, f"{hstatus} 後 body 不可變（翻案＝新 ADR supersedes；史料紀律）"))
        for k in sorted(set(hmeta) | set(cmeta)):
            if k in ADR_MUTABLE_AFTER_ACCEPT:
                continue
            if k == "status":
                allowed = ("accepted", "superseded") if hstatus == "accepted" else ("superseded",)
                if cmeta.get(k) not in allowed:
                    out.append(finding(ERROR, "GT-04", where, f"{hstatus} 的 status 僅可轉 superseded：{cmeta.get(k)!r}"))
                continue
            if hmeta.get(k) != cmeta.get(k):
                out.append(finding(ERROR, "GT-04", where, f"{hstatus} 後 front-matter 欄「{k}」不可變"))
    return out


def gen_decisions_index(adrs, events):
    """DECISIONS-INDEX.md 本文：feature 欄自 events.feature_close.adrs 反查、查無印「輕量軌」。"""
    feat = {}
    for e in events:
        if e.get("type") == "feature_close":
            for a in e.get("adrs", []) or []:
                feat.setdefault(a, e.get("feature"))
    lines = [GENERATED_HEADER, "# DECISIONS-INDEX — ADR 索引", "",
             "| id | status | date | title | feature | supersedes | superseded_by |", "|---|---|---|---|---|---|---|"]
    for key in sorted(adrs):
        a = adrs[key]
        lines.append(f"| {a.id} | {a.status} | {a.date} | {a.title} | {feat.get(a.id, '輕量軌')} | "
                     f"{'、'.join(a.supersedes) or '—'} | {'、'.join(a.superseded_by) or '—'} |")
    return "\n".join(lines) + "\n"


def backfill_superseded_by(ctx):
    """generate 時回填 supersede 對稱：被翻案者的 superseded_by 補上翻案者 id；回改動檔 rel 清單。"""
    adrs = load_adrs(ctx)
    changed = []
    for a in adrs.values():
        for x in a.supersedes:
            t = adrs.get(x)
            if t is None or a.id in t.superseded_by:
                continue
            new = sorted(set(t.superseded_by) | {a.id})
            text = ctx.text(t.rel)
            line = f"superseded_by: [{', '.join(new)}]"
            new_text, n = re.subn(r"^superseded_by:[^\n]*$", line, text, count=1, flags=re.M)
            if n == 0:
                new_text = text.replace("\n---\n", f"\n{line}\n---\n", 1)
            with open(os.path.join(ctx.root, t.rel), "w", encoding="utf-8") as f:
                f.write(new_text)
            ctx._cache.pop(t.rel, None)
            t.superseded_by = new
            changed.append(t.rel)
    return changed
