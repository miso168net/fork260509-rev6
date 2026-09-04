# Implementation Plan: 002 系統設定讀寫（server 進場首刀縱切管線）

**Branch**: `002-system-settings` | **Date**: 2026-09-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-system-settings/spec.md`（clarify Q1～Q5 已定案）＋docs/brainstorms/002-system-settings.md（拍板 Q1～Q8＋方案 A、設計十一節）

## Summary

立 `rust-api/server` crate（workspace 第四 member）打通「router→授權→handler→registry 驗證→facade→`Res` 信封→前端接線層」縱切管線，功能面＝系統設定 16 鍵讀＋寫（單鍵更新、三態）。
技術路徑＝高度參照 `rev5:002-system-settings` 終態碼（axum 0.8.9 全棧、RouteDef 註冊表、enforce 骨架、validation registry、facade 分層、oneshot 測試形——research R2 逐檔清單），
依 R3 十五筆 rev6 拍板差異點改判（型別不一致 5000、方法不符 4040 信封、msg key 後端閉環、fork-delta 斷言改形、entity-drift 即紅等）。前端腿＝typings＋service 兩新檔（§III.1、零修憲）。
治理進場＝U0 組合拳（三支碼面閘隨遷、pre-commit 六處、RUNBOOK §12 碼面閘表＋GT-12 腿、失準修單）＋主線先落名詞段「碼面閘」與 RULES-VERSION bump；契約機器化＝wire-schema 三件＋docsync routes 生成器；ADR 六筆；零 migration。

## Technical Context

**Language/Version**: Rust 1.96.1（edition 2024、`rust-toolchain.toml` 既有釘定；容器內 build／test、全程 serial）＋TypeScript（base-web typings／service 兩新檔、不動既有碼）＋Python 3 標準庫（三支隨遷碼面閘、docsync 生成器與 GT-12 腿）

**Primary Dependencies**: axum 0.8.9／serde 1.0.229／serde_json 1.0.151／tracing 0.1.44／tracing-subscriber 0.3.23／metrics 0.24.6／metrics-exporter-prometheus 0.18.3／axum-prometheus 0.10.1；既有 sea-orm 1.1.20、casbin 2.20.0＋vendored sea-orm-adapter、tokio 1.53.1；dev-dep tower 0.5.3＋jsonschema **0.53.0**（user 拍板 2026-09-05、`default-features = false`）——雙源對照表＝research R1

**Storage**: PostgreSQL 18.4（001 基線；`system_settings` 16 鍵 seed 在庫；零 migration；rev6 stack 埠 35432）

**Testing**: cargo test 三層（純函式紅綠／oneshot 契約＋雙向覆蓋閘＋快照裁判＋兩支 lint／真 DB integration 掛 RAII 還原守衛——R7）；容器內 `--test-threads=1`；python 工具自帶 `test`（三支碼面閘＋docsync test 新增 test_gates／test_references 案）；quickstart 經 front-nginx 真 HTTP 走查

**Target Platform**: Linux 容器（compose project `rev6-admin`、七件預設業務件；host＝WSL2、/mnt/d drvfs 跑過 compose 後同 shell 重新 `cd`）

**Project Type**: web-service（rust-api server crate 首落地）＋前端接線層（base-web 兩新檔）＋repo 治理工具隨遷與 docsync 擴充（單 repo 多工件；外層＋兩 worktree 兩段式 commit）

**Performance Goals**: 無業務量化目標（16 鍵低頻治理面）；pre-commit 全鏈 ≤45s 警戒／90s 硬擋（含新增三段）；容器冷編記時不入 DoD

**Constraints**: 憲法 §I.3 wire 凍結面（信封／13 碼 reuse／msg=key／例外恰二）；§I.5 rev5 參照紀律（重打字＋註解重寫＋R3 防回歸清單）；§I.6 審計欄 facade 顯式成對寫；隨遷工具四型失效引用 rev6 化；rust 全程 serial 容器內；review agent 只讀；rust-fmt 首跑對 001 承襲 17 檔若紅＝停手升 user

**Scale/Scope**: 4 routes（業務 2＋信封例外 2）／16 keys／2 DTO／6 AppError 變體／7 msg keys；server crate 約 27 檔（承 rev5 終態規模）；隨遷工具 3 支（約 2,185 行）；docsync +1 生成器 +1 GT-12 腿；base-web 2 新檔；ADR 6；BACKLOG 3 done＋2 新記

## Constitution Check

*GATE: 對照 constitution v1.1.0 §IV 九題（初檢＝Phase 0 前；複檢＝Phase 1 設計後）。*

| # | 題 | 判定 | 依據 |
|---|---|---|---|
| 1 | 違反 §I.1 base-web 權威？ | **否** | 兩端點全套讀＋寫、範圍不縮減；wire 形對齊 typings 新檔（權威）；view 延後屬交付排程（brainstorm Q1） |
| 2 | 動 base-web inline？ | **否** | 恰兩新檔（typings＝§III.1 ADAPT、service＝§III.1 WRAPPER `rev6-*.ts`）、零既有檔改動、零 `.env`、零 locales（brainstorm Q4／Q7）；fork-delta 新增型圈界標記＋lint 機器守（本刀進場） |
| 3 | menu 顯示走 Casbin enforce？ | **是（消費面）** | 不動 sys_menu／casbin seed；設定域政策列 66／67 僅 R_SUPER、enforce 消費既有政策；manage_system-settings 選單 404 已知態 |
| 4 | wire 對齊 §I.3？ | **是** | 信封三欄宣告序／code string／business error HTTP 200（例外僅 4040→404、5003→403）／13 碼全 reuse 零新碼／七碼構造層不可發出／msg＝穩定 key＋後端名冊雙向斷言／2^53 守衛承襲／PageRes 不適用／契約機器化隨本刀落地（wire 地基刀）；★方法不符→4040 信封令信封例外維持恰二（clarify Q4） |
| 5 | 拷貝前代 code？ | **否（重打字）＋隨遷工具授權** | rust 應用碼全程重打字＋註解 rev6 語境（rev5 出處帶 `rev5:`；R3 防回歸清單烤入 prompt）；三支 tools 為 RULES 名詞段「隨遷工具」（tools/、非 §I.5 射程；四型失效引用 rev6 化）；sea-orm-adapter／entity／migration 為 001 既有例外、本刀零改 |
| 6 | 抵觸 §II 拍板？ | **否** | #1 unknown header 忽略（contract case 斷言）；#2 auth route mode dynamic——本刀不觸（`.env` 延 003、brainstorm Q7；ADR-00003 註 4 之「ADAPT 首刀」＝首個需動 `.env` 的刀）；#3 路徑不帶 `/api`（front-nginx strip） |
| 7 | 觸及 §III ★ 軌道？ | **否** | 零 inline＝不觸；首個 ★軌道隨首個改 base-web 既有檔的刀 Amendment 開立；fork-delta-lint 對空 ★表以哨兵句守（R10） |
| 8 | 新建業務表含 §I.6 六審計欄？ | **不適用（零新表）** | 零 migration；`system_settings` 為 001 基線變體 A、審計欄由 facade 顯式成對寫、ORM 行為層恆空＋機器錨（BL-00008）；DDL 冒出＝FR-021 走 RUNBOOK §10 三步 |
| 9 | 觸及 §I.7 行為島？ | **否** | 本刀無狀態機（registry 純驗證、enforce 消費 seed 政策皆非島）；授權治理島隨 006、單 session 等隨 003；零 Amendment |

**初檢結論**：九題全過、零違規。
**Phase 1 複檢（設計後）**：data-model／contracts 兩檔／quickstart 產出後重走九題——判定不變；第 2 題由 contracts/code-gates.md §1.3 標記字面與 §III.1 範圍腿機器化；第 4 題由 contracts/wire-settings.md §3 七條碼面斷言承載；第 5 題 R2 清單逐檔標「重打字／隨遷」、零拷貝面。**通過**。

## Project Structure

### Documentation (this feature)

```text
specs/002-system-settings/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── checklists/requirements.md
├── contracts/
│   ├── wire-settings.md         # 兩端點契約／碼面斷言／快照與覆蓋閘／前端接線層
│   └── code-gates.md            # 三支碼面閘行為／pre-commit 六處／RUNBOOK 表＋GT-12 腿＋名詞段／routes 生成器／entity_behavior_lint／ADR 六筆
└── tasks.md                     # /speckit-tasks 產（非本命令）
```

### Source Code (repository root)

```text
rust-api/                            # worktree（rev6-admin-rust-api）
├── Cargo.toml                       # workspace members += "server"；workspace.dependencies 加 R1 十支
└── server/
    ├── Cargo.toml                   # R1 依賴子集（features 逐項註解重寫）
    ├── src/
    │   ├── main.rs / lib.rs         # boot：config→db→init_enforcer→router build→serve；tracing json
    │   ├── config.rs                # APP_DATABASE_URL[_FILE]
    │   ├── router.rs                # ROUTES const（4 條）＋build＋fallback（未註冊路徑＋方法不符→4040）
    │   ├── state.rs                 # AppState{db, enforcer}
    │   ├── envelope.rs              # Res＋2^53 守衛＋serialize_i64_as_string
    │   ├── error.rs                 # 13 碼常量＋AppError 六變體＋msg key 名冊常數（七鍵）
    │   ├── obs.rs                   # recorder＋render＋axum-prometheus
    │   ├── validation.rs            # registry 16 鍵＋NUMBER_RANGES＋canonical＋型別一致性守衛
    │   ├── auth/{mod,enforce,dev_identity}.rs
    │   ├── request_context.rs       # seam 介面位
    │   ├── handler/{mod,system_settings}.rs
    │   └── model/{mod.rs, facade/{mod,system_settings,sys_user_role}.rs}
    └── tests/
        ├── common/mod.rs / health.rs / contract.rs / wire_schema.rs
        ├── entity_access_lint.rs / entity_behavior_lint.rs
        └── fixtures/wire-schema.json   # extract 產物

