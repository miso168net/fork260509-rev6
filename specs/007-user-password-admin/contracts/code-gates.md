# Contract — 機器守、治理面與帳本（007 刀）

> 本檔凍結本刀新增或擴充之機器守之施工面、名冊守恆、測試基建與走查還原工具契約、觀測面與 ADR／帳本兌現面。決定本體住 ADR（Amendment＝ADR-00074、包含規則＝ADR-00075、明細通道＝ADR-00076、設密冷卻與改密節流＝ADR-00078、政策壞值告警＝ADR-00079、清單 wire 偏離帳＝ADR-00083、繁中 runtime 與 zh-TW 閘＝ADR-00084、m0003 與走查還原工具遷移帳前置與合成＝ADR-00085 等），本檔只寫施工；理由與替代案見 research（R13、R15、R16、R17、R19），端點行為見 `contracts/wire-user-admin.md`／`contracts/wire-user-center.md`，鍵名見 `contracts/msg-keys.md`。
> 基線座標：base-web 本刀起點 pin `fb4dac2`（upstream `example` 基線 `8be6f9ba`）、rust-api pin `6f74d20`、憲法 1.7.1→1.8.0（收刀前 PATCH 實數化後 1.8.x＝§8.1）。本檔以描述指稱單元並附 research R23 之單元號（U0～U23；派發真源＝tasks，tasks 改號時以 tasks 為準）。

## §1 fork-delta：管理頁軌道新用途 (v)～(viii)、LOGIN-CAPTCHA (ii)、I18N (i) 改寫與 (iii) 開立

### 1.1 授權來源與硬序

- 授權來源＝U0 之 Amendment（ADR-00074 決定款）：`★BASE-WEB-MANAGE-PAGE-WIRING` 新開 (v) 使用者管理頁、(vi) 個人中心改密卡、(vii) IP 規則頁來源 IP 解鎖入口、(viii) 角色與選單頁按鈕碼顯隱；`★BASE-WEB-LOGIN-CAPTCHA-WIRING` (ii) 開立；`★BASE-WEB-I18N-WIRING` (i) 改寫（明細通道）、(iii) 開立（語系型別擴 `zh-TW`、三處註冊、`zh-tw.ts` 標型、預設 zh-TW）。用途號、範圍欄注記值與 (vii) 之 i18n 鍵落點依 U0 親決；本節依建議形書寫——(vii) 之 page 鍵與型節以巢狀 (vii) 新增型圈界一塊（`en-us`／`zh-cn` 兩檔 locale 與 `app.d.ts` 各 1）落 MANAGE (i) 列既有 `page.manage.ipRule` 圈界塊內（(i) 塊首尾與理由句不動＝research R18 決定 6）；U0 取之非建議項於本節之連動（T-a②：「兩語 locale」簡稱改兩檔明寫＝憲法 1.8.0 同形）已於 T003 同批改。
- ★硬閘（spec FR-055⑤／SC-012）：Amendment 顆落地前 base-web 既有檔零 diff。機器斷言（U0 出口與收刀前承載體檢單元各一次）：`git ls-tree <Amendment 顆> base-web` 之 gitlink＝`fb4dac2`。純新增檔依表外宣告 3 不受此閘，本刀單元序亦使其落在 Amendment 之後。
- Amendment 顆落地前主線親跑 `python3 tools/fork-delta-lint.py` rc 0（新列入名冊、範圍欄注記無 rc 2；輸出之對賬項數與跳過項數入 commit 訊息）與 `python3 tools/route-artifact-gate.py check` rc 0（base-web 容器在場；該工具 `TRACK, PURPOSE` 寫死只讀 (i) 列、新列不干擾其產物檔組；具名跳過不算驗收）。
- ★範圍欄注記數量段為閉集（`tools/fork-delta-lint.py` 之 `classify_range_note`）：「N 處，修改型」／「各 N 處，修改型」／「N 處修改型＋M 塊新增型」／「N 塊，新增型」／「各 N 塊，新增型」，可冠「預估」或「各預估」，或注記含「不預估」。`rev5:` 憲法 (v)(vi) 列之「（兩支＝修改型，逐行 原行:）」類寫法不在閉集＝當場 rc 2；多檔共用一數而未寫「各」亦 rc 2。
- **名冊載入變異自證**（首個觸及 base-web 既有檔之單元順做；ADR-00074 決定款）：§III.2 表中本刀新開或範圍欄改寫之每一列逐列一發——暫把該列範圍欄任一反引號路徑之反引號內字面改為不含 `/` 之 token → `python3 tools/fork-delta-lint.py` 當場 rc 2（`load_roster` 路徑形斷言 die）→ 以存原文寫回（RL-0019）→ `git diff --name-only` 零殘留；逐列單獨跑、不疊加（RL-0005）。
- Amendment 顆同批改寫之現在式面（RL-0011 種子）：I18N (iii) 列「★`LangType` 擴充／locale 註冊／`zh-tw.ts` 標型重構不在本次授權，延前端 UI 刀」、LOGIN-CAPTCHA (i) 列尾「★用途 (ii)（`formRules` 放寬）不在本次授權，延改密端點刀」、MANAGE (i) 列尾「解鎖按鈕與其包裝不在本次授權（使用者管理頁刀）」、(ii)(iii) 列「三鈕不做按鈕碼 gating（門在頁級）」、I18N (i) 列「錯誤信封 `data` 恆 null、無明細通道 ⇒ 不建 `translateDetailValue`」、各列「兩語鍵集 MUST 相等」（改三語）與指稱 upstream 兩檔之「兩語 locale」句（改 `en-us`／`zh-cn` 兩檔明寫；U0 取 T-a②＝表內八處全改、I18N (iii) 列不設定義句＝N-b）。種子字面：「延前端 UI 刀」「延改密端點刀」「使用者管理頁刀」「門在頁級」「兩語」；`pwd-login.vue` 之「★(ii) formRules 放寬不在授權內」碼註不含上列任一詞、另以「(ii) formRules」為種子。

### 1.2 ★ 軌道逐處登記表 19 列之紀律與出口應有值

spec「★ 軌道逐處登記」表 19 列（`src/main.ts` 候選列已於 plan 期刪除——主線定案：根元件驗證器不改、zh-TW 下開發期提示為英文＝已知態；該檔零 diff；#19 碼註列為 plan 期補入、附表尾以免既有編號位移）。現值欄＝`grep -c ' START]' <檔>`／`grep -c '原行:' <檔>`（2026-10-05 現算、base-web `fb4dac2`）；出口應有值＝現值＋ADR-00074 範圍欄所載本刀增量（預估項見通則⑥）。

| # | 檔（`base-web/` 下） | 軌道·用途 | 紀律 | 現值 |
|---|---|---|---|---|
| 1 | `src/views/manage/user/index.vue` | MANAGE (v) 修改型＋新增型 | 清單接真、回收桶切換（已刪模式隱搜尋卡、操作欄換復原、不加刪除時間欄）、列操作下拉（踢除下線、重設密碼、解鎖登入）、七碼 `hasAuth(` 逐鈕；首載改走 `src/service/api/rev6-user-admin.ts` 之包裝（barrel 匯入行改指＝修改型）；`:scroll-x` 改值與表頭兩布林 prop 走通則④；記事欄純文字插值（`tools/view-render-guard.py` 射程內） | 0／0 |
| 2 | `src/views/manage/user/modules/user-operate-drawer.vue` | MANAGE (v) 修改型＋新增型 | 新增與編輯接真；★既有 `path="email"`（對 `userEmail`）與 `path="roles"`（對角色欄）兩處 path 與 model 欄名不符＝同批改正（修改型）；取全部角色之 fetcher＝`src/service/api/rev6-role-admin.ts` 之 `fetchGetAllRoles`（spec FR-053 擇一＝research R18）、改指者帶 `原行:`；狀態與角色只在改動時送、會話政策改動時另打其端點；灰色保留選項、非超管會話政策欄停用＋提示、本人列狀態與角色停用、產密入口 | 0／0 |
| 3 | `src/views/manage/user/modules/user-search.vue` | MANAGE (v) 修改型 | 手機、信箱兩欄拔格式驗證規則；零新增型 | 0／0 |
| 4 | `src/views/user-center/index.vue` | MANAGE (vi) 修改型＋新增型 | `<LookForward />` 佔位改掛改密卡（卡本體為新檔、不入表）；其餘卡位留白 | 0／0 |
| 5 | `src/views/manage/role/index.vue` | MANAGE (viii) 修改型（並觸 (ii) 既有圈界） | 列操作新增／編輯／刪除依 `role:add`／`role:edit`／`role:delete`、表頭新增與批刪走 `showAdd`／`showDelete`；(ii) 既有 6 處修改型＋2 塊新增型不變、本用途標記帶 (viii)；★表頭 `<TableHeaderOperation` 為自閉合開標籤、無自然被替換行（通則④） | 2／6 |
| 6 | `src/views/manage/menu/index.vue` | MANAGE (viii) 修改型 | 新增與新增子選單依 `menu:add`、編輯 `menu:edit`、刪除與批刪 `menu:delete`；表頭兩 prop 現為 (ii) 已加之 rev6 行（`:show-add="!showDeleted"`／`:show-delete="!showDeleted"`）＝於該 rev6 行內併入權限判斷、不增 (viii) 標記（非基線行無 `原行:` 可記）；選單回收桶「復原」鈕不設碼 | 7／16 |
| 7 | `src/views/_builtin/login/modules/pwd-login.vue` | LOGIN-CAPTCHA (ii) 修改型 | 帳號與密碼兩欄 `rules` 只驗必填（修改型）；(i) 既有 2 處＋2 塊不變；三顆快速登入鈕零 inline（BL-00049）；`src/constants/reg.ts` 零 diff（spec FR-050）；碼註改寫依實況描述 `REG_USER_NAME`（漢字、英數、底線、連字號 4～16 字）、不照抄 `rev5:` 碼註之誤述 | 2／2 |
| 8 | `src/service/request/index.ts` | I18N (i) 修改型＋新增型 | 明細轉譯白名單恰兩鍵（`biz.user.passwordPolicy`／`biz.user.pwdSetTooFrequent`；兩字面入 `FRONTEND_MSG_CONSUMERS`＝§2.3）；違規子鍵譯文取 `page.passwordPolicy.violation.<碼>`、分隔取 `page.passwordPolicy.listSeparator`（不落 `backend` 樹＝msg-key-gate 斷言 1 只收 `MSG_KEYS` 成員）；其餘錯誤仍純 key | 2／2 |
| 9 | `src/locales/langs/zh-cn.ts` | (v)(vi)(vii)＋I18N (i)(ii) 新增型 | `page:` 新鍵（`page.manage.user.*`、`page.userCenter.*`、`page.passwordPolicy.*`〔新增型圈界歸 I18N (i)〕、`page.manage.ipRule.unlock.*`〔巢狀 (vii) 圈界一塊、落 MANAGE (i) 既有塊內〕；鍵名見下「page 新鍵名冊」）；`backend` 新 22 鍵落既有 I18N (ii) 塊內、不增塊；★`route:` 樹零新增（`user-center`、`manage_user`、`manage_user-detail`、`manage_ip-rule` 路由標題鍵皆既在）；upstream 既有值一律不改（需改字面＝改用新鍵） | 10／0 |
| 10 | `src/locales/langs/en-us.ts` | 同 #9 | 同 #9（英文）；兩語與繁中三檔鍵集相等由三檔標型 `App.I18n.Schema`＋`pnpm typecheck` 承擔 | 10／0 |
| 11 | `src/typings/app.d.ts` | I18N (iii)＋(i)＋(v)(vi)(vii) 修改型＋新增型 | `type LangType` 增 `'zh-TW'`＝修改型；`Schema.page` 型節 (v)(vi) 與 I18N (i) 之 `passwordPolicy` 為新增型塊；(vii) 型以巢狀 (vii) 圈界一塊落 MANAGE (i) 既有 `manage.ipRule` 型節塊內；`backend` 型節 22 鍵落既有 I18N (iii) 塊內 | 8／0 |
| 12 | `src/locales/locale.ts` | I18N (iii) 新增型 | `import zhTW` 一行＋`'zh-TW': zhTW` 一行＝兩處單行形新增型（範圍欄預估 0 塊）；插於 `'zh-CN'` 項之後、`'en-US'` 項之前（通則②） | 0／0 |
| 13 | `src/locales/naive.ts` | I18N (iii) 新增型 | 另起一行 `import { dateZhTW, zhTW } from 'naive-ui'`（不改既有 import 行＝免修改型）、兩表各插一行（通則②）＝皆單行形新增型（範圍欄預估 0 塊）；lint 擋重複匯入即改「預估 1 處，修改型」並同批改 spec 登記表型別欄（ADR-00074 決定四） | 0／0 |
| 14 | `src/locales/dayjs.ts` | I18N (iii) 修改型＋新增型 | 預設參數與 fallback 之 `'zh-CN'`→`'zh-TW'`＝修改型（範圍欄預估 2 處）；`import 'dayjs/locale/zh-tw'`、`localMap` 插 `'zh-TW': 'zh-tw'`＝單行形新增型（不入計數） | 0／0 |
| 15 | `src/locales/index.ts` | I18N (iii) 修改型＋單行形新增型 | 未選過語言之預設 `'zh-CN'`→`'zh-TW'`（修改型、範圍欄預估 1 處）；`setupI18n` 內首開以現行語言同步 `<html lang>` 一行（單行形新增型、不入計數；ADR-00084 決定 10 甲） | 0／0 |
| 16 | `src/store/modules/app/index.ts` | I18N (iii) 修改型 | 預設 `'zh-CN'`→`'zh-TW'`、`label: '中文'`→`'简体中文'`＝修改型；插入之 `{ label: '繁體中文', key: 'zh-TW' }` 選項＝單行形新增型（不入範圍欄計數、由活書 08 §8.4 分列）；範圍欄預估 2 處修改型（ADR-00074 決定四） | 0／0 |
| 17 | `src/typings/components.d.ts` | §III 生成檔紀律（不入用途名單） | 預期變動：`src/components/custom/pwd-gen-modal.vue` 經 unplugin 自動註冊之一行宣告＋新用 naive 元件之宣告行；只許工具重算形、與引入之檔同 commit | —— |
| 18 | `src/locales/langs/zh-tw.ts` | I18N (iii)（rev6 自有檔、不入名冊） | 改為 `App.I18n.Schema` 標型之完整全樹（臺灣用語）；檔頭單行標記之軌道名與進場刀名保留、理由句改寫為現在式（「治理錨點孤立檔」「不接 runtime」「延前端 UI 刀」為 RL-0011 種子）；`backend: {` 錨 MUST 仍為檔內首個獨佔一行之命中（msg-key-gate `RE_BACKEND_ANCHOR` 取首個命中）；`tools/zh-tw-lint.py` 射程（§2.1） | `rev6-inline` 恰 1 行 |
| 19 | `src/views/manage/role/modules/role-operate-drawer.vue` | MANAGE (viii)（只觸 (iii) 既有圈界內碼註） | 既有 (iii) 圈界首行碼註改述：三鈕不掛碼之理由改為「其讀寫端點屬封死集、非超管連現況都載不出」（RL-0011「門在頁級」種子）；只動碼註、不增減標記、抽屜三鈕續不設碼（spec FR-048、US4 AS10） | 7／6 |

