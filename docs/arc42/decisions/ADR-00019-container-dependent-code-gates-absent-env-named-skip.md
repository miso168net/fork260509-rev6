---
id: "ADR-00019"
title: 容器依賴型碼面閘之環境缺席語意——docker 或對應容器不在＝具名跳過 rc 0、容器在而工具缺或重抽失敗＝fail-loud
date: 2026-09-05
status: accepted
supersedes: []
superseded_by: []
provenance: "specs/002-system-settings/spec.md Clarifications 2026-09-05 Q5（user 親決：A 具名跳過 rc 0）；rev5:ADR 0057 決定 3（rev5 rust-fmt-gate 之跳過邏輯住工具內、hook 段零條件判斷）；specs/002-system-settings/contracts/code-gates.md §1.1／§1.2；research R13 反例回跑；as-built＝002 刀 U0 之 tools/rust-fmt-gate.py 四態與 tools/wire-schema.py check"
tags: [governance, hook, code-gate]
---

## 背景

- rust 格式閘（`cargo fmt --all --check`）與 wire 契約閘（typings 重抽 byte 比對）都只能在容器內跑：host 無 rust toolchain、node 只在 base-web 容器。
- pre-commit 的既有紀律＝「stack 沒起時 hook MUST 可用」（純文件 commit 不該被 docker 綁架）；但若把「容器不在」與「容器在而工具壞」一併靜默跳過，閘就進入「守門動作恆不跑」的失效類。
- rev5 以 rev5:ADR 0057 決定 3 拍定同題；rev6 憲法 §I.5 要求以 rev6 自立 ADR 承襲。

## 決策驅動因子

- 兩種缺席不是同一件事：環境缺席（docker 不在 PATH／compose 檔缺／容器未起）是開發者本機狀態；工具缺席（容器在而 cargo-fmt 不在映像）或重抽失敗是 repo／映像壞了。
- 跳過必須**具名**（印一行「⤳ 跳過：原因」）、與通過在輸出上可辨；rc 相同不代表語意相同。
- 跳過分支的殘留風險（離線 commit 帶入未格式化碼）由「下一次 stack 在跑的 pin bump 擋下」承接＝延遲一站、非漏網（R13 反例回跑通過）。

## 考慮過的替代案

1. **環境缺席也擋下**：離線不可 commit、純文件改動被 docker 綁架；棄。
2. **一律跳過（含工具缺席）**：舊映像靜默跳過＝守門恆不跑；棄。
3. **跳過邏輯寫在 hook 段**：兩支工具各一份條件判斷、與工具自帶 self-test 分岔；棄——跳過邏輯住工具內、hook 段只做接線（承 rev5 形）。

## 決定

1. **rust 格式閘**（`tools/rust-fmt-gate.py check`）四態：①docker 不在 PATH／repo 根缺 compose 兩檔→具名跳過 rc 0 ②`rust-api` 容器未在跑→具名跳過 rc 0 ③容器在、fmt 全綠→rc 0 ④容器在、未格式化→rc 1 帶段數與補救；容器在而 cargo-fmt 缺席→**rc 2 fail-loud**、不設豁免。
2. **wire 契約閘**（`tools/wire-schema.py check [--staged-gate]`）：docker 缺／`base-web` 容器未起→具名跳過 rc 0；`--staged-gate` 且 staged 區間零 typings 變動→跳過 rc 0；容器在而重抽失敗、快照缺席或不一致→**rc 2**。
3. **跳過邏輯住工具內**、pre-commit 段零條件判斷只做接線；跳過與通過在輸出上必須可辨（具名一行）。
4. **方向不類推**：tracked 檔缺席（entity-drift 段之 schema 快照；fork-delta 之源倉缺席或未切 example）＝rc 2 fail-loud，與環境缺席各自成立。
5. 紅路徑與跳過路徑印出的補救命令必同印例外面告誡（憲法 §I.5 例外①②之承襲存量紅＝停手升 user、絕不無條件 `cargo fmt --all`）。

## 後果

- 「stack 沒起時 pre-commit MUST 可用」紀律不變；三支碼面閘皆入 pre-commit 條件段與 `for` 自測迴圈。
- 殘留風險＝離線 commit 可能帶入未格式化碼／未重抽快照，於下一次 stack 在跑的 pin bump 被擋（延遲一站）；RUNBOOK §12 碼面閘表「觸發時機」欄逐支寫明缺席語意。
- self-test 對兩跳過態、fail-loud 態、告誡輸出各有一案釘住（rust-fmt 12 案、wire-schema 27 案）。

## 翻案觸發器

- pre-commit 改為需 dev stack 常駐（或改由 CI 承載碼面閘）時，環境缺席語意反轉為擋下＝新 ADR 翻案。
