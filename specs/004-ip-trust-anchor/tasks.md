---

description: "Task list for 004-ip-trust-anchor"
---

# Tasks: 004 IP 域整批——信任錨還原真實來源、IP 存取閘、來源維節流、IP 規則管理頁、管理員解鎖

**Input**: Design documents from `/specs/004-ip-trust-anchor/`

**Prerequisites**: plan.md、spec.md（US1～US6、clarify Q1～Q3）、research.md（R1 依賴三支／R2 對應碼／R3 二十三筆差異＋清單 B 十一筆／R6 節流／R8 閘衝擊／R9 缺席退路／R10 單元骨架）、data-model.md（§5 序列名冊單一權威）、contracts 五檔（wire-ip-rule／wire-throttle-unlock／wire-auth-delta／trust-model-config／code-gates）、quickstart.md；
憲法 1.3.0（ADR-00034 draft 已落、proposed）；連帶 ADR 六筆待立（序號自 ADR-00035 起於落檔時取）。

**Tests**: 本 repo TDD＝CLAUDE.md §2 紀律、**非可選**——每實作 task 內先紅後綠。測試層對照（research R8）：*contract case*＝`rust-api/server/tests/contract.rs` registry（oneshot 免 DB、`connect_lazy` 假連線；★oneshot 不經 make-service ⇒ 請求上下文恆缺席、走 FR-013 退路＝既有 36 處 `X-Real-IP` 注入案零改形）；*integration*＝各模組 `#[cfg(test)]` 真 DB＋真 redis 案（`test_kit` 守衛；★U3 起 `SequenceResetGuard` 廢除、runtime-append 四表只清自寫列〔水位形〕、`sys_ip_rule` 清列＋setval；經 make-service 之案以 `tower::ServiceExt` 帶 `ConnectInfo` 或直呼中介層 helper）；*unit*＝純函式（`trust` 全態矩陣、`ipgate::decide`、正規化、桶粒度）；*lint*＝`tests/serve_connect_info_lint.rs`、boot 靜態掃描；*工具*＝自帶 `test`＋一正一反。
★base-web 側**零測試框架** ⇒ 凡 `base-web/**` 之 task 先紅後綠不適用、把關＝`pnpm typecheck`＋`fork-delta-lint` rc 0＋兩支新閘＋兩段 review＋CDP 走查（SC-010 結構清單）；混合單元（U7／U8／U10／U11）之 `CONTEXT` MUST 逐域列兩套驗收、review prompt「勿誤報」段列入「base-web task 無紅綠腿不算缺陷」。

**Organization**: 依 user story 分 phase（US1～US6）；story 間有天然順序相依（middleware→閘→端點→頁；`router.rs`／`contract.rs`／`test_references.py` 逐 phase 加列）；**執行單元對映**（承 research R10、依 US 交付面重切為 U0～U12：U5 拆為 U5 上下文與 auth 端點／U6 存取閘、US3 分後端 U7 與前端 U8、末尾 U12 收攏）為 Workflow 派發粒度、每單元一顆外層 commit（單元收尾六步序＝CLAUDE.md §2）。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 檔域不相交、可分派給不同執行單元或同單元內不同 implementer；★僅指「可分派」——**cargo 執行一律序列**（容器內 `--test-threads=1`）。
- **[Story]**: US1～US6；Setup／Foundational／Polish 不掛。

## 全程紀律（每 task 隱含、不逐條重複）

- ★**實作前先讀** research R2 對應之 rev5 碼（`../fork260509-rev5/{rust-api,base-web,tools}/`＝凍結 worktree、**唯讀、絕不寫入**、派 agent 時唯讀令烤進 prompt＝RL-0064）；高度參照、**重打字消化不拷貝**、註解一律 rev6 語境重寫（rev5 出處帶 `rev5:`）；research R3 二十三筆差異點與清單 B 十一筆**不得帶回**（★特別：無 L1 鎖定鍵、無 `DEL` 步、無 no-escalation、無 access_log_mw、無 region、無 HLL）。
- ★**Amendment 硬閘**：T001 未 accepted 前**不得動任何 base-web 既有檔**（含 `locales/langs/*.ts`、`app.d.ts` 之 backend 節）；純新增檔（管理頁三檔、`rev6-ip-rule.{ts,d.ts}`）依 §III.2 表外宣告 3 不受此閘。
- ★**跨子庫同步律**：`wire-schema`（typings 側 base-web／快照側 rust-api）與 `msg-key-gate`（`MSG_KEYS` 側 rust-api／三檔 locale 側 base-web）兩側改動須在**同一顆外層 commit** 同時 bump 兩 pin；單側先 bump＝閘紅或歷史留分叉組合。
- ★**API 守則**（research R1）：`toml` 1.1.6（`serde` derive＋未知鍵逐鍵檢、★不用 `deny_unknown_fields`；as-built＝先取通用 `toml::Table` 再 `try_into`）／`arc-swap` 1.9.2（`ArcSwap::load`／`store`）／`futures-util` 0.3.34 只用 `StreamExt::next`／redis 1.7 `Client::get_async_pubsub()` 專用連線（多工 `ConnectionManager` 不可 SUBSCRIBE）／`IpNetwork` 經 `sea_orm::prelude`。
- rust build／test **一律容器內、全程序列**：`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1`；容器內 `cargo fmt --all --check`（碼面閘）。
- ★**絕不 push／merge**（本清單零 push／merge 任務；收尾整合走 finishing、需 user 同意）。
- **兩段式 commit＋pin bump（六步序⑤、次序不可反）**：子庫內 commit → 回外層 `git add <子庫>` → `python3 tools/docsync generate` → `git add docs/generated docs/arc42/ARCHITECTURE.md docs/ops/LESSONS.md tools/orchestration/_sk_rules.js` → 外層 commit；★生成物一律主線動作、**不入任何 agent 允許檔案清單**；ROUTES 增列使 `routes.md` 過期、ADR／BACKLOG 增列使 `DECISIONS-INDEX.md`／`STATE.md` 過期。
- ★**發射前置**：每單元 `python3 tools/orchestration/assemble.py tmp/004-uN.py tmp/004-uN.mjs` 組裝；模型分派依 user 當前指示（2026-09-15：workflow／subagent 暫一律 opus5 1m xhigh）、**發射前向 user 確認**；review／fix 烤入 `python3 tools/docsync rules emit --scope <...>` 塊（RULES-VERSION 不變＝`a2721b391067`）；Workflow launch 與 `python3 tools/wf-watchdog.py <token>` Monitor 同回合原子成對、token≠`test`、取單元名形 `u<N>-<slug>-<4hex>`。
- 測試環境紀律：redis 測試鍵 uniq 前綴；`sys_login_attempt.real_ip` INET NN ⇒ 缺席退路案顯式注入 `X-Real-IP`、上下文案經中介層 helper 注入；fixture 一律 UPDATE 而非 INSERT 且還原顯式歸 NULL 審計欄；`sys_ip_rule` 測試寫入以 `IpRuleRowsGuard`（清列＋setval）還原；稽核斷言水位／窗形、不寫絕對計數。
- 書面產物與註解一律 zh-TW；`/mnt/d` 跑過 compose 後同 shell 先重新 `cd`。

---

## Phase 1: Setup（★主線閘：憲法 Amendment 凍結＋前置體檢；U0）

**Purpose**: 取得 base-web inline 與島 F 入憲的憲法授權（user 親決）、環境就緒。★本 phase 全數主線任務、不入 agent 單元。

- [x] T001 ★主線任務（user 親決）：`docs/arc42/decisions/ADR-00034-constitution-amendment-island-f-and-manage-page-track.md` proposed→accepted＋`.specify/memory/constitution.md`（§I.7：島 E 四處改寫逐字＝ADR §二、新增島 F 段 F1～F8、承襲指針表 F 列尾註「；rev6 已入憲 v1.4.0（ADR-00034）」、末句射程改「六島」；§III.2：新增 `★BASE-WEB-MANAGE-PAGE-WIRING` (i) 一列逐字＝ADR §一、I18N (ii) 權威句與 (i) 範圍欄／紀律欄改寫、五列範圍欄實數化、表外宣告 1 改句；文末 `Version` 1.4.0／`Last Amended`／Amendment log 加 1.4.0 列）＋`README.md` 憲法版本鏡像行「現行 1.3.0＝ADR-00026」→「現行 1.4.0＝ADR-00034」＋`python3 tools/fork-delta-lint.py` rc 0（名冊八名）＋★新列變異自證（暫把該列範圍欄任一反引號路徑改裸措辭→lint 紅→還原、porcelain 零差異＝證該列真被 `load_roster` 讀進）＋`python3 tools/docsync errata 1.3.0`／`errata 負快取` 復掃（憲法命中已改、史料面不動）＋`generate`；獨立 commit `docs(constitution): amend §I.7 島 F＋島 E 四處＋§III.2 MANAGE-PAGE 軌道與五欄實數（1.3.0→1.4.0）`。**DoD：lint 全綠；此 commit 落地即解除 base-web 既有檔硬閘**
- [x] T002 前置體檢：`bash tools/bootstrap.sh` 綠；`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait` 起得齊；容器內 `cargo --version`＝1.96.1；base-web 容器 `pnpm typecheck` 基線綠；`python3 tools/schema-gate.py check` 三閘綠；`python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-004-base.json` rc 0；★信任模型掛載實證：`docker compose … exec -T rust-api cat /etc/rev6/trust-model.toml` 與 `deploy/trust-model.dev.toml` 逐位元相同、`docker compose … config` 之 `APP_TRUST_MODEL_PATH` 指同路徑；記錄動工前基線數：`grep -rn 'AppState {' rust-api/server/` 建構點清單、`grep -rn -c 'SequenceResetGuard::new' rust-api/server/`＝69／10 檔、全量測試逐 target 計數（L-029 形、供 U3 前後比對）

---

## Phase 2: Foundational（阻塞全部 user story：U1 依賴與信任錨 → U2 規則判定與 facade → U3 測試基建 → U4 狀態容器、門鈴與 boot）

**Purpose**: 未完成前不得開任何 US——三支依賴、信任模型載入、`trust/` 純函式全形、`ipgate/` 判定核與 `sys_ip_rule` facade、兩支 lint、測試基建改形、`AppState` 七欄、門鈴、boot 接線、序列名冊。

### U1 依賴與信任錨（research R1／R4；contracts/trust-model-config.md）

