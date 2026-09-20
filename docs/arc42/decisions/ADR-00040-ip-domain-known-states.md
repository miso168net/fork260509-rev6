---
id: "ADR-00040"
title: 004 ip-trust-anchor 已知態集——解鎖無 UI 按鈕／dev 經反向代理可達二態／操作稽核覆蓋不對稱／logout 故障窗弱 oracle／redis 不開持久化／wire 裁判面不開嚴格模式（六款皆 by-design、各附翻案觸發器）
date: 2026-09-20
status: accepted
supersedes: []
superseded_by: []
provenance: "004-ip-trust-anchor brainstorm（Q2 解鎖 API-only、Q5 logout 5000 出口與弱 oracle〔BL-00062、won't-fix〕、設計節「操作稽核首寫不對稱」、風險 6 redis 不開持久化、第二輪 grill ⑦ wire 嚴格模式）；research R7（dev 可達來源信心二態）；憲法 §III.2 BASE-WEB-MANAGE-PAGE-WIRING (i) 列「解鎖按鈕與其包裝不在本次授權」；002 刀 spec FR-016（設定寫端不落稽核列）；ADR-00033（logout 靜默 no-op 之前例）；won't-fix／by-design 亦立 ADR（CLAUDE.md §4）；主線擬稿即 accepted（tasks T064）"
tags: [ip-trust-anchor, known-state, wont-fix, by-design]
---

## 背景

004 刀落地 IP 存取閘、信任錨與來源維節流後，有六處行為是**刻意選擇的現況**而非缺陷。分散記在 brainstorm 與 research 裡，日後的審查輪會一再把它們當 finding 重報；集中立案，讓每一款都有論證與「什麼時候該重新打開」的條件。

## 決策驅動因子

- 已知態要有單一出處，審查輪能一步查到「這是拍板過的」。
- 每一款都必須可到期：沒有翻案觸發器的已知態會變成永久豁免。

## 考慮過的替代案

1. **逐款各立一份 ADR**：六款皆短、同屬一刀一域，拆開只增加索引噪音——棄。
2. **只記 BACKLOG**：BACKLOG 記「待辦」，這六款是「不辦」的決定——棄（其中真有後續工作者另有 BACKLOG 條目、見各款）。
   對所選方案跑同一反例（RL-0013）：合併立案是否讓單款翻案變難？不會——翻案時新 ADR 以 `supersedes` 指向本檔並聲明「某款翻案、其餘續行」（ADR-00032 形）。

## 決定

1. **解鎖端點 API-only、無 UI 按鈕**：`POST /systemManage/unlockLogin` 只有後端端點；前端包裝與按鈕不建。理由：按鈕的自然位置在使用者管理頁，該頁不在本刀；憲法 §III.2 該軌道列明文「解鎖按鈕與其包裝不在本次授權」。按鈕權限碼已在 seed，屆時零 seed 變更。
2. **dev 經反向代理只可達來源信心二態**（`fallback`／`proxy_clean`）：dev 掛最小信任模型、反向代理主動移除 CDN 標頭，其餘信心態由整合測試直餵信任模型覆蓋。端到端走查的結論只對這二態成立；不得把整合層的結論寫成端到端已驗。
3. **操作稽核覆蓋不對稱**：`sys_operation_log` 首寫面＝IP 規則四寫端＋解鎖；既有系統設定寫端維持不落稽核列（002 刀刻意決定）。本刀不回頭補設定寫端。
4. **logout 故障窗弱 oracle（won't-fix）**：DB 故障窗內 logout 對「簽章有效的票」回 `5000`、對垃圾票回 `0000`，可據以分辨票的簽章有效性。只在故障窗可見、只洩持票者手上那張票的有效性、refresh 端點對持票者本即回應可用性；保留 `5000` 使 API 呼叫端知道撤銷未成。折成 `0000` 會把「撤銷未成」回報為成功——不取。
5. **redis 不開持久化**：解鎖標記遺失的後果＝至多少解鎖一次、可再解鎖自癒；節流判定面不依賴 redis（ADR-00038）；會話面暴險由島 C 封頂（PG 為權威）。維持現狀。
6. **wire 裁判面不開嚴格模式**：`tools/wire-schema.py` 抽出的快照零 `additionalProperties`＝後端多帶欄位不會被 JSON Schema 裁判擋下。現況由裁判案的「序列化鍵集＝快照 properties 鍵集」斷言逐型承擔；全域開啟留待專項。

## 後果

- 審查輪遇到上述六款，指向本 ADR 即結案；新發現的同類現象不自動適用、須個案判斷。
- 款 1 與款 6 各有 BACKLOG 條目承載後續工作（解鎖按鈕與前端包裝；全域 wire 守衛）。

## 翻案觸發器

- 款 1：使用者管理頁刀開工。
- 款 2：dev 需要驗 CDN 相關信心態（例如引入本機 CDN 模擬）⇒ 重評 dev 信任模型。
- 款 3：稽核合規需求要求「一切設定變更可追溯」、或系統設定寫端被重寫。
- 款 4：logout 改為需要向呼叫端隱匿撤銷結果的場景出現、或弱 oracle 被證明可組合成實際攻擊。
- 款 5：出現「redis 重啟後狀態遺失」造成的實際事故、或新增不可自癒的 redis 狀態。
- 款 6：出現一次後端欄位外洩而裁判案未擋下的事故、或 wire 型別數量使逐型斷言不可維護。
