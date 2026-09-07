# 003-auth-session — auth 域整批 brainstorm（階段 0）

- 日期：2026-09-07（Q1～Q4 與設計十一節）／2026-09-08（Q5～Q8 grilling 壓測輪與六處修補）｜狀態：拍板十題（Q1～Q4 定範圍、Q5～Q8 壓測輪一、Q9～Q10 壓測輪二）＋設計十一節已過 user 核可；下一步＝**手動** `/speckit-specify`（本檔為其 input；不自動觸發——否則 before_specify hook 不跑、分支不建、spec 落 default）。
- 一句話：把 base-web fork 原版 service 已在呼叫的認證與路由端點補齊到終態——真帳密登入、DB-stateful token rotation、會話撤銷與單一會話治理、帳號維登入節流＋圖形驗證碼、dynamic 側邊欄、後端 msg 前端轉譯；並以同一筆 MINOR Amendment 開立憲法 §III.2 首批 ★ 軌道與 §I.7 首批行為島。
- 交付價值：rev6 第一次端到端可見（瀏覽器真登入 → 側邊欄由後端 Casbin 過濾生成 → 錯誤訊息顯人話），且 rust-api release profile 第一次可跑（`dev_identity.rs` 整檔汰換）。

> 輸入：001 brainstorm §0 Q1 刀序表（003＝auth-session；「各刀範圍由各自 brainstorm 定、可翻」）、憲法 §I.2／§I.3／§I.5／§I.6／§I.7／§II／§III／§IV、`docs/ops/NOTES.md` 下一步、`docs/ops/BACKLOG.md` 觸發於本刀之條目、002 brainstorm Q7（`.env` route mode 延本刀）、ADR-00003 註 4、ADR-00012 決定 6、ADR-00014、ADR-00017、`docs/ops/RUNBOOK.md` §9c／§16、002 開刀前承載體檢（掃 002 spec Out of Scope 十六項對現在式帳本之承載；六條新 BL 與兩處修落於 default）、rev5 `rev5:003-auth-session` 全套（brainstorm／spec／research／data-model／contracts／quickstart／tasks；唯讀、凍結 SHA 外層 7eab28a／base-web 9833308／rust-api 92919b9）。

## 0. 拍板紀錄（Q1～Q4＝user 拍板 2026-09-07、一題一問；Q5～Q10＝user 拍板 2026-09-08、grilling 壓測輪一／二；首選項皆為建議）

