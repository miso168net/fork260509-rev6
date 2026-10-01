---
id: "ADR-00064"
title: 結構性封死（島 G6）——封死集＝「ptype='p' ∧ protected=TRUE ∧ v2 ∈ HTTP 方法白名單」之（路徑,方法）謂詞、不寫列數；授予側整批拒 `biz.role.protectedGrant`、R_SUPER 豁免；掛點恰兩處（端點維授權寫端、授權回收桶復原第③腿）；承重前提＝受保護旗標寫不進來；選單維受保護四列與非封死之政策端點不封、no-escalation 本體留 007 刀
date: 2026-10-01
status: proposed
supersedes: []
superseded_by: []
provenance: "006-authz-governance 之 spec FR-041②、FR-021～FR-025（US2 AS1～AS5、SC-004、Edge Cases「結構性封死與保護」段）、FR-004（純 key 一因一鍵）、FR-013（鎖內重驗含封死集）、FR-050（變異自證）；brainstorm §0 Q3（封死射程照 rev5：只封 protected=TRUE）／Q4（no-escalation 照 rev5：留 007 刀）、主線工程判斷③（選單維受保護四列不封）；plan 期主線工程判斷（HTTP 方法白名單＝新建 `router::endpoint_methods()`、由 `HttpMethod` 全變體導出；封死集查詢件＝新建 `sys_casbin_policy::protected_endpoint_set`；facade 以參數收候選與白名單）；藍本＝rev5:ADR 0054（§1 謂詞不寫列數／§2 掛點恰兩處／§3 固定序與拒因／§4 選單維射程外／§5 非 vacuous 與變異自證／§6 承重前提／§7 翻案觸發）與其 as-built rev5:server/src/model/facade/sys_casbin_policy.rs 之 `protected_endpoint_set`（掛點＝同檔 `apply_endpoints_locked` 之封死腿、rev5:server/src/model/facade/sys_casbin_archive.rs 之 `restore_locked` 第③腿；讀端消費＝同檔 `list` 之可復原旗標）；R_SUPER 豁免真案之探針形＝rev5:server/src/model/facade/sys_casbin_policy.rs 之 `protected_grant_lockout_exempts_super_role_self_grant_but_rejects_other_role`、復原第③腿之兩半（含 R_SUPER 對照臂）＝rev5:server/src/model/facade/sys_casbin_archive.rs 之 `restore_rejects_each_leg_without_consuming_and_list_flag_agrees`（其非 R_SUPER 半把封死成員植在標的自身名下之形不帶，見決定 8）；rev5 憲法 v1.10.0 島 G6 字面供對照（rev6 入憲字面由 ADR-00063 決定一於本刀 U0 親決）；承重前提之上游＝ADR-00044 決定 4（授權歸檔表三自由度 won't-use 與翻案觸發條款）；no-escalation 掛點＝ADR-00014 決定 5、對沖條目＝BL-00048；背景量測＝rust-api/migration/src/m0002_baseline_seeds.rs 之 SEED_CASBIN_RULE 對 rust-api/server/src/router.rs 之 ROUTES（2026-10-01 逐列解析）；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [authz, casbin, governance, security, behavior-island, authz-governance]
---

## 背景

