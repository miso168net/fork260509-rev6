---
id: "ADR-00081"
title: 角色與選單管理之已知態（續行 ADR-00068）——決定 4① 收回（觀察一律自建帳號持自建角色）；款 7 解除（`rev5:B-145` 結案）、款 18 解除（三頁按鈕依碼顯隱）；款 9 部分解除（使用者域寫端與 unlockLogin 帳號維受包含規則；可授出集重算為 30 支）；款 10、11、17、20 改述（按鈕碼顯隱後之可見效果／相異 R_SUPER 帳號可達／只授目錄之 `/403` 限排在個人中心之前者／UI 外送停用值生產可達並實測）；款 21 新增（seed 名稱照原字）；其餘款續行（現行十八款）
date: 2026-10-05
status: superseded
supersedes: ["ADR-00068"]
superseded_by: [ADR-00103]
provenance: "007-user-password-admin 之 spec FR-056⑧、FR-001／FR-002（ROUTES 49→61、政策保護端點 35→45）、FR-020、FR-021～FR-024、FR-040、FR-042、FR-044、FR-048、FR-057、FR-058、FR-060（BL-00048 收）、FR-065（ADR-00070 觸發器④與本 ADR 款 20 可達性實測）、SC-004、SC-010、SC-014、US1 AS4／AS10、US4 AS1～AS11、Edge Cases「包含規則與委派」「前端與按鈕碼」「自鎖防護與 seed 基線」「測試與走查基建」、刻意分岔登記表（持停用角色之抽屜、角色頁與選單頁按鈕、R_SUPER 角色與選單六碼）；brainstorm §0 Q6／Q7／Q8／Q13、GR1a、§0 主線工程判斷⑥⑦⑬、§3 §1 ADR 待立⑧；被續行面＝ADR-00068 二十款與決定 1～4（body 已 accepted 不可變、rev6 無部分翻案機制＝ADR-00011 決定 5；續行鏈 ADR-00045→ADR-00068→本 ADR）；ADR-00070 翻案觸發器第四條（使用者角色指派寫端落地＝誤擋面生產可達）；ADR-00064 決定 1／5／6（封死集謂詞與射程外兩項）；藍本＝rev5:B-145（持停用角色之指派於抽屜不可見、rev5 至凍結未解）、rev5:007 brainstorm Q10（使用者頁七碼逐鈕顯隱）、rev5:L-046／rev5:L-054（已知態須以實際操作觀察、無可觀察實例須附機器反證）；draft 於 plan 期落 feature branch、續行款沿 006 刀實測症狀、解除款之證據與改述款之症狀於本刀 CDP 三方對照單元實際觀察後定稿、user 親決於治理單元（accepted 同顆補 supersedes 並改 ADR-00068 狀態）；親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [role-menu-crud, authz-governance, user-password-admin, known-state, by-design]
---

## 背景

- ADR-00068 集中承載角色與選單管理之已知態（款 1 已於 006 刀解除；款 2～20 現行＝十九款）。本刀（007 user-password-admin）使下列各面到期或失準：
  - **決定 4①**（CDP 觀察得對 seed 角色寫入、帳號取 seed 帳號之具名例外）：唯一理由「本刀無使用者角色指派寫端、自建角色無帳號可持有」隨本刀之 addUser／updateUser 消失；該決定無翻案觸發器，須由續行處置。
  - **款 7**（翻案觸發＝使用者域刀接真使用者頁、含複核 `rev5:B-145`）：Q13 定灰色保留選項、清單列帶持有角色之 id、代碼與名稱。
  - **款 9**（翻案觸發＝007 刀島 I〔含 I7 包含規則〕進場）：使用者域八支寫端與 unlockLogin 帳號維掛包含規則（ADR-00075；spec FR-021）；路由表新增十支，可授出集須重算。
  - **款 10、款 13**：其可達路徑經角色頁編輯抽屜，而抽屜之開啟本刀起受 `role:edit` 按鈕碼顯隱（Q8）；按鈕維受保護列自 m0003 起由 0 列成 6 列（GR1a）。
  - **款 11**（翻案觸發＝007 刀使第二個帳號持有 R_SUPER）：持 R_SUPER 者之 A＝全集，得將 R_SUPER 指派他帳號。
  - **款 18**（翻案觸發＝角色、選單或使用者頁加入按鈕碼 gating）：三頁一起做（Q8；spec FR-048）。
  - **款 20**（翻案觸發＝使用者角色指派寫端落地使此面生產可達）：自建帳號得同持啟用與停用之角色。
- ADR body 已 accepted 不可變（GT-04）；rev6 無部分翻案機制（ADR-00011 決定 5）⇒ 整顆續行（同 ADR-00068 之於 ADR-00045）。
- 款 9 之量測（2026-10-05、以 `rust-api/server/src/router.rs` 之 ROUTES 與 `rust-api/migration/src/m0002_baseline_seeds.rs` 現讀；施工與觀察以資料庫現況為準）：本刀前政策保護端點 35 支、封死集在路由表者 14 支、可授出 21 支；本刀後政策保護端點 45 支（spec FR-001）、封死集 15 個（路徑,方法）（謂詞＝ADR-00064 決定 1；seed 受保護之 HTTP 方法列恰 15 個鍵，m0003 只動按鈕維、不改此數）且自本刀起全數在路由表（`/systemManage/updateUserSessionPolicy` 隨本刀註冊）、可授出 30 支（原 21 支＋使用者域九支）；seed 另有非受保護政策列 5 支尚未上線（稽核域：`getOperationLog`／`getAccessLog`／`getLoginAttempt`／`getSessionEvent`／`purgeAuditLog`）＝其路由註冊即自動成為候選（ADR-00066 決定 4）。
- 現在式面量測（2026-10-05；只供背景、施工以決定 2 之指令現算為準）：`python3 tools/docsync errata ADR-00068` 全 repo 127 處命中；扣除史料面（brainstorms、specs、reviews）、生成鏡像（`docs/generated/`）、事件源與 ADR 檔（`docs/arc42/decisions/`）後——外層現在式 8 檔 24 處（逐檔 `grep -o` 計：`docs/arc42/06-runtime-view.md` 5、`docs/arc42/08-crosscutting-concepts.md` 3、`docs/arc42/10-quality-requirements.md` 1、`docs/arc42/11-risks-and-technical-debt.md` 3、`docs/arc42/12-glossary.md` 5、`docs/ops/BACKLOG.md` 2、`docs/ops/RUNBOOK.md` 4、`docs/ops/reference-src/code-gate-contracts.md` 1）＋待判讀 3 檔 5 處（`docs/ops/NOTES.md` 之 006 刀收刀條 1、`docs/ops/LESSONS/` 兩檔 4）；rust-api 8 檔 16 處（`server/src/handler/ip_rule.rs` 1、`server/src/handler/menu.rs` 1、`server/src/handler/role.rs` 1、`server/src/handler/route.rs` 2、`server/src/handler/throttle.rs` 1、`server/src/model/facade/sys_casbin_archive.rs` 1、`server/src/router.rs` 1、`server/tests/contract.rs` 8）；base-web 0 處。款數句「十九款」現在式 2 處（活書 06、活書 11 各 1）＋NOTES 006 刀收刀條 1 處（現在式指針，見決定 2）。

## 決策驅動因子

- 角色與選單域已知態單一出處；ADR-00068 已到期之款與決定 4① 於同一顆續行中結清、不留對沖註。
- 每款可到期、可觀察（`rev5:L-046`）；CDP 排除清單（spec SC-010「已知態各款」）逐款可指。
- 觀察紀律回到常態：走查與測試之寫入一律對自建帳號與自建角色（spec FR-058、Edge Cases「測試與走查基建」）。
- 目標零新 BACKLOG：後續工作指向既有條目（BL-00045）或各款翻案觸發器。

## 考慮過的替代案

1. **ADR-00068 維持 accepted、本刀到期款另立一支**：款 7、款 18 已解除卻仍以 accepted 字面宣告其現況（「提交仍假成功」「授撤零可見效果」），現在式面須同時引兩支 ⇒ 權威鏈倒掛；棄。
2. **決定 4① 續留 seed 帳號與 seed 角色例外（只改理由句）**：例外之唯一理由消失後續留＝無理由之破紀律例外（拍板級）；且本刀起 seed 帳號之指派與欄值被改屬殘列不連坐之具名排除形（spec FR-058）；棄。
3. **款 11 以限制 R_SUPER 之指派消解**（只許 seed Super 持 R_SUPER）：與島 I7「持 R_SUPER 者 A＝全集」之語意相左、屬範圍變更；棄（續作已知態、改述可達面）。
4. **款 9 以包含規則擴至角色域、IP 域與授權回收桶復原而整款解除**：Q7 已拍不擴；棄。
5. **款號重排為連號**：現在式面「ADR-00068 款 N」改指須逐處查表換號、易錯；棄（款號保留、空號以對照表可查）。

