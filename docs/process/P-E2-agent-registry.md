---
rad_ai: [E2]
rad_ai_map:
  Model Inventory Table: 模型清冊表
  Per-Model Detail Sections: 逐模型明細
  Integration with Model Cards: 與模型卡的銜接
  Integration with Model Registry Tools: 與模型登錄工具的銜接
---
# P-E2 代理名冊（流程層）

本檔以 RAD-AI E2 的形制記載 AGT- 名冊：角色×模型×effort×最近換模日×產物進哪道閘；真源＝`tools/orchestration/` 的 OPTS 常數；系統層對應＝`docs/arc42/05-building-block-view.md` §5.4。每個子節首句標明類比張力（哪裡對得上、哪裡是硬套）。

### 模型清冊表

類比張力：對得上——名冊分兩家：角色×刻板型×產物閘是人的判斷（本表），模型與 effort 是 script 常數（生成表＝`docs/generated/reference/agents.md`、本表不重抄）。

| 角色 | 刻板型（C4-E1） | 產物 | 進哪道閘 |
|---|---|---|---|
| 主線 | ML 模型（生成型） | commit、帳本、提問 | pre-commit＋人審 |
| implementer | ML 模型 | 工作樹改動＋回傳 | review 輪；主線復核 |
| review | ML 模型（只讀） | findings | 三分流（RL-0073） |
| fix | ML 模型 | 允許清單內改動 | 次輪 review（RL-0071） |
| lens（review 形探索） | ML 模型（只讀） | findings＋coverage | 兩鏡三態（`_sk_review.js`） |
| 探針（冷啟動） | ML 模型（只讀、不帶脈絡） | 作答紀錄 | grader 評分（檢索性指標候選＝BL-00007） |
| mirror（R-real／R-decided 兩鏡） | ML 模型（只讀） | 三態 verdicts | 主線三分流（RL-0073） |
| grader（探針評分） | ML 模型（只讀） | grades＋衍生 findings | refuter 單鏡→三分流 |
| critic（完整性） | ML 模型（只讀） | gaps／unverified | 補漏 run 或 BACKLOG |
| CDP 代理 | ML 模型 | 走查回報 | 驗證審查（RL-0033） |
| 看門狗 | 監測 | stall／runaway 告警 | 與 Workflow 原子成對（RL-0061） |
| user | 人在迴圈 | 拍板、merge 同意 | 憲法 §I.8 |
| hook×3 | 無（確定性） | 擋發射／提醒 | GT-09 |

### 逐模型明細

類比張力：硬套——RAD-AI 的逐模型明細要訓練資料、評估指標、負責人；託管 LLM 這些都不可得，明細只剩 model id、effort 與換模紀錄（`*_OPTS` 的 git log），本節不另立表。

### 與模型卡的銜接

類比張力：硬套——模型卡由供應商發布、rev6 不自寫也不鏡像；需要引用時在 ADR 的 E5 形「考慮過的替代案」節指向供應商公開文件。

### 與模型登錄工具的銜接

類比張力：硬套——無 MLflow 類登錄工具；rev6 的「登錄」＝`*_OPTS` 常數＋git 歷史，生成表即登錄視圖。
