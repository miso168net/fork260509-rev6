# Data Model — 006-authz-governance（Phase 1）

> ★本刀**零 migration、零 seed 變更**（spec FR-002）——本檔描述 001 刀基線既有結構之**消費形**、狀態機、候選集、保護謂詞、守門固定序、觸發矩陣與歸檔不變式，不含任何 DDL。承 `rev5:006` data-model 形、依 rev6 拍板改寫（翻案不帶回五項與差異點住本刀 research）。
> wire 逐欄定義住 `contracts/wire-authz-governance.md`／`contracts/wire-policy-archive.md`；拒因鍵、發出點與落地時序住 `contracts/msg-keys.md`（譯文之家＝三檔 locale `backend` 子樹＝ADR-00039 決定 2）；機器守判準住 `contracts/code-gates.md`；ADR 之親決時點住本刀 research 之「ADR 配號與親決時點表」。
> 量測（2026-10-01、rust-api pin `8c8b5e1`）之量法＝以 python3 唯讀解析 `rust-api/migration/src/m0002_baseline_seeds.rs` 之 `SEED_CASBIN_RULE`／`SEED_SYS_MENU`／`SEED_SYS_ROLE` 與 `rust-api/server/src/router.rs` 之 `ROUTES` 區塊；量測值只作背景與自證前提、不入任何判定（判定一律現讀資料庫）。
> 本檔「新建」＝rev6 現無、本刀新立之件；新建件定名之單一出處＝§13（含 `msg_key` 三常數；★wire DTO 型名〔含 rust 專屬元素型 `MenuId`〕除外＝兩支 wire 契約之「共用型」節）。

## §1 既有資料表的消費面

### 1.1 `casbin_rule`（授權真相；變體 D；seed 163 列；本刀首個授予寫入者）

欄與可空性以 `rust-api/sea-orm-adapter/src/migration.rs`（基底 8 欄）＋`m0001_baseline_schema.rs` 之 ALTER（治理三欄）＋`rust-api/entity/src/casbin_rule.rs`（11 欄）為準（RL-0024）：

| 欄 | 型／可空 | 本刀消費 |
|---|---|---|
| `id` | bigint NN 自增 PK（`casbin_rule_id_seq`） | 授予與復原回插一律取 nextval＝新 id；撤銷之刪除集以列 id 圈定 |
| `ptype` | varchar(18) NN | 恆 `p`（seed 163 列全 `p`、寫入面只產 `p`）；封死謂詞與 NoOp 身分鍵之一欄 |
| `v0` | varchar(125) NN | 角色代碼；現況讀之角色條件＝`v0 = 標的角色代碼` |
| `v1` | varchar(125) NN | 標的：選單維＝路由名、按鈕維＝按鈕碼、端點維＝路徑 |
| `v2` | varchar(125) NN | 維度標記 `menu`／`button`，或 HTTP 方法（白名單＝新建 `router::endpoint_methods()`＝`GET`／`POST`／`DELETE`）；端點維以白名單**正向**辨識、不以排除他維反推、不另立維度欄 |
| `v3`～`v5` | varchar(125) NN、**無 default** | 恆空字串；授予 INSERT MUST 顯式寫 `''` |
| `protected` | bool NN default false | 受保護撤銷拒之判準、封死謂詞之來源；授予與復原回插一律**顯式** FALSE；一般管理介面永不寫此欄 |
| `created_at` | timestamptz NN default `now()` | 授予與復原回插之 INSERT 省略本欄、由 DB default 補（＝交易起始時刻；`model/facade/mod.rs` 之 `now_ts` doc 所定 rev6 慣例） |
| `created_by` | bigint 可空 | 授予＝操作者 uid、復原回插＝復原者 uid；seed 163 列全 NULL ⇒ `created_by IS NULL`＝seed 政策列之錨（BL-00136 形①、§11） |

- 約束：PK＋唯一索引 `unique_key_sea_orm_adapter`（`ptype, v0, v1, v2, v3, v4, v5`＝**七欄身分鍵**）；復原 NoOp 判定之欄集即此（§7）。授予之新授集與現況互斥 ⇒ 結構上不撞此鍵；復原不設 23505 收窄（ADR-00065 決定 10）。
- 轉接器實體（`rust-api/sea-orm-adapter/src/entity.rs`）只 8 欄（`id`、`ptype`、`v0`～`v5`）：其 `add_policy` 只 Set 六值欄 ⇒ 落不了 `created_by`、`protected` 走 default；已存在之鍵回 Err 且已吃 nextval（LL-00035）⇒ 生產寫入面 MUST NOT 經它（FR-012）。判定面重建經轉接器讀 8 欄，治理欄對判定引擎不可見。
- seed 分布（量法見檔頭）：

  | 維 | R_SUPER | R_ADMIN | R_USER_COMMON | 計 |
  |---|---|---|---|---|
  | 選單（`v2='menu'`） | 77 | 5 | 3 | 85 |
  | 按鈕（`v2='button'`） | 20 | 3 | 1 | 24 |
  | 端點（`v2` ∈ 白名單） | 50 | 3 | 1 | 54（GET 25／POST 22／DELETE 7） |

  - 端點維相異（路徑,方法）50＝R_SUPER 50 列各一；同路徑多方法 0；R_ADMIN／R_USER_COMMON 之 4 列與 R_SUPER 同鍵（跨角色重複）。
  - **受保護授權列 19 列、皆屬 R_SUPER**：選單維 4（id 10 `manage_role`、11 `manage_menu`、69 `manage_system-settings`、72 `manage_policy-archive`）＋端點維 15（id 32、33、52～57、64～68、70、71；GET 8／POST 7）；按鈕維 0。選單維四列所指之 seed 選單列（sys_menu id 4／5／9／10）皆 `sys_menu.protected`＝TRUE、受選單刪除守門擋下 ⇒ 連動歸檔之 `menu_soft_delete` 結構上歸不到受保護授權列。
  - 本刀十支端點之 seed 政策列＝32／33、52～57、70／71（皆受保護、皆 R_SUPER）。
  - 對本刀後候選集（§3）：R_SUPER 持有端點候選 35 鍵之全部；候選外 seed 端點列 16＝R_SUPER 15（id 1、17、18、19、20、68〔受保護、`/systemManage/updateUserSessionPolicy`〕、139、140、141、151、152、154、155、158、159）＋R_ADMIN 1（id 2 `/systemManage/getUserList`）；選單維 85 列之 `v1` 全在 seed 治理域路由名（78）內、按鈕維 24 列全在治理域按鈕碼聯集（20 碼）內 ⇒ seed 下選單與按鈕維之候選外列 0。
  - seed 序列態 `casbin_rule_id_seq`＝(163, true)；`created_at` 全為 `2026-08-05T00:00:00+00:00`。

### 1.2 `sys_casbin_policy_archive`（授權歸檔；14 欄；seed 0 列；本刀首個讀者與刪除者）

欄與可空性以 `m0001_baseline_schema.rs` 之建表段與 `rust-api/entity/src/sys_casbin_policy_archive.rs` 為準：

| 欄 | 型／可空 | 本刀消費 |
|---|---|---|
| `id` | bigint 自增 PK（`sys_casbin_policy_archive_id_seq`；seed 態 (1, false)） | restorePolicy 之請求識別；復原第 0 步 `FOR UPDATE` 鎖讀 |
| `role_id` | bigint 可空 | 來源角色 id：既有私有 `insert_snapshot` 以 `v0` 反查**活性**角色（未軟刪、啟停不論、**不加鎖**、查無 NULL）；本刀撤銷時標的角色列已鎖且活性 ⇒ 恆非 NULL；NULL 只見歷史列或直寫列 ⇒ 不可復原（復原第②腿、旗標②半） |
| `created_at`／`created_by` | timestamptz 可空／bigint 可空 | 原授權列治理欄快照（`insert_snapshot` 恆寫 `Some(created_at)`；seed 列之 `created_by`＝NULL）；復原**不回灌**；回收桶列形不含此兩欄（沿 rev5 as-built、逐欄住 contracts） |
| `archived_at` | timestamptz NN default `now()` | 歸檔時刻（＝交易起始時刻）；回收桶排序主鍵（降冪） |
| `archived_by` | bigint 可空 | 歸檔者 uid（授權撤銷＝操作者；連動歸檔＝該寫端操作者）；wire 回填帳號名 |
| `archive_reason` | varchar(32) NN | 六值封閉（§7-1；最長 `menu_button_removed` 19 字元）；wire 原字面 |
| `ptype`、`v0`～`v2` | varchar NN | 政策快照；`v0`＝角色代碼篩選鍵、`v2`＝維度推導源（§8） |
| `v3`～`v5` | varchar(125) NN default `''` | 快照 |

