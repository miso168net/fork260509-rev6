# Tasks: 002 系統設定讀寫（server 進場首刀縱切管線）

**Input**: Design documents from `/specs/002-system-settings/`

**Prerequisites**: plan.md、spec.md（US1～US6、clarify Q1～Q5）、research.md（R1 依賴表、R2 對應碼、R3 差異點、R12 單元切法、R13 反例）、data-model.md、contracts/wire-settings.md、contracts/code-gates.md、quickstart.md；
憲法 1.1.0（零 Amendment）；ADR 六筆待立（序號自 ADR-00013 起於落檔時取）。

**Tests**: 本 repo TDD＝CLAUDE.md §2 紀律、**非可選**——每實作 task 內先紅後綠；測試層對照（research R7）：「契約測試」＝`server/tests/contract.rs` per-route 覆蓋閘（oneshot 免 DB）；
registry 紅綠矩陣／三態五案／授權矩陣／型別不一致＝真 DB integration（handler `mod tests`、RAII 還原守衛）；工具之先紅＝自帶 `test`＋一正一反；判準本就正確的案「案綠→打壞判準→案紅→還原」才算驗證。

**Organization**: 依 user story 分 phase（US1～US6）；本刀為縱切地基刀、story 間有天然順序相依（見 Dependencies）；**執行單元對映**（research R12）另列於文末，主線編排以單元為 Workflow 派發粒度、每單元一顆外層 commit（單元收尾六步序＝CLAUDE.md §2）。

**紀律烤入**（一切任務隱含、不逐條重複）：★實作前先讀 R2 清單對應之 rev5 碼（`../fork260509-rev5/rust-api/` 凍結 worktree、唯讀、絕不寫入）；高度參照、重打字消化、註解一律 rev6 語境重寫（rev5 出處帶 `rev5:`）；
R3 十五筆差異點與 rev5 research R3 十三筆已翻案行為皆不得帶回；rust build／test 一律容器內、`--test-threads=1` serial（host 無 toolchain）；兩段式 commit（`git -C <子庫>` 內 commit → 單元邊界回外層 `git add <子庫>` bump pin）；
★絕不 push／merge（finishing 前硬禁令、本清單不含此類任務）；書面產物與註解一律 zh-TW；`/mnt/d` 跑過 compose 後同 shell 先重新 `cd`；隨遷工具拷入後先 `python3 tools/docsync lint`（GT-05 五形）。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可平行（不同檔案、無未完成相依；rust 執行一律序列、[P] 只指檔域不相交可分派）
- **[Story]**: 所屬 user story（US1～US6）；Setup／Foundational／Polish 無標籤

## Phase 1: Setup（主線直改＋前置體檢；首個 Workflow 派發前）

**Purpose**: 名詞段先落＝後續 script 以新 RULES-VERSION 組裝；環境就緒

- [ ] T001 ★主線直改（不入 agent 單元）：`docs/ops/RULES.md` 名詞段加「碼面閘／治理閘」定義（字面＝contracts/code-gates.md §3）→ `python3 tools/docsync generate`（`tools/orchestration/_sk_rules.js` 重產、RULES-VERSION bump）→ `python3 tools/docsync test`／`lint` 綠 → 外層 commit；此後一切 Workflow script 以新版 `python3 tools/docsync rules emit --scope <…>` 組裝
- [ ] T002 前置體檢：`bash tools/bootstrap.sh` 綠；`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait postgres redis base-web` 起（rust-api 於 U1 前起不來屬預期）；`rev6-admin-rust-api:dev` 映像在位、容器內 `cargo --version`＝1.96.1、`cargo fmt --version` 可用；base-web 容器 `pnpm typecheck` 基線綠

---

## Phase 2: Foundational（阻斷性前置：U0 治理組合拳 → U1 server 基座 → U2 授權與身分）

**Purpose**: 未完成前不得開任何 user story——碼面閘在場（U0）、server 可起且四條 route 骨架與覆蓋閘在場（U1）、Policy 路由可判定（U2）

**⚠️ CRITICAL**: U0 純治理零 rust 碼；U1 起每單元收尾容器內 `cargo fmt --all --check`＋`cargo test`；T003 首跑對 001 承襲 17 檔若紅＝blocked 升 user

