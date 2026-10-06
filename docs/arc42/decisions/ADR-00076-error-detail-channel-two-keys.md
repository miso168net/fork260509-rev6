---
id: "ADR-00076"
title: 錯誤明細通道射程恰兩鍵——`biz.user.passwordPolicy` 攜違規碼清單、`biz.user.pwdSetTooFrequent` 攜剩餘秒數，經新變體 `AppError::BizData` 與信封之獨立攜明細出口上 wire；受眾判準＝明細是否只是操作者自陳輸入之評估結果；`5003` 與改密節流等其餘拒因恆純 key；違規子鍵譯文落 page 樹單一命名空間
date: 2026-10-05
status: accepted
supersedes: []
superseded_by: []
provenance: "007-user-password-admin 之 spec FR-004（唯二例外、變體 9→11）、FR-033（違規碼八枚、page 樹單一共用命名空間）、FR-035（剩餘秒數下取整）、FR-051（請求層明細轉譯只限兩鍵；I18N (i) 由 Amendment 改寫；002 wire 契約對應條與錯誤信封釘案同批改寫；msg-key-gate 同批擴）、FR-064（明細信封入 wire 裁判）；brainstorm §0 Q18、§1「BizData 明細通道」列、主線工程判斷①（ADR-00014 決定 1 只管 5003、密碼違規明細 2222 不在射程）；spec Assumptions 所記 clarify 步主線工程判斷（FR-033 單一共用命名空間）；plan 期主線定案（變體名與碼映射、兩鍵明細形、違規子鍵之 page 樹路徑與圈界歸屬、msg-key-gate 斷言 2 擴認）；藍本＝rev5:ADR 0064（射程二鍵、受眾判準、`from_err` 出口分離）與其 as-built rev5:server/src/error.rs（`BizData`）、rev5:server/src/envelope.rs（`from_err_with_data`）、rev5:server/src/handler/user.rs（`password_policy_err`／`pwd_set_too_frequent_err`）；`rev5:B-139`（明細鍵名與前端佔位分岔、明細靜默消失）；rev6 既有件＝rust-api/server/src/error.rs（九變體、`MSG_KEYS`）、rust-api/server/src/envelope.rs（`Res::from_err`、釘案 `error_envelope_data_null_not_omitted`、compile_fail doctest）、rust-api/server/tests/contract.rs（`assert_error_envelope`、`msg_roster_every_key_has_an_emitter`）、tools/msg-key-gate.py 斷言 1～3、base-web/src/service/request/index.ts 之 `translateBackendMsg`；上游約束＝憲法 §I.3、§III.2 `BASE-WEB-I18N-WIRING` (i)(ii)（I18N (i) 改寫字面由 ADR-00074 於本刀 U0 親決）、ADR-00014 決定 1 與翻案觸發器首條、ADR-00039（譯文之家三檔）、specs/002-system-settings/contracts/wire-settings.md §3 第 3 條；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [wire, error, i18n, password, user-password-admin]
---

## 背景

- rev6 錯誤信封自 002 刀起 data 恆 null：`Res::from_err` 為唯一錯誤出口、data 恆 `None`；002 wire 契約 §3 第 3 條「錯誤 `data:null` 不省略」由 envelope 釘案 `error_envelope_data_null_not_omitted` 機器釘；003 刀 Amendment 之 I18N (i) 列紀律欄明文「錯誤信封 `data` 恆 null、無明細通道 ⇒ 不建 `translateDetailValue`」；`error.rs` 檔頭記「BizData／ModalLogoutByAdmin 屬後刀域、不帶」；003 刀 msg-keys 契約記前代 backend 樹九鍵白名單不建。
- 本刀密碼政策三入口一次收集全部違規（FR-032）、設密冷卻須告知剩餘秒數（FR-035）。純 key 下「一次收集」在 wire 上無意義——設密者只見「不符合政策」、不知該改哪條；管理員重設浮層之即時提示來自開浮層當下之政策投影，後端裁判時政策可能已變。Q18 拍板開通道、只限兩鍵。
- 前代以 `rev5:ADR 0064` 定二鍵與受眾判準，但 rev6 有三處前代沒有的約束：I18N (i) 列字面、跨端閘「backend 子樹鍵集＝`MSG_KEYS`」逐檔全等＋名冊每鍵 ≥1 發出點（前代 backend 樹九鍵白名單形在 rev6 不成立）、`error.rs` 明文不帶 ⇒ 須 Amendment 改一列、違規子鍵改落 page 樹。
- ADR-00014 翻案觸發器首條：「業務錯誤明細的受眾邊界重評……以新 ADR 翻案、不得就地放寬本決定」；本 ADR 即該重評之承載。

