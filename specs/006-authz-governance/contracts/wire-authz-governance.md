# Contract — 授權治理八端點（三維讀寫 6＋候選讀 2）

> 權威序依憲法 §I.3：base-web 實碼 ＞ 官方 docs ＞ mock。三顆授權彈窗為 upstream demo 面（選單彈窗真樹假勾選、按鈕彈窗全假資料、無端點彈窗），其所需之讀寫端點即本刀補齊面；契約以 `rev5:006` 之 `contracts/wire-authz-governance.md` 與其 as-built（`rev5:server/src/handler/role.rs` 三維段、`rev5:src/typings/api/rev5-role-admin.d.ts` 之 `rev5:006` 追加段）為藍本、依 rev6 拍板改寫（差異逐欄見文末「與 rev5 wire 逐欄比對」、理由住本刀 research「rev6 差異點」），由本檔凍結（spec 目錄＝定點快照；wire 活體權威＝碼＋`tests/contract.rs`＋wire-schema 快照）。
> 信封、錯誤碼總則同 005 刀 `contracts/wire-role-admin.md` 檔頭：信封一律 `{data, code, msg}`、業務錯誤 HTTP 200（例外恰二：`4040`→404、`5003`→403）；未登入＝既有 `8888`；無授權＝`5003`；寫端一律先取操作者上下文（缺席＝`5000` 拒寫、不落稽核列，先於一切守門）；其餘資料庫錯＝`5000`；授權中介層不讀 body；判定面同步結果不影響回應（commit 成功即回成功；同步失敗只告警與計數）。拒因一律純 i18n key、一因一鍵、`data` 為 null、不攜被擋項明細（FR-004；ADR-00064 決定 3）。
> 八條皆 `Protection::Policy`、路徑×動詞逐字對齊 001 刀凍結 seed 之政策列（皆只授 R_SUPER、`protected=TRUE`；量法：`rust-api/migration/src/m0002_baseline_seeds.rs` 之 `SEED_CASBIN_RULE` 逐路徑 `grep -c` 各恰 1 列）。後端 handler 住既有 `rust-api/server/src/handler/role.rs`（八支皆新建 `pub async fn`；共用該檔之域字面 target `security.role`、`BODY_FALLBACK_MSG`、私有 `operator_from`／`db_failure`）。
> 型別檔＝新建 `base-web/src/typings/api/rev6-authz.d.ts` 之 `Api.Authz`（與授權回收桶兩支共用同一命名空間＝FR-038 單數；回收桶型見 `wire-policy-archive.md`）；wrapper＝新建 `base-web/src/service/api/rev6-authz.ts`（十支 fetcher 中本檔八支；不入 barrel、錯誤不加工——業務拒與 HTTP 層拒之提示由 `service/request` 之 onError 鏈統一出 toast，呼叫端只判 `error` 有無，形同 005 刀 `rev6-role-admin.ts` 檔頭）。

## 端點總表

| # | 端點 | seed 列 | 入選單序列化域 | case_key（新建） | handler（新建） | fetcher（新建） | 前端消費者 |
|---|---|---|---|---|---|---|---|
| 1 | `GET /systemManage/getRoleMenu` | 32 | —（讀端） | `get-role-menu` | `handler::role::get_role_menu` | `fetchGetRoleMenu(id)` | 選單權限彈窗 |
| 2 | `POST /systemManage/updateRoleMenu` | 33 | 是 | `update-role-menu` | `handler::role::update_role_menu` | `fetchUpdateRoleMenu(data)` | 選單權限彈窗 |
| 3 | `GET /systemManage/getRoleButton` | 53 | —（讀端） | `get-role-button` | `handler::role::get_role_button` | `fetchGetRoleButton(id)` | 按鈕權限彈窗 |
| 4 | `POST /systemManage/updateRoleButton` | 54 | 是 | `update-role-button` | `handler::role::update_role_button` | `fetchUpdateRoleButton(data)` | 按鈕權限彈窗 |
| 5 | `GET /systemManage/getRoleEndpoints` | 56 | —（讀端） | `get-role-endpoints` | `handler::role::get_role_endpoints` | `fetchGetRoleEndpoints(id)` | 端點權限彈窗（新檔） |
| 6 | `POST /systemManage/updateRoleEndpoints` | 57 | 否 | `update-role-endpoints` | `handler::role::update_role_endpoints` | `fetchUpdateRoleEndpoints(data)` | 端點權限彈窗（新檔） |
| 7 | `GET /systemManage/getAllButtons` | 52 | —（讀端） | `get-all-buttons` | `handler::role::get_all_buttons` | `fetchGetAllButtons()` | 按鈕權限彈窗 |
| 8 | `GET /systemManage/getAllEndpoints` | 55 | —（讀端） | `get-all-endpoints` | `handler::role::get_all_endpoints` | `fetchGetAllEndpoints()` | 端點權限彈窗（新檔） |

