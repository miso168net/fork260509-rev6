# Feature Specification: 006 授權治理——三維授權接真、結構性封死、授權回收桶、島 G 入憲

**Feature Branch**: `006-authz-governance`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "docs/brainstorms/006-authz-governance.md"（階段 0 brainstorm：定稿 `e9f5525`＋grilling 輪寫回 `0f7e514`；理解校正、範圍與承載十一題 Q1～Q11、設計四節、grilling 補題六題 Q12～Q17 皆 user 拍板、首選項皆為建議；主線工程判斷①～⑧為報備、本 spec 直接採用；本 spec 之唯一輸入。該檔 §0 拍板紀錄與工程判斷、§1 rev5 承襲盤點、§2 BACKLOG 觸發項處置、§3 設計四節、§4 憲法九題預答、§5 specify 輸入摘要、§6 隨做隨記為權威來源；rev5 對應刀 `rev5:006-authz-governance` 之 spec 為沿用形藍本、rev6 座標改寫、翻案項以 brainstorm 為準）

> 摘要：把角色頁三顆授權彈窗（選單維／按鈕維／端點維；端點彈窗為新檔、掛於角色抽屜第三鈕）與授權回收桶頁自 demo 殼接成真——**10 支端點**（三維讀寫 6＋候選讀 2＋回收桶 2；ROUTES 39→49、GET 6／POST 4、全為政策保護、seed 皆 protected=TRUE 且只授 R_SUPER），前後端同刀、CDP 對照 rev5 HEAD 驗收。
> 寫入語意＝**全量替換、射程＝候選集**（候選外現役列不撤不授）；**結構性封死**（受保護端點授不出 R_SUPER 以外、受保護授權列撤不掉）；撤銷一律移入授權歸檔、**只有端點維手動撤銷可復原**（不可復原集 3→5）；授予面成功即觸發判定面同步（含空 diff）、兩個已知降級窗入條文。
> 憲法一次 MINOR（1.6.0→1.7.0）：島 G 六條入憲（G6 新立）、§III.2 管理頁 ★ 軌道加用途 (iii)(iv)、併入 BL-00135／BL-00132 兩句、島 H 序言／H1／H2 連動改寫。`MSG_KEYS` 43→46。**零 migration、零 seed 變更**。ADR 九支（plan 期起草）＋收刀前 PATCH Amendment 一支（範圍欄實數化）。
> 連帶面：走查還原工具與測試守衛擴至能補回被撤之 seed 授權列、fork-delta-lint 範圍欄對賬腿、seed-view-gate 新碼面閘；BACKLOG 開放 17 條中 5 條隨本刀收、3 條收窄、同批新記 2 條（本窗淨 −3）。

## Clarifications

### Session 2026-10-01

- Q: 復原時若同一條授權已被重新授予、正在生效（NoOp），這次復原要不要留一筆操作稽核？ → A: 照 rev5 as-built 不留稽核——歸檔列照常消費移除、回成功、不同步、零稽核；「回收桶移除一列而無稽核痕跡」入已知態 ADR⑥（FR-030、Edge Cases、SC-007）。
- Q: 三維現況讀端要不要濾掉候選集外之現役列（rev5 HEAD 之按鈕維與端點維照回全部現役列＝`rev5:ADR 0056`「讀端維持現狀」）？ → A: 只回候選內（「現況 ∩ 候選集」）；與 rev5 HEAD 之分岔登入刻意分岔登記表（UI 零差、wire 列數差）、ADR④ 註明讀端取態（plan 期取證揭出、user 親決；FR-014、US1 AS4）。
- Q: 選單權限彈窗之首頁下拉何時寫入首頁？ → A: 照 upstream 既綁之選值事件與 rev5 HEAD——選值即打首頁寫端、與確定鈕獨立（取消不還原、每次選值各一筆稽核）；spec 原「提交時首頁有變更才寫」之措辭為起草誤植、已改（plan 期取證揭出、user 親決；FR-033、US4 AS2）。
- Q: 切換角色開彈窗時要不要連候選集一起清空？ → A: 照 rev5 HEAD（`rev5:B-129`）只清角色維狀態（勾選、鎖定集、首頁值）；候選集與角色無關、每次開啟重取、成功才覆蓋；spec 原「勾選與候選」之措辭為起草誤植、已改（plan 期取證揭出、user 親決；FR-034④、US4 AS5）。
- Q: 已知態須以實際操作觀察定稿（`rev5:L-046`），但本刀無使用者角色指派寫端、自建角色無帳號可持有——觀察步驟可否對 seed 角色寫入？ → A: 具名例外：僅已知態觀察步驟可對 seed 角色（R_ADMIN／R_USER_COMMON）寫入並以 seed 帳號登入觀察；前後必套走查基準（觀察前 snapshot、觀察後 restore〔本刀擴面後可回補被撤之 seed 授權列、刪回插新列〕＋重啟 rust-api、diff rc 0 證回基準）；其餘走查寫入步驟仍一律對自建角色（plan 期起草揭出、user 親決；Edge Cases、ADR⑥）。
- Q: 走查（真登入、CDP、quickstart 手跑）可否為驗證 seed 授權列回補與超管自救而對 seed 角色寫入（US5 AS2、SC-009、FR-032 原寫「走查或測試」）？ → A: 不擴例外——走查寫入一律對自建角色，第五題之已知態觀察為唯一例外；seed 授權列撤後回補只由整合測試（清理守衛按原 id 回補）與走查工具自測合成案證明，超管自救路徑只由整合測試證明；走查工具之 seed 列回補能力於走查面只由已知態觀察窗承用（analyze 期揭出、user 親決；US2／US3／US5 Independent Test、US5 AS2、SC-009、FR-032、FR-044）。
- Q: 三維寫端 body 合法而缺期望集鍵（或鍵名拼錯）時，視為合法全撤還是壞形？ → A: 壞形——期望集鍵必填；缺鍵或拼錯與 body 缺席／壞形同處置（角色鍵收斂為預設值 → `biz.role.notFound`、零變更），只有明確送空陣列才是合法全撤；與 rev5 as-built（缺鍵＝空集＝全撤）刻意分岔、入登記表（analyze 期揭出、user 親決；US1 AS7、FR-007）。

### Session 2026-10-04

- Q: CDP 三方對照時 22080（rev5 對照環境）側要不要也以自建角色寫入（原寫兩側各自建、22080 自建殘列依 rev5 走查還原契約處置）？ → A: 22080 全程唯讀——實查 rev5 走查工具無 restore 子命令、其還原契約之清理為對 rev5 庫手動 psql 且全量測試步會寫 rev5 樹；同 004 刀 U12／005 刀 U16 先例只登入觀察；須寫入才可比之三類（彈窗確定後 toast、回收桶列與復原流程、首頁下拉選值）改 32080 單邊實測＋rev5 碼面靜態對賬、判定欄註明（CDP 三方對照單元開跑前揭出、user 親決；SC-010、FR-053）。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 超管三維授權治理（選單／按鈕／端點） (Priority: P1)

超級管理員在角色抽屜開啟「選單權限」「按鈕權限」「端點權限」三顆彈窗，看到該角色**現況已授集**（受保護項鎖定、不可取消）與**候選全集**（與判定面同源），勾選後提交**期望全集**——系統以候選集為射程比對現況、導出撤銷集與新授集，同一交易落地並寫一列操作稽核；撤銷集觸及受保護授權列時整批拒、零變更。提交成功後 API 判定即時生效；被改角色之使用者，其側欄選單與按鈕顯隱於下次載入頁面時更新。

**Why this priority**: 本刀本體；rev6 至今角色授權只能靠 seed，005 刀已知態（授權彈窗假勾選、新建或復原之選單與新按鈕碼無人持有）之解除點皆在此。

**Independent Test**: 以 Super 登入 → 新增一個角色 → 三顆彈窗各勾一組 → 提交 → 以測試資料直種指派後，驗該角色之選單可見集、按鈕碼、端點判定皆依勾選生效；再撤銷其中一項端點 → 判定即刻失效、撤銷列出現在授權回收桶；試圖取消 R_SUPER 名下任一受保護項 → 整批拒、零變更。

**Acceptance Scenarios**:

1. **Given** 角色 R 現有選單維授權 {a,b}、候選集＝治理域選單（未刪含停用），**When** 提交期望全集 {b,c}，**Then** 撤銷 a（移入授權歸檔、reason＝`menu_revoke`）、新授 c、b 不動；同交易一列稽核（`update`）；回應帶實際生效集合；commit 後判定面同步一次。
2. **Given** 期望全集與現況相同，**When** 提交，**Then** 回成功（Applied、空 diff）、零授權變更、稽核一列、仍觸發判定面同步（授予面刻意例外）。
3. **Given** 期望全集含候選外之識別（已刪或不存在之選單、不在聯集內之按鈕碼、不屬端點維候選集之端點——未註冊、非政策保護或方法不屬 HTTP 方法白名單），**When** 提交，**Then** 該項靜默略過（orphan skip）、不產生孤兒授權、回應之生效集合不含它。
4. **Given** 角色 R 名下有候選外之現役授權列（例：R_SUPER 之 seed 端點列 `/systemManage/updateUserSessionPolicy` 尚未上線），**When** 以任何期望全集提交，**Then** 該列不撤、不授、不出現於現況讀端與回應生效集合（射程＝候選集）。
5. **Given** 停用中之選單 S 與角色 R 對 S 之既有授權，**When** 以含 S 之期望全集提交，**Then** S 之授權不被撤銷（停用≠撤銷）；**When** 候選集或其映射誤用顯示域（不含 S），**Then** 必配負向測試證明兩種失效形皆為禁止形：候選半誤用＝S 之授權不被撤而自生效集合與現況讀端消失、此後不可治理；映射半誤用＝停用被靜默升級為撤銷（負向測三斷言：撤銷列數＝0、生效集合含 S、現況讀端含 S；ADR④）。
6. **Given** 角色 R 名下有一列受保護授權列（seed 中皆屬 R_SUPER），**When** 提交之期望全集缺該項（撤銷集觸及受保護列），**Then** 整批拒（`2222`＋`biz.role.protectedRevoke`）、零變更、零稽核、零判定面同步；**Given** R_SUPER 名下之非受保護列，**When** 取消並提交，**Then** 照常撤銷（brainstorm Q14）。
7. **Given** 合法之角色鍵與空的期望全集，**When** 提交，**Then** 為合法全撤——候選集內之現役列全數撤銷歸檔（仍受第 6 款撤銷拒約束；Q15）；**Given** body 缺席或壞形（含期望集鍵缺席或鍵名拼錯；Clarifications 第七題），**When** 提交，**Then** 角色鍵收斂為預設值、走 `biz.role.notFound` 早拒、零變更（MUST NOT 演成全撤；只有明確之空陣列才是合法全撤）。
8. **Given** 端點維，**When** 讀取 R 現況，**Then** 以「路徑×方法」雙鍵呈現、以 HTTP 方法白名單辨識端點維（不以排除他維反推）；**When** 提交，**Then** 全量替換語意同上；端點維寫端不進選單序列化域。
9. **Given** 三支現況讀端，**When** 讀取任一角色之現況，**Then** 每一授權項帶受保護旗標；**Given** 角色不存在或已刪，**When** 讀或寫，**Then** 皆回 `biz.role.notFound`（角色鍵一律 `id`）。
10. **Given** 兩個選單維／按鈕維寫端，**When** 併發提交，**Then** 後者於選單序列化域 advisory 等待（以 NOT-granted 等待者斷言）；入域兩寫端各配一支機器證。
11. **Given** 兩處（同一超管帳號之兩分頁或兩裝置；`single_session_default`＝off 允許多會話）同時開啟同一角色同一維之彈窗，**When** 先後送出不同之期望全集，**Then** 後送出者整份為準、先送出者之差量被靜默撤銷（端點維可自授權回收桶復原、選單／按鈕維只能重勾）——已知態（Q12；ADR⑥ 新款）、本刀不加版本比對。

