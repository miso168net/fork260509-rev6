---
id: "LL-00110"
rule_id: "none：Claude Code harness 對 subagent 寫檔之限制（平台行為之事實），守法住本檔"
promotion_surface: none
---
LL-00110｜單元定義要 implementer 把 report 全文另存 `report.md` 供審查段讀：harness 拒絕 subagent 寫 report 類檔，審查段所指之讀檔路徑全數落空（008 刀 U17）

**徵狀**：008 刀 U17 Run A 之單元定義要四支 implementer 把 StructuredOutput 之 report 逐字另存 `report.md`，並寫明「審查段收不到 StructuredOutput、只讀檔」。甲、乙b 兩支呼叫 Write 寫 `report.md` 皆被 harness 拒絕，訊息為「Subagents should return findings as text, not write report files」；乙a、丙從前支轉交之 report 得知、未再嘗試；四支都沒有改用 Bash 繞過，甲與丙在 escalations 申報。規格對照審查改讀本 run 之 workflow journal 取回四份 report 原文；dod 斷言檔、log 與表檔皆照常落檔。

**成因**：Claude Code harness 不准 subagent 以 Write 寫 report 類檔（findings 應以回傳文字交付）。骨架只把前支 report 傳給後支 implementer，不傳給審查員；單元定義另以落檔補這一段，而這條路被 harness 擋下。

**處置**：主線於收尾①由 run 結果之 `implReports` 轉存四份 report；續跑形單元改寫為「report 只經 StructuredOutput 回傳；審查員需讀其原文者讀本 run 之 workflow journal，讀不到即以 diff 與 DoD 檔判」。

**晉升面**：none（平台行為之事實；守法住本檔）。

**再犯面與守法**：
- 單元定義不要求 subagent 寫 report 類檔；要交給審查段的實得，落成斷言腳本、log 與資料表檔。
- 審查段需要 implementer 之 report 原文時，從本 run 之 workflow journal 讀，或由骨架把 `implReports` 傳進審查 prompt（改骨架屬 `tools/orchestration` 之變更、另行處理）。
