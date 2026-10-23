<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）；by-design 已知態指針總表＝`docs/arc42/11-risks-and-technical-debt.md` 技術債表。

## 下一步

- **進行中＝008 audit-settings-pages**（分支 `008-audit-settings-pages`）：SDD 五步已完、U0 兩顆已落（Amendment 顆 `8ceadb5`＝憲法 1.9.0；ADR-00099～ADR-00102、ADR-00104、ADR-00105、ADR-00107、ADR-00108 accepted；ADR-00103／ADR-00106 留 proposed 至 U18）；U1 工具前置已落（`tools/schema-gate.py offline` 離線對賬腿＋pre-commit `schema-offline` 段、runtime-append 兩工具擴 `sys_access_log`）；**下一步＝U2 測試基建**（存取日誌與清理之守衛、drain、app helper）。
- 接手機器（含 WSL）：外層取 `rev6-admin-root` → `bash tools/bootstrap.sh` 綠才可 commit（CLAUDE.md §3／§6）→ pins 以 `docs/generated/STATE.md` 為準（SessionStart 健檢應零分歧）→ 新刀起手依 CLAUDE.md §2 以 `/speckit-specify` 建分支。
- migration 檔名四碼（ADR-00008）、delta 自 `m0003` 起編（ADR-00010 決定 1）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；帶結構演進（DDL）之 delta migration 須同刀先擴 `tools/schema-gate.py offline`，未擴即被 pre-commit `schema-offline` 段擋（RUNBOOK §10）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