## 決策驅動因子

- 設密者能據明細自行修正輸入（違規條目、等待秒數）。
- 明細不得成為授權模型或系統狀態之探測面。
- 攜明細須為出口之顯式選擇，不因「反正是業務錯誤」順手外溢。
- 13 碼矩陣、可發碼集、信封三欄與宣告序不變（憲法 §I.3）。
- 跨端鍵集閘與名冊雙向閘照舊成立；前後端明細鍵名分岔不得靜默（`rev5:B-139`）。

## 考慮過的替代案

1. **維持純 key、前端以 getPasswordPolicy 預檢**：冷卻剩餘秒數前端無從得知；浮層所持政策投影與後端裁判時之現值可能有差；「一次收集全部違規」失去 wire 意義。Q18 否。
2. **每種違規各一獨立鍵、只回第一條**：多條違規時逐次猜謎；鍵數膨脹八倍。否決。
3. **明細通道全面開放、由各 handler 斟酌**：邊界靠節制不靠判準（rev4 逐刀累積至六鍵、`rev5:ADR 0064` 替代案 B）。否決。
4. **冷卻與改密節流一致**（都攜參或都純 key）：形似而資訊來源不同（決定 2）。否決。
5. **`5003` 攜缺哪條政策或角色差集**：受眾是已確定無權之人，權限地圖可逐次累積（ADR-00014 決定 1）。否決。
6. **違規子鍵落 backend 樹**（前代九鍵白名單形）：破 I18N (ii)「backend 子樹鍵集＝`MSG_KEYS` 全等」與「名冊每鍵 ≥1 發出點」——要嘛把後端恆不發之鍵塞進名冊，要嘛替兩道閘開白名單例外。否決。
7. **子鍵分頁各一份**（使用者頁、個人中心各自命名空間）：請求層轉譯為全域、不知所在頁；兩份譯文會漂移。否決。
8. **讓 `Res::from_err` 對 BizData 直接帶 data**：攜明細不再是顯式出口選擇、錯誤 data 恆 null 之釘案須整支改寫。否決，改設獨立出口（決定 4）。

對所選方案跑同一反例（RL-0013）：

- 「明細成為探測面」：兩鍵之明細皆為設密者自陳輸入之評估、或其自身上次設密時戳之算術，不含他人或授權模型資訊。成立。
- 「攜明細外溢到第三鍵」：BizData 構造點之鍵集由 msg-key-gate 射程守釘為恰兩鍵、各鍵恰一組裝點（決定 7）；新增攜參鍵即紅、須回決定 2 判準。成立。
- 「鍵名分岔、明細靜默消失」：明細信封之 wire 型入受審名冊、前後端鍵名由 wire 裁判對賬（決定 7）。成立（前提＝前端轉譯以該型取值）。

## 決定

1. **射程恰兩鍵、其餘恆純 key**：

   | 拒因鍵 | `data` 形 | 組裝點（各恰一） | 發出端點 |
   |---|---|---|---|
   | `biz.user.passwordPolicy` | `{"violations": [...]}`：違規碼八枚（`minLength`／`maxLength`／`maxBytes`／`requireDigit`／`requireLowercase`／`requireUppercase`／`requireSpecial`／`forbidUsername`）之子集、一次收集全部、序＝驗證點之檢查序（同上列序） | `password_policy_err` | addUser／resetUserPassword／changePassword |
   | `biz.user.pwdSetTooFrequent` | `{"remainingSeconds": n}`：整數（rust `u64`）＝`min(max(I−⌊Δ⌋, 1), I)`（I＝冷卻設定值、Δ＝距上次設密之經過秒數；下限 1、時鐘回撥時上限 I——照提示秒數重試必過） | `pwd_set_too_frequent_err` | resetUserPassword／changePassword（addUser 之新標的與操作者成對無前次設密、結構上不發） |

   - 兩支組裝點住 `handler/user.rs`（`pub(super)`、`handler/user_center.rs` 共用），以具型明細 `PasswordPolicyDetail { violations }`／`PwdSetTooFrequentDetail { remaining_seconds }`（`#[serde(rename_all = "camelCase")]`；`pwd_set_too_frequent_err(remaining_seconds: u64)`）構造後 `serde_json::to_value`——明細鍵名在型別層只有一份（兩型同入 wire 受審名冊、見本刀 contracts wire-user-center §3）。
   - 其餘一切拒因 data 恆 null：含 `5003`（政策無授與包含規則違反）、`biz.user.changePasswordThrottled`、`biz.user.roleNotFound` 等。
