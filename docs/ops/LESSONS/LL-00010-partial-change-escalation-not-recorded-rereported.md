---
id: "LL-00010"
rule_id: "RL-0025"
promotion_surface: code
---
LL-00010｜fix「部分改動＋升級」的升級項不入 `escalated`——次輪審查員換措辭重報、碼品質段多跑兩輪

**徵狀**：002 刀 U4 碼品質段（run wf_c074bb86-259）三輪都在同一項上打轉：第 1 輪審查報「contract.rs 兩支 verb-mismatch 案約 40 行逐字複本」，fix 抽出共用 helper 讓新案改用、對 U3 既有案（限定面「既有案零改動」）以 `done_with_escalation` 升級（`filesChanged` 2 支）；第 2 輪審查以新 summary 重報同一項、fix 再升級（仍有其他改動）；第 3 輪再報，fix 零改動升級後才被記入 `escalated`、該段收斂。多兩輪約 45 分鐘、約 70 萬 subagent token；`escalatedBlockers` 最終只回一項。

**成因**：`_sk_cycle.js`（ADR-00013 改形）只在 `done_with_escalation`＋`filesChanged` 為空時把「未駁回的 blockers」記入 `escalated`／`escalatedKeys`；同輪既修了別項又升級一項＝`filesChanged` 非空，升級項不記、次輪審查 prompt 的「已升級清單」不含它、過濾也不動作——審查員重報是合法行為。升級內容只活在 `escalations` 自由文字，script 無從對回 file×summary。ADR-00013 後果段只預期「審查員無視勿重報而換 summary」形（多一輪），未預期部分改動形。

**處置**：fix 回傳 schema 加結構化 `escalatedFindings: [{file, summary}]`（與 `rejectedFindings` 同形、summary 逐字沿用 finding 摘要），`cycle()` 不論 `filesChanged` 數皆據此記入 `escalated`／過濾；零改動分支保留為兜底（agent 漏填時仍成立）；fix prompt 明令升級項 MUST 結構化指名；harness 加一案（部分改動＋結構化升級→次輪重報被過濾、該段收斂）；RL-0025 條文補一句。隨下一顆骨架 commit 落地、U5 起生效。

**晉升面**：code（`tools/orchestration/_sk_head.js`／`_sk_cycle.js`／`harness-test.mjs`）＋RL-0025 條文一句（來源仍 ADR-00013、非翻案：改形只補「升級項的記錄面」、不動「不終止 run」決定）。

**再犯面與守法**：凡 script 以「集合比對」做過濾或收斂判定（已駁回、已升級、blocker 集合），agent 回傳就必須提供**同一鍵形的結構化欄**——不得靠「零改動」這類間接徵狀推斷集合成員；自由文字欄（`escalations`／`report`）只供人讀、不進判定。主線核 run 結果時對照 journal 看同一 file 的 blocker 是否跨輪反覆出現＝過濾失效的徵狀。
