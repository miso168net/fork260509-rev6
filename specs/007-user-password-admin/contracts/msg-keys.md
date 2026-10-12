# Contract — 本刀 msg 鍵（新增 22 鍵、攜參明細兩鍵、違規子鍵命名空間）

> 本檔凍結本刀新增 msg 鍵之鍵名、碼、發出點、首發單元、譯文起草值、攜參明細之 data 形、違規子鍵之 i18n 落點，以及跨端閘與名冊雙向閘之兌現面與落地時序。
> ★權威分工：鍵集＝`rust-api/server/src/error.rs` 之 `MSG_KEYS`（鍵數之單一來源＝其型別長度；碼註、標記註解與文件凡需提及鍵數者一律指向 `MSG_KEYS`／跨端閘輸出＝ADR-00039 決定 3）；譯文之家＝三檔 locale 各自之 `backend` 子樹（憲法 §III.2 `BASE-WEB-I18N-WIRING` (ii)「不另立譯文表」、ADR-00039 決定 2，本刀 ADR-00084 supersede 後此款續行）。★本檔各表之譯文欄＝落地單元寫入三檔 locale 之**起草依據**（plan 期主線定案之擬稿）：落地即以三檔 locale 為唯一權威、本檔不回頭同步、不作現行譯文之引用出處。
> 鍵名預設沿 `rev5:007` 名冊（spec FR-004）。zh-cn／en-us 譯文取 rev5 HEAD 三檔 locale 同鍵實文（ADR-00050 續行 ADR-00049 之判準「純換句話說者逐字對齊 rev5」：本刀 21 支沿用鍵之判定面相對 rev5 皆無語意延伸，見 §1.2）；`biz.menu.protectedButtonRemove` 為 rev5 所無之新守門（刻意分岔＝spec 分岔表「選單編輯移除按鈕碼」列、ADR-00086），三語新擬。zh-tw 以 rev5 `src/locales/langs/zh-tw.ts` 同鍵為底、依 §1.3 臺灣用語新擬（繁中畫面無 rev5 基準、不在 CDP 對照面；驗收照 spec SC-009）。
> 拒因碼面：業務拒因一律 `2222`＋純 i18n key、一因一鍵；**唯二例外**＝`biz.user.passwordPolicy`／`biz.user.pwdSetTooFrequent` 經攜參明細通道（`AppError::BizData`；ADR-00076）；包含規則違反＝`5003`＋`system.forbidden` 恆純 key、**不屬新鍵**；13 碼矩陣與可發碼集零觸碰；`AppError` 變體 9→11（`BizData`／`ModalLogoutByAdmin`）。wire 端點行為見 `contracts/wire-user-admin.md`、`contracts/wire-user-center.md`（錯誤信封之 data 上 wire 形＝其 §3）；閘與測試基建之施工面見 `contracts/code-gates.md`；常數名冊同列於 data-model §11。

## §1 新鍵 22

### 1.1 鍵表（表序＝`MSG_KEYS` 尾端追加序）

判定步編號沿 spec FR-010 之寫端固定序：①活性標的鎖讀 ②seed 保護 ③本人規則 ④包含規則 ⑤業務守門；changePassword 沿 FR-036／FR-037 之步序。首發單元＝首個在契約測試真 seed 應用面實際發出該鍵之單元（research R23 之單元切分；單元號以 tasks 為準）。

