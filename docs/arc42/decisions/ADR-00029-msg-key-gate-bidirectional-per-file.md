---
id: "ADR-00029"
title: msg key 跨端閘形制＝後端名冊與三檔 locale backend 子樹逐檔雙向全等、無白名單、Biz 構造點守衛兩形（tools/msg-key-gate.py）
date: 2026-09-13
status: accepted
supersedes: []
superseded_by: []
provenance: "003-auth-session clarify Q2（2026-09-08、user 拍板「A 逐檔雙向全等＋立 ADR」）；spec FR-025／FR-027；research R9；contracts/code-gates.md §2（閘契約逐列）與 §7 ADR ⑤；contracts/msg-keys.md（13 鍵三語譯文表＝譯文唯一權威）；ADR-00017 決定 3「跨端閘延至首個接 i18n 的前端刀」＝本 ADR 兌現、不翻案；rev5:Lint24（後端字面 ⊆ 前端 zh-tw.ts 字典＋九鍵白名單＝三向）翻案為逐檔雙向；主線擬稿即 accepted（tasks T068）"
tags: [i18n, contract, code-gate, base-web, rust-api]
---

## 背景

- ADR-00017 於 002 刀只閉後端側：`rust-api/server/src/error.rs` 之 `MSG_KEYS` 單一名冊＋contract 雙向斷言；跨端閘（後端名冊對前端字典）延至首個接 i18n 的前端刀，決定 3 的字面寫的是單向「名冊 ⊆ 前端字典」。
- 003 刀（首個接 i18n 的前端刀）把 base-web 三檔 locale（`src/locales/langs/{en-us,zh-cn,zh-tw}.ts`）的 `backend: {` 子樹自零建起（BASE-WEB-I18N-WIRING (ii)＋`zh-tw.ts` 錨點檔），名冊自 002 的七鍵擴為十三鍵；三個 Biz 鍵（`biz.auth.{notSupported,captchaRequired,locked}`）由業務構造點以 `AppError::Biz(Cow::Borrowed(msg_key::NAME))` 發出。
- rev5 的同名閘（rev5:Lint24）是三向：後端字面 ⊆ 前端整本字典＋九鍵前端內部白名單存在＋白名單不腐化——複雜度全來自「對整本字典」與白名單。

## 決策驅動因子

- 右源若取整本前端字典，雙向必恆紅（字典含大量與後端 msg 無關的 UI 鍵）——這正是 ADR-00017 所述之「雙向必恆紅」，其射程是整本字典。
- 本刀的 `backend` 子樹是 rev6 自零建的封閉集：後端能發的鍵恰等於前端該譯的鍵，雙向全等成立且有意義——同時守「後端多發前端沒譯」（缺）與「某檔孤兒鍵／`zh-tw.ts` 漏插」（多）。
- 單向 ⊆ 少守一半：孤兒鍵與三檔彼此不一致（某語系漏插）皆無訊號；rev5 為補這一半長出白名單。
- Biz 鍵的字面若以變數／`format!`／函式回傳動態構造，名冊對賬即成恆綠洞；構造點必須機器守。
- 碼面閘依 ADR-00016 一律獨立 `tools/` 工具檔、零 docker、標準庫；docsync 行數預算不吃這一支。

## 考慮過的替代案

1. **單向 ⊆（沿 ADR-00017 決定 3 字面）**：少守孤兒鍵與跨語系不一致；rev5 經驗＝為補這一半必長白名單——棄。
2. **對整本字典雙向**：恆紅（ADR-00017 已論證）——棄。
3. **由後端名冊生成前端字典（單向生成而非對賬）**：譯文須人寫、生成物無家；且憲法 §III 只授權新增型圈界塊、不授權生成整檔——棄（此案若被採即翻 ADR-00017 決定 2／3、須新 ADR）。
4. **閘寫進 docsync**：docsync 行數預算與 ADR-00016 碼面閘獨立工具檔紀律——棄。

## 決定

1. **形制＝逐檔雙向全等**：左源＝`rust-api/server/src/error.rs` 兩段解析（`pub mod msg_key` 常數表建 名稱→字面 映射；`pub const MSG_KEYS: [&str; N]` 逐元素經映射解回字面、亦容直寫字面；元素數≠N 或解不出＝rc 2）；右源＝三檔各自 `backend: {` 區塊（錨＝獨佔一行、允許前置空白；brace 配對取塊；剝 `//`／`/* */` 註解與字串值後攤平鍵路徑）；斷言 1＝三檔各自 `set(backend) == set(MSG_KEYS)`，不等 rc 1、逐檔指名「缺：…」「多：…」。**無白名單**：子樹為封閉集、不設任何前端內部例外鍵。
2. **Biz 構造點守衛兩形**（斷言 2）：`rust-api/server/src/**/*.rs` 生產區間（`#[cfg(test)]` 所附項目以 brace 配對排除）內每處 `AppError::Biz(` 須緊接 `Cow::Borrowed(` 且引數為 ①字串字面 或 ②`msg_key::NAME` 常數（經左源映射解回）、解出之鍵 ∈ `MSG_KEYS`；動態構造＝rc 1 指名檔:行。
3. **承載**＝`tools/msg-key-gate.py`（碼面閘；子命令 `check`／`test`、`--rust`／`--locales` 只供 self-test 注入；rc 0／1／2／64；self-test＝契約七案＋判準補強案＋真 repo 綠案，案數以 `test` 輸出為準；四條右源判準與斷言 2 兩腿各有反例誘餌）；接線＝pre-commit `msg-key-gate` 條件段（觸發＝staged 含 `rust-api`／`base-web` pin bump 或工具本體）＋`for t in …` 自測名冊＋`test_hook_wiring` SEGMENTS＋`tools/bootstrap.sh` `run_tool_test`＋README 樹＋RUNBOOK §12 碼面閘表工具檔列（GT-12 腿對賬）。
4. **與 ADR-00017 的射程關係**：本 ADR 是其決定 3 的兌現、不翻案——ADR-00017「雙向必恆紅」指整本字典，本閘的右源是 `backend` 子樹、不指整本字典；其決定 1／2（後端名冊＋contract 雙向）不變、左源即取之。
5. **`zh-tw.ts`**＝治理錨點孤立檔（裸 object、不接 runtime、不註冊 `LangType`＝003 brainstorm Q3）：是右源之一與繁中譯文之家，鍵集紀律與另兩檔同。

## 後果

- 後端新增 msg key 未同批補三檔 backend 子樹、或某語系漏插／多插，pre-commit 即紅並指名檔與鍵；Biz 鍵改為動態構造即紅。
- 三檔譯文各自為家（`contracts/msg-keys.md` 為譯文權威、閘只對鍵集不對譯文）；前端對後端 msg 一律經 `translateBackendMsg`（BASE-WEB-I18N-WIRING (i)）轉譯、未命中走原文 fallback。
- 代價：每加一鍵改四處（`msg_key` 常數＋`MSG_KEYS`＋三檔子樹）；接受＝這正是閘要逼出的同批紀律。

## 翻案觸發器

- 若前端字典改由後端名冊生成（單向生成），以新 ADR 翻本 ADR 決定 1 與 ADR-00017 決定 2／3。
- 若 `backend` 子樹不再是封閉集（前端自行加入非後端鍵），逐檔雙向全等失效，須以新 ADR 定白名單或改回單向。