- 索引：`idx_casbin_archive_archived_at (archived_at)`、`idx_casbin_archive_role_dim (v0, v2)`——雙篩與排序現成、讀端零 migration。
- 三自由度續 won't-use（ADR-00044 決定 4；復核結論＝ADR-00065 決定 2）：`role_id` 可空維持；**無受保護快照欄**（承重前提＝ADR-00064 決定 4②、spec FR-024）；**無 `menu_id` 同實例欄**（選單維與按鈕維之列恆不可復原）。亦無維度欄（維度由 `v2` 推導）。
- 寫入者：005 刀起之連動歸檔三支（`archive_all_role_policies`／`archive_menu_policies`／`archive_button_codes`）＋本刀授權撤銷（新建 `archive_revoked_policies`）。讀者與刪除者：本刀之 getArchivedPolicies（讀）與 restorePolicy（Applied／NoOp 消費＝刪列）；除此之外歸檔列永不刪除、不設保留期（BL-00133）。

### 1.3 `sys_role`（本刀零寫；鎖讀＋無鎖讀）

- **零寫**：三維寫端與復原不改角色列任何欄（含 `updated_*`）⇒ 無角色列快照可入稽核（§10）。
- **鎖讀**＝既有 `sys_role::find_active_by_id_for_update`（`WHERE id = $1 AND deleted_at IS NULL FOR UPDATE`；停用照鎖、只收具型交易）：三維寫端經 `handler/role.rs` 既有私有 `lock_role`（查無或已軟刪＝`biz.role.notFound`）；restorePolicy 以歸檔 `role_id` 鎖讀、再比對其代碼＝歸檔 `v0`（ADR-00065 決定 4；等價前提＝代碼建後不可變〔updateRole 對 `roleCode` 出現即拒〕＋活性代碼唯一〔`sys_role_code_active_uniq`〕＋歸檔 `role_id` 係歸檔當下以 `v0` 反查所得）。
- **無鎖讀（新建）**：`sys_role::active_code_of`（三支現況讀端之 id→代碼；活性不含狀態）；`sys_role::active_ids_by_codes`（可復原旗標②半；空集不查；★不可複用 `all_active_enabled`——其濾 `status = 1`，停用角色之列會被誤判非同實例）。以代碼鎖讀件（`rev5:` 之 `find_active_by_code_for_update`）續不帶。
- **常數**：`SUPER_ROLE_CODE`＝`"R_SUPER"`（封死豁免之單一宣告源）；`SEEDED_ROLE_IDS`＝`[1, 2, 3]`（R_SUPER 受 seeded 守門擋刪＝ADR-00064 決定 4③ 之前提之一）。
- **seed**：3 列（1 R_SUPER／2 R_ADMIN／3 R_USER_COMMON；`status` 皆 1、`role_home` 皆 `home`、`created_by` 皆 NULL）；`sys_user_role` 3 列（(1,1)／(2,2)／(3,3)）⇒ 持 R_SUPER 之帳號恰 1（Super）；`system_settings` 之 `single_session_default`＝`off`（多會話允許 ⇒ 同帳號多分頁並行編輯可達；ADR-00068 款 11）。
- 首頁讀寫（getRoleHome／updateRoleHome；`sys_role::home_of_role`／`set_home`）為 005 刀交付、本刀零後端改動，由選單權限彈窗之首頁下拉消費（spec FR-033、Clarifications 2026-10-01 第三題）。

### 1.4 `sys_menu`（本刀零寫；治理域只讀）

- 讀＝既有 `sys_menu::list_governed`（治理域＝`deleted_at IS NULL`、**含停用**；同層序 `"order" ASC NULLS LAST, id ASC`）：選單維之候選與 id↔路由名映射表**取自同一次讀**（同一真源、同一時點；ADR-00066 決定 3）；按鈕碼聯集亦由一次讀逐列導出。路由名於治理域內唯一（部分唯一索引 `sys_menu_route_name_active_uniq`）⇒ 映射 1:1。
- `buttons` jsonb 可空（`[{code, desc}]`）：碼集經既有 `sys_menu::button_codes_of`（首見序去重；NULL 或 JSON `null`＝空集；★壞形＝`DbErr::Custom`→`5000`，不帶 rev5 跳過語意）；與絕版判定 `sys_menu::obsolete_codes` 之私有掃描不共用（FR-014）。
- 顯示域（`list_active`／`display_route_names`）**不入**候選與映射（誤用之兩種失效形皆禁＝ADR-00066 決定 3）；首頁下拉候選為既有 getAllPages（顯示域，005 刀交付）。
- seed：78 列、全啟用、零已刪；受保護 8 列（id 1、2、3、4、5、6、9、10）；按鈕碼聯集 20 碼；id 10＝`manage_policy-archive`（`route_path` `/manage/policy-archive`、`component` `view.manage_policy-archive`、`icon` `mdi:recycle`、`i18n_key` `route.manage_policy-archive`、受保護、父＝2）＝回收桶頁之側欄項，其頁級門＝授權列 72。

### 1.5 `sys_operation_log`（append-only；擴寫入者）

授權寫端（三維三支）與復原為新寫入者；列形見 §10。寫入經既有 `sys_operation_log::write_in_txn`（與業務寫入同交易；稽核寫失敗＝整筆放棄）；`real_ip` INET NOT NULL ⇒ 操作者上下文缺席只能拒寫 `5000`。

### 1.6 `sys_user`／`sys_user_role`

- `sys_user`：回收桶讀端之 `archivedBy` 經既有 `sys_user::find_names_by_ids`（空集不查、★不濾軟刪、查無不入表→呼叫端映 null）；包裝件之落點（自持或提升進 `handler/common.rs`）由本刀 research 依 `handler/common.rs` 之 BL-00090／BL-00113 收攏紀律判定。
- `sys_user_role`：零寫零新讀；授權判定鏈仍經 `require_policy` 每請求 `roles_of_user` 現查（新授權於判定面換上後之下一請求即生效）。

## §2 狀態機（每列「現態×事件→次態＋副作用」；副作用皆同一交易）

### 2.1 授權列（以 `casbin_rule` 列論；同一七欄身分鍵至多一列現役、可有多列已歸檔）

| 現態 | 事件 | 次態 | 副作用與守門 |
|---|---|---|---|
| 不存在 | 授予（三維寫端 Applied、鍵屬新授集） | 現役·非受保護（新 id、`protected=FALSE`、`created_by`＝操作者） | 該請求一列稽核 `update`；commit 後判定面同步 |
| 不存在 | 授予（端點維、標的非 R_SUPER、鍵 ∈ 封死集） | 不存在 | 整批拒 `biz.role.protectedGrant`：本請求零變更（rollback）、零稽核、零同步 |
| 現役·非受保護 | 授權撤銷（鍵屬撤銷集；含 R_SUPER 名下者＝brainstorm §0 Q14） | 已歸檔（`menu_revoke`／`button_revoke`／`endpoint_revoke`；`role_id`＝標的角色 id） | 該請求一列稽核 `update`（與授予同列計）；commit 後判定面同步 |
| 現役·受保護 | 授權撤銷（鍵屬撤銷集） | 現役（不變） | 整批拒 `biz.role.protectedRevoke`：本請求零變更、零稽核、零同步 |
| 現役（候選內、屬期望） | 三維寫端 Applied | 現役（不變；列 id 不變） | 不寫 |
| 現役（候選外） | 任一三維寫端 | 現役（不變） | 不入撤銷集、不入回應（射程＝候選集；§3） |
| 現役（任一） | 連動歸檔（005 刀：刪角色／刪選單／按鈕碼絕版） | 已歸檔（`role_soft_delete`〔三維含受保護〕／`menu_soft_delete`／`menu_button_removed`） | 005 刀 data-model §2 既有；本刀零改動 |
| 已歸檔·`endpoint_revoke` | 復原（五腿全過、身分鍵無現役列） | 現役·非受保護（新 id、`created_by`＝復原者）＋該歸檔列刪除 | 稽核 `restore` 一列；commit 後同步（Applied） |
| 已歸檔·`endpoint_revoke` | 復原（五腿全過、身分鍵已現役） | 該歸檔列刪除；現役列不動 | 零稽核、不同步、commit（NoOp） |
| 已歸檔（任一原因） | 復原（第①～④腿任一拒） | 已歸檔（不變） | `biz.policy.notRestorable`；rollback、零稽核、零同步 |
| 已歸檔·不可復原五值 | 復原 | 已歸檔（不變） | 第①腿即拒、不取角色列鎖 |

