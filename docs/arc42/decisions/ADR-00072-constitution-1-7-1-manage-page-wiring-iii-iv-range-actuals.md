---
id: "ADR-00072"
title: 憲法 Amendment 1.7.0→1.7.1——§III.2 ★BASE-WEB-MANAGE-PAGE-WIRING 用途 (iii)(iv) 範圍欄預估值實數化（兌現 ADR-00063 回填義務）
date: 2026-10-04
status: accepted
supersedes: []
superseded_by: []
provenance: "前代無對應：rev5 憲法 §III.2 範圍欄無預估值填列形（凍結樹 7eab28a 之憲法對「預估」零命中），預估值與其 PATCH 實數化回填義務為 rev6 表外宣告 1 例外路徑之新立；006-authz-governance tasks T082（ADR-00063 翻案觸發器第三條與後果「回填義務」；前例 ADR-00051）；U12 實得 `menu-auth-modal.vue` 新增型 6 塊（預估 7）之 user 2026-10-04 親決延至本 Amendment 實數化；user 2026-10-04 以 AskUserQuestion 逐項親決決定 1～8（八題皆取建議）"
tags: [constitution, amendment, fork-delta, patch]
---

## 背景

ADR-00063（憲法 1.7.0）新增 §III.2 ★`BASE-WEB-MANAGE-PAGE-WIRING` 用途 (iii)（三顆授權彈窗接真，含首頁下拉）與 (iv)（授權回收桶頁進場），兩列範圍欄以預估值填列（表外宣告 1 之例外路徑），並於翻案觸發器第三條明定：收刀前以 §V.2 PATCH Amendment 實數化（前例 ADR-00051）。

(iii) 於 006 刀 U12 落地、(iv) 於 U14 落地。逐用途現算（新增型＝`MANAGE-PAGE-WIRING(<用途>)+ 006-authz-governance START]` 之 `grep -cF`；修改型＝`MANAGE-PAGE-WIRING(<用途>) 006-authz-governance]` 之 `grep -cF`；全檔 `START]`／`原行:` 總數只作交叉核）：九格中八格實數＝預估。唯一不等者為 `menu-auth-modal.vue` 之新增型：實得 6 塊、預估 7 塊。差的一塊在首頁讀端 await 之後的世代丟棄：該處與修改型同處一個變更塊，圈界不承重（拔掉標記照綠＝LL-00058），U12 撤去該圈界、改由同處修改型標記涵蓋（同檔現況讀端之同型守衛同形）；user 2026-10-04 親決此差延至本 Amendment 實數化。

## 決策驅動因子

- ADR-00063 之回填義務已到期（收刀前）；範圍欄是授權面的機器可核對口徑，留「預估」即令表外宣告 3 之對賬腿跳過 (iii)(iv) 各檔。
- 實數化只把數字填實、授權邊界不擴不縮：用途、行為描述、紀律欄與檔級名單皆不變。

## 考慮過的替代案

1. **`menu-auth-modal.vue` 改碼補回第 7 塊圈界、使實數等於預估**：該處與修改型標記同處一個變更塊，圈界不承重——拔掉照綠（LL-00058），補回只是形式、不增任何機器守；棄。
   對所選方案跑同一反例（RL-0013）：以 6 實數化，該處世代丟棄行是否失去標記涵蓋？否——它位於修改型標記涵蓋之同一變更塊，`tools/fork-delta-lint.py` 修改型判定綠（106 處授權判定皆合）；成立。
2. **延後實數化、續留「預估」**：違 ADR-00063 翻案觸發器第三條之 MUST，對賬腿續跳 (iii)(iv)；棄。
3. **版本走 MINOR（1.8.0）**：§V.3 MINOR 款為授權邊界擴展等；實數化不擴邊界（用途與檔級名單不變），ADR-00063 回填義務亦明定 PATCH，前例 1.5.1／1.5.2 同形；棄。

## 決定

§III.2 ★`BASE-WEB-MANAGE-PAGE-WIRING` 兩列範圍欄改為逐檔實數（修改型 `原行:` 處數＋新增型圈界形塊數；量法同表外宣告 1、逐用途現算）：

1. (iii) `src/views/manage/role/modules/menu-auth-modal.vue`：14 處修改型＋6 塊新增型（預估 7 塊之差見背景）。
2. (iii) `src/views/manage/role/modules/button-auth-modal.vue`：23 處修改型＋3 塊新增型。
3. (iii) `src/views/manage/role/modules/role-operate-drawer.vue`：3 塊新增型（本用途不帶修改型）。
4. (iii) `src/locales/langs/{en-us,zh-cn}.ts`：各 1 塊新增型。
5. (iii) `src/typings/app.d.ts`：1 塊新增型。
6. (iv) `src/locales/langs/{en-us,zh-cn}.ts`：各 2 塊新增型。
7. (iv) `src/typings/app.d.ts`：1 塊新增型。
8. 版本 1.7.0 → **1.7.1**（§V.3 PATCH：範圍欄實數化）；`Last Amended` 與 Amendment log 同批；README 憲法版本鏡像行同批改。

兩列之用途、行為描述、紀律欄與檔級名單不變。

## 後果

- ADR-00063 翻案觸發器第三條之回填義務兌現；表外宣告 3 之對賬腿自動納入 (iii)(iv) 各列：`tools/fork-delta-lint.py` 修改型三元組對賬 24→33、跳過 9→0，新增型逐檔對賬 14→20、跳過 6→0（產物檔 4 照跳）。
- (iii)(iv) 各檔此後任何標記增減須同批 Amendment（表外宣告 1）。

## 翻案觸發器

- (iii)(iv) 列任一檔之修改型處數或圈界塊數再有增減（另立 Amendment 同批更新）。
