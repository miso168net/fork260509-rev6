# RUNBOOK — dev stack 操作手冊

本檔＝「怎麼操作」唯一的家。分工（防鏡像）：系統長怎樣→活書 `docs/arc42/`（索引 `docs/arc42/ARCHITECTURE.md`）；十三機密明細表→`deploy/secrets/README.md`；埠全表→`docs/generated/reference/ports.md`；閘名冊→`docs/generated/GATES.md`；坑索引→`docs/ops/LESSONS.md`（全文＝`docs/ops/LESSONS/` 一坑一檔）。
本檔命令一律完整可複製、於 repo 根執行。章節編號承 rev5（`deploy/secrets/README.md` 以 §7／§15 指向本檔；改號＝勘誤級）。
創世期章節現況：§1／§4／§7 抬頭／§9c／§10／§12／§12b／§12c／§14／§16 為已補實文章、§15 為指針章；§9 已補 DB 直連與管理員解鎖、其餘維運端點與其餘各章隨對應刀補實文，章內不放未經實跑的命令。（本句為章節現況的唯一人寫家；README 文件系統地圖該列只指回本句、不重述名冊。）

## 1. 快速啟動（新機五步）

1. `bash tools/bootstrap.sh` —— 源倉 clone＋worktree＋hooksPath＋betterleaks 釘版＋hooks 指紋＋rev5 凍結斷言＋例外①自證＋docsync 三段＋閘數＋secrets 體檢（幂等、可重跑；remote 未設只 ⚠）
2. `python3 deploy/generate-secrets.py` —— 十三機密缺則補（`alert_webhook_url` 為佔位值、見 §4）
3. `python3 deploy/preflight-secrets.py` —— up 前預檢（缺檔／CR·LF／composite drift 一律非零退出）
4. `bash deploy/generate-dev-cert.sh` —— dev TLS 憑證（front-nginx 恆 bind-mount 兩支 pem，缺檔＝Docker 代建空目錄佔位→nginx 起不來）
5. `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait` —— 起預設業務件（migrate 是啟動閘：migration 失敗→rust-api 不啟）

已有 age 私鑰的新機：步驟 2 前先 `python3 deploy/decrypt-secrets.py`（自密文還原十支；passphrase 只輸入一次）。

## 2. 日常起停

`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait`／`stop`／`ps`；host 埠世代 3xxxx（ADR-00001；真表＝`docs/generated/reference/ports.md`）。rev5 對照 stack 常駐 2xxxx、兩 stack 併行是預期形（CLAUDE.md §7）。
★pull／checkout 動到 `deploy/trust-model.dev.toml`（含純註解改動）後，rust-api 容器**必重建**：`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate --no-deps rust-api`——該檔為單檔 bind mount、git 換檔即懸空，watchexec 重啟與 `restart` 皆不重掛；徵狀不紅、只在 boot 日誌現 `信任模型載入告警 kind=Missing` 與 `internal_default:0`（LL-00033；secrets 檔同口徑＝`deploy/secrets/README.md`）。其餘隨對應刀補實文。

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

DB 直連（dev stack）：`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres psql -U soybean -d soybean_admin_rust`（rev6 stack、host 埠 35432；埠全表＝`docs/generated/reference/ports.md`；★rev6 的 psql 絕不指向 rev5 庫 25432）。

管理員解鎖登入節流（`POST /systemManage/unlockLogin`；API-only、限 `R_SUPER`；契約與處理序＝活書 §6.1「登入失敗節流——島 E」⑥，無 UI 按鈕＝ADR-00040 款 1）。先以超管帳號登入取票，再擇一維度：

```bash
BASE=http://127.0.0.1:32080/api
TOKEN=$(curl -s "$BASE/auth/login" -H 'content-type: application/json' -d '{"userName":"<超管帳號>","password":"<密碼>"}' | jq -r .data.token)
# 來源維（位址字面；v6 由後端聚合為 /64 桶）
curl -s "$BASE/systemManage/unlockLogin" -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' -d '{"dimension":"ip","target":"<來源位址>"}' | jq -r .code
# 帳號維（帳號名原文）
curl -s "$BASE/systemManage/unlockLogin" -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' -d '{"dimension":"user","userName":"<帳號名>"}' | jq -r .code
```

`0000`＝已解鎖、下一次登入嘗試即自該時刻重新計數（未鎖標的亦回 `0000`）；`2222 biz.throttle.invalidUnlockTarget`＝維度或標的畸形（零稽核零狀態）。每次解鎖落一列操作稽核，查核：`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres psql -U soybean -d soybean_admin_rust -c "SELECT operation, entity_table, payload_after, real_ip, created_at FROM sys_operation_log WHERE operation='unlock' ORDER BY id DESC LIMIT 5"`。其餘維運端點隨對應刀補實文。

## 9c. CDP 真登入走查的環境還原契約

工具＝`tools/walkthrough-baseline.py`（隨遷自 rev5 同名工具、`rev5:L-071` 防法①的機制化；非碼面閘＝`NON_GATE_TOOLS` 成員、不掛 pre-commit 條件觸發、走查前後手動跑）。★只指向 rev6 dev stack（compose 專案＝倉庫根、埠 3xxxx）、絕不指向 rev5 對照 stack（2xxxx）。基準檔落 `tmp/walkthrough-<日期>.json`（gitignored；`<檔>` 必填、無隱含預設落點）。三面（表／序列／redis）與唯讀實作口徑＝工具 docstring（唯一人寫家、不在本節複述）；命令與需否 stack＝§12 工具鏈速查。CLAUDE.md §7 以節號引本節。

