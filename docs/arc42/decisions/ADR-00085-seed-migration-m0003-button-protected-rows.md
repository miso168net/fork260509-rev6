---
id: "ADR-00085"
title: seed-only migration m0003（rev6 首支 delta）——R_SUPER 名下角色與選單六碼改受保護（按鈕維受保護列首例）、刪 R_ADMIN `user:edit`（列 44）、增 R_SUPER `ipRule:unlock`（列 164）與 `manage_ip-rule` 按鈕清單一碼；seed 基線層直接改列、單一交易五句逐句斷言、前置不符整支回滾（fail-loud）；演進帳九筆＋schema 閘 seed_add 序號合成；走查還原工具之遷移帳前置與 seed 合成（兩模式之系統設定比對、清理面 seed 列照舊拒跑）；ADR-00064 背景「按鈕維受保護 0 列」之讀法
date: 2026-10-05
status: accepted
supersedes: []
superseded_by: []
provenance: "007-user-password-admin 之 spec FR-041（m0003 逐列改動表與遷移後期望）、FR-042（六碼受保護之撤銷拒、按鈕維受保護列不入封死集、ADR-00064 背景註記）、FR-044（Admin 不再持 `user:edit`）、FR-045（演進帳九筆、seed_add 序號合成、Day-1 登記三步）、FR-046（seed 錨定測試與現在式文件改對）、FR-057 (a)(b)(c)（走查還原工具遷移帳前置與 seed 合成；(b) 之範圍＝user 2026-10-05 裁定本刀做、同日納入系統設定）、FR-062、US6 AS2／AS4～AS7、SC-007、SC-008、Edge Cases「自鎖防護與 seed 基線」「測試與走查基建」、一次性遷移三欄表（m0003）、刻意分岔登記表「R_SUPER 角色與選單六碼」「Admin 預設之使用者頁」兩列；brainstorm §0 GR1／GR1a（六碼受保護；非建議項）／GR4（`ipRule:unlock`；非建議項）／GR7（刪列 44）／GR8（schema-definition 不前進）／GR9（seed_add 序號合成）、主線工程判斷⑰（seed 基線層讀法：島 G 之 G2 末句「受保護集之變更屬 seed 基線層級決策」）、§3 §4 風險 R10／R11；plan 期主線定案（m0003 檔名與單一交易五句形、新列顯式 id 164 與冪等形定義、`ipRule:unlock` 說明字面、演進帳九筆之形、序號合成之語意、走查還原工具清理面擴入經手表）；ADR-00008（migration 短號四碼）、ADR-00010 決定 1（第一支 delta 自 m0003 起編）／決定 2（凍結面永不改寫）、ADR-00009（m0001／m0002 屬憲法 §I.5 例外②）、ADR-00064 背景與決定 1／4／5、ADR-00065 決定 1（`button_revoke` 不可復原）、ADR-00071 翻案觸發器首款；契約＝`docs/ops/reference-src/schema-evolution-contract.md` §1～§3、`docs/ops/reference-src/schema-gates.md` §2／§5；前代無藍本（`rev5:007` 零 migration、rev5 無 delta migration）；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research R21（ADR 配號與親決時點表）"
tags: [schema, migration, seed, casbin, governance, walkthrough, user-password-admin]
---

## 背景

