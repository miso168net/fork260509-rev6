# Tasks: 001 schema 基線（rev5 終態逐位元承襲＋受管演進帳）

**Input**: Design documents from `/specs/001-schema-baseline/`

**Prerequisites**: plan.md、spec.md、research.md（R0 對應碼清單、R1 版本、R6 工具清單、R11 單元序）、data-model.md、contracts/、quickstart.md；
憲法 1.1.0＋ADR-00009 accepted（52fb52f）；ADR-00010 proposed。

**Tests**: 本 repo TDD＝CLAUDE.md §2 紀律、**非可選**——「驗證先行」面：拷貝碼之先紅＝parity diff 與 pristine 重放（US1 T016／T018）；工具之先紅＝自帶 `test`
（含 negative 五類、US3 T026）；docsync 之先紅＝`tests/test_snapshot.py`（US5 T032 先於 T033）；hook 之先紅＝缺席演練（US4 T031）。

**Organization**: 依 user story 分期（US1～US6）；本刀為地基刀、story 間有天然順序相依（見 Dependencies）；**執行單元對映**（research R11）另列於文末，
主線編排時以單元為 Workflow 派發粒度、每單元一顆外層 commit（單元收尾六步序＝CLAUDE.md §2）。

**紀律烤入**（一切任務隱含）：rust build/test 一律容器內、全程 serial（host 無 toolchain）；rev5 `../fork260509-rev5/` 唯讀、絕不寫入；
§I.5 例外②恰 17 檔逐位元、註解語意判準；一般碼重打字；兩段式 commit（`git -C rust-api` 內 commit → 外層即時 bump pin）；★絕不 push／merge
（finishing 前硬禁令、本清單不含此類任務）；書面產物與註解一律 zh-TW；前代編號一律 `rev5:`／`rev4:` 前綴；`/mnt/d` 跑過 compose 後同 shell 先重新 `cd`。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可平行（不同檔案、無未完成相依）
- **[Story]**: 所屬 user story（US1～US6）；Setup／Foundational／Polish 無標籤

## Phase 1: Setup（Task 0＋前置體檢）

**Purpose**: 首個 Workflow 派發前的治理前置與環境就緒

- [x] T001 **Task 0＝BL-00001**：收斂 `tools/orchestration/_sk_head.js`／`_sk_head1.js`／`_sk_head3.js` 三變體之 `IMPL_OPTS`／`REVIEW_OPTS`／`FIX_OPTS`
      為單一常數家（單一骨架、`_sk_main*.js` 對應收斂），併入 000-r1 findings（`docs/reviews/20260904-doc-governance.md`：R1-080 review prompt 烤入
      `RULES_REVIEW`／RL-0070、R1-082 `harness-test.mjs` 斷言退出碼、R1-059／060／062／087／088 `EXAMPLE-single-implementer.mjs`／`EXAMPLE-dual-implementer.mjs` 重組）；
      `node tools/orchestration/harness-test.mjs` 十案綠；`docs/generated/reference/agents.md` 由 generate 重算；`docs/ops/BACKLOG.md` BL-00001 於收刀事件帶 backlog_done
      ✔ 已落（Task 0 commit）：單一 `_sk_head.js`／`_sk_main.js`（`IMPLEMENTERS` 移 `_vars`、`IMPL_STAGES` 泛化 1～N 支）、review 烤 `RULES_REVIEW`／fix 烤 `RULES_FIX`、harness 帶斷言退出碼（spec｜quality 二模式）、七支舊檔刪除；
      ✔ 回填已落（U1 收尾）：`tools/orchestration/EXAMPLE-dual-implementer.mjs`＝U1 組裝成品原樣、README 檔表同批列入
- [x] T002 前置體檢：`bash tools/bootstrap.sh` 綠（掃描防線＋rev5 凍結 SHA 斷言）；dev stack 機密解密（RUNBOOK §15、`deploy/`）；
      `docker compose -f docker-compose.yml -f docker-compose.dev.yml build migrate` 產 `rev6-admin-rust-api:dev`；容器內 `cargo --version`＝1.96.1
      ✔ 已落：bootstrap 綠（首跑 docsync 自測 6 案 drvfs 瞬時 getcwd ENOENT、重跑全綠 rc 0）；機密 13 檔在位；`rev6-admin-rust-api:dev` build rc 0；容器內 cargo 1.96.1／rustc 1.96.1／rustfmt 1.9.0-stable

