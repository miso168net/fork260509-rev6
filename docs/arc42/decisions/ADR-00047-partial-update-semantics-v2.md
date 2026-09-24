---
id: "ADR-00047"
title: 部分更新語意（續行 ADR-00015）——envelope 級三態續行；角色與選單之可空文字欄空字串＝清空落 NULL（新增同形）、名稱欄空字串與 null 同拒；系統設定寫端「空字串＝設值」續行；提前 no-op 與不可變欄出現形
date: 2026-09-23
status: proposed
supersedes: []
superseded_by: []
provenance: "005-role-menu-crud 之 spec FR-006／FR-007／FR-009（brainstorm R1-Q3、工程判斷 23／30；clarify 2026-09-23 Q5 新增路徑名稱空字串亦拒）；被續行面＝ADR-00015 五款（其決定 1「空字串亦為設值」與決定 5「create 不在射程」為本檔改寫面；body 已 accepted 不可變、rev6 無部分翻案機制＝ADR-00011 決定 5 先例）；前代出處＝rev5:ADR 0023（rev5:002 刀三態約定）＋rev5:B-102（rev5 可空欄空字串＝清空、名稱欄空字串＝不動——名稱欄一半由本檔翻為拒）＋rev5:L-009；draft 於 plan 期落 feature branch、user 親決於 tasks T003（施工前提顆；accepted 同顆補 supersedes 並改 ADR-00015 狀態）"
tags: [wire, envelope, serde, role-menu-crud]
---

## 背景

- ADR-00015 決定 1 規定部分更新請求「欄位值為空字串亦為設值」；角色與選單之寫端承前代形（`rev5:B-102`）要「可空文字欄空字串＝清空落 NULL」——兩者正面衝突。若服從 ADR-00015 現文，角色描述等欄送 `""` 即落空字串、與 NULL 並存於同一欄，「無描述」有兩種表示（upstream 表單清空輸入框送的正是 `""`）。
- 前代對 NOT NULL 名稱欄之 `""` 靜默視同缺席（不動）；rev6 改拒（較誠實：使用者清空名稱卻看到「成功」而名稱未變＝假成功）。
- ADR-00015 決定 5 自明「create 請求……不在射程」，其翻案觸發器第一條即「create 請求語意也要鎖＝新 ADR 擴射程」——本刀新增路徑之可空文字欄同樣要防空字串與 NULL 並存。

## 決策驅動因子

- 同一欄不得有兩種「空」表示（查詢、顯示、唯一性判斷皆受影響）。
- 002 系統設定寫端行為零變化（其 `description` 空字串落空字串之既有案零改形）。
- 語意逐域明文、機器錨逐案可指。

## 考慮過的替代案

1. **服從 ADR-00015 現文**（角色與選單之 `""` 落空字串）：空字串與 NULL 並存、upstream 清空輸入框即產生第二種空；棄。
2. **全 repo 一律 `""`＝清空**（含系統設定）：改 002 既有行為與案、非本刀射程；棄。
3. **名稱欄 `""` 沿前代靜默不動**：假成功；棄（R1-Q3）。

對所選方案跑同一反例（RL-0013）：「逐域不同」是否使前端無法以單一規則送請求？不會——前端表單對可空欄一律送輸入框現值（`""` 或文字），兩域後端各自收斂；系統設定頁本無「清空」UI 需求（其 `description` 由 null 表清空之 API 路徑續存）；成立。

## 決定

