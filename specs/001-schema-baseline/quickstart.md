# quickstart — 001-schema-baseline 驗證指南

> 端到端驗證場景（US1～US6 對應）；細節指向 data-model.md 與 contracts/、不重複轉錄。
> 全部 rust 操作容器內、serial；host 無 toolchain。rev5（`../fork260509-rev5/`）唯讀、絕不寫入。

## 前置

- `bash tools/bootstrap.sh` 綠（掃描防線就位、rev5 凍結 SHA 斷言）；docker 可用；`/mnt/d` 跑過 compose 後同 shell 先重新 `cd`。
- dev stack 機密已解密（RUNBOOK §15；`migrate` 服務讀 `/run/secrets/database_url`）。
- 映像：`postgres:18.4-alpine`；`rev6-admin-rust-api:dev`（`docker compose -f docker-compose.yml -f docker-compose.dev.yml build migrate`、
  自 `deploy/Dockerfile.rust-api`、首次拉取較久）。
- DB 時區斷言（UTC+0、data-model §4）：對目標庫 `SHOW timezone` ＝ `UTC`。

## A. 拷貝例外自證（US2；ADR-00009 ①）

```sh
strip() { grep -vE '^[[:space:]]*//' "$1" | sed -E 's/[[:space:]]+$//' | sed '/^$/d'; }
R5=../fork260509-rev5/rust-api
diff <(strip $R5/migration/src/m001_baseline_schema.rs) <(strip rust-api/migration/src/m0001_baseline_schema.rs) && echo m0001 OK
diff <(strip $R5/migration/src/m002_baseline_seeds.rs)  <(strip rust-api/migration/src/m0002_baseline_seeds.rs)  && echo m0002 OK
for f in $R5/entity/src/*.rs; do b=$(basename $f); [ $b = lib.rs ] && continue; diff <(strip $f) <(strip rust-api/entity/src/$b) >/dev/null && echo "$b OK" || echo "$b DIFF"; done
python3 tools/docsync lint      # GT-05 掃 tools/ 與子庫 pin 樹：零裸前代編號
```

預期：17 檔全數 OK、lint 0 錯；結果（rc＋檔數）記 commit 訊息與收刀事件。

## B. 基線重放（US1 主流程；dev stack 只起 postgres）

```sh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait postgres
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm migrate      # ＝ migration up
```

預期：`m0001_baseline_schema`／`m0002_baseline_seeds` 兩支 applied、零錯；`seaql_migrations` 記錄名為四碼新名。

## C. pristine 重放＋fixtures 產製＋雙源互證（US1 場景 2～3；contracts/fixtures.md §2）

一次性 `postgres:18.4-alpine`＋獨立 network（容器名前綴 `rev6-u2-fix*`、零 host 埠；命令形載 fixtures/provenance.md）→ 容器內
`cargo run --bin migration up` → `python3 tools/schema-gate.py check --container rev6-u2-fixpg`（gate2 欄序面綠）→ 照相三 json＋
`pg_dump --data-only` normalize → 四份資料檔 `cmp` 對 `../fork260509-rev5/specs/001-schema-baseline/fixtures/` 同名檔：

預期：`cmp` 四檔零差異（雙源互證）；任一不全等＝停手升級 user。落檔五件（provenance 自寫）→ 同 commit 凍結；收尾拆容器、network、匿名 volume。

## D. 三閘全跑（US3）

```sh
python3 tools/schema-gate.py check       # gate1＋gate2＋audit；入口先自證 self-test（dev stack）
python3 tools/schema-gate.py test        # 離線自測＋negative 五類（結構／欄序／seed 值／sequence／假 delta 合成）
python3 tools/schema-gate.py doccheck    # data-model §2／§6／§9 vs fixtures（離線）
```

預期：check rc 0（三閘逐閘一行摘要）；test 全綠；doccheck rc 0。

## E. 演進帳往返（US3 場景 2～4）

1. 對 dev 實庫注入未登記漂移（如 `ALTER TABLE sys_user ADD COLUMN tmp_x text`）→ check rc 1、指名 `columns/sys_user/tmp_x`。
2. 於 `docs/ops/reference-src/schema-evolution.json` 補登記該欄（`knife: "001-schema-baseline"`）→ check rc 0。
3. 改壞登記檔（刪 `date` 欄）→ check rc 2、啟動斷言指名。
4. 還原（撤登記＋`DROP COLUMN`）→ check rc 0。

## F. entity 漂移防線（US4）

```sh
python3 tools/entity-drift-gate.py check     # 快照缺席→rc 2（pre-commit 段判缺席即跳過）；快照就位→綠
python3 tools/entity-drift-gate.py test
```

演練：暫移 `rust-api/entity/src` → 對 rust-api pin bump 的 commit 應被 `entity-drift` 段 rc 2 擋下 → 還原後綠。

## G. DoD 鏈（US5；順序固定）

```sh
python3 tools/docsync refresh        # 需 dev stack postgres；產 schema／accounts 兩快照
python3 tools/docsync generate       # reference/schema.md／accounts.md 首算（GENERATED_FILES 14）
python3 tools/docsync lint           # 全綠（GT-01 零漂移、GT-09 README 樹含兩支工具、GT-12 閘數 12）
git commit（任一）                    # pre-commit 全鏈綠（含 entity-drift 實跑）、耗時 ≤45s 記 perf 事件
```

## 驗收對照

| 場景 | spec 錨 |
|---|---|
| A 自證 17 檔 OK＋lint 綠 | US2、FR-006、SC-001 |
| B 重放零錯、四碼新名 | US1 場景 2、FR-001 |
| C 雙源互證四檔零差異 | US1 場景 3、FR-003、SC-002 |
| D 三閘＋negative 五類 | US3、FR-009、SC-003 |
| E 演進帳往返 | US3 場景 2～4、FR-008、SC-004 |
| F entity 防線演練 | US4、FR-012、SC-005 |
| G DoD 鏈全綠 | US5、FR-013、SC-005／SC-007 |
| 治理：憲法 1.1.0、ADR-00009／00010 accepted、BL-00001／00005、LESSONS 首條 | US6、FR-016～018、SC-006 |
