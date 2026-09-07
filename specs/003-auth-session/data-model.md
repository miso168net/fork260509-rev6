# Data Model — 003-auth-session（Phase 1）

**零 migration**：本刀所有表結構與 seed 皆在 001 基線（`docs/ops/reference-src/schema-definition.md` 為活體定稿）；本檔只描述既有結構的**行為語意**（狀態機、值域、寫入點、不變式）、redis 承載態、
`AppState`／`AppError`／ROUTES／wire DTO 的 rev6 定形。wire 逐端點形制見 `contracts/`、降級矩陣全表見 `research.md` R5、不重複。

## §1 sys_token 狀態機（隨 ADR-00026 入憲＝島 A／C）

**欄**（001 基線 9 欄、變體 C）：`id`／`created_at`／`created_by`（＝擁有者 uid）／`status`（`active`｜`rotated`｜`revoked`、碼層常數）／`token_hash`（SHA-256 hex 64、UNIQUE）／`rotation_chain`（＝`sid`＝會話身分、varchar 36）／
`issued_at`／`expires_at`／`used_at`（nullable）。★無 `last_activity` 欄——idle 時鐘只住 redis（§6）。

**DB 層護欄**：partial UNIQUE `uq_sys_token_chain_active ON (rotation_chain) WHERE status='active'` ⇒ 同鏈至多一條 active；並發 rotate 的失敗模式＝唯一鍵衝突 `DbErr`、MUST 辨識並轉 grace 冪等分支、不得籠統 `5000`。

**現態 × 事件 → 次態＋副作用**（列＝呈遞 refresh 票所對應的列狀態）：

| 現態 | 事件 | 次態 | 副作用 | 回應 |
|---|---|---|---|---|
| （無列） | refresh | — | — | `8888`（票不在狀態機內＝作廢／偽造） |
| `active` | refresh＋idle 未逾時 | 舊列→`rotated`（`used_at`＝now）；新列→`active`（同鏈、新 `token_hash`、`expires_at`＝now＋refresh_secs） | 寫 grace（30 秒、★commit 前仍持鎖時）；★次序不可反 | `0000`＋新對 |
| `active` | refresh＋idle 逾時 | 不變 | SET NX `idle-emitted` 冪等守門；僅首次落 `session_event(idle)`；★不寫 denylist | `8888` |
| `rotated` | refresh＋grace 命中 | 不變 | — | `0000`＋**既發的同一對**（冪等） |
| `rotated` | refresh＋grace miss | 全鏈→`revoked` | `revoke_family`＋落 `session_event(reuse)`＋denylist(revoked, TTL＝refresh 全壽命) | `8888`（★唯一觸發 reuse 的形） |
| `revoked` | refresh＋denylist reason==`kicked` | 不變 | — | `7777`（modal） |
| `revoked` | refresh＋reason==`revoked` **或鍵缺席** | 不變 | ★不落事件、不重複撤（status 即權威） | `8888`（靜默） |
| `active` | logout（驗章成功） | 該列→`revoked` | denylist(revoked, TTL＝refresh 全壽命)＋落 `session_event(logout)`（created_by＝本人） | `0000` |
| （任意／無） | logout（驗章失敗／垃圾票） | 不變 | ★不落事件 | `0000`（冪等 no-op） |
| `active` | 他處登入且 single-session 生效（登入事件） | 該使用者其他 sid 之 active 列→`revoked` | 逐 sid 落 `session_event(kicked, reason=single_session)`＋denylist(kicked, TTL＝refresh 全壽命)＋寫 `sys_user.session_id`＝新 sid | 被踢者下個請求得 `7777` |

**不變式**：①同鏈至多一 active（DB partial UNIQUE）②rotate 次序：先舊列轉 `rotated` 再插新 `active` ③denylist TTL＝refresh 全壽命（兩 reason 皆然）④`access_TTL ≤ N×30 < N×60 ＝ idle 門檻`（⇒ idle 觸發時 access 必已過期、idle 不寫 denylist）
⑤（clarify Q4 總則）refresh 於 `active` 腿讀 `session_idle_timeout` 現值簽新對並算 idle 門檻——既有會話最晚於下一次換發採新值、已簽發 token 的 exp 不變。

