---
id: "ADR-00026"
title: 憲法 Amendment 1.2.0→1.3.0——§III.2 首批四條 ★ 軌道八用途授權＋§I.7 首批五座行為島 A～E 入憲
date: 2026-09-08
status: proposed
supersedes: []
superseded_by: []
provenance: "003-auth-session 之 spec FR-029～FR-031（brainstorm Q1／Q5／Q9、clarify 2026-09-08 Q3／Q4）；形制輸入＝research R8（`tools/fork-delta-lint.py` load_roster 六條硬規則）；★軌道範圍欄素材＝spec「★ 軌道逐處登記」16 列表（量測日 2026-09-08、量測面 base-web worktree＝upstream example tip 8be6f9ba）；島條文以 rev5 憲法 v1.3.0 §I.7 島 A～E 逐字為底（rev5:ADR 0028、rev5 凍結 SHA 7eab28a）並依 rev6 拍板增四處；憲法 §V.2 Amendment 流程、§V.3 MINOR 判準；draft 於 plan 期落 feature branch（brainstorm Q5）、user 親決於 tasks 首個主線任務"
tags: [constitution, amendment, fork-delta, behavior-island, auth]
---

## 背景

憲法 §III.2 自 v1.0.0 起是空的凍結位（哨兵句「（空表——尚無 ★ 軌道；首列隨首刀 Amendment 落入。）」為其合法態證據），§I.7 同樣只有進場規則與承襲指針。003-auth-session 是 rev6 第一把同時撞到兩者的刀：

- **§III.2 面**：後端補齊 12 條端點後，base-web 必須接線才看得到成果。逐處勘查得 16 列（spec「★ 軌道逐處登記」表）＝`.env*` 3 列 4 行（§III.1 既有 `BASE-WEB-ADAPT`）＋新檔 `zh-tw.ts` 1 列（不觸 ★ 軌道）＋**12 支既有檔分屬四條尚未存在的 ★ 軌道、八個用途**。開立之前，動任何一支都是無授權 inline。
- **§I.7 面**：本刀落地五台狀態機（token rotation／single-session／denylist 撤銷／idle 逾時／登入失敗節流）。§IV 第 9 題問「該入憲而未入憲的新行為島、是否隨本刀排入 Amendment」——不排即當場擋。實質理由：五台機器各有刻意選定且彼此不一致的 fail-* 方向（idle fail-open 而 denylist fail-closed；節流設定缺失 fail-open 而 idle 設定缺失 fail-loud），不入憲則任何一次方向反轉都只是普通改碼、沒有 MAJOR 閘。

兩者同屬 §V.3 MINOR（「新增 ★ 軌道」與「行為島隨刀進場」各自列名），合計一次 bump：**1.2.0 → 1.3.0**。

**改本檔哪一節**（§V.2 步 1）：§III.2「已授權軌道與用途」表（落四軌道八用途、移除哨兵句；表外三項宣告不動）；§I.7「已入憲行為島」段（替換「（尚無…）」為島 A～E 條文＋跨島註）與承襲指針表 A～E 列註記；文末 `Version`／`Last Amended`／Amendment log。

## 決策驅動因子

- `tools/fork-delta-lint.py` 的名冊斷言（002 落地）以 §III.2 表為唯一來源：表列形受 `load_roster` 六條硬規則約束（首欄 `**★NAME**`、用途欄括號識別符起首、範圍欄反引號路徑 token、brace 單組展開、（…）注記內 token 不入集、哨兵句與資料列不得並存）——條文形制不對即 lint rc 2、全 repo 無法 commit。
- 三處 rev6 拍板須入條文而 rev5 條文無：島 B 生效時點（brainstorm Q9）、設定改值總則（clarify Q4）、節流設定鍵矛盾組合方向（clarify Q3）。
- 授權收窄原則：rev5 曾開更寬用途集，rev6 只開本刀實需的八用途；`(ii)` 類三項明文不授權。

## 考慮過的替代案

