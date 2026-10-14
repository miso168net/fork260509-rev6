---
id: "ADR-00080"
title: 部分更新語意（續行 ADR-00047）——系統設定與角色選單兩域續行；使用者域：可空文字欄空字串＝清空落 NULL（新增與更新同形）、缺席早退＋值 diff（同值零寫入零稽核、不 bump 時戳；早退位次在固定序⑤之首）、指派欄期望全集全量替換（界外整筆拒）；會話政策寫端值 diff 同形；並行編輯恆送欄後送出者為準（已知態）；逐域差異表
date: 2026-10-05
status: superseded
supersedes: ["ADR-00047"]
superseded_by: [ADR-00091]
provenance: "007-user-password-admin 之 spec FR-009、FR-012、FR-013、FR-016、FR-018、FR-020、FR-047、SC-003、US1 AS2／AS3、Edge Cases「使用者寫端」（空字串、同值 no-op、並行編輯、body 缺席或壞形、角色 id 界外）與刻意分岔登記表「可空文字欄之空字串」列；brainstorm §0 Q15（同值不寫不記＝非建議項）／Q16（空字串＝清空）／Q13（停用角色灰色保留）、§3 §1 ADR 待立⑦、§3 §2「no-op 與空字串」；並行編輯已知態之落點＝plan 期主線定案（spec Edge Cases 指 plan 期定）；被續行面＝ADR-00047 五款（body 已 accepted 不可變、rev6 無部分翻案機制＝ADR-00011 決定 5 先例；續行鏈 ADR-00015→ADR-00047→本 ADR）；前代出處＝rev5:server/src/model/facade/sys_user.rs（updateUser 全缺席早退＋值 diff no-op、指派實際變更亦成對寫審計欄）、rev5:server/src/handler/user.rs（`userGender` 值域外收斂為缺席、`status`／`roleIds` 之 null 與缺席同義、`userName` 出現即拒、守門固定序先於 facade 之早退）、rev5:src/views/manage/user/modules/user-operate-drawer.vue（狀態與角色只在改動時送、會話政策另打其端點）——其更新路徑不摺疊空字串之形（rev5:007 R2-1）由 Q16 翻；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [wire, envelope, serde, role-menu-crud, user-password-admin]
---

## 背景

- ADR-00047 決定 2 要求「空字串之語意逐域明文」，現行只列系統設定與角色選單兩域。本刀（007 user-password-admin）首度上線使用者寫端（addUser／updateUser）與會話政策寫端（updateUserSessionPolicy），使用者域之三態、空字串、no-op 與指派欄語意須有明文出處。
- user 拍板兩題與跨域現行約定不同形：Q15（非建議項）使用者域照 `rev5:007` as-built 採「缺席早退＋值 diff」——同值零寫入、零稽核、不 bump 時戳；角色選單域續 ADR-00047 決定 3（只認缺席、同值出現照寫照稽核）。Q16 可空文字欄之空字串＝清空落 NULL、新增與更新同形（翻 `rev5:007` 更新路徑不摺疊之形）。逐域差異須有單一出處（spec FR-013）。
- ADR body 已 accepted 不可變（GT-04）：只在活書或契約寫使用者域語意，會使 ADR-00047 之現行字面（決定 2 只列兩域、決定 3 為跨域通則）與現況相悖（權威鏈倒掛、RL-0047）；rev6 無部分翻案機制（ADR-00011 決定 5）⇒ 整顆續行。
- spec Edge Cases 之並行編輯已知態（抽屜之狀態與角色只在改動時送、其餘欄後送出者為準）指 plan 期定落點；其成因正是本 ADR 之寫端語意（恆送欄經值 diff 判「異」即寫），故入本 ADR（決定 7）。
- 現在式面量測（2026-10-05；只供背景、施工以決定 9 之指令現算為準）：`python3 tools/docsync errata ADR-00047` 全 repo 101 處命中；扣除史料面（brainstorms、specs、reviews）、生成鏡像（`docs/generated/`）、事件源與 ADR 檔（`docs/arc42/decisions/`）後，現在式面＝13 檔 50 處（逐檔 `grep -o`／`git -C <子庫> grep -o` 計）——外層 2 檔 4 處：`docs/arc42/05-building-block-view.md` 1、`docs/arc42/08-crosscutting-concepts.md` 3；rust-api 9 檔 42 處：`server/src/handler/common.rs` 6、`server/src/handler/menu.rs` 5、`server/src/handler/role.rs` 6、`server/src/handler/system_settings.rs` 8、`server/src/model/facade/sys_menu.rs` 4、`server/src/model/facade/sys_role.rs` 3、`server/tests/contract.rs` 2、`server/tests/fixtures/wire-schema.json` 4、`server/tests/wire_schema.rs` 4；base-web 2 檔 4 處：`src/typings/api/rev6-menu-admin.d.ts` 2、`src/typings/api/rev6-role-admin.d.ts` 2；`docs/ops/` 0 處。

