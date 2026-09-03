# fork260509-rev6 — rev6-admin 傘狀整合 workspace

admin 後台系統第六代重跑版：前端 fork 自 soybean-admin（Vue3＋naive-ui）、後端 Rust 從零重寫。
本 repo 是**傘狀整合層**——管文件、決策、規則、spec 與編排；程式碼住兩個 submodule（`base-web/`、`rust-api/`，本機以 git worktree 掛載）。
文件骨架參考 RAD-AI（Oliver1703dk/RAD-AI @ afdd36d）改寫，子節名與檢核表列文字一律中文改寫、不逐字。
前代 rev5（`../fork260509-rev5/`）自其 commit 7eab28a 起為**唯讀對照基準**（ADR-00002；bootstrap 斷言凍結 SHA），引用一律 `rev5:` 前綴。

## 文件系統地圖（哪些檔案在哪裡）

```text
fork260509-rev6/
├── README.md                        本檔：人類入口導覽；下列樹之 tools/、deploy/、.githooks/、.claude/ 與實檔集由 GT-09 雙向對賬
├── CLAUDE.md                        操作規則書：拓樸／工作流／git 手冊／文件規則／決策紀律／硬禁令／rev5 對照
├── .specify/memory/constitution.md  凍結權威：原則、wire 不變式、行為島與軌道凍結位、自查九題、Amendment（1.0.0＝ADR-00003）
├── docs/ops/RULES.md                規則層（人寫）：RL-NNNN｜命令句｜scope｜carrier｜source；上限＝ADR-00004；名詞段住此
├── docs/ops/NOTES.md                當前意圖；首行 <!-- wave: N --> 為「現在波」唯一真源
├── docs/ops/events.jsonl            事件源（機器讀）：feature_close／misc／review／erratum／perf；人讀 generated/MILESTONES 與 reference/perf
├── docs/ops/BACKLOG.md、BACKLOG-DEFERRED.md   待辦兩卷 BL-NNNNN（開放／滯後；配號只在主檔；完成即刪、git 即史）
├── docs/ops/LESSONS.md、LESSONS/    教訓索引（機器生成、例外註冊、檔頭 next-id）與一坑一檔 LL-NNNNN
├── docs/ops/RUNBOOK.md              操作手冊：章節編號承 rev5；創世期最小章 §1／§7 抬頭／§12／§14、§15 為指針、其餘隨刀補實
├── docs/arc42/decisions/            ADR 一決策一檔 ADR-NNNNN-<slug>.md（accepted 後 body 不可變、翻案走 supersedes）
├── docs/arc42/、docs/c4/、docs/compliance/、docs/process/   活書家族（波 2 骨架、永遠現在式）
├── docs/generated/                  機器生成、嚴禁手改：STATE／MILESTONES／DECISIONS-INDEX／GATES／RAD-AI-MAP／reference/{ports,perf}
├── docs/brainstorms/                史料面：啟動書 000-doc-architecture、波 1 計畫 000-w1-governance-tooling、各刀階段 0 產出
├── specs/<NNN>-<feature-name>/      spec-kit per-feature 文件（首刀時出現、收刀即凍結）
├── tools/                           repo 治理面工具鏈（pre-commit／bootstrap 掛勾；管「版控品質」）
│   ├── bootstrap.sh                 新機重建／體檢：源倉 clone＋worktree＋hooksPath＋betterleaks 釘版＋hooks 指紋＋rev5 凍結斷言＋docsync 三段＋閘數
│   ├── wf-watchdog.py               workflow 編排看門狗（stall／runaway 保險絲、可鎖定目標 run）
│   ├── docsync/                     治理工具 package：generate／check／lint（GT-01～GT-12）／rules emit／errata／test；tests/ 為語料面
│   └── orchestration/               Workflow 編排骨架 _sk_*.js（_sk_rules.js＝generate 產物）、EXAMPLE 組裝成品、harness-test 十案、cdp.mjs
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
├── .githooks/                       外層 hooks（core.hooksPath）：pre-commit（betterleaks→check＋lint→條件自測；雙錨 45／90 秒）、pre-push（範圍掃描）
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

- **三種材質**：人寫（規則與敘事、user 拍板審 diff）／事件源（`docs/ops/events.jsonl` 半自動 append）／機器生成（`docs/generated/` 與 `tools/orchestration/_sk_rules.js`，嚴禁手改、任何檔可刪除重算）。每個事實只有一個人寫的家；鏡像不是機器生成、就是不存在。
- **權威鏈**：constitution ＞ ADR accepted ＞ RULES.md ＞ 活書家族（arc42／c4／compliance／process）＞ generated。RULES 與 accepted ADR 衝突＝RULES 有誤、就地改 RULES。
- **時態**：活書家族永遠現在式；未來式住 ops/；過去式住 git＋events。完成即刪、git 即史。
- **守門**：pre-commit 一次跑完（秒級）——betterleaks 樣式層 → `docsync check`（GT-01 零漂移）＋`docsync lint`（GT-02～GT-12）→ staged 工具自測。閘名冊＝`docs/generated/GATES.md`（九欄；Day-1 豁免逐筆帶解除謂詞、到期即紅）。
- **規則進 prompt**：`python3 tools/docsync rules emit --scope <implementer|review|fix|主線|人>` 產出規則塊＋`RULES-VERSION`；Workflow script 一律必帶、PreToolUse hook 對賬。

## 第一次來，照這個順序讀

1. `CLAUDE.md` §1（拓樸）→ §6（硬禁令）。
2. `.specify/memory/constitution.md`（凍結權威；§IV 九題是 plan 的自查表）。
3. `docs/ops/RULES.md`（規則層＋名詞段）與 `docs/generated/GATES.md`（哪些閘在守什麼）。
4. `docs/generated/STATE.md`（現況帳：pins／現在波／帳面統計／三指標／預算對賬）→ `docs/ops/NOTES.md`（下一步）。
5. 啟動書 `docs/brainstorms/000-doc-architecture.md`（設計依據；史料面）。

## 操作快速入口

- 新機重建／體檢：`bash tools/bootstrap.sh`（幂等；掃描防線 die 級、remote 未設只 ⚠）。
- 治理工具：`python3 tools/docsync generate`｜`check`｜`lint`｜`rules emit --scope implementer [--format js]`｜`errata <詞>`｜`test`。
- 機密：`deploy/secrets/README.md`（產鑰→生成→加密→解密；離線復原鑰＝rev5:RUNBOOK §15.5 義務）。
- dev stack：`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait`（埠表＝`docs/generated/reference/ports.md`）。

## 想知道 X，看 Y

| 想知道 | 看 |
|---|---|
| 為什麼這樣做 | `docs/arc42/decisions/`（索引＝`docs/generated/DECISIONS-INDEX.md`） |
| 現在到哪、下一步 | `docs/generated/STATE.md`、`docs/ops/NOTES.md` |
| 哪些規則、誰守 | `docs/ops/RULES.md`、`docs/generated/GATES.md` |
| 怎麼操作（起停、機密、工具） | `docs/ops/RUNBOOK.md` |
| 系統長怎樣（活書索引） | `docs/arc42/ARCHITECTURE.md`（機器生成；節檔住 `docs/arc42/`） |
| RAD-AI 導入到哪、填實幾成 | `docs/generated/RAD-AI-MAP.md` |
| 埠、效能資料點 | `docs/generated/reference/ports.md`、`docs/generated/reference/perf.md` |
| 收刀／review 史 | `docs/generated/MILESTONES.md`（真源＝`docs/ops/events.jsonl`） |
| rev5 藍本 | `../fork260509-rev5/`（唯讀；憲法 §I.5、CLAUDE.md §7） |
