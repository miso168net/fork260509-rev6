# 波 2 活書骨架實作計畫（arc42 13 檔＋索引、C4 五檔、compliance 兩檔、process 八檔、ops 帳本、生成器三支）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把啟動書 §3.2 的活書骨架落成 tracked 檔，形制對得上 GT-10 八腿（第八腿＝本波加、Q4）；三個例外註冊的生成物（`docs/arc42/ARCHITECTURE.md`、`docs/ops/LESSONS.md`、`docs/generated/RAD-AI-MAP.md`）由 generate 產出；ops 帳本三檔建檔；Day-1 豁免解除四筆；波 2 出口＝`python3 tools/docsync lint` 零 ERROR、`TODO(波 3)` 為唯一合法殘留、波標記 bump 3。

**Architecture:** 活書家族（arc42／c4／compliance／process）每檔 frontmatter 是機器讀的真源：`section`／`summary` 餵 ARCHITECTURE.md 索引，`rad_ai`／`rad_ai_stage`／`rad_ai_map` 餵 RAD-AI 對照總表（子節填實計數）與 GT-10 子項名冊腿（鍵集＋值↔標題）。系統層（arc42 E 子節、c4、compliance）本波一律「目前無 AI 元件」句＋指針；流程層（process 八檔）本波只到 `###` 子節骨架、每子節首句「類比張力：TODO(波 3)」。生成器住 `tools/docsync/references.py`、名冊 GENERATED_FILES 7→10。

**Tech Stack:** python 3.12 標準庫（既有 docsync package）；Markdown＋Mermaid（D7）；git。

**Spec:** `docs/brainstorms/000-doc-architecture.md`（§3.1～§3.6、§4.6、§5 波 2 列、附錄 A／E／G）；形制真源＝`tools/docsync/book.py`（E_SUBSECTIONS、AIV_KEYS、RE_PLACEHOLDERS、RE_TODO_WAVE、TENSION、NO_AI_SENTENCE、RE_NODE）；rev5 藍本（唯讀）＝`../fork260509-rev5/docs/ops/RUNBOOK.md`、`docs/ops/BACKLOG.md`、`docs/ops/LESSONS.md`。

---

## 0. 本 brainstorm 的拍板與判斷

### 0.1 user 拍板（2026-09-03）

| # | 題 | 拍板 | 理由一句 |
|---|---|---|---|
| Q1 | LESSONS 索引 next-id 住哪 | **A：索引全生成、next-id＝`LESSONS/LL-*.md` 檔集最大號＋1、由 generate 寫進索引檔頭** | 零人工計數器、零雙向對賬；「永不回收」靠 GT-05 既有單調腿（現 next ＜ HEAD next 即紅、不跑 generate 則 GT-01 漂移紅）、不加新腿；立 ADR-00005 記載 |
| Q2 | GT-10 逼出的三項提前 | **A：照閘做、閘不放寬**——波 2 直接填 compliance 23 鍵「不適用：…」、C4-L1／L2 首版自 compose 畫齊 17 節點、arc42 E 子節「目前無」句＋指針寫齊 | 放寬閘＝調規＋例外形、波 2 出口「GT-10 零佔位」意義變弱；三項皆一句話級成本 |
| Q3（grill） | RAD-AI-MAP「子項」欄語意 | **A：填實計數、兩層兩欄**——「系統層子節」「流程層子節」各 `已填實/N`；已填實＝該檔 `###` 標題 ∈ map 值且子節正文零 `TODO(波 k)`；系統層「目前無」時顯示「目前無」 | 鍵集計數恆 N/N 空轉；DoD A1「非佔位」得到機器面 |
| Q4（grill） | map 值↔`###` 標題字面一致誰守 | **A：GT-10 加第八腿**——有 `rad_ai_map` 的檔，每個 map 值必須是同檔某 `###` 標題字面（反向不要求）；缺＝ERROR | Q3 計數靠它認子節；不加閘不加規則、約 6 行＋一正一反測 |
| Q5（grill） | RUNBOOK §15 在波 2 寫到多深 | **B：全指針**——§15 只寫資產一段＋「程序見 `deploy/secrets/README.md`、細節承 rev5:RUNBOOK §15 同節、隨首個機密事件補實」；§15.2／§15.4 只留標題與一句 rev5 指針 | 波 2 是骨架；多數節未在 rev6 實跑、不放未實跑命令 |

### 0.2 主線工程判斷（報備；user 可翻）

