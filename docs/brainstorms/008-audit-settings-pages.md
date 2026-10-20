# 008-audit-settings-pages — 系統設定頁與稽核頁進場（兩頁＋稽核五端點＋存取日誌寫入＋reaper 三 job＋島 J 入憲＋BACKLOG 五條收單）brainstorm

> 路徑＝architectural（superpowers:brainstorming；產出路徑依 CLAUDE.md §2 覆蓋為本檔）；終點＝user 確認（設計四節核可、grilling 輪後）再顯式 `/speckit-specify`（本專案不叫 writing-plans）。
> 取證＝主線唯讀親核（無 workflow）：rev5 藍本（`rev5:008` brainstorm／spec、`rev5:base-web` 稽核頁與清理浮層、`rev5:rust-api` 讀端打碼）、rev4 藍本（`rev4:server/src/bin/reaper.rs` 659 行、`rev4:m012` reaper role）、rev6 現況（BACKLOG 七條條文、ADR-00038／00047／00054／00057／00064／00065／00066／00076／00079／00081／00082／00084／00097、憲法 §I.1／§I.7／§III.2、compose jobs 段、密鑰產生器、router、m0002／m0003 seed）；承 008 前 BACKLOG 體檢最新一版（主線工作區、gitignored）之 O／X 義務枚舉為底稿。
> 輸入＝`docs/ops/NOTES.md`「下一步」008 條＋上述體檢之題單；user 2026-10-20 開工令附帶「把可在 008 處理的 BACKLOG 也評估進來」。

## 0. 拍板紀錄（全數 user 拍板 2026-10-20；一題一問、首選項皆為建議，非建議項另標）

| 題 | 拍定 | 要點 |
|---|---|---|
| 理解校正 | 正確、開始逐題問 | 目標＝系統設定頁（照 rev5 單檔、資料驅動、四組、逐項即改即存）與稽核頁（四源四分頁＋手動清理）進場，後端新增稽核五支端點（seed 已預埋、零新政策列），三語同批，側欄兩死項解除；藍本＝`rev5:008`（再承 rev4），UI 以 rev5 22080 為基準、分岔逐項登記；觸發落 008 之三條逐條成題、其餘逐條評估順手收；零 migration 為目標、長出 migration 之選項先講代價；島 J 入憲逐條親決；成功準則＝本檔定稿 commit 後等 user 令再 specify |
| B1 排程清理（BL-00043 後半） | **入，兩個 job 一起做** | audit-retention（四表保留天數）＋token-reap（過期票）照 rev4 藍本重打；最小權限 reaper role＝新 migration m0004（BL-00148 於該單元前到期）；`reaper_*` metric 發射點＝BL-00139 同批到期；心跳推 pushgateway 需 HTTP client（plan 期依全域 §6 定版本）；v11 體檢原建議「不入」之前提（008 照 rev5 射程）因開工令附帶之評估要求而改建議 |
| B2 存取日誌寫入（BL-00043 前半） | **做，加寫入中介層** | 照 rev4 形重打：只記已登入請求、寫入失敗不擋請求（fail-open＋結構化告警）、告警 ③d 依實作重錨；立 ADR 解除 004 刀 research 防回歸清單 B 之 `rev5:R2-9`（其 rev5 原因＝「歸 `rev5:B-016` 稽核域射程」、非否決判斷）；走查還原與 schema 閘之 runtime-append 常數擴入 `sys_access_log`；存取分頁有資料＝對 rev5（空表）刻意分岔；BL-00043 收刀整條刪 |
| B3 歸檔表保留期（BL-00133 前半） | **永久保留，立 by-design ADR** | 歸檔列除經復原外永久保留、零碼改、回收桶行為不變；手動清理白名單與 reaper 照 rev5 只含四張稽核表 |
| B4 授權殘留對賬（BL-00133 後半） | **做，reaper 第三個 job、只報不刪** | 唯讀逐維（選單、按鈕、端點）查殘留列與候選外現役列，結構化日誌＋心跳 metric、非零即告警；不自動刪；reaper role 多授唯讀（同 m0004）；BL-00133 收刀整條刪；風險例已核（`sys_menu` 路由名唯一索引只管活性列＝軟刪選單之路由名可被新選單重用、殘留列即生效） |
| B5 三空面板（BL-00139） | **刪掉、重排版位** | `rust-api.json` 之 HLL 兩面板與「設定讀取頻次」一面板刪除；reaper 四面板描述改 rev6 as-built、`audit-log.json` trace_id 下鑽面板與變數描述改述「rev6 稽核列此欄恆空」（照實改、不另問）；觸發因 B1／B2 成立、本刀收 |
| D1 設定寫端稽核（ADR-00082 款 3 觸發器） | **改落稽核** | updateSystemSetting 同交易落一列操作日誌（沿用動作詞 `update`、標的＝設定鍵、快照舊值→新值）；續行 ADR-00082 改寫款 3 寫入者全集；後端「設定寫入零稽核」測試反轉；ADR-00047 觸發器重評設定域空字串語意（預期維持）；資料面對 rev5 刻意分岔 |
| D2 三對跨鍵矛盾（ADR-00079 觸發器） | **存檔後即時提示、不擋** | 前端比兩現值、成對矛盾即該組卡片警示（密碼長度上下界、帳號維與來源維之驗證碼門檻對鎖定門檻），不阻存、後端照舊逐鍵驗；維持 ADR-00079 決定 2；rev5 無此提示＝刻意分岔；三語 |
| D3 密碼政策快取（BL-00045 評估點） | **設定頁改政策成功即清同分頁快取** | hook 增清除函式、設定頁寫入政策七鍵任一成功即呼叫；其他分頁仍須重新整理；RUNBOOK §11.3 與兩處檔頭已知態句同批改述；對 rev5（不作廢）刻意分岔 |
| D4 篩選時區 | **照 rev5：本地輸入、UTC 顯示** | 控件依瀏覽器本地選值、轉 UTC 上 wire、後端 [起, 迄)；spec 明文「輸入為瀏覽器本地時間、顯示為 UTC」；零分岔 |
| D5 稽核五支授出 | **照 rev5：五支都可授出** | 零 seed 變更；可授出集 30→35；ADR-00081 款 9 改述、ADR-00066 射程款同顆複核；30 天下限與清理自記兜底 |
| D6 按鈕碼 | **清理鈕加碼、設定頁不設** | 新碼 `audit:purge`（選單 77 buttons 增碼＋R_SUPER 按鈕授權列、不受保護、比照 `ipRule:unlock`）併入 m0004；設定頁讀寫端點屬封死集、加碼無意義；§III.2 稽核頁用途寫明 |
| D7 清理拒因第三攜參鍵（ADR-00076 觸發器） | **照 rev5：拒因攜 `{minDays}`** | `biz.audit.purgeBelowFloor` 攜 `{minDays}`、三語譯文只放佔位符；新 ADR 整顆 supersede ADR-00076（標題「射程恰兩鍵」被推翻）並加一款釐清 ADR-00076／ADR-00090 決定 1「照提示秒數重試必過」於牆鐘回撥不成立；msg-key-gate 名單同擴 |
| D8 reaper 保留天數設定面 | **照 rev4：環境變數** | 四表各一保留天數（缺席 90、畸形告警退 90、低於 30 前置全拒）＋票寬限（7）＋每輪間隔（dev 每日一輪）；零 seed、設定頁維持 16 鍵；RUNBOOK 寫明 |
| D9 個資打碼 | **照 rev5：後端讀出時單點打碼** | 讀端序列化一處、鍵常數 `userPhone`／`userEmail`、深度一層；手機長於 5 字＝前 3＋`****`＋後 2、否則全遮；信箱＝首字＋`***`＋`@網域`；資料庫原值不動；J4 依此 |
| D10 島 J 入憲 | **全島 J1～J5 入憲** | §V.2 Amendment（MINOR）：J1／J3／J4 以 `rev5:ADR 0077` 島 J 字面為底改座標；J2 隨 B2 回填（存取日誌寫入失敗不擋請求、只告警）；J3 射程含 reaper audit-retention；J5 一句指針指島 E 末兩點（ADR-00042）；同顆 §I.6 變體 B 括號句改 J3 交叉指針、MAJOR 射程「九島」改十島；活書 06／10 補島 J 情境；條文落字 U0 逐款親決 |
| D11 需求追溯形（ADR-00097 決定 3） | **沿用，射程全四類** | 驗收場景、SC、FR、Edge Cases 全拆子句掛錨；決定 2b 自證義務生效；檢核工具以 007 前例改寫（主線工作區）；tasks 收刀清單加「收單時重審工具入庫與通則化」（ADR-00097 翻案觸發器首條） |
| D12 繁中驗收形（ADR-00084 決定 8） | **照決定 8 字面，每刀重審全部頁面**（非建議項） | 繁中驗收＝zh-tw-lint 綠＋前端型別檢查綠＋AI 逐頁審讀紀錄涵蓋**全部接真頁面**（含 007 已審各頁與本刀兩新頁、浮層、提示）＋user 抽查並記錄；零 ADR；spec 一條 SC、tasks 收刀清單審讀與抽查各一條 |

