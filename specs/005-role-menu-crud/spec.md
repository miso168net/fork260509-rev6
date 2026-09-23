# Feature Specification: 005 role＋menu 管理 CRUD 寫端——角色與選單接真、選單域序列化、判定面同步、授權歸檔寫入面、島 H 入憲

**Feature Branch**: `005-role-menu-crud`

**Created**: 2026-09-23

**Status**: Draft

**Input**: User description: "docs/brainstorms/005-role-menu-crud.md"（階段 0 brainstorm：定稿 `4dd28dc`＋grill 第一輪修訂 `8e3bc4d`＋grill 第二輪修訂 `d78fc3e`；範圍與 BACKLOG 承載五題 Q1～Q5、grill 第一輪四題 G1～G4、第二輪十二題 R1-Q1～Q10／R1-Q4b／R2-Q1 皆 user 拍板；既定不問 8 條與工程判斷 1～43 為主線報備、本 spec 直接採用；本 spec 之唯一輸入。該檔 §0 拍板紀錄與工程判斷、§1 rev5 承襲盤點、§2 BACKLOG 觸發項處置、§3 設計十節、§4 憲法九題預答、§5 specify 輸入摘要為權威來源；rev5 對應刀 `rev5:005-role-menu-crud` 之 spec 為沿用形藍本、rev6 座標改寫、翻案項以 brainstorm 為準）

> 摘要：把 upstream 的角色頁與選單頁自 demo 殼接成真——**17 支端點**（role CRUD 6＋menu CRUD 7＋roleHome 讀寫 2＋getMenuTree＋getAllPages；ROUTES 22→39、GET 7／POST 6／DELETE 4）、
> 前後端同刀、CDP 對照 rev5 驗收。同刀落地授權治理刀（006）要消費的三件底座：**選單域 advisory 序列化域**（含 deleteRole 家族入域）、**判定面同步**（全新重建後一步換上、失敗保留上一份、
> 絕不就地清空重載；觸發恰五支移除面寫端且以「實際歸檔 ≥1 列」為門）、**授權歸檔寫入面＋不可復原 reason gate**。憲法一次 MINOR（1.4.0→1.5.0）：島 H 五條入憲（H3 增補受保護選單不可停用、
> 不可改父）、§III.2 管理頁 ★ 軌道加用途 (ii)（恰九檔）、島 E 補兩句、兩條憲法簿記句改對。`MSG_KEYS` 19→43（拒因 24 鍵）。**零 migration、零 seed 變更**。
> 連帶面：IP 規則清單之分頁收斂至共用規則（wire 逐位元不變）、ILIKE 等共用件收攏與具型交易簽章、信任模型標頭名開機體檢（只告警）、IP 域與部分更新語意兩支 supersede ADR、
> BACKLOG 開放 41 條中 19 條隨本刀收、目標零新增。

## Clarifications

### Session 2026-09-23

- Q: 超管把一個常量選單改成非常量時，若它底下還有常量子選單（含停用、不含已刪），系統該怎麼回？ → A: 拒、回 `constantParent`——更新時若清除自身常量性，反查治理域全深後代（含停用、不含已刪），存任一常量後代即拒、同鍵零新鍵（承 rev5 as-built；島 H3 零繞道；超管須由下往上逐層改；FR-021、US2 場景 13、SC-004）。
- Q: 刪除角色時的「有人掛載」判定，要不要把已停用或已軟刪使用者身上的角色指派也算進去？ → A: 算進去、不濾——掛載數＝該角色之全部指派列、不看使用者啟停與軟刪，`others = total − 操作者是否為成員`；self-role 護欄同口徑（成員身分、含停用角色）；保守、零 join（承 rev5 as-built；007 做使用者軟刪寫端時 MUST 定「軟刪是否清指派」、記入 ADR③ 翻案觸發；FR-014、US1 場景 5）。
- Q: 批次刪除（角色或選單）的 id 清單裡若有任一 id 不存在或已刪，系統該怎麼回？ → A: 整批拒、回該域 `notFound`——查無亦屬違規，單一交易零變更零稽核；併發情境下前端重新整理列表再送（承 rev5 as-built；FR-037、US1 場景 6、US2 場景 11）。
- Q: 批次刪除的 id 清單裡同一個 id 出現兩次時，系統該怎麼處理？ → A: 先去重再處理——例 `[5,5]` 視同 `[5]`、成功、只落一列稽核；稽核列數＝去重後標的數（承 rev5 as-built；兩域同式；FR-037、SC-003、SC-004）。
- Q: 新增角色或新增選單時名稱送空字串，系統該怎麼回？ → A: 拒、回該域 `nameRequired`、零寫入——與更新路徑同式（brainstorm R1-Q3 之延伸；角色在代碼形制之後、活性唯一之前；選單在路由名形制之後）；翻 rev5 as-built（新增不驗名稱）、upstream 表單本即必填、UI 零差異（FR-012、FR-029、US1 場景 2）。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 超管管理角色全生命週期 (Priority: P1)

超級管理員在角色管理頁看到真實角色列表（分頁＋名稱／代碼模糊搜尋＋狀態篩選＋備註欄），可新增角色（代碼形制受驗、活性代碼唯一）、編輯角色（名稱／描述／狀態／備註；代碼不可變）、
刪除角色（受三層守門保護）、批次刪除（任一違規整批拒）。停用角色即令其成員自下一個請求起失去該角色的授權。

**Why this priority**: 角色是授權模型的軸心實體；沒有真實角色 CRUD，006 的三維授權治理與 007 的使用者角色指派都沒有操作對象。今日該頁為 demo 殼（讀端打不存在的端點、寫端假成功）。

**Independent Test**: 以 Super 登入 → 角色頁列表顯示 seed 三角色 → 新增一個角色 → 編輯其名稱、備註與狀態 → 刪除之 → 全程回應與列表刷新一致、每筆寫入恰一列操作稽核；以 Admin 身分直打 API：角色清單得通、寫端得 `5003`（Admin 無角色頁選單授權、UI 不可達）。

**Acceptance Scenarios**:

1. **Given** seed 三角色，**When** 超管開啟角色列表（首屏查詢串帶空白篩選欄），**Then** 分頁顯示三列、空白篩選欄＝不篩選；可依名稱／代碼（不分大小寫之子字串，`%`／`_`／`\` 視為字面）與狀態篩選；備註欄顯示於列表。
2. **Given** 新增抽屜，**When** 提交合形制之代碼與名稱，**Then** 回成功、列表出現新列、該角色零授權；**When** 提交與活性列重複之代碼，**Then** 拒（`biz.role.codeExists`）；
   **When** 代碼不合形制，**Then** 拒（`biz.role.codeInvalid`）；**When** 名稱為空字串，**Then** 拒（`biz.role.nameRequired`、Clarifications Q5）；**When** 兩個請求同時以同一代碼新增，**Then** 恰一個成功、另一個回 `codeExists`（不得落成系統錯誤）。
3. **Given** 既有角色，**When** 編輯只送部分欄位，**Then** 未送之欄不動；**When** 請求出現 `roleCode`（值相同亦同），**Then** 拒（`biz.role.codeImmutable`）；
   **When** 描述、備註或首頁路由名送空字串，**Then** 該欄被清空；**When** 名稱送 null 或空字串，**Then** 拒（`biz.role.nameRequired`）；**When** 除 id 外所有欄皆缺席（不可變欄亦未出現），**Then** 成功且零變更、零稽核。
4. **Given** 操作者自身所屬之角色，**When** 將其停用，**Then** 拒（`biz.role.cannotDisableSelfRole`）；**Given** R_SUPER，**When** 非其成員之操作者將其停用，**Then** 拒（`biz.role.superCannotDisable`）；**When** R_SUPER 成員（如 Super）將其停用，**Then** 先命中 `biz.role.cannotDisableSelfRole`（固定序 self→super）；
   **Given** 他人所屬之自建角色，**When** 停用成功，**Then** 該角色成員自下一個請求起失去該角色授權、無需任何判定面同步。
5. **Given** seed 角色（id 1／2／3），**When** 刪除，**Then** 拒（`biz.role.seededProtected`）；**Given** 測試直種之「有掛載使用者」自建角色（掛載者為停用或已軟刪使用者亦同），**When** 刪除，**Then** 拒（`biz.role.inUse`）；
   **Given** 操作者自身所屬之自建角色，**When** 刪除，**Then** 拒（`biz.role.cannotDeleteSelfRole`）——三層固定序 seeded→in-use→self-role。
6. **Given** 批次刪除集合含任一違規項，**When** 提交，**Then** 整批拒、零變更零稽核（單一交易、id 升冪逐項全套守門）；**When** 提交空陣列，**Then** 成功且零副作用、不取選單域鎖；**When** 清單含任一不存在或已刪之 id，**Then** 整批拒（`biz.role.notFound`）、零變更零稽核。
7. **Given** 無掛載之自建角色、其名下經測試直種三維政策列，**When** 刪除成功，**Then** 該角色全三維政策列（含 protected）同交易移入授權歸檔（reason＝`role_soft_delete`、不可復原）、同交易落操作稽核；
   角色刪除單向（無復原端點）；因實際歸檔 ≥1 列，commit 後觸發判定面同步（US4）。

---

### User Story 2 - 超管管理選單樹 (Priority: P1)

超級管理員在選單管理頁看到真實選單樹（治理域：未刪含停用；一次取全樹、備註欄），可新增目錄或選單（父選單自現有樹選擇、可寫按鈕碼清單與常量旗標）、編輯（改父受防環與父存在性驗證；
路由名與選單型別不可變；受保護選單不可停用、不可改父）、刪除（守門＋跨全角色授權連動歸檔＋判定面同步）、批次刪除（子先於父、整批拒）。

**Why this priority**: 選單域是島 H 的本體，也是 006 三維授權治理（選單維、按鈕維）的資料真源——按鈕碼候選集＝選單按鈕碼清單之聯集。與 US1 同為本刀 MVP。

**Independent Test**: 以 Super 登入 → 選單頁樹表顯示 seed 選單樹（seed 無停用列；治理域含停用之觀察以先停用一支自建選單後重查構造）→ 新增子選單（父選擇器取自選單樹、首項為頂層）→ 以 psql 對該自建選單直種顯式大 id 之選單維／按鈕維政策列 → 編輯其按鈕碼清單移除一碼 → 刪除之 → 守門、歸檔與稽核行為可由資料查證；
以受保護選單驗證停用與改父皆被拒。

**Acceptance Scenarios**:

1. **Given** seed 選單樹，**When** 開啟選單列表（不帶分頁參數），**Then** 回全部頂層及其全深子樹（治理域、含停用、不含已刪）、同層依排序值再依 id 排列、分頁列凍結呈現、備註欄顯示。
2. **Given** 新增或編輯彈窗，**When** 父選擇器開啟，**Then** 選項樹取自治理域、首項為合成之「頂層（無父）」節點；**When** 頁面下拉開啟，**Then** 選項＝顯示域路由名全集。
3. **Given** 新增，**When** 提交 `parentId=0`，**Then** 豁免父驗證；**When** 父不存在或已刪，**Then** 拒（`biz.menu.parentNotFound`；停用之父不擋）；**When** 路由名與活性列重複，**Then** 拒（`biz.menu.routeNameExists`；
   併發同鍵亦收斂為同一拒因）；**When** 路由名不合形制，**Then** 拒（`biz.menu.routeNameInvalid`）；**When** 常量選單欲掛於非常量父之下，**Then** 拒（`biz.menu.constantParent`）。
4. **Given** 新增或編輯，**When** 外連網址（href）非空且不以 `http://`／`https://` 起首（不分大小寫；例 `javascript:alert(1)`），**Then** 拒（`biz.menu.hrefInvalid`）、零寫入；**When** 送空字串，**Then** 視為清空。
5. **Given** 新增或編輯，**When** 按鈕碼清單不是 null 也不是陣列、或任一成員非物件、缺碼、碼為空、碼逾 100 字元、同清單內碼重複，**Then** 拒（`biz.menu.buttonsInvalid`）、零寫入、零歸檔。
6. **Given** 既有選單，**When** 編輯請求出現路由名或選單型別（值相同亦同），**Then** 拒（`routeNameImmutable`／`menuTypeImmutable`）；**When** 改父使祖先鏈成環（含上溯逾上限），**Then** 拒（`biz.menu.cycleDetected`）。
7. **Given** 選單 X 之按鈕碼清單含 `x:op`、該碼不屬其他任何未刪選單（含停用）、且存在測試直種之該碼按鈕維政策列，**When** 編輯移除該碼，**Then** 該碼之按鈕維政策同交易移入授權歸檔（reason＝`menu_button_removed`、不可復原）、commit 後觸發判定面同步；
   **Given** 該碼另被他選單持有，**When** 移除，**Then** 零歸檔、零同步。
