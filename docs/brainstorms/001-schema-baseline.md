# 001 schema 基線刀・階段 0 brainstorm 定稿（rev6 首刀）

> 性質：階段 0 brainstorm 產出（superpowers:brainstorming；一題一問拍板）。執筆＝主線 Claude Fable 5.1；拍板＝user（2026-09-03）。
> 輸入：啟動書 `docs/brainstorms/000-doc-architecture.md`（D13 刀序、§3.2 樹預留、§4.5 碼面閘）、憲法 §I.5／§I.6／§IV／§V、`docs/generated/reference/rev5-blueprint-map.md` 隨刀列、rev5 `rev5:001-schema-baseline` 全套（brainstorm／spec／research／contracts／fixtures；唯讀、凍結 SHA 7eab28a／rust-api 92919b9）。
> 產出：本檔（＝手動 `/speckit-specify` 的 input）；ADR-00009／ADR-00010 草案要點（§2／§7）；刀內落地物清單（§1）。停點：本檔審定後停，specify 由 user 手動起手。
> 對齊（2026-09-04）：ADR-00008（migration 短號四碼）accepted 後就地修訂——擬立 ADR 改編 ADR-00009／00010、rev6 migration 檔名四碼 `m0001_`／`m0002_`、delta 自 `m0003`；承襲口徑＝內容逐位元、檔名依 ADR-00008。

## 0. 拍板紀錄（本 brainstorm 三題＋user 指示，一題一問、首選項為建議）

| 題 | 裁定 | 要點 |
|---|---|---|
| Q1 首刀範圍與刀序起點 | **A・承 rev5 序：首刀＝schema 基線刀，server 隨 002** | 刀序 001 schema-baseline → 002 system-settings（server 進場）→ 003 auth-session → 004 ip-trust-anchor → 005 role-menu-crud → 006 authz-governance → 007 user-password-admin → 008 audit-settings-pages（D13：本檔定序；各刀範圍由各自 brainstorm 定、可翻）。本刀 dev stack 的 rust-api 服務仍起不來（server 缺席，同 rev5 001） |
| user 指示 | **m001／m002 程式碼完整照抄、註解重寫** | 這是憲法 §I.5「拷貝禁止」的例外→走 §V.2 Amendment（MINOR 1.0.0→1.1.0）＋ADR-00009；四條件見 §2；rev6 檔名改四碼 `m0001_`／`m0002_`（ADR-00008） |
| Q2 例外射程 | **A・三件一起入例外：`rev5:m001`、`rev5:m002`、entity 15 檔** | 資料形狀契約三件（結構 migration、seed migration、entity 欄宣告）；射程鎖 rev5 rust-api 92919b9 的 17 檔；不及 server／handler 業務碼；m0003 起 delta 仍全新寫 |
| Q3 閘工具承載 | **A・搬 rev5 兩支改座標（隨遷工具形）＋refresh 與生成器入 docsync** | `tools/schema-gate.py`（2,522 行）、`tools/entity-drift-gate.py`（780 行）自 rev5 拷入改座標、註解重寫；`refresh` 子命令與 `gen_reference_schema`／`gen_reference_accounts` 入 docsync（GENERATED_FILES 12→14） |

**照抄的必然結果**（不另問）：欄序 169 欄、rename map 4 組、seed 定稿（266 列＋9 空表、簡→繁 22 筆、三帳共用 PHC 常數、`created_at` 定稿時戳）全部承 rev5 定稿制成果，**不重開欄序親排與 seed 過目工作坊**；rev5 已驗證結論照施工（啟動書 §2）。

**ADR 待立**（刀分支內落、不在 default 先落）：ADR-00009（憲法 §I.5 例外 Amendment，§2）、ADR-00010（schema 基線＝rev5 終態逐位元承襲＋受管演進帳閘契約，§7）；ADR-00008（migration 短號四碼）已 accepted、本刀直接適用。

## 1. 目標與範圍

**目標**：rev6 資料庫基線＝rev5 終態 15 表——`m0001_baseline_schema`（結構、承 `rev5:m001`）＋`m0002_baseline_seeds`（seed 定稿、承 `rev5:m002`）內容逐位元承襲、檔名四碼（ADR-00008）；rust-api workspace 骨架三 member 就位；受管演進帳三閘＋entity 漂移閘＋refresh 照相＋兩張真表就位；Day-1 紀律入 RUNBOOK。rev6 第一支 delta 自 m0003 起編。

