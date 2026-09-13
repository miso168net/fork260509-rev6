# Wire 契約 — auth 面（9 條）

權威＝base-web typings（憲法 §I.3 權威序 1）。信封恆 `{data, code, msg}`、`code` 為 string、業務錯誤走 **HTTP 200**；路徑不帶 `/api` 前綴（front-nginx strip；唯一入口 `http://127.0.0.1:32080/api`）。型別細節見 `../data-model.md` §11／§13、不重複。

碼表共用：`0000` 成功／`1000` 登入失敗（`auth.login.failed`）／`2222` 業務驗證（Biz 鍵）／`3333` access 過期（`auth.token.expired`）／`7777` 被踢（`auth.session.kicked`）／`8888` 會話失效（`auth.session.reLogin`）／`4040` 路徑或動詞不存在（`system.notFound`、HTTP 404）／`5000` 內部（HTTP 200）。★除 `4040`→404、`5003`→403 外一律 HTTP 200。

**三分碼射程**（research R4、兌現 ADR-00014 後果段）：`3333` 僅 access exp 過期（enforce 驗章 `ExpiredSignature`）；標頭缺席・非 Bearer・簽章不符・已撤銷・refresh 鏈失效→`8888`；被踢→`7777`。★refresh 端點自身任何驗章失敗恆 `8888`、絕不 `3333`。

## POST /auth/login（Public）

| 面 | 內容 |
|---|---|
| 授權 | Public（不掛 `enforce_mw`） |
| 請求 | `{userName, password, captchaId?, captchaCode?}`（後二為軟區才驗；非軟區時★完全忽略、不驗不消耗） |
| 成功 | `data: {token, refreshToken}`＝`Api.Auth.LoginToken` |
| 副作用 | 稽核列（成功 txn 內）＋`sys_token` active 列＋single-session 判定（登入事件）＋denylist／last_activity 起點 best-effort |

| 拒因 | code | msg key | 備註 |
|---|---|---|---|
| 帳密錯／帳號不存在／已停用 | `1000` | `auth.login.failed` | ★三態 collapse 同碼；落失敗列；查無帳號仍跑 dummy 驗章（時序等化） |
| userName（>64）／password（>512 bytes）超限 | `1000` | `auth.login.failed` | 形制閘、零稽核零驗章零計數桶 |
| 軟區（失敗 2–4）缺／錯／過期／重放 captcha | `2222` | `biz.auth.captchaRequired` | 驗章前擋、零列零桶；★該題已耗須重取 |
| 鎖定（失敗 ≥5） | `2222` | `biz.auth.locked` | 驗章前擋、零列零桶 |
| `session_idle_timeout` 缺失／壞值、commit 失敗 | `5000` | `system.internal` | 不落稽核列 |
| body rejection（JSON 壞形／缺欄） | `1000` | `auth.login.failed` | 與形制閘、loginCaptcha Query rejection 同取徑；零副作用（承 rev5） |

## POST /auth/refreshToken（**Public**）

Public 理由：設 Authed 則過期 token 永遠換不了。請求 `{refreshToken}`；成功 `data: {token, refreshToken}`（新對）。

| 情境 | code | 備註 |
|---|---|---|
| `active`＋idle 未逾時 | `0000` | rotate（舊列→`rotated`、插新 `active`）＋寫 grace 30s；新對 TTL 讀 `session_idle_timeout` 現值（clarify Q4 總則） |
| `rotated`＋grace 命中（≤30s） | `0000` | ★冪等回**既發的同一對** |
| `rotated`＋grace miss | `8888` | ★唯一觸發 reuse：撤全鏈＋落 `session_event(reuse)` |
| `revoked`＋denylist reason==`kicked` | `7777` | modal「你已在他處登入」 |
| `revoked`＋reason==`revoked` **或鍵缺席** | `8888` | ★靜默、不落事件、不重複撤（status 即權威） |
| `active`＋idle 逾時 | `8888` | 僅首次落 `session_event(idle)`；★不寫 denylist |
| 驗章失敗（過期／垃圾／錯簽）／查無列 | `8888` | ★絕不 `3333` |
| `session_idle_timeout` 缺失／壞值 | `5000` | 簽新對無輸入、fail-loud |
| body rejection（JSON 壞形／缺欄） | `8888` | 與驗章失敗同出口；★`3333` 會觸前端自動 refresh 死迴圈、`1000` 是登入語意；零 DB 零稽核（承 rev5） |

