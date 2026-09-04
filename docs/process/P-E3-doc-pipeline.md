---
rad_ai: [E3]
rad_ai_map:
  Pipeline Overview Diagram: 管線總覽圖
  Pipeline Inventory Table: 管線清冊表
  Quality Gates: 品質閘
  Feature Store Documentation: 特徵庫記載
  Feedback Loops: 回饋迴圈
  Integration with Data Cards: 與資料卡的銜接
---
# P-E3 文件管線（流程層）

本檔以 RAD-AI E3 的形制記載 brainstorm→spec→tasks→Workflow→review→收刀簿記的管線；品質閘＝lint 與 hook、回饋迴圈＝LESSONS→RULES→prompt；系統層對應＝`docs/arc42/06-runtime-view.md` E3 子節。每個子節首句標明類比張力（哪裡對得上、哪裡是硬套）。

### 管線總覽圖

類比張力：對得上——RAD-AI 的資料管線在流程層＝文件與碼的產生管線；每階段有輸入、輸出、閘。

```mermaid
flowchart LR
  bs["brainstorm"] --> sdd["SDD 五步"]
  sdd --> wf["Workflow 單元"]
  wf --> fr["final review"]
  fr --> mg["merge"]
  mg --> bk["收刀簿記"]
  bk --> gen["generate"]
```

### 管線清冊表

類比張力：對得上——每階段一列：輸入｜輸出｜承載｜閘。

| 階段 | 輸入 | 輸出 | 承載 | 閘 |
|---|---|---|---|---|
| brainstorm | 啟動書波次表、rev5 同題 spec、BACKLOG | `docs/brainstorms/<NNN>-*.md`＋ADR draft | superpowers:brainstorming | 拍板一題一問；GT-06 連結腿 |
| SDD 五步 | brainstorm 檔 | `specs/<NNN>-*/`（spec／plan／tasks） | spec-kit 五命令 | 憲法 §IV 九題；auto-commit |
| Workflow 單元 | tasks.md、規則塊 | 工作樹改動、findings、`{status, report}` | Workflow 工具＋看門狗 | 六件套（RL-0058～RL-0062）；PreToolUse hook |
| final review | 全 diff | 處置清單（修／BL／ADR） | 主線自審 | RL-0073 三分流 |
| merge | 分支 | default branch 前進 | `git merge --no-ff` | 人審當次同意（RL-0044） |
| 收刀簿記 | merge SHA | events append、NOTES | 主線 | GT-02／GT-03 事件形制 |
| generate | 真源檔 | `docs/generated/**`＋例外註冊 | `python3 tools/docsync generate` | GT-01 零漂移 |

### 品質閘

類比張力：對得上——三層閘：pre-commit 十二閘（名冊＝`docs/generated/GATES.md`、本節不重抄）、PreToolUse hook（RULES-VERSION 對賬、zh-TW 字面）、review 輪（findings 三分流）；每閘一正一反自證（RL-0051）。

### 特徵庫記載

類比張力：硬套——無特徵庫；最近的類比＝規則塊（`python3 tools/docsync rules emit --scope <s>`）：版本化、烤入每支 prompt、hook 對賬，扮演「訓練與推論共用同一定義」的角色，但它是規則不是特徵。

### 回饋迴圈

類比張力：對得上——三條顯式迴圈：教訓→規則→prompt（LESSONS 晉升為 RULES 一列、`rules emit` 烤入；啟動書 §3.6）；findings→修／BACKLOG／ADR（RL-0073）；events→STATE 三指標（治理批比、教訓重複率、BACKLOG 淨流量）。

### 與資料卡的銜接

類比張力：硬套——無資料卡；類比＝`docs/ops/reference-src/` 半自動快照（schema／accounts，`python3 tools/docsync refresh` 自實庫照相）與 `docs/generated/reference/`，記的是系統資料的形、不是訓練資料集。
