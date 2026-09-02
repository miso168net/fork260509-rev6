# 波 1 治理工具實作計畫（憲法 1.0.0／RULES 首版／GT-01～GT-12／docsync／hooks）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把啟動書 §3.5／§3.6／§3.8／§4 拍板的治理最小集落成可跑的工具與文件，達成波 1 出口：`python3 tools/docsync lint` 零 ERROR、Day-1 豁免逐筆有解除謂詞、GT-12 首值在預算內、pre-commit 實跑守門。

**Architecture:** `tools/docsync/` 是純 python 標準庫 package（六個領域模組＋common＋CLI），每條閘 GT-NN 是一個函式：docstring 帶固定 `GATE:` 鍵值區塊（名冊語意真源）、函式體以 `finding(LEVEL, "GT-NN", …)` 錨形回報（名冊存在真源）；GT-12 斷言兩真源同源。generate 只由 events／ADR／RULES／compose 等真源重算 `docs/generated/`，check 比對零漂移。hooks（`.githooks/`）串 betterleaks → check → lint → 條件自測；bootstrap 回填掃描防線斷言。

**Tech Stack:** python 3.12 標準庫（unittest、re、json、subprocess、hashlib）；POSIX sh hooks；git；betterleaks 1.7.3（釘版）；docker compose（只在 ports 真表與 render 斷言）。

**Spec:** `docs/brainstorms/000-doc-architecture.md`（§3.1、§3.4～§3.8、§4.1～§4.6、§5 波 1 列、附錄 E）；形制藍本＝rev5 `tools/docs-sync.py`（唯讀、不搬運）與 rev5 `.githooks/`。

## Global Constraints

- 語言：一切書面產物 zh-TW；RAD-AI 文字全部中文改寫、不逐字（D15）。
- 工具：只用 python 標準庫；`tools/docsync/` 邏輯行數 ≤4,000（測試不計）；每模組檔頭一行「守哪條 RULES」。
- 閘：恰 12 條 GT-01～GT-12（一進一出）；每條至少一正一反自證；掃描面空集合即紅（§4.2 橫切）；非 vacuous 自證（承 rev5:ADR 0024）。
- 名冊：閘的存在＝`finding(LEVEL,"GT-NN")` 錨形掃源；語意＝docstring `GATE:` 區塊；GT-12 斷言錨形集合 ⊆ 區塊集合，且 GATES.md／pre-commit 檔頭範圍字串／RUNBOOK 工具表三處相等（RUNBOOK 缺席＝Day-1 豁免）。
- 編號：BL-／LL-／ADR-（五碼）、RL-（四碼）、GT-（二碼）；引 rev5 一律 `rev5:` 前綴；裸刀號禁（附錄 E）。
- 數量預算（D8）：lint 條數 ≤12；RULES 上限＝首版實算去重後 ＋25%（本計畫 Task 2 定值，寫進 ADR-00004）；BACKLOG 開放 ≤25；波 1～5 為 WARN、波 6 起 ERROR（判準＝events 有無 feature_close）。
- 機器生成檔一律檔頭 `<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->`。
- git：可自行 commit；不 push、不 merge；每 Task 末一顆 commit；commit 訊息 zh-TW。
- 環境：/mnt/d drvfs——跑過 docker bind mount 後同 shell 先重新 `cd`；exec bit 以 `git update-index --chmod=+x` 落 index。

---

## 檔案結構（先鎖定分工）

```
tools/docsync/__init__.py        VERSION="0.1.0"；ROOT（自 __file__ 上溯兩層）；路徑常數名冊
tools/docsync/__main__.py        CLI：generate｜check｜lint｜rules emit --scope S [--format text|js]｜errata <詞>｜test
tools/docsync/common.py          Finding／finding()／Ctx／parse_front_matter／git helpers／GENERATED_HEADER／Day1Exemption
tools/docsync/events.py          EVENT_SCHEMAS、parse_events、gt_02、gt_03、metrics()
tools/docsync/adr.py             load_adrs、gt_04、gen_decisions_index、backfill_superseded_by
tools/docsync/book.py            gt_05（ID 家族）、gt_06（引用健康）、gt_10（形制閘）、gt_11（bash 面）、errata_scan
tools/docsync/rules.py           parse_rules、gt_08、emit()、rules_version()
tools/docsync/references.py      gen_reference_ports、gen_reference_perf、gen_state、gen_milestones、compute_generated、check_generated（GT-01 本體）
tools/docsync/gates.py           ROSTER、parse_gate_blocks、derive_anchor_codes、gt_01（包 check）、gt_07（機密）、gt_09（接線）、gt_12（名冊同源＋預算）、DAY1_EXEMPTIONS、run_lint、gen_gates_md
tools/docsync/tests/test_common.py … test_gates.py（每模組一檔）＋ tests/fixtures/（合成語料）
docs/ops/RULES.md                規則層首版（人寫）
docs/ops/events.jsonl            事件源（波 1 創世 misc 事件起）
docs/arc42/decisions/ADR-00003-constitution-1.0.0.md   憲法定版
docs/arc42/decisions/ADR-00004-rules-first-edition-and-budgets.md   RULES 首版與數量上限
.specify/memory/constitution.md  rev6 1.0.0（§3.8 逐條表）
.gitleaks.toml、.githooks/{pre-commit,pre-push,lib/scan-range.sh}、.githooks-submodule/{pre-commit,pre-push}
tools/bootstrap.sh               回填 §1 掃描防線、§3b 子庫 hooksPath、§5 docsync 自測與條款數
.claude/hooks/pre-workflow-gate.py   升級：RULES-VERSION 對賬
tools/orchestration/_sk_rules.js     改為 generate 產物（GENERATED_FILES 名冊）
README.md、CLAUDE.md             文件地圖（GT-09 對賬面）與正式版操作手冊
docs/generated/{STATE,MILESTONES,DECISIONS-INDEX,GATES}.md、docs/generated/reference/{ports,perf}.md
```

共用接口（各 Task 引用時以此為準）：

```python
# common.py
ERROR, WARN, SKIP = "ERROR", "WARN", "SKIP"
Finding = tuple  # (level, code, where, msg)；code 形 "GT-NN"
def finding(level, code, where, msg): return (level, code, where, msg)
class Ctx:
    root: str; tracked: list[str]
    def text(self, rel) -> str | None          # 工作樹讀檔（UTF-8、快取）；不存在→None
    def head_text(self, rel) -> str | None     # git show HEAD:rel；無 HEAD／無檔→None
    def exists(self, rel) -> bool
    def md_texts(self, prefixes=()) -> dict    # {rel: text}，只收 tracked *.md、可限前綴
    def git(self, *args, cwd=None) -> str      # 失敗→raise GitError
def parse_front_matter(text) -> tuple[dict, str]   # (meta, body)；無 frontmatter→({}, text)
GENERATED_HEADER = "<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->"
class Day1Exemption:  # key, reason, released(ctx)->bool, registered("YYYY-MM-DD")
```

閘函式簽名一律 `def gt_NN(ctx) -> list[Finding]`，docstring 首段固定形：

```
GATE:
  id=GT-02
  rule=RL-0031
  source=rev5:ADR 0012
  drift=事件帳形制、SHA 實證、pin↔worktree
  scope=docs/ops/events.jsonl；外層 index gitlink；兩 worktree HEAD
  trigger=pre-commit
  rc=1
  breaks-if-removed=事件帳可寫入任意形、假 SHA 入帳不察、pin 漂移靜默
```

---

### Task 1: docsync 骨架與 common（Finding／Ctx／frontmatter／CLI／測試入口）

**Files:**
- Create: `tools/docsync/__init__.py`、`tools/docsync/__main__.py`、`tools/docsync/common.py`
- Create: `tools/docsync/tests/__init__.py`、`tools/docsync/tests/test_common.py`

**Interfaces:**
- Produces: 上方共用接口全部；`__main__.main(argv) -> int`；`python3 tools/docsync test` 以 `unittest.defaultTestLoader.discover("tools/docsync/tests")` 跑全部。

- [ ] **Step 1: 寫失敗測試（frontmatter、Ctx.text、finding 形）**

```python
# tools/docsync/tests/test_common.py
import os, subprocess, tempfile, unittest
from docsync import common

class TestFrontMatter(unittest.TestCase):
    def test_parses_scalar_and_list(self):
        meta, body = common.parse_front_matter('---\nid: "ADR-00001"\ntags: [a, b]\nsupersedes: []\n---\n\n## 背景\n')
        self.assertEqual(meta["id"], "ADR-00001")
        self.assertEqual(meta["tags"], ["a", "b"])
        self.assertEqual(meta["supersedes"], [])
        self.assertTrue(body.startswith("\n## 背景"))
    def test_no_front_matter(self):
        self.assertEqual(common.parse_front_matter("# x\n"), ({}, "# x\n"))

class TestCtx(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", "-b", "main", self.d], check=True)
        with open(os.path.join(self.d, "a.md"), "w", encoding="utf-8") as f: f.write("A\n")
        subprocess.run(["git", "-C", self.d, "add", "a.md"], check=True)
        subprocess.run(["git", "-C", self.d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], check=True)
    def test_tracked_text_head(self):
        ctx = common.Ctx(self.d)
        self.assertEqual(ctx.tracked, ["a.md"])
        self.assertEqual(ctx.text("a.md"), "A\n")
        self.assertEqual(ctx.head_text("a.md"), "A\n")
        self.assertIsNone(ctx.text("nope.md"))
        self.assertEqual(ctx.md_texts(("a",)), {"a.md": "A\n"})
    def test_finding_shape(self):
        self.assertEqual(common.finding(common.ERROR, "GT-01", "x", "y"), ("ERROR", "GT-01", "x", "y"))
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `cd tools && python3 -m unittest docsync.tests.test_common -v`
Expected: FAIL（ModuleNotFoundError: docsync）

- [ ] **Step 3: 最小實作**

```python
# tools/docsync/__init__.py
"""守 RL-（Task 2 定號後回填）：三材質各有唯一的家、generated 禁手改。"""
import os
VERSION = "0.1.0"
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EVENTS = "docs/ops/events.jsonl"; RULES = "docs/ops/RULES.md"; BACKLOG = "docs/ops/BACKLOG.md"
BACKLOG_DEFERRED = "docs/ops/BACKLOG-DEFERRED.md"; LESSONS_INDEX = "docs/ops/LESSONS.md"; LESSONS_DIR = "docs/ops/LESSONS"
ADR_DIR = "docs/arc42/decisions"; GENERATED_DIR = "docs/generated"; CONSTITUTION = ".specify/memory/constitution.md"
DEFAULT_BRANCH = "rev6-admin-root"; SUBMODULES = ("base-web", "rust-api")
COMPOSE_FILES = ("docker-compose.yml", "docker-compose.dev.yml", "docker-compose.example.yml")
```

```python
# tools/docsync/common.py（節錄：全部函式簽名如共用接口；實作要點）
import os, re, subprocess, functools
ERROR, WARN, SKIP = "ERROR", "WARN", "SKIP"
def finding(level, code, where, msg): return (level, code, where, msg)
class GitError(RuntimeError): pass
RE_FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)
def _scalar(raw):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [] if not inner else [_scalar(x) for x in inner.split(",")]
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'": return raw[1:-1]
    return raw