**入刀**：
- `rust-api/`：`Cargo.toml` workspace（members＝migration／entity／sea-orm-adapter；`edition = "2024"`；`workspace.dependencies` 首刀子集）、`rust-toolchain.toml`（`1.96.1`＝`deploy/Dockerfile.rust-api` 同值）、`rustfmt.toml`（三值承 rev5、rust-fmt-gate 隨後刀）、`Cargo.lock`；`migration/`（`lib.rs`／`main.rs` 自寫＝sea-orm-cli 樣板；`rev5:m001`／`rev5:m002` 照抄為 `m0001_`／`m0002_`＋註解重寫）；`entity/`（15 檔照抄＋註解重寫；`lib.rs` 自寫）；`sea-orm-adapter/`（既有例外、整檔拷貝）。
- 凍結面 `specs/001-schema-baseline/fixtures/`（columns／constraints／indexes JSON＋seed.sql＋provenance；自 rev6 自己的 pristine 重放萃取、與 rev5 fixtures 逐位元比對＝雙源互證；`seaql_migrations` COPY 段承 rev5 閘契約本就剝除、四碼改名不破全等）。
- 演進面 `docs/ops/reference-src/`（啟動書樹預留）：`schema-snapshot.json`、`accounts-snapshot.json`（refresh 自實庫撈）、`archetype-map.json`（15 表變體歸屬、人寫轉錄）、`schema-evolution.json`（登記檔、初版零筆）。
- 工具：`tools/schema-gate.py`（check＝gate1 結構／gate2 欄序＋seed／audit archetype；test；doccheck）、`tools/entity-drift-gate.py`（check／test）；docsync `refresh` 子命令＋`gen_reference_schema`／`gen_reference_accounts`→`docs/generated/reference/schema.md`／`accounts.md`。
- 接線：`.githooks/pre-commit` 加 entity-drift check（快照缺席＝Day-1 跳過、就位即實跑）＋兩工具 staged 時條件自測；RUNBOOK §10 實文＋§12 兩列；README 樹加兩支工具行（GT-09 對賬面含 tools/）。
- 治理：ADR-00009＋憲法 1.1.0；ADR-00010；BL-00001 消化（開分支時、Task 0）；活書 `docs/arc42/05` §5.2 rust-api 句、`docs/arc42/08` §8.1 指針句、C4-L2 若拓樸不變則零改。

**不入刀**：server crate／router／`Res` 信封／一切業務邏輯（002 起）；wire-schema（server 在場才有意義）；xdb（rev5 dev 尾巴）；reaper DB role／GRANT（deploy 面、非 migration；承 rev5 R4）；rust-fmt-gate、fork-delta-lint（各隨其刀）；行為島（本刀無狀態機、§I.7 零進場）。

**承襲／差異表**：

| 項 | rev5 已驗證結論 | rev6 處置 |
|---|---|---|
| 15 表結構、欄序、rename map、索引 38、約束 101 | 定稿制、data-model 凍結 | 內容逐位元承襲（`rev5:m001` 照抄為 m0001、檔名依 ADR-00008） |
| seed 266 列＋9 空表、明示 id＋setval、PHC 常數、定稿時戳 | 完全決定性重放 | 內容逐位元承襲（`rev5:m002` 照抄為 m0002）；時戳字面照舊（改值即破全等） |
| entity 15 檔（含變體 A／B／C／D 語意） | 手寫、逐欄依 data-model | 照抄＋註解重寫；終態版含後刀補的 impl，防回歸審查逐檔記 ADR |
| 三閘契約：凍結＋登記合成→與實庫全等、非容差 | 受管演進帳（rev5 001 brainstorm §3） | 承襲；契約寫進 ADR-00010 |
| pristine 驗證：一次性 postgres 容器＋獨立 network、零 host 埠 | rev5 R2 | 承襲（rev6 網名／容器名帶 rev6 前綴） |
| 日常 migration：compose `migrate` 服務 `cargo run --bin migration up` | rev5 R2 | 承襲（rev6 compose 已預接線） |
| 版本組合：sea-orm／sea-orm-migration 1.1.20、tokio 1.52.3、async-trait 0.1.89、casbin 2.20.0、rust 1.96.1 | rev5 Cargo.lock 現值 | 首源＝rev5 Cargo.lock、次源＝crates.io latest stable；同值採、異值問 user（全域 §6）；research R1 記表 |
| refresh／生成器住 rev5 `tools/docs-sync.py` | 單檔工具 | 入 rev6 docsync（`references.py`＋新 `snapshot.py`）；預算估 2,043→約 2,300／4,000 |
| 工具註解含 rev4／rev5 編號 | rev5 語境 | 全部重寫、前代出處帶 `rev5:`／`rev4:`（GT-05 掃 tools/ 與子庫 pin 樹） |
| ADR 承載 | rev5 ADR 0001 決定 3、0003 | rev6 自立 ADR-00009／00010，背景引 `rev5:ADR 0001`、`rev5:ADR 0003` |

