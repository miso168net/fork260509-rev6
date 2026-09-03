# 波 4 RAD-AI 取捨 ADR 實作計畫（000-w4-rad-ai-tradeoffs）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans 逐 Task 執行（本 session 主線自做、不派 subagent；只在 merge 時點停）。Steps 用 `- [ ]` 勾選。

**Goal:** 把啟動書附錄 A 的 24 筆 RAD-AI 取捨（F01～F23 內部不一致＋F24 量表第四值）進權威面＝一份 ADR-00007（accepted），射程定為系統層形制、流程層以「類比張力：」宣告偏離；補活書四處（F03 指針雙向、F12 逐型必填性質指針、§9.1 對映表英文欄名改欄序、C4-E1 導言英文刻板型名中文化＝D15 字面在活書正文全真）；BACKLOG 記 BL-00002（GT-10 對 §9 兩腿的潛在互斥）；波標記 bump 5。

**Architecture:** 零工具改動——ADR 由既有 `gen_decisions_index` 收進 DECISIONS-INDEX、STATE 帳面 ADR 7；活書只動四處（`docs/process/P-E1-boundary.md` 一句、`docs/c4/C4-E1-ai-component-stereotypes.md` 兩句、`docs/arc42/09-architecture-decisions.md` §9.1 表）；ADR 本體＝本檔 §1 草稿逐字落地（grill 審的就是它）。三 Task 三 commit：T1 活書小補 → T2 ADR → T3 出口（merge 停點）。

**Tech Stack:** Markdown；`tools/docsync`（generate／lint／check／test，零改動）；git（`-F` 檔訊息）。

**Spec:** 啟動書 `docs/brainstorms/000-doc-architecture.md`（D3、D15、D16、§0.3 A2、§3.4 第 1／2 條、§3.5、§5 波 4 列、§7、附錄 A、附錄 B、附錄 F R1-F18）；波 3 計畫 `docs/brainstorms/000-w3-book-fill.md` §0.3 剩餘欄；本檔 §0.1 四題拍板。

---

## 0. 本 brainstorm 的拍板與判斷

### 0.1 user 拍板（2026-09-03；一題一問、首選項為建議、四題皆取 A；Q4 為 grill）

| 題 | 結論 | 理由（一句） |
|---|---|---|
| Q1 附錄 A 的射程 | **A：只管系統層（arc42 E 子節、docs/c4 E 三檔、compliance）；流程層是類比、偏離以子節首句「類比張力：」宣告即可、不算違反、不入表** | 對賬結果系統層形制零使用、五處實質偏離全在流程層且皆已宣告；啟動書 §3.4 第 2 條與 D16 本就預期流程層有硬套；波 3 grill Q3 拍的 P-E7 九欄不重開；as-built 不回灌 ADR |
| Q2 ADR 的形 | **A：一份 ADR-00007，19 列表（涵蓋 F01～F24）進「決定」節** | 仲裁規則與逐筆結果是同一決定的兩面；啟動書 §5 波 4 列即單數「取捨 ADR」；拆兩份＝結果表離開規則讀不懂；住活書＝失去凍結與翻案紀律 |
| Q3 status 路徑 | **A：直接 accepted（與 ADR-00001～00006 同形）** | 對賬已在 brainstorm 完成、表無未決列；grill 審的就是本檔 §1 全文；先 proposed 只多一次 status 改動 |
| Q4（grill）D15 字面與活書兩處正文英文的落差 | **A：活書向 D15 字面靠、零工具零新鍵**——§9.1 對映表 reference 欄改欄序（英文名冊住 `tools/docsync/book.py` E_SUBSECTIONS）、C4-E1 導言英文刻板型名改中文；ADR-00007 記「D15 在活書正文零例外」＋機器自證 | 啟動書優先於執行方便；對照鍵的家本就是 frontmatter 鍵與工具名冊、正文不該再有第二家；grep 可驗 |

### 0.2 工程判斷（回報備查；grill 可翻）

