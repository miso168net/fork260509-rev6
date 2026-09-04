# 002-system-settings — server 進場首刀 brainstorm（階段 0）

- 日期：2026-09-05｜狀態：拍板四題＋方案＋設計十一節＋grilling round 四題（Q5～Q8）已過 user 核可；下一步＝**手動** `/speckit-specify`（本檔為其 input；不自動觸發——否則 before_specify hook 不跑、分支不建、spec 落 default）。
- 一句話：立 `rust-api/server` crate，打通「router→授權→handler→registry 驗證→facade→`Res` 信封→前端接線層」整條縱切管線；功能面＝系統設定**讀＋寫**；view UI 與真登入不入本刀。

> 輸入：001 brainstorm §0 Q1 刀序表（002＝system-settings、server 進場；「各刀範圍由各自 brainstorm 定、可翻」）、憲法 §I.2／§I.3／§I.5／§I.6／§II／§III／§IV、`docs/ops/BACKLOG.md` 觸發於 002 的三條（BL-00008／BL-00010／BL-00011）、NOTES「rust-fmt-gate 隨 002」、ADR-00012 決定 6（表數斷言留給首次加表的刀）、ADR-00003 註 4（`.env` route mode as-built 落後）、rev5 `rev5:002-system-settings` 全套（brainstorm／spec／research／data-model／contracts／tasks／收刀事件；唯讀、凍結 SHA 外層 7eab28a／base-web 9833308／rust-api 92919b9）、rev5:ADR 0018／0020／0021／0022／0023、rev5:L-009／rev5:L-010／rev5:L-013／rev5:L-015／rev5:L-016。

## 0. 拍板紀錄（user 拍板 2026-09-05；一題一問、首選項為建議）

