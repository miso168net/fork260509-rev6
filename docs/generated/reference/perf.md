<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# reference/perf — 收刀簿記與 pre-commit 效能資料點

來源＝docs/ops/events.jsonl 的 perf 事件（generate 重算；kind＝close_bookkeeping／precommit_chain、量測法承 rev5:RUNBOOK §12.1）。

| date | kind | wall_s | rc | commit | notes |
|---|---|---|---|---|---|
| 2026-09-03 | close_bookkeeping | 6.33 | 0 | cdc11c5 | 波 1 收單簿記型 commit（events＋NOTES＋generated、零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行。 |
| 2026-09-03 | close_bookkeeping | 6.8 | 0 | 87e072f | 波 2 收單簿記型 commit（events＋NOTES＋generated、零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行（Day-1 餘 2、GENERATED_FILES 10）。 |
| 2026-09-03 | close_bookkeeping | 6.9 | 0 | 0727dbc | 波 3 收單簿記型 commit（events＋generated、零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行（Day-1 餘 2、GENERATED_FILES 12）。 |