## §2 session_event（append-only 稽核；001 基線 8 欄、變體 B）

`id`／`created_at`／`created_by`（操作者 uid、nullable）／`user_id`／`sid`（varchar 36）／`event_type`（varchar 20）／`reason`（varchar 64、nullable）／`source_ip`（★`varchar(45)`、**非 INET**——與 §3 `real_ip` 型別不同、寫入不共 helper）。

| `event_type` | `reason` | `created_by` | 落列時機 |
|---|---|---|---|
| `kicked` | `single_session` | 被踢對象 uid | login 第⑨步逐 sid |
| `reuse` | — | NULL | refresh 之 `rotated`＋grace miss（唯一形） |
| `idle` | `idle_timeout` | NULL | refresh 之 idle 命中首次（SET NX 守門） |
| `logout` | — | 本人 uid | logout 驗章成功 |

★無 update／delete（變體 B 不可竄改）。★redis 狀態永不影響本表內容（缺 denylist 不落假 `reuse`）。

## §3 sys_login_attempt（節流權威源；001 基線 11 欄、變體 B）

`id`／`created_at`／`created_by`（nullable）／`success`／`attempted_user_name`／`real_ip`（**INET NOT NULL**）／`peer_ip`／`x_forwarded_for`／`ip_confidence`／`region`／`trace_id`。

**本刀寫入值**：`real_ip`＝nginx 注入的 `X-Real-IP`／`ip_confidence`＝`nginx_peer`／`x_forwarded_for`＝原文截斷 1024＋剝 CR/LF／`peer_ip`／`region`／`trace_id`＝不填（NULL）；`created_by`＝帳號查得時之 uid、查無為 NULL。★integration 直打無 nginx ⇒ 測試 MUST 顯式注入 `X-Real-IP`、不為缺席開回填值。

**落列點恰三處**（皆在 login 內；spec FR-004）：①`authenticate` Denied（外層 conn）②鎖內重驗失敗（★先 rollback 再落列於外層 conn）③成功（txn 內、與建會話原子）。**不落列四類**：形制閘超限／節流三個拒絕分支／captcha 缺錯過期重放／`5000`。寫入 best-effort：失敗只發 `degraded=db_write`。

**滑動窗計數**（唯一權威）：窗內 `success=false` 列數，下界＝`GREATEST(窗起點, 窗內最近成功的 MAX(created_at), unlock_marker)`；`unlock_marker` 本刀恆綁 SQL NULL（無寫入者、參數位保留、MUST NOT sentinel）；★子查詢必帶窗下界；reset-on-success 由查詢形免費兌現、MUST 逐字帶入不得簡化。

## §4 sys_user 的會話欄（001 基線）

| 欄 | 型 | seed 現值 | 本刀語意 |
|---|---|---|---|
| `session_policy` | `varchar(20) NOT NULL DEFAULT 'inherit'` | 三帳號皆 `inherit` | 值域＝`single`｜`multi`｜`inherit`（零 CHECK、碼層收斂＋值域測試守） |
| `session_id` | `varchar(36)` nullable | 三帳號皆 NULL | login 第⑨步寫入當前 sid（single-session 生效時）；清理還原＝置回 NULL |

**兩層政策解析**：`effective_single = session_policy=='single' || (session_policy=='inherit' && single_session_default=='on')`；`single_session_default` 讀不到→off 語意。★生效時點（Q9、入憲）：只於登入事件判定、翻轉不追溯既有會話。
seed `off`＋全帳號 `inherit` ⇒ 預設不啟用，驗收前置以 002 寫端翻 `on`、驗後翻回（§9）。

## §5 sys_menu → MenuRoute 映射（dynamic 選單）

