# Quickstart — 007-user-password-admin（驗證指南）

> 目的＝以 dev stack 端到端證明本刀可用（SC-001～SC-013 之走查面與機器命令；SC-014 屬簿記後驗、本檔只列其假述掃除之命令形）；不含實作碼、不含測試全文。承 006 刀 quickstart 形、rev6 座標。★一律指向 rev6 stack（UI 32080／API 經 front-nginx 32080 之 `/api`／`/metrics` 直連 32079／PG 35432／redis 36379；埠全表＝`docs/generated/reference/ports.md`）、一律 127.0.0.1，絕不指向 rev5 對照 stack（2xxxx）。前置＝ADR-00074 accepted（憲法 1.8.0；收刀前 PATCH 實數化範圍欄後為 1.8.x）且 m0003 已套進 dev 庫（§0）。
> ★執行時點分兩段：①CDP 三方對照單元（research R23 之 U22；實作單元皆已合入、ADR⑧〔ADR-00081〕與 ADR⑨〔ADR-00082〕仍為草稿）＝§0→§10→§11→§14→§6「政策矛盾」段與其告警活體實測（前置＝§3 首塊之 `ADD()`、§6 首塊之 `SET()` 定義）→§13——§10 之刻意分岔判定與 §14 之觀察結果交治理單元定案 ADR⑧⑨ ②收刀前（research R23 之 U23；全部單元合入、容器內全量測試綠、ADR①～⑪⑬～⑮ 皆 accepted）＝§0→§1～§9→§12→§13（§10／§14 於此段可復跑作回歸、不再改 ADR；§6 告警活體實測已於①做、免重做；Day-1 登記三步排在 §13 末段）。
> ★寫入步驟一律對**走查自建**之帳號、角色與選單（帳號名與路由名 `qs_` 起首、角色代碼 `R_QS_` 起首）；seed 三帳號與 seed 角色只做登入與讀端呼叫（FR-058；ADR⑧ 收回 ADR-00068 決定 4① 之 seed 角色例外）。對 seed 列之「預期被拒」案（FR-017 seed 帳號結構保護、FR-042 R_SUPER 六碼受保護撤銷拒）一律由整合測試承擔（守衛＝`data-model.md` §10）、不入走查；例外＝§4 對 Super 之兩發（更新暱稱、踢除）與 §9 對 Super 帳號維解鎖之一發，皆為包含規則負向探針；守門失效之落點（Super 暱稱、Super 會話、`throttle:unlock:user:Super` 標記與稽核列）皆在 §13 restore 射程內。動過 `casbin_rule` 之還原後 MUST 重啟 rust-api（判定面無外部通知管道）。
> ★wire 欄名（請求 `id`／`ids`／`roleIds`／`password`／`sessionPolicy`／`oldPassword`／`newPassword`／`confirmPassword`、回應 `roles`〔項＝`{id, roleCode, roleName}`〕／`revoked`、明細 `violations`／`remainingSeconds`）沿 `rev5:007` 契約形寫入命令；逐欄定義以 `contracts/wire-user-admin.md`／`contracts/wire-user-center.md` 為準、拒因鍵以 `contracts/msg-keys.md` 為準、寫端固定序與 outcome 以 `data-model.md` §3、稽核列以 §7、會話事件與失效名單以 §8 為準，本檔不重述——不符時以 contracts／data-model 為準並同批改本檔。各節依序執行，後節之預期承前節狀態。
> ★dev 庫寫入放行（LL-00053；spec FR-062）：§3～§9 之 API 寫入、§10／§14 之 32080 寫入、§13 之 restore 與 Day-1 照相，各段起手前由主線取 user 放行；被權限分類器拒＝不繞行、列入 user 待辦。psql 一律只下 SELECT；殘列只經寫端 API 產生。

## 0. 前置

```bash
cd <rev6 workspace 根>
dc() { docker compose -f docker-compose.yml -f docker-compose.dev.yml "$@"; }
dc ps                                                   # 實看容器態：rust-api／base-web／front-nginx／postgres／redis 皆在跑；缺者下一行重建
dc up -d --wait
BASE=http://127.0.0.1:32080/api; SM=$BASE/systemManage; UC=$BASE/userCenter
J='content-type: application/json'
QP="Qs#$((2000 + 26))"                                  # 走查自建帳號密碼之共同前綴（RL-0054：合成樣本執行期串接、不落完整字面；各帳號尾段照列）
SQL() { dc exec -T postgres sh -lc "psql -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" -At -c \"$1\""; }
RC() { dc exec -T redis sh -lc "redis-cli -a \"\$(cat /run/secrets/redis_password)\" --no-auth-warning $1"; }
MET() { curl -s http://127.0.0.1:32079/metrics | grep "^$1"; }
RELOAD() { curl -s http://127.0.0.1:32079/metrics | grep '^casbin_reload_total{outcome="ok"}' | awk '{print $2}'; }
SQL "SELECT version FROM seaql_migrations ORDER BY version"
#   m0001_baseline_schema ／ m0002_baseline_seeds ／ m0003_seed_button_governance
#   缺 m0003＝撰寫 m0003 之單元收尾步（取 user 放行）：dc run --rm migrate（RUNBOOK §10 重放形）→ dc restart rust-api（判定面開機載入新值）→ 再跑上行
WB=<走查基準檔路徑（不入版控之工作區）>
python3 tools/walkthrough-baseline.py snapshot "$WB"    # rc 0（RUNBOOK §9c 第 1 步）；檔形 v4（新欄 migrations、sys_user 帶界與可變欄、經手表清理面、cpwd: 前綴＝contracts/code-gates.md §6）
UID_OF() { SQL "SELECT id FROM sys_user WHERE user_name='$1' AND deleted_at IS NULL"; }
RID() { SQL "SELECT id FROM sys_role WHERE role_code='$1' AND deleted_at IS NULL"; }
LOGW() { SQL "SELECT coalesce(max(id),0) FROM sys_operation_log"; }
LOGINJ() { curl -s "$BASE/auth/login" -H "$J" -d "{\"userName\":\"$1\",\"password\":\"$2\"}"; }
tok() { echo "authorization: Bearer $(LOGINJ "$1" "$2" | jq -r .data.token)"; }
SUPER=$(tok Super 123456); ADMIN=$(tok Admin 123456); USER=$(tok User 123456)
```

- ★基準必於 m0003 套進 dev 庫**之後**取（spec FR-057 末句）：006 刀終態基準（檔形 v3）對 v4 工具之 diff／restore 皆 rc 2 指名重新 snapshot；拍於 m0003 套用前之 v4 基準以之 restore＝寫入前比對遷移帳不等、rc 2、零寫入、指名 m0003 並指示重拍（spec FR-057 (a)）。006 刀終態基準於本刀自取基準後才可清。
- snapshot 告警「id 上界高於其序列位置」或基準取樣時清理面各表（本刀起含經手表 `sys_pwd_custody`）或 `session:`／`throttle:`／`cpwd:` 前綴已有殘留＝先 `python3 tools/walkthrough-baseline.py restore --seed`、重啟 rust-api 後重新 snapshot（RUNBOOK §9c 第 1 步；snapshot 一律排在任何登入之前）。
- ★勿秒內狂打 auth 端點（nginx `auth_limit` 5r/s burst 40 回 429）；本檔之連續登入間可插 `sleep 0.3`。CDP 走查排在 schema-gate 驗收之後、或走查後照 RUNBOOK §9c 還原（spec FR-062）。
- seed 三帳號密碼 `123456` 短於政策下限 8＝登入不受影響（登入路徑不驗政策＝FR-032；§6 復核）。

## 1. 路由與授權態（SC-001、FR-001～FR-003／FR-009／FR-061；US3 個人中心之授權面）

```bash
grep -c '^| /' docs/generated/reference/routes.md         # 61
grep -c '| Policy |' docs/generated/reference/routes.md   # 45
grep -c '| Authed |' docs/generated/reference/routes.md   # 5
grep -c '| Public |' docs/generated/reference/routes.md   # 11
grep -o 'ROUTES_COUNT: usize = [0-9]*' rust-api/server/src/router.rs   # ROUTES_COUNT: usize = 61
RQ=$(RELOAD)
for ep in getUserList getDeletedUsers; do
  echo "$ep super=$(curl -s "$SM/$ep" -H "$SUPER" | jq -r .code) admin=$(curl -s "$SM/$ep" -H "$ADMIN" | jq -r .code) user=$(curl -s "$SM/$ep" -H "$USER" | jq -r .code)"
done                                                      # getUserList super=0000 admin=0000 user=5003 ／ getDeletedUsers super=0000 admin=5003 user=5003
for ep in addUser updateUser restoreUser kickUser resetUserPassword updateUserSessionPolicy; do
  echo "$ep super=$(curl -s "$SM/$ep" -H "$SUPER" -H "$J" -d '{}' | jq -r .msg) admin=$(curl -s "$SM/$ep" -H "$ADMIN" -H "$J" -d '{}' | jq -r .code) user=$(curl -s "$SM/$ep" -H "$USER" -H "$J" -d '{}' | jq -r .code)"
done                                                      # addUser super=biz.user.userNameInvalid；其餘五支 super=biz.user.notFound（body 缺欄＝標的 id 預設值不對應現役列）；六行皆 admin=5003 user=5003
for ep in deleteUser batchDeleteUser; do
  echo "$ep super=$(curl -s -X DELETE "$SM/$ep" -H "$SUPER" -H "$J" -d '{}' | jq -r .msg) admin=$(curl -s -X DELETE "$SM/$ep" -H "$ADMIN" -H "$J" -d '{}' | jq -r .code)"
done                                                      # deleteUser super=biz.user.notFound ／ batchDeleteUser super=common.success（ids 缺席＝空陣列提前 no-op）；admin=5003
curl -s "$SM/updateUser" -H "$SUPER" -H "$J" -d 'x' | jq -r .msg       # biz.user.notFound（壞形 body 收斂為預設值、零變更、不新增錯誤碼）
curl -s "$SM/updateUser" -H "$ADMIN" -H "$J" -d 'x' | jq -r .code      # 5003（授權中介層先於 handler、不讀 body）
curl -s -o /dev/null -w '%{http_code}\n' "$SM/addUser" -H "$SUPER"     # 404（GET 打 POST 路由＝動詞不符；信封碼 4040）
for t in "$SUPER" "$ADMIN" "$USER"; do
  echo "$(curl -s "$UC/getPasswordPolicy" -H "$t" | jq -r .code) $(curl -s "$UC/changePassword" -H "$t" -H "$J" -d '{"oldPassword":"a","newPassword":"b","confirmPassword":"c"}' | jq -r .msg)"
done                                                      # 三行皆 0000 biz.user.passwordConfirmMismatch（Authed＝登入即可用；兩次輸入不一致＝首步拒、零寫入、不計改密節流）
curl -s "$UC/getPasswordPolicy" | jq -r .code             # 8888（未帶票）
[ "$(RELOAD)" = "$RQ" ] && echo no-sync                   # no-sync
```

**預期**：Super 對 12 支皆過授權層、Admin 對管理面除 getUserList 外 9 支皆 `5003`、User 對管理面 10 支皆 `5003`、個人中心 2 支三帳號皆過；addUser 之首個拒因依 `data-model.md` §3 固定序。contract 61 case、覆蓋閘雙向、授權態矩陣全量（含兩支「列 68 候選外」前提測試改植探針列）＝§12 全量測試。

