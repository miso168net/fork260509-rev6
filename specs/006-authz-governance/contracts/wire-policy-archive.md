# Contract — 授權回收桶兩端點（getArchivedPolicies／restorePolicy）

> 權威序依憲法 §I.3：base-web 實碼 ＞ 官方 docs ＞ mock。授權回收桶頁為本刀新增之獨立管理頁（seed 選單列 10 `manage_policy-archive`、component `view.manage_policy-archive`、頁級門＝其選單維受保護授權列 72〔R_SUPER〕）；契約以 `rev5:006` 之 `contracts/wire-policy-archive.md` 與其 as-built（`rev5:server/src/handler/policy_archive.rs`、`rev5:server/src/model/facade/sys_casbin_archive.rs` 之 `list`／`restore`、`rev5:src/typings/api/rev5-role-admin.d.ts` 之 `Api.PolicyArchive` 段）為藍本、依 rev6 拍板改寫（差異逐欄見文末「與 rev5 wire 逐欄比對」、理由住本刀 research「rev6 差異點」），由本檔凍結（spec 目錄＝定點快照；wire 活體權威＝碼＋`tests/contract.rs`＋wire-schema 快照）。
> 信封、錯誤碼總則同 `wire-authz-governance.md` 檔頭（業務錯誤 HTTP 200、例外恰二 `4040`→404／`5003`→403；未登入 `8888`；寫端先取操作者上下文、缺席＝`5000`；資料庫錯＝`5000`；授權中介層不讀 body；判定面同步結果不影響回應）。兩條皆 `Protection::Policy`、路徑×動詞逐字對齊 001 刀凍結 seed 之政策列 70（getArchivedPolicies GET）／71（restorePolicy POST），皆只授 R_SUPER、`protected=TRUE`（兩列與頁級之選單維受保護授權列〔授權列 72〕皆受保護＝撤不掉、自救路徑恆可走；FR-032）。
> 後端 handler 住新建 `rust-api/server/src/handler/policy_archive.rs`（新域：自有 target `security.policy_archive`、`BODY_FALLBACK_MSG`、`operator_from`、`db_failure`；`handler/mod.rs` 新增模組宣告）；鎖內重驗與寫入住擴充之 `rust-api/server/src/model/facade/sys_casbin_archive.rs`（ADR-00065 決定 3）。型別＝新建 `base-web/src/typings/api/rev6-authz.d.ts` 之 `Api.Authz`（與三維授權共用命名空間）；wrapper＝新建 `base-web/src/service/api/rev6-authz.ts`（十支 fetcher 中本檔兩支；不入 barrel、錯誤不加工）。

## 端點總表

| # | 端點 | seed 列 | 入選單序列化域 | case_key（新建） | handler（新建） | fetcher（新建） | 前端消費者 |
|---|---|---|---|---|---|---|---|
| 1 | `GET /systemManage/getArchivedPolicies` | 70 | —（讀端） | `get-archived-policies` | `handler::policy_archive::get_archived_policies` | `fetchGetArchivedPolicies(params?)` | 回收桶頁（新檔 `views/manage/policy-archive/index.vue`）＋搜尋模組（新檔 `modules/policy-archive-search.vue`） |
| 2 | `POST /systemManage/restorePolicy` | 71 | 否 | `restore-policy` | `handler::policy_archive::restore_policy` | `fetchRestorePolicy(id)` | 回收桶頁之操作欄 |

ROUTES 表尾相對次序與總計數見 `wire-authz-governance.md` 端點總表。seed 之授權歸檔表零列（`m0002_baseline_seeds.rs` 對 `sys_casbin_policy_archive` 之 `grep -c`＝0）：歸檔列只由本刀之授權撤銷與 005 刀既有之連動歸檔（刪角色、刪選單、按鈕碼絕版）產生。

## 共用型（rust DTO 與 `Api.Authz.<型>` 同名；宣告序＝wire 欄序；camelCase）

