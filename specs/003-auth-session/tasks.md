---

description: "Task list for 003-auth-session"
---

# Tasks: 003 auth 域整批——真登入、會話生命週期、節流＋驗證碼、dynamic 選單、i18n 轉譯

**Input**: Design documents from `/specs/003-auth-session/`

**Prerequisites**: plan.md、spec.md（US1～US6、clarify Q1～Q4）、research.md（R1 依賴八支／R2 對應碼／R3 二十筆差異＋十七筆承襲防回歸／R5 降級矩陣／R7 測試衝擊十三項／R8 Amendment 機器形／R9～R12 治理工具設計／R15 單元切分）、data-model.md、contracts 四檔（wire-auth／wire-route／msg-keys／code-gates）、quickstart.md；
憲法 1.2.0（ADR-00026 draft 已落、proposed）；連帶 ADR 四筆待立（序號自 ADR-00027 起於落檔時取）。

**Tests**: 本 repo TDD＝CLAUDE.md §2 紀律、**非可選**——每實作 task 內先紅後綠。測試層對照（research R7）：*contract case*＝`rust-api/server/tests/contract.rs` registry（oneshot 免 DB、`connect_lazy` 假連線 ⇒ Public route 進 handler 得 `DbErr`，case 只斷言三欄信封＋`code` ∈ 13 碼、不斷言 `0000`）；*integration*＝各 handler／facade 模組內 `#[cfg(test)]` 真 DB＋真 redis 案（`test_kit` 守衛：`SessionRowsGuard`＋`SequenceResetGuard`＋自 002 handler 私有 `mod tests` 搬入 `test_kit` 並 `pub(crate)` 曝出的 `SeedRestoreGuard`〔T008〕；redis 鍵 uniq 前綴；顯式注入 `X-Real-IP`）；*unit*＝純函式（TTL 公式、映射、值域、截斷）；*工具*＝自帶 `test`＋一正一反。
★base-web 側**零測試框架** ⇒ 判準按 task 分軌：凡 `base-web/**` 之 task 先紅後綠不適用、把關＝`pnpm typecheck`＋`fork-delta-lint` rc 0＋兩段 review＋CDP 走查；同單元內 `rust-api/**` 之 task 仍走先紅後綠。混合單元（U5／U7／U8／U9）之 `CONTEXT` MUST 逐域列出兩套驗收、review prompt「勿誤報」段列入「base-web task 無紅綠腿不算缺陷」（工程判斷 5、不動 RULES）。

**Organization**: 依 user story 分 phase（US1～US6）；本刀 story 間有天然順序相依（login.rs 步驟遞進、router／contract 逐 phase 加列）；**執行單元對映**（research R15、本檔文末表）為 Workflow 派發粒度、每單元一顆外層 commit（單元收尾六步序＝CLAUDE.md §2）。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 檔域不相交、可分派給不同執行單元或同單元內不同 implementer；★僅指「可分派」——**cargo 執行一律序列**（容器內 `--test-threads=1`）。
- **[Story]**: US1～US6；Setup／Foundational／Polish 不掛。

## 全程紀律（每 task 隱含、不逐條重複）

- ★**實作前先讀** research R2 對應之 rev5 碼（`../fork260509-rev5/rust-api/`、`../fork260509-rev5/base-web/`、`../fork260509-rev5/tools/`＝凍結 worktree、**唯讀、絕不寫入**、派 agent 時唯讀令烤進 prompt＝RL-0064）；高度參照、**重打字消化不拷貝**、註解一律 rev6 語境重寫（rev5 出處帶 `rev5:`）；research R3 二十筆差異點與承襲防回歸十七筆**不得帶回**。
- ★**Amendment 硬閘**：T001 未 accepted 前**不得動任何 base-web 既有檔**（`.env*` 亦屬既有檔）；純新增檔（`rev6-auth.d.ts`／`rev6-auth.ts`／`zh-tw.ts`）依 §III.2 表外宣告 3 不受此閘。
- ★**跨子庫同步律（閘讀工作樹、觸發於外層 pin bump）**：`wire-schema`（typings 側 base-web／快照側 rust-api）與 `msg-key-gate`（`MSG_KEYS` 側 rust-api／三檔 locale 側 base-web）皆兩側對賬——兩側改動須在**同一顆外層 commit** 同時 bump 兩 pin（子庫各自先 commit、外層 `git add rust-api base-web` 一次）；單側先 bump＝閘紅或歷史留分叉組合。
- ★**API 差異守則**（research R1）烤入 implementer：jsonwebtoken 11／argon2 0.6（`OsRng` 已無、亂數走 `getrandom::fill`）／redis 1.7／sha2 0.11／captcha 1.0.0；rev5 檔只當藍本、照新版 API 寫。
- rust build／test **一律容器內、全程序列**：`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1`；容器內 `cargo fmt --all --check`（碼面閘）。
- ★**絕不 push／merge**（本清單零 push／merge 任務；收尾整合走 finishing、需 user 同意）。
- **兩段式 commit＋pin bump（六步序⑤、次序不可反）**：子庫內 commit → 回外層 `git add <子庫>`（先把新 gitlink 進 index）→ `python3 tools/docsync generate`（`_pin` 讀 index；反序即產舊 pin 的 STATE、GT-01 當場擋）→ `git add docs/generated docs/arc42/ARCHITECTURE.md docs/ops/LESSONS.md tools/orchestration/_sk_rules.js` → 外層 commit；★生成物（GENERATED_FILES）一律主線動作、**不入任何 agent 允許檔案清單**；pin bump 使 `STATE.md` 過期、ROUTES 增列使 `routes.md` 過期、ADR／BACKLOG 增列使 `DECISIONS-INDEX.md`／`STATE.md` 過期。
- ★**發射前置**（brainstorm Q10）：每單元 `python3 tools/orchestration/assemble.py tmp/003-uN.py tmp/003-uN.mjs` 組裝後、發射前把 `tmp/003-uN.mjs` 之 `IMPL_OPTS` 改 `opus[1m]`（骨架真源不動；重組後須再調）；Workflow launch 與 `python3 tools/wf-watchdog.py <token>` Monitor 同回合原子成對、token≠`test`。
- 測試環境紀律：redis 測試鍵 uniq 前綴（時戳＋pid；dev 與測試共用 DB 0）；`sys_login_attempt.real_ip` INET NOT NULL ⇒ 顯式注入 `X-Real-IP`；寫入 `sys_token`／`session_event`／`sys_login_attempt` 的案帶 `SequenceResetGuard`；fixture 一律 **UPDATE 而非 INSERT**（`sys_user` 有 sequence）且還原時顯式把 `updated_at`／`updated_by` 歸 NULL（gate2 seed 逐列）。
- 書面產物與註解一律 zh-TW；`/mnt/d` 跑過 compose 後同 shell 先重新 `cd`；隨遷工具拷入後先 `python3 tools/docsync lint`（GT-05 五形）。

---

## Phase 1: Setup（★主線閘：憲法 Amendment 凍結＋前置體檢）

**Purpose**: 取得 base-web inline 的憲法授權（user 親決）、環境就緒。★本 phase 全數主線任務、不入 agent 單元。

- [x] T001 ★主線任務（user 親決）：`docs/arc42/decisions/ADR-00026-constitution-amendment-star-tracks-and-behavior-islands.md` proposed→accepted＋`.specify/memory/constitution.md`（§III.2 表落八列逐字＝ADR §一、**同批移除哨兵句**；§I.7「已入憲行為島」段替換為 ADR §二島 A～E＋跨島註＋跨島總則＋末句；承襲指針表 A～E 列尾註「；rev6 已入憲 v1.3.0（ADR-00026）」；文末 `Version` 1.3.0／`Last Amended`／Amendment log 加 1.3.0 列）＋§I.2 第三點 PATCH 級釐清（「builtin 三頁」→「builtin 常量集、現五條」＝ADR-00026 §四）＋`README.md` 憲法版本鏡像行（含 `現行 1.2.0＝ADR-00022`）→「現行 1.3.0＝ADR-00026」＋`tools/fork-delta-lint.py` self_test 註解「rev6 §III.2 現為空表」改現在式（樣本走合成名冊 t_s2、不讀真憲法 ⇒ 樣本名 `BASE-WEB-I18N-WIRING(i)` 與現表同名無害、屬刻意複用而非隔離）＋`python3 tools/docsync errata 1.2.0`／`errata 空表` 復掃＋`python3 tools/fork-delta-lint.py` rc 0（名冊七名、哨兵句已移）＋`generate`；獨立 commit `docs(constitution): amend §III.2 首批 ★ 軌道四條八用途＋§I.7 島 A～E（1.2.0→1.3.0）`。**DoD：lint 全綠；此 commit 落地即解除 base-web 既有檔硬閘**
- [x] T002 前置體檢：`bash tools/bootstrap.sh` 綠；`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait` 七件起得齊；容器內 `cargo --version`＝1.96.1、`cargo fmt --version` 可用；base-web 容器 `pnpm typecheck` 基線綠；`python3 tools/schema-gate.py check` 三閘綠（走查前基線）；`python3 tools/walkthrough-baseline.py` 於 U10a（U4 後、U5 前）遷入；自 U5 起每次真登入走查前 snapshot、後清理→diff rc 0（FR-036 硬前置）

---

## Phase 2: Foundational（阻塞全部 user story：U1 依賴與基座 → U2 碼表與基礎模組 → U3 facade → U4 真驗章）

**Purpose**: 未完成前不得開任何 US——依賴進場、`AppState` 五欄、碼表九可發、cache／jwt／password／request_context、六支 facade、真驗章與 `dev_identity` 汰換、測試設施。

### U1 依賴與基座（research R1／R7-10／R7-12／R12；contracts/code-gates.md §5）

