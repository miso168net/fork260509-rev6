# Quickstart — 008-audit-settings-pages（驗證指南）

> 目的＝以 dev stack 端到端證明本刀可用（SC-001～SC-015 之走查面與機器命令；SC-016 屬簿記後驗、本檔只列假述掃除之命令形）；不含實作碼與測試全文。承 007 刀 quickstart 形。★一律指向 rev6 stack（UI 32080／API 經 front-nginx 之 `/api`／`/metrics` 直連 32079／PG 35432）、一律 127.0.0.1，絕不指向 rev5 對照 stack（2xxxx）。前置＝ADR-00099 accepted（憲法 1.9.0）且 m0004 已套進 dev 庫（§0）。
> ★逐欄定義以 `contracts/wire-audit.md`／`contracts/wire-settings.md` 為準、拒因鍵以 `contracts/msg-keys.md`、固定序與稽核列形以 `data-model.md` §3／§7、reaper 以 `contracts/reaper-cli.md` 為準；不符時以 contracts／data-model 為準並同批改本檔。
> ★dev 庫寫入放行（LL-00053）：§3 清理、§5 設定寫入、§6 reaper execute、§11 restore 各段起手前由主線取 user 放行。★清理只對**本段自植之舊列**與長水平線（3650 天）執行；執行前以 §3 首行之 SELECT 確認水平線前恰為自植列。★jobs profile 只在 §6 指定步驟起、跑完即停；走查期間不起。

## 0. 前置

```bash
cd <rev6 workspace 根>
dc() { docker compose -f docker-compose.yml -f docker-compose.dev.yml "$@"; }
dc ps && dc up -d --wait
BASE=http://127.0.0.1:32080/api; SM=$BASE/systemManage; J='content-type: application/json'
SQL() { dc exec -T postgres sh -lc "psql -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" -At -c \"$1\""; }
SQL "SELECT version FROM seaql_migrations ORDER BY version"
#   m0001～m0004 四列；缺 m0004＝撰寫 m0004 之單元收尾步（取 user 放行）：dc run --rm migrate → dc restart rust-api（判定面開機載入）
python3 tools/walkthrough-baseline.py snapshot "<走查基準檔（不入版控之工作區）>"   # rc 0（RUNBOOK §9c）
TOKEN() { curl -s -X POST $BASE/auth/login -H "$J" -d "{\"userName\":\"$1\",\"password\":\"$2\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["token"])'; }
ST=$(TOKEN Super "$SEED_PW"); AT=$(TOKEN Admin "$SEED_PW")      # SEED_PW＝dev seed 密碼（RUNBOOK §14；不落字面）
H() { echo "Authorization: Bearer $1"; }
```

## 1. 路由與授權態（SC-001；FR-001／FR-002）

```bash
python3 tools/docsync generate && grep -c '^| ' docs/generated/reference/routes.md   # 表列數含表頭＝66 條＋表頭兩行
for p in getOperationLog getAccessLog getLoginAttempt getSessionEvent; do
  curl -s "$SM/$p" -H "$(H $ST)" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["code"])'   # 0000
  curl -s "$SM/$p" -H "$(H $AT)" -o /dev/null -w '%{http_code}\n'                                       # 403（5003）
  curl -s "$SM/$p" | python3 -c 'import sys,json;print(json.load(sys.stdin)["code"])'                     # 8888
done
curl -s -X POST "$SM/getOperationLog" -H "$(H $ST)" -o /dev/null -w '%{http_code}\n'                      # 404（4040；動詞不符）
```

可授出集 35：contract 測釘值（容器全量測試）。

## 2. 讀端與打碼（SC-003／SC-004；FR-006～FR-014）

```bash
curl -s "$SM/getOperationLog?size=abc&operation=&current=0" -H "$(H $ST)"            # 0000、current 1、size 10（畸形與空字串＝未設）
curl -s "$SM/getOperationLog?timeFrom=2030-01-01T00:00:00Z&timeTo=2020-01-01T00:00:00Z" -H "$(H $ST)"   # records []、total 0（顛倒＝空頁）
curl -s "$SM/getLoginAttempt?realIp=127.0" -H "$(H $ST)"                               # 畸形 IP＝未設（不作子字串比對）
curl -s "$SM/getOperationLog?entityTable=sys_user&operation=update&size=1" -H "$(H $ST)"   # payloadBefore/After 之 userPhone／userEmail 已打碼
```