| # | 鍵 | 碼 | 發出端點與判定步 | 首發單元 | zh-cn | en-us | zh-tw |
|---|---|---|---|---|---|---|---|
| 1 | `biz.menu.protectedButtonRemove` | 2222 | updateMenu：按鈕清單移除集（含改碼＝移除舊碼）含尚有受保護授權列（`casbin_rule` 按鈕維 `protected=TRUE`）之碼＝整筆拒；判定於歸檔之前、與受保護選單守門並列（spec FR-043、ADR-00086） | U4（m0003 與選單刪碼守門） | 按钮列表不可移除或修改仍有受保护授权的按钮编码 | Button codes that still have protected policies cannot be removed or changed | 按鈕清單不可移除或變更仍有受保護授權的按鈕代碼 |
| 2 | `biz.user.notFound` | 2222 | ①查無活性標的（不存在或已軟刪；body 缺席或壞形收斂之預設 id 同）：updateUser／deleteUser／batchDeleteUser（任一 id）／kickUser／resetUserPassword／updateUserSessionPolicy；restoreUser 之已刪列鎖讀查無；changePassword 之本人列鎖讀查無（並發刪除之殘窗；步位以 `contracts/wire-user-center.md` §2 為準） | U8（addUser＋updateUser） | 用户不存在 | User not found | 使用者不存在或已刪除 |
| 3 | `biz.user.userNameInvalid` | 2222 | addUser ⑤帳號名形制不符 | U8 | 用户名格式不正确 | Invalid username format | 使用者名稱格式不合法 |
| 4 | `biz.user.userNameExists` | 2222 | addUser ⑤現役同名（先驗；現役唯一索引違反之兜底同鍵）；restoreUser ⑤同名現役列存在 | U8 | 用户名已存在 | Username already exists | 此使用者名稱已被現有使用者使用 |
| 5 | `biz.user.userNameImmutable` | 2222 | updateUser ⑤ body 帶 `userName`（出現即拒、值不比對） | U8 | 用户名不可修改 | Username cannot be changed | 使用者名稱建立後不可修改 |
| 6 | `biz.user.userEmailInvalid` | 2222 | addUser／updateUser ⑤信箱簡式格式不符（空字串＝空值、不判格式＝ADR-00080） | U8 | 邮箱格式不正确 | Invalid email format | 信箱格式不合法 |
| 7 | `biz.user.userEmailExists` | 2222 | addUser／updateUser ⑤現役同信箱（不分大小寫、只比現役列；唯一索引兜底同鍵）；restoreUser ⑤同信箱現役列存在 | U8 | 邮箱已被使用 | Email already in use | 此信箱已被現有使用者使用 |
| 8 | `biz.user.roleNotFound` | 2222 | addUser／updateUser ⑤角色集含不存在或已軟刪之角色 id（含角色列 `FOR UPDATE` 後之鎖內重驗＝research R7）；整筆拒、不略過 | U8 | 角色不存在 | Role not found | 指派的角色不存在或已刪除 |
| 9 | `biz.user.seededProtected` | 2222 | updateUser ②（id 1 之期望角色集不含 R_SUPER）；deleteUser ②／batchDeleteUser ②（含 seed 三帳號任一） | U8 | 内置账号受保护 | Built-in account is protected | 系統內建帳號受保護：不可刪除，超級管理員帳號亦不可移除超級管理員角色 |
| 10 | `biz.user.superCannotDisable` | 2222 | updateUser ②（id 1 之狀態轉停用） | U8 | 超级管理员不可停用 | Super administrator cannot be disabled | 超級管理員帳號不可停用 |
| 11 | `biz.user.cannotEditSelfRoleOrStatus` | 2222 | updateUser ③本人 body 帶 `status` 或 `roleIds`（出現即拒、值不比對） | U8 | 不能修改自己的角色或状态 | Cannot change your own roles or status | 不可修改您自己帳號的角色或狀態 |
| 12 | `biz.user.passwordPolicy`（攜參） | 2222 | addUser ⑤、resetUserPassword ⑤之密碼政策違規；changePassword 之政策步；data＝§2.1 | U8 | 密码不符合安全策略：{violations} | Password does not meet the policy: {violations} | 密碼不符合安全政策：{violations} |
| 13 | `biz.user.cannotDeleteSelf` | 2222 | deleteUser ③／batchDeleteUser ③（含本人整批拒） | U9（刪除、批刪、復原） | 不能删除自己 | Cannot delete yourself | 不可刪除您自己的帳號 |
| 14 | `biz.user.cannotKickSelf` | 2222 | kickUser ③ | U10（踢除、重設、會話政策） | 不能踢除自己 | Cannot kick yourself | 不可踢除您自己的帳號 |
| 15 | `biz.user.cannotResetSelfPassword` | 2222 | resetUserPassword ③（本人改密走個人中心） | U10 | 请到个人中心修改自己的密码 | Change your own password in the user center | 請至個人中心修改您自己的密碼 |
| 16 | `biz.user.sessionPolicyInvalid` | 2222 | updateUserSessionPolicy ⑤三值（`inherit`／`single`／`multi`）以外 | U10 | 会话策略无效 | Invalid session policy | 工作階段政策不合法 |
| 17 | `biz.user.pwdSetTooFrequent`（攜參） | 2222 | resetUserPassword ⑤設密冷卻未滿（政策之後）；changePassword 之冷卻步（政策之後）；data＝§2.2 | U10 | 密码设置过于频繁，请 {remainingSeconds} 秒后再试 | Password was set too recently, retry in {remainingSeconds}s | 密碼設定過於頻繁，請於 {remainingSeconds} 秒後再試 |
| 18 | `auth.session.kickedByAdmin` | 7777 | `AppError::ModalLogoutByAdmin` 之固定鍵：授權判定之失效名單命中 reason `admin_kick`（U10）；換發 revoked 腿之失效名單 reason `admin_kick`（U11）＝三向分派（spec FR-027） | U10 | 此会话已被管理员结束，请重新登录 | This session was ended by an administrator, please sign in again | 此工作階段已被管理員結束，請重新登入 |
| 19 | `biz.user.passwordConfirmMismatch` | 2222 | changePassword 首步（兩次輸入不一致） | U12（個人中心兩端點） | 两次输入的密码不一致 | Passwords do not match | 兩次輸入的密碼不一致 |
| 20 | `biz.user.changePasswordThrottled` | 2222 | changePassword 兩次一致之後、舊密雜湊比對之前之節流 precheck（每使用者 5 次／900 秒、第 6 次起） | U12 | 尝试次数过多，请稍后再试 | Too many attempts, please try again later | 嘗試次數過多，請稍後再試 |
| 21 | `biz.user.oldPasswordMismatch` | 2222 | changePassword 舊密不符（計入節流桶） | U12 | 旧密码不正确 | Old password is incorrect | 舊密碼不正確 |
| 22 | `biz.user.passwordSameAsOld` | 2222 | changePassword 新＝舊 | U12 | 新密码不能与旧密码相同 | New password must differ from the old one | 新密碼不可與舊密碼相同 |

計數：U4 一鍵、U8 十一鍵、U9 一鍵、U10 五鍵、U12 四鍵＝22；`biz.user.*` 20＋`auth.session.*` 1＋`biz.menu.*` 1。讀端（getUserList／getDeletedUsers／getPasswordPolicy）、unlockLogin 帳號維（U13）與換發活性重驗（U11 之 `8888` 腿）零新鍵。

### 1.2 語意要求（譯文須傳達；zh-cn／en-us 照 rev5 字面而不失實之判讀）

- 一因一鍵、純 key、不指筆：batchDeleteUser 任一違規整批 rollback、拒因＝該筆之鍵、不帶 id；撞名與撞信箱各回其既有鍵（restoreUser 不另立鍵）。
- `notFound`：活性判準＝未軟刪；只有 restoreUser 認得已刪列（spec FR-016）。rev6 新增之 body 收斂（FR-009）與 rev5 「缺席→id 0→查無」同形、無語意延伸。
- `seededProtected` 一鍵承載兩情形（seed 三帳號不可刪；id 1 不可解除 R_SUPER 指派）；`superCannotDisable` 專指 id 1 停用；`cannotEditSelfRoleOrStatus` 亦承載「不得停用自己」（`status` 出現即拒、故無獨立停用鍵）。三者判定序 ②先於③：Super 對自身帳號送出停用或解除 R_SUPER，回 ②之鍵。
- `userEmailInvalid`：本刀空字串＝清空（ADR-00080）使空字串不再觸發本鍵，屬射程收窄、非延伸；字面照 rev5。
- `roleNotFound`：rev6 之角色列鎖內重驗只關閉並發窗、拒因不變。
- `changePasswordThrottled` 純 key、不下發剩餘次數或秒數（與 `pwdSetTooFrequent` 攜秒數為兩事：前者防猜舊密、後者為設密冷卻）。
- `kickedByAdmin`、`kicked`、`reLogin` 三者不互換：管理員踢除＝`7777`＋`auth.session.kickedByAdmin`；單一會話頂替＝`7777`＋`auth.session.kicked`（文案不變）；撤銷（停用、刪除、重設、自助改密）＝`8888`＋`auth.session.reLogin` 靜默（憲法島 C、spec FR-027、FR-030）。
- `protectedButtonRemove`：移除集含「改碼」（舊碼即被移除）；只看該碼是否尚有受保護授權列、不問列屬哪個角色；受保護選單守門（停用、改父）之既有鍵 `biz.menu.protectedMenu` 不變。

