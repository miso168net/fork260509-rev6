# Contract — 個人中心兩端點與錯誤明細通道

> 權威序依憲法 §I.3：base-web 實碼 ＞ 官方 docs ＞ mock。個人中心頁為 upstream demo 面（`views/user-center/index.vue` 靜態殼），本刀只掛「修改密碼」卡；契約以 `rev5:007` 之 `contracts/wire-user-center.md` 與其 HEAD as-built（`rev5:server/src/handler/user_center.rs`、`rev5:server/src/error.rs`／`rev5:server/src/envelope.rs` 之明細通道、`rev5:src/typings/api/rev5-user-center.d.ts`、`rev5:src/service/request/index.ts` 之明細插值鏈）為藍本、依 rev6 拍板改寫（差異見文末逐欄比對、理由住本刀 research R5／R11／R14），由本檔凍結（wire 活體權威＝碼＋`tests/contract.rs`＋wire-schema 快照）。
> 信封與錯誤碼總則同 `wire-user-admin.md` 檔頭。本檔 §3 為**錯誤明細通道**之 wire 家：信封形、data 兩形、後端出口與前端轉譯以 §3 為準，`wire-user-admin.md` 與 `contracts/msg-keys.md` 引之。
> 兩條皆 `Protection::Authed`（登入即可用、不進 casbin 判定；量法：`rust-api/migration/src/m0002_baseline_seeds.rs` 之 casbin seed 對 `userCenter` 字樣 `grep -c`＝0）；零角色帳號同樣可用。★標的恆＝登入者本人（`enforce_mw` 驗章後注入之 `Identity.uid`；FR-003）：兩支請求型結構性零 id 欄、body 多帶之鍵（含 `id`）一律忽略。後端 handler 住新建 `rust-api/server/src/handler/user_center.rs`（新域 target `security.user_center`、本域 `BODY_FALLBACK_MSG`、私有 `operator_from`／`db_failure`）；共用 `handler::user` 之 `finish_user_write` 與兩支明細組裝件（§3.3；皆 `pub(super)`）、不另持拷貝。型別檔＝新建 `base-web/src/typings/api/rev6-user-center.d.ts` 之 `Api.UserCenter`；wrapper＝新建 `base-web/src/service/api/rev6-user-center.ts`（兩支；不入 barrel；錯誤不加工）。

## 端點總表

| # | 端點 | 授權態 | 鎖與交易 | case_key（新建） | handler（新建） | fetcher（新建） | 成功 `data` | 前端消費者 |
|---|---|---|---|---|---|---|---|---|
| 1 | `GET /userCenter/getPasswordPolicy` | Authed | 零鎖零交易零寫入 | `user-center-get-password-policy` | `handler::user_center::get_password_policy` | `fetchGetPasswordPolicy()` | `PasswordPolicyView` | `hooks/business/pwd-policy.ts`（新檔）→ 改密卡、「重設密碼」浮層 |
| 2 | `POST /userCenter/changePassword` | Authed | advisory(uid)＋本人列鎖（雜湊於鎖前） | `user-center-change-password` | `handler::user_center::change_password` | `fetchChangePassword(data)` | `null` | 改密卡（`views/user-center/modules/password-card.vue`、新檔） |

- 兩條接 `wire-user-admin.md` 十條之後（ROUTES 49→61、Authed 3→5）。個人中心之**可達性**不是新端點：getUserRoutes 恆併入自助路由白名單 `SELF_SERVICE_ROUTES`＝`["user-center"]`（FR-039、ADR-00077；兩向案＝research R12）。ADR-00037 觸發器反向確認：改密為 Authed、依 uid 節流、不新增存取軌跡寫入面（FR-031）。

## 共用型（`Api.UserCenter`）

定名規則＝`wire-user-admin.md` 共用型節之定名規則句。五名於 pin 樹零命中（`git -C rust-api grep -nw`／`git -C base-web grep -nw`）。

