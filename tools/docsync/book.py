"""守 RL-0050／RL-0046：配號取 next 後 bump、唯一、單調、永不回收；前代編號一律帶 rev5:／rev4: 前綴、裸刀號禁。

book.py（一）：GT-05 ID 家族（BL／LL／RL 三帳＋ADR 檔名）、現在式面跨代裸編號（提及豁免、rev6 刀集豁免）、兩子庫碼面掃描。
（二）GT-06／GT-11／errata 與（三）GT-10 隨後續 Task 併入本檔。
"""
import os
import re

from . import BACKLOG, BACKLOG_DEFERRED, LESSONS_INDEX, LESSONS_DIR, RULES, ADR_DIR, EVENTS, SUBMODULES, CONSTITUTION
from .common import ERROR, SKIP, finding

ID_FAMILIES = {"BL": (BACKLOG, [BACKLOG_DEFERRED]), "LL": (LESSONS_INDEX, [LESSONS_DIR]), "RL": (RULES, [])}
RE_NEXT_ID = re.compile(r"<!--\s*next:\s*(BL|LL|RL)-(\d{4,5})\s*-->")
# 條目形＝家族真源（附錄 E 定 ID 形；行形承 rev5：帳本 `- ID｜`、LESSONS 索引可裸段形、RULES 為表列）
RE_ENTRY = {
    "BL": re.compile(r"^- (BL-\d{5})｜", re.M),
    "LL": re.compile(r"^(?:- )?(?:\*\*)?(LL-\d{5})(?:\*\*)?｜", re.M),
    "RL": re.compile(r"^\|\s*(RL-\d{4})\s*\|", re.M),
}
RE_LL_FILE = re.compile(r"^(LL-\d{5})-[a-z0-9][a-z0-9-]*\.md$")
RE_ADR_FILE = re.compile(r"^ADR-(\d{5})-")
# 刀名腿要求「NNN-」後至少兩段（rev5 刀名皆兩段以上），單段形如 256-bit／404-page 不入射程
BARE_REV5 = re.compile(r"(?<![A-Za-z0-9:_/-])(B-\d{3}|L-\d{3}|ADR 0\d{3}|Lint\d{2}|\d{3}-[a-z][a-z0-9]*(?:-[a-z0-9]+)+)(?![A-Za-z0-9-])")
MENTION = re.compile(r"`[^`\n]*`|「[^」\n]*」")
RE_KNIFE = re.compile(r"^\d{3}-")
SUB_SCAN = r"(^|[^A-Za-z0-9:_-])(B-[0-9]{3}|L-[0-9]{3})([^0-9]|$)"

PRESENT_TENSE_FACE = ("docs/arc42/", "docs/c4/", "docs/compliance/", "docs/process/", "docs/ops/", "docs/generated/",
                      "README.md", "CLAUDE.md", CONSTITUTION, "tools/", "deploy/", ".githooks/", ".claude/hooks/", ".claude/settings.json")
HISTORY_FACE = ("docs/brainstorms/", "specs/", "docs/reviews/")
THIRD_PARTY_FACE = (".claude/skills/", ".specify/")
FIXTURE_FACE = ("tools/docsync/tests/",)
BOOK_FACE = ("docs/arc42/", "docs/c4/", "docs/compliance/", "docs/process/")


def face_of(rel):
    """回 present／history／third／fixture／book 之外的 None；constitution 明列現在式面、優先於 .specify/ 第三方面。"""
    if rel.startswith(FIXTURE_FACE):
        return "fixture"
    if rel == CONSTITUTION:
        return "present"
    if rel.startswith(THIRD_PARTY_FACE):
        return "third"
    if rel.startswith(HISTORY_FACE):
        return "history"
    if rel.startswith(PRESENT_TENSE_FACE):
        return "present"
    return None


def is_book(rel):
    return rel.startswith(BOOK_FACE) and not rel.startswith(ADR_DIR + "/")


def _text_files(ctx, face="present"):
    """tracked 且屬指定面的文字檔（前 8KB 含 NUL 視為二進位、跳過）。"""
    for rel in ctx.tracked:
        if face_of(rel) != face:
            continue
        p = os.path.join(ctx.root, rel)
        try:
            with open(p, "rb") as f:
                if b"\x00" in f.read(8192):
                    continue
        except OSError:
            pass
        text = ctx.text(rel)
        if text is not None:
            yield rel, text


def _family_state(ctx, fam, head=False):
    """回 (present, next, [(id, where)…])；head=True 讀 HEAD 版（LESSONS/ 目錄以 tracked 名冊代）。"""
    main, extras = ID_FAMILIES[fam]
    read = ctx.head_text if head else ctx.text
    text = read(main)
    if text is None:
        return False, None, []
    nxt = None
    for m in RE_NEXT_ID.finditer(text):
        if m.group(1) == fam:
            nxt = int(m.group(2))
    ids = [(m.group(1), main) for m in RE_ENTRY[fam].finditer(text)]
    for extra in extras:
        if extra == LESSONS_DIR:
            names = sorted({os.path.basename(p) for p in ctx.tracked if p.startswith(LESSONS_DIR + "/")})
            if not head and os.path.isdir(os.path.join(ctx.root, LESSONS_DIR)):
                names = sorted(set(names) | set(os.listdir(os.path.join(ctx.root, LESSONS_DIR))))
            ids += [(RE_LL_FILE.match(n).group(1), f"{LESSONS_DIR}/{n}") for n in names if RE_LL_FILE.match(n)]
        else:
            t = read(extra)
            if t:
                ids += [(m.group(1), extra) for m in RE_ENTRY[fam].finditer(t)]
    return True, nxt, ids


