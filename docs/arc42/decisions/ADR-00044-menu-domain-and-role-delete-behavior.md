---
id: "ADR-00044"
title: 選單域與角色刪除之域行為——角色刪除家族入域且實際歸檔才同步、島 G 行為（G1 前半／G3／G4／G5）由本 ADR 承載、授權歸檔表三自由度 won't-use、受保護選單守門、隱藏於選單釋義、保留路由名守門、upstream 同 URL 型偏離帳
date: 2026-09-23
status: proposed
supersedes: []
superseded_by: []
provenance: "005-role-menu-crud 之 spec FR-012～FR-017、FR-024、FR-038～FR-043（brainstorm 既定不問 2／4／5、R1-Q2／R1-Q5／R2-Q1／R1-Q10、工程判斷 12／27／28；clarify 2026-09-23 Q2～Q4）；藍本＝rev5:ADR 0050（§1 deleteRole 入域、§3 島 G 行為承載、§4 歸檔表三自由度 won't-use 與前代翻案觸發條款）——其 §2 免同步論證由 R1-Q2 翻為實際歸檔才同步（ADR-00043）；rev5 憲法 v1.10.0 島 G1／G3／G4 最終字面供對照（rev6 島 G 未入憲）；憲法 §I.2（前端隱藏機制皆不啟用、釋義②）與 `docs/ops/reference-src/schema-definition.md` hide_in_menu 白名單；draft 於 plan 期落 feature branch；決定 8／9＝`/speckit-analyze` 期 user 裁定（2026-09-24）；user 親決於 tasks T003（施工前提顆）"
tags: [authz, role, menu, behavior-island, role-menu-crud]
---

## 背景

- 本刀落地授權治理刀要消費的三件底座中之兩件——選單序列化域與授權歸檔寫入面——並首次讓角色有寫端。島 G（casbin 授權治理）條文隨授權治理刀入憲；在此之前，本刀已實作之島 G 行為（歸檔真相、撤銷必歸檔、刪除守門、lock-then-redecide）需要一個凍結位：條文早入＝憲法宣告無機器證之 grant 面行為，條文晚入＝本刀行為無凍結位，ADR 承載是兩全（前代同形）。
- 前代「刪角色免同步」論證被 R1-Q2 推翻（見 ADR-00043 背景）；受保護選單原只擋刪除，停用或改父受保護列可令管理區自 UI 消失（R1-Q5／R2-Q1）；活體契約 `schema-definition.md` 載 hide_in_menu 白名單「rev6 對應釋義隨 menu 域刀重審」（R1-Q10）。
- 本刀起常量旗標與路由名皆可寫：前端常量路由表以路由名為鍵、後端常量列排在內建之後，同名即覆蓋內建路由（例：常量選單 `login` 令全站登入頁失效）；另 base-web 內 upstream 之角色清單與選單清單請求函式仍以 upstream 型宣告同一 URL 之回應，與本刀 wire 權威型逐欄不同（憲法 §I.3 型別謊言帳本）。

## 決策驅動因子

- 角色刪除與選單刪除可寫同一批授權列（前者掃 `v0=role_code`、後者掃 `v1=route_name`），兩者須互斥、競態結構性不可達。
- 已知的前代破口（刪角色→同碼重建→指派之判定面繼承）不帶入。
- 守門語意一律凍結為固定序、多重違規取先序腿。

## 考慮過的替代案

1. **角色寫端全數入域**（含新增、更新、首頁）：零授權面、零選單資料、入域徒增鎖競爭；棄。
2. **刪角色家族維持免同步**：帶已知繼承窗；棄（R1-Q2）。
3. **受保護選單停用與改父只記已知態＋RUNBOOK 復原程序**：自鎖後須直改庫復原；棄（R1-Q5／R2-Q1）。
4. **hideInMenu 不開放寫入**：upstream 表單既有欄、業務需要；棄（R1-Q10）。

對所選方案跑同一反例（RL-0013）：「只擋受保護列本身之停用與改父」能否被「停用受保護列之祖先」繞過？seed 受保護列之祖先皆受保護、受保護旗標不開放寫入 ⇒ 祖先亦不可停用、不可改父；自鎖路徑結構性不可達、成立。

## 決定

