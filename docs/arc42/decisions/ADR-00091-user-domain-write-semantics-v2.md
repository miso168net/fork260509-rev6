---
id: "ADR-00091"
title: 部分更新語意（續行 ADR-00080）——決定 1～6、8 原文續行；決定 7 改寫：使用者編輯抽屜之會話政策呼叫被拒（更新呼叫已生效）後留原地重試時，`status`／`roleIds` 之改動判定改以已生效值為比對基準；決定 9 改寫：現在式面 ADR-00080 改指本 ADR、與本 ADR 轉 accepted 同顆
date: 2026-10-14
status: superseded
supersedes: ["ADR-00080"]
superseded_by: [ADR-00107]
provenance: "007-user-password-admin 之 U17 碼品質審查第 3 輪非 blocker 觀察 1（會話政策失敗後留原地重試、狀態與角色仍比對開抽屜時之列快照；rev5 同形）；user 2026-10-14 親決（AskUserQuestion 兩問：首問答「修」；主線更正改指代價〔現在式引用 74 處〕後重問、答「修，改指併入 U22」）；spec 刻意分岔登記表「抽屜會話政策被拒後之重試」列；tasks T115（U18c）與 T103（U22：轉 accepted 與改指）；被續行面＝ADR-00080 全九決定（body 已 accepted 不可變、rev6 無部分翻案機制＝ADR-00011 決定 5 先例；續行鏈 ADR-00015→ADR-00047→ADR-00080→本 ADR）；前代出處＝rev5:src/views/manage/user/modules/user-operate-drawer.vue（狀態與角色恆比對開抽屜時之列、會話政策另打其端點）"
tags: [wire, envelope, serde, role-menu-crud, user-password-admin]
---

## 背景

- ADR-00080 決定 7 定：使用者編輯抽屜送 updateUser 時，`status`／`roleIds` 只在異於開啟時回填值才帶；updateUser 與會話政策為兩支獨立呼叫，前者成功而後者被拒時前者已生效、抽屜留原地供重試。兩句合讀＝留原地重試時，狀態與角色之「改動」仍以開啟時之值為基準。
- 本刀 U17 碼品質審查（第 3 輪）指出其後果：超管同時改狀態與會話政策，更新成功而會話政策被拒後，若於抽屜把狀態改回開啟時之值再確定，狀態因等於開啟時值而不送、畫面仍出「更新成功」，帳號實際維持已生效之新值——成功提示與結果相悖（rev5 HEAD 同形）。
- user 2026-10-14 親決修正，並定本 ADR 轉 accepted 與現在式面改指併入本刀 U22 之 ADR 顆、與 ADR-00081／ADR-00082 同批（同形前例：ADR-00082 款 1 之解除於本刀 U18 先落碼、U22 轉 accepted）。
- ADR body 已 accepted 不可變（GT-04）、rev6 無部分翻案機制（ADR-00011 決定 5）⇒ 整顆續行；決定 1～6、8 原文續行，以免被取代者成為現行條文之唯一出處。
- 現在式面量測（2026-10-14；只供背景、施工以決定 9 之指令現算為準）：外層 3 檔 5 處（`docs/arc42/05-building-block-view.md` 1、`docs/arc42/08-crosscutting-concepts.md` 3、`docs/ops/NOTES.md` 1）；rust-api 10 檔 64 處（`server/src/handler/common.rs` 6、`server/src/handler/menu.rs` 5、`server/src/handler/role.rs` 6、`server/src/handler/system_settings.rs` 8、`server/src/handler/user.rs` 20、`server/src/model/facade/sys_menu.rs` 4、`server/src/model/facade/sys_role.rs` 3、`server/tests/contract.rs` 2、`server/tests/fixtures/wire-schema.json` 5、`server/tests/wire_schema.rs` 5）；base-web 3 檔 5 處（`src/typings/api/rev6-menu-admin.d.ts` 2、`src/typings/api/rev6-role-admin.d.ts` 2、`src/typings/api/rev6-user-admin.d.ts` 1）。

## 決策驅動因子