1. **對照總表落點**＝`docs/generated/RAD-AI-MAP.md`（與 STATE／GATES 同級的名冊型帳；不入 `reference/`——它是驗收清單不是查表）。欄＝RAD-AI 項目｜系統層檔｜系統層狀態（目前無／填實）｜流程層檔｜子項（n/N）｜採用階段。啟動書 §3.3 的「非驗收列」（三階段採用路徑、Glossary）不可自 frontmatter 推導、不入表；§3.3 仍為設計來源。
2. **ARCHITECTURE.md 索引**欄＝節｜檔（連結＋標題）｜摘要｜掛載 E｜流程層檔。標題唯一家＝各節檔 H1（`# §N 標題`，索引剝 `§N`）；摘要唯一家＝frontmatter `summary`；流程層檔由 `rad_ai` 值 join 推導——**不設 `process:` frontmatter 鍵**（啟動書 §3.2 列了它，但 join 可得＝鏡像；鏡像不存在）。
3. **frontmatter 單一家**：`rad_ai_map`（英文原名→中文子節名）只住**有該組子節標題的檔**——本波＝process 八檔與 c4 E 三檔；arc42 E 檔在「目前無」期間不帶 map（GT-10 見該句即跳過鍵集腿）、AI 功能刀進場時連同子節一起補。`rad_ai_stage` 只住系統層檔（arc42 E 檔／c4 E 檔／compliance）。
4. **RUNBOOK 章節編號承 rev5 §1～§16**：`deploy/secrets/README.md` 與 `docs/ops/NOTES.md` 已以 §7 抬頭／§15／§15.2／§15.4 指向它，重編號＝四處 errata 換零收益。創世期最小章承 rev5 形制宣告（rev5 為 §1／§12／§14／§15）：rev6＝**§1／§7 抬頭／§12／§14**（§15 依 Q5 為資產段＋指針），其餘各章一行「隨對應刀補實文」；走查還原契約＝§9c（CLAUDE.md §7 以節名引）。§7 抬頭的 SECRETS_DIR 取值片段在 T1 實跑一次（無需 docker）才入章。
5. **BACKLOG 兩卷零條目**建檔；NOTES「未決」兩條（remote 時機、`alert_webhook_url` 真值）留 NOTES——它們是 user 待拍的決定、不是可排程工項。
6. **`docs/ops/LESSONS/` 目錄本波不建**（git 不追蹤空目錄）；GT-08.lessons-absent 依啟動書留到首條 LL 落地（本波若踩坑即自然解除）。
7. **process 八檔本波只到骨架**（啟動書 §5 波 3＝流程層填實）：`###` 子節齊全、首句「類比張力：TODO(波 3)」。啟動書 §5 波 2 列寫「process 九檔」、§3.2 樹實列八支（E1～E4、E6～E8、C4-E3）——E5 的流程層＝ADR 用 E5 形（§3.3）、無獨立檔；以樹為準、「九」為計數滑差、不補第九檔。
8. **AIV-3 不細分**：Annex IV 官方點 3 無字母子項（交接包 `tmp/rev5-handoff/annex-iv-2e-check.md` 表一），四個面向（能力與限制含 accuracy 程度／可預見非預期結果與風險來源／human oversight 措施／輸入資料規格）寫入要求欄；AIV_KEYS 23 鍵不動。附錄 G 四列「待核」定案見 §2.5。
9. **Mermaid 形制規則**（對得上 `book.RE_NODE` 與表格首欄對賬）：節點 id 只用 `[A-Za-z0-9_]`（compose 名的 `-` 改 `_`）、label 以雙引號包、**label 字面＝同檔表格首欄字面**、label 內不含 `()[]{}`；不用 `subgraph`；邊上文字用 `-->|文字|`。C4-L2 label＝compose 服務名原字（含 `-`）。
10. **C4-L2 邊的真源**＝compose `depends_on`＋設定檔（`deploy/prometheus/prometheus.yml` scrape、`deploy/grafana-provisioning/datasources/*.yml`、alloy→loki、dev.yml `APP_SMTP_HOST: mailpit`）；埠值不入 C4-L2 表（真表＝`docs/generated/reference/ports.md`）。
11. **GT-05 LL 家族雙計數**（brainstorm 中發現的潛在自撞）：`_family_state` 把索引條目與 `LESSONS/` 檔名都算進 ids，索引若以 `- LL-NNNNN｜` 形列條目＝每條重複配號 ERROR。處置＝生成索引用**表格列**（`| LL-NNNNN | …`，不合 RE_ENTRY）、ids 只來自檔名；加一測斷言「生成索引零 RE_ENTRY 命中、N 檔恰 N 個 id」。RE_ENTRY 的 LL 形保留＝防有人手加條目（GT-01 亦會攔）。
12. **ADR-00005**（accepted；provenance＝本檔 Q1）：三件例外註冊生成物、LL next-id 自檔集推導、RAD-AI-MAP 落點與欄。
13. **分支**＝`000-w2-book-skeleton`（輕量軌）；每 Task 一顆 commit；收單 `merge --no-ff` 需 user 同意、不 push。
14. **名詞段補三詞**（domain-modeling 產出；家＝RULES.md 名詞段、不另建 CONTEXT.md）：**系統層**＝arc42 E 子節、c4、compliance 所述之 rev6 系統本體；**流程層**＝`docs/process/` 所述之開發流程 AI 代理（D16）；**例外註冊**＝住 `docs/generated/` 之外但入 GENERATED_FILES 名冊的生成物（ARCHITECTURE.md、LESSONS.md）。名詞段不入 RULES-VERSION 雜湊（只雜湊規則列、已查 `rules_version`）。
15. **生成序**：ARCHITECTURE.md／RAD-AI-MAP 讀 `ctx.tracked`——新建活書檔一律**先 `git add` 再 `generate`**，否則索引缺列、pre-commit 才發現漂移。
16. **「截至 <日期>」＝該句落地日**、不設定期刷新；事實改變（AI 元件進場）時整句換掉。

### 0.3 波次表縮編紀錄（不改啟動書；波 3／4 brainstorm 以此為準）

| 波 | 啟動書原列 | 本波已吸收 | 剩餘 |
|---|---|---|---|
| 3 | 流程層填實；系統層各節骨架＋「目前無」句＋指針；blueprint-map；C4-L1／L2 首版 | E 子節「目前無」句＋指針；C4-L1／L2 首版（自 compose）；官方子節標題 | 流程層填實（`TODO(波 3)` 歸零）；官方子節內容（自 rev5 藍本消化）；`reference/rev5-blueprint-map.md`；C4-L1／L2 修訂；C4-E 三檔規則與表填實；12 名詞表 |
| 4 | RAD-AI 23 筆取捨 ADR；埠配號 ADR；RULES 首版定稿；compliance 填「不適用」列；四本帳自零起 | compliance 不適用列（本波）；四本帳自零起（本波）；埠配號 ADR＝ADR-00001、RULES 定稿＝ADR-00004（波 1） | RAD-AI 23 筆取捨 ADR（附錄 A 進 ADR） |

---

## Global Constraints

- 語言：一切書面產物 zh-TW；RAD-AI 子節名、欄位、檢核表列文字全部中文改寫、英文原名只出現在 frontmatter `rad_ai_map` 鍵（D15）。
- 面：**活書家族**＝docs/arc42（不含 decisions/）、docs/c4、docs/compliance、docs/process＝GT-10 形制面＋GT-06 時態面；本檔（史料面）不受形制與時態掃描，但 GT-06 連結腿掃全部 tracked *.md——本檔不放指向未建檔的 Markdown 連結（路徑一律反引號）。
- 時態（活書家族）：禁詞 待決／TBD／⏳／已完成／下一步（ERROR）；預告詞 屆時／日後／將由（WARN）；未來式一律改寫成現在式事實或 `TODO(波 3)`。
- 佔位：`*[`、五個以上底線、`- [ ]`、裸 `[Xxx]`（方括號後不接 `(`）四腿零殘留；**`TODO(波 3)` 是本波唯一合法殘留形**（現在波 2；波 3 出口歸零）。
- 前代引用：一律 `rev5:`／`rev4:` 前綴；裸刀名禁（`000-` 家族除外）。
- 每個事實只有一個家：埠只在 `reference/ports.md`；十三機密表只在 `deploy/secrets/README.md`；標題只在 H1；摘要只在 frontmatter。
- frontmatter 只用 `parse_front_matter` 認得的形：頂層 `key: value`、單行清單 `[E1]`、一層巢狀對映（`rad_ai_map:` 空值＋兩空格縮排子鍵）；巢狀鍵不含冒號、不加引號。
- 機器生成檔首行 `<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->`（`common.GENERATED_HEADER`）；名冊 GENERATED_FILES 擴為 10 件；`docs/generated/**` 只可含名冊檔。
- 工具：只用 python 標準庫；`tools/docsync/` 邏輯行 ≤4,000（現 1,872）；閘數恆 12、不加閘；每個新生成器一正一反自證。
- git：分支 `000-w2-book-skeleton`；commit 訊息 zh-TW、含反引號一律 `git commit -F <暫存檔>`；每步後以 `git rev-parse HEAD`／`git status --porcelain` 自證；merge 需 user 同意；不 push。
- 環境：/mnt/d drvfs——跑過 docker bind mount 後同 shell 先重新 `cd`；`set -e` 在工具鏈裡靠不住、以工件自證。
- 單元收尾序（CLAUDE.md §2）：③落帳早於⑤generate；每 Task 末＝新檔 `git add` → `python3 tools/docsync generate` → `git add docs/generated`＋例外註冊兩檔（存在者）→ commit。

---

## 檔案結構

