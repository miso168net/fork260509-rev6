---
id: "ADR-00056"
title: 組裝形 workflow 每支 agent 的模型家恆為 opus[1m]／xhigh、不隨主線 session effort——拍板入 ADR，TDD 形與 review 形 harness 皆以寫死字面機器守
date: 2026-09-29
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00127（user 2026-09-29 指示先記 BACKLOG、另排輕量軌）；user 2026-09-29 裁定（維持 xhigh、補 ADR 明文與 TDD 形守衛）；前例：模型家拍板於 2026-09-04 定形、2026-09-23 全角色換 opus（maint-orchestration-opus-all），兩次皆只住 `tools/orchestration/_sk_head.js` 註解與 git log；前代無對應：rev5 的編排 script 住 gitignored 工作區，其凍結樹（7eab28a）對 `*_OPTS`／`effort:` 常數零命中，模型家未曾入 ADR 或受版控碼"
tags: [governance, orchestration, model-family, harness]
---

## 背景

`tools/orchestration/assemble.py` 組出的 workflow（TDD 形與 review 形）每支 agent 的 model 與 effort，取自 `tools/orchestration/_sk_head.js` 的七個 `*_OPTS` 常數（`IMPL_OPTS`／`REVIEW_OPTS`／`FIX_OPTS`／`LENS_OPTS`／`MIRROR_OPTS`／`GRADER_OPTS`／`CRITIC_OPTS`），現值全為 `{ model: 'opus[1m]', effort: 'xhigh' }`。Workflow 工具的 `agent()` 帶 `effort` 時以之為準，不帶時沿用主線 session 的 effort。2026-09-29 以 agent transcript 每輪記錄的 `effort` 欄實測（當時主線 effort＝max）：組裝形六支 run 每輪皆為 xhigh，未帶 effort 的兩支 script 每輪皆為 max。

這個值是模型家拍板的一部分，但拍板只住 `_sk_head.js` 註解與 git log，ADR 全集與 RULES 對 `xhigh`／`opus[1m]` 零命中。守衛也不對稱：review 形 `tools/orchestration/harness-review.mjs` 案 1 斷言每支 agent 為 opus[1m]／xhigh，TDD 形 `tools/orchestration/harness-test.mjs` 則沒有任何 model／effort 斷言——`IMPL_OPTS`／`REVIEW_OPTS`／`FIX_OPTS` 被改，組裝三道自檢與 pre-commit 編排段照樣全綠、改動靜默生效。生成表 `docs/generated/reference/agents.md` 只忠實鏡像常數字面、不判對錯。

## 決策驅動因子

- 模型家是跨刀的編排拍板：每支 agent 的思考深度、牆鐘與 token 都受它支配，改動應可見、可追溯、有意識地翻案。
- 主線 session 的 effort 可隨時切換；編排結果不應隨主線當下設定漂移（同一 unitdef 兩次發射應可比）。
- 兩形守衛應對稱：review 形已守、TDD 形缺席。

## 考慮過的替代案

1. **不帶 effort、沿用主線**——編排的思考深度隨主線 session 設定漂移，且與 user 2026-09-29「維持 xhigh」裁定相反；否決。
2. **七常數改 max、與主線一致**——user 2026-09-29 裁定維持 xhigh；max 的牆鐘與 token 預期增加，且無同工作量對照實測支撐其收益；否決。
3. **只補 harness 斷言、不立 ADR**——守衛有了，但拍板仍只住碼註，翻案時無處記「為何改」，違「新拍板→ADR」；否決。
4. **harness 期望值自 script 常數推導**——等於拿常數比常數自己，常數被改仍綠；否決（見決定 2）。

## 決定

1. 組裝形 workflow（`assemble.py` 組出之 TDD 形與 review 形）每支 agent 之 model＝`opus[1m]`、effort＝`xhigh`，由 `_sk_head.js` 七個 `*_OPTS` 常數明寫；明寫值蓋過主線 session 的 effort（主線為 max 時亦同），不隨主線。
2. TDD 形 `harness-test.mjs` 與 review 形 `harness-review.mjs` 皆斷言每支 agent 之 model／effort＝決定 1 之值，期望值以字面寫死、不自 script 常數推導。TDD 形另設反例（RL-0080）：逐一把 `IMPL_OPTS`／`REVIEW_OPTS`／`FIX_OPTS` 之 effort 改為 max、以同一全路徑樁重跑，偏離須非空且恰落在該角色；常數行形一改而變異未套用即紅。
3. 換模或改 effort＝翻案本 ADR（新檔 supersede），同批改 `_sk_head.js` 常數與兩支 harness 之斷言字面，並以 `python3 tools/docsync generate` 重算 `docs/generated/reference/agents.md`。
4. 射程只及組裝形：未經 `assemble.py` 組裝、`agent()` 不帶 effort 的 script 沿用主線 session effort，不在本決定內。

## 後果

- 正面：模型家拍板有 ADR 出處；TDD 形三常數被改即在組裝自檢（`assemble.py` 第③道）與 pre-commit 編排段當場紅，與 review 形對稱。
- 負面：日後換模多一道 ADR 翻案手續；兩支 harness 各寫一次期望字面，由決定 3 綁在同一批同改。
- `docs/generated/reference/agents.md` 的生成邏輯不變（仍鏡像 `*_OPTS` 字面）。`tools/orchestration/EXAMPLE-dual-implementer.mjs` 屬 001 刀 U1 組裝當時的成品快照（其 `IMPL_OPTS` 仍為 fable），不經 harness，不受本決定約束。

## 翻案觸發器

- user 決定換模型家或改 effort 級別。
- Workflow 工具的 effort 語意改變（例：`agent()` 帶 effort 不再蓋過主線，或 effort 級別名改變）。
- `opus[1m]` 別名的解析方式改變，使 harness 字面比對誤紅或失去意義。
