# Research — 004-ip-trust-anchor（Phase 0）

> 輸入：spec（clarify Q1～Q3 定案 2026-09-15）＋brainstorm `docs/brainstorms/004-ip-trust-anchor.md`（§0 拍板 BL-00066／BL-00078／Q1～Q7／G1～G7、§5 十項定案、工程判斷 1～13、§3 設計十節、§9 單元骨架）＋`rev5:004-ip-trust-anchor` 全套（spec／plan／research R1～R10／data-model／contracts 四檔／quickstart／tasks；唯讀、凍結 SHA `92919b9`）＋rev5 收刀後動 004 域之十顆 commit（brainstorm §0 G5／工程判斷 7～9）＋rev6 對應碼唯讀勘查（2026-09-15、逐檔行數）＋crates.io 實查（2026-09-15）。每題 Decision／Rationale／Alternatives。
> CLAUDE.md §2 兩件必列：**R2 rev5 對應碼清單**、**R3 rev6 拍板差異點**（承 `rev5:ADR 0019` 形）；RL-0013 棄案反例回跑＝R11。

## R1 依賴釘版與三源核對（全域 §6；brainstorm G7 user 拍板 2026-09-15）

- **Decision**: 三支新進——`arc-swap` **1.9.2**／`futures-util` **0.3.34**（`default-features = false`）／`toml` **1.1.6**；全數字釘版、進 `[workspace.dependencies]`＋`server/Cargo.toml`（沿既有兩層形）。
- **Rationale**: 前兩支三源一致（rev6 `Cargo.lock` 傳遞既有＝rev5 lock＝crates.io 最新）＝同值直採、直接依賴化不動 lock 既有值；`toml` 三源分歧（rev5 1.1.4／crates.io 1.1.6〔2026-09-10〕／rev6 lock 無）→ user 拍板取最新穩定（G7）。零新 redis feature flag：pub/sub 訂閱在既有 `connection-manager`＋`tokio-comp` 下即可用。
- **Alternatives considered**: `toml` 沿 rev5 1.1.4（藍本逐字同版；一進場即釘舊 patch）；省 `futures-util` 改手寫 `poll_fn`（承 rev5 R3 判：規則熱重載路徑上十行難審樣板不值一支已在 lock 圖內的 crate）。

| crate | rev5 釘版 | rev6 lock 現值 | crates.io 最新穩定（2026-09-15） | 落地 | features | 用途 |
|---|---|---|---|---|---|---|
| `arc-swap` | 1.9.2 | 1.9.2（傳遞） | 1.9.2 | **1.9.2** | default | `Arc<ArcSwap<RuleSet>>` 判定面 lock-free 換版 |
| `futures-util` | 0.3.34 | 0.3.34（傳遞） | 0.3.34 | **0.3.34** | `default-features = false`（唯一使用點＝watcher `StreamExt::next()`） | 門鈴訂閱串流 |
| `toml` | 1.1.4 | 不在 lock | 1.1.6+spec-1.1.0 | **1.1.6**（G7） | default | 信任模型設定檔解析 |

**API 守則**（implementer 烤入）：`ipnetwork` 經 `sea_orm::prelude::IpNetwork` 取用、不列直接依賴（rev5 同形）；redis 1.7 之 `Client::get_async_pubsub()` 由 `config::redis_url()` 另開專用 `redis::Client`（多工 `ConnectionManager` 不可用於 SUBSCRIBE）；`toml::from_str::<RawTrustModel>`、未知鍵告警走 `serde(deny_unknown_fields)` 或載入面逐鍵檢（取前者、與 rev5 同）。

## R2 rev5 對應碼清單（實作單元動工前逐檔先讀；rev5 凍結 worktree＝終態、含後刀增量——先看 004 邊界 diff、再看終態）

rev5 004 邊界＝`git -C ../fork260509-rev5/rust-api log --oneline <004 首 commit>..<004 收刀>`（tasks 期以 `rev5:` 收刀 SHA 定界）；★行數為 rev5 **終態**行數（含後刀增量與 inline `#[cfg(test)]`、測試占大半）、只供量級估算。**rev6 facade 住 `rust-api/server/src/model/facade/`（與 rev5 同形、無獨立 model crate）。**

