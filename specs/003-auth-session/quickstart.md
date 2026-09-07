# Quickstart — 003-auth-session 驗證指南

端到端證明「真登入→續期→撤銷→節流／captcha→stub／i18n→dynamic 選單」與治理進場的可跑場景；細節指涉 `contracts/` 三檔與 `data-model.md`、不重複。
全程 rev6 dev stack（埠 3xxxx）；rust build／test 一律容器內 serial；★/mnt/d 下跑過 compose 後同 shell 先重新 `cd`；★auth 端點經 nginx 有 `auth_limit` 5r/s burst 40（429 無信封）、勿於秒內狂打。

## 0. 前置

```bash
bash tools/bootstrap.sh                 # 防線體檢
python3 deploy/preflight-secrets.py
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait
python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-$(date +%Y%m%d).json   # 走查前基準（rc 0）
BASE=http://127.0.0.1:32080/api
```

預期：七件業務件 healthy；`snapshot` rc 0 並印三面摘要（表數／序列數／redis 鍵數）。

## 1. US1 真登入與 dynamic 選單

```bash
LOGIN=$(curl -s -X POST $BASE/auth/login -H 'Content-Type: application/json' -d '{"userName":"Super","password":"<seed 明文>"}')
echo "$LOGIN" | python3 -m json.tool          # code 0000、data.token／data.refreshToken
AT=$(echo "$LOGIN" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["token"])')
RT=$(echo "$LOGIN" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["refreshToken"])')
curl -s $BASE/auth/getUserInfo -H "Authorization: Bearer $AT" | python3 -m json.tool      # userId 字串、userName、roles、buttons
curl -s $BASE/route/getUserRoutes -H "Authorization: Bearer $AT" | python3 -m json.tool   # routes 樹＋home
curl -s $BASE/route/getConstantRoutes | python3 -m json.tool                              # data: []
curl -s -X POST $BASE/auth/login -H 'Content-Type: application/json' -d '{"userName":"Super","password":"wrong"}'   # 1000 auth.login.failed
```

瀏覽器：開 `http://127.0.0.1:32080`，三顆快速登入鈕各登一次，側邊欄呈三種角色化選單；User 帳號 header 顯 `User01`。

## 2. US2 續期

```bash
curl -s -X POST $BASE/auth/refreshToken -H 'Content-Type: application/json' -d "{\"refreshToken\":\"$RT\"}" | python3 -m json.tool   # 0000 新對
curl -s -X POST $BASE/auth/refreshToken -H 'Content-Type: application/json' -d "{\"refreshToken\":\"$RT\"}" | python3 -m json.tool   # 30 秒內：0000 同一對（grace）
sleep 31; curl -s -X POST $BASE/auth/refreshToken -H 'Content-Type: application/json' -d "{\"refreshToken\":\"$RT\"}"                # 8888（reuse、撤家族）
curl -s -X POST $BASE/auth/refreshToken -H 'Content-Type: application/json' -d '{"refreshToken":"garbage"}'                            # 8888（絕不 3333）
```

access 過期→`3333`→前端自動 refresh：瀏覽器登入後等 5 分鐘再點任一頁、觀察 Network 一次 `refreshToken` 後原請求重放成功。

## 3. US3 撤銷／被踢／閒置

§2 末步已撤整條家族（`$AT`／`$RT` 失效），先重新登入取新對：

```bash
LOGIN2=$(curl -s -X POST $BASE/auth/login -H 'Content-Type: application/json' -d '{"userName":"Super","password":"<seed 明文>"}')
AT2=$(echo "$LOGIN2" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["token"])')
RT2=$(echo "$LOGIN2" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["refreshToken"])')
# logout 冪等
curl -s -X POST $BASE/auth/logout -H 'Content-Type: application/json' -d "{\"refreshToken\":\"$RT2\"}"   # 0000
curl -s $BASE/auth/getUserInfo -H "Authorization: Bearer $AT2"                                             # 8888（舊 access 已撤）
curl -s -X POST $BASE/auth/logout -H 'Content-Type: application/json' -d '{"refreshToken":"garbage"}'     # 0000（冪等）
# single-session：再登入取 AT3 後以 R_SUPER 002 寫端翻 on（驗後翻回 off）
LOGIN3=$(curl -s -X POST $BASE/auth/login -H 'Content-Type: application/json' -d '{"userName":"Super","password":"<seed 明文>"}'); AT3=$(echo "$LOGIN3" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["token"])')
curl -s -X POST $BASE/systemManage/updateSystemSetting -H "Authorization: Bearer $AT3" -H 'Content-Type: application/json' -d '{"settingKey":"single_session_default","settingValue":"on"}'
# 同帳號二次登入 → 前一會話下個請求 7777（modal）；翻 on 前既有兩條會話仍皆可用（不追溯）
```

idle：integration 測試以舊 last_activity 值寫入觸發（不注入時鐘）。

