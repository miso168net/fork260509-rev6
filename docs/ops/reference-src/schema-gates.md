# schema-gates.md — schema 三閘行為契約（跨刀活體；`tools/schema-gate.py` 的行為權威）

> **本檔＝該契約的跨刀活體家**（ADR-00041）：隨刀前進，現在式面（RUNBOOK／活書／工具）一律引本檔。
> 凍結存證＝`specs/001-schema-baseline/contracts/gates.md`（該刀收刀當下的定稿、不再前進；兩者自 ADR-00041 之日起分岔，分岔由本檔與 git 史解釋）。
> 形制承 ADR-00012（schema 定稿自 spec 目錄抽出至 reference-src 的同型處置）。
> 本檔＝閘的**行為契約**：實作必須滿足、測試自此推導。lineage：spec FR-008～FR-011、
> research R5／R6／R11、data-model §2／§6／§9、ADR-00010（閘契約＝Day-1 受管演進帳）。rev6 差異＝§2 雙源互證取代 rename 血緣、§4 加假 delta 案、§6 加 sequence 對賬面、§7 加 offline 離線對賬腿（BL-00148；ADR-00108 決定 8）。

## 0. 共通紀律

- **退出碼**（沿 repo 工具慣例）：`0` 全綠／`1` 漂移（逐項指名）／`2` 環境或結構異常
  （fixtures 缺、登記檔壞形、庫不可達、比對面為空、目標庫時區非 UTC——附補救提示）／`64` 用法錯誤。
- **self-test 無條件合成**（沿 tools/entity-drift-gate.py 模式）：check 入口先以合成
  fixtures×合成庫照相跑「健康對必綠＋注入假漂移必紅」；self-test 敗＝rc 2 指名比對邏輯壞、
  **不讀任何真檔**（防恆綠假閘）。
- **零容差語意**：一切比對＝全等；「容差」恰兩種合法形＝①演進帳登記（§2）②seed 面之 runtime-append 表級收窄（射程與其補償斷言＝`tools/schema-gate.py` 之 `RUNTIME_APPEND_TABLES` 常數與檔頭 docstring；收窄表的 seed 側必空為硬斷言、配紅綠自證，故非容差洞）。
- 實庫照相＝與 `python3 tools/docsync refresh`（`tools/docsync/snapshot.py`）同構之三查詢（columns／indexes／constraints、
  排除 seaql_migrations、確定性排序）。
- python 標準庫單檔、秒級、自帶 `test` 子命令（pre-commit 條件觸發自測既有接線）；
  「秒級」的量化去處（**自測面**、pre-commit 觸發段）＝`.githooks/pre-commit` 檔頭雙錨 45／90 秒
  （承 `rev5:ADR 0044`）；真庫 check 面（需 stack）於 001 刀 U3 實測、記 perf 事件。

## 1. gate1 結構閘（凍結＋演進帳合成 → 全等）

- **左源（期望）**：`specs/001-schema-baseline/fixtures/{columns,indexes,constraints}.json`
  （凍結面、永不改寫）⊕ `docs/ops/reference-src/schema-evolution.json`（演進面）合成：
  依 entries 逐筆把 add_table／add_column／alter_column／add_index／add_constraint 疊加到
  凍結基底，得「當下期望結構」。
- **右源（實際）**：實庫照相三節。
- **判準**：三節逐列全等。任何未登記差異＝紅（rc 1、指名 section＋table＋名稱＋左右值）；
  登記了但實庫沒有＝同樣紅（登記超前也是漂移）。
- **啟動斷言**：fixtures 三檔在場且形合（list[dict]、鍵集恰合）；演進帳過形檢
  （`docs/ops/reference-src/schema-evolution-contract.md` §2）——任一敗＝rc 2。

## 2. gate2 欄序＋seed 閘（vs 定稿左源）

- **欄序面**：左源＝`docs/ops/reference-src/schema-definition.md` §2 逐表欄序表（解析「| # | 欄 |」表體）；右源＝實庫
  information_schema ordinal。14 親排表逐表逐欄位置全等；**casbin_rule 豁免欄序**（僅
  gate1 結構語意＋audit 歸屬）。演進帳 add_column 之新欄＝接在該表末位（登記時帶
  position、預設殿後）。
