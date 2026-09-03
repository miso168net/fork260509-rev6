---
section: 3
summary: 業務脈絡與技術脈絡；E1 AI 邊界劃定的系統層落點
rad_ai: [E1]
rad_ai_stage: 1
rev5_blueprint:
  §3 系統脈絡: 不承襲：rev5 空節（該節自述尚無內容）；rev6 §3 自 C4-L1 起手
---
# §3 脈絡與範圍

## 3.1 業務脈絡

管理員經瀏覽器操作後台（能力級見 §1.1）；系統對外只有一種外部依賴——SMTP 寄信（dev＝mailpit 收信匣）。無對外開放 API、無第三方登入、無行動端。

| 對象 | 互動 |
|---|---|
| 管理員 | 登入、管理使用者／角色／選單、系統設定、看審計與 IP 規則 |
| SMTP 服務 | 系統寄出通知信；dev 由 mailpit 收下、prod 為真 SMTP |

## 3.2 技術脈絡

系統脈絡圖＝[C4-L1 系統脈絡](../c4/C4-L1-system-context.md)（同圖不複製；E1 標註畫在該圖上）。

| 介面 | 協定 | 兩端 |
|---|---|---|
| 瀏覽器 ↔ front-nginx | HTTPS（TLS 終端與反向代理） | 管理員 ↔ 系統入口 |
| front-nginx → base-web／rust-api | HTTP（容器網路） | 入口 → 前端靜態／後端 API（prod `/api/*` 前綴、憲法 §II #3） |
| rust-api → SMTP | SMTP（dev＝mailpit 容器） | 後端 → 寄信 |

rev5 對照 stack（埠 2xxxx）是驗收基準、不屬本系統脈絡（CLAUDE.md §7）。

## 3.3 E1 AI 邊界劃定

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E1 邊界劃定](../process/P-E1-boundary.md)。