1. **角色刪除家族入域**：deleteRole／batchDeleteRole 進選單序列化域（ADR-00043、島 H1）；addRole／updateRole／updateRoleHome **不進域**。機器證＝pg_locks advisory NOT-granted 等待斷言（逐進域寫端一案）。
2. **實際歸檔才同步**（翻前代免同步論證）：角色刪除家族軟刪成功且實際歸檔 ≥1 列時 commit 後觸發判定面同步；端到端案「刪除→同碼重建→直種指派→判定面零命中」。本刀新建角色零授權、seed 角色被 seeded 守門擋 ⇒ 生產面本刀實際不觸發、授權治理刀授權後才生效。
3. **島 G 行為承載**（條文隨授權治理刀入憲時由該刀 Amendment 轉正；本 ADR 不因此被 supersede）：
   - **G1 前半（真相唯一、DB-first）**：授權變更（本刀＝移除面歸檔）與其操作稽核 MUST 同一交易落地、絕不走判定引擎管理 API 寫面；判定面由真相全量重建導出。失敗契約半邊＝ADR-00043。
   - **G3（撤銷必歸檔）**：deleteRole 通過守門後，同交易掃 `v0=role_code` **全三維含 protected 列**做移入歸檔（完整快照＋`role_id`＋reason=`role_soft_delete`）；該 reason MUST NOT 可手動復原（reason gate 單點 fn 承載、本刀三值）；**角色刪除單向**——本刀與授權治理刀皆無角色復原端點。歸檔掃描 MUST 早於角色列軟刪（否則 `role_id` 反查全落 NULL）。
   - **G4（刪除守門與批次原子）**：固定序三層守門①seeded（`SEEDED_ROLE_IDS=[1,2,3]`＋`SUPER_ROLE_CODE="R_SUPER"` 單一宣告源、碼內常數形——零表欄零 migration 之刻意取捨）②in-use（`others = total − 操作者是否為成員`；total＝全部指派列、不濾使用者啟停與軟刪；拒因回誠實總掛載、純 i18n key 零攜參）③self-role（操作者所屬角色不可刪；成員身分含停用角色）；批次去重後 id 升冪逐項全套守門、任一違規（含查無）**整批拒**、單一交易。
   - **G5（lock-then-redecide）**：一切向現役授權寫入、或改動角色活性／啟用狀態之寫端 MUST 同交易鎖標的列、鎖內重判前提後才落寫；角色刪除家族另進序列化域（advisory 先於列鎖、固定鎖序 `advisory → 歸檔表列 → sys_role 列 → sys_menu 列 → casbin_rule`）。
   - **停用雙護欄**：操作者不得停用自己所屬角色＋R_SUPER 恆禁停用（不因操作者身分而異）；固定序 self→super；停用即斷權沿基線（授權讀端每請求濾角色狀態）、不以判定面同步實現。
   - in-use／self-role 兩腿於使用者角色指派寫端落地前生產面**結構性不可達**；測試以直種指派列構造真實觸發（資料態判定、零測試旗標、非 vacuous）。
4. **授權歸檔表三自由度 won't-use**（`sys_casbin_policy_archive` 結構零變更）：①`role_id` 維持可空（`v0` 反查活性角色、查無誠實退化 NULL）②不加 `protected` 快照欄（可復原列必經撤銷路徑而受保護列之撤銷整批拒 ⇒ 可復原列原值恆 `protected=false`；受保護列結構上進不了可復原歸檔；un-protect 永不 UI 化）③不加 `menu_id` 同實例欄（選單維歸檔僅三 reason 且全屬不可復原集 ⇒ 選單維歸檔列結構性無復原路徑、同實例判定無判定時點）。★**翻案觸發條款**（前代原文過境＋rev6 語境）：任何後續刀若引入角色復原、把受保護政策掛上非 seed 角色、或將 un-protect UI 化——不變式即破、缺欄變成靜默降權破口；屆時該刀 MUST 自帶 `protected` 快照欄（NULL＝unknown 誠實退化）並復核本 ADR。若引入使選單維歸檔列出現**可復原** reason 之寫端，同理 MUST 復核 `menu_id` 同實例欄之必要性。
5. **受保護選單守門（島 H3 之行為面）**：updateMenu 對受保護列拒「status 解析為停用」與「`parentId` 變更」（變更＝正規化後 ≠ 現值；同值＝無變更、放行）；deleteMenu 拒受保護列；拒因同鍵 `biz.menu.protectedMenu`、三檔譯文涵蓋刪除／停用／改父；其餘欄照常可編；受保護旗標不在寫端 DTO。
6. **hideInMenu 釋義**：憲法 §I.2「`hideInMenu`／頁面排除等前端隱藏機制**皆不啟用**」依其釋義②（「不啟用」＝禁止以 hideInMenu 作 demo 可見性治理手段）只約束 seed／demo 之可見性治理；超管運行期經選單管理改 `hideInMenu`＝業務資料、不算啟用隱藏機制；`schema-definition.md` 之六列白名單只描述 seed、該契約句改現在式並指向本款。
7. **寫端實作不變式**（兩域）：歸檔掃描先於標的列軟刪；絕版判定之按鈕碼聯集＝治理域（未刪含停用）且排除標的自身；批次刪除選單之「獨有按鈕碼」於各標的歸檔時點現算（同批先行軟刪者已不在治理域）、MUST NOT 於守門期預算；掃描依 `v2` 維度過濾；按鈕碼清單形制驗證先於「舊碼−新碼」計算；facade 歸檔 fn 回傳歸檔列數（觸發門之唯一依據）；擁有交易之入域寫端失敗腿顯式 rollback。

