---
section: 9
summary: 決策外置 decisions/ 與索引；E5 AI-ADR 形制與對映表
rad_ai: [E5]
rad_ai_stage: 2
rev5_blueprint:
  §9 架構決策: 承襲（decisions/ 一決策一檔＋DECISIONS-INDEX 指針；波 2 落地）
---
# §9 架構決策

一決策一檔住 [decisions/](decisions/)（`ADR-NNNNN-<slug>.md`；accepted 後 body 不可變、翻案走 supersedes）；索引＝[DECISIONS-INDEX](../generated/DECISIONS-INDEX.md)（機器生成）。body 節形＝背景／決策驅動因子／考慮過的替代案／決定／後果／翻案觸發器。

## 9.1 E5 AI-ADR 形制與對映表

AI-ADR 不另開號空間：rev6 五碼 id＋frontmatter `rad_ai: [E5]`＋標題前綴「AI-ADR」；AI 特定考量以五個子節承載、對應 RAD-AI reference 七欄如下（欄序＝reference 七欄順序、英文名冊住 `tools/docsync/book.py` 的 E_SUBSECTIONS；「考慮過的替代案」屬 body 節、非 AI 特定子節）。目前無 AI 元件（截至 2026-09-03）、AI-ADR 零份；本層隨 AI 功能刀填入。流程層＝無獨立檔：模型分派、effort、編排形制等流程層決策照一般 ADR 立檔、不帶 `rad_ai`（ADR-00007 決定 2：本表射程＝系統層，流程層是類比、偏離以子節首句「類比張力：」宣告、不入本表）。

| AI 特定考量子節（中文改寫） | reference 欄序 |
|---|---|
| 資料集特性 | 2 |
| 公平與偏誤取捨 | 3 |
| 模型生命週期 | 4＋5 |
| 可解釋 | 6 |
| 法規合規 | 7 |
| （body 節）考慮過的替代案 | 1 |
