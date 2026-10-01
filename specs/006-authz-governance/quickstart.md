# Quickstart — 006-authz-governance（驗證指南）

> 目的＝以 dev stack 端到端證明本刀可用（SC-001～SC-013 之走查面與機器命令；SC-014 屬簿記後驗、本檔只列其假述掃除之命令形）；不含實作碼、不含測試全文。承 005 刀 quickstart 形、rev6 座標。★一律指向 rev6 stack（UI 32080／API 經 front-nginx 32080 之 `/api`／`/metrics` 直連 32079／PG 35432；埠全表＝`docs/generated/reference/ports.md`）、一律 127.0.0.1，絕不指向 rev5 對照 stack（2xxxx）。前置＝ADR-00063 accepted（憲法 1.7.0；收刀前 PATCH 實數化範圍欄後為 1.7.x）。★執行時點分兩段：①CDP 三方對照單元（實作單元皆已合入、治理單元之前；ADR-00068／ADR-00069／ADR-00070 仍為草稿）＝§0→§8→§10→§11——§8 與 §11 之觀察結果交治理單元定案（research「執行單元切分」U16／U17）②收刀前（全部單元合入、容器內全量測試綠、ADR 皆 accepted）＝§0→§1～§7→§9→§10（§8 於此段可復跑作回歸、不再改 ADR）。
> ★寫入步驟一律對**走查自建**之角色與選單；對 seed 角色只有讀端呼叫（spec Clarifications 第六題：R_SUPER 之原樣提交、受保護撤銷拒、超管自救路徑與 seed 授權列之撤後回補皆由整合測試承擔〔清理守衛按原 id 回補〕、不入走查）；唯一例外＝spec Clarifications 第五題之已知態觀察（§11；R_ADMIN／R_USER_COMMON）。動過 `casbin_rule` 之還原後 MUST 重啟 rust-api（判定面無外部通知管道）。
> ★wire 欄名（請求 `id`／`menuIds`／`buttons`／`endpoints`、回應 `revoked`／`granted`／`effective`、讀端項 `protected`、回收桶列 `restorable` 等）沿 rev5 契約形（spec FR-005）寫入下列命令；逐欄定義以 `contracts/wire-authz-governance.md`／`contracts/wire-policy-archive.md` 為準、拒因鍵以 `contracts/msg-keys.md` 為準（譯文之家＝三檔 locale）、稽核列形與觸發矩陣以 `data-model.md` 為準，本檔不重述——兩者不符時以 contracts／data-model 為準並同批改本檔。各節依序執行，後節之預期承前節狀態。

## 0. 前置

```bash
cd <rev6 workspace 根>
dc() { docker compose -f docker-compose.yml -f docker-compose.dev.yml "$@"; }
dc ps                                                   # 實看容器態：rust-api／base-web／front-nginx／postgres／redis 皆在跑；缺者下一行重建
dc up -d --wait
BASE=http://127.0.0.1:32080/api
J='content-type: application/json'
SQL() { dc exec -T postgres sh -lc "psql -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" -At -c \"$1\""; }
RELOAD() { curl -s http://127.0.0.1:32079/metrics | grep '^casbin_reload_total{outcome="ok"}' | awk '{print $2}'; }
WB=<走查基準檔路徑（不入版控之工作區）>
python3 tools/walkthrough-baseline.py snapshot "$WB"    # rc 0（RUNBOOK §9c 第 1 步）；檔形 v3（本刀擴面：現行 v2→v3；spec FR-044、Clarifications 第五題）＝另存 id ≤ 上界之 casbin_rule 全欄快照與角色列可變欄（射程＝id ≤ 上界之角色列、含 seed 三列＝contracts/code-gates.md §6）；v2 舊檔 diff／restore 皆 rc 2 指名重取
login() { curl -s "$BASE/auth/login" -H "$J" -d "{\"userName\":\"$1\",\"password\":\"123456\"}" | jq -r .data.token; }
SUPER="authorization: Bearer $(login Super)"; ADMIN="authorization: Bearer $(login Admin)"; USER="authorization: Bearer $(login User)"
```

- snapshot 告警「id 上界高於其序列位置」或基準取樣時已有殘列＝先 `python3 tools/walkthrough-baseline.py restore --seed`、重啟 rust-api 後重新 snapshot（RUNBOOK §9c 第 1 步）。
- ★勿秒內狂打 auth 端點（nginx `auth_limit`）。CDP 走查排在 schema-gate 驗收之後、或走查後照 RUNBOOK §9c 還原（spec FR-051）。

## 1. 路由與授權態（SC-001／FR-001／FR-003／FR-007）

```bash
grep -c '^| /' docs/generated/reference/routes.md       # 49
grep -c '| Policy |' docs/generated/reference/routes.md # 35（Public 11、Authed 3 不變）
for ep in "getRoleMenu?id=1" "getRoleButton?id=1" "getRoleEndpoints?id=1" getAllButtons getAllEndpoints "getArchivedPolicies?current=1&size=10"; do
  echo "$ep super=$(curl -s "$BASE/systemManage/$ep" -H "$SUPER" | jq -r .code) admin=$(curl -s "$BASE/systemManage/$ep" -H "$ADMIN" | jq -r .code) user=$(curl -s "$BASE/systemManage/$ep" -H "$USER" | jq -r .code)"
done                                                    # 六行皆 super=0000 admin=5003 user=5003
for ep in updateRoleMenu updateRoleButton updateRoleEndpoints restorePolicy; do
  echo "$ep admin=$(curl -s "$BASE/systemManage/$ep" -H "$ADMIN" -H "$J" -d '{}' | jq -r .code) user=$(curl -s "$BASE/systemManage/$ep" -H "$USER" -H "$J" -d '{}' | jq -r .code)"
done                                                    # 四行皆 admin=5003 user=5003（授權層先於 handler、不讀 body）
RQ=$(RELOAD)
for ep in updateRoleMenu updateRoleButton updateRoleEndpoints; do curl -s "$BASE/systemManage/$ep" -H "$SUPER" -H "$J" -d '{}' | jq -r .msg; done
                                                        # 三行 biz.role.notFound（body 缺欄＝角色鍵預設值早拒、MUST NOT 演成全撤）
curl -s "$BASE/systemManage/restorePolicy" -H "$SUPER" -H "$J" -d '{}' | jq -r .msg   # biz.policy.notRestorable（識別預設值）
[ "$(RELOAD)" = "$RQ" ] && echo no-sync                 # no-sync（查無角色與 notRestorable 皆不觸發）
```

