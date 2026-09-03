"""守 RL-0050／RL-0046：配號取 next 後 bump、唯一、單調、永不回收；前代編號一律帶 rev5:／rev4: 前綴、裸刀號禁。

book.py（一）：GT-05 ID 家族（BL／LL／RL 三帳＋ADR 檔名）、現在式面跨代裸編號（提及豁免、rev6 刀集豁免）、兩子庫碼面掃描。
（二）GT-06／GT-11／errata 與（三）GT-10 隨後續 Task 併入本檔。
"""
import os
import re

from . import BACKLOG, BACKLOG_DEFERRED, LESSONS_INDEX, LESSONS_DIR, RULES, ADR_DIR, EVENTS, NOTES, SUBMODULES, CONSTITUTION, COMPOSE_FILES
from .common import ERROR, WARN, SKIP, finding

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


# ---------------------------------------------------------------------------
# （二）GT-06 引用健康／GT-11 bash 面／errata
# ---------------------------------------------------------------------------
FENCE = re.compile(r"```.*?```", re.S)
INLINE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
RE_LINENO = re.compile(r"\S+\.md:\d+")
RE_DEEP = re.compile(r"(BACKLOG(-[A-Za-z0-9-]+)?|NOTES|STATE)\.md#")
RE_HOME = re.compile(r"(~|/home/[^/\s]+|/Users/[^/\s]+)/\.claude/")
TENSE_ERR = ("待決", "TBD", "⏳", "已完成", "下一步")
TENSE_WARN = ("屆時", "日後", "將由")
RE_SHEBANG_SH = re.compile(r"^#!\s*(?:/usr/bin/env\s+)?(?:/bin/|/usr/bin/)?(?:ba)?sh\b")
SHEBANG_OK = ("#!/usr/bin/env bash", "#!/bin/sh", "#!/usr/bin/env sh", "#!/bin/bash")
RE_GLUE = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*[^\x00-\x7f]")


def strip_code(text):
    """剝除 fenced code（保留行數）與行內程式碼——連結／行號／路徑腿不看程式碼內文字（提及原則）。"""
    return INLINE.sub("", FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text or ""))


def gt_06(ctx):
    """GATE:
      id=GT-06
      rule=RL-0048
      source=rev5:ADR 0012
      drift=引用斷鏈、時態混入
      face=tracked *.md；活書家族
      trigger=pre-commit
      rc=1
      breaks-if-removed=死連結與未來式靜默入書
    """
    out = []
    book_seen = False
    for rel in ctx.tracked:
        if not rel.endswith(".md") or face_of(rel) == "fixture":
            continue
        text = ctx.text(rel)
        if text is None:
            continue
        base = os.path.dirname(rel)
        book = is_book(rel)
        book_seen = book_seen or book
        for i, line in enumerate(strip_code(text).split("\n"), 1):
            where = f"{rel}:{i}"
            for m in LINK.finditer(line):
                t = m.group(1)
                if t.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                t = t.split("#", 1)[0]
                if t and not ctx.exists(os.path.normpath(os.path.join(base, t))):
                    out.append(finding(ERROR, "GT-06", where, f"連結目標不存在：{t}（相對於 {base or '.'}）"))
            for m in RE_LINENO.finditer(line):
                out.append(finding(ERROR, "GT-06", where, f"行號形引用「{m.group(0)}」——跨檔引用不用行號（用節名或整檔）"))
            for m in RE_DEEP.finditer(line):
                out.append(finding(ERROR, "GT-06", where, f"帳本 deep-link「{m.group(0)}」——BACKLOG／NOTES／STATE 只可整檔引用"))
            for m in RE_HOME.finditer(line):
                out.append(finding(ERROR, "GT-06", where, f"per-machine 路徑「{m.group(0)}」——repo 文件不引用本機 .claude 路徑"))
            if book:
                for w in TENSE_ERR:
                    if w in line:
                        out.append(finding(ERROR, "GT-06", where, f"活書家族時態禁詞「{w}」（未來式住 ops、過去式住 git＋events）"))
                for w in TENSE_WARN:
                    if w in line:
                        out.append(finding(WARN, "GT-06", where, f"活書家族預告詞「{w}」——預告必標成預告並附回填義務"))
    if not book_seen:
        out.append(finding(SKIP, "GT-06", "docs/arc42", "GT-06.book-absent：活書家族尚無檔（Day-1；波 2 骨架即解除）——連結／行號／路徑腿照跑"))
    return out