- 001 刀凍結之 seed 以授權表治理欄 `casbin_rule.protected=TRUE` 標記「治理面授權只屬 R_SUPER」；005 刀的授權寫面只有移除面（連動歸檔）、沒有任何授予端點——授予側至今零守門。本刀上 updateRoleEndpoints 之後，R_SUPER 在端點權限彈窗把 `POST /systemManage/updateRoleEndpoints` 勾給 R_ADMIN 只是一次點擊；此後 R_ADMIN 可再授自己任何端點＝**授權面的提權鏈**。守門因此非 vacuous：候選集＝路由表中受政策保護之端點全集（新建 `router::policy_endpoints()`；含受保護端點）、授予側不預標（FR-014），UI 真做得出這一步。
- 前代以謂詞式封死承接（rev5:ADR 0054；rev4 無授予側守門；更早一代 rev3 曾有唯一一次 no-escalation 真邏輯而帶三缺陷——靜默壓縮授權、漏復原路徑、判定與寫入不同時點，見該 ADR 背景）。brainstorm Q3 照前代只封 protected=TRUE、Q4 把 no-escalation 本體留給 007 刀（使用者域）。
- 量測（2026-10-01，逐列解析 seed 與 ROUTES；只供背景、不入條文與決定）：
  - seed 受保護授權列 19 列、皆屬 R_SUPER：端點維 15 列（GET 8／POST 7；每個（路徑,方法）恰一列、無他角色之同鍵列）＝本刀後現役路由 14＋尚未上線之 `/systemManage/updateUserSessionPolicy`（007 刀）1；選單維 4 列（`manage_role`／`manage_menu`／`manage_system-settings`／`manage_policy-archive`）；按鈕維 0 列。
  - 本刀前 ROUTES 受政策保護者 25 條：受保護 4（getSystemSettings、updateSystemSetting、getDeletedMenus、restoreMenu）、非受保護 21（IP 規則 5、unlockLogin 1、角色管理 8、選單管理 7〔含 getMenuTree、getAllPages〕）。本刀後 35 條：受保護 14、非受保護仍 21。
  - 本刀十支端點之 seed 政策列（32／33、52～57、70／71）全屬受保護；持有 R_SUPER 之 seed 帳號恰 1。
- 島 G 條文入憲前，授權治理既有行為之 rev6 凍結位＝ADR-00043（判定面同步）與 ADR-00044（決定 3 之島 G 行為承載）；G6 於 rev6 無先行承載（前代新立條＝`rev5:ADR 0054`，本刀照前代謂詞形入憲；Q3），其條文字面與層級由 ADR-00063 決定一於本刀 U0 親決，本 ADR 承載其設計全文。

## 決策驅動因子

- 一條規則、謂詞式、資料庫態：封死集隨基線資料演進自動納管（seed 中尚未上線之受保護端點，其路由一註冊即受封死），不靠人工同步名冊。
- 雙路徑同一判準：現役授權之新增路徑有兩條，漏掛一條即破（該先例缺陷②）。
- 不靜默壓縮：要嘛全做、要嘛整批拒且拒因可辨識（該先例缺陷①之反面）；拒因純 key、零攜參（FR-004）。
- 鎖內現查、永不信 pre-read（該先例缺陷③之反面；ADR-00044 決定 3 之 G5）。
- 零 migration、零 seed 變更（FR-002）；不在本刀擴張為 no-escalation（Q4）。

## 考慮過的替代案

1. **以路由表旗標封**（`RouteDef` 加欄、或 `Protection` 加一個「封死」變體）：與授權表受保護旗標成為兩份真相——撤銷側（受保護撤銷拒）讀授權表、授予側讀路由表，兩者一漂移即出現「撤不掉卻授得出」或反之；封死集的變動改由改碼承載，背離島 G1 之 DB-first（授權真相＝資料庫）。否決。
2. **寫死名冊封**（常數列舉封死之（路徑,方法）、或測試斷言封死集＝常數字面）：第二份同源字面，seed 演進即漂移、假綠（前代 `rev5:B-075` 靜態守恆同判不建）；名冊寫列數＝把活量寫進不變式。否決。
3. **以 UI 警示取代封死**（或對非受保護之政策端點加授出警示）：警示不是守門、後端照樣放行；受保護判定不得在前端自行推斷（FR-005 後端單一真源）；Q3 已否（UI 不加警示）。否決。
4. **授出即告警**（授予受保護或敏感端點時落告警、事後處置）：事後偵測擋不住提權鏈——被授者一取得授權寫端即可自授，告警到時鏈已走完；且本刀期間授權寫端全屬封死集 ⇒ 授予者恆為 R_SUPER 本人，告警受眾就是操作者自身；每次授予本已同交易落操作稽核列。否決。
5. **真 no-escalation（授予集 ⊆ 操作者現役集）取代封死**：Q4 已否（本體屬 007 刀、島 I）；本刀唯一能授予者為 R_SUPER、而 R_SUPER 持有全部候選端點 ⇒ 包含規則對本刀可達之操作者幾近恆真、擋不到本刀可達之任何提權鏈；另需 body 通道與判定進入點簽章變更（ADR-00014 決定 5 之掛點簽章無 body）。否決。
6. **擴射程至選單維受保護四列**：FR-023 已否；理由見決定 5。否決。
7. **把非受保護之政策端點一併封死**（治理端點全數只屬 R_SUPER）：Q3 已否；須改 seed 受保護旗標（破 FR-002 零 seed 變更）或另立名冊（替代案 2 之弊）；其授出效果以已知態逐支登記（決定 6）、多層管理員需求出現前無此必要。否決。
8. **只掛 updateRoleEndpoints、授權回收桶復原靠原因與同實例兩腿兜底**：`endpoint_revoke` 歸檔列可復原，其（路徑,方法）可能於歸檔之後經基線資料演進成為封死集成員；該先例缺陷②正是漏了復原路徑；同一查詢件（新建 `sys_casbin_policy::protected_endpoint_set`）雙掛成本近零。否決。