---

## Phase 2: Foundational（阻斷性前置：骨架、例外①、entity、兩支閘工具）

**Purpose**: 未完成前不得開任何 user story——workspace 可建置、閘工具在場（US1 fixtures 產製與 US3 三閘皆消費之）

**⚠️ CRITICAL**: tools/ 兩支之 `test` 讀真 repo（data-model／archetype-map／fixtures），其 commit 必與 US1 T020、US3 T025 同單元（U2）

- [x] T003 `rust-api/Cargo.toml`：workspace members＝`["migration", "entity", "sea-orm-adapter"]`、`resolver = "2"`、`[workspace.package] edition = "2024"`、
      `[workspace.dependencies]` 恰五支＝sea-orm 1.1.20（default-features=false）／sea-orm-migration 1.1.20／tokio 1.53.1／async-trait 0.1.92／casbin 2.20.0
      （default-features=false）（research R1；註解 rev6 語境、承 `rev5:Cargo.toml` 形）
- [x] T004 [P] `rust-api/rust-toolchain.toml`（`channel = "1.96.1"`）＋`rust-api/rustfmt.toml`（max_width 100／use_small_heuristics Max／style_edition 2024；
      註解重寫、出處帶 `rev5:B-112`／`rev5:ADR 0057`）
- [x] T005 [P] `rust-api/migration/Cargo.toml`（sea-orm-adapter path＋sea-orm-migration features sqlx-postgres／runtime-tokio-rustls／cli＋tokio rt-multi-thread／net／time）
      ＋`rust-api/entity/Cargo.toml`（sea-orm features macros／with-chrono／with-json／with-ipnetwork）——承 `rev5:` 形自寫
- [x] T006 [P] `rust-api/sea-orm-adapter/`（§I.5 例外①整檔拷貝自 `../fork260509-rev5/rust-api/sea-orm-adapter/`：Cargo.toml＋`src/{action,adapter,entity,lib,migration}.rs`＋
      `examples/*`）：註解與字串之四型失效引用 rev6 化（前代編號帶前綴、章節號改指 rev6 去處）；`src/adapter.rs` 測試模組之假 DSN 字面改為執行期串接（RL-0054：憑證樣式不落完整字面；
      如 `format!("mysql://{}:{}@localhost:3306/casbin", "root", "123456")`）、零 allowlist；`betterleaks` 掃描零命中與「與 rev5 差一行」記 commit 訊息
- [x] T007 `rust-api/migration/src/lib.rs`（`mod m0001_baseline_schema; mod m0002_baseline_seeds;`＋`Migrator`，doc 註解 rev6）＋`rust-api/migration/src/main.rs`
      （`APP_DATABASE_URL_FILE`／`APP_DATABASE_URL` 解析、CHANGE-ME 拒啟、`run_cli`；檔頭契約註解 rev6、承 `rev5:main.rs` 形重打字）
- [x] T008 `rust-api/entity/src/lib.rs`（15 支 `pub mod`、自寫）
- [x] T009 [P] `rust-api/entity/src/{casbin_rule,session_event,sys_access_log,sys_casbin_policy_archive,sys_ip_rule,sys_login_attempt,sys_menu,sys_operation_log,sys_pwd_custody,sys_role,sys_token,sys_user,sys_user_email_verify,sys_user_role,system_settings}.rs`
      （§I.5 例外②：自 rev5 `92919b9` 照抄、程式零改；註解語意重寫——六檔各一處前代引用帶前綴；`sys_user_role.rs` 兩條真 FK Relation 保留）
- [x] T010 容器內 `cargo build --workspace`（serial；`docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --entrypoint cargo migrate build --workspace`——
      dev override 之 migrate entrypoint 已核可整段覆寫）綠；
      `rust-api/Cargo.lock` 入版控（async-trait 0.1.92 一處與 rev5 異、其餘同）
