# 007-user-password-admin — 使用者管理與密碼治理（使用者頁全套＋個人中心自助改密＋斷權與密碼政策＋繁中介面＋島 I 入憲）brainstorm

> 路徑＝architectural（superpowers:brainstorming；產出路徑依 CLAUDE.md §2 覆蓋為本檔）；終點＝user 確認後顯式 `/speckit-specify`（本專案不叫 writing-plans）。
> 取證＝唯讀十一軌（rev5 藍本三軌／rev6 後端與前端／憲法與 ADR 義務／延後義務／鎖序／測試基建／拍板分歧對照／BACKLOG 吸收）各接反駁＋完備性評審（23 支、零失敗）；主線逐項 grep 親核、更正兩處（契約測試行號、ADR-00068 款 20 新義務）；答畢後再盤連動（繁中、三頁按鈕碼、兩處解鎖入口、逐域 no-op、滯後卷）。

## 0. 拍板紀錄（全數 user 拍板 2026-10-05；一題一問、首選項皆為建議）

| 題 | 拍定 | 要點 |
|---|---|---|
| 理解校正 | 正確 | 目標三塊：使用者管理頁全套／個人中心自助改密／斷權與密碼政策；藍本＝`rev5:007`（12 支、零 migration）；假設四項：①rev5 41 題＋grilling 18 題預設沿用、只在 rev6 事實或已拍板不同處重問 ②UI 以 rev5 HEAD 22080 為基準、刻意分岔逐項登記 ③觸發欄指名 007 之七條（BL-00031／BL-00048／BL-00065／BL-00091／BL-00124／BL-00136／BL-00138）逐條成題、其餘逐條評估可否順手收、拍板級才問 ④零 migration 為目標、需 DDL 先講代價；成功準則＝本檔定稿 commit 後等 user 令再 `/speckit-specify` |
| Q1 首登強制改密 | **不做、新記 BL** | 003 刀 spec Out of Scope 排給 007 之項再延一次、改由主檔新記 BL-00140 承載（觸發＝008 brainstorm 起手前重評或出現實際需求、先到者）；島 I 之 I6 照 `rev5:007` 留空並寫明原因（條文落字 U0 親決） |
| Q2 信箱驗證／寄信／個資自助 | **不做、記入滯後卷**（非建議項） | email-verify／mailer／getProfile／updateProfile 不做、不下 won't-fix；滯後卷新記 BL-00141（與 Q3 手機驗證合併）；DB 表與 mailpit 設定維持「接而不讀」、config.rs 該句改指該條 |
| Q3 個人中心射程 | **只放改密卡、手機驗證延後** | 改密卡只舊密碼一路；手機驗證與 Q2 同形入 BL-00141（rev6 003 spec 只寫「尚未開放」、無終態 ADR）；BL-00138② 移交該條 |
| Q4 繁中介面 | **007 接上繁中**（非建議項） | LangType 擴 zh-TW、locale／naive／dayjs 註冊、語言下拉三語、zh-tw.ts 標型為完整 Schema 全樹；修憲開 I18N (iii)、各列「兩語鍵集相等」改三語；此後每刀三語同批；BL-00138① 本刀兌現；zh-TW 畫面無 rev5 基準＝刻意分岔（新能力） |
| Q4a 預設語言（補問） | **預設改為繁中** | 三處「未選過＝zh-CN」改 zh-TW；下拉「简体中文／繁體中文／English」；首次開啟與 rev5 不同＝刻意分岔登記；CDP 對照顯式設語言 |
| Q5 系統設定頁 | **不提前、留 008** | BL-00045 不動；CDP 排除清單列系統設定與稽核兩死項 |
| Q6 寫端下放之守門 | **可下放＋包含規則入憲** | T⊆A∧N⊆A（持 R_SUPER 者 A＝全集）；8 支寫端＋unlockLogin 帳號維；入憲島 I7；零 migration；ADR-00064 觸發器首條成立 |
| Q7 包含規則射程 | **只用在使用者域＋解鎖帳號維** | rev5 9 消費點；角色域、IP 域與授權回收桶復原續 ADR-00068 款 9 已知態、新 ADR 寫複核結論與不掛理由 |
| Q8 按鈕碼顯隱射程 | **三頁一起做**（非建議項） | 使用者頁七碼＋角色頁、選單頁依既有 add／edit／delete 碼逐鈕顯隱；ADR-00068 款 18 全解除；修憲改寫 (ii)／(iii) 列「門在頁級」字面；與 rev5 角色／選單頁可見差異＝刻意分岔；★衍生自鎖風險見 §3 §4 R10（處置未決、grilling 輪定） |
| Q9 解鎖入口 | **帳號放使用者列操作、來源 IP 放 IP 規則頁**（非建議項） | 使用者列操作加「解鎖登入」（標的＝該列帳號、套包含規則）；IP 規則頁加來源 IP 解鎖（彈窗輸入、不套包含規則）；兩入口同一 wrapper；修憲＝使用者頁用途含列解鎖＋IP 規則頁新用途；BL-00091 收、ADR-00069 款 1 解除；與 rev5 UI 不同＝刻意分岔 |
| Q10 解鎖鈕表頭位置 | **作廢** | Q9 取列操作＋IP 規則頁、使用者頁表頭無解鎖鈕 |
| Q11 自助頁可達 | **程式內自助白名單** | getUserRoutes 恆併入 `["user-center"]`；另立 ADR 說明與 §I.2 關係（承 `rev5:ADR 0065`）；route.rs 前代歸因勘誤（rev4:014 起源、`rev5:007` U4 帶回）；005 照帶之「不帶回」前提隨本刀消失 |
| Q12 換發活性重驗 | **加、rev5 形** | 票列鎖後、簽發前 plain 讀帳號（啟用且未刪才放行、查無列＝不活）；不取 advisory、換發鎖序不變；不做每請求判定；refresh 10＋logout 1 案改種帳號列 |
| Q13 持停用角色之抽屜 | **灰色保留選項** | 持有之停用角色以「（已停用）」標籤呈現、不可新選、可移除、送出預設保留；清單帶持有角色 id 與名稱；`rev5:B-145` 結案、ADR-00068 款 7 解除；刻意分岔 |
| Q14 清單 wire 偏離 | **記偏離帳、沿 rev6 欄名** | 比照 ADR-00044 決定 9；差集由 wire 裁判機器導出、漂移即紅 |
| Q15 同值寫入 | **照 rev5：同值不寫不記**（非建議項） | 使用者域（updateUser＋updateUserSessionPolicy）缺席早退後再值 diff：同值＝零寫、零稽核、不 bump 時戳；角色選單域續 ADR-00047 決定 3；新 ADR 續行 ADR-00047 記逐域差異 |
| Q16 空字串 | **＝清空落 NULL** | 可空文字欄新增與更新同形；Q15 之值 diff 於歸一後比對；同一支 ADR 續行 ADR-00047 擴入使用者域 |
| Q17 搜尋卡兩欄 | **後端補兩欄＋放寬搜尋卡** | 後端六欄模糊過濾（§I.1）；user-search.vue 入本刀用途名單、兩欄拔格式驗證；刻意分岔 |
| Q18 錯誤明細 | **開、只限兩鍵** | passwordPolicy{violations}／pwdSetTooFrequent{remainingSeconds}；違規子鍵落 page 樹（三語）；修 I18N (i)、002 wire 契約 §3 第 3 條與 envelope 釘案 |
| Q19 min>max | **設密全拒＋告警** | 寫端不守；跨島註記與島 E 整組退方向相反之理由；BL-00031 收 |
| Q20 改密節流 | **做（5 次／15 分）** | argon2 前判、成功即清、窗自癒、純 key；載體 redis（工程判斷）；BL-00124 隨四面比較收 |
| Q21 seed 指派殘列 | **射程外＋補還原能力** | spec 具名排除形②；restore 與測試守衛補 seed 指派回補（含 sys_user 新列刪除、序列回值）＋自測；BL-00136 收 |
| Q22 seed 欄值殘列 | **射程外＋補欄值寫回** | restore 擴 seed 帳號可變欄回寫（含密碼 PHC 與審計欄）＋自測；測試面快照守衛 |
| 設計四節 | 全核可 | 節 1 方案、範圍、修憲、ADR／節 2 後端／節 3 前端／節 4 測試、工具、驗收（即 §3） |