**預期**：Super 十支皆通（寫端之通過見 §3～§5）、Admin／User 十支皆 `5003`；contract 49 case 與覆蓋閘雙向由容器內全量測試承擔（§9）。

## 2. 三維讀端與候選讀（US1 AS4／AS8／AS9、FR-014、spec Clarifications 第二題）

```bash
curl -s "$BASE/systemManage/getAllEndpoints" -H "$SUPER" | jq '.data|length'          # 35（路由表 Policy 全集）
curl -s "$BASE/systemManage/getAllEndpoints" -H "$SUPER" | jq -c '.data[0]|keys'       # ["method","path"]（候選不帶受保護或封死預標）
curl -s "$BASE/systemManage/getAllButtons" -H "$SUPER" | jq '.data|length'             # 20（治理域按鈕碼聯集、去重）
curl -s "$BASE/systemManage/getRoleEndpoints?id=1" -H "$SUPER" | jq -c '{n:(.data|length),p:([.data[]|select(.protected)]|length)}'   # {"n":35,"p":14}
SQL "SELECT count(*) FROM casbin_rule WHERE v0='R_SUPER' AND v2 IN ('GET','POST','DELETE')"   # 50（候選外 15 列不入讀端）
curl -s "$BASE/systemManage/getRoleEndpoints?id=2" -H "$SUPER" | jq -c '[.data[].path]|sort'  # ["/systemManage/getAllRoles","/systemManage/getRoleList"]（seed 列 2 getUserList 屬候選外、不回）
curl -s "$BASE/systemManage/getRoleMenu?id=1" -H "$SUPER" | jq -c '{n:(.data|length),p:([.data[]|select(.protected)|.id]|sort)}'   # {"n":77,"p":[4,5,9,10]}
curl -s "$BASE/systemManage/getRoleButton?id=1" -H "$SUPER" | jq -c '{n:(.data|length),p:([.data[]|select(.protected)]|length)}'  # {"n":20,"p":0}
curl -s "$BASE/systemManage/getRoleMenu?id=999999999" -H "$SUPER" | jq -r .msg          # biz.role.notFound
curl -s "$BASE/systemManage/getRoleEndpoints" -H "$SUPER" | jq -r .msg                  # biz.role.notFound（id 缺席）
```

**預期**：三支現況讀端只回「現況 ∩ 候選集」且每項帶受保護旗標（受保護四列＝選單 id 4／5／9／10，即 `manage_role`／`manage_menu`／`manage_system-settings`／`manage_policy-archive`）；與 rev5 HEAD 之 wire 列數差（R_SUPER 端點維 35 對 50）屬 spec 刻意分岔登記表「三維現況讀端之回應集」列（ADR-00066 決定 5）；另 22080 之 getAllEndpoints 回 50 項（候選含 15 支 `rev5:007`／`rev5:008` 路由）＝候選集面之差（spec 刻意分岔登記表「端點候選集」列；逐支＝`contracts/wire-authz-governance.md`「與 rev5 wire 逐欄比對」getAllEndpoints 列）。端點維以 HTTP 方法白名單辨識（新建 `router::endpoint_methods()`；ADR-00064 決定 1）。

## 3. 三維寫端：全量替換（US1 AS1～AS3／AS5／AS7、US2 AS3、SC-003、FR-009～FR-012、FR-015）

```bash
curl -s "$BASE/systemManage/addRole" -H "$SUPER" -H "$J" -d '{"roleCode":"R_QS_AUTHZ","roleName":"授權走查"}' | jq -r .code   # 0000
RID=$(SQL "SELECT id FROM sys_role WHERE role_code='R_QS_AUTHZ' AND deleted_at IS NULL")
R0=$(RELOAD)
curl -s "$BASE/systemManage/updateRoleMenu" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"menuIds\":[1,11]}" | jq -c .data     # {"revoked":0,"granted":2,"effective":[1,11]}
curl -s "$BASE/systemManage/updateRoleMenu" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"menuIds\":[11,16]}" | jq -c .data    # {"revoked":1,"granted":1,"effective":[11,16]}（撤 home、授 user-center、about 不動）
SQL "SELECT archive_reason, v1, role_id = $RID FROM sys_casbin_policy_archive ORDER BY id DESC LIMIT 1"                # menu_revoke|home|t
SQL "SELECT operation, entity_table, entity_id = $RID, payload_after->>'revoked', payload_after->>'granted' FROM sys_operation_log ORDER BY id DESC LIMIT 1"   # update|sys_role|t|1|1
curl -s "$BASE/systemManage/updateRoleMenu" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"menuIds\":[11,16]}" | jq -c .data    # {"revoked":0,"granted":0,"effective":[11,16]}（空 diff 仍 Applied、稽核再一列）
curl -s "$BASE/systemManage/updateRoleMenu" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"menuIds\":[11,16,999999999]}" | jq -c .data.effective   # [11,16]（orphan skip）
echo $(( $(RELOAD) - R0 ))                                                                                             # 4（四次 Applied 各 +1、含空 diff＝授予面刻意例外）
SQL "SELECT v1, protected, created_by FROM casbin_rule WHERE v0='R_QS_AUTHZ' ORDER BY v1"                              # about|f|1 ／ user-center|f|1（受保護恆 FALSE、建立者＝Super uid）
```

停用選單不被撤銷（US1 AS5）與選單維受保護列可授可見性（US2 AS3）：

