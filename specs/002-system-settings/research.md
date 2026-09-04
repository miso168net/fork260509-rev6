# Research — 002-system-settings（Phase 0）

> 輸入：spec（clarify Q1～Q5 定案）＋brainstorm §3／§11＋`rev5:002-system-settings` research（R1～R11 形）；每題 Decision／Rationale／Alternatives。
> CLAUDE.md §2 要求兩件必列：R2 rev5 對應碼清單、R3 rev6 拍板差異點（承 rev5:ADR 0019 形）；RL-0013：棄案反例回跑＝R13。

## R1 web 框架與依賴選型（雙源對照：rev5 lockfile vs crates.io 最新穩定版；user 拍板 2026-09-05）

- **Decision**: axum 0.8.9（沿 rev5 已驗證組合）；ORM sea-orm 1.1.20、casbin 2.20.0＋vendored sea-orm-adapter、tokio 1.53.1（001 已在、三源拍板不動）。新進十支逐筆雙源對照——九支同值直採、一支分歧（jsonschema）user 拍板取最新穩定版。
- **Rationale**: rev5 全棧以 axum 為底（RouteDef 註冊表／enforce 中介層／oneshot 測試形）、參照面最小；版本組合經 rev5 002～008 七刀實戰驗證；分歧取最新穩定＝001／rev5 同型拍板先例。
- **Alternatives considered**: actix-web／poem——參照面歸零、全部設計重推、無收益；jsonschema 沿 rev5 0.49.6——重打字摩擦最小但距最新三個 minor、日後再升一次維護批（棄）。

| crate | rev5 lock | crates.io 最新穩定（2026-09-05 查） | 落地 | 用途 |
|---|---|---|---|---|
| axum | 0.8.9 | 0.8.9 | 0.8.9 | HTTP 框架 |
| serde | 1.0.229 | 1.0.229 | 1.0.229（rev6 lock 已在） | derive |
| serde_json | 1.0.151 | 1.0.151 | 1.0.151（rev6 lock 已在） | 信封 json |
| tracing | 0.1.44 | 0.1.44 | 0.1.44（rev6 lock 已在） | 結構化 log |
| tracing-subscriber | 0.3.23 | 0.3.23 | 0.3.23 | env-filter＋json |
| tower | 0.5.3 | 0.5.3 | 0.5.3 | dev-dep（oneshot） |
| metrics | 0.24.6 | 0.24.6 | 0.24.6 | counter 面 |
| metrics-exporter-prometheus | 0.18.3 | 0.18.3 | 0.18.3（default-features = false） | recorder＋render |
| axum-prometheus | 0.10.1 | 0.10.1 | 0.10.1（要求 tokio ^1.53、rev6 已釘 1.53.1 實值＝相容） | axum_http_* 三序列 |
| jsonschema | 0.49.6 | **0.53.0** | **0.53.0**（★分歧、user 拍板取最新；dev-dep、`default-features = false` 不拖 HTTP client 鏈） | draft-07 契約裁判 |

★jsonschema 守則：0.50+ 若改了 validator 建構或錯誤迭代 API，U3 實作者照新 API 寫裁判（rev5 `wire_schema.rs` 只當藍本）；若新版對 draft-07 快照之 null 聯合型判定與 rev5 實證不同→停手升 user（不得以豁免欄位繞過）。
版本單一來源＝`rust-api/Cargo.toml` workspace.dependencies；server 成員側逐項開恰需 features（比照 rev5 server Cargo.toml 註解、重寫）。**明確不進**（rev5 有、本刀域外）：jsonwebtoken／redis／argon2／captcha／sha2／hex／lettre／toml／arc-swap／once_cell／futures-util／xdb。

## R2 rev5 對應碼清單（實作單元動工前逐檔先讀；rev5 rust-api 002 終態 pin＝fce6542、凍結 worktree 現為 92919b9 終態——先讀 002 終態、再看終態差異）

