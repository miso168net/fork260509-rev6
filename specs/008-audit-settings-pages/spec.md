# Feature Specification: 008 稽核與系統設定頁進場——系統設定頁、稽核頁四源與清理、存取日誌寫入、reaper 三 job、島 J 入憲

**Feature Branch**: `008-audit-settings-pages`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "docs/brainstorms/008-audit-settings-pages.md"（階段 0 brainstorm：定稿 `3b7e519`＋grilling 輪寫回 `d0ed163`；理解校正、BACKLOG 題 B1～B5、設計題 D1～D12、設計四節、grilling g1～g5 皆 user 拍板——非建議項＝D12，其餘首選項皆為建議；主線工程判斷①～㉖為報備、本 spec 直接採用；本 spec 之唯一輸入。該檔 §0 拍板紀錄與工程判斷、§1 rev5 承襲盤點、§2 BACKLOG 觸發項處置、§3 設計四節、§4 規模總帳、§5 憲法九題預答、§6 specify 輸入摘要、§7 隨做隨記為權威來源；rev5 對應刀 `rev5:008-audit-settings-pages` 之 spec 為讀端、清理與兩頁之沿用形藍本，rev4 之 reaper bin 與其 CLI 契約〔`rev4:016-observability`、`rev4:017-audit-retention`〕為 reaper 藍本；rev6 座標改寫、翻案項以 brainstorm 為準。本檔「B 號」＝brainstorm 之 BACKLOG 題、「D 號」＝設計題、「g 號」＝本刀 grilling 題、圈號①～㉖＝brainstorm 主線工程判斷）

> 摘要：把側欄兩項死項（系統設定、稽核）接成真頁——後端新開**稽核 5 支端點**（ROUTES 61→66；path×method 逐字對齊 001 凍結 seed 列 139／140／141／158／159、全授 R_SUPER、零新政策列），前後端同刀、CDP 對照 rev5 HEAD 驗收。
> 行為面：**四源讀端**（操作日誌／存取日誌／登入嘗試／會話事件；固定序、寬鬆過濾、讀端個資打碼單點）；**水平線清理**（固定序守門、30 天下限、單交易自記、拒因攜 `{minDays}`＝錯誤明細通道第三鍵）；**存取日誌寫入**（每筆已登入請求一列、位於認證之後而包住授權判定、fail-open）；**設定寫端落操作稽核**＋設定讀端 wire 擴充（宣告界、宣告旗標）；**reaper 三 job**（票回收、排程清理、授權對賬只報不刪；排程清理自記列來源位址哨兵 `0.0.0.0`、刪 0 列照落）。
> 前端：系統設定頁（四組、逐項即改即存、界值鉗界、宣告集外列唯讀、三對跨鍵矛盾即時提示不擋、改政策即清同分頁快取）；稽核頁（四分頁、搜尋卡、XFF 純文字、快照浮層、清理浮層依 `audit:purge` 碼顯隱）；三語同批、繁中全頁審讀。
> **一支 delta migration m0004**（reaper 最小權限 role＋GRANT；選單 77 增 `audit:purge` 碼＋R_SUPER 按鈕授權列）；其前補 BL-00148 之零 docker 離線對賬腿。
> 憲法一次 MINOR（1.8.1→1.9.0）：島 J 全入（J1～J5、J2 回填）、§III.2 管理頁 ★ 軌道新用途 (ix)(x)、§I.6 變體 B 括號句改 J3 交叉指針、MAJOR 射程九島→十島。ADR ①～⑩（plan 期起草）＋收刀前 PATCH Amendment 一支。BACKLOG 開放項 5 條隨本刀收、零新記（008 窗淨約 −6）。

## Clarifications

### Session 2026-10-21

- Q: 設定頁 10 個數字鍵輸入越界值時，要不要一律鉗到後端宣告的上下界再存？ → A: 10 鍵一律鉗界（user 選建議項）——界值全由讀端下發之登記表宣告界、前端不抄鍵集；越界輸入失焦即鉗至界值後送出並存檔。rev5 前端只 5 鍵有界（`password_min_length`、`password_max_length`、`login_throttle_max_fails`、`login_throttle_window_minutes`、`login_throttle_captcha_after`），另 5 鍵（`ip_captcha_after`、`ip_max_fails`、`ip_window_minutes`、`password_change_min_interval`、`session_idle_timeout`）由「越界送出、後端拒、提示並回退」改為鉗界存檔＝刻意分岔；更正 brainstorm 工程判斷③「畫面同 rev5」只對前 5 鍵成立。落 US1 第 2、3 條、FR-046、Edge Cases、SC-009、刻意分岔登記表。
- Q: 存取日誌的「狀態」欄只記 HTTP 狀態碼，要照 rev4 欄形、在存取分頁加一句說明就好嗎？ → A: 照 rev4 欄形＋加一句說明（user 選建議項；提問緣起＝user 轉來之 side agent 提醒）——零 DDL、不加業務碼欄；rev6 與 rev4 回應對映相同（權限不足 403、找不到 404，其餘含業務拒因與系統錯誤皆 HTTP 200），故存取日誌之狀態欄分不出業務成敗＝已知態；存取分頁上方加一句告示（比照登入嘗試分頁、三語）；spec、活書與 RUNBOOK 寫明。落 US2 第 3 條、US4 第 1 條、FR-009、FR-022、FR-055、FR-064、Edge Cases、Key Entities、SC-006、刻意分岔登記表。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 超管調整系統設定（四組逐項即改即存、界值、矛盾提示、政策快取、變更入稽核） (Priority: P1)

超級管理員自側欄進入「系統設定」頁，看到 16 個運行參數依用途分為密碼策略、工作階段、IP 源登入、帳號登入四組；開關型以開關、數值型以數字框呈現，每項有說明。改任一項即單獨送出，成功或失敗都以伺服器回讀收斂畫面；數字框以後端登記表宣告的界值鉗界；登記表宣告集外的列唯讀顯示。三對相互牽制的參數一旦存成矛盾組合，該組卡片立即警示並寫明後果，但不阻擋存檔。改了密碼政策之後，同一分頁內的設密提示立即改用新政策。每次成功改動都在操作日誌留一列（舊值→新值）。

**Why this priority**: 本刀兩頁之一（BL-00045）；設定寫端 002 刀即已備妥、只欠畫面，seed-view-gate 豁免表出列以此為前提；節流、逾時、密碼政策都在此即時生效，是日常營運面。

**Independent Test**: Super 先於使用者頁開一次「重設密碼」浮層（政策快取載入、提示為 8 字下限）→ 自側欄進「系統設定」→ 四組 16 鍵、側欄與頁標題為譯文 → 把 `password_min_length` 改為 12 → 回讀 12、操作日誌分頁多一列（`update`、`system_settings`、標的 id「-」、快照含鍵與 8→12）→ 不重新整理即回使用者頁再開該浮層，即時提示改為 12 字下限 → 把 `password_max_length` 改為 10 → 密碼策略卡出現矛盾警示（三個設密入口一律拒）、值照存 → 改回 64 → 警示消失。

**Acceptance Scenarios**:

1. **Given** Super 已登入，**When** 側欄點「系統設定」，**Then** 正常進頁；四組固定序（密碼策略／工作階段／IP 源登入／帳號登入）共 16 鍵——`password_` 前綴歸密碼策略、`ip_` 歸 IP 源登入、`login_throttle_` 歸帳號登入、其餘歸工作階段；側欄項與頁內標題為譯文、非 `route.manage_system-settings` 裸鍵；組內依固定鍵序、未列序之新鍵排組尾保伺服器相對序（前綴皆不符之新鍵落工作階段組尾）；空組整卡不渲染。
2. **Given** 頁面已載入，**When** 切換開關型設定，**Then** 立即送出、成功提示、回讀全列；**When** 數字欄改值後失焦或按 Enter，**Then** 送出並回讀（值未變不送出）；**When** 清空數字欄後失焦，**Then** 不送出、回讀使畫面回退為伺服器現值；**When** 寫入被後端拒絕，**Then** 顯示可讀拒因（i18n 轉譯、非裸鍵）、回讀使畫面回退（數字框已鉗界＝畫面上送不出越界值，此分支之驗法於 plan 期定）。
3. **Given** 10 個數字鍵，**When** 輸入越界值後失焦，**Then** 框內值鉗至讀端下發之登記表宣告界後送出並存檔（如 `password_min_length` 界 1～128、輸入 999 存為 128；`session_idle_timeout` 界 5～1440、輸入 0 存為 5、操作日誌記 60→5）；界值之單一權威仍在後端登記表（ADR-00054）；其中 `ip_captcha_after`／`ip_max_fails`／`ip_window_minutes`／`password_change_min_interval`／`session_idle_timeout` 五鍵於 rev5 無前端界（越界送後端拒）＝刻意分岔（clarify Q1）。
4. **Given** 庫中有一列型別合法但不在登記表宣告集內之設定（seed 態無此列），**When** 進頁，**Then** 該列唯讀顯示、排該組尾、標示其後端 description；直呼寫端仍回 `2222`（ADR-00057 已知態）。
5. **Given** 三對跨鍵判準（皆嚴格不等式）——`password_min_length` ＞ `password_max_length`、`login_throttle_captcha_after` ＞ `login_throttle_max_fails`、`ip_captcha_after` ＞ `ip_max_fails`，**When** 任一對存成矛盾組合，**Then** 該對所屬之組卡片即時警示並寫明後果（密碼長度對＝三個設密入口一律拒；節流兩對＝後端該維三鍵整組退回出廠常數）、不阻擋存檔、後端照舊逐鍵驗；**When** 兩值相等，**Then** 不警示（相等合法：軟區寬度零）；**When** 改回非矛盾，**Then** 警示消失。
6. **Given** 同一分頁內已載入過密碼政策（使用者頁之重設或產密浮層、個人中心改密卡），**When** 於設定頁成功寫入政策七鍵任一（長度上下界、四類字元要求、禁止密碼與帳號相同），**Then** 該分頁之即時提示、產密構造界與送出前擋改用新值；其他已開分頁仍須重新整理（RUNBOOK §11.3 同批改述）。
7. **Given** 任一次 updateSystemSetting 成功，**When** commit，**Then** 同交易已落一列操作日誌：動作 `update`、`entity_table`＝`system_settings`、`entity_id` 空（該表主鍵為字串鍵）、變更前與變更後各為整列快照（鍵在快照內）；稽核頁該列標的 id 顯「-」，點「查看快照」看得到鍵與舊值→新值（g4）；**When** 寫入被拒（拒因），**Then** 零寫入、零稽核。
8. **Given** 以 Admin 或 User 登入，**When** 檢視側欄，**Then** 「系統設定」不可見；直呼兩支設定端點得 `5003`；**Given** 超管把設定頁之選單可見性授予自建角色，**When** 持該角色者進頁，**Then** 看得到頁、讀寫皆 `5003`（設定兩支端點屬封死集、不可授出；ADR-00064、ADR-00081 款 10）。

---

### User Story 2 - 超管查閱四源稽核紀錄 (Priority: P1)

超級管理員自側欄進入「稽核」頁，四個分頁分別是操作日誌、存取日誌、登入嘗試、會話事件；每個分頁有自己的搜尋卡（欄位過濾＋時間區間）、重新整理鈕與分頁表格，固定由新到舊。操作日誌可點「查看快照」以唯讀浮層看變更前後的 JSON，其中手機與信箱已打碼。操作、存取、登入三個分頁把轉發鏈（XFF）以純文字顯示。存取日誌自本刀起有資料。

**Why this priority**: 本刀兩頁之二（BL-00045）；5 支稽核端點之 path×method 早由 seed 預埋；US3 清理與 US4 存取日誌的效果都靠此頁驗證。

**Independent Test**: Super 進稽核頁 → 四分頁可切換 → 操作日誌分頁以資料表名 `system_settings` 過濾 → 看到 US1 那一列、快照浮層顯示整列舊→新 → 對某自建帳號改手機與信箱後，其 `update` 列快照中手機與信箱已打碼 → 存取日誌分頁出現自己剛才的請求列（路徑不含 query string）→ 登入嘗試分頁以精確 IP 過濾 → 會話事件分頁以事件型過濾 → 植入 XFF 含 `<script>` 字面之列 → 以字面顯示、零執行。

**Acceptance Scenarios**:

