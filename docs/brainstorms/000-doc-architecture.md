# rev6 啟動書（v1.0 拍板定稿、2026-09-03）——RAD-AI 完全導入的文件治理架構

> 性質：階段 0 brainstorm 產出（對應 rev5 的 `docs/brainstorms/000-doc-architecture.md`）。執筆＝主線 Claude Fable 5.1；拍板＝user。本檔住 `tmp/`，rev6 workspace 建立後搬進其 `docs/brainstorms/000-*.md`（史料面，比照 rev5 豁免裸編號規則）。
> v1.0：D1～D17、§3.8、§4.2 全部經 user 逐題拍板（2026-09-02～03）；覆核 R1／R2 共 52 條處置見附錄 F。
> §1.2 各列保留原預設與理由供追溯，「已拍」欄為定案。
> 輸入：`tmp/RAD4AI-report.md`、`tmp/docs-governance-review-20260902.md`、`tmp/arc42-vs-rev5-sections.md`、`tmp/RAD4AI-decisions.md`、`tmp/annex-iv-2e-check.md`、`tmp/rev6-review/R1-*.md`／`R2-*.md`、`tmp/RAD4AI-wf/` 十五份分報告、`tmp/RAD-AI/`（fork、HEAD afdd36d、MIT）。
> 口徑：rev5 lint 條款數一律「29 條款（另 Lint99 為 meta、Lint23 不存在）」，取工具 `derive_lint_codes` 自報值。

---

## 0. 目的與成功準則

### 0.1 目的

把 RAD-AI（arXiv 2603.28735v1）的**全部項目依其編號**導入 rev6 的文件治理：八個 arc42 擴充 E1～E8、三個 C4 擴充 C4-E1～E3、Annex IV 合規檢核表與十類映射、三階段採用路徑、名詞表。rev6 是完全重構的新世代：workspace、文件骨架、治理工具、編號格式全部重來；系統本體**重寫**（rust-api 全新寫、對 rev5 受控參照；base-web 自 rev5 同一 upstream 基線 SHA 重新 fork），rev5 現況＝藍本與對照基準。

### 0.2 非目標

- 不在 rev5 上改（rev5 自本檔拍板日起凍結為唯讀對照基準，同 rev5 對 rev4 的作法；凍結的機器面見 D17）。
- 不為了填滿 RAD-AI 模板而虛構 AI 元件；每個 E 子節都有真實承載對象或一句誠實的「目前無」（§3.4）。
- 不搬運 rev5 的 29 條 lint 與 24,226 行治理工具原樣（§4）。
- 不逐檔遷 rev5 的 79 份 ADR、87 條 LESSONS、35 條 BACKLOG（§3.7 遷入判準）。
- 刀序不在本檔定（D13：留到 rev6 首刀 brainstorm）。

### 0.3 成功準則（兩層）

**A. 文件創世 DoD（波 0～5 收官）**

1. **對照總表逐列兌現**：§3.3 表每一驗收列的 rev6 檔案或子節存在且非佔位。機器判＝GT-10 三腿（`*[`、`_{5,}`、未勾 `- [ ]`）零殘留＋Evidence 欄所引檔與具名表實存（連結存在＋表標題字面命中）；非驗收列（三階段採用路徑、Glossary）明標、不計。
2. **addressability 自評**：以 RAD-AI 的 0／1／2 量表對 §3.3 驗收列與 Annex IV 23 鍵自評，附證據欄；系統層無 AI 元件者標「不適用」附理由、不計分（此為對 reference 的刻意偏離，登記於附錄 A F24）。
3. **三指標落地**：演算法與空值語意寫進 generate，對現帳輸出數值或「n/a（尚未足 3 刀）」，不是人寫。
4. **核心 lint 全綠且 Day-1 豁免逐筆有解除謂詞**（§4.6）；守門名冊逐條有「守哪條規則／來源／掃描面／拿掉會壞什麼」。
5. **藍本對照表零缺**：rev5 活書每個 `###` 標題在 `docs/generated/reference/rev5-blueprint-map.md` 都有去處（rev6 節／隨刀 NNN 填入／不承襲附理由），缺一即紅（一次性 migrate-audit）；rev5 ADR 不入此表（D5：不遷、備用摘要住 tmp）。
6. **碼制重編完成**：rev6 現在式文件面（arc42／c4／compliance／process／ops／generated）零裸 rev5 編號；`docs/brainstorms/` 與 `specs/` 比照 rev5 為史料豁免面，豁免登記於 GT-05 名冊。

**B. 世代 DoD（每刀）**：該刀觸及的憲法 §I.7 行為島不變式全過＋CDP 對照 rev5 stack（2xxxx）行為全等＋走查基準六步還原。刀序與各刀範圍由首刀 brainstorm 定（D13），本檔不承載。

---

## 1. 拍板前提

### 1.1 已拍板（user 2026-09-02）

| # | 題 | 拍板 | 連動 |
|---|---|---|---|
| Q0 | RAD-AI 是否作為參照對象 | 完全導入，對象＝重構的 rev6 | 本檔 |
| — | rev6 範圍 | 完全重構，含編號格式重編 | D4 |
| D1 | rev6 的「AI」指哪一層 | 流程層先實作、系統層預留骨架 | §3.3／§3.4；流程層的家見 D16 |
| D2 | 程式碼範圍 | **重寫**：rust-api 全新寫、對 rev5 受控參照；base-web 重新 fork | §0.3 兩層 DoD、§3.7 藍本形、§5 波次、§6 風險、§3.8 憲法 §I.5 世代 bump、rev5-inline 標記不帶（rev6 token＝`rev6-inline`） |
| D12 | 埠世代 | 3xxxx（32080 UI／32079 API／32443／35432／36379／38025） | §5 波 1 產物「compose 三檔＋reference/ports 首版」；埠配號立 ADR（承 rev5 ADR 0004 形） |
| D13 | 系統重寫刀序 | 留到 rev6 首刀 brainstorm 再決定 | §5 波 6 起只留「刀」佔位；§3.3 系統層欄只寫「隨刀填入」 |
| D14 | base-web 基線 | 沿用 rev5 的基線 SHA、不前進 upstream | rev5 435 處 `rev5-inline` 標記可逐位元當藍本；upstream rebase 欠帳留 rev6 自決 |

### 1.2 拍板紀錄（原預設與理由保留；定案見各列「已拍」）