1. **表 19 列＝附錄 A 的併列形**（F13～F16、F19／F20、F22／F23 各一列），欄＝列｜不一致｜rev6 取捨｜採哪份｜理由；理由欄是附錄 A 沒有的新增欄（ADR 只寫結論與理由、不重述附錄 A 的討論）。
2. **D15 落在 ADR 正文**：RAD-AI 的子節名、欄名一律中文改寫列在表內（例：五欄＝閘號／位置／檢查型／門檻／失敗動作）；英文原名零出現；RAD-AI 對照 HEAD 只在 README 一句、ADR 不記 HEAD 字面。
3. **Task 序＝活書小補先、ADR 後**：ADR 證據段要寫「F03 指針雙向、F12 逐型必填性質有家」，必須在 ADR commit 時已為真（accepted 即凍結、不能事後補）。
4. **F03 補法**：`docs/process/P-E1-boundary.md`「四段邊界契約」表後加一句指向 `docs/c4/C4-E3-non-determinism-boundary.md` 邊界介面欄「三性質契約」（反引號路徑、不放 Markdown 連結）；arc42 §3.3 不動（§3.4 第 1 條：恰一句「目前無」＋一行指針）。子節首句仍是「類比張力：」（GT-10）。
5. **F12 認定＝承載換位**：逐型必填性質已住 C4-E1「刻板型定義」表的「必填性質」欄（五型齊、含特徵庫）；「標註準則」第 3 條加半句指過去；不改任何 `###`（`rad_ai_map` 不動、GT-10 第八腿不觸）。
6. **F02 對賬判「部分」不補**：P-E4 矩陣列＝關注、欄＝適用／承載／守門，是流程層單一元件（agent）下的轉置形，已以類比張力宣告；系統層矩陣形（列＝AI 元件、欄＝六關注）由 ADR 表 F02 列規範、AI 元件進場時照填。
7. **F08 對賬判「as-built 無承載」**：P-E2 逐模型明細為硬套（託管 LLM 無版本史與基線可填）；列仍入表、規範系統層。
8. **ADR 不帶 `rad_ai: [E5]`、不帶 `rev5_id`**：治理決策、非 AI 元件決策、非 rev5 承襲；tags＝`[governance, rad-ai]`；frontmatter 八欄形＝ADR-00006。
9. **F24 的家**＝`docs/compliance/annex-iv-checklist.md` 用法段（已在）＋波 5 §7 自評表沿用；不入 RULES 名詞段（量表值、非規則；RULES-VERSION `c7a137209e0e` 不動）、不入 §12 名詞表（該表收 RAD-AI 詞，此為 rev6 自訂值）。
10. **零工具改動**：無新生成器、無新閘、tests 88 不變、docsync 邏輯行 2,043 不變；ADR 進索引靠既有 `gen_decisions_index`（misc 收單事件無 `adrs` 欄，feature 欄印「輕量軌」＝預期）。
11. **Day-1 兩筆不動**（GT-03 需 feature_close、GT-08 需首條 LL）；本波預期零 LL；BACKLOG 新條目一筆＝BL-00002（T1 落帳、§0.2-18）。
12. **收單 misc 事件** notes 帶「ADR-00007 accepted、對賬零未決、活書四處（D15 正文零英文）、分支保留供 audit」；`backlog_add`＝`["BL-00002"]`。
13. **不新增 `TODO(波 k)`**；波標記 5 後 GT-10 以 k<5 判到期（活書家族現為零、不受影響）。
14. **final holistic review 在 T3**（RL-0073：不落報告不落事件；處置逐項列入收單 commit 訊息）。
15. **恢復點檔** `tmp/000-w4-progress.md`（gitignored）每 Task 末更新一行「T<N> 完成＠<SHA>」；壓縮或換手後先讀它再動手。
16. **決定 1 的仲裁規則寫成 D3 的枚舉形**（grill 事實查核）：「採模板或 adoption-guide 者以採哪份欄逐筆註明、未註明者一律 reference」——F06 id／F09／F18／F22 採模板並非因 reference 缺項，通則式寫法（「模板只在 reference 缺該項時補位」）會與表自相矛盾。
17. **D15 機器自證**（grill Q4）：活書正文（去 frontmatter）大寫英文雙詞 `[A-Z][a-z]{2,} [A-Z][a-z]{2,}` 零命中，排除法規名與產品名（Annex IV／EU AI Act／Regulation／Claude Code）；T1 後跑一次、命令寫進 ADR 證據段與 T1 Step 2；不加閘（閘數 12 固定、D15 是寫作紀律）。
18. **BL-00002（grill 事實查核發現、本波不改工具）**：GT-10 對 `docs/arc42/09-architecture-decisions.md` 的兩腿在首個 AI-ADR 落地（「目前無」句移除）後互斥——子項名冊腿要 `rad_ai_map` 鍵 ⊇ E5 七欄、第八腿要值＝同檔 `###`，但 E5 子項住 ADR body 的 `####`；處置屬工具改動（E5 改由 ADR 檔面守或豁免 §9 兩腿、一正一反自證）、觸發＝首個 AI-ADR 開寫前；T1 落帳、next bump BL-00003。
19. **F11 理由句改引實查出處**：四段形（來源／刺激／環境／量測）只見於 RAD-AI 總覽、adoption-guide 與詞彙表的摘要句，reference 與模板皆六段。F04「五類」在 RAD-AI 文件內查無出處、不一致欄照附錄 A 措辭、理由只寫「七類是超集」。
20. **翻案觸發器不追 upstream**：D15 拍板不建 rad-ai-pin、不立觸發式待辦；觸發器寫成「rev6 自行改採新版 RAD-AI（README 一句的對照 HEAD 更新）且不一致集合改變」。
21. **T3 出口 `TODO(波` grep 排除 `decisions/`**：ADR-00005 正文提及一次 `TODO(波 k)`（決策敘述、非佔位）、GT-10 面本就不含 decisions。

### 0.3 波次表縮編紀錄（不改啟動書；波 5 brainstorm 以此為準）

| 波 | 波 3 計畫剩餘欄 | 本波吸收 | 剩餘 |
|---|---|---|---|
| 4 | RAD-AI 23 筆取捨 ADR（附錄 A 進 ADR） | 全部（＋F24；＋F03／F12 兩句活書小補；＋D15 正文兩處英文歸零；＋BL-00002 落帳） | 無 |
| 5 | 文件創世驗收：addressability 自評（§7 形、F24 不適用值）、三指標首值或 n/a、DoD A 六條逐條、tmp-clean（含 `tmp/rev5-handoff/`） | — | 同左 |

---

## Global Constraints