```
docs/ops/BACKLOG.md                       人寫；<!-- next: BL-00001 -->；零條目（T1）
docs/ops/BACKLOG-DEFERRED.md              人寫；無 next-id；零條目（T1）
docs/ops/RUNBOOK.md                       人寫；§1～§16 承 rev5 編號＋§9c；最小章 §1／§7 抬頭／§12／§14；§15 資產段＋指針（T1）
docs/ops/RULES.md                         名詞段 +3 詞（系統層／流程層／例外註冊；T1）
docs/ops/LESSONS.md                       生成（例外註冊）；next-id＋表格索引（T2）
docs/arc42/ARCHITECTURE.md                生成（例外註冊）；13 節索引（T2 產生器、T6 填列）
docs/generated/RAD-AI-MAP.md              生成；RAD-AI 項目對照總表（T2 產生器、T3～T6 逐步填列）
docs/arc42/decisions/ADR-00005-generated-indexes-and-ll-next-id.md   accepted（T2）
tools/docsync/references.py               gen_lessons_index／gen_architecture_index／gen_rad_ai_map；GENERATED_FILES 10 件（T2）
tools/docsync/tests/test_references.py    三生成器正反自證＋名冊 10 件＋LL 零雙計數（T2）
tools/docsync/book.py                     GT-10 第八腿：map 值 ⊆ 同檔 ### 標題（T2）；tests/test_book_form.py 一正一反
tools/docsync/gates.py                    DAY1_EXEMPTIONS 6→2（T1 解除 GT-12.runbook-absent；T2 解除 GT-05.ledgers-absent、GT-06.book-absent；T6 解除 GT-10.doc-skeleton-absent）
docs/process/P-E1-boundary.md … P-E8-operations.md、P-C4-E3-materials-boundary.md   八檔骨架（T3）
docs/c4/C4-L1-system-context.md、C4-L2-container.md、C4-E1-ai-component-stereotypes.md、C4-E2-data-lineage-overlay.md、C4-E3-non-determinism-boundary.md   （T4）
docs/compliance/annex-iv-checklist.md、annex-iv-mapping.md   （T5）
docs/arc42/01-introduction-and-goals.md … 12-glossary.md、13-operational-ai-view.md   十三檔（T6）
README.md                                 docs 行更新＋「想知道 X 看 Y」三列（T1／T2）
CLAUDE.md                                 §4 名冊組成一句、§2「踩坑→LESSONS」措辭（T2）
docs/ops/NOTES.md                         波標記 3＋現況（T7）
docs/ops/events.jsonl                     misc 收單事件（T7）＋perf 事件（隨下一顆）
```

---

## 1. 共用形制（各 Task 引用時以此為準）

### 1.1 frontmatter 鍵

| 鍵 | 值域 | 誰帶 | 誰讀 |
|---|---|---|---|
| `section` | 1～13 | arc42 節檔 | ARCHITECTURE.md 索引（排序、節號） |
| `summary` | 一句（≤60 字、現在式、無禁詞） | arc42 節檔 | ARCHITECTURE.md 索引 |
| `rad_ai` | `[E1]`…`[E8]`、`[C4-E1]`…`[C4-E3]`、`[ANNEX-IV]` | 有掛載的檔（arc42 E 檔、c4 E 檔、compliance 兩檔、process 八檔） | GT-10 鍵集腿；RAD-AI-MAP；ARCHITECTURE.md「掛載 E」 |
| `rad_ai_stage` | `1`／`2`／`3`／`compliance` | 系統層檔（arc42 E 檔、c4 E 檔、compliance） | RAD-AI-MAP「採用階段」 |
| `rad_ai_map` | 一層對映：英文原名→中文子節名（鍵集＝`book.E_SUBSECTIONS[項目]`） | process 八檔、c4 E 三檔（本波）；arc42 E 檔於填實時 | GT-10 鍵集腿＋值↔標題腿；RAD-AI-MAP 兩層「已填實/N」 |

### 1.2 中文子節名對照（`rad_ai_map` 的值＝各檔 `###` 標題字面；D15 改寫）

| 項目 | 英文原名（鍵） → 中文子節名（值） |
|---|---|
| E1 | AI Components Inventory→AI 元件清冊；System Boundary Diagram→系統邊界圖；Four-Part Boundary Contract→四段邊界契約；Failure Modes→失效模式；External AI Dependencies→外部 AI 依賴 |
| E2 | Model Inventory Table→模型清冊表；Per-Model Detail Sections→逐模型明細；Integration with Model Cards→與模型卡的銜接；Integration with Model Registry Tools→與模型登錄工具的銜接 |
| E3 | Pipeline Overview Diagram→管線總覽圖；Pipeline Inventory Table→管線清冊表；Quality Gates→品質閘；Feature Store Documentation→特徵庫記載；Feedback Loops→回饋迴圈；Integration with Data Cards→與資料卡的銜接 |
| E4 | Responsible AI Concern Matrix→負責任 AI 關注矩陣；Fairness→公平；Explainability→可解釋；Human Oversight→人類監督；Transparency→透明；Privacy→隱私；Safety→安全 |
| E5 | Model Alternatives Considered→考慮過的模型替代案；Dataset Characteristics→資料集特性；Fairness and Bias Trade-offs→公平與偏誤取捨；Expected Model Lifetime→預期模型壽命；Retraining Trigger→再訓練觸發；Explainability Requirements→可解釋需求；Regulatory Compliance→法規合規 |
| E6 | Quality Attribute Definitions→品質屬性定義；Model Freshness→模型新鮮度；Drift Tolerance→漂移容忍；Explainability→可解釋；Fairness→公平；Robustness→強健；Scenario Format→情境格式；Cross-Component Scenarios→跨元件情境 |
| E7 | Boundary Erosion→邊界侵蝕；Entanglement→糾纏；Hidden Feedback Loops→隱藏回饋迴圈；Data Dependency Debt→資料依賴債；Pipeline Debt→管線債；Configuration Debt→設定債；Model Staleness→模型陳舊；Register Entry Format→登記條目格式；Debt Summary Dashboard→債務總覽板；Review Cadence→覆審節奏 |
| E8 | Monitoring→監測；Retraining Policy→再訓練政策；Deployment Strategy→部署策略；Rollback Policy→回退政策；Incident Response→事故應變 |
| C4-E1 | Stereotype Definitions→刻板型定義；Mermaid Conventions→Mermaid 慣例；Annotation Guidelines→標註準則；Template→範本 |
| C4-E2 | Data Source Inventory→資料源清冊；Lineage Diagram→血緣圖；Lineage Details→血緣明細；Freshness Requirements→新鮮度需求；Privacy Flow→隱私流；Schema Registry→schema 登錄 |
| C4-E3 | Boundary Overview→邊界總覽；Boundary Interfaces→邊界介面；Confidence Thresholds→信心門檻；Degradation Behavior→降級行為；Propagation Rules→傳播規則；Testing Implications→測試含意 |

### 1.3 三種檔的骨架範本

**(a) arc42 E 節檔**（以 03 為例；05／06／08／09／10／11／13 同形）

