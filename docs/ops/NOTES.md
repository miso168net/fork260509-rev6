<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r1-doc-governance`（報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- **001 schema 基線刀已收刀**（波 6 首刀、橫切地基；merge `d04a41c`、feature 分支 `001-schema-baseline` 保留）：資料庫基線＝rust-api workspace 三 crate（`migration` 之 m0001 結構＋m0002 seed、`entity` 15 表、`sea-orm-adapter`），凍結面＝`specs/001-schema-baseline/fixtures/` 四件，閘＝`tools/schema-gate.py` 三閘與 `tools/entity-drift-gate.py`（後者入 pre-commit 條件實跑），正典真表＝`docs/generated/reference/{schema,accounts}.md`（`python3 tools/docsync refresh` 照相後 generate 產）。憲法 1.1.0；ADR-00009／ADR-00010 accepted；LL-00001／LL-00002。
- **下一刀＝002**（刀序 001→008 承 rev5、D13；範圍由其 brainstorm 定）：起手＝階段 0 brainstorm（`docs/brainstorms/002-<slug>.md`）→ SDD 五步 → TDD 編排。★動工前先掃 `docs/ops/BACKLOG.md` 觸發欄中時點落在該刀內的條目——現有觸發於 002 者：BL-00008（`ActiveModelBehavior` 恆空機器錨隨 server crate）、BL-00010（entity-drift 段快照缺席改即紅＝閘行為變更、需 spec 面拍板；補償控制已驗、曝險面小）、BL-00011（碼面閘名冊承載處與 `rev5:Lint24` 去處，隨 wire-schema 進場）。★002 前的可直改條目已於 2026-09-05 維護批一次收掉十二條（A＋B 類）；schema 定稿權威改住 `docs/ops/reference-src/schema-definition.md`（ADR-00012）——新表先補該檔 §1 再登記 archetype-map、不再回頭改已收刀的 spec 目錄。
- migration 檔名四碼、delta 自 `m0003`（ADR-00008）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；rust-fmt-gate 隨 002。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
