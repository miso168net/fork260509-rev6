---
id: "ADR-00057"
title: 系統設定讀端回全部未刪列、不以 registry 鍵集過濾（任一列型別守衛不過即整支 5000）——宣告集外而型別合法之列讀得到、寫端回 2222 為已知態（by-design）
date: 2026-09-29
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00027（002 刀留帳）；user 2026-09-29 裁定（006 前 BACKLOG 體檢 v5 Q1 ①：照舊放行＋立 by-design ADR＋base-web 碼註據實）；前代出處：rev5 讀端只驗認識集（本庫 `rust-api/server/src/validation.rs` 之 `check_type_consistency` 碼註自陳沿之）、rev5:008 設定頁資料驅動（未映射鍵退回後端 description、排組尾、不會憑空消失）"
tags: [product, settings, wire, by-design, known-state]
---

## 背景

系統設定清單 `GET /systemManage/getSystemSettings` 回 `system_settings` 表全部未刪列：handler 逐列轉 wire、不以鍵集過濾，facade 依 `setting_key` 升冪。型別一致性守衛 `check_type_consistency` 對每列三臂判定：①型別字面不在認識集→整支 5000；②已知鍵且宣告字面與庫值不一致→整支 5000；③宣告集外的鍵（庫中多出的列）無宣告可比→放行。寫端 `POST /systemManage/updateSystemSetting` 依序 `find_by_key`→`check_type_consistency`→`validate`，而 `validate` 對宣告集外的鍵回 2222（訊息鍵 `biz.systemSettings.notFound`）。

結果：有人直改資料庫多插一列、型別合法時，該列出現在清單、寫回卻得 2222——讀得到、改不了。宣告集外之列只能源自直改庫：沒有新增鍵的端點，m0002 seed 恰為 registry 16 鍵。base-web `src/service/api/rev6-settings.ts` 讀端 doc 寫「registry 16 鍵固定集」，與第③臂不符。

同類事已有兩個前例：002 刀 FR-009 對「型別不在認識集」與「已知鍵型別不符」定為 fail-loud（5000）、MUST NOT 靜默跳過或降級為警告；ADR-00046 款 7 對 IP 規則清單的未知類型定為照原樣上 wire、不隱藏。006 不碰設定域；008 設定頁依 rev5:008 前例資料驅動。

## 決策驅動因子

- 庫中實有之列不隱藏（ADR-00046 款 7 同向）；真正的資料完整性異常（型別錯）才 fail-loud（FR-009）。
- 宣告集外之列只源自直改庫，常態不發生；為它讓整頁失敗，代價與收益不相稱。
- 008 設定頁依前例資料驅動，能承接外來列；義務不該續掛在 BACKLOG 等到 008。

## 考慮過的替代案

1. **宣告集外之列整支回 5000（與 FR-009 同形）**——直改庫多一列即令設定頁整頁載入失敗、直到該列被刪；把「多一列」與「型別錯」同等處理；否決（user 2026-09-29 裁定①）。
2. **讀端靜默濾除（wire 恆 16 鍵）**——與 FR-009「不靜默跳過」的精神及 ADR-00046 款 7「不隱藏」相反；否決。
3. **暫不裁、隨 008**——現況照舊、義務續佔開放帳；一題即可定；否決（user 裁定①）。

## 決定

1. 設定讀端回 `system_settings` 全部未刪列、不以 registry 鍵集過濾；每列須過型別一致性守衛——任一列 `setting_type` 不在認識集、或已知鍵與 registry 宣告不一致，即整支 5000、不回部分列（002 刀 FR-009，不濾除）。宣告集外、型別合法之列照原樣上 wire、不 fail-loud；常態即 registry 16 鍵。
2. 讀寫不對稱為已知態：宣告集外之列寫端回 2222（`notFound`）；寫端可寫鍵以 registry 為唯一依據（`validate`；界值權威另見 ADR-00054）。
3. 現在式碼註據實：base-web `src/service/api/rev6-settings.ts` 讀端 doc 改為「常態為 registry 16 鍵；宣告集外、型別合法之列照樣上 wire」並指向本 ADR。

## 後果

- 正面：現況成為拍板、BL-00027 結案；零 rust 改碼。
- 負面：008 設定頁若把宣告集外的 number 型列畫成可編輯欄，存檔會得 2222（`biz.systemSettings.notFound`）——由 008 頁面設計承接（例：宣告集外之鍵唯讀顯示）。
- 讀端行為不變：直改庫插一列型別合法的外來鍵，改前改後清單都回 17 列。

## 翻案觸發器

- 設定頁改採鍵硬編（不再資料驅動），或需要讀端鍵集＝registry 鍵集的消費者出現。
- 出現新增或刪除設定鍵的端點。
- registry 鍵集與 seed 分離（例：可選鍵、鍵集隨版本變動）。