```bash
R5=$(RELOAD)
curl -s "$BASE/systemManage/addMenu" -H "$SUPER" -H "$J" -d '{"menuType":"2","menuName":"qs","routeName":"qs_authz","parentId":2}' | jq -r .code   # 0000
MID=$(SQL "SELECT id FROM sys_menu WHERE route_name='qs_authz' AND deleted_at IS NULL")
curl -s "$BASE/systemManage/updateRoleMenu" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"menuIds\":[11,16,$MID]}" | jq -c '.data|{revoked,granted}'   # {"revoked":0,"granted":1}
curl -s "$BASE/systemManage/updateMenu" -H "$SUPER" -H "$J" -d "{\"id\":$MID,\"status\":\"2\"}" | jq -r .code                                 # 0000（停用；不觸發同步）
curl -s "$BASE/systemManage/updateRoleMenu" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"menuIds\":[11,16,$MID]}" | jq -c '.data|{revoked,granted}'   # {"revoked":0,"granted":0}（停用≠撤銷）
curl -s "$BASE/systemManage/getRoleMenu?id=$RID" -H "$SUPER" | jq -c '[.data[].id]|sort'                                                      # [11,16,<MID>]（停用選單仍在現況讀端）
curl -s "$BASE/systemManage/updateRoleMenu" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"menuIds\":[11,16,$MID,4]}" | jq -c '.data|{revoked,granted}'  # {"revoked":0,"granted":1}（manage_role 不在封死射程）
SQL "SELECT protected FROM casbin_rule WHERE v0='R_QS_AUTHZ' AND v1='manage_role'"                                                             # f
echo $(( $(RELOAD) - R5 ))                                                                                                                      # 3（三次 updateRoleMenu Applied 各 +1；新增選單與停用選單各 0）
```

按鈕維與端點維（orphan skip、合法全撤、封死授予拒）：

```bash
curl -s "$BASE/systemManage/updateRoleButton" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"buttons\":[\"B_CODE1\",\"qs:none\",\"B_CODE1\"]}" | jq -c .data   # {"revoked":0,"granted":1,"effective":["B_CODE1"]}
curl -s "$BASE/systemManage/updateRoleButton" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"buttons\":[]}" | jq -c '.data|{revoked,granted}'               # {"revoked":1,"granted":0}（合法全撤；Q15）
SQL "SELECT archive_reason, v1 FROM sys_casbin_policy_archive ORDER BY id DESC LIMIT 1"                                                             # button_revoke|B_CODE1
E_OK='{"path":"/systemManage/getIpRuleList","method":"GET"}'
E_SEALED='{"path":"/systemManage/updateRoleEndpoints","method":"POST"}'
curl -s "$BASE/systemManage/updateRoleEndpoints" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"endpoints\":[$E_OK,{\"path\":\"/systemManage/updateUserSessionPolicy\",\"method\":\"POST\"},{\"path\":\"/systemManage/getIpRuleList\",\"method\":\"PUT\"}]}" | jq -c '.data|{revoked,granted,effective}'
                                                        # {"revoked":0,"granted":1,"effective":[{"path":"/systemManage/getIpRuleList","method":"GET"}]}（鍵序不計；未上線端點與白名單外方法皆略過）
R1=$(RELOAD)
curl -s "$BASE/systemManage/updateRoleEndpoints" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"endpoints\":[$E_OK,$E_SEALED]}" | jq -c '{code,msg,data}'   # {"code":"2222","msg":"biz.role.protectedGrant","data":null}
[ "$(RELOAD)" = "$R1" ] && echo no-sync                                                                                     # no-sync
SQL "SELECT count(*) FROM casbin_rule WHERE v0='R_QS_AUTHZ' AND v2 IN ('GET','POST','DELETE')"                             # 1（整批拒、零變更）
curl -s "$BASE/systemManage/updateRoleEndpoints" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"endpoints\":[]}" | jq -c '.data|{revoked,granted}'   # {"revoked":1,"granted":0}
SQL "SELECT archive_reason, v1, v2 FROM sys_casbin_policy_archive ORDER BY id DESC LIMIT 1"                                # endpoint_revoke|/systemManage/getIpRuleList|GET
R1B=$(RELOAD)
curl -s "$BASE/systemManage/updateRoleEndpoints" -H "$SUPER" -H "$J" -d 'x' | jq -r .msg                                    # biz.role.notFound（壞形 body 收斂、零變更）
for ep in updateRoleMenu updateRoleButton updateRoleEndpoints; do curl -s "$BASE/systemManage/$ep" -H "$SUPER" -H "$J" -d "{\"id\":$RID}" | jq -r .msg; done   # 三行 biz.role.notFound（期望集鍵缺席＝壞形、零變更；spec Clarifications 第七題）
curl -s "$BASE/systemManage/updateRoleMenu" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"menuId\":[1]}" | jq -r .msg   # biz.role.notFound（鍵名拼錯同屬壞形）
[ "$(RELOAD)" = "$R1B" ] && echo no-sync                                                                                    # no-sync
```

- 殘列演練（SC-009 前半；不可跳過）分兩面承載：①§9 首行之容器內全量測試排在 §10 `restore` 之前，屆時 dev 庫實有之走查殘列＝撤銷與連動歸檔列、自建角色（RID2）與自建選單（MID）——★R_QS_AUTHZ 之授權已於 §5 deleteRole 連動歸檔、本段不產生授 seed 角色之選單維殘授權，故此面不觸 BL-00136 形①→ 全綠（逾時一律放進容器內＝LL-00039）②形①（授 seed 角色於 seed 選單列之殘授權）之承重演練＝主線殘列演練（植列形與步驟＝`contracts/code-gates.md` §5.2；data-model §11），走查面同形＝§11（款 10 觀察後、`restore` 前之全量測試）。
- 候選誤用顯示域之兩種失效形（候選半誤用／映射半誤用，各三斷言）、同路徑雙鍵、併發兩寫端入域之 advisory 等待（FR-049）屬整合測試面（ADR-00066 決定 3、data-model 候選集與守門固定序），走查不構造；併發觀察指令見 RUNBOOK §11.1。

## 4. 受保護撤銷拒與結構性封死（US1 AS4／AS6、US2、SC-003／SC-004、FR-011、FR-021～FR-023）

本節不對 seed 角色寫入（spec Clarifications 第六題）：封死授予拒之走查面已於 §3 以自建角色 R_QS_AUTHZ 實證（`biz.role.protectedGrant`、零變更、零同步）；R_SUPER 原樣提交（`0000`、撤銷 0、新授 0、候選外 15 列不撤不授）、選單維與端點維之受保護撤銷拒（seed 受保護列皆屬 R_SUPER）與 R_ADMIN 之封死授予拒（名下列數仍 11）皆由整合測試承擔（tasks T027／T035／T037；真 seed app 面掛清理守衛）。走查面只做唯讀對讀：