**通則**（凡觸及上表任一檔之單元）：

1. 修改型逐行 `原行:`（工具常數 `MARKER`）、標記帶本用途號；同檔多用途各帶其號（006 刀 (ii)／(iii) 同檔雙用途先例）。
2. ★新增型插入位置不得落在物件或陣列最末項之後：upstream 檔不帶尾逗號，插在最末項之後即須改該行補逗號＝多出一處修改型（005 刀 research R14 判準）。
3. locale 兩檔之 upstream 既有值不改；`route:` 樹零新增。
4. ★Vue 模板屬性行變體（憲法 §III 修改型變體句；ADR-00063 決定三）：開標籤內改動之標記置於該開標籤正上方、`原行:` 載一條真被替換之基線行；同一開標籤內之新增屬性須與該被替換行同處一個變更塊（其間無未改行）。★無真被替換行之純新增屬性行＝`find_unmarked_additions` 報未圈界（開標籤內放不了註解、上方標記與新增行之間隔著未改行即分塊）——#5 角色頁表頭自閉合開標籤即此形；施工自擇合法形（例：以自閉合 `/>` 為真被替換行，menu 頁 (ii) 先例）並以 `python3 tools/fork-delta-lint.py` rc 0 為準，不得以「未圈界新增屬性行」過關。
5. 新增型逐用途計數字面：`MANAGE-PAGE-WIRING(<用途>)+ 007-user-password-admin START]`；修改型 `MANAGE-PAGE-WIRING(<用途>) 007-user-password-admin]`；LOGIN-CAPTCHA／I18N 同形。複核以 `grep -cF` 逐用途計、不由全檔總數倒推。
6. ★預估項：範圍欄對賬腿跳過（修改型逐三元組、新增型逐檔——同檔任一項預估即整檔新增型跳過；本刀起 #5～#11 之既有實數塊在實數化前一併不入對賬）。各承載單元出口以通則⑤之字面印實數入 commit 訊息；與預估不等者記入收刀前 PATCH 實數化清單（表外宣告 1 例外路徑、延後即登記回填義務），不另停手；任一中途 PATCH Amendment MUST 同顆實數化已落地之預估項。
7. 實數項（非預估、非不預估之三元組與檔）不等＝lint rc 1，當單元即修（補／刪標記或改注記走 PATCH）。

**page 新鍵名冊**（`tools/zh-tw-lint.py` 之 `ADMIN_KICK_KEYS` 與會話用語腿所指之鍵路徑；`contracts/msg-keys.md` 射程外之 page 鍵以本表為承載處。鍵名沿 `rev5:src/locales/langs/zh-cn.ts` 之 `page.manage.user` 同名鍵＝research R18 決定 12；其餘 page 新鍵〔欄名、回收桶、產密浮層等〕由前端單元依同一來源落地、實數以 locale 為準）：

| 用途 | 鍵路徑 | 備註 |
|---|---|---|
| 列操作「踢除下線」鈕 | `page.manage.user.kick` | 入 `ADMIN_KICK_KEYS`；繁中須含「踢除」 |
| 踢除確認句 | `page.manage.user.confirmKick` | 同上 |
| 踢除成功提示 | `page.manage.user.kickSuccess` | 同上 |
| 列操作「重設密碼」鈕、浮層標題、成功提示 | `page.manage.user.resetPwd`、`page.manage.user.resetPwdTitle`（`{userName}` 具名插值）、`page.manage.user.resetPwdSuccess` | —— |
| 列操作「解鎖登入」鈕 | `page.manage.user.unlockLogin` | —— |
| 清單角色欄分隔符 | `page.manage.user.roleSeparator` | 三語各一（`contracts/msg-keys.md` §3.3） |
| IP 規則頁來源 IP 解鎖彈窗 | `page.manage.ipRule.unlock.*` | 巢狀 (vii) 圈界（#9～#11） |

### 1.3 新增型新檔九支（不入表、檔頭一行標記）

| 檔（`base-web/` 下） | 檔頭標記 |
|---|---|
| `src/service/api/rev6-user-admin.ts` | `[rev6-inline BASE-WEB-WRAPPER+ 007-user-password-admin]`（§III.1；路徑落 `S1_NEW_FILE_FACE` 之 `src/service/api/rev6-*.ts`；不入 barrel、消費端直接路徑 import） |
| `src/service/api/rev6-user-center.ts` | 同上 |
| `src/typings/api/rev6-user-admin.d.ts` | `[rev6-inline BASE-WEB-ADAPT+ 007-user-password-admin]`（§III.1；`src/typings/api/`；命名空間 `Api.UserAdmin`） |
| `src/typings/api/rev6-user-center.d.ts` | 同上（`Api.UserCenter`） |
| `src/components/custom/pwd-gen-modal.vue` | `[rev6-inline MANAGE-USER-VIEW+ 007-user-password-admin]` |
| `src/views/manage/user/modules/user-reset-pwd-modal.vue` | 同上 |
| `src/views/manage/ip-rule/modules/ip-unlock-modal.vue` | `[rev6-inline MANAGE-IP-RULE-VIEW+ 007-user-password-admin]` |
| `src/views/user-center/modules/password-card.vue` | `[rev6-inline USER-CENTER-VIEW+ 007-user-password-admin]` |
| `src/hooks/business/pwd-policy.ts` | 同上 |

- 註解引導依檔型：`.vue` 新檔之標記＝首行 `<!-- … -->`、置於 `<script setup>` 之前（`src/views/manage/ip-rule/index.vue` 先例）；`.ts`／`.d.ts` 首行 `//`。`find_new_file_marker` 只認首個實質碼行之前之空白／註解行為檔頭區——標記寫進 `<script setup>` 之後＝缺檔頭標記紅；`new_file_track_issue` 要求軌道名後緊接 `+`——`rev5:` 新檔之 `BASE-WEB-MANAGE-PAGE-WIRING(v)+` 形帶用途後綴即紅、不可沿用。名冊外之名（`MANAGE-USER-VIEW`、`MANAGE-IP-RULE-VIEW`、`USER-CENTER-VIEW`）不做名冊斷言（表外宣告 3）。
- ★新 view 子元件檔名 MUST NOT 為 `index.vue` 或 `[…].vue`：elegant-router 頁檔規則只認此兩形，命名即成新頁＝路由外掛產物重算（違 spec FR-054「路由外掛產物零重算」）且 seed-view-gate 導出集變動。
- IP 規則頁主檔 `src/views/manage/ip-rule/index.vue` 為 rev6 自有檔（upstream 無此路徑）：表頭前綴插槽解鎖鈕之改動不需 ★ 授權、檔頭標記不變；其表頭錨受 `tools/view-render-guard.py` 腿②（§3 該列）。
- `tools/view-render-guard.py` 射程（`src/views/manage/**`）自動涵蓋 `user-reset-pwd-modal.vue` 與 `ip-unlock-modal.vue`；`password-card.vue`（`src/views/user-center/`）、`pwd-gen-modal.vue`、`pwd-policy.ts` 在射程外——三者不渲染使用者可寫之自由文字（只有密碼輸入與 i18n 字面），射程不擴；日後渲染自由文字者同批擴 `SCAN_REL`。

### 1.4 變更檔集機器斷言（檔級硬邊界之機器半邊；base-web 各單元出口＋收刀全量閘復跑）

- `git -C base-web diff --name-only --diff-filter=M fb4dac2..HEAD` ⊆ §1.2 之 #1～#17、#19 ∪ {upstream `example` 基線 `8be6f9ba` 不存在之檔}（後者以 `git -C fork260509-soybean-admin-base cat-file -e 8be6f9ba:<路徑>` rc 非 0 判；`zh-tw.ts`、IP 規則頁各檔屬之）——全集機器可判、不設人工指名之追加集。
- `--diff-filter=A` 恰為 §1.3 九檔；`--diff-filter=DR` 為空。
- 零 diff 斷言（各一行 `git -C base-web diff fb4dac2..HEAD -- <路徑>` 零輸出）：路由外掛產物四檔 `src/router/elegant/{imports,routes,transform}.ts`＋`src/typings/elegant-router.d.ts`（spec FR-054）；`src/constants/reg.ts`（FR-050）；`src/main.ts`（plan 期主線定案）；`src/views/manage/user-detail/[id].vue`（續留佔位、seed-view-gate 對賬）；`src/service/api/index.ts` 與 `src/service/api/system-manage.ts`（BASE-WEB-WRAPPER：不改既有 service 檔）；`src/components/advanced/table-header-operation.vue`（兩布林 prop 已在、零改）；`src/views/plugin/excel/index.vue`（檔級名單外）。
- ★本節斷言一律排在 base-web 子庫 commit（六步序④）之後、外層 commit（⑥）之前跑——`A..HEAD` 形只見已 commit 之改動。
- 修改型標記只出現於授權三元組＝`tools/fork-delta-lint.py` 授權判定腿（名冊外三元組、用途號錯置皆紅）。

### 1.5 新增圈界塊「拔標記必紅」

- 本刀每一新增圈界塊（#1～#16 之本刀新增型塊；單行形新增型以其單行標記為對象）逐塊暫拔 START／END（單行形拔該標記行）→ `python3 tools/fork-delta-lint.py` 報未圈界新增 → 寫回 → `git -C base-web status --porcelain` 回基準（RL-0005）。落既有塊內之補鍵（#9～#11 之 backend 22 鍵）不新增塊、不另做。★巢狀 (vii) 塊（落 MANAGE (i) 既有塊內）不適用本法：拔其標記不觸發未圈界（外層 (i) 塊與之同一 change-block、`find_unmarked_additions` 見塊內有標記即放行）——其機器守＝範圍欄對賬腿之 (vii) 塊數（PATCH 實數化後生效；變異自證併入 §8.3）；承載單元出口以通則⑤字面逐檔計數恰 1 入 commit 訊息。
- 新檔九支各取一支同形自證（`.vue`、`.ts`、`.d.ts` 各一）：暫刪檔頭標記行 → 報缺檔頭標記 → 寫回。
- 塊數多時以暫存腳本逐塊迴圈跑（腳本不入版控、每發單獨寫回後再進下一塊）。

## §2 新閘與新腿

### 2.1 `tools/zh-tw-lint.py`（新碼面閘；ADR-00084；spec FR-052、SC-009、GR5 機器面）

