# Quickstart — 005-role-menu-crud（驗證指南）

> 目的＝以 dev stack 端到端證明本刀可用（SC-001／SC-003～SC-008／SC-011／SC-015 之走查面）；不含實作碼。承 `rev5:005` quickstart 形、rev6 座標。★一律指向 rev6 stack（UI 32080／API 經 front-nginx 32080 之 `/api`／PG 35432）、絕不指向 rev5 對照 stack（2xxxx）。前置＝Amendment accepted、全部單元合入、容器內全量測試綠。
> ★寫入步驟一律對**走查自建**之角色與選單（seed 列只讀）；動過 `casbin_rule` 之還原後 MUST 重啟 rust-api（判定面無外部通知管道）。端點行為之逐欄定義見 `contracts/wire-role-admin.md`／`contracts/wire-menu-admin.md`，本檔不重述。

## 0. 前置

```bash
cd <rev6 workspace 根>
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait
BASE=http://127.0.0.1:32080/api
PG='docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres'
SQL() { $PG sh -lc "psql -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" -At -c \"$1\""; }
WB=<走查基準檔路徑（不入版控之工作區）>
python3 tools/walkthrough-baseline.py snapshot "$WB"          # rc 0（RUNBOOK §9c 第 1 步）
login() { curl -s "$BASE/auth/login" -H 'content-type: application/json' \
  -d "{\"userName\":\"$1\",\"password\":\"123456\"}" | jq -r .data.token; }
SUPER="authorization: Bearer $(login Super)"; ADMIN="authorization: Bearer $(login Admin)"; USER="authorization: Bearer $(login User)"
```

★勿秒內狂打 auth 端點（nginx `auth_limit`）。

## 1. 路由與授權態（US1／SC-001）

```bash
curl -s "$BASE/systemManage/getRoleList" -H "$ADMIN" | jq -r .code                  # 0000（R_ADMIN 授權）
curl -s "$BASE/systemManage/addRole" -H "$ADMIN" -H 'content-type: application/json' -d '{}' | jq -r .code   # 5003
curl -s "$BASE/systemManage/getAllRoles" -H "$USER" | jq -c '.data[0]|keys'          # ["id","roleCode","roleName"]
curl -s "$BASE/systemManage/getMenuList/v2" -H "$ADMIN" -o /dev/null -w '%{http_code}\n'   # 403
```

## 2. 角色生命週期（US1／SC-003）

```bash
J='content-type: application/json'
curl -s "$BASE/systemManage/addRole" -H "$SUPER" -H "$J" -d '{"roleCode":"R_QS_A","roleName":"走查角色","roleMemo":"qs"}' | jq -r .code   # 0000
curl -s "$BASE/systemManage/addRole" -H "$SUPER" -H "$J" -d '{"roleCode":"R_QS_A","roleName":"x"}' | jq -r .msg     # biz.role.codeExists
curl -s "$BASE/systemManage/addRole" -H "$SUPER" -H "$J" -d '{"roleCode":"bad code","roleName":"x"}' | jq -r .msg  # biz.role.codeInvalid
curl -s "$BASE/systemManage/addRole" -H "$SUPER" -H "$J" -d '{"roleCode":"R_QS_B","roleName":""}' | jq -r .msg      # biz.role.nameRequired
RID=$(SQL "SELECT id FROM sys_role WHERE role_code='R_QS_A' AND deleted_at IS NULL")
curl -s "$BASE/systemManage/updateRole" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"roleMemo\":\"\"}" | jq -r .code         # 0000；role_memo 落 NULL
curl -s "$BASE/systemManage/updateRole" -H "$SUPER" -H "$J" -d "{\"id\":$RID,\"roleCode\":\"R_QS_A\"}" | jq -r .msg    # biz.role.codeImmutable
curl -s "$BASE/systemManage/updateRole" -H "$SUPER" -H "$J" -d '{"id":1,"status":"2"}' | jq -r .msg                  # biz.role.cannotDisableSelfRole（self→super 固定序）
curl -s "$BASE/systemManage/deleteRole" -X DELETE -H "$SUPER" -H "$J" -d '{"id":2}' | jq -r .msg                      # biz.role.seededProtected
curl -s "$BASE/systemManage/batchDeleteRole" -X DELETE -H "$SUPER" -H "$J" -d "{\"ids\":[$RID,999999999]}" | jq -r .msg   # biz.role.notFound（整批拒、零變更）
curl -s "$BASE/systemManage/deleteRole" -X DELETE -H "$SUPER" -H "$J" -d "{\"id\":$RID}" | jq -r .code                # 0000
SQL "SELECT operation, entity_table FROM sys_operation_log ORDER BY id DESC LIMIT 3"   # delete/update/add 各一、entity_table=sys_role
```

