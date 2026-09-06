# rev6 編排骨架（`tools/orchestration/`；承 rev5:008-audit-settings-pages 刀骨架、D10 入 repo；BL-00001 收斂為單一骨架、BL-00006 起兩種主流程共用同一首段）

## 檔

| 檔 | 內容 |
|---|---|
| `_sk_head.js` | 兩種主流程共用的首段：防呆①args 斷言／②guard（長度、`zh-TW`、冒煙 token、規則塊版本串 `RULES-VERSION`）／③保險絲推導＋自我斷言（TDD 形由 `IMPLEMENTERS` 推、review 形由 `_plan` 段常數推且每 run ≤24 支＝wf-watchdog 25 支底線）／④兩套 schema（WORK＝status，REVIEW＝agentStatus）；**模型家單一真源**＝TDD 三角色 `IMPL_OPTS`／`REVIEW_OPTS`／`FIX_OPTS`＋review 四角色 `LENS_OPTS`／`MIRROR_OPTS`／`GRADER_OPTS`／`CRITIC_OPTS`＋`DEEP_THINK`（生成表＝`docs/generated/reference/agents.md`；★探針〔冷啟動〕復用 `LENS_OPTS`、refuter 復用 `MIRROR_OPTS`、無獨立常數）。★模式偵測＝`_vars` 段定義 `IMPLEMENTERS`（TDD）或 `REVIEW_STAGE`（review），兩者互斥、皆缺即 throw |
| `_sk_rules.js` | **機器生成**（`python3 tools/docsync generate`＝`rules emit --format js`）：`RULES`（implementer 塊）／`RULES_REVIEW`／`RULES_FIX` 三個樣板字串常數，各以 `RULES-VERSION: <12hex>` 收尾；規則本體住 docs/ops/RULES.md、**不再手維護陣列**；PreToolUse hook 對賬版本串、不符即擋；guard 另對每支渲染後 prompt 斷言含該版本串 |
| `_sk_cycle.js` | TDD 形：`rejectedBlock`＋`escalatedBlock`＋`fixPrompt`＋`cycle`（含確認輪、⑤收斂偵測、**RL-0025 清單外零改動升級分支（承 rev5:L-078、ADR-00013 改形：不終止 run、該段收斂帶升級項、已升級項重報過濾；升級項以 fix 結構化 `escalatedFindings` 記入、不論改動數——LL-00010）**）；review prompt 一律烤 `RULES_REVIEW`、fix prompt 一律烤 `RULES_FIX`、兩者首行 `DEEP_THINK`。★引用模板常數 `UNIT`／`FEATURE`／`CONTEXT`／`ALLOWED_BLOCK`／`FIX_SELFCHECK`、組裝時由變動段供 |
| `_sk_main.js` | TDD 形主流程（serial）：依 `IMPL_STAGES` 逐支派 implementer（前支 report 原文轉交後支）→ SpecReview cycle → CodeQualityReview cycle；起手自我斷言 `IMPL_STAGES.length === IMPLEMENTERS`（保險絲推導同源）；0～N 支 implementer 同一支 main——**0 支＝續跑形**（RL-0010：某階段需重跑＝新開一支只跑審查段的 workflow、新 runId；`IMPL_STAGES=[]`、已完成結論與勿重報清單寫進 `CONTEXT`） |
| `_sk_review.js` | **review 形主流程**（BL-00006；承 000-r1 四支 run 的可重用件）：`explore`＝lens∥冷啟動探針（唯讀）、可選 `INLINE_VERIFY`＝每支 lens 的 findings 即刻進 R-real／R-decided 兩鏡、探針進 grader→refuter；`verify`＝主線合併去重後的批次×兩鏡＋探針 grader→refuter＋可選完整性 critic。三態存活規則在 script 內結構化聚合（兩鏡皆確認→confirmed；任一駁回→refuted；其餘→uncertain 主線親裁），★null／`agentStatus=failed` 不殺 run（記入 `nulls`／`failed`、status 回 `partial`）。共用烤入塊（唯讀邊界／取證紀律／報前必查拍板／各角色回傳指令）與五套 schema 皆住本檔、只放「怎麼審」；刀事實住 `CONTEXT`／`DECISIONS_BLOCK`、任務句住 `_plan` |
| `assemble.py` | **組裝器**（自 tmp/001-assemble.py 入庫）：`python3 tools/orchestration/assemble.py <unitdef.py> <out.mjs>`——unitdef 的 `MODE` 決定拼接序（tdd＝vars+head+allowed+rules+context+prompts+cycle+main；review＝vars+plan+head+rules+context+review）；拼完三道自檢（①RULES-VERSION 對賬＋`zh-TW`＋`RESIDUE` 殘留 ②`node --check` ③harness：tdd 走 harness-test spec＋quality、review 走 harness-review），任一紅＝非零退出、不留產物；另對賬 unitdef 模組層 `SMOKE` 與 `VARS` 內 `const SMOKE` 同值 |
| `harness-test.mjs` | TDD 形 **控制流十二案＋逐項斷言＋退出碼**：`node harness-test.mjs <script.mjs> [spec\|quality]`（quality＝樁把 blocker 打在碼品質段）；期望值自 script 的 `const IMPLEMENTERS = <n>` 推導（n=0 續跑形：案7 改驗零 implementer 直入審查）；樁走真 `spawn`／`guard`、只替換 `agent()`；秒級 |
| `harness-review.mjs` | review 形 **九案（六正例＋三反例）＋逐項斷言＋退出碼**：`node harness-review.mjs <script.mjs>`；期望值自 `REVIEW_STAGE`／`INLINE_VERIFY`／`CRITIC`／`SMOKE` 行與回傳結構推導；樁只替換 `agent()`／`parallel()`／`pipeline()`；秒級 |
| `EXAMPLE-tdd-unitdef.py` | TDD 形單元定義範例（單 implementer→兩段審查；尖括號佔位換刀事實；`IMPLEMENTERS=0` 即續跑形） |
| `EXAMPLE-review-unitdef.py` | review 形單元定義範例（explore＋inline 兩鏡＋一支冷啟動探針；lens 任務＝編排骨架名冊與規則承載一致性——可原樣當骨架改動後的冒煙 review）；發射前照抄到 tmp/ 改 `UNIT`／`FEATURE`／`SMOKE`／`CONTEXT` |
| `EXAMPLE-review-verify-unitdef.py` | review 形單元定義範例（verify：兩批 findings×兩鏡＋探針 grader→refuter＋critic）；批文與作答為形制樣本、真跑時由主線自探索 run 的 journal 渲染 |
| `cdp.mjs` | CDP 對照工具：接 host 瀏覽器除錯埠、開分頁對照 rev5／rev6 UI（CLAUDE.md §7） |
| `EXAMPLE-dual-implementer.mjs` | TDD 形完整組裝成品（＝001 刀 U1 原樣、改形前 cycle）：雙 implementer serial、impl-1 的 report 原文轉交 impl-2；供組裝法參考、勿照抄執行（事實接地以該單元 commit 訊息為準） |

