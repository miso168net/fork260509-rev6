# Contract — 選單管理九端點（menu CRUD 7＋getMenuTree＋getAllPages）

> 權威序依憲法 §I.3：base-web 實碼 ＞ 官方 docs ＞ mock。upstream 選單頁為 demo 殼（`fetchGetMenuList()` 無參、寫端假成功）；契約以 `rev5:005` `contracts/wire-menu-admin.md` 已驗證形為藍本、依 rev6 拍板改寫（research R3 清單 B），由本檔凍結。
> 信封、錯誤碼總則同 `wire-role-admin.md` 檔頭（寫端先取操作者上下文、缺席＝`5000`）；九條 route 皆政策保護、授權恰 R_SUPER（seed 25～31、64、65；後兩列 protected）。
> 型別檔＝`base-web/src/typings/api/rev6-menu-admin.d.ts` 之 `Api.MenuAdmin`；wrapper＝`base-web/src/service/api/rev6-menu-admin.ts`（menu 7＋`fetchGetMenuTree`；getAllPages 走 upstream barrel 既有 `fetchGetAllPages`）。

## 共用型 `MenuRecord`（28 欄＋可缺席 `children`；宣告序＝wire 欄序）

| # | 欄 | 型 | 說明 |
|---|---|---|---|
| 1 | `id` | number | 2^53 守衛 |
| 2 | `parentId` | number | DB NULL→0（頂層）；孤兒列（父被直改庫軟刪）顯 DB 原值、在樹中升根 |
| 3 | `menuType` | `'1'` \| `'2'` | DB `1`→`'1'`（目錄）、其餘→`'2'`（選單） |
| 4 | `menuName` | string | |
| 5 | `routeName` | string | 授權錨、不可變 |
| 6 | `routePath` | string \| null | |
| 7 | `component` | string \| null | |
| 8 | `status` | `'1'` \| `'2'` | |
| 9～12 | `hideInMenu`／`keepAlive`／`multiTab`／`constant` | boolean \| null | |
| 13 | `protected` | boolean | 唯讀 |
| 14 | `order` | number \| null | |
| 15 | `icon` | string \| null | |
| 16 | `iconType` | `'1'` \| `'2'` \| null | DB NULL→null、`2`→`'2'`、其餘→`'1'` |
| 17 | `i18nKey` | string \| null | |
| 18 | `href` | string \| null | |
| 19 | `activeMenu` | string \| null | |
| 20 | `fixedIndexInTab` | number \| null | |
| 21 | `query` | `{key, value}[]` \| null | jsonb 直傳 |
| 22 | `buttons` | `{code, desc}[]` \| null | jsonb |
| 23 | `menuMemo` | string \| null | 只上管理列表（純文字插值） |
| 24 | `deleted` | boolean | `deleted_at IS NOT NULL` 導出 |
| 25 | `createdAt` | string | RFC3339 |
| 26 | `updatedAt` | string \| null | |
| 27～28 | `createdBy`／`updatedBy` | string \| null | 帳號名回填 |
| — | `children` | `MenuRecord[]`（可缺席） | 子集為空則不上 wire |

可空欄 DB NULL＝顯式 `null`、不省略欄（ADR-00047 決定 1）。upstream 同 URL 之 `Api.SystemManage.MenuList`（`fetchGetMenuList`）與本型之偏離記帳於 ADR-00044 決定 9。

## 1. `GET /systemManage/getMenuList/v2`（seed 25；治理域）

Query `MenuListQuery`：`current?`／`size?`。★**全取例外**（跨端點分頁規則之唯一例外、明名入口承載、白名單恰此端點）：`size` 未帶（含完全缺席與查詢串壞形＝整串收斂為預設＝視同沒帶）⇒ 回全部頂層及其全深子樹、回應 `current=1`、`size`＝實得頂層數、`total`＝頂層總數；帶合法 `size`（含 `0`⇒clamp 成 1）⇒ 通則（current clamp [1, 10^7]、size clamp [1, 100]、逾界回空頁且 `current`＝上界值）。
200：`data: PageRes<MenuRecord>`（records＝頂層切片、各帶全深 `children`）；治理域＝未刪（含停用）；同層序＝`(order ASC NULLS LAST, id ASC)`、頂層分頁依此序切；頂層＝父為 NULL 或父不在治理域集合（孤兒升根、計入 total）。seed 下無參呼叫預期回 `current=1, size=11, total=11`。
★前端共用表格把回應 `size` 回寫每頁筆數 ⇒ 首載與頂層列數增減時各多一發重取（畫面不變；CDP 排除請求次數維度）。