★「受保護」只指 `casbin_rule.protected`（受保護授權列）；與 `sys_menu.protected`（不可刪、不可停用、不可改父）不同義。受保護旗標在一般管理介面永不可設、不可解（島 G2 防鎖死 by-design）⇒ 列之受保護態只隨基線資料（seed／migration）變動。

### 2.2 三維寫端 outcome（updateRoleMenu／updateRoleButton／updateRoleEndpoints）

| outcome | 成立條件（取先序腿；§5） | 交易收場 | 回應 | 稽核 | 判定面同步 |
|---|---|---|---|---|---|
| 操作者缺席 | 請求上下文不可得 | 未開交易 | `5000` | 0 | 否 |
| NotFound | 鎖角色列查無或已軟刪（含 body 缺席或壞形〔含期望集鍵缺席或拼錯〕收斂之角色鍵 0） | rollback | `2222`＋`biz.role.notFound` | 0 | 否 |
| Rejected{ProtectedRevoke} | 撤銷集含受保護授權列 | rollback | `2222`＋`biz.role.protectedRevoke`、`data` null | 0 | 否 |
| Rejected{ProtectedGrant}（端點維限定） | 標的非 R_SUPER ∧ 新授集 ∩ 封死集 ≠ ∅ | rollback | `2222`＋`biz.role.protectedGrant`、`data` null | 0 | 否 |
| Applied{revoked, granted, effective}（含空 diff） | 其餘 | commit（脫離請求之收場 task 內） | `0000`＋`{revoked, granted, effective}` | 恰 1 列 `update` | 是（不問 diff） |
| 故障 | 資料庫錯誤（含按鈕碼清單壞形、撤銷之等集檢查不等、commit 失敗） | rollback | `5000` | 0 | 否 |
| 收場 task 被取消 | 收場 task 自身被中止（請求 future 之丟棄不屬此態——收場已脫離請求生命週期） | commit 未必完成 | `5000`（`security.authz` error 一則） | 隨 commit 是否已落（0 或 1） | 未必完成 |

恰兩態業務 outcome（Applied／Rejected；FR-015）、無 NoOp；拒因只供 wire 純 key，被擋項（`blocked`）只供 tracing 與測試斷言、永不上 wire。

### 2.3 restorePolicy outcome

| outcome | 成立條件（§5.4） | 交易收場 | 回應 | 稽核 | 判定面同步 |
|---|---|---|---|---|---|
| 操作者缺席 | 請求上下文不可得 | 未開交易 | `5000` | 0 | 否 |
| NotRestorable | 歸檔列查無（識別不存在、已被消費、body 收斂之識別 0）或第①～④腿任一拒 | rollback（歸檔列保留） | `2222`＋`biz.policy.notRestorable`、`data` null | 0 | 否 |
| NoOp | 五腿全過、七欄身分鍵已現役 | commit（只刪歸檔列） | `0000`、`data` null | 0 | 否 |
| Applied | 五腿全過、身分鍵無現役列 | commit | `0000`、`data` null | 恰 1 列 `restore` | 是 |
| 故障 | 資料庫錯誤 | rollback | `5000` | 0 | 否 |
| 收場 task 被取消 | 同 §2.2 該列 | commit 未必完成 | `5000`（`security.authz` error 一則） | 隨 commit 是否已落（0 或 1） | 未必完成 |

NoOp 與 Applied 對前端不可區分；NoOp 使回收桶少一列而稽核表無痕跡（spec Clarifications 2026-10-01 首題；已知態＝ADR-00068 款 12）。

### 2.4 歸檔列與判定面

- 歸檔列：寫入（授權撤銷三原因、連動歸檔三原因）→ 唯一消費路徑＝restorePolicy 之 Applied／NoOp（刪列）；拒腿與一切其他寫端不改歸檔列。
- 判定面（記憶體授權判定實體）之狀態機沿 005 刀 data-model §2.3 不變（全新重建後一步換上、保留上一份、有界重試、`RELOAD_SERIAL` 全程互斥、單一行程前提）；本刀只擴觸發者（§6）。

## §3 候選集與現況讀之射程

### 3.1 三維候選集（與判定面同源、不多列不漏列；FR-010、ADR-00066 決定 3）

| 維 | 候選鍵（v1, v2） | 料源（取得時點） | 期望集收單形 | orphan skip 判準 | 生效集合之識別 | 候選讀端 |
|---|---|---|---|---|---|---|
| 選單 | （路由名, `menu`） | `sys_menu::list_governed` 一次讀 → 新建 `governed_route_names_by_id`（純函式）＝id→路由名映射表；候選＝其值域（寫端：角色列鎖後、同交易） | 選單 id 陣列 | id 不在映射表（已刪、不存在、負值、界外大值） | 選單 id | 既有 getMenuTree（治理域輕量樹） |
| 按鈕 | （按鈕碼, `button`） | `list_governed` 一次讀、逐列 `button_codes_of`、依同層序首見去重（新建 `governed_button_codes`；任一列壞形＝整請求 `5000`） | 按鈕碼陣列 | 碼不在聯集 | 按鈕碼 | getAllButtons（同件、同序） |
| 端點 | （路徑, 方法） | 新建 `router::policy_endpoints()`：`ROUTES` 中 `protection == Protection::Policy` 之（路徑, `method.as_str()`）、依註冊序；編譯期常數、handler 於交易前取得並以參數傳入 facade | `{path, method}` 陣列 | 鍵不在候選（未註冊或非政策保護之路徑、白名單外方法、大小寫或路徑變體） | `{path, method}` | getAllEndpoints（同件、同序；本刀後 35 鍵） |

- 端點候選之方法恆為白名單字面（`policy_endpoints()` 由 `HttpMethod::as_str` 導出）⇒ 候選集 ⊆（任意路徑 × `endpoint_methods()`）。
- 候選集於交易期間不變：選單與按鈕維寫端入選單序列化域、改動治理域之選單寫端全在域內（島 H1）；端點維候選為編譯期常數。
- ★已知邊界（ADR-00066 決定 3）：治理域中 `parent_id` 成環之列及其子孫在候選集內、卻不在 getMenuTree 樹中（`sys_menu::build_governed_tree` 整環剔除）——UI 無從勾選，期望集未帶其鍵即入撤銷集；環只可能由直改庫或缺陷形成。

### 3.2 期望集處理、比對與生效集合（FR-009、ADR-00066 決定 2／6）

1. 期望集 orphan skip（候選外項靜默略過、不產生孤兒授權、不另提示）→ 去重（保首見序）⇒ **生效集合**（以各維介面識別、首見序）與期望鍵集。
2. 現況＝標的角色名下該維現役列（選單維 `v2='menu'`、按鈕維 `v2='button'`、端點維 `v2 ∈ endpoint_methods()`；`id` 升冪；寫端於角色列鎖後同交易讀）→ 以候選鍵集**收窄**（三維共用之單一濾點件、純函式；新建 `scope_live_to_candidates`）。
3. 撤銷集＝（現況 ∩ 候選集）中鍵 ∉ 期望鍵集者（保 id 升冪）；新授集＝期望鍵集中 ∉ 現況鍵者（**排序後**落列＝落列序確定）。
4. 候選外現役列：不撤、不授、不入生效集合；受保護撤銷拒只看候選內撤銷集；稽核計數只含候選內（ADR-00066 決定 4）。
5. 期望空集＋合法角色鍵＝合法全撤（候選內現役列全數撤銷歸檔、仍受受保護撤銷拒約束；brainstorm §0 Q15）；body 缺席或壞形＝角色鍵收斂為 0 ⇒ notFound 早拒、MUST NOT 演成全撤（FR-007）。
6. 寫讀閉合：生效集合在集合上恆等於寫後之「現況 ∩ 候選集」（次序不保證相同）。

