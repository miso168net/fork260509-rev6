---
id: "ADR-00041"
title: 跨刀活體契約自 spec 目錄抽出至 reference-src——五份新家、spec 原檔留凍結存證、現在式面改指新家（兩種書寫形皆機器守）
date: 2026-09-21
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00042（000-r2 C1-3 兩鏡 real 確認／decided 不確定、主線裁定轉 BL）；user 2026-09-21 grilling Q6 裁定「本輪做：抽為活體契約」、Q12 裁定「落點 docs/ops/reference-src/＋射程取機器枚舉」（首版只掃絕對形得六份，`maint-backlog-42` final holistic review 補掃裸相對形後為七份）；同型前例＝ADR-00012（schema 定稿權威自 001 spec 目錄抽出至 reference-src）；語意張力來源＝ADR-00010 決定 4／5 明文指派 contracts/ 為契約權威而 ADR-00012 的原則未擴用亦未具名豁免"
tags: [governance, contracts, materials]
---

## 背景

- RULES 名詞段定 `specs/**` 為**史料面**（不受裸編號、時態、形制掃描）。跨刀活體的契約長住史料面，等於它永遠拿不到現在式面的閘。
- 機器枚舉現在式面對 spec 契約的引用得**七份**契約檔仍被跨刀消費者引著。★枚舉必須同時掃**兩種書寫形**：絕對形 `specs/NNN-…/contracts/…` 與 repo 主流的**裸相對形** `contracts/<檔>.md`——只掃前者會漏掉大多數消費者（本 ADR 首版即因此低估射程，由 `maint-backlog-42` 的 final holistic review 糾正）：
  - `specs/001-schema-baseline/contracts/gates.md` —— RUNBOOK §10（Day-1 三步）、`docs/ops/reference-src/archetype-map.json`
  - `specs/001-schema-baseline/contracts/schema-evolution.md` —— RUNBOOK §10、`tools/schema-gate.py`、`tools/docsync/snapshot.py`、`tools/walkthrough-baseline.py`（兩處）
  - `specs/002-system-settings/contracts/code-gates.md` §1.2 與 `contracts/wire-settings.md` §4 —— `tools/wire-schema.py`（★BL-00042 條文原本漏列此二份，本 ADR 一併納入＝RL-0001 機器枚舉優先於條文點名）
  - `specs/004-ip-trust-anchor/contracts/code-gates.md` §2 —— RUNBOOK §12 碼面閘表
  - `specs/004-ip-trust-anchor/contracts/trust-model-config.md` —— RUNBOOK §16、活書 `docs/arc42/03-context-and-scope.md`、`deploy/trust-model.dev.toml`
  - `specs/001-schema-baseline/contracts/fixtures.md` —— `.githooks/pre-commit`、`tools/schema-gate.py`（裸相對形）
  - `specs/002-system-settings/contracts/code-gates.md` §1.3（fork-delta-lint）與 §4（docsync routes 生成器）、`specs/003-auth-session/contracts/code-gates.md` §2（msg-key-gate）—— `tools/fork-delta-lint.py`、`tools/docsync/references.py`、`tools/msg-key-gate.py`、`.githooks/pre-commit`（皆裸相對形）
- 這些消費者全是**跨刀常設**（工具還在跑、紀律還在生效），其契約會隨刀前進；而 spec 目錄應是該刀的定點快照。

## 決策驅動因子

- 已收刀的 spec 目錄不該再被改（改它＝改別人的定稿），但跨刀契約又必須能前進——兩個需求在同一份檔上互斥。
- repo 已有同構前例與其二分法：`specs/001-schema-baseline/fixtures/`（凍結面）對 `docs/ops/reference-src/schema-snapshot.json`（活體照相），差額由演進帳解釋（ADR-00012）。
- 收錄要有判準，否則整個 `contracts/` 目錄都會被搬走：只收「該消費者是跨刀常設、且其契約會隨刀前進」者；各刀的施工面（pre-commit 改動清單、該刀 ADR 清單、收刀帳本、該刀端點契約）不收。

## 考慮過的替代案

1. **具名豁免**（立 ADR 承認 `contracts/` 就是留在 spec 目錄，ADR-00012 的原則只適用 schema 定稿）：改動面最小；但等於正式放棄「史料面不被活體引用」這條紀律，且每多一刀就多幾份長住史料面的活體契約（004 一刀就新增兩份）。棄。
2. **逐檔抽出**：一對一最好追溯；但其中六處只有單一節是跨刀活體（002 §1.2／§1.3／§4、002 wire-settings §4、003 §2、004 §2），逐檔搬會把該刀的施工面一起搬走、或造出多個幾乎空的檔。棄其形、取其實（見決定 2）。
3. **等首支帶 migration 的刀再做**（BL-00042 觸發欄原文）：本輪不做也不擋 005（rev5 前例 005 零 migration）；但射程每一刀都在長，004 一刀就讓射程從四份變六份。user 2026-09-21 裁定本輪做。棄。

## 決定