對所選方案跑同一反例（RL-0013）：收回決定 4① 後，原需 seed 角色之觀察（款 16 停用持有角色、款 17 撤 `home` 授權）是否被迫改動 seed 列？不會——自建角色 X 由 Super 建立、以 addUser／updateUser 指派給自建帳號，停用與重新啟用落在 X、首頁兜底之構造改為「X 只持該目錄之授權」，seed 列零寫入。保留款號而款 7、款 18 無現行依據，是否留下懸空引用？不會——款號對照表明示解除，現在式面引該兩款之句依決定 2 改寫為現況敘述、不改指成「本 ADR 款 7／款 18」。成立。

## 決定

本 ADR 續行並將 supersede ADR-00068（本 ADR accepted 那一顆同批補 `supersedes: ["ADR-00068"]`、ADR-00068 之 status 改 superseded；`superseded_by` 由 `python3 tools/docsync generate` 回填）。ADR-00068 決定 1～4 一律對應本 ADR 同號決定。

（草稿；續行款沿 006 刀實測症狀；解除款之證據與改述款之「觀察路徑→症狀」於本刀 CDP 三方對照單元實際觀察後定稿；user 親決於治理單元。實作單元收單後，本刀文件 as-built 單元（2026-10-14）依碼面補解除款之碼面證據指針與改述款之實作面＝各款「碼面證據（as-built）」子項，以檔與函式或測試名指、不用行號；觀察症狀與款號之定稿不在其內。）

1. **ADR-00068 二十款與決定 4① 逐款處置**：款號保留、不重用——「ADR-00068 款 N」一律對應本 ADR 款 N；解除之款其號不再配。現行款＝款 2～6、款 8～17、款 19～21（十八款）。

| ADR-00068 原款要旨 | 本 ADR | 本刀處置 | 理由與證據 |
|---|---|---|---|
| 款 1 角色頁授權彈窗假成功（006 刀已解除） | 款 1 | 空號續存 | 無現行依據 |
| 款 2 system-settings／audit 兩列選單項為死項 | 款 2 | 續行 | 兩頁屬 008 刀（BL-00045） |
| 款 3 新建或復原之選單須經授予才於側欄現 | 款 3 | 續行（觀察前提改寫＝決定 4①） | 本刀不動選單新增與復原流程 |
| 款 4 新增或復原之按鈕碼須經授予才有人持有 | 款 4 | 續行（同上） | 同上 |
| 款 5 新建選單顯原始 i18n 鍵字面 | 款 5 | 續行 | 本刀不動選單新增流程與 `route:` 樹之登記方式 |
| 款 6 治理清單兩列顯路由裸鍵 | 款 6 | 續行 | 兩頁屬 008 刀 |
| 款 7 getAllRoles 之 UI 消費者＝使用者頁新增抽屜（提交假成功、首載 `4040`、`rev5:B-145` 待複核） | 款 7 | **解除** | 使用者頁接真（spec FR-047）；`rev5:B-145` 結案（Q13、spec FR-020） |
| 款 8 治理清單分頁列凍結＋無 size 全取 | 款 8 | 續行 | 本刀不動選單治理清單 |
| 款 9 可授出端點之下放效果（含 unlockLogin 無帳號維守門） | 款 9 | **部分解除＋改述** | 使用者域八支寫端與 unlockLogin 帳號維受包含規則（Q6、Q7；spec FR-021、FR-023）；可授出集 21→30 支；角色、選單、IP 域與 unlockLogin 來源維續存 |
| 款 10 選單維受保護四列看得到、封死功能點不動 | 款 10 | **改述** | 角色與選單頁按鈕依碼顯隱（Q8）⇒ 可見效果多一層按鈕維；按鈕維受保護六列（m0003）同理不入封死集 |
| 款 11 並行編輯後送出者整份覆蓋 | 款 11 | **改述** | 相異 R_SUPER 帳號可達（指派寫端；島 I7 A＝全集） |
| 款 12 授權回收桶復原 NoOp 零稽核 | 款 12 | 續行 | 本刀不動授權回收桶 |
| 款 13 首頁下拉選值即寫 | 款 13 | 續行（可達路徑註記 `role:edit`） | 本刀不動選單權限彈窗 |
| 款 14 可授予指向不存在 view 之自建選單 | 款 14 | 續行（觀察前提改寫） | 本刀不動選單寫端之 view 驗證 |
| 款 15 選單維與按鈕維之授權撤銷只剩閱覽 | 款 15 | 續行 | 本刀不動不可復原集 |
| 款 16 授權回收桶復原不擋停用角色 | 款 16 | 續行（觀察前提改寫） | 本刀不動復原固定序 |
| 款 17 只勾目錄之無子項死項與首頁兜底落 `/403` | 款 17 | 改述（觀察前提改寫＋後半射程收窄） | 自助白名單使 `user-center`（seed order 999）恆在可見樹（ADR-00077）＝只授 order＞999 之目錄者兜底改落個人中心；本刀不動選單維父子關係與首頁兜底規則 |
| 款 18 `role:*`／`menu:*`／`user:*` 按鈕碼授撤零可見效果 | 款 18 | **解除** | 三頁逐鈕顯隱（Q8；spec FR-048） |
| 款 19 兩分頁下角色抽屜三欄舊值覆寫 | 款 19 | 續行 | 其翻案觸發＝誤蓋實際發生等；「第二個可編輯角色之人」自 006 刀起即可經授予達成、非本刀所觸發 |
| 款 20 UI 外對已停用之自身所屬角色送停用值照擋 | 款 20 | **改述＋實測** | 指派寫端使生產可達（ADR-00070 翻案觸發器第四條） |
| （無；本刀 CDP 繁中審讀新發現） | 款 21 | **新款** | seed 角色名與選單樹節點名照庫存值顯示、不經譯文（側欄與治理清單之選單名經譯文、不在射程） |
| 決定 4①（seed 帳號＋seed 角色觀察例外） | 決定 4① | **收回** | 唯一理由消失；回紀律常態（spec FR-058） |

2. **現在式面改指**：現在式面引用 ADR-00068 之處改指本 ADR 同號款（款號一對一）；引款 7、款 18 之句改寫為現況敘述（已解除、無對應款）；引款 9 之 unlockLogin「授出後無帳號維守門」句改寫為現況（帳號維受包含規則、來源維不套）——該句多與 ADR-00069 款 1 之「API-only、無 UI 按鈕」同句並存，兩支 ADR 之改指同處施工、互為前提（ADR-00082 決定 2）；角色與選單已知態之計數句「十九款」改為本 ADR 定稿之現行款數（accepted 時現算；本稿＝十八款）並帶 ADR 號——★舊數量詞「十九款」與 ADR 號並掃、命中後以同句 ADR 號判定歸屬（IP 域之計數句依 ADR-00082 決定 2 另改；RL-0011 四形）；同批種子另含「無帳號維守門」「授撤零可見效果」「使用者域刀」。★NOTES 之「006 已收刀」條（「已知態現行集＝ADR-00068（角色與選單十九款…）…其翻案觸發器即後續刀之承接點」）為指向後續刀之現在式指針：本 ADR accepted 後即失準，MUST 於本刀收刀簿記同顆整句重寫或刪條、不可原樣保留（LL-00064 守法①）；`docs/ops/LESSONS/` 兩檔之命中屬事故史述、不改。判定＝`python3 tools/docsync errata ADR-00068` 全 repo 命中扣除史料面（brainstorms、specs、reviews）、生成鏡像（`docs/generated/`）、事件源與 ADR 檔（`docs/arc42/decisions/`；accepted body 不可變——含 ADR-00070 對款 19／款 20 之引用——本刀續行 ADR 草稿自身〔本 ADR 與 ADR-00082〕對被續行者之引用屬續行面本身）；兩子庫以 `git -C <子庫> grep -o ADR-00068` 對賬（子庫只改註、走兩段式 commit）；處數以施工時同指令現算、改完復掃（量測值住背景、不作施工基準）；實際改指屬本刀治理單元（與本 ADR accepted 同批）。
3. **證據定稿與新款配號（改寫 ADR-00068 決定 3）**：ADR-00068 決定 3 之候選四款已於 006 刀治理單元定案（款 17～20、user 2026-10-04 親決），其結果由本 ADR 同號款續行；本 ADR 無候選款。本刀之解除款（款 7、款 18）之解除證據與改述款（款 9 之使用者域列與 unlockLogin 列、款 10、款 11、款 17 之後半射程、款 20）之症狀，於本刀 CDP 三方對照單元實際觀察（純後端面以整合測試，決定 4③）後定稿（`rev5:L-046`）；觀察與本稿不符者以實測改寫後才 accepted。CDP 走查期新發現之角色與選單域已知態，經治理單元 user 逐款親決採用者依定案序自款 21 起配號（附觀察路徑→症狀與翻案觸發器），不採者不入。
4. **觀察前提與觀察形（改寫 ADR-00068 決定 4）**：
   - ①**收回 seed 帳號與 seed 角色之觀察例外**（ADR-00068 決定 4①；006 刀 spec Clarifications 2026-10-01 第五題之具名例外）：各款觀察路徑凡需「持角色 X 之帳號」者，X 一律取自建角色、帳號一律取持 X 之自建帳號（Super 以 addUser 建立並指派，或以 updateUser 改指派）；R_SUPER 與其餘 seed 角色名下零寫入、seed 帳號之指派與欄值零寫入。006 刀以 seed 角色與 seed 帳號實測之症狀記錄續有效（症狀出自寫端與判定面之語意、不因持有者為 seed 或自建而異）；各款字面中之「seed 角色 X」「持 X 之 seed 帳號」自本 ADR 起一律讀作「自建角色 X」「持 X 之自建帳號」。
   - ②**前後套走查基準**：觀察前以 `tools/walkthrough-baseline.py snapshot` 取基準；觀察後 `restore`＋重啟 rust-api，再以 `diff` rc 0 證回基準（RUNBOOK §9c）。★射程界：該工具本刀起之還原面（spec FR-057）含帶界之使用者列（觀察建立之自建帳號與其指派刪除、序列回值）、被刪之 seed 指派回補、seed 帳號可變欄回寫、經手表清理、改密節流鍵前綴，並於寫入前以遷移帳前置拒用早於現行遷移之基準、seed 模式目標態與兩模式之系統設定比對改以凍結 seed ⊕ 演進登記合成（spec FR-057 (a)(b)）；自建角色、自建選單與授權列沿角色／選單域既有之帶界還原與授權表快照。還原判準＝`diff` rc 0＋RUNBOOK §9c 第 4 步後段之 `python3 tools/schema-gate.py check`（gate2 逐列比對 seed）綠。
   - ③**觀察形**：可經 UI 觀察者走 UI 路徑（CDP）；純後端面（無 UI 入口之端點、「直打端點」之放行或 `5003`、包含規則之拒、稽核列數、判定面同步計數）以整合測試觀察——清理守衛下構造同一前提、斷言同一症狀；角色標的一律取自建角色、帳號取測試件建立之自建帳號（以測試件直種指派列〔ADR-00044 決定 3 之直種形〕或經 addUser 使其持有；spec FR-058「走查與測試之寫入一律對自建帳號」）；測試不留 seed 列變更、稽核斷言取水位窗（spec FR-062）。

