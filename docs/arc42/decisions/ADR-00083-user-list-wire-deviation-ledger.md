---
id: "ADR-00083"
title: 使用者清單之 upstream 同 URL 型偏離帳——upstream `Api.SystemManage.User` 對 `Api.UserAdmin.UserRecord` 之欄差集由 wire 裁判自快照機器導出、釘值、漂移即紅（ADR-00044 決定 9 形、偏離帳第三列）；使用者管理頁改線 rev6 包裝、excel 示範頁為殘存消費面（所讀六欄皆共有欄）
date: 2026-10-05
status: proposed
supersedes: []
superseded_by: []
provenance: "007-user-password-admin 之 spec FR-005、FR-007、FR-008、FR-047、FR-053、FR-054、FR-064、SC-002、SC-011；brainstorm §0 Q14（記偏離帳、沿 rev6 欄名）／Q13（清單列帶持有角色之 id、代碼與名稱）／Q17（後端六欄過濾）、§3 §1 ADR 待立⑩、§3 §3「API 包裝與型別」；憲法 §I.3（typings 為 wire 唯一權威、每筆顯式偏離＝拍板、立 ADR）；形制前例＝ADR-00044 決定 9（角色與選單兩列偏離帳）與其機器形（`rust-api/server/tests/wire_schema.rs` 之 `DEVIATION_LEDGER`／`field_deviation`）；前代出處＝rev5:src/typings/api/rev5-user-admin.d.ts（`Api.UserAdmin` 獨立命名空間之理由：upstream 同名家族住凍結之 system-manage.d.ts、併入即須逐支改名閃避）——rev5 未立同 URL 型偏離帳、本帳為 rev6 新形；rev5:src/views/plugin/excel/index.vue 與 upstream 逐位元相同（excel 示範頁經 upstream 函式消費真端點之前代同形）；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [wire, typings, upstream-deviation, user-password-admin]
---

## 背景

- 憲法 §I.3：typings 為 wire 唯一權威，每筆顯式偏離＝拍板、立 ADR。005 刀前例＝ADR-00044 決定 9：upstream `Api.SystemManage.{Role,Menu}` 對 `Api.RoleAdmin.RoleRecord`／`Api.MenuAdmin.MenuRecord` 之欄差集自 wire-schema 快照機器導出、釘於同檔常數、漂移即紅（四類植入反例各紅）。
- base-web 之 upstream `fetchGetUserList`（`src/service/api/system-manage.ts`，經 barrel `@/service/api` 匯出；`src/service-alova/api/system-manage.ts` 另有同名一份）以 `Api.SystemManage.UserList`（列＝`Api.SystemManage.User`）宣告 `GET /systemManage/getUserList` 之回應。本刀註冊該路由；wire 權威型＝本刀 ADAPT 新型檔 `src/typings/api/rev6-user-admin.d.ts` 之 `Api.UserAdmin.UserRecord`（Q14：沿 rev6 欄名；Q13 與 spec FR-005：列帶持有角色之 id、代碼與名稱）。
- upstream `Api.SystemManage.User`（2026-10-05 自 `rust-api/server/tests/fixtures/wire-schema.json` 現讀）＝`Api.Common.CommonRecord`（`id`〔number〕、`createBy`、`createTime`、`updateBy`、`updateTime`〔皆 string〕、`status`〔`'1' | '2' | null`〕）＋`userName`、`nickName`、`userPhone`、`userEmail`（皆 string、非可空）、`userGender`（`'1' | '2' | null`）、`userRoles`（string 陣列＝角色代碼集）；十二欄皆必出。
- upstream 函式之畫面消費者（2026-10-05 `grep -rn fetchGetUserList base-web/src` 現算）＝兩支：`src/views/manage/user/index.vue`（本刀改線、spec FR-047）與 `src/views/plugin/excel/index.vue`（upstream 原檔、零 fork-delta 標記、不在本刀 ★ 軌道登記表；seed 選單 `plugin_excel`〔`sys_menu` 列 32〕只授 R_SUPER〔`casbin_rule` 列 101〕）；`service-alova` 之同名函式零畫面消費。excel 示範頁讀六欄（`userName`／`userGender`／`nickName`／`userPhone`／`userEmail`／`status`）、以 `size: 999` 一次取；本刀前其請求回 `4040`（路由未註冊）、本刀後回真資料。
- `rev5:007` 未改 excel 示範頁、其清單 wire 之六欄與 upstream 同名 ⇒ 22080 該頁本即顯示真資料；rev5 清單之 `size` 上界亦為 100。
- 使用者頁抽屜之角色下拉現經 upstream `fetchGetAllRoles`（`Api.SystemManage.AllRole[]`）；rev6 getAllRoles 之 wire 與 upstream `AllRole` 結構全等（`wire_schema.rs` 之 `all_role_serialization_matches_upstream_all_role` 直判）＝零偏離、不入本帳；本刀抽屜改取 `src/service/api/rev6-role-admin.ts` 之同名函式（spec FR-053 擇一）。