- 語言：一切書面產物 zh-TW；RAD-AI 子節名、欄位、檢核表列文字全部中文改寫、英文原名只出現在 frontmatter `rad_ai_map` 鍵（D15）——**含 ADR-00007 正文**。
- 面：`docs/arc42/decisions/` 屬現在式面——GT-04（形制／不可變）、GT-05（裸編號）、GT-06 連結腿掃；時態腿與 GT-10 形制不掃。活書兩處改動（process／c4）受 GT-06 時態＋GT-10 形制全掃。本檔（史料面）只受 GT-06 連結腿：路徑一律反引號、不放 Markdown 連結；散文不寫三反引號字面。
- 時態（活書兩句）：禁詞 待決／TBD／⏳／已完成／下一步（ERROR）；預告詞 屆時／日後／將由（WARN）。
- 前代引用：一律 `rev5:`／`rev4:` 前綴；ADR 內不引 rev5 ADR 號；`000-` 家族除外。
- ADR 形制：檔名 `ADR-00007-<slug>.md`、frontmatter 八欄（id 加引號、date `YYYY-MM-DD`、supersedes／superseded_by 空清單、provenance 字串、tags 清單）、body 六節＋證據段；accepted 落地即凍結（改動＝新 ADR supersedes）。
- 每個事實只有一個家：取捨結果只在 ADR-00007；F24 用法只在 compliance 檢核表用法段；RAD-AI 對照 HEAD 只在 README；閘名冊只在 `GATES.md`。
- 工具：零改動；`python3 tools/docsync test` 88 綠、`lint` 0 錯 0 警（2 閘 Day-1 跳過）、`check` 零漂移；閘數恆 12。
- git：分支 `000-w4-rad-ai-tradeoffs`（自 `rev6-admin-root` @ 8c42ac1）；commit 訊息 zh-TW、一律 `git commit -F <暫存檔>`；每步後以 `git rev-parse HEAD`／`git status --porcelain` 自證；merge 需 user 當次同意；不 push；rev5 樹絕不寫入。
- 新檔先 `git add` 再 generate、再 lint（lint 面＝tracked，未 add 的新檔＝假綠、索引缺列）。
- 環境：/mnt/d drvfs——每次 Bash 自 repo 根起手；跑過 docker bind mount（含 bootstrap）後同 shell 先重新 `cd`；以工件自證。
- 單元收尾序（CLAUDE.md §2）：③落帳早於⑤generate；每 Task 末＝`python3 tools/docsync generate` → `git add docs/generated docs/arc42/ARCHITECTURE.md docs/ops/LESSONS.md` → lint 全綠 → 一顆 commit。

---

## 檔案結構

```
docs/process/P-E1-boundary.md                          「四段邊界契約」表後 +1 句（F03 指針雙向）（T1）
docs/c4/C4-E1-ai-component-stereotypes.md              「標註準則」第 3 條 +半句（F12）；導言英文刻板型名→中文五型（D15）（T1）
docs/arc42/09-architecture-decisions.md                §9.1 對映表 reference 欄→欄序＋名冊指針（D15）（T1）
docs/ops/BACKLOG.md                                    +BL-00002（GT-10 §9 兩腿互斥、觸發＝首個 AI-ADR 開寫前）；next→BL-00003（T1）
docs/arc42/decisions/ADR-00007-rad-ai-tradeoffs.md     accepted；全文＝本檔 §1（T2）
docs/generated/DECISIONS-INDEX.md、STATE.md            重生：BACKLOG 開放 2（T1）；ADR 7 列／帳面 ADR 7（T2）；現在波 5（T3）
docs/ops/NOTES.md                                      波標記 5＋現況（波 4 落地物）＋下一步（波 5 文件創世驗收）（T3）
docs/ops/events.jsonl                                  misc 收單事件（merge 後簿記）＋perf 事件（隨下一顆）（T3）
tmp/000-w4-progress.md                                 恢復點（gitignored）
```

---

## 1. ADR-00007 全文草稿（T2 逐字落地；grill 審此節）

檔名 `docs/arc42/decisions/ADR-00007-rad-ai-tradeoffs.md`。以下為整檔內容（text 圍欄內；落地時去掉圍欄）：

