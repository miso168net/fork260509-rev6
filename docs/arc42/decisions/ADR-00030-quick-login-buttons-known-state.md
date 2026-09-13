---
id: "ADR-00030"
title: 登入頁三顆快速登入鈕與表單預填密碼＝已知態「保留＋記帳」（零 inline、UI 對照零差異；帳＝滯後卷 BL-00049、觸發綁 RUNBOOK §16 prod 硬化拍板）
date: 2026-09-13
status: accepted
supersedes: []
superseded_by: []
provenance: "docs/brainstorms/003-auth-session.md §0 Q4（user 拍板 2026-09-07「保留＋記帳」）與 Q7（user 拍板 2026-09-08「立在 BACKLOG-DEFERRED.md＝BL-00049」）；spec FR 登入頁條與 US1 驗收情境 6（三顆鈕各一次真登入、三種角色化選單）；contracts/code-gates.md §7 ADR ④；docs/ops/BACKLOG-DEFERRED.md BL-00049；rev5:B-053 同型已知態；主線擬稿即 accepted（tasks T073）"
tags: [base-web, security, known-state, dev-only, fork-delta]
---

## 背景

- upstream `soybean-admin` `example` 基線的登入頁（`base-web/src/views/_builtin/login/modules/pwd-login.vue`）自帶三顆快速登入鈕（Super／Admin／User）與表單預填密碼，三者各自帶 seed 帳號與同一組 dev 密碼。
- 003 刀是 rev6 第一把能真登入、也是第一把能全面走查的刀：US1 驗收情境要求三 seed 帳號分別登入（含三顆鈕各一次）、側邊欄呈現三種角色化選單；UI 以 CDP 與 rev5（22080）對照、要求零差異（憲法 §I.5、CLAUDE.md §7）。
- 代價是 dev seed 帳密露在登入頁——rev5 以 rev5:B-053 記為同型已知態；rev6 收官前無 prod 硬化刀（RUNBOOK §16 逐字「prod 不入 roadmap、若要做 prod 先立 ADR」）。
- 002 承載體檢抓過「延後但無家」形（只在 ADR 記已知態、查待辦的人看不到）；BACKLOG 檔頭又要求開放帳「觸發須可到期」——本項觸發本質不可到期，兩卷之間要選一卷。

## 決策驅動因子

- 對照面越乾淨越好：本刀首輪 CDP 對照若因拆鈕出現差異，就得標具名例外且會一直跟著後刀。
- 一鍵切三帳號正是 US1 的手動驗收動作；拆掉＝每次驗收手打三組帳密。
- 只清預填密碼而留鈕＝假改善（鈕裡仍寫死同一組密碼、帳照樣要記）。
- 帳本紀律：開放卷「觸發須可到期」不可形同虛設；滯後卷正是為「觸發本質不可到期」而設，仍計入 GT-05 配號家族、查待辦兩卷併看。
- 憲法 §III：base-web 既有檔改動只走 ★ 軌道授權用途；三顆鈕不占任何軌道用途、零 inline＝零 fork-delta 負擔。

## 考慮過的替代案

1. **拆掉三顆鈕與預填密碼**：CDP 對照與 rev5 出現差異、首輪即須標具名例外；手動驗收切帳號要手打；且拆除須開 base-web inline 用途（憲法 §III.2 軌道表無此用途）——棄。
2. **只清預填密碼、鈕保留**：鈕裡仍寫死同一組密碼＝假改善，帳照樣要記、對照仍有差異——棄。
3. **立在開放卷 BACKLOG.md（同 rev5 形）**：rev5 真有一把 prod 硬化刀可綁；rev6 無，觸發不可到期＝讓檔頭「觸發須可到期」形同虛設——棄（Q7）。
4. **只在本 ADR 記已知態、不立帳**：查待辦的人看不到＝002 承載體檢所指「延後但無家」形——棄（Q7）。

## 決定

1. **保留**：三顆快速登入鈕與表單預填密碼原樣保留、本刀對 `pwd-login.vue` 之該區零 inline（該檔本刀只開 BASE-WEB-LOGIN-CAPTCHA-WIRING(i) 軟區接線）；UI 與 rev5 對照零差異；US1 驗收含三顆鈕各一次真登入。
2. **記帳**：已知態由滯後卷 `docs/ops/BACKLOG-DEFERRED.md` **BL-00049** 承載（product；「轉 prod 前必須拆除」）；觸發＝RUNBOOK §16 之 prod 硬化拍板成立時（該節現寫「prod 不入 roadmap、若要做 prod 先立 ADR」）；不綁不存在的刀。
3. **卷別**：立在滯後卷而非開放卷（觸發本質不可到期）；滯後卷首次啟用、STATE 分開計數；配號仍在 GT-05 家族。
4. **本 ADR 只記拍板**：as-built（鈕的存在、走查截圖）歸收刀事件與活書，不回灌本檔。

## 後果

- dev 環境登入頁持續露出 seed 帳密＝已知且有帳可查；任何 prod 化提案必先讀到 BL-00049 與本 ADR。
- 後刀對 `pwd-login.vue` 的任何 inline 仍受憲法 §III.2 軌道表約束；拆鈕須先開用途（隨 prod 硬化 ADR 同批）。
- 代價：滯後卷多一條不可到期項；接受＝這正是滯後卷的用途。

## 翻案觸發器

- RUNBOOK §16 prod 硬化拍板成立（新 ADR）：BL-00049 觸發到期、拆除三顆鈕與預填密碼、憲法 §III.2 同批開該用途——屬本 ADR 決定 2 的兌現、非翻案。
- 若 rev6 改採 upstream 基線前進（D14）且 upstream 自行移除該鈕：BL-00049 以 `backlog_done` 收、本 ADR 決定 1 隨基線失效、以新 ADR 記錄。
