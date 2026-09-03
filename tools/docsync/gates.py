"""守 RL-0051／RL-0052／RL-0054／RL-0057：閘名冊同源、Day-1 豁免到期即紅、機密永不入版控、README／hook／exec bit 對賬。

gates.py：ROSTER（恰 12 閘）、parse_gate_blocks／derive_anchor_codes（兩層真源）、DAY1_EXEMPTIONS（四欄制）、
gt_01（generated 零漂移）、gt_07（機密樣式＋值比對）、gt_09（README 樹／EXEC_REQUIRED／settings.json 接線）、
gt_12（名冊同源三處＋數量預算＋波標記）、run_lint、gen_gates_md。
"""
import importlib.util
import json
import os
import re

from . import RULES, NOTES, BACKLOG, LESSONS_INDEX, LESSONS_DIR, EVENTS
from .common import ERROR, WARN, SKIP, Day1Exemption, GENERATED_HEADER, GitError, finding
from . import events as ev_mod
from . import adr as adr_mod
from . import book as book_mod
from . import rules as rules_mod
from . import references as ref_mod

GATE_KEYS = ("id", "rule", "source", "drift", "face", "trigger", "rc", "breaks-if-removed")
RE_GATE_BLOCK = re.compile(r"GATE:\n((?:[ \t]+[a-z-]+=[^\n]*\n)+)")
RE_ANCHOR = re.compile(r'finding\(\s*(?:ERROR|WARN|SKIP)\s*,\s*"(GT-\d{2})"')
RE_GT_ID = re.compile(r"GT-(\d{2})")
RE_GT_RANGE = re.compile(r"GT-(\d{2})\s*[～~]\s*GT-(\d{2})")
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
GATES_MD = "docs/generated/GATES.md"
PRECOMMIT = ".githooks/pre-commit"
RUNBOOK = "docs/ops/RUNBOOK.md"
README = "README.md"
SETTINGS = ".claude/settings.json"
HOOKS_DIR = ".claude/hooks"
ROSTER_PREFIXES = ("tools/", "deploy/", ".githooks/", ".claude/")
EXEC_REQUIRED = (".githooks/pre-commit", ".githooks/pre-push", ".githooks-submodule/pre-commit", ".githooks-submodule/pre-push",
                 "deploy/sops.sh", "deploy/generate-age-key.sh", "deploy/generate-dev-cert.sh", "tools/bootstrap.sh")
BUDGET_GATES, BUDGET_BACKLOG_OPEN, BUDGET_ERROR_WAVE = 12, 25, 6
MIN_SECRET_LEN = 8
PLACEHOLDER_LITERALS = frozenset({"https://CHANGE-ME.invalid/alert-webhook-placeholder"})  # 與 deploy/preflight-secrets.py 雙記帳（rev5:ADR 0003）
# 機密樣式四組（S1 補強面；主防線＝betterleaks；樣本於自測執行期串接、不落字面）
SECRET_PATTERNS = (
    ("私鑰 PEM 檔頭", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY(?: BLOCK)?-----")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("DSN 內嵌密碼", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:(?![$<{])[^/\s@]{8,}@")),
    ("金鑰指派字面", re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\"']?(?![$<{])[A-Za-z0-9+/=_-]{20,}[\"']?")),
)


# ---------------------------------------------------------------------------
# 名冊兩層真源
# ---------------------------------------------------------------------------
def package_sources():
    """本 package 邏輯原始碼（不含 tests/）：{rel: text}。"""
    out = {}
    for n in sorted(os.listdir(PACKAGE_DIR)):
        if n.endswith(".py"):
            with open(os.path.join(PACKAGE_DIR, n), encoding="utf-8") as f:
                out[f"tools/docsync/{n}"] = f.read()
    return out


def parse_gate_blocks(source_text):
    """docstring 固定鍵值區塊 → {id: {key: value}}。"""
    blocks = {}
    for m in RE_GATE_BLOCK.finditer(source_text or ""):
        kv = {}
        for line in m.group(1).splitlines():
            k, v = line.strip().split("=", 1)
            kv[k.strip()] = v.strip()
        if "id" in kv:
            blocks[kv["id"]] = kv
    return blocks