- 成功提示 MUST 與結果相符：「更新成功」不得在使用者要求之狀態或指派未落地時出現。
- ADR-00080 決定 7 之其餘語意不變：未改即不送、缺席＝不動、他人於開抽屜期間之狀態與指派改動不被開啟時舊值蓋回；五恆送欄後送出者為準。
- 修正只動前端抽屜；後端寫端語意（缺席早退＋值 diff、指派期望全集）零變化。

## 考慮過的替代案

1. **維持 ADR-00080 決定 7 現行形**（rev5 同形）：成功提示與結果相悖之形續存；user 2026-10-14 取修正；棄。
2. **會話政策被拒即關抽屜**（迫使重開以取得新回填值）：失去「就地重試會話政策」、須重新輸入會話政策之改動；違 ADR-00080 決定 7「抽屜留原地供重試」之現行操作形；棄。
3. **部分成功後就地重新回填整張表單**（等同重開）：使用者為重試而保留之會話政策改動被一併重置；棄。
4. **updateUser 與會話政策合併為單一原子端點**：屬 wire 契約與後端寫端之拍板級變更、非本刀射程；棄。

對所選方案跑同一反例（RL-0013）：「他人並行改動不被開啟時舊值蓋回」於所選形是否仍成立？成立——比對基準只在本抽屜之 updateUser 成功時改為該次送出之值（即本抽屜自己剛寫入、已生效之值）；他人於其間之改動不被讀回、亦不被本抽屜覆寫：狀態與指派仍只在異於基準時才帶、未改即不送。「成功提示與結果相符」於所選形成立：部分成功後改回原值＝異於已生效值＝照送。替代案 2 之「失去就地重試」對所選形不成立：抽屜仍留原地、會話政策之改動保留。成立。

## 決定

本 ADR 續行並將 supersede ADR-00080（本 ADR accepted 那一顆同批補 `supersedes: ["ADR-00080"]`、ADR-00080 之 status 改 superseded；`superseded_by` 由 `python3 tools/docsync generate` 回填）。ADR-00080 決定 1～9 一律對應本 ADR 同號決定；決定 1～6、8 原文續行，決定 7、9 改寫。

1. **解析層與 wire 型別對應（ADR-00080 決定 1 續行）**：原文續行——NOT NULL 欄之顯式清空＝拒收、nullable 欄之顯式 null＝落 NULL；解析層承載形＝`Option<Option<T>>`＋`#[serde(default)]`＋`handler/common.rs` 之泛型 `tristate`；必填欄亦以寬鬆形承載、缺席或 null 由 handler 判 `2222`（不落框架 400／422 裸 body）；寫端 body 取用經 `common::json_or_default`；wire 型別對應與讀端 NULL 表示逐域以各刀契約為準。使用者域：updateUser 之可空欄（`nickName`／`userGender`／`userPhone`／`userEmail`／`userMemo`）與不可變欄 `userName` 以 `tristate` 承載（`userName` 之承載只為判出現與否）；寫端 typings 之 nullable 三態欄為 `T | null` 可選欄、讀端清單列之 NULL 表示依本刀 contracts/wire-user-admin.md。

2. **envelope 級三態與空字串逐域明文（ADR-00080 決定 2 續行）**：部分更新請求 body 之每一可選欄——欄位缺席＝不動；JSON `null`＝顯式清空；有值＝設值；空字串語意逐域：
   - **系統設定寫端**：空字串＝設值（落空字串）——續行、行為零變化。
   - **角色與選單寫端**：原文續行——可空文字欄空字串＝清空落 NULL（與 null 同）；NOT NULL 名稱欄（`roleName`／`menuName`）之 null 或空字串＝`nameRequired`；可空非文字欄之 null＝清空落 NULL；非三態欄之 null＝缺席（兩域之 `status`、新增路徑之 `menuType`、選單之 `parentId`）；選單之 `iconType` 為三態狀態類欄、null＝清空落 NULL。
   - ★**使用者寫端**（本刀新增；Q16）：可空文字欄（`nickName`／`userPhone`／`userEmail`／`userMemo`）之空字串＝清空落 NULL（與 null 同）、**新增與更新同形**；空字串＝恰零長字串（純空白不算空、不 trim；`common::blank_to_none` 只套內層、不得套在外層缺席判定）；清空之信箱不經格式守門、不參與現役唯一判定。`userGender` 為可空非文字欄：null＝清空落 NULL、值域收斂見決定 4。非三態欄之 null＝缺席：`status`、`roleIds`（null 不表「清空指派」；清空＝空陣列，決定 6）。`userName` 為 NOT NULL 不可變欄（決定 3）。
   - ★**會話政策寫端**（`updateUserSessionPolicy`；本刀新增）：非部分更新、單欄必給；`sessionPolicy` 為 NOT NULL 三值欄（`inherit`／`single`／`multi`），缺席、null、空字串與其餘值域外一律 `2222 biz.user.sessionPolicyInvalid`（無清空語意）。

