# Data Model — 004-ip-trust-anchor（Phase 1）

> ★本刀**零 migration、零 seed 變更**（research R12-1 再證）——本檔描述既有結構的**消費形**與非資料庫的記憶體／設定實體，不含任何 DDL。承 `rev5:004` data-model §1～§7 形、依 rev6 拍板改寫（無 L1、消費側驗界、Q1～Q3、§5 ①～⑩）。

## §1 既有資料表的消費面（零結構變更）

### 1.1 `sys_ip_rule`（變體 A 業務表、六審計欄；seed 0 列、本刀首個寫入者）

| 欄 | 型 | 本刀消費 |
|---|---|---|
| `id` | bigint PK | wire 上為 number（§I.3 預設＋2^53 fail-loud 守衛） |
| `wbip_cidr` | inet NN | 寫入前**正規化主機位元**（`203.0.113.7/24`→`203.0.113.0/24`）；讀端以網段字面上 wire |
| `wbip_type` | varchar NN | 二值封閉 `allow`／`deny`；讀端對未知值 **skip＋告警** |
| `wbip_memo` | text 可空 | 僅管理列表顯示；渲染端純文字插值 |
| `order` | int 可空 | 上 wire、**不參與判定** |
| 六審計欄 | — | `created_at`／`created_by`／`updated_at`／`updated_by` 上 wire（操作者以帳號名批次回填、查無→null）；`deleted_at`／`deleted_by` 不上 wire、以導出布林 `deleted` 表達 |

**唯一性**：既有 partial unique `(wbip_cidr, wbip_type) WHERE deleted_at IS NULL` ⇒ 軟刪後同組合可重建；重複寫入映業務錯誤 `biz.ipRule.conflict`。**併發**：無版本欄（零 migration）⇒ 同列併發更新後寫勝；併發同組合新增由 partial unique 定勝負（後者得 conflict）；防自鎖判定於同一交易內以「變更後規則集」模擬、TOCTOU 窗承 rev5 已知態。

**狀態機**（軟刪二態；每列「現態×事件→次態＋副作用」）：

| 現態 | 事件 | 次態 | 副作用（同一交易；成功後 reload＋門鈴） |
|---|---|---|---|
| （無） | add | active | 類型守門→正規化→防自鎖（加入）→落庫＋稽核列 `add` |
| active | update | active | 防自鎖（移除舊、加入新）→改列＋稽核列 `update` |
| active | delete | deleted | 防自鎖（移除）→`deleted_at`／`deleted_by` 成對寫＋稽核列 `delete` |
| deleted | restore | active | 防自鎖（加入）→成對清空＋稽核列 `restore`；與現有有效列衝突→conflict |
| deleted | delete／update | — | `biz.ipRule.notFound`（狀態不符） |
| active | restore | — | `biz.ipRule.notFound` |

### 1.2 三張稽核表的來源三欄（值域擴張、零 DDL）

| 表 | `peer_ip` | `real_ip` | `ip_confidence` |
|---|---|---|---|
| `sys_login_attempt` | inet 可空｜**本刀開始填**（此前恆 NULL） | inet NN｜改由信任錨推導 | text 可空、無 CHECK｜`nginx_peer` 單字面→**八態** |
| `sys_access_log` | 同上（本刀不寫該表；BL-00043 access 面＝008） | 同上 | 同上 |

★`session_event` **不在**此列：該表只有 `source_ip varchar(45)`（無 `peer_ip`／`ip_confidence`、非 INET）；本刀 refresh／logout 寫入之 `source_ip` 改收信任錨 `real_ip` 字串、零欄變更。
| `sys_operation_log` | 本刀首寫者（§1.3） | 同上 | 同上 |

★既有列不遷移（append-only 表不可竄改）；查詢端容忍 `nginx_peer` 與八態並存。★`chain_rejected` 兩連帶：①語意＝「這條鏈逾上界、未被推理採信」——`sys_login_attempt` 上恆為「被拒」列、`sys_operation_log` 上為「標記但照服務」列，兩表同字面語意不同、報表 MUST 分表判讀；`real_ip` 在該態下**恆有值**（取自傳輸層對端）；②計數分流：帳號維查詢 `AND ip_confidence IS DISTINCT FROM 'chain_rejected'`（`<>` 對 NULL 回 NULL 會漏既有列）、來源維**不加**過濾（釘住測試守之）。

### 1.3 `sys_operation_log`（變體 B append-only；本刀首個寫入者）

