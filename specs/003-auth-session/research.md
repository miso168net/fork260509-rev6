# Research — 003-auth-session（Phase 0）

> 輸入：spec（clarify Q1～Q4 定案 2026-09-08）＋brainstorm §0～§6（Q1～Q10 拍板、五項工程判斷）＋`rev5:003-auth-session` 全套（spec／research R1～R9／data-model／contracts 三檔／plan；唯讀、凍結 SHA）
> ＋rev5 對應碼唯讀勘查（2026-09-08、逐檔行數與 crate API 要點）＋crates.io／CHANGELOG 實查（2026-09-08）。每題 Decision／Rationale／Alternatives。
> CLAUDE.md §2 兩件必列：R2 rev5 對應碼清單、R3 rev6 拍板差異點（承 rev5:ADR 0019 形）；RL-0013 棄案反例回跑＝R16。

## R1 依賴釘版與雙源核對（全域版本紀律；user 逐支拍板 2026-09-08 D1～D5）

- **Decision**: 八支新進（六支 auth 依賴＋`log`＋`getrandom`）逐支雙源對照——rev5 lockfile／rev6 lock vs crates.io 最新穩定（2026-09-08 查）；三支同值直採（captcha／hex／getrandom）、五支分歧 user 逐支拍板**全取最新穩定**（D1～D5）。
- **Rationale**: 001／002 同型先例（分歧取最新）；五支破壞性改動皆經 CHANGELOG 實查——四支之主路徑 API 不在破壞面，argon2 0.6 的 `rand_core`／`OsRng` 破壞面**觸及**本刀取亂數路徑、處置＝新增具名 CSPRNG 依賴 `getrandom`（rev6 lock 現值 0.4.3＝最新穩定、同值直採、主線回報＝D6）；MSRV 最高 1.88（jsonwebtoken／redis）≤ rev6 toolchain 1.96.1。
- **Alternatives considered**: 全沿 rev5 lock（重打字摩擦最小、但落後一至四個版本、後續再開維護批升版；002 對 jsonschema 同型棄案）；只升 minor／patch、major 沿 rev5（jsonwebtoken 10→11 破壞面不觸及主路徑、無理由獨留）。

| crate | rev5 lock | crates.io 最新穩定（2026-09-08） | 落地（user 拍板） | features（server 側） | MSRV | 用途 |
|---|---|---|---|---|---|---|
| jsonwebtoken | 10.4.0 | **11.0.0**（2026-07-24） | **11.0.0**（D1） | `default-features = false`＋`rust_crypto`（★硬要求：漏開＝decode 執行期 panic、非編譯錯；`use_pem` 不需） | 1.88 | access／refresh／captcha 三處 HS256 簽驗 |
| argon2 | 0.5.3 | **0.6.0**（2026-08-27） | **0.6.0**（D2） | 預設（`alloc`／`getrandom`／`password-hash`）；★0.6 把 `simple` 改名 `password-hash`、移除 `std` | 1.85 | seed argon2id PHC 驗章＋`dummy_verify` 時序等化 |
| redis | 1.3.0 | **1.7.0**（2026-09-05） | **1.7.0**（D3） | `default-features = false`＋`connection-manager`＋`tokio-comp`（1.7.0 兩名皆在、實查） | 1.88 | denylist／grace／last_activity／idle-emitted／captcha nonce／節流 L1 |
| captcha | 1.0.0 | 1.0.0（同值） | 1.0.0 | `default-features = false`（關 `audio`＝唯一可關） | — | 圖形題產圖 |
| sha2 | 0.10.9 | **0.11.0**（2026-03-25） | **0.11.0**（D4；★lock 將同時存 sqlx 間接帶的 0.10.9＝兩份副本、已知代價） | 預設（`alloc`／`oid`） | 1.85 | `token_hash`＋captcha `ans_mac` |
| hex | 0.4.3（rev6 lock 已在） | 0.4.3（同值） | 0.4.3 | 預設 | — | hash hex 編碼 |
| log | 0.4.33（rev6 lock 現值） | **0.4.34**（2026-08-22） | **0.4.34**（D5；容器內 `cargo update -p log` 統一間接依賴、單一副本；★取代 spec FR-034 之「釘 0.4.33」字面——該句寫於 D5 拍板前；「零新套件」仍成立、差別只在版本推進一次） | 預設 | — | 僅 `log::LevelFilter::Debug`（BL-00026） |
| getrandom | —（rev5 經 argon2 之 `rand_core::OsRng` 取亂數、無直接依賴；rev6 lock 現值 0.4.3 為間接依賴） | 0.4.3（2026-06-17） | **0.4.3**（D6 主線自拍：lock 現值＝最新穩定、同值直採） | 預設 | — | CSPRNG：captcha nonce 與答案拒絕採樣、sid／jti uuid v4 素材（`getrandom::fill`） |

**API 差異守則**（implementer 烤入；rev5 對應檔只當藍本、照新版 API 寫）：
- jsonwebtoken 11：`EncodingKey::from_secret`／`DecodingKey::from_secret`／`encode`／`decode`／`Validation::new(Algorithm::HS256)`＋`leeway = 0`＋`validate_exp`＋`set_issuer`／`set_audience` 皆沿用；`Algorithm` 等 enum 轉 `non_exhaustive` ⇒ match 補 `_` 臂；`ErrorKind::ExpiredSignature` 分派 3333 不變。
- argon2 0.6：`PasswordHash::new(phc)` → `Argon2::default().verify_password(pw, &parsed)` 同形（`password_hash` 0.6）；★`argon2::password_hash::rand_core` 於 0.6 系（rand_core 0.10）已無 `OsRng`＝rev5 取亂數路徑不可沿用——CSPRNG 一律改走 `getrandom::fill(&mut buf)`（四處：captcha nonce／答案拒絕採樣／sid／jti）；`SaltString::generate` 本刀不用（不產 hash）。
- redis 1.7：`redis::aio::ConnectionManager::new(client)`／`redis::cmd(..).query_async::<T>(&mut conn)`／`SET NX EX`／`pipe().atomic()` 沿用；`FromRedisValue` 收 owned 值 ⇒ GET 回值型別一律 `Option<String>` 明寫。
- sha2 0.11：`Sha256::digest(bytes)`／`Sha256::new().update(..).finalize()` 同形（`digest` 0.11）。
- captcha 1.0.0：`Captcha::new()` → 逐字 `add_char()` → `apply_filter(Noise)`／`Wave` → `as_base64()`；字型涵蓋自證走 `supported_chars()`。

版本單一來源＝`rust-api/Cargo.toml` workspace.dependencies（八支加列、含 `log`）；`server/Cargo.toml` 逐 crate 列 features＋註解重寫（含 root「不引 argon2」舊拍板翻案＝ADR、R3-19）。**明確不進**（rev5 有、本刀域外或紀律禁）：lettre／toml／arc-swap／once_cell／futures-util／xdb／`subtle`（captcha 模組 doc 明載不得引）。

## R2 rev5 對應碼清單（實作單元動工前逐檔先讀；rev5 rust-api 凍結 worktree `92919b9`＝終態、含後刀增量——先看 003 邊界 diff、再看終態）

rev5 003 邊界＝`git -C ../fork260509-rev5/rust-api diff --name-status bb29a0e 862294e -- server/`（首 commit `2a593c3` 之前一筆→末筆）；base-web 邊界＝`5089c28f..24317d01`（18 檔）。★行數為 rev5 終態行數（含後刀增量與 inline `#[cfg(test)]`，多支測試占大半）、只供量級估算。

