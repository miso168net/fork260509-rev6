---
id: "ADR-00052"
title: 治理閘取值口徑——文字類腿續讀工作樹＋「工作樹＝暫存區」一致性腿；HEAD 版本缺席＝新檔通過、其他 git 失敗＝ERROR
date: 2026-09-29
status: accepted
supersedes: []
superseded_by: []
provenance: "BL-00102（maint-backlog-35 final holistic review L1-6／L2-5 轉入）；user 2026-09-29 裁定（006 前 BACKLOG 體檢題 3 ①：加一致性腿）；HEAD 缺席口徑＝主線工程判斷（同體檢 §0⑦ 第 3 項：ADR-00019 決定 4 射程＝碼面閘環境缺席、不及於治理閘的比對基準）；前代出處：rev5:tools/docs-sync.py 之連結腿以「tracked ∪ 未追蹤」為存在集（本洞的前代形）、同檔 rev5:Lint16 以暫存區 diff 定射程（讀暫存區的前代先例）；rev5:ADR 0024（閘自證非空轉）"
tags: [governance, gates, docsync]
---

## 背景

pre-commit 直接跑 `docsync check／lint`。十二閘的文字類腿一律經 `Ctx.text` 讀工作樹，只有 gitlink 與檔案權限兩腿讀暫存區；commit 放進去的卻是暫存區。兩者不一致時閘全綠、commit 進去的是另一個版本。已發生過的同類：002 刀 U2 的 23ca37b（commit 的 LESSONS 索引列了 LL-00009、commit 樹沒有該檔，後 amend）；drvfs 上以小寫路徑 `git add` 新 LESSONS 檔靜默沒 stage、generate 卻已列進索引；005 刀 2bfabcf 的 generate 在 `git add` 之後才回填 ADR-00049 的 `superseded_by`（LL-00044）。

另一個口徑：`Ctx.head_text` 對任何 git 失敗都回 None。GT-02 append-only 腿、GT-04、GT-05 next-id 單調腿與 book.py 兩處存量豁免讀取都把它當「HEAD 無此檔」靜默放行，輸出上與通過不可辨；GT-12 門鈴腿則 fail-loud——同一件事三種判法（BL-00102②）。

## 決策驅動因子

- 閘判的必須是 commit 真正放進去的內容；上述三件都是「工作樹對、commit 錯、閘全綠」。
- 不動 `.githooks/pre-commit`（hook 指紋、LL-00012 的 GIT_INDEX_FILE 外洩）、不在 hook 內 stash（中斷要手動復原、drvfs 上更慢）。
- 手動跑 lint（單元收尾的自驗）時工作樹≠暫存區是常態，不能誤報。
- HEAD 讀取口徑一次定齊、不單腿特殊化；ADR-00019 的具名跳過只管容器依賴型碼面閘的環境缺席，其決定 4 明令不類推。
- 判讀不得依 git 錯誤訊息的字面（隨語系變）。

## 考慮過的替代案

1. **維持讀工作樹、以 by-design ADR 照實寫射程**——三類漏網照舊發生；否決。
2. **pre-commit 改以 `stash --keep-index --include-untracked` 的暫存快照跑 check／lint**——十二閘碼不動、口徑一次到齊，但要改 hook、中斷須手動復原、hook 內 GIT_INDEX_FILE 外洩風險（LL-00012）、drvfs 更慢；否決。
3. **HEAD 缺席一律具名 SKIP（登 ENV_SKIPS）**——新檔是正常路徑，每顆新檔 commit 都印 SKIP 等於噪音，且等於類推 ADR-00019；否決。

## 決定

1. **文字類腿續讀工作樹，另設「工作樹＝暫存區」一致性腿（掛 GT-12、不新增閘）**：只在暫存區≠HEAD（有 commit 正在準備）時執行——外層 repo 的 tracked 檔（gitlink 除外）有未暫存改動、或有未追蹤且未被 ignore 的檔，逐檔 ERROR 指名並附補救（`git add`，或 stash／移出後再 commit）；暫存區＝HEAD 時整腿不跑，手動 lint 不誤報。未追蹤檔取外層全集：閘以工作樹列目錄或查存在的面遍及 docs、specs、tools，逐面枚舉易漏。
2. **HEAD 版本讀取口徑**：HEAD 未誕生（首顆 commit 前）或該路徑不在 HEAD 樹＝新檔，比對面視為空、正常通過，不印 SKIP、不登 ENV_SKIPS；其他 git 失敗＝該閘 ERROR 指名（fail-loud）。「路徑在不在 HEAD」以一次性的 HEAD 樹清單判，不解析 git 錯誤訊息。
3. **射程**＝GT-02 append-only 腿、GT-04 的 HEAD 側讀取、GT-05 next-id 單調腿、book.py 兩處「該行逐字在 HEAD」存量豁免讀取。GT-12 門鈴腿（子庫 HEAD 樹、既有 fail-loud）與 GT-05 存量豁免的「HEAD 無檔＝全報」維持原判（與本決定同向）。
4. 碼面閘讀子庫工作樹（BL-00074）不在本決定射程——那是 pin 樹與子庫工作樹之分，另立 ADR。

## 後果

- 刻意只 commit 部分改動時，其他 tracked 改動與未追蹤檔要先 stash 或移出；若實測常誤擋正常流程，一致性腿降為 WARN 並回報 user（見翻案觸發器）。
- 一致性腿與 HEAD 樹清單各增數次 git 呼叫，pre-commit 牆鐘增量實量後記入收單事件。
- 「先 add 改寫版、再還原工作樹」與「LESSONS 漏檔／ADR 回填漏進」兩型都在同一顆 commit 當場擋下。
- `head_text` 的呼叫端改為把 git 失敗轉成該閘 ERROR finding；HEAD 未誕生的測試用 repo 照常通過。

## 翻案觸發器

- 一致性腿實測常誤擋正常流程（例：部分 commit 成為常態）→ 以新 ADR 將決定 1 的級別降為 WARN。
- pre-commit 改以暫存快照跑 check／lint（替代案 2）→ 決定 1 由新 ADR supersede。
- 出現 HEAD 以外的比對基準（例：merge 進行中的 MERGE_HEAD 需要特判）→ 重審決定 2。
