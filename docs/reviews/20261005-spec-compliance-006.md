# 006-authz-governance 規格對照審查（spec-compliance-006、2026-10-05）

範圍＝已收刀之 006 authz-governance 刀對 `specs/006-authz-governance/` 的兌現度：spec.md FR-001～FR-054（A～H 八組）、SC-001～SC-014、User Story 1～5、Clarifications（Session 2026-10-01 七題、Session 2026-10-04 一題）、Edge Cases 六節、Assumptions、Out of Scope、★軌道逐處登記表與刻意分岔登記表，連同 data-model §1～§13、`contracts/` 四份（wire-authz-governance／wire-policy-archive／msg-keys／code-gates）、quickstart.md、tasks.md、checklists/requirements.md；另核收刀後唯一一支維護批（maint-backlog-137-133）對 006 刀所建所定之面的改動有無承載。基準＝HEAD（外層 `46c46dc`、rust-api `67a7d3e`、base-web `fb4dac2`）；收刀點（merge `c1f072c`）只用於歸因；specs 本文不改（ADR-00012 定點快照）。

## 0. 方法與取證

| 項 | 值 |
|---|---|
| 形式 | RL-0073 承載處②：user 2026-10-05 臨時發起、附屬 006 刀；user 指定以 superpowers:requesting-code-review 對照 spec 做 review；分支 `maint-spec-compliance-006`（自 `rev6-admin-root @ 46c46dc`，即 maint-backlog-137-133 收單後） |
| 編排 | **兩支唯讀 Workflow**（user 裁定、沿 005 輪形；射程互斥；review 骨架 explore＋inline 兩鏡三態；全角色 `opus[1m]` xhigh、零 CDP；零 finding 之 lens 不派兩鏡）。run A＝`wf_deaaf04d-fbb`（五 lens＋一冷啟動探針；最壞 18／保險絲 19），派 14 支、零錯零 null、牆鐘 23.6 分；run B＝`wf_691ee8c2-fdb`（五 lens；最壞 15／保險絲 16），派 11 支、零錯零 null、牆鐘 33.1 分 |
| 切成兩支的理由 | FR 54 條但條文密（specs 共 2,627 行；rust-api 刀內 +14,103 行）、契約四份；另需一鏡核收刀後變動承載——本輪只一支維護批、兩子庫零 commit，故併入工具擴面鏡 |
| run A lens | L1 三維授權寫端與讀端（FR-009～016＋FR-005～007 三維側、SC-003、wire-authz-governance）｜L2 判定面同步、選單序列化域與生效時點（FR-017～020、FR-013 鎖序、FR-049、SC-005／006）｜L3 結構性封死與受保護（FR-021～025、FR-011、SC-004）｜L4 授權回收桶與復原（FR-026～032＋FR-008、SC-007、wire-policy-archive）｜L5 前端與 fork-delta×憲法 §III（FR-033～039、FR-053 與 SC-010 之靜態可證部分、SC-011）｜P1 冷啟動探針三題 |
| run B lens | L6 端點總則、授權態與契約碼表（FR-001～007 跨域總則＋FR-048、SC-001／002／008、msg-keys）｜L7 憲法 Amendment、ADR 與治理帳本（FR-040／041／046／047／054、SC-012／014）｜L8 工具擴面與收刀後變動承載歸因（FR-042～045）｜L9 測試基建與機器守保護力（FR-050～052、SC-009／013；不變式驅動）｜L10 Edge Cases 交叉、Assumptions、Out of Scope、checklists、quickstart 與跨域連帶 |
| review 模板 | requesting-code-review 要點烤入兩支 run 之 CONTEXT：spec 是願景文件（spec 沉默處以合理使用者期待判斷）；Critical／Important／Minor 對映 blocker／major／minor；每支 lens 的 notes 末附「做得好的地方」「擱置未判」「本 lens 判定」三段（摘要見 §5） |
| 前四輪經驗 | CONTEXT 烤入九條：前輪七條（BL 到期落點須明寫／逐字出自 accepted ADR 或 specs 之句不得單改現在式面／evidence 可原樣重跑／不逐檔列易漂移名冊／機器枚舉先證樣式集完備／錨字面被自身散文滿足＝恆綠無聲／已處置者不重報）＋憲法版本列與 ADR provenance 所帶 BL 號屬出處標籤（LL-00065）＋既有事件只經 RUNBOOK §12c erratum 更正列名欄位；另烤 RL-0078 防污染條款 |
| 規則塊 | `rules emit --scope review` 全塊烤入，RULES-VERSION `8af40d6633c6`（本輪調規後為 `c4a1c9749ae1`） |
| 唯讀邊界 | agent 禁寫入形命令、禁 docker／cargo／pnpm／generate；rev5 樹只讀；python 工具之保護力以記憶體內 exec 變異取證、rust 以讀碼推演。run B 之 L8 經執行環境註記「安全分類器逾時未審」：主線逐支核其工具呼叫（唯讀 Bash 125 支＋Read 3 支、零寫入工具），三棵樹與 rev5 樹之 HEAD 與 porcelain 皆不變 |
| 主線復核 | 11 筆逐筆重讀證據與兩鏡理由，並以 grep／sed 實跑複驗（§3）；另自兩鏡「擱置未判」補報 1 筆（M-1）；駁回一筆逐一查其承載 |
| 修單 | user 裁定本輪全修：rust-api `5f123a6`（三案補測＋三處碼註）；外層文件、規則與 LESSONS 與本報告同顆；三案皆變異自證、容器內全量 serial 跑（§3） |
| 未覆蓋 | SC-010 之 CDP 三方對照（承載＝006 刀 U16 走查）；前端行為面只讀碼推演、本輪未跑 `pnpm typecheck` |

