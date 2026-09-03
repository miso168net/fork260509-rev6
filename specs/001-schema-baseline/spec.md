# Feature Specification: 001 schema 基線（rev5 終態逐位元承襲＋受管演進帳）

**Feature Branch**: `001-schema-baseline`

**Created**: 2026-09-04

**Status**: Draft

**Input**: User description: "docs/brainstorms/001-schema-baseline.md"（階段 0 brainstorm 定稿 2026-09-03、對齊與 grill 修訂 2026-09-04；本 spec 之唯一輸入。該檔 §0 拍板紀錄與 §2／§7 兩 ADR 草案要點為權威來源；SDD 承襲 `rev5:001` 之 data-model 凍結後以 data-model 為欄序權威、brainstorm 轉史料）

> 摘要：rev6 資料庫基線＝rev5 終態 15 表——兩支基線遷移（結構＋seed 定稿）**內容逐位元承襲、檔名依 ADR-00008 四碼**；
> 承襲走憲法 §I.5 例外 Amendment（ADR-00009、MINOR 1.1.0）四條件紀律。同刀就位 rust-api workspace 骨架、
> 受管演進帳三閘＋entity 漂移閘、照相與兩張參考真表、Day-1 常設程序；schema 基線與閘契約立 ADR-00010。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 基線結構與 seed 逐位元承襲落地 (Priority: P1)

作為 workspace 維護者，我要 rev6 資料庫基線＝rev5 終態 15 表：結構基線遷移與 seed 基線遷移的程式內容
與 `rev5:m001`／`rev5:m002` 逐位元相同（去註解後 diff 零差異）、檔名改為四碼短號（`m0001_`／`m0002_`）、
註解全數以 rev6 語境重寫；rust-api workspace 骨架（migration／entity／adapter 三 member）同刀就位。
使後續一切功能刀建立在與 rev5 完全同形的 schema 起點上，UI 對照驗收（rev5 stack 全等）才有資料面前提；
rev6 第一支 delta 自 `m0003` 起編。

**Why this priority**: 沒有結構與 seed 基線，rust-api 首批程式工件與一切後續刀都無地基；rev5 定稿制成果
（欄序親排、seed 全量過目簽核）已由 user 拍板「照抄、不重開工作坊」，逐位元承襲是零資訊損失的唯一路徑。

**Independent Test**: 對一次性 pristine 資料庫重放 rev6 兩支基線遷移，自實庫萃取結構與 seed 定稿 fixtures，
與 rev5 同名凍結 fixtures 逐位元比對——不需閘工具、不需任何後續刀即可獨立驗證並交付價值。

**Acceptance Scenarios**:

1. **Given** rev5 rust-api 凍結版（SHA `92919b9`）之 `rev5:m001`／`rev5:m002` 與 rev6 之 `m0001_`／`m0002_`
   兩支，**When** 兩邊去註解後逐檔 diff，**Then** 零差異（機器自證、命令與結果記入 ADR-00009 證據段與 commit 訊息）。
2. **Given** 一次性 pristine 資料庫，**When** 容器內重放 rev6 兩支基線遷移，**Then** 實庫 15 表結構
   （169 欄、索引 38、約束 101）與 seed（266 列＋9 空表、明示 id＋sequence 落值）成形；`seaql_migrations`
   記錄的遷移名為四碼新名。
3. **Given** 自 rev6 pristine 萃取之 columns／constraints／indexes／seed 四份 fixtures，**When** 與 rev5 同名
   fixtures 逐位元比對，**Then** 四檔零差異（`seaql_migrations` COPY 段依承襲契約剝除、四碼改名不影響全等）；
   任一不全等＝停手升級 user、禁止單源逕行定稿。
4. **Given** rust-api workspace 骨架（三 member、toolchain 與 dev 映像同版、格式設定承 rev5、lockfile 入版控），
   **When** 容器內 serial 建置，**Then** 建置綠；server 不在場、dev stack 只起資料庫服務即可完成本刀全部驗證。

---

### User Story 2 - 拷貝例外開立與承襲紀律 (Priority: P1)

作為 workspace 維護者，我要在任何拷貝碼落地之前，先以憲法 §V.2 Amendment 把「資料形狀契約三件整檔拷貝」
列入 §I.5 例外清單（ADR-00009 accepted、版本 1.0.0→1.1.0），並以四條件（逐位元自證、註解重寫、防回歸審查、
seed 固定值紀律）約束整個承襲過程，使本刀是「依規則的例外」而非「破紀律」。

