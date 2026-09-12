"""守 RL-0051／RL-0052／RL-0054／RL-0057：閘名冊同源、Day-1 豁免到期即紅、機密永不入版控、README／hook／exec bit 對賬。

gates.py：ROSTER（恰 12 閘）、parse_gate_blocks／derive_anchor_codes（兩層真源）、DAY1_EXEMPTIONS（四欄制）、
gt_01（generated 零漂移）、gt_07（機密樣式＋值比對）、gt_09（README 樹／EXEC_REQUIRED／settings.json 接線）、
gt_12（名冊同源三處＋碼面閘表＋數量預算＋波標記＋SKIP 鍵登記＋主張對賬）、ENV_SKIPS（ADR-00019 環境型跳過登記）、
registered_skip_keys／skip_key_of（登記集合與鍵抽取的單一權威、靜態面與執行期面同取）、run_lint、gen_gates_md。
"""
import importlib.util
import json
import os
import re

from . import RULES, NOTES, LESSONS_INDEX, LESSONS_DIR, CONSTITUTION
from .common import ERROR, WARN, SKIP, Day1Exemption, GENERATED_HEADER, GitError, finding
from . import events as ev_mod
from . import adr as adr_mod
from . import book as book_mod
from . import rules as rules_mod
from . import references as ref_mod

GATE_KEYS = ("id", "rule", "source", "drift", "face", "trigger", "rc", "breaks-if-removed")
# ★kv 行的行首空白量必須從寬（`*` 而非 `+`）：同一個 regex 吃兩種輸入——原始碼文字（區塊縮排在）
# 與 `fn.__doc__`（Python ≥3.13 於編譯期剝掉 docstring 共同縮排、gh-81283）。收緊成 `+` 會讓
# gate_id() 在 3.13+ 全回 None：GATES.md 算成空表、GT-05 判滿地「真源查無」（LL-00013）。
RE_GATE_BLOCK = re.compile(r"GATE:\n((?:[ \t]*[a-z-]+=[^\n]*\n)+)")
RE_ANCHOR = re.compile(r'finding\(\s*(?:ERROR|WARN|SKIP)\s*,\s*"(GT-\d{2})"')
RE_GT_ID = re.compile(r"GT-(\d{2})")
RE_GT_RANGE = re.compile(r"GT-(\d{2})\s*[～~]\s*GT-(\d{2})")
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
GATES_MD = "docs/generated/GATES.md"
PRECOMMIT = ".githooks/pre-commit"
RUNBOOK = "docs/ops/RUNBOOK.md"
README = "README.md"
# 編排骨架子名冊（ADR-00020）：檔表資料列首欄＝反引號檔名（不含路徑）；README.md 自身不列、子目錄檔不計。
ORCH_DIR = "tools/orchestration/"
ORCH_README = ORCH_DIR + "README.md"
RE_ORCH_ROW = re.compile(r"^\| `([^`/|]+)` \|", re.M)
SETTINGS = ".claude/settings.json"
HOOKS_DIR = ".claude/hooks"
ROSTER_PREFIXES = ("tools/", "deploy/", ".githooks/", ".claude/")
EXEC_REQUIRED = (".githooks/pre-commit", ".githooks/pre-push", ".githooks-submodule/pre-commit", ".githooks-submodule/pre-push",
                 "deploy/sops.sh", "deploy/generate-age-key.sh", "deploy/generate-dev-cert.sh", "tools/bootstrap.sh")
# 數量預算（ADR-00011 supersede ADR-00004）：閘數與 RULES per-scope 保留上限但**一律 WARN**（不隨波轉 ERROR、不擋 commit）；
# BACKLOG 開放為觀測值、**不設上限**（壓低它只有「真做掉」或「不記」兩途，後者是治理面最不該給的誘因）。
BUDGET_GATES = 12
KNIFE_START_WAVE = 6   # 波 6 起＝刀期（只服務波標記落後腿；與數量預算無關）
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
DAY1_EXEMPTIONS = {
    # 目前零筆：GT-08.lessons-absent（登記 2026-09-03）隨 LL-00001 落地（2026-09-04）解除、依 RL-0052 到期即移除；新豁免逐筆具名帶解除謂詞。
}


