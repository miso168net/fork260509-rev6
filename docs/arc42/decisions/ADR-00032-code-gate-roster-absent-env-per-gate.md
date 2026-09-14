---
id: "ADR-00032"
title: 碼面閘名冊承載於 RUNBOOK §12 碼面閘表（續行 ADR-00016）——名詞定義之環境缺席語意改為逐支見表、容器依賴型具名跳過
date: 2026-09-15
status: accepted
supersedes: ["ADR-00016"]
superseded_by: []
provenance: "user 拍板 2026-09-15（spec-compliance-002 對照審查 finding L2-3 三選一：①立新 ADR 翻案並改 RULES 名詞段／②轉 BL 留帳／③駁回只記報告）；被翻案面＝ADR-00016 決定 3 名詞括注「環境缺席＝具名跳過、工具缺席＝fail-loud」寫成全體碼面閘的共同屬性，與 ADR-00010 閘契約（schema-gate 環境異常 rc 2）、ADR-00018（entity-drift 快照缺席即紅）、ADR-00019 射程（容器依賴型）及其決定 4「方向不類推」相牴；as-built＝tools/schema-gate.py 之 GateError→rc 2、RUNBOOK §12 碼面閘表各列觸發時機欄"
tags: [governance, gates, roster]
---

## 背景

- ADR-00016 決定 3 把碼面閘名詞連同括注「環境缺席＝具名跳過、工具缺席＝fail-loud」寫進 RULES 名詞段，字面讀來是全體碼面閘的共同屬性。
- 碼面閘表成員的環境缺席語意其實不一：`tools/schema-gate.py` 的 `check` 在 docker 不可執行或庫不可達時＝環境異常 rc 2（ADR-00010）；`tools/entity-drift-gate.py` 零 docker、tracked 快照缺席＝rc 2（ADR-00018）；`tools/fork-delta-lint.py` 源倉缺席＝rc 2；只有容器依賴且入 pre-commit 的 `tools/rust-fmt-gate.py` 與 `tools/wire-schema.py` 採具名跳過（ADR-00019，其決定 4 明文方向不類推）。
- accepted body 不可變（GT-04），rev6 也沒有部分翻案機制（ADR-00011 決定 5 先例）；只改 RULES 會讓 RULES 與 accepted 的 ADR-00016 決定 3 字面相悖，權威鏈倒掛（RL-0047）。

## 決策驅動因子

- 名詞定義不得對名冊成員說謊；逐支語意已有自己的家（碼面閘表「觸發時機（含環境缺席語意）」欄），定義只需指路、不重述。
- ADR-00016 決定 1／2／4 經 GT-12 腿實證有效，不因括注字面而重開。

## 考慮過的替代案

1. **轉 BL 留帳、待下次碼面閘進場再翻案**：RULES 的事實錯誤留存至觸發；棄。
2. **駁回（把括注讀成容器依賴型的慣例）**：字面無此限定，對照審查兩鏡皆判屬實；棄。
3. **只改 RULES 名詞段、不動 ADR**：RULES 與 accepted ADR 相悖＝權威鏈倒掛；棄。

## 決定

1. **ADR-00016 之決定 1、2、4 原意續行**，現行依據＝本決定：名冊唯一權威＝`docs/ops/RUNBOOK.md` §12 碼面閘表（`| 工具檔 | 守什麼 | 觸發時機（含環境缺席語意） | 根據 ADR |`；資料列首欄＝反引號 `tools/….py` 路徑、首欄非路徑者＝註記列不計）；GT-12 腿以 S_tools＝`tools/` 頂層 tracked `*.py` − `NON_GATE_TOOLS`（`tools/docsync/gates.py` 常數、成員以常數為準）對 S_table＝表首欄路徑集，雙向差集／表缺席／零路徑列即 ERROR 指名；非閘工具以 `NON_GATE_TOOLS` 具名排除、新碼面閘進場同刀入表。
2. **RULES 名詞段碼面閘定義**：`tools/` 頂層對子庫碼或跨端契約做 check 的系統面機器閘（隨刀進場、不計入 GT-12 治理閘預算、名冊＝RUNBOOK §12 碼面閘表；環境缺席語意逐支見該表「觸發時機」欄——容器依賴且入 pre-commit 者＝具名跳過、工具缺席＝fail-loud（ADR-00019），其餘不類推）；治理閘＝GT-NN 不變。
3. 現在式面引用 ADR-00016 之處（碼面閘表「根據 ADR」欄、README 查詢表）改指本 ADR；accepted ADR body 內的引用不動，讀時併讀本 ADR。

## 後果

- ADR-00016 整顆轉 superseded（`superseded_by` 由 generate 回填）；GT-12 腿、碼面閘表與 `NON_GATE_TOOLS` 的行為零改動。
- RULES 名詞段不入 agent 規則塊（`rules emit` implementer／review／fix 三 scope 皆零命中「碼面閘」），編排成品不需重組。
- 代價：多一顆 ADR，且讀 ADR-00016 時須併讀本 ADR。

## 翻案觸發器

- 碼面閘 ≥8 支、或「守什麼／觸發時機」欄需由工具 docstring 機器抽取時＝另立生成檔並翻案本決定（承 ADR-00016）。
- ADR-00010 對 GATES.md 收錄範圍改判時一併重審。
