---
id: "ADR-00075"
title: 包含規則（島 I7）與射程分工——判定＝handler 鎖內具名純函式、9 個消費點（使用者寫端八支＋unlockLogin 帳號維）共用單一包裝；中介層 no-escalation 掛點續恆放行為路徑級上限位、簽章與呼叫點不動；角色域、IP 域與授權回收桶復原不掛；ADR-00064 翻案觸發器首條與次條之複核結論；BL-00048 兌現
date: 2026-10-05
status: proposed
supersedes: []
superseded_by: []
provenance: "007-user-password-admin 之 spec FR-021～FR-025（US4 AS1～AS5、AS8、AS9、SC-004、Edge Cases「包含規則與委派」段）、FR-010（寫端固定序第④步）、FR-040（unlockLogin 帳號維掛點位次）、FR-060（BL-00048 backlog_done）；brainstorm §0 Q6（可下放＋包含規則入憲）／Q7（射程只限使用者域＋解鎖帳號維）、主線工程判斷①（ADR-00014 照 user 2026-09-07「走 BL 對沖、不翻案」；BL-00048 以兌現連動面收）；plan 期主線定案（純函式模組與 handler 包裝之命名與落點、`ActorScope` 以角色 id 為比對單位、enforce.rs 掛點續恆放行、呼叫點名冊閘合一為 `NO_ESCALATION_CALL_FILES`）；藍本＝rev5:ADR 0063 款三（兩實作位分工）與其 as-built rev5:server/src/auth/no_escalation.rs、rev5:server/src/handler/user.rs 之 `guard_no_escalation`（含全集短路）、rev5:server/src/handler/throttle.rs 之帳號維前置段、rev5:server/tests/authz_entrypoint_lint.rs 之兩張名冊；rev6 既有件＝`auth::enforce::no_escalation_check`、`sys_role::SUPER_ROLE_CODE`、`sys_user::advisory_lock_user`／`find_by_user_name`、seed 政策列 17～20／68／148／151／152／154 與 33／54／57／71 之受保護旗標（rust-api/migration/src/m0002_baseline_seeds.rs，2026-10-05 逐列核）；上游觸發＝ADR-00064 決定 7 與翻案觸發器首條／次條、ADR-00063 翻案觸發器之島 I 入憲條、ADR-00068 款 9；對沖條目＝BL-00048；島 I7 條文字面由 ADR-00074 於本刀 U0 親決；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [authz, user-domain, no-escalation, behavior-island, user-password-admin]
---

## 背景

- 本刀使用者寫端與既有 unlockLogin 之 seed 政策列除 updateUserSessionPolicy（列 68）外皆 `protected=FALSE`（列 17～20、148、151、152、154）⇒ 可授出（ADR-00064 決定 6）、路由一註冊即成候選（ADR-00066 決定 4）⇒ R_SUPER 自本刀起可把使用者寫端授給任一角色。updateUser 之角色集為期望全集（可含 R_SUPER）——無守門時，被授者可把 R_SUPER 指派給任一他人帳號，或經 addUser 另建持 R_SUPER 之帳號後自用，或停用、踢除、重設超管＝使用者域之提權鏈（改自身指派本即由本人規則先拒）。Q6 拍定「可下放＋包含規則入憲」。
- 002 刀預留掛點：ADR-00014 決定 5 之 `auth::enforce::no_escalation_check(db, actor_uid, path, method)`（恆 `Ok`、唯一呼叫點＝單一判定進入點 `enforce_role_path_method`、先於政策求值），其後果段預告「本體刀只填掛點函式體、零簽章變更、零呼叫端改動」。前代 as-built 之本體卻是 handler 鎖內之 body 級純函式（`rev5:ADR 0063` 款三）——預告與實況不符，user 2026-09-07 裁「走 BL 對沖、不翻案」，對沖條目＝BL-00048（觸發＝本刀）。
- ADR-00064 決定 7 把本體歸本刀，其翻案觸發器留兩條複核：首條（委派治理需求 ⇒ 評估「填入 ADR-00014 決定 5 之掛點本體」）、次條（本體落地或島 I 入憲 ⇒ 複核與撤銷、封死之判定序與拒因鍵不互吞、正交分工、授權回收桶復原是否同掛）；ADR-00063 翻案觸發器有同義之島 I 入憲條；ADR-00068 款 9 記 unlockLogin 授出後「無帳號維守門」。
- 本 ADR 承載島 I7 之設計全文；條文字面（含是否具名 R_SUPER）由 ADR-00074 親決。

