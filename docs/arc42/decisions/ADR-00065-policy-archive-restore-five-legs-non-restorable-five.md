---
id: "ADR-00065"
title: 授權回收桶復原——不可復原集 3→5（可復原恰 `endpoint_revoke`、零 migration）、鎖內固定序五腿（原因→同實例→封死→端點在路由表→停用不擋）、以歸檔來源角色 id 鎖角色列之等價改形、NoOp 消費歸檔列且零稽核、可復原旗標＝①～④ 同判準、回收桶只篩角色代碼與維度、不設 23505 收窄；ADR-00044 決定 4 復核結論＝選單維仍無可復原原因
date: 2026-10-01
status: proposed
supersedes: []
superseded_by: []
provenance: "006-authz-governance 之 spec FR-026～FR-032（US3 AS1～AS7、SC-006～SC-007、Edge Cases「授權回收桶」段）、FR-004（純 key）、FR-006（稽核同交易、操作者先於守門）、FR-007（body 壞形收斂）、FR-012（撤銷原因三值）、FR-017（復原 Applied 觸發同步）、FR-041③（ADR-00044 決定 4 之復核結論）、FR-050；spec Clarifications 2026-10-01 首題（復原 NoOp 照 rev5 零稽核）；brainstorm §0 Q2（手動撤銷之選單／按鈕維不可復原）／Q16（復原撞現役＝NoOp、旗標不加現役腿）／Q17（回收桶只篩角色代碼與維度）、§2 BL-00047 反向確認；plan 期主線工程判斷（以歸檔來源角色 id 鎖讀角色列之等價改形、不另設 23505 收窄、端點在路由表之判準取新建 `router::policy_endpoints()`、可復原旗標②半之代碼批次讀端＝新建 `sys_role::active_ids_by_codes`）；藍本＝rev5:ADR 0055（§1 復核結論 B／§2 reason gate 五值／§3 鎖內固定序五腿與三態／§4 腿與現役寫端守門對照／§5 restorable 逐腿同判準）與其 as-built rev5:server/src/model/facade/sys_casbin_archive.rs 之 `restore`／`restore_locked`／`list`、rev5:server/src/handler/policy_archive.rs 之 `restore_policy`／`get_archived_policies`——其以代碼鎖讀角色列之形改為以歸檔 role_id 鎖讀（決定 4）、其 23505 收窄為不可復原之形不帶（決定 10）、facade 自開交易之形不帶（handler 持交易）；被復核者＝ADR-00044 決定 4（授權歸檔表三自由度 won't-use 與翻案觸發條款）；封死判準＝ADR-00064 決定 1／決定 2；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [authz, casbin, governance, state-machine, behavior-island, authz-governance]
---

## 背景

- 005 刀立授權歸檔寫入面時，歸檔原因只有三值（`role_soft_delete`／`menu_soft_delete`／`menu_button_removed`）、皆出自連動歸檔、皆不可復原；判定單點＝`model/facade/sys_casbin_archive.rs` 之 `is_non_restorable_reason`（三值 `matches!`），既有釘案 `archive_reasons_pin_three_literals_and_non_restorable_set_is_exactly_them` 之負向臂把三個撤銷原因字面列為「不得屬不可復原集」。授權歸檔表之三自由度 won't-use（ADR-00044 決定 4）以「選單維歸檔列結構性無復原路徑」為第③款之前提，並附翻案觸發條款：引入使選單維歸檔列出現可復原原因之寫端時 MUST 復核 `menu_id` 同實例欄。
- 本刀首度產出**手動撤銷**之歸檔列（三維授權寫端之撤銷＝移入歸檔、原因 `menu_revoke`／`button_revoke`／`endpoint_revoke`；FR-012），並首度上線授權回收桶兩支端點（getArchivedPolicies／restorePolicy；seed 政策列 70／71、頁級選單列 `manage_policy-archive`＝授權列 72）。
  - 若選單維或按鈕維之撤銷列可復原 ⇒ 同路由鍵重建之新選單、或絕版後重現之按鈕碼，可經「復原舊實例授權」繼承——島 H2 同鍵重建零繼承之破口；而選單維沒有同實例錨可判。
  - rev4 形之復原只驗兩腿（原因＋同實例）、不驗端點仍在路由表、不驗封死，且列表之可復原旗標與權威判定不同判準（「顯示可復原、點了被拒」）。
