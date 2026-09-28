# context 壓縮規則範本（`.claude/hooks/compact-hook.py` 之 PreCompact 注入源；BL-00126 自本機工作區入版控）

本檔＝壓縮指示的規則真源：hook 以 `## A.`／`## B.` 標題與其下第一對 ``` 圍欄定位、抽出圍欄內文，每次壓縮（auto／manual）皆依序注入 A＋B（B 由摘要者依情境套用）。workflow agent 自身之壓縮 hook 輸入面無從分辨、同樣會注入，由注入文首的主線限定句要摘要者自判略過（判準＝hook 檔頭 docstring）。
改規則只改圍欄內文；標題形與圍欄不可改——改了＝hook 抽不到、退為一句保底指示。機制全貌（三模式、主線限定、視窗解析）＝hook 檔頭 docstring；視窗值＝`.claude/settings.json` 之 `autoCompactWindow`。

## 工作區兩檔的約定（hook 讀、不入版控）

- **進度表**＝檔名合 `*progress*.md` 的人讀流水帳，一刀或一批一份、住 gitignored 工作區；節名沿用 `## ①`～`## ⑧`，hook 摘錄 `## ③`（run 帳：runId／task id／Monitor／支數／狀態）、`## ⑦`（主線裁定）、`## ⑧`（下一步）三節。
  ★每個動作——發射（runId／task id／冒煙 token）、完成通知、升級項預設處置、裁定、單元收尾六步序每一步——與該動作**同一個 call** 追加一行：自動壓縮可能落在任何一步，這是壓完能接續的前提。
- **壓縮備忘檔**（選用）＝檔名合 `*compact-prompt*.md`；其 `## 用法備忘` 節供壓後回灌指路，`## C.` 起首之節＝手動 `/compact` 前主線寫的本 session 快照（座標、驗證面、待辦、拍板、風險、坑、指針），只在**手動觸發且該檔 30 分鐘內改過**時附上。
- hook 認檔＝本 session transcript 之主線工具呼叫輸入中出現過、且現存者，各取 mtime 最新；未碰過＝不附、並在注入文中明講。新 session 起手先碰（建或讀）進度表。
  認不到的寫法：未加引號而含空白之路徑、緊鄰中文字的路徑、非 repo 根 cwd 下的相對路徑、`~` 與 `$VAR` 形——以 Read／Edit／Write 或 repo 根相對路徑觸碰即可。

## A. 標準版

```
壓縮以「換手後不必重讀對話就能繼續幹活」為準：保留下列各項的**具體值**，其餘一律丟。

【必留】
1. 座標：當前分支｜default 分支 HEAD｜兩 pin（base-web／rust-api）與 worktree HEAD 是否相等｜有無 origin／是否 push｜工作樹是否乾淨（含子庫髒檔清單）｜NOTES 波標記 N｜RULES-VERSION。
   SHA 一律照抄七位、不概括成「最新」。
2. 進行中：停在哪一步（run 待發射／在飛／分流中／六步序第幾步）；在飛 Workflow 的 runId／Monitor task id／背景長尾腿 task id／冒煙 token／script 路徑；已寫未 commit 的檔清單（外層與兩子庫分開列）。
3. ★部分完成的驗證面：「已跑綠哪幾個測試／lint 哪幾閘／親核了哪幾項／未跑哪幾個／未跑的理由」全留——最容易被壓成「完成」或「沒做」。
4. 拍板與裁定：user 親決事項的**結論＋理由一句**（不留討論）；主線工程判斷的**判準**那一句（回報備查者）。
5. 風險留帳：內容＋觸發條件。
6. 踩過的坑：只留「徵狀→成因→防法」三句；已落 LESSONS 者只留 LL 號＋指針。
7. 尚未寫進 repo 的判斷：凡已進 commit／ADR／tasks／memory 的，只留一句指針＋去處。

【必丟】
- 工具輸出原文（unittest／lint／cargo／psql／betterleaks／git log／bootstrap／workflow 回傳 JSON）——只留結論數字與 rc。
- 已 commit 改動的逐檔細節——git 是正史，只留 SHA＋一句話；agent 的 lens／mirror／implementer report 原文——只留「主線親核過哪幾項、結論」。
- rev5 藍本檔內容摘錄——只留「承哪個檔、住哪個路徑、rev6 差異點」一句；需要時回去讀（唯讀）。
- 被否決的探索路徑（除非否決理由本身就是拍板）。
- spec／plan／tasks／research／contracts 內文——tracked 檔、壓縮後重讀；只留「對映哪些 FR／SC／US」指針。
- 已收單批次的過程細節——只留「落地了什麼」一行與 commit SHA。

【格式】七段條列：座標｜進行中｜部分完成｜待辦｜拍板與判準｜風險｜指針。每條一行，數字與 SHA 照抄。
```

## B. 加壓版（run 中段或六步序中段適用；hook 恆接在 A 之後注入）

```
另：只有「當前這一支」需要細節，已收單的一律壓成一行（批次或單元＋外層 SHA＋子庫 SHA＋一句成果）。
當前這一支請完整保留：在飛 runId／Monitor task id／背景長尾腿 task id／冒煙 token／script 路徑、分流底表住址與已裁定之 finding 處置（修／BL／won't-fix／駁回＋一句理由）、
主線抽驗做到哪（變異腳本、snapshot 檔名）、該單元的允許檔案清單與六步序已做到第幾步、與條文不一致而改採的做法及理由（這些只活在對話裡）。
```
