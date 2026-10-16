---
id: "LL-00094"
rule_id: "RL-0084"
promotion_surface: rules
recurrence_of: "LL-00067"
---
LL-00094｜RL-0084 擴面後第一刀的簿記後驗仍漏兩處：contracts 指定入收單事件的反向確認只核了一節，「假述零殘留」以 lint／check 全綠代證（spec-compliance-007 抓到；2026-10-16）

**徵狀**：
- 007 刀 contracts code-gates 之 §8.3 指定六項反向確認「命令現算、結果入收單事件」；feature_close notes 只載 §8.2 所列三條（BL-00108／BL-00043／BL-00133）。零新依賴、migration 目錄恰三支、演進帳 entries 9 與 `next_id` 10 三項的結果只住 `c9be3eb` 訊息之 T105 ④⑤。perf 第四步 `18eebcb` 的 RL-0084 後驗只照 §8.2 判「相符」。
- SC-014「機器枚舉之假述零殘留」的子句表承載命令與後驗⑤，皆以 `docsync lint`／`check` 全綠代證；lint 的 GT-06 只守時態，不含 spec FR-059 任一枚舉種子，該「相符」沒有機器證據。spec-compliance-007 run C 的 L10-1／L10-4 抓到；lens 以種子實跑補證 HEAD 零殘留。

**成因**：
- 後驗把讀到的第一處「收單事件註明」（§8.2）當成核對全集；§8.3 的「結果入收單事件」換了寫法，沒有被同一次核對涵蓋。LL-00067 守法①的 grep 樣式本可兩處都列出，這次沒有先列全集。
- RL-0084 只說「逐項核對」，沒寫「零殘留」類子句要用什麼當證據；lint／check 全綠看起來像機器證據，實際上不檢查舊詞。

**處置**：
- 三項反向確認的結果補記在 spec-compliance-007 的 review 事件 notes（feature_close notes 屬不可更正欄＝RUNBOOK §12c）；HEAD 現算仍成立。
- RL-0084 擴寫兩點（user 2026-10-16 裁定）。

**晉升面**：rules——RL-0084 條文補「contracts 以全檔中寫入／入收單事件各處之聯集為核對全集」與「假述零殘留類子句以 spec 所列種子實跑 `docsync errata`、不得以 lint／check 綠代證」。

**再犯面與守法**：
- ①後驗起手先列全集：`grep -n -E '收單事件|notes 記|feature_close' specs/<本刀目錄>/tasks.md specs/<本刀目錄>/contracts/*.md`（承 LL-00067 守法①），逐條對照 feature_close 欄與 notes；只核其中一節不算完成。
- ②「零殘留／零命中」類子句：對 spec 所列種子逐一跑 `python3 tools/docsync errata <詞>`，在 commit 訊息記每個種子的命中數與分流（現在式／史料面／已拍板面）；lint／check 全綠只證時態與生成面，不證舊詞零殘留。