| 型 | wire 形 | 方向 | rust 落點 |
|---|---|---|---|
| `PasswordPolicyView` | 七欄（§1） | 讀 | `handler/user_center.rs` |
| `ChangePasswordReq` | `{ oldPassword: string, newPassword: string, confirmPassword: string }` | 請求（body） | `handler/user_center.rs`（手寫遮蔽 `Debug`、三欄恆印遮蔽字面） |
| `PasswordViolationCode` | `'minLength' \| 'maxLength' \| 'maxBytes' \| 'requireDigit' \| 'requireLowercase' \| 'requireUppercase' \| 'requireSpecial' \| 'forbidUsername'` | 讀 | typings 專屬（rust 側＝`model::password` 之 `VIOLATION_*` 八常數、`&'static str`） |
| `PasswordPolicyDetail` | `{ violations: PasswordViolationCode[] }` | 讀（錯誤信封 `data`） | `handler/user.rs`（與組裝件同檔） |
| `PwdSetTooFrequentDetail` | `{ remainingSeconds: number }` | 讀（錯誤信封 `data`） | `handler/user.rs`（rust `u64`） |

- 明細兩型雖由使用者域與個人中心共同發出，typings 歸 `Api.UserCenter`：與 `PasswordPolicyView` 同屬密碼政策家族、消費者（請求層轉譯、`pwd-policy` hook）不屬任一管理頁。
- 受審（FR-064）：五型入受審名冊並各配正反例：預期讀端冊 4、請求端冊 1（實數以抽取為準；`contracts/code-gates.md` §4）；明細兩型之 rust 側受裁面＝兩支組裝件實際產出之 `data` 值。重點反例：`PasswordPolicyView` 多一欄冷卻、開關欄為 `'on'`／`'off'` 字串、`violations` 元素值域外、`remainingSeconds` 為字串、`ChangePasswordReq` 缺 `confirmPassword`。

## 1. `GET /userCenter/getPasswordPolicy`（Authed）

請求：無 query、無 body。200：`data: PasswordPolicyView`——恰七欄：

| 欄 | 型 | 設定鍵 | 語意 |
|---|---|---|---|
| `minLength` | number | `password_min_length` | 字元數下界（以字元計） |
| `maxLength` | number | `password_max_length` | 字元數上界 |
| `requireDigit` | boolean | `password_require_digit`（`'on'`→true） | 須含 `[0-9]` |
| `requireLowercase` | boolean | `password_require_lowercase` | 須含 `[a-z]` |
| `requireUppercase` | boolean | `password_require_uppercase` | 須含 `[A-Z]` |
| `requireSpecial` | boolean | `password_require_special` | 須含 `[^A-Za-z0-9]` |
| `forbidUsername` | boolean | `password_forbid_username` | 與帳號名不分大小寫**相等**即違規（子串不算） |

- **不下發**：冷卻秒數 `password_change_min_interval`（端點固有規則、下發即成可繞過之提示）、位元組上界 512（碼內常數 `throttle::LOGIN_PASSWORD_MAX_BYTES`）、其餘設定鍵（投影型欄集即結構性答案）。
- **與驗證點同源**（FR-032／FR-038）：與三個設密入口讀同一支載入件 `model::password::load_password_policy`（消費當下現讀、不快取），投影只經 `impl From<PasswordPolicy> for PasswordPolicyView` 一條路徑、逐欄零轉換。單鍵缺列或不可解析之處置（逐鍵退碼內預設＝seed 值，`rev5:007` HEAD 形）＝research R11；矛盾組合（min ＞ max）照原值投影、本端點不拒（前端規則使任何輸入皆不合＝與後端設密全拒同向）。
- 唯讀：零鎖、零交易、零稽核；錯誤集只有 `8888` 與 `5000`。登入路徑 MUST NOT 驗政策（seed 三帳號之 6 字元密碼照常登入）。

seed 例：`{"data":{"minLength":8,"maxLength":64,"requireDigit":false,"requireLowercase":false,"requireUppercase":false,"requireSpecial":false,"forbidUsername":false},"code":"0000","msg":"common.success"}`。
前端：`pwd-policy` hook 組表單規則（改密卡新密碼欄、「重設密碼」浮層）；取不到時退為只驗必填（卡與浮層不另出提示、不擋送出；共用請求層之統一錯誤提示照常＝user 2026-10-15 親決）、後端仍是唯一裁判；新增抽屜之設密欄只掛提示文字（FR-038）。

## 2. `POST /userCenter/changePassword`（Authed）

