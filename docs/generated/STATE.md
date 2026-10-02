<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=2248b89｜rust-api=87c1ea1

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.7.0

## 帳面統計
- ADR：71（proposed 4、accepted 60、superseded 7）
- RULES：84 條／上限 92（implementer 43/48、review 16/18、fix 17/19、主線 49/52、人 10/12）
- BACKLOG 開放：19｜滯後：3
- LESSONS：54 筆
- events：113 筆（erratum 2、feature_close 5、misc 44、perf 54、review 8）
- CLAUDE.md 行數：163（只報表、不擋）

## 治理指標（啟動書 §4.3 三項＋ADR-00021 檢索性）
| 指標 | 值 | 目標 | 狀態 |
|---|---|---|---|
| 治理批對 feature 比 | 8.4 | ≤1 | 超標 |
| LESSONS 重複率 | 0.06 | 0 | 超標 |
| BACKLOG 淨流量（rolling 3 刀） | 14 | ≤0 | 超標 |
| 檢索性（最近獨立輪 doc-governance） | ≤3 跳 0.76／答對 1.0／找不到 0／答錯 0（否定對照答錯 0）；平均最短 hops 1.68 | 找不到＋答錯＝0；≤3 跳比例輪間不降 | 達標；輪間不降 —（需前輪值） |

## 數量預算對賬（D8；ADR-00011：超限只警告、不擋）
| 項目 | 現值 | 上限 | 狀態 |
|---|---|---|---|
| 閘數 | 12 | 12 | 內 |
| RULES 總 | 84 | 92 | 內 |
| RULES implementer | 43 | 48 | 內 |
| RULES review | 16 | 18 | 內 |
| RULES fix | 17 | 19 | 內 |
| RULES 主線 | 49 | 52 | 內 |
| RULES 人 | 10 | 12 | 內 |
| docsync 行數 | 4143 | 4000 | 超 |

## 最近事件（尾 3 筆、新在前）
- 2026-10-02｜misc｜governance｜006 刀第一筆事件（tasks T003 施工前提顆）：補記 BL-00137／BL-00138 之誕生（兩條已於 006 刀 brainstorm 定稿顆…
- 2026-09-30｜perf｜close_bookkeeping｜close_bookkeeping 14.6 秒 rc=0
- 2026-09-30｜misc｜governance｜maint-backlog-128-129-130｜maint-backlog-128-129-130 收單（user 2026-09-30 開批、本批使用容器）：BL-00128 時區環境面守衛（schema…