8. **Given** 受保護選單（seed 8 列），**When** 編輯將其停用或變更其父選單，**Then** 拒（`biz.menu.protectedMenu`）；其餘欄照常可編。
9. **Given** 選單 Y 存在未刪子項（不論啟停），**When** 刪除 Y，**Then** 拒（`biz.menu.hasChildren`）；**Given** 受保護選單，**When** 刪除，**Then** 拒（`biz.menu.protectedMenu`；固定序：受保護→未刪子項）。
10. **Given** 無子項選單 Z 且測試直種跨角色選單維政策與 Z 獨有之按鈕碼政策，**When** 刪除成功，**Then** 選單維政策跨全角色歸檔＋獨有按鈕碼政策一併歸檔（兩者 reason 皆＝`menu_soft_delete`）、同交易稽核、commit 後觸發判定面同步；
    **Given** 零政策列之選單，**When** 刪除成功，**Then** 零歸檔、零同步。
11. **Given** 批刪集合內含父子，**When** 提交，**Then** 子先於父逐項全套守門、任一違規整批拒、單一交易；**When** 提交空陣列，**Then** 成功且零副作用、不取選單域鎖；**When** 清單含任一不存在或已刪之 id，**Then** 整批拒（`biz.menu.notFound`）、零變更零稽核。
12. **Given** 選單，**When** 編輯「隱藏於選單」旗標，**Then** 照常落庫（運行期由超管改值屬業務資料、非憲法 §I.2 所禁之隱藏治理手段）。
13. **Given** 常量目錄 A 底下有常量選單 B（含停用），**When** 編輯把 A 改為非常量，**Then** 拒（`biz.menu.constantParent`）；**When** 先把 B 改為非常量再改 A，**Then** 兩步皆成功（Clarifications Q1）。

---

### User Story 3 - 選單回收桶與復原 (Priority: P2)

超級管理員在選單頁切「顯示已刪除」開關，列表換源為已刪集合（常規分頁）；對已刪列執行復原——復原後選單回到未刪、原啟停狀態保留，但不回灌任何授權（可見性經 006 的授權面板重勾）。

**Why this priority**: 軟刪而無復原＝變相硬刪；但其價值依附於 US2 的刪除面，故次於 P1。

**Independent Test**: 對自建選單直種政策列後刪除之 → 開開關見其出現於已刪列表 → 復原 → 關開關見其回到樹中、狀態如刪前；被歸檔之授權不隨復原回灌。

**Acceptance Scenarios**:

1. **Given** 已刪選單若干，**When** 開啟開關，**Then** 列表換打已刪清單端點（依刪除時間新到舊、再依 id 新到舊）、操作欄整欄換為復原動作（無按鈕碼 gating；頁級授權＋復原守門重驗為唯一權威）、切換時清空勾選、每頁筆數歸位。
2. **Given** 已刪選單 W 與後建之同路由名活性選單，**When** 復原 W，**Then** 拒（`biz.menu.restoreConflict`；併發同鍵亦收斂為同一拒因）。
3. **Given** 已刪選單其父已刪，**When** 復原，**Then** 拒（`biz.menu.parentNotFound`）；**Given** 常量選單其任一祖先非常量，**When** 復原，**Then** 拒（`biz.menu.constantParent`）；非常量標的零驗祖先常量性。
4. **Given** 未刪（現役）選單，**When** 對其復原，**Then** 拒（`biz.menu.notFound`；不回冪等成功）。
5. **Given** 已刪選單 W 通過全部復原守門，**When** 復原，**Then** 成對清空軟刪時間與軟刪者、原狀態保留、零授權寫入、零判定面同步、同交易稽核。

---

### User Story 4 - 刪除後殘留授權即時失效（判定面同步） (Priority: P2)

管理員刪除選單、刪除曾被授權之角色、或自按鈕碼清單移除絕版碼後，被歸檔的授權在**判定面**即時失效——不會出現「資料庫已歸檔、記憶體殘留授權仍在生效」的窗；
同步失敗時系統保留上一份已知良好判定面並告警，絕不進入全域拒絕狀態。

**Why this priority**: 島 H2「同鍵重建零繼承」的記憶體面半邊，也是 006 授權寫端的共用基建；失手模式（判定面被清空）＝含超管在內全域拒絕、唯重啟可救——本刀最高風險件。

**Independent Test**: 測試直種一列現役選單維授權 → 刪除該選單 → 斷言資料庫已歸檔**且**判定面不再命中（未重啟）；注入壞連線使重建失敗 → 斷言舊判定面續生效（R_SUPER 既有授權續放行）、結構化告警與計數可查。

**Acceptance Scenarios**:

1. **Given** 移除面寫端（刪除選單／批刪選單／編輯選單之按鈕碼絕版／刪除角色／批刪角色）成功且實際歸檔 ≥1 列，**When** 交易 commit 後，**Then** 觸發判定面同步；被拒、無作用、標的不存在、標的零政策列、無按鈕碼變更者皆不觸發。
2. **Given** 判定面重建任一步注入失敗，**When** 移除面寫端 commit 後觸發同步，**Then** 不產出新判定面、保留舊面、發結構化告警並計數；有界重試（次數與退避為寫死常數）耗盡仍失敗＝維持舊面持續告警、服務不中斷。
3. **Given** 選單 M 有現役授權，**When** 刪除 M 後以同路由名新增，**Then** 新選單不經任何路徑（現役殘留、判定面殘留、回收桶復原）繼承舊實例授權（資料庫面＋判定面雙斷言）。
4. **Given** 已授權之自建角色 R_X 被刪除，**When** 以同代碼重建 R_X 並直種一位使用者之指派，**Then** 該使用者經判定面對舊 R_X 之授權零命中（刪除時已同步）。
5. **Given** 注入點使較早開始之重建延後完成，**When** 兩個移除面寫端交錯 commit，**Then** 較晚 commit 之結果不會被較早開始、較慢完成之重建以舊快照蓋回（同步全程互斥；以測試專用之交錯注入點機器證、生產建置零存在）。
6. **Given** 任意選單或角色，**When** 新增選單、復原選單、停用角色或停用選單成功，**Then** 不觸發判定面同步（新增零授權、復原不回灌；角色與選單之啟停由每請求之授權讀端即時濾除）。

---

### User Story 5 - 角色首頁指定 (Priority: P3)

超級管理員讀取或指定某角色的首頁路由名；寫端不驗「首頁是否在該角色可見樹內」（讀端既有兜底：不在可見樹即取先序第一葉）。

**Why this priority**: 小而獨立；「寫端不驗一致性＋讀端兜底」照前代拍板。

**Independent Test**: 讀某角色首頁回現值 → 寫入任一路由名 → 再讀為新值、稽核一列；寫入空字串 → 讀回 `null`。

**Acceptance Scenarios**:

1. **Given** 角色 R，**When** 讀取首頁設定，**Then** 回現值（無則 null）；**When** 寫入任一路由名，**Then** 落庫成功（不驗可見性一致）、同交易稽核；**When** 寫入空字串，**Then** 視為清空。
2. **Given** 不存在或已刪之角色 id，**When** 讀或寫，**Then** 拒（`biz.role.notFound`）。

---

### User Story 6 - 憲法 Amendment、既有域連帶修整、治理與帳本落帳 (Priority: P4)

作為 workspace 維護者，我要在動任何 base-web 既有檔之前，以一筆 MINOR Amendment 讓島 H 入憲、開管理頁 ★ 軌道用途 (ii)、補島 E 兩句並改對兩條憲法簿記句；同刀把 004 域留下的到期承載一併收齊
（分頁規則跨端點化而 IP 規則清單 wire 逐位元不變、共用件收攏、具型交易簽章、信任模型標頭名開機體檢、IP 域已知態 supersede）、把部分更新語意之衝突以 supersede ADR 化解、補齊測試基建與機器守，
並使帳本與活書在收刀時結清——使本刀每一處 base-web inline 自第一行起就在授權邊界內、每筆拍板都有家、既有端點零行為退化。

**Why this priority**: 治理項與功能可分開驗收，但 Amendment 是**硬序前置**（accepted 前不得動 base-web 既有檔）；優先序只表達「不是交付價值本體」、不表達次序。

**Independent Test**: Amendment 落地後 fork-delta-lint 對新用途列之名冊載入以變異自證；IP 規則清單既有契約案全數逐位元照綠；新機器守各以植入反例證非 vacuous；收刀事件之 `backlog_done` 與條文改寫與 FR 相符。

**Acceptance Scenarios**:

1. **Given** plan 期 ADR 草稿已落 feature branch，**When** user 親決→Amendment ADR accepted→憲法更新＋bump 1.5.0＋README 憲法版本鏡像＋generate，**Then** 以獨立 commit 落地（內容恰為憲法、該 ADR、README 憲法版本鏡像與 generate 產物）；在此之前 base-web 既有檔零 diff。
2. **Given** IP 規則清單端點改引共用分頁規則與共用模糊搜尋件，**When** 跑既有契約案與新增之缺席／逾界／壞形案，**Then** 回應逐位元同改前（缺席→1／10、`&size=0&current=0`→(1,1)、壞形→整串預設、`current` 逾界＝上界值）。
3. **Given** 信任模型之訪客位址標頭名寫成非法標頭名，**When** 服務啟動，**Then** 發一則指名該處並附改寫建議之結構化警告、該覆蓋層停用、不計入 IP 域降級、不觸發降級告警規則、且絕不改讀預設標頭名。
4. **Given** IP 規則表存在直改庫之未知類型列，**When** 管理頁載入清單，**Then** 該列照原樣顯示原字串（不崩、不隱藏）、存取閘既有略過＋告警不變。
5. **Given** 系統設定寫端（002）收到某欄空字串，**When** 落庫，**Then** 仍落空字串（行為零變化；新 ADR 逐款重述並續行此款）。
6. **Given** 收刀，**When** append `feature_close` 事件，**Then** `backlog_done` 19 條、條文改寫 3 條、`backlog_add` 零、`adrs` 六支，與 FR-078 相符。