> 本檔題號：B＝BACKLOG 題（提問時記「BACKLOG 第 n 題」）、D＝設計題（提問時記「設計第 n 題」）；O／X 號＝008 前 BACKLOG 體檢之義務與既存點編號（主線工作區），本檔引用時連同其內容一併寫出、不依賴該檔。

**grilling 輪必提（user 2026-10-20 指定）**：①008 規模總帳（§4）——B1～B5 全取建議後，比照 rev5 規模約增 7～10 個執行單元，長期改動＝m0004（CREATE ROLE＋GRANT＋seed）、一個新的 HTTP client 依賴、解除防回歸清單一筆；主線原建議（v11 體檢）為「不做、照 rev5」，改建議之前提＝把「評估進來」讀成「能收就收」。換得 008 窗淨流量自約 −2 降至約 −6。

**主線工程判斷**（CLAUDE.md §5 自拍、回報備查）：
①XFF 欄照 rev5 於操作／存取／登入三分頁以純文字渲染（ellipsis＋tooltip）＝與 rev5 零分岔（rev5 之「UI 對照唯一例外」是 rev5 對 rev4 的身分、不帶進 rev6 分岔表）；轉義由 view-render-guard 常駐守（稽核頁新目錄自動入掃）；入庫值＝轉發鏈判定窗轉錄、1024 字元兜底（超長留最右端）、零 CR／LF、不剝 HTML。
②來源欄欄集逐分頁照 rev5（`rev5:008` FR-B07）：traceId 三分頁渲染、值恆「-」登已知態；region 存取／登入兩分頁渲染（恆「-」）、操作分頁不渲染；peerIp、ipConfidence 不渲染；讀端照原字面回、容忍 003 期 `nginx_peer` 舊列；日後若渲染 ipConfidence，`chain_rejected` 須分表判讀（`sys_login_attempt` 上恆為被拒列、`sys_operation_log` 上是標記但照常服務）。
③設定頁數字欄界值由讀端 wire 下發 REGISTRY 宣告界（單一權威不破、輸入框照 `rev5:008` FR-D04 以 min／max 鉗界、畫面同 rev5）＝不另立界值真源、ADR-00054 翻案觸發器不成立；同一 wire 擴充下發「是否在 registry 宣告集內」，宣告集外之列唯讀顯示、排組尾、標示後端 description（ADR-00057；不在前端抄鍵集）；wire-schema 快照同步。
④設定頁授權不下放（ADR-00064 封死集不動、零 seed 變更）；選單維可見性依 ADR-00081 款 10＝看得到、讀寫 5003。
⑤四源清單固定序 `created_at` 降冪、`id` 降冪決勝、不收排序參數；Out of Scope 一行指 ADR-00058。
⑥清理守門固定序照 rev5：表名白名單（四值）→天數 ≥ `PURGE_MIN_DAYS`（30）→單交易水平線 DELETE（操作日誌源固定豁免清理自記列）＋同交易自記（含來源表、天數、刪除筆數；刪 0 列照落）；自記失敗整筆回滾，以 fault-injection 級測試證「回報刪 N 筆、實際零刪除」不可達（`rev5:B-125` 形；必要時 test_kit 增注入 db 之薄殼）；realIp 搜尋＝精確等值比對（`rev5:B-078`）入 spec 驗收句。
⑦清理浮層之天數輸入框下界照 rev5 抄為 UX 護欄、碼註寫明權威在後端 `PURGE_MIN_DAYS`；reaper audit-retention 之下限直接引用同一常數（同 crate、不再如 rev4 鏡像）。
⑧存取日誌中介層只記已登入請求、位於授權判定之後（被拒請求亦入列，rev4 形）、寫入失敗只結構化告警＋降級 metric（供 ③d 重錨）；不動連線池設定（免觸 BL-00147「改動連線池設定」臂）、不入登入路徑（免觸 BL-00145「改動判定次序」臂）；region／trace_id 無料源＝NULL。
⑨reaper 照 rev4 CLI 形：`--execute`（缺席＝dry-run）、`--job <name>`（token-reap 預設｜audit-retention｜policy-reconcile）、未知參數嚴拒、退出碼 0＝完跑（含 0 列）、失敗不推成功心跳、心跳推送 best-effort 附全程時限；audit-retention 逐表單交易「水平線刪除＋自記」、與手動清理共用同一謂詞與自記形（J3）；policy-reconcile 只讀、只報計數。
⑩pushgateway 推送之 HTTP 實作於 plan 期比較：甲＝`metrics-exporter-prometheus`（現有依賴）之內建推送功能（不新增 crate、但開 feature 會帶入其 HTTP 依賴）、乙＝rev4 藍本之 ureq（rev4 用 3.3.0）；任一新依賴之版本依全域 §6 以「參照專案 lockfile 值」與「官方最新穩定版」兩源比對、分歧則問 user。
⑪m0004 內容＝reaper role（NOLOGIN、零密碼；GRANT schema USAGE、`sys_token` SELECT／DELETE、四稽核表 SELECT／DELETE、操作日誌 INSERT 與所需序號權、授權域三表唯讀）＋選單 77 buttons 增 `audit:purge`＋R_SUPER `audit:purge` 按鈕授權列；拆不拆兩支（role 與 seed）於 plan 期定；設密仍由既有 `deploy/setup-reaper-role.py`；migrate 以 compose `database_url` 身分執行（postgres 容器 bootstrap 使用者、具 CREATEROLE）；新 casbin 列 id 與序號合成照 007 GR9 形。
⑫BL-00148 之零 docker 離線對賬腿於 m0004 單元之前落地，樣本＝m0003（seed-only）與 m0004（role DDL＋seed）兩支；DDL 類語句之處理（略過或結構化登記）於 plan 期定。
⑬設定寫端落稽核（D1）之同單元順改 rust-api 系統設定兩檔碼註前代歸因：「rev5 後刀的同 txn op-log 不帶回」實為 rev4 物件（改述為 rev4 之同 txn 審計不帶回）、裸引之 research 條號補 `rev5:` 前綴；連 assert 訊息一併改時以容器 cargo 驗。
⑭ADR-00047 觸發器（D1 使設定寫端被重寫）重評結論預期＝維持（設定值逐鍵驗型與界、空字串於 number 型＝不合法、於 enum 型＝不合法，不新增「清空」語意）；結論寫入 D1 之續行 ADR。
⑮走查還原與 schema 閘：`tools/walkthrough-baseline.py` 與 `tools/schema-gate.py` 之 `RUNTIME_APPEND_TABLES`（同值互釘）擴入 `sys_access_log`、`RESTORE_TABLES` 同評估，配自測；RUNBOOK §9c／§12 與 schema-gates 收窄射程字面同批。
⑯RUNBOOK §11 補 audit-capacity 告警（rules.yml ④）之處置子節（判讀＋經稽核頁清理或待 reaper 下一輪），比照 §11.3 形；§3／§8 jobs 與 reaper role 段改為現況。
⑰節流文案（BL-00145 滯後條文）：設定頁帳號登入／來源登入兩組說明與稽核頁登入嘗試分頁告示不承諾嚴格上限（示例「窗內失敗達此數即鎖定（並發首波不嚴格）」或不寫上界）；凍結 seed description 不可改＝三語全映射、不以 description 退底；告示語意可沿 rev5「節流短路遭拒不落表」。
⑱BL-00108 反向確認（本刀不新寫 rust 側字元級解析 lint）照 007 spec 形寫一行；探針取兩側函式名聯集（同職異名三對 `close_of`↔`match_delim`、`split_top`↔`split_entries`、`attr_spans`↔`attr_group`，wire 側另有 `token_at`），計數口徑明寫其一（`&[char]` 之 fn 簽名行：common 6／entity 18／wire 21；或 `&\[char\]|Vec<char>` 之行數：common 7／entity 28／wire 25，此式另中非解析器之 `captcha/mod.rs`、`test_kit.rs` 各 1 行，須限 `server/tests`）；byte 級 `authz_entrypoint_lint.rs` 之 `prev_nonws`／`next_nonws`／`matching_close` 不計（`&[u8]`、函式名零重疊）。
⑲X31（RL-0080 括注接線後之正則閘）：D7 擴 msg-key-gate 之名單常數（`BIZ_DATA_KEYS`／`DETAIL_HOME`），是否構成 RL-0080「增判準」於 plan 期依其字面判；本刀若改動既有 python 閘之正則判準（msg-key-gate 模組層 `RE_*` 20 支、zh-tw-lint、fork-delta-lint 等），該單元先以 `python3 tools/regex-mutants.py run` 取全成分清單、存活者逐支補殺案或附等價證明（既有存活數 zh-tw-lint 30／46、fork-delta-lint 9／13 於 maint-pre008-carriers 實測、repo 未記），並預估代價（LL-00097：同類補案 18 支、約 5.2 小時）。
⑳收刀計數三則：ADR-00011 翻案觸發器①（RULES fix 20／19 超限後第 1 刀）、ADR-00084「zh-cn.ts 新字未分類之紅」（007 ≥1、本刀＝第 2 刀）、ADR-00052「一致性腿誤擋正常部分 commit」——各單元 commit 訊息記次數、收刀 feature_close notes 同句彙記（含 0）；本刀晉升 fix／review 範圍之 RL 依 RL-0052 一進一出。
㉑CDP 走查以 Super 與 Admin 切換、沿用三顆快速登入鈕（BL-00049 條件依賴；期望＝Super 側欄有兩項且進得去、Admin／User 看不到，seed 選單維政策列 69／142 只授 R_SUPER）；32080 登入頁預填之 `Soybean` 非 rev6 seed 帳號、送出會留失敗紀錄並觸發節流＝一律按快速登入鈕；真登入照 RUNBOOK §9c；對照兩側先設簡中（ADR-00084 決定 8）。

