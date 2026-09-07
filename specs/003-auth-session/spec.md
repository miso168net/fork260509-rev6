# Feature Specification: 003 auth 域整批——真登入、會話生命週期、節流＋驗證碼、dynamic 選單、i18n 轉譯

**Feature Branch**: `003-auth-session`

**Created**: 2026-09-08

**Status**: Draft

**Input**: User description: "docs/brainstorms/003-auth-session.md"（階段 0 brainstorm 定稿 2026-09-07／08、grilling 壓測兩輪十題 Q1～Q10 皆 user 拍板；本 spec 之唯一輸入。該檔 §0 拍板紀錄與五項工程判斷、§1 rev5 承襲盤點、§2 BACKLOG 觸發項處置、§3 設計十一節、§4 憲法九題預答為權威來源；rev5 對應刀 `rev5:003-auth-session` 之 spec 為沿用形之藍本、rev6 座標改寫）

> 摘要：把 base-web fork 原版 service 已在呼叫的認證與路由端點補齊到終態——真帳密登入、DB-stateful token rotation、會話撤銷與單一會話治理、
> 帳號維登入節流三區＋圖形驗證碼、dynamic 側邊欄、後端 msg 前端轉譯（兩語 runtime＋繁中錨點檔、自零建）；ROUTES 4→16、`AppError` 6→9 變體、
> `AppState` 兩欄→五欄、`dev_identity` 整檔汰換（rust-api release profile 第一次可跑）。同一筆 MINOR Amendment（1.2.0→1.3.0）開立憲法 §III.2
> 首批 ★ 軌道四條八用途與 §I.7 首批行為島 A～E。零 migration（`sys_token`／`session_event`／`sys_login_attempt`／`sys_user.session_policy`
> 與 16 鍵 seed 全在 001 基線；零新 casbin 政策列）。治理面同刀進場：msg key 跨端閘（BL-00030）、走查基準對賬工具（RUNBOOK §9c）、
> hook 接線守衛（BL-00037）、boot 鏈 log 級距（BL-00026）、裸前代刀號兩處＋子庫腿（BL-00041）。交付價值＝rev6 第一次端到端可見
> （瀏覽器真登入 → 側邊欄由後端 Casbin 過濾生成 → 錯誤訊息顯人話）。

## Clarifications

### Session 2026-09-08

- Q: `AppState` 自兩欄（db／enforcer）擴成哪種形（欄集）？（FR-032、候選⑤）→ A: **A 五欄承 rev5**——`db`／`enforcer`／`jwt`（簽章設定）／`cache`（`Option`：測試 None＝快取自始缺席之降級測試面、production 恆 Some、boot 建連失敗即 fail-loud panic）／`captcha_secret`；
  編譯期窮舉解構錨測改五欄同形；「恰兩欄」封條翻案 ADR 之決定文據此（棄案：三欄 auth 子結構打包＝取用多一層、Option 語意藏進子結構；四欄 captcha 密鑰併 jwt 設定＝兩把秘鑰語意混型、與 RUNBOOK §7 輪替表分列不對齊）。
- Q: msg key 跨端閘的比對語意——後端名冊 ⊆ 前端字典（ADR-00017 決定 3 字面、單向）還是後端 `MSG_KEYS` ⇔ 三檔各自 backend 子樹（逐檔雙向全等）？（FR-027、候選②）→ A: **A 逐檔雙向全等＋立 ADR**——
  backend 子樹本刀自零建、為封閉集，雙向同時守「後端多發前端沒譯」與「某檔孤兒鍵／`zh-tw.ts` 漏插」、不需 rev5 九鍵白名單；新 ADR 一筆記形制與射程（不翻 ADR-00017：其「雙向必恆紅」指整本字典、不指子樹）。棄案：單向子集（少守一半、rev5 為此長出白名單＋腐化斷言）；雙向不立 ADR（「⊆→⇔」強化無拍板級的家）。
- Q: `login_throttle_captcha_after > login_throttle_max_fails` 矛盾組合（002 寫端逐鍵驗、寫得出）本刀讀到時如何處置？（FR-015、BL-00031 消費側定方向與拒因）→ A: **A 視同設定不可用→退活書常數（2／5／15）＋一筆 `degraded=settings_invalid` 結構化告警（每次載入至多一筆）**；002 寫端零改動；
  與島 E「節流設定鍵讀不到退常數」同一降級腿、零新碼路徑，方向隨島 E 條文入憲。前後對照：寫成 6／5 → 實際行為同 seed 2／5、`throttle_degraded_total{source=settings_invalid}` +1。棄案：clamp 取 min（軟區寬度歸零＝狀態機少一態、靜默修正）；fail-loud `5000`（全站不能登入、超管自己也進不去改）。
- Q: 超管改設定值後對已登入者何時生效——要不要在島條文寫成一句總則？（FR-005／FR-009／FR-031）→ A: **A 寫總則：每個設定鍵只在其消費事件當下讀現值；已簽發 token 的壽命與已建立會話不追溯**——
  具體＝`single_session_default` 於登入判定（Q9）；`session_idle_timeout` 於每次簽發（登入／換發）讀現值套 TTL 與 idle 門檻 ⇒ 既有會話最晚於下一次換發（≤ access 壽命 300 秒）採新值、手上 token 的 exp 不變；節流三鍵於每次登入嘗試讀現值 ⇒ 立即。承 rev5 實作、零新碼；007 密碼鍵同律。
  前後對照：idle 60→30 分 → 已登入者下一次換發起以 30 分計。棄案：只寫島 B 一句、其餘留活書（三鍵三答案散兩層、改活書不走 Amendment）；idle 以簽發時 N 為準烙進 token claims（新 claim、rev5 無藍本、換發簽新對仍讀現值＝新舊 N 同鏈混用）。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 真帳密登入取得會話、側邊欄由後端生成 (Priority: P1)

作為 admin 後台使用者，我以帳號密碼登入，系統驗章成功後發給我一對可續期的憑證；登入後我看到的側邊欄選單，是後端依我的角色經 Casbin 過濾後
動態生成的（非前端寫死），且登入頁等內建常量路由不受影響；登入頁三顆快速登入鈕仍可一鍵切換三個 seed 帳號（Q4 保留、BL-00049 記帳）。

**Why this priority**: 這是 rev6 第一次端到端可見——沒有真登入與 dynamic 側邊欄，一切後續功能刀（四支管理頁 view、no-escalation、IP 信任錨）都無入口。
它獨立成 MVP：只實作 login＋getUserInfo＋getUserRoutes＋getConstantRoutes 與前端 dynamic 接線，即交付「瀏覽器真登入看見角色化側邊欄」的完整價值。
★但「只做 US1」不是可交付物：access 壽命 300 秒，沒有 US2 無感續期＝每五分鐘被登出（Q1）。

**Independent Test**: 起 rev6 dev stack，瀏覽器（入口 `http://127.0.0.1:32080`）以三個 seed 帳號（Super／Admin／User）分別登入，觀察三者側邊欄差異；
比對 getUserInfo 回包（userId 字串型／userName 為 nick_name／roles／buttons）與 getUserRoutes 樹（角色可見選單）；CDP 對照 rev5 基準（22080）零差異。

**Acceptance Scenarios**:

1. **Given** seed 三帳號在庫、`.env` 已翻 `VITE_AUTH_ROUTE_MODE=dynamic`＋`VITE_HTTP_PROXY=N`＋base URL＝`/api`，**When** 使用者以正確帳密經 `/auth/login` 登入，
   **Then** 回 `{data:{token,refreshToken}, code:"0000"}`、前端存憑證並轉呼 getUserInfo／getUserRoutes、側邊欄呈現該角色可見選單。
2. **Given** 已登入的 access token，**When** 呼叫 `/auth/getUserInfo`，**Then** 回 `{userId(字串), userName(＝nick_name fallback user_name), roles[], buttons[]}` 四欄皆備
   （User 帳號之 userName 顯 `User01`＝seed 資料兌現、碼中零帳號字面）。
3. **Given** dynamic 模式，**When** 呼叫 `/route/getUserRoutes`，**Then** 回 `{routes[], home}`——routes 為該使用者角色經 Casbin `menu` 維度過濾後的 sys_menu 樹
   （含祖先包含、同層 order→id 升冪）、home 為經多角色收斂律與可導航葉兜底解析的頁。
4. **Given** 登入前尚無 access token，**When** 呼叫 `/route/getConstantRoutes`，**Then** 回常量路由集（Public 可取得）；前端與寫死的 5 條 builtin 常量路由
   （403／404／500／iframe-page／login）**合併**而非取代（seed `constant=TRUE` 為 0 列、取代語意會清空登入頁）。
5. **Given** 錯誤帳密（帳號不存在／密碼錯／帳號停用任一），**When** 登入，**Then** 一律回 `1000`（`auth.login.failed`）、三態 collapse 同一碼、不洩漏帳號是否存在。
6. **Given** 登入頁三顆快速登入鈕，**When** 逐顆點擊，**Then** 各自以對應 seed 帳號真登入成功、側邊欄呈現三種不同角色化選單（本刀對該鈕零 inline）。

---

### User Story 2 - access 過期無感續期（token rotation） (Priority: P2)

作為已登入使用者，當我的短命 access token 過期時，系統以我的 refresh token 自動換發新的一對憑證、我的操作不中斷、也不會被要求重新登入；
並發請求同時觸發換發時不會誤判我盜用而登出。

**Why this priority**: 續期是「可續期會話」的核心；沒有它，使用者每隔數分鐘就被登出。依賴 US1 的登入但可獨立驗收（登入後等 access 過期、觀察自動 refresh）。

**Independent Test**: 登入後直接以舊 last_activity 值寫入（免注入時鐘）觸發各分支；或以同票兩並發驗證 rotation 冪等——斷言一支 rotate、一支走 grace 回同一對、不觸 reuse。

**Acceptance Scenarios**:

