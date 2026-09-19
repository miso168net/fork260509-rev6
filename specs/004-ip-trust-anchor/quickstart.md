# Quickstart — 004-ip-trust-anchor（驗證指南）

> 目的＝以 dev stack 端到端證明本刀可用（SC-014／SC-010／SC-009／SC-013 之走查面）；不含實作碼。承 `rev5:004` quickstart §0～§7 形、rev6 座標（埠 3xxxx、compose 專案＝倉庫根、走查工具 seed 模式）。★一律指向 rev6 stack（32080／32079／35432／36379）、絕不指向 rev5 對照 stack（2xxxx）。前置＝Amendment accepted、全部單元合入、容器內全量測試綠。

## 0. 前置

```bash
cd /mnt/d/AnewSpaces/x_Project/fork260509-rev6
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait
BASE=http://127.0.0.1:32080/api          # 經 front-nginx（反向代理＝傳輸層對端、注入 X-Real-IP／XFF）
SIM_A='203.0.113.11'; SIM_B='203.0.113.22'   # 模擬公網來源（TEST-NET-3、非結構豁免段）
PG='docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres'
RD='docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T redis'
# 走查前基準（RUNBOOK §9c 第 1 步）
python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-004.json     # rc 0
# 信任模型真的掛上（載入面告警數須為 0；grep -c 零命中 rc=1 屬正常、看印出的數）
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs rust-api 2>&1 \
  | grep -E '信任模型|connecting_ip_header' | grep -c '"level":"WARN"'
TOKEN=$(curl -s "$BASE/auth/login" -H 'content-type: application/json' \
  -d '{"userName":"Super","password":"123456"}' | jq -r .data.token); AUTH="authorization: Bearer $TOKEN"
```

★UI 登入表單另有前端格式閘（`REG_PWD`），錯密碼字面於 UI 須用合規值（如 `wrongpw`）；curl 面不受此限（承 rev5 L-047）。★勿秒內狂打 auth 端點（nginx `auth_limit` 5r/s burst 40 回 429 無信封）。

## 1. 真實來源還原（US1／SC-014 ④）

```bash
curl -s "$BASE/auth/login" -H 'content-type: application/json' -d '{"userName":"Super","password":"wrong"}' >/dev/null
curl -s "$BASE/auth/login" -H 'content-type: application/json' -H "X-Forwarded-For: $SIM_A" -d '{"userName":"Super","password":"wrong"}' >/dev/null
$PG sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT real_ip, peer_ip, ip_confidence, attempted_user_name FROM sys_login_attempt ORDER BY id DESC LIMIT 2"'
```

**預期**：帶標頭那筆 `proxy_clean`／`real_ip=203.0.113.11`；不帶那筆 `fallback`／`real_ip`＝反向代理容器位址；兩筆 `peer_ip` 皆有值（此前恆 NULL）。

## 1b. 轉發鏈超長即拒絕（F7／F8）

```bash
XFF=$(python3 -c "print(','.join(f'198.51.100.{i}' for i in range(1,34)))")   # 33 跳 > 32
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/auth/login" -H 'content-type: application/json' -H "X-Forwarded-For: $XFF" -d '{"userName":"Super","password":"wrong"}'
$PG sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT ip_confidence, real_ip, length(x_forwarded_for) FROM sys_login_attempt ORDER BY id DESC LIMIT 1"'
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/route/getConstantRoutes" -H "X-Forwarded-For: $XFF"
```

**預期**：登入 `403`（信封 `5003 system.forbidden`）、稽核列 `chain_rejected`、`real_ip`＝判定腿結論（逾限只改信心、不覆寫位址；本例經受信反向代理＝自判定窗推導之位址、**不是**反向代理容器位址）、轉發鏈欄為判定窗（長度 ≤1024）；非登入端點 `200` 照常服務。

## 2. IP 存取閘（US2／SC-014 ②）

