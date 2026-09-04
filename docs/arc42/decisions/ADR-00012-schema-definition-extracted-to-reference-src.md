---
id: "ADR-00012"
title: schema 定稿權威自 001 spec 目錄抽出至 reference-src——凍結存證與跨刀活體二分
date: 2026-09-05
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00022（001 刀 spec-compliance-001 審查輪建議 1 所衍生）；user 拍板 2026-09-05（三選項一題一問：抽取／就地定位／延後，選抽取並指定不動 specs/001）；分類體檢 tmp/check-backlog.md §3"
tags: [governance, schema, materials]
---

## 背景

- `specs/001-schema-baseline/data-model.md`（672 行）同時扮演兩個角色：001 刀的定稿史料，以及 `tools/schema-gate.py` 的**跨刀活體左源**（gate2 欄序與 doccheck 的 §2／§6／§9）。
- RUNBOOK §10 的 Day-1 登記紀律明寫「新業務表先補 data-model §1 再登記 archetype-map」——即每支帶 migration 的刀都要回頭改這份住在**已收刀 spec 目錄**裡的檔。
- `parse_data_model_five` 另硬編碼 `if len(tables) != 14`，002 一加表就同時撞「改別人的 spec 目錄」與「改工具常數」。
- RULES 名詞段定 `specs/**` 為**史料面**（不受裸編號、時態、形制掃描）——活體權威長住史料面，等於它永遠拿不到現在式面的閘。

## 決策驅動因子

- spec 目錄應是定點快照；跨刀前進的東西不該住在裡面。
- repo 已有同構的二分先例：`specs/001-schema-baseline/fixtures/`（凍結面、永不改寫）對 `docs/ops/reference-src/schema-snapshot.json`（活體照相），差額由 `schema-evolution.json` 解釋。schema 定稿套用同一形即可，不必發明新機制。
- 工具的 §N 解析靠 `## N. … ## N+1.` 節邊界定位，故新檔必須保留十個節標題——這反而給出乾淨的切法：會前進的節抄實體、已成史的節留指針。

## 考慮過的替代案

1. **搬家**（`git mv` 至 reference-src、specs/001 留指針）：`m0001_baseline_schema.rs` 等三處子庫註解寫的是「定稿憑據＝specs/001…data-model.md」＝**成品出處的陳述**，搬走後成假述、非改不可，於是純外層維護批被迫變成動子庫（子庫 commit＋pin bump），且觸及憲法 §I.5 例外②十七檔之一。棄。
2. **就地定位**（檔不動、RULES 名詞段加現在式面例外、表數斷言改由 archetype-map 推導）：改動面最小、零內容重複；但 001 的 spec 目錄永遠不是定點快照，後續每刀仍回頭改它。棄（user 拍板要 specs/001 維持當下史料）。
3. **延後至 002 開分支前**：問題不變、只是推遲，且本輪已枚舉好的引用清單與節別分類會隨對話蒸發。棄。

## 決定

1. **新增 `docs/ops/reference-src/schema-definition.md`** ＝ rev6 現行 schema 定稿的唯一人寫權威（**左源**）；右源＝同目錄 `schema-snapshot.json`，兩者差額由 `schema-evolution.json` 逐筆解釋，歸屬面另居 `archetype-map.json`。
2. **節號與凍結存證一致**（十節齊）：§1／§2／§5／§6／§7／§8／§9 抄實體並隨刀前進；§3 rename map、§4 rev5 對 rev4 定稿差異、§10 防回歸與 001 射程界定屬已成史，只留一行指針回凍結存證。
3. **`specs/001-schema-baseline/data-model.md` 零改動**、留為 001 收刀當下的凍結史料，不再前進。其節內容與新檔自本 ADR 之日起分岔，分岔由演進帳解釋。
4. **子庫三處註解不改**：`entity/src/lib.rs`／`migration/src/lib.rs`／`m0001_baseline_schema.rs` 所述「定稿憑據＝specs/001…data-model.md」是**成品出處**的歷史陳述、於凍結存證原地保留下仍為真，故本決定不動子庫、不 bump pin、不觸憲法 §I.5 例外②射程。
5. **左源座標改指**：`tools/schema-gate.py` 之 `DATA_MODEL` 常數、pre-commit 的 `schema-frozen` 觸發面（凍結存證 ∪ 活體定稿）、RUNBOOK §10、`archetype-map.json` 之 `lineage`、arc42 §8.1 memo 欄語意權威。座標釘死測試改為「凍結面指 specs/001、跨刀活體一律指 reference-src」的二分斷言。
6. **表數斷言**維持解析自檢形（§2 宣告數 vs 解析數），`!= 14` 的硬編碼隨 002 首次加表時由該刀改對；本 ADR 不預先改，避免在零 delta 時失去自檢強度。

## 後果

- 002 起「新表先補定稿 §1 再登記 map」改在 `docs/ops/reference-src/` 內完成，不再回頭改已收刀的 spec 目錄。
- 定稿內容在兩處各有一份（凍結存證與活體），與 fixtures／snapshot 的既有二分同構；讀者由檔頭 provenance 段辨識何者為現行。
- 凍結存證目前**無機器守門防止被誤改**：`schema-frozen` hook 段雖仍在其 staged 時觸發，但 doccheck 的左源已改指活體檔，改動凍結存證不會被判紅。屬已知殘留、與 fixtures 的「違憲級但只由 review 承載」同層。
- 節號跳號問題不存在（十節齊），故 `parse_data_model_five`／`doccheck_findings` 的節邊界定位零改動。

## 翻案觸發器

- 凍結存證出現實際被誤改的事例＝本決定的「無機器守門」代價成真，重審是否對 `specs/**` 之凍結面加內容雜湊閘。
- 若日後判定 spec 目錄應可隨刀前進（推翻「定點快照」前提），本決定連同 RULES 名詞段的 specs 史料面定性一併重審。