**主線工程判斷**（CLAUDE.md §5 自拍、回報備查）：①ADR-00014 照 user 2026-09-07「走 BL 對沖、不翻案」——其決定 1 只管 5003，密碼違規明細（2222）不在射程；BL-00048 以兌現連動面收（enforce.rs 模組註與 `no_escalation_check` doc 兩處預告、002 FR-013 讀法），規則本體入島 I ADR；ADR-00064 觸發器首條「填入掛點本體」之字面由該 ADR 說明實際落點（handler 鎖內純函式、掛點續恆放行）②G5 末句照字面：指派寫端於使用者列鎖後依角色 id 去重升序 `FOR UPDATE`、鎖內重驗未軟刪；批次寫端整批聯集一次升序；偏離 `rev5:007` research R4（只讀不鎖）記 rev6 差異點；ADR-00043 決定 8 無 ABBA 論證於 ADR 重核（角色域寫端不取 per-user 鎖、指派寫端不入選單序列化域＝不成環）③改密節流載體＝redis `cpwd:{uid}`、fail-open、降級源 10→11（名冊雙向守與「恰十」數量詞同批）；007 ADR 一句釐清 ADR-00038 射程限登入節流④使用者域寫端零授權重載（`rev5:007` Q27 翻案不帶回）⑤不加每請求活性判定（BL-00065 題 b；沿 `rev5:007` 島 I2、零行為變更）⑥ADR-00068 決定 4① 收回例外（回紀律常態：觀察用自建帳號持自建角色）、款 11 續作已知態改述、款 20 改述並實測可達⑦ADR-00070 觸發器④列實測義務；⑤屬發生式、走查不造第二個可編輯角色之人⑧ADR-00043 決定 8 三失效條件記「已核未觸發」⑨ADR-00037 觸發器反向確認（改密為 Authed、按 uid 節流）⑩拒因譯文對 rev5 口徑照 ADR-00049／ADR-00050（zh-TW 無 rev5 基準、以人工檢讀）⑪修憲條文措辭（島 I 條號與 I6 空缺 header、I7 具名 R_SUPER、I1 鎖句、I5 釐清句直接併入、島 B／C 用語消歧）留 U0 親決輪⑫dev 庫寫入照 LL-00053 於 tasks 逐步標 user 放行⑬三頁按鈕對碼（Q8）：角色頁 新增→`role:add`、刪除與批刪→`role:delete`、編輯→`role:edit`；選單頁 新增與新增子選單→`menu:add`、編輯→`menu:edit`、刪除與批刪→`menu:delete`（seed 列 58～63、R_SUPER 皆持＝零 migration）；選單回收桶「復原」與角色抽屜三顆授權鈕不設碼（其讀寫屬封死集、非超管連已刪清單或授權現況都載不出＝ADR-00068 款 10 形）⑭IP 規則頁來源 IP 解鎖鈕以既有 `user:unlock` 碼顯隱（一支 API＝一個能力碼、零 migration）、放 prefix 插槽（rev5 無此入口＝無對照基準）⑮滯後卷：Q2＋Q3 合併為 BL-00141、BL-00138 於本刀收單（①由 Q4 兌現、②移交 BL-00141 並互指）⑯CDP 對照 22080 之步驟一律顯式設 `lang`＝zh-CN（cdp.mjs 現無語言設定）；zh-TW 譯文以 Taiwan 用語人工檢讀。