8. **保留路由名守門**：addMenu 於路由名形制之後驗「路由名 ∉ 前端保留路由名集」——保留集＝base-web 內建常量路由（`403`／`404`／`500`／`iframe-page`／`login`）∪ 內建根路由（`root`／`not-found`）；違反回 `biz.menu.routeNameExists`（零新鍵；語意＝該路由名已被占用）。updateMenu 因路由名不可變免驗；restoreMenu 因新增即擋而結構性不可達。保留集為 rust 單一常數、由既有跨子庫 python 閘以純讀檔對賬 base-web 路由定義之名集（附變異自證）。理由：憲法 §I.2「builtin 常量集不動」；未擋即一次誤操作全站鎖死、只能直改庫復原。
9. **upstream 同 URL 型偏離帳**（憲法 §I.3「每筆顯式偏離＝拍板、立 ADR」）：base-web 內 upstream `fetchGetRoleList`（`/systemManage/getRoleList`）、`fetchGetMenuList`（`/systemManage/getMenuList/v2`）與 `service-alova` 同名函式仍以 `Api.SystemManage.{RoleList,MenuList}` 宣告回應型；本刀 wire 權威型＝`Api.RoleAdmin.RoleRecord`／`Api.MenuAdmin.MenuRecord`（本刀 ADAPT 新型檔）。偏離類別（**實集以 wire-schema 快照之機器導出為準**；下列為舉例、非窮舉）＝①欄名差（審計四欄改名 `createBy`→`createdBy`、`createTime`→`createdAt`、`updateBy`→`updatedBy`、`updateTime`→`updatedAt`；rev6 額外欄如 `roleMemo`／`roleHome`／`menuMemo`／`deleted`）②可空性差（兩向：upstream 非空而 rev6 可空，如 `roleDesc`／`routePath`／`icon`；upstream 可空而 rev6 非空，如 `status`）③必出性差（upstream 可選而 rev6 必出，如 `component`／`buttons`）④值型差（upstream 為字面聯集型而 rev6 為寬型，如 `activeMenu`／`i18nKey`）。wire 裁判測試一案斷言「upstream 型與 rev6 型之欄差集（欄名集差＋共有欄之 required 差與型別差〔含可空性〕）＝同檔釘值常數」、漂移即紅。理由：本刀起 upstream 兩函式零 UI 消費者、rev6 型為接真頁唯一消費面；改 wire 欄名對齊 upstream 會翻 004 起之 rev6 欄名慣例。wire 行為零變化。

## 後果

- 角色刪除×選單刪除之併發窗結構性消滅；刪角色之判定面繼承窗於本刀即封（不留給使用者域刀）。
- 島 G 入憲時，本 ADR 決定 3 由該刀 Amendment 轉正、決定 4 之 won't-use 分析續有效；該刀 ADR 引用本檔為 provenance。
- 空陣列批刪語意＝提前 no-op 成功（零副作用、零稽核、不取域鎖）；查無 id 整批拒、重複 id 先去重（clarify Q3／Q4）。

## 翻案觸發器

- ★**使用者域刀之使用者軟刪寫端 MUST 定「軟刪是否清指派」**：若清指派，in-use 計數之保守口徑（含軟刪使用者之指派）須複核；若不清，掛載數語意維持並於該刀 ADR 引用本款。
- 使用者角色指派寫端落地 ⇒ in-use／self-role 兩腿轉為生產面可達、複核拒因語意與 UI 呈現。
- 決定 4 之翻案觸發條款任一成立。
- 受保護旗標開放寫入 ⇒ 重審決定 5。
- 新增 view 頁或 upstream rebase 改動內建常量路由／內建根路由之名集 ⇒ 決定 8 之保留集隨之對賬（由對賬閘攔下、同批改常數）。
- upstream 兩支清單請求函式出現消費者、或 upstream rebase 改動 `Api.SystemManage.{Role,Menu}` 型 ⇒ 重審決定 9 之偏離帳。
