# Research — 005-role-menu-crud（Phase 0）

> 輸入：spec（clarify Q1～Q5 定案 2026-09-23）＋brainstorm `docs/brainstorms/005-role-menu-crud.md`（定稿 `4dd28dc`＋grill 兩輪修訂 `8e3bc4d`／`d78fc3e`；§0 拍板 Q1～Q5／G1～G4／R1-Q1～Q10／R1-Q4b／R2-Q1、既定不問 8 條、工程判斷 1～43、§3 設計十節、§9 單元骨架）＋`rev5:005-role-menu-crud` 全套與 rev5 凍結 worktree（唯讀；外層 `7eab28a`／base-web `9833308`／rust-api `92919b9`，取證時三處 HEAD 皆核等）＋rev6 碼面唯讀勘查（外層 `bbc4841`、rust-api `246d5ff`、base-web `3fb3ea31`；2026-09-23 plan 期取證 workflow 六鏡、全程唯讀）。每題 Decision／Rationale／Alternatives。
> CLAUDE.md §2 兩件必列：**R2 rev5 對應碼清單**、**R3 rev6 拍板差異點**（承 `rev5:ADR 0019` 形）；RL-0013 棄案反例回跑＝R19。行號不入本檔（跨檔引用不用行號；取證行號只供撰寫時內部參考）。

## R1 技術脈絡定值（零新依賴）

- **Decision**: 本刀**零新依賴、零版本變更**。後端沿 rust 1.96.1（`rust-toolchain.toml`）、axum 0.8.9、sea-orm 1.1.20、casbin **2.20.0**（`default-features = false`）、tokio 1.53.1、metrics 0.24.6、serde_json 1.0.151；前端沿 vue 3.5.34、naive-ui 2.44.1、vue-i18n 11.4.2、typescript 6.0.3、`packages/axios` 之 qs 6.15.1（精確釘版）。非法標頭名判別走 `axum::http::HeaderName::from_bytes`（既有再匯出、不另加 `http` 依賴；工程判斷 17）；父選擇器元件 `NTreeSelect` 屬 naive-ui 既有元件、只觸發 `components.d.ts` 重算。
- **Rationale**: 全域 §6 版本紀律——本刀一切能力（advisory 鎖＝raw SQL、判定面重建＝既有 casbin API、分頁／形制驗證＝標準庫）皆可由既有依賴承載；casbin 2.20.0 之 `load_policy` 語意為本刀硬禁令之前提（R7），升版屬翻案觸發。
- **Alternatives considered**: 另加 `http` crate 直接依賴以取 `HeaderName`（與 axum 再匯出同物、多一個釘版面，棄）；引 `regex` 驗代碼／路由名形制（標準庫字元判定即足、零依賴，棄）。

## R2 rev5 對應碼清單（實作單元動工前逐檔先讀；rev5 凍結 worktree＝HEAD 終態、含 006～008 增量——逐檔剔除見 R3 清單 A）

| rev5 檔（`../fork260509-rev5/rust-api/server/`） | rev6 對應 | 處置（重打字＋註解 rev6 語境；rev5 出處帶 `rev5:`） |
|---|---|---|
| `src/handler/role.rs`（生產段約三分之一；兩測試模組） | `src/handler/role.rs`（新） | role 6＋roleHome 2＝8 支；DTO 形承 rev5（`RoleListQuery` 之 `status` 為字串形、`RoleUpdateReq` 三態、`RoleHomeQuery`／`RoleHomeRes`／`RoleHomeUpdateReq`）；★不帶：006 三維授權寫端、`get_all_pages`（改住 menu.rs＝工程判斷 16）、getAllButtons／getAllEndpoints、007 之 `Identity` sid、`rev5:B-113` 探針；★rev5 寫端 handler 皆以 `audit_operator` 取操作者（帶 degraded 欄）、rev6 改 `common::operator_from_context`＋各域 `operator_from`（R5） |
| `src/handler/menu.rs` | `src/handler/menu.rs`（新） | menu 7＋getMenuTree＋getAllPages＝9 支；`MenuRecord` 28 欄＋可缺席 `children`、`MenuTreeRecord`、`MenuAddReq`／`MenuUpdateReq`（三態欄集承 rev5、`status`／`parentId` 非三態）；★改：缺席 size 語意（R8）、href／buttons 形制（R9）、受保護兩腿（R9） |
| `src/handler/common.rs`（八件） | `src/handler/common.rs`（擴） | 帶：泛型 `tristate<T>`、`blank_to_none`、`db_status_to_wire`、`wire_two_value_to_db`（`rev5:B-094`／`rev5:B-108`／`rev5:B-127` 終態、首版即入＝工程判斷 23）；★不帶：`audit_operator`（帶 degraded 欄、target 借 `security.ipgate`）、`resolve_operator_names`（rev6 有 `sys_user::find_names_by_ids` 等價）、`MAX_CURRENT`（改住 envelope＝R8）；rev6 既有 `operator_from_context`／`json_or_default` 兩件直接消費並重評（R5） |
| `src/model/facade/sys_role.rs` | `src/model/facade/sys_role.rs`（擴寫端） | `SEEDED_ROLE_IDS=[1,2,3]`／`SUPER_ROLE_CODE="R_SUPER"` 單一宣告源（`rev5:B-137` sys_role 半）、`ROLE_CODE_MAX_LEN=64`、`page_query`、`all_active_enabled`、`find_active_by_id_for_update`、`create`／`update`／`delete_one_locked`、`batch_delete_locked`（rev6 名；rev5 為自開交易並取域鎖之殼 `soft_delete`／`batch_soft_delete`＋私有 `delete_one_locked`）、`home_of_role`／`set_home`（rev6 名；rev5:`update_home`）；★rev6 改：寫端公開入口一律收 `&DatabaseTransaction`（交易由 handler 持有、R6）、刪除家族回傳「實際歸檔列數」（rev5 回 `()`＝R7 觸發門之前提）；`sys_user_role` 補 `count_by_role`／`role_ids_of_user`（rev5 同名、rev6 現無） |
| `src/model/facade/sys_menu.rs` | `src/model/facade/sys_menu.rs`（擴治理域＋寫端） | `list_governed`／`build_governed_tree`（孤兒升根）／`paginate_top_level`、`governed_tree`（rev6 名；rev5:`menu_tree`；輕量樹、`label`＝`menu_name`）、`display_route_names`（rev6 新立；rev5 為 `handler/role.rs` 之 `get_all_pages` 對 `list_active` 就地排序）、`MENU_ANCESTOR_HOP_LIMIT=64`、`ROUTE_NAME_MAX_LEN=100`、`create`／`update`／`delete_one_locked`／`batch_delete_locked`（rev6 名；rev5:`batch_soft_delete`）／`restore_locked`（含第四腿＝`rev5:ADR 0051`）、`obsolete_codes`、`button_codes_of`；★rev6 改：facade 內**不再** clamp size（全取不被截在 100＝R8）、同層序 `(order ASC NULLS LAST, id ASC)` 顯式 ORDER BY、`button_codes_of` 遇壞形不再靜默跳過（寫端先驗＝R9）、`all_button_codes` 屬 006 不帶 |
| `src/model/facade/sys_casbin_archive.rs` | 同名（新） | `MENU_DOMAIN_LOCK_KEY`（值改 `rev6menu`）、`enter_menu_domain`（thin fn、handler 於交易首動作呼叫）、`menu_domain_waiter_count`（pg_locks 觀測 helper）、三 reason 常數＋`is_non_restorable_reason`（**三值**，rev5 HEAD 五值屬 006）、`insert_archived`（v0 反查活性角色填 `role_id`、查無 NULL）、`archive_all_role_policies`＋`archive_menu_policies`／`archive_button_codes`（後兩支 rev6 新立；rev5 為 `sys_menu.rs` 私有 `archive_policy_rows_of`）——三支皆回傳歸檔列數、取「pub 收 `&DatabaseTransaction` 入口＋私有 `<C: ConnectionTrait>` 本體」形（`sys_operation_log` 前例），以帶入 rev5「掃描後插隊、DELETE 以已掃 id 圈定」之等集迴歸測（自訂 ConnectionTrait 注入）；★注入旗標改 `AtomicBool::fetch_or`、不得用 `.swap(`（ipgate 整樹換版呼叫掃描、測試模組零容忍）；★不帶：`ArchiveDimension`／`list`／`restore`（006） |
| `src/model/facade/mod.rs` | 同名（擴） | `violated_constraint`（`rev5:f841b04`）、`now_ts`（`rev5:B-123`③）、`ilike_contains`（`rev5:B-138`；不寫 ESCAPE、`$1`、欄參數 `&'static str`）；模組 doc「一張表配一支」改寫（`sys_casbin_archive` 同寫兩表） |
| `src/auth/enforce.rs` | 同名（擴） | `rebuild_enforcer`（四步鏡像 init）、`reload_enforcer`（函式內 `static RELOAD_SERIAL`、`RELOAD_MAX_ATTEMPTS=3`／`RELOAD_RETRY_BACKOFF_MS=50`、`casbin_reload_total{outcome}`）、`#[cfg(test)] mod reload_seam`（`rev5:932ba8c`、Notify＋Mutex 形）；★doc 觸發矩陣以 rev6 五支重寫（rev5 HEAD 為 006 七列形）；init 改委派 rebuild |
| `src/obs.rs` | 同名（改） | `pre_register_metrics` 補 `casbin_reload_total` 三 outcome 顯式零＋「樣本行恰三」上界守 |
| `tests/authz_entrypoint_lint.rs`（005 pin 形） | `tests/authz_entrypoint_lint.rs`（新） | 帶三道名冊守恆之兩道（`RELOAD_CALL_FILES`、`ENFORCER_WRITE_FILES`）＋rev6 新增第三道（重載／建構 token 只許家檔）；判定呼叫收斂（`rev5:B-044` 之 `ALLOWED_DECISION_FILES`）＝**同檔帶入**（R12）；★不帶：007／008 名冊 |
| `tests/menu_domain_serialization.rs` | 併入 `tests/contract.rs` 外之 src 側真庫測（R6） | 帶：鎖 key 字面案、deleteRole×deleteMenu NOT-granted 等待案、`menu_domain_waiter_count` 只計本 key 案；★不帶：006 兩案；探針 id 改走號段登記（R11） |
| `src/model/mod.rs::test_db`（`RoleCleanup`／`MenuCleanup`／`CasbinCleanup`） | `src/model/facade/test_kit.rs`＋`tests/common/mod.rs` | ★不承碼：rev5 寫死 setval 值；rev6 形＝arm 時現讀水位與序列（`IpRuleRowsGuard` 前例、RL-0031）＋指派列清理先於角色列 |
| `tests/wire_schema.rs`（RoleAdmin／MenuAdmin 十二支＋roleHome 兩支） | `tests/wire_schema.rs`（擴） | 帶其裁判形（`rev5:c0067ae`＝`rev5:B-098`、`rev5:dc1cc8c` 之 roleHome 兩支）；rev6 另補請求型之 id／ids 具名型、`PageRes`、表驅動鍵集斷言（R10） |
| base-web `views/manage/role/*`（三檔）、`views/manage/menu/{index.vue,modules/menu-operate-modal.vue}` | 同名（修改型） | rev5 HEAD 形（含 `rev5:854a72ee` 分頁列凍結、`rev5:ae1ac0c9` 之 `rev5:B-100` 清勾選、`rev5:84f283c7` 之 `rev5:B-132` pageSize 歸位）；★不帶：006 端點權限鈕與其彈窗三塊、三顆授權彈窗接真；表頭疊寫改 prop（R14） |
| base-web `service/api/rev5-{role,menu}-admin.ts`、`typings/api/rev5-{role,menu}-admin.d.ts` | `rev6-{role,menu}-admin.{ts,d.ts}`（新） | role 6＋roleHome 2、menu 7＋getMenuTree；★不帶：policy-archive、三維授權、getAllButtons／getAllEndpoints wrapper；型名依 rev6 004 慣例與後端 DTO 同名（R14） |
| base-web locale／`app.d.ts`（`page:` 樹 9 鍵、backend 22 鍵） | 同名（新增型圈界） | `page:` 樹 9 鍵鍵名承 rev5；★插入位置改（R14 陷阱）；backend 鍵 rev6 為 24（+`hrefInvalid`／`buttonsInvalid`）；`protectedMenu` 譯文不照搬 |