| 題 | 拍定 | 要點 |
|---|---|---|
| Q1 刀範圍 | **A・整批一刀：US1～US5** | 憲法只 bump 一次（★軌道與行為島一次入憲）、base-web 只進場一次、fork-delta 只跑一輪、刀序號不動（BACKLOG 已有條目以刀名形引用 004 ip-trust-anchor／006 authz-governance／008 audit-settings-pages，插號要回頭改）；rev5 已驗證的整批結論直接照施工、翻案面最小。棄案：拆兩刀 US1～3／US4～5（憲法 bump 兩次、base-web 兩輪 fork-delta，且節流與 captcha 依驗收必須擋在 argon2 之前＝第二刀要回頭改第一刀的 login handler；第一刀期間前端顯示的是識別字而非人話）；整批但砍 US5 之 stub（upstream 三張表單維持假成功＝安全誤導，rev5 明文要消滅）。★「只做 US1」不成立：access token 壽命 300 秒，沒有 US2 無感續期＝每五分鐘被登出、不是可交付物 |
| Q2 帶不帶 migration | **零 migration（事實、非選擇）** | 實查 m0001 基線已含：`sys_token` 9 欄＋`uq_sys_token_chain_active` partial UNIQUE（同鏈至多一 active 的 DB 層護欄）＋`sys_user.session_policy`／`session_id`＋`session_event`＋`sys_login_attempt`；16 鍵 seed 全在 m0002。⇒ **BL-00042 不觸發**（其觸發＝「下一支帶 migration 的刀開寫前」），不需在 `/speckit-specify` 之前立跨刀活體契約抽取 ADR。待 plan 期複核：casbin 政策列零新增（rev5 同判、seed 66／67 同源） |
| Q3 前端 i18n 範圍 | **承 rev5 形：兩語 runtime＋繁中錨點檔** | `en-us.ts`／`zh-cn.ts` 插 backend 譯文樹（修改型、runtime 生效）＋新建 `zh-tw.ts` 裸 object 錨點檔（不接 runtime、當跨端閘右源與繁中譯文的家）；**不擴 `LangType`、不註冊 zh-TW 語系**（延前端 UI 刀，同 `rev5:R3-15`）。UI 對照 rev5 零差異（預設仍 zh-CN）。棄案：只做兩語不建錨點檔（繁中譯文沒有家、rev5 成果無法承襲落地）；把 zh-TW 註冊成第三介面語言（rev5 明文延前端 UI 刀、無藍本、譯文自 271 行擴到全量、UI 對照多一維，且本刀主題是 auth 不是 i18n） |
| Q4 登入頁三顆快速登入鈕 | **保留＋記帳** | 三顆鈕與表單預填密碼皆 upstream 基線既有；保留＝與 rev5 UI 對照零差異（本刀是首個能真登入、也是首個能全面走查的刀，對照面越乾淨越好），且手動驗收一鍵切三帳號正是 US1 的驗收項（三角色側邊欄差異）。代價＝dev 帳密露在登入頁 ⇒ BACKLOG 立一條「轉 prod 前必須拆除」、觸發綁 RUNBOOK §16 那筆 prod 硬化 ADR 落地時（rev6 無 prod 硬化刀，不綁不存在的刀）；★卷別由 Q7 改定為滯後卷＝BL-00049。棄案：拿掉（CDP 對照與 rev5 出現差異、首輪對照就得標具名例外且會一直跟著；每次手動驗收切帳號要手打）；只清預填密碼（鈕裡仍寫死同一組＝假改善，帳照樣要記） |
| Q5 ADR draft 產出時點 | **plan 期產 draft、tasks 首單元只跑後三步** | plan 的 research 定 Amendment 形制（★軌道表格的機器可解形、島條文骨架），ADR draft 檔同期落 feature branch；tasks 首個主線任務只做「user 親決→accepted→bump→generate」。好處＝親決時看到的是完整 draft、draft 經過 plan 那一步的審查、實作起點不卡在等人寫 draft。棄案：承 rev5 把四步全放 tasks 首單元（實作起點卡一次親決、draft 未經 plan 審查輪）；specify 之後就 draft（★軌道「範圍（檔案）」欄是硬邊界，那時尚未做設計、名單必定要再走一次 Amendment 改） |
| Q6 BL-00037 收到什麼程度 | **全收 ①②** | ①pre-push 面接線之機器守衛（`test_hook_wiring.py` 的 `HOOK` 常數自單指 pre-commit 改為三支＋對應斷言）＋放寬 pre-commit 之 selftest-docsync 觸發樣式；②`tools/bootstrap.sh` 呼叫名冊改自 tracked 檔集推導。理由＝條目意圖即「補腿與該面的下一次改動同批落地、避免為補腿單開一輪」，本刀正在改這批檔，分開做要再開一次同一批檔；兩項皆治理工具內部、不碰 auth 碼。棄案：只收②（①的觸發同樣已成立卻不收＝條目觸發欄得同時改窄）；兩項都不收（把已到期條目用改觸發欄往後推，且「專門的治理維護批」＝另開輕量軌、`gov_ratio` 再 +1） |
| Q7 快速登入鈕的帳立哪一卷 | **立在 `BACKLOG-DEFERRED.md`＝BL-00049** | 觸發本質不可到期（RUNBOOK §16 逐字寫「prod 不入 roadmap」），放開放帳等於讓檔頭「觸發須可到期」形同虛設；滯後卷正是為此設，且仍計入 GT-05 配號家族、查待辦全帳本就兩卷併看。副作用＝滯後卷首次啟用、STATE 分開計數。棄案：立在 BACKLOG（同 rev5，但 rev5 真有一把 prod 硬化刀）；只在 ADR 記已知態（查待辦的人看不到＝正是 002 承載體檢抓到的「延後但無家」形） |
| Q8 BL-00029 去留 | **轉 `BACKLOG-DEFERRED.md`** | 16 鍵治理端點只有超管能寫、無併發場景，觸發極可能永不到期；純拍板、零改碼、不動 `gov_ratio`。與 Q7 同一判準、避免兩條同型兩種處置。棄案：留在 BACKLOG（每把刀掃觸發欄都要跨過它一次）；直接刪列判定永不做（需多一筆 won't-fix ADR，且該端點真高頻化時那個優化仍成立） |
| Q9 島 B 生效時點 | **承 rev5：翻轉不追溯、只在下次登入時踢** | 不變式寫成「單一會話只於登入事件判定；`single_session_default` 翻轉不影響既有會話」。前後對照：甲已在手機與電腦各登入一次、超管翻 on → 甲兩邊都繼續能用，直到甲在第三裝置登入才踢掉前兩個。好處＝零新寫路徑、設定寫端（002）與會話域零耦合、rev5 已驗證。已知代價＝翻開後存在「政策 on 但實際多會話」的窗口，上限＝refresh 全壽命（seed N=60 ⇒ 約 65 分）。棄案：翻轉即踢（設定寫端要認識會話域＝跨域耦合、002 spec 明寫設定值零行為兌現、rev5 無藍本、後端自主決定留哪一鍵）；承 rev5 但把窗口上限與翻案路徑寫進憲法（多一句、留活書即可） |
| Q10 TDD implementer 模型 | **維持既有偏好：發射前把成品 `IMPL_OPTS` 調 `opus[1m]`** | 不在本 doc 射程、屬 TDD 起手前置；因 user 主線模型已切 Fable 5.1 而重問一次，裁定不變：骨架真源 `_sk_head.js` 不動（`IMPL_OPTS`＝`fable[1m]`），每支 run 組裝後、發射前改 `tmp/*.mjs`；三角色全 opus、與 001／002 實作期同組模型、結果可比。棄案：直接用骨架真源 fable（少一道手工、但失去與前兩刀的可比性）；改骨架真源（違「換模只調成品不改骨架」、且屬輕量軌改動不該夾在 003） |