| rev5 檔（`../fork260509-rev5/rust-api/server/`） | 行數 | rev6 對應 | 處置（重打字＋註解 rev6 語境；rev5 出處帶 `rev5:`） |
|---|---:|---|---|
| `src/trust/mod.rs` | 1489 | `src/trust/mod.rs`（新） | `TrustModel` 六集合＋單一 helper（受信集＝跳過集）／`Confidence` 八態＋`as_str` 單一出口／`resolve_client_ip` 三層＋F6 硬化／兩覆蓋／`normalize_xff`（右端取窗→逐欄正規化→丟欄）／`apply_chain_overflow`（F7 標記、`MAX_XFF_TOKENS`）／`ip_bucket` 若在此則搬 throttle |
| `src/config.rs`（信任模型段） | 1343（局部） | `src/config.rs`（擴） | `load_trust_model`＋扁平退路＋`parse_cidr_set`／`clear_warning`（三層失敗語意）＋★`rev5:B-074` IPv4-mapped 網段字面告警＋清集合（`rev5:1193bb9`）；六 getter 既有不動 |
| `src/ipgate/mod.rs` | 1320 | `src/ipgate/mod.rs`（新） | `RuleSet`／`decide` 六步（③④⑤⑥）／`STRUCTURAL_EXEMPT` 六段／`would_self_lock`（同一 `decide`）／`build_ruleset`（未知型 skip＋告警）／`reload_and_publish`（keep-last-good）／`spawn_ipgate_watcher`（專用連線、5s timeout、1s→30s backoff、重連補讀） |
| `src/middleware/mod.rs` | 1284 | `src/middleware/mod.rs`（新） | `request_context_mw`（ConnectInfo＋標頭→純函式→Extension 注入）／`ip_gate_mw`（①②前置＋`decide`→5003）／CF 標頭常數；★`access_log_mw` 不搬 |
| `src/request_context.rs` | 647 | `src/request_context.rs`（換血） | 三欄與取值器不動；`from_trust` 建構點＋`from_headers` 保留為缺席退路（§5 ①）；`peer_ip` 供落欄；模組頭預告回填 |
| `src/handler/ip_rule.rs` | 1883 | `src/handler/ip_rule.rs`（新） | 五支 handler＋`validate_wbip_type`／`normalize_cidr`／`map_mutate_err`／`guard_self_lock`；操作者名**首版即批次讀**（`rev5:6ee82e2` B-106）；`rev5:f841b04` 抽出的 `handler/common.rs` 依 rev6 消費者數判、不預建 |
| `src/handler/throttle.rs` | 1384 | `src/handler/throttle.rs`（新） | `UnlockReq`／`resolve_unlock_target`／`unlock_login`（稽核先於生效）；★rev6 只寫標記、**無** `DEL` 鎖定鍵步（Q7）；★`rev5:be1d7e1` no-escalation 不搬（BL-00048）；Q2＝不查鎖態、一律寫稽核＋標記 |
| `src/throttle/mod.rs` | 2918 | `src/throttle/mod.rs`（重寫 precheck） | 兩維並列合成、L0 顯式 allow 直讀 allow 袋、`ip_bucket`、`parse_unlock_marker`；★rev6 差異＝**無 L1**（刪 `throttle_lock_user_key`／`THROTTLE_LOCK_TTL_SECS`／`lock_ttl_secs`）、兩維 loader 以 registry 界值驗＋整組退、`redis_down` 由標記讀取立；`rev5:007` change_pwd 節流不搬 |
| `src/model/facade/sys_login_attempt.rs` | 1212 | 同（擴） | `count_recent_failures_by_ip`（`real_ip <<= $1::inet`＋GREATEST 恰兩源）；帳號維計數加 `IS DISTINCT FROM 'chain_rejected'`；帳號維查詢本體零改動、標記參數位既有 |
| `src/model/facade/sys_ip_rule.rs` | 1105 | 同（新） | `load_active`／`list`（三篩選＋分頁）／`IpRuleWrite`／四寫端（同交易帶稽核列）／`IpRuleMutateError`（唯一衝突映 conflict） |
| `src/model/facade/sys_operation_log.rs`＋`src/model/audit.rs` | 584＋410 | 同（新） | `AuditEvent`／`AuditOperation`（`rev5:31c1293` 定案形：五字面、單一宣告源、零新 variant）／`AuditOperator`；`write_in_txn`＋單寫 |
| `src/state.rs` | 101 | 同（5→7） | `trust_model: Arc<TrustModel>`／`ip_rules: Arc<ArcSwap<RuleSet>>`；封條改寫（ADR supersede ADR-00027） |
| `src/main.rs`（boot 段） | — | 同（改） | 載信任模型→初載規則集→起 watcher；`into_make_service_with_connect_info` 既在；BL-00072 靜態掃描案 |
| `src/obs.rs` | — | 同（改） | 序列名冊改（data-model §5 為單一權威）；`obs.rs` 測試模組增案＝BL-00070 第七處 |
| `src/cache/mod.rs` | — | 同（改） | 補 `throttle_unlock_user_key`／`throttle_unlock_ip_key`（rev5 形）；**刪** `throttle_lock_user_key` |
| `tests/serve_connect_info_lint.rs` | 345 | `tests/serve_connect_info_lint.rs`（新） | `rev5:B-075`：判別取 `axum::serve` 實參、裸呼與折行反例格、拔線即紅 |
| `src/model/mod.rs`（rev5 守衛群） | 4192（局部） | `src/model/facade/test_kit.rs`（改） | `rev5:55bb3e3` 廢 `SequenceResetGuard`＋水位清理守衛（`SeedOpLogCleanup` 等）形；rev6 對應＝廢除 69 處 `SequenceResetGuard::new()`（10 檔）＋新守衛住 test_kit（§5 ⑨） |
| `tests/contract.rs`／`tests/common/mod.rs`／`tests/wire_schema.rs`／`tests/entity_access_lint.rs` | — | 同（改） | 22 case（case_key 沿 rev5 命名）／`stub_state` 七欄／`Api.IpRule` 裁判 case／三新 facade 入射程 |

