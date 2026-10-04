---
id: "LL-00067"
rule_id: "RL-0084"
promotion_surface: rules
recurrence_of: "LL-00049"
---
LL-00067｜收刀簿記只照 RL-0084 核 spec 的簿記後驗 SC 子句；tasks 收刀清單與 contracts 指定寫入收單事件的註記沒有步驟承接——006 刀 feature_close notes 漏了淨流量值與 BL-00132 兌現射程註記（spec-compliance-006 抓到；2026-10-05）

**徵狀**：006 刀收刀簿記 `2410cd4` 的 feature_close notes 缺兩項：
- tasks 收刀清單寫明「notes 記淨流量值」，notes 裡沒有淨流量字樣。
- 006 刀 spec 契約 code-gates 之 §8.2 要求「收單事件註明」BL-00132 的兌現射程。這段註記在 U18 `fa5b804` 的 commit 訊息裡已備妥，並標明「收單事件 notes 用」，卻沒有搬進 feature_close。

perf 第四步 `efea202` 照 RL-0084 逐欄核了 SC-014 五欄，皆符，但 SC-014 本來就不含這兩項。spec-compliance-006 run B 的 L7-1 抓到註記一項，淨流量一項由主線複核補報。

**成因**：
- LL-00049 晉升出的 RL-0084，只把「spec 標簿記後驗之 SC 子句」放進收刀程序。
- 另有兩處同樣指定 feature_close 該寫什麼，卻沒有任何步驟承接：tasks 收刀清單（標明不在 tasks 勾選清單內），以及 contracts 的「收單事件註明」。
- 收刀簿記照 CLAUDE.md §2 範本填欄、照 RL-0084 核 SC，兩邊都看不到這兩處。
- 005 刀漏記淨流量分型（LL-00049）是同一徵狀，這次只是缺口換了位置。

**處置**：
- 兩項補記在 spec-compliance-006 的 review 事件 notes。feature_close notes 屬不可更正欄，依 RUNBOOK §12c 以後續事件說明。
- 淨流量：006 收刀時點 rolling-3＝−20（004 窗 +1、005 窗 −11、006 窗 −10）。本刀自身是 T003 誕生 2 條、收刀收 5 條，合 −3，與 spec 摘要的預估相符。
- BL-00132 兌現射程：以 `fa5b804` 訊息 T083 ⑨ 的三點為準。
- RL-0084 擴為三類（user 2026-10-05 裁定），CLAUDE.md §2 兩處指針同批改。

**晉升面**：rules——RL-0084 改寫，核對射程擴至 tasks 收刀清單各項與 contracts 指定寫入收單事件之註記。

**再犯面與守法**：
- ①收刀 perf 第四步那顆 commit 內，先列出本刀 specs 目錄中所有「指定收刀事件內容」的句子：`grep -n -E '收單事件|notes 記|feature_close' specs/<本刀目錄>/tasks.md specs/<本刀目錄>/contracts/*.md`，再加上 spec 標簿記後驗的 SC 子句。逐項對照 feature_close 欄與 notes，結果寫進 commit 訊息。
- ②有漏記時，補在該顆 perf 事件的 notes，不改既有事件。
- ③tasks 或 contracts 寫「收單事件 notes 用」的備料（常放在收刀前承載體檢那顆的 commit 訊息），簿記時要原文搬進 notes，不能只留在 commit 訊息裡。