- [x] T003 ★主線任務（user 已於 clarify Q1／D1～D6 拍板、主線擬稿即 accepted）：兩筆 ADR 於 `docs/arc42/decisions/`——②`AppState` 恰兩欄封條翻案→五欄（決定文＝clarify Q1；provenance 引 `rev5:ADR 0029` 同位、spec FR-032）③root `Cargo.toml`「不引 argon2」翻案＋server 依賴清單（附 research R1 雙源表、D1～D6 紀錄、`getrandom` 同值直採理由）；accepted＋`generate` 同 commit
- [x] T004 依賴八支釘版：`rust-api/Cargo.toml` `[workspace.dependencies]` 加 jsonwebtoken 11.0.0（`default-features = false`）／argon2 0.6.0／redis 1.7.0（`default-features = false`）／captcha 1.0.0（`default-features = false`）／sha2 0.11.0／hex 0.4.3／log 0.4.34／getrandom 0.4.3；`rust-api/server/Cargo.toml` 逐 crate `workspace = true`＋features（jsonwebtoken `rust_crypto`★漏開＝decode 執行期 panic；redis `connection-manager`＋`tokio-comp`）＋依賴清單註解重寫；root 檔頭「不引 argon2」句改現在式（指 ADR ③）；容器內 `cargo update -p log`（0.4.33→0.4.34 單一副本）＋`cargo build --workspace` 綠；`Cargo.lock` 入版控（新增套件清單記 commit 訊息；sha2 兩副本＝D4 已知代價）
- [x] T005 [P] `rust-api/server/src/config.rs` 六 getter（`jwt_secret`／`refresh_token_secret`／`jwt_iss`／`jwt_aud`／`redis_url`／`captcha_secret`；`APP_JWT_JWT_SECRET[_FILE]`／`APP_JWT_REFRESH_TOKEN_SECRET[_FILE]`／`APP_JWT_ISS`／`APP_JWT_AUD`／`APP_REDIS_URL[_FILE]`／`APP_CAPTCHA_SECRET[_FILE]`；沿 `env_or_file` 四段 panic 條件、各附 `*_with(lookup)` 注入形）＋逐鍵測試先紅後綠；檔頭「002 刀只讀 `APP_DATABASE_URL`」句改現在式
- [x] T006 `rust-api/server/src/state.rs` 兩欄→五欄（`jwt: JwtConfig{access_secret, refresh_secret, iss, aud}`／`cache: Option<SessionCache>`（★`None` 只給測試＝快取自始缺席、production 恆 `Some`）／`captcha_secret: String`；封條句改「恰五欄（ADR ②）」；編譯期窮舉解構錨測改五欄）＋★`AppState` 建構點全改（`grep -rn 'AppState {'` 現算：`main.rs`／`router.rs` 2 處／`handler/system_settings.rs` 2 處／`tests/common/mod.rs` `state_from_parts`＋`stub_state`（`cache: None`、`captcha_secret` 字面 `stub-captcha`＝非機密、測試 `JwtConfig` 字面））；★同批新建 `rust-api/server/src/cache/mod.rs`＋`rust-api/server/src/lib.rs` `pub mod cache;`（本單元只落 `SessionCache = redis::aio::ConnectionManager` 型別別名與 `connect(redis_url)` fail-loud 兩件；六鍵 builder 與原語隨 T009 補實）。**DoD：先紅後綠、既有 contract 4 case 仍綠（registry 條數＝ROUTES 中有 case 之條數）**
- [x] T007 `rust-api/server/src/main.rs` boot 鏈：config 六 getter→`JwtConfig` 組裝→`cache::connect(redis_url)`（★建連失敗 fail-loud panic、絕不退 `None`）→`captcha_secret` 注入→`AppState` 五欄；★BL-00026：`let mut connect_options = ConnectOptions::new(&database_url); connect_options.sqlx_logging_level(log::LevelFilter::Debug); Database::connect(connect_options)`（`sqlx_logging_level` 回 `&mut Self`、不可鏈進 `connect`）＋刪「屬 BACKLOG 候選、002 刀不引 log crate」自陳註解＋`python3 tools/docsync errata 不引 log crate` 復掃零殘留。**DoD：`up -d --wait` 七件起得齊、boot log 首行不再是 sqlx notice**
- [x] T008 [P] `rust-api/server/src/model/facade/test_kit.rs` 擴充（承 rev5 `model/mod.rs` 之 `test_db`、rev6 落既有 test_kit）：`real_state()`（真 DB＋真 redis＋seed enforcer＋測試 `JwtConfig`＋`captcha_secret`）／`real_app()`（沿 002 handler 內 `real_app` 收攏）／`uniq_prefix()`（時戳＋pid）／`SessionRowsGuard`（Drop：`DELETE` 本測試寫入之 `sys_token`／`session_event`／`sys_login_attempt` 列＋`UPDATE sys_user SET session_id = NULL`）／`SequenceResetGuard`（Drop：`setval('sys_token_id_seq',1,false)`＋`session_event_id_seq`＋`sys_login_attempt_id_seq`）／`X-Real-IP` 注入 helper；★`SeedRestoreGuard` 與相依（`RowSnapshot`／`RowFixupGuard`／`snapshot_of`／`assert_restored`）自 `rust-api/server/src/handler/system_settings.rs` 私有 `mod tests` 搬入本檔並 `pub(crate)` 曝出（可見性放寬＝RL-0070、同批補消費者面斷言；`system_settings.rs` 改 `use`、既有測試不動）；★本單元 `real_state()` 之 `cache` 為 `None`——真 redis 接線與簽發 token helper 隨 U2 T010 續補（本檔在 U2 清單）；範式沿 002 三件（獨立 OS thread＋一次性 runtime＋全新連線＋`thread::panicking()` 二分支、raw SQL `Statement` 不觸 `entity_access_lint`）；檔頭 BL-00041「rev5 002 刀時」→「`rev5:002` 刀時」（提及形）。**DoD：守衛 Drop 後 `python3 tools/schema-gate.py check` gate2 綠**

**Checkpoint（U1）**: 八支依賴在場、五欄 `AppState` 可起、boot 鏈接線、測試設施齊備；rust-api commit＋外層 pin bump＋generate

### U2 碼表與基礎模組（data-model §6／§11；contracts/msg-keys.md；research R7-3）

- [x] T009 [P] `rust-api/server/src/cache/mod.rs` 補實（★`lib.rs` 之 `pub mod cache;` 與 `SessionCache`／`connect` 已於 T006 落、本 task 只填模組本體；`lib.rs` 絕不裸寫 `captcha::`）：六支 key builder（`session:denylist:{sid}`／`session:{sid}:last_activity`／`session:rotate-grace:{token_hash}`／`session:idle-emitted:{sid}`／`throttle:lock:user:{name}`／`throttle:captcha:used:{nonce}`；★字面逐字承 rev5、不含 ip 維與 unlock 鍵）＋原語（`get_string`／`set_ex`／`set_nx_ex` 回 bool／`del`／denylist 讀寫／last_activity／grace）＋`GRACE_TTL_SECS = 30`／`REASON_KICKED`／`REASON_REVOKED`；★**nil↔Err 嚴格分流**（GET 一律 `Option<T>`：nil→`Ok(None)`、連線故障→`Err`）；redis 1.7 owned `FromRedisValue`。**DoD：真 redis（uniq 前綴）＋壞 redis（不存在位址）雙路測先紅後綠**
- [x] T010 [P] `rust-api/server/src/auth/jwt.rs` 新建（★同批 `rust-api/server/src/auth/mod.rs` 加 `pub mod jwt;`）：`Claims` 八欄（`uid`／`sid`／`jti`／`roles` hint／`iss`／`aud`／`exp`／`iat`）＋`sign`／`verify_access`／`verify_refresh`（★各自秘鑰；HS256、`leeway=0`、`validate_exp`、`set_issuer`／`set_audience`；jsonwebtoken 11 API、enum match 補 `_` 臂）＋`token_hash`（`hex(sha2::Sha256::digest(jwt))`）＋`TokenTtl`／`access_ttl_secs`（`min(300, N×60/2)`）／`refresh_ttl_secs`（`N×60+access`）＋`ttl_from_settings(conn)`（★三重 fail-loud：查詢失敗／列缺失／不可 parse 一律 `5000`）＋`uuid_v4()`（`getrandom::fill` 16 bytes 設版本位）；★`test_kit` 續補：`real_state()` 改帶真 redis（`cache: Some(cache::connect(config::redis_url()))`）＋簽發 helper 固定簽名 `sign_access_for(uid, roles) -> String`／`sign_pair_for(uid) -> (String, String)`（U4 起只呼叫不改）。**DoD：TTL 邊界 unit（N=60→300/3900；N=5→150/450）＋簽驗往返＋錯秘鑰紅、先紅後綠**
- [x] T011 `rust-api/server/src/error.rs`：`AppError` 加 `LoginFailed`（1000／`auth.login.failed`）／`TokenExpired`（3333／`auth.token.expired`）／`ModalLogout`（7777／`auth.session.kicked`）三變體＋`code()`／`key()` 各補三臂（`http()` 萬用臂零改動）；`pub mod msg_key` 加六常數（三固定鍵＋`BIZ_AUTH_NOT_SUPPORTED`／`BIZ_AUTH_CAPTCHA_REQUIRED`／`BIZ_AUTH_LOCKED`）；`MSG_KEYS: [&str; 13]`＝既有七鍵序＋六鍵追加（常數引用形、宣告序＝contracts/msg-keys.md）；★八處測試逐字改對（R7-3：`issuable_six_and_no_variant_seven` 改名＋6→9／`no_variant` 期望 7→4／`matrix()` 之 1000／3333／7777 三列補 key・http・sample（列數恆 13、不新增列）／`issuable_witness` 補三臂／第二份 `no_variant` 同步／`msg_keys_roster_is_exactly_seven_and_unique` 改十三／`fixed_variant_keys_are_in_roster` 補三／`biz_two_keys_are_in_roster` 改五）＋檔頭與 doc 六處自陳（「變體集恰六」「002 刀不帶」「跨端閘…不入 002 刀、BACKLOG 承載」「002 刀恰七鍵」＋`enum AppError` doc「data-model §6 六列逐字」→九列並改指本刀 data-model §11＋`MatrixRow` doc「六列」→九列）改現在式；★三新變體處補三分碼射程碼註（research R4：3333 僅 access exp 過期；標頭缺席・非 Bearer・簽章不符・已撤銷・refresh 鏈失效→8888；被踢→7777）；★`rust-api/server/tests/contract.rs` 之 `msg_roster_every_key_has_an_emitter` 重掛 `#[ignore]` 並記回填點「六鍵發出點隨 US1～US5 落齊、U9 末移除」（002 T036 同形）。**DoD：先紅後綠；13 碼矩陣測試不動仍綠**
- [x] T012 [P] `rust-api/server/src/model/password.rs` 新建（★同批 `rust-api/server/src/model/mod.rs` 加 `pub mod password;`、檔頭現在式自述改寫）：`verify(phc, password)`（`PasswordHash::new`→`Argon2::default().verify_password`；argon2 0.6 API）＋`dummy_verify`（`OnceLock` 快取 dummy PHC、每次跑滿一輪＝時序等化；★不用 `SaltString::generate`／`OsRng`）；本刀不產 hash。**DoD：seed PHC 對明文成功／錯密碼失敗／`dummy_verify` 耗時同量級，先紅後綠**
- [x] T013 [P] `rust-api/server/src/request_context.rs`（現為空結構）加 `real_ip`／`x_forwarded_for`／`ip_confidence` 三個原樣轉錄欄＋`from_headers`（`real_ip`＝`X-Real-IP` 解析 INET、缺席＝`Err`→handler 回 `5000` 並記結構化 warn；`x_forwarded_for` 截斷 1024＋剝 CR/LF；`ip_confidence` 恆 `nginx_peer`）；★零信任判定（004 ip-trust-anchor 接手只換推導）。**DoD：截斷／剝控制字元／缺席 unit 先紅後綠**