Req `ChangePasswordReq`。後端 `#[derive(Default, Deserialize)]`＋`#[serde(default, rename_all = "camelCase")]`、不 derive `Debug`；body 經 `handler::common::json_or_default(req, state, "changePassword", BODY_FALLBACK_MSG)`——缺席、壞 JSON、型別不符＝整包收斂為三欄空字串（零新鍵）。

處理序（★次序即契約；任一步拒＝零寫入零稽核；`rev5:007` 七步序沿用；逐步全文與鎖序＝data-model §3 之 changePassword 節與 §5）：

| 步 | 判定 | 拒因 | 備註 |
|---|---|---|---|
| 0 | 操作者上下文 | `5000` | 先於一切 |
| 前置 | begin 之後、①取鎖之前 `password::NewPassword::prepare`（交易內、不持任何鎖＝spec FR-012）；開交易之前不讀節流桶 | 雜湊失敗＝`5000`（實務不可達） | 節流桶之判讀在③、推進在④（皆於帳號鎖內＝ADR-00090 決定 2） |
| ① | advisory(uid) → 本人現役列 `FOR UPDATE` | `2222 biz.user.notFound` | 會話存續期間被軟刪時可達；停用照過 |
| ② | `confirmPassword` 與 `newPassword` 逐字相等 | `2222 biz.user.passwordConfirmMismatch` | |
| ③ | 改密節流：帳號鎖內現讀 `cpwd:{uid}`、計數 ≥ 5 | `2222 biz.user.changePasswordThrottled` | ★於舊密比對之前；純 key、不攜剩餘時間 |
| ④ | 舊密比對（鎖內列之雜湊；鎖內重驗＝島 I1） | `2222 biz.user.oldPasswordMismatch` | 不符＝帳號鎖仍持有、rollback 之前推進節流計數一格（唯一推進腿），再 rollback |
| ⑤ | 新≠舊（舊密已於④驗真 ⇒ 明文相等即同密、零額外 argon2） | `2222 biz.user.passwordSameAsOld` | 端點固有規則、不入政策單點 |
| ⑥ | 密碼政策（`forbidUsername` 比本人帳號名） | `2222 biz.user.passwordPolicy`＋`{violations}` | §3.2 |
| ⑦ | 設密冷卻（（本人, 本人）） | `2222 biz.user.pwdSetTooFrequent`＋`{remainingSeconds}` | 一體適用、零豁免（FR-035） |

Applied（同一交易）：UPDATE `password`＋`updated_*`（＝本人）→ `sys_pwd_custody::touch(uid, uid)`（只 upsert、不刪他人經手列）→ 撤本人**其他**有效票（`handler::user::revoke_sessions_in_txn`〔keep＝`identity.sid`〕→ `sys_token::revoke_others_of_user(uid, &identity.sid)`——與 `revoke_all_of_user` 共用私有底座 `revoke_sids_of_user`；當前會話之鏈與其後續輪替保留、已輪替列不動）→ 逐 sid 會話事件 `revoked`／`password_changed`（非 `password_reset`）→ 稽核 `change_password`（`sys_user`、本人 uid、payload 不含密碼）→ commit → `finish_user_write` 逐 sid 盡力寫失效名單 `revoked`（零重載）→ **commit 之後**清空節流桶。
200：`data: null`。其他裝置下一次請求 `8888`（換發亦拒）；當前裝置不受影響（`Identity.sid` 自 claims 注入；FR-036）。

**改密節流**（FR-037；ADR-00090〔續行 ADR-00078〕）：