## 1. rev5 承襲盤點（沿用項照已驗證結論施工、翻案項用新設計；CLAUDE.md §2）

| rev5 項目（`rev5:008` brainstorm／spec） | 處置 | rev6 落點 |
|---|---|---|
| 五支端點 path×method＝凍結 seed（列 139／140／141／158／159：四支 GET 讀端＋`purgeAuditLog` POST；全 R_SUPER、protected FALSE）、零新政策列 | 沿用；ROUTES 61→66；可授出集 30→35（D5） | router／handler |
| 四源四分頁（操作／存取／登入嘗試／會話事件） | 沿用 | 稽核頁 |
| 搜尋卡同構（預設展開、重設清空並觸發搜尋、時間區間 UTC ISO 上 wire、`timeFrom`／`timeTo`、後端 [from, to)、畸形＝未設、顛倒＝空頁） | 沿用（D4） | 前端 composable＋handler |
| 分頁 current ≥ 1、size 夾於 [1, 100]；query 參數全取可缺字串；操作者名第二發批查補齊 | 沿用 | handler |
| 後端固定序、前端零排序、零匯出 | 沿用（工程判斷⑤） | handler |
| 操作日誌快照以浮層純文字 JSON 呈現 | 沿用；讀端單點打碼（D9） | 讀端＋前端 |
| 清理守門固定序＋同交易自記＋操作日誌源豁免自記列＋原子性 fault-injection 測（`rev5:B-125`） | 沿用（工程判斷⑥）；射程擴 reaper audit-retention（B1、D10 之 J3） | handler／facade／reaper |
| `PURGE_MIN_DAYS`＝30 碼內常數；前端浮層輸入框下界抄一份 | 沿用（工程判斷⑦）；reaper 下限直接引用同一常數 | handler／reaper／前端 |
| XFF 三分頁渲染（`rev5:ADR 0076`） | 沿用、零分岔（工程判斷①） | 稽核頁 |
| traceId 恆「-」、region 存取／登入兩分頁渲染（FR-B07） | 沿用（工程判斷②） | 稽核頁 |
| 存取分頁讀空表＝已知態（拍板①：存取軌跡中介層不入） | **翻**（B2）：寫入中介層入刀；存取分頁有資料＝刻意分岔 | middleware |
| 個資打碼（`rev5:` 讀端 `mask_pii_payload`、島 J4） | 沿用（D9） | 讀端 |
| 第三攜參鍵 `purgeBelowFloor{minDays}`（`rev5:B-139`、擴跨端閘一腿） | 沿用（D7）；rev6 以新 ADR supersede ADR-00076、msg-key-gate 名單擴（佔位符對賬已在 ADR-00076 決定 7 射程） | error／跨端閘 |
| `rev5:B-078` 確認句（讀端零複驗入口、realIp 精確等值） | 沿用（工程判斷⑥） | spec 驗收句 |
| wire 命名空間 `Api.Audit` 獨立 | 沿用 | base-web typings／service |
| i18n 兩語 | **翻**：三語同批（ADR-00084 決定 11）；繁中驗收依 D12 | locales |
| 設定頁單檔、資料驅動、四組固定序（FR-D02）、逐項即改即存且成敗皆回讀（FR-D03）、label＋help 齊備與未映射退 description（FR-D04） | 沿用 | 設定頁 |
| 數字欄顯示界照 rev4（FR-D04；rev5 前端手抄 `numberRanges`＝`rev5:B-160`） | 改形（工程判斷③）：界值由讀端 wire 下發、畫面同 rev5 | 讀端 wire＋設定頁 |
| 設定後端零改動 | **翻**（D1 設定寫端落稽核；工程判斷③ 讀端 wire 擴充） | system_settings handler／facade |
| 兩頁零按鈕級 gating（FR-D05） | 設定頁沿用；稽核頁**翻**（D6 `audit:purge`） | m0004＋稽核頁 |
| 島 J 入憲（`rev5:` 憲法 1.10.0：J1／J3／J4／J5、J2 空缺） | 沿用並擴（D10）：J2 回填、J3 含 reaper、J5 寫指針 | 憲法 |
| §III.2 兩頁進場用途（rev5 號 (vii)(viii)） | 沿用形、rev6 號 (ix)(x)（rev6 (vii)(viii) 已被 007 佔用） | 憲法 |
| seed-view-gate 豁免兩列同刀摘 | 沿用 | `tools/seed-view-gate.py` |
| reaper 自動面（`rev5:B-016`：不入） | **翻**（B1、B4）：rev4 藍本重打三 job | `server/src/bin/` |
| 歸檔表 retention（`rev5:B-016`：不入） | 改形（B3）：by-design ADR 永久保留 | ADR |
| ★翻案不帶回（RL-0065） | ①rev4 HLL 廣度估計（三空面板刪、B5）②rev4 設定 TTL 快取觀測 ③`[rev5-inline]` token（rev6 用 `rev6-inline`）④前代命名空間（rev6 前綴 `rev6-`） | 全刀 |
| rev5 無藍本或 rev5 未解之 rev6 新題 | 密碼政策快取（D3）、三對跨鍵矛盾提示（D2）、設定寫端稽核（D1）、授權殘留對賬 job（B4）、歸檔表永久保留（B3）、子句表沿用（D11）、繁中全頁審讀（D12）、宣告集外列判別機制（工程判斷③）、正則閘存活者（工程判斷⑲） | 各節 |