## 決策驅動因子

- 規則須同時看見 A（操作者現役角色集）、T（標的全部指派）、N（寫後標的角色集）三元，且 T 須於標的 per-user 鎖內現讀（lock-then-redecide、永不信 pre-read）。
- 判定單點：九個消費點共用一支純函式與一支包裝，A／T 取法、拒因與日誌欄位只有一份真相。
- 一體適用、零特例分支：超管不是規則的例外，只是其 A 為全集（照字面 A＝{R_SUPER} 會使超管連編輯持 R_ADMIN 之帳號都被拒）。
- 拒絕回包不成為角色枚舉面（ADR-00014 決定 1、ADR-00076 決定 2 之判準）。
- 不擾動 006 刀已凍結之授權治理面（封死、撤銷拒、判定進入點簽章）；規則本身零 schema、零 seed 變更。

## 考慮過的替代案

1. **照 ADR-00014 後果段字面，把規則填進中介層掛點**：中介層取不到 body（N 不可得；body 只能消費一次、extractor 在 handler），也取不到鎖內之 T——中介層預讀 T 即與 lock-then-redecide 相牴；上提須先改造為帶 body 之中介層並改判定進入點簽章（spec Out of Scope）。否決。
2. **角色分級（rank）模型**：需 schema 欄與整套治理 UI，「同級互管」「零角色帳號」皆須另立特例（`rev5:ADR 0063` 同判）。否決。
3. **以 seed／migration 把使用者寫端政策列改受保護、不做包含規則**：擴大封死集即觸 ADR-00064 翻案觸發器（須立 ADR、複核決定 1～4），且與 Q6「可下放」相反——rev6 將永久沒有委派之使用者治理。否決。
4. **射程擴至角色域、IP 域與授權回收桶復原**：Q7 已否；理由見決定 6。否決。
5. **前端預判**（下拉只列操作者持有之角色、列級鈕依標的角色隱藏）：前端無從得知 DB-fresh 之 A 與鎖內 T，一漂移即「看得到、按了 5003」或「該能做卻被藏」（spec FR-024）。否決。
6. **違者回 `2222` 專屬業務鍵或攜差集**：攜「差在哪個角色」＝角色枚舉 oracle（反覆換 `roleIds` 即可問出整張角色表）；越權語意本即 `5003`。否決。

對所選方案跑同一反例（RL-0013）：

- 「讀不到 body 與鎖內 T」：判定住 handler、於 advisory 與標的列 `FOR UPDATE` 之後、任何寫入之前，A／T DB-fresh 現讀、N 由已解析之請求導出 ⇒ 三元俱在鎖內。成立。
- 「判定漂移成多份」：九個消費點皆經同一包裝、包裝內呼同一純函式；呼叫點檔集由名冊閘兩向恰等釘住（決定 8）。成立；剩餘形見後果之機器守邊界。
- 「超管被誤拒」：A 含 R_SUPER ⇒ 全集恆過、且短路不讀 T。成立。
- 「射程收窄後留提權鏈」：角色域、IP 域與授權回收桶復原之端點不改任何使用者之角色指派、亦不以使用者為標的——動不了 T 或 N；其下放效果續為已知態（決定 6）。成立。

## 決定

1. **規則**：九個消費點於鎖內、任何寫入前判 `T ⊆ A ∧ N ⊆ A`：
   - **A**＝操作者現役角色集：DB-fresh、濾角色軟刪與停用（料源＝`sys_user_role::role_ids_active_of_user`）；含 `sys_role::SUPER_ROLE_CODE` 所指之角色 ⇒ A 視為全集（不另立第二份 R_SUPER 字面）。
   - **T**＝標的之全部指派：不濾角色狀態（停用角色計入）、只濾角色軟刪（料源＝`sys_user_role::role_ids_all_of_user`；軟刪角色之指派在刪除守門下結構上不存在，此濾網為誠實面）。A 與 T 濾法不對稱屬刻意：停用角色不給操作者實權，卻仍是標的持有之物。
   - **N**＝寫後標的角色集：addUser 與帶角色集之 updateUser＝請求角色 id 集（去重；須全數在活性域）；未帶角色集之 updateUser、kickUser、resetUserPassword、updateUserSessionPolicy、unlockLogin 帳號維＝T（不動指派）；deleteUser 與 batchDeleteUser 之每筆＝∅（指派隨軟刪硬刪；與 N＝T 判定等價）；restoreUser＝∅（T 亦＝∅、復原零回灌）。請求角色集含不存在或已軟刪之 id＝寫後角色集無從成立 ⇒ 第④步以 N＝T 判（只判得到 T）、整筆拒由第⑤步 `biz.user.roleNotFound` 原位發出（rev5 HEAD 同形）。★「活性域」以角色列鎖讀結果判：指派寫端於固定序①之後、②之前對 T∪（請求角色 id 集）去重升序 `FOR UPDATE` 鎖讀角色列（addUser 只鎖請求集），④ 取鎖內結果構 N、⑤ 以同一結果判存在——鎖內構 N、不信 pre-read（封住「④ 判已刪而 ⑤ 前該角色被復原」之窗）。
   - **違者**＝`AppError::PermissionDenied`（`5003`＋HTTP 403＋純 key `system.forbidden`、data null）、零變更、零稽核；另落恰一則 warn（target `security.user`；操作者 id、標的 id、端點標籤三欄；角色差集不進日誌、不上 wire）；不新增觀測序列。A 或 T 之查庫失敗＝`5000`（不吞成空集——吞成空集會把庫故障偽裝成「此人無角色」而回 `5003`）。
   - 同級互管允許（T＝A 亦過）；零角色標的之 N＝∅ 恆滿足 `N ⊆ A`。