### 1.3 繁中用詞（本表 zh-tw 欄之用詞決定；臺灣用語）

| 概念 | 繁中用詞 | 避用（大陸用語） |
|---|---|---|
| session | 工作階段 | 會話 |
| policy（密碼、工作階段） | 政策 | 策略 |
| user／username | 使用者／使用者名稱 | 用戶／用戶名 |
| email | 信箱 | 郵箱 |
| built-in | 內建 | 內置 |
| 管理員結束他人全部工作階段 | 踢除 | ——（單一工作階段被別處登入取代＝「頂替」；spec FR-030） |
| invalid（形制） | 格式不合法（沿 rev6 既有繁中譯文慣例） | —— |
| byte／character | 位元組／字元 | 字節／字符 |
| （按鈕）code | 代碼 | 編碼 |

本表為本刀新鍵與 §3 子鍵之用詞；page 樹其餘新鍵（使用者頁、個人中心）之繁中譯文同此用詞（ADR-00084；research R19）。zh-tw 欄字面受 `tools/zh-tw-lint.py`（簡體殘字、用語表、「頂替」「踢除」語意用詞）與 spec SC-009 之審讀與 user 抽查約束。

### 1.4 既有鍵復用（零新增）

| 鍵（碼） | 本刀發出點 |
|---|---|
| `system.forbidden`（`5003`） | 包含規則違反（9 個消費點、純 key、不洩漏差集；spec FR-021）；Admin 等非授權角色呼叫只授 R_SUPER 之管理面端點 |
| `system.internal`（`5000`） | 寫端請求上下文缺席（操作者取得先於一切守門；spec FR-006）；任何 `DbErr` |
| `common.success`（`0000`） | 讀端、寫端 Applied 與 no-op（值 diff 相同、空陣列批刪） |
| `auth.session.reLogin`（`8888`） | 被撤者下一次請求；換發活性重驗不活（spec FR-028） |
| `auth.login.failed`（`1000`） | 停用或刪除者再登入（三態 collapse 不變） |
| `auth.session.kicked`（`7777`） | 單一會話頂替（文案與分派不變） |
| `biz.role.protectedRevoke`（`2222`） | 按鈕權限彈窗撤 R_SUPER 名下 m0003 後受保護之六碼（spec FR-042；判定面不變、觸發面擴） |
| `biz.role.protectedGrant`（`2222`） | updateRoleEndpoints 對非 R_SUPER 授予 updateUserSessionPolicy（seed 政策列 68 受保護＝封死集；spec FR-002） |
| `biz.throttle.invalidUnlockTarget`（`2222`） | unlockLogin 既有拒因（帳號維掛包含規則後不變） |

密碼政策矛盾（最小長度＞最大長度）不另立鍵：任何密碼至少違反 `minLength`／`maxLength` 其一，自然回 `biz.user.passwordPolicy`（spec FR-034；告警出口另見 ADR-00079）。

## §2 攜參兩鍵之 data 形與前端轉譯

射程恰此兩鍵（ADR-00076；spec FR-004、FR-051）：明細是操作者當下據以修正輸入的資訊（該改哪條、還要等多久），不是診斷面。其餘一切錯誤之 data 恆 `null`；信封形（三欄、欄序 data→code→msg、`code` 為 JSON string）見 `contracts/wire-user-center.md` §3。

### 2.1 `biz.user.passwordPolicy`

- `data＝{"violations": [<違規碼>, …]}`；違規碼恰八枚短名字面＝`minLength`／`maxLength`／`maxBytes`／`requireDigit`／`requireLowercase`／`requireUppercase`／`requireSpecial`／`forbidUsername`（`model::password` 之 `VIOLATION_*` 常數）。
- 陣列非空、元素不重複、序＝政策單一驗證點之判定固定序（上列序）；一次收集全部違規（spec FR-032）。
- data MUST NOT 含密碼明文、雜湊、政策門檻值或帳號名（島 I5 三重不洩）；門檻值由前端經 getPasswordPolicy 七鍵投影另行提示。`maxBytes` 之上界 512 為碼內常數、不在七鍵投影內——前端不預判此項（即時規則 hook 七枚），只在後端回 `maxBytes` 違規碼時由明細轉譯呈現。
- 發出入口：addUser、resetUserPassword、changePassword 三入口共用單一驗證點與單一組裝點（§4.5）。

### 2.2 `biz.user.pwdSetTooFrequent`

- `data＝{"remainingSeconds": n}`；`n` 為整數＝冷卻秒數減已經過秒數之下取整、下限 1（不發 0）、上限＝冷卻設定鍵 `password_change_min_interval` 之值域上界 86400。
- 維度＝（標的 id, 操作者 id）；冷卻設定 0＝停用＝本鍵不發。
- 發出入口：resetUserPassword、changePassword。addUser 結構上不發（新 id 無經手列；addUser 只寫入時戳、計入其後之冷卻；spec FR-035）。

### 2.3 共同約束（佔位符對賬）

- 三檔 locale 中，兩鍵譯文之佔位符集 MUST 逐字等於後端明細型序列化後之頂層鍵集（§4.5）：`passwordPolicy`＝恰 `{violations}`、`pwdSetTooFrequent`＝恰 `{remainingSeconds}`（camelCase）。名稱不一致時明細段落失真（vue-i18n 具名插值找不到參數不報錯），而鍵集閘與型別檢查皆不看字串內容＝零紅點（`rev5:B-139` 之實暴形）；機器守見 §5。
- 其餘鍵（含本刀 20 支純 key 新鍵）之譯文 MUST NOT 含 `{…}` 佔位符（現況三檔 backend 子樹含佔位符之譯文 0 處）。
- 譯文中 `{`／`}`／`@`／`|` 等 vue-i18n 訊息語法字元只許出現於上列既定佔位符。