3. **提前 no-op 與值 diff（ADR-00080 決定 3 續行）**：
   - **角色與選單寫端**：原文續行——除 `id` 外之一切欄（含不可變欄）經值域收斂後皆缺席＝提前 no-op（成功、零變更、零稽核、不 bump 時戳），位於交易之前、零觸庫；不可變欄只要出現（不論值、含 null）即不屬缺席、依各域守門拒（`codeImmutable`／`routeNameImmutable`／`menuTypeImmutable`）；非字串值＝body 壞形、部分更新型收斂為零變更成功；★同值出現照寫、照落 `update` 稽核、bump 時戳（不做值 diff）。
   - ★**使用者寫端 updateUser**（本刀；Q15）＝**缺席早退＋值 diff**：
     - ①**全缺席**（除 `id` 外一切欄經值域收斂後缺席）＝成功、零寫入、零稽核、不 bump 時戳；★位次在固定序⑤之首——請求上下文（缺席＝`5000`、先於一切）→①活性標的鎖讀（不存在或已軟刪＝`biz.user.notFound`）→②seed 保護→③本人規則→④包含規則照判，其後才早退；不另開早於①之捷徑（替代案 4）。
     - ②**有欄出現**：於鎖內以出現之欄經值域收斂與歸一（空字串＝NULL、`userGender` 值域外＝缺席、`roleIds` 去重後以集合比）後逐欄比對現值——全等＝no-op（零寫入、零稽核、`updated_at`／`updated_by` 不動、零撤票、零會話事件）；任一不等＝寫入出現之欄＋審計欄成對寫、稽核 `update` 恰一列（前後快照）；指派實際變更（差集非空）亦屬變更、同樣成對寫審計欄。
     - ③**no-op 不省鎖**：值 diff 在鎖內，同值請求照取固定序之全部鎖（per-user advisory、使用者列、角色列；spec FR-011）、只是零寫入——no-op 不成為繞過①～④之捷徑。
     - ④**守門先於值 diff**：本人之 `status`／`roleIds` 出現即拒、值不比對（同值亦拒；③先於⑤）；`roleIds` 含不存在或已軟刪之 id＝整筆 `biz.user.roleNotFound`；信箱格式與現役唯一（不分大小寫）照判。
     - ⑤**不可變欄** `userName`：出現（含 null、值同現值亦然）即 `biz.user.userNameImmutable`（位次⑤、早於值 diff；沿 `codeImmutable` 形）。
     - ⑥**停用之撤票觸發**＝狀態值經值 diff 判定實際變更、且新值非啟用（spec FR-026）；同值提交零撤票。
   - ★**會話政策寫端**（本刀）：值 diff 同形——固定序①～④照判（②③為空格）後，值域判定（決定 2）通過者與現值比：同值＝零寫入、零稽核、不 bump 時戳；異值＝寫入＋審計欄成對＋稽核 `update` 一列；改為 `single` 不即時踢除（下次登入生效；spec FR-018）。
   - **射程界**：值 diff 只及 updateUser 與 updateUserSessionPolicy；其餘使用者寫端（addUser、deleteUser、batchDeleteUser、restoreUser、kickUser、resetUserPassword）與 unlockLogin 非部分更新，通過守門即依其契約寫入與稽核（例：unlockLogin 對未鎖之標的照回成功並落一列 `unlock`＝GR3）。

