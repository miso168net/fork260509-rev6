# Research — 006-authz-governance（Phase 0）

> 輸入：spec（以工作樹版為準；Clarifications Session 2026-10-01 共五題——首題為 clarify 定案，第二～五題為 plan 期取證揭出後之 user 裁定：現況讀端取態、首頁下拉寫入時點、換角色清狀態之射程、已知態觀察步驟對 seed 角色寫入之具名例外）＋brainstorm `docs/brainstorms/006-authz-governance.md`（定稿 `e9f5525`＋grilling 輪寫回 `0f7e514`；拍板 Q1～Q17、主線工程判斷①～⑧、設計四節）＋ADR-00063～ADR-00071 草稿＋`rev5:006-authz-governance` 全套與 rev5 凍結 worktree（唯讀；外層 `7eab28a`／rust-api `92919b9`／base-web `9833308`，取證時三處 HEAD 皆核等）＋rev6 碼面唯讀勘查（外層 `316faaf`、rust-api `8c8b5e1`、base-web `2248b89`；兩子庫 pin＝worktree HEAD）。每題 Decision／Rationale／Alternatives。
> **NEEDS CLARIFICATION＝0**：plan 期揭出之拍板級題（四題）已由 user 裁定入 spec Clarifications 第二～五題，其餘皆為工程判斷（逐條附理由；交 tasks 與實作期定值者列 R20）。CLAUDE.md §2 兩件必列＝**R2 rev5 對應碼清單**、**R3 rev6 拍板差異點**（兩支 wire 契約所稱「rev6 差異點」即 R3）；RL-0013 反例回跑＝R19；ADR 時點表＝R16（ADR 與 plan 以其表名引用）。行號不入本檔；一切「新建」件於 pin 樹以 `grep -c` 零命中為據。

## R1 技術脈絡（零新依賴、零 migration、零 seed 變更）

- **Decision**: 本刀**零新依賴、零版本變更**——後端沿 rust 1.96.1（`rust-toolchain.toml`）、casbin **2.20.0**（`default-features = false`；`tests/authz_entrypoint_lint.rs` 之 `CASBIN_VERIFIED` 同值）、axum 0.8.9、sea-orm 1.1.20、tokio 1.53.1、metrics 0.24.6、serde_json 1.0.151；前端沿 vue 3.5.34、naive-ui 2.44.1（`NTree` 既有元件；`cascade` 與 `check-strategy` 皆既有 prop）、treemate 0.3.11、vue-i18n 11.4.2、typescript 6.0.3、`@elegant-router/vue` 0.3.8；wire 抽取沿 TSJS 0.67.4。**零 migration**：`rust-api/migration/src/` 維持 `m0001_baseline_schema.rs`／`m0002_baseline_seeds.rs` 兩支；本刀所用之表面全在 001 刀基線——`casbin_rule` 治理三欄（`protected` NN default false、`created_at` NN default `now()`、`created_by` 可空、無外鍵）與七欄身分鍵唯一索引 `unique_key_sea_orm_adapter`（`ptype`、`v0`～`v5`）、`sys_casbin_policy_archive` 14 欄與兩支索引（`idx_casbin_archive_archived_at`、`idx_casbin_archive_role_dim`＝`(v0, v2)`，恰承回收桶「角色代碼×維度」兩篩與時間降冪序）。**零 seed 變更**：seed 授權列 163（`created_by` 全 NULL）、選單 78、角色 3；本刀十條之 seed 政策列 32／33、52～57、70／71 與頁級選單維列 72 皆既在（皆 R_SUPER、`protected=TRUE`）。
- **Rationale**: 全域 §6 版本紀律；本刀一切能力（全量替換＝集合運算、封死＝單次 SQL 謂詞查詢、復原＝既有表之 INSERT／DELETE、候選＝路由表常數投影）皆可由既有依賴承載。casbin 2.20.0 之 `load_policy` 先清空再載入語意為「全新重建後一步換上」之前提（ADR-00043 決定 5），升版屬翻案觸發；DDL 冒出＝本刀範圍翻案（spec FR-002）。
- **Alternatives considered**: 歸檔表加維度欄或受保護快照欄（需 migration、破 FR-002；維度由列內容推導即足、受保護快照由 ADR-00064 決定 4 承重前提免除，棄）；引入版本欄做並行編輯樂觀鎖（需 migration、Q12 已拍不加，棄）。

## R2 rev5 對應碼清單（實作單元動工前逐檔先讀；rev5 凍結 worktree＝HEAD 終態、含 `rev5:007`／`rev5:008` 增量——逐檔剔除見本節末）

| 面 | rev5 檔::符號 | rev6 落點（既有或新建） | 差異註 |
|---|---|---|---|
| 三維讀寫＋候選讀 handler | `rev5:server/src/handler/role.rs`::`get_role_menu`／`update_role_menu`／`get_role_button`／`update_role_button`／`get_role_endpoints`／`update_role_endpoints`／`get_all_buttons`／`get_all_endpoints`、`active_role_code`、`finish_grant` | rust-api `server/src/handler/role.rs`（既有檔；八支 handler **新建**） | handler 持交易（R6）；`finish_grant` 之請求內 reload 改脫離請求之授予面收場件（**新建**）；操作者取既有私有 `operator_from`、body 取既有 `common::json_or_default` 四參形餵既有 `BODY_FALLBACK_MSG`；授權寫端稽核件**新建**（既有 `record_audit` 綁角色列快照、不套） |
| 三維 DTO | `rev5:server/src/handler/role.rs`::`Endpoint`／`MenuId`／`GrantResult<T>`／三支請求型／`RoleIdQuery` | 同上（DTO 全數**新建**） | `GrantResult<T>` 改三支具體型；選單 id 集合元素以 newtype（**新建**、rev5 對應件 `MenuId`）掛 2^53 守衛（R11）；型名表＝`contracts/wire-authz-governance.md` |
| 端點候選與方法白名單 | `rev5:server/src/handler/role.rs`::`policy_endpoints`／`endpoint_methods`＋`rev5:server/src/router.rs`::`policy_route_defs` | rust-api `server/src/router.rs`（既有檔）::`policy_endpoints()`／`endpoint_methods()`（**新建**） | 落點自 handler 移入路由表同檔；白名單由既有 `HttpMethod` 三變體經既有 `as_str` 導出；facade 以參數收、零 `crate::router` 引用（ADR-00064 決定 1、ADR-00066 決定 3） |
| 授權主 facade | `rev5:server/src/model/facade/sys_casbin_policy.rs`::`Dimension`／`RejectCause`／`PolicyOutcome`／`live_*`／`current_*`／`governed_route_names_by_id`／`map_menu_ids`／`route_names_to_menu_ids`／`RoleDimensionError`／`set_role_*`／`apply_*`／`scope_live_to_candidates`／`plan_full_replace`／`apply_full_replace`／`settle_txn` | rust-api `server/src/model/facade/sys_casbin_policy.rs`（**新建**檔） | 公開寫入口只收 `&DatabaseTransaction`、`set_role_*` 自開交易之殼與 `settle_txn` 不帶（收場屬 handler）；濾點件讀寫兩端共用（rev5 只寫端；ADR-00066 決定 5）；錯誤形屬 `facade/mod.rs` 所稱「後一制」（原樣回 `DbErr`、拒因以業務形回） |
| 封死集 | 同檔::`protected_endpoint_set`；測 `protected_grant_lockout_exempts_super_role_self_grant_but_rejects_other_role` | 同上::`protected_endpoint_set`（**新建**） | 白名單以參數收；探針鍵一律植於第三方合成代碼名下（R8） |
| 撤銷原因、回收桶讀端與復原 | `rev5:server/src/model/facade/sys_casbin_archive.rs`::三撤銷原因常數／`ArchiveDimension`／`dimension_of`／`list`／`RestoreOutcome`／`restore`／`restore_locked`；測 `restore_rejects_each_leg_without_consuming_and_list_flag_agrees`／`is_non_restorable_reason_pins_five_member_set` | rust-api `server/src/model/facade/sys_casbin_archive.rs`（既有檔；三常數、撤銷入口、列表件、復原件**新建**；既有 `is_non_restorable_reason` 3→5） | 角色列改以歸檔 `role_id` 經既有 `sys_role::find_active_by_id_for_update` 鎖讀再比代碼（ADR-00065 決定 4）；23505 收窄不帶（決定 10）；`restore` 自開交易之殼不帶；既有釘案 `archive_reasons_pin_three_literals_and_non_restorable_set_is_exactly_them` 正負臂翻（R9） |
| 回收桶 handler | `rev5:server/src/handler/policy_archive.rs`::`ArchivedPolicyQuery`／`RestorePolicyReq`／`ArchivedPolicy`／`endpoint_candidates`／`get_archived_policies`／`restore_policy` | rust-api `server/src/handler/policy_archive.rs`（**新建**檔） | query 型名兩側統一 `ArchivedPolicyListQuery`；`endpoint_candidates` 改呼路由表兩件；`archivedBy` 經既有 `sys_user::find_names_by_ids`＋本域 `db_failure`（R5）；分頁改既有 `envelope::page_params` |
| 角色讀件 | `rev5:server/src/model/facade/sys_role.rs`::`active_ids_by_codes`／`active_code_of`／`find_active_by_code_for_update` | rust-api `sys_role.rs`（既有檔）::`active_ids_by_codes`（以代碼批次取活角色 id；**新建**）、`active_code_of`（以 id 讀活性角色代碼；**新建**；定名之家＝data-model §13） | 以代碼鎖讀件續不帶（該檔模組 doc 之「不帶」句仍真、不改；其 rev5 取件清單補兩新件＝R17）；復原鎖讀用既有 `find_active_by_id_for_update` |
| 按鈕碼聯集讀端 | `rev5:server/src/model/facade/sys_menu.rs`::`all_button_codes` | rust-api `sys_casbin_policy.rs`（**新建**檔）::`governed_button_codes`（**新建**，經既有 `sys_menu::list_governed`＋`sys_menu::button_codes_of`；落點與 rev5 異＝候選集輔助集中於授權主 facade（R5）、定名之家＝data-model §13） | 壞形 fail-loud（`button_codes_of` 回 `Result` 之既有語意）；`rev5:B-115` 同層序首見去重沿用 |
| handler 共用件 | `rev5:server/src/handler/common.rs`::`audit_operator`／`resolve_operator_names`／`MAX_CURRENT` | rev6 既有 `common::operator_from_context`＋各域 `operator_from`、`sys_user::find_names_by_ids`、`envelope::page_params`／`PAGE_MAX_CURRENT` | 三件皆不帶（005 刀既定；BL-00113 重評結論續行） |
| 判定面同步 | `rev5:server/src/auth/enforce.rs`::`reload_enforcer` doc 觸發矩陣 | rust-api `server/src/auth/enforce.rs`（既有）::`reload_enforcer` | 機制零改；doc 改三類字面（ADR-00067 決定 1） |
| 路由表 | `rev5:server/src/router.rs`::ROUTES 十條 | rust-api `router.rs`（既有）ROUTES 尾接十列、`ROUTES_COUNT` 39→49 | 相對序依 rev5 表序（契約端點總表）；rev5 夾於其間之 getAllPages 為 rev6 既有、不重列 |
| 名冊 lint | `rev5:server/tests/authz_entrypoint_lint.rs` | rust-api `server/tests/authz_entrypoint_lint.rs`（既有） | `RELOAD_CALL_FILES` 加回收桶檔、`DOMAIN_WRITE_SIDE_FILES` 7→8；`rev5:007` 名冊增量不帶（R13） |
| 契約測 | `rev5:server/tests/contract.rs`（`rev5:006` 十案＋授權態矩陣） | rust-api `server/tests/contract.rs`（既有） | case 集 49；直種政策之 raw INSERT 帶建立者（R12） |
| 序列化域機器證 | `rev5:server/tests/menu_domain_serialization.rs`（`rev5:006` 兩案） | rust-api `handler/role.rs` 測試模組（既有 `delete_role_waits_behind_the_menu_domain_holder`／`add_role_passes_the_menu_domain_holder` 形）＋`handler/policy_archive.rs` 測試模組（**新建**） | rev6 無該檔（005 刀已併入 src 側真庫測） |
| wire 裁判 | `rev5:server/tests/wire_schema.rs`（`rev5:dc1cc8c` 十六 definition） | rust-api `server/tests/wire_schema.rs`（既有） | 節謂詞擴 `Api.Authz.`（既有 `in_role_menu_sections` 只認兩前綴；R11） |
| 測試守衛 | 無對應（rev5 守衛寫死序列值、不補 seed 列） | rust-api `src/model/facade/test_kit.rs`（既有 `CasbinRuleRowsGuard`／`PolicyArchiveRowsGuard`／`RoleMenuDomainRowsGuard`、`plant_live_policy`）＋`tests/common/mod.rs`（既有 `CasbinRuleWriteGuard`／`PolicyArchiveWriteGuard`／`RoleMenuDomainWriteGuard`） | 擴補回被撤 seed 授權列、植入件落建立者（R12） |
| 選單權限彈窗 | `rev5:src/views/manage/role/modules/menu-auth-modal.vue`（HEAD 形，含 `rev5:B-116`／`rev5:B-129`） | base-web 同名（既有；blob＝upstream 基線） | 修改型逐行 `原行:`（rev5 首頁寫入函式內以程式行替換佔位註解行而未帶 `原行:` 者逐處補帶）；barrel 匯入行 `fetchGetAllPages, fetchGetMenuTree` 不動（rev5 同） |
| 按鈕權限彈窗 | `rev5:src/views/manage/role/modules/button-auth-modal.vue` | base-web 同名（既有；blob＝基線） | setup 直呼 `init()` 改 `watch(visible)`（rev5 對 rev4 之防回歸） |
| 端點權限彈窗 | `rev5:src/views/manage/role/modules/endpoint-auth-modal.vue` | base-web 同名（**新建**） | 檔頭首行一行 `[rev6-inline MANAGE-ROLE-AUTH-VIEW+ 006-authz-governance]`（R14.4；rev5 之 `(iii)+` 形判紅＝D20）；檔內不開圈界塊 |
| 角色抽屜 | `rev5:src/views/manage/role/modules/role-operate-drawer.vue`（`rev5:006` 三塊） | base-web 同名（既有） | (iii) 3 塊新增型；(ii) 既有圈界內之狀態欄修法（ADR-00070） |
| 回收桶頁 | `rev5:src/views/manage/policy-archive/index.vue`／`modules/policy-archive-search.vue` | base-web 同名兩檔（**新建**） | 兩檔檔頭首行一行 `[rev6-inline MANAGE-POLICY-ARCHIVE-VIEW+ 006-authz-governance]`（R14.6；rev5 之 `(iv)+` 形判紅＝D20）；表格橫向捲動寬＝各欄寬之和（rev5 重算值 1054，rev6 依實際欄寬現算） |
| wrapper／型別 | `rev5:src/service/api/rev5-role-admin.ts`／`rev5:src/typings/api/rev5-role-admin.d.ts` 之 `rev5:006` 段（`Api.RoleAdmin` 三維＋`Api.PolicyArchive`） | base-web `src/service/api/rev6-authz.ts`／`src/typings/api/rev6-authz.d.ts`（**新建**） | 單一命名空間 `Api.Authz`；檔頭首行沿 §III.1 軌道 `[rev6-inline BASE-WEB-WRAPPER+ 006-authz-governance]`／`[rev6-inline BASE-WEB-ADAPT+ 006-authz-governance]`（比照 `rev6-role-admin.{ts,d.ts}` 檔頭形）；`rev6-role-admin.{ts,d.ts}` 零改 |
| locale／型節 | `rev5:src/locales/langs/{en-us,zh-cn}.ts`／`rev5:src/typings/app.d.ts` 之 (iii)(iv) 塊與後端三鍵 | base-web 同名（既有）＋`zh-tw.ts` 後端三鍵 | 塊數：兩語 (iii) 各 1、(iv) 各 2；`app.d.ts` (iii) 1、(iv) 1（ADR-00063 決定二預估依據） |
| seed-view-gate | 外層 `rev5:tools/seed-view-gate.py`（`rev5:9d709d4` 原始版） | 外層 `tools/seed-view-gate.py`（**新建**） | 缺席一律 rc 2、入 pre-commit 自測迴圈、`check` 不跑自測（ADR-00071 決定 4／6） |
| 走查還原工具 | rev5 同名工具（不補 seed 授權列） | 外層 `tools/walkthrough-baseline.py`（既有 `SCHEMA_VERSION` 2） | 基準檔 v3：補回 seed 授權列、seed 角色列可變欄回寫（R12） |

