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

資料血緣 overlay（疊加於 `C4-L2-container.md`、不另畫）的規則與表；目前無 AI 元件（截至 2026-09-03）；資料源清冊、隱私流（稽核表欄位與保留期，真內容）隨首個 schema 刀填入；流程層對應＝文件血緣鏈（brainstorm→spec→ADR→events→generated）。

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
| schema 期望 | 該階段的欄集與型（真源＝`docs/generated/reference/schema.md`、隨 schema 基線刀生成） |
| 轉換 | 一句描述＋程式落點 |

### 新鮮度需求

快變事實住 `docs/generated/reference/`（generate 每 commit 重算、GT-01 零漂移）；資料庫層新鮮度＝交易即時、無批次管線；AI 資料源進場時逐列填「允許最大時距」。

### 隱私流

稽核表欄位（登入嘗試的帳號原文、真實來源 IP 非空）與保留期隨 schema 基線刀進場、與該刀 data-model 同批填入本節（啟動書把本節列為真內容）；目前零欄。

### schema 登錄

真表＝`docs/generated/reference/schema.md`（隨 schema 基線刀生成；版本＝migration 序、受管演進帳隨該刀進場）。