| rev5 檔（`../fork260509-rev5/rust-api/server/`） | 行數 | 003 A/M | rev6 對應 | 處置（重打字＋註解 rev6 語境；rev5 出處帶 `rev5:`） |
|---|---:|---|---|---|
| `src/auth/jwt.rs` | 287 | A | 同 | Claims 8 欄／HS256 簽驗（access／refresh 各自秘鑰）／TTL 公式／`ttl_from_settings` 三重 fail-loud／`token_hash`；API 照 R1 守則 |
| `src/auth/enforce.rs` | 1398 | M | 同 | 真驗章＋denylist 四級降級鏈（redis 命中→reason 三向／nil 放行／Err→PG `has_active_in_chain`／PG 亦故障不盲放）＋`denylist_hit_total`；002 之 `require_policy`／`enforce_role_path_method`／掛點守恆不動；cfg 分支收斂為單一驗證器 |
| `src/auth/mod.rs` | 40 | M | 同 | `jwt` 進場、`dev_identity` 汰除、`Identity` 欄集不動；★`user_name` 欄 doc 改寫為已知態（真驗章下 Claims 無帳號名 ⇒ `enforce_mw` 填空字串、消費者以 uid 經 sys_user facade 現查；本刀只在 `enforce_mw` 內部消費 claims.sid、不擴 Identity 欄） |
| `src/auth/dev_identity.rs` | — | **D** | 整檔刪 | 汰換射程實查＝`auth/enforce.rs`（`verify` 呼叫點＋cfg 分支收斂）／`auth/mod.rs`／`lib.rs`／`router.rs`（3 處測試 token）／`handler/system_settings.rs`（dev token 字面以 `grep -c 'dev-super\|dev-admin\|dev-user'` 現算、現 103 行；integration 測試面、斷言不動）／`tests/contract.rs`（14 處）（R7-2） |
| `src/cache/mod.rs` | 593 | A | 同 | `SessionCache`＝`ConnectionManager`；key builder 族（denylist／last_activity／idle_emitted／grace／throttle_lock_user／throttle_captcha_used；★不含 ip 維與 unlock 鍵——R3-11）；`REASON_KICKED`／`REASON_REVOKED`；★`REASON_ADMIN_KICK`／`cpwd` 鍵為 `rev5:007` 增量、不搬 |
| `src/throttle/mod.rs` | 2918 | A | 同 | 帳號維三區（IP 維全拔＝`DIM_IP`／`DEFAULT_IP_*` 不搬）；常數 `THROTTLE_LOCK_TTL_SECS=900`／`CAPTCHA_TTL_SECS=300`／`CAPTCHA_ANSWER_LEN=4`／34 字集／`DEFAULT_{MAX_FAILS,WINDOW_MINUTES,CAPTCHA_AFTER}=5/15/2`／`LOGIN_USER_NAME_MAX=64`／`LOGIN_PASSWORD_MAX_BYTES=512`；★新增矛盾組合退常數腿（Q3） |
| `src/captcha/mod.rs` | 333 | A | 同 | 撞名消歧三規則（本檔 `::captcha::`／他處 `crate::captcha::`／lib.rs 絕不裸寫）＋檔頭碼註；`CaptchaClaims` 四欄；不驗 iss/aud、`leeway=0`；`ans_mac`；拒絕採樣亂數 |
| `src/handler/auth/login.rs` | 1930 | A | 同 | 十一步（spec FR-004）；`dummy_verify` 時序等化；advisory lock 走 facade `sys_user::advisory_lock_user` |
| `src/handler/auth/refresh.rs` | 2819 | A | 同 | rotation 狀態機（FR-007）；`GRACE_TTL_SECS=30`；idle 判定於 `active` 腿（門檻＝`refresh_secs − access_secs`、N 取自本次 `ttl_from_settings`＝Q4 總則之實作形） |
| `src/handler/auth/logout.rs` | 810 | A | 同 | 冪等（FR-010） |
| `src/handler/auth/user_info.rs` | 249 | A | 同 | 四欄（FR-006） |
| `src/handler/auth/alt_stub.rs` | 28 | A | 同 | `not_supported_stub()` ×4 |
| `src/handler/auth/mod.rs` | 17 | A | 同 | 目錄五檔（`rev5:R3-6`） |
| `src/handler/route.rs` | 548 | A | 同 | 樹組裝／`home` 收斂律／`constant = TRUE`／`isRouteExist` |
| `src/handler/captcha.rs` | 89 | A | 同 | `crate::captcha::issue` |
| `src/handler/mod.rs` | 75 | M | 同 | 模組宣告擴編 |
| `src/model/password.rs` | 984 | A | 同 | `verify`／`dummy_verify`（`OnceLock` 快取 dummy PHC）；★`hash`／`PasswordPolicy`／`NewPassword` 為 `rev5:007` 增量、不搬（本刀不產 hash） |
| `src/model/facade/sys_token.rs` | 716 | A | 同 | `find_by_hash_for_update`／`rotate`（次序不可反）／`has_active_in_chain`／`revoke_family`／`revoke_others_of_user`／`revoke_row`；★`revoke_all_of_user` 若無本刀消費者則不搬 |
| `src/model/facade/session_event.rs` | 603 | A | 同 | append-only insert |
| `src/model/facade/sys_login_attempt.rs` | 1212 | A | 同 | append-only insert＋滑動窗計數（GREATEST 三源、unlock 綁 NULL、窗下界） |
| `src/model/facade/sys_menu.rs` | 5509 | A | 同（只搬讀面） | dynamic 選單讀面＋`to_menu_route`；★寫面為 `rev5:005` 增量、不搬 |
| `src/model/facade/sys_user.rs` | 3892 | A | 同（只搬 auth 消費面） | 登入鏈讀取＋`advisory_lock_user`（rev5 由 `rev5:007` 自 login.rs 上提；rev6 直接落 facade）＋寫 `session_id`；其餘為 `rev5:007` 增量、不搬 |
| `src/model/facade/sys_role.rs` | 2785 | A | 同（只搬讀面） | 啟用角色依 id 升冪＋`role_home` |
| `src/model/facade/mod.rs` | 139 | M | 同 | 模組宣告擴編（六支） |
| `src/model/facade/test_kit.rs`（rev6 既有） | — | — | 擴充 | R7-10：真 DB＋redis 五欄 state 建構、redis uniq 前綴、三支 sequence 重設守衛（承 rev5 `model/mod.rs` 之 `test_db`／`real_app_with`／`TEST_CAPTCHA_SECRET` 形，rev6 落既有 test_kit） |
| `src/state.rs` | 101 | M | 同 | 五欄＋`JwtConfig{access_secret, refresh_secret, iss, aud}`；封條翻案（clarify Q1、ADR） |
| `src/error.rs` | 422 | M | 同 | 三變體＋`MSG_KEYS` 7→13＋八處測試改對（R7-3）；檔頭與 doc 四處自陳字面（「變體集恰六」「002 刀不帶」「跨端閘…不入 002 刀、BACKLOG 承載」「002 刀恰七鍵」）同批改現在式、`errata` 復掃 |
| `src/router.rs` | 2100 | M | 同 | ROUTES 4→16、`ROUTES_COUNT`；兩道 fallback 既有（002） |
| `src/config.rs` | 1343 | M | 同 | 六 getter（`jwt_secret`／`refresh_token_secret`／`jwt_iss`／`jwt_aud`／`redis_url`／`captcha_secret`＋`*_with` 注入形；`_FILE` 沿 `env_or_file`） |
| `src/request_context.rs` | 647 | M | 同 | rev6 現為空結構；取 rev5 **003 形**（`from_headers`：real_ip／x_forwarded_for／ip_confidence 原樣轉錄）、★不取 `rev5:004` 換血後的 `from_trust` 形 |
| `src/obs.rs` | 411 | M | 同 | 三序列 pre-register（label 集＝R5 表；`denylist_hit_total{source}` 恰二） |
| `src/main.rs` | 539 | M | 同 | boot：`cache::connect(redis_url)` fail-loud panic、`JwtConfig` 組裝、`captcha_secret` 注入；BL-00026 `sqlx_logging_level(Debug)` |
| `src/lib.rs` | 38 | M | 同 | 模組樹＋「絕不裸寫 `captcha::`」碼註 |
| `src/model/mod.rs` | 4192 | M | 同 | rev5 `test_db` 內容不搬（rev6 對應＝test_kit 擴充、上列）；rev6 同名檔須加 `pub mod password;`、檔頭現在式自述同批改 |
| `src/handler/system_settings.rs` | — | M | 同 | dev token 字面（grep 現算、現 103 行）之 integration 測試改真 token 形（斷言不動、FR-033）＋`AppState` 建構點 2 處改五欄＋`SeedRestoreGuard` 三件搬出至 `test_kit`（改 `use`）＋BL-00041 註解 |
| `Cargo.toml`（server） | — | M | 同 | 逐 crate features＋依賴清單註解改寫（R1）；root `Cargo.toml` workspace.dependencies 八支＋「不引 argon2」句翻案 |
| `src/model/facade/sys_user_role.rs` | — | M | 不納本刀 | rev5 003 順手加 `roles_of_user` 次段 DbErr 機器守（`rev5:B-050`）；rev6 不納射程、收刀 `backlog_add` 立一條（觸發＝下次動該 facade 或補 DbErr 覆蓋時）——延後不得無家 |
| `tests/contract.rs` | 3278 | M | 同 | 16 case（`verify_auth_login`／`_refresh_token`／`_logout`／`_login_captcha`／`verify_alt_stub` ×4 區別手法／`verify_authed_unauthenticated_8888`／`verify_route_*` 三支） |
| `tests/common/mod.rs` | 533 | M | 同 | `stub_state` 五欄（cache None、captcha 字面 `stub-captcha`）；connect_lazy 假連線既有（rev6 002 已採 `rev5:ADR 0034` 形） |
| `tests/authz_entrypoint_lint.rs` | 1134 | M | **rev6 無此檔** | must-list 換檔義務不適用（R3-10） |
| `tests/entity_access_lint.rs` | 453 | M | 同 | 新 facade 六支入唯一管道射程；rev6 現無 `dev_identity` 指名列 |
| `tests/wire_schema.rs` | 5487 | 緊接下一筆補 | 同 | 裁判面補 `Api.Auth` 三型（UserInfo／LoginToken／LoginCaptcha）與 `Api.Route` 兩型 case（R7-8） |
| `tests/fixtures/wire-schema.json` | 4039 | M | 同 | 容器內重抽（新檔 `rev6-auth.d.ts` 入快照） |