- [x] T003 ★主線任務（brainstorm G7 已拍板、主線擬稿即 accepted）：`docs/arc42/decisions/ADR-000NN-introduce-three-ip-domain-dependencies.md`（序號落檔時取＝ADR ⑥；決定文＝R1 三源表、G7 紀錄、`futures-util` `default-features = false` 理由、零新 redis feature flag；provenance 引 `rev5:004` research R3 同位）；accepted＋`generate` 同 commit
- [x] T004 依賴三支釘版：`rust-api/Cargo.toml` `[workspace.dependencies]` 加 `arc-swap = "1.9.2"`／`futures-util = { version = "0.3.34", default-features = false }`／`toml = "1.1.6"`；`rust-api/server/Cargo.toml` 三支 `workspace = true`＋依賴清單註解重寫（rev6 語境；檔頭「web／obs 依賴群隨功能刀進場」句本刀兌現處改現在式）；容器內 `cargo build --workspace` 綠；`Cargo.lock`：`toml` 新條目、`arc-swap`／`futures-util` 版本不變、★不出現 `futures-macro` 新條目（記 commit 訊息）
- [x] T005 [P] `rust-api/server/src/config.rs` 信任模型載入：`trust_model_path()`（`APP_TRUST_MODEL_PATH`、`*_with` 注入形）＋`RawTrustModel`（TOML 六集合、欄名＝contracts/trust-model-config.md；未知鍵逐鍵檢＝載入不變、只發 `unknown_key` 告警，★不用 `deny_unknown_fields`〔契約「未知鍵＝載入告警（不當機）」、rev5 config.rs 同判；主線 2026-09-15 修正〕）＋`load_trust_model(path, lookup) -> (TrustModel, Vec<TrustLoadWarning>)`——三層失敗語意（缺路徑／讀檔失敗→扁平退路 `APP_TRUSTED_PROXY_CIDRS` 充 `internal_default`／整體解析失敗→**全空不套退路**／單集合含無效 CIDR→只清該集合）＋★`rev5:B-074` IPv4-mapped 網段字面判別（取位址本身而非遮罩後網段；告警指名集合、壞字面、改寫建議；清該集合）＋★六集合全空告警（檔在且解析成功但全空＝零訊號不可）；永不 panic、告警回傳給 boot 逐筆 warn。**DoD：七類輸入（完整／部分／整體壞／單集合壞／mapped 字面／全空／未知鍵）unit 先紅後綠**
- [x] T006 [P] `rust-api/server/src/trust/mod.rs` 新建型別群（★同批 `rust-api/server/src/lib.rs` 加 `pub mod trust;`）：`TrustModel` 六集合＋`TunnelConfig`／`CdnEntry`／`MyPublicEntry`／`Binding`＋`Confidence` **八態**與 `as_str` 單一出口（`cdn_verified`／`proxy_clean`／`direct`／`cdn_anchored`／`proxy_soft`／`cdn_mismatch`／`fallback`／`chain_rejected`）＋`SoftReason`／`Evidence`＋★`is_trusted` 單一 helper（受信集＝跳過集＝六集合聯集、必含 tunnel＋cf_gate_egress）＋`DEFAULT_CONNECTING_IP_HEADER = "CF-Connecting-IP"`。**DoD：八態字面 unit＋六集合各一命中案先紅後綠**
- [x] T007 `rust-api/server/src/trust/mod.rs` 鏈正規化與溢出短路：`MAX_XFF_TOKENS = 32`＋`normalize_xff`（★先取右端視窗再逐欄解析）＋`parse_xff_token`（剝連接埠／IPv6 區域識別／方括號；不可解析**丟棄**＝該跳不存在）＋`apply_chain_overflow`（原始跳數 > 32 ⇒ `chain_rejected`、★只改信心、`real_ip` 沿判定腿結論不覆寫〔勘誤：初稿誤作「取傳輸層對端」、碼面由修單 U5e 更正〕；無條件套於三層之後）。**DoD：先紅後綠，必含三語意區辨測試（丟欄／中止整鏈／佔位跳三者結論相異）＋右端視窗方向反例（左端洪泛不得擠出真實來源）＋溢出腿位址不被覆寫案（經受信代理＝鏈推導位址≠peer；對端閘腿＝peer）**
- [x] T008 `rust-api/server/src/trust/mod.rs` `resolve_client_ip` 三層＋F6 硬化＋兩覆蓋＋`to_canonical`：①對端閘 ②Tier-1 錨（最右 CDN 段；★錨右鄰起至對端全受信否則棄錨退③；錨左第一非 CDN→`cdn_anchored`、無→`fallback`）③最右非受信（`proxy_clean`／`proxy_soft` 兩觸發）④整鏈受信→`fallback`；覆蓋 A 通道回退（採訪客位址、信心不升）、覆蓋 B 邊緣驗證（四前置全中→`cdn_verified`／不符→`cdn_mismatch`、不動位址）；IPv4-mapped 折疊單點。**DoD：先紅後綠——硬化兩對照案（攻擊形 `[偽造, CDN 邊緣, 攻擊者, 代理]`→攻擊者＋`proxy_clean`；合法形硬化前後逐位元相同）＋四前置各缺一透傳＋七態逐態 ≥1 案（SC-001）**

**Checkpoint（U1）**: 三支依賴在場、信任模型三層載入、信任錨純函式全態可測；rust-api commit＋外層 pin bump＋generate

### U2 規則判定核、facade 與 lint（research R5；contracts/wire-ip-rule.md；data-model §1.1／§2.2）

- [x] T009 [P] `rust-api/server/src/ipgate/mod.rs` 新建純函式核（★同批 `lib.rs` 加 `pub mod ipgate;`）：`RuleSet{allow, deny}`＋`Verdict`＋`Decision{verdict, matched_cidr}`＋`STRUCTURAL_EXEMPT` 六段＋`decide`（③豁免→④allow any-match→⑤deny any-match→⑥預設放行；集合語意、與載入順序無關）＋`build_ruleset`（未知 `wbip_type` 列 skip、回 `skipped` 清單由呼叫端告警）＋`would_self_lock`（＝`decide(rs_after, ip) == Deny`、同一 `decide`）。**DoD：先紅後綠——白＞黑（同網段兩類並存）／豁免段建 deny 仍放行／兩袋皆空放行／未知型 skip 其餘照常／`would_self_lock` 對 allow 恆 false、對豁免段恆 false**
- [x] T010 [P] `rust-api/server/src/model/facade/sys_ip_rule.rs` 新建：`load_active`（回 `Vec<(IpNetwork, String)>`）／`list(filter{cidr 模糊, type, deleted 三態}, page)`（id 降冪、`PageRes` 形）／`IpRuleWrite`＋`insert`／`update`／`soft_delete`／`restore`（皆收 `ConnectionTrait` 供 U7 同交易組稽核列；成對寫／清 `deleted_at`／`deleted_by`）／`IpRuleMutateError`（partial unique 衝突辨識→conflict、狀態不符→not_found）；`facade/mod.rs` 註冊（★終態嚴格 ASCII 升冪：`sys_ip_rule` 在 `sys_login_attempt` 前）；★`test_kit.rs` 加 `IpRuleRowsGuard`（Drop：DELETE 本案列＋`setval('sys_ip_rule_id_seq', <水位>)`）。**DoD：真 DB 案先紅後綠（衝突／軟刪後重建／復原衝突／三篩選）**
- [x] T011 [P] `rust-api/server/tests/serve_connect_info_lint.rs` 新建（`rev5:B-075`）：讀 `src/main.rs` 原始碼、定位 `axum::serve(` 呼叫實參、斷言含 `into_make_service_with_connect_info::<SocketAddr>`；不受 `with_graceful_shutdown` 鏈影響；裸呼形與格式化折行形各一反例格（合成字串）；拔線即紅。**DoD：對現行 `main.rs` 綠、兩反例紅**
- [x] T012 `rust-api/server/tests/entity_access_lint.rs` 名冊：facade 三支（`sys_ip_rule`／`sys_operation_log`〔U7 落〕／`test_kit` 擴充）落既有排除面、handler 新檔自然入掃描面、零 path-root `entity::`；`tests/entity_behavior_lint.rs` 零觸碰確認（entity crate 零改）。**DoD：兩 lint 綠、結論記 report**

**Checkpoint（U2）**: 判定核與 facade 在場、B-075 lint 守住備線；rust-api commit＋pin bump

### U3 測試基建（brainstorm G6；BL-00070；BL-00075；contracts/code-gates.md §3／§4）

- [x] T013 廢除 `SequenceResetGuard`：`rust-api/server/src/model/facade/test_kit.rs` 刪 struct＋自證測＋doc（改寫為「runtime-append 四表序列不復位、各案水位清理」立論、引 `rev5:55bb3e3`／`rev5:L-055`／LL-00017／LL-00022）＋69 處 `SequenceResetGuard::new(...)` 掛載點（10 檔、`grep -rn` 現算）逐處移除或改掛 `SessionRowsGuard`（既有、水位形）；新增 `OpLogRowsGuard`（`sys_operation_log` id 水位、只刮自寫列）供 U7／U10；`RESET_SEQUENCES` 名冊刪除；`SeedRestoreGuard`／`RowFixupGuard` 不動。**DoD：全量測試逐 target 計數與 T002 基線一致（只減不增之差＝自證測）；★dev 庫以 psql 植一列真帳號 `sys_login_attempt` 殘列後全量仍綠（SC-013）、拔除殘列**
- [x] T014 [P] BL-00070 七處收攏：`router.rs` `mod tests` `stub_state`／`lazy_db_state`、`auth/enforce.rs` `state_with`、`handler/system_settings.rs` 端點案、`handler/route.rs`、`handler/captcha.rs`（已委派、核）、`obs.rs`（具名留存、不讀 body）、`router.rs` `send`（具名留存、通用送出殼）→ 同形者委派 `test_kit::oneshot_json`；★`AppState` 測試字面建構點收斂至 `test_kit::stub_state_with(...)`／`real_state()` 單一構造點（`tests/common/mod.rs` `stub_state` 保留為 integration crate 入口）；共用件 doc 列明具名留存兩處與理由。**DoD：`grep -rn 'AppState {' rust-api/server/src` 只剩 `state.rs` 定義、`test_kit.rs` 構造點與 `main.rs`；全量綠**
- [x] T015 [P] `tools/walkthrough-baseline.py` 三改（contracts/code-gates.md §3）：①`RESTORE_TABLES` 3→5（＋`sys_ip_rule`／`sys_operation_log`）②`restore --seed` 模式（無須基準檔；五表清列＋`sys_ip_rule` 序列 setval 回 seed；安全帶語意沿用）③`diff` 對 runtime-append 四表序列只比存在性（名冊與 `tools/schema-gate.py` `RUNTIME_APPEND_TABLES` 同值、以 import 或常數對賬）；`python3 tools/walkthrough-baseline.py test` 三新案（離線樁）＋對真 stack `snapshot`／`diff` rc 0；`docs/ops/RUNBOOK.md` §9c 契約句改（五表、seed 模式、序列存在性；字面仍住工具常數）＋`python3 tools/docsync errata 三表` 復掃；`git update-index --chmod=+x` 不變