1. **Given** access 過期（回 `3333`），**When** 前端自動以 refresh token 呼叫 `/auth/refreshToken`，**Then** 回新的一對憑證（舊 refresh 列轉 `rotated`、插新 `active` 同鏈）、
   原請求以新 token 重放成功。
2. **Given** 同一 refresh token 的兩個並發換發（多分頁），**When** 兩請求先後到達，**Then** 一支完成 rotation、另一支在 grace 窗（30 秒）內冪等回既發後繼的同一對、
   **不**觸發 reuse 偵測、**不**落 `session_event(reuse)`。
3. **Given** 已 rotate 過的舊 refresh token 且 grace 窗已過，**When** 再次持它換發，**Then** 判為 reuse→撤銷整條會話家族＋落 `session_event(reuse)`→`8888`（唯一觸發 reuse 的形）。
4. **Given** refresh token 簽章失敗／過期／垃圾值，**When** 換發，**Then** 一律回 `8888`（★絕不 `3333`——否則前端自動 refresh 死迴圈）。

---

### User Story 3 - 會話撤銷與單一會話治理（logout／被踢／閒置） (Priority: P2)

作為使用者，我登出後舊憑證立即在伺服器端失效；當單一會話政策開啟時，我在他處**登入**會使前一會話被踢下線（顯示 modal）；長時間閒置的會話會逾時失效。
政策翻轉不追溯既有會話（Q9）。

**Why this priority**: 撤銷語意是安全面的底線（登出即撤、他處登入即踢）。依賴 US1／US2 的會話狀態機但可獨立驗收各撤銷路徑。

**Independent Test**: logout 後以舊 token 打受保護端點得 `8888`；`single_session_default` 前置以 002 寫端翻 on 後同帳號二次登入、斷言前一條下個請求得 `7777`；
idle 直接寫舊 last_activity 值觸發逾時；翻 on 前已存在的兩條會話翻後仍皆可用（不追溯）。

**Acceptance Scenarios**:

1. **Given** 已登入使用者，**When** 於 UI 按登出（前端 best-effort 呼 `/auth/logout` 後清本地儲存），**Then** 該 refresh token 對應會話於伺服器端撤銷、舊憑證再打受保護端點得 `8888`；
   logout 對任何 refresh token（含垃圾／已撤）一律 `0000` 冪等 no-op、不落事件。
2. **Given** `single_session_default=on`（前置以 `updateSystemSetting` 翻、驗收後 RAII 還原），**When** 同帳號在他處二次登入，**Then** 前一會話被踢、其下個請求得 `7777`
   （modal「你已在他處登入」人話）、落 `session_event(kicked, reason=single_session)`。
3. **Given** 甲已在手機與電腦各登入一次、超管此時把 `single_session_default` 翻 on，**When** 甲兩邊繼續操作，**Then** 兩邊都繼續可用（翻轉不追溯）；
   直到甲在第三裝置登入才踢掉前兩條（單一會話只於登入事件判定）。
4. **Given** 會話閒置超過 `session_idle_timeout`，**When** 持既有憑證換發或請求，**Then** 判 idle 逾時→`8888`、僅首次落 `session_event(idle)`（冪等守門、背景 refresh-loop 不刷重複列）。
5. **Given** 被踢者在 access 過期後於 (access, refresh) 窗內換發，**When** refresh，**Then** 仍得 `7777`（denylist TTL＝refresh 全壽命保證，不降級為 8888、不落假 reuse）。

---

### User Story 4 - 登入失敗節流三區＋圖形驗證碼 (Priority: P3)

作為系統，我對同一帳號的連續登入失敗施以三區節流：少量失敗自由重試、達門檻後要求圖形驗證碼、再失敗則短暫鎖定；驗證碼答對但登入仍失敗時自動換發新題。

**Why this priority**: 節流是 001 已 seed 的三區狀態機（`login_throttle_captcha_after=2`／`login_throttle_max_fails=5`／窗 15 分鐘），不做 captcha 軟區即塌。
依賴 US1 的登入路徑但可獨立驗收三區轉換。

**Independent Test**: 對同一帳號連續送錯密碼（★經 nginx 時勿於秒內狂打——邊緣層 `auth_limit` 5r/s burst 40 回無信封 429、屬 004 ip-trust-anchor 域；contract test 走 oneshot 不經 nginx），
斷言失敗 <2 自由／2–4 回 `2222 biz.auth.captchaRequired`／≥5 回 `2222 biz.auth.locked`；軟區送正確驗證碼但錯密碼→登入失敗且自動換題。

**Acceptance Scenarios**:

1. **Given** 某帳號失敗次數在滑動窗內 <2，**When** 再次登入失敗，**Then** 直接回 `1000`（不要求驗證碼）。
2. **Given** 失敗次數達 2–4（軟區），**When** 未帶或帶錯驗證碼登入，**Then** 回 `2222 biz.auth.captchaRequired`——在密碼驗章之前擋下、不落稽核列、不消耗計數桶。
3. **Given** 失敗次數 ≥5，**When** 登入，**Then** 回 `2222 biz.auth.locked`（同樣驗章前擋、零列零桶）；成功登入使滑動窗計數重置。
4. **Given** 軟區帳號，**When** 呼叫 `/auth/loginCaptcha?userName=X`（含不存在帳號），**Then** 一律發題（`{captchaId, captchaImg(data URI)}`、零存在性洩漏）；
   userName 超限走與登入端點同形的 `1000` 閘；產圖／簽章內部失敗→`5000`。
5. **Given** 軟區帳號答對驗證碼但密碼錯，**When** 登入，**Then** 回 `1000` 且該題已耗、前端自動換題；答錯驗證碼不推進鎖定但該題作廢須重取。

---

### User Story 5 - 替代登入四流程誠實 stub＋錯誤訊息顯人話 (Priority: P3)

作為使用者，當我嘗試手機驗證碼登入／註冊／重設密碼等尚未開放的流程時，得到明確的「該功能尚未開放」提示（而非假成功）；
且所有錯誤／狀態提示以我的介面語言顯示人話，而非後端識別字。

**Why this priority**: 誠實 stub 消滅 upstream 三張表單的假成功（安全誤導、rev5 明文要消滅）；i18n 前端轉譯兌現「錯誤訊息顯人話」的交付價值。
依賴 US1～US4 產生的 msg key 但可獨立驗收提示文案。

**Independent Test**: 送出替代登入四流程任一，斷言回 `2222 biz.auth.notSupported`、UI 顯示對應語言人話；切換語系觀察同一後端 key 顯示不同語言譯文；
繁中譯文以 `zh-tw.ts` 錨點檔為家（不接 runtime、Q3）。

**Acceptance Scenarios**:

1. **Given** upstream 三張表單（code-login／register／reset-pwd），**When** 送出，**Then** 打後端 stub 回 `2222 biz.auth.notSupported`、UI 顯示「該功能尚未開放」人話（非假成功 toast）。
2. **Given** 後端回任一業務碼（如 `biz.auth.captchaRequired`／`auth.login.failed`），**When** 前端顯示，**Then** 經 `$t` 轉譯為當前語系人話（zh-CN 顯簡中／en-US 顯英文）、
   未命中鍵才 graceful fallback 回原文。
3. **Given** 7777 被踢 modal，**When** 顯示，**Then** modal 內容為轉譯後人話（非 `auth.session.kicked` 裸鍵）。
4. **Given** 後端 msg 名冊 13 鍵，**When** 跑跨端閘，**Then** `en-us.ts`／`zh-cn.ts`／`zh-tw.ts` 三檔各自的 backend 子樹鍵集與名冊逐檔雙向相等；任一檔少一鍵或多一鍵即紅並指名。

---

### User Story 6 - 憲法 Amendment、治理進場與帳本落帳 (Priority: P4)

作為 workspace 維護者，我要在動任何 base-web 既有檔之前，以一筆 MINOR Amendment 把 ★ 軌道四條八用途與行為島 A～E 入憲（draft 於 plan 期產、tasks 首個主線任務凍結、Q5）；
同刀把 msg key 跨端閘與走查基準對賬工具遷入四處名冊、收 BL-00037 兩子項、BL-00026 boot 鏈、BL-00041 兩處註解＋子庫腿；並於刀內立 ADR、收刀事件把 BACKLOG 帳結清——
使 003 期間每一處 base-web inline 自第一行起就在授權邊界內受機器守、每筆拍板都有家。

**Why this priority**: 治理項與功能可分開驗收，但 Amendment 是**硬序前置**（accepted 前不得動 base-web 既有檔），其餘治理項與功能單元並行；優先序只表達「不是交付價值本體」、不表達次序。

**Independent Test**: Amendment 落地後 fork-delta-lint 名冊斷言對四條 ★ 軌道一正一反（名冊內過／名冊外攔／用途外攔／檔外攔）；跨端閘與走查工具各做一次非 vacuous 自證；
GT-12 對 `NON_GATE_TOOLS` 新成員一正一反；hook 接線守衛刪一行即紅；不需任何 auth 碼即可驗收。

**Acceptance Scenarios**:

1. **Given** plan 期 ADR draft 已落 feature branch，**When** user 親決→accepted→憲法 §III.2 表落四列（哨兵句同批移除）＋§I.7 落島 A～E＋bump 1.3.0＋generate，
   **Then** 獨立 commit 落地、fork-delta-lint 對四條 ★ 軌道名冊斷言生效；在此之前 base-web 既有檔零 diff。
2. **Given** 跨端閘落地，**When** 合成三檔任一少一鍵／多一鍵／檔缺席，**Then** 自測紅並指名；真 repo 三檔 13 鍵對齊後綠；pre-commit 於 rust-api 或 base-web pin bump 時條件觸發。
3. **Given** 走查基準對賬工具落地，**When** 走查前 snapshot→真登入走查→清理→diff，**Then** rc 0 才算環境已還原；未清理即 diff 得 rc 1 並列出差異表／序列／redis 前綴。
4. **Given** BL-00037 兩子項落地，**When** 自 `tools/bootstrap.sh` 刪去任一 `run_tool_test` 行、或改 pre-push 接線字面，**Then** 守衛紅並指名；對齊後綠。
5. **Given** 收刀，**When** append `feature_close` 事件，**Then** `backlog_done` 列 BL-00026／00030／00037／00041、`backlog_add` 列 BL-00043～BL-00049 七條（含滯後卷 BL-00049）與新記的 `/auth/error` 排程錨、
   `adrs` 列本刀全部 ADR；BL-00031 條文已刪去 003 那一段。