- **自鎖兩路**（brainstorm R10；GR1、GR1a、GR1b）：R_SUPER 名下 `role:add`／`role:edit`／`role:delete`／`menu:add`／`menu:edit`／`menu:delete`（seed 列 58～63）為非受保護之按鈕維授權，本刀起角色頁與選單頁依碼顯隱後，超管可於「按鈕權限」彈窗自撤：撤 `role:edit`＝角色頁編輯鈕消失，而三顆授權彈窗只掛在角色編輯抽屜之編輯模式＝無 UI 回復路徑；按鈕維撤銷屬不可復原集（ADR-00065 決定 1）⇒ 只能直打 API 或改庫。第二路＝選單編輯移除按鈕碼致絕版連動歸檔（由 ADR-00086 封）。
- **GR7**：R_ADMIN 持 `user:edit`（列 44），而 `updateUser` 端點只授 R_SUPER ⇒ Admin 見編輯鈕、送出必 `5003`。**GR4**：IP 規則頁來源 IP 解鎖鈕用新碼 `ipRule:unlock`（選單 78 之按鈕清單增碼＋R_SUPER 授權列）。
- 現況量測（2026-10-05；`rust-api/migration/src/m0002_baseline_seeds.rs` 之 `SEED_CASBIN_RULE`／`SEED_SYS_MENU` 逐列解析；只供背景）：授權列 163、id 上界 163、`casbin_rule_id_seq` 落值 163；受保護 19 列、皆屬 R_SUPER（端點維 15、選單維 4、按鈕維 0）；按鈕維 24 列（R_SUPER 20、R_ADMIN 3＝列 42 `B_CODE2`／列 43 `B_CODE3`／列 44 `user:edit`、R_USER_COMMON 1）；`ipRule:unlock` 零命中；選單 78（`manage_ip-rule`）之按鈕清單四碼（`ipRule:add`／`ipRule:edit`／`ipRule:delete`／`ipRule:restore`）；六碼所在選單＝列 4 `manage_role`、列 5 `manage_menu`，兩列 `protected`＝TRUE。
- 凍結面字面形（`specs/001-schema-baseline/fixtures/seed.sql`；gate2 seed 面以 COPY 文本逐列比對）：`created_at`＝`2026-08-05 00:00:00+00`、`protected`＝`t`／`f`、`sys_menu.buttons`（jsonb）＝`[{"code": "ipRule:add", "desc": "新增IP規則"}, {"code": "ipRule:edit", "desc": "編輯IP規則"}, {"code": "ipRule:delete", "desc": "刪除IP規則"}, {"code": "ipRule:restore", "desc": "恢復IP規則"}]`（鍵後與元素間各一空白）；`tools/schema-gate.py` 之 `copy_literal` 對字串值逐字比對、不做型別正規化。
- **閘缺口（GR9）**：`tools/schema-gate.py` 之 `apply_seed_entries` 對 `seed_add` 只補資料列、不推序號；gate2 seed 面比對 setval 行 ⇒ m0003 之新列（序號 163→164）即紅。`seed_update`／`seed_delete` 合成已內建。
- **走查還原工具缺口**（`tools/walkthrough-baseline.py`，檔形 v3）：①基準檔不記遷移帳 ⇒ 以 m0003 前拍之基準（含 006 刀終態基準）還原會刪列 164、補回列 44、序號撥回 163，而列 58～63 之受保護旗標與選單 78 之按鈕清單不還原＝半新半舊；遷移帳仍記 m0003＝不重跑；收尾比對 rc 1 時寫入已提交、無工具修路。②seed 模式於演進帳有角色／選單域或 `system_settings` 之 `seed_*` 登記即拒跑；兩模式之 `system_settings` 比對左源只讀凍結段 ⇒ m0003 登記後 seed 模式（RUNBOOK §9c 對走查外殘列之補救）斷路；日後任一支改系統設定之 migration 即令兩模式皆拒跑。
- compose 之一次性 `migrate` 服務每次 stack 啟動以 `rust-api` 工作樹（bind mount）套用未跑之 migration、rust-api 依賴其成功結束（`service_completed_successfully`）⇒ m0003 進 dev 庫之時機隱性；失敗＝rust-api 不啟動、`up --wait` 非零。
- ADR-00064 背景量測「按鈕維 0 列」與決定 5 末句「v2＝`button` 之受保護列現無、同理不入」；ADR-00071 翻案觸發器首款「首支寫入或改動 `sys_menu` 列 `component` 之 delta migration」。
- RUNBOOK §10 Day-1 登記紀律之「唯一操作分岔：本刀含刪除性演進＝不入本檔」——「刪除性演進」＝演進帳契約 §2 斷言 6 之 `drop_*`（結構刪除），`seed_delete` 為契約 §1 kind 枚舉八值之一、照常登記。

## 決策驅動因子

- 自鎖兩路同刀封住；受保護集之變更只走 seed 基線層（島 G 之 G2 末句）、一般管理介面永不提供。
- 零 DDL；不碰 m0001／m0002 程式內容（憲法 §I.5 例外②、ADR-00009）與凍結 fixtures（ADR-00010 決定 2）。
- 決定性：dev 庫與 pristine 庫同結果，否則 fail-loud；不靜默錯、不吞錯。
- schema 三閘比對架構零改動（GR8），只補 seed_add 序號合成（GR9）。
- 走查還原工具對 delta migration 不留混合態、不留無工具修路；`seed_*` 演進（清理面除外）之後不須逐支擴工具——含系統設定（user 2026-10-05 納入）。