## R3 rev6 拍板差異點（翻案與新增；烤入 implementer 防回歸清單）

**清單 A——rev5 HEAD 帶了、rev6 本刀不帶**（006～008 增量；implementer 讀藍本時逐項剔除）：①reason gate 五值（`menu_revoke`／`button_revoke`／`endpoint_revoke`）②三維授權讀寫端六支與 getAllButtons／getAllEndpoints③授權回收桶 `list`／`restore` 與 policy-archive 頁④`all_button_codes`、`active_ids_by_codes`、`active_code_of`⑤三顆授權彈窗接真、端點權限鈕與其彈窗⑥`protected_endpoint_set`／`protectedGrant`／`protectedRevoke`⑦`Identity` sid、no-escalation 本體與其名冊⑧使用者域一切（`sys_pwd_custody`、user 頁、user 鍵）⑨稽核頁與 purge 名冊⑩`audit_operator` 帶 degraded 欄之拒寫形⑪`RELOAD_CALL_FILES` 之 policy_archive／user 兩列⑫`POLICY_ENDPOINT_COUNT` 等 007 bump。

**清單 B——rev6 翻案或新增**（每條對應拍板或工程判斷；實作與 review 以此為準、藍本相反處不得回帶）：

| # | 面 | rev5 形 | rev6 形 | 出處 |
|---|---|---|---|---|
| B1 | deleteRole 家族之判定面同步 | 零觸發（免 reload 論證） | 實際歸檔 ≥1 列即 commit 後同步；觸發矩陣五支 | R1-Q2、ADR-00043／ADR-00044 |
| B2 | 可空文字欄空字串 | `""`＝清空（`rev5:B-102`）；名稱欄 `""`＝不動 | 可空文字欄 null 或 `""`＝清空落 NULL（新增同形）；名稱欄 null 或 `""`＝`nameRequired` | R1-Q3、ADR-00047 |
| B3 | 新增路徑名稱空字串 | 零驗 | 拒 `nameRequired` | Clarifications Q5 |
| B4 | getMenuList/v2 缺席 size | 100（facade 再 clamp） | 回全部頂層、回應 `size`＝實得頂層數；明名入口＋白名單 | R1-Q4／Q4b |
| B5 | getDeletedMenus 缺席 size | 100 | 通則 10 | 工程判斷 4 |
| B6 | 分頁常數與 clamp | 各 handler 各持 | envelope 單一共用規則、四端點同用、IP 規則清單改引（wire 逐位元不變） | Q3 |
| B7 | 受保護選單 | 只擋刪除 | ＋不可停用、不可改父（同鍵 `protectedMenu`、譯文改寫） | R1-Q5、R2-Q1 |
| B8 | href | 直傳 | 空字串清空、有值限 http(s) | R1-Q6 |
| B9 | buttons | 直傳、壞形靜默跳過 | 形制＋長度驗證、先於絕版計算 | R1-Q7 |
| B10 | getAllPages | 006、住 role.rs | 本刀、住 menu.rs | Q2、工程判斷 16 |
| B11 | 表頭寫入口 | 外層 `v-show`＋內層 `v-if` 疊寫＋碼註 | 共用元件 `showAdd`／`showDelete` prop（`withDefaults` 預設 true） | Q5 |
| B12 | 交易歸屬 | facade 自開交易並取域鎖 | handler 持交易、域鎖為交易首動作、facade 寫端收 `&DatabaseTransaction` | FR-043、ip_rule 形 |
| B13 | 入域寫端失敗腿 | 只業務拒因顯式 rollback、`?` 上拋依賴 drop | 一切失敗腿顯式 rollback＋源碼釘 | FR-045、LL-00026 |
| B14 | 測試守衛 | 寫死 setval 值 | arm 時現讀水位與序列 | 工程判斷 10、RL-0031 |
| B15 | 拒寫事件 | `audit_operator` 帶 degraded 欄、target 借 `security.ipgate` | 各域自有 target（`security.role`／`security.menu`）、`refused` 欄、零 degraded 欄、零計數 | 工程判斷 11 |
| B16 | 譯文之家 | 刀內 `contracts/msg-keys.md` | 三檔 locale 各為該語之家（ADR-00039）；`contracts/msg-keys.md` 只作候選鍵表 | ADR-00039 |
| B17 | 域鎖 key | `rev5menu` | `rev6menu`（`0x7265_7636_6D65_6E75`） | 工程判斷 2 |
| B18 | IP 域已知態載體 | 單支 ADR | 新 ADR supersede ADR-00040 | G1 |
| B19 | 非法標頭名 | ——（rev5 形即只 warn） | 只 warn、不計降級、不改讀預設名 | R1-Q8 |
| B20 | ILIKE／23505 收窄／時戳 | 007 才收攏 | 本刀收攏至 `facade/mod.rs`、`sys_ip_rule` 改引＋具型交易簽章 | G3、工程判斷 22 |
| B21 | 判定面重載 token | 無此守 | 重載與建構 token 只許判定面家檔（第三道名冊守恆） | 工程判斷 25 |

**rev5 對 rev4 之十一項防回歸**（`rev5:005` research R2；本刀照帶、烤入 prompt）：restore 現役列＝業務錯誤非冪等成功／上下文缺席＝拒寫 `5000`／`AuditOperation` 小寫封閉詞彙／`find_by_keys` 不搬／`SELF_SERVICE_ROUTES` 不帶回／zh-tw 不上 runtime／域鎖字面不帶前代值／deleteRole 入域／業務錯誤純 i18n key 不攜參／menu 彈窗 `fetchGetAllRoles` 殘留不帶／「不再重載＝終態」句翻案。

## R4 rev5 收刀後本域 commit 三分（藍本取 HEAD 形之依據；工程判斷 1）

