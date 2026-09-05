# RUNBOOK — dev stack 操作手冊

本檔＝「怎麼操作」唯一的家。分工（防鏡像）：系統長怎樣→活書 `docs/arc42/`（索引 `docs/arc42/ARCHITECTURE.md`）；十三機密明細表→`deploy/secrets/README.md`；埠全表→`docs/generated/reference/ports.md`；閘名冊→`docs/generated/GATES.md`；坑索引→`docs/ops/LESSONS.md`（全文＝`docs/ops/LESSONS/` 一坑一檔）。
本檔命令一律完整可複製、於 repo 根執行。章節編號承 rev5（`deploy/secrets/README.md` 以 §7／§15 指向本檔；改號＝勘誤級）。
創世期章節現況：§1／§7 抬頭／§10／§12／§14 為已補實文章、§15 為指針章；§9 僅補 DB 直連一句、其餘維運端點與其餘各章隨對應刀補實文，章內不放未經實跑的命令。

## 1. 快速啟動（新機五步）

1. `bash tools/bootstrap.sh` —— 源倉 clone＋worktree＋hooksPath＋betterleaks 釘版＋hooks 指紋＋rev5 凍結斷言＋docsync 三段＋閘數＋secrets 體檢（幂等、可重跑；remote 未設只 ⚠）
2. `python3 deploy/generate-secrets.py` —— 十三機密缺則補（`alert_webhook_url` 為佔位值、見 §4）
3. `python3 deploy/preflight-secrets.py` —— up 前預檢（缺檔／CR·LF／composite drift 一律非零退出）
4. `bash deploy/generate-dev-cert.sh` —— dev TLS 憑證（front-nginx 恆 bind-mount 兩支 pem，缺檔＝Docker 代建空目錄佔位→nginx 起不來）
5. `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait` —— 起預設業務件（migrate 是啟動閘：migration 失敗→rust-api 不啟）

已有 age 私鑰的新機：步驟 2 前先 `python3 deploy/decrypt-secrets.py`（自密文還原十支；passphrase 只輸入一次）。

## 2. 日常起停

`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait`／`stop`／`ps`；host 埠世代 3xxxx（ADR-00001；真表＝`docs/generated/reference/ports.md`）。rev5 對照 stack 常駐 2xxxx、兩 stack 併行是預期形（CLAUDE.md §7）。其餘隨對應刀補實文。

## 3. 觀測層 profiles（obs／metrics／jobs）

compose profile 三組：`obs`（loki、alloy、socket-proxy、grafana）、`metrics`（prometheus、postgres_exporter、redis_exporter、pushgateway、grafana）、`jobs`（reaper）；起法 `--profile <名>` 追加於 §2 命令。隨觀測刀補實文。

## 4. ★人工必填清單（腳本不代辦）

- `alert_webhook_url`：腳本只寫佔位 URL（`.invalid` 保留域）；真值由 user 直接編輯落點檔、填完依 §15.4 回寫密文（無任何閘攔佔位值、唯一徵狀＝告警投遞靜默失敗）。
- `smtp_password`：dev 走 mailpit 免認證、亂數即可；prod 真值另填。

## 5. named volume（卷名帶 project 前綴 `rev6-admin_`）

隨對應刀補實文。

## 6. 備份與還原

`python3 deploy/backup-db.py`（承 rev5:RUNBOOK §6 dump／restore／drill 三形；落點 `$HOME` 防跨代撞名；子節細目同承 rev5:RUNBOOK §6.1～§6.5）。隨對應刀補實文。

## 7. 機密輪替表（生成明細→`deploy/secrets/README.md`；密文面連帶＝§15）

抬頭＝落點取值片段（**刻意不設回退**：只嚴格讀 `.env` 一行、取不到即印 FAIL；與 `tools/bootstrap.sh` 同口徑）：

```bash
SD="$(sed -n 's/^SECRETS_DIR=//p' .env)"; [ -n "$SD" ] || { echo "FAIL：.env 無 SECRETS_DIR= 行"; exit 1; }; echo "$SD"
```

十三機密對照表、dual-write 不變式、輪替連帶皆住 `deploy/secrets/README.md`；本章隨首個機密事件補實。

## 8. reaper 操作

`python3 deploy/setup-reaper-role.py`（reaper role 設密、走 `docker compose exec psql`）。隨 jobs 軌刀補實文。