**Checkpoint（U2）**: 碼表九可發、`MSG_KEYS` 十三、cache／jwt／password／request_context 在場；rust-api commit＋pin bump

### U3 facade 六支（data-model §1～§5；`entity_access_lint` 唯一管道）

- [x] T014 [P] `rust-api/server/src/model/facade/sys_token.rs` 新建：`insert`／`find_by_hash_for_update`（`SELECT … FOR UPDATE`）／`has_active_in_chain`／`rotate`（★舊列→`rotated`＋`used_at`、插新 `active` 同鏈，次序不可反；partial UNIQUE 衝突 `DbErr` 由 caller 辨識）／`revoke_family`／`revoke_others_of_user`／`revoke_row`；`STATUS_ACTIVE`／`ROTATED`／`REVOKED` 常數。**DoD：真 DB 案（`SessionRowsGuard`＋`SequenceResetGuard`）先紅後綠、含並發 rotate 唯一鍵衝突案**
- [x] T015 [P] `rust-api/server/src/model/facade/session_event.rs` 新建：`insert`（append-only 八欄；★`source_ip` varchar(45)、與 `real_ip` 不共 helper；`created_by` nullable）
- [x] T016 [P] `rust-api/server/src/model/facade/sys_login_attempt.rs` 新建：`insert`（best-effort 由 caller 決定）＋`count_recent_failures`（★raw SQL `GREATEST` 三源下界逐字帶入不簡化：窗起點／窗內最近成功 `MAX(created_at)`／`unlock_marker` 綁 NULL；子查詢帶窗下界；碼註「unlock 源恆 NULL＝已知態」）
- [x] T017 [P] `rust-api/server/src/model/facade/sys_menu.rs` 新建（讀面）：`list_active`／`visible_menu_routes(enforcer, roles)`（Casbin `menu` 維度 `get_filtered_policy(0, [role, "", "menu"])`、`MgmtApi`）／`to_menu_route`（data-model §5 逐欄：`id` 字串、`meta.title` 恆存、`icon_type` 拆 `icon`／`localIcon` 不外洩、`meta.roles` 不下發）／`constant_routes`（★`constant = TRUE`、勿 `IS NOT FALSE`）／`route_exists(name)`
- [x] T018 [P] `rust-api/server/src/model/facade/sys_user.rs` 新建（auth 消費面）：`find_by_user_name`／`find_by_id`／`advisory_lock_user(txn, uid)`（`SELECT pg_advisory_xact_lock($1)`）／`write_session_id`／`session_policy` 值域收斂（`single`｜`multi`｜`inherit`、零 CHECK）
- [x] T019 `rust-api/server/src/model/facade/sys_role.rs` 新建：`enabled_roles_of_user`／`home_of_roles`（★收斂律＝啟用角色 `status=1` 依 role id 升冪取首個非空 `role_home`、全空→`home`；碼註釘住＋合成多角色測試守）；`rust-api/server/src/model/facade/mod.rs` 註冊八支（★嚴格 ASCII 升冪：`session_event`／`sys_login_attempt`／`sys_menu`／`sys_role`／`sys_token`／`sys_user`／`sys_user_role`／`system_settings`；檔頭「一張表配一支模組」句改八支）；`rust-api/server/tests/entity_access_lint.rs`：六支新 facade 檔落在既有排除面（`excluded_dirs()` 恰等 `model/facade` 一層、不得擴），本 task 只確認 facade 之外零 path-root `entity::`（新 handler 檔自然入掃描面）。**DoD：六支 facade 案先紅後綠、entity_access_lint 綠**

**Checkpoint（U3）**: 六支 facade 在場、唯一管道 lint 綠；rust-api commit＋pin bump

### U4 真驗章與 `dev_identity` 汰換（spec FR-011／FR-033／FR-024；research R7-2）

- [x] T020 `rust-api/server/src/auth/enforce.rs` 換真驗章：`verify` 單一驗證器（debug／release 同形、cfg 分支收斂）→`jwt::verify_access`（`ExpiredSignature`→`TokenExpired` 3333；其餘驗章失敗／缺席／非 Bearer→`Logout` 8888）→denylist 查（★四級降級：redis 命中 reason `kicked`→`ModalLogout` 7777、`revoked`→8888／nil→放行／`Err`→PG `sys_token::has_active_in_chain`、無 active→8888 fail-closed／PG 亦 `Err`→視為無 active 絕不盲放）→放行後 best-effort 推進 `last_activity`（`Some(cache)` 時）；`Identity` 欄集不動、`user_name` doc 改已知態（Claims 無帳號名 ⇒ 空字串、消費者以 uid 現查）；`rust-api/server/src/obs.rs` pre-register `denylist_hit_total{source=redis|pg}`；三分碼碼註（R4）。**DoD：四級降級各一案（真 redis／壞 redis 退 PG／PG 亦壞／nil 放行）＋三分碼案先紅後綠**
- [x] T021 汰換 dev-only 驗證器：刪 `rust-api/server/src/auth/dev_identity.rs` 整檔＋`rust-api/server/src/auth/mod.rs` 移除 `pub mod dev_identity;`＋doc 改寫＋`rust-api/server/src/lib.rs` 模組樹句；★測試面真 token 化（R7-2 實查）：`rust-api/server/src/router.rs` 3 處、`rust-api/server/src/handler/system_settings.rs`（以 `grep -c 'dev-super\|dev-admin\|dev-user'` 現算、現 103 行；逐處換 `test_kit` 簽發 helper、**斷言不動**＝FR-033、完工該 grep 回 0）、`rust-api/server/tests/contract.rs` 14 處分三類：①通則未認證案→「缺席／非 Bearer／垃圾 token 三形皆 8888」②`synthetic_policy_route_with_dev_token` 兩處與 `observed_msgs` 一處→真簽發 token ③`observed_msgs_real_db` 五處（0000／5003／biz 兩鍵之唯一發出點）→真簽發 token＋植真 `sys_token` 列並還原；★integration crate 取不到 `#[cfg(test)] pub(crate)` 之 `test_kit` ⇒ 簽發走公開 API `server::auth::jwt::sign`、helper 落 `rust-api/server/tests/common/mod.rs`（`state_from_parts` 五欄；`real_seed_app` 加可帶 `Some(cache)` 形＝`server::cache::connect(server::config::redis_url())`）；`docs/arc42/ARCHITECTURE.md` 由 generate 重產（例外註冊面）。**DoD：容器內 `cargo test` 綠＋`cargo build --release -p server` 首次可跑（以 release 二進位起服務打 `/health` 回 `ok`）**

**Checkpoint（U4）**: 真驗章上線、release 可跑、denylist 降級鏈自證；rust-api commit＋pin bump＋generate

---

## Phase 3: User Story 1 — 真帳密登入取得會話、側邊欄由後端生成（P1）🎯 MVP

**Goal**: 三個 seed 帳號真登入，側邊欄呈現後端 Casbin 過濾後的角色化選單；快速登入鈕仍可用。

**Independent Test**: quickstart §1——三帳號登入看側邊欄差異；`getUserInfo` 四欄型別對齊 typings；`getConstantRoutes` 未認證可取且前端合併不清空 builtin 五條。

### Tests for User Story 1 ⚠️（先寫、先確認紅）

- [x] T022 [P] [US1] contract case ×5 加入 `rust-api/server/tests/contract.rs` registry：`auth-login`／`auth-get-user-info`／`route-get-user-routes`／`route-get-constant-routes`／`route-is-route-exist`（wire 形依 contracts/wire-auth.md／wire-route.md；每 case 之 verify 須能在配到別條 path 時紅；Authed 兩條含未認證三形 8888 案；login 含 body rejection→1000 案）；`observed_msgs` 追加本 phase 發出點
- [x] T023 [P] [US1] integration 骨架於 `rust-api/server/src/handler/auth/user_info.rs`／`handler/route.rs`／`handler/auth/login.rs` 之 `#[cfg(test)]`：三帳號登入→`getUserInfo` 四欄（`userId` 字串、`userName` User→`User01`、`roles` DB-fresh、`buttons` 非空）＋`getUserRoutes` 樹依角色差異＋`home` 可導航葉＋★login 四條失敗路徑（帳號不存在／密碼錯——皆 `1000 auth.login.failed`／已停用 fixture＝`UPDATE sys_user SET status=2 WHERE id=3`／鎖內重驗失敗 fixture＝植第三個 status 值；RAII 還原顯式歸 `updated_at`／`updated_by` NULL；判別器＝`sys_login_attempt` 恰一列且 `created_by` 有無值）＋稽核列三處寫入點各一案

### Implementation for User Story 1