## 2. 讀端（US1 AS9、FR-005／FR-007／FR-008／FR-020）

本段只讀；預期以 seed 態寫成（dev 庫若有自建帳號殘列，`total` 與 `ids` 隨之、序不變）。

```bash
L() { curl -s "$SM/getUserList?$1" -H "$SUPER"; }
L "" | jq -c '.data|{current,size,total,ids:[.records[].id]}'          # {"current":1,"size":10,"total":3,"ids":[1,2,3]}（現役依 id 升冪、伺服端固定序、不收排序參數）
L "" | jq -c '.data.records[]|select(.id==1)|{roles,createdBy,ca:(.createdAt|test("\\+00:00$"))}'
                                                                       # {"roles":[{"id":1,"roleCode":"R_SUPER","roleName":"超級管理員"}],"createdBy":null,"ca":true}
L "" | jq -c '.data.records[0]|keys'                                   # 欄集＝contracts/wire-user-admin.md 共用型之 UserRecord（逐欄白名單）
L "" | grep -c -e argon2 -e '"password"' -e sessionId                  # 0（密碼雜湊與當前會話 id 不上 wire）
L "userName=dmi" | jq -c '[.data.records[].userName]'                  # ["Admin"]（部分字串）
L "nickName=User0" | jq -c '[.data.records[].userName]'                # ["User"]
L "status=2" | jq '.data.total'                                        # 0
for ep in getUserList getDeletedUsers; do
  echo "$ep $(curl -s "$SM/$ep" -H "$SUPER" | jq -c '.data|{current,size}') \
 $(curl -s "$SM/$ep?current=99999999&size=10" -H "$SUPER" | jq -c '.data|{current,n:(.records|length)}') \
 $(curl -s "$SM/$ep?size=0&current=0" -H "$SUPER" | jq -c '.data|{current,size}') \
 $(curl -s "$SM/$ep?size=abc" -H "$SUPER" | jq -c '.data|{current,size}') \
 $(curl -s "$SM/$ep?size=1000" -H "$SUPER" | jq -c '.data|{current,size}')"
done                                                                   # 兩行皆 {1,10}／{10000000,0}／{1,1}／{1,10}／{1,100}（005 刀分頁通則同式）
curl -s "$SM/getDeletedUsers" -H "$SUPER" | jq -c '.data|{total,records}'   # {"total":0,"records":[]}（本段前無刪除）
```

**預期**：清單列帶持有角色之 id、代碼與名稱（停用角色亦列；抽屜灰色保留見 §10）；建立者與更新者以帳號名回填；手機、信箱兩欄過濾於 §3 復核。清單 wire 偏離帳（FR-008、ADR⑩）＝wire 裁判機器導出、§12 承擔。

## 3. 使用者寫端（US1 AS1～AS9、SC-003、FR-010～FR-016、FR-019、FR-061）

新增（AS1）：

```bash
R0=$(RELOAD)
curl -s "$SM/addRole" -H "$SUPER" -H "$J" -d '{"roleCode":"R_QS_U","roleName":"使用者走查"}' | jq -r .code   # 0000
RU=$(RID R_QS_U); LOG0=$(LOGW)
ADD() { curl -s "$SM/addUser" -H "$SUPER" -H "$J" -d "$1"; }
ADD "{\"userName\":\"qs_alice\",\"password\":\"${QP}alice\",\"nickName\":\"Alice\",\"userGender\":\"1\",\"userPhone\":\"0912345678\",\"userEmail\":\"qs.alice@example.test\",\"roleIds\":[$RU],\"userMemo\":\"<b>純文字記事</b>\"}" | jq -r .code   # 0000
AL=$(UID_OF qs_alice)
SQL "SELECT status, session_policy, left(password, 9), created_by FROM sys_user WHERE id = $AL"   # 1|inherit|$argon2id|1（狀態預設啟用）
SQL "SELECT operation, entity_table, entity_id = $AL FROM sys_operation_log WHERE id > $LOG0"    # add|sys_user|t（恰一列、同交易）
SQL "SELECT count(*) FROM sys_operation_log WHERE id > $LOG0 AND (coalesce(payload_after::text,'') LIKE '%${QP}%' OR coalesce(payload_after::text,'') LIKE '%argon2%')"   # 0
SQL "SELECT count(*) FROM sys_pwd_custody WHERE user_id = $AL AND created_by = 1"                # 1（初始密碼同計入冷卻）
L "userName=qs_alice" | jq -c '.data.records[0]|{status,sessionPolicy,userMemo,createdBy,roles:[.roles[].roleCode]}'
                                                                       # {"status":"1","sessionPolicy":"inherit","userMemo":"<b>純文字記事</b>","createdBy":"Super","roles":["R_QS_U"]}
L "userPhone=2345" | jq -c '[.data.records[].userName]'                # ["qs_alice"]（部分字串；FR-007 六欄過濾）
L "userEmail=alice@example" | jq -c '[.data.records[].userName]'       # ["qs_alice"]
ADD '{"userName":"qs_alice","password":"'"$QP"'alice"}' | jq -c '{code,msg,data}'   # {"code":"2222","msg":"biz.user.userNameExists","data":null}
ADD '{"userName":"qs_alice2","password":"'"$QP"'alice","userEmail":"QS.Alice@Example.TEST"}' | jq -r .msg   # biz.user.userEmailExists（不分大小寫、只比現役列）
ADD '{"userName":"qs alice","password":"'"$QP"'alice"}' | jq -r .msg                          # biz.user.userNameInvalid（形制 ^[A-Za-z0-9_-]{1,64}$）
ADD '{"userName":"qs_alice2","password":"'"$QP"'alice","userEmail":"not-an-email"}' | jq -r .msg   # biz.user.userEmailInvalid
ADD '{"userName":"qs_alice2","password":"'"$QP"'alice","roleIds":[999999999]}' | jq -r .msg   # biz.user.roleNotFound（整筆拒、非靜默略過）
A1=$(tok qs_alice "${QP}alice"); curl -s "$BASE/auth/getUserInfo" -H "$A1" | jq -c '.data.roles'   # ["R_QS_U"]
```

編輯：帳號名不可變、缺席早退＋值 diff、空字串清空、角色集全量替換（AS2／AS3；ADR⑦）：

```bash
U() { curl -s "$SM/updateUser" -H "$SUPER" -H "$J" -d "$1"; }
U "{\"id\":$AL,\"userName\":\"qs_alice9\",\"nickName\":\"A2\"}" | jq -r .msg   # biz.user.userNameImmutable（出現即拒、零寫入）
T0=$(SQL "SELECT updated_at FROM sys_user WHERE id = $AL"); LOG1=$(LOGW)
U "{\"id\":$AL}" | jq -r .code                                          # 0000（全缺席早退）
U "{\"id\":$AL,\"nickName\":\"Alice\",\"roleIds\":[$RU,$RU]}" | jq -r .code   # 0000（同值）
[ "$(SQL "SELECT updated_at FROM sys_user WHERE id = $AL")" = "$T0" ] && echo ts-unchanged   # ts-unchanged
SQL "SELECT count(*) FROM sys_operation_log WHERE id > $LOG1"           # 0（同值零寫入、零稽核）
U "{\"id\":$AL,\"nickName\":\"Alice2\"}" | jq -r .code                  # 0000
SQL "SELECT operation, entity_id = $AL FROM sys_operation_log WHERE id > $LOG1"   # update|t（一列）
U "{\"id\":$AL,\"userEmail\":\"\",\"userMemo\":\"\",\"nickName\":null}" | jq -r .code   # 0000
SQL "SELECT user_email IS NULL, user_memo IS NULL, nick_name IS NULL FROM sys_user WHERE id = $AL"   # t|t|t（空字串＝清空、null＝清空）
U "{\"id\":$AL,\"roleIds\":[999999999]}" | jq -r .msg                   # biz.user.roleNotFound（整筆拒）
U "{\"id\":$AL,\"roleIds\":[]}" | jq -r .code                           # 0000（空陣列＝全撤）
SQL "SELECT count(*) FROM sys_user_role WHERE user_id = $AL"            # 0
U "{\"id\":$AL,\"roleIds\":[$RU]}" | jq -r .code                        # 0000（寫後角色集恰等於陣列）
U "{\"id\":$AL,\"nickName\":\"Alice\"}" | jq -r .code                   # 0000（角色欄缺席＝指派不動）
SQL "SELECT string_agg(role_id::text, ',') FROM sys_user_role WHERE user_id = $AL"   # 與 $RU 同值
```

刪除、回收桶與復原（AS5／AS7／AS8；FR-014～FR-016）：

```bash
A2=$(tok qs_alice "${QP}alice")
EV0=$(SQL "SELECT coalesce(max(id),0) FROM session_event"); LOG2=$(LOGW)
curl -s -X DELETE "$SM/deleteUser" -H "$SUPER" -H "$J" -d "{\"id\":$AL}" | jq -r .code   # 0000
SQL "SELECT deleted_at IS NOT NULL, deleted_by FROM sys_user WHERE id = $AL"            # t|1（成對軟刪欄）
SQL "SELECT count(*) FROM sys_user_role WHERE user_id = $AL"                            # 0（指派硬刪）
SQL "SELECT count(*) FROM sys_token WHERE created_by = $AL AND status = 'active'"       # 0
SQL "SELECT event_type, reason, count(*) FROM session_event WHERE id > $EV0 GROUP BY 1,2"   # revoked|user_deleted|2
SQL "SELECT operation FROM sys_operation_log WHERE id > $LOG2"                          # delete
curl -s "$BASE/auth/getUserInfo" -H "$A1" | jq -c '{code,msg}'                          # {"code":"8888","msg":"auth.session.reLogin"}
LOGINJ qs_alice "${QP}alice" | jq -c '{code,msg}'                                     # {"code":"1000","msg":"auth.login.failed"}（與帳密錯誤無差別）
curl -s "$SM/updateUser" -H "$SUPER" -H "$J" -d "{\"id\":$AL,\"nickName\":\"x\"}" | jq -r .msg              # biz.user.notFound
curl -s "$SM/kickUser" -H "$SUPER" -H "$J" -d "{\"id\":$AL}" | jq -r .msg                                    # biz.user.notFound
curl -s "$SM/resetUserPassword" -H "$SUPER" -H "$J" -d "{\"id\":$AL,\"password\":\"${QP}alicex\"}" | jq -r .msg   # biz.user.notFound
curl -s "$SM/updateUserSessionPolicy" -H "$SUPER" -H "$J" -d "{\"id\":$AL,\"sessionPolicy\":\"multi\"}" | jq -r .msg   # biz.user.notFound
curl -s -X DELETE "$SM/deleteUser" -H "$SUPER" -H "$J" -d "{\"id\":$AL}" | jq -r .msg                        # biz.user.notFound（只有復原認得已刪列）
curl -s "$SM/getDeletedUsers" -H "$SUPER" | jq -c ".data.records[]|select(.id == $AL)|{userName,roles}"     # {"userName":"qs_alice","roles":[]}
LOG3=$(LOGW)
curl -s "$SM/restoreUser" -H "$SUPER" -H "$J" -d "{\"id\":$AL}" | jq -r .code          # 0000
SQL "SELECT deleted_at IS NULL, deleted_by IS NULL, status FROM sys_user WHERE id = $AL"   # t|t|1
SQL "SELECT count(*) FROM sys_user_role WHERE user_id = $AL"                           # 0（零回灌）
SQL "SELECT operation FROM sys_operation_log WHERE id > $LOG3"                         # restore
A1=$(tok qs_alice "${QP}alice"); curl -s "$BASE/auth/getUserInfo" -H "$A1" | jq -c '.data.roles'   # []（原密碼可登入、零角色）
```

