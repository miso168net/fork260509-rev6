# Data Model — 005-role-menu-crud（Phase 1）

> ★本刀**零 migration、零 seed 變更**（spec FR-002；research R1）——本檔描述 001 基線既有結構之**消費形**、狀態機、序列化域、觸發矩陣與守門序，不含任何 DDL。承 `rev5:005` data-model 形、依 rev6 拍板改寫（research R3 清單 B）。
> wire 欄位逐欄定義住 `contracts/wire-role-admin.md`／`contracts/wire-menu-admin.md`；拒因鍵住 `contracts/msg-keys.md`；機器守判準住 `contracts/code-gates.md`。

## §1 既有資料表的消費面

### 1.1 `sys_role`（變體 A、六審計欄；seed 3 列、本刀首個寫入者）

| 欄 | 型 | 本刀消費 |
|---|---|---|
| `id` | bigint PK | wire number（2^53 守衛）；seed 1／2／3＝結構護欄（`SEEDED_ROLE_IDS`） |
| `role_code` | varchar NN | 形制 `^[A-Za-z0-9_]{1,64}$`；活性唯一（partial unique `sys_role_code_active_uniq … WHERE deleted_at IS NULL`）；建後不可變 |
| `role_name` | varchar NN | 非空（null／`""`＝`nameRequired`） |
| `role_desc`／`role_memo`／`role_home` | varchar／text／varchar 可空 | null 或 `""`＝落 NULL（新增同形）；`role_memo` 只上管理列表 |
| `status` | smallint 可空 | 寫入恰 1／2；讀端 `Some(1)`→`'1'`、其餘（含 NULL）→`'2'` |
| 軟刪兩欄 | — | 不上 wire；角色刪除單向、無復原 |

### 1.2 `sys_menu`（變體 A、29 欄；seed 78 列、本刀首個寫入者）

| 欄 | 型 | 本刀消費 |
|---|---|---|
| `parent_id` | bigint 可空 | NULL＝頂層；wire 0↔NULL（寫入 0 正規化 NULL、讀端 NULL→0；★絕不寫 0） |
| `menu_type` | smallint 可空 | 新增恰 1（目錄）／2（選單）、值域外取 1；讀端 `Some(1)`→`'1'`、其餘→`'2'`；建後不可變 |
| `route_name` | varchar NN | 形制 `^[A-Za-z0-9_-]{1,100}$`；活性唯一（`sys_menu_route_name_active_uniq`）；建後不可變；選單維授權錨 |
| `menu_name` | varchar NN | 非空 |
| `protected` | bool NN default false | 唯讀；受保護列不可刪、不可停用、不可改父；seed 8 列（1 home、2 manage、3～6、9、10） |
| `constant` | bool 可空 | 可寫；常量父鏈守（§5.3） |
| `buttons` | jsonb 可空 | null 或 `[{code, desc}]`；碼形制見 contracts；按鈕維授權錨之聯集源（治理域） |
| `href` | varchar 可空 | `""`→NULL；有值限 `http://`／`https://`（不分大小寫） |
| `query` | jsonb 可空 | 直傳（零驗；research R9） |
| `hide_in_menu`／`keep_alive`／`multi_tab`／`order`／`fixed_index_in_tab`／`icon_type` | 可空 | null＝落 NULL；`icon_type` 為三態狀態類欄：null＝清空落 NULL、非 null 值恰二值嚴格解析、值域外＝缺席（新增落 NULL、更新不動） |
| `route_path`／`component`／`icon`／`i18n_key`／`active_menu`／`menu_memo` | 可空文字 | null 或 `""`＝落 NULL（seed 既有 `icon=''` 三列不動） |
| `status` | smallint 可空 | 同角色 |
| 軟刪兩欄 | — | wire 以導出布林 `deleted` 表達；復原＝成對清空 |

### 1.3 `sys_user_role`（複合主鍵 `(user_id, role_id)`、兩條 FK `ON DELETE RESTRICT`）

本刀**零寫端**。角色掛載計數之源：`total = count(*) WHERE role_id = $1`（不 join 使用者、不濾啟停與軟刪；Clarifications Q2）、`operator_is_member = exists(user_id = 操作者 AND role_id = $1)`、`others = total − operator_is_member`。self-role 口徑＝操作者之全部指派列（含停用角色）。測試直種構造守門腿；清理序指派列先於角色列（FK RESTRICT）。