| rev5 base-web 檔（`../fork260509-rev5/base-web/`） | rev5 標記數 | 003 | rev6 對應 | 處置 |
|---|---:|---|---|---|
| `.env`（2）／`.env.test`（1）／`.env.prod`（1） | 4 | M | 同（token `rev6-inline`、刀號 `003-auth-session`） | ADAPT 四行、標記逐字形見 contracts/code-gates.md §1 |
| `src/store/modules/route/index.ts` | 1 | M | 同 | AUTH-WIRING(a) |
| `src/store/modules/auth/index.ts` | 8（含後刀） | M | 同 | LOGIN-CAPTCHA(i)：login 簽名加 captcha 參＋失敗 msg 回傳鏈（rev5 8 處含後刀增量、本刀估 ≤4） |
| `src/views/_builtin/login/modules/pwd-login.vue` | 11 | M | 同 | LOGIN-CAPTCHA(i)：軟區條件渲染塊＋提交鏈；三顆快速登入鈕零 inline |
| `.../{code-login,register,reset-pwd}.vue` | 各 2 | M | 同 | AUTH-WIRING(b) |
| `src/hooks/business/captcha.ts` | 5 | M | 同 | AUTH-WIRING(c) |
| `.../global-header/components/user-avatar.vue` | 3 | M | 同 | LOGOUT-UX(i) |
| `src/service/request/index.ts` | 6 | M | 同 | I18N(i)：`translateBackendMsg`／`translateDetailValue` |
| `src/typings/app.d.ts` | 28（含後刀） | M | 同 | I18N(iii)：只補 `backend` 必填型節（本刀 1 處） |
| `src/locales/langs/{en-us,zh-cn}.ts` | 36（含後刀） | M | 同 | I18N(ii)：插 `  backend: {` 樹 13 鍵（rev5 22 鍵含九鍵白名單、不搬） |
| `src/locales/langs/zh-tw.ts` | 1 | M（rev5 由 002 建） | **新建** | 裸 object 錨點檔 13 鍵、檔頭 `BASE-WEB-I18N-WIRING+` |
| `src/typings/api/rev5-auth.d.ts` | 1 | A | `rev6-auth.d.ts` | declaration merging 併入 `Api.Auth`（`LoginCaptcha{captchaId, captchaImg}`） |
| `src/service/api/rev5-auth.ts` | 2 | A | `rev6-auth.ts` | `fetchLoginCaptcha`／`fetchLogout`／四 stub wrapper；不入 barrel |

| rev5 工具 | 行數 | rev6 對應 | 處置 |
|---|---:|---|---|
| `tools/walkthrough-baseline.py` | 782 | `tools/walkthrough-baseline.py` | 隨遷工具（R10；四型失效引用 rev6 化） |
| `tools/docs-sync.py` 內 Lint24（`scan_backend_msg_keys` 等） | — | **新寫** `tools/msg-key-gate.py` | 形制翻案（clarify Q2；R9）：逐檔雙向全等、無白名單；rev5 抽取三面（Biz 字面／常數間接形／`key()` 臂）在 rev6 由 `MSG_KEYS` 名冊＋Biz 字面兩面取代 |

## R3 rev6 拍板差異點清單（相對 rev5 003；防回歸清單 A——實作單元 prompt 烤入）

| # | rev5 003 行為 | rev6 拍板 | 出處 |
|---|---|---|---|
| R3-1 | 標記 token `rev5-inline`、新檔 `rev5-auth.d.ts`／`rev5-auth.ts`、刀號 `003-auth-session` | token `rev6-inline`、新檔 `rev6-auth.d.ts`／`rev6-auth.ts`、刀號同名 | 憲法 §III |
| R3-2 | `.env*` 在 fork-delta-lint 射程外＝人工紀律＋BACKLOG 立「射程擴 `.env*`」 | `.env*` 在射程內（`S1_NEW_FILE_FACE` 含根層 `.env*`）＝機器守；不立該 BL | spec FR-028 |
| R3-3 | B-047 前置研究（axum `method_not_allowed_fallback` 存在性）＋新增第二道 fallback | 002 已落兩道 fallback（4040 信封）；本刀零前置、12 條新 route 自然納入 | spec Edge Cases |
| R3-4 | msg key 跨端閘＝docs-sync Lint24 三向（⊆／白名單存在／白名單腐化）＋九鍵白名單＋`gen.msg_dict` 生成器與 Day-1 豁免拔項 | 新工具 `tools/msg-key-gate.py`：`MSG_KEYS` ⇔ 三檔 backend 子樹逐檔雙向全等、無白名單、零生成物、零豁免；立 ADR | clarify Q2、R9 |
| R3-5 | i18n 三語 backend 樹 22 鍵（13 實發＋9 白名單）；`zh-tw.ts` 由 002 建、本刀補 6 鍵 | 三檔各 13 鍵；`zh-tw.ts` 本刀自零建（002 拍零 locales 改動） | brainstorm Q3、spec FR-026 |
| R3-6 | Amendment 四步全在 tasks 首單元 | ADR draft 於 plan 期落 feature branch（本刀＝`ADR-00026` proposed）；tasks 首個主線任務只跑親決→accepted→bump→generate | brainstorm Q5 |
| R3-7 | 島 B／D／E 條文＝rev5 v1.3.0 字面 | 島 B 加「單一會話只於登入事件判定；翻轉不影響既有會話」（Q9）；跨島總則「每個設定鍵只在其消費事件當下讀現值；已簽發 token 的壽命與已建立會話不追溯」（clarify Q4）；島 E 加「節流設定鍵矛盾組合（captcha_after > max_fails）視同不可用→退常數＋告警」（clarify Q3） | R8 |
| R3-8 | `AppState` 五欄（jwt／cache Option／captcha_secret） | 同形（clarify Q1）；封條翻案 ADR 序號隨落檔取 | spec FR-032 |
| R3-9 | 走查工具指 rev5 dev stack（compose 專案＝rev5 根）、禁 rev4 對照 stack | 指 rev6 dev stack（compose 專案＝rev6 根、埠 3xxxx）、★絕不指 rev5 對照 stack（2xxxx） | R10 |
| R3-10 | `dev_identity` 汰換須換兩支 lint must-list（`authz_entrypoint_lint.rs`／`entity_access_lint.rs`） | rev6 無 `authz_entrypoint_lint.rs`、`entity_access_lint.rs` 無 dev_identity 指名列 ⇒ 改 `auth/mod.rs`／`lib.rs`／`auth/enforce.rs`（`verify` 收斂）＋三處測試面真 token 化（`router.rs` 3、`handler/system_settings.rs` grep 現算約百處、`tests/contract.rs` 14） | rev6 實碼核實 |
| R3-11 | unlock marker 不讀 redis、SQL 參數位綁 NULL | 同（沿 `rev5:R3-17`）；cache key builder 不含 unlock 鍵、degraded source 集不含 `redis_unlock_marker` | spec FR-014 |
| R3-12 | `request_context.rs` 003 形（`from_headers`）後由 `rev5:004` 換血 | rev6 自空結構起家、取 003 形；004 ip-trust-anchor 接手時換血 | spec FR-018 |
| R3-13 | 六 crate 沿 rev4 釘版（argon2 0.5.3／jsonwebtoken 10.4.0／redis 1.3.0／sha2 0.10.9）；亂數經 argon2 之 `rand_core::OsRng` | 五支取最新穩定（R1）＋新增 `getrandom` 取亂數（D6）；API 差異守則烤入；★spec FR-034 之 log 0.4.33 由 D5 取代為 0.4.34 | user 拍板 D1～D5 |
| R3-14 | 走查工具掛 rev5 名冊形 | 進 `NON_GATE_TOOLS`＋GT-12 自測＋bootstrap `run_tool_test`＋README 樹＋RUNBOOK §12 工具鏈速查列（非碼面閘表） | brainstorm 工程判斷 3、R10 |
| R3-15 | — | BL-00037 ①②同批收（pre-push 面接線守衛＋selftest-docsync 觸發放寬；bootstrap 名冊自 tracked 檔集推導） | brainstorm Q6、R11 |
| R3-16 | — | BL-00026（boot 鏈 `sqlx_logging_level(Debug)`＋`log`）與 BL-00041（兩處裸前代刀號＋`SUB_SCAN` 子庫腿）刀內收 | spec FR-034、R12 |
| R3-17 | 同批 ADR 面含「ADR 0021 §3 收窄」「B-047 4040 解讀」「R5 已知態集 ADR」 | rev6 五筆 ADR（主 Amendment／AppState 翻案／argon2 翻案／快速登入鈕已知態／跨端閘形制）；無 ADR 0021 對應（rev6 無該 ADR）、B-047 不適用、已知態集歸活書與 BL | spec FR-038 |
| R3-18 | 快速登入鈕已知態＝ADR＋BACKLOG（綁 prod 硬化刀） | 帳＝BL-00049（滯後卷、觸發＝RUNBOOK §16 prod 硬化拍板）＋ADR 記拍板 | brainstorm Q4／Q7 |
| R3-19 | root `Cargo.toml` 不進 argon2 的舊拍板翻案＋`server/Cargo.toml` 清單改寫 | 同；另 `Cargo.toml` 檔頭「auth／web／obs 依賴群各隨其功能刀進場」句即本刀兌現處、註解改寫為現在式 | spec FR-032 |
| R3-20 | contract stub 連線改 `connect_lazy`（rev5 ADR 0034，003 期間修訂） | rev6 002 已採該形（`tests/common/mod.rs` 自證案在）；本刀零改連線形 | R7-1 |