### 2.4 前端轉譯（`src/service/request/index.ts`；`BASE-WEB-I18N-WIRING` (i) 經 Amendment 改寫）

- 共用 helper 擴為 `translateBackendMsg(msg, data?)`：msg 為上列兩鍵之一且 data 為物件時走具名插值，其餘一律維持現行 ``$t(`backend.${msg}`, msg)``（原文 fallback、不吞錯、不顯裸鍵）——**只限兩鍵**（spec FR-051）；他鍵即使 data 非 null 亦不插值。
- `passwordPolicy`：`data.violations` 逐碼經 `page.passwordPolicy.violation.<碼>` 譯成人話（查無子鍵＝原樣顯示該碼、不吞錯）、以 `page.passwordPolicy.listSeparator` 串成單一字串，再以 `{ violations: <串> }` 插入 `backend.biz.user.passwordPolicy`。
- `pwdSetTooFrequent`：`{ remainingSeconds: data.remainingSeconds }` 原值插入 `backend.biz.user.pwdSetTooFrequent`。
- data 形不符（非物件、`violations` 非陣列、`remainingSeconds` 非數值）＝不拋錯、照純 key 路徑呈現（後端恆附 data，此為防禦形）。
- 兩鍵之判別以 msg 字面比對、各恰一處程式碼字面（＝msg-key-gate 斷言 3 之消費點、名冊見 §5）；明細轉譯只接 toast 鏈（`2222` 走 `BACKEND_ERROR_CODE` 分支之既有修改型行改傳 data、其 `原行:` 不變）；`7777` 對話框鏈之 data 恆 null、呼叫形不變——`auth.session.kickedByAdmin` 經既有 modal 通道與既有轉譯即呈現，前端零新分支。
- 頁面（使用者頁、重設密碼浮層、個人中心改密卡）零 msg 字面比對：拒因一律經共用攔截層 toast 呈現；實作期若新增比對＝同批登記名冊（§5）。頁面以 `$t('backend.biz.user.<鍵>')` 全路徑引用既有譯文（例：改密卡「新≠舊」即時規則借 `passwordSameAsOld` 譯文）屬型別守之 i18n 鍵引用、非 wire 形消費點。
- CDP（spec SC-010「提示文案」、22080 側顯式簡中）：zh-cn 譯文逐字沿 rev5、分隔符 `、`，故 toast 與 rev5 逐字全等（例：`密码不符合安全策略：长度未达策略下限`）。

## §3 `page.passwordPolicy.*`（違規子鍵之單一共用命名空間）

### 3.1 子鍵與譯文（八枚違規碼＋分隔符；三語；零佔位符）

| 子鍵 | zh-cn | en-us | zh-tw |
|---|---|---|---|
| `violation.minLength` | 长度未达策略下限 | length below the policy minimum | 長度未達政策下限 |
| `violation.maxLength` | 长度超过策略上限 | length exceeds the policy maximum | 長度超過政策上限 |
| `violation.maxBytes` | 字节数超过上限 | byte length exceeds the limit | 位元組數超過上限 |
| `violation.requireDigit` | 须包含数字 | must contain a digit | 須包含數字 |
| `violation.requireLowercase` | 须包含小写字母 | must contain a lowercase letter | 須包含小寫字母 |
| `violation.requireUppercase` | 须包含大写字母 | must contain an uppercase letter | 須包含大寫字母 |
| `violation.requireSpecial` | 须包含特殊符号 | must contain a special character | 須包含特殊字元 |
| `violation.forbidUsername` | 不可与用户名相同 | must not be identical to the user name | 不可與使用者名稱相同 |
| `listSeparator` | `、` | `, ` | `、` |

- zh-cn／en-us 逐字取 rev5 HEAD 之 `backend.biz.user.passwordViolation.*` 與 `backend.common.listSeparator` 實文（CDP toast 逐字全等之前提）；zh-tw 依 §1.3。
- ★八枚子鍵**零佔位符**：消費者之一（請求層明細轉譯）手上只有違規碼、沒有門檻值（§2.1），同一譯文又須供即時規則共用（spec FR-033 單一命名空間），帶 `{min}` 類參數即在明細中渲染為空。
- 子鍵尾段＝違規碼字面（逐字、大小寫敏感）；後端 `VIOLATION_*` 改名＝本表三語同批改名（後端常數之逐字釘值測 doc 指向本節）。

### 3.2 為何落 page 樹、不落 backend 樹

- msg-key-gate 斷言 1：三檔 `backend` 子樹各自與 `MSG_KEYS` 雙向全等、無白名單（ADR-00039 決定 1、憲法 §III.2 I18N (ii)）——違規子鍵放進 backend 樹即判「多鍵」紅。
- contract 方向二（`msg_roster_every_key_has_an_emitter`：名冊每鍵 ≥1 真實發出點）：違規碼只以 data 元素下發、永不當 msg 發出——進 `MSG_KEYS` 即判「名冊鍵無發出點」紅。兩閘合起來：凡非 msg 之鍵不得出現在 backend 樹。
- rev5 以 backend 樹白名單九鍵（`backend.biz.user.passwordViolation.*`＋`backend.common.listSeparator`）承載＝不帶回（research R5）。
- 單一共用命名空間（spec FR-033）：請求層為全域、不知所在頁，故不落 `page.manage.user` 或 `page.userCenter` 之下；亦不落 upstream 既有之 `common` 子樹（避免新增行與 upstream 行交錯）。
- 斷言 3 不受影響：首段 `page` 不屬安全前綴（現況 `['auth', 'biz']`），`$t('page.passwordPolicy…')` 字面不是 wire 形消費點。

### 3.3 消費者、型節與圈界