**工程判斷（主線自拍、報備備查；RULES 名詞段判準下非拍板級）**

1. **跨端閘的形不照抄 rev5 三向斷言**：rev5 的 Lint24 是「子集／白名單存在性／白名單 ∩ 實發＝∅」三向，白名單九鍵是 007 使用者域的鍵——rev6 現在預載即成孤兒鍵。改為「後端 `MSG_KEYS` ⇔ 三檔各自的 backend **子樹**鍵集」逐檔雙向比對：backend 子樹本身是封閉集，不需要白名單機制，比三向更簡單且更強。ADR-00017 決定 3 所稱「雙向必恆紅」指整本字典、不指 backend 子樹。
2. **Amendment 的凍結步（親決→accepted→bump）排在 tasks 的第一個主線任務**，draft 於 plan 期產出（Q5）；不提前到 specify 之後：§III.2 表的「範圍（檔案）」欄是硬邊界，要 plan 的設計定案才列得準。plan 的 §IV 第 2／7／9 題填「涉及——授權以 Amendment 先行取得」、GATE 狀態＝條件通過。**硬序：Amendment accepted 前不得動任何 base-web 既有檔。**
3. **走查基準工具落 `tools/` 頂層並進 `NON_GATE_TOOLS`**：它是走查前後的全表對賬工具、不掛 pre-commit、不守版控品質，不是碼面閘（同 `tools/wf-watchdog.py` 之定位）；GT-12 之「`tools/` 頂層 `*.py` − `NON_GATE_TOOLS` ⇔ RUNBOOK 碼面閘表」腿據此仍綠（該常數現值只有 `tools/wf-watchdog.py` 一支，加入須同批改 `tools/docsync/gates.py` 並補 GT-12 自測）。
4. **BL-00031 收刀時改條文、不只在 notes 記**：本刀只收 `login_throttle_*` 一對，收刀時把條文中「003 auth-session（`login_throttle_*` 對鍵）」那一段刪去、只留 004／007 兩對——否則收刀後條文仍宣稱本刀是其消費側之一、帳面失準。
5. **前端執行單元的 TDD 規則以該單元 `CONTEXT` 收窄**：base-web 側零測試框架，implementer prompt 的規則塊會帶「先紅後綠」這條做不到的規則；改在該單元的 `CONTEXT` 明文記「本單元無測試框架、先紅後綠不適用；驗收＝`pnpm typecheck` 綠＋兩段 review＋CDP 對照走查」。**不動 RULES**（動 RULES 會 bump `RULES-VERSION`、影響全部骨架）。

## 1. rev5 承襲盤點（沿用項照已驗證結論施工、翻案項用新設計；CLAUDE.md §2）