1. 走查前：`python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-<日期>.json`（rc 0；輸出附三面規模＝表／序列／redis 鍵與前綴數，證明比對面非空）。
2. 走查：CDP 接 `127.0.0.1:9229`、開 32080（對照 22080＝rev5 UI）；勿於秒內狂打 auth 端點——nginx `auth_limit` 5r/s burst 40 回 429。
3. 清理（順序固定、由工具承載）：前置＝`system_settings` 值（如 `single_session_default`）若於走查中被改→先以 002 刀 `system_settings` 寫端改回 seed 值（restore **不自動改值**：值≠凍結 seed 即 rc 2 指名該鍵；seed 左源只讀凍結段、未合成演進——`docs/ops/reference-src/schema-evolution.json` 有 `system_settings` 之 `seed_*` 登記即 rc 2 指名登記 id、須先擴充工具）；再跑 `python3 tools/walkthrough-baseline.py restore tmp/walkthrough-<日期>.json`——①值＝seed 而 `updated_at`／`updated_by` 審計欄非 NULL 者歸 NULL（改回值≠改回痕）②清理面五表（會話三表 `session_event`／`sys_token`／`sys_login_attempt`＋`sys_ip_rule`＋`sys_operation_log`；名冊住工具常數）全表清空＋`sys_user.session_id` 歸 NULL ③五表之 id 序列 `setval` 回本次 snapshot 現讀值（①～③ 單交易、任一句敗即整筆回滾；寫句字面住工具常數、自測逐字釘住，本節不抄）④redis `session:`／`throttle:` 前綴逐鍵 DEL（不 FLUSHDB）⑤收尾自動跑一次 diff、其 rc 即 restore 之 rc（rc 0＝第 4 步判準已成立）。★安全帶：基準檔五表列數或 `session`／`throttle` 前綴鍵數非 0＝rc 2 拒跑、零寫入（DELETE 全表會毀掉基準資料）——基準檔模式只服務走查前為空基準之形；補救＝改用取於空基準之較早 snapshot 檔，無此檔＝改跑 seed 模式。★seed 模式＝`python3 tools/walkthrough-baseline.py restore --seed`（無須基準檔、目標態＝凍結 seed；與 `<檔>` 擇一；服務走查外殘列——被殺測試留下之列與鍵——此類殘列產生時通常無空基準檔可用）：清理步驟同上、差三處——(a)安全帶改對凍結 seed（五表於 seed 須零列；演進帳拒跑判定由 `system_settings` 擴及五表）(b)③只 `setval` `sys_ip_rule_id_seq`（值自凍結 seed 現讀）、runtime-append 四表之序列不復位(c)⑤收尾比對之判準面＝清理面對 seed 目標值、其 rc 即 restore 之 rc；清理面之外無基準可比＝不判，pg 殘留由第 4 步後段之 `python3 tools/schema-gate.py check` 兜。
   ★restore 以 SQL 直清 `sys_ip_rule`、不經規則寫端＝判定面不會自己換版——**工具已自動補按門鈴**（BL-00094）：清前 `sys_ip_rule` 列數非 0 時，④之後多一步 ④b `PUBLISH ipgate:invalidate` 並回報訂閱者數；回 **0＝無 watcher 在訂**（rust-api 未起或 watcher 未啟，其判定面於下次啟動才換版）——此時才需人工介入（重啟 rust-api）。清前 0 列＝該表本就是空的、不按。★工具按不到時（PUBLISH 回非整數／redis 不可用）會拋錯並附可照抄的完整命令——`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T redis sh -lc 'redis-cli -a "$(cat /run/secrets/redis_password)" --no-auth-warning PUBLISH ipgate:invalidate 1'`（回 1＝訂閱者在）；★重跑 restore 補不回來（屆時清前已 0 列）。走查動過 IP 規則者，restore 後仍建議以原被擋來源打一支端點確認已放行。
4. `python3 tools/walkthrough-baseline.py diff tmp/walkthrough-<日期>.json` **rc 0 才算環境已還原**（三閘綠不算、`rev5:L-071` 招牌徵狀＝三閘綠而全量紅）；之後才跑 `python3 tools/schema-gate.py check`。★序列面例外一項：runtime-append 四表（`session_event`／`sys_login_attempt`／`sys_operation_log`／`sys_token`；名冊住工具常數、與 `tools/schema-gate.py` 同名常數同值、自測對賬）之 id 序列只比存在性、不比值（同 gate2 口徑；這四支在測試與走查中只進不退、rust-api 測試守衛不復位序列），其餘序列（含 `sys_ip_rule_id_seq`）照比值。走 seed 模式而手上無走查前基準檔者＝以其 restore 之 rc 0 為準、免跑本步之 diff（有基準檔者照跑）；`schema-gate.py check` 兩形皆照跑。
5. 判準：restore（或其後 diff）回 rc 1＝①～④已完成而差異落在固定清理面之外——依 diff 列出之表／序列／前綴人工清理該面後重跑第 4 步至 rc 0（`rev5:L-071` 防法②：清理面＝走查期間被寫過的全部表、與任何閘的射程無關）；該面須常設清理者＝擴 restore 清理面（工具改動）。seed 模式之 rc 1＝清理面未達 seed 目標值（依列出項處置後重跑）。`sys_user` 列數不變但 diff 不報 `session_id`（列數面、非欄值）⇒ 第 3 步 `session_id` 還原由 gate2 seed 逐列比對兜底。

退出碼：0 全等／1 有差（列出差異表／序列／前綴＋末行摘要）／2 環境或結構異常（docker 不可執行、psql／redis 失敗、基準檔缺席或壞形、比對面為空＝假綠；restore 另含安全帶拒跑、基準檔缺清理面之表或序列、seed 左源缺席或不可解、演進登記檔缺席或壞形、`system_settings` 有 `seed_*` 演進登記、`system_settings` 值≠seed；seed 模式另含凍結 seed 缺清理面之 COPY 段或 setval 行、清理面五表有 `seed_*` 演進登記）／64 用法錯（含 `<檔>` 與 `--seed` 並帶）；restore 之 0／1 即其收尾比對之 rc。`test`＝離線自測（零 docker；pre-commit 於本體 staged 時、bootstrap 名冊皆跑）。

## 10. migration 操作

migration 短號形制＝`m0001` 四碼（ADR-00008；承襲 rev5 migration 時 `rev5:m001`→`m0001` 改名）。基線＝`m0001_baseline_schema`（結構）＋`m0002_baseline_seeds`（seed、完全決定性），程式內容逐位元承襲 rev5 終態（憲法 §I.5 例外②、ADR-00009／ADR-00010）；第一支 delta 自 `m0003` 起編。★例外②邊界稽核以 ADR-00009 之 17 檔為準：migration／entity 兩 crate 之 `main.rs`／`lib.rs`／`Cargo.toml` 五檔為承形自寫（env 橋接與 manifest 座標）、去註解後與 rev5 凍結樹只差改名級差異（模組名 `rev5:m001`→`m0001`、變數 `file_path`→`path`、其餘零差異）＝自然收斂，不屬例外②射程、亦非未登記拷貝（001 刀收單 `be69543` 訊息載 main.rs 一項）。重放＝`docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm migrate`（＝migration up、容器內；已 applied 即回「No pending migrations」）；`seaql_migrations` 記錄名＝四碼新名。

★**Day-1 登記紀律（隨刀常設）**（與 `docs/generated/GATES.md`／RL-0051 之「Day-1 豁免」為同名不同物——本項是隨刀常設的 migration 登記三步、與閘的掃描面缺席豁免無關）：每支帶 migration 的刀**收刀前必跑**下列三步（契約＝`docs/ops/reference-src/schema-gates.md` §5；`rev4:` 紅燈裸奔兩刀教訓、`rev5:K1-39`）：

