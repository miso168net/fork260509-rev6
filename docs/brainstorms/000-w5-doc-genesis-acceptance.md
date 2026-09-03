# 波 5 文件創世驗收實作計畫（000-w5-doc-genesis-acceptance）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans 逐 Task 執行（本 session 主線自做、不派 subagent；只在 merge 時點停）。Steps 用 `- [ ]` 勾選。

**Goal:** 依啟動書 §0.3 A 六條與 §7 形完成文件創世驗收：落一份 review 報告（addressability 自評表＋DoD A 六條逐條機器證據）＋一筆 review 事件（GT-03 Day-1 豁免因此解除、同 commit 移鍵）；tmp-clean（交接包＋憲法 diff）；外層 origin 已設；波標記 bump 6。

**Architecture:** 三 Task 三 commit：T1 tmp-clean（刪前列清單、刪後自證）→ T2 報告＋review 事件＋`gates.py` 移 GT-03 豁免鍵＋活書 §11.2 一列＋README 樹一行 → T3 出口（NOTES 波標記 6、未決項只剩 `alert_webhook_url`；merge 停點）。零新機制：報告住 `docs/reviews/`（RULES 名詞段既定史料面）、事件形＝events.py 既有 review schema、分數靠 grep 可重算的判準。

**Tech Stack:** Markdown；`tools/docsync`（generate／check／lint／test；改動＝`gates.py` 刪一鍵一 helper、`events.py` 零 close 事件 SKIP→ERROR、`tests/test_events.py` 一條斷言）；git（`-F` 檔訊息）。

**Spec:** 啟動書 `docs/brainstorms/000-doc-architecture.md`（§0.3 A 六條、§4.3 三指標、§4.6 Day-1 四欄、§5 波 5 列、§7 自評形、附錄 D 未決）；波 4 計畫 `docs/brainstorms/000-w4-rad-ai-tradeoffs.md` §0.3；本檔 §0.1 四題拍板。

---

## 0. 本 brainstorm 的拍板與判斷

### 0.1 user 拍板（2026-09-03；一題一問、首選項為建議；Q4 為 grill）

| 題 | 結論 | 理由（一句） |
|---|---|---|
| Q1 驗收報告的家 | **A：`docs/reviews/20260903-doc-genesis.md`＋一筆 review 事件** | 一次性驗收（分數隨刀變）＝史料；CLAUDE.md §2 既定「獨立輪落報告＋review 事件」形；GT-03 Day-1 豁免順勢解除、Day-1 剩 GT-08 一筆 |
| Q2 tmp-clean 射程 | **A：刪 `tmp/rev5-handoff/`（15 件、1.1 MB）與 `tmp/constitution-1.0.0.diff`（94 KB）；留 session 工作檔** | 交接包原件在 `../fork260509-rev5/tmp/` 唯讀可回讀、事實已入 memory；憲法 diff 可隨時對兩份 constitution 重算；session 檔非交接材質 |
| Q3 GitHub remote | **外層 origin＝`https://github.com/miso168net/fork260509-rev6.git`（user 提供 2026-09-03；brainstorm 期間已 `git remote add`、遠端為空倉、未 push）** | 兩源倉早有 origin 且 `.gitmodules` 已指向；bootstrap 對 origin 的 ok 判準＝URL 含 fork260509-rev6；push 另行當次同意 |
| Q4（grill）流程層分數判準 | **A：硬套數 ≥ 子節數一半→1、否則 2；無專屬檔但承載於他檔→1；E5 形制備妥零實例→1**（結果 2×7、1×4） | 與 RAD-AI 量表原意對齊（1＝有節但結構套不上）；輸入＝三值計數、grep 可重算；不與 RAD-AI-MAP 的 N/N 重複 |

### 0.2 工程判斷（回報備查；grill 可翻）