**各款（現行依據）**：

- **款 1**：解除（006 刀；無現行依據；號不再配）。
- **款 2 system-settings／audit 兩列選單項為死項**：側欄可見（展開態標題顯路由裸鍵 `route.manage_system-settings`／`route.manage_audit`）。觀察路徑＝Super 登入→側欄「系統管理」→點該項⇒不跳轉、停在原頁、零 API 請求、零 toast，console 拋未捕捉例外 `Error: No match for {"name":"manage_system-settings","params":{}}`（`manage_audit` 同形）；直打 `/manage/system-settings`／`/manage/audit`⇒全頁 404（blank 版面＋「返回首頁」、網址保留）（症狀字面沿 ADR-00068 款 2 之 006 刀 U16 實測）。
- **款 3 新建或復原之選單須經授予才於側欄現（含 R_SUPER）**：新建零授權（兩步流第一步）；刪除時其選單維授權以 `menu_soft_delete` 連動歸檔、屬不可復原集，選單回收桶復原不回灌、授權回收桶亦不可復原 ⇒ 第二步＝超管於角色抽屜「菜單權限」彈窗勾選授予；持被改角色之使用者於下次載入頁面時側欄更新（生效兩層時點＝ADR-00063 後果「生效語意兩層時點」）；管理列表可見可編。觀察路徑＝新增選單→展開側欄⇒新列不現；直打其路由路徑⇒全頁 404（網址保留、非 403）；角色列表→編輯自建角色 X（前提＝決定 4①）→「菜單權限」→勾該選單→確認→持 X 之自建帳號重新整理⇒側欄現。
- **款 4 新增或復原之按鈕碼須經授予才有人持有（含 R_SUPER）**：`getUserInfo` 之按鈕碼取自判定面、前端 `hasAuth` 無超管旁路 ⇒ 授予前對應按鈕不現；射程＝不屬治理域其餘選單之碼（與其餘選單共持且已授予之碼照舊有人持有，例：新選單沿用 seed 之 `B_CODE1`）；選單刪除時其獨有按鈕碼授權以 `menu_soft_delete` 連動歸檔、不可復原 ⇒ 復原後同須重授。第二步＝「按鈕權限」彈窗勾選授予。觀察路徑＝建帶新按鈕碼之選單→Super 重新登入⇒`getUserInfo` 之按鈕碼集合不含該碼；「按鈕權限」彈窗授自建角色 X 該碼→持 X 之自建帳號重新登入⇒其按鈕碼集合含該碼。
- **款 5 新建選單於治理清單顯原始 i18n 鍵字面**：新增彈窗填路由名時自動帶 i18nKey＝`route.<路由名>`、`route:` 樹零新增、`$t` 查無鍵回退字面。觀察路徑＝新增選單→治理清單「選單名稱」欄⇒顯 `route.<路由名>`（字面沿 ADR-00068 款 5）。
- **款 6 治理清單兩列顯路由裸鍵**：system-settings／audit 兩列（id 9／77）「選單名稱」欄顯 `route.manage_*`、22080 顯簡中；側欄展開態同二鍵（該兩頁進場刀帶入譯文時解除；帳＝BL-00045）。
- **款 7**：解除（本刀；號不再配）——使用者頁接真（spec FR-047）：新增與編輯抽屜之提交為真寫入、首載 getUserList 回清單（不再 `4040`）。`rev5:B-145` 結案（Q13、spec FR-020）：清單列帶持有角色之 id、代碼與名稱；抽屜以「（已停用）」灰色選項呈現持有之停用角色（不可新選、可移除、送出時預設保留），角色欄只在改動時送——持停用角色之帳號照常可改其餘角色。getAllRoles 之口徑（僅活性且啟用）不變。解除證據＝本刀 CDP 三方對照（spec 刻意分岔登記表「持停用角色之抽屜」列；rev5 HEAD 為整欄鎖住並提示）。
  - 碼面證據（as-built）：清單列之持有角色＝rust-api `server/src/handler/user.rs` 之 `UserRecord`（`roles` 元素型 `UserRole` 帶 `id`／`roleCode`／`roleName`；口徑＝T：含停用、不含已軟刪，回收桶列恆 `[]`），真 seed 釘＝`server/tests/contract.rs` 之 `user_list_rows_real_seed`、wire 裁判＝`server/tests/wire_schema.rs` 之讀端冊 `AUDITED_READ_DEFS`（含 `Api.UserAdmin.UserRecord`／`Api.UserAdmin.UserRole`）；持停用角色之帳號照常可改其餘欄與角色＝`server/src/handler/user.rs` 之 `update_user_replaces_the_role_set_by_difference_and_never_reloads`。前端：灰色保留選項＝base-web `src/views/manage/user/modules/user-operate-drawer.vue` 之 `getRoleOptions`（候選外之持有角色另立 `disabled` 選項、標籤接 `page.manage.user.roleDisabledTag`）與 `renderRoleTag`（灰項保有移除鈕）；送出＝同檔 `handleSubmit`（`roleIds` 只在改動時帶）經 `src/service/api/rev6-user-admin.ts` 之 `fetchAddUser`／`fetchUpdateUser`；清單資料源＝同一包裝檔之 `fetchGetUserList`。