seed 78 列；`constant` 值域 TRUE=0／FALSE=14／NULL=64 ⇒ `getConstantRoutes` 謂詞 MUST 寫 `constant = TRUE`（勿寫 `IS NOT FALSE`）、現回 `[]`。

| MenuRoute 欄 | 來源 | 規則 |
|---|---|---|
| `id` | `sys_menu.id`（i64） | ★序列化為字串（typings `id: string`；既有 `serialize_i64_as_string`） |
| `name`／`path`／`component` | `route_name`／`route_path`／`component` | 直傳；`path` 缺值兜底空字串 |
| `children` | 子樹 | 非空才插 |
| `meta.title` | `i18n_key` fallback `menu_name` | ★恆存（唯一必填 meta 欄） |
| `meta.i18nKey` | `i18n_key` | 須為前端生成鍵字面聯集之一 |
| `meta.icon`／`meta.localIcon` | `icon`＋`icon_type` | `icon_type==2` → `(None, icon)`；否則 `(icon, None)`；`icon_type` 不外洩 |
| `meta.{order,hideInMenu,keepAlive,constant,multiTab,href,activeMenu,fixedIndexInTab,query}` | 同名欄 | 全 optional、None 不序列化 |
| — | `roles` 類欄 | dynamic 模式前端忽略 ⇒ 不下發 |

**樹組裝**：DB-fresh roles → Casbin `menu` 維度 `get_filtered_policy(0, [role, "", "menu"])` 取 obj 集（`MgmtApi`、非 `enforce*`）→ 祖先包含 → 同層 `order`→`id` 升冪。**`home`**＝啟用角色（`status=1`）依 role id 升冪取首個非空 `role_home`、全空→`home`；再經兜底（驗屬可見樹之可導航葉；不屬→先序第一可導航頁）。★三 seed 角色 `role_home` 同值 ⇒ 收斂律 MUST 由碼註釘住＋一支合成多角色測試守。`buttons`（getUserInfo）＝同法取 `button` 維度 obj 集。

## §6 非 DB 承載態

**JWT Claims**（8 欄）：`uid`（i64）／`sid`（＝rotation_chain）／`jti`（per-token uuid v4）／`roles`（★僅 hint、授權恆 DB-fresh）／`iss`／`aud`／`exp`／`iat`。驗章：HS256、`leeway=0`、`validate_exp`、`set_issuer`／`set_audience`；access 與 refresh **各自秘鑰**（`JwtConfig` 兩把）。
**TTL**（N＝`session_idle_timeout` 分鐘）：`access = min(300, N×60/2)`／`refresh = N×60 + access`；N 缺失／壞值→`5000`。seed N=60 ⇒ access 300s／refresh 3900s／idle 門檻 3600s。`token_hash`＝`hex(SHA256(refresh_jwt))`。

**CaptchaClaims**（4 欄、單語境不設 `ctx`）：`nonce`／`user_name`／`exp`（＝簽發＋300 秒）／`ans_mac`＝`hex(SHA256(secret ‖ nonce ‖ lower(answer)))`；HS256 簽於 `APP_CAPTCHA_SECRET`（第三把秘鑰）；驗章不驗 iss/aud、`leeway=0`。題長 4、34 字集（小寫 a-z 去 `o`＋數字去 `0`）；`captchaImg`＝`data:image/png;base64,…`。

**redis 鍵族**（rev6 定形；字面單一來源＝`cache/mod.rs` key builder；走查工具前綴名冊亦由此現算）：

