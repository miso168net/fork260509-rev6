---

description: "Task list for 005-role-menu-crud"
---

# Tasks: 005 role＋menu 管理 CRUD 寫端——角色與選單接真、選單域序列化、判定面同步、授權歸檔寫入面、島 H 入憲

**Input**: Design documents from `/specs/005-role-menu-crud/`

**Prerequisites**: plan.md、spec.md（US1～US6、clarify Q1～Q5；★一律讀 HEAD 版——plan 期已精修 FR-052／FR-073／FR-042＋Key Entities／FR-058＋FR-075③／★軌道登記表六檔型別，tasks 期再精修 FR-075 之 Amendment commit 範圍〔納活書 08 §8.4 引文、與 ADR-00042 決定七同字面〕）、research.md（R2 rev5 對應碼／R3 清單 A 十二項＋清單 B 二十一筆＋十一項防回歸／R5～R14 設計定值／R17 as-built 改寫義務／**R18 單元骨架**〔tasks 期依序列不回捲之取證把測試基建前移至域鎖之前〕／R20 實作期定值）、data-model.md（§2 狀態機／§3 序列化域／§4 觸發矩陣／§5 守門序／§9 守衛）、contracts 四檔（wire-role-admin／wire-menu-admin／msg-keys／code-gates）、quickstart.md；
憲法 1.4.0（ADR-00042 draft 已落、proposed）；ADR 六支 ADR-00042～ADR-00047 皆 proposed（plan 期 draft）。

**Tests**: 本 repo TDD＝CLAUDE.md §2 紀律、**非可選**——每實作 task 內先紅後綠。測試層對照（plan Testing）：*contract case*＝`rust-api/server/tests/contract.rs` registry（oneshot、`connect_lazy` 假連線；登記表鍵集＝ROUTES、雙向覆蓋閘）＋同檔真 seed app 面（`observed_msgs_real_db` 同族；24 鍵名冊雙向閘；★tests crate 取不到 src 側 `#[cfg(test)] pub(crate) mod test_kit`，該面一律用 T016 之 tests 側守衛）；*integration*＝各模組 `#[cfg(test)]` 真 DB 案（★U3 起五表守衛就位、其後一切寫庫案皆掛守衛——`nextval` 不隨 rollback 回捲，「交易內植列＋rollback」擋不住序列漂移〔`IpRuleRowsGuard` doc 同理〕；U5 之判定面案零寫庫）；*lint*＝`tests/*_lint.rs` 源碼掃描＋植入反例變異自證；*工具*＝python 工具自帶 `test` 子命令。
★base-web 側**零測試框架** ⇒ 凡 `base-web/**` 之 task 先紅後綠不適用、把關＝`pnpm typecheck`＋`tools/fork-delta-lint.py` rc 0＋單元出口機器斷言（兩彈窗零 diff、`components.d.ts` 只兩行、(ii) 新增型塊數、拔標記必紅、模板靜態斷言）＋兩段 review＋CDP 三方對照（SC-011）；混合單元之 review prompt「勿誤報」段列入「base-web task 無紅綠腿不算缺陷」。

**Organization**: 依 research R18 單元骨架之**執行序**分 phase——每 phase 標其主 user story、task 逐條帶實際所屬 story 標籤（一單元可服務多 story；★US 的「獨立可驗收」成立於交付面、不成立於單元併發面：`router.rs`／`contract.rs`／`error.rs`＋i18n 四處／`facade/sys_menu.rs` 等共用檔逐單元遞進）。US4 之同步機制本體（U5）與 US6 之 004 域連帶（U2）因阻塞後續寫端而入 Foundational；US5（P3）併入角色寫端單元（getRoleHome 首發 `biz.role.notFound`＝R18 定案）。★R18 原序之「U3 域鎖→U4 判定面→U5 測試基建」於 tasks 期重排為 **U3 測試基建→U4 域鎖與歸檔→U5 判定面同步**（歸檔 fn 必經 `nextval`、U4 案需守衛才能還原序列；後續單元編號不變）。**執行單元對映**（文末）為 Workflow 派發粒度；每單元一顆外層 commit（例外：U0 兩顆；U17 分三段落地＝T093 主線 ADR 顆、T094～T099 治理顆、T100～T103 收攏顆；單元收尾六步序＝CLAUDE.md §2）；T 編號＝執行序。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 檔域不相交、可分派給同單元內不同 implementer；★僅指「可分派」——**cargo 執行一律序列**（容器內 `--test-threads=1`）。
- **[Story]**: US1～US6；Setup／Foundational／Polish 不掛。
- **★主線任務**：主線親做（含 user 親決）、不入 agent 單元。

## 全程紀律（每 task 隱含、不逐條重複）

- ★**實作前先讀** research R2 對應之 rev5 碼（`../fork260509-rev5/{rust-api,base-web}/`＝凍結 worktree、**唯讀、絕不寫入**、派 agent 時唯讀令烤進 prompt＝RL-0064）；高度參照、**重打字消化不拷貝**、註解一律 rev6 語境重寫（rev5 出處帶 `rev5:`）；藍本取 rev5 HEAD 形並逐檔剔除 research R3 **清單 A 十二項**（`rev5:006`～`rev5:008` 增量：五值 reason gate、三維授權讀寫端、授權回收桶、`all_button_codes`、授權彈窗接真、`protected_endpoint_set`、`Identity` sid、使用者域、稽核頁、帶 degraded 欄之 `audit_operator`、`RELOAD_CALL_FILES` 之 policy_archive／user 兩列、`rev5:007` bump）；**清單 B 二十一筆**以 rev6 形為準、藍本相反處不得回帶；**十一項 rev4 防回歸**照帶（R3 末段）。
- ★**兩道硬閘**：①**施工前提閘**＝T003（ADR-00043／ADR-00044／ADR-00047 accepted）未落地前**不得啟任何施工單元**（U1～U17）②**Amendment 硬閘**＝T002（ADR-00042 accepted＋憲法 1.5.0）未落地前**不得動任何 base-web 既有檔**（含 `locales/langs/*.ts`、`app.d.ts` 之 backend 節）；純新增檔（兩支 wrapper、兩支型別檔）依 §III.2 表外宣告 3 不受此閘。U0 在序列上先於一切、兩閘實際不生額外等待。
- ★**跨子庫同步律**：`msg-key-gate`（`MSG_KEYS` 側 rust-api／三檔 locale＋`app.d.ts` 側 base-web）與 `wire-schema`（typings 側 base-web／快照側 rust-api）兩側改動 MUST 在**同一顆外層 commit** 同時 bump 兩 pin；單側先 bump＝閘紅或歷史留分叉組合。
- ★**施工約束**（取證發現、烤入 implementer／review prompt；research R5～R7）：①`ipgate/mod.rs` 整樹掃描腿禁 `.store(`／`::store(`／`.swap(`／`::swap(`／`rcu`／`compare_and_swap` 呼叫形（連測試模組零容忍）⇒ 判定面換上一律 `*guard = new;`、seam 用 `Notify`＋`std::sync::Mutex<Option<Arc<Gate>>>`、注入旗標用 `AtomicBool::fetch_or`、不得有名為 `swap` 之 fn ②`throttle/mod.rs` 整樹字面腿禁 `throttle:lock:`／`lock_ttl_secs`／`redis_lock` 等子字串 ⇒ 新識別字與註解避開 ③`RELOAD_SERIAL` 住 `reload_enforcer` 函式內 static、**不入 AppState**（ADR-00036 恰七欄封條不動）④`handler/common.rs` 新件一律 `pub(super)`、零 `tracing::debug!`（`fallback_event` 恰 1 則之守）；清單查詢抽取器（`FromRequestParts`、壞形整串收斂 default、發 `tracing::debug!`）住各 handler 檔（ip_rule 形）⑤兩新 handler 寫端 body 一律以 `common::json_or_default(` 限定路徑形呼叫、餵本域專屬收斂訊息（不得與既有兩域同字）⑥拒寫事件各域自有 target（`security.role`／`security.menu`；同步告警 `security.authz`）、帶 `refused` 欄、**零 degraded 欄、零降級計數**（R3 B15）；寫端一律先取操作者上下文、缺席＝`5000` 拒寫且**先於一切守門與提前 no-op** ⑦交易由 handler 持有：外殼 `begin` → 內層 `<op>_in_txn(&txn, …)`（入域寫端首句＝`sys_casbin_archive::enter_menu_domain(txn)`）→ commit；一切失敗腿顯式 `txn.rollback()` 後回錯（FR-045、LL-00026）；facade 寫端公開入口收 `&DatabaseTransaction`、facade 內一律不自取域鎖；★固定鎖序＝advisory → 歸檔表列 → `sys_role` 列 → `sys_menu` 列 → `casbin_rule`（FR-043／data-model §3；歸檔表列為本交易新插入列、不與他交易競爭，故 data-model §5.3「鎖標的列→守門→歸檔」之序與此不衝突）；域內寫端**零 per-user advisory 鎖取得**（ADR-00043 決定 8 前提②）⑧★判定面命中斷言一律經 T014 之 `test_kit::face_allows`（內經 `auth::enforce::enforce_role_path_method`、讀鎖於 fn 內取放）：src 任何檔（含測試模組、`test_kit.rs`）**零 `.enforce(`／`::enforce(` 直呼**（U5 腿④射程連測試模組）；測試**不得持 `state.enforcer.read()` 守衛跨寫端呼叫**（寫端 commit 後之同步取寫鎖＝同 task 永久互鎖、非終止型故障）⑨DTO 可見性：回應 DTO `pub struct`＋`pub` 欄；請求 DTO 與清單／首頁查詢抽取器 `pub struct`＋`#[derive(Debug, Default, Deserialize)]`（ip_rule 形）——供 tests crate（`wire_schema.rs`／`contract.rs`）構造與抽取；可見性放寬依 RL-0070 查掃描閘。
- rust build／test **一律容器內、全程序列**：`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1`；容器內 `cargo fmt --all --check`（碼面閘）。★改 `deploy/trust-model.dev.toml`（含純註解）之單元 MUST 先重建 rust-api 容器再跑容器測試（單檔 bind mount 換檔後懸空＝LL-00033）。
- ★**絕不 push／merge**（本清單零 push／merge 任務；收尾整合走 finishing、需 user 當次同意）；絕不 `git submodule update`；絕不 `--no-verify`；子庫 git 一律 `git -C <子庫>`、不 `cd` 進子庫。
- **兩段式 commit＋pin bump（六步序、次序不可反）**：①復核 report（逐項 grep、`python3 tools/docsync errata <詞>` 對 research R17 四形種子〔名稱／「隨…進場」「待 005」「進場時重評」形／facade 與 handler 名冊／舊數量詞〕＋本清單點名之附加種子〔`唯一生產者`、`只落`、`不搬`、`count_by_role`、`兩域`、`六款`、`對沖`〕枚舉、改完復掃）②load-bearing 自驗（容器內 rc＋`python3 tools/docsync lint`）③落帳（BACKLOG／LESSONS／tasks 勾選／ADR）④子庫 commit ⑤`git add <子庫>` → `python3 tools/docsync generate` → `git add docs/generated docs/arc42/ARCHITECTURE.md docs/ops/LESSONS.md tools/orchestration/_sk_rules.js` ⑥一顆外層 commit；★生成物一律主線動作、**不入任何 agent 允許檔案清單**；commit 訊息含反引號一律 `git commit -F <絕對路徑>`。
- ★**發射前置**：每單元定義 `<工作區>/005-uN.py`（工作區＝gitignored、不入版控）→ `python3 tools/orchestration/assemble.py <工作區>/005-uN.py <工作區>/005-uN.mjs`（三道自檢）；編排全角色 `opus[1m]` xhigh、implementer prompt 首行帶深思關鍵詞（2026-09-23 起骨架現值）；implementer／review／fix 各烤入對應 `python3 tools/docsync rules emit --scope <implementer|review|fix>` 塊（RULES-VERSION 不變＝`0bbc9765d102`）；Workflow launch 與 `python3 tools/wf-watchdog.py <token>` 雙腿看門狗同回合原子成對、token 取單元名形 `u<N>-<slug>-<4hex>`（不可取 `test`）；TDD 單元 agent 總數保險絲 ≤20 支（由同檔常數推導＋自我斷言）；fix 允許清單＝本表「允許檔案清單」欄＋review findings 指涉檔之聯集、次輪只縮不擴。
- 測試環境紀律：U3 起角色／選單／指派造列一律**顯式大 id**、號段依「表×檔」登記於 `test_kit.rs` 單一常數表（高於 `SYNTHETIC_UID_FLOOR`）；`casbin_rule` 例外＝經真判定面新增政策路徑造列（`add_policy`、取 nextval）使判定面確實持有該授權（FR-052 防恆綠）；使用者一律用 seed 使用者（uid 1 Super／2 Admin／3 User；停用＝`UserStatusFixture`、已軟刪＝`RowFixupGuard` 對 `deleted_at`／`deleted_by` 植值並快照還原；★UPDATE 不 INSERT、免造 `sys_user`＝brainstorm 工程判斷 10）；稽核斷言一律取 `OpLogRowsGuard` 水位窗、不寫絕對計數；src 側真庫案持 `DB_SERIAL`。
- 書面產物與註解一律 zh-TW；受版控文件**不寫 gitignored 工作區之具名路徑**（RL-0077；工作區檔一律以佔位形 `<工作區>/…` 表之）；跨檔引用不用行號。
- 停下等 user 之三情形（CLAUDE.md §2）：①拍板級問題（RULES 名詞段；問法＝AskUserQuestion 一題一問、2～3 選項含建議）②到了需要 push／merge 的時點 ③觸及 CLAUDE.md §6 硬禁令；其餘單元一支接一支連續跑完、**不停下等首肯**。

---

## Phase 1: Setup（★主線：前置體檢＋U0 兩顆親決 commit）

**Purpose**: 取得 base-web inline 與島 H 入憲的憲法授權、落定施工前提三支 ADR（user 親決）、環境就緒。★本 phase 全數主線任務、不入 agent 單元。

- [ ] T001 ★主線 前置體檢（不落 commit）：`bash tools/bootstrap.sh` 綠（含 rev5 凍結三 SHA 斷言）；`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait` 起得齊；容器內 `cargo --version`＝1.96.1；base-web 容器 `pnpm typecheck` 基線綠；`python3 tools/schema-gate.py check` 三閘綠；`python3 tools/walkthrough-baseline.py snapshot <工作區>/walkthrough-005-base.json` rc 0；記錄動工前基線：全量測試逐 target 計數（供 U3 殘列演練比對：只增不減）、`git -C base-web rev-parse HEAD`＝`3fb3ea31`（兩顆授權彈窗零 diff、Amendment 前零 diff 之比對基線）、`git -C rust-api rev-parse HEAD`＝`246d5ff`、migration 目錄恰兩支、seed 計數（選單 78／政策 163／角色 3）
- [ ] T002 ★主線任務（user 親決；Amendment 顆；BL-00098／BL-00118／BL-00119）：親決以 AskUserQuestion 一題一問逐項呈 `docs/arc42/decisions/ADR-00042-constitution-amendment-island-h-and-manage-page-use-ii.md` 決定一～七——①決定三 島 H 條文全文＋**差異附表逐列**（增補兩處／明文化三處／座標改寫；風險②）②決定三 H2「同步失敗保留上一份」方向句（工程判斷 40 可選強化轉採納＝research R15）③決定二 島 E 末兩點措辭定稿 ④決定五 §III.2 用途 (ii) 列逐字（九檔、兩顆授權彈窗與 `shared.ts` 明文不入）⑤決定六 表外宣告 1 量法句 ⑥決定一 §I.7 段首括號句 ⑦決定四（MAJOR 射程改「七島」／承襲指針表 H 列尾註「；rev6 已入憲 v1.5.0（ADR-00042）」／跨島重審結論＝跨島註不動）⑧決定七（`Version` 1.5.0／`Last Amended`／Amendment log 1.5.0 列逐項①～⑤／commit 範圍）；定稿後：ADR-00042 proposed→accepted（款七註 user 親決日期與本任務）＋`.specify/memory/constitution.md`（§I.7 段首括號／島 E 末兩點／島 H 段置於島 F 之後跨島註之前／MAJOR 射程／承襲指針表 H 列尾註；§III.2 新列置於 (i) 之後／表外宣告 1 改句＋既有各列範圍欄數字依現算覆核；文末版本行與 Amendment log）＋`README.md` 憲法版本鏡像行改為「現行 1.5.0＝ADR-00042；前版 1.4.0＝ADR-00034、1.3.0＝ADR-00026、…」（舊現行版前插進前版鏈、不得自鏈中移除）＋`docs/arc42/08-crosscutting-concepts.md` §8.4 引述「新增型圈界數」之引文改為現行字面（憲法一改即成假引文、須同顆）＋`python3 tools/fork-delta-lint.py` rc 0＋`python3 tools/docsync errata 1.4.0`／`errata 六島` 復掃（憲法命中已改、史料面不動）＋`generate`；獨立 commit `docs(constitution): amend §I.7 島 H＋島 E 兩點＋§III.2 MANAGE-PAGE (ii)＋表外宣告 1 與段首句（1.4.0→1.5.0）`，內容恰為憲法、ADR-00042、README 鏡像、活書 08 §8.4 引文與 generate 產物（＝spec FR-075 精修後字面＝ADR-00042 決定七；tasks 之 T001／T002 勾選隨 T003 落帳）。**DoD：lint 全綠；此 commit 落地即解除 base-web 既有檔硬閘；落地前 `git -C base-web status --porcelain` 空且 HEAD＝`3fb3ea31`**
- [ ] T003 ★主線任務（user 親決；施工前提顆）：AskUserQuestion 逐支呈 `docs/arc42/decisions/ADR-00043-enforcer-sync-rebuild-swap.md`／`ADR-00044-menu-domain-and-role-delete-behavior.md`／`ADR-00047-partial-update-semantics-v2.md` 之決定節 → 三支 proposed→accepted；ADR-00047 同顆補 `supersedes: [ADR-00015]`、`docs/arc42/decisions/ADR-00015-*.md` 之 `status` 改 superseded（body 不動；`superseded_by` 由 generate 回填＝GT-04）；`python3 tools/docsync errata ADR-00015` 現算現在式面逐處分流改指 ADR-00047 對應款（已知面：`docs/arc42/08-crosscutting-concepts.md` frontmatter「API 慣例」藍本值與 §8.2 部分更新三態句——依 FR-076 改述 ADR-00047 兩域語意〔系統設定空字串＝設值；角色與選單可空文字欄空字串＝清空落 NULL〕；`rust-api/server/src/handler/system_settings.rs` 8 處 doc 引用〔只改註、零碼改〕；史料面與 accepted body 不動）；`docs/ops/NOTES.md`「下一步」改為「現在＝005 進行中：SDD 五步已完（含 analyze）、U0 兩顆親決已落（憲法 1.5.0、ADR-00042／ADR-00043／ADR-00044／ADR-00047 accepted）；下一步＝U1 骨架」——★併入本顆、不另補 NOTES commit（user 2026-09-23 令），commit 本文加一行註明含 NOTES 更新；tasks T001～T003 勾選同顆；兩段式：rust-api commit（只註）→ 外層 `git add rust-api` → `generate` → 一顆外層 commit `docs(adr): accept ADR-00043／ADR-00044／ADR-00047（ADR-00047 supersedes ADR-00015）＋現在式引用改指`。**DoD：`errata ADR-00015` 復掃現在式面零殘留；lint 全綠；此 commit 落地即解除施工前提閘**

