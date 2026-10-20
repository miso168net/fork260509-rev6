# Research — 008-audit-settings-pages（Phase 0）

> 取證＝主線唯讀親核（2026-10-21；無 workflow、未派 agent）：rev6 現況（rust-api `bba4a3d`、base-web `9fe562d`、外層 `926b359`）、rev5 凍結 worktree（`rev5:` 前綴；唯讀）、rev4 樹（`rev4:` 前綴；唯讀）、crates.io 公開 API（ureq 版本線）、rev6 dev 容器內 cargo registry 原始碼（`metrics-exporter-prometheus` 0.18.3）。
> 本檔「決定」皆為 plan 期定案；其中屬拍板級者已標出處（brainstorm 拍板／spec 條目／user 答覆），屬主線工程判斷者標「工程」並附判準一句。ADR 草稿之親決分類住各 ADR「親決分類」節（RL-0086），本檔不重抄。

## R1 技術脈絡

- **後端**：Rust 1.96.1（edition 2024）；axum 0.8.9、sea-orm 1.1.20、tokio 1.53.1、metrics 0.24.6、metrics-exporter-prometheus 0.18.3（`default-features = false`）、axum-prometheus 0.10.1、serde_json 1.0.151、tracing 0.1.44（`rust-api/Cargo.toml` 現讀）。容器內 build／test 全程 serial；真庫測試連 dev 庫（`config::database_url()`；`model/facade/test_kit.rs` 之 `real_db`）。
- **前端**：Vue 3.5.34／TypeScript 6.0.3／naive-ui 2.44.1／vue-i18n 11.4.2（`base-web/package.json` 現讀）；零前端測試框架＝型別檢查＋機器斷言＋兩段 review＋CDP 對照。
- **資料**：PostgreSQL 18.4；四稽核表與 `sys_token` 皆在 001 基線（欄形見 data-model §1）；本刀唯一 DDL＝m0004 之角色與權限面（R12）。
- **新依賴**：恰一項候選——pushgateway 心跳推送之 HTTP client（R11.6；ureq，版本待 user 依全域 §6 定）；其餘零新依賴、零版本變更。
- **部署面**：compose 既有 `reaper`（jobs profile）與 `pushgateway`（metrics profile）服務、密鑰產生器既產 `reaper_password`／`reaper_database_url`（角色名寫死 `reaper`：`deploy/generate-secrets.py` 之組合字串與 `deploy/setup-reaper-role.py` 之 `ALTER ROLE reaper`）；rust-api 容器不掛 `reaper_database_url`（最小權限分離、本刀不改）。

## R2 rev5 對應碼清單（後端）

藍本取 rev5 HEAD 形（rust-api 凍結 `92919b9`；`rev5:008` 之 U1～U9 收尾）。rev6 落點與差異點逐列；「差異」欄之編號指 R5。

| rev5 檔（`rev5:server/src/…`） | 內容 | rev6 落點 | 差異 |
|---|---|---|---|
| `handler/audit.rs` | 四讀端、四 query 型（全欄 `Option<String>`）、四 DTO、寬鬆 query 取用 `lenient_query`、`normalize_page`、`wire_success`／`wire_http_status`／`wire_ip`、`ipnet_to_wire`、purge 寫端（固定序①②③、`PurgeAuditTable`、`PurgeAuditLogReq`／`de_before_days`、`PURGE_MIN_DAYS`） | `server/src/handler/audit.rs`（新；讀端四支＋purge handler＋DTO＋query 型＋`PurgeBelowFloorDetail`） | ①②③④⑤ |
| `model/audit_query.rs` | `TimeRange`／`parse_time_range`、`PersonFilter`／`resolve_person_filter`、`mask_pii_payload`（`userPhone`／`userEmail`、深度一層） | `server/src/model/audit_query.rs`（新） | ⑥ |
| `model/facade/sys_operation_log.rs` | `write_in_txn`、`OperationLogFilter`／`list`、`purge_before`（收 `&DatabaseTransaction`、`operation <> 'purge'` 豁免臂） | 既有檔擴：`list`、`purge_before`、`count_before`、`write_system_in_txn`（新） | ⑦⑧ |
| `model/facade/sys_access_log.rs` | `AccessLogFilter`／`list`、`purge_before`（rev5 零寫入者） | `server/src/model/facade/sys_access_log.rs`（新；另加 `insert`） | ⑨ |
| `model/facade/sys_login_attempt.rs` | `LoginAttemptFilter`／`list`（`real_ip` 精確等值）、`purge_before` | 既有檔擴 | — |
| `model/facade/session_event.rs` | `SessionEventFilter`／`list`、`purge_before` | 既有檔擴 | — |
| `model/audit.rs` | `AuditOperation::Purge`（小寫 `purge`） | 既有檔擴（八詞→九詞、尾端追加） | ⑩ |
| `handler/common.rs` | `resolve_operator_names`（第二發批查）、`audit_operator`、`json_or_default`、`MAX_CURRENT` | rev6 既有對應件：`facade::sys_user::find_names_by_ids`、`common::operator_from_context`、`common::json_or_default`、`envelope::page_params`（`PAGE_MAX_CURRENT`／`PAGE_MAX_SIZE`） | ⑪ |
| `error.rs` | `biz.audit.invalidTable`／`biz.audit.purgeBelowFloor`、`BizData` 第三鍵 | 既有檔擴（`MSG_KEYS` 68→70、`msg_key` 兩常數） | ⑫ |
| `router.rs` | 五條接表尾、`ROUTES_COUNT` 61→66（rev5 為 65→66） | 既有檔擴（rev6 61→66） | — |
| `tests/wire_schema.rs`／`fixtures/wire-schema.json` | `Api.Audit` 受審型＋`PurgeAuditTable` 枚舉集裁判 | 既有檔擴 | — |
| `tests/authz_entrypoint_lint.rs` | 新 handler 檔入名冊 | 既有檔擴（判定面單一進入點、零 path-root entity） | — |
| （無藍本） | 設定寫端落稽核、設定讀 wire 擴充 | `handler/system_settings.rs`、`model/facade/system_settings.rs`、`validation.rs`（讀界值） | ⑬ |

## R3 rev5 對應碼清單（前端）

| rev5 檔（`rev5:src/…`） | 內容 | rev6 落點 | 差異 |
|---|---|---|---|
| `views/manage/system-settings/index.vue`（263 行） | 單檔、四組固定序（`PASSWORD_KEY_ORDER` 八鍵、`SESSION_KEY_ORDER`、`IP_KEY_ORDER`、`ACCOUNT_KEY_ORDER`）、`sortByFixedOrder`（未列鍵排組尾保相對序）、控件依 `settingType`、`numberRanges` 手抄五鍵 | `base-web/src/views/manage/system-settings/index.vue`（新） | ⑭⑮⑯⑰ |
| `views/manage/audit/index.vue`（621 行） | NTabs 四分頁、四組分頁表格、欄集、`scroll-x`＝欄寬總和、重新整理不重置頁碼、清理入口每分頁一顆（一般 `NButton`、非共用表頭元件） | `base-web/src/views/manage/audit/index.vue`（新） | ⑱⑲⑳ |
| `views/manage/audit/modules/audit-search-{operation,access,login,session}.vue` | 四支搜尋卡（同構、預設展開、重設觸發搜尋） | 同名新檔四支 | ㉑ |
| `views/manage/audit/modules/use-audit-search-date-range.ts` | 時間區間本地輸入→UTC ISO（`timeFrom`／`timeTo`） | 同名新檔 | — |
| `views/manage/audit/modules/audit-purge-modal.vue` | 清理浮層（標題帶表名、唯一欄保留天數、每開重置 30、無上界、浮層＋確認泡泡二段） | 同名新檔 | — |
| `service/api/rev5-audit.ts`／`typings/api/rev5-audit.d.ts` | 五支 fetcher、`Api.Audit` 型 | `rev6-audit.ts`／`rev6-audit.d.ts`（新；不入 barrel） | ㉒ |
| `service/api/rev5-settings.ts`／`typings/api/rev5-settings.d.ts` | 兩支 fetcher、`Api.SystemManage.SystemSetting` 四欄 | rev6 既有 `rev6-settings.ts`（零改）／`rev6-settings.d.ts`（擴三欄） | ⑬ |
| `locales/langs/{zh-cn,en-us}.ts` 之 `route:`／`page.manage.{systemSettings,audit}`／backend `biz.audit.*` | 兩語譯文 | rev6 三語（含 `zh-tw.ts`） | ㉓ |
| `typings/app.d.ts` 之 `Schema.page` 兩頁型節 | 型節 | 同 | — |
| `service/request/index.ts` 之明細轉譯 | 第三鍵 `{minDays}` 插值 | rev6 `translateBackendMsg` 之既有新增型圈界塊內補一分支 | ㉔ |

## R4 rev4 對應碼清單（reaper、存取日誌中介層、reaper role）