**commit 範圍**：rust-api `rev5:ddbab53`～`rev5:f455858`（12 顆）＋`rev5:006` 後修正 `rev5:6ee82e2`；base-web `rev5:979039fb`～`rev5:673f206e`（6 顆）＋`rev5:ae1ac0c9`（`rev5:B-116`）與 `rev5:fb71df69` 之 `rev5:B-129` 半；外層 `rev5:9d709d4`（seed-view-gate 原始版）。

**rev5 HEAD 含 `rev5:007`／`rev5:008` 增量之逐檔剔除**（量法＝`git -C ../fork260509-rev5/<子庫> log --format=%h <rev5:006 末顆>..HEAD -- <檔>`；取＝本刀面之 `rev5:006` 後修正、等價＝rev6 已由 005 刀或維護批另立同義件、不帶＝`rev5:007`／`rev5:008` 增量或純格式）：
- `handler/role.rs`：取 `rev5:6ee82e2`（`rev5:B-106` 批次讀名之語意；rev6 以既有 `find_names_by_ids` 承）；等價 `rev5:fd23de9`／`rev5:55bb3e3`；不帶 `rev5:7575379`／`rev5:4889b6d`／`rev5:166f90a`／`rev5:d5d5306`／`rev5:be1d7e1`／`rev5:2273816`／`rev5:0161d73`／`rev5:b1ec283`（攜參業務錯誤、no-escalation 八支掛點、`rev5:B-113` 探針、使用者域、碼註訂正）、`rev5:e85f447`／`rev5:7833ec7`（稽核讀端與 purge）、`rev5:d940d03`（存量格式化）。
- `handler/policy_archive.rs`：取 `rev5:6ee82e2`；等價 `rev5:fd23de9`；不帶 `rev5:b1ec283`／`rev5:d940d03`。
- `sys_casbin_policy.rs`：取 `rev5:6ee82e2`（`rev5:B-115` 穩定序、`rev5:B-123` 端點候選單源）；不帶 `rev5:d940d03`。
- `sys_casbin_archive.rs`：取 `rev5:6ee82e2`；等價 `rev5:4858236`；不帶 `rev5:7575379`／`rev5:d940d03`。
- `sys_role.rs`：等價 `rev5:e02251d`（005 刀已帶 `SUPER_ROLE_CODE` 單源）／`rev5:4858236`／`rev5:fd23de9`／`rev5:55bb3e3`；取 `rev5:6ee82e2`；不帶 `rev5:d940d03`。
- `sys_menu.rs`：取 `rev5:6ee82e2`（`rev5:B-115`）；等價 `rev5:fd23de9`／`rev5:55bb3e3`；不帶 `rev5:d940d03`。
- `router.rs`：取 `rev5:6ee82e2`（`rev5:B-123`）；不帶 `rev5:4889b6d`／`rev5:166f90a`／`rev5:d5d5306`／`rev5:be1d7e1`／`rev5:e85f447`／`rev5:7833ec7`（`rev5:007`／`rev5:008` 路由）／`rev5:d940d03`。
- `auth/enforce.rs`：不帶 `rev5:7aa0ac3`（`Identity` sid）／`rev5:0161d73`／`rev5:166f90a`／`rev5:d940d03`（存量格式化）；等價 `rev5:55bb3e3`。
- `handler/common.rs`：`rev5:6ee82e2` 之 `rev5:B-108` 已由 005 刀帶；不帶 `rev5:7575379`／`rev5:3be868e`／`rev5:7aa0ac3`。
- `tests/authz_entrypoint_lint.rs`／`tests/contract.rs`：`rev5:007`／`rev5:008` 名冊與 case 全數不帶。`tests/wire_schema.rs`：不帶 `rev5:2273816`（`rev5:007` 十四型）、`rev5:75f65ce`／`rev5:dd6db0f`（`Api.Audit`）、`rev5:515177e`（IP 規則裁判、非本刀面）、`rev5:7833ec7`、`rev5:d940d03`（存量格式化）。`tests/menu_domain_serialization.rs`：不帶 `rev5:7575379`／`rev5:d940d03`（存量格式化）。
- base-web 三顆彈窗：取 `rev5:ae1ac0c9`（請求世代）與 `rev5:fb71df69` 之 `rev5:B-129` 半（換角色清狀態；同顆之使用者頁不帶）；抽屜、回收桶頁兩檔、`rev5-role-admin.{ts,d.ts}`：`rev5:006` 後零 commit；兩語 locale 與 `app.d.ts`：`rev5:006` 後九顆（`rev5:007`／`rev5:008` 鍵）——只取 (iii)(iv) 塊與本刀三鍵。

## R3 rev6 拍板差異點（翻案與新增；烤入 implementer 防回歸清單）

**清單 A——rev5 HEAD 帶了、rev6 本刀不帶**：①`Identity` sid 與 no-escalation 本體及其八支掛點（BL-00048、ADR-00064 決定 7）②攜參業務錯誤（`BizData`）與 `rev5:B-113` 探針③使用者域一切（`updateUserSessionPolicy` 端點、指派寫端、使用者頁）④稽核頁、purge 與其名冊⑤`rev5:007`／`rev5:008` 之 ROUTES 與名冊 bump⑥seed-view-gate 之 `rev5:008` 豁免歸零版（`rev5:cd47c29`／`rev5:409b1fa`）⑦回灌撞唯一索引之 23505 收窄分支與其兩支測⑧`find_active_by_code_for_update`。

**清單 B——rev6 翻案或新增**（每條「rev5 形→rev6 形｜依據」；實作與 review 以此為準、藍本相反處不得回帶）：

| # | 面 | rev5 形→rev6 形 | 依據 |
|---|---|---|---|
| D1 | 交易歸屬 | facade 自開交易、自取域鎖、自寫稽核（`set_role_*`／`restore`）→ handler 持交易、內層 `<op>_in_txn` 首句 `enter_menu_domain`、facade 公開寫入口只收 `&DatabaseTransaction` | spec FR-013、005 刀 FR-043、brainstorm §1 翻案① |
| D2 | 操作者取得 | `audit_operator`（帶 degraded 欄、借 `security.ipgate`）→ 各域既有私有 `operator_from`（角色域 `security.role`、回收桶域 `security.policy_archive`；`refused` 欄、零 degraded） | spec FR-006、翻案② |
| D3 | deleteRole 同步 | 免同步 → 實際歸檔 ≥1 列即同步（005 刀既有、本刀不動） | ADR-00043 決定 7、ADR-00044 決定 2 |
| D4 | 測試守衛 | 寫死 setval 值、不補 seed 列 → 帶界水位＋arm 現讀序列（既有）＋本刀擴補回被撤 seed 授權列 | RL-0031、spec FR-044／FR-051 |
| D5 | msg 鍵構造 | 字面 `Cow::Borrowed("biz.role.protectedRevoke")` → `error.rs` 之 `msg_key::` 常數、`MSG_KEYS` 43→46 | spec FR-004、翻案⑤ |
| D6 | 現況讀端取態 | 按鈕維與端點維回全部現役列（`rev5:ADR 0056`「讀端維持現狀」）→ 三維皆「現況 ∩ 候選集」 | Clarifications 第二題、ADR-00066 決定 5 |
| D7 | 23505 | 回灌撞唯一索引收為不可復原 → 不設；資料庫錯一律 `5000` | ADR-00065 決定 10 |
| D8 | 按鈕碼聯集壞形 | 跳過壞形列 → 整請求 `5000`（fail-loud；讀寫兩端與 getAllButtons 同） | ADR-00066 決定 3 |
| D9 | 寫端回應型 | 泛型 `GrantResult<T>` → 三支具體型；選單 id 集合元素以 newtype 掛 2^53 守衛 | 契約共用型節、`tests/wire_i64_guard_lint.rs` 泛型名冊不變 |
| D10 | 命名空間 | `Api.RoleAdmin` 追加＋`Api.PolicyArchive` → 單一 `Api.Authz`（新檔 `rev6-authz.{ts,d.ts}`） | spec FR-038 |
| D11 | 稽核列 | rev5 稽核件欄形 → 既有 `AuditEvent{operator, operation, entity_table: &'static str, entity_id, before, after}`、操作者取 `AuditOperator::uid()`；三維 `after`＝`{dimension, revoked, granted}`、復原 `after`＝歸檔 id／維度／標的／動作四鍵 | 既有 `model/audit.rs`、ADR-00065 決定 6 |
| D12 | 復原鎖角色列 | 以 `v0` 經 `find_active_by_code_for_update` 鎖讀再比 id → 以歸檔 `role_id` 經既有 `find_active_by_id_for_update` 鎖讀再比代碼 | ADR-00065 決定 4 |
| D13 | 端點候選落點 | `handler/role.rs` 之 `policy_endpoints`＋`router.rs` 之 `policy_route_defs` → `router.rs` 之 `policy_endpoints()`／`endpoint_methods()`（具名、非 async、具體回型） | ADR-00064 決定 1、ADR-00066 決定 3 |
| D14 | 回收桶分頁 | 自持分頁換算與 `common::MAX_CURRENT` → 既有 `envelope::page_params`（缺席 1／10、clamp、壞形整串預設、逾界空頁）＋`PageRes` | spec FR-008 |
| D15 | body 收斂 | `json_or_default` 三參、端點標籤 `role.update-menu` 形 → 四參、餵本域 `BODY_FALLBACK_MSG`、標籤＝端點名 | 既有 `handler/common.rs` |
| D16 | 名稱批次讀 | `resolve_operator_names` → `sys_user::find_names_by_ids`＋本域 `db_failure`（回收桶域自持） | BL-00113 重評結論、R5 |
| D17 | 歸檔寫入 | rev5 歸檔件簽章與等集檢查形 → 既有 `insert_archived(txn, policy, reason: &'static str, archived_by)`（`role_id` 件內以 `v0` 反查活性角色）＋私有 `move_to_archive` 之「實刪列數≠掃描列數＝`DbErr::Custom`」，撤銷入口沿用此本體 | 005 刀既有、ADR-00044 決定 3 |
| D18 | 授予／回灌 INSERT | 顯式落治理欄 → `protected` 顯式 FALSE、`created_by`＝操作者 uid、`created_at` 省略由 DB default 補 | ADR-00065 決定 6、spec FR-012 |
| D19 | 授予面收場 | `finish_grant` 於請求 future 內 commit 後 reload → commit 與同步整段交脫離請求之 task、回應前 await（取消安全） | ADR-00067 決定 4 |
| D20 | 新檔標記 | 標記置於 `<script setup>` 開標籤之後、掛 `BASE-WEB-MANAGE-PAGE-WIRING(iii)+`／`(iv)+`，並於新檔內再開 `rev5:007` 圈界塊 → 首行一行：端點權限彈窗＝`[rev6-inline MANAGE-ROLE-AUTH-VIEW+ 006-authz-governance]`、回收桶頁與搜尋模組＝`[rev6-inline MANAGE-POLICY-ARCHIVE-VIEW+ 006-authz-governance]`（名形比照 004 刀 ip-rule 頁之 `MANAGE-IP-RULE-VIEW+ 004-ip-trust-anchor`）；wrapper／型別沿 §III.1 之 `BASE-WEB-WRAPPER+`／`BASE-WEB-ADAPT+`（005 刀 `rev6-role-admin.{ts,d.ts}` 前例）；新檔內不開圈界塊。★rev5 形不可沿用：`(iii)+`／`(iv)+` 於軌道名後先接用途後綴、`+` 在其後，`tools/fork-delta-lint.py` 之 `new_file_track_issue` 要求軌道名後緊接 `+` ⇒ 判紅 | 憲法 §III.2 表外宣告 3、ADR-00063 決定二、`new_file_track_issue` 定形 |
| D21 | 修改型標記 | 首頁寫入函式內以程式行替換佔位註解行未帶 `原行:` → 逐處補帶（menu 彈窗預估 14 處） | ADR-00063 決定二預估依據 |
| D22 | 抽屜狀態欄 | 編輯恆送開啟時回填值 → 異於回填值才帶 | ADR-00070、BL-00131 |
| D23 | seed-view-gate | 原始版：worktree 未就位具名跳過、`check` 連帶跑自測、以具名豁免不入自測迴圈 → tracked 面缺席 rc 2、入 pre-commit `for` 自測迴圈、`check` 不跑自測 | ADR-00071 決定 4／6 |
| D24 | 封死與復原第③腿探針 | 封死成員植在標的自身名下（改正該腿後落 NoOp）→ 植於第三方合成代碼名下 | ADR-00064 決定 8 |
| D25 | 已知降級窗 | 只記重試耗盡窗 → 記兩窗（過渡窗＋耗盡窗；含授予面反向症狀） | ADR-00067 決定 6、BL-00134 |
| D26 | 測試直種現役政策 | 不落建立者 → 一律帶非 NULL 建立者（`plant_live_policy`、`sys_menu` 測試之 `plant_role_residue`、`tests/contract.rs` 兩處 raw INSERT） | spec FR-045、BL-00136 形① |
| D27 | 使用者路由案之 seed 錨 | （rev6 自有）`sys_menu.created_by IS NULL` → `casbin_rule.created_by IS NULL` 之 seed 政策列 | spec FR-045 |
| D28 | 回收桶 query 型名 | 後端 `ArchivedPolicyQuery`、typings `ArchivedPolicyListQuery` → 兩側 `ArchivedPolicyListQuery` | `contracts/wire-policy-archive.md` |
| D29 | 約束違反判定件 | `pub(crate) fn violated_constraint(e: &DbErr) -> Option<&str>`（回約束名、呼叫端自比）→ 既有私有 `violated_constraint(err: &DbErr, unique_index: &str) -> bool`（收指名索引、只認該索引之唯一違反）；本刀零新呼叫點（不設 23505 收窄＝D7） | 既有 `model/facade/mod.rs` |
| D30 | 回收桶列表件頁碼 | handler 以 `current - 1` 交 facade `list`（0 起算頁索引）→ facade `list` 收 1 起算、已由 `envelope::page_params` 收斂之頁碼（同既有 `sys_role::page_query` 之取態） | D14 延伸、data-model §13 |
| D31 | 首頁下拉寫入時點 | rev5 HEAD 形＝rev6 形（防回歸對象＝spec 原措辭「提交時首頁有變更才寫」）：選值即打 updateRoleHome、與確定鈕獨立、取消不還原、每次選值各一筆稽核、清空即送 null；確定鈕只送 updateRoleMenu（全量） | Clarifications 第三題、spec FR-033 |
| D32 | 換角色清狀態之射程 | rev5 HEAD 形（`rev5:B-129`）＝rev6 形（防回歸對象＝spec 原措辭「勾選與候選」）：只清前一角色之角色維狀態（勾選、鎖定集、首頁值）；候選與角色無關、每次開啟重取、成功才覆蓋、失敗保留上次值 | Clarifications 第四題、spec FR-034④ |
| D33 | 已知態觀察之 seed 寫入 | （rev6 自有規則之具名例外）走查寫入一律對自建角色 → 僅 ADR-00068 各款之已知態觀察步驟得對 seed 角色（R_ADMIN／R_USER_COMMON）寫入並以 seed 帳號登入觀察，前後套走查基準（觀察前 snapshot→觀察後 restore＋重啟 rust-api→diff rc 0）；工具擴面＝R12.5、承載＝R18 U16；整合測試不在例外內（R12.6） | Clarifications 第五題、spec Edge Cases「測試與走查基建」 |