## 1. 結論

**零 blocker、零 wire 行為缺陷。** 十支 lens 之判定：L1／L2／L3／L5／L6／L7／L8／L10＝兌現，L4／L9＝修後可兌現。主線實跑核得：ROUTES 49 條（政策保護 35）與路由條數常數同值、與 seed 政策列逐列對齊；`MSG_KEYS` 46 與三檔 backend 子樹雙向全等；13 碼矩陣零新變體；零 migration、零 seed 變更；1.6.0→1.7.0 Amendment 顆 `27e8c70` 早於 base-web 首顆既有檔改動 `c0e5c324`。三維寫端射程公式、受保護撤銷拒、封死兩掛點與名冊恰等、復原五腿與旗標逐腿同判準、觸發矩陣與兩窗字面，在憲法、ADR、活書、RUNBOOK、碼註之間一致，且各有可指名的測試。收刀後唯一維護批的變動逐項有承載，兩子庫零變動。

要處置的集中在三類：

- ①**測試保護缺口**三筆，皆經變異推演存活：
  - L9-1（major）：getArchivedPolicies 端點分頁缺 size 逾上界一發。005 輪 L9-1 同型，當時由 BL-00130 補於角色清單與已刪選單清單，006 新端點沒跟上。
  - L3-1：兩支 handler 交給 facade 的方法白名單沒有行為釘。
  - L4-1：旗標「批次取料、不逐列查」沒有機器釘。
- ②**現在式碼註、文件與指路**六筆：
  - 三處碼註失準：L6-1／L6-2／L6-3。
  - RUNBOOK §13 缺兩處指路、活書 06 缺一處 ADR 指針：P1-P1～P1-P3，由探針衍生。
- ③**收刀帳本漏記**兩筆：006 feature_close notes 漏了淨流量值（M-1）與 BL-00132 兌現射程註記（L7-1）。這是 LL-00049 的再犯：RL-0084 只核 spec 的 SC 子句，承接不到 tasks 與 contracts 所指定的收單內容。

