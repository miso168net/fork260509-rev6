---
id: "LL-00081"
rule_id: "RL-0067"
promotion_surface: none
---
LL-00081｜子庫新檔於 commit 前直跑 fork-delta-lint 恆綠：掃描面取 `git diff --name-only <基線>`、看不到未追蹤檔，新檔頭標記之 rc 0 與拔標記自證在此時點皆空轉（007 刀 U14）

**徵狀**：007 刀 U14（T069）在 base-web 新增四支檔（兩支 `.d.ts`、兩支 `.ts`）。T069 的 DoD 寫兩項：`python3 tools/fork-delta-lint.py` rc 0；新檔 `.ts`、`.d.ts` 各一支同形自證（暫刪檔頭標記行 → 報缺檔頭標記）。implementer 先紅時發現，拔掉檔頭標記的新檔直跑照樣 rc 0，新檔計數停在既有的 19 支——四支新檔根本不在掃描面。

agent 不得 `git add`（含 `-N`），於是改寫一支 harness：載入原工具，只把 `changed_files` 換成「原 diff ∪ `git ls-files --others --exclude-standard`」（同 pathspec、同濾網），其餘判定原樣，零 git 寫入。紅綠與自證皆在 harness 上取得（23 支）。規格對照與碼品質審查也各自另證（記憶體內逐檔判、harness 實跑）。

**成因**：
1. `changed_files` 以 `git diff --name-only <基線>` 取掃描面。工作樹對基線之差只含已追蹤檔，未追蹤的新檔要到子庫 commit 後才進掃描面。
2. 007 刀 spec 契約 code-gates 之 §1.4 對 `A..HEAD` 形之變更檔集斷言已寫明「排在子庫 commit 之後」；§1.5 的拔標記自證與各 task DoD 的「fork-delta-lint rc 0」卻沒有同樣的時點限定。單元內（commit 前）照字面跑，即得空轉綠。
3. 外層 pre-commit 的 fork-delta 段在 base-web pin bump 時跑，此時新檔已入子庫 commit，真閘並未失守；失準的是單元內 DoD 的宣稱。

**處置**：U14 收尾於 base-web commit 後、外層 commit 前實跑 fork-delta-lint，並對新檔 `.ts`、`.d.ts` 各一支拔檔頭標記自證（報缺 → 寫回 → porcelain 回基準），結果入外層收單 commit 訊息。

**晉升面**：none。判準同 RL-0067（紅證須打在掃描面確實看得到的實例上）；守法落在單元定義與主線收尾程序。

**再犯面與守法**：
- 含 base-web 新檔之單元，單元定義烤句：新檔於子庫 commit 前，fork-delta-lint 之 rc 0 與拔標記自證一律以「併入未追蹤檔」之 harness 取得（零 git 寫入）；直跑結果不作新檔之證據。
- 主線收尾：base-web commit 之後、外層 commit 之前實跑 fork-delta-lint，新檔逐副檔名各取一支拔標記自證，再落外層 commit。