**防回歸清單 B（承 `rev5:003` research R3 十七筆 rev4→rev5 翻案、全視為已翻案、不得帶回；烤入 implementer prompt）**：`rev5:R3-1` 模組名 `cache` 非 `redis`、`captcha` 三規則消歧／`rev5:R3-2` grace 30 秒非 10／`rev5:R3-3` IP 維節流・HLL・`suppressed_breadcrumb` 不做／`rev5:R3-4` Biz 鍵 `biz.auth.*` 非 `auth.login.*`／`rev5:R3-5` `CaptchaClaims` 四欄無 `ctx`／`rev5:R3-6` `handler/auth/` 五檔非單檔／`rev5:R3-7` `revoked` 缺 denylist 靜默 8888 不落假 reuse／`rev5:R3-8` denylist TTL 兩 reason 皆 refresh_secs／`rev5:R3-9` loginCaptcha 住 `handler/captcha.rs`／`rev5:R3-10` 三分碼（缺席＝8888 非 3333）／`rev5:R3-11` request_context 原樣轉錄零信任判定／`rev5:R3-12` 不放寬 `formRules`／`rev5:R3-13` 不插 8888 前 toast／`rev5:R3-14` `VITE_HTTP_PROXY=N`、不開 DEVPROXY／`rev5:R3-15` 只補 `backend` 型節、不擴 `LangType`／`rev5:R3-16` 不做首登換密・email-verify・mailer／`rev5:R3-17` precheck 不讀 redis unlock marker。

## R4 三分碼射程與 ADR-00014 後果段兌現（clarify 候選①、spec FR-024）

- **Decision**: 措辭落三處——主 Amendment ADR（ADR-00026）後果段一句「本刀定 `3333` 射程＝僅 access exp 過期（enforce 驗章之 `ExpiredSignature`）；標頭缺席・非 Bearer・簽章不符・已撤銷・refresh 鏈失效→`8888`；被踢→`7777`；ADR-00014 只鎖未認證≠越權、不翻」＋`error.rs` 三新變體碼註＋活書 §8 API 慣例；不立獨立 ADR。
- **Rationale**: 三分碼是島 A／C 條文的直接後果（島 C 之 kicked→7777、reuse→8888 已入條文），主 Amendment ADR 即其家；ADR-00014 後果段明寫「003 接真 session 時重定」＝預留、非翻案。
- **Alternatives considered**: 獨立 ADR「三分碼射程」（多一筆、內容與島條文重複）；只記碼註（拍板級措辭無 ADR 家）。
- ★refresh 端點自身驗章失敗恆 `8888`、絕不 `3333`（前端 `expiredTokenCodes` 含 3333 ⇒ refresh 回 3333 即死迴圈；`.env` 現值 `VITE_SERVICE_EXPIRED_TOKEN_CODES=9999,9998,3333`、`VITE_SERVICE_MODAL_LOGOUT_CODES=7777,7778`、`VITE_SERVICE_LOGOUT_CODES=8888,8889` 實查）。

## R5 降級矩陣終形（五座行為島；隨 ADR-00026 入憲；spec FR-012／FR-015／FR-016）

| 降級源 | 方向 | 行為 | 觀測（label） |
|---|---|---|---|
| denylist 讀不到（連線 Err） | **fail-closed** | 退 PG `has_active_in_chain`；無 active→8888；PG 亦故障→視為無 active、絕不盲放 | `denylist_hit_total{source=pg}` |
| denylist 鍵缺席（nil） | 權威語意 | nil＝「未撤」→放行；`revoked` 列由 status 定案（靜默 8888、不落事件） | — |
| last_activity 不可讀 | **fail-open** | 不 idle-reject、照常 rotate（token exp 為界） | — |
| grace 不可用 | **fail-secure** | 並發 refresh 觸發 reuse→撤家族（多分頁全域登出、重登復原＝已知態） | — |
| captcha 標記 SET NX 瞬斷（redis 健康） | **fail-closed 不罰** | 拒該次登入、零計數桶 | `throttle_degraded_total{source=redis_captcha}` |
| redis 整體不可用 | **fail-open** | 軟區 captcha 要求整層停用、續驗密碼（密碼錯仍計數） | `throttle_degraded_total{source=redis_lock}` |
| 節流 L2（PG）查詢失敗 | **fail-open＋補償** | `count:=0` 放行＋`captcha_forced = !redis_down`；★`captcha_forced` 不入軟區計數 | `throttle_degraded_total{source=db_count}` |
| L1 lock key SET 失敗（redis 健康） | best-effort | 鎖定判定已成立、負快取未武裝（下次仍由 L2 判） | `throttle_degraded_total{source=redis_lock_set}` |
| 節流設定鍵讀不到 | 退活書常數 | 每次載入至多一筆告警 | `throttle_degraded_total{source=settings_default}` |
| **節流設定鍵矛盾組合**（captcha_after > max_fails；clarify Q3） | 退活書常數 | 視同不可用；每次載入至多一筆告警；002 寫端零改動 | `throttle_degraded_total{source=settings_invalid}` |
| 失敗列寫入失敗 | best-effort | 不改登入回應；★計數斷供必須可見 | `throttle_degraded_total{source=db_write}` |
| `session_idle_timeout` 缺失／壞值（login 第⑥步、refresh 簽新對） | **fail-loud** | `5000`、不猜值（與節流方向相反、刻意） | — |
| `single_session_default` 缺鍵 | off 語意 | 不啟用單一會話（與 D／E 皆不同、刻意） | — |
| redis 不開 AOF | 已知態 | RDB 回捲窗內 denylist 鍵可丟；暴險受「status 即權威」封頂 | — |

