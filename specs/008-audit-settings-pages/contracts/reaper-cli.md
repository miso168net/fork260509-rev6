# Contract — reaper（三 job 一次性 CLI、環境變數、退出碼、結構化事件、心跳與告警）

> 藍本＝`rev4:server/src/bin/reaper.rs` 之 CLI 與心跳形（重打字）；job 本體住 `server/src/reaper.rs`（lib）、進場點住 `server/src/bin/reaper.rs`。執行環境＝compose `reaper` 服務（jobs profile）；連線身分＝`reaper` role（m0004 建、`deploy/setup-reaper-role.py` 設密）。

## §1 參數

```text
reaper [--execute] [--job token-reap|audit-retention|policy-reconcile]
```

- `--execute` 缺席＝dry-run；`--job` 缺席＝`token-reap`。
- 未知參數、`--job` 缺值、未知 job 名＝error 事件＋退出 1（不靜默走 dry-run）。
- `policy-reconcile` 之 `--execute` 只決定心跳 `mode` 標籤、行為恆唯讀。

## §2 環境變數

| 鍵 | 消費者 | 語意 |
|---|---|---|
| `APP_DATABASE_URL_FILE`／`APP_DATABASE_URL` | 全部 | 前者優先（讀檔、去尾 CR／LF）；空值、`CHANGE-ME` 開頭＝error＋退出 1 |
| `REAPER_GRACE_DAYS` | token-reap | 缺席 7；畸形 warn＋7 |
| `AUDIT_RETENTION_OPERATION_LOG_DAYS`／`_ACCESS_LOG_DAYS`／`_LOGIN_ATTEMPT_DAYS`／`_SESSION_EVENT_DAYS` | audit-retention | data-model §3.3 三分語意；前置全驗先於連線字串解析 |
| `REAPER_INTERVAL_SECS` | compose dev loop（非 bin） | 缺席 86400；與告警⑤／⑥／⑦b 門檻 172800 互為 2× 錨 |
| `RUST_LOG` | 全部 | 預設 `info`；JSON 單行輸出 |

## §3 退出碼

0＝完跑（含 0 列）；1＝參數錯、前置全拒、連線字串錯、連線失敗、任一步查詢或交易失敗。心跳推送失敗不改退出碼。

## §4 結構化事件（`target = "reaper"`；欄名契約）

| 事件 | 級 | 欄 |
|---|---|---|
| 參數錯／未知 job | error | `error`、（`job`） |
| 保留天數前置全拒 | error | `job`、`error`（聚合指名鍵＝值） |
| 保留天數畸形 | warn | `key`、`raw`、`default` |
| 寬限畸形 | warn | `raw`、`default` |
| 連線字串／連線失敗 | error | `job`、`error` |
| token-reap 完跑 | info | `job`、`mode`、`grace_days`、`deleted`｜`candidates` |
| token-reap 失敗 | error | `job`、`mode`、`error` |
| audit-retention 逐表完跑 | info | `job`、`mode`、`table`（wire 值）、`retention_days`、`deleted`｜`candidates` |
| audit-retention 逐表失敗 | error | `job`、`mode`、`table`、`error` |
| audit-retention 摘要 | info | `job`、`mode`、`deleted_total`｜`candidates_total` |
| policy-reconcile 完跑 | info | `job`、`mode`、`menu`、`button`、`endpoint`、`total` |
| policy-reconcile 失敗 | error | `job`、`error` |
| 心跳已推／推送失敗 | info／error | `job`、`mode`／`error` |

## §5 job 行為

| job | dry-run | execute | 自記 |
|---|---|---|---|
| token-reap | `count_reap_candidates(G)` | `reap_expired(G)`（單語句） | 無 |
| audit-retention | 固定表序逐表 `count_before(days)` | 固定表序逐表 `purge_with_self_record(…, System(AuditRetention))` | 每表一列（刪 0 列照落；data-model §7） |
| policy-reconcile | `orphan_counts()` | 同左 | 無（零寫入） |

固定表序：`operationLog`→`accessLog`→`loginAttempt`→`sessionEvent`。任一表失敗即停、已 commit 之表維持（下輪冪等）。

## §6 心跳

- 端點：`PUT http://pushgateway:9091/metrics/job/reaper/reaper_job/<job>`（整組替換）；本程序內以 `PrometheusBuilder::build_recorder()` 建區域 recorder、`metrics::with_local_recorder` 設值、`handle().render()` 為 body（全域 recorder 一行程只能裝一次、且會夾帶他處註冊之序列）；HTTP client＝ureq（版本見 ADR③ 親決紀錄）、`timeout_global` 10 秒、`default-features = false`。
- 序列：

| metric | 標籤 | job | 值 |
|---|---|---|---|
| `reaper_last_success_timestamp` | `mode` | 三 job | unix 秒 |
| `reaper_deleted_total` | `mode` | token-reap、audit-retention | execute＝實刪；dry-run＝候刪 |
| `reaper_orphan_policies` | `dimension`（`menu`／`button`／`endpoint`） | policy-reconcile | 該維孤兒授權列數 |

- 只在完跑後推；失敗＝error 事件、不重試。scrape 端 `honor_labels: true`（既設）。

## §7 compose

- `docker-compose.yml` 之 `reaper` 段：現況句改 as-built（bin 與 role 已備）；互錨註補 policy-reconcile。
- `docker-compose.dev.yml` 之 loop：`token-reap --execute; audit-retention --execute; policy-reconcile --execute; sleep`（`;` 分隔）；一次性 `dry-run`／透傳兩形照舊。
- 走查期間與真庫測試期間不起 jobs profile。

## §8 告警（`deploy/grafana-provisioning/alerting/rules.yml`）

| 號 | uid | 條件 | 本刀處置 |
|---|---|---|---|
| ⑤ | `obs016-reaper-heartbeat-timeout` | `time() - reaper_last_success_timestamp{mode="execute", reaper_job="token-reap"} > 172800` | 現況註改有源 |
| ⑤b | `obs016-reaper-mode-misconfig` | token-reap dry-run 序列在而 execute 缺 | 同上 |
| ⑥ | `obs017-audit-retention-heartbeat-timeout` | audit-retention 同形 | 同上 |
| ⑥b | `obs017-audit-retention-mode-misconfig` | audit-retention 同形 | 同上 |
| ⑦ | `obs017-policy-reconcile-orphans`（新） | `max(reaper_orphan_policies{reaper_job="policy-reconcile"}) > 0` | 新增 |
| ⑦b | `obs017-reconcile-heartbeat-timeout`（新；uid ≤ 40 字元、title `policy-reconcile-heartbeat-timeout`） | `time() - reaper_last_success_timestamp{reaper_job="policy-reconcile"} > 172800`（不分 mode：`--execute` 只決定心跳 mode 標籤＝兩種心跳同證對賬已跑） | 新增；納入三檔互錨 |

RUNBOOK §8 補對賬非零之處置子節（判讀＋兩路處置：非 seed 角色＝刪除該角色經連動歸檔；seed 角色或逐列清＝維運 SQL 範本〔先匯出待刪列留存再刪、不手寫歸檔列〕）。
