<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- 已收刀＝001 schema 基線（波 6 首刀、橫切地基）、002 system-settings（server crate 進場首刀）、003 auth-session（真登入／續期／撤銷／節流＋captcha／替代登入 stub／i18n 跨端閘／治理六項；憲法 1.3.0）、004 ip-trust-anchor（信任錨／IP 存取閘／IP 規則管理／來源維節流＋判定由 PG 定案／管理員解鎖；憲法 1.4.0；碼面閘六支）與 005 role-menu-crud（角色與選單管理接真／島 H 選單域生命週期＋判定面同步／選單回收桶／分頁通則／走查還原工具擴面；憲法 1.5.0→1.5.2）；**逐刀交付、merge SHA、ADR 清單與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`）**，本檔不重述。
- 規格對照審查**四輪**（RL-0073 ②）皆已收：002 刀與 003 刀（user 2026-09-15 發起；報告 `docs/reviews/20260915-spec-compliance-002.md`、`…-003.md`）、**004 刀**（user 2026-09-22 發起；報告 `docs/reviews/20260922-spec-compliance-004.md`）、**005 刀**（user 2026-09-30 發起；報告 `docs/reviews/20260930-spec-compliance-005.md`）；逐筆處置見各報告與 `docs/generated/MILESTONES.md`。004 輪結論＝零 blocker、零 wire 行為缺陷，且 005 前維護批七支對 004 碼面的改動全部找得到承載；同輪新記 BL-00114～BL-00125。005 輪結論＝零 blocker、零 wire 行為缺陷，收刀後六支維護批對 005 面之改動全部找得到承載；user 裁修項全部轉帳（新記 BL-00129～BL-00135）、收刀程序補簿記後驗一步（RL-0084）。
- **005 前維護批（七支輕量軌；user 2026-09-21 逐題裁定）＝已全數收單並推**：`maint-backlog-79`／`-35`／`-42`／`-80-88-94-99`／`-92-97`／`-89-83-85`／`-86-90`；逐支交付、merge SHA 與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`），本檔不重述。本輪治理面產出＝ADR-00041、RL-0077／RL-0078／RL-0079、LL-00030／LL-00031／LL-00032；BACKLOG 刪列 13 條、新記 13 條（新記者幾乎全為七輪審查自既有碼面揭出的缺口，非本輪新欠）。 ★另有第 8 支 `maint-backlog-103-104-114-121-122`（user 2026-09-22 依 BACKLOG 分類體檢另次裁定、spec-compliance-004 之後）：收 python／doc 面五條 BL-00103／BL-00104／BL-00114／BL-00121／BL-00122（perf 排序、schema-definition 刀名形、GT-06 折行與懸空前綴兩腿、GT-12 門鈴字面同源腿、route-artifact-gate 沙盒旗標）並吸收其 final review 9 筆修；merge 與 backlog_done 查 `docs/generated/MILESTONES.md`。rust 測試側四條 BL-00107／BL-00110／BL-00123／BL-00115 與 BL-00106 已於 005 刀 U14 收。
- **現在＝005 已收刀**：逐單元交付、merge SHA、ADR（ADR-00042～ADR-00051）與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`；本刀新增之已知態集中於 ADR-00045（角色與選單八款）與 ADR-00046（IP 域七款），其翻案觸發器即後續刀之承接點。
- **006 前 BACKLOG 體檢維護批 `maint-backlog-28-35-36-39-74-101-102-120`（user 2026-09-29 逐題裁定、B～E 組併批）＝已收單**：八條全收（ADR-00052～ADR-00055、RL-0081、LL-00041～LL-00048）；逐條交付、merge SHA 與 backlog_done 查 `docs/generated/MILESTONES.md`。
- **006 前 BACKLOG 體檢 v5（user 2026-09-29 裁定）＝三支皆已收單**：`maint-backlog-127`（BL-00127→ADR-00056：組裝形 workflow 模型家 opus[1m]／xhigh、TDD 形 harness 模型家斷言與反例）、批 F `maint-backlog-27-44`（BL-00027→ADR-00057、BL-00044→ADR-00058）與批 A `maint-backlog-29-93`（BL-00093 告警規則活體驗證、殘餘併 BL-00043；BL-00029 設定寫端條件式 UPDATE 與 ADR-00057 決定 1 之端點真 DB 釘）；逐條交付、merge SHA 與 backlog_done 查 `docs/generated/MILESTONES.md`。
- **時區裁定施作 `maint-tz-utc`（user 2026-09-30 逐題裁定）＝已收單**：DB 伺服器時區固定 UTC（ADR-00059）、憲法 1.6.0 時間點欄通則（ADR-00060）、時間傳輸與顯示慣例（ADR-00061）、記時與帳本日期時區（ADR-00062、RL-0082／RL-0083）；環境面守衛（BL-00128）已由下條維護批收；交付與 merge SHA 查 `docs/generated/MILESTONES.md`。
- **006 前維護批 `maint-backlog-128-129-130`（user 2026-09-30 開批）＝已收單**：BL-00128（時區環境面守衛：schema-gate 時區判值＋來源、bootstrap compose 時區體檢）、BL-00129（005 刀規格對照輪文件五處）、BL-00130（碼面保護缺口補臂＋wire-schema customRoutes 讀面）全收，另含看門狗長尾腿補回形與 STALL 合法等待（LL-00050／LL-00051）；新記 BL-00136（006 brainstorm 輸入）；交付與 merge SHA 查 `docs/generated/MILESTONES.md`。
- **下一步＝006 authz-governance brainstorm**（刀序＝001 刀 brainstorm Q1〔D13〕；006 前維護批已收單〔見上條〕；輸入＝啟動書 §5 波次表、BACKLOG 觸發欄、ADR-00045／ADR-00046 翻案觸發器、ADR-00058 決定 3（006～008 spec 之 Out of Scope 指該 ADR）與 ADR-00057 後果（008 設定頁承接宣告集外之列的呈現）——授權治理面〔三顆授權彈窗接真、policy-archive 頁〕與使用者域為現存承接面）。
  - **006 前 BACKLOG 體檢 v7（開放 17＋滯後 3 逐條取證；user 2026-09-30 裁）**：006 前可輕量收 0 條——僅有的兩條候選 BL-00131 裁維持至 007、BL-00002 裁維持原觸發——⇒ 不再開 006 前維護批。
  - **006 brainstorm 的 BACKLOG 輸入**（逐條觸發與處置讀 BACKLOG 本體）：必帶 BL-00045、BL-00048、BL-00084、BL-00132、BL-00134、BL-00135、BL-00136；其中 BL-00084（006 續行 ADR-00046 時併一款 by-design）、BL-00132（§III.2 範圍欄處數／塊數對賬）與 BL-00135（§III 修改型之模板屬性行變體；user 已裁併入下次 Amendment）三條觸發欄無「006」字面、只掃觸發欄會漏。反向確認兩條：BL-00133（006 會改寫其敘述）、BL-00047（006 若裁「手動撤銷之選單／按鈕維歸檔列可復原」即須 add_column、成為首支 delta 刀、本條於開寫前到期）。另記 BL-00131：006 若把 updateRole 下放給非超管，角色編輯抽屜恆送回填 status 之「兩分頁舊值覆寫」（會把他人剛停用的角色靜默恢復啟用）即成跨人情境——定下放範圍時一併看；該條條文目前只載誤擋一面。
- 接手機器（含 WSL）：外層取 `rev6-admin-root` → `bash tools/bootstrap.sh` 綠才可 commit（CLAUDE.md §3／§6）→ pins 以 `docs/generated/STATE.md` 為準（SessionStart 健檢應零分歧）→ 新刀起手依 CLAUDE.md §2 以 `/speckit-specify` 建分支。
- migration 檔名四碼、delta 自 `m0003`（ADR-00008）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；rust-fmt-gate 已於 002 進場（碼面閘、名冊＝RUNBOOK §12 碼面閘表）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
- **事件帳待補記兩筆 user merge＋push 同意**（兩批收單事件之 notes 未載；events 既有列不可改、RUNBOOK §12c erratum 可更正欄不含 notes⇒於下一筆 events 事件之 notes 補記，補記後刪本條）：①spec-compliance-005（merge 78d4700）：user 2026-09-30 06:13 答「merge 後連同簿記一起 push」②maint-backlog-128-129-130（merge 704f743）：user 2026-09-30 11:33 原話「重新發射 U2 workflow 都沒問題的話, 我提前授權此分支合併到預設分支+push」（條件已成立後執行）。
- 他機（Mac）pull 到 maint-backlog-126 後須重開 Claude Code session，入版控之壓縮 hook 與 `autoCompactWindow` 才生效（設定只在啟動時讀入）。