1. **Given** Super 已登入，**When** 側欄點「稽核」，**Then** 正常進頁、四分頁可切換；各表固定 `created_at` 降冪、`id` 降冪決勝；每頁預設 10 筆、可調（size 夾於 [1, 100]、current 下界 1）；前端零排序、零匯出、零快照內容搜尋。
2. **Given** 操作日誌分頁，**When** 以資料表名（等值）、動作（等值）、操作者 id 或名（id 優先；名對應含已軟刪同名之全集）與時間區間過濾，**Then** 結果符合全部條件；操作者名以第二發批次查詢補齊（不 join、無 N+1）、查無名稱顯示 id、再無顯示「-」。
3. **Given** 存取日誌分頁，**When** 以 HTTP 方法（等值）、狀態碼（等值）、路徑（部分字串、萬用字元字面化）、操作者 id 或名與時間區間過濾，**Then** 結果正確；列含方法、路徑、狀態、操作者、來源 IP、XFF、region、traceId；分頁上方告示「狀態欄為 HTTP 狀態碼：權限不足顯示 403，其餘請求（含業務拒絕與系統錯誤）皆顯示 200」之語意（clarify Q2；plan 期 user 親決只提 403）。
4. **Given** 登入嘗試分頁，**When** 以嘗試帳號名（部分字串）、成敗（只收 `true`／`false`、值域外視同未設）與來源 IP 過濾，**Then** 結果正確；來源 IP 為精確等值比對（IPv4 /32、IPv6 /128）、非字串包含（`rev5:B-078` 確認句）；分頁上方告示「節流短路遭拒不落表」之語意、不承諾嚴格上限。
5. **Given** 會話事件分頁，**When** 以使用者 id 或名、事件型（等值）、原因（等值）與時間區間過濾，**Then** 結果正確；列含 sid、事件型、原因、使用者、來源 IP；該源結構上無 XFF 欄＝不渲染、不留空欄。
6. **Given** 操作日誌有快照之列，**When** 點「查看快照」，**Then** 唯讀浮層以純文字 JSON 顯示變更前／後；快照頂層之 `userPhone`／`userEmail` 已由後端讀出時打碼（手機長於 5 字＝前 3＋`****`＋後 2、否則全遮 `****`；信箱＝首字＋`***`＋`@網域`、無 `@`＝首字＋`***`；深度一層、變更前後各一次）；資料庫原值不動；無快照之列顯示無快照提示。
7. **Given** 某列 XFF 值含 `<script>` 等 HTML 字面，**When** 渲染，**Then** 以字面文字顯示（截尾＋懸停看全文）、零腳本執行、零 HTML 解析；空值顯示「-」。
8. **Given** 任一分頁之時間區間，**When** 以瀏覽器本地時間選取起迄，**Then** 轉 UTC ISO 上 wire（`timeFrom`／`timeTo`）、後端以 [起, 迄) 過濾；表格時間欄顯示 UTC（`+00:00` 原樣；D4：輸入為瀏覽器本地時間、顯示為 UTC）；**When** 起晚於迄，**Then** 空頁；**When** 時間字串畸形，**Then** 該過濾視同未設。
9. **Given** 任一讀端，**When** query 參數為空字串或畸形值（如 `?operation=`、`?size=abc`），**Then** 該參數視同未設、絕不回 4xx。
10. **Given** 以 Admin 或 User 登入，**When** 檢視側欄，**Then** 「稽核」不可見；直呼任一稽核端點得 `5003`；**Given** 未帶權杖，**When** 呼叫，**Then** 得 `8888`。

---

### User Story 3 - 稽核資料生命週期：手動清理、排程清理與票回收 (Priority: P2)

超級管理員在稽核頁任一分頁按「清理」（按鈕依 `audit:purge` 碼顯隱），輸入保留天數（下限 30 天）、經二次確認後，刪除該源早於水平線的資料；系統回報刪除筆數，並在操作日誌留一列清理自記。維運面另有排程清理：reaper 依環境變數之保留天數，對四源逐表做同樣的水平線清理並自記；同一支 reaper 也回收過期的登入票。清理自記列永遠不會被任何清理刪掉。

**Why this priority**: 稽核四表只增不減，容量告警（audit-capacity）至今無處置路；BL-00043 後半（reaper 自動面）與手動清理同屬島 J3 一條規則；依賴 US2 之讀面驗證其效果。

**Independent Test**: Super 在操作日誌分頁按「清理」、輸入 29 → 拒並提示最少 30 天 → 輸入 30 並確認 → 回報刪 N 筆、操作日誌最上方多一列 `purge`（來源表、天數、筆數）；以 jobs profile 跑 reaper `--job audit-retention`（不帶 `--execute`）→ 零變動、輸出四表候刪數 → 帶 `--execute` → 逐表刪除並寫四列自記（操作者「-」、來源 IP `0.0.0.0`、刪 0 列照落）；`--job token-reap --execute` → 過期逾寬限之票刪除。

**Acceptance Scenarios**:

1. **Given** 清理浮層，**When** 天數小於 30 送出，**Then** `2222`＋`biz.audit.purgeBelowFloor` 攜 `{minDays}`、提示含下限值（佔位符插值、三語譯文只放佔位符）；**When** 天數缺席或畸形，**Then** 視同 0、同被下限擋下（恆不裸 400）。
2. **Given** 來源表值域外，**When** 送出，**Then** `2222`＋`biz.audit.invalidTable`（純 key、不回聲原值）；**When** 來源表與天數同時違反，**Then** 回 `invalidTable`（固定序①先於②）；兩拒因皆在觸 DB 之前、零 DB 副作用。
3. **Given** 合法來源表與天數並經二次確認，**When** 送出，**Then** 單一交易：該表早於（現在−天數）之列整段刪除＋同交易落一列操作日誌自記（動作 `purge`、`entity_table`＝目標表名、`entity_id` 空、變更後快照＝{來源表, 天數, 刪除筆數}；刪 0 列照落）→ 回 {刪除筆數}；成功提示帶筆數並刷新該分頁。
4. **Given** 清理標的＝操作日誌，**When** 執行，**Then** 歷史清理自記列（動作 `purge`）不被刪（永久豁免＝後設證據）；本次自記列時戳晚於水平線、天然不在刪除範圍。
5. **Given** 自記寫入失敗（故障注入），**When** 交易結束，**Then** 整筆回滾：零刪除、零自記、回錯誤；「回報刪了 N 筆、實際零刪除」與「刪了沒記」皆不可達（`rev5:B-125` 危害形）。
6. **Given** 操作者不可得（請求上下文缺席），**When** 清理，**Then** `5000` 拒寫、零變更（不以佔位補列）；判定位次在白名單與下限之後、觸 DB 之前。
7. **Given** reaper `--job audit-retention`，**When** 不帶 `--execute`（dry-run），**Then** 逐表輸出候刪數（謂詞與刪除逐字同形）、零變動、零自記、推 dry-run 心跳；**When** 帶 `--execute`，**Then** 固定表序（操作日誌→存取日誌→登入嘗試→會話事件）逐表單交易「水平線刪除＋自記」、與手動清理同謂詞同自記形；自記列操作者空、來源位址為哨兵 `0.0.0.0`（信心、對端、XFF 皆空、快照帶 job）；刪 0 列照落（每輪四列）。
8. **Given** 四表保留天數環境變數（`AUDIT_RETENTION_OPERATION_LOG_DAYS`／`AUDIT_RETENTION_ACCESS_LOG_DAYS`／`AUDIT_RETENTION_LOGIN_ATTEMPT_DAYS`／`AUDIT_RETENTION_SESSION_EVENT_DAYS`），**When** 缺席，**Then** 取 90；**When** 畸形（非非負整數），**Then** 結構化告警並取 90 照跑；**When** 解析成功且小於 30（含 0），**Then** 開跑前四鍵一次全驗、任一違規即結構化錯誤（指名鍵與值）＋非零退出＋不推心跳，且先於任何資料庫連線。
9. **Given** reaper `--job token-reap`（預設 job），**When** dry-run，**Then** 輸出候刪數、零變動；**When** 帶 `--execute`，**Then** 以單一語句刪除過期逾寬限天數之票（`REAPER_GRACE_DAYS` 缺席或畸形退 7、畸形告警）並輸出實刪數。
10. **Given** reaper 任一 job 任一步失敗（資料庫不可達、查詢失敗、任一表交易失敗），**When** 結束，**Then** 結構化錯誤＋非零退出、不推成功心跳；已 commit 之表維持（部分完成＋整體報錯＋下輪冪等）；**When** 完跑（含 0 列），**Then** 退出碼 0；心跳推送 best-effort、附全程時限，推送失敗不改退出碼。
11. **Given** 未知參數或未知 job 名，**When** 啟動，**Then** 嚴拒（非零退出＋錯誤事件）、不靜默走 dry-run。
12. **Given** `audit:purge` 碼，**When** 持碼者開稽核頁，**Then** 見清理鈕；**When** 不持碼，**Then** 不見；碼與清理端點授權各自獨立（碼有端點無＝鈕見而按下得 `5003`；端點有碼無＝鈕不見而 API 可達）。

---

### User Story 4 - 存取日誌：每筆已登入請求留一列、寫入不擋業務 (Priority: P2)

自本刀起，每一筆已登入使用者的 API 請求都在存取日誌留下一列（誰、什麼方法、哪個路徑、回應的 HTTP 狀態碼、來源位址與轉發鏈），被授權擋下的請求也記；未登入的請求（登入、換發、驗證碼等公開端點）一律不記。寫入不影響業務：回應先回、寫入在背景完成，失敗只告警、不擋請求。

**Why this priority**: BL-00043 前半；rev5 之存取分頁讀空表（`rev5:R2-9` 不搬）於本刀翻案；告警 ③d 自本刀起有事件源。屬資料面能力、與兩頁可分開驗收，故次於 P1。

**Independent Test**: Super 登入後瀏覽數頁 → 存取日誌分頁出現對應列（路徑不含 query string）→ Admin 直呼稽核端點得 `5003` → 該請求亦有一列 → 未登入呼叫驗證碼端點 → 零列 → 注入寫入失敗 → 業務回應不變、結構化告警一則、降級計數增一。

**Acceptance Scenarios**:

1. **Given** 已登入請求，**When** 完成，**Then** 落一列：操作者 uid、HTTP 方法、路徑（只取請求路徑、絕不含 query string、絕不讀 body）、回應之 HTTP 狀態碼（不記業務碼：業務拒絕與系統錯誤皆為 200；clarify Q2）、真實來源位址、對端、XFF 判定窗轉錄（≤1024 字元、零 CR／LF、超長留最右端）、信心；region 與 trace_id 無料源＝空。
2. **Given** 已登入但被授權判定拒絕之請求（`5003`），**When** 完成，**Then** 照記一列、該列狀態＝403（中介層位於認證之後而包住授權判定）。
3. **Given** 未認證之請求（公開子路由），**When** 完成，**Then** 零列（中介層構造上不掛公開子路由；表之操作者欄 NOT NULL）；**Given** 認證失敗之請求（`8888`、`3333`、`7777`），**Then** 亦零列；**Given** 未註冊路徑或動詞不符之請求（`4040`），**Then** 亦零列（路由最外層 fallback 處理、不經記錄層）。
4. **Given** 稽核讀端自身之請求，**When** 完成，**Then** 亦記（無豁免名單）；讀端 handler 與其交易仍零寫入（島 J1「稽核查詢純唯讀」之射程不含中介層之存取日誌列）。
5. **Given** 寫入失敗（資料庫故障注入），**When** 請求完成，**Then** 業務回應之狀態與內文不變、結構化告警一則（告警 ③d 依此重錨）＋降級計數增一；**Given** 請求上下文或身分缺席，**Then** 跳過寫入（不 panic、不 500）。
6. **Given** 寫入延遲（注入慢寫），**When** 請求完成，**Then** 回應不等待寫入（回應先回、再非同步寫入）。

---

### User Story 5 - 孤兒授權列偵測：授權對賬只報不刪 (Priority: P3)

維運者以 reaper 的授權對賬 job 唯讀掃描三維授權（選單、按鈕、端點），找出孤兒授權列——標的不在該維候選集內之現役列，或角色代碼指向已軟刪或不存在之角色之列。job 只輸出逐維計數（結構化日誌＋心跳 metric），非零即告警；不自動刪。RUNBOOK 寫明判讀與處置。

**Why this priority**: BL-00133 後半（`rev5:B-025` 殘餘②）；畫面上沒有清理孤兒列之路（ADR-00066 後果：候選外現役列在角色存續期內全量替換撤不掉、唯角色軟刪之連動歸檔掃得到、seed 三角色受刪除守門），只能先讓它被看見；屬維運面、不影響終端使用者畫面，故 P3。

**Independent Test**: 全新 seed（本刀五支註冊後）跑授權對賬 → 三維皆 0、不告警 → 測試植入一列候選外端點列、一列指向已軟刪角色之選單維列、一列標的碼不在其候選集之按鈕維列 → 對應維計數各 +1、告警觸發 → job 前後授權域三表逐列不變。

**Acceptance Scenarios**:

1. **Given** 全新 seed（m0001～m0004）且本刀五支已註冊，**When** 跑對賬，**Then** 三維計數皆 0（端點維之候選外現役列今恰為列 139／140／141／158／159、本刀註冊後為 0）＝對賬不恆告警。
2. **Given** 植入各維孤兒列，**When** 跑對賬，**Then** 對應維計數正確、結構化日誌指名維與計數、心跳 metric 帶逐維計數、非零告警規則觸發。
3. **Given** 對賬 job（有無 `--execute` 皆同），**When** 執行，**Then** 零寫入（不刪、不歸檔、不寫稽核）；reaper role 對授權域三表只有讀權。
4. **Given** 對賬非零，**When** 維運者查 RUNBOOK，**Then** 處置節寫明判讀與兩路處置：非 seed 角色＝刪除該角色、經連動歸檔清除；seed 角色或需逐列清＝維運 SQL，範本先匯出待刪列留存再刪、不手寫歸檔列（歸檔原因為封閉詞彙）；系統不提供畫面清理路（g3）。

---

### User Story 6 - 治理連動：島 J 入憲、m0004 與離線對賬腿、觀測層、工具與帳本 (Priority: P3)

作為 workspace 維護者，我要在動任何 base-web 既有檔之前，以一筆 MINOR Amendment 讓島 J（J1～J5）入憲並開管理頁 ★ 軌道新用途 (ix)(x)；先補上 BL-00148 之零 docker 離線對賬腿，再以一支 delta migration m0004 建 reaper 最小權限 role、新增 `audit:purge` 碼與其 R_SUPER 授權列；把觀測層無事件源之告警依 as-built 重錨、刪除三個恆空面板；並讓走查還原工具、schema 閘、帳本與活書在收刀時結清。