---

## Phase 2: Foundational（阻塞全部 user story：U1 骨架 → U2 004 域連帶 → U3 測試基建 → U4 域鎖與歸檔 → U5 判定面同步）

**Purpose**: 十七條路由在場且受政策保護、分頁共用規則與 004 域共用件收攏（US6 驗收場景 2／3 之承載）、業務五表測試守衛與判定面斷言 helper、選單序列化域與授權歸檔寫入面、判定面重建換上機制與三道名冊守恆（US4 之機制本體）。未完成前不得開任何 US 單元。

### U1 骨架（research R18；FR-001／FR-003）

- [ ] T004 [P] `rust-api/server/src/handler/role.rs`、`rust-api/server/src/handler/menu.rs` 新建空殼（檔頭 doc＝域職責、rev5 出處帶 `rev5:`；role 8 支＝getRoleList／getAllRoles／addRole／updateRole／deleteRole／batchDeleteRole／getRoleHome／updateRoleHome，menu 9 支＝getMenuList/v2／getMenuTree／getAllPages／addMenu／updateMenu／deleteMenu／batchDeleteMenu／getDeletedMenus／restoreMenu；每支 handler 暫回 `AppError::Internal` 佔位、並帶唯一碼註字面 `佔位：U6～U9 替換`〔T100 以此字面計數驗零殘留〕）＋`rust-api/server/src/handler/mod.rs` 以 ASCII 序插 `pub mod menu;`／`pub mod role;`（`ip_rule` < `menu` < `role` < `route`；兩域皆 `pub mod` 供 tests crate 取 DTO）＋模組 doc 域數句改現值
- [ ] T005 `rust-api/server/src/router.rs` ROUTES +17（路徑×動詞逐字對齊 seed 政策列：role 讀 12～16、role 寫 21～24、`/systemManage/getMenuList/v2` 25、getAllPages 26、getMenuTree 27、menu 寫 28～31、roleHome 34／35、getDeletedMenus／restoreMenu 64／65；GET 7／POST 6／DELETE 4；十七條皆 `Protection::Policy`、`case_key` kebab 形）＋`ROUTES_COUNT` 22→39＋`mod tests` 釘值 39＋`routes_block_literal_form_and_pinned_rows` 之 `expected` 陣列逐欄 18→35 列（序＝ROUTES 宣告序）＋assert 訊息與「二十二」字面改現值。**DoD：ROUTES 條目書寫形仍過 docsync 生成器契約**
- [ ] T006 `rust-api/server/tests/contract.rs` registry +17 case（序＝ROUTES 宣告序；共用驗證函式反查 case_key 綁定擋殭屍）：每條斷言 `Protection::Policy`＋`verify_policy_unauthenticated_8888`（未認證三形）；★授權態矩陣（FR-003／SC-001；真 seed 判定面）：Admin 對 15 支 R_SUPER-only 端點得 `5003`、對 getRoleList／getAllRoles 到達 handler（非 `5003`）；User 對 getAllRoles 到達 handler、其餘 `5003`；coverage 雙向閘 39＝39（分頁等附加案住各 case 驗證函式內或獨立測試函式、不增登記表鍵）；檔頭 registry 名冊句與「二十二」改現值
- [ ] T007 [P] 外層 `tools/docsync/tests/test_references.py` `TestRoutes.test_real_repo_pinned_rows` 之**兩份**釘值清單（`parse_router_routes` 之 rows 與 `gen_reference_routes` 輸出之 `| /` 行）各 +17 列（RL-0022；與 T005 同顆外層 commit）＋`python3 tools/docsync test` 綠
- [ ] T008 [P] `rust-api/server/src/handler/throttle.rs` 檔頭「憲法面此刻無對應條文…隨稽核域行為島進場時回填」句改現在式、指向憲法 §I.7 島 E 末兩點（ADR-00042 後果；RL-0015 回填）；`rust-api/server/src/model/audit.rs` `EXPECTED_LITERALS` 五詞零改動確認（零新 variant）

**Checkpoint（U1）**: ROUTES 39、contract 39＝39、授權態矩陣綠；rust-api commit → 外層 pin bump＋test_references 同顆＋generate（routes.md 39 列）

### U2 004 域連帶（research R8／R13；FR-054～FR-056 之規則半、FR-067～FR-069；US6 驗收場景 2／3／4 後端半）

- [ ] T009 `rust-api/server/src/envelope.rs` 分頁共用規則（置於 `serialize_opt_i64_number_guarded` 之前、使其續為生產區末 item）：`pub const PAGE_DEFAULT_SIZE: u64 = 10`／`PAGE_MAX_SIZE: u64 = 100`／`PAGE_MAX_CURRENT: u64 = 10_000_000`＋`pub fn page_params(current: Option<u64>, size: Option<u64>) -> (u64, u64)`（缺席→1／10；clamp current [1, 10^7]、size [1, 100]；顯式 0 取下界）＋明名入口 `pub fn page_or_all(current, size) -> PageSpec`（`size` 缺席→`PageSpec::All`、否則 `PageSpec::Page(page_params(..))`）＋`PageSpec`；unit 案（缺席／0／上下界／逾界矩陣）；★`page_or_all` 名冊案（生產面＝逐檔扣除每個行首測試模組區塊、同 `obs.rs` `production_part` 形、整檔測試模組依 `#[cfg(test)]`＋可帶可見性前綴之 `mod <名>;` 現算豁免；計數＝`page_or_all(`／`(page_or_all)`／`::page_or_all` 三形聯集、扣定義處；**本單元期望恰 0 處**；變異自證含「於 `auth/enforce.rs` item 級門控之後植一處呼叫必紅」）；`no_wire_literal_lives_in_envelope_production_code` 正面錨不動。**DoD：先紅後綠**
- [ ] T010 `rust-api/server/src/handler/ip_rule.rs` 改引 `envelope::page_params`、刪私有三常數；模組 doc 指向活書 08 §8.2；IP 規則清單既有契約案零改形全綠＋新增四案（缺席→(1,10)／逾界 `current` 回空頁且回應 `current`＝上界值〔BL-00116 契約〕／`&size=0&current=0`→(1,1)／壞形整串收斂預設；落 `rust-api/server/tests/contract.rs` 真 seed app 面之 get-ip-rule-list 案）；★FR-069 後端半特性鎖定案（BL-00095 後端半）：`handler/ip_rule.rs` 測試模組直種未知 `wbip_type` 列（`IpRuleRowsGuard`）→ `getIpRuleList` 照原樣上 wire、存取閘既有略過＋告警不變。**DoD：wire 逐位元同改前（US6 AS2）**
- [ ] T011 [P] `rust-api/server/src/model/facade/mod.rs` 上提三件：`ilike_contains`（`rev5:B-138`；不寫 ESCAPE、`$1`、欄參數 `&'static str`；`%`／`_`／`\` 視為字面）、`violated_constraint`（`rev5:f841b04`；只認指名活性唯一索引之 23505）、`now_ts`（`rev5:B-123`③）＋unit 案（轉義三字元、他索引衝突不收窄）；`rust-api/server/src/model/facade/sys_ip_rule.rs` 改引（`cidr_text_contains` 改呼 `ilike_contains("wbip_cidr::text", ..)`、零行為變更）
- [ ] T012 BL-00096：`rust-api/server/src/model/facade/sys_ip_rule.rs` 四寫端＋`find_by_id_for_update` 改收 `&DatabaseTransaction`（模組 doc「一律收泛型連線」段改寫）；三檔裸連線測試呼叫改自開交易並 commit（`grep` 現算、預估 `model/facade/sys_ip_rule.rs`／`handler/ip_rule.rs`／`ipgate/mod.rs` 測試模組共 40 處；`ipgate/mod.rs` 測試植列必 commit、門鈴重載走另一連線）。**DoD：IP 規則既有案全綠（SC-010）**
- [ ] T013 [P] BL-00082：`rust-api/server/src/config.rs` `load_trust_model` 對 tunnel 與每筆 cdn 之 `connecting_ip_header` 以 `axum::http::HeaderName::from_bytes` 驗合法性（零新依賴）；非法＝新 `TrustLoadKind` 變體＝一則結構化 warn（`scope`＝`tunnel`／`cdn`、欄型 `&'static str` 不變；`reason` 帶 `cdn[i]` 索引、原字面與改寫建議）、原字面保留、絕不改讀預設標頭名；★`TrustLoadKind::degraded_source()` 之 impl 住 `rust-api/server/src/obs.rs` 生產區、為窮舉 match ⇒ 同批把新變體納入 `=> None` 臂並改其 doc 列舉；案：config.rs 一正一反＋`rust-api/server/src/middleware/mod.rs` 測試模組兩則對拍（「非法名時預設標頭不被讀取」反案、「非法名時覆蓋層結果與修改前逐格相同」——打私有 `resolve_request_context`／`cdn_visitor_ip`）；`obs.rs` `trust_load_kind_maps_only_real_degradations_onto_the_roster` 補新變體一列（None）＋`rust-api/server/src/main.rs` 報出點案補一列（WARN 一行、無 degraded 欄；doc「五種」→六種）；`IP_DOMAIN_DEGRADED_SOURCES` 恰八不動。**DoD：先紅後綠（US6 AS3）**

**Checkpoint（U2）**: 分頁規則在場（`page_or_all` 零生產呼叫）、IP 規則清單 wire 逐位元不變、共用件收攏、具型交易簽章、標頭名體檢；rust-api commit → pin bump＋generate。review prompt 烤入 004 域防回歸與「零 wire 行為變更」判準

### U3 測試基建（research R11；data-model §9；contracts/code-gates.md §5；FR-070；BL-00110）

- [ ] T014 `rust-api/server/src/model/facade/test_kit.rs` 新守衛五支＋組合守衛＋兩支 helper：`RoleRowsGuard`／`MenuRowsGuard`／`CasbinRuleRowsGuard`／`PolicyArchiveRowsGuard`／`UserRoleRowsGuard`（水位一律＝`COALESCE(max(id) FILTER (WHERE id < 9_300_000_000), 0)`〔界值＝`SYNTHETIC_UID_FLOOR`、五表同套〕＋序列 `(last_value, is_called)`，皆 arm 時現讀；Drop 刪 `id >` 水位再 setval 回現讀值；指派守衛刪除集＝arm 快照鍵集差 ∪ `role_id >` 角色守衛水位者、先於角色列）＋組合守衛（Drop 序：指派→歸檔→授權→選單→角色）＋live 授權植入 helper（經 `state.enforcer.write()` 之 `add_policy`＝轉接器落庫取 nextval＋記憶體面同持；本檔為整檔測試門控模組、U5 腿②豁免）＋★判定面斷言 helper `face_allows(state: &AppState, role: &str, obj: &str, act: &str) -> bool`（內經 `crate::auth::enforce::enforce_role_path_method(&state.db, &*state.enforcer.read().await, <任填 uid；no-escalation 掛點本刀恆 Ok>, &[role.into()], obj, act)`；讀鎖於 fn 內取放、返回即放；Ok→true、`PermissionDenied`→false、其餘 panic；零 `.enforce(` 直呼）；自證測：清理序反腿（反序刪角色列必撞 FK RESTRICT）／arm 前預置號段內殘角色列＋其指派列時以 nextval 造列仍於 Drop 被清、序列回位、FK 不擋／seed 態序列期望（`sys_role_id_seq=(3,true)`／`sys_menu_id_seq=(78,true)`／`casbin_rule_id_seq=(163,true)`／`sys_casbin_policy_archive_id_seq=(1,false)`）只作自證前提／`face_allows` 對 seed R_SUPER 之既有政策為 true、對不存在政策為 false；檔頭收窄集句與守衛名冊句改現值（R17）
- [ ] T015 `rust-api/server/src/model/facade/test_kit.rs` 造列號段單一常數表（依「表×檔」登記、同表不同檔不重疊；含 tests 側檔列如 `tests/contract.rs` 之角色／選單／指派號段；★預登記 U4 之 `model/facade/sys_casbin_archive.rs` 測試號段列；★另設一列「殘列演練專用」號段、任何測試案不得使用）＋`rust-api/server/tests/common/mod.rs` 以同值字面自持其號段常數、純資料段以 `include_str!` 讀 `src/model/facade/test_kit.rs` 斷言自持值與表中對應列逐字相等（漂移即紅）
- [ ] T016 `rust-api/server/tests/common/mod.rs` tests 側五表守衛（沿既有 `IpRuleWriteGuard`＋`RestorePlan`／`run_restore` 形）：`RoleWriteGuard`／`MenuWriteGuard`／`CasbinRuleWriteGuard`／`PolicyArchiveWriteGuard`／`UserRoleWriteGuard`＋組合殼（Drop 序：指派→歸檔→授權→選單→角色；水位與序列 arm 現讀同 T014；★另帶 `sys_operation_log` 水位腿＝arm 現讀 `max(id)`、Drop 刪 `id >` 水位、序列不動〔runtime-append 口徑、形同既有 `IpRuleWriteGuard`〕，並暴露水位供 contract 側稽核窗斷言）＋純資料釘；計畫涵蓋 contract 真 seed 面 24 鍵發射段所需之角色／選單／授權／指派造列（code-gates §5）；BL-00110：7777 腿 denylist 鍵改 `RestorePlan.keys` 腿 RAII（消費者＝`rust-api/server/tests/contract.rs` `observed_msgs_real_db`）；守衛名冊句改現值
- [ ] T017 ★主線 SC-014 殘列演練（於單元收尾②執行、不落 commit）：以 psql 對 dev 庫於 T015「殘列演練專用」號段植殘角色列＋其指派列＋一列顯式大 id `casbin_rule` 殘列 → 容器內全量測試仍綠 → 拔除殘列、`python3 tools/walkthrough-baseline.py diff <工作區>/walkthrough-005-base.json` rc 0＋`python3 tools/schema-gate.py check` 綠；全量測試逐 target 計數與 T001 基線比對（逐 target 只增不減、增額＝U1～U3 新案）。**DoD：結果記單元 commit 訊息**

**Checkpoint（U3）**: 五表守衛（src 側＋tests 側）＋號段表＋`face_allows` 在場、殘列不連坐；rust-api commit → pin bump

### U4 選單序列化域底座＋授權歸檔寫入面＋reason gate（research R6；data-model §1.5／§3／§6；FR-038／FR-039／FR-041）

