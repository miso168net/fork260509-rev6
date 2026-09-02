---
id: "ADR-00001"
title: host 埠配號 3xxxx 世代制——首碼 2→3、尾碼不動，D12 六值補全為十二值
date: 2026-09-03
status: accepted
supersedes: []
superseded_by: []
provenance: "啟動書 D12（2026-09-02 拍板 3xxxx、點名六值）；形制承 rev5:ADR 0004（世代首碼＋well-known 尾碼，其母版 rev4:0019）"
tags: [deploy, ports]
rev5_id: "rev5:ADR 0004"
---

## 背景

- 啟動書 D12 拍板 rev6 host 埠世代＝3xxxx，點名六值（32080 UI／32079 API／32443／35432／36379／38025）。
  rev5 compose 三檔實有 **12** 個 host 埠：D12 未點名的另六個＝base-web 直連 22081、example 22089、
  loki 23100、grafana 23000、prometheus 29090、pushgateway 29091。本 ADR 補齊全表，使 compose 三檔改寫有單一依據。
- 世代並存（2026-09-03 本機 `docker ps`／`docker compose ls` 實查）：rev5 stack 常駐 2xxxx（唯讀對照基準、D17）、
  rev4 stack 4xxxx 仍在運行；rev3 曾用 3xxxx（rev5:ADR 0004 載明）但已退役——無 rev3 compose 專案、無 3xxxx 容器。
  本機 3xxxx 現僅 38088／38089 被 docsify-mdviewer（獨立工具）佔用，不在下表十二值內。
- 3xxxx 同樣落在 macOS ephemeral 範圍 49152–65535 之外（rev5:ADR 0004 翻案動機的延續）。

## 決定

**host 埠首碼 2→3、尾碼一律不動**；容器內側照官方預設不動。十二值全表（＝本次 compose 改寫的拍板依據）：

| 服務 | rev5 host | rev6 host | 容器內側 | 檔 |
|---|---|---|---|---|
| front-nginx HTTP | 22080 | **32080** | 80 | dev |
| front-nginx HTTPS | 22443 | **32443** | 443 | dev |
| base-web 直連 | 22081 | **32081** | 80 | dev |
| rust-api | 22079 | **32079** | 8080 | dev |
| mailpit | 28025 | **38025** | 8025 | dev |
| postgres | 25432 | **35432** | 5432 | dev |
| redis | 26379 | **36379** | 6379 | dev |
| loki（profile obs） | 23100 | **33100** | 3100 | dev |
| grafana（profile obs） | 23000 | **33000** | 3000 | dev |
| prometheus（profile metrics） | 29090 | **39090** | 9090 | dev |
| pushgateway（profile metrics） | 29091 | **39091** | 9091 | dev |
| example（獨立專案） | 22089 | **32089** | 80 | example |

配套紀律（承 rev5:ADR 0004、rev6 續行）：

- **尾碼不動**：尾碼＝服務 well-known 語意，首碼純世代碼；全部 host 埠綁 `127.0.0.1`（承 rev5 dev override）。
- **容器內側 port 照官方預設**：配號只動 host 側。
- **ports 真表**＝`docs/generated/reference/ports.md`（由 `tools/docsync` generate 自 compose 三檔重算；波 1 後段落地）。
  本表為拍板依據；真表落地後以真表為準、本 ADR 不再更新鏡像。
- **同機並存的撞名連動（同刀落地）**：compose project `rev6-admin`／`rev6-admin-example`、網路 `rev6_net`、
  image `rev6-admin-rust-api:dev`、container `rev6-admin-example-dev`；observability 的 `compose_project` selector
  （alloy relabel KEEP、grafana alerting／dashboards）同批改 `rev6-admin`——否則 rev6 觀測面會撈到 rev5 stack 的 log。
- **後續動埠**走 errata 紀律（rev6 docsync 落地後的對應命令；落地前＝`grep -rn` 逐處枚舉）。

## 後果

- compose 三檔改 3xxxx；`docker compose config` 實測：dev（含 obs／metrics／jobs profile）11 值＋example 1 值
  全 3xxxx、渲染輸出零 `rev5` 字面、網路 `rev6_net`。
- rev6 無 0004 號 ADR：前代判例一律以 `rev5:ADR 0004` 前綴形引用；裸「ADR 0004」在 rev6 現在式文件＝違規（GT-05）。
- D12 六值不變、只補全；rev3 若日後復活需另擇世代碼，本 ADR 不處理。
- user 2026-09-03 確認十二值對映→accepted。
