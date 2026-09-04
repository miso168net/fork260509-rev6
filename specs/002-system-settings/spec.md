# Feature Specification: 002 系統設定讀寫（server 進場首刀縱切管線）

**Feature Branch**: `002-system-settings`

**Created**: 2026-09-05

**Status**: Draft

**Input**: User description: "docs/brainstorms/002-system-settings.md"（階段 0 brainstorm 定稿 2026-09-05、grilling round 同日；本 spec 之唯一輸入。該檔 §0 拍板紀錄 Q1～Q8 與方案 A、§3 設計十一節為權威來源；rev5 對應刀 `rev5:002-system-settings` 之 spec 為沿用形之藍本、rev6 座標改寫）

> 摘要：立 rust-api server crate（workspace 第四 member），打通「路由→授權→handler→設定值 registry 驗證→facade→回應信封→前端接線層」
> 整條縱切管線；功能面＝系統設定**讀（一次回 16 鍵）＋寫（單鍵更新、三態部分更新）**；前端腿恰兩新檔（typings＋service）、view 與真登入不入。
> 同刀完成治理進場：三支碼面閘隨遷入 pre-commit、碼面閘名冊定形、msg key 後端側閉環、ADR 五筆；零 migration、憲法零 Amendment。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 讀端管線全通：R_SUPER 讀取全部系統設定 (Priority: P1)

作為 workspace 維護者（以 R_SUPER 身分操作），我要經 API 一次取得全部 16 鍵系統設定（鍵／型別／現值／說明），
使自後端首批程式工件起，「路由→授權→handler→資料庫→信封→前端接線層」每一環都有真實流量通過並可獨立驗證；
rev6 第一條後端管線自此存在。

**Why this priority**: 本刀是 rev6 第一把功能刀，讀端是管線存在性的最小證明；沒有讀端全通，寫端與一切後續功能刀都無地基。

**Independent Test**: 僅實作讀端即可端到端驗證——起 dev stack、以 R_SUPER 測試態身分呼叫讀取端點、比對回包與 seed 定稿全等；
不需寫端即交付「管線可用」價值。

**Acceptance Scenarios**:

1. **Given** seed 基線 16 鍵在庫、全部預設業務件起得齊，**When** R_SUPER 身分呼叫讀取端點，**Then** 回應信封 `{data, code:"0000", msg}`、
   data 含 16 鍵完整清單（settingKey／settingType／settingValue／description），內容與 seed 定稿逐鍵全等、以 settingKey 升冪穩定序；僅回未刪列。
2. **Given** 前端接線層新檔（typings＋service），**When** 以其宣告型別消費回包，**Then** 逐欄位型別對齊、零手工轉換；
   自 typings 抽出的契約快照對後端序列化輸出裁判全過。
3. **Given** R_ADMIN 身分（政策無讀取授權），**When** 呼叫讀取端點，**Then** 授權拒絕（`5003`、HTTP 403）、data 不含任何設定內容。

---

### User Story 2 - 寫端合法路徑：單鍵更新落庫 (Priority: P2)

作為 workspace 維護者（R_SUPER），我要更新單一設定鍵的值，值經逐鍵型別／範圍驗證通過後落庫，回讀即得新值，
且審計欄（updated_at／updated_by）成對記錄操作者——使寫路徑與設定值 registry 自首刀即有真實消費者。

**Why this priority**: 寫端是 registry 存在的理由；「第一支寫端落地即隱含定死」的三態約定與授權語意必須在本刀顯式定形（brainstorm Q1）。
依賴 US1 的管線但可獨立驗收。

**Independent Test**: 合法更新後回讀比對新值＋審計欄成對非空；同值再寫亦成對更新（last-write-wins 一致），不需其他功能面即閉環。

**Acceptance Scenarios**:

1. **Given** number 型鍵（如 password_min_length、範圍宣告內），**When** R_SUPER 提交合法新值，**Then** `0000`、落庫、回讀一致、
   updated_at 與 updated_by 成對寫入（操作者取自請求身分）。
2. **Given** number 型鍵，**When** 提交等價但非正規形的值（前導零、前後空白、正號），**Then** 落庫為正規形（trim→整數解析→界內→正規字面）。
3. **Given** enum:on,off 型鍵（如 single_session_default），**When** 提交值域內另一值，**Then** `0000`、落庫、回讀一致；值大小寫敏感、正規形＝原值。
4. **Given** 已落庫之值，**When** 以相同值再次提交，**Then** `0000`、updated_at／updated_by 仍成對更新為本次操作（不視為 no-op）。

---

### User Story 3 - 寫端驗證失敗路徑：非法值拒收、不寫入 (Priority: P2)

