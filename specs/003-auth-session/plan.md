# Implementation Plan: 003 auth 域整批——真登入、會話生命週期、節流＋驗證碼、dynamic 選單、i18n 轉譯

**Branch**: `003-auth-session` | **Date**: 2026-09-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-auth-session/spec.md`（clarify Q1～Q4 定案 2026-09-08）＋docs/brainstorms/003-auth-session.md（拍板 Q1～Q10、五項工程判斷、設計十一節）＋依賴雙源核對 user 拍板 D1～D5（2026-09-08）

## Summary

把 base-web fork 原版 service 已在呼叫的 12 條認證與路由端點補齊到終態（ROUTES 4→16）：真帳密登入（十一步、稽核列三處）、DB-stateful token rotation（grace 30 秒）、撤銷矩陣（logout／被踢／idle；`status` 權威＋denylist 加速層）、帳號維節流三區＋無狀態簽題 captcha、dynamic 側邊欄（Casbin `menu` 維度過濾＋`home` 收斂律＋constant routes 合併）、替代登入四 stub、後端 msg 前端轉譯（三檔 backend 樹 13 鍵＋`zh-tw.ts` 錨點檔）。
技術路徑＝高度參照 `rev5:003-auth-session` 終態碼（research R2 逐檔清單、R3 二十筆 rev6 差異點＋十七筆承襲防回歸），六支新依賴＋`log` 全取最新穩定（R1 雙源表、API 守則）。
同一筆 MINOR Amendment（ADR-00026 draft 已落、status proposed）開 §III.2 首批四 ★ 軌道八用途＋§I.7 島 A～E（含 Q9／Q3／Q4 三句 rev6 增補）——tasks 首個主線任務 user 親決凍結、accepted 前不得動 base-web 既有檔。治理面同刀：跨端閘 `tools/msg-key-gate.py`（逐檔雙向全等）、走查基準對賬工具遷入（`NON_GATE_TOOLS`）、BL-00037①②／BL-00026／BL-00041 刀內收；零 migration、零新 casbin 政策列（R13 複核）。

## Technical Context

**Language/Version**: Rust 1.96.1（edition 2024、容器內 build／test 全程 serial）＋TypeScript／Vue 3（base-web 七支既有檔 inline＋三支新檔、`pnpm typecheck`）＋Python 3 標準庫（跨端閘新工具、走查工具隨遷、docsync tests／gates 擴充、bootstrap 名冊推導）

**Primary Dependencies**: 新進八支（D1～D5 user 拍板、D6 主線同值直採，2026-09-08）——jsonwebtoken **11.0.0**（`rust_crypto`）／argon2 **0.6.0**／redis **1.7.0**（`connection-manager`＋`tokio-comp`）／captcha 1.0.0（`default-features = false`）／sha2 **0.11.0**／hex 0.4.3／log **0.4.34**／getrandom 0.4.3（CSPRNG；argon2 0.6 已無 `OsRng`）；既有 axum 0.8.9、sea-orm 1.1.20、casbin 2.20.0＋vendored adapter、tokio 1.53.1、metrics 0.24.6；MSRV 最高 1.88 ≤ 1.96.1——雙源對照表＝research R1

**Storage**: PostgreSQL 18.4（001 基線；`sys_token`／`session_event`／`sys_login_attempt` 只寫入不改結構、`sys_user` 兩欄、`sys_menu` 讀）＋Redis（DB 0；六鍵族＝data-model §6；不開 AOF＝已知態）；零 migration；rev6 stack 埠 35432／36379

**Testing**: cargo test 三層（純函式紅綠／oneshot contract 16 case＋雙向覆蓋閘＋快照裁判／真 DB＋真 redis integration 掛四種 RAII 守衛——research R7）；`--test-threads=1` 容器內；python 工具自帶 `test`（跨端閘五案、走查工具離線樁、docsync test 新增 hook 四檔＋bootstrap 面＋GT-12／GT-05 腿）；前端零測試框架＝`pnpm typecheck`＋兩段 review＋CDP 對照 rev5（22080 vs 32080）；quickstart 經 front-nginx 真 HTTP 走查＋走查前後基準 diff rc 0

**Target Platform**: Linux 容器（compose project `rev6-admin`、七件業務件；host＝WSL2、/mnt/d drvfs 跑過 compose 後同 shell 重新 `cd`；CDP 由 host 瀏覽器 9229）

**Project Type**: web-service（rust-api server crate 擴編：四新模組＋七新 handler 檔＋六新 facade＋`dev_identity` 汰換）＋前端接線（base-web 四 ★ 軌道八用途＝12 支既有檔＋ADAPT 3 檔 4 行＋三新檔）＋憲法 Amendment＋治理工具（一支新閘、一支隨遷工具、hook 守衛擴充）

**Performance Goals**: 無業務量化目標；登入路徑之密碼驗章時序等化（查無帳號亦跑滿一輪）；pre-commit 全鏈 ≤45s 警戒（新增 msg-key-gate 段零 docker、秒級）；nginx `auth_limit` 5r/s burst 40 為邊緣既有態（004 域）

**Constraints**: 憲法 §I.3 wire 凍結面（信封／13 碼矩陣不動、9 可發＋4 保留／msg=key／HTTP 200 例外恰二）；§I.5 rev5 參照紀律（重打字＋註解重寫＋R3 兩份防回歸清單）；§III fork-delta 三元組硬邊界＋`.env*` 機器守；Amendment 硬序；gate2 seed × runtime 寫入（sequence 重設守衛）；redis 鍵 uniq 前綴；review agent 只讀；rev5 樹唯讀、rev5 stack 絕不指向

**Scale/Scope**: 16 routes（12 新）／9 AppError 變體（3 新）／13 msg keys（6 新）／5 設定鍵消費／6 redis 鍵族／AppState 五欄／server crate 新增約 20 檔（rev5 對應終態約 2.3 萬行含 inline 測試、rev6 本刀量級預估 8～12k 行）／base-web ★軌道既有檔 12 支（修改型 10＋純新增型塊 2）＋`.env*` 3 檔 4 行＋3 新檔／憲法 +8 表列 +5 島／ADR 5／BACKLOG done 4＋改 1＋`feature_close.backlog_add` 列 9（已配號 BL-00043～00049 七條＋收刀新配兩條：`/auth/error` 錨、`roles_of_user` DbErr 守衛錨）／執行單元 12（U0～U11、R15）

## Constitution Check

*GATE: 對照 constitution v1.2.0 §IV 九題（初檢＝Phase 0 前；複檢＝Phase 1 設計後）。★本刀為 rev6 首刀踩到「須 Amendment」路徑（001／002 皆九題全過）；第 2／7／9 題判定值「涉及——授權以 Amendment 先行取得」承 rev5 003 形制；Complexity Tracking 不填（★軌道與島皆循憲法明文機制取得授權、非違規）。*

| # | 題 | 判定 | 依據 |
|---|---|---|---|
| 1 | 違反 §I.1 base-web 權威？ | **PASS with disclosure** | 為 fork 原版 service 已在呼叫的 12 條端點補後端；回傳型逐欄忠實 typings（contracts 三檔）。揭露一處排程延後：`/auth/error`（兩張 demo 頁）不提供——§I.1「v1 從簡只能是交付排程」⇒ 排程錨（收刀新記 BL、承 `rev5:B-053`）、非範圍縮減；其兌現撞保留碼 `9999` 三錨與 §I.3 msg=key ⇒ 須先走 §I.3 Amendment（spec Out of Scope） |
| 2 | 動 base-web inline？ | **涉及——授權以 Amendment 先行取得** | ★軌道既有檔 12 支＋`.env*` 3 檔 4 行（spec ★軌道逐處登記表 16 列＝`.env*` 3 列＋★軌道 12 列＋新檔 1 列；風險判準可覆算）；授權鏈＝ADR-00026 draft（已落、proposed）→ user 親決（tasks 首個主線任務）→ accepted＋§III.2 四軌道八用途（哨兵句同批移除）＋§I.7 島 A～E＋bump 1.3.0＋generate（§V.2 四步、獨立 commit）。★硬序：accepted 前不得動任何 base-web 既有檔；`.env*` 走 §III.1 ADAPT（§II #2 明寫）零修憲、標記裸形且在 fork-delta-lint 射程內（rev6 差異 R3-2）。fork-delta 紀律＝修改型 `原行:`／新增型圈界／`rev6-inline` token／用途識別符（contracts/code-gates.md §1）。驗收錨＝`tools/fork-delta-lint.py`（三元組硬邊界）＋一正一反演練 |
| 3 | menu 走 Casbin enforce？ | **PASS** | `getUserRoutes` 以 DB-fresh roles 經 `menu` 維度 `get_filtered_policy` 過濾 sys_menu 樹；`buttons` 同法取 `button` 維度；demo menu 全集在 seed、不啟用 `hideInMenu`；constant routes 前端**合併**（§I.2 末句授權新增、builtin 不動）；零新政策列（R13 實證：12 新 route 無 Policy、seed 已含兩維度政策） |
| 4 | wire 對齊 §I.3？ | **PASS** | 信封三欄／`code` string／業務錯誤 HTTP 200（三新變體落 `_ => OK` 萬用臂）／`userId`＋`MenuRoute.id` 序列化邊界轉字串（既有 `serialize_i64_as_string`）／13 碼矩陣不動（9 可發＋4 保留、ADR-00023 雙錨八處同批改對）／`msg` 載穩定 key（`MSG_KEYS` 7→13、Biz 字面構造）／例外仍恰二（方法不符 4040 為 002 既定）；契約機器化＝contract 16 case＋wire-schema 快照重抽（新檔 `rev6-auth.d.ts`）＋跨端閘。驗收錨＝contracts/wire-auth.md、wire-route.md、msg-keys.md |
| 5 | 拷貝前代 code？ | **否（重打字）＋隨遷工具授權** | rust 應用碼全程重打字、註解 rev6 語境（rev5 出處帶 `rev5:`；R3 差異點 20 筆＋承襲防回歸 17 筆烤入 prompt）；`tools/walkthrough-baseline.py` 為 RULES 名詞段「隨遷工具」（tools/ 射程、四型失效引用 rev6 化＝R10）；跨端閘為新寫（rev5 Lint24 住 docs-sync、形制翻案）；sea-orm-adapter／entity／migration 例外零改 |
| 6 | 抵觸 §II 拍板？ | **否（兌現 #2）** | 兌現 #2（`.env` `VITE_AUTH_ROUTE_MODE=dynamic`、ADR-00003 註 4 之 ADAPT 首刀）；#1 unknown header 忽略（contract case 沿 002）；#3 `/api` 前綴拓樸不動。★翻兩處**碼內**舊拍板（非 §II 條目）：`state.rs`「恰兩欄」封條（clarify Q1）、root `Cargo.toml`「不引 argon2」——各立 ADR 並同批改寫註解（contracts/code-gates.md §7 ②③） |
| 7 | 觸及 §III ★ 軌道？ | **涉及——授權以 Amendment 先行取得** | 四條八用途（AUTH a／b／c、LOGIN-CAPTCHA i、I18N i／ii／iii、LOGOUT-UX i）屬「新能力」非「用途補完」（跨多頁、新 i18n 面級節、新元件行為）⇒ 須 Amendment；`(ii)` 類三項明文不授權；表列形受 `load_roster` 六規則約束（R8）、ADR-00026 表列已依規則書寫；i18n 三檔為最熱面（風險誠實標高、rebase 處置入 ADR 後果） |
| 8 | 新建業務表含 §I.6 六審計欄？ | **不適用（零 migration）** | 三張消費表皆 001 基線既有（sys_token 變體 C／session_event 與 sys_login_attempt 變體 B）、只寫入不改結構；append-only 兩表零 update／delete；★連帶紀律＝runtime 寫入推進三支 sequence、測試守衛與走查清理顯式 `setval` 重設（data-model §9、R7-4）；DDL 冒出＝範圍拍板翻案（BL-00042）＋RUNBOOK §10 三步 |
| 9 | 觸及 §I.7 行為島？ | **涉及——授權以 Amendment 先行取得** | 五座島 A～E 隨本刀以同筆 MINOR 入憲（ADR-00026 §二、rev5 v1.3.0 字面為底＋Q9／Q3／Q4 三句）；state-machine 鏡頭（data-model §1「現態×事件→次態＋副作用」矩陣）非 CRUD 格子；跨島刻意不一致（idle fail-loud vs 節流 fail-open）與跨島總則入條文；方向性反轉自此 MAJOR |

**初檢結論**：第 1／3／4／5／6／8 題 PASS；第 2／7／9 題「涉及、授權以 Amendment 先行取得」＝條件通過。

**Phase 1 複檢（設計後）**：research R1～R16／data-model §1～§14／contracts 四檔／quickstart／ADR-00026 draft 產出後重走九題——判定不變。第 2／7 題授權鏈之形制已定（ADR-00026 表列逐字、`load_roster` 六規則逐條對照＝R8）；第 4 題由 contracts 三檔＋data-model §11／§12 承載；第 5 題 R2 清單逐檔標「重打字／隨遷／新寫」、零拷貝面；第 9 題條文全文已在 ADR-00026 §二。design 新增之憲法接觸面＝零（Phase 1 產物皆為既有拍板的具象化）。★**GATE 狀態＝條件通過**：ADR-00026 accepted＋bump 1.3.0 為 tasks 第一個 ★ 主線任務且為硬閘，未完成前第 2／7／9 題不得視為 PASS、且不得動任何 base-web 既有檔（純新增檔不受此閘）。

## Project Structure

### Documentation (this feature)

```text
specs/003-auth-session/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── checklists/requirements.md
├── contracts/
│   ├── wire-auth.md         # auth 面 9 條＋前端 wrapper
│   ├── wire-route.md        # route 面 3 條＋動詞不符（002 既有）
│   ├── msg-keys.md          # 13 鍵三語譯文＋跨端閘機器契約
│   └── code-gates.md        # fork-delta 標記字面／msg-key-gate／walkthrough 工具＋RUNBOOK §9c 實文／BL-00037／BL-00026／BL-00041／名冊落點總表／ADR 五筆
└── tasks.md                 # /speckit-tasks 產（非本命令）
docs/arc42/decisions/ADR-00026-constitution-amendment-star-tracks-and-behavior-islands.md   # plan 期 draft（proposed）；tasks 首個主線任務 accepted
```

### Source Code (repository root)

```text
rust-api/                                    # worktree（rev6-admin-rust-api）
├── Cargo.toml                               # workspace.dependencies += 七支（R1）；「不引 argon2」註解翻案（ADR）
└── server/
    ├── Cargo.toml                           # features 逐 crate（rust_crypto／connection-manager＋tokio-comp／captcha default-features=false／log）
    ├── src/
    │   ├── main.rs                          # boot：config 六 getter→db（BL-00026 sqlx_logging_level Debug）→cache::connect panic→enforcer→AppState 五欄→router
    │   ├── lib.rs                           # 模組樹（auth/cache/throttle/captcha；絕不裸寫 captcha::）
    │   ├── config.rs                        # +jwt_secret／refresh_token_secret／jwt_iss／jwt_aud／redis_url／captcha_secret（_FILE 沿 env_or_file）
    │   ├── state.rs                         # AppState 五欄＋JwtConfig；封條翻案＋五欄窮舉錨測
    │   ├── error.rs                         # +LoginFailed／TokenExpired／ModalLogout；MSG_KEYS 13；八處測試改對
    │   ├── router.rs                        # ROUTES 16、ROUTES_COUNT 16
    │   ├── request_context.rs               # real_ip／x_forwarded_for／ip_confidence 原樣轉錄（003 形）
    │   ├── obs.rs                           # +throttle_degraded_total{source×7}／denylist_hit_total{redis|pg}／throttle_soft_zone_total
    │   ├── auth/{mod.rs(改), enforce.rs(改：真驗章＋denylist 四級降級), jwt.rs(新)}     # dev_identity.rs 整檔刪
    │   ├── cache/mod.rs(新)                 # SessionCache＋六鍵族 builder＋REASON_*
    │   ├── throttle/mod.rs(新)              # 帳號維三區＋設定載入（缺失／矛盾退常數）＋captcha 驗題接點
    │   ├── captcha/mod.rs(新)               # issue／verify_challenge／answer_mac；撞名消歧三規則
    │   ├── handler/
    │   │   ├── mod.rs(改：模組宣告擴編)
    │   │   ├── auth/{mod,login,refresh,logout,user_info,alt_stub}.rs(新)
    │   │   ├── route.rs(新) / captcha.rs(新)
    │   │   └── system_settings.rs(改：dev token 測試面真 token 化＋AppState 建構點 2 處＋BL-00041 註解)
    │   └── model/
    │       ├── mod.rs(改：+pub mod password；檔頭自述)
    │       ├── password.rs(新)              # verify／dummy_verify（OnceLock）
    │       └── facade/{sys_token,session_event,sys_login_attempt,sys_menu,sys_user,sys_role}.rs(新)＋test_kit.rs(擴：real_state／uuid／uniq_prefix／兩守衛；BL-00041 註解)＋mod.rs(改)
    └── tests/
        ├── common/mod.rs(改：stub_state 五欄) / contract.rs(改：16 case) / wire_schema.rs(改：Api.Auth／Api.Route 裁判 case)
        ├── entity_access_lint.rs(改：六 facade 射程)
        └── fixtures/wire-schema.json(重抽)

