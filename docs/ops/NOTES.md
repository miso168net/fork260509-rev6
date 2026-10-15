<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）；by-design 已知態指針總表＝`docs/arc42/11-risks-and-technical-debt.md` 技術債表。

## 下一步

- **下一步＝007 規格對照審查輪（user 手動發起）**：兩支 008 前維護批（`maint-backlog-142-146`、`maint-backlog-139-140-145-147`）收單後、008 brainstorm 起手前，由 user 手動發起 007 刀之規格對照審查輪（RL-0073 ②）；主線不自行開輪。
- **其後＝008 audit-settings-pages**（系統設定頁與稽核頁進場；待 user 開工令、依 CLAUDE.md §2 自階段 0 brainstorm 起手）；brainstorm 須答之題與約束：
  - BACKLOG 觸發落在 008 之三條：BL-00043（存取日誌寫入面與 reaper 兩 job 入不入 008）、BL-00045（兩頁射程、§III.2 新用途、密碼政策投影快取失效、稽核端點連動）、BL-00133（授權歸檔表保留期）；各題建議與指 008 之義務枚舉（O 組 with-008 二十題、交付連動改述六項、X 組 with-008 二項）住 008 前 BACKLOG 體檢 v10（主線工作區、gitignored）。
  - 錯誤明細通道是否擴第三個攜參鍵（ADR-00076 翻案觸發器首條）：擴則 plan 期續行 ADR，並把 ADR-00076／ADR-00090 決定 1 之「照提示秒數重試必過」改為碼註之窄句（牆鐘回撥時可能須再等一次）；不擴則 brainstorm 記「以碼註為準」結案。
  - BL-00108 反向確認之探針口徑（008 若在 lint 增腿即踩）：探針取兩側函式名聯集、以 char 級簽名行數計，並寫明 byte 級 authz 組不計之理由。
  - 需求追溯形一題（ADR-00094 決定 3）：本刀是否沿用子句表、射程取哪幾類。是否沿用與射程非強制；一經沿用，須自證空錨與錨不符一律計不符、核數對得上總錨數（LL-00071）。007 實數供定射程：只拆驗收場景與 SC 會漏 FR 127 個、Edge Cases 58 個缺口（含唯一 blocker）。
  - 文案約束（BL-00145 滯後條文）：設定頁帳號登入／來源登入兩組節流說明與稽核頁登入嘗試分頁告示，皆不承諾嚴格上限。
  - 觀測層連動：008 若改動 `deploy/grafana-provisioning/**` 之儀表板查詢、面板增刪或告警規則本體（純 description 與註解改寫不算），或 rust-api 之 metric 發射點（例：BL-00043 取 reaper 入刀），即觸發 BL-00139（三空面板與 reaper／audit-log 儀表板描述同批處置）。
  - 本刀起每刀三語同批（ADR-00084 決定 11）。
- 接手機器（含 WSL）：外層取 `rev6-admin-root` → `bash tools/bootstrap.sh` 綠才可 commit（CLAUDE.md §3／§6）→ pins 以 `docs/generated/STATE.md` 為準（SessionStart 健檢應零分歧）→ 新刀起手依 CLAUDE.md §2 以 `/speckit-specify` 建分支。
- migration 檔名四碼（ADR-00008）、delta 自 `m0003` 起編（ADR-00010 決定 1）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
