---
id: "ADR-00087"
title: schema 定稿權威留 001 基線（續行並 supersede ADR-00012）——`schema-definition.md` 各節不隨刀前進、其後刀之結構與 seed 變更只登演進帳、現況看實庫照相；表數斷言改屬基線恆真（BL-00047 收）；新表歸屬直接登記 `archetype-map.json`（§1 留基線 15 表）；其餘決定原文續行
date: 2026-10-05
status: accepted
supersedes: ["ADR-00012"]
superseded_by: []
provenance: "007-user-password-admin 之 spec FR-045（schema-definition 不前進、留 001 基線、差額只登演進帳、現況看實庫照相檔；檔頭句同批改寫；表數常數維持＝基線恆真 ⇒ BL-00047 收；ADR⑮ 整支續行並 supersede ADR-00012：決定 2 改為定稿各節留 001 基線、決定 6 之表數斷言改屬基線恆真、其餘決定原文續行、新表之 §1 歸屬登記形與 docsync 缺歸屬訊息同 ADR 寫明）、FR-046（schema-definition 屬 001 基線之「19」等字面不改）、FR-059（schema-definition 檔頭前進句之假述掃除）、FR-060（`backlog_done` 含 BL-00047）、US6 AS2、Key Entities「演進帳與 seed 基線」、Out of Scope「schema-definition 前進、任何 DDL 與新表」；brainstorm §0 GR8（user 拍板：schema-definition 留 001 基線、差額只登演進帳；ADR-00011 決定 5＝rev6 無部分翻案）、§2 BACKLOG 處置（BL-00047 本刀收）、§3 §1 ADR 待立⑮；被續行面＝ADR-00012 決定 1～6 與後果；BL-00047（觸發＝首支帶任何 delta migration 之刀開寫前；本刀 m0003＝首支 delta，ADR-00085）；ADR-00010 決定 1／2／6／7、ADR-00041（跨刀活體契約抽至 reference-src 之同型處置）；rev6 現行件＝`tools/schema-gate.py` 之 `parse_data_model_five`（`len(tables) != 14` 解析自檢）／`compare_column_order`／`cmd_doccheck`／`apply_seed_entries`／audit 表清單守門 finding、`tools/docsync/snapshot.py` 之缺表歸屬 `SnapshotError`、`docs/ops/reference-src/archetype-map.json` 之 `lineage`／`usage`；前代無對應：rev5 之 schema 定稿住 `rev5:specs/001-schema-baseline/data-model.md` 且全代零 delta migration、無基線與演進帳二分之先例；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research R21（ADR 配號與親決時點表）；accepted 同顆於 supersedes 補 ADR-00012 並改 ADR-00012 狀態"
tags: [governance, schema, materials, decision-reversal, user-password-admin]
---

## 背景

- ADR-00012 把 schema 定稿權威自 `specs/001-schema-baseline/data-model.md` 抽至 `docs/ops/reference-src/schema-definition.md`，決定 2 定「§1／§2／§5／§6／§7／§8／§9 抄實體並隨刀前進」，決定 6 定「`!= 14` 硬編碼隨 002 首次加表時由該刀改對」。
- BL-00047 揭兩題（皆以「首支帶任何 delta migration 之刀開寫前」為觸發）：
  - **改對義務失主**：002 刀起至 006 刀皆零加表收刀，決定 6 所指之刀不存在；`len(tables) != 14` 之改對射程另涉同檔多個依 14 之釘值測與 docstring「14 親排表」。
  - **前進與演進帳互斥**：gate2 欄序面（`compare_column_order`）以 §2 為基線再疊演進帳 `add_column`——§2 前進又登 `add_column`＝同一欄重算；doccheck（`cmd_doccheck`）以活體 §2／§6／§9 對凍結 fixtures 比對、不讀演進帳——任一節隨刀前進即報「文件有而 fixtures 無」。§8／§9 亦同：若隨 m0003 把序號落值寫成 164，doccheck §9 對凍結 `seed.sql` 之 setval 163 即紅。
- 本刀 m0003（ADR-00085）為 rev6 首支 delta migration（seed-only、零 DDL）⇒ BL-00047 到期。brainstorm GR8 user 拍板：schema-definition 留 001 基線、差額只登演進帳、現況改看 `schema-snapshot.json`；schema 三閘之比對架構零改動（m0003 新列之序號缺口另由 GR9 補，ADR-00085 決定 7）。
- 現況（2026-10-05）：`schema-definition.md` 檔頭自述「本檔隨每支帶 migration 的刀前進（RUNBOOK §10 Day-1 登記紀律）」，§1 導言「後續刀新表：先補本節歸屬、再登記 archetype-map」；同義之「先補 §1 再登記 archetype-map」另住 RUNBOOK §10 末段、`docs/ops/reference-src/schema-gates.md` §3 兩處、`archetype-map.json` 之 `usage`、`tools/schema-gate.py` audit 表清單守門之 finding 文字、`tools/docsync/snapshot.py` 之缺表歸屬訊息。schema-definition 之 §1 不入任何機器解析（doccheck 只解析 §2／§6／§9）；`archetype-map.json` 為人寫歸屬帳、audit 閘左源。
- rev6 無部分翻案機制（ADR-00011 決定 5：被翻案者整顆轉 superseded）⇒ 改寫決定 2 與決定 6＝整顆續行 ADR-00012。