- [x] T011 `tools/schema-gate.py` 隨遷（自 `../fork260509-rev5/tools/schema-gate.py`；research R6）：座標常數同名核對；**去除** `SEED_DECISION` 與其讀取（sequence 名冊改自
      `fixtures/seed.sql` 之 `setval` 行解析）、`RENAME_MAP` 與 rev4 血緣對賬碼／測試、rev4 世代座標清償測試改 rev6 斷言；**保留** `RUNTIME_APPEND_TABLES`／`--container`／
      三子命令；`test` 加 negative 第五案（登記假 add_column 後合成期望值）；`doccheck` 加 data-model §9 sequences vs seed.sql setval 對賬面；docstring 與註解四型失效引用 rev6 化
      （`tools/docs-sync.py refresh`→`python3 tools/docsync refresh`、`specs/002` 殘留零容忍）
- [x] T012 [P] `tools/entity-drift-gate.py` 隨遷（自 rev5 同名檔）：座標常數同名核對；註解 `rev4:B-110`／`rev4:ADR 0015`／`rev4:ADR 0021` 帶前綴；`test` 逐案綠（離線）
- [x] T013 接線對賬（GT-09）：`README.md` 樹 `tools/` 下加 `schema-gate.py`／`entity-drift-gate.py` 兩行；`tools/bootstrap.sh` `run_tool_test` 加兩支；
      `.githooks/pre-commit` 自測名冊 `for t in …` 加兩支（staged 含工具本體才跑）

**Checkpoint**: workspace 建置綠、兩支工具在場（其 `test` 綠於 U2 commit 時與 fixtures／map 同批成立）

✔ U1 已落（T003～T010）：五支骨架檔＋adapter 十檔（程式面差三行＝假 DSN 執行期串接＋兩處 `#[ignore]` 訊息 rev6 化；`betterleaks dir` 零命中、零 allowlist）＋entity 15 檔（實查需改註解 9 檔、通用同文零改 6 檔——非「六檔各一處」）＋自寫 lib／main；容器內 `cargo build --workspace --locked` 綠、0 warning；Cargo.lock 以 `rev5:Cargo.lock` 為種子後 cargo 剪枝（372 套件、唯一版本異動 async-trait 0.1.89→0.1.92、零新增；零種子 resolve 踩坑＝LL-00001）；T011～T013 歸 U2。

---

## Phase 3: User Story 1 - 基線結構與 seed 逐位元承襲落地 (Priority: P1) 🎯 MVP

**Goal**: rev6 基線遷移兩支＝rev5 程式逐位元、檔名四碼；dev stack 重放成形；fixtures 自 rev6 pristine 萃取並與 rev5 雙源互證後凍結

**Independent Test**: quickstart A（17 檔 parity）＋B（重放兩支 applied）＋C（四檔 `cmp` 零差異）

### Implementation for User Story 1

- [x] T014 [P] [US1] `rust-api/migration/src/m0001_baseline_schema.rs`：`cp` 自 rev5 `m001_baseline_schema.rs`、程式零改；註解語意重寫（兩處裸 `rev4:m009`／`rev4` 引用帶前綴、
      檔頭改 rev6 語境；通用註解可同文）
- [x] T015 [P] [US1] `rust-api/migration/src/m0002_baseline_seeds.rs`：`cp` 自 rev5 `m002_baseline_seeds.rs`、程式零改（PHC 常數、定稿時戳 `2026-08-05T00:00:00+00:00` 字面照舊）；
      註解中 seed-decision.json／seed-review.md 引用改指 `rev5:` 史料與 `fixtures/seed.sql`
- [x] T016 [US1] 17 檔 parity 自證（quickstart A；ADR-00009 ①命令形）：`strip()` diff 逐檔零輸出＋`python3 tools/docsync lint` GT-05 綠；結果（檔數、rc）記 rust-api commit 訊息
      與外層 pin bump 訊息
- [x] T017 [US1] dev stack 重放：`docker compose … up -d --wait postgres` → `run --rm migrate`；驗 `seaql_migrations` 恰兩筆＝`m0001_baseline_schema`／`m0002_baseline_seeds`；
      `SHOW timezone`＝`UTC`
- [x] T018 [US1] pristine 一次性重放：`docker network create rev6-u2-fixnet`＋`postgres:18.4-alpine` 容器 `rev6-u2-fixpg`（零 host 埠、拋棄式密碼）→ 以 `rev6-admin-rust-api:dev`
      容器內 `cargo run --bin migration up`（`APP_DATABASE_URL` 指向該容器）→ `python3 tools/schema-gate.py check --container rev6-u2-fixpg` gate2 欄序面綠