- 前代以 rev5:ADR 0055 定形（復核結論 B＝兩維入不可復原集、鎖內固定序五腿、旗標逐腿同判準）；brainstorm Q2／Q16／Q17 照前代。rev6 座標另有三處不同：交易由 handler 持有（前代 facade 自開交易、自寫稽核之形不帶）；rev6 之角色 facade 刻意不帶以代碼鎖讀件（`model/facade/sys_role.rs` 模組 doc）、只有以 id 鎖讀之 `sys_role::find_active_by_id_for_update`；前代回灌撞唯一索引之收斂分支，其前提之競態在 rev6 鎖序下結構不可達（決定 10）。

## 決策驅動因子

- 島 H2 同鍵重建零繼承不得經授權回收桶破口；零 migration、零 seed 變更（FR-002）。
- 後端為最終防線：鎖內重驗（lock-then-redecide、ADR-00044 決定 3 之 G5）、永不信列表時點之旗標。
- 旗標與權威同判準：UI 不出現「顯示可復原、點了被拒」。
- 撤銷而無復原＝變相硬刪：端點維（最直接的能力面）須可一鍵復原，且超管自撤後之自救路徑恆可走（Q14）。
- 不為結構不可達之情境寫業務錯誤分支。

## 考慮過的替代案

1. **三值維持、選單／按鈕維手動撤銷列可復原**：ADR-00044 決定 4③ 之論證即破、島 H2 破口實質開啟（同路由鍵重建之選單經復原舊授權繼承）。否決。
2. **選單／按鈕維可復原並加同實例欄**（歸檔表加 `menu_id`、復原時驗其＝現役同路由名活選單 id）：需 migration（破 FR-002）；按鈕碼為跨選單聯集、無單一同實例錨可加；Q2 已否。否決。
3. **復原不查封死**（靠原因與同實例兩腿兜底）：`endpoint_revoke` 列之（路徑,方法）可能於歸檔之後經基線資料演進成為封死集成員；更早一代 rev3 之先例缺陷正是漏了復原路徑；與寫端同一查詢件（新建 `sys_casbin_policy::protected_endpoint_set`）、成本近零（ADR-00064 替代案 8 同判）。否決。
4. **以歸檔 `v0` 代碼鎖讀活角色列再比 id**（前代 as-built 形）：須新建以代碼鎖讀件，而 rev6 角色 facade 刻意不帶該件；與所選形逐形等價（決定 4）、所選形之鎖足跡較窄且零新鎖讀件。否決。
5. **NoOp 回拒（`biz.policy.notRestorable`）**：使用者要的授權已在現役卻被告知失敗＝誤導；若同時不消費歸檔列，則多次撤銷留下之同鍵歸檔列恆停在回收桶、每按每拒；Q16 已否。否決。
6. **NoOp 留稽核**（寫一列 `restore` 或另立一詞）：操作稽核封閉五詞無「無作用」詞，以 `restore` 記會把零變更記成回灌、另立詞＝擴封閉詞彙；spec Clarifications 2026-10-01 首題已否（照 rev5 零稽核），代價記已知態（決定 5）。否決。
7. **restorePolicy 入選單序列化域**（rev4 形之無條件入域）：可復原列只剩端點維、端點維不涉選單資料（島 H1「端點維授權寫入不涉選單域」）；入域只增鎖競爭、無對價（FR-031）。否決。
8. **可復原旗標只算兩半（原因＋同實例）、或加「是否已在現役」腿**：兩半＝端點下線或封死之列顯示可復原、點了被第③④腿拒；加現役腿＝Q16 已否（NoOp 本即回成功、多一次查詢無對價）。否決。
9. **保留 23505 收窄**（前代 as-built：回灌撞授權表唯一索引收為不可復原、配競態測與主鍵排他測）：該競態於生產路徑結構不可達（決定 10），收窄分支＝死碼、兩支測只能以繞過鎖序之直寫假造。否決。
10. **回收桶加原因值篩選**：列表已顯原因欄；Q17 已否。否決。

