# Implementation Plan: 004 IP 域整批——信任錨還原真實來源、IP 存取閘、來源維節流、IP 規則管理頁、管理員解鎖

**Branch**: `004-ip-trust-anchor` | **Date**: 2026-09-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-ip-trust-anchor/spec.md`（clarify Q1～Q3 定案 2026-09-15）＋`docs/brainstorms/004-ip-trust-anchor.md`（拍板 BL-00066／BL-00078／Q1～Q7／G1～G7、§5 十項定案、工程判斷 1～13、設計十節）＋`rev5:004-ip-trust-anchor` 全套（唯讀）

## Summary

把「三端備好、中間沒接」的 IP 域接通：八態信任錨（三層＋兩覆蓋＋F6 硬化＋F7 溢出拒絕＋F8 判定窗轉錄）→ IP 存取閘（六步判定、any-match 白＞黑＞預設放行、ArcSwap 判定面、門鈴熱重載、keep-last-good）→ 來源維登入節流（與帳號維並列合成；★兩維皆無快取層負快取、每次嘗試讀設定現值＋PG 滑動窗定案＝BL-00066／Q7；設定壞值含越界整組退＝G4）→ IP 規則管理五端點＋管理頁（防自鎖 fail-closed、操作稽核首寫）→ 管理員解鎖端點（API-only、稽核先於生效、未鎖冪等照寫）。ROUTES 16→22、`AppState` 5→7、`MSG_KEYS` 13→19；零 migration、零 seed 變更（research R12-1）。
技術路徑＝高度參照 `rev5:004` 終態碼（R2 逐檔清單、R3 二十三筆 rev6 差異點＋防回歸清單 B 十一筆），三支新依賴依 R1 三源表定版（G7）。同一筆 MINOR Amendment（ADR-00034 draft 已落、proposed）開 §I.7 島 F（F1～F8）＋島 E 四處細項＋§III.2 `★BASE-WEB-MANAGE-PAGE-WIRING` (i)＋I18N-WIRING (ii) 權威句與 (i) 對齊＋五欄範圍實數化——tasks 首個主線任務 user 親決凍結、accepted 前不得動 base-web 既有檔。治理面同刀：兩支新碼面閘、走查工具三改、`SequenceResetGuard` 廢除（G6）、BL-00070 七處收攏、rules.yml 死規則刪除、boot 靜態守、契約增量三檔＋治理契約。

## Technical Context

**Language/Version**: Rust 1.96.1（edition 2024、容器內 build／test 全程 serial）＋TypeScript 6.0.3／Vue 3.5.34（base-web：7 支既有檔新增型圈界＋4 支產物檔重算＋5 支新檔、`pnpm typecheck`）＋Python 3 標準庫（兩支新碼面閘、走查工具改、docsync tests／hook 接線守衛擴充）

**Primary Dependencies**: 新進三支（G7 user 拍板 2026-09-15）——arc-swap **1.9.2**／futures-util **0.3.34**（`default-features = false`）／toml **1.1.6**（雙源表＝research R1；零新 redis feature flag）；既有 axum 0.8.9（`ConnectInfo<SocketAddr>` 首次消費）、sea-orm 1.1.20（`IpNetwork` 經 prelude）、redis 1.7.0（pub/sub 專用 `Client`）、tokio 1.53.1、metrics 0.24.6

**Storage**: PostgreSQL 18.4（001 基線；`sys_ip_rule` 首寫者、`sys_operation_log` 首寫者、三稽核表 `ip_confidence` 值域擴八態零 DDL、`ip_*` 三鍵首消費者；零 migration）＋Redis（DB 0；門鈴 pub/sub 頻道 `ipgate:invalidate`＋兩維解鎖標記＋既有 captcha 標記；★刪鎖定鍵族；不開 AOF＝已知態）；rev6 stack 埠 35432／36379

**Testing**: cargo test 三層（`trust` 純函式全態矩陣／oneshot contract 22 case＋覆蓋閘＋wire-schema 裁判／真 DB＋真 redis integration 掛既有守衛、★`SequenceResetGuard` 廢除後水位形）；`--test-threads=1` 容器內；兩支 lint（`serve_connect_info_lint`＝B-075、boot 靜態掃描＝BL-00072）；python 工具自帶 `test`（兩新閘 self-test、走查工具三新案、docsync test hook 接線）；前端零測試框架＝`pnpm typecheck`＋兩段 review＋CDP 對照 22080（SC-010 結構清單）；quickstart 經 front-nginx 真 HTTP 走查（構造 XFF）＋走查前後基準 diff rc 0（seed 模式）

**Target Platform**: Linux 容器（compose project `rev6-admin`；host＝WSL2、/mnt/d drvfs 跑過 compose 後同 shell 重新 `cd`；CDP 由 host 瀏覽器 9229）

**Project Type**: web-service（rust-api server crate 擴編：三新模組 `trust`／`ipgate`／`middleware`＋兩新 handler 檔＋三新 facade＋`model/audit`＋throttle 重寫＋上下文換血）＋前端接線（base-web 新軌道 7 支既有檔＋既有 I18N 三用途＋5 新檔）＋憲法 Amendment＋治理工具（兩新閘、一隨遷工具改、七 ADR）

**Performance Goals**: 無業務量化目標（dev workspace）。紀律面：①判定面每請求零資料庫零快取查詢（ArcSwap 讀）②來源維計數 SQL 必帶窗下界（`idx_login_attempt_ip_time` range scan 有界）③轉發鏈先取右端視窗再解析（解析成本上界鎖死）④鎖中每發成本＝帳號維 4 支 PG 查詢（＋來源維 4 支）、零 argon2 零落列、上界＝nginx `auth_limit` 5r/s burst 40（brainstorm 風險 3、已知態）；pre-commit 全鏈 ≤45s 警戒（兩新閘秒級）

**Constraints**: 零 migration／零 seed／13 碼矩陣零觸碰且零新變體／Amendment 硬序（accepted 前不動 base-web 既有檔、含 locale backend 六鍵）／§I.5 rev5 參照紀律（重打字＋註解重寫＋R3 兩份防回歸清單）／§III fork-delta 三元組（新軌道全新增型圈界＋產物檔紀律）／runtime-append 四表序列不復位／redis 鍵 uniq 前綴／review 只讀／rev5 樹唯讀、rev5 stack 絕不指向／TDD 發射前模型分派向 user 確認（當前指示＝opus5 1m xhigh）

**Scale/Scope**: 22 routes（6 新）／9 AppError 變體（0 新）／19 msg keys（6 新）／6 設定鍵消費（3 新消費者）／AppState 七欄／八態信心＋六段結構豁免／降級序列 `throttle_degraded_total` 10 值＋`ip_domain_degraded_total` 8 值＋`ipgate_blocked_total`／server crate 新增約 12 檔（rev5 對應終態 IP 域約 1.5 萬行含測試、生產段約四成）／base-web ★軌道既有檔 7（3 新增型圈界＋4 產物）＋既有 I18N 3 用途 4 檔＋5 新檔／憲法 +1 軌道 +1 島 +4 細項 +5 欄實數／ADR 7／BACKLOG done 8＋改 5＋add 2／執行單元 13（U0～U12；派發真源＝tasks.md 執行單元對映、承 research R10 依 US 交付面重切）

## Constitution Check

*GATE: 對照 constitution v1.3.0 §IV 九題（初檢＝Phase 0 前；複檢＝Phase 1 設計後）。第 2／7／9 題判定值「涉及——授權以 Amendment 先行取得」承 003 形制（rev5 004 同）；Complexity Tracking 不填（★軌道與島皆循憲法明文機制取得授權、非違規）。*

| # | 題 | 判定 | 依據 |
|---|---|---|---|
| 1 | 違反 §I.1 base-web 權威？ | **PASS** | 五支規則端點與解鎖端點無 upstream 既有呼叫端（fork 原版無此面）＝rev6 自建管理能力、前端消費端同批新增檔交付；回傳型逐欄忠實 `contracts/wire-ip-rule.md`＋`wire-throttle-unlock.md`＋wire-schema 快照（`rev6-ip-rule.d.ts`）；既有 auth 三端點 wire 行為不變、增量列住 `wire-auth-delta.md` |
| 2 | 動 base-web inline？ | **涉及——授權以 Amendment 先行取得** | 新軌道 7 支既有檔（兩語 locale `route:`／`page:` 兩樹、`app.d.ts` page 型節——★必需非「如需」：`page:` 為顯式型樹；路由外掛產物四檔＝產物檔紀律〔禁手改＋重算冪等、明文不要求逐行標記及理由〕）；既有 I18N (ii)(iii)(i) 授權內另動 4 檔（backend 六鍵、型節、轉譯塊）；五欄範圍實數化同批（G1）。授權鏈＝ADR-00034 draft（已落、proposed）→ user 親決（tasks 首個主線任務）→ accepted＋§III.2 一列＋(ii)(i) 改寫＋五欄實數＋§I.7 島 F＋島 E 四處＋bump 1.4.0＋generate（§V.2 四步、獨立 commit）。★硬序：accepted 前不得動任何 base-web 既有檔（含 U6 之 locale backend 六鍵）；純新增檔不受此閘。驗收錨＝`tools/fork-delta-lint.py`（`load_roster` 表列變異證）＋`route-artifact-gate.py` 冪等 |
| 3 | menu 走 Casbin enforce？ | **PASS** | `manage_ip-rule` 選單列（78）與 menu 維政策列（149）已在 seed、動態選單本就回傳；本刀只建 view 與 route；四顆按鈕碼接既有 `hasAuth`；零 seed 改動、零新政策列（143～148、157、160～163 全在） |
| 4 | wire 對齊 §I.3？ | **PASS** | 信封三欄／`code` string／業務錯誤 HTTP 200／`PageRes` 分頁形／規則 id number＋2^53 守衛／`msg` 載穩定 key（`MSG_KEYS` 13→19）；13 碼矩陣零觸碰：阻擋與 F7 復用 `5003`（`PermissionDenied` 既有）、規則錯誤與解鎖畸形復用 `2222`；例外仍恰二；契約機器化＝contract 22 case＋wire-schema＋msg-key-gate。驗收錨＝contracts 三檔＋data-model §6 |
| 5 | 拷貝前代 code？ | **否（重打字）＋隨遷工具改** | rust／vue／python 全程重打字、註解 rev6 語境（rev5 出處 `rev5:`；R3 二十三筆＋清單 B 十一筆烤入 prompt）；`walkthrough-baseline.py` 為既有隨遷工具之三改；兩新閘承 rev5 同名工具新寫；entity／migration 零改 |
| 6 | 抵觸 §II 拍板？ | **否** | 未知標頭忽略（XFF 外標頭不採信＝同向）、動態選單、`/api` 前綴皆不動；翻碼內舊拍板一處＝`state.rs`「恰五欄」封條（ADR supersede ADR-00027、同批改寫註解並保留域外欄邊界說明） |
| 7 | 觸及 §III ★ 軌道？ | **涉及——授權以 Amendment 先行取得** | 新軌道屬「新能力」（新路由、新元件、跨檔）非用途補完；(ii) 權威句改寫與 (i) 範圍欄對齊同批；五欄實數化（BL-00058）；表列形受 `load_roster` 規則約束（ADR-00034 §一逐字）；i18n 三檔仍為最熱面（spec ★軌道登記表 9 列、風險判準可覆算）、產物檔 rebase 一律重算不手解 |
| 8 | 新建業務表含 §I.6 六審計欄？ | **不適用（零 migration）** | 消費四表皆 001 基線既有：`sys_ip_rule`（變體 A、六審計欄齊、partial unique）、三稽核表（變體 B append-only、只寫入；`ip_confidence` 無 CHECK ⇒ 八態零 DDL、既有列不遷移）；來源維計數走既有索引；★連帶紀律＝runtime-append 四表序列不復位（G6；data-model §7）；DDL 冒出＝範圍翻案（BL-00042）＋RUNBOOK §10 三步 |
| 9 | 觸及 §I.7 行為島？ | **涉及——授權以 Amendment 先行取得** | 島 F 隨本刀以 MINOR 入憲（F1～F8、rev5 v1.10.0 終態字面為底、含射程分界句；ADR-00034 §二）；島 E 四處細項調整（判定由 PG 定案無負快取〔刪 L1 句〕／來源維計數下界恆兩源／解鎖標記讀取 fail-closed／壞值補越界＋整組退）＝§V.3「已入憲 invariant 細項調整」、零 fail-* 方向反轉；跨島總則不動；state-machine 鏡頭＝data-model §1.1 規則二態、§2.5 三區合成、§5 降級矩陣；方向性反轉自此 MAJOR |

**初檢結論**：第 1／3／4／5／6／8 題 PASS；第 2／7／9 題「涉及、授權以 Amendment 先行取得」＝條件通過。

**Phase 1 複檢（設計後）**：research R1～R12／data-model §1～§8／contracts 五檔／quickstart／ADR-00034 draft 產出後重走九題——判定不變。第 2／7 題授權鏈形制已定（ADR-00034 §一 表列逐字、五欄實數＝code-gates.md §1 量法可重跑）；第 4 題由 contracts 三檔＋data-model §6 承載；第 5 題 R2 逐檔標處置、零拷貝面；第 9 題條文全文在 ADR-00034 §二。design 新增之憲法接觸面＝零（Phase 1 產物皆為既有拍板具象化）。★**GATE 狀態＝條件通過**：ADR-00034 accepted＋bump 1.4.0 為 tasks 第一個 ★ 主線任務且為硬閘，未完成前第 2／7／9 題不得視為 PASS、不得動任何 base-web 既有檔；U1～U6／U9 純後端不受該閘、可先行（tasks 編號；U7／U8／U10／U11 對 U0 硬序）。

## Project Structure

### Documentation (this feature)

```text
specs/004-ip-trust-anchor/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── checklists/requirements.md
├── contracts/
│   ├── wire-ip-rule.md            # 規則管理五端點＋阻擋回應
│   ├── wire-throttle-unlock.md    # 解鎖端點＋帳號維三件
│   ├── wire-auth-delta.md         # login／refresh／logout 增量（基底 specs/003）
│   ├── trust-model-config.md      # TOML 六集合＋三層失敗語意＋標頭契約
│   └── code-gates.md              # fork-delta 新軌道與五欄實數／兩新閘／走查工具／測試基建／名冊落點／ADR 七筆／帳本
└── tasks.md                       # /speckit-tasks 產（非本命令）
docs/arc42/decisions/ADR-00034-constitution-amendment-island-f-and-manage-page-track.md   # plan 期 draft（proposed）；tasks 首個主線任務 accepted
```

### Source Code (repository root)

```text
rust-api/                                        # worktree（rev6-admin-rust-api）
├── Cargo.toml                                   # workspace.dependencies += arc-swap／futures-util／toml（R1）
└── server/
    ├── Cargo.toml                               # 同上三支（features 逐 crate）
    ├── src/
    │   ├── trust/mod.rs(新)                     # TrustModel／Confidence 八態／resolve 三層＋兩覆蓋＋F6／normalize_xff／apply_chain_overflow
    │   ├── ipgate/mod.rs(新)                    # RuleSet／decide／STRUCTURAL_EXEMPT／would_self_lock／build_ruleset／reload_and_publish／watcher
    │   ├── middleware/mod.rs(新)                # request_context_mw（ConnectInfo→純函式→Extension）／ip_gate_mw（①②→decide→5003）
    │   ├── request_context.rs(換血)             # from_trust＋from_headers（缺席退路）；peer_ip；判定窗；模組頭回填
    │   ├── config.rs(擴)                        # load_trust_model 三層＋`rev5:B-074`；扁平退路 APP_TRUSTED_PROXY_CIDRS
    │   ├── state.rs(5→7)                        # trust_model／ip_rules；封條改寫（ADR supersede ADR-00027）
    │   ├── main.rs(改)                          # 載信任模型→初載規則集→起 watcher；BL-00072 靜態掃描案；數量字面
    │   ├── router.rs(改)                        # ROUTES 22、ROUTES_COUNT 22；中介層掛載序
    │   ├── obs.rs(改)                           # 序列名冊＝data-model §5（throttle 10 值／ip_domain 8 值／ipgate_blocked）
    │   ├── error.rs(改)                         # MSG_KEYS 13→19；doc 四處權威句改指針
    │   ├── cache/mod.rs(改)                     # +throttle_unlock_user_key／throttle_unlock_ip_key；−throttle_lock_user_key
    │   ├── throttle/mod.rs(重寫 precheck)       # 兩維並列合成、無 L1、registry 驗界整組退、redis_down 標記讀取、L0、ip_bucket、parse_unlock_marker
    │   ├── handler/
    │   │   ├── ip_rule.rs(新)                   # 五支＋守門＋防自鎖＋批次操作者名
    │   │   ├── throttle.rs(新)                  # unlock_login（稽核先於生效、Q2）
    │   │   ├── auth/{login,refresh,logout}.rs(改)   # Option<Extension> 取上下文（§5 ①）；login F7 拒絕腿先於 precheck
    │   │   ├── mod.rs(改) / system_settings.rs(改：測試建構點收斂)
    │   └── model/
    │       ├── audit.rs(新)                     # AuditEvent／AuditOperation 五字面／AuditOperator
    │       └── facade/{sys_ip_rule,sys_operation_log}.rs(新)＋sys_login_attempt.rs(擴：by_ip 計數＋chain_rejected 排除)＋test_kit.rs(改：廢 SequenceResetGuard＋水位守衛＋七欄 state)＋mod.rs(改)
    └── tests/
        ├── contract.rs(改：22 case) / common/mod.rs(改：stub_state 七欄) / wire_schema.rs(改：Api.IpRule) / entity_access_lint.rs(改：三 facade)
        ├── serve_connect_info_lint.rs(新：B-075)
        └── fixtures/wire-schema.json(重抽)