def parse_front_matter(text):
    m = RE_FM.match(text or "")
    if not m: return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1); meta[k.strip()] = _scalar(v)
    return meta, text[m.end():]
class Ctx:
    def __init__(self, root):
        self.root = root; self._cache = {}
        self.tracked = self.git("ls-files").split("\n") if self.git("rev-parse", "--is-inside-work-tree") == "true" else []
        self.tracked = [t for t in self.tracked if t]
    def git(self, *args, cwd=None):
        p = subprocess.run(["git", "-C", cwd or self.root, *args], capture_output=True, text=True, encoding="utf-8")
        if p.returncode != 0: raise GitError(p.stderr.strip())
        return p.stdout.strip()
    def exists(self, rel): return os.path.exists(os.path.join(self.root, rel))
    def text(self, rel):
        if rel not in self._cache:
            p = os.path.join(self.root, rel)
            self._cache[rel] = open(p, encoding="utf-8").read() if os.path.isfile(p) else None
        return self._cache[rel]
    def head_text(self, rel):
        try: return self.git("show", f"HEAD:{rel}")
        except GitError: return None
    def md_texts(self, prefixes=()):
        return {r: self.text(r) for r in self.tracked if r.endswith(".md") and (not prefixes or r.startswith(tuple(prefixes)))}
GENERATED_HEADER = "<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->"
class Day1Exemption:
    def __init__(self, key, reason, released, registered):
        self.key, self.reason, self.released, self.registered = key, reason, released, registered
```

`__main__.py`：`argparse` 子命令 `generate／check／lint／rules／errata／test`；`rules` 再收 `emit --scope S --format {text,js}`；未實作的子命令先回 `print("尚未實作", file=sys.stderr); return 2`（Task 8／9 回填）；`test` 子命令：`sys.path.insert(0, tools 目錄)`、discover `docsync/tests`、失敗回 1。檔尾 `if __name__ == "__main__": sys.exit(main(sys.argv[1:]))`；`python3 tools/docsync …` 以目錄執行時 `sys.path[0]` 為 `tools/docsync` 本身，故 `__main__.py` 首段 `sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))` 再 `from docsync import …`。

- [ ] **Step 4: 跑測試確認通過**

Run: `python3 tools/docsync test`
Expected: `Ran 4 tests … OK`，退出碼 0

- [ ] **Step 5: Commit**

```bash
git add tools/docsync
git commit -m "feat(docsync): package 骨架——Finding／Ctx／frontmatter／CLI／test 入口（§4.4）"
```

---

### Task 2: RULES.md 首版＋rules.py（解析、emit、版本串、GT-08 RULES 側）＋ADR-00004

**Files:**
- Create: `docs/ops/RULES.md`、`docs/arc42/decisions/ADR-00004-rules-first-edition-and-budgets.md`
- Create: `tools/docsync/rules.py`、`tools/docsync/tests/test_rules.py`

**Interfaces:**
- Produces: `parse_rules(text) -> (header: dict, rows: list[Rule])`，`Rule` 具 `id, rule, scopes:set[str], carrier, source`；`rules_version(text) -> str`（12 hex）；`emit(text, scope, fmt="text") -> str`；`gt_08(ctx)`（本 Task 只做 RULES 側三腿：欄位形制、上限、source 指向存在；LESSONS 側在 Task 5 補）。
- RULES.md 表形（GT-08 解析錨＝以 `| RL-` 起的表列）：

```
<!-- next: RL-0047 -->
# RULES — 規則層

權威鏈：constitution ＞ ADR accepted ＞ RULES ＞ arc42／c4／compliance／process ＞ generated（與 accepted ADR 衝突＝就地改 RULES）。
上限（D8；ADR-00004）：總 58｜implementer 26｜review 10｜fix 14｜主線 34｜人 15。scope 可多值、逗號分隔。
carrier ∈ prompt／lint／checklist；source ∈ LL-NNNNN／ADR-NNNNN／rev5:L-NNN／rev5:ADR 00NN。