**Why this priority**: 治理項可與功能分開驗收，但 Amendment 是**硬序前置**（accepted 前不得動 base-web 既有檔）、BL-00148 離線腿是 m0004 單元之**觸發前置**、走查與 schema 閘之 runtime-append 擴列是存取日誌入刀後**測試基建前置**；優先序只表達「不是交付價值本體」、不表達次序。

**Independent Test**: Amendment 落地後 fork-delta-lint 對新用途列之名冊載入以變異自證；離線對賬腿對 m0003 與 m0004 一正一反、逐判準停用變異皆紅；m0004 於全新庫重放後 schema 三閘綠、拆掉序號合成即紅；以 reaper 憑證連線可跑三 job、權限外語句被拒；告警 ③d／⑤⑤b／⑥⑥b 有事件源並依 as-built 查詢；`rust-api.json` 三空面板已刪。

**Acceptance Scenarios**:

1. **Given** plan 期 ADR 草稿已落 feature branch，**When** user 逐款親決 → Amendment ADR accepted → 憲法更新＋bump 1.9.0＋generate，**Then** 以獨立 commit 落地；在此之前 base-web 既有檔零 diff。
2. **Given** 零 docker 離線對賬腿，**When** 對 m0003 與 m0004 執行，**Then** 綠；**When** 改壞 migration 之 SQL 常數、少登一筆演進帳、或改壞凍結 seed 前值，**Then** 各紅；逐判準停用之變異皆紅；需 docker 之 `check` 維持不進 pre-commit 常跑鏈。
3. **Given** 全新庫依序跑 m0001～m0004，**When** 跑 schema 三閘，**Then** 綠（演進帳 `seed_update`／`seed_add` 合成、新列序號期望值隨之推進）；**When** 拆掉序號合成，**Then** gate2 紅；schema-definition 不前進（ADR-00087）。
4. **Given** reaper 以 `reaper_database_url`（最小權限 role）連線，**When** 三 job 執行，**Then** 所需語句皆成功；**When** 嘗試權限外語句（如寫業務表、改授權域三表），**Then** 被資料庫拒絕。
5. **Given** 觀測層，**When** 收刀前檢查，**Then** ③d 依存取日誌 as-built 重錨、⑤⑤b（票回收）與⑥⑥b（排程清理）自「無事件源」改為現況、新增對賬告警兩條（任一維非零、對賬心跳逾時）；`rust-api.json` 兩支 HLL 面板與「設定讀取頻次」面板已刪並重排；reaper 四面板與 `audit-log.json` trace_id 相關描述改 rev6 as-built。
6. **Given** 走查還原工具與 schema 閘，**When** 存取日誌入刀後，**Then** 兩工具之 runtime-append 常數同值擴入 `sys_access_log`、自測對賬兩者相等；走查前後全表基準 diff rc 0。
7. **Given** 收刀，**When** append `feature_close` 事件，**Then** `backlog_done` 5 條與 FR-066 相符、本刀零 `backlog_add`。

---

### Edge Cases

**讀端**

- 時間區間顛倒＝空頁；畸形時間字串＝該過濾視同未設；query 參數空字串＝視同未設；任何 query 形都不回 4xx。
- 分頁參數越界：current 小於 1 取 1；size 大於 100 取 100、小於 1 取 1；畸形取預設。
- 操作者名過濾：名對應含已軟刪同名使用者之全集（以 id 集合比對）、id 與名同給時 id 優先。
- 登入嘗試之成敗過濾只收 `true`／`false`、值域外視同未設；路徑與帳號名之部分字串比對中，萬用字元字面化。
- 來源 IP 精確等值只在登入嘗試分頁（rev5 形：存取日誌之查詢與搜尋卡皆無來源 IP 欄）。
- 讀端零稽核欄複驗入口（`rev5:B-078` 確認句）；四支讀端 handler 與其交易零寫入。
- XFF 值建構點已保證 ≤1024 字元、零 CR／LF；欄內截尾、懸停看全文；空值「-」；會話事件分頁無此欄。
- 來源欄：traceId 三分頁渲染、值恆「-」；region 存取與登入兩分頁渲染（恆「-」）、操作分頁不渲染；peerIp、ipConfidence 上 wire 但不渲染；讀端照原字面回、容忍 003 期 `nginx_peer` 舊信心值。日後若渲染 ipConfidence，`chain_rejected` 須分表判讀（登入嘗試上恆為被拒列、操作日誌上為標記而照常服務）。
- 打碼封閉定義：只打快照頂層 `userPhone`／`userEmail`、深度一層；非字串值、缺席、巢狀同名鍵一律原樣；快照本身非物件原樣；無「無法打碼即洩原值」之路。
- 快照其餘欄照原文上 wire，含 007 刀使用者域整列快照之管理員記事 `userMemo`：007 刀 FR-019「記事欄不得出現在下拉、引用或對外之其他 API」之射程為業務 API，稽核快照屬只授超管之唯讀證據面、不在其射程（user 2026-10-21 tasks 期裁定）。
- 排程清理自記列：操作者顯「-」、來源 IP 顯 `0.0.0.0`；設定變更列標的 id 顯「-」（g2、g4）；與解鎖列「無列可指」之既有前例同形。
- 被授予稽核頁選單可見性（政策列 142、非受保護）而未授端點之非超管：頁可見、四分頁讀取得 `5003`（頁內形由 ADR⑤ 另立一款）。

**清理**

- 固定序（FR-016 表）不可反；①②③皆不觸 DB；操作者解析在①②之後、觸 DB 之前。
- 清理與併發寫入：只刪早於水平線之列、與新寫入零交集；自記與刪除同交易。
- 被授清理端點者（D5：五支皆可授出）受 30 天下限與永久清理自記兜底；授出不改任何守門。
- 清理浮層之天數下界為前端 UX 護欄（照 rev5 抄一份、碼註寫明權威在後端常數）；繞過前端直呼仍由後端擋。
- 天數極大至時間無法表示時 MUST NOT 使服務崩潰：資料庫拒、整筆回滾、回 `5000`（rev5 形；浮層無上界）；reaper 之保留天數環境變數同（該表交易失敗＝結構化錯誤＋非零退出）。
- 清理鈕持碼而無端點授權＝按下得 `5003`（誠實）；端點有碼無＝鈕不見、API 可達（兩鍵各自獨立、由超管一併治理）。

**存取日誌**

- 每請求一寫：負載與走查 diff 恆報差（R3）——存取日誌入 runtime-append 集、序列只比存在性。
- 非同步寫入可能於測試收尾後才落地＝跨測試污染（R3）；與業務共用連線池、突發流量下可能拖慢業務請求（R3）——對策於 plan 期定；不動連線池設定（不觸 BL-00147「改動連線池設定」臂）。
- 不入登入路徑（不觸 BL-00145「改動判定次序」臂）。
- 寫入失敗只告警、不擋＝fail-open（島 J2）；與 HTTP 寫端「上下文缺席拒寫」方向相反屬刻意（存取日誌為請求後之觀測紀錄、操作稽核為與業務同交易之紀錄）。
- 狀態欄＝HTTP 狀態碼、實際只見 200 與 403：只權限不足（403）可辨，業務拒絕（`2222`）與系統錯誤（`5000`）皆為 200、與成功無從區分＝已知態（rev4 欄形；clarify Q2）；找不到（`4040`：未註冊路徑、動詞不符）由路由最外層 fallback 處理、不經記錄層＝零列；被拒之業務操作亦不落操作日誌——業務成敗不在稽核頁之射程；存取分頁以告示說明。
- 被 IP 存取閘擋下之請求零列（閘在驗章之前＝未認證、島 J2「未認證零列」；帶有效權杖亦然）：阻擋紀錄住閘門之結構化告警（target `security.ipgate`、帶命中網段與來源 IP）與 `ipgate_blocked_total`（004 刀 FR-024）。回應產生前即被丟棄之已認證請求（用戶端中斷、逾時）零列（寫入於回應產生後才排程；rev4 形）。兩者皆屬已知態。

**系統設定**

- 未知 settingType（非二值 enum、非 number）→唯讀呈現原值；未映射 i18n 鍵之新設定→label 以後端 description 遞補（16 鍵全映射、不以 description 退底）。
- 快速連續切換開關：逐次提交、以回讀收斂（無防抖、可短暫閃動＝rev5 既有行為）。
- 越界輸入：10 個數字鍵一律鉗至宣告界後存檔（clarify Q1）；誤打越界值之察覺＝成功提示、框內數值與操作日誌舊→新；鉗界後若形成跨鍵矛盾（如 `password_min_length` 存為 128 而上界仍為 64），矛盾提示照常出現。
- 同值寫入：照寫（續 ADR-00091〔續行 ADR-00080〕系統設定域之「同值照寫」）並照落一列稽核（快照前後相同；D1「每次 updateSystemSetting 同交易落一列」字面）——本刀起與角色選單域同形；畫面上數字框值未變不送出、開關每切必變＝只 API 直呼可達。
- 空字串：16 鍵皆 number 或二值 enum 型、空字串驗證不過＝`2222`；不新增「清空」語意（ADR-00091 設定域觸發器重評結論＝維持；ADR⑧′）。
- 矛盾提示只比兩現值、不改後端行為：密碼長度對維持 ADR-00079（三入口一律拒＋專屬計數）；節流兩對維持島 E「整組退」；判準與後端同式之嚴格不等式。
- 政策快取清除只限同分頁；寫入政策七鍵以外之鍵不清；寫入失敗不清。
- 帳號登入與 IP 源登入兩組之說明不承諾嚴格上限（例「窗內失敗達此數即鎖定（並發首波不嚴格）」或不寫上界；BL-00145 約束）。

**reaper**

- 走查期間與真庫測試期間不起 jobs profile（R4）；jobs profile 活體跑一輪限指定步驟。
- dev loop 每日一輪（`REAPER_INTERVAL_SECS` 缺席退 86400），與告警⑤／⑥門檻 172800 互為 2× 錨（compose 兩檔＋告警規則三檔同步）。
- 清理自記列永久豁免＝每日一輪約每年 1,460 列不可清（g5）；操作日誌分頁可依動作或操作者篩除。
- 哨兵 `0.0.0.0` 之語意邊界：只限無操作者之系統程序自記列；HTTP 寫端照舊只轉錄請求上下文、缺席拒寫 `5000`（R13）；不用 `127.0.0.1`（dev 真請求可能來自該址）。
- 已 commit 之表不回滾（部分完成＋整體報錯＋下輪冪等）。
- reaper role 由 m0004 建為無密碼、不可登入，由既有設密腳本開登入並設密；未設密時連線失敗＝非零退出。

**授權對賬**

- 孤兒授權列與「撤銷殘留」（撤銷後判定面降級窗內仍放行）是兩件事、不互稱。
- 風險例：選單路由名唯一索引只管活性列＝軟刪選單之路由名可被新選單重用、指向舊名之孤兒列即對新選單生效——此即偵測價值所在。
- 對賬只讀、只報；處置走 RUNBOOK；系統不自動刪。

**m0004 與 seed**

- 角色為資料庫叢集層物件：dev 庫重跑、pristine 驗證庫與既有角色並存之容錯（R1；`rev4:m012` 之已存在即略過形）；遷移身分須具建立角色之權（compose 之 postgres 啟動使用者具之；日後改用無此權之託管庫須另議）。
- schema 閘照相只含欄、索引、約束與資料＝看不到角色與 GRANT；權限面由 reaper 憑證之正負向測承擔。
- `audit:purge` 不受保護（比照 `ipRule:unlock`）：可撤、可授；誤撤可經角色頁加回。
- m0004 為一支（角色、GRANT 與 seed 同支；D6「併入 m0004」字面）；新列 id（預設顯式 165、m0003 形）與冪等形於 plan 期定；dev 庫序號可能已因走查前進。
- 判定面於開機全量載入：dev 庫於 rust-api 在跑時手動遷移須重啟 rust-api。

**前端與進場**

- seed-view-gate 豁免兩列於交付頁之同單元摘除（摘列早於或同顆於 BL-00045 刪列）；route 譯文型為以路由鍵為鍵之 Record＝route 譯文不能先於 view 落地。
- 側欄兩項煙測判準反轉：裸鍵與 No match → 正常進頁（判準走側欄路徑）。
- CDP 一律以快速登入鈕登入：32080 登入頁預填之 `Soybean` 非 rev6 seed 帳號、送出會留失敗紀錄並觸發節流。
- view-render-guard 常駐守兩頁新目錄（禁原始 HTML 注入、表頭 prop 形錨）。

**測試與走查**

- reaper 與存取日誌對走查與真庫測試之互擾（R3、R4）：走查期間不起 jobs；存取日誌列由還原工具之清理面處置。
- dev 庫寫入步驟逐步取 user 放行（LL-00053）；走查前後 snapshot／diff／restore（RUNBOOK §9c）。

**繁中**

- 繁中驗收涵蓋全部接真頁面（含 007 已審各頁與本刀兩頁、浮層、提示；D12）；CDP 對照兩側先顯式設簡中（ADR-00084 決定 8）。

## Requirements *(mandatory)*

### Functional Requirements

**A. 端點、授權態與契約總則（ROUTES 61→66）**

- **FR-001**: ROUTES MUST 由 61 條擴為 66 條、路由條數常數同 commit bump；新增 5 條逐字對齊 001 凍結 seed 之政策列——`/systemManage/getOperationLog`（GET；列 139）、`/systemManage/getAccessLog`（GET；列 140）、`/systemManage/getLoginAttempt`（GET；列 141）、`/systemManage/getSessionEvent`（GET；列 158）、`/systemManage/purgeAuditLog`（POST；列 159）；零新政策列。
  政策保護端點數 45→50；contract case 登記表之 case 集 MUST 與 ROUTES 恰等（66＝66、雙向覆蓋閘）；routes 生成表由 generate 重算；外層 routes 生成器之真 repo 釘值測 MUST 同批 +5 列；ROUTES 改動之單元另跑 `python3 -B tools/docsync test`。
