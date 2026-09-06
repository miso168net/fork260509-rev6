---
id: "ADR-00015"
title: 部分更新請求之 envelope 級三態約定——欄位缺席＝不動、JSON null＝顯式清空、有值＝設值
date: 2026-09-05
status: accepted
supersedes: []
superseded_by: []
provenance: "rev5:ADR 0023（rev5 002 刀三態約定）；rev5:L-009（serde 預設把 null 落外層 None、三態塌兩態）；docs/brainstorms/002-system-settings.md §0 Q1；specs/002-system-settings/data-model.md §8 條文轉錄；spec FR-011／FR-012／US5；user 於 brainstorm 過目、主線擬稿即 accepted（2026-09-05）"
tags: [wire, envelope, serde]
---

## 背景

- 002 刀的 `POST /systemManage/updateSystemSetting` 是 rev6 第一個部分更新寫端；request body 的可選欄（`description`）同時要表達「不動」「清空」「設值」三種意圖，而 JSON 只有「缺席」與「null」兩種非值形。
- serde 對 `Option<T>` 的預設反序列化把「欄位值 null」與「欄位缺席」都落 `None`，三態塌成兩態（rev5:L-009 實證）；不在解析層顯式區分，寫端就無法承載「清空」。
- 憲法 §I.3 鎖 wire 凍結面於 envelope 級；這條約定一旦由第一支寫端隱含定死，全 repo 後續寫端都會沿用——必須顯式立文。

## 決策驅動因子

- 與 RFC 7386（JSON Merge Patch）語意一致，前端與後端對「送 null」的理解無歧義。
- 一次定形、全 repo 消費；逐域欄級三態表留各域刀自定，本 ADR 只鎖 envelope 級語意與射程。
- NOT NULL 欄的「清空」不是合法意圖：必須拒收而非靜默忽略。

## 考慮過的替代案

1. **以特殊字面表示清空**（如 `""` 或 `"__CLEAR__"`）：與「設值為空字串」語意衝突、且非 JSON 慣例；棄。
2. **每欄一個旗標欄**（`clearDescription: true`）：wire 面倍增、typings 與快照裁判複雜化；棄。
3. **只支援兩態**（缺席＝不動、有值＝設值、不提供清空）：nullable 欄永遠清不掉；棄。

## 決定

1. **envelope 級三態語意**（部分更新請求 body 之每一可選欄）：**欄位缺席＝不動；欄位值 JSON `null`＝顯式清空；欄位有值＝設值（空字串亦為設值）**。
2. **NOT NULL 欄的顯式清空＝拒收**（本刀 `settingValue` null→`2222 biz.systemSettings.invalidValue`）；nullable 欄的顯式清空＝落 NULL（本刀 `description`）。
3. **解析層承載形**＝`Option<Option<T>>`＋`#[serde(default)]`＋自訂 `deserialize_with`（欄出現時外層恆 `Some`、內層由 null／值決定；欄缺席時走 default 落外層 `None`）；必填欄亦以此寬鬆形承載，缺席或顯式 null 由 handler 層判 `2222`、不由 serde 必填機制拒收（否則落框架預設 400／422 裸 body、違憲法 §I.3）。
4. **wire 型別對應**：寫端請求物件之 nullable 三態欄 typings 為 `T | null` 可選欄（快照經 `--strictNullChecks` 忠實呈 `["null","string"]`）；讀端列型對同名欄若後端 NULL 以缺席上 wire、其 typings 不含 null——讀端缺席語意與寫端清空語意是兩件事、各自斷言。
5. **射程**＝部分更新請求 body；create 請求與 query 參數不在射程。逐域欄級三態表由各域刀自定。

## 後果

- 002 寫端之 `UpdateSystemSettingReq` 三欄皆以三態型承載；wire_schema 裁判對 UpdateReq 斷言 description 型恰 `["null","string"]`、required 恰兩必填欄；handler 三態五案（缺席不動／null 落 NULL／`""` 落空字串／設值／settingValue null 拒收）為機器錨。
- data-model §8 自本 ADR 起轉為指引、本 ADR 為權威。
- 代價：每個三態欄多一層 `Option` 與一支 deserialize_with；換得前後端對 null 零歧義。

## 翻案觸發器

- create 請求語意也要鎖（例如 create 允許 null 表「採預設值」）＝新 ADR 擴射程，不改本決定。
- 若日後採 PATCH 動詞或 JSON Patch（RFC 6902）取代 merge 語意＝新 ADR 翻案。
