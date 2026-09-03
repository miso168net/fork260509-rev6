# rev6 編排骨架（`tools/orchestration/`；承 rev5:008-audit-settings-pages 刀骨架、D10 入 repo；BL-00001 收斂為單一骨架）

## 檔

| 檔 | 內容 |
|---|---|
| `_sk_head.js` | 防呆①args 斷言／②guard（長度、`zh-TW`、冒煙 token）／③保險絲推導＋自我斷言／④兩套 schema（WORK＝status，REVIEW＝agentStatus）；**模型家單一真源**＝`IMPL_OPTS`／`REVIEW_OPTS`／`FIX_OPTS`＋`DEEP_THINK`（生成表＝`docs/generated/reference/agents.md`）。★`IMPLEMENTERS`／`SMOKE` 由 `_vars` 段供、缺之即 throw |
| `_sk_rules.js` | **機器生成**（`python3 tools/docsync generate`＝`rules emit --format js`）：`RULES`（implementer 塊）／`RULES_REVIEW`／`RULES_FIX` 三個樣板字串常數，各以 `RULES-VERSION: <12hex>` 收尾；規則本體住 docs/ops/RULES.md、**不再手維護陣列**；PreToolUse hook 對賬版本串、不符即擋 |
| `_sk_cycle.js` | `rejectedBlock`＋`fixPrompt`＋`cycle`（含確認輪、⑤收斂偵測、**rev5:L-078 的 done_with_escalation 分支**）；review prompt 一律烤 `RULES_REVIEW`、fix prompt 一律烤 `RULES_FIX`、兩者首行 `DEEP_THINK`。★引用模板常數 `UNIT`／`FEATURE`／`CONTEXT`／`ALLOWED_BLOCK`／`FIX_SELFCHECK`、組裝時由變動段供 |
| `_sk_main.js` | 主流程（serial）：依 `IMPL_STAGES` 逐支派 implementer（前支 report 原文轉交後支）→ SpecReview cycle → CodeQualityReview cycle；起手自我斷言 `IMPL_STAGES.length === IMPLEMENTERS`（保險絲推導同源）；1～N 支 implementer 同一支 main |
| `harness-test.mjs` | **控制流十案＋逐項斷言＋退出碼**：`node harness-test.mjs <script.mjs> [spec\|quality]`（quality＝樁把 blocker 打在碼品質段）；期望值自 script 的 `const IMPLEMENTERS = <n>` 推導；樁走真 `spawn`／`guard`、只替換 `agent()`；秒級 |
| `cdp.mjs` | CDP 對照工具：接 host 瀏覽器除錯埠、開分頁對照 rev5／rev6 UI（CLAUDE.md §7） |

組裝成品範例：目前無——前代 rev5:008 兩支成品已刪（000-r1 R1-059／060／062／087／088：內含 rev5 事實與行號形引用、非 rev6 現況）；回填義務＝首個單元收尾以其真 script 落 `EXAMPLE-<unit>.mjs`（`specs/001-schema-baseline/tasks.md` T001 附註）。

## 組裝法

每支單元只寫四段變動：`_vars`（meta＋`UNIT`／`FEATURE`／`IMPLEMENTERS`／`SMOKE`／`START_LOG`）／`_allowed`（`ALLOWED_BLOCK`）／
`_context`（`CONTEXT`；★冒煙 token 置於此共用段＝RL-0018，guard 對每支 prompt 斷言）／`_prompts`（`IMPL_STAGES`＝`[{ label, phase, prompt(reports) }, …]`
——label 必含 `implementer` 字樣、prompt 收前面各支 report 陣列；`SPEC_REVIEW_PROMPT`／`QUALITY_REVIEW_PROMPT`；`FIX_SELFCHECK`＝fix 修完必跑的自驗命令一句），再拼接：

```
vars + head + allowed + rules + context + prompts + cycle + main
```

`rules` 段＝`tools/orchestration/_sk_rules.js` 原樣（generate 產物；RULES.md 改動後先 `python3 tools/docsync generate` 再重組，否則 PreToolUse hook 以 RULES-VERSION 不符擋下）。

拼完必跑三道：①`node --check`（包進 async fn、`export const meta`→`const meta`）
②前單元字樣殘留檢查（`U2 執行單元`／`unit: 'U2'`／`u2:implementer` 等）
③`node harness-test.mjs <script> spec` 與 `node harness-test.mjs <script> quality` 皆 rc 0。

## 十案在守什麼

跑滿 fix→確認輪清空判收斂（rev5:L-011 變形②）／連兩輪同 blocker 攔／fix 連兩輪零改動攔／
review `agentStatus=failed` 立即 return／**review 有 blocker 時 fix 必須真的跑**（rev5:L-011 變形①）／
**implementer `done_with_escalation` 照常跑完審查**（rev5:L-035）／implementer `blocked` 立即 return 零審查／
fix `blocked` 立即 return／最壞路徑支數 < `AGENT_FUSE`／**fix `done_with_escalation`＋零改動當場 return 升級**（rev5:L-078）。
每案對派發支數、status、stage、reason 逐項斷言，任一不符 rc 1（000-r1 R1-082）；guard 在樁下照跑＝每支渲染後 prompt 的長度、`zh-TW`、冒煙 token 同時被驗。

## 已知踩點（寫 script 時會遇到）

- 陣列元素用單引號時，**元素內含單引號**（如 TS 字面 `'true' | 'false'`）會斷字串 → 該元素改用雙引號包。
- shell quoted heredoc 裡**不能用** `'"'"'` 轉義（會原樣寫入而斷 JS）；要表達單引號用 `\x27`（JS 轉義、渲染正確）或改雙引號元素。
- 批次改寫引號的腳本會**誤傷字串拼接**（`'…第 ' + roundNo + ' 輪…'` 被當撞引號改寫，插值靜默失效而 `node --check` 照樣綠）→ 改完逐行看被改的是哪幾行。
- model 字串：`opus[1m]`＝`claude-opus-5[1m]`（000-r1 實證）；`fable[1m]` 於 rev5 解析為 `claude-fable-5`——別名不等於 user 拍板的 fable 5.1，實際字串以本 repo 的探針 run（persisted `workflows/wf_*.json` 之 `model` 欄）為準。
