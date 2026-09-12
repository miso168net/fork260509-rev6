---
section: 5
summary: 建構區塊三層白盒；E2 模型登錄視圖的系統層落點
rad_ai: [E2]
rad_ai_stage: 1
rev5_blueprint:
  §5 Building blocks: 承襲（rust-api workspace 四 crate＝migration／entity／sea-orm-adapter／server；server 管線 as-built 見 §5.2、以 rev5 活書 §5 為藍本重打字＝憲法 §I.5）
---
# §5 建構區塊視圖

## 5.1 整體系統白盒

| 區塊 | 內含 | 介面 |
|---|---|---|
| `base-web/` | soybean-admin fork 全樹（upstream 原樣分層；程式碼 fork-delta＝三支新增型新檔〔typings／settings service／auth service〕、inline 修改型 6 處（`.env` 2／`.env.test` 1／`.env.prod` 1＝BASE-WEB-ADAPT、`src/store/modules/route/index.ts` 1＝BASE-WEB-AUTH-WIRING(a)、`src/layouts/modules/global-header/components/user-avatar.vue` 1＝BASE-WEB-LOGOUT-UX-WIRING(i)；同檔另新增型圈界 2 處），軌道與標記定形見 §8.4）；fork patch set 另含檔頭標記的分支來源紀錄檔 `x_fork.branch-origin.md` | 外層 gitlink pin；容器 `base-web`（Vite dev）由 front-nginx 反代 |
| `rust-api/` | Cargo workspace：migration（m0001 結構基線＋m0002 seed 基線、承 rev5 逐位元＝憲法 §I.5 例外②）／entity（15 表 sea-orm 投影）／sea-orm-adapter（例外①、vendored casbin adapter）／server（HTTP 服務 crate；模組＝`main`／`lib` boot 鏈、`config`、`state`、`obs`（tracing＋metrics）、`envelope`、`error`、`router`、`auth`、`cache`（session／節流熱快取：redis 鍵 builder、GET／SET 原語與 boot 建連）、`request_context`、`validation`、`handler`、`model`（`facade`＝entity 存取唯一管道、`password`＝argon2id 驗密純函式）；模組分層、契約測試面與 ROUTES 真表見 §5.2）；分支來源紀錄檔 `x_fork.branch-origin.md` | 外層 gitlink pin；容器 `rust-api` 由 front-nginx 反代、依賴 postgres／redis／migrate |
| `deploy/` | compose 三檔的設定檔（nginx、prometheus、grafana、loki、alloy、trust-model）與 sops 密文；建置檔 `Dockerfile.rust-api`／`Dockerfile.age`；機密與維運 CLI 群（generate-secrets／preflight-secrets／decrypt-secrets、sops.sh、backup-db、setup-reaper-role 等，逐支見 README 文件系統地圖 `deploy/` 段） | 容器 bind mount；機密解密＝age 私鑰（RUNBOOK §15） |
| `tools/` | `docsync`（十二閘＋生成器＋refresh 照相）、`orchestration/`（`_sk_*.js` 單一骨架＝TDD 與 review 兩種主流程共用首段、`assemble.py` 組裝器、harness-test／harness-review、EXAMPLE 成品與 review 單元定義範本、cdp.mjs）、`schema-gate.py`（三閘 schema 驗證）、`entity-drift-gate.py`（entity×快照漂移）、`rust-fmt-gate.py`（rust 格式）、`wire-schema.py`（wire 契約快照）、`fork-delta-lint.py`（base-web fork-delta 標記）、`wf-watchdog.py`、`bootstrap.sh`；碼面閘名冊＝RUNBOOK §12 碼面閘表 | pre-commit／PreToolUse hook；Workflow 工具 |
| `docs/` | 活書家族（arc42／c4／compliance／process）、ops 帳本與事件源、generated、史料面（brainstorms／reviews） | generate 名冊（GENERATED_FILES）；GT-01 零漂移 |

容器拓樸與 service 清單見 [C4-L2 容器視圖](../c4/C4-L2-container.md)（數量以該表為準）。

## 5.2 第二層

