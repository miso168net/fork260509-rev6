---
section: 6
summary: 執行期情境；E3 資料管線視圖的系統層落點
rad_ai: [E3]
rad_ai_stage: 3
rev5_blueprint:
  §6 Runtime: 承襲（方針段：不變式凍結面住憲法 §I.7、本節只寫 as-built）；情境隨島進場
  信任錨與 IP 存取閘: 隨刀：憲法 §I.7 島 F 進場刀
  會話狀態機（sys_token）: 承襲（§6.1「會話狀態機——島 A～D」情境：登入簽發對→每請求驗章＋denylist→續期 rotate／grace／reuse→撤銷三型 logout／kick／idle；凍結面住憲法 §I.7 島 A～D、rev5 該子節為藍本重打字）
  登入失敗節流三區（帳號維＋來源維）: 承襲（§6.1「登入失敗節流——島 E」情境：帳號維三區 precheck→captcha gate→L1 lock／L2 count→降級七源可觀測；凍結面住憲法 §I.7 島 E、rev5 該子節帳號維部分為藍本重打字）；來源維隨島 F
  使用者域斷權與密碼三入口（007 落地）: 隨刀：憲法 §I.7 島 I 進場刀（使用者域）
---
# §6 執行期視圖

## 6.1 執行情境

不變式凍結面住憲法 §I.7（行為島 A～J、fail-* 方向）；本節只寫 as-built 執行形——模組落點、常數實值、欄與鍵名（§I.7 進場規則明文把這一類留在活書）。凍結條文一律以「主題＋落點＋指島」形給指針、不複述 MUST 文字（複述＝同一事實兩個人寫的家，Amendment 改憲法而活書靜默過期）。

情境格式（每情境一個 `###`）：

| 欄 | 內容 |
|---|---|
| 標題 | 主題＋所屬島（例：會話 rotation——島 A） |
| 參與者 | 容器類＝`C4-L2-container.md` 表首欄字面；人與外部系統＝`C4-L1-context.md` 表首欄字面；模組類＝crate 內模組路徑（如 `auth::enforce`） |
| 步驟 | 單向流、每步一行；常數實值與鍵名寫在步驟內 |
| 守門 | 釘住該情境的測試或 lint（檔名） |

情境兩則（島 A～E；藍本＝rev5 活書 §6 對應兩子節、依憲法 §I.5 重打字，去處對照表＝`docs/generated/reference/rev5-blueprint-map.md`）；碼表與 HTTP 映射的權威定義住 §8.2、enforce 驗章面四級降級的逐級方向住 §8.3，本節引用而不重新定義；各島 fail-* 方向本身的凍結面住憲法 §I.7（方向性反轉＝MAJOR），本節只寫其 as-built 落點與觸發腿。稽核資料流作為系統資料流列於情境、不歸 E3。

### 會話狀態機——島 A～D