寫入時機恰五處：規則 add／update／delete／restore＋解鎖。

| 欄 | 值 |
|---|---|
| `operation` | 規則四寫端＝對應動作字面；解鎖＝`unlock`（五字面由 `AuditOperation` 單一宣告源產出、零新 variant） |
| `entity_table` | 規則＝`sys_ip_rule`；解鎖＝`login_throttle`（節流子系統識別、非真表名） |
| `entity_id` | 規則＝該列 id；解鎖＝NULL |
| `payload_before`／`payload_after` | 規則＝變更前後值；解鎖＝`{dimension, userName, target}`（來源維 `target`＝計數桶字面） |
| 操作者類欄 | uid＋來源三欄（取自請求上下文；缺席→拒寫 5000、不補佔位） |

落列與生效次序：規則四寫端＝**同一交易**原子；解鎖＝**先落稽核列、後寫標記**（稽核失敗→5000 中止、快取不動）；★Q2：未鎖標的亦照寫稽核列與標記（不查鎖態）。

### 1.4 `system_settings` 兩組節流鍵（零 seed 變更、只讀消費；界值沿 `validation::REGISTRY`）

| 鍵 | seed | registry `range` | 消費點 |
|---|---|---|---|
| `login_throttle_max_fails`／`login_throttle_window_minutes`／`login_throttle_captcha_after` | 5／15／2 | 1..100／1..1440／1..100 | 帳號維（既有；本刀加越界判） |
| `ip_max_fails`／`ip_window_minutes`／`ip_captcha_after` | 50／15／10 | 1..100／1..1440／1..100 | 來源維（本刀首個消費者；「有值零行為」已知態解除） |

**有效性判準（兩維同形、整組）**：任一鍵缺列／軟刪／不可解析／`range` 越界／`captcha_after > max_fails` ⇒ 該組整組退常數（帳號維 `5／15／2`、來源維 `50／15／10`；鍵序＝硬門檻／窗分鐘／驗證碼門檻）＋每次載入至多一筆告警（label 分流）；相等合法。★每次登入嘗試讀現值（跨島總則）；寫端零改動（Q4）。

## §2 記憶體與設定實體（非資料庫）

### 2.1 `TrustModel`（啟動時一次載入、`Arc` 唯讀共享；契約＝`contracts/trust-model-config.md`）

| 集合 | 語意 |
|---|---|
| `internal_default` | 內網預設受信集（dev 唯一填項＝容器網段） |
| `tunnel{networks, connecting_ip_header}` | 通道來源集與訪客位址標頭名（覆蓋 A） |
| `cf_gate_egress` | 掛邊緣驗證閘的我方出口集（覆蓋 B 前置） |
| `cdn[]{networks, connecting_ip_header}` | CDN 段（Tier-1 位置錨） |
| `my_public[]{networks, dual_role}` | 我方公開出口（`proxy_soft` 觸發①） |
| `bindings[]{public, internal}` | 公開出口×專屬後置內網（`proxy_soft` 觸發②） |

單一 helper 導出受信集＝跳過集＝六集合聯集（同源對稱、F4／F6）；預設全空＝全直連；載入三層失敗語意＋IPv4-mapped 網段字面清集合（`rev5:B-074`）皆不當機、皆告警。

### 2.2 `RuleSet`（判定面）

`{allow: Vec<IpNetwork>, deny: Vec<IpNetwork>}`；`Arc<ArcSwap<RuleSet>>` 存 `AppState`、每請求 `.load()`；`Default`＝兩袋皆空＝全放行。結構豁免六段（`127.0.0.0/8`／`::1/128`／`10.0.0.0/8`／`172.16.0.0/12`／`192.168.0.0/16`／`fc00::/7`）先於兩袋、只豁免阻擋。規模假設＝規則列數為百位數量級、線性 any-match 掃描（每請求零外部查詢即為 F2 之量化目標；不設索引結構）。

### 2.3 `RequestContext`（每請求一次；中介層注入、可缺席）

| 欄 | 本刀後內容 |
|---|---|
| `real_ip` | 信任錨推導之正規化字串（缺席退路＝`X-Real-IP` 原文） |
| `x_forwarded_for` | **判定窗**轉錄（最右 `MAX_XFF_TOKENS`＝32 欄，再以 `XFF_MAX_CHARS`＝1024 兜底；零 CR/LF）；缺席退路＝空 |
| `ip_confidence` | 八態字面；缺席退路＝`fallback` |
| `peer_ip`（新增消費） | 傳輸層對端（`ConnectInfo<SocketAddr>`）；缺席退路＝NULL |