1. `python3 tools/docsync refresh` —— 照相（schema／accounts 兩快照前進、六撈全成功才原子落檔；需運行中 stack）
2. 登記 `docs/ops/reference-src/schema-evolution.json` —— 該刀**全部**結構／seed 變更逐筆入帳；形（kind 枚舉、每筆必備鍵、來源刀編號）與壞形斷言＝`docs/ops/reference-src/schema-evolution-contract.md` §2。
   - ★唯一操作分岔：本刀含**刪除性**演進＝不入本檔、屬拍板級（走新 ADR 基線翻案）。
   - 工具回 rc 2＝登記壞形或合成未內建，一律照其輸出訊息的補救提示處置（勿自行放行）。
3. `python3 tools/schema-gate.py check` —— 三閘（gate1 結構／gate2 欄序＋seed／audit archetype）全綠才收刀；未登記漂移一律紅。
   - 一次性 pristine 場景加 `--container <容器名>`（預設＝compose dev stack）。
   - 判讀提示：同庫反覆 DROP→ADD COLUMN（含 down→up）後 gate1 會因 PG attnum 空洞報 ordinal 差——補救＝pristine 重放、勿誤判真漂移（承 `rev5:RUNBOOK` §10 實證）。

新業務表另備兩件（★跨刀活體一律指 `docs/ops/reference-src/schema-definition.md`；`specs/001-schema-baseline/data-model.md` 為凍結存證、不再前進＝ADR-00012）：先補 `docs/ops/reference-src/schema-definition.md` §1 archetype 歸屬、再登記 `docs/ops/reference-src/archetype-map.json`——否則 audit 表清單守門攔。

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
| `python3 tools/docsync vendored-check [--rev5 <路徑>]` | 憲法 §I.5 例外① 自證：`rust-api/sea-orm-adapter` 全部 tracked 檔去整行註解後 diff rev5 凍結樹、差異須逐對在 `tools/docsync/vendored.py` 具名 ALLOWLIST（附理由）；bootstrap 3c 步呼叫；rev5 樹缺席 rc 2、差異 rc 1 | 否 |