| 面 | 契約 |
|---|---|
| 鍵 | redis `cpwd:{uid}`（獨立前綴、不在 `throttle:` 之下：維度為 uid、與登入節流之帳號名／IP 維分離；批次清登入節流鍵時不誤清） |
| 門檻 | 碼內常數 `CHANGE_PWD_MAX_FAILS = 5`、`CHANGE_PWD_WINDOW_SECS = 900` |
| 計數 | 只有④推進（帳號鎖內、rollback 之前）：INCR 與 EXPIRE 900 於伺服器端同一原子單位、存活自最近一次失敗起算（本刀「15 分鐘滑動窗」之落地形）；其餘拒因不推進 |
| 並發 | 判讀（③）與推進（④）皆在帳號鎖持有期內：同一帳號之並發請求於①排成單列、後到者讀得到先到者已落地之推進 ⇒ 窗內舊密比對失敗合計至多 5 次（ADR-00090 決定 2） |
| 壞值 | 判讀：非整數字串＝視同 0；非字串型別＝讀取錯誤、照降級放行（計一格）；可解析整數照計數（≥ 5 即拒）。推進：遭伺服器以型別不符、非整數、遞增溢位三類錯誤拒者，於同一原子單位內除去壞值後遞增（＝1）並刷窗、warn 一則、自癒不計降級；其餘伺服器錯誤與連線故障不觸發、照降級 |
| 拒／解除 | 計數達 5 後第 6 次起於③拒；成功改密（commit 後）即清、否則鍵自然過期＝窗自癒；無解鎖端點（ADR-00069 款 5 不觸發） |
| 降級 | redis 讀寫錯誤或逾時（帳號鎖內之讀桶與推進各 1 秒上界＝`CHANGE_PWD_CACHE_TIMEOUT`；user 2026-10-12 裁定）＝放行（precheck 不拒、推進與清空略過）並計 `throttle_degraded_total{source="redis_change_pwd"}` 一格（來源 10→11）；快取自始缺席（`AppState.cache` 為 None＝測試專用形）＝放行、不計（沿 `throttle::precheck` 既有取態） |
| 射程 | ADR-00038「redis 在節流面只承載兩種鍵」限登入節流（島 E）、改密節流不在其內＝ADR-00090 決定 5 明文（照錄 ADR-00078） |

例（seed 政策；明文一律佔位、RL-0054）：
- `{"oldPassword":"<舊密碼>","newPassword":"<合政策之新密碼 A>","confirmPassword":"<同上>"}` ⇒ `0000`；alice 另一瀏覽器下一次請求 `8888`。
- 60 秒內再改（`{"oldPassword":"<新密碼 A>","newPassword":"<合政策之新密碼 B>","confirmPassword":"<同上>"}`）⇒ `{"data":{"remainingSeconds":<n>},"code":"2222","msg":"biz.user.pwdSetTooFrequent"}`（1 ≤ n ≤ 60）。
- 連續 5 次舊密錯誤後第 6 次（即使舊密正確）⇒ `{"data":null,"code":"2222","msg":"biz.user.changePasswordThrottled"}`。

前端：改密卡（舊密碼一路、無信箱與手機選項；三欄必填＋即時規則；成功後保留當前會話；FR-049）。

## 3. 錯誤明細通道信封（ADR-00076；FR-004／FR-033／FR-051）

### 3.1 射程

錯誤信封之 `data` 欄**恆在場、不省略**、其值恆 `null`；**唯二例外**：

| msg key | `data` 型 | 發出點 |
|---|---|---|
| `biz.user.passwordPolicy` | `PasswordPolicyDetail` | addUser／resetUserPassword／changePassword 之政策腿 |
| `biz.user.pwdSetTooFrequent` | `PwdSetTooFrequentDetail` | addUser（結構上恆過）／resetUserPassword／changePassword 之冷卻腿 |

其餘一切錯誤之 `data` 恆 `null`——含 `5003`（不洩差集）、`7777`（兩鍵）、`8888`、`1000`、`3333`、`4040`、`5000`、其餘 `2222` 鍵（含 `changePasswordThrottled`）。判準：明細是操作者當下修正輸入之唯一資訊（該改什麼／還要等多久）、非診斷；ADR-00014 翻案觸發器「業務錯誤明細之受眾邊界重評」由 ADR-00076 回應（`5003` 維持純 key、明細只開此二鍵）；擴第三鍵＝回 ADR-00076 判準立新 ADR。

### 3.2 data 兩形

**`{ "violations": [...] }`**：非空、不重複、元素序＝八碼宣告序、一次收集全部違規（FR-032）。觸發判準摘要（判定件 `model::password::validate_against_policy`；全文＝research R11）：

| 碼 | 違規條件 |
|---|---|
| `minLength`／`maxLength` | 字元數 ＜ 下界／＞ 上界 |
| `maxBytes` | UTF-8 位元組數 ＞ 512（字元數與位元組數雙約束） |
| `requireDigit`／`requireLowercase`／`requireUppercase`／`requireSpecial` | 開啟且不含 `[0-9]`／`[a-z]`／`[A-Z]`／`[^A-Za-z0-9]` |
| `forbidUsername` | 開啟且與帳號名不分大小寫相等 |