**Checkpoint（U3）**: 殘列不連坐、建構點單一、走查工具三改；rust-api commit＋外層工具 commit＋generate

### U4 狀態容器、門鈴、boot 與序列名冊（data-model §2.2／§5；research R5；BL-00072）

- [x] T016 ★主線擬稿即 accepted（brainstorm 既定不問 4、ADR-00027 翻案觸發器已預告）：`docs/arc42/decisions/ADR-000NN-appstate-five-to-seven-fields.md`（`supersedes: [ADR-00027]`、承 ADR-00032 形明列原意續行、決定＝加 `trust_model: Arc<TrustModel>`／`ip_rules: Arc<ArcSwap<RuleSet>>`）；`rust-api/server/src/state.rs` 5→7（封條「恰五欄」→「恰七欄、開第八欄須新 ADR」、保留域外欄邊界說明；編譯期窮舉解構錨測改七欄）＋★建構點全改（T014 後只剩 `test_kit` 構造點、`tests/common/mod.rs` `stub_state`、`main.rs`；`ip_rules` 測試預設空集、`trust_model` 預設全空）；accepted＋`generate` 同外層 commit。**DoD：既有 contract 16 case 仍綠**
- [x] T017 `rust-api/server/src/ipgate/mod.rs` 門鈴：`IPGATE_INVALIDATE_CHANNEL = "ipgate:invalidate"`（單一權威常數）＋`reload_and_publish(db, cache, rules)`（re-read `sys_ip_rule::load_active`→`build_ruleset`→成功才 `store`＋PUBLISH；失敗 keep-last-good 回 Err；PUBLISH 失敗／cache 缺席告警回 Ok；skipped 列逐筆告警）＋`spawn_ipgate_watcher(redis_url, db, rules)`（由 `config::redis_url()` 另開 `redis::Client`、`get_async_pubsub()` 帶 5 秒 timeout、斷線 backoff 1s→30s 上限、訂閱成功（含首次）後補一次 `reread_keeping_last_good`）。**DoD：真 redis 案先紅後綠——PUBLISH 後另一 handle 觀察到換版／reload 失敗保留上一份／訂閱失敗 backoff 不 hang（timeout 案以不可達位址）**
- [x] T018 `rust-api/server/src/main.rs` boot 接線：`config::trust_model_path()`→`load_trust_model`（告警逐筆 `tracing::warn!`＋`ip_domain_degraded_total` 對應 source）→`Arc<TrustModel>`；初載規則集（失敗→空集放行＋告警 `ruleset_initial_load`）→`Arc<ArcSwap<RuleSet>>`；`spawn_ipgate_watcher`；`AppState` 七欄；★BL-00072 靜態掃描案（`#[cfg(test)]` 以 `include_str!("main.rs")` 斷言 `assert_jwt_secrets_distinct` 恰一處、位於 `captcha_secret()` 之後、`Database::connect` 之前；`cache::connect` 同形；合成反例自證）＋`main.rs` 模組 doc「七鍵」與 `main.rs`／`config.rs` 之「七支 getter」數量字面同批改為現值（★`config.rs` 檔頭鍵集句已於 U1 改為九鍵；getter 現數以 `grep -c 'pub fn ' config.rs` 現算、RL-0011）＋★回填 `config.rs` 檔頭預告句「boot 呼叫點屬 004 刀 U4 T018 接線、該 task 同批回填本句」為現在式（RL-0015；U1 審查升級項）＋`python3 tools/docsync errata 七支` 復掃。**DoD：`up -d --wait` 後 `docker compose … logs rust-api | grep -E '信任模型|trust'` 見載入完成、零 WARN；`cargo build --release -p server` 可跑**
- [x] T019 [P] `rust-api/server/src/obs.rs` 序列名冊（data-model §5 逐字）：pre-register `ip_domain_degraded_total{source}` 八值（`trust_model_missing`／`trust_model_invalid`／`trust_model_set_cleared`／`ruleset_initial_load`／`ruleset_reload`／`doorbell_publish`／`doorbell_subscribe`／`request_context_absent`）＋`ipgate_blocked_total`（無 label）；`throttle_degraded_total` 七值本單元不動（U9 改十值）；檔頭「rev5 ipgate 計數器隨功能刀進場、本檔不帶」句改現在式。**DoD：render 文本含全部組合顯式 0、先紅後綠**

**Checkpoint（U4）**: 七欄容器、門鈴、boot 載信任模型與規則集；rust-api commit＋pin bump＋generate

---

## Phase 3: User Story 1 — 稽核紀錄記下真實來源與來源信心（P1）🎯 MVP（U5）

**Goal**: 中介層注入信任錨結果；login／refresh／logout 取上下文（缺席退路）；F7 登入拒絕與 F8 判定窗轉錄；稽核三欄如實。

**Independent Test**: quickstart §1／§1b——帶／不帶構造 XFF 之稽核列信心與 `peer_ip`；33 跳登入 403 且落 `chain_rejected` 列、非登入端點照常。

### Tests for User Story 1 ⚠️（先寫、先確認紅）

- [x] T020 [P] [US1] contract 增斷言於 `rust-api/server/tests/contract.rs`（contracts/wire-auth-delta.md）：`auth-login` 加 F7 案（`X-Forwarded-For` 33 跳→`5003 system.forbidden`／HTTP 403、先於 precheck）＋缺席退路兩腿（缺 `X-Real-IP`→5000／在場→照常）；`auth-refresh-token`／`auth-logout` 各加缺席退路轉錄腿一案；`observed_msgs` 不變（零新鍵）
- [x] T021 [P] [US1] integration 骨架於 `rust-api/server/src/middleware/mod.rs`／`request_context.rs`／`handler/auth/login.rs` 之 `#[cfg(test)]`：①經 make-service（`tower::ServiceExt::oneshot` 帶 `ConnectInfo`）之請求上下文三欄＋`peer_ip` 落 `sys_login_attempt` ②dev 二態（不帶 XFF→`fallback`／帶→`proxy_clean`）③溢出→登入 403＋一列 `chain_rejected`（`real_ip`＝判定腿結論〔經受信代理＝鏈推導之請求端位址、非 peer；勘誤同 T007、U5e 兌現〕、`success=false`）且該列帳號維計數排除、來源維納入（★釘住測試：來源維查詢刻意不過濾） ④非登入端點溢出照常服務、上下文帶標記 ⑤缺席退路：`from_headers` 轉錄腿信心 `fallback`、`peer_ip` NULL、判定窗空＋`request_context_absent` 計數遞增 ⑥判定窗轉錄與判定軌同一份切分（窗 >1024 字元退字元對齊尾段）

### Implementation for User Story 1

- [x] T022 [US1] `rust-api/server/src/middleware/mod.rs` 新建（★同批 `lib.rs` 加 `pub mod middleware;`）：`request_context_mw`（自 `ConnectInfo<SocketAddr>` 取 peer＋標頭 `X-Forwarded-For`／`X-CF-Verified`／各集合 `connecting_ip_header`→`trust::resolve_client_ip`＋兩覆蓋＋`apply_chain_overflow`→`RequestContext::from_trust(...)` 注入 extensions；`ConnectInfo` 缺席＝不注入＋warn＋`request_context_absent`）＋`CF_VERIFIED_HEADER` 常數；★`ip_gate_mw` 留 U6（本檔骨架預留 doc 一句）
- [x] T023 [US1] `rust-api/server/src/request_context.rs` 換血：新建構點 `from_trust(real_ip, decision_window, confidence, peer_ip)`；`x_forwarded_for` 改**判定窗**轉錄（最右 32 欄再以 `XFF_MAX_CHARS`＝1024 兜底、零 CR/LF；與 `trust::normalize_xff` 共用切分實作＝F8）；`ip_confidence` 八態字面（取自 `Confidence::as_str`）；新增 `peer_ip()` 取值器；★`from_headers` 保留為缺席退路（信心＝`Confidence::Fallback.as_str()`〔FR-007 單一出口、不得手寫字面〕、`peer_ip` None、判定窗空；`nginx_peer` 字面退役）；三欄私有＋`compile_fail` doctest 續存；模組頭「三欄與消費面不動」預告回填為現況（RL-0015）＋`python3 tools/docsync errata nginx_peer` 復掃（史料面不動）
- [x] T024 [US1] `rust-api/server/src/handler/auth/{login,refresh,logout}.rs` 取上下文改 `Option<Extension<RequestContext>>`（§5 ①）：缺席→`from_headers(&headers)` 退路＋結構化 warn＋降級計數；`ctx_absent` 就地記下（供 U9 來源維整層跳過）；★login 加 F7 拒絕腿（上下文信心＝`chain_rejected` ⇒ 先於形制閘②之後、precheck 之前：落一列 `sys_login_attempt`（`success=false`、三欄如實）→`5003`）；`record_attempt` 之 `LoginAttempt` 字面補 `peer_ip`；三處 `record_attempt(…, &ctx)` 呼叫點逐位元不變；fn doc 次序表改寫；★既有 36 處 `X-Real-IP` 注入案零改形自證（`git diff --stat` 測試模組零 hunk 除新增案）
- [x] T025 [P] [US1] `rust-api/server/src/model/facade/sys_login_attempt.rs`：`LoginAttempt` 加 `peer_ip: Option<IpAddr>` 欄＋insert 落欄；`count_recent_failures` 加 `AND ip_confidence IS DISTINCT FROM 'chain_rejected'`（碼註：`<>` 對 NULL 漏既有列）；`session_event.rs` 之 `source_ip`（既有 varchar(45)、無 `peer_ip`／`ip_confidence` 欄、零欄變更）改收信任錨 `real_ip` 字串（refresh／logout 經上下文取值器）；★`test_kit` `LoginAttempt` fixture 補欄（無 `Default` 之純欄位字面、建構點 grep 現算）
- [x] T026 [US1] `rust-api/server/src/router.rs` 掛 `request_context_mw` 為最外層（全路由含 `/health`／`/metrics`、先於 `enforce_mw`）；ROUTES 不變（16）；`mod tests` 之 middleware 掛載序自證（源序守：`request_context_mw` 之 `.layer(` 字面**後於** `enforce_mw` 兩處掛載、三子 router `.merge(` 與兩道 fallback 註冊——axum `Router::layer` 後掛者在外、且只包住呼叫當下已註冊者＝執行先於 `enforce_mw`）
- [x] T027 [US1] ★主線擬稿即 accepted（既定不問 2、`rev5:ADR 0043`）：`docs/arc42/decisions/ADR-000NN-chain-overflow-rejection-and-decision-window.md`（F7 標記全域拒絕限登入＋計數分流理由、F8 兩成立條件；provenance 引 ADR-00034 §二 F7／F8）；accepted＋`generate`
- [x] T028 [US1] 走查 quickstart §1／§1b；★走查三步：`python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-u5.json`（rc 0）→走查→`python3 tools/walkthrough-baseline.py restore --seed`→`diff` rc 0；rust-api commit→外層 pin bump＋generate（STATE）