### 1.4 `casbin_rule`（授權真相；seed 163 列）

本刀只觸及**移除面**：掃描後以 id 圈定 DELETE（搬入歸檔）。維度欄 `v2`：`menu`／`button`／HTTP 動詞（端點維）；`v0`＝角色代碼、`v1`＝路由名／按鈕碼／路徑。治理三欄（`protected`／`created_at`／`created_by`）對判定引擎轉接器不可見。★掃描 MUST 依維度過濾（路由名與按鈕碼值域可重疊）。

### 1.5 `sys_casbin_policy_archive`（14 欄；seed 0 列、本刀首個寫入者）

寫入＝完整快照（`ptype`、`v0`～`v5`、原 `created_at`／`created_by`）＋`role_id`（以 `v0` 反查**活性**角色、查無 NULL）＋`archived_at`／`archived_by`＋`archive_reason`。本刀三 reason：`role_soft_delete`／`menu_soft_delete`／`menu_button_removed`，全屬不可復原集（`is_non_restorable_reason` 單點 fn、三值成員測試）。三自由度（`role_id` 可空、無 `protected` 快照欄、無 `menu_id` 同實例欄）全不動（ADR-00044）。讀端與復原屬授權治理刀。

### 1.6 `sys_operation_log`（append-only；004 首寫）

每支寫端成功且有業務寫入時同交易恰一列（批次＝逐標的一列）；`operation` 沿既有小寫封閉集之 `add`／`update`／`delete`／`restore`（零新 variant）；`entity_table`＝`sys_role`／`sys_menu`；提前 no-op 零列。

## §2 狀態機（每列「現態×事件→次態＋副作用」；副作用皆同一交易）

### 2.1 角色

| 現態 | 事件 | 次態 | 守門（固定序）與副作用 |
|---|---|---|---|
| （無） | addRole | 活性·啟用或停用 | §5.1；零授權；稽核 `add` |
| 活性 | updateRole（非停用） | 活性 | §5.2；稽核 `update` |
| 活性·啟用 | updateRole（停用） | 活性·停用 | ＋停用雙護欄；**不**同步判定面（授權讀端每請求濾角色狀態） |
| 活性 | updateRoleHome | 活性 | 不驗可見樹；非部分更新、同值亦寫；稽核 `update` |
| 活性 | deleteRole | 已刪（單向） | §5.3；先歸檔全三維（含 protected）→ 軟刪 → 稽核 `delete`；commit 後若實際歸檔 ≥1 列＝同步判定面 |
| 已刪 | 任何寫端 | —— | `notFound` |

### 2.2 選單

| 現態 | 事件 | 次態 | 守門與副作用 |
|---|---|---|---|
| （無） | addMenu | 活性 | §5.4；零授權（兩步流第一步）；稽核 `add` |
| 活性 | updateMenu | 活性 | §5.5；絕版碼歸檔（`menu_button_removed`）；commit 後若按鈕碼絕版實際歸檔 ≥1 列＝同步；稽核 `update` |
| 活性 | deleteMenu | 已刪 | §5.6；先歸檔（選單維跨全角色＋獨有按鈕碼，`menu_soft_delete`）→ 軟刪 → 稽核；commit 後若實際歸檔 ≥1 列＝同步 |
| 已刪 | restoreMenu | 活性（原 status 保留） | §5.8；成對清空軟刪欄；零授權寫、零同步；稽核 `restore` |
| 活性 | restoreMenu | —— | `notFound`（非冪等成功） |

★停用＝暫時下架、非撤銷：治理域讀端含停用列；絕版判定聯集含停用列。幽靈父收縮（顯示域）語意不動。

### 2.3 判定面（記憶體授權判定實體）

| 現態 | 事件 | 次態 | 語意 |
|---|---|---|---|
| 良好面 G | 觸發同步（§4） | 重建中（G 續服務） | 取 `RELOAD_SERIAL` → 另建新實例 |
| 重建中 | 重建成功 | 良好面 G′ | 寫鎖內一步換上、`outcome=ok` |
| 重建中 | 第 n 次重建失敗（n＝1..3） | 重建中 | 每次 `outcome=retry`、error log；n<3 時退避 50ms×n 後重試（末次失敗後不退避） |
| 重建中 | 第 3 次失敗後 | 良好面 G（舊） | 另計 `outcome=exhausted`、error log（三次全敗＝retry 3＋exhausted 1）；耗盡窗內已歸檔授權仍在記憶體面（＝島 H2 條文所載之已知降級窗）、恢復靠下次成功同步或重啟 |