作為 workspace 維護者，我要非法寫入（型別不符／超範圍／enum 外值／未知鍵／欄缺席或壞形）被 registry 一律拒收且**不落庫**，
回包帶業務驗證錯誤碼與穩定訊息鍵，使設定值的完整性由機器把關、驗證失敗路徑與成功路徑同等被契約測試覆蓋。

**Why this priority**: 驗證失敗路徑是 registry 的另一半；與 US2 同刀落地才構成完整寫端。

**Independent Test**: 逐型別注入非法值、斷言拒收碼與原值保留；registry 每型有紅綠對（合法過／非法拒），比對器自證。

**Acceptance Scenarios**:

1. **Given** number 型鍵，**When** 提交非數值字面、小數、溢位或超出該鍵宣告範圍的值，**Then** 業務驗證錯誤（`2222`、HTTP 200 信封）、
   庫中原值保留、msg 為穩定 i18n key。
2. **Given** enum:on,off 型鍵，**When** 提交值域外的值（含大小寫不同者），**Then** 同上拒收、原值保留。
3. **Given** 請求中 settingKey 不在 registry 宣告集，**When** 提交更新，**Then** 拒收（未知鍵、`2222`）、零寫入。
4. **Given** 請求 body 缺 settingKey 或 settingValue、或其型別非字串、或 JSON 壞形，**When** 提交，**Then** 拒收（`2222`）、零寫入。
5. **Given** 庫中某列 setting_type 為 registry 不認識的型別字面（資料完整性異常、正常營運不可達），**When** 該列被讀寫路徑觸及，
   **Then** fail-loud 內部錯誤（`5000`、HTTP 200 信封）、絕不靜默略過或當作合法。

---

### User Story 4 - 越權與身分：授權骨架與拒絕語意定形 (Priority: P2)

作為 workspace 維護者，我要「有按鈕權限、無寫端政策」的角色（seed 已保證 R_ADMIN 持 user:edit 鈕而無任何設定域政策）
呼叫兩端點時被正確拒絕，且拒絕語意與錯誤明細粒度以刀內 ADR 定死；登入未到位期間以 dev-only 測試態身分頂替，
使最小授權骨架自首刀即以真實組合驗證、003 接真 session 時只換驗證器內部。

**Why this priority**: 授權面是縱切管線的一環；「第一支寫端落地即隱含定死」拒絕語意，不在本刀顯式定形＝默拍。

**Independent Test**: 以 R_ADMIN／R_SUPER／未認證三身分對兩端點打授權矩陣，斷言碼與明細粒度符合 ADR 定稿；不依賴其他功能面。

**Acceptance Scenarios**:

1. **Given** R_ADMIN 身分（casbin seed 現況：有 user:edit 鈕、無設定域任何政策），**When** 呼叫寫端，**Then** 授權拒絕
   （`5003`、HTTP 403）、回包 msg 為純 i18n key、不揭露缺哪條政策或持有哪些角色；庫中零寫入。
2. **Given** 授權判定，**When** 任一端點執行授權檢查，**Then** 判定收斂於單一純函式進入點、每請求向資料庫取現行政策，
   且存在空 no-escalation 掛點（本刀恆放行、不實作其邏輯）。
3. **Given** 請求未攜 `Authorization` 標頭、或非 Bearer 形、或 token 不在測試態查表，**When** 呼叫任一業務端點，**Then** 拒絕、`8888`
   （HTTP 200 信封）、data 零內容。
4. **Given** 測試態身分對應之使用者其角色已被軟刪或停用，**When** 呼叫業務端點，**Then** 視同無該角色→授權拒絕（`5003`）。

---

### User Story 5 - 部分更新三態語意：約定層定形 (Priority: P3)

作為 workspace 維護者，我要部分更新的三態語意（欄位缺席＝不動／顯式清空＝JSON null／設值）在 wire 契約上有通用約定（envelope 級）
且於本刀寫端具象驗證：nullable 欄（description）三態俱全、NOT NULL 欄（settingValue）顯式清空＝非法拒收——
使「第一支寫端」不以未定義語意隱含定死全 repo 的部分更新行為。

**Why this priority**: 本刀是第一個寫端＝定形時點；價值真實但依賴 US2／US3 的寫端先在。

**Independent Test**: 對 description 欄打三態矩陣（缺席／清空／設值／空字串）＋對 settingValue 打「顯式清空非法」案，斷言落庫效果與拒收碼；自成閉環。

**Acceptance Scenarios**:

1. **Given** 更新請求中 description 欄缺席，**When** 提交，**Then** 庫中 description 原值不動、其餘提交欄正常生效。
2. **Given** 更新請求對 description 欄顯式清空（該欄 JSON 值 `null`），**When** 提交，**Then** 庫中 description 落 NULL。
3. **Given** 更新請求 description 欄為空字串，**When** 提交，**Then** 庫中 description 為空字串（設值，非清空）。
4. **Given** 更新請求對 settingValue（NOT NULL 欄）顯式清空，**When** 提交，**Then** 業務驗證拒收（`2222`）、零寫入。