| rev4 檔 | 內容 | rev6 落點 | 差異 |
|---|---|---|---|
| `rev4:server/src/bin/reaper.rs`（659 行） | 兩 job（token-reap、audit-retention）、std args 極簡解析（未知參數嚴拒）、`dispatch_job`、`REAPER_GRACE_DAYS` fail-default 7、四表保留天數三分語意（`classify_retention_days` 純函式＋前置全驗先於連線）、`RetentionTable` 鏡像 handler 白名單、逐表單交易「刪＋自記」（`mutate_in_txn`）、心跳 `push_heartbeat`（PrometheusBuilder recorder＋ureq PUT、`timeout_global` 10 秒、grouping key `…/job/reaper/reaper_job/<job>`）、`resolve_database_url`（Result 形、拒空值與 `CHANGE-ME`） | `server/src/bin/reaper.rs`（新、薄殼）＋`server/src/reaper.rs`（新 lib 模組、job 本體） | ㉕㉖㉗㉘㉙ |
| `rev4:server/src/model/facade/sys_token.rs` 之 `reap_predicate`／`count_reap_candidates`／`reap_expired` | 判準 `expires_at < now() - make_interval(days => G)`（不分 status）、單語句 DELETE | rev6 `facade/sys_token.rs` 擴兩支 | ㉚ |
| `rev4:server/src/middleware/mod.rs` 之 `access_log_mw` | 掛 authed／policy 子 router 內側（enforce_mw 下游）、進入時擷取 method 與 `uri().path()`、`next.run` 後取 `status()`、回應先回再 `tokio::spawn` 寫入、缺 Claims 或 ctx 即跳過、失敗 `tracing::warn!(target: "audit.access_log", degraded = "access_log_write", …)` | rev6 `middleware/mod.rs` 擴 `access_log_mw` | ㉛㉜ |
| `rev4:server/src/router.rs` 之層序 | enforce_mw→access_log_mw→pwd_gate_mw→require_policy→handler | rev6 無 pwd_gate：enforce_mw→access_log_mw→require_policy→handler | — |
| `rev4:migration/src/m012_reaper_role.rs`＋`m013_reaper_audit_grants.rs` | `DO $$ CREATE ROLE reaper NOLOGIN EXCEPTION WHEN duplicate_object THEN NULL $$`、GRANT USAGE schema、`sys_token` SELECT／DELETE、四稽核表 SELECT／DELETE、`sys_operation_log` INSERT＋序列 USAGE；down＝REVOKE＋`DROP ROLE IF EXISTS` | rev6 一支 `m0004`（role、GRANT、授權域三表 SELECT、seed 兩筆同支）；down 之角色刪除改為無依賴時才刪（spec 三欄表 Rollback） | ㉝ |
| `rev4:` compose dev loop | 兩 job 以 `;` 分隔、`REAPER_INTERVAL_SECS` fallback 86400 | rev6 compose dev override 加第三 job | ㉞ |

## R5 rev6 拍板差異點（翻案與新增；implementer 防回歸清單）

翻案不帶回四項（spec Assumptions）：rev4 HLL 廣度估計、rev4 設定 TTL 快取觀測、`[rev5-inline]` 標記字面、前代 API 命名空間與檔名前綴（`rev5-`）。逐項差異：

1. 讀端 query 寬鬆取用沿 rev6 既有形（`impl FromRequestParts`、rejection 以 `common::query_rejection_summary` 入 debug 事件、原文不入＝BL-00143 之形），不帶 rev5 之 `lenient_query` 以 rejection `Display` 入 log 之形。
2. 分頁收斂取 `envelope::page_params`（`PAGE_MAX_CURRENT` 10^7、`PAGE_MAX_SIZE` 100），不另立 `normalize_page`；字串→數字之 trim-parse 件住稽核 handler（四支共用）。
3. purge body 收單取 `common::json_or_default`（rev6 簽章：`endpoint`、`msg` 兩參數、各域餵本域一句）；`de_before_days` 寬鬆形照 rev5。
4. 第三攜參鍵之明細以具名型 `PurgeBelowFloorDetail`（欄 `min_days`、struct 級 `rename_all = "camelCase"`）承載、單一組裝件構造 `BizData`——rev5 以 `serde_json::json!` 字面構造之形不帶回（rev6 明細鍵名之型別層單一出處＝ADR-00076 決定 7 之佔位符對賬面）。
5. 操作者取 `common::operator_from_context`（回 `Option`、拒寫 `tracing::error!` 留呼叫點帶本域 target `audit`）；rev5 之 `audit_operator`（共用件內發 log 並併 target）不帶回。
6. `resolve_person_filter` 之名→id 全集查詢經 facade（`sys_user` 新增「含已軟刪之同名 id 集」件），`model/audit_query.rs` 零 path-root `entity::`（受 `tests/entity_access_lint.rs` 掃描）。
7. 水平線刪除謂詞與自記之單一實作住 retention 共用核（R8），handler 與 reaper 共用——rev4 之 reaper 鏡像常數（`RETENTION_MIN_DAYS`、`RetentionTable` 鏡像 handler 私有 enum）不帶回（spec FR-019「直接引用同一常數」）。
8. 系統程序自記另立具名型與 facade 入口（R8.4）；rev4 之 `operator: None` 走同一事件型之形不帶回（rev6 `AuditOperator` 唯一建構點不動）。
9. `sys_access_log` facade 增 `insert`（rev5 零寫入者）；region／trace_id 恆 NULL（rev6 無料源；rev4 之 `resolve_region` 與 xdb 不帶）。
10. 動作詞彙小寫 `purge`（rev4 大寫 `PURGE` 不帶回）；只在尾端追加、字面釘值測同改。
11. 操作者與使用者名之第二發批查取 `facade::sys_user::find_names_by_ids`（空集零查詢）。
12. 新拒因兩鍵隨首發單元落地；`MSG_KEYS` 名冊、三檔 locale backend 子樹、`app.d.ts` backend 型節同批（I18N (ii)(iii) 既有授權）。
13. 設定寫端由「無交易、零稽核」改為「單交易：鎖讀→驗→寫→同交易稽核」（D1；R10）；讀 wire 擴三欄（`declared`、`rangeMin`、`rangeMax`；R10.3）——rev5 設定後端零改動之形翻案。
14. 數字框界值取讀端下發之宣告界、10 個 number 鍵一律鉗界（clarify Q1）——rev5 前端手抄 `numberRanges` 五鍵之形不帶回（`rev5:B-160`）。
15. 宣告集外列（`declared = false`）唯讀、排組尾、標示 description（工程判斷③）——rev5 依型別可編之形不帶回。
16. 三對跨鍵矛盾即時警示（D2）、寫入政策七鍵任一成功即清同分頁政策快取（D3）——rev5 無。
17. label＋help 三語全映射；帳號登入與 IP 源登入兩組說明不承諾嚴格上限（BL-00145 約束）。
18. 存取日誌分頁有資料、上方告示只提 403（R9.6、R24 E1）；登入嘗試分頁告示照 rev5 語意。
19. 清理鈕依 `audit:purge` 碼顯隱（D6）——rev5 頁內零按鈕級 gating 之形翻案。
20. 操作日誌搜尋卡之動作提示用庫內小寫字面（`update`、`kick`）——rev5「如 UPDATE、KICK」不帶回（大小寫敏感等值、照輸查無）。
21. 搜尋卡之型別取 `Api.Audit.*SearchParams`（rev6 命名空間）；rev5 檔名前綴不帶。
22. wrapper／typings 檔名 `rev6-audit.{ts,d.ts}`、檔頭一行 `rev6-inline` 標記（§III.1 WRAPPER／ADAPT）。
23. 三語同批（ADR-00084 決定 11）：`zh-tw.ts` 為 rev6 自有之整檔新增型檔、以完整 `App.I18n.Schema` 標型＝三語鍵集型別守。
24. `translateBackendMsg` 第三分支以 wire 型 `Api.Audit.PurgeBelowFloorDetail` 收窄取值、具名參數以其鍵構造（沿既有兩分支形）；須 Amendment 改 §III.2 I18N (i) 紀律欄「只限兩鍵」（R19、R24 E2）。
25. reaper 之 job 本體移入 lib 模組（可用 `test_kit` 真庫測、bin 只留 CLI／env／連線／退出碼／心跳）；rev4 全在 bin 檔之形不帶回。
26. reaper 第三 job `policy-reconcile`（B4；rev4 無）。
27. 排程清理自記列來源位址＝哨兵 `0.0.0.0`（g2）——rev4 寫 NULL 之形帶不進來（`sys_operation_log.real_ip` INET NOT NULL＝001 data-model 前瞻註）。
28. 心跳推送之 HTTP 實作與版本依 R11.6（全域 §6）。
29. 連線字串解析取 reaper 本地 Result 形（同 rev4、拒空值與 `CHANGE-ME`）——`config::env_or_file` 之 panic 形不用於 reaper（退出碼契約）。
30. token-reap 不落操作日誌自記（spec FR-032、rev4 形）；判準照 rev4。
31. 存取日誌中介層之寫入併發以號誌上限 2 收斂、另立在途計數供測試 drain（R9.4；rev4 每請求無上限 spawn 不帶回）。
32. 寫入失敗之降級計數 `access_log_write_failed_total`（rev6 新；③d 之 loki 腿照 rev4 欄形）。
33. m0004 一支含角色、GRANT（含授權域三表 SELECT＝B4 新增）與 seed 兩筆（D6）；rev4 兩支拆法不帶。
34. dev loop 三 job 依序（token-reap→audit-retention→policy-reconcile）、`;` 分隔（失敗互不阻斷）。

