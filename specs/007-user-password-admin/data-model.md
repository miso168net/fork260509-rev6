# Data Model — 007-user-password-admin（Phase 1）

> ★本刀**零 DDL、恰一支 seed-only migration `m0003`**（spec FR-041）——本檔描述 001 刀基線既有結構之**消費形**、本刀首建之寫入面與不變式、狀態機、寫端固定序、包含規則三集合、合併鎖序、wire 映射規則、稽核與會話事件列形、m0003 逐列前後值與演進帳九筆、測試資料與守衛、msg 鍵與新建件名冊；不含任何 DDL。承 `rev5:007` data-model 形、依 rev6 拍板改寫（翻案不帶回項與差異點住本刀 research R5）。
> wire 逐欄定義與 DTO 型名住 `contracts/wire-user-admin.md`／`contracts/wire-user-center.md`；拒因鍵譯文與攜參兩鍵之前端消費住 `contracts/msg-keys.md`；機器守、測試基建與走查還原工具 v4 之施工全文住 `contracts/code-gates.md`（§5／§6）；ADR 親決時點住 research R21。本檔所引 ADR-00074～ADR-00087 為本刀 plan 期 draft（proposed）。
> 量測（2026-10-05、rust-api pin `6f74d20`）之量法＝python3 唯讀解析 `rust-api/migration/src/m0002_baseline_seeds.rs` 之 `SEED_*` 常數、`m0001_baseline_schema.rs` 之建表與索引段、凍結 `specs/001-schema-baseline/fixtures/seed.sql` 之 COPY 段與 setval 行、`rust-api/server/src/validation.rs` 之 `REGISTRY`；量測值只作背景與自證前提、不入任何判定（判定一律現讀資料庫）。
> 「新建」＝rev6 現無、本刀新立之件；新建件定名之單一出處＝§12（wire DTO 型名除外＝兩支 wire 契約之「共用型」節）。

## §1 既有資料表之消費面

### 1.1 `sys_user`（變體 A、17 欄；seed 3 列；本刀首個管理寫入者）

欄與可空性以 `m0001_baseline_schema.rs` 建表段與 `specs/001-schema-baseline/data-model.md` §2 為準：

| 欄 | 型／可空 | 本刀消費 |
|---|---|---|
| `id` | bigint NN 自增 PK（`sys_user_id_seq`） | 使用者鍵（wire number、2^53 守衛）；addUser 取 nextval；per-user advisory key＝裸 id |
| `created_at`／`created_by` | timestamptz NN default `now()`／bigint 可空 | addUser：前者由 DB default 補、後者＝操作者；wire 回填帳號名 |
| `updated_at`／`updated_by` | 可空／可空 | 實寫時成對寫（`now_ts()`＋操作者；自助改密＝本人）：updateUser（含僅改角色集）、重設、改密、會話政策；同值 no-op、軟刪、復原皆不動 |
| `deleted_at`／`deleted_by` | 可空／可空 | 軟刪成對寫、復原成對清；活性判準＝`deleted_at IS NULL`（不看狀態） |
| `status` | smallint 可空、零 CHECK | 寫端只寫 1／2（`common::wire_two_value_to_db`）；讀向 `Some(1)`→`'1'`、其餘→`'2'`（`common::db_status_to_wire`） |
| `user_gender` | smallint 可空 | 寫端只寫 1／2／NULL；讀向 `Some(v)`→十進位字串、NULL→`null` |
| `user_name` | varchar NN | 形制 `^[A-Za-z0-9_-]{1,64}$`（上界引 `throttle::LOGIN_USER_NAME_MAX`；零正規化）；建後不可變 |
| `password` | varchar NN | argon2id PHC（`Argon2::default()`＝m=19456,t=2,p=1、與 seed 同參數）；★不上 wire、不入稽核、不入日誌 |
| `nick_name`／`user_phone`／`user_email`／`user_memo` | varchar／varchar／varchar／text，皆可空 | 空字串＝NULL（新增與更新同形）；信箱另守簡式格式與現役唯一；手機不守格式與長度；記事純文字顯示 |
| `session_policy` | varchar(20) NN default `'inherit'` | 三值（`SessionPolicy::parse`、大小寫敏感、不 trim）；只由 updateUserSessionPolicy 寫 |
| `session_id` | varchar(36) 可空 | 本刀零寫（login 第⑨步既有）；★不上 wire、不入稽核 |

- 索引與約束：PK `sys_user_pkey (id)`；活性唯一 `sys_user_user_name_active_uniq ON sys_user (user_name) WHERE deleted_at IS NULL` 與 `sys_user_user_email_active_uniq ON sys_user (lower(user_email)) WHERE deleted_at IS NULL AND user_email IS NOT NULL`；NOT NULL 五條（`id`、`created_at`、`user_name`、`password`、`session_policy`）；被 `fk_sys_user_role_user` 指向。兩支活性唯一索引＝「addUser 豁免 advisory、同名並發由索引兜底」「復原衝突守門」「已刪列與現役同信箱並存」之顯式前提；23505 經 `facade::violated_constraint` 依索引名收斂（帳號名索引→`userNameExists`、信箱索引→`userEmailExists`），主鍵 23505 與其餘故障＝`5000`。
- seed：1 `Super`／2 `Admin`／3 `User`（暱稱 `Super`／`Admin`／`User01`）；`status` 皆 1、`session_policy` 皆 `inherit`、其餘可空欄皆 NULL、`created_at` 皆 `2026-08-05T00:00:00+00:00`；三列共用一枚 PHC、其明文 6 字元＜政策 seed 下限 8 ⇒「登入路徑不驗政策」為 seed 帳號可登入之前提；`sys_user_id_seq`＝(3, true)。
- 讀者：既有 `find_by_user_name`（登入、unlockLogin 帳號維；濾軟刪）、`find_by_id`（登入第⑤步、getUserInfo、換發活性重驗；不濾軟刪）、`find_names_by_ids`（清單審計欄回填；不濾軟刪）；新建 `find_active_by_id_for_update`／`find_deleted_by_id_for_update`、`list_active`／`list_deleted`、`active_name_taken`／`active_email_taken`。
- 寫者：既有 `write_session_id`（登入）；新建 `insert`、`update_fields`、`soft_delete`、`restore`、`set_password`、`set_session_policy`（皆只收 `&DatabaseTransaction`）。
- 不變式：①帳號名建後不可變、活性唯一 ②寫入之 `status` ∈ {1, 2}、`session_policy` ∈ 三值 ③軟刪者零指派、復原不回灌（§1.2）④密碼只存 PHC、明文與雜湊三重不洩 ⑤`session_id` 不出本表 ⑥軟刪保留 `status` ⑦seed 帳號 1／2／3 不可刪、1 恆禁停用與恆禁解除其 R_SUPER 指派（碼內常數 `SEED_USER_IDS`／`SUPER_USER_ID`、不設 DB 旗標）。

### 1.2 `sys_user_role`（變體 C join；seed 3 列；本刀首個寫入者）

- 欄：`user_id`、`role_id`（bigint NN）；PK `sys_user_role_pkey (user_id, role_id)`；FK `fk_sys_user_role_user`→`sys_user.id`、`fk_sys_user_role_role`→`sys_role.id`，皆 `ON DELETE RESTRICT`（全 schema 恰此兩條）；無序列、無審計欄。
- seed：(1,1)／(2,2)／(3,3) ⇒ 持 R_SUPER 者恰 Super；`casbin_rule` 之 `ptype='g'` 0 列 ⇒ 指派不在判定面（授權每請求 `roles_of_user` 現查）。
- 讀者：既有 `roles_of_user`（授權；濾角色軟刪與 `status≠1`）、`count_by_role`／`is_member`（角色寫端兩腿；plain 讀）；新建 `role_ids_all_of_user`（T：濾角色軟刪、不濾 `status`）、`role_ids_active_of_user`（A：濾軟刪與 `status≠1`、回 id 與代碼）、`roles_by_user_ids`（清單回填 {id, 代碼, 名稱}；濾軟刪、含停用、角色 id 升冪）。
- 寫者（新建、只收具型交易）：`replace_roles_of_user`（期望全集 N：差集 DELETE＋缺集 INSERT、回是否有變更）、`delete_all_of_user`（軟刪時硬刪全部、回列數）。
- FK 鎖語意：INSERT 指派對父列取 `FOR KEY SHARE`（與他交易之同列 `FOR UPDATE` 互斥）；DELETE 指派不鎖父列——故角色列鎖（§5）是讓指派寫入與解除都與 deleteRole 之 in-use 計數排成單列之唯一手段。
- 不變式：①軟刪使用者同交易硬刪其全部指派（島 I4）⇒ ADR-00044 翻案觸發器首款之答案：`count_by_role` 之保守口徑結構上等同現役口徑、不改 ②復原零回灌 ③寫入時 N 成員皆為鎖得之活性角色（停用可指派、已軟刪不可）④指派變更零判定面重載（`RELOAD_CALL_FILES` 零擴列、配反向確認測試）⑤停用角色之指派列不硬刪。

### 1.3 `sys_pwd_custody`（變體 C 極簡；seed 0 列；本刀首個寫入者）

- 欄：`user_id` bigint NN、`created_at` timestamptz NN default `now()`、`created_by` bigint NN；PK `(user_id, created_by)`；零 FK、無序列；不存密碼材料。
- 語意（限縮）：一列＝（標的 `user_id`, 操作者 `created_by`）對之上次設密時刻；只作設密冷卻料源（§2.3）、不做經手判定（首登強制改密＝BL-00140）。
- 寫者：新建 `touch(txn, user_id, operator_id)`＝upsert（衝突鍵＝PK、改寫 `created_at`）；時戳取應用層 `now_ts()`（與冷卻判定同一時鐘）；消費點三：addUser（新 id, 操作者）、重設（標的, 操作者）、改密（本人, 本人）。業務碼 MUST NOT 刪本表列（軟刪使用者不連刪）。讀者：新建 `last_set_at(conn, user_id, operator_id)`（無鎖讀；呼叫點皆在標的 advisory 內）。
- 不在 `tools/schema-gate.py` 之 `RUNTIME_APPEND_TABLES` ⇒ gate2 逐列比對、seed 0 列 ⇒ 殘列即紅；清理由測試守衛（§10）與走查還原工具（§1.10）承擔、不擴閘之收窄集。

### 1.4 `sys_token`（seed 0 列；擴撤票原語）

- 相關欄：`created_by` NN（票之擁有者）、`status`（`active`／`rotated`／`revoked`）、`rotation_chain`（＝sid）；索引 `idx_sys_token_user_active ON sys_token (created_by) WHERE status = 'active'`（撤票迴圈之料源索引）、`uq_sys_token_chain_active`。
- 新建迴圈底座 `revoke_sids_of_user(conn, uid, keep: Option<&str>)`（模組私有）：每輪 SELECT「`created_by = uid` ∧ `status = 'active'` ∧（keep 在場時 `rotation_chain ≠ keep`）」之 sid → 空即收工 → 以逐條相同之過濾 UPDATE 為 `revoked` → 次輪重取快照；跨輪去重、保首見序。`revoke_all_of_user(conn, uid)`＝keep `None`（新建）；既有 `revoke_others_of_user` 改為 keep `Some` 之包裝（行為零變化）。★禁單句 UPDATE（漏撤並發 rotate 之後繼列；§5.3）。
- 不變式：只轉 `active→revoked`；`rotated` 不動（重放走既有 reuse 偵測）；`created_by = uid` 為「只及本帳號」之唯一守；同鏈至多一列 active 保證收斂。

### 1.5 `session_event`（append-only；擴詞彙）