```bash
curl -s "$BASE/systemManage/getRoleEndpoints?id=1" -H "$SUPER" | jq -c '[.data[]|select(.protected)]|length'   # 14（受保護端點列之讀端旗標）
SQL "SELECT count(*) FROM casbin_rule WHERE v0='R_SUPER' AND v2 IN ('GET','POST','DELETE')"                   # 50（含候選外 15 列〔含受保護之列 68〕）
SQL "SELECT count(*) FROM casbin_rule WHERE v0='R_ADMIN'"                                                     # 11（seed 原數）
```

- R_SUPER 標的豁免：wire 面之原樣提交由整合測試承擔（tasks T035）；真豁免（新授 ≥1 而不被封死腿擋）由 facade 層探針案承擔（ADR-00064 決定 8：非 R_SUPER 合成代碼名下直種受保護之合成探針鍵、先自證探針 ∈ 封死集且 R_SUPER 不持有，再以 R_SUPER 自授與非 R_SUPER 對照臂兩臂比對）。
- 按鈕維 seed 無受保護列 ⇒ 該維之受保護撤銷拒、先撤銷後授予之固定序（ADR-00064 決定 3）由整合測試以直種構造承擔。封死謂詞與守門之變異自證（拆守門或改謂詞 → 紅 → 還原 → 綠、紅證印 skipped=0）以單元紀錄為證。

## 5. 授權回收桶（US3 AS1～AS7、SC-007、FR-026～FR-032）

```bash
LIST() { curl -s "$BASE/systemManage/getArchivedPolicies?$1" -H "$SUPER"; }
LIST "roleCode=R_QS_AUTHZ" | jq -c '.data|{total,r:[.records[]|{dimension,v1,archiveReason,restorable,archivedBy}]}'
          # total 3；序＝endpoint（getIpRuleList、endpoint_revoke、true）→ button（B_CODE1、button_revoke、false）→ menu（home、menu_revoke、false）；archivedBy 皆 "Super"
LIST "roleCode=R_QS_AUTHZ&dimension=endpoint" | jq '.data.total'     # 1
LIST "roleCode=R_QS_AUTHZ&dimension=bogus" | jq '.data.total'        # 3（未知維度值靜默不濾）
LIST "roleCode=&dimension=menu" | jq '.data.total'                   # ≥1（空字串角色代碼＝忽略）
A_MENU=$(LIST "roleCode=R_QS_AUTHZ&dimension=menu" | jq '.data.records[0].id')
A1=$(LIST "roleCode=R_QS_AUTHZ&dimension=endpoint" | jq '.data.records[0].id')
R3=$(RELOAD)
curl -s "$BASE/systemManage/restorePolicy" -H "$SUPER" -H "$J" -d "{\"id\":$A_MENU}" | jq -r .msg      # biz.policy.notRestorable（第①腿；歸檔列保留）
curl -s "$BASE/systemManage/restorePolicy" -H "$SUPER" -H "$J" -d '{"id":999999999}' | jq -r .msg      # biz.policy.notRestorable（識別不存在）
curl -s "$BASE/systemManage/restorePolicy" -H "$SUPER" -H "$J" -d "{\"id\":$A1}" | jq -c '{code,data}' # {"code":"0000","data":null}（Applied）
echo $(( $(RELOAD) - R3 ))                                                                             # 1
SQL "SELECT id > 163, protected, created_by FROM casbin_rule WHERE v0='R_QS_AUTHZ' AND v1='/systemManage/getIpRuleList'"   # t|f|1（新 id、顯式 FALSE、建立者＝復原者）
SQL "SELECT count(*) FROM sys_casbin_policy_archive WHERE id = $A1"                                    # 0（歸檔列消費）
SQL "SELECT operation, entity_table, entity_id = $RID, payload_after->>'archive_id' = '$A1' FROM sys_operation_log ORDER BY id DESC LIMIT 1"   # restore|sys_role|t|t
```

NoOp（Q16）、第⑤腿停用不擋、第②腿同代碼新角色：

```bash
curl -s "$BASE/systemManage/updateRoleEndpoints" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"endpoints\":[]}" | jq -r .code        # 0000（再撤 → 歸檔列 A2）
curl -s "$BASE/systemManage/updateRoleEndpoints" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"endpoints\":[$E_OK]}" | jq -r .code    # 0000（重授 → 現役）
A2=$(LIST "roleCode=R_QS_AUTHZ&dimension=endpoint" | jq '.data.records[0].id')
LIST "roleCode=R_QS_AUTHZ&dimension=endpoint" | jq '.data.records[0].restorable'                                              # true（旗標不含「是否現役」腿）
LOG0=$(SQL "SELECT coalesce(max(id),0) FROM sys_operation_log"); R4=$(RELOAD)
curl -s "$BASE/systemManage/restorePolicy" -H "$SUPER" -H "$J" -d "{\"id\":$A2}" | jq -c '{code,data}'                        # {"code":"0000","data":null}（與 Applied 前端不可區分）
SQL "SELECT count(*) FROM sys_casbin_policy_archive WHERE id = $A2"                                                           # 0（仍消費移除）
SQL "SELECT count(*) FROM sys_operation_log WHERE id > $LOG0"                                                                 # 0（零稽核＝ADR-00068 款 12）
[ "$(RELOAD)" = "$R4" ] && echo no-sync                                                                                       # no-sync
SQL "SELECT count(*) FROM casbin_rule WHERE v0='R_QS_AUTHZ' AND v1='/systemManage/getIpRuleList'"                            # 1（不重複寫入）
curl -s "$BASE/systemManage/updateRoleEndpoints" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"endpoints\":[]}" | jq -r .code        # 0000（A3）
A3=$(LIST "roleCode=R_QS_AUTHZ&dimension=endpoint" | jq '.data.records[0].id')
R6=$(RELOAD)
curl -s "$BASE/systemManage/updateRole" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"status\":\"2\"}" | jq -r .code                 # 0000（停用自建角色）
curl -s "$BASE/systemManage/restorePolicy" -H "$SUPER" -H "$J" -d "{\"id\":$A3}" | jq -r .code                                # 0000（第⑤腿不擋＝Applied）
curl -s "$BASE/systemManage/updateRole" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"status\":\"1\"}" | jq -r .code                 # 0000
echo $(( $(RELOAD) - R6 ))                                                                                                    # 1（只 A3 復原 Applied；角色停用與啟用各 0）
curl -s "$BASE/systemManage/updateRoleEndpoints" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"endpoints\":[]}" | jq -r .code        # 0000（A4，來源角色 id＝RID）
A4=$(LIST "roleCode=R_QS_AUTHZ&dimension=endpoint" | jq '.data.records[0].id')
R7=$(RELOAD)
curl -s "$BASE/systemManage/deleteRole" -X DELETE -H "$SUPER" -H "$J" -d "{\"id\":$RID}" | jq -r .code                        # 0000（其餘現役列以 role_soft_delete 連動歸檔）
curl -s "$BASE/systemManage/addRole" -H "$SUPER" -H "$J" -d '{"roleCode":"R_QS_AUTHZ","roleName":"授權走查二"}' | jq -r .code   # 0000（同代碼新角色、id 不同）
echo $(( $(RELOAD) - R7 ))                                                                                                    # 1（deleteRole 實際歸檔 ≥1 列 +1；新增角色 0）
RID2=$(SQL "SELECT id FROM sys_role WHERE role_code='R_QS_AUTHZ' AND deleted_at IS NULL")
LIST "roleCode=R_QS_AUTHZ&dimension=endpoint" | jq -c "[.data.records[]|select(.id == $A4)|.restorable]"                      # [false]（第②腿：非同實例）
curl -s "$BASE/systemManage/restorePolicy" -H "$SUPER" -H "$J" -d "{\"id\":$A4}" | jq -r .msg                                 # biz.policy.notRestorable
SQL "SELECT count(*) FROM sys_casbin_policy_archive WHERE id = $A4"                                                           # 1（歸檔列保留）
LIST "roleCode=R_QS_AUTHZ&size=100" | jq -c '[.data.records[]|select(.archiveReason == "role_soft_delete")|.restorable]|unique'   # [false]
```

