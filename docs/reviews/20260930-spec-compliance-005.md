# 005-role-menu-crud 規格對照審查（spec-compliance-005、2026-09-30）

範圍＝已收刀之 005 role-menu-crud 刀對 `specs/005-role-menu-crud/` 的兌現度：spec.md FR-001～FR-079、SC-001～SC-016、User Story 1～6、Clarifications（Session 2026-09-23 五題、Session 2026-09-24 兩題）、Edge Cases、Assumptions、Out of Scope、★軌道逐處登記表，連同 data-model §1～§10、`contracts/` 四份（wire-role-admin／wire-menu-admin／msg-keys／code-gates）、quickstart.md、checklists/requirements.md；另核收刀後六支維護批對 005 刀所建所定之面的改動有無承載。基準＝HEAD（外層 `ee557f6`、rust-api `d9c4e2f`、base-web `2248b89c`）；收刀點（merge `7f09ae0`）只用於歸因；specs 本文不改（ADR-00012 定點快照）。

## 0. 方法與取證

| 項 | 值 |
|---|---|
| 形式 | RL-0073 承載處②：user 2026-09-30 臨時發起、附屬 005 刀；user 指定以 superpowers:requesting-code-review 對照 spec 做 review；分支 `maint-spec-compliance-005`（自 `rev6-admin-root @ ee557f6`，即 maint-tz-utc 收官後） |
| 編排 | **兩支唯讀 Workflow**（射程互斥；review 骨架 explore＋inline 兩鏡三態；全角色 `opus[1m]` xhigh、零 CDP；零 finding 之 lens 不派兩鏡）。run A＝`wf_cf5bf8d6-62c`（五 lens＋一冷啟動探針；最壞 18），派 16 支、零錯零 null、牆鐘 47.0 分；run B＝`wf_a5b89e75-f26`（五 lens；最壞 15），派 13 支、零錯零 null、牆鐘 48.9 分 |
| 切成兩支的理由 | FR 79 條（004 刀為 70）、契約四份；另需一支專鏡核「收刀後六支維護批對 005 碼面與帳本的改動有無承載」 |
| run A lens | L1 角色 CRUD 與首頁（FR-010～017、FR-008／009／037 角色側、SC-003、wire-role-admin）｜L2 選單結構不變式與讀寫端（FR-018～032、SC-004）｜L3 選單刪除、回收桶復原與歸檔寫入（FR-033～040、SC-009）｜L4 序列化域與判定面同步（FR-041～053、SC-005～007）｜L5 管理頁前端與 fork-delta×憲法 §III（FR-058～066、SC-011 靜態可證部分）｜P1 冷啟動探針三題 |
| run B lens | L6 端點總則、分頁通則與碼表（FR-001～009 跨域總則、FR-054～057、SC-001／002／008、msg-keys）｜L7 憲法 Amendment、治理與帳本（FR-075～079、SC-012／015／016）｜**L8 收刀後變動承載歸因**（六支維護批）｜L9 測試基建與機器守保護力（FR-070～074、SC-010／013／014）｜L10 Edge Cases、Assumptions、Out of Scope、checklists 與 004／002 域連帶（FR-067～069） |
| review 模板 | requesting-code-review 要點烤入兩支 run 之 CONTEXT：spec 是願景文件（spec 沉默處以合理使用者期待判斷）；Critical／Important／Minor 對映 blocker／major／minor；每支 lens 的 notes 末附「做得好的地方」「擱置未判」「本 lens 判定」三段（摘要見 §5） |
| 前三輪經驗 | CONTEXT 烤入七條：BL 到期落點須明寫／逐字出自 accepted ADR 或 specs 之句不得單改現在式面／evidence 可原樣重跑／不逐檔列易漂移名冊／機器枚舉先證樣式集完備／錨字面被自身散文滿足＝恆綠無聲／前三輪與 005 final holistic review 已處置者不重報；另烤 RL-0078 防污染條款 |
| 規則塊 | `rules emit --scope review` 全塊烤入，RULES-VERSION `b7a6a9c8327c` |
| 唯讀邊界 | agent 禁寫入形命令、禁 docker／cargo／pnpm／generate；rev5 樹只讀；python 工具之保護力以記憶體內 exec 變異取證、rust 以讀碼推演 |
| 主線復核 | 24 筆逐筆重讀證據與兩鏡理由；關鍵主張以 grep 實跑複驗（§3）；兩鏡駁回之三筆與探針衍生駁回一筆逐一查其承載 |
| 看門狗 | 兩支 `--bg` 長尾腿於約 35 分時被執行環境之背景時限停止（非 runaway）；改以帶 runId 之 `--rearm` Monitor 補回覆蓋至兩支完成 |
| 未覆蓋 | SC-011 之 CDP 三方對照（承載＝005 刀 U16 走查）；rust 行為面只讀碼推演、本輪未跑 cargo |