| rev5 base-web 檔（`../fork260509-rev5/base-web/src/`） | 行數 | rev6 對應 | 處置 |
|---|---:|---|---|
| `views/manage/ip-rule/index.vue`（HEAD 形＝含 `rev5:1597a671` B-099 修） | 296 | 同路徑（新增型檔頭標記） | 表頭插槽外層 `v-show`＋內層 `v-if`、備註純文字插值、回收桶復原 |
| `views/manage/ip-rule/modules/ip-rule-operate-drawer.vue` | 230 | 同 | 新增／編輯抽屜（類型二值、CIDR 校驗訊息） |
| `views/manage/ip-rule/modules/ip-rule-search.vue` | 95 | 同 | 三篩選 |
| `service/api/rev5-ip-rule.ts` | 91 | `service/api/rev6-ip-rule.ts` | 五支 wrapper（解鎖不建） |
| `typings/api/rev5-ip-rule.d.ts` | 86 | `typings/api/rev6-ip-rule.d.ts` | `Api.IpRule` 節（declaration merging） |
| `locales/langs/{en-us,zh-cn}.ts`（`route['manage_ip-rule']`＋`page.manage.ipRule.*`） | — | 同（新增型圈界） | 新軌道兩樹；`backend.biz.ipRule.*`＋`backend.biz.throttle.*` 六鍵屬既有 (ii) |
| `typings/app.d.ts`（`Schema.page.manage.ipRule` 型節） | — | 同（新增型圈界） | 新軌道；backend 型節六鍵屬既有 (iii) |
| `service/request/index.ts`（`rev5:ae1ac0c9` B-117 塊） | — | 同（新增型圈界擴） | HTTP 層信封 msg 轉譯（Q6）；`translateBackendMsg` 既有 |

| rev5 工具 | 行數 | rev6 對應 | 處置 |
|---|---:|---|---|
| `tools/route-artifact-gate.py` | 605 | `tools/route-artifact-gate.py`（新寫） | 產物四檔重算冪等＋「軌道列產物集＝實產出集」；self-test；四處名冊 |
| `tools/view-render-guard.py` | 282 | `tools/view-render-guard.py`（新寫） | `views/manage/**` 零 `v-html`／`innerHTML`；self-test；四處名冊 |
| `tools/walkthrough-baseline.py`（rev6 既有隨遷工具） | 782 | 同（改） | 還原面擴兩表＋seed 基準模式＋runtime-append 四表序列只比存在性（G6、BL-00075）；自測新案 |

## R3 rev6 拍板差異點清單（相對 rev5 004 終態；防回歸清單 A——implementer prompt 烤入）