4. **狀態類欄（ADR-00080 決定 4 續行）**：恰二值嚴格解析（trim 後 `"1"`／`"2"`；共用件 `common::wire_two_value_to_db`）；值域外（含空字串）＝缺席——新增取預設、更新不動、清單不篩選。不取整數解析之寬鬆形（孤兒狀態值會使畫面與授權各說各話）。使用者域：`status`（null＝缺席；新增缺席或值域外取預設啟用）；`userGender` 為三態狀態類欄、與選單 `iconType` 同形——null＝清空落 NULL、恰 `'1'`／`'2'`＝設值、值域外（含空字串）＝缺席（新增落 NULL、更新**不動**，非清空：打錯一個值不得變成清掉一個欄）。讀向之狀態欄沿 `common::db_status_to_wire`（DB 恰 1＝`'1'`、其餘＝`'2'`；DB 面無 CHECK、授權讀面只認 1）。

5. **射程（ADR-00080 決定 5 續行）**：部分更新請求 body＋角色、選單與**使用者新增請求**之可空文字欄空字串形（空字串＝NULL、防並存）；query 參數除狀態類欄之值域收斂（值域外＝清單不篩選）與篩選欄空字串＝不篩選外不在射程；非部分更新之寫端（如 `updateRoleHome`＝`home` 缺席、null 或空字串皆清空、同值亦寫；`updateUserSessionPolicy`＝決定 2、3）以其契約為準。逐域欄級三態表住各刀契約（本刀＝contracts/wire-user-admin.md）。

6. **使用者指派欄 `roleIds`（ADR-00080 決定 6 續行；spec FR-013、Edge Cases「角色 id 界外」）**：期望全集、全量替換——缺席或 null＝指派不動（包含規則之 N＝T）；陣列＝寫後角色集恰等於其去重集合；含不存在或已軟刪之角色 id＝整筆拒 `biz.user.roleNotFound`（非靜默略過）；停用而未刪之角色為合法成員（抽屜之灰色保留選項＝Q13、spec FR-020）；空陣列＝全撤；差集以硬刪＋新增同交易落地；同集合（異序、重複）＝屬同值（決定 3②）。addUser 之 `roleIds` 缺席或 null＝零角色。★與三維授權寫端之候選集射程（ADR-00066 決定 2／4：候選外靜默略過、候選外現役列不撤不授）刻意不同——授權寫端之期望集是在候選全集內勾選，指派寫端之期望集即指派主體本身。角色列之鎖（固定序①之後、②之前對 T∪N 去重升序 `FOR UPDATE`、鎖內重驗未軟刪；addUser 只鎖 N；spec FR-011）先於值 diff；包含規則之 N 與⑤之存在判定皆取同一鎖內結果（鎖內構 N、不信 pre-read＝ADR-00075 決定 1）。