```text
---
id: "ADR-00007"
title: RAD-AI 23 筆內部不一致的 rev6 取捨與量表第四值「不適用」——reference 為預設仲裁者、逐筆例外採模板或 adoption-guide；射程＝系統層形制、流程層偏離以「類比張力：」宣告
date: 2026-09-03
status: accepted
supersedes: []
superseded_by: []
provenance: "啟動書 D3（逐筆取捨、reference 預設；R1-F18 改述）、附錄 A 19 列（F01～F24）、§0.3 A2 與 §7（F24）、§3.4 第 2 條、D15、D16；user 拍板 2026-09-03（波 4 brainstorm Q1～Q3、grill Q4）"
tags: [governance, rad-ai]
---

## 背景

- 啟動書把 RAD-AI（對照 HEAD 記於 README 一句）定為 rev6 文件骨架的參考來源；其 reference、模板、adoption-guide、範例與 README 各層彼此有 23 處不一致（附錄 A）。D3 拍板「逐筆取捨、reference 為預設仲裁者、例外於採哪份欄註明」，§5 波 4 列要求把取捨進 ADR——啟動書是史料面，取捨要有權威面的家。
- rev6 另加一筆刻意偏離（F24）：RAD-AI 的 0／1／2 量表在「系統層目前無 AI 元件」時會把「無物可寫」誤評為 0 分。
- 波 2／3 已依附錄 A 建骨架並填實：系統層（arc42 E 子節、`docs/c4/` E 三檔、`docs/compliance/`）全為「目前無 AI 元件」句＋指針，形制尚未被使用；流程層（`docs/process/`，D16 的開發流程 AI 代理）51 子節每節以「類比張力：」首句宣告與 RAD-AI 原形的差異，其中五處與附錄 A 所採欄集不同（見證據段）。

## 決策驅動因子

- 每個事實只有一個家（RL-0049）：取捨結果若只住啟動書，AI 元件進場時無權威面可依、也無翻案紀律（supersede 鏈）。
- 啟動書 §3.4 第 2 條與 D16 早已預期流程層是類比、有硬套處；流程層 P-E7 九欄形由波 3 grill 拍板，不由本表重開。
- as-built 不回灌 ADR（CLAUDE.md §4）：流程層現況隨首個編排刀變、不能凍進 accepted body。
- D15：RAD-AI 子節名、欄名、檢核列文字一律中文改寫，英文原名不入正文；波 2／3 正文尚有兩處英文（§9.1 對映表 reference 欄、C4-E1 導言刻板型名），對照鍵的家本就是 frontmatter 鍵與工具名冊、正文不該有第二家。

## 考慮過的替代案

1. **射程管兩層、流程層向附錄 A 靠**（改 P-E7／P-E2／P-E3／P-E6 欄集）：重開波 3 拍板、四檔改表且 GT-10 第八腿同步；流程層本來就沒有模型 id、嚴重度、負責人可填——棄。
2. **流程層五處偏離逐筆入表當「刻意偏離」列**：把會隨刀變的現況凍進 accepted body、之後一改形就得 supersede 整份——棄。
3. **拆兩份 ADR**（仲裁規則一份、逐筆表一份）：結果表離開規則讀不懂、同日同源多一列索引——棄。
4. **表不入 ADR、住活書 §9.1 或 RULES**：失去凍結與翻案紀律；RULES 改列動 RULES-VERSION——棄。
5. **先 proposed 再 accepted**：對賬已於 brainstorm 完成、表無未決列；多一次 status 改動無益——棄。
6. **把 §9.1 與 C4-E1 兩處正文英文登記為 D15 例外、活書不動**：例外一開就有名冊要維護、日後 D15 機器化須逐處豁免；英文名冊已在工具常數、改欄序即零例外——棄。

## 決定

1. **仲裁規則**（D3 的枚舉形）：reference 為預設仲裁者；採模板或 adoption-guide 者以本表「採哪份」欄逐筆註明、未註明者一律 reference；例外靠枚舉、不靠通則推導；範例層一律不採。
2. **射程**：本表規範系統層——arc42 E 子節、`docs/c4/` E 三檔、`docs/compliance/` 兩檔——在 AI 元件進場時的形制。流程層（`docs/process/`）是類比：偏離以該子節首句「類比張力：」宣告即可，不構成對本表的違反、不入本表。
3. **取捨表**（19 列涵蓋 F01～F24；欄名、子節名皆中文改寫）：

| 列 | 不一致 | rev6 取捨 | 採哪份 | 理由 |
|---|---|---|---|---|
| F01 | E4 關注五類：reference 有安全無透明、模板有透明無安全 | 取聯集六節（公平／可解釋／人類監督／透明／隱私／安全） | 聯集 | 兩者皆為法規面向、取聯集不丟資訊 |
| F02 | E4 關注矩陣只在 reference 有、模板與範例零命中 | 依 reference 建矩陣：列＝AI 元件、欄＝六關注；每格＝指標／門檻／頻率／負責人 | reference | 矩陣是 E4 的中心工件、缺它即無法逐元件對賬 |
| F03 | E1 契約四段（輸出型／信心規格／換版頻率／fallback 行為）與 C4-E3 三性質（信心規格／fallback 策略／降級輪廓）互斥 | 四段與三性質各自保留、互相指針、不合併 | 各自 reference | 同一契約兩種粒度（元件級／圖級）；合併會使一方失去家 |
| F04 | E7 債類五類與七類兩說 | 七類（邊界侵蝕／糾纏／隱藏回饋迴圈／資料依賴債／管線債／設定債／模型陳舊） | reference | 七類是超集、少一類＝該類債無家 |
| F05 | E7 登記欄：模板七欄缺類別與估計工作量 | 九欄（id／類別／描述／嚴重度／影響元件／緩解計畫／估計工作量／負責人／狀態） | reference | 估計工作量是排程依據、類別欄讓單表可篩 |
| F06 | E7 id 前綴與狀態值域兩套 | id＝每類自有分類前綴＋三位流水；狀態四值（開放／處理中／已緩解／接受附理由） | 模板（id）／reference（狀態） | 分類前綴讓 id 自帶類別；四值多「處理中」才表達得了進行中 |
| F07 | E2 清冊六欄與八欄兩說 | 八欄（模型 id／名稱／任務／框架／版本／狀態／負責人／最近再訓練日） | reference | 負責人與最近再訓練日是 E8 再訓練政策與 E7 模型陳舊的輸入 |
| F08 | E2 版本史與效能基線欄名兩套 | 用 reference 欄名：版本史＝版本／日期／主要變更／主要指標／狀態；效能基線＝指標／門檻／現值／量測頻率 | reference | reference 給欄名與範例、模板只有段名 |
| F09 | E5 AI 特定考量：reference 七欄、模板五子節 | 模板五子節（資料集特性／公平與偏誤取捨／模型生命週期／可解釋／法規合規）＋對映表住 §9.1 | 模板＋對映 | 五子節是七欄的合併形（壽命與再訓練觸發併為生命週期、替代案歸 body 節）；對映表＝E5 的對照鍵（E5 子項住 ADR body、無 `###` 可掛 `rad_ai_map`），reference 欄以欄序表示、英文名冊住 `tools/docsync/book.py` |
| F10 | E3 品質閘欄名兩說、模板無閘表 | 五欄（閘號／位置／檢查型／門檻／失敗動作） | reference | 三性質加位置與閘號才定位得了每道閘 |
| F11 | E6 情境六段與四段兩說 | 六段（來源／刺激／工件／環境／回應／回應量測） | 模板＝reference | 六段是模板與 reference 一致之形；四段只見於總覽、adoption-guide 與詞彙表的摘要句 |
| F12 | C4-E1 標註準則逐型附註漏特徵庫 | 五刻板型（ML 模型／資料管線／特徵庫／監測／人在迴圈）各有必填性質 | 補 | 五刻板型皆在 reference 定義、標註不可缺一型 |
| F13～F16 | 範例層四處錯誤 | 不採範例 | — | 範例內部矛盾（附錄 B 已列不採） |
| F17 | E8 子節數：reference 四必備、模板另有事故應變 | 四必備（監測／再訓練政策／部署策略／回退政策）＋事故應變 | 兩者 | 四必備是骨架、事故應變是營運不可少之節 |
| F18 | C4-E2 兩案子節不齊 | 六子節（資料源清冊／血緣圖／血緣明細／新鮮度需求／隱私流／schema 登錄） | 模板 | 模板六子節是齊全形 |
| F19／F20 | 覆蓋數互斥、README 自述與結構不符 | 不引用 | — | 數字互斥、自述失真 |
| F21 | 採用順序兩套 | adoption-guide 三階段（可見性／決策治理／營運成熟） | adoption-guide | 採用順序是 adoption-guide 的正題 |
| F22／F23 | 範例排版與多欄表形 | 依模板（每類一表、多欄） | 模板 | 排版屬模板職掌 |
| F24（rev6 新增） | 量表只有 0／1／2 | 加第四值「不適用」、附理由、獨立於 0、不計分 | 刻意偏離 | 系統層無 AI 元件時 0 分＝誤報缺文件 |

