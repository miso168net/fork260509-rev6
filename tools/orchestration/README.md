# rev6 編排骨架（`tools/orchestration/`；承 rev5 008 刀骨架、D10 入 repo）

## 檔

| 檔 | 內容 |
|---|---|
| `_sk_head.js` | 防呆①args 斷言／②guard／③保險絲推導＋自我斷言／④兩套 schema（WORK＝status，REVIEW＝agentStatus）；`IMPLEMENTERS = 2` |
| `_sk_head1.js` | 同上、`IMPLEMENTERS = 1` |
| `_sk_rules.js` | 通用不可違反項（zh-TW／不 push／rev5 唯讀／容器 serial／cargo fmt／空間邊界／status 分值／grep 枚舉逐處判別／rev5: 前綴／TDD 先紅後綠） |
| `_sk_cycle.js` | `rejectedBlock`＋`fixPrompt`＋`cycle`（含確認輪、⑤收斂偵測、**rev5:L-078 的 done_with_escalation 分支**）。★內含 `UNIT` 變數引用，組裝時 fixPrompt 那句要參數化 |
| `_sk_main.js` | 雙 implementer 主流程（已參數化 `UNIT`／`PH1`／`PH2`／`LBL1`／`LBL2`／`START_LOG`） |
| `_sk_main1.js` | 單 implementer 主流程（同參數化；★它引用 `IMPL_PROMPT`，若變動段命名為 `IMPL1_PROMPT` 要於組裝時替換） |
| `harness-test.mjs` | **控制流十案**；`node harness-test.mjs <script.mjs>`，秒級 |
| `EXAMPLE-dual-implementer.mjs` | 完整組裝成品（＝U4）：雙 implementer serial、impl-1 的 report 烤進 impl-2 的 prompt |
| `EXAMPLE-single-implementer.mjs` | 完整組裝成品（＝U4b）：單 implementer |

## 組裝法

每支單元只寫四段變動：`_vars`（meta＋UNIT/PH/LBL/START_LOG）／`_allowed`（ALLOWED_BLOCK）／
`_context`（CONTEXT）／`_prompts`（IMPL_PROMPT〔＋impl2Prompt〕＋兩段 review），再以 python 拼接：

```
vars + head + allowed + rules + context + prompts + cycle + main
```

拼完必跑三道：①`node --check`（包進 async fn、`export const meta`→`const meta`）
②前單元字樣殘留檢查（`U2 執行單元`／`unit: 'U2'`／`u2:implementer` 等）
③`node harness-test.mjs <script>` 十案全過。

## 十案在守什麼

跑滿 fix→確認輪清空判收斂（rev5:L-011 變形②）／連兩輪同 blocker 攔／fix 連兩輪零改動攔／
review `agentStatus=failed` 立即 return／**review 有 blocker 時 fix 必須真的跑**（rev5:L-011 變形①）／
**implementer `done_with_escalation` 照常跑完審查**（rev5:L-035）／implementer `blocked` 立即 return 零審查／
fix `blocked` 立即 return／最壞路徑支數 < `AGENT_FUSE`／**fix `done_with_escalation`＋零改動當場 return 升級**（rev5:L-078）。

## 已知踩點（寫 script 時會遇到）

- 陣列元素用單引號時，**元素內含單引號**（如 TS 字面 `'true' | 'false'`）會斷字串 → 該元素改用雙引號包。
- shell quoted heredoc 裡**不能用** `'"'"'` 轉義（會原樣寫入而斷 JS）；要表達單引號用 `\x27`（JS 轉義、渲染正確）或改雙引號元素。
- 批次改寫引號的腳本會**誤傷字串拼接**（`'…第 ' + roundNo + ' 輪…'` 被當撞引號改寫，插值靜默失效而 `node --check` 照樣綠）→ 改完逐行看被改的是哪幾行。
- model 字串：`fable[1m]`＝claude-fable-5(1M)、`opus[1m]`＝claude-opus-5[1m](1M)，皆已冒煙實證。