對所選方案跑同一反例（RL-0013）：

- 「漏一路」（替代案 8 之反例）能否在所選方案下發生？現役授權之新增路徑：三維寫端之端點維授予、授權回收桶復原——兩條皆掛（決定 2）。選單維與按鈕維寫端之新授列 v2 ∈ {`menu`, `button`}、依白名單定義不屬封死集；刪角色、刪選單、按鈕碼絕版只撤不授；首頁寫端不寫授權表；判定引擎管理 API 之寫面生產碼零呼叫（判定面寫鎖檔集名冊 `ENFORCER_WRITE_FILES` 維持空冊）。成立。
- 「兩份真相漂移」（替代案 1 之反例）：封死集與撤銷側受保護判定讀同一欄（`casbin_rule.protected`），無第二份。成立。
- 豁免繞道：非 R_SUPER 角色能否取得 R_SUPER 代碼而受豁免？角色代碼建後不可變（updateRole 對 `roleCode` 出現即拒 `codeImmutable`）、活性代碼唯一索引（`sys_role_code_active_uniq`）、R_SUPER 為 seed 角色而受 seeded 守門擋刪（`sys_role::SEEDED_ROLE_IDS`）⇒ 他角色結構上無從持有 R_SUPER 代碼。成立（此前提併入決定 4）。
- 字面繞道：以小寫方法、未註冊路徑或路徑變體提交封死集端點？期望集先經候選集 orphan skip（候選鍵取自新建 `router::policy_endpoints()`：方法為新建 `router::endpoint_methods()` 之白名單字面、路徑取自路由表）⇒ 新授集之（路徑,方法）恆屬候選集、方法恆為白名單字面 ⇒ 封死判定之比對面完整。成立。
- 判定與寫入之間封死集被改？受保護旗標無任何寫端可設為 TRUE、受保護列之撤銷整批拒、R_SUPER 受 seeded 守門擋刪 ⇒ 交易期間封死集結構上不變；判定仍於標的角色列鎖之後同交易現查。成立。

## 決定

1. **封死集（謂詞式、不寫列數）**：封死集＝現役授權列中滿足 `ptype='p' ∧ protected=TRUE ∧ v2 ∈ HTTP 方法白名單` 之（v1, v2）＝（路徑,方法）集合；不問 `v0`（誰持有不影響「該鍵受保護」）；資料庫態、於寫端交易內標的角色列 `FOR UPDATE` 之後現查（單次查詢、不另取鎖）。**不變式**：任何寫端 MUST NOT 使 `role_code ≠ R_SUPER` 之角色持有封死集中任一（路徑,方法）。條文與本 ADR 一律只寫謂詞、不寫列數（量測值只住背景）。
   - HTTP 方法白名單＝新建 `router::endpoint_methods()`，由既有 `router::HttpMethod` 全變體經 `as_str` 導出（與路由表同源、不手寫第二份字面）；白名單之字面與維度標記 `menu`／`button` 不相交，選單維與按鈕維之受保護列因此結構上不在封死集。
   - 封死集查詢件單點＝新建 `sys_casbin_policy::protected_endpoint_set`（住新建 facade `model/facade/sys_casbin_policy.rs`；前代同名件）；以參數收白名單（呼叫端傳入 `router::endpoint_methods()`〔新建〕）、facade 零 `crate::router` 引用；決定 2 之兩掛點與讀端消費共用這一支、不各持一份判定。
