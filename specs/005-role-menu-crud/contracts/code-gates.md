# Contract — 機器守、治理面與帳本（005）

> 本檔凍結本刀新增或擴充之機器守判準、名冊守恆、測試基建與走查工具契約、ADR 與帳本兌現面。判準細節之理由見 research R8／R10～R12／R16～R17；wire 端點行為見兩支 wire 契約。

## §1 fork-delta：★BASE-WEB-MANAGE-PAGE-WIRING 用途 (ii)

- **檔級硬邊界恰九檔**：`src/views/manage/role/index.vue`／`src/views/manage/role/modules/role-operate-drawer.vue`／`src/views/manage/role/modules/role-search.vue`／`src/views/manage/menu/index.vue`／`src/views/manage/menu/modules/menu-operate-modal.vue`／`src/components/advanced/table-header-operation.vue`（六支，修改型＋新增型：語意改動逐行 `原行:`、純新增段走新增型圈界；處數與塊數 Amendment 時不預估、實數以標記為準）／`src/locales/langs/{en-us,zh-cn}.ts`／`src/typings/app.d.ts`（三支新增型圈界）。
- **明文不入**：`role/modules/menu-auth-modal.vue`／`role/modules/button-auth-modal.vue`（本刀出現任何 diff＝紅；前端單元出口斷言 `git -C base-web diff <基線>..HEAD -- <兩檔>` 零輸出）；`menu/modules/shared.ts`（兩向 diff 零改）。
- **範圍欄預估**（Amendment 時零標記、以 rev5 as-built 為預估；憲法表外宣告 1「實數以標記為準」）：兩語 locale 各 4 塊、`app.d.ts` 4 塊（僅此三支新增型檔有預估）；前端單元出口只對此三檔以 grep 逐檔斷言新增型塊數＝預估，不等即停手升級主線（user 定當刀 PATCH 或比照 BL-00118 滯後）；六支 view／元件檔之處數與塊數依表外宣告 1 以標記實數為準、於下次 Amendment 實數化（比照 BL-00118）。
- **名冊載入變異自證**（首個動 base-web 之單元順做）：暫把新列範圍欄任一反引號路徑之**反引號內**字面改為不含 `/` 之非路徑 token（例 `role-index`；觸發 `load_roster` 路徑形斷言 die）→ `tools/fork-delta-lint.py` 當場紅 → 還原（RL-0005 回基準態）；拔反引號形於用途 (ii) 標記出現前恆綠、不得作自證。
- **各新增圈界塊「拔標記必紅」**：逐塊拔 START／END → lint 必報未圈界新增 → 還原。★插入位置不得落在物件最末項之後（research R14）。
- **生成檔**：`src/typings/components.d.ts` 以 unplugin 重算、`git -C base-web diff` 只准出現 `NTreeSelect` 兩行增列（介面內一行、全域 const 區一行）、其餘任何差異即紅；重算檔與彈窗同 commit；路由外掛產物四檔零變動（`tools/route-artifact-gate.py` 冪等綠）。
- **ip-rule 頁**（rev6 新檔、免授權）：模板靜態斷言 `TableHeaderOperation` 帶 `:show-add="hasAuth('ipRule:add')"` 與 `:show-delete="false"`、不再覆寫 `#default` 插槽。

## §2 新 lint 兩支

### 2.1 `rust-api/server/tests/authz_entrypoint_lint.rs`（`mod common;`；行掃描＋`strip_comments_and_literals` 視圖）