★絕不就地清空重載；呼叫者不持判定面讀鎖；前提＝單一 rust-api 行程（ADR-00043）。

## §3 選單序列化域

- **載體**：`pg_advisory_xact_lock(0x7265_7636_6D65_6E75)`（ASCII `rev6menu`、= 8243124669107236469；高 32 位 1919252022、低 32 位 1835363957）；xact 級自動釋放、零逾時零重試。
- **成員（進域寫端）**：addMenu／updateMenu／deleteMenu／batchDeleteMenu／restoreMenu＋deleteRole／batchDeleteRole；**不進域**：addRole／updateRole／updateRoleHome（零授權面、零選單資料）。空陣列批刪不取域鎖。
- **規則**：域鎖＝交易首動作——handler 外殼 begin 後緊接呼叫之內層 `<op>_in_txn(&txn, …)` 首句取得（源碼釘守「外殼 begin 後第一個呼叫即內層」）；facade 寫端不自取。固定鎖序＝advisory → 歸檔表列 → `sys_role` 列 → `sys_menu` 列 → `casbin_rule`。
- **無 ABBA**：①key 空間不碰撞（per-user 鎖＝裸 uid）②鎖集合零交集（login 交易不取域鎖、域內寫端不取 per-user 鎖）。失效條件三（ADR-00043）：角色寫端連動撤會話、使用者域寫端進域、同 key 跨交易嵌套重入。

## §4 判定面同步觸發矩陣（恰五支；「成功且實際歸檔 ≥1 列」為門）

| 寫端 | 觸發條件 | 不觸發 |
|---|---|---|
| deleteMenu | 軟刪成功且實際歸檔 ≥1 列 | 被拒／標的不存在／零政策列 |
| batchDeleteMenu | 整批成功且整批合計實際歸檔 ≥1 列（至多一次） | 被拒／空陣列／合計零 |
| updateMenu | 按鈕碼絕版實際歸檔 ≥1 列 | 一般欄變更／無按鈕碼變更／非絕版移除／被拒／no-op |
| deleteRole | 軟刪成功且實際歸檔 ≥1 列 | 被拒／零政策列（本刀生產面常態） |
| batchDeleteRole | 整批成功且整批合計實際歸檔 ≥1 列（至多一次） | 被拒／空陣列／合計零 |
| 其餘寫端 | —— | addRole／updateRole（含停用）／updateRoleHome／addMenu／restoreMenu／選單啟停 |

觸發點＝交易 commit 成功之後、以 facade 回傳之歸檔列數為門（早退結構性保證）；ADR-00043、契約與 spec FR-050 同字面。

## §5 守門固定序（多重違規取先序腿；凍結入契約）

### 5.1 addRole（不進域）
操作者上下文（缺席 `5000`）→ 代碼形制（`codeInvalid`）→ 名稱非空（`nameRequired`）→ 活性唯一先驗（`codeExists`）→ INSERT（唯一索引 `sys_role_code_active_uniq` 之 23505 收窄兜底→`codeExists`；其餘 DB 錯→`5000`）→ 稽核。

### 5.2 updateRole（不進域）
操作者上下文 → 提前 no-op（除 `id` 外全欄經值域收斂後缺席＝成功零變更零稽核）→ 名稱非空（名稱出現且為 null 或 `""`）→ 鎖列（`FOR UPDATE`；查無或已刪＝`notFound`）→ 代碼出現（`codeImmutable`）→ 停用雙護欄（status 解析為停用時：操作者為成員＝`cannotDisableSelfRole` → 標的為 R_SUPER＝`superCannotDisable`）→ UPDATE → 稽核。

### 5.3 deleteRole／batchDeleteRole（進域）
操作者上下文 → （批：空陣列提前成功；去重）→ begin → 域鎖 → 逐 id 升冪：鎖列（查無或已刪＝整批 `notFound`）→ seeded（`seededProtected`）→ in-use（`others > 0`＝`inUse`）→ self-role（`cannotDeleteSelfRole`）→ 全數通過後逐標的：歸檔 `v0=role_code` 全三維含 protected（`role_soft_delete`）→ 軟刪 → 稽核 → commit → 實際歸檔 ≥1 列（批＝整批合計）＝同步。