- **FR-002**: 授權態 MUST 逐列照 seed：五支只授 R_SUPER、皆非受保護＝不屬封死集、可授出（D5）；可授出集 30→35（ADR-00081 款 9 改述）；ADR-00066 射程款同顆複核（候選外之 R_SUPER 端點列 5→0）；越權 `5003`、未帶權杖 `8888`、動詞不符 `4040`。設定兩支端點（列 66／67）維持受保護＝封死集、不下放（工程判斷④）。
- **FR-003**: 回應 MUST 逐欄白名單構造（絕不序列化原始資料列）：欄名 camelCase；id 為 number 並守 2^53 上界；時間為帶 `+00:00` 之 RFC3339、前端原樣顯示（ADR-00061）；操作者與使用者名以第二發批次查詢補齊（查無＝null）。
- **FR-004**: 業務拒因 MUST 為純 i18n key、一因一鍵；攜參例外 MUST 恰三鍵＝既有 `biz.user.passwordPolicy`、`biz.user.pwdSetTooFrequent`＋本刀 `biz.audit.purgeBelowFloor`（攜 `{minDays}`；D7）；`biz.audit.invalidTable` 純 key；錯誤變體數 MUST 維持 11、13 碼矩陣與可發碼集不變。
  新增拒因鍵 MUST 隨首個發出它的單元落地（名冊、三檔 locale 後端子樹、型別樹同批）、每鍵在契約測試之真 seed 應用面實際發出（名冊雙向閘）；三語譯文 MUST 只放佔位符 `{minDays}`、與後端明細頂層鍵逐字相等（佔位符對賬已在 ADR-00076 決定 7 射程）；msg-key-gate 之射程鍵常數與明細型之家同擴（是否構成 RL-0080「增判準」於 plan 期依其字面判；工程判斷⑲）；鍵名與實數於 plan 期 contracts 定案（預設＝上列兩鍵、`rev5:008` 名冊形）。
- **FR-005**: wire 型 MUST 開獨立命名空間 `Api.Audit`（`rev6-` 前綴新檔、不入 barrel）；本刀新增之全部 wire 型（四源列型與過濾參數型、清理請求與回應、設定讀型擴充）MUST 入 wire 裁判受審名冊、各配正向＋反例；欄名對齊 rev6 表形；新 wire 型之 i64 欄掛守衛序列化。
- **FR-006**: 讀端 query 參數 MUST 全取可缺之字串並寬鬆解析：空字串＝未設、畸形＝未設；絕不因 query 形回裸 4xx。

**B. 四源讀端（島 J1、J4）**

- **FR-007**: 四支讀端 MUST 只讀交易、零寫入（島 J1：稽核查詢純唯讀；其測試射程＝讀端 handler 與其交易、不含中介層之存取日誌列）；MUST 回共用分頁信封（current 預設 1 下界 1、size 預設 10 夾於 [1, 100]）；固定序 `created_at` 降冪、`id` 降冪決勝、不收排序參數（ADR-00058；工程判斷⑤）；時間過濾 MUST 為 RFC3339 之 [`timeFrom`, `timeTo`)、畸形＝未設、顛倒＝空頁。
- **FR-008**: getOperationLog 過濾維 MUST＝資料表名（等值）／動作（等值、大小寫敏感）／操作者 id 或名（id 優先；名對應含已軟刪同名之全集）／時間區間；列 MUST 含變更前後快照（可缺席）與來源欄。
- **FR-009**: getAccessLog 過濾維 MUST＝HTTP 方法（等值）／狀態碼（等值）／路徑（部分字串、萬用字元字面化）／操作者 id 或名／時間區間；列 MUST 含方法、路徑、狀態、操作者與來源欄；狀態碼＝HTTP 狀態碼（記錄層所見：權限不足 403、其餘含業務拒因與系統錯誤皆 200；找不到 404 只由路由最外層 fallback 構造、不經記錄層＝零列）＝業務成敗不在存取日誌之已知態（clarify Q2）。
- **FR-010**: getLoginAttempt 過濾維 MUST＝嘗試帳號名（部分字串）／成敗（嚴格 `true`|`false`、值域外＝未設）／來源 IP（精確等值）／時間區間；該源無操作者維。
- **FR-011**: getSessionEvent 過濾維 MUST＝使用者 id 或名／事件型（等值）／原因（等值）／時間區間；列 MUST 含 sid、事件型、原因、使用者與來源 IP。
- **FR-012**（`rev5:B-078` 確認句）: 讀端 MUST 零稽核欄複驗入口；來源 IP 過濾 MUST 為精確等值（IPv4 /32、IPv6 /128）、MUST NOT 以字串包含實作（路徑與帳號名之部分字串比對屬一般文字欄、非 IP 欄）。
- **FR-013**: 個資打碼（D9；島 J4）MUST 於讀端序列化單點執行：鍵常數 `userPhone`／`userEmail`、只掃快照頂層（深度一層）、變更前後各一次；手機字串長於 5 字＝前 3＋`****`＋後 2、否則全遮 `****`（不保留原長度）；信箱字串含 `@`＝首字＋`***`＋`@網域`、無 `@`＝首字＋`***`；非字串值與非物件快照原樣；資料庫原值 MUST NOT 改；拆掉打碼呼叫 MUST 有測試轉紅。
- **FR-014**: 來源欄 MUST 上 wire：XFF 原文（建構點已保證零 CR／LF 且 ≤1024 字元）、peerIp、ipConfidence、region、traceId（後兩者無料源恆空）；讀端照原字面回、MUST 容忍 003 期 `nginx_peer` 舊信心值。

**C. 水平線清理（手動；島 J3）**

- **FR-015**: purgeAuditLog 請求 MUST 為 {`table`, `beforeDays`} 二欄、寬鬆收單（body 解析恆不失敗＝固定序不可繞過）；`table` 四值白名單＝`operationLog`／`accessLog`／`loginAttempt`／`sessionEvent`（目標表依序為 `sys_operation_log`／`sys_access_log`／`sys_login_attempt`／`session_event`）。
- **FR-016**: 清理 MUST 依固定序判定（次序不可反；工程判斷⑥）：

  | 序 | 判定 | 違反 | DB 副作用 |
  |---|---|---|---|
  | ① | `table` ∈ 四值白名單 | `2222`＋`biz.audit.invalidTable`（純 key） | 零（不觸 DB） |
  | ② | `beforeDays` ≥ `PURGE_MIN_DAYS`（30；缺席或畸形＝0） | `2222`＋`biz.audit.purgeBelowFloor` 攜 `{minDays}`（攜參明細之唯一構造點） | 零（不觸 DB） |
  | ③ | 操作者解析（請求上下文；缺席或位址不可解析） | `5000` 拒寫、MUST NOT 以佔位補列 | 零（不觸 DB） |
  | ④ | 單一交易：目標表水平線刪除＋同交易操作日誌自記 → commit | 任一步失敗＝整筆回滾、`5000` | 原子：全有或全無 |

- **FR-017**: 水平線 MUST＝早於（現在 − `beforeDays` 天）之列整段刪除、禁挑列；操作日誌源之刪除 MUST 永久豁免動作 `purge` 之列；自記列 MUST＝動作 `purge`、`entity_table`＝目標表名、`entity_id` 空、變更後快照＝{`table`, `before_days`, `deleted_count`}（刪 0 列照落）、操作者與來源欄取請求上下文；回傳 {`deletedCount`}；自記失敗 MUST 整筆回滾（絕不吞自記錯誤）。
- **FR-018**（`rev5:B-125`）: 清理原子性 MUST 有 fault-injection 級測試釘住：注入自記失敗 → 斷言整筆回滾、回錯誤、零刪除零自記（非 vacuous、附紅綠證）；必要時於測試基建增注入資料庫連線之薄殼（沿用既有應用狀態建構、不新增其建構字面）。
- **FR-019**: `PURGE_MIN_DAYS`＝30 MUST 為碼內單一權威常數；reaper 排程清理之下限 MUST 直接引用同一常數（同 crate、不鏡像；工程判斷⑦）；前端清理浮層之天數下界照 rev5 抄為 UX 護欄、碼註寫明權威在後端。
- **FR-020**: 操作稽核動作詞彙 MUST 由封閉八詞擴為九詞（新增 `purge`；只在尾端追加）、字面釘值測同改；ADR-00082 款 3 之寫入者全集 MUST 以現行全集重述（既有＋設定寫端〔FR-027〕＋手動清理自記＋排程清理自記〔FR-036〕；ADR⑥）。

**D. 存取日誌寫入（島 J2；B2）**

- **FR-021**: 存取日誌寫入中介層 MUST 只掛已認證子路由、位於認證之後而包住授權判定（授權拒絕之請求照記；工程判斷㉒）；公開子路由構造上不掛＝未認證零列（表之操作者欄 NOT NULL 兜底）；MUST NOT 設豁免名單（稽核讀端自身亦記）。
- **FR-022**: 每列 MUST 記：操作者 uid、HTTP 方法、路徑（只取請求路徑、MUST NOT 含 query string、MUST NOT 讀 body）、回應之 HTTP 狀態碼（MUST NOT 新增業務碼欄；clarify Q2）、真實來源位址、對端、XFF 判定窗轉錄、信心；region 與 trace_id 無料源＝空。
- **FR-023**: 寫入 MUST 於回應之後非同步進行（MUST NOT 同步等待寫入完成）；請求上下文或身分缺席 MUST 跳過（不 panic、不 500）；寫入失敗 MUST 只發結構化告警（告警 ③d 依其 as-built 欄位重錨）＋降級 metric、業務回應零影響（fail-open）。
- **FR-024**: 中介層 MUST NOT 改動連線池設定（不觸 BL-00147 之臂）、MUST NOT 進入登入路徑或改動其判定次序（不觸 BL-00145 之臂）；ADR② MUST 解除 004 刀 research 防回歸清單 B 之 `rev5:R2-9`（`access_log_mw` 不搬；其 rev5 原因＝歸 `rev5:B-016` 稽核域射程、非否決判斷）並記射程、fail-open 方向與 R3 對策。
- **FR-025**: 存取日誌之寫入 MUST 經新 facade（資料列構造只住 facade）；走查還原工具與 schema 閘之 runtime-append 常數（兩檔同值互釘）MUST 擴入 `sys_access_log`、還原清理面同評估、配自測；RUNBOOK §9c／§12 與 schema 閘收窄射程字面同批（工程判斷⑮）。

**E. 系統設定後端（D1；工程判斷③⑬⑭）**

- **FR-026**: 設定讀端 wire MUST 擴充：每列下發登記表宣告界（number 型之上下界）與「是否在登記表宣告集內」旗標；宣告集外列 MUST 不下發界值；wire-schema 快照同步；不另立界值真源（ADR-00054 翻案觸發器不成立）、前端 MUST NOT 抄鍵集（ADR-00057）。
- **FR-027**: updateSystemSetting MUST 於同交易落一列操作日誌：動作 `update`、`entity_table`＝`system_settings`、`entity_id` 空、變更前與變更後各為整列快照（鍵在快照內；g4）；操作者取自請求上下文、缺席＝拒寫 `5000`、MUST NOT 以佔位補列；寫入被拒（拒因）＝零寫入、零稽核；後端既有「設定寫入零稽核」測試 MUST 反轉。
- **FR-028**: ADR-00091（續行 ADR-00080；plan 期更正：spec 原指 ADR-00080、該 ADR 已被 ADR-00091 supersede）之設定域觸發器（「系統設定寫端被重寫」）MUST 重評並寫入續行 ADR：結論＝維持——設定值逐鍵驗型與界、空字串於 number 與二值 enum 型皆不合法（`2222`）、不新增「清空」語意；同值寫入照寫並照落一列稽核（本刀起與角色選單域同形；ADR⑧′＝續行並 supersede ADR-00091、改寫其決定 8 逐域差異表之設定域格）。
- **FR-029**: 系統設定兩檔碼註之前代歸因 MUST 順改（工程判斷⑬）：「rev5 後刀的同 txn op-log 不帶回」改為現在式 as-built（同交易落 `update` 稽核）＋史述一句（002 刀不帶 rev4 之同交易稽核、本刀 D1 翻案）；裸引之 research 條號所指為 rev5 者補 `rev5:` 前綴（所指為本庫 002 刀 research 同號條者維持）；連 assert 訊息一併改時以容器 cargo 驗。

**F. reaper 三 job（B1、B4、D8）**

