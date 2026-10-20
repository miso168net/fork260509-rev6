---
id: "ADR-00101"
title: reaper 三 job（token-reap、audit-retention、policy-reconcile）與最小權限 role——rev4 CLI 形重打、job 本體住 lib；排程清理經 retention 共用核（自記列操作者空、來源位址哨兵 `0.0.0.0`、刪 0 列照落）；孤兒授權列只報不刪＋RUNBOOK 處置；心跳 pushgateway（ureq）與告警重錨＋對賬告警兩條
date: 2026-10-21
status: proposed
supersedes: []
superseded_by: []
provenance: "008-audit-settings-pages 之 spec FR-030～FR-038、FR-019、FR-043、US3 第 7～11 條、US5、SC-007、SC-008、Edge Cases「reaper」「授權對賬」；brainstorm §0 B1、B4、D8、grilling g2（哨兵 `0.0.0.0`）、g3（只報不刪＋RUNBOOK 處置）、g5（刪 0 列照落）、主線工程判斷⑦⑨⑩㉕；clarify 步之主線工程判斷（對賬告警兩條、每維一條 gauge）；plan 期 research R8、R11（HTTP 實作比較：甲 metrics-exporter-prometheus push-gateway 不適、乙 ureq 採、丁 hyper 低階 client 棄；版本兩源分歧＝全域 §6 交 user）、R14；001 data-model §4 前瞻註（retention 類系統程序寫操作日誌時 real_ip 取值屬該刀拍板〔sentinel 或另議〕）；藍本＝rev4:server/src/bin/reaper.rs、rev4:server/src/model/facade/sys_token.rs、rev4 compose dev loop；憲法島 E 末兩點與島 F 之 F3①（佔位位址之禁）"
tags: [audit, reaper, retention, authz-governance, observability, dependency]
---

## 背景

- compose 已有 jobs profile 之 `reaper` 服務與 metrics profile 之 `pushgateway`、密鑰產生器已產 `reaper_password`／`reaper_database_url`；rev6 無 reaper bin 與 role＝「起了也跑不動」、告警⑤⑤b⑥⑥b 無事件源（BL-00043）。
- `sys_operation_log.real_ip` 為 INET NOT NULL；rev4 reaper 自記寫 NULL＝帶不進來（g2）。
- `AuditOperator` 唯一建構點＝自請求上下文轉錄；系統程序無請求上下文。
- 孤兒授權列（候選外現役列、角色無主列）在畫面上清不掉（ADR-00066 後果）。

## 考慮過的替代案

1. **reaper 鏡像 handler 常數與白名單（rev4 形）**——兩側漂移靠雙側斷言；否決（同 crate 直接引用共用核）。
2. **自記列來源位址用 `127.0.0.1`**——dev 真請求可能同址、無從區分；否決（g2）。
3. **系統自記沿用 `AuditOperator` 加一個「系統」建構點**——HTTP 寫端拿得到該建構點＝哨兵可外溢；否決（另立具名型）。
4. **對賬自動刪除孤兒列**——畫面無清理路、誤刪不可回；否決（B4／g3）。
5. **心跳推送用甲（exporter 內建 push-gateway）**——永不返回之迴圈、成敗不回報、panic 路徑改退出碼；否決。用丁（hyper 低階 client）——偏離藍本、自寫 HTTP 管線；否決。
6. **job 本體全在 bin（rev4 形）**——真庫測試無法用 lib 之測試基建；否決。

對所選方案跑同一反例（RL-0013）：「哨兵外溢到 HTTP 寫端」→哨兵只住 facade 系統入口、HTTP 路型別上拿不到；不成立。「排程清理與手動清理謂詞漂移」→同一支共用核；不成立。「推送端黑洞卡死 loop」→全程時限 10 秒；不成立。

## 決定