4. **F24 的家**＝`docs/compliance/annex-iv-checklist.md` 用法段與 §7 形自評表；不入 RULES 名詞段（量表值、非規則）。
5. **D15 在活書正文零例外**：RAD-AI 英文原名只住 frontmatter `rad_ai_map` 鍵與工具名冊（`tools/docsync/book.py` E_SUBSECTIONS）；E5 的對照以 §9.1 欄序＋名冊承載、C4-E1 刻板型以中文名＋簡寫承載；機器判＝活書正文（去 frontmatter）大寫英文雙詞零命中（排除法規名與產品名）。

## 後果

- 首個 AI 功能刀進場時，系統層各 E 子節與 C4 E 三檔照本表形制填；本表任一列要翻＝新 ADR supersedes 本檔。
- 流程層可繼續依類比張力演進、不觸動本檔；流程層某形若要被系統層採用，走新 ADR。
- RAD-AI 對照 HEAD 只記於 README 一句；本檔不記 HEAD 字面。
- DECISIONS-INDEX 加一列；閘、規則、生成器零改動。
- 活書正文英文 RAD-AI 名歸零（§9.1 表改欄序、C4-E1 導言中文化）；首個 AI-ADR 落地前須先處置 GT-10 對 §9 兩腿的互斥（`docs/ops/BACKLOG.md` BL-00002）。

## 翻案觸發器

- rev6 自行改採新版 RAD-AI（README 一句的對照 HEAD 更新）且不一致集合改變；不追蹤 upstream、不設 pin（D15）。
- 首個 AI 功能刀證明某列形制不可行（例：E7 九欄無法填）。
- 流程層某形需成為系統層形制（類比反向輸入系統層）。

## 證據（附錄 A 對 as-built 對賬、2026-09-03）

