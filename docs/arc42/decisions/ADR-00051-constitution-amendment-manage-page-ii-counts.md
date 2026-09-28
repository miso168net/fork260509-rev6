---
id: "ADR-00051"
title: 憲法 Amendment 1.5.1→1.5.2——§III.2 ★BASE-WEB-MANAGE-PAGE-WIRING 用途 (ii) 六支 view／元件檔範圍欄「不預估」實數化（兌現 ADR-00042 回填義務）
date: 2026-09-28
status: accepted
supersedes: []
superseded_by: []
provenance: "005-role-menu-crud final holistic review（run wf_5cd4ad17-f03 之 L2-3／L4-2，兩鏡皆確認）；user 2026-09-28 以 AskUserQuestion 親決「再走 PATCH 1.5.2」"
tags: [constitution, amendment, fork-delta, patch]
---

## 背景

ADR-00042（憲法 1.5.0）把用途 (ii) 六支 view／元件檔之範圍欄寫為「處數與塊數 Amendment 時不預估、實數以標記為準」，並於翻案觸發器明定「下一次 §V.2 Amendment 提案 MUST 將用途 (ii) 六支 view／元件檔之範圍欄處數與塊數實數化（表外宣告 1 例外路徑之回填義務）」。下一次 Amendment（1.5.1＝ADR-00048）時點已在 U12／U13 落地之後，卻只校正 captcha.ts 處數、未處理此義務；final holistic review 揭出此缺口。其後 final review 修正另為 `menu-operate-modal.vue` 補兩條修改型標記（排序／頁籤固定序號限整數；user 同日親決），本 Amendment 以修正後之現算為準。

## 決策驅動因子

- ADR-00042 之 MUST 回填義務已到期；範圍欄是授權面的機器可核對口徑。
- 實數化只把數字填實、授權邊界不擴不縮（用途、行為描述、檔級名單不變）。

## 考慮過的替代案

1. **另立 ADR 延後回填至 005 收刀後首次 Amendment**：義務再延一次、範圍欄續留「不預估」；棄（user 親決當刀收）。
   對所選方案跑同一反例（RL-0013）：實數化是否使後續任何正當改動都須修憲？是——此即表外宣告 1「實作期改動同批更新」之既定紀律，與其餘各列同；成立。

## 決定

1. §III.2 ★`BASE-WEB-MANAGE-PAGE-WIRING` (ii) 列範圍欄六支 view／元件檔改為逐檔實數（修改型 `原行:` 處數＋新增型圈界形塊數；量法同表外宣告 1）：`role/index.vue` 6＋2、`role/modules/role-operate-drawer.vue` 6＋4、`role/modules/role-search.vue` 1＋1、`menu/index.vue` 16＋7、`menu/modules/menu-operate-modal.vue` 16＋6、`components/advanced/table-header-operation.vue` 3＋1；兩語 locale 與 `app.d.ts` 之「各 4 塊」不變。用途、行為描述、檔級名單不變。
2. 版本 1.5.1 → **1.5.2**（§V.3 PATCH：範圍欄實數化）。
3. README 憲法版本鏡像同批改（1.5.1 漏改一併補正）。

## 後果

- ADR-00042 之回填義務兌現；範圍欄與 `tools/fork-delta-lint.py` 現算一致（修改型全樹 69 處）。
- 用途 (ii) 六檔此後任何標記增減須同批 Amendment（表外宣告 1）。

## 翻案觸發器

- 用途 (ii) 六檔之修改型處數或圈界塊數再有增減（另立 Amendment 同批更新）。
