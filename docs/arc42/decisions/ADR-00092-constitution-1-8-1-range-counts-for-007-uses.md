---
id: "ADR-00092"
title: 憲法 Amendment 1.8.0→1.8.1——§III.2 ★`BASE-WEB-MANAGE-PAGE-WIRING` (v)～(viii)、★`BASE-WEB-LOGIN-CAPTCHA-WIRING` (ii)、★`BASE-WEB-I18N-WIRING` (i)(iii) 範圍欄預估值實數化（兌現 ADR-00074 回填義務）＋I18N (i) 理由欄 helper 簽章記法
date: 2026-10-15
status: accepted
supersedes: []
superseded_by: []
provenance: "前代無對應：rev5 憲法 §III.2 範圍欄無預估值填列形，預估值與其 PATCH 實數化回填義務為 rev6 表外宣告 1 例外路徑之新立；007-user-password-admin tasks T104（ADR-00074 翻案觸發器第三條與後果「回填義務」；`contracts/code-gates.md` §8.1 末列、§8.3；前例 ADR-00051／ADR-00072）；各承載單元出口之 PATCH 清單（U17～U20 base-web commit 訊息之逐用途計數）；I18N (i) 理由欄 helper 簽章＝U20 收尾增列（T091 後 `translateBackendMsg(msg, detail?)`）；user 2026-10-15 以 AskUserQuestion 逐項親決決定 1～12（十二題皆取建議項）"
tags: [constitution, amendment, fork-delta, patch]
---

## 背景

ADR-00074（憲法 1.8.0）於 §III.2 新增 ★`BASE-WEB-MANAGE-PAGE-WIRING` (v)～(viii) 與 ★`BASE-WEB-LOGIN-CAPTCHA-WIRING` (ii) 三列、改寫 ★`BASE-WEB-I18N-WIRING` (i)(iii) 兩列，各列範圍欄以預估值填列（表外宣告 1 之例外路徑；含 `locale.ts`／`naive.ts` 之「預估 0 塊」），並於翻案觸發器第三條明定：收刀前以 §V.2 PATCH Amendment 實數化。

(v)～(viii)、LOGIN-CAPTCHA (ii)、I18N (i)(iii) 已於 007 刀 U17～U20 全數落地。逐用途現算（2026-10-15、base-web `8ca365da`；修改型＝`<軌道>(<用途>) 007-user-password-admin]` 之 `grep -cF`、新增型＝`<軌道>(<用途>)+ 007-user-password-admin START]` 之 `grep -cF`；I18N (i) 之 `request/index.ts` 為 003 刀既有實數、本刀改寫落既有塊內；全檔 `START]`／`原行:` 總數只作交叉核）：逐（用途, 檔）共 25 項，17 項實數＝預估、8 項不等——

- (v) `src/views/manage/user/index.vue`：預估 16 處修改型＋9 塊新增型、實得 13＋8。
- (v) `src/views/manage/user/modules/user-operate-drawer.vue`：預估 22＋16、實得 23＋12。
- (v) `src/views/manage/user/modules/user-search.vue`：預估 2 處修改型、實得 4 處（規則來源之匯入行與取用行連帶改寫，加上手機、信箱兩欄各 1）。
- (v) `src/locales/langs/{en-us,zh-cn}.ts`：預估各 3 塊、實得各 2 塊；`src/typings/app.d.ts`：預估 3 塊、實得 2 塊。
- (viii) `src/views/manage/role/index.vue`：預估 3 處修改型、實得 2 處修改型＋2 塊新增型；`src/views/manage/menu/index.vue`：預估 3 處修改型、實得 1 處修改型＋2 塊新增型。兩檔新增型各為「按鈕碼判準來源之匯入」與「逐鈕顯隱之計算旗標」兩塊，原範圍欄未列新增型。

(v) 三檔與 locale／型別檔之差，出自預估按功能點逐項估、實作將相鄰改點併入同一變更塊，並有單行形新增（不入計數）；(viii) 之差，出自兩檔皆以新增型塊承載按鈕碼判準來源之匯入與逐鈕顯隱之計算旗標（原範圍欄未列新增型）；選單頁表頭新增與批刪兩 prop 之改點另落於 (ii) 既有修改型標記所涵蓋之行（紀律欄已載「不另立本用途標記」），角色頁表頭兩 prop 則自帶本用途修改型標記。8 項皆在各列紀律欄射程內（用途、行為描述、檔級名單不變）。

另 I18N (i) 理由欄記單一 helper 為 `translateBackendMsg(msg)`；U20（T091）起其簽章為 `(msg, detail?)`——業務碼分支之提示鏈傳信封 `data`、只讀明細兩鍵。同欄後文已載「錯誤明細轉譯只限兩鍵」、實義無衝突，記法隨碼面同批改（RL-0011 鏡像）。

## 決策驅動因子