★例外①自證射程＝`rust-api/sea-orm-adapter`；憲法 §I.5 例外①另列名之 `xdb` 在 rev6 與 rev5 凍結樹**皆無實例**（rev5 dev 尾巴、001 spec 明列不入刀），日後若進場須同批擴 `tools/docsync/vendored.py` 之 `VENDORED_DIR` 射程。
| `python3 tools/docsync test` | 治理工具自測（語料面 tests/） | 否 |
| `python3 tools/docsync refresh` | 自實庫撈 schema／accounts 兩快照（`docs/ops/reference-src/{schema,accounts}-snapshot.json`；六撈全成功才原子落檔；Day-1 三步之①、§10） | 是 |
| `python3 tools/schema-gate.py check｜test｜doccheck` | check＝三閘全跑（gate1 結構／gate2 欄序＋seed／audit archetype；三閘左源與判準＝ADR-00010；入口先自證 self-test；不進 pre-commit、手動／review 輪跑；一次性 pristine 加 `--container <容器名>`）／test＝離線自測（含 negative 五類）／doccheck＝活體定稿 `docs/ops/reference-src/schema-definition.md` §2／§6／§9 vs 凍結 fixtures 離線對賬（左源座標＝ADR-00012）（★不入 pre-commit 常跑鏈、護雙錨）；rc 0 全等／1 差異／2 環境或結構異常／64 用法錯 | check 是；test／doccheck 否 |
| `python3 tools/entity-drift-gate.py check｜test` | check＝`rust-api/entity/src` vs schema 快照雙向比對（表／欄完整性＋型別＋可空性；欄序歸 gate2、index／constraint 歸 gate1）——pre-commit entity-drift 段於 rust-api pin bump 或快照 staged 時實跑、★快照缺席即紅（hook 段 rc 2＋提示 `python3 tools/docsync refresh` 照相）／test＝自測；rc 同上 | 否 |
| `python3 tools/rust-fmt-gate.py check｜test` | check（預設）＝rust-api 容器內 `cargo fmt --all --check` 唯讀比對（設定＝`rust-api/rustfmt.toml`）；docker 不在 PATH／compose 兩檔缺／`rust-api` 容器未起＝具名跳過 rc 0、未格式化 rc 1（逐段計數＋補救命令）、容器在而 cargo-fmt 缺 rc 2／test＝離線自測（subprocess 全樁）；rc 64 用法錯 | check 是（未起＝具名跳過）；test 否 |
| `python3 tools/wire-schema.py extract｜check [--staged-gate]｜test` | extract＝base-web 容器內 typings→draft-07 JSON Schema 快照、原子寫 `rust-api/server/tests/fixtures/wire-schema.json`／check＝重抽至暫存與工作樹快照 byte 比對、絕不覆寫（`--staged-gate`＝**兩側** pin 區間皆零變動才跳過：base-web 區間零 typings 變動＋rust-api 區間零快照變動）；docker 缺／`base-web` 容器未起＝具名跳過 rc 0、重抽失敗或快照缺席或不一致＝rc 2／test＝離線自測；rc 64 用法錯 | extract 是；check 未起＝具名跳過；test 否 |
| `python3 tools/fork-delta-lint.py [test] [--constitution <path>]` | 無引數＝self-test＋全掃 base-web vs 源倉 `example` 基線（修改型缺 `原行:`／新增型缺圈界〔含新檔檔頭一行＋軌道×路徑〕／授權判定；rc 0 綠／1 違規／2 結構斷言敗或源倉未在 example）／test＝離線只跑 self-test（bootstrap 名冊）／`--constitution`＝只供自身變異驗證、日常一律預設憲法路徑；rc 64 用法錯 | 否（前置＝源倉在 example、bootstrap 斷言） |
| `python3 tools/msg-key-gate.py check｜test [--rust <error.rs>] [--locales <dir>] [--src <dir>]` | check（預設）＝左源 `MSG_KEYS` ⇔ 三檔 locale backend 子樹逐檔雙向全等＋Biz 構造點守衛＋前端 msg 字面消費點名冊（碼面閘表列；pre-commit msg-key-gate 段於 rust-api／base-web pin bump 或本體 staged 時跑）／test＝離線 self-test（合成契約案＋判準補強案〔斷言 2 比對面為空／同義構造形／`MSG_KEYS` 宣告數≠元素數／Biz 構造鍵之名冊歸屬兩分支〕＋真 repo 左源綠案＋斷言 3 案；案數以 `test` 輸出為準；pre-commit 自測迴圈與 bootstrap 名冊呼叫）；`--rust`／`--locales`／`--src` 只供自測注入、日常一律預設路徑；rc 0 綠／1 違規／2 結構異常／64 用法錯 | 否 |
| `python3 tools/view-render-guard.py check｜test` | check（預設）＝逐行掃 `base-web/src/views/manage/**`（`.vue`／`.ts`／`.tsx`／`.js`／`.jsx`）之原始 HTML 注入寫法被禁字面（碼面閘表列；不分註解與碼）；rc 0 綠／1 命中（指名檔:行）／2 base-web 工作樹或射程目錄缺席、零受掃檔／64 用法錯／test＝離線自測（逐條逐行反例、註解內字面照紅、三種 rc 2；pre-commit 自測迴圈與 bootstrap 名冊呼叫） | 否 |
| `python3 tools/route-artifact-gate.py check [--constitution <path>]｜test` | check（預設）＝base-web 容器內 `/tmp` 沙盒重跑路由外掛、三道斷言（①產出檔集對賬 ②工作樹為種重算冪等 ③上游基線為種零手改；碼面閘表列）、對工作樹唯讀；`--constitution`＝只供自身變異驗證、日常一律預設憲法路徑；rc 0 綠或具名跳過／1 任一道不通過（附 diff）／2 環境或結構異常／64 用法錯／test＝離線自測（subprocess 全樁；pre-commit 自測迴圈與 bootstrap 名冊呼叫）；★重算者＝dev server 內之該外掛（新 view 落地即自動重算、未觸發則重啟 base-web 服務）——`pnpm gen-route` 是互動腳手架、不重算 | check 是（未起＝具名跳過）；test 否 |
| `python3 tools/wf-watchdog.py <冒煙token> [wf目錄\|runId] [--rearm] [--bg]｜test` | Workflow 看門狗（stall／runaway 保險絲；與 Workflow launch 同回合原子成對、雙掛＝Monitor 腿＋`--bg` 背景長尾腿）；`test`＝離線自測，由 pre-commit 自測迴圈與 bootstrap 名冊呼叫——亦即冒煙 token 不可取字面 `test`（會被當自測子命令、CLAUDE.md §2） | 否 |
| `python3 tools/walkthrough-baseline.py snapshot <檔>｜diff <檔>｜restore <檔>｜restore --seed [--user U] [--db D]｜test` | 走查前後全表基準對賬與走查後清理（§9c 契約；非碼面閘＝`NON_GATE_TOOLS` 成員）：snapshot＝三面現算（public 全部表列數／全部序列 `last_value`＋`is_called`／redis `DBSIZE`＋逐前綴鍵數）寫 JSON 基準檔、`<檔>` 必填落 `tmp/walkthrough-<日期>.json`／diff＝重取現況逐值比對、只列有差者＋末行摘要、★rc 0 才算環境已還原（runtime-append 四表之 id 序列只比存在性、不比值＝同 gate2 口徑）／restore＝§9c 第 3 步清理面機器化（`system_settings` 值對凍結 seed、值≠seed 不改值即 rc 2、演進帳有其 `seed_*` 登記即 rc 2 指名 id；審計欄歸 NULL＋清理面五表 DELETE＋`session_id` 歸 NULL＋五支 setval 自基準現讀＝單交易；redis `session:`／`throttle:` 逐鍵 DEL；收尾 diff 之 rc 即其 rc；★基準五表或兩前綴非空＝rc 2 拒跑）／restore --seed＝無須基準檔、目標態＝凍結 seed（同上清理；只 setval `sys_ip_rule_id_seq`、值自凍結 seed 現讀，runtime-append 序列不復位；收尾比對面＝清理面對 seed 目標值；★凍結 seed 之五表非零列、或演進帳有 `system_settings`／五表之 `seed_*` 登記＝rc 2 拒跑）／test＝離線自測（subprocess 全樁；pre-commit 自測迴圈與 bootstrap 名冊呼叫）；snapshot／diff 唯讀（pg 只 SELECT、redis 只 DBSIZE／SCAN）、restore 寫面恰為所列語句（自測逐字釘住；pg 單交易＋④b `PUBLISH ipgate:invalidate` 門鈴〔清前 `sys_ip_rule` 非 0 時、排在 DEL 之前〕＋redis 逐鍵 DEL）、只指向 rev6 dev stack；`--user`／`--db` 預設同 `tools/schema-gate.py` 常數；rc 0 全等／1 有差／2 環境或結構異常（含比對面為空、restore 拒跑）／64 用法錯 | snapshot／diff／restore 是；test 否 |
| `python3 tools/comment-overlap.py [--min N] [--max-pct P] <rev6 檔 …>｜test` | rev5↔rev6 註解逐字重疊核（RL-0076 量尺；預設 `--min 40` 字元／`--max-pct 5`、逐檔超標 rc 1；rev5 對應檔＝同相對路徑，缺席且檔名 `rev6-` 起首者改找同目錄 `rev5-` 接其後同名之檔〔輸出行明示映射〕，仍缺席報 n/a；解析四形＝行首 `//`／`///`／`//!`、行首 `/*` 塊註解〔含單行 `/** */`〕、`.vue` 行首 `<!--` HTML 註解〔行尾 `//`、行中 `/* */`／`<!-- -->` 不收〕、`.py` 以 tokenize＋ast 取行首 `#` 與**真** docstring〔首行 shebang 與行尾 `#` 不收；語法不合＝退回只取行首 `#`〕與 `.sh`／`.bash` 行首 `#`（★「隨遷工具」逐字承襲允許、不適用 RL-0076 之 rc 0 要求），rev6 檔／rev5 對應檔／源倉基線同一解析器；base-web 路徑三型豁免後量〔`[rev6-inline …]` 標記 token 本身（同行散文照計）／源倉 `example` 基線原有註解行／`原行:` 起至行尾〕、rust-api 等其餘路徑零三型豁免；全路徑碼面豁免接其後〔行內反引號 code span／doc 註與塊註解內之三反引號圍欄；未閉合圍欄照計並指名開啟行號；rev5 文本不豁免〕；本次引數之 rev5 對應檔全缺席或受比檔全體零可解析註解＝比對面為空 rc 2；非碼面閘＝`NON_GATE_TOOLS` 成員、自測入 pre-commit 條件觸發名冊與 bootstrap 名冊；只准項既有超標＝BACKLOG 承載） | 否 |
| `bash tools/bootstrap.sh` | 新機重建／舊機體檢（§1 步驟 1） | 否 |
| `python3 tools/orchestration/assemble.py <unitdef.py> <out.mjs>` | Workflow script 組裝器（單元定義→成品；unitdef `MODE` 決定 tdd／review 拼接序；三道自檢＝RULES-VERSION 對賬／node --check／harness，任一紅不留產物） | 否 |
| `node tools/orchestration/harness-test.mjs <組裝好的 script.mjs> [spec\|quality]` | TDD 形編排骨架 harness 自測（十八案＝十二正例＋六反例、逐項斷言、rc 1 即紅） | 否 |
| `node tools/orchestration/harness-review.mjs <組裝好的 script.mjs>` | review 形編排骨架 harness 自測（九案＝六正例＋三反例、逐項斷言、rc 1 即紅） | 否 |
| `tools/orchestration/cdp.mjs`（非命令：供 import 的 CDP driver 模組，export `connect(wsUrl)`／`sleep(ms)`） | CDP 對照走查 driver：走查腳本自 tmp/ 起、import 本模組接 host 瀏覽器除錯埠 127.0.0.1:9229（CLAUDE.md §7） | 是（host 瀏覽器） |
| `python3 deploy/generate-secrets.py [--force\|--compose-only]` | 十三機密缺則補／全重生／只重組 composite | 否（需 docker） |
| `python3 deploy/preflight-secrets.py` | 上機前把關 | 否 |
| `python3 deploy/decrypt-secrets.py` | 密文→落點明文（`RV6_DECRYPT_MANUAL=1`＝逐次手打退路） | 否（需 docker＋tty） |
| `python3 deploy/setup-reaper-role.py` | reaper role 設密（§8） | 是 |
| `python3 deploy/backup-db.py` | DB 備份／還原（§6） | 是 |
| `./deploy/sops.sh <sops 參數>` | sops 官方容器 wrapper（digest 釘版；鑰選取＝`RV6_AGE_KEY_FILE` 優先、否則命名紀律預設檔） | 否（需 docker） |
| `bash deploy/generate-age-key.sh [檔名]` | 產 age 金鑰（容器化；覆蓋閘） | 否（需 docker＋tty） |
| `bash deploy/generate-dev-cert.sh` | dev TLS 憑證（§1 步驟 4） | 否（需 docker） |