## 決策驅動因子

- §I.3 型別謊言帳本：同一 URL 有兩份宣告型時，差在哪裡要有機器真源、漂移要紅。
- 偏離帳之機器形沿 005 刀既有件（比對器、釘值結構、四類植入反例），不另造第二套。
- 本刀 ★ 軌道授權面不為示範頁擴列（最小授權面；spec FR-054：base-web 變更檔集 ⊆ 授權檔集＋新增檔）。
- 與 rev5 HEAD 之 CDP 對照零差：既有示範頁之可見行為不因本刀分岔。

## 考慮過的替代案

1. **rev6 清單列對齊 upstream 欄名與形**（`createBy`／`createTime`…、`userRoles` 為代碼字串陣列）：翻 004 刀起之 rev6 審計欄名慣例（ADR-00044 決定 9 同判）；角色欄須帶 id 與名稱供灰色保留選項（Q13）、純代碼陣列承載不了；棄。
2. **改寫 upstream `Api.SystemManage.User` 宣告為 rev6 形**：修改 upstream 凍結 typings 檔＝修改型 fork-delta、不在本刀授權面，且動到 rebase 最熱之型別面；棄。
3. **excel 示範頁改線 rev6 包裝**：須 Amendment 新增管理頁軌道用途並擴 ★ 軌道登記表一列；該頁所讀六欄於 rev6 型皆同名（決定 3）、rev5 HEAD 同形未改＝CDP 零差；改線之收益只在型別宣告面；棄。
4. **不立帳（隱性偏離）**：違 §I.3；棄。

對所選方案跑同一反例（RL-0013）：替代案 3 之疑慮「不改 excel 示範頁，該頁是否靜默顯示錯欄或空欄」對所選形是否成立？不成立於欄名面——該頁所讀六欄皆為兩型共有欄（不在本帳釘值之 upstream 獨有欄集，決定 1、3），差異只在可空性（暱稱、手機、信箱為 null 之列該格空白）與 `size: 999` 經伺服端收斂為上界 100（`envelope::PAGE_MAX_SIZE`）＝至多顯示與匯出依 id 升冪之前 100 列——兩者皆與 rev5 HEAD 同形。對替代案 1 跑同一反例（欄名對齊 upstream 是否即零偏離）：仍有可空性與角色欄形之差，零偏離不可得、只是把偏離自欄名移到型別。成立。

## 決定

1. **偏離帳第三列**：upstream `Api.SystemManage.User`（getUserList 回應列之 upstream 宣告；比對面專用、非受審型）對 `Api.UserAdmin.UserRecord`（本刀 wire 權威型、入受審名冊）。偏離類別（**實集以 wire-schema 快照之機器導出為準**；下列為依 spec FR-005 與快照現讀之舉例、非窮舉）：
   - ①**欄名差**：審計四欄 upstream `createBy`／`createTime`／`updateBy`／`updateTime` 對 rev6 `createdBy`／`createdAt`／`updatedBy`／`updatedAt`；rev6 額外欄 `sessionPolicy`、`userMemo`；角色欄 upstream `userRoles`（代碼字串陣列）對 rev6 `roles`（`Api.UserAdmin.UserRole[]`，元素＝｛`id`、`roleCode`、`roleName`｝）——兩側異名＝入兩向欄名差（元素形之差由欄名差承載、不另入型別差；機器形之比對只及共有欄）。
   - ②**可空性差**：upstream 非空而 rev6 可空（`nickName`／`userPhone`／`userEmail`）；upstream 可空而 rev6 非空（`status`）。
   - ③**必出性差**：upstream 十二欄皆必出；rev6 依本刀 contracts/wire-user-admin.md（`UserRecord` 各欄恆在場、可空欄以顯式 null 在場）＝預期零必出性差。
   - ④**值型差**：`userGender` upstream `'1' | '2' | null` 對 rev6 `string | null`（後端照 DB 值轉字串、不套狀態二值收斂；值域由寫端收斂維持＝ADR-00080 決定 4）。

   wire 行為零變化（本帳只記、不改 wire）。