- [ ] T018 `rust-api/server/src/model/facade/sys_casbin_archive.rs` 新建之域鎖半：`MENU_DOMAIN_LOCK_KEY: i64 = 0x7265_7636_6D65_6E75`（ASCII `rev6menu`）＋`enter_menu_domain(txn: &DatabaseTransaction)`（thin fn、raw `SELECT pg_advisory_xact_lock($1)`；handler 內層首句呼叫、facade 其餘 fn 不自取）＋`menu_domain_waiter_count(conn)`（`pg_locks` 之 `locktype='advisory' AND NOT granted AND objsubid=1 AND ((classid::bigint << 32) | objid::bigint) = key`；可見性依 RL-0070 審）；真 DB 案：key 字面＝8243124669107236469 且高 32 位 1919252022／低 32 位 1835363957 皆 < 2^31、`menu_domain_waiter_count` 只計本 key（另持他 key advisory 等待者不計）、xact 級於 rollback／commit 自動釋放
- [ ] T019 同檔歸檔半：三 reason 常數（`role_soft_delete`／`menu_soft_delete`／`menu_button_removed`）＋`is_non_restorable_reason`（**三值**單點 fn＋成員測試）＋`insert_archived`（完整快照 `ptype`／`v0`～`v5`／原 `created_at`／`created_by`＋`role_id`＝以 `v0` 反查**活性**角色、查無 NULL＋`archived_at`／`archived_by`／`archive_reason`）＋`archive_all_role_policies`（`v0=role_code` 全三維含 protected）／`archive_menu_policies`（`v1=route_name AND v2='menu'` 跨全角色）／`archive_button_codes`（`v2='button'` 限給定碼集）——三支皆回傳歸檔列數、取「pub 收 `&DatabaseTransaction` 入口＋私有 `<C: ConnectionTrait>` 本體」形（`sys_operation_log` 前例）、掃描後以已掃 id 圈定 DELETE；`rust-api/server/src/model/facade/mod.rs` 註冊（ASCII 序）＋模組 doc「一張表配一支」改寫（例外恰一＝本檔同寫授權表與歸檔表）；真 DB 案（★掛 `CasbinRuleRowsGuard`＋`PolicyArchiveRowsGuard`＋`RoleRowsGuard`、植列取 T015 預登記號段之顯式 id）：快照逐欄完整、`role_id` 活性命中／查無 NULL、依 `v2` 維度過濾（跨維同字面誘餌列不被連坐＝SC-009）、等集迴歸（自訂 ConnectionTrait 注入「掃描後插隊」列、DELETE 不誤刪插隊列；注入旗標 `AtomicBool::fetch_or`）、回傳列數＝實際歸檔列數、各配變異紅證；`rust-api/server/tests/entity_access_lint.rs` 名冊如需同批。**DoD：先紅後綠；`python3 tools/walkthrough-baseline.py diff <工作區>/walkthrough-005-base.json` rc 0（逐表列數＋逐序列值）＋`python3 tools/schema-gate.py check` 綠**

**Checkpoint（U4）**: 域鎖與歸檔寫入面在場、reason gate 單點 fn 三值；rust-api commit → pin bump＋generate

### U5 判定面同步＋三道名冊守恆＋判定呼叫收斂（research R7／R12①；ADR-00043；FR-046～FR-049／FR-052 之機制半／FR-053）

- [ ] T020 `rust-api/server/src/auth/enforce.rs`：`rebuild_enforcer(db) -> casbin::Result<Enforcer>`（`DefaultModel::from_str(MODEL_CONF)` → `SeaOrmAdapter::new(db)` → `Enforcer::new` → `load_policy`；任一步 `Err` 即整體 `Err`）、`init_enforcer` 改委派之；`reload_enforcer(state: &AppState)`（函式內 `static RELOAD_SERIAL: tokio::sync::Mutex<()>` 全程持有；每次嘗試成功 → `#[cfg(test)] reload_seam::pause_if_armed().await` → 取寫鎖 `*guard = new;` 一行換上 → `casbin_reload_total{outcome="ok"}`；每次失敗〔含第 3 次〕→ `retry` 計數＋`tracing::error!(target: "security.authz", attempt, max, cause)`、attempt < 3 時線性退避 50ms×attempt〔末次失敗後不退避〕；三次皆敗 → 另計 `exhausted`、舊面續用）＋`RELOAD_MAX_ATTEMPTS = 3`／`RELOAD_RETRY_BACKOFF_MS = 50`＋`const _: () = assert!(…)` 常數自證＋`#[cfg(test)] mod reload_seam`（`rev5:932ba8c` 形、`Notify`＋`Mutex`、各件 `pub(super)`＝同檔測試模組可達；交錯時序案住本檔測試模組＝T063）；★檔頭與 `init_enforcer` doc 之「boot 載入即終態／不提供運行期重載／運行期只有讀鎖」諸句改寫（ADR-00043 決定 1；明引 ADR-00014 決定 4 為兌現其預告、不 supersede）＋doc 觸發矩陣恰五支（與 ADR-00043 決定 7、FR-050 同字面；不得寫成「成功即觸發」）＋casbin 2.20.0 `load_policy` 先清空再載入之版本鎖註解（升版必重核）；`rust-api/server/src/main.rs` 連線段註解、`rust-api/server/src/state.rs` 判定面欄 doc 同批改寫；`python3 tools/docsync errata 終態`／`errata 不再重載` 復掃
- [ ] T021 `rust-api/server/src/auth/enforce.rs` 測試模組（★全程零寫庫）：①失敗注入——以 `let mut state = test_kit::real_state_without_cache().await; state.db = test_kit::bad_db().await;` 構造（`AppState` 各欄皆 `pub`、不另起字面建構＝ADR-00036 唯一落點不破；舊面持 seed 政策、重建必敗；★`state_from_parts` 為 test_kit 私有 fn、U5 允許清單不含 test_kit.rs、不得改其可見性）呼 `reload_enforcer` ⇒ 舊面續放行 R_SUPER 既有授權（經 `face_allows`）、`retry` 3＋`exhausted` 1、error log 帶 cause ②「改寫為對現役判定面就地 `load_policy`」必轉紅之負向自證（以 seam 面操作、明文步驟註解：失敗轉接器下就地載入即清空⇒R_SUPER 被拒）③成功路徑換上——以 `test_kit::stub_state_with(real_db().await, None)` 取空政策面 → 斷言 R_SUPER 被拒 → `reload_enforcer` → 斷言 seed R_SUPER 政策放行＋`ok` +1（rev5 `reload_success_swaps_face_from_truth_and_counts_ok` 形）④三支併發 `reload_enforcer` 全數完成（完成性、無死鎖）⑤seam 自測（armed 時卡在換上之前、放行後完成；生產建置零存在＝`cfg(test)`）。**DoD：先紅後綠（US4 AS2；SC-006 之失敗注入／負向自證／ok 三項）**
- [ ] T022 [P] `rust-api/server/src/obs.rs` `pre_register_metrics` 補 `casbin_reload_total{outcome=ok|retry|exhausted}` 三值顯式零＋「樣本行恰三」上界守；檔頭宣告面句改現值（R17）；`IP_DOMAIN_DEGRADED_SOURCES` 恰八不動；該計數定性＝同步結果計數、非降級序列（R17③）
- [ ] T023 [P] `rust-api/server/tests/authz_entrypoint_lint.rs` 新建（`mod common;`、重用 `strip_comments_and_literals`／`collect_rs_files`；判準＝contracts/code-gates.md §2.1 逐字）：生產面定義（扣除行首測試模組區塊、item 級門控保守計入；豁免集＝整檔測試門控模組〔現樹唯一＝`model/facade/mod.rs` 之 `pub(crate) mod test_kit;`〕＋`tests/` 樹、以機器判準現算並自我對賬）＋①`RELOAD_CALL_FILES`＝**空冊**（三形聯集、家檔豁免）②`ENFORCER_WRITE_FILES`＝空冊 ③`load_policy`／`Enforcer::new` token 只許家檔 ④判定呼叫收斂（`ALLOWED_DECISION_FILES`＝{`auth/enforce.rs`}、完整 token `enforce`／`enforce_with_context`／`enforce_mut`／`enforce_ex`、前導 `.`／`::`、後隨 `(`／`::<`；射程＝src 全樹連測試模組）；各腿植入反例變異自證（④另含 `.enforce_ex(`／`CoreApi::enforce(` 必紅、`enforce_role_path_method(` 不紅；②另含「`test_kit.rs` 內植 `.enforcer.write()` 不紅、同形植入 handler 生產面必紅」）；★test crate 數量句隨本 crate 落地逐處 +1（現算、RL-0011）：`rust-api/server/tests/common/mod.rs`「守衛還原殼自證」段首註（名單補 `authz_entrypoint_lint`、「現行六支／六回／四支純源碼掃描 lint crate／×6」各 +1）＋`rust-api/server/tests/contract.rs` 檔頭「每輪跑六回」句與真基礎設施段首註（現行六支／六回／四支／×6）。**DoD：對現樹綠、反例紅**
- [ ] T024 [P] 外層 `deploy/grafana-provisioning/alerting/rules.yml`：`obs016-casbin-reload-anomaly` 錨字面不改、註解「（島 G1）」改指島 H2＋ADR-00043（FR-048；rev6 島 G 未入憲）

**Checkpoint（U5）**: 判定面可重建換上、失敗保留上一份、三道名冊守恆（空冊）與判定呼叫收斂上線；rust-api commit → 外層 pin bump＋rules.yml 同顆＋generate

---

## Phase 3: 讀端六支（U6；US1／US2／US3 之讀面基座；零新拒因鍵、不觸 locale）

**Goal**: getRoleList／getAllRoles（US1）、getMenuList/v2／getMenuTree／getAllPages（US2）、getDeletedMenus（US3）接真；`page_or_all` 名冊轉恰一處；治理域／顯示域分治。

**Independent Test**: quickstart §1（授權態）、§3 前三行（樹／輕量樹／頁面下拉）、§7（分頁四端點）；seed 下 getMenuList/v2 無參回 `current=1, size=11, total=11`、getAllPages 78 項。

### Tests（先寫、先確認紅）

