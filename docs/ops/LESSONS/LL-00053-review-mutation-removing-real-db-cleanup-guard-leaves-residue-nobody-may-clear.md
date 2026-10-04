---
id: "LL-00053"
rule_id: "RL-0080"
promotion_surface: none
---
LL-00053｜審查員以「拆掉真庫清理守衛」做判準變異，變異本身就把殘留留在 dev 庫或 redis；而 agent 刪鍵與主線 `walkthrough-baseline.py restore` 都被 auto mode 權限分類器以「Modify Shared Resources」拒絕，殘留只能等 TTL 自然到期或交 user 處置（006 刀 U1；2026-10-02）

**徵狀**：006 刀 U1 碼品質審查員為證明新授權態矩陣案之 session 鍵零殘斷言承重，於容器內副本把該案 `SessionKeysGuard` 漏帶一個 sid（變異 G）——案如期轉紅，但被漏收的 `session:<sid>:last_activity` 留在 dev redis。審查員回報後試圖 `DEL`，被權限分類器拒絕；主線依 RUNBOOK §9c 以空基準跑 `python3 tools/walkthrough-baseline.py restore <基準檔>`，同樣被拒。此後走查基準 `diff` 恆報 redis `DBSIZE 0→1`、`session 0→1`，直到該鍵 TTL（約一小時）到期。

**成因**：判準變異跑在副本程式碼上，但副本連的是同一個 dev postgres／redis——「拆掉清理守衛」這類變異的紅證本身就是「殘留真的留下來了」，副本隔離的只有程式碼、隔離不了共用資料面。清理路徑又受 auto mode 權限分類器約束：直接刪共用庫或 redis 之資料（含經 restore 工具）屬「Modify Shared Resources」、被拒；分類器之拒絕及於同一結果之任何其他途徑，不得繞行。005 刀 U18 之 LL-00039 處置仍可由主線跑 restore，本坑發生時該路已不通。

**處置**：主線核實差異恰為該鍵（表 0 差、序列 0 差、redis 只差 1 鍵 1 前綴），且全量測試前後之 `diff` 完全相同（全量本身零新增殘留）；不再嘗試以任何途徑刪除，待 TTL 到期後補跑 `diff` 取 rc 0。

**晉升面**：none——RL-0080 已要求變異打在判準上；本坑是變異手法與共用資料面的交互，守法句寫進本檔與後續單元定義之審查 prompt。

**再犯面與守法**：單元定義之 implementer／審查 prompt 一律烤入——判準變異**不得**拆除或繞過真庫（dev postgres／redis）測試之清理守衛（帶界水位守衛、`SessionKeysGuard`、`OpLogRowsGuard`、`RowFixupGuard` 等）或令其 Drop 不跑；要證守衛或零殘斷言承重，改用「守衛照掛、把斷言之期望反轉」、或在無共用資料面之合成／記憶體面上做。變異若仍意外留下殘留，必須於回報逐鍵逐列指名（表、id、鍵名、TTL）。主線收尾若見殘留：redis 帶 TTL 者等到期；DB 列或無 TTL 之鍵＝列入 user 待辦、不得自行繞過分類器。
- 同根之另一觸發形（006 刀 U3；2026-10-02）：tasks 所定之主線殘列演練（以 psql 對 dev 庫植一列寫端授予形之殘列、全量測試後依 id 刪除並 setval 回植前值）於植列一步即被同一分類器以「Modify Shared Resources」拒絕——拒在執行前、dev 庫零變。演練之植入與拔除同屬改動共用資料面，拒絕及於同一結果之任何途徑，故不繞行：該 task 不勾、列入 user 待辦（由 user 決定放行該類命令或親自執行）；本刀同形之寫端面殘列演練與收刀前終態演練預期同受此限，排程時即列為 user 待辦項。
