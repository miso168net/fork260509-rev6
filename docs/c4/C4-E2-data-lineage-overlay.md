---
rad_ai: [C4-E2]
rad_ai_stage: 3
rad_ai_map:
  Data Source Inventory: 資料源清冊
  Lineage Diagram: 血緣圖
  Lineage Details: 血緣明細
  Freshness Requirements: 新鮮度需求
  Privacy Flow: 隱私流
  Schema Registry: schema 登錄
---
# C4-E2 資料血緣 overlay

資料血緣 overlay（疊加於 `C4-L2-container.md`、不另畫）的規則與表；目前無 AI 元件（截至 2026-09-03）；資料源清冊＝系統資料源三項（下節）、隱私流之稽核表欄位已填於隱私流節（保留期目前無、理由同節）；流程層對應＝文件血緣鏈（brainstorm→spec→ADR→events→generated）。

### 資料源清冊

目前無 AI 資料源；系統資料源＝postgres（主庫）、redis（快取／會話）、compose 設定檔（`deploy/`），皆列於 `C4-L2-container.md` 表。清冊欄定義（AI 資料源進場時同批填）：

| 欄 | 內容 |
|---|---|
| 來源 | 系統或外部資料源名（＝C4-L2 表首欄字面） |
| 型 | 交易／事件／檔案／串流 |
| 擁有者 | 負責該資料源 schema 的域刀 |
| 新鮮度 | 允許的最大時距 |
| 隱私級 | 公開／內部／個資（稽核欄位屬個資） |

### 血緣圖

不另畫：血緣以邊疊加於 `C4-L2-container.md`，邊文字以「血緣：」前綴＋資料名；節點仍 ⊆ 該檔表首欄。目前零血緣邊。

### 血緣明細

| 欄 | 內容 |
|---|---|
| 階段 | 擷取／轉換／儲存／服務 |
| 輸入 | 上游來源（＝清冊列） |
| 輸出 | 下游消費者 |
| schema 期望 | 該階段的欄集與型（真源＝`docs/generated/reference/schema.md`——生成物、`python3 tools/docsync refresh` 照相＋generate 產） |
| 轉換 | 一句描述＋程式落點 |

### 新鮮度需求

快變事實住 `docs/generated/reference/`（generate 每 commit 重算、GT-01 零漂移）；資料庫層新鮮度＝交易即時、無批次管線；AI 資料源進場時逐列填「允許最大時距」。

### 隱私流

稽核表欄位（個資級）——變體 B append-only 稽核表恰四張（`sys_operation_log`／`sys_access_log`／`sys_login_attempt`／`session_event`；憲法 §I.6、歸屬帳＝`docs/ops/reference-src/archetype-map.json`）。主要個資載體四族（★本節只寫語意、不抄欄名——欄名與欄型正典＝`docs/generated/reference/schema.md`，該表由 `python3 tools/docsync refresh` 照相後 generate 產、隨 delta 自動前進；本節逐族指向該表對應表節即可）：①**來源 IP**——四張皆帶（前三張與 `session_event` 的欄名不同源，一律以真表為準；全庫一律 NN 承 rev5 拍板、rev6 照收）②**IP 鏈與位置**——前三張另帶傳輸層對端位址、轉發鏈原文與 GeoIP 填值三欄③**帳號原文**——`sys_login_attempt` 帶登入嘗試輸入的帳號字面一欄④**實體快照**——`sys_operation_log` 帶實體變更前後兩欄（內容隨被稽核實體而定、可含個資欄）。以上為主要載體、非窮舉。保留期：目前無——稽核表 append-only、無 retention 政策與清理排程（承 rev5 終態、rev5 留帳 `rev5:B-016`）；政策與權威釋義隨**稽核域行為島**進場回填（憲法 §I.6 變體 B 句、§I.7 島 J），執行面工件＝reaper（RUNBOOK §8、compose `jobs` profile）。

### schema 登錄

真表＝`docs/generated/reference/schema.md`（`python3 tools/docsync refresh` 照相、generate 產；版本＝migration 序（`rust-api/migration/src/`；delta 逐筆登記於受管演進帳 `docs/ops/reference-src/schema-evolution.json`））。