| # | 題 | 預設 | 理由（可反駁；R＝覆核修正） |
|---|---|---|---|
| D3 | RAD-AI 23 筆不一致以誰為準 | **已拍（2026-09-03）：逐筆取捨；reference 為預設仲裁者，取模板或 adoption-guide 者於附錄 A「採哪份」欄註明** | R1-F18：v0.2 的「reference 為準」被附錄 A 五筆自破，改述為實際運作形 |
| D4 | 新碼制 | **已拍（2026-09-03）**：BACKLOG `BL-00001`、LESSONS `LL-00001`、ADR `ADR-00001`（皆五碼）；刀名 `001-slug` 與 FR／SC `FR-001` 照 spec-kit 模板不動；任務 `T001`、user story `US1` 同（spec-kit tasks-template）；migration `m0001`（四碼）；規則層 `RL-0001`（四碼）；閘碼 `GT-01`（rev6 為新規則集、`LintNN` 為 rev5 跨代家族）；agent `AGT-001`；流程層檔 `P-E<k>`；執行單元 `U<n>` 與 findings `F001-1` 沿 rev5；`§P`／`§G`／`§S`／`R` 四族 rev6 不預先定形、首刀需要時再定，但 G05 登記其 rev5 字形以偵測漏前綴引用；RAD-AI 表內 ID 沿其慣例；Annex IV 列鍵 `AIV-<點><子項>`（附錄 G）；events 無編號；裸刀號禁、跨代 `rev5:` 前綴、G05 雙 pattern | user 逐族拍板；18 家族處置見附錄 E |
| D5 | rev5 帳本遷入 | **已拍（2026-09-03）：四本帳全部不遷。** rev6 的 ADR／LESSONS／BACKLOG／events 自零起；rev5 帳本以唯讀連結引用。rev5 session 只把「已證實有效的規則」做成兩份摘要（`rev5-adr-digest.md`：值得承襲的決策逐列＋rev5 號；`rev5-rules-digest.md`：約 30 條已晉升規則、命令句形）**暫存到 `../fork260509-rev6/tmp/` 備用**；rev6 需要時再決定是否立 ADR 或進 RULES 首版。RULES 的 `source` 欄允許 `rev5:L-NNN`／`rev5:ADR 00NN` 形 | user 拍板；R2-F10／F14／F09 的三個 vacuous 判準隨之消失（不再需要遷入判準） |
| D6 | E8 新節落點 | **已拍（2026-09-03）**：§13；檔名 `13-operational-ai-view.md`、與 RAD-AI 的 `12-` 檔名慣例刻意分歧 | 決定性正證＝framework-overview.md 第 176／179 行「S12 Glossary (unchanged)」「One entirely new section (E8) is added」；反向訊號＝RAD-AI 全部檔名用 `12-`（R1-F17） |
| D7 | 圖表記法 | **已拍（2026-09-03）**：Mermaid；配套規則「圖內節點名必出現在同檔表格列；C4-L2 節點 ⊇ compose 服務名」由 **GT-10** 承載 | R1-F13：v0.2 配套規則零守門載體 |
| D8 | 治理預算 | **已拍（2026-09-03）**：分兩類：**內容配額退役**（無行數配額）；**治理面數量預算**保留但形制固定＝超限只擋新增、不可調數字、只能一進一出或走 ADR；數值：lint 條款 ≤12（G 表）、RULES 條數上限＝波 1 實算去重後 ＋25%（60 為佔位）、每 scope 另設上限、BACKLOG 開放 ≤25、CLAUDE.md 行數只報表不擋 | R2-F12／F13／D8 反證：≤12 零餘裕、60 條算術不足、≤20 低於 rev5 歷史最低 24、行數配額與 §2 病因自撞 |
| D9 | Annex IV 檢核表 | **已拍（2026-09-03）**：列鍵＝真實 Annex IV 點號與子項 `AIV-1a`～`AIV-1h`、`AIV-2a`～`AIV-2h`、`AIV-3`～`AIV-9`（23 鍵；點 3 子項待波 2 對官方原文細分）；RAD-AI 原列號（1.1～9.2）降為第二欄、只作出處對照；RAD-AI 十類號第三欄；RAD-AI 無對應的鍵（1d～1h、2f、2h、7、8）標「RAD-AI 無對應、rev6 補」；系統無 AI 期間逐鍵「不適用」附理由 | `tmp/annex-iv-2e-check.md`；R1-F09；user 拍板 |
| D10 | 建置期治理程序 | **已拍（2026-09-03）：波 1 全部在 `../fork260509-rev6/` 開的新 session 執行**。起手前由 rev5 session 把交接包（本檔、拍板檔、RAD4AI-report、governance-review、annex-iv 查證、對賬腳本）放進 `../fork260509-rev6/tmp/`；rev6 session 首件＝自 `../fork260509-rev5/` 拷貝守門五件：三支 hook＋settings.json、wf-watchdog、編排骨架（入 `tools/orchestration/`）、過渡版 CLAUDE.md（只含 rev5 §2 編排紀律與 §6 硬禁令）、.gitignore／.dockerignore；首顆 commit 落這五件，之後才建其餘。空窗＝新 session 開到首顆 commit 之間（零 hook），以人紀律補 | R2 D10：環形依賴以「首件拷貝」收斂；R2-F11／R1-F08：骨架入 repo |
| D11 | upstream 回報 | **已拍（2026-09-03）：不回報**；驗證材料（A1 23 筆、A2 17 筆、Annex IV 六列錯位）留 tmp/ 供 rev6 自用 | 對外行為、user 拍板 |
| D15 | RAD-AI 授權面 | **已拍（2026-09-03）：不逐字照抄，RAD-AI 的子節名、欄位、檢核表列文字全部改寫成中文；只在 README 提一句參考來源**（含 upstream `Oliver1703dk/RAD-AI` 與對照 HEAD `afdd36d`）。不設 NOTICE、不逐檔聲明、不建 rad-ai-pin、不立觸發式 BACKLOG。RAD-AI 原子節名（英文）只作 frontmatter `rad_ai_map` 對照鍵與本檔的出處引用，不出現在 rev6 文件正文 | user 拍板；R1 遺漏 1 以「不複製實質部分」收斂 |
| D16 | 流程層的家 | **已拍（2026-09-02）：獨立成 `docs/process/`**（E1～E8 形制套用於開發流程的 AI 代理，每擴充一檔 `P-E<k>-*.md`）；arc42 的 E 子節只放系統層（目前＝一句「目前無 AI 元件」）＋一行指針到 process 檔 | R2-F01：把 agent 名冊寫進八個 arc42 節＝重演 §2-6 診斷的病；R1-F07 層別錯置同源 |
| D17 | rev5 凍結與源倉 | **已拍（2026-09-03）：與 rev5 相同做法**——`../fork260509-rev6/`（已建）根下 clone `fork260509-soybean-admin-base`（切 example tip 8be6f9ba＝D14 基線）與 `fork260509-rev2-anew-rust-api`（main＝Initial commit 32c5254），各 `git worktree add` 出 `base-web/`（分支 rev6-admin-base-web 自 8be6f9ba）與 `rust-api/`（分支 rev6-admin-rust-api 自 32c5254）；兩源倉 gitignored；`.dockerignore` 自 rev5 copy 再調註解（含 `fork260509-*/`）。凍結三件套維持：remote 分支保護＋rev5 NOTES 凍結宣告＋rev6 bootstrap 斷言 rev5 三處 HEAD＝凍結 SHA | R2 遺漏 3；rev6 源倉為新 clone、與 rev5 物理隔離 |
| §3.8 | 憲法射程 | **已拍（2026-09-03）**：逐條表（13 條、含 §I.5 改寫、§V.1 權威鏈納 RULES、§V.2／V.3 承襲）與一條新增方向性條款 | R2-F02 |
| §4.2 ★ | 核心 lint 12 條 | 修訂版 GT-01～GT-12（Lint10／14／15 回到 GT-06；Lint22 併 GT-12；Lint30 成 GT-11；hook 對賬併 GT-09；Lint20 為每條 G 的橫切要求） | R2-F03／F04／F05 |

---

## 2. rev5 診斷（設計依據）

只列會改變 rev6 設計的結論；證據在各報告內，數字經 R1／R2 逐項復算相符。

1. **治理是只加不減的棘輪**：29 天 8 個 feature 對 52 批維護；79 份 ADR 中 32 份純治理；29 條 lint 塞在 14,827 行單檔、59% 是測試；BACKLOG 開放數 24～52 震盪無收斂。⇒ D8 數量預算與 §4.3 三指標。
2. **agent 知識通道只有一條且已滿**：規則要生效必須進 CLAUDE.md（229/250 行）；LESSONS 87 條 agent 從不讀；5 條純未晉升、4 條僅有候選再晉升位；寬口徑 44 條（嚴口徑 17 條）坑出自自製 harness。⇒ §3.6 規則層與 emit。
3. **用內容配額守內容規則**：行數配額生出 ADR 0058／0062 與釘值測，§5／§6 撞頂而 §3／§7／§10 八刀空著。⇒ 每節一檔、無內容配額；數量預算另立形制（D8）。
4. **rev5 的機器守全面強於 RAD-AI，弱的是欄位形制**：§10 零品質需求記載、ADR 無翻案觸發器慣例、FR 層追溯不存在於形制、模型分派零結構化留痕、hook 註冊零對賬。⇒ 用 RAD-AI 欄位形補形制。
5. **RAD-AI 自身零守門且漂得比 rev5 慘**：23 筆內部不一致、examples 的 checklist 引用不存在的檔、Evidence 欄六處失真、22/22 假滿分。⇒ 每張 RAD-AI 表都有機器對賬面，佔位判準對每份模板都非空（GT-10）。
6. **rev5 把流程寫進了系統的書**：§1 建置狀態、§4 文件觀、§12 十五個詞裡三分之二是流程行話。⇒ 流程層獨立成 `docs/process/`（D16），系統書回歸系統。
7. **BACKLOG 不收斂的成因不是「觸發欄不填」**（35/35 已填），而是觸發條件寫成「下一把動 X 的刀」這種永遠等得到、也永遠不到期的形。⇒ §3.7 以「觸發條件是否仍在 rev6 射程」過濾；`docs-governance-review` §2.1 該句同日勘誤。

---

## 3. rev6 文件架構設計

### 3.1 材質與家

- **人寫**／**事件源**／**機器生成**三材質承襲 rev5。機器生成的家＝`docs/generated/`；**例外**＝路徑沿革需保留的索引檔（`docs/arc42/ARCHITECTURE.md`、`docs/ops/LESSONS.md`）：登記於 `GENERATED_FILES` 名冊、檔頭 Generated 標記、GT-01 掃描面納入、重算冪等（承 rev5 碼樹產物檔紀律 ADR 0052 三件套）。
- 每個事實只有一個人寫的家；鏡像不是機器生成、就是不存在。
- 時態分離：arc42／c4／compliance／process 永遠現在式（GT-06 時態腿守）；未來式住 ops/；過去式住 git＋events。
- 完成即刪、git 即史。
- 文件權威鏈：constitution ＞ ADR accepted ＞ RULES.md ＞ arc42／c4／compliance／process ＞ generated；RULES 與 accepted ADR 衝突＝RULES 有誤、就地改 RULES。

### 3.2 骨架

RAD-AI 的定位是加掛不是取代（論文 §II-A、reference 第 38 行）。E1～E7 各成所掛節的子節、E8 獨立 §13；E 子節的子項清單取自 **reference「What It Documents」的 `####`**（D3），模板 `##` 只作形制參考。E1 的 Key Artifact 是「Annotated context diagram」，故 E1 的標註落在 3.2 技術脈絡的圖上、3.3 只放契約與清冊。

