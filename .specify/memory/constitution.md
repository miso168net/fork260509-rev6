# rev6-admin (fork260509-rev6) Constitution

> **本檔為 rev6 設計凍結權威**：與活書家族（`docs/arc42/` 12 節＋§13、`docs/c4/`、`docs/compliance/`、`docs/process/`）、ADR、`docs/ops/RULES.md`、生成物衝突時以本檔為準（權威鏈＝§V.1）。
> v1.0.0 由 rev5 constitution v1.10.0（rev5 凍結 SHA `7eab28a`、唯讀）依啟動書 `docs/brainstorms/000-doc-architecture.md` §3.8 逐條表搬入、user 親審 diff 後定版（創世拍板紀錄＝ADR-00003）。
> 改動本檔一律走 Amendment 流程（§V.2）；spec-kit `/speckit-plan` 必須對照本檔跑 Constitution Check（§IV）。
> 文件治理**程序**條款（三材質細則、時態、完成即刪、ID 配號、lint 運作模式）住 `docs/ops/RULES.md`——改動走輕量軌、不走 Amendment。

---

## I. Core Principles

### I.1 base-web 為權威（NON-NEGOTIABLE）

**規則**：base-web（`rev6-admin-base-web` 分支實碼、自 upstream soybeanjs example `8be6f9ba` 衍生——基線 SHA 與 rev5 同、啟動書 D14）有的功能，rust-api 都要提供對應 endpoint。設計範圍嚴格、不縮減。

**含義**：
- base-web 的 wire／type／endpoint／route shape，rust-api 必須對齊
- 「v1 從簡」只能是交付排程、不能簡化設計範圍
- 不動 base-web inline（例外見 §III 軌道授權；授權後的變動執行紀律見 §III fork-delta 紀律）
- upstream rebase 友善——不留 upstream 衝突風險高的改動；fork 差異全程 `rev6-inline` 標記可定位

### I.2 menu 權限 Casbin enforce

**規則**：menu 由 Casbin RBAC enforce、有權才顯示。

**含義**：
- 業務 menu 走 `/route/getUserRoutes` → 後端 Casbin enforce 過濾 → 前端顯示
- demo menu 處理：demo view **全部進 `sys_menu` seed、初始僅勾給 `R_SUPER`**——全集完整、可見性由角色勾選層（casbin menu 維度）治理下放；`hideInMenu`／頁面排除等前端隱藏機制**皆不啟用**。例外與釋義（承 rev5:ADR 0005）：①toggle-auth 示範鏈（`function`／`function_toggle-auth`）保留 `R_ADMIN`／`R_USER_COMMON` 初始勾選（恰 4 列、示範「三角色各見不同按鈕」語意所需、承 rev4 終態）；②「不啟用」＝禁止以 hideInMenu 作 demo 可見性治理手段，upstream route meta 自帶之 `hide_in_menu` 值照原樣入 seed、不視為啟用（6 列白名單載 rev5:ADR 0005）
- constantRoutes（login／404／403）前端寫死、與 menu 無關、不動；constant route 集合可經 §III.2 授權新增——builtin 三頁不動與 Casbin 豁免語意不變

### I.3 wire 契約權威序與不變式（NON-NEGOTIABLE）

**權威序**（對賬裁決）：
1. **base-web 實碼**（`rev6-admin-base-web` 分支：`typings/api/*.d.ts`＋`service/api/*.ts`＋`.env`＋`views/**`）＝ wire **唯一權威**
2. 官方 docs 站＝解釋性文件，僅紀律性約束引為規範
3. mock 實測＝補充回歸 fixture，**不當 shape oracle**