| id | 規則 | scope | carrier | source |
|---|---|---|---|---|
| RL-0001 | 拍板級條目施工前先查拍板紀錄；查無即先問。勘誤一律以 `docsync errata` 機器枚舉全 repo 逐處處置，自擬樣式只取最短公共子串。 | 主線,implementer | prompt | rev5:L-003 |
```

- [ ] **Step 1: 起草 RULES.md 全表（人寫；候選來源與去重法）**

候選集＝`tmp/rev5-handoff/rev5-rules-digest.md` 的 30 條已晉升＋4 條候選＋2 條「無」＋RAD-AI adoption-guide §7～§8 八條（全部中文改寫）＋啟動書 §3.8 末段「文件治理程序條款移 RULES」六條。去重規則：同一防法只留一列、`source` 取最早的 rev5:L 號（被併入者列於 ADR-00004 附表）。首版條目（規則句已改寫為命令句、無刀名）：

| id | 規則（節錄要旨） | scope | carrier | source |
|---|---|---|---|---|
| RL-0001 | 拍板級先查紀錄、查無先問；勘誤走 errata 機器枚舉（併 L-058） | 主線,implementer | prompt | rev5:L-003 |
| RL-0002 | 世代字串掃描同列三形、先證樣式集完備再證零命中 | implementer,主線 | prompt | rev5:L-006 |
| RL-0003 | 凡寫「一律 X」先問反向情境；存在即雙向寫並給機器判準 | 人,主線 | checklist | rev5:L-008 |
| RL-0004 | 狀態欄不跨角色複用；fix 迴圈跑滿必有確認輪 | 主線 | prompt | rev5:L-011 |
| RL-0005 | 子庫 git 一律 `git -C <子庫>`；破壞性驗證逐項還原後 `status --porcelain` 確認 | implementer,fix | prompt | rev5:L-012 |
| RL-0006 | 單元收尾先落帳（BACKLOG／LESSONS append＋tasks 全勾）再 generate | 主線 | checklist | rev5:L-018 |
| RL-0007 | 非零退出先看首行：`error:`＝工具層、`FAILED`／`panicked`＝測試層 | implementer,fix | prompt | rev5:L-021 |
| RL-0008 | 派發前逐 task 問「它 import／呼叫／宣告的東西存在嗎」；blocked 先判清單缺口 | 主線 | checklist | rev5:L-022 |
| RL-0009 | resume 續跑的冒煙改看最新 agent 檔（mtime＋本輪新字串） | 主線 | checklist | rev5:L-023 |
| RL-0010 | resume 只用於故障續跑；重跑某階段＝新開只跑該階段的 workflow | 主線 | checklist | rev5:L-027 |
| RL-0011 | 改變數字／集合／方向／名稱／權威＝grep 枚舉全 repo 逐處回報；清單外依分值升級；史述保留、現在式改對 | implementer,fix,review | prompt | rev5:L-032 |
| RL-0012 | status 分 blocked／done_with_escalation；只有 blocked 立即 return | implementer,fix | prompt | rev5:L-035 |
| RL-0013 | 棄案論證寫完必對所選方案跑同一反例 | 人,主線 | checklist | rev5:L-037 |
| RL-0014 | 允許檔清單答「碰得到什麼」：對實碼查值域／建構點／消費者、納入連動釘值測所在檔、寧可多列（併 L-052） | 主線 | checklist | rev5:L-042 |
| RL-0015 | 預告必標成預告並附回填義務；活書家族零未來式 | implementer,review | lint | rev5:L-043 |
| RL-0016 | launch 被擋即 TaskStop 已 armed 看門狗，重發帶 runId 重掛 | 主線 | checklist | rev5:L-049 |
| RL-0017 | 完成通知一到立即 TaskStop 看門狗 | 主線 | checklist | rev5:L-051 |
| RL-0018 | 冒煙 token 置於所有 prompt 共用段、渲染斷言一併檢查 | 主線 | checklist | rev5:L-057 |
| RL-0019 | 暫改真檔驗紅後以存原文寫回還原、禁整檔 checkout；還原後 `git diff --name-only` 證零殘留 | implementer,fix | prompt | rev5:L-060 |
| RL-0020 | ops 帳本寫「本刀 U2」形，不寫裸刀號 | implementer,主線 | prompt | rev5:L-067 |
| RL-0021 | 變異紅證必印 skipped=0；探針就地變異、不自 repo 外載入 | implementer | prompt | rev5:L-073 |
| RL-0022 | 限定式清單項附「限定外改動＝清單外、走 done_with_escalation」；主線復核看 `git diff` 實際改動面 | 主線,fix | prompt | rev5:L-075 |
| RL-0023 | 枚舉命中逐行剝 token 再判、不 `grep -v` 整行；筆數要有第二來源對賬 | implementer,fix | prompt | rev5:L-076 |
| RL-0024 | 對賬 schema 真源用腳本比 {欄名:可空性}，可空性以 migration／entity 為準 | implementer | prompt | rev5:L-077 |
| RL-0025 | fix 對 done_with_escalation＋零改動當場 return 升級，置於零改動偵測之前 | 主線 | prompt | rev5:L-078 |
| RL-0026 | 驗「呼叫處恰 N 處」取三形聯集或改名讓編譯器列出；處數型驗收由測試釘 | implementer,review | prompt | rev5:L-079 |
| RL-0027 | 連動面盤點數字釘與名冊釘並行；新增檔的單元早跑全量測試 | implementer,主線 | prompt | rev5:L-080 |
| RL-0028 | prompt 事實接地每條附出處、明令與碼衝突以碼為準回報 | 主線 | checklist | rev5:L-081 |
| RL-0029 | 變異注入前先讀 detector 排除條件；未紅先印 scanned/hits 自證進入受檢面 | implementer | prompt | rev5:L-082 |
| RL-0030 | 動工或 triage 前復核 BACKLOG 條目技術前提；前提與價值判斷分寫、前提帶出處 | 人,主線 | checklist | rev5:L-083 |
| RL-0031 | 走查還原：清理面含審計欄；還原值自本次 baseline 現讀（併 L-086） | implementer | prompt | rev5:L-084 |
| RL-0032 | 寫驅動件／量測件／編排骨架前先 `ls -R tmp/` 與既有工件；枚舉先用 errata（併 L-085） | 主線 | checklist | rev5:L-087 |
| RL-0033 | 走查回報「無可觀察實例」須附機器反證（psql／grep／原文行號），否則 redo | review | prompt | rev5:L-054 |
| RL-0034 | 文件擴充分階段導入：先可見性、再深度；不一次填滿全部項目 | 人 | checklist | ADR-00004 |
| RL-0035 | 模板是起手結構不是表單：每節依實況寫，無實體即一句「目前無」附理由，不填樣板文 | implementer,review | lint | ADR-00004 |
| RL-0036 | 系統層 AI 元件文件由其建置者填寫；無建置者即標不適用 | 人 | checklist | ADR-00004 |
| RL-0037 | 每個 AI 元件至少一條可量測品質情境（來源／刺激／環境／回應、含門檻與期限） | implementer | checklist | ADR-00004 |
| RL-0038 | 文件更新綁定收刀與部署流程：換模、換規則版本即更新名冊與情境 | 主線 | checklist | ADR-00004 |
| RL-0039 | 記錄跨元件相依與連鎖漂移；不孤立描述單一元件 | implementer | checklist | ADR-00004 |
| RL-0040 | 文件深度依風險分級；低風險元件只做可見性層 | 人 | checklist | ADR-00004 |
| RL-0041 | 文件 frontmatter 帶 `rad_ai_map` 對照鍵；正文子節名中文改寫；對照表由 generate 產、不手維護 | implementer | lint | ADR-00004 |
| RL-0042 | 一切書面產物一律 zh-TW；agent prompt 必含該字面 | 主線,implementer,review,fix | prompt | ADR-00004 |
| RL-0043 | review agent 只讀不寫 repo 檔；findings 只放回傳訊息 | review | prompt | ADR-00003 |
| RL-0044 | push／merge 需 user 明確同意；tasks 不排入 push／merge | 主線,人 | prompt | ADR-00003 |
| RL-0045 | rust build／test 容器內、全程 serial；完工前 `cargo fmt --all` | implementer,fix | prompt | rev5:ADR 0057 |
| RL-0046 | 引前代編號一律帶 `rev5:`／`rev4:` 前綴；rev6 新形原生；裸刀號禁 | implementer,review,主線 | lint | rev5:ADR 0012 |
| RL-0047 | 文件權威鏈 constitution ＞ ADR ＞ RULES ＞ 活書家族 ＞ generated；RULES 與 accepted ADR 衝突＝就地改 RULES | 人,主線 | checklist | ADR-00003 |
| RL-0048 | 時態分離：活書家族現在式、未來式住 ops、過去式住 git＋events；完成即刪 | implementer,review | lint | ADR-00004 |
| RL-0049 | 三材質各有唯一的家；鏡像不是機器生成就是不存在；generated 禁手改 | implementer,主線 | lint | ADR-00004 |
| RL-0050 | ID 配號取檔頭 next-id 後 bump、號碼永不回收 | implementer,主線 | lint | rev5:ADR 0012 |
| RL-0051 | 每條閘一正一反自證、掃描面空集合即紅；Day-1 豁免逐筆帶解除謂詞、到期即紅 | implementer,review | lint | rev5:ADR 0024 |
| RL-0052 | 數量預算超限只擋新增、不可調數字；一進一出或走 ADR；波 6 前 WARN、之後 ERROR | 主線,人 | lint | ADR-00004 |
| RL-0053 | 收刀簿記＝events append→NOTES→generate 一顆 commit，排在 merge 之後 | 主線 | checklist | ADR-00004 |

實算：53 條 → 上限 ceil(53×1.25)＝67；per-scope 上限＝各 scope 實數 ×1.25 進位（起草完由 Step 4 的測試印出實數後回填檔頭；上表 scope 分布為草案、最終以檔為準）。`RL-0053` 之後 `<!-- next: RL-0054 -->`。另附 `## 名詞` 段（刀＝spec-kit feature；單元＝一支 Workflow 執行單元；收刀＝merge --no-ff 後簿記；輕量軌＝不開 SDD 的維護批；拍板級＝schema／scope／破紀律／user 可見行為）。

- [ ] **Step 2: 寫失敗測試（解析、上限、source 形、emit、版本串）**

```python
# tools/docsync/tests/test_rules.py
import unittest
from docsync import rules, common
GOOD = """<!-- next: RL-0003 -->
# RULES
上限（D8）：總 3｜implementer 2｜主線 2。

| id | 規則 | scope | carrier | source |
|---|---|---|---|---|
| RL-0001 | 先查紀錄。 | 主線,implementer | prompt | rev5:L-003 |
| RL-0002 | 只讀不寫。 | implementer | prompt | ADR-00003 |
"""
class TestParse(unittest.TestCase):
    def test_rows_and_caps(self):
        hdr, rows = rules.parse_rules(GOOD)
        self.assertEqual(hdr["next"], 3); self.assertEqual(hdr["caps"]["總"], 3); self.assertEqual(hdr["caps"]["implementer"], 2)
        self.assertEqual([r.id for r in rows], ["RL-0001", "RL-0002"]); self.assertEqual(rows[0].scopes, {"主線", "implementer"})
    def test_emit_scope_and_version(self):
        out = rules.emit(GOOD, "implementer")
        self.assertIn("RL-0001｜先查紀錄。", out); self.assertIn("RL-0002｜只讀不寫。", out)
        self.assertTrue(out.rstrip().endswith("RULES-VERSION: " + rules.rules_version(GOOD)))
        self.assertNotIn("RL-0002", rules.emit(GOOD, "主線"))
        self.assertEqual(len(rules.rules_version(GOOD)), 12)
    def test_js_format(self):
        js = rules.emit(GOOD, "implementer", fmt="js")
        self.assertTrue(js.startswith("// 機器生成：python3 tools/docsync rules emit"))
        self.assertIn("RULES-VERSION: " + rules.rules_version(GOOD), js)
class TestGt08RulesSide(unittest.TestCase):
    def _ctx(self, text):
        c = common.Ctx.__new__(common.Ctx); c.root = "/nonexistent"; c.tracked = ["docs/ops/RULES.md"]; c._cache = {"docs/ops/RULES.md": text}
        c.exists = lambda rel: rel in ("docs/ops/RULES.md", "docs/arc42/decisions/ADR-00003-x.md")
        return c
    def test_green(self):
        self.assertEqual([f for f in rules.gt_08(self._ctx(GOOD)) if f[0] == "ERROR"], [])
    def test_over_cap_and_bad_source(self):
        bad = GOOD.replace("總 3", "總 1").replace("rev5:L-003", "L-003")
        codes = {f[3][:6] for f in rules.gt_08(self._ctx(bad)) if f[0] == "ERROR"}
        self.assertTrue(any("超出上限" in f[3] for f in rules.gt_08(self._ctx(bad))))
        self.assertTrue(any("source 形制" in f[3] for f in rules.gt_08(self._ctx(bad))))
    def test_empty_face_is_red(self):
        c = self._ctx(""); c.exists = lambda rel: False
        self.assertTrue(any("掃描面空集合" in f[3] for f in rules.gt_08(c)))
```

- [ ] **Step 3: 跑測試確認失敗**

Run: `python3 tools/docsync test`
Expected: FAIL（`docsync.rules` 不存在）

- [ ] **Step 4: 實作 rules.py**

