---
id: "ADR-00109"
title: 憲法 Amendment 1.9.0→1.9.1——§III.2 ★`BASE-WEB-MANAGE-PAGE-WIRING` (ix)(x) 範圍欄預估值實數化（兌現 ADR-00099 回填義務）
date: 2026-10-28
status: accepted
supersedes: []
superseded_by: []
provenance: "前代無對應：rev5 憲法 §III.2 範圍欄無預估值填列形，預估值與其 PATCH 實數化回填義務為 rev6 表外宣告 1 例外路徑之新立；008-audit-settings-pages tasks T173（ADR-00099 決定 9、10、12 與翻案觸發器第三條；spec FR-060 末句、FR-061 末款、SC-014；`contracts/code-gates.md` §1.2、§2.8、§7.1；前例 ADR-00051／ADR-00072／ADR-00092）；各承載單元出口之 PATCH 清單（U14、U15 收單 commit 訊息之逐用途計數；U7 收單之 I18N (i)(ii)(iii) 零增塊復核）；user 2026-10-28 以 AskUserQuestion 逐項親決決定 1～7"
tags: [constitution, amendment, fork-delta, patch]
---

## 背景

ADR-00099（憲法 1.9.0）於 §III.2 新增 ★`BASE-WEB-MANAGE-PAGE-WIRING` (ix)（系統設定頁進場）與 (x)（稽核頁進場）兩列，範圍欄以預估值填列（表外宣告 1 之例外路徑），並於翻案觸發器第三條明定：收刀前以 §V.2 PATCH Amendment 實數化；實數與預估相符亦須去「預估」，使其轉入對賬。

(ix)(x) 已於 008 刀 U14、U15 落地。逐用途現算（2026-10-28、base-web `cee0f78f`；以 `tools/fork-delta-lint.py` 之解析器逐（軌道, 用途, 檔）計修改型 `原行:` 處數與新增型圈界塊首數，另以 `<軌道>(<用途>)+ 008-audit-settings-pages START]` 之 `grep -cF` 逐檔交叉核）：逐（用途, 檔）共 6 項，6 項實數皆＝預估、0 項不等——

- (ix) `src/locales/langs/en-us.ts`：預估 2 塊新增型、實得 2 塊（`route:` 樹與 `page:` 樹各一）；修改型 0 處。
- (ix) `src/locales/langs/zh-cn.ts`：預估 2 塊、實得 2 塊；修改型 0 處。
- (ix) `src/typings/app.d.ts`：預估 1 塊、實得 1 塊（`Schema.page` 之 `manage.systemSettings` 型節）；修改型 0 處。
- (x) `src/locales/langs/en-us.ts`：預估 2 塊、實得 2 塊；修改型 0 處。
- (x) `src/locales/langs/zh-cn.ts`：預估 2 塊、實得 2 塊；修改型 0 處。
- (x) `src/typings/app.d.ts`：預估 1 塊、實得 1 塊（`Schema.page` 之 `manage.audit` 型節）；修改型 0 處。

同檔其餘用途列之塊數同批逐用途復核：I18N (i)(ii)(iii) 與 MANAGE (i)～(vii) 於三檔之注記皆＝實數；三檔新增型塊首總數（不分軌道與用途、對賬腿口徑）`en-us.ts` 19、`zh-cn.ts` 19、`app.d.ts` 15，各＝該檔全部用途列注記合計。I18N (i) 之 `src/service/request/index.ts`（實數列、對賬腿常時守）復核＝2 處修改型＋2 塊新增型、相符；理由欄 helper 記法 `translateBackendMsg(msg, detail?)` 與碼面現簽章 `translateBackendMsg(msg: string, detail?: unknown)` 相符、不改。各承載單元出口之 PATCH 清單（U7：I18N 三列零增塊；U14：(ix) 兩語各 2、型別檔 1；U15：(x) 兩語各 2、型別檔 1、與預估全等）逐項核＝與現算相符。

## 決策驅動因子

- ADR-00099 之回填義務已到期（收刀前）；留「預估」即令表外宣告 3 之對賬腿跳過 (ix)(x)：現況修改型三元組跳過 6（兩列各三檔）、新增型逐檔跳過 3（兩語 locale 與型別檔整檔跳過＝同檔他用途之塊數增減亦失機器守）。
- 實數化只把注記轉入對賬、授權邊界不擴不縮：用途、行為描述、紀律欄與檔級名單皆不變。

## 考慮過的替代案

1. **改碼使實數符合他值**：實數已＝預估，無湊數之需；任何改碼只增風險、不增機器守；棄。
   對所選方案跑同一反例（RL-0013）：以實得值實數化後，有無任何塊落在紀律欄射程外、或因轉入對賬而轉紅？否——以候選字面合成之憲法實跑 `tools/fork-delta-lint.py --constitution` rc 0、範圍欄計數皆合、授權判定與圈界成對皆綠。成立。
2. **延後實數化、續留「預估」**：違 ADR-00099 翻案觸發器第三條之 MUST，且三檔續整檔跳過對賬；棄。
3. **版本走 MINOR（1.10.0）**：§V.3 MINOR 款為授權邊界擴展等；實數化不擴邊界，ADR-00099 決定 12 明定收刀前 PATCH，前例 1.5.1／1.5.2／1.7.1／1.8.1 同形；棄。

## 決定

§III.2 (ix)(x) 兩列範圍欄數量段去「預估」改為實數（新增型圈界形塊數；量法同表外宣告 1、逐用途現算）：

1. (ix) `src/locales/langs/en-us.ts`：2 塊新增型（＝預估）。
2. (ix) `src/locales/langs/zh-cn.ts`：2 塊新增型（＝預估）。
3. (ix) `src/typings/app.d.ts`：1 塊新增型（＝預估）。
4. (x) `src/locales/langs/en-us.ts`：2 塊新增型（＝預估）。
5. (x) `src/locales/langs/zh-cn.ts`：2 塊新增型（＝預估）。
6. (x) `src/typings/app.d.ts`：1 塊新增型（＝預估）。
7. 版本 1.9.0 → **1.9.1**（§V.3 PATCH：範圍欄實數化）；`Last Amended` 與 Amendment log 同批。

兩語 locale 實數相等，注記沿用「各 2 塊」合併形（不拆逐檔注記）。兩列之用途、行為描述、紀律欄與檔級名單不變。

- **親決紀錄**：user 2026-10-28 於 008 刀 tasks T173 以 AskUserQuestion 逐項親決決定 1～7（七題分兩批 4＋3、皆取建議項：決定 1～6 照實數定稿、決定 7 照 diff 定稿）；送出前擬稿比對 hook 兩批皆過、送出後自紀錄解碼核題面字面零差（44 欄）；出題錯字 0。

## 後果

- ADR-00099 翻案觸發器第三條之回填義務兌現；表外宣告 3 之對賬腿自動納入 (ix)(x)：以候選字面合成之憲法實跑 `tools/fork-delta-lint.py --constitution`＝修改型三元組對賬 57→63、跳過 6→0，新增型逐檔對賬 26→29、跳過 3→0（產物檔 4 照跳）。
- 兩列各檔此後任何標記增減須同批 Amendment（表外宣告 1）；三檔整檔轉入對賬，他用途列之塊數增減亦於 commit 時即受機器守。

## 翻案觸發器

- 兩列任一檔之修改型處數或圈界塊數再有增減（另立 Amendment 同批更新）。