- [x] T019 [US1] 照相與雙源互證：以 schema-gate 三查詢照相 `columns.json`／`indexes.json`／`constraints.json`（確定性排序、indent 2）＋`pg_dump --data-only`（PGTZ=UTC）經
      `normalize_seed_dump` → 四檔 `cmp` 對 `../fork260509-rev5/specs/001-schema-baseline/fixtures/` 同名檔**零差異**；任一不全等＝停手升級 user（status＝blocked）
- [x] T020 [US1] 凍結面落檔 `specs/001-schema-baseline/fixtures/{columns.json,indexes.json,constraints.json,seed.sql,provenance.md}`（provenance 六欄目＝contracts/fixtures.md §3：
      日期／映像／rust-api commit SHA／rev5 來源座標＋cmp 紀錄／欄序驗紀錄／命令形）；拆容器、network、匿名 PGDATA volume（`docker volume ls -f dangling=true` 核對）

**Checkpoint**: 基線可獨立驗證交付——重放成形、與 rev5 逐位元同形、凍結面就位

✔ U1 已落（T014～T017）：m0001／m0002 `cp`＋註解語意重寫；17 檔 parity 17/17 零輸出（fmt 後復驗同）、lint 0 錯；dev stack 重放 `seaql_migrations` 恰兩列四碼名、`SHOW timezone`＝UTC、public 16 表、sys_user 3 列；T018～T020 歸 U2。

---

## Phase 4: User Story 2 - 拷貝例外開立與承襲紀律 (Priority: P1)

**Goal**: 例外先於行為開立（已落）；四條件證據齊備、機器閘綠

**Independent Test**: 憲法 1.1.0＋ADR-00009 accepted 在場；lint GT-05 綠；防回歸清單與註解改寫清單在 commit 訊息／ADR-00010 證據段可查

### Implementation for User Story 2

- [x] T021 [US2] 憲法 §I.5 例外②＋§V.3 補句＋1.1.0＋ADR-00009 accepted（`.specify/memory/constitution.md`、`docs/arc42/decisions/ADR-00009-data-shape-copy-exception.md`；
      已落 52fb52f、早於 plan）
- [x] T022 [US2] 註解語意重寫清單：17 檔＋adapter 逐檔列出四型失效引用之改寫項（原文→rev6 文；通用同文者免列），落 rust-api commit 訊息並作 ADR-00010 證據素材
- [x] T023 [US2] 防回歸審查：`git -C ../fork260509-rev5/rust-api diff 4bbc989 92919b9 -- entity/src migration/src` 實查後刀差異 → 清單（預期唯一＝`sys_user_role.rs` 真 FK
      Relation、形狀派生保留；`m001` 之 fmt 存量與註解變動屬非語意）→ 記 ADR-00010 證據段
- [x] T024 [US2] 機器閘證據：`python3 tools/docsync lint` 0 錯（GT-05 掃 tools/ 與子庫 pin 樹）；`betterleaks git --config .gitleaks.toml` 全史掃描結果（零命中、零 allowlist——adapter 假 DSN 依 T006 改執行期串接、analyze C1）記 commit 訊息

**Checkpoint**: 例外依規則成立、四條件證據在案

✔ U1 已落（T022／T024）：註解改寫清單（23 檔機器對賬、14 檔差異逐項）落 rust-api 本單元 commit 訊息＝ADR-00010 證據素材；lint 0 錯、`betterleaks dir rust-api` 與 `betterleaks git` 全史皆零命中；T023 歸 U2。

---

## Phase 5: User Story 3 - 驗證閘＝Day-1 受管演進帳 (Priority: P2)

**Goal**: 三閘＋演進登記檔就位並往返驗證；ADR-00010 accepted

**Independent Test**: quickstart D（check／test／doccheck）＋E（往返四步）

### Implementation for User Story 3

- [x] T025 [US3] `docs/ops/reference-src/archetype-map.json`（承 rev5 同名檔改座標：`lineage`／`usage` 字串 rev6 化、15 表條目位元不動、與 data-model §1 逐筆對賬）＋
      `docs/ops/reference-src/schema-evolution.json`＝`{"next_id": 1, "entries": []}`