- **定位**：碼面閘（RULES 名詞段；不計入 GT-12 治理閘預算）、stdlib-only、連字檔名 CLI。非隨遷工具、亦無 `rev5:` 對應檔＝RL-0076 不適用（`python3 tools/comment-overlap.py tools/zh-tw-lint.py` 會因全 n/a 回 rc 2，不作交付門檻）。
- **子命令**：`check`（預設）／`test`（離線合成 fixtures、零 docker）；`check` 讀固定路徑（`base-web/src/locales/langs/zh-tw.ts`；完備腿另讀 `zh-cn.ts`）、不收路徑引數；`check` 不連帶跑自測（ADR-00084 決定 7）；用法錯 rc 64。
- **掃描面**：`zh-tw.ts` 剝註解（`//`、`/* */`）後之字串字面值（單引號、雙引號、不含 `${…}` 之反引號）；完備腿另讀 `zh-cn.ts` 之字串值；鍵名不判（皆 ASCII 識別字或路由名）、註解不判（非使用者可見面）。每個命中以「鍵路徑＋行號＋命中字或詞」指名——鍵路徑以 brace 配對自物件根攤平：物件根＝檔內首個 `const <名>(: <型>)? = {` 或 `export default {` 之開括號（兩形皆認、皆缺＝rc 2；現行 `zh-cn.ts`＝`const local: App.I18n.Schema = {…}`＋末行 `export default local;`）。本閘與 `tools/msg-key-gate.py`（以 `backend: {` 錨前最近之未配對 `{` 為外層物件）各持解析、互不共用，各以自測守自身解析。
- **判準四腿＋空值檢查**（判準設計之單一真源＝ADR-00084 決定 7；逐條獨立出列、互不遮蔽）：
  - **腿① 簡體殘字**：`zh-tw.ts` 字串值中屬 `SIMPLIFIED_CHARS`（工具常數：簡化字→正體字對照）之字＝rc 1、附正體建議。codec 判準（CJK 基本區字元可編碼於 `gb2312` 而不可編碼於 `cp950`）只作表值初建之輔助（自兩檔現有用字篩候選、逐字人審後入表）、不作判定；Big5 內之簡繁同形異用字（`于`／`后`／`里`／`台`／`干`／`适` 等）由腿③以詞境承擔。
  - **腿② 字表完備**：`zh-tw.ts` 與 `zh-cn.ts` 字串值所用之 CJK 統一表意文字（含擴充區）每字 MUST 屬 `SIMPLIFIED_CHARS` 之鍵或 `APPROVED_CHARS`（工具常數：已審為正體或繁簡同形之字）；未分類＝rc 1（指名字、首見檔與鍵路徑）；兩表相交＝rc 2（表本身受損）。新譯文之新字由本腿逼出分類；不驗歸類正確（殘餘由表值 diff 審查、AI 逐頁審讀與 user 抽查承接）。
  - **腿③ 大陸用語**：`zh-tw.ts` 字串值含工具常數 `MAINLAND_TERMS`（{大陸用語: 臺灣用語}）任一詞＝rc 1、訊息附建議詞。初版必收詞（承 GR5、活書 12 用語）：`用戶`→`使用者`、`默認`→`預設`、`登錄`→`登入`、`註銷`／`退出登錄`→`登出`、`菜單`→`選單`、`設置`→`設定`、`數據`→`資料`、`信息`→`訊息`／`資訊`、`網絡`→`網路`、`軟件`→`軟體`、`程序`→`程式`、`支持`→`支援`、`激活`→`啟用`、`賬號`→`帳號`、`服務器`→`伺服器`、`緩存`→`快取`、`內存`→`記憶體`、`打印`→`列印`、`導入`→`匯入`、`導出`→`匯出`、`搜索`→`搜尋`、`刷新`→`重新整理`、`創建`→`建立`、`保存`→`儲存`、`郵箱`→`信箱`、`鏈接`→`連結`、`圖標`→`圖示`、`字體`→`字型`、`模塊`→`模組`、`加載`→`載入`、`視頻`→`影片`、`屏幕`／`全屏`→`螢幕`／`全螢幕`、`質量`→`品質`、`于`→`於`、`后台`／`以后`／`之后`／`然后`／`最后`→`後…`、`里面`→`裡面`。全樹詞條於繁中全樹譯文單元（U15）審讀後於本閘單元（U16）定稿；具歧義之詞（例：`文件`、`項目`、`地址`）不入表、由 AI 逐頁審讀承擔。
  - **腿④ 會話用語**（GR2）：「踢」字只准出現於 `ADMIN_KICK_KEYS`（工具常數；初值＝`backend.auth.session.kickedByAdmin`＋§1.2「page 新鍵名冊」之踢除三鍵）；`backend.auth.session.kicked`（單一會話被頂替）之值 MUST 含「頂替」、MUST NOT 含「踢」與「管理員」；`backend.auth.session.kickedByAdmin` 之值 MUST 含「管理員」、不得含「頂替」；`ADMIN_KICK_KEYS` 之 page 鍵 MUST 含「踢除」；全樹不得出現 `踢出`、`踢掉`、`踢下線`、`擠下線`、`擠掉`、`頂掉`（統一為「踢除」「頂替」）。
  - **空值檢查**：`zh-tw.ts` 字串值為空字串＝rc 1（指名鍵路徑；三語 Schema 型別不擋空值＝research R19 決定 6）。
- **具名白名單**：工具常數 `EXEMPT`（逐筆＝鍵路徑×字或詞×理由；只對腿①③生效；不得取自 args／env／讀檔）；豁免項於真檔已不命中（鍵已不存在或值已無該字詞）＝幽靈即紅（RL-0051 形；`tools/seed-view-gate.py` 之 `EXEMPT` 同語意）；項數由自測釘住（增列須同批改自測斷言）。初版預期零筆（語言下拉之 `简体中文` 字面住 `src/store/modules/app/index.ts`、不在本閘射程）。
- **退出碼**：0 綠／1 任一腿命中、空值或白名單幽靈（各項合併列出、逐項指名鍵路徑、行號與字或詞）／2 結構異常（兩檔任一缺席、物件根兩形皆缺或 brace 不配對、零字串字面值＝比對面為空、兩字表相交、白名單項壞形、自測敗）／64 用法錯。tracked 面缺席一律 rc 2、不設具名跳過。
- **自測**（`test`；只用合成 fixtures、零 docker；RL-0080 一正一反、變異打在判準上）：①合成全繁中樹 rc 0 ②值含 `SIMPLIFIED_CHARS` 之字 rc 1 指名鍵路徑 ③簡化字只在註解內 rc 0 ④完備腿：未分類字 rc 1（指名字與首見檔）、兩表相交 rc 2 ⑤腿③命中附建議詞 ⑥白名單抑制腿①③命中、幽靈項 rc 1、項數恆定斷言 ⑦腿④各形（`kicked` 含「踢」、`kicked` 含「管理員」、`kicked` 缺「頂替」、`kickedByAdmin` 缺「管理員」、`ADMIN_KICK_KEYS` 外出現「踢」、全樹出現 `擠下線`）各 rc 1 ⑧空值 rc 1 ⑨空檔或零字面 rc 2、兩檔任一缺席 rc 2 ⑩物件根兩形（`const local: App.I18n.Schema = {` 與 `export default {`）各一綠案、兩形皆缺 rc 2。工具本體變異（存原文寫回、逐發單獨跑）：暫拆完備腿之歸類判斷、暫拆幽靈檢查、暫拆「踢」之歸屬檢查 → 各自測紅 → 寫回；三發後 `git diff --name-only` 零殘留。真檔面（ADR-00084 決定 7 一正一反）：正＝真 repo `check` rc 0（兩檔用字全分類）；反＝於 `zh-tw.ts` 一個字串值暫植一個簡化字 → `check` rc 1 且指名該鍵與字 → 以原檔寫回 → `git -C base-web status --porcelain` 回基準態（RL-0005）。
- **機器面之外**：GR5 之 AI 逐頁審讀紀錄與 user 抽查屬 CDP 三方對照單元（U22）承載、不入本閘；三語鍵集相等由三檔標型＋`pnpm typecheck` 承擔、本閘不重做。
- **接線**（同一單元、同一顆外層 commit；`tools/seed-view-gate.py` 進場形照之）：

| 面 | 施工 |
|---|---|
| `.githooks/pre-commit` 條件段 | 新段標籤 `zh-tw-lint`：觸發 `-e 'base-web' -e 'tools/zh-tw-lint.py'`、命令 `python3 "$HOOK_DIR/../tools/zh-tw-lint.py" check`、段內零條件判斷；段位＝seed-view-gate 段之後、submodule-sync 段之前；★`zh-tw.ts` 住子庫、外層 staged 清單只見 gitlink `base-web`＝以 pin bump 觸發，不寫子庫檔路徑字面；碼面閘段首句「七支碼面閘」與其名列同改 |
| `for t in …` 自測迴圈 | 加 `tools/zh-tw-lint.py`（`check_hook_wiring` 強制碼面閘表全員入迴圈） |
| `tools/docsync/tests/test_hook_wiring.py` | `SEGMENTS` 增一元組（標籤、兩觸發字面、命令字面同上）；`MIRROR_WORDS` 增 `"zh-tw-lint": "zh-tw-lint"`；`MIRRORS` 三處人寫鏡像行（pre-commit 檔頭段序行、README `.githooks/` 行、README 守門條目）各補字樣恰一次；模組 docstring「十三條件段」與其段名列舉同改 |
| `tools/bootstrap.sh` | 自測名冊由 tracked 檔推導、不加行；名冊註解「七支碼面閘（…）」與其列名括號同改 |
| `docs/ops/RUNBOOK.md` §12 | 工具鏈速查表一列＋碼面閘表一列（觸發時機欄尾標讀面型：(a) 閘面內——`base-web/src/locales/langs` 在 pre-commit submodule-sync 段之 base-web 閘面內、延後至下次 base-web pin bump 補抓；根據 ADR＝ADR-00084）——GT-12 腿雙向對賬（`tools/` 頂層 tracked `*.py` − `NON_GATE_TOOLS` ⇔ 表首欄） |
| README 工具樹 | 一行（GT-09 對賬） |
| 活書 05 建構塊視圖 `tools/` 列 | 補一項 |
| 活書 12 詞彙表 | 「頂替」「踢除」兩條之機器守指針＝本工具 `ADMIN_KICK_KEYS`／`MAINLAND_TERMS`（用語表之家＝工具常數、活書只指、不鏡像） |
| `docs/ops/reference-src/code-gate-contracts.md` | 新增 §8：行為契約（掃描面、四腿與空值檢查、白名單與幽靈語意、退出碼、讀面型）；接線落點不收（ADR-00041 決定 2） |

- **RL-0011 種子**：「七支碼面閘」（`.githooks/pre-commit` 碼面閘段首句、`tools/bootstrap.sh` 名冊註解）、「十三條件段」（`test_hook_wiring.py` 模組 docstring）；處數以 `python3 tools/docsync errata <詞>`（含兩子庫 pin 樹）現量、tasks 不寫死。
- **時序**：繁中全樹譯文單元（U15）之後、首個觸及 locale 之前端頁面單元（U17）之前；ADR-00084 已於 U0 accepted（RUNBOOK §12「根據 ADR」欄只收 accepted 號）。
- **ADR-00032 翻案觸發器①複核**（碼面閘 ≥8 支＝另立生成檔並翻案）：本刀前碼面閘表 9 支即已成立而未處置、本刀後 10 支；複核狀態載 ADR-00084、處置轉 BL-00142（另立生成檔並翻案 ADR-00032，或立新 ADR 續行人寫表並重設觸發條件；`backlog_add` 隨本刀第一筆 events＝§8.2）。

### 2.2 `rust-api/server/tests/authz_entrypoint_lint.rs` 腿⑦：包含規則呼叫點名冊（ADR-00075；spec FR-022、FR-061）

- **名冊**：`const NO_ESCALATION_CALL_FILES: &[&str] = &["handler/throttle.rs", "handler/user.rs"];`（相對 `src/`、路徑字典序）。受檢形＝`guard_no_escalation` 之完整 token 使用點（共用 `use_lines`：一切出現扣 `fn` 定義處，涵蓋 RL-0026 三形聯集與分組匯入）；射程＝生產面（切測試模組）；判決＝`verdict`（檔集恰等、兩向皆紅並指名檔與行）。定義處 `handler/user.rs` 同時有八支寫端之呼叫、依使用點計入名冊。
- **主案**：真樹掃描 `verdict(NO_ESCALATION_CALL_FILES, &hits)`；紅訊息附「包含規則由 handler 鎖內單一進入點判、擴列＝新消費點＝ADR-00075 範圍」。
- **植入自證**（RL-0080；真樹記憶體植入、磁碟零寫入）：①名冊外 handler 生產面植一處（例 `handler/role.rs`）→ 紅、實得檔集＝名冊∪植入檔 ②同植於測試模組內 → 不紅 ③真樹原文移除 `handler/throttle.rs` 之呼叫行後走同一管線 → 紅（名冊有而樹上無＝消費點蒸發）。
- **逐處落點**：9 個消費點（八支使用者寫端＋unlockLogin 帳號維）之「各一處」由各消費點負向案承擔（spec FR-025「拆掉判定呼叫 MUST 有測試轉紅」）、本腿不另立逐處判決。
- **同檔連動**：檔頭表與段首「六個側面」→「七個側面」、表增腿⑦列、「六腿主案」段標同改（RL-0011 種子「六個側面」「六腿」）；`scan_surface_is_pinned` 之關鍵檔清單補 `handler/user.rs`、`handler/user_center.rs`、`handler/throttle.rs`、`auth/no_escalation.rs`。
- **時序**：wire／msg 裁判面收口單元（U14；兩名冊檔之呼叫點皆已落地）。

### 2.3 `tools/msg-key-gate.py`：斷言 2 認 `AppError::BizData(`＋`FRONTEND_MSG_CONSUMERS` 擴列（ADR-00076；spec FR-004、FR-051）