## 1. rev5 承襲盤點（沿用項照已驗證結論施工、翻案項用新設計；CLAUDE.md §2）

| rev5 項目（括號題號＝`rev5:007` brainstorm 題號） | 處置（括號 Q＝本檔 §0 題號） | rev6 落點 |
|---|---|---|
| 12 支端點射程（管理面 10＋個人中心 2；profile／email 不進；`rev5:007` Q01） | 沿用；ROUTES 49→61；seed 政策列與七枚 `user:*` 按鈕碼、`manage_user` 選單列兩代逐列相同（21 列）⇒零 seed 變更 | router／handler |
| 零 migration（Q05） | 沿用；m0001 已含 session_event／sys_pwd_custody／sys_user_email_verify／兩活性唯一索引 | 反向確認 migration 恰 m0001／m0002 |
| 寫端固定序（①活性標的鎖讀②seed 保護③self 五不④no-escalation⑤業務守門）＋逐支空格（kick／reset 空②、會話政策空②③、restore 到不了②③）；seed 三帳號保護（Q11）；self 規則（G3、G25）；同級互管（G2）；批刪整批 rollback、空陣列 no-op（G4）；已刪標的一律 notFound（G5） | 沿用；空格逐支以測試釘住 | handler／facade |
| 包含規則 T⊆A∧N⊆A、T 不濾停用、A＝現役（Q09／Q09-1／Q09-2／Q28、G1、G6、G24） | 沿用（Q6、Q7）；T 讀端新建 | 島 I7；no-escalation 純函式 |
| 斷權：停用／刪除／重設／自助改密同交易撤全部 active＋best-effort denylist；kick 撤全 active、不動 rotated（Q13、Q15） | 沿用；reuse 偵測形不變（島 A） | sys_token 撤票原語 |
| refresh 鎖內活性重驗（Q15★） | 沿用（Q12） | refresh.rs |
| 不加每請求活性判定（島 I2） | 沿用（工程判斷⑤） | — |
| admin_kick 第三 reason＋`auth.session.kickedByAdmin`、enforce 與 refresh 三向分派（Q14、G9） | 沿用；島 C「兩 reason」句與島 B「踢除」用語於 Amendment 改述 | enforce.rs／refresh.rs／error.rs |
| 軟刪同交易硬刪指派、復原零回灌、status 保留（Q16） | 沿用；答 ADR-00044 觸發器①（in-use 口徑不必改：軟刪者已無指派） | facade |
| updateUser no-op＝缺席早退再值 diff（Q17、§4.7-②） | 沿用（Q15；與 rev6 角色選單域分岔、新 ADR 記逐域差異）；會話政策寫端同形 | facade |
| 空字串：新增摺疊、更新不摺疊（`rev5:007` R2-1、§4.7-③） | 翻（Q16）：空字串＝清空落 NULL、新增與更新同形 | 續行 ADR-00047 |
| 密碼政策整套（單一驗證點、八鍵、字元數＋位元組上界、三重不洩、登入不驗；Q18；I5 釐清＝`rev5:ADR 0068`） | 沿用；位元組上界引 `LOGIN_PASSWORD_MAX_BYTES`＝512；政策鍵只在消費當下讀現值 | password.rs |
| BizData 明細通道（Q19） | 沿用（Q18）；rev6 三處既有約束不同（I18N (i) 列、跨端閘無白名單、error.rs 不帶）⇒修憲一列＋違規子鍵落 page 樹 | error.rs／envelope.rs／前端 |
| min>max 安全側恆拒（password.rs 註） | 沿用並補告警（Q19） | password.rs＋告警出口 |
| 設密冷卻（借 custody 時戳、維度（標的, 操作者）、addUser 亦寫；Q20、G13、G14） | 沿用 | facade |
| changePassword 流程（兩次一致→舊密→新≠舊→政策；成功撤他 session、保留當前；Q21） | 沿用；Identity 補 sid | handler／auth |
| getPasswordPolicy＋前端動態規則（Q26） | 沿用；檔位照 rev5 as-built（components/custom、hooks/business） | 後端＋base-web |
| 改密舊密節流 5 次／15 分、成功即清、窗自癒（Q30、G12） | 沿用（Q20）；載體 redis（工程判斷③） | throttle |
| 自助路由白名單（Q22） | 沿用（Q11）；rev6 005 照帶之「不帶回」前提（無個人中心端點）隨本刀消失＝明寫翻轉 | route.rs |
| seed 68 會話政策端點、三值收斂、改 single 不即時踢（Q23、§4.7-⑨） | 沿用；路由一註冊即入封死集＝兩支以「列 68 候選外」為前提之測試改植探針 | — |
| 解鎖入口＝使用者頁頁首彈窗、雙維（Q24、G6） | 翻（Q9）：帳號維＝使用者列操作、來源維＝IP 規則頁；帳號維套包含規則、來源維不套（G6 沿用） | 使用者頁／IP 規則頁 |
| 登入表單帳號與密碼兩欄只驗必填、不動 reg.ts（Q25） | 沿用；憲法 LOGIN-CAPTCHA (ii) 已指派本刀 | pwd-login.vue |
| 授權重載擴使用者寫端（Q27） | 翻（工程判斷④）：零重載 | — |
| 稽核詞彙增 kick／reset_password／change_password（Q29、G10、§4.7-⑩） | 沿用；封閉五詞→八詞＝ADR-00069 款 3 續行 | AuditOperation |
| 按鈕碼七碼逐鈕、角色與選單頁不 gating（Q10） | 擴（Q8）：使用者頁七碼＋角色、選單兩頁依既有碼 | 三頁 |
| page 樹補 zh-cn＋en-us、zh-tw.ts 只補 backend 樹（Q08） | 翻（Q4、Q4a）：zh-TW 接 runtime、全樹三語、預設繁中 | locales |
| 前端不預判包含規則、只鎖會話政策欄與本人列（G7、G8） | 沿用 | 抽屜 |
| 回收桶 toggle、已刪模式不加刪除時間欄、產密浮層、個人中心只改密卡（Q31～Q35） | 沿用（Q3） | base-web |
| 手機欄不守長度（`rev5:ADR 0069`）、信箱簡式格式＋活性唯一預檢（G16、§4.7-⑤⑥） | 沿用 | facade |
| addUser 預設啟用、允許零角色（G17）；userName 建後不可變（§4.7-④）；形制 `^[A-Za-z0-9_-]{1,64}$`（§4.7-⑧） | 沿用 | handler |
| 詞彙六條入活書 12（G23） | 沿用；與既有「撤銷三型」條消歧 | 活書 12 |
| 已消失 | `rev5:B-129`（006 已修）、`rev5:B-132`（005 已修）、`rev5:B-127` 映射收攏（005 已收）、POLICY_ENDPOINT_COUNT（rev6 無） | — |
| ★翻案不帶回（RL-0065） | ①Q27 授權重載 ②`[rev5-inline]` token（rev6 用 `rev6-inline`）③rev5 測試守衛名（改 rev6 test_kit 水位＋setval 形）④前代命名空間 `Api.UserAdmin`／`Api.UserCenter`（rev6 前綴 `rev6-`） | 全刀 |
| rev5 無藍本或 rev5 未解之 rev6 新題 | `rev5:B-145`（Q13）、`rev5:B-143`（Q17）、G5 角色列鎖（工程判斷②）、清單 wire 偏離帳（Q14）、BL-00136 形②（Q21）、seed 欄值殘列（Q22）、zh-TW runtime（Q4）、角色選單頁 gating（Q8）、IP 規則頁解鎖入口（Q9）、ADR-00068 款 20 與 ADR-00070 觸發器④之可達性實測 | 各節 |

