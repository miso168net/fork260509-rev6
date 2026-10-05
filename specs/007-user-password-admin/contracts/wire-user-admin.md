# Contract — 使用者管理十端點（＋unlockLogin 帳號維包含規則）

> 權威序依憲法 §I.3：base-web 實碼 ＞ 官方 docs ＞ mock。使用者管理頁為 upstream demo 面（`views/manage/user/` 以 `Api.SystemManage.User` 家族之 mock 形接線），其所需之十支讀寫端點即本刀補齊面；契約以 `rev5:007` 之 `contracts/wire-user-admin.md` 與其 HEAD as-built（`rev5:server/src/handler/user.rs`、`rev5:server/src/handler/throttle.rs` 帳號維段、`rev5:src/typings/api/rev5-user-admin.d.ts`）為藍本、依 rev6 拍板改寫（差異見文末「與 rev5 wire 逐欄比對」、理由住本刀 research R5），由本檔凍結（spec 目錄＝定點快照；wire 活體權威＝碼＋`tests/contract.rs`＋wire-schema 快照）。
> 信封、錯誤碼總則同 005 刀 `contracts/wire-role-admin.md` 檔頭：信封 `{data, code, msg}`、業務錯誤 HTTP 200（例外恰二 `4040`→404、`5003`→403）；未登入 `8888`；無授權 `5003`；寫端先取操作者上下文（缺席或 `real_ip` 不可解析＝`5000` 拒寫、不落稽核列，先於一切守門與提前 no-op）；其餘資料庫錯 `5000`；授權中介層不讀 body；動詞不符 `4040`。拒因純 i18n key、一因一鍵；★錯誤信封 `data` 恆 null 之唯二例外＝密碼兩鍵（`biz.user.passwordPolicy`／`biz.user.pwdSetTooFrequent`）攜明細物件，其信封形、data 兩形與前端轉譯之家＝`wire-user-center.md` §3（FR-004；ADR-00076）；`5003` 恆純 key、不洩差集。
> 十條皆 `Protection::Policy`、路徑×動詞逐字對齊 001 刀凍結 seed 之政策列（量法：`rust-api/migration/src/m0002_baseline_seeds.rs` 之 casbin seed 逐路徑 `grep`：getUserList 2 列〔列 1 R_SUPER、列 2 R_ADMIN〕，其餘九支各恰 1 列、只授 R_SUPER；唯列 68 updateUserSessionPolicy `protected=TRUE`＝封死集成員〔島 G 之 G6〕）；m0003 不動任何端點維列（ADR-00085）。後端 handler 住新建 `rust-api/server/src/handler/user.rs`（新域：自有 target `security.user`、本域 `BODY_FALLBACK_MSG`、私有 `operator_from`／`db_failure`）。
> 型別檔＝新建 `base-web/src/typings/api/rev6-user-admin.d.ts` 之 `Api.UserAdmin`（不併入 `Api.SystemManage`：該節之 upstream `User`／`UserSearchParams`／`UserList` 同 URL 而欄名與可空性不同＝偏離帳 ADR-00083）；wrapper＝新建 `base-web/src/service/api/rev6-user-admin.ts`（十一支：本檔十支＋既有端點 unlockLogin 一支；不入 barrel、直接路徑 import；錯誤不加工——拒因 toast 與兩鍵明細轉譯由 `service/request` 之 onError 鏈統一處置，呼叫端只判 `error` 有無）。兩檔檔頭一行新增型標記（字面＝`contracts/code-gates.md` §1）。

## 端點總表

| # | 端點 | seed 列（授權態） | 鎖與交易 | case_key（新建） | handler（新建） | fetcher（新建） | 成功 `data` | 前端消費者 |
|---|---|---|---|---|---|---|---|---|
| 1 | `GET /systemManage/getUserList` | 1 R_SUPER、2 R_ADMIN | 零鎖零交易 | `get-user-list` | `handler::user::get_user_list` | `fetchGetUserList(params?)` | `PageRes<UserRecord>` | 現役清單＋搜尋卡 |
| 2 | `GET /systemManage/getDeletedUsers` | 155 | 零鎖零交易 | `get-deleted-users` | `handler::user::get_deleted_users` | `fetchGetDeletedUsers(params?)` | `PageRes<UserRecord>` | 回收桶模式 |
| 3 | `POST /systemManage/addUser` | 17 | 交易；無 advisory、鎖 N 之角色列 | `add-user` | `handler::user::add_user` | `fetchAddUser(data)` | `null` | 新增抽屜 |
| 4 | `POST /systemManage/updateUser` | 18 | advisory＋列鎖＋角色列鎖 | `update-user` | `handler::user::update_user` | `fetchUpdateUser(data)` | `null` | 編輯抽屜 |
| 5 | `DELETE /systemManage/deleteUser` | 19 | 同上（鎖 T） | `delete-user` | `handler::user::delete_user` | `fetchDeleteUser(id)` | `null` | 列「刪除」 |
| 6 | `DELETE /systemManage/batchDeleteUser` | 20 | 整批 advisory→列鎖→T 聯集角色列鎖 | `batch-delete-user` | `handler::user::batch_delete_user` | `fetchBatchDeleteUser(ids)` | `null` | 表頭批刪 |
| 7 | `POST /systemManage/restoreUser` | 152 | advisory＋已刪列鎖 | `restore-user` | `handler::user::restore_user` | `fetchRestoreUser(id)` | `null` | 回收桶「復原」 |
| 8 | `POST /systemManage/kickUser` | 154 | advisory＋列鎖 | `kick-user` | `handler::user::kick_user` | `fetchKickUser(id)` | `KickRes` | 列操作「踢除下線」 |
| 9 | `POST /systemManage/resetUserPassword` | 151 | advisory＋列鎖（雜湊於鎖前） | `reset-user-password` | `handler::user::reset_user_password` | `fetchResetUserPassword(data)` | `null` | 「重設密碼」浮層 |
| 10 | `POST /systemManage/updateUserSessionPolicy` | 68（受保護＝封死集） | advisory＋列鎖 | `update-user-session-policy` | `handler::user::update_user_session_policy` | `fetchUpdateUserSessionPolicy(data)` | `null` | 抽屜會話政策欄（改動時另打） |
| — | `POST /systemManage/unlockLogin`（既有） | 148 | 帳號維改交易形（§11） | 既有 `unlock-login` | 既有 `handler::throttle::unlock_login` | `fetchUnlockLogin(data)`（新建） | `null` | 列操作「解鎖登入」＋IP 規則頁「解鎖來源 IP」 |

