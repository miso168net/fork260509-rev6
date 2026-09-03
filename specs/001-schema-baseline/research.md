# research — 001-schema-baseline（Phase 0）

> Technical Context 零 NEEDS CLARIFICATION（座標由既有 repo 工件與 rev5 藍本定死）；本檔記施工級拍板（工程判斷、回報備查）
> 與 user 拍板（版本三源）。全部 Decision 均接地實查：rev5 對應檔逐一開過（唯讀、凍結 SHA 外層 `7eab28a`／rust-api `92919b9`）。
> ★CLAUDE.md §2 要求＝「rev5 對應碼清單＋rev6 拍板差異點」＝§R0。

## R0 rev5 對應碼清單與 rev6 拍板差異點

| rev5（`rev5:` 唯讀） | rev6 落點 | 處置 | rev6 差異點 |
|---|---|---|---|
| `rust-api/Cargo.toml` | 同路徑 | 自寫、承形 | members 去 `server`（隨 002）；`workspace.dependencies` 首刀子集 5 支；`async-trait` 0.1.92（R1） |
| `rust-api/Cargo.lock` | 同 | 容器內 cargo 產、入版控 | async-trait 一處異、其餘同 rev5 |
| `rust-api/rust-toolchain.toml` | 同 | 自寫 | `1.96.1`＝deploy/Dockerfile.rust-api 同值 |
| `rust-api/rustfmt.toml` | 同 | 三值承襲、註解重寫 | 註解之 `rev5:B-112`／`rev5:ADR 0057` 帶前綴；rust-fmt-gate 隨 002 |
| `rust-api/migration/Cargo.toml`、`entity/Cargo.toml` | 同 | 自寫、承形 | features 恰同（R3／R4） |
| `rust-api/migration/src/lib.rs`、`main.rs` | 同 | 自寫（sea-orm-cli 樣板＋承形） | `mod m0001_…`／`m0002_…` 四碼；doc 註解 rev6 語境 |
| `rust-api/migration/src/m001_baseline_schema.rs` | `m0001_baseline_schema.rs` | **§I.5 例外②**：程式逐位元照抄、改名、註解語意重寫 | 兩處裸 `rev4:m009`／`rev4` 引用帶前綴；`seaql_migrations` 記錄名隨檔名 |
| `rust-api/migration/src/m002_baseline_seeds.rs` | `m0002_baseline_seeds.rs` | 同上 | 註解引 seed-decision.json 者改指 `rev5:` 史料與 fixtures/seed.sql |
| `rust-api/entity/src/lib.rs` | 同 | 自寫 | 15 `pub mod` 同 |
| `rust-api/entity/src/*.rs`（15 檔） | 同 | **§I.5 例外②**：照抄、註解語意重寫 | 六檔各一處前代引用帶前綴；`sys_user_role` 兩條真 FK Relation（`rev5:002` FR-022）保留 |
| `rust-api/sea-orm-adapter/**`（Cargo.toml＋src 5 檔＋examples） | 同 | **§I.5 例外①**整檔拷貝 | 註解四型失效引用 rev6 化；測試碼假 DSN 字面改執行期串接（RL-0054、analyze C1 2026-09-04；零 allowlist、與 rev5 差一行） |
| `tools/schema-gate.py`（2,522 行） | 同 | **隨遷工具**（RULES 名詞段） | 去 `SEED_DECISION`／`RENAME_MAP`／rev4 血緣殘留、座標同名、容器名前綴、註解 rev6 化（R6） |
| `tools/entity-drift-gate.py`（780 行） | 同 | 隨遷工具 | 座標同；`rev4:B-110`／`rev4:ADR 0015`／`rev4:ADR 0021` 帶前綴 |
| `tools/docs-sync.py` 之 `psql_fetch`／`cmd_refresh`／`build_*_snapshot`／`SQL_*`／`gen_reference_schema`／`gen_reference_accounts` | `tools/docsync/snapshot.py`（新）＋`references.py`（掛生成器） | **重打字**（一般碼、非例外；§I.5 先讀後寫） | package 形、`Ctx` 注入、GENERATED_FILES 12→14（R8） |
| `specs/001-schema-baseline/data-model.md` | 同 | 整檔承襲改座標（文件；clarify／grill 拍板） | 檔頭權威聲明 rev6 化；§8 seed 權威＝m0002 本體＋fixtures；§10 加 entity 差異；解析面（§2／§6／§7 表體）位元不動 |
| `specs/…/contracts/{gates,schema-evolution,fixtures}.md` | 同 | 整檔承襲改座標 | 血緣核對（vs rev4）→ 雙源互證（vs rev5 fixtures）；rev5 具名重產例外不承襲 |
| `specs/…/fixtures/*`（五件） | 同 | **不拷**：自 rev6 pristine 產、與 rev5 逐位元比對 | provenance.md 自寫（六欄目形承） |
| `specs/…/seed-decision.json`／`seed-review.md`／`seed-net-effect.json` | —— | 不搬（rev5 定稿史料、唯讀引用） | seed 內容權威＝`m0002` 本體（逐位元）＋凍結 `fixtures/seed.sql` |
| `docs/ops/reference-src/archetype-map.json` | 同 | 承襲改座標（資料檔） | `lineage`／`usage` 字串 rev6 化；15 表內容不動 |
| `docs/ops/reference-src/schema-evolution.json` | 同 | 初版零筆（形同） | —— |
| `docs/ops/reference-src/{schema,accounts}-snapshot.json` | 同 | refresh 自 rev6 實庫產 | —— |
| `.githooks/pre-commit` entity-drift 段＋自測名冊 | 同 | 承形重寫 | rev6 `pc_run` 形；名冊加兩支；bootstrap `run_tool_test` 加兩支 |
| `docs/ops/RUNBOOK.md` §10 | 同 | 承襲改座標 | 命令形 `python3 tools/docsync refresh`／`tools/schema-gate.py check` |
| `docs/arc42/decisions/0006`、`0007` | ADR-00009（已 accepted）、ADR-00010（proposed→accepted） | rev6 自立、背景引 `rev5:ADR 0006`／`rev5:ADR 0007` | 憲法例外②＝rev6 獨有 |
| `tools/rust-fmt-gate.py`、`tools/wire-schema.py`、walkthrough 工具 | —— | 不入刀 | 隨 002／server 刀／首個走查刀 |