## 2. 拷貝例外與憲法 Amendment（ADR-00009 草案要點）

- **改哪一節**：憲法 §I.5「例外」清單加一句：「資料形狀契約三件整檔拷貝——基線結構 migration（`m0001_baseline_schema.rs`、承 `rev5:m001`）、基線 seed migration（`m0002_baseline_seeds.rs`、承 `rev5:m002`）、基線 entity 15 檔——射程鎖 rev5 rust-api 凍結 SHA `92919b9` 之版本；註解一律重寫、前代出處帶 `rev5:`；檔名依 ADR-00008 四碼；防回歸條款照常；m0003 起 delta migration 與一切業務碼不在此例外。」版號 1.0.0→**1.1.0**（§V.3：軌道／例外邊界擴展＝MINOR）；Amendment log 加一行。
- **§V.2 四步**：提案＝本檔＋ADR draft；討論＝user 親決（Q2 已裁）；凍結＝ADR accepted＋憲法段更新＋bump；commit＝獨立 `docs(constitution): amend §I.5 例外——資料形狀契約三件整檔拷貝`（憲法＋ADR 同 commit＋generate）。時點＝`/speckit-specify` 開出刀分支後的**第一顆 commit**（早於 `/speckit-plan` 的 §IV 第 5 題）。
- **四條件（ADR 決定節）**：①程式碼逐位元照抄：兩邊去註解後 diff 全等＝機器自證（命令與結果記 ADR 證據段與 commit 訊息）②註解一律重寫為 rev6 語境；rev5 m001 有兩處裸 `rev4:m009`／`rev4` 引用、entity 六檔各一處前代引用——照抄必觸 GT-05 子庫 pin 樹掃描 ③防回歸審查：逐檔核無 rev6 已推翻行為（現況＝憲法 §I.6 四變體與 rev5 同、零推翻；entity 終態版若含後刀 impl 逐項列出、屬形狀外者去除）④seed 固定值（三帳共用 argon2 PHC 常數、定稿時戳）＝定稿字面、非機密（承 `rev5:ADR 0003` 立場）；betterleaks 若命中，依 `.gitleaks.toml` 紀律逐條 allowlist＋雙向突變實證、絕不 `--no-verify`。
- **理由**：資料形狀是契約不是碼（承 `rev5:ADR 0001` 決定 3）；定稿制成果已 user 親排簽核，重打字零資訊增益、只增抄錯風險；UI 對照驗收（CDP 對 rev5 stack 全等）要求資料形狀同一。
- **後果**：`/speckit-plan` §IV 第 5 題答「是、屬 §I.5 例外清單（資料形狀契約三件）」；日後任何第 18 檔要拷＝新 Amendment；例外不影響 §I.5 其餘四款。

## 3. 驗證鏈（承 rev5 001 brainstorm §2、rev6 座標）