# ---------------------------------------------------------------------------
# 環境型具名跳過登記（ADR-00019 形；000-r2 修單＝BL-00003②）
# ---------------------------------------------------------------------------
# 與 Day-1 豁免兩制、不可混：Day-1 豁免有「解除謂詞」、到期即紅（RL-0052）；環境型跳過不會到期，
# 只在**本機環境缺席**時觸發、印一行「⤳ 跳過：」rc 0（ADR-00019 決定 3：跳過與通過在輸出上必須可辨）。
# 欄＝鍵 →（命中謂詞的人可讀字面, 理由）；GT-12 斷言原始碼全部 SKIP 錨形鍵 ⊆ DAY1_EXEMPTIONS ∪ 本表。
ENV_SKIPS = {
    "GT-02.submodule-absent": ("base-web／rust-api 之 .git 任一不存在",
                               "唯讀看碼捷徑（git submodule update --init、無源倉）或新機尚未 bootstrap：pins 的子庫側 SHA 無處實證"),
    "GT-05.submodule-absent": ("base-web／rust-api 之 .git 任一不存在",
                               "同上：子庫 pin 樹不在，碼面裸編號的 git grep 無標的"),
    "GT-07.secrets-absent": ("SECRETS_DIR 三級解析所得路徑非目錄",
                             "新機尚未佈機密（deploy/decrypt-secrets.py 未跑）：實值比對無標的；樣式面照掃"),
}
RE_SKIP_ANCHOR = re.compile(r'finding\(\s*SKIP\s*,\s*"GT-\d{2}"')
RE_SKIP_KEY = re.compile(r"GT-\d{2}\.[a-z0-9-]+")


def registered_skip_keys():
    """具名跳過之**登記集合**的單一權威＝Day-1 豁免 ∪ 環境型跳過。
    gt_12（靜態掃原始碼錨形）與 run_lint（執行期掃 SKIP 訊息）兩腿同取本函式：
    日後若再分出第三本登記，兩處各寫一份聯集只會改到一邊——另一邊靜默停止承認新登記
    （改 gt_12 漏 run_lint＝每趟 lint 多噴假 WARN；反向＝已登記的鍵被判未登記、pre-commit 直接紅）。"""
    return set(DAY1_EXEMPTIONS) | set(ENV_SKIPS)


def skip_key_of(text, start=0, end=None):
    """文字中第一個 `GT-NN.slug` 鍵（無則 None）——靜態面與執行期面共用同一抽取口徑。
    ★兩面的差別只在**視窗**（靜態＝錨形後方同一 call 內；執行期＝訊息全文），取法不得各寫一份。"""
    text = text or ""
    m = RE_SKIP_KEY.search(text, start, len(text) if end is None else end)
    return m.group(0) if m else None


def derive_skip_keys(source_text):
    """原始碼每個 `finding(SKIP, "GT-NN", …)` 錨形後方（同一 call 內）的第一個 `GT-NN.slug` 鍵。
    回 (鍵集, 無鍵錨形數)——具名跳過必帶鍵（ADR-00019），無鍵者由 GT-12 指名。"""
    text = source_text or ""
    keys, anchorless = set(), 0
    for m in RE_SKIP_ANCHOR.finditer(text):
        nxt = text.find("finding(", m.end())
        end = m.end() + 300 if nxt < 0 else min(nxt, m.end() + 300)
        k = skip_key_of(text, m.end(), end)
        if k:
            keys.add(k)
        else:
            anchorless += 1
    return keys, anchorless


def unregistered_skip_warnings(findings):
    """執行期 SKIP findings 中鍵未登記者逐筆 WARN；登記集合與鍵抽取皆取上方單一權威。"""
    reg = registered_skip_keys()
    out = []
    for f in findings:
        if f[0] != SKIP:
            continue
        # 具名跳過的鍵可落在訊息任一處（ADR-00019 形以「⤳ 跳過：」起頭）；連鍵都沒有者退回冒號前綴、由本腿指名
        key = skip_key_of(f[3]) or f[3].split("：", 1)[0]
        if key not in reg:
            out.append(finding(WARN, "GT-12", f[2], f"未登記的 SKIP 鍵 {key}（須登記 DAY1_EXEMPTIONS 或 ENV_SKIPS）"))
    return out