2. **落點與命名**：
   - 純函式模組 `rust-api/server/src/auth/no_escalation.rs`：`ActorScope { All, Roles(BTreeSet<i64>) }`（比對單位＝角色 id，與 T 讀端、請求角色 id 同軸、免逐請求代碼解析）、`actor_scope_of(現役角色（id, 代碼）清單) -> ActorScope`（純函式：任一代碼＝`sys_role::SUPER_ROLE_CODE` 即 `All`；A 之 DB 現讀由 `guard_no_escalation` 經 `sys_user_role::role_ids_active_of_user` 取得）、`assert_no_escalation(scope, t, n) -> Result<(), AppError>`；模組零 IO、零 path-root `entity::`。
   - handler 包裝 `guard_no_escalation(...)`（住 `handler/user.rs`、`pub(super)`、`handler/throttle.rs` 共用）：取 A → 全集即短路回 `Ok`（不讀 T：對超管該次讀可證明用不到，且其暫時性庫錯會把必過之寫入翻成 `5000`）→ 讀 T → 判 → 違者落 warn 並回拒。
   - 碼內名稱沿 002 刀既有掛點用詞 `no_escalation`、文件語稱「包含規則」。
3. **判定位次**：使用者寫端固定序第④步——①活性標的鎖讀（含角色列鎖與鎖內重驗）→②seed 保護→③本人規則→④包含規則→⑤業務守門（spec FR-010）；seed 保護與本人規則先於本規則（不因操作者身分而異）。批次刪除於全批鎖取齊之後逐筆判、任一筆違者整批 rollback、拒因不指筆。addUser 無既有標的（T＝∅、不取 advisory），判定仍在交易內、任何寫入前。
4. **unlockLogin 帳號維**：處理序＝維度解析與標的導出 → 操作者上下文檢查 → 開交易 → 以送出之帳號名原文解析現役使用者列 → advisory(標的 uid) → `guard_no_escalation` → 稽核列交易內寫入 → commit → 寫解鎖標記；拒＝零稽核、零標記，「稽核先於標記」（憲法島 E）不變、源碼次序釘同批更新。解析不到現役列（不存在或已軟刪）＝T＝∅ 恆過——不得改回異碼（未鎖標的回 `0000` 之冪等契約；異碼即開帳號存在性枚舉面）。來源維不套、處理序不變：其標的為計數桶、無 T 可取；以「該桶下曾失敗之帳號」導 T＝把 `5003` 變成「該來源後方有無超管」之探測器。已知態：帳號名解析必然先於取鎖，兩者之間若該帳號被刪且同名新帳號被建立，判定落舊 uid（T＝∅）而標記落帳號名鍵——影響限於解除該名之登入節流、不改授權與資料（前代以「帳號名不可變」推為穩定、未計刪除重建）；維持已知態、翻案觸發見下。帳號名解析為鎖前普通讀 ⇒ `sys_user::advisory_lock_user` doc「MUST 在 caller 已開的 txn 裡當首個動作呼叫」同批改為「早於任何列鎖（鎖前普通讀容許）」（research R22）。
5. **兩實作位之射程分工**（補充 ADR-00014 決定 5、不翻案）：

   | 實作位 | 判定單位 | 行為 | 為何不合併 |
   |---|---|---|---|
   | `auth::enforce::no_escalation_check`（四參掛點） | 路徑級上限位（操作者×路徑×方法） | 恆 `Ok`；簽章、唯一呼叫點與測試旗標可觀察形不動 | 取不到 body 與鎖內 T（替代案 1） |
   | `auth::no_escalation::assert_no_escalation`（經 `handler::user::guard_no_escalation`） | 請求級指派集（A／T／N） | 判 `T ⊆ A ∧ N ⊆ A` | 唯一同時見三元且在鎖內之位置 |

   - 兩位並存＝分工，不是重複實作、亦不是「該把中介層那支補起來」；上提中介層屬新拍板。
   - 讀法三處：ADR-00014 後果段「本體刀只填掛點函式體、零簽章變更、零呼叫端改動」＝掛點、簽章與呼叫端確實零改動，本體在 handler（ADR-00014 不翻案、不 supersede）；002 刀 spec FR-013「MUST 留空 no-escalation 掛點（簽章預留非同步與資料庫句柄、本刀恆放行）」＝路徑級空掛點為設計終態、字面續真（同條「判定進入點介面不變」句之語境為 003 刀接真 session、亦續真）；ADR-00064 翻案觸發器首條「填入…掛點本體」＝落地包含規則本體、落點為本表第二列。
