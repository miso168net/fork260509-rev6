---
id: "ADR-00054"
title: 設定界值唯一權威＝validation.rs 的 REGISTRY、不與設計文件做機器對賬——seed 界內以純測守衛
date: 2026-09-29
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00028（002 刀 U3 轉入；2026-09-14 體檢與 2026-09-15 spec-compliance-002 兩度收窄）；user 2026-09-29 裁定（006 前 BACKLOG 體檢題 9 ①）；seed 界內守衛＝主線測試策略（同體檢題 8）；ADR-00038 決定 4（節流界值取自 validation 之宣告、不另抄一份）；前代出處：rev5:B-160（前端界值是後端界值的手工第二份拷貝、兩側零機器對賬）"
tags: [settings, validation, rust-api, tests]
---

## 背景

設定 16 鍵（其中 10 個數字鍵）的界值住 rust-api `server/src/validation.rs` 的 `REGISTRY`（`range` 欄）；002 data-model §3 另有一份 min／max 表。兩份靠手工轉錄、零機器互鎖（BL-00028）；002 刀 U3 與 2026-09-29 體檢兩度機器比對皆全等。§3 屬 specs/002 史料面、凍結；m0002 屬 ADR-00009 的資料形拷貝例外、與 rev5 逐位元自證。

另一半：seed 值是否落在 REGISTRY 界內也零機器守——`validation::validate` 只在寫端 handler 呼叫，讀端（例：`auth/jwt.rs` 讀 session_idle_timeout）只解析、不驗界（節流兩維自 004 刀 U9 起以 `range_of` 驗界、越界整組退常數，不在此列）。現行 16 列 seed 皆在界內。

## 決策驅動因子

- 活體真源只能有一份；史料面文件不該成為對賬對象（時態分離）。
- 原觸發「首次新增或改動設定鍵」依 rev5 前例 006～008 皆不會到期（rev5 全程只有兩支 migration）。
- seed 越界時讀端會直接採用、要等寫端重存才被擋；純測守衛成本低（不碰 DB）。

## 考慮過的替代案

1. **以真源字面解析驅動期望表、或加 REGISTRY ↔ §3 跨檔對賬測**——對賬對象是凍結史料，只守得到初次轉錄；否決。
2. **續掛原觸發**——近乎不會到期、條目長掛；否決。
3. **seed 界內守衛讀真庫現值**——須持 DB_SERIAL 鎖（jwt／login／logout／refresh 的測試會暫改設定值），而純測版經既有真庫逐格全等案即可遞移到 m0002；否決。

## 決定

1. 設定界值的唯一權威＝`validation.rs` 的 `REGISTRY`；不與設計文件（含 002 data-model §3）做機器對賬。之後新增或改動設定鍵的刀以 REGISTRY 為準，設計文件只引用、不另抄一份。
2. seed 界內以純測守衛：handler 測試模組的 seed 期望表 `SEED_EXPECTED` 逐列過 `validation::validate`、須全數通過，並附一反例自證；該表經既有真庫逐格全等案（`assert_sixteen_keys_cell_equal_to_seed`）遞移到 m0002——不碰 DB、不持 DB_SERIAL 鎖。

## 後果

- 002 data-model §3 的界值表成為純史料，與現行值的一致性不再有人對賬；讀者以 REGISTRY 為準。
- 新 migration 若寫入越界 seed，只要 `SEED_EXPECTED` 同批更新（真庫逐格全等案強制），純測守衛即紅。
- BL-00028 收列。

## 翻案觸發器

- 任一刀另立界值真源（例：設定頁照 rev5 前例長出前端界值拷貝，見 `rev5:B-160`）→ 重審決定 1，改為跨端機器對賬。
- 讀端改為統一驗界（seed 越界整組退常數）→ 決定 2 的守衛可降級。
