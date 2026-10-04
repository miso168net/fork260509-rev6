---
id: "LL-00069"
rule_id: "RL-0011"
promotion_surface: none
recurrence_of: "LL-00006"
---
LL-00069｜改某一端點的案數時，勘誤種子用了帶前綴的長片語——「分頁四案」改成「五案」了，同一端點另一種寫法「app 面四案」卻漏掃（maint-readout-errata 補；2026-10-05）

**徵狀**：spec-compliance-006 修單 rust-api `5f123a6` 替 get-archived-policies 補第⑤發，把模組 doc 兩處與案 doc 的「分頁四案」改成「五案」；commit 訊息記「errata 七組改動字面零命中」。同檔 `verify_get_archived_policies` 的 doc 仍寫「分頁參數收斂之 app 面四案」，直到 BACKLOG 體檢 v9 掃漏才抓到。

**成因**：
- 當時的勘誤種子是 `errata '分頁四案'` 與 grep「get-archived-policies 分頁四案」，都是「主詞＋數量詞」的長片語，不是舊數量詞本身。
- 同一件事在同檔另有一種說法（「app 面四案」），長片語匹配不到。
- RL-0001 要求自擬樣式只取最短公共子串，RL-0011 種子④要求掃舊數量詞字面；這次兩條都沒照做，與 LL-00006（只掃名稱、漏掃數量詞）同型。

**處置**：maint-readout-errata 把該句改為「app 面五案」，以 `errata 'app 面四案'` 復掃，rust-api 工作樹零命中。

**晉升面**：none——RL-0001 與 RL-0011 條文已涵蓋；記為 LL-00006 之再犯。

**再犯面與守法**：
- 改某一標的的案數或件數時，勘誤種子一律用裸數量詞（「四案」「三支」「兩條」），不以「主詞＋數量詞」的長片語代替。
- 命中後逐筆依主詞篩選：同一標的者改；他標的者不動，並在 commit 訊息列明不動的理由。