---

### User Story 6 - 治理進場與帳本落帳 (Priority: P4)

作為 workspace 維護者，我要在 server 首支程式碼落地前，把三支碼面閘（rust 格式、wire 契約快照、fork-delta 標記）自 rev5 隨遷入 pre-commit、
碼面閘名冊定形於 RUNBOOK 並由 GT-12 機器對賬、entity 漂移段快照缺席改即紅、pre-commit 與 README 對 schema-frozen 觸發面的失準修正、
「碼面閘」入 RULES 名詞段；並於刀內立五筆 ADR、兌現三條 BACKLOG 觸發項、活書同刀更新——
使 002 期間手寫 rust 碼與 base-web 新檔自第一行起就有機器守門，且每筆拍板都有家。

**Why this priority**: 治理項與功能可分開驗收，但 brainstorm 方案 A 拍定「全落 002 內、首單元」——它是功能單元的前置，不是收尾。

**Independent Test**: 三支碼面閘各做一次非 vacuous 自證（案綠→打壞判準→案紅→還原）、hook 面真演練（移走快照→commit 被擋→還原）、
GT-12 新腿一正一反、errata 復掃零殘留；不需任何 server 碼即可驗收。

**Acceptance Scenarios**:

1. **Given** 三支碼面閘隨遷落地，**When** 各自跑自帶測試與一次打壞判準的演練，**Then** 自測綠、演練紅並指名、還原後綠；
   fork-delta 對 rev6 空 ★軌道表不誤紅（哨兵句在＝綠、哨兵句被移除＝紅）。
2. **Given** pre-commit 六處改動落地，**When** 移走 schema 快照後嘗試 commit，**Then** entity-drift 段以非零退出擋下並印補救提示；
   還原後 `git status --porcelain` 零差異。
3. **Given** RUNBOOK 碼面閘表與 GT-12 新腿，**When** 表內少列一支存在的閘工具、或多列一支不存在的，**Then** lint 紅並指名；對齊後綠。
4. **Given** 失準修單，**When** 以 errata 枚舉「schema-frozen」，**Then** 全 repo 零處仍寫舊觸發面。
5. **Given** 五筆 ADR 與名詞段定義，**When** 收刀，**Then** ADR 皆 accepted、RULES-VERSION 已 bump、BL-00008／BL-00010／BL-00011 於收刀事件 `backlog_done`。

---

### Edge Cases

- **併發同鍵更新**：兩請求同時更新同鍵 → 單鍵更新原子、last-write-wins、審計欄記最後寫入者；不設樂觀鎖（16 鍵低頻治理面）。
- **同值更新**：提交值＝庫中現值仍照寫 updated_at／updated_by（US2 場景 4）；不做 no-op 短路。
- **軟刪列觸及**：16 鍵 seed 皆未刪、本刀無刪除端點，deleted_at 非 NULL 態正常營運不可達；防禦性處置＝讀端不回、寫端視同未知鍵拒收（不為不可達態新增碼面）。
- **角色軟刪或停用**：授權判定只認未刪且啟用的角色；測試態身分掛的角色被軟刪或停用＝視同無該角色（US4 場景 4）。
- **未知型 fail-loud**：庫中 setting_type 字面不在 registry 認識集 → `5000`（US3 場景 5）；registry 絕不「跳過不認識的型」。
- **registry 宣告型別與庫中 setting_type 字面不一致**：registry 為驗證權威、庫中 setting_type 為資料；已知鍵而兩者不一致＝資料完整性異常，處置同未知型 fail-loud（`5000`），不採其一靜默放行。
- **description 空字串 vs null**：空字串＝設值為空（落 ""）、JSON null＝清空（落 NULL）、缺席＝不動——三形各有測試案（US5）。
- **enum 大小寫**：enum 值正規形＝原值、大小寫敏感；`ON`／`On` 皆值域外拒收。
- **跨鍵一致性**：password_min_length 與 password_max_length、captcha_after 與 max_fails 兩組鍵的順序關係非本刀驗證面（brainstorm Q6）；
  矛盾組合可各自合法落庫、由消費側刀處置（BACKLOG 記觸發）。