1. **報告節形**（§1）：0 範圍與量表（0／1／2 中文改寫＋「不適用」）→ 1 自評表（§7 六欄）→ 2 DoD A 六條逐條（條｜機器判｜結果｜勾）→ 3 findings 三分流→ 4 tmp-clean 紀錄→ 5 remote 紀錄。史料面：不受時態與形制掃描，GT-06 連結腿掃；路徑一律反引號。
2. **流程層分數判準（可重算）**：以各流程層檔「類比張力：」三值計數為子項分數；硬套數 < 子節數一半→2、≥ 一半→1、無承載→0；無專屬檔但承載於他檔（C4-E1→P-E2 刻板型欄、C4-E2→P-E3 管線清冊表＝文件血緣鏈）→1；E5 形制備妥零實例→1；Annex IV 流程層＝不適用（§3.3：法規射程為系統）。系統層十二列一律「不適用（系統目前無 AI 元件）」附理由（證據＝RAD-AI-MAP「目前無」句）。計數（2026-09-03 實查）：P-E1 5／0／0、P-E2 1／0／3、P-E3 4／0／2、P-E4 4／0／3、P-E6 4／3／1、P-E7 5／3／2、P-E8 2／2／1、P-C4-E3 5／1／0（對得上／部分／硬套）。
3. **DoD A 六條全用機器命令取證**（§2 表列命令與預期值），報告只抄結果不抄推論；A3「三指標」＝STATE 現值 n/a 合法（零刀）、算式住 `tools/docsync/events.py` 的 `metrics`。
4. **review 事件**：`scope: doc-genesis`、`report: docs/reviews/20260903-doc-genesis.md`、findings 三分流守恆（預期 total 0；執行時若自評抓到缺口→修／BL／won't-fix 三分流、total 同步）；`feature` 欄不填（非刀）。
5. **GT-03 豁免解除＝同 commit**：review 事件一入帳，`_has_close_events` 為真、鍵仍登記即 GT-12 ERROR「已到期」；T2 同 commit 自 `gates.py` DAY1_EXEMPTIONS 刪 `GT-03.no-close-events` 與已無人用的 `_has_close_events`（`ev_mod` import 仍被 ROSTER 用、留）；`events.py` 零 close 事件的 SKIP 分支印的鍵名解除後不在名冊、只會得到「未登記 SKIP 鍵」警告→依 RL-0051「掃描面空集合即紅」改為 ERROR（與 GT-02／GT-04 空集合守衛同形；SKIP import 若因此無人用則刪）；`tests/test_events.py` 的 `test_skip_named_when_no_close_events` 改名並改斷言 ERROR，總數仍 88（`test_gates` 逐鍵泛迭代）。
6. **活書同步三處**（grill 實查：`grep -n 'GT-03／GT-08\|豁免兩筆'` 活書命中三行）：`docs/arc42/11-risks-and-technical-debt.md` ※11.1 風險列（觸發與守門欄去 GT-03）與 ※11.2 技術債列（兩筆→一筆、去處欄去「首刀收刀事件」）、`docs/process/P-E6-quality-scenarios.md` 閘可見性列現況欄（豁免兩筆→一筆）；GATES.md 由 generate 重生（Day-1 1 筆）；NOTES 的「餘兩筆」在 T3 改。
7. **README 樹加一行** `docs/reviews/`（史料面；GT-09 對賬面不含 docs、但樹列出的路徑須實存→與報告同 commit）。
8. **remote 只設不推**：origin 已於 brainstorm 設好（可逆的本機設定）；push 在 T3 merge 停點與 merge 一併問、需 user 當次同意；NOTES 不記 push 狀態、只在未決段移除 remote 一條；bootstrap 體檢預期 ⚠ 歸零。
9. **tmp-clean 自證**：刪前 `du -sh`＋`find -type f | wc -l` 存 scratchpad 並抄進報告 §4；刪後 `ls tmp/` 只剩 `compact-prompt.md`、`000-w4-progress.md`、`000-w5-progress.md`。
10. **波標記 6 後 GT-12 進 ERROR 模式**（N≥6 預算超限即紅）：出口前核 STATE 預算表八列全「內」。
11. **零 ADR**：本波無新拍板（報告形、分數判準皆一次性）；零 RULES 改動（RULES-VERSION `c7a137209e0e` 不變）；閘數恆 12。
12. **恢復點檔** `tmp/000-w5-progress.md`（gitignored）每 Task 末更新。
13. **final holistic review 在 T3**（RL-0073）；處置列入收單 commit 訊息。
14. **取證命令用儲存格形**（grill 實查）：RAD-AI-MAP「目前無」用 `| 目前無 |`（12；裸字串多算表頭說明成 13）、N/N 列用 `\| [0-9]+/[0-9]+ \|`（8）；GATES Day-1 列用 `^| GT-[0-9][0-9]\.[a-z]`（現 2、解除後 1；`^| GT-.*\.` 會把主表 11 列一起算進）；bootstrap 警示用 `^\[bootstrap\] ⚠` 行數（完成行含 WARN 字樣、不算）。
15. **自評表 13 列**＝§3.3 驗收列（E1～E8、C4-E1～E3、Annex IV 檢核表、Annex IV 十類映射；三階段與 Glossary 為非驗收列不入）。
16. **報告「對象」寫死** `rev6-admin-root @ b27b7e3`（波 1～4 收單點＝本波分支起手點；T1／T2 的改動屬驗收動作本身）。

