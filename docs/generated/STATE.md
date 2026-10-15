<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=9fe562d｜rust-api=34aa3d6

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.8.1

## 帳面統計
- ADR：95（proposed 0、accepted 78、superseded 17）
- RULES：87 條／上限 92（implementer 45/48、review 18/18、fix 20/19、主線 51/52、人 10/12）
- BACKLOG 開放：9｜滯後：4
- LESSONS：93 筆
- events：127 筆（erratum 2、feature_close 7、misc 48、perf 61、review 9）
- CLAUDE.md 行數：165（只報表、不擋）

## 治理指標（啟動書 §4.3 三項＋ADR-00021 檢索性）
| 指標 | 值 | 目標 | 狀態 |
|---|---|---|---|
| 治理批對 feature 比 | 6.57 | ≤1 | 超標 |
| LESSONS 重複率 | 0.19 | 0 | 超標 |
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
| docsync 行數 | 4216 | 4000 | 超 |

## 最近事件（尾 3 筆、新在前）
- 2026-10-16｜misc｜governance｜maint-backlog-142-146｜maint-backlog-142-146 收單（user 2026-10-15 依 008 前 BACKLOG 體檢 v10 開批；第一批＝治理面）：BL-…
- 2026-10-15｜perf｜close_bookkeeping｜close_bookkeeping 16.28 秒 rc=0
- 2026-10-15｜feature_close｜007-user-password-admin｜007 user-password-admin 收單（rev6 第七刀）：島 I 使用者域治理入憲／使用者管理十端點（清單・回收桶兩讀端＋新增・部分更新・刪除…