批刪與復原撞名、撞信箱（AS6／AS7）：

```bash
ADD "{\"userName\":\"qs_bob\",\"password\":\"${QP}bob1\",\"roleIds\":[$RU]}" | jq -r .code   # 0000
ADD '{"userName":"qs_carol","password":"'"$QP"'carol","userEmail":"qs.carol@example.test","status":"2"}' | jq -r .code   # 0000（停用中）
BO=$(UID_OF qs_bob); CA=$(UID_OF qs_carol)
curl -s -X DELETE "$SM/batchDeleteUser" -H "$SUPER" -H "$J" -d '{"ids":[]}' | jq -r .code              # 0000（空陣列提前 no-op）
curl -s -X DELETE "$SM/batchDeleteUser" -H "$SUPER" -H "$J" -d "{\"ids\":[$CA,$BO,$BO]}" | jq -r .code  # 0000（去重、id 升序取鎖；稽核兩列 delete）
curl -s "$SM/getDeletedUsers" -H "$SUPER" | jq -c '[.data.records[].userName][0:2]'                   # ["qs_carol","qs_bob"]（刪除時間降冪再 id 降冪）
ADD '{"userName":"qs_bob","password":"'"$QP"'bob2"}' | jq -r .code                                     # 0000（已刪列不占現役唯一）
ADD '{"userName":"qs_carol2","password":"'"$QP"'carol","userEmail":"QS.CAROL@example.test"}' | jq -r .code   # 0000
NB=$(UID_OF qs_bob); C2=$(UID_OF qs_carol2)
curl -s "$SM/restoreUser" -H "$SUPER" -H "$J" -d "{\"id\":$BO}" | jq -r .msg       # biz.user.userNameExists（鎖內重驗）
curl -s "$SM/restoreUser" -H "$SUPER" -H "$J" -d "{\"id\":$CA}" | jq -r .msg       # biz.user.userEmailExists
curl -s -X DELETE "$SM/batchDeleteUser" -H "$SUPER" -H "$J" -d "{\"ids\":[$NB,999999999]}" | jq -r .msg   # biz.user.notFound（不指筆）
SQL "SELECT count(*) FROM sys_user WHERE id = $NB AND deleted_at IS NULL"          # 1（整批 rollback、零變更）
curl -s -X DELETE "$SM/batchDeleteUser" -H "$SUPER" -H "$J" -d "{\"ids\":[$NB,$C2]}" | jq -r .code   # 0000
curl -s "$SM/restoreUser" -H "$SUPER" -H "$J" -d "{\"id\":$BO}" | jq -r .code      # 0000
curl -s "$SM/restoreUser" -H "$SUPER" -H "$J" -d "{\"id\":$CA}" | jq -r .code      # 0000
SQL "SELECT id = $CA, status FROM sys_user WHERE id IN ($BO,$CA) ORDER BY id"      # f|1 ／ t|2（狀態保留刪除前原值）
SQL "SELECT count(*) FROM sys_user_role WHERE user_id = $BO"                       # 0
[ "$(RELOAD)" = "$R0" ] && echo no-sync                                            # no-sync（使用者域寫端零授權重載、含指派變更＝FR-061；新增角色亦 0）
```

- seed 帳號結構保護與 FR-010 表之逐格（拒格負向、空格以案釘理由）＝整合測試面（SC-003）；本人五不之走查面＝§4。
- 請求上下文缺席之 `5000`、稽核 `real_ip` 缺席拒寫、新增帳號同名並發由現役唯一索引兜底、同一標的兩寫端於 per-user advisory 序列化與鎖序（FR-006／FR-011；research R7）＝整合測試面。

## 4. 包含規則（US4 AS1～AS8、SC-004、FR-021～FR-025）

委派角色與帳號（委派下放之載體＝006 刀三維寫端；端點清單以 JSON 變數承載、全量替換每次重送）：

```bash
curl -s "$SM/addRole" -H "$SUPER" -H "$J" -d '{"roleCode":"R_QS_DEL","roleName":"委派走查"}' | jq -r .code   # 0000
curl -s "$SM/addRole" -H "$SUPER" -H "$J" -d '{"roleCode":"R_QS_OFF","roleName":"停用走查"}' | jq -r .code   # 0000
RD=$(RID R_QS_DEL); RO=$(RID R_QS_OFF)
E() { printf '{"path":"/systemManage/%s","method":"%s"}' "$1" "$2"; }
EP_DEL="[$(E getUserList GET),$(E getDeletedUsers GET),$(E getAllRoles GET),$(E updateUser POST),$(E deleteUser DELETE),$(E batchDeleteUser DELETE),$(E restoreUser POST),$(E kickUser POST),$(E resetUserPassword POST),$(E unlockLogin POST),$(E getRoleList GET),$(E updateRole POST),$(E getMenuList/v2 GET),$(E getMenuTree GET),$(E getAllPages GET)]"
curl -s "$SM/updateRoleMenu" -H "$SUPER" -H "$J" -d "{\"id\":$RD,\"menuIds\":[3,4,5]}" | jq -c '.data|{revoked,granted}'   # {"revoked":0,"granted":3}（使用者、角色、選單三頁可見性）
curl -s "$SM/updateRoleButton" -H "$SUPER" -H "$J" -d "{\"id\":$RD,\"buttons\":[\"user:add\",\"user:edit\",\"user:kick\",\"user:reset-pwd\",\"user:unlock\",\"user:restore\",\"role:edit\",\"menu:add\"]}" | jq -c '.data|{revoked,granted}'   # {"revoked":0,"granted":8}
curl -s "$SM/updateRoleEndpoints" -H "$SUPER" -H "$J" -d "{\"id\":$RD,\"endpoints\":$EP_DEL}" | jq -c '.data|{revoked,granted}'   # {"revoked":0,"granted":15}
curl -s "$SM/updateRoleEndpoints" -H "$SUPER" -H "$J" -d "{\"id\":$RD,\"endpoints\":$(echo "$EP_DEL" | jq -c ". + [$(E updateUserSessionPolicy POST)]")}" | jq -c '{code,msg}'
                                                                       # {"code":"2222","msg":"biz.role.protectedGrant"}（列 68 受保護＝封死集；整批拒、零變更＝AS6）
ADD "{\"userName\":\"qs_dora\",\"password\":\"${QP}dora\",\"roleIds\":[$RD]}" | jq -r .code   # 0000（被授權之非超管）
ADD "{\"userName\":\"qs_erin\",\"password\":\"${QP}erin\",\"roleIds\":[$RD]}" | jq -r .code   # 0000（同級標的）
ADD "{\"userName\":\"qs_fay\",\"password\":\"${QP}fay1\",\"roleIds\":[$RU]}" | jq -r .code    # 0000（持操作者未持之角色）
DO=$(UID_OF qs_dora); ER=$(UID_OF qs_erin); FA=$(UID_OF qs_fay)
DORA=$(tok qs_dora "${QP}dora")
DU() { curl -s "$SM/$1" -H "$DORA" -H "$J" -d "$2" | jq -r '.code + " " + .msg'; }
DUD() { curl -s -X DELETE "$SM/$1" -H "$DORA" -H "$J" -d "$2" | jq -r '.code + " " + .msg'; }
```

判定（T⊆A∧N⊆A；持 R_SUPER 者 A＝全集）：

```bash
LOG4=$(LOGW)
DU updateUser "{\"id\":$ER,\"nickName\":\"Erin\"}"                    # 0000 common.success（同級互管＝AS4）
SQL "SELECT created_by = $DO FROM sys_operation_log WHERE id > $LOG4"  # t（稽核記操作者本人）
LOG5=$(LOGW)
DU updateUser '{"id":1,"nickName":"x"}'                                # 5003 system.forbidden（T＝{R_SUPER} ⊄ A；純 key、不洩差集）
DU kickUser '{"id":1}'                                                 # 5003 system.forbidden
DU updateUser "{\"id\":$ER,\"roleIds\":[$RD,1]}"                       # 5003 system.forbidden（N ⊄ A）
DU updateUser "{\"id\":$ER,\"roleIds\":[$RD,$RU]}"                     # 5003 system.forbidden（操作者不持 R_QS_U）
DU updateUser "{\"id\":$FA,\"nickName\":\"x\"}"                        # 5003 system.forbidden
SQL "SELECT count(*) FROM sys_operation_log WHERE id > $LOG5"          # 0（零變更、零稽核）
SQL "SELECT nick_name FROM sys_user WHERE id = 1"                      # Super（任一探針非 5003＝守門失效：停手、§13 restore）
U "{\"id\":$DO,\"roleIds\":[$RD,$RU]}" | jq -r .code                   # 0000（Super 只持 R_SUPER 而指派其未持之兩角色＝A＝全集之非 vacuous 正向案＝AS2）
DU updateUser "{\"id\":$FA,\"nickName\":\"Fay\"}"                      # 0000 common.success
DU updateUser "{\"id\":$ER,\"roleIds\":[$RD,$RU]}"                     # 0000 common.success
dc logs --since 5m rust-api | grep -i warn | tail -n 5                 # 每發 5003 各一則 warn（操作者 id、標的 id、端點三欄；不含角色差集；目標名＝research R9）；不新增觀測序列
```

本人五不（固定序第③步先於包含規則；Edge Cases「本人五不」、FR-017）：

```bash
DU updateUser "{\"id\":$DO,\"status\":\"2\"}"                          # 2222 biz.user.cannotEditSelfRoleOrStatus
DU updateUser "{\"id\":$DO,\"roleIds\":[$RD,$RU]}"                     # 2222 biz.user.cannotEditSelfRoleOrStatus（出現即拒、同值亦拒）
DU kickUser "{\"id\":$DO}"                                             # 2222 biz.user.cannotKickSelf
DU resetUserPassword "{\"id\":$DO,\"password\":\"${QP}dora2\"}"      # 2222 biz.user.cannotResetSelfPassword
DUD deleteUser "{\"id\":$DO}"                                          # 2222 biz.user.cannotDeleteSelf
DUD batchDeleteUser "{\"ids\":[$ER,$DO]}"                              # 2222 biz.user.cannotDeleteSelf（整批拒）
SQL "SELECT count(*) FROM sys_user WHERE id = $ER AND deleted_at IS NULL"   # 1
DU updateUser "{\"id\":$DO,\"nickName\":\"Dora\"}"                     # 0000 common.success（本人可改非角色欄）
```

停用角色計入 T、不計入 A（AS3）；前超管復原（AS5）；碼與端點各自獨立之 API 面（AS7）：