2. **受眾判準**（承 `rev5:ADR 0064` 決定二）：明細描述的是操作者自己剛送出之輸入的評估結果 ⇒ 可攜；描述的是系統之授權模型或計數狀態 ⇒ 純 key；兩者都沾 ⇒ 純 key（混合體之洩漏面等於較寬之一半）。
   - 冷卻剩餘秒數＝操作者自身上次設密時戳與設定值之算術 ⇒ 可攜；改密節流之剩餘秒數或已用次數＝計數桶之當前狀態、等於給猜測者一個可查詢之預言機 ⇒ 純 key。是不是時間、像不像冷卻都不是判準，資訊來源歸屬才是。
   - ADR-00014 翻案觸發器首條之本刀重評結論＝`5003` 不放寬、ADR-00014 決定 1 不翻案（日後之診斷需求另見翻案觸發器）；本 ADR 兩鍵屬 `2222` 業務錯誤、不在 ADR-00014 決定 1 射程。
3. **錯誤變體**：`AppError::BizData(Cow<'static, str>, serde_json::Value)`——碼 `2222`、msg＝鍵、HTTP 200；與 `AppError::Biz` 共用 `2222` 列、13 碼矩陣不增列、可發碼集不變。變體集 9→11（另一新變體 `AppError::ModalLogoutByAdmin`〔`7777`＋`auth.session.kickedByAdmin`〕屬斷權面、見本刀 research R10）。
4. **信封出口分離**：`Res::from_err` 對一切變體（含 BizData）續回 data null；攜明細只經新設之 `Res::from_err_with_data`（`pub(crate)`），其唯一正當呼叫者＝`AppError` 之 `IntoResponse` 對 BizData 之分派臂——攜不攜明細是出口之顯式選擇、呼叫點不得自填。`Res` 三欄續非 pub、任意碼信封構造層不可得之 compile_fail 釘不動。
5. **002 wire 契約 §3 第 3 條之現行讀法**：「錯誤信封之 `data` 欄恆在場不省略；值恆 null，唯本 ADR 兩鍵攜明細物件」。`specs/002-system-settings/` 原檔屬 002 刀凍結存證、零改動（同 ADR-00041 決定 3 之取態）；改寫對照落本刀 contracts wire-user-center §3，現在式承載面＝本 ADR＋`envelope.rs` 模組 doc 與釘案＋`error.rs` 模組 doc；碼註指向 002 契約 §3 第 3 條者六處同批補指本 ADR（spec FR-051：`envelope.rs` 模組 doc、`from_err` doc、成功與錯誤信封兩測試 doc；`error.rs` `each_issuable_code_builds_error_envelope` doc；`tests/contract.rs` 之 4040 fallback 腿 doc），其中所述已不真者（「錯誤時 data 必為 null」「唯一錯誤入口」類）同批改寫。釘案改寫須涵蓋三件：BizData 經 `IntoResponse` 出明細物件、同一顆經 `from_err` 仍 null 且兩形 code 與 msg 逐字相同、其餘變體 data 恆 null 不省略；欄序 `data→code→msg` 不變（案形見本刀 contracts code-gates）。
6. **前端**（I18N (i) 改寫之設計全文；條文字面由 ADR-00074 親決）：
   - 請求層 `src/service/request/index.ts` 建明細轉譯、只認兩鍵；其餘錯誤續由 `translateBackendMsg(msg)` 呈純 key 提示；轉譯未命中一律 graceful fallback（不吞錯、不顯裸鍵）。
   - 違規子鍵譯文落 page 樹單一共用命名空間：`page.passwordPolicy.violation.<code>`（八枚）＋`page.passwordPolicy.listSeparator`；三語各一份；請求層明細轉譯、改密卡與重設浮層之即時規則、產密元件共用（請求層為全域、不知所在頁）；新增型圈界歸 `BASE-WEB-I18N-WIRING(i)`；`app.d.ts` 之 `Schema.page` 型節同批。
   - 兩鍵之 backend 子樹譯文帶具名插值佔位、佔位名＝明細鍵名（各語字面見本刀 contracts msg-keys §2）；`data` 形不合即退回純 key 轉譯；backend 子樹只放 `MSG_KEYS` 成員——I18N (ii) 與跨端閘斷言 1 不破、前代九鍵白名單形不帶。