對所選方案跑同一反例（RL-0013）：

- 島 H2 繼承（替代案 1／2 之反例）：刪選單 S（路由名 r）→ 以 r 重建 S′ → 能否經回收桶回灌 S 之舊選單維授權而令 S′ 繼承？S 之選單維授權之歸檔原因只可能是 `role_soft_delete`、`menu_soft_delete` 或 `menu_revoke`——全屬不可復原集（決定 1）⇒ 第①腿即拒。按鈕碼絕版後重現同理（`menu_button_removed`／`button_revoke`／`menu_soft_delete`／`role_soft_delete`）。成立。
- 同代碼重建（替代案 4 之反例）：角色 R（id 5、代碼 X）生前有一列 `endpoint_revoke` 歸檔列（role_id 5）→ 刪 R → 以 X 新建 R′（id 9）→ 復原該列？所選形以 5 鎖讀活性角色查無 ⇒ 拒；旗標②半：代碼 X 之活角色 id 9 ≠ 5 ⇒ false。成立。
- 刪角色並發：復原等角色列鎖期間，刪除寫端 commit 該角色之軟刪 ⇒ 鎖讀經 PG 重判活性條件剔除 ⇒ 查無 ⇒ 拒、歸檔列保留。成立。
- 復原與端點維寫端並發同角色同鍵（決定 10 之反例）：兩者皆鎖同一角色列 ⇒ 序列化；後到者於鎖內重讀——寫端見現況已含該鍵 ⇒ 不重授；復原見已在現役 ⇒ NoOp。成立。
- 旗標與權威分歧：旗標②半以「代碼→活角色 id」比 role_id、權威以「role_id 鎖讀→比代碼」，兩式會不會一真一假？在活性代碼唯一與代碼不可變之下兩式同值（決定 4）；除此之外之差異只來自列表時點與復原時點之間的狀態變化（旗標非權威、復原鎖內重驗為準）。成立。

## 決定

1. **不可復原集五值、可復原恰一值**：
   - 不可復原集＝{`role_soft_delete`, `menu_soft_delete`, `menu_button_removed`, `menu_revoke`, `button_revoke`}；唯一可復原原因＝`endpoint_revoke`（端點維授權撤銷）；原因值共六。
   - 三個撤銷原因常數新建於 `model/facade/sys_casbin_archive.rs`、與既有三個連動原因常數並列：`REASON_MENU_REVOKE`＝`"menu_revoke"`、`REASON_BUTTON_REVOKE`＝`"button_revoke"`、`REASON_ENDPOINT_REVOKE`＝`"endpoint_revoke"`。
   - 判定單點＝既有 `is_non_restorable_reason`（三值擴為五值）；凡判斷可否復原者（復原第①腿、可復原旗標①半）都問這一支、不各持一份字面。
   - 既有釘案同批改寫：正向臂五值、負向臂只餘 `endpoint_revoke` 與非法字面——`menu_revoke`／`button_revoke` 自負向臂移入正向臂是本決定之拍板變更、非回歸。
   - 零 migration：`archive_reason` 欄既有、原因值為碼內字面 ⇒ BL-00047（schema 閘表數斷言之改對義務；觸發＝首支帶任何 delta migration〔含 add_column〕之刀開寫前）本刀不到期、反向確認。