政策矛盾（min ＞ max）時任何密碼必違 `minLength` 或 `maxLength`＝自然全拒（ADR-00079）。

**`{ "remainingSeconds": n }`**：整數、`1 ≤ n ≤ password_change_min_interval`；`n`＝設定秒數 − ⌊距該對經手時戳之經過秒數⌋、至少 1、至多設定秒數（經手時戳在未來〔時鐘回撥〕仍屬未滿、上限取設定值）＝照提示秒數重試必過（rev5 HEAD 形補上限）。設定值 0＝停用、本鍵不發。

信封例（欄序恆 `data→code→msg`、HTTP 200）：

```json
{"data":{"violations":["minLength","requireDigit"]},"code":"2222","msg":"biz.user.passwordPolicy"}
{"data":{"remainingSeconds":30},"code":"2222","msg":"biz.user.pwdSetTooFrequent"}
```

★`data` MUST NOT 含密碼明文或雜湊、帳號名、政策現值或其他使用者資料（島 I5）。

### 3.3 後端構造與出口

- **變體**（`rust-api/server/src/error.rs`）：`AppError::BizData(Cow<'static, str>, serde_json::Value)`——`2222`、msg＝`.0`、HTTP 200；同刀另增 `AppError::ModalLogoutByAdmin`（`7777`、`auth.session.kickedByAdmin`、HTTP 200）。變體 9→11；★13 碼矩陣與可發碼集（九碼）不變（兩新變體各落既有 `2222`／`7777` 列；「變體集恰九」同批改）。
- **組裝點恰二**（`handler/user.rs`、`pub(super)`）：`password_policy_err(violations)`、`pwd_set_too_frequent_err(remaining_seconds)`——以 `PasswordPolicyDetail`／`PwdSetTooFrequentDetail` 具型組值後轉 `serde_json::Value`、鍵取 `msg_key` 常數；三入口共用、`handler/user_center.rs` 不自組。機器守：`tools/msg-key-gate.py` 斷言 2 擴認三形與分階段射程守（`contracts/code-gates.md` §2.3）；「生產構造點恰兩處、鍵恰此二」之名冊守＝`contracts/code-gates.md` §2；鍵與常數名＝`contracts/msg-keys.md` §2／§4。
- **出口唯一**：`impl IntoResponse for AppError` 為唯一分派點——`BizData`→新增 `Res::<serde_json::Value>::from_err_with_data(&e, data)`（`pub(crate)`；碼與 msg 仍取三映射）；其餘→既有 `Res::from_err`。★`Res::from_err` 對任何變體（含 `BizData`）仍出 `data: null`：攜不攜明細由變體決定、不是呼叫點之選擇（分派散給各 handler，同一變體遲早有站點走成 `from_err`、明細靜默消失）。`Res` 三欄續非 pub、`compile_fail` doctest 不動；新入口不持 wire 字面。

### 3.4 前端轉譯（`base-web/src/service/request/index.ts`；`BASE-WEB-I18N-WIRING(i)` 改寫後）

- 只在業務錯誤分支（`error.code === BACKEND_ERROR_CODE`）之 toast 鏈生效；HTTP 層錯誤分支與 `7777` 對話框分支不涉明細。
- **顯式兩鍵白名單**（非泛用插值）：`biz.user.passwordPolicy`→具名參數 `violations`＝逐碼 `$t('page.passwordPolicy.violation.<碼>', <碼>)` 以 `$t('page.passwordPolicy.listSeparator')` 串接；`biz.user.pwdSetTooFrequent`→具名參數 `remainingSeconds`＝數值原樣；譯文＝`$t('backend.<msg>', <具名參數>, <msg>)`。
- ★具名參數名＝`data` 鍵名：三檔 locale `backend` 子樹兩鍵之佔位符 MUST 恰為 `{violations}`／`{remainingSeconds}`（`rev5:B-139` 之教訓；機器守＝`contracts/msg-keys.md` §5）。
- 降級：`data` 形不合＝退回純 key 轉譯 `translateBackendMsg(msg)`；違規碼查無譯文＝顯示碼字面；白名單外之鍵一律不讀 `data`。
- 違規子鍵落 **page 樹**（FR-033）：`page.passwordPolicy.violation.<碼>` 八枚＋`page.passwordPolicy.listSeparator`、三語、單一共用命名空間（請求層、`pwd-policy` hook、產密元件共用）；`backend` 子樹只放 `MSG_KEYS` 成員（`rev5:007` 之 backend 樹九支白名單鍵不帶回）。譯文與型節＝`contracts/msg-keys.md` §3。