**rev5 對 rev4 之防回歸要點**（本刀照帶、烤入 prompt）：拒因純 key 不攜參／角色鍵一律 `id`／restorePolicy 不入選單域／三鈕不做按鈕碼 gating（門在頁級）／操作稽核封閉五詞小寫／請求上下文缺席＝拒寫 `5000`／回收桶頁不手加 static meta／端點彈窗群組勾選＝顯式 `cascade`＋`check-strategy="child"`（只寫後者＝結構性 inert）／button 彈窗初始化改 `watch(visible)`／表格橫向捲動寬＝各欄寬之和。

## R4 rev5 收刀後本域 commit 三分（藍本取 HEAD 形之依據）

| commit | 判定 | 本刀取用面 |
|---|---|---|
| `rev5:ddbab53`（底座） | 部分帶 | 不可復原集五值（rev6＝3→5）、以代碼批次讀件、聯集讀端（改 fail-loud）、斷環具名 fn（改住 router.rs）；`Option<i64>` 守衛 rev6 已有等價（`serialize_opt_i64_number_guarded`） |
| `rev5:51f1e19`（選單／按鈕維寫端） | 部分帶 | 全量替換語意與入域機器證；自管交易之殼不帶 |
| `rev5:0814bf9`（端點維寫端） | 部分帶 | 不入域、orphan skip、plan／apply 兩段；settle 段不帶（收場屬 handler） |
| `rev5:6dcd41d`（六支 handler＋路由＋reload 接線） | 部分帶 | handler 形、名冊擴列、授權態矩陣；`finish_grant` 請求內 reload 不帶（D19）；路由計數依 rev6 |
| `rev5:932ba8c`（封死＋交錯時序 seam） | 部分帶 | `protected_endpoint_set` 與授予側拒因；reload seam rev6 已有等價（005 刀已帶） |
| `rev5:65a5cf3`（射程＝候選集） | 部分帶 | 濾點件與候選外不動；「讀端維持現狀」半不帶（D6） |
| `rev5:d22a01c`（回收桶） | 部分帶 | 雙篩、降冪分頁、旗標批次求值、五腿固定序、三態；23505 收斂、facade 自開交易不帶 |
| `rev5:3dcb27e`／`rev5:6859d89`（快照重抽） | 不帶 | 快照為產物，rev6 以 `tools/wire-schema.py` 自抽 |
| `rev5:8f31bbc`（候選讀三支） | 部分帶 | getAllButtons／getAllEndpoints；getAllPages 已由 005 刀交付 |
| `rev5:dc1cc8c`（wire 裁判） | 部分帶 | 正向＋反例裁判形；命名空間改 `Api.Authz` |
| `rev5:f455858`（final holistic doc） | 不帶 | rev5 碼註訂正 |
| `rev5:6ee82e2`（`rev5:006` 後修正） | 部分帶 | `rev5:B-115`／`rev5:B-123` 帶；`rev5:B-106`／`rev5:B-108` rev6 已有等價 |
| base-web `rev5:979039fb`／`rev5:5d15c70d`／`rev5:def8bf8a`（三拒因鍵） | 帶 | 鍵名與子樹；落點改三檔 locale（含 `zh-tw.ts`）＋`app.d.ts`，鍵隨首發單元 |
| base-web `rev5:80e9f0d2`（回收桶頁） | 部分帶 | 頁面、搜尋卡、8 欄、停用態、復原動線、`route:`／`page:` 鍵；`Api.PolicyArchive` 改 `Api.Authz` |
| base-web `rev5:1597a671`（三顆彈窗接真） | 部分帶 | 三彈窗與端點新檔；roleHome wrapper 與 `rev5:B-099` 已由 005 刀承載 |
| base-web `rev5:673f206e`（就緒守） | 帶 | 確定鈕於現況讀成功前停用 |
| base-web `rev5:ae1ac0c9` | 部分帶 | `rev5:B-116` 帶；`rev5:B-100` 已由 005 刀帶；`rev5:B-117` 非本刀面 |
| base-web `rev5:fb71df69` | 部分帶 | `rev5:B-129` 三彈窗清狀態帶；同顆 `rev5:007` 使用者頁不帶 |
| 外層 `rev5:9d709d4`（seed-view-gate 原始版） | 部分帶 | 判準、豁免兩列、結構自證；跳過語意與自測接法依 D23 |

## R5 模組邊界與共用件落點

- **Decision**:
  - **handler**：三維六支＋候選讀兩支住既有 `handler/role.rs`（域字面沿 `security.role`、`BODY_FALLBACK_MSG`、私有 `operator_from`／`db_failure` 共用；該檔另增授予面收場件與授權寫端稽核件，皆**新建**）；回收桶兩支住**新建** `handler/policy_archive.rs`（新域：自有 target `security.policy_archive`、本域 `BODY_FALLBACK_MSG`／`operator_from`／`db_failure`、復原收場件、復原稽核件）。`handler/mod.rs` 宣告 `pub mod policy_archive`、ASCII 序插為 `menu` < `policy_archive` < `role`，域數句「八域」改「九域」。`handler/common.rs` 零新件，只於 `each_domain_keeps_its_own_log_literals` 名冊加回收桶域一列；`handler/ip_rule.rs` 之 `production_code_emits_no_degraded_field` 檔清單加回收桶檔。
  - **`archivedBy` 換算**：回收桶域自持——直呼既有 `sys_user::find_names_by_ids`（整頁 `archived_by` 去重、空集不查）並以本域 `db_failure` 包錯；不提升進 `common.rs`。判準＝BL-00113 重評結論「log 留呼叫點」：提升即把兩域之錯誤 target 併成一處、`each_domain_keeps_its_own_log_literals` 所守之逐域字面被合併。前例兩形並存（`handler/role.rs` 之 `get_role_list` 直呼、`handler/menu.rs` 私有 `operator_names` 包裝），本域取直呼或私有包裝由實作擇一、皆屬自持。
  - **測試 helper**：判定面同步計數讀取件 `reload_counts` 於回收桶測試模組自持第三份（`handler/role.rs`、`handler/menu.rs` 各一）；判準＝BL-00113 結論③「測試側庫態快照續不合併」，提升即動兩支既有測試模組。
  - **facade**：**新建** `model/facade/sys_casbin_policy.rs`＝`casbin_rule` 之主 facade（三維現況讀、濾點件、全量替換規劃、授予 INSERT、封死集查詢；錯誤形屬「後一制」）；既有 `sys_casbin_archive.rs` 擴撤銷原因、撤銷入口、列表件、復原件，續為「一張表配一支」之唯一跨表例外（復原同寫授權表與歸檔表）；候選集輔助（治理域選單映射、按鈕碼聯集讀端 `governed_button_codes`）住 `sys_casbin_policy.rs`、`sys_menu.rs` 零新件（只改模組 doc「不帶」句＝R17）；`sys_role.rs` 加兩支讀件（`active_code_of`／`active_ids_by_codes`）；`facade/mod.rs` 檔頭「十一支對十二張表」改「十二支對十二張表」、沿革括號記本刀增支、成員序句補 `sys_casbin_policy`（ASCII 序緊接 `sys_casbin_archive` 之後）、錯誤形段補一句。新建公開寫入口比照 `sys_casbin_archive.rs` 模組 doc 之「正面孿生＋`compile_fail` 反段」形各補一段具型交易機器守。
  - **路由表**：`router.rs` 新建 `policy_endpoints()`／`endpoint_methods()`，消費者＝三維端點維讀寫、getAllEndpoints、復原第④腿與旗標④半，由 handler 以參數傳入 facade。
  - **不動**：`auth/enforce.rs` 同步機制（只改 doc）、`obs.rs`（`casbin_reload_total` 三值預註冊照舊）、`AppState` 七欄、`AuditOperation` 五詞。
- **Rationale**: 三維寫端與既有角色寫端共用角色列鎖、角色域拒因與 log 字面，同檔使 `DOMAIN_LOCK_CALL_FILES`／`RELOAD_CALL_FILES` 之角色檔列免擴；回收桶域之 log 字面、拒因鍵子樹（`biz.policy.*`）與頁面皆獨立，自成一域使允許清單有圈界力（rev5 同切）。復原留在 `sys_casbin_archive.rs`＝等集保證與跨表寫入同處（ADR-00065 決定 3）。
- **Alternatives considered**: 三維寫端另立 `handler/authz.rs`（多一域、域鎖與同步兩名冊各擴一列、角色鎖讀與拒因跨檔重持，棄）；回收桶併入 `role.rs`（兩域 log 字面混居、`role.rs` 允許清單失圈界，棄）；復原落 `sys_casbin_policy.rs`（跨表寫入離開唯一例外模組＝例外變二，棄）；`archivedBy` 與 `reload_counts` 提升共用（見上判準，棄）。

## R6 交易、鎖序、入域與收場件