**鎖定不變式**：
- envelope `{data, code, msg}`（無 `success` bool）；`code`＝string `"0000"` 非 number；business error 走 **HTTP 200** 信封
- **id 序列化＝逐欄位忠實 typings**：typings 宣告 number 的欄位回 JSON number、宣告 string 的欄位（如 `MenuRoute.id`／`UserInfo.userId`）於序列化邊界轉字串；DB 一律 i64 自增；serializer 帶 2^53 fail-loud 守衛；**型別謊言帳本歸零起算**（每筆顯式偏離＝拍板、立 ADR）
- **13 碼矩陣整組凍結**：`0000`/`1000`/`2222`/`3333`/`7777`/`7778`/`8888`/`8889`/`9998`/`9999`/`4040`/`5003`/`5000`；HTTP status 例外僅 `4040`→404、`5003`→403，**內部錯誤 `5000` 一律 HTTP 200 信封**；4 保留碼（`7778`/`8889`/`9998`/`9999` 組內後端從不發出者）僅前端 `.env` 分組認得、contract test 斷言後端從不發出；新需求優先 reuse 既有碼
- `msg` 載穩定 i18n key（後端語言無關、不在地化；前端 `$t` 翻譯、未命中 graceful fallback）——「wire 凍結事實」指錯誤碼本身、`msg` 非人話字串；觀測側可讀性補強候選掛 BACKLOG
- 業務驗證 error code＝`2222`；`5xxx` 段為授權／基建、非業務；refresh 類 critical code 絕不用在業務驗證
- 分頁形 `PageRes<T>`＝`{current, size, total, records}`（camelCase、無 `pages`/`success`、空頁 `records:[]`）
- envelope universal 例外僅 2：`/health`（plain text）與 `/metrics`（Prometheus exposition）
- 預設帳號：`Super / Admin / User`（login req）＋ User → User01 alias（getUserInfo response）
- **契約機器化**：typings 抽 JSON Schema 當 contract test 裁判（唯讀、不動官方檔）＋coverage gate（每條 route 必有 contract case）＋碼表 table-driven case；機制隨 wire 地基刀落地

**錨定註**：本節錨定 `rev6-admin-base-web` 分支實碼；若上游演進使碼表／typings 與本節分叉，於 wire 地基刀對賬現形、走 Amendment 校正。

### I.4 SDD＋TDD 混合工作流（NON-NEGOTIABLE）

- 每把刀（spec-kit feature、`NNN-<name>` 分支）的路徑固定為 **brainstorm → SDD 設計鏈 → TDD 實作 → finishing**；階段不可跳、不可反序；期間拍板一律歸 ADR。
- 收尾一律 `git merge --no-ff` 回 `rev6-admin-root`（保留 feature branch 供 audit）；`git push`／`git merge` 不得出現於 finishing 之前。
- 收刀簿記三步：events append＋NOTES＋`python3 tools/docsync generate`（一筆簿記 commit；perf 第四步等細目＝RULES.md）。
- 詳細操作（各階段指令、Workflow 編排、防呆六件套、看門狗、單元收尾序、輕量軌判準）＝`docs/ops/RULES.md`＋CLAUDE.md §2（本檔不重複）。

### I.5 rust-api 全新寫、對前代 source 受控參照（RUSTAPI-SOURCE-ISOLATION）

**規則**：rev6 rust-api 整棵樹自源倉 main `32c5254`（Initial commit）起全新寫；設計以 rev5 已驗證結論為輸入（承接經 ADR provenance、引 `rev5:ADR 00NN`），**code 不拷貝**。實作以 rev5 對應碼為**預設藍本**——先讀後寫、高度參照（承 rev5:ADR 0019）。

**前代 source 立場（rev5 為主、rev4 溯源，皆唯讀參考庫；rev5 樹凍結於 SHA `7eab28a`、由 `tools/bootstrap.sh` 斷言、絕不寫入）**：
- **讀允許**：可 grep／閱讀前代 source 對照驗證（施工參考）
- **拷貝禁止**：實作必須重新打字消化、不可整段複製
- **註解一律重寫**：不拷前代註解；rev6 語境重寫（引 rev6 契約／ADR）、前代出處帶 `rev5:` 前綴（rev4 溯源帶 `rev4:`）
- **防回歸條款**：參照前代 code 時，凡 rev6 拍板已推翻的行為**不得帶回**

