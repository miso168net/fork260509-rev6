<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=1584407｜rust-api=71e37fd

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.3.0

## 帳面統計
- ADR：29（proposed 0、accepted 28、superseded 1）
- RULES：76 條／上限 92（implementer 40/48、review 14/18、fix 16/19、主線 43/52、人 10/12）
- BACKLOG 開放：28｜滯後：2
- LESSONS：18 筆
- events：48 筆（erratum 2、feature_close 2、misc 18、perf 22、review 4）
- CLAUDE.md 行數：160（只報表、不擋）

## 治理指標（啟動書 §4.3 三項＋ADR-00021 檢索性）
| 指標 | 值 | 目標 | 狀態 |
|---|---|---|---|
| 治理批對 feature 比 | 9.0 | ≤1 | 超標 |
| LESSONS 重複率 | 0.17 | 0 | 超標 |
| BACKLOG 淨流量（rolling 3 刀） | n/a | ≤0 | — |
| 檢索性（最近獨立輪 doc-governance） | ≤3 跳 0.76／答對 1.0／找不到 0／答錯 0（否定對照答錯 0）；平均最短 hops 1.68 | 找不到＋答錯＝0；≤3 跳比例輪間不降 | 達標；輪間不降 —（需前輪值） |

## 數量預算對賬（D8；ADR-00011：超限只警告、不擋）
| 項目 | 現值 | 上限 | 狀態 |
|---|---|---|---|
| 閘數 | 12 | 12 | 內 |
| RULES 總 | 76 | 92 | 內 |
| RULES implementer | 40 | 48 | 內 |
| RULES review | 14 | 18 | 內 |
| RULES fix | 16 | 19 | 內 |
| RULES 主線 | 43 | 52 | 內 |
| RULES 人 | 10 | 12 | 內 |
| docsync 行數 | 3543 | 4000 | 內 |

## 最近事件（尾 3 筆、新在前）
- 2026-09-08｜perf｜close_bookkeeping｜close_bookkeeping 1.46 秒 rc=0
- 2026-09-08｜misc｜governance｜maint-py313-docstring-dedent｜輕量軌 maint-py313-docstring-dedent 收單：閘區塊 regex 去掉對 docstring 縮排的依賴。Python ≥3.13 …
- 2026-09-07｜perf｜close_bookkeeping｜close_bookkeeping 18.07 秒 rc=0
