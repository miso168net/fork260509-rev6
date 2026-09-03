---
rad_ai: [C4-E1]
rad_ai_stage: 1
rad_ai_map:
  Stereotype Definitions: 刻板型定義
  Mermaid Conventions: Mermaid 慣例
  Annotation Guidelines: 標註準則
  Template: 範本
---
# C4-E1 AI 元件刻板型

AI 元件刻板型（<<ML Model>>、<<Data Pipeline>>、<<Feature Store>>、<<Monitor>>、<<Human-in-the-Loop>> 五類、中文改寫）的標註規則與標註表；標註直接畫在 `C4-L1-system-context.md`／`C4-L2-container.md` 上、不畫第二張圖。目前無 AI 元件（截至 2026-09-03）、標註對象零；流程層對應＝agent 角色在 `docs/process/P-E2-agent-registry.md` 表以刻板型欄標註。

### 刻板型定義

| 刻板型 | 簡寫 | 意涵 | 必填性質 | rev6 目前實例 |
|---|---|---|---|---|
| ML 模型 | ML | 提供推論的端點；輸出為機率式、隨換版而變、需獨立的生命週期管理 | 模型 id 與版本、主要指標、信心區間、延遲 | 無（流程層對應＝主線／implementer／review／fix，見 `docs/process/P-E2-agent-registry.md`） |
| 資料管線 | DP | 含轉換邏輯的資料流：擷取、前處理、特徵工程、訓練編排；決定資料品質與新鮮度 | 排程或觸發型、SLA、資料品質閘 | 無 |
| 特徵庫 | FS | 共用的特徵計算與服務層；訓練與推論共用同一特徵定義 | 特徵數、更新率、消費者 | 無 |
| 監測 | MON | 漂移偵測與模型健康監測；觸發再訓練、啟動 fallback | 追蹤指標、告警門檻 | 無（流程層對應＝`tools/wf-watchdog.py`，守存活非漂移） |
| 人在迴圈 | HITL | 人工審核或覆寫的介入點；引入延遲路徑與回饋迴圈 | 觸發條件、回應 SLA | 無（流程層對應＝user 拍板與 merge 同意） |

### Mermaid 慣例

- 節點 label 不變＝同檔表格首欄字面（GT-10 圖表對賬）；刻板型不寫進 label。
- 刻板型以 `classDef` 五類（`ml`／`dp`／`fs`／`mon`／`hitl`）宣告、以 `:::<類>` 掛在節點上；同檔表加「刻板型」欄承載簡寫、模型 id 與必填性質。
- id 只用英數與底線；label 與邊文字不含半形括號類符號；不用 subgraph；不另畫第二張圖——標註直接落在 `C4-L1-system-context.md`（邊界）與 `C4-L2-container.md`（容器）。

### 標註準則

1. 何時標：容器或元件含 AI 推論、資料管線、特徵庫、漂移監測、人工審核任一者。
2. 標在哪：容器級標在 C4-L2；L1 只標確定性區域與非確定性區域的邊界（規則＝`C4-E3-non-determinism-boundary.md`）。
3. 標什麼：刻板型欄＝簡寫＋模型 id（可追溯到 arc42 §5.4 E2 名冊）＋一個關鍵指標；ML 模型另標模型間依賴；人在迴圈另標觸發條件與回應 SLA。
4. 顏色：五類各一色（`classDef` 內定義）、全 repo 一致。
5. 零實例時：本規則存檔、圖上零標註；首個 AI 功能刀進場時同批啟用（表加欄、圖加 `:::`）。

### 範本

```text
flowchart LR
  classDef ml fill:#fde2e2,stroke:#c00
  classDef dp fill:#e2f0fd,stroke:#06c
  classDef fs fill:#e8fde2,stroke:#090
  classDef mon fill:#fdf6e2,stroke:#c90
  classDef hitl fill:#efe2fd,stroke:#609
  api["rust-api"] --> model["推論服務"]:::ml
  model --> review["人工審核"]:::hitl

| 節點 | 刻板型 | 必填性質 |
|---|---|---|
| 推論服務 | ML；模型 id 與版本；主要指標 | 信心區間、延遲 |
| 人工審核 | HITL | 觸發條件、回應 SLA |
```