```markdown
---
section: 3
summary: 業務脈絡與技術脈絡；E1 AI 邊界劃定的系統層落點
rad_ai: [E1]
rad_ai_stage: 1
---
# §3 脈絡與範圍

## 3.1 業務脈絡

TODO(波 3)

## 3.2 技術脈絡

系統脈絡圖＝[C4-L1 系統脈絡](../c4/C4-L1-system-context.md)（同圖不複製）。TODO(波 3)

## 3.3 E1 AI 邊界劃定

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E1 邊界劃定](../process/P-E1-boundary.md)。
```

**(b) process 檔**（以 P-E1 為例；子節依 §1.2）

```markdown
---
rad_ai: [E1]
rad_ai_map:
  AI Components Inventory: AI 元件清冊
  System Boundary Diagram: 系統邊界圖
  Four-Part Boundary Contract: 四段邊界契約
  Failure Modes: 失效模式
  External AI Dependencies: 外部 AI 依賴
---
# P-E1 邊界劃定（流程層）

以 RAD-AI E1 的形制記載開發流程中的 AI 代理（主線、implementer、review、fix、CDP 代理、三支 hook）與人審／機器閘的邊界；系統層對應＝`docs/arc42/03-context-and-scope.md` §3.3。每個子節首句標明類比張力（哪裡對得上、哪裡是硬套）。

### AI 元件清冊

類比張力：TODO(波 3)

### 系統邊界圖

類比張力：TODO(波 3)
（其餘子節同形）
```

**(c) c4 E 檔**（以 C4-E3 為例）：frontmatter `rad_ai: [C4-E3]`、`rad_ai_stage: 2`、`rad_ai_map` 六鍵；H1；引言一句「系統本體全為確定性區域；目前無 AI 元件（截至 2026-09-03）；流程層對應＝`docs/process/P-C4-E3-materials-boundary.md`」；六個 `###` 子節各一行 `TODO(波 3)`。C4-E1／C4-E2 同形（引言改各自一句：C4-E1「標註規則本波未定、標註對象零」；C4-E2「血緣 overlay 的系統面隨稽核表刀填入；隱私流為真內容、隨刀填」）。

### 1.4 生成物的形

**LESSONS.md**（`gen_lessons_index`）：

```
<!-- 機器生成：… -->
<!-- next: LL-00001 -->
# LESSONS — 教訓索引（機器生成；一坑一檔住 LESSONS/LL-NNNNN-<slug>.md）

配號＝本檔頭 next（自檔集最大號＋1 推導、ADR-00005）→ 建檔 → `python3 tools/docsync generate`。條目檔 frontmatter：`id`、`rule_id`（RL-NNNN 或 none：理由）、`promotion_surface`（rules／gate／code／none）、選填 `recurrence_of`；正文首行 `LL-NNNNN｜坑名`（GT-08 對賬）。

| LL | 坑名 | rule_id | promotion_surface | 檔 |
|---|---|---|---|---|
```

零檔時只有表頭；有檔時每檔一列、依 id 排序、`檔` 欄＝相對連結 `[LL-00001-<slug>.md](LESSONS/LL-00001-<slug>.md)`；坑名取正文首行 `｜` 後字串。

**ARCHITECTURE.md**（`gen_architecture_index`）：

```
<!-- 機器生成：… -->
# ARCHITECTURE — 活書索引（機器生成、例外註冊）

| 節 | 檔 | 摘要 | 掛載 E | 流程層檔 |
|---|---|---|---|---|
| §1 | [簡介與目標](01-introduction-and-goals.md) | … | — | — |
| §3 | [脈絡與範圍](03-context-and-scope.md) | … | E1 | [P-E1-boundary.md](../process/P-E1-boundary.md) |
```

輸入＝`docs/arc42/NN-*.md`（tracked）；排序＝`section`；標題＝H1 剝 `§N `；流程層檔＝`docs/process/` 中 `rad_ai` 同值之檔（零或多個、以「、」連）。

**RAD-AI-MAP.md**（`gen_rad_ai_map`）：

```
<!-- 機器生成：… -->
# RAD-AI-MAP — RAD-AI 項目對照總表（啟動書 §3.3 的機器版；DoD A1 驗收面）

| RAD-AI 項目 | 系統層檔 | 系統層子節 | 流程層檔 | 流程層子節 | 採用階段 |
|---|---|---|---|---|---|
| E1 | [03-context-and-scope.md](../arc42/03-context-and-scope.md) | 目前無 | [P-E1-boundary.md](../process/P-E1-boundary.md) | 0/5 | 1 |
```

項目序＝E1～E8、C4-E1～E3、ANNEX-IV；系統層檔＝非 process 之含該 `rad_ai` 值的檔（多檔以「、」連）；**子節欄（Q3）**＝該層檔的 `已填實/N`，N＝`len(E_SUBSECTIONS[項目])`，已填實＝檔內 `###` 標題 ∈ 該檔 `rad_ai_map` 值、且子節正文（到下一個任意層級標題前）零 `TODO(波 k)` 命中；系統層正文含 `book.NO_AI_SENTENCE` → 顯示「目前無」；無檔→「—」；有檔無 map→`0/N`；ANNEX-IV→「—」。採用階段＝系統層檔 `rad_ai_stage`（缺→「—」）。

---

## 2. 內容真源速查（各 Task 抄形不抄字）

### 2.1 compose 17 服務（C4-L2 節點；`book.compose_services` 現值）

| 服務 | 職責 | profile／檔 | 相依（邊） |
|---|---|---|---|
| front-nginx | TLS 終端與反向代理 | 預設 | → base-web、rust-api |
| base-web | 前端（Vite dev） | 預設 | — |
| rust-api | 後端 API | 預設 | → postgres、redis、migrate；dev → mailpit（SMTP 1025） |
| migrate | 啟動閘：migration | 預設 | → postgres |
| postgres | 主庫 | 預設 | — |
| redis | 快取／會話 | 預設 | — |
| mailpit | dev 收信 | dev.yml | — |
| loki | 日誌庫 | obs | — |
| alloy | 日誌採集 | obs | → loki、socket-proxy |
| socket-proxy | docker API 代理 | obs | — |
| grafana | 儀表板 | obs、metrics | → loki、prometheus（datasource） |
| prometheus | 指標庫 | metrics | → rust-api、postgres_exporter、redis_exporter、pushgateway（scrape） |
| postgres_exporter | pg 指標 | metrics | → postgres |
| redis_exporter | redis 指標 | metrics | → redis |
| pushgateway | 批次指標 | metrics | — |
| reaper | 清理 job | jobs | → postgres |
| example-dev | soybean example 原版基線 | example.yml | — |

### 2.2 arc42 十三檔的官方子節（rev6 中文名；E 子節依 §1.2）