**預期**：每筆成功寫入恰一列稽核；被拒者零列；`getRoleList` 列帶 `roleMemo`／`roleHome`、不帶軟刪欄。

## 3. 選單樹與寫端（US2／SC-004）

```bash
curl -s "$BASE/systemManage/getMenuList/v2" -H "$SUPER" | jq -c '.data|{current,size,total}'   # {"current":1,"size":11,"total":11}（seed）
curl -s "$BASE/systemManage/getMenuTree" -H "$SUPER" | jq -c '[.data[0],.data[1]]|map(keys)'   # [["id","label","pId"],["children","id","label","pId"]]（home 為葉、children 缺席；manage 帶子項）
curl -s "$BASE/systemManage/getAllPages" -H "$SUPER" | jq '.data|length'                        # 78
curl -s "$BASE/systemManage/addMenu" -H "$SUPER" -H "$J" -d '{"menuType":"2","menuName":"qs","routeName":"qs_menu","parentId":2,"href":"javascript:alert(1)"}' | jq -r .msg   # biz.menu.hrefInvalid
curl -s "$BASE/systemManage/addMenu" -H "$SUPER" -H "$J" -d '{"menuType":"2","menuName":"qs","routeName":"qs_menu","parentId":2,"buttons":[{"code":"qs:a"},{"code":"qs:a"}]}' | jq -r .msg   # biz.menu.buttonsInvalid
curl -s "$BASE/systemManage/addMenu" -H "$SUPER" -H "$J" -d '{"menuType":"2","menuName":"qs","routeName":"login","constant":true}' | jq -r .msg   # biz.menu.routeNameExists（保留路由名；ADR-00044 決定 8）
curl -s "$BASE/systemManage/addMenu" -H "$SUPER" -H "$J" -d '{"menuType":"2","menuName":"qs","routeName":"qs_menu","parentId":2,"buttons":[{"code":"qs:a","desc":"a"},{"code":"qs:b","desc":"b"}]}' | jq -r .code   # 0000
curl -s "$BASE/systemManage/updateMenu" -H "$SUPER" -H "$J" -d '{"id":5,"status":"2"}' | jq -r .msg          # biz.menu.protectedMenu（停用受保護列）
curl -s "$BASE/systemManage/updateMenu" -H "$SUPER" -H "$J" -d '{"id":5,"parentId":0}' | jq -r .msg          # biz.menu.protectedMenu（改父）
curl -s "$BASE/systemManage/deleteMenu" -X DELETE -H "$SUPER" -H "$J" -d '{"id":2}' | jq -r .msg              # biz.menu.protectedMenu
```

★受保護列「同值 `parentId` 放行、其餘欄照常可編」之正向腿若打 seed 列會留寫痕（走查還原面不還原 seed 列之更新）⇒ 由契約測試以守衛植入之自建 `protected=TRUE` 列承擔、走查不做。

## 4. 移除面：歸檔＋判定面同步（US4／SC-006／SC-007）

```bash
MID=$(SQL "SELECT id FROM sys_menu WHERE route_name='qs_menu' AND deleted_at IS NULL")
# 對自建選單植 R_ADMIN 之按鈕維政策（顯式大 id；本步植入列由 §10 restore 清除——未 restore 前勿跑容器測試），重啟使判定面持有
SQL "INSERT INTO casbin_rule (id, ptype, v0, v1, v2, v3, v4, v5) VALUES (9300005001,'p','R_ADMIN','qs:a','button','','',''),(9300005002,'p','R_ADMIN','qs_menu','menu','','','')"
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart rust-api
ADMIN="authorization: Bearer $(login Admin)"
curl -s "$BASE/auth/getUserInfo" -H "$ADMIN" | jq -c '.data.buttons|index("qs:a")'     # 非 null（刪前先證命中）
curl -s "$BASE/systemManage/updateMenu" -H "$SUPER" -H "$J" -d "{\"id\":$MID,\"buttons\":[{\"code\":\"qs:b\",\"desc\":\"b\"}]}" | jq -r .code   # 0000
SQL "SELECT archive_reason, v1 FROM sys_casbin_policy_archive ORDER BY id DESC LIMIT 1"   # menu_button_removed|qs:a
curl -s "$BASE/auth/getUserInfo" -H "$ADMIN" | jq -c '.data.buttons|index("qs:a")'     # null（未重啟即失效）
curl -s http://127.0.0.1:32079/metrics | grep '^casbin_reload_total'                     # outcome="ok" 增 1
curl -s "$BASE/systemManage/deleteMenu" -X DELETE -H "$SUPER" -H "$J" -d "{\"id\":$MID}" | jq -r .code   # 0000；menu 維 R_ADMIN 列 menu_soft_delete 歸檔、再同步一次
```

