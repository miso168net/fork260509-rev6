---
id: "LL-00044"
rule_id: "none：機器承載＝GT-12 之「工作樹＝暫存區」一致性腿（ADR-00052），不另立流程規則"
promotion_surface: gate
---
LL-00044｜先 `git add` 再跑 generate，generate 回填的 ADR `superseded_by` 沒進這顆 commit，閘卻全綠（005 刀 final holistic review 修正顆 2bfabcf、2026-09-28）

**徵狀**：新 ADR supersede 舊 ADR 的那顆 commit 落地後，舊 ADR 檔在工作樹上多了 `superseded_by` 回填，commit 裡卻沒有。

**成因**：`docsync generate` 除了寫 docs/generated，也回填被 supersede 之 ADR 的 `superseded_by`（GT-04 唯一可變欄）；單元收尾若先 `git add`、generate 後只補 add 生成檔，回填就漏掉。閘讀工作樹（已含回填）、commit 放的是暫存區（未含），所以看不出來。

**處置**：當時把回填併進下一顆 commit 補上；此後 generate 之後一律再 `git add docs/arc42/decisions`。

**晉升面**：gate——ADR-00052 的「工作樹＝暫存區」一致性腿：commit 準備中若有未暫存的 tracked 改動即擋下，本坑當場現形。

**再犯面與守法**：凡會被 generate 寫到的真源檔（ADR 的 `superseded_by`）與生成檔一樣，generate 後重新 add；被一致性腿擋下時照訊息補 add，不 `--no-verify`。
