---
rad_ai: [ANNEX-IV]
rad_ai_stage: compliance
---
# Annex IV 十類映射（RAD-AI 十類 ↔ 真實點號 ↔ rev6 節）

RAD-AI 的 EU AI Act 指南以自訂十類對照 Annex IV，其標的節號多處錯位（三源逐字核對結論＝啟動書 §1.2 D9 與附錄 G 23 鍵表；核對原件為 rev5 交接包、唯讀）；本表以真實點號為準、逐類記判定與 rev6 落點。每鍵細目住 `annex-iv-checklist.md`（23 鍵、Evidence 欄）。系統目前無 AI 元件（截至 2026-09-03），rev6 節欄＝該類有 AI 元件時的系統層落點。

| RAD-AI 十類 | RAD-AI 指南自稱的 Annex IV 節 | 真實點號 | 判定 | rev6 節 |
|---|---|---|---|---|
| 1 系統概述 | Section 1 | 點 1（1(a)～1(h)） | 對 | `docs/arc42/01-introduction-and-goals.md`＋`03-context-and-scope.md` §3.3（E1） |
| 2 系統元素與開發流程 | Section 2(a-b) | 2(a)、2(b) | 對 | `docs/arc42/05-building-block-view.md` §5.4（E2） |
| 3 設計規格與架構 | Section 2(c) | 2(b)（設計規格）＋2(c)（架構） | 半對 | `docs/arc42/05-building-block-view.md`～`07-deployment-view.md`＋`docs/c4/C4-E1-ai-component-stereotypes.md` |
| 4 資料與資料治理 | Section 2(d) | 2(d) | 對 | `docs/arc42/06-runtime-view.md` E3＋`docs/c4/C4-E2-data-lineage-overlay.md` |
| 5 訓練方法與技術 | Section 2(e) | 2(d)（datasheets describing the training methodologies and techniques） | 錯 | `docs/arc42/09-architecture-decisions.md` §9.1（E5） |
| 6 風險評估與管理 | Section 3 | 點 5（點 3 為 monitoring／functioning／control、僅「可預見非預期結果與風險來源」部分重疊） | 錯 | `docs/arc42/11-risks-and-technical-debt.md` §11.3（E7） |
| 7 生命週期變更 | Section 4 | 點 6 | 錯 | `docs/arc42/05-building-block-view.md` §5.4 版本史＋`13-operational-ai-view.md`（E8） |
| 8 效能指標與準確度 | Section 5 | 點 4＋點 3（accuracy 程度）＋2(g)（測試指標） | 錯 | `docs/arc42/10-quality-requirements.md` §10.3（E6）＋`docs/c4/C4-E3-non-determinism-boundary.md` |
| 9 人類監督 | Section 6 | 2(e)＋點 3 | 錯 | `docs/arc42/08-crosscutting-concepts.md` §8.5（E4） |
| 10 上市後監測 | Section 7-9 | 點 9；點 7（harmonised standards）與點 8（declaration of conformity）RAD-AI 十類完全無對應 | 錯且掩蓋缺口 | `docs/arc42/13-operational-ai-view.md`（E8） |

點 7／8 RAD-AI 十類無對應，rev6 以 `AIV-7`／`AIV-8` 補列於檢核表並標「不承載（合規程序、非文件框架）」。