**Checkpoint**: US1 完成——**MVP**：稽核列記下真實來源與來源信心；rev6 首次可見 `peer_ip`。

---

## Phase 4: User Story 2 — 超管以 IP 規則阻擋或放行特定來源（P2）（U6）

**Goal**: 存取閘六步判定、白＞黑＞預設放行、熱重載、keep-last-good；阻擋只作用請求層（Q1）。

**Independent Test**: quickstart §2——以 psql 直插 deny 列＋手動 PUBLISH 後構造來源得 403、另一來源 200、health 200；加 allow 反轉；被擋者既有 token 不撤、規則刪除即恢復。

### Tests for User Story 2 ⚠️

- [x] T029 [P] [US2] integration 於 `rust-api/server/src/middleware/mod.rs`／`ipgate/mod.rs` `#[cfg(test)]`（真 DB＋真 redis、`IpRuleRowsGuard`）：①六步判定序逐步一案（含 `/health`／`/metrics` 豁免、上下文缺席放行）②deny→403 信封 `5003 system.forbidden` 且 `ipgate_blocked_total` 遞增、結構化 warn 帶命中網段 ③同網段 allow＋deny→放行 ④豁免段 deny 仍放行 ⑤兩袋皆空放行 ⑥PUBLISH 後連續兩請求判定反轉（不重啟）⑦規則來源不可讀（暫改連線）→沿用上一份 ⑧★Q1：持有效 access 之來源被 deny 後 Authed 端點 403、`sys_token` 仍 active、規則刪除＋PUBLISH 後同 token 200

### Implementation for User Story 2

- [x] T030 [US2] `rust-api/server/src/middleware/mod.rs` 加 `ip_gate_mw`：①路徑 ∈ {`/health`, `/metrics`} 放行 ②extensions 無上下文放行（＋`request_context_absent`）③`state.ip_rules.load()`→`ipgate::decide(real_ip)`→Deny 即 `AppError::PermissionDenied`（5003／HTTP 403、零新碼）＋`ipgate_blocked_total`＋warn（`target: "security.ipgate"`、`matched_cidr`、`real_ip`、`ip_confidence`）；★不動會話、不寫 denylist（Q1 碼註）；★同批回填（RL-0015）：本檔檔頭「★預告（回填單元＝004 刀 U6 T030）」句改寫為現況、`obs.rs` 名冊註與 `request_context_mw` 缺席腿碼註之「存取閘腿落地後 3 格」改述現況；中介層缺席腿之 warn 訊息字面「不注入請求上下文」為 `router::tests` 掛載面探針之錨、不得改動或撞字
- [x] T031 [US2] `rust-api/server/src/router.rs` 掛載序：`request_context_mw`（最外）→`ip_gate_mw`→`enforce_mw`（Authed 路由）；`mod tests` 源序守擴為三支相對次序；ROUTES 不變
- [x] T032 [US2] 走查 quickstart §2（psql 直插 deny＋`PUBLISH ipgate:invalidate`＋curl 403／200／health＋Q1 token 案）；★走查三步（snapshot→走查→`restore --seed`＋手動 PUBLISH→`diff` rc 0）；rust-api commit→外層 pin bump＋generate

**Checkpoint**: US1＋US2 獨立可用——閘門擋得住、放得開、熱重載。

---

## Phase 5: User Story 3 — 超管在管理頁維護 IP 規則（P2）（U7 後端 → U8 前端）

**Goal**: 五端點＋防自鎖＋操作稽核首寫＋五鍵譯文（U7）；管理頁三檔＋新軌道＋兩支新閘＋HTTP 層轉譯（U8）。

**Independent Test**: quickstart §3（防自鎖零寫入）＋§6（CDP 全程、SC-010 結構清單對照 22080、403 譯文 toast）。

### Tests for User Story 3 ⚠️

- [x] T033 [P] [US3] contract case ×5 加入 `rust-api/server/tests/contract.rs` registry：`get-ip-rule-list`／`add-ip-rule`／`update-ip-rule`／`delete-ip-rule`／`restore-ip-rule`（wire 形＝contracts/wire-ip-rule.md；五條 Authed＋政策保護、含未認證三形 8888 案；缺上下文之寫端→5000 案）；`observed_msgs` 追加五鍵發出點
- [x] T034 [P] [US3] integration 於 `rust-api/server/src/handler/ip_rule.rs` `#[cfg(test)]`（真 DB、`IpRuleRowsGuard`＋`OpLogRowsGuard`、經中介層注入上下文）：①正規化落庫 ②衝突映 `biz.ipRule.conflict`（非 5000）③類型／CIDR 守門寫前拒零寫入 ④防自鎖四寫端各一（加入／移除舊加入新／移除 allow／復原）→`selfLock` 且規則列與稽核列皆零寫入 ⑤豁免段來源不判自鎖 ⑥上下文缺席→5000 零寫入 ⑦稽核列與業務列同交易（稽核失敗＝業務列零寫入） ⑧操作者名批次回填（多列一查、查無→null）⑨notFound 四形 ⑩寫端成功後判定面反轉（reload＋PUBLISH）

### Implementation for User Story 3（後端、U7）

- [x] T035 [P] [US3] `rust-api/server/src/model/audit.rs` 新建（`model/mod.rs` 加 `pub mod audit;`）：`AuditOperation` 五 variant（`Add`／`Update`／`Delete`／`Restore`／`Unlock`、`as_str` 單一宣告源）＋`AuditEvent{operator, operation, entity_table, entity_id, before, after}`＋`AuditOperator{uid, real_ip, peer_ip, ip_confidence}`（★自 `RequestContext` 組、缺席＝呼叫端 5000）；`rust-api/server/src/model/facade/sys_operation_log.rs` 新建：`write_in_txn(txn, event)`＋`write(conn, event)`（單寫、解鎖用）；`facade/mod.rs` 註冊（ASCII 升冪：`sys_menu`＜`sys_operation_log`＜`sys_role`）
- [x] T036 [US3] `rust-api/server/src/handler/ip_rule.rs` 新建（`handler/mod.rs` 加 `pub mod ip_rule;`）：`IpRuleListQuery`／`IpRuleRecord`（camelCase、`id` number＋2^53 守衛、`deleted` 導出、`deletedAt`／`deletedBy` 不上 wire）／三 Req DTO＋五 handler；`validate_wbip_type`／`normalize_cidr`／`guard_self_lock`（`ipgate::would_self_lock`、操作者 ip 取自上下文、缺席→5000）／`map_mutate_err`；四寫端＝txn 內業務列＋`sys_operation_log::write_in_txn`→commit→`ipgate::reload_and_publish`；清單操作者名以 `sys_user` facade 單次批次讀（`find_names_by_ids`、facade 補一支）
- [x] T037 [US3] `rust-api/server/src/router.rs` 加 5 條 ROUTES（`/systemManage/getIpRuleList` GET／`addIpRule` POST／`updateIpRule` POST／`deleteIpRule` DELETE／`restoreIpRule` POST；皆 Authed＋政策）＋`ROUTES_COUNT` 16→21＋`mod tests` 釘值 16→21（assert 訊息現在式）＋`tools/docsync/tests/test_references.py::TestRoutes::test_real_repo_pinned_rows` 真 repo 釘列增至 21（RL-0022）；主線 generate 後 `docs/generated/reference/routes.md` 21 列
- [x] T038 [US3] `MSG_KEYS` 13→18：`rust-api/server/src/error.rs` `pub mod msg_key` 加五常數（`BIZ_IP_RULE_INVALID_RULE_TYPE`／`INVALID_CIDR`／`CONFLICT`／`NOT_FOUND`／`SELF_LOCK`）＋`MSG_KEYS: [&str; 18]`＋名冊測試釘值 13→18；rust-api 四處 doc（`error.rs` 三處＋`handler/auth/alt_stub.rs` 一處）之「譯文權威＝003 契約」與手抄「13 鍵」改史料出處指針（Q3；`python3 tools/docsync errata 13 鍵` 復掃）；★base-web（T001 後）：`src/locales/langs/{en-us,zh-cn}.ts` 既有 `backend:` 圈界內補 `biz.ipRule.*` 五鍵（簡中重打字）＋`zh-tw.ts` 五鍵繁中＋`src/typings/app.d.ts` backend 型節五鍵（既有 (iii) 圈界內）；（★base-web 五處標記註解之權威句**與其手抄鍵數「13 鍵」**留 T063、本 task 只加鍵）；`python3 tools/msg-key-gate.py check` 綠＋一反（刪一鍵→rc 1→還原）
- [x] T039 [US3] 走查 quickstart §3（防自鎖零寫入、豁免段不判）；★走查三步（`restore --seed`＋PUBLISH→`diff` rc 0）；兩子庫 commit→外層一顆 commit 雙 pin bump（★msg-key-gate 兩側同批）＋generate（routes.md 21 列）

**Checkpoint（U7）**: 五端點與稽核首寫上線、五鍵齊；閘門有寫端可管。

### Implementation for User Story 3（前端、U8；★對 T001 硬序）