- 系統層：arc42 §3.3／§5.4／§6.2／§8.5／§10.3／§11.3／§13 皆「目前無 AI 元件」句＋指針；`docs/c4/` E 三檔與 `docs/compliance/` 兩檔的表欄與本表一致（F12 逐型必填性質住 C4-E1 刻板型定義表「必填性質」欄；F03 指針雙向：P-E1 四段邊界契約指向 C4-E3、C4-E3 邊界介面指回 E1）——本表零使用、零衝突。
- 流程層五處以「類比張力：」宣告的偏離：P-E7 九欄欄集與三值狀態（對 F05／F06）、P-E2 四欄＋`docs/generated/reference/agents.md` 四欄（對 F07；逐模型明細硬套、F08 無承載）、P-E3 品質閘指針句（對 F10）、P-E6 四欄情境（對 F11）、P-E4 矩陣轉置為列＝關注（對 F02）。依決定 2 不入表。
- 其餘列（F01／F04／F09／F13～F16／F17／F18／F19／F20／F21／F22／F23／F24）as-built 與取捨一致（F24：compliance 23 鍵全「不適用」附理由；F09 對映表以欄序承載）。
- D15：活書正文（arc42 節檔、c4、process、compliance；去 frontmatter）大寫英文雙詞 grep、排除 Annex IV／EU AI Act／Regulation／Claude Code——零命中（波 4 T1 後）。
```

---

## 2. 附錄 A 對 as-built 對賬表（brainstorm 實查；ADR 證據段的展開版）

| 列 | 附錄 A 取捨 | as-built（2026-09-03） | 判 |
|---|---|---|---|
| F01 | E4 取聯集六節 | P-E4 六關注含「透明」、7/7 | 一致 |
| F02 | 依 reference 建矩陣 | P-E4 有矩陣但轉置：列＝關注、欄＝適用／承載／守門（reference：列＝AI 元件、欄＝關注） | 部分（流程層、類比張力已宣告） |
| F03 | E1 四段、C4-E3 三性質、互相指針 | P-E1 四段 ✓；C4-E3 三性質契約欄 ✓ 且指向 E1；E1 側零指向 C4-E3 | 部分→T1 補一句 |
| F04 | E7 七類 | P-E7 七類 `###` | 一致 |
| F05 | E7 九欄（reference 欄集） | P-E7 九欄但欄集不同（無 id／嚴重度／工作量／負責人；多 來源／觸發／守門／覆審條件） | 偏離（流程層、已宣告） |
| F06 | id 分類前綴＋狀態四值 | 無 id 欄；狀態三值 已守／未守／刻意不守 | 偏離（流程層、已宣告） |
| F07 | E2 清冊八欄 | P-E2 四欄＋`reference/agents.md` 四欄 | 偏離（流程層、已宣告） |
| F08 | 版本史／基線用 reference 欄名 | P-E2 逐模型明細＝硬套、無表 | 不適用於 as-built |
| F09 | E5 模板五子節＋對映表 | §9.1 五子節＋七欄對映表（reference 欄為英文名→T1 改欄序，D15） | 一致（承載改欄序） |
| F10 | E3 品質閘五欄 | P-E3 品質閘＝指針句（三層閘、不重抄 GATES.md） | 偏離（流程層、已宣告） |
| F11 | E6 六段情境 | P-E6 四欄；§10.2（官方子節、非 E6）亦四欄 | 偏離（流程層、已宣告） |
| F12 | C4-E1 標註準則補齊五型 | 刻板型定義表五型齊、逐型必填性質住「必填性質」欄；標註準則為五條通則 | 部分（承載換位）→T1 補半句 |
| F13～F16 | 不採範例 | 範例字樣全 repo 零命中 | 一致 |
| F17 | E8 四必備＋事故應變 | P-E8 五子節、§13 同 | 一致 |
| F18 | C4-E2 六子節 | 六 `###` | 一致 |
| F19／F20 | 不引用 | 零命中 | 一致 |
| F21 | adoption-guide 三階段 | `rad_ai_stage` 1／2／3／compliance → RAD-AI-MAP 採用階段欄 | 一致 |
| F22／F23 | 模板排版 | P-E7 每類一表、P-E6 每屬性一節 | 一致 |
| F24 | 量表加「不適用」附理由 | compliance 23 鍵全「不適用」附理由；§7 自評表＝波 5 | 一致 |

命令備查（唯讀）：RAD-AI 原文＝`../fork260509-rev5/tmp/RAD-AI/documentation/arc42-extensions-reference.md`、`c4-extensions-reference.md`、`templates/arc42-extensions/*.md`、`templates/c4-extensions/*.md`；as-built＝`grep -n '^#\{2,4\} ' docs/arc42/*.md docs/c4/C4-E*.md docs/process/*.md`＋各表首列；範例字樣＝`git grep -n -i 'urban.mobility\|route.optim\|AIDB-\|QG-00\|MDL-' -- 'docs/**' README.md`（排除啟動書後 0）。

---

## 3. 活書四處＋BACKLOG 一列（T1 逐字）

1. `docs/process/P-E1-boundary.md`「四段邊界契約」表之後、下一個 `###` 之前，加一段：
   「圖級同源＝`docs/c4/C4-E3-non-determinism-boundary.md` 邊界介面欄「三性質契約」（信心規格／fallback 策略／降級輪廓）；元件級四段與圖級三性質互指、不合併。」
2. `docs/c4/C4-E1-ai-component-stereotypes.md`「標註準則」第 3 條句末（「人在迴圈另標觸發條件與回應 SLA」之後、句號之前）加：
   「；各型必填性質＝刻板型定義表「必填性質」欄（五型齊）」。