## R6 模組邊界與共用件落點

| 件 | 落點 | 理由（工程） |
|---|---|---|
| 四讀端、purge handler、DTO、query 型、`PurgeBelowFloorDetail` 與其組裝件 | `server/src/handler/audit.rs`（新） | 端點群一檔（005～007 形）；明細型與組裝件同住（ADR-00076 決定 1 之形） |
| `TimeRange`、`PersonFilter`、時間與人員解析、打碼 | `server/src/model/audit_query.rs`（新） | 純函式為主、名對應經 facade；與 handler 分開以便 reaper 不必依賴 handler |
| retention 共用核：`PURGE_MIN_DAYS`、`RetentionTable` 四值（wire 值、表名、環境變數鍵）、`purge_with_self_record`、`count_before` 分派、`PurgeActor` | `server/src/model/retention.rs`（新、`pub`） | 手動與排程清理同謂詞同自記形之結構保證（島 J3 一條規則）；reaper bin 以 `server::model::retention::*` 引用（同 crate 之 lib、不鏡像） |
| 系統自記具名型 `SystemJob` | `server/src/model/audit.rs`（擴） | 與 `AuditOperator`／`AuditOperation` 同家；欄位私有、只收碼內字面 |
| 四源 `list`／`purge_before`／`count_before`、`sys_access_log::insert`、`sys_operation_log::write_system_in_txn` | 四支 facade（三擴一新） | 層規則：碰表只走 facade |
| 存取日誌中介層 `access_log_mw`、層狀態（db＋號誌）、在途計數 | `server/src/middleware/mod.rs`（擴） | 與 `request_context_mw`／`ip_gate_mw` 同家 |
| 降級計數出口 `access_log_write_failed()` | `server/src/obs.rs`（擴；預註冊 `increment(0)`） | 既有出口形與「序列名只由 obs 具名」機器守 |
| reaper job 本體（CLI 解析、環境變數三分語意、三 job、連線字串解析） | `server/src/reaper.rs`（新 lib 模組） | 可測性（R5-25） |
| reaper 進場點（tracing、退出碼、心跳推送） | `server/src/bin/reaper.rs`（新） | cargo autobins：`src/main.rs`＝`server`、`src/bin/reaper.rs`＝`reaper`；compose dev 既以 `--bin server` 啟 server、`--bin reaper` 啟 reaper |
| 對賬三維計數 | `facade/sys_casbin_policy.rs`（擴：唯讀計數件） | 授權表讀寫之既有家 |
| 名→id 含軟刪全集 | `facade/sys_user.rs`（擴） | 同上 |
| 設定鎖讀與交易內更新 | `facade/system_settings.rs`（擴） | 同上 |

★同 crate 雙 bin 之連帶：`src/bin/reaper.rs` 引用之 lib 件須為 `pub`；`server` bin 與 `reaper` bin 共用 `rust_api_target` 卷、cargo 檔案鎖序列化（compose dev 註解既載）。

## R7 四源讀端與打碼（島 J1、J4；spec FR-006～FR-014）