### U0 治理組合拳（contracts/code-gates.md §1～§3、§6）

- [ ] T003 `tools/rust-fmt-gate.py` 隨遷（自 `../fork260509-rev5/tools/rust-fmt-gate.py`、427 行）：座標常數同名核對（compose 兩檔、`rust-api` 服務名）、註解與字串四型失效引用 rev6 化（`rev5:B-112`／`rev5:ADR 0057` 前綴）；`python3 tools/rust-fmt-gate.py test` 綠；★對現庫首跑 `check`＝rc 0（若對 001 承襲檔紅→status blocked、不得自行 fmt）
- [ ] T004 [P] `tools/wire-schema.py` 隨遷（650 行）：glob 零改、TSJS 0.67.4＋`--strictNullChecks` 照舊、快照路徑 `rust-api/server/tests/fixtures/wire-schema.json`、rev6 化註解；`python3 tools/wire-schema.py test` 綠；`check --staged-gate` 於零 typings 變動＝具名跳過 rc 0
- [ ] T005 [P] `tools/fork-delta-lint.py` 隨遷（1108 行）：token `rev5-inline`→`rev6-inline`、源倉路徑同名、註解 rev6 化；★結構斷言改形（contracts/code-gates.md §1.3、research R10）：§III.2 ★段零列時必命中哨兵句「（空表——尚無 ★ 軌道；首列隨首刀 Amendment 落入。）」、否則 ≥1 列；self-test 加「零列＋無哨兵句＝紅」案；對現 base-web（僅 `x_fork.branch-origin.md` 新檔、非掃描面）實跑 rc 0
- [ ] T006 `.githooks/pre-commit` 六處（contracts/code-gates.md §2）：①自測迴圈 `for t in …` 加三支 ②rust-fmt 段（staged 含 `rust-api` 或該工具）③wire-schema 段（staged 含 `base-web`→`check --staged-gate`）④fork-delta 段（staged 含 `base-web`、該工具或 `.specify/memory/constitution.md`）⑤entity-drift 快照缺席分支改 rc 2＋提示「跑 `python3 tools/docsync refresh` 照相」（BL-00010）⑥檔頭第 2 行 schema-frozen 觸發面補 `schema-definition.md`；雙錨 45／90 與 `pc_run` 並行形不動
- [ ] T007 [P] `docs/ops/RUNBOOK.md` §12：末段碼面閘散文改「碼面閘表」（`| 工具檔 | 守什麼 | 觸發時機（含環境缺席語意） | 根據 ADR |`；五列＋msg key 跨端閘延後註記列；根據 ADR 欄暫寫 ADR 題名、序號於 T041 落檔後回填）；工具鏈速查表加 `rust-fmt-gate.py check｜test`／`wire-schema.py extract｜check｜test`／`fork-delta-lint.py` 三列（需運行中 stack 欄如實）
- [ ] T008 `tools/docsync/gates.py` GT-12 新腿（contracts/code-gates.md §3）：`NON_GATE_TOOLS = ("tools/wf-watchdog.py",)` 常數；S_tools＝`tools/` 頂層 tracked `*.py` − 常數；S_table＝RUNBOOK 碼面閘表首欄反引號 `tools/…py` 集；不等＝ERROR 雙向指名、表缺席或零列＝ERROR；docstring `face=` 加「RUNBOOK 碼面閘表」；`tools/docsync/tests/test_gates.py` 一正一反（合成五列＝綠；刪一列／加幽靈列＝紅指名）先紅後綠；`python3 tools/docsync test`／`generate`（GATES.md GT-12 列重產）／`lint` 綠
- [ ] T009 [P] 接線對賬（GT-09）：`README.md` 樹 `tools/` 下加三支一行各一；`tools/bootstrap.sh` `run_tool_test` 加三支；`git update-index --chmod=+x` 三支（drvfs）
- [ ] T010 失準修單：`python3 tools/docsync errata schema-frozen` 全 repo 枚舉→逐處處置（現知 `.githooks/pre-commit` 第 2 行＝T006⑥、`README.md` 守門句補 `schema-definition.md`；`docs/process/P-E1-boundary.md`／`P-C4-E3-materials-boundary.md` 只列段名、掃後判「非失準」即不動並記 commit 訊息）；復掃零殘留
- [ ] T011 U0 自證與演練（US6 場景 1～4 之機器面；每項還原後 `git status --porcelain` 零差異——RL-0005）：①三支 self-test 綠＋各一次打壞判準演練（rust-fmt 以樁模擬未格式化→rc 1；wire-schema 以暫存快照篡改→rc 2；fork-delta 以 `--constitution` 指向去哨兵句副本→rc 2）②hook 面演練：移走 `docs/ops/reference-src/schema-snapshot.json`→`git add`→commit 被 ⑤ 擋且訊息含 refresh 提示→`git checkout HEAD -- <快照>`（LL-00003）③GT-12 腿：暫刪表一列→`lint` 紅指名→還原④errata 復掃零殘留；結果逐項記 U0 外層 commit 訊息；pre-commit 全鏈實測記時（perf 事件 `precommit_chain` 隨本 commit）

