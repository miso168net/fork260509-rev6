---
id: "LL-00104"
rule_id: "RL-0043"
promotion_surface: none
---
LL-00104｜審查員之變異探針以受測檔所在目錄推算「假 repo 根」，把兩份 locale 副本建進 base-web 工作樹；審查員自以 porcelain 雜湊比對發現並即刪，零後續影響（008 刀 U14）

**徵狀**：008 刀 U14 碼品質第 2 輪審查員為 zh-tw-lint 之變異準備合成 repo 根（該工具以 repo 相對路徑讀兩檔 locale）。探針把假根建在 `base-web/src/locales/langs/root/`，內含與工作樹逐字相同之兩份 locale 副本。審查員於第一批變異後比對 `git -C base-web status --porcelain` 之雜湊與審查前基準不符，因而發現，立即刪除並在回報中自陳。其間未跑 typecheck；`src/locales` 無 `import.meta.glob`、不在路由外掛射程，路由產物零變動。主線收尾以 `status --porcelain --untracked-files=all` 與 agent 面掃描復核，確認無殘留。

**成因**：
1. 探針以「受測檔所在目錄＋固定子目錄名」推算假根；基準目錄取錯，就落在真工作樹內。寫入前也沒有斷言目標路徑位於 agent 專屬暫存目錄下。
2. 單元定義之變異紀律只點名「不在 `base-web/src/views` 增刪檔」——該子樹新增檔會觸發路由外掛重算。其餘子樹沒有同等明文，探針作者只守住被點名的那一棵。

**處置**：審查員自刪假根，並把探針改為只寫本 agent 專屬目錄、加路徑斷言。主線收尾①以 porcelain（含未追蹤全列）與 agent 面掃描核得零殘留、零後續影響，記入收單訊息。

**晉升面**：none。判準同 RL-0043（review agent 只讀不寫 repo 檔）；本次由審查前後之 porcelain 雜湊比對攔下，守法在單元定義之變異紀律句與該比對。

**再犯面與守法**：
- 單元定義之變異紀律句，射程寫成整棵工作樹（含兩子庫），不只點名會觸發外掛之子樹：副本、合成 repo 根與探針輸出一律建在 agent 專屬暫存目錄下，寫入前斷言目標路徑之前綴。
- 審查與 fix agent 收尾以 `git status --porcelain --untracked-files=all` 之雜湊比對開工前基準；主線收尾①照同形復核。