---

### User Story 2 - 結構性封死：受保護端點不得授予非超管 (Priority: P1)

超級管理員試圖把受保護端點（如 updateRoleEndpoints 自身、restorePolicy、系統設定寫端）授予 R_ADMIN——系統於鎖內以資料庫現況判定「該（路徑,方法）是否屬封死集」，命中即整批拒、零變更；經授權回收桶把受保護端點政策復原給非 R_SUPER 亦走同一守門。設定或解除受保護旗標的能力在一般管理介面永不提供。

**Why this priority**: 授權治理最關鍵的安全不變式，也是零 migration 的承重前提（受保護列之撤銷整批拒 ⇒ 受保護列結構上進不了可復原歸檔）；超管在 UI 真做得出「把治理端點授給 R_ADMIN」——守門非 vacuous。

**Independent Test**: 以 Super 對自建之非 R_SUPER 角色（seed 角色同形只在整合測試、掛清理守衛；Clarifications 第六題）提交端點維期望全集含 `POST /systemManage/updateRoleEndpoints` → 整批拒（`2222`＋`biz.role.protectedGrant`）、零變更；同一請求改為非受保護端點 → 成功；變異自證：拆掉鎖內守門 → 該測必紅。

**Acceptance Scenarios**:

1. **Given** 非 R_SUPER 角色 X，**When** updateRoleEndpoints 之新授集含任一（路徑,方法）屬「ptype=p ∧ protected=TRUE ∧ v2 ∈ HTTP 方法白名單」之集合（鎖內以資料庫現況判定），**Then** 整批拒、零變更、一因一鍵（`biz.role.protectedGrant`）；**Given** 標的為 R_SUPER，**When** 提交同一新授集，**Then** 不受本腿拒（R_SUPER 豁免）。
2. **Given** 一列端點維歸檔列其標的屬上述集合且來源角色非 R_SUPER，**When** restorePolicy，**Then** 於鎖內第③腿拒（`biz.policy.notRestorable`）——雙路徑全覆蓋。
3. **Given** v2＝`menu` 之四列受保護授權列（`manage_role`／`manage_menu`／`manage_system-settings`／`manage_policy-archive`），**When** 超管經 updateRoleMenu 授予 R_ADMIN 可見性，**Then** 成功（不在謂詞射程）——該頁之封死集端點仍 `5003`、頁內非封死端點依各自授權，效果＝看得到、封死功能點不動（已知態；逐頁實況見 ADR⑥）。
4. **Given** 非受保護之 21 支政策端點（含 unlockLogin、角色與選單寫端、IP 規則寫端），**When** 授予 R_ADMIN，**Then** 成功——授出後效果逐支記入已知態 ADR（Q3；翻案觸發＝首次出現多層管理員需求）；UI 不加警示。
5. **Given** 守門實作，**When** 刻意弄壞（拆掉守門或改謂詞），**Then** 對應測試轉紅（變異自證、還原後綠）。

---

### User Story 3 - 授權回收桶：閱覽歸檔列與復原端點維授權 (Priority: P2)

超級管理員在獨立的授權回收桶頁看到全部授權歸檔列（歸檔時間新到舊；以來源角色代碼與維度篩選），每列帶後端判定之「可復原」旗標；對可復原列執行復原——鎖內固定序五腿重驗後回到現役、歸檔列移除、同交易稽核、判定面同步。手動撤銷之選單／按鈕維歸檔列與三類連動歸檔列皆不可復原（只剩閱覽）；唯一可復原的是端點維手動撤銷。

**Why this priority**: 撤銷而無復原＝變相硬刪；其價值依附於 US1 的撤銷面，且可復原集已收窄至端點維，故次於 P1。

**Independent Test**: 以 Super 撤銷自建角色一條端點維授權 → 回收桶頁見該列可復原 → 復原 → 該列回到現役（現況讀端可見）；判定即刻恢復由整合測試以直種指派驗（Clarifications 第六題）；撤銷一條選單維授權 → 該列不可復原、復原動作停用、後端強行呼叫回 `biz.policy.notRestorable`。

**Acceptance Scenarios**:

1. **Given** 歸檔表有多維多角色列，**When** 開啟回收桶頁，**Then** 共用分頁信封、依歸檔時間降冪再 id 降冪、可依來源角色代碼（文字等值、可查已刪角色之代碼）與維度篩選（不設原因值篩選；Q17）；維度由歸檔列內容推導（無維度欄）。
2. **Given** 一列 reason＝`endpoint_revoke`、其來源角色 id 等於現役同代碼活角色 id、標的端點屬端點維候選集（路由表中受政策保護之端點全集）且不屬「受保護端點→非 R_SUPER」，**When** 讀取回收桶列表，**Then** 該列可復原＝true；**Given** reason 屬五值不可復原集、或來源角色 id 為 NULL、或現役同代碼角色非同一實例、或標的端點已不屬端點維候選集、或封死謂詞命中，**When** 讀取列表，**Then** 可復原＝false（旗標與權威五腿之①～④逐腿同判準；⑤停用不擋、免算）。
3. **Given** 可復原＝true 之列，**When** 復原，**Then** 鎖內固定序五腿重驗皆過 → 回灌現役（新 id）＋刪歸檔列＋稽核（`restore`）同交易 → 判定面同步；**Given** 標的已在現役（曾被重新授予），**Then** 回成功、不重複寫入、歸檔列仍消費移除、零稽核、不觸發同步（NoOp；Q16）；**Given** 識別不存在或任一腿拒，**Then** `biz.policy.notRestorable`（後端最終防線、不依賴前端停用）。
4. **Given** 歸檔列之（路徑,方法）已不屬端點維候選集（端點下線或改為非政策保護），**When** 復原，**Then** 第④腿拒（免幽靈政策）。
5. **Given** 來源角色已停用但活性，**When** 復原，**Then** 第⑤腿不擋（停用≠撤銷）。
6. **Given** 超管撤掉 R_SUPER 名下之非受保護端點列 getRoleList、致角色頁清單讀不出，**When** 經回收桶頁復原該列，**Then** 角色頁恢復——自救路徑恆可走（回收桶頁之選單列與其兩支端點皆受保護、撤不掉；Q14）。
7. **Given** 回收桶頁，**When** 超管自側欄開啟，**Then** 側欄項經 seed 選單列 `manage_policy-archive` 顯示、頁級門＝其選單維受保護授權列（R_SUPER）；復原鈕無按鈕碼 gating；可復原＝false 之列呈停用態。

---

### User Story 4 - 三顆授權彈窗與回收桶頁接真（前端） (Priority: P2)

超級管理員在角色抽屜看到三顆授權鈕（rev5 HEAD 對照錨點；rev6 現況兩顆——選單彈窗為真樹假勾選、按鈕彈窗全為假資料）：選單權限彈窗顯示真樹、真勾選與首頁下拉（首頁讀寫）；按鈕權限彈窗之假資料消失、候選＝治理域按鈕碼聯集；端點權限彈窗以路徑群組呈現端點候選、支援群組級勾選。三顆彈窗於現況讀成功前確定鈕停用、丟棄遲到回應、切換角色即清狀態；角色抽屜之「編輯角色」不再把開啟時的舊狀態值蓋回。

**Why this priority**: 後端寫端沒有 UI 就沒有操作者；首頁讀寫端點 005 刀已交付、UI 零消費者之窗由本刀閉合。

**Independent Test**: CDP 三方對照（rev5 22080 vs rev6 32080、必要時加 upstream 22089）：抽屜三顆鈕、選單彈窗真勾選與首頁下拉可存可讀、按鈕彈窗無假資料、端點彈窗群組勾選、回收桶頁可篩可復原；角色抽屜只改名稱時請求不帶狀態欄（網路請求事件斷言）。

**Acceptance Scenarios**:

1. **Given** 角色抽屜之編輯態，**When** 開啟抽屜，**Then** 三顆授權鈕皆在（不做按鈕碼 gating、門在頁級）；角色頁主檔一行不動。
2. **Given** 選單權限彈窗，**When** 開啟，**Then** 樹＝治理域（既有選單樹讀端）、勾選＝選單維現況讀端、受保護項鎖定、首頁下拉＝顯示域頁面全集且現值＝首頁讀端（NULL 誠實 null）；**When** 於首頁下拉選值（含清空），**Then** 即打首頁寫端（與確定鈕獨立、取消不還原；null／缺席／空字串三形同義清空）；**When** 提交，**Then** 打選單維寫端（全量）。
3. **Given** 按鈕權限彈窗，**When** 開啟，**Then** 候選＝治理域按鈕碼聯集、現況＝按鈕維現況讀端；**When** 提交，**Then** 打按鈕維寫端。
4. **Given** 端點權限彈窗（新檔），**When** 開啟，**Then** 候選依路徑群組呈現、葉鍵以路徑與方法合成且反查不拆字串（路徑可含分隔符）、群組級勾選＝勾其全部未鎖葉、授予側不預標受保護端點；**When** 提交，**Then** 打端點維寫端（替非超管勾選受保護端點者於此時被拒）。
5. **Given** 任一彈窗，**When** 現況讀未回或失敗，**Then** 確定鈕停用（防「讀未成即送空集＝整批撤」）；每次開啟（含切換角色）復位；遲到回應依請求世代丟棄；切換角色清空前一角色之角色維狀態（勾選、鎖定集、首頁值）、候選集每次開啟重取且成功才覆蓋。
6. **Given** 任一彈窗之期望全集使撤銷觸及受保護列或授予觸及封死集，**When** 提交，**Then** 純 key toast 由共用攔截層呈現、無明細表。
7. **Given** 角色抽屜編輯既有角色，**When** 只改名稱或描述後送出，**Then** 請求不帶狀態欄（狀態等於開啟時回填值即不送）；**When** 改動狀態，**Then** 照常帶（BL-00131 修法；與 rev5 行為分岔、ADR⑧ 登記）。
8. **Given** 回收桶頁，**When** 開啟並操作，**Then** 表格 8 欄、篩選兩欄、分頁、可復原才可按復原並二次確認、成功後重取列表；兩語譯文鍵集相等；路由項與頁名譯文到位（側欄與選單管理清單之該列不再顯路由裸鍵）。