- **seed 面**：左源＝`fixtures/seed.sql`；右源＝實庫 `pg_dump --data-only` 經同一
  normalize：**COPY 段內整列排序**（消物理列序假紅）、setval 行保留原位、★剝除／正規化
  pg_dump 噪音**四類、分兩族**（`rev5:ADR 0026`）——
  **非決定性族**（同環境重放即異）：①`\restrict`／`\unrestrict` token 行（pg_dump 18.4
  每次 dump 隨機）②`seaql_migrations` COPY 段（框架帳表、applied_at 逐次重放異；gate1
  照相同義排除前例）——2026-08-05 兩座 pristine 獨立重放位元 diff 實證：**非決定性**恰此
  兩處、266 列與 11 支 setval 行全等（`rev5:` 實證；rev6 雙源互證再驗一次）。
  **環境相依族**（同環境穩定、換環境即異）：③`-- Dumped from database version`／
  `-- Dumped by pg_dump version` 兩行（postgres 或 pg_dump 升版即變）④`; Owner: X`
  註解行的**值**正規化為 `-`（DB 身分變更即變；`rev5:ADR 0008` 那次即為 Owner 行連動重產
  fixtures——rev6 自始正規化、不承襲該重產例外）——★只剝值不剝行：`-- Data for Name: seaql_migrations; …; Owner: x` 亦帶
  Owner，剝整行會炸掉 ② 賴以認出該 stanza 的判頭。
  ★③④ 只把噪音移出**本比對面**、不等於放棄偵測：DB 身分變更改由 **owner 一致性檢查**
  （實庫 dump 原文的 `Owner:` 值集合須恰為單元素且＝連線身分；零命中亦紅、防查空集合
  恆綠）以一筆具名 finding 回報——守門強度不減、假紅消除。
  normalize 後
  **未排序逐列 diff**（含 id 欄）；★**禁全檔排序後雜湊比對**（會同時掩蓋 sequence 落值
  漂移與真差異）。seed 演進（seed_add／seed_update／seed_delete 登記）同樣合成後才比對。
  ★**seed_add 序號合成**（ADR-00085 決定 7）：`pk` 恰單欄 `c` 且 normalize 後文本有
  `SELECT pg_catalog.setval('public.<表>_<c>_seq', N, B);` 行者，期望已發最大值 M＝N（B 真）或 N−1（B 假）；
  新列 id（須為整數、否則 rc 2）大於 M 即把該行推至（新 id, true）、否則不動；多筆依帳序逐筆推進（取大）；
  多欄 pk 或無該序列行之表不推；seed_update／seed_delete 不動序列（刪列不回捲＝同 PG 行為）。
  對應 migration 之收尾契約＝`docs/ops/reference-src/schema-evolution-contract.md` §1。
- **雙源互證（取代 rev5 之 rename 血緣對照）**：rev6 pristine 萃取之四份資料檔（三 json＋normalize 後 seed.sql）vs
  `rev5:specs/001-schema-baseline/fixtures/` 同名檔**逐位元全等**（無 normalize、無映射；provenance 不比）——該場景＝
  fixtures 產製之一次性驗證（U2、紀錄留 provenance.md），非三閘常態比對面；工具**不內建** rename map（research R6）；
  任一不全等＝停手升級 user、禁止單源逕行凍結。

## 3. audit archetype 閘（15 表歸屬逐表驗）

- **左源**：`docs/ops/reference-src/archetype-map.json`（初版＝001 基線 15 表之 §1 轉錄；新表歸屬直接登記本檔、
  `docs/ops/reference-src/schema-definition.md` §1 留 001 基線＝ADR-00087 決定 7）。
- **左源形契約**：`{lineage, usage, tables:[{table, label, active_unique, note}]}`——
  tables Day-1 恰 15 筆（由 `test` 子命令釘死；後續刀隨 add_table 登記成長、常態守門
  ＝實庫表集 vs map 表集全等）；table／label 必填非空（label ∈ 四變體字串）；active_unique＝活性唯一
  **索引名**清單或 null；note＝人讀註記。load 斷言 fail-loud（缺鍵／表重複／label 值域外
  ＝rc 2）。
