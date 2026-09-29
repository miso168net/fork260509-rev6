---
id: "ADR-00060"
title: 憲法 §I.6 修訂——表示瞬間之時間欄一律 timestamptz（不限審計欄）、禁無時區 timestamp；純日曆日期得用 date、須 spec 具名理由（v1.6.0）
date: 2026-09-30
status: accepted
supersedes: []
superseded_by: []
provenance: "user 2026-09-29 聲明（系統可能多國使用、DB 應用 UTC+0）與 2026-09-30 逐題裁定（時區盤點第 5 題：寫成規則並擴大檢查；追問：落點憲法 §I.6）；前代出處：rev5:K1-02（出處 rev4:ADR 0002：DB 層時間欄一律 timestamptz 存 UTC；其「禁 naive datetime」屬 wire 層款）；rev6 §I.6 承自 rev5 憲法 v1.10.0，其 `*_at`＝timestamptz 只位於審計欄標準"
tags: [constitution, amendment, schema, timezone]
---

## 背景

憲法 §I.6「型與約束」只在業務表審計欄標準之下定 `*_at`＝`timestamptz`；`tools/schema-gate.py` 的 audit archetype 斷言也只驗審計欄（created_at／updated_at／deleted_at／archived_at）。非審計時間欄——例：`sys_token` 之 `issued_at`／`expires_at`／`used_at`、`sys_user_email_verify` 之 `verified_at`——現況雖皆為 `timestamptz`（全庫時間欄 29 欄），卻沒有規則阻止新欄改用 `timestamp without time zone`。

前代 datetime 慣例（`rev5:K1-02`，出處 `rev4:ADR 0002`）之 DB 層款為「時間欄一律 timestamptz 存 UTC」（「禁 naive datetime」屬其 wire 層款），rev6 現在式面未承載。

## 決策驅動因子

- 系統可能多國使用；無時區 timestamp 是跨時區部署常見的時間錯亂來源。
- 規則需要機器守衛，不只靠審查。

## 考慮過的替代案

1. **維持現狀（只審計欄有明文與斷言）**——新欄只靠審查把關；否決（user 2026-09-30 裁定）。
2. **規則放 `docs/ops/RULES.md`**——走輕量軌、免修憲，但時間欄規定分散兩處；否決（user 裁定落點憲法 §I.6）。
3. **一律禁 `date`**——純日曆日期（不表示瞬間，例：生日）以 `date` 表意最準；否決，改為須 spec 具名理由。

## 決定

1. 憲法 §I.6「型與約束」新增「時間點欄通則」款：表示瞬間之欄一律 `timestamptz`，不限審計欄；MUST NOT 用 `timestamp without time zone`；純日曆日期得用 `date`，須於該刀 spec 具名理由。
2. 機器守衛：`tools/schema-gate.py check` 擴為全庫時間欄型別斷言——`timestamp without time zone` 一律紅；`date` 欄須列於閘內登記名冊（現為空）方過。
3. 憲法 version 1.5.2 → 1.6.0（§V.3 MINOR：已入憲 invariant 細項調整）。

## 後果

- 正面：新增時間欄之型別有憲法依據與機器守衛；現有 29 欄全數合規、零 migration。
- 負面：新增 `date` 欄須多一步登記。

## 翻案觸發器

- 出現必須以無時區 timestamp 表示瞬間之外部整合需求。
