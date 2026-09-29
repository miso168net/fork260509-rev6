---
id: "ADR-00062"
title: 記時與帳本日期時區——主線在 tmp/ 記時刻一律同指令取 OS 系統時間、不得估計；受版控帳本日期欄記 OS 系統時間之當地日期（UTC+8）；工具產出之機器時間欄不在此列
date: 2026-09-30
status: accepted
supersedes: []
superseded_by: []
provenance: "user 2026-09-29 聲明（主線在 tmp/ 的檔案記時間用 UTC+8＝OS 系統時間）與 2026-09-30 逐題裁定（時區盤點第 9／10／11 題）；起因＝主線 2026-09-29 人讀進度表之括號時刻憑估計填寫、偏快約 1.5～2.5 小時；前代無對應：rev5 對主線記時方式與帳本日期時區零明文（rev5:RUNBOOK 只有備份檔名帶 UTC 時戳之工具面）"
tags: [governance, process, timezone]
---

## 背景

主線的人讀進度表放在 gitignored 工作區；2026-09-29 其括號時刻曾憑估計填寫，與系統時鐘（Asia/Taipei，UTC+8）偏離約 1.5～2.5 小時。user 聲明主線在 tmp/ 的檔案記時間用 UTC+8（OS 系統時間）。

受版控帳本之日期欄（`docs/ops/events.jsonl` 之 `date`、ADR frontmatter `date`、滯後戳記）實況記 UTC+8 當地日期、無明文：105 筆事件中 49 筆與 UTC 日期不同（皆為凌晨 0～8 點所記）；docsync 只驗 `YYYY-MM-DD` 格式。git commit 時間亦為 `+0800`。

`tools/walkthrough-baseline.py` 產出之走查基準檔帶 `taken_at` 欄，以 UTC（`Z` 結尾）寫入；diff 忽略此欄。

## 決策驅動因子

- 人讀時刻與系統時鐘、commit 時間同源。
- 機器欄帶 `Z` 或偏移即無歧義。
- 規則需在各台機器生效（本機 memory 他機讀不到）。

## 考慮過的替代案

1. **帳本日期改記 UTC 日期**——既有資料不回改（events append-only、ADR accepted 不可變），前後混用兩種日期；否決（user 2026-09-30 裁定）。
2. **工具產出之機器時間欄也改 OS 時間**——user 裁定規則只涵蓋主線手寫之時間；否決。
3. **規則只記本機 memory**——他機 session 讀不到；否決，入 RULES。

## 決定

1. `docs/ops/RULES.md` 新增兩條主線規則：tmp/ 內記時刻一律在寫入的同一指令以 `date` 取 OS 系統時間、不得估計或沿上一筆推算（RL-0082）；受版控帳本之日期欄一律記 OS 系統時間之當地日期（UTC+8），既有資料不回改（RL-0083）。
2. 工具產出之機器時間欄不在 RL-0082 射程：走查基準檔之 `taken_at` 維持 UTC，`docs/ops/RUNBOOK.md` §9c 註明。

## 後果

- 正面：進度表時刻可信、可與 commit 時間對照；帳本日期時區有明文。
- 負面：凌晨 0～8 點所記事件之日期與 UTC 日期不同，屬已知態。

## 翻案觸發器

- 協作者分處不同時區，需要統一以 UTC 記帳本日期。