**例外**：①`sea-orm-adapter`／`xdb` 工具性 crate 整檔拷貝（承 rev5、已驗證、工具性質）；②資料形狀契約三件整檔拷貝——基線結構 migration（`m0001_baseline_schema.rs`、承 `rev5:m001`）、基線 seed migration（`m0002_baseline_seeds.rs`、承 `rev5:m002`）、基線 entity 15 檔——射程鎖 rev5 rust-api 凍結 SHA `92919b9` 之版本；程式內容逐位元承襲（去註解後 diff 全等自證）、檔名依 ADR-00008 四碼；註解依語意判準重寫（四型失效引用必改、前代出處帶 `rev5:`；通用註解可同文）；防回歸條款照常；`m0003` 起 delta migration 與一切業務碼不在此例外（ADR-00009）。

### I.6 業務表審計欄標準（SCHEMA-AUDIT-COLUMNS）

**規則**：業務主表建表（create migration）時 MUST 含 6 審計欄——
`created_at` / `created_by` / `updated_at` / `updated_by` / `deleted_at` / `deleted_by`。

**型與約束**：
- `*_at`：`timestamptz`。`created_at` NOT NULL default `now()`；`updated_at`／`deleted_at` nullable
- `*_by`：operator 的 `user_id`（`bigint` nullable／`Option<i64>`，**非 user_name 字串**）；system seed／migration／未認證情境無 operator → `null`
- **成對**：`deleted_at` 必與 `deleted_by` 同寫；`updated_at`＋`updated_by` 同理

**archetype 四變體**（整組凍結；各表歸屬隨 schema 刀入活書與 generated/reference/schema）：
- **A 業務全 6 欄**（例：使用者／角色／選單／系統設定表）：如上；soft-delete 表配 partial-uniq `WHERE deleted_at IS NULL`（PK 本身總體唯一者除外）
- **B append-only 日誌**（例：三 log 表）：只 `created_at` NN（＋operator 類 domain 欄）；**無 soft-delete、無 update、不可竄改**；MUST NOT 加 `updated_*`/`deleted_*`（retention 水平線刪除不屬「竄改」——權威釋義隨稽核域行為島進場時以交叉指針回填本句；rev5 位置＝rev5 憲法 §I.7 島 J3）
- **C join／狀態機**（例：user-role join＝零審計硬刪；token 表＝僅 `created_at`＋status 狀態機）；★變體 C upsert 釋義（承 rev4:ADR 0085 釋義）：1:1 已驗證值衛星表之 upsert 刷新＝重驗事件覆寫、`verified_at` 即其時戳、不設 `updated_*`——「成對」條款不因此觸發
- **D 治理變體**（例：casbin 規則表＝`protected`/`created_at`/`created_by` 對 stock adapter 隱形；archive 表＝原 grant 欄＋`archived_at/by`＋`archive_reason`、無 update/delete 欄）

**無 retrofit 條款（含範圍釋義）**：本標準自第一條 migration 即生效——建表即帶 archetype 全欄，**不允許「建表漏審計欄、事後補」**。釋義：本條款標的**僅限 archetype 審計欄**；既有表因功能需要加業務／鑑識欄的**刻意、規劃、可逆**演進不在此限——前提是 archetype 欄規則不變（如變體 B 永不加 `updated_*`/`deleted_*`、不可竄改性維持），且非「忘帶事後補」的意外債。

### I.7 行為島 invariants（隨刀進場）

**本節為行為島狀態機不變式的凍結位，隨刀填充。**

**進場規則**：每台狀態機（如 token rotation／policy governance／single-session）隨其刀的 brainstorm 拍板後，以 **MINOR Amendment** 將不變式條文入本節；前代已驗證狀態機之不變式（rev5 憲法 §I.7 已入憲者）為對應刀 brainstorm 的直接輸入（出處經 ADR provenance 溯源、引 `rev5:ADR 00NN`）。入本節後，動任一條不變式走 Amendment；方向性反轉（fail-OPEN/closed 方向、DB-first、踢人雙通道分離等）＝MAJOR。常數值與欄級細節留活書（非凍結面）。

**已入憲行為島**：（尚無——首座隨首刀以 MINOR Amendment 進場。）