- 欄寬：`event_type` varchar(20)、`reason` varchar(64)、`source_ip` varchar(45)；索引 `idx_session_event_user_time`。
- `vocabulary!` 同批擴：`EVENT_TYPES_ALL` 4→5（`EVENT_REVOKED`＝`revoked`）；`REASONS_ALL` 2→7（`REASON_USER_DISABLED`＝`user_disabled`、`REASON_USER_DELETED`＝`user_deleted`、`REASON_PASSWORD_RESET`＝`password_reset`、`REASON_PASSWORD_CHANGED`＝`password_changed`、`REASON_ADMIN_KICK`＝`admin_kick`）；最長 16 字元。列形住 §8；經既有 `insert` 與撤票同交易落列。本表 reason 與 `cache` 之失效名單 reason 分屬兩命名空間（`admin_kick` 兩邊各宣告、互不 `use`）。

### 1.6 `sys_operation_log`（append-only；擴寫入者與詞彙）

- 新寫入者：使用者寫端八支＋changePassword（`entity_table`＝`sys_user`、交易內 `write_in_txn`）；unlockLogin 帳號維自裸連線 `write` 改為 `write_in_txn`（§3.11；列形不變）、來源維不變。`AuditOperation` 5→8（§7）。`real_ip` inet NOT NULL ⇒ 上下文缺席只能拒寫 `5000`（島 F 之 F3①）。

### 1.7 `casbin_rule`（seed 163 列；m0003 改動面、執行期使用者域零寫）

- 欄形同 006 刀 data-model §1.1。使用者域寫端零寫本表；執行期新讀者恰一＝選單刪碼守門（新建 `sys_casbin_policy::protected_button_codes`：`ptype='p' ∧ protected=TRUE ∧ v2='button' ∧ v1 ∈ 移除集`；§3.10）。
- 本刀管理面十支之 seed 政策列：1（R_SUPER）、2（R_ADMIN）＝getUserList；17～20＝addUser／updateUser／deleteUser／batchDeleteUser；151／152／154／155＝resetUserPassword／restoreUser／kickUser／getDeletedUsers；68＝updateUserSessionPolicy（`protected=TRUE`＝封死集、只可屬 R_SUPER）；148＝unlockLogin（既有）。個人中心兩支零政策列。使用者頁七碼按鈕列：R_SUPER 39／40／41／150／153／156／157；R_ADMIN 44（`user:edit`；m0003 刪）。
- m0003 前→後：按鈕維 R_SUPER 20→21、R_ADMIN 3→2、R_USER_COMMON 1（計 24 不變）；選單維 85、端點維 54 不變；總列數 163 不變；受保護 19→25、皆屬 R_SUPER＝端點維 15（32、33、52～57、64～68、70、71）＋選單維 4（10、11、69、72）＋按鈕維 0→6（58～63）；按鈕維列不入封死集（`v2` 白名單只取 HTTP 方法；ADR-00064 決定 1）；`casbin_rule_id_seq` (163, true)→全新庫 (164, true)。

### 1.8 `sys_menu`（seed 78 列；m0003 改一列、updateMenu 增一守門）

- 相關列：3 `manage_user`、4 `manage_role`、5 `manage_menu`、6 `manage_user-detail`（皆受保護）；16 `user-center`（非受保護、頂層、隱藏）；78 `manage_ip-rule`（非受保護；按鈕清單 4→5 碼）。
- `buttons` jsonb 可空：既有 `sys_menu::button_codes_of`（首見序去重；NULL 與 `null`＝空集；壞形＝`DbErr::Custom`→`5000`）為選單刪碼守門之唯一解析件。治理域按鈕碼聯集 20→21（增 `ipRule:unlock`）；列數 78、受保護 8 列皆不變。

### 1.9 `system_settings` 之密碼政策鍵（八鍵；本刀首個消費者）

PK＝`setting_key`、無序列；界值唯一權威＝`validation.rs` 之 `REGISTRY`（ADR-00054；crate 內經 `validation::range_of` 讀界）：

| 鍵 | 型 | seed | 界 | 消費 |
|---|---|---|---|---|
| `password_min_length` | number | `8` | [1, 128] | 字元數下界（chars 計） |
| `password_max_length` | number | `64` | [1, 256] | 字元數上界（chars 計） |
| `password_require_digit`／`_lowercase`／`_uppercase` | `enum:on,off` | `off` | —— | 需含 ASCII 數字／小寫／大寫 |
| `password_require_special` | `enum:on,off` | `off` | —— | 需含非 ASCII 英數之字元 |
| `password_forbid_username` | `enum:on,off` | `off` | —— | 開啟時與帳號名不分大小寫**相等**即違規（子串不算；seed 說明「禁止密碼與帳號相同」） |
| `password_change_min_interval` | number | `60` | [0, 86400] | 設密冷卻秒數（0＝停用）；★不入政策與投影 |

- 前七鍵＝`PasswordPolicy` 七欄；位元組上界為碼內常數 `MAX_BYTES`＝`throttle::LOGIN_PASSWORD_MAX_BYTES`（512）。只在消費當下讀現值：政策七鍵以 `system_settings::find_all` 一句讀齊（同一快照）；冷卻鍵於冷卻步 `find_by_key` 另讀。設定寫端（002 刀）照舊只守單鍵界、不加組合守門 ⇒ min＞max 為可達存態。載入語意住 §2.5。

### 1.10 `seaql_migrations` 與演進帳（走查還原工具 v4 之讀面）

- `seaql_migrations`（框架自建；`version` varchar PK、`applied_at` bigint）：本刀後恰三列 `m0001_baseline_schema`、`m0002_baseline_seeds`、`m0003_seed_button_governance`（版本名＝檔名主幹）；schema 閘恆排除本表；新消費者＝`tools/walkthrough-baseline.py` v4（唯讀、依 `version` 升冪）。repo 側清單＝`rust-api/migration/src/lib.rs` 遷移向量之模組名（形 `^m\d{4}_[a-z0-9_]+$`、依宣告序）。
- 演進帳 `docs/ops/reference-src/schema-evolution.json`：`next_id` 1→10、`entries` 0→9（§9.2）；形與啟動斷言＝`docs/ops/reference-src/schema-evolution-contract.md` §1／§2。
- 走查還原工具 v4 之資料面（`SCHEMA_VERSION` 3→4、v3 舊檔 rc 2 指名重拍；施工全文＝`contracts/code-gates.md` §6）：
  1. 遷移帳前置（FR-057 (a)）：基準檔新欄 `migrations`＝取樣時之有序版本清單；基準檔模式 restore 寫入前比對現庫、不等＝rc 2、零寫入、指名差集並指示重拍。
  2. 使用者域面：`sys_user` 入 `BOUNDED_TABLES`（序列 `sys_user_id_seq`）；新欄 `sys_user_rows`＝上界以內列之 id＋可變欄（`nick_name`、`user_gender`、`user_phone`、`user_email`、`status`、`session_policy`、`user_memo`、`password`、`updated_at`、`updated_by`、`deleted_at`、`deleted_by`），restore 寫回不等者（改回值≠改回痕；軟刪兩欄入面＝基準內帳號被軟刪即寫回未刪、指派隨回補）；指派對回補（目標有而現況無、`ON CONFLICT DO NOTHING`）排在鍵集差刪除與上界列刪除之後（FK：先刪新帳號之指派、再刪其列）。
  3. 清理面各表（本刀起含經手表）增 `sys_pwd_custody`（全表清空；無序列＝不入 setval 名冊；安全帶＝基準檔與凍結 seed 皆須零列）；redis 清理前綴增 `cpwd`。
  4. 合成（FR-057 (b)）：seed 模式之目標態（角色／選單域與使用者域面）**與兩模式之 `system_settings` 比對左源**＝凍結 COPY 段 ⊕ 演進帳 `seed_*` 合成（執行期以 importlib 載入 `tools/schema-gate.py` 之同一合成鏈：`seed_add` 增列並推進期望序號、`seed_update` 改欄、`seed_delete` 刪列）⇒ 日後 migration 增、改、刪設定鍵或上列各域 seed 列皆由合成承接、工具毋須再擴；合成所涉之表有登記而 repo 遷移清單≠現庫已套用清單＝rc 2、零寫入、指名未套用者；仍拒跑之演進形兩種＝清理面各表之 `seed_*` 登記（整表清空以 seed 恆零列為前提）＋合成面表之結構演進屬 schema 閘合成未內建之形（與 gate2 同停、同一擴充點補齊即兩者恢復）。m0003 不動 `system_settings` ⇒ 本刀其合成結果＝凍結原值（工具自測以增、改、刪各一之合成登記證兩模式）。
  5. m0003 後之 seed 模式目標（§9.2 九筆合成）：列 44 不在、列 164 在、列 58～63 受保護、`casbin_rule_id_seq`＝(164, true)、選單 78 五碼。

## §2 狀態機（「現態×事件→次態＋副作用」；副作用同一交易，「commit 後」另標）

### 2.1 帳號生命週期

態＝∅／**啟用**（現役、`status=1`）／**停用**（現役、`status≠1`）／**已刪**（`deleted_at` 非 NULL、`status` 保留）。守門拒腿（零變更、零稽核）住 §3。

| 現態 | 事件 | 次態 | 副作用 |
|---|---|---|---|
| ∅ | addUser（狀態缺席或 `'1'`／`'2'`） | 啟用／停用 | INSERT（PHC、`created_by`）＋指派 N＋經手表 touch＋稽核 `add` |
| 啟用／停用 | updateUser 有異值（狀態除外） | 同態 | 只寫異值欄＋`updated_*`；角色集差集硬刪＋新增；稽核 `update`；零撤票、零重載 |
| 啟用／停用 | updateUser 全缺席或全同值 | 同態 | 零寫入、零稽核、`updated_*` 不動 |
| 啟用 | updateUser 狀態→`'2'` | 停用 | 寫列＋全撤＋事件 `user_disabled`＋稽核 `update`；commit 後失效名單 `revoked` |
| 停用 | updateUser 狀態→`'1'` | 啟用 | 寫列＋稽核 `update`；零撤票 |
| 啟用／停用 | deleteUser／batchDeleteUser | 已刪 | 軟刪成對＋硬刪全部指派＋全撤＋事件 `user_deleted`＋稽核 `delete`（批刪逐人）；commit 後失效名單 `revoked` |
| 已刪 | restoreUser（無撞名、撞信箱） | 刪除前之態 | 成對清、零角色、`updated_*` 不動＋稽核 `restore`；零撤票 |
| 已刪 | restoreUser 以外之寫端 | 已刪 | `biz.user.notFound` |
| 啟用／停用 | kickUser | 同態 | 全撤（`rotated` 不動）＋事件 `admin_kick`＋稽核 `kick`；commit 後失效名單 `admin_kick`；回 `{revoked: n}` |
| 啟用／停用 | resetUserPassword | 同態 | 新 PHC＋`updated_*`＋touch（標的, 操作者）＋全撤＋事件 `password_reset`＋稽核 `reset_password`；commit 後 `revoked` |
| 啟用／停用 | updateUserSessionPolicy 異值 | 同態 | 寫 `session_policy`＋`updated_*`＋稽核 `update`；零撤票（`single` 下次登入生效） |
| 現役（本人） | changePassword | 同態 | 新 PHC＋`updated_*`＋touch（本人, 本人）＋撤他會話（保留當前 sid）＋事件 `password_changed`＋稽核 `change_password`；commit 後他 sid `revoked`、清節流桶 |
| 停用／已刪／∅ | 登入 | 不變 | `1000`（三態 collapse；第③步停用判定恰 `==2`、第⑤步鎖內活性恰 `==1`） |