| 題 | 拍定 | 要點 |
|---|---|---|
| Q1 功能範圍 | **A・承 rev5：讀＋寫＋接線層** | server crate 從零、讀端回 16 鍵、寫端單鍵更新（registry 驗證＋三態＋審計欄成對寫）、base-web 恰兩新檔；view 不入、登入不入。棄案：只讀端（三態／registry／5003 矩陣全延後，且 seed 已有寫端政策列＝留孤列）；加 view（首個 ★軌道 Amendment＋CDP 走查工具進場、量級翻倍，rev5:ADR 0018 亦延後） |
| Q2 BL-00010 | **entity-drift 段快照缺席改即紅** | 跳過分支自 001 U3 快照成 tracked 檔後恆為死支且 fail-open；補償控制已驗（缺席時 docsync `compute_generated` 抛 SnapshotError、check／lint 不捕即非零、pre-commit 仍擋）故曝險小，但 002 本就要改同段 hook、順手改零成本。棄案：保留跳過立 by-design ADR（留永不走到的分支、守門靠別段側效果）；不動留帳（同段兩刀改兩次） |
| Q3 BL-00011 | **RUNBOOK §12 定形＋GT-12 加腿** | §12 末段散文改碼面閘表、GT-12 加一腿機器對賬 tools/ 檔集＝表列檔集。棄案：另立生成名冊 CODE-GATES.md（新生成器＋GENERATED_FILES 變動＋五支工具補 docstring 區塊）；won't-fix ADR（名冊永遠靠人記得、與 RL-0049 相悖） |
| Q4 msg key 契約（rev5:Lint24） | **延前端 i18n 刀；002 只做後端側閉環** | 憲法 §I.3 只鎖「msg 載穩定 i18n key、前端 graceful fallback」、未要求此閘；rev5 形需 base-web 新增 locales 孤立檔＋rev5:ADR 0021 釋義，而 rev6 §III.1 未列 locales。後端側：`error.rs` 單一名冊＋contract 斷言；跨端閘記 BACKLOG、觸發＝首個接 i18n 的前端刀。棄案：承 rev5 zh-tw.ts＋tools/msg-key-gate.py（多一筆釋義 ADR、該檔到前端刀還要重構一次）；完全不設（拼錯 key 到前端刀才現形） |
| 方案 治理項落點 | **A・全部落 002 內、U0 治理組合拳** | hook 段只改一次；rust-fmt／wire-schema 無 server 與 typings 即無物可驗；不另開維護批（三指標「治理批對 feature 比」不再 +1）。棄案：pre-002 維護批先收純治理項（比值 +1、hook 兩刀改兩次、GT-12 新腿對賬空表）；全部延到收刀後（002 期間手寫 rust 碼與 base-web 新檔零機器守門、違「隨子庫刀進場」紀律） |
| Q5 fork-delta-lint 進場時點（grilling） | **隨 002 全量進場、結構斷言改為容空 ★表** | 實查：工具直接解析憲法 §III.1／§III.2 兩表（表頭欄名 rev5 與 rev6 相同），內建斷言「★段列數 ≥4、§III.1 恰 3 列」對 rev6 空 ★表恆紅；改為「★表零列時必見『空表——尚無 ★ 軌道』哨兵句、否則 ≥1 列」（守不消失）＋一正一反 self-test。本刀能守＝兩新檔檔頭 rev6-inline 新增型標記＋路徑落在所稱軌道範圍內。棄案：延首個 inline 刀（違 001 brainstorm「隨首個 base-web 刀」字面、軌道外目錄不會紅）；只開新增型腿、★腿空即略過（fail-open、與 Q2 方向相反） |
| Q6 registry 跨鍵不變式（grilling） | **不驗、留消費側刀** | rev5 validation.rs 只有逐鍵 (min,max) 表、零跨鍵檢查；min>max、captcha_after>max_fails 兩組矛盾可各自合法落庫，本刀零消費者、無行為後果。spec Edge Cases 明寫、BACKLOG 記一條（觸發＝004 節流／007 密碼政策）。棄案：002 加兩組跨鍵驗證（registry 從純函式變讀庫、多一組拒收矩陣、兩鍵同時改可繞過） |
| Q7 `.env` route mode 翻 dynamic 時點（grilling） | **延 003 auth-session** | 實查 rev5：翻 dynamic 與 VITE_HTTP_PROXY=N 皆在 003 以 ADAPT 修改型標記做、002 零碰 `.env`；002 翻＝後端無 getUserRoutes、32080 UI 登入後拉路由失敗直到 003。ADR-00003 註 4「ADAPT 軌道首刀」解讀為首個需要動 `.env` 的刀。棄案：002 順手翻 |
| Q8 「碼面閘」入 RULES 名詞段（grilling） | **補定義** | 該詞在 RUNBOOK §12、啟動書 §4.2、GATES.md 檔頭皆用、名詞段零定義；Q3 之後它是 GT-12 新腿的判準主詞。定義＝「tools/ 頂層對子庫碼或跨端契約做 check 的系統面機器閘（隨刀進場、不計入 GT-12 預算、名冊＝RUNBOOK §12 碼面閘表）；治理閘＝GT-NN」。動名詞段＝RULES-VERSION bump，由主線於 U0 派發前直改、U0 script 即以新版組。棄案：定義寫在 RUNBOOK 表頭（glossary 分兩家、違 RL-0049） |

## 1. rev5 承襲盤點（沿用項照已驗證結論施工、翻案項用新設計；CLAUDE.md §2）