```bash
curl -s "$BASE/systemManage/addIpRule" -H "$AUTH" -H 'content-type: application/json' -d "{\"wbipCidr\":\"$SIM_A/32\",\"wbipType\":\"deny\",\"wbipMemo\":\"walkthrough\"}"
curl -s -o /dev/null -w 'A=%{http_code}\n' "$BASE/route/getConstantRoutes" -H "X-Forwarded-For: $SIM_A"
curl -s -o /dev/null -w 'B=%{http_code}\n' "$BASE/route/getConstantRoutes" -H "X-Forwarded-For: $SIM_B"
curl -s -o /dev/null -w 'health=%{http_code}\n' "$BASE/health" -H "X-Forwarded-For: $SIM_A"
```

**預期**：`A=403`（不重啟即生效、未帶 `$AUTH` 亦擋＝閘先於驗章）、`B=200`、`health=200`（觀測端點豁免）。再對 `$SIM_A` 加一條 `allow` ⇒ `A=200`（白＞黑）。★Q1：以 `$SIM_A` 先登入取 token 再建 deny ⇒ 該 token 之後續呼叫 403 但 `sys_token` 仍 active、刪 deny 後同 token 直接 200（不必重登）。

## 3. 防自鎖（US3 場景 5／SC-006／SC-014 ③）

```bash
curl -s "$BASE/systemManage/addIpRule" -H "$AUTH" -H 'content-type: application/json' -H "X-Forwarded-For: $SIM_B" -d "{\"wbipCidr\":\"203.0.113.0/24\",\"wbipType\":\"deny\"}"
$PG sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM sys_ip_rule WHERE wbip_cidr = '"'"'203.0.113.0/24'"'"'" -c "SELECT count(*) FROM sys_operation_log WHERE entity_table='"'"'sys_ip_rule'"'"' AND payload_after::text LIKE '"'"'%203.0.113.0/24%'"'"'"'
```

**預期**：`2222 biz.ipRule.selfLock`（操作者來源 `$SIM_B` 落該網段）、兩個 count 皆 0（零落庫、零稽核列）。不帶 XFF（操作者為 `fallback` 落結構豁免段）時同一請求成功＝結構豁免不判自鎖。

## 4. 來源維節流（US4／SC-007／SC-008／SC-014 ①）

```bash
for i in $(seq 1 12); do curl -s "$BASE/auth/login" -H 'content-type: application/json' -H "X-Forwarded-For: $SIM_A" -d "{\"userName\":\"ghost$i\",\"password\":\"x\"}" | jq -r .msg; sleep 0.3; done
curl -s "$BASE/auth/login" -H 'content-type: application/json' -H "X-Forwarded-For: $SIM_B" -d '{"userName":"ghost1","password":"x"}' | jq -r .msg
```

**預期**：`$SIM_A` 第 11 次起 `biz.auth.captchaRequired`（軟門檻 10、輪換帳號名仍計）、達 50 次 `biz.auth.locked`；`$SIM_B` 不受影響（計數隔離）。穿插一次 `Super` 成功登入（帶 `$SIM_A`）後再失敗一次 ⇒ 仍在軟區（來源維不重置）。**設定現值**：以 002 設定寫端把 `ip_captcha_after` 改 20 ⇒ 下一次嘗試即不再要求驗證碼；改回 10。**越界**：直改庫 `ip_max_fails=0` ⇒ 下一次嘗試照常數 50 判且 `throttle_degraded_total{source="ip_settings_default"}` 遞增（`curl -s http://127.0.0.1:32079/metrics | grep ip_settings`）；改回 50。

## 5. 管理員解鎖（US5／SC-009）