- **msg 訊息鍵未命中前端字典**：前端 graceful fallback（憲法 §I.3 既定）；本刀 msg 一律穩定 i18n key、不回人話字串；跨端鍵集閘延前端 i18n 刀（Q4）。
- **不認識的 header**：一律忽略（憲法 §II #1），契約測試不因多餘 header 改變行為。
- **值長度**：本刀不設字串長度上限（庫真表 setting_value／description 皆無長度上限；enum 值域自然限長、number 由範圍限長）。
- **4 保留碼與未進場碼**：`7778`／`8889`／`9998`／`9999` 與 `1000`／`3333`／`7777` 後端於本刀零發出（構造層不可發出）、契約測試斷言。
- **rust 格式閘首跑撞 001 逐位元承襲檔**：預期綠（rev5 存量已格式化、toolchain 同版）；若紅＝格式化即破 ADR-00009 條件①→停手升 user、不得自行格式化。
- **容器未起時的碼面閘**：rust 格式閘於 docker 缺或 `rust-api` 未在跑＝具名跳過；容器在而格式工具缺＝fail-loud；wire 契約閘於 staged 區間零 typings 變動即跳過。
- **DDL 冒出**：clarify／plan 若出現任何 migration 需求 → 走 RUNBOOK §10 Day-1 三步並改 schema 閘表數斷言（FR-021）；本刀預期零 migration。
- **rev5 側唯讀紀律**：一切讀取對凍結 worktree；絕不寫入、不動其 stack。

## Requirements *(mandatory)*

### Functional Requirements

**管線與服務啟動**

- **FR-001**: rust-api server 首批程式工件 MUST 使全部預設業務件（postgres／migrate／redis／rust-api／base-web／front-nginx／mailpit 七件）
  `up -d --wait` 起得齊（migrate 啟動閘之後 server 常駐、容器健康判定可過）。
- **FR-002**: 路由 MUST 收斂單檔 ROUTES 常量；本刀 route 集＝業務 2＋信封例外 2 恰四條：業務＝`GET /systemManage/getSystemSettings`＋
  `POST /systemManage/updateSystemSetting`（路徑與方法由 casbin seed 政策列 66／67 錨定；本刀 MUST NOT 動 casbin seed 與 sys_menu seed）；
  信封例外＝`/health`（plain text "ok"）＋`/metrics`（Prometheus exposition）皆 MUST 隨 server 就位（憲法 §I.3 例外集恰二；驗收＝dev 直連埠直打）。
  ROUTES 字面形 MUST 可被 docsync 新生成器重算為 routes 參考真表（生成物名冊 14→15、README 成員行同步）。

**讀端**

- **FR-003**: 讀取端點 MUST 一次回傳全部 16 鍵（settingKey／settingType／settingValue／description），僅未刪列、settingKey 升冪穩定序；
  回傳形＝非分頁清單（16 鍵固定集、PageRes 不適用）；審計欄不上 wire；信封與逐欄位型別忠實 typings 權威（憲法 §I.3）。
- **FR-004**: 讀端授權 MUST 依 casbin seed 現況＝僅 R_SUPER；其餘角色→授權拒絕（FR-019 碼表）。

**寫端與設定值 registry**

- **FR-005**: 寫端 MUST 為單鍵更新：以 settingKey 定位、提交新值；成功→`0000`、落庫、回讀一致。可更新欄集＝settingValue（必）＋description（三態，FR-011）；
  settingKey／settingType 不可經寫端變更；無新增鍵／刪除鍵端點（16 鍵集合凍結）。併發語意＝單鍵原子更新、last-write-wins、無樂觀鎖；同值更新照寫審計欄。
- **FR-006**: registry MUST 為每鍵顯式宣告型別與值域：型別集以現庫 16 鍵定形——字面＝setting_type 資料真值 `number`（區間型、10 鍵）／
  `enum:on,off`（開關型、6 鍵）兩型起步、可擴；每 `number` 鍵 MUST 有顯式含界範圍（逐鍵值域＝承 rev5 定稿原值、隨 plan 之 data-model 凍結）；
  registry 未宣告之鍵＝未知鍵；registry MUST 為純宣告、不讀庫、不驗跨鍵關係（Q6）。
- **FR-007**: 驗證失敗 MUST 不寫入：型別不符／超範圍／enum 外值／未知鍵／欄缺席或壞形→`2222`＋穩定 i18n key 明細、庫中原值保留；每一拒收形 MUST 有契約測試案。
- **FR-008**: number 型值 MUST 正規化落庫：trim→整數解析→界內→正規字面（前導零、前後空白、正號等等價形收斂為單一正規形；小數、溢位、非數值拒收）；
  enum 型正規形＝原值、大小寫敏感。
- **FR-009**: 庫中 setting_type 未知型、或已知鍵之庫中 setting_type 與 registry 宣告不一致 MUST fail-loud（`5000` 內部錯誤、HTTP 200 信封）、讀寫路徑觸及皆同；
  MUST NOT 靜默跳過或降級為警告。
