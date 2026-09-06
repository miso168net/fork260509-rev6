<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# STATE — 現況機器帳

## git
- default branch：rev6-admin-root（常數＝tools/docsync/__init__.py；bootstrap 同值斷言）
- pins：base-web=50812f8｜rust-api=4ebd6ce

## 現在波
- 波：6（docs/ops/NOTES.md 首行標記）

## constitution
- 版本：1.1.0

## 帳面統計
- ADR：19（proposed 0、accepted 18、superseded 1）
- RULES：74 條／上限 92（implementer 38/48、review 14/18、fix 15/19、主線 42/52、人 10/12）
- BACKLOG 開放：13｜滯後：0
- LESSONS：11 筆
- events：29 筆（erratum 1、feature_close 2、misc 10、perf 13、review 3）
- CLAUDE.md 行數：159（只報表、不擋）

## 三指標（啟動書 §4.3）
| 指標 | 值 | 目標 |
|---|---|---|
| 治理批對 feature 比 | 5.0 | ≤1 |
| LESSONS 重複率 | 0.27 | 0 |
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
| docsync 行數 | 2871 | 4000 | 內 |

## 最近事件（尾 3 筆、新在前）
- 2026-09-06｜feature_close｜002-system-settings｜002 system-settings 收單（server crate 進場首刀）：rust-api server crate 從零（router／auth／h
- 2026-09-06｜perf｜precommit_chain｜precommit_chain 15.94 秒 rc=0
- 2026-09-05｜perf｜precommit_chain｜precommit_chain 20.8 秒 rc=0
