<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）；by-design 已知態指針總表＝`docs/arc42/11-risks-and-technical-debt.md` 技術債表。

## 下一步

- **下一步＝008 audit-settings-pages**（系統設定頁與稽核頁進場；待 user 開工令、依 CLAUDE.md §2 自階段 0 brainstorm 起手）；brainstorm 須答之題與約束：
  - BACKLOG 觸發落在 008 之三條：BL-00043（存取日誌寫入面與 reaper 兩 job 入不入 008）、BL-00045（兩頁射程、§III.2 新用途、密碼政策投影快取失效）、BL-00133（授權歸檔表保留期）；各題建議與指 008 之義務枚舉住 008 前 BACKLOG 體檢最新一版（主線工作區、gitignored）。
  - 承載只住 ADR 翻案觸發器、凍結 spec 或碼註而易漏帶之題（brainstorm 承襲盤點逐題點名；逐題建議見體檢檔）：島 J 入憲射程（§V.2 Amendment；J5 位以指針指向島 E 末兩點＝ADR-00042；§I.6 變體 B 回填；稽核讀端 PII 打碼單點＝rev5 島 J4；活書 10／06 島 J 情境）；稽核頁 x_forwarded_for 欄之渲染與轉義、來源欄欄集（ip_confidence／peer_ip／trace_id）與時間區間篩選之輸入時區；系統設定寫端是否落操作稽核（ADR-00082 款 3；連動 ADR-00047 空字串語意）；設定頁對宣告集外列之呈現（ADR-00057）、數字欄界值來源（ADR-00054）與授權面是否下放（ADR-00064）；稽核五支端點註冊之連動（ADR-00081 款 9 可授出集重算、ADR-00066 射程款複核）；purge 入刀之連動（ADR-00082 寫入者全集與動作詞彙、audit-capacity 告警之處置）；兩頁按鈕碼顯隱；存取日誌寫入面入刀時之走查還原與 schema 閘 runtime-append 常數；繁中驗收形（ADR-00084 決定 8 之審讀射程）。交付連動之現在式改述以 `python3 tools/docsync errata <詞>` 枚舉（種子例：`BL-00045`、`seed-view-gate`、`恰兩列`、`008 刀`、`島 J`、`未入憲`、`purge_before`、`沒有 delete`、`尚無該 handler`）。
  - 收刀計數三則（各單元 commit 訊息記次數、收刀 feature_close notes 同句彙記，含 0）：ADR-00011 翻案觸發器首條（RULES 任一 scope 撞上限後連續三刀未回上限內；fix 範圍自 2026-10-16 起 20／19，008＝第 1 刀）、ADR-00084 末條（`zh-cn.ts` 新字未分類之紅連續三刀以上各有一次以上；007＝第 1 刀）、ADR-00052 首條（一致性腿誤擋正常部分 commit 之次數）。
  - 錯誤明細通道是否擴第三個攜參鍵（ADR-00076 翻案觸發器首條）：擴則 plan 期續行 ADR，並把 ADR-00076／ADR-00090 決定 1 之「照提示秒數重試必過」改為碼註之窄句（牆鐘回撥時可能須再等一次）；不擴則 brainstorm 記「以碼註為準」結案。
  - BL-00108 反向確認之探針口徑（008 若在 lint 增腿即踩）：探針取兩側函式名聯集、以 char 級簽名行數計，並寫明 byte 級 authz 組不計之理由。
  - 需求追溯形一題（ADR-00097 決定 3）：本刀是否沿用子句表、射程取哪幾類。是否沿用與射程非強制（決定 2a）；一經沿用即強制自證空錨與錨不符一律計不符、核數對得上總錨數（決定 2b；LL-00071）；沿用則該刀收單時重審「工具入庫與通則化」（ADR-00097 翻案觸發器首條）。007 實數供定射程：只拆驗收場景與 SC 會漏 FR 127 個、Edge Cases 58 個缺口（含唯一 blocker）。
  - 設定頁進場（ADR-00079 翻案觸發器）：複核密碼長度上下界矛盾之寫端是否加畫面前置提示或守門。
  - 文案約束（BL-00145 滯後條文）：設定頁帳號登入／來源登入兩組節流說明與稽核頁登入嘗試分頁告示，皆不承諾嚴格上限。
  - 觀測層連動：008 若改動 `deploy/grafana-provisioning/**` 之儀表板查詢、面板增刪或告警規則本體（純 description 與註解改寫不算），或 rust-api 之 metric 發射點（例：BL-00043 取 reaper 入刀），即觸發 BL-00139（三空面板與 reaper／audit-log 儀表板描述同批處置）。
  - 滯後卷與條件到期連動：008 若改動登入節流之判定次序（例：讓節流短路遭拒也落 `sys_login_attempt` 以供稽核頁呈現）即觸發 BL-00145；若改動設密／登入之雜湊位次或連線池設定（例：存取日誌寫入面入刀而調池）即觸發 BL-00147；凡拍入 seed／schema 變更而產生 delta migration（例：設定頁授權下放、purge 改受保護、兩頁增按鈕碼、保留期做成設定鍵），BL-00148 於該 migration 單元起手前到期、tasks 須排前置單元。
  - 本刀起每刀三語同批（ADR-00084 決定 11）。
- 接手機器（含 WSL）：外層取 `rev6-admin-root` → `bash tools/bootstrap.sh` 綠才可 commit（CLAUDE.md §3／§6）→ pins 以 `docs/generated/STATE.md` 為準（SessionStart 健檢應零分歧）→ 新刀起手依 CLAUDE.md §2 以 `/speckit-specify` 建分支。
- migration 檔名四碼（ADR-00008）、delta 自 `m0003` 起編（ADR-00010 決定 1）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