```bash
U "{\"id\":$ER,\"roleIds\":[$RD,$RO]}" | jq -r .code                   # 0000
curl -s "$SM/updateRole" -H "$SUPER" -H "$J" -d "{\"id\":$RO,\"status\":\"2\"}" | jq -r .code   # 0000（停用 R_QS_OFF；指派列不硬刪）
DU updateUser "{\"id\":$ER,\"nickName\":\"x\"}"                        # 5003 system.forbidden（標的所持停用角色仍計入 T）
U "{\"id\":$DO,\"roleIds\":[$RD,$RU,$RO]}" | jq -r .code               # 0000（指派停用中角色：存在且未刪即可）
DU updateUser "{\"id\":$ER,\"nickName\":\"x\"}"                        # 5003 system.forbidden（操作者所持停用角色不計入 A）
ADD '{"userName":"qs_exsup","password":"'"$QP"'exsup","roleIds":[1]}' | jq -r .code   # 0000（自建帳號持 R_SUPER）
EX=$(UID_OF qs_exsup)
curl -s -X DELETE "$SM/deleteUser" -H "$SUPER" -H "$J" -d "{\"id\":$EX}" | jq -r .code   # 0000（指派隨軟刪硬刪＝T＝∅）
DU restoreUser "{\"id\":$EX}"                                          # 0000 common.success（被授復原者可復原前超管）
SQL "SELECT count(*) FROM sys_user_role WHERE user_id = $EX"           # 0（復原後零角色；要回超管須持 R_SUPER 者指派）
DU addUser '{"userName":"qs_gil","password":"'"$QP"'gil1"}'            # 5003 system.forbidden（碼 user:add 有、端點未授）
DUD deleteUser "{\"id\":$FA}"                                          # 0000 common.success（端點有、碼 user:delete 無＝鈕不見而 API 可達）
```

- 每消費點「兩負一正＋停用角色一案」全量、拆判定呼叫即紅、判定位次不與撤銷拒及封死拒互吞、`NO_ESCALATION_CALL_FILES` 名冊閘、指派寫端與 deleteRole 併發之角色列鎖內重判＝整合測試與名冊閘面（FR-011／FR-022／FR-025）。unlockLogin 帳號維＝§9；前端不預判＝§10。

## 5. 斷權（US2 AS1～AS6、SC-005、FR-026～FR-029／FR-031；島 B／C 用語之畫面面＝§11）

管理員踢除（AS1）：

```bash
TK0=$(SQL "SELECT coalesce(max(id),0) FROM sys_token")
P=$(LOGINJ qs_alice "${QP}alice"); A1="authorization: Bearer $(jq -r .data.token <<<"$P")"; RT1=$(jq -r .data.refreshToken <<<"$P")
sleep 0.3; A2=$(tok qs_alice "${QP}alice")
N=$(curl -s "$BASE/auth/refreshToken" -H "$J" -d "{\"refreshToken\":\"$RT1\"}"); A1="authorization: Bearer $(jq -r .data.token <<<"$N")"; RT1=$(jq -r .data.refreshToken <<<"$N")
SQL "SELECT status, count(*) FROM sys_token WHERE created_by = $AL AND id > $TK0 GROUP BY 1 ORDER BY 1"   # active|2 ／ rotated|1
EV1=$(SQL "SELECT coalesce(max(id),0) FROM session_event"); LOG6=$(LOGW)
curl -s "$SM/kickUser" -H "$SUPER" -H "$J" -d "{\"id\":$AL}" | jq -c .data      # {"revoked":3}（本段兩條＋§3 復原後之一條；數＝執行當下有效會話數）
SQL "SELECT status, count(*) FROM sys_token WHERE created_by = $AL AND id > $TK0 GROUP BY 1 ORDER BY 1"   # revoked|2 ／ rotated|1（已輪替列不動、重放走既有重用偵測）
SQL "SELECT event_type, reason, count(*) FROM session_event WHERE id > $EV1 GROUP BY 1,2"   # revoked|admin_kick|3
for s in $(SQL "SELECT sid FROM session_event WHERE id > $EV1"); do RC "GET session:denylist:$s"; done   # 三行 admin_kick（失效名單原因；commit 後盡力寫入）
SQL "SELECT operation FROM sys_operation_log WHERE id > $LOG6"                  # kick
curl -s "$BASE/auth/getUserInfo" -H "$A1" | jq -c '{code,msg}'                 # {"code":"7777","msg":"auth.session.kickedByAdmin"}
curl -s "$BASE/auth/getUserInfo" -H "$A2" | jq -c '{code,msg}'                 # 同上（全部裝置）
curl -s "$BASE/auth/refreshToken" -H "$J" -d "{\"refreshToken\":\"$RT1\"}" | jq -c '{code,msg}'   # {"code":"7777","msg":"auth.session.kickedByAdmin"}（換發三向分派）
A1=$(tok qs_alice "${QP}alice"); curl -s "$BASE/auth/getUserInfo" -H "$A1" | jq -r .code   # 0000（可立即重登）
```

停用（AS2）、停用中可踢（AS4）、會話政策（FR-018）與頂替文案分立（GR2）：

```bash
P=$(LOGINJ qs_alice "${QP}alice"); A1="authorization: Bearer $(jq -r .data.token <<<"$P")"; RT1=$(jq -r .data.refreshToken <<<"$P")
EV2=$(SQL "SELECT coalesce(max(id),0) FROM session_event")
U "{\"id\":$AL,\"status\":\"2\"}" | jq -r .code                                # 0000
SQL "SELECT event_type, reason, count(*) FROM session_event WHERE id > $EV2 GROUP BY 1,2"   # revoked|user_disabled|2（含上段重登之會話）
curl -s "$BASE/auth/getUserInfo" -H "$A1" | jq -c '{code,msg}'                 # {"code":"8888","msg":"auth.session.reLogin"}（靜默）
curl -s "$BASE/auth/refreshToken" -H "$J" -d "{\"refreshToken\":\"$RT1\"}" | jq -r .code   # 8888
LOGINJ qs_alice "${QP}alice" | jq -c '{code,msg}'                            # {"code":"1000","msg":"auth.login.failed"}
curl -s "$SM/kickUser" -H "$SUPER" -H "$J" -d "{\"id\":$AL}" | jq -c '{code,data}'   # {"code":"0000","data":{"revoked":0}}（停用中可踢、清乾淨殘留會話）
U "{\"id\":$AL,\"status\":\"1\"}" | jq -r .code                                # 0000
A1=$(tok qs_alice "${QP}alice")
SP() { curl -s "$SM/updateUserSessionPolicy" -H "$SUPER" -H "$J" -d "{\"id\":$AL,\"sessionPolicy\":\"$1\"}" | jq -r .msg; }
SP bogus                                                                       # biz.user.sessionPolicyInvalid
SP single                                                                      # common.success
curl -s "$BASE/auth/getUserInfo" -H "$A1" | jq -r .code                        # 0000（改 single 不即時踢除）
LOG7=$(LOGW); SP single; SQL "SELECT count(*) FROM sys_operation_log WHERE id > $LOG7"   # common.success ／ 0（同值 no-op）
sleep 0.3; A3=$(tok qs_alice "${QP}alice")
curl -s "$BASE/auth/getUserInfo" -H "$A1" | jq -c '{code,msg}'                 # {"code":"7777","msg":"auth.session.kicked"}（單一會話頂替；文案與管理員踢除分立、原因值不改）
SP inherit                                                                     # common.success
```

- 重設與自助改密之斷權＝§6；刪除之斷權＝§3；本人踢除拒＝§4。
- 換發鎖內活性重驗三形（停用、軟刪、列不存在）：走查之停用與刪除皆同交易撤票、換發先被已撤銷腿擋下（上列 8888 屬之）——「票仍有效而帳號不活」須直改庫才構造得出＝整合測試面（SC-005）；失效名單寫入失敗注入、不新增每請求活性判定（FR-029）、不新增存取軌跡寫入面（FR-031）同屬整合測試面。

## 6. 密碼面（US3 AS1～AS7／AS9、SC-006、FR-032～FR-038）

```bash
SET() { curl -s "$SM/updateSystemSetting" -H "$SUPER" -H "$J" -d "{\"settingKey\":\"$1\",\"settingValue\":\"$2\"}" | jq -r .code; }
curl -s "$UC/getPasswordPolicy" -H "$USER" | jq -c '.data|keys'     # ["forbidUsername","maxLength","minLength","requireDigit","requireLowercase","requireSpecial","requireUppercase"]（七鍵、無冷卻秒數）
SET password_min_length 12                                           # 0000
curl -s "$UC/getPasswordPolicy" -H "$USER" | jq '.data.minLength'    # 12（消費當下讀現值、不快取）
ADD '{"userName":"qs_gus","password":"'"$QP"'abcd"}' | jq -c '{code,msg,data}'   # {"code":"2222","msg":"biz.user.passwordPolicy","data":{"violations":["minLength"]}}
SET password_require_digit on; SET password_require_uppercase on
ADD '{"userName":"qs_gus","password":"abcdefgh"}' | jq -c '.data.violations|sort'   # ["minLength","requireDigit","requireUppercase"]（一次收集全部）
SET password_require_uppercase off; SET password_require_digit off; SET password_min_length 8
SET password_forbid_username on
ADD '{"userName":"qs_frank1","password":"QS_FRANK1"}' | jq -c '.data.violations'   # ["forbidUsername"]（不分大小寫相等）
ADD '{"userName":"qs_frank1","password":"xqs_frank1y"}' | jq -r .code              # 0000（只含帳號名之子串不算違規）
SET password_forbid_username off
SET password_max_length 256
PW=$(python3 -c "print('密'*171)")                                   # 171 字、513 bytes
ADD "{\"userName\":\"qs_gus\",\"password\":\"$PW\"}" | jq -c '.data.violations'    # ["maxBytes"]（字元數＋位元組數雙約束；上界引登入密碼位元組上界常數 512）
SET password_max_length 64
```

政策矛盾（AS3；ADR⑥）：

```bash
I0=$(MET password_policy_invalid_total | awk '{print $2}')          # 開機預註冊 0 起算
SET password_min_length 20; SET password_max_length 10               # 0000 ／ 0000（設定寫端不守組合）
ADD '{"userName":"qs_gus","password":"'"$QP"'abcdefghijklmn"}' | jq -c '{code,msg}'   # {"code":"2222","msg":"biz.user.passwordPolicy"}（任一入口設密一律拒）
echo $(( $(MET password_policy_invalid_total | awk '{print $2}') - I0 ))   # 1（發射出口恰一處＝政策載入判最小＞最大）
dc logs --since 2m rust-api | grep -i warn | tail -n 3                # 設定異常 warn 一則（含最小與最大長度現值、不含任何密碼字面；目標名與欄位＝research R11）
LOGINJ Super 123456 | jq -r .code                                    # 0000（登入不受影響）
SET password_max_length 64; SET password_min_length 8
```

- 告警規則 `password-policy-invalid`（`deploy/grafana-provisioning/alerting/rules.yml`；5 分鐘增量 >0）活體實測（U22 執行＝`contracts/code-gates.md` §7.3；dev 庫寫入逐步取 user 放行）：`dc --profile metrics up -d --wait` 後重做上段觸發 → `curl -s 'http://127.0.0.1:39090/api/v1/query?query=sum(increase(password_policy_invalid_total%5B5m%5D))' | jq -r '.data.result[0].value[1]'` >0（方括號須編碼：curl 把字面 `[…]` 當網址展開、報 rc 3） → Grafana（33000）告警清單該規則轉 Firing；不入 `throttle_degraded_total`（`contracts/code-gates.md` §7）。