1. **specify 之後即 draft**：§III.2 範圍欄是檔級硬邊界、設計未定即列必再改一次——棄（brainstorm Q5）。
2. **拆成兩筆 Amendment（軌道一筆、島一筆）**：同一 MINOR 級、同一刀、兩顆憲法 commit 徒增歷史噪音——棄（rev5 同判）。
3. **島條文整表照搬 rev5 v1.10.0 終態（含 004 補記兩句）**：來源維釐清與解鎖標記方向屬 004 ip-trust-anchor 域、本刀無實作面——棄；rev6 以 v1.3.0 首批字面為底、004 進場時再補。

## 決定

### 一、§III.2 新增機器可解表列（四軌道、八用途；替換哨兵句）

以下八列逐字落入 §III.2「已授權軌道與用途」表（標題列與分隔列既有）：

| 軌道 | 用途 | 範圍（檔案） | 紀律 |
|---|---|---|---|
| **★BASE-WEB-AUTH-WIRING** | (a) constant routes 合併 | `src/store/modules/route/index.ts`（1 處，修改型） | 僅限 `initConstantRoute` 之 dynamic 分支；MUST 為**併入** static 常量集而非取代（seed `constant=TRUE` 為 0 列，取代會清空 login／403／404／500／iframe-page 五條 builtin）；不得擴及 route store 其他分支 |
| **★BASE-WEB-AUTH-WIRING** | (b) 三表單 stub 化 | `src/views/_builtin/login/modules/{code-login,register,reset-pwd}.vue`（各 2 處，修改型） | 僅改 import 指向 stub wrapper＋消滅假成功 toast；不動表單欄位、驗證規則與版面 |
| **★BASE-WEB-AUTH-WIRING** | (c) captcha hook 改打 stub | `src/hooks/business/captcha.ts`（約 4 處，修改型） | 僅改請求目標為 `/auth/sendCaptcha`＋移除假延遲與假成功 toast；hook 對外簽名不變 |
| **★BASE-WEB-LOGIN-CAPTCHA-WIRING** | (i) 登入頁 captcha 軟區 | `src/store/modules/auth/index.ts`（修改型）／`src/views/_builtin/login/modules/pwd-login.vue`（修改型＋新增型） | auth store `login()` 改打 wrapper `fetchLoginWithCaptcha`（不改 upstream `auth.ts`）並串通失敗 msg 回傳鏈；軟區為條件渲染，登入失敗後 MUST 重取新題並清空輸入（後端提交即消耗）；**非軟區時零行為變更**；三顆快速登入鈕零 inline。★用途 (ii)（`formRules` 放寬）**不在本次授權**，延改密端點刀 |
| **★BASE-WEB-I18N-WIRING** | (i) 後端 msg 轉譯 | `src/service/request/index.ts`（2 處修改型＋1 塊新增型） | 單一 helper `translateBackendMsg(msg)`＝`$t` 帶原文 fallback；modal `content` 與 `showErrorMsg` 鏈改走之；未命中 MUST graceful fallback，不得吞錯亦不得顯裸 key（錯誤信封 `data` 恆 null、無明細通道 ⇒ 不建 `translateDetailValue`） |
| **★BASE-WEB-I18N-WIRING** | (ii) locale backend 樹 | `src/locales/langs/{en-us,zh-cn}.ts`（各 1 塊，新增型） | 插入錨為**獨佔一行**的 `  backend: {`；三檔（含新檔 `zh-tw.ts`、新增型不入名冊）backend 子樹鍵集 MUST 各自與後端 `MSG_KEYS` 全等（跨端閘）；譯文以 `specs/003-auth-session/contracts/msg-keys.md` 為權威 |
| **★BASE-WEB-I18N-WIRING** | (iii) Schema backend 型節 | `src/typings/app.d.ts`（1 處，修改型） | 僅補 `App.I18n.Schema` 之 `backend` **必填**型節。★`LangType` 擴充／locale 註冊／`zh-tw.ts` 標型重構**不在本次授權**，延前端 UI 刀 |
| **★BASE-WEB-LOGOUT-UX-WIRING** | (i) 登出前撤銷接線 | `src/layouts/modules/global-header/components/user-avatar.vue`（約 3 處，修改型） | `onPositiveClick` 改 async、登出前 best-effort `await` logout wrapper，**失敗不得阻斷** `resetStore()`。★用途 (ii)（reLogin toast）**不在本次授權** |