## 決策驅動因子

- 同一欄不得有兩種「空」表示（沿 ADR-00047）；另：使用者信箱之現役唯一索引只收非 NULL 之 `lower(user_email)`——空字串若照值落庫，兩個「空信箱」帳號即撞索引。
- 管理員開抽屜未改即按確定，不得每次落一列稽核、bump 一次更新時間（Q15；使用者抽屜恆送暱稱、性別、手機、信箱、記事五欄）。
- 系統設定域與角色選單域行為零變化（002／005 刀釘案零改形）；逐域差異單一出處、逐格可指向機器錨。
- 語意判定在鎖內（lock-then-redecide、永不信 pre-read；spec FR-011）；no-op 不得成為繞過固定序守門之捷徑。

## 考慮過的替代案

1. **使用者域沿 ADR-00047 決定 3**（只認缺席、同值照寫照稽核）：跨域一致，但抽屜每次存檔即落稽核、bump 時戳；user 於 Q15 取值 diff（非建議項）；棄。
2. **全域改值 diff**（連角色選單域一併改）：改 005 刀契約與釘案、屬角色域稽核語意之拍板級變更（ADR-00070 翻案觸發器末款同義）、非本刀射程；棄。
3. **使用者域更新路徑不摺疊空字串**（`rev5:007` 形：清空只認 null、信箱空字串判格式錯、其餘落空字串）：同欄兩種空、與 upstream 表單清空輸入框即送空字串之實況相左；Q16 棄。
4. **全缺席早退置於①活性標的鎖讀之前**（角色選單域形、零觸庫）：使標的不存在或已軟刪之全缺席請求回成功，違 spec FR-016「對已軟刪標的之 updateUser 一律 `biz.user.notFound`」與 FR-009「body 缺席或壞形 → 標的不存在 → `biz.user.notFound`」；棄。
5. **指派欄沿 ADR-00066 候選集語意**（候選外靜默略過）：角色是指派主體、不是候選篩選；界外 id 靜默略過＝送出者以為已指派而實未落地（spec Edge Cases「角色 id 界外」）；候選集若取活性且啟用，持有之停用角色即「既移不掉也保不住」（ADR-00066 決定 3 禁止形同型）；棄。

對所選方案跑同一反例（RL-0013）：替代案 4 之「全缺席請求之回應依標的狀態而異」對所選形是否同樣成立？成立而方向正確——所選形令全缺席請求照跑①～④：標的不存在或已軟刪＝`biz.user.notFound`、受讓之非超管對持 R_SUPER 之標的＝`5003`；回應反映「此操作者對此標的有無寫權」，與非全缺席之同一請求同判、不因 body 為空而放寬；角色選單域之「id 查無亦成功」屬逐域差異（決定 8 表列）。替代案 5 之「送出者以為已指派」對所選形不成立：界外 id 整筆拒、零變更。成立。

## 決定

本 ADR 續行並將 supersede ADR-00047（本 ADR accepted 那一顆同批補 `supersedes: ["ADR-00047"]`、ADR-00047 之 status 改 superseded；`superseded_by` 由 `python3 tools/docsync generate` 回填）。ADR-00047 決定 1～5 一律對應本 ADR 同號決定；決定 6～9 為本刀新增。

