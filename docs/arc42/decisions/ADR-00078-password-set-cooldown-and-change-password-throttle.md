---
id: "ADR-00078"
title: 設密冷卻與改密舊密節流刻意分家——冷卻走設定鍵、維度（標的, 操作者）、借經手表時戳、零豁免；節流走碼內常數 5 次／900 秒、redis 計數桶 `cpwd:{uid}`、舊密比對之前拒、fail-open 並計入節流降級第十一源 `redis_change_pwd`；ADR-00038 射程限登入節流；通用節流 seam 以 rev6 形重做四面比較後不建（BL-00124）
date: 2026-10-05
status: superseded
supersedes: []
superseded_by: [ADR-00090]
provenance: "007-user-password-admin 之 spec FR-035（冷卻）、FR-036（改密步序）、FR-037（改密節流、降級源 10→11、ADR-00038 射程釐清、BL-00124 四面比較）、FR-031（ADR-00037 觸發器反向確認）、US3 AS5／AS6、SC-006、Edge Cases「密碼面」段；brainstorm §0 Q20、§1「設密冷卻」「改密舊密節流」兩列、主線工程判斷③（載體 redis `cpwd:{uid}`、fail-open、降級源 10→11、ADR-00038 射程釐清）與⑨（ADR-00037 觸發器反向確認）；plan 期主線定案（鍵前綴獨立不置於 `throttle:` 下、門檻為碼內常數、降級源字面與名冊雙向守、`throttle/change_pwd.rs` 與 `cache` 鍵 builder 之落點與命名）；藍本＝rev5:ADR 0066（二機制分家、門檻判準、fail-open、四面比較、seam won't-fix）與其 as-built rev5:server/src/throttle/change_pwd.rs、rev5:server/src/cache/mod.rs（`incr_with_window`、`cpwd:` 前綴）、rev5:server/src/model/facade/sys_pwd_custody.rs；冷卻拍板之更早藍本＝rev4:015-pwd-custody（只借冷卻、經手判定不帶回）；rev6 既有件＝`sys_pwd_custody`（001 基線、複合主鍵 (user_id, created_by)）、`validation::REGISTRY` 之 `password_change_min_interval`（[0, 86400]、seed 60）、`sys_login_attempt`（無用途欄）、`obs::THROTTLE_DEGRADED_SOURCES`、`throttle::warn_degraded`、告警規則 `obs016-throttle-degraded`（不設 source 篩選）；上游＝ADR-00038 決定 1～6、憲法島 E（「redis 於本島只承載…」）、ADR-00069 款 5、ADR-00037 翻案觸發器首條；對沖條目＝BL-00124；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [password, throttle, cooldown, observability, user-password-admin]
---

## 背景

- 本刀兩個「限制重試」機制在同一條路徑上同時進場、形似而擋的東西不同：**設密冷卻**＝同一對（標的, 操作者）兩次設密之間的最短間隔；**改密舊密節流**＝changePassword 之「舊密碼」欄在窗內可猜錯幾次——持有一枚未過期 access token 者（借用的瀏覽器、殘留分頁）可在 token 壽命內反覆猜舊密，而登入節流一次都不會被觸發。
- rev6 登入節流之判定面已改為每次嘗試由 PG 滑動窗定案、redis 只承載驗證碼一次性標記與解鎖標記（ADR-00038；憲法島 E「redis 於本島只承載…」；`throttle/mod.rs` 模組 doc 同義）。前代以四面比較判通用節流 seam 不建（`rev5:ADR 0066` 決定四），其比較以前代登入節流為底；004 刀 spec Out of Scope 首條「通用化節流 seam」在現在式帳本零承載——BL-00124 要求本刀以 rev6 形重做。
- ADR-00069 款 5（redis 不開持久化）之理由寫「節流判定面不依賴 redis（ADR-00038）」，其翻案觸發含「新增不可自癒之 redis 狀態」；ADR-00037 翻案觸發器首條為「登入以外再出現以來源位址做安全判定之匿名端點」。
- Q20 拍板做（5 次／15 分鐘）；載體與降級方向為主線工程判斷③。

## 決策驅動因子