## 考慮過的替代案

1. **碼內特判保護 R_SUPER 六碼**（按鈕維寫端擋撤、或後端對 R_SUPER 恆回全按鈕碼；R10 落選候選③④）：與 `casbin_rule.protected` 平行之第二份受保護真相；GR1 user 選受保護旗標。否決。
2. **記已知態＋RUNBOOK 救援步驟**（R10 候選⑤）：GR1 否決。否決。
3. **冪等形取 `ON CONFLICT DO NOTHING`／`WHERE NOT EXISTS`**：id 164 被走查殘列佔用而內容不同時靜默跳過＝seed 不一致、由 gate2 晚報；前置不符應即失敗。否決。
4. **新列不顯式 id（吃 nextval）**：dev 庫序號已前進時 id 不定，`seed_add` 須帶全欄確定值（含 id）而無從登記；pristine 與 dev 分岔。否決。
5. **改 m0002 字面**：越憲法 §I.5 例外②；凍結 fixtures 永不改寫。否決。
6. **刪列 44 改為移入授權歸檔（`button_revoke`）**：歸檔列是執行期撤銷之史、seed 層無操作者；授權歸檔表多出 seed 外列＝另需登記；島 G 之 G3 管執行期寫端。否決（工程判斷⑰）。
7. **選單 78 之審計欄寫 `now()`**：seed 列審計欄恆 NULL；`now()` 不可合成 ⇒ gate2 永紅。否決。
8. **序號不推、另以新 kind 登記 setval**：演進帳 kind 枚舉恰八值（契約斷言 5）、新增 kind 屬契約變更、射程大於 GR9。否決。
9. **走查還原工具遇遷移帳不同步「照跑並警告」**：寫入已提交才報＝無工具修路之混合態。否決。
10. **seed 合成只做角色／選單域、系統設定照舊拒跑**（spec 定稿前之形）：日後一支改設定之 migration 即令兩模式皆不可用、須再擴工具；user 2026-10-05 納入系統設定。否決。
11. **清理面各表之 seed 列亦合成**：其還原＝整表清空、以 seed 恆零列為前提；合成須改寫清空語意為「刪 seed 外列」、射程大；目前無此 migration。否決（照舊拒跑、翻案觸發器承接）。

對所選方案跑同一反例（RL-0013）：
- dev 庫序號已前進且殘列佔 164 或同鍵（`unique_key_sea_orm_adapter`）→ 句③ 23505 → 整支回滾、遷移帳不記、rust-api 不起 → 修路見決定 11。成立（不靜默）。
- 列 44 已被走查撤掉 → 句② 0 列 ≠ 1 → 回滾；列 58～63 任一已為受保護（只有直改庫可致）→ 句① 5 ≠ 6 → 回滾；選單 78 按鈕清單於 dev 被編輯過 → 句④ 舊串全等不中 → 回滾。成立。
- 拆掉序號合成 → gate2 之序號期望 163 對實庫 164 不等即紅（自測變異）。成立。
- 以 m0003 前拍之基準還原 → (a) 寫入前拒跑、零寫入。成立。
- repo 已含 m0003 而 dev 未套、跑 seed 模式 → (b) 同步前置拒跑。成立。
- 系統設定日後由 migration 改值 → 兩模式以合成值比對、值相等不報差不拒跑。成立。
- 封死集被 m0003 擴大？新受保護列 v2＝`button` ∉ HTTP 方法白名單 ⇒ 封死集與 m0003 前逐鍵相同。成立。
- 受保護按鈕列經執行期路徑離開現役？手動撤銷＝`biz.role.protectedRevoke` 整批拒；刪角色＝R_SUPER 受 seeded 守門擋刪；選單刪除＝`manage_role`／`manage_menu` 受保護、不可刪；選單編輯移除＝ADR-00086 整筆拒 ⇒ 恆零。成立。

## 決定