設密冷卻（AS5；維度＝標的×操作者）與管理員重設之斷權（US2 AS3）：

```bash
ADD '{"userName":"qs_grace","password":"'"$QP"'grace"}' | jq -r .code   # 0000（經手表寫入 (標的, Super)）
GR=$(UID_OF qs_grace)
RS() { curl -s "$SM/resetUserPassword" -H "$1" -H "$J" -d "{\"id\":$GR,\"password\":\"$2\"}"; }
RS "$SUPER" short1 | jq -c '{code,msg}'                              # {"code":"2222","msg":"biz.user.passwordPolicy"}（政策先於冷卻；三入口共用驗證點）
RS "$SUPER" "${QP}grace2" | jq -c '{code,msg,data}'                # {"code":"2222","msg":"biz.user.pwdSetTooFrequent","data":{"remainingSeconds":<1～60>}}（下取整）
RS "$DORA" "${QP}grace2" | jq -r .code                             # 0000（另一操作者不受限；T＝∅ ⊆ A）
SQL "SELECT created_by FROM sys_pwd_custody WHERE user_id = $GR ORDER BY created_by"   # 1 ／ <DO>（只 upsert、不刪他列）
G1=$(tok qs_grace "${QP}grace2")
SET password_change_min_interval 0                                   # 0000（0＝停用）
EV3=$(SQL "SELECT coalesce(max(id),0) FROM session_event"); LOG8=$(LOGW)
RS "$SUPER" "${QP}grace3" | jq -r .code                            # 0000
SET password_change_min_interval 60
curl -s "$BASE/auth/getUserInfo" -H "$G1" | jq -r .code              # 8888
SQL "SELECT event_type, reason FROM session_event WHERE id > $EV3"   # revoked|password_reset
SQL "SELECT operation FROM sys_operation_log WHERE id > $LOG8 AND entity_table = 'sys_user'"   # reset_password
LOGINJ qs_grace "${QP}grace2" | jq -r .code; sleep 0.3; LOGINJ qs_grace "${QP}grace3" | jq -r .code   # 1000 ／ 0000
```

自助改密（AS4／AS6；FR-036／FR-037）：

```bash
P=$(LOGINJ qs_alice "${QP}alice"); C1="authorization: Bearer $(jq -r .data.token <<<"$P")"; sleep 0.3; C2=$(tok qs_alice "${QP}alice")
CP() { curl -s "$UC/changePassword" -H "$C1" -H "$J" -d "{\"oldPassword\":\"$1\",\"newPassword\":\"$2\",\"confirmPassword\":\"$3\"}" | jq -r .msg; }
CP "${QP}alice" "${QP}alice" "${QP}alice"                      # biz.user.passwordSameAsOld
CP "${QP}alice" short short                                        # biz.user.passwordPolicy（攜違規清單）
CP wrong1 "${QP}alice2" "${QP}alice2"                            # biz.user.oldPasswordMismatch
RC "TTL cpwd:$AL"                                                    # 1～900（每使用者滑動窗；鍵與登入節流分離）
EV4=$(SQL "SELECT coalesce(max(id),0) FROM session_event"); LOG9=$(LOGW)
CP "${QP}alice" "${QP}alice2" "${QP}alice2"                    # common.success
RC "EXISTS cpwd:$AL"                                                 # 0（成功即清）
curl -s "$BASE/auth/getUserInfo" -H "$C2" | jq -r .code; curl -s "$BASE/auth/getUserInfo" -H "$C1" | jq -r .code   # 8888 ／ 0000（撤本人其他會話、保留當前）
SQL "SELECT event_type, reason, count(*) FROM session_event WHERE id > $EV4 GROUP BY 1,2"   # revoked|password_changed|2（§5 末之 A3 與本段 C2；保留當前 C1）
SQL "SELECT operation FROM sys_operation_log WHERE id > $LOG9"       # change_password
CP "${QP}alice2" "${QP}alice3" "${QP}alice3"                   # biz.user.pwdSetTooFrequent（冷卻對＝本人×本人、零豁免）
for i in 1 2 3 4 5; do CP wrong "${QP}alice9" "${QP}alice9"; done   # 五行 biz.user.oldPasswordMismatch
CP "${QP}alice2" "${QP}alice9" "${QP}alice9"                   # biz.user.changePasswordThrottled（第 6 次；舊密正確亦於比對之前拒；純 key）
MET 'throttle_degraded_total{' | wc -l                               # 11（來源值集 10→11、開機預註冊）
MET 'throttle_degraded_total{source="redis_change_pwd"}'             # throttle_degraded_total{source="redis_change_pwd"} 0
```

登入路徑不驗政策（AS9；FR-032、FR-050）：

```bash
ADD '{"userName":"qs_henry","password":"'"$QP"'%Complex-pass_long*"}' | jq -r .code   # 0000（含特殊字元、26 字）
LOGINJ qs_henry "${QP}%Complex-pass_long*" | jq -r .code         # 0000（登入頁之 UI 面＝§10）
sleep 0.3; LOGINJ User 123456 | jq -r .code                          # 0000（6 字短於下限照登）
```

- 改密節流窗自癒（15 分鐘）、無解鎖端點；載體不可用之放行與 `redis_change_pwd` 增一＝整合測試面（停 redis 牽動全面、不入走查）；同帳號並發上界、壞值自癒與鎖內快取往返 1 秒上界＝整合測試面（本刀 U13 期間增補＝T112）；§13 restore 清 `cpwd:`。
- 三重不洩之日誌面：`dc logs --since 30m rust-api | grep -c -F "$QP"` 印 0（零命中 rc 1 屬正常）；回應面＝§2、稽核面＝§3。

## 7. 個人中心與自助白名單（US3 AS7／AS8、FR-038／FR-039）

```bash
curl -s "$BASE/route/getUserRoutes" -H "$C1" | jq -c '[.data.routes[].name]'        # ["user-center"]（零角色帳號：只得白名單；常量路由由前端內建）
curl -s "$BASE/route/getUserRoutes" -H "$USER" | jq -c '[.data.routes[].name]|sort'  # ["function","home","user-center"]（R_USER_COMMON 無該選單政策列、碼內白名單併入）
curl -s "$BASE/route/getUserRoutes" -H "$ADMIN" | jq -c '[.data.routes[].name]|sort' # ["function","home","manage","user-center"]（白名單外路由不受影響）
curl -s "$BASE/route/getUserRoutes" -H "$SUPER" | jq '[.data.routes[]|select(.name=="user-center")]|length'   # 1（R_SUPER 既有政策列與白名單不重複）
curl -s "$UC/getPasswordPolicy" -H "$C1" | jq -r .code                               # 0000（零角色帳號可讀政策）
```

**預期**：白名單只收受眾＝本人之自助頁；R_SUPER 之 `user-center` 政策列保留；兩向案由整合測試釘死（FR-039；ADR④＝ADR-00077）；改密卡 UI 面＝§10。

## 8. 自鎖防護與 m0003（US4 AS10／AS11、US6 AS2、SC-007、FR-041～FR-046）

```bash
git -C rust-api ls-tree --name-only HEAD migration/src/ | grep -c '/m0'   # 3
SQL "SELECT count(*), count(*) FILTER (WHERE protected) FROM casbin_rule WHERE id <= 164"   # 163|25（刪一增一；受保護 19→25）
SQL "SELECT CASE WHEN v2 IN ('GET','POST','DELETE') THEN 'endpoint' ELSE v2 END, count(*) FROM casbin_rule WHERE protected GROUP BY 1 ORDER BY 1"   # button|6 ／ endpoint|15 ／ menu|4
SQL "SELECT string_agg(v1, ',' ORDER BY id) FROM casbin_rule WHERE protected AND v2 = 'button'"   # role:add,role:edit,role:delete,menu:add,menu:edit,menu:delete（皆屬 R_SUPER）
SQL "SELECT count(*) FROM casbin_rule WHERE id = 44"                       # 0（R_ADMIN 之 user:edit 已刪）
SQL "SELECT v0, v1, v2, protected, created_by IS NULL FROM casbin_rule WHERE id = 164"   # R_SUPER|ipRule:unlock|button|f|t
SQL "SELECT position('ipRule:unlock' in buttons::text) > 0, position('解鎖來源IP' in buttons::text) > 0 FROM sys_menu WHERE id = 78"   # t|t
SQL "SELECT count(*) FROM sys_menu WHERE id <= 78"                         # 78（選單列數不變）
python3 -c "import json;d=json.load(open('docs/ops/reference-src/schema-evolution.json'));e=d['entries'];print(d['next_id'],len(e),sorted({x['kind'] for x in e}),sorted({x['knife'] for x in e}),sorted({x['table'] for x in e}))"
                                                                           # 10 9 ['seed_add', 'seed_delete', 'seed_update'] ['007-user-password-admin'] ['casbin_rule', 'sys_menu']（逐筆形＝data-model.md §9；table 集＝system_settings 零登記之機器反證）
curl -s "$SM/getRoleButton?id=1" -H "$SUPER" | jq -c '{n:(.data|length),p:([.data[]|select(.protected)]|length)}'     # {"n":21,"p":6}
curl -s "$SM/getAllButtons" -H "$SUPER" | jq '.data|length'                                                          # 21（治理域按鈕碼聯集含 ipRule:unlock）
curl -s "$SM/getRoleEndpoints?id=1" -H "$SUPER" | jq -c '{n:(.data|length),p:([.data[]|select(.protected)]|length)}'  # {"n":45,"p":15}（列 68 入候選；候選外餘 5 列）
curl -s "$SM/getAllEndpoints" -H "$SUPER" | jq '.data|length'                                                        # 45
curl -s "$SM/getRoleEndpoints?id=2" -H "$SUPER" | jq -c '[.data[].path]|sort'     # ["/systemManage/getAllRoles","/systemManage/getRoleList","/systemManage/getUserList"]
curl -s "$SM/getRoleMenu?id=1" -H "$SUPER" | jq -c '{n:(.data|length),p:([.data[]|select(.protected)|.id]|sort)}'   # {"n":77,"p":[4,5,9,10]}（選單維不受 m0003 影響）
curl -s "$BASE/auth/getUserInfo" -H "$ADMIN" | jq -c '.data.buttons|sort'         # ["B_CODE2","B_CODE3"]（Admin 預設只見使用者清單＝GR7）
curl -s "$BASE/auth/getUserInfo" -H "$SUPER" | jq -c '{n:(.data.buttons|length),u:(.data.buttons|index("ipRule:unlock") != null)}'   # {"n":21,"u":true}
```

選單編輯刪碼守門（GR1b；ADR⑭＝ADR-00086）——探針取自建選單：其按鈕清單含 `role:edit`，而角色管理選單仍持該碼＝即使守門失效亦不成絕版、不連動歸檔，故探針不觸 seed 列：

