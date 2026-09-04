# Quickstart — 002-system-settings 驗證指南

端到端證明「管線七環全通」與「治理進場」的可跑場景；細節指涉 contracts/wire-settings.md、contracts/code-gates.md 與 data-model.md、不重複。
全程 rev6 dev stack（埠 3xxxx）；rust build／test 一律容器內、serial；★/mnt/d 下跑過 compose 後同 shell 先重新 `cd`。

## 0. 前置

```bash
bash tools/bootstrap.sh                 # 防線體檢（舊機＝純體檢）
python3 deploy/preflight-secrets.py     # 機密預檢
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait
docker compose -f docker-compose.yml -f docker-compose.dev.yml ps
```

預期：七件預設業務件（postgres／migrate／redis／rust-api／base-web／front-nginx／mailpit）全 healthy 或 exited 0（migrate）、`up --wait` 零非零退出；`migrate` 完成後 server 常駐。

## 1. 讀端（US1）

```bash
BASE=http://127.0.0.1:32080/api         # 經 front-nginx http 入口（免 -k；https 為 32443）
SUPER="Bearer dev-super"; ADMIN="Bearer dev-admin"   # dev-only 測試態 token（data-model §5；非機密、執行期串接）
curl -s $BASE/systemManage/getSystemSettings -H "Authorization: $SUPER" | python3 -m json.tool
```

預期：`code:"0000"`、data 為 16 元素陣列（settingKey 升冪）、欄形＝data-model §1（description 為 NULL 者該欄缺席）；與 seed 定稿逐鍵全等。

## 2. 授權矩陣（US4）

```bash
curl -s -o /dev/null -w "%{http_code}\n" $BASE/systemManage/getSystemSettings -H "Authorization: $ADMIN"   # 403（信封 5003）
curl -s $BASE/systemManage/getSystemSettings | python3 -m json.tool                                                   # 200、8888、data:null
curl -s $BASE/systemManage/getSystemSettings -H "Authorization: ${SUPER#Bearer }" | python3 -m json.tool          # 去 Bearer 前綴＝非 Bearer 形→8888
```

## 3. 寫端往返（US2／US3／US5）與 fallback（clarify Q4）

```bash
U=$BASE/systemManage/updateSystemSetting; H='-H "Authorization: $SUPER" -H "Content-Type: application/json"'
eval curl -s $U $H -d "'{\"settingKey\":\"password_min_length\",\"settingValue\":\"+10\"}'"          # 0000；回讀落庫 "10"
eval curl -s $U $H -d "'{\"settingKey\":\"password_min_length\",\"settingValue\":\"999\"}'"          # 2222 invalidValue（上界 128）
eval curl -s $U $H -d "'{\"settingKey\":\"single_session_default\",\"settingValue\":\"ON\"}'"         # 2222（大小寫敏感）
eval curl -s $U $H -d "'{\"settingKey\":\"no_such_key\",\"settingValue\":\"1\"}'"                    # 2222 notFound
eval curl -s $U $H -d "'{\"settingKey\":\"password_min_length\",\"settingValue\":\"8\",\"description\":null}'"  # 0000；description 落 NULL
eval curl -s $U $H -d "'{\"settingKey\":\"password_min_length\",\"settingValue\":\"8\",\"description\":\"\"}'"  # 0000；description 落 ""
curl -s -o /dev/null -w "%{http_code}\n" $U -H "Authorization: $SUPER"                     # GET 打 POST 路徑→404（信封 4040）
```

每步後以讀端回讀驗證落庫效果（非法案＝原值保留；成功案回包 `data:null`）。

## 4. 測試與閘（US 全；DoD）

```bash
curl -s http://127.0.0.1:32079/health          # ok（dev 直連埠；nginx /health 為自答塊）
curl -s http://127.0.0.1:32079/metrics | head  # Prometheus exposition（/api/metrics 經 nginx 為擋塊、屬預期）
python3 tools/wire-schema.py extract && python3 tools/wire-schema.py check     # 快照首抽＋drift 閘綠
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1
python3 tools/rust-fmt-gate.py check && python3 tools/fork-delta-lint.py       # 碼面閘綠
python3 tools/docsync check && python3 tools/docsync lint                      # GT-01～GT-12（含 GT-12 新腿、GT-09 routes 成員行）
python3 tools/schema-gate.py check && python3 tools/entity-drift-gate.py check # 零 migration＝現況即基線
```

預期：coverage gate 綠（4/4 case）；msg 名冊雙向斷言綠；entity_behavior_lint 綠；lint 零紅、治理閘 12、生成物名冊 15。

## 5. 治理自證（US6；每項還原後 `git status --porcelain` 零差異——RL-0005）

```bash
# ① 覆蓋閘負向：暫 comment 一 case → cargo test 紅指名 → 還原
# ② hook 面演練：mv docs/ops/reference-src/schema-snapshot.json /tmp/ && git add -A && git commit -m x   # 被 entity-drift 段擋、訊息含 refresh 提示
#    git checkout HEAD -- docs/ops/reference-src/schema-snapshot.json                                   # ★帶 HEAD（LL-00003）
# ③ GT-12 新腿：暫刪 RUNBOOK 碼面閘表一列 → python3 tools/docsync lint 紅指名 → 還原；加幽靈列同形
# ④ fork-delta 哨兵：以 --constitution 指向去掉哨兵句的憲法副本 → rc 2 → 日常不帶旗標
# ⑤ 三支碼面閘 self-test：python3 tools/rust-fmt-gate.py test; python3 tools/wire-schema.py test; python3 tools/fork-delta-lint.py（起手自跑 self-test）
# ⑥ errata 復掃：python3 tools/docsync errata schema-frozen   # 零處仍寫舊觸發面
```