## 1. 結論

**零 blocker、零 wire 行為缺陷。** 十支 lens 之判定：L1／L3／L4／L6／L8＝兌現，L2／L5／L7／L9／L10＝修後可兌現。ROUTES 39 與 `MSG_KEYS` 43 和三檔 backend 子樹雙向全等、13 碼矩陣零新變體、零 migration 零 seed 變更；憲法島 H 五條與 ADR-00042 決定文逐字相等；選單序列化域與判定面同步之五類變異（拿掉域鎖、鎖下沉、就地清空重載、觸發改恆觸發或恆不觸發、拿掉互斥）皆可指名會紅的測試；收刀後六支維護批對 005 面之改動逐項找得到承載，005 刀檔在收刀後只有註解改動。

要處置的集中在四類：①**測試保護缺口**五筆（皆經變異推演存活）；②**現在式文件失準**五處，另有收刀面帳本兩處（NOTES 下一步、淨流量分型）；③**延後義務無家**：授權歸檔表的保留期與事後對賬掃描，只住凍結 spec；④**憲法字面精度**：島 H2「唯一已知降級窗」漏記 commit 到換上之過渡窗，§III 修改型標記未涵蓋 Vue 模板屬性行變體。

**user 2026-09-30 裁定（四題）**：①對照輪之修項（文件五處、碼面五筆）本輪只落報告、全部轉 BL，之後併批收；②L4-1 記 BL、交 006 authz-governance brainstorm 一併定；③L5-3 記 BL、下次憲法 Amendment 時併入；④L7-3 本輪調規補一步（RL-0084）。

## 2. findings 與三分流（24 筆原始、無重複：修 3／轉 BL 16 筆→7 條／駁回 4／報告記載 1）