定名規則＝`wire-authz-governance.md`「共用型」節之定名規則句（本檔不另立規則；套其清單 query 例外之結果：rev5 後端 `ArchivedPolicyQuery`、typings `ArchivedPolicyListQuery`，rev6 兩側皆 `ArchivedPolicyListQuery`）。下列全為新建件（量法＝`git -C rust-api grep -n <型名> -- server`／`git -C base-web grep -n <型名> -- src` 於 pin 樹零命中）；本檔為回收桶 wire DTO 型名之家（data-model §13「新建件名冊」指回 contracts；data-model §9「wire 映射規則」只載映射規則、不列型名）。

### `ArchivedPolicyDimension`＝`'menu' | 'button' | 'endpoint'`

typings 側之三值字面聯集（後端 `dimension` 欄為 `&'static str`）。於快照自成一支 definition（`Api.IpRule.RuleType` 同形先例）、入受審讀端冊並配正反例（三值以外、大小寫變體、非字串＝反例；側別判準與「封閉字面聯集型」之裁判形＝`contracts/code-gates.md` §4）。

### `ArchivedPolicy`（`records` 元素；恰 14 欄）

| # | 欄 | 型 | 來源與說明 | 頁面消費 |
|---|---|---|---|---|
| 1 | `id` | number | 歸檔列 id（restorePolicy 請求鍵；`serialize_i64_number_guarded`） | 列鍵、復原請求鍵 |
| 2 | `ptype` | string | 快照原樣（恆 `'p'`） | — |
| 3 | `v0` | string | 來源角色代碼 | 「來源角色」欄 |
| 4 | `v1` | string | 授權標的（路由名／按鈕碼／路徑） | 「標的」欄 |
| 5 | `v2` | string | 維度標記（`menu`／`button`）或 HTTP 方法 | — |
| 6～8 | `v3`／`v4`／`v5` | string | 快照原樣（空字串即空字串） | — |
| 9 | `archiveReason` | string | 六值封閉詞彙原字面（`role_soft_delete`／`menu_soft_delete`／`menu_button_removed`／`menu_revoke`／`button_revoke`／`endpoint_revoke`）；不映譯 | 「歸檔原因」欄（純文字插值） |
| 10 | `archivedAt` | string | RFC3339、偏移恆 `+00:00`（ADR-00061） | 「歸檔時間」欄（原樣顯示） |
| 11 | `archivedBy` | string \| null | 歸檔者**帳號名**（不是 uid；批次回填、查無或 `archived_by` 為 NULL→null） | 「歸檔者」欄（null 留白） |
| 12 | `roleId` | number \| null | 歸檔之來源角色 id（`serialize_opt_i64_number_guarded`；NULL＝顯式 null、鍵在場） | — |
| 13 | `restorable` | boolean | 後端派生之可復原旗標（見 §1） | 操作欄：true＝復原鈕（二次確認）、false＝同文案停用鈕 |
| 14 | `dimension` | `ArchivedPolicyDimension` | 由 `v2` 推導：`menu`→`'menu'`、`button`→`'button'`、其餘一律 `'endpoint'`（不新增維度欄） | 「維度」欄（譯為維度標籤） |

★判定：14 欄全上 wire（rev5 契約形逐欄同）。頁面 8 欄（序號／來源角色／維度／標的／歸檔原因／歸檔時間／歸檔者／操作；FR-036）只消費 `id`、`v0`、`v1`、`archiveReason`、`archivedAt`、`archivedBy`、`restorable`、`dimension`；其餘 6 欄（`ptype`、`v2`～`v5`、`roleId`）無頁面消費者仍上 wire，判準：
- wire 與 rev5 逐欄同形 ⇒ 不新增刻意分岔列、CDP 對照不需排除回收桶列形；
- `v2`＝端點維之方法：頁面不顯方法欄之前提「同路徑多方法 0」（FR-036）是 seed 量測而非結構保證，出現同路徑多方法時 `v2` 是唯一可區分欄；
- `roleId`＝可復原旗標②半之誠實退化面（NULL→`restorable=false`）於 wire 之忠實形（rev5 之 wire-schema 裁判以之為重點欄）；
- `ptype`／`v3`～`v5`＝完整快照之原樣過境（撤銷＝移入歸檔之完整快照語意；FR-012）。
不上 wire：`created_at`／`created_by`（被歸檔列之原治理欄快照）——rev5 亦不上（逐欄白名單；FR-005）。