- **款 8 治理清單分頁列凍結＋無 size 全取**：分頁列位置不動、頁碼 1、每頁 0、整列停用、前綴顯真實筆數（`rev5:ADR 0060` 形）；後端無 size 回全部頂層；前端把回應 size 回寫每頁筆數、首載與頂層列數增減時各多一發重取（畫面不變；CDP 排除請求次數維度）。觀察路徑＝進選單管理頁⇒前綴「共 N 條」顯真實頂層數、頁碼 1 選中且停用、左右箭頭停用；無參 `getMenuList/v2` 回 `size`＝頂層數（22080 回 `size=100`）（字面沿 ADR-00068 款 8）。
- **款 9 可授出之政策端點授予非 R_SUPER 角色後之下放效果（本刀部分解除）**：可授出集＝路由表之政策保護端點 − 封死集（謂詞＝ADR-00064 決定 1；射程外二＝同 ADR 決定 6；以資料庫現況判定、不寫死）；量測 2026-10-05＝30 支（見背景）。授出之寫入照常落操作稽核（操作者＝受讓帳號）、UI 不加警示（006 刀 brainstorm Q3）。
  - ★**本刀解除之半**＝使用者域八支寫端與 unlockLogin 帳號維：受讓者之操作受包含規則（T⊆A∧N⊆A；A＝操作者現役角色集、持 R_SUPER 者 A＝全集；ADR-00075、spec FR-021）——不得操作持有自己未持角色之帳號、不得指派自己未持之角色；違者 `5003`、零變更、零稽核、一則 warn。BL-00048（unlockLogin 帳號維守門）隨本刀收（spec FR-060）。
    - 碼面證據（as-built）：判定本體＝rust-api `server/src/auth/no_escalation.rs` 之具名純函式 `assert_no_escalation`；使用者域八支寫端經 `server/src/handler/user.rs` 之單一包裝 `guard_no_escalation` 於鎖內判，unlockLogin 帳號維經 `server/src/handler/throttle.rs` 之 `judge_account_unlock` 委派同一包裝；包裝之生產使用點檔集由 `server/tests/authz_entrypoint_lint.rs` 之名冊 `NO_ESCALATION_CALL_FILES` 守；中介層 `server/src/auth/enforce.rs` 之 `no_escalation_check` 續恆放行（ADR-00075 決定 5）。行為釘＝`server/src/handler/user.rs` 之 `inclusion_rule_refuses_two_ways_per_consumer_and_admits_peers_and_full_scope`（八支各兩負一正、停用角色計入 T、A＝全集正向、拒後零變更零稽核）與 `guard_no_escalation_denial_logs_one_warn_with_exactly_three_fields`；`server/src/handler/throttle.rs` 之 `account_dimension_applies_the_inclusion_rule_and_refusals_write_nothing`；`server/tests/contract.rs` 之 `unlock_login_account_dimension_applies_the_inclusion_rule_real_seed`。
  - ★**續存之半**＝角色域、選單域、IP 域寫端、unlockLogin 來源維與授權回收桶復原不掛包含規則（Q7；ADR-00075 射程）：其下放效果照下表。
    - 碼面證據（as-built）：unlockLogin 來源維不套包含規則＝rust-api `server/src/handler/throttle.rs` 之 `source_dimension_skips_the_inclusion_rule`；他域寫端零消費點＝上列名冊 `NO_ESCALATION_CALL_FILES` 只收 `handler/throttle.rs` 與 `handler/user.rs`。可授出集之 as-built 復量（2026-10-14；以 `server/src/router.rs` 之 `ROUTES` 與 `migration/src/m0002_baseline_seeds.rs` 現讀，m0003 不動端點維之受保護旗標）＝政策保護端點 45、封死集 15（全數在路由表）、可授出 30，與背景量測同；seed 端點維政策列不在路由表者恰稽核域五支。
  - ★**包含規則之極限形**（by-design；spec US4 AS4／AS5）：零角色帳號（T＝∅）與回收桶中之帳號（指派已隨刪除硬刪）對任何受讓者恆過包含規則——受讓 updateUser 者得對零角色帳號指派其自身現役持有之角色；持相同角色集者同級互管。
  - 觀察前提＝決定 4（X 取自建角色、帳號取持 X 之自建帳號、前後套走查基準）。觀察路徑＝Super 以「端點權限」彈窗授 X 該支→持 X 之帳號直打該端點（判定面同步換上後即時生效）⇒放行、非 `5003`；UI 入口另需該頁選單維與按鈕維授權。寫端之放行一律以不改 seed 列值之探針觀察：標的取自建列，或送不合法 body 得業務拒 `2222`——授權層（`require_policy`）包在 handler 外先跑，得 `2222` 即證已過授權層（使用者域之 body 缺席＝`biz.user.notFound` 即此形）；不對 seed 列或 R_SUPER 名下做實際寫入。包含規則之拒與「含 R_SUPER」類效果以整合測試觀察（決定 4③；spec FR-025）。逐支效果：

| 端點 | 授予 X 後之效果 | 授出後仍擋住者（既有守門） | UI 入口 |
|---|---|---|---|
| `GET /systemManage/getIpRuleList` | 可讀 IP 規則清單 | —— | 選單列 `manage_ip-rule`（非受保護、可授） |
| `POST /systemManage/addIpRule` | 可新增阻擋／放行規則、全站即時生效（含 R_SUPER 之來源） | 防自鎖只以操作者自身來源判定（`biz.ipRule.selfLock`）⇒ 擋不住「封鎖他人來源」 | 同上＋按鈕碼 `ipRule:add` |
| `POST /systemManage/updateIpRule` | 可改任一現役規則 | 同上 | 同上＋`ipRule:edit` |
| `DELETE /systemManage/deleteIpRule` | 可軟刪任一現役規則 | 同上 | 同上＋`ipRule:delete` |
| `POST /systemManage/restoreIpRule` | 可復原已刪規則 | 同上 | 同上＋`ipRule:restore` |
| `POST /systemManage/unlockLogin` | 帳號維：可解除「全部指派角色 ⊆ X 之現役角色集」之帳號之鎖定（持 R_SUPER 之帳號不可解）；來源維：可解除任一來源之鎖定 | 帳號維＝包含規則（本款此半解除）；來源維＝無（不套包含規則＝Q7、by-design） | 使用者頁列操作「解鎖登入」（`user:unlock`；帳號維）、IP 規則頁表頭「解鎖來源 IP」（`ipRule:unlock`；來源維；m0003 增碼＝ADR-00085） |
| `GET /systemManage/getRoleList` | 可讀角色清單（R_ADMIN 之 seed 已持） | —— | 選單列 `manage_role`（受保護四列之一、可授可見性＝款 10） |
| `GET /systemManage/getAllRoles` | 可讀活性且啟用角色（R_ADMIN／R_USER_COMMON 之 seed 已持） | —— | 使用者頁新增與編輯抽屜之角色下拉（本刀接真；持有之停用角色另由清單列帶入、灰色保留） |
| `POST /systemManage/addRole` | 可新增角色 | 新角色零授權、三維授權端點屬封死集 ⇒ 受讓者無從授權；指派新角色受包含規則 N⊆A——非 R_SUPER 受讓者之 A 不含其新建之角色（且本人不得改自身指派）⇒ 產物只是空角色、待持 R_SUPER 者授權與指派 | `manage_role`＋`role:add` |
| `POST /systemManage/updateRole` | 可改任一角色（含 R_SUPER）之名稱與描述類欄；可停用其他角色（成員即時斷權） | 代碼不可變；停用雙護欄＝不得停用自己所屬角色、R_SUPER 恆禁停用（ADR-00044 決定 3） | `manage_role`＋`role:edit`（編輯抽屜） |
| `DELETE /systemManage/deleteRole` | 可刪無指派之自建角色，其全維授權以 `role_soft_delete` 連動歸檔（不可復原；角色刪除單向） | seeded／in-use／self-role 三層守門（ADR-00044 決定 3；本刀起 in-use 與 self-role 兩腿生產可達） | `manage_role`＋`role:delete` |
| `DELETE /systemManage/batchDeleteRole` | 同上（批次） | 同上；任一違規整批拒 | `manage_role`＋`role:delete` |
| `GET /systemManage/getRoleHome` | 可讀任一角色之首頁 | —— | 角色頁編輯抽屜（須 `role:edit`）→「菜單權限」彈窗之首頁下拉（款 10、款 13） |
| `POST /systemManage/updateRoleHome` | 可改任一角色（含 R_SUPER）之首頁、每次選值落一列 `update` 稽核 | 首頁不在可見樹時由讀端兜底（005 刀既有） | 同上；★持 getRoleList＋getAllPages＋getRoleHome＋updateRoleHome、`manage_role` 可見與 `role:edit` 碼即可經 UI 改任一角色之首頁（006 刀 U16 實測屬實：直打與下拉兩路皆改得動自建角色之首頁、`updated_by`＝受讓帳號；「含 R_SUPER」以整合測試觀察） |
| `GET /systemManage/getMenuList/v2` | 可讀選單治理清單 | —— | 選單列 `manage_menu`（受保護四列之一） |
| `GET /systemManage/getMenuTree` | 可讀治理域選單樹 | —— | 選單頁彈窗父選擇器；角色頁「菜單權限」彈窗之樹 |
| `GET /systemManage/getAllPages` | 可讀頁面全集 | —— | 選單頁新增／編輯彈窗之頁面下拉；角色頁「菜單權限」彈窗首頁下拉 |
| `POST /systemManage/addMenu` | 可新增選單 | 新選單零授權、選單維授予端點屬封死集 ⇒ 受讓者無從令其可見；保留路由名守門（ADR-00044 決定 8） | `manage_menu`＋`menu:add` |
| `POST /systemManage/updateMenu` | 可改非受保護欄、停用非受保護選單（全體含 R_SUPER 之側欄不現）、改按鈕碼清單使非受保護之獨有碼絕版（`menu_button_removed` 連動歸檔、不可復原） | 受保護選單拒停用與改父（ADR-00044 決定 5）；★移除尚有受保護授權列之按鈕碼＝整筆拒（本刀；ADR-00086）；路由名與選單型別不可變 | `manage_menu`＋`menu:edit` |
| `DELETE /systemManage/deleteMenu` | 可軟刪非受保護選單，其選單維與獨有按鈕碼授權以 `menu_soft_delete` 連動歸檔（不可復原）；選單回收桶兩端點屬封死集＝刪得掉、復原不了 | 受保護選單拒刪；有子項拒刪 | `manage_menu`＋`menu:delete` |
| `DELETE /systemManage/batchDeleteMenu` | 同上（批次） | 同上；任一違規整批拒 | `manage_menu`＋`menu:delete` |
| `GET /systemManage/getUserList` | 可讀現役使用者清單（六欄過濾；R_ADMIN 之 seed 已持） | —— | 選單列 `manage_user`（非受保護；R_ADMIN 之 seed 已持＝Admin 預設只見清單、無操作鈕＝GR7） |
| `GET /systemManage/getDeletedUsers` | 可讀回收桶（已刪帳號） | —— | 使用者頁回收桶切換 |
| `POST /systemManage/addUser` | 可新增帳號並指派角色 | 包含規則 N⊆A（只能指派自身現役持有之角色）；帳號名與信箱現役唯一；密碼政策與設密冷卻 | `manage_user`＋`user:add` |
| `POST /systemManage/updateUser` | 可改帳號欄、停用、改指派 | 包含規則 T⊆A∧N⊆A；seed 保護（Super 恆禁停用、恆禁解除其 R_SUPER 指派）；本人之狀態與指派出現即拒 | `manage_user`＋`user:edit` |
| `DELETE /systemManage/deleteUser` | 可軟刪帳號（同交易硬刪指派、撤全部有效票） | 包含規則 T⊆A；seed 三帳號不可刪；不得刪本人 | `manage_user`＋`user:delete` |
| `DELETE /systemManage/batchDeleteUser` | 同上（批次） | 同上；任一違規整批拒、不指筆 | `manage_user`＋`user:delete` |
| `POST /systemManage/restoreUser` | 可復原已刪帳號（復原後零角色） | T＝∅ 恆過包含規則；同帳號名或同信箱已有現役列＝拒 | 使用者頁回收桶模式＋`user:restore` |
| `POST /systemManage/kickUser` | 可踢除帳號之全部有效會話 | 包含規則 T⊆A；不得踢本人 | `manage_user`＋`user:kick` |
| `POST /systemManage/resetUserPassword` | 可重設他人密碼（同交易撤全部有效票） | 包含規則 T⊆A；不得以本端點重設本人；密碼政策與設密冷卻 | `manage_user`＋`user:reset-pwd` |

  封死集中之 `/systemManage/updateUserSessionPolicy` 不可授出（非超管之抽屜該欄停用並提示、不發必敗呼叫；spec FR-024）。