- [ ] T025 [US1] `rust-api/server/tests/contract.rs` get-role-list／get-all-roles 驗證函式充實（DTO 形）＋真 seed app 面分頁四案（缺席→(1,10)／逾界 `current`＝上界值且空頁／`&size=0&current=0`→(1,1)／壞形整串預設；SC-008）；`rust-api/server/src/handler/role.rs` 測試模組（`RoleRowsGuard`）：列形逐欄白名單（FR-005；`roleMemo`／`roleHome`／審計欄在、軟刪欄不上 wire、`createdBy`／`updatedBy` 帳號名批次回填且查無→null、id number）；名稱／代碼不分大小寫子字串且 `%`／`_`／`\` 視為字面、空字串＝不篩選、`status` 字串恰 `'1'`／`'2'` 等值篩選其餘不篩；id 升冪；getAllRoles 每項恰 `{id, roleCode, roleName}`（宣告序）、僅活性且啟用、id 升冪（FR-011）
- [ ] T026 [US2] `rust-api/server/tests/contract.rs` get-menu-list-v2／get-menu-tree／get-all-pages 驗證函式＋真 seed app 面分頁四案；`rust-api/server/src/model/facade/sys_menu.rs` 與 `handler/menu.rs` 測試模組（`MenuRowsGuard`）：MenuRecord 28 欄＋`children` 子集為空則缺席、`deleted` 導出、頂層 `parentId`＝0、孤兒列顯 DB 原值且升根；getMenuList/v2 無 `size`（完全缺席與壞形）⇒ 全部頂層＋全深子樹、`current=1`、`size`＝實得頂層數、`total`＝頂層總數；帶 `size` 照通則（含 `size=0`→1、逾界）；★同層序擾動案（以 UPDATE 擾動實體回列序後兩次呼叫逐位相等；序＝`(order ASC NULLS LAST, id ASC)`、頂層分頁依此序切；FR-026）；getMenuTree `{id, label, pId, children?}`、`label`＝`menu_name`、葉只三鍵；getAllPages＝顯示域路由名全集同序；★治理域誤用顯示域負向測試（停用一支自建選單 → 出現於 getMenuList/v2 與 getMenuTree、不出現於 getAllPages；FR-022）；幽靈父收縮之既有顯示域案零改形（FR-025）
- [ ] T027 [US3] `rust-api/server/tests/contract.rs` get-deleted-menus 驗證函式＋真 seed app 面分頁四案（缺席 `size`→10、非 rev5 之 100＝R3 B5；已刪列以 tests 側 `MenuWriteGuard` 植）；`rust-api/server/src/model/facade/sys_menu.rs` 測試模組：僅已刪集合、平面（`children` 恆缺席）、`deleted` 恆 true、排序 `deleted_at DESC, id DESC`、MUST NOT 帶「可復原」旗標（FR-035）

### Implementation

- [ ] T028 [US1] `rust-api/server/src/handler/common.rs` 讀面共用件首次出現即落（FR-074）：`db_status_to_wire`（`Some(1)`→`'1'`、其餘含 NULL→`'2'`）、`wire_two_value_to_db`（trim 後恰 `"1"`／`"2"`、其餘含 `""`／null＝缺席）、`blank_to_none`（空字串→缺席）——皆 `pub(super)`、零 `tracing::debug!`＋unit 案；★泛型 `tristate<T>` 與 BL-00113 重評留 U7（第三個帶稽核寫端 handler 進場時）
- [ ] T029 [P] [US1] `rust-api/server/src/model/facade/sys_role.rs` 讀面：`page_query`（名稱／代碼經 `facade::ilike_contains`、狀態等值、id ASC、未刪、`PageRes` 形、收 clamp 後值）＋`all_active_enabled`（活性且啟用、id ASC）；檔頭讀面句與測試支數句改現值（R17）
- [ ] T030 [US1] `rust-api/server/src/handler/role.rs` getRoleList（`RoleListQuery` 抽取器住本檔、壞形整串收斂 default＋`tracing::debug!`；`status` 字串形；經 `envelope::page_params`；`RoleRecord` 逐欄白名單＋`sys_user::find_names_by_ids` 單次批次回填）＋getAllRoles（`AllRole` DTO 恰三欄）；DTO／抽取器可見性依施工約束⑨；替換 T004 佔位
- [ ] T031 [P] [US2] `rust-api/server/src/model/facade/sys_menu.rs` 治理域讀面：`list_governed`（未刪含停用、顯式 ORDER BY 同層序）／`build_governed_tree`（孤兒升根）／`paginate_top_level`（★facade 內**不 clamp**＝R3 B4；`(current-1)*size` 取頁）／`governed_tree`（輕量樹）／`display_route_names`（顯示域、同層序）；檔頭與測試支數句改現值
- [ ] T032 [US2] `rust-api/server/src/handler/menu.rs` getMenuList/v2（`MenuListQuery` 抽取器住本檔；★全樹**唯一** `envelope::page_or_all` 生產呼叫；`PageSpec::All` 回 `current=1`／`size`＝實得頂層數）＋getMenuTree＋getAllPages（`MenuRecord`／`MenuTreeRecord` DTO、`children` skip-empty；可見性依施工約束⑨）；★`rust-api/server/src/envelope.rs` 之 `page_or_all` 名冊案期望 0→**恰一處且在 `handler/menu.rs`**＋`PageRes` doc「上移後唯一生產者 `handler::ip_rule::get_ip_rule_list`」句改現值（分頁端點以清單式或不綁數量描述）；替換 T004 佔位
- [ ] T033 [US3] `rust-api/server/src/handler/menu.rs` getDeletedMenus（經 `page_params` 通則、平面、`deleted` 恆 true）＋`rust-api/server/src/model/facade/sys_menu.rs` 已刪清單查詢（`deleted_at DESC, id DESC`）；替換 T004 佔位

**Checkpoint（U6）**: 六支讀端接真、分頁四端點中三支新端點各四案、名冊恰一處；rust-api commit → pin bump（零 base-web 改動）

---

## Phase 4: User Story 1 — 超管管理角色全生命週期（P1）🎯 MVP ＋ User Story 5 — 角色首頁指定（P3）（U7）

**Goal**: addRole／updateRole／deleteRole／batchDeleteRole（US1）＋getRoleHome／updateRoleHome（US5）接真；BL-00113 重評；`biz.role.*` 10 鍵與三檔 locale 同單元；判定面同步接線 role 半。

**Independent Test**: quickstart §2（角色生命週期）＋§8（角色首頁）；Admin 直打寫端 `5003`；每筆成功寫入恰一列稽核、被拒零列。

### 鍵常數（先落、使守門腿可編譯）

- [ ] T034 [US1] `MSG_KEYS` 19→**29** 之 rust 側：`rust-api/server/src/error.rs` `pub mod msg_key` 加 `biz.role.*` 10 常數（`codeInvalid`／`codeExists`／`codeImmutable`／`notFound`／`seededProtected`／`inUse`／`cannotDeleteSelfRole`／`cannotDisableSelfRole`／`superCannotDisable`／`nameRequired`）＋`MSG_KEYS: [&str; 29]` 尾端追加＋名冊兩測（`msg_keys_roster_is_pinned_and_unique`／`biz_keys_are_in_roster`）；`msg_roster_every_key_has_an_emitter` 於本步轉紅、T040～T042 落地後轉綠（TDD 紅腿）

### Tests（先寫、先確認紅）

- [ ] T035 [US1] `rust-api/server/tests/contract.rs` add-role／update-role／delete-role／batch-delete-role 驗證函式充實（DTO 形；body 缺席或壞形收斂：addRole→`codeInvalid`、updateRole→零變更成功、deleteRole→id=0→`notFound`、batch→空陣列 no-op＝FR-009）＋batch-delete-role 兩案（含查無 id→整批 `notFound`、同一植入自建角色 id 重複兩次〔`[x,x]` 形〕去重後成功且稽核恰一列〔以 T016 組合殼之稽核水位窗斷言〕＝FR-037 之 contract 釘）＋`observed_msgs_real_db` 同族真 seed app 面實打 `biz.role.*` 10 鍵各 ≥1 發出點（tests 側 T016 之組合殼；名冊雙向閘方向二；SC-002）；★`superCannotDisable` 之真 seed 面發出：seed 僅授 R_SUPER 呼 updateRole、而 R_SUPER 成員停用 R_SUPER 先命中 `cannotDisableSelfRole` ⇒ 先以 `CasbinRuleWriteGuard` 植 `p(R_ADMIN, /systemManage/updateRole, POST)` 政策列（nextval）、**之後才建真 seed app**（判定面於建構時自庫載入）→ Admin（uid 2、非 R_SUPER 成員）送 `{id:1, status:"2"}` → `superCannotDisable`
- [ ] T036 [US1] `rust-api/server/src/handler/role.rs` 測試模組（真 DB、組合守衛＋`OpLogRowsGuard`、經中介層注入上下文；SC-003／SC-006 角色半）：①addRole 守門序逐腿（`codeInvalid`→`nameRequired`〔null 與 `""`〕→`codeExists`）＋多違規取先序腿＋**併發同碼恰一成功、另一回 `codeExists` 非 5000**（23505 收窄）＋可空文字欄（`roleDesc`／`roleMemo`／`roleHome`）送 `""`→落 NULL＋`status` 值域外取預設啟用＋成功後零授權＋成功稽核 `add` 恰一列 ②updateRole 守門序（提前 no-op→`nameRequired`→鎖列查無或已刪→`notFound`→`codeImmutable`→停用雙護欄）＋部分更新（缺席不動／可空文字欄 `""` 或 null 落 NULL／名稱 null 或 `""`→`nameRequired`／除 id 外全缺席＝成功零變更零稽核不 bump 時戳／`roleCode` 出現〔值同亦同〕→`codeImmutable`＝FR-007）＋成功稽核 `update` 恰一列 ③停用雙護欄（操作者所屬→`cannotDisableSelfRole`；非成員停 R_SUPER→`superCannotDisable`；Super 停 R_SUPER 先命中 self；成員身分含停用角色）＋★停用他人所屬自建角色後其成員（seed 使用者掛自建角色）下一請求即失去該角色授權、`casbin_reload_total` 零增（US1 AS4）④deleteRole 三層固定序 seeded→in-use→self-role 逐腿（in-use／self-role 以 seed 使用者掛自建角色之直種指派構造；掛載者為停用〔`UserStatusFixture`〕或已軟刪〔`RowFixupGuard` 植 `deleted_at`／`deleted_by`〕使用者亦算＝Clarifications Q2；`others = total − 操作者是否為成員`）⑤batchDeleteRole：任一違規整批拒零變更零稽核／含查無 id 整批 `notFound`／`[5,5]` 去重後成功且稽核恰一列／空陣列 no-op 零稽核不取域鎖 ⑥刪除成功：全三維政策列（含 protected）同交易歸檔 reason＝`role_soft_delete`、歸檔列 `role_id`＝該角色（掃描先於軟刪之證＝SC-009）、稽核一列 ⑦★判定面同步端到端（live 授權經 `add_policy` 植入、**刪前經 `face_allows` 斷言命中**→刪除→資料庫零殘留＋`face_allows` 零命中〔未重啟〕＋`ok` 計數 +1；批刪合計至多一次）；零政策列刪除→零同步（計數零增）⑧上下文缺席→`5000`（先於一切守門）、零稽核、拒寫事件帶 `refused`、零 degraded 欄、零降級計數（FR-008）⑨入域寫端（delete／batch）源碼釘：外殼 begin 後第一個呼叫即內層、一切失敗腿顯式 rollback（FR-045）
- [ ] T037 [US5] `rust-api/server/tests/contract.rs` get-role-home／update-role-home 驗證函式（update-role-home body 缺席或壞形→id=0→`notFound`＝FR-009）＋`rust-api/server/src/handler/role.rs` 測試模組：getRoleHome 回 `{home}`（無則顯式 null）、`id` 缺席或壞形→id=0→`biz.role.notFound`（不放行框架 400）、已刪或不存在→`notFound`；updateRoleHome 非部分更新（`home` 缺席／null／`""`＝清空 NULL、值同現值亦寫且稽核一列、不驗可見樹）、不存在角色→`notFound`、不進域（US5 AS1／AS2）

### Implementation

- [ ] T038 [P] [US1] `rust-api/server/src/handler/common.rs` BL-00113 重評三件＋泛型 `tristate<T>`（`rev5:B-094` 終態）：結論落檔 doc（兩件簽章不動——`operator_from_context` 回 `Option`、`tracing::error!` 留呼叫點帶各域 target；測試側 `table_state`／`audit_table_state` 與角色／選單庫態快照續不合併、理由＝窗界謂詞各異）；★同批改對 R17 已知命中之預告與域數句：`common.rs` 檔頭「重評預告」與關於 rev5 是否「逐字預警過同一個坑」之自相矛盾兩句（brainstorm 工程判斷 11）、`rust-api/server/src/handler/mod.rs` 模組 doc 與 `rust-api/server/src/handler/ip_rule.rs` 檔頭之「待 005 第三個寫端 handler 進場時重評」句改現在式結論、`handler/{ip_rule,throttle,common}.rs` 之「兩域字面之機器守」類句與 `handler/throttle.rs` 檔頭「重評時點」指針——域數一律寫**不綁數量之形**（例「各域」、免 U8 再改）；`rust-api/server/src/handler/system_settings.rs` 私有 String 三態改引（先依 RL-0070 查掃描閘：整樹腿不受影響、`handler/common.rs` 受 degraded 字面／debug 恰 1／`entity_access_lint` 守而泛型件不含受守 token；`use super::common::tristate;`、保住四處 [`tristate`] 文件連結、`deserialize_with = "tristate"` 字面不變）。**DoD：系統設定三態五案（含 `settingValue` null→`biz.systemSettings.invalidValue`、`description` null→NULL、空字串落空字串）之既有案零改形全綠（ADR-00047 決定 1／US6 AS5）**
- [ ] T039 [P] [US1] `rust-api/server/src/model/facade/sys_role.rs` 寫面：`SEEDED_ROLE_IDS: [i64; 3] = [1, 2, 3]`／`SUPER_ROLE_CODE = "R_SUPER"`（單一宣告源、`rev5:B-137` sys_role 半）／`ROLE_CODE_MAX_LEN = 64`＋`find_active_by_id_for_update`＋`create`／`update`（收 `&DatabaseTransaction`；可空文字欄 `""`→NULL）＋`delete_one_locked`／`batch_delete_locked`（歸檔 `archive_all_role_policies` **先於**軟刪、回傳實際歸檔列數）＋`home_of_role`／`set_home`；檔頭「本刀只落讀面／…不搬」句與測試支數句改現值；`rust-api/server/src/model/facade/sys_user_role.rs` 只讀 `count_by_role`（全部指派列、不 join 不濾）＋`is_member(role_id, uid)`（含停用角色之成員身分；research R2 所列 rev5 `role_ids_of_user` 之口徑改以成員判定承載；既有 `roles_of_user` 只回啟用且未刪角色之 code、口徑不合 self-role 故不復用）＋檔頭「寫端 assign／count_by_role 屬 user／role 管理刀」句改現值
- [ ] T040 [US1] `rust-api/server/src/handler/role.rs` addRole（不進域：`begin` → 形制 `^[A-Za-z0-9_]{1,64}$` → 名稱非空 → 活性唯一先驗 → INSERT〔`facade::violated_constraint` 只收 `sys_role_code_active_uniq` 之 23505→`codeExists`；其餘 DB 錯→5000〕→ `sys_operation_log::write_in_txn`〔`add`〕→ commit）＋updateRole（不進域；data-model §5.2 守門序；`status` 經 `wire_two_value_to_db`、可空文字欄經 `tristate`＋`blank_to_none` 語意）＋`operator_from`（target `security.role`、拒寫腿 `AppError::Internal` 收尾）＋寫端 body 以 `common::json_or_default(` 限定路徑形取用、本域專屬收斂訊息；請求 DTO 可見性依施工約束⑨；替換 T004 佔位
- [ ] T041 [US1] `rust-api/server/src/handler/role.rs` deleteRole／batchDeleteRole（進域：外殼 begin → 內層 `delete_role_in_txn`／`batch_delete_role_in_txn` 首句 `enter_menu_domain` → 逐 id 升冪鎖列＋三層守門〔批：空陣列於 begin 前提前成功、先去重〕→ 全數通過後逐標的歸檔＋軟刪＋稽核〔`delete`〕→ commit〔失敗腿顯式 rollback；鎖序依施工約束⑦〕→ commit 後 `if archived > 0 { reload_enforcer(&state).await }`、呼叫時不持判定面讀鎖、批刪至多一次）；★名冊同批：`rust-api/server/tests/authz_entrypoint_lint.rs` `RELOAD_CALL_FILES` 擴 `handler/role.rs`；`rust-api/server/src/handler/common.rs` `each_domain_keeps_its_own_log_literals` 名冊加 role.rs 五元組（file／src／refusal tokens／fallback_arg／fallback_const 同批填齊）；`rust-api/server/src/handler/ip_rule.rs` `production_code_emits_no_degraded_field` 射程加 role.rs（錨＝行首 `fn operator_from(`）；`rust-api/server/src/model/audit.rs` `entity_table` 列舉與 `model/facade/sys_operation_log.rs` 寫入者集 doc 補角色寫端（R17）；替換 T004 佔位
- [ ] T042 [US5] `rust-api/server/src/handler/role.rs` getRoleHome（`RoleHomeQuery` 抽取器、壞形→id=0）＋updateRoleHome（不進域；鎖列→`home` 缺席／null／`""`＝NULL、同值亦寫→稽核 `update`）；DTO 可見性依施工約束⑨；替換 T004 佔位
- [ ] T043 [P] [US1] `biz.role.*` 10 鍵之 base-web 側（T002 後）：`base-web/src/locales/langs/{en-us,zh-cn}.ts` 既有 `backend:` 圈界內補 10 鍵＋`base-web/src/locales/langs/zh-tw.ts` 10 鍵繁中＋`base-web/src/typings/app.d.ts` backend 型節 10 鍵（既有 I18N (ii)(iii) 圈界內；譯文依 contracts/msg-keys.md 語意要求重打字、`nameRequired` 涵蓋 null 與空字串）；`python3 tools/msg-key-gate.py check` 綠＋一反（刪一鍵→rc 1→還原）
- [ ] T044 [US1] ★主線（本刀首個動 base-web 之單元、T043 後、收尾④前）：`tools/fork-delta-lint.py` 新用途列名冊載入變異自證——演練前記錄 `git status --porcelain` 輸出 → 把 `.specify/memory/constitution.md` §III.2 (ii) 列範圍欄任一反引號路徑之**反引號內字面**改為不含 `/` 之非路徑 token（例 `role-index`；觸發 `load_roster` 路徑形斷言 RG8 die；★拔反引號形於 U12 前無 (ii) 標記可消費、恆綠＝不得作自證）→ lint 當場紅 → 還原 → `git status --porcelain` 與演練前逐字相同且 `git diff --quiet -- .specify/memory/constitution.md` rc 0（RL-0005）；結果記外層 commit 訊息；兩子庫 commit → 外層一顆雙 pin bump（★msg-key-gate 兩側同批）＋generate

**Checkpoint（U7）**: 角色 CRUD＋首頁讀寫上線、10 鍵齊、角色刪除家族入域且實際歸檔才同步——**MVP 後端面**（UI 於 U12）

---

## Phase 5: User Story 2 — 超管管理選單樹：新增／編輯（P1）（U8）

**Goal**: addMenu／updateMenu 接真——守門序凍結、href／按鈕碼形制、受保護兩腿、常量父鏈（含清除常量性之後代腿）、絕版歸檔＋判定面同步接線 menu 半；`biz.menu.*` 12 鍵。

**Independent Test**: quickstart §3 寫端行＋§4 前半（按鈕碼絕版→歸檔→未重啟即失效）＋§6（常量選單端到端）。

### 鍵常數（先落）

- [ ] T045 [US2] `MSG_KEYS` 29→**41** 之 rust 側：`rust-api/server/src/error.rs` 加 `biz.menu.*` 12 常數（`notFound`／`routeNameExists`／`routeNameImmutable`／`menuTypeImmutable`／`parentNotFound`／`cycleDetected`／`protectedMenu`／`constantParent`／`nameRequired`／`routeNameInvalid`／`hrefInvalid`／`buttonsInvalid`）＋名冊兩測

### Tests（先寫、先確認紅）

- [ ] T046 [US2] `rust-api/server/tests/contract.rs` add-menu／update-menu 驗證函式充實（DTO 形；body 缺席或壞形：addMenu→首腿 `routeNameInvalid`、updateMenu→零變更成功）＋真 seed app 面實打本單元 12 鍵各 ≥1 發出點（tests 側 T016 之 `MenuWriteGuard`）
- [ ] T047 [US2] `rust-api/server/src/handler/menu.rs` 測試模組 addMenu（組合守衛＋`OpLogRowsGuard`）：上下文缺席→`5000`（先於一切守門）、零寫入零稽核、拒寫事件 target `security.menu` 帶 `refused`、零 degraded 欄、零降級計數（FR-008）；守門序逐腿一案（父驗證〔不存在或已刪→`parentNotFound`、停用父不擋、`parentId=0`／缺席豁免〕→防環〔上溯逾 64 跳同鍵 `cycleDetected`〕→路由名活性唯一→常量父鏈〔常量標的掛非常量父、鏈斷保守拒→`constantParent`〕→路由名形制 `^[A-Za-z0-9_-]{1,100}$`→名稱非空〔null 與 `""` 各一案；Clarifications Q5〕→href→按鈕碼）＋至少一個多違規取先序腿案；href：`javascript:alert(1)`→`hrefInvalid`、`HTTP://` 大小寫不分放行、`""`→NULL；按鈕碼清單：非 null 非陣列／成員非物件／缺碼／碼為空或非字串／碼逾 100 字元（Unicode 字元計）／同清單重複 各一→`buttonsInvalid` 且零寫入；★`parentId=0` 落 NULL、讀端映 0、絕不寫 0（FR-020）；併發同路由名收斂 `routeNameExists`（23505 收窄）；可空文字欄 `""`→NULL、`menuType`／`status` 值域外取預設、`iconType` 值域外 NULL；成功零授權、稽核 `add` 恰一列、`casbin_reload_total` 零增；源碼釘（外殼 begin 後第一個呼叫即內層 `add_menu_in_txn`、一切失敗腿顯式 rollback；FR-045）
- [ ] T048 [US2] `rust-api/server/src/handler/menu.rs` 測試模組 updateMenu：上下文缺席先於提前 no-op→`5000`；data-model §5.5 守門序逐腿一案＋多違規取先序腿案；名稱 null 或 `""`→`nameRequired`；除 id 外全缺席＝成功零變更零稽核不 bump 時戳；不可變欄出現即拒（值同亦同；`routeNameImmutable` 先於 `menuTypeImmutable`）；★受保護兩腿各一正一反（seed 受保護列：`status:"2"`→`protectedMenu`、啟用值放行；`parentId` 改值→`protectedMenu`、**同值放行**；其餘欄照常可編）；改父之父驗證與防環（含孤兒列同值送回不誤拒）、改父 `parentId=0`→落 NULL（FR-020）；★常量父鏈：改父至非常量父／設為常量而祖先非常量→拒；**清除自身常量性而治理域全深後代（含停用、不含已刪）存常量者→`constantParent`、由下往上兩步皆成功**（US2 AS13）；部分更新語意（ADR-00047：可空文字欄 null／`""`→NULL、可空非文字欄 null→NULL、`iconType` null 清空／值域外缺席、`buttons:[]` 保留 `[]`、`query` 直傳）；「隱藏於選單」照常落庫（US2 AS12）；成功稽核 `update` 恰一列；★絕版：移除之碼不屬其他未刪選單（含停用）且直種該碼 live 按鈕維政策 → 同交易歸檔 reason＝`menu_button_removed`＋**刪前經 `face_allows` 斷言命中**→未重啟即零命中＋`ok` +1（SC-006 updateMenu）；該碼另被他選單（含停用）持有→零歸檔零同步；聯集排除標的自身之案；非絕版移除零歸檔（SC-009）；一般欄變更／無按鈕碼變更／被拒／no-op→計數零增；源碼釘（外殼 begin 後第一個呼叫即內層、失敗腿顯式 rollback）
- [ ] T049 [P] [US2] `rust-api/server/tests/contract.rs` 常量路由非空案（FR-021；★[P] 僅對 T047／T048，與 T046 同檔序列）：tests 側 `MenuWriteGuard` 植一列頂層常量選單 → 公開 `getConstantRoutes`（免登入）回非空且該列在、內建路由仍在 → 守衛清列；既有 `rust-api/server/src/handler/route.rs`「seed 下常量路由回 `[]`」真庫案保留並續持 `DB_SERIAL`（與 src 側 `handler/menu.rs` 植常量選單之案同在 lib test binary、以 DB_SERIAL 序列化；contract.rs 新案住 tests binary、cargo 逐 binary 序列不交錯）＋該檔「常量回 `[]`」doc 改現在式條件句（R17）

### Implementation

- [ ] T050 [US2] `rust-api/server/src/model/facade/sys_menu.rs` 寫面狀態機：`MENU_ANCESTOR_HOP_LIMIT = 64`／`ROUTE_NAME_MAX_LEN = 100`＋`find_active_by_id_for_update`＋父驗證（存在且未刪、停用不擋、頂層豁免）＋防環（上溯遇自身或逾限）＋常量父鏈（全祖先常量、鏈斷保守拒）＋治理域全深後代常量反查＋`button_codes_of`（壞形不再靜默跳過；呼叫前已驗）＋`obsolete_codes`（舊碼−新碼中不屬治理域其餘選單〔排除標的自身〕按鈕碼聯集者）＋`create`／`update`（收 `&DatabaseTransaction`；0→NULL 正規化；可空欄語意）；檔頭與測試支數句改現值
- [ ] T051 [US2] `rust-api/server/src/handler/menu.rs` addMenu（進域：外殼 begin → 內層 `add_menu_in_txn` 首句 `enter_menu_domain` → contracts/wire-menu-admin.md §4 守門序①～⑨ → INSERT〔`violated_constraint` 只收 `sys_menu_route_name_active_uniq`→`routeNameExists`〕→ 稽核 `add` → commit；失敗腿顯式 rollback；鎖序依施工約束⑦）＋`operator_from`（target `security.menu`）＋`common::json_or_default(` 限定路徑形取用、本域專屬收斂訊息；請求 DTO 可見性依施工約束⑨；替換 T004 佔位
- [ ] T052 [US2] `rust-api/server/src/handler/menu.rs` updateMenu（提前 no-op 與名稱非空於 begin 前 → 進域 → §5 守門序③～⑨ → 絕版計算 → `archive_button_codes`〔`menu_button_removed`、先於本列 UPDATE〕→ UPDATE → 稽核 `update` → commit → `if archived > 0 { reload_enforcer }`）；★名冊同批：`rust-api/server/tests/authz_entrypoint_lint.rs` `RELOAD_CALL_FILES` 擴 `handler/menu.rs`（接線後恰兩支 handler）；`rust-api/server/src/handler/common.rs` `each_domain_keeps_its_own_log_literals` 加 menu.rs 五元組；`rust-api/server/src/handler/ip_rule.rs` `production_code_emits_no_degraded_field` 射程加 menu.rs；`rust-api/server/src/model/audit.rs` `entity_table` 列舉補 `sys_menu`、`model/facade/sys_operation_log.rs` 寫入者集補 addMenu／updateMenu（R17）；替換 T004 佔位
- [ ] T053 [US2] `biz.menu.*` 12 鍵之 base-web 側：i18n 四處（`base-web/src/locales/langs/{en-us,zh-cn,zh-tw}.ts` backend 子樹＋`base-web/src/typings/app.d.ts` backend 型節）補 12 鍵——`protectedMenu` 譯文 MUST 涵蓋**不可刪除、不可停用、不可變更父選單**三種情形（前代「不可刪除」譯文不得照搬；FR-024）；`msg-key-gate` 綠＋一反；兩子庫 commit → 外層一顆雙 pin bump＋generate

**Checkpoint（U8）**: 選單新增／編輯上線、受保護兩腿、常量父鏈、絕版歸檔即時失效；41 鍵

---

## Phase 6: User Story 2 — 刪除／批刪（P1）＋ User Story 3 — 選單回收桶與復原（P2）（U9）

**Goal**: deleteMenu／batchDeleteMenu（連動歸檔＋同步）、restoreMenu（四腿守門、不回灌）；`hasChildren`／`restoreConflict` 兩鍵、名冊 43 全發。

**Independent Test**: quickstart §3 末行＋§4 後半＋§5（回收桶）。

### 鍵常數（先落）

- [ ] T054 [US2] `MSG_KEYS` 41→**43** 之 rust 側：`rust-api/server/src/error.rs` 加 `biz.menu.hasChildren`／`biz.menu.restoreConflict`＋名冊兩測（逐字釘 43 鍵）

### Tests（先寫、先確認紅）

- [ ] T055 [US2] `rust-api/server/tests/contract.rs` delete-menu／batch-delete-menu 驗證函式（delete-menu body 缺席或壞形→id=0→`notFound`；batch-delete-menu body 缺席或壞形→空陣列 no-op＝FR-009）＋batch-delete-menu 兩案（含查無 id→整批 `biz.menu.notFound` 零變更零稽核；同一植入之無子項非受保護葉選單 id 重複兩次〔`[x,x]` 形〕去重後成功且稽核恰一列〔T016 組合殼之稽核水位窗〕＝FR-037 之 contract 釘）＋`rust-api/server/src/handler/menu.rs` 測試模組：上下文缺席→`5000`；固定序 受保護→未刪子項（不論啟停）；★刪除 Z（無子項）且直種跨角色選單維 live 政策＋Z 獨有按鈕碼政策 → 兩者 reason 皆 `menu_soft_delete` 同交易歸檔（依維度過濾、誘餌不連坐）＋**刪前經 `face_allows` 斷言命中**→未重啟零命中＋`ok` +1（SC-006 deleteMenu）；零政策列選單刪除→零歸檔零同步（計數零增）；批刪：含父子→子先於父（深度 DESC、id DESC）逐項全套守門、「未刪子項」排除同批已刪者、任一違規整批拒（單一交易零變更零稽核）／含查無 id→整批 `notFound`／重複 id 去重／空陣列 no-op 不取域鎖／整批合計歸檔 ≥1 至多一次同步（SC-006 batchDeleteMenu）；稽核逐標的一列；源碼釘（兩支）
- [ ] T056 [US3] `rust-api/server/tests/contract.rs` restore-menu 驗證函式（body 缺席或壞形→id=0→`notFound`）＋`rust-api/server/src/handler/menu.rs` 測試模組：上下文缺席→`5000`；四腿守門序（標的非已刪存在〔含現役列〕→`notFound`、非冪等成功／同路由名活性衝突→`restoreConflict`〔併發 23505 收斂同鍵〕／父已刪→`parentNotFound`／常量標的之任一祖先非常量→`constantParent`、非常量標的零驗）；成功＝成對清空 `deleted_at`／`deleted_by`、原 status 保留、零授權寫入（`casbin_rule` 列數不變）、零同步（計數零增）、稽核 `restore` 一列（US3 AS2～AS5；SC-007 復原不回灌）；源碼釘

### Implementation

- [ ] T057 [US2] `rust-api/server/src/model/facade/sys_menu.rs` `delete_one_locked`（受保護→未刪子項→`archive_menu_policies`＋獨有按鈕碼〔標的碼−治理域其餘選單聯集〕之 `archive_button_codes`、皆 `menu_soft_delete`、**先於**軟刪→軟刪；回傳歸檔列數）＋`batch_delete_locked`（鎖讀全部標的、任一查無＝整批 `notFound`；拓撲序；回傳合計）；檔頭「`soft_delete`／`restore`…不搬」句與測試支數句改現值
- [ ] T058 [US2] `rust-api/server/src/handler/menu.rs` deleteMenu／batchDeleteMenu（進域外殼＋內層；空陣列 begin 前提前成功；去重；鎖序依施工約束⑦；commit 後 `if archived > 0 { reload_enforcer }`、批至多一次）；`rust-api/server/src/model/audit.rs`／`model/facade/sys_operation_log.rs` 寫入者集 doc 補 deleteMenu／batchDeleteMenu；替換 T004 佔位
- [ ] T059 [US3] `rust-api/server/src/model/facade/sys_menu.rs` `restore_locked`（含第四腿＝`rev5:ADR 0051`；23505 兜底→`restoreConflict`）＋`rust-api/server/src/handler/menu.rs` restoreMenu（進域；零授權寫、零同步）；寫入者集 doc 補 restoreMenu；替換 T004 佔位
- [ ] T060 [US2] 兩鍵之 base-web 側：i18n 四處補 `hasChildren`／`restoreConflict`；`rust-api/server/tests/contract.rs` `msg_roster_every_key_has_an_emitter` 覆蓋 43 鍵全數（SC-002）；`tools/msg-key-gate.py` `FRONTEND_MSG_CONSUMERS` 仍恰 1 筆（BL-00074 不觸發）；兩子庫 commit → 外層一顆雙 pin bump＋generate

**Checkpoint（U9）**: 選單寫端五支全上線、回收桶可復原、43 鍵全發

---

## Phase 7: User Story 4 — 刪除後殘留授權即時失效（判定面同步）（P2）（U10）

**Goal**: 零繼承端到端（選單維＋角色維）、交錯時序機器證、序列化域逐寫端機器證、觸發矩陣特性鎖定收齊。

**Independent Test**: quickstart §4（未重啟即失效、`casbin_reload_total` 增 1）；本單元諸案全綠。

- [ ] T061 [P] [US4] `rust-api/server/src/handler/menu.rs` 測試模組 選單維零繼承端到端（SC-007／FR-023）：live 授權植入（選單維＋按鈕維）→ 刪前經 `face_allows` 斷言命中 → 刪除 M → 以同路由名新增 M′ → 資料庫面（`casbin_rule` 零殘留、歸檔 reason 正確）＋判定面（`face_allows` 對 M′ 零命中）雙斷言；另一案：刪除後復原舊實例 → 零授權回灌（資料庫＋判定面）
- [ ] T062 [P] [US4] `rust-api/server/src/handler/role.rs` 測試模組 角色維零繼承端到端（FR-051／US4 AS4）：自建 R_X 經 `add_policy` 植 live 授權（無指派）→ 刪前經 `face_allows(&state, "R_X", obj, act)` 斷言命中 → 刪除 R_X → 同代碼重建 → 直種 seed 使用者（uid 3 User）對新 R_X 之指派（`UserRoleRowsGuard` 清）→ 經 `face_allows` 斷言對舊授權零命中
- [ ] T063 [US4] `rust-api/server/src/auth/enforce.rs` 測試模組 交錯時序案（FR-047／US4 AS5；rev5 `reload_serial_holds_second_reload_until_first_swaps_then_last_rebuild_wins` 形；同步機制唯一入口＝`reload_enforcer`，以測試直寫之探針 commit 代移除面寫端）：arm seam → spawn 甲 `reload_enforcer`（抵達 seam＝`gate.arrived`、持 `RELOAD_SERIAL`）→ 探針 commit（`CasbinRuleRowsGuard` 守之政策列變更）→ disarm → spawn 乙 `reload_enforcer` → 以有界 timeout 觀測乙未完成（候 `RELOAD_SERIAL`）→ 放行甲 → join 兩支（外罩 30s timeout）→ 斷言終態反映探針 commit（較晚者未被舊快照蓋回）；SeamReset RAII 於 panic 時亦解除武裝並放行
- [ ] T064 [US4] 序列化域機器證（FR-044／SC-005；research R6）：`rust-api/server/src/handler/menu.rs` 與 `rust-api/server/src/handler/role.rs` 測試模組逐**七支進域寫端**各一案——甲交易持域鎖；乙＝測試自開交易、`SET LOCAL lock_timeout = '10s'` 後呼該寫端之內層 `<op>_in_txn`（同檔私有 fn、測試模組可達）、外罩 `tokio::time::timeout(30s)`；以 `menu_domain_waiter_count` 輪詢至 1 再放甲；結果先存變數、兩交易收乾淨後才斷言「乙於放行後才完成」；★不進域三支（addRole／updateRole／updateRoleHome）各一案斷言甲持鎖時乙直接完成；空陣列批刪不取域鎖一案
- [ ] T065 [US4] 觸發矩陣特性鎖定收齊（FR-050／US4 AS1／AS6；SC-006）：`rust-api/server/src/handler/menu.rs`／`handler/role.rs` 測試模組逐形對照 SC-006 非觸發五形（零政策列／被拒／無作用／**標的不存在**／無按鈕碼變更）與 FR-050 次句（新增選單／復原選單／角色與選單之**停用與啟用**）既有案、缺即補——至少補：deleteRole 與 deleteMenu 之標的不存在（id 查無→`notFound`）各一案、角色啟用與選單啟用各一案 `casbin_reload_total` 零增；逐支核對五支觸發寫端之觸發案皆已在 T036／T048／T055（缺即補）；主線核 `docs/arc42/decisions/ADR-00043-*.md` 決定 7、`contracts` 觸發句、spec FR-050 與 `auth/enforce.rs` doc 觸發矩陣四處同一字面（`grep` 取證記 report；不得有「成功即觸發」）

**Checkpoint（U10）**: 零繼承雙維、交錯時序、七進域＋三不進域機器證全綠；rust-api commit → pin bump

---

## Phase 8: User Story 6 — wire 裁判面（P4）（U11）

**Goal**: 兩支型別檔＋兩支 wrapper 新檔落地、wire-schema 受審名冊涵蓋本刀全部新型＋`PageRes`、表驅動鍵集斷言、首屏真串、qs 前提錨（BL-00105／BL-00109／BL-00112）。

**Independent Test**: `python3 tools/wire-schema.py check` 綠＋各植入反例紅；容器內 `cargo test --test wire_schema` 綠。

- [ ] T066 [P] [US6] base-web 新檔 `base-web/src/typings/api/rev6-role-admin.d.ts`（檔頭 `BASE-WEB-ADAPT+`；`Api.RoleAdmin`：`RoleRecord`／`RoleListQuery`／`RoleAddReq`／`RoleUpdateReq`／`RoleIdReq`／`RoleBatchDeleteReq`／`RoleHomeQuery`／`RoleHomeRes`／`RoleHomeUpdateReq`；型名與後端 DTO 同名、欄序＝wire 欄序、寫端 nullable 三態欄為 `T | null` 可選欄）＋`base-web/src/typings/api/rev6-menu-admin.d.ts`（`Api.MenuAdmin`：`MenuRecord`／`MenuTreeRecord`／`MenuListQuery`／`MenuAddReq`／`MenuUpdateReq`／`MenuIdReq`／`MenuBatchDeleteReq`）；不入 barrel
- [ ] T067 [P] [US6] base-web 新檔 `base-web/src/service/api/rev6-role-admin.ts`（檔頭 `BASE-WEB-WRAPPER+`；role 6 支含 `fetchGetAllRoles`〔本刀零消費者、research R14〕＋`fetchGetRoleHome`／`fetchUpdateRoleHome`）＋`base-web/src/service/api/rev6-menu-admin.ts`（menu 7 支＋`fetchGetMenuTree`；getAllPages 走 upstream barrel 既有 `fetchGetAllPages`、該檔零改）；不入 barrel、消費端直接路徑 import；`pnpm typecheck` 綠
- [ ] T068 [US6] wire 受審名冊與表驅動斷言：於 host（repo 根）跑 `python3 tools/wire-schema.py extract`（工具自行 exec 進 base-web 容器抽取）→ `rust-api/server/tests/fixtures/wire-schema.json` 重抽（機器產出、禁手改）＋`rust-api/server/tests/wire_schema.rs`：受審名冊＝T066 全部新型（實數以抽取為準）＋`Api.Common.PaginatingQueryRecord`（BL-00112）；請求型 id／ids 具名型；★表驅動「序列化鍵集＝快照 properties 鍵集」helper 涵蓋全部受審讀型（既有七型含 `IpRuleRecord`＋本刀新讀型＋分頁信封；`Api.Route.MenuRoute` 交叉型佔位具名豁免附理由；BL-00105）；getAllRoles DTO 對 upstream `Api.SystemManage.AllRole`、`MenuTreeRecord` 對 upstream `Api.SystemManage.MenuTree` 相容斷言（FR-005／FR-027）；各附植入反例（多帶一欄→紅）
- [ ] T069 [US6] 首屏真串抽取案（FR-057；research R10；★落點釘死＝`rust-api/server/tests/wire_schema.rs`）：於 base-web 容器以 qs 6.15.1 實跑產出——getRoleList 取 `base-web/src/views/manage/role/index.vue` 之 `searchParams` 首屏物件字面（plan 期推定 `current=1&size=10&roleName=&roleCode=&status=`、以實跑為準）、getDeletedMenus 先釘通則首屏形 `current=1&size=10`（T078 以 `menu/index.vue` 已刪模式實跑值取代）、getRoleHome 以 T067 wrapper 之 `{id}` 經序列化器產出、getMenuList/v2 釘無參形；斷言各真串經後端抽取器解析為預期值；壞形收斂案逐 query 型各一
- [ ] T070 [US6] BL-00109 腿：`tools/wire-schema.py` 新腿——純讀檔斷言 `base-web/packages/axios/src/options.ts` 之 `paramsSerializer` 為無選項 `stringify(params)` 且 `base-web/packages/axios/package.json` 之 qs 為 `6.15.1`；位於 `cmd_check` 合成 self-test 之後、staged-gate 短路與容器探測之前、**無條件執行**；self-test 另釘「staged-gate 判跳過時本腿仍執行」＋植入反例（改序列化器選項／改版本→紅）；不擴收窄 pathspec、`.githooks/pre-commit` submodule-sync 段零 diff（BL-00074 不觸發）；兩子庫 commit → 外層一顆雙 pin bump（★wire-schema 兩側同批）＋工具改動同顆＋generate

**Checkpoint（U11）**: wire 裁判面涵蓋本刀全部新型、四支新前端檔在場、qs 前提有錨

---

## Phase 9: 前端接真（U12 role 頁＝US1；U13 menu 頁＝US2／US3＋ip-rule 頁＝US6）（★對 T002 硬序）

**Goal**: role／menu 頁自 demo 殼接真；共用表頭 prop 形；ip-rule 頁改 prop 形＋未知類型退顯；base-web 既有檔改動恰為用途 (ii) 九檔。

**Independent Test**: `pnpm typecheck` 綠、`fork-delta-lint` rc 0、單元出口機器斷言全過；瀏覽器 32080 手動可達（完整對照於 U16）。

★標記定形（活書 08 §8.4）：新增型圈界＝塊首 `[rev6-inline BASE-WEB-MANAGE-PAGE-WIRING(ii)+ 005-role-menu-crud START]`／塊尾同名 `… END]`（`+` 尾綴＝新增型）；修改型＝`[rev6-inline BASE-WEB-MANAGE-PAGE-WIRING(ii) 005-role-menu-crud] …原行: <基線該行原文>`（緊鄰新行之上）。

### U12 role 頁＋共用表頭（US1）

- [ ] T071 [US1] `base-web/src/components/advanced/table-header-operation.vue`（★(ii) 修改型；BL-00117）：`withDefaults(defineProps<Props>(), { showAdd: true, showDelete: true })`（純型別宣告下未傳即 false、會令既有呼叫端靜默失鈕＝必用帶預設值宣告）；備援插槽內新增鈕 `v-if="showAdd"`、批刪 NPopconfirm `v-if="showDelete"`；修改行逐行 `原行:`、純新增段走新增型圈界（定形見本 phase 首段）
- [ ] T072 [US1] `base-web/src/views/manage/role/index.vue`（★(ii)）：列表接真（`rev6-role-admin.ts` 之 getRoleList、分頁、搜尋、狀態、備註欄純文字插值）、刪除／批刪接真且成功後清勾選、拒因提示由共用攔截層轉譯、頁內只看成敗；兩顆授權彈窗之入口鈕不動；★`searchParams` 首屏物件（型改 `Api.RoleAdmin.RoleListQuery`、status 字串形）一旦改形 → 同批復跑 T069 之 getRoleList 真串案並更新（兩側同顆）
- [ ] T073 [US1] `base-web/src/views/manage/role/modules/role-operate-drawer.vue`（★(ii)）：新增／編輯接真、備註 textarea（placeholder 註明管理員可見）、編輯態代碼欄鎖定、更新請求逐欄顯式構造且 MUST NOT 帶 `roleCode`（FR-013／FR-061）
- [ ] T074 [US1] `base-web/src/views/manage/role/modules/role-search.vue`（★(ii)）：篩選欄對齊 wire（名稱／代碼／狀態字串）、重置後即重查
- [ ] T075 [US1] `base-web/src/locales/langs/{en-us,zh-cn}.ts`（★(ii) 新增型圈界、定形同本 phase 首段）`page.manage.role` 補角色備註欄標籤與表單鍵（`form.roleMemo` 插在 `form.roleStatus` 與末項 `form.roleDesc` 之間——★不得插在物件末項之後、否則上一行補尾逗號令該塊歸修改型而零鑑別＝research R14）＋`base-web/src/typings/app.d.ts`（★(ii)）`Schema.page.manage.role` 對應型節；兩語鍵集相等；`route:` 樹零新增
- [ ] T076 [US1] U12 出口機器斷言（主線復跑、結果記 commit 訊息）：`pnpm typecheck` 綠；`python3 tools/fork-delta-lint.py` rc 0；本單元各新增圈界塊逐塊拔 START／END → lint 必報未圈界新增 → 還原（RL-0005）；`git -C base-web diff 3fb3ea31..HEAD -- src/views/manage/role/modules/menu-auth-modal.vue src/views/manage/role/modules/button-auth-modal.vue` 零輸出；base-web commit → 外層 pin bump（若 U12 復跑 T069 則雙 pin 同顆）＋generate

### U13 menu 頁＋ip-rule 頁（US2／US3／US6）

- [ ] T077 [US2] `base-web/src/views/manage/menu/index.vue`（★(ii)）：治理清單無參一次取全樹（`rev6-menu-admin.ts`）、分頁列凍結（`itemCount: undefined`＋`pageCount: 1`＋`page: 1`＋`pageSize: 0`＋`disabled`＋自備 `prefix` 顯真實筆數——★MUST 走頁數分支、否則每頁 0 算出無限頁數凍死瀏覽器；`rev5:854a72ee` 形）、備註欄純文字插值
- [ ] T078 [US3] 同檔 `base-web/src/views/manage/menu/index.vue` 回收桶開關：換源 getDeletedMenus（常規分頁）、操作欄整欄換復原（無按鈕碼 gating）、切換清勾選（`rev5:ae1ac0c9`＝`rev5:B-100`）、切換前每頁筆數歸位（`rev5:84f283c7` 形）、已刪模式 `<TableHeaderOperation :show-add="false" :show-delete="false">`（不覆寫預設插槽）；已刪模式首屏物件定形後復跑 T069 之 getDeletedMenus 真串案、以實跑值取代先釘之通則形（兩側同顆）
- [ ] T079 [US2] `base-web/src/views/manage/menu/modules/menu-operate-modal.vue`（★(ii)）：父選擇器 `NTreeSelect`（取 getMenuTree、前插合成頂層節點 `{id: 0}`、新增／新增子項／編輯三模式皆顯）、頁面下拉（upstream barrel `fetchGetAllPages`）、備註 textarea（placeholder 註明管理員可見）、upstream 殘留 `fetchGetAllRoles` 呼叫 MUST NOT 帶入、編輯態路由名與選單型別鎖定且更新請求 MUST NOT 帶該兩欄（FR-018／FR-060）；★`base-web/src/typings/components.d.ts` 以 unplugin 重算、與本檔同 commit（禁手改）
- [ ] T080 [US6] `base-web/src/views/manage/ip-rule/index.vue`（rev6 新檔、免授權；BL-00117 之 ip-rule 半＋BL-00095 前端半）：表頭改 `:show-add="hasAuth('ipRule:add')" :show-delete="false" @add="handleAdd"`、不再覆寫 `#default` 插槽、隨 prop 形失效之疊寫碼註同批刪除；★未知 `wbipType` 於標籤映射取值與 `$t` 呼叫**之前**即退回原字串（不崩、不隱藏；FR-062／FR-069 前端半）
- [ ] T081 [US2] `base-web/src/locales/langs/{en-us,zh-cn}.ts`（★(ii) 新增型圈界、定形同本 phase 首段）`page.manage.menu` 補選單備註欄標籤與表單鍵、顯示已刪除、確認復原、復原、復原成功、父選擇器頂層標籤（`form.menuMemo`／`form.parentRoot` 插在 `form.buttonDesc` 與末項 `form.menuStatus` 之間、標籤鍵同理避開物件末項）＋`base-web/src/typings/app.d.ts` `Schema.page.manage.menu` 型節；兩語鍵集相等、`page:` 樹本刀合計 9 鍵（FR-064）
- [ ] T082 [US2] U13 出口機器斷言（主線復跑、結果記 commit 訊息）：`pnpm typecheck` 綠；`fork-delta-lint` rc 0 且修改型標記只出現於用途 (ii) 九檔；本單元各新增圈界塊拔標記必紅；★三支新增型檔之 **(ii) 塊數**逐檔斷言＝預估：`grep -c 'BASE-WEB-MANAGE-PAGE-WIRING(ii)+ 005-role-menu-crud START]'` 於兩語 locale 各＝4、`app.d.ts`＝4（含 U12 之塊；檔內總塊數＝7／7／6 含既有 I18N (ii)(iii) 與 (i) 塊、不作判準）——不等即停手升級主線、由 user 定當刀 PATCH 或比照 BL-00118 滯後；`git -C base-web diff` 之 `components.d.ts` 只准 `NTreeSelect` 兩行增列（介面內一行、全域 const 區一行）；`python3 tools/route-artifact-gate.py check` 冪等綠（路由產物四檔零變動）；`src/views/manage/menu/modules/shared.ts` 與兩顆授權彈窗對 `3fb3ea31` 零 diff；ip-rule 頁模板靜態斷言（`grep` 見 `:show-add="hasAuth('ipRule:add')"` 與 `:show-delete="false"`、零 `#default` 覆寫）；base-web commit → 外層 pin bump（若 T078 復跑 T069 則雙 pin 同顆）＋generate

**Checkpoint（U12／U13）**: 兩頁接真、表頭 prop 形、ip-rule 未知類型退顯；用途 (ii) 九檔以外 base-web 既有檔零 diff

---

## Phase 10: User Story 6 — 收刀前承載體檢＋走查工具擴面（P4）（U14、U15）

**Goal**: BL-00106／BL-00107／BL-00111／BL-00123／BL-00115 收；反向確認六條零觸發；走查還原工具擴至角色／選單／授權／歸檔／指派（排在 CDP 之前）。

**Independent Test**: 容器內全量測試綠、各新機器守植入反例必紅；`python3 tools/walkthrough-baseline.py test` 綠、對真 stack snapshot／diff rc 0。

### U14 收刀前承載體檢

- [ ] T083 [P] [US6] BL-00106／BL-00107：`rust-api/server/tests/wire_i64_guard_lint.rs` 補三件——①泛型 wire 型名冊（`Res`／`PageRes`）與樹上泛型 `Serialize` 型集合恰等＋實例化掃描 ②手寫 `impl Serialize` 絆線 ③型級普查等式（`derive(Serialize)` 錨數＝解析成功數、兼抓巨集生成型）；各附變異自證；檔頭「已知不抓的邊界」「與 rev5 藍本的差異」兩段改寫、未來式句改現值（R17；FR-072）
- [ ] T084 [P] [US6] BL-00111：`rust-api/server/tests/test_module_tail_lint.rs` 新建（`mod common;`、行掃描；判準＝contracts/code-gates.md §2.2 逐字）——判準①射程＝grep 判準現算之切面腿所在檔（現樹 9 檔：`src/{envelope,main,router}.rs`、`src/handler/{common,ip_rule,throttle}.rs`、`src/handler/auth/{login,refresh}.rs`、`src/ipgate/mod.rs`）∪ 跨檔腿名冊字面所指被切檔（`("<name>.rs"` 形抽取、以所在檔目錄為基準解析、自我對賬；★grep 與抽取於原文／Keep 視圖執行、item 掃描才用 Drop 視圖；射程納 `handler/role.rs`／`handler/menu.rs`）、切點後每個 column-0 item 屬性鏈含 `#[cfg(test)]`（頭形涵蓋可見性前綴與修飾詞）；判準②射程＝src 全樹、零 `obs::` 出口 item 別名匯入（含分組與跨行、含 `middleware/mod.rs` 與 bin crate `server::obs::` 形）；變異自證六形；既有十二支切面腿 docstring 補指本腿（落上列 9 檔）；`rust-api/server/tests/common/mod.rs`「守衛還原殼自證」段首註之 test crate 數量句再 +1、名單補 `test_module_tail_lint`（現算；FR-073）
- [ ] T085 [US6] BL-00123（★T084 後：本 task 之數量句依 T084 新建之 crate 現算）：`rust-api/server/tests/contract.rs` 請求上下文缺席之每請求總數案（至少打一支角色或選單寫端、釘「其餘端點 2 格」；`with_local_recorder` 套 app 級不可行即改 serial 差值形）；★反向確認角色／選單寫端拒寫**不**增計 `request_context_absent`（新增發射腿半邊不觸發）；同檔 test crate 數量句兩處（檔頭「每輪跑…回」＋真基礎設施段首註）隨 T084 之新 crate +1、名單補 `test_module_tail_lint`（現算）
- [ ] T086 [P] [US6] BL-00115：dev 信任模型對賬三態 rust 案（落 `rust-api/server/src/model/facade/test_kit.rs` 之 `tests` 子模組、`dev_trust_model()` 同檔）——`APP_TRUST_MODEL_PATH` 缺席＝具名跳過；在而讀檔失敗＝紅、訊息附 RUNBOOK §2 重建命令；讀得到＝逐欄比對 `dev_trust_model()`；外層 `docs/ops/reference-src/trust-model-config.md` 之 dev toml 區塊刪、改指交付檔 `deploy/trust-model.dev.toml`（三鏡像「刪一錨一」）
- [ ] T087 [US6] ★主線 反向確認（`grep` 現算、結果記單元 commit 訊息；FR-078／FR-040）：BL-00047 零建表（migration 目錄恰兩支）／BL-00028 零新設定鍵／BL-00048 no-escalation 空殼零 diff／BL-00074 兩半（`FRONTEND_MSG_CONSUMERS` 仍 1 筆、`.githooks/pre-commit` submodule-sync 段零 diff）／BL-00108 兩半（零第三份字元級解析組、`rust-api/server/tests/entity_behavior_lint.rs` 零 diff）／BL-00123 新增發射腿半邊（T085）／歸檔讀端與授權復原端點零存在（FR-040）；U14 rust-api commit → 外層 pin bump＋reference-src 同顆＋generate

### U15 走查還原工具擴面（排在 CDP 之前；與 U14 檔域不交、可對調次序）

- [ ] T088 [US6] `tools/walkthrough-baseline.py`（contracts/code-gates.md §6）：①**快照檔形擴充**——新增逐表 id 上界欄（`sys_role`／`sys_menu`／`casbin_rule`／`sys_casbin_policy_archive`）與 `sys_user_role` 鍵集欄、`SCHEMA_VERSION` 1→2、舊版基準檔以 rc 2 拒收並指名重新 snapshot ②restore 面加四表（刪 `id >` snapshot 上界列＋setval 回 snapshot 現讀值）＋`sys_user_role` 以 snapshot 鍵集差刪除、先於角色列；seed 有列之表不套「列數非 0 即拒」與 DELETE 全表形 ③`restore --seed` 模式對新增五表之處置：安全帶「COPY 段須在場且零列」只套 runtime 表；seed 有列之表改以 seed.sql 之 COPY 列 id 上界與 setval 值為目標（刪上界以上列＋setval 回 seed 值）、`sys_user_role` 以 seed COPY 鍵集為目標 ④動過 `casbin_rule` 之 restore 後輸出「MUST 重啟 rust-api」補救句；`python3 tools/walkthrough-baseline.py test` 逐字釘新寫面與 seed 模式新腿（離線樁）＋對真 stack `snapshot`／`diff` rc 0；`docs/ops/RUNBOOK.md` §9c 契約句與 §12 工具鏈速查之 walkthrough-baseline 列同批改（「五表」系列字面、setval 支數、拒跑條件、重啟句；字面仍住工具常數）＋`python3 tools/docsync errata 五表` 復掃；exec bit 不變（`git update-index --chmod=+x` 如需）；外層工具 commit＋generate

**Checkpoint（U14／U15）**: 體檢五條收、反向確認在案、走查工具可還原本刀全部寫面

---

## Phase 11: CDP 三方對照（U16；US1／US2／US3／US6 驗收；判準＝spec SC-011）

**Goal**: rev5 22080 vs rev6 32080（必要時加 upstream 22089）結構清單逐項全等；ADR-00045 各款「觀察路徑→症狀」實測定稿。

**Independent Test**: SC-011 結構清單逐項記錄於工作區走查紀錄、任一項不等即紅；走查前後 `walkthrough-baseline.py diff` rc 0。

- [ ] T089 [US1] ★主線派 opus agent（CDP 接 `127.0.0.1:9229`、工具＝`tools/orchestration/cdp.mjs`、一律 127.0.0.1）：走查窗開頭 `python3 tools/walkthrough-baseline.py snapshot <工作區>/walkthrough-005-u16.json`；角色頁三方對照（表格欄位集合與列序／搜尋器項目／按鈕集合與權限顯隱／抽屜欄位與校驗訊息／分頁列形／toast 文案／備註欄）、寫入步驟一律對走查自建角色；編輯請求 body 以網路請求事件斷言不含 `roleCode`；拒因步驟挑前端不先擋之守門並以網路請求事件證請求發出；role 頁與 user 頁表頭對 22089 新增／批刪鈕仍在（FR-063）
- [ ] T090 [US2] ★主線派 opus agent：選單頁三方對照（樹表全取＋分頁列凍結形／父選擇器三模式首項頂層／頁面下拉／新增編輯彈窗欄位與校驗訊息／編輯態路由名與選單型別鎖定且請求 body 不含該兩欄／備註）；按鈕碼移除→歸檔＋同步（對自建選單植顯式大 id 政策列後操作）；★常量選單端到端一步（FR-021：建頂層常量選單→登出狀態下該列可見、內建路由仍在、路由可達→刪除）；rev6 翻案腿（受保護選單停用／改父、href、按鈕碼清單拒因）與 `protectedMenu` 譯文改寫之 toast 差異入排除清單並記錄
- [ ] T091 [US3] ★主線派 opus agent：回收桶流程對照（開關換源、操作欄換復原、切換清勾選、pageSize 歸位、已刪模式寫入口不現、復原後回樹且原狀態保留）
- [ ] T092 [US6] ★主線：ip-rule 頁表頭 prop 形與 22080 零差異、未知類型列以原字串呈現（psql 直種一列、走查後清）；ADR-00045 各款以「觀察路徑→症狀」實際操作觀察並改寫 `docs/arc42/decisions/ADR-00045-role-menu-known-states.md` 草稿（仍 proposed；新發現之已知態直接併入；policy-archive 死項症狀若與 BL-00045 描述不符＝`python3 tools/docsync errata` 後改該條文）；排除清單＝SC-011 所列（rev5 22080 之 `rev5:006`～`rev5:008` 增量、已知態各款、治理清單三列路由裸鍵、請求次數維度、rev6 翻案腿）；走查窗收尾：`python3 tools/walkthrough-baseline.py restore <工作區>/walkthrough-005-u16.json` → 重啟 rust-api（動過 `casbin_rule`）→ `diff` rc 0；外層 commit（ADR-00045 草稿改動）＋generate

**Checkpoint（U16）**: SC-011 全等、已知態定稿、走查後庫態回基準

---

## Phase 12: User Story 6 — 治理面、文件與帳本（P4）（U17 前兩段）

**Goal**: ADR-00045／ADR-00046 親決（先行）、活書 as-built、RUNBOOK、reference-src、dev toml、BACKLOG 三條改條文、四形種子假述零殘留。

**Independent Test**: `python3 tools/docsync lint` 零錯；`errata` 逐詞復掃零殘留；ADR 六支皆 accepted。

- [ ] T093 [US6] ★主線任務（user 親決；U16 收尾後即做、落地後才派 U17 agent；BL-00125／BL-00120 前代出處半）：AskUserQuestion 逐支呈 `docs/arc42/decisions/ADR-00045-role-menu-known-states.md`（CDP 定稿後各款）與 `docs/arc42/decisions/ADR-00046-ip-domain-known-states-v2.md`（七款＋款號對照表）→ 兩支 proposed→accepted；ADR-00046 同顆補 `supersedes: [ADR-00040]`＋`docs/arc42/decisions/ADR-00040-ip-domain-known-states.md` `status` 改 superseded；`python3 tools/docsync errata ADR-00040` 現算現在式面逐處改指（已知面：活書 06／08／11／12、RUNBOOK、BACKLOG BL-00043／BL-00091 條文內指針；史料面與 accepted body 不動）；★ADR-00046 後果「對沖註同批刪」：「★as-built 對沖＝BL-00125」註三處（`docs/arc42/06-runtime-view.md` 島 F ⑧、`docs/arc42/11-risks-and-technical-debt.md` IP 域已知態列、`docs/ops/RUNBOOK.md` §16.1）同批刪；活書 11 該列標題「（一刀六款）」改七款並指 ADR-00046；`generate`；單獨一顆外層 commit（二態→三態之逐處改寫由 T094～T097 承擔、rust-api 測試 doc 由 T099 承接）
- [ ] T094 [P] [US6] 活書 as-built（feature branch 內、現在式；FR-077；T093 後）：`docs/arc42/05-building-block-view.md`（handler 兩新檔、facade `sys_casbin_archive`、enforce 同步面、共用件落點）／`06-runtime-view.md`（新情境「選單域生命週期——島 H」：移除面→歸檔→commit→重建→換上、失敗保留上一份；★島 H 常數之家＝本情境內載 `MENU_DOMAIN_LOCK_KEY`＝`0x7265_7636_6D65_6E75`、防環上溯上限 64、`route_name` 形制上限 100〔FR-041、ADR-00042 島 H 常數行〕；「情境逐則如下（島 A～F」計數句改含島 H、frontmatter `rev5_blueprint` 補選單域生命週期列；島 F ① boot 步補非法標頭名只告警不計降級〔BL-00082〕；島 F 相關句之三態字面）／`08-crosscutting-concepts.md`（§8.1 備註「UI 兌現隨對應 UI 刀」改現在式；§8.2 API 慣例：跨端點分頁通則＋例外表〔恰選單治理清單〕、ROUTES 39、`MSG_KEYS` 43 名冊指針；§8.2 部分更新三態句已於 T003 改、此處只復掃；§8.3「寫後全量重載（憲法 §I.1／§I.2）」改寫並去錯誤出處歸屬、末句「回收桶」改「授權回收桶」並與選單回收桶分立；§8.4 用途 (ii) 逐用途 as-built、共用元件 prop、AUTH-WIRING(a)「seed `constant=TRUE` 為 0 列、後端回 `[]`」句改現在式條件句）／`10-quality-requirements.md`（島 H 品質情境一則＋「A～F／G～J」計數句）／`11-risks-and-technical-debt.md`（已知態列指 ADR-00045／ADR-00046、IP 域三態、寫入者集）／`12-glossary.md`（治理域／顯示域、序列化域、絕版、常量父鏈、reason gate、選單回收桶與授權回收桶分立、casbin 判定面、判定面同步與 IP 規則熱重載分立；「已隨憲法 §I.7 島 A～F 入上表」句改含島 H；「降級（基礎設施）」條目不改＝`casbin_reload_total` 為同步結果計數）／`04-solution-strategy.md`（R17 措辭）
- [ ] T095 [P] [US6] `docs/ops/RUNBOOK.md`：§11 選單域鎖觀測（`pg_locks` classid／objid 拆讀 64-bit key、bigint 直比恆假）與 `casbin_reload_total` 三 outcome 判讀；§13 exhausted 處置（查結構化 log 之 cause → 修 DB 連線 → 重啟 rust-api → 驗計數；耗盡窗殘留繼承風險；★只寫實跑過之命令）；§16.1 dev 分界三態；§16.2 標頭名核對句（BL-00082）；§12 碼面閘表 wire-schema 列補 BL-00109 腿守什麼與已知邊界（工作樹改 axios 設定未 commit）
- [ ] T096 [P] [US6] reference-src：`docs/ops/reference-src/schema-definition.md`（hide_in_menu 釋義句改現在式並指向 ADR-00044 款 6、六列白名單只描述 seed；memo 預告句改現在式）／`docs/ops/reference-src/trust-model-config.md`（失敗語意表加非法標頭名一列＝BL-00082；失敗語意節標題之計數與「皆發 `ip_domain_degraded_total`」句同改〔新列不計降級〕；dev 交付形殘句）／`docs/ops/reference-src/code-gate-contracts.md` §1（BL-00109 腿行為契約）
- [ ] T097 [US6] 外層 `deploy/trust-model.dev.toml` 註改三態、「T013 的二態走查」改為不綁態數之描述（R17④）；★改後先重建 rust-api 容器（`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate rust-api`）再跑任何容器測試（LL-00033）；T086 對賬案讀得到＝逐欄綠
- [ ] T098 [P] [US6] `docs/ops/BACKLOG.md` 條文改寫三條（FR-078）：BL-00120 改為只剩 ADR-00039 半（ADR-00040 半由 ADR-00046 補齊前代出處）／BL-00093 ② 加 casbin-reload 錨已對齊之戳記／BL-00045 補「選單管理頁治理清單顯路由裸鍵」曝光面；★`backlog_done` 19 條之刪列於收刀簿記（不在本任務）；`backlog_add` 零——實作期若冒出新欠，先問本批能否做完再議
- [ ] T099 [US6] as-built 四形種子終掃（research R17 全清單；FR-077）：`python3 tools/docsync errata <詞>` 逐詞枚舉（名稱／「隨…進場」「待 005」「進場時重評」形／facade 與 handler 名冊／舊數量詞：`二十二`、`19 鍵`、`六支`、`五種`、`不再重載`、`終態`、`二態`、`兩域`、`唯一生產者`、`只落`、`不搬`、`count_by_role`、`六款`、`對沖` 等現算）→ 逐處改對（★`二態` 之 rust-api 兩處測試 doc 由本任務承接、子庫 commit）、改完復掃零殘留；U17 治理顆：rust-api commit（如有）→ 外層一顆 commit（T094～T099、雙 pin 如有）＋generate

---

## Phase 13: Polish & Cross-Cutting Concerns（DoD 收攏；U17 第三段）

- [ ] T100 全量閘綠（FR-079）：容器內 `cargo test --workspace -- --test-threads=1`＋`cargo fmt --all --check`＋`cargo build --release -p server`＋release 二進位 `/health`；base-web 容器 `pnpm typecheck`；`python3 tools/fork-delta-lint.py`＋`python3 tools/msg-key-gate.py check`＋`python3 tools/wire-schema.py check`＋`python3 tools/view-render-guard.py check`＋`python3 tools/route-artifact-gate.py check`＋`python3 tools/schema-gate.py check`（三閘；migration 恰兩支、seed 計數不變）＋`python3 tools/entity-drift-gate.py check`＋`python3 tools/docsync test`／`check`／`lint` 零紅；`docs/generated/reference/routes.md` 恰 39 列；contract 39 case 全綠；`grep -c '佔位：U6～U9 替換' rust-api/server/src/handler/role.rs rust-api/server/src/handler/menu.rs` 皆 0（T004 佔位全數替換）；SC-012 git 史可證：base-web 首顆本刀 commit 之外層 pin bump 晚於 T002 外層 commit
- [ ] T101 反例演練（★T100 後序列、暫改主檔不與全量閘並行；RL-0005 每項還原後回基準態＝`git status --porcelain` 與演練前逐字相同）：①contract coverage 負向（抽一 case→紅→還原；殭屍 case→紅→還原）②`tools/fork-delta-lint.py` 對新用途列變異（T044 之非路徑 token 形復跑）③`rust-api/server/tests/authz_entrypoint_lint.rs` 四腿與 `tests/test_module_tail_lint.rs` 兩判準各一植入反例復跑 ④`rust-api/server/src/envelope.rs` `page_or_all` 名冊案植第二處呼叫→紅；結果記 commit 訊息
- [ ] T102 quickstart 端到端走查（SC-015）：`specs/005-role-menu-crud/quickstart.md` §0 snapshot → §1～§8 逐節（API 面；§9 UI 已於 U16）→ §10 restore＋重啟 rust-api＋`diff` rc 0；走查後容器內全量測試仍綠（SC-014）；結果記工作區紀錄
- [ ] T103 SC 與驗收場景對照（report）＋perf：SC-001～SC-015 逐條對照、US1～US6 驗收場景 → 測試函式名或演練紀錄對照表（見下「需求追溯」、無承載者即紅；SC-016 收刀面於簿記後驗）；pre-commit 全鏈實測（雙 pin bump 觸發全段）≤45s 警戒 → `docs/ops/events.jsonl` append `precommit_chain` perf 事件；U17 收攏顆：外層 commit＋generate；final holistic review 輸入

---

## 執行單元對映（承 research R18〔U3～U5 重排〕；主線派發粒度；冒煙 token 取單元名形 `u<N>-<slug>-<4hex>`、不可取 `test`）

「允許檔案清單」欄＝該單元 agent **唯一可寫面**（逐字抄成 `ALLOWED_BLOCK` 常數；★＝註冊檔或連動釘值檔、漏列即 fix agent 撞牆）；**GENERATED_FILES 成員一律不入清單、由主線六步序⑤ generate 帶入**；「限定式」項只准為還原式演練暫改、每項還原後回基準態（RL-0005）。路徑前綴 `server/`＝`rust-api/server/`。

| 單元 | 任務 | 允許檔案清單（起始） | 收尾產物 |
|---|---|---|---|
| U0 主線 | T001～T003 | `docs/arc42/decisions/ADR-{00042,00043,00044,00047,00015}-*.md`、`.specify/memory/constitution.md`、`README.md`（憲法版本鏡像行）、`docs/arc42/08-crosscutting-concepts.md`（§8.4 引文＝T002；frontmatter／§8.2＝T003）、`server/src/handler/system_settings.rs`（僅 doc 8 處）、`docs/ops/NOTES.md`、`specs/005-role-menu-crud/tasks.md`（勾選）、`errata ADR-00015` 現算之現在式面 | Amendment 顆（憲法 1.5.0 獨立 commit）；施工前提顆（rust-api commit→外層 pin bump 同顆）＋generate |
| U1 | T004～T008 | `server/src/handler/{mod,role,menu}.rs`、★`server/src/router.rs`、★`server/tests/contract.rs`、★`tools/docsync/tests/test_references.py`、`server/src/handler/throttle.rs`（僅檔頭 doc）、`server/src/model/audit.rs`（僅核） | rust-api commit→外層 pin bump＋test_references 同顆＋generate（routes.md 39） |
| U2 | T009～T013 | `server/src/envelope.rs`、`server/src/handler/ip_rule.rs`、`server/src/model/facade/{mod,sys_ip_rule}.rs`、`server/src/ipgate/mod.rs`（僅測試模組）、`server/src/config.rs`、`server/src/obs.rs`（`TrustLoadKind::degraded_source` 之 match 臂與其 doc＋測試列）、`server/src/middleware/mod.rs`（僅測試模組：T013 兩則對拍）、`server/src/main.rs`（僅測試列與 doc）、★`server/tests/contract.rs`（get-ip-rule-list 分頁案）、`server/src/model/facade/test_kit.rs`（僅既有守衛之消費） | rust-api commit→pin bump＋generate |
| U3 | T014～T017（T017 主線） | `server/src/model/facade/test_kit.rs`、`server/tests/common/mod.rs`、★`server/tests/contract.rs`（`observed_msgs_real_db` 之 7777 腿）；限定式（主線）：dev 庫殘列植入（T017、當場拔除） | rust-api commit→pin bump |
| U4 | T018～T019 | `server/src/model/facade/{sys_casbin_archive,mod}.rs`、★`server/src/model/facade/test_kit.rs`（僅號段登記）、★`server/tests/entity_access_lint.rs`（名冊如需） | rust-api commit→pin bump＋generate |
| U5 | T020～T024 | `server/src/auth/enforce.rs`、`server/src/obs.rs`、`server/src/main.rs`（doc）、`server/src/state.rs`（doc）、`server/tests/authz_entrypoint_lint.rs`（新）、★`server/tests/common/mod.rs`（段首註數量句）、★`server/tests/contract.rs`（test crate 數量句兩處：檔頭＋真基礎設施段首註）、`deploy/grafana-provisioning/alerting/rules.yml` | rust-api commit→外層 pin bump＋rules.yml 同顆＋generate |
| U6 | T025～T033 | `server/src/model/facade/{sys_role,sys_menu}.rs`、`server/src/handler/{role,menu,common}.rs`、★`server/src/envelope.rs`（名冊案期望＋`PageRes` doc）、★`server/tests/contract.rs`、★`server/src/model/facade/test_kit.rs`（號段登記）、★`server/tests/common/mod.rs`（號段自持） | rust-api commit→pin bump＋generate |
| U7 | T034～T044（T044 主線） | `server/src/handler/{role,common,system_settings}.rs`、`server/src/handler/{mod,throttle}.rs`（僅 doc）、★`server/src/handler/ip_rule.rs`（測試射程＋檔頭 doc 重評句與域數句）、`server/src/model/facade/{sys_role,sys_user_role}.rs`、`server/src/model/{audit.rs,facade/sys_operation_log.rs}`（僅 doc）、`server/src/error.rs`、★`server/tests/contract.rs`、★`server/tests/authz_entrypoint_lint.rs`、★`server/src/model/facade/test_kit.rs`、★`server/tests/common/mod.rs`、★**i18n 四處**＝`base-web/src/locales/langs/{en-us,zh-cn,zh-tw}.ts`＋`base-web/src/typings/app.d.ts`（僅 backend 節；T002 後）；限定式（主線）：`.specify/memory/constitution.md`（T044 變異自證） | 兩子庫 commit→外層一顆雙 pin bump（msg-key-gate 兩側同批）＋generate |
| U8 | T045～T053 | `server/src/handler/{menu,common}.rs`、★`server/src/handler/ip_rule.rs`（僅測試射程）、★`server/src/handler/route.rs`（僅 doc）、`server/src/model/facade/sys_menu.rs`、`server/src/model/{audit.rs,facade/sys_operation_log.rs}`（僅 doc）、`server/src/error.rs`、★`server/tests/contract.rs`、★`server/tests/authz_entrypoint_lint.rs`、★`server/src/model/facade/test_kit.rs`、★`server/tests/common/mod.rs`、★**i18n 四處**（僅 backend 節） | 兩子庫 commit→外層一顆雙 pin bump＋generate |
| U9 | T054～T060 | `server/src/handler/menu.rs`、`server/src/model/facade/sys_menu.rs`、`server/src/model/{audit.rs,facade/sys_operation_log.rs}`（僅 doc）、`server/src/error.rs`、★`server/tests/contract.rs`、★`server/src/model/facade/test_kit.rs`、★`server/tests/common/mod.rs`、★**i18n 四處**（僅 backend 節） | 兩子庫 commit→外層一顆雙 pin bump＋generate |
| U10 | T061～T065 | `server/src/handler/{menu,role}.rs`（僅測試模組）、`server/src/auth/enforce.rs`（僅測試模組）、★`server/src/model/facade/test_kit.rs`（號段） | rust-api commit→pin bump＋generate |
| U11 | T066～T070 | `base-web/src/typings/api/rev6-{role,menu}-admin.d.ts`（新）、`base-web/src/service/api/rev6-{role,menu}-admin.ts`（新）、`server/tests/wire_schema.rs`、`server/tests/fixtures/wire-schema.json`（★只由 extract 產出）、★`server/src/handler/{role,menu}.rs`（僅 DTO／抽取器可見性）、`tools/wire-schema.py` | 兩子庫 commit→外層一顆雙 pin bump（wire-schema 兩側同批）＋工具同顆＋generate |
| U12（★T002 硬序） | T071～T076 | `base-web/src/components/advanced/table-header-operation.vue`、`base-web/src/views/manage/role/{index.vue,modules/role-operate-drawer.vue,modules/role-search.vue}`、`base-web/src/locales/langs/{en-us,zh-cn}.ts`（僅 `page:` 樹）、`base-web/src/typings/app.d.ts`（僅 `Schema.page`）、★`server/tests/wire_schema.rs`（T069 復跑時） | base-web commit→外層 pin bump（復跑 T069 時雙 pin 同顆）＋generate |
| U13（★T002 硬序） | T077～T082 | `base-web/src/views/manage/menu/{index.vue,modules/menu-operate-modal.vue}`、`base-web/src/typings/components.d.ts`（★只由 unplugin 重算）、`base-web/src/views/manage/ip-rule/index.vue`、`base-web/src/locales/langs/{en-us,zh-cn}.ts`（僅 `page:` 樹）、`base-web/src/typings/app.d.ts`（僅 `Schema.page`）、★`server/tests/wire_schema.rs`（T078 復跑 T069 時） | base-web commit→外層 pin bump（雙 pin 如有）＋generate |
| U14 | T083～T087（T087 主線） | `server/tests/{wire_i64_guard_lint,test_module_tail_lint}.rs`、★`server/tests/common/mod.rs`、★`server/tests/contract.rs`、`server/src/{envelope,main,router}.rs`＋`server/src/handler/{common,ip_rule,throttle}.rs`＋`server/src/handler/auth/{login,refresh}.rs`＋`server/src/ipgate/mod.rs`（皆僅 docstring＝T084 十二支腿補指）、`server/src/model/facade/test_kit.rs`（僅 `tests` 子模組＝T086）、`docs/ops/reference-src/trust-model-config.md`（僅 toml 區塊） | rust-api commit→外層 pin bump＋reference-src 同顆＋generate |
| U15 | T088 | `tools/walkthrough-baseline.py`、`docs/ops/RUNBOOK.md`（§9c＋§12 walkthrough-baseline 列） | 外層工具 commit＋generate |
| U16 主線 | T089～T092 | `docs/arc42/decisions/ADR-00045-*.md`（草稿）、`docs/ops/BACKLOG.md`（僅 BL-00045 errata 如需）；走查紀錄與基準檔住工作區；限定式：dev 庫走查自建列（restore 還原） | 外層 commit＋generate |
| U17 | T093（主線、先行）；T094～T099；T100～T103 | T093：`docs/arc42/decisions/ADR-{00045,00046,00040}-*.md`、`errata ADR-00040` 現算之現在式面、對沖註三處所在檔（活書 06／11、RUNBOOK §16.1）；T094～T099：`docs/arc42/{04,05,06,08,10,11,12}-*.md`、`docs/ops/RUNBOOK.md`、`docs/ops/reference-src/{schema-definition,trust-model-config,code-gate-contracts}.md`、`deploy/trust-model.dev.toml`、`docs/ops/BACKLOG.md`、`errata` 現算命中之現在式面（含 rust-api 測試 doc）；T100～T103：`docs/ops/events.jsonl`；限定式：T101 各反例暫改檔（當場還原） | 三段：T093 單獨一顆外層 commit；治理顆（T094～T099、雙 pin 如有）＋generate；收攏顆（T100～T103）＋generate；final holistic review 輸入 |

★**派發序**（依相依；R18 之 U3～U5 重排）：U0→U1→U2→U3（測試基建）→U4（域鎖與歸檔）→U5（判定面同步）→U6→U7→U8→U9→U10→U11→U12→U13→U14→U15→U16→U17（T093 先行）。全部施工單元排在 T003 之後；U7～U9 之 locale 半與 U12／U13 另受 T002 硬閘（U0 在序列上先於一切）。
★**單元序不可並發的共用檔**（同檔單元不並發）：`router.rs`／`tests/contract.rs`（U1 立 17 case 後逐單元充實）、`error.rs`＋三檔 locale＋`app.d.ts`（U7 10 鍵→U8 12 鍵→U9 2 鍵）、`facade/{sys_menu,sys_role,sys_casbin_archive,mod,test_kit}.rs`、`handler/{role,menu,common}.rs`、`envelope.rs`（U2 立名冊、U6 改期望）、`sys_ip_rule.rs`＋`ipgate/mod.rs`＋`handler/ip_rule.rs`（U2；`handler/ip_rule.rs` 另於 U7／U8 改 degraded 射程測、U7 改檔頭 doc）、`tests/authz_entrypoint_lint.rs`（U5 立空冊、U7／U8 擴名冊）、`tests/common/mod.rs`（U3 計畫→U5 數量句→U6～U9 號段自持→U14 數量句）、`model/{audit.rs,facade/sys_operation_log.rs}` doc（U7→U8→U9）、兩語 locale `page:` 樹與 `app.d.ts` `Schema.page`（U12→U13）。
★**每單元邊界主線動作**（六步序、不入 agent 清單）：①復核 report（逐項 grep、`errata` 復掃）→②load-bearing 自驗（容器內 rc＋`docsync lint`）→③落帳（BACKLOG／LESSONS／tasks 勾選／ADR）→④子庫 commit→⑤`git add <子庫>`→`generate`→`git add` 生成物→⑥外層 commit（pin bump）→派下一支前逐條問「它 import／呼叫／宣告的東西存在嗎」（RL-0008）。★review 輪空 blockers 先讀 `reason` 與 journal 判該輪審查確有執行（RL-0079）。

## Dependencies & Execution Order

- **Phase 1**：T001 → T002（★硬閘、user 親決）→ T003（★施工前提閘、user 親決）。
- **Phase 2**：U1（T004→T005→T006；T007／T008 可與 T006 分派）→ U2（T009→T010；T011／T013 可分派；T012 待 T011〔同檔 `sys_ip_rule.rs`〕）→ U3（T014→T015→T016→T017〔主線演練〕）→ U4（T018→T019）→ U5（T020→T021；T022／T023／T024 可與 T021 分派）。
- **Phase 3（U6）**：依 Phase 2；T025／T026／T027 測試先寫（同動 `contract.rs`、序列）→ T028 →｛T029→T030（role）｜T031→T032→T033（menu）｝兩半可分派（T029／T031 標 [P]；T030 另依 T028；T032 同批改 `envelope.rs` 名冊期望與 `PageRes` doc）。
- **Phase 4（U7）**：依 U6（`db_status_to_wire` 等共用件、`RoleRecord`）；T034（鍵常數）→ T035～T037 測試先寫 → T038／T039（可分派）→ T040 → T041 → T042；T043（base-web 側）可與 T040～T042 分派 → T044（主線）。
- **Phase 5（U8）**：依 U7（`common.rs` 之 `tristate`、`authz_entrypoint_lint` 名冊形、msg 名冊形）；T045（鍵常數）→ T046～T049 測試先寫 → T050 → T051 → T052 → T053。
- **Phase 6（U9）**：依 U8（`sys_menu.rs` 寫面狀態機、`biz.menu.*` 12 鍵）；T054（鍵常數）→ T055／T056 → T057 → T058 → T059 → T060。
- **Phase 7（U10）**：依 U7～U9（七支進域寫端與觸發接線全在）；T061／T062 可分派 → T063 → T064 → T065。
- **Phase 8（U11）**：依 U6～U9（DTO 全在）；T066／T067 可分派 → T068 → T069 → T070。
- **Phase 9**：U12 依 U11（wrapper 與型別）＋T002；T071 → T072～T074（同目錄三檔、單一 implementer 序列收邊）→ T075 → T076。U13 依 U12（`table-header-operation.vue` prop、locale 插入點）；T077 → T078（同檔）→ T079 → T080 → T081 → T082。
- **Phase 10**：U14 依 U7／U8（BL-00111 射程需 role.rs／menu.rs 之名冊字面）；T083／T084／T086 可分派、T085 待 T084（數量句現算）→ T087（主線）。U15 與 U14 檔域不交、可對調次序，唯須在 U16 之前。
- **Phase 11（U16）**：依 U13＋U15；T089→T090→T091→T092（同一走查窗、序列）。
- **Phase 12～13（U17）**：依 U16（ADR-00045 定稿）；T093（主線、先行、獨立 commit）→ T094／T095／T096／T098 可分派 → T097 → T099 → T100 → T101 → T102 → T103（全序列）。U17 內 agent 派發一律於 T093 落地之後。
- 阻斷型：容器內 build 紅＝blocked 升主線；T069／T078 需 base-web 容器 qs 可跑；T079 需 unplugin 重算可跑；T089～T092 需 host 瀏覽器 9229 與 rev5 對照 stack（22080）在跑；任一單元需動允許檔案清單外檔案＝依防呆④分值升級、絕不擅改；T082 塊數不等＝停手升級（user 定）。

## Parallel Opportunities（[P]＝檔域不相交可分派、cargo 序列）

- **U1**：T007（外層 python）／T008（throttle doc）可與 T006 分派。**U2**：T011／T013 可分派（facade/mod.rs vs config.rs＋obs.rs＋middleware 測試）。**U5**：T022（obs）／T023（新 lint crate）／T024（外層 rules.yml）可與 T021 分派。
- **U6**：role 半（T029→T030）與 menu 半（T031→T033）可分派給兩位 implementer（`contract.rs` 與 `handler/common.rs` 由單一 implementer 收邊）。
- **U7**：T039 facade 與 T038 common 可分派；T043（base-web）可與 T040～T042（rust-api）分派、同顆外層 commit。**U8**：T049（contract 常量路由案）可與 T047／T048 分派（與 T046 同檔序列）。
- **U10**：T061（menu.rs 測試）／T062（role.rs 測試）可分派。**U11**：T066／T067 可分派。**U14**：T083（wire_i64_guard_lint）／T084（新 lint＋`tests/common`＋九檔 docstring）／T086（`test_kit.rs` tests＋reference-src）三支檔域不交、可分派；T085（`contract.rs`）待 T084 後。**U17**：T094／T095／T096／T098 可分派。

## Parallel Example: User Story 1（U7）

```text
# U6 已落 RoleRecord／db_status_to_wire；U3 已落五表守衛、face_allows 與號段表；T034 已落 10 支鍵常數
Task: "T038 handler/common.rs tristate＋BL-00113 重評＋預告句改現在式＋system_settings.rs 改引"
Task: "T039 model/facade/sys_role.rs 寫面＋sys_user_role.rs count_by_role／is_member"
# 其後 handler/role.rs（T040→T041→T042）由單一 implementer 序列收邊；
# T043 之 i18n 四處（base-web）可與 rust-api 側分派、同顆外層 commit 雙 pin bump
```

## Implementation Strategy

- **MVP**＝Phase 1＋Phase 2（U1～U5）＋U6 讀端＋**US1 後端（U7）**：角色全生命週期經 API 端到端可用（quickstart §1／§2）、選單域序列化與判定面同步底座在場；UI 半（U12）於 wire 面（U11）後補上。
- 增量：US2 新增／編輯（U8）→ US2 刪除＋US3 回收桶（U9）→ US4 零繼承與機器證收齊（U10）→ wire 面（U11）→ 前端兩頁（U12／U13）→ 體檢＋走查工具（U14／U15）→ CDP 三方對照（U16）→ 治理＋全量閘（U17）；每單元收尾六步序、單元一支接一支連續跑完。
- 收刀（★不在本清單）：final holistic review → `superpowers:finishing-a-development-branch`（push／merge 需 user 當次同意）→ 收刀簿記三步（`feature_close`：`adrs` 六支、`backlog_done` 19 條〔BACKLOG 同批刪列〕、條文改寫 3 條、`backlog_add` 零、`arch_impact` 以 `git diff --stat <merge-base>..HEAD -- docs/arc42/` 現算、notes 記淨流量值與揭露型／新欠型分型；NOTES 下一步→授權治理刀；generate）→ `close_bookkeeping` perf 第四步（簿記 commit 落地後量牆鐘、隨下一顆 commit 入帳）。

## 需求追溯（FR-079：FR／SC／US 驗收場景／backlog_done → 承載 task；無承載者即紅）

**FR**：

| FR | 承載 | FR | 承載 | FR | 承載 |
|---|---|---|---|---|---|
| 001 | T005 T006 T007 T100 | 028 | T026 T032 | 055 | T010 T025 T026 T027 T094 |
| 002 | T001 T087 T100 | 029 | T047 T048 T051 T052 | 056 | T009 T026 T032 T094 |
| 003 | T006 | 030 | T047 T048 | 057 | T069 T070 |
| 004 | T034 T035 T043 T045 T046 T053 T054 T060 | 031 | T047 T048 | 058 | T071～T082 |
| 005 | T025 T026 T027 T068 | 032 | T048 T052 | 059 | T066 T067 T079 |
| 006 | T028 T036 T047 T048 | 033 | T055 T057 T058 | 060 | T077 T078 T079 |
| 007 | T036 T038 T048 | 034 | T055 T057 T058 | 061 | T072 T073 T074 |
| 008 | T036 T037 T047 T048 T055 T056 | 035 | T027 T033 | 062 | T080 T082 |
| 009 | T035 T037 T046 T055 T056 | 036 | T056 T059 | 063 | T071 T089 |
| 010 | T025 T029 T030 | 037 | T035 T036 T055 | 064 | T043 T053 T060 T075 T081 |
| 011 | T025 T030 | 038 | T019 | 065 | T079 T082 |
| 012 | T035 T036 T040 | 039 | T019 T036 | 066 | T072 T073 T077 T079 |
| 013 | T036 T040 | 040 | T087 | 067 | T011 T012 T025 T029 |
| 014 | T036 T039 T041 | 041 | T018 T094 | 068 | T013 T096 |
| 015 | T035 T036 T041 | 042 | T064 | 069 | T010 T080 T093 T094 T095 T096 T097 T099 |
| 016 | T036 T041 T064 | 043 | 全程紀律⑦ T041 T051 T052 T058 T059 T064 | 070 | T014 T015 T016 T017 |
| 017 | T037 T042 | 044 | T064 | 071 | T068 |
| 018 | T048 T052 T079 | 045 | T036 T047 T048 T055 T056 | 072 | T083 |
| 019 | T047 T048 T050 | 046 | T020 T021 | 073 | T084 |
| 020 | T047 T048 T050 T056 | 047 | T020 T063 | 074 | T016 T028 T038 T041 T052 T068 T085 T086 |
| 021 | T047 T048 T049 T056 T090 T102 | 048 | T020 T021 T022 T024 | 075 | T002 T044 T082 |
| 022 | T026 T031 | 049 | T003 T095 | 076 | T002 T003 T093 |
| 023 | T061 | 050 | T036 T048 T055 T065 | 077 | T088 T094 T095 T096 T097 T099 |
| 024 | T048 T053 T055 | 051 | T062 | 078 | T087 T098（＋收刀簿記） |
| 025 | T026 | 052 | T021 T023 T036 T048 T055 T065 | 079 | T100 T101 T102 T103 |
| 026 | T026 T032 | 053 | T020 | | |
| 027 | T026 T032 T068 | 054 | T009 T010 T025 T026 T027 | | |

**SC**：SC-001＝T005 T006 T100｜SC-002＝T035 T043 T046 T053 T060 T100｜SC-003＝T036 T037｜SC-004＝T026 T047 T048 T055 T056｜SC-005＝T036 T047 T048 T055 T056 T064｜SC-006＝T021 T023 T036 T048 T055 T063 T065｜SC-007＝T056 T061 T062｜SC-008＝T009 T010 T025 T026 T027 T032｜SC-009＝T019 T036 T048｜SC-010＝T010 T011 T012 T013 T038 T080｜SC-011＝T089 T090 T091 T092｜SC-012＝T002 T044 T076 T082 T100｜SC-013＝T068 T069 T070 T083 T084｜SC-014＝T014 T017 T088 T102｜SC-015＝T100 T102｜SC-016＝收刀簿記（T098 預備）。

**US 驗收場景**：

| US | 場景 → 承載 |
|---|---|
| US1 | AS1＝T025 T030 T069 T072 T089｜AS2＝T035 T036｜AS3＝T036｜AS4＝T036｜AS5＝T036｜AS6＝T035 T036｜AS7＝T036 T062 |
| US2 | AS1＝T026 T077｜AS2＝T026 T079 T090｜AS3＝T047｜AS4＝T047 T048｜AS5＝T047 T048｜AS6＝T048｜AS7＝T048｜AS8＝T048｜AS9＝T055｜AS10＝T055｜AS11＝T055｜AS12＝T048｜AS13＝T048 |
| US3 | AS1＝T027 T078 T091｜AS2＝T056｜AS3＝T056｜AS4＝T056｜AS5＝T056 |
| US4 | AS1＝T036 T048 T055 T065｜AS2＝T021｜AS3＝T061｜AS4＝T062｜AS5＝T063｜AS6＝T065 |
| US5 | AS1＝T037｜AS2＝T037 |
| US6 | AS1＝T002 T100｜AS2＝T010｜AS3＝T013｜AS4＝T010 T080 T092｜AS5＝T038｜AS6＝收刀簿記（T098 預備） |

**backlog_done 19 → 承載**：BL-00082＝T013｜BL-00095＝T010 T080｜BL-00096＝T012｜BL-00098＝T002｜BL-00105＝T068｜BL-00106＝T083｜BL-00107＝T083｜BL-00109＝T070｜BL-00110＝T016｜BL-00111＝T084｜BL-00112＝T068｜BL-00113＝T038｜BL-00115＝T086｜BL-00116＝T010｜BL-00117＝T071 T080｜BL-00118＝T002｜BL-00119＝T002｜BL-00123＝T085｜BL-00125＝T093。條文改寫 3（BL-00120／BL-00093／BL-00045）＝T098（BL-00120 之 ADR-00040 半＝T093）。

## Notes

- [P]＝檔域不相交可分派；★cargo 執行一律序列。
- 測試先確認紅再實作；每單元收尾兩段式 commit（子庫 commit→外層 bump pin）。
- 任一 checkpoint 皆可停下獨立驗收該單元之交付面。
- 避免：在 T002 accepted 前動 base-web 既有檔（含 locale backend 節）、在 T003 前啟施工單元、單側 pin bump 讓兩側閘分叉、以交易 rollback 代替序列還原、facade 內自取域鎖或 clamp size、對現役判定面就地 `load_policy`、測試直呼 `.enforce(` 或持判定面讀鎖跨寫端呼叫、呼叫同步時持判定面讀鎖、把觸發寫成「成功即觸發」、locale 新鍵插在物件末項之後、新增型圈界漏 `+` 尾綴、把 rev5 清單 A 增量帶回、CDP 寫入步驟動 seed 列、動過 `casbin_rule` 後未重啟 rust-api 即 diff。