**承襲指針**（user 拍板 2026-09-03：島體不預載、隨刀重新進場確認＝世代 DoD 的每刀驗收）：rev5 憲法 v1.10.0（唯讀、凍結 SHA `7eab28a`）§I.7 曾入憲十座行為島，對應域動刀時為 brainstorm 的直接輸入、依本節進場規則重新入憲——

| 島 | 名稱 | rev5 入憲載體 |
|---|---|---|
| A | token rotation | rev5:ADR 0028（rev5 v1.3.0） |
| B | single-session | rev5:ADR 0028（rev5 v1.3.0） |
| C | denylist 撤銷 | rev5:ADR 0028（rev5 v1.3.0） |
| D | idle 逾時 | rev5:ADR 0028（rev5 v1.3.0） |
| E | 登入失敗節流 | rev5:ADR 0028（rev5 v1.3.0；來源維兩句隨 rev5 v1.4.0 補） |
| F | IP 存取閘＋信任錨＋來源維節流 | rev5:ADR 0040（rev5 v1.4.0）＋rev5:ADR 0043（rev5 v1.5.0、F7／F8）；釐清至 rev5 v1.6.2 |
| G | casbin 授權治理（含 G6 結構性封死） | rev5:ADR 0053（rev5 v1.8.0；G6＝rev5:ADR 0054、復原五腿＝rev5:ADR 0055） |
| H | 選單域生命週期 | rev5:ADR 0048（rev5 v1.7.0） |
| I | 使用者域治理（含 I7 no-escalation 包含規則） | rev5:ADR 0063（rev5 v1.9.0）；I5 釐清＝rev5:ADR 0068（rev5 v1.9.1） |
| J | 稽核域 retention 與 reporting | rev5:ADR 0077（rev5 v1.10.0） |

跨島刻意不一致（各島 fail-* 方向、島 E 與登入設定鍵缺失的相反方向）與刻意空缺位（rev5 之 I6、J2）之處置，隨各島進場時一併重審、不預裁。

### I.8 AI 代理產物必經人審與機器閘（NON-NEGOTIABLE）

- AI 代理（implementer／review／fix 等一切 agent）的產物——程式碼、文件、帳本條目、拍板文——MUST 同時經**人審**與**機器閘**放行，任一缺席即不得入 default branch。人審＝merge 回 default branch 前 user 的明確同意（當次對話），拍板級項（schema／scope／破紀律／user 可見行為）另需 user 親決，逐 diff 親讀非必要條件；機器閘＝適用於該改動之 `python3 tools/docsync lint`、pre-commit／pre-push、容器內測試。
- review agent **只讀不寫** repo 檔；findings 只以回傳訊息承載。
- `git push`／`git merge` 回 default branch MUST 有 user **明確同意**（當次對話內給出、不得沿用前次）。
- 方向性反轉（免人審入主線、review agent 可寫、agent 自主 push／merge）＝MAJOR。
- 出處＝RAD4AI-report Q11（啟動書 §3.8 新增列）；程序細節（審查輪、findings 三分流、hook 接線）＝`docs/ops/RULES.md`。

---

## II. 設計拍板凍結

隨 §I 未承載的獨立小拍板（拍板現況機器索引＝docs/generated/DECISIONS-INDEX.md）；三筆承襲 rev5 §II、2026-09-03 逐筆核 rev5 ADR 摘要無翻案：

| # | 主題 | 拍板凍結 |
|---|---|---|
| #1 | unknown header | rust-api 忽略不認識的 header（如 apifoxToken）；base-web 不動 |
| #2 | auth route mode | dynamic（後端控 menu；`.env` `VITE_AUTH_ROUTE_MODE=dynamic`、ADAPT 軌道） |
| #3 | prod 路徑前綴 | `/api/*` 主流（front-nginx strip 轉發、`/api/metrics` 擋塊） |

**排程性拍板註記**：排程性結論（何時做／先做哪個）**不預載於本檔**——入波排程時逐筆重審立 ADR；重議既有排程性拍板仍走 §V.2 Amendment、**不得默改**。