- **FR-010**: 審計欄 MUST 由寫入口顯式成對寫（updated_at＋updated_by 同寫、操作者取自請求身分）；MUST NOT 由 ORM 行為層自動承載——
  機器錨 MUST 隨 server crate 建立（BL-00008：entity 對應層全部行為實作必為空、站點數＝表 entity 檔數的等式形、合成正例自證）。

**三態約定層（envelope 級）**

- **FR-011**: 部分更新 MUST 具三態語意：欄位缺席＝不動／顯式清空＝該欄 JSON 值 `null`／設值（RFC 7386 Merge Patch 語意；承 rev5:ADR 0023、rev6 自立 ADR）；
  解析層 MUST 以三態型別區分「欄位未出現」與「欄位值 null」；本刀定形射程＝部分更新請求 body 之每一可選欄、逐域欄級表 MUST NOT 入本刀（留各域刀）。
- **FR-012**: NOT NULL 欄顯式清空 MUST 拒收（`2222`）；nullable 欄（description）顯式清空 MUST 落 NULL、空字串 MUST 落空字串；三形 MUST 各有契約測試案。

**授權面與身分**

- **FR-013**: 授權判定 MUST 收斂單一純函式進入點（enforce 骨架消費 casbin 政策、每請求向資料庫取現行政策）；角色解析 MUST 只認未刪且啟用之角色；
  MUST 留空 no-escalation 掛點（簽章預留非同步與資料庫句柄、本刀恆放行）；003 接真 session 時判定進入點介面不變。
- **FR-014**: 「R_ADMIN 有 user:edit 鈕、無寫端政策」組合之拒絕語意 MUST 為 `5003`＋HTTP 403、msg 純 i18n key、不揭露缺哪條政策亦不揭露操作者角色集；
  MUST 以刀內 ADR 定死（承 rev5:ADR 0022、draft→accepted 於本刀完成）。
- **FR-015**: 登入未到位期間 MUST 以 dev-only 測試態身分頂替：固定測試 token 走 `Authorization` 標頭 Bearer 形、dev-only 驗證器查表映射身分
  （token 字面與查表內容＝plan 細節；預設沿 rev5 三 token 對 dev 三帳）；標頭缺席／非 Bearer 形／token 不在表＝未認證→`8888`（FR-019 碼表）；
  測試態身分 MUST NOT 存在於非 dev 建置形；MUST 獨立成檔、003 整檔汰換。
- **FR-016**: 請求上下文 MUST 只留介面位（信任判定不寫死 handler）；本刀 MUST NOT 寫入 sys_operation_log／sys_access_log。

**wire 契約（憲法 §I.3）**

- **FR-017**: wire 權威＝base-web typings 新檔（`rev6-` 前綴、§III.1 ADAPT 軌道、新增型圈界標記）；型別以 declaration merging 併入既有 `Api.SystemManage`
  命名空間、不改既有 typings 檔；後端序列化 MUST 逐欄位忠實 typings 宣告；description 於 typings 為可選且允許 null（三態欄）。
- **FR-018**: 契約機器化 MUST 就位（本刀＝憲法 §I.3 之「wire 地基刀」）：容器內自 typings 抽 JSON Schema 快照（落 rust-api 測試 fixtures、抽取唯讀、輸出確定性）、
  契約測試離線消費快照裁判序列化輸出（含三態欄之 null 允許）；coverage gate＝契約測試案登記表與 ROUTES 之 case 鍵**雙向**比對——每條 route 必有案（缺即紅指名）、
  每個案必對 route（殭屍即紅指名）；wire 契約閘 MUST 入 pre-commit（base-web 變動時重抽比對、staged 區間零 typings 變動即跳過）。
- **FR-019**: 錯誤碼 MUST 全數 reuse 13 碼矩陣既有碼、零新增碼面；本刀逐碼對表：

  | 路徑 | 碼 | HTTP |
  |---|---|---|
  | 成功（讀／寫） | `0000` | 200 |
  | 型別不符／超範圍／enum 外值／欄缺席或壞形 | `2222` | 200 |
  | 未知鍵（含軟刪防禦態） | `2222` | 200 |
  | NOT NULL 欄顯式清空 | `2222` | 200 |
  | 授權拒絕（政策無授、角色軟刪或停用） | `5003` | 403 |
  | 庫中未知 setting_type／型別與 registry 不一致（fail-loud） | `5000` | 200 |
  | 未認證（標頭缺席／非 Bearer 形／token 不在表） | `8888` | 200 |
  | 路由未匹配（router fallback、非本刀業務路徑） | `4040` | 404 |

  `1000`／`3333`／`7777` 與 4 保留碼 MUST 於構造層不可發出並由契約測試斷言零發出；msg MUST 為穩定 i18n key；信封三欄宣告序 data→code→msg、
  code 恆字串、錯誤 `data:null` 不省略。