| commit | 判定 | 本刀取用面 |
|---|---|---|
| `rev5:f841b04` | 帶 | `violated_constraint`；handler 共用件收攏（`audit_operator` 帶 degraded 欄之形不帶） |
| `rev5:47e8a67` | rev6 已有等價 | 測試建構點收攏（rev6 `state_from_parts` 兩處） |
| `rev5:c0067ae` | 帶 | 空字串三案（語意改 ADR-00047 承載）＋RoleAdmin／MenuAdmin 裁判形 |
| `rev5:932ba8c` | 部分帶 | `reload_seam`＋臨界區 `pause_if_armed`＋交錯時序案；`protected_endpoint_set` 不帶 |
| `rev5:8f31bbc` | 部分帶 | `get_all_pages` 與其測（改住 menu.rs）；getAllButtons／getAllEndpoints 不帶 |
| `rev5:dc1cc8c` | 部分帶 | `RoleHomeRes`／`UpdateRoleHomeReq` 裁判四案 |
| `rev5:6ee82e2` | 部分帶 | `db_status_to_wire` 收 common、`now_ts` 收 facade/mod.rs；`rev5:B-115` 之「無 ORDER BY」教訓轉為本刀同層序顯式排序 |
| `rev5:7575379` | 部分帶 | `wire_two_value_to_db` 收 common |
| `rev5:e02251d` | 帶 | `ilike_contains`＋`SUPER_ROLE_CODE` 單源（sys_role 半） |
| `rev5:55bb3e3`、`rev5:fd23de9`、`rev5:4858236` | rev6 已有等價 | 水位守衛形、`oneshot_json`、test_kit 位置 |
| base-web `rev5:1597a671` | 部分帶 | roleHome 兩 wrapper 與兩型；三顆彈窗接真與端點彈窗不帶 |
| base-web `rev5:ae1ac0c9`／`rev5:854a72ee`／`rev5:84f283c7` | 帶 | 清勾選／分頁列凍結／pageSize 歸位（碼註以 rev6 語境重寫：缺席 size 回實得頂層數而非 100） |
| 其餘 006～008 commit（`rev5:ddbab53`、`rev5:51f1e19`、`rev5:6dcd41d`、`rev5:65a5cf3`、`rev5:d22a01c`、`rev5:f455858`、`rev5:4889b6d`～`rev5:be1d7e1`、`rev5:2273816`、`rev5:7aa0ac3`、008 四顆；base-web 006～008 十餘顆） | 不帶 | —— |

## R5 模組邊界與共用件落點

- **Decision**: 後端新檔三支＝`handler/role.rs`（8 支）、`handler/menu.rs`（9 支）、`model/facade/sys_casbin_archive.rs`；擴寫＝`facade/sys_role.rs`、`facade/sys_menu.rs`、`facade/mod.rs`、`handler/common.rs`、`envelope.rs`、`auth/enforce.rs`、`obs.rs`、`router.rs`、`error.rs`、`config.rs`；`handler/mod.rs` 宣告序依 ASCII 插為 `ip_rule` < `menu` < `role` < `route`、兩新域皆 `pub mod`（tests crate 取 DTO）。`handler/common.rs` 重評（BL-00113）結論＝**兩件簽章不動**（`operator_from_context` 回 `Option`、呼叫點自發 `tracing::error!` 帶各域 target——「log 留呼叫點」切法續行，使各域字面守不被合併）；新增四件（`tristate<T>`、`blank_to_none`、`db_status_to_wire`、`wire_two_value_to_db`）皆 `pub(super)`、零 `tracing::debug!`（`fallback_event` 恰 1 則之守不動）；測試側 `table_state`／`audit_table_state` 與本刀新增之角色／選單庫態快照**續不合併**（窗界謂詞各異、合併即失去各表之具名斷言訊息），結論落該檔 doc。`system_settings.rs` 私有 String 三態改引泛型件（掃到該檔者為整樹腿：ipgate 換版呼叫、throttle 鎖定鍵字面、obs 出口／發射字面、`entity_access_lint`、`wire_i64_guard_lint`；「degraded 字面」與「debug 恰 1」兩腿之射程只有 `ip_rule.rs`／`common.rs`、不含本檔——泛型件移入之目的檔 `handler/common.rs` 受此兩腿與 `entity_access_lint` 守；泛型件本體皆不含受守 token，RL-0070 查畢無衝突；改引時以 `use super::common::tristate;` 匯入、保住該檔四處 [`tristate`] 文件連結、`deserialize_with = "tristate"` 字面不變；該檔 8 處 ADR-00015 註已於 U0 施工前提顆改指 ADR-00047、共用件單元只做私有三態改引）。兩新 handler 之寫端 body 取用一律以 `common::json_or_default(` 限定路徑形呼叫、餵本域專屬收斂訊息（`each_domain_keeps_its_own_log_literals` 名冊五元組之 body 收斂半邊；契約 `code-gates.md` §3）。清單查詢抽取器（`FromRequestParts`、壞形收斂 default、發 `tracing::debug!`）**住各 handler 檔**（ip_rule 形），不上 common（否則破 `fallback_event` 恰 1）。
- **Rationale**: 依域拆檔使執行單元允許清單有圈界力；兩件簽章若改成「回 `Result` 並在件內發 log」，`each_domain_keeps_its_own_log_literals` 所守之「各域 target 字面在各域檔」即被併掉（工程判斷 11 明令不得）。
- **Alternatives considered**: 共用件放 `handler/mod.rs`（該檔只宣告模組、混入 fn 破其職責，棄）；`operator_from_context` 改回 `Result<_, AppError>` 並內建 log（併掉 target，棄）；抽取器泛型化上 common（撞 `fallback_event`、需改守，收益僅省兩份十行樣板，棄）。

## R6 選單序列化域

- **Decision**: 交易由 handler 持有、拆**外殼＋內層**（ip_rule `apply_write`／`write_in_txn` 同形）：外殼 `begin` → 內層 `<op>_in_txn(&txn, …)`（首句＝`sys_casbin_archive::enter_menu_domain(txn)`；其後 facade 鎖讀與寫端〔公開入口收 `&DatabaseTransaction`〕→ `sys_operation_log::write_in_txn`）→ `commit`（任一失敗腿顯式 `txn.rollback()` 後回錯）→ commit 後依歸檔列數同步；源碼釘斷言外殼 begin 後第一個呼叫即內層（FR-045 源碼釘同檔）。`enter_menu_domain` 為 facade 內 thin fn（raw `SELECT pg_advisory_xact_lock($1)`、`$1`＝`MENU_DOMAIN_LOCK_KEY`），其餘 facade fn 一律不自取域鎖。空陣列批刪於 begin 之前提前回成功（不取域鎖）。機器證＝逐進域寫端一案：甲交易持域鎖；乙＝測試自開交易、`SET LOCAL lock_timeout = '10s'`（大於 5s 輪詢窗）後呼叫該寫端之內層、外罩 `tokio::time::timeout(30s)`；以 `menu_domain_waiter_count`（`pg_locks` 之 `locktype='advisory' AND NOT granted AND objsubid=1 AND ((classid::bigint << 32) | objid::bigint) = key`）輪詢至 1、再放甲；結果先存變數、待兩交易收乾淨才斷言（「後到者須等到放行才完成」形；`sys_user` 前例為「後到者須逾時」形、兩者之 lock_timeout 取值相反）。不進域三支（addRole／updateRole／updateRoleHome）各一案斷言甲持鎖時乙直接完成。
- **Rationale**: FR-043「不下沉」＝域鎖取得點只在交易擁有者、facade 寫端可被組合進同一交易而不重入；key 高 32 位 0x72657636、低 32 位 0x6D656E75 皆 < 2^31，pg_locks 公式可直比（取證實算）；與 `sys_user::advisory_lock_user`（key＝裸 uid）key 空間不碰撞、鎖集合零交集（login 交易不取域鎖、域內寫端不取 per-user 鎖）。
- **Alternatives considered**: 承 rev5 facade 自開交易（handler 無法把稽核列併入同交易之外的組合、且與 rev6 ip_rule 交易殼不一致，棄）；`pg_blocking_pids`（對 advisory 等待之語意較間接、rev5 已踩坑，棄）；域鎖做成 AppState 欄之行程內 Mutex（多連線多行程皆不序列化 DB 交易、且開第八欄須新 ADR，棄）。

## R7 判定面同步