1. **落點＝`docs/ops/reference-src/`**（同 ADR-00012 的活體家），新增五份：
   - `schema-gates.md` ← `specs/001-schema-baseline/contracts/gates.md`（整檔）
   - `schema-evolution-contract.md` ← `specs/001-schema-baseline/contracts/schema-evolution.md`（整檔；檔名帶 `-contract` 以避開同目錄既有的資料檔 `schema-evolution.json`）
   - `trust-model-config.md` ← `specs/004-ip-trust-anchor/contracts/trust-model-config.md`（整檔）
   - `schema-fixtures-contract.md` ← `specs/001-schema-baseline/contracts/fixtures.md`（整檔）
   - `code-gate-contracts.md` ← 六處節級併入：§1 ← 002 `code-gates.md` §1.2（wire-schema）／§2 ← 002 `wire-settings.md` §4（快照與覆蓋閘）／§3 ← 004 `code-gates.md` §2（view-render-guard、route-artifact-gate）／§4 ← 002 `code-gates.md` §1.3（fork-delta-lint）／§5 ← 003 `code-gates.md` §2（msg-key-gate）／§6 ← 002 `code-gates.md` §4（docsync routes 生成器）；逐節標凍結存證出處。
2. **收錄判準**（寫進 `code-gate-contracts.md` 檔頭）：該閘／該紀律是跨刀常設，且其契約會隨刀前進。各刀 spec 的施工面節不收。
3. **`specs/**` 原檔零改動**、留為該刀收刀當下的凍結存證，不再前進；兩者自本 ADR 之日起分岔，分岔由新檔與 git 史解釋（同 ADR-00012 決定 3）。四份整檔搬者於建檔當下除檔頭外逐字相同（可 diff 佐證）；隨後於同一批**具名**修正數處，各處於新檔就地註明理由——①現在式面的 GT-05 裸刀名掃描（JSON 範例值改佔位形）②姊妹活體檔互引改指對方新家③左源名改 ADR-00012 的活體定稿 `schema-definition.md`④RL-0020 之「本刀」改刀名形⑤決定 2 所禁的施工面落點清單改指現況真源。除此之外不得再改，日後分岔一律走 git 史。
4. **現在式面改指新家**：處數不寫死字面、一律以決定 5 的機器枚舉為準（本批實改四十二處：絕對形十二、裸相對形二十七、凍結面契約三）；涉及檔＝RUNBOOK、活書 `03-context-and-scope.md`、`README.md`、`.githooks/pre-commit`、`deploy/trust-model.dev.toml`、`docs/ops/reference-src/{archetype-map.json,schema-gates.md,schema-evolution-contract.md}`、`tools/{schema-gate,wire-schema,fork-delta-lint,msg-key-gate,view-render-guard,route-artifact-gate,walkthrough-baseline}.py`、`tools/docsync/{snapshot,references}.py`。併入檔的節號同步重編（002 §1.2→§1、002 wire-settings §4→§2、004 §2①②→§3①②、002 §1.3→§4、003 §2→§5、002 §4→§6）。
5. **機器強制**：GT-06 加一腿——現在式面不得引用 spec 契約，**兩種書寫形皆掃**（絕對形 `specs/NNN-…/contracts/…`＋裸相對形 `contracts/<已抽出檔名>.md`，名冊寫死六個來源檔名）；史料面、ADR body、generated、events 不入射程。具名豁免恰一條：`docs/ops/reference-src/` 的活體檔、以 `> 凍結存證＝` 起首之行（解除謂詞＝該行不再以此起首，或該檔不在 reference-src）。形制與 RL-0077 的 tmp 腿同源。
6. **ADR-00010 決定 4／5 的「contracts/ 為契約權威」不翻案**：該款講的是**該刀之內**的契約權威落點（刀內 SDD 產物），與本 ADR 講的「跨刀活體契約的長期家」不同層；本 ADR 只把跨刀那一類搬出去，刀內契約仍寫在各刀 `contracts/`。

## 後果

- 新增五份人寫活體檔進 `docs/ops/reference-src/`（現在式面），自此受裸編號／時態／引用健康等既有閘掃描——本批一落地即被 GT-05 抓到抄來的 JSON 範例含裸刀名，屬預期效果。
- `specs/001`／`002`／`003`／`004` 的 `contracts/` 自此為凍結存證：日後看「當時怎麼定的」查 spec、看「現在怎麼定的」查 reference-src。
- 下一支帶 migration 的刀不必再回頭改 001 的 spec 目錄（BL-00042 觸發條件消滅）。
- 代價：四份整檔搬在建檔當下與 spec 原檔內容重複；此為 ADR-00012 已採的二分法（凍結存證 vs 活體），非 RL-0049 所禁的鏡像——鏡像是「同一事實兩個現在式家」，而 spec 原檔自本 ADR 起不再是現在式家。

## 翻案觸發器

- **凍結存證無機器守門**：`specs/**/contracts/**` 只靠紀律「不再前進」，無閘擋其被改；若日後出現誤改凍結存證的實例，翻案＝為 spec 契約面加 HEAD 對比腿（形制＝GT-02 的 events append-only 腿）。
- **新舊兩份再分岔無偵測**：五份整檔／節級搬入者與其凍結存證自建檔起即可能各自演化，repo 無機器面比對；若出現「有人照凍結存證施工而與活體不符」的實例，翻案＝建立分岔報表或把凍結存證改為指針。
- **相對形名冊寫死**：決定 5 的裸相對形名冊是六個檔名常數，日後若再抽出第七份而忘了加名冊，該檔的相對形引用即無守；若發生一次，翻案＝改為自 `docs/ops/reference-src/` 的實檔集推導。