2. **ADR-00044 決定 4 之復核結論（不翻案）**：
   - 本刀之選單維與按鈕維授權撤銷，是最接近該條款所指「使選單維歸檔列出現可復原原因」之寫端；依 FR-041③ 附復核結論於此。
   - 選單維歸檔列之原因只可能是 `role_soft_delete`／`menu_soft_delete`／`menu_revoke`，按鈕維只可能是 `role_soft_delete`／`menu_soft_delete`／`menu_button_removed`／`button_revoke`——全屬不可復原集（決定 1）⇒ 兩維歸檔列仍結構性無復原路徑、同實例判定無判定時點 ⇒ `menu_id` 同實例欄續 won't-use。ADR-00044 決定 4③ 前提句所稱之「三 reason」隨本刀擴為原因值六，其判準（選單維之原因全屬不可復原集）不變；ADR-00044 body 不動，讀時併讀本款。
   - ADR-00044 決定 4② 之受保護快照欄 won't-use 由 ADR-00064 決定 4（承重前提）續承；ADR-00044 決定 4① 之 `role_id` 可空維持（本 ADR 決定 4 以其 NULL 為拒）。
   - ★由此，**授權回收桶復原之選單維與按鈕維分支結構性不可達**＝憲法島 H1 括號「授權回收桶復原之該兩維分支」改寫為結構性不可達之依據（字面＝ADR-00063 決定五之 H1 括號改寫、於本刀 U0 親決）；restorePolicy 亦因可復原列只剩端點維而不入選單序列化域（決定 3）。
3. **restorePolicy 鎖內固定序五腿**（FR-029／FR-031）：
   - 前置：handler 持交易、不入選單序列化域；操作者取自請求上下文、缺席即拒寫 `5000` 且先於一切守門（FR-006）；body 缺席或壞形收斂為識別預設值、經第 0 步查無而拒（FR-007）。
   - 動作序＝鎖歸檔列（第 0 步、`FOR UPDATE`）→ ①原因 → 鎖角色列（`FOR UPDATE`；決定 4；`role_id` 為 NULL 不鎖、直接拒）→ ②～⑤ → NoOp／Applied（決定 5／決定 6）；第①腿不過即早退、不取角色列鎖（選單維與按鈕維之列恆止於此）。
   - 鎖序：歸檔表列先於角色列，與全域固定鎖序（advisory → 歸檔表列 → sys_role 列 → sys_menu 列 → casbin_rule）同向、略過 advisory。
   - 落點：鎖內重驗與寫入住擴充之 `model/facade/sys_casbin_archive.rs`（facade 層跨表例外之既有成員；復原同寫授權表與歸檔表）；交易外殼、稽核與判定面同步住新建 `handler/policy_archive.rs`。第④腿之端點全集與 HTTP 方法白名單由 handler 以參數傳入（新建 `router::policy_endpoints()`、新建 `router::endpoint_methods()`），facade 零 `crate::router` 引用。

   | 序 | 腿 | 判準（違者拒 `biz.policy.notRestorable`） | 對應之現役寫端守門 | 共用件 |
   |---|---|---|---|---|
   | 0 | 鎖歸檔列 | 歸檔列查無（識別不存在、已被消費、body 預設識別） | — | — |
   | ① | 原因 | `is_non_restorable_reason(archive_reason)` 為真 | 連動歸檔三原因（刪角色／刪選單／按鈕碼絕版）＋選單維與按鈕維授權撤銷 | `is_non_restorable_reason` |
   | ② | 同實例 | 歸檔 `role_id` 為 NULL；以 `role_id` 鎖讀活性角色列查無；鎖得角色之代碼 ≠ 歸檔 `v0`（決定 4） | 刪角色連動歸檔與三維撤銷皆寫來源角色 id；島 H2 同鍵重建零繼承之對偶 | `insert_archived` 之來源角色 id 反查、`sys_role::find_active_by_id_for_update` |
   | ③ | 封死 | 標的角色代碼 ≠ R_SUPER 且（v1, v2）∈ 封死集（ADR-00064 決定 1） | updateRoleEndpoints 之授予側封死判定（ADR-00064 決定 2） | `sys_casbin_policy::protected_endpoint_set`（新建） |
   | ④ | 端點在路由表 | （v1, v2）∉ `router::policy_endpoints()`〔新建〕之端點全集（免幽靈政策） | 端點維候選集＝getAllEndpoints 回應集；updateRoleEndpoints 之候選外 orphan skip | `router::policy_endpoints()`（新建） |
   | ⑤ | 停用不擋 | 角色停用不擋（停用≠撤銷；島 H4 精神）——無判定 | 三維寫端對停用角色照常授權；停用即斷權由授權讀端每請求濾角色狀態 | — |

   - 任一腿拒 ⇒ 早退、歸檔列保留（留作稽核）、零寫入、零稽核、零判定面同步；五腿全過後才分 NoOp／Applied（決定 5／決定 6）。
   - 「五腿」為重驗腿之計數；鎖歸檔列、鎖角色列為動作序、不計腿。
