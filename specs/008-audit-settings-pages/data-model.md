# Data Model — 008-audit-settings-pages（Phase 1）

> 欄形一律以 001 基線 entity 現讀（`rust-api/entity/src/*.rs`）；本刀零業務表 DDL，唯一 DDL＝m0004 之角色與權限面（§8）。名稱、常數與型之跨檔定名以 §12 為單一出處；設計理由住 research（R 號）。

## §1 既有資料表之消費面

### 1.1 `sys_operation_log`（變體 B、append-only；本刀擴寫入者三形、首個讀端與刪除者）

| 欄 | 型 | 本刀用法 |
|---|---|---|
| `id` | bigserial | 讀端排序決勝；守衛水位 |
| `created_at` | timestamptz NN default now() | 讀端排序、時間過濾、水平線謂詞 |
| `created_by` | bigint 可空 | 操作者過濾維；排程清理自記列＝NULL |
| `operation` | varchar(20) | 封閉九詞（§7）；過濾等值、大小寫敏感 |
| `entity_table` | varchar | 過濾等值；設定變更＝`system_settings`、清理自記＝目標表名 |
| `entity_id` | bigint 可空 | 設定變更、清理自記、解鎖＝NULL（讀端顯「-」） |
| `payload_before`／`payload_after` | jsonb 可空 | 讀端打碼後上 wire（§5） |
| `real_ip` | inet NN | 讀端去前綴上 wire；排程清理自記＝哨兵 `0.0.0.0` |
| `peer_ip`／`x_forwarded_for`／`ip_confidence` | 可空 | 原字面上 wire；排程清理自記＝NULL |
| `region`／`trace_id` | 可空 | 恆 NULL（無料源）；照欄上 wire |

### 1.2 `sys_access_log`（變體 B；本刀首個寫入者與讀端）

`id`、`created_at`、`created_by` bigint **NN**（＝`Identity.uid`；結構上只已認證請求落列）、`http_status` int4（HTTP 狀態碼；rev6 實際只見 200 與 403＝research R9.6）、`http_method` varchar、`http_path` varchar（`uri().path()`、不含 query）、`real_ip` inet NN、`peer_ip`／`x_forwarded_for`／`ip_confidence` 可空、`region`／`trace_id` 恆 NULL。

### 1.3 `sys_login_attempt`（變體 B；既有寫入者＝登入路徑；本刀首個讀端與刪除者）

`attempted_user_name`（部分字串過濾）、`success`（嚴格二值過濾）、`real_ip`（精確等值過濾）、`created_by` 恆 NULL（無操作者維）、來源四欄、`region`／`trace_id`。節流短路遭拒不落表（表語意）。

### 1.4 `session_event`（變體 B；表名無 `sys_` 前綴；本刀首個讀端與刪除者）

`user_id` NN（人員過濾之主體維）、`sid`、`event_type`（等值）、`reason`（等值、可空）、`source_ip` varchar(45) 可空（字串照回、無 XFF 欄）、`created_by` 可空（觸發操作者）。

### 1.5 `sys_token`（變體 C；本刀首個刪除者＝token-reap）

回收判準＝`expires_at < now() − G 天`（G＝`REAPER_GRACE_DAYS`、預設 7；不分 status）；單語句 DELETE；不落稽核。

### 1.6 `system_settings`（變體 A；PK＝`setting_key` 字串；本刀寫端改交易化並落稽核）

16 鍵（密碼策略 8、工作階段 2、IP 源登入 3、帳號登入 3）；界值單一權威＝`validation.rs` 之 REGISTRY（`range_of`）。寫端鎖讀＝`SELECT … FOR UPDATE`（`deleted_at IS NULL`）。

### 1.7 `casbin_rule`（變體 D；m0004 增列 165；policy-reconcile 唯讀）