2. **掛點恰兩處（雙路徑、同一查詢件 `sys_casbin_policy::protected_endpoint_set`〔新建〕）**：

   | 掛點 | 位置與時序 | 違者 |
   |---|---|---|
   | updateRoleEndpoints | 端點維寫端之鎖內：鎖標的角色列 → 候選集 orphan skip → 現況 ∩ 候選集 → 導出撤銷集與新授集 → 撤銷判定（受保護撤銷拒）→ **授予判定（本腿）** → 任何寫入 | 整批拒 `biz.role.protectedGrant` |
   | restorePolicy 第③腿 | 授權回收桶復原之鎖內固定序五腿第③腿（ADR-00065 決定 3）：標的角色非 R_SUPER 且歸檔列（v1, v2）∈ 封死集 | 拒 `biz.policy.notRestorable`、歸檔列保留 |

   讀端消費一處、**不計掛點**：授權回收桶列表之可復原旗標③半（ADR-00065 決定 8）——列表時點之推導、非授權新增路徑。為何恰兩處：現役授權之新增路徑恰兩條（見上節反例一）。★日後任何第三條現役授權新增路徑進場，MUST 掛同一查詢件、並以新 ADR 更新本表，島 G6 條文之「掛點恰兩處」同步以 Amendment 擴列（ADR-00063 翻案觸發器）。
3. **授予側固定序與拒因**：
   - updateRoleEndpoints 先判撤銷、再判授予（兩拒因並存取先序；實務上互斥——受保護授權列今皆屬 R_SUPER、封死只擋非 R_SUPER 標的）。
   - 非 R_SUPER 標的之新授集 ∩ 封死集 ≠ ∅ ⇒ **整批拒**：`2222`＋`biz.role.protectedGrant`（純 i18n key、一因一鍵、不攜被擋項；被擋項不上 wire、至多供 tracing 與測試斷言；FR-004）；判定在任何寫入之前、交易 rollback ⇒ 零變更、零歸檔、零稽核、零判定面同步。**不靜默壓縮**：不剔除被擋項後放行其餘。
   - **R_SUPER 豁免**：標的角色代碼＝`sys_role::SUPER_ROLE_CODE` 時不判本腿（無人可封死超管）；新授集為空時亦不查封死集。兩形皆零額外查詢。
   - 操作者（R_SUPER）欲知哪些端點受保護，於 R_SUPER 自身之端點權限彈窗可見（三支現況讀端每項帶受保護旗標、受保護項鎖定）；候選讀端不帶受保護或封死預標（FR-014）。
4. **承重前提（FR-024）**：
   - ①**受保護旗標結構上寫不進來**：授予 INSERT 與復原 INSERT 一律顯式寫 `protected=FALSE`；寫端 DTO 無受保護欄；一般管理介面永不提供設定或解除受保護旗標之能力（島 G2、防鎖死 by-design）⇒ 封死集之成員只隨基線資料層級之決策（seed／migration）變動。
   - ②**受保護授權列結構上進不了可復原歸檔**：手動撤銷觸及受保護列即整批拒（`biz.role.protectedRevoke`）；刪角色之連動歸檔雖含受保護列、但其原因 `role_soft_delete` 屬不可復原集，且受保護列今皆屬 R_SUPER、受 seeded 守門擋刪 ⇒ 可復原之歸檔列（唯 `endpoint_revoke`）原值恆 `protected=FALSE`。授權歸檔表不加受保護快照欄（ADR-00044 決定 4②）即以此為前提。
   - ③**豁免以代碼判定之前提**：角色代碼建後不可變、活性代碼唯一、R_SUPER 為受 seeded 守門擋刪之 seed 角色 ⇒ 他角色結構上無從持有 R_SUPER 代碼。
   - 鬆綁之處置分兩路：
     - 前提①②任一處鬆綁（受保護旗標開放寫入或 UI 化、受保護授權列之撤銷不再整批拒〔島 G2 反轉＝MAJOR〕、把受保護政策掛上非 seed 角色、引入角色復原）＝觸發 ADR-00044 決定 4 之翻案觸發條款（spec FR-024）：該刀 MUST 自帶受保護快照欄，並復核本 ADR 決定 1～決定 3。
     - 前提③鬆綁（角色代碼改為可變、活性代碼唯一索引變更、R_SUPER 變為可刪）⇒ 復核本 ADR 決定 3 之 R_SUPER 豁免，以及 ADR-00065 決定 4（以歸檔來源角色 id 鎖角色列之等價論證）／決定 8（可復原旗標②半）／決定 10（不設 23505 收窄之不可達論證）；與授權歸檔表之受保護快照欄無涉。