`throttle_degraded_total` 之 `source` label 值集恰七：`settings_default`／`settings_invalid`／`redis_lock`／`redis_lock_set`／`redis_captcha`／`db_count`／`db_write`（rev5 六源＋本刀 `settings_invalid`；不含 rev4 `redis_unlock_marker`）。★spec FR-035 所列 `captcha_mark`／`redis_down` 為舉例措辭、非實有 label（已同批校正 FR-035 字面）；obs.rs pre-register 與 tasks 一律以本表七值為準。

## R6 觀測面與 i18n 算術自證（spec FR-025／FR-026／FR-035）

- **觀測面**：`obs.rs` 之 `pre_register_metrics` 增三序列——`throttle_degraded_total{source}`（七值逐字）／`denylist_hit_total{source}`（`redis`｜`pg`）／`throttle_soft_zone_total`（無 label）；`captcha_forced` 不計入軟區計數；降級 warn 一律結構化（`target: "security.throttle"`／`"security.session"`＋`degraded` 欄）；守門走 render 文本比對（沿 002 `pre_register_renders_*` 形）。
- **i18n 算術**：三檔 backend 子樹各 **13 鍵**＝002 既有 7（`common.success`／`system.internal`／`system.notFound`／`system.forbidden`／`auth.session.reLogin`／`biz.systemSettings.invalidValue`／`biz.systemSettings.notFound`）＋本刀 6（`auth.login.failed`／`auth.token.expired`／`auth.session.kicked`／`biz.auth.notSupported`／`biz.auth.captchaRequired`／`biz.auth.locked`）；`MSG_KEYS` 同 13、序固定；`msg_keys_roster_*` 測試改十三。插入行 MUST 為獨佔一行的 `  backend: {`（跨端閘 R9 以 brace 配對抽子樹、非 fullmatch 謂詞，但獨佔一行仍是 rebase 衝突面最小形）。

## R7 測試設施與機器閘衝擊（tasks 硬前置；逐項 rev6 實碼核實）

1. **contract 測 stub 連線**：rev6 `tests/common/mod.rs` 已採 `connect_lazy` 假連線（`stub_state`＋自證案）⇒ 9 條 Public 真進 handler、查詢時得 `DbErr` ⇒ contract case 只能斷言三欄信封＋`code` ∈ 13 碼矩陣、不得斷言 `0000` 或空集 data（業務內容歸 integration）；POST body rejection（JSON 壞形／缺欄）沿 002 `from_request` 形但**出口碼依端點**（承 rev5、非 002 之 2222）：login→`1000 auth.login.failed`（與形制閘同取徑）／refreshToken→`8888 auth.session.reLogin`（★`3333` 會觸前端自動 refresh 死迴圈、`1000` 是登入語意）／logout→`0000` no-op（以 `Result<Json, JsonRejection>` 收、就地折成冪等、不上浮＝不做 oracle）／四支 stub 不解析 body ⇒ 無 rejection 面；`/auth/loginCaptcha` Query rejection 成三欄信封（`1000` 同形閘）；`stub_state` 改五欄（`cache: None`、`captcha_secret` 字面 `stub-captcha`＝非機密、`JwtConfig` 測試字面）。
2. **`dev_identity` 汰換**：rev6 無 lint must-list（R3-10）；實查引用面＝`auth/enforce.rs`（`crate::auth::dev_identity::authenticate` 真呼叫點＋cfg 分支）、`auth/mod.rs`（宣告＋doc）、`router.rs`（3 處測試 token）、`handler/system_settings.rs`（dev token 字面 grep 現算、現 103 行、integration 測試面）、`tests/contract.rs`（14 處分三類：通則未認證案／合成 Policy 與 `observed_msgs` 三處／`observed_msgs_real_db` 五處＝0000・5003・biz 兩鍵唯一發出點）；contract 通則 case 改三形皆 8888；★integration test crate 取不到 `#[cfg(test)] pub(crate)` 之 `test_kit` ⇒ tests/ 側簽發走公開 API `server::auth::jwt::sign`、helper 落 `tests/common/mod.rs`（`real_seed_app` 加可帶 `Some(cache)` 形）；src/ 側 integration 以 test_kit 簽發（R7-10）。
3. **`error.rs` 八處逐字改動**（rev6 實碼核實、比 rev5「六處」多兩處名冊測試）：①`issuable_six_and_no_variant_seven` 改名＋計數 6→9 ②其 `no_variant` 期望陣列 7→4 保留碼 ③`matrix()` 補三列（1000／3333／7777 之 key／http／sample）④`issuable_witness` 窮舉 match 補三臂（不補＝編譯紅）⑤`witness_aligns_matrix_and_excludes_no_variant_codes` 內第二份 `no_variant` 陣列同步 ⑥`msg_keys_roster_is_exactly_seven_and_unique` 改十三 ⑦`fixed_variant_keys_are_in_roster` 補三固定鍵 ⑧`biz_two_keys_are_in_roster` 改五 Biz 鍵；`each_issuable_code_builds_error_envelope` 自動涵蓋；`http()` 現為 `_ => StatusCode::OK` 萬用臂 ⇒ 三新碼落 200 零改動、只補斷言。
4. **schema-gate gate2 × runtime 寫入**（本刀首撞）：凍結 seed 對 `sys_token`／`session_event`／`sys_login_attempt` 各有 0 列段＋`setval(seq, 1, false)`；真 DB 測試守衛除 DELETE 列外 MUST 顯式 `setval(<seq>, 1, false)` 重設三支 sequence、`UPDATE sys_user SET session_id = NULL`；single-session 驗收前置翻 `on` 後 MUST 翻回 `off`（連帶 `updated_at`／`updated_by`＝002 `SeedRestoreGuard` 四欄快照形）；走查期以 R10 工具 diff rc 0 為還原判準。
5. **redis 鍵空間隔離**：dev 與測試共用 DB 0；測試鍵一律 uniq 前綴（時戳＋pid）；`--test-threads=1` 只解 PG 列爭用。
6. **`parse_router_routes` 窄形**：16 條每欄一行、`handler: || get|post(...)` 單動詞（鏈式多動詞靜默通過＝禁）、`method: HttpMethod::X`；generate 後 `docs/generated/reference/routes.md` 恰 16 列（DoD 機器核）。★`tools/docsync/tests/test_references.py` 之 `TestRoutes` 除合成語料外另有 `test_real_repo_pinned_rows`（002 T029 落、真 repo 四列逐列全等）——ROUTES 每次增列 MUST 同批增列該釘值列（U5～U9 五次：9／10／11／12／16）並把該檔納入允許檔案清單（RL-0022）；`router.rs` 自身 `routes_block_literal_form_and_pinned_rows`（`ROUTES_COUNT`＝4 與「002 刀恰四條」訊息）同批逐次改對。
7. **稽核列寫入點恰三處**（spec FR-004）；不落列四類；best-effort＋`db_write` 告警。
8. **wire-schema**：`TYPINGS_GLOB` 已含 `src/typings/api/*.d.ts` ⇒ 新檔 `rev6-auth.d.ts` 一入即進快照（容器內 `extract` 重抽、byte 比對）；`tests/wire_schema.rs` 裁判面補 `Api.Auth.{LoginToken,UserInfo,LoginCaptcha}`＋`Api.Route.{MenuRoute,UserRoute}` case（rev5 於 003 後一筆才補＝本刀直接納入）；pre-commit wire-schema 段於 base-web／rust-api pin bump 時首次真正生效。
9. **前端零測試框架**：前端單元 TDD 迴圈退化為 `pnpm typecheck`＋兩段 review＋CDP 走查（單元 `CONTEXT` 明文、不動 RULES）。
10. **test_kit 擴充**（rev6 落點＝`server/src/model/facade/test_kit.rs`，承 rev5 `model/mod.rs` 之 `test_db`）：`real_state()`（真 DB＋真 redis＋seed enforcer＋測試 `JwtConfig`＋`captcha_secret`；U1 先 `cache: None`、U2 接真 redis）、`uniq_prefix()`、`SequenceResetGuard`（三支 setval）、`SessionRowsGuard`（DELETE 三表＋清 `sys_user.session_id`）、★`SeedRestoreGuard` 三件自 `handler/system_settings.rs` 私有 `mod tests` 搬入並 `pub(crate)` 曝出（RL-0070）、簽發 helper 固定簽名（`sign_access_for`／`sign_pair_for`）；handler 內 `#[cfg(test)]` 真 DB 案一律掛守衛（RL-0005／RL-0031）。★`test_kit` 為 `#[cfg(test)] pub(crate)`、integration test crate（`tests/`）取不到 ⇒ contract 面另以公開 API 簽發（`tests/common/mod.rs`）。
11. **`schema-gate check` 於走查後才跑**（gate2 逐列）；contract／integration 測試自帶守衛故 `cargo test` 後 gate2 仍綠。
12. **`AppState` 建構點**：`grep -rn 'AppState {'` 現算（現況含測試 13 處：`main.rs`／`state.rs` 錨測／`router.rs` 2／`handler/system_settings.rs` 2／`tests/common/mod.rs`）——五欄化 MUST 同批全改、U1 允許檔案清單含上述五檔（否則 U1 收尾編譯紅）；數字不寫死。
13. **release profile 首次可跑**（spec FR-033／SC-011）＝`dev_identity` 整檔汰換的唯一機器證據：DoD 於容器內 `cargo build --release -p server` 綠＋以 release 二進位起服務打 `/health` 回 `ok`（quickstart §7）；歸 U11 收攏驗收。