讀端零寫入、名對應含軟刪全集、萬用字元字面化、成敗值域外：容器全量測試（data-model §4）。

## 3. 手動清理（SC-005；FR-015～FR-020）

```bash
SQL "SELECT count(*) FROM sys_access_log WHERE created_at < now() - interval '3650 days'"   # 植列前須為 0；植列後須恰為自植數
curl -s -X POST "$SM/purgeAuditLog" -H "$(H $ST)" -H "$J" -d '{"table":"accessLog","beforeDays":29}'
#   2222、msg biz.audit.purgeBelowFloor、data {"minDays":30}
curl -s -X POST "$SM/purgeAuditLog" -H "$(H $ST)" -H "$J" -d '{"table":"sys_user","beforeDays":10}'
#   2222、msg biz.audit.invalidTable、data null（同時違反＝invalidTable）
curl -s -X POST "$SM/purgeAuditLog" -H "$(H $ST)" -H "$J" -d '{"table":"accessLog","beforeDays":3650}'
#   0000、data {"deletedCount": N}；操作日誌最新一列＝purge／sys_access_log／entity_id NULL／after {table, before_days, deleted_count}
SQL "SELECT operation, entity_table, entity_id, payload_after FROM sys_operation_log ORDER BY id DESC LIMIT 1"
```

原子性 fault-injection、永久豁免、上下文缺席 `5000`、極大天數不崩潰：容器全量測試（research R8）。

## 4. 存取日誌（SC-006；FR-021～FR-025）

```bash
W=$(SQL "SELECT coalesce(max(id),0) FROM sys_access_log")
curl -s "$SM/getRoleList?current=1&size=1&x=1" -H "$(H $ST)" >/dev/null                # 已登入請求
curl -s "$SM/getOperationLog" -H "$(H $AT)" >/dev/null                                  # 5003
curl -s "$BASE/auth/loginCaptcha?userName=x" >/dev/null                                  # 公開端點
curl -s "$SM/noSuchEndpoint" -H "$(H $ST)" >/dev/null                                    # 未註冊（4040）
sleep 1; SQL "SELECT http_method, http_path, http_status, created_by FROM sys_access_log WHERE id > $W ORDER BY id"
#   恰兩列：GET /systemManage/getRoleList 200（路徑不含 query）／GET /systemManage/getOperationLog 403；公開端點與未註冊路徑零列
```

業務拒因列狀態 200、寫入失敗回應不變＋告警＋計數、慢寫不延遲、在途 drain：容器全量測試。

## 5. 系統設定（SC-009；FR-026～FR-029、FR-045～FR-050）

```bash
curl -s "$SM/getSystemSettings" -H "$(H $ST)" | python3 -c 'import sys,json;[print(r["settingKey"],r["declared"],r.get("rangeMin"),r.get("rangeMax")) for r in json.load(sys.stdin)["data"]]'
#   16 列皆 declared True；10 個 number 鍵帶界（contracts/wire-settings.md §1 表）
W=$(SQL "SELECT coalesce(max(id),0) FROM sys_operation_log")
curl -s -X POST "$SM/updateSystemSetting" -H "$(H $ST)" -H "$J" -d '{"settingKey":"session_idle_timeout","settingValue":"60"}'   # 0000（同值照寫）
SQL "SELECT operation, entity_table, entity_id FROM sys_operation_log WHERE id > $W"     # update／system_settings／NULL 恰一列
```

32080 設定頁：四組、鉗界（`session_idle_timeout` 輸入 0 失焦→5）、矛盾提示三對、政策快取同分頁即時（§8 CDP）。改動後以 §11 還原。

## 6. reaper（SC-007／SC-008；FR-030～FR-038）