1. **解析層與 wire 型別對應（ADR-00047 決定 1 續行）**：原文續行——NOT NULL 欄之顯式清空＝拒收、nullable 欄之顯式 null＝落 NULL；解析層承載形＝`Option<Option<T>>`＋`#[serde(default)]`＋`handler/common.rs` 之泛型 `tristate`；必填欄亦以寬鬆形承載、缺席或 null 由 handler 判 `2222`（不落框架 400／422 裸 body）；寫端 body 取用經 `common::json_or_default`；wire 型別對應與讀端 NULL 表示逐域以各刀契約為準。使用者域：updateUser 之可空欄（`nickName`／`userGender`／`userPhone`／`userEmail`／`userMemo`）與不可變欄 `userName` 以 `tristate` 承載（`userName` 之承載只為判出現與否）；寫端 typings 之 nullable 三態欄為 `T | null` 可選欄、讀端清單列之 NULL 表示依本刀 contracts/wire-user-admin.md。
2. **envelope 級三態與空字串逐域明文（ADR-00047 決定 2 續行＋擴寫）**：部分更新請求 body 之每一可選欄——欄位缺席＝不動；JSON `null`＝顯式清空；有值＝設值；空字串語意逐域：
   - **系統設定寫端**：空字串＝設值（落空字串）——續行、行為零變化。
   - **角色與選單寫端**：原文續行——可空文字欄空字串＝清空落 NULL（與 null 同）；NOT NULL 名稱欄（`roleName`／`menuName`）之 null 或空字串＝`nameRequired`；可空非文字欄之 null＝清空落 NULL；非三態欄之 null＝缺席（兩域之 `status`、新增路徑之 `menuType`、選單之 `parentId`）；選單之 `iconType` 為三態狀態類欄、null＝清空落 NULL。
   - ★**使用者寫端**（本刀新增；Q16）：可空文字欄（`nickName`／`userPhone`／`userEmail`／`userMemo`）之空字串＝清空落 NULL（與 null 同）、**新增與更新同形**；空字串＝恰零長字串（純空白不算空、不 trim；`common::blank_to_none` 只套內層、不得套在外層缺席判定）；清空之信箱不經格式守門、不參與現役唯一判定。`userGender` 為可空非文字欄：null＝清空落 NULL、值域收斂見決定 4。非三態欄之 null＝缺席：`status`、`roleIds`（null 不表「清空指派」；清空＝空陣列，決定 6）。`userName` 為 NOT NULL 不可變欄（決定 3）。
   - ★**會話政策寫端**（`updateUserSessionPolicy`；本刀新增）：非部分更新、單欄必給；`sessionPolicy` 為 NOT NULL 三值欄（`inherit`／`single`／`multi`），缺席、null、空字串與其餘值域外一律 `2222 biz.user.sessionPolicyInvalid`（無清空語意）。