- **Decision**:
  1. **外殼＋內層**（005 刀形）：外殼 begin → 內層 `<op>_in_txn(&txn, …)` → 收場件。updateRoleMenu／updateRoleButton 之內層首句＝`sys_casbin_archive::enter_menu_domain(txn)`（島 H1 終態成員）；updateRoleEndpoints 與 restorePolicy 不入域。
  2. **鎖序**（全域固定序 advisory → 歸檔表列 → `sys_role` 列 → `sys_menu` 列 → `casbin_rule`）：三維寫端＝〔入域兩支先 advisory〕→ 既有 `sys_role::find_active_by_id_for_update` 鎖標的角色列（活性、停用照鎖）→ 鎖內讀現況與候選（選單維與按鈕維以 `sys_menu::list_governed` 一次讀、不取 `sys_menu` 列鎖——改動治理域之寫端全數在域內）→ 導出撤銷集與新授集 → 受保護撤銷拒 →〔端點維〕封死 → 撤銷（`casbin_rule` 列鎖由 DELETE 取得）→ 授予 INSERT → 稽核。restorePolicy＝鎖歸檔列（`FOR UPDATE`）→ ①原因 → 以 `role_id` 鎖角色列 → ②～⑤ → NoOp／Applied。
  3. **無環論證**：端點維授權列只被三類寫端觸及——deleteRole 家族（入域、鎖角色列）、updateRoleEndpoints（鎖角色列）、restorePolicy（鎖歸檔列再鎖角色列）——三者對同一角色皆經角色列序列化；deleteMenu 家族與 updateMenu 只觸選單維與按鈕維列、與端點維列不相交；歸檔表之既有列只有 restorePolicy 會鎖，其餘寫端只插新列 ⇒ 等待圖無環。私有 `move_to_archive` 之「實刪≠掃描即 `DbErr::Custom`」對撤銷入口仍可滿足（同角色之撤銷與刪除經角色列序列化）。
  4. **收場件處置**：既有 `handler/role.rs`／`handler/menu.rs` 之 `settle_domain_write`（移除面、`archived > 0` 門）與 `handler/menu.rs` 之 `settle_domain_txn<T>` 一字不動。授予面另**新建**收場件（住 `handler/role.rs`）：取消安全殼同形（`tokio::spawn` 收 commit＋同步、本件 await 其 JoinHandle、task 被取消＝告警後 `5000`）、資料體泛型（回寫端回應三型之一）、門＝outcome（Applied 即同步、含空 diff；Rejected 顯式 rollback、零同步）。restorePolicy 之收場件自持於 `handler/policy_archive.rs`：Applied＝commit 後同步、NoOp＝只 commit、拒＝顯式 rollback。授予面與復原之取消告警字面交 tasks 定（R20）。
  5. **源碼釘**：`handler/role.rs` 之 `domain_write_ends_enter_the_domain_first_and_roll_back_explicitly`（現釘 reload 匯入句與呼叫句「恰一處」）於授予面收場件落地之單元改寫（呼叫點變兩處，或收斂為兩收場件共用之單一呼叫形——以實作為準、釘值同步）；入域兩支納入「外殼 begin 後第一呼叫即內層、內層首句入域、失敗腿顯式 rollback」釘。
  6. **機器證**：入域兩支各一 NOT-granted 等待案（`delete_role_waits_behind_the_menu_domain_holder` 形：持有者交易持域鎖、後到者 `SET LOCAL lock_timeout` 大於輪詢窗、以 `menu_domain_waiter_count` 輪詢至 1 再放鎖）；不入域兩支各一直接完成案（`add_role_passes_the_menu_domain_holder` 形）。
- **Rationale**: spec FR-013／FR-031、ADR-00065 決定 3、ADR-00067 決定 4；移除面門與授予面門方向相反為刻意並陳（ADR-00067 決定 2），共用一支收場件即須以旗標分門、反使兩門可被一處改動同時改壞。
- **Alternatives considered**: 授予面直套既有 `settle_domain_write`（新授而零撤銷時歸檔數 0＝永不同步，ADR-00067 替代案 5，棄）；收場件提升進 `common.rs`（兩域 log target 合併、違 BL-00113 結論，棄）；restorePolicy 入域（可復原列只剩端點維、入域只增競爭，ADR-00065 替代案 7，棄）。

## R7 全量替換（ADR-00066）

- **Decision**: 三維同式：撤銷集＝（現況 ∩ 候選集）−期望、新授集＝（期望 ∩ 候選集）−現況，比對鍵＝政策鍵（v1, v2）；期望集先 orphan skip 並去重（保首見序）；新授集排序後逐列寫入；候選外現役列不撤、不授、不入生效集合與現況讀端（ADR-00066 決定 2／4）。濾點件為 `sys_casbin_policy.rs` 內**新建**純函式（rev5 同位件 `scope_live_to_candidates`），寫端與三支現況讀端共用（決定 5）。候選取得：選單維＝`sys_menu::list_governed` 一次讀所得之路由名集與 id↔路由名映射表（同一真源同一時點；環成員及其子孫為已知邊界）；按鈕維＝聯集讀端（**新建**；同層序首見去重、壞形整請求 `5000`）；端點維＝`router::policy_endpoints()`（**新建**；編譯期常數，本刀後 35）。生效集合＝orphan skip 後之期望集，集合上恆等於寫後之現況讀端回應（決定 6）。期望空集＝合法全撤；body 壞形 ⇒ `id=0` ⇒ `biz.role.notFound`（決定 7）。現況讀端之角色代碼讀取以**新建**之「以 id 讀活性角色代碼」件承載、不取鎖。
- **Rationale**: 背景量測（m0002 逐列解析）：本刀後端點候選外 seed 列 16（R_SUPER 15、其中受保護 1＝列 68；R_ADMIN 1＝列 2）——`live∖desired` 形下唯一有權者之端點彈窗恆被受保護撤銷拒擋下；R_SUPER 端點維讀端回 35 項（受保護 14）、R_ADMIN 回 2 項。
- **Alternatives considered**: 見 ADR-00066 替代案 1～6；讀端照回全部現役列已由 Clarifications 第二題否決。

## R8 結構性封死（ADR-00064）

- **Decision**: 封死集＝現役授權列中 `ptype='p' ∧ protected=TRUE ∧ v2 ∈ HTTP 方法白名單` 之（v1, v2），不問 `v0`、不寫列數；查詢件單點＝**新建** `sys_casbin_policy::protected_endpoint_set`（白名單以參數收，生產端傳 `router::endpoint_methods()`）。掛點恰兩處：updateRoleEndpoints 鎖內（先判撤銷、再判授予；`biz.role.protectedGrant` 整批拒、不靜默壓縮）、restorePolicy 第③腿（`biz.policy.notRestorable`）；可復原旗標③半為讀端消費、不計掛點。R_SUPER 豁免以 `sys_role::SUPER_ROLE_CODE` 判；新授集為空或標的為 R_SUPER 時零額外查詢。機器證：非 R_SUPER 授予封死端點整批拒且零變更零歸檔零稽核零同步；撤銷先判之固定序一案；選單維受保護列可授可見性一案；謂詞釘（不問 `v0`、`menu` 維不入、`protected=FALSE` 不入、白名單外方法不入、非 `p` 不入、白名單承重）；**R_SUPER 豁免探針**＝交易內於非 R_SUPER 之第三方合成代碼名下直種一列 `protected=TRUE` 之合成（路徑,方法），先自證「探針 ∈ 封死集且 R_SUPER 與對照臂標的現役皆不持有」，R_SUPER 自授 ⇒ Applied 新授 1、對照臂（另建之非 R_SUPER 合成角色）⇒ 整批拒；復原第③腿兩半共用同一探針；變異自證（拆判定或改謂詞 ⇒ 紅）。
- **Rationale**: seed 端點維受保護 15 列（GET 8／POST 7）皆屬 R_SUPER 且每鍵恰一列 ⇒ wire 面打不出「R_SUPER 自授封死端點而新授 ≥1」，真豁免須 facade 層探針；探針植在標的自身名下（rev5 形）會令復原負向案改正後落 NoOp 而 vacuous（ADR-00064 決定 8）。
- **Alternatives considered**: 見 ADR-00064 替代案 1～8（路由表旗標、寫死名冊、UI 警示、事後告警、真 no-escalation、擴射程至選單維四列、全封政策端點、只掛單點）。

## R9 歸檔與復原（ADR-00065）

- **Decision**:
  1. `sys_casbin_archive.rs` **新建**三撤銷原因常數 `REASON_MENU_REVOKE`／`REASON_BUTTON_REVOKE`／`REASON_ENDPOINT_REVOKE`；既有 `is_non_restorable_reason` 三值擴五值（唯 `endpoint_revoke` 可復原）；既有釘案 `archive_reasons_pin_three_literals_and_non_restorable_set_is_exactly_them` 正向臂五值、負向臂只餘 `endpoint_revoke` 與非法字面，其測名（`three_literals` 字樣成假述＝改名，新名由實作定、不得再含 `three`）、doc 與斷言訊息之「恰三值」同批改（data-model §7-1 同判；`menu_revoke`／`button_revoke` 移臂為拍板變更、非回歸）。
  2. **撤銷入口**（**新建**、公開入口只收 `&DatabaseTransaction`）：以候選內撤銷集之列 id 圈定、經既有私有 `move_to_archive` 本體移入歸檔（等集檢查與 `insert_archived` 之來源角色 id 反查照舊）；模組 doc 之具型交易正面孿生補該入口、另加一段 `compile_fail` 反段。
  3. **列表件**（**新建**）：雙篩（`v0` 文字等值、空字串忽略；維度由 `v2` 推導、未知值不濾）、`archived_at DESC, id DESC`、`envelope::page_params` 分頁；可復原旗標批次求值（①共用 `is_non_restorable_reason`、②以**新建**代碼批次讀件一次取、③以 `protected_endpoint_set` 一次取、④以 handler 傳入之端點全集；①不過即短路）；`archivedBy` 由 handler 換算（R5）。
  4. **復原件**（**新建**）：固定序五腿（鎖歸檔列 →①原因 → 以 `role_id` 鎖角色列 →②同實例〔NULL 拒、查無拒、代碼≠`v0` 拒〕→③封死 →④端點在路由表 →⑤停用不擋）→ 七欄身分鍵已在現役＝NoOp（刪歸檔列、零稽核、零同步）、否則 Applied（INSERT 新 id、`protected` FALSE、建立者＝復原者、刪歸檔列、`restore` 稽核同交易）；任一腿拒＝早退、歸檔列保留、`biz.policy.notRestorable`。不設 23505 收窄；不入選單域。
  5. 模組 doc ④「歸檔原因只有三值（…）授權回收桶讀端與復原不帶」與 `is_non_restorable_reason` doc「恰上列三值」於落地單元改現在式（R17）。
- **Rationale**: ADR-00065 決定 1～11；ADR-00044 決定 4 之復核結論＝兩維歸檔列仍結構性無復原路徑（決定 2）。
- **Alternatives considered**: 見 ADR-00065 替代案 1～10。

## R10 觸發矩陣與兩窗（ADR-00067）

- **Decision**: 觸發者＝移除面五支（實際歸檔 ≥1 列，不變）＋授予面三支（Applied 即觸發、不問 diff、含空 diff＝刻意例外）＋restorePolicy（Applied）；不觸發集＝操作者缺席、未 commit 之失敗、Rejected、查無角色、NoOp、NotRestorable、本刀讀端六支。`RELOAD_CALL_FILES` 加 `handler/policy_archive.rs`（與復原同步接線同一 commit）、三維寫端住已在冊之 `handler/role.rs`；`ENFORCER_WRITE_FILES` 維持空冊。兩窗＝commit→換上之有界過渡窗（有界前提＝重建有界＋收場取消安全）＋重試耗盡窗；記窗、零碼改。碼面現在式連動（★各觸發列之落地單元同批改至該 commit 之實況＝RL-0015、ADR-00067 決定 9：選單維與按鈕維授予＝U7、端點維授予＝U8、復原類＝U9〔與 `RELOAD_CALL_FILES` 擴列同顆〕；中途 commit 不留「只由移除面觸發」之舊述）：`reload_enforcer` doc 觸發矩陣改三類並明文授予面刻意例外、其「前代授權寫端與授權回收桶兩類觸發屬授權治理刀、不帶」句改現在式；`auth/enforce.rs` 檔頭、`init_enforcer` doc、`main.rs` 連線段註解、`state.rs` 判定面欄 doc 之「移除面寫端 commit 後…」句改三類；交錯時序測試 doc「判定面同步只由移除面寫端觸發」改寫；`deploy/grafana-provisioning/alerting/rules.yml` 告警錨註解之島指針依 U0 親決題 H-a 結果改指（uid／title／判準不動）；RUNBOOK §11.2 `ok` 判讀句（隨各觸發列落地單元、同上）與 §13「剛授予或剛復原之端點仍回 `5003`」分診（三類觸發齊後補＝U10；ADR-00067 決定 9）。機器證：觸發矩陣特性鎖定測（區域 recorder 斷言 `casbin_reload_total` 增量）、授予與復原收場之取消安全案、授予後即時生效／撤銷後即時失效之單一判定進入點雙斷言、失敗注入下舊面續放行 R_SUPER。
- **Rationale**: ADR-00067 決定 1～10；授予面不以 diff 為門＝省去 diff 漏算一整類缺陷、重建冪等（決定 2）。
- **Alternatives considered**: 見 ADR-00067 替代案 1～5。

## R11 wire

- **Decision**: 型別開單一命名空間 `Api.Authz`（**新建** `base-web/src/typings/api/rev6-authz.d.ts`，declaration merging、§III.1 預設軌道）；十支 fetcher 住**新建** `base-web/src/service/api/rev6-authz.ts`（不入 barrel、錯誤不加工、query 與 body 以具名型組）。型名＝後端 DTO 名（型名之家＝兩支契約之共用型節）：三維 11 型（`Endpoint`／`RoleMenuItem`／`RoleButtonItem`／`RoleEndpointItem`／三支 `*GrantRes`／三支請求型／`RoleIdQuery`）＋回收桶 4 型（`ArchivedPolicyDimension`／`ArchivedPolicy`〔14 欄〕／`ArchivedPolicyListQuery`／`RestorePolicyReq`）。兩側零新泛型（`tests/wire_i64_guard_lint.rs` 之 `GENERIC_WIRE_TYPES` 維持 `Res`／`PageRes`）；選單 id 集合元素以 newtype 掛既有 `serialize_i64_number_guarded`（`Vec<i64>` 直出會觸絆線 `nested_generic_i64_fields_are_out_of_scope`）；`roleId` 掛 `serialize_opt_i64_number_guarded`；時間 RFC3339 `+00:00`（ADR-00061）；`method` 大寫字面。快照以 `tools/wire-schema.py` 重抽；`tests/wire_schema.rs` 之 `AUDITED_READ_DEFS`／`AUDITED_REQUEST_DEFS` 擴列、節謂詞 `in_role_menu_sections` 擴認 `Api.Authz.` 前綴、`audited_roster_is_complete_and_present_in_snapshot` 續守、表驅動鍵集斷言涵蓋新讀型；每型正向＋反例（`protected` 缺席或型錯、角色鍵寫成 `roleId`、`effective` 跨型、`archivedBy` 為 number、`roleId` 鍵缺席、`dimension` 值域外、snake_case 鍵）。
- **Rationale**: spec FR-005／FR-038／FR-052；單一命名空間使十支 fetcher 與受審名冊同一前綴、節謂詞只擴一處。
- **Alternatives considered**: 沿 rev5 分兩命名空間（同一刀之型散兩檔、節謂詞擴兩前綴，棄）；保留泛型 `GrantResult<T>`（泛型名冊與抽取器佔位 definition 連動、實例化絆線須擴，棄）；選單 id 以 `Vec<i64>` 直出並把絆線改豁免（同批 id 於讀端有守衛、於寫端回應失真＝fail-loud 單向失效，棄）。