| rev5 檔（`../fork260509-rev5/rust-api/`） | rev6 對應 | 處置（重打字＋註解 rev6 語境；rev5 出處帶 `rev5:`） |
|---|---|---|
| `server/Cargo.toml`／根 `Cargo.toml` members | 同路徑 | R1 依賴子集、features 逐項重寫註解；members += server |
| `server/src/main.rs`＋`lib.rs` | 同 | boot 鏈：config→db→init_enforcer→router build→serve（含 `into_make_service_with_connect_info` 形）；tracing-subscriber json |
| `server/src/router.rs` | 同 | RouteDef 六欄＋Protection 三態；ROUTES 恰四；★加 method-not-allowed fallback 同 4040（R3-4）；字面形守 docsync 生成器契約 |
| `server/src/state.rs` | 同 | AppState 恰 {db, enforcer} |
| `server/src/envelope.rs` | 同 | Res 三欄宣告序＋2^53 守衛＋serialize_i64_as_string；PageRes 不搬 |
| `server/src/error.rs` | 同 | 13 碼常量全列、AppError 六變體；★加 msg key 名冊常數（R3-2） |
| `server/src/config.rs` | 同 | `APP_DATABASE_URL[_FILE]` 讀取；其餘 compose 鍵接而不讀 |
| `server/src/obs.rs` | 同 | recorder＋render＋axum-prometheus layer |
| `server/src/auth/enforce.rs`＋`mod.rs` | 同 | MODEL_CONF／init_enforcer／enforce_role_path_method 單一純函式／require_policy DB-fresh／空 no-escalation 掛點；denylist／reload 不搬 |
| `server/src/auth/dev_identity.rs` | 同 | `cfg(debug_assertions)` 三 token 查表；Identity 注入形 |
| `server/src/request_context.rs` | 同 | seam 介面位空殼 |
| `server/src/validation.rs` | 同 | registry 16 鍵＋NUMBER_RANGES＋canonical；★加 registry 一致性守衛入口（R3-1） |
| `server/src/handler/system_settings.rs`＋`mod.rs` | 同 | SettingItem／UpdateReq 三態／兩 handler＋mod tests（真 DB oneshot 形、RAII 還原守衛） |
| `server/src/model/facade/system_settings.rs`／`sys_user_role.rs`／`mod.rs`、`model/mod.rs` | 同 | find_all／find_by_key／update_by_key（含 build_update_active_model 純測 seam）；roles_of_user 兩濾網 |
| `server/tests/common/mod.rs`、`health.rs`、`contract.rs`、`wire_schema.rs` | 同 | oneshot 契約形＋case registry 雙向覆蓋閘＋快照裁判（★jsonschema 0.53 API）；★加 fallback 兩案＋msg 名冊雙向案 |
| `server/tests/entity_access_lint.rs` | 同 | handler 零 `entity::` 機器強制（rev5 終態＝排除制掃描面＋結構斷言、非數量等式——沿終態形） |
| `server/tests/entity_behavior_lint.rs`（rev5 終態 325 行、strip 引擎在 tests/common） | 同 | BL-00008 錨；等式形站點數＋合成正例 |
| `server/tests/fixtures/wire-schema.json` | 同 | 由 `wire-schema.py extract` 首抽產、不手寫 |
| rev5 `tools/rust-fmt-gate.py`／`wire-schema.py`／`fork-delta-lint.py` | 同名隨遷 | 隨遷工具紀律（逐字允許；四型失效引用 rev6 化；fork-delta 結構斷言改形＝R10） |
| rev5 base-web `src/typings/api/rev5-settings.d.ts`／`src/service/api/rev5-settings.ts`（pin 5089c28） | `rev6-settings.d.ts`／`rev6-settings.ts` | 形沿用、註解 rev6 語境、標記 token `rev6-inline` |
| rev5 `tools/docs-sync.py` 之 `parse_router_routes`／gen.router | `tools/docsync/references.py` 新生成器 | 解析窄假設沿用、rev6 docsync 模組形重寫（R9） |

rev5 `specs/002-system-settings/` 全套＝設計語境參考（唯讀）；rev5:ADR 0022／0023 結論轉錄為 rev6 ADR。

## R3 rev6 拍板差異點清單（相對 rev5 002；防回歸執行面——實作單元 prompt 烤入；rev5 research R3 的十三筆 rev4→rev5 翻案一併視為已翻案、不得帶回）