- 已知態：停用者若因失效名單寫入失敗而仍持未到期之存取權杖，到期前仍可呼 Authed 端點（含 changePassword；其鎖讀只濾軟刪）；換發被鎖內重驗擋下（§2.2）＝兩層兜底之殘窗（島 I2：不加每請求活性判定）。DB 中非 1 之狀態值（含 NULL）讀向一律 `'2'`、登入第⑤步判不活。

### 2.2 會話撤銷三型（島 B／C 用語＝ADR-00074）

| 型 | 觸發 | 票列 | 事件（type／reason／created_by） | 失效名單 | enforce | 換發 `revoked` 腿 | 再登入 |
|---|---|---|---|---|---|---|---|
| 頂替（既有） | 登入第⑨步 single-session | 撤他鏈（保留新 sid） | `kicked`／`single_session`／本人 | `kicked` | `7777` `auth.session.kicked` | `7777` | 可 |
| 撤銷 | 停用／刪除／重設／自助改密 | 全撤（改密＝撤他） | `revoked`／四原因之一／操作者（改密＝本人） | `revoked` | `8888` `auth.session.reLogin` | `8888` | 停用、刪除＝`1000`；重設、改密＝新密碼 |
| 管理員踢除 | kickUser | 全撤 | `revoked`／`admin_kick`／操作者 | `admin_kick` | `7777` `auth.session.kickedByAdmin` | `7777` | 可 |

- **三向分派**（enforce_mw 失效名單命中腿與換發 `revoked` 腿同準；ADR-00074 島 C 改述）：`kicked`→`ModalLogout`；`admin_kick`→`ModalLogoutByAdmin`；其餘（`revoked`、未知字面、空字串）→`Logout`（保守側）。程式內原因值不改。
- **降級**（既有、不變）：enforce 之 redis 答不出＝退 PG `has_active_in_chain`、無 active＝`8888`（三型同落 `8888`＝降級同碼、非互換）；換發 `revoked` 腿讀名單 `Err`＝靜默 `8888`。
- **換發活性重驗**（FR-028）：active 腿於票列 `FOR UPDATE` 與 idle 判定之後、取角色與簽發之前，以 `sys_user::find_by_id`（plain、不 `FOR UPDATE`、不取 advisory）讀帳號；查無列、`status≠Some(1)` 或已軟刪＝rollback＋`8888`、零寫。`rotated` 腿之 grace 命中（30 秒窗）不重驗＝已知殘窗（其 refresh 半下次換發即 `8888`）。
- **兩層兜底**（FR-029）：①同交易撤票（權威＝`sys_token.status`）＋commit 後盡力寫名單 ②換發鎖內重驗；enforce_mw、getUserInfo 不判帳號狀態。

### 2.3 設密冷卻（經手表一對＝（標的, 操作者）；ADR-00078）

| 該對現態 | 事件 | 結果 |
|---|---|---|
| 任意 | 冷卻秒數 `I`＝0 | 停用、恆過；成功後 touch |
| 無列 | 設密 | 過；成功後 touch |
| 有列 `t0`、`Δ = now − t0 < I` | 設密 | `2222`＋`biz.user.pwdSetTooFrequent`＋`{"remainingSeconds": min(max(I − ⌊Δ⌋, 1), I)}`；零寫、不 touch |
| 有列 `t0`、`Δ ≥ I` | 設密 | 過；成功後 touch（`created_at`＝now） |

- `now` 與 `t0` 同一時鐘（`t0`＝`touch` 經 facade `now_ts()` 寫入；`now`＝`model/password.rs` 取 `Utc::now()`——`now_ts()` 為 facade 私有、本體即同一呼叫）；判定以 `Δ`＜`I` 比（不取整）；剩餘秒數＝`I − ⌊Δ⌋`、下限 1、上限 `I`（`Δ`＜0＝時鐘回撥、仍屬未滿）＝照提示秒數重試必過（`rev5` HEAD 形補上限；例：`I`＝60、`Δ`＝30.0→30、`Δ`＝29.4→31、`Δ`＝59.5→1）。不同操作者互不影響；一體適用、零豁免。
- 實判點：resetUserPassword（標的, 操作者）、changePassword（本人, 本人）；addUser 之格＝結構恆過（新 id 無經手列）、以寫經手表承載「初始密碼同計入」（同操作者其後於冷卻內重設該帳號＝拒）。
- 冷卻鍵缺列、軟刪、不可解析或越界＝退 seed 預設 60＋warn 一則（指名該鍵；不推計數族）；讀庫 `DbErr`＝`5000`。經手表只 upsert、不刪他列。

### 2.4 改密節流桶（redis `cpwd:{uid}`；ADR-00078）

| 現態 | 事件 | 結果 |
|---|---|---|
| 無鍵／計 n＜5 | 舊密比對失敗（已 rollback） | `INCR`＋`EXPIRE 900` 同一 MULTI（`cache::incr_with_window`）→ 計 n+1、窗刷滿 900 秒 |
| 計 ≥5 | 任何改密請求 | 舊密比對之前拒 `biz.user.changePasswordThrottled`（純 key）；不推進、零稽核 |
| 計 n | 最後一次失敗後滿 900 秒 | 鍵到期（窗自癒；無解鎖端點＝ADR-00069 款 5 不觸發） |
| 計 n | 改密成功且 commit 落定 | `DEL`（清在 commit 之後） |
| 任意 | 其他拒因 | 不推進 |
| 任意 | redis 讀寫失敗 | fail-open 放行：先落一則結構化 error（`step`、`error`）再經 `throttle::warn_degraded("redis_change_pwd")`＝`throttle_degraded_total{source="redis_change_pwd"}` +1＋warn |
| 任意 | 快取自始缺席（測試 seam） | 整層跳過、不計降級 |

- 門檻＝碼內常數 `CHANGE_PWD_MAX_FAILS`＝5、`CHANGE_PWD_WINDOW_SECS`＝900；前綴與登入節流 `throttle:` 分離；桶值不可解析＝視同 0。5 次失敗後第 6 次請求即拒。

### 2.5 政策載入與壞值（ADR-00079）

| 輸入態 | `load_password_policy` 結果 | 設密（三入口） | getPasswordPolicy | 觀測 |
|---|---|---|---|---|
| 七鍵在、可解析、在界、min≤max | 照值 | 照判 | 照值投影 | —— |
| 某鍵缺列、軟刪、不可解析或越界 | 該欄逐欄 fail-default 至 seed 值（8／64／五開關 off） | 照判 | 該欄＝預設 | warn 一則（指名該鍵；不推計數族） |
| min＞max（逐欄處理之後） | 照值（不修正、不整組退） | **一律拒**：任一密碼必違反 `minLength` 或 `maxLength`＝`biz.user.passwordPolicy`＋自然違規清單 | 照值投影（後端仍是唯一裁判） | 設密時 `password_policy_invalid_total` +1＋warn（含 min、max、不含密碼）；讀取不計 |
| `find_all` 讀庫失敗 | `5000` | `5000` | `5000` | 002 刀 facade 已落 log |

- 發射出口 `obs::password_policy_invalid()` 恰一處＝`validate_against_policy` 判得 min＞max 時（只有三設密入口經過；spec FR-034「設密被拒才告警」）；getPasswordPolicy 只經 `load_password_policy`、不驗、不計（讀端計數會使告警語意擴為「讀到矛盾政策」、warn 量隨開頁放大）。告警規則 `obs016-password-policy-invalid`（`sum(increase(password_policy_invalid_total[5m])) > 0`）；warn 之 target 與欄位住 research R11。不入 `throttle_degraded_total`；登入路徑零呼叫。
- 方向與島 E「整組退回預設」相反＝刻意（政策是安全下限、退預設即靜默降低要求）；入憲法跨島註（ADR-00074）。
- `validate_against_policy(pw, user_name, &policy)` 一次收集全部違規、依序 `minLength`→`maxLength`→`maxBytes`→`requireDigit`→`requireLowercase`→`requireUppercase`→`requireSpecial`→`forbidUsername`；長度以 chars 計、位元組以 `len()` 計（＞512）。

## §3 寫端固定序與 outcome（FR-010 表之展開；多重違規取先序腿、凍結入契約）

**共同前置**（管理面八支與 changePassword）：

1. 操作者上下文 `common::operator_from_context` 缺席（或 `real_ip` 不可解析）＝`5000`、error 一則（target＝`security.user`〔管理面八支〕／`security.user_center`〔changePassword〕、`refused = "request_context_absent"`）；先於一切守門、提前 no-op 與交易。
2. body 經 `common::json_or_default` 收斂成 `Default`（id 0、陣列空、字串空、可選欄缺席）；抽取器零拒絕、授權中介層不讀 body。
3. handler 外殼 `begin` → 內層 `<op>_in_txn`（首句 `advisory_lock_user(txn, 標的)`；addUser 不取）→ 拒腿與故障腿顯式 rollback → 成功腿稽核 → `finish_user_write`（commit → 逐 sid 盡力寫名單）。DB 故障＝`5000`；commit 失敗＝`5000`、不寫名單。
4. 承載密碼三支（addUser、resetUserPassword、changePassword）於 `begin` 之後、首個鎖之前 `NewPassword::prepare`（argon2 失敗＝`5000`）＝雜湊於交易內、不持任何鎖時算；鎖內只做驗證。
5. 位次 ①活性標的鎖讀 → ②seed 保護 → ③本人規則 → ④包含規則 → ⑤業務守門；任一拒＝整筆 rollback、零變更、零稽核、零名單。逐支空格以測試釘空格理由。

拒因除另註皆 `2222`＋純 key；`5003`＝`system.forbidden` 純 key。

### 3.1 addUser

`begin` → `prepare(password)` →（①無既有標的、不取 advisory；②③不適用）→ `roleIds` 非空時 N 去重升序逐一 `sys_role::find_active_by_id_for_update` 鎖讀（停用照鎖）→ **④** T＝∅、N＝去重 `roleIds`（成員皆鎖得活性列時；缺席＝∅；含不存在或已軟刪 id＝N＝T＝∅、`roleNotFound` 於 ⑤-d 原位發＝rev5 HEAD 形）〔`5003`〕→ **⑤-a** 帳號名形制〔`userNameInvalid`〕→ **⑤-b** 現役唯一〔`userNameExists`〕→ **⑤-c** 信箱空字串歸 NULL；非 NULL 者簡式格式（無空白與控制字元、恰一 `@`、兩側非空、≤254 chars、不 trim）〔`userEmailInvalid`〕→ 現役唯一（`lower`）〔`userEmailExists`〕→ **⑤-d** N 成員任一未鎖得活性列〔`roleNotFound`〕→ **⑤-e** `load_password_policy` → `validate_against_policy(明文, userName)`〔`passwordPolicy` BizData〕→ **⑤-f** 冷卻結構恆過 → **寫**：狀態收斂（缺席或值域外＝1）、性別收斂（值域外＝NULL）、空字串＝NULL → `insert`（23505 依索引名→`userNameExists`／`userEmailExists`）→ `replace_roles_of_user(新 id, N)` → `touch(新 id, 操作者)` → 稽核 `add` → commit。回 `0000`（`data` 形住 wire-user-admin §3）；零撤票。

### 3.2 updateUser

