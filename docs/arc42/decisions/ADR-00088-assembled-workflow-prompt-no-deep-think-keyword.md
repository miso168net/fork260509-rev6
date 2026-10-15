---
id: "ADR-00088"
title: 組裝形 workflow 的 agent prompt 不帶深思關鍵詞——思考深度只由 effort 承載，兩支 harness 以寫死字面守
date: 2026-10-06
status: accepted
supersedes: []
superseded_by: []
provenance: "user 2026-10-06 裁定（007 刀實作前、於 007 分支施作；007 刀 U1 為首支受影響之組裝形 run）；前例：深思關鍵詞自編排骨架收斂為單一骨架（2026-09-04）起烤在 review／fix prompt 首行、2026-09-23 擴及 implementer（輕量軌 maint-orchestration-opus-all），兩次拍板皆只住 `tools/orchestration/` 碼註與 git log、未入 ADR；前代：rev5 凍結樹（7eab28a）之 rev5:006-authz-governance research／tasks 編排慣例列記「review＝opus 1m xhigh（prompt 帶 ultrathink）」，rev6 承之；rev5 編排骨架未入庫、無機器守"
tags: [governance, orchestration, model-family, harness]
---

## 背景

`tools/orchestration/assemble.py` 組出的 workflow（TDD 形與 review 形）原本在每支 agent 的 prompt 首行放深思關鍵詞 `ultrathink`：`_sk_head.js` 一個常數，由 `_sk_main.js`（implementer）、`_sk_cycle.js`（review／fix）與 `_sk_review.js`（lens、探針、兩鏡、grader、refuter、critic）烤入。user 在主線 session 輸入這個字時，Claude Code 會附加「要求加深推理」的提示；拍板當時預期子代理同樣受益。

2026-10-06 以本機 agent transcript 實測，子代理並未出現這個機制：

- Workflow 工具把 script 渲染的 prompt 包進「computed task」框架，註明非 session user 輸入、不具 user 權限；關鍵詞以縮排文字夾在框架內。
- 最近六支組裝形 run（63 支 agent，其中 53 支首則訊息含該字）的加深推理提示 0 次；同機主線 session 由 user 輸入該字時則有。另四支手寫 workflow run（77 支 agent）亦為 0 次。
- 上述六支組裝形 run 每輪記錄的 effort 欄 5329 筆全為 xhigh、無 max。

即該字在子代理只是一般文字，思考深度實際由 `*_OPTS` 的 effort 決定（ADR-00056）。這個拍板也與 ADR-00056 背景點名的缺口同形：只住碼註與 git log，ADR 全集零命中。

## 決策驅動因子

- 思考深度應只有一個可見、可追溯、有機器守的控制點；在子代理中無可觀測效果的字樣，讓「深度由什麼決定」看似有兩個來源。
- 拍板入 ADR、兩形 harness 守衛對稱，與 ADR-00056 同一治理形。
- 007 刀 U1 是下一支組裝形 run，改動在其發射前落地即可於該 run 活體確認。

## 考慮過的替代案

1. **維持現狀**——無可觀測的機制效果，且拍板無 ADR 出處；user 2026-10-06 裁定拿掉；否決。
2. **常數保留、值改空字串**——留下無用常數與空首行，日後改回非空值時沒有任何守衛；否決。
3. **刪除但不加 harness 斷言**——關鍵詞可被靜默加回，組裝自檢與 pre-commit 照綠；否決。
4. **改 effort 為 max 以補償**——無證據顯示關鍵詞曾提高深度，且 ADR-00056 已定 xhigh；否決（要改 effort 走 ADR-00056 翻案）。

## 決定

1. 組裝形 workflow 每支 agent 的 prompt 不帶深思關鍵詞 `ultrathink`（不分大小寫）；思考深度只由 `_sk_head.js` 七個 `*_OPTS` 的 effort 承載（ADR-00056 決定 1 不變）。
2. TDD 形 `harness-test.mjs` 與 review 形 `harness-review.mjs` 的案 1 斷言每支 prompt 不含該字面（不分大小寫）；期望字面寫死在 harness、不自 script 常數推導。案 1 派發涵蓋全部角色（TDD 形 implementer／review／fix；review 形兩支入庫範例合計 lens、探針、兩鏡、grader、refuter、critic）。施作時先改 harness、後改骨架，做一次變異自證：舊骨架的四種組裝成品各恰紅此一斷言、且點名全部角色；改骨架後全綠。不另設常駐反例案（兩支 harness 案數不變）。
3. 射程：機器守只及組裝形。未經 `assemble.py` 組裝的手寫 script 比照不帶，無機器守、由主線自律。
4. 恢復帶關鍵詞或改用其他深思字樣＝翻案本 ADR（新檔 supersede），同批改骨架與兩支 harness 斷言。

## 後果

- 正面：思考深度的控制點單一（effort）；關鍵詞被加回時，組裝第③道自檢與 pre-commit 編排段當場紅。
- 負面：未做「帶／不帶」的對照實測；若該字對模型仍有文字層面的影響，子代理推理可能略淺。實測顯示無機制效果，判此風險小，不設量化觀察門檻。
- `tools/orchestration/EXAMPLE-dual-implementer.mjs` 為 001 刀 U1 成品快照、仍含該常數；它不經 harness，不受本決定約束（同 ADR-00056 後果之處置）。
- `docs/generated/reference/agents.md` 不鏡像該常數，生成邏輯不變。

## 翻案觸發器

- 帶／不帶關鍵詞的對照實測顯示，子代理推理深度或審查品質有可觀測差異。
- Workflow 工具改為對 computed task 內的關鍵詞觸發加深推理。
- ADR-00056 翻案（effort 語意或級別改變），連帶重估本決定。
