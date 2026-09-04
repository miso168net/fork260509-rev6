# Implementation Plan: 001 schema 基線（rev5 終態逐位元承襲＋受管演進帳）

**Branch**: `001-schema-baseline` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-schema-baseline/spec.md`

## Summary

rev6 資料庫基線＝rev5 終態 15 表：`m0001_baseline_schema`／`m0002_baseline_seeds` 程式內容逐位元承襲 `rev5:m001`／`rev5:m002`（憲法 §I.5 例外②、
ADR-00009 accepted 52fb52f、檔名四碼＝ADR-00008），entity 15 檔同例外承襲；同刀就位 rust-api workspace 骨架（migration／entity／adapter）、
兩支閘工具隨遷（三閘＋entity 漂移閘）、凍結 fixtures（rev6 pristine 重放萃取、與 rev5 雙源互證）、演進登記檔、docsync `refresh`＋兩張參考真表、
RUNBOOK Day-1 常設程序；schema 基線與閘契約立 ADR-00010（proposed→U2 收尾 accepted）。定稿權威：欄序＝data-model §2（承 rev5、位元不動）、
seed＝m0002 本體＋凍結 seed.sql。

## Technical Context

**Language/Version**: Rust 1.96.1（`deploy/Dockerfile.rust-api` 既定 `rust:1.96.1-slim`、`rust-toolchain.toml` 同值；user 拍板 2026-09-04）
＋Python 3 標準庫（repo 治理工具：docsync package、兩支單檔閘工具）

**Primary Dependencies**: sea-orm／sea-orm-migration 1.1.20、tokio 1.53.1、casbin 2.20.0、async-trait 0.1.92（三源核對表＝research R1；features 恰同 rev5；不引 argon2）；
vendored `sea-orm-adapter`（§I.5 例外①）

**Storage**: PostgreSQL 18.4（`postgres:18.4-alpine`；dev DB `soybean_admin_rust`／user `soybean`；rev6 stack 埠 35432、pristine 驗證零 host 埠）

**Testing**: cargo build（容器內、serial；migration 重放即整合測試）＋python 工具自帶 `test`（schema-gate 含 negative 五類、entity-drift 三型）＋
pristine 重放＋fixtures 雙源互證（`cmp`）＋17 檔去註解 diff 自證＋docsync `test`（新 `test_snapshot.py`）＋pre-commit 全鏈

**Target Platform**: Linux 容器（compose project `rev6-admin`）；host＝WSL2（/mnt/d drvfs：跑過 compose 後同 shell 重新 `cd`）

**Project Type**: DB migration／entity crates（rust-api 首批工件）＋repo 治理工具隨遷與 docsync 擴充（單 repo 多工件；外層＋rust-api worktree 兩段式 commit）

**Performance Goals**: pre-commit 全鏈 ≤45s 警戒／90s 硬擋（檔頭雙錨、不動）；entity-drift 秒級零 docker；三閘 check 秒級（需 stack）；首次映像 build 數分鐘

**Constraints**: host 無 rust toolchain；rev5 唯讀（凍結 SHA 外層 `7eab28a`／rust-api `92919b9`、絕不寫入）；fixtures 凍結後永不改寫；
17 檔逐位元自證＋註解語意判準；閘數恆 12（碼面閘不入名冊）；docsync 行數落點記錄（≤4,000 啟動書目標、非閘）；review agent 只讀

**Scale/Scope**: 15 表 169 欄、索引 38／約束 101、seed 266 列（casbin 163）、migration 兩支、entity 15 檔、adapter 5 檔、閘工具 3,302 行隨遷、docsync +約 250 行、
ADR 2 顆、BACKLOG 2 條消化（BL-00001／BL-00005）

## Constitution Check

*GATE: 對照 constitution v1.1.0 §IV 九題（初檢＝Phase 0 前；複檢＝Phase 1 設計後）。*

| # | 題 | 判定 | 依據 |
|---|---|---|---|
| 1 | 違反 §I.1 base-web 權威？ | **否** | 本刀零 endpoint 面（server 隨 002）；schema 忠實承襲、無設計範圍縮減；wire-schema 不入刀（spec Out of Scope） |
| 2 | 動 base-web inline？ | **否** | base-web 全程不動；本刀全在 rust-api worktree＋外層 tools/docs |
| 3 | menu 顯示走 Casbin enforce？ | **是（seed 面）** | 本刀無 route 過濾邏輯；seed 承 rev5 定稿含 demo menu 全集＋casbin menu 政策（§I.2 機制前提）；`hide_in_menu` 6 列＝upstream meta、釋義承 `rev5:ADR 0005`（data-model §8） |
| 4 | wire 對齊 §I.3？ | **是（射程內）** | 本刀無 wire；帶自增主鍵之 11 表 id 皆 bigint（§I.3 DB 側不變式、承 rev5 終態） |
| 5 | 拷貝前代 code？ | **是、例外內** | §I.5 例外①`sea-orm-adapter` 整檔拷貝；例外②資料形狀契約三件（m0001／m0002／entity 15 檔、射程鎖 `92919b9`）＝ADR-00009 accepted 52fb52f、憲法 1.1.0；四條件（逐位元自證／註解語意判準／防回歸審查＝data-model §10／seed 固定值）；lib.rs／main.rs／Cargo／docsync snapshot.py 重打字；兩支閘工具＝RULES「隨遷工具」授權（tools/、非 §I.5 射程） |
| 6 | 抵觸 §II 拍板？ | **否** | §II 三筆（unknown header／auth route mode／路徑前綴）皆不涉 |
| 7 | 觸及 §III ★ 軌道？ | **否** | 不動 base-web；「首批軌道隨首刀」之「首刀」＝首個觸及 base-web inline 的刀（brainstorm §0 釋義）、本刀零觸及 |
| 8 | 新建業務表含 §I.6 六審計欄？ | **是** | 15 表逐表 archetype 歸屬＝data-model §1（A×5／B×4／C×4／D×2）、audit 閘機器驗；建表即帶 rev5 終態欄、零 retrofit |
| 9 | 觸及 §I.7 行為島？ | **否** | v1.1.0 尚無已入憲島；本刀純 schema 落地、零狀態機；「首座島隨首刀」＝首個觸及狀態機的刀（brainstorm §0 釋義） |

**初檢結論**：九題全過、零違規（第 5 題例外內、Amendment 已先落）。
**Phase 1 複檢（設計後）**：data-model／contracts／quickstart 產出後重走九題——判定不變；第 5 題射程與 research R0 對應碼清單逐檔一致（例外②恰 17 檔、
例外①恰 adapter、其餘重打字或隨遷工具）；第 8 題由 audit 閘契約（contracts/gates.md §3）機器化。**通過**。

## Project Structure

### Documentation (this feature)

```text
specs/001-schema-baseline/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── checklists/requirements.md
├── contracts/
│   ├── gates.md                 # 三閘行為契約（承 rev5 改座標；雙源互證、假 delta 案、sequence 對賬面）
│   ├── schema-evolution.md      # 演進登記檔契約（形零改）
│   └── fixtures.md              # 凍結面契約（rev6 產製程序、六欄目 provenance）
├── fixtures/                    # 【U2 產】columns/indexes/constraints.json＋seed.sql＋provenance.md（與 rev5 雙源互證後凍結）
└── tasks.md                     # /speckit-tasks 產（非本命令）
```

### Source Code (repository root)

```text
rust-api/                        # worktree（現況源倉 Initial commit）——首批程式工件
├── Cargo.toml                   # workspace: members = [migration, entity, sea-orm-adapter]；deps 首刀子集（R1）
├── Cargo.lock                   # 容器內產、入版控
├── rust-toolchain.toml          # 1.96.1
├── rustfmt.toml                 # 三值承 rev5（rust-fmt-gate 隨 002）
├── migration/                   # lib.rs／main.rs 自寫；m0001_baseline_schema.rs＋m0002_baseline_seeds.rs（§I.5 例外②照抄、改名、註解語意重寫）
├── entity/                      # lib.rs 自寫；15 檔（§I.5 例外②）
└── sea-orm-adapter/             # §I.5 例外①整檔拷貝（註解四型失效引用 rev6 化；測試碼假 DSN allowlist）