**①** `begin` → advisory(id) → 鎖現役列〔`notFound`；body 缺席之 id 0 亦於此〕→ `roleIds` 出現時：T＝`role_ids_all_of_user(id)`、T∪N 去重升序 `sys_role::find_active_by_id_for_update` 鎖讀（停用照鎖；結果供 ④ 構 N、⑤-d 判存在）→ **②** `id = SUPER_USER_ID` 時：狀態出現且為 2〔`superCannotDisable`〕；`roleIds` 出現且不含 R_SUPER 現役 id（`sys_role::active_ids_by_codes` 現讀、查無＝fail-closed）〔`seededProtected`〕→ **③** `id = 操作者` 且狀態或 `roleIds` 出現（值不比對）〔`cannotEditSelfRoleOrStatus`〕→ **④** T＝`role_ids_all_of_user(id)`、N＝`roleIds` 去重（成員皆鎖得活性列時；缺席或含不存在／已軟刪 id＝N＝T、`roleNotFound` 於 ⑤-d 原位發＝rev5 HEAD 形）〔`5003`〕→ **⑤-0** 除 `id` 外全欄經值域收斂後缺席（`userName` 出現〔含 null〕不屬缺席；`status` 值域外與 null＝缺席；`roleIds` null＝缺席）＝no-op（rollback、`0000`、零寫零稽核、`updated_*` 不動）→ **⑤-a** `userName` 出現〔`userNameImmutable`〕→ **⑤-b** 信箱出現且歸一後非 NULL：格式〔`userEmailInvalid`〕→ **⑤-c** 同上信箱 `lower` 異於現值：現役唯一（排除自身；未改信箱只可能撞自身）〔`userEmailExists`〕→ **⑤-d** `roleIds` 出現：N 成員任一未鎖得活性列〔`roleNotFound`〕→ **⑤-e** 值 diff（空字串＝NULL、狀態與性別收斂後逐欄比、角色集以集合比 N 對 T）全同＝no-op（rollback、`0000`、零寫零稽核、`updated_*` 不動）→ **寫**：`update_fields`（只異值欄＋`updated_*`；僅角色集異值亦 bump；23505→`userEmailExists`）→ 角色集異值時 `replace_roles_of_user` → 本請求寫入狀態且新值≠1 時 `revoke_sessions_in_txn`（全撤）＋事件 `user_disabled` → 稽核 `update` → commit → 名單 `revoked`。

### 3.3 deleteUser

**①** advisory(id) → 鎖現役列〔`notFound`；含 body 收斂之 id 0〕→ **②** `id ∈ SEED_USER_IDS`〔`seededProtected`〕→ **③** `id = 操作者`〔`cannotDeleteSelf`〕→ **④** T⊆A、N＝∅〔`5003`〕→ **⑤** 空格 → **寫**：T 升序鎖角色列（只為與 deleteRole 計數排成單列；查無＝略過）→ `soft_delete`（成對、保留 `status`）→ `delete_all_of_user` → `revoke_all_of_user` → 事件 `user_deleted` → 稽核 `delete` → commit → 名單 `revoked`。

### 3.4 batchDeleteUser

`ids` 去重後空＝`0000`、零 `begin`。**①** ids 升序**先取完全部** advisory → 再依序鎖全部現役列；任一查無〔`notFound`〕→ **②** 任一 seed id〔`seededProtected`〕→ **③** 操作者 ∈ ids〔`cannotDeleteSelf`〕→ **④** A 讀一次、ids 升序逐筆 Tᵢ⊆A〔`5003`〕→ **⑤** 空格 → **寫**：整批 ∪Tᵢ 升序**一次**鎖角色列 → ids 升序逐人執行 §3.3 寫序（逐人一列稽核）→ commit → 全部被撤 sid 寫名單。位次「逐步全批」：同一步全批判完才進下一步 ⇒ 拒因由步序決定、與 id 排列無關；整批拒、不指筆。

### 3.5 restoreUser

**①** advisory(id) → `find_deleted_by_id_for_update`（`deleted_at IS NOT NULL`）；查無或為現役列〔`notFound`〕→ **②③** 結構不可達 → **④** T＝全部指派（軟刪時已硬刪＝∅、恆過、仍掛）、N＝∅〔`5003`〕→ **⑤-a** 同帳號名有現役列〔`userNameExists`〕→ **⑤-b** 信箱非 NULL 且同信箱有現役列〔`userEmailExists`〕→ **寫**：`restore`（成對清、`status` 保留、`updated_*` 不動；23505→上兩鍵）→ 稽核 `restore` → commit。零回灌、零撤票。

### 3.6 kickUser

**①** 鎖現役列（停用照鎖）〔`notFound`〕→ **②** 空格（Super 可被踢、受包含規則約束）→ **③** `id = 操作者`〔`cannotKickSelf`〕→ **④** T⊆A、N＝T〔`5003`〕→ **⑤** 空格 → **寫**：`revoke_all_of_user` → 事件 `admin_kick` → 稽核 `kick` → commit → 名單 `admin_kick`。回 `0000`＋`{revoked: n}`（實撤 active 數、可為 0）。

### 3.7 resetUserPassword

`begin` → `prepare(password)` → **①** 鎖現役列〔`notFound`〕→ **②** 空格（seed 帳號可重設）→ **③** `id = 操作者`（導向個人中心）〔`cannotResetSelfPassword`〕→ **④** T⊆A、N＝T〔`5003`〕→ **⑤-a** 政策（帳號名＝鎖內列）〔`passwordPolicy` BizData〕→ **⑤-b** 冷卻（標的, 操作者）〔`pwdSetTooFrequent` BizData〕→ **寫**：`set_password`（PHC＋`updated_*`）→ `touch` → `revoke_all_of_user` → 事件 `password_reset` → 稽核 `reset_password` → commit → 名單 `revoked`。回 `0000`＋`data` null（永不回傳密碼）。

### 3.8 updateUserSessionPolicy

**①** `begin` → advisory(id) → 鎖現役列〔`notFound`；body 缺席之 id 0 亦於此〕→ **②③** 空格（本人可改）→ **④** T⊆A（端點屬封死集、生產恆過、仍掛）〔`5003`〕→ **⑤-a** `sessionPolicy`（`Option<String>` 承載；必填）：缺席、null、空字串或 `SessionPolicy::parse` 值域外（含大小寫變體、前後空白）〔`sessionPolicyInvalid`〕→ **⑤-b** 同現值＝no-op（值 diff；本端點無全缺席早退） → **寫**：`set_session_policy`（＋`updated_*`）→ 稽核 `update` → commit。零撤票（`single` 下次登入生效）。

### 3.9 changePassword（自助；不屬九消費點）

上下文（標的恆＝`identity.uid`、body 無 id）→ body 三欄缺席＝空字串 → `change_pwd::precheck(uid)`（純讀、結果暫持）→ `begin` → `prepare(newPassword)` → **C1** advisory(uid)＋鎖現役列〔`notFound`〕→ **C2** `newPassword ≠ confirmPassword`〔`passwordConfirmMismatch`〕→ **C3** precheck 已達門檻〔`changePasswordThrottled`〕→ **C4** `password::verify(oldPassword, 列.password)` 假（鎖內驗證）〔`oldPasswordMismatch`；rollback 後 `record_failure`〕→ **C5** `newPassword == oldPassword`（舊密已於 C4 驗真 ⇒ 明文相等即同密、零額外 argon2）〔`passwordSameAsOld`〕→ **C6** 政策〔`passwordPolicy`〕→ **C7** 冷卻（本人, 本人）〔`pwdSetTooFrequent`〕→ **寫**：`set_password`（`updated_by`＝本人）→ `touch(uid, uid)` → `handler::user::revoke_sessions_in_txn`（keep＝`identity.sid` → `sys_token::revoke_others_of_user`）＋事件 `password_changed` → 稽核 `change_password` → commit → 他 sid 名單 `revoked` → `change_pwd::clear(uid)`。只 C4 推進節流桶；C3 拒腿零 verify。`identity.sid`＝enforce_mw 自 `claims.sid` 注入。

### 3.10 updateMenu 之受保護按鈕碼移除守門（新增一步；ADR-00086）

既有內層序（入域 → 鎖列 → ④不可變欄 → ⑤受保護選單〔停用與改父〕→ ⑥父驗證與防環 → ⑦常量父鏈 → ⑧href → ⑨按鈕碼清單形制 → ⑩絕版碼移入歸檔 → ⑪UPDATE → 稽核）於 ⑨、⑩ 之間插 **⑨′**：按鈕碼欄出現時，移除集＝`sys_menu::removed_codes`（純函式；既有 `obsolete_codes` 改呼之）＝舊清單碼中不在新清單者（`button_codes_of`、首見序；含改碼；新清單 null 或 `[]`＝舊碼全移除）；非空則 `sys_casbin_policy::protected_button_codes(txn, &移除集)` 回非空＝`biz.menu.protectedButtonRemove`、rollback、零稽核、零歸檔、零同步。

- 置 ⑨ 之後：解析以清單形制合法為前提（壞形先得 `buttonsInvalid`、不演成 `5000`）；置 ⑩ 之前：被拒者零歸檔。與 ⑤ 並立＝兩道受保護守門各管一面（選單列本身／授權碼）。射程＝移除集（非絕版集）：碼仍被他選單持有亦拒（FR-043 字面）。
- 涵蓋性：受保護按鈕碼（m0003 後六碼）之 seed 持有選單＝受保護選單 4／5（不可刪）⇒ 刪他選單永不使之絕版；唯一絕版路＝自 4／5 清單移除＝⑨′ 擋下。

### 3.11 unlockLogin 帳號維（交易化＋包含規則；帳號維守門＝ADR-00068 款 9 部分解除〔ADR-00081〕；兩處 UI 解鎖入口＝ADR-00069 款 1 解除〔ADR-00082〕）

1 `resolve_unlock_target`〔`biz.throttle.invalidUnlockTarget`；畸形先於一切〕→ 2 操作者〔`5000`〕→ 帳號維：3 `begin` → 4 `find_by_user_name(txn, 原文)`：查無或已軟刪＝T＝∅ 恆過、不取 advisory（不以異碼洩漏帳號存在性）；命中＝`advisory_lock_user(uid)` → `guard_no_escalation(txn, 操作者, Some(uid), N＝T, "unlockLogin")`〔`5003`；零稽核、零標記〕→ 5 `write_in_txn`（`unlock`；列形不變）→ 6 commit → 7 快取在場 → `set_ex` 標記〔失敗＝`5000`、稽核已落、可重試〕→ `0000`。

- 來源維不變（004 刀形）：解析 → 操作者 → 裸連線 `sys_operation_log::write` → 寫標記、不套包含規則（plan 期主線定案；spec FR-040 端點本體不變）。對未鎖帳號照回成功並落稽核（GR3）。源碼次序釘改為兩維各一序：帳號維「解析 → 操作者 → begin → 帳號維判定 → 稽核 → commit → 寫標記」、來源維既有序不變。

### 3.12 outcome 總表（成功腿；拒腿一律零稽核、零寫入、零名單，故障腿 `5000`）

| 寫端 | 回應 | 稽核列 | 撤票與事件 | commit 後 |
|---|---|---|---|---|
| addUser | `0000` | 1 `add` | —— | —— |
| updateUser（異值／no-op） | `0000` | 1 `update`／0 | 轉停用時全撤＋`user_disabled` | 有撤時名單 `revoked` |
| deleteUser／batchDeleteUser | `0000` | 每人 1 `delete` | 全撤＋`user_deleted` | 名單 `revoked` |
| restoreUser | `0000` | 1 `restore` | —— | —— |
| kickUser | `0000`＋`{revoked}` | 1 `kick` | 全撤＋`admin_kick` | 名單 `admin_kick` |
| resetUserPassword | `0000` | 1 `reset_password` | 全撤＋`password_reset` | 名單 `revoked` |
| updateUserSessionPolicy（異值／no-op） | `0000` | 1 `update`／0 | —— | —— |
| changePassword | `0000` | 1 `change_password` | 撤他＋`password_changed` | 名單 `revoked`、清桶 |
| unlockLogin | `0000` | 1 `unlock` | —— | 寫標記 |

全部寫端零判定面同步（使用者域零 `reload_enforcer`）。

