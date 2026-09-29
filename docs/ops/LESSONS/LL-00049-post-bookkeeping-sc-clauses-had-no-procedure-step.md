---
id: "LL-00049"
rule_id: "RL-0084"
promotion_surface: rules
---
LL-00049｜spec 標「收刀面於簿記 commit 後驗」的 SC 子句沒有任何收刀程序步驟承接——005 刀收刀漏了 NOTES 下一步指向與淨流量分型兩處（spec-compliance-005 L7-3 抓到；2026-09-30）

**徵狀**：005 刀 spec SC-016 與 US6-AS6 要求 NOTES 下一步指 006、收刀事件 notes 記淨流量值與揭露型／新欠型分型；T103 明文延至「收刀簿記後驗」，但簿記 68ca376 及其後各顆 commit 皆無此驗證紀錄，兩處皆漏，直到規格對照輪才抓到。003 刀與 004 刀 spec 同用此子句形、同樣無驗證紀錄。

**成因**：收刀程序（CLAUDE.md §2 簿記三步＋perf 第四步、RL-0053）只定事件、NOTES、generate 與牆鐘；spec 把部分 SC 子句推到簿記 commit 之後才可驗，卻沒有任何步驟承接「之後」那一次核對，tasks 的延後註記就此落空。

**處置**：規格對照輪報告逐欄補核 005 刀收刀面；淨流量分型補記於該輪 review 事件 notes（notes 屬不可更正欄，依 RUNBOOK §12c 以後續事件說明），NOTES 下一步於該輪簿記改正。

**晉升面**：rules——RL-0084：perf 第四步那顆 commit 內逐欄核對簿記後驗子句並寫入 commit 訊息，不符者引承載或轉 BL。

**再犯面與守法**：spec 或 tasks 出現「收刀後驗」「簿記後驗」一類延後驗證字樣時，收刀 perf 第四步那顆 commit 照 RL-0084 逐欄核對；延後驗證若不在任何程序步驟上，等於沒有驗證。
