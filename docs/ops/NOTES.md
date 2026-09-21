<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- 已收刀＝001 schema 基線（波 6 首刀、橫切地基）、002 system-settings（server crate 進場首刀）、003 auth-session（真登入／續期／撤銷／節流＋captcha／替代登入 stub／i18n 跨端閘／治理六項；憲法 1.3.0）與 004 ip-trust-anchor（信任錨／IP 存取閘／IP 規則管理／來源維節流＋判定由 PG 定案／管理員解鎖；憲法 1.4.0；碼面閘六支）；**逐刀交付、merge SHA、ADR 清單與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`）**，本檔不重述。
- 規格對照審查兩輪（user 2026-09-15 發起、RL-0073 ②）皆已收：002 刀（報告 `docs/reviews/20260915-spec-compliance-002.md`）、003 刀（報告 `docs/reviews/20260915-spec-compliance-003.md`）；逐筆處置見兩份報告與 `docs/generated/MILESTONES.md`。
- **現在＝005 前維護批（七支輕量軌；user 2026-09-21 逐題裁定）**：順序＝`maint-backlog-79`（已收單）→ `-35`（已收單）→ `-42`（已收單）→ `-80-88-94-99`（已收單）→ `-92-97`（已收單）→ `-89-83-85` → `-86-90`；逐支交付查 `docs/generated/MILESTONES.md`。**下一步＝第 6 支 `maint-backlog-89-83-85`**（tests/common 三守衛 Drop 殼收攏＋ipgate 門鈴測試次序相依＋IP 閘兩處回歸錨）。★第 7 支 `maint-backlog-86-90` 之兩條觸發條件皆未到期（`PageRes` 全樹恰一消費者、`operator_from` 恰兩份），user 2026-09-21 裁定**照做**＝提前執行，同批須改寫 `handler/ip_rule.rs` 的 `PageRes` 原地預告註解（否則其解除謂詞當場成假述）並新記一條 BACKLOG 承載「共用件形狀待 005 第三個寫端 handler 進場時重評」。
- **七支全數收單後＝005 role-menu-crud**（刀序＝首刀 brainstorm 定序、各刀範圍由各自 brainstorm 定、可翻）：自階段 0 brainstorm 起手；004 刀 final holistic review 轉入 BACKLOG 之條目觸發逐條見帳本。
- migration 檔名四碼、delta 自 `m0003`（ADR-00008）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；rust-fmt-gate 已於 002 進場（碼面閘、名冊＝RUNBOOK §12 碼面閘表）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