```bash
curl -s "$SM/addMenu" -H "$SUPER" -H "$J" -d '{"menuType":"2","menuName":"qs","routeName":"qs_guard","parentId":2,"buttons":[{"code":"role:edit","desc":"探針"},{"code":"qs:free","desc":"自由碼"}]}' | jq -r .code   # 0000
MG=$(SQL "SELECT id FROM sys_menu WHERE route_name='qs_guard' AND deleted_at IS NULL")
LOGA=$(LOGW); R8=$(RELOAD)
UM() { curl -s "$SM/updateMenu" -H "$SUPER" -H "$J" -d "{\"id\":$MG,\"buttons\":$1}" | jq -c '{code,msg}'; }
UM '[{"code":"qs:free","desc":"自由碼"}]'                                # {"code":"2222","msg":"biz.menu.protectedButtonRemove"}（移除之碼尚有受保護授權列 59）
UM '[{"code":"role:edit2","desc":"探針"},{"code":"qs:free","desc":"自由碼"}]'   # 同上（改碼＝移除舊碼）
SQL "SELECT position('role:edit' in buttons::text) > 0 FROM sys_menu WHERE id = $MG"   # t（零變更）
SQL "SELECT count(*) FROM sys_operation_log WHERE id > $LOGA"             # 0（零稽核）
UM '[{"code":"role:edit","desc":"探針"}]'                                 # {"code":"0000","msg":"common.success"}（移除集無受保護授權碼）
[ "$(RELOAD)" = "$R8" ] && echo no-sync                                   # no-sync（拒＝零判定面同步；qs:free 無授權列＝歸檔 0 列不觸發）
```

- R_SUPER 六碼之撤銷整批拒（`biz.role.protectedRevoke`）、按鈕維受保護列不入封死集、seed 錨定測試改對（FR-046）＝整合測試面（本檔對 R_SUPER 零寫入）；UI 無使超管失去 `role:edit` 之路徑＝§10 鎖定觀察＋整合測試（SC-007）。全新庫重放後三閘綠、拆序號合成即紅＝§12＋§13 Day-1 第 3 步。

## 9. 解鎖兩入口之 API 面（US4 AS9、FR-040、GR3／GR4；ADR⑨ 款 1）

```bash
LOGB=$(LOGW)
UL() { curl -s "$SM/unlockLogin" -H "$1" -H "$J" -d "$2" | jq -r '.code + " " + .msg'; }
UL "$SUPER" '{"dimension":"user","userName":"qs_alice"}'   # 0000 common.success（未鎖帳號照回成功並落稽核＝GR3）
UL "$DORA" '{"dimension":"user","userName":"Super"}'       # 5003 system.forbidden（帳號維套包含規則；拒＝零稽核、不寫標記）
UL "$DORA" '{"dimension":"user","userName":"qs_alice"}'    # 0000 common.success（T＝∅ ⊆ A）
UL "$DORA" '{"dimension":"ip","target":"203.0.113.9"}'     # 0000 common.success（來源維不套包含規則）
SQL "SELECT created_by FROM sys_operation_log WHERE id > $LOGB AND operation = 'unlock' ORDER BY id"   # 1 ／ <DO> ／ <DO>（恰三列）
RC "--scan --pattern 'throttle:unlock:*'"                   # 含 throttle:unlock:user:qs_alice 與來源維一把；無 throttle:unlock:user:Super
```

**預期**：端點本體與「稽核先於標記」不變；帳號維處理序由源碼次序釘承擔（`contracts/wire-user-admin.md` unlockLogin 帳號維之變更節）；真被鎖帳號之解鎖＝整合測試面；兩入口共用 `fetchUnlockLogin`＝§10。

## 10. 前端與 CDP 三方對照（SC-010／SC-013／FR-047～FR-051／FR-065；US1 AS4／AS9／AS10、US2 AS1、US3 AS7／AS9／AS10、US4 AS6～AS11）

一律派 opus[1m]／xhigh agent 以 CDP 接 `127.0.0.1:9229`（host 瀏覽器以 `--remote-debugging-port=9229` 起；driver＝`tools/orchestration/cdp.mjs`、走查腳本落不入版控之工作區），開分頁對照 22080（rev5 HEAD）vs 32080（rev6）、必要時加 22089（upstream example）；rev5 對照 stack 起法＝CLAUDE.md §7。CDP 基準本刀重取；判準＝結構清單逐項全等、任一不等即紅，間距／字體／顏色只記走查紀錄。
★語言：兩側結構比對一律先以 CDP 於該 origin 執行 `localStorage.setItem('SOY_lang', JSON.stringify('zh-CN'))` 後重新整理（cdp.mjs 無語言設定、由走查腳本自設；brainstorm 工程判斷⑯）——22080、32080、22089 三側步驟一律顯式設簡中（22080 為 spec 明文、32080 同設＝提示文案逐項對照之前提、22089 同形；ADR-00084 決定 8）；繁中畫面無 rev5 基準、於 §11 單邊驗收。
★22080 全程唯讀：登入後即掛非 GET 請求攔截（走查腳本內建守衛）、開抽屜或彈窗後按取消；須寫入才可比之流程（送出後 toast、踢除與重設、回收桶復原、列解鎖、改密成功、刪碼守門）改 32080 單邊實測＋rev5 碼面與 locale 字面靜態對賬、判定欄註明。
★32080 前置（單邊；經 UI 或以 §3／§4 之 API 形建立，API 形不算對照項）：自建角色 `R_QS_CDP`（授與 §4 `R_QS_DEL` 同形之三頁可見性、部分按鈕碼與端點——刻意不授 addUser、授 deleteUser 而不授 `user:delete`）、持該角色之自建帳號兩個、持停用中自建角色者一個、零角色者一個、含特殊字元且超過 18 字密碼者一個、供刪除與批刪之自建帳號三個；Super 與持 `R_QS_CDP` 者輪流登入（快速登入鈕只涵蓋 seed 三帳號、自建帳號之登入步另寫）。

| 面 | 操作 → 預期 |
|---|---|
| 使用者清單 | Super 開 `/manage/user` → 欄位集合與列序、分頁列、表頭鈕兩側逐項全等（角色欄以代碼串接）；32080 首載不再 4040（ADR⑧ 款 7）；記事欄以純文字顯示（FR-019）；不顯示鎖定狀態（GR3） |
| 搜尋卡 | 六欄兩側欄位全等；手機與信箱：22080 套格式驗證＝刻意分岔「搜尋卡手機與信箱」列；32080 輸入部分字串不出紅字、搜得該列（Q17） |
| 新增抽屜 | 欄位與預設兩側全等；設密欄掛提示文字、「隨機產生」開產密浮層；角色下拉全列含 R_SUPER（前端不預判＝FR-024） |
| 編輯抽屜 | 帳號名停用、無密碼欄；會話政策欄：Super 可改，持 `R_QS_CDP` 者顯現值而停用並提示「僅超級管理員可改」、不發 updateUserSessionPolicy（AS6）；本人列狀態與角色停用；持停用角色者：該角色以「（已停用）」灰色選項呈現、不可新選、可移除、預設保留（22080 整欄鎖住＝刻意分岔）；只改暱稱 → body 無 `status`／`roleIds`；改會話政策 → 另打其端點；32080 單邊：持 `R_QS_CDP` 者編輯同級帳號、勾 R_SUPER 送出 → `5003` 純 key 提示（AS8） |
| 刪除與批刪 | 列刪除鈕與表頭批刪依 `user:delete` 顯隱；確認框文案兩側全等（22080 開框後取消）；32080 單邊：刪除一自建帳號（先另開隔離瀏覽情境以之登入）→ 成功提示、列移入回收桶、被刪者分頁下一次請求 8888；批刪兩自建帳號同形；含本人之批刪 → 純 key 提示、零變更 |
| 回收桶 | 開關切換 → 搜尋卡隱藏、操作欄換「復原」、不加刪除時間欄；復原確認框明示「復原後需重新指派角色」（文案兩側全等＝22080 開框後取消）；32080 單邊：確定 → 列回現役、角色欄空白 |
| 列操作下拉 | 32080 項目＝踢除下線／重設密碼／解鎖登入（22080 無「解鎖登入」項、解鎖在頁首彈窗＝刻意分岔「解鎖入口」列）；本人列不列「重設密碼」；各項依 `user:kick`／`user:reset-pwd`／`user:unlock` 顯隱 |
| 踢除流程（32080 單邊＋文案靜態對賬） | 另開隔離瀏覽情境以自建帳號登入 → Super 列操作「踢除下線」→ 確認 → 成功提示；被踢分頁下一次請求 → 7777 提示框＝`auth.session.kickedByAdmin` 譯文（zh-CN 字面對 rev5 locale 同鍵；被踢者可立即重登）；單一會話頂替之提示文案不變（§5） |
| 重設密碼浮層＋產密浮層 | 即時規則隨政策（§6 設定寫端形調整、觀察後改回）；產密套用後送出成功；冷卻內 → 提示顯剩餘秒數、違規 → 顯違規清單人話（請求層兩鍵明細轉譯；子鍵＝`page.passwordPolicy.*`）；其餘拒因純 key |
| 列解鎖 | 任一列按「解鎖登入」→ 成功提示（未鎖亦成功＝GR3）；稽核一列 `unlock`（§9 SQL 形） |
| 按鈕顯隱：使用者頁 | Super 七碼全見；Admin 只見清單、無任何操作鈕（22080 見「編輯」＝刻意分岔）；User 側欄無此頁；持 `R_QS_CDP` 者只見被授之碼——碼有端點無＝鈕見而 `5003`、端點有碼無＝鈕不見（AS7） |
| 按鈕顯隱：角色頁與選單頁 | Super 全見（選單頁含新增子選單）；持 `R_QS_CDP` 者只見 `role:edit`／`menu:add` 對應鈕；選單回收桶「復原」與角色抽屜三顆授權鈕不設碼（Q8、工程判斷⑬＝FR-048；其讀寫屬封死集＝ADR⑧ 款 10）；22080 不做顯隱＝刻意分岔「角色頁、選單頁按鈕」列（ADR⑧ 款 18 全解除之對象為 rev6 現況） |
| 按鈕權限彈窗（R_SUPER；只觀察、按取消） | `role:*`／`menu:*` 六碼呈鎖定不可取消（22080 可取消＝刻意分岔「R_SUPER 角色與選單六碼」列）；`ipRule:unlock` 在候選且已勾；★不送出（受保護撤銷拒＝整合測試面） |
| 選單編輯刪碼守門（32080 單邊） | 以自建選單（按鈕清單含 `role:edit` 與一自由碼）編輯、移除 `role:edit` 送出 → `biz.menu.protectedButtonRemove` 譯文提示、按鈕清單不變（22080 照常移除＝刻意分岔「選單編輯移除按鈕碼」列；只靜態對賬） |
| IP 規則頁 | Super 見表頭前綴插槽「解鎖來源 IP」鈕（`ipRule:unlock`）→ 彈窗輸入 IP → 成功；不持碼者不見；表頭既有 prop 形不變（view-render-guard 錨）；22080 無此入口＝刻意分岔（32080 單邊＋22089 結構錨） |
| 個人中心 | 頭像下拉 → 只掛「修改密碼」卡、其餘卡位留白；即時規則（攔截政策讀使之失敗 → 退為只驗必填；卡不另出提示、共用請求層之統一錯誤提示照常）；成功 → 當前分頁保留、另一分頁 8888；零角色帳號可達 |
| 登入頁 | 兩欄只驗必填：輸入任意非空字串不出格式紅字（22080 自 `rev5:007` 已同形）；以含特殊字元且超過 18 字密碼之自建帳號直接登入成功；captcha 軟區零變更；三顆快速登入鈕仍在（BL-00049） |
| 語言下拉 | 32080 恰「简体中文／繁體中文／English」三項、清除儲存後首次開啟為繁中（22080 兩項且預設簡中＝刻意分岔「預設語言與語言下拉」列；詳 §11） |