**user 2026-10-05 裁定（五題）**：
- ①編排＝兩支唯讀 Workflow。
- ②測試補案三筆本輪補。
- ③碼註與文件六筆本輪修。
- ④RL-0084 擴面：tasks 收刀清單與 contracts 指定之收單事件註記一併核。
- ⑤收刀 merge 後容器未重建（§3 末段）只記 LESSONS、不加機制。

## 2. findings 與三分流（12 筆＝run A 6＋run B 5＋主線補報 1；修 11／轉 BL 0／駁回 1）

| 編號 | 嚴重 | 類別 | 面 | 一句話 | 處置 |
|---|---|---|---|---|---|
| **L9-1** | **major** | 測試保護缺口 | getArchivedPolicies 端點分頁（`archived_policies_paging_real_seed`） | 端點層只有四發、缺 size 逾上界：handler 改走不帶上界之內聯收斂，全樹照綠 | 修（第⑤發 `?size=1000`→(1, 100)；變異自證；活書 08 §8.2 第⑤案適用清單同批補） |
| L3-1 | minor | 測試保護缺口 | `handler/policy_archive.rs` restorePolicy／getArchivedPolicies | 兩支 handler 交 facade 之方法白名單（第③腿、旗標③半與維度篩）零行為釘：截成只剩首位方法全樹仍綠 | 修（新案逐方法各取一封死鍵＋反臂；兩發變異自證） |
| L4-1 | minor | 測試保護缺口 | `sys_casbin_archive::list` 旗標取料 | FR-027／ADR-00065 決定 8「批次求值、不逐列查」零機器釘：計數案頁內至多一列通過① | 修（計數案增第④臂；變異自證） |
| L6-1 | minor | 現在式文件失準 | `router.rs` ROUTES doc／外層 `test_references.py` | 連動釘值提示只寫「追加／加 route」、漏改序（LL-00060 認定之 006 刀 U16 漏改成因） | 修 |
| L6-2 | minor | 測試保護缺口（decided 鏡改判為檔頭失準） | `error.rs` 檔頭 | 稱「整個 crate 零第二份 wire 字面由 envelope.rs 的測試守住」，該測只掃 envelope.rs 自身；msg-key-gate 斷言 2 兩形皆收＝006 契約 msg-keys §3 已登記之取捨 | 修（收窄為改檔頭、閘判準不動） |
| L6-3 | minor | 現在式文件失準 | `model/audit.rs` `AuditOperation::Update` doc | 「更新一列現役標的」未涵蓋三維授權寫端以 update 記角色、角色列不變之用法（同刀已改 Restore doc） | 修 |
| L7-1 | minor | FR／SC 未兌現 | 006 feature_close notes | contracts/code-gates.md §8.2 指定之 BL-00132 兌現射程註記未入收單事件（只在 U18 `fa5b804` 訊息） | 修（本輪 review 事件 notes 補記；RL-0084 擴面） |
| M-1 | minor | FR／SC 未兌現（主線補報） | 006 feature_close notes | tasks 收刀清單「notes 記淨流量值」未兌現（run B real 鏡擱置欄點出、主線實證） | 修（同上） |
| P1-P1 | minor | 檢索性 | RUNBOOK §13「判定面同步耗盡」 | 漏列 ADR-00067 後果「維運面」之免重啟途徑；探針 Q3 因此漏答 | 修 |
| P1-P2 | minor | 檢索性 | RUNBOOK §13 | 缺「回收桶復原鈕停用／復原回 notRestorable」之自查指路（一因一鍵、拒因不落 log） | 修 |
| P1-P3 | minor | 檢索性 | 活書 06 §6.1 島 G ③④ | 兩步全文出自 ADR-00065，卻零處指向它 | 修 |
| L5-1 | minor | spec 自身缺陷 | 授權回收桶頁不顯方法欄 | 前提「同路徑多方法 0」無結構保證、前提失效之義務無承載 | **駁回**（見下） |