base-web/                                    # worktree（rev6-admin-base-web）
├── .env / .env.test / .env.prod             # ADAPT 四行（rev6-inline 裸形＋原行:）
└── src/
    ├── store/modules/{route,auth}/index.ts  # ★AUTH(a)／★LOGIN-CAPTCHA(i)
    ├── views/_builtin/login/modules/{pwd-login,code-login,register,reset-pwd}.vue   # ★LOGIN-CAPTCHA(i)／★AUTH(b)
    ├── hooks/business/captcha.ts            # ★AUTH(c)
    ├── layouts/modules/global-header/components/user-avatar.vue                     # ★LOGOUT-UX(i)
    ├── service/request/index.ts             # ★I18N(i)
    ├── service/api/rev6-auth.ts(新)         # WRAPPER+：fetchLoginWithCaptcha／fetchLoginCaptcha／fetchLogout／四 stub（七支）
    ├── typings/{app.d.ts(★I18N(iii)), api/rev6-auth.d.ts(新 ADAPT+)}
    └── locales/langs/{en-us.ts,zh-cn.ts}(★I18N(ii))＋zh-tw.ts(新 I18N+ 錨點檔)

tools/
├── msg-key-gate.py(新)                      # 碼面閘（contracts/code-gates.md §2）
├── walkthrough-baseline.py(隨遷)            # NON_GATE_TOOLS（§3）
├── bootstrap.sh(改：名冊自 tracked 推導、:(glob))
├── fork-delta-lint.py(改：self_test 註解「§III.2 現為空表」改現在式；U0)
└── docsync/{gates.py(NON_GATE_TOOLS), book.py(SUB_SCAN 子庫腿), tests/{test_hook_wiring,test_gates,test_book_ids}.py}
.githooks/pre-commit(改：msg-key-gate 段＋for 自測名冊兩支＋selftest-docsync 觸發放寬)
.specify/memory/constitution.md(改：§III.2 四列＋§I.7 島 A～E＋1.3.0；tasks 首個主線任務)
docs/ops/RUNBOOK.md(改：檔頭章節現況句、§9c 實文、§12 兩列＋前言現值句)；README.md(改：第 14 行憲法版本鏡像〔U0〕＋tools/ 樹兩行)
docs/arc42/{05,06,08,10,12}-*.md(as-built、U11；§10.2 島 A～E 各一品質情境)；docs/arc42/decisions/ADR-000{27..30}-*.md(刀內落)
docs/ops/BACKLOG.md(收刀：done 4／BL-00031 條文改／add 8)；docs/ops/NOTES.md(收刀→004)
```

**Structure Decision**：server crate 目錄形逐一對應 rev5 003 終態（R2 清單）以最小化參照摩擦；handler 依端點群拆檔＋facade 一表一檔，使每個執行單元的允許檔案清單有圈界力（防呆六件套⑥）；`router.rs`＋`contract.rs`＋`tools/docsync/tests/test_references.py` 為 U5～U9 序列共用檔（逐 US 加列並 bump 同一 `ROUTES_COUNT` 與真 repo 釘值列、不可並發；承 rev5 003 analyze 修正與 002 T029／T033 形、不設尾端獨佔單元）。執行單元＝research R15（U0 主線 Amendment 凍結→U1～U4 後端基座→U5～U9 依 US 交付面→U10 治理→U11 收攏）；每單元 pin bump、Workflow 六件套、review／fix 烤入 RULES scope 塊（RULES-VERSION 不變）、每 run 不重複 agent ≤20；發射前 `IMPL_OPTS`→`opus[1m]`。

## Complexity Tracking

Constitution Check 九題：六題 PASS、三題「涉及——授權以 Amendment 先行取得」（循憲法 §V.2 明文機制、非違規）——本節免填；授權鏈與硬序記於 Constitution Check 第 2／7／9 題。