**Why this priority**: 憲法 §I.5 明文「拷貝禁止」，例外必先於行為開立；否則 plan 之 Compliance Check 第 5 題
無法通過、review agent 亦無依據放行。與 US1 同為 P1——US1 是價值、US2 是其合法前提。

**Independent Test**: 憲法版本與 §I.5 例外句、ADR-00009 狀態、以及 lint 對子庫 pin 樹的裸前代編號掃描
（GT-05）可各自機器驗證；四條件中的自證 diff 與防回歸清單為可檢視的文件證據。

**Acceptance Scenarios**:

1. **Given** feature 分支已開、specify 之 auto-commit 已落，**When** 落第一顆手動 commit，**Then** 該 commit＝
   ADR-00009 accepted＋憲法 §I.5 例外句＋版本 1.1.0＋§V.3 MINOR 句補「§I 例外清單擴展」＋生成物重算；
   早於 `/speckit-plan`。
2. **Given** 17 檔已拷入並註解重寫，**When** 跑 lint（GT-05 掃 tools/ 與子庫 pin 樹），**Then** 零裸前代編號
   （rev5 原 m001 之兩處裸 `rev4:m009`／`rev4` 引用、entity 六檔各一處前代引用皆已帶前綴或改寫）。
3. **Given** entity 15 檔為 rev5 終態版，**When** 逐檔防回歸審查，**Then** 後刀差異清單在案（唯一差異＝
   `sys_user_role` 兩條真 DB FK 關聯宣告、形狀派生、保留）、零 rev6 已推翻行為帶回；紀錄入 ADR-00010 證據段。
4. **Given** seed 固定值（三帳共用 PHC 常數、定稿時戳）為定稿字面，**When** 機密掃描器命中，**Then** 依
   allowlist 紀律逐條收錄＋雙向突變實證（加豁免→通過、拔豁免→回到命中），絕不 `--no-verify`；未命中則零 allowlist。

---

### User Story 3 - 驗證閘＝Day-1 受管演進帳 (Priority: P2)

作為 workspace 維護者，我要 schema 驗證閘自 Day-1 起採「凍結面＋演進登記」合成期望值、與實庫**全等**比對的契約——
未登記漂移一律紅；每支帶 migration 的刀必跑照相＋登記，成為常設程序。承 `rev5:001` 已驗證契約、寫進 ADR-00010。

**Why this priority**: 閘是基線的保鮮機制；沒有它基線落地即開始腐化。依賴 US1 的定稿產物存在，但可獨立往返驗證。

**Independent Test**: 對就位後的閘做往返驗證——注入未登記漂移必紅、補登記後轉綠、登記檔格式破損時啟動斷言
fail-loud、登記一筆假 delta 後合成期望值案必紅——不需任何後續刀即可獨立驗證。

**Acceptance Scenarios**:

1. **Given** 凍結 fixtures＋空演進登記檔，**When** 三閘（結構全等／欄序＋seed／archetype 歸屬）對基線實庫全跑，
   **Then** 全綠。
2. **Given** 實庫注入一筆未登記漂移（新欄／改型別／seed 改值／sequence 落值任一），**When** 閘執行，**Then**
   紅且指明漂移位置（negative test、比對器先自證）。
3. **Given** 該漂移補入演進登記檔（帶來源刀編號），**When** 閘再執行，**Then** 合成期望值後全等、綠。
4. **Given** 登記檔缺欄位或來源刀編號格式錯誤，**When** 閘啟動，**Then** 啟動斷言 fail-loud、不得靜默通過。
5. **Given** rev5 之演進登記檔終態零筆（合成邏輯從未吃過真 delta），**When** 本刀自測，**Then** 含「登記一筆
   假 delta 後合成期望值」案且行為正確。
6. **Given** 兩支閘工具自 rev5 整檔搬運，**When** 改 rev6 座標、去 rev5 專屬子命令與 rev4 對賬殘留、註解重寫，
   **Then** 自帶單元測試逐案綠、GT-05 綠；工具不入 docsync 行數、不入 GT 名冊（碼面閘）。

---

### User Story 4 - entity 對應層與漂移防線 (Priority: P3)

作為 workspace 維護者，我要 15 表的 entity 對應層（承襲 rev5 終態版、註解重寫）與 entity-drift 雙向比對
（快照 vs 對應層之表／欄／型／可空）就位，pre-commit 常跑、秒級、零 docker；快照缺席時為 Day-1 跳過、
快照就位即自動實跑，使帳面與程式側的漂移在 commit 時即被攔下。