4. **角色列以歸檔來源角色 id 鎖讀（等價改形）**：
   - 以既有 `sys_role::find_active_by_id_for_update(txn, archived.role_id)`（主鍵且未軟刪、`FOR UPDATE`、不含狀態）鎖讀；`role_id` 為 NULL ⇒ 不鎖、直接拒（誠實退化、不補寫、不猜）；查無 ⇒ 拒；鎖得後比對其代碼＝歸檔 `v0`。
   - 與前代「以 `v0` 代碼鎖讀活角色列、再比 `role_id == 其 id`」等價，論證兩前提：(a) 歸檔 `role_id`＝歸檔當下以 `v0` 反查活性角色之 id（`insert_archived` 本體；查無＝NULL）；(b) 活性代碼唯一（`sys_role_code_active_uniq`）且代碼建後不可變（updateRole 對 `roleCode` 出現即拒）⇒ 若 `role_id` 所指角色仍活性，其代碼恆＝`v0`、且為代碼 `v0` 之唯一活角色。
   - 逐形對照：`role_id` 為 NULL ⇒ 兩形皆拒；所指角色已軟刪、無同代碼新角色 ⇒ 兩形皆查無、拒；所指角色已軟刪、同代碼新角色存在 ⇒ 前代鎖得新角色而 id 不等拒、本形查無拒；所指角色仍活性 ⇒ 兩形鎖同一列、通過；等鎖期間角色被刪除寫端 commit ⇒ 兩形皆經 PG 重判剔除、拒。結果逐形相同；唯一差異＝「同代碼新角色」形本形不鎖新角色列（鎖足跡較窄）。
   - 代碼比對（鎖得角色之代碼＝歸檔 `v0`）在 (a)(b) 皆成立時恆真，但 (a) 只由 `insert_archived` 之寫入路徑保證、歸檔列經資料層直寫即可破（`role_id` 指向活角色 A、`v0` 為他代碼）。此比對保留、不受決定 10「不為結構不可達之情境寫業務錯誤分支」判準約束，理由：它是鎖內對已取得之列的零成本比對、無需假造競態即可觸發；且承擔旗標與權威同判準——上述破形下旗標②半（代碼→活角色 id ≠ A）為 false，權威若拔掉此比對即放行而兩者分歧（決定 8）；決定 11 配負向案釘住。
   - 本刀後之撤銷列恆有來源角色 id（撤銷時標的角色列已鎖且活性）；NULL 只見於歷史列。
   - 角色 facade 不新建以代碼鎖讀件（前代 `find_active_by_code_for_update` 續不帶）；可復原旗標②半另需新建 `sys_role::active_ids_by_codes`（以代碼批次取活角色 id；決定 8）。
