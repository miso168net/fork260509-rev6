# Contract — 角色管理八端點（role CRUD 6＋roleHome 2）

> 權威序依憲法 §I.3：base-web 實碼 ＞ 官方 docs ＞ mock。upstream 角色頁為 demo 殼、其 fetch 標的即本刀補齊面；契約以 `rev5:005` `contracts/wire-role-admin.md` 已驗證形為藍本、依 rev6 拍板改寫（research R3 清單 B），由本檔凍結（spec 目錄＝定點快照；wire 活體權威＝碼＋`tests/contract.rs`＋wire-schema 快照）。
> 信封一律 `{data, code, msg}`、業務錯誤 HTTP 200（例外恰二：`4040`→404、`5003`→403）；八條 route 皆政策保護（授權態逐列照 seed，見各節）。未登入＝既有 `8888`；無授權＝`5003`；寫端一律先取操作者上下文（缺席＝`5000` 拒寫、不落稽核列，先於一切守門與提前 no-op）；其餘 DB 錯＝`5000`。授權中介層不讀 body。
> 型別檔＝`base-web/src/typings/api/rev6-role-admin.d.ts` 之 `Api.RoleAdmin`；wrapper＝`base-web/src/service/api/rev6-role-admin.ts`（不入 barrel）。

## 共用型 `RoleRecord`（camelCase；宣告序＝wire 欄序）

| 欄 | 型 | 說明 |
|---|---|---|
| `id` | number | DB i64→number（2^53 fail-loud 守衛） |
| `roleCode` | string | 不可變 |
| `roleName` | string | |
| `roleDesc` | string \| null | |
| `roleMemo` | string \| null | 超管備註；只上管理列表（渲染端純文字插值） |
| `roleHome` | string \| null | 首頁路由名現值（忠實回、不做讀端兜底） |
| `status` | `'1'` \| `'2'` | DB `1`→`'1'`、其餘（含 NULL）→`'2'` |
| `createdAt` | string | RFC3339 帶 offset |
| `updatedAt` | string \| null | |
| `createdBy`／`updatedBy` | string \| null | 操作者帳號名（單次批次回填、查無→null） |

軟刪欄不上 wire（角色無回收桶）。

## 1. `GET /systemManage/getRoleList`（seed 12 R_SUPER、13 R_ADMIN）