| # | rev5 004 行為 | rev6 拍板 | 出處 |
|---|---|---|---|
| R3-1 | 節流兩維各設 redis L1 負快取（`throttle:lock:*`、TTL＝min(窗,900)、命中不續期；FR-028） | **兩維皆無 L1**：每次嘗試讀兩組設定現值＋PG 滑動窗定案；刪鎖鍵族／TTL 常數／兩類 L1 測試／降級源 `redis_lock`・`redis_lock_set`；解鎖端點只寫標記（無 DEL 步） | BL-00066、Q7；spec FR-034 |
| R3-2 | `load_ip_settings` 逐鍵退常數、不判矛盾；兩 loader 只 parse 不驗界 | 兩維 loader **整組**退（缺列／不可解析／**越界**〔registry 宣告界〕／矛盾）＋來源維獨立 label；相等合法（rev5 常數註「恆須嚴格小於」不帶） | Q4、G4；FR-035 |
| R3-3 | `redis_down` 由 L1 GET Err 立 | 由節流步驟①兩維解鎖標記讀取 Err（任一）或 `cache: None` 立；L0 跳過來源維時只憑帳號維那次讀取 | §5 ②；FR-036 |
| R3-4 | msg 譯文權威＝各刀 `contracts/msg-keys.md` | 三檔 locale backend 子樹各為該語譯文之家；本刀 `contracts/` **無** msg-keys.md；憲法 (ii) 權威句改寫；新 ADR supersede ADR-00029（承 ADR-00032 形） | Q3；FR-055 |
| R3-5 | 測試守衛保留序列重設（rev6 003 硬化形拒重設） | **廢除 `SequenceResetGuard`**（69 處／10 檔）；runtime-append 四表序列不復位、各案水位清理；`walkthrough-baseline diff` 四表序列只比存在性 | G6；FR-063／FR-065 |
| R3-6 | 上下文缺席退路＝`from_headers` 空字串形（`rev5:003`）、缺標頭靠 PG INET NN 擋 | 缺席退路承 T048 形但用 rev6 `Err` 兩態：缺 `X-Real-IP`→5000 不落列、在場→轉錄（`fallback`、對端 NULL、判定窗空）；既有 36 處注入測試零改形 | §5 ①；FR-013 |
| R3-7 | `rev5:B-117` HTTP 層信封轉譯屬 006 後維護批 | 本刀提前帶入（`service/request/index.ts` onError 新增型圈界） | Q6；FR-053 |
| R3-8 | `rev5:B-074`／`B-075`／`B-111` 皆 004 收刀後維護批 | B-074＋B-075 自首版即入；B-111 不帶、收刀立 BL | G5；FR-011／FR-014 |
| R3-9 | F7／F8 於 rev5 Phase 9 追加 | 自首版即入（八態、拒絕腿、判定窗轉錄） | 既定不問 2；FR-015～018 |
| R3-10 | 操作者名逐列查（N+1、`rev5:B-106` 後修）；`handler/common.rs` 於第三消費者抽出 | 首版即批次讀；common.rs 依 rev6 消費者數判、不預建 | 工程判斷 9；FR-025 |
| R3-11 | `AuditOperation` 於 005 定案（`rev5:31c1293`） | 首版即定案形（五字面、零新 variant、單一宣告源） | 工程判斷 9；FR-043 |
| R3-12 | 標記 token `rev5-inline`、新檔 `rev5-ip-rule.*` | `rev6-inline`、`rev6-ip-rule.{ts,d.ts}`、刀號 `004-ip-trust-anchor` | 憲法 §III |
| R3-13 | rev5 007 為解鎖加 no-escalation；`Identity` 補 sid（B-140）；改密節流；`access_log_mw`；region GeoIP；HLL | 皆不帶（防回歸清單 B 之 rev6 增列） | brainstorm §1 末列 |
| R3-14 | schema-gate 收窄集本刀加 `sys_operation_log` | 創世已含＝零改；`sys_ip_rule` 刻意不收窄 | 工程判斷 2 |
| R3-15 | 走查工具無 seed 基準模式；restore 只三表 | seed 基準模式＋擴 `sys_ip_rule`／`sys_operation_log`＋序列存在性口徑；rc 沿 0／1／2／64 | §5 ⑤；BL-00075 |
| R3-16 | 契約四檔（含 msg-keys.md、trust-model-config.md） | 契約五檔＝`wire-ip-rule`／`wire-throttle-unlock`／`wire-auth-delta`（三端點增量、基底 specs/003）／`trust-model-config`／`code-gates`（治理契約） | G2、§5 ⑩；FR-044 |
| R3-17 | 解鎖對未鎖標的：DEL 不存在鍵＝no-op、稽核仍寫 | 同語意（不查鎖態、一律寫稽核＋標記） | clarify Q2；FR-041 |
| R3-18 | 阻擋只作用請求層 | 同（明文化：不撤會話、不寫 denylist） | clarify Q1；FR-024 |
| R3-19 | 管理頁對照＝人看截圖 | 結構清單逐項全等、視覺只記不擋 | clarify Q3；SC-010 |
| R3-20 | 依賴 toml 1.1.4 | 1.1.6（G7） | R1 |
| R3-21 | ADR draft 全在 tasks 首單元 | 主 Amendment ADR-00034 draft 於 plan 期落（proposed）；其餘六筆刀內落 | 003 Q5 前例；FR-056 |
| R3-22 | 活書 12 無 `fallback` 撞詞處置 | 來源信心態 `fallback` 與流程層 fallback 區分句 | 工程判斷 11；FR-068 |