- 動詞分布（含回收桶兩支之十條）＝GET 6／POST 4；ROUTES 39→49、政策保護 25→35（現況量法：`rust-api/server/src/router.rs` 之 ROUTES 區塊逐條解析 `protection`＝Policy 25〔GET 9／POST 11／DELETE 5〕、Public 11、Authed 3）。
- 十條接在 ROUTES 表尾、相對次序依 `rev5:server/src/router.rs` 表序（get-role-menu、update-role-menu、get-role-button、update-role-button、get-role-endpoints、update-role-endpoints、get-archived-policies、restore-policy、get-all-buttons、get-all-endpoints；rev5 夾於其間之 get-all-pages 為 rev6 既有、不重列）。
- 讀端（1／3／5／7／8）零鎖、零交易、零稽核、零判定面同步（ADR-00067 決定 3）。getAllPages 屬 005 刀交付（`handler::menu::get_all_pages`、`wire-menu-admin.md` §3），不在本檔。

## 共用型（rust DTO 與 `Api.Authz.<型>` 同名；宣告序＝wire 欄序；camelCase）

定名規則（兩支 wire 契約共用、只住本句；`wire-policy-archive.md` 引之）：型名＝後端 DTO 名＝rev5 後端 DTO 名（rev5 typings 名與之不同者以後端名為準——005 刀 `RoleHomeUpdateReq` 先例）；例外恰一：清單 query 型名取 rev6 `<實體>ListQuery` 慣例、優先於 rev5 後端名（rev6 既有 `IpRuleListQuery`／`MenuListQuery`／`RoleListQuery` 兩側同名；本刀適用者＝回收桶清單 query）；rev5 之泛型寫端回應 `GrantResult<T>` 改三支具體型、名取 rev5 typings 之三具體別名。兩側皆不新宣告泛型（`rust-api/server/tests/wire_i64_guard_lint.rs` 之 `GENERIC_WIRE_TYPES` 名冊不變；typings 側避免抽取器泛型佔位名位移）。下表全為新建件（pin 樹生產面零同名件：`git -C rust-api grep` 與 `git -C base-web grep` 之同名命中只見 `rust-api/server/src/handler/system_settings.rs` 測試模組之私有 `enum Endpoint` 與 `rust-api/server/tests/wire_i64_guard_lint.rs` 之 lint 合成樣本字串 `pub struct MenuId(pub i64);`，皆不與本刀新建件衝突）；本檔為三維與候選之 wire DTO 型名之家（data-model §13「新建件名冊」指回 contracts；data-model §9「wire 映射規則」只載映射規則、不列型名）。

| 型 | wire 形 | 方向 | 說明 |
|---|---|---|---|
| `Endpoint` | `{ path: string, method: string }` | 讀（受審讀端冊；兼作 `UpdateRoleEndpointsReq.endpoints` 之元素、請求面由該型承載） | 端點維雙鍵＝政策鍵（v1, v2）；getAllEndpoints 回應項＝updateRoleEndpoints 期望項、同形共用；`method`＝HTTP 動詞大寫字面 |
| `RoleMenuItem` | `{ id: number, protected: boolean }` | 讀 | `id`＝選單 id（治理域反向映射自路由名；2^53 守衛） |
| `RoleButtonItem` | `{ code: string, protected: boolean }` | 讀 | `code`＝按鈕碼 |
| `RoleEndpointItem` | `{ path: string, method: string, protected: boolean }` | 讀 | `Endpoint` 雙鍵＋`protected` |
| `RoleMenuGrantRes` | `{ revoked: number, granted: number, effective: number[] }` | 讀（寫端回應） | `effective` 元素＝選單 id |
| `RoleButtonGrantRes` | `{ revoked: number, granted: number, effective: string[] }` | 讀（寫端回應） | `effective` 元素＝按鈕碼 |
| `RoleEndpointGrantRes` | `{ revoked: number, granted: number, effective: Endpoint[] }` | 讀（寫端回應） | `effective` 元素＝`Endpoint` |
| `UpdateRoleMenuReq` | `{ id: number, menuIds: number[] }` | 請求（body） | 期望全集＝選單 id 陣列 |
| `UpdateRoleButtonReq` | `{ id: number, buttons: string[] }` | 請求（body） | 期望全集＝按鈕碼陣列 |
| `UpdateRoleEndpointsReq` | `{ id: number, endpoints: Endpoint[] }` | 請求（body） | 期望全集＝（路徑,方法）陣列 |
| `RoleIdQuery` | `{ id: number }` | 請求（query；受審請求端冊、`RoleHomeQuery` 同側） | 三支現況讀端共用之 `?id=` |