**Why this priority**: 防線與 entity 是後續 server 刀的直接輸入；價值真實但依賴 US1 的 schema 與 US5 的快照。

**Independent Test**: 對應層在場＋快照一致→綠；刻意改一欄型別→紅；觸發面內 entity 目錄缺席→commit 被擋。

**Acceptance Scenarios**:

1. **Given** entity 15 檔就位且與 schema 快照一致，**When** pre-commit 執行，**Then** entity-drift 綠。
2. **Given** 快照尚未就位，**When** pre-commit 執行，**Then** 印出 Day-1 跳過訊息、不擋；快照就位後同一步驟自動實跑。
3. **Given** 觸發面（staged 含 rust-api gitlink 或 schema 快照）內 entity 目錄缺席，**When** commit，**Then**
   被擋（fail-loud、不得降級為警告）。

---

### User Story 5 - 參考真表與 DoD 鏈 (Priority: P4)

作為 workspace 維護者，我要「查現況」的 schema／accounts 兩張參考真表自實庫照相首算就位（照相＝docsync
`refresh` 子命令、真表＝generate 重算），archetype 歸屬登記初版就位，RUNBOOK 常設程序與 README 工具行
補齊，整條 DoD 鏈全綠（pre-commit、三閘、GT-01／GT-09／GT-12）。

**Why this priority**: 收尾防線與查表可信度；依賴前四個 story 的產物齊備。

**Independent Test**: 照相→兩快照→generate→兩真表→lint／pre-commit 逐環可觀察綠／紅產物。

**Acceptance Scenarios**:

1. **Given** 基線實庫就位（dev stack 只起資料庫服務），**When** 照相首跑＋真表重算，**Then** 兩快照與兩張真表
   就位、內容與定稿一致、生成物名冊 12→14 且 GT-01 零漂移。
2. **Given** archetype 歸屬登記初版（15 表 × 憲法 §I.6 四變體、人寫轉錄），**When** audit 閘逐表驗，**Then** 15/15 綠。
3. **Given** RUNBOOK 常設程序節與工具速查兩列、README 樹兩支工具行已補，**When** GT-09 對賬，**Then** 綠。

---

### User Story 6 - 治理與帳本落帳 (Priority: P5)

作為 workspace 維護者，我要本刀的拍板與衍生工作在對的家落帳：ADR-00010（schema 基線與閘契約）accepted、
BL-00001 於開分支後首個 Workflow 前消化（編排骨架三變體收斂）、BL-00005 於收刀前處置（事件欄無家群、拍板級）、
活書對應節與 rev5 藍本圖 05 列同批更新、首條 LESSONS 落地解除 GT-08 Day-1 豁免。

**Why this priority**: 帳本正確是收刀放行條件（GT-03／GT-04／GT-05），但不阻擋前五個 story 的技術價值交付。

**Independent Test**: lint 全綠＋收刀事件引用之 spec／ADR 存在（GT-03 首次實跑）即為驗證。

**Acceptance Scenarios**:

1. **Given** 刀分支，**When** 首個 Workflow 派發前，**Then** BL-00001 已消化（單一常數家與單一骨架）並在 BACKLOG 標記完成。
2. **Given** 收刀前，**When** 處置 BL-00005，**Then** 事件欄無家群之去留由 user 親決（補渲染或刪欄），必要時立 ADR-00011。
3. **Given** 收刀簿記，**When** 寫首筆 `feature_close` 事件（window＝1、adrs＝ADR-00009／ADR-00010），**Then**
   GT-03 驗 `specs/001-schema-baseline/spec.md` 與兩 ADR 存在、綠。

---

### Edge Cases

- **雙源互證分歧**：rev6 pristine 萃取之 fixtures 與 rev5 凍結 fixtures 任一檔不全等 → 停手升級 user，
  禁止單源逕行定稿（US1 場景 3）。
- **「去註解後 diff 全等」的判準**：註解＝行註解與文件註解（`//`／`///`／`//!`）；屬性巨集與字串字面屬程式
  內容、不得改動；空白與行尾規則以 rev5 已 `cargo fmt` 之存量為準。