- 門檻進不進設定表之判準＝這個數字有沒有第二個合理答案（承 `rev5:ADR 0066` 決定三）。
- 拒絕不得推進計數、不得耗 argon2 驗密（否則持續打即可鎖死任何人之改密）。
- 降級代價不對稱：改密節流是防慢速猜測之加值防線。
- 零 DDL（本刀只有 seed-only 之 m0003）。
- 觀測沿既有單一名冊與雙向守；不擾動登入節流已拍板之判定面。

## 考慮過的替代案

1. **節流門檻入設定表**（與冷卻一致）：「舊密可猜幾次」只有一個量級之正確值，旋鈕只會被調錯；且每鍵有固定成本（registry 界、設定頁、wire、seed、三語）。否決。
2. **改密節流 fail-closed**：快取失聯整段期間全體改不了密碼（含資安應變中急著換密者）。否決。
3. **冷卻與節流合併為「密碼操作頻率限制」**：冷卻擋成功之操作、節流擋失敗之嘗試；合併後一方會被另一方之計數影響，而兩者之正確反應（等一下 vs. 你可能不是本人）不同。否決。
4. **改密節流走 PG 滑動窗**（比照 ADR-00038）：`sys_login_attempt` 無用途欄——改密失敗列寫入即被登入帳號維（`attempted_user_name`）與來源維計數吃到，使改錯舊密者被登入鎖定，並污染登入稽核軌跡；另立表或加欄＝DDL。否決。
5. **鍵置於 `throttle:` 前綴下**：維運以前綴批次清登入節流鍵（解鎖標記、驗證碼標記）時會誤清改密桶；判定維度亦不同（uid 對帳號名或位址桶）。否決。
6. **建通用節流 seam**：四面不同形（決定 4）。否決（won't-fix）。
7. **冷卻對超管或自改豁免**：spec FR-035 一體適用、零豁免；豁免＝為單一身分開特例。否決。
8. **以 `sys_user` 新欄記上次設密時間**：DDL，且失去（標的, 操作者）維度。否決。

對所選方案跑同一反例（RL-0013）：

- 「fail-open 被利用」：攻擊者須先使 redis 失聯（非請求可控）且持有效 access token；嘗試上界仍受舊密強度與 token 壽命所限；降級即計數並告警。接受（殘餘＝失聯期間之額外嘗試、記於後果）。
- 「redis 重啟遺失計數桶」：等同窗提前自癒、至多多得一窗份嘗試、重啟非攻擊者可控。成立（決定 6）。
- 「兩名操作者交替重設以繞過冷卻」：維度刻意為（標的, 操作者）——不同管理員各記各的、各自落稽核；冷卻防的是單一操作者對同一標的之頻繁設密。成立。

## 決定

1. **設密冷卻（業務政策、走設定鍵）**：
   - 門檻＝設定鍵 `password_change_min_interval`（秒；registry [0, 86400]、seed 60），於消費當下讀現值；`0`＝停用（早退、不查經手表）；缺列、軟刪、不可解析或越 registry 界＝退出廠值 60＋warn 一則（不從嚴、不放行；與密碼政策單鍵異常之取態同向＝ADR-00079 決定 4）。
   - 維度＝（標的 id, 操作者 id）；料源＝`sys_pwd_custody` 該對之 `created_at`（表內零密碼材料）；寫入＝`sys_pwd_custody::touch` upsert 該對時戳，MUST 與密碼欄 UPDATE 同一交易（標的 advisory 序列化域內——分兩交易即有「密碼改了、冷卻帳沒記」之縫）；只 upsert、不刪他列（rev4「本人自改即全刪他人經手列」不帶回）。
   - 三入口一體適用、零豁免：addUser 之初始密碼照落 touch（新標的對無前次、結構上不拒；不落則「建帳後立刻重設」白得一次）；resetUserPassword＝（標的, 操作者）；changePassword＝（本人, 本人）。
   - 未滿＝`2222`＋`biz.user.pwdSetTooFrequent`、`data.remainingSeconds`＝`min(max(I−⌊Δ⌋, 1), I)`（rust `u64`；I＝冷卻設定值、Δ＝距該對上次設密之經過秒數；下限 1、時鐘回撥上限 I——照提示秒數重試必過；明細形與受眾判準＝ADR-00076）；判定件＝`model/password.rs::cooldown_remaining_secs(conn, target_id, operator_id) -> Result<Option<u64>, AppError>`（`None`＝不擋）；判定位次＝政策驗證之後、寫入之前（逐端點步序見本刀 contracts）。