---

### Edge Cases

**角色**

- 角色代碼只在「未刪」範圍唯一——刪除後可以同代碼重建；重建之新角色 MUST NOT 經判定面繼承舊角色授權（FR-051：刪除時即同步、並以端到端案釘住）。
- in-use 與 self-role 兩腿於 007（使用者角色指派寫端）落地前生產面結構性不可達（新建角色無工具可指派、seed 角色先被 seeded 腿擋）——測試以直種指派列構造真實觸發（資料態、零測試旗標、非 vacuous）。
- 同代碼併發新增、更新與刪除併發：新增不進選單域（零授權面），同代碼衝突由唯一索引兜底收斂為 `codeExists`；刪除家族進域。
- 請求 body 缺席或壞形 → 依既有 wire 慣例收斂為預設值（新增→形制拒 2222 之對應鍵；更新→零變更成功）；授權中介層不讀 body、不因此前移守門。
- 請求上下文缺席（操作者不可得）→ 寫端拒寫 `5000`、不以佔位補稽核列；該拒寫事件不帶 IP 域降級欄、不增計降級計數。

**選單**

- 停用＝暫時下架、非撤銷：治理域讀端含停用列；「治理候選誤用顯示域」會使停用靜默升級為永久撤銷（按鈕碼絕版判定同理）——必配負向測試。
- 幽靈父收縮：停用或軟刪目錄使其可見子樹整棵收縮（不下發亦不升根）；本刀寫端不得改變此讀端語意。
- 受保護選單之祖先皆受保護、受保護旗標不開放寫入 ⇒「不可停用＋不可改父」兩腿即令「停用受保護列或其祖先而自鎖管理區」之路徑結構性不可達。
- 按鈕碼清單之壞形 payload 若未擋，會被當成零碼 ⇒ 舊碼全數判為移除 ⇒ 不可復原歸檔：形制驗證 MUST 先於「舊碼−新碼」之計算。
- 絕版判定之聯集＝未刪選單（含停用）之按鈕碼、且 MUST 排除標的自身（掃描時自身仍持舊清單）。
- 歸檔掃描 MUST 依維度（選單維／按鈕維／端點維）過濾：路由名與按鈕碼值域可能重疊，失守即跨維連坐撤除。
- 新建選單零授權（兩步流第一步）；其新增按鈕碼與復原選單之按鈕碼於 006 前無人持有（含 R_SUPER）。
- 批刪清單含查無 id（不存在或已刪）→ 整批拒 `notFound`（Clarifications Q3；兩管理員併發時後送者重新整理再送）；重複 id → 先去重再處理（Clarifications Q4；前端勾選不會送重複 id、只有直打 API 會遇到）。

**判定面同步**

- 前提＝單一 rust-api 行程；多行程或多實例部署時其他行程之判定面不會同步（翻案觸發、屆時須補跨行程通知）。
- 耗盡窗：重試耗盡仍失敗時舊面續用；期間已歸檔之授權仍留在記憶體面、同鍵重建之選單可經殘留面繼承，恢復靠下次成功同步或重啟（ADR 明記、RUNBOOK 載處置）。
- 絕不對現役判定面就地清空重載（該判定引擎版本之重載語意為「先清空再載入」，空政策＝含 R_SUPER 全拒）；呼叫同步者不得持有判定面讀鎖。

**分頁**

- 通則：缺席→第 1 頁、每頁 10；`current` clamp 至 [1, 10^7]、`size` clamp 至 [1, 100]；顯式 0 取下界；查詢串壞形→整串收斂為預設頁；`current` 逾界回空頁且回應 `current`＝上界值。
- 例外恰一：選單治理清單「未帶 `size`」⇒ 回全部頂層、回應 `size`＝實得頂層數、`current`＝1；「未帶」含完全缺席與查詢串壞形（壞形依通則整串收斂成預設＝視同沒帶 ⇒ 全取）；顯式帶合法 `size`（含 0 ⇒ clamp 成 1）照通則。前端把回應之 `size` 回寫每頁筆數，故首載與頂層列數增減時各多一發請求（畫面不變）。
- 已刪選單清單缺席 `size` 取通則之 10（rev5 為 100；前端恆帶 size、UI 零差異）。

**前端與已知態（006 進場前；煙測判準；CDP 完整排除清單見 SC-011）**

- 角色頁「菜單權限」彈窗：顯示真選單樹與真首頁下拉選項，但首頁現值恆寫死為 `home`（不讀首頁設定、切換不落庫）、勾選為寫死 id 1～21（不代表真授權）、送出假成功零寫入；「按鈕權限」彈窗全為假資料——兩顆彈窗本刀一行不動。
- policy-archive 選單項為死項；選單管理頁治理清單中 system-settings／policy-archive／audit 三列顯示路由裸鍵（各頁進場刀帶入譯文）；新建選單在治理清單顯示原始 i18n 鍵字面。
- 新建或復原之選單於 006 前無法授予側欄可見性（含 R_SUPER）——管理列表可見可編、側欄不現。
- getAllRoles 之既有 UI 消費者＝upstream 使用者頁新增抽屜（本刀不動）：自本刀起下拉顯示真角色、提交仍假成功（007 接真）；roleHome 兩端點零 UI 消費者。
- 表頭寫入口：無權者 MUST NOT 看到共用元件之備援新增／批刪鈕；共用元件新增的兩個布林 prop 未傳時 MUST 為 true（純型別宣告下未傳即 false、會令既有呼叫端靜默失鈕）。
- upstream 表單必填規則會使部分拒因在 UI 上零請求零 toast——CDP 拒因步驟挑前端不先擋的守門、並以網路請求事件證請求確實發出。

**連帶與基建**

- IP 規則清單之既有 wire 行為逐位元不變為連帶單元之出口判準；信任模型標頭名非法時執行期行為零變化（原本即失配）、淨增僅開機警告。
- 改 dev 信任模型交付檔（含純註解）後，單檔 bind mount 於換檔後懸空——同批容器測試前 MUST 先重建 rust-api 容器；對賬案「環境變數在而檔讀不到」＝紅、非跳過。
- 業務表逐列比對：`sys_role`／`sys_menu`／`casbin_rule`／`sys_casbin_policy_archive`／`sys_user_role` 皆為 gate2 逐列比對面——測試寫入 MUST 清列並以 arm 當下現讀之序列值還原；指派列之 FK 為 RESTRICT ⇒ 清理序：指派列先於角色列。
- CDP 走查之寫入步驟一律對自建列；以 SQL 還原動過 `casbin_rule` 後 MUST 重啟 rust-api 使判定面回版（判定面無外部通知管道）。
- rev5 側唯讀：一切讀取對凍結 worktree、不寫入、不動其 stack。

## Requirements *(mandatory)*

### Functional Requirements

**A. 端點、授權態與契約總則（ROUTES 22→39）**

- **FR-001**: ROUTES MUST 由 22 條擴為 39 條、路由條數常數同 commit bump；新增十七條且路徑與動詞逐字對齊 001 凍結 seed 之政策列：
  role CRUD 6——`/systemManage/getRoleList`（GET）、`/getAllRoles`（GET）、`/addRole`（POST）、`/updateRole`（POST）、`/deleteRole`（DELETE）、`/batchDeleteRole`（DELETE）；
  menu CRUD 7——`/systemManage/getMenuList/v2`（GET、字面含 `/v2`）、`/addMenu`（POST）、`/updateMenu`（POST）、`/deleteMenu`（DELETE）、`/batchDeleteMenu`（DELETE）、`/getDeletedMenus`（GET）、`/restoreMenu`（POST）；
  roleHome 2——`/systemManage/getRoleHome`（GET）、`/updateRoleHome`（POST）；支撐讀 2——`/systemManage/getMenuTree`（GET）、`/getAllPages`（GET）。動詞分布 GET 7／POST 6／DELETE 4；十七條**全為政策保護**。
  contract case 登記表之 case 集 MUST 與 ROUTES 恰等（39＝39、雙向覆蓋閘；分頁等附加案住各 case 驗證函式內或獨立測試函式、不增登記表鍵）；routes 生成表由 generate 重算；外層 routes 生成器之真 repo 釘值測 MUST 同批 +17 列。
- **FR-002**: 本刀 MUST 為**零 migration、零 seed 變更**：十七條之 seed 政策列（role 讀 12～16、role 寫 21～24、getMenuList/v2 25、getAllPages 26、getMenuTree 27、menu 寫 28～31、roleHome 34／35、
  getDeletedMenus／restoreMenu 64／65〔後兩列 protected〕）、`sys_role.role_memo`／`sys_menu.menu_memo` 欄、授權表治理三欄與授權歸檔表結構皆在 001 基線；migration 目錄維持恰兩支；
  seed 選單 78 列、政策 163 列、角色 3 列不動；以 seed 計數寫死之既有測試零改動。★DDL 冒出＝本刀範圍翻案。
- **FR-003**: 授權態 MUST 逐列照 seed、不多授不少授：寫端全為 R_SUPER；getRoleList 另授 R_ADMIN；getAllRoles 另授 R_ADMIN 與 R_USER_COMMON；其餘端點照 seed 政策列逐列對齊。
- **FR-004**: 一切業務拒因 MUST 為純 i18n key、一因一鍵（無攜參明細）；復用既有 `2222`／`5003`／`4040`／`5000`、13 碼矩陣與錯誤變體零新增。本刀新增拒因鍵恰 24：
  `biz.role.*` 10——`codeInvalid`／`codeExists`／`codeImmutable`／`notFound`／`seededProtected`／`inUse`／`cannotDeleteSelfRole`／`cannotDisableSelfRole`／`superCannotDisable`／`nameRequired`；
  `biz.menu.*` 14——`notFound`／`routeNameExists`／`routeNameImmutable`／`menuTypeImmutable`／`parentNotFound`／`cycleDetected`／`hasChildren`／`protectedMenu`／`constantParent`／`restoreConflict`／`nameRequired`／
  `routeNameInvalid`／`hrefInvalid`／`buttonsInvalid`。msg key 名冊 19→43；每鍵 MUST 在契約測試之真 seed 應用面實際發出（名冊雙向閘），且新鍵 MUST 隨首個發出它的單元落地（名冊、三檔 locale 後端子樹、型別樹同批）。
