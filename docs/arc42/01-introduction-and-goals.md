---
section: 1
summary: 系統定位、品質目標、利害關係人；RAD-AI 論文缺口段
rev5_blueprint:
  §1 簡介與目標: 承襲（能力級／明確不做／建置狀態改寫為 rev6 現況）
---
# §1 簡介與目標

## 1.1 需求概覽

rev6-admin 是一套管理後台系統：前端 fork 自 soybean-admin（Vue3／TypeScript／naive-ui），基線＝upstream `example` 分支 tip（D14、SHA 由 `tools/bootstrap.sh` 斷言）；後端以 Rust 全新寫、對前代 source 受控參照（憲法 §I.5）。系統經 rev1～rev5 五代演進，本代自 rev5 交接包重起；rev5 凍結為唯讀藍本與 UI 對照基準（ADR-00002）。

**能力級**（以 base-web 為權威——前端有的功能、後端必供對應端點，範圍不縮減；憲法 §I.1）：使用者／角色／選單管理、casbin RBAC（menu／button 維度）、認證與 session 治理、系統設定、審計（操作／存取／登入嘗試）、IP 存取控制、觀測層。

**明確不做**：多租戶、對外開放 API、行動端。

**建置狀態**：現況帳＝`docs/generated/STATE.md`（pins、現在波、帳面統計）與 `docs/ops/NOTES.md`（當前意圖）；各域隨刀建置、刀序由首刀 brainstorm 決定（D13）。

本框架要解的缺口（RAD-AI 論文 G1～G5、中文改寫）：

| 缺口 | 一句 | rev6 承載 |
|---|---|---|
| G1 | arc42 官方節沒有模型生命週期、資料管線、漂移的專屬位置 | E1～E8 子節（§3.3、§5.4、§6.2、§8.5、§9.1、§10.3、§11.3、§13）＋流程層 `docs/process/` |
| G2 | C4 圖沒有標示 ML 元件與非確定性邊界的圖型 | `docs/c4/` C4-E1～E3 三檔（規則疊加於 L1／L2、不另畫） |
| G3 | EU AI Act Annex IV 條文與 arc42／C4 節之間沒有對映 | `docs/compliance/` 兩檔（23 鍵檢核表＋十類映射） |
| G4 | 架構決策紀錄沒有 AI 專屬欄位 | §9.1 AI-ADR 形制（五個 AI 特定子節、不另開號空間） |
| G5 | 模型卡與資料卡沒有接進架構文件 | 流程層 P-E2「與模型卡的銜接」、P-E3「與資料卡的銜接」；系統層隨 AI 功能刀填入 |

## 1.2 品質目標

| 目標 | 動機 | 守門 |
|---|---|---|
| 安全 | 授權判定 DB-fresh、fail-closed 方向、機密不入版控 | 憲法 §I.2／§I.7；GT-07 |
| 契約守恆 | 前端 typings 為裁判、wire 契約機器化 | 憲法 §I.3；`tools/wire-schema.py`（碼面閘）＋`rust-api/server/tests/contract.rs` |
| 可重現 | 傘狀 pin、兩段式 commit、bootstrap 幂等 | GT-02；`tools/bootstrap.sh` |
| 文件與碼零漂移 | 機器優先文件觀：每個事實一個家、鏡像機器生成 | GT-01／GT-12 |
| UI 與 rev5 一致 | rev6 UI 須與 rev5 對照基準一致 | CDP 對照驗收（CLAUDE.md §7） |

## 1.3 利害關係人

| 角色 | 期望 | 接觸面 |
|---|---|---|
| 管理員（dev 帳號 Super／Admin／User） | 後台可用、與前代一致 | UI（front-nginx） |
| 營運者 | 一鍵起停、機密輪替有程序 | `docs/ops/RUNBOOK.md`、compose |
| 開發者（＝拍板者） | 拍板級親決、merge 前人審 | 憲法 §I.8、ADR |
| AI 代理（主線、implementer、review、fix） | 規則烤進 prompt、產物必經機器閘 | 流程層 `docs/process/`、`docs/ops/RULES.md` |
| upstream soybean-admin | 單向：rev6 rebase 其 `example` 分支、不回饋 | 憲法 §III 軌道 |
