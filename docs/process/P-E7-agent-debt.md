---
rad_ai: [E7]
rad_ai_map:
  Boundary Erosion: 邊界侵蝕
  Entanglement: 糾纏
  Hidden Feedback Loops: 隱藏回饋迴圈
  Data Dependency Debt: 資料依賴債
  Pipeline Debt: 管線債
  Configuration Debt: 設定債
  Model Staleness: 模型陳舊
  Register Entry Format: 登記條目格式
  Debt Summary Dashboard: 債務總覽板
  Review Cadence: 覆審節奏
---
# P-E7 代理債務登記（流程層）

本檔以 RAD-AI E7 的形制登記 agent／編排類的坑（嚴口徑 17 條為種子）：九欄條目、條件觸發覆審；系統層對應＝`docs/arc42/11-risks-and-technical-debt.md` §11.3。每個子節首句標明類比張力（哪裡對得上、哪裡是硬套）。

### 邊界侵蝕

類比張力：對得上——agent 越出允許清單、review 寫檔、清單本身漏建，都是邊界侵蝕；rev6 以清單常數與 status 升級守。

| 債型 | 徵狀 | 來源 | 影響面 | 觸發 | 處置 | 守門 | 狀態 | 覆審條件 |
|---|---|---|---|---|---|---|---|---|
| 清單外改動 | agent 改允許清單外的檔 | rev5:L-075 | 單元產物 | 每單元 | 清單外依 status 升級、限定式項附外改條款 | RL-0022 | 已守 | 次個編排刀收刀 |
| 清單從 task 文字建 | 漏「碰得到」的檔、implementer 正確 blocked | rev5:L-042、rev5:L-052 | 派工單 | 派發前 | 對實碼查值域／建構點／釘值測 | RL-0014、RL-0027 | 已守 | 同上 |
| 清單擋自證偽修正 | 改數字後他處假述無法同批修 | rev5:L-032 | 跨檔敘述 | 改數字／集合時 | grep 枚舉、清單外升級 | RL-0011 | 已守 | 同上 |
| 派工單缺口 | task 引用不存在的東西 | rev5:L-022 | 單元起手 | 派發前 | 逐 task 問「存在嗎」 | RL-0008 | 已守 | 同上 |
| review 寫檔 | review agent 動工作樹 | rev6（憲法 §I.8） | repo | 每輪 | findings 只回訊息 | RL-0043、RL-0063 | 已守 | 同上 |

### 糾纏

類比張力：硬套——CACE（改一處全變）描述模型輸入互相牽動；rev5:L-032 的「改一個數字、多處敘述一起紅」症狀相似但機制是確定性連動（grep 可枚舉、RL-0011），不是模型糾纏；零登記列。

### 隱藏回饋迴圈

類比張力：部分——顯式迴圈（LESSONS→RULES→prompt）是設計；隱藏者＝agent 讀到自己前輪的產物而不自知。

| 債型 | 徵狀 | 來源 | 影響面 | 觸發 | 處置 | 守門 | 狀態 | 覆審條件 |
|---|---|---|---|---|---|---|---|---|
| review 沿用被駁論據 | 同一 finding 換句重報 | rev6（ADR-00004） | fix 迴圈 | 每輪 | 次輪 prompt 附前輪駁回清單 | RL-0071 | 已守 | 次個編排刀收刀 |
| 零改動被判不收斂 | fix 正確零改動（finding 在清單外）卻觸發不收斂 | rev5:L-078 | 收斂偵測 | fix 回 done_with_escalation | 升級判定置於零改動偵測之前；升級不終止 run、該段收斂帶升級項進下一段、已升級項重報過濾（ADR-00013）；升級項以結構化 `escalatedFindings` 記入、不論改動數（LL-00010） | RL-0025 | 已守 | 同上 |

### 資料依賴債

類比張力：硬套——無訓練資料；agent 的「資料」＝prompt 內事實與 tracked 檔（規則塊、tasks），依賴顯式且版本化；唯一同型債＝寫進 prompt 的錯事實被規格化。

| 債型 | 徵狀 | 來源 | 影響面 | 觸發 | 處置 | 守門 | 狀態 | 覆審條件 |
|---|---|---|---|---|---|---|---|---|
| prompt 事實接地錯 | 錯的「事實」被 agent 照做 | rev5:L-081 | 單元產物 | 寫 prompt 時 | 每條附出處、與碼衝突以碼為準 | RL-0028 | 已守 | 次個編排刀收刀 |

### 管線債

類比張力：對得上——編排膠水（script、看門狗、續跑）就是流程層的管線，rev5 的 agent 類坑大半在此。

