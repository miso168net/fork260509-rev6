---
rad_ai: [ANNEX-IV]
rad_ai_stage: compliance
---
# Annex IV 技術文件檢核表（EU AI Act、Regulation 2024/1689）

列鍵＝真實 Annex IV 點號與子項（`AIV-1a`～`AIV-1h`、`AIV-2a`～`AIV-2h`、`AIV-3`～`AIV-9`，23 鍵；啟動書附錄 G）；RAD-AI 原列號（1.1～9.2）與十類號只作出處對照；RAD-AI 無對應的鍵由 rev6 補列並標明。官方點 3 無字母子項，四個面向並列於要求欄。

本表用法（RAD-AI 三步、中文改寫）：①填系統名與風險分級 ②逐鍵填 rev6 承載與證據——Evidence 欄寫「See `<檔>`, `<具名表>` — 記了什麼」或「不適用：<理由>」（GT-10 讀此欄：所引檔與具名表必實存）③合規審閱。量表 0／1／2 逐字承 RAD-AI；「不適用」為第四值、獨立於 0、必附理由（附錄 A F24）。

- 系統名：rev6 admin 後台（前端 base-web＋後端 rust-api）
- 風險分級：不適用（系統目前無 AI 元件、非 AI 系統）
- 評估日：2026-09-03；評估者：主線 Claude、user 拍板