rust 專屬元素型（非 wire definition：typings 側無對應型、快照不成 definition；新建件）：

| 型 | 落點 | wire 形 | 說明 |
|---|---|---|---|
| `MenuId` | `rust-api/server/src/handler/role.rs`（與三維 DTO 同檔） | 裸 JSON number（newtype 序列化透明） | `RoleMenuGrantRes.effective` 之元素型；tuple 欄掛 `crate::envelope::serialize_i64_number_guarded`；定名沿 rev5 同名件（判準＝藍本保真；與 005 刀既有 `MenuIdReq` 不同名） |

- **`protected`**（三支讀端項）＝該授權列之受保護旗標（`casbin_rule.protected`；後端單一真源、前端 MUST NOT 以 seed 靜態集自行判定；FR-005）；前端據以鎖定節點、撤銷集觸及即整批拒（後端最終防線）。
- **寫端回應三型**：`revoked`／`granted`＝本次實際撤銷列數／新授列數（候選內計；空 diff 皆 0、仍屬 Applied；rust 沿 rev5 取 `usize`）；`effective`＝生效集合（定義見下節「生效集合」）、恆陣列（空亦 `[]`、不省略）。
- **`effective` 之選單 id 守衛**：選單維之 `effective` 元素 MUST 經 2^53 守衛——後端以新建 newtype `MenuId`（上表；tuple 欄掛 `crate::envelope::serialize_i64_number_guarded`、wire 為裸 JSON number）承載集合元素，MUST NOT 以 `Vec<i64>` 直出（觸 `tests/wire_i64_guard_lint.rs` 之絆線 `nested_generic_i64_fields_are_out_of_scope`；同一批 id 於 getRoleMenu 有守衛、於寫端回應卻失真＝§I.3 fail-loud 面單向失效）。★此 newtype 進場即使該檔檔頭「rev6 真樹現況零此類欄、未立 newtype」句之後半成假述，同單元改寫（RL-0011）。
- **請求三型**：後端 `#[derive(Default, Deserialize)]`＋`#[serde(default, rename_all = "camelCase")]`；body 取用經 `handler::common::json_or_default(req, state, <端點名>, BODY_FALLBACK_MSG)`（四參數、餵 role.rs 既有本域常數）——body 缺席、壞 JSON、任一欄型別不符（例 `menuIds: ["a"]`、`endpoints` 元素缺 `method`）、★期望集鍵缺席或拼錯（例 `{"id":5}`、`{"id":5,"menuId":[1]}`；期望集欄以可缺席型承接、缺席即收斂；spec Clarifications 第七題、對 rev5「缺鍵＝空集＝全撤」之刻意分岔）＝**整包**收斂為預設形（`id=0`＋空集），不作部分採用。前端送出形之欄齊備（`id` 與期望集皆必送）由 wire-schema 快照裁判、與後端寬鬆承載是兩件事（005 刀同句）。
- **`RoleIdQuery`**：抽取器結構性無 reject 面（`FromRequestParts`、`Rejection = Infallible`；形同既有 `RoleHomeQuery`）：`id` 缺席或壞形（`?id=abc`、同名鍵重複）＝`id=0`＝查無活性角色＝`biz.role.notFound`；不放行框架 400 裸回應。前端以具名型組 query（`const params: Api.Authz.RoleIdQuery = { id };`，005 刀 `fetchGetRoleHome` 同形）。
- 受審：上表各型於 wire-schema 快照成 `Api.Authz.<型>` definition、全數入受審名冊並各配正向＋反例裁判（FR-052；`protected` 缺席或型錯、角色鍵寫成 `roleId`、`effective` 元素跨型為重點反例；名冊、側別與節謂詞擴至 `Api.Authz.` 前綴＝`contracts/code-gates.md`）；受審實數以抽取為準。

## 三維寫端共同語意（端點 2／4／6）

- **全量替換、射程＝候選集**（FR-009；ADR-00066 決定 1／決定 2）：輸入為期望全集，MUST NOT 有增量式介面。比對鍵＝政策鍵（v1, v2）。
  - 撤銷集＝（現況 ∩ 候選集）−期望集；新授集＝（期望集 ∩ 候選集）−現況。
  - 候選外現役列不撤、不授、不入 `effective`、不入現況讀端回應（spec Clarifications 第二題）；受保護撤銷拒只看候選內撤銷集；`revoked`／`granted` 只計候選內。
  - 現況與候選集皆於同一交易、標的角色列 `FOR UPDATE` 之後讀取（lock-then-redecide；FR-013）。