**Checkpoint（U0）**: 三支碼面閘在場並自證、hook 六處落地、名冊機器對賬綠、lint 零紅、治理閘數 12

### U1 server 基座（data-model §4／§6、contracts/wire-settings.md §3、contracts/code-gates.md §4／§5）

- [ ] T012 `rust-api/Cargo.toml`：members += `"server"`；`[workspace.dependencies]` 加 R1 十支（axum 0.8.9／serde 1.0.229／serde_json 1.0.151／tracing 0.1.44／tracing-subscriber 0.3.23／tower 0.5.3／metrics 0.24.6／metrics-exporter-prometheus 0.18.3 `default-features = false`／axum-prometheus 0.10.1／jsonschema 0.53.0 `default-features = false`）；`rust-api/server/Cargo.toml`（依賴子集、features 逐項註解重寫、dev-deps tower＋jsonschema）＋`server/src/lib.rs` 全模組 `mod` 宣告骨架與各模組空殼檔（`//!` 佔位）＋最小 `main.rs`；容器內 `cargo build --workspace` 綠、`Cargo.lock` 入版控（新增套件清單記 commit 訊息）；`cargo fmt --all --check` 綠
- [ ] T013 `rust-api/server/src/envelope.rs`（`Res` 三欄宣告序＋2^53 fail-loud 守衛＋`serialize_i64_as_string`；不含 PageRes）＋`error.rs`（13 碼常量 mod 全列；AppError 六變體＝data-model §6；★`MSG_KEYS` 名冊常數恰七鍵）＋in-crate 碼映射與名冊測試（先紅後綠）
- [ ] T014 [P] `rust-api/server/src/config.rs`（`APP_DATABASE_URL[_FILE]` 讀取、CHANGE-ME 拒啟）＋`state.rs`（`AppState{db, enforcer: Arc<RwLock<Enforcer>>}` 恰兩欄）
- [ ] T015 [P] `rust-api/server/src/obs.rs`（recorder＋render＋axum-prometheus layer——research R6）
- [ ] T016 `rust-api/server/src/router.rs`（RouteDef 六欄／Protection 三態／`ROUTES` 起手＝`/health`＋`/metrics` 兩條／build 迭代註冊；★`fallback` 與 `method_not_allowed_fallback` 掛同一函式→HTTP 404＋`4040` 信封——clarify Q4；字面形守 data-model §4 機器契約）＋`handler/mod.rs`
- [ ] T017 `rust-api/server/src/main.rs`＋`lib.rs` boot 鏈（config→db→init_enforcer 佔位→router build→`into_make_service_with_connect_info` serve；tracing-subscriber json）；容器內 build 綠、watchexec 起得來
- [ ] T018 `rust-api/server/tests/`：`common/mod.rs`（app 建構、send 助手、strip 引擎共用）＋`health.rs`（oneshot 基礎形）＋`contract.rs`（case registry＋`ROUTES` 雙向覆蓋閘＋health／metrics 兩 case＋★fallback 兩案獨立測試：未註冊路徑、`POST /health` 方法不符皆 4040 信封＋★msg 名冊雙向斷言骨架）＋`entity_access_lint.rs`（handler 零 `entity::`、排除制掃描面＋結構斷言——沿 rev5 終態形）＋`entity_behavior_lint.rs`（BL-00008：等式形站點數＋空體判定＋合成正例；contracts/code-gates.md §5）；容器內 `cargo test --workspace -- --test-threads=1` 綠
- [ ] T019 `tools/docsync/references.py`：`parse_router_routes`＋`gen_reference_routes`（contracts/code-gates.md §4；窄假設偏離即 raise）；`GENERATED_FILES` 14→15（`docs/generated/reference/routes.md`）；`README.md` `docs/generated/` 成員行加 `routes`；`tools/docsync/tests/test_references.py` 一正一反先紅後綠；`python3 tools/docsync test`／`generate`／`check`／`lint` 綠（GT-09 成員腿、GT-01）
- [ ] T020 七件起得齊驗證（FR-001）：`docker compose … up -d --wait` 零非零退出、`rust-api` healthy；`curl http://127.0.0.1:32079/health`＝ok、`/metrics` 有 exposition；`python3 tools/rust-fmt-gate.py check` rc 0（容器在跑、真實跑）；rust-api worktree commit＋外層 pin bump（單元邊界）