```
rev6/                                   傘狀 repo、default branch rev6-admin-root
├── CLAUDE.md                           程序與指針；規則住 docs/ops/RULES.md；行數只報表
├── README.md                           文件地圖；一句參考來源「文件骨架參考 RAD-AI（Oliver1703dk/RAD-AI @ afdd36d）改寫」（D15）；目錄樹 ↔ tools/、deploy/、.githooks/、.claude/ 實檔集機器對賬（GT-09）
├── .gitmodules                         base-web／rust-api gitlink（手寫、不 submodule add）
├── .gitignore／.dockerignore            承 rev5：兩源倉 `fork260509-*/` gitignored＋dockerignored；註解改 rev6 語境
├── fork260509-soybean-admin-base/      源倉 clone（example 8be6f9ba、gitignored）→ worktree base-web/
├── fork260509-rev2-anew-rust-api/      源倉 clone（main＝Initial commit 32c5254、gitignored）→ worktree rust-api/
├── .githooks/pre-commit                核心 lint GT-01～GT-12＋納冊工具自測迴圈；pre-push；lib/
├── .claude/hooks/                      session-start.sh／pre-workflow-gate.py／post-workflow-reminder.py（自 rev5 拷貝、D10）＋settings.json（GT-09 對賬）
├── .specify/memory/constitution.md     rev6 1.0.0（§3.8 逐條表）
├── docker-compose.yml／.dev.yml／.example.yml   埠世代 3xxxx（D12）；C4-L2 與 reference/ports 的真源
├── base-web/、rust-api/                worktree（gitlink）：分支 rev6-admin-base-web 自 8be6f9ba、rev6-admin-rust-api 自 32c5254
├── deploy/                             secrets 家族九支＋grafana provisioning（隨 compose 拓樸遷入；GT-09 對賬）
├── docs/arc42/
│   ├── ARCHITECTURE.md                 索引層（機器生成、例外註冊）：節號｜標題｜一句摘要｜掛載的 E｜流程層對應檔
│   ├── 01-introduction-and-goals.md    1.1 Requirements Overview／1.2 Quality Goals／1.3 Stakeholders（G1～G5 缺口作「本框架要解的缺口」一段）
│   ├── 02-architecture-constraints.md  技術／組織／慣例三類約束（官方無編號子節）
│   ├── 03-context-and-scope.md         3.1 Business Context／3.2 Technical Context（含 C4-L1 圖、E1 標註）／3.3 E1 — AI Boundary Delineation（AI Components Inventory／System Boundary Diagram／Four-Part Boundary Contract／Failure Modes／External AI Dependencies）
│   ├── 04-solution-strategy.md         技術選擇／頂層分解／品質目標達成法（官方無編號子節）
│   ├── 05-building-block-view.md       5.1 Whitebox Overall System／5.2 Level 2／5.3 Level 3／5.4 E2 — Model Registry View（Model Inventory Table 八欄／Per-Model Detail Sections／Integration with Model Cards／Integration with Model Registry Tools）
│   ├── 06-runtime-view.md              6.1～6.n Runtime Scenarios／6.n+1 E3 — Data Pipeline View（Pipeline Overview Diagram／Pipeline Inventory Table／Quality Gates 五欄 Gate ID／Location／Check Type／Threshold／Action on Failure／Feature Store Documentation／Feedback Loops／Integration with Data Cards）
│   ├── 07-deployment-view.md           7.1 Infrastructure Level 1（含 C4-L2）／7.2 Infrastructure Level 2
│   ├── 08-crosscutting-concepts.md     8.1 資料慣例／8.2 API 慣例／8.3 授權慣例／8.4 fork-delta 軌道（承 rev5 FORK-DELTA-WIRING 的規則面）／8.5 E4 — Responsible AI Concepts（Responsible AI Concern Matrix／Fairness／Explainability／Human Oversight／Transparency／Privacy／Safety；六類＝附錄 A F01 聯集）
│   ├── 09-architecture-decisions.md    指針到 decisions/ 與 DECISIONS-INDEX／9.1 E5 — AI-ADR 形制與對映表（模板五 #### ↔ reference 七欄：1. Model Alternatives Considered／2. Dataset Characteristics／3. Fairness and Bias Trade-offs／4. Expected Model Lifetime／5. Retraining Trigger／6. Explainability Requirements／7. Regulatory Compliance）
│   ├── 10-quality-requirements.md      10.1 Quality Requirements Overview（arc42 v8 官方名；舊名 Quality Tree 已棄用）／10.2 Quality Scenarios（六段）／10.3 E6 — AI Quality Scenarios（Quality Attribute Definitions／Model Freshness／Drift Tolerance／Explainability／Fairness／Robustness／Scenario Format／Cross-Component Scenarios（含 Illustrative Scenario: Cascading Drift）
│   ├── 11-risks-and-technical-debt.md  ※11.1 風險／※11.2 技術債（rev6 自訂子節、官方無）／※11.3 E7 — AI Debt Register（七類：1. Boundary Erosion／2. Entanglement (CACE: Changing Anything Changes Everything)／3. Hidden Feedback Loops／4. Data Dependency Debt／5. Pipeline Debt／6. Configuration Debt／7. Model Staleness／Register Entry Format 九欄／Debt Summary Dashboard／Review Cadence 改條件觸發）
│   ├── 12-glossary.md                  系統術語＋RAD-AI AI 術語（標「保留」）；流程術語住 RULES.md 名詞段
│   ├── 13-operational-ai-view.md       E8 新節：Monitoring／Retraining Policy／Deployment Strategy／Rollback Policy（reference 四必備）＋Incident Response（模板）
│   └── decisions/ADR-00001-<slug>.md        一決策一檔；frontmatter 必填 id／title／date／status＋慣例 supersedes／superseded_by／provenance／tags；選填 rev5_id／rad_ai
├── docs/c4/
│   ├── C4-L1-system-context.md         人寫 Mermaid（同圖亦引於 03 §3.2）
│   ├── C4-L2-container.md              人寫 Mermaid；節點 ⊇ compose 服務名（GT-10 腿、自 compose 機器判）；stereotype 標註直接畫在此圖
│   ├── C4-E1-ai-component-stereotypes.md   標註規則＋標註表（Stereotype Definitions／Mermaid Conventions／Annotation Guidelines 補齊 Feature Store／Template 段）；不畫第二張圖
│   ├── C4-E2-data-lineage-overlay.md   overlay 規則＋表（Data Source Inventory／Lineage Diagram（疊加於 L2）／Lineage Details／Freshness Requirements／Privacy Flow／Schema Registry）
│   └── C4-E3-non-determinism-boundary.md   overlay 規則＋表（Boundary Overview／Boundary Interfaces／Confidence Thresholds／Degradation Behavior／Propagation Rules／Testing Implications）
├── docs/compliance/
│   ├── annex-iv-checklist.md           Instructions＋23 鍵（AIV-1a…9，附錄 G）＋Summary；欄＝AIV 鍵｜Annex IV 要求原句｜RAD-AI 原列號｜RAD-AI 十類號｜rev6 承載｜Evidence（See `<檔>`, `<具名表>` — …）｜自評
│   └── annex-iv-mapping.md             Annex IV 真實點號 → RAD-AI 十類 → rev6 節；依 tmp/annex-iv-2e-check.md 表二重建
├── docs/process/                       流程層（D16）：E 形制套用於開發流程的 AI 代理，每檔首段「類比張力：」
│   ├── P-E1-boundary.md                Inventory＝主線／implementer／review／fix／CDP agent／三支 hook；Boundary＝人審與機器閘；Four-Part Contract 類比（輸出型＝報告與 diff、信心＝lint 與 review verdict、換版頻率＝規則層版本、fallback＝blocked／done_with_escalation）；Failure Modes＝hook 註冊斷裂→靜默放行、stall、runaway；External AI Dependencies＝Anthropic 託管模型（無 SLA）、upstream opencode.yml
│   ├── P-E2-agent-registry.md          AGT- 名冊：角色×模型×effort×最近換模日×產物進哪道閘；真源＝tools/orchestration/ 的 OPTS 常數（tracked）、generate 產 reference/agents.md
│   ├── P-E3-doc-pipeline.md            brainstorm→spec→tasks→Workflow→review→收刀簿記；Quality Gates 五欄＝lint 與 hook；Feedback Loops＝LESSONS→RULES→prompt
│   ├── P-E4-responsible-agent.md       Human Oversight＝拍板級判準、push／merge 同意閘、review 只讀；Transparency＝events 留痕；Privacy＝secrets 掃描；Fairness／Explainability／Safety＝不適用附理由
│   ├── P-E6-quality-scenarios.md       Robustness＝review 誤報率、lint 恆綠風險、stall 恢復；Drift Tolerance＝docs↔code 漂移閘；Model Freshness＝換模政策；Explainability＝findings 可追溯；Fairness＝不適用附理由；Cross-Component＝規則層改動對多支 agent 的連鎖
│   ├── P-E7-agent-debt.md              agent／編排類坑（嚴口徑 17 條為種子）；九欄；條件觸發覆審
│   ├── P-E8-operations.md              Monitoring＝看門狗存活與保險絲（張力：非漂移偵測）、perf 引信、lint 漂移閘；Retraining Policy＝換模與規則層更新觸發；Deployment＝規則層版本進 prompt 的發布形；Rollback＝治理閘改壞的回退程序；Incident Response＝blocked 升級路徑
│   └── P-C4-E3-materials-boundary.md   三材質即非確定性邊界：Claude 執筆／機器生成／user 拍板；Confidence＝lint 與 review；Degradation＝blocked／escalation；Testing＝harness 六案
├── docs/ops/
│   ├── NOTES.md                        當前意圖
│   ├── BACKLOG.md／BACKLOG-DEFERRED.md 檔頭 next-id（顯式）；條目＝id｜分類 product／governance｜一句話｜觸發條件（必填、須可到期）
│   ├── RULES.md                        規則層（人寫）：RL-0001／規則（命令句、≤2 行）／scope／carrier／source；上限見 D8
│   ├── LESSONS.md                      教訓索引（機器生成、例外註冊）：LL-id｜坑名｜rule_id｜promotion_surface｜檔
│   ├── LESSONS/LL-00001-<slug>.md        故事層；frontmatter 必含 rule_id（或 none 附理由）與 promotion_surface（rules／gate／code／none）
│   ├── RUNBOOK.md                      操作程序（守門面移 generated/GATES.md）
│   ├── reference-src/                  半自動快照來源（schema／accounts 快照、archetype-map、schema-evolution）
│   └── events.jsonl                    事件源；schema 見 §4.3（misc 型補 backlog_add 與 category）
├── docs/generated/
│   ├── STATE.md（帳面統計＋三指標＋數量預算對賬）／MILESTONES.md／DECISIONS-INDEX.md（無 rev5_id 欄）／GATES.md（§4.1）
│   └── reference/                      routes／ports／schema／accounts／screens／perf／tools-cli／agents／rev5-blueprint-map
├── specs/、docs/brainstorms/、docs/reviews/      承襲 rev5 形；rev6 自 000 起新編；史料豁免面
└── tools/
    ├── docsync/                        重寫最小集（§4）
    ├── orchestration/                  編排骨架、harness、_sk_rules 生成器、wf-watchdog（D10；解 rev5 L-087）
    ├── walkthrough-baseline.py         世代 DoD 六步還原的載體
    ├── bootstrap.sh                    幂等創世＋rev5 凍結 SHA 斷言（D17）
    └── 碼面閘（隨子庫刀進場：schema-gate／entity-drift-gate／wire-schema／fork-delta-lint／route-artifact-gate／view-render-guard／seed-view-gate／rust-fmt-gate）
```