### 0.3 波次表縮編紀錄（不改啟動書；首刀 brainstorm 以此為準）

| 波 | 啟動書原列 | 本波吸收 | 剩餘 |
|---|---|---|---|
| 5 | addressability 自評、三指標首值或 n/a、DoD A 六條逐條、tmp-clean | 全部（＋Q3 remote 設定、GT-03 豁免解除） | 無 |
| 6～ | 刀（刀序與範圍由首刀 brainstorm 定、D13） | — | 首刀 brainstorm 前先消化 BL-00002（首個 AI-ADR 開寫前）；三指標首值待三刀 |

---

## Global Constraints

- 語言：一切書面產物 zh-TW；RAD-AI 量表定義中文改寫、英文原名不入正文（D15）。
- 面：`docs/reviews/` 屬史料面（RULES 名詞段）——不受 GT-05／GT-06 時態／GT-10；GT-06 連結腿仍掃：路徑一律反引號、不放 Markdown 連結。活書一列（§11.2）受時態＋形制全掃。
- 事件：review 事件 required＝type／date／scope／report／findings；findings＝`{total, fixed, to_backlog, wontfix_adr}` 守恆；report 須為實存 .md 路徑（GT-03 腿）。
- 工具：只改 `tools/docsync/gates.py`（刪一鍵一 helper）、`tools/docsync/events.py`（零 close 事件 SKIP→ERROR 一行）、`tools/docsync/tests/test_events.py`（一條斷言）；`python3 tools/docsync test` 88 綠；lint 0 錯 0 警（跳過 1＝GT-08）；check 零漂移；閘數恆 12；docsync 邏輯行不增。
- git：分支 `000-w5-doc-genesis-acceptance`（自 `rev6-admin-root` @ b27b7e3）；commit 訊息 zh-TW、一律 `git commit -F <暫存檔>`；每步以 `git rev-parse HEAD`／`git status --porcelain` 自證；merge 與 push 需 user 當次同意；rev5 樹絕不寫入。
- 新檔（報告、目錄）先 `git add` 再 generate、再 lint。
- 環境：/mnt/d drvfs——每次 Bash 自 repo 根起手；跑過 bootstrap 後同 shell 先重新 `cd`。
- 單元收尾序：③落帳早於⑤generate；每 Task 末＝generate → `git add docs/generated docs/arc42/ARCHITECTURE.md docs/ops/LESSONS.md` → lint 全綠 → 一顆 commit。

---

## 檔案結構