| AIV 鍵 | Annex IV 要求（摘） | RAD-AI 原列號 | RAD-AI 十類號 | rev6 承載 | Evidence | 自評 |
|---|---|---|---|---|---|---|
| AIV-1a | 1(a) 預期用途、提供者名稱、版本與前版關係 | 1.1、1.2 | 1 | `docs/arc42/01-introduction-and-goals.md` §1.1 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無 AI 系統之預期用途與版本可述；隨 AI 功能刀填入 | 不適用 |
| AIV-1b | 1(b) 與外部軟硬體（含其他 AI 系統）的互動 | 1.3 | 1 | `docs/arc42/03-context-and-scope.md` §3.3 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無 AI 元件與外部系統的互動；隨 AI 功能刀填入 | 不適用 |
| AIV-1c | 1(c) 相關軟韌體版本與版本更新要求 | 1.4 | 1 | `docs/arc42/05-building-block-view.md` §5.4 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無模型版本史；隨 AI 功能刀填入 | 不適用 |
| AIV-1d | 1(d) 上市或投入服務的所有形式（套件、下載、API） | —（RAD-AI 無對應、rev6 補） | 1 | `docs/arc42/07-deployment-view.md` | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無 AI 系統投入服務之形式；隨 AI 功能刀填入 | 不適用 |
| AIV-1e | 1(e) 預期運行的硬體 | —（rev6 補） | 1 | `docs/arc42/07-deployment-view.md` | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無 AI 元件之硬體需求；隨 AI 功能刀填入 | 不適用 |
| AIV-1f | 1(f) 作為產品元件時的照片與內部佈局 | —（rev6 補） | 1 | 不承載（非實體產品） | 不適用：本系統為軟體後台、非實體產品元件；亦無 AI 元件（截至 2026-09-03） | 不適用 |
| AIV-1g | 1(g) 提供給 deployer 的使用者介面基本描述 | —（rev6 補） | 1 | `docs/arc42/01-introduction-and-goals.md` §1.3 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無 AI 元件之使用者介面可述；隨 AI 功能刀填入 | 不適用 |
| AIV-1h | 1(h) 使用說明（instructions for use） | —（rev6 補） | 1 | `docs/ops/RUNBOOK.md` | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無 AI 系統使用說明；後台操作手冊另居 RUNBOOK | 不適用 |
| AIV-2a | 2(a) 開發方法與步驟，含預訓練系統或第三方工具的使用 | 2.1 | 2 | `docs/arc42/05-building-block-view.md` §5.4 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無模型開發流程；隨 AI 功能刀填入 | 不適用 |
| AIV-2b | 2(b) 設計規格：一般邏輯、演算法、關鍵設計選擇與假設、取捨 | 2.2（設計規格半邊）、3.4、4.2 | 2／3 | `docs/arc42/09-architecture-decisions.md` §9.1 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、AI-ADR 零份；隨 AI 功能刀填入 | 不適用 |
| AIV-2c | 2(c) 系統架構如何組成與整合；開發／訓練／測試／驗證的運算資源 | 2.2（架構半邊）、2.3 | 3 | `docs/arc42/05-building-block-view.md`＋`docs/arc42/07-deployment-view.md` | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無訓練與驗證運算資源可述；隨 AI 功能刀填入 | 不適用 |
| AIV-2d | 2(d) 資料需求：datasheets 描述訓練方法與技術、訓練資料集、來源、標註、清理 | 3.1、3.2、3.3、4.1 | 4／5 | `docs/arc42/06-runtime-view.md` E3＋`docs/c4/C4-E2-data-lineage-overlay.md` | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無訓練資料集；隨 AI 功能刀填入 | 不適用 |
| AIV-2e | 2(e) 依 Art. 14 的 human oversight 措施評估；輸出可解釋的技術措施（Art. 13(3)(d)） | 8.1、8.2 | 9 | `docs/arc42/08-crosscutting-concepts.md` §8.5 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無需 Art. 14 監督措施；隨 AI 功能刀填入 | 不適用 |
| AIV-2f | 2(f) 預定變更（pre-determined changes）與持續合規的技術方案 | —（rev6 補） | — | `docs/arc42/13-operational-ai-view.md` | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無預定變更之 AI 系統；隨 AI 功能刀填入 | 不適用 |
| AIV-2g | 2(g) 驗證與測試程序、accuracy／robustness 指標、測試日誌與報告 | 7.1（部分） | 8 | `docs/arc42/10-quality-requirements.md` §10.3 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無模型驗證指標；隨 AI 功能刀填入 | 不適用 |
| AIV-2h | 2(h) 資安措施（cybersecurity measures） | —（RAD-AI 無對應、rev6 補） | — | `docs/arc42/08-crosscutting-concepts.md`（安全慣例） | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無 AI 元件專屬資安措施；系統本體資安慣例另居 §8 | 不適用 |
| AIV-3 | 3. 監測、運作與控制：能力與限制含 accuracy 程度／可預見非預期結果與風險來源／human oversight 措施／輸入資料規格（四面向並列、無字母子項） | 7.2、5.1（風險來源半邊）、8.2（半邊）、9.2（監測半邊） | 6／8／9 | `docs/arc42/13-operational-ai-view.md`＋`docs/arc42/10-quality-requirements.md` §10.3 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無 AI 系統可監測；隨 AI 功能刀填入 | 不適用 |
| AIV-4 | 4. performance metrics 的適切性 | 7.1 | 8 | `docs/arc42/10-quality-requirements.md` §10.3 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無模型效能指標；隨 AI 功能刀填入 | 不適用 |
| AIV-5 | 5. 依 Art. 9 的風險管理系統 | 5.1、5.2 | 6 | `docs/arc42/11-risks-and-technical-debt.md` §11.3 | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無 AI 風險登記；隨 AI 功能刀填入 | 不適用 |
| AIV-6 | 6. 生命週期中的相關變更 | 6.1 | 7 | `docs/arc42/05-building-block-view.md` §5.4＋`docs/arc42/13-operational-ai-view.md` | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無模型生命週期變更；隨 AI 功能刀填入 | 不適用 |
| AIV-7 | 7. 適用的 harmonised standards 清單（或替代方案） | —（RAD-AI 十類無對應） | — | 不承載（合規程序、非文件框架） | 不適用：harmonised standards 清單屬合規程序、文件框架不承載；亦無 AI 元件（截至 2026-09-03） | 不適用 |
| AIV-8 | 8. 依 Art. 47 的 EU declaration of conformity 副本 | —（RAD-AI 十類無對應） | — | 不承載（合規程序、非文件框架） | 不適用：宣告副本屬合規程序、文件框架不承載；亦無 AI 元件（截至 2026-09-03） | 不適用 |
| AIV-9 | 9. 依 Art. 72 的 post-market 評估系統與監測計畫 | 9.1、9.2 | 10 | `docs/arc42/13-operational-ai-view.md` | 不適用：系統目前無 AI 元件（截至 2026-09-03）、無上市後監測計畫；隨 AI 功能刀填入 | 不適用 |

總結：23 鍵全數「不適用」（系統目前無 AI 元件、截至 2026-09-03）、0／1／2 計分列零；RAD-AI 十類無對應之鍵（1d～1h、2f、2h、7、8）由 rev6 補列。附錄 G 四列「待核」定案（依 RAD-AI 原列文字對官方點文）：3.4→2b（2(b) 明列 rationale and assumptions）、4.2→2b＋2d、7.1→4＋2g、9.2→9＋3。