分頁（FR-008；與 005 刀分頁通則同式）：

```bash
ep=getArchivedPolicies
echo "$(curl -s "$BASE/systemManage/$ep" -H "$SUPER" | jq -c '.data|{current,size}') \
 $(curl -s "$BASE/systemManage/$ep?current=99999999&size=10" -H "$SUPER" | jq -c '.data|{current,n:(.records|length)}') \
 $(curl -s "$BASE/systemManage/$ep?size=0&current=0" -H "$SUPER" | jq -c '.data|{current,size}') \
 $(curl -s "$BASE/systemManage/$ep?size=abc" -H "$SUPER" | jq -c '.data|{current,size}')"   # {1,10}／{10000000,0}／{1,1}／{1,10}
```

自救路徑（Q14、US3 AS6、FR-032）由整合測試承擔、不入走查（spec Clarifications 第六題；tasks T053：真 seed app 面掛清理守衛——Super 撤 R_SUPER 名下 getRoleList〔seed 列 12〕→ getRoleList＝`5003` → 回收桶見該列 `restorable=true` → restorePolicy → `0000`；守衛 Drop 依原 id 原值回補 seed 列 12）。走查面只做唯讀對讀：

```bash
SQL "SELECT count(*) FROM casbin_rule WHERE protected AND id <= 163"                                     # 19（seed 受保護 19 列全在；授予與復原回插顯式 FALSE、管理介面永不寫此欄 ⇒ 任一受保護列被撤即降為 18）
```

- 受保護列經撤銷路徑進歸檔之案數恆零（SC-004）：走查面只以上列「seed 受保護 19 列仍在」對讀（授權歸檔表無受保護快照欄、自歸檔側 JOIN 現役之形於被撤後恆 0、正反皆綠，不得作證）；機器證由整合測試承擔（ADR-00064 決定 8 之「受保護列經撤銷路徑進歸檔之案數恆零」項）。

**預期**：可復原旗標與權威判定逐腿同判準（①～④；ADR-00065 決定 8）——第③腿（封死集標的而來源非 R_SUPER）與第④腿（端點已不在路由表）之列生產路徑產不出，由整合測試以直種歸檔列構造（ADR-00065 決定 11）；不入選單序列化域之機器證同屬整合測試面。

## 6. 判定面同步之可觀測面（SC-006、FR-017～FR-020）

以 `RELOAD`（`casbin_reload_total{outcome="ok"}`）前後差對讀上列各步（觸發矩陣＝data-model 觸發矩陣、ADR-00067 決定 1；不觸發集＝同 ADR 決定 3）：

| 寫端與結果 | ok 增量 | 本檔所在步（量測變數） |
|---|---|---|
| 三維寫端 Applied（含空 diff、含 orphan skip 後為空 diff） | +1／次 | §3（`R0`、`R5`） |
| 三維寫端 Rejected（`protectedRevoke`／`protectedGrant`）、查無角色（含 body 缺席或壞形） | 0 | §1（`RQ`）、§3（`R1`、`R1B`） |
| restorePolicy Applied | +1 | §5（`R3`、`R6`） |
| restorePolicy NoOp／NotRestorable | 0 | §5（`R4`、`R3`）、§1（`RQ`） |
| 移除面（deleteRole 實際歸檔 ≥1 列） | +1 | §5 第②腿（`R7`） |
| 選單停用、角色停用與啟用、新增角色或選單 | 0 | §3（`R5`：新增與停用選單）、§5（`R6`：角色停用與啟用；`R7`：新增角色） |

- API 判定即時生效與失效＝整合測試面（tasks T052 之單一判定進入點雙斷言、T053 自救路徑之 `5003`→`0000`；走查無帳號持有自建角色、不另觀察）；`retry`／`exhausted` 照舊為 0（`curl -s http://127.0.0.1:32079/metrics | grep '^casbin_reload_total'`；RUNBOOK §11.2）。
- 兩窗（commit→換上之有界過渡窗、重試耗盡窗）單一操作者走查觀察不到（發起者收到回應時同步已結束；ADR-00067 後果）；失敗注入下舊面續放行 R_SUPER、授予面與復原之收場取消安全屬整合測試面。