- **FR-005**: 回應 MUST 逐欄白名單構造（絕不序列化原始資料列）：欄名 camelCase；id 為 number 並守 2^53 上界；狀態類以字串 `'1'`／`'2'`；時間為帶 offset 之 RFC3339；`createdBy`／`updatedBy` 以操作者帳號名批次回填（查無→null）；
  角色列不上軟刪欄（角色無回收桶）；選單列帶導出之 `deleted` 布林、頂層 `parentId`＝0。upstream 未改動之消費者（使用者頁抽屜、菜單權限彈窗）所依之 upstream 型別 MUST 同時相容。
- **FR-006**: 狀態類輸入欄（角色與選單之 `status`、選單之 `iconType`，以及**僅新增路徑**之 `menuType`）MUST 恰二值嚴格解析；值域外（含空字串）＝缺席——新增取預設、更新不動、清單不篩選；停用護欄以「非啟用」判定；更新路徑之 `menuType` 不經值域解析、出現即拒（FR-018）。
- **FR-007**: 部分更新語意 MUST 依本刀 supersede ADR-00015 之新 ADR：欄位缺席＝不動；有值＝設值；角色與選單之可空文字欄送 null 或空字串＝清空（落 NULL；新增路徑同形、防空字串與 NULL 並存）；
  NOT NULL 名稱欄送 null 或空字串＝拒（`nameRequired`，兩域同式）；除 `id` 外之一切欄（含不可變欄）經 FR-006 值域收斂後皆缺席＝提前 no-op（不 bump 時戳、不落稽核）；不可變欄只要出現（不論值）即不屬缺席、依 FR-013／FR-018 拒。系統設定寫端（002）之「空字串落空字串」行為續行、零變化。
- **FR-008**: 每支寫端成功且有業務寫入時 MUST 於同一交易恰落一列操作稽核（批次＝逐標的一列）；提前 no-op 成功（更新全欄缺席、批刪空陣列）零稽核；動作詞彙沿既有小寫封閉集（既有五詞 add／update／delete／restore／unlock、本刀只用前四）、標的表以標的表欄區分、零新動作詞；
  操作稽核落列 MUST 為 IP 規則、角色、選單三寫端一致之要求。操作者取自請求上下文；缺席＝拒寫 `5000`、不以佔位補列；該拒寫事件帶 `refused` 欄、MUST NOT 帶 IP 域降級欄、MUST NOT 增計降級計數、以各域自有之事件目標字面發出。
- **FR-009**: 寫端請求 body 缺席或壞形 MUST 依既有 wire 慣例收斂為預設值：新增→依固定守門序落首腿拒因（`codeInvalid`／`routeNameInvalid`）；部分更新型寫端（updateRole／updateMenu）→零變更成功；以 id 定位之其餘寫端（updateRoleHome、deleteRole、deleteMenu、restoreMenu）→收斂為 id=0→該域 `notFound`；批次刪除→空陣列提前 no-op；授權中介層不讀 body。

**B. 角色 CRUD**

- **FR-010**: getRoleList MUST 提供分頁（FR-054 通則）＋名稱／代碼模糊（不分大小寫子字串、`%`／`_`／`\` 視為字面）＋狀態等值篩選；空字串篩選欄＝不篩選；穩定排序 id 升冪；列帶 `roleMemo`、`roleHome`、審計欄。
- **FR-011**: getAllRoles MUST 僅回活性且啟用之角色、id 升冪、每項恰 `{id, roleCode, roleName}`（MUST NOT 帶備註與審計欄）。
- **FR-012**: addRole 守門固定序（多重違規取先序腿）：代碼形制 `^[A-Za-z0-9_]{1,64}$`（`codeInvalid`）→名稱非空（`nameRequired`）→活性唯一（`codeExists`；先驗顯式拒＋活性唯一索引之衝突兜底收斂為同鍵、只收該索引之衝突）；可帶描述、備註、首頁路由名、狀態（承 rev5 as-built）；成功後該角色零授權。
- **FR-013**: updateRole 可編欄＝名稱／描述／備註／首頁路由名／狀態（承 rev5 as-built；首頁路由名同 FR-007 可空文字欄語意、亦可經 updateRoleHome 寫）；守門固定序：提前 no-op→名稱非空（`nameRequired`）→鎖列查無（`notFound`）→代碼出現（`codeImmutable`）→停用雙護欄（自身所屬→R_SUPER 恆禁）；請求出現 `roleCode`（值不比對）MUST 拒（`codeImmutable`、非靜默忽略）；停用 MUST 過雙護欄——操作者不得停用自身所屬角色（`cannotDisableSelfRole`、成員身分口徑含停用角色）、
  R_SUPER 恆禁停用（`superCannotDisable`、不因操作者身分而異）；停用即斷權沿基線（授權讀端每請求濾角色狀態），MUST NOT 以判定面同步實現。
- **FR-014**: deleteRole MUST 依固定序三層守門：①seeded（seed 角色 id 常數集與超管代碼常數為單一宣告源；`seededProtected`）②in-use（掛載數＝該角色之全部指派列數〔不濾使用者啟停與軟刪；Clarifications Q2〕、`others = total − 操作者是否為成員`、>0 即 `inUse`，
  拒因回誠實總掛載語意）③self-role（`cannotDeleteSelfRole`）；通過後同交易先掃該角色代碼之全三維政策列（含 protected）歸檔（reason＝`role_soft_delete`）、再軟刪角色列、落稽核；角色刪除單向（本刀與 006 皆無角色復原端點）。
- **FR-015**: batchDeleteRole MUST 單一交易、id 升冪逐項全套守門、任一違規整批拒（no-partial）；空陣列＝提前 no-op 成功（零副作用、零稽核、不取選單域鎖）。
- **FR-016**: deleteRole／batchDeleteRole MUST 進選單序列化域（FR-042）；實際歸檔 ≥1 列時 MUST 於 commit 後觸發判定面同步（FR-050／FR-051）；批刪至多一次收尾同步。
- **FR-017**: getRoleHome 回 `{home}` 現值（無則 null）；`id` 缺席或壞形 MUST 收斂為 id=0→`notFound`（不放行框架 400 裸回應）。updateRoleHome 以 `{id, home}` 落庫、MUST NOT 驗可見樹一致性（讀端既有兜底）、同交易稽核；其非部分更新（不適用 FR-007 之缺席不動與 no-op）：`home` 缺席、null 或空字串皆＝清空落 NULL，值同現值亦寫入並稽核；角色不存在或已刪＝`notFound`。

**C. 選單域結構不變式（島 H 入憲面）**

- **FR-018**: 路由名與選單型別建後 MUST 不可變——更新請求出現即拒（值不比對）、MUST NOT 靜默忽略。
- **FR-019**: 新增與改父 MUST 防環（上溯祖先鏈遇自身即拒；上溯上限為寫死常數、逾限同鍵拒）。
- **FR-020**: 父驗證 MUST 三處一致（新增／改父／復原）：父存在且未刪；**停用不擋**；`parentId=0`（頂層）豁免。頂層在 wire 上恆以 `parentId=0`（getMenuTree 為 `pId=0`）表示、資料庫恆存父欄 NULL——新增與改父收到 0 MUST 正規化為 NULL、讀端 NULL MUST 映為 0；MUST NOT 把 0 寫入父欄（否則顯示域樹組裝把 0 當幽靈父、該子樹整棵不下發）。
- **FR-021**: 常量父鏈守門：常量旗標可寫，但常量選單 MUST NOT 掛於非常量父之下——新增、改父或設為常量時驗父鏈；復原常量標的時驗其全祖先常量性（非常量標的零驗）；
  編輯清除自身常量性而其治理域全深後代（含停用、不含已刪）存常量後代時拒（Clarifications Q1）；違反皆 `constantParent`。
  常量選單可寫後，公開之常量路由讀端（免登入）於存在常量列時 MUST 回非空（contract 一案、由守衛清列；與既有「seed 下回空陣列」真庫案之相交處理由 plan 定）；CDP 與 quickstart 各一步（建頂層常量選單→登出狀態下該列可見、內建路由仍在、路由可達→刪除並還原）。
- **FR-022**: 讀端 MUST 分治理域（未刪含停用；管理列表、父選擇器、按鈕碼絕版判定、授權候選之源）與顯示域（啟用且未刪；使用者路由、頁面下拉）；治理候選 MUST NOT 誤用顯示域（必配負向測試）。
- **FR-023**: 同鍵重建零繼承（島 H2）：同路由名重建之新選單 MUST NOT 經任何路徑（現役殘留、判定面殘留、回收桶復原）繼承舊實例授權——現役無殘留（序列化域＋刪除連動歸檔掃盡）＋歸檔不可回灌（reason gate）＋判定面同步。
- **FR-024**: 受保護選單 MUST NOT 可刪（`protectedMenu`）、MUST NOT 可停用、MUST NOT 變更其父選單（兩者同鍵 `protectedMenu`；rev6 增補、憲法島 H3 同批入憲）；其餘欄照常可編；受保護旗標本身不開放寫入；三檔 locale 之 `biz.menu.protectedMenu` 譯文 MUST 改寫為涵蓋刪除／停用／改父三種情形（零新鍵；前代「不可刪除」譯文不得照搬）。
- **FR-025**: 幽靈父收縮語意 MUST 維持現狀（改判＝翻案程序）。

**D. 選單 CRUD**

- **FR-026**: getMenuList/v2 MUST 治理域、樹形、頂層計數分頁；未帶 `size`（含查詢串壞形＝視同沒帶）⇒ 回全部頂層及其全深子樹、回應 `size`＝實得頂層數、`current`＝1（FR-056）；帶 `size` 依 FR-054 通則；同層序 MUST 為（排序值升冪、無值在後，再 id 升冪）、
  頂層分頁依此序切（以擾動實體回列序後兩次呼叫逐位相等之案釘住）；列帶 `menuMemo`。
- **FR-027**: getMenuTree MUST 回治理域全樹之輕量形 `{id, label, pId, children?}`（頂層 `pId=0`）、同層序同 FR-026；wire 形 MUST 同時與 upstream `Api.SystemManage.MenuTree` 型相容（其既有消費者＝角色頁菜單權限彈窗、本刀一行不動）；本刀新增之父選擇器經新 wrapper 消費同一 wire。
- **FR-028**: getAllPages MUST 回顯示域路由名全集（字串陣列、依排序值升冪無值在後再 id 升冪）；零授權面。
- **FR-029**: addMenu MUST 支援目錄與選單兩型；守門固定序（承 rev5 as-built、多重違規取先序腿）：父驗證→防環→路由名活性唯一（域內先驗＋活性唯一索引之衝突兜底、同鍵 `routeNameExists`）→常量父鏈→路由名形制（`routeNameInvalid`）；
  本刀增補腿接其後：名稱非空（`nameRequired`）→href 形制→按鈕碼清單形制；零授權寫入（兩步流第一步）；「隱藏於選單」、多分頁等一般欄照 upstream 可寫。
  updateMenu 守門固定序：提前 no-op（FR-007）→名稱非空（`nameRequired`）→鎖列查無（`notFound`）→不可變欄出現（`routeNameImmutable` 先於 `menuTypeImmutable`）→受保護列之停用或改父（`protectedMenu`）→改父之父驗證（`parentNotFound`）與防環（`cycleDetected`）→常量父鏈（含清除常量性之後代腿；`constantParent`）→href 形制→按鈕碼清單形制（先於絕版計算）；逐腿一案並含至少一個多違規取先序腿案；此序凍結入契約。
- **FR-030**: href 於新增與更新 MUST：空字串＝清空；有值須以 `http://` 或 `https://` 起首（不分大小寫），否則拒（`hrefInvalid`）、零寫入。
- **FR-031**: 按鈕碼清單於新增與更新 MUST 為 null 或陣列；每成員為物件、碼為非空字串且 ≤100 字元、同清單內碼不重複；不限字元集；違反拒（`buttonsInvalid`）、零寫入零歸檔；驗證 MUST 先於絕版計算。
- **FR-032**: updateMenu 之按鈕碼變更：自清單移除且**絕版**（不再屬任何其他未刪選單〔含停用〕之按鈕碼聯集；判定 MUST 排除標的自身）之碼，其按鈕維政策 MUST 同交易歸檔（reason＝`menu_button_removed`）；
  非絕版移除 MUST NOT 歸檔；實際歸檔 ≥1 列即於 commit 後觸發判定面同步。
