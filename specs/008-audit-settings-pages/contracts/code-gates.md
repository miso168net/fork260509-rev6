# Contract — 機器守、治理面與帳本（008 刀）

## §1 fork-delta：管理頁軌道新用途 (ix)(x)、I18N (i) 三鍵

### 1.1 授權來源與硬序

授權鏈＝ADR-00099（proposed；條文字面 plan 期已逐款親決）→U0 銜接字面 diff 呈 user→accepted＋§III.2 兩新列與 I18N (i) 紀律欄改寫＋bump 1.9.0＋generate（§V.2 四步、獨立 commit）。★accepted 前 base-web **既有檔**零 diff（含 locale backend 子樹、`app.d.ts`、`request/index.ts`）；純新增檔（兩頁 view 與模組、`rev6-audit.{ts,d.ts}`）不受此閘。

### 1.2 ★軌道逐處登記（spec 登記表 9 列＋本 plan 補 1 列）

| 檔 | 用途 | 型別 | 出口應有值（預估；收刀前 PATCH 實數化） |
|---|---|---|---|
| `src/locales/langs/zh-cn.ts` | MANAGE (ix)(x)＋I18N (ii) | 新增型 | (ix) 2 塊、(x) 2 塊；backend 子樹於既有塊內補鍵＝0 增塊 |
| `src/locales/langs/en-us.ts` | 同上 | 新增型 | 同上 |
| `src/typings/app.d.ts` | (ix)(x)＋I18N (iii) | 新增型 | (ix) 1 塊、(x) 1 塊；backend 型節於既有塊內＝0 增塊 |
| `src/router/elegant/{imports,routes,transform}.ts`、`src/typings/elegant-router.d.ts` | 產物檔（沿 (i) 列授權） | 產物 | 重算冪等；產物檔集斷言 |
| `src/typings/components.d.ts` | 生成檔紀律 | 產物 | 稽核頁引入 `NDatePicker`（現檔未宣告）＝工具重算形（宣告行增） |
| `src/locales/langs/zh-tw.ts` | I18N (iii)＋各用途（rev6 自有檔） | 新增型 | 不入範圍欄 |
| **`src/service/request/index.ts`**（補） | I18N (i) | 新增型（既有圈界塊內補分支） | 範圍欄「2 處修改型＋2 塊新增型」不變；12m 0／24m 3＝低 |

### 1.3 新增型新檔（不入表、檔頭一行標記）

`src/views/manage/system-settings/index.vue`；`src/views/manage/audit/index.vue`；`src/views/manage/audit/modules/{audit-search-operation,audit-search-access,audit-search-login,audit-search-session,audit-purge-modal}.vue`、`use-audit-search-date-range.ts`；`src/service/api/rev6-audit.ts`；`src/typings/api/rev6-audit.d.ts`。rev6 自有檔之改動（`rev6-settings.d.ts` 擴欄、`hooks/business/pwd-policy.ts` 增清除函式、`views/manage/user/modules/user-reset-pwd-modal.vue` 檔頭句改述、`service/api/rev6-settings.ts` 碼註改現在式、`typings/api/rev6-user-center.d.ts` 明細型 JSDoc 改三鍵、`typings/api/rev6-{menu,role,user}-admin.d.ts` 與 `views/manage/ip-rule/index.vue` 之 ADR 改指註解；以檔頭 `rev6-inline` 新增型標記現算為準）不入表。

### 1.4 變更檔集機器斷言

各前端單元出口：`git -C base-web diff --name-only <基> HEAD` ⊆（1.2 表檔集 ∪ 1.3 新檔 ∪ rev6 自有檔〔檔頭首行帶 `rev6-inline` 新增型新檔標記者、現算〕∪ 既有授權用途檔中只改既有圈界塊內註解行者〔ADR 現在式改指；逐檔列名、`tools/fork-delta-lint.py` rc 0 即證落既有圈界內〕）；後兩類之修改型 `原行:` 增量為 0；收刀全量閘復跑。★U18 具名增列（user 2026-10-28 指令修個人中心換頁空白）：`src/views/user-center/index.vue` 只把既有 (vi) 修改型標記註解行自模板根層移入根元素內（模板根層註解於開發模式成多根片段、版面換頁過場卡住），歸入末類；`原行:` 淨 0、`tools/fork-delta-lint.py` rc 0。修改型標記只出現於授權三元組（fork-delta-lint 名冊斷言）。