## 7. 角色首頁（spec Clarifications 第三題之後端面）

```bash
curl -s "$BASE/systemManage/updateRoleHome" -H "$SUPER" -H "$J" -d "{\"id\":$RID2,\"home\":\"about\"}" | jq -r .code   # 0000
curl -s "$BASE/systemManage/getRoleHome?id=$RID2" -H "$SUPER" | jq -c .data                                         # {"home":"about"}
curl -s "$BASE/systemManage/updateRoleHome" -H "$SUPER" -H "$J" -d "{\"id\":$RID2,\"home\":null}" | jq -r .code      # 0000（清空）
curl -s "$BASE/systemManage/getRoleHome?id=$RID2" -H "$SUPER" | jq -c .data                                         # {"home":null}
SQL "SELECT count(*) FROM sys_operation_log WHERE operation='update' AND entity_table='sys_role' AND entity_id = $RID2"   # 2（每次寫入各一列）
```

## 8. UI 走查：CDP 三方對照（SC-010／FR-053、US4、ADR-00070 決定 5）

一律派 opus[1m]／xhigh agent 以 CDP 接 `127.0.0.1:9229`（host 瀏覽器以 `--remote-debugging-port=9229` 起；driver＝`tools/orchestration/cdp.mjs`、走查腳本落不入版控之工作區），開分頁對照 22080（rev5 HEAD）vs 32080（rev6）、必要時加 22089（upstream example）；rev5 對照 stack 起法＝CLAUDE.md §7。CDP 基準本刀重取、不沿用 005 刀產出；判準＝結構清單逐項全等、任一不等即紅，間距／字體／顏色只記走查紀錄。★兩側寫入一律對各自之自建角色（例 `R_QS_CDP`）；22080 側絕不對 seed 角色寫入（rev5 stack 不動 seed＝CLAUDE.md §6／§7）、其自建殘列依 rev5 自家 `docs/ops/RUNBOOK.md` 之 CDP 走查還原契約處置（該工具之基準檔路徑引數一律指 rev5 樹外＝CLAUDE.md §6 絕不寫入 rev5 樹）；以 R_SUPER 開彈窗只觀察、按取消。

| 面 | 操作 → 預期 |
|---|---|
| 角色抽屜 | Super 編輯任一角色 → 編輯態三鈕（選單權限／按鈕權限／端點權限；22089 只兩鈕＝錨點）、三鈕無按鈕碼 gating；角色頁主檔零 diff（§9 機器證） |
| 選單權限彈窗 | 樹＝治理域（含已停用之自建選單）、勾選＝現況讀端、以 R_SUPER 開啟見受保護四項不可取消；無父子連動（勾目錄不連帶子項）；確定只發 updateRoleMenu（期望全集）、成功後重開回讀一致 |
| 首頁下拉（spec Clarifications 第三題） | 選項＝getAllPages（顯示域）、現值＝getRoleHome（NULL 誠實顯空）；對自建角色選值 → 當下發 updateRoleHome（網路請求事件）、與確定鈕獨立；按取消後重開顯新值（不還原）；連選兩次 → 兩列稽核（§7 SQL 形）；清空 → body `home` 為 null |
| 按鈕權限彈窗 | demo 假資料消失；候選＝getAllButtons（20 碼）、勾選＝getRoleButton；確定發 updateRoleButton；seed 零受保護按鈕列 ⇒ 鎖定形無可觀察實例、以唯讀計數為反證紀錄（RL-0033：`SQL "SELECT count(*) FROM casbin_rule WHERE protected AND v2='button'"`＝0） |
| 端點權限彈窗（新檔） | ★候選集兩側不同：22080（rev5 HEAD）getAllEndpoints 回 50 項、32080 回 35 項——多出之 15 支皆 `rev5:007`／`rev5:008` 之使用者與稽核路由（逐支＝`contracts/wire-authz-governance.md`「與 rev5 wire 逐欄比對」getAllEndpoints 列）⇒ 樹之葉數 50 對 35、以 R_ADMIN 開啟時 22080 多一顆已勾之 getUserList 葉；兩側之比對面＝扣除該 15 支後之結構逐項全等（排除依據見下方排除清單條）；候選依路徑群組（群組鍵＝純路徑）、葉＝路徑×方法；勾群組＝勾其全部未鎖葉、updateRoleEndpoints 之 `endpoints` 只含葉；候選側不預標受保護；為自建角色勾 `POST /systemManage/updateRoleEndpoints` 並確定 → 請求發出、共用攔截層顯 `biz.role.protectedGrant` 之純 key toast、無明細表；以 R_SUPER 開啟（只觀察、按取消）見受保護 14 葉鎖定不可取消、反勾其所屬群組再勾回時鎖定葉維持勾選 |
| 三彈窗共同守衛（FR-034；spec Clarifications 第四題） | CDP 攔截現況讀端使之失敗 → 確定鈕維持停用（只能取消重開）；延遲前一角色之現況讀、其間改開另一角色 → 遲到回應被丟棄（`rev5:B-116` 形）；切換角色 → 前一角色之勾選、鎖定集、首頁值清空；候選讀每次開啟皆發、攔截使之失敗 → 保留上次候選值（`rev5:B-129` 形）。受保護撤銷拒經 UI 不可達（鎖定雙保險）＝其拒因由 §4 與整合測試承擔 |
| 角色抽屜狀態欄（ADR-00070 決定 1） | 32080 單邊：只改名稱送出 → updateRole body 無 `status` 鍵；改狀態送出 → 帶 `status`＝新選值 |
| 授權回收桶頁 | 所需歸檔列＝本段先以自建角色經三彈窗撤銷產生（端點維撤銷＝可復原列、選單維／按鈕維撤銷＝不可復原列；兩側各自建、不跑 §1～§7）；側欄「系統管理」下現該項（seed 選單列 10、圖示 `mdi:recycle`、標題為譯文、選單管理清單之該列亦不顯路由裸鍵）；表格 8 欄（序號／來源角色／維度／標的／歸檔原因／歸檔時間／歸檔者／操作）；列序＝歸檔時間降冪再 id 降冪；查詢列＝角色代碼（文字）×維度（下拉、可清空）；分頁；可復原＝false 之列復原鈕停用；可復原列 → 二次確認 → 成功 → 重取列表；二次確認與復原成功 toast 文案兩側全等；兩語切換無裸鍵 |