| 編號 | 嚴重 | 類別 | 面 | 一句話 | 處置 |
|---|---|---|---|---|---|
| L1-1 | minor | 測試保護缺口 | `handler/role.rs` parse_update | 提前 no-op 判定之 roleMemo／roleHome 兩腿無單欄案，拿掉任一腿全樹仍綠 | 轉 BL-00130 |
| L1-2 | minor | spec 自身缺陷 | `handler/role.rs` 停用雙護欄×角色編輯抽屜 | 護欄以請求值觸發、不比現值，抽屜恆送現值 status——所屬已停用角色經 UI 改名即被誤擋（007 指派寫端進場後可達） | 轉 BL-00131 |
| L1-3 | minor | spec 自身缺陷 | data-model §2.1 | 「已刪｜任何寫端｜notFound」寫得比 §5.2 固定序寬（提前 no-op 與名稱非空先於鎖列） | 報告記載 |
| L2-1 | minor | spec 自身缺陷 | `handler/menu.rs` query 欄 | 選單新增更新對 `query` 零形制驗證、非陣列值會使前端側欄拋錯 | **駁回**（見下） |
| L2-2 | minor | 測試保護缺口 | `tools/wire-schema.py` 保留路由名對賬腿 | 前端讀面漏 customRoutes；現值零 constant 列、屬潛伏 | 轉 BL-00130 |
| L4-1 | minor | spec 自身缺陷 | 憲法島 H2／ADR-00043 決定 9 | 「唯一已知降級窗」漏記 commit 到換上之有界過渡窗 | 轉 BL-00134（user 裁交 006） |
| L4-2 | minor | 現在式文件失準 | RUNBOOK §13 步驟 1 | `grep '判定面同步'` 另命中收場 task 被取消事件、輸出描述只列兩形 | 轉 BL-00129 |
| L5-1 | **major** | 現在式文件失準 | `code-gate-contracts.md` §4 | 兩條現算式漏用途後綴與圈界形（現算 27、全形 119；軌道名集缺兩名）；spec-compliance-004 修單落地錯 | 轉 BL-00129 |
| L5-2 | minor | 測試保護缺口 | `tools/fork-delta-lint.py` | 範圍欄處數／塊數與活書 08 §8.4 逐檔數皆手寫鏡像、零閘對賬 | 轉 BL-00132 |
| L5-3 | minor | fork-delta 標記或授權失準 | 管理頁三檔四處 | 模板屬性行之修改型標記置於開標籤上方、新增屬性由其涵蓋——憲法 §III 未明文承認此變體 | 轉 BL-00135（user 裁併入下次 Amendment） |
| L5-4 | minor | 現在式文件失準 | 活書 05 base-web 條 | 稱經 `rev6-menu-admin.ts` 打選單九端點，該檔只包八支 | 轉 BL-00129 |
| P1-P1 | minor | 檢索性 | 活書 08 §8.2 | 未界定「查詢串壞形」成員與承載處、「逾界」未限定逾上界 | 轉 BL-00129 |
| P1-P2 | minor | 現在式文件失準 | 活書 06 島 H ③／ADR-00045 款 4 鏡像 | 未寫非獨有按鈕碼之補集；「新增或復原之碼無人持有」全稱句遇共持已授予碼不成立 | 轉 BL-00129 |
| P1-P3 | minor | 檢索性 | README 入口表 | 缺「某領域執行期怎麼跑」一列 | **駁回**（見下） |
| L7-1 | minor | FR／SC 未兌現 | 005 feature_close notes | 未記 FR-078 要求之淨流量值與揭露型／新欠型分型 | 修（本輪 review 事件 notes 補記，見下） |
| L7-2 | minor | 現在式文件失準 | NOTES 下一步 | 「刀序由 user 定」無拍板出處、與 001 brainstorm Q1 刀序及 SC-016 不符 | 修（本輪簿記改寫 NOTES 下一步） |
| L7-3 | minor | FR／SC 未兌現 | 收刀程序 | spec 標「簿記後驗」之 SC 子句無程序步驟承接，003～005 三刀皆無驗證紀錄 | 修（RL-0084＋LL-00049＋CLAUDE.md §2 指針；user 裁） |
| L7-4 | minor | spec 自身缺陷 | spec FR-076／FR-078／SC-016 | 刀內部分改寫後仍保留「ADR 六支」「backlog_add 零」 | **駁回**（見下） |
| L8-1 | minor | 測試保護缺口 | 角色／選單清單列形案 | ADR-00061 定偏移恆 +00:00 後，端點級偏移值零釘 | **駁回**（見下） |
| **L9-1** | **major** | 測試保護缺口 | getRoleList／getDeletedMenus | size 上界 clamp 端點層零案、內聯收斂變異全綠存活 | 轉 BL-00130 |
| **L9-2** | **major** | FR／SC 未兌現 | `sys_menu.rs` 兩案＋`route.rs` 一案 | 以 seed 態絕對值斷言，dev 庫存啟用選單或啟用常量選單殘列即紅＝SC-014 未兌現 | 轉 BL-00130 |
| L9-3 | minor | 測試保護缺口 | `handler/role.rs` 入域源碼釘 | 角色刪除家族缺「begin 後至收場件前零 `?` 早退」腿（選單四支皆有） | 轉 BL-00130 |
| **L10-1** | major→minor | 無承載偏離 | spec Out of Scope 第 8 條後半 | 授權歸檔表保留期／清理政策（`rev5:B-016` 歸檔表一面）現在式帳本零承載 | 轉 BL-00133 |
| **L10-2** | major→minor | 無承載偏離 | spec Out of Scope 第 8 條前半 | 軟刪×授權歸檔之事後對賬掃描（`rev5:B-025` 殘餘②）現在式帳本零承載 | 轉 BL-00133 |

