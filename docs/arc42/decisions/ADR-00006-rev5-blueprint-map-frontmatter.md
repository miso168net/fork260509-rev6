---
id: "ADR-00006"
title: rev5 藍本對照表——去處住 arc42 節檔 frontmatter `rev5_blueprint`、生成器只排缺列不斷言（一次性 migrate-audit、非常駐閘）、`##` 一併入表、rev5 ADR 不入
date: 2026-09-03
status: accepted
supersedes: []
superseded_by: []
provenance: "啟動書 §1 DoD 第 5 點、§3.7 藍本表首列、§5 波 3 列、R2-F19；user 拍板 2026-09-03（波 3 brainstorm Q1／Q2）"
tags: [governance, generated, rev5]
---

## 背景

- 啟動書把 rev5 活書定為 rev6 的藍本（D2）：不搬、逐節消化；波 3 出口要有一張對照表 `docs/generated/reference/rev5-blueprint-map.md`——rev5 活書每個標題在 rev6 的去處（rev6 節／隨刀／不承襲附理由），缺一即紅、一次性 migrate-audit（R2-F19：非常駐閘）。
- `docs/generated/**` 依 RL-0049 只能是機器生成，而「去處」是 20 筆人的判斷——必須先定人寫的家，生成器再從那裡讀。
- 啟動書三處措辭不一：§1 與 §3.7 寫「每個 `###`」、§5 波 3 列寫「`###` 與 ADR」；rev5 ADR 依 D5 不遷、備用摘要住 tmp。

## 決策驅動因子

- 每個事實只有一個家（RL-0049）：對照表若另有人寫表，「本節承了 rev5 哪節」就有兩個家。
- 既有機制先用：波 2 已有兩個「frontmatter → 生成索引」前例（`summary`→ARCHITECTURE.md、`rad_ai_map`→RAD-AI-MAP），`parse_front_matter` 已認一層巢狀對映。
- 閘數固定 12（D8、GT-12）；R2-F19 已拍非常駐——不能在 generate 裡藏一道第 13 閘。
- rev5 樹凍結（ADR-00002、bootstrap 單腿斷言 SHA）：名冊字面不可能漂移，一次核對即足。

## 考慮過的替代案

1. **人寫一張表 `docs/ops/rev5-blueprint.md`、生成器讀表重排**：一檔看全貌；但生成檔幾乎是該表鏡像、節檔本身看不出承了 rev5 哪節——棄。
2. **不生成、人寫表即正典＋tmp 腳本一次對賬**：零工具；但 tmp 波 5 清掉後對賬無法重跑、啟動書的 generated 路徑作廢——棄。
3. **生成器自斷言、對不上即 rc 1**：守得最緊；但實質是一道常駐閘藏在 generate 內、不在 GATES.md 名冊、與 R2-F19 相抵——棄。
4. **名冊常駐測試對 rev5 檔逐字核（skip-if-absent）**：rev5 凍結已由 bootstrap 單腿守著，常駐測試多餘且他機會 skip——改為一次性核對、結果記於本檔證據段。

## 決定

1. **真源＝arc42 節檔 frontmatter `rev5_blueprint:`**（一層巢狀對映）：鍵＝rev5 標題字面、值＝`承襲（…）`／`隨刀：<刀類或憲法 §I.7 島>`／`不承襲：<理由>`；住同號 rev6 節檔（rev5 §N → `docs/arc42/NN-*.md`），不承襲的理由也住「本該承接它的那一節」。
2. **名冊＝`references.REV5_BLUEPRINT`**：rev5 活書 12 個 `##`＋8 個 `###`＝20 列（`##` 一併入表是 §1／§3.7「每個 `###`」的超集）；rev5 ADR 不入表（D5）。
3. **生成器 `references.gen_rev5_blueprint_map` 只排列、永不拋錯**：未宣告列「缺」、多檔宣告標「重複」、鍵不在名冊列「未知鍵」、值不以三詞起頭標「形制」；檔尾一行四項計數。「缺一即紅」＝波 3 出口 checklist 一條（四項皆零才准 bump 波標記）、結果寫進收單事件；不加閘、不加規則。
4. **名冊字面核對＝一次性**：對凍結 rev5 檔跑一次、結果記於本檔證據段；不設常駐測試。
5. GENERATED_FILES 名冊 10→12（本表＋`reference/agents.md`；後者照啟動書 §3.2 P-E2 列自 `tools/orchestration/*.js`／`*.mjs` 的 `*_OPTS` 字面生成、非本檔決策）。

## 後果

- arc42 節檔的 `###` 標題或 rev5 標題字面若改（rev5 已凍結、實際只可能是 rev6 側改鍵），generate 即多出「未知鍵」或「缺」列——看得見但不擋；波 3 之後誰刪鍵，GT-01 逼他重算、diff 裡就是那一列。
- frontmatter 多一個鍵；`rev5_blueprint` 只住 `docs/arc42/NN-*.md`，`docs/process/`、`docs/c4/` 不用。
- 生成檔內的去處欄是 Markdown 連結（GT-06 連結腿掃 generated）——只指已存在的節檔。

## 翻案觸發器

- rev5 樹解凍或 rev6 arc42 重新編號（同號對應失效）→ 重評名冊與去處住址。
- 出現第二代藍本（rev6 之後）→ 重評「一次性 migrate-audit」是否改為常駐對賬。

## 證據（一次性核對、2026-09-03）

- 命令：`grep -nE '^(##|###) ' ../fork260509-rev5/docs/arc42/ARCHITECTURE.md`（唯讀）→ 20 行；以 python 對 `references.REV5_BLUEPRINT` 逐字比對（字面＋層級）＝**20／20 全等**；rev5 HEAD `7eab28a`（bootstrap 同 SHA 斷言）。