- 本檔十條＝GET 2／POST 6／DELETE 2；連同 `wire-user-center.md` 兩條：ROUTES 49→61、政策保護 35→45（GET 15→17／POST 15→21／DELETE 5→7）、Authed 3→5、Public 11 不變（量法：解析 `rust-api/server/src/router.rs` 之 ROUTES 區塊逐條 `protection`×`method`）；`ROUTES_COUNT` 與 contract registry 同 commit 變為 61（FR-001）。
- 十二條接 ROUTES 表尾、相對次序依 `rev5:server/src/router.rs`（getUserList、getDeletedUsers、addUser、updateUser、deleteUser、batchDeleteUser、restoreUser、kickUser、resetUserPassword、updateUserSessionPolicy、getPasswordPolicy、changePassword）。case_key 依 rev6 慣例：`/systemManage/<名>`＝名之 kebab 形、`/userCenter/<名>`＝`user-center-` 前綴（同 `/auth/*` 之 `auth-` 形）；rev5 之 `user-get-list` 等形不帶回。
- 讀端零鎖、零交易、零稽核；寫端 handler 持交易（外殼 begin → 內層 `<op>_in_txn` → 稽核 → commit、失敗腿顯式 rollback；005 刀 `handler/role.rs` 同形）；使用者域寫端**零授權重載**（判定面只載 `p` 列、角色每請求現查；`RELOAD_CALL_FILES` 零擴列）、**不入選單序列化域**（FR-011）。

## 共用型（rust DTO 與 `Api.UserAdmin.<型>` 同名；宣告序＝wire 欄序；camelCase）

定名規則（本檔與 `wire-user-center.md` 共用、只住本句）：型名＝rust DTO 名＝typings 型名。寫端請求與回應沿 `rev5:007` **typings** 名（`AddReq`／`UpdateReq`／`ResetPasswordReq`／`KickRes`／`UpdateSessionPolicyReq`／`UnlockReq`／`SessionPolicy`；個人中心 `PasswordPolicyView`／`ChangePasswordReq`），清單列與 query 取實體前綴形（`UserRecord`／`UserRole`／`UserListQuery`／`DeletedUserListQuery`），`{id}`／`{ids}` 取 rev6 `<實體>IdReq`／`<實體>BatchDeleteReq` 慣例（005 刀 `RoleIdReq`／`MenuIdReq` 先例）。★與 006 刀規則（型名＝rev5 後端名）之差：`rev5:007` 本域後端名（`AddUserReq`／`UserSearchParams`…）與其 typings 名分岔，本刀取 typings 名使兩側同名（rust 模組路徑 `handler::user::` 已帶實體）。兩側不新宣告泛型（`GENERIC_WIRE_TYPES` 不變）。`UnlockReq` 之 rust 側為既有 `handler::throttle::UnlockReq`（004 刀）；`SessionPolicy` 為 typings 專屬封閉字面聯集（rust 寫端以 `String` 承載、值域判定住 facade，與 facade 列舉 `sys_user::SessionPolicy` 不同層）。其餘為新建件（量法：`git -C rust-api grep -nw` 與 `git -C base-web grep -nw` 於 pin 樹：`UserRecord`／`UserRole`／`UserListQuery`／`DeletedUserListQuery`／`UserIdReq`／`UserBatchDeleteReq`／`ResetPasswordReq`／`KickRes`／`UpdateSessionPolicyReq` 皆零命中；`AddReq`／`UpdateReq` 之命中全在 `rust-api/server/tests/wire_schema.rs`，為 IP 規則與系統設定型之散文簡稱及常數 `UPDATE_REQ_DEF`〔系統設定型〕、非同名型——本刀 definition 常數須另取不撞名之名＝`contracts/code-gates.md` §4）。本檔為使用者域 wire DTO 型名之家（data-model §12 指回 contracts；§6 只載映射規則）。

| 型 | wire 形 | 方向 | 說明 |
|---|---|---|---|
| `UserRecord` | 十四欄（下表） | 讀 | 兩支清單之 `records` 元素 |
| `UserRole` | `{ id: number, roleCode: string, roleName: string }` | 讀 | `UserRecord.roles` 元素；`id` 過 2^53 守衛 |
| `SessionPolicy` | `'inherit' \| 'single' \| 'multi'` | 讀（請求面亦引） | 快照自成一支 definition（`Api.IpRule.RuleType` 先例） |
| `UserListQuery` | `CommonType.RecordNullable<Common.CommonSearchParams & { userName: string; nickName: string; userGender: string; status: string; userPhone: string; userEmail: string }>` | 請求（query） | getUserList；八欄皆可空 |
| `DeletedUserListQuery` | `CommonType.RecordNullable<Common.CommonSearchParams>` | 請求（query） | getDeletedUsers；只收分頁兩欄 |
| `AddReq` | 九欄（欄表下） | 請求（body） | addUser |
| `UpdateReq` | 九欄（欄表下；部分更新三態） | 請求（body） | updateUser |
| `UserIdReq` | `{ id: number }` | 請求（body） | deleteUser／restoreUser／kickUser 共用（收斂標籤 `deleteUser\|restoreUser\|kickUser`；005 刀 `MenuIdReq` 形） |
| `UserBatchDeleteReq` | `{ ids: number[] }` | 請求（body） | batchDeleteUser |
| `ResetPasswordReq` | `{ id: number, password: string }` | 請求（body） | resetUserPassword |
| `KickRes` | `{ revoked: number }` | 讀（寫端回應） | 本次實際撤銷之有效票數；`0` 為正常結果（標的本不在線）；rust `usize`（計數、不入 2^53 守衛面；006 刀 `RoleMenuGrantRes.revoked` 同取態） |
| `UpdateSessionPolicyReq` | `{ id: number, sessionPolicy: SessionPolicy }` | 請求（body） | updateUserSessionPolicy |
| `UnlockReq` | `{ dimension: 'user' \| 'ip', userName?: string \| null, target?: string \| null }` | 請求（body） | 欄集與 004 刀契約請求表逐欄同 |

### `UserRecord`（恰 14 欄、恆在場）