> 轉 BL 之歸併：文件五處合為 BL-00129；碼面五筆（rust 測試四筆須容器 cargo、python 閘腿一筆）合為 BL-00130；L10-1／L10-2 同表同觸發、合為 BL-00133。L10-1／L10-2 依 spec-compliance-004 L10-3→BL-00124 前例降為 minor（兩支 decided 鏡同議）。

### 駁回與報告記載之主線裁定（5 筆）

- **L1-3（報告記載）**：as-built 固定序與 FR-013、contracts §4、data-model §5.2 一致；§2.1 那列屬 spec 字面過寬，specs 為史料面、現在式面零鏡像。
- **L2-1（駁回；real 鏡確認、decided 鏡駁回）**：`query` 零驗是 plan 期 research R9 明載的取捨（「query 同驗形制＝需新鍵、spec 未要求，棄；如需＝新拍板」），brainstorm R1-Q7 拍板的形制驗證只涵蓋 buttons。本筆新增的後果（直打 API 寫入非陣列 `query` 後前端側欄點擊拋錯）只在繞過 UI 時可達，記於此；若要重開，屬新拍板題、不屬本輪。
- **L7-4（駁回）**：ADR 由六支增為十支（ADR-00048～ADR-00051）與 backlog_add 由零變 BL-00126，逐項皆有 user 親決承載（U13b、U16、final review、刀內裁定）；specs 為定點快照，與 spec-compliance-004 L7-4 同判。
- **L8-1（駁回；real 鏡確認、decided 鏡駁回）**：同一形已於 maint-tz-utc 前置時區盤點（run `wf_167447ec-295`）之 L2-3 提出並駁回——`sys_menu` facade 真 DB 讀端測試以含 `+00:00` 字面逐字比對；user 時區第 7 題之題面前提即此，ADR-00061 背景段承載。本筆的 handler 層變異論據未構成新證據。
- **P1-P3（駁回；refuter 駁回）**：README「系統長怎樣」列已導向 ARCHITECTURE 索引、其 §6 列即執行期情境的家，另有多條現在式指針直達 §6.1 島 H；探針判繞路屬跳數問題、非缺入口（建議見 §5）。

### L7-1 補記：005 刀收刀時點之淨流量與分型

005 刀收刀時點（簿記 `68ca376`）rolling-3 淨流量＝14；brainstorm 工程判斷 41 預估 13，差 1＝BL-00126（刀內 user 2026-09-25 裁定記帳，使「005 本身 backlog_add 為零」之前提不成立）。分型：BL-00126＝新欠型（治理工具面、非 005 域揭露）；005 域揭露型零。feature_close 之 notes 屬不可更正欄，依 RUNBOOK §12c 以本輪 review 事件 notes 同記。

### L7-3 調規（user 裁：本輪補一步）

新增 RL-0084（主線、checklist、source＝LL-00049）：收刀 perf 第四步那顆 commit 內，逐欄核對 spec 標「收刀面於簿記 commit 後驗」之 SC 子句並把結果寫入該顆 commit 訊息；不符者引承載或轉 BL。CLAUDE.md §2 編排範本第四步與收刀段各補一句指針。005 刀本身之收刀面由本報告逐欄補核：adrs 十支（多出四支皆有 user 親決承載）、backlog_add＝BL-00126（有承載）、backlog_done 19 條與 FR-078 集合相等、NOTES 下一步未指 006（L7-2）、notes 缺淨流量分型（L7-1）。

## 3. 驗證（主線實跑）