- [x] T024 [US1] `rust-api/server/src/handler/auth/login.rs` 新建（★同批新建 `rust-api/server/src/handler/auth/mod.rs`＝本單元兩子模組 `login`／`user_info` 之 `pub mod` 宣告、檔頭註「宣告行逐單元遞進」——`refresh`／`logout`／`alt_stub` 三行分別隨 T034／T041／T059 加列；`rust-api/server/src/handler/mod.rs` 加 `pub mod auth;`）——十一步之③`authenticate`（三態 collapse `1000`、查無亦跑 `dummy_verify`）④txn＋`sys_user::advisory_lock_user` ⑤鎖內重驗（不重跑驗章）⑥`jwt::ttl_from_settings`（缺失→`5000`）⑦新 sid（uuid v4）＋簽對 ⑧`sys_token::insert` ⑩稽核成功列 txn 內 ⑪commit 後 best-effort denylist 起點／`last_activity`；★稽核列三處（Denied 外層 conn／鎖內重驗失敗先 rollback 再外層 conn／成功 txn 內）、best-effort 失敗只發結構化 warn（`target: "security.throttle"`＋`degraded=db_write` 欄；counter 遞增隨 T052 之 `throttle_degraded_total` 預註冊接上、本單元不動 `obs.rs`）；`LoginReq` `FromRequest` 自訂 rejection→`1000`；步驟①②留 T051、⑨留 T039
- [x] T025 [P] [US1] `rust-api/server/src/handler/auth/user_info.rs` 新建：四欄回包（`buttons`＝`button` 維度 `get_filtered_policy` 枚舉、非 `enforce*`；`userId` 用既有 `serialize_i64_as_string`）
- [x] T026 [P] [US1] `rust-api/server/src/handler/route.rs` 新建：`get_user_routes`（DB-fresh roles→過濾→祖先包含→同層 `order`→`id` 升冪；`home` 經 `resolve_home` 兜底）／`get_constant_routes`（現回 `[]`）／`is_route_exist`（`?routeName=`）
- [x] T027 [US1] `rust-api/server/src/router.rs` 加 5 條 ROUTES（`/auth/login` POST／Public、`/auth/getUserInfo` GET／Authed、`/route/getConstantRoutes` GET／Public、`/route/getUserRoutes` GET／Authed、`/route/isRouteExist` GET／Authed；case_key＝data-model §12）＋`ROUTES_COUNT` 4→9＋`router.rs` `mod tests` 之 `routes_block_literal_form_and_pinned_rows` 釘值 4→9（「002 刀恰四條」訊息與同 `mod tests` doc 之「＝4」「現行四條」舊數量詞同批改現在式；後續單元只改釘值）＋`tools/docsync/tests/test_references.py::TestRoutes::test_real_repo_pinned_rows` 真 repo 釘列同批增至 9 列（RL-0022 連動釘值檔）；★每欄一行窄形、單動詞、`docs/generated/reference/routes.md` 由主線 generate 重算 9 列
- [x] T028 [US1] `rust-api/server/tests/wire_schema.rs` 裁判面補 `Api.Auth.LoginToken`／`Api.Auth.UserInfo`／`Api.Route.MenuRoute`／`Api.Route.UserRoute` case（序列化輸出對快照）；快照零改動（upstream typings 已在）
- [x] T029 [US1] base-web `.env` 兩行 ADAPT（`VITE_AUTH_ROUTE_MODE=static`→`dynamic`、`VITE_HTTP_PROXY=Y`→`N`）＋`.env.test`／`.env.prod` 各一行（`VITE_SERVICE_BASE_URL` apifox→`/api`）；標記形 `# [rev6-inline BASE-WEB-ADAPT 003-auth-session] 原行: <基線該行>`（★T001 後才可動）；`python3 tools/fork-delta-lint.py` rc 0
- [x] T030 [US1] base-web `src/store/modules/route/index.ts` ★`BASE-WEB-AUTH-WIRING(a)`：`initConstantRoute` dynamic 分支改 `addConstantRoutes([...staticRoute.constantRoutes, ...data])`（合併非取代）；修改型標記 `// [rev6-inline BASE-WEB-AUTH-WIRING(a) 003-auth-session] 原行: …`。**DoD：`pnpm typecheck` 綠、fork-delta rc 0、登入頁仍可達**
- [x] T031 [US1] 走查 quickstart §1（三帳號登入＋側邊欄差異＋快速登入鈕三顆＋`getConstantRoutes` 未認證可取）；★走查三步（FR-036）：`python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-<單元>.json`（rc 0）→走查→清理（quickstart §8：`single_session_default` 若翻過翻回、三表 DELETE、`session_id` NULL、三支 setval、redis `session:`／`throttle:` 前綴 DEL）→`diff` rc 0；rust-api 與 base-web 各自 commit → 外層一顆 commit 同時 bump 兩 pin＋generate（routes.md 9 列）

**Checkpoint**: US1 完成——**MVP**：rev6 第一次端到端可見。

---

## Phase 4: User Story 2 — access 過期無感續期（token rotation）（P2）

**Goal**: access 過期以 refresh 自動換發；並發換發不誤判盜用。

**Independent Test**: quickstart §2——同票二度換發 30 秒內回同一對；同票兩並發一 rotate 一走 grace；驗章失敗一律 8888。

### Tests for User Story 2 ⚠️

- [x] T032 [P] [US2] contract case `auth-refresh-token`（POST／Public；含 body rejection→8888 案）加入 `rust-api/server/tests/contract.rs`；`observed_msgs` 追加
- [x] T033 [P] [US2] integration 於 `rust-api/server/src/handler/auth/refresh.rs` `#[cfg(test)]`：①`active`→rotate 新對（新對 TTL 讀現值）②同票二度→grace 冪等同一對 ③grace 窗外→reuse＋撤家族＋`session_event(reuse)`＋8888 ④驗章失敗／查無列→8888 ⑤同票兩並發→一 rotate 一 grace、不觸 reuse（唯一鍵衝突 `DbErr` 辨識、不得籠統 `5000`）⑥`session_idle_timeout` 缺失→`5000`

### Implementation for User Story 2

- [x] T034 [US2] `rust-api/server/src/handler/auth/refresh.rs` 新建（`handler/auth/mod.rs` 加 `pub mod refresh;`）：驗章失敗一律 8888（★絕不 3333）；`find_by_hash_for_update` 鎖列後分流——`active`→`ttl_from_settings`→rotate→寫 grace（TTL 30、commit 前仍持鎖）／`rotated`＋grace 命中→冪等回既發後繼／`rotated`＋grace miss→`revoke_family`＋`session_event(reuse)`＋denylist(revoked、TTL＝refresh 全壽命)→8888／查無列→8888；`RefreshReq` rejection→8888；`revoked` 三分支與 idle 判定留 T040
- [x] T035 [US2] `rust-api/server/src/router.rs` 加 `/auth/refreshToken`（POST／Public）＋`ROUTES_COUNT` 10＋`router.rs` `mod tests` 之 `routes_block_literal_form_and_pinned_rows` 釘值 9→10（assert 訊息隨釘值同批改現在式）＋`tools/docsync/tests/test_references.py::TestRoutes::test_real_repo_pinned_rows` 真 repo 釘列同批增至 10 列（RL-0022 連動釘值檔）
- [x] T036 [US2] 走查 `specs/003-auth-session/quickstart.md` §2；★走查三步（FR-036）：`python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-<單元>.json`（rc 0）→走查→清理（quickstart §8：`single_session_default` 若翻過翻回、三表 DELETE、`session_id` NULL、三支 setval、redis `session:`／`throttle:` 前綴 DEL）→`diff` rc 0＋rust-api commit＋外層 pin bump＋generate（`docs/generated/STATE.md`／`reference/routes.md`）

**Checkpoint**: US1＋US2 獨立可用——會話可續期。

---

## Phase 5: User Story 3 — 會話撤銷與單一會話治理（logout／被踢／閒置）（P2）

**Goal**: 登出即撤、他處登入即踢（modal）、閒置逾時失效；翻轉不追溯。

**Independent Test**: quickstart §3——logout 後舊 access 8888、垃圾票 0000；single-session 翻 on 後二次登入使前一條 7777、翻前既有兩條仍可用；idle 寫舊 `last_activity` 觸發。

### Tests for User Story 3 ⚠️

- [x] T037 [P] [US3] contract case `auth-logout`（POST／Public；含 body rejection→0000 案）加入 `rust-api/server/tests/contract.rs`；`observed_msgs` 追加
- [x] T038 [P] [US3] integration 於 `rust-api/server/src/handler/auth/logout.rs`／`refresh.rs`／`login.rs` 之 `#[cfg(test)]`：①logout 後舊 access→8888 ②垃圾／已撤票 logout→0000 不落事件 ③single-session（`SeedRestoreGuard` 翻 on）二次登入→前一條 7777＋`session_event(kicked, single_session)`＋`session_id` 寫入 ④★翻 on 前既有兩條會話翻後皆仍可用（不追溯、brainstorm Q9）⑤idle 逾時→8888＋僅首次 `session_event(idle)`＋不寫 denylist ⑥被踢者 (access, refresh) 窗內換發仍 7777 ⑦`revoked` 列缺 denylist→靜默 8888 不落假 reuse ⑧`single_session_default` 缺鍵→off 語意

### Implementation for User Story 3

- [x] T039 [US3] `rust-api/server/src/handler/auth/login.rs` 補步驟⑨：兩層政策解析（`effective_single`；缺鍵 off）＋`sys_token::revoke_others_of_user`＋逐 sid `session_event(kicked, reason=single_session)`＋denylist(kicked、TTL＝refresh 全壽命)＋`sys_user::write_session_id`；★只於登入事件判定（clarify Q4 總則碼註）
- [x] T040 [US3] `rust-api/server/src/handler/auth/refresh.rs` 補 `revoked` 三分支（reason `kicked`→7777／`revoked` 或鍵缺席→靜默 8888 不落事件不重複撤）＋idle 判定（門檻＝`refresh_secs − access_secs` 取自本次 `ttl_from_settings`、僅 `last_activity` 可讀時判、`Err`／nil＝fail-open；命中→SET NX `idle-emitted` 守門→僅首次 `session_event(idle)`→8888；★不寫 denylist）
- [x] T041 [P] [US3] `rust-api/server/src/handler/auth/logout.rs` 新建（`handler/auth/mod.rs` 加 `pub mod logout;`）：`Result<Json, JsonRejection>` 收 body（rejection→0000 no-op）；驗章成功→`revoke_row`＋denylist(revoked、refresh 全壽命)＋`session_event(logout, created_by=本人)`→0000；驗章失敗／查無列／已撤→0000 不落事件
- [x] T042 [US3] `rust-api/server/src/router.rs` 加 `/auth/logout`（POST／Public）＋`ROUTES_COUNT` 11＋`router.rs` `mod tests` 之 `routes_block_literal_form_and_pinned_rows` 釘值 10→11（assert 訊息隨釘值同批改現在式）＋`tools/docsync/tests/test_references.py::TestRoutes::test_real_repo_pinned_rows` 真 repo 釘列同批增至 11 列（RL-0022 連動釘值檔）
- [x] T043 [P] [US3] base-web `src/service/api/rev6-auth.ts` 新建（§III.1 WRAPPER、檔頭 `// [rev6-inline BASE-WEB-WRAPPER+ 003-auth-session] …`、不入 barrel）：`fetchLogout(refreshToken)`（本 phase 先落一支；`fetchLoginWithCaptcha`／`fetchLoginCaptcha` 隨 T054、四 stub 隨 T061 補齊同檔）
- [x] T044 [US3] base-web `src/layouts/modules/global-header/components/user-avatar.vue` ★`BASE-WEB-LOGOUT-UX-WIRING(i)`：`onPositiveClick` 改 async、登出前 best-effort `await fetchLogout(localStg refreshToken)`（失敗不阻斷）後 `resetStore()`；修改型標記帶 `原行:`；★(ii) reLogin toast 不開。**DoD：`pnpm typecheck` 綠＋UI 登出可走通**
- [x] T045 [US3] 走查 `specs/003-auth-session/quickstart.md` §3；★走查三步（FR-036）：`python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-<單元>.json`（rc 0）→走查→清理（quickstart §8：`single_session_default` 若翻過翻回、三表 DELETE、`session_id` NULL、三支 setval、redis `session:`／`throttle:` 前綴 DEL）→`diff` rc 0＋兩子庫 commit→外層一顆 commit 雙 pin bump＋generate（`docs/generated/STATE.md`／`reference/routes.md`）

**Checkpoint**: US1～US3 獨立可用——會話全生命週期到位。

---

## Phase 6: User Story 4 — 登入失敗節流三區＋圖形驗證碼（P3）

**Goal**: 同帳號連續失敗三區節流；軟區 captcha；答對密碼錯自動換題。

**Independent Test**: quickstart §4——<2 回 1000；2–4 回 `2222 biz.auth.captchaRequired`；≥5 回 `2222 biz.auth.locked`；任意 userName 發題；軟區拒絕後列數不變。