組裝成品範例＝`EXAMPLE-dual-implementer.mjs`（001 刀 U1 原樣；前代 rev5:008 兩支成品已刪＝000-r1 R1-059／060／062／087／088：內含 rev5 事實與行號形引用）；review 形以兩支 `EXAMPLE-review-*-unitdef.py`、TDD 形以 `EXAMPLE-tdd-unitdef.py` 為起手範本，成品由組裝器現產（gitignored `tmp/`）。

## 組裝法

單元定義＝一支 python 模組（`tmp/<刀>-uN.py` 形；入庫範本＝TDD 形 `EXAMPLE-tdd-unitdef.py`、review 形 `EXAMPLE-review-unitdef.py`／`EXAMPLE-review-verify-unitdef.py`；tmp/ 為 gitignored 工作區、跨 session 不保證存在），只寫變動段的 JS 原文字串；共同段由 `_sk_*.js` 供。★unitdef 的冒煙 token 兩處（模組層 `SMOKE`＝供人讀與看門狗命令、`VARS` 內 `const SMOKE`＝供 script）須同值——組裝器對賬、不同值即紅。

**TDD 形**（`MODE` 缺席或 `'tdd'`）：`VARS`（meta＋`UNIT`／`FEATURE`／`IMPLEMENTERS`／`SMOKE`／`START_LOG`）／`ALLOWED`（`ALLOWED_BLOCK`）／
`CONTEXT`（`CONTEXT`；★冒煙 token 置於此共用段＝RL-0018，guard 對每支 prompt 斷言）／`PROMPTS`（`IMPL_STAGES`＝`[{ label, phase, prompt(reports) }, …]`
——label 必含 `implementer` 字樣、prompt 收前面各支 report 陣列；`SPEC_REVIEW_PROMPT`／`QUALITY_REVIEW_PROMPT`；`FIX_SELFCHECK`＝fix 修完必跑的自驗命令一句）：

```
vars + head + allowed + rules + context + prompts + cycle + main
```

**review 形**（`MODE = 'review'`；探索＋兩鏡＝`REVIEW_STAGE = 'explore'`＋`INLINE_VERIFY = true`、主線合併去重後再驗＝`'verify'`）：`VARS`（meta＋`UNIT`／`FEATURE`／`SMOKE`／`START_LOG`／`REVIEW_STAGE`／`FINDING_CATEGORIES`／explore 另 `INLINE_VERIFY`）／
`PLAN`（explore：`LENSES=[{ key, task }]`＋`PROBES=[{ key, task }]`〔探針刻意不烤 `CONTEXT`、task 自帶冒煙 token 與 `zh-TW`〕；verify：`BATCHES=[{ batch, ids, text }]`〔text 每筆首行 `■ <id>｜<severity>｜<category>`〕＋`PROBES=[{ key, answers }]`＋`CRITIC=null｜{ scope, prior }`）／
`CONTEXT`（`CONTEXT`＋`DECISIONS_BLOCK`＝拍板紀錄清單、可為空字串）：

