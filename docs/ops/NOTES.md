<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- 已收刀＝001 schema 基線（波 6 首刀、橫切地基）、002 system-settings（server crate 進場首刀）與 003 auth-session（真登入／續期／撤銷／節流＋captcha／替代登入 stub／i18n 跨端閘／治理六項；憲法 1.3.0；碼面閘四支）；**逐刀交付、merge SHA、ADR 清單與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`）**，本檔不重述。
- **下一步＝004 ip-trust-anchor**（階段 0 brainstorm 起手＝superpowers:brainstorming 產 `docs/brainstorms/004-ip-trust-anchor.md`、`/speckit-specify` 只在定稿後顯式起手）：直接輸入＝憲法 §I.7 島 F（信任錨與 IP 存取閘、來源維節流）與承襲指針表、活書 06 frontmatter「信任錨與 IP 存取閘：隨刀」列與 §8.3 邊緣 `auth_limit` 已知態、rev5 藍本去處 `docs/generated/reference/rev5-blueprint-map.md`、BACKLOG 觸發欄指名 004 者（含 BL-00031 之 `ip_*` 對鍵）；★003 留下的「收刀後首個維護批」候選（BL-00050／BL-00052／BL-00054／BL-00055／BL-00056／BL-00057／BL-00059／BL-00060／BL-00068／BL-00069 觸發皆綁此批）可先於 004 以輕量軌開一支收攏。
- migration 檔名四碼、delta 自 `m0003`（ADR-00008）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；rust-fmt-gate 已於 002 進場（碼面閘、名冊＝RUNBOOK §12 碼面閘表）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