- **碼面事實**：現行 `RE_BIZ`（`Biz\s*\(`）與 `RE_BIZ_FNVALUE`（`Biz\b`）皆匹配不到 `BizData`——新變體之構造點對現閘隱形，MUST 同批擴閘。
- **斷言 2 擴**：BizData 構造點＝`AppError::BizData(`／`Self::BizData(`／經 use 匯入之裸 `BizData(`（`::` 與 `(` 之間容空白）；其**首引數**（括號配對內頂層第一個逗號之前）MUST 為 `Cow::Borrowed(字串字面｜msg_key::NAME)`、解出之鍵 ∈ `MSG_KEYS`；第二引數（明細物件）不解析、其鍵集由下列佔位符對賬自明細型定義取。函式值形 `AppError::BizData`／`Self::BizData`（不帶括號、`use` 行除外）＝動態構造紅；`enum AppError` 本體內之變體宣告與 match 樣式不計（同既有判準）；`#[cfg(test)]` 所附項目排除（同既有判準）。
- **★射程守**（spec FR-004「唯二例外」之機器面；分階段四句＝ADR-00076 決定 7）：工具常數 `BIZ_DATA_KEYS`＝{`biz.user.passwordPolicy`→`PasswordPolicyDetail`, `biz.user.pwdSetTooFrequent`→`PwdSetTooFrequentDetail`}（鍵→明細型名）。①BizData 構造點解出之鍵 ⊆ `BIZ_DATA_KEYS`，他鍵 rc 1（明細通道射程擴張而未經 ADR-00076）②`BIZ_DATA_KEYS` ∩ `MSG_KEYS` 之每鍵於生產區恰一處構造點，零處或多處 rc 1（構造點蒸發或分岔）③`BIZ_DATA_KEYS` 中未入 `MSG_KEYS` 之鍵構造點數須為 0，否則 rc 1 ④射程鍵以 `AppError::Biz(` 純 key 形構造＝rc 1（明細靜默消失）。②③隨兩鍵分批入名冊（U8、U10）逐鍵生效——U6～U7 生產區零 BizData 構造點即綠、不另設空比對面 rc 2；既有「Biz 構造點零處＝比對面為空 rc 2」不變。
- **佔位符對賬**（`contracts/msg-keys.md` §5 判準 5；`rev5:B-139` 之機器守）：已入 `MSG_KEYS` 之射程鍵，其明細型之序列化鍵集（解析 `rust-api/server/src/handler/user.rs` 內該名 struct 定義之欄名、依其 `rename_all` 屬性換算；查無該 struct＝rc 2）＝三檔 locale 該鍵譯文之 `{…}` 佔位符集（逐檔）；非攜參鍵之譯文佔位符集為空；不等＝rc 1 指名檔與鍵。
- **斷言 3 擴**：`FRONTEND_MSG_CONSUMERS` 增 `("service/request/index.ts", "biz.user.passwordPolicy")`、`("service/request/index.ts", "biz.user.pwdSetTooFrequent")` 兩項、各 1（＝`contracts/msg-keys.md` §2.4「各恰一處程式碼字面」；實作若異，同批改兩檔；逐項附消費語意＝明細轉譯白名單）；他處以字面比對後端 msg 者同批入冊。違規子鍵 `page.passwordPolicy.*` 之首段 `page` 屬 locale 頂層鍵＝非安全前綴、不入射程。
- **斷言 1**：三檔 backend 子樹與 `MSG_KEYS` 46→68 逐檔雙向全等；`zh-tw.ts` 全樹化後之錨位見 §1.2 #18。
- **自測新案**：BizData 合法常數形／字面形綠；首引數動態（變數、`format!`、`Cow::Owned`）紅；鍵不在名冊紅；鍵在名冊而不在 `BIZ_DATA_KEYS` 紅；已入名冊之射程鍵零構造點紅、兩處紅；未入名冊之射程鍵有構造點紅；射程鍵走 `Biz(` 紅；明細型缺 `rename_all = "camelCase"`（欄 `remaining_seconds` 對 `{remainingSeconds}`）紅、明細型欄名改名紅、查無明細型 rc 2；純 key 鍵譯文含佔位符紅；函式值形紅；變體宣告 `BizData(Cow<'static, str>, serde_json::Value)` 與 match 樣式不計；首引數收界誘餌（第二引數 `serde_json::to_value(…)` 內含逗號與括號不致錯切）；真 repo 左源綠案擴印 BizData 構造點數。真檔變異：暫把判準②之「恰一處」改為「≥0」→ 自測紅 → 寫回；暫拆佔位符對賬之比較 → 自測紅 → 寫回。
- **同批文件面**：工具 docstring；RUNBOOK §12 工具鏈速查表與碼面閘表之 msg-key-gate 兩列（「Biz 構造點守衛」擴為 Biz／BizData 兩變體＋射程守）；`docs/ops/reference-src/code-gate-contracts.md` §5；RL-0011 種子「`FRONTEND_MSG_CONSUMERS` 仍恰 1 項」（006 刀反向確認句）。
- **時序**：斷言 2 擴與 BizData 落地同單元（密碼政策單點單元、U6）；斷言 3 擴與請求層明細轉譯同單元（U20；不同批即該單元之 base-web pin bump 被 pre-commit msg-key-gate 段擋下）。

### 2.4 `tools/schema-gate.py`：seed_add 序號合成（GR9；ADR-00085；spec FR-045）

- **碼面事實**：`apply_seed_entries` 之 seed_add 只追加資料列、不動 setval 行；gate2 逐行比對含序列落值 ⇒ m0003 新增 casbin 列（序號 163→164）而閘不推進即紅。
- **判準**（seed_add 分支、資料列追加之後）：`pk` 恰單欄 `c`，且 normalize 後文本有 `SELECT pg_catalog.setval('public.<表>_<c>_seq', N, B);` 行（`RE_SETVAL`）⇒ 期望已發最大值 M＝N（B＝true）或 N−1（B＝false）；`values[c]` 須為整數（否則 `GateError` rc 2）；`values[c]` > M ⇒ 該行改寫為 `(values[c], true)`；≤ M 不動。`pk` 多欄或無對應 setval 行＝不推進。多筆 seed_add 依 entries 序逐筆推進（取大）；seed_update／seed_delete 不動序列（刪列不回捲序號＝與 PG 行為一致）。runtime-append 收窄表之 seed_add 照舊由 `runtime_seed_empty_findings` 紅。
- **★值字面形**：合成以 `copy_literal` 把登記值轉 COPY 文字格後與 `pg_dump --data-only` 逐列比——登記值 MUST 為 pg_dump COPY 文字形：時間欄 `2026-08-05 00:00:00+00`（非 SQL 字面 `2026-08-05T00:00:00+00:00`）、布林以 JSON `true`／`false`、`sys_menu.buttons`（jsonb）以 PG jsonb 輸出正規形（`{"code": "…", "desc": "…"}`、`", "` 與 `": "` 分隔）；以全新庫套 m0003 後該列之 pg_dump 實文為準、勿手寫推測。
- **自測**：①id 大於期望序號 → 推進、合成綠 ②id＝M＋1 推進、id ≤ M 不動 ③多欄 pk 不推進 ④pk 值非整數 rc 2 ⑤反：拆掉推進 → 合成之 setval 行仍為舊值、與合成實庫 dump 不等＝紅；既有 negative 五類（結構／欄序／seed 值／sequence 落值／假 delta 登記）照綠。
- **真庫變異自證**（spec US6 場景 2、SC-007）：全新庫依序跑 m0001～m0003 → `python3 tools/schema-gate.py check --container <pristine 容器>` rc 0 → 暫拆推進 → rc 1 指名 `casbin_rule_id_seq`（163 對 164）→ 寫回 → rc 0；於 m0003 單元（U4）出口與收刀前 Day-1 第 3 步各跑一次。
- **不動面**：`len(tables) != 14` 斷言維持（基線恆真＝ADR-00087；BL-00047 收）；`doccheck` 之 §9 序列落值對 001 刀基線（`casbin_rule_id_seq` 163）不變（schema-definition 不前進）。
- **同批文件面**：工具 docstring 之 gate2 seed 合成句；`docs/ops/reference-src/schema-gates.md` §2 之「seed 演進同樣合成後才比對」句補序號推進；RUNBOOK §10（`docs/ops/reference-src/schema-definition.md` 檔頭「本檔隨每支帶 migration 的刀前進」句之改寫已於 U0 施工前提顆隨 ADR-00087 accepted 同顆完成〔research R21、R22；tasks T003〕、本單元只復核其現在式；spec FR-045）。
- **時序**：工具單元（U1），早於撰寫 m0003 之單元（U4）。

## §3 既有閘與名冊擴充

| 對象 | 擴充（同單元） |
|---|---|
| `tests/authz_entrypoint_lint.rs` 既有腿 | ①`RELOAD_CALL_FILES` 零擴列（使用者域寫端零授權重載＝ADR-00080；`rev5:` 指派寫端之 reload 為 rev6 已翻之分工、帶回違 RL-0065）；反向確認＝`planting_reload_use_turns_leg_one_red_outside_exempt_faces` 補植 `handler/user.rs`、`handler/user_center.rs` 生產面各一發必紅 ②`DOMAIN_LOCK_CALL_FILES` 不變——`handler/user.rs` 生產面一出現 `enter_menu_domain` 即紅＝「指派寫端不入選單序列化域」（ADR-00043 決定 8 條件②未觸發）之機器面 ③腿⑤後半：`advisory_lock_user` 生產使用點全集擴及 `handler/user.rs`、`handler/user_center.rs`、`handler/throttle.rs`（research R6 第 8 款；連既有 `handler/auth/login.rs` 共四檔）、與 `DOMAIN_WRITE_SIDE_FILES` 交集須仍為空——`model/facade/sys_user_role.rs`、`model/facade/sys_role.rs` 之新寫函式與鎖讀（`replace_roles_of_user`、`find_active_by_id_for_update` 等）生產面零 `advisory_lock_user` token ④腿⑥不變：使用者域零 `casbin_rule` 寫入；★選單刪碼守門（ADR-00086）之受保護按鈕碼查詢 MUST NOT 經 `protected_endpoint_set`（端點維封死集；按鈕維受保護列另查）——否則腿⑥前半檔集或逐處判決紅；m0003 住 migration crate、不在 `src/` 掃描面 |
| `handler/common.rs::each_domain_keeps_its_own_log_literals` | 逐域表加 `user.rs`、`user_center.rs` 兩列（target `security.user`／`security.user_center`、拒寫 `refused = "request_context_absent"`／`endpoint`／`uid` 與本域訊息、本域專屬 `BODY_FALLBACK_MSG`〔行首 `const BODY_FALLBACK_MSG: &str = "…"`、不得與既有各域同字〕）；兩新檔須有行首 `fn operator_from(`、拒寫以 `AppError::Internal` 收尾、body 取用以 `common::json_or_default(` 限定路徑形；`throttle.rs` 列：unlock_login 交易化後拒寫 log 字面若變、同批改該列——★漏列不轉紅（`include_str!` 寫死之元組表）＝靜默缺口、tasks 明列 |
| `handler/ip_rule.rs::production_code_emits_no_degraded_field` | 射程檔集只加 `user_center.rs`（錨＝行首 `fn operator_from(`；改密節流降級一律經 `throttle::warn_degraded`）；`user.rs` 不入＝research R6 第 5 款（其生產區合法承載 `finish_user_write` 之會話面降級腿 `degraded = "ttl_read"`／`"denylist_write"`），該案 doc「射程另含其後進場之寫端域 handler」句同批補排除判準；`user.rs` 拒寫腿之零 degraded 改由 `each_domain_keeps_its_own_log_literals` 對各域拒寫事件加負向斷言（不含 `degraded`）承擔、一正一反；★漏列不轉紅、tasks 明列 |
| `handler/mod.rs` 檔頭 | 「業務 handler 九域」→十一域；宣告行 ASCII 升冪句補 `user`、`user_center`（`throttle` < `user` < `user_center`）；`throttle` 域句補「帳號維套包含規則、交易化」；宣告 `pub mod user;`、`pub mod user_center;` |
| `model/facade/mod.rs` 檔頭 | 「十二支對十二張表」→「十三支對十三張表」（新 `sys_pwd_custody`）；成員 ASCII 升冪句補 `sys_pwd_custody`（`sys_operation_log` < `sys_pwd_custody` < `sys_role`）；錯誤形兩制之歸類句補新 facade；活書 05 同句同批 |
| `model/facade/sys_user.rs::advisory_lock_user`（具型交易機器守） | 簽章收窄為只收 `&DatabaseTransaction`（比照 `enter_menu_domain`）＋模組 doc `no_run` 正面孿生＋`compile_fail`（以 `&sea_orm::DatabaseConnection` 呼叫須編不過）；既有 `advisory_lock_user_blocks_same_uid_and_lets_other_uid_through` 照綠；`handler/auth/login.rs` 呼叫形不變 |
| `error.rs` 名冊與矩陣測 | 變體 9→11（檔頭「變體集恰九」與「BizData／ModalLogoutByAdmin 屬後刀域、不帶」句勘誤）；`MSG_KEYS: [&str; 68]`；`msg_keys_roster_is_pinned_and_unique`、`fixed_variant_keys_are_in_roster`（`auth.session.kickedByAdmin` 屬固定鍵）、`biz_keys_are_in_roster` 同改；13 碼矩陣與 `mapping_methods_align_with_matrix` 之 13 列不動（矩陣以碼為鍵、兩新變體共用 2222／7777、加不進矩陣列）——另立「變體樣本表」（十一變體各一樣本、含 `BizData`／`ModalLogoutByAdmin`）逐變體斷言 `code()`／`key()`／`http()`；`issuable_witness` 之窮舉 match 補 `BizData(_, _) => "2222"`、`ModalLogoutByAdmin => "7777"` 兩臂；`each_issuable_code_builds_error_envelope` 照舊只跑矩陣樣本（BizData 之 data 斷言歸 §4 envelope 表驅動案）；`issuable_nine_and_no_variant_four`（可發碼九、保留碼四）不變 |
| `envelope.rs` 錯誤信封釘案 | §4 |
| ROUTES 釘值（★三處 MUST 同單元＝骨架單元 U3） | `rust-api/server/src/router.rs` 之 `ROUTES_COUNT` 49→61 與 ROUTES doc「現行四十九條」、`routes_block_literal_form_and_pinned_rows`（逐列斷言與斷言訊息之「四十九」）、`policy_endpoints_is_the_policy_projection_in_registration_order` 之 `POLICY_ROUTE_COUNT` 35→45、`Protection` doc 之 Policy／Authed 成員句；外層 `tools/docsync/tests/test_references.py` 之 `TestRoutes::test_real_repo_pinned_rows` 兩份字面表（元組表與渲染行表）各 +12 列與其註解。12 列接表尾、依 `rev5:` ROUTES 表序；case_key 依 rev6 慣例（`/systemManage/<名>`＝名之 kebab 形、`/userCenter/<名>`＝`user-center-` 前綴；兩支 wire 契約端點總表）：`get-user-list`、`get-deleted-users`、`add-user`、`update-user`、`delete-user`、`batch-delete-user`、`restore-user`、`kick-user`、`reset-user-password`、`update-user-session-policy`、`user-center-get-password-policy`、`user-center-change-password`。理由＝pre-commit 只在 staged 含 `tools/docsync/` 時才跑 docsync 自測、不同批即靜默紅（LL-00060）；收尾跑 `python3 -B tools/docsync test`＋`python3 tools/docsync generate`（routes 生成表重算） |
| `rust-api/server/tests/contract.rs` | case registry 恰四十九→六十一（模組 doc 與 `registry` doc 同改）＋覆蓋閘兩向（`coverage_gate_every_route_has_case`／`coverage_gate_every_case_has_route`）＋case_key 綁定；管理面十支各經 policy 驗證函式（形同 `verify_role_menu_policy`）、個人中心兩支經 `verify_authed_unauthenticated_8888` 形；授權態矩陣新建一表（形同 `GOVERNANCE_AUTHZ`；SC-001：Super 十二條皆過授權門、Admin 管理面除 getUserList 外九條 `5003`、個人中心兩條三帳號皆過）；`get-user-list`／`get-deleted-users` 各補分頁五案（缺席、current 逾界、size=0&current=0、壞形、`size=1000` clamp 成 (1, 100)）；msg 名冊雙向（`observed_msgs_are_subset_of_roster_and_non_empty`／`msg_roster_every_key_has_an_emitter`）涵蓋新 22 鍵；`role_and_menu_write_refusals_add_no_context_absent_leg_real_seed` 擴及使用者域寫端與 changePassword（寫端清單 14→23、案名改 `write_refusals_add_no_context_absent_leg_real_seed`、doc 與檔頭「十四支角色／選單／授權寫端」同改＝research R17；spec FR-006「操作者缺席先於一切守門拒寫」之降級計數面）；檔頭「恰二十一案」依收尾現算改寫 |
| ★以「本刀端點未註冊」為前提之既有測試（U3 同單元改植或現算） | ①`handler/role.rs` 之 `super_reads_leave_off_candidate_seed_grants_in_the_table_and_out_of_the_response`（列 68 候選外前提）②`model/facade/sys_casbin_policy.rs` 之 `seed_reads_and_the_seal_set_match_the_seed_facts`（列 68 候選外前提＋端點維讀回 35 鍵／受保護 14 之實數）③`tests/contract.rs` 之 `governance_endpoint_grants_real_seed`（列 68 候選外＋R_SUPER 端點維 seed 列 50／候選外 15）④`tests/contract.rs` 之 `governance_reads_real_seed`（列 2〔getUserList 之 R_ADMIN 列〕候選外＋35／14 與 R_ADMIN 端點維 seed 列恰兩項）。路由註冊後列 68 與列 2 轉入候選集：①～③之候選外前提改植合成探針列（形同 `sys_casbin_policy.rs` 之 ghost-guarded 合成案）、實數改以獨立 SQL 現算（不寫死 45／15 等新值）；定位＝`git -C rust-api grep -n '列 68\|seed 列 2 屬候選外'`（＝spec FR-061 四支） |
| `handler/route.rs` | `SELF_SERVICE_ROUTES: [&str; 1] = ["user-center"]` 之字面釘值案＋兩向案（零選單政策角色仍得自助路由／白名單外路由不受影響；spec FR-039）；檔頭前代歸因勘誤（`rev4:014` 起源、`rev5:007` U4 帶回）與「不帶」句改現在式 |
| `auth/enforce.rs` | 三向分派（`kicked`／`admin_kick`／其餘）之兩處（`enforce_mw` denylist 段與換發 revoked 腿）各配三向案；模組註與 `no_escalation_check` doc 之「本體刀接手只填函式體」類預告句勘誤（BL-00048 兌現連動面；實集以 `git -C rust-api grep -n '本體刀'` 現量）；腿④單一判定進入點不受影響 |
| 名冊釘值案（字面集合） | `cache/mod.rs`：reason 二值互異案擴三值（`REASON_ADMIN_KICK`）、檔頭「兩枚 denylist reason」與「`cpwd:` 前綴、`REASON_ADMIN_KICK`…不帶」句勘誤、檔頭「三常數（`GRACE_TTL_SECS`／`REASON_KICKED`／`REASON_REVOKED`）」句改寫（本刀增 `REASON_ADMIN_KICK` 與 `cpwd:` 前綴常數）；`model/audit.rs` 之 `EXPECTED_LITERALS` 五詞→八詞；`model/facade/session_event.rs` 之 `EVENT_REVOKED` 與五 reason 常數之字面釘值；`model/facade/sys_operation_log.rs` 模組 doc 之寫入者列舉補使用者域寫端與 changePassword |
| `obs.rs`／`throttle/mod.rs` | §7 |
| `tests/wire_schema.rs`／`tests/wire_i64_guard_lint.rs` | §4 |
| `tests/entity_access_lint.rs`／`tests/test_module_tail_lint.rs` | 程式不動：`handler/user.rs`、`handler/user_center.rs`、`auth/no_escalation.rs`、`throttle/change_pwd.rs` 自動入 `entity_access_lint` 掃描面（零 path-root `entity::`）；兩 handler 經上列逐域名冊之 `("<名>.rs"` 形字面入 `test_module_tail_lint` 判準①射程（測試模組 MUST 居檔尾）；`model/facade/sys_pwd_custody.rs` 屬 facade 排除層 |
| `tools/view-render-guard.py` 腿②（IP 規則頁表頭正面錨） | ★碼面事實：判準 (b)「`<TableHeaderOperation` 自閉合」與 spec FR-040「IP 規則頁表頭前綴插槽解鎖鈕」不相容（插槽內容須開閉標籤）；工具 docstring 自載「確需具名插槽（`#prefix`／`#suffix`）時 (b) 須同批改判準」。IP 規則頁解鎖入口單元（U18）同批改 (b)：標籤體內只許具名 `<template #prefix>`／`<template #suffix>` 子節點（及其 `v-slot:` 長形、空白、註解）、任何其他子節點＝default 插槽內容即紅；(a) 兩屬性錨與 (c) 零 `#default`／`v-slot:default` 不變；錨由單檔常數（`ANCHOR_REL`＋`ANCHOR_ATTRS`）擴為具名常數 `ANCHORS`（路徑→兩屬性錨值）四頁——IP 規則頁（錨值不變）與使用者頁隨 U18、角色頁與選單頁隨 U19（U19 前置含 U18：選單頁表頭已含 `#prefix`、須在 (b) 改寫之後）；自測補「具名 prefix 插槽綠」「具名插槽外夾一節點紅」「`#default` 紅」三案＋判準變異（RL-0080）；同批改工具 docstring、README 工具樹、RUNBOOK §12 兩表、`docs/ops/reference-src/code-gate-contracts.md` §3 ①（「錨檔＝工具常數 `ANCHOR_REL`」改指 `ANCHORS`）；`ANCHOR_REL`／`ANCHOR_ATTRS` 入 RL-0011 種子。腿①射程自動涵蓋 §1.3 兩支 manage 下之新 view 檔與 #1～#3（註解內亦不得寫出被禁字面） |
| `tools/route-artifact-gate.py` | 程式不動；不新增 view 頁目錄、子元件檔名守 §1.3 ⇒ 產物零重算；觸及 base-web 之前端單元於 base-web 容器在場下實跑 `check` rc 0（具名跳過不算驗收） |
| `tools/seed-view-gate.py` | 程式不動；views 導出集與 `imports.ts` 不變、`user-detail` 佔位續在；反向確認 ADR-00071 翻案觸發器「首支改 sys_menu component 之 delta migration 須擴讀面」未觸發——m0003 只改列 78 之 `buttons`、不改 component（本閘射程限 m0002＝工具 docstring 明文） |
| `tools/fork-delta-lint.py` | 程式不動；名冊與注記由 Amendment 經 `load_roster`／`load_range_notes` 自動讀入（§1） |
| `tools/rust-fmt-gate.py` | 程式不動；`rust-api/migration/src/m0003_seed_button_governance.rs` 為新寫檔、不在例外②（m0001／m0002 承襲）豁免名冊＝照格式化 |
| `tools/entity-drift-gate.py` | 程式不動；零 DDL＝entity 與快照零漂移 |
| `test_kit::ID_RANGES` 等測試件 | §5 |