**rev6 拍板差異點總表**：①migration 檔名四碼（ADR-00008）②憲法 §I.5 例外②＋四條件（ADR-00009；註解語意判準）③seed 權威＝m0002 本體、無 seed-decision.json
④血緣核對（vs rev4）→ 雙源互證（vs rev5 fixtures）⑤`async-trait` 0.1.92（user 2026-09-04）⑥docsync 為 package（snapshot.py）⑦閘數恆 12、碼面閘不入名冊
⑧單元序（R11）⑨rust-fmt-gate 隨 002。

## R1 版本策略＝三源核對（全域 §6；user 拍板 2026-09-04）

| 相依 | rev5 Cargo.lock | crates.io stable（2026-09-04 實查） | 拍板 |
|---|---|---|---|
| sea-orm／sea-orm-migration | 1.1.20 | 2.0.2 | **1.1.20**——2.0 破壞性 API 改動使逐位元承襲（FR-001）不成立、vendored adapter 針對 1.x；升 2.x 留日後獨立維護批 |
| tokio | 1.53.1 | 1.53.1 | **1.53.1**（同值直採；brainstorm 原載 1.52.3 為誤植、grill 已更正） |
| async-trait | 0.1.89 | 0.1.92 | **0.1.92**（user 選最新 patch；僅 adapter 使用；Cargo.lock 與 rev5 一處異） |
| casbin | 2.20.0 | 2.20.0 | **2.20.0**（同值直採；`default-features=false`） |
| rust toolchain | 1.96.1（rev5＋rev6 Dockerfile） | 1.98.1 | **1.96.1**——與既有 `deploy/Dockerfile.rust-api` 同值、零改 deploy；升版屬 deploy 面維護批 |