---

### User Story 5 - 憲法 Amendment、工具擴面、治理與帳本落帳 (Priority: P3)

作為 workspace 維護者，我要在動任何 base-web 既有檔之前，以一筆 MINOR Amendment 讓島 G 入憲、開管理頁 ★ 軌道用途 (iii)(iv)、併入兩句紀律（模板屬性行標記變體、塊數入對賬射程）並同步改寫島 H 之連動字面；同刀把走查還原工具與測試守衛擴至能補回被撤之 seed 授權列、補 fork-delta-lint 範圍欄對賬腿與 seed 選單 view 對賬閘，並使帳本與活書在收刀時結清。

**Why this priority**: 治理項可與功能分開驗收，但 Amendment 是**硬序前置**（accepted 前不得動 base-web 既有檔）、seed 授權列回補是**測試基建前置**（本刀首度以寫端撤銷 seed 授權列、現行還原射程補不回來）；優先序只表達「不是交付價值本體」、不表達次序。

**Independent Test**: Amendment 落地後 fork-delta-lint 對新用途列之名冊載入以變異自證；範圍欄對賬腿以植入反例（改一個範圍欄數字）證必紅；seed-view-gate 以刪一個 view 證必紅、具名豁免兩列照綠；整合測試撤銷一列 seed 授權後清理守衛按原 id 補回、走查工具自測之同形合成案綠（Clarifications 第六題）。

**Acceptance Scenarios**:

1. **Given** plan 期 ADR 草稿已落 feature branch，**When** user 逐款親決 → Amendment ADR accepted → 憲法更新＋bump 1.7.0＋README 憲法版本鏡像＋generate，**Then** 以獨立 commit 落地；在此之前 base-web 既有檔零 diff。
2. **Given** 整合測試以寫端撤銷一列 seed 授權列（id 在基準上界以內）並復原出新 id 列，**When** 清理守衛 Drop，**Then** seed 列按原 id 原值補回、復原回插之新 id 列清除、序列還原；**Given** 走查基準與一份「seed 授權列被撤、新 id 列回插、seed 角色列可變欄被改」之現況（工具自測合成案；走查面唯已知態觀察窗會產生此形），**When** 跑走查還原，**Then** 同樣按原 id 補回、新 id 列清除、角色列可變欄回寫基準值、序列還原、全表基準 diff rc 0，且提示重啟 rust-api（Clarifications 第六題）。
3. **Given** §III.2 範圍欄某列之修改型處數或新增型塊數與實際標記不符，**When** 跑 fork-delta-lint，**Then** 紅並指名該列；範圍欄明文不預估或以預估值填列者跳過。
4. **Given** seed 選單之 component 指向 base-web 不存在之 view，**When** 跑 seed-view-gate，**Then** 紅；具名豁免兩列（system-settings／audit，附 BL-00045 指針）照綠。
5. **Given** 收刀，**When** append `feature_close` 事件，**Then** `backlog_done` 5 條、條文改寫 3 條、敘述改寫 1 條與 FR-046 相符；BL-00137／BL-00138 之 `backlog_add` 已由本刀第一筆事件帶入。

---

### Edge Cases

**授權寫端**

- 全量替換之射程＝候選集：候選外現役列（尚未上線之 seed 端點政策列、不在治理域之路由名或按鈕碼）不撤、不授、不入回應——UI 看不見的不動；現況讀端只回候選內（Clarifications 第二題）、orphan skip 不變。
- 空 diff 仍 Applied、仍落一列稽核、仍觸發判定面同步（授予面刻意例外、重建冪等），與移除面「實際歸檔 ≥1 列才觸發」並陳。
- 期望集含候選外項 → 靜默略過（三維同式）；回應帶實際生效集合，前端不另提示。
- body 缺席或壞形（含期望集鍵缺席或鍵名拼錯；Clarifications 第七題）→ 角色鍵收斂為預設值 → `biz.role.notFound` 早拒；只有合法角色鍵＋明確之空陣列才是合法全撤（仍受撤銷拒約束）；MUST NOT 把守門前移至授權中介層、MUST NOT 為此新增錯誤碼。
- 請求上下文缺席（操作者不可得）→ 寫端拒寫 `5000`、不以佔位補稽核列。
- 標的角色停用中 → 三維寫端照常可讀寫其授權（停用≠撤銷；停用即斷權由授權讀端每請求濾角色狀態承擔）。
- 並行編輯（Q12）：兩處同開同一角色同一維之彈窗、先後送出 → 後送出者整份為準；請求世代只丟棄**同一彈窗**之遲到回應、不防跨分頁或跨裝置覆蓋；seed 持有 R_SUPER 之帳號恰 1 個、十支端點又封死授不出去 ⇒ 本刀期間只有同帳號多分頁或多裝置撞得上；已知態、翻案觸發＝007 使第二個帳號持有 R_SUPER 或實際發生誤蓋。
- 超管自撤（Q14）：R_SUPER 名下只有受保護列鎖住；撤掉非受保護端點列（例 getRoleList）會令角色頁失能，自救＝授權回收桶復原（端點維可復原、回收桶頁與其端點受保護）；選單／按鈕維被撤則於角色頁恢復後重勾。
- 授予之新列治理欄：受保護旗標恆 FALSE、建立者＝操作者；絕不經判定引擎管理 API 或轉接器之新增政策路徑寫入（後者對重複列回錯且吃序列；LL-00035）。

**結構性封死與保護**

- 封死謂詞只看資料庫現況、不寫死列數（2026-10-01 量測：端點維受保護 15 列＝本刀後之現役路由 14＋尚未上線之 `updateUserSessionPolicy` 1）；未上線端點上線即自動納管。
- v2＝`menu` 之四列受保護授權列不在封死射程：可授予他角色可見性；該頁之封死集端點仍 `5003`、頁內非封死端點依各自授權＝看得到、封死功能點不動（已知態；逐頁實況見 ADR⑥）。
- 非受保護之 21 支政策端點可授出（含 unlockLogin：授出後無帳號維守門、no-escalation 本體屬 007）——已知態 ADR 逐支記授出後效果與翻案觸發。
- 撤銷拒與封死拒於同一請求並存時先判撤銷、再判授予（實務互斥：受保護列皆屬 R_SUPER、封死只擋非 R_SUPER 標的）。

**授權回收桶**

- 選單／按鈕維只剩閱覽：不可復原集含 `menu_revoke`／`button_revoke`；選單維授權只能重勾不能復原——UI 以停用態呈現、不另造提示。
- 端點維下線列：歸檔列之（路徑,方法）已不屬端點維候選集（下線或改為非政策保護）→ 第④腿拒、旗標 false；現役中之下線端點授權列屬候選外、不被全量替換撤銷（候選集射程）。
- 來源角色 id 為 NULL 之歷史列 → 可復原＝false、誠實退化（不補寫、不猜）；本刀後之撤銷列恆有來源角色 id（標的角色列已鎖且活性）。
- 復原遇標的已在現役 → NoOp（成功、歸檔列消費移除、零稽核、不同步；與 Applied 對前端不可區分；回收桶少一列而稽核表無痕跡＝已知態、Clarifications 2026-10-01）；可復原旗標不加「是否現役」腿（Q16）。
- 同一（角色,端點）多次撤銷 → 多列歸檔；復原其一後其餘列仍在、再復原即 NoOp。
- 回收桶篩選之角色代碼為文字等值：可查已刪或停用角色之歸檔列（既有角色下拉只列活性且啟用者，故不用下拉）。

**判定面同步與生效時點**

- 生效語意兩層（Q13）：API 判定於判定面同步換上後即時生效；被改角色之使用者，其側欄選單與按鈕顯隱於下次載入頁面（重新整理或重新登入）時更新；不做即時推播。
- 有界過渡窗（Q6、BL-00134）：域鎖為交易級、commit 即釋放，判定面重建換上在其後（失敗重試另加退避、同步互斥另加排隊）——其間已撤之端點授權仍可能放行、新授之端點仍回 `5003`（授予面反向症狀）；本刀起**及於 API 授權**（005 刀時期只及 UI 可見性）；窗有界、自癒——有界之前提＝收場取消安全（FR-018）且重建有界，窗長＝一次重建＋重試退避＋同步排隊。
- 重試耗盡窗：耗盡仍失敗時舊面續用、恢復＝下次成功同步或重啟 rust-api（RUNBOOK 處置）；前提＝單一 rust-api 行程。
- 同步觸發者不得持有判定面讀鎖；同步結果（含耗盡）不改寫端回應之成功判定（commit 成功即回成功），回應於同步結束後送出。

**前端與已知態**

- 選單維無父子連動：勾選目錄不連帶勾子項、勾子項不連帶勾目錄（沿基線與 rev5 HEAD）；使用者路由組樹自動帶入祖先，故只勾子項即可見。★CDP 待觀察候選①：只勾目錄不勾子項＝側欄出現一個點入空白之項，首頁兜底可能落在它（CDP 三方對照單元實測、治理單元由 user 定案入 ADR⑥）。
- ★CDP 待觀察候選②：`role:*`／`menu:*`／`user:*` 按鈕碼今無前端按鈕碼判斷之消費點（只 `B_CODE1`～`B_CODE3` 與 `ipRule:*` 有）⇒ 授撤零可見效果。
- 可授予「指向不存在 view 之自建選單」⇒ 側欄可見但點擊零反應（seed 側由 seed-view-gate 管、自建選單不在其射程；已知態）。
- 首頁下拉候選＝顯示域頁面全集、不限該角色可見集；首頁不在可見樹時由讀端兜底落先序第一可導航葉（005 刀既有；「登入即落 404」結構性不可達）。
- system-settings／audit 兩頁仍為死項（BL-00045、008）——CDP 排除清單。

**測試與走查基建**

- 本刀首度以寫端撤銷 seed 授權列（id 在基準上界以內）：現行走查還原與測試守衛只刪上界以上之列、補不回被撤之 seed 列 ⇒ MUST 先擴面（測試守衛前移至寫端單元之前、走查工具於前端 CDP 之前）。
- 以 `sys_menu.created_by IS NULL` 錨 seed 之兩支使用者路由案，對授在 seed 選單列上之殘授權敏感 ⇒ 改錨 `casbin_rule.created_by IS NULL` 之 seed 政策列（授予落建立者後可分辨；BL-00136 形①）。
- 走查（CDP 與 quickstart 手跑）之寫入步驟一律對自建角色；seed 授權列撤後回補與超管自救只由整合測試證明、不入走查（Clarifications 第六題）；★唯一具名例外＝已知態觀察步驟（ADR⑥ 各款之「觀察路徑」）得對 seed 角色（R_ADMIN／R_USER_COMMON）寫入並以 seed 帳號登入觀察（本刀無使用者角色指派寫端、自建角色無帳號可持有），前後 MUST 套走查基準：觀察前 snapshot、觀察後 restore＋重啟、diff rc 0（Clarifications 第五題）；以 SQL 還原動過 `casbin_rule` 後 MUST 重啟 rust-api 使判定面回版（判定面無外部通知管道）。
- rev5 側唯讀：一切讀取對凍結 worktree、不寫入、不動其 stack。

