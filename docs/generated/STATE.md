<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=8fea31e｜rust-api=d443278

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.1.0

## 帳面統計
- ADR：11（proposed 0、accepted 10、superseded 1）
- RULES：74 條／上限 92（implementer 38/48、review 14/18、fix 15/19、主線 42/52、人 10/12）
- BACKLOG 開放：20｜滯後：0
- LESSONS：3 筆
- events：23 筆（feature_close 1、misc 9、perf 10、review 3）
- CLAUDE.md 行數：159（只報表、不擋）

## 三指標（啟動書 §4.3）
| 指標 | 值 | 目標 |
|---|---|---|
| 治理批對 feature 比 | 9.0 | ≤1 |
| LESSONS 重複率 | 0.0 | 0 |
| BACKLOG 淨流量（rolling 3 刀） | n/a | ≤0 |

## 數量預算對賬（D8；ADR-00011：超限只警告、不擋）
| 項目 | 現值 | 上限 | 狀態 |
|---|---|---|---|
| 閘數 | 12 | 12 | 內 |
| RULES 總 | 74 | 92 | 內 |
| RULES implementer | 38 | 48 | 內 |
| RULES review | 14 | 18 | 內 |
| RULES fix | 15 | 19 | 內 |
| RULES 主線 | 42 | 52 | 內 |
| RULES 人 | 10 | 12 | 內 |

## 最近事件（尾 3 筆、新在前）
- 2026-09-04｜perf｜close_bookkeeping｜close_bookkeeping 6.04 秒 rc=0
- 2026-09-04｜misc｜governance｜001 刀規格對照審查（獨立輪 spec-compliance-001）修單收單：schema-gate 自帶測試 103→118 案補回歸保護（audit 變
- 2026-09-04｜review｜001-schema-baseline｜findings 8（修 6／BL 2／ADR 0）；BL-00020、BL-00021