| 檔 | H1 | 子節（`##`） |
|---|---|---|
| 01-introduction-and-goals.md | §1 簡介與目標 | 1.1 需求概覽（含「本框架要解的缺口」段、波 3）／1.2 品質目標／1.3 利害關係人 |
| 02-architecture-constraints.md | §2 架構約束 | 技術約束／組織約束／慣例約束 |
| 03-context-and-scope.md | §3 脈絡與範圍 | 3.1 業務脈絡／3.2 技術脈絡（連結 C4-L1）／3.3 E1 AI 邊界劃定 |
| 04-solution-strategy.md | §4 解法策略 | 技術選擇／頂層分解／品質目標達成法 |
| 05-building-block-view.md | §5 建構區塊視圖 | 5.1 整體系統白盒／5.2 第二層／5.3 第三層／5.4 E2 模型登錄視圖 |
| 06-runtime-view.md | §6 執行期視圖 | 6.1 執行情境（首情境隨首刀）／6.2 E3 資料管線視圖（編號隨情境數浮動、無 deep-link） |
| 07-deployment-view.md | §7 部署視圖 | 7.1 基礎設施第一層（連結 C4-L2、埠指針 reference/ports）／7.2 基礎設施第二層 |
| 08-crosscutting-concepts.md | §8 橫切概念 | 8.1 資料慣例／8.2 API 慣例／8.3 授權慣例／8.4 fork-delta 軌道（憲法 §III 指針）／8.5 E4 負責任 AI 概念 |
| 09-architecture-decisions.md | §9 架構決策 | 指針段（decisions/、DECISIONS-INDEX）／9.1 E5 AI-ADR 形制與對映表（模板五子節 ↔ reference 七欄；本波寫齊，見 §2.4） |
| 10-quality-requirements.md | §10 品質需求 | 10.1 品質需求概覽／10.2 品質情境／10.3 E6 AI 品質情境 |
| 11-risks-and-technical-debt.md | §11 風險與技術債 | ※11.1 風險／※11.2 技術債（指針 BACKLOG 整檔）／※11.3 E7 AI 債務登記 |
| 12-glossary.md | §12 名詞表 | 系統術語（表、波 3）／AI 術語（表、標「保留」、自 RAD-AI glossary 中文改寫、波 3）；流程術語指針 RULES 名詞段 |
| 13-operational-ai-view.md | §13 營運 AI 視圖 | E8 一句「目前無」＋指針 P-E8（無其他子節） |

E 子節與 §13 的固定句：「目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝`[P-Ek …](../process/P-Ek-….md)`。」（連結形以各檔實際路徑代入）；其餘子節一行 `TODO(波 3)`（3.2／7.1 加圖連結一句）。

### 2.3 compliance 兩檔

**annex-iv-checklist.md** 欄＝AIV 鍵｜Annex IV 要求（摘）｜RAD-AI 原列號｜RAD-AI 十類號｜rev6 承載｜Evidence｜自評（GT-10 讀第 6 欄 Evidence）。23 列鍵與要求摘、原列號＝啟動書附錄 G 逐列；十類號＝交接包表二真實對映（1a～1h→1；2a→2；2b→2／3；2c→3；2d→4／5；2e→9；2f→—；2g→8；2h→—；3→6／8／9；4→8；5→6；6→7；7／8→—；9→10）；rev6 承載＝該鍵有 AI 元件時的系統層落點（1a／1g→`01`；1b→`03` §3.3；1c／6→`05` §5.4；1d／1e→`07`；1f→不適用（非實體產品）；1h→`docs/ops/RUNBOOK.md`；2a→`05` §5.4；2b→`09` §9.1；2c→`05`＋`07`；2d→`06` E3＋`c4/C4-E2`；2e→`08` §8.5；2f／3／9→`13`；2g／4→`10` §10.3；2h→`08`（安全慣例）；5→`11` §11.3；7／8→不承載（合規程序、非文件框架））；Evidence＝「不適用：系統目前無 AI 元件（截至 2026-09-03）、＜鍵別理由＞；隨 AI 功能刀填入」（鍵別理由例：2d「無訓練資料集」、2e「無需 Art. 14 監督措施」、7「harmonised standards 屬合規程序」）；自評＝「不適用」。表前「說明」段中文改寫 RAD-AI Instructions 三步（填系統名與風險分級→逐鍵填承載與證據→合規審閱）、表後「總結」段一句（23 鍵不適用 23、0／1／2 計分零列）。

**annex-iv-mapping.md**：表一＝Annex IV 真實點號（23 鍵）→ RAD-AI 十類 → rev6 節（同上承載欄）；表二＝RAD-AI 十類 → RAD-AI 指南自稱的 Annex IV 節 → 真實點號 → 判定（對／半對／錯／錯且掩蓋缺口；交接包表二重打字消化）；末段一句「點 7／8 RAD-AI 十類無對應、rev6 以 AIV-7／AIV-8 補列」。

### 2.4 09 §9.1 E5 對映表（本波寫齊）

| 模板五子節（AI-ADR 模板 `####`、皆在「AI 特定考量」節下） | reference 七欄 |
|---|---|
| 資料集特性 | 2. Dataset Characteristics |
| 公平與偏誤取捨 | 3. Fairness and Bias Trade-offs |
| 模型生命週期 | 4. Expected Model Lifetime＋5. Retraining Trigger |
| 可解釋 | 6. Explainability Requirements |
| 法規合規 | 7. Regulatory Compliance |

reference 欄 1「Model Alternatives Considered」對應模板 body 節「考慮過的替代案」（模板 `###` 層、非 `####`；grill 事實查核修正）。填實時 09 以 `###` 承載七鍵、Lifetime 與 Retraining Trigger 兩鍵同值「模型生命週期」（Q4 腿允許多鍵同值）。

形制句：AI-ADR 不另開號空間（rev6 五碼 id＋frontmatter `rad_ai: [E5]`＋標題前綴「AI-ADR」；啟動書 §3.5）；目前 AI-ADR 零份。

### 2.5 附錄 G 四列「待核」定案（依 RAD-AI checklist 原列文字對官方點文）

| RAD-AI 原列 | 原列文字（摘） | 定案 AIV 鍵 | 理由 |
|---|---|---|---|
| 3.4 | 訓練資料假設的表述 | **2b** | 2(b) 明列「key design choices including the rationale and assumptions made」；2(d) 為資料集本體描述 |
| 4.2 | 訓練選擇與最佳化技術 | **2b＋2d** | 2(b)「what the system is designed to optimise for」＋2(d)「training methodologies and techniques」 |
| 7.1 | 效能指標描述 | **4＋2g** | 點 4 指標適切性；2(g) 驗證測試用 accuracy／robustness 指標 |
| 9.2 | 日誌與稽核能力 | **9＋3** | 點 9 上市後評估系統；點 3 監測／運作／控制 |

### 2.6 RUNBOOK 最小章內容來源