### 3.5 002 刀 wire 契約 §3 第 3 條之改寫對照（FR-051）

| | 字面 |
|---|---|
| 改寫前（`specs/002-system-settings/contracts/wire-settings.md` §3 第 3 條） | 信封三欄宣告序 `data→code→msg`；code 恆 string；錯誤 `data:null` 不省略；business error 一律 HTTP 200（例外僅 4040→404、5003→403）。 |
| 改寫後 | 信封三欄宣告序 `data→code→msg`；code 恆 string；錯誤信封之 `data` 欄恆在場不省略、其值恆 `null`，★唯二例外＝`2222` 之 `biz.user.passwordPolicy`（`{violations}`）與 `biz.user.pwdSetTooFrequent`（`{remainingSeconds}`）攜明細物件（ADR-00076；wire 家＝007-user-password-admin 之 `contracts/wire-user-center.md` §3）；business error 一律 HTTP 200（例外僅 4040→404、5003→403）。 |

改寫落點之處置（該檔屬 ADR-00041 決定 3 所稱已抽出節之凍結原檔）＝research R11（明細通道）；`envelope.rs` 檔頭之契約指針同批改指 ADR-00076（spec FR-051 修補後讀法）。

### 3.6 envelope 釘案改寫要點

- `envelope.rs` 檔頭「錯誤時 data 為 null 且不省略」改述為「data 恆在場不省略、其值除 `BizData` 外恆 null」；`Res::from_err` doc 補「不因變體而變」。
- 既有 `error_envelope_data_null_not_omitted` 名稱保留、改寫為逐變體表驅動（`contracts/code-gates.md` envelope 列）；新增三案：①`BizData` 經 `from_err` 仍 `data:null` ②`BizData` 經 `IntoResponse` 之本體逐位元＝`{"data":{"violations":["minLength"]},"code":"2222","msg":"biz.user.passwordPolicy"}`、HTTP 200 ③`ModalLogoutByAdmin` 經 `IntoResponse`＝`{"data":null,"code":"7777","msg":"auth.session.kickedByAdmin"}`、HTTP 200。案名實作期定。
- `error.rs` 測試：全變體窮舉見證之 match 增兩臂；「可發碼恰九、無變體碼恰四」續綠；增「`BizData` 與 `Biz` 碼與 HTTP 同、key 取 `.0`」「`ModalLogoutByAdmin` 與 `ModalLogout` 同碼異鍵」兩案。
- `no_wire_literal_lives_in_envelope_production_code` 之首／中／末三正面錨於新增 impl 後仍涵蓋整個生產區（RL-0051）。

### 3.7 連動改寫面（RL-0011 種子）

以 `python3 tools/docsync errata <詞>` 枚舉（種子：「data 恆 null」「data:null」「明細通道」「translateDetailValue」「變體集恰九」「屬後刀域、不帶」）逐處判讀：`error.rs` 檔頭、`envelope.rs` 檔頭與 `Res::from_err` doc、`request/index.ts` 之 003 刀新增型圈界內碼註（「rev6 錯誤信封 `data` 恆 null、沒有明細通道 ⇒ 只此一支 helper」）、憲法 §III.2 `BASE-WEB-I18N-WIRING` (i) 列（Amendment 改寫＝ADR-00074）、上節 002 刀契約條。

## 授權態矩陣（contract 測）

| 端點 | Super | Admin | User | 零角色自建帳號 | 未登入 |
|---|---|---|---|---|---|
| getPasswordPolicy | `0000` | `0000` | `0000` | `0000` | `8888` |
| changePassword | 通（下） | 通 | 通 | 通 | `8888` |