base-web/src/                                    # worktree（rev6-admin-base-web）
├── views/manage/ip-rule/{index.vue,modules/ip-rule-operate-drawer.vue,modules/ip-rule-search.vue}(新；rev5 HEAD 形)
├── service/api/rev6-ip-rule.ts(新 WRAPPER) / typings/api/rev6-ip-rule.d.ts(新 ADAPT)
├── locales/langs/{en-us,zh-cn}.ts(★新軌道 route/page 兩樹＋既有 (ii) backend 六鍵) / zh-tw.ts(backend 六鍵)
├── typings/app.d.ts(★新軌道 page 型節＋既有 (iii) backend 型節)
├── router/elegant/{imports,routes,transform}.ts＋typings/elegant-router.d.ts(★產物檔重算)
└── service/request/index.ts(既有 (i) onError 轉譯塊擴)

deploy/trust-model.dev.toml(零改；活體樣例)   deploy/grafana-provisioning/alerting/rules.yml(刪②、③b 錨)
tools/{view-render-guard.py,route-artifact-gate.py}(新碼面閘) / walkthrough-baseline.py(三改) / bootstrap.sh・docsync/tests(名冊)
.githooks/pre-commit(兩段)   docs/ops/RUNBOOK.md(§16 實文、§9c、§12)   README.md(工具樹、憲法版本鏡像)
.specify/memory/constitution.md(§I.7 島 F＋島 E 四處、§III.2 一列＋三處改寫＋五欄實數；1.4.0；U0)
docs/arc42/{05,06,08,10,11,12,01,03}-*.md(as-built、U10) / decisions/ADR-00034～00040(七筆) / docs/ops/LESSONS/LL-00017(補述)
docs/ops/BACKLOG.md(收刀：done 8／改 5／add 2)   docs/ops/NOTES.md(收刀→005)
```

**Structure Decision**：按功能域分模組承 rev5——`trust`（純函式政策判定、零 I/O）與 `ipgate`（可變判定面＋門鈴）刻意分兩模組（可測性與生命週期不同、合併即失去離線全態矩陣邊界）；`middleware` 首次進場、只放請求層接線零政策邏輯；handler 依端點群拆檔、facade 一表一檔（執行單元允許檔案清單有圈界力）。`router.rs`＋`tests/contract.rs`＋docsync routes 真表為 U7／U10 序列共用檔（tasks 編號；逐單元加列並 bump 同一 `ROUTES_COUNT`、不可並發）。測試基建（U3）排在 AppState 擴欄（U4）與功能單元之前，使 69 處守衛廢除與七處建構點收攏獨立於功能 diff。執行單元＝tasks.md 對映表（承 research R10 重切：U0 主線 Amendment 凍結→U1～U4 基座→U5～U10 依 US 交付面→U11 治理與走查→U12 收攏）；每單元 pin bump、Workflow 六件套、review／fix 烤入 RULES scope 塊（RULES-VERSION 不變）、每 run 不重複 agent ≤20；發射前模型分派向 user 確認。

## Complexity Tracking

Constitution Check 九題：六題 PASS、三題「涉及——授權以 Amendment 先行取得」（循憲法 §V.2 明文機制、非違規）——本節免填；授權鏈與硬序記於 Constitution Check 第 2／7／9 題與 research R10。★本刀形制新例（承 rev5、供日後引用）：路由外掛產物四檔採「禁手改＋重算冪等」而非逐行標記（標記於重算即被抹除、物理不可維持），以更強的機器檢查替代較弱的註解紀律，理由寫進軌道條文本體（ADR-00034 §一）。