```
vars + plan + head + rules + context + review      （★plan 先於 head＝保險絲據其常數推導）
```

`rules` 段＝`tools/orchestration/_sk_rules.js` 原樣（generate 產物；RULES.md 改動後先 `python3 tools/docsync generate` 再重組，否則 PreToolUse hook 以 RULES-VERSION 不符擋下）。

組裝一律 `python3 tools/orchestration/assemble.py <unitdef.py> <out.mjs>`，它替你跑三道：①RULES-VERSION 對賬＋`zh-TW`＋前單元字樣殘留（`RESIDUE`＝`U2 執行單元`／`u2-…` 冒煙 token 等）②`node --check`（包進 async fn、`export const meta`→`const meta`）③對應 harness 全綠；任一紅即不留產物。發射＝`Workflow scriptPath=<out.mjs>` 與 `python3 tools/wf-watchdog.py <冒煙token>` 同回合原子成對（CLAUDE.md §2）。

## 十二案（TDD 形）在守什麼

跑滿 fix→確認輪清空判收斂（rev5:L-011 變形②）／連兩輪同 blocker 攔／fix 連兩輪零改動攔／
review `agentStatus=failed` 立即 return／**review 有 blocker 時 fix 必須真的跑**（rev5:L-011 變形①）／
**implementer `done_with_escalation` 照常跑完審查**（rev5:L-035）／implementer `blocked` 立即 return 零審查／
fix `blocked` 立即 return／最壞路徑支數 < `AGENT_FUSE`／**fix `done_with_escalation`＋零改動＝該段收斂帶升級項、進下一段**（RL-0025／ADR-00013；案 10）／**零改動升級＋駁回項續審、已升級項重報被過濾**（案 11）／**部分改動＋結構化 `escalatedFindings` 升級→次輪重報被過濾、第 2 輪收斂**（案 12；LL-00010）。
每案對派發支數、status、stage、reason 逐項斷言，任一不符 rc 1（000-r1 R1-082）；guard 在樁下照跑＝每支渲染後 prompt 的長度、`zh-TW`、冒煙 token、`RULES-VERSION` 同時被驗。

## 九案（review 形）在守什麼

派發數＝結構（lens＋probe／2×批＋2×探針＋critic）且 label 唯一、每支 opus＋schema／**三態聚合**（兩鏡皆確認→confirmed、任一駁回→refuted、缺答或不確定→uncertain；探針單鏡）／
**零 findings 跳過**（lens 零 findings 不派兩鏡、grader 零 findings 不派 refuter）／**null 回傳不殺 run**（`nulls` 留帳、status `partial`、其餘照跑、缺鏡之鍵依規則落 uncertain 或 refuted）／
**`agentStatus=failed` 不殺 run**（`failed` 留帳、該 lens 不派兩鏡）／回傳形齊全（`status`／`stage`／`smoke`／`nulls`／`failed`／`summary`／`agentsSpawned`）；三反例（RL-0051 一正一反、以讀進來的 src 就地變異驅動、皆須零派發）：args 非空→防呆① throw／`SMOKE` 取字面 `test`→防呆② throw／`_plan` 段灌到超過每 run 上限→防呆③保險絲 throw。
兩鏡三態與 grader／critic 的存活規則同 000-r1 報告 §0（`docs/reviews/20260904-doc-governance.md`）；主線拿回傳的結構化 `verdicts` 做三分流（RL-0073），不靠自由文字。

## 已知踩點（寫 script 時會遇到）

- 陣列元素用單引號時，**元素內含單引號**（如 TS 字面 `'true' | 'false'`）會斷字串 → 該元素改用雙引號包。
- shell quoted heredoc 裡**不能用** `'"'"'` 轉義（會原樣寫入而斷 JS）；要表達單引號用 `\x27`（JS 轉義、渲染正確）或改雙引號元素。
- 批次改寫引號的腳本會**誤傷字串拼接**（`'…第 ' + roundNo + ' 輪…'` 被當撞引號改寫，插值靜默失效而 `node --check` 照樣綠）→ 改完逐行看被改的是哪幾行。
- model 字串：`opus[1m]`＝`claude-opus-5[1m]`（000-r1 實證）；`fable[1m]`＝`claude-fable-5-1`（本 repo 探針 run 2026-09-04：`fable[1m]`／`claude-fable-5-1[1m]`／`claude-fable-5-1` 三種寫法於 persisted `workflows/wf_*.json` 之 `model` 欄皆解析為同一 id——fable 的 1M 為原生、後綴被正規化）。
- review 形的渲染鍵與聚合鍵同源（`lensKeys`／`probeKeys`）：鍵形一改只改那兩處——harness-review 案 2 曾抓到「渲染 `P1-P-1`、聚合 `P1-P1`」的分叉。