### 3.3 現況讀之射程（spec Clarifications 2026-10-01 第二題、ADR-00066 決定 5）

- getRoleMenu／getRoleButton／getRoleEndpoints 回「**現況 ∩ 候選集**」、每項帶受保護旗標；收窄與寫端共用 §3.2-2 之同一濾點件與 §3.1 之同一候選取得件、不另寫第二份判準。選單維先以治理域路由名收窄、再以**同一次讀**之映射表反向映射回選單 id（候選外路由名因先收窄而不反射）。讀端無交易、不取鎖。序＝授權列 `id` 升冪。
- 與 rev5 HEAD 刻意分岔（spec 刻意分岔登記表「三維現況讀端之回應集」列）：rev5 按鈕維與端點維回全部現役列（`rev5:ADR 0056`「讀端維持現狀」）；本刀後 R_SUPER 端點維讀端回 35 列、rev5 形 50 列；UI 零差係就讀端取態本身而言（彈窗只畫候選）——22080（rev5 HEAD）之端點候選另含 15 支 `rev5:007`／`rev5:008` 路由（候選 50 對 35），端點權限彈窗之樹因此不同，該差屬候選集面（spec 刻意分岔登記表「端點候選集」列；`contracts/wire-authz-governance.md`「與 rev5 wire 逐欄比對」之 getAllEndpoints 列）。rev5 測試凡以讀端讀回候選外列為前提者，rev6 改以資料庫直讀觀察。

## §4 保護謂詞與判定次序

1. **受保護撤銷拒**（三維；島 G2、FR-011）：撤銷集中任一列 `protected=TRUE` ⇒ Rejected{ProtectedRevoke}；於比對完成後、任何寫入之前判定；整批、不壓縮（不剔除後放行其餘）。R_SUPER 名下 `protected=FALSE` 列可撤；候選外之受保護列（seed id 68）不入撤銷集。
2. **封死集**（島 G6、ADR-00064 決定 1）：現役授權列中滿足 `ptype='p' ∧ protected=TRUE ∧ v2 ∈ endpoint_methods()` 之（v1, v2）集；不問 `v0`；查詢件單點＝新建 `sys_casbin_policy::protected_endpoint_set`（以參數收白名單、單次 SELECT、不另取鎖、簽章收泛型連線）：兩掛點（updateRoleEndpoints 授予判、restorePolicy 第③腿）於自身交易內、標的角色列鎖之後呼叫＝鎖內現查；回收桶可復原旗標③半為無交易、無鎖之讀端消費（§8；不計掛點＝ADR-00064 決定 2）。白名單字面與 `menu`／`button` 不相交 ⇒ 選單維與按鈕維之受保護列結構上不入（FR-023）。只寫謂詞、不寫列數（seed 量測＝端點維受保護 15 鍵，見 §1.1）。
3. **授予側判定**（端點維限定；ADR-00064 決定 3）：標的角色代碼 ≠ `SUPER_ROLE_CODE` ∧ 新授集非空 ⇒ 查封死集；新授集 ∩ 封死集 ≠ ∅ ⇒ Rejected{ProtectedGrant}。R_SUPER 標的或新授集為空 ⇒ 零額外查詢（豁免）。
4. **次序**：先判撤銷、再判授予（兩拒因並存取先序；seed 下實務互斥——受保護授權列皆屬 R_SUPER、封死只擋非 R_SUPER 標的）。
5. **復原第③腿**：標的角色代碼 ≠ `SUPER_ROLE_CODE` ∧ 歸檔（v1, v2）∈ 封死集 ⇒ 拒；與授予側共用同一查詢件（雙路徑全覆蓋）。可復原旗標③半為讀端消費、不計掛點（ADR-00064 決定 2）。
6. **承重前提**（ADR-00064 決定 4）：①受保護旗標結構上寫不進來（授予與復原回插顯式 FALSE、寫端 DTO 無此欄）②受保護授權列結構上進不了可復原歸檔（§7-8）③他角色結構上無從持有 R_SUPER 代碼（代碼不可變、活性唯一、R_SUPER 受 seeded 守門擋刪）。

## §5 守門固定序（多重違規取先序腿；凍結入契約）

**四支寫端共同前置**：操作者上下文（`handler/common.rs` 之 `operator_from_context`＋本域私有 `operator_from`；缺席＝`5000`、先於一切守門、不開交易、不帶降級欄）；body 於抽取器經 `common::json_or_default` 收斂（缺席或壞形＝預設形：角色鍵或識別 0、期望集空；三維寫端之期望集鍵缺席或拼錯亦屬壞形）；交易由 handler 外殼 begin、內層 `<op>_in_txn` 承守門序；拒腿與故障腿顯式 rollback 後回錯；commit 與其後之判定面同步交脫離請求生命週期之收場 task（取消安全；§6）。資料庫故障經本域 `db_failure` 收斂 `5000`。

**選單序列化域成員（終態）**：005 刀七支（addMenu／updateMenu／deleteMenu／batchDeleteMenu／restoreMenu／deleteRole／batchDeleteRole）＋本刀 updateRoleMenu／updateRoleButton。**不入域**：updateRoleEndpoints、restorePolicy（及 005 刀之 addRole／updateRole／updateRoleHome）。入域＝內層首句 `sys_casbin_archive::enter_menu_domain`（advisory key `MENU_DOMAIN_LOCK_KEY`＝ASCII `rev6menu`）；機器證＝兩支入域寫端各一支 NOT-granted 等待案（`sys_casbin_archive::menu_domain_waiter_count`、64 位 key 拆兩欄比對）、兩支不入域者各一支零等待案（FR-049）。

**固定鎖序**：advisory（入域者）→ 歸檔表列（restorePolicy）→ `sys_role` 列 → `sys_menu`（三維寫端只讀不鎖）→ `casbin_rule`。三維寫端之歸檔只 INSERT 新列、不佔歸檔表列位。

### 5.1 updateRoleMenu（入域）
入域 → 鎖角色列（`lock_role`；查無或已刪〔含 id 0〕＝`biz.role.notFound`）→ 治理域一次讀（同交易）→ 映射表與候選 → 期望選單 id orphan skip＋去重 → 現況讀（同交易）→ 收窄至候選 → 導出撤銷集與新授集 → 撤銷集含受保護列＝`biz.role.protectedRevoke` → 撤銷（移入歸檔、`menu_revoke`）→ 新授 INSERT（排序後）→ 稽核 `update` → commit → 判定面同步 → Applied。

### 5.2 updateRoleButton（入域）
同 5.1，候選改為治理域按鈕碼聯集（任一列壞形＝`5000`、放棄交易）、現況 `v2='button'`、撤銷原因 `button_revoke`。

### 5.3 updateRoleEndpoints（不入域）
鎖角色列（`notFound`）→ 候選＝`router::policy_endpoints()`（交易前取得、參數傳入）→ 期望 `{path, method}` orphan skip＋去重 → 現況讀（`v2 ∈ endpoint_methods()`）→ 收窄 → 導出 → **撤銷判**（`biz.role.protectedRevoke`）→ **授予判**（標的非 R_SUPER ∧ 新授集非空 ⇒ 封死集現查；交集非空＝`biz.role.protectedGrant`）→ 撤銷（`endpoint_revoke`）→ 新授 INSERT → 稽核 `update` → commit → 判定面同步 → Applied。序列化層＝角色列 `FOR UPDATE`（與刪角色、復原共享）。

### 5.4 restorePolicy（不入域；ADR-00065 決定 3）
1. 鎖歸檔列（`FOR UPDATE`；查無＝拒——識別不存在、已被消費、body 收斂之 0）。
2. 第①腿 原因：`is_non_restorable_reason(archive_reason)` 為真＝拒（選單維與按鈕維之列恆止於此、不取角色列鎖）。
3. 鎖角色列（其查無屬第②腿判準）：`role_id` 為 NULL＝拒（不鎖、誠實退化）；`find_active_by_id_for_update(role_id)` 查無＝拒（含等鎖期間刪角色 commit、經 PG 重判活性條件剔除）。
4. 第②腿 同實例：鎖得角色之代碼 ≠ 歸檔 `v0`＝拒（零成本比對、承擔旗標與權威同判準；ADR-00065 決定 4）。
5. 第③腿 封死：§4-5。
6. 第④腿 端點在路由表：（v1, v2）∉ `router::policy_endpoints()` 之端點全集（參數傳入）＝拒（免幽靈政策）。
7. 第⑤腿 停用不擋：無判定（停用≠撤銷；ADR-00068 款 16）。
8. 七欄身分鍵已在現役 ⇒ **NoOp**：刪歸檔列 → commit；零稽核、不同步。
9. 否則 **Applied**：回插 INSERT（§7-6）→ 刪歸檔列 → 稽核 `restore` → commit → 判定面同步。