- **Decision**: `enforce.rs` 新 `rebuild_enforcer(db) -> casbin::Result<Enforcer>`（`DefaultModel::from_str(MODEL_CONF)` → `SeaOrmAdapter::new(db)` → `Enforcer::new` → `load_policy`，任一步 `Err` 即整體 `Err`）；`init_enforcer` 改委派之（boot 與同步同一條建構路徑）。`reload_enforcer(state: &AppState)`：函式內 `static RELOAD_SERIAL: tokio::sync::Mutex<()>` 全程持有（rebuild＋換上＋重試）；每次嘗試成功 → `#[cfg(test)] reload_seam::pause_if_armed().await` → 取寫鎖一行賦值換上 → `casbin_reload_total{outcome="ok"}`；每次失敗（含第 3 次）→ `retry` 計數＋`tracing::error!(target: "security.authz", attempt, max, cause)`；attempt < 3 時線性退避 50ms×attempt 後重試（末次失敗後不退避）；三次皆敗 → 另計 `exhausted`＋error、舊面續用（三次全敗＝retry 3＋exhausted 1；rev5 as-built 同）。`const _: () = assert!(RELOAD_MAX_ATTEMPTS == 3 && RELOAD_RETRY_BACKOFF_MS == 50);` 常數自證。呼叫點＝兩 handler 於 commit 成功後、`if archived > 0`（批刪為合計、至多一次）；呼叫時不持判定面讀鎖。`obs.rs` 預註冊三 outcome。★施工約束（取證發現、烤入 implementer）：①`ipgate/mod.rs` 之整樹掃描腿禁 `.store(`／`::store(`／`.swap(`／`::swap(`／`rcu`／`compare_and_swap` 呼叫形（連測試模組整檔零容忍）⇒ 換上一律寫 `*guard = new;`、seam 用 `Notify`＋`std::sync::Mutex<Option<Arc<Gate>>>`（rev5 形）、不得用 `AtomicBool::store`／`mem::swap`／名為 `swap` 之 fn；②`throttle/mod.rs` 之整樹字面腿禁 `throttle:lock:`／`lock_ttl_secs`／`redis_lock` 等子字串 ⇒ 新識別字與註解避開；③`RELOAD_SERIAL` 住函式內 static、**不入 AppState**（ADR-00036 恰七欄封條不動）。
- **Rationale**: casbin 2.20.0 之 `Enforcer::load_policy` 為先清空再載入（rev5 ADR 與碼註所引；本輪 host 無原始碼可複核＝版本鎖註解＋特性鎖定測試承擔）——對現役實例裸呼，一旦載入失敗即留空政策＝含 R_SUPER 全拒、唯重啟可救；另建實例成功才換上＝全有或全無。互斥序列化封「後 commit 先換上、先 commit 慢重建後蓋回舊快照」之窗（`rev5:B-105`）；於 rev6 同受兩 handler、五支觸發點呼叫。
- **Alternatives considered**: 對現役實例 `clear_policy`＋逐條 `add_policy`（非原子、中途失敗半載，棄）；以版本號比對丟棄舊快照（需在 casbin 外另立版本面、仍要序列化 DB 讀取時點，棄）；同步改由背景週期輪詢（引入延遲窗、與 H2 即時失效相違，棄）；RELOAD_SERIAL 入 AppState 第八欄（觸 ADR-00036、收益零，棄）。

## R8 分頁共用規則

- **Decision**: `envelope.rs` 新增（置於 `serialize_opt_i64_number_guarded` 之前、使該 fn 續為生產區末 item）：`pub const PAGE_DEFAULT_SIZE: u64 = 10`、`PAGE_MAX_SIZE: u64 = 100`、`PAGE_MAX_CURRENT: u64 = 10_000_000`；`pub fn page_params(current: Option<u64>, size: Option<u64>) -> (u64, u64)`（缺席→1／10；clamp current [1, 10^7]、size [1, 100]）；明名入口 `pub fn page_or_all(current: Option<u64>, size: Option<u64>) -> PageSpec`（`size` 缺席 → `PageSpec::All`；否則 `PageSpec::Page(page_params(..))`）。壞形收斂由各 handler 之抽取器負責（整串收斂 default＝兩欄 None）⇒ 選單治理清單壞形即全取。IP 規則清單改引 `page_params`、刪其私有三常數；`handler::ip_rule` 模組 doc 指向活書 08 §8.2。`PageSpec::All` 時回應 `current=1`、`size`＝實得頂層數（零頂層＝0）、`total`＝頂層總數。名冊案（住 `envelope.rs` 測試）：生產面＝逐檔扣除每個行首測試模組區塊（同 `obs.rs` 之 `production_part` 形；整檔測試模組依 `#[cfg(test)]`＋可帶可見性前綴之 `mod <名>;` 現算豁免）——不採「切到首個行首 `#[cfg(test)]`」（`enforce.rs`／`state.rs` 之 item 級門控後仍有生產碼，且整樹切面腿之被切檔不以 `("<name>.rs"` 形出現、BL-00111 lint 抽不到）；計數取 `page_or_all(`／`(page_or_all)`／`::page_or_all` 三形聯集（RL-0026）、扣定義處；分期＝分頁規則單元落地時恰 0 處、讀端單元接線後恰一處且在 `handler/menu.rs`；變異自證含「於 `auth/enforce.rs` item 級門控之後植一處呼叫必紅」。逾界：facade 以 `(current-1)*size` 取頁、`current` 取 clamp 後值回填（10^7 × 100 遠小於 i64 上界、OFFSET 不溢位）。
- **Rationale**: Q3＋R1-Q4b；例外有名字才能被名冊守、被活書例外表列、被 review 抓擴散。IP 規則清單既有案＋新增缺席／逾界兩案（as-built 有行為、無測試釘＝取證發現）共同證「wire 逐位元不變」。
- **Alternatives considered**: 全取例外以 `Option<u64>` 哨兵值傳入通用 helper（無名字、無法名冊守，棄）；facade 保留 clamp 作雙保險（全取入口被截在 100＝靜默資料遺失，棄）；`size=0` 視同全取（與「顯式 0 取下界」通則衝突、R1-Q4b 已拍，棄）。

## R9 寫端語意細則（部分更新、父欄比較、jsonb 欄、受保護兩腿）

- **Decision**:
  1. **可空欄清空**（ADR-00047）：可空文字欄（角色 `roleDesc`／`roleMemo`／`roleHome`；選單 `routePath`／`component`／`icon`／`i18nKey`／`href`／`activeMenu`／`menuMemo`）null 或 `""`＝落 NULL；可空非文字欄（選單 `hideInMenu`／`keepAlive`／`multiTab`／`constant`／`order`／`fixedIndexInTab`／`query`／`buttons`／`iconType`）null＝落 NULL、有值＝設值（ADR-00015 決定 1 之非文字半續行）；新增路徑可空文字欄同形（`""`→NULL）。
  2. **`parentId`**：非三態（null＝缺席）；更新時「改父」＝出現且 0→NULL 正規化後之值**不等於現值**——等於現值＝該欄無變更（不跑父驗證與防環、受保護列不拒）。★理由：upstream 與 rev5 彈窗編輯態恆送 `parentId`，若「出現即改父」則受保護列一切編輯皆被 `protectedMenu` 擋；孤兒列（父被直改庫軟刪）同值送回亦不致誤拒。提前 no-op 判定仍以「出現」計（`parentId` 出現即非 no-op，走鎖列後比對）。
  3. **受保護列停用腿**：`status` 解析為停用（`'2'`）即拒 `protectedMenu`（不比對現值；受保護列經 API 不可能已停用）；啟用值照常可寫。
  4. **`buttons`**：null 或陣列；陣列成員皆物件、`code` 為非空字串 ≤100 字元（以 Unicode 字元計）、同清單不重複；`desc` 不驗；`[]` 與 null 皆落其原值（`[]`→jsonb `[]`；承 rev5、兩者於一切計算中同為空集）。**`query`** 承 rev5 直傳（零驗；FR-031 只約束 buttons、24 鍵已凍結不增）。
  5. **`constant`** 更新時出現 null 或 false＝清除常量性 → 反查治理域全深後代（Clarifications Q1）；出現 true 或改父而效值為常量 → 驗父鏈全祖先常量性（頂層豁免、鏈斷保守拒）。
  6. **`status`（兩域）／新增路徑之 `menuType`**：非三態；`wire_two_value_to_db` 先 trim、恰 `"1"`／`"2"`，其餘（含 `""`、null）＝缺席；更新路徑之 `menuType` 不經解析、出現即拒；`iconType` 為三態狀態類欄（見 1：null＝清空、非 null 值走恰二值解析、值域外＝缺席）；角色停用雙護欄以「解析為非啟用」觸發。
- **Rationale**: 1＝R1-Q3；2／3＝FR-024 之可施工解讀（「變更其父」「可停用」皆指狀態轉移），並令 CDP「其餘欄照常可編」成立；4＝R1-Q7 射程；5＝Clarifications Q1＋`rev5:ADR 0051`。
- **Alternatives considered**: `parentId` 出現即改父（受保護列 UI 編輯全數被拒、違 FR-024「其餘欄照常可編」，棄）；`buttons` 之 `[]` 正規化為 NULL（wire 上新建列與 seed 列形不同之差本即存在於 rev5、正規化反使 rev5 CDP 對照多一差，棄）；`query` 同驗形制（需新鍵、spec 未要求，棄；如需＝新拍板）。

## R10 wire 裁判面