def _bash_face(ctx):
    for rel in ctx.tracked:
        if face_of(rel) == "fixture":
            continue
        text = ctx.text(rel)
        if text is None:
            continue
        first = text.split("\n", 1)[0]
        if rel.endswith(".sh") or RE_SHEBANG_SH.match(first):
            yield rel, text, first


def gt_11(ctx):
    """GATE:
      id=GT-11
      rule=RL-0056
      source=rev5:L-001
      drift=bash 黏字與 shebang
      face=外層 tracked bash 面（*.sh ∪ sh shebang；含 deploy/、.githooks/）
      trigger=pre-commit
      rc=1
      breaks-if-removed=macOS bash 3.2 unbound variable 炸在 preflight
    """
    out = []
    n = 0
    for rel, text, first in _bash_face(ctx):
        n += 1
        if first.startswith("#!") and first.strip() not in SHEBANG_OK:
            out.append(finding(ERROR, "GT-11", f"{rel}:1", f"shebang「{first.strip()}」不在白名單 {'／'.join(SHEBANG_OK)}"))
        for i, line in enumerate(text.split("\n"), 1):
            for m in RE_GLUE.finditer(line):
                out.append(finding(ERROR, "GT-11", f"{rel}:{i}", f"$VAR 後緊接非 ASCII「{m.group(0)}」會黏進變數名（bash 3.2）——改 ${{VAR}} 形"))
    if n == 0:
        out.append(finding(ERROR, "GT-11", ".", "掃描面空集合：無 *.sh 亦無 sh shebang 檔——bootstrap／hooks 必須存在"))
    return out


def errata_scan(ctx, keyword):
    """跨檔假述枚舉：外層 tracked 文字檔（大小寫不敏感子串）＋兩子庫 pin 樹 git grep；回 [(rel, lineno, line)]。
    子庫缺席不入本表（CLI 另印「掃描未執行」警示、rc 3——未執行≠零命中）。"""
    kw = keyword.lower()
    hits = []
    for rel in ctx.tracked:
        p = os.path.join(ctx.root, rel)
        try:
            with open(p, "rb") as f:
                if b"\x00" in f.read(8192):
                    continue
        except OSError:
            continue
        text = ctx.text(rel)
        if text is None:
            continue
        for i, line in enumerate(text.split("\n"), 1):
            if kw in line.lower():
                hits.append((rel, i, line))
    for sub in SUBMODULES:
        if not ctx.exists(os.path.join(sub, ".git")):
            continue
        rc, stdout = ctx.git_try("grep", "-n", "-i", "-F", "-e", keyword, "HEAD", "--", cwd=os.path.join(ctx.root, sub))
        if rc == 0:
            for l in stdout.split("\n"):
                if not l:
                    continue
                parts = l.split(":", 3)
                if len(parts) >= 4 and parts[0].startswith("HEAD"):
                    hits.append((f"{sub}/{parts[1]}", int(parts[2]), parts[3]))
    return hits