- **數量詞與現在式假述種子**：家＝research「R22 as-built 改寫義務」（RL-0011 四形；種子、分布與承載單元以該表為準；處數以 `python3 tools/docsync errata <詞>`〔含兩子庫 pin 樹〕＋施工中 `git -C <子庫> grep -n <詞>`〔工作樹〕現量、tasks 不寫死）。本節只另列屬本檔施工面之種子：「六個側面」「六腿」（authz_entrypoint_lint）、「九域」（handler/mod.rs）、「十二支對十二張表」（facade/mod.rs）、「變體集恰九」（error.rs）、「四十九」「三十五」（router.rs、contract.rs、docsync 釘值測）、「恰二十一案」（contract.rs）、「十三條件段」「七支碼面閘」（§2.1）、「恰十」「十值」「十源」「降級十源」「逐字照抄」（§7）、「三常數」（`cache/mod.rs`）、`ANCHOR_REL`／`ANCHOR_ATTRS`（view-render-guard）、「12 條」（rules.yml 檔頭）、「v3」「四欄」「五表」「九支 `setval`」「只刪不補」「指派對被刪」（§6）。

## §4 wire 裁判面（`rust-api/server/tests/wire_schema.rs`；spec FR-005、FR-008、FR-064）

- **受審名冊**＝`src/typings/api/rev6-user-admin.d.ts` 之 `Api.UserAdmin` 與 `rev6-user-center.d.ts` 之 `Api.UserCenter` 兩節全部 wire 型（實數以抽取為準、型名與欄形依兩支 wire 契約與 data-model §6）；每型一行 `const …_DEF: &str = "Api.UserAdmin.<型>";`、依下列判準入 `AUDITED_READ_DEFS` 或 `AUDITED_REQUEST_DEFS`（兩冊不交）。常數定名＝`USER_`（`Api.UserAdmin`）或 `USER_CENTER_`（`Api.UserCenter`）前綴＋型名蛇形（型名首段已為 `User` 者不重複）＋`_DEF`，不得與既有常數撞名（現行 `UPDATE_REQ_DEF`、`USER_INFO_DEF`、`USER_ROUTE_DEF` 等）——十八型對應見下表。
- **逐型側別**（判準＝該 definition 之主要受裁面：後端序列化輸出＝讀端冊、前端送出形之反序列化落點＝請求端冊、query 型屬請求端冊）：

  | 側 | 型（常數） |
  |---|---|
  | `AUDITED_READ_DEFS`（23→31） | `Api.UserAdmin.UserRecord`（`USER_RECORD_DEF`）、`UserRole`（`USER_ROLE_DEF`）、`KickRes`（`USER_KICK_RES_DEF`）、`SessionPolicy`（`USER_SESSION_POLICY_DEF`）；`Api.UserCenter.PasswordPolicyView`（`USER_CENTER_PASSWORD_POLICY_VIEW_DEF`）、`PasswordPolicyDetail`（`USER_CENTER_PASSWORD_POLICY_DETAIL_DEF`）、`PasswordViolationCode`（`USER_CENTER_PASSWORD_VIOLATION_CODE_DEF`）、`PwdSetTooFrequentDetail`（`USER_CENTER_PWD_SET_TOO_FREQUENT_DETAIL_DEF`） |
  | `AUDITED_REQUEST_DEFS`（23→33） | `Api.UserAdmin.UserListQuery`（`USER_LIST_QUERY_DEF`）、`DeletedUserListQuery`（`USER_DELETED_USER_LIST_QUERY_DEF`）、`AddReq`（`USER_ADD_REQ_DEF`）、`UpdateReq`（`USER_UPDATE_REQ_DEF`）、`UserIdReq`（`USER_ID_REQ_DEF`）、`UserBatchDeleteReq`（`USER_BATCH_DELETE_REQ_DEF`）、`ResetPasswordReq`（`USER_RESET_PASSWORD_REQ_DEF`）、`UpdateSessionPolicyReq`（`USER_UPDATE_SESSION_POLICY_REQ_DEF`）、`UnlockReq`（`USER_UNLOCK_REQ_DEF`）；`Api.UserCenter.ChangePasswordReq`（`USER_CENTER_CHANGE_PASSWORD_REQ_DEF`） |

  - `SessionPolicy`（`'inherit' | 'single' | 'multi'`）兩向使用、擇讀端冊（後端產出點＝`UserRecord.sessionPolicy`；請求面由 `UpdateSessionPolicyReq` 之逐欄簽名經 `$ref` 承載）；★字串字面聯集、非 object ⇒ 入既有「封閉字面聯集型」類 `CLOSED_LITERAL_UNIONS`（值域釘值依字典序 `["inherit", "multi", "single"]`、rust 側三值逐值序列化過裁判、值域外／大小寫異形／非字串判否；006 刀 `ArchivedPolicyDimension` 先例），MUST NOT 以略出名冊或改 object 形迴避。`PasswordViolationCode`（違規碼八枚之字面聯集）同形入該類（值域釘值依字典序、rust 側八常數逐值序列化過裁判）。