- **orphan skip＋去重**：期望集中候選外之項（已刪或不存在之選單 id、負值或界外 id、不在聯集之按鈕碼、不在路由表之路徑、方法不屬白名單〔含小寫 `get`、`PUT`／`PATCH`〕之端點）靜默略過、不產生孤兒授權、不另提示；重複項保首見。
- **生效集合（`effective`）**＝orphan skip 與去重後之期望集（期望集 ∩ 候選集、保首見序），以各維介面識別呈現（選單 id／按鈕碼／`Endpoint`）；集合上恆等於寫後之「現況 ∩ 候選集」＝其後現況讀端所回（寫讀閉合、次序不保證相同；ADR-00066 決定 6）。
- **受保護項須原樣帶回**：期望集缺任一候選內之受保護授權列 ⇒ 該列入撤銷集 ⇒ 整批拒 `2222`＋`biz.role.protectedRevoke`（三維皆適用；任何寫入之前判定、零變更零歸檔零稽核零同步；FR-011、ADR-00066 決定 8）。R_SUPER 名下之非受保護列 MUST 可撤（Q14；自救＝授權回收桶復原端點維列）。
- **期望空集＝合法全撤**：合法 `id`＋明確之空陣列 ⇒ 候選內現役列全撤（仍受上款受保護撤銷拒約束；Q15）。body 缺席或壞形（含期望集鍵缺席或拼錯）⇒ `id=0` ⇒ `biz.role.notFound` 早拒、零變更，MUST NOT 演成全撤（FR-007、ADR-00066 決定 7＋spec Clarifications 第七題）。
- **outcome 恰兩態**（FR-015）：Applied（含空 diff）⇒ `0000`＋三型之一；Rejected ⇒ `2222`＋拒因鍵、`data` null。查無角色不屬 outcome、走 `biz.role.notFound`。
- **寫入形**：撤銷＝移入授權歸檔（完整快照、來源角色 id 由歸檔寫入件〔新建 `sys_casbin_archive::archive_revoked_policies` → 既有私有 `move_to_archive` → 既有私有 `insert_snapshot`；後者亦為公開入口 `insert_archived` 之本體〕以 `v0` 反查活性角色填入、reason＝`menu_revoke`／`button_revoke`／`endpoint_revoke`〔三常數新建〕；刪除集以剛歸檔那批 id 圈定）；新授＝經 facade 直接 INSERT（新 id、`protected` 顯式 FALSE、`created_by`＝操作者 uid、`created_at` 由 DB default），MUST NOT 經判定引擎管理 API 或轉接器之新增政策路徑（FR-012、LL-00035）；新授集排序後逐列寫入。列層細節＝data-model §7「歸檔與寫入不變式」。
- **稽核**：Applied（含空 diff）同交易恰一列——`AuditOperation::Update`（字面 `update`）、`entity_table`＝`"sys_role"`、`entity_id`＝標的角色 id、`before`＝無、`after`＝`{dimension, revoked, granted}`（`dimension`＝`"menu"`／`"button"`／`"endpoint"`、後兩者為候選內計數）；Rejected、查無角色、拒寫零列。此為「授權寫端不採 005 刀整列快照慣例」之例外（三維寫端不改角色列、無列快照可取）；role.rs 既有私有 `record_audit`（綁角色列快照）不直接套用，另立授權寫端稽核件（新建）。鍵名與值形定稿＝data-model §10「操作稽核列」。
- **判定面同步**：Applied 即觸發、不問 diff（含空 diff＝授予面刻意例外，與移除面「實際歸檔 ≥1 列」並陳、MUST NOT 統一；ADR-00067 決定 1／決定 2）；Rejected、查無角色、拒寫、未 commit 之失敗 MUST NOT 觸發（決定 3）。收場沿 005 刀取消安全形（`handler/role.rs` 之 `settle_domain_write` 形：commit 與其後同步整段交脫離請求生命週期之 task、回應前 await 之；觸發門以 outcome 判、MUST NOT 套 `archived > 0` 門；ADR-00067 決定 4）⇒ 回應於同步結束後才送出；收場 task 被取消（非常態、唯 runtime 關機可致）＝`5000`（commit 與同步未必完成；告警形同既有 `settle_domain_write` 之取消分支〔該分支 target＝`security.authz`〕，授予面之告警字面由 tasks 定）。同步呼叫時不持判定面讀鎖、每請求至多一次；`casbin_reload_total{outcome}` 依同步結果計（ok／retry／exhausted 值集不變）。
- **生效時點兩層**（FR-019）：API 判定於判定面換上後即時生效；被改角色之使用者，其側欄選單與按鈕顯隱於下次載入頁面時更新；不推播。已知降級窗兩類（commit→換上之有界過渡窗、重試耗盡窗；端點維撤銷於窗內仍放行＝撤銷殘留、新授於窗內仍回 `5003`＝授予面反向症狀）＝ADR-00067 決定 6；發起寫端之請求於同步結束後才收到回應、單一操作者一般觀察不到過渡窗。
- **處理序之 wire 可觀察面**（★多重違規取先序之拒因、此先後即契約；逐步全文、固定鎖序與入域位置＝data-model §5「守門固定序」之 §5.1～§5.3，本檔不重列）：
  1. 操作者上下文缺席 ⇒ `5000`（先於一切守門、不開交易、不落稽核列）。
  2. 標的角色查無（含已軟刪、body 收斂之 `id=0`）⇒ `2222 biz.role.notFound`；停用角色照常可讀寫授權（停用≠撤銷；停用即斷權由授權讀端每請求濾角色狀態）。
  3. 撤銷集觸及候選內受保護授權列 ⇒ `2222 biz.role.protectedRevoke`（三維）。
  4. 〔僅端點維〕新授集觸及封死集 ⇒ `2222 biz.role.protectedGrant`（後於第 3 項判；ADR-00064 決定 3）。
  5. 第 2～4 項任一拒 ⇒ 零變更、零歸檔、零稽核、零同步（顯式 rollback）；全過＝Applied ⇒ 撤銷、新授與稽核同交易落寫，收場 task 內 commit → 同步 → 回應（見本節「判定面同步」條）。
  選單維與按鈕維之寫端入選單序列化域（端點總表；入域為交易首動作、早於一切列鎖）、端點維不入域；候選集與現況於標的角色列鎖之後判定（本節首條；端點維候選為編譯期常數、由 handler 於交易前取得）。

