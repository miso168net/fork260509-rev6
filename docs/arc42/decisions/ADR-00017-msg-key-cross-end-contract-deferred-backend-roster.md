---
id: "ADR-00017"
title: msg key 跨端契約延至首個接 i18n 的前端刀，002 只閉後端側 msg key 名冊
date: 2026-09-05
status: accepted
supersedes: []
superseded_by: []
provenance: "docs/brainstorms/002-system-settings.md §0 Q4；rev5:Lint24（rev5 之 msg key 跨端閘：後端字面 ⊆ 前端 zh-tw.ts 字典）；specs/002-system-settings/spec.md FR-020；data-model §6 名冊七鍵；user 於 brainstorm 過目、主線擬稿即 accepted（2026-09-05）"
tags: [wire, i18n, contract]
---

## 背景

- 憲法 §I.3：後端 `msg` 恆為穩定 i18n key、不回人話字串；前端對未命中 key 走 graceful fallback。
- rev5 以 rev5:Lint24 在傘狀 lint 內做跨端閉環（後端可發出的 msg key 全集 ⊆ 前端 `zh-tw.ts` 字典），並在 002 同刀改動 base-web 的 locales 檔。
- rev6 002 刀憲法 §IV 第 2 題拍定零 base-web inline、零 locales 改動（brainstorm Q4／Q7）；跨端閘的右源（前端字典）在本刀不存在。

## 決策驅動因子

- 跨端閘的兩端要同時存在才有對賬語意；本刀只有左源（後端名冊）。
- 但後端側「可發出的 msg key 全集」必須在首支 server 刀就成為單一名冊並被機器守——否則 key 字面散落各構造點、殭屍鍵與拼錯鍵皆無訊號。
- 前端字典改動屬 base-web 面，該由首個接 i18n 的前端刀決定字典形與軌道授權，不該由後端刀越界。

## 考慮過的替代案

1. **本刀同時改 base-web locales 補七鍵**：破 Q7「零 locales 改動」、且需開憲法 §III.2 ★軌道；棄。
2. **跨端閘以後端名冊對 upstream 既有 locales 檔對賬**：upstream 字典無 rev6 業務 key、恆紅；棄。
3. **不立後端名冊、留到跨端刀一併做**：本刀寫端與 fallback 已發出七鍵，構造點分散無守；棄。

## 決定

1. **後端側名冊**＝`server/src/error.rs` 之 `MSG_KEYS` 常數（本刀恰七鍵：`common.success`／`biz.systemSettings.invalidValue`／`biz.systemSettings.notFound`／`system.notFound`／`system.forbidden`／`system.internal`／`auth.session.reLogin`）；每個 key 字面只在其構造點出現一次。
2. **後端側閉環的機器守**＝`server/tests/contract.rs` 雙向斷言：每條 route 每個錯誤路徑實發 `msg` ∈ 名冊、名冊每鍵 ≥1 發出點（防殭屍鍵）；全等斷言於全部發出點就位的單元成立（本刀 U5）。
3. **跨端閘**（後端名冊 ⊆ 前端字典）**延至首個接 i18n 的前端刀**進場；以 BACKLOG 條目承載觸發；RUNBOOK §12 碼面閘表以註記列預告（非 `tools/` 工具檔形、GT-12 腿不計）。
4. 本刀 base-web locales 零改動；前端未命中 key 走既有 graceful fallback。

## 後果

- 002 期間 msg key 拼錯或新增未入名冊即 contract 紅；跨端一致性由前端刀補閘。
- 跨端閘進場時左源直接取 `MSG_KEYS`、右源＝該刀決定的字典檔；名冊形不必重定。
- 代價：在前端刀進場前，前端對七鍵顯示 fallback 而非在地化文字（dev 面可接受、view 亦不在本刀）。

## 翻案觸發器

- 首個接 i18n 的前端刀進場＝本 ADR 第 3 點兌現（非翻案）；若該刀決定字典由後端名冊生成（單向而非對賬），以新 ADR 翻案第 2／3 點。