任一拒＝`biz.policy.notRestorable`（一因一鍵、不揭露哪一腿）、rollback、歸檔列保留。「五腿」為重驗腿之計數；鎖歸檔列與鎖角色列為動作序、不計腿。

### 5.5 三支現況讀端（getRoleMenu／getRoleButton／getRoleEndpoints；無交易、無鎖）
`?id=` 抽取器收斂（缺席或壞形＝0）→ 角色活性讀（新建 `sys_role::active_code_of`；查無或已軟刪＝`biz.role.notFound`；停用照讀）→ 候選取得（同寫端件）→ 現況讀 → 收窄（同寫端濾點件）→ 選單維反向映射 → 逐項帶受保護旗標。

### 5.6 候選讀兩支（getAllButtons／getAllEndpoints）
getAllButtons＝治理域按鈕碼聯集（`list_governed` 一次讀；壞形＝`5000`）；getAllEndpoints＝`router::policy_endpoints()`（零 DB）。皆零業務拒因、不帶受保護或封死預標（FR-014）。

### 5.7 getArchivedPolicies
查詢串抽取器收斂（任一欄壞形＝整串預設）→ 分頁與雙篩（§8）→ 頁內可復原旗標批次計算 → 歸檔者帳號名批次回填。零業務錯誤腿：錯誤集只有授權（未認證 `8888`／無權 `5003`）與內部（`5000`）。

## §6 判定面同步觸發矩陣（三類同一字面＝ADR-00067 決定 1；不 supersede ADR-00043）

| 類 | 寫端 | 觸發條件 | 不觸發 |
|---|---|---|---|
| 移除面（ADR-00043 決定 7，不變） | deleteMenu | 成功且實際歸檔 ≥1 列 | 被拒／標的不存在／零政策列 |
| | batchDeleteMenu | 成功且實際歸檔 ≥1 列（整批合計、至多一次） | 被拒／空陣列／合計零 |
| | updateMenu | 成功且實際歸檔 ≥1 列（按鈕碼絕版） | 一般欄變更／無絕版／被拒／no-op |
| | deleteRole | 成功且實際歸檔 ≥1 列 | 被拒／零政策列 |
| | batchDeleteRole | 成功且實際歸檔 ≥1 列（整批合計、至多一次） | 被拒／空陣列／合計零 |
| 授予面（本刀增列） | updateRoleMenu／updateRoleButton／updateRoleEndpoints | Applied 即觸發、不問 diff（含空 diff） | Rejected（`protectedRevoke`／`protectedGrant`）／notFound（含 body 收斂）／操作者缺席／未 commit 之故障 |
| 復原（本刀增列） | restorePolicy | Applied | NoOp／NotRestorable／操作者缺席／未 commit 之故障 |
| 零觸發 | addRole／updateRole（含停用）／updateRoleHome／addMenu／restoreMenu／選單啟停；本刀讀端六支（三維現況讀、候選讀兩支、getArchivedPolicies） | —— | 恆不觸發 |

- **授予面刻意例外**：授予面不以 diff 為門、移除面以實際歸檔為門——兩門方向相反為刻意並陳、MUST NOT 互相統一（重建冪等、空 diff 多跑一次無害且免「diff 漏算」一整類缺陷；ADR-00067 決定 2）。
- **觸發點**：交易 commit 之後、於脫離請求生命週期之收場 task 內（沿 005 刀 `handler/role.rs` 之 `settle_domain_write` 取消安全形）、呼叫時不持判定面讀鎖、每請求至多一次、同一支 `reload_enforcer`、零新機制；門以 outcome 判（Applied），★MUST NOT 套移除面之 `archived > 0` 門（套之＝只新授無撤銷者永不同步）；同步結果不影響寫端回應（commit 成功即回成功）。
- **兩窗**（ADR-00067 決定 6；記窗、不關窗）：①commit→換上之有界過渡窗——本刀起及於 API 授權：撤銷殘留（被撤端點於窗內仍放行）與授予面反向症狀（新授或復原之端點於窗內仍回 `5003`）②重試耗盡窗——舊面續用、恢復＝下次成功同步或重啟 rust-api。前提＝單一 rust-api 行程。
- 觀測：既有 `casbin_reload_total{outcome=ok|retry|exhausted}` 值集封閉恰三、告警 `obs016-casbin-reload-anomaly` 照舊；`ok` 增量來源自本刀起為三類（授予面空 diff 亦 +1）。

## §7 歸檔與寫入不變式（歸檔不變式＋授予與復原寫入形）

1. **原因值六**（判定單點＝既有 `sys_casbin_archive::is_non_restorable_reason`，三值擴五值；ADR-00065 決定 1）：

   | 原因 | 寫入者 | 可復原 |
   |---|---|---|
   | `role_soft_delete` | deleteRole／batchDeleteRole（`archive_all_role_policies`；三維含受保護列） | 否 |
   | `menu_soft_delete` | deleteMenu／batchDeleteMenu（`archive_menu_policies`＋獨有碼之 `archive_button_codes`） | 否 |
   | `menu_button_removed` | updateMenu 之絕版碼（`archive_button_codes`） | 否 |
   | `menu_revoke`（新建 `REASON_MENU_REVOKE`） | updateRoleMenu 之撤銷集 | 否 |
   | `button_revoke`（新建 `REASON_BUTTON_REVOKE`） | updateRoleButton 之撤銷集 | 否 |
   | `endpoint_revoke`（新建 `REASON_ENDPOINT_REVOKE`） | updateRoleEndpoints 之撤銷集 | **是（唯一）** |

   既有釘案 `archive_reasons_pin_three_literals_and_non_restorable_set_is_exactly_them` 同批改寫：正向臂五值、負向臂之 `menu_revoke`／`button_revoke` 移入正向臂、`endpoint_revoke` 與非法字面留負向臂（測名之 `three_literals` 字樣成假述＝改名、doc 與訊息之「三值」字面同批改；活書引測名處隨之改指＝research「as-built 改寫義務」節；FR-028）。
2. **撤銷＝移入歸檔、掃描集＝歸檔集＝刪除集**：新建 pub 入口 `sys_casbin_archive::archive_revoked_policies` 以私有 scope（`v0 = 標的角色代碼 ∧ id ∈ 撤銷集之列 id`）復用既有私有 `move_to_archive`（`id` 升冪掃 → 逐列快照 → 以剛掃 id 圈定 DELETE → 實刪列數 ≠ 掃描列數＝`DbErr::Custom`、呼叫端放棄交易）；回傳實際歸檔列數＝Applied 之 `revoked`。只收 `&DatabaseTransaction`、原因只收 `&'static str`（模組 doc 之具型交易機器守同批補正面孿生與 compile_fail 一段）。
3. **快照欄值**（既有私有 `insert_snapshot`）：`ptype`／`v0`～`v5`／`created_at`／`created_by` 逐欄過境；`protected` 不快照（歸檔表無此欄）；`role_id`＝以 `v0` 反查活性角色（撤銷時恆＝標的角色 id）；`archived_by`＝操作者 uid；`archived_at`＝DB default；`archive_reason`＝常數。
4. **授予 INSERT**（新建；facade 直接寫入）：`ptype='p'`、`v0`＝標的角色代碼、（v1, v2）＝新授鍵、`v3`～`v5`＝`''`、`protected`＝顯式 FALSE、`created_by`＝操作者 uid、`created_at` 省略（DB default）、`id`＝nextval；新授集排序後逐列寫入。MUST NOT 經判定引擎管理 API（島 G1）、MUST NOT 經轉接器 `add_policy`（LL-00035）。
5. **落寫次序**（同交易）：撤銷（歸檔＋刪）→ 授予 INSERT → 稽核；新授集與撤銷集鍵互斥、無互相依賴。
6. **復原回插**（Applied）：`ptype`／`v0`～`v5` 自歸檔快照過境、新 id、`protected`＝顯式 FALSE、`created_by`＝復原者 uid、`created_at` 由 DB default；快照之 `created_at`／`created_by` **不回灌**（復原＝一次新授予事件）→ 以 id 刪歸檔列 → 稽核 `restore`。
7. **復原 NoOp**：七欄身分鍵已現役 ⇒ 只刪歸檔列、授權表零寫。同一（角色,端點）多次撤銷留下之多列歸檔：復原其一後，其餘各列之復原皆為 NoOp。
8. **受保護列不入可復原歸檔**：授權撤銷觸及受保護列即整批拒；連動歸檔含受保護列者，其原因 `role_soft_delete` 屬不可復原，且受保護列今皆屬 R_SUPER、受 seeded 守門擋刪 ⇒ 可復原之歸檔列（唯 `endpoint_revoke`）原值恆 `protected=FALSE`（ADR-00064 決定 4②）；機器斷言「受保護列經撤銷路徑進歸檔之案數恆零」（SC-004）。
9. **不設 23505 收窄**（ADR-00065 決定 10）：授權表之生產 INSERT 寫者恰兩類（三維授予、復原回插），皆持同一 `v0` 所屬角色列鎖、NoOp 判定在鎖內 ⇒ 同鍵撞列於生產路徑結構不可達；任何資料庫錯誤一律 `5000`。
10. **歸檔先於軟刪**（005 刀既有、不變）：角色刪除 MUST 先歸檔後軟刪，否則 `role_id` 反查全落 NULL。