base-web/                            # worktree（rev6-admin-base-web）
└── src/typings/api/rev6-settings.d.ts、src/service/api/rev6-settings.ts   # 兩新檔、rev6-inline 新增型標記

tools/
├── rust-fmt-gate.py / wire-schema.py / fork-delta-lint.py   # 隨遷（U0；fork-delta 結構斷言改形）
└── docsync/
    ├── references.py            # routes 生成器＋GENERATED_FILES 14→15（U1）
    ├── gates.py                 # GT-12 碼面閘表腿＋NON_GATE_TOOLS（U0）
    └── tests/{test_gates,test_references}.py

.githooks/pre-commit             # 六處（U0）
docs/ops/RULES.md                # 名詞段「碼面閘」（主線直改、U0 前）
docs/ops/RUNBOOK.md              # §12 碼面閘表（U0）
README.md                        # tools/ 樹加三行（U0）＋docs/generated 成員行加 routes（U1）
tools/bootstrap.sh               # run_tool_test 加三支（U0）
docs/generated/reference/routes.md   # generate 產（U1）
docs/arc42/{05,08}-*.md          # as-built（U8）
docs/arc42/decisions/ADR-000NN-*.md     # 六筆（U6／U7／U8 落；序號落檔時取、現況 next＝ADR-00013）
docs/ops/BACKLOG.md              # 三條 done（收刀）、兩條新記（U8）
```

**Structure Decision**：server crate 目錄形逐一對應 rev5 002 終態（R2 清單）以最小化參照摩擦；rev5 縮編面（不建 redis／throttle／ipgate 等）＝R3 的目錄級呈現；
`dev_identity.rs` 獨立檔（003 汰換時整檔刪除）。執行單元＝research R12：主線直改（名詞段）→ U0 治理組合拳 → U1 基座 → U2 授權 → U3～U7 五個 US → U8 收攏；
每單元 pin bump、Workflow 六件套、review／fix 烤入 RULES scope 塊（bump 後新版）、每 run 不重複 agent ≤24。

## Complexity Tracking

Constitution Check 九題全過、零違規——本節免填。
