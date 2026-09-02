<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# reference/ports — host 埠正典表

來源＝docker-compose.yml＋docker-compose.dev.yml＋docker-compose.example.yml 的 ports: 段（generate 重算；配號紀律＝ADR-00001、世代 3xxxx）。

| 服務 | host | 容器內側 | 檔 |
|---|---|---|---|
| base-web | 32081 | 80 | docker-compose.dev.yml |
| example-dev | 32089 | 80 | docker-compose.example.yml |
| front-nginx | 32080 | 80 | docker-compose.dev.yml |
| front-nginx | 32443 | 443 | docker-compose.dev.yml |
| grafana | 33000 | 3000 | docker-compose.dev.yml |
| loki | 33100 | 3100 | docker-compose.dev.yml |
| mailpit | 38025 | 8025 | docker-compose.dev.yml |
| postgres | 35432 | 5432 | docker-compose.dev.yml |
| prometheus | 39090 | 9090 | docker-compose.dev.yml |
| pushgateway | 39091 | 9091 | docker-compose.dev.yml |
| redis | 36379 | 6379 | docker-compose.dev.yml |
| rust-api | 32079 | 8080 | docker-compose.dev.yml |