changePassword 一律送兩次輸入不一致之 body＝②拒 `2222 biz.user.passwordConfirmMismatch`、零寫入、不觸舊密比對亦不推進節流桶（空 body 之兩欄皆空串而相等＝②過→④舊密不符、逐跑推進 `cpwd:` 桶，15 分鐘內第 6 跑起轉 `changePasswordThrottled`＝跨跑連坐；research R15 第 5 款①）。各打 changePassword 之帳號其 `cpwd:{uid}` 鍵仍先以 tests 側 `CacheKeysGuard` 登記、案末驗缺席（推進腿被改壞那一發之還原網；鍵經 `server::cache` 公開 builder `change_pwd_key`；`contracts/code-gates.md` §5）。動詞不符＝`4040`。contract case 集與 ROUTES 恰等（61＝61）。

## 與 rev5 wire 逐欄比對

| 面 | rev5（HEAD） | rev6 本刀 | wire 差 |
|---|---|---|---|
| 命名空間與檔 | `Api.UserCenter`（`rev5-user-center.*`） | 同名（`rev6-user-center.*`） | 零 |
| `PasswordPolicyView`／`ChangePasswordReq` | 七欄／三欄 | 同 | 零 |
| changePassword 步序 | 七步 | 同 | 零 |
| 當前會話 sid 來源 | `Identity.sid`（`rev5:007` 收刀後補注入） | `Identity.sid`（本刀注入、Identity 兩欄→三欄） | 零 |
| 撤他票原語 | `revoke_others_of_user` | `revoke_others_of_user`（改為共用私有底座 `revoke_sids_of_user` 之包裝、行為零變化） | 零 |
| 改密節流 | `cpwd:{uid}`、5／900、`redis_change_pwd`（第十三源） | 同（第十一源） | 零 |
| 明細通道射程 | 收刀時兩鍵；`rev5:008` 擴第三鍵 | 兩鍵 | 零 |
| 明細型宣告 | 無具名型 | 三支具名型入受審名冊 | 零（快照多三支 definition） |
| 前端轉譯 | 泛用（任何 plain-object `data` 逐鍵插值） | 顯式兩鍵白名單 | 零（兩鍵呈現同形） |
| 違規子鍵落點 | `backend.biz.user.passwordViolation.*`＋`backend.common.listSeparator` | `page.passwordPolicy.violation.*`＋`page.passwordPolicy.listSeparator` | 零（i18n 路徑差） |
| 拒因構造／操作者缺席 log／body 標籤 | 字面形；`security.ipgate`；`user-center.change-password` | `msg_key` 常數；`security.user_center`＋`refused`；`changePassword` | 零（log 差） |

## 拒寫事件與觀測

- 新域字面（MUST 與既有各域不同字）：拒寫事件＝`tracing::error!(target: "security.user_center", refused = "request_context_absent", endpoint, uid, <本域訊息>)`、不帶 degraded 欄；body 收斂 debug 訊息＝本域 `BODY_FALLBACK_MSG`；資料庫故障＝本域 `db_failure`、落 `security.user_center` 後翻 `5000`。字面由 tasks 定。名冊同批入冊：`each_domain_keeps_its_own_log_literals` 加本域；`production_code_emits_no_degraded_field` 加 `user_center.rs`。
- 改密節流降級：`throttle_degraded_total{source="redis_change_pwd"}`（開機預註冊 0；`obs.rs` 之 `THROTTLE_DEGRADED_SOURCES` 10→11、名冊雙向守與「恰十」數量詞同批改「恰十一」；發射經既有 `throttle::warn_degraded`）；告警沿既有 `obs016-throttle-degraded`（`sum by (source)` 聚合、自動涵蓋新來源）。
- 政策壞值（ADR-00079；FR-034）：計數族 `password_policy_invalid_total`（無 label、開機預註冊 0；MUST NOT 併入 `throttle_degraded_total`）；發射出口 `obs::password_policy_invalid()` 恰一處＝單一驗證件 `validate_against_policy` 判 min ＞ max 時（只有三設密入口經過；§1 getPasswordPolicy 只經載入件、不計＝設密被拒才告警；ADR-00079 決定 5、research R11）；並落一則結構化 warn（含 min、max 現值、不含密碼）；告警規則 uid `obs016-password-policy-invalid`、title `password-policy-invalid`、expr `sum(increase(password_policy_invalid_total[5m]))`、門檻 ＞0（`deploy/grafana-provisioning/alerting/rules.yml`、依既有活體驗證慣例實測）。
- 密碼不入任何事件：本域 tracing 欄不得帶 `ChangePasswordReq` 之 `{:?}`；政策違規屬使用者輸入、不另發 warn。
