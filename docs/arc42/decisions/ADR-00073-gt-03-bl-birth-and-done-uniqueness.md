---
id: "ADR-00073"
title: GT-03 加 BL 唯一性腳——同一 BL 號全帳至多誕生一次、至多收一次（ERROR）
date: 2026-10-04
status: accepted
supersedes: []
superseded_by: []
provenance: "006 authz-governance 刀收刀簿記之坑（feature_close 重記窗內已由 misc 事件誕生之 BL 的風險、閘零反應；LL-00063）；user 2026-10-04 裁定（maint-backlog-137-133 開批題②：補腳）；前代無對應：rev5 docs-sync 之 `Lint04` 對 backlog_add 只驗 phantom（BACKLOG git 史查無即紅）、對 backlog_done 只驗宣稱完成卻未刪列，無同號重複誕生／收單之檢查"
tags: [governance, gate, events, backlog]
---

## 背景

BACKLOG 淨流量由 `tools/docsync/events.py` 的 `metrics` 現算：最近三個 feature_close 自然窗內，逐筆事件加總 `backlog_add` 條數減 `backlog_done` 條數，不去重。收刀簿記寫 feature_close 時，若把「本窗內已由 misc 事件 `backlog_add` 誕生過」的 BL 再記一次，該窗就多算一筆。

這筆錯一旦 commit 就改不掉：事件帳只增不改，`backlog_add`／`backlog_done` 也不在 erratum 可更正的欄集（`ERRATUM_FIELDS`＝merge／pins.web／pins.api／commit／adrs／probe）。006 沒重記，是因為其 spec（FR-046 與驗收情境 5）令 BL-00137／BL-00138 之 `backlog_add` 由本刀第一筆事件承載，tasks 的收刀條與 contracts 也寫明 feature_close 之 `backlog_add` 為零；沒有預寫的刀，只能靠收刀時人工對照。

GT-03 現行的 BL 腿只驗存在性（`backlog_done`、review 分流與兩卷帳本列號皆須先經 `backlog_add` 誕生；BL 走事件制、ADR 刻意不設同型不變式＝ADR-00025），不驗重複。2026-10-04 實核事件帳：誕生號 137 個，重複誕生 0、重複收單 0。

## 決策驅動因子

- 重記使治理指標永久偏差，且無更正管道，只能在 commit 前擋。
- BL 號永不回收（RL-0050），同一號合法地誕生或收單兩次的情境不存在；重複恆為錯。
- 歷史零重複，新腳上線即綠、不需豁免。

## 考慮過的替代案

1. **只寫 LESSONS、靠收刀時人工注意或 spec 預寫**——006 前例可行但依賴 spec 恰好寫明；否決（user 2026-10-04 裁定②）。
2. **改 `metrics` 去重（按 BL 號集合計數）**——指標算對了，但事件帳（事實源）仍留一筆不實的誕生或收單紀錄；是掩蓋而非防止。否決。
3. **只驗 `backlog_add`**——`backlog_done` 重記同樣使淨流量多減一筆；否決。

## 決定

1. GT-03 增一腳：全部事件的 `backlog_add` 中同一 BL 號出現超過一次＝ERROR；`backlog_done` 同。跨事件與單一事件內的重複皆算。錯訊指出首見處，並提示修法（刪去新增列中的重記號；窗內已由 misc 誕生或收單者，feature_close 不得重記）。
2. 不設豁免。
3. 既有閘加腳，閘數不變。

## 後果

- 正面：重記在 pre-commit 當場擋下，淨流量不再可能被永久多算或多減。
- 負面：無新增成本；BL 要「重開」時本來就須另配新號（RL-0050）。

## 翻案觸發器

- 事件 schema 引入可合法重複之 BL 欄語意（例：允許同號重開）時。
