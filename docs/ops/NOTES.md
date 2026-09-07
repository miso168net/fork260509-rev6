<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- 已收刀＝001 schema 基線（波 6 首刀、橫切地基）與 002 system-settings（server crate 進場首刀）；**逐刀交付、merge SHA、ADR 清單與 backlog_done 一律查 `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`）**，本檔不重述。
- **進行中＝003 auth-session**（分支 `003-auth-session`；階段 0 定稿＝`docs/brainstorms/003-auth-session.md`、範圍＝整批一刀 US1～US5＋治理 US6、零 migration、MINOR Amendment 1.2.0→1.3.0 開首批 ★軌道四條八用途與島 A～E）：SDD 五步已落（specify／clarify Q1～Q4／plan／tasks T001～T079／analyze 修單）、ADR-00026 draft proposed 在分支；**下一步＝TDD 編排自 U0 起**（首個主線任務＝ADR-00026 user 親決→accepted→憲法 §III.2／§I.7／§I.2 釐清＋1.3.0；派發序 U0→U1～U4→U10a→U5～U9→U10→U11、每單元允許檔案清單見 tasks 對映表）。
  ★BACKLOG 觸發項處置已定於 brainstorm §2：BL-00026／BL-00030／BL-00037／BL-00041 刀內收（收刀 `backlog_done`）、BL-00031 只收 `login_throttle_*` 一對並改條文、BL-00042／BL-00028 不觸發；收刀 `backlog_add` 須列 BL-00043～BL-00049（七筆 GT-03 在途 WARN 由此消）＋新配兩條（`/auth/error` 排程錨、`sys_user_role` `roles_of_user` DbErr 守衛錨）＝九條。RUNBOOK §9c 走查基準工具遷入隨本刀。
- migration 檔名四碼、delta 自 `m0003`（ADR-00008）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；rust-fmt-gate 已於 002 進場（碼面閘、名冊＝RUNBOOK §12 碼面閘表）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
