---
id: "ADR-00021"
title: 檢索性第四指標——review 事件 `probe` 欄（冷啟動探針＋否定對照題計數）為資料源，STATE 治理指標表加一列、比例由 generate 現算；000-r1 以 erratum 回填為基準
date: 2026-09-07
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00007（000-r1 R1 探針面衍生）；000-r1 報告 §3 逐題表＝首筆資料；user 拍板 2026-09-07（三選一：①現在立 ADR 定欄、r1 回填、r2 起結構化入帳／②等 000-r2 再定／③降級 DEFERRED）；as-built＝tools/docsync/events.py（PROBE_KEYS／_check_probe／_probe_retrieval）、references.py（_probe_row）、tests/test_events.py 四案、events.jsonl erratum 回填 000-r1"
tags: [governance, metrics, events, review]
---

## 背景

- 啟動書 §4.3 釘死三個治理指標（治理批對 feature 比／LESSONS 重複率／BACKLOG 淨流量），資料源、窗口、算式、空值全部寫死、由 generate 產進 STATE.md。
- 000-r1 獨立輪首次跑冷啟動探針（四支 25 題）與否定對照探針（7 題），grader 逐題回判定四值（找得到／繞路／找不到／答錯）與最短 hops；結果只落報告逐題表與 review 事件 notes 自由文（「探針 32 題找不到 0、答錯 0」），機器面無欄可讀、輪間無法比對。
- review 骨架入庫（maint-backlog-6）後 grader 已回結構化 `grades`（verdict 四值、min_hops），資料源就緒；下一次獨立輪 000-r2 隨時可開。若欄位在 r2 之後才定，r2 數據又只能落 notes、事後再靠 erratum 補欄——順序上應先定欄。

## 決策驅動因子

- 每個事實只有一個人寫的家（RL-0049）：探針結果的家＝review 事件、不是 notes 自由文；STATE 只現算、不存導出值。
- 事件源 append-only（BL-00004 更正視圖）：000-r1 回填走 erratum、原列不改。
- D8 棘輪警語：只加一欄、一列，不加閘、不加生成檔；GT-02 既有 schema 檢查順帶守形。
- 指標若無目標即只是報表：目標必須能由帳本判紅綠。

## 考慮過的替代案

1. **等 000-r2 跑完再定欄**：算式可由兩筆資料釘，但 r2 數據落 notes 後仍需 erratum 補欄（r1 已如此一次）；棄。
2. **在事件欄直接存比例（le3_ratio／hit_ratio）**：導出值入帳＝兩個家（RL-0049）；棄，只存計數。
3. **降級 DEFERRED（三指標為定、探針結果住報告即足）**：跨輪趨勢只能人工翻報告；棄。

## 決定

1. **資料源**＝`review` 事件新增 optional 欄 `probe`：`{questions, found, detour, not_found, wrong, avg_min_hops[, negative]}`；`negative`（否定對照題）同形、可缺席、不再巢套。形檢＝GT-02 既有 schema 腿（鍵集固定、四計數非負整數且守恆＝questions、questions ≥1、avg_min_hops 非負數）。
2. **計數口徑**＝grader 判定四值（找得到＝探針 ≤3 跳且答對／繞路＝>3 跳但答對／找不到／答錯）逐題計數；`avg_min_hops`＝grader 最短 hops 平均（小數兩位）。主線自 review 骨架回傳 `probes[].grade.grades` 計數、收單時寫入。
3. **算式**（generate 現算、不入帳）：≤3 跳比例＝found/questions；答對率＝(found＋detour)/questions；找不到＝not_found；答錯＝wrong；否定對照答錯＝negative.wrong（缺席印「—」）。
4. **窗口**＝最近一筆帶 `probe` 的 review 事件（人讀面吃 erratum 更正視圖）；無＝「n/a」。
5. **目標**＝找不到＋答錯＝0；≤3 跳比例輪間不降。
6. **基準**（同算式回算 000-r1 報告 §3）：冷啟動 25 題＝找得到 12／繞路 13／找不到 0／答錯 0、grader 最短 hops 平均 2.0（≤3 跳比例 0.48、答對率 1.0）；否定對照 7 題＝找得到 6／繞路 1／找不到 0／答錯 0、hops 平均 2.14。以 erratum（`field: probe`）回填 000-r1 review 事件；erratum 對 review 型容許目標列原無該欄（同 adrs 型之 BL-00004 先例）。
7. **承載**：STATE.md「治理指標」表第四列「檢索性（最近獨立輪 <scope>）」；erratum 可更正欄集加 `probe`。

## 後果

- 000-r2 起獨立輪收單直接結構化入帳，輪間可機器比對；STATE 立即有 r1 首值。
- 代價：review 事件多一 optional 欄、erratum 欄集多一項、STATE 多一列；閘數 12 不動、無新生成檔。
- BL-00007 於本批收掉（backlog_done）。

## 翻案觸發器

- 探針題庫改形（題數固定化、分層加權）或需要逐題入帳時＝另立 ADR 改欄形。
- 連續兩輪 ≤3 跳比例低於前輪＝目標失守、回頭審題庫或文件入口，非改算式。
