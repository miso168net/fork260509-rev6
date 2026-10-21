# Contract — 本刀 msg 鍵（後端兩鍵、第三攜參鍵、兩頁 page 節）

## §1 後端新鍵（`MSG_KEYS` 68→70、尾端追加）

| 鍵 | 常數 | 碼 | data | zh-tw | zh-cn | en-us |
|---|---|---|---|---|---|---|
| `biz.audit.invalidTable` | `BIZ_AUDIT_INVALID_TABLE` | 2222 | null | 清理目標不在允許清單內 | 清理目标不在允许清单内 | The purge target is not in the allowed list |
| `biz.audit.purgeBelowFloor` | `BIZ_AUDIT_PURGE_BELOW_FLOOR` | 2222 | `{minDays}` | 清理保留天數不可低於 {minDays} 天 | 清理保留天数不可低于 {minDays} 天 | Retention days cannot be below {minDays} days |

- 落地時序：兩鍵隨 purge 寫端單元（U7）一次落——`error.rs` 名冊、三檔 locale backend 子樹（I18N (ii)）、`app.d.ts` backend 型節（I18N (iii)）同批；contract 案各至少一案實發（名冊雙向閘）。
- 語意要求：invalidTable 不回聲原值；purgeBelowFloor 之譯文只放佔位符 `{minDays}`、不寫死 30；zh-cn／en-us 逐字取 rev5 HEAD（＝rev4）譯文（toast 屬 SC-011 提示文案對照面，另設即不等）；zh-tw 同義對譯。

## §2 攜參明細通道（恰三鍵）

| 鍵 | 明細型（家） | 頂層鍵 | 前端插值 |
|---|---|---|---|
| `biz.user.passwordPolicy` | `PasswordPolicyDetail`（`handler/user.rs`） | `violations` | 違規碼逐碼譯後以分隔符串接 |
| `biz.user.pwdSetTooFrequent` | `PwdSetTooFrequentDetail`（`handler/user.rs`） | `remainingSeconds` | 具名插值 |
| `biz.audit.purgeBelowFloor` | `PurgeBelowFloorDetail`（`handler/audit.rs`） | `minDays` | 具名插值 |

- 佔位符對賬（msg-key-gate）：三語譯文之佔位符集＝明細型經 `rename_all` 換算後之序列化鍵集；改名即紅。
- 前端：`base-web/src/service/request/index.ts` 之 `translateBackendMsg` 於既有圈界塊內增第三分支（`typeof fields.minDays === 'number'`）、`fields` 型聯集增 `Api.Audit.PurgeBelowFloorDetail`；其餘錯誤信封 `data` 恆 null。

## §3 `page.manage.systemSettings`（新節；三語）

| 子鍵 | 內容 |
|---|---|
| `group.{password,session,ip,account}` | 四組標題（密碼策略／工作階段／IP 源登入／帳號登入） |
| `item.<setting_key>.{label,help}` | 16 鍵各一對；`login_throttle_*` 與 `ip_*` 之 help 不承諾嚴格上限（例：「窗內失敗達此數即鎖定（並發首波不嚴格）」或不寫上界） |
| `conflict.{password,account,ip}` | 三對矛盾提示（寫後果：密碼對＝新增使用者、重設密碼、修改密碼三入口一律拒；節流兩對＝該維三鍵整組退回出廠預設值） |
| `readonlyTag` | 宣告集外列標示 |

頁標題由 `route.manage_system-settings` 經分頁標籤與麵包屑呈現、頁內不另設；成功提示沿用 `common.updateSuccess`（皆 rev5 HEAD 形；另設即與 rev5 結構或提示文案不等＝SC-011）。

zh-tw 草案（實作期得潤飾、語意不得改）：密碼對＝「密碼最小長度大於最大長度：新增使用者、重設密碼與修改密碼將一律被拒，請調整其中一項。」；帳號對＝「帳號登入的需驗證碼門檻大於鎖定門檻：此組三項將整組退回出廠預設值。」；IP 對＝「IP 源登入的需驗證碼門檻大於鎖定門檻：此組三項將整組退回出廠預設值。」

## §4 `page.manage.audit`（新節；三語）

| 子鍵 | 內容 |
|---|---|
| `title` | 頁卡標題（rev5 HEAD 同形） |
| `tab.{operation,access,login,session}` | 四分頁標題（zh-tw 依既有譯法 session＝工作階段，例「工作階段事件」；zh-tw 新增值不得含「會話」；spec 之「會話事件」為來源術語、非 zh-tw 畫面字面） |
| `search.*` | 四搜尋卡欄位 label 與 placeholder（動作欄範例用庫內小寫字面，如 `update`、`kick`） |
| `column.*` | 四分頁欄標題＋登入成敗兩值標籤 |
| `snapshot.{entry,title,before,after,empty}` | 快照浮層 |
| `purge.{entry,title,days,daysHint,warning,confirm,success}` | 清理浮層（`daysHint`＝天數提示行；`success` 帶 `{count}` 插值；`title` 帶 `{table}`） |
| `notice.access` | ★存取分頁告示：zh-tw「狀態欄為 HTTP 狀態碼：權限不足顯示 403，其餘請求（含業務拒絕與系統錯誤）皆顯示 200。」（不提 404：未註冊路徑與動詞不符不經記錄層） |
| `notice.login` | 登入嘗試分頁告示：被登入節流直接擋下之嘗試不記錄於此（不承諾嚴格上限） |

操作者為空之列（排程清理自記）顯「-」、零新鍵（rev5 之空值顯示形；spec FR-053）。

## §5 `route:` 樹（三語各兩鍵）

`manage_system-settings`、`manage_audit`——與 view 同單元或其後落地（`route: Record<I18nRouteKey, string>`＝route 譯文不能先於 view）。

## §6 跨端閘與名冊雙向閘

- backend 子樹三檔鍵集＝`MSG_KEYS`（70）；`zh-tw.ts` 以 `App.I18n.Schema` 標型＝三語鍵集型別守。
- msg-key-gate：`BIZ_DATA_KEYS` 三鍵、明細型之家逐鍵對映（code-gates §2.1）。
- zh-tw-lint：新字面過簡體殘字與用語表。