> 修 11 筆中，L7-1 與 M-1 的修法是在本輪 review 事件 notes 補記（feature_close notes 不可更正），其餘 9 筆為碼面與文件改動。

### 駁回之主線裁定

- **L5-1（駁回；real 鏡駁回、decided 鏡確認）**：
  - 前提實有兩面守，所以斷言不成立：
    - ROUTES 全表 path 唯一閘 `routes_paths_are_unique` 自 002 刀起常跑；授予寫端的候選只取 ROUTES 的政策保護全集。
    - 凍結 seed 的端點維是 50 個相異路徑、同路徑多方法 0；改 seed 屬拍板級。
  - finding 的否定掃描漏了「重複」與英文測試名兩種寫法。
  - 殘留一點較窄的事，只記於此、不另處置：該閘的 doc 與失敗訊息只講 axum 重複註冊，沒有指名回收桶頁依賴此不變式。日後若有刀為同路徑多方法放寬該閘，須同批補回收桶頁的方法顯示；wire 已帶 `v2`，資料面可補。

### L7-1／M-1 補記：006 刀收刀事件 notes 之兩項

feature_close notes 屬不可更正欄，依 RUNBOOK §12c 改在本輪 review 事件的 notes 同記：

- **淨流量**（tasks 收刀清單「notes 記淨流量值」）：
  - 006 收刀時點 rolling-3＝−20（004 窗 +1／005 窗 −11／006 窗 −10）。
  - 本刀自身＝誕生 2 條（BL-00137／BL-00138，T003）減收單 5 條＝−3，與 spec 摘要「本窗淨 −3」的預估相符。
- **BL-00132 兌現射程**（contracts/code-gates.md §8.2「收單事件註明此射程」）：以 U18 `fa5b804` 訊息 T083 ⑨ 的三點為準。
  - 對賬腿 U2 `00a82b5` 早於首個觸及 base-web 既有檔的 U7 `e5242ba`。
  - 1.7.1 PATCH 之後，修改型 24→33、新增型 14→20，跳過項歸零。
  - 活書 08 §8.4 的逐檔數以命令形現算，不另對賬、不另立衍生 BL。

### RL-0084 擴面（user 裁）

- RL-0084 改為：收刀 perf 第四步那顆 commit 內，逐項核對三類，結果寫入該顆 commit 訊息：
  - spec 標「收刀面於簿記 commit 後驗」之 SC 子句；
  - tasks 收刀清單各項；
  - contracts 指定寫入收單事件之註記。
- 不符者當顆修正（事件帳漏記補於該顆 perf 事件 notes）、引承載或轉 BL。
- CLAUDE.md §2 的兩處指針同批改；RULES 條數不變。
- LESSONS 新記 LL-00067（recurrence_of LL-00049）。

## 3. 驗證（主線實跑）

複驗各筆（grep／sed／git 實跑）：

- **L9-1**：`archived_policies_paging_real_seed` 元組表恰四發；全樹打 getArchivedPolicies 的請求 size 最大 100；facade `list` 不 clamp；`page_params` 的呼叫點沒有名冊閘。
- **L3-1**：
  - 兩支 handler 皆自路由表取 `endpoint_methods()` 再傳入；facade `restore` 只在第③腿用 methods。
  - handler 的拒腿案只列①①②④。
  - contract 的封死案只在 updateRoleEndpoints 授予（該接縫已由 contract 釘住），restorePolicy 與旗標③半則無。