1. **pristine 重放**：一次性 `postgres:18.4-alpine` 容器（獨立 network、零 host 埠、用畢即拆）；容器內以 dev 映像跑 `cargo run --bin migration up`（rust 容器內全程 serial）。
2. **fixtures 產製**：自 pristine 撈 information_schema（columns／constraints／indexes）＋`pg_dump --data-only`（COPY 段整列排序 normalize、剝 `\restrict` 隨機 token 行）→ `specs/001-schema-baseline/fixtures/`；與 rev5 同名 fixtures **逐位元比對全等**＝雙源互證（rev5 唯讀）。
3. **三閘**（`tools/schema-gate.py check`）：gate1 結構＝凍結 fixtures＋`schema-evolution.json` 合成期望值 vs 實庫全等；gate2 欄序＋seed vs 定稿；audit archetype＝15 表歸屬逐表驗；negative test 先自證（注入假漂移必紅）。
4. **entity-drift**（`tools/entity-drift-gate.py check`）：`schema-snapshot.json` columns vs `entity/src/*.rs` 雙向表／欄／型／可空比對；pre-commit 常跑、秒級、零 docker。
5. **DoD 鏈**：`python3 tools/docsync refresh`（需 dev stack postgres）→ 兩快照就位 → `generate` → `reference/schema.md`／`accounts.md` → pre-commit 全綠（entity-drift 由跳過轉實跑）→ `schema-gate check` 三閘綠 → GT-01 零漂移、GT-09 README 樹對賬綠、GT-12 預算內。
6. **Day-1 紀律**（RUNBOOK §10）：每支帶 migration 的刀必跑 refresh＋登記 `schema-evolution.json`；未登記漂移一律紅。

## 4. 工具承載細節（Q3）

- 兩支工具自 rev5 拷入：改座標（rev6 根、`specs/001-schema-baseline/`、compose 檔名、`docs/ops/reference-src/`、DB `soybean`／`soybean_admin_rust`、容器名前綴）、去 rev5 專屬子命令與 rev4 對賬殘留、註解全數重寫（GT-05）、自帶 unittest 逐案過；不入 docsync 預算、不入 GT 名冊（碼面閘＝啟動書 §3.2 樹「隨子庫刀進場」列）。
- docsync 新增：`refresh`（psql 唯讀撈取→兩快照 JSON、排序決定性）、`gen_reference_schema`（表×變體、欄／型／可空／預設）、`gen_reference_accounts`（dev 帳號×角色×綁定、零機密欄）；GENERATED_FILES 12→14；`compute_generated` 加兩鍵；一正一反自證；`refresh` 不入 pre-commit（需 stack）。
- pre-commit：`pc_run "entity-drift" python3 tools/entity-drift-gate.py check`（快照缺席→跳過訊息、就位→實跑）；staged 含 `tools/schema-gate.py`／`tools/entity-drift-gate.py` 時各跑其 `test`；雙錨 45／90 秒實測。
- 閘數恆 12：三閘與 entity-drift 屬碼面閘、不入 GATES.md 名冊；GATES.md 不動。

## 5. 骨架與依賴（research R1／R8 輸入）

- workspace：`members = ["migration", "entity", "sea-orm-adapter"]`、`resolver = "2"`、`edition = "2024"`；server 隨 002 加入。
- 依賴首刀子集（首源 rev5 Cargo.lock）：`sea-orm 1.1.20`（features macros／with-chrono／with-json／with-ipnetwork）、`sea-orm-migration 1.1.20`（sqlx-postgres／runtime-tokio-rustls／cli）、`tokio 1.52.3`、`async-trait 0.1.89`、`casbin 2.20.0`（adapter 用）；次源 crates.io 對照、異值提問；`Cargo.lock` 入版控。
- 建置：`docker compose ... build migrate`（rust:1.96.1-slim＋watchexec 2.5.1 首次拉取較久）；`cargo` 一律容器內 serial；target／registry 走 named volume（compose 已設）。
- 域外者不進紀律（承 rev5 `rev5:ADR 0032` 形）：本刀不引任何 auth／web 依賴。

## 6. 流程與 user 關卡