7. **機器守**：
   - `tools/msg-key-gate.py` 斷言 2 擴認 `AppError::BizData(` 構造點（現行樣式只認 `Biz(`、`BizData(` 在射程外）：鍵須 `Cow::Borrowed` 字面或 `msg_key` 常數、解出鍵 ∈ 名冊、動態構造＝紅；另加射程守分階段四句（閘常數 `BIZ_DATA_KEYS`＝本 ADR 兩鍵→其明細型名）——①BizData 構造點之鍵 ⊆ `BIZ_DATA_KEYS`（他鍵＝射程未經本 ADR 擴張）②`BIZ_DATA_KEYS` 中已入 `MSG_KEYS` 之鍵於生產區恰一處構造點（零處＝構造點蒸發、多處＝分岔）③未入 `MSG_KEYS` 之鍵構造點數為 0 ④射程鍵以 `AppError::Biz(` 純 key 形構造＝紅（明細靜默消失）；②③隨兩鍵分批入名冊逐鍵生效（U6 只落變體與出口、生產區零構造點即綠）；佔位符對賬——三檔 locale 兩鍵譯文之佔位符集恰等於明細型序列化後之欄名集（`{violations}`／`{remainingSeconds}`）、其餘鍵譯文零佔位符（`rev5:B-139` 之機器守；形見本刀 contracts msg-keys §5、code-gates §2.3）；各腿一正一反自證（RL-0080）。斷言 3 之 `FRONTEND_MSG_CONSUMERS` 依請求層明細轉譯之 wire 形字面消費點同批登記。
   - contract：兩鍵各至少一案實際發出、斷言 `data` 形（鍵名、型別、`remainingSeconds ≥ 1`）；既有 `assert_error_envelope`（data 恆 null）續用於其餘拒因；名冊雙向閘照舊。
   - wire 裁判：明細信封之 wire 型（型名見本刀 contracts wire-user-center §3）入受審名冊、配正向＋反例（spec FR-064）＝前後端明細鍵名分岔之機器守。

- **親決紀錄**：user 親決 2026-10-06（007 刀 tasks T003 施工前提顆）——決定 1／2 已於 T002 Amendment 顆之同一親決輪先定（照文；被 I18N (i) 條文重述或倚賴之款）；本輪逐款一題一問呈決定 3～7、皆照文定稿；零非建議項 ⇒ 決定節免改寫。

## 後果

- 碼面：`error.rs` 增變體、檔頭「變體集恰九」與「BizData／ModalLogoutByAdmin 屬後刀域、不帶」改現在式（可發碼「恰九」、無變體碼「恰四」不變——碼數不因變體增加而變）；`envelope.rs` 增出口、模組 doc 改述；`lib.rs` 模組樹「九變體 AppError」改「十一變體」。
- 前端：`request/index.ts` 碼註「rev6 錯誤信封 `data` 恆 null、沒有明細通道 ⇒ 只此一支 helper」改寫；I18N (i) 標記處數變動由 ADR-00074 預估範圍欄、收刀前 PATCH 實數化。
- 現在式假述（RL-0011）：種子＝「明細通道」（plan 期 errata 全 repo 18 處、含史料面）「恆 null」「data:null」「恰九」「九變體」「各對應 `AppError` 恰一變體」（活書 08 §8.2 碼表 as-built 句）「不攜參」「唯一錯誤入口」「只能由此產生」；現在式面逐處判讀，史料面（specs、brainstorms）與 accepted ADR 本文（ADR-00026 之 I18N (i) 列）不動。
- 防回歸清單翻轉：005 刀與 006 刀 research R3 照帶之「業務錯誤純 i18n key 不攜參」「拒因純 key 不攜參」兩項，自本刀起射程扣除本 ADR 兩鍵；兩份 research 屬凍結存證不改，本刀 research R5 之防回歸清單以本 ADR 改述。
- 代價：多一條信封出口、兩支組裝點與閘之兩條新腿（射程守、佔位符對賬）；新增攜參鍵必經本 ADR 判準並同批改閘常數。

## 翻案觸發器

- 提議第三個攜參鍵 ⇒ 回決定 2 判準、新 ADR；不得在 handler 就地多構造一顆 BizData。
- `5003` 出現「為何被拒」之診斷需求（例：多層管理員介面須引導去找誰開權限）⇒ 新 ADR 正面回答決定 2，並以 ADR-00014 為翻案對象。
- 生產面發生前後端明細鍵名或違規碼分岔（明細靜默消失）⇒ 加強機器守（例：違規碼八枚之前後端名冊對賬腿）。
- 違規碼集增減（例：新政策鍵）⇒ 同批改後端常數、page 樹三語子鍵與明細型，複核決定 1。
- 憲法 §I.3 信封形或 13 碼矩陣變更 ⇒ MAJOR、重審本 ADR。
