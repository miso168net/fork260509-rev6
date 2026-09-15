# Contract Delta — login／refresh／logout（相對 003 契約快照）

> **基底**＝`specs/003-auth-session/contracts/wire-auth.md`（凍結快照；本檔只記本刀**增量列**，未列者維持基底；brainstorm G2、§5 ⑩、spec FR-044）。wire 活體權威＝碼＋`tests/contract.rs`（case_key `auth-login`／`auth-refresh-token`／`auth-logout` 增斷言）；既有碼之 wire 行為不變。

## 共同增量（三端點）

| 項 | 基底（003） | 本刀 |
|---|---|---|
| 來源位址輸入 | `RequestContext::from_headers`（`X-Real-IP` 原文轉錄、信心 `nginx_peer`） | 中介層注入之信任錨結果（八態；F4）；`peer_ip` 開始落欄；轉發鏈欄改判定窗轉錄（F8） |
| 請求上下文缺席 | 不存在此態（handler 直建） | `Option<Extension>` 缺席→退 `from_headers`：缺 `X-Real-IP`→`5000 system.internal` 不落列（同基底）；在場→轉錄（信心 `fallback`、`peer_ip` NULL、判定窗空）＋降級告警＋`ip_domain_degraded_total{source="request_context_absent"}`；production 結構性不可達（B-075 lint） |
| `5000` 出口（補列、行為不變） | 表列只記一種 | 明列：資料庫錯誤（查詢／寫入）、交易 commit 失敗、上下文缺席（缺 `X-Real-IP`）、`session_idle_timeout` 缺失（login／refresh 既有 fail-loud）——皆 `5000 system.internal`、HTTP 200 |

## login `POST /auth/login` 增量

| 情境 | 碼／msg | HTTP | 說明 |
|---|---|---|---|
| 轉發鏈跳數 > 32（F7） | `5003 system.forbidden` | 403 | 先於節流 precheck 與密碼驗證；仍落一列 `sys_login_attempt`（`ip_confidence=chain_rejected`、`real_ip`＝傳輸層對端、`success=false`）；該列帳號維計數排除、來源維計數納入 |
| 來源維硬鎖 | `2222 biz.auth.locked` | 200 | 與帳號維同鍵、不揭露維度；密碼驗證前、零稽核列 |
| 來源維軟區 | `2222 biz.auth.captchaRequired` | 200 | 同上（合成：任一軟區即要求） |
| 兩維設定壞值 | （無新碼） | — | 整組退常數＋告警；行為照常數 |
| 快取不可用（標記讀取 Err） | （無新碼） | — | 軟區要求整層停用、續驗密碼、密碼錯仍計數（島 E 既定） |
| IP 閘阻擋（中介層、先於 handler） | `5003 system.forbidden` | 403 | 全端點共通；登入頁亦可達（前端譯文 toast） |

## refresh `POST /auth/refreshToken` 增量

| 情境 | 碼／msg | HTTP | 說明 |
|---|---|---|---|
| 鏈超長 | （不拒絕） | — | 標記 `chain_rejected` 照常服務；reuse 稽核列之來源三欄如實（含該標記） |
| 上下文缺席 | 見共同增量 | — | 呈遞列不動 |

## logout `POST /auth/logout` 增量（BL-00062）

| 情境 | 碼／msg | HTTP | 說明 |
|---|---|---|---|
| `5000` 出口 | `5000 system.internal` | 200 | 保留（Q5）：DbErr／commit 失敗＝撤銷未成、API 呼叫端須知；前端 best-effort 不看結果 |
| 故障窗弱 oracle | — | — | 「簽章有效→5000／無效→0000」只在 DB 故障窗可見、只洩持票者手上那張票；立 won't-fix 已知態 ADR（FR-045） |
| 鏈超長 | （不拒絕） | — | 標記照常服務；`session_event` 來源三欄如實 |

## 契約測試增斷言

- `auth-login`：F7 拒絕（跳數 33）先於 precheck（源序守＋行為案）、`chain_rejected` 列落且 `real_ip`＝peer；缺席退路兩腿（缺 `X-Real-IP` 5000／在場轉錄 `fallback`）。
- `auth-refresh-token`／`auth-logout`：缺席退路轉錄腿一案；`peer_ip` 落欄一案（經 make-service 形整合測試）。
- 既有 36 處 `X-Real-IP` 注入案零改形（缺席退路即其路徑）。