# ---------------------------------------------------------------------------
# （三）GT-10 文件形制閘（§3.4；Day-1 豁免 GT-10.doc-skeleton-absent）
# ---------------------------------------------------------------------------
FORM_FACE = BOOK_FACE
AIV_KEYS = tuple(f"AIV-1{c}" for c in "abcdefgh") + tuple(f"AIV-2{c}" for c in "abcdefgh") + tuple(f"AIV-{n}" for n in range(3, 10))
E_SUBSECTIONS = {
    "E1": ("AI Components Inventory", "System Boundary Diagram", "Four-Part Boundary Contract", "Failure Modes", "External AI Dependencies"),
    "E2": ("Model Inventory Table", "Per-Model Detail Sections", "Integration with Model Cards", "Integration with Model Registry Tools"),
    "E3": ("Pipeline Overview Diagram", "Pipeline Inventory Table", "Quality Gates", "Feature Store Documentation", "Feedback Loops", "Integration with Data Cards"),
    "E4": ("Responsible AI Concern Matrix", "Fairness", "Explainability", "Human Oversight", "Transparency", "Privacy", "Safety"),
    "E5": ("Model Alternatives Considered", "Dataset Characteristics", "Fairness and Bias Trade-offs", "Expected Model Lifetime", "Retraining Trigger", "Explainability Requirements", "Regulatory Compliance"),
    "E6": ("Quality Attribute Definitions", "Model Freshness", "Drift Tolerance", "Explainability", "Fairness", "Robustness", "Scenario Format", "Cross-Component Scenarios"),
    "E7": ("Boundary Erosion", "Entanglement", "Hidden Feedback Loops", "Data Dependency Debt", "Pipeline Debt", "Configuration Debt", "Model Staleness", "Register Entry Format", "Debt Summary Dashboard", "Review Cadence"),
    "E8": ("Monitoring", "Retraining Policy", "Deployment Strategy", "Rollback Policy", "Incident Response"),
    "C4-E1": ("Stereotype Definitions", "Mermaid Conventions", "Annotation Guidelines", "Template"),
    "C4-E2": ("Data Source Inventory", "Lineage Diagram", "Lineage Details", "Freshness Requirements", "Privacy Flow", "Schema Registry"),
    "C4-E3": ("Boundary Overview", "Boundary Interfaces", "Confidence Thresholds", "Degradation Behavior", "Propagation Rules", "Testing Implications"),
}
NO_AI_SENTENCE = "目前無 AI 元件"
TENSION = "類比張力："
CHECKLIST = "docs/compliance/annex-iv-checklist.md"
C4_L2 = "docs/c4/C4-L2-container.md"
SKELETON_ANCHOR = "docs/arc42/01-introduction-and-goals.md"
# 佔位三腿＋裸方括號：判準以拆分構造寫，避免本檔（現在式面）被規則定義文自撞
RE_PLACEHOLDERS = (
    ("星號佔位", re.compile("\\*" + "\\[")),
    ("底線佔位", re.compile("_" + "{5,}")),
    ("未勾核取佔位", re.compile("- " + "\\[ \\]")),
    ("裸方括號佔位", re.compile("\\[" + "[A-Z][A-Za-z ]+" + "\\]" + "(?!\\()")),
)
RE_TODO_WAVE = re.compile("TODO" + r"\(波\s*(\d+)\)")
RE_WAVE = re.compile(r"^<!--\s*wave:\s*(\d+)\s*-->")
RE_MERMAID = re.compile(r"```mermaid\n(.*?)```", re.S)
RE_NODE = re.compile(r"\b([A-Za-z_][\w-]*)\s*(\[\(|\(\(|\[|\(|\{)\s*\"?([^\]\)\}\"\n]+?)\"?\s*(\)\]|\)\)|\]|\)|\})")
RE_TABLE_ROW = re.compile(r"^\|\s*([^|\n]+?)\s*\|", re.M)
RE_BACKTICK = re.compile(r"`([^`\n]+)`")
RE_H3 = re.compile(r"^###\s+")


def current_wave(ctx):
    """「現在波」唯一真源＝docs/ops/NOTES.md 首行 `<!-- wave: N -->`；缺席→None。"""
    text = ctx.text(NOTES)
    if not text:
        return None
    m = RE_WAVE.match(text.split("\n", 1)[0])
    return int(m.group(1)) if m else None