5. **NoOp（標的已在現役）**：五腿全過後，七欄身分鍵（`ptype`、`v0`～`v5`；＝授權表唯一索引 `unique_key_sea_orm_adapter` 之欄集）已在現役 ⇒ 刪歸檔列（消費）、回成功（`0000`、`data` null）、不重複寫入、零稽核、不觸發判定面同步（Q16、spec Clarifications 2026-10-01 首題）。
   - 同一（角色,端點）多次撤銷留下之多列歸檔：復原其一後，其餘各列之復原皆為 NoOp。
   - 可復原旗標不加「是否已在現役」腿（Q16）。
   - 「回收桶移除一列而稽核表無痕跡」與「NoOp 與 Applied 對前端不可區分」入 ADR-00068 款 12。
6. **Applied 寫入形**：同一交易內——
   - INSERT 授權列：新 id（走序列）；`ptype`、`v0`～`v5` 自歸檔快照過境；`protected` **顯式 FALSE**；建立者＝復原者 uid；建立時間由 DB default（`now()`）補（rev6 慣例：INSERT 省略該欄）——治理欄不回灌歸檔快照，復原＝一次新授予事件。經 facade 直接寫入，MUST NOT 經判定引擎管理 API（島 G1）、MUST NOT 經轉接器之新增政策路徑（LL-00035）。
   - 刪歸檔列 → 操作稽核 `restore` 恰一列（標的表＝角色表、標的 id＝角色 id、before 無、after＝歸檔 id／維度／標的／動作四鍵；列形細節住 data-model）→ commit。
   - commit 之後、不持判定面讀鎖，觸發一次判定面同步（觸發列屬 ADR-00067 決定 1；NoOp 與拒不觸發）。
7. **拒因一律同鍵**：歸檔列查無（含 body 預設識別）與任一腿拒，一律 `2222`＋`biz.policy.notRestorable`（純 i18n key、一因一鍵、不揭露哪一腿；FR-004）；歸檔列保留、零寫入、零稽核、零同步。後端為最終防線、不依賴前端停用復原鈕。資料庫故障經本域 handler 之資料庫故障收斂回 `5000`。
8. **可復原旗標＝權威①～④ 同判準**（FR-027）：
   - getArchivedPolicies 每列 `restorable`＝①原因不屬不可復原集 ∧ ②歸檔 `role_id` 非 NULL 且等於代碼 `v0` 之現役活角色 id ∧ ③¬（`v0` ≠ R_SUPER ∧（v1, v2）∈ 封死集）∧ ④（v1, v2）∈ `router::policy_endpoints()`（新建）之端點全集；⑤恆不擋、免算；①不過即短路（選單／按鈕維列恆 false）。
   - 批次求值、不逐列查：①半共用 `is_non_restorable_reason`；②半以新建 `sys_role::active_ids_by_codes` 一次取頁內通過①之列的活角色 id（無鎖、活性不含狀態、空集不查；前代同名件）；③半以新建 `sys_casbin_policy::protected_endpoint_set` 一次取（頁內無通過①之列即零查詢；ADR-00064 決定 2 之讀端消費）；④半取 `router::policy_endpoints()`〔新建〕之端點全集（與復原第④腿同由 handler 以參數傳入 facade）。
   - ②半之求值形（代碼→活角色 id、比 `role_id`）與權威之求值形（`role_id` 鎖讀→比代碼）在決定 4 之 (a)(b) 下同值。
   - 旗標為列表時點之派生值、非權威（讀端無鎖、無交易）；權威恆為 restorePolicy 之鎖內重驗。前端 MUST NOT 自行推斷。配「旗標＝權威」逐腿同判準測（①～④ 各一）。