## 2. BACKLOG 觸發項處置（7 開放＋7 滯後逐條對觸發欄；以 BACKLOG 現文為準）

| 分類 | 條目 | 008 的哪一步 |
|---|---|---|
| 收・本刀刪列 | BL-00045（兩頁本體＋快取評估點＝D3；EXEMPT 摘列早於或同顆於刪列）｜BL-00043（B1＋B2：存取日誌寫入、reaper 兩 job、五條無事件源告警重錨）｜BL-00133（B3 永久保留＋B4 對賬 job）｜BL-00139（B5；觸發因 B1／B2 之觀測層改動成立）｜BL-00148（m0004 單元前置之零 docker 離線對賬腿；觸發＝下一支 delta migration 進場之單元起手前） | 各單元／收刀 |
| 收窄・留列 | （無） | — |
| 反向確認 | BL-00108（本刀不於 rust 側新寫字元級解析 lint；口徑見工程判斷⑱）｜BL-00002（零 AI 元件、不動 §9「目前無」句） | 收刀前體檢 |
| 滯後卷（皆不觸發、只記約束） | BL-00049（CDP 沿用快速登入鈕、刀期不拆）｜BL-00064／BL-00067（不碰 alova 與 demo 面）｜BL-00140（spec Out of Scope 一句指針）｜BL-00141（近距離不納：設定頁零郵件鍵、打碼是遮罩非個資自助）｜BL-00145（文案不承諾嚴格上限；不改登入判定次序）｜BL-00147（不動連線池設定、雜湊位次） | spec Out of Scope／約束 |
| 本檔同批新記 | （無） | — |