7. **並行編輯已知態與部分成功後之比對基準（ADR-00080 決定 7 改寫：比對基準句；本刀 U17 碼品質審查觀察）**：使用者編輯抽屜送 updateUser 時，`status`／`roleIds` 只在異於**比對基準**才帶——比對基準＝開啟時回填值；★本抽屜之 updateUser 成功而其後之會話政策呼叫被拒（抽屜留原地供重試）時，比對基準改為該次 updateUser 已送出之 `status`／`roleIds`（＝已生效值；該次未送出之欄維持原基準）、會話政策只在改動時另打 updateUserSessionPolicy（且只對超管；非超管該欄停用），而暱稱、性別、手機、信箱、記事五欄恆送開啟時表單值；抽屜無版本比對、無衝突提示。⇒ 兩位管理員（或同一帳號兩分頁）先後編輯同一帳號時：**恆送五欄＝後送出者為準**（先送出者之改動被以開啟時舊值靜默覆寫）；狀態與指派不受舊值覆寫（未改即不送、缺席＝不動）。另：抽屜之 updateUser 與會話政策為兩支獨立呼叫、非原子——前者成功而後者被拒時前者已生效（抽屜留原地供重試、清單刷新呈現已生效之改動）；重試時把狀態或角色改回開啟時之值＝異於已生效值＝照送（不得出現「狀態未送出卻提示成功」之形：rev5 HEAD 同形者，本刀改正、入 spec 刻意分岔登記）。
   - 觀察路徑＝Super 於兩分頁開同一自建帳號之編輯抽屜→分頁乙改暱稱並確定→分頁甲（未重開）只改手機並確定⇒暱稱回到開啟時舊值、兩列稽核 `update`、前端只顯成功；對照腿＝分頁乙改為停用並確定→分頁甲（未重開、表單仍顯啟用）只改記事並確定⇒帳號仍停用（甲之請求不帶 `status`）。驗收形＝本刀 CDP 實測（rev6 側網路請求事件斷言甲之 updateUser body 含五恆送欄、不含 `status`／`roleIds`）；22080 側同形＝零差。本刀實測相符：主腿＝暱稱回到開啟時舊值、兩列 `update` 稽核；對照腿＝甲之 body 鍵集＝`id` 與五恆送欄、帳號維持停用、兩列 `update` 稽核、兩頁只顯成功（32080 單邊；22080 側以 rev5 凍結碼靜態對賬、未於 22080 寫入）。
   - 部分成功腿（本 ADR 新增）＝Super 開自建帳號（啟用）之編輯抽屜→改為停用並改會話政策→確定、令會話政策那支回錯（CDP 攔截該請求）⇒帳號已停用、抽屜留原地→把狀態改回啟用並確定⇒該次 updateUser body 含 `status`（啟用）、帳號恢復啟用；22080 側＝body 不含 `status`、帳號維持停用（刻意分岔）。本刀實測相符（32080 單邊）：首輪 updateUser 帶 `status`＝`'2'` 回 `0000`、會話政策那支被攔成 `5003` 後只出錯誤提示、抽屜留原地、帳號已停用；改回啟用再送＝updateUser 帶 `status`＝`'1'`、會話政策照打且 `0000`、出成功提示、帳號啟用且會話政策已改；22080 側以 rev5 凍結碼靜態對賬（狀態比對開抽屜時之快照）。
   - 翻案觸發器：抽屜改為只送異於回填值之欄、或 updateUser 引入樂觀鎖（版本欄或更新時戳比對）、或 updateUser 與會話政策合併為單一原子端點、或誤蓋實際發生被回報。

8. **逐域差異表（ADR-00080 決定 8 續行；單一出處）**：請求上下文缺席＝`5000` 拒寫、先於一切守門與早退（各域同）。

   | 面 | 系統設定寫端（002 刀） | 角色與選單寫端（005 刀） | 使用者寫端 addUser／updateUser（本刀） | 會話政策寫端（本刀） |
   |---|---|---|---|---|
   | 可空文字欄之空字串 | 設值（`description` 落空字串） | 清空落 NULL（新增同形） | 清空落 NULL（新增同形） | 不適用（無可空欄） |
   | JSON null | nullable 欄落 NULL；`settingValue` null＝`2222` | nullable 欄落 NULL；名稱欄＝`nameRequired`；`status`／`menuType`／`parentId`＝缺席 | nullable 欄落 NULL；`status`／`roleIds`＝缺席；`userName` null＝出現即拒 | `sessionPolicy` null＝`sessionPolicyInvalid` |
   | 除 `id` 外全缺席 | 不適用（必填欄缺席＝`2222`） | 提前 no-op：交易前、零觸庫（`id` 查無亦成功） | 固定序⑤之首早退：①～④照判（查無或已軟刪＝`notFound`）、零寫零稽核 | 不適用（`sessionPolicy` 缺席＝`sessionPolicyInvalid`） |
   | 同值出現 | 照寫（審計欄重寫、列版本換新）、零稽核（系統設定寫端不落稽核） | 照寫、稽核 `update` 一列、bump 時戳 | 值 diff：零寫入、零稽核、不 bump 時戳 | 值 diff：同左 |
   | 不可變欄出現 | —— | `roleCode`／`routeName`／`menuType`（更新）即拒 | `userName`（更新）即拒 | —— |
   | body 缺席或壞形 | 收斂後必填欄缺席＝`2222` | 收斂為預設（`id` 0、全缺席）＝提前 no-op 成功 | 收斂為預設：updateUser＝`id` 0＝`biz.user.notFound`；addUser＝依其業務守門序首拒 | 收斂為預設（`id` 0）＝`biz.user.notFound` |
   | 集合欄 | —— | ——（三維授權寫端屬 ADR-00066：候選集射程、候選外略過） | `roleIds` 期望全集、界外整筆拒（決定 6） | —— |
   | 批次刪除之多重違規 | —— | 依該域契約（005 刀） | batchDeleteUser：固定序①～④逐步全批（①全批鎖讀〔`notFound`〕→②全批 seed 保護→③含本人→④逐筆包含規則；同一步全批判完才進下一步）、拒因由步序定、不指筆、整批 rollback——與 `rev5:007` 逐 id 交錯形於多 id 異類違規時可回不同鍵＝刻意差異（research R8） | —— |