- **生產面**（腿①～③）＝各 `src/**/*.rs` 扣除「行首 `#[cfg(test)]` 其後緊接行首 `mod <名> {`（可帶可見性前綴）至下一個行首 `}`」之測試模組區塊後之全文；item 級 `#[cfg(test)]` 項保守計入生產面；整檔以測試門控閘入之模組（由 `#[cfg(test)]` 其後可帶 `pub`／`pub(crate)` 等可見性前綴之 `mod <名>;` 宣告現算——現樹唯一實例＝`model/facade/mod.rs` 之 `pub(crate) mod test_kit;`，形同 `obs.rs` 之 `cfg_test_mod_decl_names`）與 `tests/` 樹豁免、豁免集自我對賬（宣告處存在且所指檔存在）。
- **①同步呼叫點名冊**：生產面含 `reload_enforcer` 使用點（`reload_enforcer(`／`(reload_enforcer)`／`::reload_enforcer` 三形聯集、RL-0026；扣定義處）之檔集＝`RELOAD_CALL_FILES`（判定面同步單元落地時空冊；角色寫端單元擴 `handler/role.rs`、選單寫端單元擴 `handler/menu.rs`；家檔 `auth/enforce.rs` 豁免）。
- **②判定面寫鎖名冊**：生產面含 `.enforcer.write()` 取得形之檔集＝`ENFORCER_WRITE_FILES`＝空冊（家檔豁免）。
- **③重載與建構 token**：生產面 `load_policy`／`Enforcer::new` 只許出現於家檔。
- **④判定呼叫收斂**（承 `rev5:B-044` 之 `ALLOWED_DECISION_FILES` 形）：strip 後之 casbin 判定呼叫形——完整 token `enforce`／`enforce_with_context`／`enforce_mut`／`enforce_ex`（後隨非識別字元；`enforce_role_path_method`／`enforce_mw`／`enforcer` 等更長識別字由 token 完整性排除）、前導限定符 `.` 或 `::`（容空白換行）、後隨 `(` 或 `::<`——之檔集＝{`auth/enforce.rs`}（集合恰等）；模組路徑 `auth::enforce::…`（後隨 `::識別字`、非呼叫形）與 `use casbin::…` 不命中；射程承前代＝src 全樹**連測試模組**（現樹唯一命中＝家檔一處、首日零誤紅）；casbin 升版 MUST 重核後綴表。
- 各腿植入反例變異自證（於臨時複本植入違規形 → 腿必紅；④另含植入 `.enforce_ex(`／`CoreApi::enforce(` 必紅、植入 `enforce_role_path_method(` 不紅、現樹合法形反向自證）；「改寫為對現役判定面就地 `load_policy`」必轉紅之負向自證住 `auth/enforce.rs` 測試（以 seam 面操作、明文步驟註解）。

### 2.2 `rust-api/server/tests/test_module_tail_lint.rs`（BL-00111 ①②；`mod common;`；行掃描）

- **判準①射程**＝(a) BL-00111 條文 grep 判準（`split("\\n#\[cfg(test)\]")\|find("\\n#\[cfg(test)\]")\|split_once(TEST_MODULE_MARKER)`）現算之切面腿所在檔 ∪ (b) 跨檔腿名冊字面所指之被切檔（於 (a) 之檔內以 `("<name>.rs"` 形抽取、以所在檔目錄為基準解析〔`include_str!` 語意〕、逐一解析存在性）；兩集合自我對賬（抽不到或解析不到即紅）。現況 (a)＝九檔、(b) 於 FR-074 擴射程後納 `handler/role.rs`／`handler/menu.rs`。★(a) 之 grep 與 (b) 之抽取皆於原文（或 Keep 視圖）執行——兩者之字面皆在字串常值內、Drop 視圖下兩集合皆空；只有判準①之 item 掃描用 Drop 視圖。
- **判準①**：首個行首 `#[cfg(test)]` 之後，每個 column-0 item 之屬性鏈 MUST 含 `#[cfg(test)]`；item 頭形 regex 涵蓋可見性前綴（`pub`／`pub(crate)`／`pub(super)`／`pub(in …)`）與修飾詞（`async`／`const`／`unsafe`／`extern`）及 `fn`／`struct`／`enum`／`impl`／`trait`／`type`／`const`／`static`／`mod`／`use`／`macro_rules!`。
- **判準②**（**射程獨立＝src 全樹**；生產面同 §2.1 之定義）：零 `obs::` 出口之 item 別名匯入——樣式涵蓋 `use (crate|server|super…)::obs::<ident> as <ident>` 與分組 `obs::{ … <ident> as <ident> … }`（含跨行）。★若沿判準①之射程即漏 `ipgate_blocked` 唯一生產呼叫檔 `middleware/mod.rs` 與 bin crate 之 `server::obs::` 形＝BL-00111 假結案。
- **變異自證六形**：item 級門控不紅、第二測試模組不紅、字串常值內行首碼不紅、植入 `pub(super) fn` 於切點後必紅、植入別名匯入必紅、於 `middleware/mod.rs` 植別名匯入必紅。既有十二支腿 docstring 補指本腿為其射程守。

## §3 既有 lint 與名冊擴充