## 2. BACKLOG 觸發項處置（14 開放＋3 滯後逐條對觸發欄；以 BACKLOG 現文為準）

| 分類 | 條目 | 007 的哪一步 |
|---|---|---|
| 收・本刀刪列 | BL-00031（Q19）｜BL-00048（Q6；兌現連動面）｜BL-00065（Q12；題 b 入島 I2 條文）｜BL-00091（Q9）｜BL-00124（Q20；四面比較以 rev6 形重做入 ADR）｜BL-00136（Q21）｜BL-00138（①由 Q4 兌現、②移交 BL-00141＝Q3） | 各單元／收刀 |
| 收窄・留列 | （無） | — |
| 反向確認 | BL-00047（零 migration⇒收刀前確認 migration 恰 m0001／m0002、演進帳 entries 空）｜BL-00108（本刀不於 rust 側新寫字元級解析 lint）｜BL-00043（改密、踢除不新增存取軌跡寫入面）｜BL-00133（本刀不觸授權歸檔表） | 收刀前體檢 |
| 不動 | BL-00045（008）｜BL-00002（user 2026-09-30 維持原觸發）｜BL-00139（觀測面） | — |
| 滯後卷 | BL-00049（三顆快速登入鈕刀期必留、登入路徑不驗政策）｜BL-00064｜BL-00067 | — |
| 本檔同批新記 | 主檔 BL-00140：首登強制改密排程錨（Q1）｜滯後卷 BL-00141：自助驗證與個資面（email-verify／mailer／getProfile／updateProfile／自助頁手機驗證；Q2＋Q3；★滯後 2026-10-05 user 拍板） | 本檔 commit |

淨效果（007 窗）：刪 7、新記 2＝−5。

## 3. 設計（四節、user 已核可）

### §1 方案、範圍、修憲、ADR