| # | 欄 | 型 | 來源與說明 | 頁面消費 |
|---|---|---|---|---|
| 1 | `id` | number | `serialize_i64_number_guarded` | 列鍵、寫端請求鍵 |
| 2 | `userName` | string | 建後不可變 | 帳號名欄 |
| 3 | `nickName` | string \| null | NULL＝顯式 null（誠實未填） | 暱稱欄 |
| 4 | `userGender` | string \| null | `smallint` 原值 `to_string`、NULL→null；不套 status 之二值收斂（「未填」不得變 `'2'`）；值域由寫端收斂維持 | 性別欄 |
| 5 | `userPhone` | string \| null | 原樣 | 手機欄 |
| 6 | `userEmail` | string \| null | 原樣（大小寫照存） | 信箱欄 |
| 7 | `status` | `Common.EnableStatus` | `common::db_status_to_wire`：`Some(1)`→`'1'`、其餘→`'2'`；恆非 null | 狀態欄 |
| 8 | `sessionPolicy` | `SessionPolicy` | 欄原值（寫端三值收斂） | 會話政策欄 |
| 9 | `userMemo` | string \| null | 渲染端 MUST 純文字插值（FR-019）；只出現於本檔兩支清單之 `UserRecord`、不入任何下拉、候選或他 API | 記事欄 |
| 10 | `roles` | `UserRole[]` | 全部指派列之角色（口徑＝T：只濾角色軟刪、**不濾狀態**；FR-020）；角色 id 升冪；整頁一次批次回填（`sys_user_role::roles_by_user_ids`、空頁不查）；回收桶列恆 `[]` | 角色欄以 `roleCode` 串接（rev5 HEAD 形）；抽屜以 `id` 對 getAllRoles 候選（經 `rev6-role-admin.ts` 之 `fetchGetAllRoles`；FR-053 擇一＝research R18）、不在候選者＝持有之停用角色→「（已停用）」灰色保留選項（以 `roleName` 呈現） |
| 11 | `createdAt` | string | RFC3339、偏移恆 `+00:00`（ADR-00061） | 原樣顯示 |
| 12 | `createdBy` | string \| null | 帳號名（非 uid；整頁 id 去重後一次 `sys_user::find_names_by_ids`、不濾軟刪；查無→null） | 建立者欄 |
| 13 | `updatedAt` | string \| null | 同 11 | 更新時間欄 |
| 14 | `updatedBy` | string \| null | 同 12 | 更新者欄 |

不上 wire（逐欄白名單、絕不序列化原始資料列；FR-005）：`password`（島 I5）、`session_id`（單一會話側信道）、`deleted_at`／`deleted_by`（回收桶序由 §2 固定序承載、不加刪除時間欄）。

### 兩支 query 型

後端以字串承接全部篩選欄（`Option<String>`；分頁兩欄 `Option<u64>`），清空之篩選欄經 qs 渲染為 `k=` 時不致整串收斂（005 刀 `RoleListQuery` 同理）；抽取器結構性無 reject 面（`Rejection = Infallible`）：查詢串壞形（`current=abc`、同名鍵重複）＝整串收斂為預設（第 1 頁、10 筆、無篩選），不放行框架 400 裸回應。前端首屏物件（upstream `Api.SystemManage.UserSearchParams` 形、搜尋卡續用）可直接賦給 `UserListQuery`。`DeletedUserListQuery` 另立：回收桶無篩選面（已刪模式隱藏搜尋卡），使「送得出的參數＝後端會濾的參數」在型面一致（`rev5:B-143` 之教訓）。

### `AddReq`／`UpdateReq` 欄表

| 欄 | `AddReq` | `UpdateReq`（三態：缺席＝不動、null＝清空、值＝設值） |
|---|---|---|
| `id` | — | `number`（必送；缺席或壞形＝0＝`notFound`） |
| `userName` | `string`（必送；後端寬鬆承載、缺席或 null＝空字串交形制守門） | `string \| null`（可選；★**出現即拒**——含 null、值同現值亦然＝`biz.user.userNameImmutable`；組 body 時不得帶；005 刀 `roleCode` 形） |
| `password` | `string`（必送；缺席或 null＝空字串交政策判） | — |
| `nickName`／`userPhone`／`userEmail`／`userMemo` | `string \| null`；缺席、null、空字串＝NULL | `string \| null`；null 或空字串＝清空落 NULL（Q16、ADR-00080）、值＝設值 |
| `userGender` | `string \| null`；trim 後恰 `'1'`／`'2'` 落值、其餘＝NULL | `string \| null`；null＝清空、trim 後恰 `'1'`／`'2'`＝設值、其餘值（含空字串）＝**缺席**（值域外不演成清空） |
| `status` | `string`；trim 後恰 `'1'`／`'2'` 落值、其餘＝預設啟用 | `string`（**非三態**：null＝缺席）；trim 後恰 `'1'`／`'2'` 才算出現（ADR-00047 決定 4 形） |
| `roleIds` | `number[]`；缺席或 null＝`[]`（零角色合法） | `number[]`（非三態：null＝缺席）；出現＝**期望全集**、全量替換（去重；空陣列＝全撤） |

- 兩型 `#[derive(Default, Deserialize)]`＋`#[serde(default, rename_all = "camelCase")]`、必填欄亦以 `Option` 承載（ADR-00047 決定 1）、三態欄掛 `common::tristate`；body 經 `handler::common::json_or_default(req, state, <端點名>, BODY_FALLBACK_MSG)`——缺席、壞 JSON、任一欄型別不符（例 `roleIds: ["a"]`）＝**整包**收斂為預設形、不作部分採用：addUser＝空帳號名＝`userNameInvalid`、updateUser＝`id=0`＝`notFound`（FR-009）。
- ★`AddReq`／`ResetPasswordReq`（與 `ChangePasswordReq`）**不 derive `Debug`**、手寫遮蔽密碼欄（恆印遮蔽字面、不印長度片段）；既有 `LoginReq` 同刀改遮蔽形並配機器釘（島 I5；`contracts/code-gates.md` §2）。
- 前端以具名型組 body（`const data: Api.UserAdmin.UserIdReq = { id };`）；更新 body **逐欄顯式構造**、不散開整列 record（FR-047）。

### 受審

上列十三型於快照各成 `Api.UserAdmin.<型>` definition、全數入受審名冊並各配正向＋反例（FR-064；`in_role_menu_sections` 謂詞擴 `Api.UserAdmin.`／`Api.UserCenter.` 前綴）：預期讀端冊 4（`UserRecord`／`UserRole`／`SessionPolicy`／`KickRes`）、請求端冊 9，連同 `wire-user-center.md` 五型合計 18——實數以抽取為準（側別判準＝`contracts/code-gates.md` §4）。重點反例：`roles` 元素為字串（rev5 形）或缺 `roleName`、`status` 為 null、`sessionPolicy` 值域外、`createdBy` 為 number、`userMemo` 鍵缺席、snake_case 鍵、`UpdateReq` 缺 `id`、`UnlockReq.dimension` 值域外。

## 寫端共同語意（端點 3～10）