```
tmp/rev5-handoff/、tmp/constitution-1.0.0.diff       刪（T1；gitignored、不入 diff）
docs/reviews/20260903-doc-genesis.md                  新；報告全文＝本檔 §1（T2）
docs/ops/events.jsonl                                 +review 事件（T2）；+misc 收單（merge 後）；+perf（隨下一顆）
tools/docsync/gates.py                                DAY1_EXEMPTIONS 刪 GT-03.no-close-events＋刪 _has_close_events（T2）
tools/docsync/events.py                               gt_03 零 close 事件分支 SKIP→ERROR（RL-0051）（T2）
tools/docsync/tests/test_events.py                    零 close 事件測試改斷言 ERROR（T2）
docs/arc42/11-risks-and-technical-debt.md             ※11.1 風險列去 GT-03；※11.2 Day-1 列 兩筆→一筆（T2）
docs/process/P-E6-quality-scenarios.md                閘可見性列現況欄 豁免兩筆→一筆（T2）
README.md                                             樹加 docs/reviews/ 一行（T2）
docs/generated/GATES.md、MILESTONES.md、STATE.md      重生（T2；T3 現在波 6）
docs/ops/NOTES.md                                     波標記 6＋現況＋下一步（首刀）＋未決只剩 alert_webhook_url（T3）
tmp/000-w5-progress.md                                恢復點（gitignored）
```

---

## 1. 報告全文草稿（T2 逐字落地、命令輸出處以執行時實值填入）

檔名 `docs/reviews/20260903-doc-genesis.md`。