6. **射程只限使用者域與 unlockLogin 帳號維**（Q7；spec FR-023），不掛者與理由：
   - 角色域寫端（新增、更新、刪除、批刪、首頁寫）：標的為角色、非使用者，無 T／N；「只能治理自己持有之角色」屬另一條角色維規則、未入本刀。
   - IP 域寫端：標的為規則列、無角色集。
   - 授權回收桶復原與三維授權寫端：政策列（33、54、57、71）皆受保護＝屬封死集（ADR-00064 決定 1）⇒ 只授 R_SUPER、可達操作者恆為全集 ⇒ 掛之恆真；其標的為授權列、亦無使用者之 T／N。授權維之委派續由 ADR-00064 翻案觸發器首條承接。
   - 上列之下放效果續為 ADR-00068 款 9 之已知態；款 9 中 unlockLogin 列「無帳號維守門」之解除與使用者域列之改述由 ADR-00081 承載。
   - updateUserSessionPolicy 之政策列（68）屬封死集 ⇒ 生產面可達操作者恆持 R_SUPER；仍為九消費點之一（使用者寫端全集一體適用，移出任一支＝方向性變更），其負向測以測試直種政策列構造（spec FR-025）。
7. **與撤銷拒、封死之邊界**（ADR-00064 翻案觸發器次條、ADR-00063 翻案觸發器島 I 入憲條之複核結論）：
   - 判定位次與拒因鍵不互吞：包含規則只掛使用者寫端與 unlockLogin；撤銷拒（`biz.role.protectedRevoke`）與封死（`biz.role.protectedGrant`、復原第③腿之 `biz.policy.notRestorable`）只掛三維授權寫端與授權回收桶復原——兩組端點不相交，任一請求至多遇其中一組；拒因碼亦分（`5003` 對 `2222`）；ADR-00064 決定 3 之「先判撤銷、再判授予」原樣。
   - 正交分工維持：封死＝角色維（非 R_SUPER 角色不得持有封死集）、包含規則＝操作者維（動不了搆不到的人、發不出自己沒有的角色）；封死不因本規則落地而撤，島 G6 條文毋須修改。
   - 授權回收桶復原不掛（決定 6）。
   - ADR-00064 翻案觸發器首條：本刀之委派需求（使用者寫端下放）使其成立、本體落點依決定 5；授權維之委派需求未出現，該條之授權維半續留。
8. **機器守**：
   - `rust-api/server/tests/authz_entrypoint_lint.rs` 增腿：`guard_no_escalation(` 之生產呼叫點檔集與名冊 `NO_ESCALATION_CALL_FILES`＝[`handler/throttle.rs`, `handler/user.rs`]（路徑字典序；`verdict` 斷言 `roster.is_sorted()`）兩向恰等；一正一反自證（RL-0080：名冊外生產面植入必紅、名冊檔拔除呼叫必紅）。前代兩張名冊合一。
   - 純函式表驅動：全集、子集、同級、T＝∅ 四正例與 T 違規、N 違規兩負例；另以「只 T 違規」「只 N 違規」兩最小案證兩條合取各自必要。
   - 每個消費點（spec FR-025，plan 期修補後字面）：負向兩案（被授權之非超管對持 R_SUPER 之標的仍 `5003`；帶指派之消費點〔addUser／updateUser〕另配指派超出自身角色集仍 `5003`、其餘消費點另配標的持操作者未持之角色仍 `5003`，restoreUser 以合成「已刪列仍掛指派」態構造〔生產恆 T＝∅〕；授權以資料列直種、測後清理）＋正向（Super 只持 R_SUPER 而對持其未持角色之標的成功＝A 全集非 vacuous）＋停用角色計入 T 一案；拆掉任一消費點之判定呼叫必有測試轉紅；unlockLogin 帳號維套、來源維不套各一案（spec FR-025、SC-004）。
