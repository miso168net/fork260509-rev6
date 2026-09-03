---
rad_ai: [E6]
rad_ai_map:
  Quality Attribute Definitions: 品質屬性定義
  Model Freshness: 模型新鮮度
  Drift Tolerance: 漂移容忍
  Explainability: 可解釋
  Fairness: 公平
  Robustness: 強健
  Scenario Format: 情境格式
  Cross-Component Scenarios: 跨元件情境
---
# P-E6 品質情境（流程層）

本檔以 RAD-AI E6 的形制記載代理面品質情境：強健（review 誤報率、lint 恆綠風險、stall 恢復）、漂移容忍（docs↔code 漂移閘）、模型新鮮度（換模政策）、可解釋（findings 可追溯）、跨元件（規則層改動對多支 agent 的連鎖）；系統層對應＝`docs/arc42/10-quality-requirements.md` §10.3。每個子節首句標明類比張力（哪裡對得上、哪裡是硬套）。

### 品質屬性定義

類比張力：對得上——RAD-AI 的 AI 品質屬性在流程層換成四個可量測的屬性，各附量測與現況。

| 屬性 | 定義 | 量測 | 現況 |
|---|---|---|---|
| review 精準度 | findings 中被主線復核判「真」的比例 | 每輪三分流的「修」占比；駁回後再報須附新證據（RL-0071） | 零輪（rev6 尚未跑 Workflow） |
| 閘可見性 | 閘失效時看不看得見（恆綠風險） | 每閘一正一反自證、掃描面空集合即紅（RL-0051）；Day-1 豁免具名、到期即紅 | 十二閘全數自證；豁免一筆 |
| stall 恢復 | 從卡死到主線接手的時間 | 看門狗 stall 閾值＝agent 邊界間隔上限（RL-0017） | 零實跑 |
| 規則烤入一致性 | prompt 內規則塊與 RULES 現算版本相符 | PreToolUse hook 對賬 RULES-VERSION、不符即擋（現行版本＝`python3 tools/docsync rules emit` 末行） | 全數 script 帶版本字面 |

### 模型新鮮度

類比張力：部分——沒有訓練週期可言；新鮮度＝供應商版本＋`*_OPTS` 的換模 commit；無自動陳舊偵測，換模是人決事件（P-E8 再訓練政策）。

### 漂移容忍

類比張力：部分——RAD-AI 的漂移是統計量的容忍帶；rev6 的漂移是確定性的、容忍為零：generated 與真源不等即紅（GT-01）、名冊與實檔不等即紅（GT-09／GT-12）、規則塊版本不等即擋（hook）。

### 可解釋

類比張力：部分——模型內部不可解釋；可解釋在流程層降為可追溯：findings 帶 file×summary、駁回附理由（RL-0071）、三分流去處可查（RL-0073）。

### 公平

類比張力：硬套——同 P-E4「公平」：agent 產物不對人分類、無人群決策，不適用。

### 強健

類比張力：對得上——強健＝面對 stall／runaway／blocked／不收斂時仍能收斂或升級：六件套③保險絲與⑤收斂偵測、status 兩值（RL-0012）、確認輪（RL-0004）、harness-test 案例守編排骨架。

### 情境格式

類比張力：對得上——刺激｜環境｜回應｜量測四欄；兩條實例。

| 刺激 | 環境 | 回應 | 量測 |
|---|---|---|---|
| review 連兩輪回同一組 blocker（file×summary 相同） | fix 迴圈第 2 輪 | 判不收斂、unresolved 帶 findings 回主線 | 主線於單元邊界醒；不進第 3 輪 |
| Workflow script 缺 RULES-VERSION 或版本不符 | 主線發射 Workflow | PreToolUse hook 擋、零派發 | agent 數＝0；錯誤訊息附去處（`rules emit`） |

### 跨元件情境

類比張力：對得上——串聯漂移的流程層版本：RULES 改一列→RULES-VERSION 變→`_sk_rules.js` 重算（generate）→EXAMPLE 與真刀 script 的版本字面過期→hook 擋發射；解法＝改規則列時同批重烤（RL-0038）。
