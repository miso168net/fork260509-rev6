# 001-schema-baseline 規格對照審查（spec-compliance-001、2026-09-04）

範圍＝已收刀之 001 schema 基線刀對 `specs/001-schema-baseline/spec.md` 的兌現度（FR-001～FR-018、SC-001～SC-007、六個 User Story 之 Acceptance Scenarios），連同碼品質、架構、測試與 production readiness。對象 git 範圍＝`16358f1..432e47b`（75 檔、+12020／−1172；子庫 rust-api `512024e..d443278`）。★不含其後與本刀無關之治理維護批。

## 0. 方法與取證

| 項 | 值 |
|---|---|
| 形式 | 不定期獨立輪（user 於收刀後臨時發起）；一支唯讀審查 agent（`opus[1m]`、ultrathink），非 Workflow 編排 |
| 規則塊 | `rules emit --scope review` 十四條全塊烤入，RULES-VERSION `e41e0f177ef3` |
| 唯讀邊界 | 禁一切寫入形與 git 狀態變更；★另加禁 `git worktree add`（兩子庫本身即 worktree、承重結構）；rev5 樹只讀 |
| 主線復核 | 依 CLAUDE.md §5 不採信 agent 回報：三發變異探針（`_check_col` 型別腿／gate1 索引·約束整節／`seed_add` 欄集斷言）分別廢除後自帶 103 案仍全綠，逐條復現屬實；另實查 `tools/docsync/` 零處引用 `fixtures`、`archived_by` 於 `schema-gate.py` 出現 0 次、`doccheck` 牆鐘 0.17 秒 |
| 審查涵蓋 | 五趟：規格面／工具碼面／rust 面／治理面／驗證面；41 發變異探針（schema-gate 22、entity-drift 4、docsync 15），28 發轉紅、13 發空轉 |
| 未覆蓋（審查員自述） | 未跑 cargo（禁用且 host 無 toolchain，建置綠只能採信 commit 訊息）；未做 pristine 重放（需建容器），改以三路交叉間接支撐 SC-002；`data-model.md` 672 行未逐行讀，靠 doccheck 機器對賬取信 |

## 1. 結論

**零 Critical。** 功能面全對：17 檔逐位元、fixtures 雙源互證、三閘與 entity 漂移閘實跑全綠，主線獨立復驗無 bug、無資料風險。要處置的全是**回歸保護的缺口**與簿記。

FR-001～FR-018、SC-001～SC-007 逐條兌現，審查員獨立復跑之關鍵值：17/17 去註解零差異、四份 fixtures 對 rev5 `cmp` 全等且 sha256 合 provenance §4、`rust-toolchain` 1.96.1 與 dev 映像同值、Cargo.lock 四支依賴版本與 research R1 三源核對表相符、`reference/{schema,accounts}.md` 表體與 rev5 同名生成物逐位元相同、`archetype-map.json` 15 表 A×5／B×4／C×4／D×2 與 `data-model.md` §1 逐筆相符。

## 2. findings 與三分流（8 筆：修 6／轉 BL 2／won't-fix 0）

| 編號 | 嚴重度 | 面 | 一句話 | 處置 |
|---|---|---|---|---|
| I-1 | Important | `tools/schema-gate.py` audit 引擎 | 變體判準零負向覆蓋：九處判準逐一廢除，自帶 103 案全綠。它是憲法 §I.6 六審計欄與 ADR-00010 決定 7 的唯一機器載體 | 修 |
| I-2 | Important | `tools/schema-gate.py` `compare_structure` | gate1 的 indexes／constraints 兩節零負向覆蓋：整節廢除仍全綠。索引與約束承載 soft-delete 活性唯一、casbin 委派、FK RESTRICT 等語意 | 修 |
| I-3 | Important | `.githooks/pre-commit` | 凍結面（`fixtures/`、`data-model.md`）零機器保護：改壞一格 commit 全綠，而 `contracts/fixtures.md` §4 自稱其位元變更為「違憲級」 | 修 |
| M-1 | Minor | audit D 變體 | `archived_by`（憲法 §I.6 變體 D 明列）不在驗則內，`schema-gate.py` 全檔零命中 | 修 |
| M-2 | Minor | audit A 變體 | `active_unique` 缺反向完整性守門：實庫有活性唯一 partial index 卻未登進 map 即靜默不驗（今日實查零缺口） | 轉 BL-00020 |
| M-3 | Minor | `apply_seed_entries` | `seed_add` 的 `values` 欄集全等斷言零測試：廢除後 `KeyError` 裸例外取代 rc 2 fail-loud，正是該斷言註解說要修掉的形 | 修 |
| M-4 | Minor | `rust-api` 入口檔 | 五個宣告「自寫」的檔去註解後與 rev5 等價（`main.rs` 僅差一處變數改名），憲法 §I.5 例外②射程鎖 17 檔，機器上分不出「重打字收斂」與「拷貝」 | 轉 BL-00021 |
| M-5 | Minor | `tools/docsync/snapshot.py` | `cmd_refresh` docstring 的「零寫入」宣稱強於實作：兩檔各自原子寫入、非跨檔單一交易 | 修（docstring 收斂） |

