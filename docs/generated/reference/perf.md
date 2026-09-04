<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# reference/perf — 收刀簿記與 pre-commit 效能資料點

來源＝docs/ops/events.jsonl 的 perf 事件（generate 重算；kind＝close_bookkeeping／precommit_chain、量測法承 rev5:RUNBOOK §12.1）。

| date | kind | wall_s | rc | commit | notes |
|---|---|---|---|---|---|
| 2026-09-03 | close_bookkeeping | 6.33 | 0 | cdc11c5 | 波 1 收單簿記型 commit（events＋NOTES＋generated、零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行。 |
| 2026-09-03 | close_bookkeeping | 6.8 | 0 | 87e072f | 波 2 收單簿記型 commit（events＋NOTES＋generated、零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行（Day-1 餘 2、GENERATED_FILES 10）。 |
| 2026-09-03 | close_bookkeeping | 6.9 | 0 | 0727dbc | 波 3 收單簿記型 commit（events＋generated、零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行（Day-1 餘 2、GENERATED_FILES 12）。 |
| 2026-09-03 | close_bookkeeping | 7.7 | 0 | 578cef9 | 波 4 收單簿記型 commit（events＋generated、零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行（Day-1 餘 2、GENERATED_FILES 12、ADR 7）。 |
| 2026-09-03 | close_bookkeeping | 8.5 | 0 | c8985e3 | 波 5 收單簿記型 commit（events＋generated、零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行（Day-1 餘 1、GENERATED_FILES 12、ADR 7、events 11）。 |
| 2026-09-04 | close_bookkeeping | 6.51 | 0 | 6339433 | 000-r1 收單簿記型 commit（events＋generated＋計畫複本、零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行（Day-1 餘 1、GENERATED_FILES 12、ADR 8、events 14）。 |
| 2026-09-04 | precommit_chain | 16.91 | 0 | 9b8f02c | 本刀 U3 外層 commit（24 檔：docsync 新模組＋tests、兩快照、兩真表、hook、schema-gate 註解、orchestration 骨架、tasks／NOTES／BACKLOG／LL-00002、generated）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈並行＝betterleaks、docsync check、lint、selftest-docsync（117 案）、selftest-schema-gate（103 案）、entity-drift 實跑（staged 含 schema 快照觸發、實比對 14 表 0 findings）；雙錨 45／90 內（T037 ≤45 s 成立）。 |
| 2026-09-04 | close_bookkeeping | 8.0 | 0 | 0aacc05 | 001 刀收刀簿記型 commit（events feature_close＋NOTES＋BACKLOG 刪兩列＋generate 三檔＋.gitleaks.toml allowlist 一條；零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行，staged 未含 tools/ 故工具自測與 entity-drift 段皆未觸發。★首次量測被 betterleaks 擋下（pins.api 40-hex SHA 撞 generic-api-key、1.33 秒 rc 1）、收 allowlist 後重量；本值為通過顆之牆鐘。 |
| 2026-09-04 | close_bookkeeping | 9.57 | 0 | df744fc | 輕量軌（數量預算只警告不擋）收單簿記型 commit（events misc＋generated 兩檔；零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行，staged 未含 tools/ 故工具自測與 entity-drift 段皆未觸發。 |
| 2026-09-04 | close_bookkeeping | 6.04 | 0 | 558c6ef | 輕量軌（規格對照審查修單）收單簿記型 commit（events misc＋generated 兩檔；零 gitlink 零工具本體）；量法＝date +%s.%N 包 git commit 整命令、單次；pre-commit 全鏈含 betterleaks、docsync check、lint 並行，staged 未含 tools/ 亦未含 specs/001-schema-baseline/fixtures 或 data-model，故工具自測、entity-drift 與本批新增之 schema-frozen 三段皆未觸發。 |