**防回歸清單 B**（承 `rev5:004` research R2 十一筆 rev4→rev5 翻案，全視為已翻案、不得帶回；烤入 implementer prompt）：`rev5:R2-1` 錨右側不得盲剝（F6）／`rev5:R2-2` 鎖 origin 只是縱深防禦建議／`rev5:R2-3` dev 必掛最小信任模型／`rev5:R2-4` 信心字面單一出口（`nginx_peer` 退役）／`rev5:R2-5` region 不搬／`rev5:R2-6` 模組名 `cache`／`rev5:R2-7` 只為新端點落操作稽核／`rev5:R2-8` HLL 不搬／`rev5:R2-9` `access_log_mw` 不搬／`rev5:R2-10` 零新 AppError 變體／`rev5:R2-11` dev 可達態如實列。

## R4 信任錨判定矩陣（七態 × 三層 × 兩覆蓋 × 硬化；承 rev5 R4、rev6 逐字沿用）

鏈＝`normalize(xff) ++ [peer]`，對端接在最右。層①對端閘（`peer ∉ 受信集`→peer、`direct`）；層② Tier-1 錨（最右 CDN 段、**錨右側全受信**〔F6〕、錨左第一個非 CDN 段→`cdn_anchored`；錨左無非 CDN→`fallback`；錨右含不受信跳→退層③）；層③ 最右非受信（`proxy_clean`／經 dual-role 或綁定不符→`proxy_soft`；整鏈受信→`fallback`）。覆蓋 A 通道回退（基礎 `fallback` ∧ peer ∈ tunnel ∧ 訪客標頭有值→採訪客位址、信心不升）；覆蓋 B 邊緣驗證（四前置全中→`cdn_verified`／推導不等→`cdn_mismatch`、不動位址）。★F7 溢出短路（`apply_chain_overflow`）套在矩陣**之後**、無條件：鏈原始跳數 > `MAX_XFF_TOKENS` ⇒ `chain_rejected`，`real_ip` 取自傳輸層對端（各腿皆可落此值；spec 第八態不入 SC-001「七態」射程）。硬化形式化＝`chain[anchor_idx+1..].all(is_trusted)`；合法 CDN 路徑硬化前後逐位元相同（SC-002）。

## R5 ipgate 與門鈴（承 rev5 R5）

判定面 `Arc<ArcSwap<RuleSet>>`、每請求 `.load()` 零外部查詢；`decide`＝③結構豁免六段（`127.0.0.0/8`／`::1/128`／`10.0.0.0/8`／`172.16.0.0/12`／`192.168.0.0/16`／`fc00::/7`）→④allow→⑤deny→⑥default-allow，①②為 middleware 前置；`would_self_lock`＝`decide(rs_after, operator_ip) == Deny`（結構豁免段恆 Allow ⇒ 不判自鎖）。門鈴頻道 `ipgate:invalidate`（常數單一權威住 `ipgate/mod.rs`）：寫端 `reload_and_publish`（re-read 成功才 store＋PUBLISH；失敗 keep-last-good 回 Err；PUBLISH 失敗告警回 Ok）；watcher 專用 pub/sub 連線、5 秒 timeout、1s→30s backoff、重連（含首次）補讀一次。★rev6 增一項：走查以 SQL 直寫（TRUNCATE）清規則不會按門鈴 ⇒ quickstart 收尾手動 PUBLISH（rev5 L 教訓、承 quickstart §7 1b）。

## R6 節流：兩維、無 L1、由 PG 定案（BL-00066／Q4／Q7／G4／§5 ②；spec FR-030～FR-038）