## §8 分頁與篩選（getArchivedPolicies）

| 面 | 規則 |
|---|---|
| 分頁 | 沿 005 刀分頁通則：`crate::envelope::page_params`（缺席＝第 1 頁、`PAGE_DEFAULT_SIZE` 10；`current` clamp `[1, PAGE_MAX_CURRENT]`＝10^7、`size` clamp `[1, PAGE_MAX_SIZE]`＝100；顯式 0 取下界 1）；查詢串任一欄壞形＝整串收斂預設；逾界回空頁、回應 `current`／`size`＝收斂後值、`total` 照回；facade 收 1 起算頁碼（rev5 收 0 起算）；MUST NOT 用 `page_or_all` |
| 排序 | 伺服端固定穩定序 `archived_at DESC, id DESC`；不收排序參數（ADR-00058） |
| 角色代碼篩 | `roleCode`＝`v0` 文字等值（區分大小寫）；空字串經 `common::blank_to_none` 視同缺席（只在 handler 收斂、facade 不再兜底）；可查已刪或停用角色之代碼 |
| 維度篩 | `dimension`＝`menu`→`v2='menu'`／`button`→`v2='button'`／`endpoint`→`v2 ∈ endpoint_methods()`（參數傳入）；三值區分大小寫，其餘值（含空字串）靜默不濾（rev5 形） |
| 不篩 | 原因值（brainstorm §0 Q17；列表已顯原因欄） |
| 維度推導 | 新建 `dimension_of(v2)`：`menu`／`button` 字面等值，其餘一律端點維（寫入面只產白名單內 `v2`，白名單外之 `v2` 結構上不可達；沿 rev5 as-built） |
| 可復原旗標 | 每列 `restorable`＝①`!is_non_restorable_reason(reason)` ∧ ②`role_id` 非 NULL 且＝代碼 `v0` 之現役活角色 id ∧ ③¬（`v0` ≠ R_SUPER ∧（v1, v2）∈ 封死集）∧ ④（v1, v2）∈ 端點全集；⑤免算；①不過即短路（選單與按鈕維列恆 false） |
| 旗標批次料源 | 只為頁內通過①之列取料：其 `v0` 排序去重 → `sys_role::active_ids_by_codes` 一次（空集不查）；通過①之列非空才 `protected_endpoint_set` 一次；④取參數傳入之 `router::policy_endpoints()` 全集；旗標非權威（無鎖、無交易）、權威恆為復原鎖內重驗；配「旗標＝權威」逐腿同判準測①～④各一 |
| 歸檔者名 | 頁內 `archived_by` 去重後一次 `sys_user::find_names_by_ids`；查無→null |

## §9 wire 映射規則

| 規則 | 內容 |
|---|---|
| 型名之家 | DTO 型名與逐欄形之家＝`contracts/wire-authz-governance.md`／`contracts/wire-policy-archive.md` 之「共用型」節；本節只定映射規則、不列型名 |
| 構造 | 回應一律由 DTO 逐欄白名單構造、絕不序列化原始資料列；欄名 camelCase（FR-005） |
| 角色鍵 | 一律 `id`（三支現況讀 `?id=`、三支寫端 body `id`；與既有首頁讀寫同式）；回收桶之 `roleCode` 為篩選文字、非識別鍵 |
| 期望集 | 選單維＝選單 id 陣列、按鈕維＝按鈕碼陣列、端點維＝`{path, method}` 陣列；欄名沿 rev5 契約形（`menuIds`／`buttons`／`endpoints`）、★期望集鍵必填：缺鍵或拼錯＝壞形、整包收斂為角色鍵 0 ⇒ notFound（rev5 as-built＝`#[serde(default)]` 收為空集＝全撤；本刀刻意分岔＝spec Clarifications 第七題）；收斂形之 wire 定案住 contracts |
| id 型 | 角色 id、選單 id、歸檔列 id＝number、經 `serialize_i64_number_guarded`（2^53 fail-loud）；歸檔列 `roleId`＝number \| null、經 `serialize_opt_i64_number_guarded`；選單維生效集合之元素亦 MUST 過守衛——`Vec<i64>` 直出即觸 `tests/wire_i64_guard_lint.rs` 之 `nested_generic_i64_fields_are_out_of_scope` 絆線（rev5 以 newtype 承載元素守衛；形住 contracts） |
| 受保護旗標 | 三支現況讀每項 `protected: boolean`＝該現役列之 `casbin_rule.protected`（後端單一真源；前端 MUST NOT 以 seed 靜態集判定）；候選讀端與寫端回應不帶 |
| 端點鍵 | `{path, method}` 恰兩鍵、`method` 為大寫白名單字面；前端葉鍵合成與反查屬前端（FR-033） |
| 寫端回應 | Applied＝`{revoked, granted, effective}`（計數只含候選內；`effective`＝§3.2 之生效集合、恆陣列、空 diff 亦 `[]`）；拒腿 `data` null、`msg` 純 key、不帶被擋項 |
| `dimension` | 回收桶列＝`menu`／`button`／`endpoint` 三值（§8 推導） |
| `archiveReason` | 原字面六值、不映譯 |
| 時間 | `archivedAt`＝RFC3339、偏移恆 `+00:00`、前端原樣顯示（ADR-00061） |
| 操作者 | `archivedBy`＝帳號名 string \| null（§8；不濾軟刪帳號） |
| 可空欄 | DB NULL＝顯式 `null`、不省略欄（typings `T \| null`；本域同 ADR-00047 決定 1 之逐域明文） |
| restorePolicy | Applied 與 NoOp 皆 `0000`＋`data` null |
| 型別承載 | 前端型住 `src/typings/api/rev6-authz.d.ts` 單一命名空間 `Api.Authz`（型名比照後端 DTO）；兩側不新宣告泛型（三維寫端回應用具體型；實例化既有 `Api.Common.PaginatingQueryRecord<…>` 允許）；`GENERIC_WIRE_TYPES` 名冊不變；`tests/wire_schema.rs` 之受審節謂詞（`in_role_menu_sections`）同批擴至 `Api.Authz.` 前綴 |

## §10 操作稽核列（稽核列形；同交易恰一列；零新詞）

| 欄 | 三維寫端（Applied、含空 diff） | restorePolicy（Applied） |
|---|---|---|
| `operation` | `update`（`AuditOperation::Update`） | `restore`（`AuditOperation::Restore`） |
| `entity_table` | `sys_role` | `sys_role` |
| `entity_id` | 標的角色 id | 來源角色 id（＝鎖得之角色列 id） |
| `payload_before` | NULL | NULL |
| `payload_after` | `{dimension, revoked, granted}`：`dimension` ∈ `menu`／`button`／`endpoint`；`revoked`／`granted`＝本次撤銷與新授列數（候選內） | `{archive_id, dimension, target, act}`：歸檔列 id、§8 推導之維度、歸檔 `v1`、歸檔 `v2` |
| `created_by` 與來源四欄 | 操作者（`AuditOperator`；`real_ip`／`peer_ip`／`x_forwarded_for`／`ip_confidence` 轉錄請求上下文） | 復原者（同上） |