命名規則：節檔＝`NN-<arc42 英文節名>.md`，frontmatter 帶 `section: N`、`summary:`、`rad_ai: [E1]`、`rad_ai_map:`（rev6 中文子節名 ↔ RAD-AI 原子節名的對照鍵，D15）、`process: P-E1-boundary.md`；E 子節標題含 `E<j>` 字面、子節名一律中文改寫；C4 檔＝`C4-L<n>-*`／`C4-E<k>-*`；流程層檔＝`P-E<k>-*`。對照總表（§3.3）與 `ARCHITECTURE.md` 索引由 generate 自 frontmatter 產出。本檔樹中的英文子節名為出處引用，rev6 文件正文不逐字使用。

### 3.3 RAD-AI 項目對照總表（導入的驗收清單）

系統層＝rev6 重寫的 admin 後台本體（目前無 AI 元件、隨刀填入）；流程層＝`docs/process/`。

| RAD-AI 項目 | rev6 系統層落點 | rev6 流程層落點 | 採用階段 | 驗收列 |
|---|---|---|---|---|
| E1 AI Boundary Delineation | `03-context-and-scope.md` §3.3：「目前無 AI 元件（截至日期）」＋指針 | `docs/process/P-E1-boundary.md` | Stage 1 | 是 |
| E2 Model Registry View | `05-building-block-view.md` §5.4：同上 | `P-E2-agent-registry.md`＋`reference/agents.md` | Stage 1 | 是 |
| E3 Data Pipeline View | `06-runtime-view.md` 末子節：同上（稽核資料流作為系統資料流列於 6.n 情境，非 E3） | `P-E3-doc-pipeline.md` | Stage 3 | 是 |
| E4 Responsible AI Concepts | `08-crosscutting-concepts.md` §8.5：同上 | `P-E4-responsible-agent.md` | Stage 3 | 是 |
| E5 AI-ADR | `09-architecture-decisions.md` §9.1 形制與對映表；`decisions/` 內 AI 決策 body 用 E5 形 | 模型分派、effort、編排形制的決策走 E5 形 | Stage 2 | 是 |
| E6 AI Quality Scenarios | `10-quality-requirements.md` §10.3：同上；10.1／10.2 為系統品質（憲法 §I.7 七島 fail-* 方向、節流、TTL 各成一情境，隨刀填） | `P-E6-quality-scenarios.md` | Stage 2 | 是 |
| E7 AI Debt Register | `11-risks-and-technical-debt.md` §11.3：七類標「目前無」、Configuration Debt 可填 | `P-E7-agent-debt.md` | Stage 3 | 是 |
| E8 Operational AI View | `13-operational-ai-view.md`：系統層「目前無」＋指針 | `P-E8-operations.md` | Stage 3 | 是 |
| C4-E1 stereotypes | `c4/C4-E1-*.md` 標註規則；標註畫在 C4-L2 | agent 角色在 P-E2 表以 stereotype 欄標註 | Stage 1 | 是 |
| C4-E2 lineage overlay | `c4/C4-E2-*.md`：**Privacy Flow 為真內容**（稽核表 attempted_user_name 原文、real_ip NOT NULL、保留期「無（承 rev5 B-016）」） | 文件血緣鏈（brainstorm→spec→ADR→events→generated） | Stage 3 | 是 |
| C4-E3 non-determinism boundary | `c4/C4-E3-*.md`：系統本體全確定性一句 | `P-C4-E3-materials-boundary.md` | Stage 2 | 是 |
| Annex IV checklist 23 鍵 | `compliance/annex-iv-checklist.md`：逐鍵「不適用（系統無 AI 元件）」附理由 | 不套用（法規射程為系統） | Compliance | 是 |
| Annex IV 十類映射 | `compliance/annex-iv-mapping.md` | — | Compliance | 是 |
| 三階段採用路徑 | 本檔 §5 波次與各刀 brainstorm | — | — | 否（非驗收列） |
| Glossary | `12-glossary.md`＋RULES.md 名詞段 | — | — | 否（非驗收列） |

### 3.4 形制規則（機器守＝GT-10）

適用面：arc42 的每個 E 子節與 §13、`docs/c4/` 五檔、`docs/compliance/` 兩檔、`docs/process/` 每檔。

1. **系統層段**：有 AI 元件則照 reference `####` 填；無則恰一句「目前無 AI 元件（截至 <日期>）；本層隨 AI 功能刀填入」＋一行指針到對應 process 檔。
2. **流程層檔**：照同一組子項填；每個子項首句必含「類比張力：」字面，標明哪裡對得上、哪裡是硬套（已認定的三處：CACE ↔ L-032 症狀相似機制無關；wf-watchdog 守存活非漂移；E4 三節對 agent 不適用）。
3. **佔位三腿零殘留**：`*[`、`_{5,}`、未勾 `- [ ]`；另掃裸 `[Xxx]` 佔位（方括號後不接 `(`）。判準以拆分構造寫，避免規則定義文自撞。
4. **子項名冊齊全**：系統層非「目前無」句時，子項集 ⊇ reference `####`；compliance 檔 23 鍵齊、每鍵 Evidence 欄非佔位且所引檔與具名表實存。
5. **圖表對賬**：圖內節點名 ⊆ 同檔表格列；C4-L2 節點 ⊇ compose 服務名（自 compose 三檔機器判）。
6. **波次標記**：`TODO(波 N)` 為合法暫留形，波 N 出口＝該標記歸零。

### 3.5 ADR 制度

- frontmatter：必填 id／title／date／status；慣例欄 supersedes／superseded_by／provenance／tags；**選填** `rev5_id`（承襲宣告時引用）與 `rad_ai`（E5 形）。DECISIONS-INDEX 不設 `rev5_id` 欄（避免死欄）。accepted 後 body 不可變（含 superseded 狀態，修 rev5 缺口）、supersede 對稱、索引 `feature` 欄由 events 反查、反查不到印「輕量軌」。
- **body 節形**：背景／決策驅動因子／考慮過的替代案／決定／後果／翻案觸發器（by-design 與 won't-fix 型必填）。「決策驅動因子」獨立節推翻 RAD4AI-report §3.2 對 rev5 的不採建議，理由＝rev6 無 79 份回溯成本。分工線：ADR 翻案觸發器答「決定何時失效」、BACKLOG 觸發欄答「待辦何時該做」。
- **基線欄集定案後不再擴充**：形制演進走 body 節。
- **AI-ADR 不另開號空間**：rev6 四碼 id＋`rad_ai: E5`＋標題前綴「AI-ADR」（R1 複驗：RAD-AI 從未要求獨立號空間）。
- **rev5 決策不遷**（D5）：rev6 ADR 自 ADR-00001 起皆為 rev6 自己的決定；需要沿用 rev5 決策時，在該 ADR 的背景段引 `rev5:ADR 00NN`（來源＝`../fork260509-rev6/tmp/rev5-adr-digest.md` 的備用摘要）。同代引用只在 rev6 ADR 間。

### 3.6 規則層與故事層