| rev5 項目 | 處置 | rev6 落點 |
|---|---|---|
| 五個 user story 與其優先序（`rev5:003` spec US1～US5） | 沿用 | 本刀範圍本身（Q1） |
| 未認證／會話失效三分碼：exp 過期→`3333`／缺席・非 Bearer・簽章不符・已撤銷・鏈失效→`8888`／被踢→`7777` | 沿用 | `error.rs` 三新變體；同時兌現 ADR-00014 後果段「003 接真 session 時對 3333／8888 分工重定」 |
| `sys_token.status=='revoked'` 即權威、denylist 純加速層（缺鍵→靜默 `8888`、不落事件、不重複撤；reuse 只保留給 `rotated`＋grace miss） | 沿用 | 會話狀態機（設計 §5） |
| rotation grace 冪等窗 **30 秒**、住 redis、fail-secure | 沿用（含其代價：redis 故障期間並發 refresh 觸發撤家族＝多分頁全域登出、重登復原） | 島 A 不變式 |
| logout 對任何 refresh token（含垃圾／已撤）一律 `0000` 冪等 no-op、不落事件 | 沿用（回異碼＝提供 token 有效性 oracle） | `handler/auth/logout.rs` |
| denylist TTL 兩 reason 一律 `refresh_secs`（`rev5:R3-8` 已修正 rev4 的不對稱） | 沿用 | 島 C 不變式 |
| captcha 字元集 34 字（小寫 a-z 去 `o`＋數字去 `0`）、`CaptchaClaims` 四欄不設 `ctx` | 沿用 | `captcha/mod.rs` |
| 多角色首頁＝啟用角色（`status=1`）依 role id 升冪取首個非空 `role_home`、全空退 `home`，選出後仍過可導航葉兜底 | 沿用 | `handler/route.rs` |
| `constantRoutes` **合併**而非取代 builtin 五條（seed `constant=TRUE` 為 0 列、取代語意會清空登入頁） | 沿用 | base-web route store 接線 |
| 模組名 `cache`（不叫 `redis`、消歧包袱不帶回）；`captcha` 模組保留同名、以三條書寫規則＋檔頭碼註承載 | 沿用 | `cache/mod.rs`／`captcha/mod.rs` |
| `handler/auth/` 拆五檔（rev4 單檔約 860 生產行 ⇒ 防呆六件套⑥的允許檔案清單失去圈界力） | 沿用 | `handler/auth/{login,refresh,logout,user_info,alt_stub}.rs` |
| 降級矩陣十二列（`rev5:003` research R5）、方向刻意不一致者兩處：redis 整體不可用＝軟區 captcha 整層停用（fail-open）vs captcha SET NX 瞬斷＝拒但不罰；idle 設定鍵缺失＝fail-loud `5000` 不猜值 vs 節流設定鍵讀不到＝退活書常數 | 沿用 | 島 A～E 不變式、隨 Amendment 入憲 |
| 觀測三序列 `throttle_degraded_total`（label `source` 六值）／`denylist_hit_total`（`redis`｜`pg`）／`throttle_soft_zone_total`；`captcha_forced` 不計入軟區計數；rev4 的 HLL 廣度兩支不做 | 沿用 | `obs.rs` 的 pre-register |
| `precheck` 完全不讀 redis unlock marker（`rev5:R3-17`；本刀無解鎖端點＝無寫入者、讀了恆 nil），SQL 參數位保留 | 沿用 | `throttle/mod.rs` |
| IP 維節流／HLL 廣度／`suppressed_breadcrumb` 一律不做（`rev5:R3-3`） | 沿用 | 不入刀、留 004 ip-trust-anchor |
| `formRules` 放寬（`rev5:R3-12`）與 request 層 8888 前插 toast（`rev5:R3-13`）兩用途不開 | 沿用 | ★軌道用途數為八、非十 |
| `.env` 翻 `VITE_HTTP_PROXY=N`、不開 DEVPROXY 軌道、由 nginx 前置拓樸取代（`rev5:R3-14`） | 沿用 | `.env` 四行走 §III.1 BASE-WEB-ADAPT |
| `app.d.ts` 只補 `backend` 必填型節；`LangType`／locale 註冊／`zh-tw.ts` 標型重構延前端 UI 刀（`rev5:R3-15`） | 沿用（Q3） | 設計 §7 |
| `zh-tw.ts` 治理錨點孤立檔 | 沿用其形、**起手鍵集不同** | rev5 由其 002 建、rev6 002 拍零 locales 改動 ⇒ 本刀自零建，起手鍵集＝後端實發 13 鍵（002 既有 7＋本刀 6） |
| Lint24 三向斷言（含前端內部鍵白名單九鍵） | **翻案**（工程判斷 1） | 改逐檔雙向比對 backend 子樹、不設白名單 |
| B-047 `method_not_allowed_fallback` 之 4040 解讀與其前置研究 | **不適用** | rev6 002 之 `router.rs` 已含 fallback（未註冊路徑＋方法不符→4040），本刀零前置 |
| `rev5:B-028` 冷編量測、`rev5:B-001` K1 承襲盤點 | 不做 | rev6 無對應帳（同 002 處置） |
| rev4→rev5 拍板差異點 17 筆（`rev5:003` research R3） | 全部視為已翻案、**不得帶回** | 烤進 implementer prompt 的防回歸清單 |

## 2. BACKLOG 觸發項處置（動工前掃描、CLAUDE.md §2）