---

## III. 軌道授權邊界

**跨軌道 fork-delta 執行紀律**（upstream 常態更新，本紀律使 fork 差異在 rebase 時可快速定位；基線 SHA＝rev5 同 SHA `8be6f9ba`、啟動書 D14）：
- **修改型**（既有行語意被改變）：**原行註解保留**、緊鄰新行之上，含標記（如 `// [rev6-inline <軌道代號>] 原行: ...`）——rebase 衝突塊自含對照基準
- **新增型**（純插入新行／區塊／檔）：插入區塊以 `[rev6-inline ...+]` 標記圈界；新檔僅檔頭一行標記
- **標記統一含 `rev6-inline` token**：全 repo grep 即得完整 fork patch set（upstream 大重構時的災難重建索引）
- **rebase 同步紀律**：解衝突時，註解內「原行」同步更新為 upstream 現行版（防對照基準過時）
- **生成檔紀律**（承 rev5:ADR 0052 條款）：判準＝檔頭帶工具 Generated 標記之機器生成檔（unplugin 元件宣告 `src/typings/components.d.ts` 同族）與 §III.2 表內「路由外掛產物四檔」同族——由工具重算產出、**禁手改**、不逐行標記、不入任何用途之檔級名單；其變更隨引入新元件／新頁之單元同 commit 帶入，審查判準＝diff 只允許工具重算形（宣告行增刪）、出現手寫內容即紅；機器承載＝fork-delta-lint 之檔頭判準（碼面閘、隨子庫刀進場）

### III.1 預設可動軌道（無需額外授權）

| 軌道 | 範圍 | 紀律 |
|---|---|---|
| **BASE-WEB-ADAPT** | `.env*`＋`src/typings/api/` 新檔 | 新增為主；**inline 修改限根層 `.env*` 接管面**（§III.2 表外宣告 2 指定之 devproxy 涵蓋路徑）；禁止刪除既有 type／field |
| **BASE-WEB-WRAPPER** | `src/service/api/rev6-*.ts` 新檔 | 一律新檔（`rev6-` 前綴）；不改既有 service 檔 |
| **RUSTAPI-SOURCE-ISOLATION** | rust-api 整棵樹 | 全新寫；前代受控參照不拷貝（§I.5） |

### III.2 ★ 需 constitution 顯式授權軌道

**本節為 ★ 軌道的凍結位**——每條軌道與其**每一個用途**皆須經 §V.2 Amendment 明文開立；未列於下表者一律無授權（同軌道內的未列用途，不因該軌道已開而自動授權）。**首批軌道隨首刀 Amendment 開立**（user 拍板 2026-09-03：rev5 名冊不預載）。

**機制骨架**（一切 ★ 軌道的共同紀律）：
- ★ 軌道＝base-web inline 的顯式授權邊界：嚴格限本檔已授權之用途／範圍，新用途一律走 §V.2 Amendment
- **補完 vs 新能力判準**：既有授權頁內「單頁、純加、復用既有 wrapper、零新 key/元件/路由」四條件全中的 dispatcher 補完＝**用途補完、不 bump 本檔**；跨多頁新能力＝**須 Amendment**
  - **「零新 key」釋義**（承 rev4:ADR 0041）：指**新 i18n 命名空間／新元件／新路由等「面」級新增**；**不含**既有授權頁、既有子命名空間之下的**資料級 label key**。新增 top-level i18n 命名空間、新元件／路由、跨頁能力仍須 Amendment；判準其餘三條件仍須全中
- 每改一處在 spec 內紀錄（位置＋改動內容＋upstream 衝突風險評估）
- 共用元件改動 MUST 用附加 prop＋安全預設（不變既有呼叫端行為）

**已授權軌道與用途**（機器可解表格；掃描錨＝本表標題列之後、以 `|` 起的資料列，跳分隔列；軌道名以 `**★NAME**` 包覆、掃描端剝 `**` 與 `★`。**授權名冊＝本表 ★ 軌道 ∪ §III.1 三軌道**）：

