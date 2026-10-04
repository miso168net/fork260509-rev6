---
id: "LL-00070"
rule_id: "none：CLAUDE.md §5「不採信 agent 或自己的回報：一律 grep／實跑取證」已涵蓋；本坑＝把體檢底稿的指針搬進 NOTES 時沒有照做"
promotion_surface: none
---
LL-00070｜NOTES「下一步」的 ADR 指針照抄 agent 寫的體檢底稿、沒有打開 ADR 核對節名——「ADR-00044 後果兩款」實際住在該 ADR 的「翻案觸發器」節（maint-readout-errata 補；2026-10-05）

**徵狀**：
- NOTES「下一步」列 007 brainstorm 的輸入，其中一項寫「ADR-00044 後果兩款」。
- ADR-00044 的「後果」節三條都不是給 007 的義務；那兩款（使用者軟刪寫端須定「軟刪是否清指派」、指派寫端落地後複核 in-use／self-role 兩腿）是「翻案觸發器」節的前兩條。
- 007 brainstorm 照 NOTES 去「後果」節會找不到。BACKLOG 體檢 v9 把它列為 007 前唯一的必要項（X9）。

**成因**：
- BACKLOG 體檢 v8 的成文 agent 在工作檔裡寫了「ADR-00044 後果兩款」，節名寫錯。
- maint-backlog-137-133 把這組義務落進 NOTES 時，直接沿用底稿措辭，沒有打開 ADR-00044 看它的節構。
- lint 不檢查散文指向的 ADR 節名，錯誤一路帶到 007 的直接輸入。

**處置**：maint-readout-errata 把 NOTES 該句改為「ADR-00044 翻案觸發器前兩款」，`errata 'ADR-00044 後果'` 復掃：NOTES 與其餘現在式面零命中（只剩本檔與 LESSONS 索引之史述引用）。

**晉升面**：none——CLAUDE.md §5 已要求一律 grep 或實跑取證；本坑記錄的是「搬運指針」這個常被當成照抄、不被當成新寫的時點。

**再犯面與守法**：
- 把 ADR 款項、RULES 條號或活書節的指針寫進 NOTES、BACKLOG 或活書之前，先對原檔取證：`grep -n '^## ' <ADR 檔>` 確認所在節名，再 grep 該款原文確認在那一節。
- 指針來自 agent 產出（體檢、review、取證回報）時一樣適用，底稿本身不算證據。
