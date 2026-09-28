---
id: "LL-00040"
rule_id: "none：hook 設計面踩點、非流程規則可承——判準與緩解寫在 `.claude/hooks/compact-hook.py` 檔頭與本檔，寫新 hook 時照本檔逐事件取證即可"
promotion_surface: none
---
LL-00040｜以為 hook 輸入一律帶 `agent_id`、拿它過濾「只作用於主線」，但 PreCompact 與 SessionStart(compact) 的輸入根本不帶這欄——workflow agent 自身壓縮時，主線的壓縮指示與回灌照樣進到 agent（maint-backlog-126）

**徵狀**：本機壓縮 hook 自 2026-09-25 起以「hook 輸入帶 `agent_id`＝subagent 內觸發＝靜默」一條判準涵蓋三種事件（PostToolUse 提醒、PreCompact 注入、SessionStart(compact) 回灌），並記入 BACKLOG 與 memory 當作已成立的事實。入版控前以 Claude Code 2.1.283 執行檔逐事件核對，先發現 PreCompact 那一支的判準從未生效；本批 final holistic review 再以 2.1.284 取證，發現 SessionStart(compact) 也一樣。結果是：workflow agent 的 context 觸及自動壓縮門檻時，兩支 hook 照跑，主線座標、主線進度表的 ⑧、「壓完直接接續被打斷的那一步」照樣併入該 agent 的壓縮指示與壓後 context。實際上 agent 很少長到門檻，所以一直沒出事。

**成因**：hook 輸入的共通欄位由同一個組裝函式產生，但 `agent_id` 只在呼叫端傳入工具呼叫脈絡時才會填上。PostToolUse 有傳；PreCompact 與 SessionStart 只傳了 session 與 cwd，這欄因而恆缺。壓縮流程對 SessionStart(compact) 只略過 delegatedObservation 型 subagent，一般 workflow agent 照跑；PreCompact 的 stdout 也只對同一型丟棄。另外，workflow agent 壓縮時 hook 收到的 `session_id`、`transcript_path` 與主線同值（執行檔所見：agent 側的 session 由主線 session 衍生、id 取自主線），所以輸入面沒有任何欄位分得出「誰在壓縮」。

**處置**：precompact 與 rehydrate 兩支都在輸出文首放主線限定句，要求摘要者在被派發 agent 的對話裡忽略整段。實作顆一度另加「auto 觸發而主線 context 低於 0.5×min(視窗, 200k) 即靜默」的數值門檻，final holistic review 找出多條誤殺主線真壓縮的路徑：主線 transcript 末筆若是 `<synthetic>` 零 usage 列（API 錯誤、No response requested.）會被讀成 context＝0；此外還有 PCT 覆寫、伺服器端預壓比例、transcript 末筆 usage 落後於當下 context 幾條。誤靜默主線（丟失全部注入）遠比誤注入 agent（有限定句兜底）嚴重，故收單顆拿掉該門檻，只留限定句。remind 的 context 讀數另外跳過 `<synthetic>` 與零 usage 列，免得級距被誤歸零、重複提醒。

**晉升面**：none——本坑屬 hook 設計取證，不是可條文化的流程紀律。

**再犯面與守法**：寫或改任何 hook，凡要依賴輸入欄位做判斷（尤其 `agent_id`、`agent_type`、`session_id`），都要**逐事件**到執行檔或實跑輸入取證，不可從另一個事件類推；取證結論連同版本號寫進 hook 檔頭。為了擋 agent 而設的任何門檻，先證它在主線的每種觸發情境下都不會誤殺，證不了就寧可不設。記入 memory 或 BACKLOG 的「機制事實」，也要標註是哪個版本、哪個事件實證過的。