### 5.4 addMenu（進域）
操作者上下文 → begin → 域鎖 → 父驗證（`parentId` 0 或缺席豁免；父不存在或已刪＝`parentNotFound`；停用不擋）→ 防環（新增無自身、上溯鏈遇環或逾 64 跳＝`cycleDetected`）→ 路由名活性唯一先驗（`routeNameExists`）→ 常量父鏈（常量標的且非頂層：全祖先須常量、鏈斷保守拒＝`constantParent`）→ 路由名形制（`routeNameInvalid`）→ 名稱非空（`nameRequired`）→ href 形制（`hrefInvalid`）→ 按鈕碼清單形制（`buttonsInvalid`）→ INSERT（23505 收窄兜底→`routeNameExists`）→ 稽核 → commit。

### 5.5 updateMenu（進域）
操作者上下文 → 提前 no-op → 名稱非空 → begin → 域鎖 → 鎖列（`notFound`）→ 不可變欄出現（`routeNameImmutable` 先於 `menuTypeImmutable`）→ 受保護列：status 解析為停用或 `parentId` 變更（`protectedMenu`）→ `parentId` 變更時父驗證（`parentNotFound`）與防環（`cycleDetected`）→ 常量父鏈（效值為常量且（改父或 constant 出現）：驗全祖先；constant 出現且效值非常量：反查治理域全深後代存常量者＝`constantParent`）→ href 形制 → 按鈕碼清單形制（先於絕版計算）→ 絕版計算（舊碼−新碼，排除標的自身之聯集；絕版者按鈕維歸檔 `menu_button_removed`）→ UPDATE → 稽核 → commit → 按鈕碼絕版實際歸檔 ≥1 列＝同步。
★「`parentId` 變更」＝出現且 0→NULL 正規化後 ≠ 現值；同值＝無變更（research R9）。

### 5.6 deleteMenu（進域）
操作者上下文 → begin → 域鎖 → 鎖列（`notFound`）→ 受保護（`protectedMenu`）→ 存在未刪子項（不論啟停；`hasChildren`）→ 歸檔（選單維 `v1=route_name AND v2='menu'` 跨全角色＋獨有按鈕碼之按鈕維 `v2='button'`；皆 `menu_soft_delete`）→ 軟刪 → 稽核 → commit → 實際歸檔 ≥1 列＝同步。

### 5.7 batchDeleteMenu（進域）
操作者上下文 → 空陣列提前成功 → 去重 → begin → 域鎖 → 鎖讀全部標的（任一查無或已刪＝整批 `notFound`）→ 拓撲序（深度 DESC、id DESC；子先於父）逐項全套 §5.6 守門（「未刪子項」判定排除同批已刪者）→ 任一違規整批拒（rollback）→ 逐項歸檔＋軟刪＋稽核 → commit → 整批合計實際歸檔 ≥1 列＝至多一次同步。

### 5.8 restoreMenu（進域）
操作者上下文 → begin → 域鎖 → 鎖列（標的須為已刪存在，否則 `notFound`）→ 同路由名活性衝突（`restoreConflict`；23505 收窄兜底同鍵）→ 父未刪（`parentNotFound`；頂層豁免）→ 常量標的之全祖先常量性（`constantParent`；非常量標的零驗）→ 成對清空 `deleted_at`／`deleted_by`、原 status 保留 → 稽核 → commit；零授權寫、零同步。

### 5.9 updateRoleHome（不進域）
操作者上下文 → 鎖列（`id` 缺席或壞形收斂為 0 → `notFound`）→ `home` 缺席、null 或 `""`＝NULL、否則原值 → UPDATE（同值亦寫）→ 稽核。

★一切擁有交易之入域寫端：失敗腿顯式 `rollback` 後回錯（源碼釘逐支）。

## §6 歸檔寫入不變式

