# Contract — 治理面：fork-delta 軌道、機器守、走查工具、名冊落點、ADR 與帳本

> 承 003 刀 `contracts/code-gates.md` 形。本檔＝本刀治理交付物的機器可驗契約與落點總表；條文本體住 ADR-00034（draft、proposed）、規則本體住 RULES／憲法。

## §1 fork-delta 標記（憲法 §III；機器強制＝`tools/fork-delta-lint.py`）

- 新軌道 `★BASE-WEB-MANAGE-PAGE-WIRING (i)`：`src/locales/langs/{en-us,zh-cn}.ts`（`route:`／`page:` 兩樹各一塊新增型圈界 `[rev6-inline BASE-WEB-MANAGE-PAGE-WIRING(i)+ 004-ip-trust-anchor START/END]`）／`src/typings/app.d.ts`（`Schema.page.manage.ipRule` 型節一塊新增型圈界）／`src/router/elegant/{imports,routes,transform}.ts`＋`src/typings/elegant-router.d.ts`（產物檔：`is_generated` 豁免、禁手改、冪等由 §2 ② 守）。
- 既有授權內：backend 六鍵入三檔 backend 子樹（(ii)、既有圈界內擴列）＋`app.d.ts` backend 型節（(iii)）；`src/service/request/index.ts` onError 轉譯塊（(i)、新增型圈界擴）。
- 新增檔（免 ★）：`views/manage/ip-rule/{index.vue,modules/ip-rule-operate-drawer.vue,modules/ip-rule-search.vue}`、`service/api/rev6-ip-rule.ts`、`typings/api/rev6-ip-rule.d.ts`（檔頭新增型標記）。
- **五欄範圍實數化（G1、BL-00058）量法**（可重跑、量測日 2026-09-15）：修改型處數＝該檔 `原行:` 標記行數（`grep -c -F '原行:'`）、新增型塊數＝`START]` 圈界數（`grep -c -F ' START]'`）：

| 軌道·用途 | 檔 | 修改型 | 新增型塊 | 現行條文 → 實數 |
|---|---|---|---|---|
| AUTH (b) | code-login／register／reset-pwd | 各 1 | 0 | 「各 2 處」→「各 1 處，修改型」 |
| AUTH (c) | `hooks/business/captcha.ts` | 3 | 1 | 「約 4 處」→「3 處修改型＋1 塊新增型」 |
| LOGIN-CAPTCHA (i) | `store/modules/auth/index.ts`／`pwd-login.vue` | 3／2 | 0／2 | 「修改型」「修改型＋新增型」→「3 處修改型」「2 處修改型＋2 塊新增型」 |
| LOGOUT-UX (i) | `user-avatar.vue` | 1 | 0 | 「約 3 處」→「1 處，修改型」 |
| I18N (iii) | `typings/app.d.ts` | 0 | 1 | 「1 處，修改型」→「1 塊，新增型」（BL-00058） |
| （對照、不改）AUTH (a)／I18N (i)／I18N (ii) | route store／request/index.ts／en-us・zh-cn | 1／2／0 | 0／1／各 1 | 與現文一致 |

## §2 兩支新碼面閘（各附 self-test、植入反例必紅；RUNBOOK §12 碼面閘表登記、不計 GT-12 治理閘預算）

① `tools/view-render-guard.py`（承 `rev5:tools/view-render-guard.py` 282 行、新寫）：射程 `base-web/src/views/manage/**`；零 `v-html`／`innerHTML`／`outerHTML` 用法；環境缺席語意＝base-web 工作樹缺席即 fail-loud（ADR-00019 形）。
② `tools/route-artifact-gate.py`（承 `rev5:tools/route-artifact-gate.py` 605 行、新寫）：於 base-web 容器內**沙盒**重跑路由外掛重算（不就地改工作樹＝pre-commit 各閘唯讀）後與版控產物四檔 byte 比對＝冪等，另以上游基線為種重算一腿承擔「手改一行即紅」（外掛對 `routes.ts` 為增量合併、版控為種時手改行存活；★勘誤 2026-09-20：原文「容器外以 `pnpm` 重跑…後 `git diff --quiet`」——`node_modules` 住容器、`pnpm gen-route` 為互動腳手架非重算指令〔`rev5:L-053`〕）；斷言「憲法 §III.2 該軌道列所列產物檔集＝外掛實際產出檔集」（雙向差集即紅）；環境缺席（無 node）＝具名跳過（pre-commit 條件段）。
四處名冊同批：RUNBOOK §12 碼面閘表（兩列）／README 工具樹／`tools/bootstrap.sh` `run_tool_test`／`.githooks/pre-commit` 段＋`tools/docsync/tests/test_hook_wiring.py` SEGMENTS（msg-key-gate 前例）。

## §3 走查基準工具 `tools/walkthrough-baseline.py`（隨遷工具、`NON_GATE_TOOLS`；BL-00075、G6）

- restore 清理面：`RESTORE_TABLES` 3→5（＋`sys_ip_rule`／`sys_operation_log`，含其序列）。
- 新子命令／模式 `restore --seed`（以凍結 seed 為目標態、無須基準檔）：五表清列（TRUNCATE 或水位 DELETE）＋`sys_ip_rule` 序列 setval 回 seed 值；退出碼沿 0 已還原／1 有差／2 環境或結構異常／64 用法。
- `diff`：runtime-append 四表之序列**只比存在性、不比值**（與 schema-gate gate2 同口徑；restore 仍依基準檔 setval）。
- 自測：三案（擴面／seed 模式／序列存在性）離線樁。RUNBOOK §9c 契約句同批改（字面住工具常數、§9c 不抄）。