3. `docs/arc42/09-architecture-decisions.md` §9.1：首段「AI 特定考量以五個子節承載、對應 RAD-AI reference 七欄如下（「考慮過的替代案」屬 body 節、非 AI 特定子節）。」改為「AI 特定考量以五個子節承載、對應 RAD-AI reference 七欄如下（欄序＝reference 七欄順序、英文名冊住 `tools/docsync/book.py` 的 E_SUBSECTIONS；「考慮過的替代案」屬 body 節、非 AI 特定子節）。」；表改為兩欄「AI 特定考量子節（中文改寫）｜reference 欄序」，六列＝資料集特性→2、公平與偏誤取捨→3、模型生命週期→4＋5、可解釋→6、法規合規→7、（body 節）考慮過的替代案→1；其餘（「目前無 AI 元件」句、指針句）不動。
4. `docs/c4/C4-E1-ai-component-stereotypes.md` 導言首句「AI 元件刻板型（<<ML Model>>、<<Data Pipeline>>、<<Feature Store>>、<<Monitor>>、<<Human-in-the-Loop>> 五類、中文改寫）的標註規則與標註表；」改為「AI 元件刻板型五類（ML 模型／資料管線／特徵庫／監測／人在迴圈；中文改寫、簡寫見刻板型定義表）的標註規則與標註表；」，句餘不動。
5. `docs/ops/BACKLOG.md`：檔頭 next→`BL-00003`；append 一列：
   「- BL-00002｜governance｜GT-10 對 `docs/arc42/09-architecture-decisions.md` 的兩腿在首個 AI-ADR 落地（「目前無」句移除）後互斥：子項名冊腿要 `rad_ai_map` 鍵 ⊇ E5 七欄、第八腿要值＝同檔 `###`，而 E5 子項住 ADR body 的 `####`→ E5 改由 ADR 檔面守或豁免 §9 兩腿（工具改動、一正一反自證）｜觸發：首個 AI-ADR 開寫前」

---

## 4. Tasks

### Task 1: 活書四處（F03 指針雙向、F12 必填性質指針、D15 正文英文歸零）＋BL-00002 落帳

**Files:** Modify `docs/process/P-E1-boundary.md`（§3 第 1 條）、`docs/c4/C4-E1-ai-component-stereotypes.md`（§3 第 2／4 條）、`docs/arc42/09-architecture-decisions.md`（§3 第 3 條）、`docs/ops/BACKLOG.md`（§3 第 5 條）。

- [ ] **Step 1: 寫入**：照本檔 §3 逐字；不動任何 `###`、不動 frontmatter；09 的「目前無 AI 元件」句與 C4-E1 的同句保留原字面（RAD-AI-MAP「目前無」判準）。
- [ ] **Step 2: 驗**：`grep -n 'C4-E3' docs/process/P-E1-boundary.md` 命中 1；`grep -n '必填性質' docs/c4/C4-E1-ai-component-stereotypes.md` 命中 2 行（表首欄＋準則第 3 條）；`grep -c '<<' docs/c4/C4-E1-ai-component-stereotypes.md`＝0；`grep -c 'Dataset\|Trade-offs\|Compliance' docs/arc42/09-architecture-decisions.md`＝0；`grep -c '欄序' docs/arc42/09-architecture-decisions.md` ≥ 2；D15 機器自證（§0.2-17；逐檔去 frontmatter 後 `grep -n '[A-Z][a-z]\{2,\} [A-Z][a-z]\{2,\}'`、排除 Annex IV／EU AI Act／Regulation／Claude Code）＝0 命中；`head -1 docs/ops/BACKLOG.md`＝`<!-- next: BL-00003 -->`、`grep -c '^- BL-' docs/ops/BACKLOG.md`＝2；`python3 tools/docsync generate` → `git add docs/generated`（STATE「BACKLOG 開放：2」；RAD-AI-MAP 計數不變：P-E1 5/5、C4-E1／E5 目前無）；`python3 tools/docsync lint` 0 錯 0 警；`python3 tools/docsync check` 零漂移。
- [ ] **Step 3: Commit**（`-F` 檔）：`docs(book): D15 正文英文歸零（§9.1 對映表改欄序、C4-E1 導言中文化）＋F03 指針雙向＋F12 必填性質指針；BACKLOG +BL-00002（GT-10 §9 兩腿互斥）`；`tmp/000-w4-progress.md` 記 T1 完成＠SHA。

### Task 2: ADR-00007 accepted＋索引重生

**Files:** Create `docs/arc42/decisions/ADR-00007-rad-ai-tradeoffs.md`（全文＝本檔 §1 圍欄內容）；重生 `docs/generated/DECISIONS-INDEX.md`、`docs/generated/STATE.md`。

- [ ] **Step 1: 寫檔**：自本檔 §1 圍欄逐字落地（去圍欄）；`git add docs/arc42/decisions/ADR-00007-rad-ai-tradeoffs.md`。
- [ ] **Step 2: 自證 D15／GT-05**：`grep -c '[A-Za-z]\{4,\} [A-Z][a-z]\+ [A-Z][a-z]\+' docs/arc42/decisions/ADR-00007-rad-ai-tradeoffs.md`＝0（無英文欄名串）；`grep -n 'rev5' docs/arc42/decisions/ADR-00007-rad-ai-tradeoffs.md` 空；`grep -c '](' docs/arc42/decisions/ADR-00007-rad-ai-tradeoffs.md`＝0（零 Markdown 連結）。
- [ ] **Step 3: generate → 驗**：`python3 tools/docsync generate`；`grep -c '^| ADR-' docs/generated/DECISIONS-INDEX.md`＝7；`grep -n 'ADR-00007 | accepted' docs/generated/DECISIONS-INDEX.md` 命中且 feature 欄「輕量軌」；`grep -n '^- ADR：' docs/generated/STATE.md` 顯示 `7（proposed 0、accepted 7、superseded 0）`；`git add docs/generated`；`python3 tools/docsync lint` 0 錯 0 警；`python3 tools/docsync check` 零漂移。
- [ ] **Step 4: Commit**（`-F` 檔）：`docs(adr): ADR-00007 RAD-AI 23 筆取捨＋F24 量表第四值 accepted——射程＝系統層、流程層以類比張力宣告；DECISIONS-INDEX 7 列`；progress 檔記 T2。