本刀相關三維：選單維（`v2 = 'menu'`、`v1`＝路由名）、按鈕維（`v2 = 'button'`、`v1`＝按鈕碼）、端點維（`v2 ∈ {GET, POST, DELETE}`、`v1`＝路徑）；`v0`＝角色代碼。

### 1.8 `sys_menu`（變體 A；m0004 改列 77 之 `buttons`）

列 77（`manage_audit`）之 `buttons`：NULL → `[{"code":"audit:purge","desc":"清理日誌"}]`。治理域＝未軟刪（含停用）。

### 1.9 `sys_role`（變體 A；policy-reconcile 唯讀）

活性角色代碼集＝`deleted_at IS NULL` 之 `role_code`（停用不排除：停用≠撤銷）。

### 1.10 `seaql_migrations` 與演進帳

遷移帳增 `m0004_reaper_role_and_audit_purge`；演進帳 `docs/ops/reference-src/schema-evolution.json` 增 E-010／E-011（§8.2）。

## §2 狀態機（現態×事件→次態＋副作用）

### 2.1 稽核列生命週期（四源共同；島 J3）

| 現態 | 事件 | 次態 | 副作用 |
|---|---|---|---|
| （無） | 業務寫入成功（同交易稽核）／登入嘗試／會話事件／已認證請求完成 | 留存 | 一列 append；變體 B 不可竄改 |
| 留存（`created_at ≥ 水平線`） | 任何清理 | 留存 | 水平線謂詞不命中 |
| 留存（`created_at < 水平線`、非 `purge` 自記） | 手動清理或排程清理執行 | 已刪 | 同交易落一列清理自記（§7） |
| 清理自記列（`operation = 'purge'`） | 任何清理（含標的＝操作日誌） | 留存（永久） | 豁免臂不命中＝後設證據 |
| 任意 | 自記寫入失敗 | 原態 | 整筆回滾（零刪除、零自記） |

水平線＝交易時戳 `now() − before_days 天`；`before_days ≥ 30`（`PURGE_MIN_DAYS`）。

### 2.2 存取日誌寫入（島 J2）

| 條件 | 結果 |
|---|---|
| 公開子路由、兩道 fallback（`4040`） | 不經記錄層＝零列 |
| 認證失敗（`8888`／`3333`／`7777`） | enforce_mw 早退＝零列 |
| 認證通過、身分或上下文缺席 | 跳過寫入（debug 事件） |
| 認證通過、授權拒絕（`5003`） | 回應先回；非同步一列、`http_status = 403` |
| 認證通過、handler 完成（含業務拒因 `2222`、系統錯誤 `5000`） | 回應先回；非同步一列、`http_status = 200` |
| 寫入失敗 | warn 事件（`target = audit.access_log`、`degraded = access_log_write`）＋`access_log_write_failed_total` +1；回應不變 |

寫入併發上界＝號誌 2（等待許可、不丟列）；在途計數供測試 drain。

### 2.3 reaper job 執行流

| 序 | 步 | 失敗出口 |
|---|---|---|
| 1 | 解析參數（未知參數／`--job` 缺值／未知 job） | error 事件＋退出 1 |
| 2 | （audit-retention）四表保留天數一次全驗 | 違規聚合指名＋退出 1、不推心跳、未連線 |
| 3 | 解析連線字串（`APP_DATABASE_URL_FILE`→`APP_DATABASE_URL`；空值與 `CHANGE-ME` 拒） | error 事件＋退出 1 |
| 4 | 連線 | error 事件＋退出 1 |
| 5 | 執行 job（dry-run／execute；policy-reconcile 兩者同為唯讀） | error 事件（指名表或維）＋退出 1、不推心跳；已 commit 之表維持 |
| 6 | 完跑摘要事件 | —— |
| 7 | 推心跳（best-effort、全程 10 秒） | error 事件、退出碼仍 0 |

### 2.4 設定寫入（D1）

