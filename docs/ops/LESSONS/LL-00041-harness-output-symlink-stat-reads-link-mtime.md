---
id: "LL-00041"
rule_id: "none：監看命令的取證寫法、非流程規則可承——寫對命令即可，判準住本檔"
promotion_surface: none
---
LL-00041｜用 `stat` 看背景 task 輸出檔的 mtime 判斷卡住，讀到的是 symlink 本身的時間、誤報「很久沒動」（005 刀收尾期、2026-09-28）

**徵狀**：主線以 `stat` 查背景 task 的輸出檔多久沒更新，時間停在建檔時刻、看似卡死；實際工作仍在寫。

**成因**：harness 的 task 輸出檔是指向實檔的 symlink；`stat` 預設不跟隨連結，回的是連結本身的 mtime（建立後不再變）。

**處置**：改用 `stat -L`（跟隨連結）讀實檔 mtime，誤報消失。

**晉升面**：none——屬監看命令寫法，寫對命令即可。

**再犯面與守法**：凡以 mtime 或大小判斷 harness 產物（task 輸出、journal、agent 檔）是否在動，一律 `stat -L` 或先 `readlink -f` 取實檔；下判斷前先 `ls -l` 看是不是連結。