**碼面閘表**（名冊唯一權威；碼面閘＝RULES 名詞段定義、屬系統面、不計入 GT-12 的 ≤12 治理閘預算、GATES.md 不收）。GT-12 腿機器對賬：`tools/` 頂層 tracked `*.py` − `NON_GATE_TOOLS`（`tools/docsync/gates.py` 常數；成員以該常數為準、此處不鏡像）⇔ 本表首欄反引號路徑集，雙向差集即紅、表缺席或零路徑列即紅；首欄非路徑者＝註記列、不計。「根據 ADR」欄＝該閘之 rev6 ADR 序號（accepted；新列進場同批填）；閘本體直接由憲法節授權者填該節（如 `tools/fork-delta-lint.py`＝憲法 §III）。

| 工具檔 | 守什麼 | 觸發時機（含環境缺席語意） | 根據 ADR |
|---|---|---|---|
| `tools/schema-gate.py` | schema 三閘：凍結 fixtures ⊕ 演進帳 vs 實庫（gate1 結構／gate2 欄序＋seed／audit archetype）＋doccheck 離線對賬 | 不進 pre-commit 常跑鏈（護雙錨）：`check` 手動／review 輪跑（需 stack）；pre-commit `schema-frozen` 段＝凍結存證或活體定稿 staged 時跑其 `test`；本體 staged 時自測 | ADR-00010（閘契約）；ADR-00032（碼面閘名冊承載於本表＋GT-12 腿） |
| `tools/entity-drift-gate.py` | `rust-api/entity/src` vs schema 快照雙向（表／欄完整性＋型別＋可空性；零 docker） | pre-commit entity-drift 段＝`rust-api` pin bump 或快照 staged 時 `check`；★快照缺席＝hook 段 rc 2 擋下＋提示 `python3 tools/docsync refresh`（不具名跳過）；本體 staged 時自測 | ADR-00010；ADR-00018（快照缺席即紅） |
| `tools/rust-fmt-gate.py` | rust 格式：容器內 `cargo fmt --all --check`（唯讀、絕不寫檔） | pre-commit rust-fmt 段＝`rust-api` pin bump 或本體 staged 時 `check`；docker 不在 PATH／compose 兩檔缺／`rust-api` 容器未起＝具名跳過 rc 0；容器在而 cargo-fmt 缺＝rc 2 fail-loud；未格式化＝rc 1；本體 staged 時自測 | ADR-00019（容器依賴型碼面閘之環境缺席語意＝具名跳過、工具缺席＝fail-loud；承 rev5:ADR 0057 決定 3） |
| `tools/wire-schema.py` | wire 契約：base-web typings → JSON Schema 快照 byte 比對（快照＝`rust-api/server/tests/fixtures/wire-schema.json`；唯讀鐵則、前端 porcelain 前後皆空） | pre-commit wire-schema 段＝`base-web` **或 `rust-api`** pin bump 時 `check --staged-gate`（雙側觸發、對稱於 entity-drift：typings 側住 base-web、快照側住 rust-api worktree；兩側 pin 區間皆零變動才跳過）；docker 缺／`base-web` 容器未起＝具名跳過 rc 0；容器在而重抽失敗、快照缺席或不一致＝rc 2；本體 staged 時自測 | ADR-00019（容器依賴型碼面閘之環境缺席語意） |
| `tools/fork-delta-lint.py` | base-web fork-delta 標記：修改型缺 `原行:`／新增型缺圈界（含我方新檔之檔頭一行標記＋所稱軌道×檔路徑相符）／授權判定（憲法 §III.1 檔面收窄＋§III.2 三元組）＋名冊結構斷言（空 ★表以哨兵句守；§III.1 範圍欄反引號 token 集對賬本工具常數、次序不計，不符即 rc 2＝Amendment 須同批重導新增面判定） | pre-commit fork-delta 段＝`base-web` pin bump、本體或憲法 staged 時全掃（源倉在 `example`＝bootstrap 斷言；源倉缺席＝rc 2 fail-loud、hook 不設跳過分支）；`test`＝離線自測、入 bootstrap 名冊 | 憲法 §III（標記字面 `rev6-inline`＋★軌道授權）；哨兵句改形＝002 刀 research R10 |
| `tools/msg-key-gate.py` | msg key 跨端：後端 `rust-api/server/src/error.rs` 之 `MSG_KEYS`（常數表＋常數引用陣列兩段解析）⇔ base-web `src/locales/langs/{en-us,zh-cn,zh-tw}.ts` 各自 `backend: {` 子樹鍵集**逐檔雙向全等**（子樹為封閉集、無白名單；ADR-00017「雙向必恆紅」指整本字典、不指子樹）＋Biz 構造點守衛（`server/src/**/*.rs` 生產區間每處 Biz 構造點〔`AppError::Biz(`／`Self::Biz(`／經 use 匯入之裸 `Biz(`、`::` 與 `(` 間容空白；函式值形亦計、`enum AppError` 變體宣告不計〕須 `Cow::Borrowed(字面｜msg_key::NAME)` 且鍵 ∈ 名冊、動態構造即紅、構造點零處＝比對面為空 rc 2；`#[cfg(test)]` 所附項目排除＝本體形 brace 配對、欄位／variant 形以 `,`／`}` 收界）＋前端 msg 字面消費點名冊（base-web `src/**/*.{ts,vue,tsx}`〔排除 `src/locales/`〕剝註解後之字串字面，恰等於 `MSG_KEYS` 成員或為安全前綴之 wire 形者＝消費點；安全前綴＝`MSG_KEYS` 頂層前綴 − 三檔 locale 頂層鍵、程式現算不寫死；實掃〔檔×鍵×次數〕⇔ 工具內名冊 `FRONTEND_MSG_CONSUMERS` 逐項雙向全等且每鍵 ∈ `MSG_KEYS`，不等即紅指名檔:行、掃描根缺席或零源檔＝比對面為空 rc 2） | pre-commit msg-key-gate 段＝`rust-api` **或** `base-web` pin bump、本體 staged 時 `check`（雙側觸發、比對面＝兩側工作樹；「兩側須同一顆外層 commit 同 bump」＝跨子庫同步律之紀律面，本閘讀不到 pin 樹、非其守備範圍；該律之粗判＝pre-commit submodule-sync 段、非碼面閘、不入本表）；零 docker、無環境跳過分支；rc 1 鍵集不等、動態構造或前端消費點與名冊不等、rc 2 結構異常（檔缺席／節缺席／名冊解析失敗／比對面為空）；`test`＝離線自測（契約案＋判準補強案＋真 repo 左源綠案＋斷言 3 案；案數以 `test` 輸出為準）、入 for 自測迴圈與 bootstrap 名冊 | ADR-00039（續行 ADR-00029 之閘形制：逐檔雙向全等、無白名單、Biz 守衛兩形；譯文之家＝三檔 locale 各自的 backend 子樹；承 ADR-00017 決定 3 兌現、rev5:Lint24 翻案為逐檔雙向） |
| `tools/view-render-guard.py` | 管理頁零原始 HTML 注入寫法：`base-web/src/views/manage/**` 之 `.vue`／`.ts`／`.tsx`／`.js`／`.jsx` 逐行比對被禁字面（Vue 模板之原始 HTML 指令、DOM `innerHTML`／`outerHTML`／`insertAdjacentHTML`、`document.write`／`writeln`；不分註解與碼、不解析語法＝射程內連註解都不得寫出被禁字面）；自由文字欄（IP 規則備註為首例）一律純文字插值（`specs/004-ip-trust-anchor/spec.md` FR-052） | pre-commit view-render-guard 段＝`base-web` pin bump 或本體 staged 時 `check`；零 docker、hook 段零條件判斷不設跳過分支（ADR-00019 決定 3／4）；base-web 工作樹缺席、射程目錄缺席或零受掃檔＝工具 rc 2 fail-loud（掃描面為空不算綠）；命中＝rc 1 指名檔:行；本體 staged 時自測 | ADR-00034（§III.2 `★BASE-WEB-MANAGE-PAGE-WIRING` 進場；閘契約＝docs/ops/reference-src/code-gate-contracts.md §3①） |
| `tools/route-artifact-gate.py` | 路由外掛產物檔（`src/router/elegant/{imports,routes,transform}.ts`＋`src/typings/elegant-router.d.ts`）之產物檔紀律三道斷言：①空沙盒觀測之外掛實產出集＝`base-web/src` 帶產物檔頭之檔集＝憲法 §III.2 `★BASE-WEB-MANAGE-PAGE-WIRING` (i) 列範圍欄「（產物檔 N 支）」注記所轄路徑集（解析＝`tools/fork-delta-lint.py` 之 `load_roster` 與其同一支範圍欄展開器；雙向差集即紅——漏列一支〔該支無授權亦無守〕與幽靈宣告一支〔授權射程虛胖〕皆紅，注記自稱支數與該組路徑數不符亦紅）②工作樹為種重算冪等（view 樹變了而產物沒跟上即紅）③上游基線 `fork260509-soybean-admin-base/` 為種重算＝工作樹（外掛對 `routes.ts` 走增量合併、工作樹為種時手改行存活——「手改一行即紅」由本道承擔）；重算一律 base-web 容器內 `/tmp` 沙盒、對工作樹唯讀、外掛設定取現行 `build/plugins/router.ts` 不重抄 | pre-commit route-artifact-gate 段＝`base-web` pin bump、本體或憲法 staged 時 `check`；docker 不在 PATH／compose 兩檔缺／`base-web` 容器未起＝具名跳過 rc 0；容器在而重算失敗、外掛零產出、憲法列或基線種子不完整＝rc 2；基線源倉缺席＝只③具名跳過並警告；任一道不通過＝rc 1 附 diff；本體 staged 時自測 | ADR-00034（§III.2 該列之產物檔紀律與「本列產物檔集＝外掛實際產出檔集」斷言）；ADR-00019（容器依賴型碼面閘之環境缺席語意） |

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


