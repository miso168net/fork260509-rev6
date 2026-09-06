---
id: "ADR-00020"
title: 編排骨架子名冊＝tools/orchestration/README.md 檔表，由 GT-09 新腿對賬 tools/orchestration/ 實檔集
date: 2026-09-07
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00032（maint-backlog-6 dogfood review L1-5、R-real／R-decided 兩鏡確認）；000-r1 R1-065（檔表漏列四支、當時人工補）；as-built＝tools/docsync/gates.py gt_09 新腿＋tools/docsync/tests/test_gates.py 一正一反、tools/orchestration/README.md 檔表；user 拍板 2026-09-07（輕量軌 maint-backlog-6：補腿並立 ADR）"
tags: [governance, gates, roster, orchestration]
---

## 背景

- 根 README 的目錄樹由 GT-09 與 `tools/`／`deploy/`／`.githooks/`／`.claude/` 實檔集雙向對賬；但樹對 `tools/orchestration/` 只列目錄、不展開子項，GT-09 以葉目錄粒度概括覆蓋——該目錄下新增或改名任何檔都不會變紅。
- `tools/orchestration/README.md` 的檔表是編排骨架的唯一子名冊（每檔一列：首欄反引號檔名、次欄內容），000-r1 R1-065 抓過漏列四支、修法純人工；BL-00006 入庫後檔數自 8 增至 13，漏列面隨之變大。
- 輕量軌 maint-backlog-6 以新 review 骨架自審，L1-5 兩鏡確認同一缺口、原提案轉 BL-00032；user 拍板改為本批補腿並立本 ADR。

## 決策驅動因子

- 名冊必須有機器對賬否則必漂（RL-0052 精神）；掃描面空集合即紅（RL-0051）。
- 治理閘預算 ≤12、一進一出（ADR-00004）：補腿不新增閘、閘數不動。
- 檔表「內容」欄是人寫語意（怎麼用、守什麼），無真源可算——不走生成檔。

## 考慮過的替代案

1. **GT-12 加腿**：GT-12 的射程是名冊三處同源與數量預算（GATES.md／pre-commit 檔頭／RUNBOOK 表），與「一份人寫檔表 ⇔ 實檔集」的語意不同；棄。
2. **另立生成檔 `docs/generated/reference/orchestration.md`**：內容欄人寫、生成器只能列檔名，多一支生成器零收益；棄（列為翻案觸發器）。
3. **維持人工**：R1-065 已證會漏；棄。

## 決定

1. **子名冊唯一權威**＝`tools/orchestration/README.md` 檔表：資料列首欄＝反引號檔名（不含路徑、不含 `/`）；`README.md` 自身不列；子目錄檔不計（現無）。
2. **GT-09 新腿**（`tools/docsync/gates.py` `gt_09`；不新增閘、閘數維持 12）：S_files＝`tools/orchestration/` 頂層 tracked 檔集 − `README.md`；S_table＝檔表首欄反引號集；雙向差集即 ERROR 指名（tracked 未列／幽靈列）；零 orchestration 檔＝腿不跑；檔表缺席或零列＝ERROR（掃描面空集合）。
3. **語料面一正一反**（`tools/docsync/tests/test_gates.py`）：綠案、漏列＋幽靈列紅案、缺席／零列紅案、零檔靜默案。
4. 生成物 `_sk_rules.js` 亦入表（它是 tracked 檔；表列內容欄註明「機器生成」）；新增 orchestration 檔＝同批入表，否則 pre-commit lint 紅。

## 後果

- GATES.md GT-09 列 face 欄含「tools/orchestration/README.md 檔表 ⇔ tools/orchestration/ tracked 檔集」；閘數 12 不動。
- 代價：增檔多一列人寫表；換得子名冊漂移即紅（本 ADR 落檔時檔表 13 列與實檔集全等）。
- BL-00032 於本批收掉（backlog_done）。

## 翻案觸發器

- `tools/orchestration/` 出現子目錄、或頂層檔數 ≥25（表過長）＝改生成檔並翻案本決定。
- GT-09 被拆分（接線腿與名冊腿分家）時一併重審本腿歸屬。
