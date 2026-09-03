# contracts/fixtures.md — 凍結面（fixtures/）契約

> 檔集＝`specs/001-schema-baseline/fixtures/`；**定稿產物、凍結後永不改寫**、provenance 保存。承 `rev5:contracts/fixtures.md`
> 改座標；rev5 之具名重產例外不承襲（§4）。消費者＝gate1（三 json）、gate2 seed 面（seed.sql）、SC-001 重放驗證。

## 1. 檔集（恰五件）

| 檔 | 內容 | 產製 |
|---|---|---|
| `columns.json` | 實庫欄快照（與 refresh 同構、確定性排序） | 基線實庫照相 |
| `indexes.json` | 索引快照（同上） | 同上 |
| `constraints.json` | 約束快照（同上、含 NOT NULL 逐欄形） | 同上 |
| `seed.sql` | `pg_dump --data-only` normalize 版（normalize 全則＝gates.md §2 seed 面：COPY 段整列排序、setval 保留、pg_dump 噪音四類兩族剝除／正規化） | 基線實庫 dump |
| `provenance.md` | 產製紀錄（見 §3；rev6 自寫、不入雙源互證） | 人寫＋機器值 |

## 2. 產製程序（實作階段執行一次；U2）

1. 一次性 pristine `postgres:18.4-alpine`（獨立 network、零 host 埠、容器名前綴 `rev6-u2-fix*`）以 `rev6-admin-rust-api:dev`
   容器內重放 rev6 `m0001`＋`m0002`（`cargo run --bin migration up`、serial）。
2. 先驗後凍（兩綠才照相落檔）：①實庫 vs data-model §2 欄序全等（`tools/schema-gate.py check --container <容器名>` 之 gate2 欄序面）
   ②照相三 json＋normalize 後 seed.sql 四份 vs `rev5:specs/001-schema-baseline/fixtures/` 同名檔**逐位元全等**（雙源互證；`cmp` 零差異、
   無 normalize 無映射）。任一不全等＝停手升級 user、禁止單源逕行凍結。
3. 照相＋dump→normalize→落 fixtures/ 五件→同 commit 凍結；用畢即拆容器、network 與匿名 PGDATA volume。

## 3. provenance.md 必載欄目（六欄目）

產製日期；容器映像（postgres／rust dev）；m0001／m0002 所在 rust-api commit SHA；rev5 來源座標（凍結 SHA 外層 `7eab28a`／rust-api `92919b9`
之 fixtures 路徑）＋雙源互證紀錄（四檔 `cmp` 零差異）；欄序驗紀錄（gate2 綠）；產製與 normalize 命令形。

## 4. 不變式

- 凍結後任何位元變更＝違憲級（pre-commit 不設專閘、由 review 與 gate1 語意承載：fixtures
  變 → gate1 期望變 → 未登記漂移紅之對偶形現形）。
- 「重產 fixtures」唯一合法路徑＝基線翻案新刀（新 ADR supersedes＋新 fixtures 目錄）。rev5 曾有一次刀內重產具名例外
  （`rev5:ADR 0008`、DB 身分回滾連動 Owner 行）——rev6 fixtures 自始以 Owner 值正規化產製、**不承襲該例外**；其後任何重產仍走本條主文。
- 快照三 json 與 `docs/ops/reference-src/schema-snapshot.json`（refresh 產、跨刀前進）
  職責不同：fixtures＝凍結史料（不動）、reference-src＝現況帳（隨刀 refresh）。