- 零列之態：Rejected（兩拒因）、notFound、NoOp、NotRestorable、操作者缺席、一切未 commit 之故障。
- ★**例外登記**：005 刀之 `sys_role` 稽核列 payload＝整列逐欄快照（`handler/role.rs` 之 `audit_snapshot`、camelCase）；授權寫端不改角色列、無列快照可取 ⇒ 採計數摘要形（沿 rev5 as-built、`AuditEvent` 欄名改 rev6 之 `before`／`after`）；同表兩形以 `payload_after` 鍵集區分；摘要形鍵名沿 rev5 as-built 原字面（`archive_id` 為 snake_case、不改 camelCase——camelCase 慣例只屬整列快照形）。既有私有 `record_audit`（綁角色列快照）不套用，另立授權寫端與復原之稽核件（新建，§13）。
- 稽核斷言一律取水位窗、不寫絕對計數（FR-051）。`sys_operation_log` 模組 doc 之寫入者列舉於落地單元同批補列授權寫端與復原（RL-0011）。

## §11 測試資料與守衛

- **守衛表集**（皆 gate2 逐列比對、非 runtime-append）：`casbin_rule`／`sys_casbin_policy_archive`／`sys_role`／`sys_menu`／`sys_user_role`＋既有 `sys_operation_log` 水位窗（`OpLogRowsGuard`；tests 側組合殼自帶）。★測試 MUST NOT 留下對 seed 列之變更（FR-051）。
- **被撤 seed 授權列回補**（FR-044、FR-051；兩族同擴）：src 側 `model/facade/test_kit.rs` 之 `CasbinRuleRowsGuard`（與內含它之組合守衛 `RoleMenuDomainRowsGuard`）、tests 側 `tests/common/mod.rs` 之 `CasbinRuleWriteGuard`（與組合殼 `RoleMenuDomainWriteGuard`）——
  - arm：既有帶界水位（`COALESCE(max(id) FILTER (WHERE id < SYNTHETIC_UID_FLOOR), 0)`）＋序列 `(last_value, is_called)` 現讀之外，另快照**界下全列**全欄（`to_jsonb`）。
  - Drop 序：①刪 `id >` 水位 ②以快照回補缺列（原 id 原值；`INSERT INTO casbin_rule SELECT * FROM jsonb_populate_recordset(NULL::casbin_rule, $1) ON CONFLICT DO NOTHING`＝`tests/contract.rs` 之 `SeedMenuDeleteNet` 既有形）③`setval` 回 arm 值。★①MUST 先於②：復原回插之新 id 列與被撤 seed 列同七欄身分鍵，未刪即補＝撞 `unique_key_sea_orm_adapter` 被 `DO NOTHING` 吞掉、隨後新 id 列被刪＝seed 列永久缺席。
  - 兩族語意逐項一致、以逐字對賬案釘同形（既有 `self_held_synthetic_uid_floor_matches_src_verbatim` 同形）。
  - `PolicyArchiveRowsGuard`／`PolicyArchiveWriteGuard` 同形擴回補（復原之 Applied／NoOp 刪歸檔列；理由＝research R12 決定 1）。
  - 歸檔腿之快照與 Drop 序、兩表兩族之自證形（嵌套守衛、自建列代 seed 列、不碰 seed）與反向變異＝`contracts/code-gates.md` §5.1（同一事實只住該處、本檔不重列）。
  - 守衛 MUST 早於任一撤銷 seed 列之寫端單元落地（FR-044）。
- **seed 角色列欄值**：會改動 seed 角色列欄值之整合測試（例：以 updateRoleHome 改 R_SUPER 首頁）一律於測試交易內 rollback，或以列快照守衛（既有 `RowFixupGuard` 形）回寫該列被寫欄與 `updated_at`／`updated_by`（RL-0031：改回值≠改回痕）。
- **殘列不連坐**（BL-00136 形①、FR-045、SC-009）：
  - 兩支以 `sys_menu.created_by IS NULL` 錨 seed 之使用者路由案（`handler/route.rs` 之 `user_routes_tree_differs_by_role_and_home_is_navigable_leaf`、`model/facade/sys_menu.rs` 之 `seed_role_trees_differ_by_role_and_nest`；兩檔各持私有 `seed_names_by_sql`）改錨 `casbin_rule.created_by IS NULL` 之 seed 政策列；兩案內寫死 seed 名之前提斷言（例：「manage 零 R_ADMIN menu 政策」）改以 seed 政策列現算。
  - 測試件之直種現役政策一律落非 NULL 建立者（值不承載語意；改錨判準只看 IS NULL）：`test_kit::plant_live_policy` 保留轉接器 `add_policy`（判定面記憶體同持、已存在即 panic 之語意不變），同件內再以 raw SQL 對剛植列補寫 `created_by`；`model/facade/sys_menu.rs` 測試模組之 `plant_role_residue`（現直呼 `enforcer.add_policy`）改走 `plant_live_policy` 或同形補寫；`tests/contract.rs` 兩處不帶 `created_by` 之 raw INSERT 是否納入，視其是否與改錨案共存而定（判定住本刀 research）。
  - 殘列演練納此形：形①承重之殘列＝授 seed 角色於 seed 選單列、`created_by` 非 NULL 之選單維授權列，以 nextval 形植入（`RESIDUE_DRILL_OWNER` 號段之列落合成 id 界之上、任一帶界守衛 Drop 即清，對兩改錨案非承重）；dev 庫有此殘列時全量測試全綠；植列形與步驟＝`contracts/code-gates.md` §5.2（同一事實只住該處）；「全表」類期望一律案內以獨立 SQL 現算。
- **造列**：角色列與政策直插列取顯式大 id，號段依「表×檔」先於 `test_kit::ID_RANGES`（現 `[IdRange; 22]`）增列、型長同批改（未登記即 panic）；歸屬 `tests/` 者 `tests/common/mod.rs` 以同值字面自持並逐字對賬（`self_held_id_ranges_match_src_registry_verbatim`）；凡需判定面持有之政策列經 `plant_live_policy` 取 nextval（真判定面路徑）。`protected=TRUE` 之合成列＝測試直植合法（旗標只在 API 面不可寫）。
- **R_SUPER 豁免之探針形**（ADR-00064 決定 8；SC-004、FR-022）：零 seed 變更下 R_SUPER 已持有全部端點候選、seed 封死集每鍵恰一列且屬 R_SUPER ⇒ wire 面打不出「R_SUPER 自授封死集端點而新授 ≥1」，真豁免由 facade 層測試承載——交易內於非 R_SUPER 之第三方合成代碼名下（只植授權列、不建角色列）直種一列 `protected=TRUE` 之合成（路徑,方法）探針列 → 先自證「探針 ∈ 封死集，且 R_SUPER 與對照臂標的現役皆不持有」（否則豁免斷言 vacuous）→ R_SUPER 自授（期望＝其端點維現役全集＋探針、候選含探針——facade 以參數收候選集）⇒ Applied、撤銷 0、新授 1、新列 `protected=FALSE` → 對照臂：同探針授另建之非 R_SUPER 合成角色 ⇒ `biz.role.protectedGrant` → rollback 收尾。wire 案只驗 R_SUPER 原樣提交 ⇒ `0000`、撤銷 0、新授 0。復原第③腿兩半同取此探針鍵，R_SUPER 半先自證「判定當下（v1, v2）∈ 封死集」。
- **seed 態序列期望**（`casbin_rule_id_seq`＝(163, true)／`sys_casbin_policy_archive_id_seq`＝(1, false)）只作守衛自證前提、不作還原目標（還原值一律 arm 時現讀）。
- **走查還原工具**（`tools/walkthrough-baseline.py`；FR-044、spec Clarifications 2026-10-01 第五題、ADR-00068 決定 4②）：擴面之施工全文（基準檔 v3 之新存欄與其射程、`restore` 寫面次序、`restore --seed` 料源、重啟提示判準、射程界、自測與同批面、落地時序）＝`contracts/code-gates.md` §6（同一事實只住該處、本檔不重列）。

