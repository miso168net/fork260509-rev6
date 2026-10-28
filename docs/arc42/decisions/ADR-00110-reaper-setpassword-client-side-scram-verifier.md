---
id: "ADR-00110"
title: reaper 設密腳本改送客端先算之 SCRAM-SHA-256 驗證碼——明文密碼不進資料庫伺服器
date: 2026-10-28
status: accepted
supersedes: []
superseded_by: []
provenance: "008-audit-settings-pages 收刀前 final holistic review 之 L4-1；user 2026-10-28 兩度裁定：先裁「本刀內修、立 ADR」（原案＝前置 `SET log_min_error_statement = panic`），後依 user 轉來之旁路提醒（該 SET 只擋失敗語句、`log_statement` 為 ddl／all 時成功亦落明文）經拋棄式 PG 18.4 實證後改裁「改送 SCRAM 驗證碼」；被改面＝`deploy/setup-reaper-role.py` 檔頭 ALTER ROLE 之 SQL 形逐字紀律（承 rev5:B-037 U2；該紀律明載改 SQL 形屬行為變更、須走 ADR）；前代無對應：rev4／rev5 之同職腳本皆送明文 ALTER ROLE"
tags: [security, secrets, deploy, reaper]
---

## 背景

- `deploy/setup-reaper-role.py` 以 psql 之 stdin 送 `ALTER ROLE reaper LOGIN PASSWORD '<明文>';`（密碼零進 host process list、零進版本庫）。明文因而進到資料庫伺服器，伺服器端有多條路會把整句記下：
  - `log_min_error_statement`（預設 `error`）：語句以 ERROR 失敗時，出錯之整句以 STATEMENT 行寫入伺服器日誌。失敗路徑實存：m0004 未套用（reaper 角色不存在）、手改之密碼含單引號致語法錯。
  - `log_statement` 為 `ddl` 或 `all`（安全基準常建議開 `ddl`）：ALTER ROLE 屬 DDL，成功亦整句寫入日誌。
  - `log_min_duration_statement`、執行當下之 `pg_stat_activity`，以及 pg_stat_statements、pgaudit 等擴充。
- dev 之 postgres 容器日誌經 `docker logs` 可讀；obs profile 起時另經 alloy 送 Loki。compose 現未設 `log_statement`（預設 `none`）。
- PostgreSQL 之 ALTER ROLE 文件提醒明文密碼可能落伺服器日誌，並指 psql 之 `\password` 可不暴露明文而改密（該命令於客端先算驗證碼）；伺服器收到驗證碼形之字串即原樣存入 `rolpassword`、不再雜湊。
- 腳本檔頭之逐字紀律載明：改 SQL 形屬行為變更，須走 ADR 拍板。

## 決策驅動因子

- 設密之任何路徑（成功與失敗）、任何伺服器日誌設定下，明文密碼都不得落入伺服器日誌及其下游。
- 不得讓密碼改走 argv、環境變數或檔案（承既有密碼紀律）。
- 不依賴連線身分為超級使用者，也不依賴伺服器之日誌設定。
- 可不動 dev 庫而驗證。

## 考慮過的替代案

1. **維持現狀、記為已知態**：缺口留著、靠人照處置。棄（user 2026-10-28 裁定修）。
2. **設密前先查角色存在、不存在即不送**：只擋「角色不存在」一途。棄。
3. **同一工作階段先送 `SET log_min_error_statement = panic;` 再送明文 ALTER**（user 首裁時之原案）：只關失敗語句之記錄。拋棄式 postgres:18.4（`log_statement=ddl`）實證：設密成功時明文照落日誌。棄。
4. **三句 SET（再加 `SET log_statement = 'none'` 與 `SET log_min_duration_statement = -1`）後接明文 ALTER**：同實證下成功、失敗兩路之伺服器日誌皆不見明文；但明文仍進伺服器——執行當下 `pg_stat_activity` 可見、pg_stat_statements／pgaudit 等擴充仍可能記到——且三句 SET 皆須超級使用者。棄（user 2026-10-28 改裁時之次選）。
5. **客端先算 SCRAM-SHA-256 驗證碼、SQL 只帶驗證碼**（選）：明文不離開本行程。

