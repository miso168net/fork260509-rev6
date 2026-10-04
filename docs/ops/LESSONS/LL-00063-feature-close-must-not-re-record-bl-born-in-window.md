---
id: "LL-00063"
rule_id: "none：機器承載＝GT-03 之 BL 唯一性腳（ADR-00073），不另立流程規則"
promotion_surface: gate
---
LL-00063｜收刀簿記若把窗內已由 misc 事件誕生的 BL 再記進 feature_close 的 `backlog_add`，淨流量就多算一筆，而且事後改不掉——006 刀靠 spec 預寫才避開、閘零反應（2026-10-04 記）

**徵狀**：006 刀新記的 BL-00137／BL-00138 在刀內已由 2026-10-02 的 misc 事件 `backlog_add` 誕生（006 刀 T003）。若收刀 feature_close 照「本刀新記的 BL」去填 `backlog_add`，兩號就會再記一次。006 沒出事，是因為事先寫好了：spec FR-046 令「BL-00137／BL-00138 之 `backlog_add` …MUST 由本刀第一筆 events 事件承載」、驗收情境 5 寫「BL-00137／BL-00138 之 `backlog_add` 已由本刀第一筆事件帶入」，tasks 的收刀條與 contracts 也寫明 feature_close 之 `backlog_add` 零。收刀當下回頭驗證時才確認：重記與否只靠人照預寫去填，GT-03 對重記零反應。

**成因**：
- `tools/docsync/events.py` 的 `metrics` 算淨流量時，逐筆事件加總 `backlog_add` 條數減 `backlog_done` 條數、不去重；同一號記兩次就算兩次。
- GT-03 的 BL 腿只驗存在性（引用之號須先誕生），不驗重複誕生或重複收單。
- 事件帳只增不改，`backlog_add`／`backlog_done` 也不在 erratum 可更正的欄集（`ERRATUM_FIELDS`），重記一旦 commit 就永久偏差。

**處置**：006 刀 feature_close 照預寫把 `backlog_add` 寫空集；maint-backlog-137-133 於 GT-03 補 BL 唯一性腳：同一號全帳 `backlog_add` 至多一次、`backlog_done` 至多一次，違者 ERROR，首見處與重記處以事件帳行號指出（ADR-00073；事件帳實核 137 個誕生號、零重複，上線即綠）。

**晉升面**：gate——GT-03 唯一性腳（ADR-00073）。

**再犯面與守法**：
- ①feature_close 的 `backlog_add` 只收「本窗內尚未由任何事件誕生」的號；窗內若有 GT-03 在途 WARN，以在途全集為準（005 刀前例）。
- ②`backlog_done` 同理：窗內維護批已收單的號，feature_close 不再收一次。
- ③重記會被 GT-03 擋下；錯訊指出首見處，刪去新增列中的重記號即可。