5. **射程外一：選單維受保護四列**（FR-023；沿前代島 G6 之射程）：v2＝`menu` 之受保護列不在封死集——可授予他角色該選單項之可見性。可見效果：該四頁中屬封死集之端點（三維授權讀寫與候選讀、選單回收兩支、系統設定兩支、授權回收桶兩支）對非 R_SUPER 仍回 `5003`；頁內非封死之端點依其各自授權。此可見效果入 ADR-00068 款 10（「看得到、封死功能點不動」之逐頁實況由本刀 CDP 三方對照單元實測定稿）。不擴射程之理由：選單可見性不是能力面——能力面在端點、端點已由封死集把關；把可見性一併綁死 R_SUPER 只增加一套平行保護、不擋任何提權鏈。v2＝`button` 之受保護列現無、同理不入。
6. **射程外二：非封死之政策端點**（Q3；FR-025）：受政策保護之路由中不屬封死集者一律可授予非 R_SUPER（分類與量測見背景）；授出後效果逐支入 ADR-00068 款 9（含 unlockLogin 授出後無帳號維守門、角色與選單寫端、IP 規則寫端之下放效果）；UI 不加警示；翻案觸發＝首次出現多層管理員需求（見翻案觸發器）。
7. **no-escalation 本體不在本刀**（Q4）：ADR-00014 決定 5 之 `no_escalation_check` 掛點維持恆放行、不動簽章與呼叫點；本體（操作者維之包含規則、前代島 I7）歸 007 刀，BL-00048 觸發收窄至 007 刀。分工：封死＝角色維（非 R_SUPER 角色不得持有封死集）；no-escalation＝操作者維（授予者不得授出自己沒有的）——兩者正交、封死不因 no-escalation 落地而撤。
8. **非 vacuous 與機器證**（FR-022、FR-050、SC-004）：MUST 配——
   - 非 R_SUPER 標的授予封死集端點 ⇒ 整批拒、零變更零歸檔零稽核零同步（非 vacuous：候選集含封死集成員，拆掉判定即通過）；同一請求改為非封死端點 ⇒ 通過。
   - 撤銷先判之固定序一案（同一請求兼具兩拒因 ⇒ `biz.role.protectedRevoke`；seed 下兩拒因互斥，測試以直種非 R_SUPER 名下之受保護列構造）。
   - restorePolicy 第③腿：非 R_SUPER 標的之封死集歸檔列 ⇒ 拒且歸檔列保留；R_SUPER 標的 ⇒ 通過而 Applied（兩案之歸檔列皆以測試直種構造——現行基線下生產路徑產不出封死集端點之 `endpoint_revoke` 列：R_SUPER 名下者屬受保護列、撤銷即整批拒；非 R_SUPER 本就持有不到；第③腿防的是歸檔之後封死集經基線資料演進而擴大之形）。兩半同取下述豁免案之探針鍵（非 R_SUPER 之第三方合成代碼名下直種一列 protected=TRUE 之合成（路徑,方法）現役列使之入封死集）；facade 以參數收端點全集，測試所傳之端點全集含探針鍵、第④腿方過。
     - R_SUPER 半：MUST 先自證「判定當下（v1, v2）∈ 封死集」（不成立＝第③腿對該列無可豁免、斷言 vacuous）且 R_SUPER 現役不持有該鍵（使過腿後為 Applied 而非 NoOp）。
     - 非 R_SUPER 半：標的＝另建之非 R_SUPER 合成角色（有角色列、非探針持有者；歸檔列原因 `endpoint_revoke`、來源角色 id 與 `v0` 取該角色，使第①②腿過），MUST 先自證標的現役不持有該鍵——使 ADR-00065 決定 11 之「僅改正該腿之條件即 Applied」成立（改正＝令探針鍵出封死集，例：探針列之 protected 改 FALSE；標的若持有同鍵，改正後落 NoOp 而非 Applied、該負向案 vacuous）。與藍本之差異：rev5 as-built 之復原第③腿測試（見 provenance）把封死成員植在標的自身名下，改正該腿後落 NoOp、不滿足前句；rev6 改取第三方名下之探針鍵。
   - 選單維受保護列可授可見性一案（決定 5、FR-023）：以 updateRoleMenu 把受保護選單項（例 `manage_role`）授予非 R_SUPER 角色 ⇒ Applied、該項入新授集、新列 `protected=FALSE`；該角色呼叫該頁所屬之封死集端點（例 getRoleMenu）仍回 `5003`。
   - 封死集謂詞釘（對 `sys_casbin_policy::protected_endpoint_set`〔新建〕）：不問 `v0`；`v2='menu'` 之受保護列不入；`protected=FALSE` 不入；白名單外方法不入；`ptype` 非 `p` 不入；白名單參數為承重（縮小白名單即少回；生產呼叫端傳 `router::endpoint_methods()`〔新建〕）。
   - 受保護列經撤銷路徑進歸檔之案數恆零。
   - **變異自證**：拆掉授予側判定、或改動謂詞 ⇒ 對應測試轉紅（紅證印 skipped=0）⇒ 還原 ⇒ 綠。
   - **R_SUPER 豁免案之構造（探針形）**：零 seed 變更下 R_SUPER 已持有全部候選端點，且 seed 之封死集每個（路徑,方法）恰一列受保護授權列、皆屬 R_SUPER（背景量測）⇒ wire 面打不出「R_SUPER 自授封死集端點而新授 ≥1」，豁免案之標的鍵 MUST 是 R_SUPER 現役不持有、而判定當下屬封死集之合成鍵。真豁免由 facade 層測試承載（藍本＝rev5 as-built 之 facade 測試，見 provenance）：
     - 交易內於非 R_SUPER 之第三方合成代碼名下（不同於對照臂標的；藍本形＝只植授權列、不建角色列）直種一列 protected=TRUE 之合成（路徑,方法）探針列（方法取白名單內字面；R_SUPER 現役不持有）。
     - 先自證「探針 ∈ 封死集，且 R_SUPER 與對照臂標的現役皆不持有」——前兩項任一不成立＝R_SUPER 自授之新授集 ∩ 封死集＝∅、拆掉豁免分支照樣通過、豁免斷言 vacuous；對照臂標的已持有＝其新授集為空、測不到授予判定。
     - R_SUPER 自授：期望＝R_SUPER 端點維現役全集＋探針，候選集含探針（facade 以參數收候選集）⇒ Applied、撤銷 0、新授 1、新列 `protected=FALSE`。
     - 對照臂：同一探針授另建之非 R_SUPER 合成角色（有角色列、非探針持有者）⇒ 整批拒 `biz.role.protectedGrant`（兩臂唯一差異＝標的角色代碼）。
     - rollback 收尾（零 seed 變更）。
     - wire 案只驗 R_SUPER 以候選內現況原樣提交 ⇒ `0000`、撤銷 0、新授 0。
   - 不建靜態守恆（封死集＝常數字面之斷言）：執行期謂詞為唯一真源（替代案 2）。