9. **現在式面改指（ADR-00080 決定 9 改寫：改指對象與時序）**：現在式面引用 ADR-00080 之處改指本 ADR 同號決定（決定號一對一）；accepted ADR body 與史料面不動。判定＝`python3 tools/docsync errata ADR-00080` 全 repo 命中扣除史料面（brainstorms、specs、reviews）、生成鏡像（`docs/generated/`）、事件源與 ADR 檔（`docs/arc42/decisions/`；含本 ADR 自身——其對被續行者之引用屬續行面本身）；兩子庫以 `git -C <子庫> grep -o ADR-00080` 對賬；子庫只改註、走兩段式 commit；base-web `src/typings/api/*.d.ts` 之碼註即 wire-schema 快照 `description` 之料源（`tools/wire-schema.py check` 對重抽結果逐位元組比對）⇒ 型別檔碼註之改指連動快照重抽（`python3 tools/wire-schema.py extract`、需 dev stack）。★時序＝本 ADR 轉 accepted 之同一顆（本刀 U22 之 ADR 顆，與 ADR-00081／ADR-00082 之改指同批）；其前之現在式面續指 ADR-00080＝已知過渡態（其決定 7 之比對基準句自本刀 U18c 起與抽屜碼不符，同 ADR-00082 款 1 於本刀 U18～U22 間之形）。ADR-00080 決定 9 所定 ADR-00047→ADR-00080 之改指已於本刀 U14 完成、無續作。處數以施工時同指令現算、改完復掃（量測值住背景、不作施工基準）。

**款號對照表**：

| ADR-00080 決定 | 本 ADR 決定 | 處置 |
|---|---|---|
| 1 解析層與 wire 型別對應 | 1 | 原文續行 |
| 2 envelope 級三態與空字串逐域明文 | 2 | 原文續行 |
| 3 提前 no-op 與值 diff | 3 | 原文續行 |
| 4 狀態類欄 | 4 | 原文續行 |
| 5 射程 | 5 | 原文續行 |
| 6 使用者指派欄 `roleIds` | 6 | 原文續行 |
| 7 並行編輯已知態 | 7 | 改寫（比對基準句：部分成功後以已生效值為基準；新增部分成功觀察腿；翻案觸發器補「合併為原子端點」） |
| 8 逐域差異表 | 8 | 原文續行 |
| 9 現在式面改指（ADR-00047→ADR-00080） | 9 | 改寫（改指對象 ADR-00080→本 ADR、時序＝本 ADR 轉 accepted 同顆＝本刀 U22） |

- **親決紀錄**：user 親決 2026-10-14（本刀 U18 收尾期間；AskUserQuestion 兩問）——首問「會話政策失敗後重試之比對基準要不要修」答「修」；主線更正首問漏算之改指代價（現在式引用 74 處）後重問，答「修，改指併入 U22」。轉 accepted 時點＝本刀 U22 之 ADR 顆（tasks T103），依親決分類（RL-0086、ADR-00089）收尾。

## 親決分類

依 ADR-00089（RL-0086）；本 ADR 非 plan 期起草，依本刀 tasks T103 以親決分類收尾；類別定義同 ADR-00081 本節。