- **FR-030**: reaper bin MUST 以 rev4 藍本重打字（rev4 出處帶 `rev4:` 前綴、註解重寫）；CLI MUST 為 `--execute`（缺席＝dry-run）＋`--job <name>`（`token-reap` 預設｜`audit-retention`｜`policy-reconcile`）；未知參數與未知 job 名 MUST 嚴拒（非零退出＋錯誤事件）；退出碼 0＝完跑（含 0 列）、非 0＝任一步失敗；失敗 MUST NOT 推成功心跳；心跳推送 best-effort、MUST 附全程時限、失敗不改退出碼（工程判斷⑨）。
- **FR-031**: reaper MUST 以 `reaper_database_url`（m0004 所建最小權限 role；既有設密腳本開登入並設密）連線、MUST NOT 掛 `database_url`。
- **FR-032**: token-reap MUST 以單一語句刪除過期逾寬限天數之票（`REAPER_GRACE_DAYS` 缺席或畸形退 7、畸形告警）；dry-run 輸出候刪數、零變動；MUST NOT 落操作日誌自記（票回收屬會話域、非稽核表之水平線清理；只結構化日誌與心跳；rev4 形）。
- **FR-033**: audit-retention MUST：固定表序（操作日誌→存取日誌→登入嘗試→會話事件）；逐表單交易「水平線刪除＋自記」、與手動清理同謂詞同自記形（島 J3）；dry-run 逐表計數（謂詞同形）、零變動零自記；任一表失敗＝結構化錯誤＋非零退出＋不推心跳（已 commit 之表維持）。
- **FR-034**: 四表保留天數環境變數（`AUDIT_RETENTION_{OPERATION_LOG,ACCESS_LOG,LOGIN_ATTEMPT,SESSION_EVENT}_DAYS`）MUST 三分語意：缺席＝90；畸形（無法解析為非負整數）＝結構化告警＋取 90；解析成功且小於 `PURGE_MIN_DAYS`（含 0）＝開跑前四鍵一次全驗之前置全拒（指名鍵與值、非零退出、不推心跳），且驗證 MUST 先於資料庫連線；每輪間隔 `REAPER_INTERVAL_SECS`（dev loop 缺席退 86400）；設定頁維持 16 鍵、零 seed（D8）；RUNBOOK 寫明。
- **FR-035**: policy-reconcile MUST 唯讀逐維（選單、按鈕、端點）計數孤兒授權列（定義見 Key Entities）、輸出結構化日誌（指名維與計數）＋心跳 metric（逐維計數＝每維一條 gauge、以標籤區分維）、任一維非零即告警；有無 `--execute` 皆 MUST 零寫入（不刪、不歸檔、不寫稽核）。
- **FR-036**: 排程清理自記列 MUST 為（g2、g5；工程判斷㉕）：`created_by` 空、`real_ip`＝哨兵 `0.0.0.0`、`ip_confidence`／`peer_ip`／`x_forwarded_for` 皆空、變更後快照帶 job 字面與 {`table`, `before_days`, `deleted_count`}；刪 0 列照落（每輪四列）。寫入路徑 MUST 與 HTTP 寫端分離：操作者型之構造保證（唯一建構點＝自請求上下文構造）不動，系統程序另立只收碼內 job 字面之具名型（形制 plan 期定）；`model/audit.rs` 檔頭「沒有『自己填一個位址』的路」句 MUST 同批改述為兩路之現在式；HTTP 寫端照舊只轉錄請求上下文、缺席拒寫 `5000`；ADR③ MUST 寫明哨兵＝無網路來源之標記（001 data-model 前瞻註「sentinel 或另議、不回改本欄」之兌現）、非島 F 之 F3①與島 E 末點所禁之「有操作者而取不到其位址時以佔位位址補足」（R13）。
- **FR-037**: 三 job MUST 各自心跳分組（grouping key 按 job、PUT 整組替換；`reaper_last_success_timestamp`／`reaper_deleted_total`＋對賬計數 `reaper_orphan_policies{dimension}`；contracts/reaper-cli.md 定案）；pushgateway 推送之 HTTP 實作 MUST 於 plan 期比較（甲＝既有 `metrics-exporter-prometheus` 之推送功能、乙＝rev4 藍本之 ureq）並記入 ADR③（plan 期定案＝乙；版本＝3.4.2、user 2026-10-21 plan 期擇定）；任一新依賴 MUST 釘完整版號、依全域 §6 以「參照專案 lockfile 值」與「官方最新穩定版」兩源比對，分歧即問 user（工程判斷⑩）。
- **FR-038**: compose jobs 段 MUST 改為現況（「rev6 無 reaper bin／role、起了也跑不動」句改 as-built）；dev override 姿態（loop 每日一輪）照舊；`REAPER_INTERVAL_SECS` 與告警⑤／⑥門檻之 2× 互錨三檔同步。

**G. m0004、seed 基線與離線對賬腿**

- **FR-039**: 本刀 MUST 恰新增一支 delta migration `m0004`（一支：D6「併入 m0004」與 B1 字面、clarify 步定案；不建表），內容 MUST 恰為：

  | 對象 | 改動 | 演進帳 | 承載 |
  |---|---|---|---|
  | reaper role | 建立（無密碼、不可登入；已存在即略過之容錯形） | 權限面、不入演進帳 kind（schema 閘照相不及；登記形 plan 期定） | B1、B4 |
  | reaper role 之 GRANT | schema USAGE；`sys_token` SELECT／DELETE；四稽核表 SELECT／DELETE；`sys_operation_log` INSERT 與所需序號權；授權域三表（`casbin_rule`、`sys_menu`、`sys_role`）SELECT | 同上 | B1、B4 |
  | `sys_menu` 77（`manage_audit`）之按鈕清單 | NULL → 恰一碼 `audit:purge`（說明字面「清理日誌」：user 2026-10-21 plan 期擇定） | `seed_update` | D6 |
  | `casbin_rule` 新列（R_SUPER 之 `audit:purge`；按鈕維） | 新增（受保護 FALSE、治理欄照 seed 形；id 預設顯式 165） | `seed_add` | D6 |

  遷移後 MUST：授權列數 163→164、序號 164→165、受保護列 25 不變、R_SUPER 按鈕碼 21→22、選單列數 78 不變；seed 部分屬 seed 基線層（島 G 之 G2 末句「受保護集之變更屬 seed 基線層級決策」同層）——直接改列、MUST NOT 走執行期之撤銷歸檔與操作稽核；遷移以 compose 之 `database_url` 身分執行（具建立角色之權）；遷移服務先於 rust-api 啟動、判定面開機即載新值。
- **FR-040**: 演進帳 MUST 登記 m0004 之 seed 筆（自 E-010 起；來源刀＝008）；新列序號合成 MUST 照 007 GR9 形（全新庫序號期望值隨新列推進）並配自測；schema-definition MUST NOT 前進（ADR-00087）；收刀前 MUST 跑 Day-1 登記三步（RUNBOOK §10；第 3 步以全新庫驗）。
- **FR-041**: BL-00148 之零 docker 離線對賬腿 MUST 於 m0004 單元之前落地：解析 delta migration 之 SQL 常數，與演進帳及凍結 seed 前值逐筆對賬；樣本 MUST 涵蓋 m0003（seed-only）與 m0004（角色 DDL＋seed）；DDL 類語句之處理（略過或結構化登記）於 plan 期定；配一正一反＋逐判準停用變異；掛點於 plan 期定；需 docker 之 `tools/schema-gate.py check` MUST 維持不進 pre-commit 常跑鏈（工程判斷⑫）。
- **FR-042**: seed 錨定之測試與現在式文件 MUST 隨 m0004 改對：授權列數 164 與新列 id、R_SUPER 按鈕集含 `audit:purge`、seed 三帳號之帳號資訊按鈕集、選單 77 按鈕清單；受保護列 25 不變；reaper role 權限以 reaper 角色身分之正負向測釘住（容器全量測試內交易中 `SET LOCAL ROLE reaper`：允許語句成功、權限外語句被拒）；以 reaper 憑證實連之驗證＝設密腳本自驗＋jobs profile 活體一輪（plan 期定形）。

**H. 觀測層（B5 與重錨）**

- **FR-043**: 告警規則 MUST 依 as-built 重錨：③d（accesslog-write-fail）綁存取日誌寫入失敗之 as-built 結構化欄位；⑤⑤b（token-reap 心跳與模式）與⑥⑥b（audit-retention 心跳與模式）之「無事件源」現況註改為有源現況；④ audit-capacity 之「rev6 尚無該 handler」註改述；MUST 新增對賬告警兩條：①任一維計數大於 0 即告警 ②對賬心跳逾時（門檻沿⑤／⑥之 172800＝每輪間隔之 2 倍、納入同一組三檔互錨）；規則名於 contracts 定案（沿 obs016／obs017 形；主線工程判斷、clarify 步定案）；RUNBOOK §11 MUST 補 audit-capacity 告警之處置子節（判讀＋經稽核頁清理或待 reaper 下一輪；比照 §11.3 形；工程判斷⑯）。
- **FR-044**: 儀表板 MUST（BL-00139）：`rust-api.json` 刪除兩支 HLL 面板與「設定讀取頻次」面板並重排版位；`reaper.json` 三面板與 `master-overview.json` 一面板之 reaper 描述改 rev6 as-built；`audit-log.json` trace_id 下鑽面板與 `trace_id` 變數之描述改述為「rev6 稽核列此欄恆空」；可選起 obs／metrics profile 活體驗證。

**I. 前端——系統設定頁（§III.2 (ix)）**

- **FR-045**: 系統設定頁 MUST 為單檔、資料驅動：控件由伺服器回之 `settingType` 決定（二值 enum→開關、number→數字框、其他→唯讀呈現原值）；四組固定序（密碼策略／工作階段／IP 源登入／帳號登入；依鍵前綴歸組＝`password_`→密碼策略、`ip_`→IP 源登入、`login_throttle_`→帳號登入、其餘→工作階段；組內固定鍵序、未列序新鍵排組尾保伺服器相對序；空組整卡不渲染；rev5 形）；前端 MUST NOT 硬編鍵→控件對應。
- **FR-046**: 逐項即改即存 MUST：開關切換即提交；數字欄失焦或 Enter 提交（值未變不送）、清空不送；提交後（成功與失敗皆）MUST 回讀伺服器全列收斂畫面；成功提示、失敗走既有攔截層之 i18n 轉譯；數字框之上下界 MUST 取自讀端下發之宣告界（FR-026）、10 個 number 鍵一律鉗界（越界輸入失焦即鉗至界值後送出；clarify Q1）；宣告集外列 MUST 唯讀、排組尾、標示 description。
- **FR-047**: 三對跨鍵矛盾 MUST 即時警示、不阻存（D2；工程判斷㉔）：判準＝`password_min_length` ＞ `password_max_length`、`login_throttle_captcha_after` ＞ `login_throttle_max_fails`、`ip_captcha_after` ＞ `ip_max_fails`（嚴格不等式、相等合法）；警示 MUST 落在該對所屬之組卡片並寫出後果（密碼對＝三個設密入口一律拒；節流兩對＝後端該維三鍵整組退回出廠常數）；三語；維持 ADR-00079 決定 2（後端照舊逐鍵驗、不新增組合守門）。
- **FR-048**: 寫入政策七鍵（`password_min_length`／`password_max_length`／`password_require_digit`／`password_require_lowercase`／`password_require_uppercase`／`password_require_special`／`password_forbid_username`）任一成功 MUST 呼叫密碼政策 hook 之清除函式（D3）；hook MUST 增清除函式，其檔頭「只增不清」與「寫入者唯一」句、重設密碼浮層檔頭之快取已知態句 MUST 同批改述；RUNBOOK §11.3「008 刀前無設定頁畫面＝走 API」MUST 改為設定頁首選。
- **FR-049**: 16 鍵之 label＋help MUST 三語全映射（凍結 seed description 不可改＝不以 description 退底；未映射之新鍵才以 description 遞補）；帳號登入與 IP 源登入兩組之說明 MUST NOT 承諾嚴格上限（工程判斷⑰；BL-00145 約束）。
- **FR-050**: 設定頁 MUST 接既有設定 wrapper 兩支（型別隨 FR-026 擴充）；頁內零按鈕級 gating（設定頁不設碼；工程判斷④）。

**J. 前端——稽核頁（§III.2 (x)）**

- **FR-051**: 稽核頁 MUST 四源四分頁（操作日誌／存取日誌／登入嘗試／會話事件；照 rev5 形：主頁＋四支搜尋卡＋清理浮層＋共用時間區間邏輯）；各分頁搜尋卡同構（預設展開、重設清空並觸發搜尋、時間區間本地輸入而 UTC ISO 上 wire〔D4〕）；搜尋卡之輸入提示範例 MUST 用庫內實際字面（動作過濾為大小寫敏感等值，範例如 `update`、`kick`；rev5 提示寫大寫範例而照輸查無資料＝本刀文案照實、入分岔表）；重新整理鈕不重置頁碼、搜尋回第 1 頁；每頁預設 10 筆可調。
- **FR-052**: 表格欄集 MUST 逐分頁照 rev5（`rev5:008` FR-B07；工程判斷①②）：XFF 於操作／存取／登入三分頁純文字插值（截尾＋懸停全文）＝與 rev5 零分岔（rev5 之「UI 對照唯一例外」為其對 rev4 之身分、不帶入 rev6 分岔表）；traceId 三分頁渲染（恆「-」）；region 存取／登入兩分頁渲染（恆「-」）、操作分頁不渲染；peerIp、ipConfidence 不渲染；會話事件分頁無 XFF 欄；橫向捲動寬度＝欄寬總和隨欄同批。
- **FR-053**: 操作日誌之「查看快照」MUST 以唯讀浮層純文字 JSON 呈現變更前／後（值已由後端打碼；無快照提示）；排程清理自記列之操作者顯「-」、來源 IP 顯 `0.0.0.0`；設定變更列之標的 id 顯「-」（g2、g4）。
- **FR-054**: 清理入口 MUST 每分頁一顆、共用單例浮層（標的隨分頁切換、浮層標題帶標的表名；唯一輸入欄＝保留天數〔下界 30 之 UX 護欄、無上界、每次開啟重置為 30〕；警語＋二次確認〔浮層為第一步、確認泡泡為第二步〕；成功提示帶刪除筆數並刷新該分頁；rev5 形）；清理鈕 MUST 依 `audit:purge` 碼顯隱（D6）。
- **FR-055**: 登入嘗試分頁 MUST 帶「節流短路遭拒不落表」語意之告示、MUST NOT 承諾嚴格上限；存取日誌分頁 MUST 帶「狀態欄為 HTTP 狀態碼：權限不足顯示 403，其餘請求（含業務拒絕與系統錯誤）皆顯示 200」語意之告示（比照登入嘗試分頁、三語；clarify Q2；plan 期 user 親決只提 403、不提 404＝表內恆無 404 列）；零匯出、零前端排序、零快照內容搜尋（rev5 同）。
- **FR-056**: 稽核頁之 API 包裝與型別 MUST 為 `rev6-` 前綴新檔與 `Api.Audit` 獨立命名空間（§III.1 BASE-WEB-WRAPPER／ADAPT；不入 barrel、直接路徑匯入）；自由文字欄一律純文字插值、新檔 MUST 過 view-render-guard。

