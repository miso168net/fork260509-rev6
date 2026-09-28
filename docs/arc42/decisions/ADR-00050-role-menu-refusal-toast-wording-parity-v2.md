---
id: "ADR-00050"
title: 角色與選單拒因譯文對 rev5 之對照口徑（續行 ADR-00049）——`nameRequired` 兩鍵改歸「帶 rev6 語意延伸」、保留 rev6 措辭並入 CDP 排除清單
date: 2026-09-28
status: accepted
supersedes: ["ADR-00049"]
superseded_by: []
provenance: "005-role-menu-crud final holistic review（run wf_5cd4ad17-f03 之 L2-1，兩鏡皆確認）；user 2026-09-28 以 AskUserQuestion 親決「修正歸類」"
tags: [role-menu-crud, i18n, cdp, parity]
---

## 背景

ADR-00049 依「純換句話說者逐字對齊 rev5、帶 rev6 語意延伸者保留 rev6 措辭」之原則分類 18 鍵，但把 `biz.role.nameRequired`／`biz.menu.nameRequired` 歸入純換句話說，en-us 因而改回 rev5 之 'Role／Menu name must not be null'。實則兩鍵帶 rev6 新判定面：rev6 於新增與更新兩條路徑皆拒空字串（ADR-00047、spec Clarifications Q5），rev5 更新路徑遇空字串為「不動」、新增路徑不驗；且 `specs/005-role-menu-crud/contracts/msg-keys.md` 明文要求英文不得只寫 must not be null。ADR-00049 已 accepted、body 不可變，以本 ADR 整顆續行。

## 決策驅動因子

- 沿用 ADR-00049 已由 user 親決之分類原則，只修正誤歸之兩鍵。
- 拒因訊息須如實說明被拒原因（空字串亦拒）。

## 考慮過的替代案

1. **維持 ADR-00049、改寫 msg-keys.md 語意要求以豁免**：英文訊息說「null」而實際亦拒空字串，訊息失實；棄。
   對所選方案跑同一反例（RL-0013）：把兩鍵移入保留集是否使 zh-cn 與 rev5 產生新差異？不會——zh-cn「角色名称不能为空」／「菜单名称不能为空」本即涵蓋空字串、與 rev5 逐字相同，只有 en-us 回 rev6 措辭；成立。

## 決定

1. ADR-00049 決定 1～3 除下列修正外原樣續行（純換句話說者逐字對齊 rev5；`protectedMenu`／`routeNameExists` 與 rev6 新鍵 `hrefInvalid`／`buttonsInvalid` 不變）。
2. `biz.role.nameRequired`／`biz.menu.nameRequired` 自決定 1 移至決定 2 之保留集：en-us 取 'Role name is required and cannot be empty'／'Menu name is required and cannot be empty'；zh-cn 維持與 rev5 相同之「不能为空」；SC-011 排除清單補列兩鍵（en-us 措辭差異）。
3. 保留集因此為六鍵：`biz.role.inUse`、`biz.role.nameRequired`、`biz.menu.constantParent`、`biz.menu.hasChildren`、`biz.menu.notFound`、`biz.menu.nameRequired`。

## 後果

- ADR-00049 轉 superseded（`superseded_by` 由 generate 回填）；現在式面之 ADR-00049 指針改指本 ADR。
- en-us 兩鍵回涵蓋空字串之措辭；CDP 對照之 en-us 該兩鍵與 rev5 不同屬排除。

## 翻案觸發器

- 同 ADR-00049：保留集各鍵所依之判定規則翻案（FR-014／Clarifications Q1／Q5／FR-033／復原現役之回鍵），或決定改以 rev6 自有譯文風格統一全部拒因訊息。