- **驗則**（對實庫照相逐表執行）：
  - 變體 A：六審計欄在場且型別／可空性合 §I.6（`*_at` timestamptz、created_at NN def
    now；`*_by` bigint 可空）；活性唯一驗則＝map `active_unique` 列出的**索引名**逐支
    在場且定義含 `WHERE (deleted_at IS NULL)`（sys_user 兩支：user_name＋lower(user_email)；
    sys_ip_rule 複合 (wbip_cidr, wbip_type)；PK 總體唯一者豁免、active_unique=null）。
  - 變體 B：禁欄＝**前綴判準**（`rev5:ADR 0016`）——欄名以 `updated_`／`deleted_` 起首即紅
    （防 updated_time／deleted_flag 之類變名欄繞過 append-only 保證）；合法 payload 欄
    走工具內具名豁免清單 `AUDIT_B_EXEMPT`（`{(表, 欄): 理由}`、Day-1 空集、每筆必附
    理由）正規出口；created_at NN。
  - 變體 C：子型規則**硬編碼於工具**（沿 rev4 已驗證先例；map 之 note＝人讀註記、非機器
    判準）——sys_user_role＝零審計欄 join；sys_token＝created_at NN＋created_by NN＋
    status；sys_pwd_custody＝複合 PK (user_id, created_by) 極簡三欄；
    sys_user_email_verify＝user_id PK 衛星五欄。
  - 變體 D：治理欄在場（casbin_rule：protected NN def false＋created_at NN＋created_by
    可空；archive：archived_at NN def now＋archived_by 可空＋archive_reason NN）。
  - `created_by` 可空性顯式驗（不靜默）：期望值＝`docs/ops/reference-src/schema-definition.md`「`*_by` 欄性質判準」逐表
    釋義——NN 恰四表（sys_access_log／sys_token／sys_pwd_custody／sys_user_email_verify）、
    其餘一律可空。
- **表清單守門**：實庫表集 ≠ map 表集＝紅（新表未登記歸屬即攔——歸屬直接登記 map〔`note` 載來源刀與理由〕、
  結構另登演進帳 `add_table`；schema-definition §1 不補＝ADR-00087 決定 7）。

## 3b. 時區前置與全時間欄型別斷言（ADR-00059／ADR-00060）

- **時區前置**（ADR-00059 決定 3）：check 右源照相段最先以 psql（帶 `-X`＝不讀 psqlrc）取兩值、兩段判準——①`SHOW timezone` 非字面 `UTC`（同義名如 `Etc/UTC` 亦不放行）即 rc 2，訊息附現值、期望與修法（compose postgres 命令列、一次性容器附 `-c timezone=UTC`、ALTER DATABASE／ROLE 與目標容器環境之 `PGTZ`／`PGOPTIONS` 排查）②`pg_settings` 之 `TimeZone` source 為 `client`／`session`（值來自連線端：psql 繼承容器環境之 `PGTZ`／`PGOPTIONS`，或連線內 SET）或撈取為空即 rc 2，伺服器側來源（command line、configuration file、database、user 等）放行；兩段任一紅皆零照相零 pg_dump。成功輸出首行「✓ 時區」並附 source。環境面（compose 各服務 `TZ=UTC`、postgres 服務環境零 `PGTZ`／`PGOPTIONS`）由 `bash tools/bootstrap.sh` 體檢斷言（非閘）。
- **全時間欄型別斷言**（ADR-00060 決定 2、憲法 §I.6 時間點欄通則）：以右源 columns 照相判——`timestamp without time zone`（含精度與陣列形）一律 finding（rc 1、名冊亦不能合法化）；`date`（含陣列形）須登記於 `DATE_COLUMNS_REGISTERED`（以 (表, 欄) 為鍵、值＝spec 出處）方過；合法化路徑＝該名冊、非演進帳；成功輸出末行「✓ 時間欄型別」。
- **射程界**：`time`／`interval`、範圍型別（`daterange`／`tsrange` 等）與以 domain 包裝之型別（format_type 只呈現 domain 名）不在斷言射程；名冊內已失效之條目不報紅。

## 4. negative test 義務（SC-003；比對器先自證）

實作 MUST 附注入式負向測試，六類各至少 1 例、全數必紅：
①結構（加欄／改型別；★indexes／constraints 兩節與 columns 節同義務——缺一支、定義異、未登記多一支各 1 例）
②欄序（同表兩欄互換）③seed 值（改一格）④sequence 落值
（setval±1）⑤演進帳合成（登記一筆假 add_column 後合成期望值必與注入後實庫全等、未登記則紅——rev5 終態登記零筆、
合成邏輯首次實證；spec FR-009）⑥**audit 變體驗則面**（右源＝真凍結 fixtures ⊕ 真 archetype-map，離線注入：
型別／可空性／default／欄缺席四腿、A 活性唯一索引的缺席與 `WHERE deleted_at IS NULL` 兩腿、C 子型複合 PK、
D 治理欄、`created_by` 顯式驗——各至少 1 例。★與①～⑤不同：①～⑤注入的是「實庫漂移」、⑥注入的是「驗則會不會抓」，
判準面任一腿被拿掉即須有案轉紅）。連同 self-test 進 `test` 子命令；pre-commit 於工具本體 staged 時自動跑，
凍結面（`fixtures/`、`specs/001-schema-baseline/data-model.md`＝凍結存證）與活體定稿（`docs/ops/reference-src/schema-definition.md`）staged 時亦條件觸發。