## §4 包含規則集合 A／T／N（島 I7；ADR-00075）

| 集合 | 定義 | 料源 | 濾 | 時點 |
|---|---|---|---|---|
| A | 操作者現役角色集 | `role_ids_active_of_user(txn, 操作者)`（id, 代碼） | 濾角色軟刪與 `status≠1`；含 `SUPER_ROLE_CODE` ⇒ `ActorScope::All` | 判定當下同交易現讀（不鎖操作者之角色列） |
| T | 標的全部指派之角色 id | `role_ids_all_of_user(txn, 標的)` | 濾角色軟刪、**不濾** `status` | 標的 advisory 內（指派寫端皆持同一把 ⇒ T 於交易內穩定） |
| N | 寫後標的角色 id 集 | 請求 `roleIds` 去重（成員皆於鎖讀中為活性角色時） | 缺席或含不存在／已軟刪 id＝T（`roleNotFound` 於 ⑤ 原位發；rev5 HEAD 形） | 角色列鎖讀之後（①後、②前） |

- 純函式 `assert_no_escalation(&ActorScope, &T, &N)`：`All` 恆過；`Roles(a)` 時 T⊆a ∧ N⊆a 才過、否則 `PermissionDenied`（`5003`、不洩差集）。`actor_scope_of(現役角色清單)` 只依代碼判全集。
- 包裝 `guard_no_escalation(txn, 操作者, 標的: Option<i64>, N: Option<&BTreeSet<i64>>, 端點標籤)`：取 A、T（`None`＝∅）、N（`None`＝T）→ 判 → 拒時 warn 一則（target `security.user`；欄＝操作者 id、標的 id、端點；不含差集）、不新增觀測序列。
- 位次＝第④、先於業務守門；N 含不存在或已軟刪 id 時 ④ 只判 T⊆A、⑤ 得 `roleNotFound`（rev5 HEAD 形：抽屜候選列全部活性角色＝無實質存在性 oracle、過期選取得準確拒因；research R5 #50）。與撤銷拒、封死拒（角色域端點）不互吞。
- 九消費點：addUser（T＝∅、N＝`roleIds`；非恆過）、updateUser（T、N＝`roleIds` 或 T）、deleteUser（T、N＝∅）、batchDeleteUser（逐筆 Tᵢ⊆A、A 讀一次＝包裝恰呼叫一次：單筆＝（標的、N＝∅），多筆＝（`None`、N＝∪Tᵢ）——T＝∅ 且 ∪Tᵢ⊆A ⇔ 逐筆 Tᵢ⊆A、判定等價；整批拒、不指筆，多筆拒時 warn 之標的欄為空）、restoreUser（T 生產恆 ∅、N＝∅；恆過仍掛）、kickUser／resetUserPassword（T、N＝T）、updateUserSessionPolicy（T、N＝T；封死集端點、生產恆過）、unlockLogin 帳號維（同名活性帳號之 T、查無＝∅；來源維不套）。生產呼叫點檔集＝`handler/throttle.rs`、`handler/user.rs`（`NO_ESCALATION_CALL_FILES`、路徑字典序；裸 token 三形兩向恰等）；enforce.rs 之 `no_escalation_check` 掛點續恆放行、簽章不動。
- 已知形：同級互管允許；前超管復原 T＝∅ ⇒ 任何被授復原者可復原、復原後零角色。

## §5 鎖序（FR-011、島 G 之 G5、ADR-00043 決定 8 重核；論證全文住 research R7）

### 5.1 全域合併鎖序

advisory（選單序列化域 `MENU_DOMAIN_LOCK_KEY` 或 per-user uid；同一交易二者擇一、永不兼取）→ 歸檔表列 → `sys_user` 列 → `sys_role` 列（id 升序）→ `sys_menu` 列 → `casbin_rule`／`sys_user_role` 寫入 → append 表（`session_event`、`sys_pwd_custody`、`sys_operation_log`）。`sys_token` 列不入此序：多列取得者（撤票、頂替）皆持該 uid advisory；換發與登出先鎖一列、其後不等寫端資源（research R7 第 1、4 款）。

- G5 末句「使用者角色指派寫端 MUST 同納本鎖序」自本刀轉非 vacuous：指派寫端於使用者列 `FOR UPDATE` 之後對 T∪N 去重升序以 `sys_role::find_active_by_id_for_update` 鎖讀並鎖內重驗未軟刪（偏離 `rev5:007` 之「角色列只讀不鎖」＝research R5 差異點）。
- 全部交易為 READ COMMITTED、零 `lock_timeout`：鎖內重判一律以取鎖後之新語句讀；`FOR UPDATE` 等鎖後 PG 以新版本重評 `deleted_at IS NULL`（已軟刪＝查無）。

### 5.2 逐寫端取鎖

| 寫端 | advisory | `sys_user` 列 | `sys_role` 列 | 其後 |
|---|---|---|---|---|
| addUser | 不取 | 無（INSERT；同名並發排隊於活性唯一索引） | N 升序 | 指派 INSERT（父列已持） |
| updateUser | uid | 現役列 | `roleIds` 出現時 T∪N 升序 | 指派差集、停用時 `sys_token` |
| deleteUser | uid | 現役列 | T 升序 | 指派 DELETE、`sys_token` |
| batchDeleteUser | 全部 uid 升序（先取完） | 全部升序 | 整批 ∪T 升序一次 | 逐人寫 |
| restoreUser | uid | 已刪列 | —— | —— |
| kickUser／resetUserPassword／changePassword | uid | 現役列 | ——（不改指派） | `sys_token` |
| updateUserSessionPolicy | uid | 現役列 | —— | —— |
| unlockLogin 帳號維 | 標的 uid（命中時） | —— | —— | —— |
| 登入（既有） | uid | plain 重驗；single 時 UPDATE `session_id` | —— | `sys_token` |
| 換發（既有＋重驗） | —— | plain 讀 | —— | 呈遞 `sys_token` 列 `FOR UPDATE` 為首動作 |
| 登出（既有） | —— | —— | —— | 呈遞 `sys_token` 列 |

- `advisory_lock_user` 簽章收窄為只收 `&DatabaseTransaction`（比照 `enter_menu_domain`；compile_fail doctest）：autocommit 連線＝即取即放、型別擋下。生產呼叫點檔集＝`handler/auth/login.rs`、`handler/user.rs`、`handler/user_center.rs`、`handler/throttle.rs`，與 `DOMAIN_WRITE_SIDE_FILES` 零交集（`tests/authz_entrypoint_lint.rs` 腿⑤後半維持綠）。
- 批次：先取完全部 advisory 守 `advisory_lock_user`「advisory 早於任何列鎖」字面；三類鎖各自單調、與單筆寫端共用同一偏序 ⇒ 不成環。★逐人各自升序鎖 Tᵢ（`rev5:007` 逐 id 交錯形）使角色列於整批內非單調、與單筆 updateUser 成 ABBA＝不帶回。

### 5.3 跨路徑無 ABBA

| 對手 | 論證 |
|---|---|
| 角色域寫端 | 不取 per-user advisory、不鎖 `sys_user`、不寫 `sys_user_role`（in-use、self-role 為 plain 讀）；唯一共用資源＝`sys_role` 列、雙方升序取得、其後各碰對方不持有之資源 |
| deleteRole 兩序 | ①deleteRole 先鎖 X：指派寫端等其 commit、重評見已軟刪＝`roleNotFound`（不再掛上已刪角色）②指派寫端先鎖 X：deleteRole 等其 commit、新語句計數見新指派＝`inUse`；解除指派亦先持 X 鎖＝不再保守誤拒 |
| 登入 | 首動作 advisory(uid) ⇒ 與同帳號寫端排成單列；第⑤步鎖內三前提因而與停用、刪除、重設序列化 |
| 換發 | 至多持一列 `sys_token` 鎖、其後只 plain 讀與 INSERT；寫端撤票可等該列、換發永不等寫端之資源。撤票迴圈三序不漏：換發先鎖→次輪新快照撈到後繼列；寫端先撤→換發見 `revoked`＝`8888`；換發先 commit→首輪即撈到 |
| 登出／unlockLogin | 前者只鎖呈遞票列；後者只取標的 advisory、不鎖列 |
| 判定面同步 | 只在 commit 後、收場 task 內；使用者域零重載 |

### 5.4 ADR-00043 決定 8 三失效條件（已核、未觸發）

①角色寫端連動撤會話——未觸發（角色寫端對 `sys_token` 零寫）②使用者域寫端進選單序列化域——未觸發（零 `enter_menu_domain`；以角色列鎖取代入域）③同 key 跨交易嵌套重入——未觸發（名單寫入在 commit 後、無交易；持 advisory 期間不另以 `state.db` 開交易取同 key）。uid key 與域鎖 key（`0x7265_7636_6D65_6E75`）不碰撞前提不變。

## §6 wire 映射規則（型名與逐欄形之家＝兩支 wire 契約之「共用型」節）

