# Contract — 稽核五端點（四源讀端＋水平線清理）

> 欄形與名稱之家＝data-model §6／§12；固定序＝data-model §3.1；過濾語意＝data-model §4。授權態逐列照 001 凍結 seed（皆 R_SUPER、非受保護）。

## 端點總表（ROUTES 表尾依序追加；61→66）

| # | 方法 路徑 | seed 政策列 | case_key | 回應 data |
|---|---|---|---|---|
| 1 | GET `/systemManage/getOperationLog` | 139 | `get-operation-log` | `PageRes<Api.Audit.OperationLog>` |
| 2 | GET `/systemManage/getAccessLog` | 140 | `get-access-log` | `PageRes<Api.Audit.AccessLog>` |
| 3 | GET `/systemManage/getLoginAttempt` | 141 | `get-login-attempt` | `PageRes<Api.Audit.LoginAttempt>` |
| 4 | GET `/systemManage/getSessionEvent` | 158 | `get-session-event` | `PageRes<Api.Audit.SessionEvent>` |
| 5 | POST `/systemManage/purgeAuditLog` | 159 | `purge-audit-log` | `Api.Audit.PurgeAuditLogRes` |

全部 `Protection::Policy`；政策保護端點 45→50；端點維候選集（`policy_endpoints()`）依註冊序增五支＝可授出集 30→35。

## 共用型（`Api.Audit`；`base-web/src/typings/api/rev6-audit.d.ts` 新檔、經 declaration merging；rust DTO 同名去 `Dto` 尾綴對映）

- 四列型欄序＝data-model §6；i64 欄經 `serialize_i64_number_guarded`／`serialize_opt_i64_number_guarded`。
- 四 query 型：`OperationLogSearchParams`、`AccessLogSearchParams`、`LoginAttemptSearchParams`、`SessionEventSearchParams`＝`CommonType.RecordNullable<…>`（rev5 形）；鍵＝data-model §4 之 wire 鍵＋`current`／`size`。
- `PurgeAuditTable`＝`'operationLog' | 'accessLog' | 'loginAttempt' | 'sessionEvent'`；`PurgeAuditLogReq`＝`{ table: PurgeAuditTable; beforeDays: number }`；`PurgeAuditLogRes`＝`{ deletedCount: number }`；`PurgeBelowFloorDetail`＝`{ minDays: number }`。
- 受審（`rust-api/server/tests/wire_schema.rs`）：四列型、`PurgeAuditLogRes`、`PurgeBelowFloorDetail` 正向各一＋反例（缺欄、多欄、i64 型錯）；`PurgeAuditTable` 枚舉集以後端 `RetentionTable::ALL` 之 wire 值為真源。

## 讀端共同語意（端點 1～4）

- 只讀交易（唯讀模式）內查清單與總數；零寫入（存取日誌中介層之列不屬讀端交易）。
- 錯誤集：授權兩碼（`5003`／HTTP 403、未帶權杖 `8888`）＋內部 `5000`；**零業務拒因**；query 壞形（含同名鍵重複）收斂成未給參數、回成功信封。
- 空頁：`records: []`、`total: 0`、`current`／`size` 回填收斂值。

## 1. getOperationLog

過濾：`entityTable`、`operation`（等值）、`operatorId`／`operatorName`、`timeFrom`／`timeTo`。`payloadBefore`／`payloadAfter` 經打碼（data-model §5）。`operatorName` 以操作者 id 去重集一次批查。

## 2. getAccessLog

過濾：`httpMethod`、`httpStatus`（等值）、`httpPath`（部分字串）、`operatorId`／`operatorName`、時間。★`httpStatus` 為 HTTP 狀態碼：rev6 實際只出現 200 與 403（未註冊路徑、動詞不符不經記錄層；業務拒因與系統錯誤皆 200）＝已知態；無來源 IP 過濾欄（rev5 形）。

## 3. getLoginAttempt

過濾：`userName`（部分字串）、`success`（嚴格二值）、`realIp`（精確等值）、時間。無操作者欄與批查。

## 4. getSessionEvent

過濾：`userId`／`userName`（主體維）、`eventType`、`reason`（等值）、時間。`userName` 與 `operatorName` 取主體與觸發者 id 之聯集一次批查。

## 5. purgeAuditLog

- 請求：JSON `{table, beforeDays}`；`beforeDays` 寬鬆（number 或數字字串、trim）；缺席、null、畸形＝0；body 壞形（任何 `JsonRejection`）收斂成全缺席＝固定序①拒。未知欄忽略（無挑列欄位落點）。
- 固定序與 outcome：data-model §3.1。
- 拒因：`2222 biz.audit.invalidTable`（純 key、`data: null`）；`2222 biz.audit.purgeBelowFloor`（`data: {minDays: 30}`）；兩者同時違反＝前者。
- 成功：`0000`＋`{deletedCount}`；同交易已落自記（data-model §7 手動清理列）。
- 故障：`5000`（整筆回滾）。

## 授權態矩陣（contract 測；逐端點）

| 身分 | 1～4 | 5 |
|---|---|---|
| Super（R_SUPER） | `0000` | `0000`（或業務拒因） |
| Admin（R_ADMIN）／User | `5003`／HTTP 403 | `5003`／HTTP 403 |
| 未帶權杖 | `8888` | `8888` |
| 動詞不符（如 POST 讀端） | `4040`／HTTP 404 | `4040`／HTTP 404 |

被授予端點之自建角色（非封死集、可授出）：照授權生效；清理仍受 30 天下限與自記兜底。

## 與 rev5 wire 逐欄比對

四列型、四 query 型、清理請求與回應、`PurgeAuditTable` 四值逐欄同 `rev5:src/typings/api/rev5-audit.d.ts`；差異＝命名空間檔名前綴（`rev6-`）、第三攜參鍵之明細型具名（`PurgeBelowFloorDetail`；rev5 為匿名物件、wire 形相同）。

## 拒寫事件與觀測

- purge 操作者缺席：`tracing::error!(target: "audit", refused = "operator_context_absent", endpoint = "purgeAuditLog", …)`；不推 `degraded` 欄（拒寫不屬降級）。
- 讀端查詢失敗：error 事件（端點標籤）＋`5000`。