- **FR-033**: deleteMenu MUST 依固定序守門（受保護→存在未刪子項〔不論啟停〕，`hasChildren`）；通過後同交易先掃「該路由名之選單維政策（跨全角色）＋該選單獨有按鈕碼之按鈕維政策」歸檔（兩者 reason 皆＝`menu_soft_delete`；依維度過濾）、
  再軟刪選單列、落稽核；實際歸檔 ≥1 列即於 commit 後觸發判定面同步。
- **FR-034**: batchDeleteMenu MUST 子先於父之拓撲序、逐項全套守門、任一違規整批拒、單一交易、至多一次收尾同步；空陣列＝提前 no-op 成功（零副作用、零稽核、不取選單域鎖）。
- **FR-035**: getDeletedMenus MUST 回已刪集合、常規分頁（FR-054）、穩定排序（刪除時間降冪、id 降冪）；MUST NOT 帶「可復原」旗標（選單復原無 reason gate 概念、復原守門即唯一權威）。
- **FR-036**: restoreMenu MUST 域內鎖列重驗（標的為已刪存在，否則 `notFound`→同鍵活性衝突 `restoreConflict`〔唯一索引衝突兜底同鍵〕→父未刪 `parentNotFound`→常量標的之祖先常量性 `constantParent`）→成對清空軟刪時間與軟刪者、原狀態保留；
  MUST NOT 回灌任何授權、零授權寫、零判定面同步；同交易稽核。
- **FR-037**: 批次刪除（角色與選單兩域同式）之查無 id（不存在或已刪）＝整批拒、回該域 `notFound`、零變更零稽核（Clarifications Q3）；重複 id＝先去重再處理（例 `[5,5]` 視同 `[5]`；稽核列數＝去重後標的數；Clarifications Q4）；兩者各以 contract 案釘住。

**E. 授權歸檔寫入面與 reason gate**

- **FR-038**: 歸檔寫入 MUST 完整快照政策列＋來源角色 id（以政策列之角色代碼反查活性角色；查無＝誠實退化為 NULL）＋reason；歸檔表結構零變更（三個潛在自由度全不動，翻案觸發條款過境本刀 ADR）。
- **FR-039**: 歸檔掃描 MUST 早於標的列軟刪更新（否則反查來源角色 id 全數落 NULL）；本刀之三 reason（`role_soft_delete`／`menu_soft_delete`／`menu_button_removed`）MUST 全屬不可復原集，且該集合 MUST 由單點函式承載、配成員測試。
- **FR-040**: 歸檔讀端與授權復原端點不在本刀（006）。

**F. 選單序列化域與鎖序**

- **FR-041**: 選單域 MUST 以單一資料庫交易級 advisory 鎖為載體（key＝`0x7265_7636_6D65_6E75`、ASCII `rev6menu`；常數住活書）；xact 級自動釋放、零逾時零重試。
- **FR-042**: 進域寫端恰為選單五寫端（新增／更新／刪除／批刪／復原）＋deleteRole／batchDeleteRole；addRole／updateRole／roleHome MUST NOT 進域；授權治理之選單維／按鈕維寫端及授權回收桶復原之該兩維分支屆時入域（端點維授權寫入不入域；條文寫終態、該等端點不存在期間 vacuous 成立）。
- **FR-043**: 域鎖 MUST 為交易首動作、MUST NOT 下沉至資料存取層內；固定鎖序＝advisory→歸檔表列→角色列→選單列→授權表列；與既有 per-user advisory 鎖 MUST 維持結構性無 ABBA（key 空間不碰撞＋鎖集合零交集），三個失效條件（角色寫端連動撤會話、使用者域寫端進場、同 key 重入）記入 ADR。
- **FR-044**: 序列化有效性 MUST 有機器證：逐進域寫端各一案，兩寫端併發時後者於 advisory 等待（以 NOT-granted 等待者斷言、64-bit key 拆兩欄比對）。
- **FR-045**: 擁有交易之入域寫端，其失敗腿 MUST 顯式回滾後再回錯，並各配一支源碼釘（防止斷言失敗時與清理守衛互鎖而整輪無訊息卡死）。

**G. 判定面同步（重建後一步換上）**

- **FR-046**: 判定面同步 MUST 另建全新判定面（模型→轉接器→建構→載入四步）、任一步失敗整體失敗不產出實例、成功才於寫鎖臨界區一步換上；MUST NOT 對現役判定面就地清空重載
  （禁令＋判定引擎版本 2.20.0 鎖註解——升版必重核其重載語意）；呼叫同步者 MUST NOT 持有判定面讀鎖；同步 MUST 於交易 commit 之後。
- **FR-047**: 同步全程（重建＋換上＋重試）MUST 互斥序列化，使較晚 commit 之結果不被較早快照蓋回；其交錯時序 MUST 以測試專用之注入點機器證、生產建置零存在。
- **FR-048**: 同步失敗 MUST 保留上一份已知良好判定面＋結構化告警＋同步結果計數（ok／retry／exhausted 三值，與既有告警規則 `obs016-casbin-reload-anomaly` 之錨字面對齊、開機預註冊）；
  有界重試（次數 3、線性退避 50ms；寫死常數、絕不取自輸入）；耗盡仍失敗＝維持舊面持續告警、服務不中斷；該告警規則註解之「（島 G1）」改指島 H2＋判定面同步 ADR（rev6 島 G 尚未入憲）。
- **FR-049**: 本刀之判定面同步前提＝單一 rust-api 行程；多行程或多實例部署為翻案觸發（須補跨行程通知），記入 ADR；耗盡窗內記憶體面殘留之繼承風險與恢復程序記入 ADR 與 RUNBOOK。
- **FR-050**: 觸發 MUST 恰為五支移除面寫端之「成功且實際歸檔 ≥1 列」：刪除選單、批刪選單、編輯選單之按鈕碼絕版、刪除角色、批刪角色；被拒／無作用／標的不存在／標的零政策列／無按鈕碼變更 MUST NOT 觸發（早退結構性保證）；
  新增選單、復原選單、角色與選單之啟停 MUST NOT 觸發。ADR、契約與本條 MUST 同一字面（不得寫成「成功即觸發」）。
- **FR-051**: deleteRole 家族之同步 MUST 封住「刪除→同代碼重建→指派」之殘留繼承窗（翻前代「刪角色免同步」論證）；角色維零繼承 MUST 有端到端案（刪除→同碼重建→直種指派→判定面零命中）。
- **FR-052**: 同步之機器守 MUST 含：失敗注入（壞連線⇒舊面續放行 R_SUPER）／「改寫為就地清空重載必轉紅」負向自證／觸發條件特性鎖定（含零政策列刪除＝零同步）／移除面端到端（資料庫＋判定面雙斷言；刪除前 MUST 先斷言判定面對該授權確實命中＝先種 live 授權、防恆綠）／
  成功路徑換上＋`ok` 計數／三支併發同步全數完成之完成性案；另三道集合恰等之名冊守恆——同步呼叫點檔集（接線後恰選單與角色兩支 handler）、判定面寫鎖取得檔集（空冊、家檔豁免）、重載與建構 token 於生產區只許出現於判定面家檔（射程＝各檔扣除行首測試模組區塊後之生產面、item 級測試門控項保守計入；整檔以測試門控閘入之模組與 tests 樹之合成判定面建構明文豁免、豁免清單以機器判準現算並自我對賬）——各附植入反例變異自證；
  該 lint 以行掃描或重用既有剝註解件實作、MUST NOT 另立第三份字元級解析組。
- **FR-053**: 判定面之「boot 載入即終態」諸宣告（判定面家檔之檔頭與初始化說明、行程進入點、應用狀態定義）MUST 以 ADR 翻案並改寫；該 ADR MUST 明引 ADR-00014 決定 4 之「運行期重載屬後刀」預告並定性為兌現（不 supersede）。

**H. 分頁（跨端點規則）**

- **FR-054**: 分頁參數 MUST 由單一共用規則收斂，四個清單端點（角色清單、已刪選單清單、選單治理清單、IP 規則清單）同用一份常數：缺席→`current=1`、`size=10`（選單治理清單 `size` 缺席之全取例外見 FR-056）；`current` clamp [1, 10^7]、`size` clamp [1, 100]；
  顯式 0 取下界；查詢串壞形→整串收斂為預設；`current` 逾界回空頁且回應 `current`＝上界值。IP 規則清單改引後 wire MUST 逐位元不變（既有案全綠）。
- **FR-055**: 規則 MUST 寫入活書 08 之 API 慣例與各端點契約、並以 contract test 逐端點至少四案釘住（缺席、逾界、`&size=0&current=0`、壞形各一）。
- **FR-056**: 「完全未帶 `size` 即全取」之例外 MUST 恰限選單治理清單：以明名之專用入口承載、白名單恰此一端點；名冊測試 MUST 釘該入口全樹恰一處生產呼叫；四個清單端點各一案釘其缺席行為（三支回 10、選單治理清單回全部）；
  活書例外表列之；新增例外 MUST 同批改白名單、測試與 ADR。邊界：只有未帶 `size` 才全取；`size=0` 仍 clamp 成 1；查詢串壞形整串收斂為預設＝視同沒帶（選單治理清單 ⇒ 全取）。
- **FR-057**: 新增之帶查詢串 query 型 MUST 各配一支真串抽取案——角色清單與已刪選單清單取頁面首屏真送出之查詢串；首頁讀取之 `id` 無 UI 消費者、改以 wrapper 經前端序列化器產出之 `{id}` 串為真源；選單治理清單另釘無參形；前端查詢串序列化前提（序列化器設定與其版本）MUST 有跨子庫機器錨，
  且該錨 MUST 在 wire 裁判工具之收窄判斷與容器探測之前無條件執行（不擴收窄路徑、不動 submodule-sync 段）。

**I. 前端**

