<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=9fe562d｜rust-api=bba4a3d

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.8.1

## 帳面統計
- ADR：108（proposed 10、accepted 80、superseded 18）
- RULES：87 條／上限 92（implementer 45/48、review 18/18、fix 20/19、主線 51/52、人 10/12）
- BACKLOG 開放：7｜滯後：7
- LESSONS：97 筆
- events：137 筆（erratum 2、feature_close 7、misc 52、perf 66、review 10）
- CLAUDE.md 行數：165（只報表、不擋）

## 治理指標（啟動書 §4.3 三項＋ADR-00021 檢索性）
| 指標 | 值 | 目標 | 狀態 |
|---|---|---|---|
| 治理批對 feature 比 | 7.0 | ≤1 | 超標 |
| LESSONS 重複率 | 0.23 | 0 | 超標 |
| BACKLOG 淨流量（rolling 3 刀） | -23 | ≤0 | 達標 |
| 檢索性（最近獨立輪 doc-governance） | ≤3 跳 0.76／答對 1.0／找不到 0／答錯 0（否定對照答錯 0）；平均最短 hops 1.68 | 找不到＋答錯＝0；≤3 跳比例輪間不降 | 達標；輪間不降 達標（0.48→0.76） |

## 數量預算對賬（D8；ADR-00011：超限只警告、不擋）
| 項目 | 現值 | 上限 | 狀態 |
|---|---|---|---|
| 閘數 | 12 | 12 | 內 |
| RULES 總 | 87 | 92 | 內 |
| RULES implementer | 45 | 48 | 內 |
| RULES review | 18 | 18 | 內 |
| RULES fix | 20 | 19 | 超 |
| RULES 主線 | 51 | 52 | 內 |
| RULES 人 | 10 | 12 | 內 |
| docsync 邏輯行 | 3652 | 4000 | 內 |

## 最近事件（尾 3 筆、新在前）
- 2026-10-19｜perf｜close_bookkeeping｜close_bookkeeping 18.4 秒 rc=0
- 2026-10-19｜misc｜governance｜maint-pre008-carriers｜maint-pre008-carriers 收單（008 前 BACKLOG 體檢 v11 之承接批；user 2026-10-18 開工令「九項全掛」）：D…
- 2026-10-17｜perf｜close_bookkeeping｜close_bookkeeping 16.88 秒 rc=0