Query `RoleListQuery`（全部可空）：`current`／`size`（跨端點分頁規則：缺席→1／10、current clamp [1, 10^7]、size clamp [1, 100]、顯式 0 取下界、逾界回空頁且回應 `current`＝上界值）／`roleName`、`roleCode`（不分大小寫子字串、`%`／`_`／`\` 視為字面；`""`＝不篩選）／`status`（**字串**：trim 後恰 `'1'`／`'2'` 等值篩選；其餘含 `""`＝不篩選）。查詢串壞形（如 `current=abc`、重複鍵）＝整串收斂為預設頁（1／10、無篩選）。
200：`data: PageRes<RoleRecord>`（`{current, size, total, records}`）；僅未刪角色；排序 id 升冪。
★前端首屏物件 `{current:1,size:10,roleName:null,roleCode:null,status:null}` 經 qs 渲染為 `k=` 形——三個篩選欄收為空字串＝不篩選；`status` 以字串承接方不致整串收斂（真串以容器內實跑為準＝research R10）。

## 2. `GET /systemManage/getAllRoles`（seed 14 R_SUPER、15 R_ADMIN、16 R_USER_COMMON）

200：`data: AllRole[]`，每項恰 `{id: number, roleCode: string, roleName: string}`（宣告序 id→roleCode→roleName；MUST NOT 帶備註與審計欄）；僅活性且啟用、id 升冪。wire 形 MUST 同時與 upstream `Api.SystemManage.AllRole` 相容（既有消費者＝upstream 使用者頁新增抽屜、本刀不動）。

## 3. `POST /systemManage/addRole`（seed 21 R_SUPER；不進選單域）

Req `RoleAddReq`：`{ roleCode: string, roleName: string, roleDesc?: string|null, roleMemo?: string|null, roleHome?: string|null, status?: string }`。
處理序（★次序即契約、多重違規取先序腿）：①代碼形制 `^[A-Za-z0-9_]{1,64}$`→否則 `2222 biz.role.codeInvalid` ②名稱非空（null 或 `""`→`biz.role.nameRequired`）③活性唯一先驗→`biz.role.codeExists`④落庫＋稽核 `add` 同交易（活性唯一索引衝突兜底收斂為 `codeExists`、MUST NOT 5000）。可空文字欄 null 或 `""`＝落 NULL；`status` 值域外＝缺席取預設啟用。成功後該角色零授權。
200：`data: null`。body 缺席或壞形＝收斂為預設（全空）⇒ 首腿 `codeInvalid`。

## 4. `POST /systemManage/updateRole`（seed 22 R_SUPER；不進選單域）

Req `RoleUpdateReq`：`{ id: number, roleName?: string|null, roleDesc?: string|null, roleMemo?: string|null, roleHome?: string|null, status?: string, roleCode?: unknown }`。
欄位語意（ADR-00047）：缺席＝不動；可空文字欄 null 或 `""`＝清空落 NULL；有值＝設值；`status` 值域外（含 `""`、null）＝缺席。
處理序：①提前 no-op（除 `id` 外全欄缺席——`roleCode` 出現即非缺席——＝成功、零變更、零稽核、不 bump 時戳）②名稱非空（出現且為 null 或 `""`→`nameRequired`）③鎖列（查無或已刪→`biz.role.notFound`）④`roleCode` 出現（不比對值）→`biz.role.codeImmutable`⑤停用雙護欄（`status` 解析為 `'2'` 時：操作者為該角色成員〔含停用角色之成員身分〕→`biz.role.cannotDisableSelfRole`；標的為 R_SUPER→`biz.role.superCannotDisable`，不因操作者身分而異）⑥UPDATE＋稽核 `update`。停用即斷權沿基線（授權讀端每請求濾角色狀態）、MUST NOT 觸發判定面同步。
200：`data: null`。body 缺席或壞形＝零變更成功。

## 5. `DELETE /systemManage/deleteRole`（seed 23 R_SUPER；進選單域）

Req `RoleIdReq`：`{ id: number }`（JSON body；缺席或壞形＝id=0→`notFound`）。
處理序：域鎖（交易首動作）→①鎖列（查無或已刪→`notFound`）②seeded（id ∈ {1,2,3}→`biz.role.seededProtected`）③in-use（`others = total − 操作者是否為成員`，total＝該角色全部指派列〔不濾使用者啟停與軟刪〕；>0→`biz.role.inUse`）④self-role（操作者為成員→`biz.role.cannotDeleteSelfRole`）⑤歸檔 `v0=role_code` 全三維含 protected（reason `role_soft_delete`、不可復原；**先於**軟刪）→軟刪→稽核 `delete`→commit⑥實際歸檔 ≥1 列＝commit 後觸發判定面同步。角色刪除單向（無復原端點）。
200：`data: null`。

## 6. `DELETE /systemManage/batchDeleteRole`（seed 24 R_SUPER；進選單域）

Req `RoleBatchDeleteReq`：`{ ids: number[] }`（缺席或壞形＝空陣列）。
語意：空陣列＝提前成功（零副作用、零稽核、不取域鎖）；重複 id 先去重（`[5,5]`≡`[5]`、稽核列數＝去重後標的數）；單一交易、id 升冪逐項全套 §5 守門；任一違規（含任一查無或已刪＝`notFound`）整批拒、零變更零稽核；全數通過後逐標的歸檔＋軟刪＋稽核；整批合計實際歸檔 ≥1 列＝commit 後至多一次同步。
200：`data: null`。

## 7. `GET /systemManage/getRoleHome`（seed 34 R_SUPER）

Query `RoleHomeQuery`：`id`（缺席或壞形＝0→`notFound`；不放行框架 400 裸回應）。
200：`data: RoleHomeRes`＝`{ home: string | null }`（顯式 null、不省略欄）；角色不存在或已刪→`notFound`。零 UI 消費者（ADR-00045 已知態）。

## 8. `POST /systemManage/updateRoleHome`（seed 35 R_SUPER；不進選單域）

Req `RoleHomeUpdateReq`：`{ id: number, home: string | null }`。**非部分更新**：`home` 缺席、null 或 `""`＝清空落 NULL；值同現值亦寫入並稽核；MUST NOT 驗「首頁是否在該角色可見樹內」（讀端 `getUserRoutes` 既有兜底：不在可見樹即取先序第一葉）。處理序：鎖列（`notFound`）→UPDATE→稽核 `update`。body 缺席或壞形＝id=0→`notFound`。
200：`data: null`。

## 拒寫事件與觀測

操作者上下文缺席之拒寫事件：`tracing::error!(target: "security.role", refused = "request_context_absent", endpoint, uid, …)`、MUST NOT 帶 degraded 欄、MUST NOT 增計任何降級序列；此事件字面納入 `each_domain_keeps_its_own_log_literals` 名冊與 `production_code_emits_no_degraded_field` 射程。