3. **提前 no-op 與值 diff（ADR-00047 決定 3 逐域改寫）**：
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
4. **狀態類欄（ADR-00047 決定 4 續行＋使用者域）**：恰二值嚴格解析（trim 後 `"1"`／`"2"`；共用件 `common::wire_two_value_to_db`）；值域外（含空字串）＝缺席——新增取預設、更新不動、清單不篩選。不取整數解析之寬鬆形（孤兒狀態值會使畫面與授權各說各話）。使用者域：`status`（null＝缺席；新增缺席或值域外取預設啟用）；`userGender` 為三態狀態類欄、與選單 `iconType` 同形——null＝清空落 NULL、恰 `'1'`／`'2'`＝設值、值域外（含空字串）＝缺席（新增落 NULL、更新**不動**，非清空：打錯一個值不得變成清掉一個欄）。讀向之狀態欄沿 `common::db_status_to_wire`（DB 恰 1＝`'1'`、其餘＝`'2'`；DB 面無 CHECK、授權讀面只認 1）。
5. **射程（ADR-00047 決定 5 續行＋擴寫）**：部分更新請求 body＋角色、選單與**使用者新增請求**之可空文字欄空字串形（空字串＝NULL、防並存）；query 參數除狀態類欄之值域收斂（值域外＝清單不篩選）與篩選欄空字串＝不篩選外不在射程；非部分更新之寫端（如 `updateRoleHome`＝`home` 缺席、null 或空字串皆清空、同值亦寫；`updateUserSessionPolicy`＝決定 2、3）以其契約為準。逐域欄級三態表住各刀契約（本刀＝contracts/wire-user-admin.md）。
6. **使用者指派欄 `roleIds`（本刀新增；spec FR-013、Edge Cases「角色 id 界外」）**：期望全集、全量替換——缺席或 null＝指派不動（包含規則之 N＝T）；陣列＝寫後角色集恰等於其去重集合；含不存在或已軟刪之角色 id＝整筆拒 `biz.user.roleNotFound`（非靜默略過）；停用而未刪之角色為合法成員（抽屜之灰色保留選項＝Q13、spec FR-020）；空陣列＝全撤；差集以硬刪＋新增同交易落地；同集合（異序、重複）＝屬同值（決定 3②）。addUser 之 `roleIds` 缺席或 null＝零角色。★與三維授權寫端之候選集射程（ADR-00066 決定 2／4：候選外靜默略過、候選外現役列不撤不授）刻意不同——授權寫端之期望集是在候選全集內勾選，指派寫端之期望集即指派主體本身。角色列之鎖（固定序①之後、②之前對 T∪N 去重升序 `FOR UPDATE`、鎖內重驗未軟刪；addUser 只鎖 N；spec FR-011）先於值 diff；包含規則之 N 與⑤之存在判定皆取同一鎖內結果（鎖內構 N、不信 pre-read＝ADR-00075 決定 1）。
7. **並行編輯已知態（本刀新增；spec Edge Cases「並行編輯」之落點）**：使用者編輯抽屜（rev5 HEAD 形）送 updateUser 時，`status`／`roleIds` 只在異於開啟時回填值才帶、會話政策只在改動時另打 updateUserSessionPolicy（且只對超管；非超管該欄停用），而暱稱、性別、手機、信箱、記事五欄恆送開啟時表單值；抽屜無版本比對、無衝突提示。⇒ 兩位管理員（或同一帳號兩分頁）先後編輯同一帳號時：**恆送五欄＝後送出者為準**（先送出者之改動被以開啟時舊值靜默覆寫）；狀態與指派不受舊值覆寫（未改即不送、缺席＝不動）。另：抽屜之 updateUser 與會話政策為兩支獨立呼叫、非原子——前者成功而後者被拒時前者已生效（抽屜留原地供重試、清單刷新呈現已生效之改動）。
   - 觀察路徑＝Super 於兩分頁開同一自建帳號之編輯抽屜→分頁乙改暱稱並確定→分頁甲（未重開）只改手機並確定⇒暱稱回到開啟時舊值、兩列稽核 `update`、前端只顯成功；對照腿＝分頁乙改為停用並確定→分頁甲（未重開、表單仍顯啟用）只改記事並確定⇒帳號仍停用（甲之請求不帶 `status`）。驗收形＝本刀 CDP 三方對照單元實測（rev6 側網路請求事件斷言甲之 updateUser body 含五恆送欄、不含 `status`／`roleIds`）；22080 側同形＝零差。
   - 翻案觸發器：抽屜改為只送異於回填值之欄、或 updateUser 引入樂觀鎖（版本欄或更新時戳比對）、或誤蓋實際發生被回報。
8. **逐域差異表（本刀新增；單一出處）**：請求上下文缺席＝`5000` 拒寫、先於一切守門與早退（各域同）。

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

9. **現在式面改指（本刀新增）**：現在式面引用 ADR-00047 之處改指本 ADR 同號決定（決定號一對一）；accepted ADR body 與史料面不動。判定＝`python3 tools/docsync errata ADR-00047` 全 repo 命中扣除史料面（brainstorms、specs、reviews）、生成鏡像（`docs/generated/`）、事件源與 ADR 檔（`docs/arc42/decisions/`；含本 ADR 草稿自身——其對被續行者之引用屬續行面本身）；兩子庫以 `git -C <子庫> grep -o ADR-00047` 對賬；子庫只改註、走兩段式 commit。外層現在式面與 rust-api 碼註於本 ADR accepted 同批改指；★base-web `src/typings/api/*.d.ts` 之碼註即 wire-schema 快照 `description` 之料源（`tools/wire-schema.py check` 對重抽結果逐位元組比對）⇒ 該兩檔碼註之改指連動快照重抽（`python3 tools/wire-schema.py extract`、需 dev stack），排入本刀首個重抽快照之單元同批（時序以 tasks 為準）。同批改寫活書 08 §8.2 部分更新句（補使用者域與逐域差異之指針）。處數以施工時同指令現算、改完復掃（量測值住背景、不作施工基準）。

