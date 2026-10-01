# Implementation Plan: 006 授權治理——三維授權接真、結構性封死、授權回收桶、島 G 入憲

**Branch**: `006-authz-governance` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-authz-governance/spec.md`（clarify 一題定案 2026-10-01＋plan 期取證揭出之四題 user 裁定，皆入 Clarifications Session 2026-10-01）＋`docs/brainstorms/006-authz-governance.md`（拍板 Q1～Q17、主線工程判斷、設計四節、§IV 九題預答）＋`rev5:006-authz-governance` 全套與 rev5 凍結 worktree（唯讀）＋plan 期唯讀取證一輪（六鏡平行取證＋逐鏡反駁＋完備性評審；load-bearing 主張 112 條確認 110、推翻 2 已更正）＋plan 期起草審查（ADR 九支與 research／data-model／contracts／quickstart 各經逐單元審查→修正→確認輪、跨檔評審→對帳→確認輪；確認輪殘留由主線定點修）

## Summary

把 upstream 三顆授權彈窗與授權回收桶自 demo 殼接成真：10 支端點（三維授權六支＋候選讀兩支住既有 `handler/role.rs`；回收桶兩支住新建 `handler/policy_archive.rs`；ROUTES 39→49）、前後端同刀、CDP 對照 rev5 HEAD 驗收。語意核心四件：①**全量替換**（期望全集輸入、射程＝候選集、三維同式；候選外現役列不撤不授、現況讀端只回候選內）②**受保護授權列撤銷拒＋G6 結構性封死**（非 R_SUPER 標的授不出受保護端點；R_SUPER 名下非受保護列可撤、自救走回收桶）③**授權撤銷一律移入回收桶**（端點維可一鍵復原、五腿固定序；選單維與按鈕維只可閱覽＝不可復原集 3→5；標的已現役＝NoOp）④**判定面同步觸發列增列**（授予面 Applied 即觸發含空 diff、復原 Applied）＋條文如實記兩窗。憲法一次 MINOR 1.6.0→1.7.0（島 G 六條入憲、§III.2 用途 (iii)(iv)、§III 修改型 Vue 模板屬性行變體句、表外宣告 3 塊數入對賬、島 H 連動）、收刀前 PATCH 實數化 (iii)(iv) 範圍欄（1.7.x）；`MSG_KEYS` 43→46；**零 migration、零 seed 變更、零新依賴**。
技術路徑＝高度參照 rev5 HEAD 形（research 之 rev5 對應碼清單與差異點）；BACKLOG 收 5／收窄 3／反向確認 2；ADR 九支（ADR-00063～ADR-00071）已於本 plan 落 draft（`proposed`）；收刀前另立 PATCH Amendment ADR 一支（配號屆時）。

## Technical Context

**Language/Version**: Rust 1.96.1（`rust-api/rust-toolchain.toml`；edition 2024、容器內 build／test 全程 serial）＋TypeScript 6.0.3／Vue 3.5.34（base-web：用途 (iii) 三支既有檔＋(iv) 與既有 I18N 用途之 locale／型別檔＋5 支新檔＋路由產物四檔重算）＋Python 3 標準庫（`tools/seed-view-gate.py` 新閘、`tools/fork-delta-lint.py` 對賬新腿、`tools/walkthrough-baseline.py` 擴面、docsync tests 釘值）

**Primary Dependencies**: 零新依賴、零版本變更——casbin 2.20.0、axum 0.8.9、sea-orm 1.1.20、tokio 1.53.1、metrics 0.24.6、serde_json 1.0.151（`rust-api/Cargo.lock` 現讀）；naive-ui 2.44.1（`NTree` 既有元件）、vue-i18n 11.4.2（`base-web/package.json` 現讀）

**Storage**: PostgreSQL 18.4（001 基線；`casbin_rule` 授予寫入與撤銷移出、`sys_casbin_policy_archive` 首個 list／restore 消費者、`sys_role` 鎖讀、`sys_menu` 治理域只讀、`sys_operation_log` 擴寫入者、`sys_user` 帳號名批次讀；advisory xact 鎖沿 005；零 migration）；rev6 stack 埠 35432；Redis 本刀零新鍵

**Testing**: cargo test（`--test-threads=1` 容器內）——facade 真 DB 案（守衛兩族擴補回 seed 授權列；交易內撤銷／授予／封死／五腿）／handler oneshot＋真 seed app 案（三維寫端全量替換、空 diff、全撤、候選外不動、受保護撤銷拒與封死授予拒、R_SUPER 豁免、超管自斷自救）／contract 49 case＋新三鍵實發點／序列化域 pg_locks NOT-granted 等待案（新入域兩支）／觸發矩陣特性測（含空 diff 與不觸發三態、取消安全）／wire-schema 新命名空間正反例／`authz_entrypoint_lint` 名冊擴列與植入自證；python 工具 `test` 子命令（seed-view-gate、fork-delta-lint 新腿、walkthrough-baseline v3）；前端零測試框架＝`pnpm typecheck`＋機器斷言（fork-delta-lint、route-artifact-gate、view-render-guard、msg-key-gate）＋兩段 review＋CDP 三方對照

**Target Platform**: Linux 容器（compose project `rev6-admin`）；host＝macOS（本機）／WSL2（他機）；CDP 由 host 瀏覽器 `127.0.0.1:9229`、一律 opus[1m]／xhigh agent 操作

**Project Type**: web-service（rust-api server crate：1 新 handler＋1 新 facade＋既有模組擴寫〔清單＝research 對應碼清單〕）＋前端接線（base-web 用途 (iii)(iv)＋5 新檔）＋憲法 Amendment＋治理（9 ADR、活書、RUNBOOK、工具與閘）

**Performance Goals**: 無業務量化目標（dev workspace）。紀律面：①判定面每請求零外部查詢不變（同步只在授權寫端與移除面寫端 commit 後、治理 QPS≈0）②全量重建一次＝163 列級政策載入、毫秒級③候選讀端：治理域選單一次讀、按鈕碼聯集一次掃描、端點候選自路由表純記憶體導出④pre-commit 全鏈秒級（新 python 閘為純讀檔）

**Constraints**: 零 migration／零 seed／零新依賴／13 碼矩陣零觸碰且 `AppError` 零新變體（拒因走既有 2222）／Amendment 硬序（accepted 前 base-web 既有檔零 diff、含 locale backend 鍵）／BL-00132 對賬腿早於 Amendment 後首個 base-web 單元／§I.5 rev5 參照紀律（重打字、註解重寫、差異點烤入 prompt）／§III fork-delta 三元組（修改型逐行 `原行:`、新增型圈界、新檔不入表）／授予一律 facade 直 INSERT（不走判定引擎管理 API、不走轉接器 `add_policy`）／review 只讀／rev5 樹與 stack 唯讀／編排全角色 opus[1m]／xhigh

**Scale/Scope**: 49 routes（10 新：GET 6／POST 4）／46 msg keys（3 新）／`AppError` 0 新變體／5 AuditOperation 詞（0 新）／6 歸檔原因（3 新）、不可復原集 5／觸發寫端 5 移除面＋3 授予面＋1 復原／入域寫端 +2（updateRoleMenu、updateRoleButton）／base-web：(iii) 三支既有檔＋(iv) locale 與型別＋5 新檔（端點權限彈窗、回收桶頁兩支、API wrapper、型別檔）＋產物四檔／憲法 +1 島（G）+2 用途＋1 變體句＋表外宣告 3＋島 H 連動／ADR 9＋收刀前 PATCH 1／BACKLOG done 5＋收窄 3＋反向確認 2（BL-00137／BL-00138 由本刀第一筆 events 事件帶 add）／執行單元 19（U0～U18；派發真源＝tasks.md、骨架＝research 單元切分節）

## Constitution Check

*GATE: 對照 constitution v1.6.0 §IV 九題（初檢＝Phase 0 前；複檢＝Phase 1 設計後）。第 2／7／9 題判定值「涉及——授權以 Amendment 先行取得」承 003～005 形制；Complexity Tracking 不填（★ 軌道與島皆循憲法明文機制取得授權、非違規）。*

| # | 題 | 判定 | 依據 |
|---|---|---|---|
| 1 | 違反 §I.1 base-web 權威？ | **PASS** | 三顆授權彈窗與授權回收桶頁為 upstream demo 面、其呼叫之 10 支端點正是本刀補齊對象；回傳型逐欄忠實兩支 wire 契約＋wire-schema 快照；wire 型開獨立命名空間 `Api.Authz`（`src/typings/api/rev6-authz.d.ts`）；首頁下拉沿 upstream 既綁之選值即寫事件（spec Clarifications） |
| 2 | 動 base-web inline？ | **涉及——授權以 Amendment 先行取得** | 用途 (iii)＝兩顆授權彈窗（修改型逐行 `原行:`＋新增型圈界）＋角色抽屜同檔雙用途（第三鈕 3 塊新增型；BL-00131 修法在 (ii) 既有圈界內）＋兩語 locale `page:` 樹＋`app.d.ts` 型節；用途 (iv)＝回收桶頁之 locale `route:`／`page:` 塊＋`app.d.ts` page 型節＋產物四檔（產物檔紀律）；backend 3 鍵走既有 I18N (ii)(iii)；新檔（端點彈窗、回收桶頁兩支、`rev6-authz.{ts,d.ts}`）不入表、檔頭標記比照 004 刀先例名形；BL-00135 變體句同顆入憲。授權鏈＝ADR-00063 draft（已落、proposed）→ user U0 逐款親決 → accepted＋§III.2 兩列＋bump 1.7.0＋generate（§V.2 四步、獨立 commit）。★硬序：accepted 前不得動任何 base-web 既有檔（含 locale backend 鍵）；純新增檔不受此閘。驗收錨＝`tools/fork-delta-lint.py`（含 BL-00132 範圍欄對賬新腿）＋`route-artifact-gate.py` 冪等＋`view-render-guard.py` |
| 3 | menu 走 Casbin enforce？ | **PASS** | 選單維授權寫入 `casbin_rule`、使用者可見性一律由判定面導出（API 判定即時、選單與按鈕顯隱下次載入；不做推播）；零 seed 改動、10 支之 seed 政策列全在；不啟用 hideInMenu 等前端隱藏機制；選單維受保護四列不封、其「看得到、封死功能點不動」與 21 支可授出端點之授出後效果為已知態（ADR-00068） |
| 4 | wire 對齊 §I.3？ | **PASS** | 信封三欄／`code` string／業務錯誤 HTTP 200／分頁 `PageRes` 不變／逐欄 id 型／`msg` 載穩定 key（`MSG_KEYS` 43→46）；13 碼矩陣零觸碰、拒因復用 2222；三維現況讀端只回「現況 ∩ 候選集」（與 rev5 HEAD 之 wire 列數差與端點候選集之差皆已登入 spec 刻意分岔登記表）；驗收錨＝contracts 兩支 wire＋`msg-keys.md`＋data-model wire 映射節 |
| 5 | 拷貝前代 code？ | **否（重打字）** | rust／vue／python 全程重打字、註解 rev6 語境（rev5 出處 `rev5:`）；翻案不帶回五項（facade 自開交易取鎖寫稽核、稽核操作者缺席之降級借欄、msg 鍵字面構造、清理件寫死序列值、deleteRole 零同步）與本刀差異點烤入 prompt（research 差異點節）；seed-view-gate 藍本取 rev5 006 刀原始版 |
| 6 | 抵觸 §II 拍板？ | **否** | 動態選單、`/api` 前綴、未知標頭忽略皆不動；觸發列以新 ADR 增列（ADR-00043 決定 7 預授、不 supersede）；ADR-00045／ADR-00046 以續行 ADR 承接（accepted 同顆補 supersedes） |
| 7 | 觸及 §III ★ 軌道？ | **涉及——授權以 Amendment 先行取得** | 既有軌道 `★BASE-WEB-MANAGE-PAGE-WIRING` 加用途 (iii)(iv)＝新能力（新接線、跨多檔）非補完；i18n 三檔與 `app.d.ts` 仍最熱（spec ★ 軌道登記表 12 列、風險判準可覆算）；表外宣告 3 同顆改為塊數入對賬射程（BL-00132） |
| 8 | 新建業務表含 §I.6 六審計欄？ | **不適用（零 migration）** | 消費之表皆 001 基線既有（`casbin_rule` 治理欄 `protected`／`created_by`；`sys_casbin_policy_archive` 14 欄；`sys_role`／`sys_menu` 變體 A；`sys_operation_log` append-only；`sys_user`）；DDL 冒出＝範圍翻案；授予寫入落 `created_by`＝操作者、復原回插落 `created_by`＝復原者且 `protected`＝FALSE（承載點＝data-model 歸檔與寫入不變式節） |
| 9 | 觸及 §I.7 行為島？ | **涉及——授權以 Amendment 先行取得** | 島 G 隨本刀 MINOR 入憲（rev5 v1.10.0 島 G 字面為底、rev6 座標改寫；G6 新立＝封死謂詞；ADR-00044 決定 3 所載 G 行為由條文轉正；停用雙護欄不轉正）；島 H 同顆連動（序言凍結位句、H1 括號改「選單維與按鈕維之復原分支結構性不可達」、H2 記兩窗、MAJOR 射程七島→八島、承襲指針表 G 列）；state-machine 鏡頭＝data-model 狀態機節（授權列：不存在／現役／已歸檔 × 授予、授權撤銷、連動歸檔、復原 Applied／NoOp／拒）＋觸發矩陣＋守門固定序；方向性反轉自此 MAJOR（射程八島） |

**初檢結論**：第 1／3／4／5／6／8 題 PASS；第 2／7／9 題「涉及、授權以 Amendment 先行取得」＝條件通過。

**Phase 1 複檢（設計後）**：research R1～R20／data-model §1～§13／contracts 四檔／quickstart §0～§11／ADR-00063～ADR-00071 draft 產出、並經起草審查（逐單元審查→修正→確認輪、跨檔評審→對帳→確認輪；確認輪殘留由主線定點修）後重走九題——判定不變。第 2／7 題授權鏈形制已定（ADR-00063 決定二表列逐字；(iii)(iv) 範圍欄以預估填列、觸及 base-web 既有檔之單元出口逐檔斷言、收刀前 PATCH 實數化；對賬腿早於首個觸及 base-web 既有檔之單元＝決定四）；第 4 題由 contracts 兩支 wire＋`msg-keys.md`＋data-model §9／§12 承載；第 5 題 research R2 逐檔標取／等價／不帶、零拷貝面；第 9 題島 G 條文全文在 ADR-00063 決定一、島 H 連動在決定五。design 新增之憲法接觸面＝收刀前 PATCH Amendment 一支（範圍欄實數化；前例 ADR-00051、承載＝ADR-00063 翻案觸發器）。plan 期對 spec 之精修——Clarifications 第二～五題（user 四題裁定）入檔與其連動之驗收場景、Edge Cases、FR-014／FR-023／FR-033／FR-034／FR-053、SC-003／SC-010；FR-008 款號；FR-041／FR-046／SC-012／SC-014 之 ADR 計數與版本（plan 期九支＋收刀前 PATCH 一支、1.7.x）；FR-042 對賬腿射程；刻意分岔登記表增「端點候選集」列——皆不觸憲法現文。★**GATE 狀態＝條件通過**：ADR-00063 accepted＋bump 1.7.0 為 tasks 首個親決之 ★ 主線任務（U0 Amendment 顆）且為硬閘，未完成前第 2／7／9 題不得視為 PASS、不得動任何 base-web 既有檔（含 locale backend 鍵）；全部施工單元皆排在 U0 施工前提顆（ADR-00064～ADR-00067 accepted）之後。

## Project Structure

### Documentation (this feature)

```text
specs/006-authz-governance/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── checklists/requirements.md
├── contracts/
│   ├── wire-authz-governance.md   # 三維六支＋候選讀兩支（getRoleMenu／updateRoleMenu／getRoleButton／updateRoleButton／getRoleEndpoints／updateRoleEndpoints／getAllButtons／getAllEndpoints）
│   ├── wire-policy-archive.md     # 授權回收桶兩支（getArchivedPolicies／restorePolicy）
│   ├── msg-keys.md                # 新三鍵（發出點、語意要求、跨端閘、落地時序；不立譯文表）
│   └── code-gates.md              # fork-delta 用途 (iii)(iv)／新閘與新腿／名冊擴列／wire 裁判／測試基建／走查工具／觀測／ADR 與帳本
└── tasks.md                       # /speckit-tasks 產（非本命令）
docs/arc42/decisions/ADR-00063～ADR-00071-*.md   # plan 期 draft（proposed）；ADR-00063 於 U0 由 user 逐款親決（Amendment 顆）；其餘依 research 之「ADR 配號與親決時點表」所定時點 accepted
```

### Source Code (repository root)

```text
rust-api/                                        # worktree（rev6-admin-rust-api）
└── server/
    ├── src/
    │   ├── handler/
    │   │   ├── role.rs(擴)                      # 三維六支＋候選讀兩支（域字面沿 security.role）；授予面 Applied 同步之 settle 件；授權寫端稽核件；生產區 reload 釘測改寫
    │   │   ├── policy_archive.rs(新)            # getArchivedPolicies／restorePolicy；target security.policy_archive；operator_from／db_failure／BODY_FALLBACK_MSG；帳號名批次換算
    │   │   ├── common.rs(改)                    # 逐域字面守名冊加回收桶域
    │   │   ├── mod.rs(改)                       # pub mod policy_archive（ASCII 序）；域數句
    │   │   ├── ip_rule.rs(改：測試)             # degraded 欄零出現腿之檔清單加回收桶檔
    │   │   └── route.rs(改：測試)               # BL-00136 形①兩類改錨
    │   ├── router.rs(擴)                        # ROUTES 49、ROUTES_COUNT 49；新建 policy_endpoints()＋方法白名單；釘值測
    │   ├── error.rs(改)                         # 3 msg_key 常數；MSG_KEYS 43→46
    │   └── model/facade/
    │       ├── sys_casbin_policy.rs(新)         # casbin_rule 主 facade：三維現況讀、候選輔助、封死集查詢、全量替換規劃、授予 INSERT
    │       ├── sys_casbin_archive.rs(擴)        # 三撤銷原因、不可復原集 3→5、授權撤銷 archive-move、回收桶 list／restore
    │       ├── sys_role.rs(擴)                  # 以 id 無鎖讀活角色代碼、以代碼批次取活角色 id；「不帶」句改寫
    │       ├── sys_menu.rs(改)                  # 「不帶」句改寫；測試 BL-00136 形①兩類改錨、植殘列件落建立者
    │       ├── mod.rs(改：doc)                  # 「十二支對十二張表」、例外恰一＝sys_casbin_archive、成員序句
    │       └── test_kit.rs(擴)                  # 守衛兩族擴補回（授權腿補被撤 seed 授權列、歸檔腿補界下歸檔列）、plant_live_policy 落建立者、號段表
    └── tests/
        ├── contract.rs(改：49 case＋新三鍵實發點＋授權態矩陣新表＋兩處 raw INSERT 補建立者)
        ├── common/mod.rs(擴：整合測試 crate 守衛族補回＋逐字對賬)
        ├── wire_schema.rs(擴：Api.Authz 受審型與正反例)
        ├── authz_entrypoint_lint.rs(改：RELOAD_CALL_FILES／DOMAIN_WRITE_SIDE_FILES 與植入案字面)
        └── fixtures/wire-schema.json(重抽)