- **款 10 受保護之選單維四列與按鈕維六列「看得到、封死功能點不動」（本刀改述）**：`casbin_rule` 中 v2＝`menu` 之受保護授權列（seed 列 10 `manage_role`、11 `manage_menu`、69 `manage_system-settings`、72 `manage_policy-archive`）不入封死射程（ADR-00064 決定 5〔射程外一〕；`rev5:ADR 0054` §4——擴射程＝把選單可見性綁死在 R_SUPER、與島 H4 治理域／顯示域分層相違）：可授他角色可見性、該頁之封死集端點恆 `5003`。★按鈕維受保護六列（R_SUPER 名下 `role:add`／`role:edit`／`role:delete`／`menu:add`／`menu:edit`／`menu:delete`，m0003 起；ADR-00085）同理不入封死集（ADR-00064 決定 1 之 HTTP 方法白名單）⇒ 可授 X 同碼（新列非受保護）、授後鈕見而其背後端點依 X 之端點維授權放行或 `5003`（spec US4 AS7、Edge Cases「包含規則與委派」：碼有端點無＝鈕見而 `5003`）。★本刀起角色頁與選單頁之鈕依碼顯隱（款 18 解除）：X 受授某頁可見性後，表頭新增與批刪、列編輯與刪除鈕只在 X 持對應碼時現。共同觀察路徑＝Super 以「菜單權限」彈窗授自建角色 X 可見該列→持 X 之自建帳號重新整理⇒側欄現該項（前提＝決定 4）；進頁後逐列：
  - 列 10 `manage_role`（角色管理頁）：清單讀端 getRoleList 非封死（依 X 之端點維授權放行或 `5003`，見款 9）；表頭與列鈕依 X 所持 `role:*` 碼顯隱；編輯抽屜須 X 持 `role:edit` 才開得起——開得起時抽屜三顆授權鈕可見（不設碼＝Q8），彈窗開得起、現況讀端（getRoleMenu／getRoleButton／getRoleEndpoints）屬封死集回 `5003`、確定鈕維持停用；按鈕與端點兩彈窗之候選讀端（getAllButtons／getAllEndpoints）亦屬封死集 ⇒ 兩樹整個為空、選單彈窗之樹（getMenuTree 非封死）照常渲染而全未勾（006 刀 U16 實測）；三彈窗開啟時各跳共用請求層錯誤提示（`system.forbidden`＝「沒有權限執行此操作」）。X 未持 getRoleHome 時，「菜單權限」彈窗開窗另發之 getRoleHome 亦回 `5003`（可授出而未授、非封死集；款 9），首頁下拉照常可操作、顯未選、候選取自 getAllPages（非封死）。★可達路徑：抽屜「菜單權限」彈窗之首頁下拉不受就緒守、選值即寫（款 13）——X 另持 getRoleList＋getAllPages＋getRoleHome＋updateRoleHome（皆可授出＝款 9）與 `role:edit` 碼時，可經此下拉改任一角色（含 R_SUPER）之首頁、每次選值落一列 `update` 稽核（觀察形同款 9 updateRoleHome 列）。
  - 列 11 `manage_menu`（選單管理頁）：治理清單讀端非封死（同上）；表頭新增與新增子選單、列編輯與刪除鈕依 X 所持 `menu:*` 碼顯隱；回收桶之讀（getDeletedMenus）與復原（restoreMenu）屬封死集＝恆 `5003`（復原鈕不設碼＝Q8）：開回收桶即跳同一錯誤提示、清單呈空——與「本來就無已刪列」於畫面上不可分，判據取回應碼。
  - 列 69 `manage_system-settings`：view 未進場＝點擊不跳轉（同款 2）；其讀寫兩端點屬封死集。
  - 列 72 `manage_policy-archive`（授權回收桶頁）：進頁後列表讀端 getArchivedPolicies 屬封死集＝`5003`、列表空；復原 restorePolicy 同屬封死集。
  - 觀察：選單維四列之頁內形沿 006 刀 U16 實測；按鈕碼顯隱之可見效果（含授 X `role:edit` 而不授 updateRole＝鈕見、送出 `5003`）於本刀 CDP 三方對照單元以持部分碼之自建角色帳號實測（spec FR-065）；列 10 與列 11 之頁內形（含三彈窗與回收桶之錯誤提示、getRoleHome 未授之 `5003`）於本刀已知態觀察段以持 `role:edit`＋`menu:add` 之自建帳號實測。
  - 碼面證據（as-built；按鈕維之改述面）：m0003 改受保護之六列（列 58～63）＝rust-api `migration/src/m0003_seed_button_governance.rs`（ADR-00085 決定 2 第①句）；按鈕維受保護列不入封死集＝`server/src/model/facade/sys_casbin_policy.rs` 之 `seed_reads_and_the_seal_set_match_the_seed_facts`（按鈕維 seed 列受保護 6；封死集之 seed 成員＝端點維讀回之受保護鍵）；角色頁與選單頁之鈕依碼顯隱、角色抽屜三顆授權鈕與選單回收桶「復原」鈕不設碼之碼面證據見款 18。