- **FR-020**: msg key MUST 後端側閉環（Q4）：本刀七鍵（`common.success`／`biz.systemSettings.invalidValue`／`biz.systemSettings.notFound`／`system.notFound`／
  `system.forbidden`／`system.internal`／`auth.session.reLogin`）住後端單一名冊、契約測試斷言每條 route 每個錯誤路徑實發 msg ∈ 名冊且名冊每鍵至少一個發出點（雙向、防殭屍鍵）；
  跨端閘（名冊 ⊆ 前端字典）MUST NOT 入本刀、以 BACKLOG 記觸發＝首個接 i18n 的前端刀；base-web locales MUST NOT 被本刀新增或改動。

**資料面**

- **FR-021**: 本刀 MUST 零 migration（16 鍵、表結構、casbin 政策列 66／67 皆已隨 001 基線在庫）；schema 閘之親排表數斷言 MUST 不動（ADR-00012 決定 6）；
  clarify／plan 若冒出 DDL → MUST 走 RUNBOOK §10 三步（照相＋演進帳登記＋三閘綠）並改該斷言、記拍板差異點。
- **FR-022**: 資料面兩拍板 MUST 承 rev5 落實：①無 DB FK 之邏輯關聯不建 ORM 關聯宣告（需要即手寫 join）②ORM 行為層不承載六審計欄自動化（FR-010 之資料面對應）；
  `sys_user_role` 兩條 DB FK 之關聯宣告已隨 001 在、本刀 MUST NOT 再動。

**前端接線層**

- **FR-023**: 前端腿 MUST 恰為兩新檔：typings 型別宣告檔（ADAPT 軌道）＋service 接線檔（WRAPPER 軌道、`rev6-` 前綴、不入 barrel）；
  兩檔檔頭 MUST 帶 `rev6-inline` 新增型圈界標記並註明軌道與刀名；全程零 inline 改動、零修憲、零 ★軌道；view 不入本刀、manage_system-settings 選單點擊 404 為已知態；
  `.env` MUST NOT 被本刀改動（route mode 翻 dynamic 延 003，Q7）。
- **FR-024**: 接線層 MUST 完整可消費：兩端點各有型別完備的呼叫函式（讀無參、寫收單一請求物件），未來 view 刀接上即用、不需回頭補型別；容器內 typecheck 綠。

**治理進場（U0 組合拳）**

- **FR-025**: 三支碼面閘 MUST 自 rev5 依「隨遷工具」紀律整檔搬運並於 server 首支 rust 碼落地前就位：rust 格式閘（容器內唯讀檢查、docker 缺或容器未起＝具名跳過、
  容器在而格式工具缺＝fail-loud）、wire 契約閘（FR-018）、fork-delta 標記閘（新增型圈界腿＋§III.1 範圍腿；結構斷言 MUST 改為容 rev6 空 ★軌道表——
  零列時必見「空表——尚無 ★ 軌道」哨兵句、否則 ≥1 列，哨兵句被移除即紅、Q5）；三支皆 MUST 自帶測試綠、註解與字串之四型失效引用 rev6 化、
  入 pre-commit 條件自測迴圈與 README 樹。
- **FR-026**: pre-commit MUST 同段改六處：①自測迴圈加三支 ②rust 格式段（staged 含 rust-api 變動即跑）③wire 契約段（staged 含 base-web 變動即跑）
  ④fork-delta 段（staged 含 base-web 變動、該工具或憲法即跑）⑤entity 漂移段快照缺席由具名跳過改為非零退出並附補救提示（BL-00010、Q2；
  hook 面真演練＝移走快照→commit 被擋→還原→porcelain 對賬）⑥檔頭對 schema-frozen 觸發面的陳述補上 schema 定稿檔；失準修單 MUST 以 errata 枚舉全 repo 逐處處置。
- **FR-027**: 碼面閘名冊 MUST 定形於 RUNBOOK §12 碼面閘表（工具檔｜守什麼｜觸發時機｜根據 ADR；含 msg key 跨端閘之延後註記列），GT-12 MUST 加一腿：
  tools/ 頂層工具檔集減去非閘名冊常數＝表列工具檔集、雙向差集即紅、一正一反自證（BL-00011、Q3）；RULES 名詞段 MUST 補「碼面閘」定義並 bump RULES-VERSION
  （於首個 Workflow 派發前由主線直改、後續 script 一律以新版組裝，Q8）；治理閘數 MUST 維持 12、碼面閘不計入 GT-12 預算。