### 1.5 新增圈界塊「拔標記必紅」

每一新增圈界塊各一支變異（拔塊首或塊尾標記）＝fork-delta-lint 紅。

## §2 python 閘與工具

### 2.1 `tools/msg-key-gate.py`

- `BIZ_DATA_KEYS` 增 `"biz.audit.purgeBelowFloor": "PurgeBelowFloorDetail"`。
- `FRONTEND_MSG_CONSUMERS` 增 `("service/request/index.ts", "biz.audit.purgeBelowFloor"): 1`（請求層明細轉譯第三分支之 msg 字面消費點；斷言 3 雙向全等、與前端分支同批落）。
- `DETAIL_HOME`（單檔）改逐鍵之家對映：兩既有鍵→`handler/user.rs`、新鍵→`handler/audit.rs`；`DEFAULT_DETAIL` 改名 `DEFAULT_DETAILS`（各家之 repo 根相對形、去重排序 tuple），與佔位符對賬讀檔同改依鍵取家。
- 射程守四句不變；不改模組層 `RE_*`。
- 自證（RL-0080）：新鍵之明細型欄改名＝佔位符對賬紅；新型移出其家＝紅；第三鍵構造點零處或兩處＝紅；既有兩鍵之對賬案重跑綠。
- pre-commit `submodule-sync` 段閘面增 `rust-api/server/src/handler/audit.rs`；`tools/docsync/tests/test_hook_wiring.py` 之閘面對賬同批。

### 2.2 `tools/schema-gate.py offline`（BL-00148；新子命令、零 docker）

- 輸入：`rust-api/migration/src/` 下 `m<四碼>_….rs`（四碼 ≥ 0003、依數值排序）、`docs/ops/reference-src/schema-evolution.json`、前值左源＝`specs/001-schema-baseline/fixtures/seed.sql` 之 COPY 段（m0002 之凍結證據；m0002 本身為多列 INSERT、無 COPY 段）⊕ 前序 delta 已配對之登記。
- 判準：①SQL 常數解析（`const` 字串、`concat!`、檔內 `macro_rules!` 字面；他形＝rc 2；SQL 之家限 `fn up`／`fn down` 本體內 `execute_unprepared(<SQL>)` 之引數與 `expect_rows(…)` 第三引數、本體他句形＝rc 2、未被引用之常數不入分類）②語句分類（seed DML／`setval`／權限面 DDL；未分類＝紅）③seed DML ↔ 該刀演進帳逐筆（表、pk、set／values 全欄）④前值 ↔ 前值左源（凍結 seed ⊕ 前序 delta 已配對之登記；UPDATE 與 DELETE 之 WHERE 所列各欄逐欄等於左源該列之值、不要求列全欄）⑤權限面 DDL 結構化列出（語句數、受權物件集）。
- 自測：真 repo 綠（m0003、m0004）；改壞常數值、少登一筆、改壞凍結前值、植未分類 DDL 各紅；逐判準停用變異各紅。
- 掛點：pre-commit 新段 `schema-offline`（`rust-api`、`tools/schema-gate.py`、`docs/ops/reference-src/schema-evolution.json` 任一 staged 時）；`check`（需 docker）不進常跑鏈。
- 時序：撰寫 m0004 之單元前落地、先對 m0003 綠。

### 2.3 runtime-append 兩工具（同值互釘）

`tools/schema-gate.py` 與 `tools/walkthrough-baseline.py` 之 `RUNTIME_APPEND_TABLES` 增 `"sys_access_log": "sys_access_log_id_seq"`；walkthrough `RESTORE_TABLES` 同批增 `sys_access_log`、`RESTORE_SEQUENCES` 同批增 `sys_access_log_id_seq`（基準檔模式 setval 回基準、seed 模式不復位）；名冊對賬自測（相等、⊆ 還原集、`SEED_SETVAL_SEQUENCES` 推導）綠；RUNBOOK §9c／§12 與 schema 閘收窄射程字面同批。

### 2.4 `tools/seed-view-gate.py`