- **方案 A**（005／006 同形）：U0 修憲 → 後端底座（使用者 facade、包含規則、密碼政策單點、撤票原語）→ 讀端 → 寫端 → 會話面（換發重驗、三向分派）→ 個人中心端點（改密、政策讀、節流、自助白名單）→ 明細通道 → 裁判面 → 前端（繁中 runtime、使用者頁、三頁按鈕碼、浮層、兩處解鎖、個人中心、登入表單）→ 工具 → 文件 → CDP → 收刀前體檢。B 按 US 垂直切片（共用底座首片即須完整）、C 後端全先（前端單元過大、CDP 最晚）皆棄。
- **範圍**：12 支端點（getUserList〔六欄過濾〕、getDeletedUsers、addUser、updateUser、deleteUser、batchDeleteUser、restoreUser、kickUser、resetUserPassword、updateUserSessionPolicy、getPasswordPolicy、changePassword）；unlockLogin 帳號維掛包含規則；refresh 活性重驗；使用者頁全套（含列操作帳號解鎖）；角色、選單兩頁按鈕碼顯隱；IP 規則頁來源 IP 解鎖入口；重設密碼與產密浮層；個人中心改密卡；登入表單放寬；繁中 runtime（三語全樹、預設繁中）。
- **Out of Scope（逐條指承載）**：首登強制改密→BL-00140（Q1）；信箱驗證／寄信／個資自助／自助頁手機驗證→BL-00141（滯後卷；Q2、Q3）；系統設定與稽核兩頁→008（BL-00045）；使用者詳情頁→續留佔位（seed-view-gate 對賬、佔位檔不可刪）；包含規則延伸至角色、IP 域與授權回收桶復原→不做（Q7）；選單回收桶復原鈕與角色抽屜三顆授權鈕之按鈕碼→不設（工程判斷⑬）；每請求活性判定→不做（工程判斷⑤）；批次復原、匯入匯出、角色分級、middleware 帶 body、改 single 即時踢除、需 migration 之密碼歷史／過期／鎖定旗標→不做（`rev5:007` Out of Scope 同形）；角色寫端連動撤會話→不做（ADR-00043 決定 8 失效條件①未觸發）；即時推播刷新已登入者之選單與按鈕顯隱→不做（006 Q13 同形）。
- **憲法 Amendment（MINOR 1.7.1→1.8.0、一筆；條文字面於 U0 由 user 逐款親決）**：①島 I 入憲（I1～I5、I7；I6 照 rev5 留空並寫明原因〔Q1〕；以 `rev5:007` 島 I 字面為底、rev6 座標改寫；I1 角色列鎖句依工程判斷②；I2 含換發重驗〔Q12〕與「不加每請求活性判定」；I5 直接併入 `rev5:ADR 0068` 釐清句；I7 具名 R_SUPER 與否於親決輪定）②跨島重審結論（密碼政策壞值「設密全拒」與島 E「整組退」方向相反之跨島註〔Q19〕；I6／J2 空缺位）③島 C「`kicked` 與 `revoked` 兩 reason」改含 `admin_kick`；島 B「踢除」用語消歧（單會話頂替 vs 管理員踢除）④§III.2：MANAGE-PAGE 新用途——(v) 使用者管理頁（index.vue、抽屜、搜尋卡〔Q17〕、列操作帳號解鎖〔Q9〕、重設密碼與產密浮層、locale／app.d.ts）、(vi) 個人中心改密卡、(vii) IP 規則頁來源 IP 解鎖入口〔Q9〕、(viii) 角色與選單頁按鈕碼顯隱〔Q8；改寫 (ii)／(iii) 列「門在頁級、三鈕不做按鈕碼 gating」字面〕（用途號於親決輪定）；LOGIN-CAPTCHA (ii) 開立；I18N (i)「data 恆 null、不建 translateDetailValue」改寫〔Q18〕；I18N (iii) 開立 LangType 擴 zh-TW、locale／naive／dayjs 註冊、zh-tw.ts 標型重構、預設語言改 zh-TW〔Q4、Q4a〕，並把各列 page／route 樹之「兩語鍵集 MUST 相等」改三語（14 處逐處判讀）⑤承襲指針 I 列補 rev6 入憲載體；「九島」與 MAJOR 射程句；README 憲法版本鏡像。範圍欄預估、收刀前 PATCH 實數化（ADR-00051 前例）。
- **ADR 待立（feature branch 內、plan 期起草；proposed 期不宣告 supersedes、accepted 同顆補）**：①島 I 入憲（Amendment；provenance `rev5:ADR 0063`＋`rev5:ADR 0068`）②包含規則與射程分工（`rev5:ADR 0063` 款三形；9 個消費點、掛點續恆放行；ADR-00064 觸發器首條與次條之複核結論：判定序與拒因鍵不與撤銷、封死互吞、正交分工維持、授權回收桶復原不掛〔Q7〕；BL-00048 收）③明細通道射程與受眾（`rev5:ADR 0064`；修 I18N (i)、error.rs 增 BizData 變體〔「變體集恰九」數量詞同批；admin_kick 之 ModalLogoutByAdmin 另隨 ADR①〕、002 wire 契約 §3 第 3 條改述、envelope 釘案改寫、msg-key-gate 擴、違規子鍵落 page 樹〔Q18〕）④自助路由白名單（`rev5:ADR 0065`；§I.2 雙支柱〔Q11〕）⑤設密冷卻＋改密節流（`rev5:ADR 0066`；BL-00124 四面比較以 rev6 形重做；ADR-00038 射程釐清；降級源 10→11；cpwd 窗自癒＝ADR-00069 款 5 不觸發〔Q20〕）⑥密碼政策壞值方向與告警出口（BL-00031；跨島註〔Q19〕）⑦ADR-00047 續行（使用者域：空字串＝清空、新增同形〔Q16〕；no-op＝缺席早退再值 diff、同值零寫零稽核〔Q15〕；會話政策寫端同形；角色選單域續決定 3）⑧ADR-00068 續行 v3（決定 4① 收回；款 7＝B-145 結案〔Q13〕；款 9 使用者域與 unlockLogin 半因包含規則解除、其餘續存；款 10 改述〔角色選單頁有按鈕碼後之可見效果〕；款 11 改述；款 18 全解除〔Q8〕；款 20 改述＋實測）⑨ADR-00069 續行（款 1 解除〔Q9 兩入口〕；款 3 寫入者擴使用者寫端、封閉五詞→八詞）⑩清單 wire 偏離帳（ADR-00044 決定 9 形〔Q14〕）⑪繁中 runtime（supersede ADR-00039：zh-tw.ts 由治理錨點孤立檔改為 runtime 註冊之完整 locale、譯文之家三檔不變；預設語言 zh-TW；ADR-00049／ADR-00050 之「zh-tw 不在對照面」改述〔Q4、Q4a〕）⑫刻意分岔登記（灰色保留選項、搜尋卡驗證放寬、兩處解鎖入口、角色選單頁按鈕碼、預設語言與 zh-TW 畫面；可併入 spec 分岔表、是否另立 ADR 於 plan 期定）。

### §2 後端

