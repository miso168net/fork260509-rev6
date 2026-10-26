---
id: "LL-00102"
rule_id: "RL-0012"
promotion_surface: code
---
LL-00102｜TDD 骨架之 unresolved 回傳形漏帶 implementer 之 `implStatuses`／`escalations`：成功形才帶，單元以 unresolved 收場時 `done_with_escalation` 之清單外待辦只剩 journal 可查（008 刀 U11）

**徵狀**：008 刀 U11 之 run 以 unresolved 收場（碼品質確認輪仍 2 blocker）。完成通知之回傳 `escalations` 為空陣列、無 `implStatuses` 欄；journal 中兩支 implementer 卻皆回 `done_with_escalation`，共帶 5 條清單外待辦（契約表判準數與 tasks 不符、`SystemJob::as_str` doc 射程、清單外舊現況句、下一單元回填參考等）。主線若只讀回傳即漏收；本次讀 journal 逐支取回。

**成因**：
1. `tools/orchestration/_sk_main.js` 之三個出口中，只有成功形以 implementer 回傳彙整 status 與 escalations；兩個 unresolved 形（規格對照段、碼品質段）只帶審查段 fix 迴圈之 escalations。
2. harness 只在成功形（案 6）斷言 implementer escalations 帶回；各 unresolved 案之 implementer 樁一律回 ok，漏帶與「本來就沒有」分不出。

**處置**：`_sk_main.js` 抽出 implementer status 與 escalations 之彙整件，成功形與兩個 unresolved 形同引；harness 案 9 之 implementer 樁改回 `done_with_escalation`，並斷言 unresolved 形逐支帶回 `implStatuses` 與 escalations（spec／quality 兩模式各驗一個 unresolved 出口）。以 U11 發射時之舊成品跑新 harness，兩模式各 2 項紅；以新骨架重組 U11 單元定義與入庫範例，兩模式皆綠。

**晉升面**：code（骨架與 harness）。判準同 RL-0012（`done_with_escalation`＝交付完成而附清單外待辦，照常進審查）；本坑在回傳面把該待辦弄丟，修在骨架、由 harness 機器守。

**再犯面與守法**：
- 修正前組裝之成品仍是舊形：以舊成品 resume 或續跑而以 unresolved 收場時，一律讀 journal、逐支取 implementer 之 status 與 escalations。
- 主線單元收尾①：回傳不是唯一來源；以完成通知之 agent 數對照 journal 之 result 行，逐支看 status，`≠ ok` 者取其 escalations。