| 章 | 本波內容 | 來源（唯讀、重打字消化） |
|---|---|---|
| §1 快速啟動 | 五步：`bash tools/bootstrap.sh`→`python3 deploy/generate-secrets.py`→`python3 deploy/preflight-secrets.py`→`bash deploy/generate-dev-cert.sh`→`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait`（README 已載、波 1 實跑） | README.md「操作快速入口」；rev5:RUNBOOK §1 |
| §7 機密輪替表 | 抬頭＝SECRETS_DIR 取值片段（`sed -n 's/^SECRETS_DIR=//p' .env`、取不到印 FAIL、不設回退）＋一句指針「十三機密表＝`deploy/secrets/README.md`」 | rev5:RUNBOOK §7 抬頭；`deploy/secrets/README.md` |
| §12 工具鏈速查 | 表：`python3 tools/docsync generate`／`check`／`lint`（GT-01～GT-12）／`rules emit --scope`／`errata`／`test`；`python3 tools/wf-watchdog.py`；`bash tools/bootstrap.sh`；deploy 六支 CLI＋`sops.sh`＋兩支 `.sh`；`tools/orchestration/cdp.mjs`、harness-test；欄＝命令｜作用｜需運行中 stack | README「操作快速入口」；rev5:RUNBOOK §12 表形 |
| §14 埠與帳號 | 真相源指針（`docs/generated/reference/ports.md`）；帳號表隨 001 型刀（`reference/accounts.md` 尚未產） | rev5:RUNBOOK §14 |
| §15 SOPS 機密營運（Q5 全指針） | 資產一段（鑰檔 `keys-fork260509-rev6.txt`、`.sops.yaml` 兩 recipient、`RV6_AGE_KEY_FILE`／`RV6_DECRYPT_MANUAL`）＋「程序見 `deploy/secrets/README.md`；細節承 rev5:RUNBOOK §15 同節、隨首個機密事件補實」；§15.2／§15.4 只留標題＋一句 rev5 指針（被 deploy README 引用、須存在） | `deploy/sops.sh` 變數名；`deploy/secrets/README.md` |
| 其餘 §2～§6、§8～§11、§13、§16、§9c | 各一行：章旨＋「隨對應刀補實文」（§13 指針 LESSONS.md；§9c 指針 CLAUDE.md §7） | rev5:RUNBOOK 章名 |

---

## 3. Tasks

### Task 1: ops 帳本三檔（BACKLOG 兩卷、RUNBOOK）＋README／CLAUDE 指針＋Day-1 GT-12.runbook-absent 解除

**Files:**
- Create: `docs/ops/BACKLOG.md`、`docs/ops/BACKLOG-DEFERRED.md`、`docs/ops/RUNBOOK.md`
- Modify: `tools/docsync/gates.py`（DAY1_EXEMPTIONS 刪 `GT-12.runbook-absent`）、`README.md`（docs 行）
- Test: `tools/docsync/tests/test_gates.py`（既有 Day-1 迭代測不變）

**Interfaces:** Produces `docs/ops/RUNBOOK.md` 含字面 `GT-01～GT-12`（GT-12 第三處名冊）；`docs/ops/BACKLOG.md` 含 `<!-- next: BL-00001 -->`。

- [ ] **Step 1: 寫 BACKLOG 兩卷**（零條目；檔頭形如下）

```markdown
<!-- next: BL-00001 -->
# BACKLOG — 待辦

條目形 `- BL-NNNNN｜<product／governance>｜<一句話>｜<觸發條件（必填、須可到期）>`；配號取檔頭 next 後 bump、號碼永不回收；完成即刪列、git 即史（RL-0050）。
滯後項另居 `BACKLOG-DEFERRED.md`（user 拍板暫不排程；lint 視為仍開放、STATE 分開計數）——查待辦全帳須兩卷併看。開放上限 25（RL-0052）。
```

BACKLOG-DEFERRED.md：同形說明、無 next-id、「配號永遠只在主檔；移入／移回＝整行搬＋滯後戳記；完成＝刪列＋事件 backlog_done」。

- [ ] **Step 2: 寫 RUNBOOK 骨架**（§2.6；抬頭宣告「創世期最小章＝§1／§7 抬頭／§12／§14；§15 為指針；其餘隨對應刀補實文；章內不放未經實跑的命令」；§12 表含 `GT-01～GT-12` 字面；§7 抬頭片段先實跑一次）
- [ ] **Step 2b: RULES 名詞段補三詞**（§0.2-14；`python3 tools/docsync rules emit --scope implementer | tail -1` 前後版本串相同＝名詞段不入雜湊的實證）
- [ ] **Step 3: 解除 Day-1**：`gates.py` 刪 `GT-12.runbook-absent` 一行 → verify: `python3 tools/docsync lint` 對 GT-12 零 SKIP、零「已到期」ERROR
- [ ] **Step 4: README docs 行**：`docs/ops/BACKLOG.md、LESSONS/` 行改為兩行（BACKLOG 兩卷／LESSONS.md＋LESSONS/）、加 `docs/ops/RUNBOOK.md` 行；「想知道 X 看 Y」加「怎麼操作→RUNBOOK」（活書行的「波 2 骨架」字樣留到 T6 拿掉）
- [ ] **Step 5: generate＋check＋lint 全綠** → verify: `python3 tools/docsync lint; echo rc=$?` 為 0；GATES.md Day-1 表 5 筆
- [ ] **Step 6: Commit**（`-F` 暫存檔）→ verify: `git log -1 --stat`

### Task 2: 生成器三支（TDD）＋GT-10 第八腿＋名冊 10 件＋ADR-00005＋Day-1 GT-05／GT-06 兩筆解除

**Files:**
- Modify: `tools/docsync/book.py`（`gt_10` 第八腿：有 `rad_ai_map` 的檔，每個 map 值須為同檔某 `###` 標題字面，缺＝`finding(ERROR, "GT-10", rel, "map 值「X」無對應 ### 標題")`）、`tools/docsync/references.py`（`GENERATED_FILES` 加 `docs/ops/LESSONS.md`、`docs/arc42/ARCHITECTURE.md`、`docs/generated/RAD-AI-MAP.md`；新函式 `gen_lessons_index(ctx)`、`gen_architecture_index(ctx)`、`gen_rad_ai_map(ctx)`；`compute_generated` 三鍵）、`tools/docsync/gates.py`（刪 `GT-05.ledgers-absent`、`GT-06.book-absent`）、`CLAUDE.md`（§4 三材質句加「＋docs/arc42/ARCHITECTURE.md、docs/ops/LESSONS.md（例外註冊）」；§2 落帳句「踩坑→LESSONS 一坑一檔＋generate」）、`README.md`（generated 行加 RAD-AI-MAP；「想知道 X 看 Y」加「系統長怎樣→ARCHITECTURE.md」「RAD-AI 導入到哪→RAD-AI-MAP.md」）
- Create: `docs/arc42/decisions/ADR-00005-generated-indexes-and-ll-next-id.md`
- Test: `tools/docsync/tests/test_references.py`、`tools/docsync/tests/test_book_form.py`

**Interfaces:**
- Produces: `references.gen_lessons_index(ctx) -> str`、`gen_architecture_index(ctx) -> str`、`gen_rad_ai_map(ctx) -> str`；`GENERATED_FILES` 長度 10。
- Consumes: `book.RE_LL_FILE`、`book.E_SUBSECTIONS`、`book.NO_AI_SENTENCE`、`common.parse_front_matter`、`common.GENERATED_HEADER`。

- [ ] **Step 1: 寫失敗測試**（三生成器＋名冊＋LL 零雙計數）