```bash
curl -s "$BASE/systemManage/unlockLogin" -H "$AUTH" -H 'content-type: application/json' -d "{\"dimension\":\"ip\",\"target\":\"$SIM_A\"}" | jq -r .code
curl -s "$BASE/auth/login" -H 'content-type: application/json' -H "X-Forwarded-For: $SIM_A" -d '{"userName":"ghost1","password":"x"}' | jq -r .msg   # 立即可再試（自由區）
curl -s "$BASE/systemManage/unlockLogin" -H "$AUTH" -H 'content-type: application/json' -d '{"dimension":"user","userName":"NeverLocked"}' | jq -r .code   # Q2：0000 且稽核列多一列
curl -s "$BASE/systemManage/unlockLogin" -H "$AUTH" -H 'content-type: application/json' -d '{"dimension":"ip","target":"not-an-ip"}' | jq -r .msg          # 畸形
$PG sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT operation, entity_table, payload_after FROM sys_operation_log WHERE operation='"'"'unlock'"'"' ORDER BY id DESC LIMIT 3"'
$RD sh -lc 'redis-cli -a "$(cat /run/secrets/redis_password)" --no-auth-warning KEYS "*unlock*"'
```

**預期**：`0000`／自由區／`0000`（未鎖標的照寫稽核與標記）／`biz.throttle.invalidUnlockTarget`（零稽核列）；稽核表恰兩列 `unlock`；redis 只有 `*unlock*` 標記鍵、**無** `*lock:*` 鎖定鍵（L1 已無）。

## 6. 管理頁走查（US3／SC-010；CDP 對照 22080）

- host 瀏覽器 `--remote-debugging-port=9229`；`tools/orchestration/cdp.mjs` `connect()` 後對 32080 分頁先 `send('Network.enable')`、`send('Network.setExtraHTTPHeaders', {headers: {'X-Forwarded-For': SIM_A}})` 使瀏覽器流量成為公網來源（阻擋／403 譯文 toast 驗收需此）；對照分頁 22080（rev5）不帶標頭。
- 流程：Super 登入→側邊欄「IP 規則管理」（標題譯文、非裸鍵）→列表→搜尋（網段片段／類型／刪除狀態）→新增 `203.0.113.7/24`（落庫 `203.0.113.0/24`）→編輯→軟刪→回收桶復原；備註填 `<b>x</b>` 顯純文字；以無 `ipRule:add` 的帳號開頁表頭無新增／批刪入口。
- ★**SC-010 結構清單（逐項全等才綠；截圖差異只記不擋）**：①表格欄位集合與列序 ②搜尋器項目 ③按鈕集合與權限顯隱 ④抽屜欄位與校驗訊息 ⑤分頁 ⑥回收桶流程 ⑦toast 文案（含被擋 403 譯文）。逐項對照 22080 同頁、結果寫入走查紀錄（tmp）。
- 機器守自證：手改 `src/router/elegant/routes.ts` 一行 ⇒ `python3 tools/route-artifact-gate.py check` 紅、還原綠；在 `views/manage/ip-rule/index.vue` 植入 `v-html` ⇒ `python3 tools/view-render-guard.py check` 紅、還原綠。

## 7. 收尾（★必做；RUNBOOK §9c）

```bash
python3 tools/walkthrough-baseline.py restore --seed      # 五表清列（sys_ip_rule 含序列 setval）；rc 0
$RD sh -lc 'redis-cli -a "$(cat /run/secrets/redis_password)" --no-auth-warning PUBLISH ipgate:invalidate 1'   # SQL 直清不按門鈴、手動補按（回 1＝訂閱者在）
curl -s -o /dev/null -w 'A=%{http_code}\n' "$BASE/route/getConstantRoutes" -H "X-Forwarded-For: $SIM_A"           # 判定面已重讀空表 ⇒ 200
python3 tools/walkthrough-baseline.py diff tmp/walkthrough-004.json   # rc 0（runtime-append 四表序列只比存在性）
python3 tools/schema-gate.py check && python3 tools/docsync check && python3 tools/docsync lint
$RD sh -lc 'redis-cli -a "$(cat /run/secrets/redis_password)" --no-auth-warning KEYS "throttle*"'   # 走查後解鎖標記可留（TTL 自然收）、鎖定鍵族 0
```

**預期**：restore rc 0、PUBLISH 回 1、`A=200`、diff rc 0、三閘綠；★三閘綠不等於清乾淨（`rev5:L-071`）——判準是 diff rc 0。走查後跑一次容器內全量測試仍綠（SC-013：殘列不連坐）。
