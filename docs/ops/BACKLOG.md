<!-- next: BL-00035 -->
# BACKLOG — 待辦

條目形 `- BL-NNNNN｜<product／governance>｜<一句話>｜<觸發條件（必填、須可到期）>`；配號取檔頭 next 後 bump、號碼永不回收；完成即刪列、git 即史（RL-0050）。
滯後項另居 `BACKLOG-DEFERRED.md`（user 拍板暫不排程；配號計入 GT-05 家族、STATE 分開計數）——查待辦全帳須兩卷併看。開放條數不設上限（觀測值、只報表；RL-0052／ADR-00011）；觸發條件寫「何時該做」、ADR 翻案觸發器寫「決定何時失效」，兩者不混。

- BL-00002｜governance｜GT-10 對 `docs/arc42/09-architecture-decisions.md` 的兩腿在首個 AI-ADR 落地（「目前無」句移除）後互斥：子項名冊腿要 `rad_ai_map` 鍵 ⊇ E5 七欄、第八腿要值＝同檔 `###`，而 E5 子項住 ADR body 的 `####`→ E5 改由 ADR 檔面守或豁免 §9 兩腿（工具改動、一正一反自證）｜觸發：首個 AI-ADR 開寫前
- BL-00003｜governance｜閘補腿群（000-r1 R1-001／R1-027／R1-C301）：GT-03 補 BL 引用存在性腿（review.to_backlog、feature_close／misc 的 backlog_add／done）、七個自稱 Day-1 的 SKIP 分支登記或改 ERROR、CLAUDE.md／憲法內容型主張零閘（主張×閘矩陣見 `docs/reviews/20260904-doc-governance.md`）→ 逐項一正一反自證；新增閘走 ADR-00004 一進一出｜觸發：下次獨立 review 輪前、或任一 lint 誤綠實例出現時
- BL-00007｜governance｜檢索性第四指標候選：冷啟動探針（命中率／平均 hops／≤3 跳比例）與否定對照題（答錯數）入 STATE 需新 generated 欄＋資料源（ADR）｜觸發：第二次獨立 review 輪
- BL-00026｜product｜server boot 沿 sea-orm 預設 `sqlx_logging`（INFO 級逐句印 SQL、compose `RUST_LOG=info` 下 boot log 首行即 sqlx notice）——rev5 以 `ConnectOptions::sqlx_logging_level(log::LevelFilter::Debug)` 降級（rev5:B-045、需具名 `log` crate），002 刀 research R1 判 `log` 為域外未進；候選＝進 `log`（lock 已有 0.4.33、零新套件）並降至 Debug、或 `sqlx_logging(false)`｜觸發：首次觀測層維護批、或 003 auth 刀 boot 鏈再動時
- BL-00027｜product｜讀端 wire 集合≠registry 鍵集：`check_type_consistency` 第③臂讓宣告集外之列（setting_type 在認識集）照常上 wire——沿 rev5 讀端只驗認識集、spec FR-009 射程外（`rust-api/server/src/validation.rs` 已自陳）；若要求「registry 集合＝wire 集合」須另立拍板｜觸發＝設定頁 view 刀進場、或 registry 鍵集首次變動時
- BL-00028｜governance｜002 刀 U3 兩份手工轉錄雙表零機器互鎖：handler `SEED_EXPECTED`↔`migration` m0002 `SEED_SYSTEM_SETTINGS`、`validation.rs` `REGISTRY`↔data-model §3——測試側只擋日後單邊漂移、擋不住初次轉錄同錯（U3 審查以 python 解析字面機器比對過一次＝全等）；改以自真源字面解析驅動期望表或加跨檔對賬測｜觸發＝m0002 seed 或 data-model §3 任一變動時
- BL-00029｜product｜寫端 `update_system_setting` 為「不對已消失的列寫入」多查一次（handler 查 setting_type 供一致性守衛、facade `update_by_key` 內再查在場）——16 鍵低頻治理端點划算（research R11 last-write-wins、不驗併發）；高頻化時改 existing 下傳＋`UPDATE … WHERE deleted_at IS NULL` 以 rows_affected 判在場、省第二次 SELECT｜觸發＝該端點轉高頻或出現併發寫入需求時
- BL-00030｜governance｜msg key 跨端閘：後端 `MSG_KEYS` 名冊 ⊆ 前端 i18n 字典（承 rev5:Lint24 形、ADR-00017 決定 3）——002 刀只閉後端側名冊（contract 雙向斷言）、跨端半邊零機器守、RUNBOOK §12 碼面閘表以註記列承載｜觸發＝首個接 i18n 的前端刀進場（該刀同批立閘、註記列轉工具檔列）
- BL-00031｜product｜settings registry 跨鍵不變式零守：`password_min_length ≤ password_max_length`、`login_throttle_captcha_after ≤ login_throttle_max_fails`、`ip_captcha_after ≤ ip_max_fails` 等成對鍵各自獨立驗證、可寫成互斥值（002 刀 validation 只驗單鍵型別與界）｜觸發＝004 ip-trust-anchor／007 user-password-admin 之消費側進場（消費側決定不變式方向與拒因）