## 9. 維運端點與 DB 直連

DB 直連（dev stack）：`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres psql -U soybean -d soybean_admin_rust`（rev6 stack、host 埠 35432；埠全表＝`docs/generated/reference/ports.md`；★rev6 的 psql 絕不指向 rev5 庫 25432）。其餘維運端點隨對應刀補實文。

## 9c. CDP 真登入走查的環境還原契約

隨首個需走查的刀遷入（工具承 rev5 `tools/walkthrough-baseline.py`；契約住本節、CLAUDE.md §7 以節名引）。

## 10. migration 操作

migration 短號形制＝`m0001` 四碼（ADR-00008；承襲 rev5 migration 時 `rev5:m001`→`m0001` 改名）。基線＝`m0001_baseline_schema`（結構）＋`m0002_baseline_seeds`（seed、完全決定性），程式內容逐位元承襲 rev5 終態（憲法 §I.5 例外②、ADR-00009／ADR-00010）；第一支 delta 自 `m0003` 起編。重放＝`docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm migrate`（＝migration up、容器內；已 applied 即回「No pending migrations」）；`seaql_migrations` 記錄名＝四碼新名。

★**Day-1 登記紀律（隨刀常設）**：每支帶 migration 的刀**收刀前必跑**下列三步（契約＝`specs/001-schema-baseline/contracts/gates.md` §5；`rev4:` 紅燈裸奔兩刀教訓、`rev5:K1-39`）：

1. `python3 tools/docsync refresh` —— 照相（schema／accounts 兩快照前進、六撈全成功才原子落檔；需運行中 stack）
2. 登記 `docs/ops/reference-src/schema-evolution.json` —— 該刀**全部**結構／seed 變更逐筆入帳；形（kind 枚舉、每筆必備鍵、來源刀編號）與壞形斷言＝`specs/001-schema-baseline/contracts/schema-evolution.md` §2。
   - ★唯一操作分岔：本刀含**刪除性**演進＝不入本檔、屬拍板級（走新 ADR 基線翻案）。
   - 工具回 rc 2＝登記壞形或合成未內建，一律照其輸出訊息的補救提示處置（勿自行放行）。
3. `python3 tools/schema-gate.py check` —— 三閘（gate1 結構／gate2 欄序＋seed／audit archetype）全綠才收刀；未登記漂移一律紅。
   - 一次性 pristine 場景加 `--container <容器名>`（預設＝compose dev stack）。
   - 判讀提示：同庫反覆 DROP→ADD COLUMN（含 down→up）後 gate1 會因 PG attnum 空洞報 ordinal 差——補救＝pristine 重放、勿誤判真漂移（承 `rev5:RUNBOOK` §10 實證）。

新業務表另備兩件：先補 `docs/ops/reference-src/schema-definition.md` §1 archetype 歸屬、再登記 `docs/ops/reference-src/archetype-map.json`——否則 audit 表清單守門攔。

## 11. 觀測層維運

隨觀測刀補實文。

## 12. 工具鏈速查（python 工具一律 `python3` 前綴直跑）

rc 判讀先辨層次：`rc=1` 常是工具**拒絕執行**（參數錯、零測試跑）而非受測物真失敗——雙證＝rc＋輸出行為。