- **完備性腿**：`in_role_menu_sections` 前綴謂詞擴及 `Api.UserAdmin.`／`Api.UserCenter.`（其 doc「三節」與 `audited_roster_is_complete_and_present_in_snapshot` doc③同改；快照副本於新兩節各植一支未入冊型、自證逐節指名）——不擴＝新節之型漏審不紅。
- **讀型**：序列化鍵集＝快照 properties 鍵集（表驅動）＋逐型「多帶一欄」反例；`UserRecord`：`roles` 元素恰 {`id`, `roleCode`, `roleName`}（缺 `roleCode` 或 `roleName` 各一反例）、`id` 為字串即紅、時間欄非帶 `+00:00` 之 RFC3339 字串即紅、建立者與更新者 `null` 與字串為正而數值為反；★三重不洩之 wire 面＝任何讀端型帶 `password`／`passwordHash` 類鍵即紅（鍵集全等自然擋、另立一顆具名反例）；`PasswordPolicyView` 恰七鍵、帶冷卻秒數鍵即紅（spec FR-038）；明細信封：`violations` 元素值域外（八枚違規碼之外）紅、`remainingSeconds` 非數值紅。
- **請求型**：逐欄簽名（欄名×required×型別正規形〔含可空性〕）一表釘值＋逐欄反例＋合法形反序列化進 rust DTO；角色集元素非數值紅、`sessionPolicy` 值域外紅；★承載密碼之 DTO（`AddReq`、`ResetPasswordReq`、`ChangePasswordReq` 之 rust 側與既有 `LoginReq`）反序列化後之 `Debug` 輸出不含密碼原文（plan 期主線定案之機器釘＝research R11；島 I5 三重不洩之日誌面）。
- **首屏真串**：getUserList 首屏 query 物件經 qs（版本＝工具釘值）於 base-web 容器內實跑之字面逐欄落點（形同 `ROLE_LIST_FIRST_SCREEN_QUERY` 案；null 欄渲染為 `k=`、rust 落 `Some("")` 須等同不濾）；getDeletedUsers 之首屏真串（形同 `DELETED_MENUS_FIRST_SCREEN_QUERY`）；壞形收斂逐 query 型各一。
- **分頁回應**：不另立 ListRes 型、直裁既有 `Api.Common.PaginatingQueryRecord`（實例化既有泛型）。
- **偏離帳**（ADR-00083；ADR-00044 決定 9 形；spec FR-008）：`DEVIATION_LEDGER` 兩列→三列，新增（比對面專用常數 `UPSTREAM_USER_CMP`＝`Api.SystemManage.User`〔非受審型、不帶 `_DEF` 尾〕, `USER_RECORD_DEF`, 釘值）——兩側獨有欄、必出性差、值型差（含可空性）四類＝`DeviationPin` 四欄（`upstream_only`／`rev6_only`／`required_diff`／`type_diff`）自快照機器導出、字面於首次抽取寫入、此後只隨拍板改。
- **upstream 舊函式之消費面**：使用者頁之首載與刪改一律走 `rev6-user-admin.ts`（§1.2 #1）；機器斷言＝`git -C base-web grep -n 'fetchGetUserList' -- src/views/manage` 之命中只來自 `rev6-user-admin` 匯入（barrel 匯入零命中）。`src/views/plugin/excel/index.vue` 續以 barrel 之 upstream 函式打同一端點（檔級名單外、零 diff）＝殘存消費面（ADR-00083 決定 3；spec FR-008 射程＝使用者管理頁，user 2026-10-05 親決）。
- **`tests/wire_i64_guard_lint.rs`**：`GENERIC_WIRE_TYPES` 不變（仍恰 `envelope.rs::PageRes`／`envelope.rs::Res`）；新 `Serialize` 型之 `i64` 欄（`UserRecord.id`、`UserRole.id`、`KickRes` 之計數若為 `i64`）一律掛 `serialize_i64_number_guarded`；★新 `Serialize` 型 MUST NOT 帶巢狀泛型 i64 欄（例回應回顯 `Vec<i64>` 之角色 id 集）——絆線 `nested_generic_i64_fields_are_out_of_scope` 出現即紅＝改立 newtype 或改回 `UserRole` 物件陣列；純 `Deserialize` 請求型之 `Vec<i64>` 不在射程。
- **`envelope.rs`**（ADR-00076；spec FR-051）：`error_envelope_data_null_not_omitted` 改寫為逐變體表驅動（十一變體：`BizData` 之 `data`＝明細物件、其餘十變體 `data` 恆 null 不省略；欄序 data→code→msg）；錯誤信封出口兩條、分派點唯一（`impl IntoResponse for AppError`：`BizData`→新增 `Res::from_err_with_data`、其餘→既有 `Res::from_err`；`from_err` 對任何變體仍出 data:null＝`contracts/wire-user-center.md` §3.3）；序列化失敗回退 `5000` 信封之釘案不變；模組 doc、`Res` doc、`from_err` doc 與該測試 doc 之「錯誤時 data 必為 null」「唯一錯誤入口」類句改述為「唯一例外＝BizData」，錯誤 data 規則之 002 契約指針改指 ADR-00076（§8.1）。
- **快照**：兩支 `.d.ts` 自動入 `tools/wire-schema.py` 抽取面；`extract`（base-web 容器）重抽 `rust-api/server/tests/fixtures/wire-schema.json` 與 typings 同單元、兩 pin 同一顆外層 commit（wire-schema 段雙側觸發、submodule-sync 段閘面含兩者）；`RESERVED_ROUTE_NAMES` 對賬腿不受影響（零新常量路由）；qs 前提腿不受影響。
- **時序**：兩支 `.d.ts` 隨 wire／msg 裁判面收口單元（U14）落地（`BASE-WEB-ADAPT` 新檔、不待前端單元；006 刀 wire 單元先例）；前端單元（U17、U20）只消費之、改型即同單元重抽快照。

## §5 測試基建（MUST 早於任一寫 seed 帳號或角色指派之寫端單元＝U2 先於 U8～U13；spec FR-057、FR-058、FR-062）

### 5.1 使用者域守衛四件＋回補腿

- **src 側**（`rust-api/server/src/model/facade/test_kit.rs`；形之家＝data-model §10、決定＝research R15 第 1 款）：
  - `UserRowsGuard`（新）：帶界水位形（共同本體 `BandedRows`；表 `sys_user`、序列 `sys_user_id_seq`）——arm 現讀 `COALESCE(max(id) FILTER (WHERE id < SYNTHETIC_UID_FLOOR), 0)` 與序列 `(last_value, is_called)`；Drop 刪 `id >` 水位之列（含 `SYNTHETIC_UID_FLOOR` 以上之合成 uid 列與 arm 前殘列）、再 setval 回 arm 值（RL-0031 現讀、不寫死 `rev5:` 之 `setval 3`）；不回補界下列（寫端只軟刪）、Drop 不刪指派。★`fk_sys_user_role_user` 為 RESTRICT：MUST 宣告在一切會動指派之守衛之前（後宣告者先 drop＝指派先清；與 `RoleMenuDomainRowsGuard` 併用亦然）；反序＝Drop 撞 FK fail-loud（反腿釘）。
  - `SeedUserRestoreGuard`（新）：arm 取 id 集（seed 形傳 `SEED_USER_IDS`）快照全可寫欄＋審計欄（`status`、`nick_name`、`user_gender`、`user_phone`、`user_email`、`user_memo`、`session_policy`、`password`、`updated_at`、`updated_by`、`deleted_at`、`deleted_by`——後兩者＝seed 保護守門被改壞而真軟刪時救得回）；Drop 無條件逐列寫回（冪等）；指派面歸 `UserRoleRowsGuard`、`session_id` 歸 `SessionRowsGuard`。既有 `UserStatusFixture`／`SessionPolicyFixture` 簽章與消費點零改動、可與本守衛疊用（RAII 反序 drop、終態恆為最外層快照）。
  - `PwdCustodyRowsGuard`（新）：arm 記 user_id 名冊（`track(uid)`；含 seed uid 與預期被拒者＝RL-0069）＋`sys_user` 帶界水位；Drop＝`DELETE FROM sys_pwd_custody WHERE user_id = ANY(<名冊>) OR user_id > <水位>`；無快照、無 setval（PK＝`(user_id, created_by)`、無序列；seed 該表零列＝界下列皆殘列、刪即還原）。
  - `UserRoleRowsGuard`（擴兩腿）：arm 另讀 `sys_user` 帶界水位；Drop 序 ①刪「`role_id` > 角色水位」∪「`user_id` > 使用者水位」∪「不在 arm 鍵集」之指派列 ②回補 arm 鍵集中兩維皆落界下之對（`INSERT … ON CONFLICT DO NOTHING`）——★先刪後補；seed 指派被撤（BL-00136 形②之測試面）即補回。
  - `RedisKeysGuard`：以既有 `track` 逐鍵登記改密節流鍵（`track(crate::cache::change_pwd_key(uid))`、先登記再寫；型不改）；會話鍵沿 `track_session(sid)`。
  - 組合序：使用者域寫端之案宣告序＝`OpLogRowsGuard`→`SessionRowsGuard`→`UserRowsGuard`→`PwdCustodyRowsGuard`→`UserRoleRowsGuard`→`SeedUserRestoreGuard`→`RedisKeysGuard`；兼動角色列之案（包含規則案以自建角色植列）另以 `UserRowsGuard` 宣告於 `RoleMenuDomainRowsGuard` 之前（指派→角色先清、使用者列最後）。
- **tests 側**（`rust-api/server/tests/common/mod.rs`；沿 `*WriteGuard` 慣例）：`UserWriteGuard`（`BandedTable` 常數增 `("sys_user", "sys_user_id_seq")`；帶界水位（表, 序列）常數逐字對賬案四組→五組）、`SeedUserWriteGuard`、`PwdCustodyWriteGuard`，既有 `UserRoleWriteGuard`／`UserRoleMarks` 同擴兩腿；改密節流鍵以 `CacheKeysGuard` 逐鍵登記。回補與 setval 語句模板兩側自持時以 `include_str!` 逐字對賬（形同 `self_held_below_band_templates_match_src_verbatim`／`self_held_synthetic_uid_floor_matches_src_verbatim`）。
- **自證**（RL-0080；一律取「自建列代 seed 列」形——直改 seed 列做拆腿或反序變異會令 seed 列留缺於 dev 庫＝違 spec FR-062）：各守衛一正（寫後 Drop 回 arm 態）一反（拆該腿＝自建列殘留而紅）。①嵌套 `UserRowsGuard`：外 arm → nextval 植一列 → 內 arm → 再植一列 → 內 Drop 後只剩外列、序列回內 arm 值 → 外 Drop 清之；變異＝暫拔 setval → 紅 ②`SeedUserRestoreGuard`：以自建帳號 id 集行使同一本體（arm → 以已提交交易改其 `nick_name`、`password`、`status`、`user_memo`、審計欄與軟刪兩欄 → Drop 後逐欄等於 arm 快照；變異＝自寫回欄集暫拔 `password` → 紅），另釘 seed 形 id 集＝`SEED_USER_IDS` ③`UserRoleRowsGuard` 回補腿取嵌套形：外層造帳號與指派、內層 arm 後撤該對並提交、內層 Drop 須補回；另植合成 uid 使用者列與其指派 → Drop 先清指派、`UserRowsGuard` 隨後清列不撞 FK；變異＝暫拔回補步 → 紅、暫拔 user_id 帶界腿 → 使用者列守衛 Drop 撞 FK fail-loud ④`PwdCustodyRowsGuard`：arm（track 自建帳號 uid）→ upsert（該 uid, 合成操作者）→ Drop 後該 uid 之列為零；變異＝暫拔刪除步 → 紅。四發單獨跑、寫回、不疊加（RL-0005）。另立整合測試一支：經寫端改 seed 帳號之指派與欄值後守衛按原值回補（spec SC-008 末句；正向路徑）。

### 5.2 換發 fixture 改造（spec FR-028；換發活性重驗單元 U11）

- `handler/auth/refresh.rs` 斷言換發 `0000` 之十案與 `handler/auth/logout.rs` 以換發為前置之一案：票主改植 `sys_user` 活列（沿既有合成 uid 家族 `9_300_000_1xx`、顯式 id、不觸序列），由 `UserRowsGuard` 清（合成 uid 落界上＝無條件清列）；模組 doc「兩件不搬：鎖內活性重驗」與「票主不必在 `sys_user` 有列」句改寫。另補停用、軟刪、查無列三形拒絕案與「重驗讀位於票列鎖之後、簽發之前」之源碼次序釘。
- 合成 uid 之 `sys_user` 顯式 id 列不入 `test_kit::ID_RANGES`（該表 doc 明載合成 uid 家族不在射程）；跨案重用同 uid 由 `UserRowsGuard` 之「界上恆清」承擔、測試全程 serial。

### 5.3 殘列不連坐與演練（spec FR-058、SC-008）

- 具名排除兩形（seed 帳號角色指派被改＝BL-00136 形②、seed 帳號欄值被改）住 spec 與 RUNBOOK §9c；測試面由 §5.1 回補與寫回承擔、走查面由 §6 承擔。
- **殘列演練**（主線對 dev 庫、逐步取 user 放行＝LL-00053；寫端 API 皆落地後、CDP 之前）：只經 API 對自建帳號產殘列——新增帳號（含初始密碼＝經手表列）、指派自建角色、以錯誤舊密打 changePassword 一次（`cpwd:` 鍵）——psql 只下 SELECT；容器內全量測試全程 serial 全綠（任何轉紅之案＝對自建帳號殘列敏感、同單元改錨或升級）；收尾 `restore`（基準檔模式）→ `diff` rc 0 → `python3 tools/schema-gate.py check` 綠；結果記單元 commit 訊息。
- seed 帳號之帳號資訊投影：`python3 tools/docsync refresh` 之 accounts 快照與凍結 seed 之投影比對含 `nick_name`／`status`——dev 庫留有 seed 帳號欄值殘值或自建帳號時 generate 即紅；Day-1 第 1 步（§8.3）前先以走查還原工具回基準。

### 5.4 號段、共用件與紀律

- `test_kit::ID_RANGES`（現型長 `[IdRange; 29]`）：新測試以顯式 id 造 `sys_role`、`casbin_rule` 等列者先依「表×檔」登記號段、型長同批改；tests 側 `self_held_id_ranges` 逐字對賬同改。
- 交易體內不得留會 panic 之佔位或斷言（LL-00037／LL-00055：持列鎖之連線使守衛 Drop 永等）；判準變異不得拆或繞過真庫清理守衛（LL-00053）；以 cargo 驗改碼或變異寫回後 touch 並以 log 見 `Compiling` 自證重編（RL-0085）；ROUTES 有增列之單元另跑 `python3 -B tools/docsync test`（LL-00060）；base-web 指令一律容器內（LL-00038）；不以 host timeout 包容器內測試（LL-00039）。
- 手寫 `casbin_rule` 列 v3～v5 一律 `''`、比對用 `= ''`（LL-00043）；直種現役政策一律落非 NULL 建立者（006 刀殘列不連坐形①之續行）。

## §6 走查還原工具 v4（`tools/walkthrough-baseline.py`；ADR-00085；spec FR-057、Q21、Q22）

### 6.1 檔形 v4