- **BL-00026**（觸發：首次觀測層維護批、或 003 auth 刀 boot 鏈再動時）→ 本刀必動 boot 鏈：`main.rs` 之裸 `ConnectOptions::new` 改帶 `sqlx_logging_level(Debug)`、`log` 釘 `0.4.33`（`rust-api/Cargo.lock` 現值、零新套件）、同批刪同檔上一行自陳為 BACKLOG 候選的註解（RL-0011 枚舉）。收刀 `backlog_done`。
- **BL-00041**（觸發：下一支動 rust-api 的刀）→ 本刀必動 rust-api：`server/src/model/facade/test_kit.rs` 與 `server/src/handler/system_settings.rs` 兩處前代刀號改 RL-0046 冒號前綴形；**同批**把 GT-05 之裸三碼刀號腿的子庫 pin 樹側（`SUB_SCAN`）接上（分開做要多一次 pin bump；改法已載於 `tools/docsync/book.py` 註解）。收刀 `backlog_done`。
- **BL-00030**（觸發：首個接 i18n 的前端刀進場）→ Q3 拍定範圍即觸發：本刀同批立跨端閘（形＝工程判斷 1）、RUNBOOK §12 碼面閘表之註記列轉工具檔列。收刀 `backlog_done`。
- **BL-00031**（觸發：三對不變式之消費側各自進場）→ 本刀為 `login_throttle_captcha_after ≤ login_throttle_max_fails` 一對的消費側：由節流三區實作決定不變式方向與拒因。`ip_*` 對留 004 ip-trust-anchor、`password_*` 對留 007 user-password-admin ⇒ **本條不刪列**，收刀時改條文刪去 003 那一段、只留 004／007 兩對（工程判斷 4）。
- **BL-00037**（觸發：下次動 `.githooks/**` 或 bootstrap 名冊時）→ 本刀新增跨端閘工具與走查基準工具，兩者皆進 `tools/bootstrap.sh` 的 `run_tool_test` 名冊、跨端閘另需 pre-commit 條件觸發段 ⇒ 觸發成立：同批收其①（pre-push 面接線之機器守衛＋放寬 selftest-docsync 觸發樣式）與②（bootstrap 呼叫名冊改自 tracked 檔集推導）。收刀 `backlog_done`。
- **BL-00042**（觸發：下一支帶 migration 的刀開寫前）→ Q2 判定零 migration，**不觸發**、本刀不碰。
- **BL-00028**（觸發：m0002 seed 或 002 data-model §3 任一變動時）→ 零 migration 且 registry 十六鍵集合凍結，本刀對 `system_settings` 只讀（走查驗收期以 `updateSystemSetting` 翻設定值後 RAII 還原、非 seed 變動）⇒ 不觸發。
- **BL-00029**（Q8）→ 已轉 `BACKLOG-DEFERRED.md`（觸發極可能永不到期）、不再佔開刀前掃描面。
- **BL-00049**（Q7）→ 快速登入鈕已知態，直接立於 `BACKLOG-DEFERRED.md`；本刀零動作、只是它的立帳刀。
- 其餘條目觸發未到、本刀不碰：BL-00002／00027／00035／00036／00038／00039／00043／00044／00045／00046／00047／00048。

## 3. 設計（十一節、user 已核可）

### §1 目標與範圍

**入刀**：US1 真帳密登入＋側邊欄由後端 Casbin 過濾生成｜US2 access 過期無感續期（token rotation）｜US3 會話撤銷與單一會話治理（logout／被踢／閒置逾時）｜US4 帳號維登入節流三區＋圖形驗證碼｜US5 替代登入四流程誠實 stub＋錯誤訊息顯人話。量級：ROUTES 4→16、`AppError` 6→9 變體、`AppState` 兩欄→五欄、`dev_identity.rs` 整檔汰換。

**不入刀**：IP 維節流與信任錨（004 ip-trust-anchor）｜改密／首登強制換密／email-verify／mailer（007 user-password-admin）｜no-escalation 本體（006 authz-governance；其預告失準已由 BL 對沖）｜四支管理頁 view（008 audit-settings-pages）｜`/auth/error` 端點（兩張 demo 頁消費；憲法 §I.1「v1 從簡只能是交付排程」⇒ 收刀新記一條 BL 當排程錨、承 `rev5:B-053`，非設計範圍縮減）｜`LangType` 擴充與 zh-TW 語系註冊（前端 UI 刀）｜`formRules` 放寬（改密端點刀）。

### §2 憲法 Amendment 射程（MINOR 1.2.0→1.3.0）

一筆 Amendment 同時開兩面：

- **§III.2 首批 ★ 軌道四條八用途**：`BASE-WEB-AUTH-WIRING`（auth store／route store／captcha hook 三用途）／`BASE-WEB-LOGIN-CAPTCHA-WIRING`（登入頁軟區接線一用途）／`BASE-WEB-I18N-WIRING`（request 層轉譯／locales backend 樹／`app.d.ts` 型節三用途）／`BASE-WEB-LOGOUT-UX-WIRING`（登出前呼 API 一用途）。範圍欄逐檔列出（硬邊界、名單外一律無授權），處數為估值、以 `rev6-inline` 標記實數為準。
- **§I.7 行為島 A～E 入憲**：A token rotation／B single-session／C denylist 撤銷／D idle 逾時／E 登入失敗節流（帳號維）。以 state-machine 鏡頭寫「現態×事件→次態＋副作用」，不寫 CRUD 格子；常數值與欄級細節留活書。

★軌道與島皆屬「循憲法明文機制正式取得授權」的路徑，非違規 ⇒ plan 的 Complexity Tracking 不填，改在 Constitution Check 記授權鏈與硬序約束。