- **交易與鎖**：handler 持交易、`<op>_in_txn` 首句取 per-user advisory（`advisory_lock_user`，既有 pub）→使用者列 `FOR UPDATE`（活性濾 `deleted_at IS NULL`、不看 status；restoreUser 鎖已刪列）→角色列依 id 去重升序 `FOR UPDATE` 並鎖內重驗未軟刪（工程判斷②）→指派表全量替換；batchDeleteUser 先 id 升序去重、同交易逐 id 取鎖；addUser 無既有 uid 可鎖、不取 advisory、同名並發由活性唯一索引 23505 兜底；指派寫端不入選單序列化域。
- **守門固定序**：①活性標的鎖讀②seed 保護③self 五不④包含規則⑤業務守門；任一拒＝整筆 rollback、零變更零稽核；kick／reset 空②、會話政策空②③（皆以測試釘空格理由）；拒因 2222＋純 key，包含規則違反＝5003（與封死、撤銷判定序不互吞）。
- **no-op 與空字串**：updateUser／updateUserSessionPolicy 先缺席早退，再於值域收斂（空字串＝NULL、roleIds 以集合比）後比對現值：同值＝零寫、零稽核、不 bump 時戳〔Q15〕；不可變欄 userName 出現即拒（與 rev6 codeImmutable 同形）。
- **斷權**：停用、刪除、重設密碼、自助改密同交易撤該帳號全部 active 票（迴圈形撤票原語、SELECT 帶頭）＋commit 後 best-effort denylist；kick 撤全部 active、不動 rotated；reason 三分（`kicked` 單會話頂替／`revoked` 撤銷／`admin_kick` 管理員踢除），enforce 與 refresh 兩處三向分派；換發於票列鎖後、簽發前 plain 讀帳號，不活或查無列＝8888〔Q12〕；不加每請求活性判定。
- **密碼**：政策單一驗證點（字元數上下界＋四類字元開關＋不得含帳號名＋位元組上界 512）；違規一次收集全部；min>max 自然全拒並落設定異常告警（告警出口於 plan 期定：不混用登入節流之 `settings_invalid` 源）〔Q19〕；雜湊於交易內、不持列鎖時算（I5 釐清）；設密冷卻借 custody 時戳；改密節流 redis `cpwd:{uid}`、argon2 之前判、成功即清、fail-open〔Q20〕；明細通道只兩鍵〔Q18〕。
- **寫入形與稽核**：操作稽核同交易、詞彙增 `kick`／`reset_password`／`change_password`；`real_ip` 缺席拒寫（島 F F3①同向）；角色鍵一律 `id`；清單固定序寫入契約（ADR-00058）；清單列帶持有角色 id 與名稱〔Q13〕。
- **解鎖**：unlockLogin 帳號維於上下文檢查之後、稽核之前掛包含規則（拒＝零稽核）、來源維不套；端點本體與「稽核先於標記」不變〔Q9〕。
- **自助白名單**：getUserRoutes 恆併入 `["user-center"]`〔Q11〕；route.rs 檔頭前代歸因勘誤。
- **其他**：msg 鍵 `biz.user.*`＋`auth.session.kickedByAdmin` 三語 backend 子樹同批、與 `MSG_KEYS` 跨端對賬；新讀型入 wire 裁判表；授權重載名冊零擴列（反向確認測試）；兩支「列 68 候選外」前提測試改植合成探針列；no-escalation 掛點不動。

### §3 前端

- **繁中 runtime**〔Q4、Q4a〕：`App.I18n.LangType` 擴 `'zh-TW'`；locale.ts／naive.ts（zhTW、dateZhTW）／dayjs.ts（zh-tw）註冊；語言下拉「简体中文／繁體中文／English」；預設語言三處改 zh-TW；zh-tw.ts 由裸 object 改為 `App.I18n.Schema` 標型之完整樹（現 66 行之 backend 子樹保留、補齊對齊 zh-cn.ts 855 行之其餘樹，Taiwan 用語）；TS 型即三語鍵集機器守、msg-key-gate 之 backend 三檔全等照舊；零新依賴（naive-ui 2.44.1、dayjs 1.11.20 已含繁中）。
- **使用者頁**（rev5 HEAD 形重打字）：清單接真（六欄搜尋、分頁、回收桶 toggle、已刪模式）；新增／編輯抽屜（roleIds 只在改動時送；持停用角色顯灰色保留選項〔Q13〕；非超管之會話政策欄 disabled＋提示、本人列狀態與角色欄停用）；刪除與批刪、復原、踢下線、重設密碼浮層（掛即時規則）＋產密浮層；列操作「解鎖登入」〔Q9〕；七碼逐鈕顯隱、新增與批刪走 showAdd／showDelete；搜尋卡兩欄拔格式驗證〔Q17〕。
- **角色頁、選單頁按鈕碼**〔Q8〕：依工程判斷⑬對碼逐鈕 `hasAuth`；表頭新增與批刪走既有 showAdd／showDelete 屬性；選單回收桶復原鈕與角色抽屜三顆授權鈕不設碼。
- **IP 規則頁**〔Q9〕：表頭 prefix 插槽加「解鎖來源 IP」鈕（`user:unlock` 顯隱）與彈窗（輸入 IP）；與帳號解鎖共用同一 wrapper。
- **個人中心**：index.vue 改真頁、只掛改密卡（舊密碼一路）；政策 hook 動態規則；成功後保留當前會話。
- **登入頁**：pwd-login.vue 帳號與密碼兩欄只驗必填、不動 reg.ts、captcha 軟區零變更、三顆快速登入鈕必留。
- **錯誤明細**：request/index.ts 建明細轉譯（只兩鍵）〔Q18〕；違規子鍵落 page 樹三語（兩頁共用命名空間於 plan 期定）。
- **API 包裝與型別**：`rev6-` 前綴新檔（§III.1 BASE-WEB-WRAPPER）；upstream 舊函式無畫面消費（偏離帳〔Q14〕）；兩份 fetchGetAllRoles 擇一。
- **fork-delta 與修憲銜接**：各新用途範圍欄預估、收刀前 PATCH 實數化；使用者頁與角色、選單頁之表頭照 view-render-guard 既有守則（不覆寫預設插槽）；fork-delta-lint 對賬腿照舊。