## 2. `GET /systemManage/getMenuTree`（seed 27；治理域）

200：`data: MenuTreeRecord[]`＝`{ id: number, label: string, pId: number, children?: MenuTreeRecord[] }`（`children` 子集為空則不上 wire——葉節點只三鍵，同共用型 `MenuRecord`；承 rev5 MenuTreeRecord 之 skip 形）；`label`＝`menu_name`（非 i18nKey）；頂層與孤兒升根者 `pId=0`；同層序同 §1。wire 形 MUST 同時與 upstream `Api.SystemManage.MenuTree` 相容（既有消費者＝角色頁菜單權限彈窗、本刀一行不動）；本刀父選擇器經新 wrapper 消費同一 wire（前端前插合成頂層節點 `{id: 0}`）。

## 3. `GET /systemManage/getAllPages`（seed 26；顯示域）

200：`data: string[]`＝顯示域（啟用且未刪）全部選單之 `routeName`、扁平、依 `(order ASC NULLS LAST, id ASC)`；零授權面。seed 下 78 項。

## 4. `POST /systemManage/addMenu`（seed 28；進選單域）

Req `MenuAddReq`：`{ menuType?: string, menuName: string, routeName: string, parentId?: number|null, routePath?, component?, icon?, i18nKey?, href?, activeMenu?, menuMemo?: string|null, status?: string, hideInMenu?, keepAlive?, multiTab?, constant?: boolean|null, order?, fixedIndexInTab?: number|null, iconType?: string, query?: {key,value}[]|null, buttons?: {code,desc}[]|null }`。
值語意：`menuType`／`status` 值域外＝取預設（1）；`iconType` 值域外＝NULL；可空文字欄 `""`＝NULL；`parentId` 缺席、null 或 0＝頂層（寫 NULL）。
處理序（★凍結、多重違規取先序腿）：域鎖→①父驗證（父不存在或已刪→`2222 biz.menu.parentNotFound`；停用之父不擋；頂層豁免）②防環（上溯祖先鏈遇環或逾上溯上限→`biz.menu.cycleDetected`）③路由名活性唯一先驗→`biz.menu.routeNameExists`④常量父鏈（`constant=true` 且非頂層：全祖先須常量、鏈斷保守拒→`biz.menu.constantParent`）⑤路由名形制 `^[A-Za-z0-9_-]{1,100}$`→`biz.menu.routeNameInvalid`⑥保留路由名（∈ 前端內建常量路由 `403`／`404`／`500`／`iframe-page`／`login` 或內建根路由 `root`／`not-found`→`biz.menu.routeNameExists`；ADR-00044 決定 8）⑦名稱非空→`biz.menu.nameRequired`⑧href 形制（非空且不以 `http://`／`https://` 起首〔不分大小寫〕→`biz.menu.hrefInvalid`）⑨按鈕碼清單形制（非 null 非陣列、成員非物件、`code` 缺席或非字串或為空、`code` 逾 100 字元、同清單 `code` 重複→`biz.menu.buttonsInvalid`；`desc` 不驗）⑩INSERT（活性唯一索引衝突兜底→`routeNameExists`）＋稽核 `add`。零授權寫入（兩步流第一步）。
200：`data: null`。body 缺席或壞形＝預設（全空）⇒ 首個命中腿＝`routeNameInvalid`。

## 5. `POST /systemManage/updateMenu`（seed 29；進選單域）

