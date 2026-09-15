# Contract — IP 規則管理五端點

> 權威序依憲法 §I.3：base-web 實碼 ＞ 官方 docs ＞ mock。本刀為 rev6 **新建**面、無 upstream 既有呼叫端 ⇒ 契約以 `rev5:004` `contracts/wire-ip-rule.md` 已驗證形為藍本、由本檔凍結（spec 目錄＝定點快照；wire 活體權威＝碼＋`tests/contract.rs`、brainstorm G2）。
> 信封一律 `{data, code, msg}`、業務錯誤 HTTP 200（例外恰二：`4040`→404、`5003`→403）；五條 route 皆政策保護（seed 143～147、`R_SUPER`）。

## 共用型 `IpRuleRecord`（camelCase；rev6 型別檔＝`src/typings/api/rev6-ip-rule.d.ts` 之 `Api.IpRule`）

| 欄 | 型 | 說明 |
|---|---|---|
| `id` | number | DB i64→number（2^53 fail-loud 守衛） |
| `wbipCidr` | string | 正規化後網段字面 |
| `wbipType` | string | `allow`｜`deny` |
| `wbipMemo` | string \| null | 備註（渲染端純文字插值） |
| `order` | number \| null | 排序值、不參與判定 |
| `deleted` | boolean | 由 `deleted_at.is_some()` 導出 |
| `createdAt` | string | RFC3339 帶 offset |
| `updatedAt` | string \| null | |
| `createdBy`／`updatedBy` | string \| null | 操作者帳號名（單次批次回填、查無→null） |

`deletedAt`／`deletedBy` 不上 wire。

## 1. `GET /systemManage/getIpRuleList`

Query（全部可空）：`current`（預設 1、下界 1）／`size`（預設 10、clamp 1..100）／`wbipCidr`（模糊）／`wbipType`（等值）／`deleted`（`active`｜`deleted`｜`all`、缺省 `all`）。
200：`{ code: "0000", msg: "common.success", data: PageRes<IpRuleRecord> }`（`{current, size, total, records}`）；列序＝伺服器固定（id 降冪；無 client 排序參數＝BL-00044 射程外）。錯誤：`5003`（非超管）／`5000`。

## 2. `POST /systemManage/addIpRule`

Req：`{ wbipCidr: string, wbipType: string, wbipMemo?: string, order?: number }`。處理序（★次序即契約）：①類型二值守門→`2222 biz.ipRule.invalidRuleType`（寫前拒、零寫入）②網段解析＋主機位元正規化→失敗 `2222 biz.ipRule.invalidCidr`（零寫入）③防自鎖：「變更後規則集（加入）」對操作者當下真實來源跑同一 `decide`→Deny 即 `2222 biz.ipRule.selfLock`（零落庫、零重載）；操作者上下文缺席→`5000`（F3①）④落庫＋操作稽核列 `add` 同一交易→唯一衝突映 `2222 biz.ipRule.conflict`（MUST NOT 5000）⑤成功後 reload＋門鈴。200：`data: null`。

## 3. `POST /systemManage/updateIpRule`

Req：`{ id: number, wbipCidr, wbipType, wbipMemo?, order? }`。同 add；防自鎖之變更後集合＝**移除舊值＋加入新值**；標的不存在或已軟刪→`2222 biz.ipRule.notFound`。

## 4. `DELETE /systemManage/deleteIpRule`

Req：`{ id: number }`。軟刪（`deleted_at`／`deleted_by` 成對寫）；防自鎖之變更後集合＝**移除該列**（刪 allow 可能使操作者失去放行 ⇒ 同樣過自鎖）；不存在或已在回收桶→`notFound`。成功後 reload＋門鈴。

## 5. `POST /systemManage/restoreIpRule`

Req：`{ id: number }`。復原（成對清空）；變更後集合＝**加入該列**；不存在或非回收桶→`notFound`；復原後與現有有效列衝突→`conflict`。成功後 reload＋門鈴。

## 阻擋回應（閘門面、與本檔五端點無關但同 wire 面）

命中阻擋（任一政策保護或匿名端點；健康／觀測除外）→`{ code: "5003", msg: "system.forbidden", data: null }`／HTTP 403；★只作用請求層：不撤會話、不寫 denylist、規則解除即恢復（clarify Q1）。前端 `service/request/index.ts` 對帶信封 msg 之 HTTP 錯誤走 `translateBackendMsg`（Q6）。

## 契約測試 case（覆蓋閘每條 route ≥1）

| case_key | 斷言重點 |
|---|---|
| `get-ip-rule-list` | 分頁形＋三 filter＋審計欄與操作者名＋`deleted` 導出＋id number |
| `add-ip-rule` | 正規化落庫＋衝突映業務碼＋自鎖拒寫零寫入＋上下文缺席 5000 |
| `update-ip-rule` | notFound＋自鎖以「移除舊＋加入新」判 |
| `delete-ip-rule` | 軟刪成對寫＋刪 allow 亦過自鎖 |
| `restore-ip-rule` | 復原成對清空＋復原衝突 |