| 規則 | 內容 |
|---|---|
| 構造 | DTO 逐欄白名單構造、絕不序列化原始列（`sys_user` 帶 `password`、`session_id`）；欄名 camelCase |
| 使用者鍵 | 一律 `id`（number、`serialize_i64_number_guarded`）；changePassword 標的恆＝登入者 |
| 角色元素 | 清單列 `roles`＝`{id, roleCode, roleName}` 陣列（角色 id 升冪、含停用、不含已軟刪、回收桶列 `[]`）；元素 `id` 為具名欄並過守衛（免觸 `wire_i64_guard_lint` 巢狀泛型絆線） |
| 狀態／性別／政策 | `status`＝`'1'`／`'2'` 恆非 null（同 rev6 角色列）；`userGender`＝`'1'`／`'2'`／`null`；`sessionPolicy`＝存值原字面 |
| 可空欄 | NULL＝顯式 `null`、不省略欄 |
| 時間 | `createdAt`／`updatedAt`＝RFC3339、`+00:00`、原樣顯示（ADR-00061）；軟刪欄不上 wire |
| 操作者 | `createdBy`／`updatedBy`＝帳號名 \| null（頁內去重一次 `find_names_by_ids`、不濾軟刪） |
| 請求空字串 | 可空文字欄空字串＝NULL、新增與更新同形（ADR-00080）；`userName` 不歸一；值 diff 於歸一後比 |
| 請求三態 | updateUser 可空欄＝缺席不動／null 清空／值設值（`common::tristate`）；`userName` 只判出現；`status` 兩態；`roleIds` 缺席或 null＝不動、陣列＝期望全集、`[]`＝全撤；`sessionPolicy`（另一端點）必填——缺席、null、空字串、值域外＝`sessionPolicyInvalid` |
| 狀態類值域 | `status`／`userGender` 經 `wire_two_value_to_db`；值域外＝缺席（新增取預設、更新不動、清單不篩） |
| body 收斂 | 缺席或壞形＝`Default`：id 0→①`notFound`（含 updateUser、updateUserSessionPolicy）；批刪空＝`0000`（提前 no-op、零 begin） |
| 清單分頁 | `envelope::page_params`（預設第 1 頁 10 筆；`current` [1, 10^7]、`size` [1, 100]、顯式 0 取 1）；查詢串壞形＝整串預設；逾界空頁、`total` 照回；facade 收 1 起算頁碼 |
| 清單序 | getUserList `id ASC`；getDeletedUsers `deleted_at DESC, id DESC`；不收排序參數（ADR-00058） |
| 清單篩選 | getUserList 六欄：帳號名、暱稱、手機、信箱＝`facade::ilike_contains`（部分字串、不分大小寫、轉義 `%`／`_`／`\`、NULL 不命中）；性別、狀態＝等值；空字串＝不篩；getDeletedUsers 只收分頁 |
| 錯誤信封 | `data` 恆 null，唯二例外＝`biz.user.passwordPolicy`→`{"violations": ["minLength", "requireDigit"]}` 形（違規碼八枚、依 §2.5 判定序）與 `biz.user.pwdSetTooFrequent`→`{"remainingSeconds": 30}` 形（ADR-00076）；`5003` 恆純 key |
| 政策投影 | getPasswordPolicy＝七欄（兩長度 number、五開關 boolean）、不含冷卻與位元組上界 |
| 型別承載 | 前端 `Api.UserAdmin`（`rev6-user-admin.d.ts`）／`Api.UserCenter`（`rev6-user-center.d.ts`）；`tests/wire_schema.rs` 受審前綴擴兩命名空間；對 upstream `Api.SystemManage.User` 之偏離（欄名、可空性、角色欄形）機器導出、記偏離帳（ADR-00083） |
| 密碼 | 承載密碼之請求 DTO（addUser、resetUserPassword、changePassword；同刀含 `LoginReq`）與 `NewPassword` 手寫遮蔽 `Debug`；回應、稽核、日誌零明文與 PHC |

## §7 操作稽核列（同交易恰一列；詞彙 5→8）

`AuditOperation` 增 `Kick`（`kick`）、`ResetPassword`（`reset_password`）、`ChangePassword`（`change_password`）；`EXPECTED_LITERALS` 型長 5→8、尾端追加。

**整列快照形**（使用者域；camelCase；白名單逐欄手構）＝`id`、`userName`、`nickName`、`userGender`、`userPhone`、`userEmail`、`userMemo`、`status`、`sessionPolicy`、`createdAt`、`createdBy`、`updatedAt`、`updatedBy`、`deletedAt`、`deletedBy` 15 欄＋`roleIds`（該時點指派之角色 id、升冪）；★結構上不含 `password`、`session_id`（機器釘：正向逐鍵、負向兩鍵不存在、`$argon2` 字面不出現）；值形同 005 刀角色快照（`status` 原值、時間 RFC3339、操作者 uid 原值）。

| 寫端 | `operation` | `entity_table`／`entity_id` | `payload_before` | `payload_after` |
|---|---|---|---|---|
| addUser | `add` | `sys_user`／新 id | NULL | 整列快照（`roleIds`＝N） |
| updateUser | `update` | `sys_user`／標的 | 整列快照（T） | 整列快照（寫後） |
| deleteUser／batchDeleteUser（逐人） | `delete` | `sys_user`／標的 | 整列快照（T） | 整列快照（軟刪欄已寫、`roleIds`＝`[]`） |
| restoreUser | `restore` | `sys_user`／標的 | 整列快照 | 整列快照（軟刪欄已清） |
| updateUserSessionPolicy | `update` | `sys_user`／標的 | 整列快照 | 整列快照 |
| kickUser | `kick` | `sys_user`／標的 | NULL | `{id, userName}` |
| resetUserPassword | `reset_password` | `sys_user`／標的 | NULL | `{id, userName}` |
| changePassword | `change_password` | `sys_user`／本人 | NULL | `{id, userName}` |
| unlockLogin | `unlock` | `login_throttle`／NULL | NULL | `{dimension, userName, target}`（既有、不變） |

- 操作者與來源四欄轉錄請求上下文（`AuditOperator`）；changePassword 之 `created_by`＝本人。零列之態＝一切拒腿（含 `5003`、⑨′）、兩種 no-op、操作者缺席、一切未 commit 之故障。稽核斷言取水位窗、不寫絕對計數（FR-062）。`sys_operation_log` 與 `model/audit.rs` 模組 doc 之寫入者與詞彙列舉同批改（RL-0011）。

## §8 會話事件與失效名單

每個被撤 sid 一列、與撤票同交易；`source_ip`＝`AuditOperator::real_ip()` 字面（≤45 字元）；撤 0 張＝0 列事件（稽核照落）：

| 來源 | `user_id` | `event_type` | `reason` | `created_by` |
|---|---|---|---|---|
| 停用 | 標的 | `revoked` | `user_disabled` | 操作者 |
| 刪除／批刪 | 標的 | `revoked` | `user_deleted` | 操作者 |
| 重設 | 標的 | `revoked` | `password_reset` | 操作者 |
| 自助改密（他 sid） | 本人 | `revoked` | `password_changed` | 本人 |
| 踢除 | 標的 | `revoked` | `admin_kick` | 操作者 |
| 頂替（既有） | 本人 | `kicked` | `single_session` | 本人 |

- 失效名單 `session:denylist:{sid}`：reason 三值 `kicked`／`revoked`（既有）＋`admin_kick`（新建 `cache::REASON_ADMIN_KICK`）；TTL＝refresh 全壽命（`jwt::ttl_from_settings` 之 `refresh_secs`；島 C 對三 reason 一體適用）。
- 寫入時點＝commit 後、`finish_user_write` 逐 sid 盡力寫：TTL 讀取失敗或快取缺席＝整段跳過、寫入失敗＝warn（target `security.session`）；皆不改回應（資料庫為權威）。當前 sid 永不進名單。讀端分派住 §2.2。`finish_user_write` 消費點＝`handler/user.rs`、`handler/user_center.rs`（不立名冊閘；每支撤票端點以名單寫入測試承載＝SC-005）。
- 改密與踢除不新增存取軌跡寫入面（BL-00043 反向確認）。

## §9 m0003 列與演進帳九筆

### 9.1 `m0003_seed_button_governance`（`rust-api/migration/src/`；零 DDL；`lib.rs` 遷移向量第三支；ADR-00085）

seed 基線層（島 G 之 G2 末句）：直接改列、不走執行期撤銷歸檔與操作稽核、零同步（一次性 `migrate` 服務先於 rust-api 啟動＝開機即載新值；dev 庫手動遷移後須重啟 rust-api）。單一遷移交易五句；①～④逐句 `rows_affected` 恰等斷言，不符＝回 Err＝整支回滾、遷移帳不記、`migrate` 非零退出、rust-api 不啟動（fail-loud）；不採 `ON CONFLICT` 吞錯；成功只跑一次、失敗可安全重跑、前置不符即失敗。

| 句 | 改動 | WHERE（前置） | 列數 |
|---|---|---|---|
| ① | `casbin_rule` 58～63 `protected` FALSE→TRUE | `(id, v1)` 逐對＝(58,`role:add`)／(59,`role:edit`)／(60,`role:delete`)／(61,`menu:add`)／(62,`menu:edit`)／(63,`menu:delete`) ∧ `ptype='p'` ∧ `v0='R_SUPER'` ∧ `v2='button'` ∧ `protected=FALSE` | 6 |
| ② | 刪 `casbin_rule` 44 | `id=44` ∧ `ptype='p'` ∧ `v0='R_ADMIN'` ∧ `v1='user:edit'` ∧ `v2='button'` | 1 |
| ③ | 增 `casbin_rule` 164 `(164, 'p', 'R_SUPER', 'ipRule:unlock', 'button', '', '', '', FALSE, '2026-08-05T00:00:00+00:00', NULL)` | 顯式 id（撞 PK＝Err） | 1 |
| ④ | `sys_menu` 78 `buttons` 四碼→五碼 | `id=78` ∧ `buttons` 與舊串 jsonb 等值 | 1 |
| ⑤ | `setval('casbin_rule_id_seq', GREATEST(164, 現 last_value), true)` | —— | —— |

- 列 58～63、44、164 之其餘欄（`v3`～`v5` 空字串、`created_at` `2026-08-05T00:00:00+00:00`、`created_by` NULL）前後不變；列 164 治理欄照 seed 形（`protected` FALSE、固定時戳、`created_by` NULL）。
- ④ 舊串（凍結 seed 字面）`[{"code":"ipRule:add","desc":"新增IP規則"},{"code":"ipRule:edit","desc":"編輯IP規則"},{"code":"ipRule:delete","desc":"刪除IP規則"},{"code":"ipRule:restore","desc":"恢復IP規則"}]`；新串＝尾端增 `{"code":"ipRule:unlock","desc":"解鎖來源IP"}`；`sys_menu` 列之 `updated_*` 不動。
- ⑤：全新庫 last_value＝163 ⇒ (164, true)；dev 庫序列已因走查前進者維持其值（列 164 若已被他列佔＝③撞 PK＝整支回滾、依 spec 三欄表處置）。
- down（逐句反向、同形斷言）：④′ 回四碼（1）→ ③′ 刪 164（1）→ ②′ 原值回插 44（1）→ ①′ 六列回 FALSE（6）→ ⑤′ `setval('casbin_rule_id_seq', GREATEST(163, (SELECT COALESCE(max(id), 0) FROM casbin_rule)), true)`；只服務全新庫可逆驗證、列 164 已被移入歸檔等執行期態下斷言失敗＝fail-loud。
- 遷移後恆真（全新庫）：`casbin_rule` 163 列、受保護 25、新列 id 164、序列 (164, true)；選單 78 列、按鈕碼聯集 21；seed 帳號之帳號資訊按鈕集＝Super 21 碼、Admin `B_CODE2`＋`B_CODE3`、User `B_CODE3`；migration 目錄恰三支。

### 9.2 演進帳九筆（`knife`＝`007-user-password-admin`；`next_id` 1→10）

`seed_*` 之 `detail` 值 MUST 為 pg_dump COPY 文字形之來源值：`tools/schema-gate.py` 之 `copy_literal` 將 `true→t`、`false→f`、`null→\N`、數值→十進位，字串只做 COPY 跳脫（`\`、tab、換行、CR；本刀九筆字串皆無此類字元）後比 gate2 右源；九筆值 U4 以全新庫套 m0003 後之 pg_dump 實文核定。

| id | kind | table | detail |
|---|---|---|---|
| E-001～E-006 | `seed_update` | `casbin_rule` | `{"pk": {"id": N}, "set": {"protected": true}}`，N 依序＝58、59、60、61、62、63 |
| E-007 | `seed_delete` | `casbin_rule` | `{"pk": {"id": 44}}` |
| E-008 | `seed_add` | `casbin_rule` | `{"pk": ["id"], "values": {"id": 164, "ptype": "p", "v0": "R_SUPER", "v1": "ipRule:unlock", "v2": "button", "v3": "", "v4": "", "v5": "", "protected": false, "created_at": "2026-08-05 00:00:00+00", "created_by": null}}` |
| E-009 | `seed_update` | `sys_menu` | `{"pk": {"id": 78}, "set": {"buttons": "[{\"code\": \"ipRule:add\", \"desc\": \"新增IP規則\"}, {\"code\": \"ipRule:edit\", \"desc\": \"編輯IP規則\"}, {\"code\": \"ipRule:delete\", \"desc\": \"刪除IP規則\"}, {\"code\": \"ipRule:restore\", \"desc\": \"恢復IP規則\"}, {\"code\": \"ipRule:unlock\", \"desc\": \"解鎖來源IP\"}]"}}` |

- ★E-008 `created_at` 取 COPY 文字形 `2026-08-05 00:00:00+00`（DB 時區 UTC＝ADR-00059；與凍結 seed 之 casbin COPY 列同形）、不取遷移 SQL 之 ISO 字面；`values` 欄集恰等 COPY 欄集 11 欄（`apply_seed_entries` 合成期斷言；啟動斷言⑦只驗形）。
- ★E-009 `buttons` 取 jsonb 正規輸出文字（`": "`、`", "` 之空白形、鍵序 `code` 先於 `desc`；與凍結 seed 之選單 COPY 列同形）、不取遷移 SQL 之緊湊字面。
- 每筆六欄齊全（`id`、`knife`、`kind`、`table`、`detail`、`date`）；`date`＝登記落地當日（實作期定：Day-1 紀律＝同刀 migration 落地同日登記、日界口徑＝ADR-00062）。
- gate2 合成：E-001～E-007、E-009 由既有 `apply_seed_entries` 承接；E-008 另需本刀擴充之序號合成（令現期望 (v, c)、已發出最大值 m＝c ? v : v−1；新 id＞m 時期望改 (新 id, true)；序列辨識＝normalize 後文本之 `setval('public.<表>_<c>_seq', N, B)` 行）⇒ 期望 `casbin_rule_id_seq`＝(164, true)；自測正反＋變異（拆掉＝gate2 紅）。schema-definition 不前進（ADR-00087）；`accounts-snapshot` 投影對賬面（使用者、角色、綁定）不受影響。

## §10 測試資料與守衛

- **守衛表集**（皆 gate2 逐列比對）：`sys_user`、`sys_user_role`、`sys_pwd_custody`＋既有 `SessionRowsGuard`（票、事件、`session_id`）、`OpLogRowsGuard`（水位窗）、角色／選單域五支、`RedisKeysGuard`。★測試 MUST NOT 留下對 seed 列之變更；守衛 MUST 早於任一寫 seed 帳號或指派之寫端單元（FR-057）。
- **新建守衛**（src `model/facade/test_kit.rs`；`tests/common/mod.rs` 同語意鏡像、逐字對賬案釘同形）：
  - `UserRowsGuard`：arm＝帶界水位 `COALESCE(max(id) FILTER (WHERE id < SYNTHETIC_UID_FLOOR), 0)`＋`sys_user_id_seq` 之 `(last_value, is_called)` 現讀；Drop＝①刪 `id > 水位` 之列（含合成 uid 與 nextval 新列）②`setval` 回 arm 值；指派由 `UserRoleRowsGuard` 先清（宣告序：使用者列守衛先宣告、後 drop；反序＝Drop 撞 `fk_sys_user_role_user` fail-loud）。
  - `SeedUserRestoreGuard`：arm＝`SEED_USER_IDS` 三列之可寫欄與審計欄快照（`nick_name`、`user_gender`、`user_phone`、`user_email`、`user_memo`、`status`、`session_policy`、`password`、`updated_at`、`updated_by`、`deleted_at`、`deleted_by`）；Drop＝不等者逐列寫回（改回值≠改回痕；`session_id` 續歸 `SessionRowsGuard`）。既有 `UserStatusFixture`／`SessionPolicyFixture`（各三欄）簽章與消費點零改動、與本守衛疊用（RAII 反序 drop、終態恆為最外層快照；research R15 第 1 款）。
  - `PwdCustodyRowsGuard`：arm＝記 user_id 名冊（含 seed uid、含預期被拒者＝RL-0069）＋`sys_user` 帶界水位；Drop＝`DELETE FROM sys_pwd_custody WHERE user_id = ANY(名冊) OR user_id > 水位`；無快照、無 setval（seed 該表零列＝界下列皆殘列）。
  - 既有 `UserRoleRowsGuard` 增 user_id 帶界腿（刪 `user_id > 使用者水位`）＋界下指派回補腿（arm 快照兩欄皆在界下之對、Drop 於刪除步之後 `ON CONFLICT DO NOTHING` 回插＝救回被撤之 seed 指派）；src 側案以 `RedisKeysGuard::track(cache::change_pwd_key(uid))` 逐鍵登記（型不改）、tests 側以 `CacheKeysGuard`。
  - 同案並用時使用者列守衛先於指派守衛宣告（Rust 逆序 Drop ⇒ 指派先清）。
- **造列**：addUser 端點案走 nextval（`UserRowsGuard` 還原序列）；直植 `sys_user` 列取顯式大 id（≥ `SYNTHETIC_UID_FLOOR`、不觸序列）——不入 `ID_RANGES`（該表 doc 明載合成 uid 家族不在射程；同 doc「免造 `sys_user`」句 U2 改寫）、新顯式合成 uid 取既有 `9_300_000_` 家族未用值（`grep -rnoE "9_300_000_[0-9]{3}"` 現核）；直植列取 `uniq_prefix()` 衍生帳號名、seed PHC、`status` 1、`inherit`；測試密碼明文一律執行期組字（沿 `test_kit::seed_plain`、RL-0054）。
- **換發與登出 fixture**（FR-028）：refresh 10 案（rotate、grace、reuse、bad_redis、idle_fresh、idle_threshold〔2 uid〕、idle_bad_redis、behind_proxy、concurrent、grace_before_commit）＋logout 1 案之合成票主改植活性 `sys_user` 列（掛 `UserRowsGuard`）；活性重驗負向三案（停用、刪除、列不存在）。
- **本刀端點未註冊前提之改植**：updateUserSessionPolicy 入 ROUTES 後 seed 列 68 成為端點候選（封死集）、getUserList 入 ROUTES 後 seed 列 2 成為候選；四支以此為前提之既有測試（research R5 #46）改植合成探針列或依新路由現算改值（形沿 006 刀 data-model §11 之豁免探針）。
- **殘列不連坐**（FR-058）：寫入一律對自建帳號；具名排除兩形＝seed 帳號指派被改（BL-00136 形②）與 seed 帳號欄值被改；非改 seed 帳號不可之觀察限於觀察窗、全量測試前先還原；自建帳號與其指派殘列在場時全量測試 MUST 全綠。
- **契約面**：registry 61 案（與 ROUTES 雙向恰等）；兩支清單各補分頁五案（缺席、`current` 逾界、`size=0&current=0`、查詢串壞形、`size=1000`；`total` 與 id 序列以獨立 SQL 現算）；授權態矩陣對照 seed（含 m0003）；22 新鍵各至少一案於真 seed app 實發（§11）。
- **dev 庫寫入**（LL-00053）：U4 中段以 U1 v4 基準 restore＋套 m0003＋重拍走查基準、U22 走查前後 restore 與告警活體實測、殘列演練皆逐步取 user 放行；演練只經 API 對自建帳號產殘列、psql 只下 SELECT。

## §11 msg key 名冊（46→68）

構造點一律 `AppError::Biz(Cow::Borrowed(msg_key::NAME))`（攜參兩鍵＝`handler/user.rs` 之 `password_policy_err`／`pwd_set_too_frequent_err` 內 `AppError::BizData(Cow::Borrowed(msg_key::NAME), data)`、生產構造點恰此二）；`MSG_KEYS` 型長 46→68、只在尾端追加（單元間依下表落地序、單元內序實作期定）；每鍵隨首個實發它的單元落地＝名冊、三檔 locale `backend` 子樹、`app.d.ts` backend 型節同批（`tools/msg-key-gate.py` 雙向全等；`tests/contract.rs` 名冊每鍵 ≥1 真 seed app 發出點）。

| 鍵 | 常數 | 碼 | 發出點（§3 步） | 首發 |
|---|---|---|---|---|
| `biz.menu.protectedButtonRemove` | `BIZ_MENU_PROTECTED_BUTTON_REMOVE` | 2222 | updateMenu ⑨′ | U4 |
| `biz.user.notFound` | `BIZ_USER_NOT_FOUND` | 2222 | 管理面七支寫端①；changePassword C1 | U8 |
| `biz.user.superCannotDisable` | `BIZ_USER_SUPER_CANNOT_DISABLE` | 2222 | updateUser② | U8 |
| `biz.user.seededProtected` | `BIZ_USER_SEEDED_PROTECTED` | 2222 | updateUser②；deleteUser／batchDeleteUser② | U8 |
| `biz.user.cannotEditSelfRoleOrStatus` | `BIZ_USER_CANNOT_EDIT_SELF_ROLE_OR_STATUS` | 2222 | updateUser③ | U8 |
| `biz.user.userNameInvalid` | `BIZ_USER_USER_NAME_INVALID` | 2222 | addUser⑤-a | U8 |
| `biz.user.userNameExists` | `BIZ_USER_USER_NAME_EXISTS` | 2222 | addUser⑤-b；restoreUser⑤-a | U8 |
| `biz.user.userEmailInvalid` | `BIZ_USER_USER_EMAIL_INVALID` | 2222 | addUser⑤-c；updateUser⑤-b | U8 |
| `biz.user.userEmailExists` | `BIZ_USER_USER_EMAIL_EXISTS` | 2222 | addUser⑤-c；updateUser⑤-c；restoreUser⑤-b | U8 |
| `biz.user.roleNotFound` | `BIZ_USER_ROLE_NOT_FOUND` | 2222 | addUser⑤-d；updateUser⑤-d | U8 |
| `biz.user.userNameImmutable` | `BIZ_USER_USER_NAME_IMMUTABLE` | 2222 | updateUser⑤-a | U8 |
| `biz.user.passwordPolicy` | `BIZ_USER_PASSWORD_POLICY` | 2222 BizData | addUser⑤-e；resetUserPassword⑤-a；changePassword C6 | U8 |
| `biz.user.cannotDeleteSelf` | `BIZ_USER_CANNOT_DELETE_SELF` | 2222 | deleteUser／batchDeleteUser③ | U9 |
| `biz.user.cannotKickSelf` | `BIZ_USER_CANNOT_KICK_SELF` | 2222 | kickUser③ | U10 |
| `biz.user.cannotResetSelfPassword` | `BIZ_USER_CANNOT_RESET_SELF_PASSWORD` | 2222 | resetUserPassword③ | U10 |
| `biz.user.pwdSetTooFrequent` | `BIZ_USER_PWD_SET_TOO_FREQUENT` | 2222 BizData | resetUserPassword⑤-b；changePassword C7 | U10 |
| `biz.user.sessionPolicyInvalid` | `BIZ_USER_SESSION_POLICY_INVALID` | 2222 | updateUserSessionPolicy⑤-a | U10 |
| `auth.session.kickedByAdmin` | `AUTH_SESSION_KICKED_BY_ADMIN` | 7777 | enforce_mw 名單命中 `admin_kick`（`ModalLogoutByAdmin`）；換發 `revoked` 腿（U11） | U10 |
| `biz.user.passwordConfirmMismatch` | `BIZ_USER_PASSWORD_CONFIRM_MISMATCH` | 2222 | changePassword C2 | U12 |
| `biz.user.changePasswordThrottled` | `BIZ_USER_CHANGE_PASSWORD_THROTTLED` | 2222 | changePassword C3 | U12 |
| `biz.user.oldPasswordMismatch` | `BIZ_USER_OLD_PASSWORD_MISMATCH` | 2222 | changePassword C4 | U12 |
| `biz.user.passwordSameAsOld` | `BIZ_USER_PASSWORD_SAME_AS_OLD` | 2222 | changePassword C5 | U12 |

- 計 22＝`biz.user.*` 20＋`auth.session.kickedByAdmin`＋`biz.menu.protectedButtonRemove`；單元分布 U4 1、U8 11、U9 1、U10 5、U12 4。U6 落 `BizData` 變體、`data` 上 wire 之信封通道與 `msg-key-gate` 斷言 2 擴認三形（射程守分階段四句＝contracts/code-gates.md §2.3）；兩攜參鍵本身隨首個實發單元（U8／U10）落地（名冊雙向閘要求真發出點；addUser 冷卻格結構恆過＝不發 `pwdSetTooFrequent`）。
- 沿用既有：包含規則違反 `system.forbidden`（5003）、操作者缺席 `system.internal`（5000）、撤銷 `auth.session.reLogin`（8888）、頂替 `auth.session.kicked`（7777）；13 碼矩陣與可發碼集不變；`AppError` 變體 9→11。
- 違規碼八枚不是 msg 鍵：前端譯文住 page 樹 `page.passwordPolicy.violation.<code>`（三語；`contracts/msg-keys.md` §3），`backend` 子樹只放本名冊成員。

## §12 新建件名冊（跨檔定名之單一出處）

| 件 | 落點 | 型與可見性 | 職責／rev5 對應 |
|---|---|---|---|
| 管理面十支 handler：`get_user_list`、`get_deleted_users`、`add_user`、`update_user`、`delete_user`、`batch_delete_user`、`restore_user`、`kick_user`、`reset_user_password`、`update_user_session_policy` | `server/src/handler/user.rs`（新檔；`handler/mod.rs` 增宣告） | `pub async fn` | §3.1～§3.8；`rev5:` 同名 |
| `guard_no_escalation` | 同上 | `pub(super) async fn`（txn, 操作者 uid, 標的 `Option<i64>`, N `Option<&BTreeSet<i64>>`, `&'static str`）→ `Result<(), AppError>` | §4；`handler/throttle.rs` 共用；`rev5:` 同名 |
| `finish_user_write` | 同上 | `pub(super) async fn`（state, txn, sids, reason, 端點標籤） | commit→名單；無重載參數（`rev5:` 帶 reload 旗標＝不帶）；`handler/user_center.rs` 共用 |
| `revoke_sessions_in_txn` | 同上 | `pub(super) async fn`（txn, 標的 uid, keep_sid: `Option<&str>`, reason, 操作者）→ `Result<Vec<String>, AppError>` | 交易內撤票＋逐 sid 會話事件（keep 缺席＝`sys_token::revoke_all_of_user`、給定＝`revoke_others_of_user`）；`handler/user_center.rs` 共用 |
| `password_policy_err`、`pwd_set_too_frequent_err` | 同上 | `pub(super) fn`（`Vec<&'static str>`／`u64`）→ `AppError` | 生產 `BizData` 構造點恰此二；data＝具型 `PasswordPolicyDetail`／`PwdSetTooFrequentDetail` 之 `serde_json::to_value`；`handler/user_center.rs` 共用；`rev5:` 同名 |
| `Res::from_err_with_data` | `server/src/envelope.rs` | `pub(crate)`（`impl Res<serde_json::Value>`） | `BizData` 之 data 上 wire 唯一出口；`rev5:` 同名 |
| `SEED_USER_IDS: [i64; 3] = [1, 2, 3]`、`SUPER_USER_ID: i64 = 1` | 同上 | 模組私有 `const` | seed 保護；`rev5:` `USER_SEED_IDS`（住 facade） |
| `get_password_policy`、`change_password` | `server/src/handler/user_center.rs`（新檔；新域 target `security.user_center`） | `pub async fn` | §3.9、政策投影；`rev5:` 同名 |
| `ActorScope { All, Roles(BTreeSet<i64>) }`、`actor_scope_of`、`assert_no_escalation` | `server/src/auth/no_escalation.rs`（新檔；`auth/mod.rs` 增 `pub mod`） | `pub`、純函式 | §4；`rev5:` 同名（代碼集元素＝改 id 集） |
| `Identity.sid` | `server/src/auth/mod.rs` | `pub sid: String` | enforce_mw 自 `claims.sid` 注入 |
| `find_active_by_id_for_update`、`find_deleted_by_id_for_update` | `model/facade/sys_user.rs` | `pub async fn (&DatabaseTransaction, i64) -> Result<Option<Model>, DbErr>` | 現役列／已刪列 `FOR UPDATE`；`rev5:` 同名 |
| `list_active`（收 `&UserListFilter`）、`list_deleted` | 同上 | `pub async fn`（conn、篩選、1 起算頁碼、頁長）→ `Result<(Vec<Model>, u64), DbErr>` | §6；`rev5:` `list`／`list_deleted` |
| `UserListFilter` | 同上 | `pub struct { user_name, nick_name, user_phone, user_email: Option<String>, user_gender, status: Option<i16> }` | 六欄篩選（rev5 四欄） |
| `UserCreate`、`UserPatch` | 同上 | `pub struct`（`UserPatch` 可空欄 `Option<Option<_>>`、只帶異值欄） | insert／update_fields 定型載體 |
| `UserWriteError { NameTaken, EmailTaken, Db(DbErr) }` | 同上 | `pub enum` | 活性唯一 23505 依索引名收斂 |
| `insert`、`update_fields`、`soft_delete`、`restore`、`set_password`、`set_session_policy` | 同上 | `pub async fn`、只收 `&DatabaseTransaction` | §1.1 寫者；`rev5:` 同名族（自開交易、寫稽核＝不帶） |
| `active_name_taken`、`active_email_taken`（後者收 `exclude: Option<i64>`） | 同上 | `pub async fn` → `Result<bool, DbErr>` | 現役唯一先驗 |
| `advisory_lock_user`（簽章收窄） | 同上 | `pub async fn (&DatabaseTransaction, i64)` | 既有（泛型形）改；compile_fail doctest |
| `role_ids_all_of_user`、`role_ids_active_of_user`、`roles_by_user_ids` | `model/facade/sys_user_role.rs` | `pub async fn`；回 `BTreeSet<i64>`／`Vec<(i64, String)>`／`HashMap<i64, Vec<(i64, String, String)>>`；原樣回 `DbErr` | T／A／清單回填 |
| `replace_roles_of_user`、`delete_all_of_user` | 同上 | `pub async fn`、只收 `&DatabaseTransaction`；回 `bool`／`u64` | §1.2；`rev5:` 同名 |
| `revoke_sids_of_user`（私有）、`revoke_all_of_user` | `model/facade/sys_token.rs` | 後者 `pub async fn (conn, i64) -> Result<Vec<String>, DbErr>` | §1.4；`rev5:` 同名 |
| `EVENT_REVOKED`、`REASON_USER_DISABLED`、`REASON_USER_DELETED`、`REASON_PASSWORD_RESET`、`REASON_PASSWORD_CHANGED`、`REASON_ADMIN_KICK` | `model/facade/session_event.rs` | `vocabulary!` 展開之 `pub const` | §1.5 |
| `touch`、`last_set_at` | `model/facade/sys_pwd_custody.rs`（新檔；facade 第十三支） | `pub async fn`；`touch` 只收具型交易 | §1.3；`rev5:` 同名 |
| `protected_button_codes` | `model/facade/sys_casbin_policy.rs` | `pub async fn (conn, &[String]) -> Result<Vec<String>, DbErr>` | §3.10（rev5 無） |
| `removed_codes` | `model/facade/sys_menu.rs` | `pub fn`（純函式；既有 `obsolete_codes` 改呼之） | §3.10 移除集（rev5 無） |
| `hash`、`NewPassword`（`prepare`／`plain`／`phc`；遮蔽 `Debug`）、`PasswordPolicy`、`load_password_policy`、`validate_against_policy`、`VIOLATION_*` 八枚、`MAX_BYTES`、`cooldown_remaining_secs(conn, target_id, operator_id) -> Result<Option<u64>, AppError>` | `model/password.rs` | `pub` | §2.5；`hash`＝`getrandom::fill` 16 bytes＋`hash_password_with_salt`（`rev5:` `SaltString` 路徑不帶） |
| `Kick`、`ResetPassword`、`ChangePassword` | `model/audit.rs` | `AuditOperation` 變體 | §7 |
| `precheck`、`record_failure`、`clear`、`Throttled`、`CHANGE_PWD_MAX_FAILS`、`CHANGE_PWD_WINDOW_SECS` | `throttle/change_pwd.rs`（新檔；`throttle/mod.rs` 增 `pub mod`） | `pub`；三支收 `Option<&SessionCache>` 與 uid | §2.4；`rev5:` 同名 |
| `CHANGE_PWD_KEY_PREFIX`、`change_pwd_key`、`incr_with_window`、`REASON_ADMIN_KICK` | `cache/mod.rs` | `pub` | `rev5:` 同名（鍵 builder 名 `change_pwd_fail_key`） |
| `AppError::BizData(Cow<'static, str>, serde_json::Value)`、`AppError::ModalLogoutByAdmin`、`msg_key` 22 常數、`MSG_KEYS: [&str; 68]` | `error.rs` | `pub` | §11 |
| `password_policy_invalid()`；`THROTTLE_DEGRADED_SOURCES: [&str; 11]`（增 `redis_change_pwd`） | `obs.rs` | `pub` | §2.4、§2.5 |
| `SELF_SERVICE_ROUTES: [&str; 1] = ["user-center"]` | `handler/route.rs` | 模組私有 `const` | getUserRoutes 授權過濾後恆併入（ADR-00077）；`rev5:` 同名 |
| `m0003_seed_button_governance` | `rust-api/migration/src/` | `Migration`（`DeriveMigrationName`） | §9.1（rev5 零 migration） |
| `UserRowsGuard`、`SeedUserRestoreGuard`、`PwdCustodyRowsGuard` | `model/facade/test_kit.rs`（`tests/common/mod.rs` 鏡像 `UserWriteGuard`、`SeedUserWriteGuard`、`PwdCustodyWriteGuard`） | `pub(crate)`（tests 側 `pub`） | §10；`rev5:` `UserCleanup` 等名不帶回 |

