# Research — 007-user-password-admin（Phase 0）

> 輸入：spec（以工作樹版為準；clarify 零提問；plan 前 user 兩度裁定走查還原工具擴面入 FR-057）＋brainstorm `docs/brainstorms/007-user-password-admin.md`（拍板 Q1～Q22、grilling GR1～GR9、主線工程判斷①～⑰、設計四節）＋ADR-00074～ADR-00087 草稿＋`rev5:007-user-password-admin` 全套與 rev5 凍結 worktree（唯讀；外層 `7eab28a`／rust-api `92919b9`／base-web `9833308`）＋rev6 碼面唯讀勘查（rust-api `6f74d20`、base-web `fb4dac2`；兩子庫 pin＝worktree HEAD）。每題以 **Decision**／**Rationale**／**Alternatives considered** 三標籤書寫（表格節除外）。
> **NEEDS CLARIFICATION＝0**：plan 期定案者皆為工程判斷（逐條附理由；交 tasks 與實作期定值者列 R25）。CLAUDE.md §2 兩件必列＝**R2／R3 rev5 對應碼清單**、**R5 rev6 拍板差異點**（兩支 wire 契約所稱「rev6 差異點」即 R5）；RL-0013 反例回跑＝R24；ADR 時點表＝R21（ADR 與 plan 以其表名引用）；執行單元骨架＝R23。行號不入本檔。

## R1 技術脈絡

- **Decision**: 本刀**零新依賴、零版本變更**。後端沿 rust 1.96.1（`rust-api/rust-toolchain.toml`）、argon2 **0.6.0**（`rust-api/Cargo.lock` 唯一版本；password-hash 0.6.1 隨附）、getrandom **0.4.3**（直接依賴；lock 另有 0.2.17／0.3.4 兩份間接副本、非本刀所引）、redis 1.7.0（`connection-manager`＋`tokio-comp`）、sea-orm 1.1.20、axum 0.8.9、tokio 1.53.1、casbin 2.20.0、metrics 0.24.6、serde_json 1.0.151。雜湊生成路徑已在碼面：`model/password.rs`::`dummy_phc` 以 `getrandom::fill` 取 16 bytes salt 餵 `PasswordHasher::hash_password_with_salt`（`Argon2::default()`＝seed PHC 之 m=19456,t=2,p=1），本刀 `password::hash` 只是把同一路徑提為公開件（R11）。前端沿 vue 3.5.34、naive-ui **2.44.1**（套件根經 `es/locales/index.mjs` 匯出 `zhTW`／`dateZhTW`，`es/locales/common/zhTW.mjs` 與 `es/locales/date/zhTW.mjs` 皆在）、dayjs **1.11.20**（`dayjs/locale/zh-tw.js` 在）、vue-i18n 11.4.2、typescript 6.0.3、vue-tsc 3.2.8；`base-web/pnpm-lock.yaml` 對 naive-ui 與 dayjs 各恰一版、與 `package.json` 字面同值。
- **一支 seed-only migration**：`rust-api/migration/src/` 現有 `m0001_baseline_schema.rs`／`m0002_baseline_seeds.rs` 兩支，本刀增 `m0003_seed_button_governance.rs`（零 DDL、不建表；五句內容、冪等形與失敗語意＝R13）。本刀用到的表面全在 001 刀基線（m0001）：`sys_pwd_custody`（3 欄、複合 PK `(user_id, created_by)`）、`session_event`、`sys_user` 之 `user_memo`／`session_policy` 欄、兩支活性唯一索引 `sys_user_user_name_active_uniq` 與 `sys_user_user_email_active_uniq`（`lower(user_email)`、`WHERE deleted_at IS NULL AND user_email IS NOT NULL`）；密碼政策八鍵（七政策鍵＋`password_change_min_interval`＝60）在 m0002 之 `system_settings`。
- **執行環境**：rust build 與 test 一律容器內、全程 serial（host 無 toolchain）；base-web pnpm 一律容器內（`docker-compose.dev.yml` 以 `CI=true` 走 frozen lockfile）；compose 之一次性 `migrate` 服務先於 rust-api（`depends_on` 之 `service_completed_successfully`）＝m0003 於 stack 啟動時自動套用（此隱性時機與走查還原工具之前置＝R16）。
- **前端零測試框架**：`base-web/package.json` 對 vitest／jest／`@vue/test-utils`／`@playwright/test`／cypress 之計數為 0；腳本面只有 `typecheck`（`vue-tsc --noEmit --skipLibCheck`）與 `lint`。前端單元之 TDD 退化形＝型別檢查（三語 `App.I18n.Schema`）＋機器斷言（`tools/fork-delta-lint.py`、`tools/msg-key-gate.py`、本刀新閘 `tools/zh-tw-lint.py`、`tools/view-render-guard.py`、`tools/route-artifact-gate.py`、`tools/seed-view-gate.py`）＋兩段 review＋CDP 三方對照（006 刀同形；spec Assumptions）。
- **連帶碼註**：兩處現在式句隨 `password::hash` 落地即失準——`rust-api/Cargo.toml` argon2 段「本刀不產 hash」與 `rust-api/server/Cargo.toml` argon2／getrandom 段之消費者清單（只列 `verify`／`dummy_verify`／dummy salt）；落雜湊之單元同批改（R22）。
- **Rationale**: 全域 §6 版本紀律；本刀全部能力（政策驗證＝純函式、雜湊＝既有 argon2 路徑、改密節流＝既有 redis 連線之 INCR＋EXPIRE、繁中＝元件庫與日期庫既有語系）皆由既有依賴承載。`rev5:007` research R3 之依賴錨（argon2 0.5.3、redis 1.3.0）不可照抄：rev6 已於 003 刀定 argon2 0.6.0／redis 1.7.0，rev5 `hash` 之 `SaltString::generate(&mut OsRng)` 在 0.6 系不存在（`model/password.rs` 模組 doc 已載此守則）。
- **Alternatives considered**: 另引 `password-hash`／`rand_core` 直接依賴取 `OsRng`（新增直接依賴、且 0.6 系已拔除 `OsRng`，棄）；前端引入 vitest 補元件測（新依賴、超出本刀範圍、spec 已定退化形，棄）；改密節流改走 PG 失敗紀錄表（需建表＝破零 DDL，Q20 已拍 redis＝ADR-00078，棄）；繁中另裝第三方語系包（元件庫與日期庫既有版本已含繁中，棄）。

## R2 rev5 對應碼清單（後端）

實作單元動工前逐檔先讀（唯讀、重打字消化、碼註以 rev6 語境重寫、出處帶 `rev5:`）。rev5 路徑相對 `rust-api/`、rev6 落點相對 `rust-api/server/src/`（測試檔相對 `rust-api/server/`）；每列 rev5 符號皆於凍結 worktree 以 `ls`／`grep -n` 核存在。藍本取 rev5 HEAD 形（依據＝R4）；「處置」欄之「R5 #n」指 R5 差異點表列號。

| rev5 檔::符號 | 角色 | rev6 落點 | 處置 |
|---|---|---|---|
| `rev5:server/src/handler/user.rs`::`get_user_list`／`get_deleted_users`／`to_user_record`／`enrich_records` | 現役清單（四欄過濾、id 升冪）、回收桶（刪除時間降冪再 id 降冪）、審計欄帳號名回填 | `handler/user.rs::get_user_list`／`get_deleted_users`（新建檔） | 沿用固定序；翻案：六欄過濾（R5 #11）、角色欄三欄形（R5 #10）；分頁與名稱回填改 rev6 共用件（R5 #41） |
| 同檔::`add_user`／`update_user`／`wire_gender_tristate`／`validate_user_name_form`／`validate_user_email_form`／`USER_EMAIL_MAX_LEN` | 新增與編輯；帳號名形制 `^[A-Za-z0-9_-]{1,64}$`（上界引 `LOGIN_USER_NAME_MAX`）、信箱簡式格式 ≤254、`roleIds`＝期望全集、帳號名出現即拒 | `handler/user.rs::add_user`／`update_user`＋私有形制件 | 判定序依 spec FR-010 固定序（④ 前移至 ⑤ 前、⑤ 內信箱先格式後唯一；與 `rev5:007` 契約 §3 之唯一先於格式不同＝API 層、畫面零差、R5 #49），期望全集沿用；翻案：空字串（R5 #2）、角色列鎖（R5 #21）、零授權重載（R5 #4） |
| 同檔::`delete_user`／`batch_delete_user`／`had_role_assignments` | 刪除與批刪（空陣列零交易、任一違規整批 rollback） | `handler/user.rs::delete_user`／`batch_delete_user` | 沿用；翻案：批次取鎖序（R5 #22）；`had_role_assignments`（reload 條件）不帶 |
| 同檔::`restore_user`／`lock_deleted_user` | 鎖已刪列→④恆過仍掛→鎖內重驗撞名、撞信箱 | `handler/user.rs::restore_user` | 沿用 |
| 同檔::`kick_user`／`reset_user_password`／`update_user_session_policy` | 踢除（撤全部 active、事件 `admin_kick`、回 `{revoked: n}`）；重設（取鎖前算雜湊→本人禁→④→政策→冷卻→寫密→撤票）；會話政策（三值收斂、同值 no-op、super-only 故④結構上恆過仍掛） | `handler/user.rs::kick_user`／`reset_user_password`／`update_user_session_policy` | 沿用（雜湊點＝交易內、取鎖前：R5 #40；會話政策必填＝R5 #51） |
| 同檔::`begin_and_lock_user`／`lock_active_user`／`lock_read_err` | 開交易→advisory(uid)→活性列 FOR UPDATE（活性＝未軟刪、不看狀態） | handler 持交易、各寫端 `<op>_in_txn` 首句（私有件；名稱實作期定：純私有、不跨檔引用、不入名冊） | 沿用語意、改 rev6 形（R5 #37） |
| 同檔::`guard_seed_delete`／`guard_seed_update`／`guard_self_delete`／`guard_self_kick`／`guard_self_reset_password`／`guard_self_update` | seed 結構保護與本人五不（純 key；超管角色查不到一律 fail-closed） | `handler/user.rs` 私有件＋`SEED_USER_IDS`／`SUPER_USER_ID` | 沿用（常數落點改、R5 #30） |
| 同檔::`guard_no_escalation` | 包含規則唯一掛點式（A＝全集短路、拒＝5003、warn 三欄） | `handler/user.rs::guard_no_escalation`（`pub(super)`、`handler/throttle.rs` 共用） | 沿用（可見性收窄、R5 #29） |
| 同檔::`finish_user_write`／`broadcast_revocation` | commit→逐 sid 盡力寫 denylist（TTL＝refresh 壽命、失敗只 warn）→依旗標 reload | `handler/user.rs::finish_user_write`（`pub(super)`、`handler/user_center.rs` 共用；無 reload 旗標） | 沿用前兩段；翻案：reload 段不帶（R5 #4） |
| 同檔::`password_policy_err`／`pwd_set_too_frequent_err` | 兩攜參鍵之單一組裝點（`pub(crate)`、三入口共用） | `handler/user.rs::password_policy_err(violations)`／`pwd_set_too_frequent_err(remaining_seconds: u64)`（`pub(super)`、`handler/user_center.rs` 共用；生產 `BizData` 構造點恰此二；data 以具型 `PasswordPolicyDetail`／`PwdSetTooFrequentDetail` 構造後 `serde_json::to_value`） | 沿用；構造改 `msg_key` 常數（R5 #39）、可見性收窄 |
| 同檔::`map_create_err` 等七支 `map_*_err` | facade 錯誤列舉→`AppError` | `<op>_in_txn` 回 `AppError`；facade 回 `DbErr` 或業務列舉（落形實作期定：純私有映射、不跨檔、不入名冊） | 改形（R5 #37） |
| 同檔::`UserRecord`／`UserSearchParams`／`AddUserReq`（手寫遮蔽 Debug）／`UpdateUserReq`／`DeleteUserReq`／`BatchDeleteUserReq`／`RestoreUserReq`／`KickUserReq`／`KickUserRes`／`ResetUserPasswordReq`／`UpdateUserSessionPolicyReq` | wire DTO（逐欄白名單、i64 守衛、`nickName` 誠實 null） | `handler/user.rs`（型名與欄集以 `contracts/wire-user-admin.md` 為準） | 沿用；翻案：角色欄（R5 #10）、查詢六欄（R5 #11）；承載密碼之請求 DTO 一律手寫遮蔽 Debug |
| `rev5:server/src/handler/user_center.rs`::`get_password_policy`／`PasswordPolicyView` | 七鍵投影（不含冷卻秒數）、登入即可用 | `handler/user_center.rs::get_password_policy`（新建檔） | 沿用 |
| 同檔::`change_password`／`ChangePasswordReq`（遮蔽 Debug）／`map_change_own_password_err` | 節流預檢→取鎖前算雜湊→七步→撤他票保留當前→commit 後清桶 | `handler/user_center.rs::change_password` | 沿用（讀 `identity.sid`＝HEAD 形、R5 #33）；雜湊點改交易內、取鎖前（R5 #40、R12） |
| `rev5:server/src/auth/no_escalation.rs`::`ActorScope`／`assert_no_escalation`／`actor_scope_of`／`ROLE_SUPER` | 包含規則純函式（`T ⊆ A ∧ N ⊆ A`） | `auth/no_escalation.rs`（新建）：`ActorScope { All, Roles(BTreeSet<i64>) }`、`actor_scope_of`、`assert_no_escalation(scope, t, n) -> Result<(), AppError>` | 沿用規則；改形：比對單位與回型（R5 #28） |
| `rev5:server/src/auth/enforce.rs`::`enforce_mw`（denylist 三向）／`no_escalation_check`（恆 `Ok`） | 撤銷分派、路徑級掛點 | `auth/enforce.rs`（既有）：三向分派；掛點簽章不動、模組註與掛點 doc 之預告句勘誤 | 沿用（R5 #32） |
| `rev5:server/src/auth/mod.rs`::`Identity`（第三欄 `sid`） | 身分注入 | `auth/mod.rs::Identity { uid, user_name, sid }` | 沿用 HEAD 形（R5 #33） |
| `rev5:server/src/handler/auth/refresh.rs`::`refresh_token`（active 腿活性重驗、revoked 腿三向）＋測試件 `seed_user_row` | 換發鎖內重驗與 fixture 種列 | `handler/auth/refresh.rs`（既有）；refresh 10 案＋logout 1 案改種帳號列並掛 `UserRowsGuard` | 沿用（R5 #31） |
| `rev5:server/src/handler/route.rs`::`SELF_SERVICE_ROUTES`／`get_user_routes` | 自助白名單於授權過濾後恆併入 | `handler/route.rs::SELF_SERVICE_ROUTES`（既有檔）＋檔頭前代歸因勘誤 | 沿用（R5 #34） |
| `rev5:server/src/handler/throttle.rs`::`unlock_login`／`guard_unlock_no_escalation` | 帳號維開交易→advisory→包含規則→`write_in_txn`→commit→寫標記；來源維不套 | `handler/throttle.rs::unlock_login`（既有）直接呼 `guard_no_escalation` | 沿用規則；改結構（R5 #36） |
| `rev5:server/src/handler/menu.rs`::`update_menu` | 按鈕清單移除碼照常連動歸檔（含 R_SUPER 列） | `handler/menu.rs`（既有）updateMenu 選單刪碼守門 | 新增（R5 #15） |
| `rev5:server/src/model/password.rs`::`hash`／`NewPassword`（`prepare`）／`PasswordPolicy`／`PASSWORD_POLICY_KEYS`／`policy_from_pairs`／`load_policy`／`validate_against_policy`／`VIOLATION_*`（八） | 政策單一驗證點（一次收集、字元數＋位元組雙約束、`forbidUsername`＝不分大小寫全等） | `model/password.rs`（既有檔擴）：`hash`、`NewPassword::prepare`、`PasswordPolicy`（七鍵）、`load_password_policy`、`validate_against_policy`、`VIOLATION_*`、`MAX_BYTES`（引 `LOGIN_PASSWORD_MAX_BYTES`） | 沿用；改形：雜湊 API（R5 #40）；新增：壞值告警（R5 #18） |
| `rev5:server/src/model/facade/sys_user.rs`::`advisory_lock_user` | per-user advisory | `sys_user::advisory_lock_user`（既有、簽章收窄） | 翻案（R5 #23） |
| 同檔::`find_active_by_id_for_update`／`find_deleted_by_id_for_update`／`active_by_id_locked_select`／`deleted_by_id_locked_select` | 活性列與已刪列之鎖讀 | `sys_user::find_active_by_id_for_update`／`find_deleted_by_id_for_update`（新建） | 沿用 |
| 同檔::`UserListFilter`／`UserListItem`／`list`／`list_deleted`／`list_select`／`deleted_select`／`attach_roles` | 清單查詢與角色回填 | `sys_user::list_active`（六欄＋分頁＋id 升冪）／`list_deleted`＋`sys_user_role::roles_by_user_ids` | 翻案（R5 #10、#11） |
| 同檔::`insert`／`UserCreate`／`UserCreateError` | 新增寫入（facade 內驗政策、算雜湊、寫指派、經手表、稽核） | `sys_user::insert`；指派、經手表、稽核由 handler 之 `<op>_in_txn` 編排 | 改形（R5 #37） |
| 同檔::`update`／`UserUpdate`／`UserUpdateOutcome`／`tri_changed` | 部分更新：全缺席早退、值 diff、停用即撤票 | `sys_user::update_fields` | 沿用 no-op；翻案：空字串（R5 #2） |
| 同檔::`soft_delete`／`batch_soft_delete`／`delete_one_locked` | 軟刪（成對刪除欄）＋硬刪指派＋撤票＋事件 | `sys_user::soft_delete`＋`sys_user_role::delete_all_of_user`＋`sys_token::revoke_all_of_user` | 沿用語意；翻案：批次取鎖序（R5 #22） |
| 同檔::`restore`／`find_by_user_name`／`active_email_taken`／`UserRestoreError` | 復原與鎖內兩腿重驗 | `sys_user::restore`／`active_name_taken`／`active_email_taken` | 沿用 |
| 同檔::`reset_password`／`load_password_policy`／`cooldown_remaining_secs`／`KEY_PWD_CHANGE_MIN_INTERVAL`／`DEFAULT_PWD_CHANGE_MIN_INTERVAL`／`UserResetPasswordError` | 重設寫入；冷卻（≤0 停用、讀不到回 60、剩餘＝`max(interval−elapsed, 1)`、維度＝標的×操作者） | `sys_user::set_password`＋`sys_pwd_custody::last_set_at`；冷卻計算件＝`model/password.rs::cooldown_remaining_secs(conn, target_id, operator_id) -> Result<Option<u64>, AppError>`（None＝放行） | 沿用；剩餘秒數補上限＝冷卻秒數（時鐘回撥；R11） |
| 同檔::`kick`／`UserKickError`、`change_own_password`／`ChangeOwnPassword`／`ChangeOwnPasswordError` | 踢除寫入；改密七步（一致→節流→舊密→新≠舊→政策→冷卻→寫密） | 各端點 `<op>_in_txn` 編排：踢除＝`sys_token::revoke_all_of_user`＋事件＋稽核；改密＝`sys_user::set_password`＋既有 `sys_token::revoke_others_of_user` | 改形（R5 #37） |
| 同檔::`set_session_policy`／`SESSION_POLICIES`／`UserSessionPolicyError` | 三值收斂、同值 no-op | `sys_user::set_session_policy`；值域重用 rev6 既有 `SESSION_POLICIES`／`SessionPolicy`（序與 rev5 不同、成員同） | 沿用 |
| 同檔::`USER_SEED_IDS`／`SUPER_USER_ID` | seed 結構保護常數 | `handler/user.rs::SEED_USER_IDS: [i64; 3] = [1, 2, 3]`／`SUPER_USER_ID: i64 = 1` | 沿用（R5 #30） |
| 同檔::`audit_json`／`audit_json_with_roles`／`id_and_name_audit_json`／`record_revocation_events` | 稽核快照（新三詞只帶 `{id, userName}`）、逐 sid 事件 | 稽核快照＝`handler/user.rs` 私有件（名稱實作期定：純私有、不跨檔）；逐 sid 事件＝`handler/user.rs::revoke_sessions_in_txn`（`pub(super)`、`user_center.rs` 共用；R6、R10） | 沿用內容；改層（R5 #37） |
| 同檔::測 `password_hash_never_computed_inside_row_lock` | 雜湊生成呼叫點不在列鎖內之源碼掃描守 | rev6 同義機器守（案名實作期定：測試案名、不入名冊；判準＝`password::hash(`／`NewPassword::prepare(` 生產呼叫點只在三支 handler 之 `begin()` 與 `<op>_in_txn` 首句之間＝R11） | 沿用（雜湊點改交易內：R5 #40） |
| `rev5:server/src/model/facade/sys_user_role.rs`::`role_codes_all_of_user`／`codes_by_active_role_ids` | T（只濾角色軟刪、不濾狀態；以代碼） | `sys_user_role::role_ids_all_of_user`（以 id） | 沿用口徑；改形（R5 #28） |
| 同檔::`roles_of_user`（A 料源、濾軟刪與停用） | A | `sys_user_role::role_ids_active_of_user`（新建；回（id, 代碼）對、供 `actor_scope_of`；既有 `roles_of_user` 續供判定面） | 新增 |
| 同檔::`codes_of_role_ids` | N 合法性（只濾軟刪、不鎖） | T∪N 去重升序經既有 `sys_role::find_active_by_id_for_update` 鎖讀並鎖內重驗 | 翻案（R5 #21） |
| 同檔::`replace_roles_of_user`／`delete_all_of_user` | 指派全量替換（差集硬刪＋新增）、軟刪全刪 | `sys_user_role::replace_roles_of_user`／`delete_all_of_user`（新建） | 沿用 |
| 同檔::`codes_by_user_ids` | 清單角色回填（只代碼） | `sys_user_role::roles_by_user_ids`（`{id, roleCode, roleName}`） | 翻案（R5 #10） |
| 同檔::`role_ids_of_user` | self-role 口徑 | rev6 既有 `sys_user_role::is_member` 已承載 | 不帶 |
| `rev5:server/src/model/facade/sys_token.rs`::`revoke_all_of_user`／`revoke_sids_of_user` | 撤票原語（SELECT 帶頭迴圈、跨輪去重） | `sys_token::revoke_all_of_user`／`revoke_sids_of_user`（新建）；既有 `revoke_others_of_user` 改走底座 | 沿用（R5 #24） |
| `rev5:server/src/model/facade/session_event.rs`::`EVENT_REVOKED`／`REASON_USER_DISABLED`／`REASON_USER_DELETED`／`REASON_PASSWORD_RESET`／`REASON_PASSWORD_CHANGED`／`REASON_ADMIN_KICK` | 會話事件詞彙 | 既有 `vocabulary!` 增列（事件 4→5、reason 2→7） | 沿用 |
| `rev5:server/src/model/facade/sys_pwd_custody.rs`::`touch`／`last_set_at` | 經手表 upsert 與讀 | `model/facade/sys_pwd_custody.rs`（新建檔）同名二支 | 沿用 |
| `rev5:server/src/model/facade/sys_operation_log.rs`::`write_in_txn` | 同交易稽核 | rev6 既有同名件 | 沿用 rev6 既有 |
| `rev5:server/src/model/audit.rs`::`AuditOperation::Kick`／`ResetPassword`／`ChangePassword`（HEAD 另含 `Purge`） | 稽核詞彙 | `model/audit.rs` 既有 macro 增三（5→8） | 沿用；`Purge` 不帶 |
| `rev5:server/src/throttle/change_pwd.rs`::`precheck`／`record_failure`／`clear`／`CHANGE_PWD_MAX_FAILS`／`CHANGE_PWD_WINDOW_SECS`／`Throttled`／`degraded` | 改密舊密節流（拒絕點在 argon2 之前、只舊密不符推進計數、fail-open） | `throttle/change_pwd.rs`（新建）同名三支＋二常數；降級發射走既有 `throttle::warn_degraded` | 沿用（R5 #20、#45） |
| `rev5:server/src/cache/mod.rs`::`REASON_ADMIN_KICK`／`CHANGE_PWD_KEY_PREFIX`／`change_pwd_fail_key`／`incr_with_window` | 第三 reason、改密桶鍵（鍵段＝uid）、INCR＋EXPIRE 原子 pipeline | `cache/mod.rs`（既有）：`REASON_ADMIN_KICK`、`CHANGE_PWD_KEY_PREFIX`、`change_pwd_key`（rev5 名 `change_pwd_fail_key`、rev6 定名去 `fail`）、`incr_with_window` | 沿用 |
| `rev5:server/src/error.rs`::`AppError::BizData`／`ModalLogoutByAdmin` | 攜參 2222、管理員踢除 7777 | `error.rs` 同名二變體（9→11）；`msg_key` 新常數 22、`MSG_KEYS` 46→68 | 沿用；HEAD 第三鍵不帶（R5 #25） |
| `rev5:server/src/envelope.rs`::`Res::from_err_with_data` | BizData 之 data 上 wire（其餘錯誤 data 恆 null） | `envelope.rs` 攜 data 錯誤信封構造件（名沿 rev5） | 沿用 |
| `rev5:server/src/obs.rs`::`THROTTLE_DEGRADED_SOURCES`／`DEGRADED_SOURCE_CHANGE_PWD` | 降級源名冊（rev5 為 12→13） | `obs.rs` 既有 `THROTTLE_DEGRADED_SOURCES` 10→11（`redis_change_pwd`）；另新增 `password_policy_invalid_total` 與 `obs::password_policy_invalid()` | 沿用＋新增（R5 #18、#45） |
| `rev5:server/src/router.rs`::ROUTES 十二條（`case_key` 為 `user-*`／`user-center-*`） | 路由 | `router.rs`（既有）ROUTES 49→61、`ROUTES_COUNT` 同 commit bump | 沿用 |
| `rev5:server/src/handler/auth/login.rs`::測 `t043_login_never_validates_the_password_policy` | 登入不驗政策之行為腿＋源碼掃描腿 | `handler/auth/login.rs` 測試模組（既有檔、新案） | 沿用 |
| `rev5:server/src/handler/common.rs`::`audit_operator`／`resolve_operator_names`／`MAX_CURRENT`／`tristate`／`json_or_default`／`blank_to_none`／`wire_two_value_to_db` | handler 共用件 | rev6 既有 `common::operator_from_context`＋本域私有 `operator_from`、`sys_user::find_names_by_ids`、`envelope::page_params`、`common::tristate`／`json_or_default`／`blank_to_none`／`wire_two_value_to_db`／`db_status_to_wire` | 前三不帶（R5 #38、#41）；其餘沿用 rev6 既有 |
| `rev5:server/src/model/facade/sys_role.rs`::`SUPER_ROLE_CODE`、`rev5:server/src/model/facade/mod.rs`::`ilike_contains`／`violated_constraint` | 共用件 | rev6 既有同名（`violated_constraint` 為 rev6 之指名索引 bool 形） | 沿用 rev6 既有（R5 #44） |
| `rev5:server/tests/authz_entrypoint_lint.rs`::`NO_ESCALATION_CALL_FILES`／`GUARD_NO_ESCALATION_CONSUMER_FILES`／`FINISH_USER_WRITE_CONSUMER_FILES`／`RELOAD_CALL_FILES`（含 `handler/user.rs`）／`PURGE_BEFORE_CALL_FILES` | 名冊閘 | `NO_ESCALATION_CALL_FILES`＝[`handler/throttle.rs`, `handler/user.rs`]（路徑字典序＝`verdict` 斷言 `roster.is_sorted()`；取 `guard_no_escalation` 裸 token 三形；一正一反自證）；`RELOAD_CALL_FILES` 零擴列＋反向確認測試；腿⑤後半維持綠 | 改形：包含規則兩名冊合一；finish 名冊不立；purge 名冊不帶（R5 #29） |
| `rev5:server/tests/contract.rs`::`verify_user_admin_policy`／`verify_user_center_authed`／`user_admin_authorization_matrix_matches_frozen_seed_policy_rows`／`user_admin_case_key_assertion_detects_sibling_route_path`／`user_center_case_key_assertion_detects_sibling_route_path` | 契約、case_key 綁定、授權態矩陣 | `tests/contract.rs`（既有）：registry 61、雙向覆蓋、兩支清單分頁五案；以本刀端點未註冊為前提之兩案（`governance_endpoint_grants_real_seed`〔列 68〕、`governance_reads_real_seed`〔seed 列 2〕）改植探針或依新路由現算改值 | 沿用（R5 #46） |
| `rev5:server/tests/wire_schema.rs`（`rev5:007` 十四型裁判） | wire 裁判 | `tests/wire_schema.rs`（既有）：`AUDITED_READ_DEFS`／`AUDITED_REQUEST_DEFS` 增列、`in_role_menu_sections` 前綴擴 `Api.UserAdmin.`／`Api.UserCenter.` | 沿用 |
| `rev5:server/src/model/mod.rs`::`test_db::UserCleanup`／`SeedUserRestoreCleanup`／`PwdCustodyCleanup`／`SessionRevokeCleanup`／`SeedOpLogCleanup` | 測試清理 | `model/facade/test_kit.rs`：`UserRowsGuard`／`SeedUserRestoreGuard`／`PwdCustodyRowsGuard`（新）、`UserRoleRowsGuard` 擴、`RedisKeysGuard` 逐鍵 `track`（型不改）、既有 `SessionRowsGuard`／`OpLogRowsGuard`；`tests/common/mod.rs` 鏡像 `UserWriteGuard`／`SeedUserWriteGuard`／`PwdCustodyWriteGuard`（沿 `*WriteGuard` 慣例） | 翻案（R5 #6） |

**commit 範圍**：rust-api `rev5:7575379`（U1）～`rev5:0161d73`（FHR 碼註）共 9 顆（外層 merge `rev5:5e8b32f` 之 rust-api pin＝`rev5:0161d73`），加收刀後零行為重構 `rev5:e02251d`／`rev5:7aa0ac3`（R4）。

## R3 rev5 對應碼清單（前端）

rev5 路徑相對 `base-web/`、rev6 落點相對 `base-web/`；標記處數為 rev5 檔內 `rev5-inline` 且帶刀名 `007-user-password-admin` 之 grep 計數（修改型＝同行帶 `原行:`、圈界＝START 數），僅作 rev6 範圍欄預估之參考、rev6 實數依 rev6 實況。

| rev5 檔::符號 | 角色 | rev6 落點 | 處置 |
|---|---|---|---|
| `rev5:src/views/manage/user/index.vue` | 使用者頁主檔：16 欄（含勾選與操作）、`scroll-x` 2002、回收桶 NSwitch（prefix 插槽、只帶分頁）、已刪模式隱搜尋卡且操作欄換復原、列操作 NDropdown（踢除、重設、隨機密碼；本人列不列後二者）、重設浮層 inline、頁首解鎖鈕；七碼 11 處 `hasAuth`；681 行、39 處標記（修改型 16、圈界 9） | `src/views/manage/user/index.vue`（`BASE-WEB-MANAGE-PAGE-WIRING(v)`；修改型＋新增型） | 沿用；翻案：表頭走 `showAdd`／`showDelete`（R5 #8）、解鎖改列操作（R5 #3）、重設浮層抽為新檔、角色欄以 `roleCode` 串接（分隔符＝`page.manage.user.roleSeparator`、不取 backend 樹） |
| `rev5:src/views/manage/user/modules/user-operate-drawer.vue` | 抽屜：寬 360、帳號名編輯態停用、密碼僅新增＋產密＋提示、會話政策僅編輯態（非超管停用＋提示、改動才另打其端點）、本人列狀態與角色停用、狀態與角色只在改動時送、更新端 `blankToNull`、關閉清明文密碼、`email→userEmail`／`roles→roleIds` 兩處修正；角色候選取 `rev5-role-admin`::`fetchGetAllRoles`＋世代守 `roleOptionsReq`＋三態 `roleOptionsState`＋`unresolvedRoleCodes`／`roleAssignLocked` 鎖；617 行、70 處標記（修改型 22、圈界 16） | 同名（(v)） | 沿用；翻案：鎖整欄改灰色保留選項（R5 #10）；候選取 `src/service/api/rev6-role-admin.ts`::`fetchGetAllRoles`（FR-053 擇一＝沿 rev5 取本代角色包裝之形） |
| `rev5:src/views/manage/user/modules/user-search.vue`（與 upstream 零 diff） | 搜尋卡（手機、信箱掛 upstream patternRules） | 同名（(v) 修改型：拔兩欄格式驗證） | 新增（R5 #11） |
| `rev5:src/views/manage/user/modules/user-unlock-modal.vue` | 頁首雙維解鎖彈窗（維度下拉、各分支顯式帶 `dimension`）；124 行 | 帳號維＝`index.vue` 列操作（無彈窗）；來源維＝`src/views/manage/ip-rule/modules/ip-unlock-modal.vue`（新檔、`MANAGE-IP-RULE-VIEW+`） | 翻案（R5 #3） |
| `rev5:src/components/custom/pwd-gen-modal.vue` | 產密浮層（`crypto.getRandomValues`＋拒絕採樣＋洗牌、長度可調、複製如實回報、`emit('apply')`、零網路）；281 行 | 同路徑新檔（`MANAGE-USER-VIEW+`） | 沿用 |
| （rev5 無獨立檔：`index.vue` 內 inline NModal、只驗非空） | 重設密碼浮層 | `src/views/manage/user/modules/user-reset-pwd-modal.vue`（新檔、`MANAGE-USER-VIEW+`；掛即時規則） | 新增 |
| `rev5:src/views/user-center/index.vue` | 個人中心真頁、只掛改密卡、刻意不綁 `:user-name`；修改型 2（原行置 HTML 註解）＋圈界 1 | 同名（(vi)） | 沿用 |
| `rev5:src/views/user-center/modules/password-card.vue` | 改密卡（舊密碼一路、兩次一致、新≠舊、成功保留當前）；130 行 | 同名新檔（`USER-CENTER-VIEW+`） | 沿用 |
| `rev5:src/hooks/business/pwd-policy.ts`::`usePwdPolicy`／`usePwdPolicyRules` | 政策模組級單例快取、讀失敗靜默退必填、規則訊息取 `backend.biz.user.passwordViolation.*`；159 行 | 同名新檔（`USER-CENTER-VIEW+`）；訊息鍵改 `page.passwordPolicy.violation.*` | 沿用；翻案：鍵位（R5 #26） |
| `rev5:src/views/_builtin/login/modules/pwd-login.vue`（LOGIN-CAPTCHA (ii) 修改型 3 處） | 帳號與密碼只驗必填（`createRequiredRule`）、不動 `reg.ts` | 同名（`BASE-WEB-LOGIN-CAPTCHA-WIRING(ii)`；rev6 現 003 刀圈界首行之「(ii) formRules 放寬不在授權內、不動」碼註同批改現在式） | 沿用；rev5 碼註錯誤不照抄（R5 末「rev5 碼註與文件已知錯誤」①②） |
| `rev5:src/service/request/index.ts`::`DETAIL_LIST_ITEM_KEY`／`translateDetailValue`／`translateBackendMsg(msg, detail)`（`rev5:003` 預建） | 錯誤明細插值 | 同名檔（`BASE-WEB-I18N-WIRING(i)` 改寫）：只轉譯兩鍵；wire 形字面同批登記 `FRONTEND_MSG_CONSUMERS` | 沿用語意；新增（rev6 003 刀明示不帶、本刀新建；R5 #26） |
| `rev5:src/service/api/rev5-user-admin.ts`（11 支；兩支刪除走 DELETE＋body） | 請求包裝 | `src/service/api/rev6-user-admin.ts`（`BASE-WEB-WRAPPER+`、不入 barrel；`fetchGetUserList` 起至 `fetchUnlockLogin` 共 11 支） | 沿用（R5 #7） |
| `rev5:src/service/api/rev5-user-center.ts`（2 支） | 個人中心包裝 | `src/service/api/rev6-user-center.ts`（`fetchGetPasswordPolicy`／`fetchChangePassword`） | 沿用（R5 #7） |
| `rev5:src/typings/api/rev5-user-admin.d.ts`::`Api.UserAdmin`（`SessionPolicy`／`UserRecord`／`ListQuery`／`DeletedListQuery`／`ListRes`／`AddReq`／`AddRes`／`UpdateReq`／`ResetPasswordReq`／`KickRes`／`UpdateSessionPolicyReq`／`UnlockReq`） | wire 型 | `src/typings/api/rev6-user-admin.d.ts`（`BASE-WEB-ADAPT+`）：型名全集＝`contracts/wire-user-admin.md` 共用型節（`UpdateReq` 容 `userName?: string | null`＝wire 可達形、出現即拒）；落地＝U14（wire 裁判右源） | 沿用；翻案：`roles` 由代碼陣列改 `UserRole[]`、查詢六欄 |
| `rev5:src/typings/api/rev5-user-center.d.ts`::`Api.UserCenter`（`PasswordPolicyView`／`ChangePasswordReq`） | wire 型 | `src/typings/api/rev6-user-center.d.ts` | 沿用 |
| `rev5:src/locales/langs/zh-cn.ts`／`en-us.ts`（各 (v) 3 塊＋(vi) 1 塊；`page.manage.user` 葉鍵 19→63、`page.userCenter` 7；backend `biz.user` 實發 20＋`auth.session.kickedByAdmin` 併入 `rev5:003` 之 (ii) 圈界） | i18n | 三檔（含 `zh-tw.ts`）：`page.manage.user.*`、`page.userCenter.*`、`page.passwordPolicy.*`、`page.manage.ipRule.unlock.*`、backend 新鍵 22；`route:` 樹零新增 | 沿用；翻案：三語同批（R5 #9）、明細子鍵落 page 樹（R5 #26） |
| `rev5:src/locales/langs/zh-tw.ts`（孤立檔、只補 backend 樹） | 繁中 | 同名：以 `App.I18n.Schema` 標型之完整全樹（臺灣用語） | 翻案（R5 #9） |
| `rev5:src/typings/app.d.ts`（(v) 3 塊＋(vi) 1 塊；backend 型節沿 `rev5:003` 圈界） | 型節 | 同名：page 型節與 backend 型節補鍵；`LangType` 擴 `'zh-TW'`（I18N (iii) 修改型） | 沿用＋新增 |
| `rev5:src/store/modules/app/index.ts`／`src/locales/index.ts`／`src/locales/locale.ts`／`src/locales/naive.ts`／`src/locales/dayjs.ts`（rev5 對 upstream 零 diff、兩語） | 語言 runtime | 同名五檔（I18N (iii)）：未選過預設 zh-TW 三處、`localeOptions` 三語、`zhTW`／`dateZhTW`、`zh-tw` 對映 | 新增（R5 #9） |
| `rev5:src/main.ts`（零改） | 開發期根元件驗證器語言判斷 | 不改 | 沿用（R5 #27） |
| `rev5:src/views/manage/role/index.vue`／`src/views/manage/menu/index.vue`（不做按鈕碼顯隱；選單頁碼註明記 rev4 gating 不帶回） | 角色與選單頁 | 同名二檔（(viii)；並觸 (ii) 既有圈界）：逐鈕 `hasAuth`、表頭 `showAdd`／`showDelete` | 翻案（R5 #8） |
| `rev5:src/views/manage/ip-rule/index.vue`（無解鎖入口；`ipRule:*` 逐鈕顯隱） | IP 規則頁 | rev6 自有檔（`MANAGE-IP-RULE-VIEW+`）：表頭 prefix 插槽「解鎖來源 IP」鈕（`ipRule:unlock`）＋彈窗 | 新增（R5 #3、#16） |
| `rev5:src/components/advanced/table-header-operation.vue`（零 diff；`index.vue` 覆寫 default 插槽之保底 div＝`rev5:B-099` 形） | 共用表頭 | rev6 既有 `showAdd`／`showDelete` 兩布林 prop（005 刀 (ii)） | 不帶保底 div 形（R5 #8） |
| `rev5:src/layouts/modules/global-header/components/user-avatar.vue`（`rev5:007` 零 diff） | 個人中心入口 | 不動 | 沿用 |
| `rev5:src/views/manage/role/modules/menu-auth-modal.vue`／`button-auth-modal.vue`／`endpoint-auth-modal.vue`（`rev5:B-129`）、`src/views/manage/menu/index.vue`（`rev5:B-132` pageSize 歸位） | `rev5:007` 順修 | rev6 已由 006 刀（請求世代、換角色清狀態）與 005 刀（pageSize 歸位）承載 | 不帶（rev6 已有） |
| `rev5:src/typings/components.d.ts`（`rev5:007` 增宣告） | 生成檔 | 同名、工具重算形 | 沿用紀律 |

**commit 範圍**：base-web `rev5:13d11eec`（U2）～`rev5:7b7cd865`（U9）共 8 顆（外層 merge `rev5:5e8b32f` 之 base-web pin＝`rev5:7b7cd865`）；其中 `rev5:fb71df69` 之 `rev5:B-129` 半與 `rev5:84f283c7` 之 `rev5:B-132` 半 rev6 已有。

## R4 rev5 收刀後本域 commit 分類（藍本取 HEAD 形之依據）

量法：`git -C ../fork260509-rev5/rust-api log 0161d73..HEAD` 與 `git -C ../fork260509-rev5/base-web log 7b7cd865..HEAD`，逐顆 `git show --stat` 對 R2／R3 檔集求交（「動到之 R2／R3 檔」欄只列交集、括號旁註為取用面相關之他檔、非全集）。rust-api 收刀後共 12 顆、base-web 共 5 顆。

| commit | 日期 | 動到之 R2／R3 檔 | 分類 | 本刀取用面 |
|---|---|---|---|---|
| `rev5:e02251d` | 2026-08-31 | `auth/no_escalation.rs`、`handler/user.rs`、`model/facade/sys_user.rs`（另 `sys_role.rs`、`facade/mod.rs`） | 行為面零改（重構；`rev5:B-137`／`rev5:B-138`、`rev5:ADR 0072`） | 取 HEAD 形：模糊比對住 `facade/mod.rs::ilike_contains`、超管代碼取 `sys_role::SUPER_ROLE_CODE`（rev6 兩件既有）；auth 側直書第二宣告源不帶（R5 #28） |
| `rev5:7aa0ac3` | 2026-08-31 | `auth/enforce.rs`、`auth/mod.rs`、`envelope.rs`、`handler/common.rs`、`handler/throttle.rs`、`handler/user_center.rs`、`sys_token.rs`、`sys_user.rs` | 行為面零改（重構＋測試；`rev5:B-140`／`rev5:B-141`／`rev5:B-107`／`rev5:B-043`、`rev5:ADR 0073`） | 取 HEAD 形：`Identity.sid` 由 `enforce_mw` 注入、改密讀 `identity.sid`（`rev5:007` 收刀時之 `current_sid` 標頭再驗章形不帶）；`rev5:ADR 0073`「共用件同住 handler::user」與 rev6 落點同向 |
| `rev5:3be868e` | 2026-08-31 | `auth/no_escalation.rs`、`handler/common.rs` | 行為面零改（碼註與測試訊息） | 不帶（碼註重寫） |
| `rev5:e7181f9` | 2026-08-31 | `model/mod.rs`（`test_db::UserCleanup` doc） | 行為面零改（碼註；`rev5:B-135` won't-fix＝`rev5:ADR 0074`） | 不帶（rev6 守衛形不同） |
| `rev5:515177e` | 2026-08-31 | `tests/wire_schema.rs`（`Api.IpRule.*`） | 行為面零改（他域 wire 裁判；`rev5:B-098`） | 不帶 |
| `rev5:51c9f79`／`rev5:b1ec283` | 2026-08-30 | `handler/menu.rs`（另 `role.rs`／`policy_archive.rs`）之 `metric_value` doc | 行為面零改（碼註；`rev5:ADR 0071`） | 不帶 |
| `rev5:e85f447` | 2026-09-01 | `sys_user.rs`（`resolve_ids_by_user_name`）、`session_event.rs`、`sys_operation_log.rs`、`envelope.rs`、`model/mod.rs`、`tests/contract.rs` | `rev5:008` 連動（稽核讀端） | 不帶 |
| `rev5:7833ec7` | 2026-09-01 | `error.rs`（BizData 射程改三鍵、增 `biz.audit.purgeBelowFloor`＝`rev5:ADR 0078`）、`model/audit.rs`（第九詞 `purge`）、`session_event.rs`／`sys_operation_log.rs`（`purge_before`）、`tests/authz_entrypoint_lint.rs`（`PURGE_BEFORE_CALL_FILES`）、`tests/contract.rs` | `rev5:008` 連動 | 不帶（rev6 射程恰兩鍵、詞彙 5→8） |
| `rev5:92919b9` | 2026-09-01 | `model/mod.rs`（test_db）、`handler/auth/logout.rs`（故障注入測） | `rev5:008` 連動 | 不帶 |
| `rev5:dd6db0f`／`rev5:75f65ce` | 2026-09-01 | `tests/wire_schema.rs`（`Api.Audit`） | `rev5:008` 連動 | 不帶 |
| `rev5:b8270630`（base-web） | 2026-08-31 | `src/views/manage/ip-rule/index.vue`（`scroll-x` 註解換 eslint 多行形；`rev5:B-144`） | 行為面零改（格式） | 不帶 |
| `rev5:32afa29e`（base-web） | 2026-09-01 | 無（`rev5-audit.d.ts` 新檔） | `rev5:008` 連動 | 不帶 |
| `rev5:f8c6b957`（base-web） | 2026-09-01 | 三檔 locale＋`app.d.ts`（`biz.audit` 兩鍵；同顆把 zh-cn／en-us backend 檔頭「53 鍵」改「76 鍵」） | `rev5:008` 連動（順手訂正 `rev5:007` 期失準之鍵數碼註） | 不帶（rev6 碼註不寫鍵數） |
| `rev5:365f532d`（base-web） | 2026-09-02 | zh-cn／en-us＋`app.d.ts`（system-settings 頁樹） | `rev5:008` 連動 | 不帶 |
| `rev5:9833308b`（base-web） | 2026-09-02 | zh-cn／en-us＋`app.d.ts`＋`components.d.ts`（audit 頁樹） | `rev5:008` 連動 | 不帶 |

**分類計數**：17 顆＝行為面零改 8 顆（重構 2：`rev5:e02251d`／`rev5:7aa0ac3`；碼註 4：`rev5:3be868e`／`rev5:e7181f9`／`rev5:51c9f79`／`rev5:b1ec283`；他域測試 1：`rev5:515177e`；格式 1：`rev5:b8270630`）＋`rev5:008` 連動 9 顆（rust-api 5、base-web 4）＋**缺陷修正 0 顆**。缺陷修正為 0 之證：收刀後動到 R2／R3 檔之 commit 無一改變 12 支端點、unlockLogin 帳號維或使用者域前端之判定、寫入與畫面行為——兩顆重構之 commit 訊息皆載「零行為改動」與容器全量 serial 綠（`rev5:e02251d`＝998、`rev5:7aa0ac3`＝1000＝基線＋恰 2 支新測），碼註四顆為純註解 diff，`rev5:008` 九顆為稽核與系統設定之增量（新端點、新詞彙、新樹），與使用者域交集只在共用檔之新增函式與 BizData 射程句。

**藍本取 HEAD 形之依據**：①rev5 HEAD 之使用者域行為＝`rev5:007` 收刀行為，HEAD 只多兩顆零行為重構與數顆碼註，取 HEAD 形可直接得到 `Identity.sid`、`SUPER_ROLE_CODE` 單源、`ilike_contains` 共用件三項較優終態（rev6 已有後兩項）；②無缺陷修正＝取 HEAD 不會漏帶修補、取收刀形亦不會缺修補，兩者行為同；③`rev5:008` 增量逐顆列入上表「不帶」，實作單元讀 HEAD 檔時以本表剔除（BizData 第三鍵、`Purge` 詞彙、稽核讀端函式、purge 名冊與其契約案）；④前端使用者域檔（`user/index.vue`、抽屜、解鎖彈窗、產密浮層、個人中心兩檔、`pwd-policy.ts`、`pwd-login.vue`、兩支包裝與兩支型別、`user-avatar.vue`）自 `rev5:7b7cd865` 至 HEAD 零 diff ⇒ 22080 之使用者頁、個人中心、登入頁即 `rev5:007` 收刀形，可直接當 CDP 基準；角色頁與選單頁收刀後亦零 diff；IP 規則頁只差一處註解格式；系統設定頁與稽核頁為 `rev5:008` 面＝CDP 排除之死項。

## R5 rev6 拍板差異點（翻案與新增；implementer 防回歸清單）

本表烤入 implementer 與 review prompt：藍本相反處一律以「rev6 本刀形」為準、不得回帶；「rev5 HEAD 形＝rev6 形」之列，防回歸對象另載於要點欄。他節以「R5 #n」引用列號。ADR 號為本刀 plan 期 draft（配號與親決時點＝R21）。

**A. brainstorm §1 翻案與翻案不帶回四項**

| # | 差異 | rev5 HEAD 形 | rev6 本刀形 | 承載 | 防回歸要點 |
|---|---|---|---|---|---|
| 1 | migration | 零 migration（seed 不動） | 一支 seed-only `m0003_seed_button_governance.rs`：列 58～63 受保護、刪列 44、增列 164（`ipRule:unlock`）、選單 78 按鈕清單增碼、序號推進；演進帳九筆；schema 閘 seed_add 序號合成；schema-definition 不前進 | GR1a、GR4、GR7、GR8、GR9、工程判斷⑰、FR-041／FR-045、ADR-00085、ADR-00087 | 零 DDL；逐句 rows_affected 恰等、不符整支回滾（不以 ON CONFLICT 吞錯）；不走執行期撤銷歸檔與操作稽核；Day-1 第 3 步以全新庫驗 |
| 2 | 可空文字欄空字串（Q16） | 新增經 `blank_to_none` 摺疊、更新三態透傳（`""` 照存、信箱 `""` 判 `userEmailInvalid`）；前端更新端已轉 null＝畫面零差 | 新增與更新同形：暱稱、手機、信箱、記事之空字串＝清空存 NULL；值 diff 於歸一後比 | Q16、FR-012／FR-013、ADR-00080 | rev5 碼註「三態透傳、不做空字串摺疊」不得照抄；信箱 `""` 不再報格式錯；兩帳號同送空信箱不得撞活性唯一索引（索引只排除 NULL） |
| 3 | 解鎖入口（Q9） | 使用者頁頁首鈕＋雙維彈窗 `user-unlock-modal.vue`（`user:unlock`） | 帳號維＝使用者列操作「解鎖登入」（不顯示鎖定狀態、每列可按）；來源維＝IP 規則頁表頭 prefix 插槽鈕＋`ip-unlock-modal.vue`（`ipRule:unlock`）；兩入口共用 `fetchUnlockLogin` | Q9、GR3、GR4、FR-040、ADR-00082（款 1 解除） | 不帶回雙維彈窗與頁首鈕；送出仍顯式帶 `dimension`；對未鎖帳號照常 0000 並落一筆解鎖稽核 |
| 4 | 使用者域授權重載（翻案不帶回①） | updateUser 角色集實際變更、deleteUser／batchDeleteUser 標的原有指派時 commit 後 `reload_enforcer`；`RELOAD_CALL_FILES` 含 `handler/user.rs` | 零 reload：`finish_user_write` 無 reload 旗標；`RELOAD_CALL_FILES` 零擴列＋反向確認測試（使用者域寫端檔不呼 reload） | 工程判斷④、FR-061、spec 刻意分岔表「使用者寫端之授權重載」列（觸發矩陣零變更＝無 ADR 落點：使用者域寫端不寫 `casbin_rule`、ADR-00043／ADR-00067 之矩陣列數不變） | seed `g` 列 0、每請求 `roles_of_user` 現查；rev5 該觸發之理由（`rev5:B-093` 繼承窗）在 rev6 已由 deleteRole 家族觸發同步關閉 |
| 5 | inline 標記 token（翻案不帶回②） | `[rev5-inline <軌道>(用途) 007-user-password-admin]`；新檔頭 `BASE-WEB-MANAGE-PAGE-WIRING(v)+` | `[rev6-inline <軌道>(用途) 007-user-password-admin]`；新檔首行一行 `[rev6-inline <標籤>+ 007-user-password-admin]`：`MANAGE-USER-VIEW+`／`MANAGE-IP-RULE-VIEW+`／`USER-CENTER-VIEW+`；包裝與型別 `BASE-WEB-WRAPPER+`／`BASE-WEB-ADAPT+`；新檔內不開圈界 | brainstorm §1、FR-054、憲法 §III | rev5 之 `(v)+` 形被 `tools/fork-delta-lint.py` 新檔軌道判定判紅；`原行:` 必與標記同行 |
| 6 | 測試守衛（翻案不帶回③） | `test_db::UserCleanup`（寫死 `setval('sys_user_id_seq', 3, true)`）／`SeedUserRestoreCleanup`／`PwdCustodyCleanup`／`SessionRevokeCleanup`／`SeedOpLogCleanup` | `UserRowsGuard`（`sys_user` 帶界水位＋`sys_user_id_seq` arm 現讀）、`SeedUserRestoreGuard`（seed 三帳號全可寫欄＋審計欄快照）、`PwdCustodyRowsGuard`、`UserRoleRowsGuard` 增 user_id 帶界腿與界下指派回補腿、`RedisKeysGuard` 以 `track(cache::change_pwd_key(uid))` 逐鍵承接（型不改）；`tests/common/mod.rs` 鏡像 `UserWriteGuard`／`SeedUserWriteGuard`／`PwdCustodyWriteGuard` | brainstorm §1、FR-062、RL-0031 | 不寫死序列值；先 arm 再寫；seed 帳號欄值以快照還原；守衛早於任一寫 seed 帳號或指派之單元 |
| 7 | 前代命名空間（翻案不帶回④） | `rev5-user-admin.{ts,d.ts}`／`rev5-user-center.{ts,d.ts}`（`Api.UserAdmin`／`Api.UserCenter`） | `rev6-` 前綴新檔重打字；型別命名空間名 `Api.UserAdmin`／`Api.UserCenter` 沿 rev6 `Api.RoleAdmin`／`Api.MenuAdmin` 先例 | brainstorm §1（讀法＝plan 期主線定案：不帶回者為 `rev5-` 前綴檔與其宣告本體）、FR-053 | 宣告本體不得自 rev5 檔複製；型內容依 rev6 契約（角色欄、六欄查詢） |
| 8 | 按鈕碼顯隱（Q8） | 使用者頁七碼逐鈕；角色、選單頁不 gating（判準＝該頁選單維政策是否僅 R_SUPER＝`rev5:ADR 0063` 款三）；表頭以覆寫 default 插槽之保底 div 承載新增與批刪 | 使用者頁七碼＋角色頁、選單頁依 add／edit／delete 逐鈕 `hasAuth`；表頭新增與批刪走既有 `showAdd`／`showDelete`；rev5 判準不帶 | Q8、工程判斷⑬、FR-048、ADR-00074（(viii)）、ADR-00081（款 18） | 選單回收桶復原鈕與角色抽屜三授權鈕不設碼；不覆寫表頭 default 插槽 |
| 9 | 繁中 runtime（Q4、Q4a） | `zh-tw.ts` 孤立檔只補 backend 樹；runtime 兩語、未選過＝zh-CN | `LangType` 擴 `'zh-TW'`、三處註冊、`localeOptions` 三語、未選過預設 zh-TW、`zh-tw.ts` 為 Schema 全樹 | Q4、Q4a、FR-052、ADR-00084 | CDP 三側（22080、32080、22089）之步驟一律顯式設簡中（rev6 未選過即繁中）；`<html lang>` 首開同步（`src/locales/index.ts`）；本刀起三語同批 |

**B. rev5 未解或無藍本之本刀新題**

| # | 差異 | rev5 HEAD 形 | rev6 本刀形 | 承載 | 防回歸要點 |
|---|---|---|---|---|---|
| 10 | 持停用角色之帳號（Q13） | 清單 `roles`＝代碼陣列；抽屜以 `unresolvedRoleCodes`／`roleAssignLocked` 鎖住整個角色欄（`rev5:B-145` 未解） | 清單帶 `{id, roleCode, roleName}`（`sys_user_role::roles_by_user_ids`）；抽屜以「（已停用）」灰色保留選項（不可新選、可移除、預設保留）；`getAllRoles` 口徑不動 | Q13、FR-020、ADR-00081（款 7 結案） | 不帶回鎖整欄形；世代守與讀取三態保留；清單角色欄顯示照 rev5 以代碼串接 |
| 11 | 清單過濾面（Q17） | 後端四欄（帳號名、暱稱、狀態、性別）、搜尋卡零改動（`rev5:B-143`） | 後端六欄（帳號名、暱稱、手機、信箱部分字串比對；性別、狀態等值）；`user-search.vue` 入 (v) 拔兩欄格式驗證 | Q17、FR-007、FR-047 | 不得只補後端（搜尋卡驗證仍擋臺灣號碼與部分字串） |
| 12 | 清單 wire 偏離帳（Q14） | 無 | wire 裁判導出與 upstream `Api.SystemManage.User` 之差集、漂移即紅 | Q14、FR-008、ADR-00083 | 使用者管理頁不再消費 upstream 舊函式；`plugin/excel` 示範頁＝殘存消費面（零 diff；ADR-00083 決定 3；user 2026-10-05 親決） |
| 13 | 走查還原與殘列（Q21、Q22） | 走查工具只有 snapshot／diff、無 restore；測試守衛不補 seed 指派 | 工具 v4：遷移帳前置（基準檔所記已套用遷移清單與現庫不等＝寫入前拒跑 rc 2、零寫入、指名差異並指示重拍）、seed 指派按原值回補、新帳號列與指派刪除並回序列、`sys_user` 可變欄（含軟刪兩欄）回寫、清理面增 `sys_pwd_custody`（全表清空、無序列）與 redis 前綴 `cpwd:`；seed 模式目標態與**兩模式之系統設定比對**一律以凍結 seed ⊕ 演進登記合成 | Q21、Q22、FR-057、FR-058、ADR-00085 | 日後 migration 增改設定項時兩模式以合成值比對、不拒跑；仍拒跑者＝清理面各表之 `seed_*` 登記、合成面表之結構演進屬 schema 閘合成未內建之形（與 gate2 同停、同一擴充點補齊即兩者恢復）、前置不符（基準遷移帳不等、repo 與現庫遷移不同步）；遷移帳前置所在單元早於撰寫 m0003 之單元 |
| 14 | 超管角色與選單六碼（GR1、GR1a） | 列 58～63 非受保護、可於按鈕權限彈窗自撤 | m0003 改受保護（受保護列 19→25）；撤之＝既有 `biz.role.protectedRevoke` 整批拒 | GR1、GR1a、FR-041／FR-042、ADR-00085 | 按鈕維受保護列不入封死集；受保護旗標永不 UI 化 |
| 15 | 選單編輯移除受保護授權碼（GR1b） | updateMenu 照常移除並連動歸檔（含 R_SUPER 列） | 移除集（含改碼之舊碼）含受保護授權列之碼＝整筆拒（`biz.menu.protectedButtonRemove`）；判定於歸檔之前、與受保護選單守門並列 | GR1b、FR-043、ADR-00086 | 零變更、零稽核、零判定面同步；正負向＋變異自證 |
| 16 | IP 規則頁解鎖碼（GR4） | 無 `ipRule:unlock` | m0003 增 R_SUPER 列 164（不受保護）、選單 78 按鈕清單尾端增 `{"code":"ipRule:unlock","desc":"解鎖來源IP"}` | GR4、FR-040／FR-041、ADR-00085 | 同一支解鎖 API 由兩頁兩碼各自顯隱 |
| 17 | Admin 預設編輯鈕（GR7） | R_ADMIN 持 `user:edit`（列 44）＝見編輯鈕、送出 5003 | m0003 刪列 44；Admin 預設只見清單 | GR7、FR-044、ADR-00085、spec 刻意分岔表 | seed 錨測試同批改（FR-046） |
| 18 | 密碼政策壞值（Q19） | min>max 自然全拒、無告警 | 同方向全拒＋計數族 `password_policy_invalid_total`（無 label、預註冊 0、發射出口 `obs::password_policy_invalid()` 恰一處）＋告警規則 `obs016-password-policy-invalid`＋一則 warn | Q19、FR-034、ADR-00079 | 不併入 `throttle_degraded_total`；設定寫端不加守門；與島 E「整組退」方向相反＝跨島註 |
| 19 | 繁中機器檢查（GR5） | 無（zh-TW 不在 runtime） | 新碼面閘 `tools/zh-tw-lint.py`（簡體殘字＋具名白名單＋禁用大陸用語表＋「頂替」「踢除」語意檢查；掃 `zh-tw.ts`（字表完備腿另讀 `zh-cn.ts`）；pre-commit 於 base-web pin bump 或工具本體 staged 時跑、bootstrap 跑自測；名冊＝RUNBOOK §12） | GR5、FR-052、SC-009、ADR-00084 | 一正一反自證；碼面閘不占 GT 閘預算 |

**C. plan 期主線定案（工程判斷）**

| # | 差異 | rev5 HEAD 形 | rev6 本刀形 | 承載 | 防回歸要點 |
|---|---|---|---|---|---|
| 20 | 改密節流鍵 | `cpwd:{uid}`、5／900、fail-open、降級源 `redis_change_pwd`（rev5 名冊 12→13） | 同鍵同常數（碼內常數）；降級源名冊 10→11 | Q20、工程判斷③、FR-037、ADR-00078 | 鍵不放 `throttle:` 之下（維運批次清登入節流鍵不得誤清改密桶）；數量詞取 rev6 實數；只有舊密不符推進計數、拒絕路徑零推進、成功即清 |
| 21 | 指派寫端之角色列鎖 | 角色列只讀不鎖（`codes_of_role_ids` 只濾軟刪） | 使用者列 FOR UPDATE 後，對 T∪N 去重升序以 `sys_role::find_active_by_id_for_update` 鎖讀並鎖內重驗未軟刪；刪除家族鎖 T；kick／reset／sessionPolicy 不鎖角色列 | 工程判斷②、FR-011、憲法 G5 末句（轉非 vacuous）、ADR-00074（島 I1） | 不得只鎖 N（留解除指派與 deleteRole 計數間之保守誤拒窗）；不得以鎖外 pre-read 判角色存在 |
| 22 | 批次寫端取鎖序 | 逐 id 交錯：advisory(id)→列鎖(id)→守門→下一 id | id 去重升序→先依序取完全部 advisory→再依序鎖全部使用者列→整批 T 聯集一次升序鎖角色列 | FR-010／FR-011、R7 | advisory 早於任何列鎖；與單筆寫端不成 ABBA |
| 23 | `advisory_lock_user` 簽章 | 泛型 `C: ConnectionTrait`（rev6 現亦同） | 只收 `&DatabaseTransaction`（比照 `enter_menu_domain`）＋compile_fail doctest | R7 | 傳入 autocommit 連線＝即取即放、型別須擋住 |
| 24 | 撤票原語 | rev5 HEAD 形＝rev6 形：`revoke_sids_of_user` 迴圈底座（SELECT 帶頭、跨輪去重）、`revoke_all_of_user` 薄殼 | 同；既有 `revoke_others_of_user` 改走同一底座 | FR-026、R10 | 防回歸對象＝單句 UPDATE 形（漏撤並發 rotate 之後繼列）；`CreatedBy.eq(uid)` 過濾不可拿掉；只撤 active、不動 rotated |
| 25 | 錯誤變體 | `BizData`／`ModalLogoutByAdmin`（2222／7777）；HEAD 射程句為三鍵（含 `rev5:008` 之 `biz.audit.purgeBelowFloor`） | 同名二變體（9→11）、射程恰兩鍵；`error.rs` 檔頭「屬後刀域、不帶」句勘誤 | FR-004、ADR-00076 | 不帶 `rev5:008` 第三鍵；5003 恆純 key；BizData 之 match 臂須被 `tools/msg-key-gate.py` 判為非構造（`rev5:L-064` 形） |
| 26 | 明細子鍵與分隔符落點 | `backend.biz.user.passwordViolation.*` 八鍵＋`backend.common.listSeparator`（`rev5:003` 預建之「後端恆不發」白名單）＋`DETAIL_LIST_ITEM_KEY` | `page.passwordPolicy.violation.<code>` 八枚＋`page.passwordPolicy.listSeparator`（page 樹、三語各一、新增型圈界歸 `BASE-WEB-I18N-WIRING(i)`）；backend 樹只放 `MSG_KEYS` 成員；明細轉譯本刀新建、只兩鍵 | FR-033、FR-051、ADR-00076、ADR-00074（I18N (i) 改寫） | backend 子樹多一鍵即跨端閘紅；請求層 wire 形字面同批入 `FRONTEND_MSG_CONSUMERS`；清單角色欄分隔符另取 `page.manage.user.roleSeparator`、不借本命名空間 |
| 27 | `src/main.ts` 根元件驗證器 | 不改（rev5 無 zh-TW runtime） | 不改：`getLocale() === 'zh-CN' ? 'zh' : 'en'` 維持；zh-TW 下開發期提示為英文＝已知態；不入 ★ 軌道登記表 | spec ★ 軌道表與 Edge Cases（plan 期改定案句）、ADR-00084 | 不為此動 `main.ts`（近 12 月 upstream 有改動之高風險檔） |
| 28 | 包含規則之比對單位與超管判定 | `ActorScope::Codes(HashSet<String>)`、比對 role_code、`assert_no_escalation -> Result<(), ()>`；auth 側直書 `ROLE_SUPER`（`rev5:ADR 0072` 兩宣告源 by-design） | `ActorScope { All, Roles(BTreeSet<i64>) }`、比對 role id、回 `Result<(), AppError>`；超管代碼取 rev6 既有 `sys_role::SUPER_ROLE_CODE` 單源（rev6 auth 層既已依賴 `model::facade`、無分層理由另立第二宣告源＝本節工程判斷） | FR-021／FR-022、ADR-00075、R9 | T 不濾角色狀態、A 濾軟刪與停用（兩邊濾法不對稱是刻意的）；warn 只三欄（操作者、標的、端點）、不含角色差集 |
| 29 | 掛點可見性與名冊閘 | `guard_no_escalation`／`finish_user_write` 為 `pub(crate)`；`NO_ESCALATION_CALL_FILES` 與 `GUARD_NO_ESCALATION_CONSUMER_FILES` 兩名冊；另立 `FINISH_USER_WRITE_CONSUMER_FILES` | `pub(super)`；`NO_ESCALATION_CALL_FILES`＝[`handler/throttle.rs`, `handler/user.rs`]（路徑字典序；`guard_no_escalation` 裸 token 三形之生產出現檔集兩向恰等）；不立 finish 名冊、改以每支撤票端點之失效名單寫入測試承載 | FR-061、SC-005、ADR-00075、RL-0070 | 可見性日後放寬須同批補消費者名冊；拆掉判定呼叫須有測試轉紅 |
| 30 | seed 結構保護常數落點 | `sys_user::USER_SEED_IDS`／`SUPER_USER_ID`（facade） | `handler/user.rs::SEED_USER_IDS`／`SUPER_USER_ID` | FR-017 | 碼內常數形；Super 恆禁停用、恆禁解除其 R_SUPER 指派 |

**D. rev5 HEAD 形＝rev6 形（防回歸對象另有所指）**

| # | 差異 | rev5 HEAD 形 | rev6 本刀形 | 承載 | 防回歸要點 |
|---|---|---|---|---|---|
| 31 | 換發活性重驗（Q12） | active 腿票列鎖後、簽發前以 `sys_user::find_by_id`（plain）重驗，不活 rollback＋8888；grace 腿回既發同一對、不重驗 | 同；refresh 10 案＋logout 1 案改種帳號列 | Q12、FR-028／FR-029、ADR-00074（島 I2） | 不取 advisory、不改換發鎖序；不新增每請求活性判定；`rev5:007` research 敘述之「撤該列＋8888」不採（as-built 為零寫 rollback） |
| 32 | 三向分派 | `enforce_mw` 與 refresh revoked 腿：`kicked`→`ModalLogout`、`admin_kick`→`ModalLogoutByAdmin`、其餘→`Logout` | 同；cache 增 `REASON_ADMIN_KICK` | FR-027、GR2、ADR-00074（島 C 改述） | 漏接 refresh 一處＝存取權杖過期後退化為靜默 8888；`auth.session.kicked` 文案不變 |
| 33 | `Identity.sid` | HEAD（`rev5:7aa0ac3` 後）三欄、`enforce_mw` 自 `claims.sid` 注入、改密讀 `identity.sid` | 同 | FR-036、ADR-00077（ADR-00014 後果段「注入形不變」句之註記） | 不帶回 `rev5:007` 收刀時之 `current_sid` 標頭再驗章形；活書 06／08 注入形句同批改 |
| 34 | 自助路由白名單（Q11） | `SELF_SERVICE_ROUTES = ["user-center"]` 於授權過濾後恆併入 | 同；`handler/route.rs` 檔頭前代歸因改為 `rev4:014` 起源、`rev5:007` U4 帶回 | Q11、FR-039、ADR-00077 | 併在過濾之前＝零選單政策角色失效且不會紅；白名單只收受眾＝本人之頁 |
| 35 | 同值 no-op（Q15） | 使用者域缺席早退＋值 diff（同值零寫、零稽核、不動時戳） | 同；與角色選單域（ADR-00047 決定 3：同值照寫照稽核）之逐域差異明文 | Q15、FR-013、ADR-00080 | 兩域不得互相「對齊」；rev5 值 diff 兼作 reload 條件之用途在 rev6 消失 |
| 36 | unlockLogin 帳號維 | 開交易→查帳號（查無即放行）→advisory→包含規則→`write_in_txn`→commit→寫標記 | rev6 現為裸連線 `sys_operation_log::write(&state.db, event)`＋源碼次序釘 `handler_order_verdict`；本刀改「begin→解析帳號→advisory→`guard_no_escalation`→`write_in_txn`→commit→寫標記」，IP 維不變 | FR-021、FR-040、ADR-00075 | 源碼次序釘與其反例同批更新；「稽核先於標記」不變；拒＝零稽核 |

**E. rev6 既有形（本刀必守、藍本為異形）**

| # | 差異 | rev5 HEAD 形 | rev6 本刀形 | 承載 | 防回歸要點 |
|---|---|---|---|---|---|
| 37 | 交易歸屬與稽核層 | handler 開交易、facade 寫入函式收 `&AuditOperator` 自寫稽核（`audit_json` 等住 facade） | handler 持交易、內層 `<op>_in_txn`、稽核以 `sys_operation_log::write_in_txn` 於同交易落；facade 公開寫入口只收 `&DatabaseTransaction`、不收操作者、不寫稽核 | FR-006／FR-011、005 刀既有形、R6 | facade 不得長出稽核寫入；業務列與稽核列同交易 |
| 38 | 操作者取得 | `common::audit_operator`（帶 degraded 欄、借 `security.ipgate` target） | `common::operator_from_context`＋本域私有 `operator_from`（本域 target、`refused` 欄、零 degraded）；先於一切守門 | FR-006 | 缺席＝拒寫 5000、不以佔位補稽核列；`real_ip` 缺席拒寫 |
| 39 | msg 鍵構造 | 構造點寫 `Cow::Borrowed("biz.user.<鍵>")` 字面 | `error::msg_key` 具名常數；`MSG_KEYS` 46→68 | FR-004、`tools/msg-key-gate.py` | 鍵隨首發單元落地、三檔 backend 子樹與型節同批 |
| 40 | 雜湊 API | argon2 0.5.3、`SaltString::generate(&mut OsRng)` | argon2 0.6：`getrandom::fill` 16 bytes＋`hash_password_with_salt`、`Argon2::default()`；`NewPassword::prepare` 於交易內、取鎖前算（spec FR-012：begin 之後、首個鎖之前） | R1、R11、ADR-00074（I5 釐清句） | 雜湊生成不在列鎖內（源碼掃描守）、驗證屬守門在鎖內 |
| 41 | 分頁與名稱回填 | `common::MAX_CURRENT` 自持 clamp、`resolve_operator_names` | `envelope::page_params`／`PageRes`／`PAGE_MAX_CURRENT`、`sys_user::find_names_by_ids` | FR-007、ADR-00058 | 不收排序參數；逾界＝空頁 |
| 42 | 部分更新三態 | `common::tristate`（rev5 語意含空字串透傳） | `common::tristate`（ADR-00047 骨架＋使用者域逐域明文＝ADR-00080） | FR-013 | 不可變欄出現即拒（含 null） |
| 43 | Vue 模板修改型標記 | 整行替換之 `原行:` 置於多行 HTML 註解 | 改動落在元素開標籤之內＝「Vue 模板屬性行變體」（標記置開標籤正上方、點名被改之屬性）；整行替換照一般修改型 | 憲法 §III | `原行:` 與標記同行 |
| 44 | 唯一違反判定 | `violated_constraint(e) -> Option<&str>`、呼叫端自比索引名 | 既有私有 `violated_constraint(err, unique_index) -> bool`（只認指名索引之 23505） | 既有 `model/facade/mod.rs`、R8 | 新增撞名、撞信箱與復原之兜底皆經此件 |
| 45 | 降級源發射形 | 具名常數 `DEGRADED_SOURCE_CHANGE_PWD`、名冊為私有常數 | 經既有 `throttle::warn_degraded("redis_change_pwd")`、名冊 `obs::THROTTLE_DEGRADED_SOURCES` 預註冊；「恰十」數量詞同批改「恰十一」 | FR-037 | 名冊雙向守；快取缺席（測試 seam）直接放行、不記降級 |
| 46 | 列 68 前提與條數釘值 | `rev5:B-113` 探針升真 assert（`rev5:2273816`）；政策端點數無具名常數 | 四支以「本刀端點未註冊」為前提之既有測（`handler/role.rs`::`super_reads_leave_off_candidate_seed_grants_in_the_table_and_out_of_the_response`〔列 68〕、`model/facade/sys_casbin_policy.rs`::`seed_reads_and_the_seal_set_match_the_seed_facts`〔列 68〕、`tests/contract.rs`::`governance_endpoint_grants_real_seed`〔列 68、`(50, 15)`〕、`tests/contract.rs`::`governance_reads_real_seed`〔seed 列 2 屬候選外〕）改植合成探針列或依新路由現算改值；`router.rs` 測試常數 `POLICY_ROUTE_COUNT` 與各處「35」「(35, 14)」等字面依新路由現算同批改（政策端點 35→45、候選內受保護 14→15 等） | FR-001、FR-061、RL-0011 | 註冊路由之單元允許檔須含 `router.rs`、`handler/role.rs`、`model/facade/sys_casbin_policy.rs`、`tests/contract.rs`；errata 以名掃不到之數字字面另以數量詞掃 |

**F. plan 收攏期補列（核對與評審所得；主線工程判斷）**

| # | 差異 | rev5 HEAD 形 | rev6 本刀形 | 承載 | 防回歸要點 |
|---|---|---|---|---|---|
| 47 | 批刪多重違規之拒因 | 逐 id 交錯（advisory→列鎖→守門→下一 id）＝取 id 最小者之首個違規 | 全部 advisory 與列鎖先取完（R5 #22）後逐步全批：①全批鎖列查無＝notFound→②全批任一 seed＝seededProtected→③含本人＝cannotDeleteSelf→④逐筆 T⊆A；同步全批判完才進下一步、拒因由步序定（與 id 排列無關）、不指筆 | FR-010、FR-014、ADR-00080（決定 8） | 多 id 異類違規時拒因可與 rev5 異（API 層、畫面零差）；不得退回逐 id 交錯判定 |
| 48 | addUser 成功回應 | `data: {id}`（`AddRes`） | `data: null`（沿 rev6 addRole；不立 `AddRes`） | R14、contracts/wire-user-admin.md | 前端新增後重拉清單＝UI 零差；不帶回 `AddRes` |
| 49 | 寫端固定序 | 包含規則位於業務守門之後；addUser 帳號名與信箱唯一先於信箱格式 | spec FR-010 固定序（④ 包含規則先於 ⑤ 業務守門）；⑤ 內信箱先格式後唯一 | FR-010、R8 | 多重違規取先序腿（凍結入契約）；API 層、畫面零差 |

**G. rev5 HEAD 形＝rev6 形（plan 收攏期定案、防回歸）**

| # | 差異 | rev5 HEAD 形 | rev6 本刀形 | 承載 | 防回歸要點 |
|---|---|---|---|---|---|
| 50 | 包含規則之 N 含界外角色 id | roleIds 帶不存在或已軟刪之 id 時 N 構造不出⇒只判 T⊆A、⑤ 回 roleNotFound | 同（N＝T；roleNotFound 於 ⑤ 原位發） | FR-010／FR-021、ADR-00075 | 不得改為 N 取原值而令非超管得 5003（抽屜列全部活性角色、無實質存在性 oracle；過期選取得準確拒因） |
| 51 | 會話政策寫端缺席 | `sessionPolicy` 以 `String` 承載、缺席即空字串→`sessionPolicyInvalid` | 同（`Option<String>` 承載；缺席、null、空字串、值域外皆 `2222`＋`biz.user.sessionPolicyInvalid`；判於 ⑤、①～④ 之後；同值 no-op） | FR-018、spec Edge「同值 no-op」、ADR-00080 | 不得做成缺席早退 `0000`；body 缺席（id 0）先於 ① 得 notFound |

**rev5 碼註與文件已知錯誤（不得照抄）**：①`rev5:src/views/_builtin/login/modules/pwd-login.vue` 論證碼註把 `REG_PWD`（`/^\w{6,18}$/`＝6～18 位英數底線）之規格寫成 `formRules.userName` 之規格；實際為 `REG_USER_NAME`（4～16 字、可含中文、底線與連字號）——rev6 碼註照實寫。②同檔 `rev5:003` 圈界首行殘留「★(ii) formRules 放寬不帶回——R3-12、延改密端點刀」（(ii) 已落地而未改）——rev6 對應句（`pwd-login.vue` 003 刀圈界首行「(ii) formRules 放寬不在授權內、不動」）於 (ii) 落地同批改現在式。③`rev5:007` research R5「軟刪角色因 in-use 守門結構上無指派列」並發下不成立（指派寫端無鎖讀、deleteRole 鎖後軟刪之序可留指派於已刪角色）——rev6 以 R5 #21 關窗。④`rev5:007` research R6「不活 ⇒ 撤該列＋8888」與 as-built（rollback、零寫）不符——取 as-built。⑤`rev5:007` spec FR-033 並陳「Applied 即觸發、不問 diff」與「角色集實際變更」兩說——rev6 零 reload、不承此條。⑥rev5 憲法 (v)(vi) 範圍欄寫兩語 locale「各 1 塊」、`app.d.ts`「1 塊」，as-built (v) 每檔 3 塊——rev6 範圍欄經機器對賬，預估依 rev6 實況、收刀前 PATCH 實數化。⑦rev5 locale backend 檔頭鍵數碼註於 `rev5:007` 收刀時寫「53 鍵」而實數已 74（`rev5:008` 方訂正）——rev6 碼註不寫鍵數。⑧rev5 HEAD `error.rs` BizData 射程句為三鍵、`obs.rs` 降級源名冊數量詞為 12→13——rev6 皆取本代實數（兩鍵、10→11）。⑨rev5 文件就地勘誤項取勘誤後形：契約 msg-keys 之 `page.manage.user` 既有葉鍵為 19（非 21）、政策「八鍵」實為七設定鍵＋`maxBytes` 碼內常數、unlockLogin 來源維欄名為 `target`（非 `ip`）、手機「≤32」為描述性上界不守門（`rev5:ADR 0069`）。

**rev5 對 rev4 之防回歸要點（本刀照帶、烤入 prompt）**：帳號名出現即拒、值不比對／角色鍵一律 `id`、`roleIds`＝期望全集、界外或已刪 id 整筆拒（非靜默略過）／審計欄 `createdAt`／`createdBy`（帳號名、查無 null）／`needChangePwd` 不帶回／unlockLogin `dimension` 必給／動詞不符 4040、刪除兩支用 DELETE／`scroll-x`＝各欄寬之和、增刪欄同批改／各頁自備 i18n 鍵、不跨頁借鍵／經手表只 upsert（不做「自改即全刪」）／改密卡不放信箱與手機假選項、回收桶不帶 `deletedAt` 孤兒鍵／`forbidUsername`＝不分大小寫全等（子串不算）／登入路徑不驗政策／denylist TTL＝refresh 全壽命／踢除與停用撤全部 active、不動 rotated（logout 只撤呈遞列＝ADR-00033 不變）／新三詞稽核 payload 只帶 `{id, userName}`、不含任何 `$argon2` 字樣／`real_ip` 缺席拒寫 5000。

## R6 模組邊界與共用件落點

- **Decision**:
  1. **handler 兩檔分域**：管理面十支住**新建** `handler/user.rs`（新域 target `security.user`；本域 `BODY_FALLBACK_MSG`＝「使用者寫端 body 取用失敗——收斂成空請求交守門判」；私有 `operator_from` 之拒寫訊息＝「使用者寫端取不到操作者來源 → 拒寫 5000（不以佔位位址補稽核列）」；私有 `db_failure(endpoint, step)`）；個人中心兩支住**新建** `handler/user_center.rs`（新域 target `security.user_center`；`BODY_FALLBACK_MSG`＝「個人中心寫端 body 取用失敗——收斂成空請求交守門判」；拒寫訊息＝「個人中心寫端取不到操作者來源 → 拒寫 5000（不以佔位位址補稽核列）」）。切分判準＝前者 `Protection::Policy`、標的取自 body、寫端八支全受包含規則；後者 `Protection::Authed`、標的恆＝`Identity.uid`（spec FR-003）、不掛包含規則。`handler/mod.rs` 宣告兩模組（ASCII 升冪 `throttle` < `user` < `user_center`）、「九域」改「十一域」；同檔檔頭「跨 handler 共用件恰一支＝`common`」句同批改述為「跨 handler 共用件＝`common`（各域共同核心）＋`user` 域對外之 `pub(super)` 五件（第 2 款；消費者＝`throttle`、`user_center`）」（R22 errata 種子）。
  2. **跨檔共用件恰五支，住 `handler/user.rs`、`pub(super)`**（不上 crate 面，同 `handler::common` 檔頭「可見性」條）：`guard_no_escalation`（R9；消費者＝本檔八支寫端＋`handler/throttle.rs` 之 unlockLogin 帳號維）、`revoke_sessions_in_txn`（交易內撤票＋逐 sid 會話事件）、`finish_user_write`（commit→逐 sid 盡力寫失效名單）、`password_policy_err(violations)`／`pwd_set_too_frequent_err(remaining_seconds: u64)`（兩攜參鍵之單一組裝點＝生產 `BizData` 構造點恰此二；R11）——後四支之消費者＝本檔相關寫端＋`handler/user_center.rs` 之 changePassword（R10、R11）；依 RL-0070 已核五支函式體零受 token 閘守之呼叫。冷卻計算件不住 handler（`model/password.rs::cooldown_remaining_secs`；R11）。seed 保護常數 `SEED_USER_IDS: [i64; 3] = [1, 2, 3]`、`SUPER_USER_ID: i64 = 1` 住同檔、只供守門②，與 seed 三列之一致性以讀庫釘值案釘住（判準不與常數共變；形同 `sys_role.rs` 之 `seeded_role_constants_match_the_seed_rows`）。
  3. **交易形以 `handler/role.rs` 模組 doc「寫端不變式」為準**（操作者上下文先於一切；外殼 begin → 內層 `<op>_in_txn` → 稽核 → commit、失敗腿顯式 rollback；提前 no-op 與被拒腿零稽核；body 經 `common::json_or_default`、三態經 `common::tristate`）。使用者域內層首句＝`sys_user::advisory_lock_user(txn, 標的 uid)`（addUser 不取；批次取法＝R7）。收場：有撤票＝`finish_user_write`；無撤票之成功＝外殼直 commit；拒與 no-op＝顯式 rollback。facade 寫入件只收 `&DatabaseTransaction`、不自開交易、不寫稽核、不自取 advisory（`rev5:server/src/model/facade/sys_user.rs` 由 facade 自取鎖、自落稽核＝不帶回）。源碼釘比照 `handler/role.rs` 之 `domain_write_ends_enter_the_domain_first_and_roll_back_explicitly`：外殼 begin 後第一呼叫即內層、內層首句取 advisory（addUser 內層零 `advisory_lock_user`）、失敗腿顯式 rollback（案名實作期定：測試案名、不入名冊）。
  4. **`handler/common.rs` 零新件**。六件之消費：`operator_from_context`（兩域各包私有 `operator_from`）、`json_or_default`（十支寫端與 changePassword）、`db_status_to_wire`（清單 `status`）、`wire_two_value_to_db`（`status`／`userGender` 寫向與篩選）、`blank_to_none`（四可空文字欄空字串＝清空；篩選欄空字串＝不篩）、`tristate`（updateUser 可空欄與 `userName` 出現偵測；`sessionPolicy` 為必填欄、以 `Option<String>` 承載＝R8 第 10 款）。不提升三件：①性別讀向（NULL→null；不得套 `db_status_to_wire` 之二值收斂）與三態寫向＝單一消費者、住 `user.rs` 私有；②`finish_user_write` 帶會話面降級腿（`target: "security.session"`、`degraded = "ttl_read"`／`"denylist_write"`，形同 `handler/auth/logout.rs`），而 `common.rs` 生產區在 `handler::ip_rule` 之 `production_code_emits_no_degraded_field` 射程內、不准發 `degraded` 欄；③操作者名回填直呼 `sys_user::find_names_by_ids`（BL-00113 重評結論：拒寫與故障 log 留各域呼叫點）。
  5. **逐域名冊**：`each_domain_keeps_its_own_log_literals` 加 `user.rs`／`user_center.rs` 兩列；`production_code_emits_no_degraded_field` 只加 `user_center.rs`（錨 `\nfn operator_from(`）——`user.rs` 生產區合法承載上述會話面降級腿而不入，該案 doc「射程另含其後進場之寫端域 handler」句同批補排除判準；為守 `user.rs` 拒寫腿之零 degraded，`each_domain_keeps_its_own_log_literals` 對各域拒寫事件（`refusal_event` 切出之文本）加負向斷言＝不含 `degraded`，一正一反自證（RL-0080）。
  6. **auth 層**：**新建** `auth/no_escalation.rs`（純函式、零 IO、零 `entity::`；R9）；`auth/mod.rs` 宣告之、doc「模組恰兩支＋一型」改三支、`Identity` 增 `sid`（R12）；`auth/enforce.rs` 之 `no_escalation_check` 簽章、函式體與唯一呼叫點不動、只改 doc。
  7. **facade 擴充**（名稱照 plan 期主線定案；皆屬 `facade/mod.rs` 所稱「後一制」＝原樣回 `DbErr`、業務形另分 enum、不落 log）：`sys_user.rs`＝鎖讀 `find_active_by_id_for_update`（`deleted_at IS NULL`、不看 `status`）／`find_deleted_by_id_for_update`（`deleted_at IS NOT NULL`；兩支皆只收 `&DatabaseTransaction`）、`list_active`（四文字欄經 facade 共用件 `ilike_contains`、性別與狀態等值、`id ASC`）／`list_deleted`（`deleted_at DESC, id DESC`）、`insert`／`update_fields`／`set_password`／`set_session_policy`（`updated_*` 成對、`now_ts`）／`soft_delete`（`deleted_*` 成對、不動 `updated_*`）／`restore`（`deleted_*` 成對清空）、預檢 `active_name_taken`（帳號名全等、大小寫敏感＝對齊 `sys_user_user_name_active_uniq`）／`active_email_taken`（`lower()` 比、只比現役）、23505 經 `violated_constraint` 只認 `sys_user_user_name_active_uniq`／`sys_user_user_email_active_uniq`（業務形型名實作期定：facade 內部 enum、不入名冊；形同 `RoleCreateError`）、`advisory_lock_user` 簽章收窄（R7 第 7 款）；`sys_user_role.rs`＝`role_ids_all_of_user`（T）、`role_ids_active_of_user`（A 料源，回（id, 代碼））、`replace_roles_of_user`、`delete_all_of_user`、`roles_by_user_ids`；`sys_token.rs`＝私有底座 `revoke_sids_of_user`＋公開 `revoke_all_of_user`、`revoke_others_of_user` 改委派（R10）；`session_event.rs`＝`EVENT_REVOKED` 與五 reason（R10）；**新建** `sys_pwd_custody.rs`（R11），`facade/mod.rs`「十二支對十二張表」改十三、成員序補之（接 `sys_operation_log` 之後）。
  8. **advisory 使用點與腿⑤**：本刀後 `advisory_lock_user` 生產使用點檔集＝{`handler/auth/login.rs`, `handler/throttle.rs`, `handler/user.rs`, `handler/user_center.rs`}（自 1 檔增為 4 檔），與 `tests/authz_entrypoint_lint.rs` 腿⑤後半 `DOMAIN_WRITE_SIDE_FILES` 八檔交集恆為 ∅：取鎖點一律在 handler 交易擁有者，facade（含新寫入件所在之 `sys_user_role.rs`）不自取帳號鎖（「不下沉」）。該腿只看取得點、不追呼叫鏈——`sys_user_role.rs` 之寫入件於持帳號鎖之交易內被呼叫不違其意旨，列鎖層之新交集另於 R7 第 4 款重核。反向：三支 handler 生產面零 `enter_menu_domain`（腿⑤前半 `DOMAIN_LOCK_CALL_FILES` 恰等、新檔一出現即紅）、零 `reload_enforcer`（腿① `RELOAD_CALL_FILES` 零擴列＝使用者域零授權重載；行為面另以 `casbin_reload_total` 區域 recorder 斷言零增量）。
- **Rationale**: 照 005／006 刀「一域一檔、交易歸 handler、log target 逐域」之形擴兩域，即沿用逐域名冊與既有源碼釘；斷權整腿只有一份；包含規則住 `auth/` 純函式可表驅動測、不入判定面家檔（ADR-00064 決定 7）。
- **Alternatives considered**: 個人中心併入 `user.rs`（`NO_ESCALATION_CALL_FILES` 失圈界，棄）；撤票件入 `common.rs`（degraded 欄入無 degraded 射程即紅，棄）；照 `rev5:007` 由 facade 持交易與稽核（取鎖點下沉，棄）；把廣播搬去 `handler/auth/` 另立共用件以讓 `user.rs` 入無 degraded 名冊（login／logout／refresh 既有內嵌形不動即成第四份，棄）。

## R7 交易、鎖序與 ABBA 重核

- **Decision**:
  1. **合併鎖序**（島 G5 固定序插入 `sys_user` 槽）：advisory（帳號鎖 key＝裸 uid、選單域鎖 key＝`MENU_DOMAIN_LOCK_KEY`，二擇一、絕不同交易兼取）→ 歸檔表列 → `sys_user` 列 → `sys_role` 列（id 升冪）→ `sys_menu` 列 → `casbin_rule`；使用者域之寫入（`sys_user_role` 增刪、`sys_user` 欄、`sys_token` 撤票、`session_event`／`sys_pwd_custody`／`sys_operation_log` 新增）一律在取完全部列鎖之後。歸檔表列與 `sys_user` 列從不同交易出現、相對序無實義。`sys_token` 列不入此序：多列取得者（使用者域撤票、login 單一會話頂替）皆持該 uid 之 advisory、已序列化；refresh／logout 先鎖一列、其後不再等寫端持有之資源（第 4 款）。
  2. **角色列鎖射程**（spec FR-011；G5 末句之兌現）：指派寫端於使用者列鎖之後，對觸及之角色集去重升冪逐一 `sys_role::find_active_by_id_for_update`、鎖內重驗未軟刪——updateUser 帶 `roleIds`＝T∪N、addUser＝N、deleteUser＝T（N＝∅）；batchDeleteUser＝id 去重升冪→**先依序取完全部 advisory**→再依序鎖全部使用者列→整批 T 聯集一次升冪鎖角色列。restoreUser、kickUser、resetUserPassword、updateUserSessionPolicy、不帶 `roleIds` 之 updateUser 不改指派、不鎖角色列。T 之料源列只被持同一 advisory 之交易寫入 ⇒ 鎖內普通讀即穩定。操作者不取鎖：A 為鎖內 DB 現讀（兩管理員互操作若各取「標的鎖→操作者鎖」即 ABBA；A 之陳舊窗與每請求授權判定同級）。鎖持有期間不做 argon2 雜湊生成：生成在交易內、取鎖前（spec FR-012：begin 之後、首個鎖之前）；舊密驗證（verify）屬守門、依 I1 於鎖內重驗（login 第⑤步同形；R11／R12）。
  3. **G5 末句轉非 vacuous 之讀法**：島 G5 首句「同交易 `FOR UPDATE` 鎖標的角色列、鎖內重判前提後才落寫」，末句「使用者角色指派寫端 MUST 同納本鎖序」自本刀生效＝第 2 款；條文零修（ADR-00063 後果）。`rev5:007` research R4 與 `rev5:` 島 I1「角色列（僅比對需要時讀、識別升序）」之不鎖形有一窗：deleteRole 先鎖角色 X、以普通讀計數照刪，不鎖之指派寫端其外鍵檢查（`FOR KEY SHARE`）等其 commit 後放行（軟刪只改非鍵欄）⇒ 指派掛上已軟刪角色。甲案下兩序皆確定：指派先鎖 ⇒ deleteRole 等後計數見新列＝`biz.role.inUse`；deleteRole 先 ⇒ 指派寫端等鎖後重評 `deleted_at IS NULL` 落空＝`biz.user.roleNotFound`。T 亦鎖：子表 DELETE 不鎖父列，只鎖 N 即留「解除未 commit、計數見舊列」之保守誤拒窗；updateRole 停用之 self-role 腿（普通讀 `is_member`）對並發指派操作者本人亦兩序確定。ADR-00044 觸發器②（in-use／self-role 轉生產可達）之複核＝語意與拒因不變、併發下由角色列鎖確定化。
  4. **互等推演**（須「對手持有而寫端會等」與「寫端持有而對手會等」同時非空才可能成環）：

     | 對手 | 對手鎖序 | 共享資源 | 結論 |
     |---|---|---|---|
     | login | advisory(uid)→普通讀 `sys_user`→INSERT 票→撤他鏈 active→UPDATE `session_id` | advisory、該 uid 之票列與使用者列 | 列序與寫端相反，但同以 advisory(uid) 起手 ⇒ 同 uid 永不交錯、異 uid 列集互斥；無環（同 key 為刻意序列化：登入第⑤步看得見已 commit 之停用，反序則撤票迴圈撈得到登入剛插之票） |
     | refresh active 腿 | 鎖呈遞票列→普通讀（含活性重驗）→降級舊列＋插後繼列 | 該票列 | 會等寫端撤票迴圈已鎖之同列（「refresh 永不等停用交易」不成立），但取得後只再普通讀與插新列（`sys_token` 無 FK）；無環 |
     | refresh reuse 腿 | 鎖呈遞 rotated 列→`revoke_family` UPDATE 全鏈 | 該鏈 active 列 | 寫端撤票謂詞只命中 `status = 'active'`、不鎖呈遞之 rotated 列；無環 |
     | logout | 鎖呈遞列→撤之→插事件 | 該票列 | 先鎖一列、其後零等待；無環 |
     | deleteRole 家族、updateRole（含停用）、updateRoleHome、三維授權寫端 | 〔部分先入域〕→`sys_role` 單列或升冪→`casbin_rule`／自列 | `sys_role` 列 | 對手不取帳號鎖、不鎖 `sys_user`；雙方在 `sys_role` 上單列或升冪；無環 |
     | restorePolicy | 歸檔表列→`sys_role` 單列→`casbin_rule` | `sys_role` 列 | 寫端不碰歸檔表；無環 |
     | 選單、IP 規則、系統設定寫端 | 域鎖→`sys_menu`→`casbin_rule`；`sys_ip_rule`；設定列 | 無（選單面對 `sys_role` 只普通讀） | 無環 |

     批次對批次或單筆：advisory 一律升冪且全數先於列鎖 ⇒ 等 advisory 時不持列鎖、角色列皆升冪；`rev5:server/src/handler/user.rs` 之逐 id 交錯形（advisory→列→下一 id）若再逐人鎖角色列，批次持角色 5 等 advisory(u2)、單筆持 advisory(u2) 等角色 5 即成環——不帶回。唯一索引等待只發生於新增活性索引項之語句（addUser 插入、restoreUser 清軟刪、updateUser 改信箱），各交易至多一句、且皆在取完全部列鎖之後；批刪之軟刪只移出索引、不生唯一等待 ⇒ 不成環。
  5. **ADR-00043 決定 8 三失效條件逐條已核未觸發**：①角色寫端連動撤會話——`handler/role.rs`／`handler/menu.rs`／`handler/policy_archive.rs` 與 `model/facade/` 之 `sys_casbin_archive.rs`／`sys_casbin_policy.rs`／`sys_role.rs`／`sys_menu.rs`／`sys_user_role.rs` 生產面 `sys_token::` 與 `advisory_lock_user` 引用皆 0，本刀不加（spec Out of Scope）。②使用者域寫端進選單序列化域（或反向）——指派寫端不入域（腿⑤前半恰等）、域內寫端不取帳號鎖（腿⑤後半交集 ∅）；列鎖層之新交集＝`sys_role` 列，第 4 款已推無回邊（非本條字面、仍記入）。③同 key 跨交易嵌套重入——帳號鎖之對偶由第 7 款防法承載，本刀無此路徑。論證前提①（key 不碰撞）見第 6 款，前提②在 advisory 層續真。本款為推演全文；spec FR-011「於 ADR 重核」之結論（兩前提＋三失效條件已核未觸發）入 ADR-00074 決定二。
  6. **H1 key space**：本刀不新增 advisory 用途、只擴帳號鎖消費者（key 仍＝裸 uid）。兩鎖皆單 bigint 形（`objsubid = 1`），碰撞唯一條件＝某 uid 恰等 `MENU_DOMAIN_LOCK_KEY`（8243124669107236469）；`sys_user.id` 為 bigserial、seed 序列值 3、測試合成號段起於 `SYNTHETIC_UID_FLOOR`（9300000000）。現況無「uid < 域鎖 key」之機器斷言，本刀不新增、記已知態；翻案觸發＝出現以外部指定 id 寫入 `sys_user` 之生產路徑。
  7. **READ COMMITTED、40P01、重入**：生產面零隔離級別設定、零 `lock_timeout` ⇒ 每句各取快照、`FOR UPDATE` 等鎖後依最新版本重評 WHERE（本節「鎖內重驗」皆依此）；交易內兩次普通讀可見不同結果，判定一律取鎖內那一次。死鎖由 PG 回 40P01、各域 `db_failure` 翻 `5000`、零重試；第 4 款推得生產路徑無環 ⇒ 40P01 真出現即缺陷。advisory xact 鎖同交易可重入（批次已去重、非設計依賴）；另開交易或以裸連線再取同 key＝應用層自等待、PG 偵測不到。防法：`advisory_lock_user` 收窄為只收 `&DatabaseTransaction`（比照 `enter_menu_domain`）＋`compile_fail` doctest（以 `&sea_orm::DatabaseConnection` 呼叫 MUST 編不過、正面孿生同路徑同型名 MUST 編得過；login 與既有測試皆傳交易、零改）；內層 `<op>_in_txn` 不收 `AppState`（型別上拿不到池連線）；`finish_user_write` 先 commit 再以 `state.db` 讀 TTL 與寫失效名單；unlockLogin 帳號維之稽核改 `sys_operation_log::write_in_txn`。
  8. **批次規模**：advisory 佔 PG 共享鎖表（compose 只設時區、`max_locks_per_transaction` 取預設）；不設批量上界（UI 批選上限一頁＝`PAGE_MAX_SIZE` 100），API 超大批最壞＝鎖表耗盡 ⇒ `5000` 整批回滾，記已知態。
  9. **島 I1 改寫要點（交 U0 親決）**：`rev5:` 島 I1 三處不可照抄——「與登入／換發同源」（換發不取 advisory，`rev5:` as-built 亦然）、「角色列（僅比對需要時讀、識別升序）」（改 `FOR UPDATE` 鎖讀＋鎖內重驗、T∪N）、「批次刪除依識別去重升序逐一取鎖」（改第 2 款之三段）。
- **Rationale**: 照 G5 字面即甲案；現行一切 `sys_role` 列鎖者皆單列或升冪、且無任何路徑先鎖 `sys_role` 再取帳號鎖或使用者列 ⇒ 加鎖不引入回邊，代價只是同角色上之指派與角色寫端互等。撤票迴圈之正確性不依賴換發取鎖（R10），換發鎖序不動。
- **Alternatives considered**: 不鎖角色列（`rev5:` 形；留幽靈掛載窗、與 G5 首句有落差，棄）；只鎖 N（留誤拒窗，棄）；`FOR SHARE` 鎖讀（不合 G5 字面，棄）；逐 id 交錯取鎖（對甲案回跑即成環，棄）；先鎖角色列再取帳號鎖（與甲案 ABBA，棄）；換發先取 advisory（同帳號換發串行，棄）；操作者亦取 advisory（互操作 ABBA，棄）；SERIALIZABLE（全面加重試，棄）。

## R8 寫端固定序、no-op 與空字串、批刪與復原（ADR⑦）

標註〔ADR-00080：〈款主題〉〕＝屬 ADR-00080（spec 序⑦，ADR-00047 續行）之款；未標者承載於 spec FR 與島 I 條文（ADR-00074）。

- **Decision**:
  1. **通則**：操作者上下文 → body 收斂 → 外殼 begin → ①活性標的鎖讀 → ②seed 保護 → ③本人規則 → ④包含規則 → ⑤業務守門（內部次序依 spec FR-010 表之列舉）；任一拒＝顯式 rollback、零變更、零稽核；多重違規取先序腿。
  2. **FR-010 逐格碼位**（`handler/user.rs` 各支內層 `<op>_in_txn`；私有件名實作期可調：純私有、不跨檔、不入名冊）：

     | 寫端 | ① | ② | ③ | ④ | ⑤ | 空格理由與釘法 |
     |---|---|---|---|---|---|---|
     | addUser | 無 | 不適用 | 不適用 | `target=None`：T＝∅、N＝`roleIds` | 帳號名形制（`userNameInvalid`）→`active_name_taken`（`userNameExists`）→信箱非空時形制（`userEmailInvalid`）→`active_email_taken`（`userEmailExists`）→角色 id（`roleNotFound`）→密碼政策→冷卻（結構性恆過：新 id 從未有經手列、不呼 `cooldown_remaining_secs`；INSERT 後同交易 `touch`）〔⑤ 內先格式後唯一、④ 先於 ⑤＝spec FR-010；與 `rev5:007` 契約 §3 不同＝R5 #49〕 | ①無既有標的、同名並發由現役唯一索引 23505 兜底（釘：內層零 `advisory_lock_user`）；②③新帳號不可能是 seed 或本人；冷卻格恆過（釘：addUser 後同操作者於冷卻內 resetUserPassword 得 `pwdSetTooFrequent`） |
     | updateUser | `lock_active_user` | 標的＝`SUPER_USER_ID`：`status` 解析為非啟用＝`superCannotDisable`；`roleIds` 出現而不含 R_SUPER 活性 id（`sys_role::active_ids_by_codes` 以 `SUPER_ROLE_CODE` 查、查無＝fail-closed）＝`seededProtected` | 本人而 `status` 或 `roleIds` 出現（值不比對）＝`cannotEditSelfRoleOrStatus` | T⊆A∧N⊆A | 全欄缺席＝早退 no-op（`userName` 出現〔含 null〕不屬缺席）→`userName` 出現＝`userNameImmutable`→信箱（形制；`lower()` 異於現值時預檢唯一、排除自身）→角色 id（T∪N 鎖讀、查無＝`roleNotFound`）→值 diff no-op | —— |
     | deleteUser | 同上 | `SEED_USER_IDS`＝`seededProtected` | `cannotDeleteSelf` | T⊆A（N＝∅） | 無 | ⑤：軟刪無業務前提（釘：持指派與多會話之自建帳號照刪成功） |
     | batchDeleteUser | 全部 advisory→全部列 | 任一 seed 整批拒 | 含本人整批拒 | 逐筆 T⊆A | 空陣列提前 no-op | —— |
     | restoreUser | `lock_deleted_user`（現役或查無＝`notFound`） | 不可達 | 不可達 | T⊆A（生產 T≡∅） | 同帳號名現役（`userNameExists`）→同信箱現役（`userEmailExists`） | ②seed 刪不掉 ⇒ 回收桶無 seed；③本人刪不掉自己，被他人刪者指派已硬刪、每請求現查角色為空 ⇒ 連授權層都過不了（釘：兩刪除拒案＋「已刪帳號殘留之存取權杖打政策端點得 `5003`」） |
     | kickUser | `lock_active_user`（停用照鎖） | 空 | `cannotKickSelf` | T⊆A | 無 | ②：踢除零永久傷害、超管遭盜用時須能由另一持 R_SUPER 者踢下線（釘：第二個持 R_SUPER 之自建帳號踢 Super 成功）；⑤：零 active 亦成功、照落稽核 |
     | resetUserPassword | 同上 | 空 | `cannotResetSelfPassword` | T⊆A | 密碼政策→冷卻（R11） | ②：重設可逆、為 seed 帳號之救援路徑（釘：Super 重設 seed Admin 成功、測後快照守衛還原） |
     | updateUserSessionPolicy | 同上 | 空 | 空 | T⊆A（生產恆過＝封死端點） | 三值收斂（`sessionPolicyInvalid`）→值 diff no-op | ②：無永久傷害；③：本人可改（spec FR-017）（釘：本人改本人成功） |

  3. **no-op 判準**〔ADR-00080：no-op〕：判定位於⑤、不早於①～④（與 `rev5:007` contracts §4 之守門序 notFound→seed→self→T⊆A→唯一／格式→值 diff 同序）：全欄缺席→早退；否則值域歸一（可空文字欄空字串＝空值、`status`／`userGender` 值域外＝缺席、角色集去重成集合）後逐欄比現值、角色集以集合比 → 全等＝no-op＝零寫入、零稽核、零撤票、`updated_*` 不動、rollback 後回 `0000`。有變更＝只寫變更欄＋`updated_*` 成對 bump（角色集變更亦 bump）＋稽核一列 `update`；角色面有無變更以 `replace_roles_of_user` 回值為單一真源（同集提交零寫入回 false）。逐域差異：ADR-00047 決定 3 之角色、選單域提前 no-op 在 begin 之前（不存在之 `id` 亦 `0000`）、同值照寫照稽核；使用者域先鎖標的再判——全缺席請求對已刪或不存在標的得 `notFound`（spec FR-009／FR-016）、對無權標的得 `5003`，同值零寫零稽核（Q15）。
  4. **空字串＝清空**〔ADR-00080：空字串〕：暱稱、手機、信箱、記事之空字串，新增與更新同形落 NULL（`blank_to_none` 套內層）；信箱空字串或 null 不判形制與唯一。性別：null＝清空、空字串與值域外＝缺席（不動；`rev5:` 形）；狀態：null 與值域外＝缺席。ADR-00047 決定 2 之逐域明文與決定 5 之射程以續行款擴入使用者域、不改其本文。
  5. **帳號名不可變**〔ADR-00080：不可變欄〕：`userName` 以 `tristate` 承載、出現即 `userNameImmutable`，位於⑤首（對已刪標的仍先 `notFound`），與角色域 `codeImmutable` 同形。
  6. **角色集全量替換**〔ADR-00080：角色集〕：缺席＝不動（不鎖、不替換）；陣列＝寫後角色集恰等其去重集；含不存在或已軟刪 id＝整筆 `roleNotFound`（角色是指派主體、非候選集過濾，與 006 刀授權彈窗之略過不同形）；空陣列＝全撤；差集以硬刪＋新增落地、交集列不動。N 構造不出時④只判 T⊆A、`roleNotFound` 於⑤原位發。
  7. **批刪**：`ids` 缺席或壞形＝空陣列→去重升冪→空＝提前 `0000`（零 begin、零稽核）→整批①（任一查無＝`notFound`）→整批②→整批③→角色列聯集鎖→逐筆④→逐筆寫入（軟刪→硬刪指派→撤票＋`user_deleted` 事件→稽核 `delete` 每標的一列）→`finish_user_write` 一次廣播；拒因純 key 不指筆。多重違規取「先序相位」——與 `rev5:007` 逐 id 交錯（回首個違規 id 之先序腿）在「多 id 且違規類別不同」時可回不同鍵；屬 R7 鎖序之連帶、拒因集合不變、畫面零差；承載＝ADR-00080 決定 8 表、R5 #47。
  8. **復原**：鎖已刪列→④→鎖內兩腿重驗（帳號名；信箱非 NULL 時 `lower()` 比）→`deleted_*` 成對清空（`updated_*` 不動，同 `sys_ip_rule` 復原語句形）→稽核 `restore`；狀態保留原值、零回灌、零撤票。預檢至寫入間之撞列（addUser 不取 advisory、兩支同名已刪帳號各持不同帳號鎖）由現役唯一索引 23505 收窄為同二鍵。本款即 ADR-00044 觸發器①之答案（軟刪同交易硬刪指派 ⇒ in-use 保守口徑不必改；spec FR-015）。
  9. **已刪標的、本人五不、body 收斂**：五支之①皆經活性版鎖讀（只有 restoreUser 經已刪版；批刪含已刪 id＝整批 `notFound`）。本人五不＝刪除、停用與改自身指派、踢除、以管理頁重設各配純 key（表③欄）；本人可改非角色欄與會話政策。寫端請求型 `impl FromRequest` 委派 `json_or_default`（端點標籤＝端點名）收斂成 `Default`：`id`＝0 ⇒ `notFound`、`ids` 空 ⇒ 提前 no-op、addUser 全預設 ⇒ `userNameInvalid`；中介層不讀 body、零新錯誤碼（spec FR-009）；清單 query 壞形整串收斂（形同 `RoleListQuery`）。
  10. **會話政策寫端**〔ADR-00080：會話政策〕：`sessionPolicy` 為必填欄、以 `Option<String>` 承載（缺席與 null 同判）：缺席、null、空字串、值域外（`SessionPolicy::parse` 大小寫敏感、不 trim）一律 `sessionPolicyInvalid`（ADR-00047 決定 1「必填欄亦以寬鬆形承載、缺席或 null 由 handler 判 `2222`」；`rev5:007` contracts §10 同形）；判於⑤（①～④ 之後；body 缺席〔`id` 0〕先於①得 `notFound`）；同值 no-op（值 diff、無全缺席早退）；改 `single` 不即時踢；零撤票。spec Edge Cases「同值 no-op」句與 FR-018 已於 plan 期修補為此形（R25；R5 #51）。
  11. **並行編輯已知態**〔ADR-00080：並行編輯〕：抽屜之狀態與角色只在改動時才送、會話政策另打其端點（R18）⇒ 舊值不把他人剛停用之帳號啟用回來、不覆蓋他人指派；其餘恆送欄（暱稱、性別、手機、信箱、記事）後送出者為準（無版本欄、零 DDL），`rev5:` HEAD 同形。
- **Rationale**: ①置首使拒因呈現穩定（已刪即 `notFound`、不因帶了哪些欄而變）；no-op 置⑤與 `rev5:007` 契約同序、且「同值不寫不記」不繞過任何守門；空字串清空消除同欄兩種空（ADR-00047 決定 2 之逐域明文義務）。
- **Alternatives considered**: 全缺席早退置 begin 前（角色域形；違 FR-009／FR-016，棄）；更新路徑空字串不摺疊（Q16 已翻，棄）；性別空字串＝清空（非文字欄，棄）；同值照寫照稽核（Q15 已否，棄）；會話政策缺席＝no-op（與 ADR-00047 決定 1 及 rev5 HEAD 不合，棄；spec 已修補同形）。

## R9 包含規則（ADR②）

- **Decision**:
  1. **純函式**（ADR-00075）：`auth/no_escalation.rs` 持 `ActorScope { All, Roles(BTreeSet<i64>) }`、`actor_scope_of`（純函式：吃 A 料源之（id, 代碼）、任一代碼＝`sys_role::SUPER_ROLE_CODE` 即 `All`，R_SUPER 判準沿 006 刀封死豁免之同一常數）、`assert_no_escalation(scope, t, n) -> Result<(), AppError>`（`All` 恆過；否則 T⊆A∧N⊆A，違者 `PermissionDenied`＝`5003`＋`system.forbidden`、零 payload）。碼內名稱沿 002 刀掛點用詞 no_escalation、文件語「包含規則」。比對單位＝角色 id（`rev5:` 以代碼）：id 即 wire、鎖讀與指派表之單位，代碼於軟刪後可被新角色重用而 id 不重用。
  2. **handler 包裝** `guard_no_escalation(txn, operator_uid, target: Option<i64>, next: Option<&BTreeSet<i64>>, endpoint)`：鎖內讀 A（`role_ids_active_of_user`）→`All` 即回（不讀 T：省持鎖期間一次往返、免「結果用不到之查詢」之抖動翻 `5000`）→讀 T（`target` None＝∅）→N＝`next` 或 T→判定→違者記 warn 一則後回 `5003`；查庫故障一律 `5000`、不吞成空集。
  3. **A／T／N 口徑**：A＝操作者指派之角色濾軟刪與 `status≠1`（DB 現讀、不鎖；停用角色不給實權）、持 R_SUPER＝全集。T＝標的全部指派列所指角色、**不濾 `status`**、濾已軟刪（已軟刪角色之指派列在 in-use 腿＋R7 角色列鎖下生產不可生成，濾之只使直改庫殘列不致標的永久不可治理；`rev5:` 同口徑）。N＝寫後角色集：帶 `roleIds` 且全數在活性域＝其去重集；缺席或含界外 id＝N＝T（`roleNotFound` 於⑤原位發）——「活性域」以角色列鎖讀結果判：指派寫端於①之後、②之前先對 T∪N 去重升序鎖讀（R7 第 2 款；addUser 只鎖 N），④ 取鎖內結果構 N、⑤ 以同一結果判存在（鎖內構 N、不信 pre-read）；刪除＝∅（與 N＝T 判定等價）。
  4. **9 消費點**（判定位次＝固定序第④，seed 保護與本人規則先判）：

     | 消費點 | T | N | 生產可達性 |
     |---|---|---|---|
     | addUser | ∅ | `roleIds` | 非恆過（「新開超管帳號」為最直接之提權路徑） |
     | updateUser | 現指派 | `roleIds` 或 T | 可達 |
     | deleteUser／batchDeleteUser（逐筆） | 現指派 | ∅ | 可達 |
     | restoreUser | 生產恆 ∅ | ∅ | 恆過、結構齊一而掛（負向案以合成「已刪列仍掛指派」態釘） |
     | kickUser／resetUserPassword | 現指派 | T | 可達 |
     | updateUserSessionPolicy | 現指派 | T | 生產恆過（列 68 屬封死集；負向案以測內資料列授權繞過封死而釘） |
     | unlockLogin 帳號維 | 帳號名解析之活性使用者之指派；查無或已刪＝∅ | T | 可達；查無＝恆過、照回 `0000` 不洩存在性 |

     機器守＝`tests/authz_entrypoint_lint.rs` 增 `NO_ESCALATION_CALL_FILES`（`guard_no_escalation` 裸 token〔呼叫、指標、路徑三形聯集＝RL-0026〕之生產出現檔集恰等 [`handler/throttle.rs`, `handler/user.rs`]，路徑字典序＝`verdict` 斷言 `roster.is_sorted()`）＋一正一反自證（RL-0080）＋每消費點拆掉呼叫即轉紅之行為案（spec FR-025）。
  5. **unlockLogin 帳號維交易化**：`resolve_unlock_target`→`operator_from`→帳號維：begin→`sys_user::find_by_user_name`（鎖前普通讀）→查得則 `advisory_lock_user(標的)`＋`guard_no_escalation(Some)`、查無則 `guard_no_escalation(None)`→`sys_operation_log::write_in_txn`（`unlock`）→commit→`cache::set_ex` 寫標記；來源維照舊（裸連線稽核→標記、不套規則）。「稽核先於標記」不變、拒＝零稽核零標記；`STEP_ANCHORS` 源碼次序釘同批改。已知態：帳號名→uid 之解析必然先於取鎖，其間若帳號被刪而同名新帳號被建立，判定取舊 uid（T＝∅）而標記落帳號名鍵——影響限於解除該名之登入節流、不改授權與資料（`rev5:` 以「帳號名不可變」推為穩定、未計刪除重建）。`advisory_lock_user` doc「MUST 在 caller 已開的 txn 裡當首個動作呼叫」同批改為「早於任何列鎖（鎖前普通讀容許）」（R22）。
  6. **warn 日誌**：target `security.user`、欄＝`actor`（操作者 uid）、`target`（`Option<i64>` 以 `?` 呈）、`endpoint`（端點名）；三欄外一律不記、角色差集不進日誌亦不上 wire（403 不作角色枚舉 oracle）；不新增觀測序列。unlockLogin 帳號維之拒絕亦掛 `security.user`（判定與日誌單一真相源、以 `endpoint` 欄區分；`security.throttle` 檢索面不含此則＝已知態）。
  7. **射程只限使用者域與 unlockLogin 帳號維**（Q7）：角色域、IP 域、授權回收桶復原續 ADR-00068 款 9 已知態（款 9 之使用者域與 unlockLogin 半由 ADR-00081 解除）。不掛理由：角色域寫端之標的是角色、無「標的持有之角色集」可比，硬套須另立角色分級（spec Out of Scope）；授權回收桶兩支屬封死集、只持 R_SUPER 者打得到 ⇒ 掛之恆過。
  8. **ADR-00064 觸發器複核**（入 ADR-00075）：首條（委派治理需求 ⇒ 評估填入 ADR-00014 決定 5 掛點本體）＝觸發；結論＝本體不填入掛點（掛點無 body、未取列鎖，填入即需中介層解 body 或 handler 重做路徑判定＝判定面第二入口），實際落點＝handler 鎖內純函式、掛點續恆放行；「整批拒」由批刪整批 rollback 承載、復原路徑依第 7 款不掛；島 G6 不動（封死約束角色維、包含規則約束操作者維，正交）。次條（本體落地或島 I 入憲 ⇒ 復核位次與拒因不互吞、正交分工、復原是否同掛）＝觸發；結論＝包含規則只住使用者域與 unlockLogin，撤銷拒（`biz.role.protectedRevoke`）與封死拒（`biz.role.protectedGrant`、`biz.policy.notRestorable`）只住角色域三維寫端與授權回收桶 ⇒ 無共居端點、結構上不互吞；使用者域④之 `5003` 與中介層 casbin 拒同碼同鍵、分層先後固定；授權回收桶復原不掛。
  9. **BL-00048 兌現連動面四處**：①`auth/enforce.rs` 模組註「no-escalation 本體、`REASON_ADMIN_KICK` 第三向與 `Identity.sid` 第三欄屬後刀域、不帶」與 `no_escalation_check` 條目之「本體刀接手只填函式體」兩句改現在式（掛點續恆放行＝路徑級上限位；本體住 `auth/no_escalation.rs`、handler 鎖內呼叫）；②`no_escalation_check` doc「本體刀接手時簽章與呼叫端都不必動」改為射程分工之說明，同檔測試 doc「本體刀前空殼」同批改；`enforce_role_path_method` 內掛點唯一呼叫點碼註「本刀恆 Ok；本體刀接手後 deny 走同一出口」與掛點拒絕計數測試 doc「本體刀接手後看不見真實拒絕量」兩句同批改現在式（「本體刀」入 R22 errata 種子）；③ADR-00014 後果段「本體刀只填掛點函式體、零簽章變更、零呼叫端改動」（body 不可變）由 ADR-00075 背景明記不兌現之實況，BL-00048 之對沖職責移交、收刀刪列；④`specs/002-system-settings/spec.md` FR-013（凍結）之讀法入 ADR-00075：「MUST 留空 no-escalation 掛點」與「003 接真 session 時判定進入點介面不變」續真——掛點存續且恆放行、`enforce_role_path_method` 簽章不動、包含規則不經該掛點。活書 08 之「空掛點」句同批改（R22）。
- **Rationale**: ADR-00064 決定 7 已定本體歸使用者域、掛點不動；只有 handler 鎖內同時拿得到 N 與鎖定後之 T。純函式＋單一包裝使 9 消費點只有一份判定；`All` 短路使 seed 預設態（寫端只屬 R_SUPER）負載不增。
- **Alternatives considered**: unlockLogin 帳號維鎖內重解析帳號名（uid 異動時已持之 advisory 非新 uid 之鎖、交易內不可釋放重取＝須改拒或重試，射程增而得益限同名重建之毫秒窗，棄）；填入 `no_escalation_check`（無 body、無列鎖，棄）；以角色代碼比對（代碼可重用，棄）；T 濾停用（放寬，棄）；A 不給 R_SUPER 全集（seed 之 Super 只持 R_SUPER、編輯持 R_ADMIN 者即誤擋，棄）；射程擴至角色域與授權回收桶（Q7 已否，棄）；拒時攜差集或新增計數序列（spec FR-021 不做，棄）。

## R10 斷權兩層與三向分派

- **Decision**:
  1. **兩層**：第一層＝同交易撤票（PG 權威：票→revoked＋逐 sid 會話事件，與業務寫、稽核同進退）＋commit 後盡力寫失效名單（加速層）；第二層＝換發於票列鎖後之帳號活性重驗。不加每請求判定（島 I2；spec FR-029）：`enforce_mw` 與 getUserInfo 續不判 `status`／`deleted_at`，`handler/auth/user_info.rs` handler doc 之「刻意不看 `status` 與 `deleted_at`」與「要先立 ADR 才能落」兩句與島 I2 同向、續真；BL-00065 題 b 以島 I2「MUST NOT 新增每請求活性判定」入條文收。
  2. **撤票原語**：`sys_token` 私有底座 `revoke_sids_of_user(conn, uid, keep: Option<&str>)`＝既有 `revoke_others_of_user` 本體上提（SELECT 帶頭迴圈、跨輪去重保首見序、SELECT 與 UPDATE 過濾條件逐條相同、`created_by = uid` 圈定、只碰 active、rotated 不動）；`revoke_others_of_user`＝`Some(keep_sid)`、新公開 `revoke_all_of_user`＝`None`；禁單句 UPDATE。`revoke_sessions_in_txn(txn, target_uid, keep_sid: Option<&str>, reason, operator) -> Result<Vec<String>, AppError>`：keep 缺席呼 `sys_token::revoke_all_of_user`、給定呼 `sys_token::revoke_others_of_user`（二者皆委派私有底座）→逐 sid 落事件（`event_type` `revoked`、`user_id`＝標的、`created_by`＝操作者、`source_ip`＝操作者 `real_ip`）→回 sid 清單。
  3. **並發三序**（停用撤票對並發換發；READ COMMITTED）：①換發先鎖 T1、rotate 出 T2 後 commit：寫端首輪 UPDATE 等 T1、重評後略過，次輪 SELECT 撈到 T2 撤之；②寫端先撤 T1：換發等列鎖、讀得 revoked→revoked 腿；③換發已先 commit：首輪即撈到 T2。三序皆不漏；單句 UPDATE 在序①漏撤 T2（該句快照不含後插之列）。login 與寫端同 advisory ⇒ 不交錯。
  4. **事件與失效名單**：`session_event` 經 `vocabulary!` 增 `EVENT_REVOKED`＝`revoked` 與 `REASON_USER_DISABLED`／`REASON_USER_DELETED`／`REASON_PASSWORD_RESET`／`REASON_PASSWORD_CHANGED`／`REASON_ADMIN_KICK`（值集案、欄寬案同批）；`cache` 增 `REASON_ADMIN_KICK`＝`admin_kick`（與 `session_event` 同字面常數分屬兩命名空間、不互相 `use`）。`finish_user_write(state, txn, revoked_sids, reason, endpoint)`：commit（失敗＝`5000`、零失效名單）→sid 空或快取缺席即返→交易外 `jwt::ttl_from_settings(&state.db)`（失敗＝warn `target: "security.session"`、`degraded = "ttl_read"`、整段跳過）→逐 sid `cache::denylist_set(sid, reason, refresh_secs)`（TTL＝換發票全壽命；寫失敗＝warn `degraded = "denylist_write"`、續下一枚）；權威在 PG、失敗不回錯；零授權重載（`rev5:` 之 `reload` 參數不帶）。
  5. **五路 reason 對照**：

     | 路徑 | 撤票射程 | 會話事件 | 失效名單 | 被撤者下一請求 | 再登入 | 稽核 |
     |---|---|---|---|---|---|---|
     | 停用（`status` 由啟用轉非啟用；回復啟用與同值零撤） | 全部 active | `revoked`／`user_disabled` | `revoked` | `8888` | `1000` | `update` |
     | 刪除（單筆、批次） | 全部 active | `revoked`／`user_deleted` | `revoked` | `8888` | `1000` | `delete` |
     | 重設 | 全部 active | `revoked`／`password_reset` | `revoked` | `8888` | 新密成功 | `reset_password` |
     | 自改 | 本人其他 active（keep＝`Identity.sid`） | `revoked`／`password_changed` | `revoked` | 他裝置 `8888`、當前保留 | 新密成功 | `change_password` |
     | 踢除 | 全部 active（rotated 不動；零 active 亦成功） | `revoked`／`admin_kick` | `admin_kick` | `7777`＋`auth.session.kickedByAdmin` | 成功 | `kick` |
     | （既有）頂替 | 同帳號他鏈 active | `kicked`／`single_session` | `kicked` | `7777`＋`auth.session.kicked`（不變） | —— | 登入稽核 |

     kickUser 不動 `sys_user` 任何欄、回 `{revoked: n}`（撤下之 sid 數）；會話政策改 `single` 不撤票。
  6. **三向分派**：`enforce_mw` denylist 第 1 級與 `handler/auth/refresh.rs` revoked 腿同改：`kicked`→`ModalLogout`（`7777`＋`auth.session.kicked`）、`admin_kick`→`ModalLogoutByAdmin`（`7777`＋`auth.session.kickedByAdmin`）、其餘→`Logout`（`8888`；萬用臂保守側不變）。redis 答不出時 reason 不可得、同落 `8888`（降級同碼）。已知窄窗：踢除 commit 至失效名單寫入之間，被踢者換發先讀到 nil 即得 `8888` 而非踢除提示——只差呈現。
  7. **換發活性重驗**：落點＝refresh active 腿「idle 判定之後、DB 現查角色與簽發之前」（`rev5:` 同位）；`sys_user::find_by_id(&txn, claims.uid)` 普通讀、不加 `FOR UPDATE`、不取 advisory；`status == Some(1) && deleted_at.is_none()` 才放行、查無列＝不活；不活＝rollback＋`8888`（本腿唯一拒絕出口、零寫入）。不加列鎖（在此鎖使用者列即「票列→使用者列」插隊、與寫端 ABBA）；普通讀足夠之理由是落點（票列鎖後、與 rotate 同進退）而非快照一致。定位如實：迴圈原語已封並發漏撤，本腿實際承載＝查無帳號列、繞過寫端之停用（直改庫）與日後不撤票之斷權路徑；`rev5:` 碼註以「票列因競態而漏撤」稱其非有不可，該理由在迴圈原語下不成立、不援用。模組 doc「★兩件不搬」句改現在式。
  8. **殘窗（已知態，入島 I2 說明與 ADR-00074）**：①grace 腿——rotated 列於 `GRACE_TTL_SECS`（30 秒）內重放且快取命中即回既發之對、不查 DB；其 refresh 半下次換發撞 revoked 列得 `8888`，access 半受失效名單攔截。②失效名單寫失敗（或 commit 至寫入之間）時，被撤者未過期之 access 票續通至多 `access_secs`；換發由兩層擋下（spec US2 場景 6）。
  9. **fixture 改造**（rev6 測試現數）：落點在 idle 之後 ⇒ `handler/auth/refresh.rs` 測試 20 案中走到簽發者 10 案、合成票主 11 個：`refresh_active_rotates_to_new_pair_marks_rows_and_reads_ttl_current_value`、`refresh_second_presentation_within_grace_returns_identical_pair`、`refresh_grace_miss_triggers_reuse_revokes_family_audits_and_denylists`、`refresh_concurrent_same_token_one_rotates_one_graces_no_reuse_no_5000`、`refresh_grace_written_before_commit_while_row_lock_still_held`、`refresh_grace_read_error_fails_secure_into_reuse`、`refresh_activity_within_idle_window_rotates_with_zero_idle_side_effects`、`refresh_idle_threshold_follows_current_idle_timeout_setting`（兩票主）、`refresh_last_activity_read_error_fails_open_and_still_rotates`、`refresh_behind_proxy_serves_overflowing_chain_and_audits_trust_anchor_source`；`handler/auth/logout.rs` 1 案＝`logout_rotated_ticket_is_noop_and_active_successor_logout_revokes_only_that_row`。其餘 10 案（驗章失敗、TTL 缺失、body 壞形、idle 拒、idle 標記寫失敗、revoked 三形、純函式與源碼形各一）零改。改法＝以既有合成 uid 植顯式 id 之活性 `sys_user` 列（不觸序列；`password` 植不可驗之佔位 PHC），由新使用者列守衛（R15）清除；另補停用、已軟刪、查無列三形拒案（spec SC-005）與落點源序釘（票列 `FOR UPDATE` 之後、`find_by_id(&txn`、早於 `sign_pair`）。落點若在 TTL 讀取之前，TTL 缺失與 idle 拒兩案亦須改種（＝12 案）且其 `5000`／idle 拒被活性拒搶先——spec FR-028「10 案」即對應本落點。
  10. **ADR-00037 觸發器反向確認**：首條＝「登入以外再出現『以來源位址做安全判定』的匿名端點（如改密、註冊真實作）」；changePassword 為 `Protection::Authed`（非匿名）、節流維度＝使用者 id（非來源位址），其餘寫端皆 `Policy` ⇒ 未觸發、逾限拒絕仍只限登入。BL-00043 反向確認：改密與踢除不新增存取軌跡寫入面（`sys_access_log` 生產面零 facade、零寫入點，本刀不增）。
  11. **ADR-00043 決定 8 失效條件①之核**：一切撤票出自持帳號鎖之使用者域寫端與 changePassword；角色、選單、回收桶生產面 `sys_token::` 引用維持 0，角色停用與刪除由每請求授權讀端即時濾除、不撤會話 ⇒ 未觸發（R7 第 5 款）。
- **Rationale**: 權威優先（PG 先落定、快取只加速）沿島 C；迴圈原語是封 READ COMMITTED 漏撤窗之主力、與換發是否取鎖無關，換發鎖序不動；活性重驗與 `rev5:` 同位且 fixture 改造面最小；三向分派使「管理員踢除」與「他處頂替」兩種體驗分立（GR2）。
- **Alternatives considered**: 單句 UPDATE 撤全部（序①漏撤，棄）；以空字串 keep 借用 `revoke_others_of_user`（魔術字面承載語意，棄）；活性重驗加 `FOR UPDATE` 或先取 advisory（ABBA／換發串行，棄）；不加活性重驗（Q12 已否，棄）；落點置 TTL 讀取前（搶先既有拒因，棄）；`admin_kick` 併入 `kicked`（違島 C 不互換，棄）；失效名單 TTL 取 `access_secs`（換發窗內記號已消失，棄）；每請求活性判定（違島 I2，棄）。

## R11 密碼面：政策單點、冷卻、改密節流、明細通道、壞值告警（ADR③⑤⑥）

- **Decision**:
  1. **政策單點**（`model/password.rs`；島 I5；addUser 初始密碼、resetUserPassword、changePassword 三入口共用、登入路徑零呼叫）：
     - `PasswordPolicy` 七欄（`min_length`／`max_length`：`usize`；`require_digit`／`require_lowercase`／`require_uppercase`／`require_special`／`forbid_username`：`bool`），`Default`＝m0002 seed 值（8／64／五旗標 off）。`password_change_min_interval` 不入本型、不下發（冷卻屬端點固有規則）。
     - `load_password_policy(conn)`：一次 `system_settings::find_all`（單快照、防跨鍵 torn read）篩七鍵逐鍵解析；number 二鍵以 `validation::range_of` 驗 registry 界（現值 min [1,128]、max [1,256]、不另抄）；enum 五鍵只認 `on`／`off`。缺列、不可解析、越界或值域外＝**該鍵**退 seed 預設＋warn 一則（target `security.password`、欄 `setting_key`；不計數）。查庫 `Err` 上拋 `5000`：設密入口在交易內呼叫、PG 錯誤已使交易失效，不得如 `throttle::load_settings` 於外層連線吞錯。每次消費現讀、不快取。
     - `validate_against_policy(pw, user_name, &policy) -> Vec<&'static str>`：違規碼八枚 `VIOLATION_*`＝`minLength`／`maxLength`／`maxBytes`／`requireDigit`／`requireLowercase`／`requireUppercase`／`requireSpecial`／`forbidUsername`，依此序**一次收集全部**。字元數＝`chars().count()`、位元組＝`len()`（雙約束）；三類字元取 ASCII 類；special＝任一非 ASCII 英數字元；`forbid_username` 開啟時與帳號名**不分大小寫相等**即違規、子串不算（m0002 該鍵說明字面「禁止密碼與帳號相同」）。帳號名：addUser 取請求中已過形制者、其餘兩入口取鎖內標的列。min＞max 時任一密碼必命中 `minLength` 或 `maxLength`＝自然全拒、不另設違規碼。
     - `MAX_BYTES` 直引 `crate::throttle::LOGIN_PASSWORD_MAX_BYTES`（512）＝與登入形制閘同一常數（設得進必登得進）；該常數 doc「取密碼政策上界的兩倍當餘裕、不插手密碼政策」改述為兩面共用之唯一字面。登入路徑零政策（FR-032）以源碼掃描案釘：`handler/auth/login.rs` 生產面 `load_password_policy(`／`validate_against_policy(` 零命中（三形聯集＝RL-0026；變異自證）。
     - 雜湊：`hash(plain)`＝argon2 0.6 API——`getrandom::fill` 取 16 bytes 裸 salt、`Argon2::default().hash_password_with_salt(…)`、`to_string()` 即 PHC；參數 m=19456,t=2,p=1＝seed PHC 與 `dummy_phc` 同（現行模組 doc 已載此守則；Cargo.lock argon2 0.6.0、getrandom 0.4.3，零新依賴）；失敗＝`5000`、錯誤路徑不攜內容。`NewPassword::prepare(plain)`＝唯一構造（明文＋PHC 成對、刻意零 `Debug`），**handler 於 `begin()` 之後、首個鎖之前呼叫**（交易內、不持鎖＝spec FR-012）、`*_in_txn` 與 facade 只收 `NewPassword`。島 I5 釐清（`rev5:ADR 0068`；由 ADR① 併入條文）：生成不得持列鎖、驗證（改密舊密比對、login 第⑤步）依島 I1 鎖內重驗。機器守＝源碼掃描：`password::hash(`／`NewPassword::prepare(` 生產呼叫點只在三支 handler 之 `begin()` 與 `<op>_in_txn` 首句（取鎖）之間，`*_in_txn` 與 facade 零命中（變異自證）。
     - 碼註連動（U6）：`model/password.rs` 模組 doc「本刀恰兩支公開面」「不落 `hash()`…三支一併不帶」「自證案恰 5 支」「rev5 出處…只取 verify／dummy_verify／dummy_phc 三支形」、`rust-api/Cargo.toml` argon2 列「本刀不產 hash」、`server/Cargo.toml` argon2 與 getrandom 消費者句改現在式；migration 兩處「m0002 無 runtime 雜湊」描述 m0002 本身、仍真不改。
  2. **設密冷卻**（ADR⑤；data-model §2.3）：
     - `model/password.rs::cooldown_remaining_secs(conn, target_id, operator_id) -> Result<Option<u64>, AppError>`（None＝放行；resetUserPassword、changePassword 呼叫，addUser 結構性恆過、不呼）：秒數讀 `password_change_min_interval`（seed 60、registry [0,86400]；壞值退 60＋warn）；0＝停用、早退不查經手表。料源＝`sys_pwd_custody::last_set_at`（PK＝(user_id, created_by)＝(標的, 操作者)）；查無列放行。已過秒數＝（現刻−上次時戳）**取整秒下取整**；已過 ≥ 冷卻＝放行，否則剩餘＝min(max(冷卻−已過, 1), 冷卻)（已過為負＝時鐘回撥＝仍屬未滿、上限取冷卻秒數；`rev5` HEAD 形補上限）。
     - 位次（resetUserPassword／changePassword）＝政策之後、寫入之前、per-user advisory 內（同標的並發設密序列化、後到者鎖後讀到前者時戳）。addUser 之冷卻結構性恆過（新 id 由序列發、從未有經手列；bigserial 不回收）＝不呼 `cooldown_remaining_secs`，INSERT 後同交易 `touch(新 id, 操作者)`＝初始密碼計入（一案釘空格理由）；一體適用零豁免；不同操作者各記各帳。
     - `sys_pwd_custody::touch`＝upsert 該對 `created_at`（衝突鍵＝複合 PK），時戳取 `facade::now_ts()`（`ON CONFLICT DO UPDATE` 不吃欄 default、PG `now()` 交易內恆定），MUST 與密碼寫入同交易；只 upsert、永不刪他人經手列（`rev4` 自改全刪語意屬首登強制改密＝BL-00140、不帶回）。
     - 拒絕＝`handler::user::pwd_set_too_frequent_err(remaining_seconds)`（見 4）。
  3. **改密舊密節流**（ADR⑤；data-model §2.4）：
     - 鍵 `cpwd:{uid}`（`cache::CHANGE_PWD_KEY_PREFIX`、`cache::change_pwd_key(uid)` 單點渲染；不放 `throttle:` 下＝判定維度為已驗身 uid、兩態無軟區、維運批清 `throttle:*` 不得誤清）；新原語 `cache::incr_with_window`＝atomic pipeline `INCR`＋`EXPIRE`。
     - `throttle/change_pwd.rs`：碼內常數 `CHANGE_PWD_MAX_FAILS`＝5、`CHANGE_PWD_WINDOW_SECS`＝900（不入設定表：正確值只一個量級、旋鈕只會被調鬆＝`rev5:ADR 0066` 決定三）；`precheck(cache, uid) -> Result<(), Throttled>`（純讀；計數 ≥5＝`Err(Throttled)`；拒因 `biz.user.changePasswordThrottled` 純 key 由 handler 於步序③構造＝R12、不下發剩餘秒數或次數）；`record_failure`（每次失敗刷回 900 秒＝窗自**最後一次失敗**起算）；`clear`（`DEL`）；後兩支回 `()`。
     - 只有舊密不符推進（交易 rollback 後呼叫）；其餘拒因不推進；成功於 **commit 之後** `clear`。第 6 次起於舊密比對前即拒；窗自癒、無解鎖端點。預檢＝begin 前之純讀、結果暫持，拒於鎖讀之後之步序③（R12）＝被節流請求零舊密比對、零稽核、零推進（新密雜湊已於取鎖前算出＝白算一次生成，`rev5:ADR 0066` 與 ADR-00078 後果同）。〔本刀 U13 期間註：判讀改帳號鎖內現讀、推進改於 rollback 之前＝ADR-00090 決定 2（BL-00144）；本段為 plan 期論證、不改寫〕
     - fail-open：三支 redis `Err` 一律放行——先落一則結構化 error（target `security.throttle`、欄 `step`＝`precheck`／`record_failure`／`clear`、`error`＝redis 錯誤；同 `db_count` 先落 root cause 之形），再經**既有單一出口** `throttle::warn_degraded("redis_change_pwd")` 推進 `throttle_degraded_total{source="redis_change_pwd"}`＋warn（target `security.throttle`）；快取缺席（測試專用形、ADR-00036 決定 1）放行不計數。不沿 `rev5` 另立降級函式：`obs.rs` 發射字面靜態掃描只掃 `warn_degraded(` 引數、第二出口會逃出機器守。redis 不開持久化（ADR-00069 款 5）下重啟清空各桶＝與 fail-open 同向之放寬；款 5「節流判定面不依賴 redis」射程＝登入節流、不構成翻案。
     - 同一 commit（節流模組與降級名冊）：`obs::THROTTLE_DEGRADED_SOURCES` `[&str; 10]`→`[&str; 11]`、末位 `redis_change_pwd`、預註冊 0；常數 doc「恰十」→「恰十一」、凍結存證句改「前十值＝004 刀 data-model §5、第十一值＝本刀 data-model §2.4」；`obs.rs` 檔頭「十值」、預註冊案區域常數與訊息、名冊字面釘；`throttle/mod.rs` `warn_degraded` doc「十值」→「十一值」、「其餘九源皆在本模組」→「其餘十源皆在本模組樹（含 `change_pwd`）」與長度斷言；同檔測試 `warn_degraded_increments_each_of_the_ten_sources` 改名 `…_eleven_sources`、doc「對十源各呼一次」「值集恰十」與斷言訊息「十源名冊」改十一；`lib.rs`「降級十源」；發射掃描案已知發射點補 `throttle/change_pwd.rs`；名冊→發射端＝以 `test_kit::bad_cache()` 對三支各打一次。活書 06（降級源逐值列舉）與 12（「節流兩維降級源」）依 RL-0011 枚舉逐處判讀。`obs016-throttle-degraded` expr 無 source selector（規則註解自陳新增值亦命中）＝規則零改動。
     - ADR-00038 射程釐清（ADR⑤ 決定款；不翻案、不 supersede）：全篇射程＝標題「登入節流判定面」，決定 2「redis 在節流面只承載兩種鍵」讀作登入節流面；憲法島 E 該句以「於本島」自限、不受觸。`cache::CHANGE_PWD_KEY_PREFIX` doc、`change_pwd.rs` 模組 doc 各一句指 ADR⑤；`cache/mod.rs` 檔頭「`cpwd:` 前綴…`incr_with_window` 屬後刀域、不帶」改現在式；`throttle/mod.rs` 檔頭「快取層在本模組只承載兩種鍵」補射程限定「（登入節流判定面；子模組 `change_pwd` 之 `cpwd:` 計數鍵另見 ADR⑤）」（入同一 commit）。
     - BL-00124 四面比較（rev6 形；入 ADR⑤；登入節流已改 PG 滑動窗＝ADR-00038，故比較載體）：

       | 面 | redis 計數桶 | PG 滑動窗 |
       |---|---|---|
       | 一致性 | 單鍵 atomic；並發至多多放一次、加值防線可承受 | 需失敗紀錄面：借 `sys_login_attempt` 即與登入帳號維互染；另立表或欄＝DDL |
       | 降級 | 獨立故障域、fail-open 可告警 | 與端點同庫，PG 壞時端點本身已失敗 |
       | 清理 | TTL 自癒；測試 `RedisKeysGuard`、走查清 `cpwd:`（R16） | append-only 累積：收窄集或 TRUNCATE＋setval、另需保留期（BL-00043） |
       | 維運 | 無解鎖端點；前綴批清不殃及登入鍵 | 可查證據，但 FR-031 禁改密新增存取軌跡寫入面 |

       結論取 redis；通用節流 seam 續不做（判定鍵、語意分區、門檻來源、載體四者皆異）；翻案觸發＝出現第三個與既有兩者之一同形之消費端。BL-00124 收刀刪列。
  4. **明細通道**（ADR③；contracts/wire-user-center.md §3、msg-keys.md §2）：
     - `AppError::BizData(Cow<'static, str>, serde_json::Value)`：碼 2222、`msg`＝鍵；變體 9→11（另一＝`ModalLogoutByAdmin`，R10）；13 碼矩陣與可發碼集不變。`envelope.rs` 增 `Res::from_err_with_data`（`pub(crate)`、`impl Res<serde_json::Value>`），分派點**恰一處**＝`impl IntoResponse for AppError` 之 `BizData(_, data)` 臂；`Res::from_err` 不動、對 `BizData` 亦回 null。
     - 單一組裝點（`handler/user.rs`、`pub(super)`、`handler/user_center.rs` 共用）：`password_policy_err(violations)`→具型 `PasswordPolicyDetail { violations }`（例 `{"violations":["minLength","requireDigit"]}`，序同 1）、`pwd_set_too_frequent_err(remaining_seconds: u64)`→具型 `PwdSetTooFrequentDetail { remaining_seconds }`（`rename_all = "camelCase"`＝`{"remainingSeconds": 30}`）；具型構造後 `serde_json::to_value` 入 `BizData`（兩型同入 wire 受審名冊）。生產面 `BizData(` 構造點**恰兩處**、皆在此兩支內＝射程嚴限兩鍵之機器面（源碼掃描案、三形聯集、變異自證）。其餘錯誤 `data` 恆 null、`5003` 恆純 key；payload 零密碼材料。
     - 落地序：U6 只立 `BizData` 變體、`Res::from_err_with_data`、`IntoResponse` 之 `BizData` 分派臂與 msg-key-gate 斷言 2 擴認（含 `#[cfg(test)]` 構造驗證；生產區零 `BizData` 構造點、零新鍵）；兩支組裝點、兩 `msg_key` 常數、`MSG_KEYS` 與三檔 backend 子樹增列隨首個發出者落地——`passwordPolicy`＝U8（addUser）、`pwdSetTooFrequent`＝U10（resetUserPassword；addUser 冷卻格結構恆過、不發）（R14 決定 9、R23）。
     - msg-key-gate 斷言 2 擴認 `AppError::BizData(`／`Self::BizData(`／裸 `BizData(` 三形：首引數須 `Cow::Borrowed(` 字面或 `msg_key::` 常數；射程守分階段四句（①構造點之鍵 ⊆ 工具常數 `BIZ_DATA_KEYS`〔恰兩鍵〕②`BIZ_DATA_KEYS`∩`MSG_KEYS` 之每鍵生產區恰一處構造點③未入 `MSG_KEYS` 之鍵構造點數 0④射程鍵以 `AppError::Biz(` 構造＝紅）＋佔位符對賬（明細型序列化欄名＝三檔 locale 該鍵譯文之 `{…}` 佔位符集；非攜參鍵譯文零佔位符）（現行 `Biz\s*\(` 對 `BizData(` 零命中＝不擴即逃出守門）；`BizData(_, _) =>`／`BizData(..) =>` 等樣式不計（`rev5:L-064` 前例）；自測一正一反（RL-0080）。
     - 002 刀 wire 契約 §3 第 3 條（錯誤 `data:null` 不省略）之改寫形：`specs/002-system-settings/` 本文不動（凍結存證＝ADR-00041；004 刀 brainstorm G2「後刀改前刀端點契約＝增量記本刀 contracts」前例），改寫落現在式承載：①本刀 contracts/wire-user-center.md §3 記「`data` 鍵恆在場；值恆 null，唯 ADR③ 兩鍵攜明細」②`envelope.rs` 模組 doc、`Res`／`from_err` doc 與 `error_envelope_data_null_not_omitted` doc 改述為「一般錯誤恆 null＋唯一例外＝ADR③」，增兩釘（`BizData` 經 `IntoResponse`＝物件、2222、同鍵、欄序 `data→code→msg`；經 `from_err`＝null、code／msg 逐字同）③`error.rs` 檔頭「變體集恰九」→「恰十一」、「BizData／ModalLogoutByAdmin 屬後刀域、不帶」改現在式；同檔 `AppError` doc「data-model §11 九列逐字」與測試對照表 doc「九列」改十一、`impl IntoResponse for AppError` doc「信封統一交給 `Res::from_err` 組（data:null 保留不省略）」改述（`BizData` 經 `from_err_with_data`）④碼註指向 002 契約 §3 第 3 條者 6 處（`envelope.rs` 3、`error.rs` 1、`tests/common/mod.rs` 1、`tests/contract.rs` 1）同批補指 ADR-00076（U6；spec FR-051 修補後讀法）。
     - 相容論證：違規碼是 `data` 之**值**、非 `msg` 鍵 ⇒ 不入 `MSG_KEYS`、不入 backend 子樹，斷言 1 不受影響；譯文落 `page.passwordPolicy.violation.<code>`（plan 期主線定案；三語 Schema 型別守鍵集）。contract 方向二只及 `msg`：兩攜參鍵各由真 seed app 一案實發：`passwordPolicy`＝過短密碼新增帳號（拒、零寫入）；`pwdSetTooFrequent`＝以 `PwdCustodyWriteGuard` 登記並植（自建帳號, Super）經手列後重設一次（首發即拒、零業務寫入；R14 決定 7），`data` 之值無發出義務。斷言 3：請求層對兩鍵之字面消費點登記 `FRONTEND_MSG_CONSUMERS`；`page.passwordPolicy.violation.${code}` 屬動態模板、`page` 非安全前綴，不入射程。
  5. **政策壞值告警**（ADR⑥；data-model §2.5）：
     - 計數族 `password_policy_invalid_total`（無 label）、出口 `obs::password_policy_invalid()`（只計數、同 `obs::ipgate_blocked` 形）、`pre_register_metrics` 預註冊 0、`obs.rs` 檔頭宣告面補列。生產呼叫點**恰一處**＝`password::validate_against_policy` 判出 `min_length > max_length` 之腿（只有三設密入口經過；靜態掃描案、同 `ipgate_blocked_outlet_is_called_from_exactly_one_production_site` 形；變異自證）；不入 `throttle_degraded_total`。計數語意＝「設密因政策矛盾被拒之次數」（spec FR-034）：每次設密各計一；getPasswordPolicy 只讀不驗、不計（讀端亦計會使告警語意擴為「有人讀到矛盾政策」、warn 量隨開頁次數放大；plan 期初案之「載入件」位改置驗證件、仍恰一處）。
     - 同腿 warn 一則：target `security.password`、欄 `min_length`／`max_length`（現值）、零密碼零帳號名。
     - rules.yml 增 ③e：uid `obs016-password-policy-invalid`、title `password-policy-invalid`、expr `sum(increase(password_policy_invalid_total[5m]))`、A→B（reduce last）→C（`gt 0`）、`for: 0s`、`noDataState: OK`、`execErrState: Alerting`、`severity: warning`；檔頭「五組 12 條」→「13 條」、出處句「rev4:016 四組 10 條＋rev4:017 一組 2 條」補「＋本刀 ③e 一條」；RUNBOOK §11 增判讀一則。
     - 活體驗證（承 `maint-backlog-29-93`〔2026-09-29〕之告警規則活體驗證形；dev 庫寫入逐步取 user 放行＝LL-00053；排入 U22 走查窗＝dev 庫寫入點）：①`--profile obs --profile metrics` 起、確認規則自檔載入且評估健康、`/metrics` 見 0②Super 經系統設定寫端設 min 20／max 10③對自建帳號設密一次＝`2222 biz.user.passwordPolicy`、計數 +1、一評估窗內轉 Alerting④寫端改回 8／64（走查還原工具對 `system_settings` 只清審計欄、不改值）後還原、diff rc 0⑤增量滑出 5 分鐘窗後復歸。
     - 設定寫端不加組合守門（BL-00031 方向）；登入不受影響；與島 E「整組退」方向相反之跨島註入 ADR①（R20）。BL-00031 收刀刪列。
  6. **三重不洩與 DTO 遮蔽**（plan 期主線定案）：回應白名單零 `password` 欄、兩寫端回 `data:null`；稽核 addUser `payload_after` 白名單無密碼、reset／change 只載 `{id, userName}`；日誌零明文零 PHC。addUser、resetUserPassword、changePassword 三支請求 DTO（型名照 contracts）與 `handler/auth/login.rs` 之 `LoginReq`（現 `#[derive(Debug, Deserialize)]`、`password` 未遮）一律手寫 `Debug`、密碼欄印 `<redacted>`；每支一案（各密碼欄互異樣本、`{:?}` 不含任一、遮蔽字面次數＝密碼欄數）；稽核 payload 案斷言零 `password` 鍵且不含明文與 PHC。
- **Rationale**:①三件皆 `rev5:007` as-built 已驗形（`rev5:ADR 0066`／`rev5:ADR 0068`），rev6 差異只在 argon2 0.6 API、registry 單一權威（ADR-00054）、降級走既有出口、交易歸 handler。②壞值逐鍵退而非 ADR-00038 決定 4 之整組退：節流三鍵是同組門檻、混合值無人拍板；密碼七鍵彼此獨立，整組退會因一鍵壞值拋棄已設之較嚴政策（例：僅 `password_require_special` 列壞，整組退即連 min 12 一併退回 8）＝靜默放寬；跨鍵矛盾依 Q19 全拒。③剩餘秒數以已過整秒扣：與 US3 場景 5（T0＋30 秒、冷卻 60＝剩 30）一致，且不小於真實剩餘、照提示重試不再撞冷卻。④節流預檢於 begin 前純讀、拒於鎖讀後之步序③：與其餘寫端「①活性標的鎖讀先行」同形、且島 I5 要求生成在交易內（取鎖前）⇒ 被節流請求仍白算一次 argon2 生成（`rev5:ADR 0066` 後果同、ADR-00078 後果），拒因鍵不變。⑤兩項明細是使用者唯一能據以修正輸入之資訊；其餘拒因攜明細即逐案外洩（ADR-00014 翻案觸發器「明細受眾邊界重評」由 ADR③ 回應）。
- **Alternatives considered**:①改密節流走 PG 滑動窗（需失敗紀錄面＝DDL 或與登入桶互染）②節流門檻入設定表③節流 fail-closed（快取失聯期全體改不了密碼）④另立降級函式（逃出發射掃描）⑤政策壞值整組退（理由②）⑥設定寫端加跨鍵守門（Q19 定寫端不守）⑦壞值併入 `throttle_degraded_total`（非節流降級、標題誤導）⑧載入件判矛盾即計數（getPasswordPolicy 亦計＝告警語意擴為讀到即告、warn 量隨開頁放大；plan 期初案之載入件位，改置驗證件）⑨明細開放全部 2222（逐案外洩）⑩改寫 `specs/002` 契約本文（違 ADR-00041、GT-06）⑪鎖內雜湊（違島 I5）⑫違規碼入 backend 子樹（非 `msg`、卻須入名冊負發出義務）。

## R12 個人中心與自助白名單（ADR④）

- **Decision**:
  1. **getPasswordPolicy**（`handler/user_center.rs::get_password_policy`；`Protection::Authed`、零政策列）：`load_password_policy(&state.db)` 經**唯一投影路徑** `impl From<PasswordPolicy>` 出七鍵（`minLength`／`maxLength` number；`requireDigit`／`requireLowercase`／`requireUppercase`／`requireSpecial`／`forbidUsername` boolean；後端型名同前端 `Api.UserCenter.PasswordPolicyView`），**不含冷卻秒數**。與把關同源＝同一載入件、同一缺鍵預設。唯讀不取鎖；零副作用（讀端不計矛盾數＝R11 決定 5）；查庫失敗 `5000`、前端退為必填（FR-038）。
  2. **changePassword**（`handler/user_center.rs::change_password`；Authed）：body `oldPassword`／`newPassword`／`confirmPassword`、結構性零 `id`＝標的恆 `identity.uid`；壞形經 `common::json_or_default` 收斂為三空字串交既有守門。步序：
     - 交易外：`common::operator_from_context`（缺席 `5000`、先於一切守門）→body 收斂→`change_pwd::precheck`（純讀 `cpwd:{uid}`、結果暫持；redis 錯誤 fail-open＝R11 決定 3）。
     - 交易內：begin→`NewPassword::prepare`（交易內、不持鎖＝spec FR-012）→`sys_user::advisory_lock_user(txn, uid)`→①`find_active_by_id_for_update`（查無或已刪＝`biz.user.notFound`）→②兩次一致（`biz.user.passwordConfirmMismatch`）→③節流（預檢結果為 `Err(Throttled)`＝`biz.user.changePasswordThrottled`、零推進）→④舊密 `password::verify`（鎖內；不符＝`biz.user.oldPasswordMismatch`、rollback 後 `record_failure`）→⑤新≠舊（舊密已驗真＝明文相等即拒 `biz.user.passwordSameAsOld`、零額外 argon2）→⑥政策（帳號名取鎖內列）→⑦冷卻 (uid, uid)→寫 `password`＋`updated_at`／`updated_by`→`sys_pwd_custody::touch(uid, uid)`→`sys_token::revoke_others_of_user(txn, uid, &identity.sid)`（迴圈形、只撤 active、保留當前鏈）→逐 sid 會話事件 `revoked`／`password_changed`→稽核 `change_password`（`{id, userName}`）。
     - commit 後：`handler::user::finish_user_write`（`pub(super)` 共用；逐 sid 盡力寫失效名單、原因 `revoked`）→`change_pwd::clear`；回 `data:null`。
     - 對 `rev5` HEAD 之差：雜湊生成自 begin 前移至交易內、取鎖前（spec FR-012；R5 #40）；判定序與拒因鍵同 `rev5` HEAD（鎖讀 notFound 先行→一致→節流→舊密→新≠舊→政策→冷卻）。FR-031 反向確認＝R10 第 10 款。
  3. **Identity 增 sid**（plan 期主線定案）：`auth::Identity` 增 `sid: String`；注入點唯一＝`auth::enforce::enforce_mw` 放行後之 `insert(Identity { … })`，值取 `claims.sid`（`jwt::Claims` 必填欄、值即 `sys_token.rotation_chain`）。構造點 11 處＝生產 1＋測試 10（`handler/menu.rs` 4、`policy_archive.rs` 2、`role.rs` 2、`system_settings.rs` 1、`throttle.rs` 1；`tests/` 零），加欄由編譯器逐處列出（RL-0026）；`rev5` 舊形「標頭再驗章取 sid」不帶。連動：`auth/mod.rs` 模組 doc「恰兩欄」與 `Identity` doc「第三欄 `sid` 屬後刀域」、`enforce.rs` 檔頭同句；活書 06「注入 `Identity{uid}`」、08「注入 `Identity{uid, user_name: ""}`」補 `sid`；ADR-00014 後果段「注入形不變」由 ADR④ 註記（body 不改）。
  4. **自助路由白名單**（`handler/route.rs`）：`const SELF_SERVICE_ROUTES: [&str; 1] = ["user-center"]`；`get_user_routes` 於 `sys_menu::visible_menu_routes`（casbin `menu` 維過濾）**之後**、組樹之前恆併入（`HashSet` 去重）——併在過濾前或塞進角色集＝零選單政策角色仍被濾掉、且 Super 案照綠。seed 政策列 123（`p|R_SUPER|user-center|menu`）保留。收錄判準：只收受眾＝本人之自助頁（頁上每支端點皆 Authed、標的恆 `claims.uid`）；RBAC 資源頁禁入（入即對全體永久開啟、繞過授權 UI）；擴列回 ADR④ 重驗。零角色帳號之樹＝白名單一項、`resolve_home` 兜底取先序第一可導航葉＝登入即落個人中心；白名單葉亦參與首頁兜底：首頁不在可見樹且可見葉皆排序於 999 之後之角色，登入落點為個人中心（與 rev5 HEAD 同形；ADR-00077 後果、ADR-00081 款 17）。機器守：①零選單政策角色（自建角色無 `menu` 授權之帳號、零指派帳號各一）得 `user-center`②白名單外路由不受影響③常數恰一列之射程釘④拆併入段即 ① 紅。
  5. **與 §I.2 之關係**（ADR④；承 `rev5:ADR 0065` 二支柱、依 rev6 事實重核）：§I.2 規則句無頁級豁免，不援 `rev4` 頁級豁免形——①含義首條射程＝「**業務** menu 走 getUserRoutes→Casbin 過濾→顯示」，個人中心無受治理資料面、受眾恆本人；②`sys_menu` id 16 之 `hide_in_menu`＝TRUE（m0002 實值）＝側欄「顯示」結構性不觸發，且屬 §I.2 釋義② upstream 原樣六列白名單（`rev5:ADR 0005`：16｜user-center）。缺一不可。翻案觸發＝白名單增至三頁以上或收進不帶 `hide_in_menu` 之頁。
  6. **檔頭前代歸因勘誤**：`handler/route.rs` 檔頭「自助路由白名單屬 `rev5:004` 增量…不帶」不實。`rev5` rust-api 子庫 `git log -S SELF_SERVICE_ROUTES`：`rev5:67e59c7`（2026-08-10，`rev5:003` T026）碼註「`rev4` 之白名單（`rev4:014-user-center`、`rev4:ADR 0065`）不帶回」；`rev5:d5d5306`（2026-08-29，`rev5:007` U4）引入。正確出處＝起源 `rev4:014-user-center`、`rev5:003` 不帶回、`rev5:007` U4 帶回（`rev5:ADR 0065`）；隨 U12 改寫並以 `python3 tools/docsync errata 'rev5:004'` 枚舉。
  7. **005 刀照帶前提之翻轉**：005 刀 research「rev5 對 rev4 之十一項防回歸（本刀照帶、烤入 prompt）」含「`SELF_SERVICE_ROUTES` 不帶回」，其前提（個人中心端點不存在）隨本刀消失＝明寫翻轉、入 ADR④，本刀防回歸清單不列（R5）；同清單「業務錯誤純 key 不攜參」→ADR③、「zh-tw 不上 runtime」→ADR⑪ 同刀翻轉。005 刀 research 屬史料面、不改。
- **Rationale**:七步序與白名單皆 `rev5:007` 已驗形；rev6 憲法無 `rev4` 之頁級豁免條，`rev5:ADR 0065` 二支柱逐一實查成立。sid 已在票面、驗章當下即得，是保留當前會話之唯一誠實來源。
- **Alternatives considered**:①seed 給他角色增 `user-center` 政策列（新建角色仍漏配、需 migration）②憲法補頁級豁免條（與釋義②重複）③前端寫進常量路由（破後端唯一路由來源）④keep-sid 以標頭再驗章取得（`rev5` 舊形）⑤一致與節流移至雜湊與交易之前（被拒請求省一次雜湊，但與其餘寫端「①活性標的鎖讀先行」不同形、已刪本人之拒因隨輸入而變）⑥回設定列 key/value 陣列（`rev4` 形、解析推給前端）。

## R13 m0003、閘序號合成、選單刪碼守門、schema-definition（ADR⑬⑭⑮）

- **Decision**:
  1. **m0003**（ADR⑬）：`rust-api/migration/src/m0003_seed_button_governance.rs`，`DeriveMigrationName`＝遷移帳版本名 `m0003_seed_button_governance`；`migration/src/lib.rs` 加 `mod` 並 append 為向量第三元，其 doc「後續 delta 自 m0003 起編」改現在式。寫法沿 m0001／m0002（`manager.get_connection()`＋`execute_unprepared`、不自開交易）；零 DDL、零新依賴；屬新寫碼、不在憲法 §I.5 例外②（只及 m0001／m0002 與 entity 十五檔）⇒ 受 `rust-fmt-gate` 一般判準。`up`：

     ```sql
     -- ① 六碼改受保護（GR1、GR1a）——恰 6
     UPDATE casbin_rule SET protected = TRUE
      WHERE (id, v1) IN ((58,'role:add'),(59,'role:edit'),(60,'role:delete'),
                         (61,'menu:add'),(62,'menu:edit'),(63,'menu:delete'))
        AND ptype = 'p' AND v0 = 'R_SUPER' AND v2 = 'button' AND protected = FALSE;
     -- ② 刪 R_ADMIN 之 user:edit（GR7）——恰 1
     DELETE FROM casbin_rule
      WHERE id = 44 AND ptype = 'p' AND v0 = 'R_ADMIN' AND v1 = 'user:edit' AND v2 = 'button';
     -- ③ 增 R_SUPER 之 ipRule:unlock（GR4）——恰 1
     INSERT INTO casbin_rule (id, ptype, v0, v1, v2, v3, v4, v5, protected, created_at, created_by)
     VALUES (164, 'p', 'R_SUPER', 'ipRule:unlock', 'button', '', '', '', FALSE, '2026-08-05T00:00:00+00:00', NULL);
     -- ④ 選單 78 按鈕清單尾端增碼（GR4）——恰 1
     UPDATE sys_menu SET buttons = '[{"code":"ipRule:add","desc":"新增IP規則"},{"code":"ipRule:edit","desc":"編輯IP規則"},{"code":"ipRule:delete","desc":"刪除IP規則"},{"code":"ipRule:restore","desc":"恢復IP規則"},{"code":"ipRule:unlock","desc":"解鎖來源IP"}]'::jsonb
      WHERE id = 78 AND buttons = '[{"code":"ipRule:add","desc":"新增IP規則"},{"code":"ipRule:edit","desc":"編輯IP規則"},{"code":"ipRule:delete","desc":"刪除IP規則"},{"code":"ipRule:restore","desc":"恢復IP規則"}]'::jsonb;
     -- ⑤ 序號只進不退
     SELECT setval('casbin_rule_id_seq', GREATEST(164, (SELECT last_value FROM casbin_rule_id_seq)), true);
     ```

     兩串皆緊湊 JSON 字面、以 `::jsonb` 轉型後語意相等比對（舊串＝m0002 現值四碼、逐字取自 m0002；新串＝尾端加 `ipRule:unlock` 一元素）。①～④ 以 `rows_affected()` 比恰等值（6／1／1／1），不符回 `Err(DbErr::Custom(…))`（指名步驟、期望與實得）。④ 不動 `sys_menu` 審計欄（seed 基線層改列；E-009 只登 `buttons`、兩者須一致）。
     - 交易與失敗：sea-orm-migration 於 Postgres 以單一交易包住一次 `up` 之全部待跑 migration 與 `seaql_migrations` 記帳（m0002 檔頭「框架交易保證失敗零殘留」同一前提；本段未讀框架原始碼，U4 以斷言變異實證）⇒ 任一斷言不符或 SQL 錯（例：dev 庫已有 id 164）＝整支回滾、帳不記→`migrate` 非零退出→`rust-api` 不啟動（`depends_on … service_completed_successfully`）＝fail-loud。冪等形＝成功只跑一次、失敗可安全重跑、前置不符即失敗；不採 `ON CONFLICT DO NOTHING`。
     - seed 基線層（島 G 之 G2 末句；工程判斷⑰）：直接改列、**不**走撤銷歸檔（列 44 不入歸檔表）與操作稽核。遷移後：授權列 163、序列 (164, true)、受保護 25（端點 15／選單 4／按鈕 6，皆 R_SUPER）、選單 78 列；R_ADMIN 按鈕碼餘 `B_CODE2`／`B_CODE3`。判定面開機載入；`run --rm migrate` 手動套用時須重啟 `rust-api`。
     - `down`（反序、逐句斷言）：④′ 選單 78 回舊串（恰 1）→③′ 刪列 164（恰 1）→②′ 回插列 44 原 id 原值（恰 1）→①′ 六列改回 FALSE（恰 6）→⑤′ `setval('casbin_rule_id_seq', GREATEST(163, (SELECT COALESCE(max(id), 0) FROM casbin_rule)), true)`（全新庫往返回 163）。
  2. **演進帳九筆**（data-model §9）：`knife`＝`007-user-password-admin`、`date`＝登記當日（實作期定）、`next_id`＝10。★`detail` 值取 **pg_dump COPY 文字形**（`copy_literal` 只跳脫、比對對象為正規化 dump）——與 SQL 字面不同形兩處：時戳 `"2026-08-05 00:00:00+00"`、jsonb 正規輸出（`": "`／`", "` 帶空白；凍結 `seed.sql` 該列即此形）：

     | id | kind | table | detail |
     |---|---|---|---|
     | E-001～E-006 | `seed_update` | `casbin_rule` | `pk` `{"id": 58}`～`{"id": 63}`；`set` `{"protected": true}` |
     | E-007 | `seed_delete` | `casbin_rule` | `pk` `{"id": 44}` |
     | E-008 | `seed_add` | `casbin_rule` | `pk` `["id"]`；`values` 十一欄 `{"id": 164, "ptype": "p", "v0": "R_SUPER", "v1": "ipRule:unlock", "v2": "button", "v3": "", "v4": "", "v5": "", "protected": false, "created_at": "2026-08-05 00:00:00+00", "created_by": null}` |
     | E-009 | `seed_update` | `sys_menu` | `pk` `{"id": 78}`；`set` `{"buttons": "[{\"code\": \"ipRule:add\", \"desc\": \"新增IP規則\"}, {\"code\": \"ipRule:edit\", \"desc\": \"編輯IP規則\"}, {\"code\": \"ipRule:delete\", \"desc\": \"刪除IP規則\"}, {\"code\": \"ipRule:restore\", \"desc\": \"恢復IP規則\"}, {\"code\": \"ipRule:unlock\", \"desc\": \"解鎖來源IP\"}]"}`（五元素全串；U4 以全新庫套 m0003 後之 pg_dump 實文核定） |

     `seed_delete` 屬契約 §1 kind 枚舉（恰八值）之合法值；§2 第 6 條排除之「刪除性演進」＝`drop_*`——RUNBOOK §10 步 2「刪除性演進＝不入本檔」同批補括號釋義。docsync 帳號投影只消費三帳號表之 `seed_*`＝九筆不影響 generate。九筆零 `system_settings` 登記＝走查還原工具之系統設定比對不受 m0003 影響；兩模式改以「凍結 seed ⊕ 演進登記」合成值比對系統設定（FR-057 (b)，user 2026-10-05 同日納入）屬 R16，為日後設定鍵之 seed 演進預備、本刀 m0003 不觸發。
  3. **dev 庫套用時機與 U4 內序**：`migrate`（dev 以 `cargo run --bin migration up`、bind mount `./rust-api`）每次 stack 起動自動套未跑者 ⇒ m0003 一落工作樹、下次 `up` 即進 dev 庫（不待 commit），故 U1（FR-057 (a)(b)）MUST 早於 U4。U4 內序：①撰 m0003＋九筆＋閘真凍結面合成案（離線）②取 user 放行：先以 U1 所取之 v4 基準跑基準檔模式 restore（遷移帳相同＝前置放行；seed 模式僅於演進帳尚未登記 m0003 時可用、此時九筆已登記＝不可用）、確認序列 (163, true) 且無 id 164，再重起 stack 套用③即重拍走查基準（LL-00053）④seed 錨改對（決定 5）並容器內全量⑤`schema-gate.py check`（dev 庫）。Day-1 三步（第 3 步 `--container` 全新庫重放 m0001～m0003）屬 U23；兩快照因零 DDL、零帳號列變更而無差。
  4. **GR9 序號合成**（`tools/schema-gate.py`）：`apply_seed_entries` 之 `seed_add` 現只 append 資料列、不碰 setval 行 ⇒ m0003 後 gate2 必報序列 163／164。擴充：`pk` 恰一欄且值為整數時，尋 `<表>_<pk>_seq` 之 setval 行（無此行＝非序列主鍵、不動；值壞形＝`GateError`），令現期望為 (v, c)、已發出最大值 m＝c ? v : v−1；新 id＞m 時期望改 (新 id, true)、否則不動——在 is_called 真之序列上與 m0003 ⑤ 之 `GREATEST` 形等價；此即 seed_add migration 之收尾契約（MUST `setval(<序列>, GREATEST(<新 id>, last_value), true)`）。docstring 同批補。自測：①`TestSeedSynthesis` 增三案（`t_ok` 加 id 3＝(2,t)→(3,t)；加不高於已發出最大值之 id＝不動；is_called 假之序列〔如 seed 之 `sys_ip_rule_id_seq` (1, false)〕加 id 1＝(1, true)；無序列行之表＝不動）②`TestNegativeInjection` 增一案（`test_5_fake_delta_synth_real_fixtures` 形、對真凍結 fixtures 登記假 `seed_add` casbin_rule id 164、獨立構造注入後 dump；未登記紅、登記後綠）③拆推進段＝①首案與② 轉紅。U1 時真帳仍空，故②用假登記；真九筆之活體驗證由 U4 `check` 與 U23 全新庫承擔。
  5. **seed 錨改對清單**（FR-046；grep 實數：`user:edit` 於史料面以外命中＝rust 測試 2（`tests/wire_schema.rs` 合成樣本）＋accepted ADR 2（ADR-00014、ADR-00068）＋m0002 3（憲法 §I.5 例外②逐位元檔、述 m0002 本身、不改）；schema-definition 零命中；帶列數之「受保護」現在式命中＝ADR-00064 背景 1）：

     | 檔／符號 | m0003 前 → 後 |
     |---|---|
     | `model/facade/sys_casbin_policy.rs` `seed_reads_and_the_seal_set_match_the_seed_facts`：「按鈕維 seed 實數」斷言與 doc 句 | (20, 0) → (21, 6)（聯集因選單 78 增碼含列 164；58～63 受保護） |
     | `tests/contract.rs` `governance_reads_real_seed`：「R_SUPER 按鈕維之 seed 列：20 項、受保護 0」斷言與 doc | → 21 項、受保護 6 |
     | 同函式：「seed 選單登記之碼恰 20 個」斷言與 doc | → 21 |
     | `handler/system_settings.rs` `us4_matrix_no_policy_roles_read_write_5003_no_disclosure` doc「該角色在 casbin seed 上持有使用者管理面的按鈕政策列」 | 改述為持 `B_CODE2`／`B_CODE3`；斷言不變 |
     | `model/facade/test_kit.rs` 角色／選單域守衛自證段註「`casbin_rule_id_seq=(163,true)`」 | → (164,true)；行為不變 |
     | `docs/arc42/12-glossary.md`「受保護授權列」條之維度枚舉 | 補按鈕維六列 |

     不改：`handler/auth/user_info.rs` 三帳號按鈕集案（期望以 `casbin_rule` 直查現算、Admin 餘兩碼「非空」照成立）；`tests/wire_schema.rs` 之 `user:edit`（合成請求樣本）；m0002 檔頭「true 數＝casbin 19」（述 m0002 本身、且屬逐位元檔）；schema-definition §8／§9（001 基線）；ADR-00014 背景、ADR-00068 款 18（accepted；後者由 ADR⑧ supersede）；ADR-00064 背景（ADR⑬ 註記＝決定 8）；史料面。同函式另有隨 ROUTES 49→61 而變之錨（端點維 35／14→45／15、getAllEndpoints 35→45、「列 68 候選外」前提改植探針＝FR-061）歸 U3、先於 U4；走查工具自測之 163 類錨屬 R16。
  6. **選單刪碼守門**（ADR⑭；FR-043；`handler/menu.rs::update_menu_in_txn`）：現序＝入域→鎖列→④不可變欄→⑤受保護選單（只看停用與改父＝`protectedMenu`）→⑥父驗證與防環→⑦常量父鏈→⑧href→⑨按鈕清單形制→⑩絕版碼按鈕維政策移入歸檔（先於 UPDATE）→⑪`sys_menu::update`→稽核；⑩ 不問受保護＝自鎖第二條路。新守門插 ⑨ 後、⑩ 前＝位次標籤「⑨′」（移除集以形制已過之清單為前提）：`patch.buttons` 出現時，移除集＝`sys_menu::button_codes_of(before.buttons)` − `button_codes_of(buttons_after)`（改碼＝舊碼移除；`null`／`[]`＝全移除；取**移除集**、不問他選單是否仍持有），移除集計算件＝`sys_menu::removed_codes`（純函式；既有 `obsolete_codes` 改呼之），經新讀件 `sys_casbin_policy::protected_button_codes(conn, &移除集)`（單一 SELECT：`ptype='p' ∧ v2='button' ∧ protected ∧ v1 ∈ 集`、不問 `v0`、空集不查庫）取交集，非空＝`2222 biz.menu.protectedButtonRemove`（純 key；常數名依 contracts/msg-keys.md §4）。拒＝外殼顯式 rollback：零變更、零歸檔、零稽核、零同步。不取鎖（已在選單序列化域、受保護旗標執行期零寫者）；不得借 `protected_endpoint_set`（腿⑥前半 `SEAL_QUERY_CALL_FILES` 守其使用點）。先序：⑤ `protectedMenu`、⑨ `buttonsInvalid` 先於本守門。名冊方向二發出案＝自建選單＋直植之受保護按鈕維授權列（形見 contracts/msg-keys.md §5；契約測試不打 seed 受保護列）；真 seed app 對 `manage_role`（選單 id 4）送移除 `role:edit`（拒、零變更）屬 `handler/menu.rs` 測試之真 seed 負向案。測試：真 seed 負向（移除與改碼兩形）、自建選單正向（非受保護碼照舊歸檔並同步）、合成形（自建選單掛碼 C＋合成角色直植 `protected=TRUE` 之 C 列）、先序兩案、變異。完備性：六碼只住受保護選單 `manage_role`（id 4，`role:*`）與 `manage_menu`（id 5，`menu:*`）——m0002 `role:edit` 字面恰 2 處（授權列 59 與選單 4 清單），兩選單不可刪、不可停用、不可改父（島 H3），清單移除由本守門擋、受保護旗標執行期不可設 ⇒ 受保護授權列無經選單寫端進歸檔之路。
  7. **schema-definition 留 001 基線**（ADR⑮ 整支續行並 supersede ADR-00012；GR8；ADR-00011 決定 5）：

     | ADR-00012 決定 | ADR⑮ 處置 |
     |---|---|
     | 1 左源／右源（`schema-snapshot.json`）／差額由演進帳解釋 | 續行；左源定性改「001 基線之人寫權威」 |
     | 2 十節齊；§1／§2／§5～§9 隨刀前進 | 改：十節齊、**各節留 001 基線不前進**；現況看快照、差額只登演進帳 |
     | 3 specs/001 data-model 零改動 | 續行 |
     | 4 子庫三處註解不改 | 續行 |
     | 5 左源座標改指 | 續行 |
     | 6 `!= 14` 隨首次加表改對 | 改：`parse_data_model_five` 之 `len(tables) != 14`＝**基線恆真**之解析完整性自檢（§2 永不前進⇒恆 14 親排表），非現況表數、不再有改對義務；依賴 14 之釘值案與 docstring 同理保留 |

     另明文：①新表＝演進帳登 `add_table`＋`archetype-map.json` 登歸屬（§1 為基線 15 表、不補列）②缺歸屬訊息兩處改新形——`tools/docsync/snapshot.py::gen_reference_schema`（現「先補 schema-definition.md §1（ADR-00012）再登記」）與 `tools/schema-gate.py::audit_archetype`（現「先補 data-model §1、再登記」）改為「於 `archetype-map.json` 登記該表歸屬（新表另登 `add_table`；§1 為 001 基線＝ADR⑮）」（現無測試釘字面）③`doccheck` 自此為基線完整性對賬、恆綠為預期；現況結構之機器守＝gate1④檔頭「本檔隨每支帶 migration 的刀前進」改「各節留 001 基線（ADR⑮）；現況結構＝快照、差額見演進帳；seed 現況＝凍結 seed ⊕ `seed_*`」，身分句「現行 schema 定稿」改「001 基線定稿」⑤`python3 tools/docsync errata ADR-00012` 全 repo 51 處，扣史料面、accepted ADR、BACKLOG 本條、events 與生成檔後之現在式 13 處改指 ADR⑮：`README.md` 工具樹 1、RUNBOOK §10、§12 各 1、`docs/ops/reference-src/` 六檔各 1、`snapshot.py` 2、`schema-gate.py` docstring 2；RUNBOOK §10「新業務表先補 §1 再登記 map」同批改②之形。BL-00047 收刀刪列。
  8. **ADR-00064 背景註記**（ADR⑬；FR-042）：其背景「受保護 19 列、按鈕維 0 列」m0003 後為 25 列（按鈕維 6）；決定 1 謂詞 `v2 ∈ HTTP 方法白名單`（`protected_endpoint_set` 收 `router::endpoint_methods()`＝GET／POST／DELETE）使按鈕維列結構上不入封死集＝封死集仍 15 鍵、端點維判定不受影響。撤六碼之任一＝既有受保護撤銷拒（`set_role_buttons` 撤銷集觸及受保護列即 Rejected、`biz.role.protectedRevoke` 整批拒）；現行自證以自建角色直植之受保護按鈕列承載，本刀補真 seed 一案（R_SUPER 送缺 `role:edit` 之期望集）；006 刀前端已依受保護旗標鎖定該項。ADR-00064 body 不改。
- **Rationale**:自鎖兩條路一以既有「受保護撤不掉」擋（零新判定碼）、一以選單刪碼守門擋；受保護集屬 seed 基線層（島 G2）＝只能經 migration、零 DDL 仍成立。逐句斷言把「dev 庫已偏離 seed」轉為 fail-loud。閘合成與 migration 之 `GREATEST` 同語意＝全新庫與走查前進過之 dev 庫皆可判。schema-definition 不前進＝BL-00047 之「§2 前進又登 `add_column` 即重算、doccheck 不讀演進帳」矛盾根除，較「改衍生數」「doccheck 疊合成」少一層。
- **Alternatives considered**:①按鈕維寫端以碼內特例擋超管撤 `role:edit`（R10 候選③、兩套保護並存）②後端對 R_SUPER 恆回全按鈕碼（候選④、與授權真相脫鉤）③已知態＋救援步驟（候選⑤、自鎖後只能改庫）④`ON CONFLICT DO NOTHING` 求冪等（前置不符時半新半舊而帳已記）⑤新列 id 取 `nextval`（全新庫與 dev 庫 id 不同、演進帳無確定值）⑥bump 選單審計欄（非執行期寫入、須多登一欄並與時刻耦合）⑦列 44 走執行期撤銷歸檔（歸檔語意錯置、回收桶多假候選）⑧守門取絕版集（強度隨他選單內容浮動；GR1b 定移除集）⑨借 `protected_endpoint_set` 傳 `["button"]`（觸名冊、混淆封死謂詞）⑩schema-definition 前進＋doccheck 疊合成（多一層、仍須解重算）⑪表數改自 §2 標題解析（基線不前進即無必要）⑫改寫 specs/001 凍結存證（決定 3 續行）。

## R14 wire 與 msg 鍵（ADR⑩）

- **Decision**:
  1. **清單列 wire 形**（getUserList／getDeletedUsers 之 `records` 元素＝`Api.UserAdmin.UserRecord`；型名＝後端 DTO 名、欄序＝wire 欄序，沿 `Api.RoleAdmin.RoleRecord` 慣例）：逐欄白名單構造；十四欄恆在場（DB NULL 以顯式 `null` 上 wire）＝`id`、`userName`、`nickName`、`userGender`、`userPhone`、`userEmail`、`status`、`sessionPolicy`、`userMemo`、`roles`、`createdAt`、`createdBy`、`updatedAt`、`updatedBy`（`rev5:007` HEAD 欄集、角色欄依 Q13 改形）；結構性無 `password`／`sessionId`／軟刪欄。審計欄照 `RoleRecord`：`createdAt` 恆非 null、`updatedAt` 可 null，皆 RFC3339 帶 `+00:00`（ADR-00061）；`createdBy`／`updatedBy`＝帳號名批次回填（查無即 null、不是 uid）。`id` 為 JSON number、掛 `serialize_i64_number_guarded`（2^53 fail-loud）；`status` 二值收斂 `'1'`／`'2'`、恆非 null。`roles`＝`Api.UserAdmin.UserRole[]`＝`{id, roleCode, roleName}`（`id` 同掛守衛；料源 `sys_user_role::roles_by_user_ids`＝濾軟刪角色、不濾 status，回收桶列恆 `[]`）。各欄型別與可空性之家＝`contracts/wire-user-admin.md` 共用型節。
  2. **型別兩檔**：`base-web/src/typings/api/rev6-user-admin.d.ts`（`Api.UserAdmin`）、`rev6-user-center.d.ts`（`Api.UserCenter`）；declaration merging、檔頭一行 `BASE-WEB-ADAPT+`、既有 typings 檔零改；命名空間沿 rev6 `Api.RoleAdmin`／`Api.MenuAdmin` 先例。型名＝plan 期主線定案十二支（`UserRecord`／`UserRole`／`UserListQuery`／`AddReq`／`UpdateReq`／`ResetPasswordReq`／`KickRes`／`UpdateSessionPolicyReq`／`UnlockReq`／`SessionPolicy`；`PasswordPolicyView`／`ChangePasswordReq`）＋本節補立六支：
     - `Api.UserAdmin.UserIdReq`（deleteUser／restoreUser／kickUser 之 `{id}`）、`UserBatchDeleteReq`（`{ids}`）、`DeletedUserListQuery`（getDeletedUsers 之分頁專用查詢）——沿 rev6 角色／選單域先例（`RoleIdReq`／`RoleBatchDeleteReq` 具名受審、`MenuListQuery` 為分頁專用查詢型）。
     - `Api.UserCenter.PasswordPolicyDetail`（`{violations: PasswordViolationCode[]}`）、`PasswordViolationCode`（違規碼八枚之封閉字面聯集）、`PwdSetTooFrequentDetail`（`{remainingSeconds: number}`）——spec FR-064 明列「明細信封」為受審 wire 型；違規碼聯集兼供 `hooks/business/pwd-policy.ts` 組 `page.passwordPolicy.violation.<code>` 之型守。
     - rust 側同名（handler DTO；`UnlockReq` 即 004 刀既有 `handler/throttle.rs::UnlockReq`；明細兩形以同名 `Serialize` 型構造後轉 `serde_json::Value` 入 `AppError::BizData`，構造落點＝R11）。addUser 成功回 `data: null`（沿 rev6 `addRole`、不立 `AddRes`；對 rev5 HEAD 之 `data:{id}` 為刻意差異、前端新增後重拉清單＝UI 零差、R5 #48）。請求型簽名沿 `Api.RoleAdmin.RoleUpdateReq` 先例：不可變欄 `userName` 列入 `UpdateReq`（出現即拒 `biz.user.userNameImmutable`）、可空文字欄容 null——型別涵蓋 wire 全部可達形（`rev5:007` 以型別結構性排除 `userName` 之形不帶回＝R5 差異點）。
  3. **upstream 同 URL 型偏離帳第三列**（ADR-00044 決定 9 形；spec FR-008）：`rust-api/server/tests/wire_schema.rs` 之 `DEVIATION_LEDGER` 2→3 列，增（`UPSTREAM_USER_CMP`＝`"Api.SystemManage.User"`、`USER_RECORD_DEF`、`&USER_DEVIATION`）；比對常數不帶 `_DEF` 尾、非受審型（同 `UPSTREAM_ROLE_CMP`）。釘值以首次重抽之機器導出寫入、之後只隨拍板改；依快照現形（upstream `User`＝`CommonRecord` 之 `allOf` 兩支、六基底欄＋六業務欄全必出）預估：`upstream_only`＝`createBy`／`createTime`／`updateBy`／`updateTime`／`userRoles`；`rev6_only`＝`createdAt`／`createdBy`／`roles`／`sessionPolicy`／`updatedAt`／`updatedBy`／`userMemo`；`type_diff` 至少含 `nickName`／`userEmail`／`userPhone`（`string`→可 null）與 `status`（`'1' | '2' | null`→`'1' | '2'`），`userGender` 入帳與否隨共用型節定形。既有 `deviation_ledger_turns_red_on_each_planted_drift` 以迴圈走帳＝四類植入反例自動及於第三列，其前提（upstream 基底在 `allOf[0]`、rev6 `updatedAt` 為 `string | null`、`id` 必出 number）與上列欄形一致、不另寫反例。★畫面消費面：使用者管理頁改直接路徑匯入 `rev6-user-admin.ts`；`views/plugin/excel/index.vue`（upstream 示範頁、seed 選單列 32 授 R_SUPER、非 ★ 授權檔）仍經 barrel 消費 upstream `fetchGetUserList`——本刀後得 rev6 列形、與 `rev5:` 側 22080 同頁收斂；處置＝示範頁不改、為殘存消費面（ADR⑩ 決定 3）；spec FR-008 已於 plan 期收窄至使用者管理頁（user 2026-10-05 親決）。`DEVIATION_LEDGER` doc「兩列」、`upstream_same_url_types_deviate_exactly_as_ledger_pins` doc 之 `{Role,Menu}`、反例案 doc「兩列帳各打四類」同批改三列（含 User）。
  4. **wire 裁判名冊增列**：`AUDITED_READ_DEFS` 23→31（`UserRecord`／`UserRole`／`SessionPolicy`／`KickRes`／`PasswordPolicyView`／`PasswordPolicyDetail`／`PasswordViolationCode`／`PwdSetTooFrequentDetail`）、`AUDITED_REQUEST_DEFS` 23→33（`UserListQuery`／`DeletedUserListQuery`／`AddReq`／`UpdateReq`／`UserIdReq`／`UserBatchDeleteReq`／`ResetPasswordReq`／`UpdateSessionPolicyReq`／`UnlockReq`／`ChangePasswordReq`）、快照 `tests/fixtures/wire-schema.json` definitions 76→94（實數以 `python3 tools/wire-schema.py extract` 容器內重抽為準、不符即回改本節與 contracts）。節謂詞 `in_role_menu_sections` 擴認 `Api.UserAdmin.`／`Api.UserCenter.`（`wire_schema.rs` 之「三節」字面全檔 14 處——讀端完備性腿與請求端受審節段之 doc、斷言訊息、「快照三節零 definition」訊息——逐處改五節；植未入冊型之自證同擴兩節）。讀型入「序列化鍵集＝快照 properties 鍵集」表驅動（多帶 `password`／`sessionId`／冷卻鍵即紅），兩字面聯集型入「封閉字面聯集型」類。逐型反例：`UserRecord`＝`id` 為字串、`status` 為 null、`createdAt` 偏移非 `+00:00`、`roles` 元素缺 `roleName`；`UserRole`／`KickRes`＝數值欄為字串；`PasswordPolicyView`＝多冷卻鍵；明細兩形＝違規碼值域外、鍵缺席或型錯；請求型＝逐欄簽名一表釘值＋逐欄反例＋合法形反序列化落點（`roleIds` 元素型錯＝rust 整包判敗而由 `json_or_default` 收斂），兩支 query 型另走首屏真串與壞形收斂（同 005 刀 spec FR-057 形）。明細兩形之受裁對象＝錯誤路徑實產之 `BizData` 所攜 `data`。
  5. **`tests/wire_i64_guard_lint.rs`**：新 `Serialize` 型無巢狀 i64——`roles` 為 `Vec<UserRole>`（元素 `id` 為已守衛之 Plain 欄）、`roleIds`／`ids` 只在純 `Deserialize` 請求型、`KickRes.revoked` 取 `usize`（沿 `RoleMenuGrantRes.revoked`）、`remainingSeconds` 取 `u64`（皆非 i64）、addUser 回 `Res<()>`（不觸泛型實例化絆線）⇒ 絆線 `nested_generic_i64_fields_are_out_of_scope` 維持零筆、`EXEMPT_FIELDS`（4 筆）與 `GENERIC_WIRE_TYPES`（`PageRes`／`Res`）零增減、本檔零 diff。實作期若需直出 id 集合＝比照 `handler/role.rs::MenuId` 立 newtype、不得以入名冊閃避。
  6. **MSG_KEYS 46→68**：`msg_key` 增 22 常數、`MSG_KEYS: [&str; 68]` 尾端依落地序追加；`biz.user.*` 20 枚＋`auth.session.kickedByAdmin`＋`biz.menu.protectedButtonRemove`。`auth.session.kickedByAdmin`＝`AppError::ModalLogoutByAdmin` 之固定鍵（經 `AppError::key`、非 Biz 構造點）⇒ `msg_key` doc「固定鍵八支」改九支；`biz.user.passwordPolicy`／`pwdSetTooFrequent` 經 `AppError::BizData`（ADR③）、其餘 19 枚經 `AppError::Biz`。違規子鍵 `page.passwordPolicy.violation.<code>` 八枚與 `listSeparator` 非名冊成員、落 page 樹（spec FR-033）——放進 backend 子樹即須入名冊、入名冊即須真發出，兩向皆不成立。
  7. **contract 方向二（名冊每鍵 ≥1 發出點）承載點**：`tests/contract.rs` 之 `msg_roster_every_key_has_an_emitter`（`observed_msgs` ∪ `observed_msgs_real_db`）。`observed_msgs_real_db` 增掛使用者管理域與個人中心兩支發出件（命名實作期定：測試輔助件、不入名冊；沿 `<域>_msgs_real_db` 形）；選單刪碼守門鍵併入 `menu_msgs_real_db`；`auth.session.kickedByAdmin` 沿既有 `auth.session.kicked` 一發之形（`cache::denylist_set` 植 `REASON_ADMIN_KICK`、同 sid 真票再打、`common::CacheKeysGuard` 自 sid 產生處收鍵）。發出紀律：一律打應被拒之路徑、零業務寫入；需既存狀態者以守衛植之（冷卻＝植經手列後重設、節流＝植 `cpwd:{uid}` 達門檻後改密、`passwordSameAsOld`＝對本案 addUser 自建帳號送新密等舊密）；`oldPasswordMismatch` 一發必推進 `cpwd:{uid}`＝該鍵登記 `CacheKeysGuard`。檔頭「契約面用真 seed app 者恰二十一案」與該案 doc 逐刀列記段同批改（RL-0011；LL-00069 同主體異寫法併掃）。
  8. **msg-key-gate 三斷言**（`tools/msg-key-gate.py`）：①斷言 1：三檔 backend 子樹各 +22、`app.d.ts` backend 型節同批（I18N-WIRING (ii)(iii) 既有授權、新鍵落既有圈界、塊數不變）；`zh-tw.ts` 於 U15 改 Schema 全樹時 `backend: {` 錨行續獨佔一行。②斷言 2：現行 `RE_BIZ`／`RE_BIZ_FNVALUE` 對 `BizData` 恆不匹配（`Biz` 後緊接 `Data`）＝新變體構造點對閘隱形；擴認 `AppError::BizData(`／`Self::BizData(`／裸 `BizData(`：首參須 `Cow::Borrowed("字面"|msg_key::NAME)`、射程守分階段四句（①構造點之鍵 ⊆ 工具常數 `BIZ_DATA_KEYS`〔恰兩鍵＝ADR③ 射程之機器面〕②`BIZ_DATA_KEYS`∩`MSG_KEYS` 之每鍵生產區恰一處構造點③未入 `MSG_KEYS` 之鍵構造點數 0〔U6～U9 之過渡態〕④射程鍵以 `AppError::Biz(` 構造＝紅；②③隨落地階段生效）、第二參之佔位符對賬取明細型序列化欄名（R11 決定 4）；不帶括號之函式值形＝動態構造；enum 宣告與 match 樣式照既有排除；「構造點零處＝rc 2」改以 Biz ∪ BizData 之和判（現況 Biz 60 處、掃 52 檔）。③斷言 3：安全前綴現算＝{`auth`, `biz`} 不變；`FRONTEND_MSG_CONSUMERS` 1→3 項（既有 `views/_builtin/login/modules/pwd-login.vue`×`biz.auth.captchaRequired`；增 `service/request/index.ts`×`biz.user.passwordPolicy`、×`biz.user.pwdSetTooFrequent`＝請求層明細轉譯之鍵比對，次數預期各 1、以實掃為準）；7777 兩文案經 `translateBackendMsg` 動態轉譯、不成字面消費點。
  9. **落地時序**：每鍵隨其首個真端點發出單元落地（名冊、三檔 backend 子樹、`app.d.ts` 型節、發出件同批；跨子庫＝同一顆外層 commit 同 bump 兩 pin，pre-commit msg-key-gate 與 submodule-sync 兩段機器守）。★兩明細鍵之首個發出者＝addUser（U8）：U6 只立 `BizData` 變體、信封 `data` 上 wire 與閘之擴認（合成案與 `#[cfg(test)]` 構造驗證；斷言 2 排除測試區間），政策單點與冷卻判定回傳領域結果（違規碼集／剩餘秒數），構造 `BizData` 之映射與兩鍵隨 U8 落地——否則 U6 之生產構造點迫鍵入名冊、名冊鍵卻無真端點發出＝方向二紅。選單刪碼守門鍵隨 U4、`auth.session.kickedByAdmin` 隨 U10；逐鍵對單元表之家＝`contracts/msg-keys.md` §6。typings 兩檔、快照重抽、`wire_schema.rs` 名冊擴列同一顆外層 commit（pre-commit wire-schema 段雙側重抽比對工作樹；U14 收口、前端單元消費之）。
- **Rationale**:spec FR-004／FR-005／FR-008／FR-033／FR-053／FR-064／SC-002；Q13、Q14、Q18。審計欄沿 rev6 欄名＝004 刀起之 wire 慣例，與 upstream 之差由偏離帳機器導出；明細兩形與違規碼不立型則 FR-064 之「明細信封」無 definition 可裁；id 與批刪請求型具名受審，wire 裁判才覆蓋全部寫端請求且與角色域同形；`BIZ_DATA_KEYS` 把「唯二例外」變成機器判準（第三支 `BizData` 構造即紅、須先過 ADR③ 翻案觸發器）；明細鍵延至 U8 是方向二與斷言 2 疊加之唯一可行序。
- **Alternatives considered**:①沿 upstream 欄名（`createBy`／`userRoles: string[]`）免偏離帳——翻 004 刀起審計欄慣例、字串陣列承載不了 Q13 之 id 與名稱，棄。②沿 `rev5:007` 以角色代碼 `string[]`——灰色保留選項需 id 回送全量替換，棄。③明細信封不立型、只由 contract 案斷言——FR-064 明列受審、前端轉譯與 hook 失型守，棄。④id 請求體於包裝內聯 `{ id }`（`rev5:007` HEAD 形）——rust DTO 無受審 definition、與角色域分岔，棄（若維持原十二支，請求端實數為 30、快照 91）。⑤違規子鍵放 backend 子樹（`rev5:` 之 `passwordViolation.*`）——斷言 1 與方向二迫其入名冊並真發出，棄。⑥斷言 2 擴認而不設兩鍵白名單——明細通道射程無機器邊界，棄。

## R15 測試基建

- **Decision**:
  1. **守衛四件＋回補腿**（src＝`rust-api/server/src/model/facade/test_kit.rs`、tests 側鏡像＝`tests/common/mod.rs`；施工全文＝`contracts/code-gates.md` §5、形之家＝data-model §10）。現況：test_kit 有 14 支 `Guard`／`Fixture` 型與私有共同本體 `BandedRows`；無 `sys_user`／`sys_user_id_seq` 守衛、無 `sys_pwd_custody` 守衛；`UserRoleRowsGuard` 之 Drop 恰一句 `DELETE FROM sys_user_role WHERE role_id > $1 OR NOT (<arm 鍵集>)`＝只刪不補；`UserStatusFixture`／`SessionPolicyFixture` 各快照三欄。全 schema 之 FK 恰兩條、皆在 `sys_user_role`（指 `sys_user.id`、`sys_role.id`，`ON DELETE RESTRICT`）。
     - **`UserRowsGuard`**：包一枚 `BandedRows`（`sys_user`／`sys_user_id_seq`；帶界水位＝`COALESCE(max(id) FILTER (WHERE id < SYNTHETIC_UID_FLOOR), 0)`、序列 `(last_value, is_called)` arm 當下現讀）；Drop＝刪 `id >` 水位（界上合成 uid 列與 arm 前殘列無條件清）→ `setval` 回 arm 值；不回補界下列（寫端只軟刪）。★宣告在一切會動指派之守衛之前（後宣告者先 drop＝指派先清；與 `RoleMenuDomainRowsGuard` 併用亦然）；反序＝Drop 撞 `fk_sys_user_role_user` fail-loud（反腿釘）。
     - **`UserRoleRowsGuard` 擴兩腿**：arm 另讀 `sys_user` 帶界水位；Drop 序＝①刪「`role_id` > 角色水位」∪「`user_id` > 使用者水位」∪「不在 arm 鍵集」②回補 arm 鍵集中兩維皆在界下之對（`ON CONFLICT DO NOTHING`）——★先刪後補（同 006 刀授權腿：先補則被吞、新列隨後被刪）。回補語句模板兩側自持＝同批增 `include_str!` 逐字對賬案（`self_held_below_band_templates_match_src_verbatim` 同形）。
     - **`SeedUserRestoreGuard`**：arm 取 id 集（seed 形傳 `SEED_USER_IDS`）快照全可寫欄＋審計欄（`status`／`nick_name`／`user_gender`／`user_phone`／`user_email`／`user_memo`／`session_policy`／`password`／`updated_at`／`updated_by`，另含 `deleted_at`／`deleted_by`＝seed 保護守門被改壞而真軟刪時救得回）；Drop 無條件逐列寫回（`rev5:SeedUserRestoreCleanup` 已驗證之冪等理由）。指派面歸 `UserRoleRowsGuard`。既有兩 fixture 簽章與消費點（`handler/auth/login.rs` 8、`handler/role.rs` 1、`model/facade/sys_user_role.rs` 1）零改動，可與本守衛疊用（RAII 反序 drop、終態恆為最外層快照）。
     - **`PwdCustodyRowsGuard`**：arm 記 user_id 名冊（含 seed uid、含預期被拒者＝RL-0069）＋`sys_user` 帶界水位；Drop＝`DELETE FROM sys_pwd_custody WHERE user_id = ANY(<名冊>) OR user_id > <水位>`；無 setval（PK＝`(user_id, created_by)`、無序列）。seed 該表零列＝界下列皆殘列、刪即還原（`rev5:PwdCustodyCleanup` 同判）。
     - **`RedisKeysGuard`**：以 `cache::change_pwd_key(uid)` 逐鍵登記 `cpwd:{uid}`（先登記再寫）；tests 側沿 `CacheKeysGuard`。
     - **tests 側鏡像**：`UserWriteGuard`（`BandedTable` 常數增 `("sys_user", "sys_user_id_seq")`；帶界水位（表, 序列）常數逐字對賬案四組→五組）、`PwdCustodyWriteGuard`、`SeedUserWriteGuard`（沿 tests 側 `*WriteGuard` 慣例）、`UserRoleWriteGuard`／`UserRoleMarks` 同擴兩腿。
     - **自證**（RL-0080；取「自建列代 seed 列」形——直改 seed 列做拆腿或反序變異會令 seed 列留缺於 dev 庫＝違 spec FR-062）：各守衛一正（寫後 Drop 回 arm 態）一反（拆該腿＝自建列殘留而紅）；`SeedUserRestoreGuard` 以自建帳號 id 集行使同一本體、另釘 seed 形 id 集＝`SEED_USER_IDS`；回補腿取嵌套形（外層造帳號與指派、內層 arm 後撤該對、內層 Drop 須補回）。另立整合測試一支：經寫端改 seed 帳號之指派與欄值後守衛按原值回補（spec SC-008 末句；正向路徑）。
  2. **合成 uid 號段**：`SYNTHETIC_UID_FLOOR`＝9_300_000_000，兩側各自持、`self_held_synthetic_uid_floor_matches_src_verbatim` 逐字對賬；`sys_user` 帶界水位沿同界。現行顯式合成 uid 字面（界值除外）分布 13 檔、值落 `9_300_000_001`～`9_300_000_701`、逐檔互不重疊（`9_300_000_701` 為兩側同一植入建立者常數之鏡像）；`ID_RANGES`（29 列、自 9_300_100_000 起）之 doc 明載 `sys_user` 合成家族不在射程；同 doc「`sys_user_role`…`user_id` 一律取 seed 使用者（uid 1／2／3、免造 `sys_user`）」句本刀起成假述＝改為「`user_id` 取 seed 使用者或經 `UserRowsGuard` 守之自建帳號」（U2；R22 errata 種子）。本刀定：`sys_user` 造列一律走 nextval（寫端或 facade `insert`），由 `UserRowsGuard` 還原列與序列；唯換發 10 案與登出 1 案之 fixture 植顯式 id 活列（沿既有 `9_300_000_101`～`124` 常數、不觸序列；改造本體＝R10）。新顯式合成 uid 取該家族未用值（`grep -rnoE "9_300_000_[0-9]{3}"` 現核）；`ID_RANGES` 不增列。測試帳號名、信箱一律帶 `uniq_prefix()`（形 `t<hex>-<pid>-<n>`、≤32 字元、合 `^[A-Za-z0-9_-]{1,64}$`）。
  3. **seed 帳號為請求身分之敏感面**：`rust-api/server` 現有 20 檔（src 19、`tests/contract.rs` 1；不計定義處 `test_kit.rs`）以 seed uid 簽票、以 seed 明文登入或斷言 seed 角色集與暱稱（`UID_SUPER|UID_ADMIN|UID_USER`、簽票件首參 1／2／3、`login_pair(`、`seed_plain()`、`(1, "Super"`、`roles_of_user(<連線>, 1|2|3)` 六形聯集現算）。機制：`enforce_mw` 每請求以 uid 現查 `roles_of_user`、不採信票面 hint ⇒ 以 seed uid 打而期望放行之案皆依 seed 指派現值；docsync 帳號快照投影另比 `id`／`user_name`／`nick_name`／`status` 與指派全鍵。故 seed 指派或欄值一改即大面積連坐——守衛須「還原」而非「免疫」。
  4. **殘列不連坐**（spec FR-058、Q21、Q22）：具名排除兩形＝①seed 帳號角色指派被改（BL-00136 形②）②seed 帳號欄值被改，承載＝守衛（測試面）與走查還原工具（dev 面、R16）之還原。紀律：測試與走查寫入一律對自建帳號；斷言取水位窗、獨立 SQL 現算或鍵集過濾，不寫絕對列數；非改 seed 帳號不可之觀察限觀察窗、全量前先還原。保證面＝dev 庫存在自建帳號、自建指派、經手列與 `cpwd:` 鍵殘留時容器內全量全綠（殘列演練承載、形同 006 刀 T086）。應被拒之負向樣本（seed 保護、本人五不、Super 恆禁停用）亦掛 `SeedUserRestoreGuard` 與 `SessionRowsGuard`＝守門被改壞那一發之寫痕救得回（RL-0069 同理）。
  5. **契約面兩處陷阱**（真 seed app）：①授權態矩陣與他案打 changePassword 一律送兩次不一致之 body（第一步即拒、不觸舊密比對）——三個 seed 帳號送空 body 時兩欄皆空串而相等，會逐跑推進 `cpwd:` 桶、15 分鐘內第 6 跑起轉 `changePasswordThrottled`＝跨跑連坐。②resetUserPassword／addUser 之空 body 於標的或帳號名判拒前不觸冷卻寫入（案內以經手表列數前後不變佐證）。
  6. **LL 教訓適用點**：
     - LL-00017：`sys_user` 守衛用帶界水位、序列還原值取 arm 現讀；不帶回 `rev5:UserCleanup` 以 seed 上界常數寫死 `setval` 之形。
     - LL-00022：使用者域守衛只清本帶與 arm 差集、絕不以「有殘列即拒跑」硬化（FR-058 之前提）。
     - LL-00026：使用者寫端持 advisory＋列鎖，失敗腿顯式 rollback 並配源碼次序釘；drop-only 收場在 current-thread 測試中與守衛 Drop 互鎖、整輪卡死不轉紅。
     - LL-00035／LL-00043：委派測試以 `plant_live_policy` 植授權（重複植入回 `Err` 且吃 nextval、`CasbinRuleRowsGuard` 還原序列）；手寫 `casbin_rule` INSERT 之 v3～v5 填空字串。
     - LL-00037（RL-0066）／LL-00055：交易體內不放 `todo!()`、會 panic 之斷言與 `expect`／`unwrap`——斷言排在 commit／rollback 之後（判準變異同理）。
     - LL-00053：判準變異不拆真庫守衛；dev 庫寫入步驟排程即列 user 待辦（第 7 點）。
     - LL-00054：冷卻剩餘秒數與節流窗之斷言容忍牆鐘回撥（區間或下界斷言）；LL-00020：走查等 7777／8888 一律輪詢 `exp`。
     - LL-00059：觀察窗全量步只帶指定型殘列（自建帳號形）。
     - LL-00060：U3（ROUTES 49→61）與任何動 ROUTES 之單元收尾②另跑 `python3 -B tools/docsync test`。
     - LL-00069：數量詞勘誤種子含同主體異寫法（「恰二十一案」「分頁五案」「app 面」；走查工具內含「五表」之行現 29 行）。
     - LL-00032／LL-00056／LL-00061（RL-0085）：寫回不保 mtime、以 `Compiling` 自證重編；LL-00039：不以 host `timeout` 包容器內 `cargo test`；LL-00038：pnpm 一律容器內。
  7. **dev 庫寫入放行點**（LL-00053；逐步取 user 放行、演練只經 API 對自建帳號產殘列、psql 只下 SELECT）：①U4 中段（m0003 與單元測試寫成之後、全量前）以 U1 v4 基準跑基準檔模式 restore＋重起 stack 套 m0003（其後重拍基準＝唯讀免放行）；U1 前置不符時之 006 刀終態基準還原（R23 U1 出口）②殘列演練之產殘列與 restore 兩步 ③U22 之 CDP 走查本身與其前後 restore、告警活體實測（系統設定兩鍵改矛盾→觸發→改回；R11 決定 5） ④U23 之 Day-1 第 1 步前若需 restore 清殘列（帳號快照投影比 seed 欄值與指派、殘值令 generate 紅）與第 3 步 pristine 容器建立 ⑤任何手寫 SQL 回正（m0003 三欄表 Rollback 欄）。容器內全量測試之守衛自清不在此列。
- **Rationale**:spec FR-057、FR-058、FR-062、SC-008；本刀首度以寫端改動 seed 帳號並首寫 `sys_user`／`sys_pwd_custody`，三表皆在 gate2 收窄集（`RUNTIME_APPEND_TABLES` 恰四表）之外＝逐列比對、殘值即紅；指派表無建立者欄，006 刀形①之「建立者為 NULL＝seed」錨法不適用，只剩還原一途。
- **Alternatives considered**:①`sys_user_role` 加建立者欄比照形①——動 schema、牴觸零 DDL（GR8），棄。②形②與欄值形納入不連坐、改寫 20 檔 seed 身分案——超出交付面，棄。③`PwdCustodyRowsGuard` 取快照回補形——seed 零列、回補無對象，棄。④既有兩 fixture 以新守衛重寫——10 處改動、射程無增益，棄。⑤`sys_user` 合成家族另立號段表——帶界水位對界上列恆清、與檔別無關，棄。

## R16 走查還原工具 v4（FR-057）

- **Decision**:
  1. **檔形 v4**（`tools/walkthrough-baseline.py`；`SCHEMA_VERSION` 3→4；v3／v2／v1 舊檔 diff／restore 皆 rc 2 指名重拍——006 刀終態基準〔v3〕自 U1 起不可用）：新欄三項，併入現行角色／選單域撈取之單句（同一快照）——①`migrations`＝`seaql_migrations.version` 依名排序（非空、互異；空＝比對面為空 rc 2）②`id_bounds` 增 `sys_user`（`BOUNDED_TABLES` 四→五、序列 `sys_user_id_seq`）③`sys_user_rows`（`ROW_FACES` 新面、diff 面名「使用者列」）＝上界以內列之 `id`＋`nick_name`（text?）、`user_gender`（int?）、`user_phone`（text?）、`user_email`（text?）、`status`（int?）、`session_policy`（text）、`user_memo`（text?）、`password`（text）、`updated_at`（ts?）、`updated_by`（int?）、`deleted_at`（ts?）、`deleted_by`（int?）；欄型依 001 刀基線之欄定義；`user_name`、建立兩欄、`session_id` 不在面內（不可變／不經寫端改／清理句全域歸 NULL）；軟刪兩欄入面（基準內帳號被軟刪＝寫回未刪、指派隨回補；不入則已刪帳號帶回補之指派＝違 FR-014／FR-015 不變式）。
  2. **寫面擴充**（③b 同交易、次序固定）：`sys_user_role` 鍵集差刪除 → `BOUNDED_TABLES` 五表刪 `id >` 上界（`sys_user` 居末；指派先刪＝不撞 RESTRICT）→ `casbin_rule` 回補 → **指派對回補**（目標有而現況無、`ON CONFLICT DO NOTHING`、排在一切刪除之後）→ `sys_role` 回寫 → **`sys_user` 可變欄回寫**（句形同角色列：`UPDATE sys_user SET <欄> = <值> WHERE id = <N> AND (<欄>) IS DISTINCT FROM (<值>)`；含密碼雜湊與審計欄＝改回值≠改回痕）→ 五支 `setval`。清理面擴列 `sys_pwd_custody`（全表清空、無序列＝`RESTORE_SEQUENCES` 維持五支）；`setval` 合計基準檔模式 10 支、seed 模式 6 支。`RESTORE_REDIS_PREFIXES` 增 `cpwd`（改密節流鍵之獨立前綴、R11；安全帶「前綴鍵數非 0 即拒」隨之涵蓋）。重啟句判準不變（`sys_user` 與指派回寫不需重啟——角色成員每請求自庫讀）。
  3. **(a) 遷移帳前置**（基準檔模式）：任何寫入前以單句現讀 `seaql_migrations`、與基準檔 `migrations` 不等＝rc 2、零寫入；訊息指名兩向差集並指示：走查前＝重拍；走查已發生而無同遷移狀態之基準＝改跑 `restore --seed`。時點＝結構安全帶之後、system_settings 比對與門鈴、重啟句之現讀之前。`diff` 另報「遷移帳」面；snapshot 時現庫遷移帳≠repo 清單＝stderr 告警（rc 仍 0：stack 重起即套用、此基準隨即失效）。
  4. **(b) 合成**：
     - **語意**：期望 seed＝凍結 COPY ⊕ 演進帳 `seed_*` 依帳序逐筆——`seed_add` 全欄附列、新列 id 大於該表期望序號時期望序號推至該 id 且 `is_called` 真（GR9＝R13）；`seed_update`／`seed_delete` 以 pk 恰命中一列改或刪；命中≠1、欄不在段、值型不支援＝rc 2；`add_column`（nullable 無 default）補 `\N`、帶 default 或 NOT NULL＝`GateError`（第 5 款②）、`add_table` 不在合成面。
     - **單一來源**：執行期依路徑以 `importlib` 載入 `tools/schema-gate.py`，取 gate2 期望 seed 之同一合成鏈（`normalize_seed_dump` → `apply_seed_entries`，GR9 含於其內）施於凍結 seed，再以既有解析件（`seed_restore_target`、`seed_settings`）讀合成文字——不寫第二份合成；先例＝`tools/route-artifact-gate.py` 執行期載入 `tools/fork-delta-lint.py` 之名冊載入器。載入失敗或 `GateError`＝rc 2、原訊息照轉。餵入登記只取合成面之表（seed 模式＝`system_settings`∪角色／選單域五表∪`sys_user`；基準檔模式＝`system_settings`），他表登記（含未內建之 `add_table`）不擋；各筆只作用於自表 COPY 段與自表序列＝逐表獨立（濾與不濾於合成面結果全等、自測釘）。
     - **左源**：seed 模式目標態與兩模式之 `system_settings` 比對左源一律取合成文字；`check_settings_against_seed` 判準不變（值≠合成值才 rc 2、補救照指 002 刀寫端）；`check_seed_evolution` 之 `system_settings` 腿與角色／選單域腿刪除。
     - **repo↔現庫遷移同步前置**：合成面之表於演進帳有 `seed_*` 登記時才驗——repo 清單≠現庫遷移帳＝rc 2、零寫入、指名未套用與 repo 外之遷移（補救＝重起 stack 讓 migrate 服務套用〔需 user 放行〕或切回對應分支）；無涉表登記＝不驗。**repo 清單**＝解析 `rust-api/migration/src/lib.rs` 之 `migrations()` 向量內 `Box::new(<模組>::Migration)` 依序之模組名，並斷言各有 `mod <模組>;` 與同名 `.rs` 實檔（`DeriveMigrationName` 取檔名主幹＝`seaql_migrations.version`；001 刀重放實證記錄名＝`m0001_baseline_schema`／`m0002_baseline_seeds`）；零命中或不一致＝rc 2。
     - **交叉對賬**：`tools/docsync/snapshot.py` 之 `seed_account_projection` 為獨立重寫之同語意實作；自測以合成登記（`sys_user`／`sys_role`／`sys_user_role` 三 kind 各一）餵兩者，本工具合成面投影至 `USER_KEYS`／`ROLE_KEYS`／`BINDING_KEYS` 須與 docsync 投影逐節全等（以套件匯入 `docsync.snapshot`）。
  5. **仍拒跑之演進形（兩種）**：①清理面各表（本刀起含經手表）之 `seed_*` 登記——seed 模式照舊 rc 2 指名（整表清空以 seed 恆零列為前提）；基準檔模式由既有安全帶兜住。②合成面表之結構演進屬 schema 閘合成未內建之形（`add_column` 帶 default 或 NOT NULL；`add_table` 不在合成面＝不擋）——共用合成鏈與 gate2 同時 rc 2、於 `tools/schema-gate.py` 同一擴充點補齊即兩者同時恢復（不須另擴本工具）。user 2026-10-05 裁定時之選項所述「之後每支 migration 都不必再處理」（spec FR-057 (b) 與 Edge Cases「仍拒跑之演進形」承載）之射程即此：`seed_*` 演進（含系統設定）不再要求擴本工具；其餘拒跑屬前置不符（基準遷移帳不等、repo↔現庫遷移不同步），重拍或套遷移即解；基準檔每逢遷移須重拍（(a) 擋之）。
  6. **輸出面**：`render_diff` 摘要增「使用者列」「遷移帳」；`password` 欄差只報「不等」、不印值。基準檔含 seed 帳號密碼雜湊，落 gitignored 工作區（RUNBOOK §9c 既有落點）；自測之雜湊欄用非 PHC 形佔位字面（RL-0054）。
  7. **自測合成案與變異點**（零 docker、subprocess 全樁；拆所驗之腿即紅）：
     - US6 場景 3：seed 指派被刪、新帳號列與其指派、seed 帳號暱稱與密碼雜湊被改、基準內自建帳號被軟刪（指派同交易硬刪）、經手列與 `cpwd:` 鍵殘留 → 收尾 rc 0（被刪帳號寫回未刪、指派回補）；變異＝拆指派回補、拆軟刪兩欄回寫、`sys_user` 出上界名冊、拆使用者列回寫、經手表出清理面、`cpwd` 出前綴名冊，各令 rc 1 並歸因於對應面。
     - 場景 4：基準遷移帳少於現況 → rc 2、零寫呼叫、訊息含差集與重拍指示；變異＝拆前置＝交易照送。
     - 場景 5：形同 m0003 九筆（data-model §9）之合成登記＋已套用＋殘列 → 目標態＝列 44 不在、列 164 在、列 58～63 受保護、序號 164，收尾 rc 0；變異＝拆合成（目標退回凍結 seed）＝restore 照跑後收尾 rc 1、歸因授權列面（列 58～63 protected 不等、列 164 缺、列 44 多）；另以 monkeypatch 拆共用鏈之序號推進一形，證上界 164 高於目標序列 163 被前置拒跑 rc 2。
     - 場景 6：repo 清單三支而現庫兩支、涉表有登記 → rc 2 指名未套用之遷移；變異＝拆前置＝照跑。
     - 場景 7：`system_settings` 增鍵、改值、刪鍵各一且已套用 → 兩模式各跑、值＝合成值不報差不拒跑；變異＝拆合成＝兩模式報值≠seed 而 rc 2。
     - 邊界與真 repo：清理面各表登記照舊拒跑（逐表含 `sys_pwd_custody`）；他表 `add_table` 不擋；lib.rs 解析結果＝`m[0-9]{4}_*.rs` 實檔主幹集且非空；真凍結 seed ⊕ 真演進帳之合成可解且各上界不高於其序列（不釘實值）；docsync 交叉對賬案。
     - 既有釘案翻轉並改 doc：「`sys_user` 多一列不碰、收尾照報」→刪列且 rc 0；「seed 指派對被刪不在回補射程＝rc 1」→回補且 rc 0；`system_settings` 與角色／選單域有登記即拒之兩案→合成形；`RESTORE_TABLES` 釘值擴 `sys_pwd_custody`；「他表登記不擋」樣本（現取 `sys_user` 之 `seed_update`）v4 落入合成面＝換成合成面外之表。
  8. **RUNBOOK §9c 改寫要點**（工具 docstring 為唯一人寫家、§9c 只寫契約）：①v4 三新欄、v3 rc 2 ②第 3 步前置句改「左源＝凍結 ⊕ 演進合成、值≠合成值才 rc 2」、刪「有登記即拒跑」③清理面「五表」→「各表（本刀起含經手表）」、前綴增 `cpwd:`、`setval` 十支／六支 ④③b 加使用者上界、指派回補、使用者列回寫與其次序 ⑤(a)(b) 兩條拒跑與補救 ⑥seed 模式差處改為合成目標、演進形拒跑只剩兩種（第 5 款）⑦射程界改寫（指派對被刪入射程；軟刪兩欄入列面、`session_id` 不在）⑧第 5 步判準與退出碼清單 ⑨具名排除兩形與「走查寫入一律對自建帳號」（spec SC-008）⑩m0003 進 dev 庫之時機隱性與「套用後即重拍」。同批面＝工具 docstring、README 工具樹該列、RUNBOOK §12 速查該列（「清理面五表」「角色／選單域五表」與 v3 字面依 RL-0011 四形種子掃——`sys_user` 入上界面後後者之數量詞與域名同改）。
  9. **單元次序**：U1 早於 U4 與 U22。compose 之 migrate 服務於每次 stack 啟動自動套用未跑之 migration（rust-api 依賴其成功結束）＝m0003 檔一入工作樹、任一次重起即入 dev 庫，故 (a) 須早於撰寫 m0003。U1 收尾以現庫取 v4 基準（唯讀），供至 U4；U4 收尾經放行重起套 m0003 後，(a) 令該基準拒跑、即重拍本刀基準（其後走查與 CDP 用之）。
- **Rationale**:spec FR-057（含 user 2026-10-05 裁定 seed 模式本刀做、同日納入系統設定）、US6 場景 3～7、SC-008；Edge Cases「以 m0003 之前之基準還原＝半新半舊、遷移帳仍記 m0003、無工具修路」已由主線以 006 刀終態基準之純函式模擬實證——寫入前以遷移帳擋下是唯一不留混合態之點。合成取 schema-gate 同鏈：gate2 為期望 seed 之權威，第二份實作即第二份真相；濾表使本工具不因無關表之未內建 kind 連坐。
- **Alternatives considered**:①遷移帳不符時自動重放或反向遷移——越過 migrate 服務寫 dev 庫，棄。②自持一份合成（docsync 形）＋交叉對賬——GR9 須寫兩次、多一份須同改之實作，棄。③repo 清單取目錄 glob——未註冊之檔被誤計，棄。④同步前置一律驗——零登記亦新增拒跑面，棄。⑤`sys_user_rows` 只存 seed 三帳——須另立 seed 識別條件、與角色列「取樣時已在之列」口徑分岔，棄。⑥清理面登記亦合成（只刪非 seed 列）——整表清空之單句語意即失，棄。⑦`sys_user_rows` 不含軟刪兩欄——基準內非 seed 帳號被軟刪即不還原、且指派回補成已刪帳號帶指派＝違 FR-014／FR-015，棄。⑧合成只餵 `seed_*`、濾除結構類 kind——合成面表加欄後指涉新欄之 `seed_*` 即因凍結 COPY 段無此欄而 `GateError`＝反製造拒跑面，棄。

## R17 機器守

- **Decision**:
  1. **新碼面閘 `tools/zh-tw-lint.py`**（ADR⑪；判準內容之家＝R19；本節定登記面，逐項對照 006 刀 `tools/seed-view-gate.py`）：子命令 `check`（預設；掃 `base-web/src/locales/langs/zh-tw.ts`）／`test`；rc 0／1／2／64；純標準庫、零 docker、無環境跳過分支（讀面缺席或零鍵＝rc 2；RL-0051）；index 落 100755（drvfs 以 `git update-index --chmod=+x`）。登記面：
     - RUNBOOK §12 碼面閘表一列（GT-12 碼面閘表腿：`tools/` 頂層 tracked `*.py` − `NON_GATE_TOOLS` ⇔ 表首欄雙向對賬＝不入表即紅；表 9→10 列）＋工具鏈速查一列；`tools/docsync/gates.py` 之 `NON_GATE_TOOLS`（三支）與閘數 12 不動（碼面閘不占 GT 名額）。ADR-00032 翻案觸發器①（碼面閘 ≥8 支＝另立生成檔並翻案）本刀前 9 支已成立、未處置，本刀後 10 支：複核狀態入 ADR-00084、處置轉 BL-00142（另批評估生成檔或續行人寫表）。
     - `.githooks/pre-commit`：條件段觸發 `-e 'base-web' -e 'tools/zh-tw-lint.py'`、命令 `python3 "$HOOK_DIR/../tools/zh-tw-lint.py" check`（外層 staged 面只見 base-web gitlink＝「該檔 staged 時跑」以 pin bump 實現）；`for t in` 自測迴圈名冊加本檔；檔頭段序與「七支碼面閘」段註改八支。
     - `tools/docsync/tests/test_hook_wiring.py`：`SEGMENTS` 增一元組、`MIRROR_WORDS` 增 `"zh-tw-lint"`、模組 doc「十三條件段」改十四；三處人寫鏡像（pre-commit 檔頭段序、README 樹 `.githooks/` 列、README 守門條目）各恰一次。
     - `tools/bootstrap.sh`：自測名冊自 `git ls-files ':(glob)tools/*.py'` 推導＝入 tracked 即入冊、推導行零改；「七支碼面閘」註解改八支並列名。
     - README 工具樹一列、活書 05 `tools/` 列、`docs/ops/reference-src/code-gate-contracts.md` 新節 §8「`tools/zh-tw-lint.py` 行為契約」。
     - `submodule-sync` 段之 base-web 閘面已含 `src/locales/langs`＝本閘讀面已在內、`check_sync_paths` 等式零改。
  2. **新腿**：
     - **包含規則呼叫點名冊**（`tests/authz_entrypoint_lint.rs` 腿⑦；ADR②）：`NO_ESCALATION_CALL_FILES`＝[`handler/throttle.rs`, `handler/user.rs`]，`guard_no_escalation` 生產使用點檔集須恰等名冊（共用判決式 `verdict`、使用點偵測沿 `use_lines`＝RL-0026 三形聯集扣 `fn` 定義處）；`handler/user_center.rs` 不在冊（自助面無他人標的）；檔頭腿表增一列。
     - **msg-key-gate 斷言 2 擴認 `BizData`＋`BIZ_DATA_KEYS`、斷言 3 名冊 1→3**：見 R14 第 8 點。**wire 裁判名冊與偏離帳**：見 R14 第 3、4 點。
     - **obs 名冊雙向**（`rust-api/server/src/obs.rs`）：`THROTTLE_DEGRADED_SOURCES: [&str; 10]`→11（增 `redis_change_pwd`；ADR⑤）；預註冊案 `pre_register_renders_throttle_degraded_ten_sources_explicit_zero` 之「恰十」與案名同批改十一（案名亦屬數量詞面＝RL-0011），`degraded_emit_literals_across_src_stay_within_roster` 自動涵蓋 `throttle/change_pwd.rs`；`throttle/mod.rs` 測試 `warn_degraded_increments_each_of_the_ten_sources` 同批改名 `…_eleven_sources`（R11 決定 3）。新計數族 `password_policy_invalid_total`（無 label；ADR⑥）比照 `ipgate_blocked_total` 兩腿：出口 `obs::password_policy_invalid()` 生產面恰一處呼叫＋一處宣告、序列名字面只在 `obs.rs` 兩處（預註冊 0＋出口 +1），各配真檔文字之記憶體內變異反例。告警規則 `obs016-password-policy-invalid`（`deploy/grafana-provisioning/alerting/rules.yml`）無碼面閘、依既有活體驗證慣例實測（contracts/code-gates.md §7）。
     - **schema-gate GR9**（本體＝R13）：正例（新列 id 高於期望序號＝推至該 id、`is_called` 真）、反例（不高於已發出最大值＝不動）、變異（拆推進＝m0003 九筆合成之期望與合成 dump 比對轉紅；spec US6 場景 2）。
     - **走查還原工具 v4**：見 R16（非碼面閘、`NON_GATE_TOOLS` 成員、不掛條件觸發；自測入 pre-commit 迴圈與 bootstrap 名冊照舊）。
  3. **既有閘之名冊擴列**（依判決形兩類、tasks 逐項明列）：
     - **集合恰等類**（漏列即紅＝擴列與接線同 commit）：`NO_ESCALATION_CALL_FILES`；`tests/contract.rs` registry 與兩道覆蓋閘 49→61；`AUDITED_*_DEFS` 與節謂詞；`DEVIATION_LEDGER`；`MSG_KEYS`⇔三檔 backend 子樹；`FRONTEND_MSG_CONSUMERS`；`THROTTLE_DEGRADED_SOURCES`；`src/router.rs` 之 `routes_block_literal_form_and_pinned_rows` 與 `tools/docsync/tests/test_references.py` 之 `TestRoutes::test_real_repo_pinned_rows`（+12 列；LL-00060）；RUNBOOK §12 碼面閘表；`SEGMENTS`。
     - **漏列靜默類**（不轉紅、只留缺口）：`handler/common.rs` 之 `each_domain_keeps_its_own_log_literals`（逐域元組表加使用者管理域與個人中心之拒寫 target／欄名／訊息文字與 body 收斂訊息）、`handler/ip_rule.rs` 之 `production_code_emits_no_degraded_field`（`include_str!` 檔表只加 `user_center.rs`；`user.rs` 承載會話面降級腿不入＝R6 第 5 款）——兩表以 `("<名>.rs"` 形指名新檔、使其入 `tests/test_module_tail_lint.rs` 判準①射程；`tests/contract.rs` 之 `role_and_menu_write_refusals_add_no_context_absent_leg_real_seed` 寫端清單 14→23（加使用者寫端 8 支與 changePassword；操作者缺席每發仍 2 格；案名改 `write_refusals_add_no_context_absent_leg_real_seed`＝RL-0011 名稱面），其 doc 與檔頭「十四支角色／選單／授權寫端」同批改「二十三支角色／選單／授權／使用者／個人中心寫端」；`tests/entity_access_lint.rs` 射程自動涵蓋新檔（無名冊）。
  4. **反向確認**：
     - **BL-00108**：本刀不動 `tests/entity_behavior_lint.rs` 與 `tests/wire_i64_guard_lint.rs`（R14 第 5 點；零 entity 變更），腿⑦沿既有 `use_lines` 與 `tests/common` strip 引擎、不新寫第三份字元級零件（`skip_ws`／`ident_at`／`close_of`／`split_top`／`peel_attrs`／`attr_spans`／`token_positions` 族）＝兩觸發形皆未成立；收刀以 `git -C rust-api grep -l -E 'fn (skip_ws|ident_at|close_of|split_top|peel_attrs|attr_spans|token_positions)\b' -- server` 之輸出仍恰為該兩檔（自起點 pin 零增）佐證、入收單註記。附記：m0003 落 `rust-api/migration/src/`＝`entity_behavior_lint` 之 migration 掃描面（FK 集取全部 migration 文字並集），其 SQL 常值不得含 `REFERENCES`／`FOREIGN KEY`／`DROP CONSTRAINT` 字樣。
     - **授權重載**：`RELOAD_CALL_FILES`＝[`handler/menu.rs`, `handler/policy_archive.rs`, `handler/role.rs`] 零擴列；植入案 `planting_reload_use_turns_leg_one_red_outside_exempt_faces` 增兩發——分別植 `reload_enforcer` 呼叫於 `handler/user.rs`、`handler/user_center.rs` 生產面，實得檔集＝名冊∪植入檔即紅＝使用者域寫端零重載之反向確認測試。
     - **腿⑤後半**：`advisory_lock_user` 生產使用點擴至 `handler/user.rs`、`handler/user_center.rs`、`handler/throttle.rs`（unlockLogin 帳號維），三檔皆不在 `DOMAIN_WRITE_SIDE_FILES`（8 檔、不變）＝零交集維持綠；指派寫端呼 `sys_role::find_active_by_id_for_update` 不在該腿判準（只看 advisory 使用點）；`DOMAIN_LOCK_CALL_FILES` 不變（指派寫端不入選單域＝FR-011）。
     - **前端面**：不新增 view 目錄＝`route-artifact-gate` 零重算、`seed-view-gate` 零改；`view-render-guard`（射程 `views/manage`）涵蓋使用者頁記事欄純文字插值（FR-019），`views/user-center` 在射程外而改密卡不渲染自由文字＝射程不擴（以改密卡模板被禁字面 `grep -c` 為 0 佐證）。
  5. **每閘一正一反自證**（RL-0080；變異打在判準上）：zh-tw-lint＝真檔綠＋植簡體字、植禁用語、白名單字面越出具名鍵、單會話語境誤用「踢除」、字表完備腿植未分類字各 rc 1，兩表相交與讀面缺席 rc 2；腿⑦＝真樹綠＋他檔植一處呼叫即紅、記憶體內自 `handler/throttle.rs` 拔除即紅（名冊有而樹無）；msg-key-gate＝`BizData` 動態鍵、名冊外鍵、`BIZ_DATA_KEYS` 外鍵各 rc 1，合法形、enum 宣告與 match 樣式不計；前端名冊＝拔請求層一處字面即 rc 1；wire_schema＝兩新節各植一支未入冊型即紅、第三列四類植入反例；obs＝出口兩腿之真檔記憶體變異；GR9、走查工具、守衛＝R13、R16 第 7 點、R15 第 1 點。
- **Rationale**:spec FR-022、FR-034、FR-037、FR-054、FR-061、FR-064、SC-002、SC-009；ADR②、ADR⑤、ADR⑥、ADR⑪；名冊判決形分兩類承 006 刀 research R13——集合恰等類擴列與接線同顆，漏列靜默類須逐項明列，否則新域之 log 字面與 degraded 欄靜默無守。
- **Alternatives considered**:①zh-tw 檢查只做一次性收刀腳本——本刀起每刀三語同批、無機器錨即持續退化，棄。②zh-tw-lint 掛子庫 `.githooks-submodule/pre-commit`——子庫 hook 現只承機密掃描、新開接線形與鏡像面，棄。③包含規則只靠逐消費點負向測——新增未接線之寫端無人知，棄。④沿 `rev5:` 立 finish 名冊閘——失效名單寫入已由每支撤票端點之測試承載，棄。⑤`view-render-guard` 射程擴至 `views/user-center`——無自由文字渲染、無承重對象，棄。

## R18 前端

> 射程：使用者頁（★`BASE-WEB-MANAGE-PAGE-WIRING` (v)）、個人中心改密卡（(vi)）、IP 規則頁來源 IP 解鎖（(vii)）、角色與選單頁按鈕碼（(viii)）、登入表單（★`BASE-WEB-LOGIN-CAPTCHA-WIRING` (ii)）、請求層明細轉譯（★`BASE-WEB-I18N-WIRING` (i)）；繁中 runtime 見 R19。對應 spec FR-024／FR-038／FR-040／FR-047～FR-054；碼面現況取 base-web pin `fb4dac2`，藍本取 `rev5:` base-web HEAD（R3；該批檔於 `rev5:007` 收刀後零 commit＝22080 即 as-built）。前端零測試框架 ⇒ 驗收＝容器內 `pnpm typecheck`＋機器斷言＋兩段 review＋CDP 對照。

- **Decision**:
  1. **使用者頁 index（(v)；`src/views/manage/user/index.vue`）**——`rev5:src/views/manage/user/index.vue` HEAD 形重打字，只換本刀拍板處：
     - 資料源：api 依回收桶開關切兩支——現役 `fetchGetUserList`、已刪 `fetchGetDeletedUsers`（只收 `{current, size}`、自持分頁參）。現役**整份送出搜尋參**（後端六欄皆濾；`rev5:` 之「逐欄只送四欄」不帶回）；搜尋參之 ref 型沿 upstream `Api.SystemManage.UserSearchParams`（搜尋卡 `v-model` 雙向指派、`user-search.vue` 之模型型別行免改），整份送入型為 `Api.UserAdmin.UserListQuery` 之包裝參數＝單向可賦值（窄型賦寬字串型；反向不成立——`status`／`userGender` 為寬字串、不可回賦搜尋卡模型；本刀 U17 實作勘正）。
     - 回收桶：表頭 `#prefix` 插槽之 NSwitch「顯示已刪除」（005 刀 menu 頁同形；開關不掛碼＝rev5 HEAD 形，未授 getDeletedUsers 者切換得 `5003`）；切換即清勾選並回第一頁（`rev5:B-100` 同形）；已刪模式 `<UserSearch v-if="!showDeleted">`、操作欄整欄換「復原」（`user:restore`；確認框兩行＝確認句＋「復原後需重新指派角色」）、不加刪除時間欄。
     - 欄集：基線九欄＋角色、會話政策、記事、建立時間、建立者、更新時間、更新者七欄（與 rev5 HEAD 同集同寬）。角色欄＝`row.roles` 之 `roleCode` 以 `page.manage.user.roleSeparator` 串接（各頁自備鍵、不跨頁借鍵＝rev5 對 rev4 防回歸要點；`page.passwordPolicy.listSeparator` 只供違規碼串接）；記事欄不設 render（純文字插值）；時間欄原樣顯示 RFC3339；性別欄收斂為「非 `'1'`／`'2'` 即不渲染」。操作欄寬 130→200，**`:scroll-x` 962→2002＝Σ(width｜minWidth)** 同批改（與 rev5 HEAD 同值）。
     - 七碼逐鈕（spec FR-048）：表頭新增與批刪走既有 prop——`:show-add="!showDeleted && hasAuth('user:add')"`、`:show-delete="!showDeleted && hasAuth('user:delete')"`，**不覆寫 default 插槽**（`rev5:B-099` 之保底 div 形不帶回）；列鈕：編輯 `user:edit`、刪除 `user:delete`、復原 `user:restore`；列操作下拉（觸發鈕 `common.action`）收「踢除下線」`user:kick`、「重設密碼」與「隨機密碼」`user:reset-pwd`（**本人列不列此兩項**——其拒因是改道指引）、「解鎖登入」`user:unlock`；選項集空即不渲染下拉；本人列之踢除、刪除、解鎖照列、拒因交後端；下拉鍵以字面聯合型承載。
     - 浮層：標的列於開浮層時鎖定（不回讀清單）；踢除確認＝NModal dialog preset，成功只出 toast；重設成功刷新當前頁（更新時間與更新者會變）；解鎖成功只出 toast。
  2. **新增／編輯抽屜（(v)；`user-operate-drawer.vue`）**——rev5 HEAD 形防護全帶、只換 Q13 一處：
     - 候選：`fetchGetAllRoles` 改自 `@/service/api/rev6-role-admin` 直接路徑匯入（兩份同名 fetcher 擇 rev6 包裝、barrel 之 upstream 版一行不動）；選項值＝角色 id、**全列不過濾**（含 R_SUPER；前端不預判包含規則＝FR-024）。
     - 請求世代守 `roleOptionsReq`（過期回應一律丟棄）＋讀取態 `roleOptionsState` 三態（`loading` 只停用不出字；`failed` 停用並出 `page.manage.user.roleOptionsUnavailable`）；每次開抽屜重置候選、快照與讀取態（抽屜從不卸載）。
     - **灰色保留選項取代 `rev5:` 之 `unresolvedRoleCodes` 鎖**（Q13；FR-020）：清單列已帶持有角色 id 與名稱 ⇒ 編輯初值 `roleIds` 取自 `row.roles` 之 id、同步落定（不再等候選做 code→id 映射）；持有而不在候選（＝停用）者另立選項——標籤＝角色名＋`page.manage.user.roleDisabledTag`（「（已停用）」）、`disabled: true`（內建灰階、下拉點不選＝不可新選）。naive-ui 2.44.1 之 NSelect 預設標籤對停用選項不給關閉鈕（`_internal/selection` 之 `closable: !option.disabled` 實讀）⇒ 以 `render-tag` 自繪標籤、關閉鈕只隨選擇器整體停用與否（＝可移除；移除後灰項仍見於下拉、不可再選）；未移除即隨初值保留。讀失敗態下拉停用、仍顯列上持有角色、送出恆不帶 `roleIds`。
     - 送出：`status` 與 `roleIds` **只在改動時才帶**（狀態＝非本人鎖且值異於列；角色＝非本人鎖、讀取態 ready 且集合不等）——防並行編輯以舊值把他人剛停用之帳號啟用回來或蓋掉他人之指派；更新端可空文字欄經 `blankToNull`（後端亦歸一、畫面零差）。會話政策**僅編輯態渲染**，非超管（`authStore.userInfo.roles` 不含 `R_SUPER`）停用並出 `sessionPolicyHint`；第二支呼叫 `fetchUpdateUserSessionPolicy` 之門＝超管且值有變（寫在提交面、不倚賴 `:disabled`）；其失敗時先 `emit('submitted')` 讓清單顯示已生效之 updateUser、抽屜留原地。本人列（`String(row.id) === authStore.userInfo.userId`）之狀態與角色控制項停用；帳號名編輯態停用、組 body 不帶 `userName`（型別容 `userName?: string | null`＝wire 可達形、出現即拒；契約＝contracts/wire-user-admin.md）；表單模型自持、逐欄回填。
     - 密碼欄僅新增態：必填＋`passwordHint` 提示（不掛即時規則＝FR-038 末句）＋「隨機密碼」鈕開產密浮層、帶入即填欄；**關閉即清明文**（`watch(visible)` 之 falsy 邊、涵蓋叉、遮罩與 ESC）。
     - path 修正兩處：`email`→`userEmail`、`roles`→`roleIds`（修改型；基線兩處非模型欄名、掛規則即落空）。
  3. **搜尋卡（(v)；`user-search.vue`）**：拔除手機、信箱兩欄之 `patternRules`（Q17；`patternRules.phone` 只收中國大陸 11 碼、部分字串亦被擋）；連帶不再使用之型別與匯入同批移除或改寫（typecheck 與 oxlint 綠為準）；`validate()` 保留（無規則即恆過）。本檔自 rev5 零 diff 轉為修改型＝刻意分岔（`rev5:B-143`）。
  4. **重設密碼浮層與產密浮層（新檔）**：
     - `src/views/manage/user/modules/user-reset-pwd-modal.vue`：自 rev5 HEAD 之 index 內嵌浮層抽成新檔（index 修改面縮小＝rebase 緩解）；輸入欄**掛即時規則**＝`usePwdPolicyRules().buildPolicyRules(policy, () => 標的列帳號名)`（清單列之 `userName` 即登入帳號名、`forbidUsername` 於此有效）；送出鈕空值停用；失敗時浮層留著、值不清（就地改）；關閉即清明文；接受產密帶入之預填值，帶入後仍須按確定（改他人密碼不可逆、多一次確認）。
     - `src/components/custom/pwd-gen-modal.vue`：props＝政策七鍵投影（`null` 即以後備界 8／64、偏好長度 16）＋標的帳號名；零網路請求；`crypto.getRandomValues`＋拒絕取樣消模偏差＋Fisher–Yates 洗牌、依必含類別構造；長度可調（界＝政策上下限；矛盾政策以下限為準、後端仍是唯一裁判）；複製如實回報成敗；「帶入」以 emit 交掛載端；鍵 `page.manage.user.pwdGen.*`（元件住 components/custom、唯一掛載面在使用者頁、鍵隨消費場景）。
  5. **列解鎖（帳號維；(v)）**：下拉「解鎖登入」→ dialog 確認 → `fetchUnlockLogin({ dimension: 'user', userName: row.userName })`（帳號名原樣、零 trim；`dimension` 逐分支顯式帶）；清單不顯示鎖定狀態、每列可按、對未鎖帳號後端回成功並落一筆稽核（GR3）；鍵 `page.manage.user.unlockLogin*`（鈕標籤、確認句、成功句）。rev5 頁首雙維浮層 `user-unlock-modal.vue` 不帶回（Q9；刻意分岔登記）。
  6. **IP 規則頁來源 IP 解鎖（(vii)）**：`src/views/manage/ip-rule/index.vue`（rev6 自有檔、整檔新增型）表頭 `<TableHeaderOperation>` 改對標籤，`#prefix` 插槽掛「解鎖來源 IP」鈕（`v-if="hasAuth('ipRule:unlock')"`；碼由 m0003 增）→ 新檔 `modules/ip-unlock-modal.vue` 單欄位址字面（只驗必填、形制交後端 `biz.throttle.invalidUnlockTarget`）→ `fetchUnlockLogin({ dimension: 'ip', target })`（與帳號維**共用 `rev6-user-admin.ts` 同一支包裝**；來源維欄名為 `target`、非 `ip`）；開啟即復位；不套包含規則（後端判）；表頭既有兩 prop 錨值不動。該頁表頭上方註解「標籤保持自閉合、不覆寫預設插槽」改寫為現行判準。鍵 `page.manage.ipRule.unlock.*` 落 `page.manage.ipRule` 子樹——該子樹整棵在 (i) 既有圈界內（zh-cn／en-us／`app.d.ts` 實讀）⇒ 以巢狀 (vii) 新增型圈界一塊承接（塊首塊尾帶 `MANAGE-PAGE-WIRING(vii)+ 007-user-password-admin`、(i) 塊首尾與理由句不動；lint 圈界排除以深度計、允許巢狀）；巢狀塊之機器守＝範圍欄對賬腿之 (vii) 塊數（PATCH 實數化後生效）——拔其標記不觸發未圈界（外層 (i) 塊與之同一 change-block、`find_unmarked_additions` 見塊內有標記即放行）；U18 出口以通則⑤字面逐檔計數恰 1 入 commit 訊息（`contracts/code-gates.md` §1.5）。
  7. **角色頁與選單頁按鈕碼（(viii)）**——對碼照 spec FR-048：
     - 角色頁 `role/index.vue`：表頭 `:show-add="hasAuth('role:add')"`、`:show-delete="hasAuth('role:delete')"`；操作欄編輯 `role:edit`、刪除 `role:delete`；`useAuth` 匯入與取用為新增型。角色抽屜三顆授權鈕不設碼。
     - 選單頁 `menu/index.vue`：表頭兩 prop 改為 `!showDeleted && hasAuth('menu:add')`／`!showDeleted && hasAuth('menu:delete')`（改寫 005 刀既有附加屬性行、同一變更塊、不增 `原行:`；該標記理由句「已刪模式不顯新增與批刪」同批補按鈕碼）；現役操作欄新增子選單 `menu:add`、編輯 `menu:edit`、刪除 `menu:delete`；回收桶「復原」不設碼。
     - 「門在頁級」碼註改寫：`role-operate-drawer.vue` 之 (iii) 既有圈界首行（「三鈕都不掛按鈕碼判斷，能進角色頁即可用（門在頁級）」）與 `menu/index.vue` 回收桶復原之 (ii) 標記理由（「此頁的門是頁級超管授權」）同批改為現理由——三彈窗與選單回收桶之讀寫皆屬封死集、非超管連現況或已刪清單都載不出（ADR-00068 款 10 形；brainstorm 工程判斷⑬）；`policy-archive/index.vue` 之同類句續真、不改。
  8. **個人中心（(vi)）**：`src/views/user-center/index.vue` 兩行基線（`<script setup lang="ts"></script>`、`<LookForward />`）改為修改型——前者之標記置於 SFC 頂層單行 HTML 註解（原行含 script 收尾標籤、不可入 script 區）；只掛新檔 `modules/password-card.vue`、其餘卡位留白；入口沿頭像下拉（`user-avatar.vue` 零 diff）；零角色帳號經自助路由白名單可達（R12）。改密卡：舊密碼一路；新密碼規則＝`buildPolicyRules(policy, '')`＋新≠舊（訊息借 `backend.biz.user.passwordSameAsOld`）；確認欄 `createConfirmPwdRule`；成功 toast `page.userCenter.password.success`、清欄；掛載即 `ensureLoaded`。★`forbidUsername` 即時提示**結構性缺席**：前端唯一可得之 `userInfo.userName` 為 `nick_name` 退 `user_name` 之顯示名（`handler/auth/user_info.rs` 現讀），綁它即對有暱稱者比錯對象；本刀無個資讀端（BL-00141）⇒ 父層刻意不綁帳號名、該條交後端單一驗證點（rev5 同形）。
     - `src/hooks/business/pwd-policy.ts`（新檔）對外兩支：`usePwdPolicy()`＝政策投影之模組層單例快取（各消費點共用、一次登入只讀一次；唯一寫入者 `ensureLoaded`；讀失敗靜默維持 `null`）；`usePwdPolicyRules().buildPolicyRules(policy, userName)`＝七鍵投影→naive 規則（`null` 只回必填；四類字元正則與後端同界；`forbidUsername` 不分大小寫相等、帳號名空字串即略過）。規則訊息取 `page.passwordPolicy.violation.<碼>`（`maxBytes` 只見於後端明細）。快取只增不清＝SPA 存活期政策被改時提示用舊值、後端照新值裁決（已知態）。
  9. **登入表單（LOGIN-CAPTCHA (ii)；`pwd-login.vue`）**：`rules` computed 內三行基線改修改型——`const { formRules } = useFormRules();` 改取 `createRequiredRule`；`userName: formRules.userName,`、`password: formRules.pwd` 改為只驗必填（`form.userName.required`／`form.pwd.required`）。`reg.ts` 零 diff、register／reset-pwd 不動、三顆快速登入鈕零 inline（BL-00049）、captcha 軟區零變更。碼註照實寫規格：`REG_USER_NAME`＝`/^[\u4E00-\u9FA5a-zA-Z0-9_-]{4,16}$/`（4～16 字、限 U+4E00～U+9FA5 之漢字與英數、底線、連字號）、`REG_PWD`＝`/^\w{6,18}$/`（6～18 字英數底線）；後端帳號名形制 `^[A-Za-z0-9_-]{1,64}$`、密碼依政策且 ≤512 bytes ⇒ 兩欄前端正則皆會擋下合法輸入（`rev5:` 該處碼註「6~18 位英數底線」張冠李戴、不照抄）。003 刀軟區圈界首行碼註「★(ii) formRules 放寬不在授權內、不動」同批改現在式。
  10. **請求層明細轉譯（I18N (i)；`src/service/request/index.ts`）**：沿單一 helper，簽章擴為 `translateBackendMsg(msg, detail?)`；明細只認兩鍵——`biz.user.passwordPolicy`：`detail.violations` 逐碼經 `$t('page.passwordPolicy.violation.<碼>', 碼)` 譯、以 `page.passwordPolicy.listSeparator` 串成 `{violations}`；`biz.user.pwdSetTooFrequent`：`{remainingSeconds}` 原值插入；兩鍵走 `$t(key, named, msg)` 三參（原文 fallback 照舊）；其餘鍵一律不讀 data（純 key）。只改 onError 業務碼分支之 toast 鏈（該處既有修改型行之內容、`原行:` 不變）；`7777` 對話框與 HTTP 層錯誤鏈不傳 data（兩鍵只以 `2222` 下發）；明細表與轉譯落 003 刀既有圈界內 ⇒ (i) 列之 2 處修改型＋2 塊新增型實數不變。兩鍵字面成為前端 msg 字面消費點 ⇒ msg-key-gate 之 `FRONTEND_MSG_CONSUMERS` 同批 +2 項（`service/request/index.ts` 各 1 次；R17）。圈界內註解「錯誤信封 `data` 恆 null、明細插值鏈不帶回」同批改寫。
  11. **API 包裝與型別**：新檔 `src/service/api/rev6-user-admin.ts`（11 支：清單兩支 GET＋params、刪除兩支 DELETE＋JSON body、其餘 POST＋body；含 `fetchUnlockLogin`＝BL-00091 之包裝面）與 `rev6-user-center.ts`（2 支）；不入 barrel、消費端直接路徑匯入、錯誤不加工（拒因由攔截層轉譯）。型別新檔 `src/typings/api/rev6-user-admin.d.ts`（`Api.UserAdmin`）／`rev6-user-center.d.ts`（`Api.UserCenter`）以 declaration merging 開節、既有 typings 零改；型名與欄形照兩支 wire 契約（`UserRecord.roles: UserRole[]`、`UnlockReq.dimension` 必給、`UpdateReq` 容 `userName?: string | null`〔出現即拒〕、`UserRecord` 結構性無 `password`／`sessionId`）。四支新檔落地＝U14（wire 裁判右源）、U17 起消費。`rev5-` 前綴檔與其宣告本體不帶回（R5）。新型入 wire 裁判受審名冊與節謂詞前綴擴認（R14、R17）。
  12. **i18n 鍵落點**：前端專用鍵一律落 `page:` 樹——`page.manage.user.*`（欄名、回收桶、確認句、下拉、`pwdGen.*`、`resetPwd*`、`unlockLogin*`、`roleDisabledTag`、`roleOptionsUnavailable`、`sessionPolicyHint`、`passwordHint` 等）、`page.userCenter.*`、`page.passwordPolicy.*`（違規碼八枚＋分隔符；圈界歸 I18N (i)）、`page.manage.ipRule.unlock.*`；`route:` 樹零新增；`backend:` 樹只放 `MSG_KEYS` 成員（msg-key-gate 斷言 1 與憲法 I18N (ii) 列兩道約束；`rev5:` 之 `backend.common.listSeparator` 與 `passwordViolation.*` 白名單形不帶回）。鍵全集、三語譯文與實數以 contracts 為準；鍵與其消費者同單元落地（`page:` 樹孤兒鍵無機器守）；三語同批（R19）。
  13. **fork-delta 落點**（憲法 §III；機器守＝`tools/fork-delta-lint.py`）：
     - 修改型逐行 `原行:`、標記與 `原行:` 同一行（lint 強制）；template 用單行 HTML 註解形（lint 剝行尾 `-->`、rev6 既有先例；`rev5:` 之多行形不帶回）。
     - **Vue 模板屬性行變體**：標記置於開標籤正上方、點名被改屬性、`原行:` 載一條真實被替換之基線行，新增屬性須與該行同一變更塊——使用者頁表頭（`/>`→`>`＋兩 prop＋`#prefix`，`原行: />`）、`:scroll-x`、`<UserSearch>` 加 `v-if`、抽屜各控件之 `:disabled`。角色頁表頭自閉合且無既有改點：兩 prop 排既有屬性之後、末個 prop 與自閉合符同行以取代基線獨行之 `/>`（`原行: />`）（以 `pnpm lint` 與 fork-delta-lint 雙綠為準）。
     - JSX 操作欄：JSX 子節點內放不了 `//` 標記、`{/* */}` 亦非 lint 所認之註解行 ⇒ 依 005 刀 menu 頁先例，標記置於 `render:` 行上方、`原行: render: row => (`，並使顯隱條件與既有鈕落同一連續替換塊（render 改區塊形、整段 JSX 隨縮排變動）。
     - 新增型：圈界 `[rev6-inline <軌道>(<用途>)+ 007-user-password-admin START]`／`END`；物件字面新塊**不插在末項之後**（上一行補尾逗號即被歸修改型＝005 刀陷阱）；既有圈界內之改動沿原塊標記（006 刀 role 抽屜先例）。
     - 新檔檔頭：lint 之檔頭區＝首個實質碼行之前的空白與註解行 ⇒ `.vue` 新檔首行即 `<!-- [rev6-inline <名>+ 007-user-password-admin] <理由> -->`（不可落在 `<script setup>` 之後）、`.ts` 新檔首行 `// [rev6-inline …]`；軌道名後緊接 `+`；自稱 §III.1 軌道時檔路徑須落其新增面（WRAPPER＝`src/service/api/rev6-*.ts`、ADAPT＝`src/typings/api/`）；名冊外之名（`MANAGE-USER-VIEW`、`MANAGE-IP-RULE-VIEW`、`USER-CENTER-VIEW`）不做名冊斷言。
     - 變更檔集斷言（FR-054）之授權集＝§III.2 全表檔級名單 ∪ 新增檔；`role-operate-drawer.vue` 只動 (iii) 既有圈界內碼註。
     - 單元出口：觸及含預估項之檔逐檔斷言實數＝範圍欄應有值；`hasAuth('<碼>')` 碼集以 grep 集合相等斷言（使用者頁＝`user:*` 七碼、角色頁＝`role:*` 三碼、選單頁＝`menu:*` 三碼、IP 規則頁含 `ipRule:unlock`）。
  14. **view-render-guard**：腿①射程＝`base-web/src/views/manage/**`，涵蓋使用者頁、重設浮層、IP 解鎖彈窗與角色選單頁（受掃檔 18→20）；`src/views/user-center/**`、`src/components/custom/pwd-gen-modal.vue`、`src/hooks/business/pwd-policy.ts` 在射程外、**不擴射程**——三者不渲染使用者可寫之自由文字（改密卡只呈標籤與密碼輸入、產密元件只呈固定字元集之 CSPRNG 產物），記事、暱稱等只在 `views/manage/user` 渲染＝射程內。腿②：IP 規則頁表頭加 `#prefix` 即違現行判準 (b)「自閉合」⇒ 同批改 (b) 為「標籤體內除具名插槽 template（`#prefix`／`#suffix` 及其 `v-slot:` 長形）與註解外零內容」，(c) 照舊；錨由單檔擴為具名常數 `ANCHORS`（路徑→兩屬性錨值）四頁：IP 規則頁（錨值不變）、使用者頁、角色頁、選單頁——四頁表頭自本刀皆以兩 prop 承載按鈕碼顯隱、同一失效類（覆寫 default 插槽即脫離 prop、覆寫成空則冒出備援鈕＝`rev5:B-099`），使用者頁另有 seed 實例（m0003 後 R_ADMIN 有頁無碼）。四錨隨各頁表頭改形之單元落地（IP 規則頁與使用者頁＝U18、角色與選單頁＝U19）；自測正反＋判準變異（RL-0080）、工具檔頭、README 工具樹、RUNBOOK §12 兩表與 `docs/ops/reference-src/code-gate-contracts.md` §3 ①（「錨檔＝工具常數 `ANCHOR_REL`」改指 `ANCHORS`；`ANCHOR_REL` 入 R22 errata 種子）同批。
  15. **生成檔與既有閘**：`src/typings/components.d.ts`＝unplugin 自 `src/components/**` 自動註冊 ⇒ `PwdGenModal` 兩行（介面與全域常數各一）＋所用新圖示（若有）隨引入單元同 commit、只許工具重算形（容器內 dev server 重算、禁手改）。views 下新檔皆非 `index.vue`／`[x].vue` ⇒ 路由產物四檔零重算（route-artifact-gate 冪等）。seed-view-gate 兩側讀面（m0002 `SEED_SYS_MENU` 塊之 view 鍵——m0003 只改選單 78 之按鈕清單；views 導出集——零新頁檔）皆不變、豁免兩鍵照舊；`user-detail/[id].vue` 續佔位、不可刪。
  16. **upstream `fetchGetUserList` 之其他消費者**：`src/views/plugin/excel/index.vue`（upstream 範例頁、選單只授 R_SUPER）零 diff、續經 barrel 消費；端點上線後由 `4040` 轉為真資料——`size: 999` 由分頁上界收斂為 100、所讀六欄與 rev6 wire 同名相容（偏離只在角色欄形、該頁不讀）；rev5 HEAD 該檔同為 upstream 原檔＝與 22080 收斂、毋需 CDP 排除（spec FR-008 已收窄、殘存消費面入 ADR-00083 決定 3＝user 2026-10-05 親決）。`system-manage.ts` 與 `service-alova` 同名函式不動（WRAPPER 軌道不改既有 service 檔）。
  17. **單元對映**：U14＝`rev6-user-admin.{ts,d.ts}`、`rev6-user-center.{ts,d.ts}` 四支新檔（純新增、不受 Amendment 硬閘；wire 裁判右源）；U17＝index（清單、回收桶、七碼、下拉骨架與踢除）、抽屜（不含產密鈕）、搜尋卡、`page.manage.user` 型節與兩語塊（含 `roleSeparator`；`zh-tw.ts` 同批補鍵）；U18＝重設浮層、產密浮層（含抽屜產密鈕接上與 components.d.ts 重算）、列解鎖、IP 規則頁解鎖彈窗、`pwd-policy.ts` 與 `page.passwordPolicy` 塊（三語＋型節；I18N (i) 圈界）、view-render-guard 判準 (b) 改寫及 IP／使用者頁兩錨；U19＝角色與選單頁按鈕碼、「門在頁級」碼註（含 `role-operate-drawer.vue`）及其兩錨（前置 U15、U18）；U20＝改密卡（消費 U18 之 `pwd-policy.ts`）、登入表單、請求層明細轉譯（前置 U15）。各單元先決＝U0 Amendment accepted 與 U15 已把 `zh-tw.ts` 改為 Schema 標型（三語同批自 U15 起由型別強制）。
- **Rationale**:spec FR-047～FR-054 與刻意分岔表；rev5 HEAD 之防護皆為 `rev5:007` 品質輪實打之缺陷修補、成因在 rev6 仍在（`getAllRoles` 同口徑＝只回活性且啟用），故全帶；唯 Q13 改以清單帶持有角色 id 與名稱、「解不出即鎖」不再必要。表頭 prop 形與禁覆寫 default 插槽為 005 刀既定（憲法 (ii) 列）、四頁同一失效類故同閘守。違規子鍵離開 backend 樹是唯一不必改閘與憲法 (ii) 列之路；請求層只認兩鍵＝FR-051 射程。重設浮層抽新檔、IP 解鎖鍵落既有圈界皆為縮小修改型面之 rebase 緩解。角色與選單頁按鈕碼使 ADR-00068 款 18 全解除、灰色保留選項使款 7（`rev5:B-145`）結案（ADR⑧）。
- **Alternatives considered**:
  1. 照 rev5 覆寫表頭 default 插槽（保底 div＋v-show 兩層）：與 005 刀 prop 形先例相背、覆寫內容不受 prop 控制；且 rev6 seed 有「有頁無碼」帳號＝`rev5:B-099` 瀏覽器可達。棄。
  2. 灰色選項改「不設 `disabled`、移除即自下拉消失」：灰階須自訂樣式、移除後使用者看不到「該角色存在而停用」之事實。棄。對所選方案跑同一反例（RL-0013：使用者能否在未見之下失去指派）：持有之停用角色恆以灰項標籤顯示、只有點其關閉鈕才移除、未動角色欄即不送 `roleIds` ⇒ 無無聲遺失；成立。
  3. `getAllRoles` 改回停用角色：牽動 005 刀契約與角色頁下拉口徑（Q13 已拍）。棄。
  4. 違規碼譯文留 backend 樹（rev5 白名單形）：違 msg-key-gate 斷言 1 與憲法 (ii) 列、且名冊每鍵須有發出點（contract 方向二）。棄。
  5. 請求層把任一錯誤之 data 原樣交 `$t`（不限兩鍵）：明細通道射程擴散、與 ADR③「只限兩鍵」相背。棄。
  6. 改密卡綁 `userInfo.userName` 以補 `forbidUsername` 提示：比錯對象（顯示名）。棄。
  7. view-render-guard 腿①擴及 user-center 與 components/custom：射程內無自由文字渲染面＝空守。棄。
  8. 重設浮層仍內嵌於 index（rev5 HEAD 形）：index 修改型面增大、rebase 風險高（該檔近 12 月 upstream 有改動）。棄。

## R19 繁中 runtime 與 zh-TW 閘（ADR⑪）

> 對應 spec US5、FR-052、SC-009、Edge Cases「繁中介面」；Q4／Q4a／GR2／GR5。決定之承載＝ADR⑪（ADR-00084）。碼面現況取 base-web pin `fb4dac2`。

- **Decision**:
  1. **語系型別與三處註冊（I18N (iii)）**：`src/typings/app.d.ts` 之 `type LangType = 'en-US' | 'zh-CN';` 增 `'zh-TW'`（修改型）；`src/locales/locale.ts`（`import zhTW from './langs/zh-tw'`＋`'zh-TW': zhTW`）、`src/locales/naive.ts`（`zhTW`／`dateZhTW`）、`src/locales/dayjs.ts`（`import 'dayjs/locale/zh-tw'`＋對映 `'zh-TW': 'zh-tw'`）三處註冊——三處分別以 `Record<App.I18n.LangType, …>`／`satisfies Record<App.I18n.LangType, string>` 宣告 ⇒ 型別一擴即強制三處補齊（少一處即 typecheck 紅）；物件字面新項插在 `'zh-CN'` 與 `'en-US'` 之間（不插末項之後）。零新依賴：naive-ui 2.44.1 匯出 `zhTW`／`dateZhTW`、dayjs 1.11.20 含 `locale/zh-tw.js`（node_modules 實讀）。naive.ts 匯入以獨立匯入行新增為先（登記表型別欄＝新增型）；lint 若擋重複匯入即改修改型、同批更新登記表。
  2. **預設語言三處**（未選過＝`localStg.get('lang')` 為 null）：`src/locales/index.ts` 之 `createI18n` 起始語系、`src/store/modules/app/index.ts` 之 `locale` 初值、`src/locales/dayjs.ts` 之 `setDayjsLocale` 預設參數與其 fallback 兩字面——由 `'zh-CN'` 一律改 `'zh-TW'`（修改型）；選過者照記（`changeLocale` 寫入；儲存鍵＝`.env` `VITE_STORAGE_PREFIX`〔`SOY_`〕＋`lang`、值為 JSON 字串）。`fallbackLocale: 'en'` 不變。
  3. **語言下拉三項**：`localeOptions`＝`[{label:'简体中文',key:'zh-CN'},{label:'繁體中文',key:'zh-TW'},{label:'English',key:'en-US'}]`——既有 `label: '中文',` 行改修改型、繁中項插於兩項之間；標籤為語言自稱、硬寫於 store、不經 i18n（三語畫面同字）⇒「简体中文」之簡體字不入 zh-TW 樹、不在 zh-tw-lint 射程。
  4. **`zh-tw.ts` 全樹**（rev6 自有檔、整檔新增型）：由 `export default { backend: {…} }` 裸物件改為 `const local: App.I18n.Schema = { … }; export default local;`（與 zh-cn／en-us 同形）。既有 backend 子樹逐鍵保留（續為繁中譯文權威；`kicked` 之用語修正隨 U16、與 zh-tw-lint 腿④同顆）、補齊其餘十棵頂層樹。規模（pin `fb4dac2` 現算）：zh-cn.ts 855 行、葉鍵 619（backend 46、其餘十棵 573；最大為 page 303、theme 104、route 81）；zh-tw.ts 現 66 行、葉鍵 46 ⇒ U15 補 573 葉（其後各單元之新鍵三語同批另計）。譯文以 zh-cn 現行措辭之臺灣用語對譯（非逐字轉繁），會話用語依 GR2。結構約束：`backend: {` 須獨佔一行（msg-key-gate 右源錨 `RE_BACKEND_ANCHOR`）；整檔豁免圈界、只留檔頭一行，檔頭句「治理錨點孤立檔、不接 runtime、不註冊 LangType」「標型與 runtime 註冊延前端 UI 刀」改現在式（刀名欄續記進場刀 003-auth-session）。msg-key-gate 斷言 3 之安全前綴＝`MSG_KEYS` 頂層前綴 − locale 頂層鍵：zh-tw 補齊後頂層鍵與另兩檔同集 ⇒ 安全前綴仍為 `auth`、`biz`，零漂移。
  5. **`src/main.ts` 不改與已知態**：根元件驗證器 `getLocale() === 'zh-CN' ? 'zh' : 'en'` 維持——zh-TW 下開發期提示落英文（開發期提示、非產品面；外掛只有 zh／en 兩語；該檔近 12 月有 upstream 改動）；不入 ★ 登記表。另兩則：①`index.html` 之 `<html lang="zh-CN">` 為靜態、`setLocale`（`src/locales/index.ts`）只於切換時改寫 ⇒ 本刀於同檔初始化時以現行語言同步 `<html lang>`（I18N (iii) 檔集內、不擴檔集；主線工程判斷：實作 Q4 預設繁中之必要面，不同步則首開以簡中字型呈現繁中、AI 審讀必報）；②pro-naive-ui 3.2.2 只帶 zh-cn／en-us 語系、`src/views/pro-naive/ConfigProvider.vue` 只對 `'zh-CN'` 給語系 ⇒ zh-TW 下五支 pro-naive 範例頁（選單只授 R_SUPER）之 pro 專屬元件字串退英文（`form/basic` 範例另硬寫簡中）＝已知態（user 2026-10-05 親決：零 diff、不擴檔集；GR5 審讀與 CDP 排除其元件內建字；spec 刻意分岔表；ADR-00084 後果）。
  6. **三語鍵集相等之機器守**：zh-cn、en-us、zh-tw 三檔皆以 `App.I18n.Schema` 標型之物件字面賦值 ⇒ vue-tsc 對缺鍵（必填屬性缺）與多鍵（物件字面多餘屬性檢查、遞及巢狀字面）皆報錯＝三語鍵集機器相等；backend 子樹另由 msg-key-gate 斷言 1 逐檔對 `MSG_KEYS` 雙向全等（照舊）。型別不擋空字串值 ⇒ 由 zh-tw-lint 補「值非空」（決定 7）。憲法各列「兩語鍵集 MUST 相等」改三語屬 Amendment 逐處判讀（R20）；碼註之「兩語」句（`app.d.ts` 9 行、zh-cn／en-us 各 3 行；`grep -c` 現算）隨落地單元改寫。
  7. **zh-tw-lint**（新碼面閘 `tools/zh-tw-lint.py`；Python 標準庫、零 docker；`check`（預設）／`test`；rc 0 綠／1 違規／2 結構異常／64 用法錯）：判準設計之單一真源＝ADR-00084 決定 7（U0 accepted；四腿＝①簡體殘字 `SIMPLIFIED_CHARS` 查表②字表完備腿〔`zh-tw.ts` 與 `zh-cn.ts` 字串值所用 CJK 字每字 MUST 屬 `SIMPLIFIED_CHARS` 之鍵或 `APPROVED_CHARS`；未分類 rc 1、兩表相交 rc 2〕③大陸用語 `MAINLAND_TERMS`④會話用語：「踢」只准出現於 `ADMIN_KICK_KEYS`、`backend.auth.session.kicked` 不含「踢」與「管理員」、`kickedByAdmin` 含「管理員」；具名白名單 `EXEMPT` 只對①③生效、幽靈項紅）。本款只記理由與落地：繁中譯文自 zh-cn 對譯、殘字來源即 zh-cn 字集 ⇒ 完備腿逼新字分類（不驗歸類正確，殘餘由表值 diff 審查、AI 審讀與 user 抽查承接＝ADR-00084 RL-0013 段）；codec 判準（gb2312 可編且 cp950 不可編）只作表值初建輔助、不作判定。掃描面＝兩檔剝註解後之字串值、以鍵路徑指名；物件根＝檔內首個 `const <名>(: <型>)? = {` 或 `export default {` 之開括號（兩形皆認、皆缺 rc 2；與 msg-key-gate 各持解析、不共用）。
     - 自測：每腿一正一反、判準變異（拆完備性腿、拆殭屍檢查、拆歸屬檢查即自測紅；RL-0080）、掃描面空集合 rc 2（RL-0051）、真 repo 綠案。接線：外層 pre-commit 新段（`base-web` gitlink 或工具本體 staged 時跑 `check`——外層只見子庫 gitlink、子庫自用 `.githooks-submodule`，同 view-render-guard 段形）、`for t in` 自測迴圈、bootstrap `run_tool_test` 名冊、README 工具樹、RUNBOOK §12 速查表與碼面閘表各一列、`tools/docsync/tests/test_hook_wiring.py` 接線字面同批；碼面閘不占 GT 閘預算。落地＝U16（U15 先完成全樹、U16 上閘並修正既有三語鍵之繁中用語）；其後各單元之 zh-tw 新鍵即受閘。
  8. **GR5 驗收形**（SC-009）：①機器檢查＝容器內 `pnpm typecheck`（三語 Schema）＋msg-key-gate＋zh-tw-lint 皆綠；②AI 逐頁審讀＝U22 由 CDP agent（opus[1m]／xhigh）於 32080 顯式設 zh-TW 後逐頁讀可見文字，射程＝接真頁面（登入頁含 captcha 軟區、首頁、使用者頁〔清單、回收桶、抽屜兩態、列下拉、各確認與浮層〕、角色頁〔抽屜與三彈窗〕、選單頁〔彈窗與回收桶〕、IP 規則頁〔抽屜與解鎖彈窗〕、授權回收桶頁、個人中心）＋全域外框（頂欄、側欄路由名、語言與頭像下拉、主題設定抽屜、分頁籤）＋兩種 `7777` 對話框與重新登入提示；每頁判無裸鍵、無簡體字、臺灣用語、頂替／踢除語意四項；upstream 範例頁之元件庫內建字串不在必涵蓋射程；③user 抽查＝主線以 AskUserQuestion 請 user 於 32080 繁中介面自選頁抽查並回報。**紀錄落點**：逐頁明細住工作區（gitignored）；受版控者＝tasks.md 該 T 項落地註記（頁清單、發現數、處置〔修／轉 BL／已知態〕、user 抽查結果）＋U22 commit 訊息。
  9. **CDP 對照之語言設定**：`tools/orchestration/cdp.mjs` 現況 25 行、只匯出 `connect`（`send`／`evalJs`／`events`）與 `sleep`，零語言設定 ⇒ **不改工具**；quickstart 步驟以 `evalJs` 對每個 origin（22080、32080，必要時 22089；一律 127.0.0.1）執行 `localStorage.setItem('SOY_lang', JSON.stringify('zh-CN'))` 後 `Page.reload`，再以已知 zh-CN 字串（如登入鈕文字）斷言生效——儲存鍵由 `.env` `VITE_STORAGE_PREFIX=SOY_`（rev5、rev6 與 upstream 基線三方同值）與 `localStg` 之 JSON 字串形導出；寫的是瀏覽器端儲存、不觸 rev5 stack 資料＝22080 側唯讀照守。對照兩側皆須設 zh-CN（rev6 未選過即繁中、不設則文案逐項不等）。繁中審讀與「首訪預設繁中」驗收另於 32080：前者寫 `'zh-TW'`、後者 `removeItem('SOY_lang')` 後重載斷言繁中字串。
  10. **ADR⑪（ADR-00084）要點**：①supersede ADR-00039——其決定 1（除「孤立檔」一語：閘形制、無白名單、構造點守衛、承載工具）、決定 2（譯文之家＝三檔，範圍由 backend 子樹擴至全樹）、決定 3（鍵數不手抄）原意續行，決定 4 之改指義務轉指本 ADR；`zh-tw.ts` 改為 runtime 註冊之完整 locale；②ADR-00050（續行 ADR-00049 決定 1）之「`zh-tw.ts` 不接 runtime、不在對照面，不隨改」改述——「不在 CDP 對照面、拒因譯文不以 rev5 措辭為起點」之決定續成立、理由改為「rev5 無繁中基準、驗收改走 GR5」，「不接 runtime」一語自本刀不再成立；決定內容未翻 ⇒ ADR-00050 不被 supersede，現在式面之引用讀時併讀 ADR-00084；③LangType、三處註冊、預設 zh-TW、下拉三項、`main.ts` 不改、`<html lang>` 首開同步、pro-naive 已知態（決定 5）；④三語鍵集之機器守＝型別；⑤zh-tw-lint 為碼面閘；⑥GR5 驗收形；⑦本刀起每刀三語同批；⑧ADR-00032 翻案觸發器①（碼面閘 ≥8）之複核狀態（R17；處置轉 BL-00142）。翻案觸發器：naive-ui 或 dayjs 移除繁中語系、locale 改由翻譯平台管理（檔成產物）、驗證器外掛支援 zh-TW。
  11. **as-built 改寫種子**（RL-0011；落地單元同批、餘由 U21 收）：「孤立檔」「不接 runtime」「延前端 UI 刀」「LangType 擴充」「標型」「兩語」——現在式面含 `zh-tw.ts` 檔頭、`app.d.ts` (iii) 圈界首行碼註、zh-cn／en-us／`app.d.ts` 之「兩語鍵集」碼註、憲法 I18N (iii) 列與「兩語」14 處、活書 08（「不接 runtime」3 行、「兩語」1 行）與 05、BACKLOG BL-00138 條文；實集以 `python3 tools/docsync errata <詞>` 枚舉、逐處判讀（史料面保留）。
- **Rationale**:spec FR-052（Q4、Q4a）與 GR2、GR5；`Record<LangType, …>` 與 `App.I18n.Schema` 標型使「三處註冊」與「三語鍵集相等」皆由既有型別系統機器守、零新工具；zh-tw-lint 補型別守不到之內容面（簡體殘字、空值、大陸用語、會話用語），且以完備性腿讓「表漏列字」顯形（樣式集先證完備）、以碼面閘持久化使本刀起每刀三語同批後持續有效；CDP 語言設定以兩行 `evalJs` 即足、毋需擴工具 API。
- **Alternatives considered**:
  1. `zh-tw.ts` 維持裸物件、以 msg-key-gate 擴全樹比對：重造型別已有之能力、多一份解析器。棄。
  2. 引第三方繁簡轉換套件（如 OpenCC）判簡體：新依賴觸版本紀律、且仍需白名單與用語表。棄。
  3. 只靠 AI 審讀、不設閘：無持久化、下一刀即失守。棄。
  4. 預設語言依瀏覽器 `navigator.language` 偵測：Q4a 已拍未選過＝繁中。棄。
  5. 改 `main.ts` 驗證器判斷：開發期提示、外掛無 zh-TW、近 12 月 upstream 有改動之檔多一處修改型（plan 期定案）。棄。
  6. 擴 `cdp.mjs` 增語言 helper：兩行步驟足矣、增 API 面無益。棄。
  7. 簡體偵測只用手列表、不設完備性腿：漏列字即假綠（無從察覺）。棄。對所選方案跑同一反例（RL-0013：是否仍有假綠）：zh-cn 未用之簡體字手誤鍵入仍漏（已具名為射程外）；空字串值由空值檢查補上（ADR-00084 決定 7）；成立。

## R20 Amendment 要點與 U0 待親決清單（ADR①）

- **Decision**: 一次 MINOR 1.7.1→1.8.0（§V.3「行為島隨刀進場」＋「軌道授權邊界擴展」；零既有入憲不變式反轉），獨立 commit、條文字面由 user 於 U0 逐款親決；載體＝ADR①（ADR-00074）。五款：①§I.7 島 I 入憲（I1～I5、I7；I6 空缺），以 `rev5:` 憲法 v1.9.1 島 I 字面為底（`rev5:ADR 0063`、I5 釐清＝`rev5:ADR 0068`），rev6 改寫要點見下表 ②跨島重審：跨島註新增「密碼政策壞值設密全拒 vs 島 E 整組退」一則（ADR⑥）、跨島總則之生效時點補密碼政策鍵、承襲指針表尾句不動（I6 空缺之交代住島 I 標頭） ③島 B 第三點「踢除」改述「頂替」（`kicked`）、「踢除」專指管理員結束他人全部會話（`admin_kick`；GR2）；島 C「`kicked` 與 `revoked` 兩 reason」改三 reason；H2 補選單刪碼守門句與否親決（GR1b） ④§III.2：★`BASE-WEB-MANAGE-PAGE-WIRING` 新用途 (v)～(viii)、★`BASE-WEB-LOGIN-CAPTCHA-WIRING` (ii) 開立、★`BASE-WEB-I18N-WIRING` (i) 改寫（明細通道只限兩鍵）與 (iii) 開立（既有 (iii) 列之延後半）、表內「兩語鍵集 MUST 相等」改三語；連動字面同顆改四處——MANAGE-PAGE (i) 列「解鎖按鈕與其包裝不在本次授權（使用者管理頁刀）」、(iii) 列「三鈕不做按鈕碼 gating（門在頁級）」、LOGIN-CAPTCHA (i) 列「用途 (ii)…延改密端點刀」、I18N (iii) 列「…不在本次授權，延前端 UI 刀」 ⑤承襲指針表 I 列補「rev6 已入憲 v1.8.0（ADR-00074）」、MAJOR 射程句「八島」→「九島」、Amendment log 新列、generate（版本由 STATE 承載；README 只指針）。範圍欄初值依表外宣告 1 例外路徑、收刀前 PATCH 實數化（R21 表末列）。**硬閘**：Amendment 顆落地前 base-web 既有檔零 diff（`git -C base-web status --porcelain` 空且 HEAD＝pin `fb4dac2`）；純新增檔不受此閘。**U0 程序**：①前置體檢（ADR① 所引「現行」原文逐段對憲法、R22 種子現算、兩子庫 HEAD＝pin）②先定條文將直指之 U0 accepted ADR 決定款（ADR② 消費點與判定位次、ADR③ 兩鍵、ADR⑥ 方向與告警、ADR⑪ 三語與預設 zh-TW、ADR⑭ 選單刪碼守門），再依下表依賴序呈 ADR① 各題 ③一題一問（AskUserQuestion）④ADR① accepted＋Amendment commit（主線親跑 `python3 tools/fork-delta-lint.py` 與 `python3 tools/route-artifact-gate.py check` 皆 rc 0、關鍵行入 commit 訊息）⑤施工前提顆（R21）。★條文與 §III.2 紀律欄所引 ADR 限 U0 accepted 者；ADR⑧⑨ 不得被條文直指。

**島 I 改寫要點**（全文住 ADR① 決定節；常數與量測值不入條文）：

| 條 | rev6 對 `rev5:` 字面之改寫 | 題 |
|---|---|---|
| I1 鎖序 | 角色列由「僅比對需要時讀」改鎖形：T∪N 去重升序 `FOR UPDATE`、鎖內重驗未軟刪（島 G5 末句自此非 vacuous；R7）；批次改三段單調（advisory 全取→使用者列全鎖→整批 T 聯集一次升序鎖角色列；`rev5:` 逐 id 交錯形不帶回）；消費者含 unlockLogin 帳號維（R9）；key space 句改引島 H1 | I-d1 |
| I2 斷權 | 撤票集補自助改密（撤本人其他有效票、保留當前）；三類體驗碼具名（撤銷 `8888`／頂替 `7777`＋`auth.session.kicked`／踢除 `7777`＋`auth.session.kickedByAdmin`）；換發重驗時點（票列鎖後、簽發前、不取 advisory、不改鎖序）入條文與否；grace 腿回既發之同一對、不簽新票＝不在重驗射程（記 ADR① 後果） | I-d2 |
| I3／I4 | 字面沿用；seed 識別以 rev6 seed id 1／2／3 為準、常數名不入條文；I4 為 ADR-00044 翻案觸發器①之答案（ADR 級） | I-d3、I-d4 |
| I5 政策 | `rev5:ADR 0068` 釐清句直接併入；「單一快照讀取」改述「只在消費當下讀現值」；補「子串不算違規」；DTO 遮蔽句本刀兌現（`LoginReq` 改形＝R11） | I-d5 |
| I6 | 留空；標頭一句載明首登強制改密不做（不寫 BL 號；承載 BL-00140 記 ADR-00074 後果） | I-a、I-b |
| I7 包含規則 | 字面沿用；9 消費點；判定位次＝固定序第④（R8）；「與島 G2／G6 判定位次與拒因鍵不互吞」入條文與否；兩實作位射程分工屬 ADR②、不入條文；射程排除自助改密（其標的恆為操作者本人；spec FR-021） | I-c、I-d6 |

**U0 待親決清單**＝ADR-00074「親決題索引」（單一真源：題號、題目、建議與依賴序以該 ADR 為準、本節不重列；I-a～I-d7、X-a／X-b、B-a、C-a、H-a、P-a～P-d4、L-a、N-a／N-b、M-a／M-b、T-a、Y-a／Y-b、S-a）。plan 期已定、不再列題者：P-b excel 示範頁＝不入（user 2026-10-05 親決）；ADR-00084 決定 10 兩候選＝`<html lang>` 首開同步（主線工程判斷）與 pro-naive 已知態（user 2026-10-05 親決）。憲法 G5 括號句不改、承襲指針表尾句不動、條文不寫 BL 號（ADR-00074 決定二、決定五）。

**§III.2 檔級名單與範圍欄初值**＝ADR-00074 決定四（單一真源；U0 親決）。plan 收攏期訂正已併入該 ADR：①`src/service/request/index.ts` 沿現行實數「2 處修改型＋2 塊新增型」（明細轉譯落 003 刀既有圈界、toast 鏈只改既有修改型行內容＝R18 決定 10）②`src/locales/locale.ts` 預估 0 塊（匯入與對映兩處單行形新增型、不入計數）③`naive.ts` 預估 0 塊（獨立匯入行與兩表各一項皆單行形；lint 擋重複匯入即改「預估 1 處，修改型」並同批改 spec 登記表型別欄）④`dayjs.ts` 預估 2 處修改型（預設參數與退路之 `'zh-CN'`；匯入與對映單行形不入計數）⑤`src/store/modules/app/index.ts` 繁中選項＝單行形新增型、範圍欄預估 2 處修改型（預設與「中文」標籤）⑥(vii) 補鍵＝巢狀 (vii) 圈界一塊（兩語 locale 與 `app.d.ts` 各 1；巢於 MANAGE (i) 既有塊內、(i) 塊首尾與理由句不動）。單元出口之差額程序依 ADR-00074 P-c①（射程內差額記入單元收尾、延收刀前 PATCH 實數化；射程外改點＝停手升級）。
★`src/main.ts` 不入（R19）；`components.d.ts` 走生成檔紀律；`zh-tw.ts` 為 rev6 自有檔。新列紀律欄一律「三語鍵集 MUST 相等（`zh-tw.ts` 同鍵同批）」。
**「兩語」逐處**（`grep -o` 現算 14）：§III.2 MANAGE-PAGE (i)～(iv) 四列各兩處＝表內 8（「兩語鍵集 MUST 相等」4 改三語；「兩語 locale」檔面語 4 留並補 zh-tw 句）；Amendment log 1.4.0／1.5.0／1.7.0／1.7.1 共 6＝史述不動。

- **Rationale**: spec FR-055；條文只凍方向面（006 刀 ADR-00063 同形）；LL-00058 守法③；條文所指 ADR 限 U0 accepted＝權威鏈不倒掛。
- **Alternatives considered**: 分兩次 Amendment（版本與 log 雙倍、硬閘延後，棄）；範圍欄直取 `rev5:` 標記實數（LL-00058 守法③：作預估前須先過拔標記判定，棄直取）；I5 釐清另立 PATCH（`rev5:ADR 0068` 已證屬字面不精確，棄）。

## R21 ADR 配號與親決時點表

- **Decision**: 接續 ADR-00073，plan 期十四支（ADR-00074～ADR-00087；⑫ 不另立）全數 `proposed`、草稿期 `supersedes: []`（GT-04）、accepted 同顆補；收刀前 PATCH Amendment 一支（表末列；plan 期不起草）；`feature_close.adrs`＝15。被島 I 條文或 §III.2 紀律欄指向之決定款於 accepted 前 MUST NOT 改動（需改＝停手升級）。

| ADR | 主題（前代出處） | 與既有 ADR 關係 | accepted 時點 | 凍結款／同顆連動 |
|---|---|---|---|---|
| ADR-00074 ① | 憲法 Amendment 1.7.1→1.8.0（`rev5:ADR 0063`＋`rev5:ADR 0068`） | 兌現 ADR-00034／ADR-00042／ADR-00026 翻案觸發器（新用途走 §V.2）；記載 ADR-00063「G5 轉非 vacuous」複核 | U0 Amendment 顆 | 親決改字即同步改寫；連動＝憲法、log、P-a、generate |
| ADR-00075 ② | 包含規則與射程分工（`rev5:ADR 0063` 款三形） | 不 supersede ADR-00014（不翻案）；兌現 ADR-00064 與 ADR-00063 島 I 條；BL-00048 收 | U0 施工前提顆 | I7 所指消費點與判定位次 |
| ADR-00076 ③ | 明細通道射程與受眾（`rev5:ADR 0064`） | 不 supersede ADR-00014（決定 1 只管 `5003`）；002 刀 wire 契約 §3 第 3 條之兩鍵例外以本 ADR 為現行依據 | U0 施工前提顆 | I18N (i) 所指兩鍵射程 |
| ADR-00077 ④ | 自助路由白名單（`rev5:ADR 0065`） | 與 §I.2 關係；ADR-00014 後果「注入形不變」句隨 `Identity` 增 `sid` 之註記 | U0 施工前提顆 | —— |
| ADR-00078 ⑤ | 設密冷卻＋改密節流（`rev5:ADR 0066`） | 釐清 ADR-00038 射程；ADR-00069 款 5 不觸發；ADR-00037 反向確認；BL-00124 收 | U0 施工前提顆 | —— |
| ADR-00079 ⑥ | 政策壞值方向與告警出口 | 與 ADR-00038 決定 4 方向相反之理由；BL-00031 收 | U0 施工前提顆 | 跨島註所指方向款 |
| ADR-00080 ⑦ | 使用者域寫端語意（空字串、no-op、會話政策必填、並行編輯、批刪多重違規） | 整支續行並 supersede ADR-00047（決定 1～5 原意續行；決定 2 增使用者域、決定 5 射程擴 addUser 可空文字欄空字串形、no-op 增使用者域值 diff 口徑；rev6 無部分翻案機制＝ADR-00011 決定 5）；ADR-00043 決定 8 重核＝ADR-00074 決定二；ADR-00044 觸發器①＝ADR-00074 I4、②＝ADR-00074 決定二島 G 款 | U0 施工前提顆 | 補 supersedes、ADR-00047 狀態；現在式面引 ADR-00047 處改指 |
| ADR-00081 ⑧ | 角色與選單已知態 v3 | supersede ADR-00068 | U22（CDP 後） | 補 supersedes、ADR-00068 狀態、活書 11 改指 |
| ADR-00082 ⑨ | IP 域已知態 v4 | supersede ADR-00069 | U22 | 同上；「五詞」改八詞之現在式面 |
| ADR-00083 ⑩ | 使用者清單 wire 偏離帳（ADR-00044 決定 9 形） | —— | U0 施工前提顆 | —— |
| ADR-00084 ⑪ | 繁中 runtime、預設 zh-TW、`tools/zh-tw-lint.py` | supersede ADR-00039；改述 ADR-00050 決定 1（原樣續行之 ADR-00049 決定 1 末句「`zh-tw.ts` 不接 runtime」） | U0 施工前提顆 | I18N (iii) 所指款；補 supersedes |
| ADR-00085 ⑬ | m0003、按鈕維受保護首例、閘序號合成、走查工具遷移帳前置與合成 | ADR-00008 delta 首支；ADR-00064 背景「按鈕維受保護 0 列」註記；封死集擴大與 `sys_menu.component` delta 兩類觸發之反向確認 | U0 施工前提顆 | —— |
| ADR-00086 ⑭ | 選單編輯移除受保護授權碼之守門 | 承島 G2；與 H2 連動歸檔之關係 | U0 施工前提顆 | H2 補句所指判定款 |
| ADR-00087 ⑮ | schema-definition 留 001 基線 | supersede ADR-00012（ADR-00011 決定 5）；BL-00047 收 | U0 施工前提顆 | 補 supersedes；schema-definition 檔頭句同顆改 |
| 當下下一號 | 收刀前 PATCH：(v)～(viii)、LOGIN-CAPTCHA (ii)、I18N (i)(iii) 範圍欄實數化（前例 ADR-00051／ADR-00072） | 兌現 ADR-00074 回填義務 | U23（與 Amendment 同一顆獨立 `docs(constitution): amend`） | 1.8.0→1.8.1、log、generate |

- **Rationale**: Amendment 顆只含 ADR①＝§V.2 步 4 之獨立顆，可單獨審查與回退；施工前提十一支 U0 accepted＝條文所指款不得為可變 body、且為 U1～U20 前提、毋需觀察（005／006 刀同形）；⑧⑨ 排 CDP 後＝款 20 改述與 ADR-00070 觸發器實測、款 1 解除與款 3 八詞落字皆待觀察（`rev5:L-046`），先 accepted 後觀察即須再 supersede；⑫ 不另立＝分岔表各列已指承載 ADR／FR，另立即同一事實兩個家（RL-0049）、CDP 中追加即須 supersede；PATCH 配號取收刀前當下下一號（窗內他批先取即順延、GT-05 永不重用）。
- **Alternatives considered**: 全數 U0 accepted（已知態未觀察即凍結，棄）；施工前提隨落地單元 accepted（條文指向可變 body，棄）；⑫ 另立（重複承載，棄）；Amendment 與施工前提同顆（失獨立性，棄）。

## R22 as-built 改寫義務（RL-0011）

- **Decision**: 各單元收尾以 `python3 tools/docsync errata <詞>` 對下列種子枚舉（全 repo 含兩子庫 pin 樹）、逐處判讀「改／史述留／accepted 只能續行／生成物 generate」、改完復掃；新值（六十一、十一域、十三支、三語、九島、十一源、十一變體、八詞、八支碼面閘）改後以同指令驗有命中。`MSG_KEYS` 鍵數不設文字新值（ADR-00039 決定 3）。★「可發碼恰九」屬 13 碼矩陣之可發碼集、本刀不變，勿隨變體數誤改。現量（以行計）＝外層 HEAD `7847b77`、兩子庫 pin 樹（2026-10-05 實跑；本刀 plan 產物與 ADR 草稿未入版控、不在其內）。

| 形 | 種子（現量） | 現在式面與處置（摘；其餘＝accepted ADR 只能續行、史料留） | 單元 |
|---|---|---|---|
| ①名稱 | `使用者域刀`（14） | 活書 11 已知態列「解除點」改指 ADR⑧；ADR 10 | U22 |
| ①名稱 | `使用者角色指派寫端`（17） | 憲法 G5 1＝括號條件句恆真、不改（ADR-00074 決定二）；BACKLOG 1（收刀刪列）；ADR 10 | —— |
| ①名稱 | `007 刀`（32） | 現在式須改零：ADR 26 由下表觸發器承接；BACKLOG 1、DECISIONS-INDEX 1（生成） | —— |
| ①名稱 | `使用者管理頁刀`（22）／`改密端點刀`（4）／`前端 UI 刀`（13） | 憲法各 1（M-a／L-a／N-b）；`zh-tw.ts` 檔頭 1 改現在式；BACKLOG（BL-00091、BL-00138 收刀刪列） | U0／U15 |
| ①名稱 | `本體刀`（10） | `auth/enforce.rs` 5（BL-00048 兌現連動面：掛點續恆放行、本體＝handler 鎖內純函式；含 `enforce_role_path_method` 內掛點呼叫點碼註與掛點拒絕計數測試 doc）；ADR-00014 3 不翻案 | U7 |
| ①名稱 | `門在頁級`（17） | 憲法 1（M-b）；`role-operate-drawer.vue` 註 1 改述（三顆授權鈕仍不設碼、門非僅頁級；spec ★ 登記表該列）；`policy-archive/index.vue` 1 仍真留；活書 05／06／08 各 1 | U0／U19／U21 |
| ①名稱 | `孤立檔`（9）／`不接 runtime`（16） | `zh-tw.ts` 1；活書 08 3；ADR-00039／ADR-00049 由 ADR⑪ supersede 或改述 | U15／U21 |
| ①名稱 | `無 UI 按鈕`（19） | 活書 06／11／12 各 1、RUNBOOK §9 1；`rev6-ip-rule.ts` 檔頭同語意句；ADR 7（款 1 由 ADR⑨ 解除） | U18／U21 |
| ①名稱 | `踢除`（56） | 憲法島 B 1（B-a）；活書 12 2；rust 碼註 6 指單一會話改「頂替」（`login.rs` 3、`session_event.rs`、`sys_token.rs`、`test_kit.rs` 各 1）；`m0002` 1 屬管理員義、例外②檔不動 | U0／U2／U5／U10／U21 |
| ①名稱 | `自助路由白名單`（9） | `handler/route.rs` 檔頭「屬 `rev5:004` 增量…不帶」改現在式＋歸因勘誤（`rev4:014` 起源、`rev5:007` U4 帶回） | U12 |
| ①名稱 | `消費歸各自功能刀`（2） | `config.rs`、`docker-compose.yml` 改指 BL-00141 | U21 |
| ①名稱 | `translateDetailValue`（7）／`恆 null`（20） | 憲法 1（N-a）；`request/index.ts` 註 1；`envelope.rs`／`error.rs` 錯誤 `data` 句與「契約 §3 第 3 條」引用改指 ADR③；其餘欄值他義留 | U6／U20 |
| ①名稱 | `UserStatusFixture`（22）／`SessionPolicyFixture`（14） | rust 碼 34 處（`test_kit.rs` 17、`login.rs` 13、`role.rs` 2、`sys_user_role.rs` 2）：不改名、不改呼叫點（R15 第 1 款：既有兩 fixture 零改動、與 `SeedUserRestoreGuard` 疊用）；doc 現在式復核 | U2 |
| ②不帶 | `屬後刀域`（8）／`後刀`（75） | 本刀兌現者改現在式：`enforce.rs`（三向、`sid`）、`auth/mod.rs`、`cache/mod.rs`、`error.rs`、`password.rs`、`handler/throttle.rs`；其餘 `rev5:` 他刀增量仍真者留 | U6／U10／U12／U13 |
| ②不帶 | `不搬`（51）／`` rev5:007` 增量 ``（8） | `refresh.rs`「兩件不搬」、`sys_token.rs`、`sys_user.rs`、`session_event.rs` 改現在式；他義留 | U5／U11 |
| ②不帶 | `不產 hash`（7） | 根 `Cargo.toml` 1；`server/Cargo.toml` argon2 與 getrandom 消費者句同義補 `hash`／salt | U6 |
| ②不帶 | `隨每支帶 migration 的刀前進`（3） | schema-definition 檔頭依 ADR⑮ 改；BACKLOG 1 收刀刪 | U0 |
| ②不帶 | `零 migration`（113） | `sys_user.rs` 2＝003 刀不下 CHECK 之史因、復核留；NOTES 1 收刀改；本刀新寫一律「一支 seed-only migration」 | U5／收刀 |
| ②不帶 | `隨刀：憲法 §I.7 島 I 進場刀`（5） | 活書 06 frontmatter 值改「承襲（§6.1 島 I 情境…）」；生成物 generate；`test_book_refs.py` 語料面不動 | U21 |
| ②不帶 | `不在本次授權`（15）／`不在授權內`（3） | 憲法 4（三處依 M-a／L-a／N-b、LOGOUT-UX 仍真留）；`app.d.ts`、`pwd-login.vue` 圈界註各 1；活書 08 1 | U0／U15／U20／U21 |
| ③名冊 | `兩語`（96） | 憲法 8 行（T-a）；base-web 圈界註 15（`en-us.ts` 3、`zh-cn.ts` 3、`app.d.ts` 9）改三語；活書 05／08 各 1 | U0／U15／U21 |
| ③名冊 | `九域`（9）／`十二支`（25）／`十二張表`（9） | `handler/mod.rs` 3→十一域；`facade/mod.rs` 3→十三支對十三張表；`test_kit.rs`、`deploy/` 屬他義留 | U3／U5 |
| ③名冊 | `三條 Authed`（7） | `router.rs` 1、`contract.rs` 全集語改五條；指 003 刀三支未認證案者留 | U3 |
| ③名冊 | `兩 reason`（14） | 憲法島 C 1（C-a）；活書 06 1；`cache/mod.rs`、`error.rs` 各 1 改三 reason | U0／U10／U21 |
| ③名冊 | `跨 handler 共用件恰一支`（plan 收攏期補；現量 errata 現算） | `handler/mod.rs` 檔頭改述（R6 第 1 款） | U3 |
| ③名冊 | `ANCHOR_REL`（3 檔） | 工具常數改 `ANCHORS`；RUNBOOK §12、`code-gate-contracts.md` §3 ① 改指（R18 決定 14） | U18／U19 |
| ③名冊 | `免造 sys_user`（`test_kit.rs` `ID_RANGES` doc） | 改「`user_id` 取 seed 使用者或經 `UserRowsGuard` 守之自建帳號」（R15 第 2 款） | U2 |
| ③名冊 | `首個動作`（`advisory_lock_user` doc） | 改「早於任何列鎖（鎖前普通讀容許）」（R9 第 5 款） | U13 |
| ③名冊 | `三節`（`wire_schema.rs` 14 處）／`兩列`（偏離帳 doc 三處） | 改五節／三列（R14 決定 3、4） | U14 |
| ③名冊 | `十四支`（`contract.rs` 寫端拒寫案名與檔頭） | 案名改 `write_refusals_add_no_context_absent_leg_real_seed`、「二十三支…寫端」（R17） | U8～U13 逐支擴列、U14 收口 |
| ③名冊 | `七支碼面閘`（2） | `.githooks/pre-commit`、`tools/bootstrap.sh` 改八支 | U16 |
| ③名冊 | `五詞`（17）／`恰兩支`（13） | `model/audit.rs`「恰五個動作」「這五個字面」改八（未用「五詞」字面、同語意補掃）；ADR-00069 款 3＝ADR⑨；`password.rs`「本刀恰兩支公開面」「自證案恰 5 支」改實數 | U5／U6／U22 |
| ③名冊 | 活書逐島情境 | 06 §6.1／10 §10.2 各增「使用者域治理——島 I」情境一則與 frontmatter；10 導言依 S-a | U0／U21 |
| ④數量詞 | `四十九`（11）／`十九列`（2） | `router.rs` 5、`contract.rs` 3、`test_references.py` 2 改六十一與 +12 列 | U3 |
| ④數量詞 | `35 鍵`（3）／`受保護 0`（9） | `sys_casbin_policy.rs` 種子實數案：端點維 35 鍵受保護 14、封死集 15＝14＋候選外列 68 →45／15／候選外 0（U3）；按鈕維 20 項受保護 0 → 21／6（U4）；`contract.rs` 2 同（U4）；`test_kit.rs` 合成案他義留 | U3／U4 |
| ④數量詞 | `恰十`（18）／`十源`（5）／`十值`（10） | `obs.rs`、`throttle/mod.rs`（含測試名 `…_ten_sources`）、`lib.rs` 降級源改十一；「恰十鍵」類 wire 欄數他義留 | U12 |
| ④數量詞 | `變體集恰九`（2）／`九變體`（3） | `error.rs` 檔頭與「§11 九列」、`lib.rs` 改十一（U6 增一、U10 定稿） | U6／U10 |
| ④數量詞 | `163 列`（23） | `walkthrough-baseline.py` 3 自測判讀（凍結 163、合成目標上界 164）；`m0002`、schema-definition 屬基線不改 | U1 |
| ④數量詞 | `八島`（15） | 憲法 MAJOR 射程句改九島（log 不動） | U0 |
| ④數量詞 | 受保護列數「19」現在式面 | `受保護.{0,30}19` 雙向掃描：rust 現在式碼與測試、活書、RUNBOOK 零命中；`m0002`／schema-definition 屬 001 基線；ADR-00064 背景＝ADR⑬ 註記；本刀新寫一律 25 | U4 復核 |

**指向本刀之 ADR 翻案觸發器全集**（掃描面＝`status: accepted` 且 `superseded_by` 空之 64 支之 `## 翻案觸發器` 節；樣式＝`(?<![0-9])007(?![0-9])`、`使用者域刀`、`使用者管理頁刀`、`改密端點刀`、`前端 UI 刀`，排除 `ADR-0007x` 編號誤中；實得 8 支 13 行）：

| ADR | 觸發器（摘） | 處置 | 承接 |
|---|---|---|---|
| ADR-00034 | 使用者管理頁刀之解鎖按鈕＝新用途、走 §V.2 | 成立：(v)／(vii) | ADR① |
| ADR-00042 | 使用者管理頁刀進場＝下一個新用途 | 同上 | ADR① |
| ADR-00044 | 使用者軟刪 MUST 定是否清指派 | 成立：同交易硬刪、in-use 口徑不改 | ADR①（I4） |
| ADR-00063 | 指派寫端落地＝G5 轉非 vacuous；G4 兩腿轉生產可達 | 成立：I-d1（I1 鎖形）；G5 括號句恆真不改；U8 測試複核 | ADR① |
| ADR-00063 | 島 I 入憲複核 G2／G6 邊界與跨島不一致 | 成立：I-d6、X-a | ADR②／① |
| ADR-00064 | 本體落地或島 I 入憲⇒複核決定 3／7 與復原同掛否 | 成立：不互吞、正交、復原不掛 | ADR② |
| ADR-00068 款 7 | 接真使用者頁（複核 `rev5:B-145`） | 成立：灰色保留＝結案 | ADR⑧ |
| ADR-00068 款 9 | 多層管理員或島 I 進場 | 成立：使用者域與帳號維解鎖半解除 | ADR⑧ |
| ADR-00068 款 11 | 第二帳號持 R_SUPER 或誤蓋發生 | 可達、未發生＝續作已知態改述 | ADR⑧ |
| ADR-00068 款 18 | 頁加入按鈕碼 gating | 成立：三頁全解除 | ADR⑧ |
| ADR-00068 款 20 | 指派寫端落地使此面生產可達 | 成立：改述＋U22 實測 | ADR⑧ |
| ADR-00069 款 1 | 使用者管理頁刀開工 | 成立：兩入口＝解除 | ADR⑨ |
| ADR-00070 | 指派寫端落地→實測只改名稱不被擋 | 成立：U22 實測、結果入款 20 | ADR⑧ |

**以他詞指向本刀者**（同掃描面補掃 10 條）：ADR-00014 明細受眾重評＝不觸發（ADR③）；ADR-00044「指派寫端落地⇒in-use／self-role 生產可達」＝成立（ADR① 決定二島 G 款、U8、U22）；ADR-00037 匿名端點擴拒絕射程＝不觸發（改密為登入即可用；ADR⑤）；ADR-00043 ABBA 三失效條件＝不觸發（角色寫端不撤會話、使用者域寫端不入選單域、無跨交易重入；ADR① 決定二）；ADR-00064 多層管理員需求＝成立（ADR②）；ADR-00063／ADR-00064 封死集下放或擴大＝不觸發（m0003 只動 `v2='button'` 列；ADR⑬）；ADR-00067 新增改 `casbin_rule` 之寫端＝不觸發（使用者域寫端不寫、m0003 屬遷移；R17 反向確認）；ADR-00071 改 `sys_menu.component` 之 delta＝不觸發（只改 `buttons`；ADR⑬）；ADR-00066 候選外列結構性消失＝不觸發（seed 候選外端點列 16→5、餘 008 刀稽核五支；R13）；ADR-00028／ADR-00036 郵件＝不觸發（BL-00141）。

- **Rationale**: RL-0011／RL-0015、spec FR-059；觸發器以結構化掃描取實數。
- **Alternatives considered**: 收刀前一次總掃（lint 窗內持假述、review 重報，棄）；只掃「007」字面（漏以刀名指向之 4 條，棄）。

## R23 執行單元切分 U0～U23

- **Decision**: 單元表如下（派發真源＝tasks.md）。commit 欄代碼：R＝rust-api 子庫 commit＋外層 pin；B＝base-web＋外層 pin；RB＝兩子庫＋外層兩 pin；外＝外層一顆零 pin（兩段式、`git -C <子庫>`、外層 `git add <子庫>`＋generate；單元收尾六步序）。★dev 庫寫入點只四處（U1 派發前〔條件式：序號斷言不符時〕、U4、U22、U23 Day-1 第 1 步前〔條件式：dev 庫有殘列或 seed 帳號欄值殘值時 restore；R15 第 7 款④〕），逐步取 user 放行（LL-00053）；U23 另建 pristine 庫（非 dev 庫）。

| 單元 | 內容與涵蓋 FR | 主要涉檔 | 前置 | 出口驗證 | commit |
|---|---|---|---|---|---|
| U0 ★主線 | Amendment 親決（R20）、施工前提十一支 accepted（R21）、首筆事件（misc、`backlog_add` BL-00140／BL-00141／BL-00142）；FR-055／056／060 | 憲法、ADR-00074～00087、schema-definition 檔頭、活書 08／10（P-a）、`events.jsonl` | 一切之前；base-web 既有檔零 diff | fork-delta-lint、route-artifact-gate check rc 0；docsync 零錯（GT-03 在途三警消失） | 外兩顆（Amendment 顆、施工前提顆） |
| U1 工具 | `schema-gate.py` seed_add 序號合成；`walkthrough-baseline.py` v4（`migrations` 欄與遷移帳前置、`sys_user` 帶界＋可變欄回寫、指派回補、清理面增 `sys_pwd_custody`、前綴增 `cpwd:`、seed 模式目標態與兩模式 `system_settings` 比對改合成、遷移不同步拒跑、清理面 seed_* 照舊拒跑）；RUNBOOK §9c；FR-045（閘）、FR-057、FR-058 | 兩工具、RUNBOOK §9c、`reference-src/schema-gates.md`、`schema-evolution-contract.md` | 早於 U4、U22；派發前主線斷言 dev 庫 `casbin_rule` max(id)＝163 且序列＝(163, true)（不符＝以 006 刀終態基準＋現行 v3 工具 restore〔dev 庫寫入點、逐步取 user 放行〕或停手升級） | 兩工具 `test` 綠＋拆前置／合成／序號推進即紅；收尾以 v4 取首份基準（唯讀） | 外 |
| U2 測試基建 | `UserRowsGuard`、`SeedUserRestoreGuard`、`PwdCustodyRowsGuard`、指派回補腿、`cpwd:` 逐鍵 track（tests 側 `UserWriteGuard`／`SeedUserWriteGuard`／`PwdCustodyWriteGuard`）、`ID_RANGES` doc 句改寫；FR-062 | `test_kit.rs`、`tests/common/mod.rs`、呼叫點 | 早於 U8～U13 | 守衛自證（植殘列→回基準、拆腿即紅）；全量 serial 綠 | R |
| U3 骨架 | ROUTES 49→61＋常數、兩 handler 空殼、十一域、registry 61、授權態矩陣、四支以本刀端點未註冊為前提之測試改植探針或依新路由現算改值、`handler/mod.rs` 檔頭共用件句；FR-001／002／061 | `router.rs`、`handler/{mod,user,user_center}.rs`、`contract.rs`、`role.rs`、`sys_casbin_policy.rs`、`test_references.py` | —— | 全量 serial 綠；`python3 -B tools/docsync test`（LL-00060） | R＋外層釘值測 |
| U4 m0003 | m0003（五句、rows_affected 斷言、down 反向）、演進帳九筆、seed 錨改對、選單刪碼守門＋`biz.menu.protectedButtonRemove`；FR-041～046 | `migration/src/*`、`schema-evolution.json`、`menu.rs`、`error.rs`、`model/facade/sys_casbin_policy.rs`、`contract.rs`、`test_kit.rs`、`system_settings.rs`（doc）、三檔 locale＋`app.d.ts`、活書 12 | U1；Amendment；名冊載入新列變異自證（派發前主線親跑＝ADR-00074 決定五） | 守門正負＋變異；schema 三閘綠；msg-key-gate 綠；全量 serial 綠 | RB |
| U5 facade 底座 | `sys_user`／`sys_user_role`／`sys_token`（迴圈撤票）／`session_event`／`sys_pwd_custody`／`AuditOperation` 5→8；`advisory_lock_user` 收窄＋compile_fail；FR-006／011／026 | `model/facade/*`、`model/audit.rs` | —— | doctest 正反；`authz_entrypoint_lint.rs` 腿⑤後半綠；全量綠 | R |
| U6 政策與明細通道 | `password.rs` 政策單點與 hash、冷卻件、壞值告警（計數族、`rules.yml`）、`BizData`（9→10）與 envelope、`msg-key-gate.py` 斷言 2 擴、DTO 遮蔽（含 `LoginReq`）；FR-032～035、FR-004／051（後端半） | `password.rs`、`obs.rs`、`error.rs`、`envelope.rs`、`login.rs`、`rules.yml`、`msg-key-gate.py`、`code-gate-contracts.md` §5、兩 `Cargo.toml` | 早於 U8 | 全量綠；`msg-key-gate.py test` 綠；告警規則檔形、`/metrics` 預註冊 0、計數出口單元測試綠（活體轉 Firing 移 U22） | R＋外層工具 |
| U7 包含規則與讀端 | `auth/no_escalation.rs`＋`guard_no_escalation`；getUserList／getDeletedUsers；`enforce.rs` 預告句改寫（BL-00048）；FR-005／007／008／021～023 | `auth/*`、`user.rs`、facade、`contract.rs` | U5 | 純函式全分支；分頁五案＋六欄過濾；全量綠 | R |
| U8 新增與編輯 | addUser／updateUser（固定序、值 diff no-op、空字串、全量替換＋角色列鎖、停用撤票、`finish_user_write`、經手表）；鍵 11；併發與 in-use／self-role 生產可達；零 reload 反向；FR-003／009～013／017／020／021／025／026／035 | `user.rs`、`error.rs`、`contract.rs`、三檔 locale＋`app.d.ts` | U2、U6、U7 | 每格負向＋空格案；每消費點兩負一正；拆判定即紅；全量綠 | RB |
| U9 刪除與復原 | deleteUser、batchDeleteUser（三段單調取鎖、整批 rollback）、restoreUser；鍵 1；FR-014～017 | 同上 | U8 | 整批 rollback、撞名兩腿、零回灌；全量綠 | RB |
| U10 踢除、重設、會話政策 | kick（`admin_kick`）、reset（政策＋冷卻）、sessionPolicy；`ModalLogoutByAdmin`（→11）、enforce 三向分派；login 第⑤步併發案；鍵 5；FR-004／018／027／035 | `user.rs`、`enforce.rs`、`cache/mod.rs`、`error.rs`、`login.rs`、locale | U8 | 三向各臂、冷卻邊界、已輪替列不動；全量綠 | RB |
| U11 換發重驗 | refresh 鎖內活性重驗、revoked 腿三向、refresh 10＋logout 1 案改種帳號列；FR-028／029 | `refresh.rs`、`logout.rs`、`test_kit.rs` | U2、U10 | 重驗三形、失效名單寫入失敗注入；全量綠 | R |
| U12 個人中心兩端點 | getPasswordPolicy、changePassword、`Identity.sid`、`change_pwd.rs`（`cpwd:`）、降級源 10→11、自助白名單＋`route.rs` 勘誤；鍵 4；FR-031／036～039 | `user_center.rs`、`route.rs`、`auth/*`、`throttle/*`、`cache`、`obs.rs`、locale | U6、U10 | 第 6 次比對前拒、成功即清、fail-open＋計數；白名單兩向案；全量綠 | RB |
| U13 unlockLogin 帳號維 | 交易化＋advisory＋包含規則＋源碼次序釘；FR-021（第 9 點）、FR-040（後端） | `handler/throttle.rs`、`contract.rs` | U7 | 帳號維套、來源維不套；未鎖帳號回成功落稽核 | R |
| U14 裁判面收口 | `wire_schema.rs` 受審名冊與偏離帳第三列；base-web 新檔型別與包裝四支＋快照重抽；registry 雙向、矩陣全量；`NO_ESCALATION_CALL_FILES` 腿；FR-008／053／061／064 | `wire_schema.rs`、`contract.rs`、`authz_entrypoint_lint.rs`、`wire-schema.json`、`rev6-user-{admin,center}.{ts,d.ts}` | U3～U13 之後 | `wire-schema.py check` 綠；名冊腿正反；全量綠 | RB |
| U15 繁中 runtime | `LangType`、三處註冊、預設 zh-TW、下拉三語（繁中項單行形新增型）、`<html lang>` 首開同步、`zh-tw.ts` 全樹標型、圈界註三語；FR-052／054 | `app.d.ts`、`src/locales/*`、`store/modules/app/index.ts` | U0 | 型別檢查綠；fork-delta-lint 綠＋變異 | B |
| U16 zh-tw-lint | 新碼面閘（ADR-00084 決定 7 四腿＋白名單）、pre-commit／bootstrap／RUNBOOK §12、八支碼面閘；FR-052 | `tools/zh-tw-lint.py`、`.githooks/pre-commit`（條件段與 `for t in` 自測迴圈）、`bootstrap.sh`、`tools/docsync/tests/test_hook_wiring.py`、README 工具樹、RUNBOOK §12、`code-gate-contracts.md` §8 | U15 | `test`／`check` 綠＋判準變異 | 外（必要時 B） |
| U17 使用者頁 | 清單、抽屜、搜尋卡、七碼、表頭屬性、三語 `page.manage.user.*`（含 `roleSeparator`）；FR-019／020／024／047／048 | `views/manage/user/*`、locale、`app.d.ts` | U14、U15 | 型別、fork-delta-lint、view-render-guard、seed-view-gate、route-artifact-gate 綠；圈界逐塊拔標記必報（LL-00058） | B |
| U18 浮層與解鎖入口 | 重設與產密浮層、`pwd-policy.ts` 與 `page.passwordPolicy` 塊（三語＋型節）、列操作三項、IP 規則頁解鎖鈕與彈窗（巢狀 (vii) 圈界）、view-render-guard 判準 (b)＋IP／使用者頁兩錨、RUNBOOK §9 句；FR-038／040／047／048 | 新檔四支（重設浮層、產密浮層、IP 解鎖彈窗、`hooks/business/pwd-policy.ts`）、抽屜產密鈕、`components.d.ts`（工具重算）、`user/index.vue`、`ip-rule/*`、locale＋`app.d.ts`、`tools/view-render-guard.py`、README 工具樹、RUNBOOK §9／§12 兩表、`code-gate-contracts.md` §3 | U12、U17 | 同 U17＋view-render-guard 自測正反與判準變異；巢狀 (vii) 塊逐檔字面計數恰 1（拔標記不觸發未圈界、其守＝PATCH 實數化後之對賬腿） | B＋外層工具 |
| U19 角色與選單頁按鈕碼 | 依碼逐鈕顯隱、表頭屬性、「門在頁級」碼註改述、角色與選單頁兩錨；FR-042（UI）、FR-048 | `views/manage/{role,menu}/index.vue`、`role/modules/role-operate-drawer.vue`（(iii) 圈界碼註）、`tools/view-render-guard.py`（兩錨） | U15、U18 | 同 U17 | B＋外層工具 |
| U20 個人中心、登入、明細轉譯 | 改密卡（消費 U18 之 `pwd-policy.ts`）、登入兩欄只驗必填、兩鍵轉譯、`FRONTEND_MSG_CONSUMERS`；FR-033／038／049～051 | `user-center/*`、`pwd-login.vue`、`request/index.ts`、`msg-key-gate.py` | U6、U12、U15、U18 | 型別、msg-key-gate、fork-delta-lint 綠 | B＋外層工具 |
| U21 文件 | 活書現在式（島 I 情境、三語、詞組消歧）、RUNBOOK 復核、R22 全掃、BL-00141 指向句、ADR⑧⑨ 草稿續寫；FR-030／059 | `docs/arc42/*`、RUNBOOK、`config.rs`、compose | 實作單元之後 | docsync 零錯；種子復掃零殘留 | 外（必要時 R） |
| U22 CDP 與治理 | CDP 三方對照（opus[1m]／xhigh；22080、32080 及 22089 一律以 `localStorage.setItem('SOY_lang', JSON.stringify('zh-CN'))`＋重載顯式設簡中）、告警活體實測（R11 決定 5）、zh-TW 審讀＋user 抽查、ADR-00070／款 20 實測、殘列演練、ADR⑧⑨ accepted＋活書 11；FR-056／058／065 | ADR-00081／00082、活書 11 | U1、U15～U20 之後；分岔表凍結 | SC-010；走查後 diff rc 0 | 外 |
| U23 收刀前承載體檢 | Day-1 三步（第 3 步 pristine 庫）、PATCH Amendment、BL 反向確認三條、帳本條文、FR-066 DoD | 憲法、PATCH ADR | 最後 | 全閘零紅；pristine 重放後三閘綠 | 外 |

**dev 庫寫入點**：U1 派發前（條件式）——序號斷言不符時以 006 刀終態基準＋現行 v3 工具 restore；U4 中段——①以 U1 v4 基準跑基準檔模式 restore 清界上殘列（遷移帳相等＝前置放行，免撞 id 164；seed 模式此時不可用＝演進帳已登 m0003）②重起 stack（一次性 migrate 服務套 m0003、rust-api 隨後載新判定面）③重拍本刀基準；U22——走查前 snapshot→走查寫入（自建帳號與角色）→殘列演練全量測試→restore→diff rc 0、告警活體實測（系統設定兩鍵改矛盾→觸發→改回）；U23——pristine 庫建立與重放（非 dev 庫）。其餘單元之測試寫入受清理守衛、對自建帳號。

**跨單元約束**：①Amendment 硬序：首個 base-web 既有檔 diff＝U4（locale backend）、須在 U0 Amendment 顆之後；名冊載入新列變異自證＝U4 派發前主線親跑（ADR-00074 決定五） ②U1 早於 U4（FR-057 (c)；m0003 進 dev 庫之時機隱性）與 U22；U2 早於 U8～U13 ③ROUTES 只在 U3 改（一次 61 條）、另跑 `docsync test`；其後改列序即同跑 ④鍵隨首發單元落地（名冊、三檔 locale、型節同批；逐鍵表＝contracts/msg-keys.md §6）：U4 1、U8 11、U9 1、U10 5、U12 4＝22（逐鍵首發＝contracts/msg-keys.md §1.1）；兩攜參鍵之 `BizData` 構造點住 `handler/user.rs` 兩組裝件——`passwordPolicy` 首發 U8 addUser、`pwdSetTooFrequent` 首發 U10 resetUserPassword（addUser 之標的為新帳號、經手表無先前時戳、不可能冷卻拒）；U6 之政策與冷卻件回領域型，免名冊雙向閘方向二（實發＝名冊）於 U6～U7 轉紅 ⑤三語同批（前端單元皆在 U15 之後） ⑥同檔序列鏈不並發：`router.rs`／`contract.rs`、`handler/user.rs`、`error.rs`＋locale＋`app.d.ts`、`test_kit.rs`、`enforce.rs`、`sys_user.rs`、`authz_entrypoint_lint.rs`、`views/manage/user/index.vue` ⑦紀律烤入：rev5 樹唯讀（RL-0064）、rust 容器內全程 serial、pnpm 容器內、review 只讀。

- **Rationale**: 工具與守衛前置＝FR-057 (c)／FR-062；m0003 寫與套同單元、先清殘列再套＝免 fail-loud 停機；裁判面收口在後端之後、前端之前＝006 刀 U11 同形（型別新檔先於畫面消費）；CDP 與治理同單元＝已知態先觀察後 accepted。
- **Alternatives considered**: brainstorm 草案序（工具在 m0003 之後：違 FR-057 (c)，棄）；包裝與型別新檔隨使用者頁（wire 裁判無右源，棄）；兩攜參鍵於 U6 落地（名冊雙向閘無實發點即紅，棄）；讀寫同單元（單元過大，棄）。

## R24 RL-0013 棄案反例回跑

| 題 | 棄案與棄因（反例） | 對所選方案回跑 |
|---|---|---|
| brainstorm 方案 B（US 垂直切片） | 首片須含完整底座、跨片同檔並發 | 底座 U5～U7 先落、寫端只消費、同檔鏈已序列化；**成立** |
| 方案 C（後端全先） | 前端一大片、CDP 回饋最遲 | 前端拆 U15～U20、U14 先定型別；**成立**（以拆分承擔） |
| brainstorm 風險 R10 候選①（角色頁編輯鈕不套顯隱） | 與 Q8 不一致；選單刪碼路照開 | 六碼受保護：撤 `role:edit`→整批拒；選單刪 `role:edit`→整筆拒；刪角色頁選單→受保護選單守門；**成立** |
| 候選③（寫端專擋撤 R_SUPER `role:edit`） | 與受保護機制並存兩套、刪碼路照開 | 沿用既有受保護機制＋GR1b；**成立** |
| 候選④（R_SUPER 恆回全碼） | 撤碼成功而畫面不反映＝真相與顯隱分離 | 撤即拒＝兩者一致；**成立** |
| 候選⑤（已知態＋RUNBOOK 救援） | 自鎖後只能直打 API 或改庫 | UI 上無失去 `role:edit` 之路徑（SC-007）；**成立** |
| Q2 連帶面（棄 won't-fix ADR、取滯後卷） | 003 刀延後義務斷鏈 | BL-00141 承載並寫回收時點；`config.rs`／compose 指向句改指（R22）；**成立** |
| Q4 連帶面（棄不接繁中） | 無 rev5 基準、譯文量、每刀三語 | GR5 驗收形、CDP 三側顯式簡中；U15／U16；型別三語機器守＋`zh-tw-lint`；**成立** |
| Q8 連帶面（棄只做使用者頁） | 角色頁依碼後超管可自撤 `role:edit`（風險 R10） | GR1／GR1a／GR1b 封兩路；Admin 無效鈕隨 GR7 消失；**成立** |
| Q9 連帶面（棄頁首雙維彈窗） | 修憲面擴大；列解鎖不知鎖定狀態 | (v)＋(vii)；未鎖帳號回成功並落稽核（GR3：無洩漏無副作用）；`ipRule:unlock` 獨立顯隱；**成立** |
| Q15 連帶面（棄同值照寫照稽核） | 逐域分岔、同值無稽核 | ADR⑦ 明文逐域；值 diff 於鎖內歸一後比對；舊值覆寫由「只在改動時送」擋；**成立** |
| GR1a（棄 `role:edit` 單碼） | 單碼已足保回復路徑 | 六碼：超管不能自撤（by design）、受保護 19→25、按鈕維不入封死集＝判定面不受影響；其餘碼可撤可加回；**成立** |
| GR4（棄沿用 `user:unlock`） | 授帳號維碼即連帶顯示來源維鈕＝兩頁語意混同 | 兩碼各顯其頁、共用一包裝；碼只管顯隱、端點授權照判；**成立** |
| 改密節流前綴（棄 `throttle:`） | 以 `throttle` 前綴批次清解鎖／captcha 標記（含走查還原之前綴清理）時連帶清改密桶＝計數歸零、攻擊者重得五次 | 走查清理另增 `cpwd:` 前綴、`RedisKeysGuard` 逐鍵 track；降級源獨立；**成立** |
| 指派寫端角色列（棄只讀不鎖） | 無鎖讀 R 活→deleteRole 鎖 R 軟刪 commit→指派插入（FK 之 KEY SHARE 與非鍵欄 UPDATE 相容）＝掛上已刪角色；違 G5 | 鎖形：deleteRole 先＝鎖內重驗見刪→`roleNotFound`；指派先＝deleteRole 等鎖後 in-use 見新指派→拒；兩鎖集只交於角色列且皆升序＝無 ABBA；**成立** |
| 批次取鎖序（棄逐 id 交錯形） | u5（T={3,9}）、u7（T={4}）交錯＝鎖 3、9 再 4；另一編輯 u8（{4,9}）升序先 4 等 9⇒ABBA；且列鎖後才取 advisory | 三段單調：advisory 全取→使用者列全鎖→聯集 {3,4,9} 一次升序⇒不成環、advisory 恆早於列鎖；**成立** |
| 不立 finish 名冊閘 | 新撤票寫端漏寫失效名單 | 每支撤票端點測試斷言失效名單（SC-005）＝漏呼即紅；名冊閘抓不到既有檔內漏呼；**成立** |
| m0003 冪等形（棄 ON CONFLICT／nextval） | ON CONFLICT：id 164 被殘列佔用即靜默略過而遷移帳記已跑；nextval：各庫 id 不同、演進帳 values 只對其一 | 顯式 164＋rows_affected 斷言：不符即整支回滾、migrate 非零退出、rust-api 不啟動（fail-loud）；U4 套前先 restore 清殘列；`setval` 不倒退；**成立** |
| `main.ts` 不改 | 改之代價＝高風險 upstream 檔為開發期提示新增 ★ 檔；外掛只認 zh／en | zh-TW 下提示為英文＝開發期、非產品面、記已知態；**成立** |
| ADR⑫ 不另立 | 同一事實兩個家；CDP 追加即 supersede | 分岔表單一登記、CDP 前凍結、追加須親決；**成立** |
| zh-TW 檢查載體（棄一次性腳本） | 後續刀三語無閘回歸 | 碼面閘入 pre-commit 與 bootstrap；白名單收斂誤判；**成立** |
| 走查工具 seed 合成射程（棄系統設定照舊拒跑） | 日後 migration 增改設定鍵＝兩模式皆比對 `system_settings` 而拒跑＝工具全廢、與 user 選「本刀做」時之預期不符 | spec FR-057 (b)（2026-10-05 納入）：兩模式設定比對皆以凍結 seed ⊕ 演進登記合成、增改刪三形自測＋變異；仍拒跑之演進形兩種＝往清理面各表塞 seed 列之 migration（明列邊界、屆時另擴工具）＋合成面表之結構演進屬 schema 閘合成未內建之形（與 gate2 同停、同一擴充點補齊即兩者恢復）；其餘拒跑屬前置不符（基準遷移帳不等、repo↔現庫遷移不同步），重拍或套遷移即解；**成立** |

## R25 交 tasks 與實作期定值之事項

- 新建件名照本刀命名（R6、data-model §12、contracts 共用型節）；msg 鍵逐鍵發出點與 data 形住 `contracts/msg-keys.md`；`FRONTEND_MSG_CONSUMERS` 預期 +2（`service/request/index.ts` 兩攜參鍵各 1、名冊 1→3），U20 以實掃為準。
- 範圍欄實數：單元出口以標記現算；依 ADR-00074 P-c①——差額之標記皆在紀律欄射程內＝記入單元收尾、延收刀前 PATCH 實數化；射程外改點＝停手升級；「不預估」項 U23 一次實數化；PATCH ADR 配號＝U23 當下下一號。
- U0 親決結果（ADR-00074 親決題索引：P-a 用途號、P-c 範圍欄與出口程序、I-a～I-d7 島 I 字面、H-a、S-a 活書等）＝同步改寫 ADR① 與憲法、回寫 tasks 對應條。
- 政策壞值 warn 日誌之 target 與欄位＝R11；告警活體實測於 U22（走查窗；R11 決定 5）。
- `incr_with_window` 原子形與 `cpwd:` TTL 設置形＝U12（契約＝R11）；守衛水位常數與自證案數＝U2（形＝R15）；m0003 錯誤訊息字面與 down 句形＝U4（R13）；選單刪碼守門之查詢件＝U4（拒因與位次已定）。
- `zh-tw-lint` 用語表與白名單初版＝U16 依 U15 審讀定；AI 逐頁審讀與 user 抽查紀錄＝U22 收單 commit 訊息與 tasks 註記（不寫本機工作區路徑）。
- 分岔表凍結時點＝U22 起手；ADR⑧ 款號與實測結果、ADR⑨ 八詞落字＝U22；活書島 I 情境字面＝U21；`wire-schema.json` 重抽實數＝U14；Day-1 第 3 步命令＝RUNBOOK §10 既有形。
- errata 處數施工時現算；`arch_impact` 收刀時以 `git diff --stat <merge-base>..HEAD -- docs/arc42/` 現算；淨流量本窗 −4（刪 10、新記 6：BL-00140／BL-00141／BL-00142／BL-00143〔本刀 U10 誕生、user 2026-10-11 裁定本刀內修〕／BL-00144〔本刀 U12 誕生、user 2026-10-12 裁定本刀內修〕／BL-00145〔本刀 U13 期間誕生、user 2026-10-12 裁定延後重評〕）。
- Technical Context 零 NEEDS CLARIFICATION。
- **plan 期 spec 字面修補**（2026-10-05；主線工程判斷＋user 親決兩題；修補清單之家＝本段）：E1 ★ 軌道表刪 `src/main.ts` 候選列與 Edge Cases 定案句；E2 清理面「五表」→「各表（本刀起含經手表）」三處；E3 FR-056 ⑫ 與摘要＝併入分岔表、不另立；E4 FR-041 `ipRule:unlock` 說明字面；E5＋E12 並行編輯落點＝ADR⑦、恆送欄集；E6 m0003 新列 id 與冪等形；E7 FR-008 excel 示範頁＝殘存消費面（user 親決）；E8 FR-021 與 Key Entities 之 T 濾已軟刪；E9 FR-025 負向案形；E10 FR-061 四支；E11 FR-051 之 002 契約原檔不改（ADR-00041 決定 3）；E13 同值 no-op 句與 FR-018 會話政策必填；E14 US6 場景 4 與兩處「含 006 刀終態基準」（v3 檔形先拒）；E15 仍拒跑之演進形兩種；E16 FR-035 與冷卻邊界之剩餘秒數；E17 FR-037 與 Key Entities 之計數窗；E18 FR-015／US1 場景 7 撞名撞信箱之鍵；E19 ★ 登記表四列改述與 role-operate-drawer 碼註列（19 列）；E20 FR-055④ (iii) 改寫並擴範圍與 (iii) 列門在頁級句；E21 Edge 值域狀態讀寫兩向；E22 FR-006 unlockLogin 處理序；E23 FR-065、SC-010、Edge 繁中介面之 CDP 三側顯式簡中與 `<html lang>` 首開同步；E24 刻意分岔表與 Edge 繁中介面之 pro-naive 已知態（user 親決）；E25 FR-060 補 BL-00142。檢核表 16／16 不變。
