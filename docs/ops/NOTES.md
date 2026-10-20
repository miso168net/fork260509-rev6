<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）；by-design 已知態指針總表＝`docs/arc42/11-risks-and-technical-debt.md` 技術債表。

## 下一步

- **下一步＝008 audit-settings-pages**：階段 0 brainstorm 已定稿（`docs/brainstorms/008-audit-settings-pages.md`；user 2026-10-20 一題一問 18 題〔理解校正＋BACKLOG 題 B1～B5＋設計題 D1～D12；非建議 1＝D12 繁中驗收照 ADR-00084 決定 8 字面、每刀重審全部接真頁面〕＋設計四節核可；原列之 BACKLOG 三條、承載易漏帶之題、收刀計數三則、錯誤明細通道第三鍵、BL-00108 探針口徑、需求追溯形、ADR-00079 複核、節流文案約束、觀測層與滯後卷連動、三語同批皆已於該檔 §0～§3 逐條處置）；grilling 輪已畢（user 2026-10-20 一題一問五題皆取建議項：規模維持全射程、排程清理自記列來源位址哨兵 `0.0.0.0`、孤兒授權列只報不刪＋RUNBOOK 處置、設定變更列照 rev5 欄形、刪 0 列照落；結論見該檔 §0 末段）；下一動作＝依 CLAUDE.md §2 以 `/speckit-specify` 顯式起手（input＝該檔）。
- 接手機器（含 WSL）：外層取 `rev6-admin-root` → `bash tools/bootstrap.sh` 綠才可 commit（CLAUDE.md §3／§6）→ pins 以 `docs/generated/STATE.md` 為準（SessionStart 健檢應零分歧）→ 新刀起手依 CLAUDE.md §2 以 `/speckit-specify` 建分支。
- migration 檔名四碼（ADR-00008）、delta 自 `m0003` 起編（ADR-00010 決定 1）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