- [x] T040 [P] [US3] base-web `src/typings/api/rev6-ip-rule.d.ts` 新建（`// [rev6-inline BASE-WEB-ADAPT+ 004-ip-trust-anchor] …`；declaration merging 併入 `Api.IpRule`：`IpRuleRecord`／`IpRuleListQuery`／三 Req）＋`src/service/api/rev6-ip-rule.ts` 新建（WRAPPER、五支 `fetchGetIpRuleList`／`fetchAddIpRule`／`fetchUpdateIpRule`／`fetchDeleteIpRule`／`fetchRestoreIpRule`；不入 barrel；★解鎖不建）；★rust-api 側同批：`python3 tools/wire-schema.py extract`（base-web 容器）→`rust-api/server/tests/fixtures/wire-schema.json` 重抽＋`tests/wire_schema.rs` 補 `Api.IpRule.IpRuleRecord` 裁判 case＋`check` 綠
- [x] T041 [US3] base-web ★`BASE-WEB-MANAGE-PAGE-WIRING(i)`：`src/locales/langs/en-us.ts` 與 `zh-cn.ts` 各插 `route:` 樹一鍵 `'manage_ip-rule'` 與 `page:` 樹 `manage.ipRule` 子樹（鍵集＝rev5 HEAD `../fork260509-rev5/base-web/src/locales/langs/en-us.ts` 之 `page.manage.ipRule` 逐鍵重打字、本刀零增減）（兩語鍵集相等；各一塊新增型圈界 `[rev6-inline BASE-WEB-MANAGE-PAGE-WIRING(i)+ 004-ip-trust-anchor START/END]`）＋`src/typings/app.d.ts` `Schema.page.manage.ipRule` 型節（一塊新增型圈界）。**DoD：`pnpm typecheck` 在 T042 前紅（`RouteKey` 未含 `manage_ip-rule`）、T042 後綠**
- [x] T042 [US3] base-web 路由產物重算：新建 `src/views/manage/ip-rule/index.vue`（最小殼、T043 補實）後於 base-web 容器跑路由外掛重算（`pnpm` 腳本或 dev server 產出）⇒ `src/router/elegant/{imports,routes,transform}.ts`＋`src/typings/elegant-router.d.ts` 四支更新（`manage_ip-rule` 路由、`RouteKey`／`RouteMap`）；★禁手改；再跑一次重算 `git -C base-web diff --quiet` 四檔＝冪等
- [x] T043 [US3] base-web `src/views/manage/ip-rule/{index.vue,modules/ip-rule-operate-drawer.vue,modules/ip-rule-search.vue}` 依 rev5 HEAD 形重打字（檔頭新增型標記；含 `rev5:1597a671` B-099 修：表頭插槽外層 `v-show`＋內層 `v-if`、無權不退回共用元件備援鈕）：列表（欄位＝contracts 型別、id 降冪、操作者名）、三篩選、新增／編輯抽屜（類型二值、CIDR 校驗訊息、備註）、軟刪、回收桶頁內復原、四按鈕接 `hasAuth('ipRule:add'|'ipRule:edit'|'ipRule:delete'|'ipRule:restore')`、備註純文字插值、失敗 msg 經 `translateBackendMsg`。**DoD：`pnpm typecheck` 綠、`fork-delta-lint` rc 0、瀏覽器頁面可達、側邊欄標題譯文**
- [x] T044 [US3] base-web `src/service/request/index.ts` ★`BASE-WEB-I18N-WIRING(i)` 擴：onError 對「非業務碼分支但回應帶信封 `msg`」之 HTTP 錯誤（403／404）走 `translateBackendMsg(msg)` 顯示（新增型圈界第二塊；`rev5:B-117` 形）；無信封維持 axios 原文；既有被踢 modal／過期換發判斷零影響；demo 頁 `/auth/error` 4040 toast 同步變譯文（只驗、不動 demo 頁）。**DoD：`pnpm typecheck` 綠、CDP 帶 XFF 被擋時 toast 顯 `system.forbidden` 譯文**
- [x] T045 [P] [US3] `tools/view-render-guard.py` 新建（承 `rev5:tools/view-render-guard.py` 新寫；標準庫、零 docker）：掃 `base-web/src/views/manage/**` 零 `v-html`／`innerHTML`／`outerHTML`；rc 0/1/2/64＋`test`（植入反例必紅、正案綠、工作樹缺席 rc 2）；★接線四處：`.githooks/pre-commit` 新段（觸發 `-e 'base-web' -e 'tools/view-render-guard.py'`＝base-web pin bump 或工具本體 staged；★勘誤 2026-09-20：原文之 `-e 'base-web/src/views/manage/'` 於外層 hook 永不命中——外層 staged 面只看得到 `base-web` gitlink、子庫內路徑永不現身；沿既有碼面閘段形）＋`for` 自測名冊＋`tools/docsync/tests/test_hook_wiring.py` SEGMENTS＋`README.md` 樹＋`docs/ops/RUNBOOK.md` §12 碼面閘表一列（根據 ADR＝ADR-00034）；`git update-index --chmod=+x`；`python3 tools/docsync test`／`lint` 綠（GT-12 碼面閘表腿）
- [x] T046 [US3] `tools/route-artifact-gate.py` 新建（承 `rev5:tools/route-artifact-gate.py` 新寫；★於 T045 之後序列——四處名冊同檔）：①冪等＝於 base-web 容器重跑路由外掛重算後 `git -C base-web diff --quiet -- <四檔>`（無 node＝具名跳過、pre-commit 條件段）②名冊＝解析憲法 §III.2 `★BASE-WEB-MANAGE-PAGE-WIRING` 列範圍欄之產物檔集（`load_roster` 同源規則）與外掛實際產出檔集雙向差集即紅；`test`（手改一行即紅、漏列一支即紅）；接線四處同 T045（碼面閘表一列、pre-commit 段觸發 `-e 'base-web' -e 'tools/route-artifact-gate.py' -e '.specify/memory/constitution.md'`＝base-web pin bump、工具本體或憲法〔名冊來源〕staged；★勘誤 2026-09-20：同 T045、原文三條子庫內路徑永不命中；★重算一律容器內沙盒、不就地改工作樹＝pre-commit 並行 harness 各閘唯讀；「手改一行即紅」須以上游基線為種之重算腿承擔——外掛對 `routes.ts` 為增量合併、以版控為種重算時手改行會存活〔`rev5:tools/route-artifact-gate.py` 檔頭第③道〕）
- [x] T047 [US3] CDP 走查 quickstart §6（含 §2 之瀏覽器 403 譯文 toast）：`tools/orchestration/cdp.mjs` `send('Network.setExtraHTTPHeaders', …)` 構造公網來源；全程「列表→搜尋→新增正規化→編輯→軟刪→回收桶復原」；★SC-010 七項結構清單逐項對照 22080 同頁、視覺差異只記入 `tmp/004-u8-walkthrough.md`；兩支新閘自證（手改產物一行紅／植入 `v-html` 紅、還原綠）；★走查三步（`restore --seed`＋PUBLISH→`diff` rc 0）；兩子庫 commit→外層一顆雙 pin bump（★wire-schema 兩側同批：`rust-api/server/tests/fixtures/wire-schema.json`＋`base-web/src/typings/api/rev6-ip-rule.d.ts`）＋外層工具 commit 同顆＋generate

**Checkpoint（U8）**: US3 端到端可見——管理頁對照 22080 結構全等、兩支新閘上線。

---

## Phase 6: User Story 4 — 來源維登入節流生效＋節流判定每次由資料庫定案（P3）（U9）

**Goal**: 兩維並列合成、無 L1、每次嘗試讀設定現值＋PG 計數定案；越界／矛盾整組退；來源維不重置；L0 顯式放行跳節流。

**Independent Test**: quickstart §4——同來源輪換帳號名 11 次起要求驗證碼、50 次鎖；另一來源不受影響；穿插成功不重置；放寬門檻下一次即生效；越界 `ip_max_fails=0` 照常數判且 `ip_settings_default` 遞增。

### Tests for User Story 4 ⚠️

- [x] T048 [P] [US4] integration 於 `rust-api/server/src/throttle/mod.rs`／`model/facade/sys_login_attempt.rs`／`handler/auth/login.rs` `#[cfg(test)]`：①來源維三區（輪換帳號名仍計）②雙維合成四組合 ③★負向自證：穿插成功登入後來源計數不重置（誤加第三源即紅）④L0 顯式 allow 跳過、豁免段不跳 ⑤IPv6 `/64` 聚合＋mapped 折疊＋`unspecified` 無桶 ⑥★設定現值變異：鎖定後放寬硬門檻下一次即依新值（改為不讀現值即紅）⑦設定未變、最早失敗列出窗即解鎖無額外鎖期 ⑧越界（`max_fails=0`／`window_minutes=0`／`captcha_after=101`）與矛盾組合各整組退＋告警一筆、兩維 label 分流、相等合法 ⑨解鎖標記讀取 Err（壞 redis）→視為無標記＋`redis_down`（軟區停用、密碼錯仍計數）＋`unlock_marker_*` 遞增 ⑩任一維計數 DbErr→count 0＋`captcha_forced`＋`ip_db_count`／`db_count` ⑪上下文缺席→來源維整層跳過 ⑫★src 零 `throttle:lock:` 字面、零 `THROTTLE_LOCK_TTL_SECS`（grep 案）

### Implementation for User Story 4