- 哨兵句「（空表——尚無 ★ 軌道；首列隨首刀 Amendment 落入。）」MUST 同批移除（`load_roster`：並存＝die）。
- 表外三項適用宣告不動（處數為估值、檔級名單硬邊界；devproxy／modal 不另開軌道；新增型 `NAME+` 不入名冊）。
- `.env*` 四行走 §III.1 `BASE-WEB-ADAPT`（§II #2 明寫 ADAPT 軌道）＝零修憲、標記裸形。

### 二、§I.7「已入憲行為島」段（替換「（尚無——首座隨首刀以 MINOR Amendment 進場。）」）

**已入憲行為島**（首批五座由 ADR-00026 於 v1.3.0 隨 003-auth-session 進場；出處 `rev5:ADR 0028`、rev5 v1.3.0 字面為底；rev6 增補恰四處＝島 B 第二點（brainstorm Q9）、島 E 末點（clarify Q3）、跨島總則（clarify Q4）、末句「方向性反轉自此為 MAJOR」射程確認，其餘逐字）：

**A. token rotation**
- 同一鏈（family）至多一條 `active`；DB partial UNIQUE 為護欄而非唯一防線。
- rotate 次序 MUST 為「舊列轉 `rotated` 並寫 `used_at` → 插新 `active`」，**次序不可反**。
- grace 窗內同票二度換發 MUST 冪等回**既發的同一對**；grace 窗 MUST 大於前端最壞重試間隔。
- reuse 偵測的**唯一觸發形**＝列為 `rotated` 且 grace miss；命中即撤整條家族。
- fail-* 方向：grace 不可用＝**fail-secure**（並發換發觸發 reuse、撤家族；重登復原）。

**B. single-session**
- 政策解析為**兩層**：`effective_single = session_policy=='single' || (session_policy=='inherit' && single_session_default=='on')`。
- 單一會話**只於登入事件判定**；`single_session_default` 翻轉不影響既有會話（不追溯；窗口上限＝refresh 全壽命、值留活書）。
- 踢除 MUST 落 `session_event(kicked)` 並寫 denylist；被踢者在 `(access, refresh)` 窗內換發仍得 `7777`。
- fail-* 方向：`single_session_default` 讀不到＝**off 語意**（刻意與 D、E 方向不同）。

**C. denylist 撤銷**
- `sys_token.status` 為**權威**、denylist 為加速層；兩者不一致時以 status 定案。
- 鍵缺席（nil）＝「未撤」語意 ⇒ 放行；`revoked` 列缺 denylist MUST 靜默 `8888`、**不得落假 reuse**。
- denylist TTL MUST ＝ refresh 全壽命，`kicked` 與 `revoked` 兩 reason 皆同。
- fail-* 方向：讀不到（連線 Err）＝**fail-closed**——退 PG 查該鏈是否仍有 active，無 active→`8888`；**PG 亦故障 MUST 視為無 active、絕不盲放**。

**D. idle 逾時**
- 門檻＝`refresh_secs − access_secs`；`session_event(idle)` MUST 僅首次落（SET NX 守門）。
- 不等式 `access_TTL ≤ N×30 < N×60` ⇒ idle 命中 **MUST NOT** 寫 denylist。
- fail-* 方向：`last_activity` 不可讀＝**fail-open**（不 idle-reject，以 token exp 為界）。

**E. 登入失敗節流（帳號維）**
- 三區（自由／需驗證碼／鎖定）；滑動窗（PG）為**權威**、redis L1 為負快取。
- 軟區與鎖定 MUST 在密碼雜湊驗證**之前**擋下，且**零稽核列、零計數桶**（拒絕不得消耗受害者的額度）。
- fail-* 方向：redis 整體不可用＝**fail-open**（軟區 captcha 要求整層停用、續驗密碼，密碼錯仍計數）；L2（PG）查詢失敗＝**fail-open ＋ 補償**（計數歸零放行並置 `captcha_forced`）；captcha 標記 SET NX 瞬斷（redis 健康）＝**fail-closed 不罰**（拒該次、零計數桶）。
- 節流設定鍵缺失、或**矛盾組合**（驗證碼門檻大於鎖定門檻）＝視同不可用、退活書常數並發結構化告警（每次載入至多一筆）；門檻相等＝合法（軟區寬度零）。