### Tests for User Story 4 ⚠️

- [x] T046 [P] [US4] contract case `auth-login-captcha`（GET／Public；含缺 `userName` query rejection→1000 三欄信封案）加入 `rust-api/server/tests/contract.rs`；`observed_msgs` 追加
- [x] T047 [P] [US4] integration 於 `throttle/mod.rs`／`captcha/mod.rs`／`handler/auth/login.rs` `#[cfg(test)]`：①三區轉換 ②軟區與鎖定皆驗章前擋、零稽核列零計數桶（拒絕後成功登入仍可） ③滑動窗 reset-on-success ④nonce 重放第二次拒 ⑤答錯不推進鎖定但該題已耗 ⑥兩層降級（redis 整體不可用→軟區停用且密碼錯仍計數／單次 SET NX 瞬斷→拒零計數） ⑦L2 `DbErr`→`count:=0`＋`captcha_forced = !redis_down` ⑧設定鍵讀不到→退常數＋每次載入至多一筆告警 ⑨★矛盾組合 `captcha_after > max_fails`→整組退常數＋`settings_invalid` 一筆（clarify Q3）；`captcha_after == max_fails` 合法

### Implementation for User Story 4

- [x] T048 [P] [US4] `rust-api/server/src/throttle/mod.rs` 新建（★同批 `lib.rs` 加 `pub mod throttle;`）：常數（`THROTTLE_LOCK_TTL_SECS` 900／`CAPTCHA_TTL_SECS` 300／`CAPTCHA_ANSWER_LEN` 4／`CAPTCHA_CHARSET` 34 字／`DEFAULT_MAX_FAILS` 5／`DEFAULT_WINDOW_MINUTES` 15／`DEFAULT_CAPTCHA_AFTER` 2／`LOGIN_USER_NAME_MAX` 64／`LOGIN_PASSWORD_MAX_BYTES` 512）＋`ThrottleSettings`＋`load_settings`（缺失或矛盾組合→整組退常數＋`warn_degraded(settings_default|settings_invalid)` 至多一筆）＋`precheck` 四步（L1 GET lock 命中不續期／unlock NULL＋新鮮 L2 讀／`count ≥ max_fails`→SET L1（唯一寫入點）→`biz.auth.locked`／captcha gate）＋`captcha_gate`（`verify_challenge`＋SET NX 消耗先於比對；redis 整體不可用→停用；瞬斷→拒不罰）＋`warn_degraded`（結構化 `target: "security.throttle"`＋`degraded` 欄＋counter）；★IP 維全拔、`precheck` 簽名無 real_ip 參數位
- [x] T049 [P] [US4] `rust-api/server/src/captcha/mod.rs` 新建（★同批 `lib.rs` 加 `pub mod captcha;`、絕不裸寫）：`CaptchaClaims` 四欄＋`issue(secret, user_name)`（`::captcha::Captcha::new()` 逐字 `add_char`＋`Noise`／`Wave` 濾鏡＋`as_base64()`→data URI；nonce 與答案取 `getrandom::fill` 拒絕採樣）＋`sign`／`verify_challenge`（HS256、不驗 iss/aud、`leeway=0`）＋`answer_mac`＝`hex(SHA256(secret ‖ nonce ‖ lower(answer)))`；★撞名消歧三規則＋檔頭碼註；字型涵蓋測試（`supported_chars()` ⊇ 34 字）
- [x] T050 [P] [US4] `rust-api/server/src/handler/captcha.rs` 新建（★同批 `handler/mod.rs` 加 `pub mod captcha;`、一律 `crate::captcha::`）：`GET /auth/loginCaptcha?userName=`——任意 userName 發題不查 DB、超限走 `1000` 同形閘、Query rejection→1000 三欄信封、產圖／簽章失敗→`5000`
- [x] T051 [US4] `rust-api/server/src/handler/auth/login.rs` 補步驟①②：①輸入形制閘（超限→`1000`、零稽核零驗章零桶）②`throttle::precheck`（`?` 早退＝構造上零落列）；軟區 captcha 兩欄非軟區完全忽略
- [x] T052 [US4] `rust-api/server/src/obs.rs` pre-register `throttle_degraded_total{source}`（★七值逐字＝R5：`settings_default`／`settings_invalid`／`redis_lock`／`redis_lock_set`／`redis_captcha`／`db_count`／`db_write`）＋`throttle_soft_zone_total`（無 label；`captcha_forced` 不計入）。**DoD：render 文本含全部組合顯式 0，先紅後綠**
- [x] T053 [US4] `rust-api/server/src/router.rs` 加 `/auth/loginCaptcha`（GET／Public）＋`ROUTES_COUNT` 12＋`router.rs` `mod tests` 之 `routes_block_literal_form_and_pinned_rows` 釘值 11→12（assert 訊息隨釘值同批改現在式）＋`tools/docsync/tests/test_references.py::TestRoutes::test_real_repo_pinned_rows` 真 repo 釘列同批增至 12 列（RL-0022 連動釘值檔）
- [x] T054 [P] [US4] base-web `src/typings/api/rev6-auth.d.ts` 新建（`// [rev6-inline BASE-WEB-ADAPT+ 003-auth-session] …`；declaration merging 併入 `Api.Auth`：`LoginCaptcha{captchaId: string; captchaImg: string}`）＋`src/service/api/rev6-auth.ts` 補 `fetchLoginCaptcha(userName)`／`fetchLoginWithCaptcha(userName, password, captcha?)`（未帶 captcha 時欄位 undefined 省略＝wire 形同 upstream）；★`python3 tools/wire-schema.py extract`（base-web 容器）→`rust-api/server/tests/fixtures/wire-schema.json` 重抽含 `Api.Auth.LoginCaptcha`＋`check` 綠＋`tests/wire_schema.rs` 補 `LoginCaptcha` 裁判 case
- [x] T055 [US4] base-web ★`BASE-WEB-LOGIN-CAPTCHA-WIRING(i)`：`src/store/modules/auth/index.ts` `login()` 改 import `fetchLoginWithCaptcha` 並串通失敗 msg 回傳鏈（`captchaRequired`／`locked` 同碼 2222、以 msg 區分）＋`src/views/_builtin/login/modules/pwd-login.vue` 軟區條件渲染（圖＋輸入欄、新增型圈界）＋提交鏈接線（修改型 `原行:`）＋★軟區換題契約（登入失敗後重呼 `fetchLoginCaptcha` 換題並清空輸入；非軟區零行為變更）＋快速登入鈕零 inline；★(ii) `formRules` 不動。**DoD：`pnpm typecheck` 綠、fork-delta rc 0、瀏覽器軟區出圖、答對密碼錯自動換題**
- [x] T056 [US4] 走查 `specs/003-auth-session/quickstart.md` §4（含 metrics 三序列基線與遞增）；★走查三步（FR-036）：`python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-<單元>.json`（rc 0）→走查→清理（quickstart §8：`single_session_default` 若翻過翻回、三表 DELETE、`session_id` NULL、三支 setval、redis `session:`／`throttle:` 前綴 DEL）→`diff` rc 0＋兩子庫 commit→外層一顆 commit 雙 pin bump（wire-schema 兩側同批：`rust-api/server/tests/fixtures/wire-schema.json`＋`base-web/src/typings/api/rev6-auth.d.ts`）＋generate

**Checkpoint**: US1～US4 獨立可用——暴力破解阻力到位。

---

## Phase 7: User Story 5 — 替代登入誠實 stub＋錯誤訊息顯人話（P3）

**Goal**: 未開放流程回明確提示；所有後端 msg 經 `$t` 轉譯；跨端閘機器守三檔 13 鍵。

**Independent Test**: quickstart §5——四支 stub 皆 `2222 biz.auth.notSupported`；切語系同一 key 顯對應譯文；7777 modal 顯人話；`msg-key-gate check` 綠。

### Tests for User Story 5 ⚠️

- [x] T057 [P] [US5] contract case ×4（`auth-send-captcha`／`auth-code-login`／`auth-register`／`auth-reset-pwd`）加入 `rust-api/server/tests/contract.rs`（★四支同形 ⇒ 各自斷言 path 專屬 case_key 對映＝區別手法）；`observed_msgs` 追加
- [x] T058 [P] [US5] `tools/msg-key-gate.py` self-test 七案先落先紅（三檔全等綠／缺鍵／多鍵／缺 backend 節 rc 2／常數間接形解析成功／常數表缺該名 rc 2／動態 Biz 構造紅）

### Implementation for User Story 5

