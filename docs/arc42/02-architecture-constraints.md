---
section: 2
summary: 技術／組織／慣例三類約束
rev5_blueprint:
  §2 約束: 承襲（技術棧／拓樸／環境／上游關係四條＋rev6 新約束）
---
# §2 架構約束

## 技術約束

- **技術棧**：前端＝soybean-admin fork（Vue3／TypeScript／naive-ui／vite／pnpm）；後端＝Rust（axum／sea-orm／PostgreSQL／Redis／casbin）；容器化 docker compose；工作區工具＝python3 標準庫（`tools/docsync`、`tools/wf-watchdog.py`）。
- **環境**：WSL2（drvfs）為工作環境；host 無 rust toolchain，build／test 一律容器內且全程 serial（平行 cargo 互撞 target）；repo 全域 `.gitattributes` 強制 LF。
- **埠世代**：host 埠 3xxxx（ADR-00001；真表＝`docs/generated/reference/ports.md`）；rev5 對照 stack 常駐 2xxxx、兩 stack 併行為預期形。
- **書面語**：一切書面產物 zh-TW；RAD-AI 子節名、欄位、檢核表列文字全部中文改寫（D15）。

## 組織約束

- **repo 拓樸**：傘狀 repo（本 repo、default branch `rev6-admin-root`）＋兩個雙身分子體（本機 git worktree／外層 submodule gitlink）：`base-web/`（分支 `rev6-admin-base-web`、自 upstream `example` tip 衍生）與 `rust-api/`（分支 `rev6-admin-rust-api`、自源倉 main 全新寫）。fork 源倉以本機 clone 住 repo 根下（gitignored）、必須保留——worktree 的 `.git` 檔指向它。
- **rev5 唯讀凍結**：`../fork260509-rev5/` 為對照基準，三處 HEAD 由 `tools/bootstrap.sh` 斷言（ADR-00002）；絕不寫入、絕不對其 stack 做 schema／seed／設定變更。
- **人審**：push／merge 回 default 需 user 當次明確同意；拍板級項親決（憲法 §I.8）。
- **人力形**：單一開發者＋AI 代理；代理產物必經人審與機器閘。

## 慣例約束

- **fork 差異治理**：憲法 §III 軌道制——不動 inline 為預設、★軌道逐用途授權、`rev6-inline` token；upstream 常態 rebase 為預期事件。
- **前代引用**：一律 `rev5:`／`rev4:` 前綴（RL-0046）；rev5 四本帳不遷入、唯讀引用。
- **文件材質**：人寫／事件源／機器生成三材質，每個事實只有一個人寫的家（RL-0049）；活書家族永遠現在式（RL-0048）。
- **波標記**：`docs/ops/NOTES.md` 首行 `<!-- wave: N -->`＝現在波唯一真源。