---

### Edge Cases

- **並發同鏈 rotation**：同鏈至多一條 active 由 `uq_sys_token_chain_active` partial UNIQUE 硬保證；並發失敗模式＝唯一鍵衝突 DbErr，MUST 辨識並轉 grace 冪等分支、不得籠統回 `5000`。
- **redis 全故障（島 A～E 各異、隨 Amendment 入憲）**：denylist 查 fail-closed（退 PG `has_active_in_chain`、PG 亦故障→視為無 active 拒絕、絕不盲放）；idle fail-open
  （無 last_activity 即不 idle-reject、退 token exp 為界）；grace fail-secure（並發 refresh 觸發家族撤銷、多分頁全域登出、重登復原＝已知態）；captcha 分兩層——
  整體不可用→軟區要求停用（fail-open、免把合法使用者鎖死；密碼錯仍照常計數）／單次標記寫入瞬斷→拒但不罰。
- **redis RDB 回捲**（不開 AOF＝已知態）：denylist 鍵可在回捲窗內丟失；暴險受「`sys_token.status` 即權威」封頂（換發被 PG 擋）、復活面＝被踢者既有 access 直打 API 至自然過期（≤access TTL）。
- **設定鍵讀不到（兩處刻意相反）**：節流三鍵退活書常數＋一筆 `degraded=settings_default` 告警（每次載入至多一筆）；`session_idle_timeout` 缺失於 login 套 TTL 步反而 fail-loud `5000`（不猜值）；
  `single_session_default` 缺鍵→off 語意。三方向皆隨 Amendment 條文寫明理由。
- **`login_throttle_captcha_after > login_throttle_max_fails`（BL-00031 矛盾組合；clarify 定案）**：消費側視同節流設定不可用→退活書常數（2／5／15）＋`degraded=settings_invalid` 告警（每次載入至多一筆）；002 寫端不加驗證（零改動）；方向隨島 E 入憲。
- **設定值改動對已登入者的生效時點（clarify 總則：消費事件當下讀現值、不追溯已簽發）**：`single_session_default` 翻轉時已有多會話（Q9）→ 不追溯、只在該帳號下次登入時判定並踢，窗口上限＝refresh 全壽命（seed N=60 ⇒ 約 65 分）＝已知態、記活書非憲法；
  `session_idle_timeout` 改值 → 既有會話最晚於下一次換發（≤300 秒）採新 TTL 與門檻、手上 token 的 exp 不變；節流三鍵改值 → 下一次登入嘗試立即生效。
- **X-Real-IP 缺席**（integration 直打、無 nginx）：`sys_login_attempt.real_ip` 為 INET NOT NULL，測試 MUST 顯式注入 X-Real-IP、不為缺席開回填值。
- **x_forwarded_for 惡意值**：入庫前截斷至 1024 字元＋剝 CR/LF；該欄為不可信原文、渲染端轉義隨稽核 UI 刀（008 audit-settings-pages）。
- **非 2xx HTTP 吞信封**：前端 validateStatus 只放 2xx＋304，非 2xx 使錯誤信封整個丟失——故 `1000`／`2222`／`3333`／`7777`／`8888` MUST 皆映射 HTTP 200；僅 `4040`→404、`5003`→403（憲法 §I.3）。
- **方法不符**：002 已落 router 兩道 fallback（未註冊路徑／方法不符→`4040` 信封＋HTTP 404）；本刀 12 條新 route 自然納入、零前置研究（rev5 所需之 `rev5:B-047` 前置於 rev6 不適用）。
- **loginCaptcha 廢題**：字元集含 `0`／`o` 時產圖 crate 靜默跳過無 glyph 字元→約 20% 不可解題；故字集 MUST 為 34 字（去 `o`／`0`）。
- **nginx 邊緣層限流先於後端存在**：rev6 deploy 面波 1 已承襲 rev5 終態——`auth_limit` 5r/s burst 40、`limit_req_status 429`（無信封、不在 13 碼矩陣）套四個 auth 端點，
  `X-CF-Verified`／`CF-Connecting-IP` 無條件覆寫；屬 004 ip-trust-anchor 域、本刀零改動；走查腳本與 US4 驗收須知其在（burst 40 足、勿秒內狂打）。
- **走查期 runtime 寫入推進 sequence**：真登入寫 `sys_token`／`session_event`／`sys_login_attempt` 三支 sequence，與 schema-gate gate2 seed 逐列比對相撞（本刀首撞）
  ⇒ 走查基準對賬工具與 RAII 還原守衛為硬前置、排在首次走查之前；還原判準＝diff rc 0。
- **Amendment 硬序**：accepted 前任何 base-web 既有檔出現 diff＝違序；§III.1 純新增檔（`rev6-` 前綴 typings／service 新檔）不受此限。
- **i18n 三檔為 upstream 最熱檔**（近 12 月各 13–15 commit）：修改型逐處帶 `原行:`、插入行為獨佔一行的 `  backend: {`；rebase 時先比對 upstream 是否已自行新增 `backend` 節，若是則改為對齊而非疊加。
- **`/auth/error` demo 端點**：base-web 原版兩張 demo 頁經 `fetchCustomBackendError` 打 `GET /auth/error`——本刀 16 條 ROUTES 不含；`.env` 翻 `/api`＋dynamic 後 R_SUPER 可見該兩頁、
  點擊得 `4040`＋`system.notFound` 信封＝user 可見已知態；排程錨於收刀新記 BACKLOG（Out of Scope）。
- **快速登入鈕暴露 dev seed 帳密**：upstream 基線既有、本刀零 inline、UI 對照零差異；已知態由 BL-00049（滯後卷）承載、觸發＝RUNBOOK §16 prod 硬化拍板。
- **dev 模式 `VITE_HTTP_PROXY=N` 後 base URL 來源**（候選⑦、2026-09-08 實核）：`dev` script＝`vite --mode test` ⇒ `loadEnv` 載 `.env`＋`.env.test`；request 層 `isHttpProxy = DEV && VITE_HTTP_PROXY==='Y'`，翻 N 後 baseURL＝`.env.test` 之 `VITE_SERVICE_BASE_URL`（改 `/api` 即打 nginx）；四行改法承 rev5。
- **DDL 冒出**：clarify／plan 若出現任何 migration 需求→本刀範圍拍板翻案（BL-00042 觸發、須先立跨刀活體契約抽取 ADR）＋RUNBOOK §10 Day-1 三步；本刀硬預期零 migration。
- **rev5 側唯讀紀律**：一切讀取對凍結 worktree；絕不寫入、不動其 stack；走查工具只准指向 rev6 dev stack（3xxxx）、絕不指向 rev5 stack（2xxxx）。

## Requirements *(mandatory)*

### Functional Requirements

**端點與路由（ROUTES 4→16）**

- **FR-001**: ROUTES MUST 由 4 條擴為 16 條、`ROUTES_COUNT` 同 commit bump，逐條對齊 rev5 實表。新增 12 條：`/auth/login`（POST／Public）、`/auth/refreshToken`（POST／Public）、
  `/auth/logout`（POST／Public）、`/auth/getUserInfo`（GET／Authed）、`/auth/loginCaptcha`（GET／Public）、`/auth/{sendCaptcha,codeLogin,register,resetPwd}`（POST／Public）、
  `/route/getConstantRoutes`（GET／Public）、`/route/getUserRoutes`（GET／Authed）、`/route/isRouteExist`（GET／Authed）。三個 Public（refreshToken／logout／getConstantRoutes）
  各有非做不可理由（過期不能換／壞了不能撤／登入前需取常量路由）。contract case 登記表 MUST 每條 route ≥1 case（coverage gate 雙向：缺 case／殭屍 case 皆紅）；
  docsync routes 真表由 generate 重算。
- **FR-002**: 零新 casbin 政策列——16 條 route 無一為 `Protection::Policy`；163 列 seed 政策一列不動、維持零 migration。seed 已含後續刀政策列（kickUser／getSessionEvent／user:kick 等），
  本刀 MUST NOT 消費（防 review 質疑「政策設得進、端點不存在」）；plan 期複核此判（Q2）。
- **FR-003**: `/auth/loginCaptcha` MUST 帶 `?userName=` query（challenge 綁帳號的前提；對任意 userName 一律發題＝零存在性洩漏）；userName 超限走與登入端點**同形**的 `1000` 閘
  （零新碼零新 key）；產圖／簽章內部失敗→`5000`。

**認證與登入**

- **FR-004**: login MUST 依序執行十一步：①輸入形制閘（超限 `1000`、零稽核零驗章不消耗桶）②節流狀態機（FR-013）③`authenticate`（帳號不存在／密碼錯／已停用三態 collapse 同一 `1000`；
  不存在帳號仍跑等時序 dummy 驗章）④開 txn＋帳號級 advisory lock ⑤**鎖內重驗**（status／deleted_at／password 字面比對；★不重跑密碼驗章）⑥讀 `session_idle_timeout` 套 TTL（缺失→`5000` 不猜值）
  ⑦生新 sid＋簽對 ⑧`sys_token` insert ⑨single-session 判定＋逐 sid `session_event(kicked)`＋寫 `session_id` ⑩稽核成功列同 txn ⑪commit 後 best-effort 進 denylist＋last_activity 起點。
  ★第⑥步之 TTL 公式（規範）：`access = min(300, N×60/2)`／`refresh = N×60 + access`（N＝`session_idle_timeout` 分鐘）；seed N=60 ⇒ access 300s／refresh 3900s／idle 門檻 3600s。
  ★**稽核列寫入點恰三處**（FR-014「滑動窗為權威」的資料來源）：①`authenticate` Denied（外層 conn；uid 可為 None＝帳號查無）②鎖內重驗失敗（★先 rollback 再落列於**外層 conn**）
  ③成功（落 txn 內、與建會話原子）。**不落列四類**：形制閘超限／節流三個拒絕分支（構造上零寫入）／captcha 缺錯過期重放／`5000` 配置與內部異常。
  寫入為 best-effort：失敗只發 `degraded=db_write` 告警、不改登入回應——★但等於計數斷供（該帳號永不鎖亦永不 captcha），故 MUST 可觀測（FR-035）。