## 三維現況讀端共同語意（端點 1／3／5）

- 以 `id` 讀活性角色代碼（未軟刪、停用照讀；查無、已軟刪、`id=0`＝`2222 biz.role.notFound`）。所用讀端＝新建 `sys_role::active_code_of`（data-model §13；rev5 同名件）。
- 回「現況 ∩ 候選集」、每項帶 `protected`（FR-014；spec Clarifications 第二題）：收窄 MUST 與寫端共用同一濾點件與同一候選取得件、MUST NOT 另寫第二份判準（ADR-00066 決定 5）。★與 `rev5:ADR 0056`「讀端維持現狀」刻意分岔（UI 零差〔就讀端取態本身而言；22080 之端點候選另多 15 支後刀路由＝文末比對表 getAllEndpoints 列〕、wire 列數差；已登入 spec 刻意分岔登記表）：rev5 測試凡以讀端讀回候選外列為前提者，rev6 改以資料庫直讀觀察。
- 列序＝授權列 id 升冪（rev5 同）。資料庫錯＝`5000`（經 role.rs 既有 `db_failure`，target `security.role`）。

## 1. `GET /systemManage/getRoleMenu`（seed 32）

Query `RoleIdQuery`：`id`。
200：`data: RoleMenuItem[]`——該角色選單維現役列（`v2='menu'`）先以治理域（未刪、含停用）路由名收窄、再以同一次 `sys_menu::list_governed` 讀所得之映射表反向映射回選單 id（候選外路由名因先收窄而不反射；停用選單照回）；`protected` 依該列。seed 下 `id=1`（R_SUPER）預期 77 項、其中 `protected=true` 4 項（量法：解析 `SEED_CASBIN_RULE`，R_SUPER 之 `v2='menu'` 77 列全落 seed 78 選單之路由名內、受保護 4 項之選單 id＝4／5／9／10〔＝回應 `id` 欄之值；對應授權列 10／11／69／72，勿與選單 id 混用——授權列 10＝`manage_role`、選單 id 10＝`manage_policy-archive`〕）。
前端：選單權限彈窗之勾選集與鎖定集（受保護項 `disabled`＋受控勾選集之可寫 computed setter 補回；FR-034①）；現況讀成功前確定鈕停用、遲到回應依請求世代丟棄、切換角色先清角色維狀態（FR-034②～④）。同彈窗另消費既有 getMenuTree（樹＝治理域；005 刀 `wire-menu-admin.md` §2）、getAllPages（首頁下拉候選＝顯示域；同檔 §3）、getRoleHome／updateRoleHome（005 刀 `wire-role-admin.md` §7／§8；首頁下拉選值即打 updateRoleHome、與確定鈕獨立、取消不還原、清空送 null＝spec Clarifications 第三題、FR-033、ADR-00068 款 13）。

## 2. `POST /systemManage/updateRoleMenu`（seed 33；進選單域）