## 5. Day-1 營運紀律（隨刀常設）

每支帶 migration 的刀收刀前 MUST：跑 refresh（快照前進）＋ schema-evolution.json 登記
（該刀全部結構／seed 變更；新增 `date` 欄另登記 `DATE_COLUMNS_REGISTERED`）＋check 全綠（時區前置＋三閘＋全時間欄型別斷言）。此條入 `docs/ops/RUNBOOK.md` migration 操作節
（`rev4:` 紅燈裸奔兩刀教訓、`rev5:K1-39`）。

## 6. doccheck 文件面對賬（`rev5:B-010`；三閘之外的離線子命令）

- **對賬面**：`docs/ops/reference-src/schema-definition.md` **§2 逐欄五元組**（ordinal／column／type／NN／default）vs
  `fixtures/columns.json`（casbin_rule 依 §7／欄序豁免名冊不在 §2、自 fixtures 面排除）；
  **§6 索引與約束定義** vs `fixtures/{indexes,constraints}.json`（全表）；**§9 sequences 落值** vs `fixtures/seed.sql` 之 `setval` 行
  （rev6 新增對賬面、取代 rev5 seed-decision.json sequences 節；research R6）。文件單邊被改
  ＝紅、逐項指名——補「§2 型別/NULL/default 三欄與 §6 定義從未進機器比對面」缺口。
- **解析紀律**（兩個已實證陷阱、負向測試釘死）：§2 default 欄「——」＝無 default
  （None、非字面）；§6 條目行可帶尾註（條目正則不錨行尾）。宣告欄數／支數逐表自檢＋
  §6 總計行自檢，防靜默漏列。
- **運行面**：離線零 docker、只讀 repo 檔；退出碼同 §0（0 全等／1 差異／2 環境或結構
  異常）；★**不入 pre-commit 常跑鏈**（護雙錨 45 秒警戒線）——手動／review 輪跑。精確界線：
  schema-gate.py 本體 staged 時，pre-commit 條件觸發的工具自測含「真 repo doccheck 綠」
  一案、仍會帶到（成本併入自測、實測毫秒級）；反面＝單改 `docs/ops/reference-src/schema-definition.md` 不觸發本檢查，
  文件單邊漂移於下一次手動／review 輪才被抓（設計取捨、非缺陷）。

## 7. offline 離線對賬腿（BL-00148；ADR-00108 決定 8；三閘之外的離線子命令）

- **輸入**（純讀檔、零 docker、不讀庫、不收引數）：①delta migration＝rust-api 工作樹 `rust-api/migration/src/` 下檔名形
  `m<四碼>_<小寫蛇形>.rs` 且四碼 ≥ 0003 者（m0003 起之 delta migration；依四碼數值升冪、m0010 起照收；m0001／m0002 基線不在射程）
  ②演進帳 `docs/ops/reference-src/schema-evolution.json`（經 §1 同一啟動斷言）③凍結 fixtures（`specs/001-schema-baseline/fixtures/`
  之 seed.sql 供前值左源與 seed 表集、columns.json 供欄型、constraints.json 供 pk 欄）。