| 現態 | 事件 | 次態 | 副作用（同一交易） |
|---|---|---|---|
| 鍵存在、值 v | 合法新值 w（含 w = v） | 值 w | 審計欄成對重寫；稽核 `update` 一列（before＝v 之整列、after＝w 之整列） |
| 鍵存在 | 非法值 | 不變 | 零寫入、零稽核（`2222`） |
| 鍵不存在或已軟刪 | 任意 | 不變 | `2222 notFound` |
| 任意 | 請求上下文缺席 | 不變 | `5000`、先於一切 |

## §3 固定序與 outcome

### 3.1 purgeAuditLog

| 序 | 判定 | 違反 | DB |
|---|---|---|---|
| ① | `table ∈ {operationLog, accessLog, loginAttempt, sessionEvent}` | `2222 biz.audit.invalidTable` | 零 |
| ② | `beforeDays ≥ 30`（缺席或畸形＝0） | `2222 biz.audit.purgeBelowFloor`＋data `{minDays: 30}` | 零 |
| ③ | 操作者（上下文缺席或位址不可解析） | `5000` | 零 |
| ④ | 單交易：水平線刪除＋自記→commit | 任一步失敗＝回滾、`5000` | 全有或全無 |

成功＝`0000`＋`{deletedCount}`（0 亦成功、自記照落）。

### 3.2 updateSystemSetting

①上下文（`5000`）→②`settingKey`／`settingValue` 必填（缺席或 null＝`2222 invalidValue`）→③交易內鎖讀（查無或軟刪＝`2222 notFound`）→④型別一致性（`5000`）→⑤registry 驗值（`2222 invalidValue`）→⑥更新（`RETURNING`）→⑦同交易稽核→commit→`0000`＋`data:null`。

### 3.3 reaper 參數與環境

見 §2.3；保留天數判定表：

| 原值 | 判定 | 結果 |
|---|---|---|
| 缺席 | Absent | 90 |
| 無法解析為非負整數（含負數、非數字、空字串） | Malformed | warn（指名鍵與原值）＋90 |
| 解析成功且 < 30（含 0） | 違規 | 前置全拒 |
| 解析成功且 ≥ 30 | Adopt | 採該值 |

`REAPER_GRACE_DAYS`：缺席 7；畸形 warn＋7。`REAPER_INTERVAL_SECS`：只由 compose dev loop 消費（缺席 86400）。

## §4 讀端過濾語意（query 全取可缺字串；空字串與畸形＝未設、絕不 4xx）