base-web/src/                                    # worktree（rev6-admin-base-web）
├── views/manage/role/modules/{menu-auth-modal.vue,button-auth-modal.vue}(★(iii) 修改型＋新增型)
├── views/manage/role/modules/role-operate-drawer.vue(★(iii) 新增型 3 塊＋(ii) 既有圈界內 BL-00131)
├── views/manage/role/modules/endpoint-auth-modal.vue(新)
├── views/manage/policy-archive/{index.vue,modules/policy-archive-search.vue}(新；view 目錄＝seed sys_menu 列 10 之 component `view.manage_policy-archive`)
├── service/api/rev6-authz.ts(新 WRAPPER) / typings/api/rev6-authz.d.ts(新 ADAPT；Api.Authz)
├── locales/langs/{en-us,zh-cn}.ts(★(iii)(iv) page:／route: 塊＋既有 I18N (ii) backend 3 鍵) / zh-tw.ts(backend 3 鍵)
├── typings/app.d.ts(★(iii)(iv) page 型節＋既有 I18N (iii) backend 型節)
├── router/elegant/{imports,routes,transform}.ts / typings/elegant-router.d.ts(產物檔重算：新 view 頁)
└── typings/components.d.ts(若引入新元件＝工具重算形)

tools/seed-view-gate.py(新) / fork-delta-lint.py(範圍欄對賬新腿) / walkthrough-baseline.py(基準檔 v3、restore 補回) / docsync/tests/test_references.py(+10 列) / bootstrap.sh(閘名冊)   .githooks/pre-commit(seed-view-gate 段)
.specify/memory/constitution.md(§I.7 島 G＋島 H 連動＋MAJOR 八島＋指針表；§III 變體句；§III.2 (iii)(iv)＋表外宣告 3；1.7.0；U0)   README.md(憲法版本鏡像)
docs/arc42/{04,05,06,08,10,11,12}-*.md(as-built、feature branch 內) / decisions/ADR-00063～00071＋ADR-00045／ADR-00046(accepted 時 status→superseded)
docs/ops/RUNBOOK.md(§9c／§11.2／§12／§13)   docs/ops/BACKLOG.md(收刀：done 5／改 3)   docs/ops/NOTES.md   docs/ops/events.jsonl(第一筆事件帶 BL-00137／BL-00138 backlog_add；收刀 feature_close)
```

**Structure Decision**：承 rev6 005 形——handler 依端點群拆檔、交易殼住 handler（入域者域鎖為交易首動作、facade 寫端只收具型交易、可被組合）；三維八支住既有 `handler/role.rs`（域字面沿 `security.role`、`DOMAIN_LOCK_CALL_FILES`／`RELOAD_CALL_FILES` 角色列已在、零擴），回收桶兩支自成新域檔 `handler/policy_archive.rs`（`security.policy_archive`、兩逐域名冊各加一列）；`casbin_rule` 之主 facade 新立 `sys_casbin_policy.rs`、facade 名冊句改「十二支對十二張表」、跨表例外恰一＝`sys_casbin_archive`；候選導出住 `router.rs`（`policy_endpoints()`／`endpoint_methods()`），facade 零 `crate::router` 引用、候選與白名單以參數收；前端新檔不入 barrel、wire 型開單一命名空間 `Api.Authz`、零新泛型。高風險共享檔序列鏈（同檔單元不並發）：`router.rs`／`tests/contract.rs`、`error.rs`＋三檔 locale＋`app.d.ts`（隨各拒因鍵首發單元分批）、`handler/role.rs`、`facade/{sys_casbin_policy,sys_casbin_archive,sys_role,sys_menu,mod,test_kit}.rs`、`tests/authz_entrypoint_lint.rs`。執行單元＝research R18 骨架（U0 主線兩顆〔Amendment 顆＋施工前提顆〕→U1～U11 後端與 wire〔U2 對賬腿早於首個觸及 base-web 既有檔之單元 U7〕→U12～U14 前端→U15 走查工具 v3→U16 CDP 三方對照〔已知態觀察〕→U17 治理單元〔已知態兩支與 ADR-00070 親決〕→U18 收刀前承載體檢〔PATCH Amendment〕）；每單元 pin bump、Workflow 六件套、review／fix 烤入 RULES scope 塊、TDD 單元保險絲 ≤20 支；編排全角色 opus[1m] xhigh。

## Complexity Tracking

Constitution Check 九題：六題 PASS、三題「涉及——授權以 Amendment 先行取得」（循憲法 §V.2 明文機制、非違規）——本節免填；授權鏈與硬序記於 Constitution Check 第 2／7／9 題與 research R15～R16。★本刀形制新例：①表外宣告 3 之範圍欄處數與塊數首度入機器對賬（BL-00132；含預估項之檔改由單元出口逐檔斷言承擔至收刀前 PATCH）②首支讀面型碼面閘 `tools/seed-view-gate.py`（ADR-00071；ADR-00055 決定 3 之首例）。
