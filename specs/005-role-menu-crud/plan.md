# Implementation Plan: 005 role＋menu 管理 CRUD 寫端——角色與選單接真、選單域序列化、判定面同步、授權歸檔寫入面、島 H 入憲

**Branch**: `005-role-menu-crud` | **Date**: 2026-09-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-role-menu-crud/spec.md`（clarify Q1～Q5 定案 2026-09-23）＋`docs/brainstorms/005-role-menu-crud.md`（拍板 Q1～Q5／G1～G4／R1-Q1～Q10／R1-Q4b／R2-Q1、既定不問 8 條、工程判斷 1～43、設計十節）＋`rev5:005-role-menu-crud` 全套與 rev5 凍結 worktree（唯讀）

## Summary

把 upstream 角色頁與選單頁自 demo 殼接成真：17 支端點（role CRUD 6＋roleHome 2 住 `handler/role.rs`；menu CRUD 7＋getMenuTree＋getAllPages 住 `handler/menu.rs`；ROUTES 22→39）、前後端同刀、CDP 對照 rev5 驗收。同刀落地授權治理刀要消費的三件底座：①**選單域 advisory 序列化域**（`rev6menu` key、交易由 handler 持有且域鎖為首動作、角色刪除家族入域）②**casbin 判定面同步**（全新重建後一步換上、函式內靜態互斥件全程序列化、保留上一份、`casbin_reload_total` 三值；觸發恰五支移除面寫端之「實際歸檔 ≥1 列」）③**授權歸檔寫入面＋三值 reason gate**。憲法一次 MINOR 1.4.0→1.5.0（島 H 入憲含 H3 受保護兩腿與 H2 同步失敗保留上一份、§III.2 用途 (ii) 恰九檔、島 E 兩句、兩句簿記改對）；`MSG_KEYS` 19→43；**零 migration、零 seed 變更、零新依賴**。
技術路徑＝高度參照 rev5 HEAD 形（research R2 逐檔清單、R3 清單 A 剔除 006～008 增量十二項＋清單 B rev6 翻案二十一筆、R4 commit 三分），連帶收 004／002 域到期承載（分頁共用規則＋明名全取入口、ILIKE／23505 收窄／時戳上提＋`sys_ip_rule` 具型交易簽章、信任模型標頭名開機體檢、兩支 supersede ADR）與測試基建／機器守（五表守衛、兩支新 lint、i64 lint 三件、wire 表驅動鍵集斷言、qs 前提錨），BACKLOG 19 條隨刀收。ADR 六支（ADR-00042～ADR-00047）已於本 plan 落 draft（`proposed`）。

## Technical Context

**Language/Version**: Rust 1.96.1（edition 2024、容器內 build／test 全程 serial）＋TypeScript 6.0.3／Vue 3.5.34（base-web：用途 (ii) 九支既有檔＋4 支新檔＋1 支產物檔重算＋rev6 自有檔 2 支〔ip-rule 頁、`zh-tw.ts`〕；`pnpm typecheck`）＋Python 3 標準庫（`tools/wire-schema.py` 新腿、`tools/walkthrough-baseline.py` 擴面、docsync tests 釘值）

**Primary Dependencies**: 零新依賴、零版本變更（research R1）——casbin **2.20.0**（`default-features = false`；硬禁令前提）、axum 0.8.9（`axum::http::HeaderName` 再匯出供標頭名體檢）、sea-orm 1.1.20、tokio 1.53.1（`sync::Mutex` 互斥件、`Notify` seam）、metrics 0.24.6、serde_json 1.0.151；naive-ui 2.44.1（`NTreeSelect` 既有元件）、vue-i18n 11.4.2、qs 6.15.1（前提錨對象）

**Storage**: PostgreSQL 18.4（001 基線；`sys_role`／`sys_menu`／`sys_casbin_policy_archive` 首寫者、`casbin_rule` 移除面、`sys_user_role` 只讀計數、`sys_operation_log` 擴寫入者；advisory xact 鎖；零 migration）；rev6 stack 埠 35432；Redis 本刀零新鍵

**Testing**: cargo test（`--test-threads=1` 容器內）——facade 真 DB 案（五表守衛、交易內擾動排序）／handler oneshot＋真 seed app 案（24 鍵名冊雙向閘）／contract 39 case＋雙向覆蓋閘／序列化域 pg_locks NOT-granted 等待案（七進域寫端＋三不進域）／判定面同步十類案（失敗注入、負向自證、交錯時序 seam、端到端雙斷言）／wire-schema 表驅動鍵集＋首屏真串／新 lint 兩支（`authz_entrypoint_lint`、`test_module_tail_lint`）＋`wire_i64_guard_lint` 三件；python 工具 `test` 子命令；前端零測試框架＝`pnpm typecheck`＋機器斷言（fork-delta-lint 變異自證、兩彈窗零 diff、`components.d.ts` 兩行、ip-rule 模板靜態斷言）＋兩段 review＋CDP 三方對照（SC-011）

**Target Platform**: Linux 容器（compose project `rev6-admin`）；host＝macOS（本機）／WSL2（他機）；CDP 由 host 瀏覽器 `127.0.0.1:9229`、一律 opus agent 操作

**Project Type**: web-service（rust-api server crate：2 新 handler＋1 新 facade＋10 擴寫模組〔清單＝research R5〕＋2 新 lint 測試檔）＋前端接線（base-web 用途 (ii) 九檔＋4 新檔＋rev6 自有檔 2 支）＋憲法 Amendment＋治理（6 ADR、活書 7 章、RUNBOOK 6 節、reference-src 3 檔）

**Performance Goals**: 無業務量化目標（dev workspace）。紀律面：①判定面每請求零外部查詢不變（同步只在移除面寫端 commit 後、治理 QPS≈0）②全量重建一次＝163 列級政策載入、毫秒級③選單治理清單全取＝seed 78 列一次、樹組裝 O(n)④pre-commit 全鏈 ≤45s 警戒（新 python 腿為純讀檔、秒級）

**Constraints**: 零 migration／零 seed／零新依賴／13 碼矩陣零觸碰且零新錯誤變體／AppState 恰七欄不動（ADR-00036）／Amendment 硬序（accepted 前 base-web 既有檔零 diff、含 locale backend 鍵）／§I.5 rev5 參照紀律（重打字、註解重寫、清單 A／B 烤入 prompt）／§III fork-delta 三元組（修改型只在九檔、兩彈窗零 diff）／整樹掃描既有腿約束（`ipgate` 禁 `.store(`／`::swap(` 等呼叫形、`throttle` 禁鎖快取字面、`fallback_event` debug 恰 1、`entity_access_lint`）／review 只讀／rev5 樹與 stack 唯讀／編排全角色 opus[1m] xhigh、CDP 一律 opus

**Scale/Scope**: 39 routes（17 新：GET 7／POST 6／DELETE 4）／43 msg keys（24 新）／9 AppError 變體（0 新）／5 AuditOperation 詞（0 新）／3 archive reason／5 觸發寫端／7 進域寫端／4 分頁端點＋1 例外／base-web 修改型 6 檔＋新增型圈界 3 檔（預估 12 塊）＋4 新檔＋1 產物檔／憲法 +1 島 +1 用途 +2 島 E 句＋2 簿記句／ADR 6／BACKLOG done 19＋改 3＋add 0／執行單元 18（U0～U17；派發真源＝tasks.md、骨架＝research R18）

## Constitution Check

*GATE: 對照 constitution v1.4.0 §IV 九題（初檢＝Phase 0 前；複檢＝Phase 1 設計後）。第 2／7／9 題判定值「涉及——授權以 Amendment 先行取得」承 003／004 形制；Complexity Tracking 不填（★軌道與島皆循憲法明文機制取得授權、非違規）。*

| # | 題 | 判定 | 依據 |
|---|---|---|---|
| 1 | 違反 §I.1 base-web 權威？ | **PASS** | role／menu 頁為 upstream demo 面、其 fetch 標的正是本刀補齊對象；回傳型逐欄忠實兩支 wire 契約＋wire-schema 快照；wire 型開獨立命名空間 `Api.RoleAdmin`／`Api.MenuAdmin`；upstream 未改動之消費者（使用者頁抽屜之 `AllRole`、菜單權限彈窗之 `MenuTree`）所依 upstream 型同受審斷言相容 |
| 2 | 動 base-web inline？ | **涉及——授權以 Amendment 先行取得** | 用途 (ii) 九檔（六支修改型＋新增型：語意改動逐行 `原行:`、純新增段走新增型圈界；三支僅新增型圈界；兩顆授權彈窗與 `shared.ts` 明文不入）；backend 24 鍵走既有 I18N (ii)(iii)；`components.d.ts` 走 §III 生成檔紀律。授權鏈＝ADR-00042 draft（已落、proposed）→ user 親決（tasks 首個主線任務）→ accepted＋§III.2 一列＋bump 1.5.0＋generate（§V.2 四步、獨立 commit）。★硬序：accepted 前不得動任何 base-web 既有檔（含 locale backend 鍵）；純新增檔不受此閘。驗收錨＝`tools/fork-delta-lint.py`（名冊載入變異自證、各新增塊拔標記必紅）＋`route-artifact-gate.py` 冪等 |
| 3 | menu 走 Casbin enforce？ | **PASS** | 本刀對選單域只做 CRUD 資料面；可見性授權屬授權治理刀；零 seed 改動、零新政策列（17 條之 seed 政策列全在）；新建／復原選單側欄不現＝本項誠實結果（ADR-00045 款 3） |
| 4 | wire 對齊 §I.3？ | **PASS** | 信封三欄／`code` string／業務錯誤 HTTP 200／`PageRes` 四欄不變／id number＋2^53 守衛／`msg` 載穩定 key（`MSG_KEYS` 19→43）；13 碼矩陣零觸碰、`2222` 復用、例外仍恰二；跨端點分頁規則入活書 08 §8.2＋契約＋contract test；IP 規則清單未知類型上 wire＝ADR-00046 by-design（wire 逐位元不變）。驗收錨＝contracts 兩支 wire＋`msg-keys.md`＋data-model §7～§8 |
| 5 | 拷貝前代 code？ | **否（重打字）** | rust／vue／python 全程重打字、註解 rev6 語境（rev5 出處 `rev5:`；research R3 清單 A 十二項剔除＋清單 B 二十一筆翻案＋十一項前代防回歸烤入 prompt）；entity／migration 零改 |
| 6 | 抵觸 §II 拍板？ | **否** | 動態選單、`/api` 前綴、未知標頭忽略皆不動；翻碼內舊宣告三處＝判定面「boot 載入即終態」（ADR-00043、明引 ADR-00014 決定 4 為兌現其預告、不 supersede）；翻 ADR-00040（ADR-00046 supersede）與 ADR-00015（ADR-00047 supersede） |
| 7 | 觸及 §III ★ 軌道？ | **涉及——授權以 Amendment 先行取得** | 既有軌道 `★BASE-WEB-MANAGE-PAGE-WIRING` 加用途 (ii)＝新能力（新接線、跨九檔）非補完；共用表頭元件為本刀新衝突面（只附加 prop、預設 true、帶預設值宣告）；i18n 三檔仍最熱（spec ★軌道登記表 11 列、風險判準可覆算）；表外宣告 1 量法句同批改（BL-00118） |
| 8 | 新建業務表含 §I.6 六審計欄？ | **不適用（零 migration）** | 消費六表皆 001 基線既有（`sys_role`／`sys_menu` 變體 A 六審計欄齊、partial unique；`casbin_rule` 治理三欄；`sys_casbin_policy_archive` 14 欄；`sys_user_role` 複合 PK＋FK RESTRICT；`sys_operation_log` append-only）；DDL 冒出＝範圍翻案 |
| 9 | 觸及 §I.7 行為島？ | **涉及——授權以 Amendment 先行取得** | 島 H 隨本刀 MINOR 入憲（rev5 v1.7.0 字面為底；增補＝H3 受保護選單不可停用／不可改父、H2 同步失敗保留上一份；明文化＝H3 常量父鏈寫端列舉、H4 兩域消費面、H5 常量重驗；ADR-00042 款三逐字＋差異附表）；島 E 補兩句（BL-00098）；依承襲指針表尾句完成跨島重審（結論＝跨島註不動；唯一降級腿＝判定面同步失敗、方向＝保留上一份與 F2 同向——方向入 H2 條文、機制細節由 ADR-00043 承載）；島 G 行為由 ADR-00044 承載、條文隨授權治理刀入憲；state-machine 鏡頭＝data-model §2（角色／選單／判定面三矩陣）＋§4 觸發矩陣＋§5 守門序；方向性反轉自此 MAJOR（射程七島） |

**初檢結論**：第 1／3／4／5／6／8 題 PASS；第 2／7／9 題「涉及、授權以 Amendment 先行取得」＝條件通過。

**Phase 1 複檢（設計後）**：research R1～R20／data-model §1～§10／contracts 四檔／quickstart／ADR-00042～ADR-00047 draft 產出、並經唯讀對抗查證一輪（五鏡＋逐鏡複核、55 筆成立皆已改入）後重走九題——判定不變。第 2／7 題授權鏈形制已定（ADR-00042 款五表列逐字、範圍欄為 rev5 as-built 預估且前端單元出口逐檔斷言）；第 4 題由 contracts 兩支 wire＋`msg-keys.md`＋data-model §7～§8 承載；第 5 題 R2 逐檔標處置、零拷貝面；第 9 題條文全文在 ADR-00042 款三。design 新增之憲法接觸面＝零（Phase 1 產物皆為既有拍板具象化）；plan 期對 spec 措辭之精修五處——FR-052 判定面 lint 生產面定義、FR-073 BL-00111 lint 射程納跨檔被切檔（research R12；皆擴大覆蓋）、FR-042 與 Key Entities 之終態入域成員限選單維／按鈕維（對齊島 H1 前代字面）、FR-058／FR-075③ 與 ★ 軌道登記表之六檔型別改「修改型＋新增型」且預估限三支僅新增型檔（ADR-00042 款五）——皆不觸憲法現文。★**GATE 狀態＝條件通過**：ADR-00042 accepted＋bump 1.5.0 為 tasks 第一個 ★ 主線任務且為硬閘，未完成前第 2／7／9 題不得視為 PASS、不得動任何 base-web 既有檔；純後端單元（零 base-web 既有檔改動者）不受該閘，但全部施工單元皆排在 U0 施工前提顆（ADR-00043／ADR-00044／ADR-00047 accepted）之後。

## Project Structure

### Documentation (this feature)

```text
specs/005-role-menu-crud/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── checklists/requirements.md
├── contracts/
│   ├── wire-role-admin.md     # 角色八端點（role CRUD 6＋roleHome 2）
│   ├── wire-menu-admin.md     # 選單九端點（menu CRUD 7＋getMenuTree＋getAllPages）
│   ├── msg-keys.md            # 24 拒因鍵候選表（發出點、語意要求、落地單元；譯文之家＝三檔 locale）
│   └── code-gates.md          # fork-delta 用途 (ii)／新 lint 兩支／名冊擴充／wire 裁判／測試基建／走查工具／觀測／ADR 與帳本
└── tasks.md                   # /speckit-tasks 產（非本命令）
docs/arc42/decisions/ADR-00042～ADR-00047-*.md   # plan 期 draft（proposed）；U0 親決 00042（Amendment 顆）與 00043／00044／00047（施工前提顆）；00045／00046 治理單元親決（治理單元排在 CDP 三方對照之後）
```

### Source Code (repository root)

```text
rust-api/                                        # worktree（rev6-admin-rust-api）
└── server/
    ├── src/
    │   ├── handler/
    │   │   ├── role.rs(新)                      # role 6＋roleHome 2；交易殼（begin→域鎖→facade→稽核→commit／顯式 rollback→同步）；operator_from（target security.role）
    │   │   ├── menu.rs(新)                      # menu 7＋getMenuTree＋getAllPages；page_or_all 唯一生產呼叫；operator_from（target security.menu）
    │   │   ├── common.rs(擴)                    # +tristate<T>／blank_to_none／db_status_to_wire／wire_two_value_to_db；BL-00113 重評結論入 doc；兩域字面守名冊擴
    │   │   ├── mod.rs(改)                       # pub mod menu／role（ASCII 序）；域數句
    │   │   ├── ip_rule.rs(改)                   # 改引 page_params、刪私有三常數；degraded 腿射程擴；doc 指針
    │   │   └── system_settings.rs(改：只註＋私有三態改引)
    │   ├── model/facade/
    │   │   ├── sys_casbin_archive.rs(新)        # MENU_DOMAIN_LOCK_KEY／enter_menu_domain／menu_domain_waiter_count／三 reason＋is_non_restorable_reason／insert_archived／三支歸檔 fn（回傳列數）
    │   │   ├── sys_role.rs(擴)                  # SEEDED_ROLE_IDS／SUPER_ROLE_CODE／page_query／all_active_enabled／寫端（收 &DatabaseTransaction）
    │   │   ├── sys_menu.rs(擴)                  # list_governed／build_governed_tree／paginate_top_level（不 clamp）／governed_tree／display_route_names／寫端狀態機
    │   │   ├── sys_ip_rule.rs(改)               # 改引共用件；四寫端＋find_by_id_for_update 收 &DatabaseTransaction（BL-00096）
    │   │   ├── mod.rs(擴)                       # ilike_contains／violated_constraint／now_ts；名冊句改寫
    │   │   ├── sys_user_role.rs(擴)             # count_by_role／is_member（只讀）
    │   │   └── test_kit.rs(擴)                  # 五守衛＋組合守衛＋號段表＋自證測
    │   ├── auth/enforce.rs(擴)                  # rebuild_enforcer／reload_enforcer（static RELOAD_SERIAL）／reload_seam（cfg(test)）；終態句改寫
    │   ├── envelope.rs(擴)                      # PAGE_* 三常數／page_params／page_or_all／PageSpec（置於末錨 fn 之前）
    │   ├── config.rs(擴)                        # load_trust_model 標頭名體檢（新 TrustLoadKind 變體、degraded_source→None）
    │   ├── obs.rs(改)                           # casbin_reload_total 三值預註冊
    │   ├── error.rs(改)                         # 24 msg_key 常數；MSG_KEYS 19→43；名冊兩測
    │   ├── router.rs(改)                        # ROUTES 39、ROUTES_COUNT 39；釘值測
    │   ├── model/audit.rs(改：doc) / model/facade/sys_operation_log.rs(改：doc) / main.rs(改：doc) / state.rs(改：doc) / ipgate/mod.rs(改：測試模組 3 處改交易)
    │   └── handler/route.rs(改：doc)
    └── tests/
        ├── contract.rs(改：39 case＋24 鍵發射段＋常量路由非空案＋請求上下文缺席總數案)
        ├── common/mod.rs(改：tests 側五表 RestorePlan＋BL-00110 RAII)
        ├── wire_schema.rs(改：新受審型＋PageRes＋表驅動鍵集＋首屏真串)
        ├── wire_i64_guard_lint.rs(改：三件＋檔頭兩段)
        ├── authz_entrypoint_lint.rs(新) / test_module_tail_lint.rs(新)
        └── fixtures/wire-schema.json(重抽)

base-web/src/                                    # worktree（rev6-admin-base-web）
├── views/manage/role/{index.vue,modules/role-operate-drawer.vue,modules/role-search.vue}(★(ii) 修改型)
├── views/manage/menu/{index.vue,modules/menu-operate-modal.vue}(★(ii) 修改型)
├── components/advanced/table-header-operation.vue(★(ii) 修改型：showAdd／showDelete)
├── views/manage/ip-rule/index.vue(rev6 新檔改：prop 形＋未知類型退顯)
├── service/api/rev6-{role,menu}-admin.ts(新 WRAPPER) / typings/api/rev6-{role,menu}-admin.d.ts(新 ADAPT)
├── locales/langs/{en-us,zh-cn}.ts(★(ii) page 9 鍵＋既有 I18N (ii) backend 24 鍵) / zh-tw.ts(backend 24 鍵)
├── typings/app.d.ts(★(ii) page 型節＋既有 I18N (iii) backend 型節)
└── typings/components.d.ts(產物檔重算：NTreeSelect 兩行)

deploy/trust-model.dev.toml(改註：三態)   deploy/grafana-provisioning/alerting/rules.yml(改註：島 H2＋ADR-00043)
tools/wire-schema.py(BL-00109 腿) / walkthrough-baseline.py(restore 擴面) / docsync/tests/test_references.py(+17 列)
.specify/memory/constitution.md(§I.7 島 H＋島 E 兩句＋段首句＋MAJOR 七島＋指針表；§III.2 (ii)＋表外宣告 1；1.5.0；U0)   README.md(憲法版本鏡像)
docs/arc42/{04,05,06,08,10,11,12}-*.md(as-built、feature branch 內) / decisions/ADR-00042～00047
docs/ops/RUNBOOK.md(§9c／§11／§12／§13／§16.1／§16.2) / reference-src/{schema-definition,trust-model-config,code-gate-contracts}.md
docs/ops/BACKLOG.md(收刀：done 19／改 3／add 0)   docs/ops/NOTES.md(specify 起手後指 005 進行中、收刀→006)
```

**Structure Decision**：承 rev6 004 形——handler 依端點群拆檔、交易殼住 handler（域鎖為交易首動作、facade 寫端收具型交易、可被組合）；facade 一表一檔之例外恰一（`sys_casbin_archive` 同寫授權表與歸檔表、名冊句改寫）；共用件依消費面分層（handler 共用件住 `handler/common.rs`、facade 共用件住 `facade/mod.rs`、分頁規則住 `envelope.rs` 與 `PageRes` 同檔）。高風險共享檔序列鏈（同檔單元不並發）：`router.rs`／`tests/contract.rs`（U1 立 17 case 後逐單元充實）、`error.rs`＋三檔 locale＋`app.d.ts`（U7～U9 隨首發單元分批、雙 pin 同顆）、`facade/{sys_menu,sys_role,sys_casbin_archive,mod}.rs`、`handler/{role,menu,common}.rs`、`envelope.rs`（U2；U6 改名冊期望）＋`sys_ip_rule.rs`＋`ipgate/mod.rs`＋`handler/ip_rule.rs`（U2；後者另於 U7／U8 改其 degraded 射程測）。執行單元＝research R18 骨架（U0 主線兩顆〔Amendment 顆＋施工前提顆〕→U1～U11 後端與 wire〔U6 讀端六支零新鍵、getRoleHome 併入 U7〕→U12～U13 前端→U14 體檢→U15 走查工具→U16 CDP 三方對照〔ADR-00045 觀察定稿〕→U17 治理面與全量閘〔ADR-00045／00046 親決〕）；每單元 pin bump、Workflow 六件套、review／fix 烤入 RULES scope 塊（RULES-VERSION 不變）、TDD 單元保險絲 ≤20 支；編排全角色 opus[1m] xhigh、prompt 首行帶深思關鍵詞（骨架現值）。

## Complexity Tracking

Constitution Check 九題：六題 PASS、三題「涉及——授權以 Amendment 先行取得」（循憲法 §V.2 明文機制、非違規）——本節免填；授權鏈與硬序記於 Constitution Check 第 2／7／9 題與 research R15～R16。★本刀形制新例：①supersede ADR 首度附**款號對照表**（ADR-00046／ADR-00047；spec FR-069 要求、rev6 前例皆為行內句）②判定面同步 lint 之「生產面」採「扣除行首測試模組區塊」定義（item 級測試門控項保守計入），與既有切面腿之「切到首個行首測試門控」形並存、由 BL-00111 lint 守後者之射程（research R12）。
