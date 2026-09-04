---
id: "ADR-00004"
title: RULES.md 首版 73 條與數量上限——總 92、per-scope 實算 ＋25%；六件套與看門狗紀律入 RULES；agent 面不可違反項自 CLAUDE.md 範本補列
date: 2026-09-03
status: superseded
supersedes: []
superseded_by: [ADR-00011]
provenance: "啟動書 §3.6／D8（附錄 F R2-F12／R2-F13 採）＋user 拍板 2026-09-03（計畫 grill：六件套與看門狗紀律全入 RULES、RULES-VERSION 全 script 必帶）＋user 審表 2026-09-03"
tags: [governance, rules, budget]
---

## 背景

- 啟動書 §3.6 定規則層形制：每條＝`RL-NNNN｜規則（命令句、無刀名、無行話、≤2 行）｜scope｜carrier｜source（必須存在）`；
  `docsync rules emit --scope <s>` 輸出規則塊＋`RULES-VERSION`，編排骨架改為呼叫此命令、PreToolUse hook 對賬版本串。
- D8 治理預算：內容配額退役（無行數配額）；治理面數量預算形制固定＝**超限只擋新增、不可調數字、一進一出或走 ADR**；
  RULES 條數上限＝波 1 實算去重後 ＋25%（60 為佔位）、每 scope 另設上限。rev5 診斷：治理是只加不減的棘輪
  （29 條 lint 塞 14,827 行單檔、CLAUDE.md §2 通道塞滿）。
- 候選來源：①`tmp/rev5-handoff/rev5-rules-digest.md` 37 條（30 已晉升＋5 候選＋2 無家）②RAD-AI adoption-guide §8
  **七條** Pitfall（實檔只有 Pitfall 1～7；全部中文改寫、D15）③啟動書 §3.8 末段文件治理程序條款（三材質、時態、完成即刪、
  ID 配號、lint 運作模式、權威鏈）④rev6 過渡版 CLAUDE.md §2 編排範本之不可違反項與 `tools/orchestration/_sk_rules.js` 11 條（agent 面）。
- 憲法 1.0.0（ADR-00003）先於本 ADR 落地：§I.4／§I.8／§V.1 是 RL-0043／0044／0047／0065 的 source。

## 決策驅動因子

- 單一規則層：agent prompt 的規則塊由機器產出、hook 對賬，人不再手維護 `_sk_rules.js` 陣列。
- 通道容量由條數管、不由行數管；每條有 `source` 可追溯（GT-08 反向腿首版即非空集合）。
- 骨架改吃 emit 之後，凡不在 RULES 的 agent 面規則即從 prompt 消失——表必須涵蓋現行 `_sk_rules.js` 與 §2 範本全部不可違反項。

## 考慮過的替代案

1. **照搬 rev5 CLAUDE.md §2 全段為規則**：通道重塞滿、行話與刀名帶入、無 source 欄——棄。
2. **只收 RAD-AI 七條 Pitfall＋程序六條**（約 13 條）：丟失 rev5 37 條已驗證防法、六件套與看門狗無家——棄。
3. **計畫草案 62 條**（六件套與看門狗入 RULES、agent 面不可違反項留在 CLAUDE.md §2 範本）：Task 12 骨架改吃 emit 後
   11 條 agent 面規則（rev5 樹唯讀、agent 不動 git、先讀 rev5 碼、TDD 先紅後綠、變異三紀律、可見性放寬、次輪 review 附駁回清單、
   cargo 綠≠lint 綠、findings 三分流）從 prompt 消失——補列為 RL-0063～RL-0073（決定 5）。

## 決定

1. **首版 73 條** RL-0001～RL-0073；檔頭 `<!-- next: RL-0074 -->`。表形＝§3.6；GT-08 解析錨＝以 `| RL-` 起的表列。
2. **上限**（實算 ×1.25 進位、寫進 RULES.md 檔頭「上限」行、GT-12 預算腿讀取）：

   | 面 | 實算 | 上限 |
   |---|---|---|
   | 總 | 73 | 92 |
   | implementer | 38 | 48 |
   | review | 14 | 18 |
   | fix | 15 | 19 |
   | 主線 | 41 | 52 |
   | 人 | 9 | 12 |

   超限只擋新增；改任一上限＝supersede 本 ADR。波 1～5 為 WARN、波 6 起 ERROR（判準＝NOTES.md 波標記）。
3. **去重併入表**（同一防法只留一列、source 取最早號）：rev5:L-058→RL-0001；rev5:L-052→RL-0014；rev5:L-086→RL-0031；
   rev5:L-085→RL-0032。「家在 script」的 rev5:L-006／rev5:L-054 轉為 RL-0002／RL-0033、carrier=prompt。
4. **六件套與看門狗紀律入 RULES**（RL-0004／0012／0025／0058～0062／0016／0017／0061）＝user 拍板 2026-09-03；
   CLAUDE.md §2 只留步驟骨架＋指針（波 1 Task 13）。
5. **agent 面不可違反項補列** RL-0063～RL-0073（source：ADR-00002／ADR-00003／本 ADR／rev5:L-063／065／066／069／064／rev5:ADR 0075）。
6. **RULES-VERSION**＝表列正規化（`id|規則|scope 排序|carrier|source`、依 id 排序）之 sha256 前 12 hex；空白與列序無關、任一欄改字即變。
   首版值＝`c7a137209e0e`。所有 Workflow script 一律必帶、PreToolUse hook 對賬（user 拍板；波 1 Task 12）。
7. **名詞段**（刀／單元／收刀／輕量軌／拍板級／波／五面／提及／人審）住 RULES.md `## 名詞`；不另立根目錄 CONTEXT.md（單一家、啟動書 §3.1）。
8. `rules emit --format js` 產 `const RULES`／`RULES_REVIEW`／`RULES_FIX` 三個樣板字串常數（識別字沿用、既有消費者 `_sk_cycle.js` 不改）；
   `_sk_rules.js` 自波 1 Task 12 起為 generate 產物、入 GENERATED_FILES 名冊。

## 後果

- GT-08 RULES 側首值：73 列 source 全存在、scope 值域內、≤2 行；LESSONS 側首版空＝Day-1 豁免 `GT-08.lessons-absent`（波 1 Task 6／10）。
- 現行手寫 `_sk_rules.js` 11 條退場（其內容已由 RL-0042／0063／0064／0045／0022／0012／0011／0023／0046／0065／0066 承載）。
- 一條新教訓要成為規則＝在 RULES.md 加一列（輕量軌）；上限撞頂＝先併列或退一列，不改數字。
- **翻案觸發器**：連續兩刀 implementer emit 塊超過 prompt 預算、或任一 scope 上限被撞三次＝重審上限（supersede 本 ADR）。
