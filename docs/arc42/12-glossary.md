---
section: 12
summary: 系統術語與 AI 術語（保留）；流程術語住 RULES 名詞段
rev5_blueprint:
  §12 名詞表: 承襲（治理詞入 §12 系統術語；踢除／撤銷、鎖定兩組域詞與 IP 域詞組〔信任錨、來源信心、來源維、存取閘等〕已入表，停用／軟刪、重設／修改密碼兩組隨島 I 進場刀）
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
| 撤銷三型 | logout（本人、只撤呈遞列、denylist `revoked`→舊 access 8888 靜默）／kick（single-session 頂替、撤同帳號其他 chain、denylist `kicked`→7777 modal）／idle（逾時拒換發、列不動、不寫 denylist→8888）；稽核落 `session_event`（event_type kicked／reuse／idle／logout） | §6.1；憲法 §I.7 島 B／C／D |
| grace 窗 | rotate 後 30 秒（`cache::GRACE_TTL_SECS`）的冪等窗：同票再呈遞回既發同一對、不再轉列；窗外（grace miss）＝reuse 偵測的唯一觸發形、撤整條家族 | `rust-api/server/src/cache/mod.rs`；憲法 §I.7 島 A |
| 節流三區 | 每一維（帳號維、來源維）各自的滑動窗三區；判定於每次登入嘗試以 PG `sys_login_attempt` 計數＋該維設定三鍵現值定案、快取層不持有鎖定態（無負快取、無鎖定鍵；該維解鎖標記以計數下界的形式入判）：`count < captcha_after` 自由／`captcha_after ≤ count < max_fails` 軟區（須過圖形驗證碼、否則 2222 `biz.auth.captchaRequired`）／`count ≥ max_fails` 鎖定（2222 `biz.auth.locked`）；合成＝任一維鎖定即鎖定、否則任一維軟區即要求驗證碼，兩維拒絕共用同一組 msg、不揭露觸發維度；拒絕皆在密碼驗證之前、零稽核列零計數桶 | `rust-api/server/src/throttle/mod.rs`；憲法 §I.7 島 E；ADR-00038 |
| 鎖定 | 節流第三區：某一維窗內失敗達該維 `max_fails` 時新的登入嘗試被拒；是每次嘗試由 PG 滑動窗現算的判定結果、不是一把存起來的鎖——最早一筆失敗出窗、門檻放寬、或該維寫入解鎖標記，下一次嘗試即解；不動 token、不寫 denylist——鎖的是門、已持有效憑證者照常；管理員解鎖＝`POST /systemManage/unlockLogin`（API-only、限 `R_SUPER`；無 UI 按鈕＝ADR-00040） | `rust-api/server/src/throttle/mod.rs`；`rust-api/server/src/handler/throttle.rs`；ADR-00038 |
| denylist 加速層 vs status 權威 | redis `session:denylist:{sid}`（值＝reason `kicked`｜`revoked`、TTL＝refresh 全壽命）只是每請求的加速判定；定案恆＝`sys_token.status`——鍵缺席＝未撤放行、鍵不可讀退 PG 查鏈上是否仍有 active、兩者不一致以 status 為準、`revoked` 列缺鍵靜默 8888 不落假 reuse | `rust-api/server/src/auth/enforce.rs`；憲法 §I.7 島 C |
| idle 逾時 | 換發時距 `session:{sid}:last_activity` 逾 `refresh_secs − access_secs`（＝N×60 秒）即拒；時鐘只住 redis、由 enforce 放行後推進、換發端點自身不推進；不可讀＝fail-open | `rust-api/server/src/handler/auth/refresh.rs`；憲法 §I.7 島 D |
| 降級（基礎設施） | 本系統確定性本體的降級：redis／PG／設定鍵不可用時依憲法 §I.7 各島拍板的 fail-* 方向走保守腿（denylist 讀不到退 PG＝fail-closed、`last_activity` 讀不到續換發＝fail-open、節流三鍵缺失整組退常數…）；二軌可觀測面覆蓋不等寬——軌道①結構化 warn（target `security.session`／`security.throttle`／`security.trust`／`security.ipgate`、`degraded` 欄即腿名）是每條具名腿的共同軌，軌道②計數器只有 `throttle_degraded_total`（節流兩維降級源；值集＝`obs.rs` `THROTTLE_DEGRADED_SOURCES`）、`denylist_hit_total`（enforce 驗章面 denylist 二源）與 `ip_domain_degraded_total`（IP 域降級源＝信任模型載入三腿、規則集初載／重載、門鈴發布／訂閱、請求上下文缺席；值集＝`obs.rs` `IP_DOMAIN_DEGRADED_SOURCES`）三支（`throttle_soft_zone_total` 計的是軟區命中、`ipgate_blocked_total` 計的是存取閘阻擋，兩者皆不屬降級），`last_activity_read`／`grace_read`／`grace_write` 等其餘腿只查得到事件、無計數序列可撈（逐腿覆蓋＝§6.1、§8.3 與各該 fn doc；enforce 放行後推進 `last_activity` 的 best-effort 寫入兩軌皆無、語意見其碼註）；★與下表 AI 術語「降級輪廓」（AI 元件不可用或低信心時的行為型錄）不同義、兩詞不互用 | §8.3、§10.2；`rust-api/server/src/obs.rs` |
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

踢除／撤銷（撤銷三型）、鎖定兩組域詞與 IP 域詞組（信任錨～解鎖標記）已隨憲法 §I.7 島 A～F 入上表；停用／軟刪、重設／修改密碼兩組隨島 I 的進場刀入本表（rev5 活書 §12 為藍本）。

## AI 術語（保留；自 RAD-AI glossary 中文改寫）

標記＝`保留`（系統層尚無實例）／`流程層`（`docs/process/` 已用）。

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