- [x] T026 [US3] `python3 tools/schema-gate.py test` 全綠（真 repo 案：data-model 解析／map Day-1 形／真 repo 基線 rc 0；negative 五類含假 delta 合成）；
      `python3 tools/schema-gate.py doccheck` rc 0（§2 五元組＋§6 索引約束＋§9 sequences vs fixtures）
- [x] T027 [US3] `python3 tools/schema-gate.py check`（dev stack）rc 0：gate1／gate2 欄序＋seed／audit archetype 15/15 三閘摘要各一行；記 perf（秒數）
- [x] T028 [US3] 演進帳往返驗證（quickstart E）：注入 `ALTER TABLE sys_user ADD COLUMN tmp_x text` → rc 1 指名；登記 `E-001`（knife `001-schema-baseline`）→ rc 0；
      刪 `date` 欄 → rc 2；還原（撤登記＋DROP COLUMN）→ rc 0；四步輸出記 commit 訊息
- [x] T029 [US3] `docs/arc42/decisions/ADR-00010-schema-baseline-and-gate-contract.md`：證據段補齊（T016 parity、T019 cmp、T023 清單、T027 首跑）→ `status: accepted`；
      `python3 tools/docsync generate`（DECISIONS-INDEX／STATE 重算）

**Checkpoint**: 閘可獨立往返驗證；ADR-00010 accepted（此後 body 不可變）

✔ U2 已落（T011～T013、T018～T020、T023、T025～T029）：兩支閘工具隨遷（schema-gate 2,522→2,639 行、`test` 103 案；entity-drift 45 案）＋接線三處；pristine 重放（`rev6-u2-fixpg`）→ `check --container` 四行綠 → 四檔 `cmp` vs rev5 fixtures 逐位元零差異（sha256 載 provenance §4）→ 凍結五件＋拆除零殘留；archetype-map（tables 15 筆位元不動）／schema-evolution 初版；T023 後刀差異 5 檔清單（m001 fmt 中性自證）；dev stack `check` rc 0（1.27 秒）；往返四步 rc 1→0→2→0 還原；ADR-00010 證據四項補齊→accepted；contracts §4「四類／SC-002」與 fixtures §1§4／research R5「Owner 自始正規化」措辭漂移於本收尾更正（產製形恰四項、③④屬比對期）。

---

## Phase 6: User Story 4 - entity 對應層與漂移防線 (Priority: P3)

**Goal**: entity-drift 常跑 pre-commit（Day-1 跳過→快照就位實跑）、缺席演練被擋

**Independent Test**: quickstart F

### Implementation for User Story 4

- [x] T030 [US4] `.githooks/pre-commit` 加 entity-drift 段：staged 含 `rust-api` gitlink 或 `docs/ops/reference-src/schema-snapshot.json` 時——快照在場→
      `pc_run "entity-drift" python3 tools/entity-drift-gate.py check`、缺席→一行「⤳ entity-drift 跳過：schema 快照缺席（就位後自動實跑）」；雙錨 45／90 不動
- [x] T031 [US4] 演練：快照就位後 `python3 tools/entity-drift-gate.py check` rc 0；暫移 `rust-api/entity/src` → 對 rust-api pin bump 之 commit 被 rc 2 擋下 → 還原後綠；
      結果記 commit 訊息

**Checkpoint**: 帳面與程式側漂移在 commit 時被攔

✔ U3 已落（T030～T035）：`tools/docsync/snapshot.py`（六撈／refresh／兩生成器、208 行）＋`tests/test_snapshot.py`（先紅 ImportError→綠；docsync test 91→117）＋接線（GENERATED_FILES 12→14、`refresh` 子命令）＋兩快照（columns 169／indexes 38／constraints 101、users 3／roles 3／bindings 3；與 U2 fixtures 三 json 逐列相等、與 rev5 快照位元相同、二次 refresh 位元冪等）＋兩真表（表體與 rev5 逐位元相同、FR-002 三帳成立）＋pre-commit entity-drift 段（閘級演練 rc 0→2→0／0→1→0 零殘改；hook 面演練於 U3 外層 commit 親做、結果記該 commit 訊息）。編排＝三 run：主 run 兩支 implementer 後於規格審查段走 rev5:L-078 升級（README 樹行已兌現預告）→ 主線落地並加骨架 IMPLEMENTERS=0 續跑形 → 續跑 run 1 再升級（README `docs/generated/` 成員列舉未隨名冊補）→ 主線全掃同語意四處落地 → 續跑 run 2 收斂（規格 1 輪＋品質 1 輪零 blocker）；碼品質 notes 三分流見 U3 commit 訊息；BL-00009／BL-00010、LL-00002 隨 U3 落。