`precheck` 新流程：①讀兩維解鎖標記（帳號維鍵＋若有桶且非顯式放行則來源維鍵；任一 Err 或 `cache: None` → `redis_down`＝軟區 captcha 整層停用；Err 那維視為無標記）→②帳號維：三鍵現值（registry 界值驗、整組退＋告警 ≤1 筆）＋PG 計數（三源）→硬鎖即回 `biz.auth.locked`（短路省來源維）→③來源維：L0（顯式 allow 直讀 allow 袋、或無桶）整層跳過；否則三鍵現值同法（獨立 label）＋PG 計數（恰兩源、`<<=`）→④合成：任一硬鎖→locked；否則任一軟區或 `captcha_forced`→captcha gate；否則放行。DbErr（任一維計數）→`count := 0`＋`captcha_forced = !redis_down`（島 E 既定）。解鎖標記值＝unix 秒十進位字串（不可解析視為無標記）。設定有效性判準（兩維同形）：缺列／軟刪／不可解析／`range` 越界（沿 `validation::REGISTRY` 宣告：門檻 1..100、窗 1..1440，不另抄）／`captcha_after > max_fails` → 整組退（帳號維 5／15／2、來源維 50／15／10，鍵序＝硬門檻／窗分鐘／驗證碼門檻）。鎖中每發成本＝帳號維 4 支 PG 查詢（＋來源維 4 支）、零 argon2 零落列、上界＝nginx `auth_limit`（brainstorm 風險 3、已知態）。

## R7 dev 可達來源信心態（★誠實分界；quickstart 與 SC-014 前提；承 rev5 R7）

dev 掛最小信任模型（`deploy/trust-model.dev.toml`：僅 `internal_default = ["172.16.0.0/12"]`、compose 已掛 `APP_TRUST_MODEL_PATH`）後，經反向代理可達**二態**：`fallback`（瀏覽器不帶轉發標頭、real_ip＝反向代理位址、落結構豁免段）／`proxy_clean`（帶 `X-Forwarded-For: 203.0.113.x`）；`direct`／`cdn_anchored`／`proxy_soft`／`cdn_verified`／`cdn_mismatch` 五態由整合測試直餵信任模型覆蓋（SC-001 落整合層、SC-014 落端到端層、不得混寫）；dev 的 `geo $cf_edge` 恆 0 ⇒ 反向代理主動移除 `X-CF-Verified`／`CF-Connecting-IP`。

## R8 測試設施與機器閘衝擊（tasks 硬前置）

| 面 | 衝擊 | 處置 |
|---|---|---|
| `schema-gate` gate2 | `sys_operation_log` 已在 `RUNTIME_APPEND_TABLES`（創世）；`sys_ip_rule` 業務表逐列比對 | 零改常數；走查後由 walkthrough seed 模式清 `sys_ip_rule`（清列＋setval） |
| contract 覆蓋閘 | 16→22 case | case_key：`get-ip-rule-list`／`add-ip-rule`／`update-ip-rule`／`delete-ip-rule`／`restore-ip-rule`／`unlock-login`；既有 `auth-login`／`auth-refresh-token`／`auth-logout` 依 `wire-auth-delta.md` 增斷言 |
| `wire_schema` 裁判面 | 新 DTO 入快照 | 新檔 `rev6-ip-rule.d.ts`（沿 `rev6-auth.d.ts` 先例）＋`Api.IpRule` case；容器內重抽 fixture |
| `entity_access_lint`／`entity_behavior_lint` | 三新 facade 入唯一管道射程；entity crate 零改 | 名冊加三支；behavior lint 零觸碰 |
| `msg-key-gate` | `MSG_KEYS` 13→19 ⇒ 三檔 backend 子樹各 19 | 六鍵三語同批（U6，受 U0 硬閘） |
| `fork-delta-lint` | 新軌道列須過 `load_roster`；名冊斷言只掃修改型（本軌道全為新增型或產物檔＝結構性不適用） | 實得機器守＝`find_unmarked_additions`（圈界須存在）＋`is_generated` 豁免＋`route-artifact-gate.py` 冪等；「該列真被載入」以表列變異證（U0） |
| ★五欄範圍精確化（G1、BL-00058）實跑取數（2026-09-15；以 `原行:` 標記數計修改型、`START]` 圈界數計新增型） | (b) 三表單各 **1 處**修改型（原「各 2 處」）／(c) captcha hook **3 處**修改型＋**1 塊**新增型（原「約 4 處」）／LOGIN-CAPTCHA (i) auth store **3 處**修改型、pwd-login **2 處**修改型＋**2 塊**新增型／LOGOUT-UX (i) **1 處**修改型（原「約 3 處」）／I18N (iii) app.d.ts **0 處修改型＋1 塊新增型**（原「1 處，修改型」＝BL-00058）；(a)／I18N (i)(ii) 與現文一致 | 實數落 ADR-00034 §一 表列；`contracts/code-gates.md` §1 記量法可重跑 |
| 新增機器守 | `view-render-guard.py`（`views/manage/**` 零 `v-html`／`innerHTML`）、`route-artifact-gate.py`（產物四檔重算冪等＋憲法列產物集＝實產出集） | 各附 self-test（植入反例必紅）；四處名冊＝RUNBOOK §12 碼面閘表／README 樹／bootstrap `run_tool_test`／pre-commit 段＋`test_hook_wiring` SEGMENTS（msg-key-gate 前例） |
| `SequenceResetGuard` 廢除 | 69 處 `::new()`／10 檔＋自證測＋doc；殘列在場全量須綠 | U3 獨立單元、排在功能單元前；驗收＝造一列真帳號殘列後全量綠 |
| BL-00070 七處 | AppState 擴欄使 `router.rs` `stub_state`／`enforce.rs` `state_with`／`system_settings.rs` 端點案受編譯強制改；`obs.rs` 增案 | U3 一次收攏（委派 `oneshot_json`；`obs.rs` 案與 `send` 具名留存） |
| `docsync generate` | ROUTES 22 ⇒ `reference/routes.md` 重算；STATE pins | 每單元收尾既有步驟 |
| `test_kit` 守衛 | 水位清理守衛（`sys_operation_log` 只刮自寫列、`sys_ip_rule` 清列＋setval）住 test_kit（§5 ⑨） | U3 |