`EXEMPT` 兩列各於交付該頁之單元摘除（U14 摘 `view.manage_system-settings`、U15 摘 `view.manage_audit`）；`TestExemptInvariants` 改斷言空表、`TestRunCheck` 之真表案改寫；現在式「恰兩列」字面改對、檔頭 rev5 原始版史述句不改。

### 2.5 `tools/route-artifact-gate.py`

兩頁 view 落地之單元重算產物四檔、冪等綠。

### 2.6 `tools/view-render-guard.py`

兩新目錄自動入腿①；稽核頁不用 `TableHeaderOperation`＝腿②錨表不擴（若實作期改用之＝同批擴錨表與自測）。

### 2.7 `tools/zh-tw-lint.py`

新增之 zh-tw 字面綠；動三檔 locale 之單元（U7、U14、U15）由腿②逼出 zh-cn 與 zh-tw 兩檔之未分類新字，逐字人審後只增列五張表值（`SIMPLIFIED_CHARS`／`_APPROVED_PLAIN`／`_APPROVED_HOMOGRAPHS`／`_HOMOGRAPH_TERMS`／`_HOMOGRAPHS_NO_TERM`）與其旁註、判準函式與模組層 `RE_*` 零改；腿①③命中一律改 `zh-tw.ts` 譯文、`EXEMPT` 維持 0 筆；若需改其正則判準＝該單元先跑 `python3 tools/regex-mutants.py run`（spec FR-062）。

### 2.8 `tools/fork-delta-lint.py`

新用途 (ix)(x) 列之名冊載入以變異自證（列之範圍欄反引號路徑改非路徑 token＝該檔掉出名冊即紅之對照）；範圍欄對賬腿於 PATCH 實數化後納入兩新列。

### 2.9 `tools/wire-schema.py`

`rev6-audit.d.ts` 新型與 `rev6-settings.d.ts` 擴欄之快照重抽；rust 側裁判同批。

### 2.10 `tools/docsync`

routes 生成表重算（66 條）；真 repo 釘值測 +5 列；動 ROUTES 之單元另跑 `python3 -B tools/docsync test`。

## §3 rust 側名冊閘與源碼釘

| 閘 | 本刀擴列 |
|---|---|
| `tests/authz_entrypoint_lint.rs` | `handler/audit.rs` 入判定面單一進入點與 handler 層零 path-root entity |
| `tests/entity_access_lint.rs` | 掃描面自動含 `model/audit_query.rs`、`model/retention.rs`、`reaper.rs`、`bin/reaper.rs` |
| `tests/wire_i64_guard_lint.rs` | 新 DTO 之 i64 欄 |
| `router.rs` 層序源碼釘 | `access_log_mw` 掛載恰兩處、各在其子 router 之 `enforce_mw` 掛載之前（內側） |
| `obs.rs` 序列名具名腿 | `access_log_write_failed_total` 只由出口與預註冊具名 |
| `error.rs` 名冊與矩陣 | `MSG_KEYS` 70、變體 11、13 碼不變 |
| `model/audit.rs` 字面釘 | 九詞 |
| `tests/system_audit_entry_lint.rs`（新；排程清理單元立） | 系統程序自記入口名冊四判準：生產面 `write_system_in_txn` 只在 `model/facade/sys_operation_log.rs`（定義）與 `model/retention.rs`（恰一處呼叫）；`SystemJob` 生產面只在 `model/audit.rs`、`model/retention.rs`、`model/facade/sys_operation_log.rs`、`reaper.rs` 四檔；`SystemJob` 零字串建構點（生產面 `impl … for SystemJob` 之 trait 零 `FromStr`／`From`／`TryFrom`／`Deserialize`、derive 零 `Deserialize`）；排程清理 job 本體 `run_audit_retention` 生產面只在 `reaper.rs`（恰一處定義）與 `bin/reaper.rs`（恰兩處、其中呼叫一處、定義零）（判準④，final holistic review 增）；各判準掃描面非空＋植入反例＋停用變異 |
| `handler/common.rs` 之 `each_domain_keeps_its_own_log_literals`、`EXTRACTION_SITES` | 入冊 `audit.rs`（拒寫事件字面＋body 收斂腿）與 `system_settings.rs`（拒寫事件字面）；抽取點 14→15（稽核讀端 `lenient_query`） |
| `handler/ip_rule.rs` 之 `production_code_emits_no_degraded_field` | 入冊 `audit.rs`、`system_settings.rs` |
| `tests/contract.rs` 之 `write_refusals_add_no_context_absent_leg_real_seed` | 寫端清單增 `purge-audit-log`、`update-system-setting` |