- **FR-005**: single-session 判定（第⑨步）MUST 為**兩層政策解析**：`effective_single = session_policy=='single' || (session_policy=='inherit' && single_session_default==on)`；
  `sys_user.session_policy` 值域＝{single, multi, inherit}（碼層收斂＋值域測試守、不加 CHECK 以保零 migration）；`single_session_default` 缺鍵→off 語意。
  ★生效時點（Q9、入憲條文；clarify 2026-09-08 總則之一例）：單一會話只於登入事件判定，`single_session_default` 翻轉不影響既有會話；設定寫端（002）與會話域零耦合。
- **FR-006**: getUserInfo MUST 回 `UserInfo{userId, userName, roles[], buttons[]}` 四欄皆備：`userId` typings 宣告字串、DB i64 於序列化邊界轉字串（憲法 §I.3）；
  `userName`＝`nick_name` fallback `user_name`（碼中零帳號字面）；`roles` DB-fresh；`buttons`＝Casbin `button` 維度政策枚舉（`get_filtered_policy`、非 `enforce*`＝不觸單一判定進入點守恆）。

**會話生命週期**

- **FR-007**: refresh MUST：驗章失敗一律 `8888`（★絕不 `3333`——jwt 底層恆吐過期、handler 漏 map_err 即死迴圈）；鎖呈遞列後分流——`active`→idle 檢查→rotate（舊列轉 `rotated`＋`used_at`、
  插新 `active`，次序不可反、partial UNIQUE 護欄）→寫 grace（TTL＝**30 秒**＞前端最壞換發間隔約 11 秒；★commit 前、仍持鎖時）；`rotated` 且 grace 窗內→冪等回既發後繼；
  `rotated` 且 grace miss→reuse 偵測（唯一觸發形）→家族撤銷＋`session_event(reuse)`→`8888`；`revoked`→denylist reason==kicked→`7777`／其餘（reason==revoked **或鍵缺席**）→靜默 `8888`、
  不落事件、不重複撤；查無列→`8888`。撤銷語意的權威＝`sys_token.status`，denylist 純加速層、其狀態永不污染稽核帳。
- **FR-008**: denylist TTL MUST 為 **refresh 全壽命**（非 access），且 **kicked／revoked 兩 reason 一律 refresh_secs**（`rev5:R3-8` 已修正 rev4 不對稱）——否則被踢／被撤者於 (access, refresh) 窗內換發時
  denylist 已過期、掉進 reuse 分支回 `8888` 並落假 `session_event(reuse)`。
- **FR-009**: idle 逾時 MUST：門檻＝`refresh_secs − access_secs`（＝N×60；N 於每次簽發〔登入／換發〕讀 `session_idle_timeout` 現值、與該次簽發之 TTL 同源——既有會話最晚於下一次換發採新值、已簽發 token 的 exp 不變＝clarify 總則）、僅 last_activity 可讀時判；命中→`idle-emitted:{sid}` SET NX 冪等守門、僅首次落 `session_event(idle)`→`8888`；
  idle 命中 MUST NOT 寫 denylist（不變式 `access_TTL ≤ N×30 < N×60` ⇒ idle 觸發時 access 必已過期）。
- **FR-010**: logout MUST 冪等：驗 refresh 成功→撤該會話（列轉 revoked＋denylist）＋落 `session_event(logout, created_by=本人)`→`0000`；驗章失敗（垃圾／過期）→仍 `0000` no-op、不落事件、
  ★絕不 `8888`（回異碼＝token 有效性 oracle）。
- **FR-011**: enforce middleware MUST：驗 access→denylist 查→放行後推進 last_activity；redis 故障退 PG `has_active_in_chain`（無 active→`8888` fail-closed）；PG 亦故障→視為無 active、絕不盲放。
  Public 路由不掛本 middleware（「Public 不查 denylist／refresh 不推進 idle-clock」天然成立）；單一判定進入點守恆（002 既定）不變。
- **FR-012**: 五座行為島的降級方向 MUST 落實並隨 §I.7 入憲：denylist fail-closed／idle fail-open／grace fail-secure／captcha 兩層（整體不可用→要求停用 fail-open；單次標記瞬斷→拒但不罰）／
  節流設定鍵缺失**或矛盾組合**退常數＋告警（與 idle 鍵缺失 fail-loud 刻意相反；矛盾組合＝clarify 定案）；兩處刻意的方向不一致 MUST 在 Amendment 條文與 data-model 逐條寫明理由。`session_event.source_ip` 為 varchar(45)
  （與 `sys_login_attempt.real_ip` 的 INET 不同、寫入不共 helper）；event_type／reason 字面沿 rev5（kicked／reuse／idle／logout；reason=single_session／idle_timeout 等）。

**登入節流（帳號維）**

- **FR-013**: 節流三區 MUST：失敗 <captcha_after 自由／[captcha_after, max_fails) 回 `2222 biz.auth.captchaRequired`／≥max_fails 回 `2222 biz.auth.locked`（seed 2／5）；
  後兩者 MUST 在密碼驗章之前擋下、不落稽核列、不消耗計數桶（構造上零 record_attempt——落列則鎖可被週期性探測無限延長）。
- **FR-014**: 節流權威源 MUST 為 `sys_login_attempt` 滑動窗（GREATEST 三源下界：窗起點／窗內最近成功／unlock marker——reset-on-success 由查詢形免費兌現、MUST 逐字帶入不得簡化；
  子查詢必帶窗下界、防全歷史回掃）；redis 為 L1 負快取（命中不續期；lock key 唯一寫入點＝同一次新鮮 L2 讀）；設定鍵讀不到→退活書常數＋一筆 `degraded=settings_default` 告警。
  ★unlock marker 在本刀**無寫入者**（管理員解鎖端點屬後續刀）：SQL 參數位保留、綁 NULL、`GREATEST` 非 strict 自然退化為兩源、MUST NOT 用 sentinel 值；`precheck` 完全不讀 redis unlock marker
  （`rev5:R3-17`：無寫入者、讀了恆 nil）；「該源恆 NULL」列為已知態、不得據此宣稱三源皆已驗。
- **FR-015**: 節流實作 MUST 老實記為 **login 專用**（本刀唯一消費者）、不宣稱通用 seam；per-IP 維本刀不做（`request_context` 留原樣轉錄欄、信任判定屬 004 ip-trust-anchor）。
  BL-00031 之 `login_throttle_captcha_after ≤ login_throttle_max_fails` 不變式由本刀消費側定方向與拒因（clarify 2026-09-08 定案）：讀入時矛盾組合視同設定不可用→退活書常數＋`degraded=settings_invalid` 告警（每次載入至多一筆）；
  002 寫端零改動；`ip_*`／`password_*` 兩對留 004 ip-trust-anchor／007 user-password-admin，收刀時改 BL-00031 條文刪去 003 那一段、條目不刪列。

**圖形驗證碼**

- **FR-016**: captcha MUST 為無狀態簽題 `CaptchaClaims{nonce, user_name, exp, ans_mac}`（HS256、第三把秘鑰 `APP_CAPTCHA_SECRET`、compose 已接）；`ans_mac = hex(SHA256(secret ‖ nonce ‖ lower(answer)))`
  ——秘鑰參與雜湊故答案不可離線還原；challenge 綁 user_name；驗題在 redis 標記 nonce used（SET NX、寫入**先於**答案比對＝提交即消耗）。**redis 降級分兩層、方向相反**：
  ①整體不可用→整個軟區 captcha 要求停用、直接續驗密碼（密碼錯仍照常計數）②連得上但單次 SET NX 瞬斷→拒但零計數不罰。★captcha 缺／錯／過期／重放一律 `2222 biz.auth.captchaRequired`
  且零稽核列零計數桶；題目有效期＝**300 秒**（`CaptchaClaims.exp` 與 nonce-used 標記 TTL 同值）。
- **FR-017**: captcha 字元集 MUST 為 34 字（小寫 a-z 去 `o`＋數字去 `0`）、題長 4（34⁴≥10⁶）；`CaptchaClaims` 四欄、不設 `ctx`（單語境）。答對但登入失敗時前端自動換題。
- **FR-018**: request_context MUST 自空結構加 `real_ip`／`x_forwarded_for`／`ip_confidence` **原樣轉錄**欄（零信任判定——handler 一律經此型取請求事實、絕不自讀轉發標頭；
  004 ip-trust-anchor 接手只換 `real_ip` 推導、欄與寫入點不動）；`real_ip`＝nginx 注入的 X-Real-IP（INET NOT NULL）、`ip_confidence`＝`nginx_peer`、`x_forwarded_for` 截斷 1024＋剝 CR/LF 後存。

**dynamic 選單與路由**

- **FR-019**: getUserRoutes MUST 回 `UserRoute{routes[], home}`：routes＝DB-fresh roles→Casbin `menu` 維度過濾→sys_menu 樹（祖先包含、同層 order→id 升冪）；`MenuRoute.id` 為字串；
  欄位映射（icon_type 拆 icon／localIcon、title 恆存、其餘欄 optional）；`home` 之多角色收斂律＝**啟用角色（status=1）依 role id 升冪、取首個非空 `role_home`；全空→預設 `home`**，
  選出後再經兜底解析（驗 home 屬可見樹可導航葉、不屬→先序第一可導航頁——否則「登入落 404」復活）；★三 seed 角色 role_home 同值＝機器測不出分歧，收斂律 MUST 由碼註釘住＋一支合成多角色測試守。
  demo menu 仍全集在 seed、不啟用 `hideInMenu` 治理（憲法 §I.2）。