```python
"""守 RL-0049／RL-0052：RULES 為規則層唯一家；數量預算只擋新增。"""
import hashlib, re
from . import RULES, ADR_DIR
from .common import ERROR, WARN, finding
RE_NEXT = re.compile(r"<!--\s*next:\s*RL-(\d{4})\s*-->")
RE_CAPS = re.compile(r"上限[^：]*：([^\n]+)")
RE_ROW = re.compile(r"^\|\s*(RL-\d{4})\s*\|\s*(.+?)\s*\|\s*([^|]+?)\s*\|\s*(prompt|lint|checklist)\s*\|\s*([^|]+?)\s*\|\s*$", re.M)
RE_SOURCE = re.compile(r"^(LL-\d{5}|ADR-\d{5}|rev5:L-\d{3}|rev5:ADR \d{4})$")
SCOPES = ("implementer", "review", "fix", "主線", "人")
class Rule:
    def __init__(self, id, rule, scopes, carrier, source): self.id, self.rule, self.scopes, self.carrier, self.source = id, rule, scopes, carrier, source
def parse_rules(text):
    hdr = {"next": None, "caps": {}}
    m = RE_NEXT.search(text or "")
    if m: hdr["next"] = int(m.group(1))
    c = RE_CAPS.search(text or "")
    if c:
        for part in re.split(r"[｜|]", c.group(1)):
            mm = re.match(r"\s*(\S+?)\s*(\d+)\s*[。．]?\s*$", part)
            if mm: hdr["caps"][mm.group(1)] = int(mm.group(2))
    rows = [Rule(g[0], g[1], {s.strip() for s in g[2].split(",") if s.strip()}, g[3], g[4].strip()) for g in RE_ROW.findall(text or "")]
    return hdr, rows
def _canonical(rows): return "\n".join(f"{r.id}|{r.rule}|{','.join(sorted(r.scopes))}|{r.carrier}|{r.source}" for r in sorted(rows, key=lambda r: r.id))
def rules_version(text): return hashlib.sha256(_canonical(parse_rules(text)[1]).encode("utf-8")).hexdigest()[:12]
def emit(text, scope, fmt="text"):
    _, rows = parse_rules(text); ver = rules_version(text)
    sel = [r for r in rows if scope in r.scopes]
    body = "\n".join(f"{r.id}｜{r.rule}" for r in sel)
    block = f"=== RULES scope={scope}（{len(sel)} 條）===\n{body}\nRULES-VERSION: {ver}\n"
    if fmt == "text": return block
    esc = block.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return ("// 機器生成：python3 tools/docsync rules emit --scope %s --format js——嚴禁手改；差異由 pre-commit check 攔下\n"
            "const RULES_BLOCK = `%s`;\nconst RULES_SCOPE = '%s';\n" % (scope, esc, scope))
def gt_08(ctx):
    """GATE:
      id=GT-08
      rule=RL-0049
      source=rev5:ADR 0024
      drift=RULES↔LESSONS 對賬、規則數量預算
      scope=docs/ops/RULES.md；docs/ops/LESSONS/*.md；docs/ops/LESSONS.md
      trigger=pre-commit
      rc=1
      breaks-if-removed=規則層可無來源、可超上限、教訓可不指向規則
    """
    out = []; text = ctx.text(RULES)
    if not text: return [finding(ERROR, "GT-08", RULES, "掃描面空集合：RULES.md 缺席或空檔——規則層首版必須存在")]
    hdr, rows = parse_rules(text)
    if hdr["next"] is None: out.append(finding(ERROR, "GT-08", RULES, "缺 next-id 檔頭（<!-- next: RL-NNNN -->）"))
    if not rows: out.append(finding(ERROR, "GT-08", RULES, "掃描面空集合：零規則列"))
    for r in rows:
        if not RE_SOURCE.match(r.source): out.append(finding(ERROR, "GT-08", f"{RULES}｜{r.id}", f"source 形制不合「{r.source}」（LL-NNNNN／ADR-NNNNN／rev5:L-NNN／rev5:ADR 00NN）"))
        elif r.source.startswith("ADR-") and not any(p.startswith(f"{ADR_DIR}/{r.source}-") for p in ctx.tracked) and not _adr_file_exists(ctx, r.source):
            out.append(finding(ERROR, "GT-08", f"{RULES}｜{r.id}", f"source 指向不存在的 {r.source}"))
        if not r.scopes - set(SCOPES) == set() : out.append(finding(ERROR, "GT-08", f"{RULES}｜{r.id}", f"scope 值域外：{sorted(r.scopes - set(SCOPES))}"))
        if len(r.rule.splitlines()) > 2: out.append(finding(ERROR, "GT-08", f"{RULES}｜{r.id}", "規則句超過 2 行"))
    caps = hdr["caps"]; level = ERROR  # 波判準由 gates.gt_12 統一；本閘只報「超出上限」事實、層級由呼叫端依波換算
    if caps.get("總") is not None and len(rows) > caps["總"]: out.append(finding(WARN, "GT-08", RULES, f"超出上限：總 {len(rows)} > {caps['總']}（D8 只擋新增）"))
    for s in SCOPES:
        n = sum(1 for r in rows if s in r.scopes)
        if caps.get(s) is not None and n > caps[s]: out.append(finding(WARN, "GT-08", RULES, f"超出上限：{s} {n} > {caps[s]}"))
    return out
def _adr_file_exists(ctx, adr_id):
    import os
    d = os.path.join(ctx.root, ADR_DIR)
    return os.path.isdir(d) and any(n.startswith(adr_id + "-") for n in os.listdir(d))
```

（測試的 `_ctx` 以 `exists` 樁替代目錄掃描：實作 `_adr_file_exists` 先試 `ctx.exists(f"{ADR_DIR}/{adr_id}-x.md")` 樁、再落真目錄掃描；兩腿都寫。）

- [ ] **Step 5: 跑測試確認通過；以真檔實算條數與 per-scope 數回填檔頭上限**

Run: `python3 tools/docsync test && python3 - <<'EOF'
import sys; sys.path.insert(0,'tools'); from docsync import rules
t=open('docs/ops/RULES.md',encoding='utf-8').read(); h,r=rules.parse_rules(t)
import math; print('總',len(r),'→上限',math.ceil(len(r)*1.25))
for s in rules.SCOPES: n=sum(1 for x in r if s in x.scopes); print(s,n,'→',math.ceil(n*1.25))
EOF`
Expected: 全綠；印出各實數，據以改 RULES.md 檔頭「上限」行與 ADR-00004 數值。

- [ ] **Step 6: 寫 ADR-00004（accepted；user 於本 Task 檢視 RULES 表後確認）**

frontmatter 照 ADR-00001 形（id/title/date/status/supersedes/superseded_by/provenance/tags）。body：背景（§3.6、D8、R2-F12／F13；候選來源三處）／決策驅動因子／考慮過的替代案（照搬 rev5 CLAUDE.md 全段＝通道重塞滿；只收 RAD-AI 八條＝丟失 rev5 已驗證防法）／決定（首版 53 條；上限總 N 與 per-scope；去重併入表：L-058→RL-0001、L-052→RL-0014、L-086→RL-0031、L-085→RL-0032）／後果（GT-08 首值、emit 進骨架、CLAUDE.md §2 規則句改指針）／翻案觸發器（連續兩刀 emit 塊超過 prompt 預算或 scope 上限被撞三次＝重審上限）。

- [ ] **Step 7: Commit**

```bash
git add docs/ops/RULES.md docs/arc42/decisions/ADR-00004-rules-first-edition-and-budgets.md tools/docsync/rules.py tools/docsync/tests/test_rules.py
git commit -m "feat(rules): RULES.md 首版 53 條＋上限實算（ADR-00004）；docsync rules 解析／emit／RULES-VERSION／GT-08 RULES 側"
```

---

### Task 3: events.py——rev6 事件 schema、GT-02、GT-03、三指標；創世事件

**Files:**
- Create: `tools/docsync/events.py`、`tools/docsync/tests/test_events.py`、`docs/ops/events.jsonl`

**Interfaces:**
- Produces: `parse_events(text) -> (events: list[dict], errors: list[(lineno, msg)])`；`EVENT_SCHEMAS`；`gt_02(ctx)`；`gt_03(ctx)`；`metrics(events) -> dict` 鍵 `gov_ratio`／`lessons_dup_rate`／`backlog_net`，值為 `float|int|"n/a"`；`RE_SHA, RE_BID, RE_LID, RE_ADR, RE_FEATURE, RE_DATE`。
- schema（必填／選填）：
  - feature_close：type,date,feature,summary,merge,pins{web,api},adrs[ADR-NNNNN],arch_impact("none"|["§N"…]),backlog_add[BL-NNNNN],backlog_done[BL-NNNNN],window(int≥1)／選填 notes,kind(vertical|horizontal),spec_supersessions
  - misc：type,date,summary,category(product|governance),backlog_add[]／選填 notes,backlog_done[],merge(SHA),workflow
  - review：type,date,scope,report(路徑),findings{total,fixed,to_backlog[],wontfix_adr[]}／選填 feature
  - erratum：type,date,target_line(int≥1),field(merge|pins.web|pins.api|commit),corrected(SHA),reason
  - perf：type,date,kind(close_bookkeeping|precommit_chain),wall_s(>0),notes／選填 rc,commit(SHA)
  - 共通：summary 單行 ≤300 字；date `YYYY-MM-DD`；jsonl 無空行、行界只認 `\n`。

- [ ] **Step 1: 寫失敗測試**

```python
# tools/docsync/tests/test_events.py
import json, unittest
from docsync import events
def ev(**k): return json.dumps(k, ensure_ascii=False)
MISC = ev(type="misc", date="2026-09-03", summary="s", category="governance", backlog_add=[])
class TestSchema(unittest.TestCase):
    def test_good_misc(self):
        evs, errs = events.parse_events(MISC + "\n"); self.assertEqual(errs, []); self.assertEqual(evs[0]["category"], "governance")
    def test_misc_requires_category_and_backlog_add(self):
        _, errs = events.parse_events(ev(type="misc", date="2026-09-03", summary="s") + "\n")
        self.assertTrue(any("category" in m for _, m in errs) and any("backlog_add" in m for _, m in errs))
    def test_feature_close_window_and_ids(self):
        fc = ev(type="feature_close", date="2026-09-03", feature="001-x", summary="s", merge="a"*40, pins={"web": "b"*40, "api": "c"*40},
                adrs=["ADR-00001"], arch_impact="none", backlog_add=["BL-00001"], backlog_done=[], window=1)
        self.assertEqual(events.parse_events(fc + "\n")[1], [])
        bad = fc.replace("BL-00001", "B-001").replace('"window": 1', '"window": 0')
        msgs = [m for _, m in events.parse_events(bad + "\n")[1]]
        self.assertTrue(any("BL-NNNNN" in m for m in msgs) and any("window" in m for m in msgs))
    def test_blank_line_and_unknown_type(self):
        _, errs = events.parse_events(MISC + "\n\n" + ev(type="zzz", date="2026-09-03") + "\n")
        self.assertTrue(any("空行" in m for _, m in errs) and any("未知 type" in m for _, m in errs))
class TestMetrics(unittest.TestCase):
    def test_na_without_feature_close(self):
        m = events.metrics([json.loads(MISC)], lessons=[])
        self.assertEqual(m["gov_ratio"], "n/a"); self.assertEqual(m["backlog_net"], "n/a"); self.assertEqual(m["lessons_dup_rate"], "n/a")
    def test_values(self):
        fc = json.loads(ev(type="feature_close", date="2026-09-03", feature="001-x", summary="s", merge="a"*40, pins={"web":"b"*40,"api":"c"*40},
                           adrs=[], arch_impact="none", backlog_add=["BL-00001","BL-00002"], backlog_done=["BL-00001"], window=1))
        m = events.metrics([json.loads(MISC), fc], lessons=[{"recurrence_of": "RL-0001"}, {"recurrence_of": ""}])
        self.assertEqual(m["gov_ratio"], 1.0); self.assertEqual(m["backlog_net"], 1); self.assertEqual(m["lessons_dup_rate"], 0.5)
```