| 對象 | 擴充 |
|---|---|
| `tests/wire_i64_guard_lint.rs`（BL-00106／BL-00107） | ①泛型 wire 型名冊（`Res`／`PageRes`）＝樹上泛型 `Serialize` 型集合（恰等）＋實例化掃描②手寫 `impl Serialize` 絆線③`derive(Serialize)` 錨數＝解析成功數（兼抓巨集生成型）；各附變異自證；檔頭兩段改寫 |
| `handler/common.rs::each_domain_keeps_its_own_log_literals` | 名冊加兩列五元組（file／src／refusal tokens／fallback_arg／fallback_const）：`role.rs`（target `security.role`、`refused`、`uid`、拒寫訊息）、`menu.rs`（target `security.menu` 同形）；兩新檔須有行首 `fn operator_from(`、拒寫腿以 `AppError::Internal` 收尾；★寫端 body 取用一律以 `common::json_or_default(` 限定路徑形呼叫（生產區至少一處，否則本案掃描面空集 panic）並餵本域專屬收斂訊息（角色／選單各一句、不得與既有兩域同字），擇一形：①行首 `const BODY_FALLBACK_MSG: &str = "…"`（fallback_arg 填常數名、fallback_const 填〔行首錨, 字面〕＝ip_rule 形）②呼叫點內聯字面（fallback_arg 填該字面、fallback_const 為 None＝throttle 形）；五欄同批填齊 |
| `handler/ip_rule.rs::production_code_emits_no_degraded_field` | 射程加 `role.rs`／`menu.rs`（錨＝行首 `fn operator_from(`） |
| `error.rs` 名冊兩測 | `msg_keys_roster_is_pinned_and_unique` 逐字釘 43 鍵、`biz_keys_are_in_roster` 加 24 支常數 |
| `envelope.rs::no_wire_literal_lives_in_envelope_production_code` | 正面錨不動（分頁常數與 helper 置於 `serialize_opt_i64_number_guarded` 之前）；新增 `page_or_all` 名冊案：生產面＝逐檔扣除每個行首測試模組區塊（同 `obs.rs` 之 `production_part` 形、整檔測試模組現算豁免；不採「切到首個行首 `#[cfg(test)]`」）；計數＝`page_or_all(`／`(page_or_all)`／`::page_or_all` 三形聯集、扣定義處；分期＝分頁規則單元落地時恰 0 處、讀端單元接線後恰一處且在 `handler/menu.rs`；變異自證含「於 `auth/enforce.rs` item 級門控之後植一處呼叫必紅」 |
| `router.rs`／`tests/contract.rs`／外層 `tools/docsync/tests/test_references.py` | ROUTES 22→39、`ROUTES_COUNT` 同 commit bump；contract case 集＝ROUTES（39＝39、雙向覆蓋閘）；外層兩份釘值清單各 +17 列（同顆外層 commit、收尾跑 `python3 tools/docsync test`） |
| `obs.rs` | `pre_register_metrics` 補 `casbin_reload_total{outcome=ok|retry|exhausted}` 顯式零＋「樣本行恰三」上界守；`IP_DOMAIN_DEGRADED_SOURCES` 恰八不動 |
| `model/audit.rs` | 零新 variant 之既有釘不動（`EXPECTED_LITERALS` 五詞） |

## §4 wire 裁判面

- 受審名冊＝本刀新增全部 wire 型（實數以抽取為準）＋`Api.Common.PaginatingQueryRecord`；getAllRoles 之 DTO 另對 `Api.SystemManage.AllRole`、`MenuTreeRecord` 另對 `Api.SystemManage.MenuTree`。
- 表驅動「序列化鍵集＝快照 properties 鍵集」涵蓋全部受審讀型（既有七型＋本刀新讀型＋分頁信封）；`Api.Route.MenuRoute` 具名豁免（交叉型佔位、只裁 `id` 必填）。
- 首屏真串抽取案：`getRoleList`／`getDeletedMenus`（頁面首屏物件經 qs 6.15.1 容器內實跑之字面）、`getRoleHome`（wrapper `{id}` 經序列化器產出）、getMenuList/v2 無參形；壞形收斂案逐 query 型各一。
- **BL-00109 腿**（`tools/wire-schema.py`）：純讀檔斷言 `base-web/packages/axios/src/options.ts` 之 `paramsSerializer` 為無選項 `stringify(params)` 且 `base-web/packages/axios/package.json` 之 qs 為 `6.15.1`；位於 `cmd_check` 合成 self-test 之後、staged-gate 短路與容器探測之前、無條件執行；self-test 另釘「staged-gate 判跳過時本腿仍執行」；不擴收窄 pathspec、不動 pre-commit submodule-sync 段。已知邊界（工作樹改 axios 設定未 commit）記 RUNBOOK §12 該列；行為契約入 `docs/ops/reference-src/code-gate-contracts.md` §1。

## §5 測試基建