- **FR-020**: getConstantRoutes MUST 濾 `sys_menu.constant = TRUE`（★勿寫 IS NOT FALSE——constant 允許 NULL）組樹；seed `constant=TRUE` 為 0 列故現回 `[]`；前端 constant routes 接線 MUST **合併**
  （`[...staticRoute.constantRoutes, ...data]`、Map 按 name 收斂後端同名可覆寫）而非取代——取代會清空 5 條 builtin 常量路由。
- **FR-021**: isRouteExist（GET／Authed）MUST 回傳路由存在性判定。dynamic 模式下前端三處硬閘（initConstantRoute／initAuthRoute／getIsAuthRouteExist）方會呼叫本組 route 端點；
  故 `.env` MUST 翻 `VITE_AUTH_ROUTE_MODE=dynamic`（FR-028；兌現憲法 §II #2 與 ADR-00003 註 4）。

**替代登入誠實 stub**

- **FR-022**: 四替代登入端點（sendCaptcha／codeLogin／register／resetPwd）MUST 共用一支 `not_supported_stub()`、恆回 `2222 biz.auth.notSupported`；四支同形 stub 之 contract case MUST 有區別手法
  （防殭屍 case）；前端三張表單（code-login／register／reset-pwd）各改打 stub wrapper（消滅假成功 toast）、表單與入口原樣保留；captcha hook 改打 `/auth/sendCaptcha` stub、移除假延遲與假成功。

**錯誤處理與碼表（憲法 §I.3、ADR-00023）**

- **FR-023**: `AppError` MUST 由 6→9 變體（加 `LoginFailed` 1000／`TokenExpired` 3333／`ModalLogout` 7777；`Biz(Cow)` 既有故三新 Biz 構造點不需新變體）。碼表終形＝9 可發＋4 保留
  （7778／8889／9998／9999）＝13；`error.rs` 矩陣斷言（`MatrixRow` 補三列 sample）與型別層全變體窮舉（ADR-00023 雙錨）MUST 同批改對——漏一即編譯紅或恆綠；`MSG_KEYS` 7→13 且名冊測試改斷言十三鍵序固定。
- **FR-024**: 新變體 HTTP 映射 MUST 落 `_ => StatusCode::OK` 臂（1000／2222／3333／7777／8888 皆 HTTP 200）；僅 `4040`→404、`5003`→403。三分碼射程（兌現 ADR-00014 後果段「003 接真 session 時對 3333／8888 分工重定」、
  不翻該 ADR）：`3333` **僅** access exp 過期（前端自動 refresh）；標頭缺席・非 Bearer・簽章不符・已撤銷・refresh 鏈失效→`8888`；被踢→`7777`（modal）——措辭落主 Amendment ADR 後果段＋`error.rs` 碼註＋活書 §8（clarify 候選①）。
  router 既有兩道 fallback（002）對 12 條新 route 自然生效、本刀零新 fallback。

**wire 契約與 i18n（憲法 §I.3、ADR-00017、BL-00030）**

- **FR-025**: msg key MUST：固定變體鍵 `auth.login.failed`（1000）／`auth.token.expired`（3333）／`auth.session.kicked`（7777）；既有 `auth.session.reLogin`（8888）不動、★勿漏列；
  Biz 構造點鍵 `biz.auth.{notSupported,captchaRequired,locked}`（前端 captcha 軟區判斷式拿 msg 字面比對區分兩態、須用此名）。三個 Biz 鍵 MUST 以 `Cow::Borrowed("字面")` 構造——非字面即跨端閘 fail-loud（防恆綠洞）；
  contract 雙向斷言（每條 route 每個錯誤路徑實發 msg ∈ 名冊、名冊每鍵 ≥1 發出點）於全部發出點就位的單元成立。本刀後端實發名冊＝002 既有 7＋本刀 6＝**13 鍵**。
- **FR-026**: i18n 前端轉譯（★`BASE-WEB-I18N-WIRING` 三用途）MUST：(i) request 層 modal content＋showErrorMsg 鏈改走 `translateBackendMsg`（``$t(`backend.${msg}`, msg)`` 原文 fallback、detail 值連帶轉譯）
  ／(ii) `en-us.ts`＋`zh-cn.ts` 各插獨佔一行 `  backend: {` 起的 backend 樹 **13 鍵**（修改型、runtime 生效；簡中譯文以 rev5 為藍本重打字消化）＋新建 `zh-tw.ts` 裸 object 錨點檔 13 鍵
  （不接 runtime、不擴 `LangType`、不註冊 zh-TW 語系＝Q3；繁中譯文之家、跨端閘右源之一；檔頭圈界標記自稱 `BASE-WEB-I18N-WIRING+`、新增型不入名冊＝clarify 候選③）
  ／(iii) `app.d.ts` 只補 `backend` 必填型節（zh-cn 結構同步由必填型節＋`pnpm typecheck` 免費守）。三語譯文字面於 plan 之 contracts 定稿、繁中以 `zh-tw.ts` 為權威。
- **FR-027**: msg key 跨端閘 MUST 以 `tools/` 頂層碼面閘工具落地（BL-00030 觸發、ADR-00017 決定 3 兌現；形＝clarify 2026-09-08 定案、立 ADR）：後端 `MSG_KEYS` ⇔ 三檔各自 backend **子樹**鍵集
  **逐檔雙向全等**比對（backend 子樹為封閉集、不設白名單；ADR-00017「雙向必恆紅」指整本字典、不指子樹）；self-test 一正一反（合成缺鍵／多鍵／檔缺席／非字面 Biz 構造）；
  入 pre-commit 條件段（staged 含 rust-api 或 base-web pin bump、或工具本體即跑）、`tools/bootstrap.sh` 之 `run_tool_test`、README 樹（GT-09）、RUNBOOK §12 碼面閘表（註記列轉工具檔列、GT-12 對賬）。

**前端接線（`.env` ADAPT 軌道）**

- **FR-028**: `.env` 面 MUST 走 §III.1 `BASE-WEB-ADAPT`——**三檔四行**：`.env` 兩行（`VITE_AUTH_ROUTE_MODE` static→dynamic、`VITE_HTTP_PROXY` Y→N）＋`.env.test`／`.env.prod` 各一行
  （`VITE_SERVICE_BASE_URL` 自 apifox mock 改 `/api`；漏改＝test／prod build 打 mock）。四行皆修改型、帶 `# [rev6-inline BASE-WEB-ADAPT 003-auth-session] 原行: …` 標記；
  ★rev6 差異：`.env*` 在 fork-delta-lint 射程內＝機器守得到（rev5 為手寫＋review）。翻 N 後 vite 直連 `/api` 必 404、唯一入口 `http://127.0.0.1:32080`（curl 與瀏覽器鎖同一 origin、一律 127.0.0.1）；
  dev 模式 base URL 解析鏈 plan MUST 實核（候選⑦）。新檔一律 `rev6-` 前綴：`typings/api/rev6-auth.d.ts`（captcha 形）與 `service/api/rev6-auth.ts`（loginCaptcha／logout／四 stub wrapper）。

**憲法 Amendment（MINOR 1.2.0→1.3.0；★ 軌道首開＋§I.7 首批行為島）**

- **FR-029**: Amendment 時點 MUST 為（Q5）：plan 之 research 定形制（★軌道表的機器可解形、島條文骨架）、ADR draft 同期落 feature branch；tasks **首個主線任務**只跑「user 親決→accepted→
  更新憲法 §III.2／§I.7＋bump 1.3.0→generate」、獨立 commit `docs(constitution): amend …`（§V.2）。★硬序：accepted 前不得動任何 base-web **既有檔**。
  plan 之 Constitution Check 第 2／7／9 題填「涉及——授權以 Amendment 先行取得」、GATE 狀態＝條件通過；Complexity Tracking 不填（★軌道與島皆屬循憲法明文機制取得授權、非違規）。
- **FR-030**: §III.2 首批 ★ 軌道 MUST 恰四條八用途：`BASE-WEB-AUTH-WIRING` 三用途（(a) constant routes 合併／(b) 三表單 stub／(c) captcha hook）／`BASE-WEB-LOGIN-CAPTCHA-WIRING` 一用途
  （(i) auth store 簽名＋登入頁軟區接線；(ii) formRules 放寬延改密端點刀）／`BASE-WEB-I18N-WIRING` 三用途（FR-026 (i)(ii)(iii)）／`BASE-WEB-LOGOUT-UX-WIRING` 一用途（(i) 登出前 best-effort 呼 API）。
  範圍欄逐檔列出（硬邊界、名單外一律無授權、處數為估值）；首列落入時哨兵句 MUST 同批移除（哨兵句與資料列並存＝fork-delta-lint die）；名冊斷言隨即對四軌道生效並 MUST 一正一反自證
  （名冊內過／名冊外攔／用途外攔／檔外攔）；修改型標記形＝`[rev6-inline <軌道名>(<用途>) 003-auth-session] 原行: …`。用途 (a) 為必需非選配（seed constant=TRUE 為 0 列、取代清空登入頁）。
- **FR-031**: §I.7 行為島 A～E（token rotation／single-session／denylist 撤銷／idle 逾時／登入失敗節流〔帳號維〕）之不變式與 fail-* 方向 MUST 同筆 MINOR 入憲，以 state-machine 鏡頭寫
  「現態×事件→次態＋副作用」、不寫 CRUD 格子；常數值（30 秒／300 秒／seed 門檻）與欄級細節留活書；島 B 條文含 Q9「單一會話只於登入事件判定；翻轉不影響既有會話」；★跨島總則一句（clarify 2026-09-08）：「每個設定鍵只在其消費事件當下讀現值；已簽發 token 的壽命與已建立會話不追溯」——
  single_session 於登入、idle_timeout 於每次簽發（登入／換發）、節流三鍵於每次登入嘗試；島 E 條文含矛盾組合退常數方向（Q3）；跨島刻意不一致（FR-012 兩處）逐條寫明理由。出處經 ADR provenance 引 `rev5:ADR 0028`。