| 軌道 | 用途 | 範圍（檔案） | 紀律 |
|---|---|---|---|

（空表——尚無 ★ 軌道；首列隨首刀 Amendment 落入。）

**表外三項適用宣告**：
1. 範圍欄的**處數為估值**，實作期以 `rev6-inline` 標記實數為準；**檔級名單則是硬邊界**——名單外的 base-web 既有檔一律無授權，需要動即回本節走 §V.2。
2. devproxy 接管面由 §III.1 `BASE-WEB-ADAPT` 以根層 `.env*` 涵蓋、**不另開軌道**；modal 治理需求隨其頁面接線軌道之用途承載、**不另開專屬軌道**（承 rev5 處置）。
3. 新增型 `NAME+` 標記**不入名冊**（承 rev5:ADR 0021 款 1）——名冊斷言的射程僅修改型（帶 `原行:`）。

**承襲指針**：rev5 憲法 v1.10.0（唯讀、凍結 SHA `7eab28a`）§III.2 曾授權五條 ★ 軌道十七用途（`BASE-WEB-AUTH-WIRING` 三用途／`BASE-WEB-LOGIN-CAPTCHA-WIRING` 二用途／`BASE-WEB-I18N-WIRING` 三用途／`BASE-WEB-LOGOUT-UX-WIRING` 一用途／`BASE-WEB-MANAGE-PAGE-WIRING` 八用途），連同 §III.1 三軌道＝rev5 名冊八條；對應接線需求出現時為 Amendment 提案的直接輸入——base-web 基線與 rev5 同 SHA，範圍欄可逐檔對照，但用途集隨 rev6 刀序重定、不整表照搬。

---

## IV. Compliance Check（spec-kit `/speckit-plan` 用）

`/speckit-plan` 必須對照本 constitution 逐項 yes/no：

1. **此 plan 是否違反 §I.1 base-web 為權威紀律？** rust-api 是否未提供 base-web 用到的對應 endpoint？
2. **此 plan 是否動到 base-web inline？** 若是、屬 §III.2 哪個用途／範圍？授權邊界內？是否依 fork-delta 紀律（修改型原行註解／新增型圈界、`rev6-inline` token）？
3. **此 plan 涉及 menu 顯示是否走 Casbin enforce？**（§I.2；demo menu 是否進 seed 而非隱藏？）
4. **此 plan 的 wire 設計是否對齊 §I.3 權威序與不變式？**（envelope／逐欄位 id 型／13 碼矩陣／msg=key；mock 僅補充 fixture）
5. **此 plan 是否從前代 source 拷貝 code？** 若是、屬 §I.5 例外清單嗎？參照處（§I.5 前代＝rev5、rev4 溯源）是否觸發防回歸條款？
6. **此 plan 是否抵觸 §II 拍板？** 任一拍板需改變、必先走 Amendment
7. **此 plan 是否觸及 §III ★ 軌道？** 若是、在授權邊界內？屬「補完」還是「新能力」（§III.2 判準）？
8. **此 plan 是否新建業務表（create migration）？** 若是，是否含 §I.6 六審計欄（建表即帶、無 retrofit）？append-only／join 表是否依變體處理？
9. **此 plan 是否觸及 §I.7 已入憲的行為島？** 若是、各 invariants 是否保持？是否用 state-machine 鏡頭設計（非 CRUD 格子）？若屬「該入憲而未入憲」的新行為島、是否隨本刀排入 Amendment（候選來源＝§I.7 承襲指針）？

任一檢查不通過 → plan 須回 brainstorm 或申請 Amendment（§V.2）。

註：本題組承接 rev5 九題制；「不增列 push/merge 自查題」為已封案事項、日後不再議——該紀律之方向性條款＝§I.8、程序承載＝CLAUDE.md 硬禁令＋agent prompt 烤入。

---

## V. Governance

### V.1 凍結權威性

本 constitution 為 rev6 的**凍結權威**；與其他文件衝突時**以本檔為準**。文件權威鏈：