Req `MenuUpdateReq`：`{ id: number, menuName?, routePath?, component?, icon?, i18nKey?, href?, activeMenu?, menuMemo?: string|null, status?: string, parentId?: number|null, hideInMenu?, keepAlive?, multiTab?, constant?: boolean|null, order?, fixedIndexInTab?: number|null, iconType?: string|null, query?, buttons?: …|null, routeName?: string|null, menuType?: string|null }`（`routeName`／`menuType` 出現〔含 null〕即拒；非字串值＝body 壞形、零變更成功）。
欄位語意（ADR-00047）：缺席＝不動；可空文字欄 null 或 `""`＝清空落 NULL；可空非文字欄 null＝清空落 NULL；`status` 值域外＝缺席；`iconType` 值域外＝缺席、null＝清空；`parentId` 非三態（null＝缺席、0＝頂層）；`buttons: null`＝清空全部按鈕碼（舊碼全數參與絕版計算）；`constant: null`／`false`＝清除常量性。
處理序（★凍結）：①提前 no-op（除 `id` 外全欄缺席——`routeName`／`menuType` 出現即非缺席）②名稱非空（出現且 null 或 `""`→`nameRequired`）③域鎖→鎖列（查無或已刪→`biz.menu.notFound`）④不可變欄出現（不比對值；`routeName`→`biz.menu.routeNameImmutable` 先於 `menuType`→`biz.menu.menuTypeImmutable`）⑤受保護列：`status` 解析為 `'2'` 或 `parentId` 變更→`biz.menu.protectedMenu`⑥`parentId` 變更時：父驗證（`parentNotFound`）→防環（`cycleDetected`）⑦常量父鏈：效值為常量且（改父或 `constant` 出現）→驗全祖先；`constant` 出現且效值非常量→反查治理域全深後代（含停用、不含已刪）存常量者即拒；皆 `constantParent`⑧href 形制（`hrefInvalid`）⑨按鈕碼清單形制（`buttonsInvalid`；先於絕版計算）⑩絕版計算：舊碼−新碼中不屬治理域其餘選單（排除標的自身）按鈕碼聯集者＝絕版 → 其按鈕維政策歸檔（reason `menu_button_removed`、不可復原；先於本列 UPDATE）⑪UPDATE＋稽核 `update`→commit⑫按鈕碼絕版實際歸檔 ≥1 列＝commit 後觸發判定面同步。
★「`parentId` 變更」＝出現且 0→NULL 正規化後 ≠ 現值；同值＝該欄無變更（不跑⑥、受保護列不拒）。「隱藏於選單」照常落庫（運行期改值屬業務資料、ADR-00044）。
200：`data: null`。body 缺席或壞形＝零變更成功。

## 6. `DELETE /systemManage/deleteMenu`（seed 30；進選單域）

Req `MenuIdReq`：`{ id: number }`（缺席或壞形＝0→`notFound`）。
處理序：域鎖→①鎖列（`notFound`）②受保護→`protectedMenu`③存在未刪子項（不論啟停）→`biz.menu.hasChildren`④歸檔：`v1=route_name AND v2='menu'`（跨全角色）＋獨有按鈕碼（標的碼 − 治理域其餘選單聯集）之 `v2='button'` 列；reason 皆 `menu_soft_delete`；先於軟刪⑤軟刪＋稽核 `delete`→commit⑥實際歸檔 ≥1 列＝同步。零政策列之選單＝零歸檔零同步。
200：`data: null`。

## 7. `DELETE /systemManage/batchDeleteMenu`（seed 31；進選單域）

Req `MenuBatchDeleteReq`：`{ ids: number[] }`（缺席或壞形＝空陣列）。
語意：空陣列＝提前成功（零副作用、不取域鎖）；重複 id 先去重；鎖讀全部標的、任一查無或已刪＝整批 `notFound`（★查無優先、先於各項守門）；子先於父（深度 DESC、id DESC）逐項全套 §6 守門（「未刪子項」排除同批已刪者）；任一違規整批拒、單一交易、零變更零稽核；全數通過後依同拓撲序逐項「現算獨有按鈕碼（同批先行者已軟刪、不在治理域）→ 歸檔 → 軟刪 → 稽核」（MUST NOT 於守門期預算；同批共持而批外無持有者之碼於批內恰歸檔一次）；整批合計實際歸檔 ≥1 列＝至多一次同步。
200：`data: null`。

## 8. `GET /systemManage/getDeletedMenus`（seed 64、protected 政策）

Query `MenuListQuery`：通則分頁（缺席→1／10；前端恆帶 size）。
200：`data: PageRes<MenuRecord>`；平面（`children` 恆缺席）、`deleted` 恆 true；排序 `deleted_at DESC, id DESC`；MUST NOT 帶「可復原」旗標（復原守門即唯一權威）。

## 9. `POST /systemManage/restoreMenu`（seed 65、protected 政策；進選單域）

Req `MenuIdReq`：`{ id: number }`。
處理序：域鎖→①鎖列（標的須為已刪存在；現役或不存在→`notFound`，非冪等成功）②同路由名活性衝突→`biz.menu.restoreConflict`（活性唯一索引衝突兜底同鍵）③父未刪（頂層豁免）→`parentNotFound`④常量標的之全祖先常量性→`constantParent`（非常量標的零驗）⑤成對清空 `deleted_at`／`deleted_by`、原 status 保留＋稽核 `restore`。MUST NOT 回灌任何授權、零授權寫、零判定面同步。
200：`data: null`。

## 拒寫事件

同 `wire-role-admin.md`，target 字面＝`security.menu`。