**跨島註（方向刻意不一致，記於此以免日後被「統一」）**：登入流程讀 `session_idle_timeout` 設定鍵缺失＝**fail-loud**（`5000`、不猜 TTL 值），與 E 的節流設定鍵缺失走 fail-open 退常數方向相反——前者猜錯會靜默改變所有人的會話壽命，後者猜錯只影響阻力強度。

**跨島總則（設定改值的生效時點）**：每個設定鍵只在其消費事件當下讀現值；已簽發 token 的壽命與已建立的會話不追溯——single-session 於登入事件、idle 門檻與 TTL 於每次簽發（登入／換發）、節流三鍵於每次登入嘗試。

**方向性反轉自此為 MAJOR**（§I.7 進場規則既有條款，此處確認其射程已涵蓋上列五島）。

承襲指針表 A～E 列之「rev5 入憲載體」欄尾註「；rev6 已入憲 v1.3.0（ADR-00026）」。

### 三、版本與程序

- bump **1.2.0 → 1.3.0**（MINOR：§V.3「新增 ★ 軌道」與「行為島隨刀進場」兩款）；`Last Amended` 改凍結日；Amendment log 加一列（形沿 1.2.0 列）。
- 本 ADR 轉 accepted 與憲法改動 MUST 同一顆 commit（§V.2 步驟 4）、同批 `python3 tools/docsync generate`；commit 訊息 `docs(constitution): amend §III.2 首批 ★ 軌道四條八用途＋§I.7 島 A～E（1.2.0→1.3.0）`。
- 該 commit 落地即解除「base-web 既有檔硬閘」；在此之前，純新增檔（`rev6-auth.d.ts`／`rev6-auth.ts`／`zh-tw.ts`）依 §III.2 表外宣告 3 不受此閘。

## 後果

- §III.2 自此不再是空節；`tools/fork-delta-lint.py` 名冊＝§III.2 四名 ∪ §III.1 三名（七名），三元組硬邊界對真標記首次生效；哨兵句移除後 `load_roster` 走「≥1 列」腿。
- **三分碼射程**（兌現 ADR-00014 後果段「003 接真 session 時對 3333／8888 分工重定」、不翻該 ADR）：`3333` 僅 access exp 過期（enforce 驗章）；標頭缺席・非 Bearer・簽章不符・已撤銷・refresh 鏈失效→`8888`；被踢→`7777`；refresh 端點自身驗章失敗恆 `8888`。措辭同落 `error.rs` 碼註與活書 §8。
- i18n 三檔（`app.d.ts`／`en-us.ts`／`zh-cn.ts`）是本次授權裡 upstream 衝突風險最高的面（近 12 月各 13～15 commit）；rebase 處置＝先比對 upstream 是否已自行新增 `backend` 節或改 `Schema` 結構，若是則對齊而非疊加。
- 授權是收窄的：`(ii)` 類三項（`formRules` 放寬／reLogin toast／`LangType` 與 locale 註冊）明文不授權；要開走 §V.2，不得以「同軌道內」默開。
- §I.7 一旦填入，五島 fail-* 方向與跨島總則受 MAJOR 閘保護；常數值（30 秒／300 秒／seed 門檻／窗口上限）留活書。
- 本 Amendment 不新增 migration、不動 wire 契約、不動 §II 拍板；§I.1～§I.6 一字不動。

## 翻案觸發器

- 004 ip-trust-anchor 進場時島 E 須補來源維釐清與解鎖標記方向兩句（rev5 v1.4.0 補記）——屬「已入憲 invariant 細項調整」MINOR、由該刀 Amendment 承載。
- 任一島 fail-* 方向要反轉（如 idle 改 fail-closed、denylist 改 fail-open）＝MAJOR。
- 前端接線需要表外檔或新用途（含 `(ii)` 類）＝回 §III.2 走 §V.2。