## R8 憲法 Amendment 形制（spec FR-029～FR-031；ADR-00026 draft＝本 plan 產物、status proposed）

- **Decision**: ADR-00026 於本 plan 落 feature branch（status `proposed`、body 可改）；tasks 首個主線任務＝user 親決→轉 accepted→憲法 §III.2 落四列（哨兵句同批移除）＋§I.7 落島 A～E＋Amendment log 1.3.0＋`Version` 行→`python3 tools/docsync generate`→獨立 commit `docs(constitution): amend …`。
- **§III.2 表列機器形**（`tools/fork-delta-lint.py` `load_roster` 六條硬規則、逐條對照）：①每列以 `|` 起首、首欄 `**★NAME**`（載入器剝 `**`／`★`）②首欄不得留空（續列守）③用途欄 MUST 以 `(a)`／`(i)` 括號識別符起首 ④範圍欄 MUST 含 ≥1 反引號路徑 token（含 `/` 或根層 `.env*`）、brace 展開單組 `{a,b,c}`、（…）注記內的反引號 token 不入集 ⑤不得殘留 brace／全形括號於 token 內 ⑥首列落入時哨兵句「（空表——尚無 ★ 軌道；首列隨首刀 Amendment 落入。）」MUST 同批移除（並存＝die）；§III.1 三列一字不動（`S1_RANGE_LITERAL` 對賬）；`MODAL-WIRING`／`BASE-WEB-DEVPROXY-WIRING` 不入冊。
- **修改型標記形**：`[rev6-inline <軌道名>(<用途>) 003-auth-session] 原行: <基線該行>`（`TRACK` 正則捕裸名＋括號識別符；`.env` 走 `[rev6-inline BASE-WEB-ADAPT 003-auth-session] 原行: …` 裸形）；新增型 `[rev6-inline <軌道名>+ 003-auth-session]`（不入名冊）。
- **名冊斷言自證（四腿、spec FR-030）**：fork-delta-lint 既有 self-test 已含合成憲法之三元組正反例（`rev5:B-068` 升維）；Amendment 落地後真 repo 演練四腿（每腿還原後 `git -C base-web status --porcelain` 零差異、RL-0005）：①名冊內過＝真 repo 首跑 rc 0 ②名冊外攔＝把某修改型標記軌道名改成名冊外之名（如 `BASE-WEB-MANAGE-PAGE-WIRING`）→ rc 1 ③用途外攔＝`(a)`→`(z)` → rc 1 ④檔外攔＝把某授權用途標記搬到同軌道範圍欄外的既有檔（如 `BASE-WEB-AUTH-WIRING(a)` 標在 `src/hooks/business/captcha.ts`）→ rc 1。
- **§I.7 條文**：島 A～E 以 rev5 v1.3.0 逐字為底（provenance `rev5:ADR 0028`）、rev6 增三句（R3-7）；「已入憲行為島」段替換「（尚無…）」；承襲指針表 A～E 列註「已入憲 v1.3.0」。
- **Alternatives considered**: specify 後即 draft（範圍欄未定）；tasks 首單元四步全做（親決時看到的不是完整 draft）——皆 brainstorm Q5 棄案。

## R9 msg key 跨端閘設計（clarify Q2；spec FR-027；工具＝`tools/msg-key-gate.py`、碼面閘）

- **Decision**: 零 docker、純標準庫；左源＝`rust-api/server/src/error.rs` **兩段解析**（實碼形＝`pub mod msg_key { pub const NAME: &str = "字面"; }` 常數表＋`pub const MSG_KEYS: [&str; N] = [ msg_key::NAME, … ];` 常數引用陣列、零字面）：①抽常數表建 名稱→字面 映射 ②以映射解析陣列元素（`msg_key::NAME` 形；亦容直寫字面）；元素數≠N、任一元素解不出＝rc 2；右源＝`base-web/src/locales/langs/{en-us,zh-cn,zh-tw}.ts` 各自的 `backend: {` 區塊（自獨佔一行錨起、brace 配對取整塊、剝註解與字串、巢狀鍵以 `.` 串接攤平）；斷言＝三檔各自 `set(backend) == set(MSG_KEYS)`（逐檔、雙向、指名缺鍵／多鍵）＋Biz 構造點守衛（`server/src/**/*.rs` 生產區間之 `AppError::Biz(` 後 MUST 緊接 `Cow::Borrowed(` 且引數為 ①字串字面 或 ②`msg_key::NAME` 常數（經映射解回字面）、解出之鍵 ∈ `MSG_KEYS`；動態構造（變數／`format!`／函式回傳）＝rc 1；`#[cfg(test)]` 區間以大括號配對排除；002 既有兩處常數形＝合法、零改動）；rc 0 綠／1 鍵集不等或動態 Biz 構造／2 結構異常（檔缺席、常數表或陣列解析失敗、backend 節缺席或 brace 不配對）／64 用法錯；`test` 子命令＝離線 self-test（合成樣本七案：三檔全等綠／缺鍵／多鍵／某檔缺 backend 節／常數間接形解析成功／常數表缺該名 rc 2／動態 Biz 構造紅）。
- **Rationale**: backend 子樹本刀自零建＝封閉集、雙向可行；rev5 三向（⊆＋白名單存在＋白名單腐化）的複雜度來自九鍵白名單，rev6 無白名單則三向退化為雙向全等；標準庫 regex＋brace 配對足夠、不引 TS 解析器。
- **接線五處**：pre-commit 條件段（觸發＝staged 含 `rust-api`／`base-web` pin bump、或工具本體即跑）＋★pre-commit `for t in …` 自測名冊加列（`test_hook_wiring` 斷言該名冊 ⊇ 碼面閘表 ∪ `NON_GATE_TOOLS`、缺即 docsync test 紅）、`test_hook_wiring.py` SEGMENTS、`tools/bootstrap.sh` 名冊（R11②推導）、README 樹（GT-09）、RUNBOOK §12 碼面閘表（註記列轉工具檔列、GT-12 對賬）。
- **Alternatives considered**: 單向 ⊆（少守一半、rev5 為此長出白名單）；把閘寫進 docsync（docsync 行數預算 3542/4000、且碼面閘依 ADR-00016 一律獨立 `tools/` 工具檔）。

## R10 走查基準對賬工具遷入（spec FR-036；RUNBOOK §9c 實文；`NON_GATE_TOOLS`）

