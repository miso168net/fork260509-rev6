---
id: "ADR-00025"
title: won't-fix——ADR 方向不設「誕生必帶事件」反向不變式；ADR 的家是檔案本身，BL／ADR 兩個 ID 家族刻意兩制
date: 2026-09-07
status: accepted
supersedes: []
superseded_by: []
provenance: "000-r2 獨立輪 C3-3（major、閘覆蓋缺口；C3 lens inline 兩鏡皆確認）與 C3-1（misc.adrs 欄 2026-09-05 才上線、九筆漏記）；user 停點① 拍板 2026-09-07（三選一：①ADR 同形立不變式／②明立 won't-fix／③WARN 級軟腿）"
tags: [governance, events, adr, wont-fix]
---

## 背景

- 000-r2 的 D 修單為 BL 建立 events-only 反向存在性不變式（計畫 Q14）：任一處引用的 `BL-NNNNN` 必須曾出現在某筆事件的 `backlog_add`，否則 GT-03 紅。今日實算三類差集皆空、零遷移成本。
- ADR 方向不同形：`misc.adrs` 在 EVENT_SCHEMAS 是 **optional**，`gt_03` 只走前向存在性（事件引用的 ADR 號必須有對應檔），沒有反向腿。
- 同形套用到 ADR 今日會紅 7 筆：ADR-00001～00007 誕生於創世波，當時 `misc.adrs` 欄尚未上線（該欄由 BL-00004 於 2026-09-05 補；同日 001 feature_close 已在用）。C3-1 另指出更正政策不一致——九筆漏記中只為 ADR-00011 補過一筆 erratum。

## 決策驅動因子

- **兩個家族的「家」本質不同**：BL 條目完成即刪列（RL-0050），離了事件就真的無家可查；ADR 檔案永久留存且 accepted 後不可變，檔案本身即權威，事件只是「哪一批收單帶進來」的索引。
- 立反向不變式需先補至少四筆 erratum，且要把 `misc.adrs` 自 optional 升為條件必填＝動 EVENT_SCHEMAS 形制，非零遷移。
- WARN 級軟腿在本 repo 已有前例稀釋問題：ADR-00011 已讓數量預算超限只警告不擋，再加一種軟告警會使警告面失去信號價值。

## 考慮過的替代案

1. **ADR 同形立不變式**（gt_03 加反向腿）：語意與 BL 一致、DECISIONS-INDEX 的 feature 欄從此不可能查無。棄——需先補四筆 erratum、且 `misc.adrs` 須自 optional 升為條件必填（形制變更）；收益（生成面欄位不空）小於代價。
2. **WARN 級軟腿**：某 ADR 誕生 commit 落在某收單 merge 區間而該事件無 `adrs` 欄→警告不擋。棄——見決策驅動因子第三點。

## 決定

1. **ADR 方向不設反向存在性不變式**：`gt_03` 維持只走前向（事件引用的 ADR 必須有檔），不新增「每支 ADR 檔必須被某事件引用」的腿。
2. **`misc.adrs` 維持 optional**：EVENT_SCHEMAS 不動。
3. **理由入現在式面**：`docs/ops/RUNBOOK.md` §12c（事件更正機制）旁記一句「ADR 的家是 `docs/arc42/decisions/` 檔案本身，不設反向不變式（ADR-00025）；BL 反之——完成即刪列，故其誕生必帶 `backlog_add` 事件」。
4. **創世豁免不逐筆補 erratum**：ADR-00001～00007 誕生時該欄未上線，屬形制演進的自然缺口、非帳目錯誤；本 ADR 即其登記處，不再另補 erratum。ADR-00008（won't-fix 出身、住 review 事件 `wontfix_adr`）與 ADR-00011 的生成面歸屬另由 A run L1-03／L1-04 的修單處理（`gen_decisions_index` 加 review 反查、去除硬編「輕量軌」fallback）。

## 後果

- BL 與 ADR 兩個同構 ID 家族刻意兩制：BL 有反向不變式、ADR 無。差異與理由由本 ADR 與 RUNBOOK §12c 一句承載。
- 零遷移、零 schema 變更、零新閘。
- 代價：讀者須記住兩制差異；`DECISIONS-INDEX` 的 feature 欄對創世期 ADR 仍可能無來源（由 L1-04 修單改為中性「—」、不再憑空標「輕量軌」）。

## 翻案觸發器

- `misc.adrs` 因其他理由升為必填時，反向不變式的邊際成本降為零，應重審。
- ADR 檔案改為可刪除或可搬移（不再永久留存）時，「家是檔案本身」的前提失效。