---

## Phase 7: User Story 5 - 參考真表與 DoD 鏈 (Priority: P4)

**Goal**: `refresh` 照相→兩快照→兩張真表；RUNBOOK／活書／README 補齊；DoD 鏈全綠

**Independent Test**: quickstart G

### Tests for User Story 5（先紅）

- [x] T032 [P] [US5] `tools/docsync/tests/test_snapshot.py`：合成六撈→兩快照→`gen_reference_schema`／`gen_reference_accounts` 內容斷言（表×變體、零密碼欄）；
      ★回填條（U2 收尾登記）：三 SQL 常數同構對賬——`rev5:TestSnapshotIsomorphism` 已自 `tools/schema-gate.py` 移除，本檔須讀 `tools/schema-gate.py` 文本（importlib 依路徑載入）比對 `SQL_COLUMNS`／`SQL_INDEXES`／`SQL_CONSTRAINTS` 三常數與 `snapshot` 模組逐一相等；
      反向：快照缺檔／壞 JSON／綁定指向不存在 role／map 缺表歸屬＝fail-loud；refresh 任一撈失敗＝不寫部分結果

### Implementation for User Story 5

- [x] T033 [US5] `tools/docsync/snapshot.py`：`SQL_COLUMNS`／`SQL_INDEXES`／`SQL_CONSTRAINTS`／`SQL_USERS`／`SQL_ROLES`／`SQL_BINDINGS`（json_agg 形、排除 seaql_migrations）、
      `psql_fetch`（`docker compose … exec -T postgres psql -U soybean -d soybean_admin_rust -qAt`、stack 缺席 fail-loud＋啟動提示）、`build_schema_snapshot`／`build_accounts_snapshot`
      （確定性排序）、`cmd_refresh`（六撈全成功才原子落檔）、兩生成器——承 `rev5:docs-sync.py` 先讀後寫、重打字、`Ctx` 注入
- [x] T034 [US5] `tools/docsync/references.py`：`GENERATED_FILES` 加 `docs/generated/reference/schema.md`／`accounts.md`（12→14）、`compute_generated` 掛兩鍵（讀
      reference-src 三檔、缺檔 fail-loud 指引 refresh）；`tools/docsync/__main__.py` 加 `refresh` 子命令；`python3 tools/docsync test` 全綠
- [x] T035 [US5] DoD 鏈：`python3 tools/docsync refresh`（dev stack）→ `docs/ops/reference-src/{schema,accounts}-snapshot.json` → `generate` → `docs/generated/reference/{schema,accounts}.md`
      → `check` 零漂移 → `lint` 0 錯（GT-01／GT-09／GT-12 閘數 12）；`accounts.md` 列 Super／Admin／User 三帳與角色綁定同 rev5（FR-002 斷言）——與 T033／T034 同一 commit 落地（無 stub）
- [ ] T036 [US5] 文件：`docs/ops/RUNBOOK.md` §10 實文（三步常設程序、rev6 命令形）、§12 表加 `schema-gate.py check｜test｜doccheck`／`entity-drift-gate.py check｜test`／
      `docsync refresh` 三列（需 stack 欄）、§9 補 psql 直連一句、§14 帳號節核對（dev 三帳承 rev5、指向 accounts.md）；`docs/arc42/05-building-block-view.md` §5.1 樹列 rust-api 三 member、§5.2 rust-api 句改現在式、
      frontmatter `rev5_blueprint` §5 列「隨刀」→「承襲」；`docs/arc42/08-crosscutting-concepts.md` §8.1 指針句核對（真表已生成）；
      ★U3 收尾補列（U4 定義已涵蓋、本行原缺）：`docs/c4/C4-E2-data-lineage-overlay.md` 提及「隨 schema 基線刀」三句、`docs/process/P-E3-doc-pipeline.md` 「隨 schema 基線刀進場」一句改現在式
- [ ] T037 [US5] pre-commit 全鏈實測（含 entity-drift 實跑、工具自測條件觸發）≤45s → `docs/ops/events.jsonl` append perf 事件（隨該單元 commit）

