# Contract — 本刀新增拒因鍵（`biz.role.protectedRevoke`／`biz.role.protectedGrant`／`biz.policy.notRestorable`）

> 本檔凍結本刀三支新拒因鍵之鍵名、發出點、語意要求、跨端閘兌現面與落地時序（`msg_key` 常數名照引 data-model §13）。★權威分工：鍵集＝`rust-api/server/src/error.rs` 之 `MSG_KEYS`（鍵數之單一來源＝其型別長度；碼註、標記註解與文件凡需提及鍵數者一律指向 `MSG_KEYS`／跨端閘輸出、不寫實數＝ADR-00039 決定 3）；譯文之家＝三檔 locale 各自之 `backend` 子樹（ADR-00039 決定 2）。
> ★本檔不立譯文表（ADR-00039 決定 2；005 刀同名契約同形）：譯文實作時直接寫進三檔 locale。譯文出處＝en-us／zh-cn 逐字取 rev5 base-web `src/locales/langs/{en-us,zh-cn}.ts` 之 `backend.biz` 同鍵（比照 ADR-00050 決定 1 之判準「純換句話說者逐字對齊 rev5」——三鍵之判定面相對 rev5 皆無語意延伸，見 §1 語意要求），使 spec SC-010 之 toast 文案逐項全等、CDP toast 基準即該出處；zh-tw 以 rev5 `src/locales/langs/zh-tw.ts` 同鍵為底（rev6 自有檔、不接 runtime、不在 CDP 對照面＝ADR-00050 決定 1〔續行 ADR-00049 決定 1〕）。
> 一切拒因皆 `2222`＋純 i18n key、一因一鍵、零攜參（spec FR-004）；13 碼矩陣零觸碰、`AppError` 九變體零新增。wire 端點行為見 `contracts/wire-authz-governance.md`、`contracts/wire-policy-archive.md`；閘與名冊之施工面見 `contracts/code-gates.md`。

## §1 新鍵三支

| 鍵 | `msg_key` 常數（新建） | 發出端點與腿 |
|---|---|---|
| `biz.role.protectedRevoke` | `BIZ_ROLE_PROTECTED_REVOKE` | updateRoleMenu／updateRoleButton／updateRoleEndpoints：取得操作者、`FOR UPDATE` 鎖標的角色列（活性）之後，鎖內重算之撤銷集〔（現況 ∩ 候選集）−期望全集〕觸及受保護授權列（`casbin_rule.protected=TRUE`）＝整批拒；於任何寫入之前判定、三維皆適用；updateRoleEndpoints 先判本腿再判封死（ADR-00066 決定 2／決定 8、ADR-00064 決定 3） |
| `biz.role.protectedGrant` | `BIZ_ROLE_PROTECTED_GRANT` | 唯 updateRoleEndpoints：撤銷腿通過後，標的角色代碼≠R_SUPER 且新授集〔（期望全集 ∩ 候選集）−現況〕∩ 封死集 ≠ ∅＝整批拒；標的為 R_SUPER 或新授集為空時不查封死集（ADR-00064 決定 1～決定 3） |
| `biz.policy.notRestorable` | `BIZ_POLICY_NOT_RESTORABLE` | restorePolicy：鎖歸檔列查無（含 body 缺席或壞形收斂之預設識別），或固定序重驗之 ①原因屬不可復原集 ②來源角色非同實例（來源角色 id 為 NULL、已軟刪、或現役同代碼角色為另一實例）③標的角色非 R_SUPER 且（路徑,方法）∈ 封死集 ④（路徑,方法）不在路由表 任一腿拒；⑤角色停用不擋（五腿全文＝ADR-00065 決定 3、拒因同鍵＝決定 7）；歸檔列保留、零稽核、不同步 |

- 常數命名沿 `pub mod msg_key` 現行 `BIZ_<域>_<鍵>` 形（例既有 `BIZ_ROLE_NOT_FOUND`、`BIZ_MENU_RESTORE_CONFLICT`）；常數名之家＝data-model §13「新建件名冊」，本表照引。

**語意要求**（譯文須傳達；三鍵照 rev5 字面而不失實之判讀）：
- `protectedRevoke`：期望全集會撤掉受保護之授權 → 整批未寫入。三維共用一鍵、不分維；撤銷射程限候選集（ADR-00066），候選外之現役列不入撤銷集、不會觸發本鍵。seed 之受保護授權列皆屬 R_SUPER，故實務上只有「取消 R_SUPER 名下受保護項」會觸發（前端以受保護旗標鎖定、只能繞過 UI 送出）。
- `protectedGrant`：受保護端點只能由超級管理員角色持有。只在端點維發出——v2＝`menu` 之受保護授權列不在封死射程（ADR-00064 決定 5），選單維授予永不發本鍵。
- `notRestorable`：涵蓋「該歸檔列不存在」與「重驗任一腿拒」兩情形（同一鍵、不分腿；前端對可復原旗標為 false 之列已停用復原鈕，本鍵為後端最終防線）。★rev6 不把 `unique_key_sea_orm_adapter` 衝突收窄為本鍵——同角色之授權寫入者皆持該角色列鎖、NoOp 判定在鎖內，同鍵 INSERT 於生產路徑結構不可達，任何 `DbErr` 經本域 `db_failure` 回 `5000`（ADR-00065 決定 10）；與 rev5（23505 競態亦回本鍵）之差異記 research 之 rev6 差異點。