- features 恰同 rev5：migration＝`sea-orm-migration` sqlx-postgres／runtime-tokio-rustls／cli＋`tokio` rt-multi-thread／net／time；entity＝`sea-orm` macros／with-chrono／with-json／with-ipnetwork；
  adapter＝`casbin` default-features=false＋`sea-orm` macros＋dev `tokio` full。**不引 argon2**（PHC 常數、無 runtime 雜湊；承 `rev5:R1`）。
- 域外者不進（承 `rev5:ADR 0032` 形）：本刀不引任何 auth／web 依賴。

## R2 建置／執行容器策略（rev6 座標）

- **Decision**：日常路徑＝compose `migrate` 服務（`rev6-admin-rust-api:dev`、`APP_DATABASE_URL_FILE=/run/secrets/database_url`；`docker compose … run --rm migrate`）；
  dev stack 只起 `up -d --wait postgres`（server 缺席、rust-api 服務起不來屬預期）。pristine 驗證＝一次性 `postgres:18.4-alpine`＋獨立 network、零 host 埠、
  容器名前綴 `rev6-u2-fix*`、用畢即拆（含匿名 PGDATA volume）。cargo 一律容器內 serial；target／registry 走 compose named volume（project `rev6-admin`）。
- **Rationale**：承 `rev5:R2`（已實證）；rev6 compose 已預接線；named volume 非 pristine、驗證鏈要乾淨初始化；獨立 network 免碰埠治理（ADR-00001）。
- **Alternatives**：對 dev stack postgres 重放——放棄（volume 殘留、refresh 快照面被污染）。

## R3 m0001／m0002 施工形＝逐位元承襲＋改名＋自證

- **Decision**：`rev5:m001`／`rev5:m002` 原檔以 `cp` 落 `m0001_baseline_schema.rs`／`m0002_baseline_seeds.rs`，**程式零改動**；註解依語意判準重寫（ADR-00009 ②）；
  `lib.rs` 的 `mod` 名與 `migrations()` 向量四碼。自證命令形（ADR-00009 ①；兩邊各自）：
  ```sh
  strip() { grep -vE '^[[:space:]]*//' "$1" | sed -E 's/[[:space:]]+$//' | sed '/^$/d'; }
  diff <(strip ../fork260509-rev5/rust-api/migration/src/m001_baseline_schema.rs) <(strip rust-api/migration/src/m0001_baseline_schema.rs) && echo "m0001 parity OK"
  ```
  期望零輸出；結果（rc＋行數）記 commit 訊息與收刀 `feature_close` 事件 notes。
- **Rationale**：rev5 m002／entity 程式面零引用 `m001` 模組名（實查：只有自寫 lib.rs 引用），改名不動兩支內容；rev5 三件零行內尾註解，
  「刪整行註解」判準無歧義；rev5 存量已 `cargo fmt`（`rev5:d940d03`）、空白規則穩定。
- **Alternatives**：保留三碼檔名——已被 ADR-00008 否決。

## R4 entity 15 檔承襲形

- **Decision**：15 檔照抄（§I.5 例外②）＋註解語意重寫；`lib.rs` 自寫（15 `pub mod`）；sea-orm features 恰四項；`casbin_rule.rs` 在場、drift 比對豁免該表（承 `rev5:R8`）。
  後刀差異唯一＝`sys_user_role.rs` 之兩條真 DB FK `Relation`＋`Related` impl（`rev5:002` FR-021／FR-022「僅真 FK 建 Relation」）：形狀派生、**保留**、清單記 ADR-00010。
- **Rationale**：entity-drift 左源＝rev6 快照（欄名＝rev5 定稿名）→ entity 必同名；rev5 entity 在 001 後只此一處變動（`git log` 實查 2 commits）。

## R5 fixtures 凍結格式＋雙源互證

- **Decision**：`fixtures/` 五件形承 `rev5:R5`：`columns.json`／`indexes.json`／`constraints.json`（三查詢同構、確定性排序、indent 2）＋`seed.sql`
  （`pg_dump --data-only`、PGTZ=UTC，經 schema-gate `normalize_seed_dump`：COPY 段整列排序＋setval 原位＋剝 `\restrict`／`\unrestrict` 行＋剝 `seaql_migrations` COPY 段＋
  Dumped 版本兩行剝除＋`Owner:` 值正規化）＋`provenance.md`（六欄目）。**先驗後凍**＝①vs data-model §2 欄序全等 ②四份資料檔 vs `rev5:specs/001-schema-baseline/fixtures/` 同名檔
  **逐位元全等**（雙源互證；provenance 不比）——兩綠才落檔；任一不全等＝停手升級 user。