- 排除清單（SC-010）＝spec 刻意分岔登記表各列（★登記表於 CDP 開跑前凍結；CDP 中新發現者須經 user 親決〔AskUserQuestion〕入表、否則判紅）＋ADR⑧／ADR⑨ 草稿各款＋spec Edge Cases「前端與按鈕碼」所列已知態（使用者詳情頁佔位、個人中心其餘卡位留白、三顆快速登入鈕）＋008 刀兩頁死項（system-settings／audit）＋請求次數維度。
- ADR-00070 觸發器④（只改名稱不被擋）與 ADR⑧ 款 20 之可達性實測＝§14。

## 11. 繁中介面（US5 AS1～AS5、SC-009、FR-052、GR5；ADR⑪＝ADR-00084）

```bash
dc exec -T base-web pnpm typecheck                              # rc 0（zh-tw.ts 以完整 App.I18n.Schema 標型＝三語鍵集相等之機器守）
grep -c '^const local: App.I18n.Schema = {' base-web/src/locales/langs/zh-tw.ts   # 1
grep -c "'zh-TW'" base-web/src/locales/index.ts base-web/src/store/modules/app/index.ts base-web/src/locales/dayjs.ts   # 三檔皆 ≥1（未選過語言之預設三處）
python3 tools/msg-key-gate.py check                             # rc 0（MSG_KEYS 68 ⇔ 三檔 backend 子樹逐檔雙向全等）
python3 tools/zh-tw-lint.py check                               # rc 0（簡體殘字零命中〔具名白名單除外〕、禁用大陸用語零命中、「頂替」「踢除」語意用詞檢查綠）
python3 tools/zh-tw-lint.py test                                # rc 0（合成反例逐類轉紅＝RL-0080；命令形與判準＝contracts/code-gates.md §2）
```

CDP（32080 單邊；22080 無 runtime 繁中＝刻意分岔「繁中畫面」列）：

- 清除該 origin 之儲存後開啟登入頁 → 畫面文字為繁中、語言下拉之當前項為「繁體中文」（AS1）；切到簡中或英文後重開 → 照記（`SOY_lang`）。
- 語言下拉恰三項（AS2）；三語各切一次 → 全頁面無裸鍵、無簡體殘字；日期選擇器與表格分頁元件隨語言切換（naive `zhTW`／`dateZhTW`、dayjs `zh-tw`）。
- 用語（AS5、GR2）：管理員踢除之被踢提示與按鈕「踢除下線」用「踢除」語意、單一會話被別處登入擠掉之提示用「頂替」語意；程式內原因值不改。
- AI 逐頁審讀（GR5）：涵蓋全部接真頁面——登入頁、首頁、使用者管理（含抽屜、回收桶、三浮層）、角色管理（含三顆授權彈窗）、選單管理、IP 規則頁、授權回收桶頁、個人中心、版面共用面（頂欄、頭像下拉、分頁籤、主題設定）與 7777／8888 提示框；逐頁記「頁面→不當用語或殘字→處置」，承載於 CDP 三方對照單元之走查紀錄（落點由 tasks 定）。
- user 抽查：主線請 user 抽查繁中畫面並記錄結果；三者（機器檢查、AI 審讀紀錄、user 抽查）齊全才算 AS4 兌現。

## 12. 工具與閘（SC-002／SC-007／SC-008／SC-011～SC-013、FR-045／FR-054～FR-057／FR-061／FR-063～FR-066）

```bash
dc exec -T rust-api cargo test --workspace -- --test-threads=1   # 全綠（contract 61 case 與覆蓋閘雙向、新鍵實發點與名冊雙向、名冊閘、包含規則 9 消費點、守衛四件補回自證）；★此時 dev 庫帶 §3～§9 之走查殘列（自建帳號與其指派、自建角色與其授權列、經手表列、改密節流鍵、會話與稽核列）＝SC-008 前半之殘列面、不可跳過、MUST 排在 §13 restore 之前；逾時一律放進容器內（LL-00039）
dc exec -T base-web pnpm typecheck                               # rc 0
python3 tools/docsync check && python3 tools/docsync lint && python3 -B tools/docsync test   # 零紅（docsync 自測含 routes 釘值 61 列＝LL-00060）
python3 tools/msg-key-gate.py check && python3 tools/msg-key-gate.py test   # rc 0（斷言 2 擴認 BizData 構造點；前端消費點名冊含兩鍵明細轉譯）
grep -o 'MSG_KEYS: \[&str; [0-9]*\]' rust-api/server/src/error.rs   # MSG_KEYS: [&str; 68]
python3 tools/wire-schema.py check && python3 tools/view-render-guard.py check && python3 tools/route-artifact-gate.py check && python3 tools/rust-fmt-gate.py check && python3 tools/entity-drift-gate.py check   # 皆 rc 0（容器依賴者未起＝具名跳過，收刀前須在起態跑；碼面閘表全員＝RUNBOOK §12）
python3 tools/seed-view-gate.py check && python3 tools/zh-tw-lint.py check   # rc 0
python3 tools/schema-gate.py test                                # rc 0（含 seed_add 序號合成之正反案＝GR9）
python3 tools/walkthrough-baseline.py test                       # rc 0（v4 合成案：seed 指派被刪回補、新帳號列與其指派清除與序列回值、seed 帳號欄值回寫、經手表與 cpwd: 清除、遷移帳前置拒跑、seed 模式合成目標、兩模式系統設定合成比對、遷移不同步拒跑——各附變異自證）
grep -n '^\*\*Version\*\*' .specify/memory/constitution.md       # 1.8.0；收刀前 PATCH 實數化範圍欄後為 1.8.x
```

fork-delta-lint（新用途列名冊載入、範圍欄對賬腿、修改型只在授權檔；`contracts/code-gates.md` §1）一正一反（RL-0080；`--constitution` 只供自身變異驗證）：

```bash
python3 tools/fork-delta-lint.py                                 # 正：rc 0（self-test＋全掃＋對賬腿）
C=<憲法副本路徑（不入版控之工作區）>
cp .specify/memory/constitution.md "$C"
#   反①（範圍欄對賬腿；須於收刀前 PATCH 實數化之後跑——預估注記不入對賬）：副本 §III.2 新用途 (v) 列某檔之「N 處」改「N+1 處」（片段與憲法現文逐字相同、grep -c＝1）
python3 tools/fork-delta-lint.py --constitution "$C"             # rc 1、指名（軌道, 用途, 檔, 注記值, 實數）
cp .specify/memory/constitution.md "$C"                          # 反②前重取副本（兩發單獨跑、不疊加＝RL-0005）
#   反②（新用途列名冊載入）：副本 (v)～(viii) 任一列範圍欄反引號路徑之「反引號內」字面改為不含 / 之非路徑 token；拔反引號形只令該檔靜默掉出名冊、不 die，不得作自證
python3 tools/fork-delta-lint.py --constitution "$C"             # rc 2、指名「範圍欄抽出殘渣／非路徑 token」（LOGIN-CAPTCHA (ii)、I18N (iii) 列同形各另跑一發）
rm "$C"
```

base-web 變更檔集（SC-011、FR-054；fork-delta-lint 不做檔集斷言——判準與允許集＝`contracts/code-gates.md` §1，本檔不重抄）：

```bash
for f in $(git -C base-web diff --name-only --diff-filter=M fb4dac2..HEAD); do git -C base-web cat-file -e 8be6f9ba:"$f" 2>/dev/null && echo "$f"; done   # 輸出 ⊆ code-gates §1 之修改型授權檔集（upstream 基線不存在之檔＝rev6 自有檔或新增檔、不列）
git -C base-web diff --name-only --diff-filter=A fb4dac2..HEAD    # 恰 code-gates §1 之新增檔名冊（data-model.md §12）
git -C base-web diff --name-only --diff-filter=DR fb4dac2..HEAD   # 空
```

- 新增圈界塊「拔標記必紅」（SC-011）：各塊之紅證以落地單元紀錄為證（塊名冊與做法＝`contracts/code-gates.md` §1）；走查時可任取一塊重跑——暫拔其 START／END 標記 → `python3 tools/fork-delta-lint.py` 紅（報未圈界新增）→ 以存原文寫回（RL-0019）→ `git -C base-web status --porcelain` 回基準（逐塊單獨跑、不疊加＝RL-0005；不與 CDP 走查並行）。路由產物零重算（不新增 view 目錄）＝`route-artifact-gate.py check` 綠；`components.d.ts` 若有變化只許工具重算形。
- 憲法 Amendment 先行（SC-012、US6 AS1）：`B0=$(git merge-base rev6-admin-root HEAD)` → `git log --format='%h %s' "$B0"..HEAD -- .specify/memory/constitution.md` 見 1.7.1→1.8.0 之 Amendment 顆（ADR-00074；另見收刀前 PATCH 顆）→ 機器斷言＝`git ls-tree <Amendment 顆> base-web` 之 gitlink＝`fb4dac2`（本刀起手 pin；本刀單元序使純新增檔亦落在 Amendment 之後）。
- ADR：plan 期十四支（ADR-00074～ADR-00087；⑫ 不另立）＋實作期翻案一支（ADR-00090；本刀 U13 期間增補、supersede ADR-00078）＋收刀前 PATCH Amendment 一支（配號＝當下下一號）於收刀前皆 `status: accepted`（ADR-00078 轉 `superseded`）——`for n in $(seq 74 87); do grep -m1 '^status:' docs/arc42/decisions/ADR-000$n-*.md; done | sort | uniq -c` 印 `13 status: accepted` 與 `1 status: superseded`（ADR-00078）、`grep -m1 '^status:' docs/arc42/decisions/ADR-00090-*.md` 印 `status: accepted`；supersede 宣告以各 ADR accepted 顆為準（spec 明定者＝ADR⑪ supersede ADR-00039、ADR⑮ supersede ADR-00012；實作期＝ADR-00090 supersede ADR-00078）；親決時點＝research R21（ADR-00090＝user 2026-10-12 裁定）。
- 整合測試承擔面（走查不構造）：SC-003 seed 結構保護與 FR-010 逐格；SC-004 每消費點全量；SC-005 換發重驗三形與失效名單寫入失敗注入；SC-006 載體不可用放行；SC-007 R_SUPER 六碼撤銷拒；FR-063 之併發四案（含本刀 U13 期間增補之改密節流並發上界＝T112）與 ADR-00044 觸發器②；`advisory_lock_user` 收窄之 compile_fail doctest、零重載反向確認、`NO_ESCALATION_CALL_FILES` 一正一反（`contracts/code-gates.md` §2～§5）。守門變異自證（拆 → 紅 → 還原 → 綠、skipped=0）以單元紀錄為證；判準變異不得拆真庫守衛（LL-00053）。
- 現在式假述掃除（SC-014、FR-059；RL-0011 四形種子）：以 `python3 tools/docsync errata <詞>` 逐詞現量——種子例：「使用者域刀」「使用者角色指派寫端」「007 刀」「屬後刀域、不帶」「不產 hash」「恰十」「恰九」「門在頁級」「不接 runtime」「孤立檔」「兩語」「無 UI 按鈕」「零 migration」「隨每支帶 migration 的刀前進」「五詞」「四十六」「四十九」「三十五」，與阿拉伯數字形並掃；受保護列數「19」之現在式面（schema-definition 屬 001 基線者除外）與指單會話被擠掉之「踢除」句逐處判讀；命中只餘史料面、accepted ADR body 與事件源；處數以現量為準、不寫死。
- `bash tools/bootstrap.sh`（舊機重跑＝純體檢；含新碼面閘 `tools/zh-tw-lint.py` 自測之名冊推導）rc 0。