## Requirements *(mandatory)*

### Functional Requirements

**A. 端點、授權態與契約總則（ROUTES 39→49）**

- **FR-001**: ROUTES MUST 由 39 條擴為 49 條、路由條數常數同 commit bump；新增十條且路徑與動詞逐字對齊 001 凍結 seed 之政策列：三維讀寫 6——`/systemManage/getRoleMenu`（GET）、`/updateRoleMenu`（POST）、`/getRoleButton`（GET）、`/updateRoleButton`（POST）、`/getRoleEndpoints`（GET）、`/updateRoleEndpoints`（POST）；候選讀 2——`/systemManage/getAllButtons`（GET）、`/getAllEndpoints`（GET）；授權回收桶 2——`/systemManage/getArchivedPolicies`（GET）、`/restorePolicy`（POST）。動詞分布 GET 6／POST 4；十條**全為政策保護**。
  contract case 登記表之 case 集 MUST 與 ROUTES 恰等（49＝49、雙向覆蓋閘）；routes 生成表由 generate 重算；外層 routes 生成器之真 repo 釘值測 MUST 同批 +10 列。
- **FR-002**: 本刀 MUST 為**零 migration、零 seed 變更**：十條之 seed 政策列（32／33、52～57、70／71；皆 R_SUPER、protected=TRUE）、選單列 `manage_policy-archive` 與其選單維受保護授權列、授權表治理三欄與授權歸檔表結構皆在 001 基線；migration 目錄維持恰兩支；seed 選單 78 列、政策 163 列、角色 3 列不動；不可復原集擴列為純碼變更（Q2）。★DDL 冒出＝本刀範圍翻案。
- **FR-003**: 授權態 MUST 逐列照 seed、不多授不少授：十條只授 R_SUPER；R_ADMIN／R_USER_COMMON 對十條皆 `5003`。
- **FR-004**: 一切業務拒因 MUST 為純 i18n key、一因一鍵（無攜參明細）；復用既有 `2222`／`5003`／`4040`／`5000`，13 碼矩陣與錯誤變體零新增。本刀新增拒因鍵恰 3：`biz.role.protectedRevoke`（撤銷集觸及受保護授權列）、`biz.role.protectedGrant`（授予集觸及封死集）、`biz.policy.notRestorable`（復原標的不存在或任一腿拒）；角色不存在或已刪沿用既有 `biz.role.notFound`。
  msg key 名冊 43→46；每鍵 MUST 在契約測試之真 seed 應用面實際發出（名冊雙向閘），且新鍵 MUST 隨首個發出它的單元落地（名冊、三檔 locale 後端子樹、型別樹同批）。
- **FR-005**: 回應 MUST 逐欄白名單構造（絕不序列化原始資料列）：欄名 camelCase；id 為 number 並守 2^53 上界；時間為帶 `+00:00` 之 RFC3339、前端原樣顯示（ADR-00061）；歸檔者以操作者帳號名批次回填（查無→null）；三支現況讀端之受保護旗標 MUST 為後端單一真源、MUST NOT 以 seed 靜態集於前端判定（旗標義務本體見 FR-014）；
  角色鍵 MUST 一律為 `id`（三維六支與既有首頁讀寫同式；期望集之欄名與形於 contracts 定案、沿 rev5 契約形）。
- **FR-006**: 操作稽核 MUST 與業務寫入同一交易：三維寫端 Applied（含空 diff）恰一列 `update`、Rejected 與查無角色零稽核；restorePolicy Applied 恰一列 `restore`、NoOp 與 NotRestorable 零稽核（承 rev5 as-built）；動作詞彙沿既有封閉五詞、零新詞；稽核列之標的表一律＝`sys_role`（三維寫端之標的 id＝標的角色、restorePolicy＝來源角色），與 005 刀角色列整列快照形同表、以 `payload_after` 鍵集區分（計數摘要形）；
  操作者取自請求上下文，缺席＝拒寫 `5000`、不以佔位補列、不帶 IP 域降級欄、不增計降級計數，且其取得 MUST 先於一切守門（005 刀 FR-008 同式）。
- **FR-007**: 寫端請求 body 缺席或壞形（三維寫端之壞形含期望集鍵缺席或鍵名拼錯——期望集鍵必填；Clarifications 第七題、刻意分岔登記表）MUST 依既有 wire 慣例以共用件收斂為預設值：三維寫端 → 角色鍵預設值不對應任何活性角色 → `biz.role.notFound` 早拒、零變更（MUST NOT 演成「空期望集＝全撤」）；restorePolicy → 識別預設值 → `biz.policy.notRestorable`；授權中介層不讀 body、MUST NOT 把守門前移；不得為此新增錯誤碼。合法角色鍵＋明確之空陣列＝合法全撤（Q15；仍受 FR-011 約束）。
- **FR-008**: getArchivedPolicies MUST 採共用分頁規則（005 刀分頁通則：缺席 1／10、clamp、壞形整串預設、逾界回空頁）與共用分頁信封、伺服端固定穩定序（歸檔時間降冪、id 降冪；ADR-00058 決定 1——不收排序參數；固定序由本刀定＝決定 2）；讀端零 migration。

**B. 三維授權寫端與讀端（島 G2／G3／G5）**

- **FR-009**: 三維寫入 MUST 以「期望全集」為輸入、由系統與現況比對導出撤銷集與新授集（全量替換語意）；MUST NOT 提供增量式寫入介面。★射程＝候選集（Q8、ADR④；三維同式）：撤銷集 MUST ＝（現況 ∩ 候選集）−期望集；新授集 MUST ＝（期望集 ∩ 候選集）−現況；
  候選外之現役列 MUST NOT 被撤銷、MUST NOT 出現於回應之生效集合（現況讀端之射程見 FR-014）；期望集中之候選外項 MUST 靜默略過（orphan skip）、回應帶實際生效集合。
- **FR-010**: 候選集 MUST 與判定面同源、不多列不漏列：選單維＝治理域選單（未刪含停用；以介面選單識別收單、以路由名落授權、讀端反向映射回識別）；按鈕維＝治理域選單按鈕碼之聯集（去重、穩定序）；端點維＝路由表中受政策保護之端點全集（路徑×方法；以具名入口供寫端與候選讀共用、斷循環依賴）；
  現況辨識 MUST 以 HTTP 方法白名單判別端點維（不以排除他維反推）、MUST NOT 引入平行之維度標記；候選集與其映射 MUST NOT 誤用顯示域（島 H4；兩種失效形皆禁：候選半誤用＝停用選單之授權自生效集合與現況讀端消失而不可治理、映射半誤用＝被全量替換靜默升級為撤銷；必配負向測試、三斷言見 ADR④）。
- **FR-011**: 撤銷集觸及受保護授權列時 MUST 整批拒（`biz.role.protectedRevoke`）、於任何寫入之前判定、零變更零稽核零同步；三維皆適用；R_SUPER 名下之非受保護列 MUST 可撤（Q14）；一般管理介面 MUST NOT 提供設定或解除受保護旗標之能力（防鎖死 by-design）。
- **FR-012**: 新授 MUST 由授權 facade 直接寫入授權表、補齊治理欄（受保護＝FALSE、建立時間、建立者＝操作者 uid；BL-00136 形①之料源）；MUST NOT 經判定引擎管理 API（島 G1）、MUST NOT 經轉接器之新增政策路徑（LL-00035）。
  撤銷 MUST 為移入授權歸檔（完整快照＋來源角色 id 由歸檔寫入件內以角色代碼反查活性角色自動填入＋reason；reason＝`menu_revoke`／`button_revoke`／`endpoint_revoke`）；刪除集以剛歸檔那批 id 圈定。
- **FR-013**: 入域與鎖序：handler 持有交易、入域寫端之交易內主體首句取域鎖（005 刀形）；updateRoleMenu／updateRoleButton MUST 於選單序列化域內執行（島 H1 終態成員）；updateRoleEndpoints MUST NOT 入域（端點維不涉選單資料）；
  三維寫端 MUST 鎖標的角色列（FOR UPDATE、活性）→ 鎖內重驗（角色活性／受保護集／候選集／封死集）→ 落寫（lock-then-redecide、永不信 pre-read）；固定鎖序沿 005 刀定案（advisory → 歸檔表列 → 角色列 → 選單列 → 授權表列）；角色不存在或已刪＝`biz.role.notFound`。
- **FR-014**: 三支現況讀端（getRoleMenu／getRoleButton／getRoleEndpoints）MUST 回「現況 ∩ 候選集」、每項帶受保護旗標；getAllButtons MUST 回治理域按鈕碼聯集（去重、穩定序；與絕版判定之私有掃描語意不同、不共用）；getAllEndpoints MUST 回路由表中受政策保護之端點全集（路徑×方法；回應集隨路由表成長、本刀後 35）；
  候選讀端 MUST NOT 帶受保護或封死預標（授予側不預標；Q3、rev5 HEAD 形）。
- **FR-015**: 三維寫端 outcome MUST 恰兩態：Applied{撤銷集, 新授集, 生效集合}／Rejected{拒因}；空 diff 屬 Applied；回應帶實際生效集合。
- **FR-016**: 並行編輯 MUST 維持「後送出者整份為準」之全量替換語意、本刀 MUST NOT 引入版本比對或差量提交（Q12）；此已知態入 ADR⑥（觀察路徑→症狀；翻案觸發＝007 使第二個帳號持有 R_SUPER 或實際發生誤蓋）。

**C. 判定面同步（島 G1；005 刀基建純消費）**

- **FR-017**: 觸發矩陣 MUST 以三類同一字面承載（ADR⑤ 增列、不 supersede ADR-00043——其決定 7「觸發列由該刀 ADR 增列」）：①移除面五支（005 刀既有）＝「成功且實際歸檔 ≥1 列」②授予面三支（三維寫端）＝「Applied 即觸發、不問 diff（含空 diff）」——MUST 於島 G1 條文與判定面家檔 doc 明文為「授予面刻意例外」、與移除面並陳 ③restorePolicy＝「Applied」；
  Rejected／NoOp／NotRestorable／查無角色 MUST NOT 觸發（早退結構性保證）；其餘寫端之零觸發維持 ADR-00043 決定 7。