- 消費者：①請求層明細轉譯（八枚＋分隔符）②即時規則 hook `src/hooks/business/pwd-policy.ts`（七枚；`maxBytes` 不預判）——個人中心改密卡、重設密碼浮層、產密元件經 hook 共用。使用者頁清單角色欄之分隔符不借用本命名空間、另立 `page.manage.user.roleSeparator`（三語；隨 U17 之 `page.manage.user` 塊落地＝research R18）。
- 型節：`src/typings/app.d.ts` 之 `App.I18n.Schema.page` 增 `passwordPolicy: { violation: { <八枚>: string }; listSeparator: string }`；zh-cn／en-us 已標 Schema、zh-tw.ts 自 U15 起標 Schema ⇒ 三語缺鍵或多鍵由前端型別檢查攔。
- 圈界：en-us／zh-cn／app.d.ts 各新增 1 塊新增型，標記 `[rev6-inline BASE-WEB-I18N-WIRING(i)+ 007-user-password-admin START]`／`END`（plan 期主線定案：本子樹之授權歸 (i) 明細轉譯用途）；零 `原行:`。位置：三檔同位、建議接在 `page.about` 之後、`page.home` 之前——MUST 前後皆為 upstream 行、不與其他圈界塊相鄰（相鄰即落同一變更塊、拔掉本塊標記仍被鄰塊蓋住而 lint 照綠）。zh-tw.ts（rev6 自有檔、不入名冊）同位、無圈界。

## §4 後端名冊與構造形（`rust-api/server/src/error.rs`）

### 4.1 `pub mod msg_key` 新常數（22）

命名沿現行 `<首段>_<次段>_<鍵>` 全大寫蛇形（例既有 `BIZ_MENU_MENU_TYPE_IMMUTABLE`、`AUTH_SESSION_KICKED`）；字面只住本模組。

| 常數 | 字面 | 常數 | 字面 |
|---|---|---|---|
| `BIZ_MENU_PROTECTED_BUTTON_REMOVE` | `biz.menu.protectedButtonRemove` | `BIZ_USER_CANNOT_DELETE_SELF` | `biz.user.cannotDeleteSelf` |
| `BIZ_USER_NOT_FOUND` | `biz.user.notFound` | `BIZ_USER_CANNOT_KICK_SELF` | `biz.user.cannotKickSelf` |
| `BIZ_USER_USER_NAME_INVALID` | `biz.user.userNameInvalid` | `BIZ_USER_CANNOT_RESET_SELF_PASSWORD` | `biz.user.cannotResetSelfPassword` |
| `BIZ_USER_USER_NAME_EXISTS` | `biz.user.userNameExists` | `BIZ_USER_SESSION_POLICY_INVALID` | `biz.user.sessionPolicyInvalid` |
| `BIZ_USER_USER_NAME_IMMUTABLE` | `biz.user.userNameImmutable` | `BIZ_USER_PWD_SET_TOO_FREQUENT` | `biz.user.pwdSetTooFrequent` |
| `BIZ_USER_USER_EMAIL_INVALID` | `biz.user.userEmailInvalid` | `AUTH_SESSION_KICKED_BY_ADMIN` | `auth.session.kickedByAdmin` |
| `BIZ_USER_USER_EMAIL_EXISTS` | `biz.user.userEmailExists` | `BIZ_USER_PASSWORD_CONFIRM_MISMATCH` | `biz.user.passwordConfirmMismatch` |
| `BIZ_USER_ROLE_NOT_FOUND` | `biz.user.roleNotFound` | `BIZ_USER_CHANGE_PASSWORD_THROTTLED` | `biz.user.changePasswordThrottled` |
| `BIZ_USER_SEEDED_PROTECTED` | `biz.user.seededProtected` | `BIZ_USER_OLD_PASSWORD_MISMATCH` | `biz.user.oldPasswordMismatch` |
| `BIZ_USER_SUPER_CANNOT_DISABLE` | `biz.user.superCannotDisable` | `BIZ_USER_PASSWORD_SAME_AS_OLD` | `biz.user.passwordSameAsOld` |
| `BIZ_USER_CANNOT_EDIT_SELF_ROLE_OR_STATUS` | `biz.user.cannotEditSelfRoleOrStatus` | `BIZ_USER_PASSWORD_POLICY` | `biz.user.passwordPolicy` |

模組內位置依域歸組（核現行：006 刀之 `BIZ_ROLE_PROTECTED_REVOKE`／`BIZ_ROLE_PROTECTED_GRANT` 插在 role 組末、`BIZ_POLICY_NOT_RESTORABLE` 自成新組接在模組末）：`AUTH_SESSION_KICKED_BY_ADMIN` 緊接 `AUTH_SESSION_KICKED`；`BIZ_MENU_PROTECTED_BUTTON_REMOVE` 接在 menu 組末（`BIZ_MENU_RESTORE_CONFLICT` 之後）；`BIZ_USER_*` 二十支自成新組、接在 `BIZ_POLICY_NOT_RESTORABLE` 之後、組內依 §1.1 表序。

### 4.2 `MSG_KEYS` 排列規則

- `pub const MSG_KEYS: [&str; 46]` → `[&str; 68]`：**尾端追加、既有序不動**（核現行：模組依域歸組，而 `MSG_KEYS` 依落地序——006 刀三鍵排在 menu 十四鍵之後即此形）；追加序＝落地單元序、同單元依 §1.1 表序；元素一律 `msg_key::NAME` 常數引用。
- 依 research R23 之單元序落地時，第 47～68 位＝§1.1 之 #1～#22；tasks 改變單元先後時依實際落地序追加，不回頭重排。

### 4.3 同單元同批改之測試與 doc

