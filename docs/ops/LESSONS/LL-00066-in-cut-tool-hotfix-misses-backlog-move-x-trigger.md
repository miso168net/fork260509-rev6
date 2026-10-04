---
id: "LL-00066"
rule_id: "none：BACKLOG 檔頭「動 X」口徑已定義到期；本坑＝刀內順手改工具時沒人回掃觸發欄，守法寫於本檔"
promotion_surface: none
---
LL-00066｜刀內順手熱修某工具檔，沒回頭掃 BACKLOG 觸發欄：以「下一支動該檔」為觸發的條目到期了卻沒人接（BL-00137；006 刀 ec8c8ff、2026-10-03）

**徵狀**：BL-00137（壓縮 hook 的背景 task 目錄 fallback 在 macOS 推錯暫存根）於 006 brainstorm 定稿顆 `e9f5525`（2026-10-01）記帳，觸發＝「下一支動 `.claude/hooks/compact-hook.py` 可執行碼之批」。006 刀內 `ec8c8ff`（2026-10-03）改了同檔 `precompact()` 手動觸發分支的注入字串（可執行語句、改變 hook 輸出），觸發已到期。006 收刀時的承接與反向確認清單只列 BL-00047／BL-00108，BL-00137 沒被接住；直到 007 前 BACKLOG 體檢 v8 才查出，改由 maint-backlog-137-133 補收。

**成因**：
- 「動 X」型觸發沒有機器偵測：commit 改到 X 時，沒有任何閘或流程步驟去對 BACKLOG 觸發欄比對 X。
- `ec8c8ff` 是刀內對工作流程的熱修（壓縮不是停點），不屬任何 task，也就不在 tasks 的承載盤點裡。
- 刀的收刀反向確認清單由 spec 預先寫定，只涵蓋當時已知會被碰到的條目；刀內臨時碰到的檔不會自動進清單。

**處置**：v8 體檢以 `git merge-base --is-ancestor` 實證 `e9f5525` 早於 `ec8c8ff`、兩者皆在 HEAD，判為已到期之補收；maint-backlog-137-133 收單並刪列。

**晉升面**：none——目前只記守法；同形再犯即評估把「改動檔 × BACKLOG 觸發欄路徑」比對做成閘腿。

**再犯面與守法**：
- ①任何 commit 改到工具、hook 或測試設施的可執行碼時，先以檔名（basename）`grep -n -F '<檔名>' docs/ops/BACKLOG.md docs/ops/BACKLOG-DEFERRED.md`，子庫檔另以子庫相對路徑再掃一次；觸發欄可能只寫檔名或模組名，以完整路徑 grep 會漏命中。
- ②命中且屬「動 X」型：同批處置（收掉，或在收單訊息寫明為何不收並改寫觸發），不留給下一次體檢。
- ③刀收刀前的承載體檢，除 spec 列名的反向確認外，另以本刀改動檔清單對 BACKLOG 觸發欄掃一次。
