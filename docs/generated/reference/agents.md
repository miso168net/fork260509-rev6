<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# reference/agents — 編排 script 的模型與 effort 名冊

來源＝tracked `tools/orchestration/*.js`／`*.mjs`（名冊內生成物 `_sk_rules.js` 除外）的 `const <NAME>_OPTS = { model, effort }` 字面（generate 重算）；角色×刻板型×產物進哪道閘＝`docs/process/P-E2-agent-registry.md`（人寫）；換模史＝git。

| script | 常數 | model | effort |
|---|---|---|---|
| _sk_head.js | IMPL_OPTS | fable[1m] | xhigh |
| _sk_head.js | REVIEW_OPTS | opus[1m] | xhigh |
| _sk_head.js | FIX_OPTS | opus[1m] | xhigh |