## 12c. 事件寫錯了怎麼辦（erratum 更正機制）

`docs/ops/events.jsonl` 是 **append 型單一事實源：既有列永不改**。寫錯不回頭編輯，改為 append 一筆 `erratum` 事件；人讀面（MILESTONES／STATE／DECISIONS-INDEX／perf）吃的是套用更正後的視圖。

★機器守＝GT-02 的 HEAD 對比腿：HEAD 版須為現版的**逐行前綴**，改寫／刪列／疑中間插入三態各自指名行號（BL-00035②）。紀律兩句：
- **一律尾端 append、不按日期插入**——遲到的 `close_bookkeeping` perf 事件亦然；插入會讓其後所有 `erratum` 的 `target_line` 整體位移。
- 已 commit 的列寫錯、而該顆**尚未推送**：`git reset --soft HEAD^` 後改再 commit；`git commit --amend` 會以被改寫的那顆為基準、本腿恆紅，`--no-verify` 為 CLAUDE.md §6 硬禁令。

- **可更正欄**（`ERRATUM_FIELDS`）：`merge`／`pins.web`／`pins.api`／`commit`／`adrs`／`probe`。前四者之 `corrected` 須為 40 位 hex SHA；`adrs` 須為 `ADR-NNNNN` 字串 list；`probe` 須為完整欄物件（形檢同 GT-02）。
- **不可更正欄**：`summary`／`reason`／`notes` 等自由文字——寫錯只能在後續事件的 notes 說明，故落帳前務必看過一遍。
- **形**：`{"type":"erratum","date":"YYYY-MM-DD","target_line":<events.jsonl 行號>,"field":"<欄>","corrected":<新值>,"reason":"<單行理由>"}`；`target_line` 指向被更正那一列的行號。
- **ID 家族的家不同**：ADR 的家是 `docs/arc42/decisions/` 檔案本身（accepted 後不可變、永久留存），故**不設**「誕生必帶事件」的反向不變式（ADR-00025）；BL 反之——完成即刪列（RL-0050），離了事件就無處可查，故其誕生必帶某筆事件的 `backlog_add`（GT-03 反向腿）。
- ★與 `python3 tools/docsync errata <詞>` **不是同一件事**：後者是跨檔假述枚舉工具（RL-0001），用於改字面後掃全 repo 殘留；本節講的是事件帳的更正機制。檢索「勘誤」二字時請先分辨要的是哪一個。