- **Rationale**：rev5 fixtures 已剝 `seaql_migrations` 段（實查零命中），四碼改名不破全等；Owner 正規化使 DB 身分無關。
- **Alternatives**：直接拷 rev5 fixtures——放棄：凍結面必須是 rev6 自己重放的證據，拷來即無「rev6 基線＝rev5 終態」的實證。

## R6 兩支閘工具隨遷改座標清單

- **Decision**（`tools/schema-gate.py`）：
  - 座標常數同名不動：`FIXTURES_DIR`／`DATA_MODEL`／`LEDGER`／`ARCHETYPE_MAP`／`DB_USER`／`DB_NAME`／`COMPOSE_EXEC`（rev6 compose 檔名同、DB 身分同）。
  - **去除**：`SEED_DECISION` 常數與 sequence 名冊讀取（改自 `fixtures/seed.sql` 之 `setval` 行解析、data-model §9 由 doccheck 對賬）；`RENAME_MAP` 與一切 rev4 血緣對賬碼／測試；
    rev4 世代座標清償測試（`test_…rev4…`）改為 rev6 座標斷言。
  - **保留**：`RUNTIME_APPEND_TABLES` 四表收窄（`rev5:B-065`；資料形狀同、server 刀後即需要）；`--container`／`--user`／`--db`；三子命令 `check`／`test`／`doccheck`；退出碼語意。
  - 註解與字串：四型失效引用 rev6 化（`rev4:ADR 0015`、`rev5:B-010`、`rev5:K1-39` 等前綴；`tools/docs-sync.py refresh` → `python3 tools/docsync refresh`；`specs/002` 殘留零容忍）。
- **Decision**（`tools/entity-drift-gate.py`）：座標同名（`SNAPSHOT_REL`／`ENTITY_DIR_REL`／`SKIP_TABLES`／`TYPE_MAP`）；註解前綴化；`test` 逐案綠。
- **Rationale**：隨遷工具＝逐字承襲允許、四型失效引用須 rev6 化（RULES 名詞段）；rev5 seed-decision.json 不搬則其唯一消費點必改；rename map 是 rev4 血緣、rev6 無此場景。
- **Alternatives**：重寫兩支工具——放棄（3,302 行已驗證、隨遷授權在案）。

## R7 演進登記檔＝承 rev5 形、零改

- **Decision**：`docs/ops/reference-src/schema-evolution.json` 初版 `{"next_id": 1, "entries": []}`；形、kind 八值、啟動斷言七條＝contracts/schema-evolution.md（承 `rev5:R7`）。
  ★rev5 終態亦零筆——合成邏輯無真 delta 實證，本刀 `test` 加「登記一筆假 add_column 後合成期望值」案（spec FR-009）。

## R8 docsync 新增＝`snapshot.py`＋兩生成器

- **Decision**：新模組 `tools/docsync/snapshot.py`：`SQL_COLUMNS`／`SQL_INDEXES`／`SQL_CONSTRAINTS`／`SQL_USERS`／`SQL_ROLES`／`SQL_BINDINGS` 六撈（json_agg 形）、`psql_fetch`
  （compose exec postgres psql、stack 缺席 fail-loud＋啟動提示）、`build_schema_snapshot`／`build_accounts_snapshot`、`cmd_refresh`（六撈全成功才原子落兩檔）、
  `gen_reference_schema`／`gen_reference_accounts`；`references.py` 之 `compute_generated` 掛兩鍵、`GENERATED_FILES` 加 `reference/schema.md`／`accounts.md`（12→14）；
  `__main__.py` 加 `refresh` 子命令；tests 新增 `test_snapshot.py`（一正一反：合成快照→真表；缺檔／壞 JSON／綁定指向不存在 role＝fail-loud）。
  **無 stub、無 Day-1 豁免**：生成器與兩快照＋archetype-map **同一單元同一 commit** 落地（GT-01 零漂移不開洞）。