- 前端（標記與用途住 `contracts/code-gates.md` §1）：`src/service/api/rev6-user-admin.ts`（`fetchGetUserList`、`fetchGetDeletedUsers`、`fetchAddUser`、`fetchUpdateUser`、`fetchDeleteUser`、`fetchBatchDeleteUser`、`fetchRestoreUser`、`fetchKickUser`、`fetchResetUserPassword`、`fetchUpdateUserSessionPolicy`、`fetchUnlockLogin`）、`src/service/api/rev6-user-center.ts`（`fetchGetPasswordPolicy`、`fetchChangePassword`）；`src/typings/api/rev6-user-admin.d.ts`（`Api.UserAdmin`）、`src/typings/api/rev6-user-center.d.ts`（`Api.UserCenter`）——型名全集＝兩支 wire 契約之「共用型」節（`Api.UserAdmin` 13 型、`Api.UserCenter` 5 型）；四支落地＝U14；新檔 `src/components/custom/pwd-gen-modal.vue`、`src/views/manage/user/modules/user-reset-pwd-modal.vue`、`src/views/manage/ip-rule/modules/ip-unlock-modal.vue`、`src/views/user-center/modules/password-card.vue`、`src/hooks/business/pwd-policy.ts`。
- 工具與閘：`tools/schema-gate.py`（`seed_add` 序號合成）、`tools/walkthrough-baseline.py`（`SCHEMA_VERSION = 4`；新欄 `migrations`、`sys_user_rows`；`BOUNDED_TABLES` 增 `sys_user`；可變欄名冊 `SYS_USER_MUTABLE_COLUMNS`〔含軟刪兩欄〕；合成鏈執行期 importlib 載入 `tools/schema-gate.py`；清理面增 `sys_pwd_custody`；redis 前綴增 `cpwd`）、`tools/msg-key-gate.py`（斷言 2 擴認三形＋`BIZ_DATA_KEYS` 分階段射程守；`FRONTEND_MSG_CONSUMERS` 同批擴）、`tools/view-render-guard.py`（判準 (b)、`ANCHORS`）、`tools/zh-tw-lint.py`（新碼面閘）、`tests/authz_entrypoint_lint.rs` 之 `NO_ESCALATION_CALL_FILES`、`deploy/grafana-provisioning/alerting/rules.yml` 之 `obs016-password-policy-invalid`。
- 寫入件之公開入口一律只收 `&DatabaseTransaction`；新增公開寫入入口者同批於模組 doc 之具型交易機器守補正面孿生與 compile_fail 一段。新建件落地即成假述之現在式句（模組 doc、檔頭數量詞與「不帶／不搬／後刀域」類碼註）之種子全表與承載單元＝research R22（同一事實只住該處）；處數以 `python3 tools/docsync errata <詞>` 現算。