- [x] T049 [US4] `rust-api/server/src/throttle/mod.rs` 重寫 `precheck`（research R6；簽名加 `source: Option<SourceInput{bucket: IpNetwork, explicit_allow: bool}>`、`None`＝缺席或無桶）：①讀兩維解鎖標記（帳號維鍵＋來源維鍵〔有桶且非顯式放行〕；任一 Err 或 `cache: None`→`redis_down`、該維視為無標記）②帳號維 `load_settings`（缺列／不可解析／★`validation::REGISTRY` 界值越界／矛盾→整組退 `5／15／2`＋`settings_default|settings_invalid` ≤1 筆）＋計數三源→硬鎖即 `biz.auth.locked`（短路）③來源維 `load_ip_settings`（同法、退 `50／15／10`、`ip_settings_*` label）＋`count_recent_failures_by_ip` 兩源 ④合成（任一軟區或 `captcha_forced`→captcha gate）；DbErr→`count := 0`＋`captcha_forced = !redis_down`；★刪 `THROTTLE_LOCK_TTL_SECS`／`lock_ttl_secs`／L1 GET／SET 與兩類 L1 測試；新常數 `DEFAULT_IP_MAX_FAILS = 50`／`DEFAULT_IP_WINDOW_MINUTES = 15`／`DEFAULT_IP_CAPTCHA_AFTER = 10`、`DIM_IP`／`ip_bucket`／`parse_unlock_marker`；`rust-api/server/src/cache/mod.rs` 刪 `throttle_lock_user_key`、加 `throttle_unlock_user_key(name)`／`throttle_unlock_ip_key(bucket)`＋`get_string` 既有；`python3 tools/docsync errata L1` 復掃（活書面留 U11）；★`rust-api/server/src/validation.rs` 開 `pub(crate) fn range_of(key: &str) -> Option<(i64, i64)>` 存取器供兩維 loader 取界值（`REGISTRY` 維持私有；RL-0070 可見性放寬、附消費者面斷言）
- [x] T050 [P] [US4] `rust-api/server/src/model/facade/sys_login_attempt.rs` 加 `count_recent_failures_by_ip(conn, bucket, window_minutes, unlock_marker)`：`WHERE real_ip <<= $1::inet AND success = false AND created_at > GREATEST(now() - make_interval(mins => $2), $3)`（★恰兩源、`$3` 無標記綁 NULL；刻意不加 `chain_rejected` 過濾）；走 `idx_login_attempt_ip_time`（`EXPLAIN` 記 report）；★釘住測試（FR-017、ADR-00037 決定 2）：一列 `chain_rejected` 被拒列 MUST 被本查詢計入其 `real_ip` 之桶（前置事實＝U5 之 facade 案與 login 拒絕腿案）；★同批把測試造窗 seed 之 `nginx_peer` 字面六處（`throttle/mod.rs` 兩處、`test_kit::seed_failures` 兩處、`tests/common/mod.rs` 兩處）改取八態字面（舊列並存面已由 facade 之 legacy 列案承載）；★同批裁定並回填（RL-0015）：`count_recent_failures` fn doc 預告之「④回退腿共桶界值面」——整鏈受信／錨左無可取時位址本就退成對端，被拒列與同代理後之正常登入失敗共用一桶；裁「維持現狀並於本查詢 doc 記明／改以 `peer_ip` 另計／對被拒列另設門檻」其一（涉 user 可見行為者先升主線），該預告句改述現況
- [x] T051 [US4] `rust-api/server/src/handler/auth/login.rs` 步驟②改呼新 `precheck`：`source`＝`ctx_absent`（U5 就地記下之 `_ctx_absent` 於本任務改名啟用）或無桶→`None`；`explicit_allow`＝`state.ip_rules.load().allow` 直讀 `contains(real_ip)`（★絕不經 `decide`）；fn doc 次序表改寫；`obs.rs` 引用之 `warn_degraded` 呼叫點對齊新名冊
- [x] T052 [US4] `rust-api/server/src/obs.rs` `THROTTLE_DEGRADED_SOURCES` 7→10（data-model §5 逐字：刪 `redis_lock`／`redis_lock_set`；加 `ip_settings_default`／`ip_settings_invalid`／`unlock_marker_user`／`unlock_marker_ip`／`ip_db_count`）＋pre-register 測試「恰十」＋doc「七值」→「十值」。**DoD：render 文本組合恰十、先紅後綠**
- [x] T053 [US4] ★主線擬稿即 accepted（BL-00066／Q7 user 拍板）：`docs/arc42/decisions/ADR-00038-throttle-decided-by-pg-every-attempt-no-negative-cache.md`（決定＝兩維無 L1、每次嘗試讀現值＋PG 定案、`redis_down` 由標記讀取立、越界整組退；棄案＝Amendment MAJOR、保留 L1 後備；provenance 引 `rev5:004` FR-028 翻案、ADR-00034 §二 島 E）；accepted＋`generate`
- [x] T054 [US4] 走查 quickstart §4（含 metrics 序列）；★走查三步（`restore --seed`→`diff` rc 0；redis `throttle*` 零鎖定鍵）；rust-api commit→外層 pin bump＋generate

**Checkpoint**: US1～US4 獨立可用——輪換帳號名的撞庫被來源維擋下；節流全由 PG 定案。

---

## Phase 7: User Story 5 — 超管手動解鎖被鎖的帳號或來源（P3）（U10）

**Goal**: 解鎖端點 API-only、稽核先於生效、未鎖冪等照寫（Q2）、畸形零稽核零狀態。

**Independent Test**: quickstart §5——來源維／帳號維解鎖後立即可再試；未鎖標的 0000 且稽核多一列；畸形 `invalidUnlockTarget` 零列；redis 只有 `*unlock*` 標記鍵。

### Tests for User Story 5 ⚠️

- [x] T055 [P] [US5] contract case `unlock-login`（POST／Authed＋政策）加入 `rust-api/server/tests/contract.rs`（含畸形→`2222 biz.throttle.invalidUnlockTarget` 案、未認證三形 8888、缺上下文→5000）；`observed_msgs` 追加第 19 鍵
- [x] T056 [P] [US5] integration 於 `rust-api/server/src/handler/throttle.rs` `#[cfg(test)]`（真 DB＋真 redis、`OpLogRowsGuard`）：①兩維各一案：鎖到硬門檻→解鎖→立即可再試（標記值＝unix 秒十進位字串、TTL 在）②畸形三形零稽核零狀態 ③稽核寫入失敗（暫壞 txn）→5000、標記不寫 ④★Q2：未鎖標的→0000、稽核多一列 `unlock`、標記寫入 ⑤上下文缺席→5000 ⑥源序守：`write` 稽核字面先於標記 `set_ex` 字面

### Implementation for User Story 5

- [x] T057 [US5] `rust-api/server/src/handler/throttle.rs` 新建（`handler/mod.rs` 加 `pub mod throttle;`）：`UnlockReq{dimension, userName, target}`＋`resolve_unlock_target`（`user`→帳號名原文、`ip`→`throttle::ip_bucket`；畸形→`invalidUnlockTarget`、先於一切）→上下文缺席→5000→`sys_operation_log::write`（`entity_table=login_throttle`、`entity_id=NULL`、`payload_after={dimension,userName,target}`；失敗→5000 中止）→該維標記 `set_ex(unix 秒十進位, 1440*60)`→`0000`；★不查鎖態、不 DEL 任何鍵（無 L1）；帳號維三件補齊之讀取端已於 T049 落、本 task 只核
- [x] T058 [US5] `rust-api/server/src/router.rs` 加 `/systemManage/unlockLogin`（POST／Authed＋政策）＋`ROUTES_COUNT` 21→**22**＋`mod tests` 釘值 22＋`tools/docsync/tests/test_references.py` 真 repo 釘列 22；主線 generate 後 `routes.md` 恰 22 列
- [x] T059 [US5] `MSG_KEYS` 18→**19**：`error.rs` 加 `BIZ_THROTTLE_INVALID_UNLOCK_TARGET`＋名冊釘值 19；★base-web 三檔 locale backend 子樹＋`app.d.ts` backend 型節各補第 19 鍵（既有圈界內）；`python3 tools/msg-key-gate.py check` 綠；`tests/contract.rs` 之 `msg_roster_every_key_has_an_emitter` 六鍵發出點齊（U7 五＋本刀一）
- [x] T060 [US5] 走查 quickstart §5；★走查三步（`restore --seed`→`diff` rc 0；redis 零 `*lock:*`）；兩子庫 commit→外層一顆雙 pin bump（★msg-key-gate 兩側同批）＋generate（routes.md 22 列）

**Checkpoint**: 全部功能 US 獨立可用——本刀功能面完成。

---

## Phase 8: User Story 6 — 憲法 Amendment、治理進場、測試基建與帳本落帳（P4）（U11）

**Goal**: T001 已凍結、U3 已改形、兩閘已上線；餘＝告警規則、RUNBOOK、ADR 譯文之家與已知態、活書 as-built、LESSONS 補述、BACKLOG 預告。

**Independent Test**: rules.yml 規則數 12 且 `ipgate-degraded` 錨對齊；`msg-key-gate` 綠；活書零 L1 敘述；`docsync errata` 逐詞零殘留。

### Implementation for User Story 6