淨效果（008 窗；未計本刀內新記）：開放窗既有 −1＋本刀刪 5＝約 −6。

## 3. 設計（四節、待 user 核可）

### §1 方案、範圍、修憲、ADR

- **方案 A**（005～007 同形）：U0 修憲與施工前提 ADR → 骨架與授權態 → BL-00148 前置 → m0004 → 後端讀端 → 清理 → 存取日誌寫入 → 設定寫端稽核與讀端擴充 → reaper 三 job → 觀測層 → 前端兩頁 → 工具 → 文件 → CDP 與繁中審讀 → 收刀前體檢。B 按 US 垂直切片（四源讀端與打碼共用底座須先完整）、C 前端先行（讀端 wire 未定、CDP 最晚）皆棄。
- **範圍**：稽核五支端點（getOperationLog／getAccessLog／getLoginAttempt／getSessionEvent／purgeAuditLog）；讀端個資打碼單點（D9）；清理（D7 拒因攜參）；存取日誌寫入中介層（B2）；設定寫端落操作稽核（D1）與設定讀端 wire 擴充（界值、宣告旗標）；reaper bin 三 job（token-reap、audit-retention、policy-reconcile；B1、B4、D8）；m0004（reaper role＋`audit:purge` 碼與 R_SUPER 授權列）；BL-00148 離線對賬腿；觀測層（③d／⑤⑤b／⑥⑥b 重錨、對賬告警、B5 儀表板）；系統設定頁（四組、逐項存、界值鉗、集外唯讀、跨鍵提示 D2、快取清除 D3）；稽核頁（四分頁、搜尋卡、XFF、快照打碼、清理浮層、`audit:purge` 顯隱）；三語同批；seed-view-gate 摘兩列。
- **Out of Scope（逐條指承載）**：歸檔表保留期→不設（B3 by-design ADR）；授權殘留之自動清理→不做（B4 只報不刪，清理經既有撤銷或回收桶）；設定頁授權下放→不做（工程判斷④）；稽核清單排序參數→不做（ADR-00058）；匯出、快照內容搜尋、前端排序→不做（rev5 同）；reaper 保留天數之畫面設定→不做（D8 環境變數）；trace_id／region 料源→不做（恆空已知態、BL-00139 描述改述）；首登強制改密→BL-00140（滯後卷）；郵件與個資自助→BL-00141（滯後卷）；登入節流判定次序與連線池設定→不動（BL-00145／BL-00147）；ipConfidence 欄渲染→不做（工程判斷②）。
- **憲法 Amendment（MINOR 1.8.1→1.9.0、一筆；條文字面於 U0 由 user 逐款親決）**：①島 J 入憲（J1～J5；D10）②§I.6 變體 B 括號句改島 J3 交叉指針、§I.7 表尾句之 J2 空缺位處置、MAJOR 射程句「九島」改十島、承襲指針 J 列補 rev6 入憲載體③§III.2 `BASE-WEB-MANAGE-PAGE-WIRING` 新用途 (ix) 系統設定頁進場、(x) 稽核頁進場（形照 (i)／(iv)：範圍欄只列 upstream 既有檔——`{en-us,zh-cn}.ts` 之 `route:`／`page:` 新增型塊、`app.d.ts` 型節、路由產物四檔；`zh-tw.ts` 為 rev6 自有之整檔新增型檔、不入範圍欄，三語由行為欄「三語鍵集 MUST 相等」與型別守承擔；(x) 寫明 `audit:purge` 顯隱）④README 憲法版本鏡像。範圍欄預估、收刀前 PATCH 實數化（ADR-00051 前例）。
- **ADR 待立（feature branch 內、plan 期起草、親決依 ADR-00089 分類；proposed 期不宣告 supersedes、accepted 同顆補）**：①島 J 入憲與 §III.2 (ix)(x)（Amendment；provenance `rev5:ADR 0077`；J2 回填理據、J3 涵蓋 reaper、J5 指針）②存取日誌寫入（解除防回歸清單 B 之 `rev5:R2-9`；射程＝已登入請求；fail-open 方向；③d 重錨；runtime-append 常數擴列；不動池設定）③reaper 三 job 與最小權限 role（B1、B4、D8；m0004；與清理同形；心跳與告警重錨；HTTP 依賴取捨與版本）④錯誤明細通道三鍵（supersede ADR-00076；D7；ADR-00076／ADR-00090 決定 1「必過」窄句釐清款；msg-key-gate 擴）⑤ADR-00081 續行（角色與選單已知態 v4：款 2／款 6 解除；款 9 可授出集 30→35；款 10 改述＝設定頁「看得到、讀寫 5003」與稽核頁「`audit:purge` 碼顯隱」之可見效果；稽核選單維〔列 142、protected FALSE〕之非超管頁內形另立一款；ADR-00066 射程款複核結論；活書 11「十八款」→十六款）⑥ADR-00082 續行（IP 域已知態：款 3 寫入者全集＝既有＋設定寫端〔D1〕＋清理自記＋reaper audit-retention 自記；動作詞彙八→九〔`purge`〕；`AuditOperation` 釘值測同改）⑦授權歸檔表永久保留（B3 by-design；ADR-00065 代價句之承接）⑧設定頁進場複核（ADR-00079 觸發器＝前端即時提示不擋〔D2〕、ADR-00054 觸發器不成立〔工程判斷③〕、ADR-00057 宣告集外列呈現與判別、ADR-00047 觸發器重評結論〔工程判斷⑭〕、ADR-00064 不下放、密碼政策快取清除〔D3〕之刻意分岔）⑨m0004 seed 與 role（演進帳登記、序號合成、Day-1 登記三步；ADR-00008 delta 第二支）⑩刻意分岔登記（存取分頁有資料、設定變更入操作日誌、跨鍵提示、快取清除、`audit:purge` 碼；可併入 spec 分岔表、是否另立 ADR 於 plan 期定）。

### §2 後端