### §4 測試、工具、驗收

- **測試**（rust 容器內 serial；base-web pnpm 容器內）：島 I 不變式逐條；寫端固定序與逐支空格；包含規則 9 消費點正負向；指派寫端與 deleteRole 併發（角色列鎖之鎖內重判）；值 diff no-op（同值零稽核、異值照寫）；換發活性重驗（refresh 10＋logout 1 案改種帳號列＋清理守衛）；三向分派；設密冷卻、改密節流、min>max；明細通道與 envelope 契約改寫；殘列不連坐（seed 政策列錨照 006、形②與欄值殘列具名排除〔Q21、Q22〕）；ADR-00044 觸發器②之 in-use／self-role 生產可達；login 第⑤步鎖內密碼比對併發測試（寫端進場後首次可測）；base-web vue-tsc 型檢（三語 Schema）；wire-schema、msg 鍵跨端閘、authz_entrypoint_lint、route-artifact-gate、fork-delta-lint、seed-view-gate、view-render-guard 全綠；ROUTES 改動單元另跑 `python3 -B tools/docsync test`。
- **工具**：`tools/walkthrough-baseline.py` restore 擴面——被刪 seed 指派回補、sys_user 新列刪除與序列回值、seed 帳號可變欄回寫（含密碼雜湊與審計欄）、sys_pwd_custody 清理、redis `cpwd` 前綴清除，並附自測；test_kit 守衛同理；RUNBOOK §9c 契約同批。
- **驗收**：觸及之島不變式全過；CDP 三方對照（22080 對 32080，必要時加 22089；對照步驟顯式設 `lang`＝zh-CN；對照面＝使用者頁全套、角色與選單頁按鈕、浮層、兩處解鎖、個人中心、登入頁；CDP 一律 opus[1m] xhigh）；刻意分岔逐項登記（灰色保留選項、搜尋卡驗證、兩處解鎖入口、角色選單頁按鈕碼、預設繁中與 zh-TW 畫面、實作期新發現者）；zh-TW 畫面逐頁人工檢讀（無 rev5 基準）；CDP 排除清單（系統設定與稽核兩死項）；ADR-00070 觸發器④（只改名稱不被擋）與 ADR-00068 款 20 可達性實測；走查基準本機自取 snapshot、前後還原 diff rc 0；dev 庫寫入步驟逐步取 user 放行（LL-00053）。
- **現在式假述掃除**（RL-0011、`python3 tools/docsync errata` 枚舉）：「使用者域刀」「使用者角色指派寫端」「007 刀」三詞全 repo 逐處判讀；「屬後刀域、不帶」「不搬」類碼註（error.rs、auth、cache、refresh、password、sys_user、sys_token 等；實集以 errata 枚舉逐處判讀為準）；Cargo.toml 兩處「不產 hash」類句；obs.rs「恰十」；route.rs 歸因；「門在頁級」（憲法、role-operate-drawer.vue 碼註、活書 05／06／08；policy-archive 頁者留）；「zh-tw 不接 runtime／孤立檔／延前端 UI 刀」（憲法、zh-tw.ts 檔頭、活書 08）；憲法「兩語」14 處；活書 06／08／10／11／12、RUNBOOK §9「無 UI 按鈕」句；rev5-blueprint-map 隨刀列。
- **單元草案**（約 23 支；tasks 定稿於 SDD）：U0 前置體檢＋Amendment 親決＋施工前提 ADR accepted → U1 骨架（ROUTES 49→61 空殼＋授權態矩陣＋探針改植）→ U2 測試基建（使用者清理、seed 帳號快照、指派回補守衛前移）→ U3 使用者 facade（鎖讀、T 讀端、指派全量替換＋角色列鎖、撤票原語）→ U4 密碼政策單點＋冷卻＋壞值告警 → U5 包含規則純函式＋讀端兩支 → U6 新增與編輯（值 diff no-op）→ U7 刪除、批刪、復原 → U8 踢除、重設、會話政策 → U9 換發重驗＋三向分派＋fixture 改造 → U10 個人中心兩端點＋改密節流＋sid＋自助白名單 → U11 解鎖帳號維＋稽核詞彙 → U12 明細通道 → U13 wire／msg 裁判面 → U14 繁中 runtime 註冊＋預設語言＋zh-tw 標型 → U15 zh-TW 全樹譯文 → U16 使用者頁 → U17 浮層、列解鎖、IP 規則頁解鎖 → U18 角色與選單頁按鈕碼 → U19 個人中心、登入表單、明細轉譯 → U20 走查還原工具擴面 → U21 文件、ADR 續行、假述掃除 → U22 CDP 三方對照＋zh-TW 檢讀 → U23 收刀前承載體檢＋範圍欄 PATCH 實數化。
- **風險**：R1 seed 帳號被改後回不來（U2／U20）；R2 換發 fixture 大面改造（U9）；R3 包含規則與封死、撤銷判定序互吞（U5、ADR②）；R4 明細通道改既有契約（U12）；R5 CDP 基準為 rev5 HEAD 而 rev6 預設繁中（對照顯式設語言）；R6 errata 面廣（含「兩語」14 處）；R7 dev 庫寫入放行（LL-00053）；R8 BL-00049 條件依賴（快速登入鈕必留）；R9 zh-TW 全樹譯文量（約 855 行）與用語一致性（U15、人工檢讀）；★R10 角色頁按鈕碼自鎖（Q8 衍生；user 2026-10-05 轉入外部提醒、裁「後續安排解決方案、grilling 本檔時提出」＝**處置未決**）：超管所持 `role:*`／`menu:*` 碼（seed 列 58～63）為非受保護授權、可於「按鈕權限」彈窗自撤；撤 `role:edit`＝角色頁編輯鈕消失，而選單、按鈕、端點三顆權限彈窗只掛在角色編輯抽屜之編輯模式＝無 UI 回復路徑；按鈕維撤銷不可自授權回收桶復原（006 Q2）⇒只能直打 API 或改庫。處置候選（grilling 輪由 user 定）：①角色頁編輯鈕不套顯隱 ②R_SUPER 名下該等碼改受保護（seed migration、BL-00047 到期）③按鈕維寫端擋撤 R_SUPER 之 `role:edit` ④後端對 R_SUPER 恆回全按鈕碼 ⑤記已知態＋救援步驟入 RUNBOOK。