- `docs/ops/RULES.md`：每條＝`RL-0001｜規則（命令句、無刀名、無行話、≤2 行）｜scope（implementer／review／fix／主線／人）｜carrier（prompt／lint／checklist）｜source（LL-NNNNN 或 ADR-NNNNN，必須存在；允許 rev5:LL／rev5:ADR 形）`。上限＝波 1 實算去重後 ＋25%（D8），並依 scope 各設上限。
- **機器可判的烤入**：`docsync rules emit --scope <s>` 輸出該 scope 規則塊＋末行 `RULES-VERSION: <sha256 前 12>`；編排骨架組裝改為呼叫此命令（不再手維護陣列）；PreToolUse hook 升級為對賬：自 script 抽出規則塊與版本串、比對現算 sha256，不符即擋（純字面斷言只證明有人打了那串字）。
- `LESSONS/LL-NNNNN-*.md`：故事層；frontmatter `rule_id`（指向 RULES 一列或 none 附理由）＋`promotion_surface`（rules／gate／code／none）。索引 `LESSONS.md` 為派生物 ⇒ rev5 Lint26 的「索引↔檔雙向」退場、由 GT-01 承載；非派生腿（檔名↔正文 ID、`rule_id` 指向存在）併入 GT-08；GT-08 反向腿＝每條 RULES 的 `source` 指向存在的 L 或 ADR（RULES 首版即須有實例，否則反向腿空集合）。
- 晉升＝在 RULES.md 加一列；通道容量由條數上限管，不由行數管。rev5 L-006／L-054 這類「家在 script 而非文件」的防法轉為 RULES 一列、carrier=prompt。

### 3.7 rev5 帳本遷入判準（D2 後＝藍本形）

| rev5 產物 | rev6 去處 | 判準與機器面 |
|---|---|---|
| 活書 12 節 | 不搬；rev5 活書＝藍本 | 波 3 產 `reference/rev5-blueprint-map.md`：rev5 每個 `###` 標題 → rev6 節／隨刀 NNN／不承襲附理由；缺一即紅（一次性 migrate-audit）。流程層可直接遷的 as-built（perf 引信、看門狗、hook）進 process 檔 |
| `FORK-DELTA-WIRING.md` | `08-crosscutting-concepts.md` 8.4（軌道規則）；接線 as-built 隨 base-web 各刀重生 | rev5-inline 標記不帶（D2）；rev6 token＝`rev6-inline` |
| 79 份 ADR | **不遷**（D5）；`rev6/tmp/rev5-adr-digest.md` 備用摘要 | rev6 ADR 需要時引 `rev5:ADR 00NN` |
| 87 條 LESSONS | **不遷**（D5）；`rev6/tmp/rev5-rules-digest.md` 備用摘要（約 30 條已晉升規則、命令句形、附 rev5:L 號） | RULES 首版可自摘要挑選、`source` 填 `rev5:L-NNN`；rev6 LESSONS 自 LL-00001 起 |
| BACKLOG 28＋7 | **不遷**（D5）；rev6 BACKLOG 自 BL-00001 起 | 各刀 brainstorm 讀 rev5 同題 spec 與 BACKLOG 時自行決定是否重提 |
| events.jsonl | rev6 新帳；rev5 events 唯讀連結 | 不回填；schema 補欄（§4.3） |
| RUNBOOK | 操作程序→RUNBOOK（隨刀重生）；守門面→GATES.md；效能量測法→P-E8 | 拆家 |
| constitution 1.10.0 | 逐條表見 §3.8 | rev6 1.0.0 |
| `specs/`、`docs/brainstorms/`、`docs/reviews/` | 留 rev5 唯讀史料；各刀 brainstorm 以 rev5 同題 spec 為輸入（重打字消化、不拷貝） | 史料不搬 |
| `docs/ops/reference-src/*.json` | 隨 001 型 schema 刀重 refresh | 半自動材質 |
| `docs/generated/` | 刪除重算 | 機器材質 |

### 3.8 憲法射程（已拍 2026-09-03；逐條表）

| rev5 條 | rev6 去處 | 理由 |
|---|---|---|
| §I.1 base-web 為權威 | 承襲 | 系統事實 |
| §I.2 menu 權限 casbin enforce | 承襲 | 系統事實 |
| §I.3 wire 契約權威序 | 承襲 | 系統事實 |
| §I.4 SDD＋TDD 混合工作流 | 承襲（方向性條款）；程序細節住 RULES／CLAUDE.md | 世代不變的工作法 |
| §I.5 rust-api 全新寫、對前代受控參照 | **改寫為對 rev5 受控參照**（世代 bump）；§IV 第 5 題同批改引 | D2 |
| §I.6 業務表審計欄標準 | 承襲 | 系統事實 |
| §I.7 行為島 invariants | 承襲十島；作為世代 DoD 的每刀驗收（隨刀重新進場確認） | 系統事實 |
| §II 設計拍板凍結 | 承襲（逐條核有無被 rev5 ADR 翻案） | — |
| §III 軌道授權邊界 | 承襲；token 改 `rev6-inline`；基線 SHA＝rev5 同 SHA（D14） | — |
| §IV Compliance Check 九題 | 承襲；第 5 題改引 rev6 §I.5 | — |
| §V.1 凍結權威性（權威鏈） | 承襲並**納入 RULES.md**：constitution ＞ ADR ＞ RULES ＞ 活書家族 ＞ generated | R2-F26 |
| §V.2 Amendment 流程 | 承襲（ADR draft→user 親決→accepted＋改本檔＋bump） | 文件程序條款移 RULES 的「輕量軌」依賴它存在 |
| §V.3 Version 規則 | 承襲；rev6 自 1.0.0 起 | — |
| 新增 | 方向性條款：「AI 代理產物必經人審與機器閘；review agent 只讀；push／merge 需 user 明確同意」 | RAD4AI-report Q11；MAJOR 級反轉閘 |

文件治理**程序**條款（三材質細則、時態、完成即刪、ID 配號、lint 運作模式）移 RULES.md，改動走輕量軌不走 amendment。

---

## 4. 治理工具最小集（重寫、不搬運）

### 4.1 名冊制優先

`generated/GATES.md`：`閘｜守哪條 RULES／ADR｜監測哪一面的漂移｜真源｜掃描面｜觸發時機｜紅時 rc｜Day-1 豁免狀態｜拿掉會壞什麼`。兩層真源：①閘的存在與編號由 `finding(LEVEL,"GT-NN")` 錨形掃源推導（承 rev5 `derive_lint_codes`）；②語意欄由各閘 docstring 內**固定鍵值區塊**（`GATE: id= rule= source= scope= breaks-if-removed=`）抽取；GT-12 斷言「①集合 ⊆ ②區塊集合」，缺區塊即紅。名冊 ↔ pre-commit 檔頭範圍字串 ↔ RUNBOOK 工具表三處同源（承 rev5 Lint22）。

### 4.2 核心 lint（已拍 2026-09-03 照表全收；上限 12＝本表條數，一進一出）

| # | 守什麼 | 承襲 rev5 |
|---|---|---|
| GT-01 | generated 與真源零漂移（缺／多／drift；含例外註冊的索引檔與重算冪等） | Lint01／02 |
| GT-02 | events.jsonl schema、SHA 實證、pin↔worktree HEAD 互證 | Lint03／17／18 |
| GT-03 | 收刀與 review 事件完整性（specs／ADR／merge／report／分流引用存在） | Lint04／05／06 |
| GT-04 | ADR frontmatter 不可變（含 superseded）、supersede 對稱、禁刪除 | Lint08＋修缺口 |
| GT-05 | ID 家族 next-id 唯一單調不回收；跨代裸編號禁（雙 pattern：rev5 三碼須 `rev5:`、rev6 四碼原生）；掃描面含子庫碼面；史料豁免面登記 | Lint09／25／29 |
| GT-06 | 引用健康：連結存在、禁行號引用、禁 deep-link 揮發區內部錨、禁 per-machine 路徑、活書家族時態禁詞 | Lint12／13／14／15／10 |
| GT-07 | 憑證與機密掃描 | Lint16＋secret-value-guard |
| GT-08 | RULES↔LESSONS 對賬：L 檔名↔正文 ID、`rule_id` 指向存在、RULES `source` 指向存在；RULES 條數與 per-scope 上限 | Lint26 非派生腿 |
| GT-09 | 接線與實檔集對賬：README 目錄樹 ↔ tools／deploy／.githooks／.claude 實檔集；直接執行腳本 exec bit；settings.json 三支 hook 註冊存在且被引用 | Lint27／21＋新 |
| GT-10 | 文件形制閘：佔位三腿＋裸佔位、子項名冊 ⊇ reference、compliance 23 鍵 Evidence 實存、圖節點 ⊆ 表格、C4-L2 ⊇ compose 服務、「類比張力：」字面、`TODO(波 N)` 歸零 | 新 |
| GT-11 | bash 面：變數黏字、shebang 白名單；掃描面＝外層 tracked bash 面（含 deploy/） | Lint30 |
| GT-12 | 名冊同源（錨形集合 ⊆ docstring 區塊集合；GATES／pre-commit 檔頭／RUNBOOK 三處相等）＋數量預算（lint 條數、RULES 條數與 per-scope、BACKLOG 開放數）：波 1～5 WARN、波 6 起 ERROR（到期即紅形） | Lint22＋新 |