```python
class TestGeneratedIndexes(unittest.TestCase):
    LL1 = '---\nid: "LL-00001"\nrule_id: RL-0001\npromotion_surface: rules\n---\nLL-00001｜坑一\n'
    LL3 = '---\nid: "LL-00003"\nrule_id: none：理由\npromotion_surface: none\n---\nLL-00003｜坑三\n'

    def test_lessons_index_next_is_max_plus_one_and_rows_are_table(self):
        out = references.gen_lessons_index(stub({f"{LESSONS_DIR}/LL-00001-a.md": self.LL1, f"{LESSONS_DIR}/LL-00003-c.md": self.LL3}))
        self.assertIn("<!-- next: LL-00004 -->", out)
        self.assertIn("| LL-00001 | 坑一 | RL-0001 | rules | [LL-00001-a.md](LESSONS/LL-00001-a.md) |", out)
        self.assertEqual(book.RE_ENTRY["LL"].findall(out), [])          # 零雙計數
        self.assertIn("<!-- next: LL-00001 -->", references.gen_lessons_index(stub({})))

    def test_architecture_index_sorted_title_and_process_join(self):
        files = {"docs/arc42/03-context-and-scope.md": "---\nsection: 3\nsummary: 脈絡\nrad_ai: [E1]\n---\n# §3 脈絡與範圍\n",
                 "docs/arc42/01-introduction-and-goals.md": "---\nsection: 1\nsummary: 目標\n---\n# §1 簡介與目標\n",
                 "docs/process/P-E1-boundary.md": "---\nrad_ai: [E1]\n---\n# P-E1\n"}
        out = references.gen_architecture_index(stub(files))
        rows = [l for l in out.split("\n") if l.startswith("| §")]
        self.assertTrue(rows[0].startswith("| §1 | [簡介與目標](01-introduction-and-goals.md) | 目標 | — | — |"))
        self.assertIn("| §3 | [脈絡與範圍](03-context-and-scope.md) | 脈絡 | E1 | [P-E1-boundary.md](../process/P-E1-boundary.md) |", out)

    def test_rad_ai_map_status_and_subsection_ratio(self):
        pmap = "".join(f"  {k}: 中文{i}\n" for i, k in enumerate(book.E_SUBSECTIONS["E1"]))
        files = {"docs/arc42/03-context-and-scope.md": "---\nsection: 3\nrad_ai: [E1]\nrad_ai_stage: 1\n---\n# §3\n\n目前無 AI 元件（截至 2026-09-03）。\n",
                 "docs/process/P-E1-boundary.md": f"---\nrad_ai: [E1]\nrad_ai_map:\n{pmap}---\n# P-E1\n"}
        out = references.gen_rad_ai_map(stub(files))
        self.assertIn("| E1 | [03-context-and-scope.md](../arc42/03-context-and-scope.md) | 目前無 | [P-E1-boundary.md](../process/P-E1-boundary.md) | 0/5 | 1 |", out)
        self.assertIn("| E2 | — | — | — | — | — |", out)

    def test_rad_ai_map_counts_filled_subsections_only(self):
        keys = book.E_SUBSECTIONS["E1"]
        pmap = "".join(f"  {k}: 中文{i}\n" for i, k in enumerate(keys))
        body = "# P-E1\n\n### 中文0\n\n類比張力：真句。\n\n### 中文1\n\n類比張力：TODO(波 3)\n\n### 中文2\n\n類比張力：真句。\n\n## 其他\n\nTODO(波 3)\n"
        out = references.gen_rad_ai_map(stub({"docs/process/P-E1-boundary.md": f"---\nrad_ai: [E1]\nrad_ai_map:\n{pmap}---\n{body}"}))
        self.assertIn("| E1 | — | — | [P-E1-boundary.md](../process/P-E1-boundary.md) | 2/5 | — |", out)

    def test_roster_ten_and_compute_has_three_new_keys(self):
        self.assertEqual(len(references.GENERATED_FILES), 10)
        for rel in ("docs/ops/LESSONS.md", "docs/arc42/ARCHITECTURE.md", "docs/generated/RAD-AI-MAP.md"):
            self.assertIn(rel, references.GENERATED_FILES)
```

- [ ] **Step 1b: GT-10 第八腿失敗測試**（test_book_form；仿既有 `run()`）：process 檔 `rad_ai_map` 含值「甲」而正文無 `### 甲` → 有 ERROR 含「無對應 ### 標題」；補上 `### 甲`＋類比張力行 → 零 ERROR；兩鍵同值只需一個標題
- [ ] **Step 2: 跑測試確認失敗** → `python3 -m unittest docsync.tests.test_references docsync.tests.test_book_form -v`（自 `tools/` 目錄）：AttributeError／AssertionError
- [ ] **Step 3: 實作三生成器**（各 ≤40 邏輯行）：`gen_lessons_index` 掃 tracked＋工作樹 `LESSONS/` 檔名（沿 `book._family_state` 同口徑）、讀 frontmatter 與正文首行；`gen_architecture_index` 掃 `docs/arc42/` 之 `^\d{2}-.*\.md$`、H1 剝 `§N `、process join；`gen_rad_ai_map` 依 §1.4 規則；三者皆以 `GENERATED_HEADER` 起、`\n` 結尾、內容只依賴 tracked 檔（冪等）
- [ ] **Step 3b: 實作 GT-10 第八腿**（≤8 行；docstring GATE 區塊 drift 欄加「map 值↔標題」）
- [ ] **Step 4: 名冊 10 件＋compute_generated 三鍵** → 測試綠；`python3 tools/docsync test` 全綠
- [ ] **Step 5: 立 ADR-00005**（accepted；frontmatter 同 ADR-00004 形；body 六節：背景（§3.1 例外註冊、§3.6 派生物、GT-05 讀檔頭 next 的互撞）／決策驅動因子／考慮過的替代案（Q1 之 B、C）／決定（三件入名冊、next＝max＋1、單調靠 GT-05 既有腿、RAD-AI-MAP 落點與六欄含兩層填實計數、索引列為表格形防雙計數、GT-10 值↔標題腿）／後果／翻案觸發器（LL 檔出現刪除需求＝重評 append-only 假設））
- [ ] **Step 6: 解除 Day-1 兩筆**（`GT-05.ledgers-absent`、`GT-06.book-absent`）＋CLAUDE.md／README 兩處指針 → `python3 tools/docsync generate`（首生三檔：LESSONS.md 零列、ARCHITECTURE.md 零列、RAD-AI-MAP.md 十二列全「—」）→ verify: `python3 tools/docsync check && python3 tools/docsync lint` rc 0；GATES.md Day-1 表 3 筆；`git status` 見三個新生成檔
- [ ] **Step 7: Commit**

### Task 3: process 八檔骨架

**Files:** Create `docs/process/P-E1-boundary.md`、`P-E2-agent-registry.md`、`P-E3-doc-pipeline.md`、`P-E4-responsible-agent.md`、`P-E6-quality-scenarios.md`、`P-E7-agent-debt.md`、`P-E8-operations.md`、`P-C4-E3-materials-boundary.md`（八檔；E5 無流程層檔、見 §0.2-7）。

