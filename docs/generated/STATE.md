<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=386e366｜rust-api=9952cfa

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.5.2

## 帳面統計
- ADR：56（proposed 0、accepted 49、superseded 7）
- RULES：81 條／上限 92（implementer 43/48、review 16/18、fix 17/19、主線 46/52、人 10/12）
- BACKLOG 開放：14｜滯後：4
- LESSONS：48 筆
- events：100 筆（erratum 2、feature_close 5、misc 38、perf 48、review 7）
- CLAUDE.md 行數：162（只報表、不擋）

## 治理指標（啟動書 §4.3 三項＋ADR-00021 檢索性）
| 指標 | 值 | 目標 | 狀態 |
|---|---|---|---|
| 治理批對 feature 比 | 7.6 | ≤1 | 超標 |
| LESSONS 重複率 | 0.06 | 0 | 超標 |
| BACKLOG 淨流量（rolling 3 刀） | 14 | ≤0 | 超標 |
| 檢索性（最近獨立輪 doc-governance） | ≤3 跳 0.76／答對 1.0／找不到 0／答錯 0（否定對照答錯 0）；平均最短 hops 1.68 | 找不到＋答錯＝0；≤3 跳比例輪間不降 | 達標；輪間不降 —（需前輪值） |

## 數量預算對賬（D8；ADR-00011：超限只警告、不擋）
| 項目 | 現值 | 上限 | 狀態 |
|---|---|---|---|
| 閘數 | 12 | 12 | 內 |
| RULES 總 | 81 | 92 | 內 |
| RULES implementer | 43 | 48 | 內 |
| RULES review | 16 | 18 | 內 |
| RULES fix | 17 | 19 | 內 |
| RULES 主線 | 46 | 52 | 內 |
| RULES 人 | 10 | 12 | 內 |
| docsync 行數 | 4136 | 4000 | 超 |

## 最近事件（尾 3 筆、新在前）
- 2026-09-29｜misc｜governance｜maint-backlog-127｜maint-backlog-127 收單（user 2026-09-29：BL-00127 單獨成輕量軌）：組裝形 workflow 每支 agent 之模型…
- 2026-09-29｜misc｜governance｜記帳 BL-00127（user 2026-09-29 指示先記 BACKLOG、另排輕量軌）：組裝形 workflow 之 agent effort＝xhi…
- 2026-09-29｜perf｜close_bookkeeping｜close_bookkeeping 14.4 秒 rc=0