1. **決定（承決＝spec FR-007～FR-012；形照 rev5）**：四支讀端只讀、零寫入；固定序 `created_at DESC, id DESC`；分頁 `page_params`；時間 RFC3339 閉開、畸形＝未設、顛倒＝空頁短路（不下 SQL）；人員過濾 id 優先、名→含已軟刪同名全集、零命中＝空頁短路；等值欄空字串＝未設；路徑與帳號名部分字串（ILIKE、`%`／`_`／`\` 字面化）；登入嘗試來源 IP 精確等值（`IpNetwork::from(IpAddr)`＝/32、/128）；成敗嚴格 `true`／`false`。
2. **只讀交易（工程）**：四支以 `begin_with_config(None, Some(AccessMode::ReadOnly))` 開唯讀交易包住清單與計數兩查詢（同一快照、總數與列一致）；J1 之機器守＝測試以寫入計數前後相等＋唯讀交易內任何寫入被資料庫拒之負向案。判準：J1「純唯讀」由資料庫強制最硬、不靠自律。
3. **打碼（承決＝D9、spec FR-013）**：`mask_pii_payload` 單點、讀端序列化前對 `payload_before`／`payload_after` 各一次；鍵常數 `userPhone`／`userEmail`（rev6 使用者寫端快照鍵＝`handler/user.rs` 之 `audit_snapshot` 現讀）；手機 `chars().count() > 5`＝前 3＋`****`＋後 2、否則 `****`；信箱含 `@`＝首字＋`***`＋`@網域`、否則首字＋`***`；非字串、缺席、巢狀、非物件快照原樣。拆除即紅之機器守＝讀端案斷言打碼後字面（非 vacuous：植列含兩鍵）。
4. **IP 欄 wire 形（形照 rev5）**：INET 單址欄去前綴（`ip().to_string()`）；`session_event.source_ip` 為 `varchar(45)` 字串照回。
5. **授權拒絕與存取日誌**：讀端自身之請求亦經存取日誌中介層落列（R9）；J1 之測試射程＝讀端 handler 與其交易（spec FR-007）。

## R8 水平線清理（手動）與 retention 共用核（島 J3；spec FR-015～FR-020、FR-033、FR-036）

1. **固定序（承決＝spec FR-016）**：①`table` 白名單→②`beforeDays ≥ PURGE_MIN_DAYS`→③操作者解析→④單交易。①②③皆不觸 DB。`PurgeAuditLogReq` 寬鬆收單（`json_or_default`；壞形收斂成 `table` 缺席＝①拒）。
2. **共用核（工程）**：`model::retention::purge_with_self_record(db, table, before_days, actor) -> Result<u64, DbErr>`——開交易→`table.purge_before(&txn, days)`（四源 facade 分派；操作日誌版帶 `operation <> 'purge'` 豁免臂、豁免字面取 `AuditOperation::Purge.as_str()`）→同交易自記→commit→回刪除數。handler 之④與 reaper audit-retention 之逐表執行皆經此一支。判準：J3「手動與排程同一條規則」以單一實作承擔、不靠兩處對齊。
3. **謂詞（形照 rev5）**：`created_at < now() - ($1 * interval '1 day')`（SQL `now()`＝交易時戳、免時鐘偏移）；`count_before` 與 `purge_before` 共用同一謂詞字串常數（dry-run 候刪數＝將刪數）。極大天數致時間不可表示＝資料庫拒（interval overflow）→整筆回滾→handler `5000`／reaper 該表失敗退出（spec Edge Cases）；以 `before_days = i64::MAX` 之真庫案釘住不崩潰。
4. **自記兩路（承決＝g2、g5、spec FR-036；形制＝工程）**：
   - HTTP 寫端：`AuditEvent { operator: AuditOperator, operation: Purge, entity_table: 目標表名, entity_id: None, before: None, after: {table, before_days, deleted_count} }` 經既有 `write_in_txn`。
   - 系統程序：新型 `SystemJob`（封閉 enum、現恰一值 `AuditRetention`＝`"audit-retention"`；欄位私有、無自由字串建構點）＋`SystemAuditEvent { job, operation, entity_table, entity_id, before, after }` 經新入口 `sys_operation_log::write_system_in_txn(txn, event)`——落 `created_by` NULL、`real_ip`＝哨兵 `0.0.0.0`（常數只住該 facade）、`peer_ip`／`x_forwarded_for`／`ip_confidence` NULL；`after` 由共用核組為 `{table, before_days, deleted_count, job}`。
   - `PurgeActor { Operator(AuditOperator), System(SystemJob) }` 由呼叫端給定；HTTP 寫端「上下文缺席拒寫 `5000`」照舊（`AuditOperator::from_context` 唯一建構點不動）。`model/audit.rs` 檔頭「沒有『自己填一個位址』的路」句改述為兩路現在式：HTTP 路恆轉錄請求上下文；系統路恆為哨兵且操作者空——兩路之構造點互斥、皆無自由位址參數。
   - 判準：哨兵只能經「無操作者之系統程序」構造（型別層），HTTP 路徑物理上拿不到哨兵（R13 之防外溢）。
5. **刪 0 列照落（承決＝g5）**：共用核不因 `deleted == 0` 早退。
6. **原子性 fault-injection（承決＝spec FR-018；形制＝工程）**：共用核以泛型連線之內部件承載注入點（同 `sys_operation_log::insert_row` 之「泛型連線只為測試注入」形）——測試以「刪除成功、自記必敗」之注入連線（自記語句命中時回合成 `DbErr`）跑一次，斷言回錯誤、零刪除（植列仍在）、零自記；並以拆除「自記失敗即回滾」之變異證案轉紅（RL-0080）。不新增 `AppState` 建構字面（測試側沿用 `test_kit` 既有建構件）。
7. **真庫保護（工程；承 `rev5:` 形）**：清理類真庫案一律①長水平線（3650 天）②植列 4000 天前③執行前斷言「水平線前恰為本案所植之 N 列」、不等即拒跑（防刪到 dev 庫之真實舊稽核列）④操作者取合成 uid（≥ `SYNTHETIC_UID_FLOOR`）圈自記列。reaper audit-retention 之真庫案同形（以函式參數注入天數、不經環境變數）。
8. **永久豁免與量**：每日一輪排程清理每年約 1,460 列自記不可清（g5）；操作日誌分頁可依動作或操作者篩除。

## R9 存取日誌寫入中介層（島 J2、ADR②；spec FR-021～FR-025）

1. **掛點（承決＝㉒、spec FR-021；形＝工程）**：`router::build_from` 之 Authed 與 Policy 兩子 router 各改為 `.layer(access_log).layer(enforce_mw)`（後掛者在外）＝enforce_mw 先跑、access_log_mw 次之、Policy 條目之 `require_policy` 在其內側。效果：授權拒絕（`5003`）照記且狀態 403；認證失敗（`8888`／`3333`／`7777`）由 enforce_mw 早退、不入記錄層＝零列；Public 子 router 不掛＝未認證零列；兩道 fallback（未註冊路徑、動詞不符＝`4040`）掛在合併後之外層、不經兩子 router 之 layer＝零列。`router.rs` 既有之層序源碼釘值測擴列（access_log 兩處掛載、皆在各自 enforce_mw 掛載之前一個 `.layer(`）。
2. **欄位（承決＝spec FR-022）**：`created_by`＝`Identity.uid`；`http_method`＝`method().as_str()`；`http_path`＝`uri().path()`（不含 query、不讀 body）；`http_status`＝`response.status().as_u16()`；來源四欄轉錄 `RequestContext`（`real_ip` 字串→`IpAddr` 解析不成＝跳過寫入）；region／trace_id NULL。
3. **非同步與 fail-open（承決＝spec FR-023；形照 rev4）**：`next.run` 取回應→擷取欄位→`tokio::spawn` 寫入→回應立即返回；身分或上下文缺席＝跳過（debug 事件、不 panic、不 500）；寫入失敗＝`tracing::warn!(target: "audit.access_log", degraded = "access_log_write", error = %e, …)`＋`obs::access_log_write_failed()`（計數 `access_log_write_failed_total`），業務回應零影響。
4. **R3 對策（工程）**：
   - **連線池壓力**：層狀態持 `Arc<Semaphore>`（許可 2＝碼內常數 `ACCESS_LOG_WRITE_CONCURRENCY`）；spawn 之任務內 `acquire().await` 後才取連線寫入——存取日誌同時佔用之連線數上界 2、業務請求不被寫入洪峰擠滿；不丟列（等待許可、非 `try_acquire`）。連線池設定零改動（BL-00147 之臂不觸）。判準：上界常數化＝可推理之最壞佔用；丟列違「每筆一列」。代價＝庫故障時待寫任務於記憶體排隊（同期業務請求亦失敗、恢復後消化）＝記入 ADR② 後果。
   - **測試收尾**：中介層維護在途計數（spawn 前 +1、任務結束 −1；`middleware::access_log_pending()` 讀值）；`test_kit` 與 `tests/common` 各增 `AccessLogRowsGuard`（arm 取 `max(id)` 水位；Drop 先等在途歸零〔上界 5 秒、逾時 panic 指名〕再刪 `id >` 水位之列；兩份逐字對賬）；app 建構 helper 回傳帶守衛之包裝（全套件零殘列；呼叫點約 150 處為機械改寫、於測試基建單元一次落）。驗收＝全量測試前後 `sys_access_log` 列數相等（quickstart §9）。
   - **斷言形**：存取日誌案取水位窗＋合成 uid 圈列、先 drain 再斷言；不寫絕對計數（FR-070）。
5. **runtime-append 兩工具（承決＝spec FR-025）**：`tools/schema-gate.py` 與 `tools/walkthrough-baseline.py` 之 `RUNTIME_APPEND_TABLES` 同值擴入 `"sys_access_log": "sys_access_log_id_seq"`；walkthrough 之 `RESTORE_TABLES` 同批納入（該工具自測斷言 runtime-append 集 ⊆ 還原集）；兩工具名冊對賬自測照跑。
6. **狀態欄之 as-built 語意（R24 E1）**：rev6 之 `4040` 只由 `router.rs` 兩道 fallback 構造（`AppError::NotFound` 之生產構造點恰兩處、業務 handler 零構造），而 fallback 不經記錄層——存取日誌之狀態欄實際只見 200 與 403。告示文案只提 403（msg-keys contract；緣起＝user 2026-10-21 轉來 side agent 提醒、與主線取證同結論；user 2026-10-21 plan 期 AskUserQuestion 親決「只提 403」）。
7. **不入登入路徑**：登入、換發、登出、驗證碼皆 Public＝不經記錄層（BL-00145 之「改動判定次序」臂不觸）。

## R10 系統設定後端（D1、clarify Q1、ADR⑧／⑧′；spec FR-026～FR-029）

1. **寫端改形（承決＝D1、g4、spec FR-027；鎖形＝工程）**：`update_system_setting` 改收 `Option<Extension<RequestContext>>`；固定序＝①請求上下文（缺席或位址不可解析＝`5000`、先於一切；ADR-00091 決定 8「各域同」之兌現）→②必填欄（缺席或 null＝`2222`）→③開交易、`find_by_key_for_update`（`FOR UPDATE`；查無或已軟刪＝`notFound`）→④型別一致性守衛→⑤`validate`→⑥`update_by_key_in_txn`（`RETURNING` 取寫後整列）→⑦`write_in_txn`（`update`、`system_settings`、`entity_id` None、before／after＝整列快照）→commit。快照形＝camelCase 整列（`settingKey`、`settingValue`、`settingType`、`description`、六審計欄；同 `handler/ip_rule.rs` 之 `audit_snapshot` 形）。判準：鎖讀使 before 快照與寫入同一版本、並行寫入不致快照錯位。
2. **同值寫入（承決＝D1 字面、spec FR-028）**：照寫（審計欄重寫）並照落一列稽核（前後快照之業務四欄相同、審計欄不同）。
3. **讀 wire 擴充（承決＝工程判斷③、spec FR-026；欄名＝工程）**：`SettingItem` 增 `declared: bool`（恆在場；鍵在 registry 宣告集內＝true）、`range_min`／`range_max: Option<i64>`（`skip_serializing_if = "Option::is_none"`；只在 `declared ∧ number` 時給值；值取 `validation::range_of`＝REGISTRY 單一權威）。`rev6-settings.d.ts` 之 `SystemSetting` 同批擴 `declared: boolean`、`rangeMin?: number`、`rangeMax?: number`；wire-schema 快照重抽；ADR-00054 翻案觸發器不成立（不另立界值真源）。
4. **碼註順改（承決＝⑬、spec FR-029）**：「rev5 後刀的同 txn op-log 不帶回」改述為「rev4 之同交易稽核不帶回」之史述已失真——本刀起設定寫端即同交易落稽核；裸引之 research 條號補前綴。改 assert 訊息時容器 cargo 驗。
5. **部分更新語意之續行（工程；R24 E3）**：設定域之翻案觸發器（「系統設定寫端重寫或出現清空 UI 需求」）現行承載＝ADR-00091（續行 ADR-00080）；其決定 8 逐域差異表為「單一出處」、設定域「同值出現」格「照寫、零稽核」於 D1 後失真＝須新 ADR 續行並 supersede ADR-00091（ADR-00107 草稿：決定 1～7、9 原文續行、決定 8 設定域兩格改寫、觸發器重評結論＝空字串語意維持）。
6. **設定頁授權不下放（承決＝工程判斷④）**：設定兩端點（列 66／67）續為封死集；選單維可見性可授（ADR-00081 款 10 改述）。

## R11 reaper 三 job（B1、B4、D8、ADR③；spec FR-030～FR-038）

1. **CLI（承決＝spec FR-030；形照 rev4）**：`--execute`（缺席＝dry-run）、`--job <name>`（`token-reap` 預設｜`audit-retention`｜`policy-reconcile`）；未知參數、`--job` 缺值、未知 job＝`tracing::error!(target: "reaper", …)`＋退出 1；完跑（含 0 列）＝0。
2. **環境變數（承決＝D8、spec FR-034）**：四表保留天數三分語意（缺席 90、畸形 warn＋90、解析成功且 `< PURGE_MIN_DAYS`〔含 0〕＝開跑前四鍵一次全驗、聚合指名、退出 1、不推心跳、先於連線字串解析與連線）；`REAPER_GRACE_DAYS` 缺席或畸形退 7（畸形 warn）；判定核為純函式、吃 `Option<&str>`（免測試改 process env）。
3. **token-reap（承決＝spec FR-032）**：`sys_token::count_reap_candidates`／`reap_expired`（rev4 判準）；不落自記；只結構化日誌＋心跳。
4. **audit-retention（承決＝spec FR-033、FR-036）**：固定表序四表、逐表經 retention 共用核（`PurgeActor::System(SystemJob::AuditRetention)`）；dry-run＝逐表 `count_before`；任一表失敗＝error 事件指名表＋退出 1＋不推心跳（已 commit 表維持）。
5. **policy-reconcile（承決＝B4、g3、spec FR-035；SQL 形＝工程）**：唯讀三維計數（`ptype = 'p'`）：
   - 選單維（`v2 = 'menu'`）：`v1` 不在「未軟刪選單之路由名」集、或 `v0` 不在「未軟刪角色之代碼」集；
   - 按鈕維（`v2 = 'button'`）：`v1` 不在「未軟刪選單之按鈕碼聯集」（`governed_button_codes` 同源）、或 `v0` 同上；
   - 端點維（`v2 ∈ endpoint_methods()`）：`(v1, v2)` 不在 `router::policy_endpoints()`、或 `v0` 同上；
   每列每維至多計一次；有無 `--execute` 皆零寫入（執行後授權三表逐列不變之案）；結構化日誌指名三維計數＋總數；心跳推 `reaper_orphan_policies{dimension}` 三序列＋`reaper_last_success_timestamp{mode}`。全新 seed（m0001～m0004）＋本刀五支註冊後三維皆 0（端點維今之候選外現役列恰為 seed 列 139／140／141／158／159）。
6. **心跳推送之 HTTP 實作（spec FR-037、R5 風險；比較＝工程、版本＝user plan 期親決 3.4.2）**：

   | 案 | 形 | 新增 crate（相對 rev6 lockfile） | 一次性 CLI 之適配 | 結論 |
   |---|---|---|---|---|
   | 甲 | `metrics-exporter-prometheus` 0.18.3 之 `push-gateway`／`push-gateway-no-tls-provider` feature（`with_push_gateway(endpoint, interval, …)`） | `hyper-rustls`、`rustls-native-certs` 起（`push-gateway` 另帶 `aws-lc-rs`）＋既有 `hyper`／`hyper-util` 開 client feature | 不適：推送器為「sleep(interval)→render→PUT」之永不返回迴圈、成敗只入其內部 `tracing::error!`、無完成訊號；啟動時 `CryptoProvider::get_default().expect(…)` 與原生根憑證缺席之 `expect` 皆可 panic＝改變退出碼（違 spec FR-030「推送失敗不改退出碼」） | 棄 |
   | 乙 | ureq（rev4 藍本形：recorder 之 `PrometheusHandle::render()`＋`Agent` 設 `timeout_global` 10 秒＋`put(url).send(body)`） | `ureq`、`ureq-proto`、`utf8-zero`（3.3.0）；3.4.2 另加 `base64` 0.23 | 適：同步一發、回 `Result`、全程時限明設、`default-features = false`＝純 HTTP（pushgateway 在 compose 內網） | **採** |
   | 丁 | 既有 `hyper` 1.11.0 之低階 client（`client::conn::http1::handshake`＋`TokioIo`） | 零（既有 crate 開 `client` feature） | 可：需手寫連線、Host 標頭、body 型與逾時約 30 行 | 棄：偏離 rev4 藍本、自寫 HTTP 管線之審查面大於三支小 crate |

   對所選方案跑同一反例（RL-0013）：「推送端黑洞時卡死 loop」於乙是否成立？不成立——`timeout_global` 給端到端上界、逾時走 `Err`＝error 事件＋照常返回。「推送失敗改變退出碼」？不成立——推送在 job 完跑後呼叫、結果只入日誌。「新增 crate 擴大供應鏈」？成立（擇 3.4.2＝四支：`ureq`、`ureq-proto`、`utf8-zero`、`base64` 0.23；純 Rust、無 TLS）——接受，版本依全域 §6 交 user（R20 待決題、已答）。
   **版本兩源**：參照專案（rev4）lockfile＝`ureq 3.3.0`（其下 `ureq-proto 0.6.0`）；crates.io 最新穩定＝`3.4.2`（2026-09-13 發布；其 `ureq-proto ^0.6.3` 之最新相容版 0.6.5 為 2026-10-17 發布、要求 `base64 ^0.23.1`）。兩源分歧＝依全域 §6 呈 user 擇一：user 2026-10-21 plan 期 AskUserQuestion 擇「3.4.2，官方最新穩定版」（非建議項；建議項為 rev4 驗證過之 3.3.0＋`ureq-proto` 0.6.0）——workspace 釘 `ureq = { version = "3.4.2", default-features = false }`、lockfile 解析 `ureq-proto` 0.6.5 與 `base64` 0.23.1（與既有 `base64` 0.22.1 兩大版本並存）；答覆記 ADR③（ADR-00101）親決紀錄。
7. **心跳形（承決＝spec FR-037；名＝工程）**：grouping key `…/metrics/job/reaper/reaper_job/<job>`、PUT 整組替換；`reaper_last_success_timestamp{mode}`（三 job）、`reaper_deleted_total{mode}`（token-reap 與 audit-retention；dry-run＝候刪數）、`reaper_orphan_policies{dimension}`（policy-reconcile）；推送 best-effort、只在完跑後、失敗只 error 事件。
8. **連線（承決＝spec FR-031）**：`APP_DATABASE_URL_FILE`（compose 既設為 `reaper_database_url`）優先、`APP_DATABASE_URL` 次之；Result 形解析（R5-29）。
9. **reaper role 權限測（工程；R24 E4）**：rust-api 容器不持 reaper 憑證——權限之正負向測以 `soybean`（bootstrap 超級使用者）連線、交易內 `SET LOCAL ROLE reaper` 後執行允許語句（成功）與權限外語句（`permission denied`、SQLSTATE 42501）再回滾；以 reaper 憑證之實連驗證由 `deploy/setup-reaper-role.py` 之自驗（`SELECT 1`）與 jobs profile 活體一輪承擔（quickstart §12）。判準：測試射程是角色之權限集、非密碼；把 reaper 憑證掛進 server 容器違最小權限分離。

## R12 m0004、演進帳、序號合成、BL-00148 離線對賬腿（ADR⑨；spec FR-039～FR-042）

1. **檔名與內容（承決＝D6、B1、B4、spec FR-039；語句形＝工程、形照 m0003）**：`rust-api/migration/src/m0004_reaper_role_and_audit_purge.rs`；`lib.rs` 遷移向量第四支。up 依序：
   - S1 角色：`DO $$ BEGIN CREATE ROLE reaper NOLOGIN; EXCEPTION WHEN duplicate_object THEN NULL; END $$`（rev4:m012 形；已存在即略過）。
   - S2～S7 GRANT（六條）：schema `public` USAGE；`sys_token` SELECT, DELETE；`sys_operation_log, sys_access_log, sys_login_attempt, session_event` SELECT, DELETE；`sys_operation_log` INSERT；`sys_operation_log_id_seq` USAGE；`casbin_rule, sys_menu, sys_role` SELECT。
   - S8 選單 77 按鈕清單：`UPDATE sys_menu SET buttons = '[{"code":"audit:purge","desc":"清理日誌"}]'::jsonb WHERE id = 77 AND buttons IS NULL`（影響列數期望 1）。
   - S9 新授權列：`INSERT INTO casbin_rule (id, ptype, v0, v1, v2, v3, v4, v5, protected, created_at, created_by) VALUES (165, 'p', 'R_SUPER', 'audit:purge', 'button', '', '', '', FALSE, '2026-08-05T00:00:00+00:00', NULL)`（期望 1）。
   - S10 序列：`SELECT setval('casbin_rule_id_seq', GREATEST(165, (SELECT last_value FROM casbin_rule_id_seq)), true)`。
   - down 反序：刪列 165（期望 1、全欄比對）→選單 77 回 NULL（期望 1、比對新值）→REVOKE 各 GRANT→角色無依賴時刪除（`DO` 塊內 `DROP ROLE IF EXISTS reaper`、捕 `dependent_objects_still_exist` 即略過並 `RAISE NOTICE`；spec 三欄表 Rollback；`rev4:m012` 之無條件 DROP 不帶）→setval 回推形照 m0003。
   - 影響列數斷言件 `expect_rows` 照 m0003 形（不符＝整支回滾、遷移帳不記）。
2. **新列 id 與冪等（工程）**：新列 id 顯式 165（m0003 形）；dev 庫序號若已因走查前進（`last_value` ≥ 165）而 id 165 已被執行期新增列佔用＝INSERT 撞 PK 即整支失敗——處置＝走查基準還原後重跑（spec 三欄表第 4 列）；全新庫序號合成期望值隨之推進。
3. **演進帳（承決＝spec FR-040）**：`E-010` `seed_update` `sys_menu` `{pk:{id:77}, set:{buttons:"[{\"code\": \"audit:purge\", \"desc\": \"清理日誌\"}]"}}`；`E-011` `seed_add` `casbin_rule` `{pk:["id"], values:{id:165, …, created_at:"2026-08-05 00:00:00+00", created_by:null}}`；`knife`＝`008-audit-settings-pages`、`next_id` 10→12。角色與 GRANT 不入演進帳（八 kind 無權限面、schema 閘照相不及；權限面由 R11.9 之測承擔）。
4. **連動改對（承決＝spec FR-042）**：授權列 163→164、序號 164→165、受保護 25 不變、R_SUPER 按鈕碼 21→22、選單 77 按鈕清單；seed 錨定測、getUserInfo 三帳號按鈕集（Super 多 `audit:purge`；Admin／User 不變）、m0003 之 setval 期望與 schema 閘之序號合成期望值。
5. **BL-00148 離線對賬腿（承決＝⑫、spec FR-041；掛點與 DDL 處理＝工程）**：
   - 載體＝`tools/schema-gate.py` 新子命令 `offline`（零 docker、純讀檔）：①解析 `rust-api/migration/src/m000[3-9]*.rs` 之 `const <名>: &str = …;`（含 `concat!` 與檔內 `macro_rules!` 字面展開；展開器只認兩形、其餘形＝rc 2 指名）②逐語句分類：seed DML（`INSERT INTO`／`UPDATE`／`DELETE FROM` 於 seed 表）、序列（`setval`）、權限面 DDL（`CREATE ROLE`〔含 `DO $$` 包裝〕／`GRANT`／`REVOKE`／`DROP ROLE`）、其餘＝無法分類即紅 ③seed DML 與演進帳該刀登記逐筆對賬（表、pk、set／values 全欄）、與凍結 seed（`m0002_baseline_seeds.rs` 之 COPY 段）之前值對賬（UPDATE 之 WHERE 前值、DELETE 之全欄比對）④權限面 DDL 結構化列出（逐支語句數與受權物件集、不入演進帳；不對賬）——判準：權限面之真偽由 R11.9 之權限測承擔，離線腿只保證「語句類別可辨、seed 面與帳一致」。
   - 一正一反＋逐判準停用變異（RL-0080）：真 repo 綠；改壞 SQL 常數之值、少登一筆、改壞凍結 seed 前值、植一句未分類 DDL 各紅；逐判準停用（DML 對帳、前值對帳、分類器）各一支變異皆紅。
   - 掛點：pre-commit 新段（`rust-api` pin bump、`tools/schema-gate.py`、`docs/ops/reference-src/schema-evolution.json` 任一 staged 時跑 `schema-gate.py offline`；零 docker、秒級）＋`schema-gate.py test` 自測納入新案；需 docker 之 `check` 維持不進常跑鏈（工程判斷⑫）。接線字面入 `tools/docsync/tests/test_hook_wiring.py` 之機器守。
   - 時序：本腿於撰寫 m0004 之單元前落地，並先對 m0003 綠（BL-00148 觸發條件）。
6. **schema 閘（承決＝spec FR-040、ADR-00087）**：全新庫 m0001～m0004 重放後三閘綠；序號合成依 E-011 推進 `casbin_rule_id_seq` 期望；拆合成即 gate2 紅之變異照跑；schema-definition 不前進。
7. **Day-1 登記三步（承決＝spec FR-040）**：收刀前 RUNBOOK §10；第 3 步以 pristine 庫（一次性 postgres 容器）驗——角色為叢集層物件：pristine 容器內新建、不與 dev 叢集共享。

## R13 錯誤明細通道第三鍵與 msg 鍵（D7、ADR④；spec FR-004）

1. **新鍵（承決＝spec FR-004；鍵名＝rev5 名冊形）**：`biz.audit.invalidTable`（純 key）、`biz.audit.purgeBelowFloor`（攜 `{minDays}`）；`MSG_KEYS` 68→70、尾端追加；`msg_key::BIZ_AUDIT_INVALID_TABLE`／`BIZ_AUDIT_PURGE_BELOW_FLOOR`；`AppError` 變體數維持 11、13 碼矩陣不變。
2. **明細型（工程）**：`PurgeBelowFloorDetail { min_days: i64 }`（`#[serde(rename_all = "camelCase")]`、欄位不掛 serde 屬性）＋單一組裝件 `purge_below_floor_err()`（生產區 `BizData` 構造點恰一）。
3. **msg-key-gate 擴（工程；RL-0080 判讀）**：`BIZ_DATA_KEYS` 增第三鍵→型名；`DETAIL_HOME`（單檔）改逐鍵之家之對映（`handler/user.rs` 兩鍵、`handler/audit.rs` 一鍵）；不改任何模組層 `RE_*` 常數。判讀：名冊與家之擴列屬判準之資料面、非新增判準；但佔位符對賬多一條讀檔途徑＝射程宣稱逐途徑配變異（新家之明細型欄改名即紅、明細型移出其家即紅），並重跑與新途徑共用輸出面之既有對賬案（RL-0080「每增判準即重跑」之保守讀法）。正則未動＝FR-062 之 regex-mutants 前置不觸發（若實作期需改 `RE_*`，該單元先跑 `python3 tools/regex-mutants.py run`）。
4. **閘面連動（工程）**：pre-commit submodule-sync 段之 rust 側閘面增 `rust-api/server/src/handler/audit.rs`（明細型之家）；`tools/docsync/tests/test_hook_wiring.py` 之閘面對賬同批。
5. **前端轉譯（工程；須 Amendment）**：`translateBackendMsg` 既有圈界塊內增第三分支（`msg === 'biz.audit.purgeBelowFloor' && typeof fields.minDays === 'number'`）；`fields` 之型聯集增 `Api.Audit.PurgeBelowFloorDetail`；不增圈界塊、無修改型行。
6. **釐清款（承決＝D7）**：ADR-00076 決定 2 列與 ADR-00090 決定 1 之「時鐘回撥時上限 I——照提示秒數重試必過」——牆鐘回撥使「距上次設密之經過秒數」可為負，提示之秒數為上界而非必過之保證；ADR④ 以新字面續行 ADR-00076、並對 ADR-00090 決定 1 立釐清款（射程釐清不 supersede；前例 ADR-00090 決定 5）。

## R14 觀測層（B5、重錨；spec FR-043、FR-044）

1. **重錨（承決＝spec FR-043）**：③d 之 expr 已合 as-built 欄形（target `audit.access_log`＋`fields_degraded="access_log_write"`）＝註解改現況、規則體不動；⑤⑤b／⑥⑥b 之「無事件源」現況註改有源現況；④ audit-capacity 之「rev6 尚無該 handler」改述（稽核頁清理＋reaper 排程清理即處置路）。
2. **新告警兩條（承決＝主線工程判斷、clarify 步定案；名＝工程）**：
   - `obs017-policy-reconcile-orphans`：`max(reaper_orphan_policies{reaper_job="policy-reconcile"}) > 0`；
   - `obs017-policy-reconcile-heartbeat-timeout`：`time() - reaper_last_success_timestamp{mode="execute", reaper_job="policy-reconcile"} > 172800`；
   兩條沿⑤／⑥之 datasource、labels、noDataState 形；172800 納入三檔互錨註（compose 兩檔＋rules.yml）。前綴取 `obs017`（reaper 排程作業族；⑥⑥b 同族）。
3. **儀表板（承決＝B5、spec FR-044）**：`rust-api.json` 刪面板 10、11（兩支 HLL）與 14（設定讀取頻次）、面板 13（軟區命中）移至原 10 之版位並擴寬（重排；無空洞）；`reaper.json` 四面板與 `master-overview.json` 面板 5 之描述改 rev6 as-built（三 job、grouping key、心跳形）；`audit-log.json` 面板 3 與變數 `trace_id` 之描述改「rev6 稽核列此欄恆空」。可選起 obs／metrics profile 活體驗證。
4. **compose（承決＝spec FR-038）**：兩檔之「rev6 無 reaper bin／role、起了也跑不動」句改 as-built；dev loop 加 `cargo run --bin reaper -- --job policy-reconcile --execute`（`;` 分隔）；互錨註補 policy-reconcile。

## R15 前端：系統設定頁（§III.2 (ix)；spec FR-045～FR-050）

1. **形（承決＝spec FR-045；照 rev5）**：單檔 `base-web/src/views/manage/system-settings/index.vue`；四組依前綴歸組、組內固定鍵序（rev5 四常數照抄）、未列鍵排組尾保伺服器相對序、空組不渲染。
2. **控件與提交（承決＝spec FR-046）**：`settingType` 二值 enum→`NSwitch`、number→`NInputNumber`（`:min`／`:max` 取 `rangeMin`／`rangeMax`、`@blur`／Enter 提交、值未變不送、清空不送）、其他→唯讀；`declared = false`＝唯讀＋排組尾＋description；提交後成敗皆回讀全列。
3. **矛盾提示（承決＝D2、spec FR-047）**：三對嚴格不等式、computed 自兩現值導出、警示落該對所屬組卡片（`NAlert` warning）、三語文案寫後果；不阻存。
4. **政策快取清除（承決＝D3、spec FR-048）**：`pwd-policy.ts` 增 `clearPwdPolicyCache()`（模組層 `cachedPolicy` 置 null）；設定頁寫入政策七鍵任一成功後呼叫；檔頭「只增不清」「寫入者唯一」句與重設密碼浮層檔頭之快取句同批改述；RUNBOOK §11.3 改設定頁首選。
5. **譯文（承決＝spec FR-049）**：`page.manage.systemSettings` 節＝四組標題、16 鍵 label＋help、矛盾提示三則、成功提示；節流兩組 help 不承諾嚴格上限。
6. **授權面**：頁內零按鈕級 gating；非超管被授可見性＝進頁後讀取 `5003`（既有請求層提示）。

## R16 前端：稽核頁（§III.2 (x)；spec FR-051～FR-056）

1. **形（承決＝spec FR-051、FR-052；照 rev5）**：主頁＋四搜尋卡＋清理浮層＋時間區間 composable；四分頁欄集照 rev5（traceId 三分頁、region 存取／登入兩分頁、XFF 三分頁純文字插值＋ellipsis tooltip、會話事件無 XFF）；`scroll-x`＝各分頁欄寬總和（碼註列算式）。
2. **快照浮層（承決＝spec FR-053）**：`NModal`＋`<pre>` 文字插值 `JSON.stringify(…, null, 2)`；無快照提示。
3. **清理（承決＝spec FR-054、D6）**：清理鈕 `v-if="hasAuth('audit:purge')"`、每分頁一顆、單例浮層；浮層 `NInputNumber :min="30"`（碼註：UX 護欄、權威在後端 `PURGE_MIN_DAYS`）、每開重置 30、確認泡泡；成功提示帶 `deletedCount`、刷新該分頁。
4. **告示（承決＝spec FR-055、clarify Q2；文案＝R24 E1）**：存取分頁一句（只提 403）；登入嘗試分頁一句（節流短路遭拒不落表、不承諾上限）。
5. **自由文字欄**：一律 `{{ }}` 插值或 render 之文字節點；新目錄自動入 view-render-guard 腿①掃描；本頁不用共用表頭元件＝不入腿②錨表（rev5 形：一般 `NButton`）。

## R17 進場面與 fork-delta 範圍欄預估（spec FR-057～FR-059）

1. **路由產物（承決＝spec FR-057）**：兩頁 view 落地後以路由外掛重算四產物檔（route-artifact-gate 冪等）；route 鍵 `manage_system-settings`／`manage_audit`（seed 列 9／77 之 component 字面導出）。
2. **seed-view-gate（承決＝spec FR-058）**：`EXEMPT` 兩列各於交付該頁之單元摘除；`TestExemptInvariants`／`TestRunCheck` 改斷言空表；同檔現在式「恰兩列」字面改對、檔頭 rev5 原始版史述句不改。
3. **範圍欄預估（工程；收刀前 PATCH 實數化＝表外宣告 1 例外路徑）**：(ix)＝`{en-us,zh-cn}.ts` 各 2 塊（`route:`、`page:`）、`app.d.ts` 1 塊；(x)＝`{en-us,zh-cn}.ts` 各 2 塊、`app.d.ts` 1 塊；產物四檔授權沿 (i) 列；backend 子樹之 `biz.audit.*` 屬 I18N (ii) 既有塊內、`app.d.ts` backend 型節屬 I18N (iii) 既有塊內＝零增塊。I18N (i) 之 `request/index.ts` 範圍欄「2 處修改型＋2 塊新增型」不變（改動在既有塊內）。
4. **★軌道登記表補一列（R24 E2）**：`src/service/request/index.ts`｜`BASE-WEB-I18N-WIRING(i)`｜新增型（既有圈界塊內補分支、不增塊）｜第三攜參鍵具名插值｜12m 0／24m 3（2026-10-21 對 `8be6f9ba` 量）｜低。

## R18 測試基建與機器守（spec FR-068～FR-072）

1. **守衛（工程）**：`AccessLogRowsGuard`（R9.4）；`PurgeSelfAuditGuard`（以合成操作者 uid 圈自記列、水位形；排程清理案以 `created_by IS NULL AND real_ip = '0.0.0.0'::inet AND id > 水位` 圈列）；清理類真庫案之前置斷言（R8.7）；reaper 案以函式參數注入天數。`tests/common` 鏡像逐字對賬（既有慣例）。
2. **R4（承決＝spec Edge Cases）**：jobs profile 不於走查與真庫測試期間起；reaper 真庫案於容器測試內以函式呼叫跑、不起 jobs 容器。
3. **名冊閘**：`authz_entrypoint_lint` 新 handler 檔入判定面單一進入點與零 path-root entity 掃描；`entity_access_lint` 掃 `model/audit_query.rs`、`model/retention.rs`、`reaper.rs`；`wire_i64_guard_lint` 掃新 DTO 之 i64 欄（守衛序列化）。
4. **wire 裁判（承決＝spec FR-005）**：`Api.Audit` 受審型入 `tests/wire_schema.rs` 名冊、各配正向＋反例；`PurgeAuditTable` 枚舉集以後端白名單為真源；`SystemSetting` 擴三欄。
5. **contract（承決＝spec FR-069）**：五支 case＋覆蓋閘雙向＋case_key 綁定＋授權態矩陣（Super 通、Admin／User `5003`、未帶權杖 `8888`、動詞不符 `4040`）；兩新鍵各至少一案實發；可授出集 30→35 釘值。
6. **島 J 不變式測（承決＝spec FR-068）**：J1 讀端零寫入（唯讀交易負向＋計數不變）、J2 未認證零列／fail-open／`5003` 照記、J3 清理唯一形＋原子自記（含排程）、J4 打碼單點、J5 所指島 E 兩點之既有測照舊。

## R19 Amendment 要點與 U0 待親決清單（ADR①；spec FR-060）

- **版本**：MINOR 1.8.1→1.9.0（§V.3「行為島隨刀進場」「軌道授權邊界擴展」）；獨立 commit；accepted 前 base-web 既有檔零 diff（新增檔不受此閘）。
- **條文面**：①§I.7 島 J（J1～J5；起草輸入＝brainstorm ㉓；J1 補回 rev4 島 J1 分句、J2 以 rev4 島 J2 字面為底、J3 含排程清理與自記列形、J4 打碼、J5 指島 E 末兩點）②§I.6 變體 B 括號句改 J3 交叉指針 ③§I.7 表尾句 J2 空缺位處置、MAJOR 射程九島→十島、承襲指針 J 列尾註 ④§III.2 `BASE-WEB-MANAGE-PAGE-WIRING` (ix)(x) 兩新列 ⑤★§III.2 `BASE-WEB-I18N-WIRING` (i) 紀律欄「錯誤明細轉譯只限兩鍵」→三鍵（新增清理下限天數、具名插值；R24 E2）⑥Amendment log 列、島 J 標頭與島末常數句（README 不設憲法版本鏡像＝ADR-00074）。
- **親決時點**：條文字面於 plan 期逐款一題一問（ADR-00089 決定 4／7；brainstorm D10 原寫 U0、user 2026-10-21 plan 第 4 題裁定改 plan 期；9 款皆照候選定稿）；主線自擬之銜接字面於 U0 以一份 diff 一次呈 user（ADR-00089 決定 7）。

## R20 ADR 配號與親決時點表

ADR 草稿於本 plan 落 feature branch（`proposed`；proposed 期 `supersedes` 恆空、accepted 同顆補；親決分類住各檔）。配號接續 `ADR-00098`：

| 號 | 主題（spec FR-061） | 續行／取代 | accepted 時點 |
|---|---|---|---|
| ADR-00099 | ① 島 J 入憲、§III.2 (ix)(x)、I18N (i) 三鍵（Amendment） | —— | U0 Amendment 顆（憲法同顆；條文字面已於 plan 期逐款親決） |
| ADR-00100 | ② 存取日誌寫入（解除 `rev5:R2-9`） | —— | U0 施工前提顆 |
| ADR-00101 | ③ reaper 三 job、最小權限 role、哨兵、對賬只報不刪、心跳與告警、HTTP 依賴 | —— | U0 施工前提顆（ureq 版本已於 plan 期親決） |
| ADR-00102 | ④ 錯誤明細通道三鍵＋「必過」釐清款 | supersede ADR-00076；釐清 ADR-00090 決定 1（不 supersede） | U0 施工前提顆 |
| ADR-00103 | ⑤ 角色與選單已知態 v4 | supersede ADR-00081 | CDP 對照單元後之治理顆（已知態須實測） |
| ADR-00104 | ⑥ IP 域已知態 v5（寫入者全集、九詞） | supersede ADR-00082 | U0 施工前提顆 |
| ADR-00105 | ⑦ 授權歸檔表永久保留（by-design） | —— | U0 施工前提顆 |
| ADR-00106 | ⑧ 設定頁進場複核 | —— | CDP 對照單元後之治理顆（刻意分岔實測後定稿） |
| ADR-00107 | ⑧′ 部分更新語意 v3（設定域同值照落稽核） | supersede ADR-00091 | U0 施工前提顆 |
| ADR-00108 | ⑨ m0004（role＋seed、演進帳、序號合成、Day-1） | —— | U0 施工前提顆 |

- ⑩ 刻意分岔登記：併入 spec 刻意分岔表、不另立（007 前例）。
- 收刀前 PATCH Amendment 一支：配號＝當下下一號、plan 期不起草（ADR-00089 決定 1）。
- 親決分類（RL-0086）：plan 期當場問之待決款與獨立核對結果，記各 ADR 親決紀錄；轉 accepted 前依 ADR-00089 決定 6 收尾。

## R21 as-built 改寫義務（RL-0011；spec FR-063～FR-065）

- **errata 種子**：spec FR-065 所列 26 詞，另加本 plan 新增 `ADR-00080`（設定域承載改指 ADR-00091 後之殘留）、`只限兩鍵`、`恰二鍵`、`射程恰兩鍵`、`找不到 404`。
- **碼註**：`model/audit.rs`（檔頭「沒有『自己填一個位址』的路」、「`rev5:008` 追加之 `purge` 不帶」）、四支稽核 facade 之「讀端與水平線清理屬後刀增量、不帶」「沒有 delete」、`handler/auth/logout.rs` 同類句、`handler/system_settings.rs`／`facade/system_settings.rs` 之「無 op-log」「rev5 後刀的同 txn op-log 不帶回」三行、`error.rs` 檔頭「攜明細之射程恰二鍵」、`envelope.rs` 之錯誤 data 例外句（若述「兩鍵」）、`router.rs` 之 Authed／Policy 成員句與層序 doc、`docker-compose{,.dev}.yml` 兩處現況句、`rules.yml` 五處現況註。
- **活書與 RUNBOOK**：spec FR-064 所列；RUNBOOK 孤兒授權處置節落 §8「reaper 操作」之下新子節（§8.1）；存取日誌狀態欄已知態落 RUNBOOK §11 新子節（§11.4 稽核容量與存取日誌）與活書 08。
- **ADR 現在式改指**：ADR-00076／ADR-00081／ADR-00082／ADR-00091 之現在式引用面於各續行 ADR accepted 後改指（機器枚舉、改完復掃）。

## R22 執行單元切分 U0～U19（派發真源＝tasks.md）

| 單元 | 內容 | 前置 |
|---|---|---|
| U0 | 前置體檢；Amendment 親決（ADR-00099＋憲法 1.9.0）；施工前提 ADR accepted（ADR-00100／00101／00102／00104／00105／00107／00108） | — |
| U1 | 工具前置：BL-00148 離線對賬腿（對 m0003 先綠）＋pre-commit 段；runtime-append 兩工具擴 `sys_access_log`＋還原集 | U0 |
| U2 | 測試基建：`AccessLogRowsGuard`、`PurgeSelfAuditGuard`、在途計數 drain、app 建構 helper 帶守衛（兩層）、清理類前置斷言件 | U0 |
| U3 | 骨架：ROUTES 61→66＋handler 空殼五支（形依 007 刀 U3 前例）＋contract 登記＋授權態矩陣＋可授出集 35＋docsync 釘值 | U2 |
| U4 | m0004＋演進帳 E-010／E-011＋序號合成＋seed 錨定測改對＋reaper 權限測（`SET LOCAL ROLE`） | U1、U3 |
| U5 | 四源讀端 facade（`list`）＋`model/audit_query.rs`（時間、人員、打碼）＋`sys_user` 名對應件 | U3 |
| U6 | 讀端 handler 四支＋DTO＋`Api.Audit` 讀型（`rev6-audit.d.ts` 新檔）＋wire 裁判 | U5 |
| U7 | retention 共用核＋四源 `purge_before`／`count_before`＋purge handler＋兩新鍵＋第三攜參鍵＋msg-key-gate／submodule-sync 閘面＋三語 backend 子樹＋`translateBackendMsg` 第三分支 | U6 |
| U8 | 存取日誌中介層＋`sys_access_log::insert`＋號誌與在途計數＋降級計數＋層序釘 | U2、U3 |
| U9 | 設定寫端稽核＋讀 wire 擴三欄＋`rev6-settings.d.ts`＋wire 快照＋碼註順改 | U3 |
| U10 | reaper 骨架＋token-reap＋心跳（ureq）＋`sys_token` 兩件 | U4 |
| U11 | audit-retention（`SystemJob`、`write_system_in_txn`、環境變數三分語意） | U7、U10 |
| U12 | policy-reconcile（三維計數件、gauge） | U4、U10 |
| U13 | 觀測層（rules.yml 重錨＋對賬兩告警、儀表板 B5、compose 現況與 dev loop） | U8、U11、U12 |
| U14 | 系統設定頁（view＋route／page 譯文＋`app.d.ts`＋hook 清除函式＋seed-view-gate 摘列 9＋路由產物） | U0、U9 |
| U15 | 稽核頁（view＋五模組＋`rev6-audit.ts`＋譯文＋seed-view-gate 摘列 77＋路由產物） | U0、U6、U7 |
| U16 | 走查還原工具與測試守衛之 reaper／存取日誌影響評估收尾 | U8、U11 |
| U17 | 文件：活書、C4、RUNBOOK、ADR 現在式改指、假述掃除 | U13～U16 |
| U18 | CDP 三方對照（兩頁、側欄、浮層）＋繁中全頁審讀＋jobs profile 活體一輪；ADR-00103／ADR-00106 實測後定稿 | U14、U15 |
| U19 | 收刀前承載體檢＋Day-1 三步＋PATCH Amendment 實數化＋子句表逐列核 | U17、U18 |

高風險共享檔序列鏈（同檔單元不並發）：`router.rs`／`tests/contract.rs`（U3、U8）；`error.rs`＋三檔 locale＋`app.d.ts`（U7、U14、U15）；`model/facade/test_kit.rs`／`tests/common/mod.rs`（U2 起）；`tools/schema-gate.py`（U1、U4）；`model/facade/sys_operation_log.rs`（U5、U7、U11）。

## R23 RL-0013 棄案反例回跑

1. **存取日誌掛在授權判定之後（棄）**——反例「被拒之請求無列」對所選形（包住授權判定）：不成立，`5003` 照記。所選形之反例「認證失敗也記」：不成立，enforce_mw 早退於記錄層之外。
2. **存取日誌每請求無上限 spawn（rev4 形，棄）**——反例「洪峰佔滿連線池」對所選形（號誌 2）：上界 2；反例「丟列」：不成立（等待許可）。
3. **reaper 鏡像常數（rev4 形，棄）**——反例「兩側漂移」對所選形（同 crate 直接引用）：結構上單一、不成立。
4. **哨兵用 `127.0.0.1`（棄）**——反例「與 dev 真請求同址、無從區分」對 `0.0.0.0`：真請求之真實來源不會是未指定位址、可區分。
5. **m0004 拆兩支（棄）**——反例「角色與 seed 半套用」對一支：單支整體成敗、不成立；代價＝down 較長。
6. **甲案推送（棄）**——見 R11.6。
7. **設定寫端無鎖讀（棄）**——反例「並行寫入使 before 快照錯版」對所選形（`FOR UPDATE`）：不成立。
8. **reaper 權限測以 reaper 憑證直連（棄）**——反例「server 容器持 reaper 憑證」對所選形（`SET LOCAL ROLE`）：不成立；所選形之反例「驗不到登入面」：成立，由設密腳本自驗與活體一輪承擔（R11.9）。

## R24 plan 期 spec 字面修補（E1～E8）

| # | 位置 | 修補 | 依據 |
|---|---|---|---|
| E1 | US2 第 3 條、Edge Cases「存取日誌」狀態欄條、FR-009、FR-055、US4 第 3 條、刻意分岔登記表「存取日誌分頁告示」列 | 存取日誌之狀態欄實際只見 200 與 403；未註冊路徑與動詞不符（`4040`）由路由最外層 fallback 處理、不經記錄層＝零列；告示改只提 403 | R9.6；緣起＝user 2026-10-21 轉來 side agent 提醒（與主線取證同結論）；user 2026-10-21 plan 期 AskUserQuestion 親決「只提 403（建議）」後套入 |
| E2 | FR-060（增⑤）、★軌道登記表（增一列）、FR-004 | Amendment 增 §III.2 I18N (i) 紀律欄兩鍵→三鍵；`src/service/request/index.ts` 入登記表 | R13.5、R17.4 |
| E3 | Edge Cases「系統設定」同值寫入與空字串兩條、FR-028、FR-061⑧、Assumptions clarify 段 | 設定域觸發器之現行承載改指 ADR-00091（續行 ADR-00080）；FR-061 增⑧′（續行 ADR-00091） | R10.5 |
| E4 | FR-042、US6 第 4 條 | reaper role 權限測改為「以 reaper 角色身分（交易內 SET LOCAL ROLE）之正負向測＋jobs profile 活體以 reaper 憑證實連一輪」 | R11.9 |
| E5 | FR-037 | 心跳 metric 名定案（`reaper_last_success_timestamp`、`reaper_deleted_total`、`reaper_orphan_policies`）；HTTP 實作＝乙（ureq）、版本＝3.4.2（user plan 期答覆） | R11.6～R11.7 |
| E6 | FR-061⑤、FR-064 | 活書 11 角色與選單已知態款數「十八→十六」改「十八→十七」（款 2、6 解除、另立款 22） | R20；ADR-00103 |
| E7 | FR-060 首句、Assumptions「Amendment 與 ADR 親決時點」、checklist Notes | Amendment 條文字面之親決時點由 U0 改 plan 期 | ADR-00089 決定 4／7；user 2026-10-21 plan 第 4 題 |
| E8 | FR-039 表（選單 77 按鈕清單列） | 按鈕說明字面定為「清理日誌」 | user 2026-10-21 plan 第 3 題 |

另於 `checklists/requirements.md` Notes 補一行 plan 期更正（ADR-00080→ADR-00091）；檢核項狀態不變。

## R25 交 tasks 與實作期定值之事項

- 清理浮層與搜尋卡之欄寬、`scroll-x` 實數（以欄寬總和現算、碼註列算式）。
- 三語文案逐字（msg-keys contract 定語意；zh-tw 用詞依臺灣用語表）。
- U3 骨架 handler 之空殼形（依 007 刀 U3 前例；不得回假資料）。
- `AccessLogRowsGuard` 之 drain 上界（預設 5 秒）與 app helper 包裝型名。
- reaper 結構化事件之訊息文字（欄名照 contracts reaper-cli）。
- 範圍欄實數（收刀前 PATCH）。