Req `UpdateRoleMenuReq`：`{ id: number, menuIds: number[] }`（期望全集；含受保護項須原樣帶回；順序與重複不影響結果）。
候選集＝治理域選單（未刪、含停用）之路由名集；映射表與候選集取自 `sys_menu::list_governed` 之同一次讀（ADR-00066 決定 3）；★MUST NOT 誤用顯示域（映射半誤用＝停用被靜默升級為撤銷、候選半誤用＝停用選單之授權自生效集合與現況讀端消失而不可治理；兩形皆配負向測＝FR-010、SC-003）。已知邊界：治理域中 `parent_id` 成環之列及其子孫在候選內而不在 getMenuTree 樹中（ADR-00066 決定 3）。
處理序＝「三維寫端共同語意」節（入域；逐步全文＝data-model §5.1）；撤銷列 reason＝`menu_revoke`（屬不可復原集＝ADR-00065 決定 1：回收桶只剩閱覽、只能重勾）。
200：`data: RoleMenuGrantRes`；Applied 即同步。拒：`2222 biz.role.notFound`／`2222 biz.role.protectedRevoke`；`5000`：上下文缺席、資料庫錯、收場被取消。
例：`{"id":5,"menuIds":[1,2,3]}` ⇒ `{"revoked":0,"granted":3,"effective":[1,2,3]}`（標的原無選單維授權、三 id 皆在治理域時）；同 body 再送一次 ⇒ `{"revoked":0,"granted":0,"effective":[1,2,3]}`、仍同步一次、稽核一列。
前端：選單權限彈窗之確定鈕（只送本端點、全量；不加父子連動＝FR-033）。

## 3. `GET /systemManage/getRoleButton`（seed 53）

Query `RoleIdQuery`：`id`。
200：`data: RoleButtonItem[]`——按鈕維現役列（`v2='button'`）以治理域按鈕碼聯集（與 §7 同一讀端）收窄。seed 下 `id=1` 預期 20 項、`protected=true` 0 項（R_SUPER 之 `v2='button'` 20 列全落 seed 聯集 20 碼內）。
前端：按鈕權限彈窗之現況與鎖定集（同 §1 之三守衛）。

## 4. `POST /systemManage/updateRoleButton`（seed 54；進選單域）

Req `UpdateRoleButtonReq`：`{ id: number, buttons: string[] }`（期望全集＝按鈕碼）。
候選集＝治理域選單按鈕碼之聯集（與 §7 同一讀端；含停用選單之碼）；任一治理域列之按鈕碼清單壞形 ⇒ 整請求 `5000`（沿既有 `sys_menu::button_codes_of` 之壞形回錯語意；ADR-00066 決定 3）。
處理序＝「三維寫端共同語意」節（入域；逐步全文＝data-model §5.2）；撤銷列 reason＝`button_revoke`（不可復原）。
200：`data: RoleButtonGrantRes`；Applied 即同步。拒與 `5000` 腿同 §2。
前端：按鈕權限彈窗之確定鈕。

## 5. `GET /systemManage/getRoleEndpoints`（seed 56）

Query `RoleIdQuery`：`id`。
200：`data: RoleEndpointItem[]`——以 HTTP 方法白名單（新建 `router::endpoint_methods()`，由既有 `router::HttpMethod` 全變體經 `as_str` 導出；不以排除他維反推）辨識端點維現役列、再以端點全集（新建 `router::policy_endpoints()`）收窄。seed 下 `id=1` 預期 35 項、`protected=true` 14 項；`id=2`（R_ADMIN）預期 2 項（seed 3 列中列 2 `/systemManage/getUserList` 屬候選外）。量法：`SEED_CASBIN_RULE` 對 ROUTES 之 Policy 條目聯集本刀十條逐鍵比對（R_SUPER 端點維 50 列＝50 相異（路徑,方法）、其中 35 列落候選內；受保護 15 列中 14 列落候選內）。
前端：端點權限彈窗之現況與鎖定集（葉鍵以路徑與方法合成、反查由映射表還原不拆字串＝FR-033）。

## 6. `POST /systemManage/updateRoleEndpoints`（seed 57；不進選單域）

