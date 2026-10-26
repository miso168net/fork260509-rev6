---
id: "LL-00106"
rule_id: "RL-0008"
promotion_surface: rules
recurrence_of: "LL-00105"
---
LL-00106｜tasks DoD 要求「八支新檔 eslint rc 0」，而 base-web 之 eslint 設定只收 .vue：兩支 .ts 新檔只得「File ignored」警告、rc 0 恆綠；RL-0008 擴寫後首次派發前核對未列此類綠斷言（008 刀 U15）

**徵狀**：008 刀 U15 之 T133～T135 與 T141① 之 DoD 要求容器內 `pnpm exec eslint`（不帶修正旗標）對本單元八支新檔 rc 0。implementer 與兩輪審查實跑皆 rc 0，但兩支 .ts（`src/service/api/rev6-audit.ts`、`src/views/manage/audit/modules/use-audit-search-date-range.ts`）各得一則「File ignored because no matching configuration was supplied」警告：eslint 對這兩檔沒有判定。主線收尾以 `--max-warnings 0` 實證：.ts rc 1、.vue rc 0。兩支 .ts 另由 oxlint（0 warnings／0 errors）與 oxfmt 覆蓋，實害為零。

**成因**：
1. base-web 之 eslint 設定只收 .vue，.ts 由 oxlint 承擔；eslint 對射程外之檔只發警告、不改退出碼。DoD 把三支工具並列於同一檔集，沒有逐檔核每支工具之射程。
2. 同日 008 刀 U14 收尾擴寫之 RL-0008，已要求派發前對「預期轉紅、計數與零命中」斷言逐條指出判定點並核射程。主線派發前清冊只挑 grep 類計數與預期紅變異，把「工具 rc 0 對一組檔」當成一般綠檢查略過：條文涵蓋此形，套用時分類過窄。同根前三形為 LL-00082、LL-00085、LL-00105。

**處置**：子庫與收單訊息如實記「eslint 實質只覆蓋六支 .vue，兩支 .ts 由 oxlint／oxfmt 承擔」。user 2026-10-27 裁定 RL-0008 再擴寫兩處：
- rc 0／零錯誤類綠斷言明列為零命中斷言，逐檔核射程（工具輸出 ignored、skipped、no matching configuration 類字樣＝射程外）。
- 派發前清冊以 DoD 子句全集為底，逐列填判定點。

**晉升面**：rules（RL-0008 擴寫；主線派發前 checklist）。

**再犯面與守法**：
- 派發前先把該單元每條 DoD 機械切成子句（以「；」分開），一子句一列，再逐列填判定點；不先分類再挑。
- 「工具 rc 0」類子句逐檔核射程：以該工具對受測檔集實跑一次，看有無 ignored、skipped 類輸出，或讀其設定之檔案樣式。射程外之檔改由實際覆蓋它的工具承擔，tasks 字面同改。