## 13. 故障排除速查

索引→`docs/ops/LESSONS.md`、全文→`docs/ops/LESSONS/`；本表只指路。前代候選＝rev5 `docs/ops/LESSONS.md`（唯讀、引用帶 `rev5:`）。

症狀「回應 403」的分診（只給座標、事實住活書）：`5003` 的發出面與彼此在 wire 上不可分辨＝活書 §8.2；IP 存取閘阻擋的可觀測面（豁免路徑、`ipgate_blocked_total`、`security.ipgate` 阻擋告警之命中網段欄）＝活書 §6.1「信任錨與 IP 存取閘——島 F」④；登入端點轉發鏈逾限拒絕（落一列 `chain_rejected` 登入稽核）＝同情境②。★Grafana `ipgate-degraded` 只看降級事件、不涵蓋阻擋（阻擋告警不帶 `degraded` 欄）——告警沒響不等於不是閘擋的。誤擋的解法＝IP 規則管理頁改規則（不重啟即生效）——★該改動若涵蓋操作者自身來源會被**防自鎖**當場拒絕（`2222`／`biz.ipRule.selfLock`、規則列與稽核列皆零寫入）、須改自其他來源操作或改建不涵蓋自身之規則，事實＝活書 §6.1「信任錨與 IP 存取閘——島 F」⑤ 與 §12「防自鎖」列；來源被登入節流鎖住＝§9 管理員解鎖。

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

prod 不入 roadmap（rev6 尚未自立拍板、暫承 rev5:ADR 0014 為預設；若要做 prod 先立 ADR）。本章＝把系統放到「前面有反向代理或 CDN」的環境時，信任錨與 IP 存取閘這一面要逐項確認的清單——是文件、不是 prod 設定檔。樣例一律以 dev 實際掛載、實跑過的那一份（`deploy/trust-model.dev.toml`）為基底；章內命令皆在 rev6 dev stack 實跑過。六集合語意、載入失敗語意、反向代理標頭契約與 prod 樣例的權威＝`docs/ops/reference-src/trust-model-config.md`，本章只寫操作、不重抄。

### 16.1 信任模型設定檔

1. **掛載**：環境變數 `APP_TRUST_MODEL_PATH` 指向一份 TOML；rust-api 啟動時載入一次、之後唯讀共享——改檔後要重啟 rust-api 才生效。dev 現況＝`docker-compose.dev.yml` 把 `deploy/trust-model.dev.toml` 唯讀掛到容器內 `/etc/rev6/trust-model.toml`，環境變數值與掛載目標共用同一個 YAML anchor（兩者不會分岔）。
2. **由 dev 那份擴充**（prod 樣例＝上述 contracts 檔「prod 樣例」節）：
   - `internal_default`＝我方內網／容器網段。反向代理連到 rust-api 的來源位址必須落在受信集（六集合聯集）內、慣例就放這一項；對端不受信時，**位址推導**在第一層對端閘就結案＝直取對端、來源信心 `direct`，轉發鏈與兩個覆蓋層都不參與（兩覆蓋各自的對端前置集同樣在那個聯集內）。唯溢出短路不看對端受不受信、一律套在最後：鏈的原始非空欄數逾上界者來源信心改 `chain_rejected`，登入端點據此拒絕（`5003`／HTTP 403、另落一列登入稽核），其餘端點帶著標記照常服務（管線全序＝活書 §6.1「信任錨與 IP 存取閘——島 F」情境②）。
   - 前置 CDN 者另填 `[[cdn]]`（`networks`＋`connecting_ip_header`）與 `cf_gate_egress`（掛邊緣驗證閘的我方出口；缺它則邊緣驗證標記不被採信、信心升不到 `cdn_verified`）。
   - `[tunnel]`／`[[my_public]]`／`[[bindings]]` 依實際拓樸填；用不到就不宣告（缺鍵＝空集、沒有隱含的寬鬆預設）。
   - 網段一律寫裸 IPv4／IPv6 字面；IPv4-mapped 形（`::ffff:` 起首）會讓該集合整個被清空並記 `trust_model_set_cleared`。
3. **載入失敗不擋啟動**：路徑未設或讀不到、整體解析失敗、單一集合含壞網段，三種情形都只縮小受信集、服務照常起來（逐情形行為＝contracts 檔「載入失敗語意」節）。「服務起得來」因此不代表設定有生效——每次部署或改檔後跑第 4 步。
4. **驗收**（四條皆唯讀）：

   ```sh
   # ①容器內讀到的就是 repo 那一份（rc 0＝逐位元相同；其他環境把右側換成該環境的設定檔）
   docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cat /etc/rev6/trust-model.toml | diff - deploy/trust-model.dev.toml
   # ②載入總結行：讀的是哪份檔、各集合的受信網段數、本次啟動的載入告警筆數
   docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --no-log-prefix rust-api 2>&1 | grep '信任模型載入完成' | tail -1
   # ③載入告警行數：期望印出 0
   docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --no-log-prefix rust-api 2>&1 | grep -c '信任模型載入告警'
   # ④IP 域降級計數：各格期望皆 0（值集以 rust-api/server/src/obs.rs 之 IP_DOMAIN_DEGRADED_SOURCES 為準）
   curl -s http://127.0.0.1:32079/metrics | grep '^ip_domain_degraded_total'
   ```

   dev 實得（②之欄位段）：`"trust_model_path":"/etc/rev6/trust-model.toml","warnings":0,"internal_default":1,"tunnel":0,"cf_gate_egress":0,"cdn":0,"my_public":0,"bindings_internal":0`。
   - ②各集合欄報的是**受信網段數**、不是條目數；`trust_model_path` 印「(未設定)」＝環境變數沒掛上。
   - ②的 `warnings` 含兩類不算降級的告警（設定檔有不認得的鍵、載入完成但零受信網段）；這兩類不進④的計數，所以④全 0 不等於零告警——以②③為準，非 0 時逐行讀③命中行的 `kind`／`scope`／`reason` 欄。
   - ③看印出的數、不看 rc：`grep -c` 零命中時印 `0` 而 rc 為 1。③橫跨容器 log 內歷次啟動；只看最近一段就在 `logs` 後加 `--since <時間>`（如 `--since 24h`）。
   - 告警規則 `ipgate-degraded`（`deploy/grafana-provisioning/alerting/rules.yml`）也涵蓋載入降級，但啟動端事件每次啟動只發一次、紅一個評估窗即復歸——部署當下以②③④為準、不等告警。