| rev5 項目 | 處置 | rev6 落點 |
|---|---|---|
| 功能域＝系統設定、server 首刀縱切（rev5 002 §1 拍板） | 沿用 | 本刀功能域本身 |
| 前端腿＝typings＋service 接線層兩新檔、view 延後（rev5:ADR 0018） | 沿用 | `src/typings/api/rev6-settings.d.ts`＋`src/service/api/rev6-settings.ts`；view 隨後續前端刀 |
| 純新增檔不觸 ★軌道釋義（rev5:ADR 0021 款 1） | 沿用其結論、不需再立釋義 ADR | rev6 憲法 §III.1 ADAPT（typings 新檔）／WRAPPER（`rev6-*.ts` 新檔）已直接涵蓋兩新檔；locales 不碰（Q4） |
| zh-tw.ts 治理錨點孤立檔＋Lint24 閉環（rev5:ADR 0021 款 2、data-model §6） | **翻案**（Q4） | 後端側名冊閉環＋BACKLOG 跨端閘 |
| gen.msg_dict Day-1 豁免改謂詞（rev5:ADR 0020） | 不適用 | rev6 無 msg dict 生成器、無此豁免 |
| 授權拒絕語意＝5003＋純 i18n key、no-escalation 掛點簽章（rev5:ADR 0022） | 沿用 | rev6 自立 ADR（provenance 引 rev5:ADR 0022） |
| 部分更新三態約定（rev5:ADR 0023） | 沿用 | rev6 自立 ADR（provenance 引 rev5:ADR 0023） |
| registry 16 鍵值域（rev5 data-model §3：number 10 鍵含界、enum 6 鍵） | 沿用原值 | `server/src/validation.rs` const |
| wire 形＝POST 單鍵更新（seed 政策列 67 錨定 `updateSystemSetting POST`）、未知鍵→2222、未認證→8888、JSON null 承載清空（rev5 clarify 四答） | 沿用 | spec 直接轉錄、clarify 不重問 |
| dev-only 測試態 identity（rev5 research R8：`cfg(debug_assertions)` 固定 token 查表） | 沿用 | `auth/dev_identity.rs` 獨立檔、003 整檔汰換 |
| ROUTES 四條單檔＋case_key 雙向覆蓋閘（rev5 data-model §4） | 沿用 | 字面形同時是 docsync `reference/routes.md` 生成器的解析契約 |
| rev4→rev5 拍板差異點 13 筆（rev5 research R3） | 全部視為已翻案、**不得帶回** | 烤進 implementer prompt 的防回歸清單 |
| rev5:B-014 `sys_user_role` FK Relation | 001 已做（形狀派生、保留） | 不入本刀 |
| rev5:B-028 冷編量測兩輪、rev5:B-001 K1 承襲盤點 | 不做 | rev6 無對應帳；冷編時長列風險（§3 §10） |
| registry 只驗單鍵界、零跨鍵檢查（rev5 validation.rs） | 沿用（Q6） | 跨鍵矛盾留消費側刀、BACKLOG 記觸發 |
| `roles_of_user` 兩濾網（角色 `deleted_at IS NULL`＋`status=1`）、`update_by_key` 同值更新照寫審計欄（rev5 002 facade） | 沿用 | spec Edge Cases 明寫 |
| 六起「守門抓不到它該抓的東西」與 RAII 還原守衛（rev5 002 收刀 notes） | 沿用為紀律 | 烤進 review prompt（非 vacuous 自證：案綠→打壞判準→案紅→還原） |

## 2. BACKLOG 觸發項處置（動工前掃描、CLAUDE.md §2）

- **BL-00008**（觸發：002 開分支時）→ U0 建 `server/tests/entity_behavior_lint.rs` 機器錨（設計 §5）；收刀 `backlog_done`。
- **BL-00010**（觸發：002 brainstorm）→ Q2 拍定改缺席即紅、U0 hook 段同批改（設計 §7）；收刀 `backlog_done`。
- **BL-00011**（觸發：wire-schema 進場刀 brainstorm）→ Q3 拍定 RUNBOOK §12 定形＋GT-12 加腿、msg key 契約去處＝Q4（設計 §7）；收刀 `backlog_done`。
- 其餘五條（BL-00002／00003／00006／00007／00021）觸發未到、本刀不碰。

## 3. 設計（十一節、user 已核可）

### §1 目標與範圍

立 `rust-api/server` crate（workspace 第四 member），功能＝系統設定讀（一次回 16 鍵）＋寫（單鍵更新）；前端腿恰兩新檔；零 migration（`system_settings` 表＋16 鍵 seed＋casbin 政策列 66／67 皆已隨 m0001／m0002 在庫）；`tools/schema-gate.py` 表數斷言 `!= 14` 不動。本刀＝憲法 §I.3 所稱「wire 地基刀」（契約機器化機制隨本刀落地）。**不入刀**：view UI、真登入／session（003 auth-session）、稽核 log 寫入、設定值消費側（節流／逾時／密碼原則 enforce 各留對應域刀）、no-escalation 本體（僅空掛點）、新增／刪除設定鍵端點、列表排序、prod 資產。rev5 對應碼＝預設藍本：先讀後寫、重打字消化、註解一律 rev6 語境重寫、前代出處帶 `rev5:`（憲法 §I.5）。

