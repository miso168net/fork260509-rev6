---
section: 12
summary: 系統術語與 AI 術語（保留）；流程術語住 RULES 名詞段
rev5_blueprint:
  §12 名詞表: 承襲（治理詞入 §12 系統術語；會話撤銷詞組〔撤銷三型、頂替、踢除、撤銷（使用者域）〕、鎖定、IP 域詞組〔信任錨、來源信心、來源維、存取閘等〕、選單域詞組〔選單序列化域、治理域／顯示域、絕版、常量父鏈、reason gate、兩回收桶分立、casbin 判定面與判定面同步〕、授權治理詞組〔全量替換、候選集、授權撤銷、連動歸檔、受保護授權列、封死集、不可復原集、撤銷殘留〕、使用者域詞組〔停用／軟刪、重設密碼／修改密碼、包含規則、設密冷卻、改密節流、經手表〕與稽核域詞組〔存取日誌、水平線清理、手動清理、排程清理、票回收、授權對賬、清理自記列、孤兒授權列〕已入表）
---
# §12 名詞表

## 系統術語

| 術語 | 定義 | 出處 |
|---|---|---|
| 傘狀 repo | 本 repo；只記文件、spec、編排與 gitlink pin，不含子體實碼 | CLAUDE.md §1 |
| 雙身分子體 | `base-web/`、`rust-api/`：本機＝源倉的 git worktree、對外層＝submodule gitlink | CLAUDE.md §1 |
| pin | 外層 repo 記錄的子體 commit SHA；單元邊界即時 bump、GT-02 斷言＝worktree HEAD | CLAUDE.md §3 |
| 短名／長名 | 目錄與口語用短名（base-web／rust-api）；git 分支用長名（`rev6-admin-*`） | CLAUDE.md §1 |
| fork 源倉 | repo 根下 gitignored 的兩份 clone；worktree 的 `.git` 檔指向它、必須保留 | CLAUDE.md §1 |
| 基線 | base-web fork-delta「原行」的對照基準＝upstream `example` 分支 tip（bootstrap 斷言、D14）；前進＝拍板級 | 憲法 §III、CLAUDE.md §1 |
| 軌道 | 憲法 §III 授權的 base-web 改動邊界類別（預設可動／★需顯式授權） | 憲法 §III |
| `rev6-inline` 標記 | fork 改動的統一 token：修改型帶 `原行:`、新增型圈界；全 repo grep 即得 patch set | 憲法 §III |
| 島 | 具狀態機性質的行為子系統（如 token rotation）；其不變式隨所屬域的刀 brainstorm 拍板後以 MINOR Amendment 入憲法 §I.7（進場規則）——「島 X 進場刀」即指該刀 | 憲法 §I.7 |
| 事件源 | `docs/ops/events.jsonl`：五型事件（feature_close 收刀／misc 收單／review／erratum 勘誤／perf 效能資料點）的 append 型單一事實源；人讀面＝`docs/generated/` 之 MILESTONES／reference/perf／STATE／DECISIONS-INDEX | CLAUDE.md §4 |
| 對照 stack | rev5 於 `../fork260509-rev5/` 起的 dev stack（埠 2xxxx）；UI 對照基準、唯讀 | CLAUDE.md §7 |
| 會話 | 一條 `sys_token.rotation_chain`＝`sid`（JWT `sid` claim、`sys_user.session_id`、`session:*` 鍵素材三處都以它認會話）；同鏈至多一列 `active`（DB partial UNIQUE 為護欄） | `rust-api/server/src/model/facade/sys_token.rs`；憲法 §I.7 島 A |
| 憑證對 | `(token, refreshToken)`＝access（存活 `min(300, N×30)` 秒）與 refresh（`N×60＋access` 秒）兩枚 HS256 JWT、各自秘鑰簽驗（N＝`session_idle_timeout` 分鐘）；只有 refresh 以 `token_hash`（SHA-256 hex）落庫、原文不落 | `rust-api/server/src/auth/jwt.rs` |
| 態三值 | `sys_token.status`＝`active`（現行）／`rotated`（已被換發；grace 窗內同票冪等、窗外＝reuse）／`revoked`（終態、不再轉出） | `rust-api/server/src/model/facade/sys_token.rs`；憲法 §I.7 島 A／C |
| 撤銷三型 | 會話狀態機（島 A～D）依觸發機制分之三型：logout（本人、只撤呈遞列、denylist `revoked`→舊 access 8888、回登入頁並 toast、不彈 modal）／kick（single-session 頂替、撤同帳號其他 chain、denylist `kicked`→7777 modal）／idle（逾時拒換發、列不動、不寫 denylist→8888）；稽核落 `session_event`（event_type kicked／reuse／idle／logout）；★與島 I2 之「分碼三類」（依被撤者所見碼與文案鍵分＝撤銷〔`revoked`→8888〕／頂替〔`kicked`→7777〕／踢除〔`admin_kick`→7777〕）不同軸、兩詞不互用——logout 與撤銷（使用者域）同落 denylist `revoked`、kick 即頂替、idle 不寫 denylist 而不屬分碼三類、踢除不屬撤銷三型 | §6.1 會話情境與島 I 情境；憲法 §I.7 島 B／C／D／I2 |
| 頂替 | 單一會話政策下，同帳號於他處新登入時撤下該帳號既有會話（撤銷三型之 kick、分碼三類之一；撤他鏈並逐 sid `session_event(kicked, single_session)`、denylist reason `kicked`、被撤者提示鍵 `backend.auth.session.kicked`）；提示用語含「頂替」、不用「踢」字與「管理員」；★與「踢除」不同義、兩詞不互用 | `rust-api/server/src/handler/auth/login.rs`；憲法 §I.7 島 B；用語機器守＝`tools/zh-tw-lint.py` 會話用語腿（用語表之家＝該工具常數 `ADMIN_KICK_KEYS`／`MAINLAND_TERMS`、本表只指不鏡像） |
| 踢除 | 管理員結束他人全部會話（`POST /systemManage/kickUser`；同交易撤標的全部 active 票、逐 sid `session_event(revoked, admin_kick)`、不動帳號列；分碼三類之一、denylist reason `admin_kick`、被撤者提示鍵 `backend.auth.session.kickedByAdmin`、提示用語含「管理員」；Super 可被踢除、操作者不得踢除自己）；「踢」字只用於管理員踢除語境之鍵（`ADMIN_KICK_KEYS`）；★與「頂替」不同義、兩詞不互用 | `rust-api/server/src/handler/user.rs`；`specs/007-user-password-admin/spec.md` FR-030（GR2）；用語機器守＝同上 |
| 撤銷（使用者域） | 停用、刪除、管理端重設密碼、自助改密四路連帶之會話失效：同交易撤標的全部 active 票（自助改密撤本人其餘、保留當前會話）、rotated 列不動，逐 sid `session_event(revoked, <reason>)`（reason＝`user_disabled`／`user_deleted`／`password_reset`／`password_changed`）；commit 後盡力寫 denylist `revoked`→被撤者 8888 `auth.session.reLogin` 靜默；權威＝`sys_token.status`、名單只是加速層（斷權第二層＝換發活性重驗）；分碼三類之一；★與「授權撤銷」（授權列移入授權歸檔）不同物 | `rust-api/server/src/handler/user.rs`（`revoke_sessions_in_txn`／`finish_user_write`）；憲法 §I.7 島 I2 |
| grace 窗 | rotate 後 30 秒（`cache::GRACE_TTL_SECS`）的冪等窗：同票再呈遞回既發同一對、不再轉列；窗外（grace miss）＝reuse 偵測的唯一觸發形、撤整條家族 | `rust-api/server/src/cache/mod.rs`；憲法 §I.7 島 A |
| 節流三區 | 每一維（帳號維、來源維）各自的滑動窗三區；判定於每次登入嘗試以 PG `sys_login_attempt` 計數＋該維設定三鍵現值定案、快取層不持有鎖定態（無負快取、無鎖定鍵；該維解鎖標記以計數下界的形式入判）：`count < captcha_after` 自由／`captcha_after ≤ count < max_fails` 軟區（須過圖形驗證碼、否則 2222 `biz.auth.captchaRequired`）／`count ≥ max_fails` 鎖定（2222 `biz.auth.locked`）；合成＝任一維鎖定即鎖定、否則任一維軟區即要求驗證碼，兩維拒絕共用同一組 msg、不揭露觸發維度；拒絕皆在密碼驗證之前、零稽核列零計數桶 | `rust-api/server/src/throttle/mod.rs`；憲法 §I.7 島 E；ADR-00038 |
| 鎖定 | 節流第三區：某一維窗內失敗達該維 `max_fails` 時新的登入嘗試被拒；是每次嘗試由 PG 滑動窗現算的判定結果、不是一把存起來的鎖——最早一筆失敗出窗、門檻放寬、或該維寫入解鎖標記，下一次嘗試即解；不動 token、不寫 denylist——鎖的是門、已持有效憑證者照常；管理員解鎖＝`POST /systemManage/unlockLogin`（seed 預設只屬 `R_SUPER`、自 006 刀起可經端點權限彈窗授出非 `R_SUPER` 角色〔授出後：帳號維受包含規則〔007 刀 U13〕、來源維無守門＝ADR-00081 款 9 之續存半〕；UI 入口＝使用者清單列操作「解鎖登入」〔帳號維〕與 IP 規則頁表頭「解鎖來源 IP」〔來源維〕） | `rust-api/server/src/throttle/mod.rs`；`rust-api/server/src/handler/throttle.rs`；ADR-00038 |
| denylist 加速層 vs status 權威 | redis `session:denylist:{sid}`（值＝reason `kicked`｜`revoked`｜`admin_kick`、TTL＝refresh 全壽命）只是每請求的加速判定；定案恆＝`sys_token.status`——鍵缺席＝未撤放行、鍵不可讀退 PG 查鏈上是否仍有 active、兩者不一致以 status 為準、`revoked` 列缺鍵靜默 8888 不落假 reuse | `rust-api/server/src/auth/enforce.rs`；憲法 §I.7 島 C |
| idle 逾時 | 換發時距 `session:{sid}:last_activity` 逾 `refresh_secs − access_secs`（＝N×60 秒）即拒；時鐘只住 redis、由 enforce 放行後推進、換發端點自身不推進；不可讀＝fail-open | `rust-api/server/src/handler/auth/refresh.rs`；憲法 §I.7 島 D |
| 降級（基礎設施） | 本系統確定性本體的降級：redis／PG／設定鍵不可用時依憲法 §I.7 各島拍板的 fail-* 方向走保守腿（denylist 讀不到退 PG＝fail-closed、`last_activity` 讀不到續換發＝fail-open、節流三鍵缺失整組退常數…）；二軌可觀測面覆蓋不等寬——軌道①結構化 warn（target `security.session`／`security.throttle`／`security.trust`／`security.ipgate`、`degraded` 欄即腿名）是每條具名腿的共同軌，軌道②計數器只有 `throttle_degraded_total`（節流降級源＝登入節流兩維＋改密節流；值集＝`obs.rs` `THROTTLE_DEGRADED_SOURCES`）、`denylist_hit_total`（enforce 驗章面 denylist 二源）與 `ip_domain_degraded_total`（IP 域降級源＝信任模型載入三腿、規則集初載／重載、門鈴發布／訂閱、請求上下文缺席；值集＝`obs.rs` `IP_DOMAIN_DEGRADED_SOURCES`）三支（`throttle_soft_zone_total` 計的是軟區命中、`ipgate_blocked_total` 計的是存取閘阻擋，兩者皆不屬降級），`last_activity_read`／`grace_read`／`grace_write` 等其餘腿只查得到事件、無計數序列可撈（逐腿覆蓋＝§6.1、§8.3 與各該 fn doc；enforce 放行後推進 `last_activity` 的 best-effort 寫入兩軌皆無、語意見其碼註）；★與下表 AI 術語「降級輪廓」（AI 元件不可用或低信心時的行為型錄）不同義、兩詞不互用 | §8.3、§10.2；`rust-api/server/src/obs.rs` |
| 信任錨 | 把「傳輸層對端」與「轉發鏈標頭」還原成「真實來源位址＋來源信心」的純函式判定（三層＋兩覆蓋＋溢出短路；零 I/O、零狀態）；來源維度一切機制（存取閘、來源維節流、稽核落列、防自鎖）的唯一位址輸入；受信集與跳過集由同一 helper 導出 | `rust-api/server/src/trust/mod.rs`；憲法 §I.7 島 F 之 F4／F6；§6.1 |
| 來源信心 | 信任錨對「這個真實來源位址多可信」的結論標籤＝稽核欄 `ip_confidence` 的值域，八態字面單一出口 `trust::Confidence::as_str`（`cdn_verified`／`proxy_clean`／`direct`／`cdn_anchored`／`proxy_soft`／`cdn_mismatch`／`fallback`／`chain_rejected`）；前七態＝三層判定與兩覆蓋的出口，第八態是套在其後的溢出短路標記——語意是「這條鏈逾上界、未被推理採信」而非「請求未被服務」（`sys_login_attempt` 上恆為被拒列、`sys_operation_log` 上是標記但照常服務，分表判讀）；★與下表 AI 術語「信心規格」（對 AI 輸出品質的可量化承諾）不同義、兩詞不互用 | `rust-api/server/src/trust/mod.rs`；ADR-00037 |
| 來源信心態 `fallback` | 來源信心第七態：整鏈受信、或位置錨左側無可取段時退回傳輸層對端的結論（最低；通道覆蓋可在此態上改採訪客位址、信心不升）；請求上下文缺席退路組出的那一份亦標此態；★與下表 AI 術語「fallback」（降級輪廓中實際採用的行為、流程層）不同義、兩詞不互用——文件寫此態一律反引號碼識別字並冠「來源信心態」（上一列「來源信心」的八態值域列舉＝值域定義自身、不套此形）；★同名第三義＝axum `Router::fallback` 的「兩道 fallback」（未註冊路徑／方法不符、皆回 `4040`；§5.2），指路由兜底臂、亦非本條所指 | `rust-api/server/src/trust/mod.rs`；`rust-api/server/src/request_context.rs` |
| 判定窗 | 轉發鏈最右 `MAX_XFF_TOKENS`（32）個非空欄＝信任錨實際推理所看的那一組欄；稽核欄 `x_forwarded_for` 轉錄的即是它（`trust::decision_window`：與判定軌共用同一份切分、`", "` 接回、`XFF_MAX_CHARS`＝1024 字元兜底留最右端）；複驗性帶兩個成立條件（真實來源由鏈推導／窗未逾字元上限）、不是無條件保證 | `rust-api/server/src/trust/mod.rs`；憲法 §I.7 島 F 之 F8；ADR-00037 |
| 存取閘 | 請求層的 IP 存取判定（`middleware::ip_gate_mw`＋`ipgate::decide`；同義註＝閘門、IP 閘）：六步固定判定序、any-match 集合語意（白＞黑＞預設放行、與載入順序無關）、每請求零外部查詢；阻擋＝`5003`／HTTP 403、只擋該次請求、不撤會話不寫 denylist；全鏈 fail-open | `rust-api/server/src/middleware/mod.rs`；`rust-api/server/src/ipgate/mod.rs`；憲法 §I.7 島 F 之 F1～F3 |
| 結構豁免 | 存取閘判定序第③步恆放行的六段（v4／v6 loopback、RFC1918 三段、RFC4193 ULA；`ipgate::STRUCTURAL_EXEMPT`）：先於兩袋、任何規則都蓋不掉，保住基建自身與內網救援路徑；只豁免「阻擋」、不豁免來源維節流 | `rust-api/server/src/ipgate/mod.rs`；憲法 §I.7 島 F 之 F1／F5 |
| 顯式放行 | 來源位址命中 allow 規則（落在 `RuleSet::allow` 任一段）；效果＝存取閘放行（白＞黑）且來源維節流整層跳過；判定直讀放行袋、不經 `ipgate::decide`（後者對結構豁免段也回放行、分不出兩者） | `rust-api/server/src/ipgate/mod.rs`；`rust-api/server/src/handler/auth/login.rs`；憲法 §I.7 島 F 之 F5 |
| 防自鎖 | IP 規則四寫端的寫前守門：以交易內現讀的現役列套上本次變更組出「變更後規則集」，對操作者當下的真實來源跑存取閘的同一支 `ipgate::decide`（`would_self_lock`）；結論為阻擋→2222 `biz.ipRule.selfLock`、零落庫零重載；操作者來源取不到→`5000` 拒寫（不跳過檢查、不補佔位位址）＝島 F 兩處 fail-closed 之一 | `rust-api/server/src/handler/ip_rule.rs`；`rust-api/server/src/ipgate/mod.rs`；憲法 §I.7 島 F 之 F3 |
| 來源維 | 登入失敗節流的第二個計數維度：以信任錨還原的真實來源位址（歸入計數桶）為鍵，與帳號維並列判定、合成；計數下界恰兩源（窗起點／解鎖標記）、成功登入不重置；文件一律稱「來源維」，碼識別字維持 `ip`（`DIM_IP`、`ip_bucket`、設定鍵 `ip_*`） | `rust-api/server/src/throttle/mod.rs`；憲法 §I.7 島 E、島 F 之 F4／F5 |
| 計數桶 | 一維的計數身分：來源維＝`throttle::ip_bucket` 單點導出的網段（先折疊 IPv4-mapped；v4 逐位址 `/32`、v6 聚合至 `/64`；未指定位址無桶＝該維整層跳過），快取鍵與計數 SQL 共用此值；帳號維＝送出的帳號名原文（大小寫敏感、零正規化） | `rust-api/server/src/throttle/mod.rs` |
| 解鎖標記 | 某帳號名或某計數桶「自此刻起重新計數」的時點：redis 鍵 `throttle:unlock:user:{name}`／`throttle:unlock:ip:{bucket}`、值＝unix 秒十進位字串（不可解析視為無標記）、存活 1440×60 秒；寫入者＝解鎖端點（稽核列落定之後才寫）、讀者＝`throttle::precheck` 第一步（作該維滑動窗下界之一；讀取 `Err`＝視為無標記＝fail-closed，並兼作本次嘗試的快取可用性判定）；遺失的後果＝至多少解鎖一次、可再解鎖自癒 | `rust-api/server/src/cache/mod.rs`；`rust-api/server/src/handler/throttle.rs`；憲法 §I.7 島 E；ADR-00038 |
| 選單序列化域 | 選單樹五寫端（新增／更新／刪除／批刪／復原）、角色刪除家族（刪除／批刪）與選單維／按鈕維授權寫端（updateRoleMenu／updateRoleButton）互斥執行的交易級 advisory 鎖域：key＝`MENU_DOMAIN_LOCK_KEY`（`0x7265_7636_6D65_6E75`＝ASCII `rev6menu`）、入域＝交易擁有者內層首句、commit 或 rollback 即釋放；域內鎖標的並重驗全部守門後才落寫（lock-then-redecide）；固定鎖序與 key 空間分立見 §6.1 島 H 情境①；角色新增／更新／首頁寫、端點維授權寫端與授權回收桶復原不入域 | `rust-api/server/src/model/facade/sys_casbin_archive.rs`；憲法 §I.7 島 H1／G5；ADR-00043 決定 8；ADR-00044 決定 1 |
| 治理域／顯示域 | 選單讀端的兩個謂詞域：治理域＝未軟刪全集（含停用；授權候選與映射〔三維授權之選單維候選與 id↔路由名映射、按鈕維候選聯集 `getAllButtons`、選單維與按鈕維現況讀之收窄〕、管理清單、父選擇器之輕量樹〔兼選單維授權候選讀端〕、寫端守門快照、按鈕碼絕版判定之聯集）；顯示域＝啟用且未軟刪（使用者路由、常量路由、頁面下拉、路由存在查詢）；兩域謂詞各住 facade 一處；治理用途誤用顯示域＝把停用靜默升級為撤銷 | `rust-api/server/src/model/facade/sys_menu.rs`；憲法 §I.7 島 H4 |
| 絕版（按鈕碼） | 某按鈕碼於選單編輯時自清單移除後，不再屬任何其他未刪選單（含停用＝治理域、排除標的自身）之按鈕碼聯集；絕版碼之按鈕維政策同交易移入授權歸檔（reason `menu_button_removed`；移除集觸及受保護按鈕維授權列之碼者已先整筆拒〔ADR-00086〕、故不及受保護列）、非絕版移除不歸檔；刪除選單時之對應概念＝獨有按鈕碼（刪後不再屬任何未刪選單者；reason `menu_soft_delete`、批刪逐標的於其歸檔時點現算） | `rust-api/server/src/model/facade/sys_menu.rs`（`obsolete_codes`）；憲法 §I.7 島 H2 |
| 常量父鏈 | 常量選單（`constant=TRUE`、經免認證的常量路由端點下發）之全祖先皆須常量——否則非常量父目錄以祖先身分隨樹經免認證端點流出；寫端於新增、改父、設為常量、復原常量標的時驗全祖先常量性（沿治理域上溯、逾上限或鏈斷保守拒），清除自身常量性時反查未刪常量後代；違反拒 `biz.menu.constantParent` | `rust-api/server/src/model/facade/sys_menu.rs`（`GovernedMenus`）；憲法 §I.7 島 H3／H5 |
| reason gate | 授權歸檔列可否復原的單點判定 `sys_casbin_archive::is_non_restorable_reason`：歸檔原因六值中不可復原集五值＝連動歸檔三值 `role_soft_delete`／`menu_soft_delete`／`menu_button_removed`＋選單維與按鈕維之授權撤銷 `menu_revoke`／`button_revoke`，唯一可復原者＝端點維之授權撤銷 `endpoint_revoke`——刪除連動與絕版歸檔之授權不得經授權回收桶回灌（島 H2「歸檔不可回灌」半邊）、角色刪除之連動歸檔亦然（島 G3）；生產呼叫點＝授權回收桶復原第①腿與清單可復原旗標之①半（同判準），成員集由該檔案釘住 | `rust-api/server/src/model/facade/sys_casbin_archive.rs`；憲法 §I.7 島 H2／G3；ADR-00044 決定 3；ADR-00065 決定 1 |
| 選單回收桶 vs 授權回收桶 | 兩者分立、不共用端點與判定：選單回收桶＝已刪選單清單（getDeletedMenus）＋復原（restoreMenu：域內鎖列重驗、成對清空軟刪欄、原狀態保留、零授權回灌、零判定面同步＝島 H5），UI＝選單頁「顯示已刪除」開關；授權回收桶＝授權歸檔表 `sys_casbin_policy_archive` 之讀端（getArchivedPolicies：分頁、來源角色代碼與維度兩篩、逐列可復原旗標）與單列復原（restorePolicy：受 reason gate 擋、鎖內固定序五腿、回插為一次新授予事件、不入選單序列化域、Applied 才同步判定面），UI＝授權回收桶頁；角色無回收桶（角色刪除單向） | §6.1 島 H／島 G 情境；憲法 §I.7 島 H2／H5／G3／G5；ADR-00044 決定 3；ADR-00065 |
| casbin 判定面 | 記憶體中的 casbin `Enforcer`（`AppState.enforcer`、`tokio` 讀寫鎖包覆）＝授權真相 `casbin_rule` 的全量導出；單一判定進入點 `enforce_role_path_method`、使用者路由之 menu 維可見集與按鈕碼皆讀它；★「判定面」一詞另指 IP 域之規則集判定面（`ipgate`、`ArcSwap<RuleSet>`）與登入節流判定面（ADR-00038），三者同詞異物、互不代稱；本表以限定詞區分，活書與 RUNBOOK 各處多依所在情境省略限定詞、由上下文判讀所指（§6.1 島 G／島 H 情境、RUNBOOK §11.2／§13 所稱者＝casbin 判定面；§6.1 島 F 情境所稱者＝IP 規則集判定面） | `rust-api/server/src/auth/enforce.rs`；`rust-api/server/src/state.rs`；ADR-00043 |
| 判定面同步（vs IP 規則熱重載） | casbin 判定面同步＝觸發矩陣內之寫端 commit 後以 `reload_enforcer` 自 `casbin_rule` 全新重建、於寫鎖內一步換上（觸發三類＝移除面成功且實際歸檔 ≥1 列／授予面 Applied 即觸發、不問 diff〔含空 diff〕／復原 Applied；失敗保留上一份、至多 3 次、全程互斥、單一行程前提；commit→換上之過渡窗與重試耗盡窗＝已知降級窗兩類；結果計 `casbin_reload_total{outcome}`＝同步結果計數、非降級序列）；IP 規則熱重載＝規則寫端 commit 後 `ipgate::reload_and_publish` 重讀換版並按門鈴 `ipgate:invalidate`、各行程 watcher 補讀（失敗沿用上一份、計 `ip_domain_degraded_total`）。兩者同為「DB 真相→記憶體投影、失敗沿用上一份」，觸發面、互斥件、跨行程通知與可觀測序列皆不同、互不代稱 | ADR-00043；ADR-00067；§6.1 島 G／島 H／島 F 情境 |
| 全量替換 | 三維授權寫端（updateRoleMenu／updateRoleButton／updateRoleEndpoints）之寫入語意：請求帶該角色該維之期望全集，系統於標的角色列鎖內與現況比對導出撤銷集＝（現況 ∩ 候選集）−期望、新授集＝（期望 ∩ 候選集）−現況，撤銷先於授予落寫；不提供逐項增減、差量提交或版本比對介面；期望集鍵必填——明確空陣列＝合法全撤、鍵缺席或拼錯＝body 壞形、收斂成查無角色（`biz.role.notFound`）；Applied（含空 diff）回撤銷數、新授數與生效集合（orphan skip 後之期望集）；同一角色同一維之並行編輯＝後送出者整份覆蓋（ADR-00081 款 11） | `rust-api/server/src/model/facade/sys_casbin_policy.rs`；ADR-00066 決定 1／2／6／7 |
| 候選集 | 三維授權之可操作射程、與判定面同源：選單維＝治理域（未刪、含停用）選單之路由名集（期望以選單 id 收、經同一次治理域讀映射）、按鈕維＝治理域選單按鈕碼聯集（getAllButtons）、端點維＝`router::policy_endpoints()`＝路由表中政策保護條目之（路徑, 方法）（getAllEndpoints）；候選集＝寫端射程＝現況讀端射程＝候選讀端回應——候選外期望項靜默略過（orphan skip）、候選外現役列不撤不授不入生效集合；已知偏差＝選單維候選讀端不呈現成環列及其子孫；★誤用顯示域（啟用且未刪）取候選或映射＝把停用升級為撤銷或使授權不可治理（島 H4） | `rust-api/server/src/model/facade/sys_casbin_policy.rs`；`rust-api/server/src/router.rs`；ADR-00066 決定 2～5／9 |
| 授權撤銷 | 經三維全量替換自角色移除之授權：該列移入授權歸檔（完整快照＋來源角色 id＋原因值＋歸檔者，同交易一插一刪＝撤銷必歸檔），原因值依維度＝`menu_revoke`／`button_revoke`／`endpoint_revoke`；撤銷集觸及受保護授權列＝整批拒（`biz.role.protectedRevoke`）；只有端點維之授權撤銷可經授權回收桶復原；★與「撤銷三型」（會話之 logout／kick／idle）不同義、兩詞不互用 | `rust-api/server/src/model/facade/sys_casbin_archive.rs`（`archive_revoked_policies`）；憲法 §I.7 島 G2／G3；ADR-00065 決定 1 |
| 連動歸檔 | 刪除類寫端同交易把標的連帶之授權移入授權歸檔：刪角色＝`v0` 為該角色代碼之全三維（含受保護授權列；`role_soft_delete`）、刪選單＝其路由名之選單維（跨全角色）與其獨有按鈕碼之按鈕維（`menu_soft_delete`）、選單編輯移除絕版按鈕碼＝該碼之按鈕維（`menu_button_removed`）；三原因皆屬不可復原集；移除面之同步觸發門（成功且實際歸檔 ≥1 列）所數者即本歸檔之實際列數 | `rust-api/server/src/model/facade/sys_casbin_archive.rs`；憲法 §I.7 島 G3／H2；§6.1 島 H 情境③ |
| 受保護授權列 | `casbin_rule` 中 `protected=TRUE` 之列（seed 基線層級之決定；m0003 起 seed 下恰 25 列、皆屬 `R_SUPER`＝端點維 15〔即封死集之 seed 成員〕／選單維 4／按鈕維 6〔`role:add`／`role:edit`／`role:delete`／`menu:add`／`menu:edit`／`menu:delete`；m0003 改受保護＝ADR-00085〕）：撤銷集觸及即整批拒、零變更；選單編輯之按鈕碼移除集（含改碼之舊碼）觸及受保護按鈕維授權列之碼即整筆拒（`biz.menu.protectedButtonRemove`；ADR-00086）；設定或解除受保護旗標之能力經一般管理介面永不提供（授予與復原之 INSERT 一律顯式寫 `protected` FALSE）；三維現況讀端逐項帶受保護旗標、授權彈窗鎖定該項；★與「受保護選單」（`sys_menu.protected`；島 H3 之不可刪、不可停用、不可改父）不同物 | `rust-api/server/src/model/facade/sys_casbin_policy.rs`；憲法 §I.7 島 G2；ADR-00064 決定 4；ADR-00086 |
| 封死集 | 現役授權列中滿足 `ptype='p' ∧ protected=TRUE ∧ v2 ∈ HTTP 方法白名單` 之（路徑, 方法）集合（謂詞式、不問 `v0`、不寫列數；鎖內以資料庫現況現查＝`sys_casbin_policy::protected_endpoint_set`、白名單＝`router::endpoint_methods()`）：非 `R_SUPER` 角色不得持有其成員——掛點恰兩處＝updateRoleEndpoints 之授予判定（`biz.role.protectedGrant`）與授權回收桶復原第③腿（`biz.policy.notRestorable`），`R_SUPER` 標的豁免；選單維之受保護列不在射程（可授可見性、該頁之封死集端點仍拒＝ADR-00081 款 10）；路由表之政策保護端點扣掉封死集＝可授出集（ADR-00081 款 9） | `rust-api/server/src/model/facade/sys_casbin_policy.rs`；憲法 §I.7 島 G6；ADR-00064 決定 1～3 |
| 不可復原集 | 歸檔原因中不得經授權回收桶回灌之五值＝`role_soft_delete`／`menu_soft_delete`／`menu_button_removed`／`menu_revoke`／`button_revoke`（判定單點＝reason gate）；可復原恰一值 `endpoint_revoke` ⇒ 選單維與按鈕維之授權撤銷在授權回收桶只剩閱覽（恢復＝於授權彈窗重勾；ADR-00081 款 15）、授權回收桶復原之該兩維分支結構性不可達 | `rust-api/server/src/model/facade/sys_casbin_archive.rs`；憲法 §I.7 島 G3／H1／H2；ADR-00065 決定 1／2 |
| 撤銷殘留 | 被撤之端點於判定面已知降級窗內仍放行：①commit→換上之有界過渡窗（其他並行請求讀舊面、換上即止）②重試耗盡窗（舊面續用至下次任一成功同步或重啟 rust-api）；對向症狀＝授予面反向症狀（剛授予或剛復原之端點仍回 `5003`）；前提＝單一 rust-api 行程；分診與處置＝RUNBOOK §13；與「孤兒授權列」（授權真相中失去對象之列、由授權對賬計數）為兩件事 | ADR-00067 決定 6；憲法 §I.7 島 G1；§6.1 島 G 情境⑥ |
| 停用／軟刪 | 停用＝`sys_user.status` 轉停用（wire `'2'`；列仍在、可再啟用、再啟用不撤票）；軟刪＝成對寫軟刪時間與軟刪者（自現役面消失、經回收桶可復原、狀態保留）；兩者皆同交易撤標的全部 active 票（撤銷〔使用者域〕）、登入與換發皆判不活；軟刪另同交易硬刪其全部角色指派、復原零回灌指派（須重新指派）、同帳號名重建之新帳號不繼承舊實例角色；前三個 seed 帳號不可刪、Super 不可停用 | `rust-api/server/src/handler/user.rs`；憲法 §I.7 島 I2／I3／I4 |
| 重設密碼／修改密碼 | 重設＝管理員對他人（`POST /systemManage/resetUserPassword`：不驗舊密碼、撤標的全部 active 票、設密冷卻鍵＝（標的, 操作者）、對自己即拒並改道個人中心）；修改＝本人對自己（`POST /userCenter/changePassword`：驗舊密碼、受改密節流、撤本人其餘 active 票而保留當前會話、設密冷卻鍵＝（本人, 本人））；兩者與新增帳號之初始密碼共用政策單一驗證點與經手表 | `rust-api/server/src/handler/user.rs`；`rust-api/server/src/handler/user_center.rs`；憲法 §I.7 島 I2／I3／I5 |
| 包含規則 | 使用者域寫端之請求級授權約束 `T ⊆ A ∧ N ⊆ A`：A＝操作者現役角色集（濾軟刪與停用、同交易現讀；持 `R_SUPER`＝全集）、T＝標的全部指派（停用角色照計）、N＝寫後標的角色集（不動指派＝T）；判定純函式 `auth::no_escalation::assert_no_escalation`、包裝 `handler::user::guard_no_escalation` 於標的鎖內、任何寫入前呼叫；九消費點＝使用者管理面八寫端＋帳號維解鎖（自助改密與來源維解鎖不套）；違者 `5003`、純 key、零變更零稽核；seed 保護與本人規則先於本規則；前端不預判；與封死集正交；中介層 no-escalation 掛點恆放行（射程分工）；文件用語取「包含規則」、碼識別字維持 `no_escalation` | `rust-api/server/src/auth/no_escalation.rs`；`rust-api/server/src/handler/user.rs`；憲法 §I.7 島 I7；ADR-00075 |
| 設密冷卻 | 同一（標的, 操作者）對兩次設密之最小間隔：秒數＝設定鍵 `password_change_min_interval` 現值（0＝停用；壞值退 seed 值 60）、料源＝經手表該對之上次設密時刻；resetUserPassword 以（標的, 操作者）判、changePassword 以（本人, 本人）判、addUser 不判而照落經手列；未滿＝2222 `biz.user.pwdSetTooFrequent`＋剩餘秒數明細；判在政策之後（政策不合者先報政策） | `rust-api/server/src/model/password.rs`（`cooldown_remaining_secs`）；ADR-00090 |
| 改密節流 | 自助改密之舊密碼猜測節流：判定鍵＝uid、計數載體＝redis 桶 `cpwd:{uid}`；窗內舊密比對失敗達 5 次後，其後請求於舊密比對之前即拒（2222 `biz.user.changePasswordThrottled`、純 key、不洩剩餘時間）；窗 900 秒自最後一次失敗起算、到期自癒、無解鎖端點；判讀與推進皆在帳號鎖內；redis 故障＝fail-open＋降級源 `redis_change_pwd`；★與登入失敗節流（「節流三區」「鎖定」）分家——判定鍵、真源、語意分區與門檻來源皆異 | `rust-api/server/src/throttle/change_pwd.rs`；ADR-00090 |
| 經手表 | `sys_pwd_custody`：一列＝（標的, 操作者）一對之上次設密時刻；三設密入口成功即同交易 upsert（`touch`，時戳取應用層現刻）；語意限縮為設密冷卻之料源、不做經手判定、不設刪除出口；走查還原清理面成員 | `rust-api/server/src/model/facade/sys_pwd_custody.rs`；ADR-00090 |
| 存取日誌 | `sys_access_log`：已認證請求之觀測軌跡，由統一記錄層 `middleware::access_log_mw` 寫入（掛 Authed 與 Policy 兩受保護子 router 之 `enforce_mw` 內側；Public 子 router、兩道 fallback 與被 IP 存取閘擋下者不經記錄層）——通過驗章之請求依 ADR-00100 落一列（含授權拒絕 `5003`＝403；寫入失敗 fail-open；回應產生前即被丟棄之請求零列；停機在途之寫入可能缺列〔等候許可者零列、寫入中者視 INSERT 是否已送達庫端而定、已送達者仍可能落列而照計失敗〕＝ADR-00100 後果之已知態）；欄＝操作者、方法、路徑（不含 query、不讀 body）、HTTP 狀態碼、來源四欄（信任錨結論）；狀態欄只見 200 與 403；★消歧：活書各處「零稽核（列）」指業務稽核表之列——寫端語境＝操作稽核 `sys_operation_log`、登入節流判定語境（§6.1 島 E 情境之形制閘與拒絕分支、詞條「節流三區」、§5.2 login 接線段、§10.2 島 E 情境）＝登入嘗試 `sys_login_attempt`；存取日誌屬統一記錄層、不入「零稽核」之計 | `rust-api/server/src/middleware/mod.rs`；`rust-api/server/src/model/facade/sys_access_log.rs`；憲法 §I.7 島 J2；ADR-00100 |
| 水平線清理 | 稽核四表（操作日誌／存取日誌／登入嘗試／會話事件）唯一之刪除形：`created_at` 早於（交易時戳 − 保留天數）之列整段刪除、構造上禁挑列；保留天數下限 `PURGE_MIN_DAYS`＝30（碼內單一權威）；操作日誌源固定豁免清理自記列；刪除與自記同交易、自記失敗整筆回滾；單一實作＝retention 共用核 `purge_with_self_record`（手動清理與排程清理同一條規則） | `rust-api/server/src/model/retention.rs`；憲法 §I.7 島 J3 |
| 手動清理 | 稽核頁清理浮層經 `POST /systemManage/purgeAuditLog`（`handler::audit::purge_audit_log`）發動之水平線清理：固定序＝表名白名單→天數下限（拒＝`biz.audit.purgeBelowFloor` 攜 `{minDays}`）→操作者（上下文缺席＝`5000` 拒寫），三步皆不觸庫、任一拒＝零刪除零自記；自記列操作者＝請求者、來源欄轉錄請求上下文；端點 seed 只授 `R_SUPER`、可經端點權限彈窗授出，按鈕碼 `audit:purge` 只管顯隱 | `rust-api/server/src/handler/audit.rs`；憲法 §I.7 島 J3；ADR-00102 |
| 排程清理 | reaper `audit-retention` job（`reaper::run_audit_retention`）依固定表序逐表經同一支共用核清理（每表一交易）：保留天數＝四個環境變數、三分語意（缺席＝90、畸形＝warn 後 90、低於下限或逾 i64 上界＝四鍵全驗後前置全拒）；自記列操作者空、來源位址＝無網路來源之哨兵 `0.0.0.0`、`payload_after` 另帶 `job`（只經 `SystemJob` 與 `sys_operation_log::write_system_in_txn` 構造）；缺 `--execute`＝dry-run 只計數 | `rust-api/server/src/reaper.rs`；`rust-api/server/src/model/audit.rs`；憲法 §I.7 島 J3；ADR-00101 |
| 票回收 | reaper `token-reap` job（預設 job）：刪除過期逾寬限（`REAPER_GRACE_DAYS`、缺席或畸形取 7 天）之 `sys_token` 列、不分 status（execute＝`sys_token::reap_expired` 單一 DELETE、dry-run＝同判準計數）；屬會話域、不落操作日誌自記、不經 retention 共用核 | `rust-api/server/src/reaper.rs`；`rust-api/server/src/model/facade/sys_token.rs`；ADR-00101 決定 3 |
| 授權對賬 | reaper `policy-reconcile` job（`reaper::run_policy_reconcile`）：於可重複讀唯讀交易內計數三維孤兒授權列、只報不刪——有無 `--execute` 皆零寫入（`mode` 只決定事件與心跳標籤）；結果經心跳 `reaper_orphan_policies{dimension}` 與告警 `obs017-policy-reconcile-orphans`；處置＝RUNBOOK §8.1 | `rust-api/server/src/reaper.rs`；ADR-00101 決定 6 |
| 清理自記列 | 每次水平線清理同交易落之一列操作日誌：`operation`＝`purge`、`entity_table`＝目標表名、`entity_id` 空、`payload_after`＝`{table, before_days, deleted_count}`（排程清理另帶 `job`）；刪 0 列照落；操作日誌源之清理永久豁免此列（後設證據）；寫不進＝整筆回滾 | `rust-api/server/src/model/audit.rs`（`AuditOperation::Purge`）；`rust-api/server/src/model/retention.rs`；憲法 §I.7 島 J3 |
| 孤兒授權列 | 現役授權列（`ptype`＝`p`）中候選外（選單維＝路由名不在治理域、按鈕維＝碼不在治理域按鈕碼聯集、端點維＝（路徑, 方法）不在 `router::policy_endpoints()`）或角色無主（`v0` 不在活性角色代碼集；停用角色仍屬活性）之列，每列每維至多計一次；由授權對賬計數、系統不自動刪；★與「撤銷殘留」為兩件事——孤兒授權列是授權真相 `casbin_rule` 中失去對象之列，撤銷殘留是判定面降級窗內被撤端點仍放行 | `rust-api/server/src/model/facade/sys_casbin_policy.rs`（`orphan_counts`）；ADR-00101 決定 6 |