**依賴與汰換**

- **FR-032**: `AppState` MUST 由兩欄→五欄（clarify 2026-09-08 定案）：`db`／`enforcer` 既有＋`jwt`（簽章設定）／`cache`（`Option`；測試 None＝快取自始缺席、production 恆 Some、boot 建連失敗即 fail-loud panic）／`captcha_secret`；欄型於 plan 之 data-model 定；
  `state.rs`「恰兩欄」封條 MUST 立 ADR 翻案、檔頭拍板註同批改寫、編譯期窮舉解構錨測改為五欄同形。config MUST 新讀六鍵（`APP_JWT_JWT_SECRET`／`APP_JWT_REFRESH_TOKEN_SECRET`／`APP_JWT_ISS`／
  `APP_JWT_AUD`／`APP_REDIS_URL`／`APP_CAPTCHA_SECRET`，compose 皆已接、`_FILE` 形沿 002 `env_or_file`）。六支新依賴（密碼雜湊／jwt／redis 客戶端／產圖／hex／sha2）MUST 走全域版本紀律雙源核對
  （rev5 lockfile 值 vs 官方最新穩定；同值採、分歧問 user）、plan research 記表（候選⑥）；root `Cargo.toml`「不引 argon2」舊拍板 MUST 立 ADR 翻案並改寫註解、`server/Cargo.toml` 依賴清單註解同批改寫。
- **FR-033**: `auth/dev_identity.rs` MUST 整檔汰換、release profile 首次可跑；enforce 之 cfg 分支收斂為真驗章（debug／release 同一驗證器）、`Bearer dev-*` 測試面全清、contract 通則 case（未認證 8888）改以真 token 形；
  單一判定進入點守恆與 002 授權矩陣測試不變。
- **FR-034**: BL-00026 與 BL-00041 MUST 刀內收：①boot 鏈 `ConnectOptions` 帶 `sqlx_logging_level(Debug)`、`log` 釘 0.4.33（lock 現值、零新套件）、同批刪同檔「屬 BACKLOG 候選、002 刀不引 log crate」自陳註解
  （errata 枚舉）；②`test_kit.rs`／`system_settings.rs` 兩處裸前代刀號改 RL-0046 冒號前綴形，**同批**把 GT-05 裸三碼刀號腿的子庫 pin 樹側（`SUB_SCAN` 精判）接上、`tools/docsync/book.py` 該處註解改寫、
  GT-05 自測補子庫腿一正一反。收刀 `backlog_done`。

**觀測面**

- **FR-035**: 本刀的靜默降級與安全事件 MUST 雙軌可觀測——①結構化 tracing warn（帶 target＋欄位）②Prometheus 計數器三支：`throttle_degraded_total`（label `source`：settings_default／settings_invalid／
  db_write／captcha_mark／redis_down 等實有源集）／`denylist_hit_total`（label `redis`｜`pg`）／`throttle_soft_zone_total`（無 label；`captcha_forced` 不計入）；三支 MUST 依 `obs.rs` 既有紀律
  **啟動即顯式註冊 0**（label 值集與發射點同步）；守門走計數器 render 文本比對；rev5 之 HLL 廣度兩支不做。

**治理與工具（RUNBOOK §9c、BL-00037）**

- **FR-036**: 走查基準對賬工具 MUST 自 rev5 依「隨遷工具」紀律整檔搬運至 `tools/` 頂層（承 `rev5:tools/walkthrough-baseline.py`；三面現算＝全部表列數／全部序列 last_value＋is_called／redis DBSIZE＋逐前綴鍵數；
  唯讀：pg 只 SELECT、redis 只 DBSIZE／SCAN）、註解與字串四型失效引用 rev6 化、★只准指向 rev6 dev stack（compose 專案＝倉庫根）、絕不指向 rev5 stack；rc 語意＝0 全等／1 有差／2 環境或結構異常
  （含比對面為空＝假綠）／64 用法錯（候選④）；`snapshot`／`diff`／`test` 三子命令、`<檔>` 必填落 tmp/。它是走查前後對賬工具、不是碼面閘 ⇒ 登記 `tools/docsync/gates.py` 之 `NON_GATE_TOOLS`
  並補 GT-12 自測一正一反（工程判斷 3）；入 `run_tool_test` 名冊、README 樹、RUNBOOK §12 工具鏈速查；RUNBOOK §9c MUST 自指針章改實文（契約：走查前 snapshot→走查→清理〔RAII 還原＋三支 sequence 重設守衛〕→diff rc 0 才算還原；
  清理判準；tmp/ 落點）；MUST 排在首次真登入走查之前（否則 gate2 seed 逐列比對首撞）。
- **FR-037**: BL-00037 兩子項 MUST 同批收：①`test_hook_wiring.py` 之 `HOOK` 常數自單指 pre-commit 改為三支（pre-commit／pre-push／submodule pre-push＋共用 scan-range）＋對應接線斷言、
  pre-commit 之 selftest-docsync 觸發樣式自 `^\.githooks/pre-commit$` 放寬至 `.githooks/**`；②`tools/bootstrap.sh` 呼叫名冊（`run_tool_test` 九支＋docsync 三段＋閘數斷言＋vendored-check）改自 tracked 檔集推導、
  刪任一行即紅自證。收刀 `backlog_done`。
- **FR-038**: ADR MUST 於刀內落地 accepted、一決策一檔、皆帶 rev5 provenance：①主 Amendment（★軌道四條八用途＋島 A～E；draft 於 plan 期）②`AppState` 恰兩欄封條翻案 ③root `Cargo.toml` 不引 argon2 翻案
  ④快速登入鈕已知態（Q4 拍板紀錄；帳由 BL-00049 承載）⑤跨端閘形制＝逐檔雙向全等（clarify 定案；記與 ADR-00017 之射程關係）；收刀 `feature_close` 事件 `adrs` 列全。憲法版本恰 bump 一次（1.3.0）。
- **FR-039**: 帳本時點 MUST 兌現：收刀 `backlog_done`＝BL-00026／BL-00030／BL-00037／BL-00041；BL-00031 條文刪去 003 那一段、只留 004 ip-trust-anchor／007 user-password-admin 兩對（工程判斷 4）；`backlog_add` MUST 列 BL-00043～BL-00049 七條
  （開刀前承載體檢六條＋滯後卷 BL-00049：配號已發、事件未載，七筆 GT-03 在途 WARN 由此消；移卷不需事件、但新配號仍需 backlog_add）＋新記一條 `/auth/error` demo 端點排程錨（承 `rev5:B-053`；觸發＝首個動 demo 頁的前端刀）；NOTES「下一步」specify 起手後改 003 進行中、
  收刀改 004 ip-trust-anchor；活書 MUST 同刀更新（arc42 §5 server 管線 as-built／§6 會話狀態機與登入失敗節流兩情境／§8 API 慣例三分碼與 fork-delta 接線現況／§12 auth 域詞＋「降級（基礎設施）」術語條與既有「降級輪廓」消歧；
  現在式、feature branch 內改；C4-L2 拓樸不變零改）。
- **FR-040**: 收刀 DoD MUST 全綠：`cargo test --workspace -- --test-threads=1`（容器內、全程 serial；redis 測試鍵 uniq 前綴隔離、X-Real-IP 顯式注入）＋contract 16 case（per route＋三分碼矩陣＋msg 名冊雙向＋四 stub 區別手法）
  ＋`pnpm typecheck`＋`fork-delta-lint`（名冊斷言對四軌道生效）＋`wire-schema check`（本刀新增 typings ⇒ base-web 側首次真正觸發、快照重抽）＋跨端閘＋`schema-gate check`（gate2 逐列綠——走查後經還原）
  ＋走查基準 diff rc 0＋`docsync check`／`lint` 零紅＋GT-12 預算內（治理閘 12 不變、碼面閘不計）＋release profile 起得動＋CDP 對照 rev5（22080 vs 32080）三帳號登入／側邊欄／登出／被踢 modal／軟區 captcha 零差異；
  US1～US6 驗收場景全數對應至少一測試案或一演練紀錄（函式名＋案序粒度）。前端執行單元無測試框架、驗收＝typecheck＋兩段 review＋CDP 走查（工程判斷 5、以單元 `CONTEXT` 收窄、不動 RULES）。

**★ 軌道逐處登記（憲法 §III.2 必需三欄：位置＋改動內容＋upstream 衝突風險評估）**

風險判準（可覆算，量測面＝base-web worktree＝upstream `example` tip `8be6f9ba`，量測日 2026-09-08、以 `git log --since` 計檔級 commit 數）：**高**＝近 12 月 ≥5；**中**＝近 12 月 1–4 或近 24 月 ≥5；
**低**＝近 12 月 0 且近 24 月 ≤4。**修改型再 +1 級**（衝突塊必然與 upstream 行交錯）、純新增型不加級。

