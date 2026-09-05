<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r1-doc-governance`（報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- **001 schema 基線刀已收刀**（波 6 首刀、橫切地基；merge `d04a41c`、feature 分支 `001-schema-baseline` 保留）：資料庫基線＝rust-api workspace 三 crate（`migration` 之 m0001 結構＋m0002 seed、`entity` 15 表、`sea-orm-adapter`），凍結面＝`specs/001-schema-baseline/fixtures/` 四件，閘＝`tools/schema-gate.py` 三閘與 `tools/entity-drift-gate.py`（後者入 pre-commit 條件實跑），正典真表＝`docs/generated/reference/{schema,accounts}.md`（`python3 tools/docsync refresh` 照相後 generate 產）。憲法 1.1.0；ADR-00009／ADR-00010 accepted；LL-00001／LL-00002。
- **002 system-settings 進行中**（波 6 第二刀、server crate 進場首刀；分支 `002-system-settings`、brainstorm `docs/brainstorms/002-system-settings.md` 定稿 2026-09-05、spec 已落 `specs/002-system-settings/`）：範圍＝承 rev5 讀＋寫＋前端接線層兩新檔、零 migration、憲法零 Amendment；治理項全落刀內 U0（三支碼面閘隨遷、entity-drift 缺席即紅、RUNBOOK §12 碼面閘表＋GT-12 腿、名詞段「碼面閘」、ADR 六筆）。SDD 五步已完（specify `3ddf9d0`→clarify `c3f3fde`→plan `efbd760`→tasks `fa31d95`→analyze `5d1738e`）；TDD 進行中——單元序＝`specs/002-system-settings/tasks.md` 執行單元對映（主線 T001 與 U0 治理組合拳已落→U1 基座→U2 授權→U3 讀端 MVP→U4～U7→U8 收攏）。BL-00008／BL-00010／BL-00011 於本刀兌現、收刀 backlog_done；BL-00002／00003／00006／00007／00021 觸發未到。
- migration 檔名四碼、delta 自 `m0003`（ADR-00008）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；rust-fmt-gate 隨 002。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
