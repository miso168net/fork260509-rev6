---
section: 10
summary: 品質需求概覽與情境；E6 AI 品質情境的系統層落點
rad_ai: [E6]
rad_ai_stage: 2
rev5_blueprint:
  §10 品質要求: 不承襲：rev5 空節；rev6 §10 自 §1.2 品質目標展開、情境隨島進場
---
# §10 品質需求

## 10.1 品質需求概覽

| 屬性 | §1.2 目標 | 量測 | 守門 |
|---|---|---|---|
| 安全性 | 安全 | 授權判定零快取（角色一撤、下一請求即生效）；fail-* 方向逐島明文；tracked 檔零機密實值 | 憲法 §I.2／§I.7；GT-07 |
| 契約一致性 | 契約守恆 | 每條 route 有 contract case、13 碼矩陣零偏離 | 憲法 §I.3；`tools/wire-schema.py`（碼面閘） |
| 可重現性 | 可重現 | 任一外層 commit 的 pin＝子庫 worktree HEAD；新機 bootstrap rc 0 | GT-02；`tools/bootstrap.sh` |
| 文件正確性 | 文件與碼零漂移 | generate 兩次同 bytes；名冊同源；預算表「內」 | GT-01／GT-12；STATE 預算對賬 |
| UI 一致性 | UI 與 rev5 一致 | CDP 三方比對零差異（rev5／rev6／example） | 走查流程（CLAUDE.md §7） |

## 10.2 品質情境

情境格式（每情境一個 `###`）：

| 欄 | 內容 |
|---|---|
| 刺激 | 誰在什麼環境下做了什麼（含異常：redis 失聯、PG 查詢失敗、鏈長逾上界） |
| 回應 | 系統的可觀察行為與方向（fail-open／fail-closed、降級腿） |
| 量測 | 可斷言的值：碼、HTTP status、序列計數、時限 |
| 守門 | 釘住該情境的測試或 lint |

目前零情境：憲法 §I.7 行為島（A～J）各隨其刀進場時，該島的 fail-* 方向、節流、TTL 各成一情境（承襲指針表＝憲法 §I.7）。

## 10.3 E6 AI 品質情境

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E6 品質情境](../process/P-E6-quality-scenarios.md)。