1. **檔與形**：`rust-api/migration/src/m0003_seed_button_governance.rs`（`seaql_migrations.version`＝檔名主幹；`Migrator::migrations()` 向量依序 append 為第三支）；seed-only、零 DDL、不建表。rev6 新寫碼（不屬憲法 §I.5 例外②之 17 檔）＝一般 rustfmt 紀律、無 rev5 對應檔。
2. **up＝單一遷移交易內五句、依序執行**（遷移框架之交易包覆＝失敗零殘留，與 m0002 模組文件所述「框架交易保證失敗零殘留」同一前提；U4 以 pristine 庫之強制失敗演練佐證、含遷移帳未記一項）：
   - ①`UPDATE casbin_rule SET protected = TRUE`，WHERE 帶 `id IN (58,59,60,61,62,63)`、`ptype='p'`、`v0='R_SUPER'`、`v1` 屬六碼、`v2='button'`、`protected = FALSE` ⇒ 影響列數 MUST＝6。
   - ②`DELETE FROM casbin_rule`，WHERE 帶 `id = 44`、`v0='R_ADMIN'`、`v1='user:edit'`、`v2='button'` ⇒ MUST＝1。
   - ③`INSERT INTO casbin_rule` 十一欄顯式值 `(164, 'p', 'R_SUPER', 'ipRule:unlock', 'button', '', '', '', FALSE, '2026-08-05T00:00:00+00:00', NULL)`（`created_at` 照 seed 固定字面、`created_by` NULL、受保護 FALSE）；不帶 `ON CONFLICT` ⇒ MUST＝1，id 佔用或同鍵即 23505。
   - ④`UPDATE sys_menu SET buttons = <新串>`，WHERE 帶 `id = 78` 且 `buttons = <舊串>`（jsonb 等值）⇒ MUST＝1；新串＝舊四碼原序＋尾端 `{"code":"ipRule:unlock","desc":"解鎖來源IP"}`（說明字面沿既有四碼之繁中無空格形）；★只動 `buttons`、審計欄不動（seed 列恆 NULL）。
   - ⑤`SELECT setval('casbin_rule_id_seq', GREATEST(164, 現值), true)`（序號只進不退）。
   - ①～④任一影響列數不符 ⇒ 回 `Err`（訊息指名句號、期望與實得）⇒ 整支回滾、遷移帳不記 ⇒ `migrate` 服務非零退出 ⇒ rust-api 不啟動、`up --wait` 非零（fail-loud）。
   - **冪等形之定義**：成功只跑一次（遷移帳）；失敗整支回滾、可安全重跑；前置不符即失敗、不吞錯。
3. **down＝逐句反向**：④′ 選單 78 回舊串（WHERE 新串全等）→ ③′ 刪列 164（WHERE 十一欄全等）→ ②′ 列 44 原值回插 → ①′ 列 58～63 改回 FALSE（WHERE `protected = TRUE`）→ ⑤′ `setval('casbin_rule_id_seq', GREATEST(163, (SELECT COALESCE(max(id), 0) FROM casbin_rule)), true)`（全新庫往返回 163；序列已前進之庫不倒退）；①′～④′ 同以影響列數斷言。
4. **seed 基線層之讀法**（島 G 之 G2 末句、工程判斷⑰）：直接改列——不走執行期撤銷歸檔（G3 管寫端）、不寫操作稽核（G1 管寫端）、不觸判定面同步（`migrate` 先於 rust-api 啟動、開機全量載入）；本 migration 即「受保護集之變更」之合法形，一般管理介面永不提供設定或解除受保護旗標（G2）。dev 庫於 rust-api 在跑時手動跑遷移（`run --rm migrate`）⇒ MUST 重啟 rust-api 使判定面載入新值。
5. **遷移後期望**（FR-041、SC-007）：授權列 163（刪一增一）、`casbin_rule_id_seq` 164、受保護 25 列（端點維 15、選單維 4、按鈕維 6；皆屬 R_SUPER）、選單列 78 不變、migration 目錄恰三支；R_ADMIN 按鈕碼餘 `B_CODE2`／`B_CODE3`；R_SUPER 按鈕碼 21（增 `ipRule:unlock`）。
6. **演進帳九筆**（`docs/ops/reference-src/schema-evolution.json`；`knife`＝`007-user-password-admin`、`date`＝登記當日、登記後 `next_id`＝10）：
   - E-001～E-006：`seed_update`、`casbin_rule`、`{"pk": {"id": 58～63 各一}, "set": {"protected": true}}`。
   - E-007：`seed_delete`、`casbin_rule`、`{"pk": {"id": 44}}`。
   - E-008：`seed_add`、`casbin_rule`、`{"pk": ["id"], "values": {"id": 164, "ptype": "p", "v0": "R_SUPER", "v1": "ipRule:unlock", "v2": "button", "v3": "", "v4": "", "v5": "", "protected": false, "created_at": "2026-08-05 00:00:00+00", "created_by": null}}`。
   - E-009：`seed_update`、`sys_menu`、`{"pk": {"id": 78}, "set": {"buttons": "[{\"code\": \"ipRule:add\", \"desc\": \"新增IP規則\"}, {\"code\": \"ipRule:edit\", \"desc\": \"編輯IP規則\"}, {\"code\": \"ipRule:delete\", \"desc\": \"刪除IP規則\"}, {\"code\": \"ipRule:restore\", \"desc\": \"恢復IP規則\"}, {\"code\": \"ipRule:unlock\", \"desc\": \"解鎖來源IP\"}]"}}`。
   - ★值形一律取 pg_dump COPY 文本形（`copy_literal` 逐字比對）：時間欄＝`2026-08-05 00:00:00+00`（非 m0003 SQL 字面之 `2026-08-05T00:00:00+00:00` 形）、jsonb＝伺服端正規化輸出（鍵後與元素間各一空白、鍵序 `code` 先於 `desc`）；與 m0003 SQL 字面不同形屬預期。以 pristine 重放後 `pg_dump --data-only` 實得字面為準、U4 自測釘住。