1. 歸檔掃描 MUST 早於標的列軟刪 UPDATE（否則 `role_id` 反查全落 NULL）。
2. 絕版判定聯集＝治理域（未刪含停用）全部選單之按鈕碼、MUST 排除標的自身。
3. 掃描依 `v2` 維度過濾（選單維 `menu`、按鈕維 `button`；角色刪除掃全三維）。
4. 「獨有按鈕碼」（deleteMenu）＝標的按鈕碼 −（治理域其餘選單之按鈕碼聯集）。
5. facade 歸檔 fn 回傳歸檔列數（觸發門之唯一依據）。

## §7 分頁規則（四清單端點）

| 端點 | 缺席 `current`／`size` | clamp | 壞形查詢串 | 排序 |
|---|---|---|---|---|
| getRoleList | 1／10 | current [1, 10^7]、size [1, 100]；0 取下界 | 整串收斂預設 | id ASC |
| getDeletedMenus | 1／10 | 同上 | 同上 | `deleted_at DESC, id DESC` |
| getIpRuleList（004、改引） | 1／10 | 同上 | 同上 | id DESC（不變） |
| getMenuList/v2 | ★`size` 缺席＝全取（回應 `current=1`、`size`＝實得頂層數） | 帶 `size` 時同上 | 收斂預設＝`size` 缺席＝全取 | 頂層與子樹同層序 `(order ASC NULLS LAST, id ASC)` |

逾界 `current` 回空頁、回應 `current`＝上界值。頂層＝父為 NULL 或父不在治理域集合（孤兒升根、`total` 計入；僅直改庫可達）。零頂層不可達（受保護頂層列不可刪）。常數與明名入口住 `envelope.rs`（research R8）。

## §8 wire 映射規則

| 規則 | 內容 |
|---|---|
| `status`（兩域）與新增路徑之 `menuType` | 非三態；寫入 trim 後恰 `"1"`／`"2"`，其餘（含 `""`、null）＝缺席；更新路徑之 `menuType` 不經解析、出現即拒；讀端 `Some(1)`→`'1'`、其餘→`'2'` |
| `iconType` | 三態；寫入 null＝清空落 NULL、trim 後恰 `"1"`／`"2"`＝設值、其餘（含 `""`）＝缺席（新增＝NULL、更新＝不動）；讀端 NULL→null、`Some(2)`→`'2'`、其餘→`'1'` |
| 頂層 | `parentId`／`pId`＝0 ⇔ DB NULL；孤兒列 `parentId` 顯 DB 原值、在樹中升根（`pId`＝0） |
| 時間 | RFC3339 帶 offset；`updatedAt` 可空 |
| 操作者 | `createdBy`／`updatedBy`＝帳號名（單次批次回填、查無 null） |
| 導出 | 選單 `deleted`＝`deleted_at IS NOT NULL`；角色列不上軟刪欄 |
| id | number、2^53 fail-loud 守衛 |

## §9 測試資料與守衛（research R11）

- 守衛表集＝`sys_role`／`sys_menu`／`casbin_rule`／`sys_casbin_policy_archive`／`sys_user_role`（皆 gate2 逐列比對、非 runtime-append）＋既有 `sys_operation_log` 水位窗。
- 水位＝`COALESCE(max(id) FILTER (WHERE id < 9_300_000_000), 0)`（界值＝`SYNTHETIC_UID_FLOOR`；五表同套）＋序列 `(last_value, is_called)`，皆 arm 時現讀；Drop 刪 `id >` 水位（號段內顯式大 id 列恆被清）、再 setval 回現讀值；指派列刪除集＝arm 快照鍵集差 ∪ `role_id >` 角色守衛水位者、先於角色列。
- seed 態序列期望（`sys_role_id_seq=(3,true)`／`sys_menu_id_seq=(78,true)`／`casbin_rule_id_seq=(163,true)`／`sys_casbin_policy_archive_id_seq=(1,false)`）只作守衛自證前提、不作還原目標。
- 造列：角色／選單／指派＝顯式大 id、號段依「表×檔」於 `test_kit.rs` 單一常數表登記（含 tests 側檔列；tests 側同值字面自持並以 `include_str!` 對賬）；`casbin_rule`＝經真判定面新增政策路徑取 nextval。

## §10 msg key 名冊

既有 19 鍵＋本刀 24 鍵（`biz.role.*` 10、`biz.menu.*` 14）；逐鍵發出點與語意要求見 `contracts/msg-keys.md`；譯文之家＝三檔 locale `backend` 子樹（ADR-00039）。
