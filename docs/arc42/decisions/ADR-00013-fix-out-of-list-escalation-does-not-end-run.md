---
id: "ADR-00013"
title: fix 清單外零改動升級不終止 run——該段收斂帶升級項、碼品質段照跑、已升級項重報過濾
date: 2026-09-05
status: accepted
supersedes: []
superseded_by: []
provenance: "rev5:L-078（原分支＝fix 零改動升級即當場 return）；002 刀 U1 五輪確認 run 實證（每輪一項文件面清單外 finding 即終止、碼品質段四輪未跑到；LL-00006～LL-00008）；user 拍板 2026-09-05（三選項一題：改骨架分支／維持原規則／改允許清單，選改骨架分支）"
tags: [orchestration, workflow, review]
---

## 背景

- 編排骨架 `_sk_cycle.js` 承 rev5:L-078：fix agent 判本輪 findings 全落允許檔清單外而正確零改動、回 `done_with_escalation` 時，script 當場 return 升級主線（置於「連兩輪零改動」偵測之前，免把正確的防呆⑥反應判成故障）。
- 代價在 002 刀 U1 現形：五支確認 run 各被**一項**文件面清單外 finding（數量詞、tasks 回填條、README 查詢表列、預告承載單元、R12 表對齊）在規格段終止，碼品質段四輪未跑到；每輪 35～45 分鐘、約 60 萬 subagent token，主線改完文件再發下一支。
- CLAUDE.md §2 對 implementer 之 `done_with_escalation` 語意本就是「照常跑完審查再連同升級項回」（rev5:L-035）；fix 迴圈卻是另一套（終止），兩處不對稱。

## 決策驅動因子

- 清單外 finding 依 RL-0022 本來就歸主線收尾處理；run 為它終止、再由主線重發只跑審查段的續跑 run，是純粹的往返成本。
- 碼品質審查是每單元唯一一次對碼面的獨立審視；被文件面小缺口擋在門外＝品質段對 U1 整整五輪缺席。
- 收斂偵測（RL-0004⑤）比較的是 blocker 集合；已升級主線的 blocker 若再被重報，會被誤判成不收斂——改形必須同時處理這一腿。

## 考慮過的替代案

1. **維持原分支**（任何升級即終止、主線改完再發續跑 run）：最保守；但 U3～U8 幾乎每單元都會再多一支確認 run。棄。
2. **改允許清單**（把 `tasks.md`／`research.md` R12 以限定式納入各單元 fix 清單、讓 agent 自己落文件面項）：省往返，但計畫真源由 agent 改寫、與「specs/** 史料面／主線持有」的分工相違。棄。
3. **改骨架分支**（本決定）：清單外零改動升級＝該段收斂帶升級項進下一段；升級項隨最終結果回主線、主線在收尾 commit 處理。採。

## 決定

1. `cycle()` 對 fix `done_with_escalation`＋零改動：把本輪**未被駁回**的 blockers 記為「已升級主線」（`escalated`）；本輪零駁回＝無事可再審→該段當場判**收斂帶升級項**（`converged: true`、`escalatedOnly: true`）進下一段；有駁回項→續下一輪 review（帶已駁回清單、RL-0071）由審查員核駁回是否成立。
2. review prompt 附「前輪已升級主線之 findings 清單」（`escalatedBlock`，與已駁回清單並列）：明令勿重報；同 file×summary 之重報由 script **過濾不計**——不進 fix、不進收斂比較、不擋收斂。
3. 最終結果新增 `escalatedBlockers`（兩段合併）與 `escalatedStages`；`escalations` 併入兩段 fix 的升級文字。主線收尾①復核時逐條處理，並於收尾 commit 訊息列處置。
4. 此分支仍置於零改動偵測之前；零改動偵測只服務 status ok 的真空轉（RL-0025 改寫）。
5. harness 案 10 改為驗「該段收斂帶升級、進下一段」，新增案 11 驗「升級＋駁回續審、已升級項重報過濾」；十案→十一案。

## 後果

- 每單元省掉至少一支只為文件面缺口而發的確認 run；碼品質段不再被規格段的清單外項擋住。
- 主線責任不變但時點後移：清單外項在單元收尾 commit 一併處理（原本是 run 終止當下）。最終結果 `status: 'ok'` 帶非空 `escalatedBlockers`＝主線 MUST 逐條處理，不得因 ok 而略過。
- 若審查員無視「勿重報」而以**新 summary** 重述同一升級項，過濾失效、進 fix 後 fix 會再次零改動升級——仍收斂（第二次升級亦記入 escalated），只多一輪；不致死迴圈（fix 迴圈上限與保險絲不變）。
- 保險絲值不變：本改形不增加任何段的最壞派發支數。

## 翻案觸發器

- 出現「升級項被主線漏處理」事例（收尾 commit 未列處置、後續單元審查重抓同一項）＝主線責任後移的代價成真，重審是否改回終止形或加機器守（收尾 commit 訊息對賬 escalatedBlockers）。
- 若日後允許清單機制改為「計畫文件納入 fix 清單」，本決定的前提（清單外＝主線持有）改變、一併重審。