### Task 3: 波 4 出口驗收＋波標記 bump 5（merge 停點在此）

**Files:** Modify `docs/ops/NOTES.md`（首行 `<!-- wave: 5 -->`；現況＝波 4 落地物：ADR-00007 accepted、對賬零未決、活書兩句；下一步＝波 5 文件創世驗收四件（addressability 自評、三指標首值或 n/a、DoD A 六條逐條、tmp-clean 含 `tmp/rev5-handoff/`）＋首刀指針；未決兩條不動）。

- [ ] **Step 1: 出口 checklist（全部以工件自證）**：①`grep -c '^| ADR-' docs/generated/DECISIONS-INDEX.md`＝7 且 ADR-00007 accepted ②`grep -rn --exclude-dir=decisions 'TODO(波' docs/arc42 docs/c4 docs/compliance docs/process | wc -l`＝0（ADR-00005 的敘述性提及不在 GT-10 面） ③`python3 tools/docsync test` 88 綠 ④`python3 tools/docsync lint` 0 錯 0 警（GT-04／GT-05 綠、GT-08 Day-1 跳過） ⑤`python3 tools/docsync check` 零漂移 ⑥`bash tools/bootstrap.sh` rc 0（純體檢；跑完重新 `cd`） ⑦RAD-AI-MAP 流程層八列 N/N、系統層十二列「目前無」 ⑧Day-1 仍 2 筆 ⑨RULES-VERSION 仍 `c7a137209e0e` ⑩STATE「BACKLOG 開放：2」（BL-00001、BL-00002）⑪D15 機器自證再跑一次＝0。
- [ ] **Step 1b: final holistic review（自審、不落報告、不落事件）**：`git diff rev6-admin-root...HEAD --stat` 全 diff 對本檔 §1～§3 逐項核（ADR 全文＝§1 逐字、活書兩句＝§3 逐字、對賬表＝§2）；findings 三分流（修／BL／won't-fix ADR）；處置清單存 scratchpad、逐項寫入 Step 5 收單 commit 訊息（RL-0073）。
- [ ] **Step 2: NOTES 改**（波標記 5）→ generate（STATE 現在波 5）→ lint → commit（`-F` 檔）：`docs(ops): 波 4 出口——波標記 5、現況與下一步`；progress 檔記 T3。
- [ ] **Step 3: 停——merge 需 user 同意**（AskUserQuestion：merge --no-ff 回 rev6-admin-root／保留分支不 merge／其他）。
- [ ] **Step 4（同意後）: merge**：訊息寫檔 → 在 rev6-admin-root `git merge --no-ff -F <檔> 000-w4-rad-ai-tradeoffs` → `git log -1` 核 merge commit。
- [ ] **Step 5: 簿記 commit**：`docs/ops/events.jsonl` append misc（category governance、merge 全 SHA、backlog_add＝`["BL-00002"]`（T1 落帳）、notes 含「ADR-00007 accepted、附錄 A 24 筆對賬零未決、活書四處（D15 正文零英文）、分支保留供 audit、Day-1 仍 2」）→ generate → lint → commit：`docs(ops): 波 4 收單簿記`（訊息逐項列 final review 處置）。
- [ ] **Step 6: perf 第四步**：量簿記 commit 牆鐘、append `close_bookkeeping` perf 事件（隨下一顆 commit 入帳；RL-0053）。

---

## Self-Review

- **Spec coverage**：啟動書 §5 波 4 列剩餘唯一項「RAD-AI 23 筆取捨 ADR」（T2）＋出口「DECISIONS-INDEX 首批；GT-04／GT-05／GT-08 全綠」（T3 ①④）；附錄 A F24（表末列＋§0.2-9 家）；D3 仲裁規則（決定 1）；§3.4 第 2 條與 D16（決定 2）；D15（Global Constraints 第 1 條＋T1 活書四處歸零＋T1／T3 機器自證＋ADR 決定 5）；grill Q4（§0.1）；BL-00002（§0.2-18、T1、T3 misc backlog_add）；波 3 計畫 §0.3 剩餘欄全入（§0.3 表）。
- **Placeholder scan**：本檔零 TBD／TODO 字面；每 Task 有實際檔名、逐字內容（§1／§3）、驗證命令與預期值。
- **Type consistency**：ADR 檔名 `ADR-00007-rad-ai-tradeoffs.md` 在 §1、檔案結構、T2、T3 一致；frontmatter 八欄與 ADR-00006 同形；DECISIONS-INDEX 列數 7、STATE `accepted 7` 與 T2／T3 斷言一致；tests 88、RULES-VERSION `c7a137209e0e`、Day-1 2 皆與現帳一致；BACKLOG next `BL-00003`、STATE「BACKLOG 開放：2」在 §3、T1、T3 一致。
- **Risk／Guard／Rollback**：Risk＝ADR 表 accepted 即凍結、若某列寫錯只能 supersede→Guard＝§1 全文先過 grill、T3 Step 1b 對 §1 逐字核、T2 Step 2 三條機器自證→Rollback＝merge 前 `git reset --hard` 回 T1 顆重寫（accepted 尚未進 default 分支）；merge 後＝新 ADR supersedes。