## 後果

- 島 G6 條文（字面由 ADR-00063 決定一於本刀 U0 親決）之設計全文＝本 ADR；新增掛點＝新 ADR 更新決定 2 之表＋島 G6「掛點恰兩處」同步 Amendment。
- 新拒因鍵 `biz.role.protectedGrant` 隨首個發出它的單元落地（`MSG_KEYS` 名冊、三檔 locale 之後端子樹、`app.d.ts` backend 型節同批；FR-004）；前端以共用攔截層之純 key toast 呈現、無明細表（FR-034）。
- 封死集查詢件 `sys_casbin_policy::protected_endpoint_set`、HTTP 方法白名單導出件 `router::endpoint_methods()`、端點候選入口 `router::policy_endpoints()` 皆新建；facade 保持零 router 引用（白名單與端點全集由呼叫端以參數傳入）。
- 島 G6 之承重前提①②（決定 4）使 ADR-00044 決定 4 之 won't-use 分析續有效；授權回收桶之復原路徑經第③腿結構上不可能把封死集端點回灌給非 R_SUPER。
- 已知態交 ADR-00068：選單維受保護四列之可見性下放（決定 5＝其款 10）、非封死政策端點之授出效果（決定 6＝其款 9）。
- no-escalation 掛點續恆放行；BL-00048 收窄至 007 刀、列不刪。
- 代價：R_SUPER 以外之角色永遠拿不到封死集端點——多層管理員需求出現前此即設計。