```bash
python3 deploy/setup-reaper-role.py                                  # 首次：設密＋LOGIN＋reaper 憑證 SELECT 1 自驗
dc --profile jobs run --rm reaper dry-run                            # token-reap dry-run：candidates 事件、零變動
dc --profile jobs run --rm reaper --job audit-retention              # 四表候刪數、零自記
dc --profile jobs run --rm reaper --job policy-reconcile             # menu=0 button=0 endpoint=0
AUDIT_RETENTION_ACCESS_LOG_DAYS=10 dc --profile jobs run --rm -e AUDIT_RETENTION_ACCESS_LOG_DAYS reaper --job audit-retention   # 退出 1、指名鍵值、零連線
dc --profile jobs run --rm reaper --job nope; echo "rc=$?"           # rc 1
# execute 一輪（取 user 放行；四表保留天數以環境變數設 3650）：四列 purge 自記（created_by NULL、real_ip 0.0.0.0、after 帶 job）
```

reaper 權限正負向（`SET LOCAL ROLE reaper`）、心跳推送失敗不改退出碼、對賬植列計數：容器全量測試。

## 7. m0004 與離線腿（SC-010；FR-039～FR-042）

```bash
python3 tools/schema-gate.py offline                                  # rc 0：m0003／m0004 之 seed DML 與演進帳、凍結 seed 前值一致；權限面語句列出
python3 tools/schema-gate.py test                                     # 自測含一正一反與逐判準停用變異
SQL "SELECT count(*), max(id) FROM casbin_rule"                       # 164、165
SQL "SELECT buttons FROM sys_menu WHERE id = 77"                      # [{"code": "audit:purge", "desc": "清理日誌"}]
SQL "SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname = 'reaper'"   # reaper（設密後 t）
python3 tools/schema-gate.py check                                    # 需 docker；三閘綠（含序號合成）
```

## 8. 前端與 CDP 三方對照（SC-011／SC-013；FR-051～FR-059、FR-073）

- 一律以快速登入鈕登入；對照兩側先寫 `lang` 儲存值為簡中（ADR-00084 決定 8）。
- 側欄：Super 見「系統設定」「稽核」且進得去；Admin／User 不見。
- 設定頁：四組與鍵序、控件型、說明、逐項存與回讀、鉗界、矛盾提示、宣告集外列（合成列由整合測試承擔）。
- 稽核頁：四分頁欄集與列序、搜尋卡、XFF 字面（含 `<script>` 植列）、快照浮層（打碼）、清理浮層二段確認、清理鈕依碼顯隱、兩則告示。
- 判準＝結構清單逐項全等；排除＝spec 刻意分岔登記表各項。
- 機器面：`pnpm typecheck`（容器內）、`python3 tools/fork-delta-lint.py`、`route-artifact-gate.py check`、`seed-view-gate.py check`、`view-render-guard.py check`、`zh-tw-lint.py check`、`msg-key-gate.py check`。

## 9. 測試殘列（R3 驗收）

```bash
B=$(SQL "SELECT count(*) FROM sys_access_log"); <容器內全量 cargo test --test-threads=1>; A=$(SQL "SELECT count(*) FROM sys_access_log"); test "$B" = "$A"
```

## 10. 繁中（SC-012；FR-074）

zh-tw-lint 綠＋型別檢查綠＋AI 逐頁審讀紀錄（全部接真頁面：007 已審各頁＋本刀兩頁、浮層、提示）＋user 抽查紀錄。

## 11. 收尾（SC-014～SC-016）

```bash
python3 tools/walkthrough-baseline.py diff "<基準檔>"; python3 tools/walkthrough-baseline.py restore "<基準檔>"   # 還原後 diff rc 0
python3 tools/docsync check && python3 tools/docsync lint
for w in BL-00045 BL-00043 BL-00133 BL-00139 BL-00148 seed-view-gate 恰兩列 "008 刀" "島 J" 未入憲 只限兩鍵 恰二鍵 "找不到 404"; do python3 tools/docsync errata "$w"; done
#   種子全集＝spec FR-065＋research R21 追加詞；現在式面命中逐條判讀（RL-0084）
```

Day-1 登記三步（RUNBOOK §10；第 3 步 pristine 庫）於收刀前承載體檢單元執行。