## R9 上下文缺席退路與測試面（§5 ①；spec FR-013）

- **Decision**: login／refresh／logout 取 `Option<Extension<RequestContext>>`；缺席→`RequestContext::from_headers(&headers)`（rev6 Err 兩態：缺 `X-Real-IP`→5000 不落列；在場→轉錄、信心 `fallback`、`peer_ip` NULL、判定窗空）＋結構化 warn＋`ip_domain_degraded_total{source="request_context_absent"}`；規則四寫端與解鎖以 `audit_operator(ctx: Option<&RequestContext>, ..)` 組稽核列、缺席→5000（F3①）；閘門缺席放行、來源維整層跳過（`ctx_absent` 就地記下、由 precheck 參數傳入）。
- **Rationale**: production 結構性不可達（`main.rs` 恆掛 connect_info、B-075 lint 守之）＝偵測腿；既有 `X-Real-IP` 注入之 oneshot 測試 36 處（login 15／refresh 11／logout 9／contract 1）零改形。
- **Alternatives considered**: mandatory `Extension`（36 處整批改形、缺席 5000＝fail-closed 違 F3）；缺席時以 peer 合成上下文（無 ConnectInfo 即無 peer、不可行）。

## R10 執行單元切分（tasks 的 phase 骨架；承 brainstorm §9、rev5 R10）

| 單元 | 內容 | 相依 |
|---|---|---|
| **U0** ★主線 | ADR-00034 user 親決→accepted→憲法 §I.7／§III.2 改＋bump 1.4.0＋generate（獨立 commit；硬閘：accepted 前不動 base-web 既有檔）；fork-delta 名冊變異證 | — |
| U1 | 依賴三支進場＋`config` 信任模型載入（三層＋B-074）＋`trust/` 純函式全形（八態／三層／兩覆蓋／F6／正規化／溢出短路）；ADR 三支依賴 | 純後端、可先行 |
| U2 | `ipgate/`（RuleSet／decide／六段／would_self_lock／build_ruleset）＋facade `sys_ip_rule`（load_active／list／四寫端）＋B-075 lint | U1 |
| U3 | 測試基建：廢 `SequenceResetGuard`（69 處）＋水位守衛＋`walkthrough-baseline` 三改（擴面／seed 模式／序列存在性）＋BL-00070 七處收攏＋AppState 測試建構點收斂 | 純後端；排在 U4 前 |
| U4 | `AppState` 5→7＋門鈴（reload_and_publish／watcher 專用連線）＋boot（載信任模型／初載規則集／起 watcher；BL-00072 靜態掃描＋數量字面）；ADR supersede ADR-00027 | U2／U3 |
| U5 | `middleware/` 兩支＋`request_context` 換血（八態／判定窗／peer）＋login／refresh／logout 取 Extension（§5 ①）＋F7 拒絕腿＋F8 轉錄＋`wire-auth-delta` 契約與 contract 增斷言；ADR F7／F8 | U4 |
| U6 | 規則五端點（handler）＋`model/audit`＋facade `sys_operation_log` 首寫＋防自鎖＋`MSG_KEYS` 13→19＋三檔 locale backend 六鍵＋`app.d.ts` backend 型節＋contract 5 case | U2／U5／**U0**（locale 既有檔） |
| U7 | 節流重寫（兩維、無 L1、registry 驗界整組退、`redis_down` 標記讀取、`count_recent_failures_by_ip`、帳號維 `chain_rejected` 排除、L0）＋obs 名冊改；ADR 節流去負快取 | U5 |
| U8 | 解鎖端點（稽核先於生效、兩維標記、帳號維三件、Q2 冪等）＋contract case | U6／U7 |
| U9 | 前端：管理頁三檔＋`rev6-ip-rule.{ts,d.ts}`＋locale route／page 樹＋`app.d.ts` page 型節＋路由產物重算＋`view-render-guard.py`／`route-artifact-gate.py`＋四處名冊＋`request/index.ts` 轉譯塊（Q6）＋wire-schema 快照 | **U0**／U6 |
| U10 | 治理：rules.yml（刪②、③b 錨）、RUNBOOK §16 實文／§9c／§12、活書 as-built、LL-00017 補述、ADR 譯文之家（supersede ADR-00029）＋已知態、BACKLOG 條文改寫；CDP 端到端走查（quickstart §1～§6、SC-010 結構清單）＋走查收尾 | U9 |
| U11 | 收攏：全量閘＋contract 22＋DoD（FR-070）＋final holistic review 前復核 | 全部 |