- **Decision**: 受審名冊＝本刀新增全部 wire 型（實數以 `tools/wire-schema.py` 抽取為準；預期：`Api.RoleAdmin.{RoleRecord,RoleListQuery,RoleAddReq,RoleUpdateReq,RoleIdReq,RoleBatchDeleteReq,RoleHomeQuery,RoleHomeRes,RoleHomeUpdateReq}`、`Api.MenuAdmin.{MenuRecord,MenuTreeRecord,MenuListQuery,MenuAddReq,MenuUpdateReq,MenuIdReq,MenuBatchDeleteReq}`）＋`Api.Common.PaginatingQueryRecord`（BL-00112）；getAllRoles 之後端 DTO 對 upstream `Api.SystemManage.AllRole`、`MenuTreeRecord` 另對 upstream `Api.SystemManage.MenuTree` 同斷言（FR-005／FR-027）。「序列化鍵集＝快照 properties 鍵集」做成表驅動 helper，涵蓋既有七讀型（含 `IpRuleRecord`）＋本刀新讀型＋分頁信封；`Api.Route.MenuRoute`（交叉型佔位）具名豁免附理由。首屏真串（FR-057）：`getRoleList`／`getDeletedMenus` 取頁面首屏物件經 qs 6.15.1 於 base-web 容器內實跑產出之字面（plan 期推定角色清單＝`current=1&size=10&roleName=&roleCode=&status=`，實作時以實跑為準）、`getRoleHome` 以 wrapper `{id}` 經序列化器產出、getMenuList/v2 釘無參形。BL-00109 錨＝`tools/wire-schema.py` 新腿：純讀檔斷言 `base-web/packages/axios/src/options.ts` 之 `paramsSerializer` 仍為無選項 `stringify(params)` 且 `package.json` 之 qs 為 `6.15.1`，置於 `cmd_check` 合成 self-test 之後、staged-gate 短路之前無條件執行；self-test 另釘「staged-gate 判跳過時本腿仍執行」；不擴收窄 pathspec。
- **Rationale**: BL-00105／BL-00112／BL-00109 三條到期；讀型逐型斷言由表驅動承擔，ADR-00046 款 6 重述時才為真述。
- **Alternatives considered**: 全域開 `additionalProperties: false`（動抽取器與全部快照、屬專項，棄）；錨落 rust 側（rust-api 容器看不到 base-web 工作樹，棄）；擴 staged-gate pathspec 納 axios 兩檔（連動 pre-commit submodule-sync 段＝BL-00074 到期，棄）。

## R11 測試基建

- **Decision**: src 側 `test_kit.rs` 新守衛五支（`RoleRowsGuard`／`MenuRowsGuard`／`CasbinRuleRowsGuard`／`PolicyArchiveRowsGuard`／`UserRoleRowsGuard`）＋一支組合守衛（依 FK 固定 Drop 序：指派列→歸檔列→授權列→選單列→角色列），水位一律＝`COALESCE(max(id) FILTER (WHERE id < 9_300_000_000), 0)`（界值＝`SYNTHETIC_UID_FLOOR`、號段一律落此界之上；`casbin_rule` 與歸檔表雖不以顯式 id 造列亦同套此形，免得走查植入之顯式大 id 抬高水位）＋序列 `(last_value, is_called)`，皆 arm 時現讀；Drop 刪 `id >` 水位（號段內列因此恆被清、形同 `SessionRowsGuard` 合成腿無水位＝LL-00017 守法）再 setval 回現讀值；指派表為複合主鍵、刪除集＝arm 快照鍵集差 ∪ `role_id >` 角色守衛水位者、且先於角色列；tests 側 `tests/common` 以 `RestorePlan`／`run_restore` 形另立同族計畫；各配自證測（含「指派列清理序反腿」自證：反序刪角色列必撞 FK RESTRICT；另一腿：arm 前預置號段內殘角色列＋其指派列，API 造列仍於 Drop 被清、序列回位、FK 不擋）。造列號段＝`test_kit.rs` 單一常數表依「表×檔」登記（高於 `SYNTHETIC_UID_FLOOR` 之既有慣例、同表不同檔不重疊；tests 側檔列如 `tests/contract.rs` 之角色／選單／指派號段亦登記於此表），tests 側以同值字面自持其號段常數（`JwtConfig` 與 tests/common 同值字面前例）、並於 tests/common 純資料段以 `include_str!` 讀 `src/model/facade/test_kit.rs`、斷言自持值與表中對應列逐字相等（登記處唯一、漂移即紅）；角色／選單／指派造列一律顯式大 id；`casbin_rule` 例外：經真判定面之新增政策路徑造列（取 nextval）、守衛以現讀序列還原——使「刪除前判定面確實命中」可斷言（FR-052 防恆綠）。稽核斷言一律取 `OpLogRowsGuard` 水位窗。`route.rs` 既有「seed 下常量路由回 `[]`」真庫案保留（守衛 Drop 後 seed 態恆成立、同持 `DB_SERIAL` 不交錯）；新增「存在常量列時回非空」案住 `tests/contract.rs`、由 tests 側選單守衛清列（FR-021）。BL-00110：7777 腿 denylist 鍵改 `RestorePlan.keys` 腿 RAII。
- **Rationale**: 業務五表皆 gate2 逐列比對面；寫死 setval 遇 dev 庫走查殘列即令下一次 nextval 撞 PK（RL-0031）；同一表並存「顯式大 id 造列」與「寫端 API 走 nextval 造列」兩種來源，若水位取不帶界之 `max(id)`，一次中斷殘留之大 id 列即把水位抬高、此後 API 造列落水位之下永不清且序列被 setval 回舊值＝自我延續之連環紅（LL-00017 同機制）——帶界水位使兩種來源皆恆被清；FK RESTRICT 決定清理序。
- **Alternatives considered**: 交易 fixture 改 seed 列再 rollback（無法測 commit 後之判定面同步與跨連線門檻，棄）；`casbin_rule` 亦顯式大 id 直 INSERT（判定面不持有該授權、端到端「刪前命中」無從斷言，棄）。

## R12 機器守（新 lint 與既有 lint 擴充）

- **Decision**:
  1. **`tests/authz_entrypoint_lint.rs`**（新、`mod common;`、重用 `strip_comments_and_literals`／`collect_rs_files`）：①`reload_enforcer` 生產使用點檔集＝名冊（`reload_enforcer(`／`(reload_enforcer)`／`::reload_enforcer` 三形聯集、RL-0026；判定面同步單元落地時空冊、角色寫端單元擴 `handler/role.rs`、選單寫端單元擴 `handler/menu.rs`）②判定面寫鎖取得形檔集＝空冊（家檔 `auth/enforce.rs` 豁免）③`load_policy`／`Enforcer::new` token 於生產面只許家檔；④**判定呼叫收斂（承 `rev5:B-044` 之 `ALLOWED_DECISION_FILES` 形、同檔帶入）**：strip 後之 casbin 判定呼叫形——完整 token `enforce`／`enforce_with_context`／`enforce_mut`／`enforce_ex`（後隨非識別字元；`enforce_role_path_method`／`enforce_mw`／`enforcer` 等更長識別字由 token 完整性排除）、前導限定符 `.` 或 `::`（容空白換行）、後隨 `(` 或 `::<`——之檔集＝{`auth/enforce.rs`}；模組路徑 `auth::enforce::…`（後隨 `::識別字`、非呼叫形）不命中；射程承前代＝src 全樹**連測試模組**（現樹唯一命中＝家檔一處、首日零誤紅）；casbin 升版 MUST 重核後綴表；變異自證＝植入 `.enforce_ex(`／`CoreApi::enforce(` 必紅、植入 `enforce_role_path_method(` 不紅。★①～③之生產面定義（對 spec FR-052 措辭之精修、同批改 spec）：各檔**扣除行首測試模組區塊**（行首 `#[cfg(test)]` 其後緊接行首 `mod <名> {`〔可帶可見性前綴〕、至下一個行首 `}`）後之全文；item 級 `#[cfg(test)]` 項保守計入生產面（`enforce.rs`／`state.rs` 之 item 級門控在前、其後仍有生產碼——取證模擬證「切到首個行首門控」形會漏掉兩檔其後之生產碼）；豁免集（整檔以測試門控閘入之模組＝由 `#[cfg(test)]` 其後可帶 `pub`／`pub(crate)` 等可見性前綴之 `mod <名>;` 宣告現算〔現樹唯一實例＝`model/facade/mod.rs` 之 `pub(crate) mod test_kit;`、形同 `obs.rs` 之 `cfg_test_mod_decl_names`〕、tests 樹）以機器判準現算並自我對賬。各附植入反例變異自證。
  2. **BL-00111 lint**（`tests/test_module_tail_lint.rs`、新、`mod common;`、行掃描）：判準①射程＝BL-00111 條文 grep 判準現算之切面腿所在檔 ∪ 跨檔腿名冊字面所指之被切檔（`("<name>.rs"` 形抽取、以所在檔目錄為基準解析〔`include_str!` 語意〕、逐一解析存在性；FR-074 擴 `production_code_emits_no_degraded_field`／`each_domain_keeps_its_own_log_literals` 射程後，`handler/role.rs`／`handler/menu.rs` 由此入射程——同批改 spec FR-073 射程句）；★grep 判準與名冊抽取之字面皆在字串常值內，故兩者於原文（或 Keep 視圖）執行、判準①之 item 掃描才用 Drop 視圖（否則兩集合皆空）；判準①＝首個行首 `#[cfg(test)]` 之後每個 column-0 item 之屬性鏈含 `#[cfg(test)]`（頭形 regex 納 `pub(…)`／`async`／`const`／`unsafe`／`extern`／`type`／`trait` 等）；判準②（**射程獨立＝src 全樹**、生產面同 1 之定義）＝零 `obs::` 出口之 item 別名匯入——樣式涵蓋 `use (crate|server|super…)::obs::<ident> as <ident>` 與分組 `obs::{ … <ident> as <ident> … }`（含跨行）；★判準②若沿判準①之射程即漏 `ipgate_blocked` 唯一生產呼叫檔 `middleware/mod.rs`（與 bin crate 之 `server::obs::` 形）＝BL-00111 假結案；變異自證六形（item 級門控不紅、第二測試模組不紅、常值內行首碼不紅、`pub(super) fn` 植入必紅、別名匯入植入必紅、於 `middleware/mod.rs` 植別名匯入必紅）；既有十二支腿 docstring 補指本腿。
  3. **i64 守衛 lint**（`wire_i64_guard_lint.rs` 擴）：①泛型 wire 型名冊（`Res`／`PageRes`）與樹上泛型 `Serialize` 型集合恰等＋實例化掃描②手寫 `impl Serialize` 絆線③型級普查等式（`derive(Serialize)` 錨數＝解析成功數，兼抓巨集生成型）；各附變異自證；檔頭「已知不抓的邊界」與「與 rev5 藍本的差異」兩段改寫。
  4. **體檢三案**：BL-00107（併入 3③）、BL-00123（請求上下文缺席之每請求總數案：至少打一支角色或選單寫端、釘「其餘端點 2 格」；`with_local_recorder` 套 app 級不可行即改 serial 差值形）、BL-00115（dev 信任模型對賬三態：`APP_TRUST_MODEL_PATH` 缺席＝具名跳過、在而讀檔失敗＝紅並附重建命令、讀得到＝逐欄比對 `dev_trust_model()`）。
  5. `page_or_all` 名冊案（R8）、`components.d.ts` 只准兩行增列之斷言、兩顆授權彈窗零 diff 斷言、ip-rule 頁 `show-add` 綁權限之模板靜態斷言（R14）。
