---
id: "LL-00040"
rule_id: "none：hook 設計面踩點、非流程規則可承——判準與緩解寫在 `.claude/hooks/compact-hook.py` 檔頭與本檔，寫新 hook 時照本檔逐事件取證即可"
promotion_surface: none
---
LL-00040｜以為 hook 輸入一律帶 `agent_id`、拿它過濾「只作用於主線」，但 PreCompact 的輸入根本不帶這欄——workflow agent 自身壓縮時，主線快照照樣被注入（maint-backlog-126）

**徵狀**：本機壓縮 hook 自 2026-09-25 起以「hook 輸入帶 `agent_id`＝subagent 內觸發＝靜默」一條判準涵蓋三種事件（PostToolUse 提醒、PreCompact 注入、SessionStart 回灌），並記入 BACKLOG 與 memory 當作已成立的事實。入版控前以 Claude Code 2.1.283 執行檔逐事件核對，才發現 PreCompact 那一支的判準從未生效：workflow agent 的 context 觸及自動壓縮門檻時，hook 照跑，其 stdout（主線座標、主線進度表的 ⑧、「壓完直接接續被打斷的那一步」）照樣併入該 agent 的壓縮指示。實際上 agent 很少長到門檻，所以一直沒出事。

**成因**：hook 輸入的共通欄位由同一個組裝函式產生，但 `agent_id` 只在呼叫端傳入工具呼叫脈絡時才會填上。PostToolUse 有傳，PreCompact 只傳了 session 與 cwd，這欄因而恆缺。更麻煩的是，workflow agent 與主線共用同一個 session 物件，兩者壓縮時 hook 收到的 `session_id`、`transcript_path` 完全相同，輸入面上沒有任何欄位分得出「誰在壓縮」。只有 delegatedObservation 型的 subagent 會被呼叫端丟棄 stdout，一般 workflow agent 不在此列。

**處置**：precompact 改設兩道緩解：①注入文首加主線限定句，要求摘要者在被派發 agent 的對話裡忽略整段 ②auto 觸發時，若 transcript 末筆主線 usage 低於 0.5×min(視窗, 200k)（主線不可能在此壓縮），hook 靜默。「主線 context 也大、同時 agent 觸頂」的情形仍無法以機器區分，殘餘風險由①承擔。判準與實證都寫進 hook 檔頭，測試另補「auto＋主線過小＝靜默」的正反案。

**晉升面**：none——本坑屬 hook 設計取證，不是可條文化的流程紀律。

**再犯面與守法**：寫或改任何 hook，凡要依賴輸入欄位做判斷（尤其 `agent_id`、`agent_type`、`session_id`），都要**逐事件**到執行檔或實跑輸入取證，不可從另一個事件類推；取證結論連同版本號寫進 hook 檔頭。記入 memory 或 BACKLOG 的「機制事實」，也要標註是哪個版本、哪個事件實證過的。