| 債型 | 徵狀 | 來源 | 影響面 | 觸發 | 處置 | 守門 | 狀態 | 覆審條件 |
|---|---|---|---|---|---|---|---|---|
| 誤報失敗 | script 把做完的工作報成失敗 | rev5:L-011 | 單元結果 | 每單元 | 狀態欄不跨角色複用、確認輪 | RL-0004 | 已守 | 次個編排刀收刀 |
| blocked 語意重載 | 交付完整卻整段審查零輪次 | rev5:L-035 | 審查階段 | agent 回報時 | status 分 blocked／done_with_escalation | RL-0012 | 已守 | 同上 |
| launch 被擋鎖舊目錄 | 看門狗鎖上前一支 wf | rev5:L-049 | 看門狗 | launch 失敗時 | TaskStop 後帶 runId 重掛 | RL-0016 | 已守 | 同上 |
| stall 判定無心跳 | run 結束後 journal 不動＝必誤報 | rev5:L-051 | 看門狗 | 完成通知時 | 立即 TaskStop | RL-0017 | 已守 | 同上 |
| 續跑冒煙殘留 | ARMED 行位元組是前一輪的 | rev5:L-023 | 續跑 | resume 時 | 改看最新 agent 檔 | RL-0009 | 已守 | 同上 |
| resume 誤用 | 把續跑當「某支重跑」 | rev5:L-027 | 續跑 | 需重跑某階段時 | 新開只跑該階段的 workflow | RL-0010 | 已守 | 同上 |
| 冒煙 token 蒸發 | 派生 script 時 token 隨 prompt 段消失 | rev5:L-057 | 冒煙 | 派生 script 時 | token 置於共用段、渲染斷言 | RL-0018 | 已守 | 同上 |
| 現成工件不用 | 自拼射程更窄的 grep／helper | rev5:L-085、rev5:L-087 | 工具面 | 寫驅動件前 | 先 `ls -R tmp/`、errata 優先 | RL-0032 | 已守 | 同上 |
| 骨架多變體 | 骨架收斂為單一 `_sk_head.js`（共用首段）＋`_sk_cycle.js`／`_sk_main.js`（TDD 形）＋`_sk_review.js`（review 形）；變動段（`_vars`／`_allowed`／`_context`／`_prompts`；review 形＝`_vars`／`_plan`／`_context`）逐單元另寫、組裝成品自帶複本屬必然 | rev6 現況 | 編排骨架 | 每次組裝 | 已收斂；成品由 `assemble.py` 組裝器產出、`harness-test.mjs` 十五案與 `harness-review.mjs` 九案守控制流（各含三反例） | 名冊可見（`docs/generated/reference/agents.md`）＋harness 退出碼 | 已守 | 次個編排刀收刀 |

### 設定債

類比張力：對得上——RAD-AI 說設定債是散落各處、無人擁有的旗標；`*_OPTS`、保險絲值、effort 就是。

| 債型 | 徵狀 | 來源 | 影響面 | 觸發 | 處置 | 守門 | 狀態 | 覆審條件 |
|---|---|---|---|---|---|---|---|---|
| 保險絲手挑 | 保險絲值小於結構最壞值 | rev5:L-068 | Workflow | 寫 script 時 | 由同檔常數推導並自我斷言 | RL-0062 | 已守 | 次個編排刀收刀 |
| OPTS 散落 | `IMPL_OPTS`／`REVIEW_OPTS`／`FIX_OPTS`＋`DEEP_THINK` 單一常數家住 `_sk_head.js`；換模只改該檔一處、名冊由 generate 重算 | rev6 現況 | 換模 | 換模時 | 已收斂為單一常數家 | 名冊可見（`docs/generated/reference/agents.md`） | 已守 | 次個編排刀收刀 |
| 版本字面耦合 | 規則列一改、組裝成品 script 的 RULES-VERSION 字面過期 | rev6 現況 | 發射 | 改規則列時 | 同批重烤（RL-0038） | PreToolUse hook 擋發射 | 已守（偵測） | 改規則列時 |

### 模型陳舊

類比張力：部分——model id 釘死在 `*_OPTS`；供應商下架即陳舊；無自動偵測、換模＝人決（P-E8 再訓練政策）。

| 債型 | 徵狀 | 來源 | 影響面 | 觸發 | 處置 | 守門 | 狀態 | 覆審條件 |
|---|---|---|---|---|---|---|---|---|
| model id 釘死 | 供應商下架後派發失敗 | rev6 現況 | 全部 agent | 供應商公告 | 改 `*_OPTS` 一次 commit、名冊重算 | 無（人決事件） | 刻意不守 | 供應商公告時 |

### 登記條目格式

類比張力：對得上——九欄：債型｜徵狀｜來源（rev5:L 號或 rev6 現況）｜影響面｜觸發｜處置｜守門（RL／GT／名冊／無）｜狀態（已守／未守／刻意不守）｜覆審條件；登記列住各類別子節，「未守」者衍生 BACKLOG 條目（本檔是現況表、不是待辦簿）。

### 債務總覽板

類比張力：部分——RAD-AI 的儀表板是統計面；rev6 只有一句總覽＋指針：未守零列（前兩列「骨架多變體」「OPTS 散落」已於 001 刀 Task 0 收斂）；刻意不守一列（模型陳舊）；其餘皆已守。三指標（治理批比、教訓重複率、BACKLOG 淨流量）＝`docs/generated/STATE.md`。

### 覆審節奏

類比張力：對得上——條件觸發而非定期：覆審條件欄到期時全表覆審（首輪＝001 刀收刀，結論記於該刀收單 commit 訊息；下一輪＝次個編排刀收刀）；收刀 final holistic review（RL-0073）；不定期獨立輪（`docs/reviews/`）；Day-1 豁免到期紅；新坑→LESSONS 一坑一檔、晉升→RULES 一列。