7. **schema 閘之 seed_add 序號合成（GR9）**：`tools/schema-gate.py` 之 seed 面合成於 `seed_add` 時，若 `pk` 恰單欄 `c` 且 normalize 後文本有 `SELECT pg_catalog.setval('public.<表>_<c>_seq', N, B);` 行（無此行＝不推進），則期望已發最大值 M＝N（B＝true）或 N−1（B＝false；未動用形 `1, false` 即 0）；新列 id（須為整數、否則 rc 2）大於 M ⇒ 把該行推至（新列 id, true）、否則不動；多筆依 entries 序逐筆推進（取大）；`seed_update`／`seed_delete` 不動序號（只進不退）；多欄 pk 或無序號之表（`system_settings`、`sys_user_role` 等）不推。自測正反各一＋變異自證（拆掉推進 ⇒ 合成案轉紅）；`docs/ops/reference-src/schema-gates.md` §2 seed 面句與演進帳契約 §1 `seed_*` detail 說明同批補一句。
8. **既有 ADR 之讀法**（accepted body 不可變；現在式面引用以本款為準）：
   - ADR-00064 背景「按鈕維 0 列」於 m0003 後為 6 列；其決定 5 末句之結論（按鈕維受保護列不入封死集）不變——判定依決定 1 之 HTTP 方法白名單、白名單字面與 `button` 不相交 ⇒ 封死集與 m0003 前逐鍵相同；決定 4①（封死集成員只隨基線資料層級決策變動）與決定 4②（受保護授權列今皆屬 R_SUPER、不進可復原歸檔）續真；其翻案觸發器中「封死集端點經基線資料層級決策下放」與「以 seed／migration 使封死集擴大」兩款未觸發（m0003 不改端點維列）。
   - ADR-00071 翻案觸發器首款未觸發：m0003 只改選單 78 之 `buttons`、不改 `component`。
   - ADR-00010 決定 1「第一支 delta 自 m0003 起編」由本 ADR 兌現。