1. **已知鍵型別與 registry 不一致→`5000`**（clarify Q1；rev5 只對未知字面 fail-loud）——讀寫觸及皆同、不跳列。
2. **msg key 後端側名冊閉環**（brainstorm Q4；rev5 為 zh-tw.ts＋Lint24 跨端閉環）——error.rs 單一名冊＋contract 雙向斷言；base-web locales 零改動；跨端閘 BACKLOG。
3. **寫端成功 `data:null`**（clarify Q3）——與 rev5 同形、但 rev6 明文為契約（非默認）。
4. **方法不符→`4040` 信封**（clarify Q4；rev5 為框架 405 無信封）——router `method_not_allowed_fallback` 與未註冊路徑同一函式。
5. **讀端 description NULL 缺席**（clarify Q2）——與 rev5 同形、明文為契約；讀端型別不含 null、寫端型別含 null。
6. **fork-delta-lint 隨本刀進場＋結構斷言容空 ★表**（brainstorm Q5；rev5 創世已有、斷言 ≥4 列）。
7. **entity-drift 快照缺席即紅**（brainstorm Q2；rev5 為具名跳過）。
8. **容器依賴型碼面閘環境缺席＝具名跳過、rev6 自立 ADR**（clarify Q5；承 rev5:ADR 0057 決定 3 形）。
9. **routes 真表由 docsync 新生成器產**（rev5 在 docs-sync.py 內建＋gen.router Day-1 豁免；rev6 無 Day-1 豁免、U1 隨 router.rs 同批落）。
10. **碼面閘名冊住 RUNBOOK §12 表＋GT-12 腿；「碼面閘」入名詞段**（brainstorm Q3／Q8；rev5 無名冊）。
11. **前端新檔前綴 `rev6-`、token `rev6-inline`**；**無 zh-tw.ts、無 gen.msg_dict 豁免、無 rev5:B-028 型量測、無 K1 盤點**；quickstart curl 範例之 dev token 以 shell 變數執行期串接、零 `.gitleaks.toml` allowlist（RL-0054 精神；rev5 為 allowlist 放行 `curl-auth-header`）。
12. **jsonschema 0.53.0**（rev5 0.49.6；user 拍板）；tokio 直釘 1.53.1 實值（rev5 manifest 寫下界 1.52.3）。
13. **`.env` route mode 不翻**（brainstorm Q7；與 rev5 002 同、明文）；**`sys_user_role` FK Relation 不入本刀**（001 已在；rev5 為本刀 T028）。
14. **跨鍵不變式不驗**（brainstorm Q6；與 rev5 同形、明文＋BACKLOG）。
15. **ADR 六筆、憲法零 Amendment**（rev5 四筆 0020～0023）。

## R4 registry 值域（→data-model §3 凍結）

NUMBER_RANGES 10 鍵逐鍵界＝rev5 定稿原值承襲（rev5 自 rev4 五刀漸進定界、已驗證）；enum:on,off 6 鍵值域自含於 setting_type 字面。canonical：number＝`trim`→`parse::<i64>`→界內→`to_string()`（棄空白／前導零／正號；小數、溢位、非數值拒）；enum＝精確成員、原值即 canonical、大小寫敏感。

## R5 契約機器化管線（本刀＝憲法 §I.3 wire 地基刀）

- **Decision**: 三件形——①`tools/wire-schema.py` 隨遷（extract／check --staged-gate／test；glob 零改、TSJS 0.67.4、`--strictNullChecks`）②`server/tests/wire_schema.rs`（jsonschema 0.53.0 對快照 definitions 建 validator、驗 DTO 序列化輸出）③`server/tests/contract.rs` case registry＋雙向覆蓋閘＋fallback 兩案＋msg 名冊雙向案。
- **Rationale**: 「容器內抽」語意 rev5 實證＝npx 一次性、不碰工作樹、輸出 byte 確定；覆蓋閘＝cargo test 形（spec FR-018）；`--strictNullChecks` 為 rev5 已修的 rev4 缺陷（不帶則 null 聯合型被吃、快照低報）——本刀直接承 rev5 終態旗標。
- **Alternatives considered**: host 直跑 tsc——host 無 node 工具鏈（node 住 base-web 容器）、棄；快照放外層 repo——契約裁判與消費者同住 rust-api 才能單庫自證、棄。

## R6 觀測面三件（工程自拍、回報備查）

rev6 compose `metrics` profile 之 prometheus 刮取 `rust-api:8080/metrics`（`deploy/prometheus/prometheus.yml` 既設 target）；`/metrics` 為憲法例外集成員、本刀必掛。拍板：recorder＋render（metrics-exporter-prometheus、default off、由 axum route 吐）＋axum-prometheus layer（axum_http_* 三序列；最外側、量到 fallback 404）。`/health`＝plain text "ok"；front-nginx healthcheck 打 nginx 自答塊、不轉發；驗收＝dev 直連埠 32079 直打。

## R7 測試分層（沿 rev5 實形；容器內 serial）