## 13. 收尾（SC-008 後半、SC-013；US6 AS3～AS7、FR-057）

```bash
SQL "SELECT setting_key || '=' || setting_value FROM system_settings WHERE setting_key LIKE 'password%' ORDER BY 1"
                     # password_change_min_interval=60 ／ password_forbid_username=off ／ password_max_length=64 ／ password_min_length=8 ／ password_require_digit=off ／ password_require_lowercase=off ／ password_require_special=off ／ password_require_uppercase=off（§6 改過者已逐鍵改回；比對左源＝凍結 seed ⊕ 演進登記之 `seed_*` 合成＝spec FR-057 (b)〔本刀 system_settings 零登記（§8 之 table 集為機器反證）＝合成值即 seed 值〕；值不等＝rc 2 指名該鍵、restore 不改值＝RUNBOOK §9c 第 3 步）
python3 tools/walkthrough-baseline.py restore "$WB"   # rc 0；輸出含「MUST 重啟 rust-api」（刪自建角色之授權列、自建帳號與其指派〔指派先於帳號＝FK RESTRICT〕、自建選單與角色、經手表全表、序列回基準；redis session:／throttle:／cpwd: 逐鍵 DEL）
dc restart rust-api                                    # 動過 casbin_rule 即重啟
python3 tools/walkthrough-baseline.py diff "$WB"      # rc 0（SC-008 後半）
python3 tools/schema-gate.py check                    # rc 0（gate2 逐列比對 seed ⊕ 演進帳合成；sys_user 與指派表不在收窄集＝逐列全等）
SQL "SELECT last_value, is_called FROM casbin_rule_id_seq"    # 164|t
SQL "SELECT last_value, is_called FROM sys_user_id_seq"       # 3|t（seed 態；基準取樣時另有既存列者以基準值為準）
RC "--scan --pattern 'cpwd:*'" | wc -l                        # 0
```

- 手上無走查前基準檔者改跑 `python3 tools/walkthrough-baseline.py restore --seed`（v4：目標態＝凍結 seed ⊕ 演進登記之 `seed_*` 合成——列 44 不在、列 164 在、列 58～63 受保護、序號 164；系統設定比對左源同合成）＋重啟＋`schema-gate.py check`（RUNBOOK §9c 第 3～4 步）。repo 已含之 migration 尚未套進 dev 庫＝rc 2、零寫入、指名未套用之遷移（spec FR-057 (b)）；清理面各表有 `seed_*` 登記＝照舊拒跑（明列邊界）。
- seed 帳號欄值或指派若於觀察中被改（本檔無此步；BL-00136 形②與欄值形屬具名排除＝FR-058）：v4 restore 依基準回寫 seed 帳號可變欄（含密碼雜湊與審計欄）並回補被刪之指派對，`diff` rc 0＋`schema-gate.py check` 綠為判準。

收刀前 Day-1 登記三步（RUNBOOK §10；只於 U23 跑、排在上列還原之後）：

```bash
python3 tools/docsync refresh                         # rc 0（照相；需乾淨 dev 庫——accounts 投影逐鍵比對，自建帳號、指派殘列或 seed 帳號欄值殘留即令 generate 轉紅）
#   第 2 步＝演進帳九筆已由撰寫 m0003 之單元登記（§8 已核 next_id 10／entries 9）；本步只復核、不新增
python3 tools/schema-gate.py check                    # rc 0（dev 庫）
#   第 3 步 pristine：一次性 postgres 容器＋獨立 network（命令形＝specs/001-schema-baseline/fixtures/provenance.md §6，容器與 network 名改本刀自取）→ 容器內 migration up（m0001～m0003）→
python3 tools/schema-gate.py check --container <pristine 容器名>   # rc 0（gate2 之 casbin_rule 序號期望＝164＝seed_add 合成推進）
#   拆除容器、network、匿名 volume；★drvfs 上跑過 docker bind mount 後先重新 cd 再跑 python／git（CLAUDE.md §3）
```

- 照相若改動快照檔，其 `python3 tools/docsync generate`＋`git add` 屬主線收單；schema-definition 不前進（GR8）＝`python3 tools/schema-gate.py doccheck` rc 0。

## 14. 已知態觀察（ADR⑧＝ADR-00081、ADR⑨＝ADR-00082、ADR⑦＝ADR-00080；spec Edge Cases）

ADR⑧ 收回 ADR-00068 決定 4① 之 seed 例外：觀察一律以自建帳號持自建角色（承 §4 之 `qs_dora`／`R_QS_DEL`／`R_QS_OFF` 或 §10 前置之 `R_QS_CDP`）、不對 seed 角色寫入 ⇒ 本段與主走查共用同一基準、排在 §13 之前。階段①（CDP 三方對照單元）未跑 §3／§4 者，先跑 §3 首塊之 `R_QS_U` 建立（`RU`）與 `ADD()`、§3 編輯塊之 `U()` 定義，再跑 §4 首塊（`R_QS_DEL`／`R_QS_OFF`、三維授權、`qs_dora`、`qs_erin`、`DU`／`DUD` 兩函式）與停用角色段前四行，使 `qs_dora` 持 {`R_QS_DEL`, `R_QS_U`, `R_QS_OFF`} 且 `R_QS_OFF` 已停用。每款記「觀察路徑→症狀」（`rev5:L-046`：推論不得代替觀察）；無可觀察實例者附機器反證（RL-0033）。

```bash
# ADR⑧ 款 20 改述＋實測（ADR-00070 觸發器④之 API 面）：qs_dora 持停用中之 R_QS_OFF 與啟用之 R_QS_DEL（後者授 updateRole、getRoleList、角色頁可見性與 role:edit）
DU updateRole "{\"id\":$RO,\"status\":\"2\"}"                       # 2222 biz.role.cannotDisableSelfRole（繞過 UI 對已停用之自身所屬角色送停用值照擋）
DU updateRole "{\"id\":$RO,\"roleName\":\"停用走查改名\"}"           # 0000 common.success（不帶 status 之只改名稱不被擋）
# ADR⑧ 款 9 部分解除：使用者域與 unlockLogin 帳號維已由包含規則守（§4、§9）；角色域續存——持委派角色者可改其未持之自建角色
curl -s "$SM/addRole" -H "$SUPER" -H "$J" -d '{"roleCode":"R_QS_X","roleName":"未持走查"}' | jq -r .code   # 0000
DU updateRole "{\"id\":$(RID R_QS_X),\"roleName\":\"x\"}"            # 0000 common.success（角色域不套包含規則＝Q7；對 seed 角色之同形以整合測試觀察）
# ADR⑨ 款 3：稽核寫入者擴列、動作詞彙五詞→八詞
SQL "SELECT string_agg(DISTINCT operation, ',' ORDER BY operation) FROM sys_operation_log"   # add,change_password,delete,kick,reset_password,restore,unlock,update（階段①＝§10 之 32080 單邊寫入〔新增、編輯、刪除、復原、踢除、重設、改密、解鎖〕與本段之後；階段②＝§3～§9 全跑後）
```

| 款 | 觀察路徑 → 症狀（以實測定稿） |
|---|---|
| ADR⑧ 款 7（結案） | Super 開使用者頁 → 首載清單成功、新增抽屜之角色下拉列活性且啟用之角色；持停用角色者於編輯抽屜以灰色保留選項呈現（`rev5:B-145` 結案） |
| ADR⑧ 款 10（改述） | 以 `qs_dora` 開角色頁（其角色被授角色管理頁可見性）→ 表頭與列鈕只見所持 `role:edit` 之編輯鈕；抽屜三顆授權鈕可見、彈窗之現況讀端屬封死集回 `5003`、確定鈕停用、開窗各跳共用請求層錯誤提示「沒有權限執行此操作」；「菜單權限」彈窗另發之 getRoleHome 未授亦 `5003`、首頁下拉照常可操作；選單頁同形（只見 `menu:add` 對應鈕；回收桶清單讀端 getDeletedMenus 屬封死集恆 `5003`、跳同一提示、清單載不出＝復原鈕不可達） |
| ADR⑧ 款 11（改述） | 全量替換之並行編輯後送出者整份覆蓋續存；可撞上之情境隨本刀擴大——指派寫端可使 R_SUPER 為多帳號持有（三維寫端屬封死集、只 R_SUPER 持有者可達）⇒ Super 與持 R_SUPER 之自建帳號於兩瀏覽情境對同一自建角色之端點權限彈窗先後送出不同期望全集 ⇒ 後送出者整份為準、前者差量被靜默撤銷；改述字面以 ADR⑧ 草稿為準 |
| ADR⑧ 款 18（全解除） | §10 按鈕顯隱兩列之實測即其證（授撤 `role:*`／`menu:*`／`user:*` 碼後重新登入 ⇒ 對應鈕隨之顯隱） |
| ADR⑧ 款 20（改述＋實測） | 上列 API 兩發＋CDP：`qs_dora` 於角色頁編輯 `R_QS_OFF` 只改名稱送出 ⇒ 成功、updateRole body 無 `status` 鍵（ADR-00070 觸發器④）；可達條件＝帳號同時屬已停用角色又持 updateRole（本刀指派寫端使之生產可達） |
| ADR⑨ 款 1（解除） | §10 列解鎖與 IP 規則頁解鎖鈕兩入口之實測即其證 |
| ADR⑨ 款 3（續行） | 上列 SQL：八詞皆出現；寫入者擴至使用者寫端與個人中心改密 |
| ADR⑦ 並行編輯已知態 | Super 於兩分頁開同一自建帳號之編輯抽屜 → 分頁乙改暱稱並確定 → 分頁甲（未重開）只改手機並確定 ⇒ 暱稱回到開啟時舊值（文字欄後送出者為準）；甲之 updateUser body 無 `status`／`roleIds` 鍵（狀態與角色只在改動時送、不把他人剛停用之帳號啟用回來） |
| spec 已知態 | 使用者詳情頁續為佔位（seed-view-gate 對賬、佔位檔不可刪）；個人中心其餘卡位留白；三顆快速登入鈕仍在（BL-00049）；系統設定與稽核兩頁仍為死項（008 刀；CDP 排除）；會話政策改 single 不即時踢除（§5） |

- 新發現之已知態併入 ADR⑧／ADR⑨ 草稿，交治理單元依親決分類（RL-0086）經 user 親決後 accepted（spec FR-056 親決時點）；ADR⑧⑨ accepted 前不得以本段推論代替觀察。