9. **走查還原工具（FR-057；檔形 v4）**：
   - **(a) 遷移帳前置**：`snapshot` 另記 `migrations`（`seaql_migrations.version` 有序清單）；基準檔模式 `restore` 於任何寫入之前比對現庫遷移帳，不等＝rc 2、零寫入、訊息指名差異（基準有而現庫無／現庫有而基準無）並指示重拍；`diff` 亦比該欄（不等＝rc 1）；v3 以下舊檔＝rc 2 指名重拍（沿舊檔形慣例）。
   - **(b) seed 合成**：seed 模式之目標態（角色／選單域與本刀擴入之使用者域面）與兩模式之 `system_settings` 比對左源，一律改為凍結 seed ⊕ 演進帳 `seed_*` 合成——語意同決定 7 之 schema 閘合成（含序號推進；否則 seed 模式之「上界高於序列位置」前置會對合成目標誤判）與 docsync 帳號快照投影；`system_settings` 之鍵集與值比對合成值、審計欄一律歸 NULL（現行 restore 語句；`seed_*` 帶審計欄值之演進出現時同批擴充）；值等於合成值者不報差、不拒跑。原「`system_settings` 有 `seed_*` 登記即拒跑」與 seed 模式「角色／選單域五表有登記即拒跑」兩判定撤除、改為合成。
   - **同步前置**：合成所涉之表有 `seed_*` 登記時，現庫遷移帳 MUST 恰等 repo 之 migration 清單（`rust-api/migration/src/lib.rs` 之 `migrations()` 向量所列模組名、並斷言各有 `mod` 宣告與同名 `.rs` 實檔；零解析＝rc 2；遷移版本名＝檔名主幹＝`DeriveMigrationName`；compose `migrate` 服務即掛載此工作樹）；不等＝rc 2、零寫入、指名未套用或多出之遷移。所涉之表：基準檔模式＝`system_settings`；seed 模式＝`system_settings`＋角色／選單域五表＋使用者域面。
   - **清理面邊界**：清理面各表（會話三表、IP 規則、操作紀錄，本刀起含經手表 `sys_pwd_custody`）之 `seed_*` 登記，seed 模式照舊拒跑零寫入並指名登記項（整表清空以 seed 恆零列為前提）；基準檔模式由既有安全帶（基準檔清理面須零列）與 (a) 承擔同一邊界。
   - **合成實作**：執行期依路徑以 importlib 載入 `tools/schema-gate.py`、取 gate2 期望 seed 之同一合成鏈（`normalize_seed_dump`→`apply_seed_entries`）——不自持第二份合成碼（schema 閘之合成日後擴充即兩工具同時生效）；只餵合成面各表之登記；載入失敗或 `GateError`＝rc 2、原訊息照轉；自測另以 docsync 帳號快照投影（`docsync.snapshot.seed_account_projection`）交叉對賬。
   - **(c) 自測與契約**：(a)(b) 各附自測合成案與變異自證（spec US6 AS4～AS7）；工具 docstring 與 RUNBOOK §9c 同批改。
   - **射程界**：此後 `seed_*` 演進（清理面各表除外）不須再擴工具。仍拒跑之演進形恰兩種：①清理面各表之 `seed_*` 登記（seed 模式；見上款）②合成面表之結構演進屬 schema 閘合成未內建之形（帶 default 或 NOT NULL 之 `add_column`）——與 gate2 同 rc 2，於 `tools/schema-gate.py` 同一擴充點補齊即兩工具同時恢復（不須另擴本工具）。新表（`add_table`）不在合成面＝不擋；其餘結構類演進不使工具拒跑（工具以欄名取值、新欄不入回寫射程、新表不入清理面），其新增面若於走查中被寫，由收尾比對報出 rc 1、依 RUNBOOK §9c 判準處置或擴清理面（現行射程界紀律不變）。
10. **單元序與 dev 庫套用**（LL-00053：dev 庫寫入逐步取 user 放行）：(a)(b) 與決定 7 所在單元（U1）MUST 早於撰寫 m0003 之單元（U4）。套 m0003 進 dev 庫（stack 重起之 `migrate` 服務或手動 `run --rm migrate`）之前：先以 U1 所取之 v4 基準跑基準檔模式 `restore`（遷移帳相同＝(a) 前置放行；seed 模式僅於演進帳尚未登記 m0003 時可用、其後依 (b) 同步前置拒跑）使 dev 庫回乾淨態，再以 v4 工具 `snapshot` 一份 m0003 前之基準（遷移帳＝m0001、m0002；供決定 11 修路）；套用成功後即重拍本刀基準。m0003 前所拍之一切基準（含 006 刀終態 v3 基準）此後不再可用。
11. **Rollback**（一次性遷移三欄表）：
    - m0003 失敗（整支回滾、遷移帳未記）⇒ 以決定 10 之 m0003 前 v4 基準 `restore`（遷移帳相同、(a) 放行）⇒ 排除前置不符之因 ⇒ 重起 stack 重跑。
    - 已記帳而列不符（五句逐句斷言下只餘直改庫可致）⇒ 手寫 SQL 回正（刪列 44、補列 164、序號 164 等）或經 user 授權重建 dev 庫（全新庫重放 m0001～m0003）。
    - 撤回 m0003 本身（拍板翻案）⇒ down 遷移＋演進帳以反向四類追加修正筆（契約 §3 append-only：寫錯＝新 entry 修正）＋FR-046 錨測試與文件回退。
    - 工具擴面回退 ⇒ 還原工具與 RUNBOOK §9c 同批回退（seed 模式回到拒跑形）。