三欄私有＋取值器簽名不變（編譯期守門 doctest 續存）；建構點兩個＝`from_trust`（中介層）與 `from_headers`（缺席退路、既有）。★缺席矩陣（§5 ①）：

| 消費面 | 缺席處置 |
|---|---|
| `ip_gate_mw` | 放行（F1②）＋`request_context_absent` 降級計數 |
| 來源維節流 | 整層跳過（`ctx_absent` 就地記下、precheck `source=None`） |
| login／refresh／logout | 退 `from_headers`：缺 `X-Real-IP`→5000 不落列；在場→轉錄（`fallback`／peer NULL／窗空）＋warn＋降級計數 |
| 規則四寫端／解鎖 | 拒寫 5000（F3① 同向；不補佔位位址） |

### 2.4 來源信心（八態、DB／wire 穩定小寫底線字面、單一出口 `Confidence::as_str`）

`cdn_verified`／`proxy_clean`／`direct`／`cdn_anchored`／`proxy_soft`／`cdn_mismatch`／`fallback`／`chain_rejected`——前七態＝三層矩陣出口（research R4）、第八態＝矩陣之後的溢出短路（鏈跳數 > 32）。dev 經反向代理可達二態（R7）。★術語：文件寫「來源信心態 `fallback`」、與活書 12 流程層「fallback」不互用。

### 2.5 節流實體

| 項 | 形 |
|---|---|
| 計數桶 | v4 `a.b.c.d/32`；v6 `xxxx::/64`（截斷主機位元）；IPv4-mapped 先折 v4；`unspecified`→無桶（來源維整層跳過） |
| 快取鍵 | 兩維解鎖標記 `throttle_unlock_user_key(name)`／`throttle_unlock_ip_key(bucket)`＋既有 `throttle_captcha_used_key`；★**無**鎖定鍵族 |
| 解鎖標記值 | unix 秒十進位字串；不可解析→視為無標記；讀取 Err→視為無標記（fail-closed）＋本次 `redis_down`；TTL＝最長窗上界 1440 分（標記只需活過最長窗） |
| 計數下界 | 帳號維三源（窗起點／窗內最近成功／標記）；來源維**恰兩源**（窗起點／標記，`GREATEST` 非 strict、無標記綁 NULL） |
| `ThrottleSettings` | 兩維各一份 `{max_fails, window_minutes, captcha_after, origin: Seed|Default}`；載入結果附「是否退常數」供 label |
| 三區判定 | `count < captcha_after` 自由／`captcha_after ≤ count < max_fails` 軟區／`count ≥ max_fails` 鎖定；合成＝任一硬鎖→locked、任一軟區或 `captcha_forced`→captcha gate |

## §3 判定資料流（單一方向）

```
ConnectInfo(peer) ─┐
                   ├→ trust::resolve（純函式；三層＋兩覆蓋＋F6）→ apply_chain_overflow（F7） → RequestContext（Extension；可缺席）
XFF／CF 標頭 ──────┘                                                                         │
            ┌──────────────┬──────────────────┬──────────────────┬──────────────────────────┤
            ▼              ▼                  ▼                  ▼                          ▼
       ip_gate_mw     來源維節流           稽核落列          防自鎖（decide 同源）      F7 登入拒絕（login 先於 precheck）
       （decide）  （ip_bucket＋L0 allow 直讀袋）（三欄如實）
```

同源約束：閘門與防自鎖共用 `decide`；來源維 L0 直讀 allow 袋、絕不經 `decide`（F5）。

## §4 不變式（隨 ADR-00034 入憲；條文全文住該 ADR §二）

島 F：F1 六步判定序＋any-match／F2 真相分層 keep-last-good／F3 fail-open 且 fail-closed 恰兩處（①寫端自鎖含輸入不可得同向 ②F7）／F4 信任錨唯一位址輸入＋兩集合同源／F5 顯式放行跳節流、結構豁免不跳／F6 Tier-1 錨傳輸層背書／F7 鏈跳數上界（登入拒絕、其餘標記）／F8 判定窗轉錄兩成立條件。島 E 四處：判定每次嘗試由 PG 定案、無負快取（刪 L1 句）／來源維計數下界恆兩源、禁成功即重置／解鎖標記讀取故障＝fail-closed（兩維共用）／設定壞值判準補「越界」且整組退。跨島總則不動。