- **讀端四支**：只讀交易、逐欄構造回應（不序列化原始列）；時間過濾 RFC3339 閉開、畸形＝未設、顛倒＝空頁；分頁夾界；操作者名第二發批查；固定序（工程判斷⑤）；操作日誌快照於序列化單點打碼（D9，鍵常數、深度一層、before／after 各一次）；存取／登入兩源 realIp 精確等值。
- **清理**：固定序守門（工程判斷⑥）；拒因 `biz.audit.invalidTable`（2222）與 `biz.audit.purgeBelowFloor{minDays}`（2222、經 BizData；D7）；自記之動作詞彙 `purge`（ADR⑥）；fault-injection 原子性測。
- **存取日誌寫入**（B2；工程判斷⑧；rev4 形）：中介層只掛在已認證子路由內側（授權判定之後；Public 子路由構造上不掛＝未認證零列）、無豁免名單（稽核讀端自身亦記）；進入時擷取方法與 `uri().path()`（★絕不含 query string、絕不讀 body）、操作者 uid 與請求上下文（真實來源位址、對端、XFF 判定窗轉錄、信心）；回應**先回**、再非同步寫入（MUST NOT 同步 await）；上下文或身分缺席即跳過（不 panic、不 500）；寫入失敗只 `tracing` 結構化告警＋降級 metric（③d 依此重錨）、業務回應零影響；region／trace_id 無料源＝NULL。
- **設定**（D1、工程判斷③⑬⑭）：updateSystemSetting 同交易落操作日誌（`update`、標的＝設定鍵、快照舊→新）；後端「零稽核」測試反轉；讀端 wire 擴充下發 REGISTRY 宣告界與宣告旗標；wire-schema 快照同步；系統設定兩檔碼註歸因順改。
- **reaper**（B1、B4、D8；工程判斷⑨⑩⑪）：`server/src/bin/reaper.rs` 以 rev4 藍本重打字；token-reap＝過期票（含寬限天數）單語句刪除；audit-retention＝固定表序（操作→存取→登入嘗試→會話事件）、逐表單交易「水平線刪除＋自記」、環境變數三分語意（缺席 90、畸形告警退 90、低於 `PURGE_MIN_DAYS` 前置全拒且先於連線）；policy-reconcile＝唯讀逐維殘留列與候選外現役列計數；三 job 各自心跳分組（`reaper_last_success_timestamp`／`reaper_deleted_total` 形＋對賬計數 metric，名稱於 plan 期定）；連線走 `reaper_database_url`（最小權限 role）。
- **m0004**（工程判斷⑪）：reaper role＋GRANT；選單 77 buttons 增 `audit:purge`；R_SUPER `audit:purge` 按鈕授權列（不受保護）；演進帳 `seed_update`／`seed_add`、序號合成照 007 GR9；RUNBOOK §10 Day-1 登記三步（第 3 步 pristine 庫）。
- **其他**：msg 鍵 `biz.audit.*` 三語 backend 子樹同批、與 `MSG_KEYS` 跨端對賬；新讀型入 wire 裁判表；ROUTES 61→66 逐列釘值測（`tools/docsync/tests/test_references.py` 之真 repo 釘值案同改；動 ROUTES 之單元另跑 `python3 -B tools/docsync test`）；碼註現在式改述（`model/audit.rs`、`facade/session_event.rs`、`facade/sys_login_attempt.rs`、`facade/sys_operation_log.rs`、`handler/auth/logout.rs` 之「`rev5:008` 增量不帶／沒有 delete」類句，清理入刀後寫明清理是唯一刪除路徑；rules.yml ④「rev6 尚無該 handler」）。

### §3 前端

- **系統設定頁**（§III.2 (ix)）：單檔、資料驅動（enum on/off→開關、number→數字框、其他→唯讀）；四組固定序（密碼策略／工作階段／IP 源登入／帳號登入，依鍵前綴；未列序新鍵排組尾、空組整卡不渲染）；逐項即改即存（開關切換即提交；數字欄失焦或 Enter 提交、清空不送；成敗皆回讀全列）；數字框以讀端下發界值鉗界；宣告集外列唯讀、排組尾、標示 description；三對跨鍵矛盾即時警示、不阻存（D2）；寫入政策七鍵任一成功即呼叫密碼政策 hook 之清除函式（D3）；label＋help 三語全映射（節流兩組說明不承諾嚴格上限）；接既有 `rev6-settings.ts` 兩支 wire（型別隨讀端擴充）。
- **稽核頁**（§III.2 (x)）：四分頁＋各自搜尋卡（同構、預設展開；時間區間本地輸入、UTC 上 wire＝D4）；XFF 純文字欄（ellipsis＋tooltip）；traceId／region 欄集照 rev5；操作日誌快照浮層（純文字 JSON、值已由後端打碼）；清理浮層（表名×天數兩欄、輸入框下界＝UX 護欄）以 `audit:purge` 碼顯隱（D6）；登入嘗試分頁告示「節流短路遭拒不落表」語意；新檔 `rev6-audit.ts`／typings（§III.1 BASE-WEB-WRAPPER／ADAPT）、`Api.Audit` 命名空間。
- **路由與譯文**：三語 `route:`／`page:` 樹與 `app.d.ts` 型節同批；`route: Record<I18nRouteKey, string>` 使 route 譯文不能先於 view 落地（同單元或其後）；路由產物四檔以外掛重算（route-artifact-gate 冪等）；seed-view-gate EXEMPT 兩列於交付頁之同單元摘除、自測改斷言空表、`TestRunCheck` 兩支真表案重寫。
- **密碼政策 hook**（D3）：增清除函式；檔頭「只增不清」與「寫入者唯一」句、重設浮層檔頭快取已知態句同批改述。
- **fork-delta 與修憲銜接**：範圍欄預估、收刀前 PATCH 實數化；view-render-guard 守則（禁原始 HTML 注入、表頭 prop 形錨）照舊。

### §4 測試、工具、驗收