tools/
├── schema-gate.py               # 隨遷工具（去 seed-decision／rename map；座標同名）
├── entity-drift-gate.py         # 隨遷工具
└── docsync/
    ├── snapshot.py              # 新：六撈／psql_fetch／build_*_snapshot／cmd_refresh／gen_reference_schema／gen_reference_accounts
    ├── references.py            # GENERATED_FILES 12→14、compute_generated 掛兩鍵
    ├── __main__.py              # 加 refresh 子命令
    └── tests/test_snapshot.py   # 一正一反

docs/ops/reference-src/          # 新目錄
├── archetype-map.json           # 承 rev5 改座標（15 表歸屬）
├── schema-evolution.json        # 初版零筆
├── schema-snapshot.json         # refresh 首跑產
└── accounts-snapshot.json       # refresh 首跑產

docs/generated/reference/{schema,accounts}.md   # generate 首算（U3 同批）
.githooks/pre-commit             # 自測名冊加兩支＋entity-drift 段（Day-1 跳過／就位實跑）
tools/bootstrap.sh               # run_tool_test 加兩支
README.md                        # tools/ 樹加兩行（GT-09）
docs/ops/RUNBOOK.md              # §10 實文、§12 兩列＋refresh 列、§9 psql 直連一句
docs/arc42/05-building-block-view.md   # §5.1 樹列、§5.2 rust-api 句、frontmatter rev5_blueprint §5「隨刀」→「承襲」
docs/arc42/decisions/ADR-00010-*.md    # proposed→accepted（U2 收尾、證據段補齊）
docs/ops/BACKLOG.md              # BL-00001（Task 0 消化）、BL-00005（U5）、append docsync 行數對賬條目
docs/ops/LESSONS/                # 首條 LL 即解除 GT-08.lessons-absent
```

**Structure Decision**：rust-api＝Cargo workspace 首建、members 僅本刀三 crate（server 隨 002）；兩段式 commit（worktree 內 commit → 外層即時 bump pin）；
治理工件全在外層。執行單元（research R11、依 tasks 展開）：**Task 0**＝BL-00001 骨架收斂（首個 Workflow 前）→ **U1** 骨架＋17 檔＋adapter＋容器內 build＋dev stack migrate up
→ **U2** 兩工具隨遷＋pristine 重放＋fixtures 雙源互證凍結＋archetype-map／schema-evolution 初版＋工具自測綠＋ADR-00010 accepted
→ **U3** docsync snapshot.py＋refresh 首跑＋兩快照＋兩生成器＋entity-drift hook 接線與實跑 → **U4** RUNBOOK／README／bootstrap／活書＋DoD 鏈全綠＋perf 事件
→ **U5** BL-00005（收刀前、拍板級 user 親決）。編排＝CLAUDE.md §2 Workflow 六件套（規則塊現算、每 run 不重複 agent ≤24、launch 與 Monitor 原子成對）。

## Complexity Tracking

Constitution Check 九題全過、零違規——本節免填（第 5 題為例外內、非違規；Amendment 紀錄＝ADR-00009／憲法 Amendment log 1.1.0）。