| 命令 | 作用 | 需運行中 stack |
|---|---|---|
| `python3 tools/docsync generate` | 由真源重算全部生成物（GENERATED_FILES 名冊；跑完必 `git add`） | 否 |
| `python3 tools/docsync check` | GT-01 零漂移比對（pre-commit 第一道） | 否 |
| `python3 tools/docsync lint` | GT-01～GT-12 全數（GT-01 與 check 同源；pre-commit 第二道；Day-1 豁免逐筆具名 SKIP） | 否 |
| `python3 tools/docsync rules emit --scope <implementer\|review\|fix\|主線\|人> [--format js]` | 規則塊＋`RULES-VERSION`（Workflow script 必帶、PreToolUse hook 對賬） | 否 |
| `python3 tools/docsync errata <詞>` | 全 repo（含兩子庫 pin 樹）同語意枚舉 | 否 |
| `python3 tools/docsync test` | 治理工具自測（語料面 tests/） | 否 |
| `python3 tools/docsync refresh` | 自實庫撈 schema／accounts 兩快照（`docs/ops/reference-src/{schema,accounts}-snapshot.json`；六撈全成功才原子落檔；Day-1 三步之①、§10） | 是 |
| `python3 tools/schema-gate.py check｜test｜doccheck` | check＝三閘全跑（gate1 結構／gate2 欄序＋seed／audit archetype；三閘左源與判準＝ADR-00010；入口先自證 self-test；不進 pre-commit、手動／review 輪跑；一次性 pristine 加 `--container <容器名>`）／test＝離線自測（含 negative 五類）／doccheck＝data-model §2／§6／§9 vs 凍結 fixtures 離線對賬（★不入 pre-commit 常跑鏈、護雙錨）；rc 0 全等／1 差異／2 環境或結構異常／64 用法錯 | check 是；test／doccheck 否 |
| `python3 tools/entity-drift-gate.py check｜test` | check＝`rust-api/entity/src` vs schema 快照雙向比對（表／欄完整性＋型別＋可空性；欄序歸 gate2、index／constraint 歸 gate1）——pre-commit entity-drift 段於 rust-api pin bump 或快照 staged 時實跑、★快照缺席即紅（hook 段 rc 2＋提示 `python3 tools/docsync refresh` 照相）／test＝自測；rc 同上 | 否 |
| `python3 tools/rust-fmt-gate.py check｜test` | check（預設）＝rust-api 容器內 `cargo fmt --all --check` 唯讀比對（設定＝`rust-api/rustfmt.toml`）；docker 不在 PATH／compose 兩檔缺／`rust-api` 容器未起＝具名跳過 rc 0、未格式化 rc 1（逐段計數＋補救命令）、容器在而 cargo-fmt 缺 rc 2／test＝離線自測（subprocess 全樁）；rc 64 用法錯 | check 是（未起＝具名跳過）；test 否 |
| `python3 tools/wire-schema.py extract｜check [--staged-gate]｜test` | extract＝base-web 容器內 typings→draft-07 JSON Schema 快照、原子寫 `rust-api/server/tests/fixtures/wire-schema.json`／check＝重抽至暫存與工作樹快照 byte 比對、絕不覆寫（`--staged-gate`＝staged base-web 區間零 typings 變動即跳過）；docker 缺／`base-web` 容器未起＝具名跳過 rc 0、重抽失敗或快照缺席或不一致＝rc 2／test＝離線自測；rc 64 用法錯 | extract 是；check 未起＝具名跳過；test 否 |
| `python3 tools/fork-delta-lint.py [test] [--constitution <path>]` | 無引數＝self-test＋全掃 base-web vs 源倉 `example` 基線（修改型缺 `原行:`／新增型缺圈界〔含新檔檔頭一行＋軌道×路徑〕／授權判定；rc 0 綠／1 違規／2 結構斷言敗或源倉未在 example）／test＝離線只跑 self-test（bootstrap 名冊）／`--constitution`＝只供自身變異驗證、日常一律預設憲法路徑；rc 64 用法錯 | 否（前置＝源倉在 example、bootstrap 斷言） |
| `python3 tools/wf-watchdog.py <冒煙token> [wf目錄\|runId]` | Workflow 看門狗（stall／runaway 保險絲；與 Workflow launch 同回合成對） | 否 |
| `bash tools/bootstrap.sh` | 新機重建／舊機體檢（§1 步驟 1） | 否 |
| `node tools/orchestration/harness-test.mjs <組裝好的 script.mjs> [spec\|quality]` | 編排骨架 harness 自測（十二案、逐項斷言、rc 1 即紅） | 否 |
| `node tools/orchestration/cdp.mjs` | CDP 對照走查工具（127.0.0.1:9229；CLAUDE.md §7） | 是（host 瀏覽器） |
| `python3 deploy/generate-secrets.py [--force\|--compose-only]` | 十三機密缺則補／全重生／只重組 composite | 否（需 docker） |
| `python3 deploy/preflight-secrets.py` | 上機前把關 | 否 |
| `python3 deploy/decrypt-secrets.py` | 密文→落點明文（`RV6_DECRYPT_MANUAL=1`＝逐次手打退路） | 否（需 docker＋tty） |
| `python3 deploy/setup-reaper-role.py` | reaper role 設密（§8） | 是 |
| `python3 deploy/backup-db.py` | DB 備份／還原（§6） | 是 |
| `./deploy/sops.sh <sops 參數>` | sops 官方容器 wrapper（digest 釘版；鑰選取＝`RV6_AGE_KEY_FILE` 優先、否則命名紀律預設檔） | 否（需 docker） |
| `bash deploy/generate-age-key.sh [檔名]` | 產 age 金鑰（容器化；覆蓋閘） | 否（需 docker＋tty） |
| `bash deploy/generate-dev-cert.sh` | dev TLS 憑證（§1 步驟 4） | 否（需 docker） |