（GT-02 的 SHA 實證與 pin 互證、GT-03 的收刀完整性用 Task 1 的臨時 git repo 樁測：建 repo→兩顆 commit→以真 SHA／假 SHA 各一筆事件→斷言假 SHA 紅、真 SHA 綠；GT-03 空面＝零 feature_close／review 事件時回 SKIP＋具名 Day-1 鍵 `GT-03.no-close-events`，有事件時：specs/<feature>/spec.md 缺→紅、adrs 指向不存在→紅、review.report 不存在→紅、findings 不守恆→紅。各寫一案。）

- [ ] **Step 2: 跑測試確認失敗** → Expected: ImportError

- [ ] **Step 3: 實作 events.py**（要點：`EVENT_SCHEMAS` dict `{type: {"required": (...), "optional": (...)}}`；`_check_event(e)` 照 rev5 形逐型驗、正則換 rev6 五碼／四碼；`parse_events` 逐行 `json.loads`、空行報「空行」、行界只用 `split("\n")`；`gt_02`：schema 錯誤→ERROR；SHA 實證＝`git cat-file -e <sha>^{commit}`（pins 對子庫 `git -C base-web`，子庫缺席→SKIP 具名）；pin 互證＝`git ls-files -s <sub>` 之 gitlink 與 `git -C <sub> rev-parse HEAD` 相等，否則 WARN；window 單調＝第 k 筆 feature_close 的 window 必為 k；`metrics`：gov_ratio＝misc.category=governance 數／feature_close 數（0→n/a，round 2）；lessons_dup_rate＝recurrence_of 非空／全部（零檔→n/a）；backlog_net＝最近 3 個 feature_close 窗內 Σbacklog_add−Σbacklog_done（含窗內 misc；不足 3 刀→仍計但 STATE 標「（不足 3 刀）」？——**否**：規格寫不足 3 刀 n/a；測試 `test_values` 只有 1 刀卻期望 1 → 改為：`metrics(events, lessons, min_window=3)`，測試傳 `min_window=1`；預設 3。）

- [ ] **Step 4: 建 `docs/ops/events.jsonl` 首筆（波 1 創世 misc）**

```json
{"type": "misc", "date": "2026-09-03", "summary": "rev6 波 1 創世：守門五件（49f37d2）＋源倉 gitlink（881c621）＋啟動書搬入（7f34015）＋compose 3xxxx 與 deploy 遷入（8a20aaa）＋bootstrap 凍結斷言（4c24966）＋ADR-00001/00002（a31cb54）＋機密管線首建（ce6cfff／5e8e69f）", "category": "governance", "backlog_add": [], "notes": "波 1 前段；治理工具與憲法／RULES 於後續 commit 落地"}
```

- [ ] **Step 5: 跑測試確認通過** → `python3 tools/docsync test` OK

- [ ] **Step 6: Commit**

```bash
git add tools/docsync/events.py tools/docsync/tests/test_events.py docs/ops/events.jsonl
git commit -m "feat(docsync): events schema（rev6 欄位）＋GT-02／GT-03＋三指標算式；events.jsonl 創世首筆（§4.3）"
```

---

### Task 4: adr.py——GT-04 與 DECISIONS-INDEX

**Files:**
- Create: `tools/docsync/adr.py`、`tools/docsync/tests/test_adr.py`

**Interfaces:**
- Produces: `load_adrs(ctx, head=False) -> dict[id, Adr]`（`Adr`: id,title,date,status,supersedes,superseded_by,provenance,tags,rev5_id,rad_ai,body,rel）；`gt_04(ctx)`；`gen_decisions_index(adrs, events) -> str`；`backfill_superseded_by(ctx) -> list[rel]`（generate 時回填對稱、回傳改動檔）。
- 規則：檔名 `ADR-NNNNN-<slug>.md` 且 frontmatter id 相等；status ∈ proposed／accepted／superseded；必填 id/title/date/status；HEAD 為 accepted 或 superseded 者 body 逐位元組不變（frontmatter 只允許 status accepted→superseded 與 superseded_by 增列）；supersedes 對稱且被 supersede 者 status=superseded；HEAD 有、現無＝禁刪除紅；id 與檔名數字相等；日期形制。

- [ ] **Step 1: 寫失敗測試**（臨時 git repo：commit 一份 accepted ADR → 改 body → gt_04 紅「accepted 後 body 不可變」；改 status 為 superseded 並加 superseded_by → 綠；刪檔 → 紅「禁刪除」；A.supersedes=[B] 但 B 未標 superseded → 紅「supersede 不對稱」；空目錄 → 紅「掃描面空集合」；`gen_decisions_index` 對兩份 ADR 產表、feature 欄由 events.adrs 反查、查無印「輕量軌」。）