**K. 進場面（路由、譯文、seed-view-gate）與 fork-delta**

- **FR-057**: 兩頁路由 MUST 經路由外掛重算產出（產物四檔零手改、route-artifact-gate 冪等）；三語 `route:` 樹各補兩鍵、`page:` 樹各補兩頁之節、`app.d.ts` 之 `Schema.page` 型節同批（三語鍵集 MUST 相等、由型別機器守）；route 譯文 MUST 與 view 同單元或其後落地；選單可見性照 seed（兩頁選單維只授 R_SUPER：政策列 69／142）。
- **FR-058**: seed-view-gate 之具名豁免兩列（seed 選單列 9 與 77）MUST 於交付各頁之同單元摘除（摘列早於或同顆於 BL-00045 刪列；ADR-00071 後果）；自測改斷言空表、綁真豁免鍵之案（`TestExemptInvariants`、`TestRunCheck`）同改；同檔「恰兩列」之現在式字面改對、檔頭 rev5 原始版史述句不改；側欄兩項煙測判準 MUST 反轉（裸鍵與 No match → 正常進頁）。
- **FR-059**: fork-delta 檔集 MUST：修改型 inline 只出現於既有授權用途與 Amendment 新授之 (ix)(x)；新增型以圈界；新檔（兩頁 view 與其模組、稽核 wrapper 與型別）以檔頭一行；base-web 變更檔集 MUST 以機器斷言 ⊆ 授權檔集＋新增檔；`components.d.ts` 若有變化只許工具重算形；修改型標記逐行 `原行:`。

**L. 憲法 Amendment、ADR、工具與帳本**

- **FR-060**: 憲法 Amendment MUST 一次 MINOR（1.8.1→1.9.0）、獨立 commit、條文字面由 user 逐款親決（D10；時點＝plan 期——依 ADR-00089 決定 4／7、user 2026-10-21 plan 期裁定；起草輸入見工程判斷㉓）：
  ①§I.7 島 J 入憲 J1～J5：J1 以 `rev5:ADR 0077` 字面為底、補回 rev4 島 J1「存取日誌由統一記錄層承載、非查詢職責」分句（不補則「稽核查詢純唯讀」與「稽核讀端之請求亦落存取日誌列」表面互斥）；J2 以 rev4 島 J2 字面為底回填（存取日誌寫入失敗不擋請求只告警、不記請求內文與查詢字串、未認證零列、位址取信任錨）；J3 射程含 reaper 排程清理與其自記列形（哨兵 `0.0.0.0`、操作者空、刪 0 列照落）；J4 個資打碼（讀端單點）；J5 一句指針指島 E 末兩點（ADR-00042）
  ②§I.6 變體 B 括號句改 J3 交叉指針；§I.7 表尾句之 J2 空缺位處置；MAJOR 射程句「九島」改十島；承襲指針 J 列補 rev6 入憲載體
  ③§III.2 `BASE-WEB-MANAGE-PAGE-WIRING` 新用途 (ix) 系統設定頁進場、(x) 稽核頁進場（形照 (i)／(iv)：範圍欄只列 upstream 既有檔＝`{en-us,zh-cn}.ts` 之 `route:`／`page:` 新增型塊、`app.d.ts` 型節、路由產物四檔；`zh-tw.ts` 為 rev6 自有之整檔新增型檔、不入範圍欄，三語由行為欄「三語鍵集 MUST 相等」與型別守承擔；(x) 寫明 `audit:purge` 顯隱）
  ④活書狀態句同顆改現在式（10 §10.2 導言與 frontmatter、C4-E2 保留期段之「未入憲」句等）、generate；活書 06／10 之島 J 情境本體屬 as-built，依 FR-064 於行為落地後寫（RL-0048；007 刀 S-a 前例）。⑤（plan 期補）§III.2 `BASE-WEB-I18N-WIRING` (i) 紀律欄「錯誤明細轉譯只限兩鍵」改三鍵——增稽核清理下限天數之具名插值；`src/service/request/index.ts` 之改動落既有新增型圈界塊內、範圍欄處數不變。範圍欄初值依表外宣告 1 例外路徑預估、收刀前 PATCH 實數化（前例 ADR-00051）。Amendment accepted 前 base-web 既有檔 MUST 零 diff。
- **FR-061**: ADR MUST 於 plan 期起草（feature branch 內、序號接續；proposed 期不宣告 supersedes、accepted 同顆補；親決依 ADR-00089 分類）＋收刀前 PATCH Amendment 一支（配號＝當下下一號、plan 期不起草）：①島 J 入憲與 §III.2 (ix)(x)（Amendment；provenance `rev5:ADR 0077`；FR-060）②存取日誌寫入（解除 `rev5:R2-9`；FR-021～FR-025）③reaper 三 job 與最小權限 role（哨兵與刪 0 列照落、孤兒授權列只報不刪＋RUNBOOK 處置、心跳與告警重錨、HTTP 依賴取捨與版本；FR-030～FR-038）④錯誤明細通道三鍵（整顆 supersede ADR-00076〔其標題「射程恰兩鍵」被推翻〕；另一款釐清 ADR-00076／ADR-00090 決定 1「照提示秒數重試必過」於牆鐘回撥不成立；FR-004）⑤ADR-00081 續行（角色與選單已知態：款 2／款 6 解除；款 9 可授出集 30→35；款 10 改述＝設定頁「看得到、讀寫 `5003`」與稽核頁 `audit:purge` 碼顯隱之可見效果；稽核選單維〔政策列 142〕之非超管頁內形另立一款；ADR-00066 射程款複核結論；活書 11「十八款」改十七款〔款 2、6 解除、另立款 22〕）⑥ADR-00082 續行（IP 域已知態：款 3 寫入者全集與動作詞彙八→九；FR-020）⑦授權歸檔表永久保留（B3 by-design；歸檔列除經復原外永久保留、零碼改；ADR-00065 代價句之承接）⑧設定頁進場複核（ADR-00079 觸發器＝前端即時提示不擋；ADR-00054 觸發器不成立；ADR-00057 宣告集外列之呈現與判別；ADR-00091 設定域觸發器重評結論〔FR-028；另立⑧′續行 ADR-00091〕；ADR-00064 不下放；密碼政策快取清除與數字框 10 鍵一律鉗界〔clarify Q1〕之刻意分岔）⑨m0004 seed 與 role（演進帳登記、序號合成、Day-1 三步；ADR-00008 delta 第二支；FR-039～FR-042）⑩刻意分岔登記（可併入本 spec 分岔表、是否另立 ADR 於 plan 期定）。
  親決時點：Amendment 顆只含 ADR① 與其連動條文、其餘另顆。
- **FR-062**: 工具 MUST：走查還原工具與測試守衛評估 reaper 與存取日誌之影響（走查期間不起 jobs；FR-025）；子句表檢核工具（FR-071）；本刀若改動既有 python 閘之正則判準（msg-key-gate 模組層 `RE_*`、zh-tw-lint、fork-delta-lint 等），該單元 MUST 先以 `python3 tools/regex-mutants.py run` 取全成分清單、存活者逐支補殺案或附等價證明並預估代價（工程判斷⑲；既有存活數 zh-tw-lint 30／46、fork-delta-lint 9／13 為 maint-pre008-carriers 實測、repo 未記；LL-00097 前例代價）。
- **FR-063**: 碼註與現在式文件 MUST 改為 as-built：稽核模型與四支稽核 facade、登出 handler 之「`rev5:008` 增量不帶」「沒有 delete」類句（清理入刀後寫明水平線清理是唯一刪除路徑）；告警規則④之「rev6 尚無該 handler」；compose jobs 段（FR-038）。
- **FR-064**: 活書 MUST 於 feature branch 內改為現在式 as-built：06／10 島 J 情境；05 `tools/` 列「恰兩列」與 seed-view-gate 描述；07 jobs profile 現況；08 稽核頁時間輸入語意（本地輸入、UTC 顯示）與存取日誌狀態欄語意（HTTP 狀態碼、業務成敗不在其內；clarify Q2）；11 角色與選單已知態款數（十八→十七）、IP 域已知態寫入者；12 稽核域詞組（存取日誌、水平線清理、手動清理、排程清理、票回收、授權對賬、清理自記列、孤兒授權列；與既有「撤銷殘留」區分）；C4-L2 reaper 列與 C4-E2 隱私流節保留期句；RUNBOOK §3／§8／§9c／§10／§11／§12 現在式，另增孤兒授權處置一節（落點 plan 期定；g3），並寫明存取日誌狀態欄＝HTTP 狀態碼之已知態（落點 plan 期定；clarify Q2）。C4-L2 拓樸之容器集不變（reaper 與 pushgateway 既已在 compose）。
- **FR-065**: 本刀落地後成假述之現在式句 MUST 以 `python3 tools/docsync errata <詞>` 機器枚舉逐處判讀改對（RL-0011），種子＝`BL-00045`、`BL-00043`、`BL-00133`、`BL-00139`、`BL-00148`、`seed-view-gate`、`恰兩列`、`008 刀`、`島 J`、`未入憲`、`稽核域行為島`、`保留期`、`purge_before`、`沒有 delete`、`尚無該 handler`、`rev5:008`、`死項`、`view 未進場`、`設定頁 view 刀`、`view 刀`、`裸鍵`、`只增不清`、`起了也跑不動`、`無事件源`、`reaper bin`、`access_log_mw`；另點名（種子掃不到）：系統設定兩檔三行碼註（FR-029）、重設密碼浮層檔頭快取句、RUNBOOK §11.3 走 API 句、`schema-definition.md` §8 缺頁句（改為不隨刀前進之形、基線字面不動；改此檔時 pre-commit 跑 schema-gate test）。
- **FR-066**: 帳本 MUST 於收刀兌現：`backlog_done` 5 條＝BL-00043（FR-021～FR-025、FR-030～FR-038、FR-043）／BL-00045（FR-045～FR-058）／BL-00133（ADR⑦、FR-035）／BL-00139（FR-044）／BL-00148（FR-041）；反向確認 2 條＝BL-00108（本刀不於 rust 側新寫字元級解析 lint；探針取兩側函式名聯集〔同職異名三對 `close_of`↔`match_delim`、`split_top`↔`split_entries`、`attr_spans`↔`attr_group`，wire 側另有 `token_at`〕、計數口徑明寫其一〔字元切片參數之函式簽名行：common 6／entity 18／wire 21；或字元切片與字元向量之行數：common 7／entity 28／wire 25、限 `server/tests`〕；byte 級 lint 之三支輔助函式不計；工程判斷⑱）、BL-00002（零 AI 元件、不動 §9「目前無」句）；滯後卷約束照守（BL-00049 快速登入鈕刀期不拆、BL-00064／BL-00067 不碰 alova 與 demo 面、BL-00140 指針、BL-00141 不納、BL-00145 文案不承諾嚴格上限且不改登入判定次序、BL-00147 不動連線池設定與雜湊位次）；本刀零 `backlog_add`；`feature_close.adrs` 列全（plan 期 ADR＋收刀前 PATCH Amendment）、`arch_impact` 以收刀時 diff 現算之活書節號為準；NOTES 下一步 specify 起手後改 008 進行中。
- **FR-067**: 收刀計數三則 MUST 逐單元記次數、收刀 `feature_close` notes 同句彙記（含 0）：ADR-00011 翻案觸發器①（RULES fix 20／19 超限後之刀數）、ADR-00084「zh-cn.ts 新字未分類之紅」（本刀＝第 2 刀）、ADR-00052「一致性腿誤擋正常部分 commit」；本刀晉升 fix／review 範圍之 RL 依 RL-0052 一進一出（工程判斷⑳）。

**M. 測試與紀律**