5. **dev 的分界**：dev 只宣告 `internal_default`，經反向代理端到端可達的只有來源信心態 `fallback` 與 `proxy_clean` 二態，其餘信心態由整合測試覆蓋（已知態＝ADR-00040）（★as-built 對沖＝BL-00125：`chain_rejected` 不依賴信任模型、經反向代理送逾上界轉發鏈即端到端可達，實為三態；ADR-00040 款 2 之「二態」為該刀當時枚舉、body 不可變故以 BACKLOG 對沖）。要在 dev 追加可達態＝加設定、不改判定碼。★dev-only 邊界：`internal_default` 取 docker 橋接的上位段，docker 閘道位址也落在其內——經 rust-api 直連埠（只綁 `127.0.0.1`）打進來的請求其對端受信、`X-Forwarded-For` 會被採信，來源位址由請求端指定（走查與整合測試正是靠這條路構造來源；2026-09-20 實測落列 `proxy_clean`、對端＝docker 閘道位址）。prod 的 `internal_default` 不得涵蓋任何可由外部直達 API 埠的位址、且 API 埠不對外。

### 16.2 CDN 邊緣網段：兩處各存一份、必須同步更新

| 落點 | 拿它判什麼 | 填法 |
|---|---|---|
| `deploy/nginx/nginx.conf` 的 `geo $cf_edge` 區塊 | **傳輸層對端**是不是 CDN 邊緣——決定 `X-CF-Verified`／`CF-Connecting-IP` 兩標頭注入還是移除 | 每個網段一行 `<CIDR> 1;`（區塊內附註解樣例）；dev 留空 |
| 信任模型檔 `[[cdn]]` 的 `networks` | **轉發鏈裡**哪一跳是 CDN 邊緣（位置錨） | CIDR 字串陣列；`connecting_ip_header` 填該 CDN 的訪客位址標頭名 |

- ★訪客位址標頭（信任模型 `[[cdn]]`／`[tunnel]` 的 `connecting_ip_header`）的前置層義務：該名 MUST 由前置層**無條件覆寫或移除**——`deploy/nginx/conf.d/_locations.inc` 只對固定一組標頭名 `proxy_set_header`（含預設的 `CF-Connecting-IP`），宣告成別的名字而 nginx 沒有同步為它加一行（非 CDN／非通道流量給空值＝移除）時，請求端可自帶該標頭原樣穿透：`[[cdn]]` 側扭曲來源信心，`[tunnel]` 側在通道回退成立時直接改寫真實來源（連帶影響存取閘判定、來源維計數桶與稽核列）。另該名須為合法 HTTP 標頭名——非法名使兩層覆蓋靜默失效、載入面現無告警（承載＝BACKLOG BL-00082）。
- 兩份用途不同、內容必須一致。來源＝CDN 供應商公告的邊緣網段表（Cloudflare＝`https://www.cloudflare.com/ips/`，IPv4 與 IPv6 兩份都要）；它是部署參數、會變——**更新節奏跟供應商公告走**，每次變更**兩處同一批改**，改完 nginx 重載設定、rust-api 重啟（信任模型只在啟動時載入）。
- ★只改一邊的表徵：
  - 只改 nginx、漏改信任模型：新邊緣位址在轉發鏈上不被認得是 CDN、被當成真實來源（多個訪客塌成同一個邊緣位址）；同時邊緣驗證標記為真、訪客標頭與它對不上 ⇒ 來源信心大量落 `cdn_mismatch`（前提＝`cf_gate_egress` 已填）。
  - 只改信任模型、漏改 nginx：兩標頭被 nginx 移除 ⇒ 位置錨照常成立，但信心停在 `cdn_anchored`、升不到 `cdn_verified`。
- 查來源信心分布（唯讀；登入稽核表）：

  ```sh
  docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres psql -U soybean -d soybean_admin_rust -At -c "SELECT ip_confidence, count(*) FROM sys_login_attempt GROUP BY 1 ORDER BY 2 DESC;"
  ```

- dev 兩處皆為空集：nginx 恆移除那兩個標頭 ⇒ `cdn_verified`／`cdn_mismatch` 在 dev 經反向代理到不了（同 16.1 第 5 點）。

### 16.3 鎖定來源站只收 CDN 邊緣連線——縱深防禦建議

- 前置 CDN 時，建議在來源站的網路層（防火牆／安全群組／CDN 專屬通道）只接受 CDN 邊緣網段的連線，縮小直達來源站的攻擊面。
- ★它是建議、不是來源還原正確性的前提：位置錨的成立條件已入碼（憲法 §I.7 島 F 之 F6；ADR-00034）——錨的右鄰起、直到傳輸層對端，每一跳都得是受信基建，否則棄錨、改取最右的不受信跳。有人繞過 CDN 直連來源站、在轉發鏈自填「偽造位址, CDN 邊緣位址」時，還原出來的是他自己的位址，不是偽造的那個。
- 漏做這一項時，本系統的來源還原不因此失真；文件約束沒有機器面、漏做零訊號，所以不把安全宣稱壓在它上面。

### 16.4 其餘 prod 遞延項（只留指針）

| 項 | 去處 |
|---|---|
| 登入頁三顆快速登入鈕與表單預填密碼把 dev seed 帳密帶進前端——★轉 prod 前必須拆除 | 滯後卷 BL-00049（拍板＝ADR-00030） |
| redis 持久化 | 維持不開（已知態＝ADR-00040） |
| 機密輪替與 prod 值 | §7、§15 |
