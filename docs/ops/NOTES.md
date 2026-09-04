<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r1-doc-governance`（報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- 首刀＝001 schema 基線刀（波 6 起＝刀、走 SDD 全程）：階段 0 定稿＝`docs/brainstorms/001-schema-baseline.md`（刀序 001→008 承 rev5、D13；各刀範圍由各自 brainstorm 定）；specify、clarify、plan、tasks、analyze 已完成（分支 `001-schema-baseline`；憲法 1.1.0＋ADR-00009 accepted 已落；ADR-00010 proposed、U2 收尾轉 accepted；版本三源拍板：sea-orm 1.1.20、async-trait 0.1.92、rust 1.96.1）；analyze 11 項（HIGH 1＝adapter 假 DSN 改執行期串接、其餘對齊已套用）；TDD 編排進行中（tasks.md 41 條、單元對映 research R11）：Task 0（BL-00001 骨架收斂）與 U1（rust-api 骨架＋17 檔承襲＋adapter＋dev stack 重放）已落、LL-00001 首條教訓已落；下一步＝U2（兩閘工具隨遷＋pristine 重放＋fixtures 雙源互證＋ADR-00010 accepted）→ U3（docsync refresh＋兩真表＋entity-drift hook）→ U4（RUNBOOK／活書／DoD 鏈／perf）→ U5（BL-00005、拍板級）。
  specify 後首顆手動 commit＝ADR-00009（憲法 §I.5 例外 Amendment、MINOR 1.1.0），ADR-00010（schema 基線契約）隨刀；migration 檔名四碼 `m0001_`／`m0002_`、delta 自 `m0003`（ADR-00008）；rust-fmt-gate 隨 002。
  動工前先掃 `docs/ops/BACKLOG.md` 觸發欄中時點落在本刀內的條目（現有：BL-00001 開分支後首個 Workflow 前＝Task 0、BL-00005 收刀前＝U5（拍板級）；BL-00002 本刀不觸發、兩 ADR 非 AI-ADR）；rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