會話撤銷詞組（撤銷三型～撤銷〔使用者域〕）、鎖定、IP 域詞組（信任錨～解鎖標記）、選單域詞組（選單序列化域～判定面同步）、授權治理詞組（全量替換～撤銷殘留）、使用者域詞組（停用／軟刪～經手表）與稽核域詞組（存取日誌～孤兒授權列）已隨憲法 §I.7 島 A～J 入上表（rev5 活書 §12 為藍本；稽核域詞組 rev5 活書 §12 無對應條、依 as-built 與島 J 寫）。

## AI 術語（保留；自 RAD-AI glossary 中文改寫）

標記＝`保留`（系統層目前無實例——系統本體無 AI 元件）／`流程層`（`docs/process/` 已用）。

| 術語 | 定義 | 標記 |
|---|---|---|
| 非確定性邊界 | 確定性程式碼與機率式（AI）元件之間的界線；每次越界都要標明輸出型、信心、換版頻率、fallback | 流程層 |
| 確定性區域 | 同輸入必同輸出的程式區；rev6 系統本體目前全屬此區 | 流程層 |
| 邊界契約（四段） | 越界處的四項標註：輸出型／信心規格／換版頻率／fallback 行為 | 流程層 |
| 信心規格 | 對輸出品質的可量化承諾（指標、門檻、延遲上界） | 流程層 |
| 降級輪廓 | AI 元件不可用或低信心時系統的行為：規則預設／快取末值／人工升級／優雅降級／斷路器 | 保留 |
| fallback | 降級輪廓中實際採用的那一種行為 | 流程層 |
| 人在迴圈 | 由人審核或接手 AI 輸出的元件刻板型；rev6＝user 拍板與 merge 同意 | 流程層 |
| 資料漂移 | 輸入資料的分佈隨時間偏離訓練時分佈 | 保留 |
| 概念漂移 | 輸入與目標之間的關係隨時間改變（資料形不變、意義變了） | 保留 |
| 串聯漂移 | 上游元件的漂移經依賴鏈放大到下游 | 保留 |
| 漂移偵測 | 監測輸入或輸出分佈以察覺漂移的機制 | 保留 |
| 模型新鮮度 | 模型自上次訓練或換版以來的時間，對照允許的最大時距 | 流程層 |
| 模型陳舊 | 模型因世界變了而品質退化的債；解法＝再訓練或換版 | 流程層 |
| 再訓練觸發 | 決定何時重訓或換版的條件：排程／事件／連續／靜態 | 保留 |
| 回退政策 | 換版失敗時退回上一版的條件與程序 | 流程層 |
| 糾纏（CACE） | 改一處即全部改變：模型輸入之間互相牽動，無法獨立變更 | 流程層 |
| 邊界侵蝕 | AI 元件的責任邊界因權宜接線而逐漸模糊 | 流程層 |
| 隱藏回饋迴圈 | 模型輸出經由世界回頭影響自己的輸入，卻未被記載 | 流程層 |
| 資料依賴債 | 對不穩定或未受管的資料來源的隱性依賴 | 流程層 |
| 資料血緣 | 資料從來源到模型與輸出的流向與轉換紀錄 | 保留 |
| 特徵庫 | 集中管理模型特徵、供訓練與推論共用的儲存 | 流程層 |
| 模型卡／資料卡 | 隨模型／資料集發布的標準化說明文件（用途、限制、指標、來源） | 流程層 |
| 品質閘 | 資料或產物進入下一階段前必須通過的檢查點 | 流程層 |
| 雙生命週期 | 軟體發布週期與模型訓練換版週期並行、各自節奏 | 保留 |
| Annex IV | EU AI Act 對高風險 AI 系統技術文件的要求清單；rev6 對映住 `docs/compliance/` | 保留 |

流程術語住 [RULES 名詞段](../ops/RULES.md)。