- **Rationale**: 工程判斷 18／25／7；spec 措辭精修之兩處皆為取證發現之「判準字面落地即漏抓」形（brainstorm 風險 13），精修方向為**擴大覆蓋、不縮**。
- **Alternatives considered**: 判定面 lint 沿「切到首個行首 `#[cfg(test)]`」（漏 `state.rs` 門控後生產碼、並使本 lint 自成 BL-00111 射程外之新切面腿，棄）；BL-00111 射程取全樹（`enforce.rs`／`state.rs` 首日誤紅、工程判斷 18 已棄）；另立 char 級解析組（成 BL-00108 第三份，棄）。

## R13 004／002 域連帶（零 wire 行為變更）

- **Decision**: ①`facade/mod.rs` 三件上提、`sys_ip_rule` 改引（`cidr_text_contains` 改呼 `ilike_contains("wbip_cidr::text", ..)`——比對面為運算式非裸欄名、`&'static str` 字面照收）②BL-00096：`sys_ip_rule` 四寫端與 `find_by_id_for_update` 改收 `&DatabaseTransaction`；三檔 40 處裸連線測試呼叫改自開交易並 commit（`ipgate/mod.rs` 測試植列必 commit、門鈴重載走另一連線）；模組 doc「一律收泛型連線」段改寫③BL-00082：`load_trust_model` 對 tunnel 與每筆 cdn 之 `connecting_ip_header` 驗合法性、非法＝新 `TrustLoadKind` 變體（`degraded_source()` 回 None）＝一則結構化 warn（`scope`＝`tunnel` 或 `cdn`〔欄型 `&'static str` 不變、不帶索引〕；`reason` 帶 `cdn[i]` 索引、原字面與改寫建議）、`obs.rs` 之 `trust_load_kind_maps_only_real_degradations_onto_the_roster` 與 `main.rs` 報出點案各補新變體一列（`None`、WARN 一行、無 degraded 欄；後者 doc「五種」同批改六種）、原字面保留（中介層查標頭自然失配＝該覆蓋層停用、`cdn_visitor_ip` 有 cdn 條目時本即不回退預設名＝現況語意）、`IP_DOMAIN_DEGRADED_SOURCES` 恰八不動④ADR-00046 supersede ADR-00040；「二態」現在式鏡像以 `python3 tools/docsync errata 二態` 現算逐處分流（取證：現在式面 12 處、含 `deploy/trust-model.dev.toml`、`trust-model-config.md`、活書 06／11、RUNBOOK §16.1、兩處測試 doc）⑤ADR-00047 supersede ADR-00015；`system_settings.rs` 行為零變化——8 處註隨 U0 施工前提顆改指、私有三態改引隨共用件單元。
- **Rationale**: G2／G3／G1／R1-Q3／R1-Q8；每件皆以既有案全綠為出口（IP 規則清單 wire 逐位元、系統設定空字串案零改形）。
- **Alternatives considered**: 見 brainstorm G1～G3 棄案；非法標頭名計入第九降級來源（R1-Q8 已棄）。

## R14 前端

- **Decision**: 用途 (ii) 九檔（role 三、menu 兩、`table-header-operation.vue`、兩語 locale、`app.d.ts`）；新檔四支（`service/api/rev6-{role,menu}-admin.ts`＝`BASE-WEB-WRAPPER+` 檔頭、`typings/api/rev6-{role,menu}-admin.d.ts`＝`BASE-WEB-ADAPT+` 檔頭；`Api.RoleAdmin`／`Api.MenuAdmin` 獨立命名空間、型名與後端 DTO 同名、不入 barrel、消費端直接路徑 import）。wrapper：role 6（含 `fetchGetAllRoles`——rev5 形；upstream barrel 同名函式續由使用者頁抽屜消費、本刀不動）＋roleHome 2、menu 7＋`fetchGetMenuTree`；getAllPages 走 upstream barrel。共用表頭：`withDefaults(defineProps<Props>(), { showAdd: true, showDelete: true })`，備援插槽內新增鈕 `v-if="showAdd"`、批刪 NPopconfirm `v-if="showDelete"`（修改型逐行 `原行:`）；menu 頁已刪模式傳 `:show-add="false" :show-delete="false"`、不覆寫預設插槽；ip-rule 頁改 `:show-add="hasAuth('ipRule:add')" :show-delete="false" @add="handleAdd"`、刪疊寫碼註；未知 `wbipType` 於映射取值與 `$t` 之前退回原字串。★locale 插入位置陷阱（取證模擬證實）：`fork-delta-lint` 遇塊內含移除行即整塊歸修改型並跳過——在 `form:{}` **最末項之後**插入必令上一行補尾逗號（一行移除＋新增）⇒ 該塊零鑑別；故兩語 locale 之 `form.*` 新鍵一律插在 `form` 內**非最末項之間**（例：`form.roleMemo` 插在 `form.roleStatus` 與末項 `form.roleDesc` 之間；`form.menuMemo`／`form.parentRoot` 插在 `form.buttonDesc` 與末項 `form.menuStatus` 之間），標籤鍵同理避開物件末項；`app.d.ts` 型成員以 `;` 結尾、無此問題。各塊落地後「拔標記必紅」變異自證。`components.d.ts` 以 unplugin 重算、只准 `NTreeSelect` 兩行（介面一行、全域 const 一行）。menu 頁分頁列凍結＝`itemCount: undefined`＋`pageCount: 1`＋`page: 1`＋`pageSize: 0`＋`disabled`＋自備 `prefix`（顯真實筆數）。
- **Rationale**: Q5、工程判斷 3／13／20／38、FR-058～FR-066；插入位置陷阱為 FR-064「拔標記必紅」可成立之前提。
- **Alternatives considered**: 型別併入 `Api.SystemManage`（與 upstream 同名型衝突、002 形不適用於 CRUD 面，棄）；wrapper 入 barrel（barrel 屬 upstream 既有檔、入名單外，棄）；不帶 `fetchGetAllRoles` wrapper（role 域 wrapper 面不完整、後續 007 使用者頁接真時仍須補，承 rev5 帶入；棄）。★新 wrapper 之 `fetchGetAllRoles` 本刀零消費者（使用者頁抽屜續用 upstream barrel 同名函式；使用者域刀接真時改用或刪除）——此事於本條記載、不入 ADR-00045（該 ADR 只承載 CDP 可觀察之已知態）。

## R15 憲法 Amendment 字面要點（ADR-00042 起草依據）