### §2 架構與單元邊界（server crate 內、各單元一責；對照 rev5 002 終態 server 27 檔的樹）

- `router.rs`：`ROUTES` const 單檔四條（`/health`、`/metrics`、`GET /systemManage/getSystemSettings`、`POST /systemManage/updateSystemSetting`）；RouteDef 帶 path／method／case_key／envelope_exception／protection（Public／Authed／Policy 三態，本刀無 Authed 成員）；字面形＝docsync routes 生成器解析契約（每欄一行、枚舉字面）。
- `auth/enforce.rs`：casbin 最小骨架——判定收斂單一純函式進入點、require_policy 每請求 DB-fresh、空 no-escalation 掛點；`auth/dev_identity.rs`：`cfg(debug_assertions)` 查表 dev-super／dev-admin／dev-user→uid 1／2／3，缺席或未知→8888。
- `handler/system_settings.rs` 薄殼（解析→授權→registry 驗證→facade→信封）；`validation.rs` registry（16 鍵 const、每鍵顯式型別與值域、number canonical＝trim→parse i64→界內→to_string、未知鍵 2222、庫中未知型 5000 fail-loud）；`model/facade/system_settings.rs`（find_all／find_by_key／update_by_key 皆帶 `deleted_at IS NULL`、審計欄顯式成對寫）；`model/facade/sys_user_role.rs`（roles_of_user）。
- `envelope.rs`（`Res` 三欄宣告序 data→code→msg、2^53 fail-loud 守衛、i64 序列化守衛）；`error.rs`（13 碼常量 mod 全列、AppError 恰六變體＝0000／2222／4040／5003／5000／8888，1000／3333／7777 與 4 保留碼無變體＝構造層不可發出；msg key 名冊常數）；`config.rs`（`APP_DATABASE_URL[_FILE]`）；`state.rs`（AppState 恰 {db, enforcer}）；`obs.rs`（recorder＋render＋axum-prometheus 三序列）；`request_context.rs`（信任判定 seam 介面位、空殼）。
- 不建：redis／throttle／ipgate／jwt／captcha／PageRes／熱套用 stub／reload_enforcer（rev5 research R3 縮編面沿用）。web 框架＝axum（rev5 已驗證組合；版本於 plan research 逐筆雙源對照、CLAUDE.md §6）。

### §3 wire 契約與機器化

- 權威＝typings 新檔：TS declaration merging 併入 `Api.SystemManage`——`SystemSetting`（settingKey／settingValue／settingType／description?）、`UpdateSystemSettingReq`（settingKey／settingValue／description?: string | null 三態欄）；service 新檔兩函式 `fetchGetSystemSettings`／`fetchUpdateSystemSetting(req)`、不入 barrel。兩檔皆走 fork-delta 新增型圈界檔頭標記（token `rev6-inline`、註明軌道與刀名）。
- `tools/wire-schema.py` 自 rev5 隨遷（650 行；容器內 `npx typescript-json-schema@0.67.4` 唯讀抽取、`--strictNullChecks`、原子替換寫快照、`check --staged-gate` 收窄；typings glob `src/typings/{common,api/*}.d.ts` 已涵蓋 `api/rev6-*.d.ts`、零改）；隨遷核對＝compose 兩檔名、`base-web` 服務名與 `-w /app`（rev6 皆同）、註解四型失效引用 rev6 化。
- 快照 `rust-api/server/tests/fixtures/wire-schema.json`＋`tests/wire_schema.rs` 裁判（SettingItem 序列化輸出必過、UpdateReq 三態欄以快照斷言 `["null","string"]`）＋`tests/contract.rs` case registry 與 `ROUTES` 之 case_key **雙向**覆蓋閘（缺 case 紅指名、殭屍 case 紅指名；本刀 case 恰四）。
- docsync 新生成器 `docs/generated/reference/routes.md`（自 `router.rs` ROUTES const 重算；欄＝path／method／protection／case_key／envelope 例外）；GENERATED_FILES 14→15、README 樹 `docs/generated/` 成員行同步（BL-00009 新腿守）。