## §2 既有鍵復用（零新增）

| 鍵（碼） | 本刀發出點 |
|---|---|
| `biz.role.notFound`（`2222`） | 三支現況讀端與三支寫端之角色不存在或已軟刪（角色鍵一律 `id`；query 或 body 缺席、壞形收斂之預設 id 亦同——寫端 body 經 `common::json_or_default` 收斂、讀端 query 沿 `RoleHomeQuery` 之壞形收斂形；★MUST NOT 演成「空期望集＝全撤」＝spec FR-007） |
| `system.forbidden`（`5003`） | 非 R_SUPER 呼叫十支端點（seed 政策列 32／33、52～57、70／71 只授 R_SUPER；spec FR-003） |
| `system.internal`（`5000`） | 寫端請求上下文缺席（操作者取得先於一切守門；spec FR-006）；任何 `DbErr`（含治理域按鈕碼聯集遇壞形 `buttons` 時 `sys_menu::button_codes_of` 回之錯誤——fail-loud、不跳過） |
| `common.success`（`0000`） | 三維寫端 Applied（含空 diff）、restorePolicy Applied 與 NoOp、本刀六支讀端 |

getAllButtons／getAllEndpoints／getArchivedPolicies 零業務拒因：分頁與篩選之壞形一律收斂預設、維度未知值靜默不濾（spec FR-008、FR-026）。

## §3 後端名冊與構造形（`rust-api/server/src/error.rs`）

- `pub mod msg_key` 新增 §1 三常數（新建；字面恰如 §1）；★字面只住本模組。
- `pub const MSG_KEYS: [&str; 43]` → `[&str; 46]`：尾端追加、既有序不動；追加序＝落地單元序（同單元落地者依 §1 表序）；元素一律 `msg_key::NAME` 常數引用。
- 同單元同批改：`msg_keys_roster_is_pinned_and_unique`（逐鍵釘值陣列尾補三字面、doc 批次句補一段）、`biz_keys_are_in_roster`（常數迴圈補三支、doc 列舉補三鍵）、`MSG_KEYS` doc 之批次句（沿既有「005 刀 U7 之 role 十鍵」形以刀名形補記）、`pub mod msg_key` doc 之構造點句（role 兩鍵構造點住 `handler::role`、policy 一鍵住新建 `handler::policy_archive`）。
- 構造點一律 `AppError::Biz(Cow::Borrowed(msg_key::NAME))` 常數形。rev5 於構造點直書字面（rev5 rust-api `server/src/handler/role.rs` 之 `map_reject_cause`、`server/src/handler/policy_archive.rs` 之 `restore_policy`）＝翻案不帶回（brainstorm §1 承襲盤點末列⑤；research 差異點同載）。★`tools/msg-key-gate.py` 斷言 2 兩形皆收、攔不到字面形 ⇒ 落鍵單元出口另以 `git -C rust-api grep -n 'Cow::Borrowed("' -- server/src` 斷言命中只有 `error.rs` 測試模組之矩陣列（現況恰該一處），新構造點不增命中。

## §4 跨端閘與名冊雙向閘