## R12 測試基建

- **Decision**:
  1. **被撤 seed 授權列回補**（spec FR-044／FR-051）：src 側 `CasbinRuleRowsGuard` 與 tests 側 `CasbinRuleWriteGuard`（及兩組合守衛之授權腿）於 arm 時除既有帶界水位與序列外，另快照「id ≤ 水位」之授權列全欄值；Drop 序＝刪 `id >` 水位（含授予新列與復原回插之新 id 列）→ 依快照補回缺列（原 id 原值；回補語句形＝`contracts/code-gates.md` §5.1：無衝突目標之 `ON CONFLICT DO NOTHING`，同 tests 側 `SeedMenuDeleteNet` 既有形）→ setval 回 arm 值。★先刪後補：七欄身分鍵唯一索引 `unique_key_sea_orm_adapter` 下，復原回插之新 id 列與被撤 seed 列同鍵；反序＝回補撞該索引被 `DO NOTHING` 靜默吞掉、新 id 列隨後被刪 ⇒ seed 列永久缺席（不報錯）。歸檔表守衛（`PolicyArchiveRowsGuard`／`PolicyArchiveWriteGuard`）同形擴回補——理由：restorePolicy 之 Applied／NoOp 皆刪歸檔列，arm 前已在之界下歸檔列（走查或中斷跑次之殘列）一經案消費即不復返；兩表守衛同語意、免「哪支守衛救得回刪除」之分歧（凍結 seed 該表零列、seed 比對不受影響）。組合守衛 `RoleMenuDomainRowsGuard`／`RoleMenuDomainWriteGuard` 之固定 Drop 序不變。回補語句模板兩族自持時，同批新增一支 `include_str!` 逐字對賬案（`self_held_synthetic_uid_floor_matches_src_verbatim` 同形）。施工全文（兩表兩族之快照、Drop 序、回補語句、自證形與反向變異）＝`contracts/code-gates.md` §5.1（自證取嵌套守衛形、自建列代 seed 列、不碰 seed——直撤真 seed 列做反序變異會令 seed 列永久留缺於 dev 庫＝違 spec FR-051）。`test_kit.rs` 檔頭「救不回 seed 列之寫痕」句之射程同批改寫（授權表自本刀起救得回被撤列；UPDATE 寫痕仍屬 `RowFixupGuard` 形）。
  2. **建立者**（BL-00136 形①、spec FR-045）：`plant_live_policy` 經既有 `add_policy` 落庫後、同件補寫該列之 `created_by`（非 NULL 合成 uid；`casbin_rule.created_by` 無外鍵）——判定面持有與 DB 列可與 seed 分辨兩者同時成立；`sys_menu.rs` 測試之 `plant_role_residue` 同形；`tests/contract.rs` 兩處 raw INSERT（`super_cannot_disable_msg` 之 R_ADMIN 植列、`seed_menu_delete_net_rewrites_the_deletion_pair_and_reinserts_removed_grants` 之合成角色植列）補非 NULL `created_by`。判準＝一致不變式「測試直種現役政策一律帶建立者」：跨 run 異常終止之殘列可能與改錨案共存，任一處留 NULL 即被改錨案誤算為 seed。
  3. **改錨**：`sys_menu.rs` 與 `handler/route.rs` 測試之 `seed_names_by_sql`（現以 `sys_menu.created_by IS NULL` 錨 seed）改錨 `casbin_rule.created_by IS NULL` 之 seed 政策列；兩案內寫死 seed 名之前提斷言（例：「manage 零 R_ADMIN menu 政策」）同批改以 seed 政策列現算；`user_routes_tree_differs_by_role_and_home_is_navigable_leaf`／`seed_role_trees_differ_by_role_and_nest` 兩案於 dev 庫存在經寫端授予之殘列時照綠（殘列演練納此形；承重植列＝授 seed 角色於 seed 選單列之 nextval 形殘授權，形與步驟＝`contracts/code-gates.md` §5.2）。
  4. **號段表**：`ID_RANGES` 依「表×檔」為本刀新測試檔增列（同表不同檔不重疊；tests 側同值字面自持並經 `self_held_id_ranges_match_src_registry_verbatim` 逐字對賬）；稽核斷言一律取水位窗。
  5. **走查還原工具 v3**（spec FR-044、Clarifications 第五題、ADR-00068 決定 4②）：基準檔升 v3、另存授權表快照與角色列可變欄（射程含 seed 角色列）、`restore` 補回被撤之 seed 授權列並回寫角色列可變欄（含審計欄）；同一「先刪後補」序之理由同決定 1。施工全文（新存欄與其射程、寫面次序、`restore --seed` 料源、重啟提示判準、自測與同批面、時序）＝`contracts/code-gates.md` §6。
  6. **seed 角色列欄值**（spec FR-051：測試不留 seed 列變更）：會改動 seed 角色列欄值之整合測試（例：以 updateRoleHome 改 R_SUPER 首頁）一律於測試交易內 rollback，或由守衛回補該列被寫欄與 `updated_at`／`updated_by`（既有 `RowFixupGuard` 形；改回值≠改回痕）；形之家＝data-model §11。Clarifications 第五題之 seed 角色寫入例外只及 CDP 已知態觀察步驟、不及整合測試（D33）。
- **Rationale**: 本刀首度以寫端撤銷 seed 授權列（id 在上界以內），現行守衛與工具只刪上界以上列；先刪後補是唯一不令回補被唯一索引靜默吞掉之序。
- **Alternatives considered**: 測試只撤自建列、永不撤 seed 列（spec US2 Independent Test、FR-032 自救案、SC-003 候選外案皆以 seed 列為標的，棄）；補回改以 seed.sql 重灌整表（連帶抹掉 arm 前之合法殘列與其序列語意，棄）；`plant_live_policy` 改直寫＋重建判定面（偏離「經真判定面路徑造列」之 005 刀判準，棄）。

## R13 機器守

- **Decision**:
  1. **`tests/authz_entrypoint_lint.rs`**：`RELOAD_CALL_FILES` [menu, role] 加 policy_archive；`ENFORCER_WRITE_FILES` 維持空冊；`DOMAIN_LOCK_CALL_FILES` [menu, role] 不變（入域兩支住 `role.rs`）；`DOMAIN_WRITE_SIDE_FILES` 7→8（加 `model/facade/sys_casbin_policy.rs`＝域內交易所呼 facade）；植入自證案 `planting_reload_use_turns_leg_one_red_outside_exempt_faces`／`planting_lock_uses_turns_leg_five_red` 之期望紅集與逐檔迴圈依新名冊實況改（字面以植入實跑為準）；`CASBIN_VERIFIED` 不變。
  2. **逐域名冊**：`handler/common.rs` 之 `each_domain_keeps_its_own_log_literals` 加回收桶域；`handler/ip_rule.rs` 之 `production_code_emits_no_degraded_field` 檔清單加回收桶檔——兩名冊以 `("<name>.rs"` 形指名新檔，使其入 `tests/test_module_tail_lint.rs` 判準①射程（新檔之測試模組 MUST 居檔尾）。`tests/entity_access_lint.rs` 之 handler 層零 path-root entity token 射程自動涵蓋新檔。
  3. **契約與名冊閘**：`tests/contract.rs` registry 與兩道 coverage gate 49＝49、case_key 綁定、授權態矩陣對照凍結 seed 政策列、`msg_roster_every_key_has_an_emitter` 涵蓋新三鍵；`error.rs` `MSG_KEYS` 43→46；外層 `tools/msg-key-gate.py` 雙向閘（三檔 locale 後端子樹）；前端消費者名冊 `FRONTEND_MSG_CONSUMERS` 不動（仍恰 1 項；判準＝`contracts/msg-keys.md` §4、收刀反向確認＝`contracts/code-gates.md` §8.2）。
  4. **fork-delta-lint 範圍欄對賬腿**（BL-00132；spec FR-042、ADR-00063 決定四）：解析 §III.2 範圍欄、修改型 `原行:` 數逐軌道×用途×檔比、新增型圈界塊數逐檔加總比；「不預估」或「預估」項跳過（新增型以檔為單位跳過、修改型只跳該三元組）；零解析即紅；植入反例（改一個範圍欄數字）變異自證；活書 08 §8.4 之機器守射程句同單元改寫；`find_unmarked_additions` 碼註補 Vue 模板屬性行變體指針。
  5. **seed-view-gate**（ADR-00071）：新碼面閘、接線四處（pre-commit 條件段、自測迴圈、bootstrap 推導、RUNBOOK §12 碼面閘表一列）、連動名冊（`tools/docsync/tests/test_hook_wiring.py` 之 `SEGMENTS`／`MIRROR_WORDS` 與三處人寫鏡像、README 工具樹、RUNBOOK §12 工具鏈速查表、活書 05 `tools/` 列）；不佔 GT 名額；跨刀活體契約入 `docs/ops/reference-src/code-gate-contracts.md` 新節。
  6. **既有閘之連動**：`route-artifact-gate` 讀面（(i) 列產物檔注記）不變、新頁產物四檔重算冪等；`view-render-guard` 掃描根 `views/manage` 自動涵蓋回收桶頁；外層 `tools/docsync/tests/test_references.py` 之 `TestRoutes::test_real_repo_pinned_rows` +10 列；`router.rs` 之 `routes_block_literal_form_and_pinned_rows` 同批；`gates.py` `NON_GATE_TOOLS` 不變。
- **Rationale**: spec FR-018／FR-042／FR-043／FR-048；本刀擴列之名冊判決形分兩類，tasks 依類施工：①集合恰等（實得檔集須等於名冊、漏列即紅）＝`RELOAD_CALL_FILES`／`DOMAIN_LOCK_CALL_FILES`——擴列與接線同 commit 才不留紅窗 ②漏列靜默（不轉紅、靜默缺口）＝`DOMAIN_WRITE_SIDE_FILES`（`leg_per_user_lock_in_domain` 之過濾集）、`each_domain_keeps_its_own_log_literals` 與 `production_code_emits_no_degraded_field`（皆 `include_str!` 寫死之元組表）——須由 tasks 逐項明列擴列（與 `contracts/code-gates.md` §3 同口徑）。
- **Alternatives considered**: 回收桶檔不入兩逐域名冊（新域 log 字面無守、degraded 欄可回帶，棄）；對賬腿延至收刀前（窗內 locale 與 `app.d.ts` 計數無機器承載、ADR-00063 決定四保守序，棄）。

## R14 前端

- **Decision**:
  1. **選單權限彈窗**（修改型＋新增型）：樹＝既有 getMenuTree（barrel 匯入行不動）、勾選＝getRoleMenu、首頁下拉候選＝既有 getAllPages、現值＝getRoleHome（NULL 誠實 null）、選值即打 updateRoleHome（upstream 既綁之選值事件、與確定鈕獨立、取消不還原、每次選值各一筆稽核；清空即送 null＝三形同義清空；Clarifications 第三題）、確定鈕＝updateRoleMenu（全量）；不加父子連動。
  2. **按鈕權限彈窗**（修改型＋新增型）：假資料移除、候選＝getAllButtons、現況＝getRoleButton、提交＝updateRoleButton；初始化改 `watch(visible)`。
  3. **共同守衛**（rev5 HEAD 形、`rev5:673f206e`／`rev5:B-116`／`rev5:B-129`）：受保護項＝`TreeOption.disabled`＋受控勾選集之可寫 computed setter 補回，模板 `v-model:checked-keys` 一行不動（Vue 模板屬性行變體句入憲後依新句標記）；確定鈕於現況讀成功前停用、每次開啟復位；請求世代丟棄遲到回應；切換角色只清角色維狀態（勾選、鎖定集、首頁值），候選每次開啟重取、成功才覆蓋（Clarifications 第四題）；拒因由共用攔截層純 key toast。
  4. **端點權限彈窗**（**新建**；首行一行 `[rev6-inline MANAGE-ROLE-AUTH-VIEW+ 006-authz-governance]`＝D20）：候選依路徑群組（群組鍵＝純路徑）、葉鍵以路徑與方法合成並以映射表反查（不拆字串）、顯式 `cascade`＋`check-strategy="child"`、授予側不預標受保護端點。
  5. **角色抽屜**：既有 `<NSpace v-if="isEdit">` 區加第三鈕「端點權限」與新彈窗之引入、顯隱狀態、掛載＝(iii) 3 塊新增型；(ii) 既有圈界內之 handleSubmit 更新分支改為狀態異於 `rowData` 回填值才帶 `status`、塊內註解「狀態已過必填規則、`?? undefined` 只為收窄型別」同批改寫（ADR-00070）；兩改點同單元。角色頁主檔零 diff。
  6. **回收桶頁**（**新建**兩檔；兩檔首行一行 `[rev6-inline MANAGE-POLICY-ARCHIVE-VIEW+ 006-authz-governance]`＝D20；view 目錄＝seed 選單列之 component `view.manage_policy-archive`）：8 欄、兩篩（角色代碼文字、維度下拉可清空）、共用分頁、可復原才可按且二次確認、成功後重取、表格橫向捲動寬＝各欄寬之和、不寫 static meta、自由文字欄純文字插值；路由外掛產物四檔於容器內重算；`components.d.ts` 若有變化只許工具重算形。
  7. **locale 與型節**：(iii)＝兩語 `page.manage.role.endpointAuth` 一鍵（各 1 塊；`buttonAuth` 之後、非物件末項——005 刀插入位置陷阱：插在物件末項之後必令上一行補尾逗號、塊即被歸修改型而零鑑別）＋`app.d.ts` `Schema.page` 型節 1 塊；(iv)＝兩語 `route:` 鍵 `manage_policy-archive` 與 `page.manage.policyArchive` 子樹各 1 塊＋`app.d.ts` 1 塊；後端三鍵落既有 I18N (ii)(iii) 塊內、`zh-tw.ts` 只補後端三鍵；各新增塊「拔標記必紅」變異自證。
  8. **出口斷言**：觸及含預估項之六檔之單元，出口逐檔斷言實數等於範圍欄應有值（預估項於其承載單元落地後取預估、之前計 0；新增型以全檔各項之和比對）、不等即停手升級主線。
