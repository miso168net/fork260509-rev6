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
| A1 對照總表逐列兌現 | `python3 tools/docsync lint` GT-10 零 finding；`docs/generated/RAD-AI-MAP.md` 系統層儲存格「目前無」12、流程層 N/N 列 8；非驗收列不入表 | GT-10 finding 0；儲存格「目前無」12；N/N 列 8 | ✓ |
| A2 addressability 自評 | 本報告 §1（十三列）＋檢核表自評欄儲存格「\| 不適用 \|」計數＝23（命令見下） | 十三列（§1）；23 | ✓ |
| A3 三指標落地 | `docs/generated/STATE.md` 三指標三列＝n/a（零刀）；算式＝`tools/docsync/events.py` `metrics`（資料源／窗口／空值語意寫死） | n/a 三列；`metrics` 定義 1 處 | ✓ |
| A4 核心 lint 全綠＋Day-1 逐筆謂詞 | lint 0 錯 0 警（跳過 1＝GT-08）；`docs/generated/GATES.md` 主表 12 列九欄、Day-1 表 1 列且有解除謂詞 | 0 錯 0 警 1 跳過（GT-08）；主表 12 列；Day-1 表 1 列、謂詞＝檔存在 | ✓ |
| A5 藍本對照表零缺 | `tail -1 docs/generated/reference/rev5-blueprint-map.md`＝`缺：0｜重複：0｜未知鍵：0｜形制：0` | 缺：0｜重複：0｜未知鍵：0｜形制：0 | ✓ |
| A6 碼制重編完成 | lint GT-05 零 finding（現在式面零裸 rev5 編號）；史料面豁免＝RULES 名詞段「後三面不受裸編號…」（GATES GT-05 掃描面同義） | GT-05 finding 0；名詞段字面 1 | ✓ |

## 3. findings 三分流

total 0｜修 0｜轉 BACKLOG []｜won't-fix ADR []（六條全以機器判過、自評十三列無缺口列；零 finding）。

## 4. tmp-clean 紀錄

刪前：`tmp/rev5-handoff/` 29 檔 1.1 MB（15 個頂層項、含兩個子目錄）；`tmp/constitution-1.0.0.diff` 94,677 bytes。刪後 `ls tmp/`＝`000-w4-progress.md`、`000-w5-progress.md`、`compact-prompt.md`（session 工作檔、gitignored）。交接包原件仍在 `../fork260509-rev5/tmp/`（唯讀）。

## 5. remote 紀錄

外層 origin＝`https://github.com/miso168net/fork260509-rev6.git`（user 提供 2026-09-03；遠端為空倉）；兩源倉 origin 與 `.gitmodules` 既已一致；bootstrap 體檢 ok 行「外層 repo 身分」取代 ⚠。push 狀態不記帳。

取證命令（逐條可重跑）：

```text
python3 tools/docsync lint | grep -c 'GT-10'                       # 0
grep -c '| 目前無 |' docs/generated/RAD-AI-MAP.md                  # 12
grep -cE '\| [0-9]+/[0-9]+ \|' docs/generated/RAD-AI-MAP.md       # 8
grep -c '| 不適用 |' docs/compliance/annex-iv-checklist.md         # 23
grep -c 'n/a' docs/generated/STATE.md                             # 3
grep -c 'def metrics' tools/docsync/events.py                     # 1
python3 tools/docsync lint | tail -1                              # 0 錯誤／0 警告／1 閘跳過
grep -c '^| GT-[0-9][0-9] |' docs/generated/GATES.md              # 12
grep -c '^| GT-[0-9][0-9]\.[a-z]' docs/generated/GATES.md          # 1
tail -1 docs/generated/reference/rev5-blueprint-map.md            # 缺：0｜重複：0｜未知鍵：0｜形制：0
python3 tools/docsync lint | grep -c 'GT-05'                       # 0
grep -c '後三面不受裸編號' docs/ops/RULES.md                        # 1
```