12. **連動與收尾**：seed 錨定測試與現在式文件同單元改對（FR-046：受保護 19→25、新列 id 164、R_ADMIN 按鈕集去 `user:edit`、seed 三帳號之帳號資訊按鈕集）；收刀前跑 RUNBOOK §10 Day-1 登記三步，第 3 步以全新庫（`--container`）驗；schema-definition 不前進（ADR-00087）。

- **親決紀錄**：user 親決 2026-10-06（007 刀 tasks T003 施工前提顆）——本輪逐款一題一問呈決定 1～12、皆照文定稿；零非建議項 ⇒ 決定節免改寫；原決定節首之草稿標記改由本紀錄承載。

## 後果

- 自鎖第一路封住：按鈕權限彈窗撤六碼之任一＝`biz.role.protectedRevoke` 整批拒；R_SUPER 之按鈕權限彈窗六碼呈受保護鎖定（現況讀端每項帶受保護旗標）。第二路由 ADR-00086 封。
- Admin 於 seed 預設態只見使用者清單、無操作鈕（刻意分岔登記）；IP 規則頁解鎖鈕有碼可顯隱、R_SUPER 持有。
- 受保護按鈕列首例：ADR-00044 決定 4 之 won't-use 分析續有效（受保護列不進可復原歸檔）。
- gate2 期望＝凍結 seed ⊕ 九筆（含序號 164）；pristine 重放三閘綠、拆序號合成即紅（SC-007）。
- 走查還原工具 v4：m0003 前之基準一律重拍；seed 模式於 m0003 後可用、系統設定日後之演進不再令兩模式拒跑；仍拒跑之演進形兩種＝清理面各表之 seed 列、合成面表之結構演進屬 schema 閘合成未內建之形（與 gate2 同停、同一擴充點補齊即兩者同時恢復）。
- 現在式假述之同單元改寫（RL-0011；種子四形皆跑、處數以 `python3 tools/docsync errata <詞>` 現算、改完復掃；ADR 檔與史料面不動）：「按鈕維 0 列」「按鈕維受保護」（現在式面）、受保護列數「19」之現在式面（schema-definition 屬 001 基線不改）、「零 migration」「兩支」migration 計數句、m0001／m0002 列舉句（活書 05／08、RUNBOOK §10）、走查工具「未合成演進」「先擴充本工具」「清理面五表」「檔形 v3」、RUNBOOK §10「刪除性演進」措辭（明寫＝`drop_*`）。
- 代價：dev 庫套用時機隱性＝寫入點須提前規劃（決定 10）；m0003 前置不符即 stack 起不來（刻意 fail-loud）；down 只保證 pristine 往返。

## 翻案觸發器

- 第二支 delta migration 進場 ⇒ 沿本 ADR 形（逐句斷言、演進帳同批、Day-1 三步）；若屬結構類 ⇒ 複核 schema 閘合成射程（`add_table` 之 seed 面合成未內建＝fail-loud）。
- 首支往清理面各表塞 seed 列之 migration ⇒ 擴走查還原工具（清理語意改為刪 seed 外列）並複核決定 9 之清理面邊界。
- 受保護集再變更 ⇒ 依 G2 走 seed 基線層 migration；涉端點維＝封死集變動、複核 ADR-00064；涉按鈕維＝複核 ADR-00086 之前提。
- R_SUPER 名下非受保護碼被誤撤成為實際問題 ⇒ 評估擴受保護射程（spec Out of Scope「非受保護按鈕碼被誤撤之專屬防護」之翻轉）。
- 遷移框架升版改變交易包覆語意 ⇒ 複核決定 2 之回滾前提。
- 走查還原工具與 schema 閘之合成語意實際分岔一次 ⇒ 收攏為單一實作。