def derive_anchor_codes(source_text):
    return set(RE_ANCHOR.findall(source_text or ""))


def gate_id(fn):
    return parse_gate_blocks(fn.__doc__ or "").get(next(iter(parse_gate_blocks(fn.__doc__ or "")), ""), {}).get("id") if fn.__doc__ else None


# ---------------------------------------------------------------------------
# Day-1 具名豁免（§4.6 四欄：鍵→理由、解除謂詞、到期即紅、登記日）
# ---------------------------------------------------------------------------
def _has_close_events(ctx):
    evs, _ = ev_mod.parse_events(ctx.text(EVENTS))
    return any(e.get("type") in ("feature_close", "review") for e in evs)


DAY1_EXEMPTIONS = {
    "GT-03.no-close-events": Day1Exemption("GT-03.no-close-events", "波 1 尚無 feature_close／review 事件", _has_close_events, "2026-09-03"),
    "GT-05.ledgers-absent": Day1Exemption("GT-05.ledgers-absent", "BACKLOG／LESSONS 帳本波 2 才建空檔", lambda ctx: ctx.exists(BACKLOG) and ctx.exists(LESSONS_INDEX), "2026-09-03"),
    "GT-06.book-absent": Day1Exemption("GT-06.book-absent", "活書家族波 2 骨架才落地", lambda ctx: any(book_mod.is_book(r) for r in ctx.tracked), "2026-09-03"),
    "GT-08.lessons-absent": Day1Exemption("GT-08.lessons-absent", "首條 LL 教訓尚未落地", lambda ctx: ctx.exists(LESSONS_DIR), "2026-09-03"),
    "GT-10.doc-skeleton-absent": Day1Exemption("GT-10.doc-skeleton-absent", "活書骨架波 2 才落地", lambda ctx: ctx.exists(book_mod.SKELETON_ANCHOR), "2026-09-03"),
}


# ---------------------------------------------------------------------------
# GT-01
# ---------------------------------------------------------------------------
def gt_01(ctx):
    """GATE:
      id=GT-01
      rule=RL-0049
      source=rev5:ADR 0052
      drift=generated↔真源
      face=GENERATED_FILES（docs/generated/**＋tools/orchestration/_sk_rules.js）
      trigger=pre-commit
      rc=1
      breaks-if-removed=鏡像可手改、生成檔與真源靜默分叉
    """
    return ref_mod.check_generated(ctx, ref_mod.compute_generated(ctx))