**Checkpoint（U1）**: 管線骨架可跑、四條 route 之二在場、覆蓋閘與 fallback 形固定、routes 真表首算

### U2 授權與身分（data-model §5、spec FR-013～FR-016）

- [ ] T021 `rust-api/server/src/auth/enforce.rs`（`MODEL_CONF`／`init_enforcer`（vendored adapter、boot 一次載入即終態）／`enforce_role_path_method` 單一純函式進入點／`require_policy(path, method)` DB-fresh 走 `roles_of_user`／★`no_escalation_check` 空掛點簽章預留 async 與 db、本刀恆 Ok）＋`auth/mod.rs`；純函式單元測先紅後綠
- [ ] T022 [P] `rust-api/server/src/auth/dev_identity.rs`（`#[cfg(debug_assertions)]` 查表 dev-super→1／dev-admin→2／dev-user→3、`Authorization: Bearer <token>` 剝前綴 trim；`Identity{uid, user_name}` 注入形；缺席／非 Bearer／不在表→`8888`）；release 建置驗證器缺席＝一律 8888（測試以 cfg 反向斷言）
- [ ] T023 [P] `rust-api/server/src/request_context.rs`（seam 介面位空殼）＋`model/mod.rs`＋`model/facade/mod.rs`＋`model/facade/sys_user_role.rs`（`roles_of_user`：`sys_user_role` join `sys_role`、`deleted_at IS NULL`＋`status=1` 兩濾網）；純函式／facade 測先紅後綠
- [ ] T024 `enforce_mw` 掛 Policy 路由（router build 依 Protection 分派；Public 不掛）＋`contract.rs` 補 Policy 路由通則 case 形（未認證→8888 免 DB oneshot；★對未認證先回 8888 而非 405）；容器內 cargo test 綠；worktree commit＋pin bump（單元邊界）

**Checkpoint（U2）**: 授權判定單點在場、測試態身分（dev-only）可用、Policy 路由未認證 8888——user story 解鎖

---

## Phase 3: User Story 1 - 讀端管線全通（Priority: P1）🎯 MVP

**Goal**: R_SUPER 一次讀取 16 鍵全集，七環管線每環有真實流量；契約快照裁判與覆蓋閘對讀端成立

**Independent Test**: quickstart §1（dev-super 讀回 16 鍵與 seed 定稿逐鍵全等、升冪、description NULL 缺席）＋§2 越權 403

### Implementation for User Story 1