- src 側 `test_kit.rs`：`RoleRowsGuard`／`MenuRowsGuard`／`CasbinRuleRowsGuard`／`PolicyArchiveRowsGuard`／`UserRoleRowsGuard`＋組合守衛（Drop 序：指派→歸檔→授權→選單→角色）；水位一律＝`COALESCE(max(id) FILTER (WHERE id < 9_300_000_000), 0)`（界值＝`SYNTHETIC_UID_FLOOR`、五表同套）＋序列 `(last_value, is_called)`，皆 arm 現讀；Drop 刪 `id >` 水位（號段內顯式大 id 列恆被清＝LL-00017 守法）再 setval 回現讀值；指派守衛刪除集＝arm 快照鍵集差 ∪ `role_id >` 角色守衛水位者、先於角色列；自證測（含清理序反腿必撞 FK RESTRICT；arm 前預置號段內殘角色列＋其指派列時 API 造列仍於 Drop 被清、序列回位、FK 不擋）。
- tests 側 `tests/common`：同族 `RestorePlan` 計畫＋純資料釘；contract 真 seed 面之 24 鍵發射段各掛所需守衛。
- 造列號段：`test_kit.rs` 單一常數表依「表×檔」登記、防跨檔撞號（含 tests 側檔列，如 `tests/contract.rs` 之角色／選單／指派號段）；tests 側以同值字面自持其號段常數，並於 tests/common 純資料段以 `include_str!` 讀 `src/model/facade/test_kit.rs`、斷言自持值與表中對應列逐字相等（登記處唯一、漂移即紅）；`casbin_rule` 經真判定面新增政策路徑取 nextval。
- BL-00110：7777 腿 denylist 鍵改 `RestorePlan.keys` 腿 RAII。
- BL-00123：請求上下文缺席之每請求總數案（至少打一支角色或選單寫端、釘「其餘端點 2 格」）。
- BL-00115：dev 信任模型對賬三態（`APP_TRUST_MODEL_PATH` 缺席＝具名跳過；在而讀檔失敗＝紅、訊息附 RUNBOOK §2 重建命令；讀得到＝逐欄比對 `dev_trust_model()`）；改 `deploy/trust-model.dev.toml`（含純註解）之單元 MUST 先重建 rust-api 容器再跑容器測試。

## §6 走查工具擴面（`tools/walkthrough-baseline.py`）

- restore 面加 `sys_role`／`sys_menu`／`casbin_rule`（刪 `id >` snapshot 上界列＋setval 回 snapshot 現讀值）與 `sys_casbin_policy_archive`（依水位刪＋setval）；`sys_user_role` 以 snapshot 鍵集差刪除（先於角色列）；seed 有列之表不套「列數非 0 即拒」與 DELETE 全表形。
- 動過 `casbin_rule` 之 restore 後輸出「MUST 重啟 rust-api」補救句（判定面無外部通知管道）；自測逐字釘住新寫面。
- RUNBOOK §9c 同批改（「五表」系列字面、重啟句）；本工具單元排在 CDP 單元之前。

## §7 觀測與告警

- `casbin_reload_total{outcome}` 三值＝**同步結果計數**（非降級序列；活書 12「降級（基礎設施）」條目不改）；`deploy/grafana-provisioning/alerting/rules.yml` 之 `obs016-casbin-reload-anomaly` 錨字面不改、註解「（島 G1）」改指島 H2＋ADR-00043；BL-00093 ② 加戳記。
- RUNBOOK §11 補選單域鎖觀測（`pg_locks` classid／objid 拆讀 64-bit key、bigint 直比恆假）與三 outcome 判讀；§13 補 exhausted 處置（查結構化 log 之 cause → 修 DB 連線 → 重啟 rust-api → 驗計數）；只寫實跑過之命令。

## §8 ADR 與帳本

- ADR 六支＝ADR-00042～ADR-00047（research R16）；草稿期 `supersedes: []`、accepted 同顆補並改舊 ADR 狀態；現在式面指向 ADR-00040／ADR-00015 之引用以 `python3 tools/docsync errata <ID>` 現算、逐處改指（史料面與 accepted body 不動）。
- 收刀 `feature_close`：`backlog_done` 19＝BL-00082／BL-00095／BL-00096／BL-00098／BL-00105／BL-00106／BL-00107／BL-00109／BL-00110／BL-00111／BL-00112／BL-00113／BL-00115／BL-00116／BL-00117／BL-00118／BL-00119／BL-00123／BL-00125；條文改寫 3＝BL-00120（只剩 ADR-00039 半）、BL-00093（② 戳記）、BL-00045（補選單管理頁曝光面）；`backlog_add` 零；`adrs` 六支；`arch_impact` 收刀時現算。
- 反向確認（收刀體檢時 grep 現算）：BL-00047 零建表／BL-00028 零新設定鍵／BL-00048 no-escalation 空殼不動／BL-00074 兩半（`FRONTEND_MSG_CONSUMERS` 仍 1 筆、pre-commit submodule-sync 段零 diff）／BL-00108 兩半（零第三份字元級解析組、`entity_behavior_lint.rs` 零 diff）／BL-00123 之新增發射腿半邊（角色／選單寫端拒寫不增計請求上下文缺席計數）。