- `msg_keys_roster_is_pinned_and_unique`：逐鍵釘值陣列尾補該單元字面；doc 批次句以刀名形補記（沿既有「006 刀 U7 與 U8 之 role 各一鍵」形，例「007 刀 U8 之 user 十一鍵」）。
- `biz_keys_are_in_roster`：常數迴圈補該單元之 `BIZ_*`（共 21 支：user 二十＋menu 一）、doc 列舉同補；兩攜參鍵另斷言 `AppError::BizData(Cow::Borrowed(k), …)` 之 `key()` 原樣透出。
- `fixed_variant_keys_are_in_roster`：固定 key 變體補 `AppError::ModalLogoutByAdmin`（「八個固定 key 變體」→九個，U10）。
- `AppError::key()`：增 `BizData(key, _) => key.as_ref()`、`ModalLogoutByAdmin => msg_key::AUTH_SESSION_KICKED_BY_ADMIN` 兩臂。
- `pub mod msg_key` doc：固定鍵「八支」→九支（U10）；構造點句「menu 十四鍵之構造點住 `handler::menu`（005 刀 U8 十二鍵、U9 二鍵）」→十五鍵並補「007 刀 U4 一鍵」歸因（U4）；增 user 二十鍵住 `handler::user` 與 `handler::user_center`（`changePasswordThrottled` 之構造點住 `handler::user_center`：節流預檢 `throttle::change_pwd::precheck` 回 `Result<(), Throttled>`、不構造 `AppError`，拒因由 handler 於步序③構造＝research R11 決定 3、ADR-00090 決定 2）；攜參兩鍵之組裝點見 §4.5。
- `MSG_KEYS` doc 之批次句同補（刀名形）。

### 4.4 構造形（純 key）

- 一律 `AppError::Biz(Cow::Borrowed(msg_key::NAME))` 常數形。rev5 於構造點直書字面（rev5 rust-api `server/src/handler/user.rs`、`server/src/handler/user_center.rs`）＝翻案不帶回（research R5）。
- 測試側之構造亦取常數形：落鍵單元出口以 `git -C rust-api grep -n 'Cow::Borrowed("' -- server/src` 斷言命中仍只有 `error.rs` 測試模組之矩陣列（現況恰該 1 處），新構造點不增命中。
- `auth.session.kickedByAdmin` 非 Biz 構造點：由 `AppError::ModalLogoutByAdmin` 之固定臂給鍵，構造於授權判定（`auth::enforce`）與換發（`handler::auth::refresh`）之三向分派點。

### 4.5 `AppError::BizData` 構造點限制

- 射程恰二鍵：`msg_key::BIZ_USER_PASSWORD_POLICY`、`msg_key::BIZ_USER_PWD_SET_TOO_FREQUENT`（ADR-00076）；擴第三鍵＝新 ADR。
- 每鍵恰一組裝點（單一構造點）：`handler/user.rs` 之 `pub(super) fn password_policy_err(violations: Vec<&'static str>) -> AppError` 與 `pub(super) fn pwd_set_too_frequent_err(remaining_seconds: u64) -> AppError`（同層 `user_center.rs` 共用；三入口一律經之、不得各自組 data）。組裝函式隨其鍵之首發單元落地（§1.1：U8、U10）；U6 落變體、信封出口與閘擴充，**生產區不構造 BizData**（無真實發出點之鍵不得入名冊＝contract 方向二）。
- 形：`AppError::BizData(Cow::Borrowed(msg_key::NAME), <data>)`——鍵引數常數形；data 一律以具型明細 `PasswordPolicyDetail { violations }`／`PwdSetTooFrequentDetail { remaining_seconds }`（與組裝件同住 `handler/user.rs`、`#[serde(rename_all = "camelCase")]`、兩型入 wire 受審名冊＝`contracts/wire-user-center.md` §3）構造後 `serde_json::to_value`（不以 `json!` 字面或執行期 map 組：明細鍵名在型別層只有一份＝ADR-00076 決定 1）；`violations` 元素只取 `VIOLATION_*` 常數、組裝點不翻譯、不排序、不去重（序與唯一由驗證點保證）。
- data MUST NOT 含密碼明文、雜湊、門檻值（§2.1）。
- `AppError::BizData(..)`／`AppError::BizData(_, _)`／`AppError::BizData(key, _)` 之 match 與 if-let 樣式非構造點；以函式值形（不帶括號）把執行期值包成 `BizData`＝動態構造。

## §5 跨端閘與名冊雙向閘

- **msg-key-gate 斷言 1**（三檔 `backend: {` 子樹逐檔與 `MSG_KEYS` 雙向全等、無白名單）：`biz` 下新開 `user` 子樹（接在 `policy` 之後＝依刀序）收 20 鍵；`auth.session` 補 `kickedByAdmin`（接在 `kicked` 之後）；`biz.menu` 尾補 `protectedButtonRemove`。en-us／zh-cn 落在既有 `BASE-WEB-I18N-WIRING(ii)+ 003-auth-session` 圈界塊內、zh-tw 落在其 `backend` 子樹內：不增塊、零 `原行:`；`backend: {` 獨佔一行之右源錨行不動（U15 改 zh-tw.ts 為標型全樹時亦 MUST 保留該錨行獨佔一行）。
- **`src/typings/app.d.ts` backend 型節**（既有 `BASE-WEB-I18N-WIRING(iii)+ 003-auth-session` 圈界塊內）：`auth.session` 補 `kickedByAdmin: string`、`biz.menu` 補 `protectedButtonRemove: string`、`biz` 下新開 `user: { <20 鍵>: string }`。en-us／zh-cn 標 `App.I18n.Schema` ⇒ 缺鍵或多鍵由前端型別檢查攔；zh-tw 自 U15 起同受型別守、在那之前只由跨端閘守。
- **斷言 2**（構造點守衛）擴認 `AppError::BizData(`（`Self::`／經 use 匯入之裸形同）：首引數 MUST 為 `Cow::Borrowed(字面|msg_key::NAME)` 且解出之鍵 ∈ `MSG_KEYS`；BizData 構造點計入既有構造點總數（不另設空比對面之 rc 2——U6 至 U8 之間生產區 BizData 構造點為 0 屬預期）。另增射程守分階段四句與佔位符對賬（閘內常數 `BIZ_DATA_KEYS`＝射程二鍵→其明細型名之對照、出處 ADR-00076；第 2、3 句隨兩鍵分批入名冊而逐鍵生效）：
  1. 射程：BizData 構造點解出之鍵 ⊆ `BIZ_DATA_KEYS`，他鍵＝rc 1；
  2. 唯一：`BIZ_DATA_KEYS` ∩ `MSG_KEYS` 之每鍵於生產區恰一處 `BizData` 構造點（零處或多處＝rc 1）；
  3. 未落地：`BIZ_DATA_KEYS` 中未入 `MSG_KEYS` 之鍵，生產區構造點數 MUST 為 0（≥1＝rc 1）；
  4. 不降級：射程鍵以 `AppError::Biz(` 純 key 形構造＝rc 1（明細靜默消失）；
  5. 佔位符對賬：已入 `MSG_KEYS` 之射程鍵，其明細型之序列化鍵集（解析 `handler/user.rs` 內該名 struct 定義之欄名、依其 `rename_all` 屬性換算序列化名；查無該 struct＝rc 2）＝三檔 locale 該鍵譯文之 `{…}` 佔位符集（逐檔），且非攜參鍵之譯文佔位符集為空——不等＝rc 1 指名檔與鍵（§2.3；`rev5:B-139` 之機器守，rev5 於後刀以跨端 lint 第三腿補上）。
  自測補正反案（RL-0080）：常數形 BizData 綠、動態鍵紅、射程外鍵紅、同鍵兩處紅、已入名冊之射程鍵零構造點紅、未入名冊之射程鍵有構造點紅、射程鍵走 `Biz(` 紅、明細型缺 `rename_all = "camelCase"`（欄 `remaining_seconds` 對 `{remainingSeconds}`）紅、明細型欄名改名紅、純 key 鍵譯文含佔位符紅、match 樣式不計。`docs/ops/reference-src/code-gate-contracts.md` §5 斷言 2 列、RUNBOOK §12 碼面閘表列與工具檔頭同批改（U6）。
