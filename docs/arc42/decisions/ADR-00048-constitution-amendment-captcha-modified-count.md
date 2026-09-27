---
id: "ADR-00048"
title: 憲法 Amendment 1.5.0→1.5.1——§III.2 ★BASE-WEB-AUTH-WIRING (c) 列範圍欄 captcha.ts 修改型處數 3→5（fork-delta-lint 改逐值比次數後揭出之既有缺漏補錄）
date: 2026-09-27
status: accepted
supersedes: []
superseded_by: []
provenance: "005-role-menu-crud U13 碼品質審查升級（fork-delta-lint `find_missing` 以集合判定、非唯一基線行被刪改而缺 `原行:` 照綠）→ U13b 改逐值比次數；user 2026-09-27 以 AskUserQuestion 親決「本刀收」"
tags: [constitution, amendment, fork-delta, patch]
---

## 背景

`tools/fork-delta-lint.py` 的 `find_missing` 原以**集合**判定「基線某行是否仍在我方檔」：同檔尚有其他同字面行時，被刪改的那一行永遠算「仍在」，缺 `原行:` 標記也照綠。005 刀 U13 碼品質審查以選單頁表頭 `原行: />` 實證此缺口（拔除該標記或改其原行值，三道判定皆綠）。U13b 把判準改為逐值比次數（基線次數 > 我方存留次數＋有效記錄次數＝缺；我方次數不計新增型圈界塊內行），隨即揭出 `base-web/src/hooks/business/captcha.ts`（003 刀 `BASE-WEB-AUTH-WIRING` (c) 軌道）兩處自 003 刀起即缺錄的刪改：被刪的 Promise 閉合行 `});`、原本無條件執行而移入圈界塊內條件式的 `start();`。兩處均補修改型註解標記（碼行零改）；拔除任一條新判準即紅。

憲法 §III.2 表外宣告 1 規定範圍欄處數以 `rev6-inline` 標記實數為準、實作期改動同批更新；(c) 列範圍欄現寫「3 處修改型」，實數已為 5。

## 決策驅動因子

- 範圍欄是授權面的機器可核對口徑；與實數不符即授權描述失準。
- 兩處皆為真缺漏（變異自證：拔除即紅），不是量法誤差；補錄只加註解、零碼改、零行為變更。
- 表外宣告 1 之同批更新義務適用於實數列（(c) 列不屬「不預估」列）。

## 考慮過的替代案

1. **延至 005 收刀後的輕量軌**：本刀撤回兩條標記、lint 對該兩行加具名豁免、記 BACKLOG 一條。不取——BACKLOG 淨流量 +1，且 lint 帶臨時豁免期間之缺漏仍在。
2. **撤回 lint 次數比對**：不取——已知零機器守缺口留在碼面。

## 決定

1. §III.2 ★`BASE-WEB-AUTH-WIRING` (c) 列範圍欄改為「`src/hooks/business/captcha.ts`（5 處修改型＋1 塊新增型）」；用途、行為描述、檔級名單不變。
2. 版本 1.5.0 → **1.5.1**（§V.3 PATCH：文字校正——範圍欄實數化，授權邊界不擴不縮）。
3. 005 刀 spec FR-058 與 contracts/code-gates.md §1、tasks T076／T082／T100 之「base-web 改動恰為用途 (ii) 九檔」變更檔集斷言，同批把 `src/hooks/business/captcha.ts` 列為具名例外（只補修改型註解標記、碼行零改）。

## 後果

- captcha.ts 之修改型處數與憲法範圍欄一致；fork-delta-lint 逐值比次數後全掃描面修改型標記零守 0 條。
- 005 刀 base-web 變更檔集多一支「只改註解」之既有檔，由上列具名例外承載。
- 史料面（ADR-00026、specs/003、specs/004 所載之 3 處）不改——過去式住 git 與史料。

## 翻案觸發器

- captcha.ts 之修改型改動再有增減（範圍欄須同批更新，另立 Amendment）。
- fork-delta-lint 判準再變而使補錄之兩條標記不再必要（屆時以新判準現算、另立 Amendment 校正）。
