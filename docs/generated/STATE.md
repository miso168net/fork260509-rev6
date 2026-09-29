<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=2248b89｜rust-api=d9c4e2f

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.6.0

## 帳面統計
- ADR：62（proposed 0、accepted 55、superseded 7）
- RULES：83 條／上限 92（implementer 43/48、review 16/18、fix 17/19、主線 48/52、人 10/12）
- BACKLOG 開放：12｜滯後：3
- LESSONS：48 筆
- events：107 筆（erratum 2、feature_close 5、misc 41、perf 52、review 7）
- CLAUDE.md 行數：162（只報表、不擋）

## 治理指標（啟動書 §4.3 三項＋ADR-00021 檢索性）
| 指標 | 值 | 目標 | 狀態 |
|---|---|---|---|
| 治理批對 feature 比 | 7.8 | ≤1 | 超標 |
| LESSONS 重複率 | 0.06 | 0 | 超標 |
| BACKLOG 淨流量（rolling 3 刀） | 14 | ≤0 | 超標 |
| 檢索性（最近獨立輪 doc-governance） | ≤3 跳 0.76／答對 1.0／找不到 0／答錯 0（否定對照答錯 0）；平均最短 hops 1.68 | 找不到＋答錯＝0；≤3 跳比例輪間不降 | 達標；輪間不降 —（需前輪值） |

## 數量預算對賬（D8；ADR-00011：超限只警告、不擋）
| 項目 | 現值 | 上限 | 狀態 |
|---|---|---|---|
| 閘數 | 12 | 12 | 內 |
| RULES 總 | 83 | 92 | 內 |
| RULES implementer | 43 | 48 | 內 |
| RULES review | 16 | 18 | 內 |
| RULES fix | 17 | 19 | 內 |
| RULES 主線 | 48 | 52 | 內 |
| RULES 人 | 10 | 12 | 內 |
| docsync 行數 | 4136 | 4000 | 超 |

## 最近事件（尾 3 筆、新在前）
- 2026-09-30｜perf｜close_bookkeeping｜close_bookkeeping 12.9 秒 rc=0
- 2026-09-30｜misc｜governance｜maint-tz-utc｜maint-tz-utc（時區裁定施作）收單（user 2026-09-29 聲明＋2026-09-30 逐題裁定）：DB 伺服器時區以 compose 命令…
- 2026-09-29｜perf｜close_bookkeeping｜close_bookkeeping 12.69 秒 rc=0