## §12 msg key 名冊（43→46）

| 鍵 | 常數（新建、`error.rs` 之 `pub mod msg_key`） | 碼 | 語意 | 發出點 |
|---|---|---|---|---|
| `biz.role.protectedRevoke` | `BIZ_ROLE_PROTECTED_REVOKE` | `2222` | 撤銷集觸及受保護授權列 | `handler/role.rs` 三維寫端 |
| `biz.role.protectedGrant` | `BIZ_ROLE_PROTECTED_GRANT` | `2222` | 授予集觸及封死集 | `handler/role.rs` 之 updateRoleEndpoints |
| `biz.policy.notRestorable` | `BIZ_POLICY_NOT_RESTORABLE` | `2222` | 復原標的不存在或任一腿拒 | `handler/policy_archive.rs` 之 restorePolicy |

- 各鍵之真 seed app 實發點（`tests/contract.rs` 之 `msg_roster_every_key_has_an_emitter` 雙向閘所需之觀察段）＝`contracts/msg-keys.md` §4 之名冊雙向閘段（同一事實只住該處、本檔不重列）。

- 角色不存在沿用既有 `biz.role.notFound`；13 碼矩陣與 `AppError` 變體零新增；構造點一律 `AppError::Biz(Cow::Borrowed(msg_key::NAME))`（字面只住 `msg_key`；rev5 於構造點直書字面＝翻案不帶回）。
- `MSG_KEYS` 型長 43→46、逐刀只在尾端追加；新鍵 MUST 隨首個發出它的單元落地——名冊、三檔 locale（`en-us`／`zh-cn`／`zh-tw`）之 `backend:` 子樹、`app.d.ts` backend 型節同批（`tools/msg-key-gate.py` 雙向全等；FR-004）。譯文之家＝三檔 locale `backend` 子樹（ADR-00039 決定 2）；鍵之語意要求、譯文出處與落地時序住 `contracts/msg-keys.md`。

## §13 新建件名冊（跨檔定名之單一出處）

| 件 | 落點 | 職責 | rev5 對應 |
|---|---|---|---|
| `policy_endpoints()` | `rust-api/server/src/router.rs` | `ROUTES` 中 `Protection::Policy` 之（路徑, 方法字面）`Vec<(&'static str, &'static str)>`、依註冊序；具名、非 async、具體回型 | `rev5:` `router::policy_route_defs`＋`handler::role::policy_endpoints` |
| `endpoint_methods()` | 同上 | `HttpMethod` 全變體經 `as_str` 導出之 `[&'static str; 3]`（增變體＝型長同改、窮舉 match 測守） | `rev5:` `handler::role::endpoint_methods` |
| `model/facade/sys_casbin_policy.rs` | 新檔 | `casbin_rule` 之主 facade（現況讀、候選輔助、封死集、全量替換、授予 INSERT）；零 `crate::router` 引用（候選與白名單以參數收） | `rev5:` 同名檔 |
| `Dimension { Menu, Button }`（`act()`／`revoke_reason()`）、`RejectCause { ProtectedRevoke, ProtectedGrant }`、`PolicyOutcome<T> { Applied { revoked, granted, effective }, Rejected { cause, blocked } }` | `sys_casbin_policy` | 維度字面與撤銷原因、拒因、三維寫端 outcome（`T`＝選單 id／按鈕碼／（路徑,方法）；非 wire 型） | `rev5:` 同名型 |
| `set_role_menu`／`set_role_buttons`／`set_role_endpoints` | `sys_casbin_policy` | 三維寫端之鎖內本體（收具型交易與已鎖之角色列；端點維另收候選與白名單）：候選→orphan skip→現況→收窄→比對→保護判定→`apply_full_replace`；回 `PolicyOutcome`；不取域鎖、不寫稽核 | `rev5:` 同名入口（rev5 自開交易、取域鎖、寫稽核＝翻案不帶回） |
| `current_menu_ids`／`current_button_codes`／`current_endpoints` | `sys_casbin_policy` | 三支現況讀端之資料面（泛型連線、無鎖；回「現況 ∩ 候選集」各項＋受保護旗標；端點維收候選與白名單） | `rev5:` `current_targets`／`current_endpoints`（rev5 按鈕維與端點維不收窄、選單維經治理域反查） |
| `governed_button_codes` | `sys_casbin_policy` | 治理域按鈕碼聯集（經 `super::sys_menu::list_governed`＋`button_codes_of`；壞形回錯）；getAllButtons 與按鈕維寫讀共用 | `rev5:` `sys_menu::all_button_codes`（跳過壞形＝不帶） |
| `protected_endpoint_set` | `sys_casbin_policy` | 封死集查詢件單點（§4-2） | `rev5:` 同名 |
| 私有 `governed_route_names_by_id`／`scope_live_to_candidates`／`plan_full_replace`／`apply_full_replace` | `sys_casbin_policy` | 映射表（純函式、收 `list_governed` 之列）／三維共用濾點件／比對純函式（`ReplacePlan`／`ReplaceWrites`）／落寫（撤銷經 `archive_revoked_policies` → 授予 INSERT；回（撤銷數, 新授數）） | `rev5:` 同名（映射表 rev5 為 async 自讀） |
| `REASON_MENU_REVOKE`／`REASON_BUTTON_REVOKE`／`REASON_ENDPOINT_REVOKE` | `sys_casbin_archive` | 撤銷原因三常數；`is_non_restorable_reason` 3→5 | `rev5:` 同名 |
| `archive_revoked_policies` | `sys_casbin_archive` | 授權撤銷之移入歸檔（§7-2） | `rev5:` `apply_full_replace` 內之歸檔＋刪除 |
| `ArchiveDimension { Menu, Button, Endpoint }`（`as_str()`／`parse()`）、`dimension_of`、`ArchiveListFilter { role_code, dimension }`、`ArchivedRecord { row, restorable, dimension }`、`list` | `sys_casbin_archive` | 回收桶讀端資料面（泛型連線、1 起算頁碼、雙篩、旗標批次；收端點全集與白名單） | `rev5:` 同名（rev5 收 0 起算頁索引） |
| `RestoreOutcome { Applied { role_id, snapshot }, NoOp, NotRestorable }`、`restore` | `sys_casbin_archive` | 復原鎖內本體（收具型交易、識別、端點全集、白名單、復原者 uid；§5.4 序；`Applied` 帶來源角色 id 與歸檔快照供 handler 寫稽核）；不入域、不寫稽核 | `rev5:` `restore`／`restore_locked`（rev5 自開交易、寫稽核、23505 收窄＝不帶） |
| `active_code_of`／`active_ids_by_codes` | `sys_role` | §1.3 之無鎖讀 | `rev5:` 同名 |
| `BIZ_ROLE_PROTECTED_REVOKE`／`BIZ_ROLE_PROTECTED_GRANT`／`BIZ_POLICY_NOT_RESTORABLE` | `error.rs` | §12 | `rev5:` 構造點字面 |
| 三維讀寫六支＋候選讀兩支之 handler；私有 `record_grant_audit`／`settle_grant_write` | `handler/role.rs` | 授權寫端稽核件（§10）／授予面收場件（取消安全、Applied 即同步；取消時之 log 字面由 tasks 定） | `rev5:` `handler::role` 後段、`finish_grant`（rev5 於請求 future 內直呼 reload＝不帶） |
| `handler/policy_archive.rs`；私有 `record_restore_audit`／`settle_restore_write` | 新檔 | 回收桶兩支 handler／復原稽核件／復原收場件（Applied 同步、NoOp 只 commit） | `rev5:` 同名檔 |

- 寫入件之公開入口一律只收 `&DatabaseTransaction`；新增公開寫入入口者同批於其模組 doc 之具型交易機器守補正面孿生與 compile_fail 一段。wire DTO 之型名住 contracts。
- 落地連動之現在式句（新建件落地即成假述之模組 doc、檔頭數量詞與職責句；涉 `model/facade/sys_menu.rs`／`sys_role.rs`／`sys_casbin_archive.rs`／`facade/mod.rs`、`handler/role.rs` 等）：種子全表、逐處分布與承載單元＝本刀 research「as-built 改寫義務」節（同一事實只住該處、本檔不另列）；同單元改寫、處數一律以 `python3 tools/docsync errata <詞>` 現算。