| 鍵 | 值 | TTL | 寫入點 | 讀取點 |
|---|---|---|---|---|
| `session:denylist:{sid}` | reason（`kicked`｜`revoked`） | refresh 全壽命 | logout／kick／reuse 撤銷 | enforce（每請求）／refresh |
| `session:{sid}:last_activity` | unix 秒 | refresh 全壽命（SET EX） | login ⑪（起點）／enforce 放行後 | refresh idle 判定 |
| `session:idle-emitted:{sid}` | `1` | refresh 全壽命 | refresh idle 首次（SET NX） | 同左（NX 即守門） |
| `session:rotate-grace:{token_hash}` | 新對 JSON | 30 秒 | refresh rotate（commit 前） | refresh `rotated` 腿 |
| `throttle:lock:user:{user_name}` | `1` | 900 秒（`THROTTLE_LOCK_TTL_SECS`） | precheck 鎖定判定成立時（L1 負快取、best-effort） | precheck（命中即拒、不續期） |
| `throttle:captcha:used:{nonce}` | `1` | 300 秒（＝`CAPTCHA_TTL_SECS`） | captcha 驗題（SET NX、先於答案比對） | 同左（NX 即消耗） |

★六鍵字面逐字承 rev5 `cache/mod.rs`（零差異）；不含 ip 維鍵、不含 unlock 鍵（`rev5:R3-17`）。測試鍵一律加 uniq 前綴（時戳＋pid）。

## §7 設定鍵消費表（16 鍵中本刀只活 5 個；生效時點＝clarify Q4 總則）

| 鍵 | seed | 消費事件（讀現值） | 缺鍵／壞值 | 既有會話 |
|---|---|---|---|---|
| `session_idle_timeout` | 60 | login 第⑥步（簽對）；refresh `active` 腿（簽新對＋idle 門檻） | **fail-loud `5000`** | 最晚下一次換發採新值；已簽發 token exp 不變 |
| `single_session_default` | off | login 第⑨步 | off 語意 | 不追溯（Q9） |
| `login_throttle_max_fails` | 5 | 每次登入嘗試 precheck 載入 | 退常數 5＋`settings_default` 告警 | 立即 |
| `login_throttle_captcha_after` | 2 | 同上 | 退常數 2＋告警 | 立即 |
| `login_throttle_window_minutes` | 15 | 同上 | 退常數 15＋告警 | 立即 |

★三鍵任一缺失＝整組退常數、每次載入至多一筆告警；**矛盾組合** `captcha_after > max_fails`（clarify Q3）＝整組退常數＋`settings_invalid` 告警一筆；`captcha_after == max_fails`＝合法（軟區寬度零）。走查驗收以 002 寫端翻值後還原（§9）、非 seed 變動（BL-00028 不觸發）。

## §8 降級不變式（島歸屬；全表＝research R5）

島 A（grace fail-secure）／島 B（`single_session_default` 缺鍵 off；翻轉不追溯）／島 C（status 權威、denylist fail-closed、PG 亦故障不盲放、TTL＝refresh 全壽命）／島 D（last_activity fail-open、不寫 denylist、不等式）／島 E（三區、滑動窗權威、驗章前擋零列零桶、redis 整體不可用 fail-open、L2 失敗 fail-open＋補償、captcha 標記瞬斷 fail-closed 不罰、設定鍵缺失或矛盾退常數）；跨島註＝idle 鍵缺失 fail-loud 與 E 相反；跨島總則＝消費事件讀現值、不追溯已簽發。

## §9 gate2 seed 與 runtime 寫入的相容紀律（本刀首撞）

- 真 DB 測試守衛（`test_kit` 擴充）：`SessionRowsGuard`（Drop：`DELETE FROM sys_token／session_event／sys_login_attempt` 本測試寫入列＋`UPDATE sys_user SET session_id = NULL`）＋`SequenceResetGuard`（Drop：三支 `setval('<seq>', 1, false)`）＋沿 002 `SeedRestoreGuard`（`single_session_default` 翻 on 之四欄快照還原）；panic-safe、先 arm 再改。
- 走查期（非測試）：R10 工具 `snapshot` → 走查 → 清理（同上三動作以 psql 手動或腳本執行＋redis 依前綴 DEL 本次鍵）→ `diff` rc 0 才算還原；之後才跑 `schema-gate check`。
- redis：測試前綴鍵於守衛 Drop 時 DEL；dev 走查鍵於清理步 DEL（只刪 `session:`／`throttle:` 前綴、不 FLUSHDB）。