## §4 測試基建（G6、BL-00070）

- 廢 `SequenceResetGuard`（69 處 `::new()`／10 檔＋自證測＋doc）；新水位清理守衛住 `model/facade/test_kit.rs`：`sys_operation_log` 只刮自寫列（id 水位）、`sys_ip_rule` 清列＋setval；`SessionRowsGuard` 等既有守衛不動。
- BL-00070 七處收攏：`router.rs` `stub_state`／`lazy_db_state`、`enforce.rs` `state_with`、`system_settings.rs` 端點案、`route.rs`、`captcha.rs`（已委派）、`obs.rs`（具名留存、不讀 body）、`send`（通用送出殼、具名留存）→ 委派 `oneshot_json`；AppState 測試建構點收斂至 `test_kit`。
- 驗收＝dev 庫造一列真帳號殘列後 `cargo test --workspace -- --test-threads=1` 全綠。

## §5 boot 靜態掃描（BL-00072）

`main.rs` 內 `#[cfg(test)]` 以 `include_str!("main.rs")`（只掃測試模組分界之前的 production 段、去註解）斷言三條位序：`assert_jwt_secrets_distinct` 恰一處、位於 `captcha_secret()` 之後、`Database::connect` 之前；`cache::connect` 恰一處、位於 `Database::connect` 之後、`spawn_ipgate_watcher` 之前（watcher 之 URL 不可解析腿在 production 不可達、靠的是 cache 已先 fail-loud 驗過同一 URL）；`spawn_ipgate_watcher` 恰一處（as-built＝004 刀 U4）；附合成反例（文字變異）自證；`main.rs` 模組 doc 與 `config.rs` 檔頭「七支／七鍵」數量字面同批改對（RL-0011）。★`tests/serve_connect_info_lint.rs`（B-075）另守 `axum::serve` 實參形。

## §6 msg key 跨端閘（既有 `tools/msg-key-gate.py`）

`MSG_KEYS` 13→19（六鍵）；三檔 backend 子樹各 19、逐檔雙向全等；譯文權威句改（憲法 (ii)＋ADR supersede ADR-00029）；base-web 五處標記註解與 rust-api 四處 doc 之「權威＝003 契約」與手抄「13 鍵」改史料出處指針。

## §7 告警規則 `deploy/grafana-provisioning/alerting/rules.yml`（BL-00078）

刪 `obs016-throttle-suppressed` 規則塊＋②註解＋檔頭「告警六組 13 條」→12 與「LogQL 形（②③b③d）」「fields_suppressed」兩處；`obs016-ipgate-degraded` 錨改 `ipgate/mod.rs` as-built 事件欄；其餘不動。tools／hooks／rust-api 對 rules.yml 零引用（無計數斷言）。

## §8 RUNBOOK／README／活書落點總表

| 落點 | 內容 |
|---|---|
| RUNBOOK §16 | 部署 checklist 實文（FR-066；樣例＝`trust-model-config.md` prod 段） |
| RUNBOOK §9c | 還原面五表、seed 模式、序列存在性口徑一句 |
| RUNBOOK §12 | 碼面閘表＋兩列；工具鏈速查 walkthrough 列更新 |
| README | tools 樹兩行；憲法版本鏡像 1.4.0（U0） |
| 活書 05／06／08／10／11／12／01／03 | FR-068 as-built（§6 島 F 情境＋島 E 改寫；§12 詞彙含 `fallback` 撞詞） |
| LESSONS LL-00017 | 補述 G6 結構解 |

## §9 ADR 七筆（一決策一檔；序號＝落檔時取、現況 next＝ADR-00034；皆帶 rev5 provenance）

| # | 題 | 時點 |
|---|---|---|
| ADR-00034 | 主 Amendment 1.3.0→1.4.0（島 F＋島 E 四處＋§III.2 新軌道、I18N (ii)(i)、五欄精確化） | plan 期 draft（proposed）→ U0 accepted |
| ADR-00035（暫） | `AppState` 5→7（supersede ADR-00027） | U4 |
| ADR-00036（暫） | 節流判定面去負快取、每次由 PG 定案（BL-00066、Q7；含 `redis_down` 判定點） | U7 |
| ADR-00037（暫） | msg 譯文之家＝三檔 locale（supersede ADR-00029、承 ADR-00032 形） | U10 |
| ADR-00038（暫） | 轉發鏈超長拒絕與判定窗轉錄（F7／F8；`rev5:ADR 0043`） | U5 |
| ADR-00039（暫） | 三支依賴進場（R1） | U1 |
| ADR-00040（暫） | 本刀已知態集（解鎖無 UI／dev 二態／稽核不對稱／logout 弱 oracle／redis 持久化／wire 嚴格模式） | U10 |

## §10 帳本（收刀）

`backlog_done`＝BL-00058／00062／00066／00070／00072／00075／00077／00078（★勘誤 2026-09-20：另加 BL-00081＝本刀 U4 新增、U9 兌現之刀內條目，收刀事件之 `backlog_add` 與 `backlog_done` 兩欄同列、BACKLOG 同批刪列——final holistic review）；條文改寫＝BL-00028／00031／00042／00043／00045；`backlog_add`＝解鎖按鈕＋前端包裝（使用者管理頁刀）／全域 wire i64 守衛 lint（`rev5:B-111`）；NOTES 下一步→005。