- [ ] T061 [P] [US6] `deploy/grafana-provisioning/alerting/rules.yml`（BL-00078）：刪 `obs016-throttle-suppressed` 規則塊＋②註解＋檔頭「告警六組 13 條」→12 與「LogQL 形（②③b③d）」「fields_suppressed」兩處；`obs016-ipgate-degraded` 錨與查詢欄位改 `ipgate/mod.rs`／`middleware/mod.rs`／★`main.rs`（`report_trust_load_warnings`）as-built（`target`／`degraded` 欄名；★boot 端信任模型降級 log 之 target＝`security.trust`、規則須一併涵蓋＝U4 升級項）；`python3 tools/docsync errata throttle-suppressed`／`errata suppressed_breadcrumb` 復掃（史料面不動）
- [ ] T062 [P] [US6] `docs/ops/RUNBOOK.md` §16 部署 checklist 實文（FR-066：CDN 邊緣網段填法與更新節奏／信任模型樣例＝contracts/trust-model-config.md prod 段、dev 實掛為基底／nginx `geo` 與 TOML 兩處同步義務與 `cdn_mismatch` 表徵／「鎖定來源站」降為縱深防禦建議／快速登入鈕 prod 前拆除指針 BL-00049；「隨對應刀補實文」句改實文）＋§12 工具鏈速查 walkthrough 列（seed 模式）＋檔頭章節現況句；`README.md` tools 樹核（T045／T046 已加）
- [ ] T063 [US6] ★主線擬稿即 accepted（brainstorm Q3 user 拍板）：`docs/arc42/decisions/ADR-00039-msg-translation-home-three-locale-files.md`（`supersedes: [ADR-00029]`、承 ADR-00032 形：ADR-00029 決定 N 原意續行、只改譯文權威句＝三檔 backend 子樹各為該語權威、現在式引用改指本檔）；★九處註解改指針（base-web 五處標記註解：`en-us.ts`／`zh-cn.ts`／`zh-tw.ts`／`request/index.ts`／`app.d.ts` 之「權威＝003 契約」句；rust-api 四處 doc 已於 T038 改、本 task 核）；`python3 tools/docsync errata msg-keys.md` 復掃現在式面零殘留；accepted＋`generate`；兩子庫 commit→外層雙 pin bump；★U8 回填：`base-web/src/locales/langs/zh-cn.ts` backend 圈界內既有一行不合 oxfmt（003 刀遺留、U8 implementer-1 發現而該面在其限定外未動）——本條改該檔標記註解時同批以 formatter 修正
- [x] T064 [US6] ★主線擬稿即 accepted：`docs/arc42/decisions/ADR-00040-ip-domain-known-states.md`（本刀已知態集＝解鎖無 UI 按鈕／dev 經反向代理可達二態／稽核覆蓋不對稱／logout 故障窗弱 oracle〔Q5、won't-fix〕／redis 持久化重評維持不開／wire 裁判面嚴格模式重評維持不動〔rev6 零 `additionalProperties`〕；各附論證與翻案觸發器）；accepted＋`generate`
- [ ] T065 [P] [US6] 活書 as-built（feature branch 內、現在式；FR-068）：`docs/arc42/05-building-block-view.md`（`trust`／`ipgate`／`middleware` 三模組、handler 兩檔、facade 三支）／`06-runtime-view.md` §6（新增「信任錨與 IP 存取閘——島 F」情境；改寫「登入失敗節流——島 E」為兩維無 L1；frontmatter「信任錨與 IP 存取閘：隨刀」→「承襲」）／`08-crosscutting-concepts.md`（§8 API 慣例 ROUTES 22、msg 名冊權威＝三檔 locale；fork-delta 五軌道 as-built）／`10-quality-requirements.md` §10.2（島 F 品質情境、島 E 情境改寫）／`11-risks-and-technical-debt.md`（`auth_limit` 列之「來源維與信任錨還原不在本 crate」句改現在式；已知態指 ADR）／`12-glossary.md`（信任錨、來源信心〔與 AI「信心規格」區分〕、來源信心態 `fallback`〔與流程層 fallback 區分、兩詞不互用〕、來源維、結構豁免、判定窗、計數桶、顯式放行、解鎖標記、防自鎖；「節流三區」列刪 L1、「鎖定」列改寫；「存取閘」立條目、「閘門／IP 閘」為同義註）／`01`／`03`／`10` 之 L1 敘述；`python3 tools/docsync errata 負快取`／`errata L1`／`errata 無解鎖端點` 復掃；`generate`（`rev5-blueprint-map.md` 重算）；★U9 回填（主線 errata 枚舉、`python3 tools/docsync errata "負快取"`／`"七源"`／`"redis_lock"`／`"throttle:lock"` 復掃）：活書仍載 L1 與降級七源之處＝`06` frontmatter 節流列與 §6.1 節流情境表（參與者列、③ precheck 四步、⑤降級七源、守門列）、`12` 詞彙「節流三區」「鎖定」「降級（基礎設施）」三列、`10` 節流量測列之「七源」、`11` 風險表節流列、`05` rust-api 模組枚舉之「七源統一出口／鍵 builder 六字面／帳號維唯一」——皆隨本條改為兩維＋PG 定案＋十源＋七支鍵 builder 之現況；★U10 回填：`05` handler 名冊「九檔」→十檔（新增 `throttle.rs`）、`12`「無解鎖端點」句改述為 API-only 端點在位（按鈕＝ADR 已知態）
- [ ] T066 [P] [US6] 帳本：`docs/ops/LESSONS/LL-00017-*.md` 補述 G6 結構解（廢除守衛、水位清理、序列存在性口徑；引 LL-00022）；`docs/ops/BACKLOG.md` 收刀預告——`backlog_done` 八條（BL-00058／00062／00066／00070／00072／00075／00077／00078）刪列於簿記；條文改寫五條（BL-00028 刪 `throttle::load_settings` 半句／BL-00031 刪 `ip_*` 臂／BL-00042 刪②／BL-00043 只剩 access 面／BL-00045 刪 ip-rule 頁）本 task 落；`backlog_add` 兩條（解鎖按鈕＋前端包裝待使用者管理頁刀／全域 wire i64 守衛 lint `rev5:B-111` 同形；配號於檔頭 next）本 task 落；一坑一檔候選（實際踩到者才立）；`docs/ops/NOTES.md`「下一步」→005 之文字於收刀簿記改

**Checkpoint（U11）**: 治理面齊、活書現在式、帳本預告落；外層 commit（含雙 pin）＋generate

---

## Phase 9: Polish & Cross-Cutting Concerns（DoD 收攏；U12）

- [ ] T067 CDP 端到端走查全程（quickstart §0 snapshot→§1～§6 逐節→§7 收尾：`restore --seed`＋手動 PUBLISH＋`diff` rc 0＋三閘綠）；走查腳本住 `tmp/`（import `tools/orchestration/cdp.mjs`、`setExtraHTTPHeaders`）；SC-014 四項與 SC-010 七項結果記 `tmp/004-u12-walkthrough.md`；走查後容器內全量測試仍綠（SC-013）
- [ ] T068 全量閘綠（spec FR-070 逐條）：容器內 `cargo test --workspace -- --test-threads=1`＋`cargo fmt --all --check`＋`cargo build --release -p server`＋release 二進位 `/health`＋`pnpm typecheck`＋`python3 tools/fork-delta-lint.py`＋`python3 tools/msg-key-gate.py check`＋`python3 tools/wire-schema.py check`＋`python3 tools/view-render-guard.py check`＋`python3 tools/route-artifact-gate.py check`＋`python3 tools/schema-gate.py check`＋`python3 tools/entity-drift-gate.py check`＋`python3 tools/docsync test`／`check`／`lint`＋routes.md 22 列＋contract coverage 負向（抽一 case→紅→還原；殭屍 case→紅→還原）；SC-001～SC-015 逐條對照（SC-016 收刀面於簿記後驗）＋US1～US6 驗收場景→測試案或演練紀錄對照表（函式名＋案序）記 report
- [ ] T069 反例四組（★T068 後序列、暫改主檔不與全量閘並行；RL-0005 每項還原後 porcelain 零差異）：①`tools/fork-delta-lint.py` 對新軌道列變異（暫改 `.specify/memory/constitution.md` 該列一路徑→紅→還原；T001 已做、復跑）②`tools/view-render-guard.py`／`tools/route-artifact-gate.py` 各一反（植入 `base-web/src/views/manage/ip-rule/index.vue` `v-html`／手改 `base-web/src/router/elegant/routes.ts` 一行→紅→還原；T047 已做、復跑）③`rust-api/server/tests/serve_connect_info_lint.rs` 對 `rust-api/server/src/main.rs` 暫拔 `into_make_service_with_connect_info`→紅→還原④BL-00072 靜態掃描對 `rust-api/server/src/main.rs` 合成反例（暫移 `assert_jwt_secrets_distinct` 位置）→紅→還原；結果記單元 commit 訊息
- [ ] T070 perf 事件：pre-commit 全鏈實測（含兩新閘段、雙 pin bump 觸發全段）≤45s → `docs/ops/events.jsonl` append `precommit_chain`；容器冷編時長記 commit 訊息（不入 DoD）

---

## 執行單元對映（承 research R10、依 US 交付面重切；主線派發粒度、每單元一顆外層 commit；冒煙 token 取單元名形 `u<N>-<slug>-<4hex>`、不可取 `test`）

「允許檔案清單」欄＝該單元 agent **唯一可寫面**（逐字抄成 `ALLOWED_BLOCK` 常數；★＝註冊檔或連動釘值檔、漏列即 fix agent 撞牆）；**GENERATED_FILES 成員一律不入清單、由主線六步序⑤ generate 帶入**；「限定式」項只准為還原式演練暫改、每項還原後 porcelain 零差異（RL-0005）。

