---
id: "ADR-00018"
title: pre-commit entity-drift 段之 schema 快照缺席由 Day-1 具名跳過改為 rc 2 擋下並提示照相
date: 2026-09-05
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00010；docs/brainstorms/002-system-settings.md §0 Q2；ADR-00010 決定 6 之「快照缺席 Day-1 跳過」語意（001 刀 FR-012 已兌現、本 ADR 為其後續而非翻案：ADR-00010 body 不變、其 Day-1 語意到期）；as-built＝002 刀 U0 之 .githooks/pre-commit entity-drift 段；user 於 brainstorm 過目、主線擬稿即 accepted（2026-09-05）"
tags: [governance, hook, schema]
---

## 背景

- 001 刀在 `docs/ops/reference-src/schema-snapshot.json` 尚未產出前，pre-commit entity-drift 段以「快照缺席＝具名跳過」放行創世期的 rust-api pin 首記（ADR-00010 決定 6、Day-1 語意）。
- 快照成為 tracked 檔後，該分支恆為死支且 fail-open：快照被誤刪或 checkout 掉時 hook 靜默放行、非 rc 2。
- 補償控制已驗（2026-09-05）：快照缺席時 docsync `compute_generated` 抛 `SnapshotError`、`check`／`lint` 不捕即非零——pre-commit 仍擋得下，故曝險面小；但擋下的訊息是 traceback 而非補救提示，且依賴的是側效果而非該段自身。

## 決策驅動因子

- Day-1 豁免的紀律＝到期即紅（RL-0052）；解除謂詞（快照就位）已成立。
- 環境缺席（docker／容器）與 tracked 檔缺席方向不同：前者不該擋無關 commit，後者是 repo 自身壞了、必須擋（clarify Q5 同刀拍定兩向各自成立）。
- 002 本就要改同一段 hook（加三支碼面閘），順手改零成本。

## 考慮過的替代案

1. **保留跳過分支、立 by-design ADR**：留一條永不走到的 fail-open 分支、守門靠別段側效果；棄。
2. **不動、留帳**：同段 hook 兩刀改兩次；棄。
3. **改由 docsync 主動捕例外並回具名錯誤**：把補償控制改成唯一防線、且改動面在 docsync 而非該段；棄（列為翻案觸發器之反例）。

## 決定

1. `.githooks/pre-commit` entity-drift 段：`rust-api` gitlink 或快照 staged 時，**快照在場＝`entity-drift-gate.py check` 實跑；快照缺席＝rc 2 擋下**，訊息指名快照路徑並提示「跑 `python3 tools/docsync refresh` 照相（需 dev stack）、git add 快照後重試」；原具名跳過分支移除。
2. 缺席分支在 `pc_run` 並行框架內回報（由 `pc_join` 統一計失敗），不另開 exit 路徑。
3. 語句面同刀改齊（RL-0011）：README 樹與守門句、RUNBOOK §12 兩表、docs/process 兩檔之 pre-commit 列、hook 檔頭。
4. 「快照缺席即紅」與「容器依賴型碼面閘環境缺席＝具名跳過」（同刀另一 ADR）方向各自成立、互不類推。

## 後果

- hook 面演練（移走快照→`git add`→commit）被擋且訊息含補救提示；還原以 `git checkout HEAD -- <快照>`（LL-00003）。
- docsync 的 `SnapshotError` 補償控制仍在（雙重守、非唯一防線）。
- 001 之 ADR-00010 決定 6 的 Day-1 語意自本 ADR 起到期；ADR-00010 body 不變（史料紀律）。

## 翻案觸發器

- 無翻案面：若 docsync 改為捕例外並靜默生成，本段仍紅（本段不依賴補償控制）。若日後快照改為由 hook 自動照相（需 stack 常駐），屬 pre-commit 依賴形變更、以新 ADR 翻案。