- **遷移改名的副作用**：改四碼後遷移登記表記錄的名稱與 rev5 不同——該表 COPY 段本就依承襲契約自 seed
  fixtures 剝除，不影響全等；ADR-00008 翻案觸發器（改名破雙源互證）實證不成立。
- **entity 終態版之後刀差異**：唯一差異為 `sys_user_role` 真 DB FK 關聯宣告；屬形狀派生、保留；若審查再發現
  形狀外行為（rev6 已推翻者）→ 去除並記錄，不得靜默帶回。
- **前代裸編號走私**：拷入註解重寫漏改 → GT-05 紅；先掃後 commit。
- **機密掃描命中**：`.gitleaks.toml` 預告的兩條皆落本刀（adapter 測試碼假 DSN、收刀事件 40-hex SHA）；
  逐條 allowlist＋雙向實證；seed PHC 常數在 rev5 零 allowlist 即通過、預期不命中。
- **演進登記檔破損**：缺欄、格式錯、來源刀編號不合規 → 閘啟動斷言 fail-loud。
- **entity 對應層半缺**：目錄缺席或表數不足 → 於觸發面內一律擋 commit；不得降級為警告。
- **server 缺席**：本刀 dev stack 的 rust-api 服務起不來屬預期；一切驗證只起資料庫服務、不等待全體健康。
- **rev5 側唯讀紀律**：一切讀取對凍結 worktree；絕不寫入、不動其 stack 之 schema／seed／設定。

## Requirements *(mandatory)*

### Functional Requirements

**基線承襲**

- **FR-001**: rev6 資料庫基線 MUST 為 rev5 終態 15 表：結構基線遷移＋seed 基線遷移兩支，程式內容（去註解後）
  與 `rev5:m001`／`rev5:m002` 逐位元全等；檔名 MUST 依 ADR-00008 為四碼（`m0001_baseline_schema`／
  `m0002_baseline_seeds`）；rev6 第一支 delta 自 `m0003` 起編。
- **FR-002**: seed 基線 MUST 完全決定性：三帳共用 PHC 常數與 `created_at` 定稿時戳字面照 rev5 原值（改值即破全等）；
  重放結果 MUST 與凍結 fixtures 逐列全等、比對器 MUST NOT 為任何欄開豁免洞（承 `rev5:FR-016`）。
- **FR-003**: 凍結 fixtures（columns／constraints／indexes／seed＋provenance）MUST 自 rev6 自己的 pristine 重放萃取、
  與 rev5 同名 fixtures 逐位元比對全等＝雙源互證；`seaql_migrations` COPY 段與隨機 token 行依承襲契約剝除；
  不全等 MUST 停手升級 user。
- **FR-004**: rust-api workspace 骨架 MUST 就位：三 member（migration／entity／adapter）、toolchain 版本＝dev 映像同值、
  格式設定三值承 rev5、lockfile 入版控；依賴首刀子集首源＝rev5 lockfile、次源＝官方最新穩定版，同值採、異值問 user；
  建置與測試 MUST 容器內、全程 serial；server 不入。

**拷貝例外與紀律**

- **FR-005**: 任何拷貝碼落地之前 MUST 先完成憲法 Amendment：ADR-00009 accepted＋§I.5 例外清單加「資料形狀契約三件」
  句＋版本 1.0.0→1.1.0（MINOR、依據＝類比 §V.3「軌道授權邊界擴展」、同批補 §V.3 MINOR 句「§I 例外清單擴展」）；
  時點＝specify auto-commit 之後、clarify 之前的第一顆手動 commit。
- **FR-006**: 承襲 MUST 滿足四條件：①逐位元自證（去註解後 diff 全等、命令與結果入 ADR 證據段與 commit 訊息）
  ②註解一律重寫為 rev6 語境、前代出處帶 `rev5:`／`rev4:` 前綴（GT-05 掃 tools/ 與子庫 pin 樹綠）③防回歸審查逐檔
  列後刀差異、屬形狀外者去除並記錄 ④seed 固定值＝定稿字面非機密（承 `rev5:ADR 0003`）、掃描命中才 allowlist
  且雙向實證、絕不 `--no-verify`。
- **FR-007**: 例外射程 MUST 限 17 檔（兩支基線遷移＋entity 15 檔）、鎖 rev5 rust-api 凍結 SHA `92919b9`；
  adapter crate 為既有例外；遷移與 entity 之 crate 入口檔 MUST 自寫；`m0003` 起 delta 與一切業務碼 MUST NOT 適用例外；
  日後第 18 檔要拷＝新 Amendment。

