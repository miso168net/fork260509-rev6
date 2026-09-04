---
section: 5
summary: 建構區塊三層白盒；E2 模型登錄視圖的系統層落點
rad_ai: [E2]
rad_ai_stage: 1
rev5_blueprint:
  §5 Building blocks: 承襲（rust-api workspace 三 crate＝migration／entity／sea-orm-adapter 已就位；server 管線形隨 002 刀進場、以 rev5 活書 §5 為藍本重打字）
---
# §5 建構區塊視圖

## 5.1 整體系統白盒

| 區塊 | 內含 | 介面 |
|---|---|---|
| `base-web/` | soybean-admin fork 全樹（upstream 原樣分層、程式碼 fork-delta 零；fork patch set 只有檔頭標記的分支來源紀錄檔 `x_fork.branch-origin.md`） | 外層 gitlink pin；容器 `base-web`（Vite dev）由 front-nginx 反代 |
| `rust-api/` | Cargo workspace：migration（m0001 結構基線＋m0002 seed 基線、承 rev5 逐位元＝憲法 §I.5 例外②）／entity（15 表 sea-orm 投影）／sea-orm-adapter（例外①、vendored casbin adapter）；server 隨 002 刀；分支來源紀錄檔 `x_fork.branch-origin.md` | 外層 gitlink pin；容器 `rust-api` 由 front-nginx 反代、依賴 postgres／redis／migrate |
| `deploy/` | compose 三檔的設定檔（nginx、prometheus、grafana、loki、alloy、trust-model）與 sops 密文 | 容器 bind mount；機密解密＝age 私鑰（RUNBOOK §15） |
| `tools/` | `docsync`（十二閘＋生成器＋refresh 照相）、`orchestration/`（`_sk_*.js` 單一骨架、EXAMPLE 成品、harness-test、cdp.mjs）、`schema-gate.py`（三閘 schema 驗證）、`entity-drift-gate.py`（entity×快照漂移）、`wf-watchdog.py`、`bootstrap.sh` | pre-commit／PreToolUse hook；Workflow 工具 |
| `docs/` | 活書家族（arc42／c4／compliance／process）、ops 帳本與事件源、generated、史料面（brainstorms／reviews） | generate 名冊（GENERATED_FILES）；GT-01 零漂移 |

容器拓樸與 service 清單見 [C4-L2 容器視圖](../c4/C4-L2-container.md)（數量以該表為準）。

## 5.2 第二層

- **base-web**：upstream `example` 分支原樣分層——`src/views`（頁）、`router`（路由；auth route mode＝dynamic、憲法 §II #2）、`store`、`service`／`service-alova`（API 客戶端）、`typings`（wire 契約裁判、憲法 §I.3）、`layouts`／`components`／`hooks`／`locales`／`theme`／`plugins`／`utils`／`constants`／`enum`／`styles`／`assets`；程式碼 fork-delta 目前為零（fork patch set 只有分支來源紀錄檔 `x_fork.branch-origin.md`），改動一律走憲法 §III 軌道並帶 `rev6-inline` 標記。另有 pnpm workspace `packages/`（工具鏈子套件）。
- **rust-api**：Cargo workspace 三 crate——`migration`（m0001 結構基線＋m0002 seed 基線、程式內容逐位元承襲 rev5 終態＝憲法 §I.5 例外②、ADR-00009）／`entity`（15 表 sea-orm 投影；與 schema 快照逐欄一致由 `tools/entity-drift-gate.py` 守恆——`casbin_rule` 委派 adapter 建基底、依 `rev4:ADR 0015` 雙向豁免，實比對 14 表）／`sea-orm-adapter`（例外①、vendored casbin adapter）；`server` crate 與管線形隨 002 刀進場、以 rev5 活書 §5 為藍本重新打字（憲法 §I.5）。

## 5.3 第三層

隨各域刀進場；本節以指針列各刀 spec（`specs/<NNN>-<feature>/`），不預載模組拓樸。

## 5.4 E2 模型登錄視圖

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E2 代理名冊](../process/P-E2-agent-registry.md)。