純後端單元 U1～U5／U7 不受 U0 硬閘；U6（locale 既有檔）、U9 對 U0 為硬序。每單元 pin bump、Workflow 六件套、review／fix 烤入 RULES scope 塊（RULES-VERSION 不變）、每 run 不重複 agent ≤20；發射前模型分派向 user 確認（memory 通則：implementer 與其餘角色分派、CDP 走查類另調；「暫一律 opus5 1m xhigh」為 user 2026-09-15 當前指示）。

## R11 棄案反例回跑（RL-0013：對所選方案跑同一反例）

| 棄案 | 反例 | 對所選方案回跑 |
|---|---|---|
| 保留 L1 作 PG 故障後備（Q7 棄案） | 計數查詢單獨失敗時已鎖帳號被放行 | 所選（無 L1）：走島 E 既定補償＝要求驗證碼、密碼錯仍計數＝有阻力非盲放；PG 整體故障時 `authenticate` 查 `sys_user` 即 5000＝兩案皆無法登入（差別只在部分故障窗、已記已知可見差異） |
| mandatory `Extension`（R9 棄案） | 中介層漏掛時 handler 拿不到上下文 | 所選（Option＋退路）：同一情境走轉錄退路＋結構化 warn＋降級計數＝可見且照服務；production 由 B-075 lint 守恆掛 |
| 寫端守跨鍵不變式（Q4 棄案） | 超管先把 `ip_captcha_after` 調高過 `ip_max_fails` | 所選（消費側整組退）：下一次登入嘗試即整組退常數＋告警、無鎖死無失效；寫端順序問題不存在 |
| 阻擋同時撤會話（clarify Q1 棄案） | 被擋者持既有 token 續操作 | 所選（只擋請求）：每個 API 呼叫 403、無法操作；規則解除即恢復、免重登＝符合「擋來源」語意且零跨島機制 |

## R12 本輪複核（對既有文件的確認）

1. **零 migration、零 seed 變更**再證：政策列 143～148、149、157、160～163 與選單 78 皆在 m0002；三稽核表 `ip_confidence` 可空 text 無 CHECK；來源維計數走 m0001 既有 `idx_login_attempt_ip_time (real_ip, created_at)`（`<<=` 對 inet 走 b-tree 網段運算）＝不需新索引。
2. **零新 `AppError` 變體**：`PermissionDenied`（5003）與 `Biz`（2222）既有；13 碼矩陣零觸碰。
3. **`THROTTLE_DEGRADED_SOURCES` 現七值**＝`settings_default`／`settings_invalid`／`redis_lock`／`redis_lock_set`／`redis_captcha`／`db_count`／`db_write`；本刀改十值（data-model §5 單一權威）。
4. **rev6 `precheck` 現簽名**＝`(conn, cache, captcha_secret, user_name, captcha_id, captcha_code)`；本刀加 `source: Option<SourceThrottleInput>`（桶＋L0 判定結果、缺席即 None）。
5. **base-web 現況**：`views/manage/` 無 ip-rule；`en-us.ts` `page.manage` 節在（`:551`）、`route:` 樹在（`:252`）；路由產物 `manage_ip-rule` 零命中。