### §4 授權面與身分

- Policy 路由＝enforce_mw（dev 驗證器取 uid→roles_of_user）＋require_policy(path, method)；casbin act＝HTTP 方法字面、與 seed 政策列 66（GET）／67（POST）對齊；路徑不帶 `/api`（front-nginx strip、憲法 §II #3）；不動 sys_menu／casbin seed。
- 拒絕語意承 rev5:ADR 0022：越權＝`5003`＋HTTP 403、回包恰 `{data:null, code:"5003", msg:"system.forbidden"}`、不揭露缺哪條政策；no-escalation 掛點簽章預留 async 與 db、本刀恆放行。未認證（無 Authorization／非 Bearer／token 不在 dev 表）＝`8888`（HTTP 200 信封）；003 接真 session 時再對齊 3333／8888 分工。
- rev6 自立 ADR 承此形（拍板歸 ADR；序號落檔時取）。

### §5 資料面

- 零 migration；`system_settings` 變體 A 六欄、PK＝setting_key（總體唯一、免 partial-uniq）。讀端僅未刪列、`settingKey` 升冪穩定序、審計欄不上 wire；寫端單鍵原子 UPDATE、last-write-wins、無樂觀鎖（16 鍵低頻治理面）、`updated_at`＋`updated_by` 由 facade 顯式成對寫（憲法 §I.6）、operator uid 取自請求身分；驗證失敗零寫入。
- **BL-00008 機器錨**＝`server/tests/entity_behavior_lint.rs`（承 rev5 終態形重打字：entity crate 全部 `impl ActiveModelBehavior for ActiveModel` 必為空實作、站點數＝表 entity 檔數的等式形、strip 註解與字串後再判、合成正例自證）。
- 邊界案（spec 轉錄）：同值更新照寫 `updated_at`／`updated_by`（承 rev5、last-write-wins 一致）；`description` 空字串＝設值為 ""、與 JSON null 清空不同；角色軟刪或停用（`status≠1`）視同無該角色（承 rev5 `roles_of_user` 兩濾網）；enum 值大小寫敏感（canonical＝原值）；跨鍵一致性非本刀驗證面（Q6）。
- `sys_user_role` 兩條 FK Relation 001 已在、不再動；`tools/schema-gate.py` 的 `!= 14` 不動（ADR-00012 決定 6）。clarify／plan 若冒出 DDL→RUNBOOK §10 Day-1 三步照走並改該斷言（spec 以 FR 形寫死此分岔）。

### §6 錯誤處理、三態、msg key

- 三態承 rev5:ADR 0023：部分更新 body 每一可選欄——缺席＝不動／JSON null＝清空／有值＝設值；NOT NULL 欄收 null→2222；nullable 欄（description）→落 NULL；解析層 `Option<Option<T>>`＋`#[serde(default)]`＋自訂 `deserialize_with`（rev5:L-009：預設 Deserialize 把 null 也落外層 None、三態塌兩態）。射程＝部分更新請求 body；rev6 自立 ADR。
- 錯誤矩陣＝rev5 contracts §1／§2 照收：settingValue 型別不符／超範圍／enum 外／顯式 null、欄缺席／型別非 string／反序列化失敗→2222 `biz.systemSettings.invalidValue`；settingKey 不在 registry（含軟刪防禦態）→2222 `biz.systemSettings.notFound`；越權 5003；未認證 8888；庫中未知型→5000 `system.internal`（讀寫皆 fail-loud、不跳過該列）；router fallback→4040 `system.notFound`（HTTP 404）；成功 `common.success`。
- msg key 後端側閉環（Q4）：`error.rs` 單一常數名冊（本刀七鍵）；contract test 斷言每條 route 每個錯誤路徑實發 msg ∈ 名冊、名冊每鍵至少一個發出點（雙向、防殭屍鍵）。跨端閘（名冊 ⊆ 前端字典）記 BACKLOG、觸發＝首個接 i18n 的前端刀。