| 位置（檔案） | 軌道·用途 | 型別 | 改動內容 | 12m／24m | 風險 |
|---|---|---|---|---|---|
| `.env`（2 處） | ADAPT（§III.1、非 ★） | 修改型 | `VITE_AUTH_ROUTE_MODE` static→dynamic；`VITE_HTTP_PROXY` Y→N | 0／3 | 中 |
| `.env.test`（1 處） | ADAPT（非 ★） | 修改型 | `VITE_SERVICE_BASE_URL` apifox mock→`/api` | 0／0 | 中 |
| `.env.prod`（1 處） | ADAPT（非 ★） | 修改型 | 同上（dev／prod 同形） | 0／0 | 中 |
| `src/store/modules/route/index.ts`（1 處） | `BASE-WEB-AUTH-WIRING(a)` | 修改型 | `addConstantRoutes(data)`→併入 static 常量集 | 0／7 | 高 |
| `src/store/modules/auth/index.ts` | `BASE-WEB-LOGIN-CAPTCHA-WIRING(i)` | 修改型 | login 簽名加 captcha 參＋失敗 msg 回傳鏈 | 1／6 | 高 |
| `src/views/_builtin/login/modules/pwd-login.vue` | `BASE-WEB-LOGIN-CAPTCHA-WIRING(i)` | 修改型＋新增型 | 軟區條件渲染塊（新增型圈界）＋提交鏈接線（修改型）；三顆快速登入鈕零 inline | 0／4 | 中 |
| `.../login/modules/code-login.vue`（2 處） | `BASE-WEB-AUTH-WIRING(b)` | 修改型 | import stub wrapper＋消滅假成功 toast | 0／2 | 中 |
| `.../login/modules/register.vue`（2 處） | `BASE-WEB-AUTH-WIRING(b)` | 修改型 | 同上 | 0／2 | 中 |
| `.../login/modules/reset-pwd.vue`（2 處） | `BASE-WEB-AUTH-WIRING(b)` | 修改型 | 同上 | 0／2 | 中 |
| `src/hooks/business/captcha.ts`（約 4 處） | `BASE-WEB-AUTH-WIRING(c)` | 修改型 | 改打 `/auth/sendCaptcha` stub、移除假延遲與假成功 | 0／1 | 中 |
| `.../global-header/components/user-avatar.vue`（約 3 處） | `BASE-WEB-LOGOUT-UX-WIRING(i)` | 修改型 | `onPositiveClick` 改 async＋登出前 best-effort 呼 logout wrapper | 0／0 | 中 |
| `src/service/request/index.ts`（2 處＋1 塊） | `BASE-WEB-I18N-WIRING(i)` | 修改型＋新增型 | modal `content` 與 `showErrorMsg` 鏈改走轉譯（修改型）＋`translateBackendMsg`／`translateDetailValue`（新增型圈界） | 0／3 | 中 |
| `src/typings/app.d.ts`（1 處） | `BASE-WEB-I18N-WIRING(iii)` | 修改型 | `App.I18n.Schema` 補 `backend` 必填型節 | **13／32** | **高** |
| `src/locales/langs/en-us.ts`（1 塊） | `BASE-WEB-I18N-WIRING(ii)` | 新增型 | 插 backend 樹 13 鍵 | **14／37** | **高** |
| `src/locales/langs/zh-cn.ts`（1 塊） | `BASE-WEB-I18N-WIRING(ii)` | 新增型 | 插 backend 樹 13 鍵（簡中） | **15／38** | **高** |
| `src/locales/langs/zh-tw.ts`（新檔） | `BASE-WEB-I18N-WIRING+`（新增型、不入名冊） | 新增型 | 繁中錨點檔 13 鍵、不接 runtime | —— | 低 |

★本表最重要的一件事：i18n 三檔（`app.d.ts`／`en-us.ts`／`zh-cn.ts`）是基線最熱的三個檔（近 12 月各 13–15 commit）——本刀提前吃下該面、代價已知並入帳（rev5 走過同路）。
**rebase 處置**（承憲法 §III「rebase 同步紀律」）：修改型一律以 `原行:` 為基準重放語意並同步更新為 upstream 現行版；純新增型整塊搬移、不與 upstream 行交錯；i18n 三檔另加：rebase 前先比對 upstream 是否已自行新增 `backend` 節或改動 `Schema` 結構，若是則改為對齊而非疊加。
★逐處明細（精確行號與 `原行:` 逐字）由實作期各任務的 fork-delta 標記逐處落地並受 `fork-delta-lint` 機器強制（全 repo grep `rev6-inline` 即得完整 patch set）；本表為檔級風險評估與 rebase 處置索引。

### Key Entities *(include if feature involves data)*

- **sys_token**（會話憑證狀態機、001 基線 9 欄、變體 C）：id／created_at／created_by（擁有者 uid）／status（active｜rotated｜revoked）／token_hash（SHA-256、UNIQUE）／rotation_chain（＝sid＝會話身分）／
  issued_at／expires_at／used_at；partial UNIQUE `uq_sys_token_chain_active` 保證同鏈至多一 active；**無 last_activity 欄**（idle 依賴 redis）。
- **session_event**（append-only 稽核、001 基線 8 欄、變體 B）：id／created_at／created_by（操作者 uid：kicked＝被踢對象／logout＝本人）／user_id／sid／event_type（kicked／reuse／idle／logout）／reason／source_ip（varchar(45)）。
- **sys_login_attempt**（節流權威、001 基線 11 欄、變體 B）：id／created_at／created_by／success／attempted_user_name／real_ip（INET NOT NULL）／peer_ip／x_forwarded_for／ip_confidence／region／trace_id；帳號維滑動窗計數源。
- **sys_user**（001 基線）：session_policy（varchar(20) default 'inherit'、值域 single｜multi｜inherit 碼層守）／session_id（varchar(36) nullable）；三 seed 帳號密碼皆 argon2id PHC、共用同一 hash。
- **sys_menu → MenuRoute**（dynamic 選單來源）：78 列 seed、constant=TRUE 為 0 列；映射為前端 `MenuRoute`（id 字串／meta 欄 optional）。
- **casbin 政策（seed 現況、本刀不動）**：163 列；menu／button 兩維度以 `get_filtered_policy` 枚舉、enforce 走既有單一判定進入點；後續刀政策列本刀不消費。
- **系統設定五鍵（本刀消費側、只讀）**：`session_idle_timeout`／`single_session_default`（會話面）＋`login_throttle_max_fails`／`login_throttle_captcha_after`／`login_throttle_window_minutes`（節流面）；
  走查驗收期以 002 寫端翻值後 RAII 還原、非 seed 變動（BL-00028 不觸發）。
- **CaptchaClaims**（無狀態簽題、非 DB）：nonce／user_name／exp／ans_mac；HS256 簽於 `APP_CAPTCHA_SECRET`；nonce used 標記住 redis。
- **redis 承載態**（非 DB、fail-* 各異）：denylist（reason=kicked｜revoked、TTL＝refresh 全壽命）／last_activity（idle 時鐘）／rotate-grace（新對 JSON、TTL＝30 秒）／captcha nonce used（SET NX、TTL＝300 秒）／
  節流 L1 負快取／idle-emitted 冪等守門。
- **msg key 名冊（13 鍵）**：後端可發出之 i18n key 全集＝002 七鍵＋本刀六鍵；跨端閘左源；三檔 backend 子樹為右源。
- **★ 軌道名冊（Amendment 後）**：§III.2 四條八用途 ∪ §III.1 三軌道；fork-delta-lint 名冊斷言之權威、逐處登記表為其 spec 面。
- **走查基準檔（tmp/、非 tracked）**：三面快照 JSON（表列數／序列 last_value＋is_called／redis 前綴鍵數）＋taken_at＋schema_version；diff 忽略 taken_at。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 端到端可見——三 seed 帳號分別登入（含三顆快速登入鈕各一次），側邊欄呈現三種不同的角色化選單；getUserInfo 四欄型別逐欄對齊 typings（userId 字串／userName＝nick_name、User 顯 `User01`）；
  CDP 對照 rev5 基準零差異。
- **SC-002**: token rotation 往返——access 過期回 `3333`→自動 refresh 得新對→原請求重放成功；同票兩並發斷言一 rotate 一走 grace 回同一對且不觸 reuse；rotated＋grace miss 才判 reuse；驗章失敗恆 `8888`（紅綠測）。
- **SC-003**: 撤銷矩陣全數正確——logout 後舊 token 得 `8888`（且對垃圾 token 冪等 `0000`）；single-session on 時二次登入使前一條得 `7777`；翻 on 前既有兩條會話翻後皆仍可用（不追溯）；
  被踢者 (access, refresh) 窗內換發仍 `7777`（denylist TTL＝refresh 全壽命、兩 reason 皆 refresh_secs 自證）；redis 缺 denylist 的 revoked 列靜默 `8888` 不落假 reuse；idle 僅首次落事件。
- **SC-004**: 節流三區全數正確——<2 自由／2–4 `captchaRequired`／≥5 `locked`；軟區與鎖定皆驗章前擋、零稽核列零計數桶（連續失敗 N 次〔N＜captcha_after〕後窗內 `success=false` 列數恰為 N；
  軟區拒絕後再數一次列數**不變**）；成功登入重置窗；矛盾設定組合退常數且告警遞增。
- **SC-005**: captcha 全數正確——任意 userName（含不存在）發題、userName 超限 `1000`、產圖失敗 `5000`、答對密碼錯自動換題、答錯不推進鎖定但該題作廢、nonce 重放第二次拒；兩層降級各一案：
  redis 整體不可用→軟區要求停用且密碼錯仍計數／單次標記寫入瞬斷→拒但計數桶不進。
- **SC-006**: dynamic 選單全數正確——getUserRoutes 樹依角色 Casbin 過濾、home 兜底非 404、合成多角色測試守收斂律；getConstantRoutes 濾 constant=TRUE（現 `[]`）、前端合併保留 5 條 builtin 常量路由；零新政策列（複核在案）。
- **SC-007**: 替代登入四流程恆 `2222 biz.auth.notSupported`、三表單無假成功 toast；三檔 backend 子樹鍵集各＝名冊 13 鍵（跨端閘綠）、UI 顯人話（zh-CN 簡中／en-US 英文）、7777 modal 顯人話非裸鍵；
  `zh-tw.ts` 13 鍵在案、`LangType` 未擴、預設語系仍 zh-CN。
- **SC-008**: 碼表與契約自證——碼表 9 可發＋4 保留＝13、矩陣斷言與型別層窮舉雙錨一致；`3333`／`7777` 映射 HTTP 200 自證；contract case 4→16、coverage gate 缺 case／殭屍 case 皆紅（四支同形 stub 有區別手法）；
  `MSG_KEYS` 十三鍵雙向斷言在案；wire 契約快照重抽後裁判全過。
- **SC-009**: 憲法與機器守——Amendment bump 1.3.0（四 ★ 軌道八用途＋島 A～E）、accepted 前 base-web 既有檔零 diff（git 史可證）；fork-delta-lint 名冊斷言四向自證（名冊內過／名冊外攔／用途外攔／檔外攔）
  且哨兵句已移除；`.env` 四行修改型標記機器綠；跨端閘一正一反自證；走查工具 `NON_GATE_TOOLS` 登記＋GT-12 一正一反；hook 接線守衛與 bootstrap 名冊推導各刪一行即紅。
