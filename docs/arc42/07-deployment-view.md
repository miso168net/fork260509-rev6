---
section: 7
summary: 基礎設施兩層；容器拓樸＝C4-L2、埠＝reference/ports
rev5_blueprint:
  §7 部署: 不承襲：rev5 空節；rev6 §7 自 C4-L2 與 reference/ports 起手
---
# §7 部署視圖

## 7.1 基礎設施第一層

容器拓樸＝[C4-L2 容器視圖](../c4/C4-L2-container.md)（同圖不複製）；host 埠真表＝[reference/ports](../generated/reference/ports.md)（世代 3xxxx、ADR-00001）。

- **dev stack**：於 repo 根 `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait` 一鍵起（起停與觀測 profiles＝RUNBOOK §1～§3）；migrate 容器為啟動閘、失敗則 rust-api 不啟。
- **兩 stack 併行**：rev5 對照 stack 常駐 2xxxx、rev6 走 3xxxx，兩者不衝突、併行是預期形（CLAUDE.md §7）；rev6 的 psql 絕不指向 rev5 庫。
- **入口**：front-nginx 為系統入口（TLS 終端、反向代理 base-web 與 rust-api）；其餘 host 埠皆為維運與對照用、只綁 127.0.0.1（真表＝ports）。

## 7.2 基礎設施第二層

- **compose 三檔的組合形**：`docker-compose.yml`（基底：front-nginx／base-web／rust-api／migrate／postgres／redis 與觀測層）＋`docker-compose.dev.yml`（dev 疊加：mailpit）＋`docker-compose.example.yml`（soybean example 原版基線、對照用）。
- **profiles**：`obs`（loki／alloy／socket-proxy／grafana）、`metrics`（prometheus／exporters／pushgateway／grafana）、`jobs`（reaper）；例行只 up／stop／ps。
- **卷與機密**：named volume 卷名帶 project 前綴（RUNBOOK §5）；機密＝sops×age 密文入版控、執行期解密到 SECRETS_DIR（`deploy/secrets/README.md`、RUNBOOK §15）。
- **prod 形**：`/api/*` 前綴由 front-nginx strip 轉發、`/api/metrics` 擋塊（憲法 §II #3）；部署 checklist＝RUNBOOK §16。