def compose_services(ctx):
    names = set()
    for rel in COMPOSE_FILES:
        text = ctx.text(rel)
        if text is None:
            continue
        inside = False
        for line in text.split("\n"):
            if line.startswith("services:"):
                inside = True
                continue
            if inside and line and not line.startswith(" "):
                inside = False
            if inside:
                m = re.match(r"^  ([A-Za-z0-9_.-]+):\s*$", line)
                if m:
                    names.add(m.group(1))
    return names


def _clean_cell(s):
    return s.strip().strip("*`★ ").strip()


def _table_first_cells(text):
    cells = set()
    for m in RE_TABLE_ROW.finditer(text):
        c = _clean_cell(m.group(1))
        if c and not set(c) <= set("-: "):
            cells.add(c)
    return cells


def _mermaid_nodes(text):
    """回 {(id, label)}；label 缺席時 label=id。"""
    nodes = set()
    for blk in RE_MERMAID.findall(text):
        for m in RE_NODE.finditer(blk):
            nodes.add((m.group(1), m.group(3).strip()))
    return nodes


def gt_10(ctx):
    """GATE:
      id=GT-10
      rule=RL-0035
      source=ADR-00004
      drift=佔位與樣板文、子項名冊（鍵集＋值↔標題）、圖表對賬
      face=BOOK_FACE（docs/arc42 非 decisions、docs/c4、docs/compliance、docs/process）
      trigger=pre-commit
      rc=1
      breaks-if-removed=RAD-AI 表可空殼交卷（22/22 假滿分重演）
    """
    out = []
    files = [(rel, ctx.text(rel)) for rel in ctx.tracked if rel.endswith(".md") and is_book(rel)]
    files = [(r, t) for r, t in files if t is not None]
    if not files:
        return [finding(SKIP, "GT-10", "docs/arc42", f"GT-10.doc-skeleton-absent：活書家族尚無檔（Day-1；{SKELETON_ANCHOR} 存在即解除）")]
    wave = current_wave(ctx)
    if wave is None:
        out.append(finding(ERROR, "GT-10", NOTES, "波標記缺席：docs/ops/NOTES.md 首行須為 <!-- wave: N -->（現在波唯一真源）"))
    for rel, text in files:
        from .common import parse_front_matter
        meta, body = parse_front_matter(text)
        stripped = strip_code(body)
        for i, line in enumerate(stripped.split("\n"), 1):
            for name, rx in RE_PLACEHOLDERS:
                for m in rx.finditer(line):
                    out.append(finding(ERROR, "GT-10", f"{rel}:{i}", f"{name}「{m.group(0)}」——模板是起手結構不是表單：無實體即一句「目前無」附理由"))
            for m in RE_TODO_WAVE.finditer(line):
                k = int(m.group(1))
                if wave is not None and k < wave:
                    out.append(finding(ERROR, "GT-10", f"{rel}:{i}", f"TODO(波 {k}) 已到期（現在波 {wave}；波 {k} 出口＝該標記歸零）"))
        if rel.startswith("docs/process/"):
            lines = body.split("\n")
            for i, line in enumerate(lines):
                if RE_H3.match(line):
                    nxt = next((l for l in lines[i + 1:] if l.strip()), "")
                    if TENSION not in nxt:
                        out.append(finding(ERROR, "GT-10", f"{rel}:{i + 1}", f"流程層子節「{line.strip()}」首句缺「{TENSION}」"))
        rad = meta.get("rad_ai")
        if isinstance(rad, list) and NO_AI_SENTENCE not in body:
            keys = set(meta.get("rad_ai_map", {}).keys()) if isinstance(meta.get("rad_ai_map"), dict) else set()
            for e in rad:
                need = set(E_SUBSECTIONS.get(e, ()))
                missing = sorted(need - keys)
                if missing:
                    out.append(finding(ERROR, "GT-10", rel, f"{e} 子項名冊缺：{'、'.join(missing)}（frontmatter rad_ai_map 鍵集須 ⊇ reference 子節）"))
        amap = meta.get("rad_ai_map")
        if isinstance(amap, dict):  # 第八腿（波 2 grill Q4）：map 值＝同檔 ### 標題字面；反向不要求、多鍵同值合法
            h3 = {RE_H3.sub("", l).strip() for l in stripped.split("\n") if RE_H3.match(l)}
            for k, v in amap.items():
                if v not in h3:
                    out.append(finding(ERROR, "GT-10", rel, f"map 值「{v}」無對應 ### 標題（鍵 {k}；rad_ai_map 值＝同檔 ### 標題字面）"))
        nodes = _mermaid_nodes(text)
        if nodes:
            cells = _table_first_cells(text)
            for nid, label in sorted(nodes):
                if label not in cells and nid not in cells:
                    out.append(finding(ERROR, "GT-10", rel, f"圖內節點「{label}」不在同檔表格首欄（圖表對賬：節點 ⊆ 表列）"))
    tracked = {r for r, _ in files}
    if CHECKLIST in tracked:
        text = ctx.text(CHECKLIST)
        rows = {}
        for line in text.split("\n"):
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            key = _clean_cell(cells[0]) if cells else ""
            if key.startswith("AIV-"):
                rows[key] = cells
        for k in AIV_KEYS:
            if k not in rows:
                out.append(finding(ERROR, "GT-10", CHECKLIST, f"Annex IV 檢核表缺鍵 {k}（23 鍵齊全＝附錄 G）"))
        for k, cells in rows.items():
            ev = cells[5] if len(cells) > 5 else ""
            if not ev or ev in ("—", "-", "TBD") or any(rx.search(ev) for _, rx in RE_PLACEHOLDERS):
                out.append(finding(ERROR, "GT-10", f"{CHECKLIST}｜{k}", "Evidence 欄佔位——填「See `<檔>`, `<具名表>` — …」或「不適用：<理由>」"))
                continue
            if ev.startswith("不適用"):
                if len(ev) < 5:
                    out.append(finding(ERROR, "GT-10", f"{CHECKLIST}｜{k}", "Evidence「不適用」須附理由"))
                continue
            refs = RE_BACKTICK.findall(ev)
            if not refs:
                out.append(finding(ERROR, "GT-10", f"{CHECKLIST}｜{k}", "Evidence 欄未引 `<檔>`（反引號路徑）"))
                continue
            target = refs[0]
            if not ctx.exists(target):
                out.append(finding(ERROR, "GT-10", f"{CHECKLIST}｜{k}", f"Evidence 所引檔不存在：{target}"))
                continue
            if len(refs) > 1 and refs[1] not in (ctx.text(target) or ""):
                out.append(finding(ERROR, "GT-10", f"{CHECKLIST}｜{k}", f"Evidence 具名表「{refs[1]}」標題字面未命中 {target}"))
    services = compose_services(ctx)
    if any(r.startswith("docs/c4/") for r in tracked):
        if C4_L2 not in tracked:
            out.append(finding(ERROR, "GT-10", C4_L2, "C4-L2 缺席：docs/c4/ 已有檔但 C4-L2-container.md 不存在（compose 服務對賬無面）"))
        elif not services:
            out.append(finding(ERROR, "GT-10", C4_L2, "compose 三檔無 services（掃描面空集合、對賬未執行）"))
        else:
            nodes = _mermaid_nodes(ctx.text(C4_L2))
            names = {n for pair in nodes for n in pair} | {n.replace("_", "-") for pair in nodes for n in pair}
            missing = sorted(services - names)
            if missing:
                out.append(finding(ERROR, "GT-10", C4_L2, f"C4-L2 節點缺 compose 服務：{'、'.join(missing)}（節點 ⊇ compose 三檔 services）"))
    return out