- [ ] T025 [P] [US1] `base-web/src/typings/api/rev6-settings.d.ts`（declaration merging 併入 `Api.SystemManage`：`SystemSetting` 四欄 description?: string、`UpdateSystemSettingReq` 三欄 description?: string | null——contracts/wire-settings.md §5；檔頭 `// [rev6-inline BASE-WEB-ADAPT+ 002-system-settings] …` 標記）；`python3 tools/fork-delta-lint.py` rc 0；base-web worktree commit
- [ ] T026 [US1] `python3 tools/wire-schema.py extract`（stack 在跑）→`rust-api/server/tests/fixtures/wire-schema.json` 首抽落地＋`check` 綠；受審 definitions 含 `Api.SystemManage.SystemSetting`（description 不含 null）與 `UpdateSystemSettingReq`（description 呈 `["null","string"]`）
- [ ] T027 [P] [US1] `rust-api/server/src/validation.rs`：registry 16 鍵 const（data-model §3 原值）＋`is_known_type`＋`declared_type(key)`＋★`check_type_consistency(key, db_type)`（clarify Q1：不一致→Internal 5000）＋`validate(key, value)→canonical`（number：trim→parse i64→界內→to_string；enum：精確成員、大小寫敏感）；TDD 紅綠矩陣（每型合法／非法／未知鍵／未知型／不一致）
- [ ] T028 [US1] `rust-api/server/src/model/facade/system_settings.rs`：`find_all`（`deleted_at IS NULL`、`ORDER BY setting_key`）；facade 測先紅後綠
- [ ] T029 [US1] `rust-api/server/src/handler/system_settings.rs`：`SettingItem`（camelCase、審計欄不上 wire、description `skip_serializing_if` None——clarify Q2）＋`get_system_settings`（Model→DTO 映射帶兩守衛：認識集＋一致性→5000 整支 fail-loud、不跳列）＋`router.rs` 掛 `GET /systemManage/getSystemSettings`（Policy）＋`contract.rs` 補 get-system-settings case（含未認證 8888 免 DB＋不認識 header（apifoxToken）回包全等斷言——憲法 §II #1）＋`tests/wire_schema.rs`（jsonschema 0.53.0 對快照 `Api.SystemManage.SystemSetting` 裁判 SettingItem 序列化輸出；★若 0.53 API 與 rev5 藍本不同照新 API 寫；null 判定與 rev5 實證不同→blocked）
- [ ] T030 [US1] handler `mod tests` 真 DB integration（real_app oneshot、RAII 還原守衛）：dev-super 讀回 16 鍵與 seed 定稿全等含升冪與 NULL 缺席（SC-001）／dev-admin→5003／無標頭→8888／★植入型別不一致列（UPDATE setting_type 後還原）→讀端 5000 不跳列（US3 場景 5 讀端半條）；容器內 cargo test 綠
- [ ] T031 [US1] `base-web/src/service/api/rev6-settings.ts`：`fetchGetSystemSettings()`（直接路徑 import `../request`、不經 barrel；檔頭 `// [rev6-inline BASE-WEB-WRAPPER+ 002-system-settings] …`）；容器內 `pnpm typecheck` 綠；fork-delta rc 0；base-web worktree commit＋兩子庫 pin bump（單元邊界）；quickstart §1／§2 走查記 commit 訊息

**Checkpoint**: US1 獨立可驗——rev6 第一條管線存在（MVP）

---

## Phase 4: User Story 2 - 寫端合法路徑（Priority: P2）

**Goal**: 單鍵更新經 registry 驗證＋正規化落庫、審計欄成對、回包 `data:null`

**Independent Test**: quickstart §3 首例（`"+10"`→`"10"`、回讀一致、updated_at／by 非空）＋同值再寫審計欄仍更新

### Implementation for User Story 2

- [ ] T032 [US2] facade `system_settings.rs` 補：`find_by_key`（`deleted_at IS NULL`、軟刪視同 miss→`Ok(None)`）＋`build_update_active_model`（純測 seam、now 注入、§I.6 updated_at／by 成對 Set、description 三態 Set 或不動）＋`update_by_key`（單鍵原子 UPDATE、無 op-log）；純函式測先紅後綠
- [ ] T033 [US2] handler 補：`UpdateSystemSettingReq`（三態承載 `Option<Option<String>>`＋default＋自訂 `deserialize_with`——rev5:L-009；settingKey／settingValue 寬鬆承載、缺席或型別不符由 handler 判 2222；JSON 反序列化失敗以自訂 rejection 落 2222 信封 HTTP 200）＋`update_system_setting`（解析→授權→一致性守衛→registry 驗證→facade→`Res::ok(())` ★data:null——clarify Q3；未知鍵→2222 notFound）＋`router.rs` 掛 `POST /systemManage/updateSystemSetting`（Policy）＋`contract.rs` 補 update-system-setting case（含未認證 8888、★`GET` 打此路徑→4040 信封案）＋`wire_schema.rs` 補 UpdateReq 裁判
- [ ] T034 [US2] integration（handler mod tests）：number `"+10"`／`" 7 "`／`"007"`→canonical 落庫＋enum 更新＋審計欄成對（operator uid＝1）＋回讀一致＋★同值再寫 updated_at 前進（SC-002、US2 場景 1～4）＋★FR-016 斷言：合法更新前後 `sys_operation_log`／`sys_access_log` 列數不變（本刀零稽核寫入）；容器內 cargo test 綠
- [ ] T035 [US2] service `rev6-settings.ts` 補 `fetchUpdateSystemSetting(req): request<null>`（型別完備）；`pnpm typecheck` 綠；fork-delta rc 0；worktree commit＋pin bump（單元邊界）；quickstart §3 首例走查記 commit 訊息