> constitution（凍結權威）＞ ADR accepted（拍板全文；索引＝docs/generated/DECISIONS-INDEX.md）＞ docs/ops/RULES.md（規則層）＞ 活書家族 docs/arc42（不含 decisions/）／docs/c4／docs/compliance／docs/process（as-built 敘事）＞ docs/generated/（機器鏡像）

本檔與 accepted ADR 不一致＝Amendment 未同步的程序錯誤，以本檔為準並立即補同步。RULES.md 與 accepted ADR 衝突＝RULES 有誤、就地改 RULES（輕量軌）。

### V.2 Amendment 流程

1. **提案**：立 ADR draft（背景／決定／後果；註明改本檔哪一節）
2. **討論**：user 親決（本檔內容皆為 user 拍板項，Claude 不主動 amend）
3. **凍結**：ADR 轉 accepted＋更新本檔對應段＋bump version（§V.3）
4. **commit**：獨立 commit `docs(constitution): amend <條目>`（憲法改動＋ADR 同 commit）＋`python3 tools/docsync generate`

### V.3 Version 規則

- **MAJOR**（2.0.0）：鐵紀律（§I 原則、含 §I.8 方向性反轉）改變、§I.7 方向性不變式反轉、§II 拍板撤回、★ 軌道授權撤銷
- **MINOR**（1.1.0）：新拍板固化（§II 加項）、軌道授權邊界擴展（新用途／新範圍）、新增 ★ 軌道、**行為島隨刀進場（§I.7 填充）**、已入憲 invariant 細項調整、§I 例外清單擴展（規則方向不變、只擴例外）
- **PATCH**（1.0.1）：文字校正、釐清、reference 更新、Compliance Check 增補

---

**Version**: 1.1.0 | **Ratified**: 2026-09-03 | **Last Amended**: 2026-09-04

**Amendment log**:
- 1.0.0（2026-09-03）：創世初版——自 rev5 constitution v1.10.0（凍結 SHA `7eab28a`）依啟動書 §3.8 逐條表搬入：§I.1～§I.3、§I.6 承襲改字（分支名、基線 SHA、fork 標記 token、前代 ADR 引用一律 `rev5:` 前綴）；§I.4 收為方向性四句、程序細節移 RULES.md；§I.5 世代 bump（前代＝rev5、rev4 溯源、源倉 main `32c5254` 起全新寫）；§I.7 僅搬進場規則、十座行為島以承襲指針表列（rev5 入憲載體逐島註明）、島體隨刀重新進場；§I.8 新增（AI 代理產物必經人審與機器閘、review 只讀、push／merge 需 user 明確同意）；§II 三筆承襲（逐筆核 rev5 ADR 摘要無翻案）；§III fork-delta 紀律與 §III.1 三軌道承襲（token `rev6-inline`、wrapper 前綴 `rev6-`）、§III.2 僅機制骨架＋補完判準＋表外三項宣告＋空表頭、rev5 五條 ★ 軌道十七用途以承襲指針列名；§IV 九題承襲（第 2 題 token、第 5 題前代改引）；§V.1 權威鏈納 RULES.md、§V.2 第 4 步改 `python3 tools/docsync generate`、§V.3 MAJOR 款納 §I.8。user 親審 diff＋grill 三題親決（§I.4 錨定「刀」＝spec-kit feature、§I.8 人審＝merge 同意＋拍板親決、§III.2 宣告 2 改原則句）後定版（創世拍板）。ADR-00003 同 commit 轉 accepted。
- 1.1.0（2026-09-04）：§I.5 例外清單加②資料形狀契約三件整檔拷貝（基線結構 migration＋基線 seed migration＋基線 entity 15 檔；射程鎖 rev5 rust-api `92919b9`；程式逐位元自證、檔名四碼＝ADR-00008、註解語意判準、防回歸照常、`m0003` 起不適用）；§V.3 MINOR 款補「§I 例外清單擴展」釋義。ADR-00009 同 commit accepted（user 拍板：例外射程 2026-09-03、版級 MINOR 與註解語意判準 2026-09-04、Amendment 全文核准 2026-09-04）。