9. **回收桶篩選只角色代碼與維度**（Q17；FR-026）：
   - 角色代碼＝歸檔 `v0` 文字等值；空字串視同缺席；可查已刪或停用角色之代碼（故不用只列活性且啟用角色之下拉）。
   - 維度＝由列內容推導之三值（`menu`＝`v2` 為 `menu`、`button`＝`v2` 為 `button`、`endpoint`＝`v2` ∈ HTTP 方法白名單〔新建 `router::endpoint_methods()`〕）；未知值靜默不濾；不新增維度欄。
   - 不收原因值篩選；伺服端固定序＝歸檔時間降冪、id 降冪，不收排序參數（ADR-00058）。
10. **不另設 23505 收窄**：前代於回灌 INSERT 撞授權表唯一索引時收為不可復原；rev6 不帶。
    - 判準：生產碼之授權表 INSERT 寫者恰兩類——三維寫端之授予與本復原——皆持該列 `v0` 所屬角色之角色列鎖（三維寫端鎖標的角色列、復原依決定 4 鎖同一列；活性代碼唯一＋代碼不可變 ⇒ 同 `v0` ⇔ 同一活角色列）；NoOp 判定在該鎖內 ⇒「NoOp 判定之後、INSERT 之前他交易 commit 同鍵」於生產路徑結構不可達。授權表之其餘寫端（連動歸檔、撤銷）只刪不插，刪除只會使 INSERT 更不衝突；判定引擎管理 API 之寫面生產碼零呼叫。
    - 任何資料庫錯誤（含序列失步撞主鍵之環境故障）一律 `5000`、根因落 log；不為不可達情境寫業務錯誤分支。
11. **非 vacuous 與機器證**（FR-050、SC-007；不入域一案＝FR-049、SC-005）：MUST 配——
    - ①～④ 各一負向：每案只令該腿不過——其前各腿皆過、且僅改正該腿之條件即 Applied（否則該案 vacuous）；②至少含三形：`role_id` 為 NULL、「來源角色已軟刪而同代碼新角色存在」（決定 4 逐形對照之承重形）、直種「`role_id` 指向活角色 A、`v0` 為他代碼」之端點維歸檔列 ⇒ 拒、歸檔列保留、旗標 false（拔掉決定 4 之代碼比對即轉紅）；③之構造與 ADR-00064 決定 8 之第③腿案共用、不另立；④以測試直種（v1, v2）不在所傳端點全集（生產＝新建 `router::policy_endpoints()`）之端點維歸檔列構造。每案斷言 `2222`＋`biz.policy.notRestorable`、歸檔列保留、授權表零寫、零稽核、判定面同步零觸發。
    - ⑤停用不擋一案：標的角色停用 ⇒ Applied（新 id、`protected=FALSE`、建立者＝復原者、歸檔列消費、`restore` 稽核恰一列、commit 後同步一次）；加入任何停用判定即轉紅。
    - NoOp 一案（決定 5）：`0000`、歸檔列消費、授權表零寫、零稽核、判定面同步零觸發。
    - 識別不存在一案、body 缺席或壞形收斂為識別預設值一案 ⇒ `biz.policy.notRestorable`（決定 7）。
    - 不入域一案（決定 3）：並發交易持選單序列化域 advisory 期間，restorePolicy 之交易本體直接完成並 commit、不等待——域鎖上零等待者（既有 `sys_casbin_archive::menu_domain_waiter_count`＝0）且完成時點早於持有者放鎖；加入入域即轉紅（005 刀 `handler/role.rs` 之 `add_role_passes_the_menu_domain_holder` 同形）。
    - 選單維與按鈕維之列恆不可復原一案：列表旗標 false、強呼 restorePolicy ⇒ `biz.policy.notRestorable`、歸檔列保留。
    - 決定 1 之不可復原集五值釘案（含負向臂翻）、決定 8 之「旗標＝權威」逐腿同判準四案、後果之自救路徑端到端一案同屬本款機器證、不重列。

## 後果