### §7 治理進場（U0 組合拳）

- **碼面閘三支自 rev5 隨遷**（RULES 名詞段「隨遷工具」：逐字承襲允許、註解與字串的四型失效引用 rev6 化、自帶 self-test 綠後入 pre-commit 自測迴圈與 GT-09 EXEC／README 樹）：`tools/rust-fmt-gate.py`（427 行；容器內 `cargo fmt --all --check` 唯讀、docker 缺或 `rust-api` 未起＝具名跳過、容器在而 cargo-fmt 缺＝rc 2；rev6 映像已裝 rustfmt component）、`tools/wire-schema.py`（§3）、`tools/fork-delta-lint.py`（1108 行；本刀兩新檔只走新增型圈界腿＋§III.1 範圍腿、修改型腿 vacuous；需源倉 `fork260509-soybean-admin-base/` 在 example tip、bootstrap 已斷言；★隨遷必改其結構斷言（Q5）：rev5 形「§III.2 ★段列數 ≥4」對 rev6 空 ★表恆紅，改為「零列時必見『空表——尚無 ★ 軌道』哨兵句、否則 ≥1 列」，self-test 一正一反：移除哨兵句即紅）。
- **pre-commit 同段改動六處**：①自測迴圈 for 名冊加三支 ②rust-fmt 段（staged 含 `rust-api` gitlink 或該工具即跑）③wire-schema 段（staged 含 `base-web` gitlink 即 `check --staged-gate`）④fork-delta 段（staged 含 `base-web`、該工具或憲法即跑）⑤entity-drift 快照缺席改 rc 2 帶補救提示「跑 `python3 tools/docsync refresh` 照相」（BL-00010；hook 面真演練＝移走快照→commit 被擋→`git checkout HEAD --` 還原→porcelain 對賬，LL-00003）⑥檔頭第 2 行 schema-frozen 觸發面補 `schema-definition.md`。失準修單＝`python3 tools/docsync errata schema-frozen` 全 repo 枚舉逐處處置（現知 pre-commit 檔頭、README 守門句；docs/process 兩檔只提段名未寫觸發面、掃後定）。
- **RUNBOOK §12 碼面閘表＋GT-12 新腿**：§12 末段散文改表（工具檔｜守什麼｜觸發時機｜根據 ADR）；GT-12 腿＝`tools/` 頂層 `*.py` 檔集 − 非閘名冊常數（`wf-watchdog.py`）＝ 表列工具檔集（雙向差集即紅；`tests/test_gates.py` 一正一反）；GATES.md 之 GT-12 掃描面欄由 docstring 同步。`rev5:Lint24` 去處＝Q4（表內以一列註記「msg key 跨端閘：延前端 i18n 刀、BL 承載」）。
- **RULES 名詞段補「碼面閘」定義**（Q8；字面見 §0）：由主線於 U0 派發前直改＋RULES-VERSION bump、`generate` 重產 `_sk_rules.js`，U0 起全部 script 以新版組裝。
- **ADR 五筆**（一決策一檔；rev6 自立、序號自 ADR-00013 起於落檔時取；皆帶 rev5 provenance）：①部分更新三態約定 ②授權拒絕語意＋no-escalation seam ③碼面閘名冊承載於 RUNBOOK §12＋GT-12 腿（BL-00011）④msg key 跨端契約延前端 i18n 刀、002 後端側閉環（Q4）⑤entity-drift 快照缺席即紅（BL-00010）。憲法零 Amendment（零 inline、零狀態機、零新表、零新 ★軌道）。
- 隨遷工具落地當日先跑 GT-05 子庫腿與 `python3 tools/docsync lint`（五形＋rev6 刀集豁免已就位）。

### §8 測試與 DoD