1. 本檔審定（grill）→ **手動** `/speckit-specify`（input＝本檔；分支 `001-schema-baseline` 自 rev6-admin-root 開出、GT-05 以 `specs/` 名冊豁免裸刀名）。
2. 刀分支首顆 commit＝ADR-00009 accepted＋憲法 1.1.0（§V.2 步 4）。
3. SDD：clarify【rev6 差異三問：DB 名同 rev5、dev 帳號 Super／Admin／User 同 seed、定稿時戳字面照舊——預期皆「是」】→ plan【§IV 九題；第 5 題答例外、第 8 題答 §I.6 四變體 15 表歸屬】→ tasks → analyze；每步 auto-commit。
4. Task 0（開分支後、首個 Workflow 前）＝BL-00001：`_sk_head*.js` 三變體 `*_OPTS` 收斂為單一常數家與單一骨架（governance、觸發已到）。
5. TDD：Workflow 編排（六件套＋watchdog 原子成對；rust 容器內 serial）；單元粗分＝U1 骨架＋拷貝＋註解＋build → U2 pristine 重放＋fixtures＋refresh＋快照 → U3 兩工具＋hook → U4 生成器＋RUNBOOK＋README＋DoD 鏈；實際分單元依 tasks。
6. 收刀：final holistic review → finishing（merge／push 需 user 當回合同意）→ 簿記三步（首筆 `feature_close` 事件、window＝1、adrs＝[ADR-00009, ADR-00010]；GT-03 首次實跑：`specs/001-schema-baseline/spec.md` 與 ADR 存在）→ perf 第四步。
7. 非一次性遷移（pristine 建庫、無既有資料搬移），三欄表免附；風險列於 §8。

## 7. ADR-00010 草案要點（schema 基線與閘契約）

- 決定：①rev6 基線＝rev5 終態 15 表內容逐位元承襲（`rev5:m001`／`rev5:m002`→`m0001`／`m0002`、檔名四碼＝ADR-00008），第一支 delta 自 m0003 起編；②凍結面＝`specs/001-schema-baseline/fixtures/`（永不改寫；翻案＝新 ADR supersedes）；演進面＝`docs/ops/reference-src/schema-evolution.json`（跨刀登記、帶來源刀編號）；③閘語意＝凍結＋登記合成後與實庫**全等**、非容差；未登記漂移一律紅；④entity 漂移閘常跑 pre-commit、schema 三閘手動與 review 輪；⑤archetype 歸屬 15 表（A 業務六欄／B append-only／C join・狀態機／D 治理）住 `archetype-map.json`、真表由 generate 產。
- provenance：本檔 Q1～Q3、`rev5:001-schema-baseline` brainstorm §3 與 contracts/gates.md、憲法 §I.6。翻案觸發器：基線表集或變體歸屬需改（新刀 supersedes）；閘由全等改容差（不允許、須 ADR）。

## 8. 風險（非三欄表）

- 註解重寫漏裸前代編號→GT-05 紅：guard＝拷入後先 `grep -n 'rev4\|rev5\|K1-\|ADR 0\|B-[0-9]\{3\}\|L-[0-9]\{3\}'` 逐處帶前綴或改寫，再 commit。
- betterleaks 命中 seed 固定值：guard＝逐條 allowlist＋雙向實證（§2 條件④）；rev6 首版零 allowlist、此為預告的兩條之一。
- entity 終態版含後刀 impl：guard＝防回歸審查逐檔記 ADR-00010 證據段；形狀外行為去除並記錄。
- docsync 預算：refresh＋兩生成器估約 250 行→約 2,300／4,000；超估即 GT-12 WARN（波 6 起 ERROR），對策＝`snapshot.py` 精簡、不搬 rev5 doccheck 進 docsync。
- 首次 docker build 時長與 /mnt/d bind mount：target／registry 走 named volume；跑過 compose 後同 shell 先重新 `cd`。
- pre-commit 雙錨：entity-drift 秒級、工具自測條件觸發；實測記 perf 事件。

## 9. 隨做隨記

- 新拍板→ADR（00009／00010）；活書：`docs/arc42/05` §5.2 rust-api 句與 §5.1 樹列、`docs/arc42/08` §8.1 指針句（schema 真表家＝`docs/generated/reference/schema.md`）、frontmatter `rev5_blueprint` 05 列由「隨刀」改「承襲」；C4-L2 零改（拓樸不變）。
- 踩坑→LESSONS 一坑一檔（首條 LL 落地＝同 commit 解除 GT-08.lessons-absent）；衍生→BACKLOG；per-unit pin 即時 bump（GT-02）。