**預期**：資料庫面（`casbin_rule` 零殘留、歸檔列 reason 正確、`role_id` 回填 R_ADMIN 之 id）與判定面（未重啟即失效）雙成立；零政策列之刪除不增 `casbin_reload_total`。

## 5. 選單回收桶（US3）

```bash
curl -s "$BASE/systemManage/getDeletedMenus?current=1&size=10" -H "$SUPER" | jq -c '.data.records[0]|{routeName,deleted}'   # qs_menu / true
curl -s "$BASE/systemManage/restoreMenu" -H "$SUPER" -H "$J" -d "{\"id\":$MID}" | jq -r .code          # 0000；原 status 保留
curl -s "$BASE/systemManage/restoreMenu" -H "$SUPER" -H "$J" -d "{\"id\":$MID}" | jq -r .msg           # biz.menu.notFound（現役列不冪等）
SQL "SELECT count(*) FROM casbin_rule WHERE v1 IN ('qs_menu','qs:a','qs:b')"                               # 0（復原不回灌）
```

## 6. 常量選單端到端（FR-021）

以 Super 建一支頂層常量選單（`constant: true`、`parentId: 0`）→ 登出狀態下 `curl -s "$BASE/route/getConstantRoutes" | jq '.data|length'` ≥1、該列可見、內建路由仍在、路由可達 → 刪除之 → 回 `[]`。

## 7. 分頁共用規則（FR-054～FR-056／SC-008）

```bash
for ep in getRoleList getDeletedMenus getIpRuleList getMenuList/v2; do
  echo "$ep: $(curl -s "$BASE/systemManage/$ep" -H "$SUPER" | jq -c '.data|{current,size}') \
 $(curl -s "$BASE/systemManage/$ep?current=99999999&size=10" -H "$SUPER" | jq -c '.data|{current,n:(.records|length)}') \
 $(curl -s "$BASE/systemManage/$ep?size=0&current=0" -H "$SUPER" | jq -c '.data|{current,size}') \
 $(curl -s "$BASE/systemManage/$ep?size=abc" -H "$SUPER" | jq -c '.data|{current,size}')"
done
```

**預期**：三支通則端點＝`{1,10}`／`{10000000,0}`／`{1,1}`／`{1,10}`；getMenuList/v2 之缺席與壞形＝`{1,11}`（全取）、其餘同通則；IP 規則清單回應逐位元同改前。

## 8. 角色首頁（US5）

```bash
curl -s "$BASE/systemManage/getRoleHome?id=3" -H "$SUPER" | jq -c .data                 # {"home":"home"}
curl -s "$BASE/systemManage/getRoleHome" -H "$SUPER" | jq -r .msg                         # biz.role.notFound（id 缺席）
```

寫入以自建角色驗（`updateRoleHome` → 讀回新值 → 送 `""` → 讀回 `null`；稽核各一列）。

## 9. UI 走查（CDP 三方對照；判準＝spec SC-011）

一律派 opus agent 以 CDP 接 `127.0.0.1:9229`、開分頁對照 22080（rev5）vs 32080（rev6）、必要時加 22089（upstream example）：角色頁（列表／搜尋／新增／編輯〔代碼鎖定〕／刪除／批刪／備註）、選單頁（樹表全取＋分頁列凍結／父選擇器三模式首項頂層／頁面下拉／回收桶開關換源與清勾選與 pageSize 歸位／復原／備註／已刪模式無寫入口）、ip-rule 頁表頭 prop 形零差異、user 與 role 頁表頭對 22089 新增批刪鈕仍在、ADR-00045 已知態各款以「觀察路徑→症狀」實際操作觀察；拒因步驟挑前端不先擋之守門並以網路請求事件證請求發出；編輯請求 body 以網路請求事件斷言不含不可變欄。

## 10. 收尾

```bash
python3 tools/walkthrough-baseline.py restore "$WB"        # 擴面後含角色／選單／授權／歸檔／指派五表
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart rust-api   # 動過 casbin_rule 即重啟
python3 tools/walkthrough-baseline.py diff "$WB"           # rc 0
```