- **判準五款**：
  - ①**解析**：逐檔以字元級掃描器切 Rust 詞素（一般字串之跳脫與 `\` 接換行之續行〔吃掉其後全部空格、`\t`、`\r`、`\n`，含空行〕、
    `r` 前綴 raw 字串〔任意個 `#`〕、raw 識別字 `r#<名>`〔切為識別字詞素〕、行與塊註解、字元字面〔含跳脫形〕與 lifetime〔止於識別字字元；
    二者皆不起字串〕、識別字與標點）。字串、字元字面與註解之外只收 ASCII 識別字、數字、空格／`\t`／`\r`／`\n` 與 Rust 標點，他字元＝rc 2
    fail-closed（rustc 之切法與本掃描器不同、詞素錯位可繞過以詞素形比對之判準），逐途徑：非 ASCII 識別字字元（rustc 依 Unicode XID 收；
    `#[path]` 配 `mod 影;`、`mod shadow影;`）、rustc 視為空白而本掃描器不收者（`\x0b`、`\x0c`、U+0085、U+200E、U+200F、U+2028、U+2029）；
    rustc 亦拒之字元同拒。
    `const <名>: &str = <右式>;` 之右式恰三形——字串字面、檔內 `macro_rules!` 零引數呼叫、`concat!`（項＝前兩形）；`macro_rules!` 恰單規則、
    零引數、展開恰一字面；常數名與 `macro_rules!` 名各須恰一宣告（同名第二次宣告不辨 scope 與 `#[cfg]`、Rust 擇一綁定而本腿無從定其所綁）。
    右式所呼叫之檔內 `macro_rules!` 須定義於檔案頂層且先於該常數（Rust 先查文本作用域、查無才循路徑解析：定義在後、在 inline `mod` 或函式本體內者
    可綁到 `use` 匯入或 `#[macro_export]` 之同名檔外巨集）；檔外巨集之引入途徑拒收——檔案模組宣告 `mod <名>;`（不論屬性與可見性；`<名>` 為
    ASCII 識別字或 raw 識別字 `r#<名>`——非 ASCII 名與 `mod` 後之 rustc 空白由上述字元白名單先 rc 2；其檔之 `macro_rules!` 經 `#[macro_use]`
    延伸至本檔其後文本、後定義遮蔽檔內巨集與內建 `concat!`）、`use` 宣告含識別字 `concat`（含 `as` 改名與清單形；匯入者遮蔽內建 `concat!`）；
    `#[macro_use]`／`#[path]` 不另判（承載者為檔案模組即屬前者、inline `mod` 之內容照掃、`#[macro_use] extern crate` 限 crate 根）。
    遷移二進位所跑之 `MigrationTrait` 實作須即本腿所解析之 head `impl MigrationTrait for Migration {`——四款皆須成立：①head 在檔案頂層、
    全檔 `impl` 詞素恰一＝head ②識別字 `MigrationTrait` 全檔恰一＝head、且頂層有 `use sea_orm_migration::prelude::*;` ③識別字 `Migration`
    全檔恰二＝頂層 `struct Migration` 與 head ④識別字 `cfg`／`cfg_attr` 全檔零（head 與 struct 無條件編譯時，Rust 之衝突實作檢查〔E0119〕
    即排除 crate 內他處〔含本腿不讀之他檔〕之另一實作；`#[cfg]` 互斥則二者並存、遷移二進位可跑他處者）。
    head 內 `async fn up`／`async fn down` 各恰一，本體逐句只認四形：
    `let db = manager.get_connection();`、`expect_rows(db, "…", <SQL>, <整數>, <常數名>).await?;`（rustfmt 折行照收）、
    `db.execute_unprepared(<SQL>).await?;`、`Ok(())`；`<SQL>`＝本檔 `&str` 常數名或字串字面，依頂層 `;` 分句（單引號字串、雙引號識別字、
    `$$` 本體與 SQL 註解內不切；空句略過）。SQL 註解同 PG 切法（`--` 至行尾〔`\n` 或 `\r` 之前〕、`/* */` 可巢狀）切為單一註解詞素，其內之 `;`、
    引號與 `$` 不起作用。未支援之 SQL 詞素（PG 之切法或值語意與本詞素器不同者；其中 `$<標籤>$`、`$$` 緊貼識別字、`E'…'` 三形之引號或
    `$$` 配對錯位即可把頂層 `;` 吞進字串而併句）＝rc 2 fail-closed，逐途徑：`$` 不成 `$$`（標籤式 dollar 引號 `$<標籤>$`、位置參數
    `$<n>`）、`$$` 緊貼識別字字元（ASCII 字母數字底線、非 ASCII 字元）、前綴字串（單引號緊貼識別字字元、或緊貼「識別字字元＋`&`」：
    `E'…'`、`U&'…'`、`B'…'`、`X'…'`、`N'…'` 等）；塊註解未閉合亦 rc 2。
    他形＝rc 2 指名檔、常數名或句首，逐途徑：右式之 `include_str!`、`format!`、引用他常數、函式呼叫、
    `concat!` 含非字面非巨集項；帶引數之 `macro_rules!`；同名第二次宣告（`#[cfg]` 互斥雙宣告、巢狀 `mod` 內、他函式本體內、
    `impl` 關聯常數、非 `&str` 同名常數、`macro_rules!` 同名）；呼叫處不在檔內巨集之文本作用域（定義在後、在 inline `mod` 內、在函式本體內）；
    檔案模組宣告（`#[macro_use]` 形、`#[path]` 配可見性修飾形、無屬性形、名為 raw 識別字 `r#<名>` 形）；`use` 宣告含 `concat`（`as concat` 改名形、清單形）；
    head 之四款違反（①款：限定路徑之 trait `impl sea_orm_migration::MigrationTrait for Migration`、他型別與 inherent 之 impl、inline `mod`
    與函式本體內之 impl、型別位置之 `impl Trait`；②款：`use …::MigrationTrait`〔含不改名之他路徑匯入〕、`use … as MigrationTrait`、
    檔內 `trait MigrationTrait`、缺頂層 prelude 匯入〔換為他 glob、或只在 inline `mod` 內〕；③款：`use … as Migration`、`use …::Migration`、
    `type Migration`、他處第二 `struct Migration`、`struct Migration` 不在頂層；④款：`#[cfg]`、`#[cfg_attr]`、`#![cfg]`、`cfg!`）；本體之 `manager.` 他方法（如 `create_table`）、`db.execute(`／`query_*`、
    檔內他 helper 呼叫；缺 `fn up` 或 `fn down`。
  - ②**分類**：每句恰歸一類——seed DML（`INSERT INTO`／`UPDATE`／`DELETE FROM` 之標的表屬凍結 seed.sql 有 COPY 段之表、且不屬
    `RUNTIME_APPEND_TABLES` 收窄表）、序列（整句恰 `SELECT setval('<序列>', …)`）、權限面（`GRANT`／`REVOKE` 之權限與物件皆單詞、`ON` 後可帶
    `TABLE`／`SEQUENCE`／`SCHEMA`、`TO`／`FROM` 單一角色且句尾無他詞；裸 `CREATE ROLE <角色>` 後接零至多個白名單屬性詞——PG 預設值或減權之
    `NOLOGIN`／`NOSUPERUSER`／`NOCREATEDB`／`NOCREATEROLE`／`NOREPLICATION`／`NOBYPASSRLS`／`INHERIT`／`NOINHERIT`，不分大小寫；
    `DROP ROLE [IF EXISTS]` 單一角色；`DO $$` 包裝恰「`CREATE ROLE` 略過 `duplicate_object`」〔選項詞至少一個、同白名單〕與
    「`DROP ROLE IF EXISTS` 捕 `dependent_objects_still_exist`」兩形）。未分類＝rc 1（`[offline·分類]`），逐途徑：`ALTER`、
    `CREATE TABLE`／`CREATE INDEX`、`TRUNCATE`、他形 `DO` 塊（塊內藏 DML 即屬之）、`ON ALL TABLES IN SCHEMA`、`WITH GRANT OPTION`、
    多詞權限（如 `ALL PRIVILEGES`）、角色成員授予（無 `ON` 之 `GRANT` 形；`CREATE ROLE` 之 `IN ROLE`／`IN GROUP`／`ROLE`／`USER`／`ADMIN`
    子句）、`CREATE ROLE` 選項尾段之他詞素（白名單外屬性詞 `SUPERUSER`／`CREATEDB`／`CREATEROLE`／`REPLICATION`／`BYPASSRLS`／`LOGIN`、
    `WITH`、`SYSID`、`CONNECTION LIMIT`、`[ENCRYPTED] PASSWORD`、`VALID UNTIL`、引號形屬性詞、SQL 註解；`DO` 包裝形零選項亦屬之）、
    他 `SELECT`、對收窄表之 DML、標的不屬凍結 seed 有 COPY 段之表之 DML（逐途徑：凍結 seed 外之表名〔`seaql_migrations` 等〕、schema
    限定名 `public.<表>`〔標的位首詞素為 schema 名〕）。
  - ③**seed DML ↔ 演進帳逐筆**（只 up）：句形恰三種——`INSERT INTO <表> (<欄>, …) VALUES (<字面>, …)[, (…)]`、
    `UPDATE <表> SET <欄> = <字面>[, …] WHERE <條件>[ AND …]`、`DELETE FROM <表> WHERE <條件>[ AND …]`；條件＝`<欄> = <非 NULL 字面>`、
    `<欄> IS NULL` 或至多一個 `(<欄>, …) IN ((<非 NULL 字面>, …), …)`；字面＝整數、單引號字串（`''` 解為一個單引號）、`TRUE`／`FALSE`／`NULL`、`'…'::<型>`
    （型為單詞、大小寫不敏感，須與該欄同族：整數族 bigint／int8／integer／int／int4／smallint／int2、boolean／bool、文字族 text／varchar、timestamptz、jsonb）。表名與欄名之識別字
    同 PG：未加引號者摺小寫、雙引號識別字原樣（`"SYS_MENU"` 非 `sys_menu`）。INSERT 欄清單與 WHERE 須定住該表全部 pk 欄（凍結 constraints.json），元組 `IN` 每一元組展開為一筆；句形超出或 pk
    未定住＝rc 2，逐途徑：`SET`／`VALUES`／`WHERE` 右式非字面（欄參照〔含雙引號識別字 `"…"`——PG 之雙引號為識別字、非字串〕、運算式、轉型字面後再串接）、多詞型轉型（`'…'::character varying` 等）、轉型之型與欄型不同族（`'…'::char` 入文字欄、
    `'…'::timestamp` 入 timestamptz 欄、表外型詞等——PG 依轉型之型解析後指派落欄、落值可≠字面；SET／VALUES、WHERE 與 pk 各位皆核）、INSERT
    欄清單缺 pk 欄、UPDATE／DELETE 之 WHERE 未以 `=` 或元組 `IN` 定住 pk 欄、WHERE 同欄重複、WHERE 第二個元組 `IN`、`<欄> = NULL` 與元組含 `NULL`（SQL 之
    `= NULL` 恆不成立、該列不匹配；比空值須寫 `IS NULL`）、up 方向 seed DML 標的表之後之 SQL 註解。
    演進帳 `seed_*` 登記依 id 序、按 delta 檔序逐支切出與該支展開筆數等量之一段，段內以（kind、表、pk）配對（帳側 pk＝`seed_add` 取 values
    之該表 pk 欄、`seed_update`／`seed_delete` 取 detail.pk 全部欄——其欄集多列非 pk 欄或缺 pk 欄即鍵不合）後比：`seed_add` 之 values
    全欄與 pk 欄名清單（須＝該表 pk 欄）、`seed_update` 之 set 欄集與值；不等、未登之句、多出之登記（含帳總筆數≠展開筆數）＝rc 1
    （`[offline·對賬]`，逐一指名登記 id 或句）。非 `seed_*` 登記不入配對。
  - ④**前值 ↔ 凍結 seed ⊕ 前序配對登記**（只 up 之 UPDATE／DELETE）：左源＝凍結 seed（§2 同一 normalize）依呼叫序逐筆疊上已配對之登記
    （同支與跨支皆累進：同支後序句或後序 delta 改到前序已改之列時，前值即其改後值）；WHERE 所列非 pk 欄（含元組 `IN` 之非 pk 位與
    `IS NULL`）逐欄等於左源該 pk 列之值、不要求列全欄；不等或 pk 不命中（命中＝該表 pk 全部欄皆等、複合 pk 亦然）＝rc 1（`[offline·前值]`）。INSERT 不比前值；down 方向一律只分類。
  - ⑤**權限面只列不對賬**：逐支逐方向列出 `CREATE ROLE`／`GRANT`／`REVOKE`／`DROP ROLE` 句數、角色集與受權物件（物件×權限）；
    不入演進帳、不影響 rc。本腿只保證「語句類別可辨、seed 面與帳一致」；權限真偽由權限測承擔（ADR-00108 決定 7）。
