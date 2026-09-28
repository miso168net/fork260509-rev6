<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- 已收刀＝001 schema 基線（波 6 首刀、橫切地基）、002 system-settings（server crate 進場首刀）、003 auth-session（真登入／續期／撤銷／節流＋captcha／替代登入 stub／i18n 跨端閘／治理六項；憲法 1.3.0）、004 ip-trust-anchor（信任錨／IP 存取閘／IP 規則管理／來源維節流＋判定由 PG 定案／管理員解鎖；憲法 1.4.0；碼面閘六支）與 005 role-menu-crud（角色與選單管理接真／島 H 選單域生命週期＋判定面同步／選單回收桶／分頁通則／走查還原工具擴面；憲法 1.5.0→1.5.2）；**逐刀交付、merge SHA、ADR 清單與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`）**，本檔不重述。
- 規格對照審查**三輪**（RL-0073 ②）皆已收：002 刀與 003 刀（user 2026-09-15 發起；報告 `docs/reviews/20260915-spec-compliance-002.md`、`…-003.md`）、**004 刀**（user 2026-09-22 發起；報告 `docs/reviews/20260922-spec-compliance-004.md`）；逐筆處置見三份報告與 `docs/generated/MILESTONES.md`。004 輪結論＝零 blocker、零 wire 行為缺陷，且 005 前維護批七支對 004 碼面的改動全部找得到承載；同輪新記 BL-00114～BL-00125。
- **005 前維護批（七支輕量軌；user 2026-09-21 逐題裁定）＝已全數收單並推**：`maint-backlog-79`／`-35`／`-42`／`-80-88-94-99`／`-92-97`／`-89-83-85`／`-86-90`；逐支交付、merge SHA 與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`），本檔不重述。本輪治理面產出＝ADR-00041、RL-0077／RL-0078／RL-0079、LL-00030／LL-00031／LL-00032；BACKLOG 刪列 13 條、新記 13 條（新記者幾乎全為七輪審查自既有碼面揭出的缺口，非本輪新欠）。 ★另有第 8 支 `maint-backlog-103-104-114-121-122`（user 2026-09-22 依 BACKLOG 分類體檢另次裁定、spec-compliance-004 之後）：收 python／doc 面五條 BL-00103／BL-00104／BL-00114／BL-00121／BL-00122（perf 排序、schema-definition 刀名形、GT-06 折行與懸空前綴兩腿、GT-12 門鈴字面同源腿、route-artifact-gate 沙盒旗標）並吸收其 final review 9 筆修；merge 與 backlog_done 查 `docs/generated/MILESTONES.md`。rust 測試側四條 BL-00107／BL-00110／BL-00123／BL-00115 與 BL-00106 已於 005 刀 U14 收。
- **現在＝005 已收刀**：逐單元交付、merge SHA、ADR（ADR-00042～ADR-00051）與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`；本刀新增之已知態集中於 ADR-00045（角色與選單八款）與 ADR-00046（IP 域七款），其翻案觸發器即後續刀之承接點。
- **下一步＝下一刀 brainstorm**（刀序由 user 定；輸入＝啟動書 §5 波次表、BACKLOG 觸發欄、ADR-00045／ADR-00046 翻案觸發器——授權治理面〔三顆授權彈窗接真、policy-archive 頁〕與使用者域為現存承接面）；另 BL-00126（context 自動壓縮機制入版控）為輕量軌候選。
- 接手機器（含 WSL）：外層取 `rev6-admin-root` → `bash tools/bootstrap.sh` 綠才可 commit（CLAUDE.md §3／§6）→ pins 以 `docs/generated/STATE.md` 為準（SessionStart 健檢應零分歧）→ 新刀起手依 CLAUDE.md §2 以 `/speckit-specify` 建分支。
- migration 檔名四碼、delta 自 `m0003`（ADR-00008）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；rust-fmt-gate 已於 002 進場（碼面閘、名冊＝RUNBOOK §12 碼面閘表）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