- [x] T059 [P] [US5] `rust-api/server/src/handler/auth/alt_stub.rs` 新建（`handler/auth/mod.rs` 加 `pub mod alt_stub;`）：`not_supported_stub()` 四端點共用、恆 `2222`＋`Cow::Borrowed(msg_key::BIZ_AUTH_NOT_SUPPORTED)`、`data: null`、不解析 body、零副作用
- [x] T060 [US5] `rust-api/server/src/router.rs` 加四條（`/auth/{sendCaptcha,codeLogin,register,resetPwd}` POST／Public）＋`ROUTES_COUNT` **16**＋`router.rs` `mod tests` 之 `routes_block_literal_form_and_pinned_rows` 釘值 12→16（assert 訊息隨釘值同批改現在式）＋`tools/docsync/tests/test_references.py::TestRoutes::test_real_repo_pinned_rows` 真 repo 釘列同批增至 16 列（RL-0022 連動釘值檔）；主線 generate 後 `docs/generated/reference/routes.md` 恰 16 列（DoD 機器核、零鏈式動詞）；★`tests/contract.rs` 補齊免 DB 面觀察不到的四鍵承載案（沿 002 T036 形、落 `observed_msgs_real_db`＋`rust-api/server/tests/common/mod.rs`）：3333＝以 `server::auth::jwt::sign` 簽已過期 access 打 `/auth/getUserInfo`；7777＝`real_seed_app` 帶 `Some(cache)`、以 `server::cache::denylist_set(sid, kicked)` 後持真簽發 token 打 Authed；`biz.auth.captchaRequired`／`biz.auth.locked`＝以 `sea_orm::Statement` 植 2／5 列 `sys_login_attempt` 失敗列後打 `/auth/login`（還原＝DELETE＋`setval`＋redis 前綴 DEL）——四案落齊後移除 `msg_roster_every_key_has_an_emitter` 之 `#[ignore]` 並改回填點措辭為現在式
- [x] T061 [US5] base-web `src/service/api/rev6-auth.ts` 補四支 stub wrapper（★先於 T062／T063：wrapper 先於消費者、否則 typecheck 紅）（`fetchSendCaptchaStub`／`fetchCodeLoginStub`／`fetchRegisterStub`／`fetchResetPwdStub`；七支齊）
- [x] T062 [P] [US5] base-web 三張表單 ★`BASE-WEB-AUTH-WIRING(b)`：`base-web/src/views/_builtin/login/modules/code-login.vue`／`register.vue`／`reset-pwd.vue` 各 2 處（import stub wrapper＋消滅假成功 toast；表單欄位／驗證規則／版面不動）；修改型 `原行:`
- [x] T063 [P] [US5] base-web `src/hooks/business/captcha.ts` ★`BASE-WEB-AUTH-WIRING(c)`（約 4 處）：`getCaptcha` 改打 `fetchSendCaptchaStub`、移除假延遲與假成功 toast；hook 對外簽名不變
- [x] T064 [US5] base-web `src/typings/app.d.ts` ★`BASE-WEB-I18N-WIRING(iii)`：`App.I18n.Schema` 補 `backend` 必填型節（13 鍵巢狀）；★`LangType`／locale 註冊不動。**DoD：`pnpm typecheck` 紅→T065 後綠**
- [x] T065 [US5] base-web ★`BASE-WEB-I18N-WIRING(ii)`：`src/locales/langs/en-us.ts` 與 `zh-cn.ts` 插獨佔一行 `  backend: {` 起的 13 鍵樹（新增型圈界；譯文＝contracts/msg-keys.md、簡中重打字消化）＋`src/locales/langs/zh-tw.ts` 新檔（`// [rev6-inline BASE-WEB-I18N-WIRING+ 003-auth-session] …`；`export default {` 換行後 `  backend: {` 獨佔一行；13 鍵繁中逐字；不接 runtime）。**DoD：`pnpm typecheck` 綠**
- [x] T066 [US5] base-web `src/service/request/index.ts` ★`BASE-WEB-I18N-WIRING(i)`：新增型圈界 `translateBackendMsg(msg)`＝``$t(`backend.${msg}` as App.I18n.I18nKey, msg)``＋modal `content` 與 `showErrorMsg` 鏈兩處修改型改走之（`原行:`）；★不建 `translateDetailValue`；★勿與 LOGOUT-UX(ii) 混。**DoD：`pnpm typecheck` 綠＋瀏覽器錯誤提示顯人話、7777 modal 顯人話**
- [x] T067 [US5] `tools/msg-key-gate.py` 新建（contracts/code-gates.md §2；標準庫、零 docker）：左源兩段解析（`pub mod msg_key` 常數表→`MSG_KEYS` 常數引用陣列、亦容字面；N≠元素數／解不出＝rc 2）＋右源三檔 `backend: {` brace 配對攤平＋斷言 1 逐檔雙向全等＋斷言 2 Biz 構造點守衛（字面形或 `msg_key::NAME` 常數形、解出鍵 ∈ `MSG_KEYS`；動態構造 rc 1；`#[cfg(test)]` 排除）＋rc 0/1/2/64＋`test`（T058 七案綠）；★接線五處：`.githooks/pre-commit` 新段 `pc_run "msg-key-gate"`（觸發 `-e 'rust-api' -e 'base-web' -e 'tools/msg-key-gate.py'`）＋`for t in …` 自測名冊加列＋`tools/docsync/tests/test_hook_wiring.py` SEGMENTS 加列＋`README.md` 樹加行＋`docs/ops/RUNBOOK.md` §12 碼面閘表註記列轉工具檔列（根據 ADR＝T068）與工具鏈速查加列；`git update-index --chmod=+x`；`python3 tools/docsync test`／`lint` 綠（GT-12 碼面閘表腿、GT-09）
- [x] T068 [US5] ★主線任務（clarify Q2 已拍板、主線擬稿即 accepted）：`docs/arc42/decisions/ADR-000NN-msg-key-gate-bidirectional-per-file.md`（序號落檔時取）＝ADR ⑤ 跨端閘形制＝逐檔雙向全等、無白名單、Biz 守衛兩形；與 ADR-00017 射程關係（「雙向必恆紅」指整本字典）；accepted＋`generate`＋回填 RUNBOOK §12 「根據 ADR」欄
- [x] T069 [US5] 走查 quickstart §5；★走查三步（FR-036）：`python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-<單元>.json`（rc 0）→走查→清理（quickstart §8：`single_session_default` 若翻過翻回、三表 DELETE、`session_id` NULL、三支 setval、redis `session:`／`throttle:` 前綴 DEL）→`diff` rc 0＋`python3 tools/msg-key-gate.py check` 綠＋一反（`zh-tw.ts` 刪一鍵→rc 1 指名→還原、porcelain 零差異）＋兩子庫 commit→外層一顆 commit 雙 pin bump（★msg-key-gate 兩側同批）＋generate

**Checkpoint**: 全部 US 獨立可用——本刀功能面完成；跨端閘上線。

---

## Phase 8: User Story 6 — 憲法 Amendment、治理進場與帳本落帳（P4）

**Goal**: T001 已凍結；餘＝走查基準工具遷入、BL-00037／BL-00041、ADR ④、治理自證四腿。

**Independent Test**: fork-delta 四腿一正三反；GT-12 對 `NON_GATE_TOOLS` 一正一反；hook 接線守衛刪一行即紅；`walkthrough-baseline.py test` 綠。

### Implementation for User Story 6

- [x] T070 [US6] ★U10a（於 U4 後、U5 前派發＝FR-036「MUST 排在首次真登入走查之前」；T 號不動、依相依派發）：`tools/walkthrough-baseline.py` 隨遷（自 `../fork260509-rev5/tools/walkthrough-baseline.py`、782 行、唯讀取用）：四型失效引用 rev6 化（compose 專案＝rev6 根；「rev5 dev stack」→「rev6 dev stack」、「rev4 對照 stack」→「rev5 對照 stack（2xxxx）」；裸前代編號 `B-147`／`L-071`／`L-055`／`ADR 0010`→`rev5:` 前綴、★以 `book.py` `BARE_REV5` 復掃零命中；前綴例句去 `cpwd:`）；`--user`／`--db` 預設 `soybean`／`soybean_admin_rust`；`python3 tools/walkthrough-baseline.py test` 綠、對真 stack `snapshot` rc 0；★同批把 `CLAUDE.md` §7 末句與 `docs/ops/RUNBOOK.md` §9c 之「隨首個需走查的刀遷入」句改現在式（工具落地單元改自己的預告句＝RL-0015）、`python3 tools/docsync errata 隨首個需走查的刀` 復掃零未來式殘留；★時序告誡：`git ls-files` 只看 tracked，新遷入檔在主線 `git add` 前不入 T071 推導名冊、非推導行壞掉；登記：`tools/docsync/gates.py` `NON_GATE_TOOLS` 加該檔＋`tools/docsync/tests/test_gates.py` 一正一反（含該檔綠／`patch.object` 抽掉→GT-12 紅指名）＋`.githooks/pre-commit` `for` 自測名冊加列＋`README.md` 樹加行＋`docs/ops/RUNBOOK.md`（§9c 自指針章改實文＝contracts/code-gates.md §3 五步／§12 工具鏈速查加列／§12 碼面閘表前言「現＝`tools/wf-watchdog.py`」句改兩支／檔頭「創世期章節現況」句 §9c 移入已補實文章）＋`python3 tools/docsync errata NON_GATE_TOOLS`／`errata 指針章` 復掃；`git update-index --chmod=+x`
- [x] T071 [US6] BL-00037 ①②（★與 T070 共用 `.githooks/pre-commit`；T070 已於 U10a 先落、本 task 在其上放寬觸發）：①`tools/docsync/tests/test_hook_wiring.py` `HOOK`→四檔名冊（pre-commit／`.githooks/pre-push`／`.githooks-submodule/pre-push`／`.githooks/lib/scan-range.sh`）＋pre-push 兩支各三字面斷言＋lib 四種範圍推導字面斷言＋一正多反；`.githooks/pre-commit` selftest-docsync 觸發放寬為 `'^tools/docsync/\|^\.githooks/\|^\.githooks-submodule/'`（SEGMENTS 同批）②`tools/bootstrap.sh` `run_tool_test` 名冊改 `git -C "$ROOT" ls-files ':(glob)tools/*.py' ':(glob)deploy/*.py' | grep -v -e '^deploy/decrypt-secrets\.py$' -e '^deploy/secrets_common\.py$'` 推導（註明 `*` 跨 `/` 根因與兩排除理由；Day-1 分支獨立處理）＋`test_hook_wiring.py` bootstrap 面案（推導行字面／docsync 三段／閘數斷言／`vendored-check` 存在、刪一即紅；反例＝去 `:(glob)` 合成名冊多出 `assemble.py`→紅）；`bash tools/bootstrap.sh` 綠；DoD 等式形（不寫死支數）：推導所得名冊 ＝ `git -C "$ROOT" ls-files ':(glob)tools/*.py' ':(glob)deploy/*.py'` 去兩排除項之全集（003 前現值 10 支；本刀 `tools/msg-key-gate.py`／`tools/walkthrough-baseline.py` tracked 後＝12）＋Day-1 分支——處數由等式釘、不由人挑數（RL-0026）
- [x] T072 [P] [US6] BL-00041：`rust-api/server/src/handler/system_settings.rs` 「rev5 002 收刀坑」→「`rev5:002` 收刀坑」（test_kit.rs 已於 T008）；`tools/docsync/book.py` `SUB_SCAN` 粗篩加 `rev[45] [0-9]{3}` 形＋`BARE_PREV_KNIFE_NUM` 對子庫命中列精判（提及形豁免同外層）＋「子庫 pin 樹側尚未接」註解改現在式；`tools/docsync/tests/test_book_ids.py` 補子庫腿一正一反（合成命中列）；`python3 tools/docsync test`／`lint` 綠（★兩子庫 pin 樹重掃零 ERROR）
- [x] T073 [US6] ★主線任務（brainstorm Q4／Q7 已拍板）：`docs/arc42/decisions/ADR-000NN-quick-login-buttons-known-state.md`（序號落檔時取）＝ADR ④ 快速登入鈕已知態（保留＋記帳、棄案兩項、帳＝BL-00049 滯後卷、觸發＝RUNBOOK §16 prod 硬化拍板）；accepted＋`generate`
- [x] T074 [US6] 治理自證四組（工具＝`tools/fork-delta-lint.py`／`tools/msg-key-gate.py`／`tools/docsync`；每項還原後 `git status --porcelain`／`git -C base-web status --porcelain` 零差異＝RL-0005；結果記單元 commit 訊息）：①fork-delta 四腿（名冊內過 rc 0／名冊外攔／用途外攔 `(a)`→`(z)`／檔外攔→各 rc 1；反例一律打在 `base-web/src/store/modules/route/index.ts` 之 (a) 標記、當場還原）②跨端閘一正一反（T069 已做、復跑）③GT-12 `NON_GATE_TOOLS` 反例＋hook 接線守衛反例（暫刪 `.githooks/pre-push` 一字面／暫刪 `tools/bootstrap.sh` 推導行→`docsync test` 紅指名→還原）④BL-00041 子庫腿反例（於 `rust-api/server/src/handler/system_settings.rs` 註解合成 `rev5 002` 裸形→GT-05 紅→還原）