---

## Phase 5: User Story 3 - 寫端驗證失敗路徑（Priority: P2）

**Goal**: 非法寫入一律拒收零寫入、碼與 msg key 正確、未知型與不一致 fail-loud

**Independent Test**: quickstart §3 中段四例（超範圍／大小寫／未知鍵／壞形）＋回讀原值保留

### Implementation for User Story 3

- [ ] T036 [US3] integration 失敗矩陣（handler mod tests）：型別不符／小數／溢位／超範圍／enum 外含大小寫→2222 invalidValue；未知鍵→2222 notFound；settingKey 或 settingValue 缺席／型別非 string／JSON 壞形→2222 invalidValue；庫中手植未知 setting_type 列→讀端 find_all 與寫端 update 觸及**兩案皆** 5000（測試內 SQL 植入後 RAII 還原）；★已知鍵型別不一致寫端案→5000；全案回讀斷言原值保留零寫入（SC-003）＋★FR-016：非法路徑亦斷言兩 log 表列數不變；msg 名冊雙向斷言此時可完整成立（七鍵皆有發出點）；容器內 cargo test 綠；worktree commit＋pin bump

---

## Phase 6: User Story 4 - 越權與身分（Priority: P2）

**Goal**: 「有鈕無政策」組合正確拒絕、拒絕語意 ADR 定死、角色軟刪停用視同無角色

**Independent Test**: quickstart §2 三身分×兩端點矩陣全數符合 ADR 定稿

### Implementation for User Story 4

- [ ] T037 [US4] ★主線任務（不入 agent 執行單元）：`docs/arc42/decisions/ADR-000NN-authz-denial-semantics-and-no-escalation-seam.md`（ADR ②：5003＋HTTP 403＋`msg` 純 key `system.forbidden`、不揭露政策明細與角色集；掛點簽章 `no_escalation_check(db, actor_uid, path, method) -> Result<(), AppError>` 本刀恆 Ok、enforce 進入點唯一呼叫；provenance 引 rev5:ADR 0022＋brainstorm §4；翻案觸發器＝受眾邊界重評）→ accepted＋`python3 tools/docsync generate` 同 commit
- [ ] T038 [US4] integration 授權矩陣（handler mod tests）：dev-admin 讀／寫→5003、dev-user 讀／寫→5003、無標頭讀／寫→8888、非 Bearer 形→8888、token 不在表→8888（SC-004）＋dev-admin 寫被拒後 dev-super 回讀該鍵 settingValue 與 updated_at 皆未變＋★角色軟刪／停用案（測試內 UPDATE sys_role.deleted_at 或 status 後還原→5003）＋no-escalation 掛點可觀察形（測試替身使掛點回 Err→請求被 5003 擋＝掛點在判定鏈上）；容器內 cargo test 綠；worktree commit＋pin bump

---

## Phase 7: User Story 5 - 部分更新三態語意（Priority: P3）

**Goal**: envelope 級三態在真實寫端具象驗證、ADR 定形

**Independent Test**: quickstart §3 末三例（null 清空／空字串設值／settingValue null 拒收）＋缺席不動

### Implementation for User Story 5