- `SCHEMA_VERSION` 3→4；v3／v2／v1 舊檔之 `diff`／`restore` rc 2、指名重新 snapshot（v3 以前之檔不載遷移帳、無從判遷移差——訊息明示）。
- 新欄：①`migrations`＝`seaql_migrations.version` 依字典序之有序清單（與其餘欄同一句撈取＝同一快照）②`sys_user_rows`＝`sys_user` 之 `id ≤` 上界列之 `id`＋可變欄——欄名冊 `SYS_USER_MUTABLE_COLUMNS`＝`nick_name`（text?）、`user_gender`（int?）、`user_phone`（text?）、`user_email`（text?）、`status`（int?）、`session_policy`（text）、`user_memo`（text?）、`password`（text）、`updated_at`（ts?）、`updated_by`（int?）、`deleted_at`（ts?）、`deleted_by`（int?），併入 `ROW_FACES`（diff 面名「使用者列」）。
- `BOUNDED_TABLES` 四表→五表：增 `sys_user`（序列 `sys_user_id_seq`）；`id_bounds` 五鍵；`bounds_above_sequence` 前置自動涵蓋。
- `validate_snapshot`／`_check_bound_faces` 同驗新兩欄之形（`migrations` 為非空字串清單、互異；`sys_user_rows` 依欄名冊與欄型）。
- diff 新面：「遷移帳」（逐版本兩向差）、「使用者列」（同 id 逐欄）；★`password` 欄只報「有差」、值以遮蔽字面呈現、不印雜湊原文（島 I5 三重不洩延伸至維運工具輸出）；基準檔本身落 gitignored 工作區、不入版控。

### 6.2 restore 寫面（同一交易、次序固定；自測逐字釘住）

- ①`system_settings`：現況對「凍結 seed ⊕ 演進登記之 `seed_*` 合成」（§6.4）比值——值≠合成值即 rc 2 指名、不自動改值；值等而審計欄非 NULL 者歸 NULL。
- ②清理面各表 DELETE：`RESTORE_TABLES` 五表→六表（增 `sys_pwd_custody`：全表清空；無序列＝不入 setval 名冊）＋`sys_user.session_id` 歸 NULL。
- ③清理面序列 setval（五支、名冊不變）。
- ③b 角色／選單／使用者域：`sys_user_role` 鍵集差刪除 → 五表依名冊序刪 `id >` 上界（`sys_user` 之刪排在指派刪除之後＝FK）→ `casbin_rule` 回補目標列 → ★`sys_user_role` 回補目標鍵集有而現況無之對（`ON CONFLICT DO NOTHING`；排在刪之後）→ `sys_role` 可變欄回寫 → ★`sys_user` 可變欄回寫（`IS DISTINCT FROM` 條件、含 `password`、審計欄與軟刪兩欄：改回值＝改回痕）→ 五支序列 setval 回目標值（基準檔模式合計十支 setval）。
- ④redis：`RESTORE_REDIS_PREFIXES` 增 `cpwd`（`session`／`throttle`／`cpwd` 三前綴逐鍵指名 DEL）；④b 門鈴不變。
- ⑤收尾比對、⑥重啟句不變：`sys_user`／`sys_user_role` 之回補與回寫不需重啟 rust-api（角色每請求自庫現查、帳號活性於登入與換發自庫讀）。
- 安全帶：清理面六表列數或 `session`／`throttle`／`cpwd` 前綴鍵數非 0＝拒跑 rc 2、零寫入；五表不套列數拒跑、套「上界高於序列位置」前置（涵蓋 `sys_user`）。
- ★射程界改述：補回被刪之授權列與指派對、回寫角色列與使用者列可變欄（含軟刪兩欄＝基準內帳號被軟刪即寫回未刪、指派隨回補）；其餘欄之就地改寫與他表 `id ≤` 上界列之被刪不還原。

### 6.3 遷移帳前置（spec FR-057 (a)）

- 基準檔模式之 restore 於任何寫入前撈現庫 `seaql_migrations.version` 有序清單、與基準檔 `migrations` 比：不等＝rc 2、零寫入，訊息逐版本指名「基準有現庫無」／「現庫有基準無」並指示重新 snapshot（舊基準照跑＝反做該遷移之增刪列而不還原其欄值改動、遷移帳仍記已跑＝無工具修路之混合態）。
- `diff` 亦報遷移帳面之差（rc 1）。

### 6.4 演進登記合成（spec FR-057 (b)）

- **合成語意**同 `tools/schema-gate.py` 之 `apply_seed_entries`（docsync 帳號快照投影 `seed_account_projection` 同形先例）：凍結 `specs/001-schema-baseline/fixtures/seed.sql` 之 COPY 列 ⊕ `docs/ops/reference-src/schema-evolution.json` 之 `seed_add`／`seed_update`／`seed_delete`；`seed_update`／`seed_delete` 之 pk 須命中恰一列、`seed_add` 之 `values` 欄集須恰等 COPY 欄集——不符＝rc 2；新列之序號期望同 §2.4（單欄 pk 且有對應序列者推進）。合成實作＝執行期依路徑以 importlib 載入 `tools/schema-gate.py`、取 gate2 期望 seed 之同一合成鏈（`normalize_seed_dump`→`apply_seed_entries`）——不自持第二份合成碼；載入失敗或 `GateError`＝rc 2、原訊息照轉；自測另以 `docsync.snapshot.seed_account_projection` 交叉對賬（合成語意對賬案）。
- **合成射程**：基準檔模式＝`system_settings`；seed 模式＝`system_settings`＋角色／選單域五表（`sys_role`、`sys_menu`、`casbin_rule`、`sys_casbin_policy_archive`、`sys_user_role`）＋`sys_user`。射程外之表有 `seed_*` 登記而工具不觸之（例 `sys_user_email_verify`）＝不影響 restore。
- **repo↔現庫遷移同步前置**：本次模式之合成射程內任一表有 `seed_*` 登記 ⇒ 寫入前比對現庫 `seaql_migrations.version` 集與 repo 之 migration 清單（`rust-api/migration/src/lib.rs` 之 `migrations()` 向量所列模組名；遷移版本名＝檔名主幹＝`DeriveMigrationName`；零解析＝rc 2）；不等＝rc 2、零寫入，訊息指名「repo 有現庫無＝未套用」或「現庫有 repo 無」。
- **清理面照舊拒跑**：seed 模式下清理面六表任一有 `seed_*` 登記＝拒跑 rc 2 指名登記 id（整表清空面以 seed 恆零列為前提）；基準檔模式由安全帶（基準檔清理面列數非 0 即拒）承擔同一邊界。
- `check_seed_evolution` 之拒跑射程由「`system_settings`＋（seed 模式）清理面與角色／選單域」收窄為「（seed 模式）清理面六表」；其餘改走合成。

### 6.5 seed 模式

- 目標態＝凍結 seed ⊕ 合成射程內之演進登記：清理面六表 0 列、`sys_ip_rule_id_seq` 依合成後 setval 行、五表上界＝合成後 COPY 列 id 最大值、五支序列＝合成後 setval 行、指派鍵集、授權列、角色列與使用者列可變欄。m0003 九筆登記後之期望：列 44 不在、列 164 在、列 58～63 `protected` 為真、`casbin_rule_id_seq`＝(164, true)、`casbin_rule` 163 列、`sys_menu` 列 78 不在任何列面（只在上界與序列面）。
- 收尾比對（seed 模式判準面）擴及使用者域（`sys_user` 列數、上界、序列與使用者列可變欄、指派鍵集）。

### 6.6 退出碼增項

- rc 2 增：v3 以前舊檔形；基準檔遷移帳≠現庫；合成射程有登記而 repo↔現庫遷移不同步；合成之 pk 命中≠1 或 values 欄集不符；repo migration 清單零解析；清理面六表有 `seed_*` 登記（seed 模式）。刪：「`system_settings` 有 `seed_*` 演進登記」（改合成）、「角色／選單域五表有 `seed_*` 演進登記」（seed 模式；改合成）。

### 6.7 自測合成案與變異（spec US6 場景 3～7、SC-008）

- ①使用者域回基準（US6-3）：基準＝seed 三帳號、鍵集 [[1,1],[2,2],[3,3]]、經手表 0、`cpwd` 0；現況＝(2, 2) 被刪、新帳號列 id 4 與其指派、seed 帳號 2 之 `nick_name` 與 `password` 被改、經手表一列、`cpwd:4` 一鍵 → restore 寫句逐字＝§6.2 序、收尾 diff rc 0；①b 基準含自建帳號（id 4＋其指派）、現況該帳號被軟刪且指派被刪 → 軟刪兩欄寫回、指派回補、收尾 diff rc 0。
- ②遷移帳前置（US6-4）：v4 基準之 `migrations` 少於現況 → rc 2、零 docker 寫入呼叫、訊息含遷移差與重拍指示；v3 檔 → rc 2 檔形版本訊息。
- ③seed 模式合成（US6-5）：合成登記＝m0003 九筆形、現況已套用並留走查殘列 → 目標態如 §6.5、殘列清除、收尾比對 rc 0。
- ④repo↔現庫不同步（US6-6）：repo 清單含 m0003、現庫未套用、登記在 → seed 模式 rc 2 指名未套用之遷移、零寫入。
- ⑤`system_settings` 合成（US6-7）：登記含 `system_settings` 之增鍵、改值、刪鍵各一且現庫已套用 → 基準檔模式與 seed 模式各一發、值等於合成值者不報差且不拒跑。
- ⑥清理面登記照舊拒跑（含 `sys_pwd_custody`）；⑦合成語意對賬案（§6.4）；⑧password 欄 diff 遮蔽；⑨寫句逐字釘、`STUB_BOUNDED_IDS`、`SEED_RESTORE_TEXT` 之樁擴 `sys_user` 全欄 COPY 與 `sys_pwd_custody` 空 COPY——密碼欄樁值一律非 PHC 形之合成字面（RL-0054；免撞機密樣式掃描）。
- **變異自證**（存原文寫回、逐發單獨跑、`git diff --name-only` 零殘留）：暫拆遷移帳前置呼叫 → ②紅；暫改合成為只讀凍結段 → ③⑤紅；暫拆 repo↔現庫前置 → ④紅；暫拔 `sys_user_role` 回補句 → ①紅。

### 6.8 同批文件面與時序

- **同批**（RL-0011 種子「v3」「四欄」「四表」「五表」「九支 `setval`」「只刪不補」「指派對被刪＝③b 射程外」「未合成演進」「`sys_user` 列數不變但 diff 不報」）：工具 docstring（射程界、退出碼、檔形演進句）；RUNBOOK §9c 第 1 步（v4 新欄、m0003 套用後即重拍）、第 3 步（清理面各表〔本刀起含經手表〕、`cpwd`、③b 使用者域、`system_settings` 左源合成）、第 5 步（射程界與具名排除兩形）與退出碼段；RUNBOOK §12 工具鏈速查表該列；README 工具樹該行；活書 05 同語意句。
- **時序**：工具單元（U1）早於撰寫 m0003 之單元（U4）與 CDP 三方對照單元（U22）。U1 落地後之 v4 基準供 U2～U3 期間演練；m0003 套進 dev 庫（U4 收尾、取 user 放行、重起 stack 由一次性 migrate 服務套用＋重啟 rust-api）後該基準即被 §6.3 拒用＝當場重拍本刀基準（落點依 RUNBOOK §9c）。006 刀終態基準於本刀基準取得後方可清。

## §7 觀測與告警

### 7.1 政策壞值計數與告警（ADR-00079；spec FR-034、BL-00031）

- **計數族**：`password_policy_invalid_total`（無 label）；`obs::pre_register_metrics` 預註冊為 0；發射出口 `obs::password_policy_invalid()`（只計數、不發 log）恰一處呼叫＝`model/password.rs` 之單一驗證件 `validate_against_policy` 判出 min > max 之腿（三設密入口共經；getPasswordPolicy 只經載入件 `load_password_policy`、不經驗證件＝不計；計數語意＝矛盾期間之設密驗證次數、每次設密驗證至多一格；ADR-00079 決定 5）；★MUST NOT 併入 `throttle_degraded_total`（非節流降級）。
- **機器守**：`obs.rs` 測試模組增預註冊顯式 0 案（形同 `pre_register_renders_ipgate_blocked_explicit_zero`）、出口每呼一次恰 +1 案、出口恰一處生產呼叫點之靜態掃描案 `password_policy_invalid_outlet_is_called_from_exactly_one_production_site`（形同 `ipgate_blocked_outlet_is_called_from_exactly_one_production_site`；RL-0026 處數由測試釘；掃描輔件與阻擋出口共用或提升依 `handler/common.rs` 檔頭之收攏紀律判定、research 記判定）；行為面＝政策矛盾下三設密入口各回拒＋計數增一（spec SC-006）。
- **warn 日誌**：一則結構化 warn（target 與欄名依 research R11；含 min、max 現值、不含任何密碼字面）。
- **告警規則**（`deploy/grafana-provisioning/alerting/rules.yml`；組號 ③e、段錨註解寫事件錨與承載 ADR）：uid `obs016-password-policy-invalid`、title `password-policy-invalid`、`condition: C`、`for: 0s`、`noDataState: OK`（預註冊 0＝無增量即健康）、`execErrState: Alerting`、`labels.severity: warning`；評估鏈 A（prometheus instant：`sum(increase(password_policy_invalid_total[5m]))`、`relativeTimeRange` 300 秒）→ B（reduce last）→ C（threshold `gt 0`）；annotation `summary` 只帶規則名與 `$values.B`（annotation 契約：零 log 行、零個資），文面例「password-policy-invalid：密碼政策設定矛盾（最小長度大於最大長度、設密一律被拒；5m 增量 {{ $values.B }}、判準 > 0）」。檔頭「現況＝告警五組 12 條」改 13 條（組數不變）。
- **零新容器、零新 scrape 目標**：`deploy/prometheus/prometheus.yml` 不動（rust-api `/metrics` 既在 scrape 面）。

### 7.2 改密節流降級源（ADR-00078；spec FR-037）