## 翻案觸發器

- 首次出現多層管理員或委派治理需求（非 R_SUPER 角色須授予下級、但不得超出自身）⇒ 以新 ADR 評估填入 ADR-00014 決定 5 之掛點本體（包含規則、鎖內重驗、整批拒、含復原路徑），並復核本 ADR 與島 G6 條文（反轉＝MAJOR）。
- 007 刀之 no-escalation 本體（操作者維之包含規則；決定 7）落地或島 I 入憲 ⇒ 復核決定 3 之固定序與拒因鍵（包含規則之判定位次與其拒因鍵不得與撤銷判定、封死判定互相吞沒）、決定 7 之正交分工，以及授權回收桶復原是否同掛包含規則（島 G6 條文面之對應觸發＝ADR-00063 翻案觸發器之島 I 入憲條）。
- 新增第三條現役授權新增路徑（例：新授權維度之寫端、批次授權匯入）⇒ 掛同一查詢件（`sys_casbin_policy::protected_endpoint_set`〔新建〕）、以新 ADR 更新決定 2 之表，並同步以 Amendment 擴列島 G6 之「掛點恰兩處」（ADR-00063 翻案觸發器）。
- 決定 4 前提①②任一處鬆綁（受保護旗標開放寫入或 UI 化、受保護授權列之撤銷不再整批拒〔島 G2 反轉＝MAJOR〕、把受保護政策掛上非 seed 角色、引入角色復原）＝觸發 ADR-00044 決定 4 之翻案觸發條款（spec FR-024）⇒ 該刀 MUST 自帶受保護快照欄，並復核本 ADR 決定 1～決定 3。
- 決定 4 前提③鬆綁（角色代碼改為可變、活性代碼唯一索引變更、R_SUPER 變為可刪）⇒ 復核本 ADR 決定 3 之 R_SUPER 豁免與 ADR-00065 決定 4／決定 8／決定 10。
- `router::HttpMethod` 增刪變體（例 PUT／PATCH）⇒ 複核白名單導出（`router::endpoint_methods()`〔新建〕）與維度標記不相交、封死集與端點維現況辨識同步擴。
- 封死集端點經基線資料層級決策（seed／migration）下放給非 R_SUPER——改受保護旗標，或把端點維受保護授權列掛上非 R_SUPER 角色（含 seed 之 R_ADMIN；後者＝破決定 1 之不變式）（例：008 刀之設定頁下放）⇒ 須立 ADR，並復核本 ADR 決定 1～決定 4 與島 G6 條文（島 G6 條文面之對應觸發＝ADR-00063 翻案觸發器）；其中掛上非 seed 角色者屬決定 4 前提①②之鬆綁形、依該款自帶受保護快照欄。
- 以 seed／migration 使封死集擴大而納入非 R_SUPER 角色現役已持有之（路徑,方法）（例：把可授出之政策端點之授權列改為受保護）⇒ 該 migration MUST 同批處置非 R_SUPER 角色名下之同鍵現役列（例：以 `endpoint_revoke` 移入授權歸檔、復原第③腿即擋其回灌），否則即破決定 1 之不變式；並立 ADR 復核本 ADR 決定 1／決定 4。
- 選單維受保護四列之可見性下放被實測判為缺陷（CDP 或使用者回報）⇒ 重審決定 5（FR-023）。
