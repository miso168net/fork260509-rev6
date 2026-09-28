---
id: "ADR-00049"
title: 角色與選單拒因譯文對 rev5 之對照口徑——純換句話說者逐字對齊 rev5、帶 rev6 語意延伸之四鍵保留 rev6 措辭並入 CDP 排除清單
date: 2026-09-28
status: superseded
supersedes: []
superseded_by: [ADR-00050]
provenance: "005-role-menu-crud U16 CDP 三方對照（T089 揭出 `biz.role.*` 拒因 toast 措辭與 rev5 不同、T090 同形）；user 2026-09-28 以 AskUserQuestion 兩題親決"
tags: [role-menu-crud, i18n, cdp, parity]
---

## 背景

005 刀新增的 24 支 msg key 中，`biz.role.*`／`biz.menu.*` 之 zh-cn、en-us 譯文由各單元 implementer 自寫，CDP 對照時兩語各有 18 鍵措辭與 rev5 22080 不同。spec SC-011 要求 toast 文案逐項全等，排除清單只列 `protectedMenu`／`routeNameExists` 兩鍵的譯文改寫（兩者因 rev6 語意擴張而刻意改寫）。18 鍵分兩類：一類語意與 rev5 相同、只是換句話說；另一類的措辭多說了一條 rev6 spec 已定、rev5 沒有的判定規則。

## 決策驅動因子

- SC-011 以 rev5 為 UI 對照基準；無語意差的措辭漂移不應放寬判準。
- 拒因訊息須如實說明被拒原因；rev6 新增的判定面若不寫進訊息，使用者看不出為何被拒。
- 譯文之家仍為三檔 locale（ADR-00039），本決策只定對照口徑，不另立譯文表。

## 考慮過的替代案

1. **全部改回 rev5 措辭**：語意延伸四鍵之訊息將不再說明 rev6 規則（例：刪除只掛停用帳號之角色只見「仍掛有用戶」）；棄。
2. **全部保留 rev6 措辭並放寬 SC-011**：無語意差之漂移亦被放行、判準失去意義；棄。
   對所選方案跑同一反例（RL-0013）：分類是否會把語意差誤歸為換句話說而丟失資訊？四鍵各有 spec 依據逐一核過（下列），其餘鍵之 rev6 措辭所多出者皆為 rev5 同一判定面之改寫；成立。

## 決定

1. **純換句話說者逐字對齊 rev5**：zh-cn 12 鍵（`role.codeInvalid`／`codeExists`／`notFound`／`seededProtected`／`cannotDeleteSelfRole`／`cannotDisableSelfRole`／`nameRequired`、`menu.parentNotFound`／`cycleDetected`／`nameRequired`／`routeNameInvalid`／`restoreConflict`）、en-us 14 鍵（上列扣 `seededProtected`〔en-us 本已相同〕、另加 `role.codeImmutable`、`menu.routeNameImmutable`／`menuTypeImmutable`）。`zh-tw.ts` 不接 runtime、不在對照面，不隨改。
2. **帶 rev6 語意延伸之四鍵保留 rev6 措辭**，SC-011 排除清單補列：`biz.role.inUse`（掛載數不濾使用者啟停與軟刪＝FR-014）、`biz.menu.constantParent`（清除自身常量性時反查常量後代＝Clarifications Q1）、`biz.menu.hasChildren`（子項不論啟停＝FR-033）、`biz.menu.notFound`（對現役選單復原亦回本鍵＝US3 AS4）。
3. 既列之 `protectedMenu`／`routeNameExists` 與 rev6 新鍵 `hrefInvalid`／`buttonsInvalid` 不變。

## 後果

- CDP 對照之拒因 toast 除排除清單所列外與 rev5 逐字全等；spec SC-011 與 tasks T090 排除清單同批補四鍵。
- 往後新刀若新增之 msg key 與 rev5 同鍵同語意，譯文以 rev5 措辭為起點；帶語意延伸者須於該刀 SC 排除清單具名。

## 翻案觸發器

- 四鍵所依之判定規則翻案（FR-014／Clarifications Q1／FR-033／復原現役之回鍵）。
- 決定改以 rev6 自有譯文風格統一全部拒因訊息（屆時放棄 rev5 逐字對照）。