### `ArchivedPolicyListQuery`＝`CommonType.RecordNullable<Common.CommonSearchParams & { roleCode: string; dimension: ArchivedPolicyDimension }>`

四欄皆可空：`current`／`size`／`roleCode`／`dimension`（語意見 §1）。後端 `dimension` 以**字串**承接（`Option<String>`）：前端清空之篩選欄送空字串時不致整串收斂（005 刀 `RoleListQuery` 之 `status` 同理）。

### `RestorePolicyReq`＝`{ id: number }`

歸檔列 id。後端 `#[derive(Default, Deserialize)]`＋`#[serde(default, rename_all = "camelCase")]`；body 取用經 `handler::common::json_or_default(req, state, "restorePolicy", BODY_FALLBACK_MSG)`（餵本域新建常數）——缺席或壞形＝`id=0`。前端以具名型組 body（`const data: Api.Authz.RestorePolicyReq = { id };`，005 刀 `fetchRestoreMenu` 同形）。

回應信封：`getArchivedPolicies` 回 `Api.Common.PaginatingQueryRecord<Api.Authz.ArchivedPolicy>`（wrapper 內直接實例化既有泛型、不另立清單回應別名＝005 刀形；後端 `envelope::PageRes<ArchivedPolicy>`）；`restorePolicy` 回 `null`。受審：上列四型入受審名冊（側別＝`contracts/code-gates.md` §4 逐型側別表：`ArchivedPolicy`／`ArchivedPolicyDimension` 讀端冊、`ArchivedPolicyListQuery`／`RestorePolicyReq` 請求端冊）、各配正向＋反例（`archivedBy` 為 number、`roleId` 鍵缺席、`restorable` 非布林、`dimension` 值域外、snake_case 鍵＝重點反例；FR-052；名冊與節謂詞＝`contracts/code-gates.md`）。

## 1. `GET /systemManage/getArchivedPolicies`（seed 70）

Query `ArchivedPolicyListQuery`（全部可空）：
- `current`／`size`：既有 `envelope::page_params`（005 刀分頁通則：缺席→1／10；`current` clamp [1, `PAGE_MAX_CURRENT`＝10^7]、`size` clamp [1, `PAGE_MAX_SIZE`＝100]；顯式 0 取下界；逾界回空頁且回應 `current`＝clamp 後值）。MUST NOT 用 `envelope::page_or_all`（全取例外恰限選單治理清單）。
- `roleCode`：等值濾 `v0`（文字等值、不分子字串）；空字串＝不篩選（`handler::common::blank_to_none`）；可查已刪或停用角色之代碼（故頁面以文字欄、不用只列活性且啟用角色之下拉）。
- `dimension`：恰 `'menu'`→`v2='menu'`、`'button'`→`v2='button'`、`'endpoint'`→`v2 ∈` HTTP 方法白名單（新建 `router::endpoint_methods()`）；其餘一律靜默不濾（含空字串、大小寫變體、未知值）。
- 不收原因值篩選（Q17）、不收排序參數（ADR-00058 決定 1）。
- 查詢串壞形（`current=abc`、同名鍵重複）＝整串收斂為預設（第 1 頁、10 筆、無篩選）：抽取器結構性無 reject 面（`FromRequestParts`、`Rejection = Infallible`），不放行框架 400 裸回應（serde 對查詢串整串判成敗：一個壞參數會讓同串之合法篩選一起落預設）。
- 前端首屏 query 物件 `{ current: 1, size: 10, roleCode: null, dimension: null }`（rev5 形）之 null 篩選欄經 qs 渲染形同 005 刀 `wire-role-admin.md` §1 所記；兩欄皆字串承接、空字串＝不篩選 ⇒ 分頁參數不受影響。