1. **純函式單元測**（免 DB）：registry 紅綠矩陣（含型別一致性守衛）、error 碼映射、build_update_active_model 欄映射（now 注入純測 seam）、三態 deserialize 三形。
2. **oneshot 契約測**（免 DB、tests/ crate）：case registry 全 route（未認證 8888 形、信封例外形）＋快照裁判＋覆蓋閘＋fallback 兩案（未註冊路徑／方法不符→4040）＋msg 名冊雙向＋entity_access_lint＋entity_behavior_lint。
3. **真 DB integration**（handler `mod tests` 形、`Database::connect(db_url)`＋real_app oneshot）：授權矩陣（uid 1／2／3＋未認證×兩端點）、寫端往返（含同值更新）、驗證失敗零寫入、三態落庫效果（含空字串）、型別不一致 5000（以測試中改列後 RAII 還原）；★寫測試掛 panic-safe RAII 還原守衛（rev5 002 收刀坑）。

## R8 dev-only 測試態身分

- **Decision**: 固定 token 查表 `dev-super`→uid 1／`dev-admin`→uid 2／`dev-user`→uid 3；roles 不入表；驗證器整體 `#[cfg(debug_assertions)]`；`Authorization: Bearer <token>` 形、剝前綴 trim 後查表；release 建置＝驗證器缺席、一切 Policy 請求 8888。
- **Rationale**: 零密碼學、003 僅換驗證器內部；debug_assertions＝零新 feature flag、編譯期可證。
- **Alternatives considered**: cargo feature flag（需 compose build args 配合）；env 開關（runtime 可誤開）——皆棄。

## R9 docsync routes 生成器（rev6 新）

- **Decision**: `tools/docsync/references.py` 加 `parse_router_routes(text)`＋`gen_reference_routes(ctx)`；掛 GENERATED_FILES（14→15）；解析窄假設＝data-model §4；來源缺席或偏離即 raise（generate 非零）。
- **Rationale**: rev5 docs-sync 已證明「窄假設字面契約」可維持三年零漂移；rev6 docsync 為模組化 package、生成器各自一函式＋一測試即入名冊；不設 Day-1 豁免（U1 與 router.rs 同批落、生成器永不對空源）。
- **Alternatives considered**: 由 cargo test 產表再 commit（工具鏈跨語言、pre-commit 需容器、棄）；手寫 routes 表（違 RL-0049 鏡像不存在、棄）。

## R10 fork-delta-lint 結構斷言改形（brainstorm Q5）

- **Decision**: `load_roster` 對 §III.2 ★段：零資料列時必命中憲法哨兵句「（空表——尚無 ★ 軌道；首列隨首刀 Amendment 落入。）」、否則 ≥1 列；§III.1 恰 3 列與其餘斷言不變；self-test 加「零列＋無哨兵句＝紅」一案；§III.1 表頭 `| 軌道 | 範圍 | 紀律 |`、§III.2 表頭 `| 軌道 | 用途 | 範圍（檔案） | 紀律 |` 皆與 rev5 同、解析器零改。
- **Rationale**: rev5 的「≥4 列」是防名冊被無聲移除；rev6 空 ★表是憲法明寫的合法態，哨兵句就是「表為空是刻意的」證據，守的目的（無聲移除即紅）不變。
- **Alternatives considered**: 零列即略過（fail-open、與 Q2 方向相反）；把 ≥4 改 ≥0（守消失）——皆棄。

## R11 併發語意（spec Assumptions 指派項）

`update_by_key`＝單鍵原子 UPDATE、無樂觀鎖、last-write-wins（updated_at 非版本欄）；同值更新照寫審計欄；16 鍵低頻治理面、單管理者情境；本刀不驗併發、U8 DoD 記帳。

## R12 執行單元切法（→tasks 展開；CLAUDE.md §2 Workflow 六件套、每單元 pin bump、rust 全程容器內 serial）

