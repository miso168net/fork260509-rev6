---
id: "ADR-00093"
title: unlockLogin 帳號維對範圍外現役帳號回 5003、與查無之 0000 可區辨＝揭露該帳號之存在——包含規則之固有代價、記為 by-design 已知態；「不洩存在性」之射程收窄為「查無與範圍內現役帳號同形」
date: 2026-10-15
status: accepted
supersedes: []
superseded_by: []
provenance: "前代同形未登記：rev5:server/src/handler/throttle.rs 之 `guard_unlock_no_escalation`（查無即提早回成功、查得委派使用者域判定件、範圍外拒＝同一可區辨面；前代未記為已知態）；007-user-password-admin 刀收刀前 final holistic review 之安全面 finding（unlockLogin 帳號維存在性探測面；複核判確認、未拍板）；上游拍板＝ADR-00075 決定 4（帳號維套包含規則）、spec FR-021、spec Clarifications Q2（未鎖標的照寫照回 0000）；as-built＝rust-api/server/src/handler/throttle.rs 之 `judge_account_unlock`（查無或已刪＝T 為空集恆過；查得＝取帳號鎖後經 `handler::user::guard_no_escalation`）；舊宣稱出處＝同檔檔頭與 `judge_account_unlock` doc、活書 §6.1「登入失敗節流——島 E」⑥（本刀收單顆同批收窄）、specs/007-user-password-admin/research.md R9 表與 contracts/wire-user-admin.md 端點 11（史料面、不改）；user 2026-10-15 以 AskUserQuestion 裁定「記為已知態」（建議項）"
tags: [known-state, security, throttle, user-domain, user-password-admin]
---

## 背景

unlockLogin 帳號維自 007 刀起套包含規則（ADR-00075 決定 4）：交易內以帳號名解析現役列——查無或已軟刪＝T 為空集、恆過，照寫稽核與解鎖標記、回 `0000`（冪等契約）；查得＝取該帳號鎖後以 `guard_no_escalation` 判（T＝該帳號之全部指派、N＝T），操作者非 `R_SUPER` 而 T 含其現役角色集以外之角色＝`5003`、零稽核零標記。

兩種回應在 wire 上可區辨：被授 unlockLogin、未被授 getUserList 之委派者送 `{"dimension":"user","userName":"Super"}` 得 `5003`、送不存在之名得 `0000`——等於揭露「該帳號名存在、且持有我未持之角色」。`handler::throttle` 檔頭、`judge_account_unlock` doc 與活書 06 卻寫「查無恆過＝不以異碼洩漏帳號存在性」，此宣稱只對「查無 vs 範圍內現役帳號」成立、對範圍外現役帳號不成立；ADR-00075、ADR-00081、ADR-00082 與 spec 皆未登記此連帶面。

## 決策驅動因子

- 拒絕必須可見：包含規則拒絕若做成與查無同形（回 `0000`），即謊報「已解鎖」——操作者以為已解、使用者仍被鎖。
- 查無恆過是既有冪等契約（spec Clarifications Q2）：改成查無亦拒，等於翻轉該契約。
- 暴險面受限：端點於 seed 只屬 `R_SUPER`，授出非超管為顯式行政動作（006 刀起可經端點權限彈窗授出）。

## 考慮過的替代案

1. **範圍外亦回 `0000`、但不解鎖**：謊報成功、破冪等語意（同一請求之回應與實際狀態不符）。否決。
2. **查無亦回 `5003`**：翻轉查無恆過之冪等契約，且對任意不存在之名一律拒、誤導操作者以為是權限問題。否決。
3. **帳號維收為封死集（只許 `R_SUPER`）**：縮減 006 刀起之授出能力、屬 scope 級變更；現無運維需求支持。否決（列為翻案觸發器）。
4. **行為不變、記為已知態並收窄宣稱**（選）。
   對所選方案跑同一反例（RL-0013）：委派者大量探測範圍外帳號是否無痕？否——`5003` 路徑由 `guard_no_escalation` 落 warn 一則（target `security.user`、`endpoint` 欄＝unlockLogin），`0000` 路徑落操作稽核一列；兩路皆留痕。成立。

## 決定

1. **行為不變**：帳號維對範圍外現役帳號回 `5003`（零稽核零標記）；查無與已刪之帳號名回 `0000`（照寫稽核與標記）。
2. **「不洩存在性」之射程收窄**：只保證「查無／已刪與範圍內現役帳號同回 `0000`」；範圍外現役帳號之存在可由 `5003` 推知＝by-design 已知態。
3. **現在式面同批收窄**：`handler::throttle` 檔頭與 `judge_account_unlock` doc 兩處碼註、帳號維查無案之 doc、活書 §6.1「登入失敗節流——島 E」⑥ 之同句，於本刀收單顆改述為上款之射程並指本 ADR；`specs/007-user-password-admin/` 之 research 表與 contracts 端點 11 屬史料面、不改。
4. **可觀察**：探測留痕於 `5003` 之 warn（`security.user`）與 `0000` 之操作稽核列，查核法同 RUNBOOK §9 管理員解鎖段。

## 後果

- 持 unlockLogin 而未持 getUserList 之委派者，可藉帳號名探知範圍外帳號之存在與「其持有我未持之角色」——所得資訊多於其清單權限。
- 活書 11 技術債表「使用者域與繁中 runtime by-design 已知態」列指向本 ADR。

## 翻案觸發器

- unlockLogin 授出非超管成為常態運維需求，或稽核要求委派者不得知悉範圍外帳號之存在 ⇒ 評估改形（例：帳號維收為封死集，或改以經清單權限取得之 uid 為標的）。
- 包含規則之拒因形變更（ADR-00075 決定 4 翻案）⇒ 複核本 ADR。