| 欄 | 內容 |
|---|---|
| 標題 | 會話狀態機（`sys_token`）：登入簽發→每請求驗章→續期 rotate／grace／reuse→撤銷三型——島 A（token rotation）／B（single-session）／C（denylist 撤銷）／D（idle 逾時） |
| 參與者 | 管理員；`base-web`（登入頁、`service/request` 攔截器）→`front-nginx`→`rust-api`；`postgres`（`sys_token`／`session_event`／`sys_user`／`system_settings`）；`redis`（`session:*` 鍵族）；模組＝`handler::auth::{login,refresh,logout}`、`auth::enforce`、`auth::jwt`、`cache`、`model::facade::{sys_token,session_event,sys_user}` |
| 步驟 | ①登入 `POST /auth/login`（Public；`handler::auth::login` 十一步、稽核寫入點恰三）：形制閘→`RequestContext::from_headers`（缺或壞 `X-Real-IP`→5000、不回填）→節流 precheck（下一情境）→`authenticate` 三態 collapse 同一 1000（查無亦跑滿一輪 dummy argon2）→txn＋`pg_advisory_xact_lock(uid)`→鎖內重驗→`jwt::ttl_from_settings` 讀 `session_idle_timeout`（分鐘 N；access＝`min(300, N×30)` 秒、refresh＝`N×60＋access` 秒；seed N＝60 ⇒ 300／3900；缺鍵或壞值→5000 不猜）→新 sid（uuid v4）＋簽對（access／refresh 各自秘鑰、Claims 八欄、票面 `roles` 僅 hint）→`sys_token::insert` active（`rotation_chain`＝sid、`token_hash`＝SHA-256(refresh)、refresh 原文不落庫）→single-session 兩層解析（`sys_user.session_policy` single／multi／inherit × `single_session_default`；值域外或缺鍵皆 off 語意、讀 Err fail-loud）真→`sys_token::revoke_others_of_user`＋逐被踢 sid `session_event(kicked, reason=single_session)`＋`sys_user.session_id`＝新 sid→成功稽核列 txn 內→commit→best-effort：逐被踢 sid `session:denylist:{sid}`＝`kicked`（TTL＝refresh 全壽命）＋寫 `session:{sid}:last_activity` 起點 |
| | ②每請求（`auth::enforce::enforce_mw`，Authed／Policy 子 router）：Bearer→`jwt::verify_access`→三分碼→`session:denylist:{sid}` 四級降級→放行後 best-effort 推進 `last_activity`（TTL＝refresh 全壽命）→注入 `Identity{uid}`→Policy 再 `require_policy` 現查角色 |
| | ③續期 `POST /auth/refreshToken`（Public；`handler::auth::refresh`）：`jwt::verify_refresh`（refresh 秘鑰；任何失敗恆 8888、絕不 3333）→txn＋`sys_token::find_by_hash_for_update` 列鎖→依鎖住那一刻的 `status` 分流：`active`→idle 判定（`now − last_activity > refresh_secs − access_secs`＝N×60 秒→`reject_idle`：SET NX `session:idle-emitted:{sid}` 守門、僅首次落 `session_event(idle, reason=idle_timeout)`、列不動、★不寫 denylist、8888；`last_activity` 缺席或讀 Err→fail-open 續換發）→DB-fresh roles→`sign_pair`（同 sid、新 jti）→`sys_token::rotate`（★先舊列→`rotated`＋`used_at`、再插新 active）→commit 前寫 `session:rotate-grace:{token_hash}`（新對 JSON、`GRACE_TTL_SECS`＝30）→commit→0000 新對；`rotated`→grace 命中→回既發同一對（冪等）、grace miss 或讀 Err（fail-secure）→`detect_reuse`＝`revoke_family`＋`session_event(reuse)`＋denylist `revoked`→8888；`revoked`→零 DB 寫、denylist reason `kicked`→7777、其餘／缺席／Err→8888 靜默不落事件；並發 rotate 撞 partial UNIQUE→`is_chain_conflict` 重入一輪（上限 `DISPATCH_ROUNDS_MAX`＝2） |
| | ④登出 `POST /auth/logout`（Public；`handler::auth::logout`）：驗章失敗／查無列／呈遞列非 active 一律 0000 冪等 no-op、零 DB 寫、不落事件（回異碼＝token 有效性 oracle）；active→`FOR UPDATE`→`sys_token::revoke_row`（只撤呈遞列）＋`session_event(logout, created_by=本人)` 同 txn→commit 後 best-effort denylist `revoked` |
| | ⑤撤銷三型各自的態與 msg：logout→呈遞列 `revoked`＋denylist `revoked`→舊 access 8888 `auth.session.reLogin`（靜默）；kick→同帳號其他 chain 的 active 轉 `revoked`＋denylist `kicked`→7777 `auth.session.kicked`（前端 modal、按確認回登入頁）；idle→列不動、無 denylist→8888（access 必已過期）。權威恆＝`sys_token.status`、denylist 只是加速層；兩 reason TTL 皆＝refresh 全壽命；`session_event` 四 event_type（kicked／reuse／idle／logout）× 兩 reason（single_session／idle_timeout），字面單一宣告源＝`model/facade/session_event.rs` |
| 守門 | `auth/enforce.rs`、`auth/jwt.rs`、`handler/auth/{login,refresh,logout,user_info}.rs`、`model/facade/sys_token.rs` 各自 `#[cfg(test)]` 案冊（案名以檔為準；逐島代表案列 §10.2）；`tests/contract.rs`（ROUTES×case 雙向覆蓋）；`tests/entity_access_lint.rs`（facade 唯一管道）；活體走查＝`tools/walkthrough-baseline.py` snapshot→diff（RUNBOOK §9c） |

### 登入失敗節流——島 E