## 決策驅動因子

- 每個事實只有一個人寫的家（RL-0049）：現況＝基線 ⊕ 演進帳＝實庫照相，不另在定稿檔重寫一份。
- 不留互斥規則：文件前進與演進帳登記不得同時要求。
- schema 三閘與 doccheck 之比對架構零改動（GR8）。
- 讀者找得到現況：檔頭指明現況之家。

## 考慮過的替代案

1. **§2／§6／§9 照前進、改 doccheck 疊演進帳合成、gate2 欄序扣除已入 §2 之 `add_column`**：改動比對架構（違 GR8）；同一事實住兩個人寫的家（定稿檔與演進帳）。否決。
2. **只改衍生數**（§2 標題之欄數、§6 總計行隨刀改）：表體不前進而標題前進＝自相矛盾、解析自檢即紅。否決。
3. **只改決定 6、決定 2 不動**（部分續行）：rev6 無部分翻案機制。否決（整顆續行）。
4. **閘改自 §2 標題解析宣告數、不再硬編碼 14**（BL-00047 所列候選）：§2 既永為基線、宣告數恆 14，改了無收益，反失常數之自檢強度。否決。
5. **只有 §1 前進（新表歸屬續補本節）**：§1 不入機器解析、不生互斥；但檔頭成為「一節前進、餘節基線」之混合形，且新表歸屬同時住 §1 與 `archetype-map.json` 兩個人寫的家、兩者無機器對賬。否決（新表歸屬之家＝`archetype-map.json`，決定 7）。

對所選方案跑同一反例（RL-0013）：
- 「定稿留基線，讀者失去現況」？現況＝`docs/ops/reference-src/schema-snapshot.json`（refresh 照相）與其生成鏡像 `docs/generated/reference/schema.md`；差額逐筆住演進帳；檔頭明指。成立。
- 「日後加表，定義住哪」？演進帳 `add_table`（全欄）＋`add_index`／`add_constraint`、歸屬登記 `archetype-map.json`；gate1 合成含欄序（`add_table` 帶 ordinal）、audit 表清單守門以 map 為左源。gate2 欄序面維持 14 親排基線表；gate2 seed 面之 `add_table` 合成未內建＝現行 fail-loud、由首支加表之刀擴閘（工具訊息已指此路）。成立。
- 「`add_column` 仍會重算」？§2 永不前進 ⇒ 基線欄序＋`add_column` 接末位恰一次。成立。
- 「doccheck 仍會報差」？活體 §2／§6／§9 與凍結 fixtures 同為 001 基線 ⇒ 恆等。成立。

## 決定

1. **整顆續行並 supersede ADR-00012**（ADR-00011 決定 5）：ADR-00012 決定 1～6 之逐條處置見本 ADR 決定 2～6；新表登記形、檔頭句、不改面與 ADR-00012 後果段之讀法見決定 7～10。
2. **ADR-00012 決定 1 原文續行**（讀法：本檔仍是 rev6 現行之人寫左源；其內容固定為 001 基線定稿；現況＝左源 ⊕ 演進帳＝右源 `schema-snapshot.json`；歸屬面另居 `archetype-map.json`）。
3. **ADR-00012 決定 2 改寫**：十節編號照舊齊全（`## N.` 節邊界解析不變）；§1／§2／§5／§6／§7／§8／§9 抄實體並**留 001 基線、不隨刀前進**；§3／§4／§10 之指針形不變；其後各刀之結構與 seed 變更一律只登演進帳（RUNBOOK §10 Day-1 登記三步）。
4. **ADR-00012 決定 3 原文續行**（`specs/001-schema-baseline/data-model.md` 零改動、為 001 收刀當下之凍結史料；讀法：自本 ADR 起兩檔之節內容不再分岔——兩者皆為 001 基線）。
5. **ADR-00012 決定 4、決定 5 原文續行**（子庫三處「定稿憑據」註解不改；左源座標之改指——`DATA_MODEL` 常數、pre-commit `schema-frozen` 觸發面、RUNBOOK §10、`archetype-map.json` 之 `lineage`、arc42 §8.1——續有效）。
6. **ADR-00012 決定 6 改寫**：表數斷言（`parse_data_model_five` 之 `len(tables) != 14`）改屬**基線恆真**——§2 永為 001 基線之 14 親排表、常數不隨加表改；同檔依 14 之釘值測（真 repo 兩案、摘要字面「14 親排表逐位全等」、合成 14 表 fixture）與 docstring「14 親排表」續真、不改；解析自檢強度保留。BL-00047 由本款與決定 3 兌現、收刀時 `backlog_done`。
7. **新表登記形**（本刀不加表；寫明供首支加表之刀照行）：
   - ①結構＝演進帳 `add_table`（全欄）＋該表之 `add_index`／`add_constraint`；②歸屬＝直接登記 `docs/ops/reference-src/archetype-map.json`（人寫歸屬帳、audit 閘左源；`note` 欄載來源刀與理由）——schema-definition §1 不補、留基線 15 表；③欄序由 gate1 之 ordinal 比對承擔、gate2 欄序面維持 14 親排基線表；④gate2 seed 面之 `add_table` 合成未內建＝fail-loud、由首支加表之刀擴 `tools/schema-gate.py`；⑤審計欄與時間欄通則照憲法 §I.6、ADR-00060。
   - 缺歸屬訊息與導言同義句改寫為「新表歸屬登記 `archetype-map.json`（schema-definition §1 留 001 基線＝本 ADR）」：`tools/docsync/snapshot.py` 之缺表歸屬 `SnapshotError`、`tools/schema-gate.py` audit 表清單守門之 finding 文字、`archetype-map.json` 之 `lineage`／`usage`、`docs/ops/reference-src/schema-gates.md` §3 之左源句與表清單守門句、RUNBOOK §10 末段、schema-definition §1 導言。