## 4. US4 節流三區＋captcha

```bash
for i in 1 2; do curl -s -X POST $BASE/auth/login -H 'Content-Type: application/json' -d '{"userName":"User","password":"wrong"}'; sleep 1; done   # 1000 ×2
curl -s -X POST $BASE/auth/login -H 'Content-Type: application/json' -d '{"userName":"User","password":"wrong"}'   # 2222 biz.auth.captchaRequired（第 3 次起、軟區）
curl -s "$BASE/auth/loginCaptcha?userName=User" | python3 -m json.tool    # captchaId＋data URI；不存在帳號亦發題
# 帶正確 captcha 但錯密碼 → 1000 且該題作廢（前端軟區自動重呼 loginCaptcha 換題並清空輸入＝contracts/wire-auth.md 軟區換題契約；curl 面以再送同一 captchaId 得 captchaRequired 證明已耗）；連續至 ≥5 → 2222 biz.auth.locked（驗章前擋、零列零桶）
PG_USER=soybean; PG_DB=soybean_admin_rust   # 同 tools/schema-gate.py 之 DB_USER／DB_NAME 預設
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres psql -U "$PG_USER" -d "$PG_DB" -Atc "select count(*) from sys_login_attempt where success=false and attempted_user_name='User'"   # 軟區拒絕後再數＝不變
curl -s http://127.0.0.1:32079/metrics | grep -E 'throttle_(degraded|soft_zone)_total|denylist_hit_total'   # 三序列基線 0 已在、命中後遞增
```

## 5. US5 stub 與 i18n

```bash
curl -s -X POST $BASE/auth/register -H 'Content-Type: application/json' -d '{}'   # 2222 biz.auth.notSupported（四支同形）
```

瀏覽器：code-login／register／reset-pwd 三表單送出顯「該功能尚未開放」人話（非假成功）；錯密碼顯人話；切 en-US 顯英文；被踢 modal 顯人話非裸鍵。

## 6. CDP 對照 rev5（世代 DoD B）

host 瀏覽器 `--remote-debugging-port=9229`；`tools/orchestration/cdp.mjs` 開兩分頁 22080（rev5）vs 32080（rev6）：三帳號登入／側邊欄／登出／被踢 modal／軟區 captcha 五面截圖比對零差異（快速登入鈕在、預設 zh-CN）。

## 7. 測試與閘（DoD）

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1   # 容器內 serial；含 contract 16 case、error.rs 八處、facade／handler 真 DB 案（守衛還原）
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T base-web pnpm typecheck
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo build --release -p server   # release profile 首次可跑（dev_identity 汰換的機器證據；再以 release 二進位起服務打 /health 回 ok）
python3 tools/entity-drift-gate.py check    # 零 DDL 仍綠（SC-011）
python3 tools/docsync test                  # hook 接線守衛／GT-12／GT-05 子庫腿新案
python3 tools/fork-delta-lint.py            # 名冊斷言對四軌道生效
python3 tools/msg-key-gate.py check         # 三檔 13 鍵逐檔雙向
python3 tools/wire-schema.py check          # 快照含 rev6-auth.d.ts
python3 tools/docsync check && python3 tools/docsync lint
python3 -c "import re;t=open('docs/generated/reference/routes.md',encoding='utf-8').read();print(len([l for l in t.splitlines() if l.startswith('| /')]))"   # 16
```

## 8. 清理與還原（walkthrough 後；順序固定＝contracts/code-gates.md §3）

```bash
# 翻回 single_session_default=off（002 寫端）→ psql 三表 DELETE＋session_id 置 NULL＋三支 setval(…,1,false) → redis 依 session:/throttle: 前綴 DEL
python3 tools/walkthrough-baseline.py diff tmp/walkthrough-<日期>.json   # rc 0 才算還原
python3 tools/schema-gate.py check                                        # 三閘綠（gate2 逐列）
```

## 9. 治理自證（每項還原後 `git status --porcelain` 零差異——RL-0005）

1. Amendment 後：把 base-web 某修改型標記用途 `(a)`→`(z)` → `python3 tools/fork-delta-lint.py` rc 1 指名 → 還原。
2. 跨端閘：`zh-tw.ts` 刪一鍵 → `msg-key-gate.py check` rc 1 指名檔與鍵 → 還原；`python3 tools/msg-key-gate.py test` 七案綠。
3. 走查工具：`python3 tools/walkthrough-baseline.py test` 綠；`tests/test_gates.py` 之 `NON_GATE_TOOLS` 反例（抽掉→GT-12 紅）。
4. hook 接線：刪 pre-push 一字面／刪 bootstrap 名冊推導行 → `python3 tools/docsync test` 紅指名 → 還原。
5. BL-00041 子庫腿：合成 `rev5 002` 裸形命中列 → GT-05 紅 → 還原。
