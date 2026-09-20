# Contract — 管理員解鎖端點

> 一條 route、政策保護（seed 148、`R_SUPER`）；按鈕權限碼 `user:unlock`（seed 157）已在 ⇒ 零 seed 變更。★本刀 **API-only**：不建前端包裝（按鈕歸使用者管理頁刀；已知態、收刀記 BL）。藍本＝`rev5:004` `contracts/wire-throttle-unlock.md`；rev6 差異＝**無 L1 鎖定鍵 DEL 步**（Q7）、未鎖標的照寫稽核與標記（clarify Q2）、`redis_down` 由標記讀取立（§5 ②）。

## `POST /systemManage/unlockLogin`

Req（camelCase；兩維擇一）：

| 欄 | 型 | 語意 |
|---|---|---|
| `dimension` | string | `user`｜`ip` |
| `userName` | string \| null | 維度 `user` 時必給（帳號名原文＝帳號維計數身分） |
| `target` | string \| null | 維度 `ip` 時必給——位址字面，由後端導出計數桶（v4 `/32`、v6 `/64`、IPv4-mapped 先折 v4；`unspecified`→畸形） |

處理序（★次序即契約）：
1. 維度解析＋標的導出——畸形（維度不明／位址不可解析／該維必填欄缺席）→`2222 biz.throttle.invalidUnlockTarget`；★先於一切稽核與狀態寫入 ⇒ 零稽核列、零狀態變更。
2. 操作者上下文缺席→`5000`（F3① 同向、不補佔位）。
3. **先寫操作稽核列**（`entity_table=login_throttle`、`entity_id=NULL`、`payload_after={dimension,userName,target}`）——寫入失敗→`5000` 中止、快取一概不動。
4. 寫該維解鎖標記（`throttle_unlock_user_key(name)`／`throttle_unlock_ip_key(bucket)`；值＝unix 秒十進位字串；TTL＝該維窗長上界 1440 分〔標記只需活過最長窗〕）。★**不查鎖態、不 DEL 任何鎖定鍵**（無 L1）；未鎖標的同樣走 3→4、回 `0000`（冪等：解鎖＝「自此刻重新計數」）。

200：`{ code: "0000", msg: "common.success", data: null }`。錯誤：`2222 biz.throttle.invalidUnlockTarget`／`5003 system.forbidden`（非超管）／`5000 system.internal`（稽核寫入失敗、上下文缺席、內部異常）。標記寫入失敗（稽核已落）→`5000`（可重試；稽核留下「有人嘗試過」）。

## 帳號維三件補齊（計數查詢本體零改動）

前一刀已把帳號維計數下界的解鎖標記參數位預留（無標記綁 NULL、`GREATEST` 非 strict）。本刀補：①標記鍵 builder ②讀取端（precheck 步驟①，Err→視為無標記＋`redis_down`、`throttle_degraded_total{source="unlock_marker_user"}`）③計數標籤（觀測維度）。來源維同形（`unlock_marker_ip`）。

## 契約測試 case

| case_key | 斷言重點 |
|---|---|
| `unlock-login` | 兩維各一案解鎖後立即可再試；畸形零稽核零狀態；稽核寫入失敗即中止；未鎖標的 `0000` 且稽核列與標記照寫；上下文缺席 5000 |
