<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=506e3b4｜rust-api=34aa3d6

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.8.1

## 帳面統計
- ADR：93（proposed 0、accepted 77、superseded 16）
- RULES：86 條／上限 92（implementer 44/48、review 16/18、fix 18/19、主線 51/52、人 10/12）
- BACKLOG 開放：11｜滯後：4
- LESSONS：91 筆
- events：125 筆（erratum 2、feature_close 7、misc 47、perf 60、review 9）
- CLAUDE.md 行數：165（只報表、不擋）

## 治理指標（啟動書 §4.3 三項＋ADR-00021 檢索性）
| 指標 | 值 | 目標 | 狀態 |
|---|---|---|---|
| 治理批對 feature 比 | 6.43 | ≤1 | 超標 |
| LESSONS 重複率 | 0.19 | 0 | 超標 |
| BACKLOG 淨流量（rolling 3 刀） | -23 | ≤0 | 達標 |
| 檢索性（最近獨立輪 doc-governance） | ≤3 跳 0.76／答對 1.0／找不到 0／答錯 0（否定對照答錯 0）；平均最短 hops 1.68 | 找不到＋答錯＝0；≤3 跳比例輪間不降 | 達標；輪間不降 —（需前輪值） |

## 數量預算對賬（D8；ADR-00011：超限只警告、不擋）
| 項目 | 現值 | 上限 | 狀態 |
|---|---|---|---|
| 閘數 | 12 | 12 | 內 |
| RULES 總 | 86 | 92 | 內 |
| RULES implementer | 44 | 48 | 內 |
| RULES review | 16 | 18 | 內 |
| RULES fix | 18 | 19 | 內 |
| RULES 主線 | 51 | 52 | 內 |
| RULES 人 | 10 | 12 | 內 |
| docsync 行數 | 4170 | 4000 | 超 |

## 最近事件（尾 3 筆、新在前）
- 2026-10-15｜feature_close｜007-user-password-admin｜007 user-password-admin 收單（rev6 第七刀）：島 I 使用者域治理入憲／使用者管理十端點（清單・回收桶兩讀端＋新增・部分更新・刪除…
- 2026-10-15｜perf｜precommit_chain｜precommit_chain 55.11 秒 rc=0
- 2026-10-06｜misc｜governance｜007 刀第一筆事件（tasks T003 施工前提顆）：補記 BL-00140／BL-00141（brainstorm 定稿顆 5bfd07b 入 BACK…
