---
id: "LL-00072"
rule_id: "none：守法改由單元定義常駐段承載（主線組裝每支單元定義必烤）；是否升 RULES（implementer／review 範圍）屬調規，留 007 刀收刀前提請 user 裁定"
promotion_surface: none
recurrence_of: "LL-00055"
---
LL-00072｜LL-00055 的守法只寫「寫進後續單元定義」，主線組 007 刀 U5 單元定義時漏烤——同機制再犯兩發：讀者交易持列鎖時斷言 panic、並發案對手任務持鎖期間 panic，守衛 Drop 互鎖卡死而不轉紅（007 刀 U5）

**徵狀**：007 刀 U5 兩處。①implementer-3 補做判準變異（`last_set_at` 加列鎖）首跑：斷言在讀者交易仍持列鎖時 panic，守衛 Drop 的 DELETE 等那把鎖，cargo 逾時 rc 124、無 FAILED。②碼品質審查第 3 輪以探針（等鎖判準改為永不成立）實證 `sys_token` 並發三序案：`await_lock_wait` 的 assert 與中途 `expect` 在換發側仍持列鎖、撤票側任務交易未收時 panic；capture 模式 60 秒被殺、全程無訊息。該案要抓的回歸（過濾條件或鎖讀被改壞）因此會讓全量跑次掛死、拿不到紅因。

**成因**：機制同 LL-00026／LL-00037／LL-00055——current-thread runtime 下交易未收即 panic，rollback 只排進連線佇列；守衛 Drop 阻塞等鎖，runtime 推不動那筆 rollback。LL-00055 的守法「寫進本檔與後續單元定義」要靠主線組裝時手動帶入；007 刀 U5 的單元定義沒帶（同刀預組的 U6、U7 也沒帶）。agent 只在部分案例自發照做（`sys_user` 鎖讀兩案、`sys_pwd_custody` 讀案）；並發案多出「對手任務持鎖」這一形，更不在既有守法的字面內。

**處置**：①讀案改為先 rollback 兩筆交易再斷言（implementer-3）。②三序案改為兩段：持鎖段只記紅因；收場段先放掉主線手上的交易，再收對手任務（逾時就 abort，並觀測其後端退出交易），最後才紅。探針七發皆在數秒內 FAILED、帶出紅因（碼品質 fix-3）。③主線自 U6 起把守法烤成單元定義的常駐不可違反項（implementer／review／fix 三面）：真庫案的斷言、`expect`、`unwrap` 一律放在交易收場之後；並發案對手任務持鎖時，先收場（主線交易 commit 或 rollback、對手任務 join 或 abort）再紅。

**晉升面**：none——同機制已四犯（LL-00026→LL-00037→LL-00055→本則），守法改由單元定義常駐段承載；是否升 RULES（經 `docsync rules emit` 自動烤入、不再靠主線記得）屬調規，留收刀前提請 user 裁定。

**再犯面與守法**：凡 LESSONS 守法寫成「寫進後續單元定義」者，主線組裝每支單元定義時以 grep 核其在場（本則關鍵字＝「交易收場之後」）。跑測試若零輸出長時間不動，先查 `pg_stat_activity` 的 idle in transaction 連線，再懷疑框架。