| 單元 | 任務 | 允許檔案清單（起始） | 收尾產物 |
|---|---|---|---|
| U0 主線 | T001、T002 | `docs/arc42/decisions/ADR-00034-*.md`、`.specify/memory/constitution.md`、`README.md`（憲法版本鏡像行） | 憲法 1.4.0 獨立 commit＋generate |
| U1 | T003（主線）、T004～T008 | `rust-api/Cargo.toml`、`rust-api/server/Cargo.toml`、`rust-api/Cargo.lock`（機器重算）、`server/src/config.rs`、`server/src/trust/mod.rs`、★`server/src/lib.rs` | ADR ⑥ 外層 commit；rust-api commit→pin bump＋generate |
| U2 | T009～T012 | `server/src/ipgate/mod.rs`、★`server/src/lib.rs`、`server/src/model/facade/{sys_ip_rule,mod,test_kit}.rs`、`server/tests/serve_connect_info_lint.rs`、★`server/tests/entity_access_lint.rs` | rust-api commit→pin bump |
| U3 | T013～T015 | `server/src/model/facade/test_kit.rs`、69 處掛載檔（`grep -rln SequenceResetGuard rust-api/server` 現算、10 檔）、★`server/src/router.rs`（僅 `mod tests`）、★`server/src/auth/enforce.rs`（僅 `mod tests`）、★`server/src/handler/{system_settings,route,captcha}.rs`（僅測試模組）、`server/src/obs.rs`（僅測試模組）、`server/tests/common/mod.rs`、`tools/walkthrough-baseline.py`、`docs/ops/RUNBOOK.md`（§9c） | rust-api commit→pin bump＋外層工具 commit＋generate |
| U4 | T016（主線 ADR）、T017～T019 | `docs/arc42/decisions/ADR-000NN-appstate-*.md`、`server/src/state.rs`、`server/src/ipgate/mod.rs`、`server/src/main.rs`、`server/src/config.rs`（檔頭數量字面）、`server/src/obs.rs`、`server/src/model/facade/test_kit.rs`（構造點）、`server/tests/common/mod.rs` | ADR 外層 commit；rust-api commit→pin bump＋generate |
| U5（US1） | T020～T028（T027 主線） | ★`server/tests/contract.rs`、`server/src/middleware/mod.rs`、★`server/src/lib.rs`、`server/src/request_context.rs`、`server/src/handler/auth/{login,refresh,logout}.rs`、`server/src/model/facade/{sys_login_attempt,session_event,test_kit}.rs`、★`server/src/router.rs`（掛載＋源序守） | ADR 外層 commit；rust-api commit→pin bump＋generate |
| U6（US2） | T029～T032 | `server/src/middleware/mod.rs`、`server/src/ipgate/mod.rs`（測試模組）、★`server/src/router.rs`、`server/src/obs.rs`（僅發射點） | rust-api commit→pin bump＋generate |
| U7（US3 後端） | T033～T039 | ★`server/tests/contract.rs`、★`server/src/router.rs`、★`tools/docsync/tests/test_references.py`、`server/src/model/{audit,mod}.rs`、`server/src/model/facade/{sys_operation_log,sys_user,mod}.rs`、★`server/src/handler/{mod,ip_rule}.rs`、`server/src/error.rs`、`server/src/handler/auth/alt_stub.rs`（僅 doc 一處）、★**i18n 四處**＝`base-web/src/locales/langs/{en-us,zh-cn,zh-tw}.ts`＋`base-web/src/typings/app.d.ts`（既有檔、僅 backend 節；★T001 後） | 兩子庫 commit→外層一顆雙 pin bump（msg-key-gate 兩側同批）＋generate（routes.md 21） |
| U8（US3 前端；★T001 硬序） | T040～T047 | `base-web/src/typings/api/rev6-ip-rule.d.ts`、`base-web/src/service/api/rev6-ip-rule.ts`、`base-web/src/views/manage/ip-rule/`（三檔）、`base-web/src/locales/langs/{en-us,zh-cn}.ts`（route／page 兩樹）、`base-web/src/typings/app.d.ts`（page 型節）、`base-web/src/router/elegant/{imports,routes,transform}.ts`＋`base-web/src/typings/elegant-router.d.ts`（★產物、只由重算產出）、`base-web/src/service/request/index.ts`、`tools/{view-render-guard,route-artifact-gate}.py`、`.githooks/pre-commit`、`tools/docsync/tests/test_hook_wiring.py`、`README.md`、`docs/ops/RUNBOOK.md`（§12 兩列）、★`rust-api/server/tests/{wire_schema.rs,fixtures/wire-schema.json}` | 兩子庫 commit→外層一顆雙 pin bump（wire-schema 兩側同批）＋工具 commit 同顆＋generate |
| U9（US4） | T048～T054（T053 主線） | `server/src/throttle/mod.rs`、`server/src/cache/mod.rs`、`server/src/model/facade/{sys_login_attempt,test_kit}.rs`、`server/src/handler/auth/login.rs`、`server/src/obs.rs`、`server/src/validation.rs`（僅 `range_of` 存取器）、`docs/arc42/decisions/ADR-000NN-throttle-*.md` | ADR 外層 commit；rust-api commit→pin bump＋generate |
| U10（US5） | T055～T060 | ★`server/tests/contract.rs`、★`server/src/router.rs`、★`tools/docsync/tests/test_references.py`、★`server/src/handler/{mod,throttle}.rs`、`server/src/error.rs`、`server/src/cache/mod.rs`、★**i18n 四處**（僅 backend 節） | 兩子庫 commit→外層一顆雙 pin bump（msg-key-gate 兩側同批）＋generate（routes.md 22） |
| U11（US6） | T061～T066（T063／T064 主線） | `deploy/grafana-provisioning/alerting/rules.yml`、`docs/ops/RUNBOOK.md`、`README.md`、`docs/arc42/decisions/`（兩 ADR）、`docs/arc42/{01,03,05,06,08,10,11,12}-*.md`、`docs/ops/LESSONS/LL-00017-*.md`、`docs/ops/BACKLOG.md`、base-web 五處標記註解（`locales/langs/{en-us,zh-cn,zh-tw}.ts`／`service/request/index.ts`／`typings/app.d.ts`、僅註解行） | ADR 兩筆外層 commit；base-web commit→pin bump；外層 docs commit＋generate |
| U12 收攏 | T067～T070 | `tmp/`（走查腳本、紀錄、基準檔）、`docs/ops/events.jsonl`、限定式：`rust-api/server/tests/contract.rs`（coverage 負向演練）、`base-web/src/router/elegant/routes.ts`／`views/manage/ip-rule/index.vue`（兩閘反例）、`rust-api/server/src/main.rs`（B-075／BL-00072 反例）——皆當場還原 | 外層 commit＋generate；final holistic review 輸入 |

★**修單單元 U5e**（非 T 條目；U5 規格審查實暴；已收）：`apply_chain_overflow` 改回只改信心、位址沿判定腿結論（`trust/mod.rs`＋`middleware/mod.rs` 呼叫端＋login／facade 測試期望值與碼註）；排在 U5 之後、T028 走查與 U6 之前。

★**派發序**（依相依）：U0→U1→U2→U3→U4→U5→U5e→U6→U7→U8→U9→U10→U11→U12。純後端 U1～U6、U9 不受 U0 硬閘（可於 T001 親決前先行）；★U7（locale backend 五鍵）、U8、U10（第 19 鍵）、U11（註解）對 U0 硬序。
★**單元序不可並發的共用檔**：`router.rs`／`contract.rs`／`test_references.py`（U7／U10 加列並 bump 同一 `ROUTES_COUNT` 與釘值列；U5／U6 掛載序）、`middleware/mod.rs`（U5 建、U6 加閘）、`ipgate/mod.rs`（U2 核、U4 門鈴）、`login.rs`（U5 上下文＋F7、U9 precheck 呼叫）、`error.rs`＋i18n 四處（U7 五鍵、U10 一鍵）、`obs.rs`（U4 ip_domain、U9 throttle 十值）、`test_kit.rs`（U2／U3／U4／U5／U9 遞進）——⇒ US 的「獨立可驗收」成立於交付面、不成立於單元併發面。
★**每單元邊界主線動作**（六步序、不入 agent 清單）：①復核 report（逐項 grep、`errata` 復掃）→②load-bearing 自驗（容器內 rc＋`docsync lint`）→③落帳（BACKLOG／LESSONS／tasks 勾選／ADR）→④子庫 commit→⑤`git add <子庫>`→`generate`→`git add` 生成物→⑥外層 commit（pin bump）→派下一支前逐條問「它 import／呼叫／宣告的東西存在嗎」。

## Dependencies & Execution Order

- **Phase 1**：T001（★硬閘、user 親決）／T002 可先於 T001。
- **Phase 2**：U1（T003→T004→{T005、T006 可分派}→T007→T008）→U2（{T009、T010、T011 可分派}→T012）→U3（T013→{T014、T015 可分派}；★T014 待 T013 因同動測試模組）→U4（T016→T017→T018；T019 可與 T017 分派；T018 待 T017／T019）。
- **Phase 3～7**：皆依 Phase 2；實作序照 US1→US2→US3（後端→前端）→US4→US5（共用檔遞進、不可並行）；U7／U8／U10 另依 T001。U5 內序：T020／T021 可分派→T022→T023→{T024、T025}→T026→T027（主線）→T028。U6：T029→T030→T031→T032。U7：T033／T034 可分派→T035→T036→T037→T038→T039。U8：T040／T045 可分派（rust 側 wire-schema 重抽於 T040）；T046 待 T045（名冊四檔）；T041→T042→T043→T044→T047。U9：T048→T049→{T050、T052 可分派}→T051→T053（主線）→T054。U10：T055／T056 可分派→T057→T058→T059→T060。
- **Phase 8**：T061／T062／T065／T066 可分派；T063／T064 主線；U11 硬依 U10（活書 ROUTES 22、msg 名冊 19）。
- **Phase 9**：依全部；T067→T068→T069→T070 全序列（T069 暫改主檔、不與 T068 並行）。
- 阻斷型：T004 容器內 build 紅＝blocked 升主線；T017 訂閱 timeout 案需 redis 容器在跑；T042 需 base-web 容器與路由外掛可跑；T047／T067 需 host 瀏覽器 9229；任一單元需動允許檔案清單外檔案＝依防呆④分值升級、絕不擅改。

## Parallel Opportunities（逐 US；[P]＝檔域不相交可分派、cargo 序列）

- **U1**：T005／T006 可分派（config vs trust）。**U2**：T009／T010／T011 三支主體檔可分派（`lib.rs`／`facade/mod.rs` 註冊行序列化）。**U3**：T014／T015 可分派。**U4**：T017／T019 可分派。
- **US1（U5）**：T020／T021 測試骨架可分派；T025 facade 與 T022～T024 中介層／handler 可分派；`router.rs` 由單一 implementer 收邊。**US2（U6）**：序列。
- **US3（U7）**：T033／T034 可分派；T035 model 與 T036 handler 序列（facade 先）；T038 之 rust 側與 base-web 側可分派、同顆外層 commit。**US3（U8）**：T040／T045 可分派、T046 待 T045；locale→重算→頁面→轉譯序列。
- **US4（U9）**：T048 先；T050／T052 可分派；T049→T051 序列。**US5（U10）**：T055／T056 可分派；T057→T058→T059 序列。
- **U11**：T061／T062／T065／T066 可分派；T063／T064 主線。**U12**：全序列 T067→T068→T069→T070。

## Parallel Example: User Story 3（後端 U7）

```text
# facade sys_ip_rule 已於 U2 就位、OpLogRowsGuard 已於 U3 就位；U7 內可分派（檔域不相交；cargo 序列）
Task: "T033 contract case ×5 in rust-api/server/tests/contract.rs"
Task: "T034 integration 骨架 in rust-api/server/src/handler/ip_rule.rs #[cfg(test)]"
Task: "T035 model/audit.rs＋facade/sys_operation_log.rs"
# handler/ip_rule.rs（T036）→ router.rs（T037）→ error.rs＋i18n 四處（T038）由單一 implementer 序列收邊
```

## Implementation Strategy

- **MVP**＝Phase 1＋Phase 2（U1～U4）＋US1（U5）：稽核列記下真實來源與來源信心、`peer_ip` 首次落欄、鏈超長拒絕＝rev6 IP 域第一次端到端可見（quickstart §1／§1b）。
- 增量：US2（存取閘）→US3（端點＋頁）→US4（來源維節流、無 L1）→US5（解鎖）→US6（治理）→Polish；每單元收尾六步序；review／fix 烤入 RULES scope 塊（RULES-VERSION 不變＝`a2721b391067`）。
- 收刀（★不在本清單）：final holistic review → `superpowers:finishing-a-development-branch`（push／merge 需 user 同意）→ 收刀簿記三步（`feature_close` window 4：`adrs` 七筆、`backlog_done` 八條、條文改寫五條、`backlog_add` 兩條；NOTES 下一步→005；generate）→ `close_bookkeeping` perf 第四步。

## Notes

- [P]＝檔域不相交可分派；★cargo 執行一律序列。
- 測試先確認紅再實作；每 task 或邏輯群組後 commit（子庫 commit→外層 bump pin）。
- 任一 checkpoint 皆可停下獨立驗收該 US。
- 避免：跨 US 破壞獨立性、同檔並行、在 T001 accepted 前動 base-web 既有檔（含 locale backend 節）、單側 pin bump 讓兩側閘分叉、以 `decide` 判 L0 顯式放行（違 F5）、把 `SequenceResetGuard` 帶回、走查後忘了手動 PUBLISH（TRUNCATE 不按門鈴）。