- **FR-068**: 島 J 不變式 MUST 逐條有測：讀端零寫入（J1）、存取日誌 fail-open 與未認證零列（J2）、清理唯一形與原子自記（J3；含排程清理）、打碼單點（J4）、J5 所指島 E 兩點之既有測照舊。
- **FR-069**: 每支新端點 MUST 配 contract case＋覆蓋閘雙向＋case_key 綁定＋授權態矩陣對照 seed 政策列（含 m0004）；判定只呼單一進入點；handler 層零 path-root entity token；名冊閘（判定面、寫鎖、同步呼叫點）全綠；可授出集 30→35 以測試釘住。
- **FR-070**: 測試環境紀律 MUST：真表測試配清理守衛（四稽核表帶界水位、存取日誌之非同步寫入收尾對策〔R3〕、arm 當下現讀之序列值）；稽核斷言取水位窗、不寫絕對計數；reaper 測試對真庫不互擾（R4）；測試 MUST NOT 留下對 seed 列之變更；測後 schema 三閘綠；CDP 走查排 schema-gate 驗收之後、或走查後照 RUNBOOK §9c 還原；dev 庫寫入步驟逐步取 user 放行（LL-00053）。
- **FR-071**（D11；ADR-00097 決定 2b）: 需求追溯 MUST 沿用子句表、射程全四類：驗收場景、SC、FR、Edge Cases 全拆子句掛錨，子句表住 tasks.md（007 形）；MUST 自備檢核工具（以主線工作區之 007 前例改寫）並自證空錨與錨不符一律計不符、核數對得上總錨數；tasks 收刀清單 MUST 含「收單時重審工具入庫與通則化」一條（ADR-00097 翻案觸發器）。
- **FR-072**: 守門非 vacuous 自證 MUST（本條為自證索引）：清理固定序各步負向與同時違反之位次；原子性 fault-injection（FR-018）；打碼拆除即紅（FR-013）；存取日誌未認證零列、`5003` 照記、寫入失敗回應不變；reaper 環境變數三分語意、未知參數嚴拒、心跳失敗不改退出碼；排程清理自記之哨兵形與 HTTP 寫端仍拒佔位之對照；對賬計數之正負向植入；設定寫端稽核列（舊→新）與拒因零稽核；m0004 序號合成變異；離線對賬腿一正一反＋逐判準停用變異；reaper role 權限正負向。
- **FR-073**: CDP 三方對照 MUST 覆蓋兩頁全套（設定頁四組與逐項存、矛盾提示；稽核頁四分頁與搜尋卡、快照浮層、清理浮層）與側欄兩項（rev5 22080 vs rev6 32080、必要時 22089）；22080 側全程唯讀、對照步驟兩側顯式設簡中（ADR-00084 決定 8）；一律 127.0.0.1；以 Super 與 Admin 切換、沿用三顆快速登入鈕（BL-00049 條件依賴；期望＝Super 側欄有兩項且進得去、Admin／User 看不到）；真登入照 RUNBOOK §9c；CDP 操作一律 opus[1m]／xhigh；刻意分岔逐項登記（下表）；jobs profile 活體跑一輪（dry-run 與 execute 各一）。
- **FR-074**: 繁中驗收 MUST（D12、ADR-00084 決定 8 字面）＝zh-tw-lint 綠＋前端型別檢查綠＋AI 逐頁審讀紀錄涵蓋**全部接真頁面**（含 007 已審各頁與本刀兩新頁、浮層、提示）＋user 抽查並記錄；tasks 收刀清單審讀與抽查各一條。
- **FR-075**: 收刀 DoD MUST 全綠：容器內後端全量測試（全程 serial）＋contract 66 case＋前端型別檢查＋fork-delta-lint（新用途列名冊載入變異自證、範圍欄對賬腿、修改型只在授權檔）＋msg-key-gate（含佔位符對賬）＋wire 裁判 check＋schema 三閘（含 m0004 合成）＋路由產物冪等＋seed-view-gate（豁免已摘）＋view-render-guard＋zh-tw-lint＋docsync check／lint 零紅＋走查基準 diff rc 0＋CDP 三方對照（判準＝SC-011）；FR-001～FR-075 與 US1～US6 驗收場景全數對應至少一測試案、機器守或演練紀錄（子句表逐條映射、無承載者即紅）。

**★ 軌道逐處登記（憲法 §III.2 必需三欄：位置＋改動內容＋upstream 衝突風險評估）**

風險判準（承 004～007 刀 spec、可覆算；量測面＝base-web upstream `example` tip `8be6f9ba`〔提交日 2026-05-13〕、量測日 2026-10-20、以 `git log --since` 計檔級 commit 數：12m＝2025-10-20 起、24m＝2024-10-20 起）：**高**＝近 12 月 ≥5；**中**＝近 12 月 1–4 或近 24 月 ≥5；**低**＝近 12 月 0 且近 24 月 ≤4。
**修改型再 +1 級**、純新增型與產物檔不加級。收錄準則：新用途 (ix)(x) 授權面之 upstream 既有檔＋I18N 授權面之錨點檔；兩頁 view 與其模組、稽核 wrapper 與型別屬新檔，密碼政策 hook、設定 wrapper 與型別、重設密碼浮層屬 rev6 自有檔——皆不列；共 10 列（含一列候選；`src/service/request/index.ts` 一列為 plan 期補）。

| 位置（檔案） | 軌道·用途 | 型別 | 改動內容 | 12m／24m | 風險 |
|---|---|---|---|---|---|
| `src/locales/langs/zh-cn.ts` | `BASE-WEB-MANAGE-PAGE-WIRING(ix)(x)`＋`BASE-WEB-I18N-WIRING(ii)` | 新增型 | `route:` 樹兩鍵、`page:` 樹兩頁之節（設定頁四組、16 鍵 label／help、矛盾提示；稽核頁四分頁、搜尋卡、快照與清理浮層、告示）、backend 子樹 `biz.audit.*` 新鍵 | **12／35** | **高** |
| `src/locales/langs/en-us.ts` | 同上 | 新增型 | 同上（英文） | **12／34** | **高** |
| `src/typings/app.d.ts` | `(ix)(x)`＋`BASE-WEB-I18N-WIRING` | 新增型 | `Schema.page` 兩頁型節、backend 型節補鍵 | **11／31** | **高** |
| `src/router/elegant/imports.ts` | `(ix)(x)`（路由外掛產物、採產物檔紀律） | 產物檔 | 路由外掛重算：兩頁 view 匯入 | 1／4 | 中 |
| `src/router/elegant/routes.ts` | 同上 | 產物檔 | 同上：兩頁路由條目 | 1／4 | 中 |
| `src/router/elegant/transform.ts` | 同上 | 產物檔 | 同上：路由名與路徑映射 | 1／5 | 中 |
| `src/typings/elegant-router.d.ts` | 同上 | 產物檔 | 同上：路由鍵型 | 1／5 | 中 |
| `src/typings/components.d.ts`（確定：稽核頁搜尋卡需 `NDatePicker`、現檔未宣告；tasks 期定） | §III 生成檔紀律（不入用途名單） | 產物檔 | 若引入新元件則工具重算（宣告行增刪） | 8／16 | **高** |
| `src/locales/langs/zh-tw.ts`（rev6 錨點檔） | `BASE-WEB-I18N-WIRING(iii)`＋各用途（rev6 自有之整檔新增型檔、不入範圍欄） | 新增型 | 兩頁 `route:`／`page:` 與 backend 新鍵之繁中（臺灣用語） | —— | 低 |
| `src/service/request/index.ts`（plan 期補） | `BASE-WEB-I18N-WIRING(i)` | 新增型 | 既有圈界塊內 `translateBackendMsg` 補第三分支（`{minDays}` 具名插值；不增塊、零修改型行） | 0／3 | 低 |

★本表最重要的一件事：i18n 兩檔與 `app.d.ts` 仍是基線最熱之檔（近 12 月 11～12 次）；緩解＝於 upstream 既有檔一律以新增型圈界承接、預期零修改型行（兩頁 view 皆新檔），不與 upstream 行交錯；若實作期出現修改型需要，須落在 Amendment 新授用途之檔集內並以 `原行:` 逐行標記。**rebase 處置**（承憲法 §III「rebase 同步紀律」）：生成檔與產物檔一律於 rebase 後以工具重算、絕不手工解衝突；新增型圈界塊隨 upstream 樹形移位時整塊搬移。
★逐處明細由實作期 fork-delta 標記落地並受 `fork-delta-lint` 機器強制（含範圍欄對賬腿）；本表為檔級風險評估與 rebase 處置索引；表外宣告之新增檔與 rev6 自有檔照既有紀律。

**刻意分岔登記（CDP 對照用：與 rev5 HEAD 行為之刻意差異，逐項指承載）**

| 面 | rev5 HEAD | rev6 本刀 | 承載 |
|---|---|---|---|
| 存取日誌分頁 | 空表（存取軌跡中介層不搬＝`rev5:R2-9`） | 每筆已登入請求一列（含授權拒絕者）、分頁有資料 | B2、FR-021～FR-025、ADR② |
| 設定變更 | 設定寫端零稽核 | 每次成功寫入落一列 `update`（`system_settings`、標的 id「-」、快照舊→新） | D1、g4、FR-027 |
| 設定頁跨鍵矛盾 | 無提示 | 三對嚴格不等式即時警示、不阻存 | D2、FR-047 |
| 密碼政策快取 | SPA 存活期間只增不清 | 設定頁寫入政策七鍵任一成功即清同分頁快取 | D3、FR-048 |
| 宣告集外設定列（seed 態無） | 依型別可編、寫入回 `2222` | 唯讀、排組尾、標示 description | 工程判斷③、FR-046 |
| 數字框界值（5 鍵） | `ip_captcha_after`／`ip_max_fails`／`ip_window_minutes`／`password_change_min_interval`／`session_idle_timeout` 無前端界：越界送出、後端拒、提示「设置值无效」並回退 | 10 鍵一律依宣告界鉗界：越界失焦即改為界值後存檔 | clarify Q1、工程判斷③、FR-046 |
| 操作日誌搜尋卡之動作提示 | 範例寫大寫（「如 UPDATE、KICK」），而過濾為大小寫敏感等值＝照提示輸入查無資料 | 範例改用庫內實際字面（如 `update`、`kick`） | 主線自校（clarify 步）、FR-051 |
| 存取日誌分頁告示 | 無（該分頁為空表） | 分頁上方一句告示：狀態欄為 HTTP 狀態碼，權限不足顯示 403、其餘請求（含業務拒絕與系統錯誤）皆顯示 200 | clarify Q2、FR-055 |
| 稽核頁清理鈕 | 頁內零按鈕級 gating | 依 `audit:purge` 碼顯隱（Super 持碼＝畫面同 rev5） | D6、FR-054、FR-039 |
| 排程清理自記列 | 無 reaper（`rev5:B-016` 不入） | 起 jobs 時操作日誌出現 `purge` 自記列（操作者「-」、來源 IP `0.0.0.0`） | B1、g2、g5、FR-036 |
| 繁中畫面 | runtime 兩語 | 兩頁全樹繁中（無 rev5 基準、驗收照 D12） | D12、FR-074 |
| 實作期新發現者 | —— | 逐項追加、CDP 開跑前凍結；CDP 中新發現者須經 user 親決（AskUserQuestion）才可入表、否則依 SC-011 判紅 | CDP 三方對照單元 |

**一次性遷移三欄表（m0004；CLAUDE.md §2）**

| Risk | Guard | Rollback |
|---|---|---|
| 角色為叢集層物件：dev 庫重跑、pristine 驗證庫與既有角色並存（R1） | 建立採已存在即略過之容錯形（`rev4:m012` 形）；Day-1 第 3 步以全新庫驗；走查前後套基準 snapshot／restore | m0004 之反向遷移（撤 GRANT、角色無依賴時刪除、刪新列、選單 77 按鈕清單回 NULL）；全新庫重放 |
| GRANT 射程過寬或過窄 | reaper 憑證之正負向測（允許語句成功、權限外語句被拒）；compose 實連三 job 一輪 | 以新 migration 補正（已套用之 m0004 不改檔） |
| 離線對賬腿遇 DDL 類語句之形制（R2） | 形制 plan 期定；一正一反＋逐判準停用變異 | 還原腿碼與演進帳登記 |
| dev 庫序號已因走查前進：新列 id 與期望不符或撞 id | 新列 id 與冪等形於 plan 期定；序號合成（007 GR9 形）＋自測 | 全新庫重放；dev 庫以走查基準還原後重跑 |
| 判定面未載入新列 | 遷移服務先於 rust-api 啟動；dev 庫手動遷移後重啟 rust-api | 重啟 rust-api |

### Key Entities *(include if feature involves data)*