- **FR-058**: role 頁與 menu 頁 MUST 接真後端（列表／搜尋／新增編輯抽屜或彈窗／刪除批刪／回收桶開關／備註）；本刀動到之 base-web 既有檔恰為用途 (ii) 九檔（FR-075 ③；六檔修改型逐行 `原行:`〔純新增段走新增型圈界〕、三檔僅新增型圈界）；兩顆授權彈窗 MUST 一行不動（本刀出現任何 diff＝紅）。
- **FR-059**: 新增型新檔 MUST 為兩支 API wrapper 與兩支型別檔（獨立命名空間；角色含 roleHome 兩支、選單含 getMenuTree）；頁面下拉走 upstream 既有 getAllPages 包裝（該檔零改）；menu 彈窗之 upstream 殘留 `fetchGetAllRoles` 呼叫 MUST NOT 帶入。
- **FR-060**: menu 頁 MUST：治理清單無參一次取全樹、分頁列凍結呈現（位置不動、頁碼 1、每頁 0、整列停用、前綴顯真實筆數；分頁元件 MUST 走頁數分支而非筆數分支，否則每頁 0 會算出無限頁數凍死瀏覽器）；
  回收桶開關換源、操作欄整欄換復原、切換清勾選、切換前每頁筆數歸位；已刪模式以共用元件 prop 關閉新增與批刪入口；父選擇器三模式（新增／新增子項／編輯）皆顯、首項為合成頂層節點；彈窗含備註 textarea（placeholder 註明管理員可見）；編輯態路由名與選單型別鎖定且更新請求 MUST NOT 帶該兩欄（FR-018）。
- **FR-061**: role 頁 MUST：列表接真（分頁＋搜尋＋狀態＋備註欄）、抽屜含備註 textarea（placeholder 註明管理員可見）、編輯態代碼欄鎖定且更新請求逐欄顯式構造、MUST NOT 帶 `roleCode`（FR-013）、搜尋重置後即重查；拒因提示由共用攔截層轉譯、頁內只看成敗。
- **FR-062**: ip-rule 頁 MUST 改為以 prop 控制表頭：新增鈕綁新增按鈕碼權限、批刪鈕關閉、接上新增事件，不再覆寫預設插槽；隨 prop 形失效之疊寫碼註同批刪除；「無權者看不到新增」以模板靜態斷言守（seed 下 CDP 不可達）。
  未知規則類型 MUST 在標籤映射與翻譯呼叫之前即退回顯示原字串。
- **FR-063**: 共用表頭元件 MUST 附加「顯示新增」「顯示批刪」兩個布林 prop、預設 true 且以帶預設值之宣告承載；既有呼叫端零行為變化（user 頁與 role 頁表頭另對 upstream example 驗鈕仍在）。
- **FR-064**: i18n MUST：`page:` 樹補 9 鍵（角色備註欄標籤與表單鍵、選單備註欄標籤與表單鍵、顯示已刪除、確認復原、復原、復原成功、父選擇器頂層標籤），兩語鍵集相等、型別樹同補；`route:` 樹零新增；
  三檔 locale 後端子樹各補 24 鍵；各新增圈界塊落地後做「拔標記必紅」變異自證。
- **FR-065**: `components.d.ts` 重算 MUST 只出現父選擇器元件之兩行增列（介面內一行、全域常數區一行）、其餘差異即紅；重算檔與彈窗同 commit；路由外掛產物四檔零變動（不新增 view 頁）；前端路由 static meta 以 DB 為唯一真源、不維護（一句紀律、不建閘）。
- **FR-066**: 備註兩欄 MUST 兌現於管理列表與編輯入口、純文字插值（無原始 HTML 插值）；被取用處（角色下拉、路由樹）MUST NOT 帶備註。

**J. 004／002 域連帶（零 wire 行為變更）**

- **FR-067**: 模糊搜尋共用件 MUST 為單一源（IP 規則清單與角色清單改引；不另寫轉義子句、佔位符與欄參數形照既有正典）；「只認活性唯一索引之衝突」判斷與時戳取得兩件共用件同批上提、IP 規則資料層改引（零行為變更）；
  IP 規則資料層四寫端與鎖讀 MUST 改為只收交易之具型簽章（跨三檔之測試呼叫同批改為自開交易並 commit）。
- **FR-068**: 信任模型載入 MUST 對通道與每筆 CDN 之訪客位址標頭名驗合法性：非法＝一則結構化警告（指名處、原字面、改寫建議）、不計入 IP 域降級、不帶降級欄、降級來源名冊維持恰八；原字面保留、MUST NOT 改讀預設標頭名；
  配一正一反＋「非法名時預設標頭不被讀取」反案＋「非法名時覆蓋層結果與修改前逐格相同」對拍；判別不新增依賴；活體契約失敗語意表加一列。
- **FR-069**: IP 規則清單端點對未知類型列 MUST 照原樣上 wire（by-design、不過濾、不改契約與快照）；以新 ADR supersede ADR-00040（六款重述：款 2 改三態、款 3 寫入者集對齊 as-built、款 6 對齊 as-built 並以讀型鍵集斷言兌現；新款＝未知類型上 wire＋前端退顯；補前代出處；附款號對照表）。
  「二態」之現在式鏡像 MUST 以機器枚舉逐處分流改對。

**K. 測試基建與機器守**

- **FR-070**: 測試 MUST 配業務表清理守衛（角色、選單、授權、授權歸檔、指派五表）＋守衛自證測：arm 時現讀 id 水位與序列值、Drop 先刪水位以上之列再以現讀值還原序列；seed 態之序列期望只作自證前提；
  指派列之清理先於角色列；測試造列一律顯式大 id 且號段集中登記（`casbin_rule` 除外：經真判定面之新增政策路徑造列、取序列 nextval，由守衛以 arm 時現讀之序列值還原——如此判定面才真的持有該授權）；稽核斷言取水位窗、不寫絕對計數；契約測試側另立所需庫態守衛。
- **FR-071**: wire 裁判面 MUST：本刀新增之全部 wire 型（回應＋請求＋query；實數以抽取為準）＋共用分頁信封入受審名冊；「序列化鍵集＝快照鍵集」斷言以表驅動涵蓋全部受審讀型（既有七型＋本刀新讀型＋分頁信封；交叉型佔位之一型具名豁免附理由）。
- **FR-072**: i64 守衛 lint MUST 補：泛型 wire 型名冊與樹上泛型序列化型集合恰等＋實例化掃描；手寫序列化實作絆線；型級解析普查等式（`derive(Serialize)` 錨數＝解析成功數，同時兌現巨集生成型之偵測）；各附變異自證、檔頭邊界段改寫。
- **FR-073**: MUST 立一支行掃描形 lint（不另立字元級解析組）：射程＝源碼掃描切面腿所在檔及其跨檔所切之檔（皆以機器判準現算並自我對賬）；在與切面腿同一切點之後，每個 column-0 item 之屬性鏈 MUST 含測試門控；頭形涵蓋可見性前綴與修飾詞；
  掃描視圖剝除註解與字串常值；同檔另立「生產區零觀測出口別名匯入」腿；各附變異自證。
- **FR-074**: 其餘到期承載 MUST 同刀收：`handler/common.rs` 重評三件（兩件共用件之簽章、`tracing::error!` 留呼叫點之切法、測試側狀態快照家族；結論落檔 doc）；泛型三態、空字串轉缺席、兩向狀態映射首次出現即落 `handler/common.rs`，系統設定 handler 之私有三態改引（先依 RL-0070 查掃描閘）或於 doc 註明保留理由；角色／選單寫端之拒寫事件 MUST 同時納入既有兩道字面守——各域事件目標字面名冊與「生產碼零降級欄」掃描射程皆擴及角色與選單兩 handler（前代 HEAD 帶降級欄之寫法不帶入）；7777 腿 denylist 鍵改 RAII；請求上下文缺席之每請求總數案（至少打一支角色或選單寫端、釘住「其餘端點 2 格」）；
  dev 信任模型三鏡像「刪一錨一」（對賬三態：環境變數缺席＝具名跳過、在而讀檔失敗＝紅、讀得到＝逐欄比對）；共用分頁信封與其 typings 權威之錨。

**L. 治理、文件與簿記**

- **FR-075**: 憲法 Amendment MUST 一次 MINOR（1.4.0→1.5.0）、獨立 commit（內容恰為憲法、ADR①、README 憲法版本鏡像與 generate 產物；②③⑥ 另起一顆）：①§I.7 島 H 五條入憲（以前代 v1.7.0 字面為底；H1 終態句以描述形＋現在式條件句寫成、不帶刀集外刀名；H3 增補受保護選單不可停用、不可改父；
  常數留活書；承襲指針表 H 列尾註；MAJOR 射程句「六島」改「七島」；依承襲指針表尾句完成之跨島重審結論載 ADR）②島 E 補兩句（解鎖端點之操作稽核先於解鎖標記寫入；操作者上下文缺席即拒寫 `5000`、不以佔位補列）
  ③§III.2 ★ 軌道加用途 (ii)「role／menu 管理頁 CRUD 接真」恰九檔（role 三檔、menu 兩檔、共用表頭元件、兩語 locale、`app.d.ts`；兩顆授權彈窗與 `menu/modules/shared.ts` 明文不入；範圍欄對三支僅新增型檔寫 rev5 as-built 預估塊數、六支 view／元件檔不預估，實數以標記為準；前端單元出口對三支僅新增型檔逐檔斷言新增型塊數等於預估，不等即停手升級主線、由 user 定當刀 PATCH 或比照 BL-00118 滯後）
  ④表外宣告 1 之量法句與既有列範圍欄數字改為與活書 08 同一量法（BL-00118）⑤§I.7 段首增補計數句改為以 Amendment log 為準（BL-00119）。Amendment accepted 前 base-web 既有檔 MUST 零 diff。
- **FR-076**: ADR MUST 六支（刀分支內落、序號接續）：①Amendment ②判定面同步重建換上（含觸發矩陣五支、硬禁令與版本鎖、互斥序列化、ABBA 三失效條件、單行程前提、耗盡窗；明引 ADR-00014 決定 4）
  ③選單域與角色刪除之域行為（deleteRole 入域＋實際歸檔才同步；島 G 行為 G1／G3／G4／G5 由 ADR 承載、條文隨 006 入憲；歸檔表三自由度 won't-use 與前代翻案觸發條款過境；hideInMenu 釋義；受保護選單守門行為面；007 須定「使用者軟刪是否清指派」之觸發）
  ④本刀已知態與 by-design（各款寫成「觀察路徑→症狀」、CDP 實際觀察後定稿）⑤IP 域已知態 supersede ADR-00040 ⑥部分更新語意 supersede ADR-00015。親決時點：U0 兩顆（Amendment 顆＝①；施工前提顆＝②③⑥）；④⑤ 留草稿至治理單元才親決 accepted。
  草稿期 `supersedes` 留空、accepted 那一顆同批補並改舊 ADR 狀態；同批將現在式面指向被取代 ADR 之引用改指新檔（以機器枚舉 ADR-00040／ADR-00015 現算後逐處分流；已知面含活書 06／08／11／12、RUNBOOK、BL-00043／BL-00091 條文內指針、活書 08 部分更新三態句改述 ADR⑥ 兩域語意、系統設定 handler 內 8 處 doc 引用〔該檔納入 ADR⑥ 單元允許清單、只准改註〕；史料面與已 accepted 之 body 不動）。