### §3 後端架構與模組邊界

按功能域分模組：`auth/{jwt.rs 新, enforce.rs 改, mod.rs 改}`（`dev_identity.rs` 整檔刪）／`cache/mod.rs` 新／`throttle/mod.rs` 新（帳號維三區）／`captcha/mod.rs` 新；handler 依端點群拆檔：`handler/auth/{login,refresh,logout,user_info,alt_stub}.rs`、`handler/route.rs`、`handler/captcha.rs`。facade 新增 `sys_token`／`session_event`／`sys_login_attempt`／`sys_menu`／`sys_user`／`sys_role` 六支。`model/password.rs` 承 argon2 驗章與 `dummy_verify` 時序等化。`{state,error,router,config,request_context,obs}.rs` 改。

**兩處碼內舊拍板須翻、各立 ADR 並同批改寫註解**：`rust-api/server/src/state.rs` 的「恰兩欄是拍板釘死的邊界」封條（含其編譯期窮舉解構錨測）→ 五欄（rev5 同位＝`db`／`enforcer`＋jwt 設定／cache 句柄／captcha 簽章密鑰三欄；確切欄集與型待 plan 定，見 §5 clarify 候選⑤）；`rust-api/Cargo.toml` 的「不引 argon2」註解 → auth 依賴群進場。`server/Cargo.toml` 之依賴清單形待 plan 期核。

### §4 會話狀態機與降級不變式

`sys_token` 狀態機以 `rotation_chain`（＝會話身分 sid）為鏈、`status` 為態；DB 層護欄＝m0001 既有的 `uq_sys_token_chain_active` partial UNIQUE（同鏈至多一 active）。rotate 次序：先舊列轉 `rotated` 再插新 `active`。撤銷語意的權威是 `sys_token.status`，redis denylist 只是加速層——其狀態（TTL 短／連線故障／資料遺失）永不污染稽核帳。

本刀實際消費的設定鍵恰五個（16 鍵之中）：`session_idle_timeout`／`single_session_default`（會話面）＋`login_throttle_max_fails`／`login_throttle_captcha_after`／`login_throttle_window_minutes`（節流面）。島 B 生效時點（Q9）：單一會話只於登入事件判定，`single_session_default` 翻轉不追溯既有會話（窗口上限＝refresh 全壽命）。降級方向見 §1 承襲表；兩處刻意的方向不一致（redis 整體不可用 vs 單次寫入瞬斷；idle 設定鍵 vs 節流設定鍵）須在 Amendment 條文與 data-model 逐條寫明理由，避免後刀誤判為缺陷。

### §5 節流三區與 captcha

帳號維三區以 `sys_login_attempt` 滑動窗為權威（L2／PG）、redis 為 L1 負快取；門檻取自 registry 三鍵（`login_throttle_max_fails`／`login_throttle_captcha_after`／`login_throttle_window_minutes`），讀不到退活書常數並每次載入至多一筆告警。**節流與 captcha 拒絕一律擋在 argon2 之前**（零稽核列、零計數桶）；鎖內重驗不重跑 argon2；滑動窗子查詢必帶窗下界（防全歷史回掃）。captcha 為無狀態簽題＋redis nonce 一次性標記。

BL-00031 之 `login_throttle_captcha_after ≤ login_throttle_max_fails` 不變式由本節消費側定方向與拒因。

### §6 dynamic 選單與授權

`getUserRoutes` 以 DB-fresh roles 經 Casbin `menu` 維度 `get_filtered_policy` 過濾 `sys_menu` 樹（含祖先包含、同層 order→id 升冪），`home` 走多角色兜底規則。demo menu 仍全集在 seed、不啟用 `hideInMenu` 治理。`getConstantRoutes` 與前端 builtin 五條**合併**。零新 casbin 政策列（待 plan 複核）。

### §7 前端接線與 i18n

`.env` 面走 §III.1 `BASE-WEB-ADAPT`——**三檔四行**（實查 rev5 同位）：`.env` 兩行（`VITE_AUTH_ROUTE_MODE` 翻 `dynamic`、`VITE_HTTP_PROXY` 翻 `N`）＋`.env.test`／`.env.prod` 各一行（`VITE_SERVICE_BASE_URL` 自 apifox mock 改為 `/api`；漏改＝test／prod build 打 mock）。四行皆修改型、須帶 `原行:` 標記，該檔類在 fork-delta-lint 射程內＝機器守得到。★軌道八用途逐處在 spec 的「★ 軌道逐處登記」表記位置＋改動內容＋upstream 衝突風險評估（憲法 §III.2 三必需欄位）。新檔一律 `rev6-` 前綴 wrapper 與 `typings/api/` 宣告檔（§III.1、純新增檔不觸 ★軌道、只需檔頭圈界標記）。