| 款 | 類別 | 出處或理由 | 白話一句 |
|---|---|---|---|
| 導言 | 工程 | 決定節導言之 supersedes 與被續行者 status 屬 accepted 同顆簿記（GT-04） | 本 ADR 轉 accepted 時一併取代 ADR-00080。 |
| 決定 1 | 承決 | ADR-00080 決定 1 原文續行 | 欄位缺席、null、有值三態的解析方式不變。 |
| 決定 2 | 承決 | ADR-00080 決定 2 原文續行 | 空字串與 null 的意思逐域寫明，不變。 |
| 決定 3 | 承決 | ADR-00080 決定 3 原文續行 | 使用者寫端同值提交不寫、不記稽核，不變。 |
| 決定 4 | 承決 | ADR-00080 決定 4 原文續行 | 狀態類欄只認兩個值，不變。 |
| 決定 5 | 承決 | ADR-00080 決定 5 原文續行 | 三態規則適用的範圍不變。 |
| 決定 6 | 承決 | ADR-00080 決定 6 原文續行 | 角色指派以送來的全集為準，不變。 |
| 決定 7 | 承決 | ADR-00080 決定 7（並行編輯已知態原文續行）；user 2026-10-14 AskUserQuestion 親決（首問「修」）；spec 刻意分岔登記表「抽屜會話政策被拒後之重試」列 | 並行編輯時暱稱等五欄後送出者為準（已知態、不變）；會話政策被拒後重試，改以已生效的狀態與角色為比對基準。 |
| 決定 8 | 承決 | ADR-00080 決定 8 原文續行 | 各域差異對照表不變。 |
| 決定 9 | 承決 | user 2026-10-14 AskUserQuestion 親決（重問「修，改指併入 U22」）；改指施工法屬工程 | 引 ADR-00080 的地方改指本 ADR，與本 ADR 轉 accepted 同一顆。 |

- **親決紀錄（轉 accepted）**：依 ADR-00089（本 ADR 非 plan 期起草、依 007 刀 tasks T103 以親決分類收尾；2026-10-15）。分類＝本表 10 列：承決 9、工程 1（導言，依核對觀察增列）；待決 0（決定 7、9 為 2026-10-14 親決之承決）。獨立核對（決定 5）首輪：升待決 0、改正 1 列（決定 7 出處補 ADR-00080 決定 7、白話補已知態半）；改正後復核（決定 6②）相符。決定 7 兩腿與部分成功腿於本刀 U22 補跑 CDP 實測相符（user 2026-10-15 放行補跑）。對照表收尾一題（與 ADR-00081 共用）答「照表定稿（建議）」、拉出 0 款。

## 後果

- 前端：使用者編輯抽屜於 updateUser 成功、會話政策被拒後之重試，以已生效值為狀態與角色之比對基準（tasks T115＝本刀 U18c）；spec 刻意分岔登記「抽屜會話政策被拒後之重試」列。
- 後端零變化；決定 1～6、8 之機器錨（ADR-00080 後果段所列各項）不變、續由本刀既有釘案承載。
- ADR-00080 將整顆轉 superseded（本刀 U22）；續行鏈 ADR-00015→ADR-00047→ADR-00080→本 ADR，讀前三者須併讀本 ADR。
- 過渡態：本刀 U18c 至 U22 之間，現在式面續指 ADR-00080；其決定 7 之比對基準句與抽屜碼不符（同 ADR-00082 款 1 之形），U22 改指後消。
- 並行編輯已知態（決定 7）續入 CDP 排除清單之「已知態各款」；部分成功腿入 CDP 對照（刻意分岔）。

## 翻案觸發器

- 沿 ADR-00080 翻案觸發器各款（角色或選單域改採值 diff、create 請求允許 null 表預設、採 PATCH 動詞或 JSON Patch、系統設定寫端重寫或出現清空 UI 需求、使用者表引入版本欄或狀態類欄 CHECK）——其所指 ADR-00080 決定改讀本 ADR 同號決定。
- 決定 7：見該決定之翻案觸發器。