| 欄 | 內容 |
|---|---|
| 標題 | 登入失敗節流三區（帳號維）＋圖形驗證碼——島 E；來源維（IP 維）不在本情境、隨島 F |
| 參與者 | 管理員；`base-web`（登入頁軟區條件渲染）→`front-nginx`（邊緣 `auth_limit` per-IP 粗閘、§11.2）→`rust-api`；`postgres`（`sys_login_attempt` 滑動窗權威、`system_settings` 三鍵）；`redis`（`throttle:*` 鍵族＝L1 負快取＋captcha 消耗標記）；模組＝`throttle`、`captcha`、`handler::captcha`、`handler::auth::login`、`model::facade::{sys_login_attempt,system_settings}` |
| 步驟 | ①取題 `GET /auth/loginCaptcha?userName=`（Public；`handler::captcha::login_captcha`）：任意帳號名皆發題（零存在性洩漏）、缺 query 或帳號名逾 64 字元→1000、產圖／簽章失敗→5000；`crate::captcha::issue`＝四欄 `CaptchaClaims`（`nonce` 32 hex／`user_name`／`exp`＝now＋`CAPTCHA_TTL_SECS`＝300／`ans_mac`＝SHA-256(secret‖nonce‖lower(answer))）以第三把秘鑰 `APP_CAPTCHA_SECRET` HS256 簽成 `captchaId`、圖＝`data:image/png;base64,…`（題長 4、34 字集）；伺服器零 DB 零 redis |
| | ②login 第①步形制閘 `throttle::login_input_within_limits`：帳號名 ≤64 字元、密碼 ≤512 bytes，超限 1000、零稽核列零計數桶 |
| | ③login 第②步 `throttle::precheck` 四步（判定鍵＝`user_name` 送出原文、帳號維唯一）：(a) L1 `GET throttle:lock:user:{name}` 命中→2222 `biz.auth.locked`、★不續期；讀 Err→`redis_lock` 降級並置 `redis_down`（fail-open、節流由 L2 生效）。(b) `load_settings` 三鍵（`login_throttle_max_fails`／`login_throttle_captcha_after`／`login_throttle_window_minutes`；seed 5／2／15）任一缺列、壞值或查庫失敗→整組退常數＋`settings_default`；矛盾組合 `captcha_after > max_fails`→整組退常數＋`settings_invalid`（相等＝合法、軟區寬度零）；再以 `sys_login_attempt::count_recent_failures` 對 PG 新鮮計數（`GREATEST` 下界＝窗起點／窗內最近一次成功；unlock marker 參數位恆 `None`＝本 crate 無寫入者）；計數 Err→`db_count`、`count := 0` 放行＋`captcha_forced = !redis_down` 補償。(c) `count ≥ max_fails`→`SET EX throttle:lock:user:{name}`（TTL＝`min(窗秒, THROTTLE_LOCK_TTL_SECS=900)`；寫 Err→`redis_lock_set`、鎖由 L2 逐請求維持）→2222 locked、零稽核列。(d) `count ≥ captcha_after`→軟區、計 `throttle_soft_zone_total`（`captcha_forced` 不計入）；`required && !redis_down`→`captcha_gate` 三步固定序：帳號綁定（題之 `user_name` ≠ 送出帳號即拒）→`SET NX throttle:captcha:used:{nonce}`（TTL 300、一次性；瞬斷 Err→`redis_captcha`、拒該次不罰）→答案比對；缺／錯／過期／重放→2222 `biz.auth.captchaRequired`；`redis_down` 時 captcha 整層停用、續驗密碼；非軟區兩欄不讀不耗 |
| | ④三個拒絕分支皆以 `?` 早退於 `authenticate` 之前＝構造上零稽核列、零 argon2、零計數桶；自由區失敗才落 `sys_login_attempt(success=false)` 推進計數（寫失敗→`db_write` 降級、回應不變＝計數斷供可見）；成功列使窗下界前移＝reset-on-success |
| | ⑤降級七源統一出口 `throttle::warn_degraded`：結構化 warn（target `security.throttle`、`degraded` 欄＝source）＋`throttle_degraded_total{source}`；七值＝`settings_default`／`settings_invalid`／`redis_lock`／`redis_lock_set`／`redis_captcha`／`db_count`／`db_write`（值集單一權威＝`obs.rs` `THROTTLE_DEGRADED_SOURCES`、預註冊顯式 0） |
| | ⑥前端（BASE-WEB-LOGIN-CAPTCHA-WIRING(i)、§8.4）：登入失敗 msg＝`biz.auth.captchaRequired` 即顯驗證碼欄並取題、帳號名一變即換題、每次失敗重取新題並清空輸入（後端提交即消耗）；非軟區送出形與 upstream 全等 |
| 守門 | `throttle/mod.rs`（常數字面、三區與 TTL、驗章前擋、滑動窗 reset、重放、答錯已耗、redis 整體不可用、L2 DbErr、SET NX 瞬斷、七源各增；案數與案名以該檔案冊註為準）、`captcha/mod.rs`（往返、零 leeway、字型涵蓋）、`handler/captcha.rs`、`handler/auth/login.rs` 各自 `#[cfg(test)]` 案冊；`obs.rs` 預註冊案；`tests/contract.rs`（`auth-login-captcha` case）；活體走查（RUNBOOK §9c）以錯密碼二次進軟區驗出欄 |

## 6.2 E3 資料管線視圖

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E3 文件管線](../process/P-E3-doc-pipeline.md)。