- **款 11 並行編輯後送出者整份覆蓋（006 刀 brainstorm Q12、spec FR-016；本刀改述可達面）**：全量替換下，同一角色同一維之兩處彈窗先後送出不同期望全集 ⇒ 後送出者整份為準、先送出者之差量被靜默撤銷；請求世代只丟棄同一彈窗之遲到回應、不防跨分頁、跨裝置或跨帳號覆蓋。三維寫端屬封死集＝只有持 R_SUPER 之帳號撞得上；★本刀起持 R_SUPER 者得以 addUser／updateUser 將 R_SUPER 指派他帳號（包含規則之 A＝全集）⇒ 相異之 R_SUPER 帳號亦撞得上（006 刀時只有同帳號多分頁或多裝置）。症狀形不因送出者為同一或相異帳號而異（寫端只比對期望集與現況、不看會話）。觀察路徑＝Super 於兩分頁開同一自建角色之「端點權限」彈窗→分頁甲勾 E 並確認→分頁乙（未重開）改勾 F 並確認⇒生效集合＝乙之期望（E 被撤）、授權回收桶出現 E 之歸檔列（端點維可復原）；選單／按鈕維同形而歸檔列不可復原、只能重勾；兩次各一列稽核 `update`；前端無衝突提示。相異 R_SUPER 帳號之可達性以整合測試證（Super 對自建帳號指派 R_SUPER 成功＝持 R_SUPER 者 A＝全集；spec FR-021、US4 AS1），並於本刀已知態觀察段以 CDP 直接觀察（Super 指派 R_SUPER 予自建帳號後，兩帳號各開同一自建角色之「端點權限」彈窗先後送出）：症狀形與同帳號多分頁同（後送出者整份為準、前者之端點被撤並入授權回收桶、兩列 `update` 稽核分屬兩帳號、兩邊皆只見成功提示）。
  - 碼面證據（as-built）：Super 以含超管角色之 `roleIds` 新增帳號＝`0000`、寫後指派恰超管角色＝rust-api `server/src/handler/user.rs` 之 `add_user_has_no_seed_or_self_gate_and_matches_names_case_sensitively`。
- **款 12 授權回收桶復原 NoOp：移除歸檔列而零稽核、與 Applied 對前端不可區分**（006 刀 brainstorm Q16；006 刀 spec Clarifications 2026-10-01 首題）：歸檔列之授權身分鍵已在現役時，復原回成功、歸檔列照常消費移除、不重複寫入、零操作稽核、不觸發判定面同步；可復原旗標不含「是否現役」腿 ⇒ 已重新授予之歸檔列仍顯可復原（NoOp 判準＝ADR-00065 決定 5、固定序五腿＝同 ADR 決定 3、旗標同判準＝同 ADR 決定 8）。觀察路徑＝新建自建角色 X→以「端點權限」彈窗授 X 端點 E 並確認→再撤 E 並確認（回收桶出現 E 之歸檔列 A、可復原）→再重授 E→回收桶頁 A 仍顯可復原→復原 A⇒成功 toast、A 自列表消失、X 之現役授權列數不變、`sys_operation_log` 零新列、同步結果計數不增；對照一次 Applied 之復原⇒前端所見相同。（X 毋須帳號持有；稽核列數與同步計數並以整合測試觀察。）
- **款 13 首頁下拉選值即寫、與確定鈕獨立、取消不還原**（006 刀 spec Clarifications 2026-10-01 第三題）：選單權限彈窗之首頁下拉沿 upstream 既綁之選值事件，每次選值（含清空＝送 null）即打 updateRoleHome、各落一列稽核 `update`；確定鈕只送 updateRoleMenu（全量）。觀察路徑＝角色列表→編輯自建角色→「菜單權限」→首頁下拉選一頁⇒當下即發 updateRoleHome；按「取消」關閉→重開⇒首頁顯新值（不還原）；連選兩次⇒兩列稽核。（可達路徑：角色頁編輯鈕本刀起依 `role:edit` 顯隱——Super 持之〔受保護列 59〕＝路徑不變。）
- **款 14 可授予指向不存在 view 之自建選單＝側欄可見而點擊零反應**（`rev5:006` 同形已知態）：選單寫端不驗 component 指向之 view 是否存在於 base-web；seed 側由 seed-view-gate 管（ADR-00071 決定 1）、自建選單不在其射程。觀察路徑＝新增一個 component 指向 base-web 不存在之 view 的選單→「菜單權限」彈窗授予自建角色 X（前提＝決定 4①）→持 X 之自建帳號重新整理⇒側欄現該項、點擊不跳轉（症狀形同款 2）。
- **款 15 選單維與按鈕維之授權撤銷在授權回收桶只剩閱覽**（不可復原集＝ADR-00065 決定 1）：`menu_revoke`／`button_revoke` 屬不可復原集 ⇒ 其歸檔列可復原旗標恆 false、復原鈕呈停用態、不另造提示；後端強行呼叫回 `biz.policy.notRestorable`；恢復唯一路徑＝於彈窗重勾（新授一列、非回灌原列）。觀察路徑＝新建自建角色 X→以「菜單權限」彈窗授 X 某選單並確認→再取消勾選並確認（撤銷）→授權回收桶頁⇒該列之歸檔原因為 `menu_revoke`、復原鈕停用；以「按鈕權限」彈窗先授後撤某按鈕碼⇒原因 `button_revoke`、同形。
- **款 16 授權回收桶復原不擋停用角色＝復原成功而持該角色者至重新啟用前仍 `5003`**（固定序第⑤腿＝ADR-00065 決定 3；停用≠撤銷＝島 H4 精神）：來源角色停用而活性時第⑤腿不擋，可復原旗標依①～④同判準 ⇒ 回收桶顯可復原、復原為 Applied（授權表新 id 一列、`restore` 稽核一列、commit 後判定面同步一次）；停用即斷權出自授權讀端每請求濾角色狀態、不經判定面 ⇒ 復原回來之授權於角色重新啟用前不生效、重新啟用後下一請求即生效（啟用不觸發同步）。觀察前提＝決定 4（X 取自建角色、帳號取持 X 之自建帳號；E 取持 X 之帳號其餘角色皆不持有之可授出端點，例 getRoleList；停用與重新啟用落在 X、seed 列零寫入）。觀察路徑＝以「端點權限」彈窗授 X 之 E 再撤之→角色列表編輯 X、狀態改停用→授權回收桶頁⇒E 之歸檔列顯可復原；復原⇒成功 toast、該列自列表消失、X 名下現役授權列多 1；持 X 之帳號直打 E⇒仍 `5003`；再將 X 改回啟用→直打 E⇒放行（症狀沿 006 刀 U16 實測：復原 Applied 時授權表新增一列、`restore` 稽核一列、同步 +1；停用與重新啟用皆不觸發同步）。整合測試觀察法同形（清理守衛下自建角色 Y 與自建帳號、直種指派、授→撤→停用 Y→復原→`5003`→啟用 Y→放行）。
- **款 17 只勾目錄不勾子項＝側欄現無子項之死項、首頁兜底可落其上致登入即落 `/403`**：選單維無父子連動（勾目錄不連帶勾子項）。觀察路徑＝「菜單權限」彈窗對自建角色 X（前提＝決定 4①）只勾某目錄型選單、不勾其任何子項→確認→持 X 之自建帳號重新整理⇒側欄頂層現該目錄項、為普通項（無展開箭頭、無子項；getUserRoutes 之該項無 `children` 欄）；點擊零反應（網址不變、零 API、零 toast，console 報 `No match for {"name":<該目錄路由名>}`＝形同款 2／款 14）、直打其路徑⇒全頁 404（006 刀 U16 實測）。後半（首頁兜底落在它）之構造＝X 只持某 order＜999 之目錄（例 `manage`〔order 2〕或自建小序目錄）之選單維授權（不授 `home` 與其他選單）⇒ 可見樹＝該目錄＋自助白名單之 `user-center`（ADR-00077）、讀端兜底（`navigable_names` 以 `children` 缺席判葉、依樹序取首葉）先取該目錄即落其上：持 X 之帳號登入即落全頁 `/403`（無側欄），「返回首頁」只發 isRouteExist、仍停在 `/403`＝使用者卡住、須直打他頁離開；授予 `home` 後落點回 `/home`（症狀沿 006 刀 U16 實測；`rust-api/server/src/handler/route.rs` 之 `navigable_names`／`resolve_home` doc 註明此例外與其 order 條件〔限該目錄於可見樹先序排在自助白名單 `user-center` 之前；RL-0011〕）；只授 order＞999 之目錄（例插件示例、function）者兜底落個人中心＝症狀消解。本刀 CDP 實測（自建角色、自建帳號）：只持 `manage`（order 2）者登入即落全頁 `/403`、getUserRoutes 之 home＝`manage`、「返回首頁」只發 isRouteExist 而仍停 `/403`；加授 `home` 後落 `/home`、側欄「系統管理」為無子項之普通項、點擊零反應（console `No match for {"name":"manage"}`）；只持 `plugin`（order 1006）者落個人中心、home＝`user-center`。
  - 碼面證據（as-built；後半射程收窄面）：自助路由白名單恰一列 `user-center`＝rust-api `server/src/handler/route.rs` 之常數 `SELF_SERVICE_ROUTES` 與 `self_service_whitelist_holds_exactly_the_user_center_route`；只授排序在 `user-center` 之後之頂層葉者回包樹恰為 `[user-center, 該葉]`、`home`＝`user-center`＝同檔 `self_service_whitelist_reaches_accounts_without_menu_policy_and_widens_nothing`。