- **Rationale**: spec FR-033～FR-039、ADR-00063 決定二／三、ADR-00070；兩顆彈窗近 24 月幾乎零改動但修改型面最大——勾選綁定一行不動為 rebase 緩解。
- **Alternatives considered**: 選單彈窗改匯入 `rev6-menu-admin.ts` 之同名 fetcher（多一處修改型、rev5 亦留 barrel，棄）；BL-00131 改後端轉移觸發（不消除舊值覆寫，ADR-00070 替代案 1，棄）；抽屜兩改點分兩單元（同檔兩用途之出口斷言須做兩次、(ii) 實數不變與 (iii) 預估 3 塊宜同一次核，棄）。

## R15 Amendment 要點與 U0 待親決清單（ADR-00063）

- **Decision**: 一次 MINOR 1.6.0→1.7.0，六款：①§I.7 島 G 六條入憲（rev5 v1.10.0 字面為底、rev6 座標改寫依其差異附表；G6 新立；ADR-00044 決定 3 所載 G1 前半／G3／G4／G5 轉正、不 supersede；停用雙護欄不轉正）②§III.2 用途 (iii)(iv) 兩列（範圍欄預估值：menu 彈窗 14＋7、button 彈窗 23＋3、抽屜 3、兩語 locale (iii) 各 1／(iv) 各 2、`app.d.ts` (iii) 1／(iv) 1）＋(ii) 列兩彈窗句③§III 修改型 Vue 模板屬性行變體句（BL-00135；活書 08 §8.4 同顆）④表外宣告 3 範圍欄入機器對賬（BL-00132）⑤島 H 連動（序言、H1 終態括號、H2 兩窗、MAJOR 射程「七島」→「八島」、承襲指針表 G 列尾註）⑥README 憲法版本鏡像＋generate。**U0 程序**：①前置體檢——ADR-00063 所引「現行」原文逐段對憲法現況、其所指單元逐一對 tasks 定稿、`git -C base-web status --porcelain` 空且 HEAD＝pin、errata 種子現算②親決序——先定島 G 條文所指之 ADR-00064 決定 1／2、ADR-00065 決定 1／3、ADR-00067 決定 1／2／6，再呈 ADR-00063 各題③逐款一題一問④ADR-00063 accepted（補親決紀錄）＋Amendment commit（主線親跑 `tools/fork-delta-lint.py` 與 `tools/route-artifact-gate.py check` 皆 rc 0、關鍵行入 commit 訊息）⑤施工前提顆（R16）。**待親決清單**（依賴序：H-a 先於 G-a／G-c1／H-b1／H-b3／P-a；G-b 先於 G-c5）：H-a 同步失敗方向與兩窗落位（建議①移 G1、H2 互引）→ G-a 島 G 標頭（建議①列區間＋申報短句）→ G-b G5 條文層級（建議 a 方向面＋兩腿名）→ G-c1～G-c7（G1～G6 與常數行字面）→ III-a 範圍欄初值形（建議①預估值）→ III-b (iv) 產物四檔（建議①不重列）→ III-c (ii) 列兩彈窗句（建議①同顆改寫）→ III-d1／III-d2（(iii)(iv) 列其餘字面）→ III-e 變體句 → III-f 表外宣告 3 → H-b1～H-b5（序言、H1 括號、H2、MAJOR 射程、指針表尾註）→ P-a 活書狀態句（建議同顆改）。**硬閘**：Amendment 顆落地前 base-web 既有檔零 diff；純新增檔與 `rev6-authz.{ts,d.ts}` 不受此閘。
- **Rationale**: spec FR-040；條文只凍方向面、常數與全文住 ADR（ADR-00063 決策驅動因子）。
- **Alternatives considered**: 見 ADR-00063 替代案 1～9。

## R16 ADR 配號與親決時點表

- **Decision**: 配號＝現行最大號 ADR-00062 之後接續，plan 期九支全數 `proposed`、草稿期 `supersedes: []`（GT-04）；收刀前另立 PATCH Amendment ADR 一支（表末列；配號待定、plan 期不起草）；accepted 時點如下表。凡被島 G 條文或 §III.2 (iii) 列紀律欄指向之決定款，於各自 accepted 前 MUST NOT 改動（確需改動＝停手升級、條文指針另走 §V.2）。

| ADR | 主題（前代出處） | 與既有 ADR 關係 | accepted 時點 | accepted 前凍結款 | 同顆連動 |
|---|---|---|---|---|---|
| ADR-00063 | 憲法 Amendment 1.6.0→1.7.0（`rev5:ADR 0053`） | 轉正 ADR-00044 決定 3、不 supersede；完成 ADR-00042 翻案觸發器第一條之複核 | U0 Amendment 顆（user 逐款親決後同顆） | ——（親決題改字即同步改寫本 ADR） | 憲法、README 版本鏡像、活書 08 §8.4 變體引文、P-a 活書狀態句、generate |
| ADR-00064 | G6 結構性封死（`rev5:ADR 0054`） | 承重前提承 ADR-00044 決定 4② | U0 施工前提顆 | 決定 1／2 | —— |
| ADR-00065 | 復原五腿＋不可復原集 3→5（`rev5:ADR 0055`） | 復核 ADR-00044 決定 4（不翻案） | U0 施工前提顆 | 決定 1／3 | —— |
| ADR-00066 | 全量替換射程＝候選集（`rev5:ADR 0056`） | —— | U0 施工前提顆 | ——（島 G 條文不直指；承載對照所引決定 8 隨 accepted 即不可變） | —— |
| ADR-00067 | 觸發列增列＋兩窗 | 增列 ADR-00043 決定 7、補述其決定 9、不 supersede；聲明 ADR-00042 兩處同字面被取代 | U0 施工前提顆 | 決定 1／2／6 | —— |
| ADR-00068 | 角色與選單已知態續行 | supersede ADR-00045 | U17 治理單元（CDP 之後、候選四款定案之後） | —— | 補 `supersedes: [ADR-00045]`、ADR-00045 `status` 改 superseded、`superseded_by` 由 generate 回填；現在式改指 |
| ADR-00069 | IP 域已知態續行 | supersede ADR-00046 | U17 治理單元 | —— | 同上（對 ADR-00046）；「七款」→「八款」 |
| ADR-00070 | 抽屜狀態欄修法（BL-00131） | 與 rev5 刻意分岔 | U17 治理單元（不早於 ADR-00068 決定 3 之候選四款中出自本 ADR 後果之兩款定案；可與 ADR-00068 同顆） | 決定 1／2（§III.2 (iii) 列紀律欄所引） | 決定 6 與後果之候選名改寫為所配款號或刪去 |
| ADR-00071 | seed-view-gate（ADR-00055 決定 3 首例） | —— | U14 接線單元同顆（不晚於；RUNBOOK §12「根據 ADR」欄只收 accepted 號） | —— | RUNBOOK §12 碼面閘表一列 |
| （配號待定＝屆時下一號） | 收刀前 PATCH Amendment：(iii)(iv) 範圍欄預估值實數化（前例 ADR-00051） | 兌現 ADR-00063 翻案觸發器第三條與後果「回填義務」 | U18 收刀前承載體檢（user 親決後 accepted、與 Amendment 同一顆獨立 `docs(constitution): amend` commit＝§V.2 步 3／4） | —— | 憲法版本 1.7.0→1.7.x、Amendment log、README 憲法版本鏡像、generate |

- **Rationale**: 施工前提四支於 U0 accepted 之理由＝①島 G 條文直指 ADR-00064／ADR-00065／ADR-00067 之決定款，條文落地而所指 ADR 仍可變＝權威鏈倒掛②四支為 U1～U10 之施工前提③內容不需 as-built 觀察（005 刀 ADR-00043／ADR-00044／ADR-00047 同形）。已知態兩支與 ADR-00070 須 CDP 實際觀察定稿（`rev5:L-046`），accepted 後 body 不可變，故排在 CDP 之後。★收刀前 PATCH Amendment（(iii)(iv) 範圍欄實數化、ADR-00063 翻案觸發器第三條）依 ADR-00051 前例須另立一支 ADR（配號＝當下下一號；憲法 §V.2 步 3「ADR 轉 accepted＋更新本檔對應段＋bump version」），本 plan 期不起草；spec FR-041／FR-046／SC-012／SC-014 同此計數與版本（plan 期九支＋收刀前 PATCH Amendment 一支、`feature_close.adrs` 十支；憲法 1.7.0、收刀前 PATCH 後 1.7.x），plan 產物一律寫「plan 期九支（ADR-00063～ADR-00071）＋收刀前 PATCH ADR 一支（配號待定）」（`contracts/code-gates.md` §8、quickstart §9 同形）。
- **Alternatives considered**: 九支全數 U0 accepted（已知態兩支未經觀察即凍結、觀察後須再 supersede，棄）；施工前提四支於各自落地單元 accepted（島 G 條文於 U0 即指向可變 body，棄）；ADR-00071 延至治理單元（RUNBOOK §12 該列「根據 ADR」欄於接線至治理單元間指向 proposed 號＝違其導言，棄）。

## R17 as-built 改寫義務（RL-0011 四形種子）

- **Decision**: 各單元收尾以 `python3 tools/docsync errata <詞>` 對下列種子枚舉（全 repo 含兩子庫 pin 樹）、逐處判讀「改／史述留／accepted 不動／生成物由 generate」、改完復掃；史料面（brainstorms、specs、reviews）與 accepted ADR body 不動；新值（「四十九」「九域」「十二支」「八島」「三類」）改後應有命中、以同指令驗；★`MSG_KEYS` 鍵數不設新值——鍵數一律指向 `MSG_KEYS`／跨端閘輸出、文件與碼註不寫實數（accepted ADR-00039 決定 3；活書 08 §8.2 同句）。現量（以行計）＝外層 HEAD `316faaf`、兩子庫 pin 樹；ADR-00063～ADR-00071 草稿未入版控、不在其內。