| 單元 | 內容 | 允許檔案面（fix prompt 種子） | 前置 |
|---|---|---|---|
| 主線直改 | RULES 名詞段「碼面閘」＋RULES-VERSION bump＋generate | docs/ops/RULES.md、tools/orchestration/_sk_rules.js、docs/generated | U0 派發前 |
| U0 治理組合拳 | 三支閘隨遷（fork-delta 斷言改形＋self-test）＋pre-commit 六處＋失準修單 errata＋RUNBOOK §12 碼面閘表＋GT-12 腿＋test_gates＋README 樹＋bootstrap 自測名冊＋hook 演練 | tools/{rust-fmt-gate,wire-schema,fork-delta-lint}.py、.githooks/pre-commit、README.md、docs/ops/RUNBOOK.md、tools/docsync/gates.py、tools/docsync/tests/test_gates.py、tools/bootstrap.sh、docs/process 兩檔（掃後定） | 名詞段已落 |
| U1 server 基座 | Cargo member＋R1 依賴＋envelope／error（含 msg 名冊）／config／state／obs／router（含 fallback）／main／lib＋health＋contract 骨架＋覆蓋閘＋fallback 兩案＋entity_access_lint＋entity_behavior_lint＋docsync routes 生成器＋GENERATED_FILES／README＋rust-fmt 首跑＋七件起得齊 | rust-api/Cargo.toml、rust-api/server/**、tools/docsync/references.py、tests/test_references.py、README.md | U0 |
| U2 授權與身分 | enforce／dev_identity／request_context／facade sys_user_role＋未認證 8888 case＋授權矩陣骨架 | rust-api/server/src/auth/**、request_context.rs、model/facade/sys_user_role.rs、tests/contract.rs | U1 |
| U3 讀端 US1 | validation registry（含一致性守衛）／facade find_all／handler get／typings 新檔／wire-schema extract 首抽／wire_schema.rs 裁判／get case／16 鍵全等 integration | rust-api/server/src/{validation.rs,handler/**,model/facade/system_settings.rs}、tests/{wire_schema.rs,contract.rs,fixtures/}、base-web/src/typings/api/rev6-settings.d.ts | U2 |
| U4 寫端 US2 | UpdateReq 三態型／facade update_by_key／handler update／service 新檔／update case／往返 integration（含同值） | 同 U3＋base-web/src/service/api/rev6-settings.ts | U3 |
| U5 驗證失敗 US3 | 紅綠矩陣（型別／範圍／enum／未知鍵／缺席壞形／未知型／不一致）零寫入 integration | validation.rs、handler、tests | U4 |
| U6 越權矩陣 US4 | 三身分×兩端點＋角色軟刪停用案＋ADR ②落 | tests、docs/arc42/decisions | U4 |
| U7 三態 US5 | description 四形＋settingValue null 拒收＋ADR ①落 | handler、tests、decisions | U4 |
| U8 收攏 | 活書 §5／§8 as-built、quickstart 走查、DoD 負向自證、ADR ③④⑤⑥落、BACKLOG 兩條、Day-1 三步不適用記載、perf 事件 | docs/arc42/**、docs/ops/**、specs/002-system-settings/quickstart.md | U7 |

冒煙 token 取單元名（如 `u0-govgate`）、不可取 `test`；每 run 不重複 agent ≤24；launch 與 Monitor 同回合原子成對。

## R13 棄案反例回跑（RL-0013：棄案論證寫完回頭對所選方案跑同一反例）

| 拍板 | 棄案被駁的反例 | 對所選方案回跑同一反例 | 結果 |
|---|---|---|---|
| Q1 型別不一致→5000 | 「migration 改了 setting_type 忘同步 registry」→ 棄案 B（不比對）兩邊各自綠、前後端不一致 | A：首次讀寫即 5000、U5 案覆蓋 | 通過；代價＝每鍵一次字串比較 |
| Q4 方法不符→4040 信封 | 「前端錯誤處理只認信封」→ 棄案 A（405 無信封）前端收到非信封 body | B：同 fallback 信封；反例「客戶端想靠 405 分辨方法錯」→ B 以 msg `system.notFound` 足夠、方法錯屬開發期錯誤非運行期分支 | 通過 |
| Q5 環境缺席具名跳過 | 「沒起 stack 就 commit 壞格式碼」→ 棄案 B（擋）令離線不可 commit | A 放行→真防線＝U1 起每單元收尾容器內 `cargo fmt --check`＋pin bump 時 stack 通常在跑；反例殘留＝離線 commit 的壞格式在下次 stack 在時被抓 | 通過（殘留可接受、ADR ⑥記） |
| R1 jsonschema 0.53.0 | 「0.x minor 破 API」→ 棄案 0.49.6 零摩擦 | 0.53.0：實作者照新 API 寫；反例「null 聯合型判定不同」→ 守則＝停手升 user | 通過（有停手線） |
| R9 routes 生成器不設 Day-1 豁免 | 「U0 時 router.rs 不在、generate 對空源紅」→ 若放 U0 需豁免 | 改落 U1 與 router.rs 同批→反例消失 | 通過 |