- **L4-1**：`list` 先把代碼去重再一次取料；計數案在頁內至多一列通過①，逐列或逐代碼取料都同值。
- **L6-1／L6-2／L6-3**：三處字面逐字在場；envelope.rs 的源碼掃描案只 `include_str!` 自身、只檢四個字面。
- **L7-1／M-1**：feature_close notes 對「兌現射程」「§8.4」「淨流量」皆零命中；tasks 收刀清單與 contracts §8.2 的字面在場。
- **P1-P1**：ADR-00067 後果「維運面」載有免重啟途徑；RUNBOOK 全檔「原樣提交／免重啟／不必重啟」只有 §11.2 計數判讀一處。
- **P1-P2**：RUNBOOK「notRestorable／復原鈕」只 1 命中，屬 §11.2；NotRestorable 分支只 rollback 回鍵、零 tracing。
- **P1-P3**：06 島 G 段 ADR-00065 零次；ADR-00065 決定號（1 不可復原集／3 五腿／4 以 role_id 鎖讀／5 NoOp／6 Applied／7 拒因同鍵／8 旗標同判準／9 篩選／10 不收窄）依決定節標題核對。
- **L5-1**：`routes_paths_are_unique` 在場且常跑。
- **封死集現況**：GET 8／POST 7／DELETE 0（L3-1 修法據此逐方法各取一鍵）。

修單驗證：

- **修前綠**：三支新增或擴充的案，在未變異碼上單支 serial 跑，各 1 passed。
- **變異自證**：
  - 做法：每發只改一處生產碼，容器內 touch 後單支 serial 跑，log 須見 `Compiling server`；寫回不保 mtime，逐位元還原並核 sha256 全等（RL-0085）。
  - L9-1：handler 改走不帶 size 上界的內聯收斂 → 第⑤發紅（size 1000≠100）。
  - L3-1①：restore_policy 傳 `&methods[..1]` → POST 封死鍵 updateSystemSetting 被復原（0000≠2222）。
  - L3-1②：get_archived_policies 傳 `&methods[..1]` → 清單 total 2≠3。
  - L4-1：取料改為逐代碼查詢 → 第④臂 (2,2)≠(1,1)，原三臂在同一變異下仍綠，坐實舊案的盲區。
  - L4-1 首發因變異碼缺 `HashMap` 匯入而編譯失敗，不計為轉紅；改用完整路徑重跑。
- **容器內全量（serial）**：1259 passed／0 failed／2 ignored，即 006 收刀時的 1258 加本輪新案 1；建置零警告。
- **其餘閘**：rustfmt 閘綠；schema 三閘綠；走查基準 diff 前後皆全等；docsync check 零漂移、lint 0 錯 0 警、test 綠。
- **errata 複掃**：七組改動字面在全 repo（含兩子庫 pin 樹）皆零命中：「追加時的連動釘值」「由 envelope.rs 的測試掃源碼守住」「更新一列現役標的」「日後加 route 時」「get-archived-policies 分頁四案」「角色清單與已刪選單清單另一案」「（不需重送）」。

**全量首跑的環境紅（LL-00068）**：

- 徵狀：server lib `dev_trust_model_matches_the_delivered_file` 轉紅，容器內 `/etc/rev6/trust-model.toml` 讀不到。
- 成因：006 收刀 merge `c1f072c` 把 `deploy/trust-model.dev.toml` 的新版寫進工作樹（host 檔 mtime 與該 merge 同刻），容器內的單檔 bind mount 因此懸空，屬 LL-00033 同形。cargo 在該紅之後中斷，後面的整合測試未跑。
- 處置：依 RUNBOOK §2 重建 rust-api 容器（target 與 registry 為具名卷）後重跑，全綠。
- 這與本輪改動無關。user 裁定只記 LESSONS（LL-00068，recurrence_of LL-00033）。

## 4. 冷啟動探針（只入報告與事件 notes、不填事件 `probe` 欄）

三題：

- 端點權限取消勾選後授權去向、能否找回，以及選單／按鈕維的差別。
- 能否把受保護端點授給 R_ADMIN、擋在哪、選單可見性為何不在此限。
- 授權變更後 API 判定與側欄顯隱的生效時點、判定失敗如何恢復。

結果：