8. **schema-definition 檔頭句改寫**（FR-045、FR-059）：「本檔隨每支帶 migration 的刀前進」改為「本檔各節留 001 基線、不隨刀前進；其後各刀之結構與 seed 變更只登演進帳（`m0003` 起）；現況看 `schema-snapshot.json`（人讀鏡像 `docs/generated/reference/schema.md`）」。基線字面（§2 欄數、§6 總計、§8 之 266 列與 `casbin true×19`、§9 之落值）MUST NOT 改（FR-046）。
9. **不改面**：schema 三閘與 doccheck 之比對架構（seed_add 序號合成屬 ADR-00085 決定 7、與本 ADR 正交）；凍結 fixtures；ADR-00010（其決定 7「與 data-model §1 對賬」讀為基線 15 表之對賬，後刀新表以 `archetype-map.json` 為唯一家）。
10. **ADR-00012 後果段之讀法**：「002 起新表先補定稿 §1 再登記 map」由決定 7 取代；「定稿內容在兩處各有一份」續真（兩處皆基線）；「凍結存證無機器守門」之已知殘留不變。

- **親決紀錄**：user 親決 2026-10-06（007 刀 tasks T003 施工前提顆）——本輪逐款一題一問呈決定 1～10、皆照文定稿；零非建議項 ⇒ 決定節免改寫；原決定節首之草稿標記改由本紀錄承載；`supersedes` 與 ADR-00012 之 status 依決定 1 於本顆補改。

## 後果

- BL-00047 之兩題同時消解：表數常數恆真、無改對義務；文件前進與演進帳之互斥消失（doccheck 恆比基線對基線、gate2 欄序面不重算）。
- 現況之讀法單一：基線看 schema-definition、差額看演進帳、合成結果看照相與其生成鏡像；schema-definition 不再是「現況」。
- 首支加表之刀之施工面縮為：演進帳＋`archetype-map.json`＋（如需）擴 gate2 seed 面合成；不再回頭改定稿檔。
- 現在式假述之同單元改寫（RL-0011；種子四形皆跑、處數以 `python3 tools/docsync errata <詞>` 現算、改完復掃；ADR 檔與史料面不動）：「隨每支帶 migration 的刀前進」「隨刀前進」（schema-definition 語境）、「先補 data-model §1」「先補 schema-definition §1」「先補本節歸屬」、「與 data-model §1 對賬」（現在式面）；「14 表」「14 親排表」字面（活書 05／08、`schema-gates.md`、`rust-api/entity/src/lib.rs` 模組 doc）續真、不改。
- 現在式面引 ADR-00012 為現行依據之處改指本 ADR；引其為形制出處之史述（「形制承 ADR-00012」類）保留；2026-10-05 已知命中面＝RUNBOOK、README 樹、`docs/ops/reference-src/` 之契約檔五支、`tools/schema-gate.py` docstring、`tools/docsync/snapshot.py`（缺表歸屬訊息與其 docstring）、BL-00047 條文（收刀刪列）——逐處判讀、處數以 `python3 tools/docsync errata ADR-00012` 現算；accepted ADR body 內之引用不動、讀時併讀本 ADR。

## 翻案觸發器

- 演進帳筆數增長至「基線 ⊕ 演進帳」難以人讀（或合成射程不足以表達某次變更）⇒ 依演進帳契約 §3 基線翻案（新 fixtures＋清空 entries＋新 ADR），屆時本檔可隨新基線重寫一次。
- 出現須人寫之現行 schema 敘事而生成鏡像不足以承載 ⇒ 另立生成物或活書節、不回頭令本檔前進。
- 首支加表之刀發現 `archetype-map.json` 之 `note` 不足以承載歸屬理由 ⇒ 複核決定 7②。
- 判定 spec 目錄或 reference-src 之定稿應改為隨刀前進（推翻「基線＋演進帳」二分）⇒ 本 ADR 連同 ADR-00010 決定 4／5 重審。