## §10 AppState 五欄與 JwtConfig（clarify Q1）

```text
AppState { db: DatabaseConnection, enforcer: Arc<RwLock<Enforcer>>, jwt: JwtConfig, cache: Option<SessionCache>, captcha_secret: String }
JwtConfig { access_secret: String, refresh_secret: String, iss: String, aud: String }   // boot 自 config 四 getter 組裝、建好即不可變
SessionCache = redis::aio::ConnectionManager                                             // 自動重連句柄、內部 Arc 廉價 clone
```

- `cache: None` **只給測試**（快取自始缺席＝降級鏈的天然測試面）；production 恆 `Some`、boot 建連失敗 MUST fail-loud panic（否則島 C fail-closed 被開機期軟失敗旁路）。
- `state.rs` 封條：「恰兩欄」→「恰五欄（ADR 翻案）」；編譯期錨測改五欄窮舉解構（加第六欄即編譯紅）；建構點以 `grep -rn 'AppState {'` 現算（現況含測試 13 處、五檔）、U1 同批全改（research R7-12）。
- config 六 getter：`jwt_secret`／`refresh_token_secret`（`APP_JWT_JWT_SECRET[_FILE]`／`APP_JWT_REFRESH_TOKEN_SECRET[_FILE]`）／`jwt_iss`／`jwt_aud`（`APP_JWT_ISS`／`APP_JWT_AUD`）／`redis_url`（`APP_REDIS_URL[_FILE]`）／`captcha_secret`（`APP_CAPTCHA_SECRET[_FILE]`）；compose 皆已接（`rev6-admin`／`rev6-admin-web`）。

## §11 AppError 9 變體與 MSG_KEYS 13（單一來源住 error.rs）

| 變體 | code | msg key | HTTP | 本刀 |
|---|---|---|---|---|
| `Success` | 0000 | `common.success` | 200 | 既有 |
| `LoginFailed` | 1000 | `auth.login.failed` | 200 | **新** |
| `Biz(Cow)` | 2222 | 構造點字面（`biz.systemSettings.{invalidValue,notFound}` 既有＋`biz.auth.{notSupported,captchaRequired,locked}` 新） | 200 | 擴 |
| `TokenExpired` | 3333 | `auth.token.expired` | 200 | **新** |
| `ModalLogout` | 7777 | `auth.session.kicked` | 200 | **新** |
| `Logout` | 8888 | `auth.session.reLogin` | 200 | 既有 |
| `NotFound` | 4040 | `system.notFound` | **404** | 既有 |
| `PermissionDenied` | 5003 | `system.forbidden` | **403** | 既有 |
| `Internal` | 5000 | `system.internal` | 200 | 既有 |

4 保留碼（7778／8889／9998／9999）維持構造層不可發出（ADR-00023 雙錨）。`MSG_KEYS: [&str; 13]` **宣告序**＝002 既有七鍵之 `error.rs` 現行序（`common.success`／`biz.systemSettings.invalidValue`／`biz.systemSettings.notFound`／`system.notFound`／`system.forbidden`／`system.internal`／`auth.session.reLogin`）＋本刀六鍵（`auth.login.failed`／`auth.token.expired`／`auth.session.kicked`／`biz.auth.notSupported`／`biz.auth.captchaRequired`／`biz.auth.locked`）；元素一律 `msg_key::NAME` 常數引用、字面只住 `pub mod msg_key`（002「零第二份 wire 字面」不變式不動）；五個 Biz 鍵一律 `Cow::Borrowed(msg_key::NAME)` 常數形構造（跨端閘 Biz 守衛接受字面形與常數形、拒動態構造）。

## §12 ROUTES 16 條註冊表（RouteDef 六欄、每欄一行、單動詞；`ROUTES_COUNT = 16`）