1. **CLI 與退出碼**：`--execute`（缺席＝dry-run）＋`--job token-reap|audit-retention|policy-reconcile`（預設 token-reap）；未知參數與 job 嚴拒；0＝完跑（含 0 列）、1＝任一步失敗；失敗不推心跳（契約＝本刀 contracts/reaper-cli.md）。
2. **環境變數**：四表保留天數三分語意（缺席 90、畸形告警退 90、解析成功且 < `PURGE_MIN_DAYS` 前置全拒且先於連線）；`REAPER_GRACE_DAYS` 缺席或畸形退 7；dev loop 每日一輪（`REAPER_INTERVAL_SECS` 缺席 86400）與告警門檻 172800 互為 2× 錨（三檔同步）。
3. **token-reap**：判準 `expires_at < now() − G 天`（rev4 形、不分 status）、單語句刪除；不落操作日誌自記（會話域、非稽核表之水平線清理）。
4. **audit-retention**：固定表序四表、逐表經 retention 共用核單交易「刪＋自記」（與手動清理同謂詞同自記形；下限直接引用 `PURGE_MIN_DAYS`、不鏡像）；任一表失敗＝退出 1、已 commit 之表維持。
5. **排程清理自記列**：`created_by` NULL、`real_ip`＝`0.0.0.0`、`peer_ip`／`x_forwarded_for`／`ip_confidence` NULL、`payload_after`＝`{table, before_days, deleted_count, job}`；刪 0 列照落（每輪四列）。寫入經系統程序具名型（封閉 enum、只收碼內字面）與 facade 專屬入口；哨兵常數只住該 facade。★哨兵＝無網路來源之標記，只用於無操作者之系統程序自記列；非島 F 之 F3① 與島 E 末點所禁之「有操作者而取不到其位址時以佔位位址補足」——HTTP 寫端照舊只轉錄請求上下文、缺席拒寫 `5000`（001 data-model 前瞻註之兌現）。
6. **policy-reconcile**：唯讀三維（選單、按鈕、端點）計數孤兒授權列（候選外或角色無主；每列每維至多計一次）；有無 `--execute` 皆零寫入；結構化日誌指名三維計數；不自動刪。處置＝RUNBOOK（非 seed 角色＝刪除角色經連動歸檔；seed 角色或逐列清＝維運 SQL 範本：先匯出待刪列留存再刪、不手寫歸檔列）。
7. **心跳**：grouping key `…/metrics/job/reaper/reaper_job/<job>`（PUT 整組替換）；`reaper_last_success_timestamp{mode}`（三 job）、`reaper_deleted_total{mode}`（token-reap、audit-retention）、`reaper_orphan_policies{dimension}`（policy-reconcile）；完跑後推、best-effort、全程時限 10 秒、失敗不改退出碼。
8. **HTTP 實作**：ureq（`default-features = false`；rev4 藍本形）；版本＝3.4.2（user 2026-10-21 plan 期擇定；全域 §6 兩源：rev4 lockfile 3.3.0、crates.io 最新穩定 3.4.2）、完整版號釘於 workspace（`ureq = { version = "3.4.2", default-features = false }`）；lockfile 連帶解析 `ureq-proto` 0.6.5、`base64` 0.23.1（與既有 0.22.1 兩大版本並存）。
9. **連線與 role**：以 `reaper_database_url`（`reaper` role）連線、不掛 `database_url`；連線字串解析取 Result 形（拒空值與範本佔位值）。role 由 m0004 建（ADR-00108）、`deploy/setup-reaper-role.py` 設密。
10. **告警**：⑤⑤b⑥⑥b 現況註改有源；新增 `obs017-policy-reconcile-orphans`（任一維 > 0）與 `obs017-policy-reconcile-heartbeat-timeout`（> 172800）；④ audit-capacity 現況註改述（處置路＝稽核頁清理或排程清理）。
11. **compose**：兩檔 reaper 段現況改 as-built；dev loop 依序三 job、`;` 分隔（失敗互不阻斷）。
12. **碼位**：job 本體住 lib `server/src/reaper.rs`；`server/src/bin/reaper.rs` 只為進場點（契約＝本刀 contracts/reaper-cli.md）；真庫測試直接呼叫 lib 之 job 函式、以參數注入天數（替代案 6）。

## 後果

