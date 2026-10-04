<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=fb4dac2｜rust-api=67a7d3e

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.7.1

## 帳面統計
- ADR：73（proposed 0、accepted 64、superseded 9）
- RULES：85 條／上限 92（implementer 44/48、review 16/18、fix 18/19、主線 50/52、人 10/12）
- BACKLOG 開放：13｜滯後：3
- LESSONS：66 筆
- events：118 筆（erratum 2、feature_close 6、misc 45、perf 57、review 8）
- CLAUDE.md 行數：163（只報表、不擋）

## 治理指標（啟動書 §4.3 三項＋ADR-00021 檢索性）
| 指標 | 值 | 目標 | 狀態 |
|---|---|---|---|
| 治理批對 feature 比 | 7.17 | ≤1 | 超標 |
| LESSONS 重複率 | 0.09 | 0 | 超標 |
| BACKLOG 淨流量（rolling 3 刀） | -20 | ≤0 | 達標 |
| 檢索性（最近獨立輪 doc-governance） | ≤3 跳 0.76／答對 1.0／找不到 0／答錯 0（否定對照答錯 0）；平均最短 hops 1.68 | 找不到＋答錯＝0；≤3 跳比例輪間不降 | 達標；輪間不降 —（需前輪值） |

## 數量預算對賬（D8；ADR-00011：超限只警告、不擋）
| 項目 | 現值 | 上限 | 狀態 |
|---|---|---|---|
| 閘數 | 12 | 12 | 內 |
| RULES 總 | 85 | 92 | 內 |
| RULES implementer | 44 | 48 | 內 |
| RULES review | 16 | 18 | 內 |
| RULES fix | 18 | 19 | 內 |
| RULES 主線 | 50 | 52 | 內 |
| RULES 人 | 10 | 12 | 內 |
| docsync 行數 | 4163 | 4000 | 超 |

## 最近事件（尾 3 筆、新在前）
- 2026-10-05｜perf｜close_bookkeeping｜close_bookkeeping 16.69 秒 rc=0
- 2026-10-05｜misc｜governance｜maint-backlog-137-133｜maint-backlog-137-133 收單（user 2026-10-04 依 BACKLOG 體檢 v8 開批）：BL-00137 壓縮 hook 背…
- 2026-10-04｜perf｜close_bookkeeping｜close_bookkeeping 15.21 秒 rc=0