- **款 18**：解除（本刀；號不再配）——角色、選單、使用者三頁之鈕依 spec FR-048 對碼表逐鈕顯隱（使用者頁 `user:add`／`user:edit`／`user:delete`／`user:restore`／`user:kick`／`user:reset-pwd`／`user:unlock`；角色頁 `role:add`／`role:edit`／`role:delete`；選單頁 `menu:add`／`menu:edit`／`menu:delete`；表頭新增與批刪走既有 showAdd／showDelete；選單回收桶復原鈕與角色抽屜三顆授權鈕不設碼）⇒ 授撤上列碼於重新登入後即有可見效果。解除證據＝本刀 CDP 三方對照（使用者頁以 Super 與 Admin、角色與選單頁以 Super 與持部分碼之自建角色帳號實測；spec FR-065；角色頁與選單頁之顯隱屬刻意分岔登記表「角色頁、選單頁按鈕」列）。
  - 碼面證據（as-built）：使用者頁＝base-web `src/views/manage/user/index.vue`（表頭 `:show-add`／`:show-delete` 綁 `user:add`／`user:delete`、列鈕 `user:edit`／`user:delete`、回收桶列 `user:restore`、列操作下拉之 `getOperateOptions` 依 `user:kick`／`user:reset-pwd`／`user:unlock` 組選項）；角色頁＝`src/views/manage/role/index.vue`（表頭 `role:add`／`role:delete`、列鈕 `role:edit`／`role:delete`）；選單頁＝`src/views/manage/menu/index.vue`（表頭 `menu:add`／`menu:delete`、列鈕新增子選單 `menu:add`、`menu:edit`、`menu:delete`）；四頁表頭兩 prop 錨＝`tools/view-render-guard.py` 之常數 `ANCHORS`。不設碼兩處＝`src/views/manage/role/modules/role-operate-drawer.vue` 之三顆授權鈕、`src/views/manage/menu/index.vue` 之回收桶「復原」鈕。
- **款 19 兩分頁下角色編輯抽屜之名稱、描述、備註三欄舊值覆寫**（＝ADR-00070 後果殘餘②）：抽屜編輯既有角色送出 updateRole 時，三欄恆送開啟時表單值；BL-00131 修法只收狀態欄（ADR-00070 決定 1）。觀察路徑＝Super 於兩分頁開同一自建角色之編輯抽屜→分頁乙改名稱並確定→分頁甲（未重開）只改描述並確定⇒名稱回到開啟時舊值、兩次各一列稽核 `update`、前端無衝突提示；甲之 updateRole 請求 body 帶開啟時之 `roleName`（006 刀 U16 實測屬實）。
- **款 20 繞過 UI 對已停用之自身所屬角色送停用值照擋（本刀起生產可達）**（＝ADR-00070 後果殘餘③）：停用雙護欄之觸發口徑（請求 `status` 解析為停用即判、不比對現值；ADR-00044 決定 3）不動（ADR-00070 決定 4）。★本刀起帳號得同持多角色 ⇒ 自建帳號 P 同持啟用之自建角色 Y（受授 getRoleList、updateRole 端點、`manage_role` 可見性與 `role:edit` 碼）與已停用之自建角色 Z，即同時屬已停用角色又持 updateRole＝生產可達。UI 路徑：P 於角色頁編輯 Z、只改名稱並確定⇒請求不帶 `status`（ADR-00070 決定 1）⇒不被擋、名稱落地；UI 外路徑：P 直打 updateRole 對 Z 送停用值⇒`biz.role.cannotDisableSelfRole`（by-design）。觀察形：UI 路徑＝本刀 CDP 三方對照單元實測（ADR-00070 翻案觸發器第四條之實測義務；rev6 側網路請求事件斷言只改名稱之 updateRole body 無 `status` 鍵且回 `0000`；可達前提〔P 同持 Y 與已停用之 Z、Z 之抽屜開得起〕同步觀察——本刀已知態觀察段實得：body 鍵集＝{id, roleName, roleDesc, roleMemo}、`0000`、名稱落地、Z 仍停用、一列 `update` 稽核）；UI 外路徑＝整合測試（`handler/role.rs` 測試模組之 `disable_guards_refuse_self_role_before_super_and_count_disabled_memberships` 已釘 Super 掛已停用自建角色再送停用之形）。
  - 碼面證據（as-built）：UI 路徑之「只改名稱不帶 `status`」＝base-web `src/views/manage/role/modules/role-operate-drawer.vue` 之 `handleSubmit`（狀態只在表單終值異於開啟時回填值才帶；ADR-00070 決定 1）。UI 外路徑以兩案合證：rust-api `server/src/handler/role.rs` 之 `disable_guards_refuse_self_role_before_super_and_count_disabled_memberships`（成員身分含停用角色：掛已停用之自建角色再送停用＝`cannotDisableSelfRole`）、`server/src/handler/user.rs` 之 `self_role_refusals_become_reachable_once_update_user_assigns_the_role`（自建帳號經 updateUser 持自建角色後，以其票經 updateRole 真路由送停用＝`cannotDisableSelfRole`、零變更零稽核）。「自建帳號同持啟用 Y 與已停用 Z」之組合形未另立單案，其可達前提與 UI 路徑症狀由本刀 CDP 三方對照單元實測。

- **款 21 seed 角色名與選單樹節點名於繁中介面照原字顯示（大陸用語）**：角色名（角色頁清單、使用者新增與編輯抽屜之角色候選）與選單樹節點名（getMenuTree 之 `label`＝`menu_name`：角色頁「編輯選單權限」彈窗之樹、選單頁父選擇器）照庫存值顯示、不經譯文；側欄與選單治理清單之選單名經 `i18nKey` 譯文（例：選單 14 之 `route.plugin` 於 zh-TW 顯「外掛範例」）、不在本款。m0002 seed（承 rev5 逐位元＝憲法 §I.5 例外②）之 R_USER_COMMON 角色名「普通用戶」與插件示例目錄之 `menu_name`「插件示例」於上列照原字處以 zh-TW 呈現。觀察路徑＝32080 設 `zh-TW` 後開角色頁清單（角色名欄）與使用者新增／編輯抽屜之角色候選⇒見「普通用戶」；Super 對 R_SUPER 開「編輯選單權限」彈窗⇒樹節點見「插件示例」（本刀 CDP 繁中審讀實測）。其餘譯文不受影響；改名須動 seed（新 migration）或另立顯示層對照，屬拍板級——本刀記為已知態、不動。

## 親決分類

依 ADR-00089（RL-0086）；類別：待決＝無出處之新拍板級內容／承決＝轉錄 user 已做之決定（出處終點＝user 決定紀錄或 spec 條目）／工程＝怎麼做。