**Checkpoint（U10）**: 走查工具在場、hook 守衛擴至四檔、bootstrap 名冊機器推導、子庫腿接上；外層 commit（含 rust-api pin bump）

---

## Phase 9: Polish & Cross-Cutting Concerns（DoD 收攏）

- [ ] T075 CDP 對照走查（quickstart §0 snapshot→§1～§5 瀏覽器面＋§6 兩分頁 22080 vs 32080 五面截圖比對零差異→§8 清理（翻回 `single_session_default=off` 以 psql 直改並歸 NULL 審計欄、三表 DELETE、`session_id` NULL、三支 setval、redis 前綴 DEL）→`python3 tools/walkthrough-baseline.py diff` **rc 0**→`python3 tools/schema-gate.py check` 三閘綠）；走查腳本住 `tmp/`（import `tools/orchestration/cdp.mjs`）；結果記單元 report
- [ ] T076 全量閘綠（quickstart §7 逐條）：容器內 `cargo test --workspace -- --test-threads=1`＋`cargo build --release -p server`＋release 二進位 `/health`＋`pnpm typecheck`＋`python3 tools/fork-delta-lint.py`＋`python3 tools/msg-key-gate.py check`＋`python3 tools/wire-schema.py check`＋`python3 tools/entity-drift-gate.py check`＋`python3 tools/docsync test`／`check`／`lint`＋routes.md 16 列＋contract coverage 負向（抽一 case→紅→還原；加殭屍 case→紅→還原）；SC-001～SC-011 逐條對照（SC-012 收刀面子句於簿記 commit 後驗）＋US1～US6 驗收場景→測試案或演練紀錄對照表（函式名＋案序）
- [ ] T077 [P] 活書 as-built（feature branch 內、現在式；★不回灌 ADR）：`docs/arc42/05-building-block-view.md`（server 管線：auth／cache／throttle／captcha 四模組、handler 七檔、facade 八支）／`06-runtime-view.md` §6（會話狀態機、登入失敗節流兩情境；`rev5_blueprint` frontmatter「隨刀」→「承襲」）／`08-crosscutting-concepts.md` §8（§8.2 API 慣例三分碼＋msg 名冊跨端閘句自「不在本面、去處＝ADR-00017」改 `tools/msg-key-gate.py` as-built／§8.3 授權慣例驗證器句改真驗章 as-built（`jwt::verify_access`→denylist 四級降級；`dev_identity.rs` 已刪、release／debug 同形）／§8.4 fork-delta 接線現況＝四 ★ 軌道八用途 as-built）／`10-quality-requirements.md` §10.2（島 A～E 各一品質情境：刺激／回應／量測／守門；刪「目前零情境」句）／`11-risks-and-technical-debt.md`（本刀 by-design 已知態三則：redis 不開 AOF〔暴險受島 C status 權威封頂〕、快速登入鈕暴露 dev seed 帳密〔BL-00049〕、nginx 邊緣 `auth_limit` 先於後端〔004 域〕——現在式面之家、RL-0049）／`12-glossary.md`（auth 域詞：會話＝`rotation_chain`＝sid／憑證對／態三值／撤銷三型／grace 窗／節流三區／denylist 加速層 vs status 權威／idle 逾時；★「降級（基礎設施）」術語條與既有「降級輪廓」消歧）；C4-L2 拓樸不變零改（核對）；`generate`（`rev5-blueprint-map.md` 重算）
- [ ] T078 [P] 帳本預告與勘誤：`docs/ops/BACKLOG.md`——BL-00031 條文刪去「003 auth-session（`login_throttle_*` 對鍵）」段只留 004／007（工程判斷 4）；BL-00041 條文「rev5 001」誤記訂正（該條收刀 `backlog_done` 刪列、訂正記 commit 訊息）；收刀 `backlog_add` 三條新記預告（`/auth/error` demo 端點排程錨、`sys_user_role` `roles_of_user` DbErr 守衛錨、★`sys_user_role` `roles_of_user` 三帳只讀案未持 `test_kit::DB_SERIAL`＝真 DB 案行程級互斥的覆蓋缺口〔data-model §9；與前一條同函式、不同關切：那條要 DbErr 覆蓋、本條要並行互斥〕、回填錨＝`test_kit.rs` 之 `DB_SERIAL` doc 預告段——配號於簿記 commit 取）；一坑一檔落點 `docs/ops/LESSONS/LL-NNNNN-<slug>.md`（配號＝`docs/ops/LESSONS.md` 檔頭 next、索引由 generate 重產；候選：gate2 對 runtime sequence 不可逆敏感、`:(glob)` pathspec、argon2 0.6 拔 `OsRng`——實際踩到者才立）；`docs/ops/NOTES.md`「下一步」改 004 ip-trust-anchor 之預告文字（正式改於收刀簿記）；`python3 tools/docsync errata` 逐詞（`恰七鍵`／`恰六`／`六列`／`＝4`／`現行四條`／`不入 002 刀`／`不引 log crate`／`空表`／`1.2.0`／`指針章`／`NON_GATE_TOOLS`／`隨首個需走查的刀`／`003 接真 session`／`dev-only 查表`／`不在本面`）現在式面逐處改為現在式或指針、史料面不動、憲法命中只走 Amendment（T001 已含）；`docs/ops/NOTES.md`「下一步」→004 ip-trust-anchor（收刀簿記時）
- [ ] T079 perf 事件：pre-commit 全鏈實測（含 msg-key-gate 新段、雙 pin bump 觸發全段）≤45s → `docs/ops/events.jsonl` append `precommit_chain`；容器冷編時長記 commit 訊息（不入 DoD）

---

## 執行單元對映（承 research R15、依 US 交付面重切：`router.rs`／`contract.rs` 逐 US 加列而非尾端獨佔＝rev5 003 analyze 修正與 002 T029／T033 形；主線派發粒度、每單元一顆外層 commit；冒煙 token 取單元名形 `u<N>-<slug>-<4hex>`、不可取 `test`）

「允許檔案清單」欄＝該單元 agent **唯一可寫面**（逐字抄成 `ALLOWED_BLOCK` 常數；★＝註冊檔或連動釘值檔、漏列即 fix agent 撞牆）；**GENERATED_FILES 成員（`docs/generated/**`、`docs/arc42/ARCHITECTURE.md`、`docs/ops/LESSONS.md`、`tools/orchestration/_sk_rules.js`）一律不入清單、由主線六步序⑤ generate 帶入**；「限定式」項只准為還原式演練暫改、每項還原後 porcelain 零差異（RL-0005）。

| 單元 | 任務 | 允許檔案清單（起始） | 收尾產物 |
|---|---|---|---|
| U0 主線 | T001、T002 | `docs/arc42/decisions/ADR-00026-*.md`、`.specify/memory/constitution.md`（§III.2／§I.7／§I.2 釐清／版本與 log）、`README.md`（憲法版本鏡像行）、`tools/fork-delta-lint.py`（self_test 註解） | 憲法 1.3.0 獨立 commit＋generate |
| U1 | T003（主線）、T004～T008 | `rust-api/Cargo.toml`、`rust-api/server/Cargo.toml`、`rust-api/Cargo.lock`、`server/src/{config,state,main}.rs`、★`server/src/lib.rs`、`server/src/cache/mod.rs`（型別＋connect）、★`server/src/router.rs`（2 建構點）、★`server/src/handler/system_settings.rs`（2 建構點＋`SeedRestoreGuard` 搬出改 `use`）、`server/tests/common/mod.rs`、`server/src/model/facade/test_kit.rs` | ADR ②③ 外層 commit；rust-api commit→pin bump＋generate（STATE） |
| U2 | T009～T013 | `server/src/cache/mod.rs`、`server/src/auth/{jwt,mod}.rs`、`server/src/error.rs`、`server/src/model/{password,mod}.rs`、`server/src/request_context.rs`、★`server/src/lib.rs`、★`server/tests/contract.rs`（`#[ignore]` 回填點）、`server/src/model/facade/test_kit.rs`（真 redis＋簽發 helper） | rust-api commit→pin bump＋generate |
| U3 | T014～T019 | `server/src/model/facade/{sys_token,session_event,sys_login_attempt,sys_menu,sys_user,sys_role,mod}.rs`、★`server/tests/entity_access_lint.rs` | rust-api commit→pin bump＋generate |
| U4 | T020、T021 | `server/src/auth/{enforce,mod}.rs`、`server/src/auth/dev_identity.rs`（刪）、`server/src/lib.rs`、`server/src/obs.rs`、★`server/src/router.rs`、★`server/src/handler/system_settings.rs`、★`server/tests/contract.rs`、★`server/tests/common/mod.rs`（公開 API 簽發 helper、`real_seed_app` 帶 cache 形）、`server/src/model/facade/test_kit.rs`（helper 簽名微調落點） | rust-api commit→pin bump＋generate（ARCHITECTURE 例外註冊面由主線 generate） |
| U5（US1） | T022～T031 | ★`server/tests/contract.rs`、★`server/src/router.rs`、★`tools/docsync/tests/test_references.py`（真 repo 釘列）、`server/src/handler/auth/{mod,login,user_info}.rs`、★`server/src/handler/{mod,route}.rs`、`server/tests/wire_schema.rs`、`base-web/{.env,.env.test,.env.prod}`、`base-web/src/store/modules/route/index.ts` | 兩子庫 commit→外層一顆雙 pin bump＋generate（routes.md 9 列） |
| U6（US2） | T032～T036 | ★`server/tests/contract.rs`、★`server/src/router.rs`、★`tools/docsync/tests/test_references.py`、`server/src/handler/auth/{refresh,mod}.rs`、`server/src/model/facade/sys_token.rs`（若補） | rust-api commit→pin bump＋generate（routes.md 10 列） |
| U7（US3） | T037～T045 | ★`server/tests/contract.rs`、★`server/src/router.rs`、★`tools/docsync/tests/test_references.py`、`server/src/handler/auth/{login,refresh,logout,mod}.rs`、`server/src/model/facade/test_kit.rs`（守衛消費）、`base-web/src/service/api/rev6-auth.ts`、`base-web/src/layouts/modules/global-header/components/user-avatar.vue` | 兩子庫 commit→外層一顆雙 pin bump＋generate（routes.md 11 列） |
| U8（US4） | T046～T056 | ★`server/tests/contract.rs`、★`server/src/router.rs`、★`tools/docsync/tests/test_references.py`、★`server/src/lib.rs`、★`server/src/handler/mod.rs`、`server/src/throttle/mod.rs`、`server/src/captcha/mod.rs`、`server/src/handler/{captcha,auth/login}.rs`、`server/src/obs.rs`、`server/src/model/facade/test_kit.rs`（守衛消費）、`server/tests/wire_schema.rs`、`server/tests/fixtures/wire-schema.json`、`base-web/src/typings/api/rev6-auth.d.ts`、`base-web/src/service/api/rev6-auth.ts`、`base-web/src/store/modules/auth/index.ts`、`base-web/src/views/_builtin/login/modules/pwd-login.vue` | 兩子庫 commit→外層一顆雙 pin bump（wire-schema 兩側同批）＋generate（routes.md 12 列） |
| U9（US5） | T057～T069（T068 主線） | ★`server/tests/contract.rs`、★`server/tests/common/mod.rs`（四鍵承載案）、★`server/src/router.rs`、★`tools/docsync/tests/test_references.py`、`server/src/handler/auth/{alt_stub,mod}.rs`、`base-web/src/service/api/rev6-auth.ts`、`base-web/src/views/_builtin/login/modules/code-login.vue`、`base-web/src/views/_builtin/login/modules/register.vue`、`base-web/src/views/_builtin/login/modules/reset-pwd.vue`、`base-web/src/hooks/business/captcha.ts`、`base-web/src/typings/app.d.ts`、`base-web/src/locales/langs/{en-us,zh-cn,zh-tw}.ts`、`base-web/src/service/request/index.ts`、`tools/msg-key-gate.py`、`.githooks/pre-commit`、`tools/docsync/tests/test_hook_wiring.py`、`README.md`、`docs/ops/RUNBOOK.md` | ADR ⑤ 外層 commit；兩子庫 commit→外層一顆雙 pin bump（msg-key-gate 兩側同批）＋generate（routes.md 16 列） |
| U10a（US6、★U4 後 U5 前） | T070 | `tools/walkthrough-baseline.py`、`tools/docsync/gates.py`、`tools/docsync/tests/test_gates.py`、`.githooks/pre-commit`（`for` 名冊）、`README.md`、`docs/ops/RUNBOOK.md`（§9c 實文、§12 兩處、檔頭句）、`CLAUDE.md`（§7 末句） | 外層工具 commit＋generate |
| U10（US6） | T071～T074（T073 主線） | `tools/walkthrough-baseline.py`、`tools/docsync/{gates,book}.py`、`tools/docsync/tests/{test_gates,test_hook_wiring,test_book_ids}.py`、`tools/bootstrap.sh`、`.githooks/pre-commit`、★`.githooks/pre-push`、★`.githooks-submodule/pre-push`、★`.githooks/lib/scan-range.sh`（T071① 斷言標的兼 T074③ 反例落點）、`README.md`、`docs/ops/RUNBOOK.md`、`CLAUDE.md`（§7 末句現在式）、`rust-api/server/src/handler/system_settings.rs`（BL-00041 一行；兼 T074④ 反例落點）、限定式：`base-web/src/store/modules/route/index.ts`（T074① 四腿反例、當場還原） | ADR ④ 外層 commit；rust-api commit→pin bump＋外層工具 commit＋generate |
| U11 收攏 | T075～T079 | `tmp/`（走查腳本、基準檔）、`docs/arc42/{05,06,08,10,12}-*.md`、`docs/ops/BACKLOG.md`、`docs/ops/LESSONS/`（目錄、一坑一檔）、`docs/ops/NOTES.md`、`docs/ops/events.jsonl`、限定式：`rust-api/server/tests/contract.rs`（T076 coverage 閘負向演練、還原後 `git -C rust-api status --porcelain` 零差異） | 外層 commit＋generate；final holistic review 輸入 |