200：`data: PageRes<ArchivedPolicy>`＝`{ current, size, total, records }`；`total`＝篩選後總數；伺服端固定穩定序＝`archived_at DESC, id DESC`（ADR-00058 決定 2；同刻者以 id 降冪決勝）。
- **可復原旗標**（每列；FR-027、ADR-00065 決定 8）：`restorable`＝①`archive_reason` 不屬不可復原集（既有 `sys_casbin_archive::is_non_restorable_reason`，本刀 3→5）∧ ②`role_id` 非 NULL 且等於代碼 `v0` 之現役活角色 id（活性不含狀態）∧ ③¬（`v0` ≠ `sys_role::SUPER_ROLE_CODE` ∧（`v1`, `v2`）∈ 封死集）∧ ④（`v1`, `v2`）∈ 新建 `router::policy_endpoints()` 之端點全集；⑤停用不擋、免算；①不過即短路 ⇒ 選單維與按鈕維之列恆 false。批次求值、不逐列查：②半以新建 `sys_role::active_ids_by_codes` 一次取頁內通過①之列的活角色 id（空集不查）、③半以新建 `sys_casbin_policy::protected_endpoint_set` 一次取（頁內無通過①之列即零查詢）、④半之端點全集與白名單由 handler 以參數傳入 facade（facade 零 `crate::router` 引用）。旗標為列表時點之派生值、非權威；權威恆為 restorePolicy 之鎖內重驗；前端 MUST NOT 自行推斷。
- **`archivedBy`**：整頁 `archived_by` 去重後一次批次讀既有 `sys_user::find_names_by_ids`（空集不查；不濾軟刪之使用者；查無→null）；包裝件之落點（本域自持一份或提升進 `handler/common.rs`）依該檔之收攏與重評紀律於 research 判定。
- 零鎖、零交易、零稽核、零判定面同步（ADR-00067 決定 3）。
- 錯誤集只有授權（`5003`／`8888`）與內部（`5000`；經本域 `db_failure`）兩腿、零業務錯誤腿（值域外之篩選一律沉默）。

前端：回收桶頁表格 8 欄、`remote` 分頁、列鍵＝`id`；搜尋模組＝來源角色代碼（文字）×維度（下拉、可清空；重置即刷新）；表頭只一顆重新整理鈕（不掛 `TableHeaderOperation`＝rev5 形、CDP 對照結構同形）；`restorable=false` 之列渲染同文案停用鈕、不包二次確認；復原無按鈕碼 gating（門＝頁級選單維受保護授權列＋列級旗標）。

## 2. `POST /systemManage/restorePolicy`（seed 71；不進選單域）

Req `RestorePolicyReq`：`{ id: number }`（歸檔列 id）。

處理序之 wire 可觀察面（★逐步全文與鎖序＝data-model §5.4、腿表＝ADR-00065 決定 3，本檔不重列動作序；序號沿 ADR-00065：鎖歸檔列＝第 0 步、重驗腿＝①～⑤；不入選單序列化域＝可復原列只剩端點維、FR-031）：
- 操作者上下文缺席 ⇒ `5000` 拒寫（先於一切守門；FR-006）。
- 下列任一成立 ⇒ `2222 biz.policy.notRestorable`（同鍵、不揭露哪一腿 ⇒ 腿序對 wire 不可區分；各腿判準以 ADR-00065 決定 3 腿表為準）：
  - 第 0 步鎖歸檔列（`FOR UPDATE`；歸檔列鎖讀為新建件）查無：識別不存在、已被消費、body 收斂之 `id=0`。
  - ①原因屬不可復原集（`is_non_restorable_reason`；選單維與按鈕維之列恆止於此、不取角色列鎖）。
  - ②同實例不成立：歸檔 `role_id` 為 NULL（不鎖、誠實退化）；以之經既有 `sys_role::find_active_by_id_for_update` 鎖讀（未軟刪、停用照鎖）查無（含等鎖期間被刪）；或鎖得角色之代碼 ≠ 歸檔 `v0`（與 rev5 以代碼鎖讀＋比 id 逐形等價＝ADR-00065 決定 4）。
  - ③結構性封死：標的角色代碼 ≠ `sys_role::SUPER_ROLE_CODE` 且（`v1`, `v2`）∈ 封死集（新建 `sys_casbin_policy::protected_endpoint_set` 鎖內現查；ADR-00064 決定 1／決定 2）。
  - ④（`v1`, `v2`）∉ 新建 `router::policy_endpoints()` 之端點全集（免幽靈政策）。