### 三分流細節

**修（6 筆）**——落於本輪修單 commit：

- **I-1**：新增 `TestAuditArchetypeNegative`（11 案）。右源＝真凍結 fixtures ⊕ 真 archetype-map、離線注入。覆蓋型別／可空性／default／欄缺席四腿、A 活性唯一索引的缺席與 `WHERE deleted_at IS NULL` 兩腿、C 子型複合 PK、D 治理欄、`created_by` 顯式驗。
- **I-2**：`TestNegativeInjection` 加三案（索引缺一支／約束定義異／索引未登記多一支）。
- **I-3**：`pre-commit` 加 `schema-frozen` 條件段（`grep -qE '^specs/001-schema-baseline/(fixtures/|data-model\.md$)'` → `schema-gate.py test`，實測 0.36 秒、零 docker）。同批依 RL-0011 改齊五處守門鏈列舉（hook 檔頭、README 兩處、`P-E1-boundary.md`、`P-C4-E3-materials-boundary.md`）。
- **M-1**：D 變體補 `_check_col(..., "archived_by", "bigint", nn=False)`；`contracts/gates.md` §3 同批補句。★本項為真正的先紅後綠：檢查不存在，測試先失敗、加驗則後轉綠。
- **M-3**：`TestDetailBadForms` 加 `values` 欄集不等一案。
- **M-5**：`cmd_refresh` docstring 收斂為「零寫入保證的射程＝撈取與組裝階段」，並註明兩檔各自原子、非跨檔單一交易。

**轉 BL（2 筆）**：M-2 → BL-00020、M-4 → BL-00021。

**won't-fix**：無。

### 契約面同批修正（非 finding，屬 I-1／I-2 的規格側）

審查員指出 I-1／I-2 同時是 **spec 自身的缺口**而不只是實作偷懶：`contracts/gates.md` §4 的 negative 義務清單只列五類（結構／欄序／seed 值／sequence／假 delta），audit 面根本不在清單裡，且「結構」的字面只涵蓋 columns 節。實作是照 spec 做的。故同批把 §4 由五類擴為六類，並在①註明 indexes／constraints 兩節與 columns 同義務、新增⑥ audit 變體驗則面（並註明⑥與①～⑤的差別：前五類注入「實庫漂移」、第六類注入「驗則會不會抓」）。

## 3. 驗證（主線實跑）

| 項 | 值 |
|---|---|
| `schema-gate.py test` | 103 → **118 案**（新增 15）全綠 |
| 變異驗紅 | 十發探針逐一打在新案對應的判準腿上、**全數轉紅**（型別／可空性／default／欄缺席／活性唯一索引缺席／索引 WHERE／C 複合 PK／`created_by` 顯式驗／gate1 索引·約束節／`seed_add` 欄集）；驗紅在同構目錄的副本上做、repo 零寫入 |
| hook 段離線四案 | fixtures 檔→觸發；`data-model.md`→觸發；同目錄他檔→不觸發；他刀 fixtures→不觸發 |
| 其餘 | `docsync test` 126 綠、`check` 零漂移、`lint` 0 錯 0 警 0 跳過、`doccheck` rc 0、`entity-drift test` 45 綠 |

## 4. 建議（未列為 finding、供後續刀參考）

1. **`data-model.md` 的可變性定位**：它住 `specs/001-schema-baseline/`，隔壁 `fixtures/` 宣告「永不改寫」，但 `gates.md` §3 與 RUNBOOK §10 都要求後續刀回頭改它；`parse_data_model_five` 另硬編碼 `if len(tables) != 14`。同一個 feature spec 目錄裡混了凍結史料與跨刀活體權威，002 之後首支加表的刀會同時撞到兩者。→ BL-00022，觸發訂 002 開分支前。
2. **audit 的 C／D 子型規則硬編碼於工具內**（`if t == "sys_user_role" / …`），map 的 `note` 只是人讀；未硬編碼即 `GateError` rc 2 的設計正確，但表數長起來後宜把子型規則資料化到 map。
3. **schema 防線的自動觸發面**：`check` 需 docker、`doccheck` 刻意不入鏈，本輪 I-3 已把「離線可跑的那一半」掛上條件觸發，補回大半。
4. **三指標之「治理批對 feature 比」首度有真值 7.0（目標 ≤1）**：創世波使然、非本刀問題，但宜在下一刀收刀時決定是「三刀後才看」還是「現在就該壓」。

## 5. 判定

**需要後續處置：是（本輪即處理完）。** 八筆全部落地或轉帳，無一動到已 accepted 的 ADR、無一需要 spec 翻案以外的動作。