- **FR-077**: 活書 MUST 於 feature branch 內改為現在式 as-built：模組、執行期情境（選單域生命週期＝島 H）、分頁通則與例外表、fork-delta 用途 (ii)、品質情境新增島 H 一則、已知態列、詞彙
  （治理域／顯示域、序列化域、絕版、常量父鏈、reason gate、選單回收桶與授權回收桶分立、判定面同步與 IP 規則熱重載分立）；RUNBOOK MUST 補選單域鎖觀測與同步結果判讀、同步耗盡之處置（只寫實跑過之命令）、
  dev 分界三態、標頭名核對句、wire 前提腿之已知邊界、走查還原擴面與「動過授權表即重啟」；活體契約之 hide_in_menu 釋義句與備註預告句改現在式；本刀落地後成假述之現在式句 MUST 以四形種子機器枚舉、逐處改對。
- **FR-078**: 帳本 MUST 於收刀兌現：`backlog_done` 19 條＝BL-00082／BL-00095／BL-00096／BL-00098／BL-00105／BL-00106／BL-00107／BL-00109／BL-00110／BL-00111／BL-00112／BL-00113／BL-00115／BL-00116／BL-00117／BL-00118／BL-00119／BL-00123／BL-00125；
  條文改寫 3 條＝BL-00120（只剩 ADR-00039 半）、BL-00093（② 加 casbin-reload 錨已對齊之戳記）、BL-00045（補選單管理頁曝光面）；`backlog_add` 零；反向確認 BL-00047／BL-00028／BL-00048／BL-00074（兩半）／BL-00108（兩半）／BL-00123 之新增發射腿半邊（角色／選單寫端拒寫不增計請求上下文缺席計數）零觸發並現算；收刀事件 notes 記淨流量值與揭露型／新欠型分型；
  `feature_close.adrs` 六支、`arch_impact` 以收刀時 diff 現算之活書節號為準；NOTES 下一步 specify 起手後改 005 進行中、收刀改 006。
- **FR-079**: 收刀 DoD MUST 全綠：容器內後端全量測試（全程 serial）＋contract 39 case＋前端型別檢查＋fork-delta-lint（新用途列名冊載入變異自證、修改型只在九檔）＋msg-key-gate＋wire 裁判 check＋schema 三閘＋
  路由產物冪等＋docsync check／lint 零紅＋走查基準 diff rc 0＋CDP 三方對照（判準＝SC-011）；FR-001～FR-079 與 US1～US6 驗收場景全數對應至少一測試案、機器守或演練紀錄（tasks 逐條映射、無承載者即紅）。

**★ 軌道逐處登記（憲法 §III.2 必需三欄：位置＋改動內容＋upstream 衝突風險評估）**

風險判準（承 004 spec、可覆算；量測面＝base-web upstream `example` tip `8be6f9ba`〔提交日 2026-05-13〕、量測日 2026-09-23、以 `git log --since` 計檔級 commit 數）：**高**＝近 12 月 ≥5；
**中**＝近 12 月 1–4 或近 24 月 ≥5；**低**＝近 12 月 0 且近 24 月 ≤4。**修改型再 +1 級**、純新增型與產物檔不加級。收錄準則：用途 (ii) 九檔逐處＋生成檔＋I18N 授權面之錨點檔；兩支 wrapper 與兩支型別新檔屬 §III.1 純新增、不列——共 11 列。

| 位置（檔案） | 軌道·用途 | 型別 | 改動內容 | 12m／24m | 風險 |
|---|---|---|---|---|---|
| `src/views/manage/role/index.vue` | `BASE-WEB-MANAGE-PAGE-WIRING(ii)` | 修改型＋新增型 | 列表接真、分頁、搜尋、備註欄、刪除批刪接真 | 2／4 | **高**（中＋1） |
| `src/views/manage/role/modules/role-operate-drawer.vue` | 同上 | 修改型＋新增型 | 新增編輯接真、備註 textarea、編輯態代碼鎖定（兩顆授權彈窗之入口鈕不動） | 1／3 | **高**（中＋1） |
| `src/views/manage/role/modules/role-search.vue` | 同上 | 修改型＋新增型 | 篩選欄對齊 wire、重置後即重查 | 2／3 | **高**（中＋1） |
| `src/views/manage/menu/index.vue` | 同上 | 修改型＋新增型 | 治理清單接真、分頁列凍結、回收桶開關、備註欄、prop 關寫入口 | 1／3 | **高**（中＋1） |
| `src/views/manage/menu/modules/menu-operate-modal.vue` | 同上 | 修改型＋新增型 | 父選擇器（合成頂層）、頁面下拉、備註 textarea、殘留呼叫不帶、編輯態鎖定 | 2／4 | **高**（中＋1） |
| `src/components/advanced/table-header-operation.vue` | 同上 | 修改型＋新增型 | 附加兩個布林 prop（預設 true、帶預設值宣告） | 0／0 | 中（低＋1）★本刀新衝突面 |
| `src/locales/langs/en-us.ts` | `BASE-WEB-MANAGE-PAGE-WIRING(ii)`＋`BASE-WEB-I18N-WIRING(ii)` | 新增型 | `page:` 樹補 9 鍵（新增型圈界）；既有 backend 塊內補 24 鍵 | **14／37** | **高** |
| `src/locales/langs/zh-cn.ts` | 同上 | 新增型 | 同上（簡中） | **15／38** | **高** |
| `src/typings/app.d.ts` | `BASE-WEB-MANAGE-PAGE-WIRING(ii)`＋`BASE-WEB-I18N-WIRING(iii)` | 新增型 | `Schema.page` 型節補鍵；既有 backend 型節補 24 鍵 | **13／32** | **高** |
| `src/typings/components.d.ts` | §III 生成檔紀律（不入用途名單） | 產物檔 | 工具重算：父選擇器元件兩行增列（FR-065 斷言） | 8／17 | **高** |
| `src/locales/langs/zh-tw.ts`（rev6 錨點檔） | `BASE-WEB-I18N-WIRING+`（新增型、不入名冊） | 新增型 | backend 子樹補 24 鍵（繁中譯文之家） | —— | 低 |

★本表最重要的一件事：本刀首度動到 upstream 共用元件（表頭）——雖近 24 月零改動，但它是全部管理頁的表頭，rebase 時一旦 upstream 改動即多頁連動；緩解＝只附加 prop、不改既有行、預設值維持舊行為。
i18n 三檔仍是基線最熱之檔；緩解＝一律新增型圈界、不與 upstream 行交錯。**rebase 處置**（承憲法 §III「rebase 同步紀律」）：修改型逐行 `原行:` 同步 upstream 現行版；生成檔一律於 rebase 後以工具重算、絕不手工解衝突。
★逐處明細由實作期 fork-delta 標記落地並受 `fork-delta-lint` 機器強制；本表為檔級風險評估與 rebase 處置索引。

### Key Entities *(include if feature involves data)*

- **角色**（`sys_role`、001 基線）：代碼（不可變、形制受驗、活性唯一）、名稱、描述、狀態（啟用／停用）、備註（超管書寫、管理列表可見）、首頁路由名、軟刪欄；seed 三列受結構護欄；停用即斷權；刪除單向。
- **選單**（`sys_menu`、001 基線）：樹狀實體（父選單、防環）；路由名（授權錨、不可變、活性唯一）、型別（目錄／選單、不可變）、按鈕碼清單、常量旗標（父鏈常量性受守）、受保護旗標（唯讀；不可刪、不可停用、不可改父）、
  隱藏於選單旗標（業務資料）、外連網址（限 http(s)）、備註、啟停、軟刪欄；治理域與顯示域雙讀面。
- **使用者角色指派**（`sys_user_role`、001 基線、複合主鍵、兩條 FK RESTRICT）：本刀零寫端；角色掛載計數之源；測試直種以構造守門腿。
- **授權政策**（`casbin_rule`）：授權真相（資料庫優先）；本刀只觸及移除面（刪除與絕版連動歸檔）；治理欄對判定引擎轉接器不可見。
- **授權歸檔**（`sys_casbin_policy_archive`）：移除＝移入歸檔；完整快照＋來源角色 id（可空）＋reason；本刀三 reason 全屬不可復原集（單點函式承載）；本刀建寫入面、讀端屬 006。
- **選單序列化域**（概念實體）：單一 advisory 鎖承載之互斥執行域；成員＝選單五寫端＋角色刪除家族（＋授權治理之選單維／按鈕維寫端）；交易首動作、固定鎖序。
- **判定面**（記憶體授權判定實體）：由授權真相全量導出；重建後一步換上、保留上一份、絕不就地清空；同步觸發恰五支移除面寫端之「成功且實際歸檔 ≥1 列」；前提單一行程。
- **分頁規則**：四個清單端點共用之參數收斂規則；例外恰一（選單治理清單無 size 全取）。
- **msg key 名冊（43 鍵）**：既有 19 鍵＋本刀 24 鍵；三檔 locale 後端子樹各為該語譯文之家。
- **★ 軌道名冊（Amendment 後）**：§III.2 管理頁軌道新增用途 (ii) 九檔；其餘軌道不變。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 路由與授權態對賬零漂移——路由表恰 39 條且與 seed 政策列路徑×動詞逐字對齊；契約覆蓋閘無缺案無殭屍案；授權態矩陣逐端點實測（Admin 對寫端得 `5003`、對角色清單得通；一般使用者對 getAllRoles 得通）。
- **SC-002**: 拒因碼表自證——24 支新鍵每支各至少一案實際發出、名冊雙向閘綠；13 碼矩陣可發碼與保留碼數量不變、零新錯誤變體；三檔 locale 後端子樹逐檔與名冊雙向相等、型節齊備。
- **SC-003**: 角色守門全可驗——三層守門固定序逐腿一案（in-use 與 self-role 以直種指派構造）；停用雙護欄兩案；代碼形制、活性唯一（含併發同碼一案）、不可變各一案；批刪含違規整批零變更一案、含查無 id 整批拒一案、含重複 id 去重後成功一案、空陣列 no-op 一案。
- **SC-004**: 選單守門全可驗——父驗證三處、防環（含上溯逾限）、不可變兩欄、常量父鏈（新增／改父／清除常量性之後代腿／復原第四腿）、受保護三腿（刪除／停用／改父；停用與改父各一正一反）、href 形制、按鈕碼清單形制（非 null 非陣列、成員非物件、缺碼、碼為空或非字串、超長、重複各一）、同層排序擾動案、四支寫端固定守門序之多違規取先序腿案、
  子先於父批刪（含查無 id 整批拒、重複 id 去重各一）各至少一案；治理域誤用顯示域之負向測試在案。
