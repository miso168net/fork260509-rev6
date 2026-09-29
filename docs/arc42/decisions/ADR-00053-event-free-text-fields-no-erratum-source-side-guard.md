---
id: "ADR-00053"
title: 事件帳自由文字欄（summary／reason／spec_supersessions[].note）不入更正欄位、寫錯以後續事件 notes 說明——三欄於寫入端套 notes 同一道守衛
date: 2026-09-29
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00035①③（000-r2 L1-06／L1-07／P3-P1；②④ 已收於 maint-backlog-35）；user 2026-09-29 裁定（006 前 BACKLOG 體檢題 1 ①，推翻 2026-09-21「①③ 留」）；前代出處：rev5:B-120（summary 寫錯無 erratum 出口；其「澄清事件帶 erratum_of」變體本決定不採）"
tags: [governance, events, docsync]
---

## 背景

`docs/ops/events.jsonl` 只准尾端 append。每筆事件的 `summary`、erratum 的 `reason`、feature_close 的 `spec_supersessions[].note` 會經 `_event_summary` 原文進 MILESTONES／STATE。寫錯時既有列不能改（GT-02 append-only 對比腿），這三欄也不在 `ERRATUM_FIELDS`（merge／pins.web／pins.api／commit／adrs／probe）裡。`notes` 在寫入端有 `notes_gt06_risks` 四腿守衛（行號引用、帳本 deep-link、per-machine 路徑、相對 markdown 連結），這三欄沒有——寫壞時要到生成的 MILESTONES.md 才被 GT-06 擋下，錯誤指向生成檔。

另有一筆舊帳：000-r1 review 事件（事件帳第 13 列）notes 記「confirmed 86＝修 75（含主線 R1-M01）／BL 9／ADR 1／none 2」，相加 87；報告 §5 記修 74、本身自洽。差額是主線自提的 R1-M01 被算進「修」、卻不在 confirmed 86 之內。

## 決策驅動因子

- 事件帳是事件源，人讀面由它重算；「寫錯」的補救形要單一、可預期。
- 擴 `ERRATUM_FIELDS` 等於動事件 schema（前例：ADR-00021 為 probe 欄動過）。
- 000-r1 報告屬史料，正文不改（000-r1 Q19）。
- 錯誤要在寫入端指名真源欄位，不要指向生成檔。

## 考慮過的替代案

1. **`ERRATUM_FIELDS` 納入 summary／reason，MILESTONES／STATE 改吃更正後的視圖**（或 `rev5:B-120` 提過的「澄清事件帶 erratum_of」變體）——動事件 schema、人讀面多一層覆寫邏輯；自由文字欄的錯多屬措辭，以後續 notes 補述已足；否決。
2. **維持 2026-09-21「①③ 留」**——③ 的觸發「動 000-r1 相關報告」因報告屬史料而永不到期、條目長掛；006 收刀寫 feature_close 時 `spec_supersessions[].note` 仍沒有寫入端守衛；user 2026-09-29 裁定推翻。

## 決定

1. `summary`、erratum 的 `reason`、feature_close 的 `spec_supersessions[].note` 三欄不入 `ERRATUM_FIELDS`；寫錯一律於後續事件的 notes 說明（RUNBOOK §12c 現行口徑維持）。事件 schema 不變。
2. 三欄於寫入端（GT-02 事件驗證）套 notes 同一道 GT-06 四腿守衛，錯誤訊息指名列號與欄名；四腿正則仍只住 book.py、不另抄。
3. 000-r1 計數以本批收單 misc 事件的 notes 澄清口徑（修 75 含主線自提 R1-M01、不在 confirmed 86 之內；扣除後 74＋9＋1＋2＝86，與報告 §5 一致）；000-r1 報告與事件帳第 13 列一字不動。

## 後果

- 寫錯的 summary 在人讀面永遠照原文顯示，更正只存在於後續 notes，讀者須對照兩筆。
- 現帳 96 列三欄套上守衛零命中，上線即綠。
- 006 起收刀的 feature_close 各自由文字欄在寫入端即受檢。

## 翻案觸發器

- 自由文字欄出現「人讀面必須顯示更正值」的實際需求（例：對外發布的 MILESTONES 誤導讀者）→ 以新 ADR 擴 `ERRATUM_FIELDS`（替代案 1）。
- GT-06 四腿增減 → 三欄與 notes 同步跟進（同源、不另立）。