- [ ] T039 [US5] ★主線任務：`docs/arc42/decisions/ADR-000NN-partial-update-tristate-envelope-convention.md`（ADR ①：data-model §8 條文轉錄；射程＝部分更新 body；provenance 引 rev5:ADR 0023；翻案觸發器＝create 語意要鎖時新 ADR）→ accepted＋generate 同 commit；data-model §8 加「權威＝該 ADR」指針句
- [ ] T040 [US5] 三態 deserialize 純函式測（缺席／null／值三形×兩欄）＋integration 五案：description 缺席不動／null 落 NULL／`""` 落空字串／設值生效、settingValue null→2222（SC-005、US5 場景 1～4）；容器內 cargo test 綠；worktree commit＋pin bump

---

## Phase 8: User Story 6 - 治理進場與帳本落帳（Priority: P4）

**Goal**: U0 產物已自證（T011）；餘＝ADR 四筆、BACKLOG、活書 as-built、勘誤

**Independent Test**: ADR 六筆 accepted 且 DECISIONS-INDEX 列全；BACKLOG 兩條新記在案；lint 全綠；errata 復掃零殘留

### Implementation for User Story 6

- [ ] T041 [US6] ★主線任務：ADR ③碼面閘名冊承載於 RUNBOOK §12＋GT-12 腿（BL-00011；含非閘名冊常數形與 ≥8 支翻案觸發器）、④msg key 跨端契約延前端 i18n 刀＋後端側閉環（brainstorm Q4）、⑤entity 漂移段快照缺席即紅（BL-00010）、⑥容器依賴型碼面閘環境缺席＝具名跳過／工具缺席 fail-loud（clarify Q5、承 rev5:ADR 0057 決定 3）——四檔 `docs/arc42/decisions/ADR-000NN-*.md` accepted＋generate；回填 T007 表「根據 ADR」欄序號
- [ ] T042 [P] [US6] `docs/ops/BACKLOG.md` append 兩條（取檔頭 next 配號）：msg key 跨端閘（後端名冊 ⊆ 前端字典；觸發＝首個接 i18n 的前端刀）；registry 跨鍵不變式（min≤max、captcha_after≤max_fails；觸發＝004 ip-trust-anchor／007 user-password-admin 消費側進場）；BL-00008／00010／00011 於收刀事件 `backlog_done`（簿記 commit 刪列、本 task 只預告）
- [ ] T043 [P] [US6] 活書 as-built（feature branch 內、現在式）：`docs/arc42/05-building-block-view.md` §5.1 樹列 server crate＋§5.2 server 管線句改現在式＋frontmatter `rev5_blueprint` §5「隨刀」→「承襲」；`docs/arc42/08-crosscutting-concepts.md` §8.2（契約機器化＋三態＝ADR ① 指針、msg 名冊後端閉環）／§8.3（拒絕語意＝ADR ② 指針）改現在式＋★frontmatter `rev5_blueprint` 之「API 慣例」列「隨刀：wire 地基刀…」→「承襲（…）」；`docs/generated/reference/rev5-blueprint-map.md` 由 generate 自該 frontmatter 重算；C4-L2 拓樸不變零改（核對）
- [ ] T044 [US6] 勘誤：`python3 tools/docsync errata` 逐詞掃本刀改變的字面（`wire 地基刀`、`隨 002`、`rust-fmt-gate 隨 002`、`server 隨 002`、`Lint24`）→ 現在式面逐處改為現在式或指針、史料面不動；★憲法命中（§I.3「機制隨 wire 地基刀落地」）＝不動（provenance 陳述、非未來式；憲法只走 §V.2 Amendment、非勘誤射程）並記 commit 訊息；arc42 01／04 之紀律敘述句不改；只改 08 frontmatter／§8.2 與 NOTES 的「隨刀」「隨 002」形；`docs/ops/NOTES.md`「rust-fmt-gate 隨 002」等句改為已在

---

## Phase 9: Polish & Cross-Cutting

- [ ] T045 quickstart §0～§5 全場景復跑（含 fallback 案、三支碼面閘 check 真實跑、hook 演練復跑、GT-12 腿負向、errata 復掃）＋DoD 負向自證（抽 update case→紅指名→還原；加殭屍 case→紅→還原）＋SC-001～SC-009 逐條對照＋US1～US6 驗收場景→測試案或演練紀錄對照表（函式名＋案序）＋「併發面本刀不驗、結論＝research R11」與「Day-1 三步不適用（零 migration）」記帳（結果全記單元 report、供 final holistic review）
- [ ] T046 perf 事件：pre-commit 全鏈實測（含新增三段、staged 觸發全段）≤45s → `docs/ops/events.jsonl` append `precommit_chain`（若 T011 已記則以本次為第二筆、含 rust-fmt 真跑）；容器冷編時長記 commit 訊息（不入 DoD）

