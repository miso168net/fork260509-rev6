---
rad_ai: [E8]
rad_ai_map:
  Monitoring: 監測
  Retraining Policy: 再訓練政策
  Deployment Strategy: 部署策略
  Rollback Policy: 回退政策
  Incident Response: 事故應變
---
# P-E8 代理營運（流程層）

本檔以 RAD-AI E8 的形制記載代理面營運：監測（看門狗存活與保險絲、perf 引信、lint 漂移閘）、再訓練政策（換模與規則層更新觸發）、部署（規則層版本進 prompt 的發布形）、回退（治理閘改壞的回退程序）、事故應變（blocked 升級路徑）；系統層對應＝`docs/arc42/13-operational-ai-view.md`。每個子節首句標明類比張力（哪裡對得上、哪裡是硬套）。

### 監測

類比張力：部分——RAD-AI 的監測是漂移偵測；rev6 看門狗守的是存活（stall／runaway）不是漂移，漂移面由確定性閘承擔，效能面＝perf 事件。

| 面 | 機制 | 訊號 |
|---|---|---|
| 存活 | `tools/wf-watchdog.py`（與 Workflow 原子成對，RL-0061） | stall（agent 邊界間隔逾閾）、runaway（不重複 agent key 超保險絲，RL-0062） |
| 漂移 | pre-commit 閘 | GT-01 generated↔真源、GT-12 名冊同源、hook RULES-VERSION 對賬 |
| 效能 | events perf 型 | 簿記 commit 牆鐘（RL-0053）；人讀 `docs/generated/reference/perf.md` |

### 再訓練政策

類比張力：硬套——無訓練；對應的是兩種換版觸發：換模（改 `*_OPTS` 常數、名冊重算）與規則層更新（LESSONS 晉升→RULES 一列→RULES-VERSION 變→重烤 script）；兩者皆事件觸發、人決。

### 部署策略

類比張力：部分——沒有金絲雀與影子部署；「部署」＝規則層版本進 prompt 的發布形：`python3 tools/docsync rules emit --scope <s>` 產塊烤入 script、PreToolUse hook 對賬版本字面；換模同理、一次 commit 全量切換。

### 回退政策

類比張力：對得上——治理閘改壞→`git revert` 該顆＋`python3 tools/docsync generate` 重算；規則列回退→RULES-VERSION 重算、組裝成品 script 版本字面同批重烤；換模回退＝改回 `*_OPTS`；一切回退走 pre-commit 全鏈、不 `--no-verify`。

### 事故應變

類比張力：對得上——三級：`blocked`（立即回主線）／`done_with_escalation`（跑完審查連同升級項回）／stall 或 runaway（看門狗告警→TaskStop→修 script→`resumeFromRunId` 續跑，RL-0010／RL-0016）；每次事故落 LESSONS 一坑一檔、晉升為 RULES 列。