**驗證閘＋演進帳**

- **FR-008**: schema 閘契約 MUST 為 Day-1 受管演進帳：凍結面（`specs/001-schema-baseline/fixtures/`、永不改寫、
  翻案＝新 ADR supersedes）＋演進面（`docs/ops/reference-src/schema-evolution.json` 單一登記檔、kind 枚舉八值、
  每筆帶來源刀編號、初版零筆）合成期望值後與實庫**全等**——非容差；未登記漂移一律紅；登記檔 MUST 有啟動斷言。
- **FR-009**: 三閘 MUST 就位並先自證：結構全等／欄序（vs data-model 定稿）＋seed（vs 凍結 fixtures）／
  archetype 歸屬 15 表逐表驗；negative test MUST 含結構、欄序、seed 值、sequence 落值各至少一例假漂移必紅，
  以及「登記一筆假 delta 後合成期望值」案。
- **FR-010**: 兩支閘工具 MUST 依「隨遷工具」紀律自 rev5 整檔搬運：改 rev6 座標、去 rev5 專屬子命令與 rev4 對賬殘留、
  註解全數重寫、自帶單元測試逐案綠；不入 docsync 行數、不入 GT 名冊（碼面閘、閘數恆 12）；staged 含工具本體時
  pre-commit 條件自測。
- **FR-011**: 「每支帶 migration 的刀必跑照相＋演進帳登記」MUST 入 RUNBOOK 常設程序節（現有四碼短號指針句之後補實文）。

**entity 與 DoD 鏈**

- **FR-012**: entity 對應層 MUST 覆蓋 15 表（承襲 rev5 終態版、註解重寫）；entity-drift MUST 為快照 vs 對應層之
  雙向比對（表／欄／型／可空）、pre-commit 常跑、秒級、零 docker；快照缺席＝Day-1 跳過、就位即實跑；觸發面內
  entity 目錄缺席 MUST 被擋（fail-loud）。
- **FR-013**: DoD 鏈 MUST 依序完成：照相首跑（dev stack 只起資料庫服務）→ 兩快照就位 → generate → 兩張參考真表
  （生成物名冊 12→14）→ pre-commit 全綠（entity-drift 由跳過轉實跑）→ 三閘綠 → GT-01 零漂移、GT-09 對賬綠、
  GT-12 預算內。
- **FR-014**: archetype 歸屬登記初版 MUST 就位：15 表 × 憲法 §I.6 四變體、人寫轉錄自 data-model；真表由 generate 產。
- **FR-015**: data-model 與 contracts 三檔 MUST 以 `rev5:001` 同名檔為底整檔承襲改座標（文件非碼、§I.5 不及；
  帶 `rev5:` 前綴）、與 fixtures 對賬；閘工具解析之表體形制 MUST 保持不變。

**治理與帳本**

- **FR-016**: ADR-00010（schema 基線＝rev5 終態逐位元承襲＋受管演進帳閘契約）MUST 於刀內落地 accepted；
  收刀 `feature_close` 事件 adrs＝ADR-00009／ADR-00010。
- **FR-017**: BACKLOG 時點 MUST 兌現：BL-00001 於開分支後首個 Workflow 前消化（Task 0）；BL-00005 於收刀前處置
  （拍板級、user 親決）；BL-00002 本刀不觸發（兩 ADR 非 AI-ADR）；收刀 append 一條「STATE 預算表納 docsync 行數對賬」。
- **FR-018**: 活書 MUST 同刀更新：建構視圖 rust-api 句與樹列、資料慣例節指針句（schema 真表家）、rev5 藍本圖 05 列
  「隨刀」→「承襲」；README 樹加兩支工具行；C4-L2 拓樸不變零改；首條 LESSONS 落地即解除 GT-08 Day-1 豁免。

### Key Entities