- ADR-00074 之回填義務已到期（收刀前）；留「預估」即令表外宣告 3 之對賬腿跳過本刀各列：現況修改型三元組跳過 25、新增型逐檔跳過 15。
- 實數化只把數字填實、授權邊界不擴不縮：用途、行為描述、紀律欄與檔級名單皆不變；(viii) 補列新增型塊數屬計數形之補全，非新增授權面（該兩檔已在 (ii) 列帶新增型、檔級名單不變）。

## 考慮過的替代案

1. **改碼使實數等於預估**（例：(v) 補拆變更塊、(viii) 把兩塊新增型改寫進修改型標記）：只為湊數，不增任何機器守、反增拆塊或併塊之風險；棄。
   對所選方案跑同一反例（RL-0013）：以實得值實數化後，(viii) 之兩塊新增型是否落在紀律欄射程外？否——兩塊分別為按鈕碼判準來源之匯入與逐鈕顯隱之計算旗標，屬「表格操作鈕依按鈕碼逐鈕顯隱」之實作；`tools/fork-delta-lint.py` 授權判定與圈界成對皆綠。成立。
2. **延後實數化、續留「預估」**：違 ADR-00074 翻案觸發器第三條之 MUST；棄。
3. **版本走 MINOR（1.9.0）**：§V.3 MINOR 款為授權邊界擴展等；實數化不擴邊界，ADR-00074 明定 PATCH，前例 1.5.1／1.5.2／1.7.1 同形；棄。

## 決定

§III.2 七列範圍欄改為逐檔實數（修改型 `原行:` 處數＋新增型圈界形塊數；量法同表外宣告 1、逐用途現算）：

1. LOGIN-CAPTCHA (ii) `src/views/_builtin/login/modules/pwd-login.vue`：3 處修改型（＝預估）。
2. I18N (i) `src/locales/langs/{en-us,zh-cn}.ts` 各 1 塊新增型、`src/typings/app.d.ts` 1 塊新增型（＝預估）；理由欄 helper 記法改 `translateBackendMsg(msg, detail?)`。
3. I18N (iii) `src/typings/app.d.ts` 1 處修改型＋1 塊新增型、`src/locales/locale.ts` 0 塊、`src/locales/naive.ts` 0 塊、`src/locales/dayjs.ts` 2 處修改型、`src/locales/index.ts` 1 處修改型、`src/store/modules/app/index.ts` 2 處修改型（＝預估）。
4. (v) `src/views/manage/user/index.vue`：13 處修改型＋8 塊新增型（預估 16＋9）。
5. (v) `src/views/manage/user/modules/user-operate-drawer.vue`：23 處修改型＋12 塊新增型（預估 22＋16）。
6. (v) `src/views/manage/user/modules/user-search.vue`：4 處修改型（預估 2）。
7. (v) `src/locales/langs/{en-us,zh-cn}.ts` 各 2 塊新增型（預估各 3）、`src/typings/app.d.ts` 2 塊新增型（預估 3）。
8. (vi) `src/views/user-center/index.vue` 2 處修改型＋1 塊新增型、`src/locales/langs/{en-us,zh-cn}.ts` 各 1 塊、`src/typings/app.d.ts` 1 塊（＝預估）。
9. (vii) `src/locales/langs/{en-us,zh-cn}.ts` 各 1 塊、`src/typings/app.d.ts` 1 塊（＝預估）。
10. (viii) `src/views/manage/role/index.vue`：2 處修改型＋2 塊新增型（預估 3 處修改型）。
11. (viii) `src/views/manage/menu/index.vue`：1 處修改型＋2 塊新增型（預估 3 處修改型）。
12. 版本 1.8.0 → **1.8.1**（§V.3 PATCH：範圍欄實數化與理由欄記法）；`Last Amended` 與 Amendment log 同批。

七列之用途、行為描述、紀律欄與檔級名單不變（I18N (i) 理由欄只改 helper 簽章記法）。

- **親決紀錄**：user 2026-10-15 於 007 刀 tasks T104 以 AskUserQuestion 逐項親決決定 1～12（十二題分三批、皆取建議項）。出題面勘誤兩則（不涉決定字面、作答後即向 user 更正）：第 7 項題面之差額成因「預估按三類鍵各 1 塊估」為主線推測、查無紀錄；第 10 項題面把角色頁表頭兩 prop 誤述為落於 (ii) 既有標記行（實為自帶本用途修改型標記；選單頁才是）——本 ADR 背景句以實況為準。另第 1～4 項題面「憲法」誤成鄰近碼位字。

## 後果

- ADR-00074 翻案觸發器第三條之回填義務兌現；表外宣告 3 之對賬腿自動納入本刀各列：以候選字面合成之憲法實跑 `tools/fork-delta-lint.py --constitution`＝修改型三元組對賬 32→57、跳過 25→0，新增型逐檔對賬 14→29、跳過 15→0（產物檔 4 照跳）。
- 七列各檔此後任何標記增減須同批 Amendment（表外宣告 1）。

## 翻案觸發器

- 七列任一檔之修改型處數或圈界塊數再有增減（另立 Amendment 同批更新）。