- **FR-018**: 同步 MUST 純消費 005 刀基建（全新重建後一步換上、保留上一份、有界重試、全程互斥、單一行程前提）、零新機制；MUST 於交易 commit 之後且不持有判定面讀鎖；授予面三支與 restorePolicy 之收場 MUST 取消安全（commit＋同步交脫離請求生命週期之 task、回應於同步結束後送出；ADR⑤）；同步呼叫點檔集名冊 MUST 同批擴列新寫端檔（集合恰等、不擴列即紅）、判定面寫鎖取得檔集 MUST 維持空冊；判定引擎版本錨不升版。
- **FR-019**: 生效語意 MUST 明文兩層時點（Q13；落點＝島 G 入憲 ADR 後果段＋活書 08 授權慣例）：API 判定於同步換上後即時生效；被改角色之使用者，其選單與按鈕顯隱於下次載入頁面時更新；本刀 MUST NOT 做即時推播。
- **FR-020**: 已知降級窗 MUST 如實記兩窗（Q6、BL-00134）：①commit→換上之有界過渡窗（重建一次、失敗重試另加退避、同步互斥另加排隊；有界之前提＝收場取消安全〔FR-018〕；本刀起端點維撤銷使之及於 API 授權，授予面之反向症狀＝新授端點短暫仍回 `5003`）②重試耗盡窗（舊面續用、恢復＝下次成功同步或重啟）；
  由 Amendment 同顆改寫島 H2（與島 G 對應條）之「唯一已知降級窗」字面；ADR⑤ 補述 ADR-00043 決定 9、並聲明 ADR-00042 body 內兩處同字面被取代；RUNBOOK §13 補授予面反向症狀與排障錨；既有同步結果計數與 `obs016-casbin-reload-anomaly` 告警照舊；零碼改（記窗、不關窗）。

**D. 結構性封死（島 G6）**

- **FR-021**: 不變式：屬「ptype=p ∧ protected=TRUE ∧ v2 ∈ HTTP 方法白名單（`router::endpoint_methods()`）」之（路徑,方法）集合 MUST NOT 授予非 R_SUPER 角色——謂詞式、鎖內以資料庫現況判定；條文 MUST 只寫謂詞、不寫列數（2026-10-01 量測：端點維 15 列＝本刀後現役路由 14＋未上線 1）。
- **FR-022**: 掛點 MUST 恰兩處：updateRoleEndpoints（先判撤銷、再判授予）與 restorePolicy 第③腿；違者整批拒、零變更（前者 `biz.role.protectedGrant`、後者 `biz.policy.notRestorable`）；R_SUPER 標的豁免；守門非 vacuous（超管在 UI 真做得出）、MUST 配變異自證（弄壞 → 紅 → 還原 → 綠）；「恰兩處」MUST 有機器釘：封死查詢件之生產呼叫點名冊（兩掛點＋可復原旗標讀端一處、不計掛點）與授權表生產面寫入者名冊（授予、復原回插兩類）集合恰等、多出即紅。
- **FR-023**: v2＝`menu` 四列受保護授權列 MUST NOT 納入封死射程（已知態：可見性可授、該頁之封死集端點仍 `5003`、頁內非封死端點依各自授權；rev5 同形）。
- **FR-024**: 承重前提 MUST 明文於 ADR②：可復原之歸檔列原值恆 protected=FALSE（受保護列之撤銷整批拒 ⇒ 受保護列結構上進不了可復原歸檔）；歸檔表不加受保護快照欄之前提＝「撤銷整批拒＋受保護旗標永不 UI 化（FR-011）」；任一處鬆綁＝觸發 ADR-00044 決定 4 之翻案觸發條款。
- **FR-025**: 非受保護之 21 支政策端點 MUST 可授予非 R_SUPER（Q3）；授出後效果 MUST 逐支記入 ADR⑥（含 unlockLogin 授出後無帳號維守門、角色與選單寫端、IP 規則寫端之下放效果）＋翻案觸發（首次出現多層管理員需求）；UI 不加警示；no-escalation 本體不在本刀（Q4；掛點不動）。

**E. 授權回收桶（島 G5 復原面）**

- **FR-026**: getArchivedPolicies MUST 分頁（FR-008）＋雙篩（來源角色代碼＝授權列角色欄等值、空字串忽略／維度＝由列內容推導：`menu`→選單維、`button`→按鈕維、HTTP 方法白名單內之方法→端點維；不新增維度欄）；不收原因值篩選（Q17）；每列帶歸檔者帳號名與可復原旗標。
- **FR-027**: 可復原旗標 MUST ＝權威五腿之 ①reason 不屬不可復原集 ∧ ②歸檔之來源角色 id 等於現役同代碼活角色 id（NULL→false）∧ ③封死不擋 ∧ ④端點屬端點維候選集（路由表中受政策保護之端點全集；選單／按鈕維列因①恆 false、免此半）；第⑤腿恆不擋故免算；前端 MUST NOT 自行推斷；
  旗標 MUST 與權威判定**逐腿同判準**（reason 半共用單點函式、其餘半與鎖內重驗同判準；批次讀端一次取活性角色與受保護集、避免逐列查）；配「旗標＝權威」逐腿同判準測（①～④各一）。
- **FR-028**: 不可復原 reason 集 MUST 擴為五值 {`role_soft_delete`, `menu_soft_delete`, `menu_button_removed`, `menu_revoke`, `button_revoke`}（單點函式承載、集合成員測更新）；唯一可復原 reason＝`endpoint_revoke`；既有釘案中斷言三撤銷原因「屬可復原」之負向臂 MUST 同批翻為兩值不可復原、`endpoint_revoke` 仍可復原（Q2）；零 migration、島 H2 零破口。
- **FR-029**: restorePolicy MUST 鎖內固定序五腿重驗（ADR③；每腿註對應寫端守門）：①reason gate（五值集）②來源角色同實例（NULL 不可復原、誠實退化）③結構性封死（受保護端點政策不得復原給非 R_SUPER）④端點屬端點維候選集（不屬→拒、免幽靈政策）⑤角色停用不擋（停用≠撤銷、島 H4 精神、已知態）。
- **FR-030**: restorePolicy outcome MUST 三態：Applied（以快照之身分欄重新授予〔新 id；受保護＝FALSE、建立者＝復原者 uid、建立時間由資料庫預設；快照之建立欄不回灌＝復原為一次新授予事件，與 FR-012／FR-045 同判準〕＋刪歸檔列＋稽核 `restore` 同交易 → 判定面同步）／NoOp（授權列身分鍵已在現役 → 回成功、歸檔列仍消費移除、不重複寫入、零稽核、不同步；與 Applied 對前端不可區分、回收桶移除該列而無稽核痕跡——兩者皆已知態、入 ADR⑥；Q16、Clarifications 2026-10-01）／NotRestorable（識別不存在或任一腿拒 → `biz.policy.notRestorable`）；後端 MUST 為最終防線。
- **FR-031**: restorePolicy MUST NOT 進選單序列化域（可復原列只剩端點維）；鎖序＝歸檔表列（FOR UPDATE）→ ①reason gate（不過即止、不取角色列鎖）→ 角色列（FOR UPDATE）→ ②～⑤鎖內重驗 → 回插 → 刪歸檔 → 稽核；與 updateRoleEndpoints 共用同一封死判準（雙路徑全覆蓋）。島 H1 括號之「授權回收桶復原之該兩維分支」由 Amendment 改寫為結構性不可達（FR-040）。
- **FR-032**: 自救路徑 MUST 恆可走（Q14）：撤掉 R_SUPER 名下非受保護端點列致角色頁失能時，授權回收桶頁（其選單列與兩支端點皆受保護）MUST 仍可達並復原該列；spec 列 edge case、配一支端到端整合測試（撤 getRoleList → 回收桶復原 → 判定恢復；整合測試承擔、不入走查＝Clarifications 第六題）。

**F. 前端**

- **FR-033**: 三顆授權彈窗 MUST 接真：menu-auth-modal（修改型；樹＝既有選單樹讀端〔治理域〕、勾選＝getRoleMenu、首頁下拉＝既有頁面讀端〔顯示域〕、首頁現值＝getRoleHome〔NULL 誠實 null〕、首頁下拉選值即打 updateRoleHome〔與確定鈕獨立、沿 upstream 既綁之選值事件與 rev5 HEAD；清空即送 null＝三形同義清空〕、提交＝updateRoleMenu〔全量〕；★不加父子連動〔沿基線與 rev5 HEAD 形〕）／
  button-auth-modal（修改型；候選＝getAllButtons、現況＝getRoleButton、提交＝updateRoleButton）／endpoint-auth-modal（新增型新檔；候選＝getAllEndpoints 依路徑群組呈現、葉鍵以路徑與方法合成、群組鍵＝純路徑、反查由映射表還原不拆字串、群組級勾選＝勾群組即勾其全部未鎖葉且回報值只含葉鍵、現況＝getRoleEndpoints、提交＝updateRoleEndpoints）；
  掛載點＝角色抽屜（同檔雙用途：既有編輯態區加第三鈕「端點權限」並掛新彈窗）；角色頁主檔 MUST 一行不動；三鈕 MUST NOT 做按鈕碼 gating（門在頁級）。
- **FR-034**: 三顆彈窗之共同守衛 MUST（rev5 HEAD 形）：①依現況讀端之受保護旗標鎖定——樹節點 disabled＋受控勾選集之可寫 computed setter 強制補回雙保險、模板之勾選雙向綁定一行不動（BL-00135 之變體句入憲後依新句標記）②確定鈕於現況讀成功前停用、讀失敗維持停用（僅能取消重開）、每次開啟（含切換角色）復位③請求世代丟棄遲到回應④切換角色清空前一角色之角色維狀態（勾選、鎖定集、首頁值；候選集與角色無關、每次開啟重取、成功才覆蓋＝`rev5:B-129` 形）；
  授予側 MUST NOT 預標受保護端點；拒因 UI MUST 為共用攔截層之純 key toast（不建明細型、不擴明細對照表）。
- **FR-035**: 角色抽屜編輯既有角色時 MUST 只在狀態值與開啟時之回填值不同時才帶狀態欄（BL-00131 修法；Q9）；改點在用途 (ii) 既有新增型圈界內、(ii) 範圍欄實數不變；與 rev5 行為之分岔 MUST 立 ADR⑧ 登記並列入刻意分岔登記表。
- **FR-036**: 授權回收桶頁 MUST 以獨立管理頁交付（頁面與搜尋模組兩支新增型新檔）：查詢列＝來源角色代碼（文字）×維度（下拉、可清空）；表格 8 欄（序號／來源角色／維度／標的／歸檔原因／歸檔時間／歸檔者／操作；不顯方法欄——seed 端點維 50 相異路徑、同路徑多方法 0）；分頁；
  可復原＝false 之列復原鈕停用；復原二次確認、成功後重取；復原無按鈕碼 gating（門＝頁級選單維受保護授權列＋列級旗標）；view 目錄由 seed 選單列之 component 字面決定、圖示以 DB 為唯一真源（不寫 static meta）；自由文字欄純文字插值。
- **FR-037**: i18n MUST：後端子樹三檔（`en-us`／`zh-cn`／`zh-tw`）各補 3 鍵、`app.d.ts` backend 型節同補（既有 I18N-WIRING (ii)(iii) 射程、前後端鍵同 commit）；`page:` 樹補回收桶頁整節與抽屜第三鈕一鍵（兩語鍵集相等、`app.d.ts` `Schema.page` 型節同補；`zh-tw` 不塞 page 鍵）；
  `route:` 樹補 `manage_policy-archive` 一鍵（兩語；側欄與選單管理清單之該列不再顯路由裸鍵＝ADR-00045 款 2／款 6 之該列解除）；新增圈界塊落地後做「拔標記必紅」變異自證；回收桶頁之復原三鍵各頁自有、不與選單回收桶收斂。