- **Decision**: 島 H 以 rev5 v1.7.0 字面為底（取證：H2～H5 與常數行 v1.7.0→v1.10.0 逐字不變、只序言與 H1 括號於 rev5 v1.8.0 回填授權治理兌現句——不取）。rev6 對前代字面之差異**逐項申報**（序言以短句申報、細目住 ADR-00042 決定三附表）：①**增補**＝H3 受保護選單 MUST NOT 可停用、MUST NOT 變更其父選單（R1-Q5／R2-Q1）；H2 補「同步失敗 MUST 保留上一份已知良好判定面、耗盡窗為本條唯一已知降級窗」（見下）②**明文化**（前代 as-built 入條文）＝H3 常量父鏈之寫端列舉（改父、設為常量、復原常量標的＝`rev5:ADR 0051`；清除自身常量性而後代存常量者＝clarify Q1）、H4 兩域消費面補列（治理域＋按鈕碼絕版判定、顯示域＋頁面下拉＝spec FR-022）、H5 守門補常量標的之父鏈重驗（`rev5:ADR 0051`）③**座標改寫**＝序言出處改 `rev5:ADR 0048`、G 位與兩島對偶句（島 G 未入憲、凍結位指 ADR-00043／ADR-00044）、H1 終態成員句寫成描述形＋現在式條件句（「授權治理之選單維／按鈕維寫端與授權回收桶復原之該兩維分支——該等端點不存在期間本條 vacuous 成立；端點落地即入域、零修憲」；端點維不入域）、H1 之「deleteRole 家族（rev5 新增域成員）」改「角色刪除家族」、H2 措辭中文化（buttons 聯集→按鈕碼聯集、in-memory 面→記憶體判定面）、H3 刪「（rev5 專屬新條）」、H4「授權列 v1 錨」去版本號。H3 無「反轉＝MAJOR」尾句之原形保留、MAJOR 射程由 ADR 後果節承載（取 `rev5:ADR 0048` 後果字面並補受保護兩腿與同步失敗方向）；常數留活書；承襲指針表 H 列尾註；MAJOR 射程句「六島」→「七島」；跨島重審結論＝跨島註不動；★**同步失敗方向入 H2 條文**（保留上一份、與島 F 之 F2 同向；機制細節由 ADR-00043 承載）。島 E 補兩句（稽核先於解鎖標記、標記寫入失敗回 `5000` 可重試且重試多記之稽核列明文接受；上下文缺席拒寫 `5000`、不以佔位補列；前代位置＝rev5 v1.10.0 島 J5）。§III.2 (ii) 列逐字擬稿於 ADR-00042 款五（紀律欄明文兩顆授權彈窗與 `shared.ts` 不入、兩語鍵集相等、`route:` 零新增、路由產物零變動；範圍欄：六支 view／元件檔寫「修改型＋新增型、處數與塊數 Amendment 時不預估、實數以標記為準」，兩語 locale 各 4 塊與 `app.d.ts` 4 塊為 rev5 as-built 預估）。BL-00118／BL-00119 兩句改寫（前者連帶活書 08 §8.4 之對應引文同批改）。Amendment log 條目與 `Last Amended` 之規格寫入 ADR-00042 款七。★ADR-00034 翻案觸發器曾預告「使用者管理頁刀之解鎖按鈕＝本軌道新用途 (ii)」——本刀佔用 (ii) 後該序號預測失準；ADR-00034 為 accepted body 不可改，於 ADR-00042 背景註一句（解鎖按鈕屆時取下一個可用用途號）。
- **Rationale**: brainstorm §3 §2、工程判斷 40；v1.7.0 為底使 rev6 不預先吸收授權治理刀之 reason gate 五值兌現句；差異逐項申報使 user 親決時看得到全部改字。同步失敗方向入條文之理由＝若只留 ADR，H2 之絕對 MUST NOT 與 ADR-00043 明記之耗盡窗殘留繼承互相矛盾（下位 ADR 宣告可違上位條文＝權威鏈倒掛），且「保留上一份」方向無 MAJOR 保護（前代於島 G1 入憲並附 MAJOR、rev6 島 G 未入憲）；ADR-00042 之「只收有機器證之行為」前提已由 ADR-00043 決定 10 之失敗注入案滿足。
- **Alternatives considered**: 取 v1.10.0 終態字面（帶入本刀不存在之五值與授權治理兌現句＝憲法宣告無機器證行為，棄）；同步失敗方向只留 ADR-00043（工程判斷 40 列為可選強化；棄＝理由見 Rationale）；序言逐項列舉全部差異（條文冗長、細目與出處宜住 ADR，棄——序言只短句申報三類）。

## R16 ADR 六支配號與親決時點

- **Decision**: ADR-00042（①Amendment）／ADR-00043（②判定面同步）／ADR-00044（③選單域與角色刪除之域行為）／ADR-00045（④本刀已知態與 by-design）／ADR-00046（⑤IP 域已知態、supersede ADR-00040）／ADR-00047（⑥部分更新語意、supersede ADR-00015），plan 期全數 `proposed` 落本分支；草稿期 `supersedes: []`（GT-04：一宣告即要求被翻案者為 superseded）、accepted 那一顆同批補 `supersedes` 並改舊 ADR `status`。親決：U0 兩顆（Amendment 顆＝憲法＋ADR-00042＋README 憲法版本鏡像＋活書 08 §8.4 引文改字＋generate；施工前提顆＝ADR-00043／ADR-00044／ADR-00047）；ADR-00045／ADR-00046 留草稿至治理單元（排在 CDP 三方對照單元之後；ADR-00045 各款於 CDP 實際觀察後定稿）。★施工前提顆同批（FR-076）：以 `python3 tools/docsync errata ADR-00015` 現算之現在式面引用逐處改指 ADR-00047 對應款——活書 08 frontmatter 之「API 慣例」藍本值與 §8.2 部分更新三態句（依 FR-076 改述 ADR-00047 兩域語意）、`handler/system_settings.rs` 8 處 doc 引用（只改註；子庫 commit→外層 pin bump，與該顆外層 commit 同顆、兩段式）；史料面與 accepted body 不動。ADR-00046 accepted 時同形處置 ADR-00040 之現在式引用（R13④）。
- **Rationale**: 配號＝現行最大號 ADR-00041 之後接續；取證：本機保留分支 `rebase260923-005-role-menu-crud` 曾以同號（00042～00046）落首輪草稿、從未進入 default 或本分支——該分支為 user 保留之本機對照、不入帳，GT-04 撞號比對面（工作樹與 HEAD）零衝突；帳面號序連續性優先。
- **Alternatives considered**: 自 ADR-00047 起配號以避開首輪分支同號（帳面留五號空洞、且首輪分支不會合入，棄）；ADR-00045／ADR-00046 亦於 U0 親決（內容須 as-built 後才定、提前 accepted 即須翻案，棄）；U0 只改指針、兩域語意改述延到治理單元（違 FR-076「同批」明文，棄）。

## R17 as-built 改寫義務與措辭決定

- **Decision**: 各單元收尾以 `python3 tools/docsync errata <詞>` 對四形種子（名稱／「隨…進場」「待 005」形／facade 與 handler 名冊／舊數量詞）枚舉、改完復掃；取證已知命中面約 95 處（碼註：`enforce.rs`／`main.rs`／`state.rs` 終態句、`sys_role.rs`／`sys_menu.rs` 檔頭與測試支數、`facade/mod.rs` 名冊、`test_kit.rs` 收窄集句、`model/audit.rs` 寫入時機句與 `entity_table` 列舉、`sys_operation_log.rs` 寫入者、`obs.rs` 宣告面、`envelope.rs` 唯一生產者、`router.rs`／`contract.rs` 之「二十二」、`handler/{mod,common,ip_rule,throttle}.rs` 之重評預告與「兩域」、`handler/throttle.rs` 檔頭「憲法面此刻無對應條文…隨稽核域行為島進場時回填」句〔Amendment 落地後改現在式、指向憲法 §I.7 島 E 末兩點〕、`route.rs` 常量回 `[]`、`wire_i64_guard_lint.rs` 未來式句、`main.rs` 載入告警報出點案 doc「五種」〔BL-00082 新變體後改六種〕、`tests/common/mod.rs` 守衛名冊與「現行六支」段〔名單、六回、四支純源碼掃描 lint crate、×6〕＋`tests/contract.rs` 檔頭「每輪跑六回」與真基礎設施段首註〔現行六支、六回、四支、×6〕——隨兩支新 lint crate 落地改八支、八回、六支、×8、名單補 `authz_entrypoint_lint`／`test_module_tail_lint`；外層：活書 04／05／06／08（§8.2 部分更新三態句已於 U0 改述、治理單元只復掃；§8.4 之「新增型圈界數」引文隨 Amendment 同批改）／10／11／12、RUNBOOK §9c／§11／§12／§13／§16.1／§16.2、`schema-definition.md`、`trust-model-config.md`、`code-gate-contracts.md` §1、`deploy/trust-model.dev.toml`、`rules.yml`、`walkthrough-baseline.py`、`test_references.py`、BACKLOG 三條改條文）。措辭：①詞彙表新條目寫「casbin 判定面」與「判定面同步」（「判定面」一詞既用於 IP 規則集與節流面，限定詞避免撞義）②活書 04／08 §8.3「寫後全量重載（憲法 §I.1／§I.2）」改寫時一併去掉錯誤出處歸屬（憲法原文零命中該語）③活書 12「降級（基礎設施）三支」不因 `casbin_reload_total` 而改——ADR-00043 定性該計數為**同步結果計數**、非降級序列（其 retry／exhausted 由既有 `obs016-casbin-reload-anomaly` 承告警）④`deploy/trust-model.dev.toml`「T013 的二態走查」屬 004 走查史述、改為不綁態數之描述（避免與三態並存）。
- **Rationale**: RL-0011／FR-077；詞彙定性影響活書 12 是否成假述。
- **Alternatives considered**: `casbin_reload_total` 入降級序列（retry 為可自癒之重試、非基礎設施降級，混入即稀釋降級語意，棄）。

## R18 執行單元切分（tasks 定稿之骨；派發真源＝tasks.md）