## §5 降級矩陣與序列名冊（★本表＝值名單一權威，`obs.rs` 常數照抄、pre-register 全部為 0）

**`throttle_degraded_total{source}`（7→10 值）**

| source | 維 | 觸發 | 方向 |
|---|---|---|---|
| `settings_default` | 帳號 | 缺列／不可解析／越界／查庫失敗→整組退 | fail-open |
| `settings_invalid` | 帳號 | 矛盾組合→整組退 | fail-open |
| `ip_settings_default` | 來源 | 同上（來源維獨立 label） | fail-open |
| `ip_settings_invalid` | 來源 | 同上 | fail-open |
| `unlock_marker_user` | 帳號 | 標記讀取 Err（視為無標記＋立 `redis_down`） | fail-closed（標記）＋fail-open（captcha 層） |
| `unlock_marker_ip` | 來源 | 同上 | 同上 |
| `redis_captcha` | — | 既有（消耗標記 SET NX 瞬斷） | fail-closed 不罰 |
| `db_count` | 帳號 | 計數 DbErr→count 0＋captcha_forced | fail-open＋補償 |
| `ip_db_count` | 來源 | 同上 | 同上 |
| `db_write` | — | 既有（record_attempt 寫失敗） | warn |

刪除：`redis_lock`／`redis_lock_set`（L1 已無）。

**`ip_domain_degraded_total{source}`（新序列、8 值）**：`trust_model_missing`（缺席→扁平退路）／`trust_model_invalid`（整體損壞→全空）／`trust_model_set_cleared`（單集合含無效網段或 IPv4-mapped 字面→清該集合）／`ruleset_initial_load`（初載失敗→空集放行）／`ruleset_reload`（執行中重載失敗→keep-last-good）／`doorbell_publish`／`doorbell_subscribe`（含 timeout、斷線、重連補讀失敗）／`request_context_absent`（閘門放行＋auth 端點退路共用）。

**`ipgate_blocked_total`**（無 label；命中網段記於結構化 warn、非降級）。

★刻意不在矩陣內：F7 拒絕（明確處置；可觀測＝warn＋`chain_rejected` 稽核列）／`build_ruleset` 未知型列（資料品質事件、載入面 warn）／IP 閘阻擋（正常工作）／寫端自鎖（業務錯誤回應）——與 `rev5:004` data-model §5 同判。

## §6 錯誤碼對應（13 碼矩陣零觸碰、零新變體）

| 情境 | 碼 | msg key |
|---|---|---|
| IP 閘阻擋／F7 登入拒絕 | `5003`（HTTP 403 例外） | `system.forbidden`（既有） |
| 規則類型非二值／網段不可解析／唯一衝突／標的不存在或狀態不符／寫端自鎖 | `2222` | `biz.ipRule.invalidRuleType`／`invalidCidr`／`conflict`／`notFound`／`selfLock` |
| 解鎖參數畸形 | `2222` | `biz.throttle.invalidUnlockTarget` |
| 兩維硬鎖／軟區 | `2222` | `biz.auth.locked`／`biz.auth.captchaRequired`（既有、不揭露維度） |
| 上下文缺席（寫端）／稽核寫入失敗／DbErr | `5000` | `system.internal`（既有） |

六新鍵之家＝三檔 locale backend 子樹（各語權威）＋`app.d.ts` backend 型節；鍵集由 msg-key-gate 對賬（`MSG_KEYS` 19）。

## §7 sequence 與測試基建紀律（G6）

runtime-append 四表（`session_event`／`sys_login_attempt`／`sys_operation_log`／`sys_token`）序列在測試中一律不復位、各案只清自己寫的列（水位守衛住 `test_kit.rs`）；`walkthrough-baseline diff` 對四表序列只比存在性（與 schema-gate gate2 正規化同口徑）、restore 仍依基準檔 setval；`sys_ip_rule` 業務表＝測試與走查寫入須清列＋還原序列（seed 模式承載）。稽核斷言一律水位／窗形（`entity_id` 對規則 id、序列復位後 id 重用即誤紅）。

## §8 clarify 定案之資料面落點

| Q | 落點 |
|---|---|
| Q1 阻擋不撤會話 | §1.2 無新寫入面；`sys_token`／denylist 零觸碰 |
| Q2 未鎖解鎖照寫 | §1.3 解鎖列無「是否在鎖」欄；標記無條件寫 |
| Q3 UI 對照結構清單 | 非資料面；quickstart §6 清單 |
