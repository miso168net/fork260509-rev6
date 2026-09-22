<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- 已收刀＝001 schema 基線（波 6 首刀、橫切地基）、002 system-settings（server crate 進場首刀）、003 auth-session（真登入／續期／撤銷／節流＋captcha／替代登入 stub／i18n 跨端閘／治理六項；憲法 1.3.0）與 004 ip-trust-anchor（信任錨／IP 存取閘／IP 規則管理／來源維節流＋判定由 PG 定案／管理員解鎖；憲法 1.4.0；碼面閘六支）；**逐刀交付、merge SHA、ADR 清單與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`）**，本檔不重述。
- 規格對照審查**三輪**（RL-0073 ②）皆已收：002 刀與 003 刀（user 2026-09-15 發起；報告 `docs/reviews/20260915-spec-compliance-002.md`、`…-003.md`）、**004 刀**（user 2026-09-22 發起；報告 `docs/reviews/20260922-spec-compliance-004.md`）；逐筆處置見三份報告與 `docs/generated/MILESTONES.md`。004 輪結論＝零 blocker、零 wire 行為缺陷，且 005 前維護批七支對 004 碼面的改動全部找得到承載；同輪新記 BL-00114～BL-00125。
- **005 前維護批（七支輕量軌；user 2026-09-21 逐題裁定）＝已全數收單並推**：`maint-backlog-79`／`-35`／`-42`／`-80-88-94-99`／`-92-97`／`-89-83-85`／`-86-90`；逐支交付、merge SHA 與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`），本檔不重述。本輪治理面產出＝ADR-00041、RL-0077／RL-0078／RL-0079、LL-00030／LL-00031／LL-00032；BACKLOG 刪列 13 條、新記 13 條（新記者幾乎全為七輪審查自既有碼面揭出的缺口，非本輪新欠）。
- **現在＝005 role-menu-crud**：自階段 0 brainstorm 起手（`docs/brainstorms/005-role-menu-crud.md`）。★開刀前必看的兩條到期承載：**BL-00113**（`handler/common.rs` 兩件共用件係於恰兩份樣本時提前收攏、非終態，第三個帶操作稽核之寫端 handler 進場時 MUST 重評形狀）與 **BL-00106**（i64 守衛 lint 的三個靜默逃逸面，改以「005 收刀前的承載體檢」為謂詞）；另 BL-00105／BL-00112 兩條 wire 裁判面缺口於動 `tests/wire_schema.rs` 時到期。★spec-compliance-004 新記之條目中與 005 直接相關者：**BL-00116**（IP 規則清單端點之 `current` 上界 clamp 契約未宣告——005 第二個分頁端點落地時一併定）、**BL-00124**（Out of Scope「通用化節流 seam」零承載）；另 **BL-00118**／**BL-00119** 兩條憲法面（user 2026-09-22 裁定）待 005 走 §V.2 Amendment 時併入。004 刀 final holistic review 轉入 BACKLOG 之條目觸發逐條見帳本。
- migration 檔名四碼、delta 自 `m0003`（ADR-00008）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；rust-fmt-gate 已於 002 進場（碼面閘、名冊＝RUNBOOK §12 碼面閘表）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