- **Decision**: U0 ★主線（兩顆親決 commit：Amendment 顆＋施工前提顆〔含 ADR-00015 現在式引用改指〕）→ U1 骨架（兩 handler 空殼、router +17＋`ROUTES_COUNT` 39＋外層 `test_references.py` 同批、contract 登記表 +17 case 佔位驗 Policy 保護與 `8888`）→ U2 004 域連帶（分頁規則＋`page_or_all`〔名冊恰 0 處〕＋IP 規則清單改引＋缺席／逾界案、`facade/mod.rs` 三件＋BL-00096 三檔、BL-00082）→ U3 測試基建（五守衛＋組合守衛＋tests 側計畫＋號段表＋BL-00110；★tasks 期重排至域鎖之前：歸檔 fn 必經 `nextval`、rollback 不回捲序列，域鎖單元之真 DB 案須有守衛才能還原序列）→ U4 域鎖底座＋歸檔寫入面＋reason gate → U5 判定面同步＋三道名冊守恆 lint（空冊）＋判定呼叫收斂腿＋obs 預註冊＋rules.yml 註＋終態句改寫 → U6 讀端六支（getRoleList／getAllRoles／getMenuList/v2〔`page_or_all` 名冊轉恰一處〕／getDeletedMenus／getMenuTree／getAllPages；零新拒因鍵；＋讀面共用三件 `db_status_to_wire`／`wire_two_value_to_db`／`blank_to_none`＝FR-074 首次出現即落）→ U7 角色寫端＋roleHome 讀寫兩支（BL-00113 重評＋泛型 `tristate<T>`＋`biz.role.*` 10 鍵與三檔 locale 同單元〔`notFound` 首發於 getRoleHome／updateRole〕＋同步接線 role 半〔`RELOAD_CALL_FILES` 擴 `handler/role.rs`〕）→ U8 選單寫端 add／update（守門序、href／buttons、受保護兩腿、常量父鏈、絕版歸檔＋同步接線 menu 半〔擴 `handler/menu.rs`〕）→ U9 選單 delete／batch／restore（回收桶；剩餘 `biz.menu.*` 鍵隨首發單元）→ U10 零繼承端到端＋交錯時序＋序列化域機器證逐寫端 → U11 wire 面（受審名冊、表驅動鍵集、`PageRes`、首屏真串、BL-00109 腿）→ U12 前端 role 頁＋共用表頭 prop → U13 前端 menu 頁＋ip-rule 頁 → U14 收刀前承載體檢（BL-00106／BL-00107／BL-00111／BL-00123／BL-00115）→ U15 走查還原工具擴面＋RUNBOOK §9c → U16 CDP 三方對照（含 ADR-00045 各款「觀察路徑→症狀」實測、新發現已知態併入草稿）→ U17 治理面＋全量閘（活書、RUNBOOK、reference-src、dev toml〔改後先重建容器〕、ADR-00045／ADR-00046 親決 accepted＋ADR-00040 現在式引用改指、BACKLOG 三條改條文、as-built 復掃、容器內全量測試與全部閘）→ final holistic review → finishing → 收刀簿記。高風險共享檔序列鏈：`router.rs`／`tests/contract.rs`（U1 後逐單元加案）、`error.rs`＋三檔 locale＋`app.d.ts`（U7～U9 隨首發單元分批）、`facade/{sys_menu,sys_role,sys_casbin_archive,mod}.rs`、`handler/{role,menu,common}.rs`、`envelope.rs`（U2；U6 改名冊期望）、`sys_ip_rule.rs`＋`ipgate/mod.rs`＋`handler/ip_rule.rs`（U2；`handler/ip_rule.rs` 另於 U7／U8 改其 degraded 射程測）——同檔單元不並發。
- **Rationale**: brainstorm §9 骨架依相依重排；全部施工單元皆排在 U0 兩顆之後（施工前提顆為硬閘）；零 base-web 既有檔改動之單元（U1～U6、U10、U11、U14、U15）只受施工前提顆之閘，U7～U9 之 locale 半與前端 U12／U13 另受 Amendment 顆之 base-web 硬閘（U0 在序列上先於一切、實際不生額外等待）；getRoleHome 併入角色寫端單元使讀端單元零新拒因鍵、不觸 locale；CDP 排在治理單元之前，使 ADR-00045 於觀察定稿後才 accepted（accepted 後 body 不可變）。
- **Alternatives considered**: 原序 U3 域鎖→U4 判定面→U5 測試基建（plan 期原案；歸檔 fn 必經 `nextval`、rollback 不回捲序列，域鎖單元之真 DB 案無守衛可還原序列＝SC-014 走查基準 diff 與 schema-gate 首日即紅；tasks 期改測試基建前移，棄）；role／menu 寫端各拆 facade 與 handler 兩單元（單元數逼近 25、每單元都要跨檔一致性審查，併為依端點群切）；locale 鍵集中一單元（撞 msg-key-gate 與名冊雙向閘夾擊＝工程判斷 24，棄）；讀端單元即落 `biz.role.notFound`＋三檔 locale（讀端單元即受 base-web 硬閘、且角色域鍵分散兩單元，棄）；CDP 後另立「ADR-00045 親決」主線步驟、治理單元仍在 CDP 前（治理單元與 CDP 之活書已知態列須二次改，棄）。

## R19 RL-0013 棄案反例回跑（對所選方案跑同一反例）

| 棄案 | 棄因（反例） | 對所選方案回跑 |
|---|---|---|
| RELOAD_SERIAL 入 AppState（R7） | 觸 ADR-00036 封條 | 函式內 static：多實例 AppState（測試建多個 state）共用同一把鎖 → 序列化跨 state 仍成立、測試並發（serial 執行）無死鎖；**成立** |
| 判定面 lint 切到首個 `#[cfg(test)]`（R12） | 漏 `state.rs` 門控後生產碼 | 扣除測試模組區塊：`state.rs` item 級 `impl JwtConfig` 計入生產面、不含受守 token → 不誤紅；`enforce.rs` 家檔豁免；第二測試模組後之生產項亦被掃到；**成立** |
| `parentId` 出現即改父（R9） | 受保護列 UI 編輯全被拒 | 同值即無變更：受保護列同值送回 → 放行；改值 → `protectedMenu`；孤兒列同值 → 放行、改值 → 父驗證；**成立** |
| 全取以哨兵值入通用 helper（R8） | 無名可守 | 明名入口：壞形 → 兩欄 None → `page_or_all` → All（全取）；`size=0` → `Page(1..)` clamp 成 1；**成立**（與 R1-Q4b 邊界三句逐一對上） |
| facade 保留 size clamp（R8） | 全取被截 | 移除 facade clamp 後，通則端點之 size 上界由 `page_params` 保證、facade 只收 clamp 後值；**成立** |
| `buttons:[]` 正規化 NULL（R9） | 增 CDP 差 | 保留原值：絕版計算把 `[]`／NULL 同視空集 → 清空按鈕碼（送 `[]` 或 null）皆令舊碼全數視為移除 → 僅絕版者歸檔；**成立** |
| ADR 自 00047 起配（R16） | 帳面空洞 | 自 00042 起：GT-04／GT-05 比對面（工作樹、HEAD、tracked）不含首輪分支 → 零衝突；**成立** |
| `casbin_rule` 亦顯式大 id（R11） | 判定面不持有 | 真新增政策路徑取 nextval：守衛以帶界水位（`id < 9_300_000_000`）與 arm 時現讀序列還原 → 走查植入之顯式大 id 殘列與 nextval 殘列皆於 Drop 被清、不撞 PK；**成立** |
| 同步失敗方向只留 ADR-00043（R15） | H2 絕對句與耗盡窗殘留互相矛盾、方向無 MAJOR 保護 | 方向入 H2：一句「同步失敗 MUST 保留上一份…耗盡窗為本條唯一已知降級窗」即消矛盾、條文仍短、機制細節續住 ADR；**成立** |
| 讀端單元即落 `biz.role.notFound`（R18） | 讀端單元受 base-web 硬閘 | getRoleHome 併入角色寫端單元：讀端六支零新鍵 → msg-key-gate 與名冊雙向閘皆不觸；角色域 10 鍵同單元首發；**成立** |
| 原序「域鎖→判定面→測試基建」（R18） | 域鎖單元真 DB 案序列漂移、無守衛可還原 | 測試基建前移：U3 自證以自身守衛還原；U3 只依賴既有件（`enforce_role_path_method`、`state.enforcer`、m0001 既有之歸檔表 schema）、不反依賴 U4／U5；U4 真 DB 案掛 U3 守衛、序列回位；**成立** |
| locale 塊插在 `form` 末項後（R14） | 零鑑別 | 插在非末項之間：塊內零移除行 → 純新增塊 → 拔標記即被 `find_unmarked_additions` 報出；**成立**（實作時以變異自證複核） |

## R20 交 tasks 與實作期定值之事項（非 NEEDS CLARIFICATION）

- 角色清單與已刪選單清單之首屏真串字面（容器內 qs 實跑）；`components.d.ts` 重算之實際兩行字面；用途 (ii) 新增型塊實數（前端單元出口逐檔斷言等於預估，不等即停手升級主線、由 user 定當刀 PATCH 或比照 BL-00118 滯後）。
- ADR-00045 各款之「觀察路徑→症狀」以 CDP 實際操作定稿（policy-archive 死項之症狀若與 BL-00045 描述不符、以 errata 改條文）。
- `arch_impact` 以收刀時 `git diff --stat <merge-base>..HEAD -- docs/arc42/` 現算。
- 淨流量：兩前提下 005 收刀 rolling-3＝13（工程判斷 41），收刀事件 notes 記揭露型／新欠型分型。
- Technical Context 零 NEEDS CLARIFICATION。