- **FR-038**: 新增型新檔 MUST 為：端點權限彈窗、回收桶頁兩支、一支 API wrapper（`src/service/api/rev6-authz.ts`）與一支型別檔（`src/typings/api/rev6-authz.d.ts`；獨立命名空間、§III.1 預設軌道）；路由外掛產物四檔 MUST 由外掛重算（新增 view 頁）、走產物檔紀律（禁手改、重算冪等、`route-artifact-gate` 三道斷言）；`components.d.ts` 若有變化只許工具重算形。
- **FR-039**: fork-delta 檔集 MUST 恰為：修改型 inline＝兩顆授權彈窗（(iii)）；角色抽屜＝(iii) 新增型（零修改型）、(ii) 既有圈界內之 BL-00131 修法（(ii) 實數不變）；兩語 locale 與 `app.d.ts` 之新增型圈界（(iii)／(iv)／I18N (ii)(iii)）；`zh-tw.ts` 為 rev6 自有檔（新增型、不入名冊）；產物四檔；base-web 變更檔集 MUST 以機器斷言 ⊆ 授權檔集＋新增檔；修改型標記逐行 `原行:`。

**G. 憲法 Amendment、ADR、工具與帳本**

- **FR-040**: 憲法 Amendment MUST 一次 MINOR（1.6.0→1.7.0）、獨立 commit、條文字面由 user 逐款親決（U0）：
  ①§I.7 島 G 六條入憲（以 rev5 v1.10.0 島 G 字面為底、rev6 座標改寫：G1 真相唯一與同步失敗契約〔DB-first；觸發方向面入憲、矩陣留 ADR⑤〕／G2 受保護拒絕〔整批拒、一因一鍵、明細載體不入條文、受保護旗標永不 UI 化〕／G3 撤銷必歸檔〔撤銷＝移入歸檔、授予＝補齊治理欄之寫入、刪角色同交易全維連動歸檔〕／G4 刪除守門與批次原子／G5 復原同實例與全端點鎖序〔lock-then-redecide、固定鎖序〕／G6 結構性封死謂詞〔承 rev5 新條、ADR②〕；ADR-00044 決定 3 所載 G1 前半／G3／G4／G5 之行為由本條轉正、該 ADR 不因此被 supersede；停用雙護欄不轉正、續由 ADR-00044 決定 3 承載〔Q5〕；G5 之條文層級與島 G 標頭寫法於親決輪定）
  ②§III.2 ★`BASE-WEB-MANAGE-PAGE-WIRING` 加兩列：(iii) 三顆授權彈窗接真（兩顆彈窗＋角色抽屜同檔雙用途＋兩語 locale `page:` 樹資料級補鍵＋`app.d.ts` 型節；端點彈窗新檔另註、不入表）、(iv) 授權回收桶頁（兩語 locale `route:`／`page:` 塊、`app.d.ts` page 型節；產物四檔沿 (i) 列之產物檔紀律、(iv) 不重列＝親決題 III-b 建議形；頁面兩檔新檔不入表）；(ii) 列紀律欄之兩彈窗「明文不入名單」句同顆改寫（親決題 III-c）；範圍欄初值依表外宣告 1 例外路徑以「不預估」或預估值填列、收刀前 PATCH 實數化（前例 ADR-00051）
  ③§III 修改型補 Vue 模板屬性行之標記變體句（BL-00135；活書 08 §8.4 同批）④表外宣告 3 改寫為塊數納入對賬射程（BL-00132）
  ⑤島 H 連動：序言「島 G 條文入憲前之凍結位」句改寫、H1 括號改寫為「授權治理之選單維與按鈕維寫端已入域；授權回收桶復原之該兩維分支因不可復原集擴列而結構性不可達」、H2 記兩窗（FR-020）、MAJOR 射程「七島」改「八島」、承襲指針表 G 列補 rev6 入憲載體；H2「同步失敗保留上一份」方向句之落位（留 H2 或移 G1 並互引）於親決輪定（ADR-00042 翻案觸發器要求複核）
  ⑥README 憲法版本鏡像與 generate。Amendment accepted 前 base-web 既有檔 MUST 零 diff。
- **FR-041**: ADR MUST 九支於 plan 期起草（feature branch 內、序號接續；plan 期草稿、proposed 期不宣告 supersedes、accepted 同顆補）＋收刀前 PATCH Amendment 一支（(iii)(iv) 範圍欄預估值實數化；前例 ADR-00051；配號＝當下下一號、plan 期不起草）。九支為：①島 G 入憲 Amendment（provenance `rev5:ADR 0053`）②G6 結構性封死（`rev5:ADR 0054`；承重前提 FR-024）③回收桶復原五腿＋不可復原集 3→5（`rev5:ADR 0055`；附 ADR-00044 決定 4 之復核結論＝選單維仍無可復原 reason、選單維歸檔之 `menu_id` 同實例欄續 won't-use〔ADR-00044 決定 4③〕）④全量替換射程＝候選集（`rev5:ADR 0056`）
  ⑤判定面同步觸發列增列＋記窗（補述 ADR-00043 決定 9；聲明 ADR-00042 兩處同字面被取代；不 supersede ADR-00043）⑥ADR-00045 續行（八款逐款處置：款 1／3／4／7 之解除或改述、款 2／6 之 policy-archive 列解除而 system-settings／audit 兩列續存〔FR-037〕、款 5／8 續行；＋新已知態：21 支可授出端點與 unlockLogin 窗、選單維受保護四列之可見性可授而該頁封死集端點仍拒、並行編輯後送出者覆蓋、復原 NoOp 移除歸檔列而零稽核、CDP 實測定稿之候選款）
  ⑦ADR-00046 續行（款 3 操作稽核寫入者擴列 update／restore＋BL-00084 by-design 款〔每次阻擋恰一則結構化 warn、不設節流〕；改指現在式面）⑧BL-00131 前端修法（與 rev5 行為分岔登記）⑨seed-view-gate 碼面閘（RUNBOOK §12 讀面型、ADR-00055 決定 3 之首例）。
  親決時點：Amendment 顆只含 ADR① 與其連動條文、其餘另顆；ADR⑥⑦ 於治理單元定稿後 accepted。
- **FR-042**: fork-delta-lint MUST 加範圍欄對賬腿（BL-00132）：修改型逐軌道×用途×檔比 `原行:` 數、新增型塊數逐檔加總比；範圍欄明文不預估或預估列跳過；零解析即紅；以植入反例變異自證；MUST 於首個觸及 base-web 既有檔之單元之前落地（含依 FR-004 把新拒因鍵落入 locale 與 `app.d.ts` 之後端單元；碼面閘加腿、不佔 GT 名額）。
- **FR-043**: MUST 立 seed-view-gate（python 碼面閘）：seed 選單 component 之 view 集 ⊆ base-web view 集；具名豁免恰兩列（system-settings／audit，附 BL-00045 指針、兌現即縮）；入 pre-commit 段、自測、bootstrap 名冊、RUNBOOK §12 碼面閘表；MUST NOT 另立第三份字元級解析組（BL-00108）。
- **FR-044**: 走查還原工具與測試守衛 MUST 擴至能補回被撤之 seed 授權列：還原以基準快照回補 id 在上界以內而被刪之 seed 授權列（原 id 原值）、並清除復原回插之新 id 列、序列還原；走查還原工具另 MUST 回寫上界以內角色列之可變欄（首頁、狀態、名稱、描述、備註與審計欄；已知態觀察窗之 seed 角色寫入所需）；測試守衛同理（arm 時現讀、Drop 回補）；seed 列回補之實證＝測試守衛之整合測試與走查工具之自測合成案（Clarifications 第六題）；RUNBOOK §9c 契約同批；測試守衛 MUST 早於任一撤銷 seed 列之寫端單元、走查工具 MUST 早於前端 CDP。
- **FR-045**: 殘列不連坐（BL-00136 形①）MUST：兩支以 `sys_menu.created_by IS NULL` 錨 seed 之使用者路由案改錨 `casbin_rule.created_by IS NULL` 之 seed 政策列；測試件之直種現役政策同步落建立者；殘列演練納此形（dev 庫存在經寫端授予之殘列時全量測試全綠）；形②（使用者角色指派之殘列形）屬 007。
- **FR-046**: 帳本 MUST 於收刀兌現：`backlog_done` 5 條＝BL-00084／BL-00131／BL-00132／BL-00134／BL-00135；條文改寫 3 條＝BL-00045（收窄為 008 之 system-settings／audit 兩頁）、BL-00048（觸發收窄 007）、BL-00136（只剩形②）；敘述改寫 1 條＝BL-00133（歸檔表已有消費面〔復原刪列〕、撤銷原因新增）；
  反向確認 2 條＝BL-00047（migration 目錄恰 m0001／m0002、演進帳 entries 空）與 BL-00108（rust 側零第三份字元級解析組；FR-043）；BL-00137／BL-00138 之 `backlog_add` 與 NOTES「未決」兩筆 merge＋push 同意之補記 MUST 由本刀第一筆 events 事件承載、同批刪該未決條；`feature_close.adrs` 十支（plan 期九支＋收刀前 PATCH Amendment 一支）、`arch_impact` 以收刀時 diff 現算之活書節號為準；NOTES 下一步 specify 起手後改 006 進行中、收刀改 007。
- **FR-047**: 活書 MUST 於 feature branch 內改為現在式 as-built（04／05／06／08／10／11／12、RUNBOOK §9c／§11.2／§12／§13）；名詞表 MUST 新增「授權撤銷」「連動歸檔」「受保護授權列」「封死集」「候選集」「全量替換」「不可復原集」並改寫 reason gate、兩回收桶分立、判定面同步三條；
  本刀落地後成假述之現在式句 MUST 以機器枚舉逐處判讀改對（「只由移除面寫端觸發」類、「限 R_SUPER」類、「七款」→「八款」、「授權治理島」歸屬措辭→島 I；RL-0011）；C4-L2 拓樸不變（零新容器）。

**H. 測試與紀律**

- **FR-048**: 每支新端點 MUST 配 contract case＋覆蓋閘雙向＋case_key 綁定＋授權態矩陣對照凍結 seed 政策列；判定只呼單一進入點；handler 層零 path-root entity token；名冊閘（判定面、寫鎖、同步呼叫點）全綠。
- **FR-049**: 兩支入域寫端（updateRoleMenu／updateRoleButton）MUST 各配一支 advisory NOT-granted 等待機器證（64-bit key 拆兩欄比對；缺測則刪掉入域那行全測仍綠＝禁止形）；不入域之端點維寫端與 restorePolicy 不取域鎖之案在案。
- **FR-050**: 守門非 vacuous 自證 MUST（本條為自證索引：封死見 FR-022、旗標見 FR-027、reason gate 見 FR-028）：結構性封死變異自證；復原①～④腿各配負向測（各配「僅改正該腿即 Applied」之反臂）、⑤停用不擋配一 Applied 案；受保護整批拒負向測；reason gate 五值成員測（含負向臂翻）；可復原旗標與權威判定逐腿同判準測（①～④各一）；orphan skip 三維負向測；候選集射程（候選外現役列不動）一案；
  觸發矩陣特性鎖定測（授予面 Applied 觸發含空 diff、Rejected 不觸發、復原 Applied 觸發、NoOp／NotRestorable 不觸發）；自救路徑端到端一案（FR-032）；授予面與復原收場之取消安全各一案（FR-018）。