| 形 | 種子 | 現量 | 現在式面分布（摘） | 承載單元 |
|---|---|---|---|---|
| ①名稱 | `授權治理島` | 10 | 憲法 1、活書 06 1、`auth/enforce.rs` no-escalation 掛點 doc 1（勘誤為島 I、勿改指島 G）、ADR 3、史料 4 | U0（憲法、06）／U10（碼註） |
| ①名稱 | `島 H2` | 28 | `rules.yml` 1、活書 04 1、11 1、12 3、BACKLOG 1、`menu.rs` 1、`role.rs` 1（指同步失敗契約者依 H-a 改、指同鍵重建零繼承者留） | U0（P-a）／U10／U17 |
| ①名稱 | `島 G／I` | 7 | 活書 08 2、10 1、`rev5-blueprint-map`（生成）1 | U0（P-a） |
| ①名稱 | `凍結位`／`未入憲` | 19／17 | 憲法島 H 序言、活書 06 1、README 1；§IV 第 9 題通則不動 | U0 |
| ①名稱 | `唯一已知降級窗` | 12 | 憲法 1、BACKLOG 1、ADR-00042 2 與 ADR-00043 1（accepted 不動）、史料 7 | U0（憲法）／收刀（BACKLOG） |
| ①名稱 | `ADR-00045`／`ADR-00046` | 38／46 | 現在式面依 ADR-00068 背景（5 檔）與 ADR-00069 背景（11 檔、含 rust-api 2 檔與 base-web ip-rule 頁） | U17 |
| ①名稱 | ``限 `R_SUPER` ``／`限 R_SUPER`／`只授 R_SUPER` | 11／8／6 | 活書 06 2、12 1、RUNBOOK 1、`ip_rule.rs`／`menu.rs`／`role.rs` 各 1、`throttle` 2、`router.rs` 2＋裸詞形 `system_settings` 2、`router.rs` 2、`contract.rs` 2（seed 事實句留、能力限定句改） | U17（碼註同單元） |
| ①名稱 | `policy-archive`／`授權回收桶`／`授權彈窗` | 39／50／39 | 活書 10 1、11 1、BACKLOG 1、`schema-definition.md` 1（三頁 view 缺席句）；活書 08 §8.4 引 ADR-00045 款 1 之句 | U14／U17 |
| ①名稱 | `all_button_codes`／`未立 newtype`／`零 tuple 形` | 4／1／1 | `sys_menu.rs` 模組 doc 1（其餘 005 刀史料）／`tests/wire_i64_guard_lint.rs` 模組 doc 1／同檔 `guarded_fields_are_seen_on_real_tree` fn doc 1（其 must 名單同批補 `MenuId` 一筆） | U4／U7／U7 |
| ②未來式與「不帶」 | `授權治理刀` | 30 | 憲法 1、BACKLOG 2、`auth/enforce.rs` 1、`sys_casbin_archive.rs` 2 | U0／U5／U7（`enforce.rs` 觸發句；U9 補復原類）／U9／收刀（BACKLOG） |
| ②未來式與「不帶」 | `候選集端點`／`授權回收桶讀端與復原不帶`／`授權治理島的本體由後刀填入` | 1／1／1 | `handler/role.rs` 檔頭／`sys_casbin_archive.rs` 模組 doc ④／`auth/enforce.rs` `no_escalation_check` doc | U6／U9／U10 |
| ②未來式與「不帶」 | `三維授權與授權回收桶諸支不帶` | 1 | base-web `rev6-role-admin.ts` 檔頭出處句（仍真：指 rev5 該檔之諸支不帶入本檔；不補指向 `rev6-authz.ts` 之指針＝該檔零改、同 R2） | ——（零改） |
| ③名冊與枚舉 | `十一支`／`十二張表`／`八域`／`十七支` | 2／1／3／1 | `facade/mod.rs`／同上／`handler/mod.rs`／`tests/contract.rs` | U4／U4／U1／U1 |
| ③名冊與枚舉 | `八端點` | 12 | `handler/mod.rs` 1（`role` 域列）、`handler/role.rs` 2（檔頭首句、`// ── 八端點 ──` 分節）、`router.rs` 1（getRoleHome／updateRoleHome doc 之「角色管理八端點（`handler::role`）」）、活書 05 2（base-web 列、rust-api 列）；`rev6-role-admin.{ts,d.ts}` 檔頭 2 仍真（新十支住 `rev6-authz.{ts,d.ts}`）、`test_references.py` 沿革註 1 與史料 3 留 | U1（`handler/mod.rs`、`role.rs` 兩處、`router.rs`）／U17（活書 05） |
| ③名冊與枚舉 | `八條皆`／`八支皆已接真` | 1／1 | `handler/role.rs` 檔頭（路由保護句／現況句） | U1（立殼即改）／U6～U8（接真逐單元續寫） |
| ③名冊與枚舉 | `現有兩組讀面與一組寫面`／`藍本出處＝rev5:server/src/model/facade/sys_role.rs` | 1／1 | `sys_role.rs` 模組 doc：首句與「各支分工」清單補兩支無鎖讀；藍本出處句之 rev5 取件清單補 `active_code_of`／`active_ids_by_codes`（同 doc 對 `find_active_by_code_for_update` 之「不帶」句仍真、不改） | U4 |
| ③名冊與枚舉 | 活書逐島情境（06 §6.1／10 §10.2）與 frontmatter `rev5_blueprint` | 06 §6.1 島情境 4 則（島 A～D、E、F、H）、10 §10.2 7 則（島 A～F、H），皆無島 G（`grep -n '^### ' docs/arc42/06-runtime-view.md docs/arc42/10-quality-requirements.md`） | 06 §6.1 與 10 §10.2 各新增「授權治理——島 G」情境一則（逐島一則慣例）並補兩檔 frontmatter `rev5_blueprint` 鍵（rev5 活書 §6／§10 無同主題子節，註法同 06 選單域情境之「藍本改取」形）；藍本＝`rev5:docs/arc42/ARCHITECTURE.md` §8 授權慣例之三維授權治理段、§5 Building blocks 之 facade 段、§1 能力清單句與 `rev5:ADR 0053`～`rev5:ADR 0056`（依憲法 §I.5 重打字）；06 島 H 情境標題列「授權治理島 G 未入憲……凍結位＝ADR-00043／ADR-00044」句改指島 G 條文——該句不歸本列：隨 U0 P-a（ADR-00063 決定六；與上方 `凍結位`／`未入憲` 列同一處），P-a 取延至治理單元時才歸 U17；08 frontmatter「授權慣例」值與生成之 `docs/generated/reference/rev5-blueprint-map.md` 隨之變（其「島 G／I 承襲指針」狀態句屬上方 `島 G／I` 種子、隨 U0 P-a；生成物由 generate 重產、不手改） | U17 |
| ③名冊與枚舉 | `恰五支`／`移除面寫端`／`只由移除面寫端觸發` | 12／34／3 | `auth/enforce.rs` 1＋編排範例 2／活書 04・05・06・08・10・11・12 各 1、RUNBOOK 2、`enforce.rs` 3、`menu.rs` 2、`role.rs` 2、`main.rs` 1、`state.rs` 1／`enforce.rs` 1（講移除面類別本身之句留；編排範例 2＝workspace 依賴之同字面、無關、留） | U7～U9（碼註與 RUNBOOK：各觸發列落地單元同批改至該 commit 實況＝R10）／U17（活書） |
| ③名冊與枚舉 | `選單五寫端`／`選單樹五寫端`（入域成員列舉） | 4／4 | 活書 06 §6.1 島 H 情境①、RUNBOOK §11.1 首句／活書 12「選單序列化域」列、憲法 H1（U0 Amendment 承擔）——U7 起 updateRoleMenu／updateRoleButton 入域＝成漏列；005 刀 spec 與 ADR 為史料、留 | U7（RUNBOOK §11.1）／U17（活書 06／12） |
| ③名冊與枚舉 | `零歸檔之寫端不觸發同步` | 2 | 活書 10 §10.2 島 H 情境「回應」列（泛稱「寫端」自授予面上線起含零歸檔亦觸發者＝成假述；改限移除面或改寫為三類；ADR-00067 後果點名）；另 1＝ADR-00067 草稿 | U17 |
| ①名稱 | `決定 7 觸發矩陣` | 4 | `tests/authz_entrypoint_lint.rs` 之 `RELOAD_CALL_FILES` doc「擴列」句與 `reload_call_sites_match_roster` panic 訊息（改指 ADR-00043 決定 7＋ADR-00067 決定 1；ADR-00067 後果點名）；另 2＝ADR-00067 草稿 | U7 |
| ③名冊與枚舉 | `島 A～F 與島 H`／`六支碼面閘`／`十二條件段` | 3／3／1 | 活書 06・10・12／`.githooks/pre-commit`、`tools/bootstrap.sh`／`test_hook_wiring.py` docstring | U17／U14 |
| ③名冊與枚舉 | `只刪不補`／`刪上界以上列`／`例外恰一` | 4／10／7 | RUNBOOK 2、工具 2／活書 05 1、RUNBOOK 2、README 1、工具 4／`facade/mod.rs`、活書 05（仍真、復核） | U15／U4 |
| ③名冊與枚舉 | `三支掃描`／`三支公開`／`兩件職責` | 3／2／1 | 皆 `sys_casbin_archive.rs`：模組 doc ⑤「三支掃描歸檔都回傳實際歸檔列數」、`insert_snapshot` doc「歸三支掃描歸檔 fn」、`move_to_archive` doc「三支掃描歸檔的共同本體」與「三支公開入口」、測試 doc「三支公開 fn 的掃描範圍」（撤銷入口 `archive_revoked_policies` 亦走 `move_to_archive`＝第四支；測試 doc 隨該案是否擴及撤銷 scope 判讀）／模組 doc 首段「本檔兩件職責」（本刀增回收桶讀端與復原）；同 doc 錯誤形段之 log target 列舉「（角色域 `security.role`、選單域 `security.menu`）」補回收桶域 `security.policy_archive`（定位＝`git -C rust-api grep -n 'security.menu' -- server/src/model/facade/sys_casbin_archive.rs`） | U5（三支掃描／三支公開）／U9（兩件職責、log target 列舉） |
| ③名冊與枚舉 | `整列快照`／`不進域三支`／`首頁寫三支` | 9／3／1 | `handler/role.rs` 檔頭三句：「每筆成功每標的恰一列稽核（整列快照）」（三維寫端之稽核為計數摘要形＝data-model §10 例外登記，成假述）、「不進域三支＝[`apply_write`]」與「不進選單序列化域：新增、更新、首頁寫三支零授權面」（updateRoleEndpoints 不入域且觸授權面＝成漏列）；同詞之 `role.rs` `record_audit` doc 與測試 doc、`handler/menu.rs` 3、活書 06 選單域情境 1（皆指 005 刀寫端、仍真）與史料留 | U7（整列快照）／U8（不進域兩句） |
| ④舊數量詞 | `三十九`（含「現行三十九」5） | 8 | `router.rs` 4、`tests/contract.rs` 3、`test_references.py` 1 | U1 |
| ④舊數量詞 | `恰 17 支`／`恰 36 支` | 1／1 | `sys_role.rs` 模組 doc 之本檔測試計數／`sys_menu.rs` 模組 doc 之本檔測試計數 | 增減該檔測試之單元（預期 U4／U3；以實數現算、不增即不改） |
| ④舊數量詞 | `五支公開寫入入口` | 1 | `sys_casbin_archive.rs` 模組 doc 具型交易機器守句（「入域一支＋歸檔四支」；本刀增 `archive_revoked_policies`、`restore` 兩支公開寫入入口，正面孿生與 `compile_fail` 段同批＝R9.2、R18 U9） | U5／U9 |
| ④舊數量詞 | `七款`／`八款` | 6／10 | 活書 11 1（IP 域）／活書 06 1、11 1（角色與選單）；NOTES 之 005 刀收刀條屬史述 | U17 |
| ④舊數量詞 | `三 reason`／`恰三值`／`恰上列三值` | 11／3／1 | 活書 05 1（同句另含「掃描歸檔回實際歸檔列數＝同步觸發門之唯一依據」＝授予面以 Applied 為門後失準、同改）、06 2／`sys_casbin_archive.rs` 2（`sys_user.rs` 1 不相關）／同檔 1 | U5／U17 |
| ④舊數量詞 | `69 處`／`圈界塊 46`／`單行形 27`／`rev6-{settings` | 2／1／1／2（活書 08；`69 處` 之 004 刀檔與 ADR-00051 為史料、留） | 活書 08 §8.4 fork-delta as-built 段：inline 修改型實數與逐檔分項、現算合計（圈界塊／單行形／新檔檔頭）、我方新檔清單（本刀增 `rev6-authz.{ts,d.ts}` 與兩支 view 新檔） | U17（依 `tools/fork-delta-lint.py` 綠訊息與 `grep -c` 現算改寫；BL-00132 之「以現算為準、不另對賬」只指對賬腿射程、不免本段改寫） |
| ④舊數量詞 | `archive_reasons_pin_three_literals`（釘案測名） | 2 | `sys_casbin_archive.rs` 測試模組 1（改名＝R9.1、data-model §7-1）、活書 10 §10.2 守門列 1（引測名、隨改名同批改指） | U5 |
| ④舊數量詞 | `七島`／`實際歸檔 ≥1 列` | 13／76 | 憲法 2／多數為移除面門之真述、留；改寫限稱觸發集合者 | U0／U10 |

- **Rationale**: RL-0011／RL-0015；spec FR-047。命中分布為取證現量、施工以同指令現算為準。
- **Alternatives considered**: 收刀前一次總掃（碼註與單元出口之 lint 窗內持假述、且 review 輪會重報，棄）。

## R18 執行單元切分 U0～U18（tasks 定稿之骨；派發真源＝tasks.md）

| 單元 | 內容 | 硬序與出口 |
|---|---|---|
| U0 ★主線 | 前置體檢＋親決（R15）；兩顆 commit：Amendment 顆、施工前提顆（ADR-00064～ADR-00067 accepted） | 一切施工之前；Amendment 前 base-web 既有檔零 diff |
| U1 骨架 | ROUTES 尾接十列（rev5 相對序）＋`ROUTES_COUNT` 49＋兩處釘值測同批（`router.rs`、`test_references.py`）；新建 `policy_endpoints()`／`endpoint_methods()`＋型別推導環之編譯面自證；兩組 handler 空殼（`role.rs` 八支、新建 `policy_archive.rs` 兩支）；`handler/mod.rs` 宣告、ASCII 序與「九域」；contract 49 case 佔位＋授權態矩陣（Policy 保護、`8888`） | 不觸 base-web |
| U2 對賬腿 | `tools/fork-delta-lint.py` 範圍欄對賬腿＋變異自證 | MUST 早於首個觸及 base-web 既有檔之單元（U7） |
| U3 測試基建 | 兩族守衛補回被撤 seed 授權列、植入件與 raw INSERT 落建立者、BL-00136 形①改錨、`ID_RANGES` 增列 | MUST 早於任一撤銷 seed 列之單元 |
| U4 授權 facade | `sys_casbin_policy.rs` 之讀與候選半（型、現況讀、濾點件、聯集讀端、`protected_endpoint_set`）、`sys_role` 兩讀件、`facade/mod.rs` 十二支、`DOMAIN_WRITE_SIDE_FILES` 7→8（寫入半＝規劃、授予 INSERT、`set_role_*` 與具型交易 doctest 隨 U7／U8：其撤銷半依 U5 之撤銷入口、私有件無從掛 doctest；`Dimension::revoke_reason()` 亦隨 U7——其回傳之撤銷原因常數由 U5 立；tasks 期定） | 依 U3 |
| U5 歸檔面 | 三撤銷原因、3→5、釘案翻臂、撤銷入口＋doctest、模組 doc ④改寫 | —— |
| U6 讀端五支 | getRoleMenu／getRoleButton／getRoleEndpoints／getAllButtons／getAllEndpoints；`handler/role.rs` 檔頭「不帶」句改寫；零新拒因鍵 | 不觸 base-web |
| U7 選單維與按鈕維寫端 | `sys_casbin_policy.rs` 寫入半（`plan_full_replace`／`apply_full_replace`〔收撤銷原因參數〕／`set_role_menu`／`set_role_buttons`＋`Dimension::revoke_reason()`＋具型交易 doctest）、入域、授予面收場件、稽核件、選單 id newtype（寫端回應 `effective` 首現處）＋`wire_i64_guard_lint.rs` 模組 doc 與 `guarded_fields_are_seen_on_real_tree` 之 doc／must 名單改寫、`protectedRevoke` 首發＋三檔 locale＋`app.d.ts`、reload 源碼釘改寫、觸發矩陣現在式（授予面類首現：R10 所列碼註諸處、`RELOAD_CALL_FILES` doc 之觸發門句、RUNBOOK §11.2 `ok` 判讀句改至本單元實況）、NOT-granted 機器證；名冊載入新列之變異自證（暫改 (iii) 列範圍欄任一反引號路徑之反引號內字面為不含 `/` 之非路徑 token→`tools/fork-delta-lint.py` rc 2→以存原文寫回；形＝`contracts/code-gates.md` §1.1）；出口預估斷言 | 首個觸及 base-web 既有檔之單元 |
| U8 端點維寫端＋封死 | `set_role_endpoints`＋具型交易 doctest、不入域、`protectedGrant` 首發（三檔 locale＋`app.d.ts`）、R_SUPER 豁免探針、封死變異自證、觸發矩陣句補端點維授予（同 U7 諸處） | 出口逐檔斷言（含預估項之 en-us／zh-cn／`app.d.ts`；不等＝停手升級；R14.8） |
| U9 回收桶兩端點 | `handler/policy_archive.rs`、列表件與復原件＋doctest、`notRestorable` 首發（三檔 locale＋`app.d.ts`）、`RELOAD_CALL_FILES` 擴列與植入字面＋觸發矩陣句補復原類（三類齊；RUNBOOK §11.2 句後半「復原」改「選單復原」；同顆）、兩逐域名冊、五腿負向與旗標同判準四案、NoOp、不入域案 | 出口逐檔斷言（同 U8；R14.8） |
| U10 觸發矩陣特性鎖定 | 特性鎖定測、取消安全、即時生效雙斷言、自救路徑端到端、`rules.yml` 錨註解（島指針依 H-a）、殘列演練；RUNBOOK §13「剛授予或剛復原之端點仍回 `5003`」分診（三類觸發齊後補；ADR-00067 決定 9；§11.2 `ok` 判讀句隨 U7～U9、§11.2 流程指針之島 G 情境一項＝U17） | —— |
| U11 wire | `rev6-authz.{ts,d.ts}` 新檔、快照重抽、`wire_schema.rs` 擴 `Api.Authz` 與正反例 | 只建 base-web 新檔 |
| U12 兩顆授權彈窗 | menu／button 彈窗之修改型＋新增型、共同守衛 | 出口逐檔斷言 |
| U13 端點彈窗與抽屜 | 端點彈窗新檔、抽屜 (iii) 3 塊＋(ii) 圈界內狀態欄修法、`endpointAuth` 鍵 | 出口逐檔斷言 |
| U14 回收桶頁 | 頁面兩檔、(iv) locale 與型節、產物四檔重算、seed-view-gate 進場與接線四處（含 RUNBOOK §12 碼面閘表一列；ADR-00071 同顆 accepted）、`schema-definition.md` 三頁句 | seed-view-gate 不早於本頁落地；出口逐檔斷言（含預估項之 en-us／zh-cn／`app.d.ts`；R14.8） |
| U15 走查工具 v3 | 基準檔 v3、seed 角色列可變欄、RUNBOOK §9c | MUST 早於 U16 |
| U16 CDP 三方對照 | 三顆彈窗、抽屜第三鈕、首頁下拉、回收桶頁；候選四款觀察；網路請求事件單邊斷言；seed 角色寫入前後套基準 | 一律 opus[1m]／xhigh |
| U17 治理單元 | 活書 04／05／06／08／10／11／12（含 06 §6.1／10 §10.2 島 G 情境各一則與 frontmatter `rev5_blueprint` 鍵＝R17）、RUNBOOK §11.2 流程指針補島 G 情境一項（與 06 島 G 情境同顆）與其餘 RUNBOOK 節之 as-built 復核（§9c 屬 U15、§12 屬 U14、§11.2 三類判讀句屬 U7～U9、§13 分診屬 U10）、名詞表七新條＋三改寫（並由 user 定候選詞「撤銷殘留」是否入名詞表——入則第八條；R20）、ADR-00068／ADR-00069／ADR-00070 親決 accepted、現在式改指與假述掃除、容器內全量測試與全部閘 | 排在 U16 之後 |
| U18 收刀前承載體檢 | H1 括號兌現（兩入域寫端與 3→5 皆已落地）、(iii)(iv) 範圍欄 PATCH 實數化（PATCH ADR 一支＝R16 表末列）、BL-00047 反向確認（migration 目錄恰兩支、演進帳 entries 空）、帳本條文備妥、FR-054 DoD | final holistic review 之前 |