```text
# 文件創世驗收（doc-genesis、2026-09-03）

範圍＝啟動書 §0.3 A 六條與 §7 addressability 自評；對象＝rev6-admin-root @ b27b7e3（波 1～4 已收單；本波分支起手點）；評估者＝主線 Claude、user 拍板。一次性驗收：分數隨刀變、日後重評另落新日期報告。

## 0. 量表（RAD-AI 三值中文改寫＋rev6 第四值）

| 值 | 定義 |
|---|---|
| 0 | 無承載：文件架構裡沒有任何節或工件能放這件事 |
| 1 | 部分：有相關節，但缺 AI 特定結構；能寫、但架構不給指引 |
| 2 | 完整：有專屬節或工件、結構與指引明確 |
| 不適用 | 系統層無 AI 元件、無物可寫；附理由、不計分（ADR-00007 F24） |

流程層分數判準（可重算）：以該檔「類比張力：」三值計數為子項分數；硬套數 < 子節數一半→2、≥ 一半→1；無專屬檔但承載於他檔→1；E5 形制備妥零實例→1。

## 1. addressability 自評（§7 形）

| RAD-AI 項目 | rev6 落點 | 系統層分數 | 流程層分數 | 子項分數（對得上／部分／硬套） | 證據 |
|---|---|---|---|---|---|
| E1 | `docs/arc42/03-context-and-scope.md` §3.3／`docs/process/P-E1-boundary.md` | 不適用（無 AI 元件） | 2 | 5／0／0（5） | RAD-AI-MAP E1 列 5/5；P-E1 四段契約表＋C4-E3 指針 |
| E2 | `05-building-block-view.md` §5.4／`P-E2-agent-registry.md`＋`docs/generated/reference/agents.md` | 不適用 | 1 | 1／0／3（4） | 託管 LLM 無版本史、模型卡、登錄工具（三節硬套附理由）；名冊生成表 15 列 |
| E3 | `06-runtime-view.md` §6.2／`P-E3-doc-pipeline.md` | 不適用 | 2 | 4／0／2（6） | 管線清冊表七階段；品質閘指針句 |
| E4 | `08-crosscutting-concepts.md` §8.5／`P-E4-responsible-agent.md` | 不適用 | 2 | 4／0／3（7） | 關注矩陣三適用三不適用附理由 |
| E5 | `09-architecture-decisions.md` §9.1／無獨立檔 | 不適用 | 1 | —（形制備妥、AI-ADR 零份） | §9.1 五子節＋欄序對映；BL-00002 記 GT-10 兩腿互斥 |
| E6 | `10-quality-requirements.md` §10.3／`P-E6-quality-scenarios.md` | 不適用 | 2 | 4／3／1（8） | 四屬性各附量測；兩條實例情境 |
| E7 | `11-risks-and-technical-debt.md` §11.3／`P-E7-agent-debt.md` | 不適用 | 2 | 5／3／2（10） | 九欄登記 21 列；未守兩列→BL-00001 |
| E8 | `13-operational-ai-view.md`／`P-E8-operations.md` | 不適用 | 2 | 2／2／1（5） | 五子節；事故三級 |
| C4-E1 | `docs/c4/C4-E1-ai-component-stereotypes.md`／P-E2 刻板型欄 | 不適用 | 1 | —（承載於 P-E2 一欄） | 五型定義表＋標註準則五條 |
| C4-E2 | `C4-E2-data-lineage-overlay.md`／P-E3 管線清冊表（文件血緣鏈） | 不適用 | 1 | —（承載於 P-E3 一表） | 六子節；資料源清冊欄定義 |
| C4-E3 | `C4-E3-non-determinism-boundary.md`／`P-C4-E3-materials-boundary.md` | 不適用 | 2 | 5／1／0（6） | 邊界介面三性質契約；信心四帶 |
| Annex IV 檢核表 | `docs/compliance/annex-iv-checklist.md` | 不適用（23 鍵逐鍵附理由） | 不適用（法規射程為系統） | — | 自評欄 23 列「不適用」；Evidence 欄所引檔與具名表由 GT-10 對賬 |
| Annex IV 十類映射 | `docs/compliance/annex-iv-mapping.md` | 不適用（映射存、無 AI 系統可套） | 不適用（同上） | — | 十類→rev6 節對照表、節號依真實點號 |

## 2. DoD A 六條（啟動書 §0.3 A）

| 條 | 機器判／命令 | 結果（執行時實值） | 勾 |
|---|---|---|---|
| A1 對照總表逐列兌現 | `python3 tools/docsync lint` GT-10 零 finding；`docs/generated/RAD-AI-MAP.md` 系統層儲存格「目前無」12、流程層 N/N 列 8；非驗收列不入表 | <實值> | ✓ |
| A2 addressability 自評 | 本報告 §1（十三列）＋`grep -c '| 不適用 |' docs/compliance/annex-iv-checklist.md`＝23 | <實值> | ✓ |
| A3 三指標落地 | `docs/generated/STATE.md` 三指標三列＝n/a（零刀）；算式＝`tools/docsync/events.py` `metrics`（資料源／窗口／空值語意寫死） | <實值> | ✓ |
| A4 核心 lint 全綠＋Day-1 逐筆謂詞 | lint 0 錯 0 警（跳過 1＝GT-08）；`docs/generated/GATES.md` 主表 12 列九欄、Day-1 表 1 列且有解除謂詞 | <實值> | ✓ |
| A5 藍本對照表零缺 | `tail -1 docs/generated/reference/rev5-blueprint-map.md`＝`缺：0｜重複：0｜未知鍵：0｜形制：0` | <實值> | ✓ |
| A6 碼制重編完成 | lint GT-05 零 finding（現在式面零裸 rev5 編號）；史料面豁免＝RULES 名詞段「後三面不受裸編號…」（GATES GT-05 掃描面同義） | <實值> | ✓ |

## 3. findings 三分流

total <n>｜修 <n>｜轉 BACKLOG []｜won't-fix ADR []（執行時填；零 finding 亦合法）。

## 4. tmp-clean 紀錄

刪前：`tmp/rev5-handoff/` <N> 檔 <size>；`tmp/constitution-1.0.0.diff` <size>。刪後 `ls tmp/`＝`000-w4-progress.md`、`000-w5-progress.md`、`compact-prompt.md`（session 工作檔、gitignored）。交接包原件仍在 `../fork260509-rev5/tmp/`（唯讀）。

## 5. remote 紀錄

外層 origin＝`https://github.com/miso168net/fork260509-rev6.git`（user 提供 2026-09-03；遠端為空倉）；兩源倉 origin 與 `.gitmodules` 既已一致；bootstrap 體檢 ok 行「外層 repo 身分」取代 ⚠。push 狀態不記帳。
```

---

## 2. DoD A 取證命令（T2 Step 2 逐條跑、實值抄入 §1 報告 §2 表）

| 條 | 命令 | 預期 |
|---|---|---|
| A1 | `python3 tools/docsync lint \| grep -c 'GT-10'`；`grep -c '| 目前無 |' docs/generated/RAD-AI-MAP.md`；`grep -cE '\| [0-9]+/[0-9]+ \|' docs/generated/RAD-AI-MAP.md` | 0；12；8 |
| A2 | `grep -c '| 不適用 |' docs/compliance/annex-iv-checklist.md` | 23 |
| A3 | `grep -c 'n/a' docs/generated/STATE.md`；`grep -n 'def metrics' tools/docsync/events.py` | 3；命中 |
| A4 | `python3 tools/docsync lint \| tail -1`；`grep -c '^| GT-[0-9][0-9] |' docs/generated/GATES.md`；`grep -c '^| GT-[0-9][0-9]\.[a-z]' docs/generated/GATES.md` | 0 錯 0 警 1 跳過；12；1（GT-08） |
| A5 | `tail -1 docs/generated/reference/rev5-blueprint-map.md` | 四項皆零 |
| A6 | `python3 tools/docsync lint \| grep -c 'GT-05'`；`grep -c '後三面不受裸編號' docs/ops/RULES.md` | 0；1 |

---

## 3. 活書三處＋README 一行＋工具三處（T2 逐字）

1. `docs/arc42/11-risks-and-technical-debt.md` ※11.2 表列：
   「| Day-1 豁免兩筆（GT-03.no-close-events、GT-08.lessons-absent） | 閘腿以豁免鍵跳過、解除謂詞具名 | 首刀收刀事件／首條 LL 檔落地同 commit 移除 |」
   改為「| Day-1 豁免一筆（GT-08.lessons-absent） | 閘腿以豁免鍵跳過、解除謂詞具名 | 首條 LL 檔落地同 commit 移除 |」。
2. `README.md` 樹在 `docs/brainstorms/` 行之後加一行（對齊同欄）：
   「├── docs/reviews/                    史料面：不定期獨立 review 報告 YYYYMMDD-<scope>.md（review 事件 report 欄指向此；首份＝文件創世驗收）」
3. `tools/docsync/gates.py`：刪 DAY1_EXEMPTIONS 的 `"GT-03.no-close-events"` 一行；刪 `def _has_close_events(ctx):` 函式（含其後空行）；`ev_mod` import 留（ROSTER 用）。
4. `docs/arc42/11-risks-and-technical-debt.md` ※11.1 風險列：「| Day-1 豁免到期未解 | 首刀收刀／首條 LL 落地時忘記解除鍵 | GT-03／GT-08 解除謂詞（檔或事件存在即到期紅）；名冊＝`docs/generated/GATES.md` |」改為「| Day-1 豁免到期未解 | 首條 LL 落地時忘記解除鍵 | GT-08 解除謂詞（檔存在即到期紅）；名冊＝`docs/generated/GATES.md` |」。
5. `docs/process/P-E6-quality-scenarios.md` 閘可見性列現況欄：「十二閘全數自證；豁免兩筆」改為「十二閘全數自證；豁免一筆」（該列其餘不動、首句類比張力不動）。
6. `tools/docsync/events.py` gt_03 零 close 事件分支：`return [finding(SKIP, "GT-03", EVENTS, "GT-03.no-close-events：零 feature_close／review 事件（Day-1；首刀收刀即解除）")]` 改為 `return [finding(ERROR, "GT-03", EVENTS, "掃描面空集合：零 feature_close／review 事件——文件創世驗收 review 事件必須存在")]`；`SKIP` 若在 events.py 內無其他用處則自 import 刪。
7. `tools/docsync/tests/test_events.py`：`test_skip_named_when_no_close_events` 改名 `test_error_when_no_close_events`、斷言改為 `any(f[0] == "ERROR" and "掃描面空集合" in f[3] for f in fs)`。

---

## 4. Tasks

### Task 1: tmp-clean（Q2 A）

- [ ] **Step 1: 刪前取證**：`du -sh tmp/rev5-handoff`；`find tmp/rev5-handoff -type f | wc -l`；`ls -la tmp/constitution-1.0.0.diff`——存 scratchpad（抄進 T2 報告 §4）。
- [ ] **Step 2: 刪**：`rm -r tmp/rev5-handoff tmp/constitution-1.0.0.diff`；`ls tmp/`＝`000-w4-progress.md`、`compact-prompt.md`（＋本波 progress 檔）。
- [ ] **Step 3: 自證零版控影響**：`git status --porcelain | wc -l`＝0（tmp gitignored）；`tmp/000-w5-progress.md` 記 T1（無 commit）。

### Task 2: 報告＋review 事件＋GT-03 豁免解除＋活書一列＋README 一行

**Files:** Create `docs/reviews/20260903-doc-genesis.md`；Modify `docs/ops/events.jsonl`、`tools/docsync/gates.py`、`tools/docsync/events.py`、`tools/docsync/tests/test_events.py`、`docs/arc42/11-risks-and-technical-debt.md`、`docs/process/P-E6-quality-scenarios.md`、`README.md`。

- [ ] **Step 1: 取證**：跑本檔 §2 六條命令、記實值。
- [ ] **Step 2: 寫報告**：本檔 §1 圍欄逐字、`<實值>` 以 Step 1 結果填、§4 以 T1 取證填；`git add docs/reviews/`。
- [ ] **Step 3: 事件**：append `{"type":"review","date":"2026-09-03","scope":"doc-genesis","report":"docs/reviews/20260903-doc-genesis.md","findings":{"total":0,"fixed":0,"to_backlog":[],"wontfix_adr":[]},"notes":"文件創世驗收：DoD A 六條全勾、§7 自評十二列（系統層全不適用、流程層 2×8／1×3）；GT-03 Day-1 豁免同 commit 解除。"}`（findings 依實際三分流調整、守恆）。
- [ ] **Step 4: 工具三處＋活書三處＋README 一行**（本檔 §3 逐字）。
- [ ] **Step 5: 驗**：`python3 tools/docsync test` 88 綠；`python3 tools/docsync generate`（GATES Day-1 1 筆、MILESTONES 加 review 列、STATE events 10）；`git add docs/generated`；`python3 tools/docsync lint` 0 錯 0 警 **1 跳過**（GT-03 腿正式跑：report 存在、wontfix_adr 空）；`python3 tools/docsync check` 零漂移；`grep -c 'no-close-events\|豁免兩筆\|GT-03／GT-08' tools/docsync/gates.py tools/docsync/events.py tools/docsync/tests/test_events.py docs/generated/GATES.md docs/arc42/11-risks-and-technical-debt.md docs/process/P-E6-quality-scenarios.md` 每檔 0；`grep -c '^| GT-[0-9][0-9]\.[a-z]' docs/generated/GATES.md`＝1。
- [ ] **Step 6: Commit**（`-F` 檔）：`docs(review): 文件創世驗收報告＋review 事件；GT-03 Day-1 豁免解除（gates.py 移鍵、零 close 事件改 ERROR）；活書 Day-1 三處一筆；README 樹 docs/reviews/`；progress 檔記 T2。

### Task 3: 波 5 出口＋波標記 bump 6（merge 停點在此）

**Files:** Modify `docs/ops/NOTES.md`（首行 `<!-- wave: 6 -->`；現況＝文件創世收官：DoD A 六條✓、報告路徑、Day-1 餘 GT-08 一筆、tmp 已清、外層 origin 已設；下一步＝首刀 brainstorm（D13 刀序；rev5 藍本去處＝blueprint-map；島進場＝憲法 §I.7；首個 AI-ADR 前消化 BL-00002；三指標首值待三刀）；未決＝只剩 `alert_webhook_url`）。

- [ ] **Step 1: 出口 checklist**：①`grep -c '^| GT-[0-9][0-9]\.[a-z]' docs/generated/GATES.md`＝1 ②`python3 tools/docsync test` 88 ③lint 0 錯 0 警 1 跳過 ④check 零漂移 ⑤`bash tools/bootstrap.sh` rc 0 且 `grep -c '^\[bootstrap\] ⚠' <log>`＝0（跑完重新 `cd`）⑥STATE 預算表八列「內」（GT-12 N≥6 進 ERROR 模式前核）⑦`ls tmp/` 只剩 session 檔 ⑧RULES-VERSION `c7a137209e0e`。
- [ ] **Step 1b: final holistic review**：`git diff rev6-admin-root...HEAD --stat` 對本檔 §1～§3 逐字核；處置存 scratchpad、列入 Step 5 收單訊息（RL-0073）。
- [ ] **Step 2: NOTES 改**（波標記 6）→ generate（STATE 現在波 6）→ lint → commit：`docs(ops): 波 5 出口——波標記 6、文件創世收官、下一步＝首刀 brainstorm`。
- [ ] **Step 3: 停——merge／push 需 user 同意**（AskUserQuestion：merge --no-ff 回 rev6-admin-root、是否同時 push origin rev6-admin-root／保留分支／其他）。
- [ ] **Step 4（同意後）: merge**：訊息寫檔 → 在 rev6-admin-root `git merge --no-ff -F <檔> 000-w5-doc-genesis-acceptance` → `git log -1` 核。
- [ ] **Step 5: 簿記 commit**：misc 事件（category governance、merge 全 SHA、backlog_add `[]`、notes 含「DoD A 六條✓、review 事件、Day-1 餘 1、tmp 清、origin 已設、分支保留供 audit」）→ generate → lint → commit：`docs(ops): 波 5 收單簿記`（列 final review 處置）。
- [ ] **Step 6: perf 第四步**：量簿記 commit 牆鐘、append `close_bookkeeping` perf 事件（隨下一顆 commit 入帳）。
- [ ] **Step 7（若 user 同意 push）**：`git push -u origin rev6-admin-root`；分支 `000-w*` 與兩子庫長名分支是否一併推＝同一題內選項；push 後 `git ls-remote --heads origin` 自證。

---

## Self-Review

- **Spec coverage**：啟動書 §5 波 5 列四件（自評＝T2 §1、三指標＝A3、DoD A＝T2 §2、tmp-clean＝T1）；§0.3 A 六條逐條有命令（§2 表）；§7 六欄形（報告 §1）；F24「不適用」用法（報告 §0）；附錄 D 未決 remote（Q3、T3 NOTES）；GT-03 豁免解除（§0.2-5、T2 Step 4）。
- **Placeholder scan**：`<實值>`／`<n>`／`<N>`／`<size>`／`<T2 起手 SHA>` 為執行時填入的既定佔位、只在報告草稿圍欄內；本檔其餘零 TBD／TODO。
- **Type consistency**：報告檔名在 §1、檔案結構、T2 Step 2／3、T3 一致；review 事件欄名與 `events.py` schema 一致；Day-1 計數 2→1 在 §0.2-6、§3、T2 Step 5、T3 ① 一致（同一 grep 形）；自評表 13 列在 §0.2-15、報告 §1、A2 一致；tests 88 不變（一條改名）。
- **Risk／Guard／Rollback**：Risk＝tmp 刪除不可逆→Guard＝刪前取證入報告、原件在 rev5 tmp 唯讀→Rollback＝自 `../fork260509-rev5/tmp/` 複製回（唯讀讀取、不寫 rev5）。Risk＝GT-03 腿正式跑後對報告路徑敏感→Guard＝報告與事件同 commit、GT-03 面含 docs/reviews→Rollback＝revert 該 commit。
