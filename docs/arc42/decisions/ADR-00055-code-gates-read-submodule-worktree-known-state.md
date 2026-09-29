---
id: "ADR-00055"
title: 碼面閘讀子庫工作樹、不讀本顆 commit 所 pin 的子庫內容——照實登記兩型（閘面內延後偵測／閘面外無兜底）為已知態、不擴觸發（won't-fix）
date: 2026-09-29
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00074（maint-backlog-pre-004 final holistic review 轉入）；user 2026-09-29 裁定（006 前 BACKLOG 體檢題 6 ①：立 won't-fix ADR、照實記兩型）；前代出處：rev5:006 T025（seed-view-gate 之觸發含工具本體 staged＝同形新成員）"
tags: [governance, code-gate, submodule, wont-fix, known-state]
---

## 背景

碼面閘（RUNBOOK §12 碼面閘表）比對的是子庫**工作樹**，不是這顆外層 commit 所 pin 的子庫內容。只 stage 外層檔（閘工具本體、憲法、schema 快照）時，pre-commit 照樣觸發會讀子庫工作樹的段落；子庫工作樹若有未 commit 改動，閘判的就不是本次 commit 的內容。pre-commit 的 submodule-sync 段只在 `rust-api`／`base-web` gitlink staged 時，要求兩側「雙側閘閘面路徑」無未 commit 改動，其閘面只含 rust-api 的 `server/src/error.rs`、`server/tests/fixtures/wire-schema.json` 與 base-web 的 `src`（含 `src/locales/langs`、`src/typings/**`）。依讀面落在閘面內外，分兩型（逐列落點見 RUNBOOK §12）：

- **(a) 閘面內＝延後偵測**：msg-key-gate 的名冊兩腿（左源 `error.rs`、base-web locales 與前端消費點）、view-render-guard、fork-delta 與 route-artifact-gate 的 `src` 部分。外層單獨 commit 時可能判到工作樹；下一次任一側 pin bump 時 submodule-sync 要求閘面乾淨，屆時補抓。
- **(b) 閘面外＝無兜底**：entity-drift（`rust-api/entity/src`）、rust-fmt（整個 rust-api）、msg-key-gate 的 Biz 構造點守衛（`server/src/**/*.rs`）、fork-delta 的 `build/` 與根層 `.env*`、route-artifact-gate 讀的外掛設定 `build/plugins/router.ts`、wire-schema 的兩條跨子庫錨腿（既有「★已知邊界」）。連 pin bump 時也照讀工作樹。

實務上子庫一律先在 worktree commit、外層再 bump pin，外層 commit 時子庫工作樹通常是乾淨的；真正漏網要「子庫有未 commit 改動、同時只 stage 外層檔」（(b) 型另含「pin bump 時閘面外仍有未 commit 改動」）。rev5 前例中，`rev5:006` 另新建同形的雙側閘 seed-view-gate（其 T025：觸發含工具本體 staged）。

## 決策驅動因子

- 補機器守只補得到 (a)：submodule-sync 的觸發加上工具本體與憲法路徑，(b) 仍開著；代價是 base-web `src` 有半成品時，這類外層 commit 會被擋——過往動這些外層路徑的 commit 約七成沒帶 pin bump（2026-09-29 重算：28 顆中 20 顆），單獨提交是常態。
- 已知邊界要照實寫，不宣稱一律有兜底（原稿「偵測延後、pin bump 兜底」只對 (a) 成立，寫進不可變 body 即成假述）。
- 同形新成員會隨刀進場，登記規則要先定。

## 考慮過的替代案

1. **擴 submodule-sync 觸發（工具本體、憲法路徑）**——只補 (a)、(b) 照舊，且使外層單獨 commit 常被子庫半成品擋下；否決。
2. **帶進 006 brainstorm 與 seed-view-gate 一起定**——006 前不動；user 2026-09-29 裁定現在以本 ADR 結案。
3. **閘改讀 pin 樹（`git show <pin>:<path>`）**——等於各碼面閘重寫取值層、部分閘在容器內重算需完整樹；成本遠大於洞的實際風險；否決。

## 決定

1. 碼面閘讀子庫工作樹之兩型照實登記為**已知態（won't-fix）**：不擴 submodule-sync 觸發、不改閘的取值層。
2. RUNBOOK §12 碼面閘表逐列標明該閘讀面屬 (a)／(b)（或不讀子庫），並加一句通則指向本 ADR；msg-key-gate 列既有「本閘讀不到 pin 樹、非其守備範圍」與 wire-schema 列既有「★已知邊界」同口徑、保留。
3. 新雙側或讀子庫工作樹的碼面閘進場時（首例＝006 若照 rev5 新建 seed-view-gate），同刀在 RUNBOOK §12 該列標 (a)／(b)；若其讀面落在閘面外、且屬必須兜底者，於該刀另議擴閘面，不在本 ADR 預裁。
4. 防法＝紀律面：外層 commit 前子庫工作樹應乾淨（子庫先 commit、外層再 bump pin）；本 ADR 不新增機器守。

## 後果

- (a) 型漏網最遲在下一次該側 pin bump 被 submodule-sync 擋下；(b) 型只靠紀律，漏網時由下一次 stack 在跑的全量或審查輪發現。
- RUNBOOK §12 成為兩型的唯一落點；新碼面閘進場時多一個登記動作。
- BL-00074 收列。

## 翻案觸發器

- (b) 型實際漏網一次（以 commit 內容與閘判讀不一致為證）→ 重審決定 1，評估該閘改讀 pin 樹或擴閘面。
- 外層單獨 commit 不再常見（例：流程改為每顆外層 commit 必帶 pin bump）→ 替代案 1 的代價消失、可改補機器守。