- 排除清單（SC-010）＝spec 刻意分岔登記表各列（★登記表於 CDP 開跑前凍結；CDP 中新發現者須經 user 親決入表、否則判紅；角色抽屜送出狀態欄、刪除角色後之判定面同步、已知降級窗之條文、三維現況讀端之回應集、端點候選集、實作期新發現者）＋ADR-00068 各款＋008 刀兩頁死項（system-settings／audit；ADR-00068 款 2／款 6）＋請求次數維度；端點候選集之 15 支後刀路由差（上表端點權限彈窗列）＝該表「端點候選集」列。
- 已知態各款之本段觀察：ADR-00068 款 2／5～8／11～13／15 與候選丙於本段以「觀察路徑→症狀」實測（觀察標的取自建角色與自建選單、不需 seed 寫入）；需 seed 帳號持被改角色之款 3／4／9／10／14／16 與候選甲／乙＝§11（ADR-00068 決定 4①）。
- 已知態候選（ADR-00068 決定 3）：候選丙（兩分頁下抽屜三欄舊值覆寫）＝上條本段實測；候選甲、乙＝§11；候選丁以既有整合測試 `rust-api/server/src/handler/role.rs` 測試模組之 `disable_guards_refuse_self_role_before_super_and_count_disabled_memberships` 為觀察記錄。各候選記「觀察路徑→症狀」、交治理單元由 user 定案。

## 9. 治理與工具（SC-008／SC-011～SC-013、FR-042～FR-044、FR-054）

```bash
dc exec -T rust-api cargo test --workspace -- --test-threads=1   # 全綠（contract 49 case、新三鍵實發點、名冊閘、觸發矩陣特性測、守衛兩族補回自證）；★此時 dev 庫帶本段走查殘列（撤銷與連動歸檔列、自建角色與選單；不含授 seed 角色之選單維殘授權＝§3 末條）＝SC-009 前半之走查殘列面、不可跳過、MUST 排在 §10 restore 之前；BL-00136 形①之承重演練＝contracts/code-gates.md §5.2（主線殘列演練）與 §11
dc exec -T base-web pnpm typecheck                               # rc 0（兩語 locale 皆受 app.d.ts 之 Schema 型約束＝鍵集相等）
python3 tools/docsync check && python3 tools/docsync lint && python3 tools/docsync test   # 零紅（docsync 自測含 routes 釘值 49 列）
python3 tools/msg-key-gate.py check                              # rc 0（MSG_KEYS 46 ⇔ 三檔 locale backend 子樹逐檔雙向全等）
python3 tools/wire-schema.py check && python3 tools/view-render-guard.py check && python3 tools/route-artifact-gate.py check && python3 tools/rust-fmt-gate.py check && python3 tools/entity-drift-gate.py check   # 皆 rc 0（容器依賴者未起＝具名跳過，收刀前須在起態跑；碼面閘表全員＝RUNBOOK §12，schema-gate 見 §10、fork-delta-lint 與 seed-view-gate 見下）
git -C rust-api ls-tree --name-only HEAD migration/src/ | grep -c '/m0'   # 2（零 migration）
git -C base-web diff --quiet 2248b89 HEAD -- src/views/manage/role/index.vue && echo untouched   # untouched（角色頁主檔一行不動；2248b89＝本刀起手 pin）
grep -n '^\*\*Version\*\*' .specify/memory/constitution.md       # 1.7.0；收刀前 PATCH 實數化範圍欄後為 1.7.x
```

fork-delta-lint（含範圍欄對賬腿＝本刀新腿；spec FR-042、`contracts/code-gates.md` §2.1）一正一反（RL-0080；`--constitution` 只供自身變異驗證）：

```bash
python3 tools/fork-delta-lint.py                                 # 正：rc 0（self-test＋全掃＋對賬腿；修改型只在授權三元組）
C=<憲法副本路徑（不入版控之工作區）>
cp .specify/memory/constitution.md "$C"
#   反①：副本 §III.2 (ii) 列片段 `src/views/manage/role/index.vue`（6 處修改型＋2 塊新增型） 之「6 處」改「7 處」（片段與憲法現文逐字相同、grep -c＝1）
python3 tools/fork-delta-lint.py --constitution "$C"             # rc 1、指名（軌道, 用途, 檔, 注記值, 實數）＝該檔 (ii) 修改型實數≠範圍欄
cp .specify/memory/constitution.md "$C"                          # 反②前重取副本（兩發單獨跑、不疊加＝RL-0005）
#   反②：副本 (iii) 列範圍欄任一反引號路徑之「反引號內」字面改為不含 / 之非路徑 token（例 menu-auth）；拔反引號形只會令該檔靜默掉出名冊、不 die，不得作自證
python3 tools/fork-delta-lint.py --constitution "$C"             # rc 2、指名「範圍欄抽出殘渣／非路徑 token」（load_roster 路徑形斷言 die；同形＝contracts/code-gates.md §1.1 名冊載入變異自證，(iv) 列同形另跑一發）
rm "$C"
```

base-web 變更檔集（SC-011、FR-039；fork-delta-lint 不做檔集斷言——判準與允許集＝`contracts/code-gates.md` §1.4，本檔不重抄）：

```bash
for f in $(git -C base-web diff --name-only --diff-filter=M 2248b89..HEAD); do git -C base-web cat-file -e 8be6f9ba:"$f" 2>/dev/null && echo "$f"; done   # 輸出 ⊆ code-gates §1.2 之 12 檔（upstream 基線不存在之檔＝新增檔、不列）
git -C base-web diff --name-only --diff-filter=A 2248b89..HEAD    # 恰 code-gates §1.3 五檔
git -C base-web diff --name-only --diff-filter=DR 2248b89..HEAD   # 空
```

- 新增圈界塊「拔標記必紅」（SC-011、FR-037）：各塊之紅證以落地單元紀錄為證（塊名冊與做法＝`contracts/code-gates.md` §1.5）；走查時可任取一塊重跑——暫拔其 START／END 標記 → `python3 tools/fork-delta-lint.py` 紅（報未圈界新增）→ 以存原文寫回（RL-0019）→ `git -C base-web status --porcelain` 回基準（逐塊單獨跑、不疊加＝RL-0005；不與 CDP 走查並行）。