- 使用者可見行為（前後對照）：
  - 選單／按鈕維撤銷列在回收桶只能看、不能復原（旗標 false、復原鈕停用、強呼回 `biz.policy.notRestorable`）；選單維授權「撤了想復原」只能回授權彈窗重勾。
  - 端點維手動撤銷列可復原；端點已下線、屬封死集而標的非 R_SUPER、非同實例三類列旗標 false。
  - 復原成功即觸發判定面同步、API 判定於換上後生效；NoOp 回成功且該列自回收桶消失。
- 自救路徑恆可走（Q14、FR-032）：回收桶頁之選單列（授權列 72）與兩支端點（授權列 70／71）皆為受保護授權列、撤不掉 ⇒ R_SUPER 撤掉自身非受保護端點列（例 getRoleList）致角色頁失能時，仍可經回收桶復原該端點維列；選單／按鈕維被撤者於角色頁恢復後重勾。配一支端到端測試。
- 條文面：島 G5 之條文層級（五腿是否入條文）由 ADR-00063 決定一（親決題 G-b）於本刀 U0 親決；不論條文取何層級，五腿之判準、落點與逐腿對照全文由本 ADR 承載；增減腿＝以新 ADR supersede 本檔（條文若列腿名則同步 Amendment）。
- 碼面：三撤銷原因常數新建、`is_non_restorable_reason` 3→5、既有釘案之正負臂與其「恰三值」字面同批改寫；`sys_casbin_archive.rs` 模組 doc 之「歸檔原因只有三值……授權回收桶讀端與復原不帶」句於落地單元改現在式（RL-0011 種子）。
- 復原回插之授權列取新 id（落在 seed 上界之外）：走查還原與測試守衛須能清除之、並回補被撤之 seed 列（FR-044、FR-051；屬測試與工具基建）。
- 帳本：BL-00047 反向確認不到期；BL-00133 之敘述隨本刀改寫（授權歸檔表自本刀起有消費面＝復原刪列、撤銷原因新增三值）。
- 已知態交 ADR-00068：NoOp 零稽核移除歸檔列、NoOp 與 Applied 前端不可區分（款 12）、選單／按鈕維只剩閱覽（款 15）、復原不擋停用角色（款 16）。
- 代價：歸檔列除經復原（Applied／NoOp）消費外永不刪除、本刀不設保留期與清理（屬 BL-00133 之承載）。

## 翻案觸發器

- 產品需要選單維或按鈕維之授權可復原 ⇒ 決定 1 翻案；決定 2 之「該兩維分支結構性不可達」隨之失效，憲法島 H1 括號之「結構性不可達」句須同批以 Amendment 改寫（ADR-00063 翻案觸發器）；ADR-00044 決定 4 之 `menu_id` 同實例欄（及按鈕維之同實例錨）須復核、屬 migration（FR-002 範圍翻案）。
- 引入角色復原端點 ⇒ 決定 4 之同實例判準與 ADR-00044 決定 4 翻案觸發條款同時復核；該刀 MUST 依 ADR-00064 決定 4 自帶受保護快照欄（承重前提鬆綁）。
- 角色代碼改為可變、或活性代碼唯一索引變更 ⇒ 決定 4 之等價論證失效，改回以代碼鎖讀或另證等價；決定 8 之②半同審；決定 10 之不可達論證同破（須補唯一索引撞列之收斂或改鎖序）——與 ADR-00064 翻案觸發器之前提③鬆綁條同一組款號（決定 4／決定 8／決定 10）。
- 授權表出現第三類 INSERT 寫者（例：批次授權匯入、跨行程同步寫回），或任一 INSERT 寫者不持標的角色列鎖 ⇒ 決定 10 之不可達論證失效，須補唯一索引撞列之收斂或改鎖序。
- 非併發窗下實測出「旗標可復原、權威拒」或反之 ⇒ 逐腿同判準破口、復核決定 8。
- 新增第七種歸檔原因 ⇒ MUST 同批判定其可否復原、更新決定 1 與既有釘案。
- 回收桶出現原因值篩選或排序之實際需求 ⇒ 重審決定 9（Q17、ADR-00058）。