- **值正規化**（③④ 共用；依凍結 columns.json 欄型）：整數族（bigint／integer／smallint）→整數；boolean→布林（COPY `t`／`f`、
  SQL `TRUE`／`FALSE`、JSON 布林同值）；文字族（text、character varying〔含帶長度形〕）→字串（COPY 跳脫還原）；timestamptz→帶時區時刻
  （ISO 與 COPY 形同值、無時區不收）；jsonb→JSON 解析後語意（鍵序與空白不計；布林與數字不同值〔`true`≠`1`、`false`≠`0`〕、數字依
  十進位值比〔同 PG numeric：`1` 與 `1.0` 同值〕）；SQL `NULL`、COPY `\N`、JSON null→空值（不查欄型）。
  `'…'::<型>` 之值先核轉型之型與欄型同族；PG 落值≠此值之字串值拒收（逐途徑：character varying(n) 欄值長度逾 n——PG 於超出部分全為
  空白時靜默截斷、否則報錯；timestamptz 小數秒逾六位——PG 依 rint 進位至微秒、本腿之解析截斷）；他欄型、凍結面無之欄、轉型之型與欄型
  不同族、PG 落值≠此值、值不合欄型＝rc 2 指名。
- **退出碼**：`0` 全綠／`1` finding（`[offline·分類]`／`[offline·對賬]`／`[offline·前值]`，逐項指名）／`2` 結構異常（delta 目錄缺席或
  零支＝比對面為空、解析他形（含字元白名單外之字元與未支援之 SQL 詞素）、句形超出或 pk 未定住、欄型未支援、fixtures 或演進帳缺席壞形）／`64` 帶引數。不設環境跳過分支
  （ADR-00019 決定 3／4：讀面缺席＝rc 2）。
