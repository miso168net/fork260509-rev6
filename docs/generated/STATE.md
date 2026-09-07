<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=50812f8｜rust-api=4ebd6ce

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.2.0

## 帳面統計
- ADR：25（proposed 0、accepted 24、superseded 1）
- RULES：74 條／上限 92（implementer 38/48、review 14/18、fix 15/19、主線 43/52、人 10/12）
- BACKLOG 開放：14｜滯後：0
- LESSONS：14 筆
- events：45 筆（erratum 2、feature_close 2、misc 17、perf 20、review 4）
- CLAUDE.md 行數：160（只報表、不擋）

## 治理指標（啟動書 §4.3 三項＋ADR-00021 檢索性）
| 指標 | 值 | 目標 | 狀態 |
|---|---|---|---|
| 治理批對 feature 比 | 8.5 | ≤1 | 超標 |
| LESSONS 重複率 | 0.21 | 0 | 超標 |
| BACKLOG 淨流量（rolling 3 刀） | n/a | ≤0 | — |
| 檢索性（最近獨立輪 doc-governance） | ≤3 跳 0.76／答對 1.0／找不到 0／答錯 0（否定對照答錯 0）；平均最短 hops 1.68 | 找不到＋答錯＝0；≤3 跳比例輪間不降 | 達標；輪間不降 —（需前輪值） |

## 數量預算對賬（D8；ADR-00011：超限只警告、不擋）
| 項目 | 現值 | 上限 | 狀態 |
|---|---|---|---|
| 閘數 | 12 | 12 | 內 |
| RULES 總 | 74 | 92 | 內 |
| RULES implementer | 38 | 48 | 內 |
| RULES review | 14 | 18 | 內 |
| RULES fix | 15 | 19 | 內 |
| RULES 主線 | 43 | 52 | 內 |
| RULES 人 | 10 | 12 | 內 |
| docsync 行數 | 3542 | 4000 | 內 |

## 最近事件（尾 3 筆、新在前）
- 2026-09-07｜misc｜governance｜maint-backlog-40-39-37｜輕量軌 maint-backlog-40-39-37 收單（003 開刀前治理維護、三條合一顆）：BL-00040 探針題庫隔離全收（否定對照表刪「真相」欄、…
- 2026-09-07｜perf｜close_bookkeeping｜close_bookkeeping 14.84 秒 rc=0
- 2026-09-07｜misc｜governance｜000-r2-doc-governance｜獨立輪 000-r2 文件治理架構第二輪體檢收單：五支 Workflow 85 支 agent、findings 102（confirmed 88）、修 69…
