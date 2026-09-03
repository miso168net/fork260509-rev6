---
id: "ADR-00008"
title: migration 短號形制＝`m0001` 四碼（承啟動書 D4；rev6 現在式面唯一家；承襲 rev5 migration 時改名）
date: 2026-09-04
status: accepted
supersedes: []
superseded_by: []
provenance: "啟動書 §1.2 D4＋附錄 E（user 拍板 2026-09-03）；000-r1 文件治理體檢 finding R1-C4P04（user 裁定 2026-09-04：四碼、承 D4）"
tags: [governance, ids, schema]
---

## 背景

- 啟動書 D4／附錄 E 拍 migration 短號 `m0001`（四碼），但該拍板只住史料面（docs/brainstorms）；rev6 現在式面（RULES 名詞段、RL-0046 編號家族括號、RUNBOOK §10）零定義。
- rev5 的 migration 檔名為三碼（`rev5:m001_baseline_schema`、`rev5:m002_baseline_seeds`）；首刀 brainstorm 草案曾以「照抄 rev5 檔名、delta 自 m003 起」為前提（三碼），與 D4 互斥。
- 000-r1 體檢的否定對照探針實測：新 session 能正確判「現在式面查無」，但會發現兩份史料互斥而無仲裁點。

## 決策驅動因子

- 單一家（RL-0049）：編號家族形制須有現在式面的家，不能只住史料。
- 史料不改、只加指針（000-r1 Q19）：D4 與附錄 E 原文不動，由本 ADR 承載現在式結論。
- 承襲成本 vs 一致性：rev6 rust-api 目前零 migration 檔，兩形制皆零改名成本；差別只在「照抄 rev5 migration 時改不改檔名」。

## 考慮過的替代案

- 三碼 `m001`（與 rev5 檔名一致、照抄零改名；＝翻 D4）——被 user 否決（2026-09-04）：D4 是唯一經 user 逐族親拍的形制紀錄，翻案需新證據。
- 不定、留待首刀 brainstorm——被否決：現在式面持續零家，新 session 仍會撞到史料互斥。

## 決定

- migration 短號＝`m` ＋ 四碼十進位，自 `m0001` 起；檔名 `m0001_<slug>`。
- 承襲 rev5 migration 時檔名改為四碼（`rev5:m001`→`m0001`、`rev5:m002`→`m0002`），登記序與 fixtures 對照隨首個 schema 刀處理；引用 rev5 原檔一律 `rev5:m001` 前綴形（RL-0046）。
- 現在式面落點：RL-0046 編號家族括號補「migration 短號 `m` 四碼＝ADR-00008」、RUNBOOK §10 一句指針；附錄 E 不改。

## 後果

- 首刀（schema 基線）照抄 rev5 migration 須同批改名並對照 fixtures；「逐位元承襲」的口徑改為「內容逐位元、檔名依本 ADR」。
- 上限 9999 支；rev5 八刀用不到十支。

## 翻案觸發器

- 首個 schema 刀實證改名對照成本高於一致性收益（例：ORM migration 登記序依檔名排序需連動改、fixtures 雙源互證因改名失效）→ 新 ADR `supersedes: [ADR-00008]` 改回三碼。