**Checkpoint**: 查現況正典入口就位、全鏈綠

---

## Phase 8: User Story 6 - 治理與帳本落帳 (Priority: P5)

**Goal**: BL-00005 處置、BACKLOG／LESSONS 落帳

**Independent Test**: lint 全綠；BACKLOG 條目狀態正確；GT-03 於收刀事件實跑綠

### Implementation for User Story 6

- [ ] T038 [US6] **BL-00005**（拍板級、user 親決）：事件欄無家群（misc.workflow、feature_close.kind／spec_supersessions、非 perf 型 notes）補渲染或刪欄——
      `tools/docsync/events.py`／`references.py`（MILESTONES／STATE 渲染）＋一正一反自證；若改 schema 立 `docs/arc42/decisions/ADR-00011-*.md`；`docs/ops/BACKLOG.md` 標處置
- [ ] T039 [US6] `docs/ops/BACKLOG.md`：BL-00001 消化紀錄（收刀 misc／feature_close 事件帶 backlog_done）；append「STATE 預算表納 docsync 行數對賬」條目（取檔頭 next 配號）；
      `docs/ops/LESSONS/` 首條 LL（任一單元踩坑即落、解除 GT-08.lessons-absent）

---

## Phase 9: Polish & Cross-Cutting

- [ ] T040 勘誤掃描：`python3 tools/docsync errata m001`／`m002`／`docs-sync.py`／`seed-decision`（本刀改變的字面）逐處處置、含兩子庫 pin 樹
- [ ] T041 quickstart A～G 全場景復跑（含三閘 `check` 復跑＝FR-013 順序面）＋`cat tools/docsync/*.py | wc -l` 記 docsync 行數落點（SC-007、入收刀事件 notes）
      ＋tasks 全勾對賬 spec SC-001～SC-007（final holistic review 輸入；不落報告、處置列於收單 commit 訊息）

---

## 執行單元對映（research R11；主線派發粒度、每單元一顆外層 commit）

| 單元 | 任務 | 收尾產物 |
|---|---|---|
| Task 0 | T001、T002 | 骨架收斂 commit（外層）；映像就緒 |
| U1 | T003～T010、T014～T017、T022、T024 | rust-api commit（17 檔＋adapter＋骨架、parity 結果入訊息）→ 外層 pin bump |
| U2 | T011～T013、T018～T020、T023、T025～T029 | 外層 commit：兩工具＋fixtures 五件＋map／ledger＋ADR-00010 accepted＋README／bootstrap／hook 名冊 |
| U3 | T030～T035 | 外層 commit：snapshot.py＋tests＋兩快照＋兩真表＋entity-drift 段 |
| U4 | T036、T037、T040、T041 | 外層 commit：RUNBOOK／活書／perf 事件 |
| U5 | T038、T039 | 外層 commit：BL-00005 處置（可能 ADR-00011）＋BACKLOG／LESSONS |

## Dependencies

- Phase 1 → Phase 2 → US1；US2 之 T022～T024 依 US1 T014～T016 與 Foundational T009；US3 依 US1 T020（fixtures）與 Foundational T011；
  US4 依 US5 T035 之快照（T031 演練在快照就位後）；US5 依 US3 T025（map）；US6 T038 拍板級、僅依主線可派時點（收刀前）。
- 阻斷型：T019 不全等＝blocked 升級 user；T029 accepted 後 ADR-00010 不可變；T038 需 user 親決。

## Parallel Execution Examples

- Foundational：T004／T005／T006／T009 四項不同檔可平行；T011／T012 可平行。
- US1：T014／T015 可平行；T016 待兩者。
- US5：T032（先紅）與 T033 可分工，T034 待 T033。

## Implementation Strategy

- **MVP**＝Phase 1＋Phase 2＋US1＋US2（＝Task 0＋U1＋U2 之 fixtures 面）：基線成形、與 rev5 逐位元同形、例外證據在案。
- 增量：US3（閘）→ US4／US5（防線與真表）→ US6（帳本）；每單元收尾六步序（復核→自驗→落帳→子庫 commit→pin bump＋generate→外層 commit）。
- 收刀：final holistic review → finishing（push／merge 需 user 當回合同意）→ 簿記三步（feature_close window 1、adrs [ADR-00009, ADR-00010]）→ perf 第四步。