- **射程外**（逐項）：檔內 helper 本體（`expect_rows` 只認其名、不掃其體）；未被 up／down 引用之 `&str` 常數（右式三形照判、SQL 不入分類）；
  `lib.rs` 遷移向量未宣告之孤檔（以檔名形入射程、不比對 `lib.rs`）；crate 根檔（`lib.rs`／`main.rs`）之巨集引入（delta 模組宣告之前之
  `macro_rules!`、`#[macro_use] mod`、`#[macro_use] extern crate`——可遮蔽內建 `concat!`；檔內巨集則由檔內其後之定義遮蔽、不受影響）；
  `lib.rs` 之遷移向量所列型別與 delta 模組宣告之屬性（`#[path]` 改指他檔、`#[cfg]`）；glob 匯入（`use …::*`）引入之巨集；item 位置 `include!`
  所引入之項（不讀其檔）；檔外巨集之展開（屬性巨集〔head 之 `#[async_trait::async_trait]` 照收〕、derive〔`#[derive(DeriveMigrationName)]`〕、
  item 位置之檔外巨集呼叫——不展開）；檔名不合 `m<四碼>_<小寫蛇形>.rs` 者（三碼、五碼、大寫、他副檔名）；
  權限面語句之真偽；`setval` 呼叫內第二引數以後之內容；SQL 註解之內容（切為單一註解詞素、不入判準；註解所在句逐途徑：句首、seed DML
  標的表之前、權限面五形之句內或句尾、`setval` 呼叫第二引數之前或整句之後＝未分類 rc 1；up 方向 seed DML 標的表之後＝句形超出 rc 2；
  `setval` 第二引數以後與 down 方向 seed DML 標的表之後＝不察）；影響列數（由 migration 之
  `expect_rows` 於遷移期斷言）。