- **msg-key-gate 斷言 1**（三檔 `backend:` 子樹逐檔與 `MSG_KEYS` 雙向全等、無白名單）：`biz.role` 子樹尾補 `protectedRevoke`／`protectedGrant`；`biz` 下新開 `policy: { notRestorable }`（建議接在 `menu` 之後＝依刀序；rev5 置於 `menu` 與 `role` 之間——位置不影響閘、CDP 零差）。en-us／zh-cn 落在既有 `BASE-WEB-I18N-WIRING(ii)+ 003-auth-session` 圈界塊內、zh-tw 落在其 `backend` 子樹內：不增塊、零 `原行:`；`backend: {` 獨佔一行之右源錨行不動。
- **`src/typings/app.d.ts` backend 型節**（既有 `BASE-WEB-I18N-WIRING(iii)+ 003-auth-session` 圈界塊內）：`role` 補兩鍵之 `string` 型、`biz` 下新開 `policy: { notRestorable: string }`。en-us／zh-cn 兩檔標型 `App.I18n.Schema` ⇒ 缺鍵或多鍵由 `pnpm typecheck` 攔；zh-tw 未標型、只由跨端閘守。
- **斷言 2**（Biz 構造點守衛）：新構造點住 `handler/role.rs` 與新建 `handler/policy_archive.rs` 之生產區，須為 `Cow::Borrowed(msg_key::NAME)` 且解出之鍵 ∈ `MSG_KEYS`。
- **斷言 3**（前端 msg 字面消費點名冊）：`FRONTEND_MSG_CONSUMERS` 不動（仍恰 1 項）——三鍵只經共用攔截層之純 key toast 呈現（spec FR-034）、前端零字面消費；安全前綴集不變（三鍵皆在既有頂層 `biz` 下）。
- **名冊雙向閘**（`rust-api/server/tests/contract.rs` 之 `msg_roster_every_key_has_an_emitter`；免 DB 面 ∪ 真 seed app 面去重後＝`MSG_KEYS`）：三鍵須於真 seed app 面實際發出。新建本刀觀察段（形同 `role_msgs_real_db`／`menu_msgs_real_db`、併入 `observed_msgs_real_db`；本案 doc 之逐刀批次句同補）：
  - 前置：Super 票、經 `app_with_peer` 帶對端（寫端先取操作者上下文）；先 arm `common::RoleMenuDomainWriteGuard`（含本刀擴面之被撤授權列回補＝`contracts/code-gates.md` §5.1）；自建角色以 `plant_contract_role` 植於 `common::CONTRACT_ROLE_ID_RANGE` 號段、代碼帶段標記（應被拒之樣本亦帶＝RL-0069）；逐發斷言 `(code, msg)`。
  - `protectedRevoke`：自建角色名下以 raw SQL 直植一列 `protected=TRUE` 之選單維授權列——v1 MUST 為治理域內之選單路由名（候選外之列不入撤銷集、守門 vacuous）、`created_by` 非 NULL、v3～v5 填 `''`（LL-00043）——再以該角色 `id`＋空期望全集打 updateRoleMenu ⇒ 拒。★不打 seed 受保護列（形同 `menu_msgs_real_db` 之「不打 seed 受保護列」）。
  - `protectedGrant`：零端點授權之自建角色，以期望全集＝{一個封死集成員（例 `POST /systemManage/updateRoleEndpoints`＝seed 政策列 57）} 打 updateRoleEndpoints ⇒ 撤銷集為空、授予腿拒。
  - `notRestorable`：restorePolicy 帶號段內不存在之歸檔 id 一發、body 缺席一發（收斂預設識別）⇒ 皆拒。
  - 段末零寫入復核：段標記角色名下之授權列只剩直植之一列、歸檔表與稽核表於守衛水位窗內零新列。
  - 請求體欄名與形依兩支 wire 契約。

## §5 落地時序

- **同單元同批面**（spec FR-004「新鍵 MUST 隨首個發出它的單元落地」）：①`msg_key` 常數＋`MSG_KEYS` 尾端追加＋兩支名冊測試＋doc 批次句 ②三檔 locale `backend` 子樹 ③`app.d.ts` backend 型節 ④contract 真 seed 發出案。兩子庫各自 commit 後，**兩 pin 同一顆外層 commit**——pre-commit msg-key-gate 段於任一側 pin bump 即比對兩側工作樹、submodule-sync 段要求兩側閘面無未 commit 改動。
- **首個發出單元**（以描述指稱、單元號以 tasks 為準）：`protectedRevoke`＝首個落地之三維授權寫端單元（選單維／按鈕維入域寫端或端點維寫端中先落地者）；`protectedGrant`＝端點維寫端單元（封死掛點之一）；`notRestorable`＝授權回收桶端點單元。tasks 合併單元時，鍵隨之同批；讀端與候選讀之單元零新鍵、不觸 locale。
- ★**硬序**：落鍵單元觸及 base-web 既有檔（`en-us`／`zh-cn`／`app.d.ts`）⇒ MUST 排在 ①本刀 U0 之 Amendment（ADR-00063）accepted 之後（spec FR-040⑥）②fork-delta-lint 範圍欄對賬腿落地之後（spec FR-042；`contracts/code-gates.md` §2.1）。brainstorm §3 §4 之單元草案把落鍵之後端單元排在對賬腿之前，依 FR-042 由 tasks 重排（ADR-00063 後果「硬閘解除點」）。
- **出口斷言**（`contracts/code-gates.md` §1.2 之逐檔應有值）：落鍵本身不增塊——`en-us`／`zh-cn` 之 ` START]` 數＝現值 7＋已落地之 (iii)(iv) 塊、`app.d.ts`＝現值 6＋已落地之 (iii)(iv) 塊、三檔 `原行:` 恆 0；`zh-tw.ts` 之 `rev6-inline` 標記仍恰檔頭 1 行。不等即停手升級（ADR-00063 決定二「預估依據」）。
- 射程外：本刀 `page:`／`route:` 樹之新鍵（回收桶頁整節 `page.manage.policyArchive`、抽屜第三鈕一鍵、`route.manage_policy-archive`）非 msg key、不入 `MSG_KEYS` 與本檔——落點與塊數見 `contracts/code-gates.md` §1.2。