i18n：`en-us.ts`／`zh-cn.ts` 插獨佔一行的 backend 樹（修改型、runtime 生效）＋新建 `zh-tw.ts` 錨點檔；`app.d.ts` 只補 `backend` 必填型節。跨端閘形＝工程判斷 1。★i18n 三檔是 upstream 基線最熱檔，為本刀最高 rebase 衝突風險面。

### §8 治理面

碼面閘新增兩支：跨端閘（BL-00030）與走查基準對賬工具（RUNBOOK §9c、`NON_GATE_TOOLS`）。兩者皆入 `tools/bootstrap.sh` 的 `run_tool_test` 名冊、README 樹（GT-09 對賬）、RUNBOOK §12；走查工具另須進 `tools/docsync/gates.py` 的 `NON_GATE_TOOLS`（現值單支）並補 GT-12 自測；跨端閘另需 pre-commit 條件觸發段 ⇒ 連帶收 BL-00037（見 §2）。RUNBOOK §9c 自指針章改實文（走查前後全表基準 snapshot／diff 之契約、清理判準）。

### §9 測試與 DoD

後端：`cargo test --workspace -- --test-threads=1`（容器內、全程 serial）＋contract 16 case（per route＋三分碼矩陣＋msg 名冊雙向）＋兩支 lint must-list 換檔。前端：**base-web 側零測試框架** ⇒ 前端執行單元的 TDD 迴圈退化為 `pnpm typecheck`＋review 迴圈＋CDP 對照走查。收刀 DoD 另含 `fork-delta-lint`、`wire-schema check`（本刀動 typings ⇒ base-web 側觸發首次真正生效、快照須重抽）、`docsync check`／`lint`、`schema-gate check`（gate2 seed 逐列綠——走查期 runtime 寫入會推進 sequence，須自帶重設守衛與 RAII 還原）。

### §10 單元切分草案（tasks 定稿於 SDD；此處只定骨）

沿 001／002 前例以 T 號區間表達單元邊界。骨架承 `rev5:003` research R9 之十四單元建議，rev6 調整：①B-047 前置研究不需要（002 已做 fallback）②i18n 單元加重（自零建 backend 樹與錨點檔）③治理單元加重（兩支新工具入四處名冊＋BL-00037 兩子項）④首單元＝★主線憲法 Amendment（硬閘：未 accepted 不得動任何 base-web 既有檔）。預估與 rev5 同量級。

### §11 風險

1. **i18n 三檔為 upstream 最熱檔**（rev5 實測近 12 月各 15–17 commit）⇒ rebase 衝突面最大；緩解＝修改型逐處帶 `原行:`、插入行為獨佔一行的 `  backend: {`。
2. **走查期 runtime 寫入推進三支 sequence**，與 gate2 seed 逐列比對相撞（本刀首撞）⇒ 走查基準工具與 RAII 還原守衛為硬前置，須排在首次走查之前。
3. **redis 不開 AOF**（已知態）：RDB 回捲窗內 denylist 鍵可丟；暴險由「`status` 即權威」封頂。
4. **前端零測試框架**：US1～US5 的前端腿只靠 typecheck＋review＋CDP 走查，缺自動回歸網。
5. **快速登入鈕暴露 dev 帳密**（Q4 已記帳、BL-00049）。
6. **nginx 邊緣層已有 per-IP 限流與 CF 標頭覆寫**——rev6 deploy 面於波 1 整批承襲 rev5 終態，領先後端兩刀：`auth_limit` zone 5r/s、burst 40、`limit_req_status 429`（無信封、不在 13 碼矩陣），套在 `/api/auth/{login,loginCaptcha,refreshToken,logout}` 四個 exact-match 塊；`X-CF-Verified`／`CF-Connecting-IP` 以 map 值無條件覆寫。屬 004 ip-trust-anchor 域、本刀零改動；但走查腳本與 US4「連續送錯密碼」驗收須知其在（burst 40 足、勿於秒內狂打）；contract test 走 oneshot 不經 nginx、不受影響。

## 4. 憲法 §IV 九題預答（供 `/speckit-plan` Constitution Check 起手）

1. base-web 為權威：PASS with disclosure——本刀為 fork 原版 service 已在呼叫的端點補後端實作；`/auth/error` 屬排程錨、非範圍縮減。2. base-web inline：**涉及——授權以 Amendment 先行取得**（★軌道四條八用途、十餘支既有檔；`.env` 四行走 §III.1）。3. casbin：menu 走 `enforce`、demo menu 進 seed 不隱藏。4. §I.3：三分碼落 `http()` 萬用臂、13 碼矩陣不動、`msg` 載穩定 key、序列化邊界 id 轉字串。5. 前代拷貝：rust 應用碼零拷貝、全重打字消化；走查基準對賬工具屬**隨遷工具**（RULES 名詞段授權、同 001 搬兩支閘工具之形），改座標＋註解重寫；防回歸清單＝`rev5:003` research R3 十七筆。6. §II：兌現 `.env` route mode 拍板；翻兩處**碼內**舊拍板（`state.rs` 恰兩欄、root `Cargo.toml` 不引 argon2）各立 ADR。7. ★軌道：**涉及——授權以 Amendment 先行取得**，屬「新能力」非「用途補完」。8. 新表：零、零 migration（Q2）；三張消費表皆 001 基線既有、只寫入不改結構。9. 行為島：**涉及——島 A～E 隨本刀以 MINOR Amendment 入憲**。