- **Decision**: `rev5:tools/walkthrough-baseline.py`（782 行）依「隨遷工具」整檔搬運至 `tools/walkthrough-baseline.py`；四型失效引用 rev6 化：①compose 專案＝rev6 根（`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres|redis`）②「rev5 dev stack」→「rev6 dev stack」、「絕不指向 rev4 對照 stack」→「絕不指向 rev5 對照 stack（2xxxx）」③裸前代編號 `B-147`／`L-071`／`L-055`／`ADR 0010` → `rev5:` 前綴形，★以 `tools/docsync/book.py` 之 `BARE_REV5` 對遷入後全檔復掃、零命中才算 rev6 化完成（不靠人列清單）④前綴例句「session:／throttle:／cpwd:」→ rev6 現行前綴（本刀＝`session:`／`throttle:`；`cpwd:` 為 `rev5:007` 增量、刪）；`--user`／`--db` 預設沿 `tools/schema-gate.py` 常數（`soybean`／`soybean_admin_rust`）。三面現算、唯讀、rc 0／1／2／64（clarify 候選④）；`test` 離線 self-test（subprocess 全樁）。
- **登記**：`tools/docsync/gates.py` `NON_GATE_TOOLS += ("tools/walkthrough-baseline.py",)`；`tests/test_gates.py` 補一正一反（常數含該檔＝綠；抽掉＝GT-12 紅指名「未列於碼面閘表」）；★pre-commit `for t in …` 自測名冊加列（進 `NON_GATE_TOOLS` 即落入 `test_hook_wiring` 聯集斷言）；bootstrap 名冊（R11②推導）；README 樹；RUNBOOK §12 工具鏈速查加列（非碼面閘表）＋§12 碼面閘表前言「`NON_GATE_TOOLS` 現＝`tools/wf-watchdog.py`」句改兩支＋檔頭「創世期章節現況」句之 §9c 自「指針章」移入「已補實文章」（皆人寫鏡像、`errata NON_GATE_TOOLS`／`errata 指針章` 復掃）；RUNBOOK §9c 自指針章改實文＝契約（見 contracts/code-gates.md §3）。
- **Rationale**: 工程判斷 3——它是走查前後對賬工具、不守版控品質、不掛 pre-commit（同 `tools/wf-watchdog.py` 定位）；不登記 `NON_GATE_TOOLS` 則 GT-12 對賬立紅。
- **Alternatives considered**: 列入碼面閘表（它不是閘、會誤導 pre-commit 名冊）；不遷、走查靠三閘（`rev5:L-071` 招牌徵狀＝三閘綠而全量紅、已證偽）。

## R11 BL-00037 ①② 設計（spec FR-037）

- **①pre-push 面接線守衛**：`tools/docsync/tests/test_hook_wiring.py` 自單常數 `HOOK` 擴為四檔名冊（`.githooks/pre-commit`／`.githooks/pre-push`／`.githooks-submodule/pre-push`／`.githooks/lib/scan-range.sh`）；pre-push 兩支各斷言三字面（source `lib/scan-range.sh` 之相對路徑形、`SCAN_CONFIG="$HOOK_DIR/…/.gitleaks.toml"`、`scan_push_ranges || exit 1`）；lib 斷言 `betterleaks git --config "$SCAN_CONFIG" --redact --verbose --exit-code 2 --log-opts=` 與四種範圍推導字面；一正多反（刪任一字面→紅指名）。pre-commit selftest-docsync 觸發樣式自 `'^tools/docsync/\|^\.githooks/pre-commit$'` 放寬為 `'^tools/docsync/\|^\.githooks/\|^\.githooks-submodule/'`（SEGMENTS 字面同批改）。
- **②bootstrap 名冊自 tracked 檔集推導**：`run_tool_test` 現行十行無條件硬編＋一行 Day-1 條件分支（`deploy/decrypt-secrets.py`），改為 `for t in $(git -C "$ROOT" ls-files ':(glob)tools/*.py' ':(glob)deploy/*.py' | grep -v -e '^deploy/decrypt-secrets\.py$' -e '^deploy/secrets_common\.py$'); do run_tool_test "$t"; done`——★git pathspec 的 `*` 會跨 `/`（裸 `'tools/*.py'` 會命中 `tools/docsync/*.py` 與 `tools/orchestration/*.py`、後者 `assemble.py test` 回 2 即 die），`:(glob)` magic 令 `*` 不跨層；`deploy/secrets_common.py` 無 `test` 子命令、`deploy/decrypt-secrets.py` 維持 Day-1 條件分支，兩者顯式排除並註明理由；自證＝`test_hook_wiring.py` 加 bootstrap 面案：讀真 `tools/bootstrap.sh`、斷言推導行字面（含 `:(glob)` 與兩排除）存在＋docsync 三段（test／check／lint）＋閘數斷言＋`vendored-check` 呼叫字面存在；刪任一即紅；另一反例＝推導行被改寬（去 `:(glob)`）→ 以合成 tracked 清單模擬名冊多出 `tools/orchestration/assemble.py` → 紅。
- **Rationale**: 條目意圖即「補腿與該面的下一次改動同批」；本刀正在改 pre-commit（跨端閘段）與 bootstrap 名冊（兩支新工具）。
- **Alternatives considered**: 只收②（①觸發同樣已到）；兩項不收（另開輕量軌、`gov_ratio` +1）——brainstorm Q6 棄案。

## R12 BL-00026／BL-00041 刀內收（spec FR-034）

- **BL-00026**：`main.rs` 之 `Database::connect(ConnectOptions::new(&database_url))` 改兩敘述形（★`sqlx_logging_level` 回 `&mut Self`、不可鏈進 `connect` 引數）：`let mut connect_options = ConnectOptions::new(&database_url); connect_options.sqlx_logging_level(log::LevelFilter::Debug); Database::connect(connect_options)`（sea-orm 1.1.20 API、承 rev5 as-built 形）；root `Cargo.toml` workspace.dependencies 加 `log = "0.4.34"`、`server/Cargo.toml` 加 `log = { workspace = true }`（只為 `LevelFilter` 型別、本 crate 觀測輸出仍走 tracing）；同批刪 `main.rs` 該行上方「屬 BACKLOG 候選、002 刀不引 log crate」自陳註解＋`errata`「不引 log crate」復掃；`config`／`obs` 不動。
- **BL-00041**：兩處皆為「rev5 002」裸形（實查；BACKLOG 條文之「rev5 001」為誤記、收刀改條文時一併訂正）：`server/src/model/facade/test_kit.rs` 檔頭「rev5 002 刀時」→「`rev5:002` 刀時」、`server/src/handler/system_settings.rs` 「rev5 002 收刀坑」→「`rev5:002` 收刀坑」（提及形反引號）；`tools/docsync/book.py` 之 `SUB_SCAN` 粗篩 ERE 加 `rev[45] [0-9]{3}` 形、精判以 `BARE_PREV_KNIFE_NUM` 對子庫命中列重判（提及形豁免同外層）、該處「尚未接」註解改寫；`tests/test_book_ids.py`（GT-05 子庫腿既有測試面）補一正一反（合成命中列）。★兩處改動落子庫＋外層同批（一次 pin bump）。

## R13 casbin 零新政策列複核（brainstorm Q2 待 plan 複核；spec FR-002）

- **結論：成立、零新列。** 證據：①12 條新 route 無一 `Protection::Policy`（9 Public＋3 Authed）⇒ 無 route 政策查詢（★spec FR-002 之「16 條 route 無一為 Policy」已同批校正為「12 條新 route」——既有兩條 systemManage 為 002 既定 Policy、不動）；②seed 163 列已含 `menu` 維度（act＝`menu`、obj＝route_name；三角色皆有）與 `button` 維度（act＝`button`、obj＝按鈕碼）⇒ `getUserRoutes` 以 `get_filtered_policy(0, [role, "", "menu"])` 取 obj 集、`getUserInfo.buttons` 同法取 `button`（`MgmtApi` trait、非 `enforce*`＝不觸單一判定進入點守恆）；③seed 已含後續刀端點列（`/systemManage/getUserList` 等）本刀不消費；④model 為 3-tuple RBAC（`sub, obj, act`）、`g` 無政策——角色代碼即 sub，與 002 同。

## R14 設定改值總則與 BL-00031（clarify Q3／Q4；spec FR-005／FR-009／FR-015／FR-031）

