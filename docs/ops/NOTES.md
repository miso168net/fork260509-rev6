<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r1-doc-governance`（報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- **001 schema 基線刀已收刀**（波 6 首刀、橫切地基；merge `d04a41c`、feature 分支 `001-schema-baseline` 保留）：資料庫基線＝rust-api workspace 三 crate（`migration` 之 m0001 結構＋m0002 seed、`entity` 15 表、`sea-orm-adapter`），凍結面＝`specs/001-schema-baseline/fixtures/` 四件，閘＝`tools/schema-gate.py` 三閘與 `tools/entity-drift-gate.py`（後者入 pre-commit 條件實跑），正典真表＝`docs/generated/reference/{schema,accounts}.md`（`python3 tools/docsync refresh` 照相後 generate 產）。憲法 1.1.0；ADR-00009／ADR-00010 accepted；LL-00001／LL-00002。
- **002 system-settings 已收刀**（波 6 第二刀、server crate 進場首刀；merge `ecea8ee`、feature 分支 `002-system-settings` 保留）：rust-api `server` crate（router→auth（判定單點、DB-fresh 取角色、no-escalation 掛點）→handler（讀 16 鍵／寫單鍵＋三態）→validation（registry）／facade（entity 唯一存取管道）；契約測試面 contract／wire_schema／entity_access_lint／entity_behavior_lint／health＋handler endpoint_tests 真 DB 案）、base-web 兩支新增型新檔（typings／service；fork-delta as-built 見 arc42 08 §8.4）、三支碼面閘＋RUNBOOK §12 碼面閘表＋GT-12 腿；ADR-00013～ADR-00019 accepted；活書 05／08 as-built。零 migration、憲法零 Amendment。BL-00008／00010／00011／00024 已兌現（收刀事件 `backlog_done`）。
- **下一刀＝003 auth-session**（001 brainstorm §0 Q1 刀序表；範圍由其 brainstorm 定、可翻；`.env` route mode 翻 dynamic 與 `VITE_HTTP_PROXY` 延至此刀＝002 brainstorm Q7）：起手＝階段 0 brainstorm（`docs/brainstorms/003-auth-session.md`）→ `/speckit-specify`。
- migration 檔名四碼、delta 自 `m0003`（ADR-00008）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；rust-fmt-gate 已於 002 進場（碼面閘、名冊＝RUNBOOK §12 碼面閘表）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