1. **操作者上下文先於一切**（FR-006）：缺席＝`5000`——先於 body 判定與批刪之空陣列提前成功、不開交易、不補佔位稽核列。
2. **固定判定序**（FR-010；★多重違規取先序之拒因、此先後即契約）：①活性標的鎖讀 → ②seed 保護 → ③本人規則 → ④包含規則 → ⑤業務守門；任一拒＝整筆 rollback、零變更、零稽核、零撤票、零失效名單。逐支空格（kickUser／resetUserPassword 之②、updateUserSessionPolicy 之②③、restoreUser 結構性不可達之②③、addUser 之①②③、deleteUser 與 kickUser 之⑤）以測試釘住空格理由。
3. **活性**＝未軟刪、不看狀態（停用帳號照樣治理得動）；對已軟刪、不存在、`id` ≤ 0 之標的，除 restoreUser 外一律 `2222 biz.user.notFound`（FR-016）。
4. **seed 結構保護**（FR-017；碼內常數 `SEED_USER_IDS = [1, 2, 3]`、`SUPER_USER_ID = 1`）：三帳號不可刪＝`biz.user.seededProtected`；id 1 恆禁停用＝`biz.user.superCannotDisable`、恆禁解除其 R_SUPER 指派＝`biz.user.seededProtected`（R_SUPER 角色 id 以 `sys_role::SUPER_ROLE_CODE` 現查、查無＝fail-closed 拒）。
5. **本人規則**（標的＝操作者 uid）：不得刪除＝`biz.user.cannotDeleteSelf`；`status`（值域收斂後）或 `roleIds` 出現＝`biz.user.cannotEditSelfRoleOrStatus`（值不比對）；不得踢除＝`biz.user.cannotKickSelf`；不得以 resetUserPassword 重設本人＝`biz.user.cannotResetSelfPassword`；本人可改非角色欄與會話政策。
6. **包含規則**（FR-021；島 I7；ADR-00075）：鎖內、任何寫入前判 T⊆A∧N⊆A——A＝操作者現役角色 id 集（濾軟刪與停用、交易內現讀；★含 R_SUPER 者 A＝全集）、T＝標的全部指派之角色 id（只濾角色軟刪）、N＝寫後角色集（請求 `roleIds` 去重；缺席＝T；刪除家族＝∅；addUser 之 T＝∅）。違者 `5003 system.forbidden`（純 key、HTTP 403）＋一則 warn（操作者 id、標的 id、端點三欄；不含差集；不新增觀測序列）。★N 含不存在或已軟刪之角色 id 時第④步只判 T⊆A、拒因留給⑤之 `biz.user.roleNotFound`（不以 `5003` 先吞；`rev5:007` HEAD 形）；N 之活性以角色列鎖讀結果判（指派寫端於①後、②前對 T∪N 去重升序鎖讀；addUser 只鎖 N）。判定只呼單一具名件（handler 包裝 `guard_no_escalation` → 純函式 `auth::no_escalation::assert_no_escalation`）；中介層 `no_escalation_check` 掛點續恆放行、簽章不動。同級互管允許。
7. **鎖序**（FR-011；全文＝data-model §5）：交易內主體首句取 per-user advisory（`sys_user::advisory_lock_user`，簽章收窄為只收 `&DatabaseTransaction`）→ 使用者列 `FOR UPDATE`（restoreUser 鎖已刪列）→ 指派寫端之角色列依 id 去重升序 `FOR UPDATE` 並鎖內重驗未軟刪 → 寫入；lock-then-redecide。addUser 不取 advisory（同名並發由現役唯一索引兜底）。
8. **稽核同交易**（FR-006）：每筆成功每標的恰一列（`entity_table`＝`"sys_user"`、`entity_id`＝標的 id）；動作詞彙封閉八詞（本刀增 `kick`／`reset_password`／`change_password`；ADR-00082）；payload 逐欄白名單、不含 `password`（明文與雜湊）與 `session_id`（欄集＝data-model §7）。被拒腿與 no-op 零稽核。
9. **斷權**（FR-026／FR-027；島 I2）：停用（啟用轉停用）、刪除、重設密碼與 kickUser，同交易以迴圈形撤票原語撤標的**全部有效票**（`sys_token::revoke_all_of_user`；與 `revoke_others_of_user` 共用底座 `revoke_sids_of_user`；已輪替列不動）、逐 sid 寫會話事件 `revoked`（原因 `user_disabled`／`user_deleted`／`password_reset`／`admin_kick`）；commit 後逐 sid **盡力**寫失效名單（kickUser＝`admin_kick`、其餘＝`revoked`；存活＝換發票全壽命；失敗只記 warn、不改回應）。被撤者下一次請求：`revoked`＝`8888`、`admin_kick`＝`7777`＋`auth.session.kickedByAdmin`；停用與刪除者再登入＝`1000`。MUST NOT 新增每請求活性判定（FR-029）。
10. **同值 no-op**（updateUser、updateUserSessionPolicy；Q15、ADR-00080）：位於⑤——先判全欄缺席早退、再於值域收斂後比對鎖內現值（空字串＝NULL、`userGender` 值域外＝缺席、角色集以集合比）；同值＝零寫入、零稽核、不動 `updated_*`、零撤票，回應與 Applied 同形（`0000`、`data: null`）。★與角色選單域（ADR-00047 決定 3：交易前提前 no-op、同值照寫照稽核）之差由 ADR-00080 明文：因位於第⑤，body 缺席仍回 `notFound`、對範圍外標的之全缺席請求仍回 `5003`。
11. **密碼三重不洩**（島 I5）：回應不含密碼（addUser／resetUserPassword 回 `null`）、稽核不含、日誌不含（請求型遮蔽 `Debug`、明細只帶中性違規碼）。雜湊於取任何鎖之前算好（`password::NewPassword::prepare`；FR-012；失敗＝`5000`、實務不可達）。

## 1. `GET /systemManage/getUserList`（seed 1、2）