Req `UpdateRoleEndpointsReq`：`{ id: number, endpoints: Endpoint[] }`（期望全集＝（路徑,方法））。
候選集＝新建 `router::policy_endpoints()`（住 `rust-api/server/src/router.rs`、由 ROUTES 中 `protection == Protection::Policy` 導出之（路徑,方法）全集；編譯期常數、恆不變）；handler 於交易前取得候選與白名單、以參數傳入 facade（facade 零 `crate::router` 引用）。
處理序＝「三維寫端共同語意」節但★不入域（序列化層＝標的角色列 `FOR UPDATE`；逐步全文＝data-model §5.3）；受保護撤銷拒**先判**、結構性封死**後判**（該節處理序第 3／第 4 項；ADR-00064 決定 3）：標的角色代碼 ≠ `sys_role::SUPER_ROLE_CODE` 且新授集 ∩ 封死集 ≠ ∅ ⇒ 整批拒 `2222`＋`biz.role.protectedGrant`（不靜默壓縮：不剔除被擋項後放行其餘）；封死集＝`ptype='p' ∧ protected=TRUE ∧ v2 ∈ HTTP 方法白名單` 之（路徑,方法）、鎖內以新建 `sys_casbin_policy::protected_endpoint_set` 現查（ADR-00064 決定 1／決定 2）；標的為 R_SUPER 或新授集為空時不查封死集。撤銷列 reason＝`endpoint_revoke`（唯一可復原原因＝ADR-00065 決定 1）。
200：`data: RoleEndpointGrantRes`；Applied 即同步。拒：`biz.role.notFound`／`biz.role.protectedRevoke`／`biz.role.protectedGrant`（皆 `2222`）；`5000` 腿同 §2。
例：R_SUPER 以候選內現況原樣提交 ⇒ `0000`、`revoked 0`、`granted 0`、`effective`＝候選內 35 項（候選外 15 列原封）；對 R_ADMIN 提交含 `{"path":"/systemManage/updateRoleEndpoints","method":"POST"}` ⇒ `2222 biz.role.protectedGrant`、零變更。
前端：端點權限彈窗之確定鈕（候選未就緒時靜默早退、不關窗＝rev5 形）；替非 R_SUPER 勾選封死集端點者於此被拒（純 key toast、無明細；FR-034）。

## 7. `GET /systemManage/getAllButtons`（seed 52）

200：`data: string[]`——治理域（未刪、含停用）選單按鈕碼之聯集：依 `sys_menu::list_governed` 之同層序（`"order" ASC NULLS LAST, id ASC`）逐列經 `sys_menu::button_codes_of` 取碼、首見序去重（`rev5:B-115` 穩定序同形；聯集讀端為新建件，rev5 對應件 `sys_menu::all_button_codes`）；與絕版判定之 `sys_menu::obsolete_codes` 私有掃描不共用（FR-014）。不帶受保護或封死預標。任一列按鈕碼清單壞形或資料庫錯 ⇒ `5000`（rev5 為跳過壞形列；差異見文末）。seed 下預期 20 項（量法：解析 m0002 `sys_menu` 78 列之 `buttons` 欄去重）。
前端：按鈕權限彈窗之候選樹（每次開啟重取、成功才覆蓋；FR-034④）。

## 8. `GET /systemManage/getAllEndpoints`（seed 55）

200：`data: Endpoint[]`——新建 `router::policy_endpoints()` 之全集投影、照 ROUTES 註冊序、每項恰 `{path, method}` 兩鍵（不帶 `protected`、不帶封死預標＝Q3、FR-014）；含自身；不觸資料庫。回應集隨路由表成長：本刀後 35 項（＝ROUTES 政策保護條數）。與 updateRoleEndpoints 之候選集、授權回收桶復原第④腿與可復原旗標④半同一真源（ADR-00066 決定 3）。
前端：端點權限彈窗之候選樹（依路徑群組、群組鍵＝純路徑、群組級勾選＝勾其全部未鎖葉、回報值只含葉鍵；FR-033）。

## 授權態矩陣（contract 測）

Super 八支皆通（三支寫端以空 body 打＝`2222 biz.role.notFound`、零變更）；Admin／User 八支皆 `5003`（seed 只授 R_SUPER）；未登入 `8888`。contract case 集與 ROUTES 恰等（49＝49、雙向覆蓋閘、case_key 綁定）；新三鍵之真 seed 實發點與名冊雙向閘＝`contracts/msg-keys.md`；case 名冊、授權態矩陣表與名冊閘擴列＝`contracts/code-gates.md`。

## 與 rev5 wire 逐欄比對