**橫切要求（每條 G 皆須、不計條數）**：掃描面空集合即紅（承 Lint20 八組具名語料、擴為每條 G 的自證）；非 vacuous 自證（承 ADR 0024：合成正例＋破壞性驗證）。

退役（留 rev5，判準＝以行數／配額為判準者或 rev6 結構上不再需要）：Lint07 行數與章節配額、Lint11 禁入詞典（改由 GT-10 形制閘與 RULES 承載）、Lint19 命令形對賬（工具表改為 GATES 名冊、GT-12 承載）、Lint28 活書 §1 建置狀態對賬（建置狀態由 MILESTONES 生成）。碼面閘（schema-gate、entity-drift-gate、wire-schema、fork-delta-lint、route-artifact-gate、view-render-guard、seed-view-gate、rust-fmt-gate、Lint24 msg key 契約）屬系統面、隨刀進場、不計入。

rev5 Lint01～30 逐條處置：01／02→GT-01；03／17／18→GT-02；04／05／06→GT-03；08→GT-04；09／25／29→GT-05；10／12／13／14／15→GT-06；16→GT-07；26→GT-08；21／27→GT-09；30→GT-11；20／22→GT-12 與橫切要求；24→碼面閘；07／11／19／28→退役；23 不存在；99 meta。

### 4.3 三個治理指標（generate 產、進 STATE.md；資料源／窗口／算式釘死）

| 指標 | 資料源 | 算式與空值 | rev5 基準（同算式回算） | rev6 目標 |
|---|---|---|---|---|
| 治理批對 feature 比 | events：type=misc 且 category=governance 之數／type=feature_close 之數 | 全期累計；feature_close＝0 時輸出「n/a」 | 6.5（52/8；rolling-3 為 8.33） | ≤1 |
| LESSONS 重複率 | L 檔 frontmatter `recurrence_of`（指向既有 L 或 RULES）非空之數／全部 | 全期；零檔時 n/a | 18%（16/87，寬關鍵字） | 0（晉升後再踩＝規則層 bug） |
| BACKLOG 淨流量 | events：Σbacklog_add − Σbacklog_done（**misc 型亦須帶 backlog_add**；feature_close 帶 window 鍵） | rolling 3 個 feature_close 自然窗；不足 3 刀 n/a | events 面 93−126＝−33（實開 164、入流低估 43%，故 rev6 補欄） | ≤0 |

events schema（rev6）：feature_close＝rev5 十一欄＋`window`；misc＝rev5 五欄＋`category`（product／governance）＋`backlog_add`；perf＝rev5 七欄；review、erratum 承襲。

### 4.4 工具形與預算

- package `tools/docsync/`（events／adr／book／rules／references／gates 各一模組）＋`tools/orchestration/`；邏輯行數目標 ≤4,000、測試不計入預算但每條 G 至少一正一反自證；每模組檔頭一行「守哪條 RULES」。

### 4.5 隨遷工具（非治理 lint）

`tools/wf-watchdog.py`（D10）、`tools/walkthrough-baseline.py`（世代 DoD 六步）、`tools/bootstrap.sh`（含 rev5 凍結 SHA 斷言）、`deploy/` 九支（secrets 家族，隨 compose 拓樸）、三支 hook＋settings.json。全部入 GT-09 對賬面。

### 4.6 Day-1 具名豁免（承 rev5 `DAY1_EXEMPTIONS` 四欄制）

波 1 時掃描面必空的閘各登記一筆：鍵→（理由、命中謂詞、到期即紅、登記日）；GATES.md「Day-1 豁免狀態」欄逐筆顯示；波次出口判準＝lint 全綠**且**未解除的豁免逐筆有解除謂詞。

---

## 5. 啟動波次

| 波 | 內容 | 產物 | 出口判準 |
|---|---|---|---|
| 0 | 本啟動書拍板（D1～D17、§3.8、§4.2） | v1.0 定稿（2026-09-03）、交接包投放 `../fork260509-rev6/tmp/`、rev6 session 搬進 `docs/brainstorms/000-*.md` | 已完成 |
| 1 | workspace 創世：`../fork260509-rev6/` 內 git init＋clone 兩源倉＋worktree 兩子庫＋.gitmodules 手寫＋.gitignore／.dockerignore 承 rev5（D17）、埠 3xxxx compose 三檔（D12）、bootstrap 含 rev5 凍結 SHA 斷言、自 rev5 拷貝三支 hook＋settings.json＋wf-watchdog＋編排骨架入 `tools/orchestration/`（D10）、憲法 1.0.0（§3.8）、CLAUDE.md、RULES.md 首版（rev5 29＋1 條晉升規則＋8 條 Pitfall 去重實算→定上限）、`rules emit`、核心 GT-01～GT-12＋Day-1 豁免登記、GATES 名冊、埠配號 ADR | 空骨架可 commit | lint 全綠且豁免逐筆有解除謂詞；GT-12 首值在預算內 |
| 2 | 骨架：arc42 12 節檔（官方子節、E 子節取 reference ####、E5 9.1）＋§13＋ARCHITECTURE.md 索引（例外註冊）＋C4 五檔＋compliance 兩檔（23 鍵）＋process 九檔骨架＋ops 帳本空檔；frontmatter 帶 rad_ai／process | 對照總表由 generate 產出 | GT-10 零佔位；每個流程層檔非空或 `TODO(波 3)` |
| 3 | 流程層填實（P-E1～E8、P-C4-E3，每子項「類比張力：」）；系統層各節骨架＋「目前無」句＋指針；`reference/rev5-blueprint-map.md`（rev5 活書 ### 與 ADR 逐項去處）；C4-L1／L2 首版（自 compose） | 十二節無空節（骨架＋指針） | `TODO(波 3)` 歸零；blueprint-map 零缺 |
| 4 | RAD-AI 23 筆取捨 ADR；埠配號 ADR；RULES 首版定稿（自 `tmp/rev5-rules-digest.md` 挑選＋RAD-AI 八條 Pitfall）；compliance 兩檔填「不適用」列；四本帳自零起（D5） | DECISIONS-INDEX 首批 | GT-04／GT-05／GT-08 全綠 |
| 5 | 文件創世驗收：addressability 自評、三指標首值或 n/a、DoD A 六條逐條、tmp-clean | DoD A 打勾 | §0.3 A |
| 6～ | 刀（系統重寫；刀序與範圍由首刀 brainstorm 定、D13）；每刀走世代 DoD B | — | §0.3 B |

波 1 起即在 `../fork260509-rev6/` 開新 session 執行（D10）；首顆 commit＝守門五件；波 1 末 rev6 正式 CLAUDE.md／RULES／hook 取代過渡版。rev5 session 只負責交接包投放，之後不再開 rev5 session 寫入。

---

## 6. 一次性遷移的 Risk／Guard／Rollback

| 風險 | Guard | Rollback |
|---|---|---|
| 兩代並存期間文件分岔 | rev5 remote 分支保護＋NOTES 凍結宣告；rev6 bootstrap 斷言 rev5 三處 HEAD＝凍結 SHA；源倉不共用（D17） | rev5 原封即回滾點 |
| 重寫期 rev5 對照 stack 不可用 | rev5 stack 常駐 2xxxx、rev6 3xxxx（D12）；走查基準六步（walkthrough-baseline） | 重起 rev5 stack |
| 藍本內容遺漏 | `rev5-blueprint-map` 一次性 migrate-audit 零缺；rev5 兩份備用摘要在 rev6/tmp | 補列 |
| 工具重寫期間零守門或恆綠 | 波 1 先落 GT-01～GT-12＋Day-1 豁免；波次出口綁「全綠且豁免有解除謂詞」 | 停在波 1 |
| 碼制重編破壞跨代引用 | GT-05 雙 pattern＋`rev5:` 前綴；史料豁免面登記 | 對照表可逆 |
| RAD-AI 模板不一致或 upstream 變動 | 附錄 A 取捨 ADR；README 一句記對照 HEAD `afdd36d`（D15） | 改 ADR、重生成 |
| E 子節空表或流程層硬套 | §3.4 形制＋GT-10（含「類比張力：」字面） | 刪節重寫 |
| 數量預算重演放寬螺旋 | 超限只擋新增、不可調數字、一進一出或走 ADR；波 1～5 WARN、波 6 起 ERROR | 調值走 ADR |
| 授權瑕疵 | 不複製實質部分：全部中文改寫、README 一句來源（D15） | 補改寫 |

---

## 7. 驗收：addressability 自評（形）

| RAD-AI 項目 | rev6 落點 | 系統層分數 | 流程層分數 | 子項分數（若逐子節評） | 證據（See `<檔>`, `<表>` — 記了什麼） |
|---|---|---|---|---|---|
| E1 | `03-*.md` §3.3／`P-E1-*.md` | 不適用（無 AI 元件） | 0／1／2 之一 | … | … |
| AIV-1a … AIV-9 | `compliance/annex-iv-checklist.md` | 不適用 | — | — | … |

量表 0／1／2 逐字承襲 RAD-AI；「不適用」為第四值、獨立於 0、必附理由（附錄 A F24）。