## §4 測試基建（U2 先於一切寫稽核表之單元）

- `AccessLogRowsGuard`、`PurgeSelfAuditGuard`（data-model §10）；`tests/common` 鏡像（`AccessLogWriteGuard`、`PurgeSelfAuditWriteGuard`）逐字對賬。
- 在途計數 drain：`middleware::access_log_pending()`；drain 於帶守衛 app 之逐回應層（上界 5 秒、逾時 panic 指名）；守衛 Drop 先確認在途歸零再清（current-thread 在途非零＝先清後 fail-loud）。
- app 建構 helper 內部帶守衛（`test_kit` 與 `tests/common` 兩層；守衛隨 Router clone 走、呼叫點零改寫）；驗收＝全量測試前後 `sys_access_log` 列數相等。
- 清理原子性注入：`test_kit::occupy_next_audit_id` 預佔操作日誌下一 id（自記必敗；手動與排程兩臂各一案、由清理寫端與排程清理單元自持）；拆回滾即紅之變異。
- reaper 權限測：`SET LOCAL ROLE reaper` 正負向（允許：四稽核表 SELECT／DELETE、`sys_operation_log` INSERT、`sys_token` SELECT／DELETE、授權三表 SELECT；拒：`sys_user` 任意寫、授權三表 INSERT／UPDATE／DELETE、`system_settings` 讀寫——SQLSTATE 42501）。
- 清理類真庫案前置斷言（R8.7）；reaper 真庫案以參數注入天數。

## §5 走查還原工具（`tools/walkthrough-baseline.py`）

- runtime-append 與還原集見 §2.3；走查期間不起 jobs profile。
- 首次真登入走查前 snapshot；007 終態基準於本刀自取基準後才可清。

## §6 觀測與告警

- rules.yml：③d 註解改現況（expr 不動）、④ 註解改述、⑤⑤b⑥⑥b 現況註改有源、⑦⑦b 新增（reaper-cli §8）。
- 儀表板：`rust-api.json` 刪面板 10／11／14、面板 13 移位擴寬；`reaper.json` 三面板（id 1／2／4）與 `master-overview.json` 面板 5 描述改 as-built（legend 以 `reaper_job` 分序列）；`audit-log.json` 面板 3 與變數 `trace_id` 描述改述。
- 活體驗證：觀測層單元可選起 obs／metrics profile、以合成推送證規則面；驗收單元之 jobs profile 活體一輪 metrics profile 必起（觀察三組心跳、⑤⑥⑦b inactive、⑦ 值 0）、obs 可選（未起時 Loki 規則之 health error 依 RUNBOOK §11.3 判為環境未起）。

## §7 ADR 與帳本

### 7.1 ADR accepted 時點

依 research R20：Amendment 顆（ADR-00099）→施工前提顆（ADR-00100／00101／00102／00104／00105／00107／00108）→CDP 後治理顆（ADR-00103、ADR-00106）；續行 ADR accepted 同顆補 `supersedes` 並改被續行者 status（ADR-00076、ADR-00081、ADR-00082、ADR-00091）。收刀前 PATCH Amendment 一支。

### 7.2 帳本

- `feature_close`：`backlog_done` 5 條（BL-00043／BL-00045／BL-00133／BL-00139／BL-00148）、零 `backlog_add`；`adrs` 列全（plan 期十支＋PATCH 一支）；`arch_impact` 以收刀 diff 現算；notes 收刀計數三則（spec FR-067）。
- 反向確認 2 條（BL-00108、BL-00002）入收刀前體檢紀錄。

### 7.3 收刀前承載體檢與 DoD 機器面（U19）

spec FR-075 全項；子句表檢核工具自證（空錨與錨不符計不符、核數＝總錨數）；Day-1 登記三步；errata 種子（spec FR-065＋research R21 追加詞）。