- **SC-005**: 序列化域有機器證——七支進域寫端各一案斷言併發者於 advisory 等待；不進域之三支寫端（新增角色、更新角色、首頁寫入）不取域鎖；入域寫端失敗腿之顯式回滾源碼釘逐支在案。
- **SC-006**: 判定面同步可證——五支觸發寫端各至少一案「資料庫歸檔＋判定面零命中（未重啟）」；刪除前先斷言判定面確實命中（防恆綠）；零政策列刪除、被拒、無作用、標的不存在、無按鈕碼變更各一案零同步（同步結果計數零增）；壞連線注入下 R_SUPER 既有授權續放行且告警與計數可查、
  重試耗盡維持舊面；交錯時序案證較晚 commit 不被蓋回；三支併發同步全數完成；三道名冊守恆與「就地清空重載必轉紅」各以植入反例證非 vacuous。
- **SC-007**: 零繼承端到端——選單維（同路由名刪後重建）與角色維（同代碼刪後重建＋直種指派）各一案，資料庫面與判定面雙斷言零繼承（刪除前先斷言判定面確實命中）；復原選單不回灌授權一案。
- **SC-008**: 分頁規則逐端點釘住——四個清單端點各至少四案（缺席、逾界、`&size=0&current=0`→(1,1)、壞形整串預設〔三支＝1／10、選單治理清單＝全取〕）；選單治理清單無 size 全取一案且其專用入口恰一處生產呼叫之名冊案在案；IP 規則清單既有契約案零改形全綠。
- **SC-009**: 歸檔寫入正確——三 reason 各一案且皆屬不可復原集（成員測試）；角色刪除之歸檔列來源角色 id 等於該角色（掃描先於軟刪之證）；非絕版移除零歸檔一案；跨維同字面誘餌列不被連坐一案；各配變異紅證。
- **SC-010**: 連帶零退化——模糊搜尋共用件之轉義案、具型交易簽章後 IP 規則既有案全綠；信任模型非法標頭名一正一反＋反案＋對拍四案綠、降級來源名冊仍恰八；系統設定寫端空字串行為之既有案零改形全綠；
  IP 規則清單未知類型列於管理頁以原字串呈現。
- **SC-011**: CDP 三方對照（rev5 22080 vs rev6 32080、必要時加 upstream 22089）以**結構清單逐項全等**為判準（表格欄位集合與列序／搜尋器項目／按鈕集合與權限顯隱／抽屜與彈窗欄位與校驗訊息／分頁列形／回收桶流程／toast 文案；
  另含已刪模式寫入口不現、備註欄），任一項不等即紅；間距／字體／顏色只記入走查紀錄、不擋收刀；已知態各款以「觀察路徑→症狀」實際操作觀察記錄；排除清單＝rev5 22080 之 006～008 增量（三顆授權彈窗接真、角色抽屜之端點權限鈕與其彈窗、policy-archive 頁、user 頁、audit 頁）＋已知態各款＋治理清單三列路由裸鍵＋請求次數維度＋rev6 翻案腿（受保護選單停用／改父、href、按鈕碼清單之拒因）與 `protectedMenu` 譯文改寫造成之 toast 差異；
  role 與 user 頁表頭對 upstream example 驗新增批刪鈕仍在；常量選單端到端一步（FR-021）通過；編輯請求之 body 以網路請求事件斷言不含不可變欄。
- **SC-012**: 治理面全綠——憲法 1.5.0 且 accepted 前 base-web 既有檔零 diff（git 史可證）；新用途列被名冊載入器讀進（變異自證）；修改型標記只出現於九檔、兩顆授權彈窗零 diff、`components.d.ts` 只有兩行增列；
  各新增圈界塊拔標記必紅；docsync lint 零錯誤。
- **SC-013**: 機器守非 vacuous——BL-00111 lint（含別名匯入腿）、i64 守衛三件、wire 鍵集表驅動斷言、前端查詢串前提錨（含「收窄判跳過時仍執行」自測）各以植入反例證必紅；wire 受審名冊涵蓋本刀新增全部型（以抽取現算）。
- **SC-014**: 測試基建不連坐——dev 庫存在走查殘列時容器內全量測試全綠；守衛以現讀值還原序列（寫死值零殘留）；指派列清理序反腿之自證在案；跑全量前後走查基準 diff rc 0；走查工具還原擴面後 diff rc 0 且提示重啟。
- **SC-015**: 交付鏈全綠（FR-079）——後端全量測試容器內 serial 全綠、前端型別檢查綠、全部閘零紅、手動端到端走查（入口 `http://127.0.0.1:32080`）全數通過、走查後 diff rc 0。
- **SC-016**（★收刀面子句於簿記 commit 後驗）: 治理帳本結清——六支 ADR 全數 accepted 且 `feature_close.adrs` 列全；`backlog_done` 19 條、條文改寫 3 條、`backlog_add` 零與 FR-078 相符；
  NOTES 下一步指 006；活書各節現在式更新、四形種子枚舉之假述零殘留。

## Assumptions

- rev5 為本機可達之唯讀參考庫（凍結 SHA 由 bootstrap 斷言）；應用碼全程重打字消化、註解 rev6 語境重寫、前代出處帶 `rev5:`；藍本取前代 HEAD 形（005 收刀後本域修補自首版帶入）並逐檔剔除 006～008 之能力增量
  （授權寫面、reason gate 五值、支撐讀其餘兩支、授權回收桶、授權彈窗接真、使用者域、no-escalation、稽核頁）；翻案與新增項（判定面同步觸發擴及角色刪除、部分更新空字串語意、治理清單無 size 全取、
  已刪清單缺席 size、受保護選單兩腿、href 與按鈕碼形制、非法標頭名只告警、表頭 prop 形、getAllPages 提前且依域歸選單 handler〔前代住角色 handler、不承〕、測試守衛形〔寫死值還原→arm 當下現讀值還原〕、譯文權威〔刀內鍵表→三檔 locale 各為該語之家〕、IP 域已知態載體〔以新 ADR supersede ADR-00040〕）入 plan research 差異點表、烤入 implementer 防回歸清單。
- **零 migration、零 seed 變更＝事實非選擇**（FR-002）；本刀非一次性遷移、Risk／Guard／Rollback 三欄表免附。
- **clarify 必問四項**（brainstorm R1-Q1：首輪 SDD 之 clarify 已問過前三項、user 選重做時重新出題）——已全數由本 spec Clarifications Q1～Q4 定案（皆同 rev5 as-built）：①編輯清除自身常量性而存常量後代時是否拒（FR-021；★已由 Clarifications Q1 定案＝拒）
  ②角色掛載計數是否含停用或已刪使用者之指派（FR-014；★已由 Clarifications Q2 定案＝算進去、不濾）③批次刪除含查無 id 是否整批拒（FR-037；★已由 Clarifications Q3 定案＝整批拒）④批次內重複 id 是否先去重（FR-037；★已由 Clarifications Q4 定案＝先去重）。
- **新增路徑名稱空字串亦拒**（FR-012、FR-029）：與更新路徑同式（ADR⑥ 之延伸；★已由 Clarifications Q5 定案）；upstream 表單本即必填、UI 零差異。
- **判定面同步之單行程前提**：現行部署為單服務單實例；跨行程通知不在本刀（翻案觸發記 ADR）。
- **原 clarify 候選已轉工程判斷、本 spec 直接採用**（brainstorm §5 所列十三項，含共用件落點、分頁 helper 與四端點改引、前端查詢串前提錨落點、i64 lint 收法、契約落點、守衛形、CDP 排除清單與模型、
  getAllPages 落點、非法標頭名形、BL-00111 lint 形、第二輪工程判斷 21～43）；其中 user 可見者皆已經 brainstorm 第二輪拍板。
- **契約落點**：刀內 wire 契約住本 spec 目錄之 contracts；跨端點分頁規則住活書 08；004 IP 契約凍結不改、其與 as-built 之差由活書與 git 史解釋（快照無法表達數值界、上界由 contract test 釘）。
- **稽核覆蓋不對稱屬刻意最小改動**：系統設定寫端維持不落操作稽核列（002 刀 spec）；本刀為角色與選單寫端落列。
- **前端語言面不擴**：沿用兩語 runtime locale＋繁中錨點檔；錨點檔只承載後端訊息鍵。
- **前端零測試框架**：前端執行單元之 TDD 迴圈退化為型別檢查＋機器斷言＋兩段 review＋CDP 對照走查。
- **Amendment 與 ADR 親決時點**：plan 期全數產草稿；Amendment 與施工前提三支於 tasks 首個主線任務親決；已知態兩支於治理單元親決（004 T064 形）。
- **TDD 發射前置**：編排骨架全角色 opus 1M xhigh、prompt 首行帶深思關鍵詞（2026-09-23 起骨架現值）；CDP 操作一律 opus。
- **實作紀律引用**（非本 spec 新拍板）：rust build／test 容器內全程 serial；每單元 pin bump；review 只讀不寫；rev5 樹唯讀令烤入 agent prompt。
- **stakeholder 判定承 001～004 前例**：本刀 stakeholder＝admin 後台之超級管理員與 workspace 維護者；spec 中的端點路徑／碼／政策座標／軌道名／閘與工具名／常數係交付物座標（WHAT）與治理設施引用，非實作技術選型（HOW）。

### Out of Scope

- **三維授權治理**（getRoleMenu／updateRoleMenu／getRoleButton／updateRoleButton／getRoleEndpoints／updateRoleEndpoints）＋支撐讀 getAllButtons／getAllEndpoints＋授權回收桶讀端與授權復原——006（授權治理刀）。
- **結構性封死、島 G 條文入憲、policy-archive 頁（BL-00045）、兩顆授權彈窗接真**——006。
- **使用者域一切**（使用者備註欄、角色指派寫端、密碼面、解鎖按鈕〔BL-00091〕、會話面帳號活性閘〔BL-00065〕、設定跨鍵不變式〔BL-00031〕、通用節流 seam〔BL-00124〕）——007；007 須定「使用者軟刪是否清指派」（ADR③ 觸發）、
  並依 rev5:B-145 複核角色下拉是否帶停用角色。
- **稽核頁、設定頁、存取軌跡寫入面、設定清單排序**（BL-00027／BL-00043／BL-00044／BL-00045 之兩頁）——008。
- **no-escalation 本體**（BL-00048；本刀不動其空殼）；**列表排序能力**。
- **判定面跨行程通知**（多實例部署時再立 ADR）。
- **軟刪×歸檔之事後對賬掃描**（`rev5:B-025` 殘餘②→背景 job 刀）；**授權歸檔表之保留期與清理政策**（`rev5:B-016` 之歸檔表一面→須明確納入憲法 §I.7 島 J 或 C4-E2 資料血緣疊圖之承載）。
- **治理工具面拍板群**（BL-00002／BL-00035／BL-00036／BL-00039／BL-00101／BL-00102）——000-r3 等；**觀測面**（BL-00084／BL-00093 其餘子項）——觀測 profile 首起；滯後卷四條（BL-00029／BL-00049／BL-00064／BL-00067）不動。
- **demo 頁去留與第二 HTTP 客戶端**（BL-00064／BL-00067）。
- **RULES 改動**：預期零 RULES 表列改動（RULES-VERSION 不變）；若實作期需要，依輕量紀律另行拍板。
