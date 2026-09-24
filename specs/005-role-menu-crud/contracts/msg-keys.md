# Contract — 本刀新增拒因鍵候選表（`biz.role.*`／`biz.menu.*`）

> 本檔只作**候選鍵表**（鍵名、發出點、語意要求、落地單元）；★譯文之家＝三檔 locale `backend` 子樹（`en-us.ts`／`zh-cn.ts`／`zh-tw.ts` 各為該語唯一權威，ADR-00039）——本檔不立譯文表、實作時譯文直接寫進三檔 locale。鍵集權威＝`rust-api/server/src/error.rs` 之 `MSG_KEYS`（鍵數以其型別長度為準）。
> 一切拒因皆 `2222`＋純 i18n key、一因一鍵、零攜參；新鍵 MUST 隨**首個發出它的單元**落地（`msg_key` 常數＋`MSG_KEYS` 尾端追加＋兩支名冊測試＋三檔 locale backend 子樹＋`app.d.ts` backend 型節同單元、兩 pin 同一顆外層 commit），且於 `tests/contract.rs` 真 seed 應用面實際發出（名冊雙向閘）。

## `biz.role.*`（10）

| 鍵 | 發出點 | 語意要求（譯文須傳達） |
|---|---|---|
| `codeInvalid` | addRole ① | 代碼只許字母、數字、底線、最長 64 字元 |
| `codeExists` | addRole ③④（先驗＋唯一索引兜底） | 代碼已被現役角色使用 |
| `codeImmutable` | updateRole ④ | 代碼建立後不可修改 |
| `notFound` | updateRole ③、deleteRole／batchDeleteRole（含查無 id）、getRoleHome、updateRoleHome | 角色不存在（含已刪） |
| `seededProtected` | deleteRole／batch ② | 系統內建角色不可刪除 |
| `inUse` | deleteRole／batch ③ | 角色仍有使用者掛載、不可刪除（誠實總掛載語意、不帶人數） |
| `cannotDeleteSelfRole` | deleteRole／batch ④ | 不可刪除自己帳號所屬之角色 |
| `cannotDisableSelfRole` | updateRole ⑤ | 不可停用自己帳號所屬之角色 |
| `superCannotDisable` | updateRole ⑤ | 超級管理員角色不可停用 |
| `nameRequired` | addRole ②、updateRole ② | 名稱不可為空（★涵蓋 null 與空字串；英文不得只寫 "must not be null"） |

## `biz.menu.*`（14）

| 鍵 | 發出點 | 語意要求 |
|---|---|---|
| `notFound` | updateMenu ③、deleteMenu／batch（含查無 id）、restoreMenu ①（含現役列） | 選單不存在（或不在可操作狀態） |
| `routeNameExists` | addMenu ③⑥⑩（⑥＝保留路由名、ADR-00044 決定 8） | 路由名已被使用（現役選單或系統保留路由） |
| `routeNameImmutable` | updateMenu ④ | 路由名建立後不可修改 |
| `menuTypeImmutable` | updateMenu ④ | 選單類型建立後不可修改 |
| `parentNotFound` | addMenu ①、updateMenu ⑥、restoreMenu ③ | 父選單不存在或已刪除 |
| `cycleDetected` | addMenu ②、updateMenu ⑥ | 不可把選單移到自身或其子孫之下 |
| `hasChildren` | deleteMenu ③、batch | 選單下仍有子項、須先處理子項 |
| `protectedMenu` | deleteMenu ②、batch、updateMenu ⑤ | ★受保護選單**不可刪除、不可停用、不可變更父選單**——三種情形皆須涵蓋（前代「不可刪除」譯文不得照搬；零新鍵） |
| `constantParent` | addMenu ④、updateMenu ⑦（含清除常量性之後代腿）、restoreMenu ④ | 常量選單只能掛在常量父選單之下（清除常量性時亦受此約束） |
| `restoreConflict` | restoreMenu ② | 已有同路由名之現役選單、無法復原 |
| `nameRequired` | addMenu ⑦、updateMenu ② | 名稱不可為空（涵蓋 null 與空字串） |
| `routeNameInvalid` | addMenu ⑤ | 路由名只許字母、數字、底線、連字號、最長 100 字元 |
| `hrefInvalid` | addMenu ⑧、updateMenu ⑧ | 外連網址須以 http:// 或 https:// 開頭 |
| `buttonsInvalid` | addMenu ⑨、updateMenu ⑨ | 按鈕碼清單格式不正確（每項須有非空且不重複之碼、最長 100 字元） |

## 落地時序（工程判斷 24）

- 角色寫端單元（含 roleHome 讀寫兩支）：`biz.role.*` 全 10 鍵——`notFound` 首發於 getRoleHome／updateRole；讀端單元（六支）零新拒因鍵、不觸 locale。
- 選單 add／update 單元：`notFound`／`routeNameExists`／`routeNameImmutable`／`menuTypeImmutable`／`parentNotFound`／`cycleDetected`／`protectedMenu`／`constantParent`／`nameRequired`／`routeNameInvalid`／`hrefInvalid`／`buttonsInvalid`。
- 選單 delete／batch／restore 單元：`hasChildren`／`restoreConflict`（其餘鍵已在前單元落地、本單元只加發出點）。
- 前端頁面不直接引用 `backend.biz.*` 字面（拒因提示由共用攔截層轉譯）⇒ `FRONTEND_MSG_CONSUMERS` 仍恰 1 筆（BL-00074 不觸發）。