★**派發序**（依相依，非依編號）：U0→U1→U2→U3→U4→**U10a**（T070 走查工具、FR-036 硬前置）→U5→U6→U7→U8→U9→U10→U11；★U10 硬依 U9（T074② 復跑跨端閘需 `tools/msg-key-gate.py` 已在；且 U9／U10 共用 `.githooks/pre-commit`／`README.md`／`docs/ops/RUNBOOK.md` 三檔、不可並發）。
★**單元序不可並發的共用檔**：`router.rs`／`contract.rs`／`test_references.py`（U5～U9 逐 phase 加列並 bump 同一 `ROUTES_COUNT` 與釘值列）、`login.rs`（U5 ③～⑪／U7 ⑨／U8 ①②遞進）、`handler/auth/mod.rs`（宣告行逐單元遞進）、`rev6-auth.ts`（U7／U8／U9 分批補 wrapper）——⇒ US 的「獨立可驗收」成立於交付面、不成立於單元併發面。
★**每單元邊界主線動作**（六步序、不入 agent 清單）：①復核 report（逐項 grep、`errata` 復掃）→②load-bearing 自驗（容器內 rc＋`docsync lint`）→③落帳（BACKLOG／LESSONS／tasks 勾選／ADR）→④子庫 commit →⑤`git add <子庫>`→`generate`→`git add` 生成物→⑥外層 commit（pin bump）→ 派下一支前逐條問「它 import／呼叫／宣告的東西存在嗎」。

## Dependencies & Execution Order

- **Phase 1**：T001（★硬閘）→T002；T001 需 user 親決。
- **Phase 2**：U1（T003→T004→{T005、T006 可分派}→T007→T008〔★待 T006 之五欄與 `system_settings.rs` 建構點落、非與 T006 併行〕）→U2（{T009、T010、T012、T013 可分派}→T011；★T009 動 `lib.rs`（已由 T006 註冊、只補本體）、T010 動 `auth/mod.rs` 註冊行、T012 動 `model/mod.rs` 註冊行——三處互不相交、仍於 U2 內序列落地；T010 所需 `cache::connect` 已於 U1 之 T006 落、與 T009 無相依）→U3（T014～T018 可分派、共用 `facade/mod.rs` 註冊行；T019 收攏）→U4（T020→T021）。
- **Phase 3～7**：皆依 Phase 2 與 U10a（走查工具在場）；實作序照 US1→US2→US3→US4→US5（`login.rs`／`router.rs`／`contract.rs`／`test_references.py`／`handler/auth/mod.rs`／`rev6-auth.ts` 同檔遞進、不可並行）。US1 另依 T001（base-web 既有檔硬閘）。U9 內序：T061→{T062、T063}（wrapper 先於消費者）；T064→T065→T067（型節→兩語＋zh-tw→跨端閘右源齊後才落閘）；T057～T060 rust 側可與前端側分派、但 T060 之四鍵承載案待 T059。
- **Phase 8**：T070 獨立成 U10a、於 U4 後 U5 前派發（FR-036；`.githooks/pre-commit` 之 `for` 名冊先加列）；U10 內 T071／T072 檔域不相交可分派（T071 在 T070 已落的 pre-commit 上放寬觸發）；T073 主線；T074 待 T070～T072；U10 硬依 U9（跨端閘反例）與 T001（fork-delta 四腿需真標記）。
- **Phase 9**：依全部；T075 之 `schema-gate check` 必在清理與 diff rc 0 之後；T076 待 T075；T077／T078 可分派；T079 末。
- 阻斷型：T004 容器內 build 紅（features 或 MSRV）＝blocked 升主線；T021 release build 紅＝blocked；T054 需 base-web 容器在跑；T060 之 7777 承載案需 `real_seed_app` 帶 cache（redis 容器在跑）；T065 譯文只認 contracts/msg-keys.md；任一單元需動允許檔案清單外檔案＝依防呆④分值升級、絕不擅改。

## Parallel Opportunities（逐 US；[P]＝檔域不相交可分派、cargo 序列）

- **U1**：T005／T006 可分派；T008 待 T006。**U2**：T009／T010／T012／T013 四支主體檔可分派、T011 序列。**U3**：T014～T018 五支 facade 主體檔可分派（`facade/mod.rs` 註冊行由 T019 收攏）。**U4**：T020→T021 序列。
- **US1（U5）**：T022／T023（測試骨架）可分派；T025／T026 兩 handler 可分派；T029（`.env`）與 rust 側可分派；`login.rs`／`handler/auth/mod.rs`／`router.rs`／`contract.rs`／`test_references.py` 由單一 implementer 序列收邊。
- **US2（U6）**：T032／T033 可分派；T034→T035→T036 序列。**US3（U7）**：T037／T038 可分派；T039／T040／T041／T043 主體檔可分派（`handler/auth/mod.rs` 由 T041 加行）；T044 待 T043；T042 收攏。
- **US4（U8）**：T046／T047 可分派；T048／T049／T050 三支主體檔可分派（`lib.rs`／`handler/mod.rs` 註冊行序列化）；T051 待 T048、T052 待 T048、T053 待 T050；T054 與 rust 側可分派；T055 待 T054。
- **US5（U9）**：T057／T058 可分派；T059→T060 序列；前端側 T061→{T062、T063}、T064→T065→T066；T067 待 T065（右源齊）；T068 主線。
- **U10a**：T070 單獨一支。**U10**：T071／T072 可分派；T074 末。**U11**：T077／T078 可分派；T075→T076→T079 序列。

## Parallel Example: User Story 1

```text
# facade 已於 U3 就位；U5 內可分派（檔域不相交；cargo 序列）
Task: "T025 user_info handler in rust-api/server/src/handler/auth/user_info.rs"
Task: "T026 route handler in rust-api/server/src/handler/route.rs"
Task: "T029 .env 四行 ADAPT（T001 後）in base-web/.env、.env.test、.env.prod"
# login.rs／handler/auth/mod.rs／router.rs／contract.rs 由單一 implementer 序列收邊
```

## Implementation Strategy

- **MVP**＝Phase 1＋Phase 2（U1～U4）＋US1（U5）：瀏覽器真登入看見角色化側邊欄＝rev6 第一次端到端可見。
- 增量：US2（續期）→US3（撤銷）→US4（節流＋captcha）→US5（stub＋i18n＋跨端閘）→US6（治理）→Polish；每單元收尾六步序；每單元 review／fix 烤入 RULES scope 塊（RULES-VERSION 不變＝89ec0586d6a9）。
- 收刀（★不在本清單）：final holistic review → `superpowers:finishing-a-development-branch`（push／merge 需 user 同意）→ 收刀簿記三步（`feature_close` window 3：`adrs` 五筆、`backlog_done` BL-00026／00030／00037／00041、`backlog_add` BL-00043～00049 七條＋新配兩條；NOTES 下一步→004；generate）→ `close_bookkeeping` perf 第四步。

## Notes

- [P]＝檔域不相交可分派；★cargo 執行一律序列。
- 測試先確認紅再實作；每 task 或邏輯群組後 commit（子庫 commit→外層 bump pin）。
- 任一 checkpoint 皆可停下獨立驗收該 US。
- 避免：跨 US 破壞獨立性、同檔並行、在 T001 accepted 前動 base-web 既有檔、單側 pin bump 讓兩側閘分叉。