## POST /auth/logout（**Public**）

Public 理由：設 Authed 則 token 一壞就再也撤不掉那條會話。請求 `{refreshToken}`；成功 `data: null`。

| 情境 | code | 備註 |
|---|---|---|
| 驗章成功 | `0000` | 該列→`revoked`＋denylist(revoked、refresh 全壽命)＋落 `session_event(logout)` |
| 驗章失敗（垃圾／過期）／查無列／已撤 | `0000` | ★冪等 no-op、不落事件——回異碼＝token 有效性 oracle |
| body rejection（JSON 壞形／缺欄） | `0000` | 以 `Result<Json, JsonRejection>` 收、就地折成 no-op、不上浮（承 rev5） |

## GET /auth/getUserInfo（Authed）

成功 `data`＝`Api.Auth.UserInfo` 四欄皆必填：`userId`（★DB i64→字串）／`userName`（＝`nick_name` fallback `user_name`；碼中零帳號字面）／`roles`（DB-fresh）／`buttons`（Casbin `button` 維度 `get_filtered_policy` 枚舉）。
未認證面：標頭缺席／非 Bearer／簽章不符／已撤銷→`8888`；access 過期→`3333`；被踢→`7777`。

## GET /auth/loginCaptcha（Public）

| 面 | 內容 |
|---|---|
| 請求 | ★必帶 `?userName=`（challenge 綁帳號） |
| 成功 | `data: {captchaId, captchaImg}`＝`Api.Auth.LoginCaptcha`（新檔 `rev6-auth.d.ts`）；`captchaImg`＝`data:image/png;base64,…` |
| 存在性 | ★對任意 userName 一律發題（含不存在帳號）＝零存在性洩漏；不查 DB |

| 拒因 | code | 備註 |
|---|---|---|
| userName 超限（>64） | `1000` | ★與登入端點同形閘（零新碼零新 key） |
| 缺 `userName` query | `1000` | Query rejection 亦須成三欄信封 |
| 產圖／簽章內部失敗 | `5000` | captcha 字型涵蓋自證的失效出口 |

## POST /auth/{sendCaptcha,codeLogin,register,resetPwd}（Public × 4）

四端點共用一支 `not_supported_stub()`：一律 `2222`＋`biz.auth.notSupported`、`data: null`、零副作用（不落表、不查 DB、不解析請求體 ⇒ 無 body rejection 面）。前端三張表單改打此 stub、captcha hook 改打 `/auth/sendCaptcha`；第四流程（自助頁手機驗證）整頁未建。
★contract case：四支同形 ⇒ 各自斷言 path 專屬 case_key 對映（區別手法，防殭屍 case）。

## 前端接線（`rev6-auth.ts` wrapper、不入 barrel）

七支：`fetchLoginWithCaptcha(userName, password, captcha?)`（★承 rev5 同名形；未帶 captcha 時 `captchaId`／`captchaCode` 為 undefined、序列化省略 ⇒ wire 形與 upstream `fetchLogin` 全等；auth store `login()` 改 import 本支＝LOGIN-CAPTCHA(i)——upstream `fetchLogin` 為 `(userName, password)` 兩參且 data 於函式內構造、呼叫端無法擴欄，而 `src/service/api/auth.ts` 不在任何授權面）／`fetchLoginCaptcha(userName)`／`fetchLogout(refreshToken)`（best-effort、失敗不阻斷 `resetStore`）／`fetchSendCaptchaStub`／`fetchCodeLoginStub`／`fetchRegisterStub`／`fetchResetPwdStub`；消費端以直接路徑 import（沿 `rev6-settings.ts` 先例）。upstream `fetchLogin`／`fetchGetUserInfo`／`fetchRefreshToken` 不動。

**軟區換題契約**（spec FR-017／SC-005；LOGIN-CAPTCHA(i) 授權射程內）：登入頁處於軟區（曾收 `2222 biz.auth.captchaRequired`）時，任何登入失敗回應（`1000` 或再次 `captchaRequired`）後 `pwd-login.vue` MUST 重呼 `fetchLoginCaptcha(userName)` 換題並清空驗證碼輸入——後端「提交即消耗」＝該題已作廢，不換題則後續每次提交必得 `captchaRequired`；非軟區零行為變更。