def _num(id_):
    return int(id_.rsplit("-", 1)[1])


def _rev6_knives(ctx):
    names = {p.split("/")[1] for p in ctx.tracked if p.startswith("specs/") and p.count("/") >= 2}
    d = os.path.join(ctx.root, "specs")
    if os.path.isdir(d):
        names |= {n for n in os.listdir(d) if os.path.isdir(os.path.join(d, n))}
    ev = ctx.text(EVENTS) or ""
    names |= set(re.findall(r'"feature":\s*"(\d{3}-[a-z0-9-]+)"', ev))
    return names


def gt_05(ctx):
    """GATE:
      id=GT-05
      rule=RL-0050
      source=rev5:ADR 0012
      drift=配號唯一單調、跨代裸編號
      face=docs/ops 三帳＋現在式面＋兩子庫 pin 樹
      trigger=pre-commit
      rc=1
      breaks-if-removed=號碼可回收、rev5 編號走私入 rev6 現在式文件
    """
    out = []
    for fam in ("BL", "LL", "RL"):
        main = ID_FAMILIES[fam][0]
        present, nxt, ids = _family_state(ctx, fam)
        if not present:
            if fam == "RL":
                out.append(finding(ERROR, "GT-05", main, "掃描面空集合：RULES.md 缺席——規則層首版必須存在"))
            else:
                out.append(finding(SKIP, "GT-05", main, f"GT-05.ledgers-absent：{fam} 家族帳本 {main} 尚未建檔（Day-1；波 2 ops 帳本空檔即解除）"))
            continue
        if nxt is None:
            out.append(finding(ERROR, "GT-05", main, f"缺 next-id 檔頭（<!-- next: {fam}-NNNNN -->）"))
        seen = {}
        for id_, where in ids:
            if id_ in seen:
                out.append(finding(ERROR, "GT-05", where, f"{id_} 重複配號（已見於 {seen[id_]}；號碼永不重用）"))
            seen.setdefault(id_, where)
            if nxt is not None and _num(id_) >= nxt:
                out.append(finding(ERROR, "GT-05", where, f"{id_} ≥ next {fam}-{nxt}（配號取 next 後 bump）"))
        hpresent, hnxt, hids = _family_state(ctx, fam, head=True)
        if hpresent and hnxt is not None:
            if nxt is not None and nxt < hnxt:
                out.append(finding(ERROR, "GT-05", main, f"next-id 單調違反：HEAD {fam}-{hnxt} → 現 {fam}-{nxt}"))
            hset = {i for i, _ in hids}
            for id_, where in ids:
                if id_ not in hset and _num(id_) < hnxt:
                    out.append(finding(ERROR, "GT-05", where, f"{id_} 為新條目但號碼 < HEAD next {fam}-{hnxt}（號碼不回收）"))
    adr_nums = {}
    for rel in ctx.tracked:
        if rel.startswith(ADR_DIR + "/"):
            m = RE_ADR_FILE.match(os.path.basename(rel))
            if m:
                if m.group(1) in adr_nums:
                    out.append(finding(ERROR, "GT-05", rel, f"ADR 檔名編號 {m.group(1)} 與 {adr_nums[m.group(1)]} 重複"))
                adr_nums.setdefault(m.group(1), rel)
    knives = _rev6_knives(ctx)
    for rel, text in _text_files(ctx, "present"):
        for i, line in enumerate(text.split("\n"), 1):
            for m in BARE_REV5.finditer(MENTION.sub("", line)):
                tok = m.group(1)
                if RE_KNIFE.match(tok) and (tok.startswith("000-") or tok in knives):
                    continue
                kind = "裸刀名（rev6 刀集外）" if RE_KNIFE.match(tok) else "裸 rev5 編號"
                out.append(finding(ERROR, "GT-05", f"{rel}:{i}", f"{kind}「{tok}」——前代引用一律 rev5:／rev4: 前綴（提及形用反引號或「」）"))
    for sub in SUBMODULES:
        if not ctx.exists(os.path.join(sub, ".git")):
            out.append(finding(SKIP, "GT-05", sub, f"GT-05.submodule-absent：{sub} 不在工作樹、碼面裸編號未掃"))
            continue
        rc, stdout = ctx.git_try("grep", "-nE", SUB_SCAN, "HEAD", "--", cwd=os.path.join(ctx.root, sub))
        if rc == 0:
            lines = [l for l in stdout.split("\n") if l]
            for l in lines[:10]:
                out.append(finding(ERROR, "GT-05", f"{sub}/{l.split(':', 1)[-1]}", "子庫碼面裸 rev5 編號（B-NNN／L-NNN）——一律 rev5: 前綴"))
            if len(lines) > 10:
                out.append(finding(ERROR, "GT-05", sub, f"…另 {len(lines) - 10} 處"))
        elif rc not in (0, 1):
            out.append(finding(ERROR, "GT-05", sub, f"子庫 git grep 失敗 rc={rc}（掃描未執行即紅）"))
    return out