- ⑤停用不擋：標的角色停用不擋（無判定；停用≠撤銷）。
- 以上全過 ⇒ 七欄身分鍵（`ptype`、`v0`～`v5`＝授權表唯一索引 `unique_key_sea_orm_adapter` 之欄集）已在現役＝**NoOp**；否則＝**Applied**；收場 task：commit →（限 Applied）判定面同步 → 回應。

三態（FR-030；ADR-00065 決定 5～7）：

| outcome | 寫入（同一交易） | 稽核 | 判定面同步 | 回應 |
|---|---|---|---|---|
| Applied | INSERT 授權列（新 id；`ptype`、`v0`～`v5` 自歸檔快照過境；`protected` **顯式 FALSE**；`created_by`＝復原者 uid；`created_at` 由 DB default）＋刪歸檔列 | 恰一列 `restore` | commit 後一次 | `0000`、`data: null` |
| NoOp（標的已在現役） | 只刪歸檔列（消費）；授權表零寫 | 零 | 不觸發 | `0000`、`data: null` |
| NotRestorable（第 0 步查無或①～④任一腿拒） | 零寫（rollback；歸檔列保留、留作稽核） | 零 | 不觸發 | `2222`＋`biz.policy.notRestorable`、`data: null` |

- 拒因一律同鍵、純 key、不揭露哪一腿（FR-004、ADR-00065 決定 7）；後端為最終防線、不依賴前端停用復原鈕。
- ★Applied 與 NoOp 對前端不可區分；NoOp 使回收桶移除一列而稽核表無痕跡（兩者皆已知態＝ADR-00068 款 12；spec Clarifications 首題）。同一（角色,端點）多次撤銷之多列歸檔：復原其一後，其餘之復原皆 NoOp。可復原旗標不加「是否已在現役」腿（Q16）。
- 寫入 MUST 經 facade 直接 INSERT，MUST NOT 經判定引擎管理 API（島 G1）或轉接器之新增政策路徑（LL-00035）；授權回收桶之選單維與按鈕維分支結構性不可達（不可復原集 3→5＝ADR-00065 決定 1／決定 2）。
- 稽核（Applied 恰一列；同交易）：`AuditOperation::Restore`（字面 `restore`）、`entity_table`＝`"sys_role"`、`entity_id`＝標的角色 id、`before`＝無、`after`＝`{archive_id, dimension, target, act}`（`dimension`＝由 `v2` 推導之三值、`target`＝`v1`、`act`＝`v2`）；鍵名與值形定稿＝data-model §10「操作稽核列」。
- 判定面同步（ADR-00067 決定 1／決定 4）：觸發門＝Applied；收場沿 005 刀取消安全形（commit 與其後同步交脫離請求生命週期之 task、回應前 await；NoOp 亦於 task 內 commit、不同步）⇒ 回應於同步結束後送出；收場 task 被取消＝`5000`（告警形同既有 `handler/role.rs` 之 `settle_domain_write` 取消分支、字面由 tasks 定）。Applied 之 API 判定於換上後即時生效；來源角色停用者至重新啟用前仍 `5003`（停用即斷權不經判定面；ADR-00068 款 16）。
- **不另設 23505 收窄**（ADR-00065 決定 10）：同一 `v0` 之授權表 INSERT 寫者（三維寫端之授予、本端點）皆持該角色列鎖、NoOp 判定在鎖內 ⇒「NoOp 判定後、INSERT 前他交易 commit 同鍵」於生產路徑結構不可達；任何資料庫錯（含序列失步撞主鍵）一律經本域 `db_failure` 回 `5000`、根因落 log。
- 自救路徑（Q14、FR-032）：R_SUPER 撤掉自身非受保護端點列（例 getRoleList）致角色頁失能時，本頁之選單維受保護授權列（授權列 72；側欄項＝選單列 10）與本檔兩支端點（授權列 70／71）皆受保護而撤不掉 ⇒ 經本端點復原該列即恢復；選單維與按鈕維被撤者於角色頁恢復後重勾。

