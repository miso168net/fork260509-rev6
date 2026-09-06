---
section: 4
summary: 技術選擇、頂層分解、品質目標達成法
rev5_blueprint:
  §4 解法策略: 承襲（五條策略對 rev6 仍真、上位＝憲法 §I.1～I.5）
---
# §4 解法策略

## 技術選擇

- **從上游重來的 fork 策略**：base-web 自 upstream `example` tip 衍生、fork 差異以軌道制治理（憲法 §III）；rust-api 全新寫、對前代 source 受控參照——讀允許、拷貝禁止、註解重寫、拍板已推翻者不帶回（憲法 §I.5）。
- **base-web 為權威**：前端有的功能、後端必供對應端點；menu 權限以 casbin enforce、DB-first 寫入、寫後全量重載（憲法 §I.1／§I.2）。
- **wire 契約機器化**：前端 typings 為裁判、contract test＋coverage gate 守恆、13 碼矩陣凍結（憲法 §I.3；機制＝`tools/wire-schema.py` 快照裁判＋`contract.rs` 雙向覆蓋，002 已 as-built）。
- **傘狀雙脊椎與縱切刀工作流**：傘狀 repo 管文件／spec／編排，兩子體各自成倉；兩段式 commit（worktree 內 commit→外層 pin bump）保證每個外層 commit 可重現；功能以縱切刀交付、走 SDD＋TDD（憲法 §I.4）。
- **機器優先文件觀＋人審機器閘**：文件為機器與人共讀而設計，每個事實一個人寫的家、鏡像一律機器生成（`tools/docsync`）、契約 lint 在 commit 當下強制；AI 代理產物必經人審與機器閘（憲法 §I.8）。

## 頂層分解

| 區塊 | 職責 | 真源 |
|---|---|---|
| `base-web/` | 前端（soybean-admin fork、Vite） | 子庫 worktree、外層 gitlink pin |
| `rust-api/` | 後端 API（Rust；隨刀建置） | 子庫 worktree、外層 gitlink pin |
| `deploy/` | compose 三檔的設定檔、機密（sops×age 密文入版控） | `docker-compose*.yml`、`deploy/secrets/README.md` |
| `tools/` | 治理工具鏈（docsync 十二閘與生成器、編排骨架、看門狗、bootstrap） | `tools/docsync/`、`tools/orchestration/`、`tools/bootstrap.sh` |
| `docs/` | 活書家族、ops 帳本、事件源、機器生成物 | `docs/arc42/`、`docs/c4/`、`docs/compliance/`、`docs/process/`、`docs/ops/`、`docs/generated/` |

## 品質目標達成法

| §1.2 目標 | 手段 | 守門 |
|---|---|---|
| 安全 | 授權單一判定點、每請求 DB-fresh；fail-* 方向隨行為島入憲；機密只以密文入版控 | 憲法 §I.2／§I.7；GT-07、betterleaks |
| 契約守恆 | typings 抽 JSON Schema 當裁判；每條 route 必有 contract case | 憲法 §I.3；`tools/wire-schema.py`（碼面閘）＋`rust-api/server/tests/contract.rs` |
| 可重現 | gitlink pin＝worktree HEAD；bootstrap 一鍵幂等重建 | GT-02；`tools/bootstrap.sh` |
| 文件與碼零漂移 | 生成物只由真源重算；名冊同源、數量預算 | GT-01／GT-12 |
| UI 與 rev5 一致 | 兩 stack 併行、CDP 三方比對（rev5／rev6／example） | CLAUDE.md §7 走查流程 |