---

## 附錄 A：RAD-AI 23 筆內部不一致的 rev6 取捨（D3；加「採哪份」欄）

| A1 | 不一致 | rev6 取捨 | 採哪份 |
|---|---|---|---|
| F01 | E4 五類：documentation 說 Safety、模板是 Transparency | 取聯集六節 | 聯集 |
| F02 | E4 concern matrix 模板與範例零命中 | 依 reference 建矩陣 | reference |
| F03 | E1 契約四段 vs C4-E3 三屬性互斥 | E1 四段；C4-E3 三屬性；互相指針、不合併 | 各自 reference |
| F04 | E7 債類五 vs 七 | 七類 | reference |
| F05 | E7 欄 Estimated Effort 模板缺 | 九欄 | reference |
| F06 | E7 ID 前綴與 Status 值域兩套 | ID 分類前綴；Status 四值 | 模板／reference |
| F07 | E2 Inventory 六欄 vs 八欄 | 八欄 | reference |
| F08 | E2 Versioning／Baselines 欄名兩套 | reference 欄名 | reference |
| F09 | E5 七欄 vs 模板五個 #### | 模板五子節＋對映表寫在 §9.1 | 模板＋對映 |
| F10 | E3 quality gate 欄名 | 五欄（Gate ID／Location／Check Type／Threshold／Action on Failure） | reference |
| F11 | E6 六段 vs 四段 | 六段 | 模板＝reference |
| F12 | C4-E1 Annotation Guidelines 漏 Feature Store | 補齊五個 | 補 |
| F13～F16 | 範例層錯誤 | 不採範例 | — |
| F17 | E8 子節數 | reference 四必備＋模板 Incident Response | 兩者 |
| F18 | C4-E2 兩案子節不齊 | 六子節 | 模板 |
| F19／F20 | Netflix 覆蓋數互斥、README 自述不符 | 不引用 | — |
| F21 | 採用順序兩套 | adoption-guide 三階段 | adoption-guide |
| F22／F23 | 範例排版與多欄 | 模板 | 模板 |
| F24（新） | 量表只有 0／1／2 | rev6 加第四值「不適用」附理由 | 刻意偏離 |

## 附錄 B：RAD-AI repo 全部項目的 rev6 處置

| RAD-AI repo 項目 | rev6 處置 | 去處 |
|---|---|---|
| LICENSE（MIT、© 2026 Oliver Larsen） | 不複製實質部分（全部中文改寫）；README 一句參考來源（D15） | README |
| README.md（repo 根） | 參考；結構自述不符（A1-F20）不引用 | — |
| templates/arc42-extensions 8 檔 | 導入形制：子項依 reference ####，中文改寫、不逐字 | §3.2 |
| templates/c4-extensions 3 檔 | 導入：標註規則＋表 | docs/c4/ |
| templates/compliance-checklist.md | 導入：24 列 | docs/compliance/ |
| templates/README.md | 參考（用法三步內化為 §3.2） | — |
| documentation/README.md | 參考 | — |
| documentation/framework-overview.md | 參考；Key Results 數字不引用 | §2 |
| documentation/arc42-extensions-reference.md | 導入為預設仲裁者（D3） | E 子節、附錄 A |
| documentation/c4-extensions-reference.md | 導入為預設仲裁者；overlay 定位（R1-F05） | docs/c4/ |
| documentation/adoption-guide.md §1～§3 | 導入：採用階段欄與波次 | §3.3、§5 |
| adoption-guide §4 Compliance-Driven Adoption | 條件導入（AI 功能進場時） | annex-iv-mapping |
| adoption-guide §5 Team Roles | 轉譯：單人＋agent，映到 P-E2 名冊 | P-E2 |
| adoption-guide §6 Integration with Existing Tools | 部分導入：Mermaid；Structurizr／MLflow／DVC 不適用記一句 | P-E2 |
| adoption-guide §7 Templates、§8 Common Pitfalls | 導入：Pitfall 2／5／7 為 D1 與 §3.4 依據；八條進 RULES 候選 | RULES.md |
| documentation/eu-ai-act-compliance-guide.md | 導入十類映射（節號依 annex-iv-2e-check 修正）；量表作自評 | compliance、§7 |
| documentation/glossary.md | 導入：AI 術語進 12-glossary（標保留）；流程術語進 RULES 名詞段 | — |
| documentation/research-background.md | 參考 | — |
| documentation/evaluation-results.md | 參考；數字不引用 | — |
| documentation/case-studies 3 檔 | 參考、不導入 | — |
| evaluation/practitioner_scoring_sheet v1／v2 | 導入形制：§7 自評表格式 | §7 |
| examples/smart-urban-mobility | 不採（內部矛盾） | — |
| comparative_analysis 兩案 | 不採（與論文矛盾） | — |
| 論文 G1～G5、RC1～RC4 | 參考：G1～G5 進 01 需求概覽「本框架要解的缺口」段 | 01 |

## 附錄 C：完整性對賬（機器產出；射程限定）

對賬腳本＝`tmp/rev6-coverage-audit.py`（v2），結果＝`tmp/rev6-coverage.tsv`。**射程**：只驗本啟動書是否逐項提及與定位（三態 ✓／✗／⊘＝明文不採），**不驗 rev6 產物**；產物層對賬＝DoD A 與波 2／3 出口。掃描面：A rev5 文件家族；B RAD-AI reference `####` ∪ 模板 `##` ∪ checklist 22 列；C arc42 官方子節（英文原名、v8）；D rev5 Lint01～30 逐條處置；E RAD-AI repo 頂層項目（含 LICENSE、兩份 README）；命中限縮在 §3.2 樹、§3.3 表、附錄 A／B 儲存格內。

## 附錄 D：未決與待查

- rev6 workspace 實體路徑＝`../fork260509-rev6/`（已建、空）；remote（三條長名分支的 origin）待定。
- RULES 條數上限的實算（波 1 首件）。
- upstream 回報（D11）另題。

## 附錄 E：編號家族的 rev6 處置（G05 名冊真源；D4 拍板 2026-09-03）

| 家族 | rev5 形 | rev6 形 | 控制者 | 跨代引用 |
|---|---|---|---|---|
| BACKLOG | `B-164` | **`BL-00001`**（五碼） | rev6 | `rev5:B-NNN` |
| LESSONS | `L-087` | **`LL-00001`**（五碼） | rev6 | `rev5:L-NNN` |
| ADR | `0079-slug.md`／`ADR 0079` | **`ADR-00001-slug.md`／`ADR-00001`**（五碼） | rev6 | `rev5:ADR 00NN` |
| 規則層 | （無） | **`RL-0001`**（四碼） | rev6 | — |
| 閘碼 | `Lint01`～`Lint30` | **`GT-01`～`GT-12`** | rev6 | `rev5:LintNN` |
| migration 短號 | `m001` | **`m0001`**（四碼） | rev6 | `rev5:m001` |
| agent 名冊 | （無） | `AGT-001` | rev6 | — |
| 流程層檔 | （無） | `P-E1`～`P-E8`、`P-C4-E3` | rev6（對應 RAD-AI 編號） | — |
| Annex IV 列鍵 | （無） | `AIV-<點><子項>`（23 鍵） | rev6（對應法規） | — |
| RAD-AI 表內 ID | （無） | `MDL-`／`PL-`／`DS-`／`QS-`／`AIDB-`／`QG-` | RAD-AI 慣例 | — |
| 刀名 | `008-slug` | `001-slug`（三碼、自 001 重起） | spec-kit `create_new_feature_branch.py` | `rev5:008-slug`（同形碰撞、必前綴） |
| 需求／成功指標 | `FR-050`／`SC-010` | `FR-001`／`SC-001`（刀內） | spec-kit spec-template | 刀內語意、不跨代引用 |
| 任務號 | `T037` | `T001`（刀內） | spec-kit tasks-template | 同上 |
| user story | `US1` | `US1`（刀內） | spec-kit tasks-template | 同上 |
| 執行單元 | `008 U2` | `001 U2`（刀內） | rev6 編排紀律（承 rev5） | 同上 |
| findings | `F001-1` | `F001-1`（報告內） | rev6 review 報告形（承 rev5） | 同上 |
| research 條目 | `research R1` | **不預先定形**（首刀 spec 需要時再定） | rev6 首刀 | G05 登記 rev5 字形、偵測漏 `rev5:` 前綴的引用 |
| review 報告 | `20260811-003-slug-final.md` | `YYYYMMDD-<刀名>-<scope>.md` | rev6 | — |
| 契約條款號／契約節號 | `§P1.1`／`§P1` | **不預先定形**（首刀需要時再定；rev4 契約遺形、rev5 原生零用） | rev6 首刀 | G05 登記 rev5 字形；引 rev4 者寫完整 `rev4:P1.1` |
| contracts 守衛號 | `contracts G4`／`§G4` | **不預先定形**（rev4 遺形、rev5 原生 1 處） | rev6 首刀 | G05 登記 rev5 字形；`rev4:contracts G4` |
| scan-gates 節號 | `scan-gates §S3` | **不預先定形**（rev4 遺形、rev5 原生零用） | rev6 首刀 | G05 登記 rev5 字形；`rev4:scan-gates §S3` |
| 裸刀號 | `001` | **禁** | — | — |
| events | 無編號 | 無編號（type＋date；erratum 以 type＋date＋欄定位） | rev6 | — |