- **Rationale**：rev6 docsync 為 package（`Ctx` 注入），rev5 單檔函式不可整檔拷（一般碼、§I.5 先讀後寫重打字）；估約 250 行→docsync 約 2,600／啟動書目標 4,000（GT-12 無此預算）。
- **Alternatives**：沿 rev5 `gen_reference_stub`＋Day-1 豁免——放棄：閘數已 12/12、GATES 名冊不動（brainstorm §4）。

## R9 接線＝hook／README／bootstrap／RUNBOOK

- `.githooks/pre-commit`：自測名冊 `for t in …` 加 `tools/schema-gate.py`／`tools/entity-drift-gate.py`；新增 entity-drift 段（staged 含 `rust-api` gitlink 或 `schema-snapshot.json` 時：
  快照在場→`pc_run "entity-drift" python3 tools/entity-drift-gate.py check`、缺席→一行跳過訊息）；雙錨 45／90 秒不動、實測記 perf 事件。
- `tools/bootstrap.sh`：`run_tool_test` 加兩支（與 pre-commit 名冊對賬、GT-09）。
- `README.md` 樹：`tools/` 下加兩行（GT-09 README 樹 vs 實檔集）。
- `docs/ops/RUNBOOK.md`：§10 補實文（三步常設程序、命令形 rev6）；§12 表加兩列（`python3 tools/schema-gate.py check｜test｜doccheck`＝需 stack（check）／否；`python3 tools/entity-drift-gate.py check｜test`＝否）
  ＋`python3 tools/docsync refresh`＝需 stack；§9 補 psql 直連一句（`docker compose … exec postgres psql -U soybean -d soybean_admin_rust`、絕不指 rev5 庫）；§14 帳號節指向 accounts.md 已在。

## R10 治理落點

- ADR-00009 已 accepted（52fb52f）；ADR-00010（schema 基線與閘契約）於 plan 落 `proposed`、U2 收尾（fixtures 雙源互證與 entity 差異清單為證據）轉 `accepted`（GT-04：accepted 後不可變）。
- BL-00001＝Task 0（開分支後、首個 Workflow 前）：`_sk_head*.js` 三變體 `*_OPTS` 收斂單一常數家與單一骨架（governance）。BL-00005＝U5（收刀前、拍板級 user 親決）。BL-00002 不觸發。
- 活書：`docs/arc42/05` §5.1 樹列與 §5.2 rust-api 句、frontmatter `rev5_blueprint` §5 列「隨刀」→「承襲」；`docs/arc42/08` §8.1 指針句現文已指 `reference/schema.md`（隨刀生成即成立、零改或微調）；C4-L2 零改。
- LESSONS 首條（U1 起任何踩坑）即解除 GT-08.lessons-absent；收刀 BACKLOG append「STATE 預算表納 docsync 行數對賬」；`feature_close` window＝1、adrs＝[ADR-00009, ADR-00010]。

## R11 單元切分修正（工具自測讀真 repo）

- **Decision**：rev5 `schema-gate.py test` 含 `test_real_data_model_parses`／`test_real_map_day1_form`／`test_real_repo_green_rc0`（讀真 data-model、archetype-map、fixtures）
  → 工具、fixtures、archetype-map 必須同單元落地。修正後：**U1** 骨架＋17 檔拷貝＋adapter＋build＋dev stack migrate up →
  **U2** 兩工具隨遷＋pristine 重放＋fixtures 產製與雙源互證＋archetype-map／schema-evolution 初版＋兩工具自測綠＋ADR-00010 accepted →
  **U3** docsync snapshot.py＋refresh 首跑＋兩快照＋兩生成器＋entity-drift hook 接線與實跑 → **U4** RUNBOOK／README／bootstrap／活書＋DoD 鏈全綠＋perf 事件 → **U5** BL-00005。
- **Rationale**：spec FR-013 DoD 鏈順序不變；只把「工具落地」與「其自測所需真檔」綁同批。