- `obs::THROTTLE_DEGRADED_SOURCES` 增 `redis_change_pwd`（10→11、序接尾）；發射經既有 `throttle::warn_degraded("redis_change_pwd")`（target `security.throttle`、`degraded` 欄＝source）；預註冊與名冊雙向守（`degraded_emit_literals_across_src_stay_within_roster` 之全樹掃描自動涵蓋 `throttle/change_pwd.rs`）。
- 同改：常數 doc「★恰十」→恰十一並補該值說明、常數 doc「本常數逐字照抄」與測試訊息「十源名冊須逐字＝data-model §5 表」改述為「前十值＝004 刀 data-model §5 逐字、第十一值 007 刀增」；`lib.rs` crate doc「降級十源」改十一源；`obs.rs` 之 `pre_register_renders_throttle_degraded_ten_sources_explicit_zero` 與 `throttle/mod.rs` 之 `warn_degraded_increments_each_of_the_ten_sources` 兩案之名、期望值與訊息「恰十」「十源」同改；`obs.rs` 檔頭「十值」句與 004 刀 U9 歸因句補本刀。告警 `obs016-throttle-degraded` 不設 source selector＝新值自動涵蓋、規則零改。

### 7.3 活體驗證步驟（U22 執行；告警規則依既有活體驗證慣例實測；dev 庫寫入步驟逐步取 user 放行＝LL-00053）

1. rust-api 重啟後 `curl -s http://127.0.0.1:32079/metrics | grep '^password_policy_invalid_total'` 印 `password_policy_invalid_total 0`；`grep '^throttle_degraded_total{source="redis_change_pwd"}'` 印 0。
2. 以超管票經系統設定寫端（`POST /systemManage/updateSystemSetting`）把 `password_min_length` 設 20、`password_max_length` 設 10（皆在 REGISTRY 界內：前者 (1, 128)、後者 (1, 256)）。
3. 對自建帳號打一次 resetUserPassword（或本人 changePassword）→ `2222`＋`biz.user.passwordPolicy`；步驟 1 之命令印值 ≥1。
4. 起 `metrics` profile（prometheus＋grafana；`docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile metrics up -d`）→ 於兩個評估週期內（`interval: 1m`、`for: 0s`）Grafana 告警清單（`127.0.0.1:33000`）中 `password-policy-invalid` 轉 Firing、summary 帶增量；窗過後（5 分鐘內無新增）自然解除。查核命令形（UI 或 Grafana HTTP API）於本步實跑後原樣入 RUNBOOK（只寫實跑過之命令＝006 刀前例）。
5. 收尾：兩鍵改回 seed 值（8／64）→ 走查還原工具 restore（`system_settings` 值等於合成 seed 值、審計欄歸 NULL；設定寫端之稽核列隨清理面清除）→ `diff` rc 0。
6. 改密節流降級源以單元測試注入 redis 故障承擔（活體不另造 redis 故障）。

### 7.4 RUNBOOK 同批

- §11 增一子節「密碼政策壞值計數 `password_policy_invalid_total`」：讀法（行程內累計、重啟歸零、預註冊 0）、告警名與判準、處置（經系統設定寫端把兩鍵改回合法組合；008 刀前無設定頁＝走 API，命令形同 §9）。
- §13 增排障錨「設密一律回 `2222 biz.user.passwordPolicy`（含看似合規之密碼）」→ 先查政策矛盾（§11 該子節）。
- 新 tracing target `security.user`／`security.user_center` 與政策壞值 warn 之 target 屬 operator 可見輸出：活書與 RUNBOOK 有 target 列舉處同批補（以 `git grep -n 'security.policy_archive'` 現量枚舉）。

## §8 ADR 與帳本

### 8.1 ADR 之 accepted 時點（plan 期十四支＋收刀前 PATCH ADR 一支；詳表＝research R21）

| ADR | 主題 | accepted 時點約束 | accepted 同顆 |
|---|---|---|---|
| ADR-00074 | Amendment 1.7.1→1.8.0（島 I、§III.2 新用途、LOGIN-CAPTCHA (ii)、I18N (i)(iii)、島 B／C 用語、九島） | U0：user 逐款親決 → accepted＝獨立一顆 Amendment commit（只含本 ADR 與其連動條文；憲法 bump＋generate）；施工前提 | 親決紀錄（日期、所在任務、逐題結果）；改動提案字面者同步改寫決定節與 Amendment log |
| ADR-00075 | 包含規則與射程分工 | U0 施工前提顆（Amendment 顆之後另一顆） | —— |
| ADR-00076 | 明細通道射程與受眾 | 同上 | —— |
| ADR-00077 | 自助路由白名單 | 同上 | —— |
| ADR-00078 | 設密冷卻＋改密節流 | 同上 | —— |
| ADR-00079 | 政策壞值方向與告警出口 | 同上 | —— |
| ADR-00080 | ADR-00047 續行（使用者域寫端語意） | 同上 | `supersedes: [ADR-00047]`、ADR-00047 status→superseded |
| ADR-00081 | ADR-00068 續行 v3 | 治理單元（CDP 三方對照與已知態實測之後；U22）依親決分類（RL-0086）經 user 親決 | `supersedes: [ADR-00068]`、ADR-00068 status→superseded |
| ADR-00082 | ADR-00069 續行 | 同上 | `supersedes: [ADR-00069]`、ADR-00069 status→superseded |
| ADR-00083 | 清單 wire 偏離帳 | U0 施工前提顆 | —— |
| ADR-00084 | 繁中 runtime、預設 zh-TW、zh-tw-lint 閘 | 同上（不晚於 zh-tw-lint 接線單元同顆之要求自動滿足） | `supersedes: [ADR-00039]`、ADR-00039 status→superseded |
| ADR-00085 | m0003、按鈕維受保護列首例、GR9 序號合成、走查還原工具遷移帳前置與合成 | 同上（MUST 早於工具單元 U1） | —— |
| ADR-00086 | 選單編輯移除受保護授權碼之守門 | 同上 | —— |
| ADR-00087 | ADR-00012 整支續行（schema-definition 留 001 刀基線） | 同上 | `supersedes: [ADR-00012]`、ADR-00012 status→superseded |
| 收刀前 PATCH ADR（配號＝屆時下一號；plan 期不起草） | 範圍欄預估值實數化（表外宣告 1 例外路徑；前例 ADR-00051／ADR-00072） | 收刀前承載體檢單元（U23）：user 親決後 accepted、與 Amendment 同一顆獨立 `docs(constitution): amend` commit | 憲法 1.8.0→1.8.x、Amendment log、generate |

- proposed 期 `supersedes: []`；續行型 accepted 那一顆補 supersedes 並改被續行者 status、`superseded_by` 由 `python3 tools/docsync generate` 回填，generate 後再 `git add docs/arc42/decisions`（LL-00044）；新 ADR 檔先 `git add` 再跑 lint（GT-05 只掃 tracked）。
- 現在式面指向 ADR-00039／ADR-00047／ADR-00068／ADR-00069／ADR-00012 之引用：各於 supersede 之顆以 `python3 tools/docsync errata <號>` 現算、逐處改指（扣除史料面、生成鏡像、事件源與 ADR 檔；兩子庫另以 `git -C <子庫> grep` 並掃）；ADR 間互引一律「號＋決定款／款號」。
- ★`specs/002-system-settings/contracts/wire-settings.md` §3 第 3 條屬凍結存證：本刀不改該檔（ADR-00041 決定 3；spec FR-051 修補後讀法）；碼註以之為錯誤 data 規則依據者同批改指 ADR-00076——`envelope.rs` 模組 doc、`Res` doc、`from_err` doc、測試 `error_envelope_data_null_not_omitted` doc、`error.rs` 測試 `each_issuable_code_builds_error_envelope` doc（U6；逐處見 `contracts/msg-keys.md` §6）；成功信封測試 doc 與 `tests/contract.rs` 之 4040 fallback 腿 doc 所述仍真、只補 ADR-00076 指針（spec FR-051「碼註指向該條者同批改指」；六處＝ADR-00076 決定 5）。

### 8.2 帳本

- **本刀第一筆 events 事件**：`backlog_add`＝BL-00140／BL-00141／BL-00142（前兩條已於 brainstorm 顆入 `docs/ops/BACKLOG.md`／`docs/ops/BACKLOG-DEFERRED.md`、BL-00142 於 plan 顆入 `docs/ops/BACKLOG.md`；事件帳現 0 筆；spec FR-060）。
- **收刀 `feature_close`**：`backlog_done` 9＝BL-00031（spec FR-034）／BL-00047（FR-045）／BL-00048（FR-022）／BL-00065（FR-028、FR-029）／BL-00091（FR-040）／BL-00124（FR-037）／BL-00136（FR-057、FR-058）／BL-00138（①由 FR-052 兌現、②移交 BL-00141）／BL-00143（spec FR-032 日誌面；T111）；`backlog_add` 一＝BL-00143（本刀 U10 誕生、晚於第一筆事件；BL-00140～BL-00142 已由第一筆事件帶，GT-03 唯一性腳＝不得重記）；`adrs`＝ADR-00074～ADR-00087（十四支）＋收刀前 PATCH ADR 一支；`arch_impact` 以收刀時 diff 現算之活書節號為準；收單事件註明反向確認三條之結果。
- **刪列前掃現在式引用**（RL-0050）：BL-00136 之現在式引用除 BACKLOG 本條外另有 `rust-api/server/tests/contract.rs`、`docs/ops/NOTES.md`、LESSONS 一檔；其餘七條逐條以 `python3 tools/docsync errata BL-NNNNN` 現量。
- **NOTES**：下一步收刀後改 008 刀（008 刀起每刀三語同批）；不記推送狀態、只記 SHA。
- **活書與 RUNBOOK**（spec FR-059；feature branch 內改為現在式 as-built）：06（島 I 情境、§6.1 島 G 情境之 no-escalation 句）、08（§8.1 記事欄句、§8.3 掛點句、§8.4 新用途逐用途一句碼上實作〔含單行形新增型分列〕、i18n 三語）、10（島 I 情境）、11（已知態摘要改指 ADR-00081）、12（使用者域詞組、「頂替」「踢除」、「撤銷三型」消歧）、05（`tools/zh-tw-lint.py`、新 handler 與 facade 成員句）；RUNBOOK §9（解鎖兩入口取代「無 UI 按鈕」句）、§9c（§6）、§10（Day-1 與 m0003）、§11（§7.4）、§12（§2.1、§2.3、§6 各列）、§13。C4-L2 拓樸不變（零新容器）。

### 8.3 收刀前承載體檢與 DoD 機器面（U23）

- **反向確認**（命令現算、結果入收單事件）：BL-00108——`git -C rust-api grep -l -E 'fn (skip_ws|ident_at|close_of|split_top|peel_attrs|attr_spans|token_positions)\b' -- server` 之輸出仍恰為 `server/tests/entity_behavior_lint.rs`、`server/tests/wire_i64_guard_lint.rs` 兩檔（自起點 pin 零增＝零第三份字元級解析組）；BL-00043——生產面零新增存取軌跡寫入點（`git -C rust-api grep -n 'sys_access_log' -- server/src` 前後現算比對、零 `access_log_mw`）；BL-00133——生產面對 `sys_casbin_policy_archive` 之讀寫點集合自起點 pin 零增；零新依賴——`rust-api/Cargo.lock`、`base-web/pnpm-lock.yaml` 自本刀起點 pin 起零 diff；migration 目錄恰 `m0001_baseline_schema.rs`／`m0002_baseline_seeds.rs`／`m0003_seed_button_governance.rs`；`docs/ops/reference-src/schema-evolution.json` 之 entries 恰九筆、`next_id` 10。
- **Day-1 登記三步**（RUNBOOK §10）：①`python3 tools/docsync refresh`（dev 庫先以走查還原工具回基準＝accounts 投影不連坐；需 stack）②演進帳九筆已於 m0003 單元登記、此處只複核 ③`python3 tools/schema-gate.py check --container <pristine 容器>`（全新庫重放 m0001～m0003）綠＋§2.4 真庫變異自證。
- **另複核**：§1.4 變更檔集斷言全量復跑；§1.1 Amendment 顆 gitlink＝`fb4dac2`；範圍欄 PATCH 實數化（§1.2 通則⑥之清單）後 `python3 tools/fork-delta-lint.py` 對賬腿自動納入實數化項、rc 0；★對賬腿變異自證（spec SC-011）：PATCH 實數化之後逐用途取本刀一列，暫把其範圍欄實數改 +1（或暫拔一枚該用途標記；巢狀 (vii) 塊取「暫拔一對塊首塊尾」形）→ `python3 tools/fork-delta-lint.py` 當場 rc 1 指名該三元組或檔 → 以存原文寫回（RL-0019）→ `git diff --name-only` 與 `git -C base-web status --porcelain` 零殘留；逐發單獨跑、結果入 commit 訊息。
- **收刀 DoD 之機器面**（spec FR-066）：容器內後端全量測試全程 serial＋contract 61 case；`pnpm typecheck`（三語 Schema；容器內）；碼面閘表全員 `check` rc 0（名冊唯一權威＝RUNBOOK §12 碼面閘表；本刀後成員＝`python3 tools/schema-gate.py check`〔含 m0003 合成〕、`python3 tools/entity-drift-gate.py check`、`python3 tools/rust-fmt-gate.py check`、`python3 tools/wire-schema.py check`、`python3 tools/fork-delta-lint.py`〔含名冊載入變異自證、範圍欄對賬腿、修改型只在授權檔〕、`python3 tools/msg-key-gate.py check`、`python3 tools/view-render-guard.py check`、`python3 tools/route-artifact-gate.py check`〔容器在場〕、`python3 tools/seed-view-gate.py check`、`python3 tools/zh-tw-lint.py check`；容器依賴者具名跳過不算驗收）；`python3 tools/docsync check`／`lint` 零紅；走查基準 `diff` rc 0；CDP 三方對照（判準＝spec SC-010）。