G05 雙 pattern：rev5 三／四碼形（`B-\d{3}`、`L-\d{3}`、`ADR 0\d{3}`、`Lint\d{2}`、`\d{3}-slug`）在 rev6 現在式文件面一律須帶 `rev5:` 前綴；rev6 新形原生。史料豁免面（`docs/brainstorms/`、`specs/`）登記於名冊。

## 附錄 F：對抗式覆核處置表（R1 22 條、R2 30 條）

| id | 處置 | 落點 |
|---|---|---|
| R1-F01 | 採 | §3.2 E 子節改 reference ####（含 Cards、契約、Cross-Component） |
| R1-F02／R2-F08 | 採 | §3.4 佔位三腿＋裸佔位；DoD A1 Evidence 實存 |
| R1-F03 | 採（b 形） | §3.1 例外註冊三件套 |
| R1-F04 | 採 | §3.2 09 加 9.1 E5 |
| R1-F05 | 採 | C4-E 三檔＝標註規則＋表；C4-L2 人寫；GT-10 腿 |
| R1-F06／R2-F06 | 採 | §4.3 資料源／窗口／算式／空值；misc 補欄 |
| R1-F07 | 採 | 流程層落 process（D16） |
| R1-F08／R2-F11 | 採 | 骨架入 `tools/orchestration/`（波 1、D10） |
| R1-F09 | 採 | D9 24 列、鍵空間、逐列對應 |
| R1-F10 | 採 | §3.5 選填欄、承襲宣告 ADR、同代引用 |
| R1-F11／R2-F30 | 採 | 附錄 C 射程限定；腳本 v2 |
| R1-F12 | 採 | §3.2 樹補齊 |
| R1-F13 | 採 | GT-10 承載 D7 配套 |
| R1-F14／R2-F27 | 採 | 口徑 29 |
| R1-F15 | 採 | 橫切要求措辭 |
| R1-F16 | 採 | 五欄 |
| R1-F17 | 採 | D6 理由改引 |
| R1-F18 | 採 | D3 改述＋附錄 A 採哪份欄 |
| R1-F19 | 採 | 官方子節名；11.x 標 ※ |
| R1-F20 | 採 | P-E6 五屬性齊 |
| R1-F21 | 採 | 附錄 C 數字改以 tsv 為準 |
| R1-F22 | 採（保留節、標翻案理由） | §3.5 |
| R1 遺漏 1～6 | 採（授權面依 D15 改為全中文改寫＋README 一句） | D15／類比張力字面／非驗收列／blueprint-map／compliance 形制 |
| R2-F01 | 採（①形） | D16 process/ |
| R2-F02 | 採 | §3.8 逐條表 |
| R2-F03 | 採 | Lint10／14／15→GT-06 |
| R2-F04 | 採 | 橫切要求；Lint30→GT-11 全掃描面 |
| R2-F05 | 採 | Lint22→GT-12 |
| R2-F07 | 採 | §4.6 Day-1 豁免 |
| R2-F09 | 採 | §3.7 兩腿過濾；§2-7 成因改寫；governance-review 勘誤 |
| R2-F10 | 採（D2 後改承襲宣告） | §3.5 |
| R2-F12 | 採 | D8 兩類分立＋形制 |
| R2-F13 | 採 | 上限實算＋per-scope |
| R2-F14 | 採 | 三分流 |
| R2-F15 | 採 | §4.5 |
| R2-F16 | 採 | §4.1 兩層真源 |
| R2-F17 | 採 | D4 雙 pattern＋附錄 E |
| R2-F18 | 採 | GT-12 WARN→ERROR |
| R2-F19 | 採 | migrate-audit 非常駐閘 |
| R2-F20 | 採 | §3.6 Lint26 退場說明 |
| R2-F21 | 採 | rules emit＋版本 sha＋hook 對賬 |
| R2-F22 | 採（②形） | DoD A6 史料豁免 |
| R2-F23 | 採 | D12 已拍 |
| R2-F24 | 採 | §3.6 |
| R2-F25 | 採 | 波 2 出口 |
| R2-F26 | 採 | §3.1 權威鏈 |
| R2-F28 | 採 | §2 口徑 |
| R2-F29 | 採 | §7 表形；附錄 A F24 |
| R2 遺漏 1～8 | 採 | D10／D17／D12／rev6-inline／§4.6／§4.3／§4.4 測試預算 |

## 附錄 G：Annex IV 檢核表 23 鍵（列鍵＝真實 Annex IV 點號與子項；RAD-AI 原列號為第二欄）

來源：`tmp/annex-iv-2e-check.md`（三源逐字一致）；RAD-AI 22 列原句見 `tmp/RAD-AI/templates/compliance-checklist.md`，其九節為 1. General Description of the AI System／2. Detailed Description of System Elements／3. Data and Data Governance／4. Training Methodology and Techniques／5. Risk Assessment and Management／6. Lifecycle Changes／7. Performance and Accuracy／8. Human Oversight／9. Post-Market Monitoring（RAD-AI 自訂節號、與 Annex IV 點號無關，故 rev6 不以它為鍵）。標「待核」者於波 2 對官方原文逐鍵確認；RAD-AI 無對應的鍵由 rev6 補列、標「RAD-AI 無對應」。

| AIV 鍵 | Annex IV 要求（摘） | RAD-AI 原列號 |
|---|---|---|
| **AIV-1a** | 1(a) intended purpose、provider 名稱、版本與前版關係 | **1.1**、**1.2** |
| **AIV-1b** | 1(b) 與外部軟硬體（含其他 AI 系統）的互動 | **1.3** |
| **AIV-1c** | 1(c) 相關軟韌體版本與版本更新要求 | **1.4** |
| **AIV-1d** | 1(d) 上市或投入服務的所有形式（套件、下載、API） | —（RAD-AI 無對應、rev6 補） |
| **AIV-1e** | 1(e) 預期運行的硬體 | —（rev6 補） |
| **AIV-1f** | 1(f) 作為產品元件時的照片與內部佈局 | —（rev6 補） |
| **AIV-1g** | 1(g) 提供給 deployer 的使用者介面基本描述 | —（rev6 補） |
| **AIV-1h** | 1(h) 使用說明（instructions for use） | —（rev6 補） |
| **AIV-2a** | 2(a) 開發方法與步驟，含預訓練系統或第三方工具的使用 | **2.1** |
| **AIV-2b** | 2(b) 設計規格：一般邏輯、演算法、關鍵設計選擇與假設、取捨 | **2.2**（設計規格半邊）、**3.4**（假設、待核）、**4.2**（設計選擇、待核） |
| **AIV-2c** | 2(c) 系統架構如何組成與整合；開發／訓練／測試／驗證的運算資源 | **2.2**（架構半邊）、**2.3** |
| **AIV-2d** | 2(d) 資料需求：datasheets 描述訓練方法與技術、訓練資料集、來源、標註、清理 | **3.1**、**3.2**、**3.3**、**4.1** |
| **AIV-2e** | 2(e) 依 Art. 14 的 human oversight 措施評估；輸出可解釋的技術措施（Art. 13(3)(d)） | **8.1**、**8.2** |
| **AIV-2f** | 2(f) 預定變更（pre-determined changes）與持續合規的技術方案 | —（rev6 補） |
| **AIV-2g** | 2(g) 驗證與測試程序、accuracy／robustness 指標、測試日誌與報告 | **7.1**（部分、待核） |
| **AIV-2h** | 2(h) cybersecurity measures put in place | —（RAD-AI 無對應、rev6 補） |
| **AIV-3** | 3. 監測、運作與控制：能力與限制（含 accuracy 程度）、可預見非預期結果與風險來源、human oversight 措施、輸入資料規格（子項待波 2 對官方原文細分） | **7.2**、**5.1**（風險來源半邊）、**8.2**（半邊） |
| **AIV-4** | 4. performance metrics 的適切性 | **7.1** |
| **AIV-5** | 5. 依 Art. 9 的風險管理系統 | **5.1**、**5.2** |
| **AIV-6** | 6. 生命週期中的相關變更 | **6.1** |
| **AIV-7** | 7. 適用的 harmonised standards 清單（或替代方案） | —（RAD-AI 無對應；文件框架不承載、屬合規程序） |
| **AIV-8** | 8. 依 Art. 47 的 EU declaration of conformity 副本 | —（同上） |
| **AIV-9** | 9. 依 Art. 72 的 post-market 評估系統與監測計畫 | **9.1**、**9.2**（logging 半邊、待核） |

RAD-AI 22 列 → AIV 鍵對映（反向查詢）：1.1→1a｜1.2→1a｜1.3→1b｜1.4→1c｜2.1→2a｜2.2→2b＋2c｜2.3→2c｜3.1～3.3→2d｜3.4→2b／2d（待核）｜4.1→2d｜4.2→2b／2d（待核）｜5.1→5＋3｜5.2→5｜6.1→6｜7.1→4＋2g｜7.2→3｜8.1→2e｜8.2→2e＋3｜9.1→9｜9.2→9（待核）。