- 三題皆 found、答錯 0、找不到 0。
- Q1、Q2 判找得到（最短 2 跳）。
- Q3 判繞路：最短 3 跳、有效 4 跳，且漏答 ADR-00067 後果所載的免重啟恢復途徑。成因是處置唯一的家 RUNBOOK §13 沒有載入該途徑，修法見 P1-P1。

探針建議的處置：

- 「誤撤授權怎麼辦」與「復原失敗自查」：拆成 P1-P2，補在 RUNBOOK §13；不另立 FAQ 檔，以免同一事實有第二個家（RL-0049）。
- 「授權改了、對方側欄沒變」：判為設計語意，08 §8.3 與 06 ⑥ 已明載，不入 §13。

grader 另指出 12 名詞表的「受保護授權列」「封死集」「不可復原集」各列，是三題共同的高效入口，探針沒有利用到；這屬探針路徑選擇，不報。

## 5. 各 lens 判定摘要與建議（requesting-code-review 模板要點）

**做得好的地方（摘）**：

- `sys_casbin_policy` 的 ReplacePlan 恰兩態，整批拒時型別上拿不到寫入集，「拒在任何寫入之前」因此成為結構保證。
- 封死查詢次數與旗標取料以語句回呼計數，並帶陽性對照，把 ADR 的「零額外查詢」從散文變成機器證。
- 授權治理之同步呼叫點、封死查詢點、授權表寫入點都以（檔×fn）逐處釘處數，補上「只比檔集」的盲區。
- 復原五腿以「旗標與權威同一發取證」釘逐腿同判準；第②腿以形 (e) 專釘「role_id 非 NULL」前提。
- 取消安全案在「commit 已落、換上前」丟棄 future，並先證明請求尚未完成，非 vacuous。
- 走查還原工具的回補置於刪上界之後，次序由自測逐字釘住。
- 前端三顆彈窗以 ★ 註解釘住「先清受保護集、再經 setter 落空集」的次序；在記憶體內逐塊拔除圈界標記，20 塊全數被報出。

**擱置未判中值得主線留意者**：

- ①**README 的憲法版本鏡像是人寫鏡像**，docsync 沒有對賬腿。這自創世即有，並由 ADR-00063 決定六與 ADR-00072 決定 8 明定同批改；可交下一個獨立治理輪評估改指針或加腿。
- ②**NOTES 現況有一句「已全數收單並推」**，帶著推送揮發態，CLAUDE.md §6 禁記此類狀態。該句屬 005 前維護批條、不在 006 射程，可於下次改 NOTES 時順手改述。
- ③**getIpRuleList 的端點層分頁同樣沒有 size 逾上界一發**。屬 004／005 域，本輪未核其 handler 層有無承載。
- ④**FR-049「64-bit key 拆兩欄比對」**：碼的做法是兩欄組回 64 位全值再比，語意等價，RUNBOOK §11.1 有載理由。
- ⑤**ADR-00066 決定 3「負向測試兩形各一案」**：由一支常駐案三斷言，加上 U7 兩發變異自證兌現，保護力等價。
- ⑥**contracts「十條接在 ROUTES 表尾」**：U16 改置之後已不逐字成立。spec 刻意分岔登記表末列已記，specs 屬史料面。

**L5-1 衍生建議**：見 §2 駁回段之殘留點；不另立 BL。

## 6. 判定

006 authz-governance 刀之 spec 在 HEAD 上**實質兌現**：零 blocker、零 wire 行為缺陷、零無承載之行為偏離。剩餘缺口全數於本輪收掉，零轉帳：

- 測試保護力三筆：rust-api `5f123a6`。
- 現在式碼註、文件與指路六筆：rust-api `5f123a6` 與外層本顆。
- 收刀帳本兩筆：本輪 review 事件 notes 補記。

收刀程序的承接缺口以 RL-0084 擴面補上（LL-00067）；收刀 merge 後的容器重建以 LL-00068 記守法。