# ---------------------------------------------------------------------------
# GT-01
# ---------------------------------------------------------------------------
def gt_01(ctx):
    """GATE:
      id=GT-01
      rule=RL-0049
      source=rev5:ADR 0052
      drift=generated↔真源；真源掃描面存在性
      face=GENERATED_FILES（docs/generated/**＋tools/orchestration/_sk_rules.js＋例外註冊 docs/arc42/ARCHITECTURE.md、docs/ops/LESSONS.md）＋agents.md 之真源掃描面（tracked tools/orchestration 之 *.js／*.mjs 的 *_OPTS 字面；空集合＝WARN）
      trigger=pre-commit
      rc=1
      breaks-if-removed=鏡像可手改、生成檔與真源靜默分叉、*_OPTS 字面形改動可靜默縮小掃描面而不察
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
        return out + [finding(SKIP, "GT-07", sdir, "⤳ 跳過：機密落點目錄不存在"
                                            "（命中謂詞＝SECRETS_DIR 三級解析所得路徑非目錄；GT-07.secrets-absent）"
                                            "——實值比對未執行、樣式面已掃；ADR-00019 環境缺席具名跳過 rc 0")]
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
            toks = m.group(2).split("、")
            # 深度 0 的項本身就是完整路徑；同列後續 token 若無目錄段（如「docs/ops/LESSONS.md、LESSONS/」之 LESSONS/），
            # 繼承首項的目錄前綴——否則被解析成根層路徑、目錄形者還會誤入 leaf_dirs 覆蓋集（000-r2 L3-08）。
            prefix = os.path.dirname(toks[0].rstrip("/")) if not stack else ""
            for i, tok in enumerate(toks):
                base = tok.rstrip("/")
                if i and prefix and "/" not in base:
                    base = f"{prefix}/{base}"
                full = "/".join(stack + [base]) + ("/" if tok.endswith("/") else "")
                paths.add(full)
            stack.append(toks[0].rstrip("/"))
    leaf_dirs = {d for d in paths if d.endswith("/") and d not in parents}
    return paths, leaf_dirs


def _covered(rel, declared, leaf_dirs):
    if rel in declared:
        return True
    return any(rel.startswith(d) for d in leaf_dirs)


def readme_generated_members(text):
    """README 樹之 `docs/generated/` 行描述文字 → 成員相對路徑集（BL-00009）。
    形＝`… 嚴禁手改：A／B／…／reference/{x,y,z}`：以「：」取右段、`／` 分隔、`{a,b}` 展開為 `前綴a`…。
    找不到該行回 None（與「行在但成員集為空」區分——後者是真漂移）。"""
    m = re.search(r"^\s*[│├└─\s]*docs/generated/\s+[^\n：]*：([^\n]+)$", text or "", re.M)
    if m is None:
        return None
    members = set()
    for tok in m.group(1).split("／"):
        tok = tok.strip()
        if not tok:
            continue
        b = re.match(r"^(.*?)\{([^}]*)\}$", tok)
        if b:
            members |= {f"{b.group(1)}{x.strip()}" for x in b.group(2).split(",") if x.strip()}
        else:
            members.add(tok)
    return members


def gt_09(ctx):
    """GATE:
      id=GT-09
      rule=RL-0057
      source=rev5:L-061
      drift=接線與實檔集（含編排骨架子名冊）
      face=README 樹（含 docs/generated 成員行）、tools/deploy/.githooks/.claude、settings.json、EXEC_REQUIRED、tools/orchestration/README.md 檔表（⇔ tools/orchestration/ tracked 檔集；ADR-00020）
      trigger=pre-commit
      rc=1
      breaks-if-removed=hook 被 pnpm install 覆寫或失去 exec bit 而靜默失效、README 地圖與實檔分叉
    """
    out = []
    tracked = set(ctx.tracked)
    readme = ctx.text(README)
    if readme is None:
        out.append(finding(ERROR, "GT-09", README, "README 文件地圖缺席（現在式面必在；RL-0051 掃描面空集合即紅）"))
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
        # docs/generated 成員窮舉腿（BL-00009）：ROSTER_PREFIXES 不含 docs/，該行歷來只能人工同刀改齊
        _GEN_PREFIX = "docs/generated/"
        declared_gen = readme_generated_members(readme)
        if declared_gen is None:
            out.append(finding(ERROR, "GT-09", README, "README 樹缺 docs/generated/ 成員行（形＝「…：A／B／reference/{x,y}」）"))
        else:
            actual_gen = {r[len(_GEN_PREFIX):-3] for r in ref_mod.GENERATED_FILES
                          if r.startswith(_GEN_PREFIX) and r.endswith(".md")}
            for x in sorted(declared_gen - actual_gen):
                out.append(finding(ERROR, "GT-09", README, f"README generated 成員行列 {x} 但不在 GENERATED_FILES 名冊"))
            for x in sorted(actual_gen - declared_gen):
                out.append(finding(ERROR, "GT-09", README, f"GENERATED_FILES 有 {x} 但 README generated 成員行未列（名冊變動須同刀改齊）"))
    # 編排骨架子名冊腿（ADR-00020；maint-backlog-6）：tools/orchestration/ 頂層 tracked 檔集（README.md 除外）⇔ tools/orchestration/README.md 檔表首欄
    #   反引號集、雙向差集即紅——根 README 樹只以葉目錄粒度覆蓋該目錄、新增檔漏列不紅（000-r1 R1-065 人工補四支）；零 orchestration 檔＝腿不跑；
    #   表缺席／零列＝掃描面空集合即紅（RL-0051）。
    orch_files = {r[len(ORCH_DIR):] for r in tracked if r.startswith(ORCH_DIR) and "/" not in r[len(ORCH_DIR):]} - {"README.md"}
    if orch_files:
        orch_readme = ctx.text(ORCH_README)
        if orch_readme is None:
            out.append(finding(ERROR, "GT-09", ORCH_README, "編排骨架檔表缺席（掃描面空集合；ADR-00020：tools/orchestration/ 有 tracked 檔即須有檔表）"))
        else:
            listed = set(RE_ORCH_ROW.findall(orch_readme))
            if not listed:
                out.append(finding(ERROR, "GT-09", ORCH_README, "編排骨架檔表零列（掃描面空集合；表形＝資料列首欄反引號檔名）"))
            for x in sorted(listed - orch_files):
                out.append(finding(ERROR, "GT-09", ORCH_README, f"檔表列 {x} 但 tools/orchestration/ 無此 tracked 檔（幽靈列；改名／移除須同批改表）"))
            for x in sorted(orch_files - listed):
                out.append(finding(ERROR, "GT-09", ORCH_DIR + x, "tracked 檔未列於 tools/orchestration/README.md 檔表（增檔須同批入表；ADR-00020）"))
    hooks_absent = not ctx.exists(PRECOMMIT)
    if hooks_absent:
        out.append(finding(ERROR, "GT-09", ".githooks", ".githooks/pre-commit 缺席（現在式面必在；RL-0051 掃描面空集合即紅）——其餘 EXEC_REQUIRED 照驗"))
    for rel in EXEC_REQUIRED:
        if rel not in tracked:
            if not (hooks_absent and rel.startswith(".githooks/")):   # 尾斜線：.githooks-submodule/* 不在此豁免內（000-r2 L3-07）
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
# 主張對賬（000-r2 修單＝BL-00003③；user 停點① 拍板「補既有閘腿、不占閘數」）
# ---------------------------------------------------------------------------
# 人寫面（CLAUDE.md、憲法）寫死的數值與 SHA 字面，過去只靠人記得同批改；本腿把它們對回工具側常數。
# ★兩側值一律**唯讀讀檔＋正則**取：不 import 編排骨架、不執行 js（骨架是 node 檔、閘是 host python）。
CLAIM_FACE = ("CLAUDE.md", CONSTITUTION)
BOOTSTRAP = "tools/bootstrap.sh"
SK_HEAD = "tools/orchestration/_sk_head.js"
# 人寫面之 SHA 主張＝反引號短 hex（至少含一位數字，避開 `decade` 這類純字母 token）
RE_DOC_SHA = re.compile(r"`(?=[0-9a-f]*[0-9])([0-9a-f]{7,40})`")
RE_BOOT_SHA = (("BASEWEB_BASE_SHA", re.compile(r'\bBASEWEB_BASE_SHA="([0-9a-f]+)"')),
               ("RUSTAPI_BASE_SHA", re.compile(r'\bRUSTAPI_BASE_SHA="([0-9a-f]+)"')))
RE_BOOT_FROZEN = re.compile(r'\bREV5_FROZEN="([^"]*)"')
# 五處 SHA 主張**逐槽**對賬：(名, 人寫面錨形正則〔捕獲組＝被控字面〕, bootstrap 側常數名)；比照同檔 CAP_CLAIMS 形。
# ★錨形只認語境、不認值——認值即循環論證。整檔「集合成員」判定只答得出「是不是那五個之一」、答不出「這一處該是哪一個」，
#   三型真實錯法（兩處對調／整行刪除／張冠李戴）全數靜默過關，故逐槽比值＋逐槽錨形零命中即紅（RL-0051）。
SHA_CLAIMS = (
    ("base-web 基線", re.compile(r"(?:example|基線 SHA)[^\n]{0,14}?" + RE_DOC_SHA.pattern), "BASEWEB_BASE_SHA"),
    ("rust-api 分支點", re.compile(r"源倉 main[^\n]{0,8}?" + RE_DOC_SHA.pattern), "RUSTAPI_BASE_SHA"),
    # 外層槽：「rust-api 凍結 SHA」「base-web 凍結 SHA」屬下兩槽，以定寬 lookbehind 讓出
    ("rev5 外層凍結", re.compile(r"(?<!base-web )(?<!rust-api )凍結(?:於)?\s?SHA[^\n]{0,6}?" + RE_DOC_SHA.pattern), "REV5_FROZEN[.]"),
    ("rev5 base-web 凍結", re.compile(r"base-web\s?" + RE_DOC_SHA.pattern), "REV5_FROZEN[base-web]"),
    ("rev5 rust-api 凍結", re.compile(r"rust-api[^\n]{0,10}?" + RE_DOC_SHA.pattern), "REV5_FROZEN[rust-api]"),
)
# 三個上限主張：(名, 人寫面錨形正則, 工具側取值正則, 工具側常數名)
CAP_CLAIMS = (
    ("fix 迴圈上限", re.compile(r"fix 迴圈[^\n；]*?≤\s*(\d+)"), re.compile(r"\bconst MAX_FIX_ROUNDS = (\d+)"), "MAX_FIX_ROUNDS"),
    # ★工具側錨形必綁常數名：認「第一個 Math.min(」＝與 AGENT_FUSE 零語境綁定，骨架日後在該行之前多出任一
    #   `Math.min(n, …)`（節流／切片／進度）即改抓別的值——要嘛指著錯的兩側值誤紅、要嘛在真保險絲已改時靜默放行（000-r2 修-CQ1）。
    ("TDD 執行單元 agent 保險絲", re.compile(r"保險絲[^\n；]*?≤\s*(\d+)"),
     re.compile(r"\bAGENT_FUSE\s*=\s*Math\.min\(\s*(\d+)\s*,"), "AGENT_FUSE = Math.min(<上限>, …)"),
    ("review 形每 run 上限", re.compile(r"review 形每 run[^\n；]*?≤\s*(\d+)"), re.compile(r"\bconst MAX_AGENTS_PER_RUN = (\d+)"), "MAX_AGENTS_PER_RUN"),
)


def _bootstrap_sha_map(boot):
    """bootstrap.sh → {常數名: 值}；`REV5_FROZEN` 依 `<子庫>:<sha>` 逐對展成 `REV5_FROZEN[<子庫>]`。取不到的鍵不入表。"""
    vals = {}
    for name, rx in RE_BOOT_SHA:
        m = rx.search(boot)
        if m:
            vals[name] = m.group(1)
    fm = RE_BOOT_FROZEN.search(boot)
    for pair in (fm.group(1).split() if fm else ()):
        if ":" in pair:
            sub, sha = pair.split(":", 1)
            vals[f"REV5_FROZEN[{sub}]"] = sha
    return vals


def _sha_claim_legs(ctx, tool_vals):
    """五處 SHA 主張逐槽比值（不等即指名檔:行＋兩側值）、逐槽錨形零命中即紅；
    槽外殘留的**基線／凍結 SHA 字面**＝錨形涵蓋不到的新寫法、一併指名（錨形隨人寫面演化的保命腿）。
    ★非該五值的反引號 hex（commit SHA、RULES-VERSION 值）不在本腿射程——那些不是基線／凍結 SHA 主張。"""
    out, claimed = [], {}
    for name, doc_rx, const_name in SHA_CLAIMS:
        want, n = tool_vals.get(const_name), 0
        for rel in CLAIM_FACE:
            text = ctx.text(rel)
            if text is None:
                continue
            for i, line in enumerate(text.split("\n"), 1):
                for m in doc_rx.finditer(line):
                    n += 1
                    claimed.setdefault((rel, i), set()).add(m.span(1))
                    if want is not None and m.group(1) != want:
                        out.append(finding(ERROR, "GT-12", f"{rel}:{i}",
                                           f"主張對賬：{name} 宣稱 `{m.group(1)}`、{BOOTSTRAP} 之 {const_name}＝`{want}`（兩側之一失準）"))
        if want is not None and n == 0:
            out.append(finding(ERROR, "GT-12", "／".join(CLAIM_FACE),
                               f"主張對賬：{name}（{const_name}）錨形於人寫面零命中（掃描面空集合即紅、RL-0051）"
                               f"——主張整段刪除、或措辭改到錨形外，兩者都須同批處置"))
    known = set(tool_vals.values())
    for rel in CLAIM_FACE:
        text = ctx.text(rel)
        if text is None:
            continue
        for i, line in enumerate(text.split("\n"), 1):
            for m in RE_DOC_SHA.finditer(line):
                if m.group(1) in known and m.span(1) not in claimed.get((rel, i), ()):
                    out.append(finding(ERROR, "GT-12", f"{rel}:{i}",
                                       f"主張對賬：`{m.group(1)}` 是基線／凍結 SHA、卻落在任一具名槽的錨形外"
                                       f"（新寫法未入槽＝該處無人對賬；SHA_CLAIMS 須同批補錨形）"))
    return out


def _claim_legs(ctx):
    """人寫面的數值／SHA 主張 ⇄ 工具常數；不符即 ERROR 指名（檔:行、兩側值）。錨形零命中＝掃描面空集合即紅（RL-0051）。"""
    out = []
    boot = ctx.text(BOOTSTRAP)
    if boot is None:
        out.append(finding(ERROR, "GT-12", BOOTSTRAP, "主張對賬：tools/bootstrap.sh 缺席——基線／凍結 SHA 的單一家不在，無對賬基準"))
    else:
        tool_vals = _bootstrap_sha_map(boot)
        slots = {c for _, _, c in SHA_CLAIMS}
        if set(tool_vals) != slots:
            out.append(finding(ERROR, "GT-12", BOOTSTRAP,
                               f"主張對賬：bootstrap SHA 常數集與具名槽不對應（缺 {sorted(slots - set(tool_vals))}"
                               f"、多 {sorted(set(tool_vals) - slots)}）——常數形改動須同批改 SHA_CLAIMS"))
        out += _sha_claim_legs(ctx, tool_vals)
    head = ctx.text(SK_HEAD)
    for name, doc_rx, tool_rx, const_name in CAP_CLAIMS:
        tm = tool_rx.search(head or "")
        if tm is None:
            out.append(finding(ERROR, "GT-12", SK_HEAD, f"主張對賬：{SK_HEAD} 取不到 {const_name}（{name} 無對賬基準）"))
            continue
        n = 0
        for rel in CLAIM_FACE:
            text = ctx.text(rel)
            if text is None:
                continue
            for i, line in enumerate(text.split("\n"), 1):
                for m in doc_rx.finditer(line):
                    n += 1
                    if m.group(1) != tm.group(1):
                        out.append(finding(ERROR, "GT-12", f"{rel}:{i}",
                                           f"主張對賬：宣稱 {name} ≤{m.group(1)}、{SK_HEAD} 之 {const_name}＝{tm.group(1)}（兩側之一失準）"))
        if n == 0:
            out.append(finding(ERROR, "GT-12", "／".join(CLAIM_FACE), f"主張對賬：{name} 錨形於人寫面零命中（掃描面空集合即紅、RL-0051）——錨形措辭改動須同批改本腿"))
    return out


# ---------------------------------------------------------------------------
# GT-12
# ---------------------------------------------------------------------------
# 碼面閘表腿（002 刀 U0）：tools/ 頂層 *.py 除下列非閘工具外皆為碼面閘、MUST 列於 RUNBOOK §12 碼面閘表（名冊唯一權威；
# GATES.md 依 ADR-00010 不收碼面閘）。新增非閘工具＝改此常數同刀；碼面閘進場＝入表同刀。
# 003 刀 U10a：tools/walkthrough-baseline.py＝走查前後全表基準對賬（隨遷、需 dev stack、走查收尾手動跑）、不守版控品質＝非閘。
NON_GATE_TOOLS = ("tools/wf-watchdog.py", "tools/comment-overlap.py", "tools/walkthrough-baseline.py")
RE_CODEGATE_HEADER = re.compile(r"^\|\s*工具檔\s*\|")
RE_CODEGATE_PATH = re.compile(r"^`(tools/[^`/]+\.py)`$")


def runbook_codegate_tools(text):
    """RUNBOOK 碼面閘表（表頭首欄「工具檔」）→ 首欄反引號 `tools/….py` 路徑集；首欄非路徑者＝註記列、不計。
    表缺席回 None（與「表在但零路徑列」區分——後者是空集合、RL-0051 即紅）。"""
    lines = (text or "").split("\n")
    start = next((i for i, ln in enumerate(lines) if RE_CODEGATE_HEADER.match(ln)), None)
    if start is None:
        return None
    paths = set()
    for ln in lines[start + 1:]:
        if not ln.startswith("|"):
            break
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not cells or re.fullmatch(r":?-+:?", cells[0]):
            continue
        m = RE_CODEGATE_PATH.match(cells[0])
        if m:
            paths.add(m.group(1))
    return paths


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
      drift=名冊同源與數量預算、SKIP 鍵登記、人寫面數值／SHA 主張
      face=tools/docsync/*.py（含 SKIP 錨形鍵 ⊆ DAY1_EXEMPTIONS ∪ ENV_SKIPS）、GATES.md、pre-commit 檔頭、RUNBOOK、RUNBOOK 碼面閘表（⇔ tools/ 頂層 *.py − NON_GATE_TOOLS）、NOTES 波標記、CLAUDE.md 與憲法之 SHA／上限主張（⇔ tools/bootstrap.sh、tools/orchestration/_sk_head.js）
      trigger=pre-commit
      rc=1
      breaks-if-removed=閘可無語意區塊、名冊三處分叉、預算超限連警告都沒有、跳過分支可無名無登記、人寫面數值與工具常數可單邊漂移
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
    if set(blocks) != roster_ids:   # 只驗名冊一致；數量歸下方預算腿（ADR-00011：兩種語意分離）
        out.append(finding(ERROR, "GT-12", "tools/docsync", f"區塊集合 {sorted(blocks)} ≠ ROSTER {sorted(roster_ids)}"))
    # SKIP 鍵登記腿（000-r2 修單＝BL-00003②）：原始碼全部 SKIP 錨形鍵 ⊆ DAY1_EXEMPTIONS ∪ ENV_SKIPS
    skip_keys, anchorless = derive_skip_keys(joined)
    for k in sorted(skip_keys - registered_skip_keys()):
        out.append(finding(ERROR, "GT-12", "tools/docsync", f"GT-12：SKIP 鍵 {k} 未登記（DAY1_EXEMPTIONS／ENV_SKIPS）"))
    if anchorless:
        out.append(finding(ERROR, "GT-12", "tools/docsync", f"{anchorless} 處 SKIP 錨形後方無 GT-NN.slug 鍵——具名跳過必帶鍵（ADR-00019）"))
    gates_md = ctx.text(GATES_MD)
    if gates_md is not None:
        ids = set(re.findall(r"^\| (GT-\d{2}) \|", gates_md, re.M))
        if ids != roster_ids:
            out.append(finding(ERROR, "GT-12", GATES_MD, f"GATES.md 閘集合 {sorted(ids)} ≠ ROSTER（跑 generate）"))
    pre = ctx.text(PRECOMMIT)
    if pre is None:
        out.append(finding(ERROR, "GT-12", PRECOMMIT, "pre-commit 缺席（現在式面必在；RL-0051 掃描面空集合即紅）"))
    else:
        head = "\n".join(pre.split("\n")[:20])
        m = RE_GT_RANGE.search(head)
        ids = {f"GT-{i:02d}" for i in range(int(m.group(1)), int(m.group(2)) + 1)} if m else set()
        if ids != roster_ids:
            out.append(finding(ERROR, "GT-12", PRECOMMIT, f"pre-commit 檔頭範圍字串 {'缺席' if not m else m.group(0)} ≠ ROSTER（{min(sorted(roster_ids))}～{max(sorted(roster_ids))}）"))
    rb = ctx.text(RUNBOOK)
    if rb is None:
        out.append(finding(ERROR, "GT-12", RUNBOOK, "RUNBOOK 缺席（現在式面必在；RL-0051 掃描面空集合即紅）"))
    else:
        if _gt_ids_in(rb) != roster_ids:
            out.append(finding(ERROR, "GT-12", RUNBOOK, f"RUNBOOK 工具表閘集合 {sorted(_gt_ids_in(rb))} ≠ ROSTER"))
        # 碼面閘表腿（002 刀 U0）：S_tools（tools/ 頂層 tracked *.py − NON_GATE_TOOLS）⇔ S_table（表首欄反引號路徑集）雙向對賬
        s_tools = {p for p in ctx.tracked if p.startswith("tools/") and p.count("/") == 1 and p.endswith(".py")} - set(NON_GATE_TOOLS)
        s_table = runbook_codegate_tools(rb)
        if s_table is None:
            out.append(finding(ERROR, "GT-12", RUNBOOK, "RUNBOOK 碼面閘表缺席（§12 表頭首欄「工具檔」）——碼面閘名冊唯一權威、GATES.md 不收"))
        elif not s_table:
            out.append(finding(ERROR, "GT-12", RUNBOOK, "RUNBOOK 碼面閘表零路徑列（掃描面空集合即紅、RL-0051）——首欄須為反引號 tools/….py"))
        else:
            for x in sorted(s_table - s_tools):
                out.append(finding(ERROR, "GT-12", RUNBOOK, f"RUNBOOK 碼面閘表列 {x} 但 tools/ 頂層無此 tracked 檔（幽靈列；改名／移除須同刀改表）"))
            for x in sorted(s_tools - s_table):
                out.append(finding(ERROR, "GT-12", x, f"tools/ 頂層 {x} 未列於 RUNBOOK 碼面閘表（碼面閘進場須同刀入表；非閘工具改 NON_GATE_TOOLS）"))
    out += _claim_legs(ctx)
    wave = book_mod.current_wave(ctx)
    if wave is None:
        out.append(finding(ERROR, "GT-12", NOTES, "波標記缺席：docs/ops/NOTES.md 首行須為 <!-- wave: N -->"))
    level = WARN   # ADR-00011：數量預算一律只警告、不擋 commit（舊形＝波 6 起 ERROR）
    if wave is not None and wave < KNIFE_START_WAVE:
        knives = {r.split("/")[1] for r in ctx.tracked if r.startswith("specs/") and r.count("/") >= 2 and re.match(r"\d{3}-", r.split("/")[1])}
        if knives:
            out.append(finding(ERROR, "GT-12", NOTES, f"波標記落後：specs/ 已有刀目錄 {sorted(knives)} 而現在波 {wave} < {KNIFE_START_WAVE}（波次出口須 bump 標記）"))
    if len(roster_ids) > BUDGET_GATES:
        out.append(finding(level, "GT-12", "tools/docsync", f"閘數 {len(roster_ids)} 超上限 {BUDGET_GATES}（一進一出；本腿只警告、不擋）"))
    counts, caps = rules_mod.budget_counts(ctx.text(RULES) or "")
    for k, n in counts.items():
        cap = caps.get(k)
        if isinstance(cap, int) and n > cap:
            out.append(finding(level, "GT-12", RULES, f"RULES {k} {n} 超上限 {cap}（一進一出或改上限＝supersede ADR-00011；本腿只警告、不擋）"))
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
    findings += unregistered_skip_warnings(list(findings))
    n_err = sum(1 for f in findings if f[0] == ERROR)
    n_warn = sum(1 for f in findings if f[0] == WARN)
    n_skip = sum(1 for f in findings if f[0] == SKIP)
    return findings, f"lint：{n_err} 錯誤／{n_warn} 警告／{n_skip} 閘跳過"


def gen_gates_md(ctx):
    blocks = parse_gate_blocks("\n".join(package_sources().values()))
    lines = [GENERATED_HEADER, "# GATES — 閘名冊（§4.1）", "",
             f"閘數 {len(ROSTER)}／上限 {BUDGET_GATES}（一進一出；超限只警告不擋＝ADR-00011）。真源兩層：存在＝原始碼 finding 錨形、語意＝docstring GATE 區塊（GT-12 斷言錨形 ⊆ 區塊、三處名冊同源）。"
             f"Day-1 豁免 {len(DAY1_EXEMPTIONS)} 筆（§4.6；到期即紅）、環境型具名跳過 {len(ENV_SKIPS)} 筆（ADR-00019；rc 0、不到期）。", "",
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
        lines.append(f"| {k} | {ex.reason} | {ex.predicate_text or '（見 gates.py）'} | {ex.registered} |")
    lines += ["", "## 環境型跳過登記（鍵｜命中謂詞｜理由）", "",
              "ADR-00019 形：環境缺席＝具名跳過 rc 0（不到期、與 Day-1 豁免兩制）；GT-12 斷言原始碼 SKIP 錨形鍵 ⊆ 本表 ∪ Day-1 豁免。", "",
              "| 鍵 | 命中謂詞 | 理由 |", "|---|---|---|"]
    for k, (pred, reason) in ENV_SKIPS.items():
        lines.append(f"| {k} | {pred} | {reason} |")
    return "\n".join(lines) + "\n"