- **基線 schema（15 表、169 欄）**: 14 親排表＋casbin 規則表；欄序／rename map／索引 38／約束 101 全承 rev5 定稿制成果。
- **兩支基線遷移**: 結構基線（`m0001_`）與 seed 基線（`m0002_`）；內容逐位元承襲、檔名四碼、註解 rev6 語境。
- **凍結 fixtures（凍結面）**: 結構三份＋seed 定稿＋provenance；自 rev6 pristine 萃取、與 rev5 雙源互證；永不改寫。
- **演進登記檔（演進面）**: 跨刀單一登記檔；每筆帶來源刀編號；初版零筆。
- **archetype 歸屬登記**: 15 表 × 憲法 §I.6 四變體之歸屬帳；真表由 generate 產。
- **entity 對應層**: 15 表之程式側對應（承襲）；entity-drift 比對之一側。
- **參考真表與快照**: schema／accounts 兩快照（照相產物）與兩張參考真表（重算產物）；「查現況」正典入口。
- **憲法例外清單項**: 「資料形狀契約三件整檔拷貝」（射程 17 檔、鎖 `92919b9`）；ADR-00009 承載。
- **data-model 定稿文件**: 承襲 `rev5:001` 同名檔改座標；欄序權威、閘工具解析源。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 17 檔去註解後 diff 逐檔零差異；自證命令與結果在 ADR-00009 證據段與對應 commit 訊息中可查。
- **SC-002**: rev6 pristine 萃取之四份 fixtures 與 rev5 同名 fixtures 逐位元零差異（含 id 欄與 sequence 落值、
  PHC 常數與定稿時戳）。
- **SC-003**: 比對器自證通過：假漂移（結構、欄序、seed 值、sequence 落值、假 delta 登記）各至少一例全數必紅、零漏報。
- **SC-004**: 演進帳往返驗證通過：未登記漂移→紅；補登記→綠；登記檔破損→啟動斷言 fail-loud。
- **SC-005**: DoD 鏈全綠：兩快照與兩真表就位、生成物名冊 14、entity-drift 實跑綠、entity 目錄缺席演練被擋、
  三閘綠、GT-01／GT-09／GT-12 綠、閘數 12 不變。
- **SC-006**: 治理全綠：憲法 1.1.0、ADR-00009／ADR-00010 accepted、lint 零錯（GT-03／GT-04／GT-05 含子庫 pin 樹）、
  BL-00001 與 BL-00005 消化紀錄在案、首條 LESSONS 落地。
- **SC-007**: pre-commit 全鏈實測 ≤45 秒（雙錨警戒線）並記 perf 事件；docsync 行數落點記錄（現值 2,345、預期約 2,600、
  ≤4,000 為啟動書目標而非閘）。

## Assumptions

- rev5 為本機可達之唯讀參考庫（工作區同層 `../fork260509-rev5/`、凍結 SHA 外層 `7eab28a`／rust-api `92919b9`，
  由 bootstrap 斷言）；一切讀取不寫入。
- 容器化資料庫可起一次性 pristine 實例（獨立網路、零 host 埠、用畢即拆）；rust 建置／測試一律容器內、全程 serial。
- dev 帳號 Super／Admin／User 與 seed 內容同 rev5；資料庫名 `soybean_admin_rust` 已是兩代 compose 事實（不問）；
  定稿時戳字面照舊——前兩項待 clarify 確認、預期皆「是」。
- 憲法 Amendment 版級＝MINOR 1.1.0（user 拍板 2026-09-04）；「首刀」釋義＝首個觸及該面的刀，本刀零 base-web inline、
  零狀態機，不開 ★ 軌道、不入行為島（plan §IV 第 7／9 題答「否」）。
- rust-fmt-gate 隨 002 server 刀進場（本刀 rust 碼全為逐位元拷自 rev5 已格式化存量）；fork-delta-lint 隨首個 base-web 刀。
- 依賴版本以 rev5 lockfile 現值為首源（sea-orm 1.1.20、tokio 1.53.1、async-trait 0.1.89、casbin 2.20.0、rust 1.96.1），
  次源官方最新穩定版；異值於 research 提問。
- 本刀非一次性遷移（pristine 建庫、無既有資料搬移），Risk／Guard／Rollback 三欄表免附。
- 兩支閘工具與其解析之 data-model 表體形制承 rev5 不變；閘語意「全等、非容差」不允許翻案（改容差須 ADR）。

### Out of Scope

- server crate／router／回應信封／一切業務邏輯（002 起）；wire-schema（server 在場才有意義）。
- xdb 工具性 crate（rev5 dev 尾巴）；reaper DB role／GRANT（deploy 面、非 migration）。
- rust-fmt-gate（隨 002）、fork-delta-lint（隨首個 base-web 刀）；行為島（本刀無狀態機）。
- 任何新能力面 schema 設計（本刀＝承襲，零新設計夾帶）；`m0003` 起 delta。
- 走查基準 snapshot／diff 工具（隨首個需 UI 走查的刀遷入）。