1. **ADR-00015 之決定 2～4 原意續行**，現行依據＝本決定：NOT NULL 欄之顯式清空＝拒收、nullable 欄之顯式 null＝落 NULL；解析層承載形＝`Option<Option<T>>`＋`#[serde(default)]`＋自訂反序列化（本刀起為 `handler/common.rs` 之泛型 `tristate<T>`、系統設定寫端之私有 String 版改引）；必填欄亦以寬鬆形承載、缺席或 null 由 handler 判 `2222`（不落框架 400／422 裸 body）；wire 型別對應（寫端請求之 nullable 三態欄 typings 為 `T | null` 可選欄〔快照經 `--strictNullChecks` 忠實呈 `["null","string"]`〕；讀端列型可空欄之 NULL 表示〔缺席或顯式 null〕逐域以各刀契約為準、typings 忠實對應 wire——缺席形之 typings 不含 null、顯式形為 `T | null`；系統設定讀端〔002〕與路由讀端〔003：`MenuRoute`／`RouteMeta`〕為缺席形、005 新增之角色與選單管理讀端〔`RoleRecord`／`MenuRecord`〕為顯式 null 形；讀端 NULL 表示與寫端清空語意各自斷言）；系統設定寫端之機器錨續行（`settingValue` null→`2222 biz.systemSettings.invalidValue`、`description` null 落 NULL）。
2. **envelope 級三態（改寫 ADR-00015 決定 1）**：部分更新請求 body 之每一可選欄——**欄位缺席＝不動；JSON `null`＝顯式清空；有值＝設值**；★空字串之語意**逐域明文**：
   - **系統設定寫端**：空字串＝設值（落空字串）——續行、行為零變化。
   - **角色與選單寫端**：可空**文字**欄之空字串＝清空落 NULL（與 null 同）；NOT NULL 名稱欄（`roleName`／`menuName`）之 null 或空字串＝拒 `nameRequired`；可空**非文字**欄之 null＝清空落 NULL。
   - ★**非三態欄之 null＝缺席**：兩域之 `status`、新增路徑之 `menuType`、選單之 `parentId`（其 0＝頂層）；選單之 `iconType` 為三態狀態類欄、null＝清空落 NULL。逐欄三態與否以各刀契約為準。
3. **提前 no-op**：除 `id` 外之一切欄（含不可變欄）經值域收斂後皆缺席＝成功、零變更、零稽核、不 bump 時戳；**不可變欄只要出現（不論值、含 null）即不屬缺席**、依各域守門拒（`codeImmutable`／`routeNameImmutable`／`menuTypeImmutable`）；承載形＝`tristate::<String>`（null＝出現），非字串值＝body 壞形、依各域收斂（部分更新型＝零變更成功）。
4. **狀態類欄**（角色與選單之 `status`、選單之 `iconType`、僅新增路徑之 `menuType`）：恰二值嚴格解析（trim 後 `"1"`／`"2"`）；值域外（含空字串）＝缺席——新增取預設、更新不動、清單不篩選（null 之語意依決定 2 之逐欄規定：`status`／`menuType` 為缺席、`iconType` 為清空）。
5. **射程（改寫 ADR-00015 決定 5）**：部分更新請求 body＋**角色與選單新增請求之可空文字欄空字串形**（空字串＝NULL、防並存；新增之名稱欄空字串亦拒）；query 參數除決定 4 之狀態類欄值域收斂（值域外＝清單不篩選）外不在射程；非部分更新之寫端（如 `updateRoleHome`＝`home` 缺席、null 或空字串皆清空、同值亦寫）以其契約為準。逐域欄級三態表住各刀契約。

**款號對照表**：

| ADR-00015 決定 | 本 ADR 決定 | 處置 |
|---|---|---|
| 1 三態語意（空字串亦為設值） | 2 | 改寫（空字串逐域明文） |
| 2 NOT NULL 顯式清空＝拒收 | 1、2 | 續行＋擴寫（名稱欄空字串同拒＝決定 2） |
| 3 解析層承載形 | 1 | 續行（泛型件上 common） |
| 4 wire 型別對應 | 1 | 續行＋讀端 NULL 表示逐域明文 |
| 5 射程＝部分更新 body | 5 | 改寫（擴角色與選單新增之可空文字欄） |
| —— | 3、4 | 新增（提前 no-op 與不可變欄出現形；狀態類值域收斂） |

## 後果

- ADR-00015 整顆轉 superseded（`superseded_by` 由 generate 回填）；現在式面引用 ADR-00015 之處（活書 08 §8.2 部分更新句改述兩域語意、frontmatter 藍本值、`handler/system_settings.rs` 八處碼註〔只准改註〕）改指本 ADR 對應款；accepted ADR body 內之引用不動。
- 機器錨：系統設定寫端三態五案零改形全綠（空字串落空字串）；角色與選單寫端各有「可空文字欄空字串→NULL」「名稱欄空字串拒」「新增可空文字欄空字串→NULL」「全缺席 no-op 零稽核」「不可變欄同值出現即拒」案。
- 代價：空字串語意兩域不同、須讀契約；換得同欄零雙重空表示。

## 翻案觸發器

- create 請求允許 null 表「採預設值」等新語意＝新 ADR 擴射程。
- 採 PATCH 動詞或 JSON Patch（RFC 6902）取代 merge 語意＝新 ADR 翻案。
- 系統設定寫端被重寫、或其欄出現「清空」UI 需求 ⇒ 重評該域空字串語意是否向角色選單形收斂。