| 源 | 過濾維（wire 鍵） | 比對 |
|---|---|---|
| 操作日誌 | `entityTable`、`operation` | 等值（大小寫敏感） |
| | `operatorId`／`operatorName` | id 優先；名→含已軟刪同名之 id 全集 `IN`；零命中＝空頁 |
| 存取日誌 | `httpMethod`、`httpStatus` | 等值（status 整數 trim-parse） |
| | `httpPath` | ILIKE 部分字串、`%`／`_`／`\` 字面化 |
| | `operatorId`／`operatorName` | 同上 |
| 登入嘗試 | `userName` | `attempted_user_name` ILIKE 部分字串（字面化） |
| | `success` | 嚴格 `true`／`false`（trim 後）；其餘＝未設 |
| | `realIp` | `IpAddr` 解析成功＝INET 精確等值（/32、/128）；否則未設 |
| 會話事件 | `userId`／`userName` | 主體維 `user_id`；名→全集 |
| | `eventType`、`reason` | 等值 |
| 四源共同 | `timeFrom`／`timeTo` | RFC3339 [起, 迄)；畸形＝該端未設；起 ≥ 迄＝空頁 |
| | `current`／`size` | `page_params`：current [1, 10^7]、size [1, 100]、預設 1／10 |

排序恆 `created_at DESC, id DESC`；不收排序參數。

## §5 打碼規則（讀端序列化單點；島 J4）

| 輸入（快照頂層） | 輸出 |
|---|---|
| `userPhone` 字串、字元數 > 5 | 前 3 字元＋`****`＋後 2 字元 |
| `userPhone` 字串、字元數 ≤ 5 | `****` |
| `userEmail` 字串、含 `@` | 首字元＋`***`＋`@`＋網域 |
| `userEmail` 字串、無 `@` | 首字元＋`***` |
| 兩鍵之非字串值、缺席、巢狀同名鍵、快照非物件 | 原樣 |

`payload_before` 與 `payload_after` 各一次；資料庫原值不動。

## §6 wire 映射（逐欄白名單構造；欄序＝wire 序；camelCase）

| 型（`Api.Audit.*`） | 欄（← 表欄） |
|---|---|
| `OperationLog` | `id`(i64 守衛)、`createTime`(← created_at RFC3339)、`operatorId`(可空 i64 守衛)、`operatorName`(批查、可空)、`operation`、`entityTable`、`entityId`(可空 i64 守衛)、`payloadBefore`／`payloadAfter`(打碼後、可空)、`realIp`(字串)、`peerIp`、`xForwardedFor`、`ipConfidence`、`region`、`traceId`（後五可空） |
| `AccessLog` | `id`、`createTime`、`operatorId`(i64 守衛、恆在)、`operatorName`、`httpMethod`、`httpPath`、`httpStatus`(i32)、`realIp`、`peerIp`、`xForwardedFor`、`ipConfidence`、`region`、`traceId` |
| `LoginAttempt` | `id`、`createTime`、`attemptedUserName`、`success`、`realIp`、`peerIp`、`xForwardedFor`、`ipConfidence`、`region`、`traceId` |
| `SessionEvent` | `id`、`createTime`、`userId`(i64 守衛)、`userName`、`sid`、`eventType`、`reason`、`operatorId`、`operatorName`、`sourceIp` |
| `PurgeAuditLogRes` | `deletedCount`(u64、不入 2^53 守衛面) |
| `PurgeBelowFloorDetail` | `minDays`(i64) |

`Api.SystemManage.SystemSetting` 擴三欄：`declared`(boolean、恆在)、`rangeMin`／`rangeMax`(number、只在宣告之 number 鍵在場)。分頁信封 `PageRes<T>` 不變。

## §7 操作稽核列（封閉九詞；本刀新增寫入形三種）

詞彙＝`add`、`update`、`delete`、`restore`、`unlock`、`kick`、`reset_password`、`change_password`、**`purge`**（尾端追加）。

| 寫入形 | operation | entity_table | entity_id | before | after | 操作者／來源 |
|---|---|---|---|---|---|---|
| 設定變更（updateSystemSetting） | `update` | `system_settings` | NULL | 整列快照 | 整列快照 | 請求上下文 |
| 手動清理（purgeAuditLog） | `purge` | 目標表名 | NULL | NULL | `{table, before_days, deleted_count}` | 請求上下文 |
| 排程清理（audit-retention） | `purge` | 目標表名 | NULL | NULL | `{table, before_days, deleted_count, job}` | `created_by` NULL、`real_ip` `0.0.0.0`、餘 NULL |

整列快照（設定）＝`{settingKey, settingValue, settingType, description, createdAt, createdBy, updatedAt, updatedBy, deletedAt, deletedBy}`。`table` 取 wire 值（`operationLog`…）；`job`＝`audit-retention`。

## §8 m0004 與演進帳

### 8.1 `m0004_reaper_role_and_audit_purge`（`rust-api/migration/src/`；`lib.rs` 遷移向量第四支）

| 對象 | up | 期望 | down |
|---|---|---|---|
| 角色 `reaper` | `CREATE ROLE reaper NOLOGIN`（`DO` 塊、`duplicate_object` 略過） | —— | 角色無依賴時刪除（REVOKE 之後；`DO` 塊捕 `dependent_objects_still_exist` 即略過；spec 三欄表 Rollback） |
| GRANT | schema `public` USAGE；`sys_token` SELECT,DELETE；四稽核表 SELECT,DELETE；`sys_operation_log` INSERT；`sys_operation_log_id_seq` USAGE；`casbin_rule`／`sys_menu`／`sys_role` SELECT | —— | 逐條 REVOKE |
| `sys_menu` 77 `buttons` | NULL→`[{"code":"audit:purge","desc":"清理日誌"}]` | 1 列 | 回 NULL（比對新值；1 列） |
| `casbin_rule` 165 | `(165,'p','R_SUPER','audit:purge','button','','','',FALSE,'2026-08-05T00:00:00+00:00',NULL)` | 1 列 | 全欄比對刪除（1 列） |
| `casbin_rule_id_seq` | `setval(GREATEST(165, last_value), true)` | —— | m0003 形回推 |

遷移後：授權列 164、序號 165、受保護 25、R_SUPER 按鈕碼 22、選單 78 列不變。

### 8.2 演進帳兩筆（`knife`＝`008-audit-settings-pages`；`next_id` 10→12）

| id | kind | table | detail |
|---|---|---|---|
| E-010 | `seed_update` | `sys_menu` | `{pk:{id:77}, set:{buttons:"[{\"code\": \"audit:purge\", \"desc\": \"清理日誌\"}]"}}` |
| E-011 | `seed_add` | `casbin_rule` | `{pk:["id"], values:{id:165, ptype:"p", v0:"R_SUPER", v1:"audit:purge", v2:"button", v3:"", v4:"", v5:"", protected:false, created_at:"2026-08-05 00:00:00+00", created_by:null}}` |

角色與 GRANT 不入演進帳（權限面；research R12.3）。

## §9 孤兒授權列（policy-reconcile；只讀只報）

定義（`ptype = 'p'` 之現役列；每列每維至多計一次）：

| 維 | 候選外 | 角色無主 |
|---|---|---|
| 選單（`v2='menu'`） | `v1 ∉` 治理域選單路由名 | `v0 ∉` 活性角色代碼 |
| 按鈕（`v2='button'`） | `v1 ∉` 治理域按鈕碼聯集 | 同上 |
| 端點（`v2 ∈ endpoint_methods()`） | `(v1, v2) ∉ policy_endpoints()` | 同上 |

全新 seed（m0001～m0004）＋ROUTES 66 下三維皆 0。與「撤銷殘留」（撤銷後判定面降級窗內仍放行）為兩件事。

## §10 測試資料與守衛

| 件 | 圈界 |
|---|---|
| `AccessLogRowsGuard` | `max(id)` 水位；Drop 先 drain 在途寫入（上界 5 秒）再刪 `id >` 水位 |
| `PurgeSelfAuditGuard` | HTTP 路：合成操作者 uid＋水位；系統路：`created_by IS NULL AND real_ip = '0.0.0.0'` ＋水位 |
| 清理類真庫案 | 水平線 3650 天、植列 4000 天前、執行前斷言水平線前恰本案所植 N 列（否則拒跑） |
| 操作者 | 合成 uid ≥ `SYNTHETIC_UID_FLOOR`（9_300_000_000）；號段依 `ID_RANGES` 增列 |
| reaper 權限 | 交易內 `SET LOCAL ROLE reaper`、語句後回滾 |

## §11 msg key 名冊（68→70）

| 鍵 | 碼 | 攜參 | 發出點 |
|---|---|---|---|
| `biz.audit.invalidTable` | 2222 | 無 | purge 固定序① |
| `biz.audit.purgeBelowFloor` | 2222 | `{minDays}` | purge 固定序②（唯一 `BizData` 構造點） |

攜參明細通道恰三鍵：`biz.user.passwordPolicy`、`biz.user.pwdSetTooFrequent`、`biz.audit.purgeBelowFloor`。

## §12 新建件名冊（跨檔定名之單一出處）

| 名 | 種類 | 住處 |
|---|---|---|
| `handler::audit::{get_operation_log, get_access_log, get_login_attempt, get_session_event, purge_audit_log}` | handler | `server/src/handler/audit.rs` |
| `OperationLogQuery`／`AccessLogQuery`／`LoginAttemptQuery`／`SessionEventQuery`／`PurgeAuditLogReq` | 請求型 | 同上 |
| `OperationLogDto`／`AccessLogDto`／`LoginAttemptDto`／`SessionEventDto`／`PurgeAuditLogRes`／`PurgeBelowFloorDetail`、`purge_below_floor_err` | 回應型與組裝件 | 同上 |
| `TimeRange`、`parse_time_range`、`PersonFilter`、`resolve_person_filter`、`mask_pii_payload` | 讀端件 | `server/src/model/audit_query.rs` |
| `PURGE_MIN_DAYS`（30）、`RetentionTable`（`ALL`、`wire`、`entity_table`、`env_key`）、`PurgeActor`、`purge_with_self_record`、`count_before` | retention 共用核 | `server/src/model/retention.rs` |
| `AuditOperation::Purge`、`SystemJob`（`AuditRetention`）、`SystemAuditEvent` | 稽核型 | `server/src/model/audit.rs` |
| `write_system_in_txn`、`list`、`purge_before`、`count_before` | facade | `facade/sys_operation_log.rs` |
| `sys_access_log::{insert, list, purge_before, count_before}`、`NewAccessLog` | facade | `facade/sys_access_log.rs`（新） |
| `sys_login_attempt::{list, purge_before, count_before}`、`session_event::{list, purge_before, count_before}` | facade | 既有檔 |
| `sys_token::{count_reap_candidates, reap_expired}` | facade | 既有檔 |
| `sys_user::find_ids_by_name_incl_deleted` | facade | 既有檔 |
| `sys_casbin_policy::orphan_counts` | facade | 既有檔 |
| `system_settings::{find_by_key_for_update, update_by_key_in_txn}` | facade | 既有檔 |
| `access_log_mw`、`AccessLogLayer`、`ACCESS_LOG_WRITE_CONCURRENCY`（2）、`access_log_pending` | 中介層 | `server/src/middleware/mod.rs` |
| `access_log_write_failed`／`access_log_write_failed_total` | 觀測 | `server/src/obs.rs` |
| `reaper::{Args, parse_args, Job, dispatch_job, classify_retention_days, resolve_retention_days, grace_days_from, resolve_database_url, run_token_reap, run_audit_retention, run_policy_reconcile, OrphanCounts}` | reaper 本體 | `server/src/reaper.rs` |
| `reaper` bin（`push_heartbeat`、`HEARTBEAT_TIMEOUT_SECS` 10、`PUSHGATEWAY_URL_BASE`） | bin | `server/src/bin/reaper.rs` |
| `msg_key::{BIZ_AUDIT_INVALID_TABLE, BIZ_AUDIT_PURGE_BELOW_FLOOR}` | 名冊 | `server/src/error.rs` |
| `SettingItem.{declared, range_min, range_max}` | wire 擴欄 | `handler/system_settings.rs` |
| `AccessLogRowsGuard`、`PurgeSelfAuditGuard` | 測試守衛 | `facade/test_kit.rs`＋`tests/common/mod.rs` |
| `rev6-audit.ts`（`fetchGetOperationLog`／`fetchGetAccessLog`／`fetchGetLoginAttempt`／`fetchGetSessionEvent`／`fetchPurgeAuditLog`） | wrapper | `base-web/src/service/api/` |
| `rev6-audit.d.ts`（`Api.Audit.*`） | typings | `base-web/src/typings/api/` |
| `clearPwdPolicyCache` | hook 出口 | `base-web/src/hooks/business/pwd-policy.ts` |
| `obs017-policy-reconcile-orphans`、`obs017-policy-reconcile-heartbeat-timeout` | 告警規則 | `deploy/grafana-provisioning/alerting/rules.yml` |
| `reaper_orphan_policies{dimension}` | 心跳 gauge | reaper 推送 |