**碼面閘表**（名冊唯一權威；碼面閘＝RULES 名詞段定義、屬系統面、不計入 GT-12 的 ≤12 治理閘預算、GATES.md 不收）。GT-12 腿機器對賬：`tools/` 頂層 tracked `*.py` − `NON_GATE_TOOLS`（`tools/docsync/gates.py` 常數，現＝`tools/wf-watchdog.py`）⇔ 本表首欄反引號路徑集，雙向差集即紅、表缺席或零路徑列即紅；首欄非路徑者＝註記列、不計。「根據 ADR」欄之 rev6 ADR 暫記題名（預告；序號回填條＝002 刀 tasks T041）。

| 工具檔 | 守什麼 | 觸發時機（含環境缺席語意） | 根據 ADR |
|---|---|---|---|
| `tools/schema-gate.py` | schema 三閘：凍結 fixtures ⊕ 演進帳 vs 實庫（gate1 結構／gate2 欄序＋seed／audit archetype）＋doccheck 離線對賬 | 不進 pre-commit 常跑鏈（護雙錨）：`check` 手動／review 輪跑（需 stack）；pre-commit `schema-frozen` 段＝凍結存證或活體定稿 staged 時跑其 `test`；本體 staged 時自測 | ADR-00010（閘契約）；ADR-00016（碼面閘名冊承載於本表＋GT-12 腿） |
| `tools/entity-drift-gate.py` | `rust-api/entity/src` vs schema 快照雙向（表／欄完整性＋型別＋可空性；零 docker） | pre-commit entity-drift 段＝`rust-api` pin bump 或快照 staged 時 `check`；★快照缺席＝hook 段 rc 2 擋下＋提示 `python3 tools/docsync refresh`（不具名跳過）；本體 staged 時自測 | ADR-00010；ADR-00018（快照缺席即紅） |
| `tools/rust-fmt-gate.py` | rust 格式：容器內 `cargo fmt --all --check`（唯讀、絕不寫檔） | pre-commit rust-fmt 段＝`rust-api` pin bump 或本體 staged 時 `check`；docker 不在 PATH／compose 兩檔缺／`rust-api` 容器未起＝具名跳過 rc 0；容器在而 cargo-fmt 缺＝rc 2 fail-loud；未格式化＝rc 1；本體 staged 時自測 | ADR-00019（容器依賴型碼面閘之環境缺席語意＝具名跳過、工具缺席＝fail-loud；承 rev5:ADR 0057 決定 3） |
| `tools/wire-schema.py` | wire 契約：base-web typings → JSON Schema 快照 byte 比對（快照＝`rust-api/server/tests/fixtures/wire-schema.json`；唯讀鐵則、前端 porcelain 前後皆空） | pre-commit wire-schema 段＝`base-web` pin bump 時 `check --staged-gate`（staged 區間零 typings 變動即跳過）；docker 缺／`base-web` 容器未起＝具名跳過 rc 0；容器在而重抽失敗、快照缺席或不一致＝rc 2；本體 staged 時自測 | ADR-00019（容器依賴型碼面閘之環境缺席語意） |
| `tools/fork-delta-lint.py` | base-web fork-delta 標記：修改型缺 `原行:`／新增型缺圈界（含我方新檔之檔頭一行標記＋所稱軌道×檔路徑相符）／授權判定（憲法 §III.1 檔面收窄＋§III.2 三元組）＋名冊結構斷言（空 ★表以哨兵句守；§III.1 範圍欄反引號 token 集對賬本工具常數、次序不計，不符即 rc 2＝Amendment 須同批重導新增面判定） | pre-commit fork-delta 段＝`base-web` pin bump、本體或憲法 staged 時全掃（源倉在 `example`＝bootstrap 斷言；源倉缺席＝rc 2 fail-loud、hook 不設跳過分支）；`test`＝離線自測、入 bootstrap 名冊 | 憲法 §III（標記字面 `rev6-inline`＋★軌道授權）；哨兵句改形＝002 刀 research R10 |
| msg key 跨端閘 | 後端錯誤 msg key 名冊 ⇔ 前端 i18n 字典（非 `tools/` 工具檔形、GT-12 腿不計） | 延前端 i18n 刀進場（觸發由 BACKLOG 條目承載）；002 刀只閉後端側名冊（註記列） | ADR-00017（msg key 跨端契約延前端 i18n 刀、002 後端側閉環；承 rev5:Lint24） |