- **自證義務**（`test` 子命令；§4 之延伸）：一正（真 repo 綠）多反（改壞 SQL 常數之值、少登一筆、改壞凍結前值、植一句未分類 DDL 各紅；
  合成 m0004 形樣本綠且權限面列出）；判準各為可單獨替換之模組層函式，逐判準以恆放行之樁停用各一案、皆紅（RL-0080）；新增模組層已編譯
  正則者以 `python3 tools/regex-mutants.py run` 之全成分清單為全集、存活者逐支補殺或附等價證明（本腿以字元級掃描器切詞、模組層零新增正則）。
- **掛點**：pre-commit `schema-offline` 段——`rust-api` pin bump、`tools/schema-gate.py` 本體或演進帳 staged 時跑；零 docker、秒級、
  段內零條件判斷。讀面＝rust-api 工作樹 `migration/src/`＋外層演進帳與凍結 fixtures，子庫面屬 (b) 閘面外、無兜底（ADR-00055）。
  需 docker 之 `check` 子命令維持不進常跑鏈（護雙錨 45 秒警戒線；`tools/docsync/tests/test_hook_wiring.py` 釘 pre-commit 非註解行零命中其命令字面）。
- **結構演進之後果**：結構演進之 DDL（`ALTER`、`CREATE TABLE`／`CREATE INDEX` 等；判準②分類為白名單、名單外一律未分類）於本腿判未分類（rc 1）
  ＝帶結構演進之 delta migration 須同刀先擴本腿（分類＋對演進帳結構類 kind〔`add_table`／`add_column`／`alter_column`／`add_index`／
  `add_constraint`〕之對賬）；未擴＝該 migration 一落 rust-api 工作樹，凡 stage 掛點三觸發面之外層 commit 皆被 `schema-offline` 段擋
  （不得 `--no-verify`）。