- **base-web**：upstream `example` 分支原樣分層——`src/views`（頁）、`router`（路由；as-built＝`.env` `VITE_AUTH_ROUTE_MODE=dynamic`〔003 刀 U5 翻自 upstream 基線 `static`、憲法 §II #2 拍板〕）、`store`、`service`／`service-alova`（API 客戶端）、`typings`（wire 契約裁判、憲法 §I.3）、`layouts`／`components`／`hooks`／`locales`／`theme`／`plugins`／`utils`／`constants`／`enum`／`styles`／`assets`；程式碼 fork-delta＝`src/typings/api/rev6-settings.d.ts`／`src/service/api/rev6-settings.ts`／`src/service/api/rev6-auth.ts` 三支新增型新檔（軌道與標記定形見 §8.4）、inline 修改型 6 處（`.env` 2／`.env.test` 1／`.env.prod` 1＝BASE-WEB-ADAPT、`src/store/modules/route/index.ts` 1＝BASE-WEB-AUTH-WIRING(a)、`src/layouts/modules/global-header/components/user-avatar.vue` 1＝BASE-WEB-LOGOUT-UX-WIRING(i)；同檔另新增型圈界 2 處）；fork patch set 另含分支來源紀錄檔 `x_fork.branch-origin.md`，改動一律走憲法 §III 軌道並帶 `rev6-inline` 標記。另有 pnpm workspace `packages/`（工具鏈子套件）。
- **rust-api**：Cargo workspace 四 crate——`migration`（m0001 結構基線＋m0002 seed 基線、程式內容逐位元承襲 rev5 終態＝憲法 §I.5 例外②、ADR-00009）／`entity`（15 表 sea-orm 投影；與 schema 快照逐欄一致由 `tools/entity-drift-gate.py` 守恆——`casbin_rule` 委派 adapter 建基底、依 `rev4:ADR 0015` 雙向豁免，實比對 14 表）／`sea-orm-adapter`（例外①、vendored casbin adapter）／`server`（HTTP 服務 crate；模組分層＝`router`（`ROUTES` 六欄註冊表＝路徑單一來源、依 protection 三態分派、兩道 fallback 皆 4040）→`auth`（`enforce_mw` 驗證器＋`require_policy` per-route 政策層；判定單點與 DB-fresh 見 §8.3）→`handler`→`validation`（16 鍵 registry＋型別一致性守衛）／`model/facade`（entity 存取唯一管道）→`entity`；業務 route 回應一律 `Res` 信封、錯誤一律 `AppError`（§8.2），信封例外恰二＝`ROUTES` 之 `envelope_exception` 欄標記的 `/health`（純文字）與 `/metrics`（exposition）、紀律上位＝憲法 §I.3；真表由 generate 重算為 `docs/generated/reference/routes.md`；契約測試面＝`tests/contract.rs`／`tests/wire_schema.rs`（機制＝§8.2）、`tests/entity_access_lint.rs`（facade 唯一管道之機器錨）、`tests/entity_behavior_lint.rs`（ORM 行為層機器錨＝§8.1）、`tests/health.rs`；真 DB 端點案住 `handler/system_settings.rs` 之 `endpoint_tests`（行程級 `DB_SERIAL` 互斥＋seed 還原守衛；三者之機制落點皆在 `model/facade/test_kit.rs`、該檔為 `DB_SERIAL` 的單一持有者）；以 rev5 活書 §5 為藍本重打字＝憲法 §I.5）。　★共用測試件＝`model/facade/test_kit.rs`（`#[cfg(test)]` 圈界、寄居 facade 層；名冊四群＝免 DB 件／真 DB・真 redis 設施／簽發 helper／庫態守衛，逐件以該檔頭註為準、此處不鏡像；消費者名冊不寫死、以 grep 為準＝LL-00009）。

## 5.3 第三層

隨各域刀進場；本節以指針列各刀 spec（`specs/<NNN>-<feature>/`），不預載模組拓樸。

## 5.4 E2 模型登錄視圖

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E2 代理名冊](../process/P-E2-agent-registry.md)。