- 自記列永久豁免＝每年約 1,460 列不可清（g5）。
- 新增四支純 Rust crate（ureq 3.4.2、ureq-proto 0.6.5、utf8-zero、base64 0.23.1）；base64 兩大版本並存、ureq-proto 0.6.5 為 2026-10-17 新發布版。
- 走查與真庫測試期間不起 jobs profile（R4）；reaper 真庫案以函式參數注入天數並帶前置斷言（防刪 dev 庫真實舊列）。
- 對賬非零只告警、處置仰賴維運者照 RUNBOOK。

## 翻案觸發器

- 出現需記錄操作者之排程作業（如由人觸發之批次）⇒ 重評哨兵之射程。
- 對賬非零長期無人處置、或出現畫面清理路之需求 ⇒ 重評「只報不刪」。
- pushgateway 改為 TLS 端點 ⇒ 重評 ureq 之 feature 與依賴。
- 保留天數需於畫面設定 ⇒ 重評 D8（環境變數）。

## 親決分類

依 ADR-00089（RL-0086）；類別定義同 ADR-00099 本節。

| 款 | 類別 | 出處或理由 | 白話一句 |
|---|---|---|---|
| 決定 1 | 承決 | brainstorm ⑨；spec FR-030 | 三個工作、預設只看不刪，參數打錯就退出。 |
| 決定 2 | 承決 | brainstorm D8；spec FR-034、FR-038 | 保留天數用環境變數，太短就整輪拒跑，每天跑一輪。 |
| 決定 3 | 承決 | brainstorm B1；spec FR-032 | 回收過期登入票，不寫稽核自記。 |
| 決定 4 | 承決 | brainstorm B1、⑦；spec FR-033、FR-019 | 排程清理和手動清理用同一套規則與同一個下限。 |
| 決定 5 | 承決 | grilling g2、g5；spec FR-036 | 排程清理的自記列沒有操作者、來源位址記 0.0.0.0，刪 0 列也記。 |
| 決定 6 | 承決 | brainstorm B4、grilling g3；spec FR-035、US5 | 找出孤兒授權列只報數字不刪，處理方式寫在 RUNBOOK。 |
| 決定 7 | 承決 | spec FR-030（best-effort、全程時限、失敗不改退出碼）、FR-037（grouping key 按 job、PUT 整組替換；metric 名與 10 秒屬款內工程細節） | 每個工作各自回報心跳與數字，推送失敗不影響結果。 |
| 決定 8 | 承決 | user 2026-10-21 plan 期 AskUserQuestion 答「3.4.2，官方最新穩定版」（原標待決：新依賴版本兩源分歧、全域 §6 交 user 擇一）；實作取乙＝spec FR-037（plan 期定案＝乙） | 心跳用 ureq 送出，版本用官方最新穩定版 3.4.2。 |
| 決定 9 | 承決 | spec FR-031；brainstorm ⑪ | 用專屬的最小權限帳號連資料庫。 |
| 決定 10 | 承決 | spec FR-043（規則名＝主線工程判斷、clarify 步定案） | 既有告警改成有資料來源，另加兩條對賬告警。 |
| 決定 11 | 承決 | spec FR-038 | compose 說明改成現況，開發環境每輪跑三個工作。 |
| 決定 12 | 工程 | 碼位（替代案 6；research R11） | 工作的本體寫在共用程式庫，執行檔只負責啟動。 |

- **親決紀錄**：（plan 期）待決 1 款（決定 8）於 plan 期 AskUserQuestion 一題：user 2026-10-21 答「3.4.2，官方最新穩定版」（非建議項；建議項＝rev4 驗證過之 3.3.0＋ureq-proto 0.6.0；作答時 HEAD＝`926b359`、本 ADR 草稿未入版控），同日改標承決、版本與連帶依賴入款文與後果。獨立核對（ADR-00089 決定 5；2026-10-21）：11 列中相符 10（決定 1～6、8～11；決定 8 之待決標註）、改正 1（決定 7 含 spec 承決之心跳語意、原標工程＝依混類取最高改標承決並補 FR-030／FR-037）、漏列 1（標題「job 本體住 lib」無對應款＝補決定 12〔工程〕並入表）；改過之款於轉 accepted 前依 ADR-00089 決定 6② 復核。