- **SC-010**: 靜默降級變得看得見——三類降級（設定鍵缺失或矛盾退預設／redis 不可用退資料庫／節流軟區命中）各有獨立可量測訊號，服務啟動後即帶基線值（不因「事件尚未發生」而序列缺席）；
  三類各至少一案觸發後訊號遞增可被斷言，降級記錄帶可機器判讀的欄位。
- **SC-011**: DoD 鏈全綠（FR-040）——`cargo test` 容器內 serial 全綠、`pnpm typecheck` 綠、fork-delta-lint／wire-schema／跨端閘／schema 三閘／entity 漂移閘／lint 全量零紅、release profile 起得動、
  手動端到端走查（入口 `http://127.0.0.1:32080`）七項通過、走查後 diff rc 0。
- **SC-012**: 治理帳本結清——ADR 全數 accepted 且 `feature_close.adrs` 列全；`backlog_done` 四條、`backlog_add` 七加一條、BL-00031 條文已改；七筆 GT-03 在途 WARN 歸零；RULES 零改動（RULES-VERSION 不變）；
  治理閘數維持 12；NOTES 下一步指 004 ip-trust-anchor；活書四節現在式更新且「降級（基礎設施）」術語條在案。

## Assumptions

- rev5 為本機可達之唯讀參考庫（工作區同層、凍結 SHA 由 bootstrap 斷言）；rust 應用碼全程重打字消化、註解 rev6 語境重寫、前代出處帶 `rev5:`；走查基準對賬工具依名詞段「隨遷工具」整檔搬運（同 001 搬閘工具之形）；
  rev4→rev5 拍板差異點十七筆（`rev5:003` research R3）全視為已翻案、烤進 implementer prompt 防回歸清單、不得帶回。
- **零 migration＝事實非選擇**（Q2）：三張消費表與 `sys_user` 兩欄、16 鍵 seed 全在 001 基線；BL-00042／BL-00028 皆不觸發；本刀非一次性遷移、Risk／Guard／Rollback 三欄表免附。
- **grace 窗＝30 秒**（承 rev5 clarify；rev4 10 秒小於前端最壞換發間隔約 11 秒）：不變式＝grace 窗 MUST > 前端最壞換發間隔，前端 timeout 若變更須重算。
- **TTL 公式**已升為規範（FR-004 第⑥步逐字載明）；**home 多角色收斂律**沿 rev5 已驗證規則（FR-019）；**captcha 有效期 300 秒、字集 34 字、題長 4**（FR-016／017）；**ip_confidence 字面＝`nginx_peer`**、004 接手時再治理。
- **`AppState` 五欄欄集**（候選⑤、clarify 定案）＝`db`／`enforcer`／`jwt`／`cache`（`Option`、測試 None）／`captcha_secret`；錨測改五欄窮舉同形。
- **六支新依賴釘版**（候選⑥）：rev5 lockfile 值（密碼雜湊 0.5.3／產圖 1.0.0／hex 0.4.3／jwt 10.4.0〔須帶 rust_crypto feature〕／redis 1.3.0／sha2 0.10.9）為雙源之一、官方最新穩定版為另一源；
  同值採、分歧問 user（全域版本紀律）；hex／sha2／log 已在 lock、零新套件。
- **跨端閘形**（候選②、clarify 定案）＝`MSG_KEYS` ⇔ 三檔 backend 子樹逐檔雙向全等、無白名單、Biz 鍵非字面構造即紅；立 ADR（FR-038 ⑤）。
- **`zh-tw.ts` 檔頭圈界標記**（候選③研判預設）＝`// [rev6-inline BASE-WEB-I18N-WIRING+ 003-auth-session] <理由>`、自稱 ★ 軌道名但新增型不入名冊、不佔用途（憲法 §III.2 表外宣告 3）。
- **走查工具 rc 語意**（候選④研判預設）＝0 全等／1 有差／2 環境或結構異常（含空面假綠）／64 用法錯；登記 `NON_GATE_TOOLS`、不掛 pre-commit。
- **三分碼措辭**（候選①研判預設）＝FR-024；ADR-00014 不翻案、措辭落主 Amendment ADR 後果段。
- **dev 模式 base URL 來源**（候選⑦、已實核）＝`vite --mode test` 載 `.env.test` 之 `VITE_SERVICE_BASE_URL`；翻 `VITE_HTTP_PROXY=N` 後 request 層直用該值 ⇒ 四行改法承 rev5、無另一來源。
- **wire fixture**：LoginToken／UserInfo／MenuRoute／UserRoute／ElegantConstRoute 已在 002 快照（TYPINGS_GLOB 全 api 目錄）；真正新增＝captcha 形、靠新檔 `rev6-auth.d.ts` 入快照。
- **seed 密碼**＝明文與 upstream demo 同值、三帳共用同一 PHC（字面見 `docs/ops/reference-src/schema-definition.md`）；single-session 驗收前置＝先以 002 寫端翻 `single_session_default=on`（001 凍結 seed 不可動、驗後 RAII 還原）。
- **登入頁三顆快速登入鈕保留**（Q4）：本刀零 inline、不占軌道用途、UI 對照零差異；已知態＝BL-00049（滯後卷、觸發＝RUNBOOK §16 prod 硬化拍板）；ADR 記拍板（FR-038 ④）。
- **BL-00031 拒因**（clarify 定案）：矛盾組合視同設定不可用、退常數＋告警；不在 002 寫端加驗證。
- **前端零測試框架**（工程判斷 5）：前端執行單元的 TDD 迴圈退化為 `pnpm typecheck`＋兩段 review＋CDP 對照走查，以單元 `CONTEXT` 明文收窄、不動 RULES。
- **Amendment 流程時點**（Q5）：draft 於 plan 期落 feature branch、凍結三步為 tasks 首個主線任務；plan 之 Constitution Check 記授權鏈與硬序、Complexity Tracking 不填。
- **後端模組邊界與 handler 分檔**（brainstorm §3：`handler/auth/` 依端點群拆檔、`cache`／`throttle`／`captcha` 三新模組、facade 六支）為 plan 定案面；spec 只約束行為與圈界能力（允許檔案清單須有圈界力）。
- **nginx 邊緣層限流與 CF 標頭覆寫**已在（波 1 承襲 rev5 終態）、屬 004 ip-trust-anchor 域；本刀零改動、走查與 US4 驗收知其在。
- **實作紀律引用**（非本 spec 新拍板）：rev5 對應碼先讀後寫、重打字消化、註解一律重寫（憲法 §I.5）；rust build／test 容器內全程 serial；每單元 pin bump；review 只讀不寫；redis dev 與測試共用 DB 0＝測試鍵 uniq 前綴隔離。
- **stakeholder 判定承 001／002 前例**：本刀 stakeholder＝admin 後台使用者與 workspace 維護者；spec 中的端點路徑／碼／casbin 座標／★軌道名／閘名稱／工具名係交付物座標（WHAT）與治理設施引用，非實作技術選型（HOW）；
  「容器內 serial」「cargo test 形」等屬憲法與 CLAUDE.md 既定紀律引用；crate 版本號出現係「釘版紀律」交付要求、非本 spec 選型拍板。

### Out of Scope

- **per-IP 節流／信任錨／IP 存取閘**（004 ip-trust-anchor；`ip_*` 三鍵無消費者、request_context 僅留原樣轉錄欄、nginx 邊緣限流不動）。
- **改密／首登強制換密／email-verify／mailer**（007 user-password-admin；`password_*` 八鍵無消費者、`BASE-WEB-LOGIN-CAPTCHA-WIRING(ii)` formRules 放寬延此刀）。
- **no-escalation 本體**（006 authz-governance；其預告失準已由 BL-00048 對沖）。
- **四支管理頁 view**（008 audit-settings-pages；BL-00045 承載）。
- **`/auth/error` demo 端點**：憲法 §I.1「v1 從簡只能是交付排程」⇒ 排程延後、非設計範圍縮減；延後理由＝拍板級衝突（回吐 client 任意 code／msg 撞保留碼 `9999` 三錨與 §I.3「msg 載穩定 key」）、兌現須先走 §I.3 Amendment；
  收刀 `backlog_add` 新記一條（承 `rev5:B-053`、觸發＝首個動 demo 頁的前端刀）；user 可見已知態＝該兩頁按鈕得 `4040`。
- **`LangType` 擴充與 zh-TW 語系註冊、`zh-tw.ts` 標型重構**（前端 UI 刀；`rev5:R3-15`）。
- **自助頁手機驗證從零建頁**（第四流程只 stub；承 `rev5:B-022` 半消化形、rev6 無對應帳＝零承載、隨前端 UI 刀重評）。
- **★MODAL-WIRING／★DEVPROXY-WIRING**：不開（modal 治理隨頁面接線軌道用途承載、DEVPROXY 由 nginx 前置拓樸取代＝憲法 §III.2 表外宣告 2）。
- **IP 維 HLL 廣度計數、`suppressed_breadcrumb`、管理員解鎖端點**（`rev5:R3-3`；解鎖端點隨 007 user-password-admin 或稽核域刀）。
- **redis AOF 持久化**：不開＝已知態（暴險受 status 即權威封頂）；prod 化由 RUNBOOK §16 prod 硬化 ADR 重評。
- **稽核管理頁 x_forwarded_for 渲染轉義**（入庫已截斷剝控制字元；渲染端隨 008 audit-settings-pages）。
- **prod 資產／base-web prod build**：release「可跑」僅指 rust-api profile；base-web 無 prod build target（RUNBOOK §16 承載）。
- **`RULES.md` 改動**：本刀零 RULES 改動（工程判斷 5 以 `CONTEXT` 收窄、RULES-VERSION 不變）；schema 閘表數斷言（ADR-00012 決定 6）留首次加表的刀。