- 總則入島條文（R8）；實作形＝rev5 既有：`single_session` 於 login 第⑨步讀現值；`ttl_from_settings` 於 login 第⑥步與 refresh `active` 腿各讀一次（新對 TTL＋idle 門檻同源）；節流三鍵於 `throttle::precheck` 每次載入。矛盾組合判定住 `throttle` 設定載入函式：`captcha_after > max_fails` ⇒ 三鍵整組退常數＋`source=settings_invalid` 告警一筆（與 `settings_default` 同一「每次載入至多一筆」紀律）。收刀改 BL-00031 條文（刪 003 段）。

## R15 執行單元切分建議（→tasks 展開；CLAUDE.md §2 六件套、每單元 pin bump、rust 容器內 serial、每 run 不重複 agent ≤20）

| 單元 | 內容 | 硬序 |
|---|---|---|
| U0（主線） | ADR-00026 親決→accepted＋憲法 §III.2 四列（移哨兵句）＋§I.7 島 A～E＋1.3.0＋generate；同批＝README 第 14 行憲法版本鏡像（1.2.0→1.3.0＝ADR-00026）＋`tools/fork-delta-lint.py` self_test 註解「rev6 §III.2 現為空表」改現在式＋`errata 1.2.0`／`errata 空表` 復掃；獨立 commit | ★accepted 前不得動 base-web 既有檔 |
| U1 | 依賴八支進場（R1、features、`cargo update -p log`）＋`config.rs` 六 getter＋`state.rs` 五欄＋錨測＋`AppState` 建構點全改（R7-12）＋`cache/mod.rs` 型別與 `connect`＋`main.rs` boot（cache 建連 panic、JwtConfig、captcha_secret、BL-00026）＋兩筆翻案 ADR（AppState／argon2）＋test_kit 擴充（R7-10、含 `SeedRestoreGuard` 搬入） | — |
| U2 | `error.rs` 三變體＋`MSG_KEYS` 13（常數形；contract 雙向測重掛 `#[ignore]` 至 U9）＋八處測試＋檔頭四處自陳改寫＋`auth/jwt.rs`＋`cache/mod.rs` 補實＋`model/password.rs`＋`request_context.rs`＋`model/mod.rs`／`auth/mod.rs` 宣告＋test_kit 真 redis 與簽發 helper | U1 |
| U3 | facade 六支（sys_token／session_event／sys_login_attempt／sys_menu／sys_user／sys_role）＋`facade/mod.rs` 八支 ASCII 序＋entity_access_lint 確認 | U1 |
| U4 | `auth/enforce.rs` 真驗章＋denylist 四級降級＋`dev_identity` 汰換（射程＝R7-2：含 `router.rs`／`handler/system_settings.rs`／`tests/contract.rs`／`tests/common/mod.rs` 測試面真 token 化）＋`obs.rs` `denylist_hit_total`＋release build 首次可跑 | U2、U3 |
| U5（US1） | contract 5 case＋integration 骨架＋`handler/auth/{mod,login,user_info}.rs`（login 十一步之③～⑧⑩⑪）＋`handler/{mod,route}.rs`＋`router.rs` +5（`ROUTES_COUNT` 9、兩處釘值列）＋`wire_schema.rs` 裁判＋`.env*` 四行＋route store (a)＋走查 §1 | U4、U0 |
| U6（US2） | contract 1 case＋`handler/auth/refresh.rs`（rotation／grace／reuse）＋`router.rs` +1（10）＋走查 §2 | U5 |
| U7（US3） | contract 1 case＋`login.rs` ⑨＋`refresh.rs` revoked 三分支與 idle＋`logout.rs`＋`router.rs` +1（11）＋`rev6-auth.ts`（fetchLogout）＋user-avatar (i)＋走查 §3 | U6 |
| U8（US4） | contract 1 case＋`throttle/mod.rs`（三區＋矛盾組合）＋`captcha/mod.rs`＋`handler/captcha.rs`＋`login.rs` ①②＋`obs.rs` 兩序列＋`router.rs` +1（12）＋`rev6-auth.d.ts`／`rev6-auth.ts`（fetchLoginCaptcha／fetchLoginWithCaptcha）＋wire-schema 重抽＋auth store／pwd-login (i)＋軟區換題＋走查 §4 | U7 |
| U9（US5） | contract 4 case（區別手法）＋`alt_stub.rs`＋`router.rs` +4（16）＋四鍵承載案落齊後移除 `#[ignore]`＋四 stub wrapper＋三表單 (b)＋captcha hook (c)＋`app.d.ts` (iii)＋兩語 backend 樹＋`zh-tw.ts` (ii)＋request 層 (i)＋`tools/msg-key-gate.py`＋pre-commit 段與 `for` 名冊＋test_hook_wiring＋README＋RUNBOOK §12 列＋跨端閘 ADR＋走查 §5 | U8、U0 |
| U10（US6） | `tools/walkthrough-baseline.py` 遷入（`BARE_REV5` 復掃、CLAUDE.md §7 與 RUNBOOK 預告句改現在式）＋`NON_GATE_TOOLS`＋GT-12 自測＋pre-commit `for` 名冊＋RUNBOOK §9c 實文／§12 列與前言現值句／檔頭章節現況句＋BL-00037①②＋BL-00041（`system_settings.rs` 註解＋`SUB_SCAN` 子庫腿＋`test_book_ids` 自測）＋快速登入鈕 ADR＋治理自證四組 | U9、U0 |
| U11（收攏） | release profile 復核（R7-13）＋CDP 對照走查（snapshot→三帳號登入／續期／登出／被踢／軟區→清理→diff rc 0）＋schema-gate check＋全量閘＋活書 §5／§6／§8／§10.2（島 A～E 各一品質情境、刪「目前零情境」句）／§12＋BACKLOG／LESSONS／NOTES 預告＋perf 事件＋final holistic review 輸入 | 全部 |

★`router.rs`／`contract.rs`／`test_references.py` 為 U5～U9 序列共用檔（逐 US 加列並 bump 同一 `ROUTES_COUNT` 與釘值列、不可並發；承 rev5 003 analyze 修正與 002 T029／T033 形、不設尾端獨佔單元）。

預估 T 號 50～60；每單元 pin bump；U8～U9 前端腿 review 以 typecheck＋CDP 為驗收（工程判斷 5）；每 run 組裝後、發射前 `IMPL_OPTS`→`opus[1m]`（brainstorm Q10）。

## R16 棄案反例回跑（RL-0013：棄案論證寫完回頭對所選方案跑同一反例）

| 拍板 | 棄案的反例 | 對所選方案回跑 | 結論 |
|---|---|---|---|
| Q2 逐檔雙向全等 | 「前端 backend 子樹要放一個後端不發的鍵」（單向 ⊆ 才容） | 雙向下該需求須先改閘或把鍵挪出 backend 子樹 | 可接受：backend 子樹依設計為封閉集、前端內部鍵不該住 backend 節；閘紅即設計訊號 |
| Q3 矛盾組合退常數 | 「管理員刻意設 captcha_after=max_fails+1 想關掉軟區」（clamp 才保留意圖） | 退常數＝意圖不生效、但告警可見；「關軟區」的正確表達＝`captcha_after = max_fails`（軟區寬度零、合法） | 可接受：語意有合法寫法、不需靠矛盾組合 |
| Q4 總則不追溯 | 「超管想立即踢掉所有既有多會話」（追溯型才做得到） | 總則下需管理端點（踢人／撤銷）＝後刀（稽核／使用者域） | 可接受：spec Out of Scope 已列管理員解鎖／踢人隨後刀 |
| D1～D5 取最新 | 「新版 API 與 rev5 藍本不同、實作摩擦」（沿 lock 才零摩擦） | R1 守則逐 crate 列出主路徑 API；四支不觸破壞面、argon2 0.6 的 `OsRng` 破壞面實查觸及 | 可接受但非零成本：處置＝新增 `getrandom`（D6、lock 同值）；摩擦＝features 名、`_` 臂、取亂數改道一處 |
| R9 獨立工具非 docsync | 「多一支工具＝多一處名冊」（塞 docsync 才零名冊） | GT-12 碼面閘表腿自動對賬新 tools/ 檔、test_hook_wiring 守 pre-commit 段 | 可接受：名冊由機器對賬、非人記 |
| R10 `NON_GATE_TOOLS` | 「登記常數是第二份名冊」（列入碼面閘表才單一） | 常數有 GT-12 反例守（清空即紅） | 可接受：兩處皆機器守、語意正確（它不是閘） |