- L1-1：`sed -n` 讀 `parse_update` 提前 no-op 之 AND 鏈；`grep` updateRole 實發 body，只帶 roleMemo 或 roleHome 起首者恰一例且兩欄並存。
- L1-2：停用護欄以 `update.patch.status.is_some_and(...)` 判定；角色編輯抽屜 `fetchUpdateRole` 恆帶 `status: model.value.status`。
- L2-2：`tools/wire-schema.py` 讀面常數只有 `ELEGANT_ROUTES_TS`／`BUILTIN_ROUTES_TS`；`src/router/routes/index.ts` 之 customRoutes 以 `[...customRoutes, ...generatedRoutes]` 入靜態路由，現值 `constant:` 零命中。
- L4-2：RUNBOOK §13 步驟 1 之 grep 字面與輸出描述逐字比對；`enforce.rs` 兩則、`menu.rs`／`role.rs` 各一則取消事件訊息皆含「判定面同步」。
- L5-1：§4 式新增型現算 27、涵蓋用途後綴與圈界尾形之全形 119。
- L5-4：活書 05「打後端角色八端點與選單九端點」一句存在；`rev6-menu-admin.ts` 之 `export function` 恰 8。
- L9-1：全樹 `size=` 逾 100 之字面只在 envelope 與 facade 之註解、ip_rule 清單案與選單治理清單案，getRoleList／getDeletedMenus 零案。
- L9-2：`sys_menu.rs` 以 78 絕對值斷言顯示域全收；`menu.rs` 之 `STATUS_DEFAULT` 為 1（addMenu 缺省即啟用）。
- L9-3：`contains('?')` 在 `role.rs` 0 處、`menu.rs` 4 處。
- L4-1：「唯一已知降級窗」在憲法與 ADR-00043 各 1 處。
- L5-3：menu 頁 `#header-extra` 標記位於 `TableHeaderOperation` 開標籤之上、內文自陳「屬性之間放不了標記」。
- 本輪落地後 `python3 tools/docsync lint`：0 錯誤，GT-03 七則在途警告（BL-00129～BL-00135 之 backlog_add 於收單事件補上即消）。

## 4. 冷啟動探針（只入報告與事件 notes、不填事件 `probe` 欄）

三題（刪選單後授權與判定面、回收桶復原之拒因與授權是否回來、三清單端點之分頁規則與例外）皆 found、答錯 0、找不到 0，三題皆判繞路（最短 2／2／1 跳）。共同成因＝活書 06 島 H 與 08 §8.2 對「補集」「壞形成員」未寫明，探針須下探碼註或 ADR 才得全貌——已併入 BL-00129 ④⑤。探針在 Q1 另指出「commit 到換上之間的間隙文件沒明寫」，與 L4-1 同源（BL-00134）。

## 5. 各 lens 判定摘要與建議（requesting-code-review 模板要點）

- **做得好的地方（摘）**：`move_to_archive` 以已掃 id 圈定 DELETE 並比對實刪數，把「掃描集＝歸檔集＝刪除集」釘在結構上；判定面同步觸發測試一律先斷言刪前命中再整行比對計數（防恆綠）；批刪之「逐項交錯」與「同批共持碼恰歸檔一次」以 PG cmin 轉為可斷言值；授權中介層 lint 植入反例一律走與主案同一條掃描管線；`role_menu_authz_matrix_real_seed` 把「路徑×動詞逐字對齊 seed」轉成判定面行為證；menu 頁分頁元件以頁數分支封住每頁 0 之無限頁數凍死路徑。
- **擱置未判中值得主線留意者**：①選單彈窗 `watch(routeName)` 首開編輯即重設 i18nKey 與 routePath（upstream／rev5 同碼、seed 78 列皆合命名慣例），建議下次 CDP 走查抽驗自建列；②判定面重建於 `Enforcer::new` 後再顯式 load_policy＝雙載（只作用於非現役新實例、正確性無虞），屬可選最佳化；③`handler/common.rs` 檔頭稱某錨「全檔恰一處」實有兩處（出自 005 刀之前、保護力不受影響）。以上皆未列為 finding。
- **P1-P3 衍生建議**：活書 06 frontmatter `summary` 可改為「執行期情境（依行為島分則）」，由 generate 帶進 ARCHITECTURE 索引，縮短「某領域執行期怎麼跑」的檢索跳數；不另立 BL。

## 6. 判定

005 role-menu-crud 刀之 spec 在 HEAD 上**實質兌現**：零 blocker、零 wire 行為缺陷、零無承載之行為偏離；剩餘缺口為測試保護力、現在式文件精度與延後義務承載，依 user 裁定轉入 BL-00129～BL-00135，建議 006 authz-governance brainstorm 起手前與 BL-00128 併批評估（BL-00131 綁 007、BL-00133 綁 008 或背景 job 刀、BL-00135 綁下次 Amendment）。