2. **機器形（沿 ADR-00044 決定 9 之件）**：`rust-api/server/tests/wire_schema.rs` 之偏離帳表 `DEVIATION_LEDGER` 由兩列擴為三列；第三列之釘值四項（欄名集差兩向、共有欄 required 差、共有欄型別正規形差）字面由本刀首次抽取之 `field_deviation` 機器導出結果寫入、之後只隨拍板改——upstream rebase 改了 `Api.SystemManage.User`、或本刀 typings 改了 `UserRecord`，重抽後即紅；紅了先重審本 ADR 再改釘值。既有四類植入反例（rev6 型多帶一欄／upstream 基底欄改名／rev6 一欄改可缺席／rev6 一欄改值型）逐列套用、三列帳各打四類（upstream `User` 之基底分支同為 `CommonRecord`、含 `updateTime`）。`Api.SystemManage.User` 只入比對面、不入受審名冊；`Api.UserAdmin.*` 新型入受審名冊與完備性腿（spec FR-064；完備性腿之節前綴同批擴入 `Api.UserAdmin.`／`Api.UserCenter.`），並受表驅動之「序列化鍵集＝快照 properties 鍵集」斷言（ADR-00082 款 6）。
3. **消費面**：
   - **使用者管理頁改線**：清單（`src/views/manage/user/index.vue`）改取 `src/service/api/rev6-user-admin.ts` 之 `fetchGetUserList`、抽屜角色下拉改取 `src/service/api/rev6-role-admin.ts` 之 `fetchGetAllRoles`（皆直接路徑 import、不入 barrel；與 upstream 同名函式並存＝005 刀 `rev6-role-admin.ts` 前例）⇒ 本刀起使用者管理頁零 upstream 舊函式消費。
   - ★**excel 示範頁為殘存消費面（不改）**：`src/views/plugin/excel/index.vue` 續經 upstream `fetchGetUserList` 以 upstream 型消費 rev6 wire。其所讀六欄皆為兩型共有欄、同名同義；差異限於：暱稱、手機、信箱可為 null（表格與匯出該格空白）；`userGender` 之宣告型窄於 wire 寬字串（決定 1④；寫端只產 `'1'`／`'2'`／null）；`size: 999` 經伺服端收斂為上界 100＝至多顯示與匯出依 id 升冪之前 100 列。上述皆與 rev5 HEAD 同形＝CDP 零差。
   - upstream `fetchGetAllRoles` 自本刀起零畫面消費（其型 `AllRole` 與 rev6 零偏離、不入本帳）；`service-alova` 之同名 `fetchGetUserList` 維持零畫面消費。
4. **查詢參數型不立偏離列**：upstream `Api.SystemManage.UserSearchParams` 之六過濾欄（`userName`／`userGender`／`nickName`／`userPhone`／`userEmail`／`status`）與分頁兩欄（`current`／`size`）即 rev6 後端所收之六欄過濾與分頁參數（spec FR-007；§I.1 後端補齊前端已有之功能）——前提＝本刀契約之過濾參數名與之同名同義；前提不成立（rev6 查詢參數與 upstream 出現欄差）＝新增偏離列、以新 ADR 擴本帳。

## 後果

- §I.3 偏離帳自兩列成三列；wire 行為零變化。
- 現在式面勘誤（RL-0011）：`wire_schema.rs` 偏離帳表之「兩列」字面與其 doc、`all_role_serialization_matches_upstream_all_role` 之 doc 句「upstream 使用者頁抽屜仍以之消費」於抽屜改線後成假述——同批改；`src/views/manage/user/index.vue` 之 upstream import 隨改線消失。
- spec FR-008（plan 期修補後字面；射程收窄＝user 2026-10-05 plan 期親決）之射程＝使用者管理頁；excel 示範頁為本 ADR 決定 3 所記之殘存消費面（本 ADR 不自行重定 spec 射程）。
- 代價：偏離帳多一列、釘值隨 typings 改動需重審；excel 示範頁之型別宣告續與 wire 不一致（只限可空性與值型、欄名零差）。

## 翻案觸發器

- upstream rebase 改動 `Api.SystemManage.User`、`Api.SystemManage.UserSearchParams` 或 `fetchGetUserList` 之宣告 ⇒ 重抽、偏離帳轉紅、重審本 ADR。
- upstream `fetchGetUserList` 出現 excel 示範頁以外之新消費者、或 excel 示範頁改讀 rev6 型未有之欄 ⇒ 重審決定 3（改線或擴授權）。
- 本刀 `UserRecord` 之欄集或角色欄形變更（拍板）⇒ 同批改釘值。
- §I.3 偏離帳之形制改為全域開嚴格模式（ADR-00082 款 6 翻案）⇒ 併入重審。
