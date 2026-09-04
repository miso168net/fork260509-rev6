---
id: "ADR-00011"
title: 數量預算改為只警告不擋——BACKLOG 開放取消上限（觀測值）、閘數與 RULES per-scope 保留上限但一律 WARN
date: 2026-09-04
status: accepted
supersedes: ["ADR-00004"]
superseded_by: []
provenance: "user 拍板 2026-09-04（三題一題一問：①BACKLOG 上限移除改只報表 ②閘數與 RULES 兩腿改永遠只警告 ③硬擋機制不動）；起因＝001 刀收刀後檢視 STATE 預算對賬表；ADR-00004 決定 2 末句與啟動書 D8 為被翻案面"
tags: [governance, budget, gates]
---

## 背景

- ADR-00004 決定 2 末句把三個數量預算腿綁在同一個嚴厲度開關：超限只擋新增、波 1～5 為 WARN、波 6 起 ERROR。實作＝`tools/docsync/gates.py` 的 `BUDGET_ERROR_WAVE`，三腿共用。
- 001 刀收刀後開放 17／25。檢視預算對賬表時判定：三個量的性質不同，不該共用一個開關。
- 閘數與 RULES per-scope 數的是「我們主動加了幾條治理規則」，增長完全由自己控制，撞頂時「一進一出」是做得到的紀律。
- BACKLOG 開放數是「發現多少問題」的觀測值。壓低它只有兩途：真的做掉，或者不記。後者正是治理面最不該給誘因的方向，而上限恰好在給這個誘因。
- 實查另發現：`BUDGET_GATES` 身兼兩職——除預算上限腿外，另有一處無條件 ERROR 的結構斷言 `len(roster_ids) != BUDGET_GATES`（等於，非小於等於）。只降級預算腿而不拆兩職，「閘數只警告」形同虛設。

## 決策驅動因子

- 觀測值不該有配額；配額只對「自己主動加的東西」有意義。
- 硬擋的主要對象是 Claude（CLAUDE.md §4「被擋的是 Claude、同回合修復」）。預算超限不屬「同回合可修復」類：出路是消化一條或翻案，擋下只會逼人繞道或不記。
- rev5 的棘輪病症（29 條 lint 塞進一萬四千行單檔）真實存在，閘數與 RULES 的數字仍該留著當儀表。
- 名冊同源與數量預算是兩種漂移，混在同一個判斷式裡會讓降級無效。

## 考慮過的替代案

1. **只降級 BACKLOG 一腿、閘數與 RULES 維持波 6 起 ERROR**：三腿行為不一致、概念要記兩套；user 拍板要一致。棄。
2. **連數字一起移除（含閘數與 RULES 上限）**：ADR-00004 的上限表整個失效，失去 rev5 棘輪的唯一儀表；改動面最大。棄。
3. **保留 ERROR 分類、改讓 pre-commit 不擋狀態型閘**：射程比本 ADR 大，會讓「lint 綠」不再是 commit 的前提，生成檔漂移與裸編號可進 git 歷史；user 另題裁定硬擋機制不動。棄。

## 決定

1. **BACKLOG 開放不設上限**：移除 `BUDGET_BACKLOG_OPEN`、GT-12 的 BACKLOG 腿、STATE 數量預算對賬表的 BACKLOG 列。帳面統計段仍報現值與滯後數，形同 CLAUDE.md 行數的「只報表、不擋」。
2. **閘數 12 與 RULES 總／per-scope 上限保留數值**（數值續 ADR-00004 決定 2 之表：總 92、implementer 48、review 18、fix 19、主線 52、人 12），但**超限一律 WARN**：不隨波轉 ERROR、不影響 `docsync lint` 退出碼、不擋 commit。
3. **GT-12 的名冊結構腿與數量預算腿語意分離**：結構腿只驗 docstring GATE 區塊集合 == ROSTER；數量交預算腿。pre-commit 檔頭範圍字串的期望值改自 ROSTER 實算、不再取自預算常數。
4. `BUDGET_ERROR_WAVE` 更名 `KNIFE_START_WAVE`：它已不服務數量預算，只服務波標記落後腿（波 6 起＝刀期）。
5. **ADR-00004 之決定 1、3～8 與決定 2 之上限表數值原文續行**；本 ADR 只取代其決定 2 末句（超限只擋新增、波別嚴厲度）與後果段末項之翻案觸發器。rev6 無部分翻案機制（GT-04 要求被翻案者 status 轉 `superseded`、`superseded_by` 由 generate 回填），故 ADR-00004 整顆轉 superseded；其續行決定的現行依據＝本決定，讀 ADR-00004 時須併讀本 ADR。
6. **硬擋機制不動**：pre-commit 對任一非零退出碼仍 `exit 1`；機密掃描仍為事件型、繞過不可逆。本 ADR 只改「什麼算 ERROR」，不改「ERROR 要不要擋」。

## 後果

- 撞閘數或任一 RULES scope 上限時 lint 印 WARN、commit 照過；「一進一出」自此為紀律而非機器強制。
- BACKLOG 可無限增長且無自動提醒；積壓觀測改看 STATE 帳面統計與三指標之「BACKLOG 淨流量（rolling 3 刀）」。
- RULES-VERSION 因 RL-0052 改寫而變，所有未發射的 Workflow script 須重組（PreToolUse hook 對賬）。
- GT-12 仍可產 ERROR（名冊分叉、GATES.md／pre-commit／RUNBOOK 三處不同源、波標記缺席或落後），docstring 之 `rc=1` 不變。

## 翻案觸發器

- 閘數或任一 RULES scope 上限被撞後、連續三刀未回到上限內＝棘輪重現，重審是否恢復 ERROR（supersede 本 ADR）。
- BACKLOG 開放連續三刀淨增且零消化＝觀測值失去意義，重審是否改用別的機制（非上限形）。