## 4. 憲法 §IV 九題預答（供 `/speckit-plan` Constitution Check 起手）

1. base-web 為權威：PASS——使用者頁、個人中心、角色與選單頁、IP 規則頁皆為 upstream 既有面、其呼叫之端點正是本刀補齊對象；搜尋卡兩欄由後端補齊（§I.1）；郵件與個資不做而入滯後卷（upstream 個人中心為佔位、無個資 wrapper＝不違 §I.1）。2. base-web inline：**涉及——授權以 Amendment 先行取得**（§III.2 新用途四列、LOGIN-CAPTCHA (ii)、I18N (i)(iii) 改寫）。3. casbin：PASS——使用者寫端零 casbin_rule 寫入；三頁按鈕碼由 `getUserInfo` 按鈕集導出；自助白名單與 §I.2 關係另立 ADR。4. §I.3：**涉及**——清單型偏離帳（Q14）；明細通道使錯誤信封 data 於兩鍵非 null（Q18）；13 碼零觸碰（admin_kick 共用 7777）。5. 前代 source：否——重打字消化、翻案四項不帶回。6. §II：無抵觸。7. ★ 軌道：觸及——新用途、須 Amendment（§V.2；user 親決）。8. 建業務表／migration：否——零 migration、零 seed 變更；BL-00047 不到期。9. §I.7：觸及——島 I 隨本刀以 MINOR 入憲；島 B／C 用語與跨島註同顆；以狀態機鏡頭設計（帳號啟停刪復、會話撤銷三型、密碼設定冷卻與節流），非 CRUD 格子。

## 5. 給 `/speckit-specify` 的輸入摘要

- feature 名＝`007-user-password-admin`；user 故事核心＝US1 超管管理使用者（清單、新增編輯、刪除批刪、回收桶復原、按鈕碼顯隱）／US2 斷權（停用、刪除、重設、踢除即時撤會話；換發重驗）／US3 密碼政策與自助改密（政策單點、冷卻、改密節流、明細提示、個人中心可達）／US4 委派治理（寫端下放＋包含規則、兩處解鎖入口、角色與選單頁按鈕碼）／US5 繁中介面（三語、預設繁中）；12 支端點、零 migration、憲法 1.8.0。
- 直接輸入：本檔＋§2 處置表所列 BL＋`rev5:007-user-password-admin` spec 之 US、FR、SC、Edge Cases（rev6 座標改寫：ROUTES 49→61、seed 列號以 rev6 現數、handler 持交易形、rev6 test_kit 守衛形、CDP 基準 rev5 HEAD）。
- FR 措辭要求：寫端固定序與逐支空格寫成表；包含規則判定位次與拒因寫明不互吞；斷權寫成「同交易撤票＋換發重驗、不做每請求判定」兩層；no-op 寫成「缺席早退＋值 diff」並註明與角色選單域不同；殘列不連坐 SC 具名排除形②與欄值殘列；三頁按鈕對碼表；★spec 須含「★ 軌道逐處登記」表與「刻意分岔登記」表；Out of Scope 逐條指承載。
- clarify 候選：違規子鍵命名空間（兩頁共用或分置）；告警出口形（新 metric 族或新 source 值）。

## 6. 隨做隨記

- ADR 待立見 §3 §1；plan 期全數產 draft；Amendment 顆只含島 I ADR 與其連動條文、其餘另顆。
- 收刀 `backlog_done` 7 條（BL-00031／BL-00048／BL-00065／BL-00091／BL-00124／BL-00136／BL-00138）；本檔同批 `backlog_add` 2 條＝BL-00140／BL-00141（隨下一筆 events 事件入帳）。
- NOTES「下一步」：specify 起手後同批改為 007 進行中；收刀時改 008（008 起每刀三語同批）。
- ★grilling 輪必提：§3 §4 R10（角色頁按鈕碼自鎖、Q8 衍生、處置未決）；定案前不得把 Q8 之角色頁顯隱寫成 spec 定稿。
- 依賴：零新依賴（argon2 0.6.0 與 getrandom 0.4.3 已為直接依賴；dummy PHC 已走 `hash_password_with_salt`；naive-ui 2.44.1 與 dayjs 1.11.20 已含繁中）——毋須版本拍板。
- 走查基準本機自取（`.specify/feature.json` 仍指 006＝specify 起手後更新）；006 終態基準於本刀自取基準後才可清。
- 活書：06（島 I 情境）、08（user_memo 句、i18n 三語）、10、11、12（使用者域詞組、「撤銷三型」消歧）、RUNBOOK §9／§9c／§12 於 feature branch 內改成現在式；C4-L2 拓樸不變（零新容器）。