- **FR-028**: ADR MUST 於刀內落地 accepted、一決策一檔、皆帶 rev5 provenance：①部分更新三態約定 ②授權拒絕語意＋no-escalation seam ③碼面閘名冊承載於 RUNBOOK §12＋GT-12 腿
  ④msg key 跨端契約延前端 i18n 刀、002 後端側閉環 ⑤entity 漂移段快照缺席即紅；收刀 `feature_close` 事件 adrs 列全五筆。憲法 MUST 零 Amendment。
- **FR-029**: BACKLOG 時點 MUST 兌現：BL-00008（機器錨）、BL-00010（缺席即紅）、BL-00011（名冊）於收刀 `backlog_done`；新記兩條＝msg key 跨端閘（觸發＝首個接 i18n 的前端刀）
  與 registry 跨鍵不變式（觸發＝004／007 消費側進場）；活書 MUST 同刀更新（建構視圖 server 管線形、API 慣例之契約機器化與三態 as-built、授權慣例之拒絕語意 as-built；
  現在式、feature branch 內改；C4-L2 拓樸不變零改）。
- **FR-030**: 收刀 DoD MUST 全綠：契約測試（per route＋registry 紅綠矩陣＋三態案＋授權矩陣＋msg 名冊雙向）＋契約快照裁判＋entity 漂移閘＋schema 三閘＋
  三支碼面閘各一正一反＋GT-12 新腿一正一反＋lint 全量；US1～US6 驗收場景全數對應至少一測試案或一演練紀錄（函式名＋案序粒度）；
  rust 建置與測試全程容器內 serial。

### Key Entities

- **系統設定（system_settings、16 鍵）**: 鍵值型設定表（PK＝setting_key、setting_type／setting_value NOT NULL、description nullable、六審計欄 archetype A）；
  現庫 16 鍵＝number 型 10 鍵（節流窗／密碼長度／逾時等）＋enum:on,off 型 6 鍵（密碼複雜度開關／single_session_default 等）；鍵集合本刀凍結、僅值可變。
- **設定值 registry**: 逐鍵型別與值域宣告表（`number` 含界區間型／`enum:on,off` 開關型兩型起步、可擴；字面＝setting_type 資料真值）；驗證的唯一權威、純宣告不讀庫、未宣告鍵拒收。
- **wire 契約物**: typings 新檔（權威）＋自其抽出之 JSON Schema 快照＋離線裁判＋契約測試案登記表（與 ROUTES 雙向覆蓋）；信封與 13 碼矩陣照憲法 §I.3 凍結面消費。
- **casbin 政策（seed 現況、本刀不動）**: 設定域三列皆僅 R_SUPER（讀 66／寫 67／menu 69）；R_ADMIN 之 user:edit 鈕構成「有鈕無政策」驗證組合。
- **測試態身分（dev-only）**: 登入未到位期間的請求身分頂替；固定 token 走 `Authorization` 標頭、dev-only 驗證器查表；003 接真 session 時僅換驗證器內部、通道與判定進入點不變。
- **三態約定（envelope 級）**: 部分更新之通用語意約定（缺席／清空／設值）；本刀定形、全 repo 後續寫端消費。
- **msg key 名冊**: 後端可發出之 i18n key 全集（本刀七鍵）；後端側閉環的權威；跨端閘之左源（延後）。
- **碼面閘名冊**: RUNBOOK §12 碼面閘表（本刀後五支：schema 閘、entity 漂移閘、rust 格式閘、wire 契約閘、fork-delta 標記閘）；GT-12 對賬之右源；「碼面閘」一詞由 RULES 名詞段定義。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 讀端端到端：R_SUPER 讀回 16 鍵、與 seed 定稿逐鍵全等（key／type／value／description 四欄）、升冪穩定序；契約快照裁判對序列化輸出全過。
- **SC-002**: 寫端往返：合法更新（number 與 enum 各至少 1 例）後回讀＝新值、審計欄成對非空；number 非正規字面（前導零、空白、正號各一例）落庫為正規形；同值更新審計欄仍更新。
- **SC-003**: registry 紅綠矩陣全數正確：兩型各有合法過／非法拒對、未知鍵拒、欄缺席與壞形拒、未知型與型別不一致 fail-loud——非法案庫中原值保留（零寫入以回讀證明）。
- **SC-004**: 授權矩陣全數正確：R_SUPER 讀寫皆 `0000`；R_ADMIN 讀寫皆 `5003`（HTTP 403）且回包不含政策明細；未認證三形（標頭缺席／非 Bearer／token 不在表）皆 `8888`；
  角色軟刪或停用案 `5003`。
- **SC-005**: 三態矩陣全數正確：description 缺席不動／null 清空落 NULL／空字串落空字串／設值生效；settingValue 顯式清空拒收——五案各有契約測試。
- **SC-006**: 契約覆蓋自證：兩業務 route 皆有契約測試案，抽掉任一 route 之案 coverage gate 即紅並指名、加一殭屍案亦紅（negative 自證）；
  `1000`／`3333`／`7777` 與 4 保留碼零發出斷言在案；msg 名冊雙向斷言在案。