- **測試**（rust 容器內 serial；base-web 型檢容器內）：島 J 不變式逐條（讀端零寫入、清理唯一形與原子自記〔fault-injection〕、打碼單點、存取日誌 fail-open、J5 指針所指島 E 兩點既有測照舊）；四源讀端過濾、分頁、固定序、realIp 等值；清理拒因兩鍵與明細通道三鍵契約；設定寫端稽核列（舊→新）與讀端 wire 擴充；reaper 三 job（dry-run 零變動、execute 刪除與自記、環境變數三分語意、未知參數嚴拒、心跳失敗不改退出碼、對賬計數之正負向植入）；存取日誌中介層（已登入落列、未登入不落、寫入失敗回應不變＋告警）；m0004 連動釘值（受保護列數不變、新按鈕授權列、R_SUPER 按鈕集含 `audit:purge`、getUserInfo 三帳號按鈕集）；可授出集 30→35；wire-schema、msg 鍵跨端閘、authz_entrypoint_lint、route-artifact-gate、fork-delta-lint、seed-view-gate、view-render-guard、zh-tw-lint 全綠；schema 三閘（演進帳 seed 合成＋序號合成）。
- **工具**：BL-00148 離線對賬腿（m0004 單元之前；一正一反＋逐判準停用變異）；`RUNTIME_APPEND_TABLES`／`RESTORE_TABLES` 擴 `sys_access_log`＋自測；走查還原工具與 test_kit 守衛評估 reaper 與存取日誌之影響（走查期間不起 jobs）；子句表檢核工具（D11；主線工作區前例改寫）。
- **觀測層**（B5 與重錨）：`rules.yml` ③d／⑤⑤b／⑥⑥b 依 as-built 重錨、新增對賬非零告警；`rust-api.json` 刪三空面板並重排；`reaper.json`／`master-overview.json` reaper 面板描述改 as-built；`audit-log.json` trace_id 描述改述；可選起 obs／metrics profile 活體驗證。
- **驗收**：觸及之島不變式全過；CDP 三方對照（22080 對 32080，必要時加 22089；對照步驟兩側顯式設簡中；對照面＝兩頁全套、清理浮層、快照浮層、側欄兩項；CDP 一律 opus[1m] xhigh）；刻意分岔逐項登記（存取分頁有資料、設定變更入操作日誌、跨鍵提示、快取清除、`audit:purge` 碼、實作期新發現者）；繁中驗收＝D12（全部接真頁面之 AI 逐頁審讀紀錄＋user 抽查）；側欄兩項煙測判準反轉（裸鍵與 No match→正常進頁）；走查基準本機自取 snapshot、前後還原 diff rc 0；dev 庫寫入步驟逐步取 user 放行（LL-00053）；jobs profile 活體跑一輪（dry-run 與 execute 各一）。
- **現在式假述掃除**（RL-0011、`python3 tools/docsync errata` 枚舉；種子例）：`BL-00045`、`BL-00043`、`BL-00133`、`BL-00139`、`BL-00148`、`seed-view-gate`、`恰兩列`（`seed-view-gate.py` 檔頭 rev5 原始版史述句不改、現在式兩處改）、`008 刀`、`島 J`、`未入憲`、`稽核域行為島`、`保留期`、`purge_before`、`沒有 delete`、`尚無該 handler`、`rev5:008`、`死項`、`view 未進場`、`設定頁 view 刀`、`view 刀`、`裸鍵`、`只增不清`、`起了也跑不動`、`無事件源`、`reaper bin`、`access_log_mw`；另點名（種子掃不到）：系統設定兩檔三行碼註（工程判斷⑬）、重設浮層檔頭快取句、RUNBOOK §11.3「008 刀前無設定頁畫面＝走 API」改設定頁首選、`schema-definition.md` §8 缺頁句改為不隨刀前進之形（ADR-00087；基線字面不動；改此檔時 pre-commit 跑 schema-gate test）。
- **單元草案**（約 20 支；tasks 定稿於 SDD）：U0 前置體檢＋Amendment 親決＋施工前提 ADR accepted → U1 骨架（ROUTES 61→66 空殼＋授權態矩陣＋可授出集）→ U2 BL-00148 離線對賬腿 → U3 m0004（role＋`audit:purge`）＋演進帳＋閘序號合成 → U4 四源讀端 facade＋打碼單點 → U5 讀端 handler＋`Api.Audit` wire 裁判 → U6 清理＋拒因三鍵 ADR 落地＋msg-key-gate 擴 → U7 存取日誌中介層＋runtime-append 常數 → U8 設定寫端稽核＋讀端 wire 擴充＋碼註順改 → U9 reaper 骨架＋token-reap＋心跳依賴 → U10 audit-retention → U11 policy-reconcile → U12 觀測層（告警重錨、對賬告警、儀表板 B5）＋compose jobs 段現況改寫 → U13 繁中與三語譯文底（兩頁 page／route 樹、backend 鍵） → U14 系統設定頁 → U15 稽核頁＋清理與快照浮層＋seed-view-gate 摘列 → U16 走查還原工具與 test_kit 守衛 → U17 文件、ADR 續行群、假述掃除 → U18 CDP 三方對照＋繁中全頁審讀 → U19 收刀前承載體檢＋Day-1 登記三步＋範圍欄 PATCH 實數化＋子句表逐列核。
- **風險**：R1 m0004 之 CREATE ROLE 與 GRANT 於 dev 庫冪等重跑與 pristine 庫行為（U3；Day-1 第 3 步）；R2 BL-00148 離線腿遇 DDL 類語句之形制（U2、ADR⑨）；R3 存取日誌每請求一寫之負載與走查 diff 恆報差（U7、U16）；R4 reaper 與走查／真庫測試互擾（jobs 只在指定步驟起；U9～U11、U16）；R5 HTTP 依賴新增之版本拍板（全域 §6）；R6 errata 面廣（兩頁、島 J、清理、觀測層四族）；R7 dev 庫寫入放行（LL-00053）；R8 BL-00049 條件依賴；R9 繁中全頁審讀量隨刀累增（D12）；R10 子句表規模與 007 同級（D11）；R11 正則閘存活者（工程判斷⑲）；R12 規模（§4；grilling 輪必提）。

## 4. 規模總帳（user 2026-10-20 指定 grilling 輪必提）

