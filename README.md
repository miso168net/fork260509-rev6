# fork260509-rev6 — rev6-admin 傘狀整合 workspace

admin 後台系統第六代重跑版：前端 fork 自 soybean-admin（Vue3＋naive-ui）、後端 Rust 從零重寫。
本 repo 是**傘狀整合層**——管文件、決策、規則、spec 與編排；程式碼住兩個 submodule（`base-web/`、`rust-api/`，本機以 git worktree 掛載）。
文件骨架參考 RAD-AI（Oliver1703dk/RAD-AI @ afdd36d）改寫，子節名與檢核表列文字一律中文改寫、不逐字。
前代 rev5（`../fork260509-rev5/`）自其 commit 7eab28a 起為**唯讀對照基準**（ADR-00002；bootstrap 斷言凍結 SHA），引用一律 `rev5:` 前綴。

## 文件系統地圖（哪些檔案在哪裡）

```text
fork260509-rev6/
├── README.md                        本檔：人類入口導覽；下列樹之 tools/、deploy/、.githooks/、.claude/ 與實檔集由 GT-09 雙向對賬；docs/ 列項為地圖、出現時機標於括號
├── CLAUDE.md                        操作規則書：拓樸／工作流／git 手冊／文件規則／決策紀律／硬禁令／rev5 對照
├── .specify/memory/constitution.md  凍結權威：原則、wire 不變式、行為島與軌道凍結位、自查九題、Amendment 走 §V.2（現行 1.4.0＝ADR-00034；前版 1.3.0＝ADR-00026、1.2.0＝ADR-00022／ADR-00023／ADR-00024 三筆同批、1.1.0＝ADR-00009、創世 1.0.0＝ADR-00003）
├── docs/ops/RULES.md                規則層（人寫）：RL-NNNN｜命令句｜scope｜carrier｜source；上限＝ADR-00011（數值續自其翻案之 ADR-00004 表）；名詞段住此
├── docs/ops/NOTES.md                當前意圖；首行 <!-- wave: N --> 為「現在波」唯一真源
├── docs/ops/events.jsonl            事件源（機器讀）：feature_close／misc／review／erratum／perf；人讀 generated/MILESTONES、reference/perf、STATE（帳面統計與治理指標）、DECISIONS-INDEX（feature 欄）
├── docs/ops/BACKLOG.md、BACKLOG-DEFERRED.md   待辦兩卷 BL-NNNNN（開放／滯後；配號只在主檔；完成即刪、git 即史）
├── docs/ops/LESSONS.md、LESSONS/    教訓索引（機器生成、例外註冊、檔頭 next-id）與一坑一檔 LL-NNNNN（`LESSONS/` 首條 LL 落地時出現）
├── docs/ops/RUNBOOK.md              操作手冊：章節編號承 rev5；章節現況以本檔檔頭句為準（唯一人寫的家）
├── docs/ops/reference-src/         人寫／照相真源：`schema-snapshot.json`／`accounts-snapshot.json`（`python3 tools/docsync refresh` 照相）＋`archetype-map.json`＋`schema-evolution.json`（演進帳）＋`schema-definition.md`（欄語意權威、ADR-00012）
├── docs/arc42/decisions/            ADR 一決策一檔 ADR-NNNNN-<slug>.md（accepted 後 body 不可變、翻案走 supersedes）
├── docs/arc42/、docs/c4/、docs/compliance/、docs/process/   活書家族（索引＝docs/arc42/ARCHITECTURE.md；永遠現在式）
├── docs/generated/                  機器生成、嚴禁手改：STATE／MILESTONES／DECISIONS-INDEX／GATES／RAD-AI-MAP／reference/{ports,perf,rev5-blueprint-map,agents,schema,accounts,routes}
├── docs/brainstorms/                史料面：啟動書 000-doc-architecture、波 1 計畫 000-w1-governance-tooling、各刀階段 0 產出
├── docs/reviews/                    史料面：不定期獨立 review 報告 YYYYMMDD-<scope>.md（review 事件 report 欄指向此；首份＝文件創世驗收）
├── specs/<NNN>-<feature-name>/      spec-kit per-feature 文件（首刀時出現、收刀即凍結）
├── tools/                           repo 治理面工具鏈（pre-commit／bootstrap 掛勾；管「版控品質」）
│   ├── bootstrap.sh                 新機重建／體檢：源倉 clone＋worktree＋hooksPath＋betterleaks 釘版＋hooks 指紋＋rev5 凍結斷言＋docsync 三段＋閘數
│   ├── wf-watchdog.py               workflow 編排看門狗（stall／runaway 保險絲、可鎖定目標 run）
│   ├── walkthrough-baseline.py      走查前後全表基準對賬：snapshot／diff（三面現算、唯讀、需 rev6 dev stack）＋restore（走查後清理面機器化＋收尾 diff、基準須為空；`--seed`＝無須基準檔、以凍結 seed 為目標態）／test（離線）；diff 對 runtime-append 四表之序列只比存在性；隨遷自 rev5、非碼面閘（NON_GATE_TOOLS）
│   ├── schema-gate.py               三閘 schema 驗證閘：check（凍結 fixtures ⊕ 演進帳 vs 實庫）／test／doccheck（隨遷自 rev5、碼面閘不入 GATES 名冊）
│   ├── entity-drift-gate.py         entity×schema 快照漂移閘：check／test（隨遷自 rev5；自測入 pre-commit 條件觸發名冊、check 入 pre-commit entity-drift 段＝rust-api pin bump 或快照 staged 時實跑、快照缺席即紅 rc 2＋refresh 提示）
│   ├── rust-fmt-gate.py             rust 格式閘：check＝容器內 cargo fmt --all --check 唯讀比對／test（隨遷自 rev5；pre-commit rust-fmt 段＝rust-api pin bump 或本檔 staged 時實跑、docker 缺或容器未起＝具名跳過 rc 0、容器在而 cargo-fmt 缺＝rc 2）
│   ├── wire-schema.py               wire 契約閘：extract（typings→JSON Schema 快照、需 stack）／check [--staged-gate]（重抽 byte 比對、絕不覆寫；pre-commit wire-schema 段＝base-web 或 rust-api pin bump 時、容器未起＝具名跳過 rc 0）／test（隨遷自 rev5）
│   ├── fork-delta-lint.py           base-web fork-delta 標記閘：修改型缺原行／新增型缺圈界（含新檔檔頭一行＋所稱軌道×檔路徑）／授權判定（§III.1 檔面收窄＋§III.2 三元組）、空 ★表以哨兵句守（隨遷自 rev5；pre-commit fork-delta 段＝base-web pin bump、本檔或憲法 staged 時全掃；test＝離線自測；--constitution 只供自身變異驗證）
│   ├── msg-key-gate.py              msg key 跨端閘：check＝rust-api `error.rs` 之 MSG_KEYS ⇔ base-web 三檔 locale 各自 backend 子樹逐檔雙向全等（無白名單）＋Biz 構造點守衛（`Cow::Borrowed(字面|msg_key::NAME)`、`#[cfg(test)]` 排除）＋前端 msg 字面消費點名冊（base-web src 剝註解後之 wire 字面 ⇔ 工具內名冊逐項雙向全等、安全前綴現算）／test＝離線自測（契約案＋判準補強案＋真 repo 左源綠案＋斷言 3 案；案數以 `test` 輸出為準）；零 docker；pre-commit msg-key-gate 段＝rust-api 或 base-web pin bump、本檔 staged 時實跑
│   ├── comment-overlap.py           rev5↔rev6 註解逐字重疊核：對 rev5 對應檔（同相對路徑；缺席且檔名 `rev6-` 起首者映射同目錄 `rev5-` 同名檔）量共同子字串比（預設 40 字元／5%、超標 rc 1；解析 `//` 行＋`/* */` 塊註解＋`.vue` 之 `<!-- -->`；base-web 路徑三型豁免後量；全路徑碼面豁免〔code span／doc 註與塊註解內之三反引號圍欄〕；比對面為空 rc 2）／test 自測（RL-0076 量尺；非閘工具＝`NON_GATE_TOOLS` 成員、自測入 pre-commit 條件觸發名冊）
│   ├── docsync/                     治理工具 package：generate／check／lint（GT-01～GT-12）／refresh（快照照相、需 dev stack）／rules emit／errata／vendored-check（§I.5 例外① 自證、bootstrap 3c）／test；tests/ 為語料面
│   └── orchestration/               Workflow 編排骨架 _sk_*.js（單一骨架、TDD／review 兩種主流程共用首段；_sk_rules.js＝generate 產物）、assemble.py 組裝器（三道自檢）、harness-test 十八案（六反例）／harness-review 九案（三反例）（斷言＋退出碼）、cdp.mjs、EXAMPLE 成品與 TDD／review 單元定義範本
├── deploy/                          營運面：dev stack 部署資產＋機密管線（管「跑起來的系統」）
│   ├── secrets_common.py            機密落點三級解析共用庫（消費者＝下列 CLI＋docsync GT-07）
│   ├── preflight-secrets.py         機密上機前把關（缺檔／CR·LF／composite drift）
│   ├── decrypt-secrets.py           密文→落點明文（passphrase 自動應答）
│   ├── generate-secrets.py          十三機密缺則補（亂數走 docker openssl）
│   ├── setup-reaper-role.py         reaper role 設密（docker compose exec psql）
│   ├── backup-db.py                 DB 備份／還原（pg_dump 走容器；落點 $HOME 防跨代撞名）
│   ├── sops.sh                      sops 官方容器 wrapper（digest 釘版、exec 薄殼）
│   ├── generate-age-key.sh          age 產鑰（容器化）
│   ├── generate-dev-cert.sh         dev TLS 憑證（容器化 openssl）
│   ├── Dockerfile.age、Dockerfile.rust-api    建置檔
│   ├── secrets.dev.enc.yaml         機密密文（sops age 雙 recipient、tracked；世代錯開、不沿用 rev5 鑰）
│   ├── loki-config.yml、trust-model.dev.toml   觀測層與信任錨設定
│   ├── secrets/                     明文落點說明（README＋.example；實值住 SECRETS_DIR、gitignored）
│   ├── alloy/、grafana-provisioning/、nginx/、prometheus/   compose 掛載的服務／觀測層設定（動它＝動 runtime）
│   └── dev-certs/                   dev TLS 憑證落點（gitignored、.gitkeep）
├── .githooks/                       外層 hooks（core.hooksPath）：pre-commit（betterleaks→check＋lint→條件自測→bootstrap-roster（bootstrap.sh staged 時只跑 test_hook_wiring 單檔）→rust-fmt／wire-schema／fork-delta／msg-key-gate→submodule-sync（pin bump 時兩子庫雙側閘閘面須無未 commit 改動、含未追蹤新檔）→entity-drift（快照缺席即紅）／schema-frozen／orchestration（骨架或範例 staged 時三支範例組裝＋harness）皆條件實跑；接線字面由 docsync tests 機器守；雙錨門檻＝pre-commit 檔頭常數）、pre-push（範圍掃描）
│   ├── pre-commit、pre-push
│   └── lib/                         scan-range.sh：pre-push 範圍推導（三 repo 共用）
├── .githooks-submodule/             兩 worktree 專用 hooks（pre-commit／pre-push；bootstrap 以絕對路徑設 hooksPath）
├── .claude/                         Claude Code 接線
│   ├── settings.json                三支 hook 註冊（SessionStart／PreToolUse(Workflow)／PostToolUse(Workflow)）
│   ├── hooks/                       session-start.sh、pre-workflow-gate.py（zh-TW＋RULES-VERSION 對賬）、post-workflow-reminder.py
│   └── skills/                      spec-kit 1.0.3 產物（第三方面；speckit-* 十五支）
├── .gitleaks.toml                   betterleaks 設定（extend 預設＋rev6-dsn-credential-url；allowlist 逐條雙向實證後才收）
├── docker-compose*.yml              dev stack 三檔：base 層／dev override／example 參照實例（host 埠 3xxxx＝ADR-00001）
├── fork260509-*/                    fork 源倉本機 clone（gitignored、必留、勿直接編輯）
└── base-web/、rust-api/             程式體 worktree（本機 worktree／外層 gitlink 雙身分；分支長名 rev6-admin-base-web／rev6-admin-rust-api）
```

**工具擺放原則**（承 rev5）：`tools/`＝repo 治理面、`deploy/`＝營運面——分界是**服務對象、不是語言**。命名慣例：連字檔名＝CLI（不可 import）、底線檔名＝庫（可 import）。

## 這裡的文件系統怎麼運作（30 秒版）

- **三種材質**：人寫（規則與敘事、user 拍板審 diff）／事件源（`docs/ops/events.jsonl` 半自動 append）／機器生成（名冊＝`GENERATED_FILES`：`docs/generated/**`＋`tools/orchestration/_sk_rules.js`＋例外註冊 `docs/arc42/ARCHITECTURE.md`、`docs/ops/LESSONS.md`；嚴禁手改、任何檔可刪除重算）。每個事實只有一個人寫的家；鏡像不是機器生成、就是不存在。
- **權威鏈**：constitution ＞ ADR accepted ＞ RULES.md ＞ 活書家族（arc42／c4／compliance／process）＞ generated。RULES 與 accepted ADR 衝突＝RULES 有誤、就地改 RULES。
- **時態**：活書家族永遠現在式；未來式住 ops/；過去式住 git＋events。完成即刪、git 即史。
- **守門**：pre-commit 一次跑完（秒級）——betterleaks 樣式層 → `docsync check`（GT-01 零漂移）＋`docsync lint`（GT-01～GT-12；GT-01 與前項同源）→ staged 工具自測 → bootstrap-roster（`tools/bootstrap.sh` staged 時只跑 `test_hook_wiring` 單檔、秒級）→ rust-fmt／wire-schema（雙側：base-web 或 rust-api pin bump）／fork-delta（base-web pin bump、工具本體或憲法 staged 時條件實跑；名冊＝RUNBOOK §12 碼面閘表）→ msg-key-gate（rust-api 或 base-web pin bump、工具本體 staged 時條件實跑；零 docker、無環境跳過分支）→ submodule-sync（rust-api 或 base-web pin bump 時兩子庫工作樹之雙側閘閘面須無未 commit 改動（含未追蹤新檔）＝跨子庫同步律粗判；零 docker）→ entity-drift（rust-api pin bump／schema 快照 staged 時條件實跑；快照缺席即紅）→ schema-frozen（凍結 fixtures／data-model／schema-definition staged 時條件實跑）→ orchestration（`tools/orchestration/` 之 `*.js|*.mjs|*.py` staged 時三支入庫範例組裝＋harness）；接線字面由 `tools/docsync/tests/test_hook_wiring.py` 機器守（hook 本體 staged 時自跑）。閘名冊＝`docs/generated/GATES.md`（九欄；Day-1 豁免逐筆帶解除謂詞、到期即紅）。
- **規則進 prompt**：`python3 tools/docsync rules emit --scope <implementer|review|fix|主線|人>` 產出規則塊＋`RULES-VERSION`；Workflow script 一律必帶、PreToolUse hook 對賬。

## 第一次來，照這個順序讀

1. `CLAUDE.md` §1（拓樸）→ §6（硬禁令）。
2. `.specify/memory/constitution.md`（凍結權威；§IV 九題是 plan 的自查表）。
3. `docs/ops/RULES.md`（規則層＋名詞段）與 `docs/generated/GATES.md`（哪些閘在守什麼）。
4. `docs/generated/STATE.md`（現況帳：pins／現在波／帳面統計／治理指標／預算對賬）→ `docs/ops/NOTES.md`（下一步）。
5. 啟動書 `docs/brainstorms/000-doc-architecture.md`（設計依據；史料面）。

★動工前掃 `docs/ops/BACKLOG.md` 的觸發欄——指名「本刀會踩到」的條目要當輸入。

## 操作快速入口

- 新機重建／體檢：`bash tools/bootstrap.sh`（幂等；掃描防線 die 級、remote 未設只 ⚠）。
- 治理工具：`python3 tools/docsync generate`｜`check`｜`lint`｜`refresh`（需 dev stack postgres）｜`rules emit --scope implementer [--format js]`｜`errata <詞>`｜`vendored-check`（憲法 §I.5 例外① 自證＝bootstrap 3c 步）｜`test`。
- 機密：`deploy/secrets/README.md`（產鑰→生成→加密→解密；離線復原鑰＝rev5:RUNBOOK §15.5 義務）。
- dev stack：`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait`（埠表＝`docs/generated/reference/ports.md`）。

## 想知道 X，看 Y

| 想知道 | 看 |
|---|---|
| 為什麼這樣做 | `docs/arc42/decisions/`（索引＝`docs/generated/DECISIONS-INDEX.md`） |
| 現在到哪、下一步 | `docs/generated/STATE.md`、`docs/ops/NOTES.md` |
| 我要開新刀（從哪起手） | `docs/ops/NOTES.md` 下一步 → `CLAUDE.md` §2 階段 0 → `docs/brainstorms/<NNN>-<feature-name>.md` |
| feature 分支與 specs 目錄怎麼來 | `CLAUDE.md` §2 SDD 段（分支＝before_specify hook 建、目錄＝`/speckit-specify` 自建並寫 `.specify/feature.json`；序號設定＝`.specify/extensions/git/git-config.yml`、`.specify/init-options.json`） |
| 哪些規則、誰守 | `docs/ops/RULES.md`、`docs/generated/GATES.md` |
| 哪些碼面閘在守子庫碼與跨端契約 | `docs/ops/RUNBOOK.md` §12 碼面閘表（名冊唯一權威、ADR-00032；治理閘另見 `docs/generated/GATES.md`） |
| 踩過什麼坑、怎麼避 | `docs/ops/LESSONS.md`（索引、機器生成；全文＝`docs/ops/LESSONS/` 一坑一檔） |
| 還欠什麼、下一批做什麼 | `docs/ops/BACKLOG.md`、`docs/ops/BACKLOG-DEFERRED.md`（條目帶觸發欄） |
| git／submodule 怎麼操作（兩段式 commit、pin 判方向） | `CLAUDE.md` §3 |
| 怎麼操作（起停、機密、工具） | `docs/ops/RUNBOOK.md` |
| 系統長怎樣（活書索引） | `docs/arc42/ARCHITECTURE.md`（機器生成；節檔住 `docs/arc42/`） |
| RAD-AI 導入到哪、填實幾成 | `docs/generated/RAD-AI-MAP.md` |
| 埠、效能資料點 | `docs/generated/reference/ports.md`、`docs/generated/reference/perf.md` |
| rev5 活書哪節去了哪 | `docs/generated/reference/rev5-blueprint-map.md`（真源＝arc42 節檔 frontmatter `rev5_blueprint`；ADR-00006） |
| 編排 agent 用哪個模型 | `docs/generated/reference/agents.md`（真源＝`tools/orchestration/` 的 `*_OPTS` 常數） |
| 怎麼組一支 Workflow script（TDD／review 兩形）、怎麼自測 | `tools/orchestration/README.md`（組裝器 `assemble.py`＋harness 兩支；發射與看門狗＝`CLAUDE.md` §2） |
| 全量正典 schema 長怎樣（表×archetype、欄／索引／約束） | `docs/generated/reference/schema.md`（真源＝`docs/ops/reference-src/` 快照＋archetype-map；`python3 tools/docsync refresh` 照相） |
| dev 三帳與角色綁定 | `docs/generated/reference/accounts.md`（真源＝`docs/ops/reference-src/accounts-snapshot.json`） |
| 後端路由真表（path×method×protection×case_key×信封例外） | `docs/generated/reference/routes.md`（真源＝`rust-api/server/src/router.rs` 的 ROUTES const；generate 重算） |
| 收刀／review 史 | `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`） |
| rev5 藍本 | `../fork260509-rev5/`（唯讀；憲法 §I.5、CLAUDE.md §7） |