body 缺席或壞形 ⇒ `id=0` ⇒ 第 0 步查無 ⇒ `2222 biz.policy.notRestorable`（FR-007；不為此新增錯誤碼）。
200：`data: null`（Applied／NoOp）；`2222 biz.policy.notRestorable`；`5000`（上下文缺席、資料庫錯、收場被取消）。

前端：操作欄「復原」鈕（二次確認）→ `fetchRestorePolicy(row.id)` → 成功 toast 後重取列表、留在當頁；失敗由共用攔截層出純 key toast（譯文之家＝三檔 locale `backend` 子樹；出處＝`contracts/msg-keys.md` 檔頭）。

## 授權態矩陣（contract 測）

Super 兩支皆通（restorePolicy 以合成 fixture 打出 Applied＝rev5 形；空 body＝`2222 biz.policy.notRestorable`）；Admin／User 兩支皆 `5003`；未登入 `8888`。contract case 集、覆蓋閘與名冊擴列＝`contracts/code-gates.md`；`biz.policy.notRestorable` 之真 seed 實發點＝`contracts/msg-keys.md`。

## 與 rev5 wire 逐欄比對

| 面 | rev5（HEAD） | rev6 本刀 | wire 差 |
|---|---|---|---|
| 命名空間與檔 | `Api.PolicyArchive`（追加於 `rev5-role-admin.d.ts`）；fetcher 追加於 `rev5-role-admin.ts` | `Api.Authz`（新建 `rev6-authz.d.ts`）；fetcher 新建 `rev6-authz.ts` | 零（型名前綴差） |
| `ArchivedPolicy` 14 欄（名、型、序） | `id`、`ptype`、`v0`～`v5`、`archiveReason`、`archivedAt`、`archivedBy`、`roleId`、`restorable`、`dimension` | 同 | 零 |
| `archivedAt` | `to_rfc3339()` | 同；偏移恆 `+00:00` 由 ADR-00061 明文 | 零 |
| `archivedBy` 回填 | 共用件 `resolve_operator_names`（`rev5:B-106` 批次） | 既有 `sys_user::find_names_by_ids` 批次讀（包裝落點見 research） | 零 |
| `restorable` | ①～④ 批次、②半＝`sys_role::active_ids_by_codes` | 同判準；②半之讀端新建（rev5 同名件） | 零 |
| `ArchivedPolicyDimension` | 三值、`parse` 區分大小寫、未知值不濾 | 同 | 零 |
| 清單 query 型名 | 後端 `ArchivedPolicyQuery`／typings `ArchivedPolicyListQuery` | 兩側 `ArchivedPolicyListQuery` | 零 |
| 分頁 | 就地 `unwrap_or(1).clamp(1, MAX_CURRENT)`／`unwrap_or(10).clamp(1, 100)`、facade 收 0 起算 | `envelope::page_params`（同值界）、facade 收 1 起算 | 零 |
| 清單回應型 | typings 另立別名 `ArchivedPolicyListRes`（快照一支 definition） | 不立別名、wrapper 直接實例化 `Api.Common.PaginatingQueryRecord<…>`（005 刀形） | 零（快照少一支 definition） |
| 復原請求型 | 後端 `RestorePolicyReq`；typings 無具名型（fetcher 內聯 `{ id }`） | 兩側 `RestorePolicyReq`（005 刀 `MenuIdReq` 形） | 零 |
| 鎖角色列 | 以 `v0` 代碼鎖讀活角色列（`find_active_by_code_for_update`）再比 `role_id` | 以歸檔 `role_id` 鎖讀（既有 `find_active_by_id_for_update`）再比代碼 | 零（逐形等價＝ADR-00065 決定 4） |
| NotRestorable 射程 | 識別不存在、任一腿拒、回灌撞 `unique_key_sea_orm_adapter`（23505 收窄） | 識別不存在、任一腿拒；不設 23505 收窄 | 只在結構不可達之競態有差（rev5 `2222`、rev6 `5000`） |
| 交易與收場 | facade 自開交易、自寫稽核；handler 於請求 future 內 commit 後 reload | handler 持交易、稽核同交易；commit 與同步交脫離請求之 task | 零（僅收場被取消時回 `5000`） |
| 拒因構造 | 字面 `Cow::Borrowed("biz.policy.notRestorable")` | `error.rs` 之 `msg_key::` 常數、入 `MSG_KEYS` | 零 |
| 操作者缺席 | `5000`；log 借 `security.ipgate`＋`degraded` 欄 | `5000`；log 掛 `security.policy_archive`＋`refused` 欄、零 degraded | 零（log 差） |
| body 收斂之端點標籤 | `policy.restore`（三參數 `json_or_default`） | `restorePolicy`（四參數、餵本域常數） | 零（log 差） |
| 稽核列 | `Restore`、`sys_role`、角色 id、`payload_after` 四鍵 | 同（欄名 rev6 `after`） | 非 wire |

