---
id: "LL-00045"
rule_id: "none：fork-delta 標記寫法細節，判準住 tools/fork-delta-lint.py 與憲法 §III"
promotion_surface: none
---
LL-00045｜在 base-web 跨多行的元素標籤裡加屬性，修改型的 `原行:` 標記沒有位置可放（005 刀、2026-09-28）

**徵狀**：修改型改動須在同塊標一行 `原行:`（憲法 §III、fork-delta-lint 驗），但改動落在一個跨多行的元素標籤內——屬性之間不能插註解，標記無處可放。

**成因**：Vue 模板的元素標籤內不能放 HTML 註解；fork-delta 的修改型標記又要求與改動落在同一塊。

**處置**：標記放在元素上方，並讓改動落在同一塊中一條真實被替換的基線行（照 base-web 管理頁既有 `原行: />` 的寫法），lint 通過。

**晉升面**：none——寫法細節，判準在 lint 與憲法。

**再犯面與守法**：要往多行標籤加屬性前，先在 base-web 找既有同形先例（`grep -rn '原行: />'`）照其結構寫；改完跑 `python3 tools/fork-delta-lint.py` 自驗。