**款號對照表**：

| ADR-00047 決定 | 本 ADR 決定 | 處置 |
|---|---|---|
| 1 解析層與 wire 型別對應 | 1 | 續行（補使用者域承載形） |
| 2 envelope 級三態、空字串逐域明文 | 2 | 續行＋擴寫（使用者域、會話政策寫端） |
| 3 提前 no-op 與不可變欄出現形 | 3 | 逐域改寫（角色選單續行；使用者域與會話政策＝缺席早退＋值 diff） |
| 4 狀態類欄 | 4 | 續行＋擴寫（使用者域 `status`／`userGender`） |
| 5 射程 | 5 | 續行＋擴寫（使用者新增之可空文字欄） |
| —— | 6、7、8、9 | 新增（指派欄、並行編輯已知態、逐域差異表、現在式面改指） |

- **親決紀錄**：user 親決 2026-10-06（007 刀 tasks T003 施工前提顆）——本輪逐款一題一問呈決定節導言（併決定 1 一題）與決定 1～9（決定 9 併款號對照表）、皆照文定稿；零非建議項 ⇒ 決定節免改寫；`supersedes` 與 ADR-00047 之 status 依導言於本顆補改。

## 後果

- ADR-00047 整顆轉 superseded（accepted 同顆補 supersedes、改狀態；`superseded_by` 由 generate 回填）；續行鏈 ADR-00015→ADR-00047→本 ADR，讀前兩者須併讀本 ADR。
- 機器錨（本刀 tasks 逐條承載）：使用者寫端——可空文字欄空字串之新增與更新皆落 NULL；信箱空字串清空、不判格式錯；全缺席成功零寫零稽核，而對已軟刪標的之全缺席請求＝`notFound`；同值重送（含 `roleIds` 同集合異序）零寫入、零稽核、列版本不換；異值照寫且稽核恰一列；`userName` 出現（含 null、同值）即拒；本人送同值 `status` 即拒；`userGender` 值域外不動、null 清空；`roleIds` 界外整筆拒、null 不動、空陣列全撤、含停用角色照存；會話政策同值零稽核、值域外（含缺席、null、空字串）拒。系統設定域與角色選單域既有釘案零改形全綠。
- 刻意分岔（spec 刻意分岔登記表「可空文字欄之空字串」列）：API 層與 rev5 HEAD 不同、畫面零差（rev5 前端送出前已將空白轉 null）。
- 並行編輯已知態（決定 7）入 CDP 排除清單之「已知態各款」；審查輪遇之指向本 ADR 決定 7 即結案。
- 代價：部分更新之 no-op 口徑兩域不同（使用者域值 diff、角色選單域只認缺席）、讀契約須看域；換得使用者域抽屜存檔零噪音稽核。

## 翻案觸發器

- 角色或選單域欲改採值 diff（同值不寫不記）＝拍板級（連帶稽核語意；ADR-00070 翻案觸發器末款同義）⇒ 新 ADR 翻案本 ADR 決定 3 之該域半。
- create 請求允許 null 表「採預設值」等新語意 ⇒ 新 ADR 擴射程（沿 ADR-00047）。
- 採 PATCH 動詞或 JSON Patch（RFC 6902）取代 merge 語意 ⇒ 新 ADR 翻案（沿 ADR-00047）。
- 系統設定寫端被重寫、或其欄出現「清空」UI 需求 ⇒ 重評該域空字串語意是否向角色選單形收斂（沿 ADR-00047）。
- 使用者表引入版本欄或狀態類欄之資料庫 CHECK 約束（屬 DDL、拍板級）⇒ 複核決定 3、4、7。
- 決定 7：見該決定之翻案觸發器。