- **FR-051**: 測試環境紀律 MUST：真表測試配清理守衛（授權表與歸檔表帶界水位＋arm 當下現讀之序列值還原、角色與選單守衛）＋被撤 seed 列回補（FR-044）；凡需判定面持有之政策列經真判定面路徑造列；測試 MUST NOT 留下對 seed 列之變更；稽核斷言取水位窗、不寫絕對計數；測後 schema 三閘綠；CDP 走查排 schema-gate 驗收之後、或走查後照 RUNBOOK §9c 還原。
- **FR-052**: wire 裁判面 MUST：本刀新增之全部 wire 型（三維讀寫、候選讀、回收桶讀寫；回應＋請求＋query、實數以抽取為準）入受審名冊、各配正向＋反例裁判（受保護旗標為重點）；前端型別檢查綠；msg 鍵跨端閘三檔 locale 後端子樹與名冊雙向相等。
- **FR-053**: CDP 三方對照 MUST 覆蓋三顆彈窗、抽屜第三鈕、首頁下拉、回收桶頁（rev5 22080 vs rev6 32080、必要時 22089）；dev 帳號 Super／Admin／User；一律 127.0.0.1；CDP 操作一律 opus[1m]／xhigh；刻意分岔逐項登記（下表）；CDP 待觀察已知態候選（ADR⑥ 之候選甲、乙＝本檔 Edge Cases 候選①②，候選丙＝ADR⑧ 後果殘餘②）以實際操作觀察記錄、候選丁（ADR⑧ 後果殘餘③）以整合測試釘案記錄（ADR⑥ 定候選機制）。
- **FR-054**: 收刀 DoD MUST 全綠：容器內後端全量測試（全程 serial）＋contract 49 case＋前端型別檢查＋fork-delta-lint（新用途列名冊載入變異自證、範圍欄對賬腿、修改型只在授權檔）＋msg-key-gate＋wire 裁判 check＋schema 三閘＋路由產物冪等＋seed-view-gate＋docsync check／lint 零紅＋走查基準 diff rc 0＋CDP 三方對照（判準＝SC-010）；
  FR-001～FR-054 與 US1～US5 驗收場景全數對應至少一測試案、機器守或演練紀錄（tasks 逐條映射、無承載者即紅）。

**★ 軌道逐處登記（憲法 §III.2 必需三欄：位置＋改動內容＋upstream 衝突風險評估）**

風險判準（承 004／005 刀 spec、可覆算；量測面＝base-web upstream `example` tip `8be6f9ba`〔提交日 2026-05-13〕、量測日 2026-10-01、以 `git log --since` 計檔級 commit 數：12m＝2025-10-01 起、24m＝2024-10-01 起）：**高**＝近 12 月 ≥5；**中**＝近 12 月 1–4 或近 24 月 ≥5；**低**＝近 12 月 0 且近 24 月 ≤4。
**修改型再 +1 級**、純新增型與產物檔不加級。收錄準則：用途 (iii)(iv) 逐檔＋生成檔＋I18N 授權面之錨點檔；新增檔（端點彈窗、回收桶頁兩支、wrapper 與型別）屬新檔、不列——共 12 列。

| 位置（檔案） | 軌道·用途 | 型別 | 改動內容 | 12m／24m | 風險 |
|---|---|---|---|---|---|
| `src/views/manage/role/modules/menu-auth-modal.vue` | `BASE-WEB-MANAGE-PAGE-WIRING(iii)` | 修改型＋新增型 | 真勾選、受保護鎖定、首頁下拉接首頁讀寫、就緒守、請求世代、換角色清狀態 | 0／1 | 中（低＋1） |
| `src/views/manage/role/modules/button-auth-modal.vue` | 同上 | 修改型＋新增型 | 假資料移除、候選與現況接真、受保護鎖定、三守衛 | 0／0 | 中（低＋1） |
| `src/views/manage/role/modules/role-operate-drawer.vue` | `(iii)`＋`(ii)` | 新增型（(iii)）；(ii) 既有圈界內改寫 | 第三鈕「端點權限」＋掛新彈窗；BL-00131 修法 | 1／3 | 中（新增型不加級；(ii) 既有修改型之風險見 005 刀登記） |
| `src/locales/langs/en-us.ts` | `(iii)`／`(iv)`＋`BASE-WEB-I18N-WIRING(ii)` | 新增型 | `route:` 一鍵、`page:` 回收桶頁整節與第三鈕一鍵（新增型圈界）；既有 backend 塊內補 3 鍵 | **14／37** | **高** |
| `src/locales/langs/zh-cn.ts` | 同上 | 新增型 | 同上（簡中） | **15／38** | **高** |
| `src/typings/app.d.ts` | `(iii)`／`(iv)`＋`BASE-WEB-I18N-WIRING(iii)` | 新增型 | `Schema.page` 型節補鍵；既有 backend 型節補 3 鍵 | **13／32** | **高** |
| `src/router/elegant/imports.ts` | `(i)` 列產物檔紀律（(iv) 不重列；III-b） | 產物檔 | 外掛重算：新增回收桶頁 view | 1／5 | 中 |
| `src/router/elegant/routes.ts` | 同上 | 產物檔 | 同上 | 1／5 | 中 |
| `src/router/elegant/transform.ts` | 同上 | 產物檔 | 同上 | 1／6 | 中 |
| `src/typings/elegant-router.d.ts` | 同上 | 產物檔 | 同上 | 1／6 | 中 |
| `src/typings/components.d.ts` | §III 生成檔紀律（不入用途名單） | 產物檔 | 若引入新元件則工具重算（宣告行增刪） | 8／17 | **高** |
| `src/locales/langs/zh-tw.ts`（rev6 錨點檔） | `BASE-WEB-I18N-WIRING+`（新增型、不入名冊） | 新增型 | backend 子樹補 3 鍵（繁中譯文之家） | —— | 低 |

★本表最重要的一件事：兩顆授權彈窗近 24 月幾乎零改動、衝突機率低，但修改型面最大（勾選綁定改受控、守衛與首頁下拉皆落其中）——rebase 時一旦 upstream 動到彈窗即需逐行對照；緩解＝模板勾選綁定一行不動、改點以可寫 computed 承接。
i18n 三檔仍是基線最熱之檔；緩解＝一律新增型圈界、不與 upstream 行交錯。**rebase 處置**（承憲法 §III「rebase 同步紀律」）：修改型逐行 `原行:` 同步 upstream 現行版；生成檔與產物檔一律於 rebase 後以工具重算、絕不手工解衝突。
★逐處明細由實作期 fork-delta 標記落地並受 `fork-delta-lint` 機器強制（含範圍欄對賬腿）；本表為檔級風險評估與 rebase 處置索引。

**刻意分岔登記（CDP 對照用：與 rev5 HEAD 行為之刻意差異，逐項指承載）**

| 面 | rev5 HEAD | rev6 本刀 | 承載 |
|---|---|---|---|
| 角色抽屜送出狀態欄 | 恆送開啟時回填之狀態值 | 狀態與回填值不同才送 | FR-035、ADR⑧（BL-00131） |
| 刪除角色後之判定面同步 | 免同步 | 實際歸檔 ≥1 列即同步（005 刀既有；UI 不可見） | ADR-00043 決定 7、ADR-00044 決定 2 |
| 已知降級窗之條文 | 只記重試耗盡窗 | 記過渡窗與耗盡窗兩窗（文件面；UI 零差） | FR-020、ADR⑤ |
| 三維現況讀端之回應集 | 按鈕維與端點維回全部現役列（`rev5:ADR 0056`「讀端維持現狀」；選單維經治理域反查、實效已同候選內） | 回「現況 ∩ 候選集」（本刀後 R_SUPER 端點維 35 列、rev5 形 50 列；UI 零差係就讀端取態本身而言——彈窗只畫候選、候選外列不撤不授；候選集本身之差見下列） | FR-014、ADR④ |
| 端點候選集（getAllEndpoints） | 50 項（含 `rev5:007`／`rev5:008` 之使用者與稽核端點 15 支）⇒ 端點權限彈窗 50 葉、以 R_ADMIN 開啟時多一顆已勾之 getUserList 葉 | 35 項（本刀後路由表之受政策保護端點全集；後刀路由隨其刀進場）⇒ 35 葉 | FR-014、ADR④ |
| 三維寫端期望集鍵缺席或拼錯 | 收為空集＝合法全撤（struct 層 `serde(default)`） | 視同壞形 → `biz.role.notFound`、零變更；只有明確之空陣列才是合法全撤（UI 零差：前端包裝恆帶鍵） | FR-007、Clarifications 第七題 |
| 實作期新發現者 | —— | 逐項追加、CDP 開跑前凍結；CDP 中新發現者須經 user 親決（AskUserQuestion）才可入表、否則依 SC-010 判紅（2026-10-04 凍結時零項；CDP 中新發現 1 項＝端點權限彈窗群組序〔後端路由註冊序與 rev5 不同〕、user 親決修正對齊而不入表） | CDP 三方對照單元 |

### Key Entities *(include if feature involves data)*