- [ ] **Step 2: 確認失敗 → Step 3: 實作**（docstring GATE 區塊：rule=RL-0047 source=rev5:ADR 0012 drift=ADR 不可變與 supersede 對稱 scope=docs/arc42/decisions/*.md breaks-if-removed=拍板全文可被改寫、翻案可單向）→ **Step 4: 全綠** → **Step 5: Commit** `feat(docsync): adr——GT-04 不可變／對稱／禁刪除＋DECISIONS-INDEX（§3.5）`

---

### Task 5: book.py（一）——GT-05 ID 家族與跨代裸編號＋GT-08 LESSONS 側

**Files:**
- Create: `tools/docsync/book.py`、`tools/docsync/tests/test_book_ids.py`
- Modify: `tools/docsync/rules.py`（gt_08 加 LESSONS 側三腿）

**Interfaces:**
- Produces: `gt_05(ctx)`；`ID_FAMILIES = {"BL": (BACKLOG, [BACKLOG_DEFERRED]), "LL": (LESSONS_INDEX, [LESSONS_DIR/*]), "RL": (RULES, [])}`；`RE_NEXT_ID = r"<!--\s*next:\s*(BL|LL|RL)-(\d{4,5})\s*-->"`；`BARE_REV5 = re.compile(r"(?<![A-Za-z0-9:_/-])(B-\d{3}|L-\d{3}|ADR 0\d{3}|Lint\d{2}|\d{3}-[a-z][a-z0-9]*(?:-[a-z0-9]+)+)(?![A-Za-z0-9-])")`；`PRESENT_TENSE_FACE = ("docs/arc42/", "docs/c4/", "docs/compliance/", "docs/process/", "docs/ops/", "docs/generated/", "README.md", "CLAUDE.md", "tools/", "deploy/", ".githooks/", ".claude/")`；`HISTORY_FACE = ("docs/brainstorms/", "specs/", "docs/reviews/")`。
- 判準：(a) 各家族 next-id 存在、條目唯一、皆 < next、next 對 HEAD 單調、現有而 HEAD 無之號 ≥ HEAD next（不回收）；家族檔缺席→SKIP 具名 Day-1 鍵 `GT-05.ledgers-absent`（BL／LL）；RL 必在。(b) 現在式面（含 tools/、deploy/ 文字檔）命中 `BARE_REV5` 即 ERROR，除非該刀名 ∈ rev6 刀集（specs/ 子目錄名 ∪ events.feature）或為 `000-` 起首之創世史料家族（啟動書、本計畫）；史料面豁免。(c) 子庫碼面：`git -C <sub> grep -nE '(^|[^A-Za-z0-9:_-])(B-[0-9]{3}|L-[0-9]{3})([^0-9]|$)' HEAD --` 命中即 ERROR；子庫缺席→SKIP。ADR 家族：目錄檔名數字唯一且與 frontmatter 相等（GT-04 已管 id；此處只管唯一單調）。

- [ ] **Step 1: 失敗測試**：合成 BACKLOG（next 3、條目 BL-00001／BL-00002 綠；重複號紅；BL-00005≥next 紅；HEAD next 4→現 3 紅「單調」）；裸 `L-011` 在 docs/ops/x.md 紅、在 docs/brainstorms/x.md 綠、`rev5:L-011` 綠、`001-foo` 在無 specs 時紅、有 `specs/001-foo/` 時綠；子庫命中案用臨時 repo 當 base-web 樁（Ctx.git cwd 參數）。
- [ ] **Step 2/3/4**：實作＋全綠。docstring：rule=RL-0050 source=rev5:ADR 0012 drift=配號唯一單調、跨代裸編號 scope=docs/ops 三帳＋現在式文件面＋兩子庫 pin 樹 breaks-if-removed=號碼可回收、rev5 編號走私入 rev6 現在式文件。
- [ ] **Step 5: gt_08 補 LESSONS 側**：`LESSONS/LL-NNNNN-<slug>.md` 檔名↔正文首行 `LL-NNNNN｜` 相等；frontmatter `rule_id`（RL-NNNN 存在或 `none：<理由>`）與 `promotion_surface ∈ rules/gate/code/none`；`recurrence_of`（選填）指向存在的 LL 或 RL；目錄缺席→SKIP 具名 `GT-08.lessons-absent`。測試三案（合形綠／rule_id 指向不存在紅／目錄缺席 SKIP）。
- [ ] **Step 6: Commit** `feat(docsync): GT-05 ID 家族＋雙 pattern 跨代裸編號＋子庫碼面；GT-08 LESSONS 側（附錄 E）`

---

### Task 6: book.py（二）——GT-06 引用健康＋GT-11 bash 面＋errata

**Files:**
- Modify: `tools/docsync/book.py`；Create: `tools/docsync/tests/test_book_refs.py`

**Interfaces:**
- Produces: `gt_06(ctx)`、`gt_11(ctx)`、`errata_scan(ctx, keyword) -> list[(rel, lineno, line)]`（外層 tracked 文字檔＋兩子庫 `git grep`）。
- GT-06 判準：md 相對連結目標存在（`http(s)://`、`mailto:`、`#` 不驗；連結解析相對於該檔目錄）；禁 `\S+\.md:\d+`；禁 `(BACKLOG(-[A-Za-z0-9-]+)?|NOTES|STATE)\.md#`；禁 `(~|/home/[^/\s]+|/Users/[^/\s]+)/\.claude/`；活書家族（docs/arc42 非 decisions、docs/c4、docs/compliance、docs/process）時態禁詞 `待決／TBD／⏳／已完成／下一步` ERROR、預告詞 `屆時／日後／將由` WARN；活書家族缺席→SKIP 具名 `GT-06.book-absent`（其餘腿照跑）。
- GT-11 判準：面＝tracked `*.sh` ∪ 首行 shebang 含 `sh` 之檔（含 `.githooks/*`）；`\$[A-Za-z_][A-Za-z0-9_]*` 後緊接非 ASCII 字元→ERROR；shebang 白名單 `#!/usr/bin/env bash`／`#!/bin/sh`／`#!/usr/bin/env sh`／`#!/bin/bash`；面空→ERROR。

- [ ] **Step 1: 失敗測試**：連結存在綠／不存在紅；`x.md:12` 紅；`BACKLOG.md#a` 紅；`/home/u/.claude/x` 紅；活書檔含「下一步」紅、含「日後」WARN、brainstorms 含「下一步」綠；bash `"$VAR全形"` 紅、`"${VAR}全形"` 綠、`#!/usr/bin/python3` 當 shebang 之 `.sh` 紅；errata 對合成 repo 回 (rel, lineno)。
- [ ] **Step 2/3/4**：實作＋全綠。docstring GT-06：rule=RL-0048 source=rev5:ADR 0012 drift=引用斷鏈、時態混入 scope=tracked *.md；活書家族 breaks-if-removed=死連結與未來式靜默入書。GT-11：rule=RL-0051 source=rev5:L-001 drift=bash 黏字與 shebang scope=外層 tracked bash 面（含 deploy/、.githooks/）breaks-if-removed=macOS bash 3.2 unbound variable 炸在 preflight。
- [ ] **Step 5: `__main__` 接 `errata`** 子命令：印 `rel:行號：行`，零命中印「零命中」、rc 0；子庫掃描未執行（缺席）印具名警示、rc 3。
- [ ] **Step 6: Commit** `feat(docsync): GT-06 引用健康＋GT-11 bash 面＋errata（§4.2）`

---

### Task 7: book.py（三）——GT-10 文件形制閘（Day-1 豁免承載）

**Files:**
- Modify: `tools/docsync/book.py`；Create: `tools/docsync/tests/test_book_form.py`、`tools/docsync/tests/fixtures/form/`（合成 arc42／c4／compliance／process 語料各一檔）

**Interfaces:**
- Produces: `gt_10(ctx)`；常數 `FORM_FACE = ("docs/arc42/", "docs/c4/", "docs/compliance/", "docs/process/")`（arc42 排除 decisions/）、`AIV_KEYS`（附錄 G 23 鍵）、`E_SUBSECTIONS = {"E1": ("AI Components Inventory","System Boundary Diagram","Four-Part Boundary Contract","Failure Modes","External AI Dependencies"), "E2": (...八欄 Inventory 表＋Per-Model Detail Sections＋Integration with Model Cards＋Integration with Model Registry Tools), "E3": (...), "E4": (...六節), "E5": (...五 ####), "E6": (...), "E7": (...七類＋Register Entry Format＋Debt Summary Dashboard＋Review Cadence), "E8": ("Monitoring","Retraining Policy","Deployment Strategy","Rollback Policy","Incident Response")}`（英文原名只當 frontmatter `rad_ai_map` 的對照鍵，不入正文）。
- 七腿：①佔位三腿 `\*\[`、`_{5,}`、`- \[ \]`＋裸 `\[[A-Z][A-Za-z ]+\](?!\()`；②`TODO(波 N)` 只在波 N 未出口前合法（波號 ≤ 當前波：當前波＝events 內 `wave_exit` 標記？——**定案**：當前波＝`docs/ops/NOTES.md` 首行 `<!-- wave: N -->`，缺席視為 1；`TODO(波 k)` 且 k ≤ 當前波→ERROR）；③process 檔每個 `###` 子節首句含「類比張力：」；④系統層段非「目前無 AI 元件」句時，frontmatter `rad_ai_map` 的鍵集 ⊇ `E_SUBSECTIONS[E]`；⑤compliance/annex-iv-checklist.md 含全部 23 鍵且每鍵 Evidence 欄非佔位、所引 `<檔>` 存在且 `<具名表>` 標題字面命中該檔；⑥同檔 mermaid 節點標籤 ⊆ 同檔表格首欄集合；⑦`docs/c4/C4-L2-container.md` mermaid 節點 ⊇ compose 三檔 services 名（解析 `services:` 下二層鍵）；面缺席→SKIP 具名 `GT-10.doc-skeleton-absent`（解除謂詞＝`docs/arc42/01-introduction-and-goals.md` 存在）。

- [ ] **Step 1: 失敗測試**（fixtures 各腿一紅一綠：`*[待填]` 紅；`_____` 紅；`- [ ]` 紅；`[Owner]` 紅、`[link](x)` 綠；`TODO(波 1)` 於 wave 1 紅、`TODO(波 3)` 綠；process 子節缺「類比張力：」紅；rad_ai_map 少鍵紅；checklist 缺 `AIV-2h` 紅、Evidence 引不存在檔紅；mermaid 節點 `X` 不在表格紅；C4-L2 缺 `postgres` 紅（compose 樁）；面缺席 SKIP）。
- [ ] **Step 2/3/4**：實作＋全綠（解析器以拆分構造寫，避免規則定義文自撞：正則字面在測試檔以字串串接構造）。docstring：rule=RL-0035 source=ADR-00004 drift=佔位與樣板文、子項名冊、圖表對賬 scope=FORM_FACE breaks-if-removed=RAD-AI 表可空殼交卷（22/22 假滿分重演）。
- [ ] **Step 5: Commit** `feat(docsync): GT-10 文件形制閘七腿（§3.4；波 1 Day-1 豁免）`

---

### Task 8: references.py——generate／check 本體（GT-01）、STATE／MILESTONES／ports／perf

**Files:**
- Create: `tools/docsync/references.py`、`tools/docsync/tests/test_references.py`
- Modify: `tools/docsync/__main__.py`（接 generate／check）

**Interfaces:**
- Produces: `GENERATED_FILES = ("docs/generated/STATE.md","docs/generated/MILESTONES.md","docs/generated/DECISIONS-INDEX.md","docs/generated/GATES.md","docs/generated/reference/ports.md","docs/generated/reference/perf.md","tools/orchestration/_sk_rules.js")`；`compute_generated(ctx) -> dict[rel, text]`；`check_generated(ctx, computed) -> list[Finding]`（缺／多／drift 三分支，多＝`docs/generated/**` tracked 但不在名冊）；`gen_reference_ports(ctx)`（解析三檔 `ports:` 之 `"127.0.0.1:HHHHH:CCCC"` 形；輸出表 服務｜host｜容器內側｜檔；非 3xxxx 首碼→在表尾附「★非本代世代」列並由 GT-01 之外的 bootstrap 斷言擋）；`gen_reference_perf(events)`；`gen_state(ctx)`（git 段：default branch＋pins；constitution 版本（自檔尾 `**Version**:`）；帳面統計：ADR 各 status 數、RULES 條數／上限、BACKLOG 開放（缺檔印「未建」）、LESSONS 數、events 各型數；三指標；數量預算對賬表（項目｜現值｜上限｜狀態）；最近事件尾 3）；`gen_milestones(events)`（非 perf、新在前）；`cmd_generate(ctx)`（先 `adr.backfill_superseded_by` 再寫檔；冪等）；`cmd_check(ctx)`（＝GT-01；`_sk_rules.js` 由 `rules.emit(…, "implementer", "js")` 產）。

- [ ] **Step 1: 失敗測試**：ports 解析對本 repo 三檔實掃得 12 列且全 3xxxx（真檔案）；合成 compose 含 `"127.0.0.1:22080:80"` 時列入且標記；`gen_state` 對合成 ctx 印「n/a」三指標；`check_generated`：缺檔紅、多檔紅、drift 紅、全等綠；generate 兩次逐位元組相同（冪等）。
- [ ] **Step 2/3/4**：實作＋全綠；`python3 tools/docsync generate` 真跑產出七檔；`python3 tools/docsync check` rc 0。
- [ ] **Step 5: `.gitignore` 不動（generated 需 tracked）；Commit** `feat(docsync): generate／check（GT-01 本體）＋STATE／MILESTONES／DECISIONS-INDEX／ports／perf 首次重算`

---

### Task 9: gates.py——名冊、GT-07、GT-09、GT-12、Day-1 豁免、GATES.md、lint 入口

**Files:**
- Create: `tools/docsync/gates.py`、`tools/docsync/tests/test_gates.py`
- Modify: `tools/docsync/__main__.py`（接 lint）

**Interfaces:**
- Produces: `ROSTER = (gates.gt_01, events.gt_02, events.gt_03, adr.gt_04, book.gt_05, book.gt_06, gates.gt_07, rules.gt_08, gates.gt_09, book.gt_10, book.gt_11, gates.gt_12)`；`parse_gate_blocks(source_text) -> dict[id, dict]`；`derive_anchor_codes(source_text) -> set[str]`（正則 `finding\(\s*(?:ERROR|WARN|SKIP)\s*,\s*"(GT-\d{2})"`）；`DAY1_EXEMPTIONS: dict[key, Day1Exemption]`（初版六筆：`GT-03.no-close-events`、`GT-05.ledgers-absent`、`GT-06.book-absent`、`GT-08.lessons-absent`、`GT-10.doc-skeleton-absent`、`GT-12.runbook-absent`；解除謂詞皆為檔／目錄存在或事件存在）；`run_lint(ctx) -> (findings, summary_line)`（到期即紅：豁免鍵之 `released(ctx)` 為 True 仍在表→ERROR；SKIP 必列明細；末行「lint：X 錯誤／Y 警告／Z 條款跳過」）；`gen_gates_md(ctx) -> str`（欄＝§4.1 九欄；Day-1 狀態欄＝該閘有無未解除豁免鍵）；`gt_01`（呼叫 `references.check_generated`）；`gt_07`（樣式四組＋自測紅綠樣本執行期串接；值比對：SECRETS_DIR 三級解析→讀 `*.txt` 非 `CHANGE-ME` 起首值→tracked 文字檔（跳二進位：前 8KB 含 NUL）含該值即 ERROR；落點缺席→SKIP 具名）；`gt_09`（README ```text 樹解析：`├──`／`└──` 行之路徑（目錄以 `/` 結尾；含 `、` 分隔多檔者逐一拆）與 tracked `tools/**`、`deploy/**`、`.githooks/**`、`.claude/**` 雙向對賬；shebang 檔 index mode 必 100755；`.claude/settings.json` 內三支 hook 命令所指檔存在、且 `.claude/hooks/*` 每檔被引用）；`gt_12`（錨形集合 ⊆ 區塊集合；區塊 id 集合 == ROSTER id 集合 == 恰 12；三處：GATES.md id 集合、`.githooks/pre-commit` 檔頭範圍字串 `GT-01～GT-12`（半／全形波浪皆收）、`docs/ops/RUNBOOK.md` 工具表（缺席→SKIP 具名）；預算：閘數 ≤12、RULES 總／per-scope（讀 rules.gt_08 的 WARN 轉本閘統一定級）、BACKLOG 開放 ≤25；級別＝events 無 feature_close→WARN、有→ERROR）。

- [ ] **Step 1: 失敗測試**：`parse_gate_blocks` 對本 package 真原始碼得 12 鍵且必填鍵齊；`derive_anchor_codes` 對真原始碼 ⊆ 區塊集合；合成一段含 `finding(ERROR, "GT-13", …)` 的源碼→gt_12 紅「錨形不在區塊」；ROSTER 長度 12；Day-1 到期即紅（樁 released=True 仍在表→紅）；gt_07 紅綠樣本自測＋值比對（臨時 SECRETS_DIR 放值 `s3cr3tV4lue`、tracked 檔含之→紅；`CHANGE-ME-x` 值不比對）；gt_09 README 樹漏列 `tools/x.py`→紅、樹列不存在檔→紅、shebang 檔 100644→紅、settings.json 指向缺檔→紅；`run_lint` 末行格式。
- [ ] **Step 2/3/4**：實作＋全綠；docstring GT-01：rule=RL-0049 source=rev5:ADR 0052 drift=generated↔真源 scope=GENERATED_FILES；GT-07：rule=RL-0044? ——**改**：rule=RL-0051 不合；新增規則 `RL-0054｜機密實值與憑證樣式永不入版控面；佔位值不算機密`（source rev5:ADR 0003）於 Task 2 表尾（上限實算含之）；GT-09：rule=RL-0049 source=rev5:L-061 drift=接線與實檔集 scope=README 樹、tools/deploy/.githooks/.claude、settings.json；GT-12：rule=RL-0051 source=rev5:ADR 0024 drift=名冊同源與數量預算 scope=tools/docsync/*.py、GATES.md、pre-commit 檔頭、RUNBOOK。
- [ ] **Step 5: 真跑** `python3 tools/docsync lint`：預期 0 ERROR、若干 WARN／SKIP（六筆 Day-1 逐筆列明細）；`generate` 重算含 GATES.md；`check` rc 0。
- [ ] **Step 6: Commit** `feat(docsync): gates 名冊＋GT-01／07／09／12＋Day-1 豁免六筆＋GATES.md；lint 入口全鏈綠（§4.1／§4.6）`

---

### Task 10: 憲法 1.0.0（§3.8 逐條表）＋ADR-00003＋spec-kit 產物入版控

**Files:**
- Modify: `.specify/memory/constitution.md`（以 rev5 v1.10.0 為藍本重寫）
- Create: `docs/arc42/decisions/ADR-00003-constitution-1.0.0.md`
- Add to index: `.claude/skills/**`、`.specify/**`（user 決定：與憲法同批）

**逐節改寫清單（每項可核）：**
1. 標頭：「rev6-admin (fork260509-rev6) Constitution」；v1.0.0 由 rev5 v1.10.0 依啟動書 §3.8 逐條表搬入、user 親審 diff 定版（記錄＝ADR-00003）；活書改指 `docs/arc42/`（12 節＋§13）。
2. §I.1／§I.2／§I.3／§I.6：承襲；分支名 `rev6-admin-base-web`、token `rev6-inline`；內文引 rev5 ADR 一律 `rev5:ADR 00NN`（例 §I.2 之 ADR 0005、§I.6 之 rev4:ADR 0085 保留）。
3. §I.4：只留方向性四句（brainstorm→SDD→TDD→finishing；merge 回 `rev6-admin-root`；push／merge 不得早於 finishing；簿記三步）；「詳細操作＝RULES.md＋CLAUDE.md §2」。
4. §I.5 改寫：rust-api 自源倉 main `32c5254` 起全新寫；**前代＝rev5（唯讀對照）、rev4 溯源**；拷貝禁止；註解重寫為 rev6 語境、rev5 出處帶 `rev5:` 前綴；防回歸＝rev6 拍板已推翻的行為不得帶回；例外 `sea-orm-adapter`／`xdb` 整檔拷貝（承 rev5）。
5. §I.7：保留進場規則段；「已入憲行為島」段改為**承襲指針**：列 rev5 十座 A～J（名稱＋rev5 入憲 ADR：A/B/C/D/E＝rev5:ADR 0028、F＝rev5 v1.4.0～1.6.2、G＝rev5:ADR 0054、H＝rev5 v1.7.0、I＝rev5:ADR 0063、J＝rev5:ADR 0077）為各刀 brainstorm 直接輸入；島體隨刀以 MINOR Amendment 重新進場（**user 拍板項 Q2**）。
6. §I.8 新增：「AI 代理產物必經人審與機器閘；review agent 只讀；push／merge 需 user 明確同意」（反轉＝MAJOR）。
7. §II：三筆承襲，逐筆核 `tmp/rev5-handoff/rev5-adr-digest.md` 有無被翻案（grep「unknown header」「auth route」「/api」），被翻者改為現行拍板。
8. §III：fork-delta 紀律 token 改 `rev6-inline`；生成檔紀律引 `rev5:ADR 0052`；§III.1 三軌道（wrapper 前綴 `rev6-*.ts`）；§III.2 只留機制骨架＋補完判準＋表外三項宣告＋空表頭（「首批軌道隨首刀 Amendment 開立」）＋承襲指針列 rev5 八條軌道名（**user 拍板項 Q3**）。
9. §IV 九題：第 2 題 token `rev6-inline`；第 5 題「§I.5 前代＝rev5」；其餘承襲。
10. §V.1 權威鏈納 RULES：constitution ＞ ADR accepted ＞ RULES.md ＞ arc42／c4／compliance／process ＞ generated；§V.2 第 4 步 `python3 tools/docsync generate`；§V.3 承襲；Version 1.0.0｜Ratified 2026-09-03；Amendment log 只一筆 1.0.0。
11. 全檔零裸 rev5 編號（GT-05 面含 `.specify/`？——**否**：`.specify/memory/constitution.md` 加入 `PRESENT_TENSE_FACE`，本 Task 同步改 book.py 常數）。

- [ ] **Step 1: 產 diff 供 user 親審**：`diff -u ../fork260509-rev5/.specify/memory/constitution.md .specify/memory/constitution.md > tmp/constitution-1.0.0.diff`，逐節對照上表；`python3 tools/docsync lint` 對憲法零 GT-05 紅。
- [ ] **Step 2: ADR-00003**（accepted、provenance＝啟動書 §3.8＋user 親審日期；body 含逐條表摘要與 Q2／Q3 拍板結果）。
- [ ] **Step 3: user 親審通過後 Commit**（獨立 commit，含 spec-kit 產物）`docs(constitution): rev6 1.0.0 定版（§3.8 逐條表；ADR-00003）＋spec-kit 1.0.3 產物入版控`

---

### Task 11: 掃描防線——.gitleaks.toml、.githooks、.githooks-submodule、bootstrap 回填

**Files:**
- Create: `.gitleaks.toml`（自 rev5 改寫：rule id `rev6-dsn-credential-url`；allowlist 逐條以雙向突變實證後才收：①`docs/ops/events.jsonl` SHA 欄 ②啟動書 `docs/brainstorms/000-doc-architecture.md` 若實測命中）
- Create: `.githooks/pre-commit`、`.githooks/pre-push`、`.githooks/lib/scan-range.sh`、`.githooks-submodule/pre-commit`、`.githooks-submodule/pre-push`
- Modify: `tools/bootstrap.sh`（§1：hooksPath＋betterleaks 1.7.3 釘版 die 級＋兩 worktree hooksPath 指外層 `.githooks-submodule` 絕對路徑＋pre-commit／pre-push 指紋＝HEAD blob；§5：`python3 tools/docsync test`＋`check`＋`lint` 零 ERROR＋條款數斷言＝`derive_anchor_codes` 得 12）
- Modify: `README.md` 尚未存在→Task 13；本 Task 先讓 gt_09 對 `.githooks/**` 的面由 Task 13 補樹。

**pre-commit 形（承 rev5 ADR 0061 並行 harness、ADR 0044 雙錨 45／90 秒）：**
```sh
#!/bin/sh
# rev6 pre-commit：機密掃描（樣式層 betterleaks）→ docsync check（GT-01）＋lint（GT-02～GT-12）→ staged 工具自測。
# 範圍字串（GT-12 三處同源之一）：GT-01～GT-12
# …（事件型／狀態型語意、--config 顯式帶、雙錨門檻註解自 rev5 改寫、rev5 出處帶 rev5: 前綴）
```
鏈：`betterleaks git --config "$HOOK_DIR/../.gitleaks.toml" --pre-commit --staged --redact --verbose --exit-code 2`（rc 2 擋、其餘非零＝掃描器異常指向 bootstrap）→ `pc_run check python3 tools/docsync check`；`pc_run lint python3 tools/docsync lint` → staged 含 `tools/docsync/`→`pc_run docsync-test python3 tools/docsync test`；含 `tools/wf-watchdog.py`／`deploy/*.py`→各自 `test`；`pc_join`；牆鐘 >45s WARN、>90s FAIL。

- [ ] **Step 1: 先實跑 `betterleaks git --config .gitleaks.toml --no-banner --redact --verbose --exit-code 2 --log-opts=HEAD`** 對全樹史：零命中或逐條判定誤報→allowlist（每條加前跑「加豁免→rc 0、拔豁免→回到命中」雙向實證並記入 commit 訊息）。
- [ ] **Step 2: 落 hooks 檔（exec bit `git update-index --chmod=+x`）；`git config core.hooksPath .githooks`；兩 worktree `core.hooksPath` 指絕對路徑 `.githooks-submodule`。**
- [ ] **Step 3: 樁驗（承 rev5 TestGateWiring 精神、但用 shell 實跑）**：在 staged 暫放一檔含**執行期串接**的合成 DSN（shell 變數拼三段：`postgres://` 前綴、`u:p4ssw0rd` 帳密段、`@h:5432/db` 主機段；完整字面只存在於暫存檔、絕不落任何 tracked 檔或本計畫）→ `git commit` 必被擋 rc 1、訊息含 rule id；移除後 commit 通過。記錄兩次輸出於 commit 訊息。
- [ ] **Step 4: bootstrap 回填後正向 rc=0（⚠ 只剩 remote 未定）；負向：暫改 `.githooks/pre-commit` 一字元→bootstrap 指紋斷言 die；還原。**
- [ ] **Step 5: Commit** `chore(gates): 掃描防線落地——.gitleaks.toml／.githooks／.githooks-submodule＋bootstrap §1／§5 回填（GT-07 樣式層、rev5:ADR 0044／0061 承襲）`

---

### Task 12: hook 升級（RULES-VERSION 對賬）＋編排骨架改吃 rules emit

**Files:**
- Modify: `.claude/hooks/pre-workflow-gate.py`（保留 zh-TW 字面斷言；新增：自 script 抽 `RULES-VERSION: <12hex>`，缺→擋；與 `python3 tools/docsync rules emit --scope implementer` 現算版本不符→擋，訊息附「重跑 rules emit 重組骨架」）
- Modify: `tools/orchestration/README.md`（組裝法：`rules` 段＝`python3 tools/docsync rules emit --scope implementer --format js` 產物 `_sk_rules.js`，不再手維護陣列）；`tools/orchestration/_sk_rules.js` 由 generate 產（Task 8 已列入 GENERATED_FILES）；`EXAMPLE-*.mjs` 改引 `RULES_BLOCK`（把手寫十條陣列改為 `RULES_BLOCK.split('\n')` 過濾 `RL-` 起首行）；`harness-test.mjs` 十案照跑。

- [ ] **Step 1: 失敗測試**（pre-workflow-gate 以 stdin 餵 JSON `{"tool_input":{"script":"…"}}`：含 zh-TW 但缺 RULES-VERSION→rc 2 訊息含「RULES-VERSION」；版本錯→rc 2；正確→rc 0。測試住 `tools/docsync/tests/test_hook_gate.py`，以 subprocess 跑 hook。）
- [ ] **Step 2/3**：實作；`node harness-test.mjs EXAMPLE-dual-implementer.mjs` 與 single 皆十案 rc 0；`python3 tools/docsync check` 對 `_sk_rules.js` 綠。
- [ ] **Step 4: Commit** `feat(hooks): PreToolUse 升級為 RULES-VERSION 對賬；編排骨架規則段改由 docsync rules emit 產出（§3.6、R2-F21）`

---

### Task 13: README.md 首版＋CLAUDE.md 正式版（取代過渡版）

**Files:**
- Create: `README.md`（文件地圖；```text 目錄樹＝GT-09 對賬面，逐檔列 tools/、deploy/、.githooks/、.claude/ 實檔；一句參考來源「文件骨架參考 RAD-AI（Oliver1703dk/RAD-AI @ afdd36d）改寫」；「rev5 自 7eab28a 起唯讀對照」一句（ADR-00002）；三材質與權威鏈一段；快查去處）
- Modify: `CLAUDE.md`（正式版）：§1 workspace 用途與 repo 拓樸（rev6 分支長名、源倉、凍結 rev5、埠 3xxxx）；§2 feature 工作流（承過渡版，但**規則句改為指針**：「不可違反項＝`python3 tools/docsync rules emit --scope <s>` 產出塊、烤進 script、hook 對賬」；六件套與看門狗段保留）；§3 git／submodule 操作手冊（承 rev5 §3 改寫：pin 判方向、worktree、絕不 submodule update／add）；§4 文件系統規則（指針到 RULES.md、三材質、時態、ID 配號、errata、Day-1 豁免）；§5 提問／決策紀律（拍板級判準四項）；§6 硬禁令（承過渡版、去 D10 例外句）；§7 rev5 對照環境（唯讀、埠 2xxxx、走查基準指針）；行數只報表（STATE.md 印）。

- [ ] **Step 1: 寫 README 與 CLAUDE.md；`python3 tools/docsync lint` GT-09 綠（樹 ↔ 實檔集雙向）、GT-05／GT-06 綠。**
- [ ] **Step 2: Commit** `docs: README 文件地圖（GT-09 對賬面、D15 參考來源）＋CLAUDE.md 正式版取代過渡版（波 1 末）`

---

### Task 14: 波 1 出口驗收＋收單

- [ ] **Step 1: 全鏈實跑**：`bash tools/bootstrap.sh` rc 0（⚠ 僅 remote 未定）；`python3 tools/docsync test` 全綠；`lint` 0 ERROR、列出 WARN（數量預算）與 SKIP（Day-1 六筆逐筆含解除謂詞字面）；`check` rc 0；`docker compose … config` 綠。
- [ ] **Step 2: 邏輯行數預算**：`grep -vcE '^\s*(#|$)' tools/docsync/*.py` 合計 ≤4,000（測試不計）；超出即先精簡再收單。
- [ ] **Step 3: 收單簿記**：events append 一筆 misc（category=governance、backlog_add=[]、summary＝波 1 後段收單：憲法 1.0.0／RULES 首版 N 條／GT-01～12／docsync／hooks；notes 含 commit 清單）→ `python3 tools/docsync generate` → 一顆 commit（pre-commit 實跑守門、牆鐘記於 commit 訊息，perf 事件自下一顆入帳）。
- [ ] **Step 4: 回報**：GT-12 首值（閘 12／12、RULES N／上限、BACKLOG 0／25）、Day-1 六筆與解除謂詞、剩餘 ⚠、下一波（波 2 骨架）入口。

---

## Self-Review

- **Spec coverage**：§3.5（Task 4）、§3.6（Task 2／5／12）、§3.8（Task 10）、§4.1（Task 9）、§4.2 十二條（Task 3～9 逐條）、§4.3（Task 3／8）、§4.4（結構、預算 Task 14）、§4.5（bootstrap Task 11）、§4.6（Task 9）、§5 波 1 產物「rules emit」（Task 2／12）「GATES 名冊」（Task 9）「CLAUDE.md」（Task 13）、D15 README 一句（Task 13）。未涵蓋且刻意延後：`reference/rev5-blueprint-map`（波 3）、`tools/walkthrough-baseline.py`（世代 DoD、波 6 前）、`reference/agents.md`（P-E2、波 2／3）、RUNBOOK（波 2；GT-12 第三處以 Day-1 承載）。
- **Placeholder scan**：本檔無 TBD／TODO；Task 3 的 `min_window` 與 Task 7 的「當前波」判準已定案於文內。
- **Type consistency**：`finding()` 四元組；`Ctx.text/head_text/exists/md_texts/git` 全檔同名；`gt_NN(ctx)`；`rules.parse_rules/emit/rules_version`；`events.metrics(events, lessons, min_window=3)`；`references.GENERATED_FILES` 含 `_sk_rules.js`（Task 8 與 Task 12 一致）。
- **待 user 拍板（阻塞 Task 10）**：Q2 §I.7 十島島體是否全文搬入 1.0.0；Q3 §III.2 ★ 軌道表是否搬入。Task 1～9 不受影響。
