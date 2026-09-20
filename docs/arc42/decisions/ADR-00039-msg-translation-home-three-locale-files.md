---
id: "ADR-00039"
title: msg key 譯文之家＝三檔 locale backend 子樹各為該語權威（續行 ADR-00029）——不另立譯文表、鍵數以跨端閘為準
date: 2026-09-20
status: accepted
supersedes: ["ADR-00029"]
superseded_by: []
provenance: "004-ip-trust-anchor brainstorm Q3（BL-00042 ②；user 2026-09-15 拍板「三檔 locale backend 子樹各為該語之家」）；憲法 §III.2 BASE-WEB-I18N-WIRING (ii) 權威句已由 ADR-00034 Amendment（1.4.0）改寫、本檔＝其 ADR 面翻案紀錄；被翻案面＝ADR-00029 後果段與 provenance 所稱「`contracts/msg-keys.md` 為譯文（唯一）權威」；形承 ADR-00032（原意續行、只改一句）；ADR-00012 原則（跨刀活體不住 spec 目錄）；主線擬稿即 accepted（tasks T063）"
tags: [i18n, contract, code-gate, base-web, rust-api, decision-reversal]
---

## 背景

ADR-00029 立下 msg key 跨端閘的形制（後端名冊 ⇔ 三檔 locale `backend` 子樹逐檔雙向全等），同時在後果段把**譯文**的權威定於 003 刀的 `specs/003-auth-session/contracts/msg-keys.md`。該檔是 003 刀的定點快照：004 刀新增六鍵後，它既不會再被更新（spec 目錄不承載跨刀活體＝ADR-00012），也已與三檔 locale 的實況脫節——「權威」指向一份注定過期的文件。

## 決策驅動因子

- 每個事實只有一個人寫的家（RL-0049）：譯文已經住在三檔 locale 裡、且受跨端閘對賬鍵集；再立一張譯文表＝人寫鏡像。
- 跨刀活體不住 spec 目錄（ADR-00012）。
- 閘的形制（ADR-00029 決定 1～5）經兩刀驗證有效，不該因權威句翻案而重立。

## 考慮過的替代案

1. **各刀各立 `contracts/msg-keys.md`**（前代形）：活體權威散落各刀 spec 目錄、同一鍵兩家以上——棄。
2. **另立一份跨刀譯文表**（`docs/` 下）：與三檔 locale 構成人寫鏡像、無機器對賬譯文內容——棄。
   對所選方案跑同一反例（RL-0013）：三檔各為該語之家，是否也有「兩家」？沒有——每一語恰一檔、鍵集由跨端閘逐檔對賬；三檔之間是「三種語言」而非同一事實的三份抄本。

## 決定

1. **ADR-00029 之決定 1～5 原意續行**，現行依據＝本決定：形制＝逐檔雙向全等、無白名單；Biz 構造點守衛兩形；承載＝`tools/msg-key-gate.py` 與其接線名冊；與 ADR-00017 的射程關係；`zh-tw.ts` 為治理錨點孤立檔、是右源之一。
2. **譯文之家＝三檔 locale 各自的 `backend` 子樹**：`en-us.ts`／`zh-cn.ts`／`zh-tw.ts` 各為該語譯文的唯一權威；鍵集由跨端閘對賬；**不另立譯文表**。`specs/003-auth-session/contracts/msg-keys.md` 降為 003 刀的史料出處（首批 13 鍵之來歷），不再是現行權威。
3. **鍵數不手抄**：碼註、標記註解與文件凡需提及鍵數者，一律指向 `MSG_KEYS`／跨端閘輸出，不寫實數（手抄數字每加一鍵就過期一次）。
4. 現在式面引用 ADR-00029 之處（RUNBOOK §12 碼面閘表「根據 ADR」欄、活書、碼註）改指本 ADR；accepted ADR body 內的引用不動，讀時併讀本 ADR。

## 後果

- 新增 msg key 的同批改動面不變（`msg_key` 常數＋`MSG_KEYS`＋三檔子樹＋`app.d.ts` 型節）；譯文審閱面＝三檔 diff。
- base-web 五處標記註解與 rust-api 四處 doc 之「權威＝003 契約」句改為史料出處指針。
- 閘只對鍵集、不對譯文內容：三語語意一致性仍靠人審（與 ADR-00029 同）。

## 翻案觸發器

- 沿 ADR-00029 兩款（前端字典改由後端名冊單向生成；`backend` 子樹不再是封閉集）。
- 若譯文改由外部翻譯平台管理（locale 檔成為產物）⇒ 權威移轉、以新 ADR 定。
