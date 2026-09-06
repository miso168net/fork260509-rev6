---
id: "ADR-00016"
title: 碼面閘名冊承載於 RUNBOOK §12 碼面閘表，由 GT-12 新腿對賬 tools/ 頂層工具檔集
date: 2026-09-05
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00011（碼面閘名冊在現在式面無單一權威）；docs/brainstorms/002-system-settings.md §0 Q3／Q8；specs/002-system-settings/contracts/code-gates.md §3；as-built＝002 刀 U0（tools/docsync/gates.py NON_GATE_TOOLS＋runbook_codegate_tools、RUNBOOK §12 碼面閘表六列、RULES 名詞段「碼面閘／治理閘」）；user 於 brainstorm 過目、主線擬稿即 accepted（2026-09-05）"
tags: [governance, gates, roster]
---

## 背景

- rev6 兩類機器閘並存：治理閘 GT-NN（名冊＝`docs/generated/GATES.md`、預算 ≤12、由 GT-12 三處同源對賬）與碼面閘（`tools/` 頂層對子庫碼或跨端契約做 check 的工具：schema-gate、entity-drift-gate、rust-fmt-gate、wire-schema、fork-delta-lint）。
- ADR-00010 刻意讓 GATES.md 不收碼面閘；RUNBOOK §12 原以散文列名；啟動書 §4.2 類比另含 `rev5:Lint24` msg key 契約——碼面閘在現在式面零單一權威、零機器對賬（BL-00011）。
- 002 刀一次進場三支碼面閘，名冊若仍散文，「進場時入本表」只能靠人記得。

## 決策驅動因子

- 每個事實一個人寫的家（RL-0049）；名冊必須有機器對賬否則必漂（RL-0052 精神）。
- 碼面閘屬系統面、隨刀進場，不該吃治理閘的數量預算；但其存在性仍要被閘守住（RL-0051 掃描面空集合即紅）。
- 生成檔形（由工具檔集重算表）在五支規模下是過度設計，且「守什麼／觸發時機／根據 ADR」三欄是人寫語意、機器算不出。

## 考慮過的替代案

1. **納入 GATES.md 名冊**：與 ADR-00010「GATES 只收治理閘」相衝、且撞 ≤12 預算；棄。
2. **另立生成檔 `docs/generated/reference/code-gates.md`**：三欄人寫語意無真源可算；五支規模下多一支生成器零收益；棄（列為翻案觸發器）。
3. **won't-fix、維持散文**：BL-00011 的漂移風險原樣保留；棄。

## 決定

1. **名冊唯一權威**＝`docs/ops/RUNBOOK.md` §12 **碼面閘表**：`| 工具檔 | 守什麼 | 觸發時機（含環境缺席語意） | 根據 ADR |`；資料列首欄＝反引號 `tools/….py` 路徑；首欄非路徑者＝註記列（本刀＝msg key 跨端閘、預告延前端 i18n 刀）、不計入對賬。
2. **GT-12 新腿**（`tools/docsync/gates.py`）：S_tools＝`tools/` 頂層 tracked `*.py` − `NON_GATE_TOOLS`（模組常數、初值 `("tools/wf-watchdog.py",)`）；S_table＝碼面閘表首欄路徑集；雙向差集即 ERROR 指名（漏列／幽靈列）、表缺席或零路徑列即 ERROR。
3. **名詞**入 RULES 名詞段：碼面閘＝`tools/` 頂層對子庫碼或跨端契約做 check 的系統面機器閘（隨刀進場、不計入 GT-12 治理閘預算、名冊＝本表；環境缺席＝具名跳過、工具缺席＝fail-loud）；治理閘＝GT-NN。
4. 非閘工具（編排看門狗等）以 `NON_GATE_TOOLS` 常數具名排除、不入表；新碼面閘進場＝同刀入表（否則 lint 紅）。

## 後果

- 治理閘數維持 12；碼面閘五支入表、GT-12 對賬綠；GATES.md GT-12 列 face 欄含「RUNBOOK 碼面閘表」。
- 「根據 ADR」欄於本 ADR 落檔前暫記題名、落檔後回填序號（tasks T041）。
- 代價：新碼面閘進場多一列人寫表；換得名冊漂移即紅。

## 翻案觸發器

- 碼面閘 ≥8 支、或「守什麼／觸發時機」欄需由工具 docstring 機器抽取時＝另立生成檔並翻案本決定。
- ADR-00010 對 GATES.md 收錄範圍改判時一併重審。