2. **改密舊密節流（安全參數、走碼內常數）**：
   - 門檻＝`throttle/change_pwd.rs` 之 `CHANGE_PWD_MAX_FAILS = 5`、`CHANGE_PWD_WINDOW_SECS = 900`；不入 `system_settings`；與登入節流之同值常數不共用（調參理由不同）。
   - 載體＝redis 計數桶 `cpwd:{uid}`（`cache::CHANGE_PWD_KEY_PREFIX = "cpwd:"`、builder `cache::change_pwd_key`；`cache` 仍為全 crate 唯一鍵渲染點）。寫入原語 `cache::incr_with_window`＝INCR 與 EXPIRE 同一原子管線、每次失敗把存活期刷滿 900 秒——以「最後一次失敗後 15 分鐘無新失敗即自癒」實作之滑動窗；拆成兩步則 INCR 成而 EXPIRE 敗會留永不過期之鍵＝該使用者改密永久鎖死。
   - 判定序（逐步全文＝本刀 contracts wire-user-center §2）：`precheck(cache, uid) -> Result<(), Throttled>`（純讀 `cpwd:{uid}`、於開交易之前、結果暫持、不構造 `AppError`）→ 開交易 → 新密雜湊生成（取鎖前＝島 I5）→ ①本人列鎖讀（查無＝`biz.user.notFound`）→ ②兩次輸入一致 → ③節流（預檢結果為 `Err(Throttled)`＝handler 以 `biz.user.changePasswordThrottled` 構造拒因、純 key、不下發剩餘秒數或已用次數）→ ④舊密比對（鎖內；不符＝`biz.user.oldPasswordMismatch`、交易回滾後 `record_failure` 推一格＝唯一推進腿）→ 後續步。節流拒絕路徑零 argon2 驗密、零稽核、零計數推進；成功改密於 commit 之後 `clear`（清在前而交易回滾＝白清一次桶）。
   - 窗自癒、無解鎖端點。降級＝redis 讀寫失敗即放行（不計數、不拒）並經既有出口 `throttle::warn_degraded("redis_change_pwd")` 落一則 warn、計數一格；快取層自始缺席（測試 seam）＝整層跳過、不計降級。
3. **觀測**：`THROTTLE_DEGRADED_SOURCES` 增 `redis_change_pwd`（10→11）、開機預註冊 0；名冊雙向守照舊——名冊→發射端（出口逐值增長案）、發射端→名冊（obs 測試對 `warn_degraded` 字串字面引數之全樹掃描；經既有出口發射即自動在射程內，此為不另立第二出口之理由，前代則自成出口、不經該函式）。告警規則 `obs016-throttle-degraded` 不設 source 篩選、自動涵蓋新值、規則本體零改動。
4. **不建通用節流 seam**（BL-00124；rev6 形四面比較）：

   | 面 | 登入節流（島 E／F；ADR-00038） | 改密舊密節流（島 I；本 ADR） |
   |---|---|---|
   | 判定鍵 | 帳號維＝送出之帳號名原文（未驗身、請求端自選）；來源維＝來源位址桶 | uid（已驗身、取自身分注入、請求不可指定） |
   | 判定真源與載體 | PG 滑動窗：`sys_login_attempt` 失敗列於每次嘗試重算；redis 只承載驗證碼標記與解鎖標記 | redis 計數桶本身即真源；無 PG 列 |
   | 語意分區與解除 | 三區（自由／需驗證碼／鎖定）；窗出界、帳號維成功重置、管理員解鎖端點 | 兩態（過／拒）；窗自癒、成功即清；無解鎖端點 |
   | 門檻與壞值 | 每維設定三鍵、每次嘗試讀現值；壞值整組退常數＋告警 | 碼內常數；無設定鍵、無壞值面 |

   抽一個同時容納三區與兩態、PG 真源與 redis 真源之 seam＝為兩個不同形之消費者硬造抽象（`throttle::precheck` 之簽章將被迫長出「要不要驗證碼」「真源在哪」之參數）。共通者只有觀測序列（同名冊、同出口；決定 3），不構成 seam。004 刀 spec Out of Scope 首條之通用化 seam 判 won't-fix；翻案觸發＝出現第三個消費者且與既有兩者之一同形。