- **授權政策**（`casbin_rule`、001 基線）：授權真相（資料庫優先）；`v0`＝角色代碼、`v1`＝標的（路由名／按鈕碼／路徑）、`v2`＝維度標記（`menu`／`button`）或 HTTP 方法；治理欄（受保護旗標、建立時間、建立者）對判定引擎轉接器不可見；本刀建授予寫入面與撤銷面，亦為封死謂詞之標的集來源。
- **授權歸檔**（`sys_casbin_policy_archive`、001 基線）：撤銷＝移入歸檔；完整快照＋來源角色 id（可空、誠實退化）＋reason（六值＝不可復原五值＋`endpoint_revoke`）；維度由列內容推導；可復原旗標為派生值（非欄）；本刀建讀端與復原端。
- **三維候選集**（概念實體）：選單維＝治理域選單；按鈕維＝治理域按鈕碼聯集；端點維＝路由表中受政策保護之端點全集——皆與判定面同源；全量替換之射程。
- **受保護授權列與封死集**（概念實體）：受保護授權列＝授權表受保護旗標為真之列（seed 19 列、皆屬 R_SUPER；撤不掉）；封死集＝其中端點維之（路徑,方法）集合（謂詞導出、鎖內現查；授不出 R_SUPER 以外）；與選單之受保護旗標（`sys_menu.protected`：不可刪、不可停用、不可改父）不同義。
- **選單序列化域**（終態成員）：005 刀既有七寫端＋本刀 updateRoleMenu／updateRoleButton；updateRoleEndpoints 與 restorePolicy 不入域。
- **判定面**（記憶體授權判定實體）：由真相全量導出；授予面 Applied 即同步（刻意例外）、移除面實際歸檔 ≥1 列才同步、復原 Applied 同步；保留上一份；兩個已知降級窗；前提單一行程。
- **授權回收桶頁**：獨立管理頁（seed 選單列 `manage_policy-archive`）；查詢列＝角色代碼×維度；列級復原門＝可復原旗標。
- **msg key 名冊（46 鍵）**：既有 43 鍵＋本刀 3 鍵；三檔 locale 後端子樹各為該語譯文之家。
- **★ 軌道名冊（Amendment 後）**：§III.2 管理頁軌道新增用途 (iii)(iv)；其餘軌道不變。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 路由與授權態對賬零漂移——路由表恰 49 條且與 seed 政策列路徑×動詞逐字對齊；契約覆蓋閘無缺案無殭屍案；授權態矩陣逐端點實測（Super 對十條皆通、Admin 對十條皆 `5003`）。
- **SC-002**: 拒因碼表自證——3 支新鍵每支各至少一案實際發出、名冊雙向閘綠（43→46）；13 碼矩陣可發碼與保留碼數量不變、零新錯誤變體；三檔 locale 後端子樹逐檔與名冊雙向相等、型節齊備。
- **SC-003**: 全量替換可驗——三維各一案「撤銷＋新授＋不動」同時成立且稽核恰一列；空 diff 一案（Applied、零變更、稽核一列、同步一次）；合法全撤一案；body 壞形收斂 `notFound` 一案（零變更）；orphan skip 三維各一；候選外現役列不動一案（R_SUPER 之未上線 seed 端點列）；停用選單不被撤銷一案＋誤用顯示域負向兩形（候選半誤用＝不撤而自生效集合與現況讀端消失、映射半誤用＝靜默升級為撤銷）。
- **SC-004**: 保護與封死非 vacuous——三維撤銷觸及受保護列各一案整批拒、零變更零稽核零同步；超管以 UI 可達路徑試授受保護端點給 R_ADMIN 必拒、R_SUPER 標的豁免一案；拆掉守門測試必紅；選單維受保護四列可授可見性一案；受保護列經撤銷路徑進歸檔之案數恆零。
- **SC-005**: 序列化域有機器證——兩支入域寫端各一案斷言併發者於 advisory 等待；端點維寫端與 restorePolicy 不取域鎖各一案。
- **SC-006**: 判定面同步可證——觸發矩陣特性測全在案（授予面三支 Applied 觸發含空 diff、Rejected 不觸發、復原 Applied 觸發、NoOp／NotRestorable 不觸發；同步結果計數增量相符）；授予成功後以單一進入點探測雙斷言 API 判定即時生效、撤銷成功後即時失效；失敗注入下舊面續放行 R_SUPER；授予面與復原收場之取消安全各一案（請求於判定面換上前被丟棄 ⇒ 同步仍完成）。
- **SC-007**: 授權回收桶可證——可復原旗標與權威逐腿同判準四案；①～④腿各一負向（含非 vacuous 反臂）＋⑤停用不擋一案；NoOp 一案（成功、歸檔列消費、零稽核、零同步）；識別不存在一案；選單／按鈕維列恆不可復原一案；自救路徑端到端一案；reason gate 五值成員測綠且負向臂已翻。
- **SC-008**: 零 migration 兌現——migration 目錄維持兩支、schema-gate 三閘照常綠、seed 計數不變；不可復原集擴列為純碼變更。
- **SC-009**: 測試與走查基建不連坐——dev 庫存在經寫端授予與撤銷之走查殘列時容器內全量測試全綠（BL-00136 形①）；整合測試以寫端撤銷 seed 授權列並復原後，清理守衛按原 id 回補、新 id 列清除、序列還原；走查工具自測之同形合成案綠，已知態觀察窗 restore 後全表基準 diff rc 0（含 seed 角色列可變欄回寫；Clarifications 第六題）。
- **SC-010**: CDP 三方對照（rev5 22080 vs rev6 32080；upstream 22089 作錨點——抽屜鈕數差與兩側不等時判 upstream 原形）以**結構清單逐項全等**為判準（抽屜三鈕、三顆彈窗之樹與勾選與鎖定形、首頁下拉可存可讀、按鈕彈窗無假資料、端點彈窗群組勾選、回收桶頁之欄位集合與列序與篩選與分頁與復原流程、toast 文案），任一項不等即紅；
  間距／字體／顏色只記入走查紀錄、不擋收刀；排除清單＝刻意分岔登記表各項（CDP 開跑前凍結；CDP 中新發現者須經 user 親決入表、否則判紅）＋已知態各款＋008 兩頁死項＋請求次數維度；CDP 待觀察已知態候選甲、乙、丙以「觀察路徑→症狀」實際操作記錄、候選丁以整合測試釘案記錄（ADR⑥）；角色抽屜只改名稱時請求不帶狀態欄（網路請求事件斷言）。
- **SC-011**: 前端與 fork-delta 全綠——前端型別檢查綠；修改型標記只出現於授權檔、base-web 變更檔集 ⊆ 授權檔集＋新增檔（機器斷言）；範圍欄對賬腿綠且變異自證；路由產物重算冪等；seed-view-gate 綠（具名豁免兩列）且變異自證；各新增圈界塊拔標記必紅。
- **SC-012**: 治理面全綠——憲法 1.7.0（收刀前 PATCH 實數化範圍欄後為 1.7.x）且 accepted 前 base-web 既有檔零 diff（git 史可證）；新用途兩列被名冊載入器讀進（變異自證）；docsync lint 零錯誤。
- **SC-013**: 交付鏈全綠（FR-054）——後端全量測試容器內 serial 全綠、SC-011 所列前端面與其餘全部閘零紅、手動端到端走查（入口 `http://127.0.0.1:32080`）全數通過、走查後 diff rc 0。
- **SC-014**（★收刀面子句於簿記 commit 後驗）: 治理帳本結清——十支 ADR（plan 期九支＋收刀前 PATCH Amendment 一支）全數 accepted 且 `feature_close.adrs` 列全；`backlog_done` 5 條、條文改寫 3 條、敘述改寫 1 條與 FR-046 相符；BL-00137／BL-00138 之 `backlog_add` 在事件帳；NOTES 下一步指 007；活書各節現在式更新、機器枚舉之假述零殘留。

## Assumptions

- rev5 為本機可達之唯讀參考庫（凍結 SHA 由 bootstrap 斷言）；應用碼全程重打字消化、註解 rev6 語境重寫、前代出處帶 `rev5:`；藍本取 rev5 HEAD 形（含 `rev5:B-116` 請求世代、`rev5:B-129` 換角色清狀態等 006 後修正）；
  翻案不帶回五項（facade 自開交易／取域鎖／寫稽核、稽核操作者缺席之降級欄形、deleteRole 免同步、測試守衛寫死序列值、msg 鍵字面構造）入 plan research 差異點表、烤入 implementer 防回歸清單。
- 005 刀八件底座已全兌現（選單域、重建換上、歸檔寫入件、reason gate 單點函式、治理域讀端、共用件、測試基建、名冊閘）；本刀純消費、不改基建語意；getAllPages、首頁讀寫端點與其 fetcher 已由 005 刀交付。
- **零 migration、零 seed 變更＝事實非選擇**（FR-002）；本刀非一次性遷移、Risk／Guard／Rollback 三欄表免附。
- **原 clarify 候選已於 brainstorm grilling 輪定案**（Q14～Q17，皆照 rev5）：R_SUPER 名下非受保護列可撤、自救走回收桶／全撤允許／復原撞現役＝NoOp／回收桶兩篩；另 Q12 並行覆蓋記已知態、Q13 生效兩層時點。`/speckit-clarify` 照常掃描、依專案紀律一題一問（不採內建一次三題形）。
- **稽核覆蓋沿 rev5 as-built**：三維寫端 Applied（含空 diff）一列、復原 NoOp 零稽核（FR-006／FR-030）。
- **判定面同步之單行程前提**：現行部署為單服務單實例；跨行程通知不在本刀（翻案觸發記 ADR-00043）。
- **前端語言面不擴**：沿用兩語 runtime locale＋繁中錨點檔（只承載後端訊息鍵）；`LangType` 與 zh-TW 語系註冊屬 BL-00138。
- **前端零測試框架**：前端執行單元之 TDD 迴圈退化為型別檢查＋機器斷言＋兩段 review＋CDP 對照走查。
- **Amendment 與 ADR 親決時點**：plan 期全數產草稿；Amendment 條文於 U0 逐款親決；施工前提 ADR 另顆；ADR⑥⑦ 於治理單元親決，治理單元排在 CDP 三方對照單元之後（005 刀形：觀察定稿在前、親決在後）。
- **TDD 發射前置**：組裝形 workflow 模型家由 ADR-00056 固定（opus[1m]／xhigh）；CDP 操作一律 opus[1m]／xhigh；本機缺他機單元範本時由入庫範例經組裝器起手；base-web pnpm 與其逾時一律放容器內（LL-00038／LL-00039）。
- **走查與 CDP 基準本機自取**：首次真登入走查前 snapshot（RUNBOOK §9c）；rev6 stack 走查前實看容器態、必要時重建；CDP 基準重取、不沿用 005 刀產出。
- **實作紀律引用**（非本 spec 新拍板）：rust build／test 容器內全程 serial；每單元 pin bump；review 只讀不寫；rev5 樹唯讀令烤入 agent prompt。
- **stakeholder 判定承 001～005 刀前例**：本刀 stakeholder＝admin 後台之超級管理員與 workspace 維護者；spec 中的端點路徑／碼／政策座標／軌道名／閘與工具名／常數係交付物座標（WHAT）與治理設施引用，非實作技術選型（HOW）。

### Out of Scope

- **no-escalation 本體**（BL-00048；掛點不動）——007；unlockLogin 授出後之帳號維守門同屬之。
- **使用者域一切**（seed 68 `updateUserSessionPolicy`〔受保護、未上線；謂詞式封死下上線即自動納管〕、角色指派寫端、密碼面）與使用者角色指派之殘列形（BL-00136 形②）——007。
- **系統設定頁與稽核頁**（BL-00045 之兩頁）——008；**授權歸檔表之保留期與清理政策、軟刪×歸檔事後對賬掃描**（BL-00133）——008 或首個背景 job 刀。
- **列表排序能力**（ADR-00058 決定 3）；**008 設定頁之呈現**（ADR-00057 後果）。
- **「前端 UI 刀」兩項**（`LangType` 與 zh-TW 語系註冊、自助頁手機驗證）——BL-00138（007 brainstorm 起手前重評）。
- **即時推播刷新已登入者之選單與按鈕顯隱**（Q13）；**增量式授權寫入介面**；**並行編輯之版本比對或差量提交**（Q12）；**受保護旗標之設定／解除管理介面**（永不提供）。
- **選單維受保護四列之封死**（已知態、FR-023）。
- **判定面跨行程通知**（多實例部署時再立 ADR）；**過渡窗之關窗**（採記窗、不改碼；Q6）。
- **RULES 改動**：預期零 RULES 表列改動（RULES-VERSION 不變）；若實作期需要，依輕量紀律另行拍板。