seed-view-gate（本刀新建碼面閘；ADR-00071 決定 1）一正一反（ADR-00071 決定 2／決定 4／決定 7；逐步命令形＝`contracts/code-gates.md` §2.2）：

```bash
python3 tools/seed-view-gate.py check    # 正：rc 0、輸出列具名豁免恰兩鍵 view.manage_system-settings／view.manage_audit（附 BL-00045）
python3 tools/seed-view-gate.py test     # rc 0（合成反例：缺 view 紅、豁免到期紅、幽靈豁免紅、導出≠imports.ts 兩向紅、空集 rc 2、豁免表恆定）
```

- 反（真檔暫改、不與 CDP 走查並行）：先 `dc stop base-web`（免路由外掛隨暫移重算產物四檔）→ 暫移 `base-web/src/views/manage/policy-archive/` → `check` rc 1、指名 `view.manage_policy-archive` 與 sys_menu 列 10，並報導出集≠imports.ts → 原檔寫回 → `git -C base-web status --porcelain` 回基準 → `dc start base-web` → 再以 `git -C base-web status --porcelain` 與 `python3 tools/route-artifact-gate.py check` 復核回基準。
- 憲法 Amendment 先行（SC-012）：`B0=$(git merge-base rev6-admin-root HEAD)` → `git log --format='%h %s' "$B0"..HEAD -- .specify/memory/constitution.md` 見 1.6.0→1.7.0 之 Amendment 顆（另見收刀前 PATCH 顆）→ 機器斷言＝`git ls-tree <Amendment 顆> base-web` 之 gitlink＝`2248b89`（`contracts/code-gates.md` §1.1；比「只准新增檔」嚴——本刀單元序使純新增檔亦落在 Amendment 之後）。
- ADR：plan 期九支（ADR-00063～ADR-00071）＋收刀前 PATCH ADR 一支（配號待定）於收刀前皆 `status: accepted`、ADR-00045／ADR-00046 轉 superseded（續行 ADR accepted 同顆）；親決時點＝research 之「ADR 配號與親決時點表」。
- 現在式假述掃除（SC-014、FR-047）：以 `python3 tools/docsync errata <詞>` 逐詞現量（種子例：「三十九」「四十三」「十七支」「三值」「八域」「唯一已知降級窗」「授權治理島」「十一支對十二張表」「七款」「只由移除面寫端觸發」「限 `R_SUPER`」；「四十三」＝MSG_KEYS 43→46、「三值」＝不可復原集 3→5、「八域」＝handler 域數，與阿拉伯數字形並掃）、命中只餘史料面、accepted ADR body 與事件源；處數以現量為準、不寫死。
- `bash tools/bootstrap.sh`（舊機重跑＝純體檢；含新閘自測之名冊推導）rc 0。

## 10. 收尾

```bash
python3 tools/walkthrough-baseline.py restore "$WB"   # rc 0；輸出含「MUST 重啟 rust-api」（刪復原回插之新 id 列與自建角色／選單／歸檔列、序列回基準；本段不撤 seed 列——seed 列回補之走查面只在 §11 觀察窗）
dc restart rust-api                                    # 動過 casbin_rule 即重啟
python3 tools/walkthrough-baseline.py diff "$WB"      # rc 0（SC-009 後半）
python3 tools/schema-gate.py check                    # rc 0（gate2 逐列比對 seed）
```

- 手上無走查前基準檔者改跑 `python3 tools/walkthrough-baseline.py restore --seed`（以凍結 seed 之 casbin_rule 列回補）＋重啟＋`schema-gate.py check`（RUNBOOK §9c 第 3～4 步）。

## 11. 已知態觀察（seed 角色寫入之具名例外；spec Clarifications 第五題、ADR-00068 決定 4）

只有 ADR-00068 各款之觀察路徑得對 seed 角色（R_ADMIN／R_USER_COMMON）寫入並以 seed 帳號（Admin／User）登入觀察；Clarifications 第五題之例外不及 R_SUPER——本檔對 R_SUPER 零寫入（原樣提交與自救路徑皆由整合測試承擔＝spec Clarifications 第六題）。本段自成一顆基準、排在 §10 收尾之後（基準檔模式只服務清理面為空之基準＝RUNBOOK §9c 安全帶，故不在主走查中途另取）：

```bash
WB_OBS=<已知態觀察用基準檔路徑（不入版控之工作區）>
python3 tools/walkthrough-baseline.py snapshot "$WB_OBS"   # 觀察前；rc 0
#   依 ADR-00068 款 3／4／9／10／14／16 與候選甲／乙（需 seed 帳號持被改角色＝ADR-00068 決定 4①）之觀察路徑以 CDP 實際操作（款 9 逐支效果、款 10 逐頁實況以其表列為準）；
#   其餘各款與候選丙已於 §8 實測、不在本段；純後端面（直打端點之放行或 5003、稽核列數、同步計數）並以整合測試觀察
dc exec -T rust-api cargo test --workspace -- --test-threads=1   # 全綠＝BL-00136 形①之走查面（款 10 觀察授 R_ADMIN 可見受保護選單列後、restore 前跑；該授予不在觀察內撤回、交 restore 清 ⇒ 此時 dev 庫帶授 seed 角色於 seed 選單列之殘授權）
python3 tools/walkthrough-baseline.py restore "$WB_OBS"    # 回補被撤之 seed 授權列、刪上界以上之新 id 列（含復原回插者與款 10 之授予）、角色列可變欄（首頁、狀態、名稱、描述、備註、updated_at／updated_by；射程含 seed 三列）回寫基準值
dc restart rust-api
python3 tools/walkthrough-baseline.py diff "$WB_OBS"       # rc 0
python3 tools/schema-gate.py check                         # rc 0（款 16 改過 seed 角色狀態與審計欄者必跑）
```

- 每款記「觀察路徑→症狀」（`rev5:L-046`：推論不得代替觀察）；新發現之已知態併入 ADR-00068 草稿，候選四款與 ADR-00070 後果之對應引用由治理單元 user 逐款定案（ADR-00068 決定 3）。