## 12b. 收刀簿記牆鐘量法（perf 事件 `close_bookkeeping` 的唯一命令形）

牆鐘**無法回溯量測**，必須在下 commit 之前就把命令包起來——RL-0053 的「簿記落地後量該顆牆鐘」講的是時序（先量再記），不是「事後補量」。

```sh
t0=$(date +%s.%N)
git commit -F <訊息檔>                     # 簿記顆；訊息含反引號一律 -F、絕不 -m
rc=$?; t1=$(date +%s.%N)
python3 -c "print(f'{float('$t1')-float('$t0'):.2f}')"   # ← 即 wall_s
```

`wall_s` 取兩位小數、`rc` 同記；事件另帶 `commit`（該簿記顆的 40 位 hex）與 `notes`（該顆 staged 面、哪些條件段未觸發）。append 後隨**下一顆** commit 入帳（該顆需同批 `generate` 重算 `reference/perf.md` 與 `STATE.md`）。

同法適用 `precommit_chain`（量的是帶 gitlink 或工具本體的單元 commit，用以對雙錨 45／90 秒）。

## 13. 故障排除速查

索引→`docs/ops/LESSONS.md`、全文→`docs/ops/LESSONS/`；本表只指路。前代候選＝rev5 `docs/ops/LESSONS.md`（唯讀、引用帶 `rev5:`）。

## 14. 埠與帳號

- 真相源：埠全表→`docs/generated/reference/ports.md`（機器生成；配號紀律＝ADR-00001、世代 3xxxx）；帳號／角色→`docs/generated/reference/accounts.md`（generate 產；真源＝`docs/ops/reference-src/accounts-snapshot.json`、`python3 tools/docsync refresh` 自實庫照相；dev 三帳 Super／Admin／User 之角色綁定承 rev5 對照基準、全表見該檔）。
- 本檔命令帶字面埠純為可複製執行；動埠的刀照勘誤紀律（`python3 tools/docsync errata <埠>`）機器枚舉全 repo 同步、含本檔。

## 15. SOPS 機密營運（密文入版控 × age 私鑰）

資產：密文 `deploy/secrets.dev.enc.yaml`（tracked；十支＝九 leaf＋`alert_webhook_url`）；recipient 兩把（`.sops.yaml`）＝開發鑰 `keys-fork260509-rev6.txt`（住 `~/.config/sops/age/`、世代錯開、不沿用 rev5 鑰）與離線復原鑰（只存離線、承 rev5:ADR 0015 子題三之義務；施工紀錄＝rev5:B-041）；wrapper `deploy/sops.sh`（鑰選取＝`RV6_AGE_KEY_FILE` 優先、否則命名紀律預設檔）；`RV6_DECRYPT_MANUAL=1`＝逐次手打退路。passphrase 只存持鑰者腦中與離線紙本、絕不進 chat／命令／檔案。
程序見 `deploy/secrets/README.md`（解密／重組／預檢三條路徑、亂數生成、特例與不變式）；加人、撤銷、值變更回寫、災難復原四情境、輪替表、手動 wrapper 三步——細節承 rev5:RUNBOOK §15 同節，隨首個機密事件補實。

### 15.2 加人四步（新成員／新機器）

承 rev5:RUNBOOK §15.2（產鑰→交公鑰入 `.sops.yaml`→`updatekeys`→新機 decrypt）；隨首個加人事件補實。

### 15.4 值變更後回寫加密檔

承 rev5:RUNBOOK §15.4（路徑 (a) 全套重建；不需 passphrase）；隨首個值變更事件（`alert_webhook_url` 真值）補實。

## 16. 部署 checklist

prod 不入 roadmap（rev6 尚未自立拍板、暫承 rev5:ADR 0014 為預設；若要做 prod 先立 ADR）；信任錨與 IP 存取閘設定＝`deploy/trust-model.dev.toml`。隨對應刀補實文。
