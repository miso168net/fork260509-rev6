<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）。

## 下一步

- 已收刀＝001 schema 基線（波 6 首刀、橫切地基）、002 system-settings（server crate 進場首刀）與 003 auth-session（真登入／續期／撤銷／節流＋captcha／替代登入 stub／i18n 跨端閘／治理六項；憲法 1.3.0；碼面閘四支）；**逐刀交付、merge SHA、ADR 清單與 backlog_done／backlog_add 一律查 `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`）**，本檔不重述。
- 規格對照審查兩輪（user 2026-09-15 發起、RL-0073 ②）皆已收：002 刀（報告 `docs/reviews/20260915-spec-compliance-002.md`）、003 刀（報告 `docs/reviews/20260915-spec-compliance-003.md`）；逐筆處置見兩份報告與 `docs/generated/MILESTONES.md`。
- **進行中＝004 ip-trust-anchor**（分支 `004-ip-trust-anchor`）：階段 0 brainstorm 已定稿（`docs/brainstorms/004-ip-trust-anchor.md`；定稿 `fe6f8ad`＋grill 兩輪修訂 `bfaba0e`——起手前收斂之 BL-00066〔節流判定改每次由資料庫定案、拔除快取負快取〕與 BL-00078〔刪 rules.yml 永不觸發規則〕皆已拍板、隨本刀兌現；原留給 clarify 的十項候選已於第二輪 grill 定案為該檔 §5）；`/speckit-specify` 已產 `specs/004-ip-trust-anchor/spec.md`（`1fef4d7`；零 NEEDS CLARIFICATION、§5 十項定案直接落 FR）；`/speckit-clarify` 已收（`bf30d03`；三題皆採建議＝阻擋只擋請求不撤會話／未鎖標的解鎖照寫稽核與標記／管理頁對照 22080 以結構清單全等為判準）；`/speckit-plan` 已落（`aa29a6a`：plan／research R1～R12／data-model／contracts 五檔／quickstart；Constitution Check 六 PASS＋三「涉及——授權以 Amendment 先行取得」；ADR-00034 draft proposed 同落、user 親決於 tasks 首個主線任務）；`/speckit-tasks` 已落（`c118bde`：T001～T070、執行單元 U0～U12、U0＝Amendment 凍結硬閘、U7／U8／U10／U11 對 U0 硬序）；`/speckit-analyze` 已收（零 CRITICAL；1 HIGH＋4 MEDIUM＋6 LOW 修單同顆落地）。**下一步＝TDD 實作**（U0 主線＝ADR-00034 user 親決→accepted→bump 1.4.0→generate；U1～U12 Workflow 編排、發射前模型分派向 user 確認；單元收尾六步序）。003 刀收刀後兩支維護批 `maint-backlog-pre-004`、`maint-backlog-71-46-76` 皆已收（逐條見 `docs/generated/MILESTONES.md`）。
- migration 檔名四碼、delta 自 `m0003`（ADR-00008）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；rust-fmt-gate 已於 002 進場（碼面閘、名冊＝RUNBOOK §12 碼面閘表）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；三指標首值待三刀後由 STATE 現讀；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
