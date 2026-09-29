---
id: "ADR-00059"
title: DB 伺服器時區以 compose 明文固定 UTC、全服務容器明設 TZ=UTC、schema-gate check 常設斷言——取代「postgres 容器預設、不另設定」
date: 2026-09-30
status: accepted
supersedes: []
superseded_by: []
provenance: "user 2026-09-29 聲明（系統可能多國使用、DB 應用 UTC+0）與 2026-09-30 逐題裁定（時區盤點第 1／2／13 題）；被取代之款＝specs/001-schema-baseline/data-model.md §4 時區拍板（user 2026-08-05：DB 以 UTC+0 運行——postgres 容器預設、不另設定）；前代出處：rev5:ADR 0006 決定「DB 以 UTC+0 運行」"
tags: [ops, database, timezone, compose, gate]
---

## 背景

「DB 以 UTC+0 運行」是 user 2026-08-05 的拍板（001 刀 data-model §4、承 `rev5:ADR 0006`），其機制為「postgres 容器預設、不另設定」：rev6 postgres 之 `TimeZone`／`log_timezone`＝UTC，來自映像 initdb 依當時容器時區寫入 postgresql.conf 的值；compose、DB URL、migration 皆無釘點。

應用連線不受伺服器預設影響——sqlx-postgres 0.8.6 每條連線以啟動參數送 `TimeZone=UTC`。受伺服器預設左右者＝手動 psql 之時間顯示、pg_dump 文字輸出（備份與 fixtures）、伺服器日誌時間。例：某部署若在 initdb 前於容器設 `TZ=Asia/Tokyo`，postgresql.conf 即寫入該時區，手動 `SELECT now()` 顯示 `+09`、備份演練之逐位元比對假紅。

常設守衛為零：唯一斷言是 001 刀 quickstart 前置之手動 `SHOW timezone`。各服務容器皆未設 `TZ`（預設 UTC）；front-nginx 存取日誌之 `$time_iso8601` 隨容器當地時間。

## 決策驅動因子

- 多國部署時，DB 與日誌時間不隨部署地環境變動。
- UTC 不變式需要機器守衛，不靠人記得。

## 考慮過的替代案

1. **維持容器預設（2026-08-05 原款）**——換環境即可能偏離；否決（user 2026-09-30 裁定）。
2. **只在 DB URL 或連線層設 TimeZone**——應用連線已由驅動固定，psql／pg_dump／伺服器日誌仍不受控；否決。

## 決定

1. `docker-compose.yml` 之 postgres 服務以命令列參數固定 `timezone=UTC`、`log_timezone=UTC`（命令列來源優先於 postgresql.conf；既有資料卷於容器重建後即生效）。
2. compose 各檔所有服務明設環境變數 `TZ=UTC`（`docker-compose.yml` 全部服務、`docker-compose.dev.yml` 之 dev 限定服務、`docker-compose.example.yml`）。
3. `tools/schema-gate.py check` 前置斷言目標庫 `SHOW timezone`＝UTC，不符即 rc 2 fail-loud（附修法提示；一正一反自證）。
4. 取代 specs/001 data-model §4 時區款之「postgres 容器預設、不另設定」；同款「DB 以 UTC+0 運行」「migration 與閘不得依賴 session timezone」不變，其現在式家＝`docs/arc42/08-crosscutting-concepts.md` §8.1。

## 後果

- 正面：換主機、換國家部署皆維持 UTC；偏離時 schema-gate check 當場紅。
- 負面：compose 多一段 postgres 命令列與各服務 `TZ` 環境變數；容器需重建一次。
- 既有資料不變（timestamptz 內部恆以 UTC 儲存）。

## 翻案觸發器

- 出現必須以非 UTC 伺服器時區運行之部署需求。