| path | method | case_key | envelope_exception | protection |
|---|---|---|---|---|
| /health | GET | health | true | Public |
| /metrics | GET | metrics | true | Public |
| /systemManage/getSystemSettings | GET | get-system-settings | false | Policy |
| /systemManage/updateSystemSetting | POST | update-system-setting | false | Policy |
| /auth/login | POST | auth-login | false | Public |
| /auth/refreshToken | POST | auth-refresh-token | false | Public |
| /auth/logout | POST | auth-logout | false | Public |
| /auth/getUserInfo | GET | auth-get-user-info | false | Authed |
| /auth/loginCaptcha | GET | auth-login-captcha | false | Public |
| /auth/sendCaptcha | POST | auth-send-captcha | false | Public |
| /auth/codeLogin | POST | auth-code-login | false | Public |
| /auth/register | POST | auth-register | false | Public |
| /auth/resetPwd | POST | auth-reset-pwd | false | Public |
| /route/getConstantRoutes | GET | route-get-constant-routes | false | Public |
| /route/getUserRoutes | GET | route-get-user-routes | false | Authed |
| /route/isRouteExist | GET | route-is-route-exist | false | Authed |

- Authed＝`enforce_mw`（真驗章→denylist→推進 last_activity）、無 per-route 政策；Policy＝002 既有形；Public 不掛 authn。零新 casbin 政策列（research R13）。
- 兩道 fallback（未註冊路徑／方法不符→`4040`＋404）002 既有、覆蓋全 16 條；contract case registry 與本表 case_key 雙向對賬；四支 stub case 各以 path 專屬 case_key 對映區別（防殭屍）。

## §13 wire DTO（權威＝base-web typings；序列化邊界 i64→字串）

| DTO | 形 | 來源 |
|---|---|---|
| LoginReq | `{userName, password, captchaId?, captchaCode?}`（後二為軟區才驗；非軟區完全忽略） | 新 wrapper `fetchLoginWithCaptcha(userName, password, captcha?)`（承 rev5 形；未帶 captcha 時 wire 形與 upstream `fetchLogin` 全等；auth store `login()` 改 import 該支＝LOGIN-CAPTCHA(i)；upstream `auth.ts` 不動） |
| `Api.Auth.LoginToken` | `{token, refreshToken}` | upstream `auth.d.ts` |
| RefreshReq／LogoutReq | `{refreshToken}` | upstream `fetchRefreshToken`／新 wrapper `fetchLogout` |
| `Api.Auth.UserInfo` | `{userId: string, userName, roles: string[], buttons: string[]}` | upstream |
| `Api.Auth.LoginCaptcha` | `{captchaId: string, captchaImg: string}` | **新檔** `typings/api/rev6-auth.d.ts`（declaration merging 併入 `Api.Auth`） |
| `Api.Route.MenuRoute`／`UserRoute` | `MenuRoute extends ElegantConstRoute { id: string }`；`UserRoute { routes: MenuRoute[], home }` | upstream `route.d.ts` |
| isRouteExist | query `?routeName=`；`data: boolean` | upstream `fetchIsRouteExist` |
| 四 stub | 請求體任意（不解析）；`data: null`、`2222 biz.auth.notSupported` | 新 wrapper 四支 |

## §14 i18n backend 樹（三檔各 13 鍵；譯文權威＝contracts/msg-keys.md）

`en-us.ts`／`zh-cn.ts`：於頂層 object 插獨佔一行 `  backend: {` 起的巢狀樹（`common.success` → `backend.common.success`）；`zh-tw.ts`：新建裸 object（同樹形、不接 runtime、不標 `App.I18n.Schema`；`export default {` 換行後 `  backend: {` 獨佔一行＝跨端閘右源錨、與兩語插入錨同形）；`app.d.ts`：`App.I18n.Schema` 補 `backend` **必填**型節（結構＝13 鍵巢狀）。跨端閘攤平比對（research R9）。
