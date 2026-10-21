---
id: "ADR-00108"
title: delta migration m0004（rev6 第二支 delta）——建 `reaper` 最小權限 role（NOLOGIN、已存在即略過）＋GRANT（`sys_token` 與四稽核表 SELECT／DELETE、操作日誌 INSERT＋序列、授權域三表 SELECT）；選單 77 按鈕清單增 `audit:purge`、R_SUPER 按鈕授權列 165（不受保護）；演進帳 E-010／E-011、序號合成；權限面不入演進帳；BL-00148 離線對賬腿為其前置
date: 2026-10-21
status: proposed
supersedes: []
superseded_by: []
provenance: "008-audit-settings-pages 之 spec FR-039～FR-042、US6 第 2～4 條、SC-010、Edge Cases「m0004 與 seed」、一次性遷移三欄表；brainstorm §0 B1、B4（授權域唯讀）、D6（`audit:purge` 併入 m0004）、主線工程判斷⑪⑫；clarify 步主線工程判斷（m0004 一支）；plan 期 research R12（語句、新列 id 與冪等、演進帳兩筆、離線腿判準與掛點）、R11.9（權限測形）、spec 修補 E4；藍本＝rev4:migration/src/m012_reaper_role.rs、rev4:migration/src/m013_reaper_audit_grants.rs；rev6 前例＝ADR-00085（m0003 形：影響列數斷言、顯式新列 id、setval GREATEST）、ADR-00087（schema-definition 不前進）、ADR-00008／ADR-00010（四碼檔名、delta 自 m0003 起）；BL-00148（下一支 delta 進場之單元起手前補零 docker 離線對賬腿）"
tags: [migration, seed, reaper, authz-governance, schema-gate]
---

## 背景

- reaper 需專屬最小權限 role（`deploy/setup-reaper-role.py` 只 `ALTER ROLE reaper`、期待 role 由 migration 建；`deploy/generate-secrets.py` 之連線字串寫死使用者 `reaper`）。
- D6 拍板 `audit:purge` 按鈕碼與 R_SUPER 授權列併入 m0004；選單 77 之按鈕清單現為 NULL。
- schema 閘照相只含欄、索引、約束與資料＝看不到角色與 GRANT。
- BL-00148：delta migration、演進帳與凍結 seed 三者一致性只由需 docker 之 `check` 承載。

## 考慮過的替代案

1. **拆兩支（role 與 seed）**——D6 字面「併入 m0004」；兩支可半套用；否決。
2. **新列 id 交序列自配**——全新庫與 dev 庫 id 不一、演進帳 pk 不定；否決（顯式 165）。
3. **權限面登入演進帳新 kind**——schema 閘照相不及、新 kind 無比對面；否決（權限測承擔）。
4. **離線腿遇 DDL 一律略過不列**——未分類語句無聲通過；否決（結構化分類、未分類即紅）。

對所選方案跑同一反例（RL-0013）：「GRANT 射程過寬無人察覺」→`SET LOCAL ROLE reaper` 之權限外負向案；不成立。「dev 庫重跑撞既有 role」→`duplicate_object` 略過；不成立。

## 決定

1. **檔與序**：`rust-api/migration/src/m0004_reaper_role_and_audit_purge.rs`；`lib.rs` 遷移向量第四支；以 compose `database_url` 身分執行（具建立角色之權）。
2. **up**：角色（`DO` 塊、`duplicate_object` 略過）→GRANT 六條（schema USAGE；`sys_token` SELECT, DELETE；四稽核表 SELECT, DELETE；`sys_operation_log` INSERT；`sys_operation_log_id_seq` USAGE；`casbin_rule`、`sys_menu`、`sys_role` SELECT）→選單 77 `buttons` NULL→`[{"code":"audit:purge","desc":"清理日誌"}]`（期望 1 列）→`casbin_rule` 列 165（`R_SUPER`／`audit:purge`／`button`、受保護 FALSE、治理欄照 seed 形；期望 1 列）→`setval('casbin_rule_id_seq', GREATEST(165, last_value), true)`；影響列數不符＝整支回滾。
3. **down**：刪列 165（全欄比對、期望 1）→選單 77 回 NULL（比對新值、期望 1）→逐條 REVOKE→角色無依賴時刪除（`DO` 塊內 `DROP ROLE IF EXISTS reaper`、捕 `dependent_objects_still_exist`〔叢集內他庫仍有其授權或物件〕即略過並 `RAISE NOTICE`，整支 down 不因此失敗；`rev4:m012` 之無條件 DROP 不帶）→序列回推（m0003 形）。
4. **seed 基線層**：seed 兩筆屬 seed 基線層級決策（島 G 之 G2 末句同層）——直接改列、不走執行期撤銷歸檔與操作稽核；`audit:purge` 不受保護（可撤、可授）。
5. **演進帳**：E-010（`seed_update` `sys_menu` 77 `buttons`）、E-011（`seed_add` `casbin_rule` 165）；`knife`＝`008-audit-settings-pages`；序號合成依 E-011 推進期望值；角色與 GRANT 不入演進帳；schema-definition 不前進（ADR-00087）。
6. **連動改對**：授權列 163→164、序號 165、受保護 25 不變、R_SUPER 按鈕碼 21→22、Super 之帳號資訊按鈕集含 `audit:purge`；seed 錨定測與現在式文件同批。
7. **權限測**：容器全量測試內以 `soybean` 連線、交易內 `SET LOCAL ROLE reaper` 執行允許語句（成功）與權限外語句（SQLSTATE 42501）後回滾；以 reaper 憑證實連之驗證＝設密腳本自驗＋jobs profile 活體一輪。
8. **BL-00148 前置**：零 docker 離線對賬腿（`tools/schema-gate.py offline`；語句分類＋seed DML 對賬＋凍結前值對賬＋權限面結構化列出；pre-commit `schema-offline` 段）於撰寫 m0004 之單元前落地並先對 m0003 綠；`check` 不進常跑鏈。
9. **Day-1 登記三步**：收刀前 RUNBOOK §10（第 3 步以一次性 pristine 庫驗；角色於該叢集新建）。