9. **前端不預判**（spec FR-024）：角色下拉全列（含 R_SUPER）、列級鈕只依按鈕碼顯隱；被拒走共用攔截層之 `5003` 提示。

## 後果

- 新建：`auth/no_escalation.rs`、`handler/user.rs` 之 `guard_no_escalation`；`sys_user_role` 擴兩支料源讀端；unlockLogin 帳號維改開交易。
- 成本：非超管操作者每次寫入多兩次查詢（A、T）、超管一次（A）；批次刪除 T 逐筆一次。
- BL-00048 於收刀 backlog_done。兌現連動面（RL-0011）：`auth/enforce.rs` 預告句 6 處（「本體刀」字面 5 處＝模組 doc 之掛點條目〔「空殼／本體刀接手只填函式體」〕、`no_escalation_check` doc、`enforce_role_path_method` 內註、兩支掛點測試 doc；另模組 doc 首段「no-escalation 本體…屬後刀域、不帶」之本體半）；`handler/throttle.rs` 檔頭「授出後無帳號維守門」「不帶 rev5 後刀才加的帳號維 no-escalation 守門」兩句；`auth/mod.rs` 模組 doc「模組恰兩支＋一型」；`handler/throttle.rs` 檔頭「rev6 差異：稽核列走 facade 的裸連線單寫入口 `sys_operation_log::write`」與 `model/facade/sys_operation_log.rs` 模組 doc「[`write`] 只收裸連線——解鎖端點…沒有業務列可綁」兩句（改述為帳號維交易內寫、來源維裸連線）；`sys_user::advisory_lock_user` doc「首個動作」句（決定 4）；活書 08 §8.3 之「no-escalation 掛點＝…空掛點」「no-escalation 本體＝島 I 承襲指針」兩句與檔頭授權慣例行；`authz_entrypoint_lint.rs` 檔頭「六個側面」。種子＝「本體刀」「屬後刀域」「空殼」「恰兩支」「六個側面」「無帳號維守門」「裸連線」「首個動作」，施工時以 `python3 tools/docsync errata <詞>` 現算、改完復掃；accepted 之 ADR-00014／ADR-00064／ADR-00068 本文不改。
- 活書 06 增島 I 情境之包含規則判定序（spec FR-059）。
- 機器守邊界：名冊腿只數 `guard_no_escalation(` 使用點；繞過包裝直呼 `assert_no_escalation` 之形不在該腿射程、由審查兜底（前代另以一張名冊守此形，本刀合一時未納）。

## 翻案觸發器

- 角色域或 IP 域出現委派需求（非 R_SUPER 須治理角色或規則而不得超出自身）⇒ 新 ADR 設計該域之對應規則、複核決定 6。
- 授權維委派需求出現、或封死集鬆綁使三維授權寫端或授權回收桶復原可授非 R_SUPER ⇒ 依 ADR-00064 翻案觸發器首條與決定 4 立 ADR，並複核決定 6、決定 7。
- 要把判定上提中介層（帶 body）或改判定進入點簽章 ⇒ 新 ADR、走 §V.2。
- 改變 A／T／N 任一取法（A 含停用角色、T 濾停用角色、超管不再視為全集、任一使用者寫端移出射程、改由前端預判）⇒ 島 I7 方向性變更＝MAJOR。
- unlockLogin 來源維需要操作者維守門（例：來源桶與帳號綁定之新模型）⇒ 複核決定 4。
- 帳號維之「帳號名解析先於取鎖」已知態被實測觸發、或出現帳號刪除後同名重建之營運流程 ⇒ 決定 4 改為 advisory 後以帳號名鎖內重解析（uid 不同即以新 uid 重取鎖再判、至多一次）。
- 新增以使用者為標的之寫端（例：批次復原、匯入）⇒ 掛同一包裝、擴名冊並更新決定 1 之 N 表。
- 角色分級需求出現 ⇒ 複核替代案 2。
