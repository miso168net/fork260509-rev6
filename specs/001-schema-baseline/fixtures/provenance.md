# fixtures/provenance.md — 凍結面產製紀錄（contracts/fixtures.md §3 六欄目）

> 本目錄五件＝001-schema-baseline 凍結面（rev6 基線＝rev5 終態逐位元承襲；ADR-00010），**凍結後永不改寫**
> （重產唯一合法路徑＝基線翻案新刀、新 ADR supersedes；rev5 之刀內重產具名例外不承襲、contracts/fixtures.md §4）。
> 四份資料檔（三 json＋seed.sql）＝rev6 自己的 pristine 重放萃取；本檔＝rev6 自寫產製紀錄、不入雙源互證。

## 1. 產製日期

2026-09-04（本刀 U2；先驗後凍兩綠同日、隨即照相落檔）。

## 2. 容器映像

- postgres：`postgres:18.4-alpine`（一次性 pristine 容器 `rev6-u2-fixpg`、獨立 network `rev6-u2-fixnet`、零 host 埠、
  拋棄式密碼不落任何檔；`SHOW timezone`＝`UTC`、data-model §4 UTC+0 拍板；用畢即拆＝容器 `-v`＋network＋匿名 PGDATA volume、
  `docker volume ls -f dangling=true` 集合前後全等）
- rust dev（migration 重放）：`rev6-admin-rust-api:dev`（`deploy/Dockerfile.rust-api` dev target；cargo 1.96.1）

## 3. m0001／m0002 所在 rust-api commit SHA

`c6c7d42`（rust-api worktree HEAD、分支 rev6-admin-rust-api；migration 序列＝`m0001_baseline_schema`＋`m0002_baseline_seeds`，
`cargo run --bin migration up` 兩支 applied 零錯；`seaql_migrations` 恰兩列四碼新名、public 16 表＝15 基線表＋seaql_migrations）。

## 4. rev5 來源座標＋雙源互證紀錄

- rev5 來源：`../fork260509-rev5/specs/001-schema-baseline/fixtures/`（rev5 外層凍結 SHA `7eab28a`、rust-api `92919b9`；唯讀）。
- 四檔 `cmp` 逐位元零差異（無 normalize、無映射；provenance 不比）：

  | 檔 | cmp rc | sha256（rev6＝rev5） | bytes |
  |---|---|---|---|
  | columns.json | 0 | `1e28787546719953f8f79872d3cee6cc18c66887c4d8c05c56c98d23e84d3492` | 26735 |
  | indexes.json | 0 | `b7aefe4652d9467dac47747a0a3a827e0d1295b6a31d58c4044f8ee10a4e7a45` | 7559 |
  | constraints.json | 0 | `dc1ce3db5e37df9aa9fb01c03aa8d9e31ddeb8de3920a7bd9c5fb707a6a096d9` | 12553 |
  | seed.sql | 0 | `ce2bced0e1e419064e929bdf158ce463a914376bd7f2d7b2362c715cd2887118` | 35883 |

- 結論：rev6 `m0001`／`m0002` 重放結果＝rev5 終態（169 欄／38 索引／101 約束／266 列 seed＋11 支 setval），
  遷移改四碼名不破全等（`seaql_migrations` COPY 段依產製形剝除；ADR-00008 翻案觸發器實證不成立）。

## 5. 欄序驗紀錄（gate2 綠；`python3 tools/schema-gate.py check --container rev6-u2-fixpg`，rc 0）

```text
[check] ✓ gate1 結構：columns 169／indexes 38／constraints 101 全等（演進帳合成 0 筆）
[check] ✓ gate2 欄序：14 親排表逐位全等（casbin_rule 豁免）
[check] ✓ gate2 seed：normalize 後 486 行逐列零差異（setval 名冊 11 支；runtime-append 收窄 4 表）
[check] ✓ audit archetype：15/15 綠（表清單守門通過）
```

先驗後凍次序＝①候選四檔落本目錄 → ②上列 check 全綠（gate2 欄序面＝vs data-model §2）→ ③§4 四檔 cmp 零差異 → 凍結（本檔同 commit）。

## 6. 產製與 normalize 命令形

```sh
# 一次性 pristine（零 host 埠、獨立 network；<拋棄式>＝執行期亂數、不落檔）
docker network create rev6-u2-fixnet
docker run -d --name rev6-u2-fixpg --network rev6-u2-fixnet \
  -e POSTGRES_USER=soybean -e POSTGRES_PASSWORD=<拋棄式> \
  -e POSTGRES_DB=soybean_admin_rust postgres:18.4-alpine
# 重放（容器內、serial；target／registry 走 compose named volume）
docker run --rm --network rev6-u2-fixnet -v <repo>/rust-api:/app \
  -v rev6-admin_rust_api_cargo_cache:/usr/local/cargo/registry \
  -v rev6-admin_rust_api_target:/app/target \
  -e APP_DATABASE_URL=postgres://soybean:<拋棄式>@rev6-u2-fixpg:5432/soybean_admin_rust \
  --entrypoint cargo rev6-admin-rust-api:dev run --bin migration up
# 照相三 json＝tools/schema-gate.py 之三查詢（SQL_COLUMNS／SQL_INDEXES／SQL_CONSTRAINTS、docsync refresh 同構）
#   ＋確定性排序（columns 依 table,ordinal；indexes／constraints 依 table,name）、json indent 2、檔尾一個換行
# seed.sql＝pg_dump -U soybean -d soybean_admin_rust --data-only（PGTZ=UTC）經產製形 normalize＝恰四項：
#   ①COPY 段內資料列整列排序 ②setval 行原位保留 ③剝 \restrict／\unrestrict token 行 ④剝 seaql_migrations stanza＋COPY 段
#   ★不剝「-- Dumped … version」兩行、不正規化「Owner:」值——該兩類＝gates.md §2 比對期噪音處理（閘兩側各自做）；
#   凍結實檔須與 rev5 逐位元全等、產製形必同 rev5。冪等斷言後落檔。
# 拆除
docker rm -f -v rev6-u2-fixpg && docker network rm rev6-u2-fixnet && docker volume ls -f dangling=true
```