| 面 | rev5（HEAD） | rev6 本刀 | wire 差 |
|---|---|---|---|
| 命名空間與檔 | `Api.RoleAdmin` 追加於 `rev5-role-admin.d.ts`；fetcher 追加於 `rev5-role-admin.ts` | `Api.Authz`（新建 `rev6-authz.d.ts`）；fetcher 新建 `rev6-authz.ts` | 零（型名前綴差） |
| `Endpoint` | `{path, method}` | 同 | 零 |
| `RoleMenuItem`／`RoleButtonItem`／`RoleEndpointItem` 欄 | `{id, protected}`／`{code, protected}`／`{path, method, protected}` | 同 | 零 |
| 現況讀端回應集 | 選單維經治理域反查（實效＝候選內）；按鈕維與端點維回全部現役列（`rev5:ADR 0056`「讀端維持現狀」） | 三維皆「現況 ∩ 候選集」 | ★列數差：R_SUPER 端點維 rev5 50 列、rev6 35 列；R_ADMIN 端點維 rev5 3 列、rev6 2 列；按鈕維與選單維 seed 下同數（刻意分岔登記表列） |
| 寫端回應型 | 泛型 `GrantResult<T>`（後端以 `GrantResult<MenuId>`／`<String>`／`<Endpoint>` 實例化；typings 泛型＋三具體別名） | 三支具體型 `RoleMenuGrantRes`／`RoleButtonGrantRes`／`RoleEndpointGrantRes`（兩側零新泛型） | 零（欄 `revoked`／`granted`／`effective` 同；快照少泛型本體與一支佔位 definition） |
| 寫端請求三型 | `{id, menuIds}`／`{id, buttons}`／`{id, endpoints}` | 同 | 零 |
| 讀端 query | 後端 `RoleIdQuery`；typings 無具名型（fetcher 內聯 `{ id }`） | 兩側 `RoleIdQuery`（005 刀 `RoleHomeQuery` 形） | 零 |
| getAllButtons 壞形列 | `all_button_codes` 跳過壞形列 | 整請求 `5000`（fail-loud；按鈕維讀寫端同） | 只在庫內直改壞形時有差 |
| getAllButtons 序 | `(order NULL 殿後, id)` 首見去重（`rev5:B-115`） | 同（`list_governed` 同層序） | 零 |
| getAllEndpoints | ROUTES Policy 全集、註冊序＝50 項（rev5 HEAD 之 ROUTES 含 `rev5:007`／`rev5:008` 之使用者與稽核端點 15 支：getUserList、getDeletedUsers、addUser、updateUser、deleteUser、batchDeleteUser、restoreUser、kickUser、resetUserPassword、updateUserSessionPolicy、getOperationLog、getAccessLog、getLoginAttempt、getSessionEvent、purgeAuditLog；`rev5:006` 收刀時為 35） | 同判準、本刀後 35 項 | ★候選少 15 支（皆後刀路由）⇒ 端點權限彈窗之候選樹 22080 為 50 葉、32080 為 35 葉；R_ADMIN 之 seed 列 2（getUserList）於 22080 屬候選內而顯已勾、32080 不出現——CDP 結構清單須排除此差（排除依據＝spec 刻意分岔登記表「端點候選集」列；觀察形＝quickstart §8 端點權限彈窗列） |
| 拒因鍵 | 構造點以字面 `Cow::Borrowed("biz.role.protectedRevoke")` 等 | 構造點取 `error.rs` 之 `msg_key::` 常數、入 `MSG_KEYS`（43→46） | 零（鍵字面同） |
| 操作者缺席 | `5000`；log 借 `security.ipgate`＋`degraded` 欄 | `5000`；log 掛 `security.role`＋`refused` 欄、零 degraded | 零（log 差） |
| 交易與收場 | facade 自開交易、自取域鎖、自寫稽核；handler 於請求 future 內 commit 後 reload | handler 持交易、內層首句入域、稽核同交易；commit 與同步交脫離請求之 task | 零（僅收場被取消時回 `5000`） |
| body 收斂之端點標籤 | `role.update-menu` 形（三參數 `json_or_default`） | `updateRoleMenu` 形（四參數、餵本域 `BODY_FALLBACK_MSG`） | 零（log 差） |
| 稽核列 | `{dimension, revoked, granted}`、`sys_role`、角色 id、空 diff 亦一列 | 同（欄名 rev6 `before`／`after`） | 非 wire |

## 拒寫事件與觀測

- 操作者上下文缺席之拒寫事件＝role.rs 既有私有 `operator_from` 所發：`tracing::error!(target: "security.role", refused = "request_context_absent", endpoint, uid, "角色寫端取不到操作者來源 → 拒寫 5000（不以佔位位址補稽核列）")`、MUST NOT 帶 degraded 欄、MUST NOT 增計任何降級序列（字面已由 `handler/common.rs` 之 `each_domain_keeps_its_own_log_literals` 逐域釘住；三支新寫端共用、不另立）。
- body 收斂 debug 事件：三支新寫端之 `FromRequest` 一律餵 role.rs 既有 `BODY_FALLBACK_MSG`（「角色寫端 body 取用失敗——收斂成空請求交守門判」）、端點標籤＝端點名。
- 資料庫故障：經 role.rs 既有 `db_failure(endpoint, step)`（target `security.role`）落 error 後翻 `5000`。
- 受保護撤銷拒與封死拒之被擋項：MUST NOT 上 wire；至多入 tracing 與測試斷言（ADR-00064 決定 3）。
- 判定面同步：`casbin_reload_total{outcome="ok"|"retry"|"exhausted"}` 與告警 `obs016-casbin-reload-anomaly` 照舊（ADR-00067 決定 8）；授予面空 diff 亦 `ok` +1。同步呼叫點名冊 `RELOAD_CALL_FILES` 已含 `handler/role.rs`（三維寫端零擴列）；role.rs 生產區同步觸發點之源碼釘測隨授予面收場件同單元改寫（`contracts/code-gates.md`）。