- [ ] **Step 1: 逐檔寫骨架**（§1.3(b) 範本；引言一句寫實：各檔對應的系統層檔與 §3.2 樹的一句定位，例 P-E2「AGT- 名冊：角色×模型×effort×最近換模日×產物進哪道閘；真源＝`tools/orchestration/` OPTS 常數」）；每個 `###`＝§1.2 中文子節名、首句 `類比張力：TODO(波 3)`
- [ ] **Step 2: 自證**：`python3 tools/docsync lint` 零 ERROR（GT-10 類比張力腿、鍵集腿、值↔標題腿皆過）；RAD-AI-MAP 流程層子節欄八列皆 `0/N`；`grep -c '類比張力：TODO(波 3)' docs/process/*.md` 合計＝5＋4＋6＋7＋8＋10＋5＋6＝51
- [ ] **Step 3: generate**（RAD-AI-MAP 流程層欄與子項欄填入）→ check 綠 → Commit

### Task 4: C4 五檔（L1／L2 首版＋E1～E3 骨架）

**Files:** Create `docs/c4/C4-L1-system-context.md`、`C4-L2-container.md`、`C4-E1-ai-component-stereotypes.md`、`C4-E2-data-lineage-overlay.md`、`C4-E3-non-determinism-boundary.md`。

- [ ] **Step 1: C4-L1**：Mermaid `flowchart LR`，節點 `admin["管理員"]`、`system["rev6 admin 系統"]`、`smtp["SMTP 服務"]`（dev＝mailpit）；表 3 列首欄＝label 字面；一句「E1 標註：目前無 AI 元件、無非確定性區域」
- [ ] **Step 2: C4-L2**：Mermaid 17 節點（id 底線形、label＝compose 名）＋§2.1 邊；表 17 列（服務｜職責｜profile／檔｜相依）；埠一句指針 `docs/generated/reference/ports.md`；stereotype 標註句「本圖零 AI stereotype（C4-E1 規則隨 AI 功能刀啟用）」
- [ ] **Step 3: C4-E1／E2／E3 骨架**（§1.3(c)）
- [ ] **Step 4: 自證**：`python3 tools/docsync lint` 零 ERROR（C4-L2 ⊇ 17 服務腿、節點 ⊆ 表腿）；破壞性驗證＝暫刪 C4-L2 一個節點→lint 紅「C4-L2 節點缺 compose 服務」→還原→`git status --porcelain` 回基準
- [ ] **Step 5: generate → Commit**

### Task 5: compliance 兩檔

**Files:** Create `docs/compliance/annex-iv-checklist.md`、`docs/compliance/annex-iv-mapping.md`（§2.3、§2.5）。

- [ ] **Step 1: 檢核表**：frontmatter `rad_ai: [ANNEX-IV]`、`rad_ai_stage: compliance`；說明段、23 列、總結段
- [ ] **Step 2: 映射表**：frontmatter 同上；表一、表二、末句
- [ ] **Step 3: 自證**：lint 零 ERROR（23 鍵齊、Evidence 腿）；破壞性驗證＝暫把 AIV-2d Evidence 改 `TODO(波 4)`→lint 紅「Evidence 欄未引」→還原
- [ ] **Step 4: generate → Commit**

### Task 6: arc42 十三檔＋Day-1 GT-10.doc-skeleton-absent 解除

**Files:** Create §2.2 十三檔；Modify `tools/docsync/gates.py`（刪 `GT-10.doc-skeleton-absent`）。

- [ ] **Step 1: 逐檔寫**（§1.3(a) 範本、§2.2 子節；09 §9.1 表＝§2.4；12 兩表骨架各一列 `TODO(波 3)`；連結只指已存在檔：`../c4/C4-L1-…`、`../c4/C4-L2-…`、`../process/P-Ek-…`、`decisions/`、`../generated/DECISIONS-INDEX.md`、`../generated/reference/ports.md`、`../ops/BACKLOG.md`、`../ops/LESSONS.md`、`../ops/RULES.md`）
- [ ] **Step 2: 解除 Day-1 第四筆**＋README 活書行去「波 2 骨架」字樣 → generate（ARCHITECTURE.md 13 列；RAD-AI-MAP 系統層子節欄全「目前無」）
- [ ] **Step 3: 自證**：`python3 tools/docsync check && python3 tools/docsync lint` rc 0；GATES.md Day-1 表恰 2 筆（GT-03.no-close-events、GT-08.lessons-absent）；`grep -rc 'TODO(波 3)' docs/arc42 docs/c4 docs/compliance docs/process` 逐檔數字入 commit 訊息
- [ ] **Step 4: Commit**

### Task 7: 波 2 出口驗收＋收單

- [ ] **Step 1: 全量自證**：`python3 tools/docsync test`（79＋新增 6 全綠）；`bash tools/bootstrap.sh` rc 0（僅 remote ⚠）；`python3 tools/docsync lint` 0 ERROR 0 WARN；`python3 tools/docsync errata 'LESSONS append'`／`errata '波 2 建空檔'` 零殘留
- [ ] **Step 2: final holistic review**（不落報告；處置逐項列入收單 commit 訊息）
- [ ] **Step 3: 波標記 bump**：`docs/ops/NOTES.md` 首行 `<!-- wave: 3 -->`、現況改「波 2 出口已過、波 3 起手」、下一步＝波 3 列（§0.3 剩餘欄）→ lint 綠（`TODO(波 3)` 於 N=3 仍合法）→ 一顆 commit
- [ ] **Step 4: 停——merge 需 user 同意**：`git merge --no-ff -F <暫存檔> 000-w2-book-skeleton` 回 `rev6-admin-root` → verify `git rev-parse HEAD` 變、`git log -1 --merges`
- [ ] **Step 5: 簿記 commit**：events append misc（category governance、summary、`merge`＝merge 全 SHA、`backlog_add: []`）→ `python3 tools/docsync generate` → commit（量牆鐘）
- [ ] **Step 6: perf 事件** `close_bookkeeping`（wall_s、rc、commit＝簿記 SHA）隨下一顆 commit 入帳（RL-0053）

---

## Self-Review

1. **Spec coverage**：§3.2 樹的 docs/ 每一項→T1（ops 三檔）、T2（三生成物＋ADR）、T3（process 八檔）、T4（c4 五檔）、T5（compliance 兩檔）、T6（arc42 十三檔）；§4.6 Day-1 四筆→T1／T2／T6；§5 波 2 出口→T7；`reference-src/` 隨 001 型刀（不在本波、啟動書 §3.7）。
2. **Placeholder scan**：本檔的 `TODO(波 3)` 全部是產物內容的規格、非計畫佔位；無 TBD／待決。
3. **Type consistency**：`gen_lessons_index`／`gen_architecture_index`／`gen_rad_ai_map` 名稱與 T2 測試一致；frontmatter 鍵五個（§1.1）在 §1.3、§2.3、T3～T6 同名；`rad_ai_stage` 值域 `1／2／3／compliance` 與 RAD-AI-MAP 欄一致；RAD-AI-MAP 六欄名在 §1.4、T2 測試、T3／T6 自證同字。
4. **閘對賬**：GT-10 八腿逐腿有對應形制（§1.3、§0.2-9、§2.3；第八腿＝T2）；GT-06 連結目標全在建檔序之後（T3 process → T4 c4 → T5 compliance → T6 arc42）；GT-12 RUNBOOK 字面在 T1；GT-01 名冊 10 件在 T2。