## 拒寫事件與觀測

- 新域字面（新建；全數 MUST 與既有各域不同字）：
  - 操作者上下文缺席之拒寫事件＝本域私有 `operator_from`：`tracing::error!(target: "security.policy_archive", refused = "request_context_absent", endpoint, uid, <本域訊息>)`；MUST NOT 帶 degraded 欄、MUST NOT 增計任何降級序列；取得 MUST 經 `handler::common::operator_from_context`（共用核心）＋本域拒寫腿。
  - body 收斂 debug 事件之訊息＝本域常數 `BODY_FALLBACK_MSG`（行首 `const BODY_FALLBACK_MSG: &str = ` 定義形）；清單 query 壞形收斂另落一則 debug（形同 role.rs 之清單 query 抽取器）。
  - 資料庫故障＝本域 `db_failure(endpoint, step)`：落 `target: "security.policy_archive"` 之 error 後翻 `5000`。
  - 本域訊息文字與 `BODY_FALLBACK_MSG` 之字面由 tasks 定。
- 名冊同批入冊（漏列之後果與自證案＝`contracts/code-gates.md`）：`handler/common.rs` 之 `each_domain_keeps_its_own_log_literals` 逐域元組表加本域；`handler/ip_rule.rs` 之 `production_code_emits_no_degraded_field` 檔清單加 `policy_archive.rs`；`tests/authz_entrypoint_lint.rs` 之 `RELOAD_CALL_FILES` 加 `handler/policy_archive.rs`（restorePolicy 之同步接線同一 commit；ADR-00067 決定 5）；`DOMAIN_LOCK_CALL_FILES` 不加（本域不入域）。
- 判定面同步：`casbin_reload_total{outcome}` 值集與告警 `obs016-casbin-reload-anomaly` 照舊（ADR-00067 決定 8）；restorePolicy Applied 亦計入 `ok` 之來源。剛復原之端點仍回 `5003` 之排障錨＝RUNBOOK §13（ADR-00067 決定 9）。