- **SC-007**: DoD 鏈全綠：七件預設業務件 `up -d --wait` 起得齊（`/health` 直打回 "ok"、`/metrics` exposition 可取得）＋quickstart 讀端／授權矩陣／寫端往返經 front-nginx 真 HTTP 走查全通
  ＋entity 漂移閘綠＋schema 三閘綠＋lint 全量零紅＋GT-12 預算內（治理閘 12、生成物名冊 15）。
- **SC-008**: 治理全綠：三支碼面閘各一正一反自證通過、hook 面缺席演練被擋且還原後 porcelain 零差異、GT-12 新腿一正一反通過、errata「schema-frozen」復掃零殘留、
  RULES-VERSION 已 bump 且名詞段含「碼面閘」、ADR 五筆 accepted、BL-00008／00010／00011 收刀 `backlog_done`、新記兩條 BACKLOG 在案。
- **SC-009**: pre-commit 全鏈實測 ≤45 秒（雙錨警戒線；含新增三段）並記 perf 事件；rust 格式閘首跑對 001 承襲檔綠（若紅＝升 user、不自行格式化）。

## Assumptions

- rev5 為本機可達之唯讀參考庫（工作區同層、凍結 SHA 由 bootstrap 斷言）；rust 應用碼全程重打字消化、註解 rev6 語境重寫、前代出處帶 `rev5:`；
  三支碼面閘依名詞段「隨遷工具」整檔搬運（逐字允許、四型失效引用 rev6 化）。
- 本刀＝憲法 §I.3 所稱「wire 地基刀」（002 為首支 server 刀）；契約機器化機制隨本刀落地。
- 零 migration（表、seed、政策列已在基線）；schema 閘表數斷言不動；本刀非一次性遷移、Risk／Guard／Rollback 三欄表免附。
- wire 形＝POST 單鍵更新（seed 政策列 67 錨定 `updateSystemSetting POST`；改 PUT／PATCH 須動 seed＝拍板級翻案、不做）；請求物件含 settingKey／settingValue／description 三欄。
- 未認證回 `8888`（承 rev5 clarify；003 接真 session 時再對齊 3333／8888 分工）；未知鍵回 `2222`（非 `4040`）。
- dev-only 測試態身分：固定三 token 對應 dev 三帳（Super／Admin／User＝uid 1／2／3）、走 `Authorization: Bearer` 形；token 字面非機密、於 plan 定稿。
- registry 逐鍵值域數字＝承 rev5 定稿原值（number 10 鍵含界、enum 6 鍵），隨 plan 之 data-model 凍結；registry 純宣告、不讀庫、不驗跨鍵。
- 已知鍵之庫中 setting_type 與 registry 宣告不一致＝資料完整性異常、處置同未知型 `5000`（registry 為驗證權威）。
- 併發語意＝單鍵原子、last-write-wins、無樂觀鎖；同值更新照寫審計欄。
- 前端新檔命名 `rev6-settings.d.ts`／`rev6-settings.ts`、標記 token `rev6-inline`；`.env` 零改動；base-web locales 零改動。
- 新進 crate 版本（web 框架、序列化、追蹤、觀測三件、契約裁判、測試工具）於 plan research 逐筆雙源對照（前代 lockfile vs 官方最新穩定版）後定案；tokio 直釘 1.53.1（001 已拍）。
- 世代 DoD B 之 CDP 對照與走查基準工具不適用本刀（無 UI）；走查以 curl 經 front-nginx 真 HTTP 路徑完成。
- 每單元 pin bump、rust 建置測試容器內 serial；review 只讀不寫；rev5 六起守門假綠與 rev6 LESSONS 三條烤進 prompt。

### Out of Scope

- view UI（manage_system-settings 頁面）；真登入／session（003 auth-session）；稽核 log 寫入；設定值消費側（節流／逾時／密碼原則 enforce 各留對應域刀）。
- no-escalation 本體（僅空掛點）；新增／刪除設定鍵端點；列表排序；prod 資產；三態逐域欄級表（留各域刀）。
- msg key 跨端閘與 base-web locales 檔（延前端 i18n 刀、BACKLOG 承載）；registry 跨鍵不變式（BACKLOG、觸發＝004／007）。
- `.env` route mode 翻 dynamic（003）；schema 閘表數斷言改動（首次加表的刀）；`sys_user_role` 關聯宣告（001 已在）。
- 冷編量測與 K1 承襲盤點（rev6 無對應帳；冷編時長只記時不入 DoD）；走查基準 snapshot／diff 工具（隨首個需 UI 走查的刀遷入）。