| 面向 | 比照 rev5:008 | 本刀（照 §0 拍板） | 增量來源 |
|---|---|---|---|
| 執行單元 | rev5:008 為 U1～U9（37 個 T）；rev6 同射程估約 12 支（rev6 另有三語、更多碼面閘與文件面） | 約 20 支（§3 §4 單元草案）；參照 007＝U1～U23（117 個 T） | B1 reaper 三支＋觀測層一支、B2 一支、BL-00148 一支、m0004 一支、D1／D3 併入既有單元 |
| migration | 零 | m0004 一支（或拆兩支）：reaper role＋GRANT（權限面 DDL）＋`audit:purge` seed | B1、B4、D6 |
| 新依賴 | 零 | pushgateway 推送之 HTTP 實作（甲：既有 exporter 之推送功能、乙：ureq）；版本依全域 §6 | B1 |
| 解除「不得帶回」 | 零 | 004 刀防回歸清單 B 之 `rev5:R2-9`（存取軌跡中介層） | B2 |
| ADR | rev5:008 立 2 支 | 約 10 支（§3 §1 ADR 待立） | B1～B4、D1～D10 |
| 憲法 | MINOR（島 J 入、J2 空缺） | MINOR 1.9.0（島 J 全入、J2 回填） | D10 |
| BACKLOG 淨流量（008 窗） | 約 −2（開放窗 −1＋BL-00045） | 約 −6（另收 BL-00043／00133／00139／00148） | B1～B5 |
| 繁中驗收面 | 兩語、無繁中 | 全部接真頁面逐頁審讀＋抽查 | D12 |

> 主線原建議（v11 體檢）＝B1～B4「不做、照 rev5」；改建議之前提＝把開工令之「評估進來」讀成「能收就收」。若 grilling 輪縮回 rev5 射程：B1、B2、B4 改不入 ⇒ m0004 與新依賴消失、BL-00148／BL-00139 不到期、BL-00043／BL-00133 收窄留列，008 窗回到約 −2。

## 5. 憲法 §IV 九題預答（供 `/speckit-plan` Constitution Check 起手）

1. base-web 為權威：PASS——設定頁與稽核頁之選單、元件鍵與 seed 端點早已預埋，本刀補齊 view 與端點；存取日誌與 reaper 屬後端稽核面、不涉 upstream 功能縮減。2. base-web inline：**涉及——授權以 Amendment 先行取得**（§III.2 (ix)(x)）。3. casbin：PASS——讀端與清理零 casbin_rule 寫入；`audit:purge` 碼與 R_SUPER 按鈕授權列經 m0004（seed 基線層級決策＝島 G 之 G2 末句）；可授出集隨五支註冊再算（ADR-00081 款 9）。4. §I.3：**涉及**——錯誤明細通道擴第三鍵（D7）；四保留碼零觸碰。5. 前代 source：否——rev5／rev4 重打字消化、翻案項不帶回（§1 末兩列）。6. §II：無抵觸。7. ★ 軌道：觸及——新用途 (ix)(x)、須 Amendment（§V.2；user 親決）。8. 建業務表／migration：是——一支 delta migration m0004（不建表；reaper role 權限面＋seed 增碼與授權列）；BL-00148 離線腿於其單元前；收刀前 Day-1 登記三步（RUNBOOK §10）。9. §I.7：觸及——島 J 隨本刀以 MINOR 入憲（J1～J5）；以狀態機與生命週期鏡頭設計（稽核列之寫入→保留→水平線清理→自記、存取日誌 fail-open、殘留授權偵測），非 CRUD 格子。

## 6. 給 `/speckit-specify` 的輸入摘要

- feature 名＝`008-audit-settings-pages`；user 故事核心＝US1 超管調整系統設定（四組、逐項存、界值、矛盾提示、政策快取清除、變更入操作日誌）／US2 稽核查閱（四源四分頁、搜尋與時間區間、XFF、快照打碼）／US3 稽核資料生命週期（手動清理＋reaper 自動保留與票回收、30 天下限、原子自記）／US4 存取軌跡（已登入請求落列、fail-open）／US5 授權殘留偵測（policy-reconcile 只報不刪）／US6 治理連動（島 J 入憲、`audit:purge` 碼、可授出集、觀測層與儀表板）；五支端點、一支 delta migration m0004、憲法 1.9.0。
- 直接輸入：本檔＋§2 處置表所列 BL＋`rev5:008-audit-settings-pages` spec 之 US、FR、SC、Edge Cases（rev6 座標改寫：ROUTES 61→66、seed 列號以 rev6 現數、handler 持交易形、rev6 test_kit 守衛形、CDP 基準 rev5 HEAD）＋rev4 reaper 契約（token-reap／audit-retention 之 CLI 與心跳）。
- FR 措辭要求：清理守門固定序寫成表；島 J 各條方向寫明 fail-open／fail-closed；reaper 三 job 各自之退出碼與心跳語意；存取日誌射程（已登入請求、授權判定之後）；設定寫端稽核之快照形；三對跨鍵矛盾逐對列出；★spec 須含「★ 軌道逐處登記」表、「刻意分岔登記」表與子句層需求追溯表（D11）；Out of Scope 逐條指承載；繁中驗收 SC 照 D12。
- clarify 候選：對賬計數 metric 與告警規則之名稱與門檻；m0004 拆不拆兩支；HTTP 依賴取捨（甲／乙）。

## 7. 隨做隨記

- ADR 待立見 §3 §1；plan 期全數產 draft；Amendment 顆只含島 J／§III.2 ADR 與其連動條文、其餘另顆。
- 收刀 `backlog_done` 5 條（BL-00043／BL-00045／BL-00133／BL-00139／BL-00148）；本檔零 `backlog_add`。
- NOTES「下一步」：本檔定稿 commit 同批改為「008 brainstorm 定稿、待 user grilling 本檔後 `/speckit-specify`」；specify 起手後改為 008 進行中。
- grilling 輪（user 2026-10-20 預告叫用）：首提 §4 規模總帳；結論入 §0 末段與各節。
- migration：m0004＝本刀唯一 migration；施工單元同批登演進帳、收刀前跑 RUNBOOK §10 Day-1 登記三步（第 3 步 pristine 庫）；BL-00148 離線腿須先於其單元。
- 依賴：pushgateway 推送之 HTTP 實作若需新 crate，版本於 plan 期依全域 §6 兩源比對、分歧即問 user。
- 走查基準本機自取（`.specify/feature.json` 仍指 007＝specify 起手後更新）；007 終態基準於本刀自取基準後才可清。
- 活書：06／10（島 J 情境）、05（`tools/` 列「恰兩列」與 seed-view-gate 描述）、07（jobs profile 現況）、08（稽核頁時間輸入語意）、11（角色選單已知態款數、IP 域已知態寫入者）、12（稽核域詞組：水平線清理、自記、存取軌跡、殘留授權）；C4-L2 reaper 列與 C4-E2 隱私流節保留期句改為現況；RUNBOOK §3／§8／§9c／§10／§11／§12 於 feature branch 內改成現在式。