| 款 | 類別 | 出處或理由 | 白話一句 |
|---|---|---|---|
| 決定 1 | 承決 | 各款處置之出處見本表各款列；決定 4① 收回＝spec FR-056⑧、FR-058；款號保留不重用屬編號工程（替代案 5）；決定節導言之 supersedes 與被續行者 status 屬 accepted 同顆簿記（GT-04） | 舊 ADR 二十款逐款標明續行、解除或改述（款號一對一沿用），新增款 21，並收回 seed 帳號與 seed 角色之觀察例外。 |
| 決定 2 | 工程 | 現在式面改指之施工法（機器枚舉、改完復掃；RL-0050、LL-00064） | 文件與碼註裡引舊 ADR 的地方改指本 ADR，用工具掃到零殘留。 |
| 決定 3 | 承決 | ADR-00068 決定 3（候選四款於 006 刀經 user 2026-10-04 親決）；spec FR-056（已知態 ADR 經 user 親決後 accepted） | 解除與改述要實際操作看過才定稿，新發現的已知態要 user 點頭才收。 |
| 決定 4 | 承決 | spec FR-057（走查基準與還原）、FR-058（走查與測試之寫入一律對自建帳號）、FR-062（稽核斷言取水位窗） | 觀察一律用自建帳號與自建角色、前後套基準還原，純後端面用整合測試。 |
| 款 1 | 承決 | ADR-00068 款 1（006 刀解除） | 舊款 1 上一刀已解除，號碼不再用。 |
| 款 2 | 承決 | ADR-00068 款 2；BL-00045 | 系統設定與稽核兩個選單項點了沒反應，等 008 刀。 |
| 款 3 | 承決 | ADR-00068 款 3；觀察前提改寫＝spec FR-058 | 新建或復原的選單要再授權才會出現在側欄。 |
| 款 4 | 承決 | ADR-00068 款 4；觀察前提改寫＝spec FR-058 | 新的按鈕碼要再授權才有人持有。 |
| 款 5 | 承決 | ADR-00068 款 5 | 新建選單在治理清單顯示原始翻譯鍵。 |
| 款 6 | 承決 | ADR-00068 款 6；BL-00045 | 治理清單兩列顯示路由裸鍵，等 008 刀。 |
| 款 7 | 承決 | spec FR-047、FR-020（brainstorm Q13） | 使用者頁接真、停用角色以灰色保留，舊款解除。 |
| 款 8 | 承決 | ADR-00068 款 8 | 選單治理清單分頁列凍結、一次全取。 |
| 款 9 | 承決 | ADR-00068 款 9；spec FR-001、FR-002、FR-007、FR-010、FR-014、FR-015、FR-017、FR-020、FR-021、FR-023、FR-024、FR-025、FR-026、FR-027、FR-035、FR-040、FR-041（ADR-00085）、FR-043（ADR-00086）、FR-044、FR-047、FR-048、FR-060、FR-063、US4 AS4／AS5（brainstorm Q6／Q7）；可授出集 30 支屬量測 | 使用者域寫端受包含規則、不能越權；角色、選單、IP 域照舊可下放。 |
| 款 10 | 待決 | 按鈕維之改述有出處（ADR-00085、spec FR-048、US4 AS7）；本刀觀察新收之兩症狀（開三顆授權彈窗與選單回收桶各跳「沒有權限執行此操作」、getRoleHome 未授亦 `5003` 而首頁下拉照常可操作）屬 user 可見行為、spec 無對應條目 | 受保護之選單維四列與按鈕維六列可授他人（頁看得到、鈕依所持碼顯隱），封死功能點恆 `5003`；開授權彈窗與選單回收桶會跳無權限提示，未授 getRoleHome 時首頁下拉仍可操作。 |
| 款 11 | 承決 | ADR-00068 款 11（006 刀 brainstorm Q12）；spec FR-021、US4 AS1（brainstorm Q6：持 R_SUPER 者 A＝全集 ⇒ 得指派 R_SUPER） | 同一或不同超管帳號同時改同一角色的同一維授權，後送出者整份為準、先送出者的改動被靜默撤銷。 |
| 款 12 | 承決 | ADR-00068 款 12 | 授權回收桶復原已在現役者回成功但不落稽核。 |
| 款 13 | 承決 | ADR-00068 款 13；`role:edit` 顯隱＝spec FR-048 | 首頁下拉選了就寫，按取消也不還原。 |
| 款 14 | 承決 | ADR-00068 款 14 | 可授予指向不存在頁面的自建選單，點了沒反應。 |
| 款 15 | 承決 | ADR-00068 款 15 | 選單與按鈕授權撤了只能重勾，回收桶不能復原。 |
| 款 16 | 承決 | ADR-00068 款 16 | 停用角色的授權可復原，但重新啟用前仍不生效。 |
| 款 17 | 承決 | ADR-00068 款 17；後半射程收窄＝ADR-00077（自助路由白名單） | 只勾目錄不勾子項會出死項；首頁兜底可能落 403，排在個人中心之後的目錄改落個人中心。 |
| 款 18 | 承決 | spec FR-048（brainstorm Q8） | 三頁按鈕依碼顯隱，舊款解除。 |
| 款 19 | 承決 | ADR-00068 款 19（＝ADR-00070 後果殘餘②） | 兩分頁同改一個角色，名稱、描述、備註以後送出者為準。 |
| 款 20 | 承決 | ADR-00068 款 20；ADR-00070 翻案觸發器第四條；spec FR-065 | 對停用中的自身角色只改名可以過，送停用值照擋。 |
| 款 21 | 承決 | user 2026-10-15 AskUserQuestion 親決（seed 用語「記為已知態」） | seed 的「普通用戶」「插件示例」在角色頁、使用者抽屜與選單權限樹等處照原字顯示，本刀不改。 |

- **親決紀錄**：依 ADR-00089（新制首次驗證；007 刀 tasks T103、2026-10-15）。分類＝本表 25 列：待決 1（款 10）、承決 23、工程 1。獨立核對（非起草者之 fresh-context 審查 agent；決定 5）首輪：升待決 0（誤標 0）、改正 7 列——決定 1（白話與出處）、決定 3 與 title（補款 17 之改述）、款 9（出處補列；Q3 冠 006 刀）、款 10（白話與引文出處）、款 11（出處改 spec FR-021／US4 AS1／brainstorm Q6；Q12 冠 006 刀；白話）、款 12（Q16 冠 006 刀）、款 21（款文射程與碼不符：側欄與治理清單之選單名經 `i18nKey` 譯文，改為只及角色名與選單樹節點名）；改正後復核（決定 6②）仍不符 1 列（款 9 出處欄）→ 補齊。待決款 10 經 user 2026-10-15 AskUserQuestion 答「記為已知態（建議）」，作答後款文未改（決定 6①）。對照表收尾一題（決定 6③；三支共用）答「照表定稿（建議）」、拉出 0 款。實問題數＝2（待決 1＋收尾 1）。

## 後果

- ADR-00068 整顆轉 superseded：本 ADR accepted 那一顆同批補 `supersedes: ["ADR-00068"]`、把 ADR-00068 之 status 改為 superseded、`superseded_by` 由 generate 回填（GT-04 對宣告者不看 status，故草稿期 supersedes 恆空）；續行鏈＝ADR-00045→ADR-00068→本 ADR，讀前兩者須併讀本 ADR。
- 審查輪與 CDP 對照遇上列各款，指向本 ADR 即結案；新發現之同類現象不自動適用、須個案判斷；CDP 走查期新發現之已知態依決定 3 併入後才 accepted。
- ADR-00070 後果之殘餘面以本 ADR 同號款承載（殘餘①同型於款 11、殘餘②③＝款 19／款 20）；ADR-00070 為 accepted body、其「ADR-00068 款 19／款 20」之引用不改，讀者經 superseded 鏈至本 ADR。
- 款 2／款 6 之後續工作帳＝BL-00045（008 刀）；款 9 之 unlockLogin 帳號維守門（BL-00048）隨本刀收；其餘款之解除點＝各款翻案觸發器。
- 現在式改指（決定 2）之同批面：活書 06（島 H 前端項之款數句、unlockLogin 與 IP 規則寫端之授出效果句）、活書 08（§8.4 引款 8、款 13 之句）、活書 10（UI 一致性列之已知例外句）、活書 11（角色與選單已知態列之逐款摘要、款數與解除點句——含「`user:*` 按鈕碼授撤零可見效果」症狀與「使用者域刀」解除點）、活書 12（可授出集、並行覆蓋、射程外各條）、RUNBOOK、BACKLOG 條文、`docs/ops/reference-src/code-gate-contracts.md`、rust-api 碼註；以決定 2 之指令現算、改完復掃。
- 代價：多一顆 ADR；款號保留使款 1、款 7、款 18 成空號（對照表可查）。

## 翻案觸發器

- 款 2／款 6：system-settings、稽核兩頁進場刀（008 刀）帶入頁面與譯文。
- 款 21：改 seed 角色名或選單名之 migration、或為 seed 名稱另立顯示層譯文。
- 款 3／款 4：選單或按鈕碼之新增流程改為同交易授予、或選單回收桶復原改為回灌授權（須先使選單維歸檔出現可復原原因＝觸發 ADR-00044 決定 4 之翻案條款）。
- 款 5：選單新增流程改為同時登記 `route:` 譯文、或改以 `menuName` 回退顯示。
- 款 8：決定改走治理清單真分頁、或頂層列數使全取回應成本不可忽略。
- 款 9：首次出現多層管理員需求（非 R_SUPER 角色須持受限之角色、選單或 IP 域管理權）、或包含規則射程擴至角色域、IP 域或授權回收桶復原（Q7 翻案）、或 seed 尚未上線之政策列（稽核域五支）隨其刀註冊（可授出集再算）。
- 款 10：出現「選單可見性或按鈕碼須與頁面端點授權綁定」之需求、或受保護列之可見性或碼下放造成誤判被回報 ⇒ 重評封死射程（ADR-00064 決定 5）。
- 款 11：實際發生誤蓋、或三維寫端引入版本比對（ADR-00066 決定 1 翻案）。
- 款 12：稽核合規要求授權回收桶之每次移除皆可追溯、或 NoOp 與 Applied 不可區分造成誤判被回報。
- 款 13：使用者回報誤寫。
- 款 14：選單寫端改為驗 component 指向之 view 存在、或出現自建死項之實際誤判回報。
- 款 15：選單維或按鈕維出現可復原原因之需求（須先復核 ADR-00044 決定 4 之同實例欄與島 H2 破口）。
- 款 16：角色停用語意改為撤銷（停用連動歸檔授權）、出現「復原須擋停用角色」之需求，或「復原成功而仍 `5003`」造成誤判被回報。
- 款 17：選單維引入父子連動、或首頁兜底規則改動。
- 款 19：抽屜改為只送變動欄或開啟時重取、updateRole 引入樂觀鎖、或誤蓋實際發生（沿 ADR-00070 翻案觸發器）。
- 款 20：停用雙護欄改為轉移觸發（另立 ADR）、或 UI 外送停用值之誤擋實際被回報。