- **斷言 3**（前端 msg 字面消費點名冊）：`FRONTEND_MSG_CONSUMERS` 增兩項——`("service/request/index.ts", "biz.user.passwordPolicy"): 1`、`("service/request/index.ts", "biz.user.pwdSetTooFrequent"): 1`（1 項→3 項，隨請求層明細轉譯所在單元 U20 同批）；安全前綴集不變（仍 `auth`、`biz`：本刀不增 `MSG_KEYS` 頂層前綴）；`page.passwordPolicy.*` 與 `backend.*` 全路徑字面不屬消費點（§3.2）。
- **contract 方向一**（實發 ⊆ 名冊；`observed_msgs_are_subset_of_roster_and_non_empty` 與名冊測之 outside 斷言）：任何新鍵於首次被測試觀察前 MUST 已入 `MSG_KEYS`。免 DB 面（`observed_msgs`）之 12 條新路由只發既有鍵（未認證 `8888`、stub 假連線 `5000`），零改動。
- **contract 方向二**（`msg_roster_every_key_has_an_emitter`；免 DB 面 ∪ 真 seed app 面去重後＝`MSG_KEYS`）：22 鍵皆須於真 seed app 面實際發出；逐發斷言 `(code, msg)`，攜參兩鍵另斷言 data 形（§2）。觀察段併入 `observed_msgs_real_db`、doc 之逐刀批次句同補：
  - `biz.menu.protectedButtonRemove`（U4；併入既有 `menu_msgs_real_db`、沿用其 `RoleMenuDomainWriteGuard`）：植自建選單（按鈕清單含帶段標記之碼）＋以直植形植一列該碼之受保護按鈕維授權列（v0＝帶段標記之角色代碼、`created_by` 非 NULL、v3～v5 填 `''`＝LL-00043）→以移除該碼之按鈕清單打 updateMenu ⇒ 拒；★不打 seed 受保護列；段末復核選單列與授權列不變、歸檔表與稽核表於守衛水位窗內零新列。
  - user 十六鍵（新段 `user_msgs_real_db`；U8 建、U9／U10 續補）：Super 票、經 `app_with_peer` 帶對端（寫端先取操作者上下文）；先 arm 使用者列、seed 帳號快照、指派列、經手表四類守衛（`UserWriteGuard`／`SeedUserWriteGuard`／`UserRoleWriteGuard`／`PwdCustodyWriteGuard`；`contracts/code-gates.md` §5）；植自建帳號（帶界號段、名與信箱帶段標記）。各鍵之觸發：`notFound`＝updateUser 號段內不存在 id；`userNameInvalid`＝addUser 形制外帳號名；`userNameExists`＝addUser 帳號名 `Super`；`userNameImmutable`＝updateUser 自建帳號帶 `userName`；`userEmailInvalid`＝addUser 非信箱字面；`userEmailExists`＝addUser 信箱＝自建帳號信箱之大小寫異形；`roleNotFound`＝addUser 號段內不存在角色 id；`seededProtected`＝updateUser `{id:1, roleIds:[]}`；`superCannotDisable`＝updateUser id 1 帶停用值之 `status`；`cannotEditSelfRoleOrStatus`＝updateUser id 1 帶啟用值之 `status`（②放行、③拒）；`passwordPolicy`＝addUser 合形制帳號名＋3 字元密碼（seed 政策下 data 恰 `{"violations":["minLength"]}`）；`cannotDeleteSelf`＝以資料列指派 R_SUPER 予自建帳號（授權每請求現查指派列、零重載）、以其票 deleteUser 自身 id（seed 帳號之本人刪除先撞 ②）；`cannotKickSelf`＝kickUser `{id:1}`；`cannotResetSelfPassword`＝resetUserPassword `{id:1}`；`sessionPolicyInvalid`＝updateUserSessionPolicy 自建帳號、值域外字面；`pwdSetTooFrequent`＝以 `PwdCustodyWriteGuard` 登記並植（自建帳號, Super）經手列（時戳＝當下）後對該帳號 resetUserPassword 一次（首發即拒、零業務寫入），得 data `1 ≤ remainingSeconds ≤ 60`（seed 冷卻 60 秒）。段末復核：零寫入（經手列由守衛清）。
  - `auth.session.kickedByAdmin`（U10；併入 `observed_msgs_real_db` 既有被踢腿旁）：失效名單先種 reason `admin_kick`、同 sid 真票再打 Authed 端點 ⇒ `7777`＋本鍵；該鍵自 sid 產生處即交 `CacheKeysGuard`、案末顯式 drop 後就地斷言零殘（同既有 `kicked` 腿）。
  - user 四鍵（新段 `user_center_msgs_real_db`；U12）：植自建帳號（密碼雜湊執行期算＝RL-0054）＋其票；arm 含 `cpwd:` 前綴之 redis 鍵守衛。`passwordConfirmMismatch`＝兩次輸入不一致；`oldPasswordMismatch`＝舊密錯；`changePasswordThrottled`＝先將該帳號節流桶置於門檻再發；`passwordSameAsOld`＝新＝舊。段末復核密碼雜湊未變、零 `change_password` 稽核列。