- TDD 三層：純函式紅綠（registry 每型合法／非法／未知鍵／未知型、三態解析缺席／null／值三形、碼映射）；oneshot 契約（per route case＋錯誤矩陣＋4 保留碼與 1000／3333／7777 零發出＋unknown header 忽略斷言）；真庫 integration（容器內 `--test-threads=1`、寫測試掛 panic-safe RAII 還原守衛、殘留會紅在 16 鍵全等斷言上）。
- 閘全綠：entity-drift、schema-gate 三閘、wire_schema 裁判、entity_behavior_lint、三支碼面閘各一正一反、coverage gate 負向自證（抽一 case→紅指名→還原）。
- DoD：全部預設業務件 `up -d --wait` 起得齊（七件：postgres／migrate／redis／rust-api／base-web／front-nginx／mailpit）；`curl http://127.0.0.1:32079/health` 回 ok、`/metrics` 有 exposition（皆 dev 直連埠——front-nginx 的 /health 自答塊、/api/metrics 擋塊）；quickstart 讀端／授權矩陣／寫端往返經 front-nginx 真 HTTP 走查；lint 全綠、GT-12 預算內；SC 逐條對照、US 場景逐一對到具名測試案（函式名＋案序）。世代 DoD B 之 CDP 對照＝不適用（本刀無 UI）、走查基準工具不隨本刀遷。

### §9 起手固定 tasks 與單元切法草案（tasks 定稿於 SDD；此處只定骨）

U0 治理組合拳（純治理、零 rust 碼：三支閘隨遷含 fork-delta 斷言改形＋hook 六處＋§12 碼面閘表＋GT-12 腿＋失準修單；名詞段定義由主線先落）→ U1 server 基座（Cargo member、envelope／error／config／state／obs、boot 鏈、/health＋/metrics、contract 骨架＋覆蓋閘、rust-fmt 首跑、docsync routes 生成器＋GENERATED_FILES／README 同步、`entity_behavior_lint.rs` 機器錨——後兩件要 crate 與 `router.rs` 先在、故不落 U0）→ U2 授權與身分（enforce／dev_identity／facade sys_user_role）→ U3 讀端 US1（typings 新檔＋wire-schema 快照首抽＋裁判）→ U4 寫端合法路徑 US2（service 新檔）→ U5 驗證失敗 US3 → U6 越權矩陣 US4 → U7 三態 US5 → U8 收攏（活書 §5／§8 as-built、quickstart 走查、DoD 負向自證、Day-1 三步不適用之記載）。每單元 pin bump；rust build／test 全程容器內 serial；review／fix 烤入 RULES scope 塊。

### §10 風險

1. 容器冷編時長未量（rev5 記 43.9 秒、registry 卷已含 rev5 依賴集）——U1 首次 build 記時、超出預期只留帳不擋。
2. **rust-fmt-gate 首跑對 001 逐位元承襲的 17 檔**：預期綠（rev5 92919b9 存量已 fmt、toolchain 同版）；若紅＝格式化即破 ADR-00009 條件①逐位元自證——**停手升 user**、不得自行 fmt。
3. fork-delta-lint 1108 行 rev6 化註解工作量、結構斷言改形（Q5）與源倉依賴；wire-schema 需 base-web 容器起得來（node 26、pnpm install 冷啟）。
4. pre-commit 新增三段的牆鐘：雙錨 45／90 秒；rust-fmt 容器內約 2 秒、wire-schema 只在 typings 變動時重抽、fork-delta 含 self-test——U0 落地後量一次 precommit_chain perf 事件。
5. 隨遷工具拷入後先 grep 前代裸編號（GT-05 子庫腿與外層五形）；rev5 六起守門假綠與 rev6 LL-00001～00003 烤進 prompt。
6. U0 為純治理單元、無 rust 碼；若 RULES 需動須同批 bump RULES-VERSION（後續 script 重組）。

### §11 rev6 對 rev5 002 的差異點（防回歸反向清單：rev5 已翻案者不得帶回；rev6 新差異逐條記）

