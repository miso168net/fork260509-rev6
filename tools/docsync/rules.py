"""守 RL-0049／RL-0052：RULES 為規則層唯一家；數量預算只擋新增。

rules.py：解析 docs/ops/RULES.md、依 scope 輸出規則塊（含 RULES-VERSION）、emit_js 產編排骨架的三區塊、GT-08 RULES 側三腿。
"""
import hashlib
import os
import re

from . import RULES, ADR_DIR
from .common import ERROR, finding

RE_NEXT = re.compile(r"<!--\s*next:\s*RL-(\d{4})\s*-->")
RE_CAPS = re.compile(r"上限[^：]*：([^\n]+)")
RE_ROW = re.compile(
    r"^\|\s*(RL-\d{4})\s*\|\s*(.+?)\s*\|\s*([^|]+?)\s*\|\s*(prompt|lint|checklist)\s*\|\s*([^|]+?)\s*\|\s*$",
    re.M,
)
RE_SOURCE = re.compile(r"^(LL-\d{5}|ADR-\d{5}|rev5:L-\d{3}|rev5:ADR \d{4})$")
SCOPES = ("implementer", "review", "fix", "主線", "人")


class Rule:
    def __init__(self, id, rule, scopes, carrier, source):
        self.id, self.rule, self.scopes, self.carrier, self.source = id, rule, scopes, carrier, source


def parse_rules(text):
    """回 (header, rows)；header={"next": int|None, "caps": {名: 上限}}。表列錨＝以 `| RL-` 起的行。"""
    hdr = {"next": None, "caps": {}}
    m = RE_NEXT.search(text or "")
    if m:
        hdr["next"] = int(m.group(1))
    c = RE_CAPS.search(text or "")
    if c:
        for part in re.split(r"[｜|]", c.group(1)):
            mm = re.match(r"\s*(\S+?)\s*(\d+)(?!\d)", part)  # 數字後允許「。」與後綴句、不吃掉末項
            if mm:
                hdr["caps"][mm.group(1)] = int(mm.group(2))
    rows = [
        Rule(g[0], g[1], {s.strip() for s in g[2].split(",") if s.strip()}, g[3], g[4].strip())
        for g in RE_ROW.findall(text or "")
    ]
    return hdr, rows


def _canonical(rows):
    return "\n".join(
        f"{r.id}|{r.rule}|{','.join(sorted(r.scopes))}|{r.carrier}|{r.source}"
        for r in sorted(rows, key=lambda r: r.id)
    )


def rules_version(text):
    """規則表的內容指紋（sha256 前 12 hex）；欄位任一字改動即變、與空白／排序無關。"""
    return hashlib.sha256(_canonical(parse_rules(text)[1]).encode("utf-8")).hexdigest()[:12]


def emit(text, scope):
    _, rows = parse_rules(text)
    ver = rules_version(text)
    sel = [r for r in rows if scope in r.scopes]
    body = "\n".join(f"{r.id}｜{r.rule}" for r in sel)
    return f"=== RULES scope={scope}（{len(sel)} 條）===\n{body}\nRULES-VERSION: {ver}\n"


def _js_str(block):
    return block.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def emit_js(text):
    head = "// 機器生成：python3 tools/docsync generate（自 docs/ops/RULES.md 之 rules emit）——嚴禁手改；差異由 pre-commit check 攔下\n"
    return head + "".join(
        f"const {name} = `{_js_str(emit(text, scope))}`;\n"
        for name, scope in (("RULES", "implementer"), ("RULES_REVIEW", "review"), ("RULES_FIX", "fix"))
    )


def _adr_file_exists(ctx, adr_id):
    """兩腿：先試 exists 樁（測試以 `<id>-x.md` 樁替代目錄掃描），再落真目錄掃描。"""
    if ctx.exists(f"{ADR_DIR}/{adr_id}-x.md"):
        return True
    d = os.path.join(ctx.root, ADR_DIR)
    return os.path.isdir(d) and any(n.startswith(adr_id + "-") for n in os.listdir(d))


def gt_08(ctx):
    """GATE:
      id=GT-08
      rule=RL-0049
      source=rev5:ADR 0024
      drift=RULES↔LESSONS 對賬
      face=docs/ops/RULES.md；docs/ops/LESSONS/*.md；docs/ops/LESSONS.md
      trigger=pre-commit
      rc=1
      breaks-if-removed=規則層可無來源、可超上限、教訓可不指向規則
    """
    out = []
    text = ctx.text(RULES)
    if not text:
        return [finding(ERROR, "GT-08", RULES, "掃描面空集合：RULES.md 缺席或空檔——規則層首版必須存在")]
    hdr, rows = parse_rules(text)
    if hdr["next"] is None:
        out.append(finding(ERROR, "GT-08", RULES, "缺 next-id 檔頭（<!-- next: RL-NNNN -->）"))
    if not rows:
        out.append(finding(ERROR, "GT-08", RULES, "掃描面空集合：零規則列"))
    for r in rows:
        where = f"{RULES}｜{r.id}"
        if not RE_SOURCE.match(r.source):
            out.append(finding(ERROR, "GT-08", where, f"source 形制不合「{r.source}」（LL-NNNNN／ADR-NNNNN／rev5:L-NNN／rev5:ADR 00NN）"))
        elif r.source.startswith("ADR-") and not any(p.startswith(f"{ADR_DIR}/{r.source}-") for p in ctx.tracked) and not _adr_file_exists(ctx, r.source):
            out.append(finding(ERROR, "GT-08", where, f"source 指向不存在的 {r.source}"))
        extra = r.scopes - set(SCOPES)
        if extra:
            out.append(finding(ERROR, "GT-08", where, f"scope 值域外：{sorted(extra)}"))
        if len(r.rule.splitlines()) > 2:
            out.append(finding(ERROR, "GT-08", where, "規則句超過 2 行"))
    return out


def budget_counts(text):
    """給 gates.gt_12 的計數（數量預算由 GT-12 統一定級與回報；本閘不報上限）。回 ({"總": n, <scope>: n…}, caps)。"""
    hdr, rows = parse_rules(text or "")
    counts = {"總": len(rows)}
    counts.update({s: sum(1 for r in rows if s in r.scopes) for s in SCOPES})
    return counts, hdr["caps"]