- `server/tests/contract.rs` 之 `observed_msgs` doc「補三十七鍵」數量詞：現況已失準（006 刀三鍵未計，真值 40），本刀首個落鍵單元 U4 同批改為指向 `MSG_KEYS`、不再手抄鍵數（ADR-00039 決定 3）。

## §6 落地時序

- **同單元同批面**（spec FR-004「新鍵 MUST 隨首個發出它的單元落地」）：①`msg_key` 常數＋`MSG_KEYS` 尾端追加＋§4.3 之測試與 doc ②三檔 locale `backend` 子樹（譯文依 §1.1 擬稿）③`app.d.ts` backend 型節 ④contract 真 seed 發出案（§5）⑤攜參鍵另含 §5 佔位符對賬綠。兩子庫各自 commit 後，**兩 pin 同一顆外層 commit**——pre-commit msg-key-gate 段於任一側 pin bump 即比對兩側工作樹、submodule-sync 段要求兩側閘面無未 commit 改動。
- **單元對應**：U4＝`biz.menu.protectedButtonRemove`；U6＝明細通道件（`BizData` 變體、錯誤信封 data 出口、斷言 2 擴充與自測；零新鍵、生產區零 `BizData` 構造點）；U8＝十一鍵；U9＝一鍵；U10＝五鍵（含 `ModalLogoutByAdmin` 變體與授權判定三向分派）；U11＝換發三向分派（零新鍵、`kickedByAdmin` 增第二發出點）；U12＝四鍵；U18＝`page.passwordPolicy.*`（三語＋型節）＋即時規則 hook `src/hooks/business/pwd-policy.ts`（首個消費者＝重設密碼浮層）；U20＝請求層明細轉譯＋`FRONTEND_MSG_CONSUMERS` 兩項（只消費 `page.passwordPolicy.*`）。
- ★**硬序**：①任何落鍵單元觸及 base-web 既有檔（`en-us`／`zh-cn`／`app.d.ts`）⇒ MUST 排在 U0 之 Amendment（ADR-00074）accepted 之後（spec FR-055⑤）。②`page.passwordPolicy.*` 隨首個消費者 U18 落地、MUST 排在 U15（zh-tw.ts 改為 Schema 標型全樹）之後，三語＋型節同批；U20（請求層明細轉譯）只消費、MUST 排在 U18 之後。③Amendment 改寫之 `BASE-WEB-I18N-WIRING` (i) 列範圍欄 MUST 涵蓋 `src/locales/langs/{en-us,zh-cn}.ts` 與 `src/typings/app.d.ts` 各 1 塊新增型（§3.3 圈界；範圍欄對賬腿逐檔跨列加總），並刪「錯誤信封 `data` 恆 null、無明細通道 ⇒ 不建 `translateDetailValue`」句（spec FR-051）。
- **出口斷言**（逐檔應有值；現值＝本刀起手量測）：backend 鍵落地不增塊——`en-us`／`zh-cn` 之 ` START]` 數＝現值 10＋已落地之本刀 page 樹新塊、`app.d.ts`＝現值 8＋已落地之本刀新塊、三檔 `原行:` 由 msg 面零增；`zh-tw.ts` 之 `rev6-inline` 標記仍恰檔頭 1 行；`src/service/request/index.ts` 之明細轉譯改寫不增塊、`原行:` 仍 2。不等即停手升級。另：`python3 tools/msg-key-gate.py check` 綠、容器內 contract 名冊雙向案綠、前端型別檢查綠。
- **現在式假述（msg 面；RL-0011，實集以 `python3 tools/docsync errata <詞>` 枚舉為準）**：`error.rs` 檔頭「變體集恰九」與「rev5 後刀之 BizData／ModalLogoutByAdmin 屬後刀域、不帶」（U6／U10）、`IntoResponse` doc「信封統一交給 `Res::from_err` 組（data:null…）」（U6）、`envelope.rs` 之模組 doc（002 契約 §3 指針與「錯誤時 data 為 null 且不省略」）、`Res` doc「錯誤時必為 null 且不省略」、`from_err` doc「錯誤信封只能由此產生」、測試 `error_envelope_data_null_not_omitted` doc「經 from_err 唯一錯誤入口」（U6；錯誤 data 規則之指針改指 ADR-00076＝spec FR-051 修補後讀法、002 原檔屬凍結存證不改＝ADR-00041 決定 3；成功信封測試 doc 與 `tests/contract.rs` 之 4040 fallback 腿 doc 只補 ADR-00076 指針＝六處見 ADR-00076 決定 5）、`error.rs` 測試 `each_issuable_code_builds_error_envelope` doc「每個可發碼…data 為 null（契約 §3 第 3 條）」（U6；補述矩陣樣本皆純 key 變體、BizData 之 data 形歸 envelope 表驅動案）、`error.rs` 測試 doc「八個固定 key 變體」（U10）、`src/service/request/index.ts` helper 註「錯誤信封 data 恆 null、沒有明細通道」（U20）、`app.d.ts` backend 型節圈界註「兩語缺樹即 typecheck 紅；LangType 擴充…不在授權內」與 `zh-tw.ts` 檔頭「治理錨點孤立檔」（U15）、`tools/msg-key-gate.py` 檔頭斷言 2 說明與 `docs/ops/reference-src/code-gate-contracts.md` §5（U6）、活書 08 之 msg 名冊段（U21）。
- **射程外**：`page.manage.user.*`、`page.userCenter.*`、`page.manage.ipRule.unlock.*` 等 page 樹新鍵非 msg key、不入 `MSG_KEYS` 與本檔——落點與塊數見 `contracts/code-gates.md` §1；`route:` 樹零新增。