---

## 執行單元對映（research R12；主線派發粒度、每單元一顆外層 commit；冒煙 token 取單元名、不可取 `test`）

| 單元 | 任務 | 收尾產物 |
|---|---|---|
| 主線 | T001、T002 | RULES 名詞段＋RULES-VERSION bump 外層 commit；環境就緒 |
| U0 | T003～T011 | 外層 commit：三支閘＋hook 六處＋RUNBOOK 表＋GT-12 腿＋README／bootstrap＋失準修單＋演練紀錄＋perf 事件 |
| U1 | T012～T020 | rust-api commit（server 基座＋tests 骨架）→ 外層 pin bump＋docsync routes 生成器＋README 成員行 |
| U2 | T021～T024 | rust-api commit（auth／identity／seam／facade sys_user_role）→ 外層 pin bump |
| U3 | T025～T031 | base-web commit（typings＋service 讀端）＋rust-api commit（registry／facade／handler／快照／裁判）→ 外層兩 pin bump |
| U4 | T032～T035 | rust-api commit＋base-web commit（service 寫端）→ 外層兩 pin bump |
| U5 | T036 | rust-api commit → pin bump |
| U6 | T037（主線）、T038 | ADR ② 外層 commit；rust-api commit → pin bump |
| U7 | T039（主線）、T040 | ADR ① 外層 commit；rust-api commit → pin bump |
| U8 | T041（主線）、T042～T046 | 外層 commit：ADR 四筆＋BACKLOG＋活書＋勘誤＋perf；quickstart 復跑紀錄 |

## Dependencies

- Phase 1（T001 必先於任何 Workflow 派發）→ Phase 2 U0（T003～T011）→ U1（T012～T020）→ U2（T021～T024）→ US1（U3）→ US2（U4）→ US3（U5）；US4（U6）與 US5（U7）皆依 US2 寫端在場、彼此獨立；US6（U8）依全部。
- 主線任務 T037／T039／T041 為 ADR 落檔（user 已於 brainstorm／clarify 拍板、主線擬稿→accepted）、不派 agent；T041 回填 T007 之 ADR 序號欄。
- 阻斷型：T003 首跑對 001 承襲檔紅＝blocked；T029 jsonschema 0.53 null 判定異於 rev5 實證＝blocked；T026 需 base-web 容器在跑；T020／T024 起 rust 收尾必在容器內 serial。

## Parallel Execution Examples

- U0：T004／T005 與 T003 不同檔可平行；T007／T009 與 T006／T008 不同檔可平行（皆為 [P] 檔域、agent 內序列亦可）。
- U1：T014／T015 與 T013 不同檔可平行；T018 待 T013～T017；T019（docsync）與 T012～T018（rust）檔域不相交可平行。
- U2：T022／T023 與 T021 不同檔可平行；T024 待三者。
- U3：T025（base-web）與 T027（rust）可平行；T026 待 T025；T029 待 T026～T028；T030 待 T029；T031 待 T030。
- U8：T042／T043 可平行；T044 待 T043；T045 待全部。
- ★rust build／test 不平行（容器內 serial）——[P] 僅指檔域不相交可分派。

## Implementation Strategy

- **MVP**＝Phase 1＋Phase 2（U0～U2）＋US1（U3）：讀端全通即「rev6 第一條管線存在」的可交付增量。
- 增量：US2→US3→US4／US5→US6；每單元收尾六步序（復核→自驗→落帳→子庫 commit→pin bump＋generate→外層 commit）；每單元 review／fix 烤入 RULES scope 塊（T001 之後的新版）。
- 收刀（不在本清單）：final holistic review → finishing-a-development-branch（push／merge 需 user 當回合同意）→ 收刀簿記三步（feature_close window 2、adrs 六筆、backlog_done 三條）→ close_bookkeeping perf 第四步。