Query `UserListQuery`（全部可空）：
- `current`／`size`：`envelope::page_params`（缺席→1／10；`current` clamp [1, 10^7]、`size` clamp [1, 100]；顯式 0 取下界；逾界回空頁且回應 `current`＝clamp 後值）；MUST NOT 用 `page_or_all`。
- `userName`／`nickName`／`userPhone`／`userEmail`：不分大小寫子字串（既有 `ilike_contains`：`%`／`_`／`\` 轉義為字面）；空字串＝不篩選；欄值 NULL 之列於該欄有篩選時不命中。★手機與信箱自本刀起真篩選（Q17）。
- `userGender`／`status`：trim 後恰 `'1'`／`'2'` 等值（DB 值 1／2）、其餘＝不篩選（`common::wire_two_value_to_db`）。六欄 AND；不收排序參數（ADR-00058 決定 1）。

200：`data: PageRes<UserRecord>`；`total`＝篩選後總數；域＝未軟刪（含停用）；固定穩定序＝`id ASC`（FR-007）。錯誤集只有授權（`5003`／`8888`）與內部（`5000`）兩腿。seed 下 `total=3`、id 1 之列形：

```json
{"id":1,"userName":"Super","nickName":"Super","userGender":null,"userPhone":null,"userEmail":null,"status":"1","sessionPolicy":"inherit","userMemo":null,"roles":[{"id":1,"roleCode":"R_SUPER","roleName":"超級管理員"}],"createdAt":"2026-08-05T00:00:00+00:00","createdBy":null,"updatedAt":null,"updatedBy":null}
```

前端：現役清單（`remote` 分頁、列鍵 `id`；查詢欄逐欄顯式送出）；搜尋卡六欄（手機與信箱拔除格式驗證＝FR-047）。upstream `fetchGetUserList` 本刀起零畫面消費。

## 2. `GET /systemManage/getDeletedUsers`（seed 155）

Query `DeletedUserListQuery`：只收 `current`／`size`（規則同 §1）、其餘鍵忽略。200：`data: PageRes<UserRecord>`；域＝已軟刪；固定穩定序＝`deleted_at DESC, id DESC`；`roles` 恆 `[]`、`status`＝刪除前原值。seed 下零列。錯誤集同 §1。前端：回收桶模式（隱藏搜尋卡、操作欄換「復原」、不加刪除時間欄）。

## 3. `POST /systemManage/addUser`（seed 17）

Req `AddReq`。①②③不適用；④T＝∅、N＝`roleIds` 去重（成員皆鎖得活性列時；含不存在或已軟刪 id＝N＝T＝∅、拒因留給⑤之 `roleNotFound`＝rev5 HEAD 形）；⑤依序：
1. 帳號名形制 `^[A-Za-z0-9_-]{1,64}$`（不 trim、大小寫敏感；上界引 `throttle::LOGIN_USER_NAME_MAX`）＝`biz.user.userNameInvalid`；
2. 帳號名現役唯一＝`biz.user.userNameExists`；
3. 信箱（非空時）格式：≤254 字元、無空白與控制字元、恰一個 `@` 且兩側非空＝`biz.user.userEmailInvalid`（手機不驗格式與長度＝`rev5:ADR 0069` 形）；
4. 信箱現役唯一（`lower()` 等值、只比現役列）＝`biz.user.userEmailExists`；
5. `roleIds` 每一 id 存在且未軟刪（角色列鎖內重驗；停用角色可指派）＝否則整筆 `biz.user.roleNotFound`（不靜默略過；與 006 刀授權彈窗之候選外略過不同形）；
6. 密碼政策（`forbidUsername` 比請求之帳號名）＝`biz.user.passwordPolicy`＋`{violations}`；
7. 設密冷卻（（新 id, 操作者））結構上恆過，★但經手列照寫＝計入其後同一操作者對該帳號之冷卻（FR-035）。

Applied：INSERT（`status` 預設 1、`session_policy` 預設 `inherit`）→ 指派列 → `sys_pwd_custody::touch(新 id, 操作者)` → 稽核 `add` → commit；零撤票、零重載。併發撞現役唯一索引（23505）依索引名收窄為 `userNameExists`／`userEmailExists`（既有 `violated_constraint`；索引 `sys_user_user_name_active_uniq`／`sys_user_user_email_active_uniq`），其餘 23505＝`5000`。
200：`data: null`（不回新 id；rev6 各域新增端點同形）。例：`{"userName":"alice","password":"<合政策之密碼>","roleIds":[]}` ⇒ `0000`；再送 ⇒ `2222 biz.user.userNameExists`。
前端：新增抽屜（密碼欄只掛提示＋隨機產密浮層；角色下拉全列、不預判包含規則＝FR-024）。

## 4. `POST /systemManage/updateUser`（seed 18）

Req `UpdateReq`。①鎖現役列（`notFound`）→ ②標的為 id 1：`status` 收斂為 `'2'`＝`superCannotDisable`；`roleIds` 出現且不含 R_SUPER 角色 id＝`seededProtected`（皆中取前者）→ ③本人：`status`／`roleIds` 出現＝`cannotEditSelfRoleOrStatus` → ④T⊆A∧N⊆A → ⑤依序：全欄缺席（除 `id`；值域外與非三態欄之 null 皆計缺席）＝提前 no-op → `userName` 出現＝`userNameImmutable` → 信箱（非空字串）格式＝`userEmailInvalid` → 信箱現役唯一（排除自身）＝`userEmailExists` → `roleIds` 每一 id 存在且未軟刪＝否則 `roleNotFound` → 值 diff 無變更＝no-op。
Applied：欄寫入（缺席欄不碰）＋`updated_*` 成對 bump；`roleIds` 集合有變＝指派差集硬刪＋新增同交易（寫後角色集恰等於請求之去重集）；`status` 啟用轉停用＝同交易撤全部有效票＋事件 `user_disabled`＋commit 後失效名單 `revoked`；稽核 `update`（before／after 含角色集＝data-model §7）。單純改角色不撤票、不重載（下一請求即生效）；改回啟用不撤票。併發佔走同信箱＝23505 收窄為 `userEmailExists`。
200：`data: null`。例：bob 持 {R_X〔停用〕, R_USER_COMMON}，Super 送 `{"id":<bob>,"roleIds":[<R_X>,<R_USER_COMMON>,2]}` ⇒ 三者（US1 場景 4）；`{"id":<bob>,"nickName":""}` ⇒ 落 NULL；`{"id":<bob>}` ⇒ `0000`、零寫入零稽核。
前端：編輯抽屜（帳號名停用；狀態與角色只在改動時送、防並行之舊值把他人剛停用之帳號啟用回來；會話政策改動時另打 §10；本人列狀態與角色停用；非超管之會話政策欄停用＋提示）。並行編輯其餘文字欄＝後送出者為準（已知態＝ADR-00080）。

## 5. `DELETE /systemManage/deleteUser`（seed 19；JSON body）

Req `UserIdReq`。①鎖現役列 → ②id ∈ {1,2,3}＝`seededProtected` → ③本人＝`cannotDeleteSelf` → ④T⊆A（N＝∅）→ Applied：軟刪（`deleted_at`／`deleted_by` 成對、`status` 保留）→ 硬刪全部指派列 → 撤全部有效票＋事件 `user_deleted` → 稽核 `delete` → commit → 失效名單 `revoked`。200：`data: null`。★指派隨軟刪硬刪＝ADR-00044 翻案觸發器首款之答案（軟刪者已無指派⇒角色刪除之掛載數口徑不必改；FR-015）。前端：列「刪除」（`user:delete`；DELETE 動詞、`id` 走 body）。

## 6. `DELETE /systemManage/batchDeleteUser`（seed 20；JSON body）

Req `UserBatchDeleteReq`（重複 id 先去重、依 id 升冪處理）。上下文先判；去重後為空＝**提前成功**（零 begin、零鎖、零稽核；body 缺席或壞形同此）。取鎖序（data-model §5）：先依序取完**全部** advisory(uid) → 依序鎖全部使用者列 → 對整批 T 聯集一次依 id 升冪鎖角色列（守「advisory 早於任何列鎖」、整批單調、與單筆寫端不成 ABBA）。判定（★wire 可觀察面）：逐步全批——①全批鎖列、任一查無或已刪＝`notFound` → ②全批任一 seed id＝`seededProtected` → ③操作者 ∈ ids＝`cannotDeleteSelf` → ④A 讀一次、ids 升冪逐筆 Tᵢ⊆A＝`5003`；同一步全批判完才進下一步、拒因由步序決定（與 id 排列無關）、純 key 不指筆、整批 rollback（與 `rev5:007` 逐 id 交錯形於多 id 異類違規時可異；research R5 #47、ADR-00080 決定 8）。全過：逐筆執行 §5 寫入（每筆稽核一列 `delete`）→ 一次 commit → 全部被撤 sid 寫失效名單。200：`data: null`。前端：表頭批刪（`showDelete`＋`user:delete`）。

## 7. `POST /systemManage/restoreUser`（seed 152）

Req `UserIdReq`。①advisory(id) → 鎖**已刪**列；查無（含現役 id、`id=0`）＝`notFound` → ②③結構性不可達 → ④T⊆A（生產態 T≡∅ 恆過、仍呼叫；通則序）→ ⑤鎖內重驗：同帳號名有現役列＝`userNameExists`；標的信箱非空且有現役列同信箱（`lower()`）＝`userEmailExists` → Applied：成對清除軟刪欄（審計欄處置＝data-model §3 之 restoreUser 節）→ 稽核 `restore` → commit。★**零回灌**（復原後零角色；同帳號名重建不繼承舊實例角色）、`status` 保留、零撤票。併發撞索引＝23505 收窄為同二鍵。200：`data: null`。例：回收桶中曾持 R_SUPER 之 X（T＝∅）由被授復原者復原 ⇒ `0000`、X 零角色（US4 場景 5）。前端：「復原」（`user:restore`；確認框明示需重新指派角色）。

## 8. `POST /systemManage/kickUser`（seed 154）

Req `UserIdReq`。①鎖現役列 → ②空格（Super 可被踢）→ ③本人＝`cannotKickSelf` → ④T⊆A → Applied：撤全部有效票（已輪替列不動＝重放仍走重用偵測；島 A）＋事件 `admin_kick` → 稽核 `kick`（撤 0 張亦一列）→ commit → 失效名單 `admin_kick`。停用中之標的可踢。200：`data: KickRes`（例 `{"revoked":2}`）。被踢者下一次請求（授權中介層與換發兩處三向分派）＝`7777`＋`auth.session.kickedByAdmin`、可立即重登；單一會話頂替之 `kicked`＝`7777`＋`auth.session.kicked` 文案不變；三者不互換（島 C；FR-027）。不新增存取軌跡寫入面（BL-00043 反向確認）。前端：列操作下拉「踢除下線」（`user:kick`；成功 toast 不據 `revoked` 改寫）。

## 9. `POST /systemManage/resetUserPassword`（seed 151）

Req `ResetPasswordReq`（管理員手輸或產密浮層產生）。①鎖現役列 → ②空格（seed 帳號可重設）→ ③本人＝`cannotResetSelfPassword`（導向個人中心）→ ④T⊆A → ⑤密碼政策（`forbidUsername` 比鎖內列之帳號名）＝`passwordPolicy`＋`{violations}` → 設密冷卻（（標的, 操作者）、經手表該對時戳為上次設密時間；設定 `password_change_min_interval` 消費當下現讀、0＝停用）＝`pwdSetTooFrequent`＋`{remainingSeconds}` → Applied：UPDATE `password`＋`updated_*` → `sys_pwd_custody::touch(標的, 操作者)`（只 upsert 該對）→ 撤全部有效票＋事件 `password_reset` → 稽核 `reset_password` → commit → 失效名單 `revoked`。200：`data: null`（不回密碼）。另一操作者對同一標的不受限。例：T0 重設 alice、T0＋30 秒再重設 ⇒ `{"data":{"remainingSeconds":30},"code":"2222","msg":"biz.user.pwdSetTooFrequent"}`。前端：「重設密碼」浮層（`user:reset-pwd`；即時規則來自 `wire-user-center.md` §1；本人列不列此項）。

## 10. `POST /systemManage/updateUserSessionPolicy`（seed 68；封死集）

Req `UpdateSessionPolicyReq`。①鎖現役列（body 缺席＝`id=0`＝`notFound`）→ ②③空格（本人可改）→ ④T⊆A（結構上恆過：列 68 受保護、006 刀封死謂詞使其不可授予非 R_SUPER；仍呼叫＝9 消費點之一）→ ⑤`sessionPolicy`（`Option<String>` 承載；必填）恰為 `inherit`／`single`／`multi`（大小寫敏感、不 trim）、其餘（含缺席、null、空字串）＝`biz.user.sessionPolicyInvalid`（同 rev5 HEAD 與 ADR-00047 決定 1；spec FR-018 修補後形）→ 同值＝no-op（值 diff；本端點無全缺席早退）→ Applied：UPDATE＋`updated_*` → 稽核 `update` → commit。改為 `single` MUST NOT 即時踢除（下次登入生效）；零撤票。200：`data: null`。授予非 R_SUPER＝006 刀結構性封死整批拒（`biz.role.protectedGrant`）。前端：非超管之抽屜欄停用＋提示「僅超級管理員可改」、不發必敗呼叫（FR-024）。

## 11. `POST /systemManage/unlockLogin` 帳號維之變更（既有端點；seed 148）

端點本體、請求形、既有拒因腿與「稽核先於標記」不變（FR-040）；本刀只於**帳號維**插入包含規則，並因 advisory 需交易而把該維稽核改為單列交易。以 004 刀 `contracts/wire-throttle-unlock.md` 處理序四步為基準核：

| 步 | 004 刀處理序 | 本刀後：帳號維（`user`） | 本刀後：來源維（`ip`） |
|---|---|---|---|
| 1 | 維度解析＋標的導出；畸形＝`2222 biz.throttle.invalidUnlockTarget`、零稽核零狀態 | 不變 | 不變 |
| 2 | 操作者上下文缺席＝`5000` | 不變（★本端點既有序為標的解析先於上下文；FR-040「端點本體不變」優先於 FR-006 通則字面） | 不變 |
| 2.5 | —— | **新增**：開交易 → 以帳號名原文（大小寫敏感、零正規化）`sys_user::find_by_user_name` 解析現役 uid → **查得**：`advisory_lock_user(uid)` → `guard_no_escalation`（T＝該帳號全部指派、N＝T、端點 `unlockLogin`）→ 違者 `5003`、rollback、★零稽核零標記；**查無**（不存在或已軟刪）＝T＝∅ 恆過 | 不套（標的是計數桶、非使用者） |
| 3 | 先寫稽核（裸連線 `sys_operation_log::write`）；失敗＝`5000`、快取不動 | 交易內 `sys_operation_log::write_in_txn` → commit；寫入或 commit 失敗＝`5000`、快取不動 | 不變 |
| 4 | 寫該維解鎖標記（不查鎖態、不刪任何鍵）；失敗＝`5000`（稽核已落、可重試） | 不變 | 不變 |

- 稽核欄值不變（`entity_table`＝`login_throttle`、`entity_id`＝NULL、`after`＝`{dimension, userName, target}`）。**冪等與不洩存在性不變**：未鎖、不存在或已刪之帳號名照寫稽核與標記、回 `0000`（GR3）；查無恆過、不回 `notFound`（否則成帳號存在性枚舉面）；停用帳號屬現役、照套規則。
- 只取 advisory(uid)、不鎖使用者列與角色列（解鎖不寫使用者列、不改指派；八支寫端改指派前皆取同一把 advisory⇒T 於鎖內穩定）。帳號名→uid 解析必先於取鎖；帳號名建後不可變，其間唯一能改變結果者＝該帳號被刪並以同名重建之窄窗，沿 `rev5:007` HEAD 形接受（以先解析之 uid 為準）。
- 錯誤集＝`2222 biz.throttle.invalidUnlockTarget`／`5003`（新；帳號維限定、純 key；對前端不區分「端點未授權」與「包含規則違反」）／`5000`。包含規則第 9 消費點（FR-021）；ADR-00068 款 9「授出後無帳號維守門」於帳號維解除（ADR-00081）、來源維續存；BL-00048 兌現連動面＝ADR-00075。
- `handler/throttle.rs` 之源碼次序四錨同批改為反映 2.5 步與帳號維稽核形、「生產區零 `cache::del(`」不變（`contracts/code-gates.md` §3）；逐步全文＝data-model §3.11。
- 前端：兩入口共用 `fetchUnlockLogin`——使用者列「解鎖登入」送 `{dimension:'user', userName:<該列帳號名原文>}`（`user:unlock`；不顯示鎖定狀態、每列可按）；IP 規則頁表頭「解鎖來源 IP」送 `{dimension:'ip', target:<輸入之位址字面>}`（`ipRule:unlock`；m0003 增碼）。★來源維欄名為 `target`（`rev5:007` 契約曾誤寫 `ip`、其 U7 勘誤）；`dimension` 必送。

## 清單 wire 偏離帳（ADR-00083；ADR-00044 決定 9 形）

upstream `fetchGetUserList` 以 `Api.SystemManage.UserList`＝`PaginatingQueryRecord<Api.SystemManage.User>` 宣告回應型；本刀權威型＝`Api.UserAdmin.UserRecord`。偏離類別（★實集以快照機器導出為準；下表為現況導讀）：

| 類別 | 欄 | upstream `User` | `UserRecord` |
|---|---|---|---|
| ①欄名差 | 審計四欄 | `createBy`／`createTime`／`updateBy`／`updateTime` | `createdBy`／`createdAt`／`updatedBy`／`updatedAt` |
| ①欄名差 | 角色 | `userRoles` | `roles` |
| ①欄名差 | rev6 額外欄 | —— | `sessionPolicy`／`userMemo` |
| ②可空性差 | `nickName`／`userPhone`／`userEmail` | 非空 | `string \| null` |
| ②可空性差 | `status` | `EnableStatus \| null` | `EnableStatus` |
| ③值型差 | `userGender` | `'1' \| '2' \| null` | `string \| null` |

wire 裁判一案斷言「兩型欄差集（欄名集差＋共有欄之 required 差與型別差〔含可空性〕）＝同檔釘值常數」、漂移即紅（`contracts/code-gates.md` §4）。query 面兩型欄名集相同、rev6 值型較寬（upstream 形可直接賦值）＝不構成偏離。理由：本刀起使用者管理頁不再消費 upstream 清單函式（`plugin/excel` 示範頁為殘存消費面、所讀六欄兩型同名＝ADR-00083 決定 3；user 2026-10-05 親決）；改欄名對齊 upstream 會翻 004 刀起之 rev6 欄名慣例。翻案觸發＝upstream 清單函式出現 excel 示範頁以外之消費者、或 rebase 改動 `Api.SystemManage.User` 家族。

## 授權態矩陣（contract 測）

| 端點 | Super | Admin | User | 未登入 |
|---|---|---|---|---|
| getUserList | `0000` | `0000` | `5003` | `8888` |
| 其餘九支 | 皆通（下） | `5003` | `5003` | `8888` |

Super 以空 body 打寫端：addUser＝`2222 biz.user.userNameInvalid`；updateUser／deleteUser／restoreUser／kickUser／resetUserPassword／updateUserSessionPolicy＝`2222 biz.user.notFound`；batchDeleteUser＝`0000`（提前成功）——皆零變更。動詞不符（例 `GET /systemManage/deleteUser`）＝`4040`。m0003 刪 Admin 之 `user:edit` 屬按鈕顯隱面、不影響本矩陣。contract case 集與 ROUTES 恰等（61＝61、雙向覆蓋閘、case_key 綁定）；兩支清單各補分頁真 seed 附加五案（缺席→(1,10)／`current` 逾界→空頁且回填 10^7／`?size=0&current=0`→(1,1)／查詢串壞形→預設／`?size=1000`→(1,100)）；包含規則每消費點兩負一正＋停用角色計入 T 一案（FR-025；測內以資料列授權、測後清理）；新鍵實發點與名冊雙向閘＝`contracts/msg-keys.md` §5；名冊閘 `NO_ESCALATION_CALL_FILES`＝[`handler/throttle.rs`, `handler/user.rs`]（路徑字典序）與 case 名冊＝`contracts/code-gates.md` §2／§3。

## 既有端點之 wire 連動（逐項指承載）

- **006 刀授權治理讀寫端**（候選＝ROUTES 政策保護條目 +10）：getAllEndpoints 35→45 項；getRoleEndpoints `id=1` 35→45 項、`protected=true` 14→15（列 68 轉入候選）；`id=2` 2→3 項（列 2 轉入）；R_SUPER 端點維 seed 50 列之候選外者 15→5（皆 008 刀稽核端點）；封死集不變（15 鍵）。量法：解析 m0002 casbin seed 對 ROUTES 政策條目聯集本刀十條逐鍵比對。新入候選之九支（列 68 除外）可經端點權限彈窗授出、由包含規則兜底；以「列 68 候選外」為前提之兩支既有測試改植合成探針列（FR-061）。
- **m0003 對按鈕維讀端**（ADR-00085）：getAllButtons 20→21 碼；getRoleButton `id=1` 20→21 項、`protected=true` 0→6；`id=2` 3→2 項；getUserInfo 之 Admin 按鈕集去 `user:edit`（FR-046）。
- **授權中介層與換發**（FR-027／FR-028）：失效名單原因三向分派（`kicked`／`admin_kick`／其餘）；換發 active 腿於票列鎖後、簽發前以一般讀取重驗活性（啟用且未軟刪、查無列＝不活）→ 不活＝rollback＋`8888`；不取 advisory、不改鎖序；寬限腿不重驗（已知殘窗＝research R10）。
- **錯誤變體** 9→11（`BizData`、`ModalLogoutByAdmin`）；13 碼矩陣與可發碼集（九碼）不變（`wire-user-center.md` §3.3）。

## 與 rev5 wire 逐欄比對

| 面 | rev5（HEAD） | rev6 本刀 | wire 差 |
|---|---|---|---|
| 命名空間與檔 | `Api.UserAdmin`（`rev5-user-admin.*`、十一支） | 同名（`rev6-user-admin.*`、十一支） | 零 |
| `UserRecord.roles` | `string[]`（代碼、同口徑） | `UserRole[]`（`{id, roleCode, roleName}`） | ★元素形差（Q13；灰色保留選項之料源；`rev5:B-145` 結案）；清單角色欄顯示畫面零差 |
| 清單過濾 | 四欄（userName／nickName 模糊、status／userGender 等值） | 六欄（加 userPhone／userEmail 模糊） | ★過濾面差（Q17；`rev5:B-143` 不帶回） |
| query／回應型名 | 後端 `UserSearchParams`；typings `ListQuery`／`DeletedListQuery`／`ListRes` | 兩側 `UserListQuery`／`DeletedUserListQuery`；不立清單回應別名（005 刀形） | 零 |
| 寫端請求型名 | 後端 `AddUserReq` 等、typings `AddReq` 等；`{id}` 後端三支各自具名、typings 內聯 | 兩側取 typings 名；`{id}` 兩側共用 `UserIdReq`、`{ids}` 為 `UserBatchDeleteReq` | 零（log 標籤差） |
| `UpdateReq.userName` | typings 無此欄 | typings 列 `userName?: string \| null`（出現即拒） | 零 |
| addUser 回應 | `{ id }`（前端零消費） | `null` | ★`data` 形差（畫面零差） |
| 更新端空字串 | 照存空字串；信箱 `""`＝`userEmailInvalid` | 可空文字欄 `""`＝清空落 NULL | ★API 層差（Q16；rev5 前端已轉 null＝畫面零差；ADR-00080） |
| 自身 `status` 判定 | `status` 鍵出現（非 null）即拒 | 值域收斂後出現即拒 | 只在送值域外字面時有差 |
| addUser 判定序 | 帳號名、信箱、角色存在先於 `5003` | `5003`（④）先於業務腿（⑤） | 只在多重違規時有差 |
| 批刪 | 逐 id「取鎖＋守門」交錯（取 id 最小者之首個違規） | 整批先取鎖、判定逐步全批（拒因由步序決定） | 多 id 異類違規時拒因可異（API 層、畫面零差） |
| 角色列 | 指派寫端只讀不鎖 | 依 id 升冪 `FOR UPDATE`＋鎖內重驗（G5 末句轉非 vacuous） | 只在與 deleteRole 併發時有差（rev5 可掛上已軟刪角色、rev6 回 `roleNotFound`） |
| 授權重載 | 指派變更或刪除有指派者即重載 | 零重載 | 零 |
| `KickRes.revoked` | `i64`＋2^53 守衛 | `usize` | 零 |
| unlockLogin | 兩維皆單列交易；帳號維包含規則；標記後 DEL 鎖定鍵 | 帳號維交易＋包含規則、來源維裸連線（004 刀形）；無 DEL 步（ADR-00038） | 零 |
| 拒因構造／操作者缺席 log | 字面 `Cow::Borrowed`；`security.ipgate`＋`degraded` 欄 | `msg_key` 常數（`MSG_KEYS` 46→68）；`security.user`＋`refused` 欄 | 零（log 差） |
| 交易與稽核 | facade 自開交易、自寫稽核 | handler 持交易、稽核同交易 | 零 |

## 拒寫事件與觀測

- 新域字面（MUST 與既有各域不同字）：拒寫事件＝本域私有 `operator_from`：`tracing::error!(target: "security.user", refused = "request_context_absent", endpoint, uid, <本域訊息>)`，MUST NOT 帶 degraded 欄或增計降級序列；body 收斂 debug 訊息＝本域 `BODY_FALLBACK_MSG`（清單 query 壞形另落一則 debug）；資料庫故障＝本域 `db_failure(endpoint, step)`、落 `security.user` 之 error 後翻 `5000`。訊息字面由 tasks 定。
- 包含規則違反之 warn 由 `handler::user::guard_no_escalation` 單點發出（unlockLogin 帳號維經同一件、端點欄＝`unlockLogin`）；失效名單寫入失敗之 warn 不改回應；兩者皆不新增序列。
- 名冊同批入冊：`handler/common.rs` 之 `each_domain_keeps_its_own_log_literals` 加本域（並對各域拒寫事件加不含 `degraded` 之負向斷言）；`handler/ip_rule.rs` 之 `production_code_emits_no_degraded_field` 不加 `user.rs`（承載 `finish_user_write` 之會話面降級腿；只加 `user_center.rs`＝research R6 第 5 款）；`tests/authz_entrypoint_lint.rs` 增 `NO_ESCALATION_CALL_FILES`（一正一反自證）；`RELOAD_CALL_FILES`、`DOMAIN_LOCK_CALL_FILES` 不加（配反向確認測試）；腿⑤後半「`advisory_lock_user` 使用點與 `DOMAIN_WRITE_SIDE_FILES` 零交集」維持綠。
- 本域 tracing 欄不得帶請求型之 `{:?}`（遮蔽 `Debug` 為第二道防線）。