## 後果

- 判定面開機全量載入：dev 庫於 rust-api 在跑時手動遷移須重啟 rust-api。
- 日後改用無建立角色權之託管庫＝m0004 失敗，須另議（spec Edge Cases）。
- dev 庫序號若已前進致 id 165 被佔＝走查基準還原後重跑。

## 翻案觸發器

- reaper 需新權限（新 job 或新表）⇒ 新 migration 補 GRANT（已套用之 m0004 不改檔）。
- 出現權限面之機器對照需求 ⇒ 重評演進帳 kind。

## 親決分類

依 ADR-00089（RL-0086）；類別定義同 ADR-00099 本節。

| 款 | 類別 | 出處或理由 | 白話一句 |
|---|---|---|---|
| 決定 1 | 承決 | brainstorm ⑪；spec FR-039（一支）、Edge Cases「m0004 與 seed」 | 一支遷移，用有建角色權的身分跑。 |
| 決定 2 | 承決 | brainstorm B1、B4、D6；spec FR-039 表；按鈕說明字面「清理日誌」＝user 2026-10-21 plan 第 3 題答（建議；原草稿字面「清理稽核紀錄」為新 seed 字面、無 user 出處＝待決） | 建清理專用帳號並只給必要權限，加清理按鈕碼（說明「清理日誌」）與超管授權。 |
| 決定 3 | 承決 | spec 一次性遷移三欄表 Rollback 欄（撤 GRANT、角色無依賴時刪除、刪新列、選單 77 按鈕清單回 NULL）；`DO` 塊與例外捕捉屬款內工程細節 | 退回時刪掉新增的兩筆資料、撤銷權限，reaper 角色沒有其他依賴時一併刪除。 |
| 決定 4 | 承決 | spec FR-039 末段、Edge Cases（`audit:purge` 不受保護） | 這兩筆是基線資料的直接修改，按鈕碼可撤可授。 |
| 決定 5 | 承決 | spec FR-040 | 兩筆資料改動登入演進帳，權限面不登。 |
| 決定 6 | 承決 | spec FR-042 | 依新列數與按鈕碼修正測試與文件。 |
| 決定 7 | 工程 | research R11.9；spec 修補 E4 | 用切換角色的方式測權限，實際帳號登入另外跑一輪驗。 |
| 決定 8 | 承決 | brainstorm ⑫；spec FR-041；BL-00148 觸發條件 | 先補不用 docker 的遷移對賬檢查，再寫這支遷移。 |
| 決定 9 | 承決 | spec FR-040 | 收刀前照手冊做三步登記。 |

- **親決紀錄**：（plan 期）獨立核對（ADR-00089 決定 5；2026-10-21）：9 列中相符 7（決定 1、4～9）、升待決 2——決定 2（選單 77 按鈕說明字面為新 seed 字面、無 user 出處；另「GRANT 七條」與所列六組不一致）、決定 3（反向遷移屬 migration 內容、原標工程；款文無條件 DROP ROLE 偏離 spec 三欄表「角色無依賴時刪除」）。處置：決定 2 改「GRANT 六條」、說明字面於 plan 期 AskUserQuestion 一題——user 2026-10-21 答「清理日誌（建議）」（作答時 HEAD＝`926b359`、草稿未入版控），改標承決；決定 3 對齊 spec 三欄表改「角色無依賴時刪除」、改標承決（出處＝spec 條目、免問）；改過之款於轉 accepted 前依 ADR-00089 決定 6② 復核。
