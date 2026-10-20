---
id: "ADR-00104"
title: IP 域已知態集（續行 ADR-00082）——款 3 改寫：操作稽核寫入者以現行全集重述（擴列系統設定寫端、手動清理自記、排程清理自記），封閉詞彙八詞→九詞（`purge`）；其餘款續行（現行七款）
date: 2026-10-21
status: proposed
supersedes: []
superseded_by: []
provenance: "008-audit-settings-pages 之 spec FR-020、FR-027、FR-036、FR-061⑥；brainstorm §0 D1（ADR-00082 款 3 觸發器：設定寫端改落稽核）、grilling g2／g5；plan 期 research R8.4、R10.1；被續行面＝ADR-00082 款 1～8（body 不可變；續行鏈 ADR-00069→ADR-00082→本 ADR）；前代：rev5:ADR 0079（動作詞 `purge` 小寫之前代拍板）、rev5:server/src/handler/audit.rs（手動清理自記形）"
tags: [ip-domain, audit, known-state]
---

## 背景

ADR-00082 款 3 以現行全集重述操作稽核寫入者並定封閉詞彙八詞；其「系統設定寫端維持不落列」於 D1 後失真，且本刀新增兩種清理自記與一個動作詞。

## 考慮過的替代案

1. **只增列不重述全集**——讀者須併讀兩 ADR 才得全集；否決（ADR-00082 形：以現行全集重述）。

對所選方案跑同一反例（RL-0013）：「全集漏列某寫入者」→以 `write_in_txn`／`write`／`write_system_in_txn` 三入口之呼叫點機器枚舉核對（U17）；不成立。

## 決定

本 ADR 續行並將 supersede ADR-00082（accepted 同顆補 supersedes、ADR-00082 status 改 superseded）。款號一對一沿用：款 1 空號（續）；款 2、4～8 原文續行；**款 3 改寫**：

- **寫入者全集**＝ADR-00082 款 3 所列各寫端（IP 規則四寫端、解鎖端點兩維、角色寫端、選單寫端、三維授權寫端、授權回收桶復原、使用者域寫端八支、個人中心改密）＋**系統設定寫端**（`update`、`system_settings`、`entity_id` NULL、整列快照）＋**手動清理**（`purge`、目標表名、`entity_id` NULL、`{table, before_days, deleted_count}`）＋**排程清理**（`purge`、同上加 `job`；操作者空、來源位址哨兵 `0.0.0.0`＝ADR-00101 決定 5）。
- **封閉詞彙九詞**：`add`、`update`、`delete`、`restore`、`unlock`、`kick`、`reset_password`、`change_password`、`purge`（只在尾端追加；字面釘值測同改）。
- 入口三支：交易內 `write_in_txn`、裸連線 `write`（解鎖來源維）、系統程序 `write_system_in_txn`（排程清理）。
- **非寫入者**（改寫 ADR-00082 款 3 同段）：刪「既有系統設定寫端維持不落稽核列」；m0003 與 m0004 之 seed 基線層改列不落操作稽核（島 G 之 G2 末句；ADR-00085、ADR-00108 決定 4）；token-reap 不落自記（ADR-00101 決定 3）；policy-reconcile 零寫入（ADR-00101 決定 6）；讀端（含 getPasswordPolicy 與稽核四讀端）不落；包含規則、seed 保護、本人規則與各業務守門之拒絕腿皆零列（續行）。⇒ 查詢端不得據此表宣稱「所有管理操作皆有稽核」（續行）。

## 後果

- ADR-00082 轉 superseded；現在式引用面改指本 ADR（機器枚舉、改完復掃）。

## 翻案觸發器

沿 ADR-00082 翻案觸發器各款；另：出現第二個系統程序自記者 ⇒ 重評系統具名型之成員與哨兵射程。

## 親決分類

依 ADR-00089（RL-0086）；類別定義同 ADR-00099 本節。

| 款 | 類別 | 出處或理由 | 白話一句 |
|---|---|---|---|
| 決定節導言 | 承決 | ADR-00082 款 1～8；supersede 簿記＝GT-04 | 舊 ADR 各款續行，只改第 3 款。 |
| 款 3 寫入者全集 | 承決 | brainstorm D1、g2、g5；spec FR-020、FR-027、FR-036 | 會寫操作日誌的地方多了設定變更、手動清理與排程清理。 |
| 款 3 九詞 | 承決 | spec FR-020 | 動作詞多一個 purge。 |
| 款 3 非寫入者 | 承決 | ADR-00082 款 3；brainstorm D1；spec FR-027（設定寫端改落）、FR-039 末段（m0004 seed 基線層）、FR-032（token-reap 不自記）、FR-035（對賬零寫入） | 不寫操作日誌的：種子資料改列、回收過期登入票、授權對賬、讀取，以及被擋下的操作。 |
| 款 3 入口三支 | 工程 | research R8.4（系統程序入口之形制＝spec FR-036「形制 plan 期定」） | 寫入有三個入口，排程清理走專用入口。 |
| 其餘續行款 | 承決 | ADR-00082 同號款 | 其餘已知態照舊。 |

- **親決紀錄**：（plan 期）獨立核對（ADR-00089 決定 5；2026-10-21）：5 列中相符 4（決定節導言、款 3 九詞、款 3 入口三支、其餘續行款）、改正 1（款 3 寫入者全集：括號列舉漏三維授權寫端、原款「非寫入者」段未處置）；處置＝補列三維授權寫端、立「非寫入者」子項並入表；改過之款於轉 accepted 前依 ADR-00089 決定 6② 復核。
