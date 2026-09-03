---
id: "ADR-00010"
title: schema 基線＝rev5 終態逐位元承襲＋受管演進帳閘契約（凍結面／演進面／全等語意／archetype 歸屬／雙源互證）
date: 2026-09-04
status: proposed
supersedes: []
superseded_by: []
provenance: "001 schema 基線刀 brainstorm §7 草案要點（user 拍板 Q1～Q3、2026-09-03）；spec FR-001～FR-003、FR-008～FR-009、FR-014；research R5～R7；前代：rev5:ADR 0006（基線＝壓平＋定稿制）、rev5:ADR 0007（閘契約＝Day-1 受管演進帳）、rev5:001-schema-baseline brainstorm §3 與 contracts/gates.md；憲法 §I.6 四變體。轉 accepted 時點＝U2 收尾（證據段補齊）。"
tags: [schema, gates, rust-api, governance]
---

## 背景

- rev6 資料庫基線＝rev5 終態 15 表（啟動書 D13、001 brainstorm Q1）：rev5 以定稿制（欄序親排、seed 全量過目簽核）落成 `rev5:m001`／`rev5:m002`，
  並以凍結 fixtures＋演進登記檔＋三閘（`rev5:ADR 0007`）守住基線；rev5 八刀期間零 delta migration、演進登記檔終態零筆。
- rev6 拍板：程式內容逐位元承襲（憲法 §I.5 例外②、ADR-00009）、檔名四碼（ADR-00008）、不重開親排與過目工作坊。
- 閘契約若不隨基線同刀就位，基線落地即開始腐化（`rev5:K1-32`／`rev5:K1-39` 教訓：凍結模型被三段鑿洞）。

## 決策驅動因子

- 單一權威：資料形狀的家＝m0001／m0002 本體（程式）＋data-model §2（欄序）＋凍結 fixtures（實庫證據）；三者互證、零容差。
- 兩代同形：UI 對照驗收（CDP 對 rev5 stack 全等）與 entity 漂移閘要求 rev6 與 rev5 資料形狀同一。
- 演進可稽核：日後每支帶 migration 的刀必登記、未登記漂移一律紅。

## 考慮過的替代案

- **容差比對**（允許未登記小差異）——否決：rev4 三段鑿洞重演；「容差」唯一合法形＝演進帳登記。
- **直接拷 rev5 fixtures 當凍結面**——否決：凍結面必須是 rev6 自己重放的證據；拷來即無「rev6 基線＝rev5 終態」實證。改採雙源互證。
- **rename map 血緣核對照搬**——否決：rev6 無 rev4 血緣場景；工具去映射（research R6）。

## 決定

1. **基線**：rev6 資料庫基線＝rev5 終態 15 表（169 欄、索引 38、約束 101、seed 266 列＋9 空表）；`m0001_baseline_schema`／`m0002_baseline_seeds`
   程式內容逐位元承襲 `rev5:m001`／`rev5:m002`（去註解後 diff 全等）、檔名四碼；rev6 第一支 delta 自 `m0003` 起編。
2. **凍結面**＝`specs/001-schema-baseline/fixtures/`（columns／indexes／constraints 三 json＋normalize 後 seed.sql＋provenance）：自 rev6 pristine 重放萃取、
   **永不改寫**；翻案＝新 ADR supersedes＋新 fixtures 目錄；rev5 之刀內重產具名例外不承襲。
3. **雙源互證**：四份資料檔與 `rev5:specs/001-schema-baseline/fixtures/` 同名檔逐位元全等（無 normalize、無映射）方可凍結；不全等＝停手升級 user。
4. **演進面**＝`docs/ops/reference-src/schema-evolution.json`（單一登記檔、kind 八值、每筆帶來源刀編號、初版零筆；契約＝contracts/schema-evolution.md）。
5. **閘語意**＝凍結面 ⊕ 演進面合成期望值後與實庫**全等**、非容差；未登記漂移一律紅；登記檔啟動斷言七條 fail-loud；三閘（結構／欄序＋seed／audit archetype）
   契約＝contracts/gates.md；negative test 五類（含假 delta 合成）先自證。
6. **entity 漂移閘**常跑 pre-commit（快照缺席 Day-1 跳過、就位即實跑；觸發面內 entity 目錄缺席 fail-loud）；schema 三閘手動與 review 輪跑；doccheck 離線對賬
   data-model §2／§6／§9。
7. **archetype 歸屬**：15 表 × 憲法 §I.6 四變體住 `docs/ops/reference-src/archetype-map.json`（承 rev5 同名檔改座標、與 data-model §1 對賬）；真表由 generate 產
   （`docs/generated/reference/schema.md`／`accounts.md`）。
8. **Day-1 常設程序**（RUNBOOK §10）：每支帶 migration 的刀收刀前必跑 refresh＋登記＋三閘綠。

## 後果

- 兩支閘工具依「隨遷工具」紀律自 rev5 整檔搬運（座標同名、去 seed-decision／rename 依賴）；docsync 新增 `refresh`（`snapshot.py`）與兩生成器、GENERATED_FILES 12→14。
- 閘數恆 12：三閘與 entity-drift 屬碼面閘、不入 GATES.md 名冊。
- 基線表集或變體歸屬需改＝新刀 supersedes 本 ADR；閘由全等改容差＝不允許（須新 ADR）。

## 翻案觸發器

- 基線表集／變體歸屬／欄改動（新刀 supersedes、新 fixtures）。
- 雙源互證於 U2 實證不成立且無法歸因於 rev6 側（rev5 fixtures 與其程式不一致）→ 停手、新 ADR 重議凍結面來源。

## 證據（U2 收尾補齊後轉 accepted；accepted 後不可變）

- 17 檔逐位元自證：（待補：命令 rc、檔數、rust-api commit SHA）
- 雙源互證：（待補：四檔 `cmp` 結果、rev5 fixtures 來源 SHA、rev6 provenance 摘要）
- entity 後刀差異清單：`sys_user_role.rs` 兩條真 DB FK Relation（`rev5:002` FR-022）保留；其餘 14 檔零差異（待補：實查結果）
- 三閘首跑：（待補：check rc 0 三閘摘要、test 案數、doccheck rc 0）