對所選方案跑同一反例（RL-0013；拋棄式 postgres:18.4-alpine、`log_statement=ddl`，以腳本自身之 `alter_role_sql` 實打）：

- 「`log_statement=ddl` 下設密成功」——日誌只見驗證碼、不見明文；`rolcanlogin` 為真；以明文經 scram 登入成功、錯密碼被拒。成立。
- 「角色不存在致 ALTER 失敗」——錯誤訊息與 STATEMENT 行只帶驗證碼、不見明文。成立。
- 「手改密碼含單引號／反斜線／空白等」——驗證碼零單引號、SQL 不破裂；設密成功、經腳本自驗同形（stdin→`read -r`→PGPASSWORD）登入成功、日誌不見明文。成立（舊「已知極限」解除）。
- 「重跑」——每次新鹽、驗證碼不同，登入等效。成立。
- 「驗證碼本身落日誌」——即庫內 `rolpassword` 所存之值；48 位隨機 hex 密碼無從自驗證碼反推。可接受。
- 「非 ASCII 密碼」——libpq 登入時先做 SASLprep 正規化、ASCII 原樣送，腳本不實作 SASLprep ⇒ 前置拒跑；產生器值域＝[0-9a-f]。成立。
- 「空密碼（只有換行之密碼檔）」——舊形由伺服器清密碼；新形會存成空密碼之驗證碼、容許空密碼之客端即可登入 ⇒ 前置拒跑。成立。
- 「雜湊實作錯」——自測以 RFC 7677 範例向量走伺服器端驗證（ClientProof、ServerSignature）相符；拋棄式 PG 實登入相符。成立。

## 決定

1. 設密之 stdin payload 改為 `ALTER ROLE reaper LOGIN PASSWORD '<SCRAM-SHA-256 驗證碼>';`：驗證碼於本機以 Python 標準庫計算（RFC 5802：PBKDF2-HMAC-SHA-256、迭代 4096、鹽 16 位元組亂數＝PostgreSQL 伺服器自算時之預設），形＝`SCRAM-SHA-256$4096:<鹽>$<StoredKey>:<ServerKey>`（後三者 base64）。
2. 密碼剝尾端換行後為空、或含非 ASCII 位元組＝前置拒跑（退出 1、零 docker 調用、訊息不含密碼）。
3. 自驗那一發（stdin→`read -r`→PGPASSWORD，走容器網段 scram）不變。
4. 腳本自測：SQL 形改釘「外框＋驗證碼格式＋以自帶之鹽重算相符＋不含明文」，另立 RFC 7677 已知答案案與兩支前置拒跑案；檔頭逐字紀律改指本 ADR。

## 後果

- 明文密碼不進資料庫伺服器：伺服器日誌（失敗、語句、慢查詢）、`pg_stat_activity` 與擴充皆無從記到明文，與伺服器日誌設定及連線身分無關。
- 伺服器日誌至多見驗證碼（＝`rolpassword` 所存之值）。
- 手改密碼含單引號等特殊字元亦可設定（舊形 SQL 破裂之極限解除）；非 ASCII 與空密碼改為前置拒跑（舊形前者由伺服器正規化後照設、後者由伺服器清密碼後自驗失敗）。
- 代價：腳本多一支雜湊函式；設密 payload 每次不同（鹽隨機），自測改以解析重算比對、不再逐位元組固定。

## 翻案觸發器

- PostgreSQL 預設 SCRAM 迭代數或驗證碼儲存形改變時重審（提高迭代數屬可選加固）。
- 須支援非 ASCII 密碼時重審（須於腳本內實作 SASLprep）。
- reaper 改用 SCRAM 以外之認證方式（如用戶端憑證）時重審。