1. 前端新檔前綴 `rev6-`、圈界 token `rev6-inline`。
2. 無 zh-tw.ts、無 Lint24、無 msg dict 生成器——後端側名冊閉環＋BACKLOG 跨端閘（Q4）。
3. fork-delta-lint 隨本刀進場（rev5 創世已有）。
4. 無 rev5:B-028 型量測、無 K1 盤點（rev6 無對應帳）。
5. tokio 直釘 1.53.1 實值（001 已拍）；其餘新進 crate（axum／serde／serde_json／tracing／tracing-subscriber／tower／metrics 三件／jsonschema）逐筆雙源對照後於 plan 定案。
6. routes 真表由 docsync 新生成器產（rev5 在 docs-sync 內建）。
7. entity-drift 快照缺席即紅（rev5 為具名跳過）。
8. `sys_user_role` FK Relation 已隨 001 在、不入本刀。
9. ADR 自立四筆、皆帶 rev5 provenance；憲法零 Amendment。
10. `.env` `VITE_AUTH_ROUTE_MODE` 翻 dynamic 延 003 auth-session（Q7 拍板；承 rev5 時點、本刀無消費者）——ADR-00003 註 4 之「ADAPT 軌道首刀」以首個需要動 `.env` 的刀解讀。
11. fork-delta-lint 結構斷言改為容空 ★表（rev5 形＝★段 ≥4 列；Q5）。

## 4. 憲法 §IV 九題預答（供 `/speckit-plan` Constitution Check 起手）

1. base-web 為權威：PASS——wire 形對齊 typings 新檔、範圍不縮減、view 延後屬排程。2. base-web inline：零（恰兩新檔、皆 §III.1）。3. casbin：不動 seed、enforce 消費既有政策列。4. §I.3：信封／13 碼 reuse 零新碼／msg=key／2^53 守衛／PageRes 不適用／契約機器化隨本刀落地。5. 前代拷貝：rust 應用碼全重打字；三支 tools 為隨遷工具（名詞段授權）。6. §II：#1 unknown header 忽略（contract 斷言）、#2 不觸（`.env` 延 003）、#3 路徑不帶 `/api`。7. ★軌道：零。8. 新表：零、零 migration。9. 行為島：無狀態機（registry 純驗證、enforce 消費 seed）；零 Amendment。

## 5. 給 `/speckit-specify` 的輸入摘要

- feature 名＝`002-system-settings`；user 故事核心＝R_SUPER 經 API 讀取全部系統設定、更新單鍵且值受型別／範圍驗證，非法值與越權寫入被正確拒絕，部分更新具三態語意。
- 直接輸入：本檔＋BL-00008／00010／00011＋rev5 `rev5:002-system-settings` spec 之 US1～US5、FR、SC、Edge Cases（沿用形、rev6 座標改寫：無 zh-tw.ts／Lint24／rev5:B-028／K1 相關 FR，新增 U0 治理組合拳、routes 生成器、msg key 後端閉環、entity-drift 即紅之 FR）。
- 待 clarify 候選：①dev token 字面與查表落點（研判＝沿 rev5 三 token）②msg key 名冊落點與雙向斷言形③fork-delta 新增型檔頭標記字面（`// [rev6-inline BASE-WEB-ADAPT+ 002-system-settings] …`）④RUNBOOK 碼面閘表欄集與 GT-12 腿的非閘名冊常數形⑤routes 真表欄集⑥registry 宣告型別與庫中 `setting_type` 字面不一致時的處置（研判＝視同未知型 5000 fail-loud、registry 為驗證權威）。

## 6. 隨做隨記

- ADR 待立五筆（§7；刀分支內落、序號自 ADR-00013 起）。
- RULES 名詞段「碼面閘」定義（Q8）＝U0 派發前主線直改、RULES-VERSION bump。
- BACKLOG 待記兩條：msg key 跨端閘（後端名冊 ⊆ 前端字典；觸發＝首個接 i18n 的前端刀）；registry 跨鍵不變式（min≤max、captcha_after≤max_fails；觸發＝004 ip-trust-anchor／007 user-password-admin 之消費側進場）。
- 收刀 `backlog_done`：BL-00008／BL-00010／BL-00011。
- NOTES「下一步」：specify 起手後同批改為 002 進行中；收刀時改 003。
- 活書：arc42 §5（server crate 管線形）／§8.2（契約機器化與三態 as-built）／§8.3（拒絕語意 as-built）於 feature branch 內改成現在式；C4-L2 若拓樸不變零改。
