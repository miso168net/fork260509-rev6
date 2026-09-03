---
rad_ai: [C4-E3]
rad_ai_stage: 2
rad_ai_map:
  Boundary Overview: 邊界總覽
  Boundary Interfaces: 邊界介面
  Confidence Thresholds: 信心門檻
  Degradation Behavior: 降級行為
  Propagation Rules: 傳播規則
  Testing Implications: 測試含意
---
# C4-E3 非確定性邊界

非確定性邊界 overlay 的規則與表；系統本體全為確定性區域、目前無 AI 元件（截至 2026-09-03）；流程層對應＝`docs/process/P-C4-E3-materials-boundary.md`（三材質即邊界）。

### 邊界總覽

系統本體全為確定性區域（目前無 AI 元件）；非確定性只存在於開發流程——Claude 執筆的產物經人審與機器閘才進入 repo（三材質邊界＝`docs/process/P-C4-E3-materials-boundary.md`）。

```mermaid
flowchart LR
  proc["開發流程"] -->|人審與機器閘| det["確定性區域"]
```

| 區域 | 內含 | 邊界 |
|---|---|---|
| 確定性區域 | rev6 系統本體全部容器（`C4-L2-container.md` 17 節點）；同輸入必同輸出 | 零 AI 越界點 |
| 開發流程 | Claude 執筆的碼、文件、帳本條目（非確定性） | 人審＋機器閘（憲法 §I.8）；細節見 P-C4-E3 |

### 邊界介面

目前無（系統）；AI 元件進場時每個越界點一列：

| 欄 | 內容 |
|---|---|
| 介面 id | 本檔配號、永不回收 |
| 自 | 確定性側元件 |
| 至 | 非確定性側元件 |
| 交換資料 | 越界的資料 |
| 三性質契約 | 信心規格／fallback 策略／降級輪廓（與 arc42 §3.3 E1 四段契約同源） |

### 信心門檻

目前無；AI 元件進場時每模型四帶各配動作：

| 帶 | 判準 | 動作 |
|---|---|---|
| 高 | 指標遠高於門檻 | 直接採用 |
| 中 | 指標接近門檻 | 採用並記錄、放寬邊界 |
| 低 | 指標低於門檻 | 啟動 fallback |
| 拒絕 | 模型不可用或指標遠低於門檻 | 只走確定性 fallback |

### 降級行為

目前無；AI 元件進場時單一元件失效與相關失效（共用依賴倒下、全模型同時 fallback）各寫一段：使用者可見影響、業務影響、可容忍最長時間、恢復程序。

### 傳播規則

| 規則 | 內容 |
|---|---|
| 信心合成 | 上游資料新鮮度或品質降級時，下游模型信心按比例扣減 |
| 串聯 fallback | 共用依賴倒下＝所有依賴模型同時 fallback |
| 模型間傳播 | 上游模型進 fallback，下游失去該訊號 |
| 確定性包覆 | 業務規則在 AI 輸出之後套硬限制、把非確定性框住 |
| 稽核完整 | 每次越界決定（採用／fallback／人工覆寫）都留痕 |

rev6 現況：零越界點；流程層的傳播規則＝非確定產物只經閘入 default branch（P-C4-E3）。

### 測試含意

系統測試全為確定性（contract test、fault-injection 隨刀進場）；AI 元件進場時加五類：門檻路由測、fallback 啟動與品質測、串聯測、恢復測、人工審核佇列量測。