5. **ADR-00038 射程釐清**（不翻案、不 supersede）：該 ADR 為登入節流判定面（標題與 provenance 皆指 004 刀之登入兩維）；其決定 2「redis 在節流面只承載兩種鍵」之「節流面」讀作登入節流面，決定 1「PG 定案、無負快取」亦只對登入兩維。改密節流桶屬島 I 之常數面（前代島 I 常數列即含「改密節流之窗與次數」；rev6 條文字面由 ADR-00074 親決）、不屬島 E；憲法島 E「redis 於本島只承載…」之「本島」已自限、續真。改密桶是計數真源、不是負快取（沒有第二份會落後的真相）。
6. **不觸發者**（複核結論）：ADR-00069 款 5 之翻案觸發「新增不可自癒之 redis 狀態」不成立——改密桶遺失＝窗提前自癒；ADR-00037 翻案觸發器首條不成立——changePassword 為 Authed、判定鍵為 uid、不讀來源位址（spec FR-031）。

- **親決紀錄**：user 親決 2026-10-06（007 刀 tasks T003 施工前提顆）——本輪逐款一題一問呈決定 1～6、皆照文定稿；零非建議項 ⇒ 決定節免改寫。

## 後果

- 碼面新建／擴：`throttle/change_pwd.rs`（`precheck`／`record_failure`／`clear`、兩常數）；`cache/mod.rs` 之前綴常數、鍵 builder、`incr_with_window`；`model/facade/sys_pwd_custody.rs`（`touch`／`last_set_at`）；`obs.rs` 名冊 11 值。
- 現在式假述（RL-0011）：「恰十」「十值」「十源」（`obs.rs` 名冊 doc 與釘值案、`throttle/mod.rs` 出口 doc 與逐源案、`lib.rs` 模組樹「降級十源」）改十一；`obs.rs` 名冊 doc「逐字照抄 004 data-model §5」改述為前十值之凍結存證＋第十一值出處本刀 data-model；`throttle/mod.rs` 模組 doc「登入失敗節流」「快取層在本模組只承載兩種鍵」改述為登入節流之自限句（本模組下新設改密子模組）、`lib.rs` 之 throttle 模組描述同；`cache/mod.rs` 檔頭「`cpwd:` 前綴…`incr_with_window` 屬後刀域、不帶」與「七支 redis 鍵 builder」改現在式；告警規則檔 throttle-degraded 段錨註「（島 E1）」補島 I 改密源；活書 06 降級出口句。種子施工時以 `python3 tools/docsync errata <詞>` 現算、改完復掃。
- ADR-00069 款 5 之「節流判定面不依賴 redis」自本刀起讀作登入節流判定面（讀法承載＝本 ADR 決定 5、決定 6；accepted 本文不改）；其續行 ADR（ADR-00082）若重述款 5，同批改述。
- 走查還原工具清理前綴增 `cpwd`、經手表全表清空；測試守衛 `RedisKeysGuard` 增 `cpwd:`、新增 `PwdCustodyRowsGuard`（本刀 research R15／R16）。
- BL-00124 收刀 backlog_done（本 ADR 即通用 seam 之 won't-fix 承載）。
- 代價誠實記：fail-open 期間猜測者多得之嘗試為已接受之殘餘；節流拒絕路徑零 argon2 驗密，但新密雜湊於開交易後、取鎖前計算（島 I5「不持列鎖時計算」）、早於節流判定③ ⇒ 被節流擋下之請求仍白算一次雜湊生成——容量與防濫用判斷不可據「被節流的請求不吃 CPU」推論。

## 翻案觸發器

- 出現第三個節流消費者且與既有兩者之一同形 ⇒ 重評通用 seam（決定 4）。
- 改密失敗須留可稽核之持久紀錄（安全審查、事故鑑識）⇒ PG 載體＋DDL，複核決定 2 與 ADR-00038 之射程關係。
- redis 狀態遺失成為可被利用之實際事故、或改密桶改為不可自癒之形 ⇒ 複核決定 6 與 ADR-00069 款 5。
- 支援面出現「替使用者解除改密節流」之實際需求 ⇒ 複核「無解鎖端點」。
- 節流門檻出現第二個合理答案（組織差異之實際調參需求）⇒ 依判準改設定鍵。
- 冷卻出現豁免需求、或維度須改為標的單維 ⇒ 複核決定 1。
- fail-open 於事故中被實際利用 ⇒ 複核降級方向。
- 登入節流判定面改形（ADR-00038 翻案）⇒ 複核決定 4、決定 5。