# ---------------------------------------------------------------------------
# GT-07
# ---------------------------------------------------------------------------
def _resolve_secrets_dir(ctx):
    """三級口徑：env SECRETS_DIR（此處直判、與共用庫第一級同義）→ .env 一行（共用庫嚴格解析）→ deploy/secrets。"""
    val = os.environ.get("SECRETS_DIR")
    if val:
        return (val if os.path.isabs(val) else os.path.join(ctx.root, val)), None
    path = os.path.join(ctx.root, "deploy", "secrets_common.py")
    if not os.path.isfile(path):
        return None, "deploy/secrets_common.py 缺席（落點解析共用庫）"
    spec = importlib.util.spec_from_file_location("_rv6_secrets_common", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.resolve_secrets_dir(ctx.root)


def _selftest_patterns():
    """紅綠樣本執行期串接：每組樣式必中紅樣本、不中綠樣本；回錯誤訊息 list。"""
    red = {
        "私鑰 PEM 檔頭": "-----BEGIN " + "RSA PRIVATE KEY" + "-----",
        "AWS access key id": "AKIA" + "ABCDEFGHIJKLMNOP",
        "DSN 內嵌密碼": "postgres://app:" + "Pa55w0rdXYZ12" + "@db:5432/x",
        "金鑰指派字面": "password" + "=" + "Qm9ndXNWYWx1ZUZvclRlc3RpbmcxMjM",
    }
    green = ["postgres://app:${POSTGRES_PASSWORD}@db:5432/x", "password=${PW}", "SECRET_KEY: <填入>", "-----BEGIN CERTIFICATE-----", "AKIA short"]
    errs = []
    for name, rx in SECRET_PATTERNS:
        if not rx.search(red[name]):
            errs.append(f"樣式「{name}」自測紅樣本未命中（閘恆綠）")
        for g in green:
            if rx.search(g):
                errs.append(f"樣式「{name}」自測綠樣本誤中：{g}")
    return errs


def gt_07(ctx):
    """GATE:
      id=GT-07
      rule=RL-0054
      source=rev5:ADR 0003
      drift=機密入版控
      face=tracked 文字檔＋SECRETS_DIR 實值
      trigger=pre-commit
      rc=1
      breaks-if-removed=機密實值或樣式進 git 歷史、不可逆
    """
    out = [finding(ERROR, "GT-07", "tools/docsync/gates.py", m) for m in _selftest_patterns()]
    texts = []
    for rel in ctx.tracked:
        p = os.path.join(ctx.root, rel)
        try:
            with open(p, "rb") as f:
                if b"\x00" in f.read(8192):
                    continue
        except OSError:
            continue
        t = ctx.text(rel)
        if t is not None:
            texts.append((rel, t))
    for rel, text in texts:
        for i, line in enumerate(text.split("\n"), 1):
            for name, rx in SECRET_PATTERNS:
                if rx.search(line):
                    out.append(finding(ERROR, "GT-07", f"{rel}:{i}", f"機密樣式「{name}」命中（值不印；合成樣本一律執行期串接）"))
    sdir, err = _resolve_secrets_dir(ctx)
    if err:
        return out + [finding(ERROR, "GT-07", ".env", f"SECRETS_DIR 解析失敗：{err}")]
    if not os.path.isdir(sdir):
        return out + [finding(SKIP, "GT-07", sdir, "GT-07.secrets-absent：機密落點缺席、值比對未執行（樣式面已掃）")]
    secrets = {}
    for n in sorted(os.listdir(sdir)):
        if not n.endswith(".txt") or not os.path.isfile(os.path.join(sdir, n)):
            continue
        with open(os.path.join(sdir, n), encoding="utf-8", errors="replace") as f:
            v = f.read().rstrip("\r\n")
        if v.startswith("CHANGE-ME") or v in PLACEHOLDER_LITERALS or len(v) < MIN_SECRET_LEN or "\n" in v:
            continue
        secrets[n[:-4]] = v
    for rel, text in texts:
        for name, v in secrets.items():
            if v in text:
                out.append(finding(ERROR, "GT-07", rel, f"機密現值「{name}」出現於 tracked 檔（值不印）——立即撤換該機密、絕不只刪字面"))
    return out


# ---------------------------------------------------------------------------
# GT-09
# ---------------------------------------------------------------------------
RE_TREE_LINE = re.compile(r"^((?:[│ ]   |    )*)(?:├──|└──)\s+(\S+)")


def readme_tree_paths(text):
    """README text 樹 → (宣告路徑集, 葉目錄集)；目錄以 / 結尾、深度以 4 字元縮排推、「、」分隔多檔逐一拆。
    葉目錄（樹中未展開子項者）概括覆蓋其下全部 tracked 檔；已展開子項的目錄不概括。"""
    paths, parents, stack = set(), set(), []
    for blk in re.findall(r"```text\n(.*?)```", text or "", re.S):
        stack = []
        for line in blk.splitlines():
            m = RE_TREE_LINE.match(line)
            if not m:
                continue
            depth = len(m.group(1)) // 4
            stack = stack[:depth]
            if stack:
                parents.add("/".join(stack) + "/")
            for tok in m.group(2).split("、"):
                full = "/".join(stack + [tok.rstrip("/")]) + ("/" if tok.endswith("/") else "")
                paths.add(full)
            stack.append(m.group(2).split("、")[0].rstrip("/"))
    leaf_dirs = {d for d in paths if d.endswith("/") and d not in parents}
    return paths, leaf_dirs


def _covered(rel, declared, leaf_dirs):
    if rel in declared:
        return True
    return any(rel.startswith(d) for d in leaf_dirs)


def gt_09(ctx):
    """GATE:
      id=GT-09
      rule=RL-0057
      source=rev5:L-061
      drift=接線與實檔集
      face=README 樹、tools/deploy/.githooks/.claude、settings.json、EXEC_REQUIRED
      trigger=pre-commit
      rc=1
      breaks-if-removed=hook 被 pnpm install 覆寫或失去 exec bit 而靜默失效、README 地圖與實檔分叉
    """
    out = []
    tracked = set(ctx.tracked)
    readme = ctx.text(README)
    if readme is None:
        out.append(finding(SKIP, "GT-09", README, "GT-09.readme-absent：README 文件地圖尚未建（Day-1；波 1 Task 13 即解除）"))
    else:
        declared, leaf_dirs = readme_tree_paths(readme)
        for d in sorted(declared):
            if not d.endswith("/") and d.startswith(ROSTER_PREFIXES) and d not in tracked:
                out.append(finding(ERROR, "GT-09", README, f"README 樹列 {d} 但非 tracked 檔（地圖與實檔分叉）"))
            if d.endswith("/") and d.startswith(ROSTER_PREFIXES) and not any(r.startswith(d) for r in tracked):
                out.append(finding(ERROR, "GT-09", README, f"README 樹列目錄 {d} 但無 tracked 檔"))
        for rel in sorted(tracked):
            if rel.startswith(ROSTER_PREFIXES) and not _covered(rel, declared, leaf_dirs):
                out.append(finding(ERROR, "GT-09", rel, "tracked 檔未列於 README 樹（列檔、或列其目錄且不展開子項）"))
    hooks_absent = not ctx.exists(PRECOMMIT)
    if hooks_absent:
        out.append(finding(SKIP, "GT-09", ".githooks", "GT-09.hooks-absent：.githooks 尚未落地（Day-1；波 1 Task 11 即解除）——其餘 EXEC_REQUIRED 照驗"))
    for rel in EXEC_REQUIRED:
        if rel not in tracked:
            if not (hooks_absent and rel.startswith(".githooks")):
                out.append(finding(ERROR, "GT-09", rel, "EXEC_REQUIRED 名冊檔缺席"))
            continue
        try:
            mode = ctx.git("ls-files", "-s", rel).split()[0]
        except (GitError, IndexError):
            mode = "?"
        if mode != "100755":
            out.append(finding(ERROR, "GT-09", rel, f"index mode {mode} ≠ 100755（git update-index --chmod=+x）"))
    settings = ctx.text(SETTINGS)
    if settings is None:
        out.append(finding(ERROR, "GT-09", SETTINGS, "settings.json 缺席（三支 hook 接線無面）"))
        return out
    try:
        cfg = json.loads(settings)
    except ValueError as ex:
        return out + [finding(ERROR, "GT-09", SETTINGS, f"settings.json 非合法 JSON：{ex}")]
    referenced = set()
    for _event, entries in (cfg.get("hooks") or {}).items():
        for entry in entries:
            for h in entry.get("hooks", []):
                for tok in re.findall(r"\.claude/hooks/\S+", h.get("command", "")):
                    referenced.add(tok)
                    if tok not in tracked:
                        out.append(finding(ERROR, "GT-09", SETTINGS, f"hook 命令指向不存在的 {tok}"))
    for rel in sorted(r for r in tracked if r.startswith(HOOKS_DIR + "/")):
        if rel not in referenced:
            out.append(finding(ERROR, "GT-09", rel, "hook 檔未被 settings.json 任一命令引用（孤兒）"))
    return out


# ---------------------------------------------------------------------------
# GT-12
# ---------------------------------------------------------------------------
def _gt_ids_in(text):
    ids = set(f"GT-{n}" for n in RE_GT_ID.findall(text or ""))
    for a, b in RE_GT_RANGE.findall(text or ""):
        ids |= {f"GT-{i:02d}" for i in range(int(a), int(b) + 1)}
    return ids


def gt_12(ctx, extra_sources=None):
    """GATE:
      id=GT-12
      rule=RL-0052
      source=rev5:ADR 0024
      drift=名冊同源與數量預算
      face=tools/docsync/*.py、GATES.md、pre-commit 檔頭、RUNBOOK、NOTES 波標記
      trigger=pre-commit
      rc=1
      breaks-if-removed=閘可無語意區塊、名冊三處分叉、預算超限靜默
    """
    out = []
    sources = package_sources()
    if extra_sources:
        sources.update(extra_sources)
    joined = "\n".join(sources.values())
    blocks = parse_gate_blocks(joined)
    anchors = derive_anchor_codes(joined)
    roster_ids = {gate_id(g) for g in ROSTER}
    for gid in sorted(anchors - set(blocks)):
        out.append(finding(ERROR, "GT-12", "tools/docsync", f"錨形 {gid} 不在 docstring GATE 區塊集合（閘存在但無語意欄）"))
    for gid, b in blocks.items():
        missing = [k for k in GATE_KEYS if k not in b]
        if missing:
            out.append(finding(ERROR, "GT-12", "tools/docsync", f"{gid} GATE 區塊缺鍵：{'、'.join(missing)}"))
    if set(blocks) != roster_ids or len(roster_ids) != BUDGET_GATES:
        out.append(finding(ERROR, "GT-12", "tools/docsync", f"區塊集合 {sorted(blocks)} ≠ ROSTER {sorted(roster_ids)} 或閘數 ≠ {BUDGET_GATES}"))
    gates_md = ctx.text(GATES_MD)
    if gates_md is not None:
        ids = set(re.findall(r"^\| (GT-\d{2}) \|", gates_md, re.M))
        if ids != roster_ids:
            out.append(finding(ERROR, "GT-12", GATES_MD, f"GATES.md 閘集合 {sorted(ids)} ≠ ROSTER（跑 generate）"))
    pre = ctx.text(PRECOMMIT)
    if pre is None:
        out.append(finding(SKIP, "GT-12", PRECOMMIT, "GT-12.precommit-absent：pre-commit 尚未落地（Day-1；波 1 Task 11 即解除）"))
    else:
        head = "\n".join(pre.split("\n")[:20])
        m = RE_GT_RANGE.search(head)
        ids = {f"GT-{i:02d}" for i in range(int(m.group(1)), int(m.group(2)) + 1)} if m else set()
        if ids != roster_ids:
            out.append(finding(ERROR, "GT-12", PRECOMMIT, f"pre-commit 檔頭範圍字串 {'缺席' if not m else m.group(0)} ≠ ROSTER（GT-01～GT-{BUDGET_GATES}）"))
    rb = ctx.text(RUNBOOK)
    if rb is None:
        out.append(finding(SKIP, "GT-12", RUNBOOK, "GT-12.runbook-absent：RUNBOOK 尚未建（Day-1；波 2 即解除）"))
    elif _gt_ids_in(rb) != roster_ids:
        out.append(finding(ERROR, "GT-12", RUNBOOK, f"RUNBOOK 工具表閘集合 {sorted(_gt_ids_in(rb))} ≠ ROSTER"))
    wave = book_mod.current_wave(ctx)
    if wave is None:
        out.append(finding(ERROR, "GT-12", NOTES, "波標記缺席：docs/ops/NOTES.md 首行須為 <!-- wave: N -->"))
    level = ERROR if (wave or 0) >= BUDGET_ERROR_WAVE else WARN
    if wave is not None and wave < BUDGET_ERROR_WAVE:
        knives = {r.split("/")[1] for r in ctx.tracked if r.startswith("specs/") and r.count("/") >= 2 and re.match(r"\d{3}-", r.split("/")[1])}
        if knives:
            out.append(finding(ERROR, "GT-12", NOTES, f"波標記落後：specs/ 已有刀目錄 {sorted(knives)} 而現在波 {wave} < {BUDGET_ERROR_WAVE}（波次出口須 bump 標記）"))
    if len(roster_ids) > BUDGET_GATES:
        out.append(finding(level, "GT-12", "tools/docsync", f"閘數 {len(roster_ids)} 超上限 {BUDGET_GATES}（一進一出）"))
    counts, caps = rules_mod.budget_counts(ctx.text(RULES) or "")
    for k, n in counts.items():
        cap = caps.get(k)
        if isinstance(cap, int) and n > cap:
            out.append(finding(level, "GT-12", RULES, f"RULES {k} {n} 超上限 {cap}（超限只擋新增、不可調數字；改上限＝supersede ADR-00004）"))
    bl = ctx.text(BACKLOG)
    if bl is not None:
        n_open = len(book_mod.RE_ENTRY["BL"].findall(bl))
        if n_open > BUDGET_BACKLOG_OPEN:
            out.append(finding(level, "GT-12", BACKLOG, f"BACKLOG 開放 {n_open} 超上限 {BUDGET_BACKLOG_OPEN}"))
    return out


ROSTER = (gt_01, ev_mod.gt_02, ev_mod.gt_03, adr_mod.gt_04, book_mod.gt_05, book_mod.gt_06, gt_07, rules_mod.gt_08, gt_09, book_mod.gt_10, book_mod.gt_11, gt_12)


# ---------------------------------------------------------------------------
# lint 入口與名冊生成
# ---------------------------------------------------------------------------
def run_lint(ctx):
    """跑 ROSTER 全部＋Day-1 到期斷言＋未登記 SKIP 鍵警告；回 (findings, 末行)。"""
    findings = []
    for g in ROSTER:
        findings += g(ctx)
    for key, ex in DAY1_EXEMPTIONS.items():
        if ex.released(ctx):
            findings.append(finding(ERROR, "GT-12", "tools/docsync/gates.py", f"Day-1 豁免 {key} 已到期（解除謂詞成立、登記 {ex.registered}）——自 DAY1_EXEMPTIONS 移除"))
    for f in list(findings):
        if f[0] == SKIP:
            key = f[3].split("：", 1)[0]
            if key not in DAY1_EXEMPTIONS:
                findings.append(finding(WARN, "GT-12", f[2], f"未登記的 SKIP 鍵 {key}（環境型跳過；非 Day-1 豁免）"))
    n_err = sum(1 for f in findings if f[0] == ERROR)
    n_warn = sum(1 for f in findings if f[0] == WARN)
    n_skip = sum(1 for f in findings if f[0] == SKIP)
    return findings, f"lint：{n_err} 錯誤／{n_warn} 警告／{n_skip} 閘跳過"


def gen_gates_md(ctx):
    blocks = parse_gate_blocks("\n".join(package_sources().values()))
    lines = [GENERATED_HEADER, "# GATES — 閘名冊（§4.1）", "",
             f"閘數 {len(ROSTER)}／上限 {BUDGET_GATES}（一進一出）。真源兩層：存在＝原始碼 finding 錨形、語意＝docstring GATE 區塊（GT-12 斷言錨形 ⊆ 區塊、三處名冊同源）。"
             f"Day-1 豁免 {len(DAY1_EXEMPTIONS)} 筆（§4.6；到期即紅）。", "",
             "| 閘 | 守哪條 RULES／ADR | 監測哪一面的漂移 | 真源 | 掃描面 | 觸發時機 | 紅時 rc | Day-1 豁免狀態 | 拿掉會壞什麼 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for g in ROSTER:
        gid = gate_id(g)
        b = blocks.get(gid, {})
        pending = [k for k, ex in DAY1_EXEMPTIONS.items() if k.startswith(gid + ".") and not ex.released(ctx)]
        status = "未解除：" + "、".join(pending) if pending else "—"
        lines.append(f"| {gid} | {b.get('rule', '')} | {b.get('drift', '')} | {b.get('source', '')} | {b.get('face', '')} | {b.get('trigger', '')} | {b.get('rc', '')} | {status} | {b.get('breaks-if-removed', '')} |")
    lines += ["", "## Day-1 豁免登記（鍵｜理由｜解除謂詞｜登記日）", "", "| 鍵 | 理由 | 解除謂詞 | 登記日 |", "|---|---|---|---|"]
    for k, ex in DAY1_EXEMPTIONS.items():
        lines.append(f"| {k} | {ex.reason} | 檔／事件存在（見 gates.py） | {ex.registered} |")
    return "\n".join(lines) + "\n"