## 5. 給 `/speckit-specify` 的輸入摘要

- feature 名＝`003-auth-session`；user 故事核心＝使用者以帳密真登入取得可續期會話、側邊欄依角色由後端生成、登出與被踢即時失效、連續失敗受三區節流與圖形驗證碼保護、尚未開放的替代登入誠實拒絕、錯誤訊息以介面語言顯示人話。
- 直接輸入：本檔＋BL-00026／00030／00031／00037／00041＋`rev5:003-auth-session` 之 US1～US5、FR、SC、Edge Cases（沿用形、rev6 座標改寫：無 Lint24 白名單相關 FR、無 B-047 前置 FR；新增 i18n 字典自零建、兩支新工具入名冊、BL-00037 兩子項、走查契約補實文之 FR）。
- 待 clarify 候選：①三分碼與 ADR-00014 後果段的兌現措辭②跨端閘的雙向比對形與其一正一反自證③`zh-tw.ts` 錨點檔的檔頭圈界標記字面與軌道自稱名④走查基準工具的 rc 語意與 `NON_GATE_TOOLS` 登記⑤`AppState` 五欄的欄集與 `state.rs` 編譯期錨測的改法⑥六支新依賴的釘版（走全域 §6 雙源核對、plan research 記表）⑦dev 模式翻 `VITE_HTTP_PROXY=N` 後 base URL 的解析來源（rev6 `.env` 無 `VITE_SERVICE_BASE_URL` 行、疑由 vite mode 載 `.env.test`；rev5 四行改法走查通過、承襲即可但 plan 須實核）。

## 6. 隨做隨記

- ADR 待立（刀分支內落、序號自 ADR-00026 起）：主 Amendment（★軌道四條八用途＋島 A～E）／`AppState` 恰兩欄封條翻案／root `Cargo.toml` 不引 argon2 翻案／快速登入鈕已知態／跨端閘形制（工程判斷 1，若 clarify 判為需拍板）。
- 帳本已落（brainstorm 修訂同批）：BL-00049 快速登入鈕已知態立於滯後卷；BL-00029 轉滯後卷。開放 19｜滯後 2。
- ADR draft（主 Amendment）於 **plan 期**產出並落 feature branch（Q5）；tasks 首個主線任務只跑「user 親決→accepted→bump→generate」。
- 收刀 `backlog_done`：BL-00026／BL-00030／BL-00037（全收①②）／BL-00041；BL-00031 只收 `login_throttle_*` 一對、不刪列但**須改條文刪去 003 那一段**（工程判斷 4）。
- 收刀 `backlog_add` 另新記一條：`/auth/error` demo 端點排程錨（承 `rev5:B-053`；觸發＝首個動 demo 頁的前端刀）——本刀 Out of Scope 之排程錨不得無家（002 承載體檢同型教訓）。
- 收刀 `feature_close` 之 `backlog_add` 必須列 BL-00043～BL-00048 六條（開刀前承載體檢配號已發、事件未載，六筆 GT-03 在途 WARN 由此消）。
- TDD 發射前置（Q10）：每支執行單元 `assemble.py` 組裝後、發射前把 `tmp/<uN>.mjs` 之 `IMPL_OPTS` 改 `opus[1m]`（骨架真源不動；重組後須再調）——寫進 tasks 的每單元發射步。
- NOTES「下一步」：specify 起手後同批改為 003 進行中；收刀時改 004。
- 活書：arc42 §5（server 管線 as-built）／§6（會話狀態機、登入失敗節流兩情境）／§8（API 慣例三分碼、fork-delta 接線現況）／§12（auth 域詞：會話＝`rotation_chain`＝sid／憑證對（access＋refresh）／態三值 active・rotated・revoked／撤銷三型＝登出（本鏈）・踢除（他鏈）・家族撤銷（reuse 偵測）／grace 窗／節流三區＝自由・軟區・硬鎖／denylist 加速層 vs `status` 權威／idle 逾時；★「降級」與既有 AI 術語「降級輪廓」撞詞——另立系統術語條「降級（基礎設施）＝redis／PG 不可用時的 fail-* 方向」以區分）於 feature branch 內改成現在式；C4-L2 若拓樸不變零改。