- **Rationale**: 共享高風險檔序列鏈＝`router.rs`／`tests/contract.rs`（U1 後逐單元加案）、`handler/role.rs`（U1／U6／U7／U8／U10）、`sys_casbin_policy.rs`（U4／U6～U8）、`sys_casbin_archive.rs`（U5／U9）、`error.rs`＋三檔 locale＋`app.d.ts`（U7～U9 隨首發）、`authz_entrypoint_lint.rs`（U4／U9）——同檔單元不並發。對賬腿排在首個落鍵單元之前＝ADR-00063 決定四之保守序；brainstorm 單元草案把落鍵之後端單元排在對賬腿之前，依 spec FR-042 重排。CDP 排在治理單元之前＝已知態先觀察後 accepted。
- **Alternatives considered**: brainstorm 草案序（測試基建 U2、對賬腿 U11、文件 U16、CDP U17：落鍵單元早於對賬腿、已知態先 accepted 後觀察，棄）；讀端與寫端同單元（單元過大、跨檔一致性審查成本升，棄）；三拒因鍵集中一單元（msg-key-gate 與名冊雙向閘「每鍵須有實發點」夾擊，棄）。

## R19 RL-0013 棄案反例回跑（對所選方案跑同一反例）

| 題 | 棄案與棄因（反例） | 對所選方案回跑 |
|---|---|---|
| Q2 手動撤銷不可復原 | 選單／按鈕維撤銷可復原：刪選單 S（路由名 r）→ 以 r 重建 S′ → 回灌舊授權使 S′ 繼承＝島 H2 破口 | S 名下選單維歸檔原因只可能是 `role_soft_delete`／`menu_soft_delete`／`menu_revoke`，全屬五值集 ⇒ 第①腿拒；按鈕碼絕版後重現同理；代價「撤了只能重勾」入 ADR-00068 款 15；**成立** |
| Q3 封死只圈 protected=TRUE | 全封政策端點：須改 seed 受保護旗標或另立名冊 | 授出 updateRole／addRole 等給 R_ADMIN：三維授權寫端屬封死集 ⇒ 受讓者造出之角色零授權、無從自授；R_SUPER 恆禁停用、代碼不可變 ⇒ 擋住提權鏈；21 支下放效果逐支入款 9；**成立** |
| Q6 記窗 | 入域寫端等待在途同步以關窗：只關一半、需跨交易可見之新狀態 | 「請求於 commit 後被丟棄 ⇒ 窗無界」：收場整段交脫離請求之 task（R6④）⇒ 同步照跑完、窗仍有界；**成立** |
| Q8 射程＝候選集 | `live∖desired`：R_SUPER 端點彈窗原樣提交 ⇒ 撤銷集含受保護列 68 ⇒ 恆被拒 | 候選外 16 列兩邊皆進不去 ⇒ R_SUPER 原樣提交撤銷 0、新授 0；殘餘形＝選單治理域環成員及其子孫（候選內而樹不呈現），記已知邊界；**成立** |
| Q9 BL-00131 前端修 | 後端改轉移觸發：不消除兩分頁舊值覆寫 | 只改名稱 ⇒ 不帶 `status` ⇒ 護欄不觸發、他分頁之停用存續；真改停用 ⇒ 照帶照擋；先改再改回 ⇒ 終值＝回填值 ⇒ 不帶；**成立** |
| Q12 並行後送出者覆蓋 | 版本比對：需版本欄（migration）或新協定、屬範圍變更 | 「後送出者漏帶受保護列」⇒ 撤銷集觸及受保護 ⇒ 整批拒 ⇒ 受保護列不因覆蓋而失；端點維被覆蓋者可自回收桶復原；**成立** |
| Q16 撞現役＝NoOp | 回拒：多次撤銷留下之同鍵歸檔列恆停在回收桶、每按每拒 | NoOp 消費歸檔列 ⇒ 其餘同鍵列再按亦 NoOp、逐列清空；零稽核代價入款 12；**成立** |
| 澄清二 讀端只回候選內 | 照回全部現役列：讀端回寫端動不到之列、寫後讀回與生效集合不一致 | 「藏起候選外列誤導治理者」：候選外列無可觀察授權效果（端點路由未註冊、選單已刪、按鈕碼不屬任何未刪選單），路由一註冊即自動入候選；**成立** |
| 澄清三 首頁下拉選值即寫 | 提交時才寫：須改 upstream 既綁事件＝修改型擴面、且與 rev5 HEAD 行為分岔增 CDP 差 | 「選值後按取消、以為未存」：寫入時點明記款 13、每次選值落稽核可追溯；確定鈕只送選單維、兩寫端互不依賴；**成立（以已知態承擔）** |
| 澄清四 換角色只清角色維狀態 | 連候選一起清：候選與角色無關、清之只多一次空樹窗 | 「候選重取失敗」：候選成功才覆蓋 ⇒ 沿用上次候選；現況讀已清且失敗 ⇒ 確定鈕停用 ⇒ 不可能送出空期望集；**成立** |
| 澄清五 seed 角色具名例外 | 一律自建角色：自建角色無帳號可持有、已知態無從以使用者路徑觀察 | 「款 16 停用並重啟用 seed 角色留下改回痕」：走查工具 v3 回寫可變欄與審計欄、`schema-gate check` gate2 逐列驗；例外只及 CDP 觀察、整合測試仍取自建角色；**成立** |
| handler 落點 | 三維寫端另立新域檔：多一域、兩名冊各擴、角色鎖讀與拒因跨檔重持 | 住 `role.rs`：`DOMAIN_LOCK_CALL_FILES`／`RELOAD_CALL_FILES` 角色列已在、零擴；代價＝reload 源碼釘須改寫（U7 承擔）；回收桶自成一域＝兩逐域名冊各加一列、反例「新域 log 字面無守」不成立；**成立** |
| 復原鎖角色列 | 以 `v0` 代碼鎖讀：須新建以代碼鎖讀件、鎖足跡較寬 | 同代碼重建（角色 5 刪後以同代碼新建 9）：以 `role_id`＝5 鎖讀查無 ⇒ 拒；旗標②半代碼→9≠5 ⇒ false；等鎖期間角色被刪 ⇒ PG 重判剔除 ⇒ 拒；直種「`role_id` 指活角色 A、`v0` 為他代碼」⇒ 代碼比對拒；**成立** |
| 不設 23505 | 保留收窄：分支為死碼、兩支測只能以繞過鎖序之直寫假造 | 復原與端點維授予並發同角色同鍵：兩者皆鎖同一角色列 ⇒ 序列化、後到者鎖內見已在現役 ⇒ 不重授／NoOp；序列失步撞主鍵＝環境故障 ⇒ `5000`；**成立** |
| R_SUPER 豁免探針 | 探針植在標的自身名下（rev5 形）：改正第③腿後標的已持有 ⇒ 落 NoOp、負向案 vacuous | 植於第三方合成代碼名下並先自證「∈ 封死集、R_SUPER 與對照臂皆不持有」⇒ 改正探針 `protected` 為 FALSE 即 Applied；拆豁免分支 ⇒ R_SUPER 臂轉拒；**成立** |
| CDP 先於治理 | 治理單元在 CDP 前：已知態先 accepted、觀察到新症狀即須再 supersede | CDP 在前：候選四款依觀察定案、ADR-00068／ADR-00070 一次 accepted；「CDP 中發現活書需改」⇒ 治理單元在後一次改齊；**成立** |
| 授予面收場件新建 | 直套 `archived > 0` 門：只新授零撤銷 ⇒ 永不同步 | outcome 門：Applied（含空 diff）即同步、Rejected 零同步；空 diff 多重建一次冪等；**成立** |
| `archivedBy`／`reload_counts` 自持 | 提升共用：併 log target／動兩支既有測試模組 | 自持：`each_domain_keeps_its_own_log_literals` 逐域字面仍各住各檔；三份 `reload_counts` 各服務本域、無跨域斷言；**成立** |
| 施工前提四支 U0 accepted | 各自落地單元 accepted：島 G 條文於 U0 即指向可變 body | U0 accepted 後「實作期發現決定款須改」⇒ 依 ADR-00063 翻案觸發器停手升級、另立 ADR；不靜默改 body；**成立** |
| seed 列補回先刪後補 | 先補後刪：復原回插之新 id 列與被撤 seed 列同七欄鍵 ⇒ 回補撞唯一索引被 `DO NOTHING` 吞掉、新 id 列隨後被刪 ⇒ seed 列永久缺席 | 先刪 `id >` 水位 ⇒ 新 id 同鍵列先消失 ⇒ 補回原 id 不撞；arm 前已存在之合法殘列（id ≤ 水位）不動；**成立** |

## R20 交 tasks 與實作期定值之事項（非 NEEDS CLARIFICATION）

- 新建件名已定、tasks 照引不另定：`router::policy_endpoints()`／`router::endpoint_methods()`／`sys_casbin_policy::protected_endpoint_set`／`sys_role::active_ids_by_codes` 與其餘新建件（`sys_role::active_code_of`、`sys_casbin_policy::governed_button_codes`、`sys_casbin_archive::archive_revoked_policies`／`list`／`restore`、兩收場件、兩稽核件、`msg_key` 三常數）之家＝data-model §13，wire 型名（含選單 id newtype `MenuId`）之家＝兩支 wire 契約之共用型節；譯文之家＝三檔 locale `backend` 子樹（ADR-00039 決定 2），鍵、發出點、語意要求與落地時序住 `contracts/msg-keys.md`。
- 授予面與復原收場 task 被取消之告警字面（若另立，RUNBOOK §13 log 引文同批補；ADR-00067 決定 9）。
- `ID_RANGES` 新列之號段值；contract 之 policy 驗證函式擴既有 `verify_role_menu_policy` 或另立同形函式（授權態矩陣新建一表已定＝`contracts/code-gates.md` §3 `tests/contract.rs` 列）。
- `role.rs` reload 源碼釘之改寫形（兩呼叫點或單一共用呼叫形）以實作為準。
- (iii)(iv) 範圍欄實數（單元出口逐檔斷言；不等即停手由 user 定當刀 PATCH 或延至收刀前 PATCH）；收刀前 PATCH ADR 之配號。
- ADR-00068 決定 3 之候選四款之觀察結果、定案與款號；ADR-00070 決定 6 之對應改寫。
- 活書 06 §6.1／10 §10.2 島 G 情境之字面（射程、藍本與承載單元已定＝R17）；`rules.yml` 錨註解之島指針依 H-a 結果。
- 候選詞「撤銷殘留」（被撤端點於過渡窗內或重試耗盡後仍放行；ADR-00067 決定 6 已用此詞）是否入活書 §12 名詞表：治理單元由 user 定奪（入則為名詞表第八新條、spec FR-047 七條之外；不入則 ADR-00067 與活書以描述句承載）。
- BL-00132 收單事件註明「活書 08 §8.4 逐檔數以現算為準」（該節本已寫命令形）、不另立衍生 BL；對賬腿射程維持 spec FR-042（憲法範圍欄入對賬）。
- errata 處數以施工時同指令現算為準（R17 為取證現量）；`arch_impact` 以收刀時 `git diff --stat <merge-base>..HEAD -- docs/arc42/` 現算；淨流量本窗 −3（刪 5、新記 2；收窄 3 不計）。
- Technical Context 零 NEEDS CLARIFICATION。