- **操作日誌**（`sys_operation_log`、001 基線、append-only）：動作（封閉九詞）、標的表名、標的 id（可空：設定變更列、清理自記列、解鎖列）、變更前後快照、操作者（可空：排程清理自記列）、來源欄（真實來源位址 NOT NULL、對端、XFF、信心）、region／trace_id（恆空）。
- **存取日誌**（`sys_access_log`）：每筆已登入請求一列——操作者（NOT NULL）、HTTP 狀態碼（非業務碼；業務拒絕與系統錯誤皆 200）、方法、路徑、來源欄、region／trace_id（恆空）。
- **登入嘗試**（`sys_login_attempt`）：嘗試帳號名、成敗、操作者（可空）、來源欄；節流短路遭拒不落表。
- **會話事件**（`session_event`）：使用者、sid、事件型、原因、來源 IP（文字）、操作者。
- **清理請求與清理自記列**：{來源表（四值）, 保留天數（≥30）}→刪除筆數；自記列＝動作 `purge`、目標表名、標的 id 空、快照 {table, before_days, deleted_count}（排程清理另帶 job、操作者空、來源位址哨兵 `0.0.0.0`）；操作日誌源之清理永久豁免之。
- **系統設定**（`system_settings`、主鍵＝字串鍵）：16 鍵（密碼策略 8、工作階段 2、IP 源登入 3、帳號登入 3）；值為字串載體、型別描述（number／二值 enum）驅動控件；登記表宣告界為界值單一權威；讀端 wire 擴充宣告界與宣告旗標。
- **三對跨鍵判準**（概念）：密碼長度上下界、帳號維驗證碼門檻對鎖定門檻、來源維驗證碼門檻對鎖定門檻；嚴格不等式；前端提示、後端行為不變。
- **reaper job**（概念）：token-reap（票回收）、audit-retention（排程清理）、policy-reconcile（授權對賬）；CLI 兩參數、退出碼、心跳分組、環境變數（四表保留天數、寬限天數、每輪間隔）。
- **reaper role**：最小權限資料庫角色（m0004 建、設密腳本開登入）；權限面＝FR-039 表。
- **孤兒授權列**（概念；詞彙正名）：現役授權列中，標的不在該維候選集內者（候選外現役列；候選集依 ADR-00066 之三維定義），或角色代碼指向已軟刪或不存在之角色者；與既有詞條「撤銷殘留」區分、不稱「殘留授權」。
- **`audit:purge` 碼**：選單 77 按鈕清單之唯一碼；R_SUPER 按鈕授權列（不受保護）；顯隱清理鈕。
- **哨兵 `0.0.0.0`**（概念）：無網路來源之標記，只用於無操作者之系統程序自記列。
- **錯誤明細通道**：攜參三鍵（違規清單、剩餘秒數、清理下限天數）；其餘拒因純 key。
- **msg key 名冊**：既有 68 鍵＋本刀新增（預設兩鍵、實數於 contracts 定案）；三檔 locale 後端子樹各為該語譯文之家。
- **稽核域詞彙**：存取日誌、水平線清理、手動清理、排程清理、票回收、授權對賬、清理自記列、孤兒授權列（活書 12 隨施工落）。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 路由與授權態對賬零漂移——路由表恰 66 條（公開 11、政策保護 50、登入即可 5）、與 seed 政策列路徑×動詞逐字對齊；契約覆蓋閘無缺案無殭屍案；授權態矩陣逐端點實測（Super 對 5 支皆通；Admin 與 User 皆 `5003`；未帶權杖 `8888`）；可授出集恰 35。
- **SC-002**: 拒因碼表自證——兩支新鍵各至少一案實際發出、名冊雙向閘綠；攜參通道恰三鍵、佔位符 `{minDays}` 三語與後端明細鍵逐字相等（改名即紅）；錯誤變體恰 11、13 碼矩陣不變。
- **SC-003**: 讀端語意可驗——四源每一過濾維各至少一案（含名對應已軟刪同名全集、萬用字元字面化、成敗值域外＝未設）；來源 IP 精確等值之反例一案（子字串不得命中）；分頁夾界、固定序、時間閉開、顛倒空頁、畸形未設、空字串 query 不 4xx 各一；四支讀端零寫入（寫入計數前後相等）。
- **SC-004**: 打碼單點——兩鍵於變更前後各一案、手機 ≤5 字與無 `@` 信箱之邊界各一、非字串與巢狀不動各一；拆掉打碼呼叫必有測試轉紅；資料庫原值不變。
- **SC-005**: 清理可證——低於 30 天 100% 被拒且拒因含下限值；白名單外拒；同時違反回 `invalidTable`；成功清理之回報筆數與實刪一致；清理自記列留存率 100%（含對操作日誌之清理）；故障注入下零部分成功（紅綠證）；上下文缺席 `5000` 零變更。
- **SC-006**: 存取日誌——已登入請求每筆恰一列且路徑不含 query；`5003` 請求照記且狀態 403；業務拒絕（`2222`）之請求列狀態為 200 一案（已知態釘住）；存取分頁告示三語在場；未認證與認證失敗零列；注入寫入失敗時回應狀態與內文不變、告警與降級計數各增一；注入慢寫時回應不被延遲。
- **SC-007**: reaper——三 job 之 dry-run 零變動；audit-retention 之 execute 逐表刪除＋四列自記（哨兵 `0.0.0.0`、操作者空、刪 0 列照落）；token-reap 之 execute 實刪數與 dry-run 候刪數一致；環境變數三分語意各一案（前置全拒先於連線）；未知參數與 job 嚴拒；任一失敗非零退出且不推成功心跳；心跳推送失敗不改退出碼；HTTP 寫端於上下文缺席仍 `5000`（哨兵不外溢）。
- **SC-008**: 授權對賬——全新 seed 三維恆 0；三維各植入一形孤兒列皆被計入且告警觸發；job 前後授權域三表逐列不變。
- **SC-009**: 系統設定頁——16 鍵 100% 可視可讀；可改鍵改動後 1 次回讀內畫面與伺服器一致；非法值 100% 被拒且拒因可讀；數字框界值與登記表宣告界逐鍵相等、越界輸入鉗界存檔一案（取 rev5 無前端界之鍵）；宣告集外列唯讀（合成列一案）；三對矛盾各一案警示、相等不警示；同分頁政策快取即時；每次成功寫入恰一列 `update` 稽核、拒因零列。
- **SC-010**: m0004 與離線腿——全新庫重放後 schema 三閘綠、拆掉序號合成即紅；離線腿對 m0003／m0004 綠且一正一反與逐判準停用變異皆紅；授權列 164、受保護 25、R_SUPER 按鈕碼 22、選單 77 恰一碼；reaper role 允許語句成功、權限外語句被拒；Day-1 三步完成。
- **SC-011**: CDP 三方對照（rev5 22080 vs rev6 32080；upstream 22089 作錨點）以**結構清單逐項全等**為判準（設定頁四組與鍵序、控件型、說明提示、逐項存與回讀；稽核頁四分頁之欄集與列序、搜尋卡、快照浮層、清理浮層流程；側欄兩項；提示文案），任一項不等即紅；間距／字體／顏色只記入走查紀錄、不擋收刀；排除清單＝刻意分岔登記表各項（CDP 開跑前凍結；CDP 中新發現者須經 user 親決入表、否則判紅）＋已知態各款＋請求次數維度；22080 側步驟一律顯式設簡中。
- **SC-012**: 繁中介面兌現——zh-tw-lint 綠（簡體殘字掃描零命中、具名白名單除外；用語表綠）；型別檢查證三語鍵集相等；AI 逐頁審讀紀錄涵蓋全部接真頁面；user 抽查完成並記錄（D12）。
- **SC-013**: 前端與 fork-delta 全綠——前端型別檢查綠；修改型標記只出現於授權檔、base-web 變更檔集 ⊆ 授權檔集＋新增檔（機器斷言）；範圍欄對賬腿綠且變異自證；路由產物冪等；seed-view-gate 綠且豁免表為空；view-render-guard 綠；各新增圈界塊拔標記必紅。
- **SC-014**: 治理與觀測面——憲法 1.9.0（收刀前 PATCH 實數化範圍欄後為 1.9.x）且 accepted 前 base-web 既有檔零 diff（git 史可證）；新用途列被名冊載入器讀進（變異自證）；告警 ③d／⑤⑤b／⑥⑥b 有事件源、對賬告警存在；`rust-api.json` 恰少三面板；docsync lint 零錯誤。
- **SC-015**: 交付鏈全綠（FR-075）——後端全量測試容器內 serial 全綠、SC-013 所列前端面與其餘全部閘零紅、手動端到端走查（入口 `http://127.0.0.1:32080`）全數通過、走查後 diff rc 0；子句表檢核工具自證綠（空錨與錨不符計不符、核數＝總錨數）。
- **SC-016**（★收刀面子句於簿記 commit 後驗）: 治理帳本結清——plan 期 ADR 與收刀前 PATCH Amendment 全數 accepted 且 `feature_close.adrs` 列全；`backlog_done` 5 條與 FR-066 相符、零 `backlog_add`；收刀計數三則入 notes（FR-067）；NOTES 下一步指下一刀；活書各節現在式更新；假述零殘留——以 FR-065 所列種子實跑 `python3 tools/docsync errata <詞>`、依 RULES 名詞段分面、現在式面命中逐條判讀並記結果（不得以 lint／check 綠代證；RL-0084）。

## Assumptions

- rev5 與 rev4 為本機可達之唯讀參考庫（rev5 凍結 SHA 由 bootstrap 斷言；rev4 樹同為唯讀）；應用碼全程重打字消化、註解 rev6 語境重寫、前代出處帶 `rev5:`／`rev4:`；藍本：讀端、清理與兩頁取 rev5 HEAD 形，reaper 取 rev4 形；翻案不帶回四項（rev4 HLL 廣度估計、rev4 設定 TTL 快取觀測、`[rev5-inline]` 標記字面、前代 API 命名空間）入 plan research 差異點表、烤入 implementer 防回歸清單；plan research MUST 列「rev5 對應碼清單＋rev6 拍板差異點」（承 `rev5:ADR 0019`），本刀另列 rev4 reaper 對應碼。
- 001～007 刀底座已兌現且本刀純消費：四張稽核表在 001 基線（除 m0004 之角色與權限面外零 DDL）；操作稽核寫入面（004 起）、信任錨與請求上下文、錯誤明細通道（007）、判定面同步、設定寫端（002）、密碼政策 hook（007）、測試基建與名冊閘。
- compose 已有 jobs profile 之 reaper 服務、metrics profile 之 pushgateway，密鑰產生器已產 `reaper_password`／`reaper_database_url`＝本刀補 bin、role 與現況註。
- 風險 R1～R13 照 brainstorm §3 §4、plan 期逐條承接對策；其中存取日誌每請求一寫之負載與測試面影響（R3）、哨兵語意邊界（R13）已入本 spec 之 Edge Cases 與 FR。
- **clarify 步（2026-10-21）兩題**：數字框 10 鍵一律鉗界；存取日誌照 rev4 欄形（只記 HTTP 狀態碼）＋存取分頁加一句告示（緣起＝user 轉來之 side agent 提醒）——兩題皆 user 選建議項（見 Clarifications）。specify 期所列 clarify 候選四題之處置：對賬 metric 與告警＝命名與觀測出口之 HOW、主線工程判斷定案（每維一條 gauge；任一維大於 0 告警＋對賬心跳逾時告警、門檻沿 172800 互錨；名稱留 contracts；FR-035、FR-037、FR-043）；m0004 一支（依 D6「併入 m0004」之 user 拍板紀錄；FR-039）；同值設定寫入照寫照落（D1 字面＋ADR-00091；畫面不可達；FR-028）；pushgateway 推送之 HTTP 實作甲乙＝plan research 比較（一次性 CLI 之推送形與全程時限、依賴樹增量；若引入新依賴，版本依全域 §6 兩源比對、分歧即問 user）。另以 rev5／rev4 原碼補明與更正七處：清理浮層形（FR-054）、動作過濾大小寫敏感與搜尋卡提示照實字面（FR-008、FR-051、分岔表）、token-reap 不落自記（FR-032）、極大天數不崩潰（Edge Cases）、授權拒絕之存取日誌列狀態 403（US4）、遷移身分須具建立角色之權（Edge Cases）、brainstorm 工程判斷③「畫面同 rev5」只對 5 鍵成立（Q1）。
- **前端零測試框架**：前端執行單元之 TDD 迴圈退化為型別檢查＋機器斷言＋兩段 review＋CDP 對照走查。
- **Amendment 與 ADR 親決時點**：plan 期全數產草稿；Amendment 條文於 plan 期逐款親決（user 2026-10-21 裁定；U0 照定稿落字、銜接字面一份 diff）；施工前提 ADR 另顆。
- **TDD 發射前置**：組裝形 workflow 模型家由 ADR-00056 固定（opus[1m]／xhigh）；CDP 操作一律 opus[1m]／xhigh；base-web pnpm 與其逾時一律放容器內。
- **走查與 CDP 基準本機自取**：首次真登入走查前 snapshot（RUNBOOK §9c）；007 刀終態基準於本刀自取基準後才可清；rev6 stack 走查前實看容器態、必要時重建；走查期間不起 jobs profile。
- **實作紀律引用**（非本 spec 新拍板）：rust build／test 容器內全程 serial；每單元 pin bump；review 只讀不寫；rev5／rev4 樹唯讀令烤入 agent prompt；dev 庫寫入逐步取 user 放行（LL-00053）。
- **stakeholder 判定承 001～007 刀前例**：本刀 stakeholder＝admin 後台之超級管理員、被委派之管理員、維運者與 workspace 維護者；spec 中的端點路徑／碼／seed 列號／環境變數名／軌道名／閘與工具名／常數係交付物座標（WHAT）與治理設施引用，非實作技術選型（HOW）。

### Out of Scope

- **授權歸檔表之保留期與清理**——不設（B3；ADR⑦ by-design：歸檔列除經復原外永久保留）；手動清理白名單與 reaper 只含四張稽核表。
- **孤兒授權列之自動清理與畫面清理路**——不做（B4 只報不刪；ADR-00066 後果；處置＝RUNBOOK，g3）。
- **設定頁授權下放**——不做（工程判斷④；ADR-00064 封死集不動、零 seed 變更）。
- **稽核清單排序參數**——不做（ADR-00058）；**匯出、快照內容搜尋、前端排序**——不做（rev5 同）。
- **存取日誌之來源 IP 過濾欄**——不做（rev5 形：只登入嘗試有來源 IP 過濾）。
- **reaper 保留天數之畫面設定**——不做（D8：環境變數；設定頁維持 16 鍵）。
- **trace_id 與 region 料源**——不做（恆空已知態；儀表板描述改述）；**ipConfidence 欄渲染**——不做（工程判斷②）。
- **首登強制改密**——BL-00140（滯後卷；本 spec 只留此指針）。
- **郵件與個資自助**——BL-00141（滯後卷；設定頁零郵件鍵、打碼是遮罩而非個資自助）。
- **登入節流判定次序與連線池設定**——不動（BL-00145／BL-00147）。
- **快速登入鈕拆除**——不做（BL-00049 滯後卷）；**alova 與 demo 面**——不碰（BL-00064／BL-00067）。
- **AI 元件**——零（BL-00002 反向確認）；**rust 側字元級解析組**——不新寫（BL-00108 反向確認）。
- **schema-definition 前進、新表與業務表 DDL**——不做（ADR-00087；本刀唯一 DDL 為 m0004 之角色與權限面）。
- **RULES 改動**：預期零 RULES 表列改動（RULES-VERSION 不變）；若實作期需要，依輕量紀律另行拍板；晉升 fix／review 範圍之 RL 依 RL-0052 一進一出。
