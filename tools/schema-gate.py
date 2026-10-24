#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/schema-gate.py — 三閘 schema 驗證閘（001-schema-baseline 基線；Day-1 受管演進帳）

隨遷工具（承 rev5:tools/schema-gate.py 逐字承襲、改 rev6 座標；RULES 名詞段「隨遷工具」）。

子命令：
  check [--container 名] [--user U] [--db D]
        三閘全跑（gate1 結構＋gate2 欄序/seed＋audit archetype）＋時間欄型別斷言；入口無條件
        先跑合成 self-test（敗＝rc 2、不讀任何真檔），右源照相前先斷言目標庫時區＝UTC 且其值來源
        在伺服器側（不符＝rc 2）。預設對 dev stack（compose exec postgres）；
        `--container` 指向一次性 pristine 容器（fixtures 產製／演進帳往返驗證場景）。
  test  跑自帶測試（unittest、離線、零 docker）——含 SC-003 五類 negative 注入
        （結構／欄序／seed 值／sequence 落值／假 delta 登記合成）、seed_add 序號合成與登記檔壞形自測、
        offline 之解析層、一正多反植入案與逐判準停用變異。
  doccheck  活體定稿 docs/ops/reference-src/schema-definition.md 文件面（§2 欄五元組＋§6 索引約束＋§9 sequences 落值；左源座標＝ADR-00087 決定 5）vs 凍結
        fixtures 機器對賬（承 rev5:B-010；離線零 docker、不讀庫；★不入 pre-commit 常跑鏈——
        手動／review 輪跑）。
  offline  零 docker 離線對賬腿（BL-00148；ADR-00108 決定 8；行為權威＝docs/ops/reference-src/schema-gates.md 之
        offline 節）：純讀檔、不讀庫、不收引數、不設環境跳過分支（讀面缺席＝rc 2）。讀面三件——①delta migration＝
        rust-api 工作樹 rust-api/migration/src/ 下檔名 m<四碼>_<小寫蛇形>.rs 且四碼 ≥ 0003 者（依數值升冪；
        m0001／m0002 基線不在射程）②演進帳 docs/ops/reference-src/schema-evolution.json（經 load_ledger、
        啟動斷言照跑）③凍結 fixtures 四件。判準五款：
        ①解析——逐檔以字元級掃描器切 Rust 詞素（一般字串跳脫與 `\\` 接換行之續行〔吃掉其後全部空格、\\t、\\r、\\n，
          含空行〕、r 前綴 raw 字串〔任意個 #〕、raw 識別字 r#<名>〔切為識別字詞素〕、行與塊註解、字元字面〔含跳脫形〕與
          lifetime〔止於識別字字元〕——二者皆不起字串）；字串、字元字面與註解之外只收 ASCII 識別字、數字、空格／\\t／\\r／\\n
          與 Rust 標點（判準①n，fail-closed rc 2——rustc 之切法與本掃描器不同、詞素錯位可繞過以詞素形比對之判準，逐途徑：
          非 ASCII 識別字字元〔rustc 依 Unicode XID 收；#[path] 配 mod 影;、mod shadow影;〕、rustc 視為空白而本掃描器不收者
          〔\\x0b、\\x0c、U+0085、U+200E、U+200F、U+2028、U+2029〕；rustc 亦拒之字元同拒）。
          `const <名>: &str = <右式>;` 之右式恰三形：字串字面、檔內 macro_rules! 零引數呼叫、
          concat!（項＝前兩形）；macro_rules! 單規則、零引數、展開恰一字面；常數名與 macro_rules! 名各須恰一宣告
          （同名第二次宣告不辨 scope 與 #[cfg]，逐途徑：#[cfg] 互斥雙宣告、巢狀 mod 內、他函式本體內、impl 關聯常數、
          非 &str 同名常數、macro_rules! 同名——皆屬他形）；右式所呼叫之檔內巨集須定義於檔案頂層（括號深度 0）且先於該常數
          （判準①k；Rust 先查文本作用域、查無才循路徑解析——定義在後〔配 use 匯入或 #[macro_export] 之同名巨集〕、在 inline mod
          或函式本體內者可綁到檔外定義，皆屬他形）；檔外巨集引入屬他形（判準①j，逐途徑：檔案模組宣告 mod <名>;〔不論屬性與
          可見性；<名> 為 ASCII 識別字或 raw 識別字 r#<名>——非 ASCII 名與 mod 後之 rustc 空白由判準①n 先 rc 2；
          其檔之 macro_rules! 經 #[macro_use] 延伸至本檔其後文本、後定義遮蔽檔內巨集與內建 concat!〕、use 宣告含識別字
          concat〔含 as 改名與清單形；匯入者遮蔽內建 concat!〕；#[macro_use]／#[path] 不另判——承載者為檔案模組即屬前者、
          inline mod 之內容照掃、#[macro_use] extern crate 限 crate 根）；遷移二進位所跑之 MigrationTrait 實作須即本腿所解析之
          head `impl MigrationTrait for Migration {`（判準①m，四款逐途徑：①head 在檔案頂層、全檔 impl 詞素恰一＝head〔拒限定路徑之
          trait、他型別與 inherent 之 impl、inline mod 與函式本體內之 impl、型別位置之 impl Trait〕②識別字 MigrationTrait 全檔恰一＝
          head、且頂層有 use sea_orm_migration::prelude::*;〔拒 use 匯入（含不改名之他路徑匯入）、as 改名、檔內 trait 定義、缺頂層
          prelude 匯入〕③識別字 Migration 全檔恰二＝頂層 struct Migration 與 head〔拒 use … as Migration、use …::Migration、
          type Migration、他處第二 struct Migration、struct Migration 不在頂層〕④識別字 cfg／cfg_attr 全檔零〔#[cfg]、#[cfg_attr]、
          #![cfg]、cfg!——head 與 struct 無條件編譯，Rust 之衝突實作檢查即排除 crate 內他處（含他檔）之另一實作〕；皆屬他形）；
          head 內 `async fn up`／`async fn down` 各恰一，本體逐句只認四形：let db = manager.get_connection()、
          expect_rows(db, "…", <SQL>, <整數>, <常數名>).await?（rustfmt 折行與尾逗號照收）、
          db.execute_unprepared(<SQL>).await?、Ok(())。<SQL>＝本檔 &str 常數名或字串字面，依頂層 `;` 分句
          （單引號字串、雙引號識別字、`$$` 本體與 SQL 註解內不切）；SQL 註解同 PG 切法（`--` 至行尾〔`\\n` 或 `\\r` 之前〕、
          `/* */` 可巢狀）切為單一註解詞素，其內之 `;`、引號與 `$` 不起作用。未支援之 SQL 詞素（PG 之切法或值語意與
          本詞素器不同者；其中 `$<標籤>$`、`$$` 緊貼識別字、E'…' 三形之引號或 `$$` 配對錯位即可把頂層 `;` 吞進字串而
          併句）＝rc 2 fail-closed，逐途徑：`$` 不成 `$$`（標籤式 dollar 引號 `$<標籤>$`、位置參數 `$<n>`）、`$$` 緊貼
          識別字字元（ASCII 字母數字底線、非 ASCII 字元）、前綴字串（單引號緊貼識別字字元、或緊貼「識別字字元＋&」：
          E'…'、U&'…'、B'…'、X'…'、N'…' 等）；塊註解未閉合亦 rc 2。
          他形＝rc 2 指名檔、常數名或句首。
        ②分類——每句恰歸一類：seed DML（INSERT INTO／UPDATE／DELETE FROM 之標的表屬凍結 seed.sql 有 COPY 段之表、
          不屬 RUNTIME_APPEND_TABLES）、序列（整句恰 SELECT setval('<序列>', …)）、權限面（GRANT／REVOKE 之權限
          與物件皆單詞、ON 後可帶 TABLE／SEQUENCE／SCHEMA、TO／FROM 單一角色且句尾無他詞；裸 CREATE ROLE <角色>
          後接零至多個白名單屬性詞〔PG 預設值或減權：NOLOGIN／NOSUPERUSER／NOCREATEDB／NOCREATEROLE／NOREPLICATION／
          NOBYPASSRLS／INHERIT／NOINHERIT；不分大小寫〕；DROP ROLE [IF EXISTS] 單一角色；DO $$ 包裝恰 CREATE ROLE
          〔選項詞至少一個、同白名單〕略過 duplicate_object 與 DROP ROLE IF EXISTS 捕 dependent_objects_still_exist
          兩形）。未分類＝rc 1（[offline·分類]），含：ALTER、CREATE TABLE／INDEX、TRUNCATE、他形 DO 塊（塊內藏 DML
          即屬之）、ON ALL TABLES IN SCHEMA、WITH GRANT OPTION、角色成員授予（無 ON 之 GRANT 形；CREATE ROLE 之
          IN ROLE／IN GROUP／ROLE／USER／ADMIN 子句）、CREATE ROLE 選項尾段之他詞素（白名單外屬性詞 SUPERUSER／
          CREATEDB／CREATEROLE／REPLICATION／BYPASSRLS／LOGIN、WITH、SYSID、CONNECTION LIMIT、[ENCRYPTED] PASSWORD、
          VALID UNTIL、引號形屬性詞、SQL 註解；DO 包裝形零選項亦屬之）、他 SELECT、對收窄表之 DML、標的不屬凍結 seed
          有 COPY 段之表之 DML（判準④b，逐途徑：凍結 seed 外之表名〔seaql_migrations 等〕、schema 限定名 public.<表>〔標的位
          首詞素為 schema 名〕）。
        ③seed DML ↔ 演進帳逐筆（只 up）——句形恰三種：INSERT INTO <表> (<欄>, …) VALUES (<字面>, …)[, (…)]、
          UPDATE <表> SET <欄> = <字面>[, …] WHERE <條件>[ AND …]、DELETE FROM <表> WHERE <條件>[ AND …]；
          條件＝<欄> = <非 NULL 字面>、<欄> IS NULL 或至多一個 (<欄>, …) IN ((<非 NULL 字面>, …), …)；字面＝整數、
          單引號字串（'' 解為一個單引號）、TRUE／FALSE／NULL、'…'::<型>（型為單詞、大小寫不敏感，須與該欄同族＝判準①i：
          整數族 bigint／int8／integer／int／int4／smallint／int2、boolean／bool、文字族 text／varchar、timestamptz、jsonb）。表名與
          欄名之識別字同 PG：未加引號者摺小寫、雙引號識別字原樣（"SYS_MENU" 非 sys_menu）。INSERT 欄清單與 WHERE 須定住該表全部 pk 欄（凍結
          constraints.json），元組 IN 每一元組展開為一筆；句形超出或 pk 未定住＝rc 2，逐途徑：SET／VALUES／WHERE 右式非字面（欄參照
          〔含雙引號識別字 "…"——PG 之雙引號為識別字、非字串〕、運算式、轉型字面後再串接）、
          多詞型轉型（'…'::character varying 等）、轉型之型與欄型不同族（'…'::char 入文字欄、
          '…'::timestamp 入 timestamptz 欄、表外型詞等——PG 依轉型之型解析後指派落欄、落值可≠字面；SET／VALUES、WHERE 與
          pk 各位皆核）、INSERT 欄清單缺 pk 欄、UPDATE／DELETE 之
          WHERE 未以 = 或元組 IN 定住 pk 欄、WHERE 同欄重複、WHERE 第二個元組 IN、<欄> = NULL 與元組含 NULL（SQL 之
          = NULL 恆不成立、該列不匹配；比空值須寫 IS NULL）、up 方向 seed DML 標的表之後之 SQL 註解。演進帳 seed_* 依 id 序、按 delta 檔序逐支切出
          與該支展開筆數等量之一段，段內以（kind、表、pk）配對（帳側 pk＝seed_add 取 values 之該表 pk 欄、
          seed_update／seed_delete 取 detail.pk 全部欄——其欄集多列非 pk 欄或缺 pk 欄即鍵不合）後比：seed_add 之 values 全欄與 pk 欄名清單
          （須＝該表 pk 欄）、seed_update 之 set 欄集與值；不等、未登之句、多出之登記（含帳總筆數≠展開筆數）
          ＝rc 1（[offline·對賬]，逐一指名登記 id 或句）。非 seed_* 登記不入配對。
        ④前值 ↔ 凍結 seed ⊕ 前序配對登記（只 up 之 UPDATE／DELETE）——左源＝凍結 seed（normalize_seed_dump）
          依呼叫序逐筆疊上已配對之登記（apply_seed_entries；同支與跨支皆累進：同支後序句或後序 delta 改到前序已改之
          列時，前值即其改後值）；WHERE 所列非 pk 欄（含元組 IN 之非 pk 位與 IS NULL）逐欄等於左源該 pk 列之值、不要求
          列全欄；不等或 pk 不命中（命中＝該表 pk 全部欄皆等、複合 pk 亦然）＝rc 1（[offline·前值]）。INSERT 不比前值；down 方向一律只分類。
        ⑤權限面結構化列出——逐支逐方向印 CREATE ROLE／GRANT／REVOKE／DROP ROLE 句數、角色集與受權物件
          （物件×權限）；不對賬、不影響 rc。
        值正規化（③④ 共用；依凍結 columns.json 欄型）：整數族（bigint／integer／smallint）→int；boolean→bool
        （COPY t／f、SQL TRUE／FALSE、JSON 布林）；文字族（text、character varying〔含帶長度形〕）→str（COPY
        跳脫還原）；timestamptz→帶時區時刻（ISO 與 COPY 形同值、無時區不收）；jsonb→JSON 解析後語意（鍵序與空白
        不計；布林與數字不同值〔true≠1、false≠0〕、數字依十進位值比〔同 PG numeric：1 與 1.0 同值〕）；
        SQL NULL／COPY \\N／JSON null→None（不查欄型）；'…'::<型> 之值先核轉型之型與欄型同族（判準①i）；PG 落值≠此值之
        字串值拒收（判準①l，逐途徑：character varying(n) 欄值長度逾 n〔PG 於超出部分全為空白時靜默截斷、否則報錯〕、
        timestamptz 小數秒逾六位〔PG 依 rint 進位至微秒、本腿之解析截斷〕）；他欄型、凍結面無之欄、轉型之型與欄型不同族、
        PG 落值≠此值、值不合欄型＝rc 2 指名。
        射程外（逐項）：檔內 helper 本體（expect_rows 只認其名、不掃其體）；未被 up／down 引用之 &str 常數
        （右式三形之判照做、SQL 不入分類）；lib.rs 遷移向量未宣告之孤檔（以檔名形入射程、不比對 lib.rs）；crate 根檔
        （lib.rs／main.rs）之巨集引入（delta 模組宣告之前之 macro_rules!、#[macro_use] mod、#[macro_use] extern crate——可遮蔽
        內建 concat!；檔內巨集則由檔內其後之定義遮蔽、不受影響）；lib.rs 之遷移向量所列型別與 delta 模組宣告之屬性（#[path]
        改指他檔、#[cfg]）；glob 匯入（use …::*）引入之巨集；item 位置 include! 所引入之項（不讀其檔）；檔外巨集之展開（屬性巨集
        〔head 之 #[async_trait::async_trait] 照收〕、derive〔#[derive(DeriveMigrationName)]〕、item 位置之檔外巨集呼叫——不展開）；
        檔名不合 m<四碼>_<小寫蛇形>.rs 者（三碼、五碼、大寫、他副檔名）；權限面真偽（本腿只列；權限之正負向
        ＝ADR-00108 決定 7 之 SET LOCAL ROLE reaper 權限測）；setval 呼叫內第二引數以後之內容；SQL 註解之內容（切為
        單一註解詞素、不入判準；註解所在句逐途徑：句首、seed DML 標的表之前、權限面五形之句內或句尾、setval 呼叫
        第二引數之前或整句之後＝未分類 rc 1；up 方向 seed DML 標的表之後＝句形超出 rc 2；setval 第二引數以後與 down
        方向 seed DML 標的表之後＝不察）；影響列數（由 migration 之 expect_rows 於遷移期斷言）。

契約＝docs/ops/reference-src/schema-gates.md（行為）＋`docs/ops/reference-src/schema-evolution-contract.md`
（登記檔形＋啟動斷言七條）＋`docs/ops/reference-src/schema-fixtures-contract.md`（凍結面）。零容差語意：一切比對＝全等，
「容差」合法形恰兩種＝①演進帳登記（docs/ops/reference-src/schema-evolution.json）
②rev5:B-065 表級收窄（RUNTIME_APPEND_TABLES 寫死本檔、配 seed 必空斷言；見下 gate2 seed 段）；
除此之外一律全等。

三閘：
  gate1 結構——左源＝specs/001-schema-baseline/fixtures/{columns,indexes,constraints}.json
        （凍結面）⊕ 演進帳合成期望；右源＝實庫照相三節（與 python3 tools/docsync refresh
        同構三查詢、排除 seaql_migrations、確定性排序）；三節逐列全等，未登記差異＝紅
        （指名 section／table／名稱／左右值）、登記超前（登記了實庫沒有）同紅。
  gate2 欄序——左源＝schema-definition.md §2 逐表欄序（解析「| # | 欄 |」表體；ADR-00087）＋演進帳
        add_column 接末位；右源＝實庫 ordinal；14 親排表逐位全等、casbin_rule 豁免。
  gate2 seed——左源＝fixtures/seed.sql ⊕ seed_* 演進合成；右源＝實庫 pg_dump --data-only；
        兩側同一 normalize（COPY 段整列排序＋setval 原位＋剝除 \\restrict／\\unrestrict
        token 行＋seaql_migrations COPY 段＋pg_dump 版本兩行＋Owner 值正規化）後
        **未排序逐列 diff**（含 id 欄）；★禁全檔排序後雜湊（會掩蓋 sequence 落值漂移與
        真差異）。sequence 名冊＝凍結 fixtures/seed.sql 之 setval 行（RE_SETVAL 解析、勿手抄
        名字面；rev5 另讀其 seed 決策 json、rev6 不搬該檔——名冊與凍結 seed 同源）。
        ★seed_add 序號合成（GR9；ADR-00085 決定 7）：pk 恰單欄且有該表 `<表>_<pk>_seq` 之
        setval 行者，新 id 高於期望已發最大值（is_called 真取 N、假取 N−1）即把期望推至
        (新 id, true)、否則不動（登記值非整數＝rc 2）；多筆依帳序逐筆取大；seed_update／
        seed_delete 不動序列（刪列不回捲）——對應 seed_add migration 之收尾契約 MUST
        `setval(<序列>, GREATEST(<新 id>, last_value), true)`（is_called 真之序列上兩者等價；
        未收尾＝實庫序列留舊值、gate2 指名該序列紅）。
        ★rev5:B-065 表級收窄：RUNTIME_APPEND_TABLES 五表（session_event／sys_login_attempt／
        sys_token／sys_operation_log／sys_access_log——sys_operation_log 於 rev5:004-ip-trust-anchor 入集、
        sys_access_log 依 ADR-00100 決定 8 入集）
        兩側再剝其 COPY 資料列（段首欄名行照比＝結構漂移仍紅）＋其 sequence 之
        setval 值正規化為佔位（行存在仍比、整行消失＝紅），並另斷言 seed 側此類表
        必 0 列——runtime 寫入不再紅、往 seed 塞稽核列照樣紅。
  audit archetype——左源＝docs/ops/reference-src/archetype-map.json（15 表歸屬、形契約
        gates.md §3）；對實庫照相逐表驗四變體規則（C／D 子型硬編碼於工具、map note＝
        人讀註記）；created_by 可空性顯式驗（NN 恰四表）；表清單守門（實庫表集≠map
        表集＝紅）。

三閘之外（check 同跑）：
  時區前置（ADR-00059 決定 3）——右源照相段最先查目標庫 SHOW timezone（字面≠UTC＝rc 2），緊接查
        pg_settings 之 TimeZone source（client／session＝值來自連線端而非伺服器——目標容器環境之
        PGTZ／PGOPTIONS 或 psqlrc 之 SET timezone——＝rc 2）；皆附補救、不往下照相比對。psql 撈取
        不帶 PGTZ 且帶 -X（不讀 psqlrc）；compose 各服務 TZ＝UTC 與 postgres 服務環境零
        PGTZ／PGOPTIONS 另由 tools/bootstrap.sh 體檢斷言。
  時間欄型別（憲法 §I.6 時間點欄通則、ADR-00060 決定 2）——對實庫照相之全庫欄（不限審計欄）：
        無時區 timestamp 一律紅、無豁免出口；date 須列於 DATE_COLUMNS_REGISTERED 名冊
        （{(表, 欄): spec 出處}、現為空）方過——合法化路徑＝名冊、非演進帳；time／interval
        類不在射程。

退出碼：0 全綠／1 漂移（逐項指名）／2 環境或結構異常（fixtures 缺、登記檔壞形、庫不可達、
目標庫時區非 UTC 或其值來自連線端、比對面為空、self-test 敗——附補救提示）／64 用法錯誤（usage 走 stderr）。
offline 同四碼：1＝[offline·分類]／[offline·對賬]／[offline·前值] finding；2＝delta 目錄缺席或零支（比對面為空）、
解析他形（含字元白名單外之字元與未支援之 SQL 詞素）、句形超出或 pk 未定住、欄型未支援、fixtures 或演進帳缺席壞形（含 GateError）；64＝帶引數。
只跑唯讀查詢與 pg_dump、絕不寫庫；pg_dump 帶 PGTZ=UTC（閘不依賴 session timezone；UTC 慣例
之現在式家＝docs/arc42/08-crosscutting-concepts.md §8.1、ADR-00059）；輸出不含 deploy 機密值
（seed 定稿值〔含 PHC 常數〕本在版控、gate2 seed diff 可回顯——非洩密面）。

雙源互證（rev6 pristine 萃取之 fixtures vs rev5 同名檔逐位元全等；`docs/ops/reference-src/schema-gates.md` §2）＝
fixtures 產製之一次性驗證（紀錄住 fixtures/provenance.md）、非三閘常態比對面；工具不內建
rename 映射（rev5 有、供其 rev4 血緣對賬；rev6 無此場景、research R6）。
"""

import collections
import contextlib
import datetime
import decimal
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIXTURES_DIR = os.path.join("specs", "001-schema-baseline", "fixtures")
DATA_MODEL = os.path.join("docs", "ops", "reference-src", "schema-definition.md")   # 人寫定稿左源（跨刀活體；BL-00022）
LEDGER = os.path.join("docs", "ops", "reference-src", "schema-evolution.json")
ARCHETYPE_MAP = os.path.join("docs", "ops", "reference-src", "archetype-map.json")

DB_USER = "soybean"
DB_NAME = "soybean_admin_rust"
COMPOSE_EXEC = ["docker", "compose", "-f", "docker-compose.yml",
                "-f", "docker-compose.dev.yml", "exec", "-T"]

# 三節列鍵集（與 docsync refresh 快照同構；fixtures 形斷言用）
COL_KEYS = frozenset({"table", "column", "ordinal", "type", "nullable", "default"})
DEF_KEYS = frozenset({"table", "name", "definition"})

# 登記檔（`docs/ops/reference-src/schema-evolution-contract.md`）：kind 枚舉恰八值；id／knife／date 格式
KINDS = ("add_table", "add_column", "alter_column", "add_index", "add_constraint",
         "seed_add", "seed_update", "seed_delete")
# 斷言⑦（rev5:B-006；`docs/ops/reference-src/schema-evolution-contract.md` §2 第 7 條）：kind×detail 必備鍵表——八 kind
# 逐 kind 定形、load_ledger 啟動即驗（原合成期 _need 臨時檢查升格為啟動斷言；_need 留作
# 直呼合成路徑的兜底）。需比對面在場的值域斷言（pk 欄名 ⊆ COPY 欄集、同名 index/
# constraint 重複登記攔）歸合成期驗、同樣 GateError→rc 2。
DETAIL_KEYS = {
    "add_table": ("columns",),
    "add_column": ("column", "type", "nullable"),
    "alter_column": ("column",),
    "add_index": ("name", "definition"),
    "add_constraint": ("name", "definition"),
    "seed_add": ("pk", "values"),
    "seed_update": ("pk", "set"),
    "seed_delete": ("pk",),
}
RE_ENTRY_ID = re.compile(r"^E-\d{3}$")
RE_KNIFE = re.compile(r"^\d{3}-[a-z0-9-]+$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# archetype 四變體字串（gates.md §3 label 值域；C 子型明細走 note 人讀）
LABELS = ("A 業務全六欄", "B append-only", "C join·狀態機", "D 治理")
# created_by NN 恰四表（data-model §1「*_by 欄性質判準」：domain 欄、非審計欄）；其餘一律可空
CREATED_BY_NN = ("sys_access_log", "sys_token", "sys_pwd_custody", "sys_user_email_verify")
AUDIT_SIX = ("created_at", "created_by", "updated_at", "updated_by",
             "deleted_at", "deleted_by")
# 變體 B 禁欄判準＝前綴通配（rev5:ADR 0016、gates.md §3）：updated_／deleted_ 起首即紅——
# 防變名欄（updated_time／deleted_flag 之類）繞過 append-only 保證（憲法 §I.6）。
AUDIT_B_FORBIDDEN_PREFIXES = ("updated_", "deleted_")
# 具名豁免清單（rev5:ADR 0016 正規出口；沿 CREATED_BY_NN 具名慣例）：合法 payload 欄
# （例：日後稽核表 updated_fields jsonb 記變更欄集）加列於此、Day-1 空集。
# 格式＝{(表名, 欄名): "理由"}；加列程序＝隨引入該欄之刀同 commit 加列＋附理由字串
# （誤攔勿就地退回具名判準——等於白拍 rev5:ADR 0016），review 輪隨審計欄語意演進複核。
AUDIT_B_EXEMPT = {}
ORDER_EXEMPT = ("casbin_rule",)   # 委派建表、欄序不入親排（data-model §7）

# ── rev5:B-065 runtime-append 表級收窄（rev5 2026-08-11 拍板「表級收窄寫死工具內」形、rev6 承襲）──
# gate2 seed 對下列表改比「結構＋setval 存在性」：兩側 normalize 後剝其 COPY 資料列
# （段首欄名行照比＝結構漂移仍紅）、其 sequence 之 setval **值**正規化為佔位（行本身
# 保留——整行消失＝紅）；另斷言 seed 側（凍結 seed ⊕ 演進合成）此類表必 0 列（非 0＝
# 具名 finding 紅）。動機（rev5 實證）：這些表 runtime 寫入即紅，曾迫使每次走查後全套
# 收尾（TRUNCATE＋setval——rev5:003 全刀付出三次收尾成本、rev5:L-015 實暴一次髒庫連鎖）。
# 射程＝恰五表：rev5:003 實痛三表（該刀走查收尾清的正是那三表三 sequence）＋
# ★sys_operation_log（rev5:004-ip-trust-anchor T037／其 spec FR-042 **明列的排程工作項**）＋
# ★sys_access_log（ADR-00100 決定 8）。
# ★sys_operation_log 入集的時點理由：該表在 rev5:004 之前是**零寫入者**，該刀的 IP 規則四寫端使它取得
# rev5 首個寫入者——寫端一落列，gate2 對它的 seed 逐列 diff 即紅，那是**預期的**、
# 不是回歸；入集是 spec 排定的處置，不得當 bug 追。rev6 資料形狀同 rev5、server 刀後即
# 需要同一收窄（research R6：保留）。
# ★sys_access_log 入集的理由（ADR-00100 決定 8；論證形同 sys_operation_log 入集）：存取日誌之決定形＝每筆
# 已登入請求一列＝runtime 寫入、凍結 seed 該段恆零列（setval (1, false)）——runtime 落列即令 gate2 對它的
# seed 逐列 diff 紅，屬預期、非回歸；值欄＝凍結 columns.json 該表 id 欄之 nextval default。
# ★sys_ip_rule **MUST NOT 入集**：它是 archetype 變體 A 業務表、列內容即真 seed 面
# （zero-seed 亦是一種 seed 面宣告），收窄它＝管理面誤寫一列規則不再被閘看見。
# 該表的 runtime 測試殘留一律走走查還原紀律（TRUNCATE＋setval 收尾；RL-0031）。
# ★sys_user_role 絕不入集——archetype 同標變體 C 但屬**有 seed 列的 join 表**（種子
# 使用者的角色掛載），收窄它＝真 seed 面被弱化。其餘變體 B/C 零 seed 表不入集：sys_pwd_custody（007 刀起
# 設密寫端落經手列、業務碼不刪；走查殘列由 tools/walkthrough-baseline.py 之還原清理面收，gate2 對它照逐列比＝
# 未清即紅）與 sys_user_email_verify（零寫入者）。擴集＝本常數加一行：鍵欄（表名）之「seed 必空」斷言
# 對新成員自動生效；值欄（sequence 名）由凍結 columns.json 之 nextval default 機器
# 對賬（TestConstantsPinned 值欄對賬測——值欄作用面＝setval 佔位、與鍵欄作用面＝剝列
# 互相獨立，手抄錯名＝非收窄表的 setval 落值守門靜默弱化，該測指名紅、勿臆測手抄）。
# ★安全邊界紀律：清單寫死本檔、絕不取自呼叫端——另一候選「runtime-tolerant 呼叫旗標」
# 已於 rev5 被否決：旗標＝呼叫端控制安全邊界（任何呼叫都能帶旗標把守門面調弱、閘形同
# 虛設）。收窄語意權威＝rev5 隨 rev5:B-065 所立之 ADR；rev6 承襲點＝research R6、本註解為
# 工具面記載。
RUNTIME_APPEND_TABLES = {
    "session_event": "session_event_id_seq",
    "sys_access_log": "sys_access_log_id_seq",
    "sys_login_attempt": "sys_login_attempt_id_seq",
    "sys_operation_log": "sys_operation_log_id_seq",
    "sys_token": "sys_token_id_seq",
}

# ── 照相三查詢（與 python3 tools/docsync refresh 同構 SQL；SELECT only）───
#    同構的機器載體＝tools/docsync/tests/test_snapshot.py 之同構案（importlib 依路徑載入本檔、
#    對 SQL_COLUMNS／SQL_INDEXES／SQL_CONSTRAINTS 與 tools/docsync/snapshot.py 同名常數逐一比對）；
#    改動本三常數任一支 MUST 同步 snapshot.py 側，否則該案即紅（gate1 照相 SQL 與快照 SQL 不得分家）。
#    rev5 側由 schema-gate 自帶的 TestSnapshotIsomorphism 承載、隨舊工具不承襲（research R6）。
_JSON_WRAP = "SELECT COALESCE(json_agg(t), '[]'::json) FROM ({}) t"
SQL_COLUMNS = _JSON_WRAP.format(
    'SELECT c.table_name AS "table", c.column_name AS "column",'
    ' c.ordinal_position AS "ordinal", format_type(a.atttypid, a.atttypmod) AS "type",'
    " c.is_nullable = 'YES' AS \"nullable\", c.column_default AS \"default\""
    " FROM information_schema.columns c"
    " JOIN pg_class cl ON cl.relname = c.table_name"
    " JOIN pg_namespace ns ON ns.oid = cl.relnamespace AND ns.nspname = c.table_schema"
    " JOIN pg_attribute a ON a.attrelid = cl.oid AND a.attname = c.column_name"
    " WHERE c.table_schema = 'public' AND c.table_name <> 'seaql_migrations'"
    " ORDER BY c.table_name, c.ordinal_position")
SQL_INDEXES = _JSON_WRAP.format(
    'SELECT tablename AS "table", indexname AS "name", indexdef AS "definition"'
    " FROM pg_indexes WHERE schemaname = 'public' AND tablename <> 'seaql_migrations'"
    " ORDER BY tablename, indexname")
SQL_CONSTRAINTS = _JSON_WRAP.format(
    'SELECT rel.relname AS "table", con.conname AS "name",'
    ' pg_get_constraintdef(con.oid) AS "definition"'
    " FROM pg_constraint con"
    " JOIN pg_class rel ON rel.oid = con.conrelid"
    " JOIN pg_namespace ns ON ns.oid = rel.relnamespace"
    " WHERE ns.nspname = 'public' AND rel.relname <> 'seaql_migrations'"
    " ORDER BY rel.relname, con.conname")

# ── 時區前置（ADR-00059 決定 3）：右源照相段最先查目標庫時區。psql 撈取不帶 PGTZ（只 pg_dump
#    帶）且帶 -X（不讀 psqlrc）。判準①＝SHOW timezone 與期望值字面全等；判準②緊接其後＝該值之來源
#    （pg_settings 之 source）不得在連線端——SHOW 讀的是 session 生效值：psql 在容器內繼承容器環境，
#    環境帶 PGTZ 或 PGOPTIONS（-c timezone=…）時連線啟動參數即以連線端值覆蓋（source＝client），
#    psqlrc 之 SET timezone 則 source＝session；兩者皆使伺服器非 UTC 而判準①恆綠。伺服器側來源
#    （命令列、設定檔、ALTER DATABASE／ALTER ROLE、預設值）放行、值由判準①判。環境面（compose 各服務
#    TZ＝UTC、postgres 服務環境零 PGTZ／PGOPTIONS）另由 tools/bootstrap.sh 體檢斷言。
SQL_TIMEZONE = "SHOW timezone"
EXPECTED_TIMEZONE = "UTC"
SQL_TIMEZONE_SOURCE = "SELECT source FROM pg_settings WHERE name = 'TimeZone'"
CLIENT_TIMEZONE_SOURCES = ("client", "session")


class GateError(Exception):
    """環境／結構異常（fixtures 缺、登記檔壞形、庫不可達、目標庫時區非 UTC 或其值來自連線端、
    比對面為空）——rc 2 fail-loud。"""


# ---------------------------------------------------------------------------
# DB 存取（helper 單支帶 parse 旗標；--container 指定＝docker exec、預設＝compose exec）
# ---------------------------------------------------------------------------

def _db_base(container):
    if container:
        return ["docker", "exec", "-i", container]
    return list(COMPOSE_EXEC) + ["postgres"]


def _run_docker(cmd, run):
    """docker 子行程統一入口：docker 執行不起來（OSError；不在 PATH／CLI 缺）＝
    環境異常 GateError→rc 2、非漂移——與 docsync refresh 之 psql 撈取同慣例
    （承 rev5 之 docsync 前身 psql_fetch／rev5:tools/wire-schema.py extract_schema）。"""
    try:
        return run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    except OSError as ex:
        raise GateError(f"無法執行 docker（{ex}）——三閘需 docker 可用；dev stack 啟動："
                        "docker compose -f docker-compose.yml -f docker-compose.dev.yml "
                        "up -d --wait postgres；一次性容器場景→確認 --container 名"
                        ) from None


def psql(sql, parse=False, container=None, user=DB_USER, db=DB_NAME, run=subprocess.run):
    """docker（compose）exec psql 唯讀撈取；parse=True 時 stdout 以 JSON 解析。
    psql 失敗（含 docker 不可執行）或 JSON 壞形皆屬環境異常（GateError→rc 2）。"""
    # -X＝不讀 psqlrc：其中之 SET 會改 session 設定、時區前置即讀到 session 值
    cmd = _db_base(container) + ["psql", "-X", "-U", user, "-d", db,
                                 "-tA", "-v", "ON_ERROR_STOP=1", "-c", sql]
    r = _run_docker(cmd, run)
    if r.returncode != 0:
        raise GateError(f"psql 失敗（rc={r.returncode}）：{r.stderr.strip()[:300]}"
                        "——補救：dev stack 未起→docker compose -f docker-compose.yml "
                        "-f docker-compose.dev.yml up -d --wait postgres；"
                        "一次性容器場景→確認 --container 名")
    out = r.stdout.strip()
    if not parse:
        return out
    try:
        return json.loads(out or "[]")
    except json.JSONDecodeError as ex:
        raise GateError(f"psql 輸出非合法 JSON：{ex}；前 200 字＝{out[:200]}")


def timezone_problem(value):
    """時區前置判準（ADR-00059 決定 3）：SHOW timezone 值字面＝UTC → None；否則回可操作之失敗
    訊息（現值、期望、修法）——cmd_check 轉 GateError→rc 2、不往下照相比對。"""
    if value == EXPECTED_TIMEZONE:
        return None
    return (f"目標庫時區不符：SHOW timezone＝{value!r}、期望＝{EXPECTED_TIMEZONE!r}"
            "（ADR-00059：DB 伺服器時區固定 UTC；psql 顯示、pg_dump 文字輸出與伺服器日誌皆依此）"
            "——補救：dev stack＝確認 docker-compose.yml 之 postgres 服務 command 帶 "
            "`-c timezone=UTC -c log_timezone=UTC`，再以 docker compose -f docker-compose.yml "
            "-f docker-compose.dev.yml up -d --wait postgres 重建該容器；一次性容器場景"
            "（--container）＝起容器時於映像名後附 `-c timezone=UTC`；命令列已帶仍不符＝查 "
            "ALTER DATABASE／ALTER ROLE 之 timezone 設定，以及目標容器環境之 PGTZ／PGOPTIONS"
            "（連線端覆蓋：psql 繼承容器環境變數，本判準先於來源判準、故先紅在此）")


def timezone_source_problem(source):
    """時區來源判準（ADR-00059 決定 3 之判準前提）：pg_settings 之 TimeZone source 為伺服器側 → None；
    為連線端（CLIENT_TIMEZONE_SOURCES）或撈取為空 → 回可操作之失敗訊息（現 source、意義、修法）——
    cmd_check 轉 GateError→rc 2、不往下照相比對。"""
    if not source:
        return ("目標庫時區來源撈取為空（pg_settings 無 TimeZone 列？）——時區前置判準失準、不往下比對"
                "（ADR-00059）")
    if source not in CLIENT_TIMEZONE_SOURCES:
        return None
    return (f"目標庫時區來源不符：pg_settings 之 TimeZone source＝{source!r}——值來自連線端而非伺服器"
            "（client＝連線啟動參數：psql 在容器內繼承容器環境之 PGTZ／PGOPTIONS；session＝連線內 SET："
            "psqlrc 之 SET timezone），SHOW timezone 讀到的不是伺服器時區、時區前置判準失效"
            "（ADR-00059：DB 伺服器時區固定 UTC）——補救：移除目標容器環境之 PGTZ／PGOPTIONS"
            "（dev stack＝docker-compose*.yml 之 postgres 服務 environment；一次性容器"
            "（--container）＝docker run 之 -e）或 psqlrc 之 SET timezone，再重跑")


def pg_dump_data(container=None, user=DB_USER, db=DB_NAME, run=subprocess.run):
    """實庫 pg_dump --data-only（右源原文）；PGTZ=UTC＝閘不依賴 session timezone。"""
    base = _db_base(container)
    # -e 必掛 exec 子命令之後（兩形皆然）；插 docker compose 頂層＝unknown shorthand flag
    i = base.index("exec") + 1
    cmd = base[:i] + ["-e", "PGTZ=UTC"] + base[i:] + \
        ["pg_dump", "-U", user, "-d", db, "--data-only"]
    r = _run_docker(cmd, run)
    if r.returncode != 0:
        raise GateError(f"pg_dump 失敗（rc={r.returncode}）：{r.stderr.strip()[:300]}")
    return r.stdout


# ---------------------------------------------------------------------------
# 左源載入（啟動斷言全部 fail-loud；「列缺欄」類壞形前置斷言、勿裸 KeyError）
# ---------------------------------------------------------------------------

def _load_json(path, what):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise GateError(f"{what} 缺席（{path}）") from None
    except json.JSONDecodeError as ex:
        raise GateError(f"{what} JSON 壞形：{ex}") from None


def _assert_detail(e):
    """斷言⑦：kind×detail 必備鍵（表＝DETAIL_KEYS）＋逐 kind 值形檢——任一敗＝GateError
    （呼叫端轉 rc 2）；`docs/ops/reference-src/schema-evolution-contract.md` §2 第 7 條。"""
    kind, d, eid = e["kind"], e["detail"], e["id"]
    for k in DETAIL_KEYS[kind]:
        if k not in d:
            raise GateError(f"登記檔啟動斷言⑦敗：{eid}（{kind}）detail 缺必備鍵 {k}"
                            f"（必備鍵表＝{'＋'.join(DETAIL_KEYS[kind])}）")

    def _nonempty_str(key):
        if not isinstance(d[key], str) or not d[key]:
            raise GateError(f"登記檔啟動斷言⑦敗：{eid}（{kind}）detail.{key} 須為非空字串"
                            f"（得 {d[key]!r}）")

    if kind == "add_table":
        cols = d["columns"]
        if not isinstance(cols, list) or not cols:
            raise GateError(f"登記檔啟動斷言⑦敗：{eid} add_table columns 須為全欄非空清單")
        for i, c in enumerate(cols):
            if not isinstance(c, dict) or any(k not in c for k in
                                              ("column", "type", "nullable")):
                raise GateError(f"登記檔啟動斷言⑦敗：{eid} add_table columns[{i}] 須為含"
                                " column＋type＋nullable 之物件")
    elif kind == "add_column":
        _nonempty_str("column")
        _nonempty_str("type")
        if not isinstance(d["nullable"], bool):
            raise GateError(f"登記檔啟動斷言⑦敗：{eid} add_column nullable 須為布林"
                            f"（得 {d['nullable']!r}）")
    elif kind == "alter_column":
        _nonempty_str("column")
        if not any(k in d for k in ("type", "nullable", "default")):
            raise GateError(f"登記檔啟動斷言⑦敗：{eid} alter_column 須帶 type／nullable"
                            "／default 至少一項（零改動項＝空登記、必屬筆誤）")
    elif kind in ("add_index", "add_constraint"):
        _nonempty_str("name")
        _nonempty_str("definition")
    elif kind == "seed_add":
        if not isinstance(d["pk"], list) or not d["pk"] \
                or any(not isinstance(x, str) or not x for x in d["pk"]):
            raise GateError(f"登記檔啟動斷言⑦敗：{eid} seed_add pk 須為主鍵欄名非空清單")
        if not isinstance(d["values"], dict) or not d["values"]:
            raise GateError(f"登記檔啟動斷言⑦敗：{eid} seed_add values 須為物件"
                            "（欄:值 全欄）")
    else:   # seed_update／seed_delete
        if not isinstance(d["pk"], dict) or not d["pk"]:
            raise GateError(f"登記檔啟動斷言⑦敗：{eid}（{kind}）pk 須為非空物件（欄:值）")
        if kind == "seed_update" and (not isinstance(d["set"], dict) or not d["set"]):
            raise GateError(f"登記檔啟動斷言⑦敗：{eid} seed_update set 須為非空物件"
                            "（欄:值）")


def load_ledger(root):
    """演進登記檔＋啟動斷言七條（`docs/ops/reference-src/schema-evolution-contract.md` §2）；任一敗＝GateError。"""
    path = os.path.join(root, LEDGER)
    data = _load_json(path, "演進登記檔 schema-evolution.json")
    # ① 頂層鍵恰集＋型別
    if not isinstance(data, dict) or set(data) != {"next_id", "entries"}:
        raise GateError("登記檔啟動斷言①敗：頂層鍵須恰為 {next_id, entries}"
                        f"（得 {sorted(data) if isinstance(data, dict) else type(data).__name__}）")
    if not isinstance(data["next_id"], int) or isinstance(data["next_id"], bool) \
            or data["next_id"] < 1:
        raise GateError(f"登記檔啟動斷言①敗：next_id 須正整數（得 {data['next_id']!r}）")
    if not isinstance(data["entries"], list):
        raise GateError("登記檔啟動斷言①敗：entries 須為 list")
    nums = []
    for i, e in enumerate(data["entries"]):
        tag = f"entries[{i}]"
        if not isinstance(e, dict):
            raise GateError(f"登記檔啟動斷言②敗：{tag} 非物件")
        # ② 欄位齊全非空
        for k in ("id", "knife", "kind", "table", "detail", "date"):
            if k not in e or e[k] in (None, "", [], {}):
                raise GateError(f"登記檔啟動斷言②敗：{tag} 欄位 {k} 缺席或空"
                                f"（id={e.get('id', '?')}）")
        # ③ id 格式；⑤ kind 枚舉＋date 格式；④ knife 格式；⑥ drop_* 不存在
        if not isinstance(e["id"], str) or not RE_ENTRY_ID.match(e["id"]):
            raise GateError(f"登記檔啟動斷言③敗：{tag} id 格式非 E-NNN（得 {e['id']!r}）")
        if not isinstance(e["knife"], str) or not RE_KNIFE.match(e["knife"]):
            raise GateError(f"登記檔啟動斷言④敗：{e['id']} knife（來源刀編號）格式非 "
                            f"NNN-slug（得 {e['knife']!r}）")
        if isinstance(e["kind"], str) and e["kind"].startswith("drop_"):
            raise GateError(f"登記檔啟動斷言⑥敗：{e['id']} kind={e['kind']}——刪除性演進"
                            "屬拍板級、走新 ADR＋基線翻案，不入登記檔")
        if e["kind"] not in KINDS:
            raise GateError(f"登記檔啟動斷言⑤敗：{e['id']} kind={e['kind']!r} 不在枚舉"
                            f"恰八值 {KINDS}")
        if not isinstance(e["date"], str) or not RE_DATE.match(e["date"]):
            raise GateError(f"登記檔啟動斷言⑤敗：{e['id']} date 格式非 YYYY-MM-DD"
                            f"（得 {e['date']!r}）")
        if not isinstance(e["detail"], dict):
            raise GateError(f"登記檔啟動斷言②敗：{e['id']} detail 須為物件")
        # ⑦ kind×detail 必備鍵表＋值形（rev5:B-006）
        _assert_detail(e)
        nums.append(int(e["id"][2:]))
    # ③ 全檔唯一、遞增、永不回收（next_id＝最大號＋1）
    if len(set(nums)) != len(nums):
        raise GateError("登記檔啟動斷言③敗：id 重複")
    if nums != sorted(nums) or any(b <= a for a, b in zip(nums, nums[1:])):
        raise GateError(f"登記檔啟動斷言③敗：id 非遞增（序列 {nums}）")
    if nums and data["next_id"] != nums[-1] + 1:
        raise GateError(f"登記檔啟動斷言③敗：next_id={data['next_id']} ≠ 最大號＋1"
                        f"（={nums[-1] + 1}）")
    return data


def _assert_rows(rows, keys, what):
    if not isinstance(rows, list) or not rows:
        raise GateError(f"{what} 非非空 list——比對面為空、不得靜默判綠")
    for i, r in enumerate(rows):
        if not isinstance(r, dict) or set(r) != keys:
            raise GateError(f"{what} 第 {i} 列形壞：鍵集須恰為 {sorted(keys)}"
                            f"（得 {sorted(r) if isinstance(r, dict) else type(r).__name__}）")
    return rows


def load_fixtures(root):
    """凍結面四件（三 json＋seed.sql）；缺席＝GateError 附補救提示（rc 2）。"""
    remedy = ("——補救：fixtures＝凍結面（specs/001-schema-baseline/fixtures/、"
              "`docs/ops/reference-src/schema-fixtures-contract.md`）；未產製→依 §2 產製程序（pristine 重放＋三驗後照相"
              "落檔）；已凍結卻缺檔＝repo 受損，自 git 還原、絕不重產")
    fx = {}
    for name, keys in (("columns", COL_KEYS), ("indexes", DEF_KEYS),
                       ("constraints", DEF_KEYS)):
        path = os.path.join(root, FIXTURES_DIR, f"{name}.json")
        try:
            rows = _load_json(path, f"fixtures/{name}.json")
        except GateError as ex:
            raise GateError(str(ex) + remedy) from None
        fx[name] = _assert_rows(rows, keys, f"fixtures/{name}.json")
    seed_path = os.path.join(root, FIXTURES_DIR, "seed.sql")
    try:
        with open(seed_path, encoding="utf-8") as fh:
            fx["seed"] = fh.read()
    except FileNotFoundError:
        raise GateError(f"fixtures/seed.sql 缺席（{seed_path}）{remedy}") from None
    if not fx["seed"].strip():
        raise GateError("fixtures/seed.sql 內容為空——比對面為空、不得靜默判綠" + remedy)
    return fx


def load_archetype_map(root):
    """archetype-map 載入＋形斷言（gates.md §3 形契約；缺鍵／表重複／label 值域外＝rc 2）。"""
    data = _load_json(os.path.join(root, ARCHETYPE_MAP), "archetype-map.json")
    if not isinstance(data, dict) or set(data) != {"lineage", "usage", "tables"}:
        raise GateError("archetype-map 形壞：頂層鍵須恰為 {lineage, usage, tables}")
    tables = data["tables"]
    if not isinstance(tables, list) or not tables:
        raise GateError("archetype-map 形壞：tables 非非空 list")
    seen = set()
    for i, row in enumerate(tables):
        if not isinstance(row, dict) or set(row) != {"table", "label",
                                                     "active_unique", "note"}:
            raise GateError(f"archetype-map tables[{i}] 形壞：鍵集須恰為 "
                            "{table, label, active_unique, note}")
        if not isinstance(row["table"], str) or not row["table"]:
            raise GateError(f"archetype-map tables[{i}]：table 必填非空")
        if row["table"] in seen:
            raise GateError(f"archetype-map：表 {row['table']} 重複登記")
        seen.add(row["table"])
        if row["label"] not in LABELS:
            raise GateError(f"archetype-map：{row['table']} label={row['label']!r} "
                            f"值域外（四變體字串＝{LABELS}）")
        au = row["active_unique"]
        if au is not None and (not isinstance(au, list) or not au
                               or any(not isinstance(x, str) or not x for x in au)):
            raise GateError(f"archetype-map：{row['table']} active_unique 須為索引名"
                            "非空清單或 null")
        if not isinstance(row["note"], str):
            raise GateError(f"archetype-map：{row['table']} note 須為字串（人讀註記）")
    return tables


def parse_data_model_order(text):
    """data-model §2 →「表→定稿欄名序」＝parse_data_model_five 的投影（單一解析源：
    §2 版面一變只改一處，防 gate2 欄序面與 doccheck 面各自漂移；自檢同在該支）。"""
    return {t: [r[1] for r in rows]
            for t, rows in parse_data_model_five(text).items()}


def load_data_model_order(root):
    path = os.path.join(root, DATA_MODEL)
    try:
        with open(path, encoding="utf-8") as fh:
            return parse_data_model_order(fh.read())
    except FileNotFoundError:
        raise GateError(f"data-model.md 缺席（{path}）") from None


# ---------------------------------------------------------------------------
# doccheck（承 rev5:B-010）：data-model 文件面 vs 凍結 fixtures 機器對賬（離線、零 docker）；
# rev6 新增 §9 sequences 落值對賬面（取代 rev5 之 seed 決策 json sequences 節；research R6）
# ---------------------------------------------------------------------------

RE_DM6_HEAD = re.compile(r"^(索引|約束)（(\d+)）：")
# ★條目正則不錨行尾：§6 條目行可帶尾註（實例＝sys_operation_log_real_ip_not_null 行帶
# 「（★§4 定稿差異新增、rev4 無）」）——嚴格行尾錨會少數一條（rev5:B-010 已實證陷阱②）。
RE_DM6_ITEM = re.compile(r"^- `([^`]+)`：`([^`]+)`")


def parse_data_model_five(text):
    """data-model §2 →「表→[(ordinal, column, type, nullable, default)…]」；§2 唯一
    解析源（gate2 欄序面＝parse_data_model_order 投影本支；本支五元組、doccheck 消費）；
    宣告欄數 vs 解析列數逐表自檢（防靜默漏列）。
    ★default 欄「——」＝無 default（None）——取字面比對即全表假紅（rev5:B-010 已實證陷阱①）。"""
    m = re.search(r"^## 2\. .*?$(.*?)^## 3\. ", text, re.M | re.S)
    if not m:
        raise GateError("data-model §2 段落定位失敗（## 2. … ## 3. 邊界不在）")
    tables, declared, cur = {}, {}, None
    for line in m.group(1).splitlines():
        h = re.match(r"^### (\w+)（(\d+) 欄", line)
        if h:
            cur = h.group(1)
            declared[cur] = int(h.group(2))
            tables[cur] = []
            continue
        if cur and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 5 and cells[0].isdigit():
                tables[cur].append((int(cells[0]), cells[1], cells[2],
                                    cells[3] != "NN",
                                    None if cells[4] in ("——", "") else cells[4]))
    for t, n in declared.items():
        if len(tables[t]) != n:
            raise GateError(f"data-model §2 解析自檢敗：{t} 宣告 {n} 欄、解析得 "
                            f"{len(tables[t])}")
    if len(tables) != 14:
        raise GateError(f"schema-definition §2 解析自檢敗：期望 14 親排表、解析得 {len(tables)}")
    return tables


def parse_data_model_defs(text):
    """data-model §6 →（索引 {(表,名):定義}, 約束 {(表,名):定義}）；宣告支數 vs 解析數
    逐表逐節自檢＋總計行自檢（防尾註陷阱之外的任何靜默漏列）。"""
    m = re.search(r"^## 6\. .*?$(.*?)^## 7\. ", text, re.M | re.S)
    if not m:
        raise GateError("data-model §6 段落定位失敗（## 6. … ## 7. 邊界不在）")
    body = m.group(1)
    tm = re.search(r"總計：索引 (\d+) 支、約束 (\d+) 條", body)
    if not tm:
        raise GateError("data-model §6 總計行（索引 N 支、約束 N 條）定位失敗")
    idx, con = {}, {}
    cur, mode, want, seen = None, None, 0, 0

    def _selfcheck():
        if mode is not None and seen != want:
            raise GateError(f"data-model §6 解析自檢敗：{cur} {mode}宣告 {want} 條、"
                            f"解析得 {seen}")

    for ln in body.splitlines():
        h = re.match(r"^### (\w+)\s*$", ln)
        if h:
            _selfcheck()
            cur, mode, want, seen = h.group(1), None, 0, 0
            continue
        hm = RE_DM6_HEAD.match(ln)
        if hm:
            _selfcheck()
            mode, want, seen = hm.group(1), int(hm.group(2)), 0
            continue
        im = RE_DM6_ITEM.match(ln)
        if im:
            if not cur or not mode:
                raise GateError(f"data-model §6 條目行落在表／節之外：{ln[:60]}")
            store = idx if mode == "索引" else con
            key = (cur, im.group(1))
            if key in store:
                raise GateError(f"data-model §6 重複條目：{key}")
            store[key] = im.group(2)
            seen += 1
    _selfcheck()
    if (len(idx), len(con)) != (int(tm.group(1)), int(tm.group(2))):
        raise GateError(f"data-model §6 解析自檢敗：總計宣告索引 {tm.group(1)}／約束 "
                        f"{tm.group(2)}、解析得 {len(idx)}／{len(con)}")
    return idx, con


def doccheck_findings(five, idx_doc, con_doc, fixtures):
    """rev5:B-010 對賬核心（純函數）：§2 五元組 vs fixtures/columns（ORDER_EXEMPT 表依
    data-model §7 不在 §2、自 fixtures 面排除——勿誤報）；§6 vs fixtures/{indexes,
    constraints}（全表、含 casbin_rule）。文件單邊被改＝紅、逐項指名。"""
    fnd = []
    fx_five = {}
    for r in fixtures["columns"]:
        if r["table"] in ORDER_EXEMPT:
            continue
        fx_five.setdefault(r["table"], {})[r["column"]] = (
            r["ordinal"], r["type"], r["nullable"], r["default"])
    doc_five = {t: {r[1]: (r[0], r[2], r[3], r[4]) for r in rows}
                for t, rows in five.items()}
    for t in sorted(set(doc_five) - set(fx_five)):
        fnd.append(f"[doccheck·§2] {t}｜文件有、fixtures 無")
    for t in sorted(set(fx_five) - set(doc_five)):
        fnd.append(f"[doccheck·§2] {t}｜fixtures 有、文件無")
    for t in sorted(set(doc_five) & set(fx_five)):
        am, bm = doc_five[t], fx_five[t]
        for c in sorted(set(am) - set(bm)):
            fnd.append(f"[doccheck·§2] {t}.{c}｜文件有、fixtures 無")
        for c in sorted(set(bm) - set(am)):
            fnd.append(f"[doccheck·§2] {t}.{c}｜fixtures 有、文件無")
        for c in sorted(set(am) & set(bm)):
            if am[c] != bm[c]:
                fnd.append(f"[doccheck·§2] {t}.{c}｜(ordinal,type,nullable,default) "
                           f"文件={am[c]}、fixtures={bm[c]}")
    for what, doc in (("indexes", idx_doc), ("constraints", con_doc)):
        fx = {(r["table"], r["name"]): r["definition"] for r in fixtures[what]}
        for k in sorted(set(doc) - set(fx)):
            fnd.append(f"[doccheck·§6] {what}/{k[0]}/{k[1]}｜文件有、fixtures 無")
        for k in sorted(set(fx) - set(doc)):
            fnd.append(f"[doccheck·§6] {what}/{k[0]}/{k[1]}｜fixtures 有、文件無")
        for k in sorted(set(doc) & set(fx)):
            if doc[k] != fx[k]:
                fnd.append(f"[doccheck·§6] {what}/{k[0]}/{k[1]}｜定義異：文件="
                           f"{doc[k]!r}、fixtures={fx[k]!r}")
    return fnd


# §9 sequences 落值表（rev6 新增對賬面）：具名列「| <seq> | <落值> |」＋殿後一列
# 「| 其餘 N 支（<表>／<表>…） | 未動用（不 setval） |」——未動用＝pg_dump 之 setval(…, 1, false)。
RE_DM9_ROW = re.compile(r"^\| (\w+_seq) \| (\d+) \|")
RE_DM9_REST = re.compile(r"^\| 其餘 (\d+) 支（([^）]*)） \| 未動用（不 setval） \|")


def parse_data_model_sequences(text):
    """data-model §9 →（{具名 sequence: 落值}, [其餘未動用之表名…]）；「其餘 N 支」宣告數
    vs 解析數自檢（防靜默漏列）。其餘者以表名列出、其 sequence 名＝<表>_id_seq（pg serial
    慣例、與 fixtures/columns.json 之 nextval default 同形）。"""
    m = re.search(r"^## 9\. .*?$(.*?)^## 10\. ", text, re.M | re.S)
    if not m:
        raise GateError("data-model §9 段落定位失敗（## 9. … ## 10. 邊界不在）")
    named, rest, rest_declared = {}, [], None
    for ln in m.group(1).splitlines():
        rm = RE_DM9_ROW.match(ln)
        if rm:
            if rm.group(1) in named:
                raise GateError(f"data-model §9 重複條目：{rm.group(1)}")
            named[rm.group(1)] = int(rm.group(2))
            continue
        xm = RE_DM9_REST.match(ln)
        if xm:
            if rest_declared is not None:
                raise GateError("data-model §9「其餘 N 支」列重複")
            rest_declared = int(xm.group(1))
            rest = [t.strip() for t in xm.group(2).split("／") if t.strip()]
    if not named:
        raise GateError("data-model §9 零具名 sequence 落值列——比對面為空、不得靜默判綠")
    if rest_declared is None:
        raise GateError("data-model §9「其餘 N 支（…） | 未動用（不 setval）」列缺席")
    if len(rest) != rest_declared:
        raise GateError(f"data-model §9 解析自檢敗：其餘宣告 {rest_declared} 支、解析得 "
                        f"{len(rest)}")
    overlap = sorted({f"{t}_id_seq" for t in rest} & set(named))
    if overlap:
        raise GateError(f"data-model §9 具名列與其餘列重疊：{overlap}")
    return named, rest


def doccheck_sequence_findings(named, rest, seed_text):
    """§9 sequences vs fixtures/seed.sql setval 行：具名落值＝setval(名, 落值, true) 全等；
    其餘＝setval(名, 1, false)；名冊雙向全等（文件有 seed 無／seed 有文件無皆紅）。
    seed 側零 setval 行＝比對面為空 GateError（不得靜默判綠）。"""
    doc = {seq: (val, "true") for seq, val in named.items()}
    doc.update({f"{t}_id_seq": (1, "false") for t in rest})
    seed = {}
    for ln in seed_text.splitlines():
        sm = RE_SETVAL.match(ln)
        if sm:
            seed[sm.group(1)] = (int(sm.group(2)), sm.group(3))
    if not seed:
        raise GateError("fixtures/seed.sql 零 setval 行——§9 比對面為空、不得靜默判綠")
    fnd = []
    for seq in sorted(set(doc) - set(seed)):
        fnd.append(f"[doccheck·§9] {seq}｜文件有、fixtures 無")
    for seq in sorted(set(seed) - set(doc)):
        fnd.append(f"[doccheck·§9] {seq}｜fixtures 有、文件無")
    for seq in sorted(set(doc) & set(seed)):
        if doc[seq] != seed[seq]:
            fnd.append(f"[doccheck·§9] {seq}｜(落值, is_called) 文件={doc[seq]}、"
                       f"fixtures={seed[seq]}")
    return fnd


# ---------------------------------------------------------------------------
# gate1：凍結 ⊕ 演進帳合成 → 三節逐列全等
# ---------------------------------------------------------------------------

def _need(detail, keys, eid):
    for k in keys:
        if k not in detail:
            raise GateError(f"演進帳 {eid} detail 缺鍵 {k}——不足以機器合成期望值")


def synth_expected(fixtures, entries):
    """凍結三節 ⊕ 結構性 entries（seed_* 歸 gate2 seed 面）→ 期望三節（確定性排序）。"""
    cols = [dict(r) for r in fixtures["columns"]]
    idxs = [dict(r) for r in fixtures["indexes"]]
    cons = [dict(r) for r in fixtures["constraints"]]
    for e in entries:
        kind, t, d, eid = e["kind"], e["table"], e["detail"], e["id"]
        if kind == "add_table":
            _need(d, ("columns",), eid)
            if not isinstance(d["columns"], list) or not d["columns"]:
                raise GateError(f"演進帳 {eid} add_table columns 須為全欄非空清單")
            if any(c["table"] == t for c in cols):
                raise GateError(f"演進帳 {eid} add_table：表 {t} 已存在於期望面")
            for i, c in enumerate(d["columns"], 1):
                if not isinstance(c, dict):
                    raise GateError(f"演進帳 {eid} add_table columns[{i - 1}] 非物件")
                _need(c, ("column", "type", "nullable"), eid)
                cols.append({"table": t, "column": c["column"], "ordinal": i,
                             "type": c["type"], "nullable": c["nullable"],
                             "default": c.get("default")})
        elif kind == "add_column":
            _need(d, ("column", "type", "nullable"), eid)
            if d.get("position", "末位") != "末位":
                raise GateError(f"演進帳 {eid} add_column position={d['position']!r} "
                                "未支援——契約＝接末位（gates.md §2）")
            existing = [c for c in cols if c["table"] == t]
            if not existing:
                raise GateError(f"演進帳 {eid} add_column：表 {t} 不在期望面")
            cols.append({"table": t, "column": d["column"],
                         "ordinal": max(c["ordinal"] for c in existing) + 1,
                         "type": d["type"], "nullable": d["nullable"],
                         "default": d.get("default")})
        elif kind == "alter_column":
            _need(d, ("column",), eid)
            hit = [c for c in cols if c["table"] == t and c["column"] == d["column"]]
            if len(hit) != 1:
                raise GateError(f"演進帳 {eid} alter_column：{t}.{d['column']} 在期望面"
                                f"命中 {len(hit)} 筆（須恰 1）")
            for k in ("type", "nullable", "default"):
                if k in d:
                    hit[0][k] = d[k]
        elif kind == "add_index":
            _need(d, ("name", "definition"), eid)
            if any(r["table"] == t and r["name"] == d["name"] for r in idxs):
                raise GateError(f"演進帳 {eid} add_index：{t}/{d['name']} 同名 index 重複"
                                "登記——比對面 (table,name) 鍵合併會吞漂移、不得靜默")
            idxs.append({"table": t, "name": d["name"], "definition": d["definition"]})
        elif kind == "add_constraint":
            _need(d, ("name", "definition"), eid)
            if any(r["table"] == t and r["name"] == d["name"] for r in cons):
                raise GateError(f"演進帳 {eid} add_constraint：{t}/{d['name']} 同名 "
                                "constraint 重複登記——比對面鍵合併會吞漂移、不得靜默")
            cons.append({"table": t, "name": d["name"], "definition": d["definition"]})
        # seed_add／seed_update／seed_delete：gate2 seed 面合成（apply_seed_entries）
    return {
        "columns": sorted(cols, key=lambda r: (r["table"], r["ordinal"])),
        "indexes": sorted(idxs, key=lambda r: (r["table"], r["name"])),
        "constraints": sorted(cons, key=lambda r: (r["table"], r["name"])),
    }


def compare_structure(expected, actual):
    """三節逐列全等；未登記差異／登記超前逐項指名（section＋table＋名稱＋左右值）。"""
    findings = []
    exp_c = {(c["table"], c["column"]):
             (c["ordinal"], c["type"], c["nullable"], c["default"])
             for c in expected["columns"]}
    act_c = {(c["table"], c["column"]):
             (c["ordinal"], c["type"], c["nullable"], c["default"])
             for c in actual["columns"]}
    for k in sorted(set(exp_c) - set(act_c)):
        findings.append(f"[gate1] columns/{k[0]}/{k[1]}｜期望有、實庫無"
                        f"（左={exp_c[k]}、右=∅）——登記超前也是漂移")
    for k in sorted(set(act_c) - set(exp_c)):
        findings.append(f"[gate1] columns/{k[0]}/{k[1]}｜實庫有、期望無"
                        f"（左=∅、右={act_c[k]}）——未登記漂移（合法化唯一路徑＝"
                        "schema-evolution.json 登記）")
    for k in sorted(set(exp_c) & set(act_c)):
        if exp_c[k] != act_c[k]:
            findings.append(f"[gate1] columns/{k[0]}/{k[1]}｜(ordinal,type,nullable,"
                            f"default) 左（期望）={exp_c[k]}、右（實庫）={act_c[k]}")
    for section in ("indexes", "constraints"):
        exp = {(r["table"], r["name"]): r["definition"] for r in expected[section]}
        act = {(r["table"], r["name"]): r["definition"] for r in actual[section]}
        for k in sorted(set(exp) - set(act)):
            findings.append(f"[gate1] {section}/{k[0]}/{k[1]}｜期望有、實庫無"
                            f"（左={exp[k]!r}）")
        for k in sorted(set(act) - set(exp)):
            findings.append(f"[gate1] {section}/{k[0]}/{k[1]}｜實庫有、期望無"
                            f"（右={act[k]!r}）——未登記漂移")
        for k in sorted(set(exp) & set(act)):
            if exp[k] != act[k]:
                findings.append(f"[gate1] {section}/{k[0]}/{k[1]}｜定義異：左（期望）="
                                f"{exp[k]!r}、右（實庫）={act[k]!r}")
    return findings


# ---------------------------------------------------------------------------
# gate2 欄序：data-model §2 ＋ add_column 末位 vs 實庫 ordinal
# ---------------------------------------------------------------------------

def compare_column_order(dm_order, entries, actual_cols):
    """14 親排表逐位全等；casbin_rule 豁免；演進帳 add_column 依 id 序接末位。"""
    findings = []
    expected = {t: list(names) for t, names in dm_order.items()}
    for e in entries:
        if e["kind"] == "add_column" and e["table"] in expected:
            expected[e["table"]].append(e["detail"]["column"])
    by_table = {}
    for c in actual_cols:
        by_table.setdefault(c["table"], []).append(c)
    for t in sorted(expected):
        if t in ORDER_EXEMPT:
            continue
        if t not in by_table:
            findings.append(f"[gate2·欄序] {t}｜表不在實庫")
            continue
        act = [c["column"] for c in sorted(by_table[t], key=lambda c: c["ordinal"])]
        exp = expected[t]
        if act != exp:
            for i in range(max(len(act), len(exp))):
                a = act[i] if i < len(act) else "∅"
                x = exp[i] if i < len(exp) else "∅"
                if a != x:
                    findings.append(f"[gate2·欄序] {t} 第 {i + 1} 位｜期望={x}、實庫={a}")
    return findings


# ---------------------------------------------------------------------------
# gate2 seed：pg_dump normalize（兩側同則）＋ seed_* 合成 ＋ 未排序逐列 diff
# ---------------------------------------------------------------------------

RE_COPY_HDR = re.compile(r"^COPY public\.(\w+) \(([^)]*)\) FROM stdin;$")
# 環境相依噪音兩類（rev5:B-011；gates.md §2）
RE_DUMPED = re.compile(r"^-- Dumped (?:from database|by pg_dump) version ")
RE_OWNER = re.compile(r"^(-- .*; Owner: )(.+)$")
OWNER_PLACEHOLDER = "-"


def normalize_seed_dump(text):
    """gates.md §2 normalize 全則。剝除／正規化四類噪音，分兩族：

    **非決定性**（同環境重放即異）——①`\\restrict`／`\\unrestrict` token 行
    （pg_dump 18.4 每次 dump 隨機）②`seaql_migrations` COPY 段（框架帳表、applied_at
    逐次重放異）。
    **環境相依**（同環境穩定、換環境即異；rev5:B-011）——③`-- Dumped from database version`
    ／`-- Dumped by pg_dump version` 兩行（postgres 或 pg_dump 升版即變）④`; Owner: X`
    註解行的**值**正規化為 `-`（DB 身分變更即變；rev5:ADR 0008 那次即為此連動重產 rev5
    fixtures；rev6 fixtures 與 rev5 逐位元同形、比對期兩側同則正規化）。

    ★③④ 只把噪音移出 **seed 逐列 diff** 的比對面，不等於放棄偵測：DB 身分變更改由
    [`compare_dump_owner`] 以一筆具名 finding 回報（守門強度不減、假紅消除）。
    ★④ 必須正規化「值」而非剝整行——`-- Data for Name: seaql_migrations; …; Owner: x`
    也帶 Owner，剝整行會連帶炸掉本函式賴以認出 seaql stanza 的那一行。

    另：COPY 段內整列排序（消物理列序假紅）；setval 原位。
    冪等：normalize(normalize(x))＝normalize(x)。
    """
    lines = text.splitlines()
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = RE_OWNER.sub(rf"\g<1>{OWNER_PLACEHOLDER}", lines[i])
        if ln.startswith("\\restrict ") or ln.startswith("\\unrestrict "):
            i += 1
            continue
        if RE_DUMPED.match(ln):
            i += 1
            continue
        if ln.startswith("-- Data for Name: seaql_migrations;"):
            if out and out[-1] == "--":
                out.pop()
            i += 1
            if i < n and lines[i] == "--":
                i += 1
            while i < n and lines[i] == "":
                i += 1
            if i < n and lines[i].startswith("COPY public.seaql_migrations "):
                while i < n and lines[i] != "\\.":
                    i += 1
                i += 1                       # 吃掉 \.
            while i < n and lines[i] == "":
                i += 1
            continue
        m = RE_COPY_HDR.match(ln)
        if m:
            out.append(ln)
            i += 1
            block = []
            while i < n and lines[i] != "\\.":
                block.append(lines[i])
                i += 1
            out.extend(sorted(block))        # 整列排序（僅段內；全檔不排序）
            if i < n:
                out.append(lines[i])         # \.
                i += 1
            continue
        out.append(ln)
        i += 1
    return "\n".join(out) + "\n"


def copy_literal(v):
    """python 值 → pg COPY text 格；不支援型別 fail-loud。"""
    if v is None:
        return "\\N"
    if v is True:
        return "t"
    if v is False:
        return "f"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        return (v.replace("\\", "\\\\").replace("\t", "\\t")
                .replace("\n", "\\n").replace("\r", "\\r"))
    raise GateError(f"seed 合成不支援的值型別：{type(v).__name__}")


def _copy_blocks(lines):
    """normalize 後文本 → {表: (欄名序, 首列行號, 末列行號後一)}；行號指 COPY 資料列範圍。"""
    blocks = {}
    i = 0
    while i < len(lines):
        m = RE_COPY_HDR.match(lines[i])
        if m:
            cols = [c.strip().strip('"') for c in m.group(2).split(",")]
            start = i + 1
            j = start
            while j < len(lines) and lines[j] != "\\.":
                j += 1
            blocks[m.group(1)] = (cols, start, j)
            i = j
        i += 1
    return blocks


def _advance_seed_sequence(lines, t, d, eid):
    """seed_add 序號合成（GR9；ADR-00085 決定 7；就地改 `lines` 之 setval 行）。

    pk 恰單欄 c 且文本有 `<表>_<c>_seq` 之 setval 行（[`RE_SETVAL`]）時：期望已發最大值
    M＝N（is_called 真）或 N−1（假；未動用形 `1, false` 即 0）；values[c] 非整數＝
    GateError；values[c] > M ⇒ 該行改寫為 (values[c], true)、≤ M 不動。pk 多欄或無對應
    setval 行（非序號主鍵）＝不推進。逐筆呼叫＝多筆依 entries 序推進取大。"""
    if len(d["pk"]) != 1:
        return
    c = d["pk"][0]
    seq = f"{t}_{c}_seq"
    for k, ln in enumerate(lines):
        m = RE_SETVAL.match(ln)
        if not m or m.group(1) != seq:
            continue
        v = d["values"][c]
        if isinstance(v, bool) or not isinstance(v, int):
            raise GateError(f"演進帳 {eid} seed_add：{t}.{c}＝{v!r} 非整數——序列 {seq} "
                            "之期望序號無從推進（序號主鍵之登記值須為整數）")
        issued = int(m.group(2)) if m.group(3) == "true" else int(m.group(2)) - 1
        if v > issued:
            lines[k] = f"SELECT pg_catalog.setval('public.{seq}', {v}, true);"
        return


def apply_seed_entries(norm_text, entries):
    """seed 面演進合成到左源（normalize 後施作、段內重排序）。消費四類 entries：
    seed_add＝{pk:[主鍵欄…], values:{欄:值 全欄}}／seed_update＝{pk:{欄:值}, set:{欄:值}}
    ／seed_delete＝{pk:{欄:值}}；★seed_add 另推進該表序號主鍵之 setval 期望行
    （[`_advance_seed_sequence`]；新 id 高於已發最大值才推、只進不退）——seed_update／
    seed_delete 不動序列（刪列不回捲＝與 PG 行為一致）；★add_column 亦動 seed 面
    （pg_dump COPY 段首欄清單隨結構走）——僅支援 nullable 無 default 形（既有列補 \\N）；其它形與 add_table 之
    seed 面合成未內建＝GateError fail-loud（該刀擴充本閘或走基線翻案；gate1 結構面照常）。"""
    seed_kinds = [e for e in entries
                  if e["kind"].startswith("seed_") or e["kind"] in ("add_column",
                                                                    "add_table")]
    if not seed_kinds:
        return norm_text
    lines = norm_text.splitlines()
    for e in seed_kinds:
        kind, t, d, eid = e["kind"], e["table"], e["detail"], e["id"]
        if kind == "add_table":
            raise GateError(f"演進帳 {eid} add_table：seed 面（pg_dump 新增 COPY 段）"
                            "合成未內建——該刀擴充 tools/schema-gate.py seed 合成或走"
                            "基線翻案（gate1 結構面已承載）")
        blocks = _copy_blocks(lines)
        if t not in blocks:
            raise GateError(f"演進帳 {eid} {kind}：seed 面無表 {t} 之 COPY 段")
        cols, start, end = blocks[t]
        rows = lines[start:end]
        if kind == "add_column":
            _need(d, ("column", "type", "nullable"), eid)
            if not (d["nullable"] is True and d.get("default") is None):
                raise GateError(f"演進帳 {eid} add_column {t}.{d['column']}：seed 面"
                                "列值合成僅支援 nullable 無 default（既有列補 \\N）——"
                                "帶 default／NOT NULL 回填形＝該刀擴充本閘或走基線翻案")
            if not re.match(r"^[a-z_][a-z0-9_]*$", d["column"]):
                raise GateError(f"演進帳 {eid} add_column：欄名 {d['column']!r} 非"
                                "樸素識別字——pg_dump 引號形無法機器合成")
            hdr = lines[start - 1]
            lines[start - 1] = hdr.replace(") FROM stdin;",
                                           f", {d['column']}) FROM stdin;")
            lines[start:end] = sorted(r + "\t\\N" for r in rows)
            continue

        def _match(row, pk_map):
            vals = row.split("\t")
            if len(vals) != len(cols):
                raise GateError(f"演進帳 {eid}：{t} COPY 列欄數 {len(vals)} ≠ 段首欄數 "
                                f"{len(cols)}（凍結面受損？）")
            return all(vals[cols.index(k)] == copy_literal(v)
                       for k, v in pk_map.items())

        # 值域斷言（rev5:B-006、斷言⑦同源；直呼合成路徑兜底）：pk/set/values 型別＋pk ⊆ COPY
        # 欄集——前世逸出裸例外（ValueError／AttributeError／TypeError）、今 GateError→rc 2。
        # ★缺鍵情形一併由本塊攔下（seed 三 kind 原 _need 呼點已被完全遮蔽、故移除）。
        if kind == "seed_add":
            if not isinstance(d.get("values"), dict):
                raise GateError(f"演進帳 {eid} seed_add：values 須為物件（欄:值 全欄）")
            if not isinstance(d.get("pk"), list) or not d["pk"]:
                raise GateError(f"演進帳 {eid} seed_add：pk 須為主鍵欄名非空清單")
            bad = sorted(set(d["pk"]) - set(cols))
            if bad:
                raise GateError(f"演進帳 {eid} seed_add：pk 欄 {bad} 不在 {t} COPY 欄集"
                                f"（欄集＝{cols}）")
        else:
            if not isinstance(d.get("pk"), dict) or not d["pk"]:
                raise GateError(f"演進帳 {eid} {kind}：pk 須為非空物件（欄:值）")
            bad = sorted(set(d["pk"]) - set(cols))
            if bad:
                raise GateError(f"演進帳 {eid} {kind}：pk 欄 {bad} 不在 {t} COPY 欄集"
                                f"（欄集＝{cols}）")
            if kind == "seed_update" and (not isinstance(d.get("set"), dict)
                                          or not d["set"]):
                raise GateError(f"演進帳 {eid} seed_update：set 須為非空物件（欄:值）")
        if kind == "seed_add":
            if set(d["values"]) != set(cols):
                raise GateError(f"演進帳 {eid} seed_add：values 欄集 ≠ {t} COPY 欄集"
                                f"（差集 {sorted(set(cols) ^ set(d['values']))}）")
            rows.append("\t".join(copy_literal(d["values"][c]) for c in cols))
            _advance_seed_sequence(lines, t, d, eid)
        elif kind == "seed_update":
            hits = [i for i, r in enumerate(rows) if _match(r, d["pk"])]
            if len(hits) != 1:
                raise GateError(f"演進帳 {eid} seed_update：{t} pk={d['pk']} 命中 "
                                f"{len(hits)} 列（須恰 1）")
            vals = rows[hits[0]].split("\t")
            for k, v in d["set"].items():
                if k not in cols:
                    raise GateError(f"演進帳 {eid} seed_update：欄 {k} 不在 {t} COPY 段")
                vals[cols.index(k)] = copy_literal(v)
            rows[hits[0]] = "\t".join(vals)
        else:  # seed_delete
            hits = [i for i, r in enumerate(rows) if _match(r, d["pk"])]
            if len(hits) != 1:
                raise GateError(f"演進帳 {eid} seed_delete：{t} pk={d['pk']} 命中 "
                                f"{len(hits)} 列（須恰 1）")
            del rows[hits[0]]
        lines[start:end] = sorted(rows)      # 段內重排序、段外原位
    return "\n".join(lines) + "\n"


RE_SETVAL = re.compile(r"^SELECT pg_catalog\.setval\('public\.(\w+)', (\d+), (true|false)\);$")


def sequence_roster(seed_text):
    """sequence 名冊＝凍結 fixtures/seed.sql 之 setval 行（RE_SETVAL 解析；唯一源、勿手抄
    名字面——rev5 另讀其 seed 決策 json 之 sequences 節並與凍結 seed 對賬、rev6 不搬該檔，
    名冊與凍結 seed 同源、該對賬改由 doccheck §9 面承載）。零命中＝比對面為空 GateError
    （pg_dump 形變或凍結面受損）；重名同紅。"""
    names = [m.group(1) for m in
             (RE_SETVAL.match(ln) for ln in seed_text.splitlines()) if m]
    if not names:
        raise GateError("凍結 fixtures/seed.sql 零 setval 行——sequence 名冊無源（比對面為空、"
                        "不得靜默判綠；凍結面受損自 git 還原、絕不重產）")
    if len(set(names)) != len(names):
        raise GateError(f"凍結 fixtures/seed.sql setval 名冊重複：{sorted(names)}")
    return sorted(names)


# rev5:B-065 setval 值佔位字面：刻意不匹配 RE_SETVAL（無數字）——再過一次收窄即原樣保留、
# 冪等自然成立；行本身仍在比對面、整行消失照紅。
_RT_SETVAL_PLACEHOLDER = "<runtime>"


def narrow_runtime_append(norm_text):
    """rev5:B-065 表級收窄變換（兩側同則、冪等；輸入＝normalize 後文本）。

    對 [`RUNTIME_APPEND_TABLES`] 各表：①剝其 COPY 資料列（段首欄名行與 ``\\.`` 照留
    照比——結構漂移仍紅）②其 sequence 之 setval **值**正規化為佔位（行本身保留——
    整行消失＝紅）。非收窄表一概不動（收窄不外溢）。冪等：佔位行不再匹配
    [`RE_SETVAL`]、零列 COPY 段再剝仍零列。★seed 側必空斷言
    （[`runtime_seed_empty_findings`]）須在本變換**之前**對左源施作——剝列後左源
    恆零列、餵後者即恆綠假閘。
    """
    lines = norm_text.splitlines()
    out, i, n = [], 0, len(lines)
    seqs = frozenset(RUNTIME_APPEND_TABLES.values())
    while i < n:
        ln = lines[i]
        m = RE_COPY_HDR.match(ln)
        if m and m.group(1) in RUNTIME_APPEND_TABLES:
            out.append(ln)                   # 段首欄名行照比
            i += 1
            while i < n and lines[i] != "\\.":
                i += 1                       # 剝 runtime 資料列
            if i < n:
                out.append(lines[i])         # \.
                i += 1
            continue
        mv = RE_SETVAL.match(ln)
        if mv and mv.group(1) in seqs:
            out.append(f"SELECT pg_catalog.setval('public.{mv.group(1)}', "
                       f"{_RT_SETVAL_PLACEHOLDER});")
            i += 1
            continue
        out.append(ln)
        i += 1
    return "\n".join(out) + "\n"


def runtime_seed_empty_findings(norm_text):
    """rev5:B-065 新斷言：seed 側（凍結 seed ⊕ 演進合成）收窄表必 0 列。

    收窄後 gate2 對這些表的資料列**無感**，防線全繫於此：有人往 seed 塞稽核列
    （或演進帳 seed_add 指向收窄表）→ 具名 finding 紅（rc 1）。★必須吃剝列**前**
    的左源文本——[`narrow_runtime_append`] 之後恆零列、餵後者即恆綠
    （同 [`compare_dump_owner`] 的輸入次序陷阱）。COPY 段缺席不在此報：收窄保留
    段首欄名行、缺段由 diff 自紅（本腿與此論證＝TestRuntimeAppendNarrow 第⑧臂釘住；
    rev5:L-019：降級腿有論證必有紅綠載體）。
    """
    findings = []
    blocks = _copy_blocks(norm_text.splitlines())
    for t in sorted(RUNTIME_APPEND_TABLES):
        if t not in blocks:
            continue
        _cols, start, end = blocks[t]
        if end > start:
            findings.append(f"[gate2·seed] runtime-append 表 {t}｜seed 側有 "
                            f"{end - start} 列資料——此類表 seed 必空（rev5:B-065 收窄"
                            "前提：稽核列只能由 runtime 寫入實庫；seed 面塞列＝繞過"
                            "收窄防線）")
    return findings


def compare_dump_owner(dump_text, expected):
    """實庫 dump 的 Owner 值一致性（rev5:B-011；配 [`normalize_seed_dump`] 第 ④ 類）。

    normalize 把 `; Owner: X` 的值抹成佔位字面後，seed 逐列 diff 對「DB 身分變更」
    從此無感——而那正是 rev5:ADR 0008 那次逼 rev5:001 凍結 fixtures 重產一次的事實。本檢查把該
    偵測換成一筆具名 finding：噪音消除、守門強度不減。

    ★零 Owner 行必須紅，不得靜默判綠：pg_dump 形變或 dump 為空時比對面即空集合，
    「查空集合恆綠」是前代反覆踩過的形（rev5:L-010 同族）。
    ★取原文 dump（normalize 前）為輸入——normalize 後值已被抹掉，餵進來恆綠。
    """
    owners = sorted({m.group(2) for m in
                     (RE_OWNER.match(ln) for ln in dump_text.splitlines()) if m})
    if not owners:
        return ["[gate2·owner] 實庫 dump 零 Owner 註解行——比對面為空、不得靜默判綠"
                "（pg_dump 輸出形變，或本檢查誤收 normalize 後文本）"]
    if owners != [expected]:
        return [f"[gate2·owner] 實庫 dump 的 Owner 值集合＝{owners}、期望恰 [{expected}]"
                "——DB 身分變更（rev5:ADR 0008 那次即此形）或 schema 出現多主人；確認為刻意"
                "變更後改連線身分之單一來源（--user／DB_USER），勿改本判準"]
    return []


def compare_seed(expected_text, actual_text, limit=60):
    """normalize 後未排序逐列 diff（含 id 欄）；★禁全檔排序後雜湊比對。"""
    exp, act = expected_text.splitlines(), actual_text.splitlines()
    if exp == act:
        return []
    import difflib
    diff = list(difflib.unified_diff(exp, act, lineterm="",
                                     fromfile="期望（fixtures⊕演進帳）",
                                     tofile="實庫（pg_dump normalize）"))
    body = diff[:limit] + ([f"…（共 {len(diff)} 行 diff、截斷）"]
                           if len(diff) > limit else [])
    return ["[gate2·seed] normalize 後逐列 diff 非零：\n    " + "\n    ".join(body)]


# ---------------------------------------------------------------------------
# audit archetype：15 表歸屬逐表驗（C／D 子型硬編碼；map note＝人讀）
# ---------------------------------------------------------------------------

TS_TZ = "timestamp with time zone"


def _cols_of(actual_cols):
    by = {}
    for c in actual_cols:
        by.setdefault(c["table"], {})[c["column"]] = c
    return by


def _check_col(fnd, t, tcols, name, type_=None, nn=None, default=None):
    c = tcols.get(name)
    if c is None:
        fnd.append(f"[audit] {t}｜欄 {name} 缺席")
        return
    if type_ is not None and c["type"] != type_:
        fnd.append(f"[audit] {t}.{name}｜型別={c['type']}、期望={type_}")
    if nn is not None and c["nullable"] != (not nn):
        fnd.append(f"[audit] {t}.{name}｜可空性={'可空' if c['nullable'] else 'NN'}、"
                   f"期望={'NN' if nn else '可空'}")
    if default is not None and (c["default"] or "") != default:
        fnd.append(f"[audit] {t}.{name}｜default={c['default']!r}、期望={default!r}")


def _pk_def(t, cons_by):
    for (tt, _name), definition in cons_by.items():
        if tt == t and definition.startswith("PRIMARY KEY"):
            return definition
    return None


def audit_archetype(map_rows, actual_cols, actual_idxs, actual_cons):
    """gates.md §3 驗則逐表執行（對實庫照相）；表清單守門；created_by 可空性顯式驗。
    C／D 子型規則不明的表＝GateError（不可驗＝不得靜默放行）。"""
    fnd = []
    cols_by = _cols_of(actual_cols)
    idx_by = {(r["table"], r["name"]): r["definition"] for r in actual_idxs}
    cons_by = {(r["table"], r["name"]): r["definition"] for r in actual_cons}
    map_tables = {r["table"] for r in map_rows}
    actual_tables = set(cols_by)
    for t in sorted(actual_tables - map_tables):
        fnd.append(f"[audit] 表清單守門｜實庫表 {t} 未登記 archetype 歸屬——"
                   "於 `archetype-map.json` 登記該表歸屬（新表另登 `add_table`；"
                   "§1 為 001 基線＝ADR-00087）")
    for t in sorted(map_tables - actual_tables):
        fnd.append(f"[audit] 表清單守門｜map 登記表 {t} 不在實庫")
    for row in sorted(map_rows, key=lambda r: r["table"]):
        t, label = row["table"], row["label"]
        if t not in cols_by:
            continue                          # 守門已計
        tc = cols_by[t]
        if label == "A 業務全六欄":
            _check_col(fnd, t, tc, "created_at", TS_TZ, nn=True, default="now()")
            _check_col(fnd, t, tc, "updated_at", TS_TZ, nn=False)
            _check_col(fnd, t, tc, "deleted_at", TS_TZ, nn=False)
            _check_col(fnd, t, tc, "created_by", "bigint")
            _check_col(fnd, t, tc, "updated_by", "bigint", nn=False)
            _check_col(fnd, t, tc, "deleted_by", "bigint", nn=False)
            for iname in (row["active_unique"] or []):
                definition = idx_by.get((t, iname))
                if definition is None:
                    fnd.append(f"[audit] {t}｜活性唯一索引 {iname} 不在實庫")
                elif "deleted_at IS NULL" not in definition:
                    fnd.append(f"[audit] {t}｜索引 {iname} 定義缺 WHERE "
                               f"(deleted_at IS NULL)：{definition!r}")
            # 反向完整性（BL-00020）：實庫有活性唯一 partial index 卻未登進 map＝靜默不驗；
            # 本工具在 sequence_roster／compare_dump_owner 對「查空集合恆綠」是明文防過的，此處補齊一致性。
            declared_au = set(row["active_unique"] or [])
            for extra in sorted({n for (tt, n), d in idx_by.items()
                                 if tt == t and "UNIQUE INDEX" in d.upper() and "deleted_at IS NULL" in d}
                                - declared_au):
                fnd.append(f"[audit] {t}｜實庫活性唯一索引 {extra} 未登進 archetype-map 之 active_unique"
                           "（登記或說明；未登記＝該支永不受本閘驗）")
        elif label == "B append-only":
            # 前綴判準（rev5:ADR 0016）：updated_*／deleted_* 起首即紅；豁免走 AUDIT_B_EXEMPT
            for bad in sorted(tc):
                if bad.startswith(AUDIT_B_FORBIDDEN_PREFIXES) \
                        and (t, bad) not in AUDIT_B_EXEMPT:
                    fnd.append(f"[audit] {t}｜變體 B 禁欄 {bad} 在場（前綴判準 "
                               "updated_*／deleted_*、append-only 不可竄改、憲法 §I.6；"
                               "合法 payload 欄走 AUDIT_B_EXEMPT 具名豁免＋理由）")
            _check_col(fnd, t, tc, "created_at", TS_TZ, nn=True, default="now()")
            _check_col(fnd, t, tc, "created_by", "bigint")
        elif label == "C join·狀態機":
            if t == "sys_user_role":
                for bad in AUDIT_SIX:
                    if bad in tc:
                        fnd.append(f"[audit] {t}｜零審計欄 join 卻見 {bad}")
            elif t == "sys_token":
                _check_col(fnd, t, tc, "created_at", TS_TZ, nn=True)
                _check_col(fnd, t, tc, "created_by", "bigint")
                if "status" not in tc:
                    fnd.append(f"[audit] {t}｜狀態機欄 status 缺席")
            elif t == "sys_pwd_custody":
                if set(tc) != {"user_id", "created_at", "created_by"}:
                    fnd.append(f"[audit] {t}｜極簡三欄集不符：{sorted(tc)}")
                pk = _pk_def(t, cons_by)
                if pk != "PRIMARY KEY (user_id, created_by)":
                    fnd.append(f"[audit] {t}｜複合 PK 期望 (user_id, created_by)、"
                               f"實得 {pk!r}")
            elif t == "sys_user_email_verify":
                if len(tc) != 5 or "user_id" not in tc:
                    fnd.append(f"[audit] {t}｜衛星五欄形不符：{sorted(tc)}")
                pk = _pk_def(t, cons_by)
                if pk != "PRIMARY KEY (user_id)":
                    fnd.append(f"[audit] {t}｜PK 期望 (user_id)、實得 {pk!r}")
            else:
                raise GateError(f"audit：表 {t} 標 C 變體但子型規則未硬編碼——"
                                "先補 gates.md §3 驗則與本工具子型分派")
        else:  # D 治理
            if t == "casbin_rule":
                _check_col(fnd, t, tc, "protected", "boolean", nn=True, default="false")
                _check_col(fnd, t, tc, "created_at", TS_TZ, nn=True, default="now()")
                _check_col(fnd, t, tc, "created_by", "bigint")
            elif t == "sys_casbin_policy_archive":
                _check_col(fnd, t, tc, "archived_at", TS_TZ, nn=True, default="now()")
                _check_col(fnd, t, tc, "archived_by", "bigint", nn=False)
                _check_col(fnd, t, tc, "archive_reason", nn=True)
                _check_col(fnd, t, tc, "created_at", TS_TZ, nn=False)
                _check_col(fnd, t, tc, "created_by", "bigint", nn=False)
            else:
                raise GateError(f"audit：表 {t} 標 D 變體但子型規則未硬編碼——"
                                "先補 gates.md §3 驗則與本工具子型分派")
        # created_by 可空性顯式驗（不靜默；期望＝data-model §1 判準：NN 恰四表）
        if "created_by" in tc:
            want_nn = t in CREATED_BY_NN
            if tc["created_by"]["nullable"] != (not want_nn):
                fnd.append(f"[audit] {t}.created_by｜可空性顯式驗不符："
                           f"{'可空' if tc['created_by']['nullable'] else 'NN'}、期望"
                           f"={'NN' if want_nn else '可空'}（NN 恰四表＝{CREATED_BY_NN}）")
        elif t in CREATED_BY_NN:
            fnd.append(f"[audit] {t}｜created_by 欄缺席（NN 四表之一）")
    return fnd


# ---------------------------------------------------------------------------
# 全時間欄型別斷言（憲法 §I.6 時間點欄通則、ADR-00060 決定 2）：射程＝右源 columns 照相之
# 全庫欄、不限審計欄。型別字面＝format_type 輸出，帶精度（timestamp(3) …）與陣列（…[]）形
# 同判：無時區 timestamp 一律紅、無豁免出口；date 須列於登記名冊方過；time／interval 類不在射程。
# ---------------------------------------------------------------------------

RE_TS_TZ_TYPE = re.compile(r"timestamp(\(\d+\))? with time zone(\[\])*")
RE_TS_NAIVE_TYPE = re.compile(r"timestamp(\(\d+\))? without time zone(\[\])*")
RE_DATE_TYPE = re.compile(r"date(\[\])*")
# date 欄登記名冊（純日曆日期、不表示瞬間——例：生日；須於引入該欄之刀 spec 具名理由）：
# 格式＝{(表名, 欄名): "<spec 出處>"}；加列＝引入該欄之刀同 commit 加列＋出處字串
# （TestConstantsPinned 同改）。合法化路徑＝本名冊、非演進帳——演進帳登記只合法化 gate1
# 結構差異、不豁免本斷言。現為空集。
DATE_COLUMNS_REGISTERED = {}


def audit_time_columns(actual_cols, registered=None):
    """回 (findings, timestamptz 欄數, 已登記 date 欄數)；registered=None＝本檔名冊常數。"""
    registered = DATE_COLUMNS_REGISTERED if registered is None else registered
    fnd, n_tz, n_date = [], 0, 0
    for c in actual_cols:
        t, name, typ = c["table"], c["column"], c["type"]
        if RE_TS_TZ_TYPE.fullmatch(typ):
            n_tz += 1
        elif RE_TS_NAIVE_TYPE.fullmatch(typ):
            fnd.append(f"[時間欄] {t}.{name}｜型別={typ}——表示瞬間之欄一律 timestamptz、禁無時區 "
                       "timestamp（憲法 §I.6 時間點欄通則／ADR-00060）；改為 timestamp with "
                       "time zone（本項無豁免出口、演進帳登記亦不合法化）")
        elif RE_DATE_TYPE.fullmatch(typ):
            if (t, name) in registered:
                n_date += 1
            else:
                fnd.append(f"[時間欄] {t}.{name}｜型別={typ} 未登記——純日曆日期欄須於引入該欄之刀 "
                           "spec 具名理由、並登記本工具 DATE_COLUMNS_REGISTERED 名冊（憲法 §I.6 "
                           "時間點欄通則／ADR-00060；合法化路徑＝登記名冊、非演進帳）；表示瞬間者"
                           "改為 timestamp with time zone")
    return fnd, n_tz, n_date


# ---------------------------------------------------------------------------
# self-test（check 入口無條件合成；敗＝rc 2 不讀真檔——防恆綠假閘）
# ---------------------------------------------------------------------------

def _st_fixtures():
    return {
        "columns": [
            {"table": "t_log", "column": "id", "ordinal": 1, "type": "bigint",
             "nullable": False, "default": "nextval('t_log_id_seq'::regclass)"},
            {"table": "t_log", "column": "created_at", "ordinal": 2, "type": TS_TZ,
             "nullable": False, "default": "now()"},
            {"table": "t_ok", "column": "id", "ordinal": 1, "type": "bigint",
             "nullable": False, "default": None},
            {"table": "t_ok", "column": "name", "ordinal": 2,
             "type": "character varying", "nullable": False, "default": None},
        ],
        "indexes": [{"table": "t_ok", "name": "t_ok_pkey",
                     "definition": "CREATE UNIQUE INDEX t_ok_pkey ON public.t_ok"
                                   " USING btree (id)"}],
        "constraints": [{"table": "t_ok", "name": "t_ok_pkey",
                         "definition": "PRIMARY KEY (id)"}],
    }


_ST_DUMP = ("\\restrict TOKEN123\n"
            "-- Dumped from database version 18.4\n"
            "-- Dumped by pg_dump version 18.4\n"
            "--\n"
            "-- Data for Name: seaql_migrations; Type: TABLE DATA; Schema: public;"
            " Owner: soybean\n"
            "--\n"
            "\n"
            "COPY public.seaql_migrations (version, applied_at) FROM stdin;\n"
            "m001\t123\n"
            "\\.\n"
            "\n"
            "--\n"
            "-- Data for Name: t_ok; Type: TABLE DATA; Schema: public; Owner: soybean\n"
            "--\n"
            "\n"
            "COPY public.t_ok (id, name) FROM stdin;\n"
            "2\tb\n"
            "1\ta\n"
            "\\.\n"
            "\n"
            "SELECT pg_catalog.setval('public.t_ok_id_seq', 2, true);\n"
            "\n"
            "\\unrestrict TOKEN123\n")


# rev5:B-065 收窄自測 dump（三收窄表零列＋非收窄 t_ok 兩列＋★前綴鄰接假想表 sys_token_x
# 帶一列與 setval——兩軸各取貼界線形釘死成員判定＝全名全等（rev5:L-020 貼界線值紀律：
# 守門值取判別點附近、非安全距離外的 t_ok）：COPY 軸表名 sys_token_x＝收窄表
# sys_token 的前綴延伸；setval 軸 sequence 名**刻意非慣例配名**取 sys_token_id_seq_x
# ＝收窄 sequence sys_token_id_seq 的前綴延伸（慣例形 sys_token_x_id_seq 在 _x 處
# 即分岔、貼不到 sequence 判別點——rev5 變異實測：前綴版對它恆綠）。匹配若退化成前綴／
# 子字串形（startswith／in 子串）即誤剝其列／誤佔位其 setval 值；
# 欄名行取合成短形——收窄邏輯只認表名與 sequence 名、不管欄集內容；離線合成、不碰真庫）
_RT_DUMP = ("COPY public.session_event (id, event_type) FROM stdin;\n"
            "\\.\n"
            "\n"
            "COPY public.sys_login_attempt (id, success) FROM stdin;\n"
            "\\.\n"
            "\n"
            "COPY public.sys_token (id, status) FROM stdin;\n"
            "\\.\n"
            "\n"
            "COPY public.sys_token_x (id, status) FROM stdin;\n"
            "9\tzz\n"
            "\\.\n"
            "\n"
            "COPY public.t_ok (id, name) FROM stdin;\n"
            "2\tb\n"
            "1\ta\n"
            "\\.\n"
            "\n"
            "SELECT pg_catalog.setval('public.session_event_id_seq', 1, false);\n"
            "SELECT pg_catalog.setval('public.sys_login_attempt_id_seq', 1, false);\n"
            "SELECT pg_catalog.setval('public.sys_token_id_seq', 1, false);\n"
            "SELECT pg_catalog.setval('public.sys_token_id_seq_x', 7, true);\n"
            "SELECT pg_catalog.setval('public.t_ok_id_seq', 2, true);\n")


def check_self_test():
    """健康對必綠＋注入假漂移必紅（四類：結構／欄序／seed 值／sequence 落值）＋
    normalize 冪等＋rev5:B-065 收窄三點探針＋時區前置（值與來源）與時間欄型別判準一正一反——任一敗＝
    AssertionError（呼叫端轉 rc 2、不讀真檔）。"""
    fix = _st_fixtures()
    healthy = synth_expected(fix, [])
    # gate1：健康綠
    if compare_structure(synth_expected(fix, []), healthy) != []:
        raise AssertionError("gate1 健康合成對被誤判為漂移")
    # gate1：未登記加欄必紅＋指名
    drifted = json.loads(json.dumps(healthy))
    drifted["columns"].append({"table": "t_ok", "column": "ghost", "ordinal": 3,
                               "type": "text", "nullable": True, "default": None})
    f = compare_structure(synth_expected(fix, []), drifted)
    if not any("columns/t_ok/ghost" in x for x in f):
        raise AssertionError("gate1 未登記加欄假漂移未被攔或未指名")
    # gate1：登記後同欄轉綠；登記超前（實庫沒有）必紅
    entry = {"id": "E-001", "knife": "001-schema-baseline", "kind": "add_column",
             "table": "t_ok", "detail": {"column": "ghost", "type": "text",
                                         "nullable": True, "default": None,
                                         "position": "末位"},
             "date": "2026-08-05"}
    if compare_structure(synth_expected(fix, [entry]), drifted) != []:
        raise AssertionError("gate1 演進帳合成後應綠而未綠")
    if not compare_structure(synth_expected(fix, [entry]), healthy):
        raise AssertionError("gate1 登記超前未被攔")
    # gate1：型別改動必紅
    mutated = json.loads(json.dumps(healthy))
    mutated["columns"][2]["type"] = "integer"
    if not compare_structure(synth_expected(fix, []), mutated):
        raise AssertionError("gate1 型別改動假漂移未被攔")
    # gate2 欄序：健康綠／同表兩欄互換必紅
    dm = {"t_ok": ["id", "name"]}
    if compare_column_order(dm, [], healthy["columns"]) != []:
        raise AssertionError("gate2 欄序健康對被誤判")
    swapped = json.loads(json.dumps(healthy["columns"]))
    for c in swapped:
        if c["table"] == "t_ok":
            c["ordinal"] = 3 - c["ordinal"]
    if not compare_column_order(dm, [], swapped):
        raise AssertionError("gate2 欄序互換假漂移未被攔")
    # gate2 seed：normalize（剝 token 行＋seaql 段＋段內排序）＋冪等＋健康綠
    norm = normalize_seed_dump(_ST_DUMP)
    if "\\restrict" in norm or "seaql_migrations" in norm:
        raise AssertionError("normalize 未剝除 pg_dump 框架噪音")
    # rev5:B-011 環境相依噪音兩類：③版本行剝除 ④Owner 值正規化
    if "Dumped from database version" in norm or "Dumped by pg_dump version" in norm:
        raise AssertionError("normalize 未剝除 pg_dump 版本行（環境相依噪音③）")
    if "Owner: soybean" in norm:
        raise AssertionError("normalize 未正規化 Owner 值（環境相依噪音④）")
    # ★正規化「值」而非剝整行：Owner 註解行本身須留下，否則 seaql stanza 認不出來
    if f"-- Data for Name: t_ok; Type: TABLE DATA; Schema: public; " \
       f"Owner: {OWNER_PLACEHOLDER}" not in norm:
        raise AssertionError("normalize 誤剝整行 Owner 註解——應只抹值、保留該行")
    # ★環境相依噪音改變後仍須判綠（rev5:B-011 存在的理由：升版／換身分不得紅在純噪音）
    upgraded = (_ST_DUMP.replace("version 18.4", "version 19.1")
                        .replace("Owner: soybean", "Owner: other_role"))
    if compare_seed(norm, normalize_seed_dump(upgraded)) != []:
        raise AssertionError("normalize 後 pg_dump 升版／DB 身分變更仍被判 seed 漂移")
    if norm.index("1\ta") > norm.index("2\tb"):
        raise AssertionError("normalize COPY 段內未整列排序")
    if normalize_seed_dump(norm) != norm:
        raise AssertionError("normalize 非冪等")
    if compare_seed(norm, normalize_seed_dump(_ST_DUMP)) != []:
        raise AssertionError("gate2 seed 健康對被誤判")
    # rev5:B-011 owner 一致性檢查＝噪音移出比對面後的補償守門，四格自證
    if compare_dump_owner(_ST_DUMP, DB_USER) != []:
        raise AssertionError("owner 檢查對健康 dump 誤判")
    if not compare_dump_owner(_ST_DUMP.replace("Owner: soybean", "Owner: other_role"),
                              DB_USER):
        raise AssertionError("owner 檢查未攔全庫身分變更（rev5:ADR 0008 那次即此形）")
    if not compare_dump_owner(
            _ST_DUMP.replace("Owner: soybean", "Owner: other_role", 1), DB_USER):
        raise AssertionError("owner 檢查未攔多主人 schema（值集合非單元素）")
    if not compare_dump_owner("COPY public.t_ok (id) FROM stdin;\n\\.\n", DB_USER):
        raise AssertionError("owner 檢查對零 Owner 行未紅——查空集合恆綠")
    # ★接錯輸入即恆綠：normalize 後值已成佔位，本檢查必須吃原文 dump
    if not compare_dump_owner(norm, DB_USER):
        raise AssertionError("owner 檢查誤收 normalize 後文本卻判綠——輸入須為原文 dump")
    # seed 值改一格必紅；sequence 落值 ±1 必紅
    if not compare_seed(norm, norm.replace("1\ta", "1\tX")):
        raise AssertionError("gate2 seed 值假漂移未被攔")
    if not compare_seed(norm, norm.replace("', 2, true);", "', 3, true);")):
        raise AssertionError("gate2 sequence 落值假漂移未被攔")
    # add_column 登記之 seed 面合成：COPY 段首欄清單接末位＋既有列補 \N 後轉綠
    drift_dump = (norm.replace("COPY public.t_ok (id, name) FROM stdin;",
                               "COPY public.t_ok (id, name, ghost) FROM stdin;")
                  .replace("1\ta", "1\ta\t\\N").replace("2\tb", "2\tb\t\\N"))
    if compare_seed(norm, drift_dump) == []:
        raise AssertionError("gate2 seed 未攔加欄後的 COPY 段漂移")
    if compare_seed(apply_seed_entries(norm, [entry]), drift_dump) != []:
        raise AssertionError("gate2 seed add_column 合成後應綠而未綠")
    # rev5:B-065 runtime-append 收窄三點探針（九臂全測歸 TestRuntimeAppendNarrow；此處常駐
    # 防恆綠）：①收窄表 runtime 列剝後綠②非收窄表列漂移照紅③seed 側塞列必紅
    rt_left = narrow_runtime_append(normalize_seed_dump(_RT_DUMP))
    rt_hot = _RT_DUMP.replace(
        "COPY public.session_event (id, event_type) FROM stdin;\n",
        "COPY public.session_event (id, event_type) FROM stdin;\n7\tlogin\n")
    if compare_seed(rt_left, narrow_runtime_append(normalize_seed_dump(rt_hot))) != []:
        raise AssertionError("rev5:B-065 收窄未生效——收窄表 runtime 列仍被判 seed 漂移")
    if not compare_seed(rt_left, narrow_runtime_append(
            normalize_seed_dump(_RT_DUMP.replace("1\ta", "1\tX")))):
        raise AssertionError("rev5:B-065 收窄外溢——非收窄表列漂移未被攔")
    if not runtime_seed_empty_findings(normalize_seed_dump(rt_hot)):
        raise AssertionError("rev5:B-065 seed 必空斷言未攔 seed 側稽核列")
    # audit：健康 A／B 合成對綠；B 表注入 updated_at 必紅
    amap = [{"table": "t_biz", "label": "A 業務全六欄",
             "active_unique": ["t_biz_code_active_uniq"], "note": ""},
            {"table": "t_log2", "label": "B append-only",
             "active_unique": None, "note": ""}]
    acols = [
        {"table": "t_biz", "column": "id", "ordinal": 1, "type": "bigint",
         "nullable": False, "default": None},
        {"table": "t_biz", "column": "created_at", "ordinal": 2, "type": TS_TZ,
         "nullable": False, "default": "now()"},
        {"table": "t_biz", "column": "created_by", "ordinal": 3, "type": "bigint",
         "nullable": True, "default": None},
        {"table": "t_biz", "column": "updated_at", "ordinal": 4, "type": TS_TZ,
         "nullable": True, "default": None},
        {"table": "t_biz", "column": "updated_by", "ordinal": 5, "type": "bigint",
         "nullable": True, "default": None},
        {"table": "t_biz", "column": "deleted_at", "ordinal": 6, "type": TS_TZ,
         "nullable": True, "default": None},
        {"table": "t_biz", "column": "deleted_by", "ordinal": 7, "type": "bigint",
         "nullable": True, "default": None},
        {"table": "t_log2", "column": "id", "ordinal": 1, "type": "bigint",
         "nullable": False, "default": None},
        {"table": "t_log2", "column": "created_at", "ordinal": 2, "type": TS_TZ,
         "nullable": False, "default": "now()"},
        {"table": "t_log2", "column": "created_by", "ordinal": 3, "type": "bigint",
         "nullable": True, "default": None},
    ]
    aidx = [{"table": "t_biz", "name": "t_biz_code_active_uniq",
             "definition": "CREATE UNIQUE INDEX t_biz_code_active_uniq ON"
                           " public.t_biz USING btree (code)"
                           " WHERE (deleted_at IS NULL)"}]
    if audit_archetype(amap, acols, aidx, []) != []:
        raise AssertionError("audit 健康合成對被誤判")
    bad = json.loads(json.dumps(acols))
    bad.append({"table": "t_log2", "column": "updated_at", "ordinal": 4,
                "type": TS_TZ, "nullable": True, "default": None})
    if not any("禁欄 updated_at" in x for x in audit_archetype(amap, bad, aidx, [])):
        raise AssertionError("audit 變體 B 禁欄假漂移未被攔")
    # 時區前置（ADR-00059）：UTC 放行／非 UTC 必攔
    if timezone_problem("UTC") is not None:
        raise AssertionError("時區前置對 UTC 誤攔")
    if timezone_problem("Asia/Tokyo") is None:
        raise AssertionError("時區前置未攔非 UTC")
    # 時區來源（ADR-00059）：伺服器側放行／連線端（client、session）必攔
    if timezone_source_problem("command line") is not None:
        raise AssertionError("時區來源對伺服器側（command line）誤攔")
    for source in CLIENT_TIMEZONE_SOURCES:
        if timezone_source_problem(source) is None:
            raise AssertionError(f"時區來源未攔連線端（{source}）")
    # 時間欄型別（ADR-00060）：健康 timestamptz 綠／無時區 timestamp 紅／date 未登記紅、登記後綠
    if audit_time_columns(acols, {}) != ([], 4, 0):
        raise AssertionError("時間欄型別健康合成對被誤判或計數錯")
    naive = acols + [{"table": "t_biz", "column": "fired_at", "ordinal": 8,
                      "type": "timestamp without time zone", "nullable": True, "default": None}]
    if not any("t_biz.fired_at" in x for x in audit_time_columns(naive, {})[0]):
        raise AssertionError("時間欄型別未攔無時區 timestamp")
    dated = acols + [{"table": "t_biz", "column": "birthday", "ordinal": 8,
                      "type": "date", "nullable": True, "default": None}]
    if not any("t_biz.birthday" in x for x in audit_time_columns(dated, {})[0]):
        raise AssertionError("時間欄型別未攔未登記 date")
    if audit_time_columns(dated, {("t_biz", "birthday"): "self-test"}) != ([], 4, 1):
        raise AssertionError("時間欄型別對已登記 date 誤攔或計數錯")


# ---------------------------------------------------------------------------
# check 子命令
# ---------------------------------------------------------------------------

def cmd_check(root=REPO_ROOT, container=None, user=DB_USER, db=DB_NAME,
              run=subprocess.run):
    # ① self-test（無條件；敗＝rc 2、不讀任何真檔——防恆綠假閘）
    try:
        check_self_test()
    except (AssertionError, GateError) as ex:
        print(f"[check] ✗ self-test 失敗（比對邏輯壞、不讀真檔）：{ex}", file=sys.stderr)
        return 2
    # ② 左源載入（啟動斷言 fail-loud）
    try:
        ledger = load_ledger(root)
        fixtures = load_fixtures(root)
        map_rows = load_archetype_map(root)
        dm_order = load_data_model_order(root)
    except GateError as ex:
        print(f"[check] ✗ {ex}", file=sys.stderr)
        return 2
    # ③ 右源照相＋dump（唯讀）；最先斷言目標庫時區（ADR-00059 決定 3；≠UTC＝rc 2、不往下比對），
    #    緊接斷言其來源在伺服器側（client／session＝值來自連線端＝rc 2、不往下比對）
    try:
        problem = timezone_problem(psql(SQL_TIMEZONE, container=container, user=user,
                                        db=db, run=run))
        if problem:
            raise GateError(problem)
        tz_source = psql(SQL_TIMEZONE_SOURCE, container=container, user=user, db=db, run=run)
        problem = timezone_source_problem(tz_source)
        if problem:
            raise GateError(problem)
        actual = {
            "columns": sorted(psql(SQL_COLUMNS, parse=True, container=container,
                                   user=user, db=db, run=run),
                              key=lambda r: (r["table"], r["ordinal"])),
            "indexes": sorted(psql(SQL_INDEXES, parse=True, container=container,
                                   user=user, db=db, run=run),
                              key=lambda r: (r["table"], r["name"])),
            "constraints": sorted(psql(SQL_CONSTRAINTS, parse=True, container=container,
                                       user=user, db=db, run=run),
                                  key=lambda r: (r["table"], r["name"])),
        }
        if not actual["columns"]:
            raise GateError("實庫照相 columns 為空——比對面為空（migration 未跑？）")
        dump = pg_dump_data(container=container, user=user, db=db, run=run)
    except GateError as ex:
        print(f"[check] ✗ {ex}", file=sys.stderr)
        return 2
    # ④ 三閘（合成期望；合成不可能＝結構異常 rc 2）
    try:
        expected = synth_expected(fixtures, ledger["entries"])
        frozen_norm = normalize_seed_dump(fixtures["seed"])
        roster = sequence_roster(frozen_norm)
        seed_expected = apply_seed_entries(frozen_norm, ledger["entries"])
        findings = compare_structure(expected, actual)
        findings += compare_column_order(dm_order, ledger["entries"], actual["columns"])
        # rev5:B-065：必空斷言吃**左源**且先於剝列（左右搞反／次序反轉皆＝恆綠假閘；
        # TestCmdCheckSeedEmptyWiring 釘住兩者）；兩側同則收窄後再逐列 diff
        findings += runtime_seed_empty_findings(seed_expected)
        seed_narrowed = narrow_runtime_append(seed_expected)
        seed_findings = compare_seed(seed_narrowed,
                                     narrow_runtime_append(normalize_seed_dump(dump)))
        findings += seed_findings
        # ★餵原文 dump（normalize 前）：normalize 已把 Owner 值抹成佔位，餵後者恆綠
        findings += compare_dump_owner(dump, user)
        findings += audit_archetype(map_rows, actual["columns"], actual["indexes"],
                                    actual["constraints"])
        # 全時間欄型別斷言（憲法 §I.6 時間點欄通則、ADR-00060 決定 2）
        time_findings, n_tz, n_date = audit_time_columns(actual["columns"])
        findings += time_findings
    except GateError as ex:
        print(f"[check] ✗ {ex}", file=sys.stderr)
        return 2
    if findings:
        print(f"[check] ✗ {len(findings)} 項漂移（未登記差異一律紅；合法化唯一路徑＝"
              "schema-evolution.json 登記——[時間欄] 項除外、見該項訊息）：", file=sys.stderr)
        for x in findings:
            print(f"    DRIFT {x}", file=sys.stderr)
        return 1
    n_entries = len(ledger["entries"])
    print(f"[check] ✓ 時區：SHOW timezone＝{EXPECTED_TIMEZONE}（source＝{tz_source}）")
    print(f"[check] ✓ gate1 結構：columns {len(actual['columns'])}／indexes "
          f"{len(actual['indexes'])}／constraints {len(actual['constraints'])} 全等"
          f"（演進帳合成 {n_entries} 筆）")
    print(f"[check] ✓ gate2 欄序：{len(dm_order)} 親排表逐位全等"
          f"（{'、'.join(ORDER_EXEMPT)} 豁免）")
    print(f"[check] ✓ gate2 seed：normalize 後 {len(seed_narrowed.splitlines())} 行"
          f"逐列零差異（setval 名冊 {len(roster)} 支；runtime-append 收窄 "
          f"{len(RUNTIME_APPEND_TABLES)} 表）")
    print(f"[check] ✓ audit archetype：{len(map_rows)}/{len(map_rows)} 綠"
          "（表清單守門通過）")
    print(f"[check] ✓ 時間欄型別：{n_tz} 欄 timestamptz、date 登記 {n_date}")
    return 0


# ---------------------------------------------------------------------------
# doccheck 子命令（承 rev5:B-010；離線、不讀庫；★不入 pre-commit 常跑鏈——護 pre-commit 雙錨
# 45／90 秒預算（承 rev5:B-007），手動／review 輪跑）
# ---------------------------------------------------------------------------

def cmd_doccheck(root=REPO_ROOT):
    """data-model 文件面（§2／§6／§9）vs 凍結 fixtures 機器對賬；rc：0 全等／1 對賬差異／
    2 環境或結構異常（fixtures 缺、段落定位失敗、解析自檢敗）。"""
    try:
        fixtures = load_fixtures(root)
        path = os.path.join(root, DATA_MODEL)
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except FileNotFoundError:
            raise GateError(f"data-model.md 缺席（{path}）") from None
        five = parse_data_model_five(text)
        idx_doc, con_doc = parse_data_model_defs(text)
        seq_named, seq_rest = parse_data_model_sequences(text)
        findings = doccheck_findings(five, idx_doc, con_doc, fixtures)
        findings += doccheck_sequence_findings(seq_named, seq_rest, fixtures["seed"])
    except GateError as ex:
        print(f"[doccheck] ✗ {ex}", file=sys.stderr)
        return 2
    if findings:
        print(f"[doccheck] ✗ {len(findings)} 項文件面 vs fixtures 對賬差異（文件單邊"
              "被改＝紅；fixtures 屬凍結面、受損自 git 還原絕不重產）：", file=sys.stderr)
        for x in findings:
            print(f"    DOC-DRIFT {x}", file=sys.stderr)
        return 1
    n_cols = sum(len(v) for v in five.values())
    print(f"[doccheck] ✓ §2 五元組：{len(five)} 親排表 {n_cols} 欄 vs fixtures/columns "
          f"全等（{'、'.join(ORDER_EXEMPT)} 依 §7 豁免）")
    print(f"[doccheck] ✓ §6 索引 {len(idx_doc)} 支／約束 {len(con_doc)} 條 vs "
          "fixtures/{indexes,constraints} 全等")
    print(f"[doccheck] ✓ §9 sequences：具名 {len(seq_named)} 支落值＋其餘 {len(seq_rest)} 支"
          f"未動用 vs fixtures/seed.sql setval 行全等（名冊 {len(seq_named) + len(seq_rest)} 支）")
    return 0


# ---------------------------------------------------------------------------
# offline 子命令（BL-00148；ADR-00108 決定 8）
# ---------------------------------------------------------------------------

# 判準五款各為可單獨替換之模組層函式（TestOfflineCriterionMutants 逐支以恆放行之樁停用）。本節零新增模組層
# 正則：Rust 與 SQL 兩層皆以字元級掃描器切詞——字串續行、raw 字串、巢狀括號與 `$$` 本體非正則可正確切分。
OFFLINE_MIGRATION_DIR = os.path.join("rust-api", "migration", "src")   # REPO_ROOT 相對；讀 rust-api 工作樹
OFFLINE_FIRST_DELTA = 3     # 四碼 ≥ 0003＝delta；m0001／m0002 為基線（ADR-00010 決定 1）

_DIGITS = "0123456789"
_HEX = _DIGITS + "abcdefABCDEF"
_LOWER_SNAKE = "abcdefghijklmnopqrstuvwxyz" + _DIGITS + "_"
_ID_START = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
_ID_CONT = _ID_START + _DIGITS
# Rust 標點字元全集（判準①n：字串、字元字面與註解之外，識別字、數字與空白以外只收此集）
_RUST_PUNCT = "+-*/%^!&|=<>@.,;:#$?~()[]{}"
# 詞素形（shape）之非識別字標記：識別字與標點以原值為形，字串／數字以下列標記為形（不與任何原值相撞）
_S_STR, _S_NUM = "\0str", "\0num"


def _offline_delta_number(name):
    """檔名 `m<四碼>_<小寫蛇形>.rs` → 四碼數值；不合形＝None（三碼、五碼、大寫、他副檔名皆不合）。"""
    stem = name[:-3] if name.endswith(".rs") else ""
    if len(stem) < 7 or stem[0] != "m" or stem[5] != "_":
        return None
    if any(c not in _DIGITS for c in stem[1:5]) or any(c not in _LOWER_SNAKE for c in stem[6:]):
        return None
    return int(stem[1:5])


def offline_delta_files(root):
    """delta 檔集＝OFFLINE_MIGRATION_DIR 下合檔名形且四碼 ≥ OFFLINE_FIRST_DELTA 者，依四碼數值升冪（m0010 起照收）。
    目錄缺席＝GateError（本工具不設環境跳過分支；ADR-00019 決定 3／4）。"""
    d = os.path.join(root, OFFLINE_MIGRATION_DIR)
    try:
        names = os.listdir(d)
    except (FileNotFoundError, NotADirectoryError):
        raise GateError(f"delta migration 目錄缺席（{d}）——比對面為空、不得靜默判綠"
                        "（本工具不設環境跳過分支：rust-api 工作樹缺席即 rc 2）") from None
    found = []
    for name in names:
        num = _offline_delta_number(name)
        if num is not None and num >= OFFLINE_FIRST_DELTA:
            found.append((num, name))
    return [os.path.join(d, name) for _num, name in sorted(found)]


def _offline_assert_nonempty(paths, root):
    """判準⑦（比對面為空）：零支 delta＝GateError（rc 2）——零支即無一句可對賬、全綠是假綠。"""
    if not paths:
        raise GateError(f"{os.path.join(root, OFFLINE_MIGRATION_DIR)} 零支 delta migration"
                        f"（m<四碼>_<小寫蛇形>.rs、四碼 ≥ {OFFLINE_FIRST_DELTA:04d}）——比對面為空、不得靜默判綠")


# ── Rust 詞素（判準①之載體；只切本腿所需之粗粒度、不做語法分析）──────────────

def _rust_string(text, i, where, line):
    """自 text[i]（`"`）解一般字串字面 → (值, 結束後位置)：跳脫還原；`\\` 接換行＝續行（吃掉換行與其後全部空格、`\\t`、`\\r`、
    `\\n`——含空行；同 rustc 之續行略過集）。"""
    simple = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", "0": "\0", "'": "'", '"': '"'}
    out, j, n = [], i + 1, len(text)
    while j < n:
        c = text[j]
        if c == '"':
            return "".join(out), j + 1
        if c != "\\":
            out.append(c)
            j += 1
            continue
        e = text[j + 1:j + 2]
        if e == "\n":
            j += 2
            while j < n and text[j] in " \t\r\n":
                j += 1
        elif e in simple:
            out.append(simple[e])
            j += 2
        elif e == "x" and len(text[j + 2:j + 4]) == 2 and all(h in _HEX for h in text[j + 2:j + 4]):
            out.append(chr(int(text[j + 2:j + 4], 16)))
            j += 4
        elif e == "u" and text[j + 2:j + 3] == "{" and text.find("}", j) > j:
            k = text.find("}", j)
            hexd = text[j + 3:k].replace("_", "")
            if not hexd or any(h not in _HEX for h in hexd):
                raise GateError(f"{where} 第 {line} 行：字串之 \\u{{…}} 跳脫壞形")
            out.append(chr(int(hexd, 16)))
            j = k + 1
        else:
            raise GateError(f"{where} 第 {line} 行：字串含未支援之跳脫 \\{e}")
    raise GateError(f"{where} 第 {line} 行：字串未閉合")


def _rust_unsupported(c):
    """判準①n（字串、字元字面與註解之外之字元白名單；fail-closed）：c 屬 [`_RUST_PUNCT`]＝None；否＝訊息（呼叫端 GateError
    指名檔與行）。呼叫端只在 c 非 ASCII 識別字字元、數字、空白（空格、`\\t`、`\\r`、`\\n`）、引號與註解起首時呼叫。rustc 之切法與
    本掃描器不同處，詞素錯位即可繞過以詞素形比對之判準（判準①j 之 `mod`、識別字、`;` 三詞素比對落空等），逐途徑：非 ASCII 識別字
    字元（rustc 依 Unicode XID 收；`#[path]` 配 `mod 影;`、`mod shadow影;`）、rustc 視為空白而本掃描器不收者（`\\x0b`、`\\x0c`、
    U+0085、U+200E、U+200F、U+2028、U+2029）；rustc 亦拒之字元（他控制字元、非 ASCII 標點、反斜線）同拒。"""
    if c in _RUST_PUNCT:
        return None
    return (f"字串、字元字面與註解之外之未支援字元 {c!r}（U+{ord(c):04X}；只收 ASCII 識別字、數字、空格／\\t／\\r／\\n 與"
            " Rust 標點——rustc 之切法與本掃描器不同、詞素錯位可繞過判準）")


def _rust_tokens(text, where):
    """Rust 原文 → 詞素 [(類, 值, 行)]；類＝id（ASCII 識別字與 raw 識別字 `r#<名>`）／str（一般與 r 前綴 raw 字串〔任意個 `#`〕，
    值已還原）／num（數字字面原文）／p（單字元 Rust 標點）／other（byte 與 c 字串、字元、lifetime——不入本腿判準）。行註解與塊註解
    （可巢狀）略去；字串、字元與塊註解未閉合＝GateError；他字元＝GateError（判準①n [`_rust_unsupported`]）。"""
    toks, i, n, line = [], 0, len(text), 1
    while i < n:
        c = text[i]
        if c == "\n":
            line += 1
            i += 1
        elif c in " \t\r":
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text.startswith("/*", i):
            depth, j = 1, i + 2
            while depth:
                if j >= n:
                    raise GateError(f"{where} 第 {line} 行：塊註解未閉合")
                if text.startswith("/*", j):
                    depth, j = depth + 1, j + 2
                elif text.startswith("*/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            line += text.count("\n", i, j)
            i = j
        elif c in _ID_START:
            j = i
            while j < n and text[j] in _ID_CONT:
                j += 1
            word = text[i:j]
            h = j
            while h < n and text[h] == "#":
                h += 1
            if word in ("r", "br", "cr") and h < n and text[h] == '"':
                close = '"' + "#" * (h - j)
                k = text.find(close, h + 1)
                if k < 0:
                    raise GateError(f"{where} 第 {line} 行：raw 字串未閉合")
                toks.append(("str" if word == "r" else "other", text[h + 1:k], line))
                line += text.count("\n", i, k)
                i = k + len(close)
            elif word == "r" and h == j + 1 and h < n and text[h] in _ID_START:
                k = h
                while k < n and text[k] in _ID_CONT:
                    k += 1
                toks.append(("id", text[h:k], line))      # raw 識別字 r#名
                i = k
            elif word in ("b", "c") and j < n and text[j] == '"':
                _val, k = _rust_string(text, j, where, line)
                toks.append(("other", text[i:k], line))
                line += text.count("\n", i, k)
                i = k
            else:
                toks.append(("id", word, line))
                i = j
        elif c == '"':
            val, k = _rust_string(text, i, where, line)
            toks.append(("str", val, line))
            line += text.count("\n", i, k)
            i = k
        elif c == "'":
            if text[i + 1:i + 2] == "\\":
                k = text.find("'", i + 3)
            elif text[i + 2:i + 3] == "'":
                k = i + 2
            else:
                k = i + 1
                while k < n and text[k] in _ID_CONT:
                    k += 1
                toks.append(("other", text[i:k], line))   # lifetime／label
                i = k
                continue
            if k < 0:
                raise GateError(f"{where} 第 {line} 行：字元字面未閉合")
            toks.append(("other", text[i:k + 1], line))
            i = k + 1
        elif c in _DIGITS:
            j = i
            while j < n and text[j] in _ID_CONT:
                j += 1
            toks.append(("num", text[i:j], line))
            i = j
        else:
            bad = _rust_unsupported(c)
            if bad:
                raise GateError(f"{where} 第 {line} 行：{bad}")
            toks.append(("p", c, line))
            i += 1
    return toks


def _tok_shape(t):
    """詞素之形：識別字與標點取原值、字串與數字取標記（Rust 與 SQL 詞素共用；SQL 詞取大寫）。"""
    kind, val = t[0], t[1]
    if kind in ("id", "p"):
        return val
    if kind == "w":
        return val.upper()
    if kind in ("str", "s"):
        return _S_STR
    if kind in ("num", "n"):
        return _S_NUM
    return "\0" + kind


def _tok_close(toks, i):
    """toks[i] 為開括號 → 其配對閉括號之索引（括號種類不辨、只計深度）；未配對＝None。"""
    depth = 0
    for k in range(i, len(toks)):
        if toks[k][0] != "p":
            continue
        if toks[k][1] in "([{":
            depth += 1
        elif toks[k][1] in ")]}":
            depth -= 1
            if depth == 0:
                return k
    return None


def _tok_find(toks, start, seps):
    """自 start 起第一個深度 0 且值屬 seps 之標點的索引；無＝None。"""
    depth = 0
    for k in range(start, len(toks)):
        if toks[k][0] != "p":
            continue
        if toks[k][1] in "([{":
            depth += 1
        elif toks[k][1] in ")]}":
            depth -= 1
        elif depth == 0 and toks[k][1] in seps:
            return k
    return None


def _tok_split(toks, sep):
    """依深度 0 之標點 sep 切段（括號內不切）；回段之清單（恆 ≥ 1 段，尾段可為空）。"""
    parts, depth = [[]], 0
    cur = parts[0]
    for t in toks:
        if t[0] == "p" and t[1] in "([{":
            depth += 1
        elif t[0] == "p" and t[1] in ")]}":
            depth -= 1
        if depth == 0 and t[0] == "p" and t[1] == sep:
            cur = []
            parts.append(cur)
        else:
            cur.append(t)
    return parts


def _tok_args(toks):
    """呼叫引數：依深度 0 之逗號切段，容 rustfmt 直排之尾逗號（末段為空即去）。"""
    parts = _tok_split(toks, ",")
    if len(parts) > 1 and not parts[-1]:
        parts.pop()
    return parts


def _rust_render(toks, limit=12):
    """詞素回顯（錯誤訊息指名用）：相鄰兩詞素皆為字詞類時補空白、餘者直接相接；字串加引號。"""
    out, prev_word = [], False
    for t in toks[:limit]:
        word = t[0] in ("id", "num", "str", "other")
        if word and prev_word:
            out.append(" ")
        out.append(f'"{t[1]}"' if t[0] == "str" else t[1])
        prev_word = word
    return "".join(out) + ("…" if len(toks) > limit else "")


def _rust_head(toks):
    """句首回顯：至第一個 `(`（含）為止——例 `manager.create_table(`、`run_sql(`。"""
    for k, t in enumerate(toks):
        if t[:2] == ("p", "("):
            return _rust_render(toks[:k + 1], limit=k + 1)
    return _rust_render(toks)


def _offline_construct(toks):
    """右式他形之構造名（rc 2 訊息指名用）。"""
    s = [_tok_shape(t) for t in toks]
    if len(toks) >= 2 and toks[0][0] == "id" and s[1] == "!":
        return f"{toks[0][1]}!"
    if len(toks) >= 2 and toks[0][0] == "id" and s[1] == "(":
        return f"函式呼叫 {toks[0][1]}(…)"
    if len(toks) == 1 and toks[0][0] == "id":
        return f"引用他常數 {toks[0][1]}"
    return _rust_render(toks)


def _offline_macro_body(where, name, body):
    """判準①b：`macro_rules! 名 { () => { "字面" }; }`——單規則、零引數、展開恰一字面（字串或 raw 字串）、
    末規則分號可省；回展開字串。他形（帶引數、多規則、展開非單一字面）＝GateError 指名巨集名。"""
    s = [_tok_shape(t) for t in body]
    if s in (["(", ")", "=", ">", "{", _S_STR, "}"], ["(", ")", "=", ">", "{", _S_STR, "}", ";"]):
        return body[5][1]
    raise GateError(f"{where}：macro_rules! {name} 非「單規則、零引數、展開恰一字面」形"
                    f"（得 {_rust_render(body)}）")


def _offline_unique_name(where, what, name, seen):
    """判準①f：同名第二次宣告＝GateError 指名檔與名（常數名冊與 macro_rules! 名冊各自判；不論所在 scope 或
    `#[cfg]`）——Rust 依 scope／cfg 擇一綁定、本腿不辨二者，取文本序之任一皆可綁錯定義而假綠，故同名宣告須恰一。"""
    if name in seen:
        raise GateError(f"{where}：{what} {name} 重複定義（不辨 scope 與 #[cfg]；同名宣告須恰一）")


def _offline_foreign_scope(where, toks):
    """判準①j（檔外巨集引入；fail-closed）：本腿只展開檔內 macro_rules! 與內建 concat!，檔外定義得以進入本檔作用域而遮蔽二者之途徑
    ＝GateError 指名檔與途徑，逐途徑：①檔案模組宣告 `mod <名>;`（不論屬性與可見性；`<名>` 為 ASCII 識別字或 raw 識別字 `r#<名>`
    〔掃描器還原為識別字詞素〕——非 ASCII 名與 `mod` 後之 rustc 空白不成三詞素，由判準①n [`_rust_unsupported`] 於切詞時先擋；
    其檔之 macro_rules! 經 `#[macro_use]` 延伸至本檔其後文本、後定義遮蔽先定義——檔案模組非巨集展開、不受「巨集展開之 macro_rules!
    不得遮蔽外層同名巨集」之限，檔內巨集與內建
    concat! 皆可被遮蔽，本腿不讀該檔）②`use` 宣告含識別字 `concat`（含 `as concat` 改名與清單形；匯入之同名巨集於模組作用域遮蔽
    prelude 之內建 concat!）。`#[macro_use]`／`#[path]` 不另判：承載者為檔案模組即屬①；inline mod 之內容照判準①b／①f／①k 掃；
    `#[macro_use] extern crate` 限 crate 根（rustc E0468）、delta 檔非 crate 根。"""
    for i in range(len(toks) - 2):
        if toks[i][:2] == ("id", "mod") and toks[i + 1][0] == "id" and toks[i + 2][:2] == ("p", ";"):
            raise GateError(f"{where}：檔案模組宣告 mod {toks[i + 1][1]};（其檔之 macro_rules! 經 #[macro_use] 可遮蔽檔內巨集"
                            "與內建 concat!、本腿不讀該檔）")
    for i, t in enumerate(toks):
        if t[:2] == ("id", "use"):
            end = _tok_find(toks, i + 1, ";")
            seg = toks[i + 1:] if end is None else toks[i + 1:end]
            if ("id", "concat") in [x[:2] for x in seg]:
                raise GateError(f"{where}：use 宣告含 concat（匯入之同名巨集遮蔽內建 concat!）——得 use {_rust_render(seg)}")


def _offline_macro_reach(where, name, rhs, macros, at):
    """判準①k（檔內巨集之文本作用域）：常數 name（宣告於詞素 at）之右式所呼叫之檔內巨集（`<巨集名>!`）須定義於檔案頂層（括號深度 0）
    且先於該常數——Rust 對未限定之巨集名先查文本作用域、查無才循路徑解析（`use` 匯入、`#[macro_export]`）：定義在後、或在 inline mod
    與函式本體內（文本作用域止於其閉括號）時，呼叫可綁到檔外同名巨集而本腿照檔內定義展開判綠。違者＝GateError 指名常數與巨集名。
    macros：巨集名 → (展開字串, 定義詞素位置, 括號深度)。"""
    for k in range(len(rhs) - 1):
        if rhs[k][0] == "id" and rhs[k][1] in macros and rhs[k + 1][:2] == ("p", "!"):
            _lit, pos, depth = macros[rhs[k][1]]
            if depth or pos > at:
                raise GateError(f"{where}：常數 {name} 呼叫之檔內巨集 {rhs[k][1]}! 不在其文本作用域（macro_rules! 須定義於檔案頂層"
                                "且先於呼叫之常數；否則 Rust 循路徑解析、可綁到檔外同名巨集）")


def _offline_const_rhs(where, name, rhs, macros):
    """判準①a：`const 名: &str = 右式;` 之右式恰三形——字串字面、檔內巨集零引數呼叫 `名!()`、`concat!(項, …)`
    （項＝字串字面或檔內巨集零引數呼叫；尾逗號可）；回展開字串。他形＝GateError 指名檔、常數名與構造
    （include_str!／format! 等他巨集、引用他常數、函式呼叫、concat! 含他項）。"""
    def item(part):
        s = [_tok_shape(t) for t in part]
        if s == [_S_STR]:
            return part[0][1]
        if len(part) == 4 and part[0][0] == "id" and s[1:] == ["!", "(", ")"] and part[0][1] in macros:
            return macros[part[0][1]]
        return None

    v = item(rhs)
    if v is not None:
        return v
    s = [_tok_shape(t) for t in rhs]
    if len(rhs) >= 4 and s[:3] == ["concat", "!", "("] and _tok_close(rhs, 2) == len(rhs) - 1:
        out = []
        for part in _tok_args(rhs[3:-1]):
            pv = item(part)
            if pv is None:
                raise GateError(f"{where}：常數 {name} 之 concat! 含非字面、非檔內巨集零引數呼叫之項"
                                f"（{_rust_render(part) or '空項'}）")
            out.append(pv)
        return "".join(out)
    raise GateError(f"{where}：常數 {name} 之右式非三形（字串字面／檔內巨集零引數呼叫／concat!）——得 "
                    f"{_offline_construct(rhs)}")


def _offline_sql_arg(where, d, idx, tok, consts):
    """本體 SQL 引數＝本檔 `const …: &str` 常數名或字串字面 → (來源, SQL)。"""
    if tok[0] == "str":
        return "字面", tok[1]
    if tok[0] == "id" and consts.get(tok[1]) is not None:
        return tok[1], consts[tok[1]]
    raise GateError(f"{where}：fn {d} 第 {idx} 句之 SQL 引數 {_rust_render([tok])} 非本檔 `const …: &str` "
                    "常數名或字串字面")


_OFFLINE_LET = ["let", "db", "=", "manager", ".", "get_connection", "(", ")"]
_OFFLINE_OK = ["Ok", "(", "(", ")", ")"]
_OFFLINE_AWAIT = [".", "await", "?"]


def _offline_body_stmt(where, d, idx, st, consts):
    """判準①c：up／down 本體一句恰四形——`let db = manager.get_connection()`、`expect_rows(db, "…", SQL, 整數,
    常數名).await?`（第三引數＝SQL；rustfmt 折行與尾逗號照收）、`db.execute_unprepared(SQL).await?`、`Ok(())`；
    回該句攜帶之 SQL 項（零或一項）。他句形＝GateError 指名句首（manager 他方法、db.execute／query_*、檔內他
    helper、format! 組 SQL 等）。"""
    s = [_tok_shape(t) for t in st]
    if s in (_OFFLINE_LET, _OFFLINE_OK):
        return []
    if len(st) >= 6 and s[-3:] == _OFFLINE_AWAIT:
        if s[:2] == ["expect_rows", "("] and _tok_close(st, 1) == len(st) - 4:
            a = _tok_args(st[2:-4])
            if (len(a) == 5 and [_tok_shape(t) for t in a[0]] == ["db"]
                    and [_tok_shape(t) for t in a[1]] == [_S_STR] and len(a[2]) == 1
                    and [_tok_shape(t) for t in a[3]] == [_S_NUM]
                    and all(c in _DIGITS for c in a[3][0][1])
                    and len(a[4]) == 1 and a[4][0][0] == "id"):
                return [_offline_sql_arg(where, d, idx, a[2][0], consts)]
        if s[:4] == ["db", ".", "execute_unprepared", "("] and _tok_close(st, 3) == len(st) - 4:
            a = _tok_args(st[4:-4])
            if len(a) == 1 and len(a[0]) == 1:
                return [_offline_sql_arg(where, d, idx, a[0][0], consts)]
    raise GateError(f"{where}：fn {d} 第 {idx} 句非四形（let db＝manager.get_connection()／expect_rows(…)／"
                    f"db.execute_unprepared(…)／Ok(())）——句首 {_rust_head(st)}")


_OFFLINE_HEAD = ["impl", "MigrationTrait", "for", "Migration", "{"]
_OFFLINE_PRELUDE = ["use", "sea_orm_migration", ":", ":", "prelude", ":", ":", "*", ";"]


def _offline_impl_binding(where, toks, depths, head):
    """判準①m（impl 綁定；fail-closed）：本腿只解析字面 head `impl MigrationTrait for Migration {`（詞素 head 起）之 up／down，
    遷移二進位所跑之 MigrationTrait 實作須即此 head——四款皆須成立，違者＝GateError 指名檔與款：①head 在檔案頂層（括號深度 0）、
    全檔 `impl` 詞素恰一＝head（拒限定路徑之 trait〔`impl sea_orm_migration::MigrationTrait for Migration`〕、他型別與 inherent 之
    impl、inline mod 與函式本體內之 impl、型別位置之 `impl Trait`——不辨用途、一律拒）②識別字 `MigrationTrait` 全檔恰一＝head、
    且頂層有 `use sea_orm_migration::prelude::*;`（拒 `use …::MigrationTrait`〔不改名之他路徑匯入亦改綁〕、`use … as MigrationTrait`、
    檔內 `trait MigrationTrait`、缺頂層 prelude 匯入〔他 glob 為唯一來源〕；與 prelude 並存之他 glob 同名＝編譯期歧義 E0659）
    ③識別字 `Migration` 全檔恰二＝頂層 `struct Migration` 與 head（拒 `use … as Migration`、`use …::Migration`、`type Migration`、
    他處第二 `struct Migration`、`struct Migration` 不在頂層——可改綁 head 與遷移向量所指之型別；不辨實際綁定、一律拒）
    ④識別字 `cfg`／`cfg_attr` 全檔零（`#[cfg]`、`#[cfg_attr]`、`#![cfg]`、`cfg!`）——head 與 struct 無條件編譯時，Rust 之衝突
    實作檢查（E0119）即排除 crate 內他處（含本腿不讀之他檔）同 trait 對同型之另一實作；cfg 互斥則二者並存、遷移二進位可跑他處者。
    識別字只認詞素（註解、字串字面與他識別字之一部分不計）。"""
    def at(i):
        return f"第 {toks[i][2]} 行"

    def ids(name):
        return [i for i, t in enumerate(toks) if t[:2] == ("id", name)]

    if depths[head]:
        raise GateError(f"{where}：impl 綁定——`impl MigrationTrait for Migration` 須在檔案頂層（{at(head)}在括號內）")
    for i in ids("impl"):
        if i != head:
            k = next((j for j in range(i + 1, min(len(toks), i + 12)) if toks[j][:2] == ("p", "{")), i + 6)
            raise GateError(f"{where}：impl 綁定——全檔 `impl` 詞素須恰一＝head；{at(i)}另有 {_rust_render(toks[i:k])}"
                            "（他實作可為遷移二進位所跑、本腿不解析）")
    for i in ids("MigrationTrait"):
        if i != head + 1:
            raise GateError(f"{where}：impl 綁定——識別字 MigrationTrait 須只出現於 head；{at(i)}另見"
                            "（匯入、改名或檔內定義可改綁 head 之 trait）")
    shapes = [_tok_shape(t) for t in toks]
    if not any(shapes[i:i + len(_OFFLINE_PRELUDE)] == _OFFLINE_PRELUDE and not depths[i] for i in range(len(toks))):
        raise GateError(f"{where}：impl 綁定——缺頂層 `use sea_orm_migration::prelude::*;`（head 之 MigrationTrait 須經之引入）")
    others = [i for i in ids("Migration") if i != head + 3]
    if len(others) != 1 or toks[others[0] - 1][:2] != ("id", "struct") or depths[others[0]]:
        got = "、".join(at(i) for i in others) or "無"
        raise GateError(f"{where}：impl 綁定——識別字 Migration 須恰二處＝頂層 `struct Migration` 與 head（head 之外：{got}；"
                        "use 匯入或改名、type 別名、他處之 struct 可改綁 head 與遷移向量所指之型別）")
    for i, t in enumerate(toks):
        if t[0] == "id" and t[1] in ("cfg", "cfg_attr"):
            raise GateError(f"{where}：impl 綁定——{at(i)}含 {t[1]}（head 與 struct Migration 須無條件編譯；cfg 互斥下 crate 內"
                            "他處〔含本腿不讀之他檔〕可另有實作）")


# ── SQL 詞素與分句 ────────────────────────────────────────────────────────────

def _sql_comment_end(sql, i, where):
    """判準①h（SQL 註解；同 PG 切法）：sql[i] 起為註解 → 註解迄（不含）；否＝None。`--` 至行尾（`\\n` 或 `\\r` 之前）；
    `/* */` 可巢狀（內層 `/*` 計深）、未閉合（含內層閉合而外層未閉合）＝GateError。註解切為單一註解詞素，其內之 `;`、
    引號與 `$` 不起詞素作用——否則註解內成對之引號會與後方字面錯配、把頂層 `;` 吞進「字串」而併句。"""
    if sql.startswith("--", i):
        j = i
        while j < len(sql) and sql[j] not in "\r\n":
            j += 1
        return j
    if not sql.startswith("/*", i):
        return None
    j, depth = i + 2, 1
    while depth:
        o, e = sql.find("/*", j), sql.find("*/", j)
        if e < 0:
            raise GateError(f"{where}：SQL 之塊註解未閉合")
        if 0 <= o < e:
            depth, j = depth + 1, o + 2
        else:
            depth, j = depth - 1, e + 2
    return j


def _sql_id_adjacent(sql, i):
    """sql[i] 之前一字元屬識別字字元（ASCII 字母、數字、底線；PG 另把非 ASCII 字元一律當識別字字元）＝True。"""
    return i > 0 and (sql[i - 1] in _ID_CONT or ord(sql[i - 1]) >= 0x80)


def _sql_unsupported(sql, i):
    """判準①g（未支援之 SQL 詞素；fail-closed）：sql[i]（`$` 或單引號）起之詞素於 PG 之切法與本詞素器不同 → 指名字串；
    否＝None。逐途徑：`$` 不成 `$$`＝標籤式 dollar 引號 `$<標籤>$` 或位置參數 `$<n>`；`$$` 緊貼識別字字元＝PG 將之併入
    該識別字；單引號緊貼識別字字元、或緊貼「識別字字元＋`&`」＝前綴字串 `E'…'`（`\\'` 為跳脫）、`U&'…'`、`B'…'`、`X'…'`、
    `N'…'`。其中 `$<標籤>$`、`$$` 緊貼識別字、`E'…'` 三形之配對與本詞素器錯位即可把頂層 `;` 吞進「字串」而併句；位置參數
    與他前綴形不致錯位，一律拒收以免另立值與型別規則（fail-closed）。"""
    if sql[i] == "$":
        if not sql.startswith("$$", i):
            return "`$` 不成 `$$`（標籤式 dollar 引號 `$<標籤>$`、位置參數 `$<n>`；只認未加標籤之 `$$`）"
        if _sql_id_adjacent(sql, i):
            return "`$$` 緊貼識別字字元（PG 將之併入該識別字、不起 dollar 引號）"
    elif _sql_id_adjacent(sql, i) or (sql[i - 1:i] == "&" and _sql_id_adjacent(sql, i - 1)):
        return "前綴字串（單引號緊貼識別字字元、或緊貼「識別字字元＋&」：E'…'、U&'…'、B'…'、X'…'、N'…' 等）"
    return None


def _sql_tokens(sql, where):
    """SQL → 詞素 [(類, 值, 起, 迄)]：w＝未加引號之詞（值為原文）／q＝雙引號識別字（解 `""`）／s＝單引號字串
    （解 `''`）／n＝整數／d＝`$$` 本體／c＝SQL 註解（[`_sql_comment_end`]；值為原文）／p＝標點（`::` 合一、他字元各一）。
    單引號、雙引號、`$$` 與塊註解未閉合＝GateError；未支援之 SQL 詞素（[`_sql_unsupported`]）＝GateError。註解所在句之判
    逐途徑（未分類／句形超出／不察）見檔頭 offline 射程外段。"""
    toks, i, n = [], 0, len(sql)
    while i < n:
        c = sql[i]
        end = _sql_comment_end(sql, i, where) if c in "-/" else None
        if end is not None:
            toks.append(("c", sql[i:end], i, end))
            i = end
            continue
        bad = _sql_unsupported(sql, i) if c in "$'" else None
        if bad:
            raise GateError(f"{where}：未支援之 SQL 詞素——{bad}")
        if c in " \t\r\n":
            i += 1
        elif c in _ID_START:
            j = i
            while j < n and sql[j] in _ID_CONT:
                j += 1
            toks.append(("w", sql[i:j], i, j))
            i = j
        elif c in _DIGITS:
            j = i
            while j < n and sql[j] in _DIGITS:
                j += 1
            toks.append(("n", sql[i:j], i, j))
            i = j
        elif c in "'\"":
            buf, j = [], i + 1
            while True:
                k = sql.find(c, j)
                if k < 0:
                    what = "字串" if c == "'" else "雙引號識別字"
                    raise GateError(f"{where}：SQL 之{what}未閉合")
                buf.append(sql[j:k])
                if sql.startswith(c, k + 1):
                    buf.append(c)
                    j = k + 2
                    continue
                break
            toks.append(("s" if c == "'" else "q", "".join(buf), i, k + 1))
            i = k + 1
        elif sql.startswith("$$", i):
            k = sql.find("$$", i + 2)
            if k < 0:
                raise GateError(f"{where}：SQL 之 $$ 本體未閉合")
            toks.append(("d", sql[i + 2:k], i, k + 2))
            i = k + 2
        elif sql.startswith("::", i):
            toks.append(("p", "::", i, i + 2))
            i += 2
        else:
            toks.append(("p", c, i, i + 1))
            i += 1
    return toks


def _offline_split_sql(sql, where):
    """SQL 依頂層 `;` 分句（單引號字串、雙引號識別字、`$$` 本體與 SQL 註解內不切；空句略過）→ [(句文, 詞素)]。"""
    out, cur = [], []
    for t in _sql_tokens(sql, where) + [("p", ";", len(sql), len(sql))]:
        if t[:2] == ("p", ";"):
            if cur:
                out.append((sql[cur[0][2]:cur[-1][3]], cur))
            cur = []
        else:
            cur.append(t)
    return out


def offline_parse_file(path):
    """判準①：一支 delta migration → {"up": [(來源, 句文, 詞素)…], "down": […]}——依呼叫序，來源＝常數名或「字面」，
    每項 SQL 依頂層 `;` 分句。SQL 之家只認兩條呼叫途徑（execute_unprepared 之引數、expect_rows 之第三引數）；
    未被 up／down 引用之 `&str` 常數不入序列（右式三形之判照做）；檔內 helper 本體（expect_rows）只認其名、不掃其體。"""
    where = os.path.basename(path)
    with open(path, encoding="utf-8") as fh:
        toks = _rust_tokens(fh.read(), where)
    shapes = [_tok_shape(t) for t in toks]
    _offline_foreign_scope(where, toks)
    depths, depth = [], 0              # 各詞素所在之括號深度（判準①k 之頂層判定）
    for t in toks:
        if t[0] == "p" and t[1] in ")]}":
            depth -= 1
        depths.append(depth)
        if t[0] == "p" and t[1] in "([{":
            depth += 1
    macros = {}
    for i in range(len(toks) - 2):
        if shapes[i:i + 2] == ["macro_rules", "!"] and toks[i + 2][0] == "id":
            name = toks[i + 2][1]
            end = _tok_close(toks, i + 3) if shapes[i + 3:i + 4] == ["{"] else None
            if end is None:
                raise GateError(f"{where}：macro_rules! {name} 本體非 `{{ … }}` 形或括號未配對")
            _offline_unique_name(where, "macro_rules!", name, macros)
            macros[name] = (_offline_macro_body(where, name, toks[i + 4:end]), i, depths[i])
    expansions = {name: v[0] for name, v in macros.items()}
    consts = {}
    for i in range(len(toks) - 2):
        if shapes[i] == "const" and toks[i + 1][0] == "id" and shapes[i + 2] == ":":
            name = toks[i + 1][1]
            eq = _tok_find(toks, i + 3, "=;")
            semi = None if eq is None or shapes[eq] != "=" else _tok_find(toks, eq + 1, ";")
            if semi is None:
                raise GateError(f"{where}：常數 {name} 之宣告不完整（缺 `=` 或 `;`）")
            _offline_unique_name(where, "常數", name, consts)
            if shapes[i + 3:eq] == ["&", "str"]:
                _offline_macro_reach(where, name, toks[eq + 1:semi], macros, i)
                consts[name] = _offline_const_rhs(where, name, toks[eq + 1:semi], expansions)
            else:
                consts[name] = None       # 非 &str 常數：不得充 SQL 引數
    heads = [i for i in range(len(toks) - 4) if shapes[i:i + 5] == _OFFLINE_HEAD]
    if len(heads) != 1:
        raise GateError(f"{where}：`impl MigrationTrait for Migration` 須恰一（得 {len(heads)}）")
    _offline_impl_binding(where, toks, depths, heads[0])
    end = _tok_close(toks, heads[0] + 4)
    if end is None:
        raise GateError(f"{where}：impl MigrationTrait 本體括號未配對")
    body = toks[heads[0] + 5:end]
    bshapes = shapes[heads[0] + 5:end]
    out = {}
    for d in ("up", "down"):
        hits = [k for k in range(len(body) - 2) if bshapes[k:k + 3] == ["async", "fn", d]]
        if len(hits) != 1:
            raise GateError(f"{where}：impl MigrationTrait 內 `async fn {d}` 須恰一（得 {len(hits)}）")
        lb = next((k for k in range(hits[0] + 3, len(body)) if bshapes[k] == "{"), None)
        rb = None if lb is None else _tok_close(body, lb)
        if rb is None:
            raise GateError(f"{where}：fn {d} 本體未找到或括號未配對")
        items, idx = [], 0
        for st in _tok_split(body[lb + 1:rb], ";"):
            if not st:
                continue
            idx += 1
            for src, sql in _offline_body_stmt(where, d, idx, st, consts):
                for text, stoks in _offline_split_sql(sql, f"{where} fn {d} 第 {idx} 句（{src}）"):
                    items.append((src, text, stoks))
        out[d] = items
    return out


def offline_parse_tree(root):
    """判準①全程：delta 檔集（判準⑦：零支＝GateError）→ [(檔名主幹, offline_parse_file 結果)…]，依四碼升冪。"""
    paths = offline_delta_files(root)
    _offline_assert_nonempty(paths, root)
    return [(os.path.basename(p)[:-3], offline_parse_file(p)) for p in paths]


# ── 判準②：語句分類（seed DML／序列／權限面；他形＝未分類）─────────────────────

def _sql_ident(t):
    """識別字詞素 → 名（未加引號者轉小寫＝PG 摺疊、雙引號者原樣）；非識別字＝None。"""
    if t[0] == "w":
        return t[1].lower()
    if t[0] == "q":
        return t[1]
    return None


def _sql_head(text, limit=60):
    """句首回顯（訊息指名用）。"""
    return text if len(text) <= limit else text[:limit] + "…"


def _offline_narrowed_table(table):
    """判準④（收窄表 DML 排除）：表屬 RUNTIME_APPEND_TABLES＝True——收窄表之 seed 必空，對其之 DML 一律未分類。"""
    return table in RUNTIME_APPEND_TABLES


def _offline_seed_table(table, seed_tables):
    """判準④b（seed 表成員）：DML 之標的（`INSERT INTO`／`DELETE FROM` 後、`UPDATE` 後之首詞素，依 [`_sql_ident`] 摺疊）屬凍結
    seed.sql 有 COPY 段之表＝True。否＝該句未分類，逐途徑：凍結 seed 外之表名（seaql_migrations 等）、schema 限定名
    `public.<表>`（首詞素為 schema 名 public）。"""
    return table in seed_tables


# CREATE ROLE 選項尾段白名單（裸形與 DO 包裝形同判）：只收 PG 預設值或減權之單詞屬性——以之建出之角色能力不逾預設，
# 權限面列出（角色集與受權物件）即完整。角色成員子句、提權或連線屬性、多詞選項與 SQL 註解詞素皆不在此集＝該句未分類。
_OFFLINE_ROLE_OPTIONS = frozenset({"NOLOGIN", "NOSUPERUSER", "NOCREATEDB", "NOCREATEROLE", "NOREPLICATION",
                                   "NOBYPASSRLS", "INHERIT", "NOINHERIT"})


def _offline_role_options(opts):
    """判準②b（CREATE ROLE 選項尾段）：`<角色>` 之後之詞素全為 [`_OFFLINE_ROLE_OPTIONS`] 之詞（不分大小寫；可零個）＝True。
    白名單外逐途徑＝False：角色成員子句（IN ROLE／IN GROUP／ROLE／USER／ADMIN）、白名單外屬性詞（SUPERUSER／CREATEDB／
    CREATEROLE／REPLICATION／BYPASSRLS／LOGIN）、WITH、SYSID、CONNECTION LIMIT、[ENCRYPTED] PASSWORD、VALID UNTIL、
    引號形屬性詞（`"…"`、`'…'`；只收未加引號之詞）、SQL 註解（`--`、`/* */` 切為註解詞素）。"""
    return all(t[0] == "w" and t[1].upper() in _OFFLINE_ROLE_OPTIONS for t in opts)


_OFFLINE_DO_CREATE_TAIL = [";", "EXCEPTION", "WHEN", "DUPLICATE_OBJECT", "THEN", "NULL", ";", "END"]
_OFFLINE_DO_DROP_HEAD = ["BEGIN", "DROP", "ROLE", "IF", "EXISTS"]
_OFFLINE_DO_DROP_TAIL = [";", "EXCEPTION", "WHEN", "DEPENDENT_OBJECTS_STILL_EXIST", "THEN", "RAISE", "NOTICE",
                         _S_STR, ";", "END"]


def _offline_do_block(body, where):
    """判準③（`DO $$ … $$` 嚴格形）：本體恰兩形（詞素比對＝空白正規化、關鍵字不分大小寫）——
    `BEGIN CREATE ROLE <角色> <選項詞…>; EXCEPTION WHEN duplicate_object THEN NULL; END`（選項詞至少一個、全屬
    [`_offline_role_options`] 白名單）、
    `BEGIN DROP ROLE IF EXISTS <角色>; EXCEPTION WHEN dependent_objects_still_exist THEN RAISE NOTICE '<訊息>'; END`；
    回權限面細目，他形（含塊內藏 DML）＝None。"""
    t = _sql_tokens(body, where)
    s = [_tok_shape(x) for x in t]
    if len(t) >= 13 and s[:3] == ["BEGIN", "CREATE", "ROLE"] and s[-8:] == _OFFLINE_DO_CREATE_TAIL:
        role, opts = t[3], t[4:-8]
        if _sql_ident(role) and _offline_role_options(opts):
            return {"kind": "CREATE ROLE", "role": _sql_ident(role), "objects": {}}
    if len(t) == 16 and s[:5] == _OFFLINE_DO_DROP_HEAD and s[6:] == _OFFLINE_DO_DROP_TAIL and _sql_ident(t[5]):
        return {"kind": "DROP ROLE", "role": _sql_ident(t[5]), "objects": {}}
    return None


_OFFLINE_GRANT_OBJECT_KINDS = ("TABLE", "SEQUENCE", "SCHEMA")


def _offline_grant(toks, s):
    """`GRANT <權限>[, …] ON [TABLE |SEQUENCE |SCHEMA ]<物件>[, …] TO <角色>`／同形 `REVOKE … FROM <角色>`；
    權限與物件皆單詞、角色恰一、句尾無他詞 → 細目；他形（無 ON＝角色成員授予、ON ALL … IN SCHEMA、
    WITH GRANT OPTION、欄級權限、多詞權限、限定名物件、CASCADE 等）＝None。"""
    if "ON" not in s:
        return None
    on = s.index("ON")
    privs = _tok_split(toks[1:on], ",")
    if not all(len(p) == 1 and p[0][0] == "w" for p in privs):
        return None
    j = on + 1
    kind = "TABLE"
    if s[j:j + 1] and s[j] in _OFFLINE_GRANT_OBJECT_KINDS:
        kind, j = s[j], j + 1
    to = "TO" if s[0] == "GRANT" else "FROM"
    if to not in s[j:]:
        return None
    k = s.index(to, j)
    objs = _tok_split(toks[j:k], ",")
    if (not all(len(p) == 1 and _sql_ident(p[0]) for p in objs)
            or len(toks) != k + 2 or not _sql_ident(toks[k + 1])):
        return None
    granted = {p[0][1].upper() for p in privs}
    return {"kind": s[0], "role": _sql_ident(toks[k + 1]),
            "objects": {(kind, _sql_ident(p[0])): set(granted) for p in objs}}


def _offline_perm(toks, s, where):
    """權限面五形（GRANT／REVOKE、裸 CREATE ROLE <角色> [白名單屬性詞…]〔[`_offline_role_options`]〕、
    DROP ROLE [IF EXISTS] <角色>、DO 包裝兩形）→ 細目；否＝None。"""
    if s[:1] in (["GRANT"], ["REVOKE"]):
        return _offline_grant(toks, s)
    if s[:2] == ["CREATE", "ROLE"] and len(toks) >= 3 and _sql_ident(toks[2]) and _offline_role_options(toks[3:]):
        return {"kind": "CREATE ROLE", "role": _sql_ident(toks[2]), "objects": {}}
    if s[:2] == ["DROP", "ROLE"]:
        rest = toks[4:] if s[2:4] == ["IF", "EXISTS"] else toks[2:]
        if len(rest) == 1 and _sql_ident(rest[0]):
            return {"kind": "DROP ROLE", "role": _sql_ident(rest[0]), "objects": {}}
        return None
    if s == ["DO", "\0d"]:
        return _offline_do_block(toks[1][1], where)
    return None


def _offline_classify(toks, seed_tables, where):
    """判準②之分類器：一句 → (類, 細目)，未分類＝(None, None)。類恰三：
    seed DML＝`INSERT INTO`／`UPDATE`／`DELETE FROM` 且標的表屬凍結 seed.sql 有 COPY 段之表、不屬收窄表（細目＝表）；
    序列＝`SELECT setval('<序列>', …)` 整句即該呼叫（細目＝序列名）；權限面＝[`_offline_perm`] 五形（細目＝kind／role／objects）。"""
    s = [_tok_shape(t) for t in toks]
    if s[:2] in (["INSERT", "INTO"], ["DELETE", "FROM"]) or s[:1] == ["UPDATE"]:
        pos = 1 if s[0] == "UPDATE" else 2
        table = _sql_ident(toks[pos]) if len(toks) > pos else None
        if _offline_seed_table(table, seed_tables) and not _offline_narrowed_table(table):
            return "seed DML", table
        return None, None
    if s[:3] == ["SELECT", "SETVAL", "("] and s[3:5] == [_S_STR, ","] and _tok_close(toks, 2) == len(toks) - 1:
        return "序列", toks[3][1]
    perm = _offline_perm(toks, s, where)
    return ("權限面", perm) if perm else (None, None)


def _offline_classify_findings(stmts):
    """判準②（未分類即紅）：未分類句逐句一筆 finding（rc 1），指名檔、方向、序號、來源與句首。"""
    return [f"[offline·分類] {x['at']} 未分類——句首「{_sql_head(x['text'])}」（只認 seed DML／序列 setval／"
            "權限面〔GRANT／REVOKE／CREATE ROLE／DROP ROLE／DO 包裝兩形〕；結構演進之 DDL 須擴本腿）"
            for x in stmts if x["cat"] is None]


# ── 判準③：seed DML 句形與展開 ─────────────────────────────────────────────────

_SQL_LITERAL_WORDS = {"TRUE": True, "FALSE": False, "NULL": None}


class _SqlCast(str):
    """`'…'::<型>` 字面之值：str 本體＝引號內原文（`''` 已解）、`cast`＝型詞原文（單詞）。值比較時由 [`_offline_value`]
    以判準①i [`_offline_cast_ok`] 核轉型之型與欄型同族；他處照字串用。"""

    def __new__(cls, text, cast):
        obj = super().__new__(cls, text)
        obj.cast = cast
        return obj


def _sql_literal(part):
    """一段詞素恰為一字面 → (值,)；否＝None。字面＝整數（可帶負號）、單引號字串（`''` 已解）、TRUE／FALSE／NULL、
    `'…'::<型>`（型為單詞；值為 [`_SqlCast`]＝攜型詞，轉型之型須與欄型同族〔判準①i〕、值依欄型正規化）。"""
    s = [_tok_shape(t) for t in part]
    if s == [_S_NUM]:
        return (int(part[0][1]),)
    if s == ["-", _S_NUM]:
        return (-int(part[1][1]),)
    if len(part) == 1 and part[0][0] == "w" and s[0] in _SQL_LITERAL_WORDS:
        return (_SQL_LITERAL_WORDS[s[0]],)
    if s == [_S_STR]:
        return (part[0][1],)
    if len(part) == 3 and s[:2] == [_S_STR, "::"] and part[2][0] == "w":
        return (_SqlCast(part[0][1], part[2][1]),)
    return None


def _sql_where(toks):
    """WHERE 條件串（深度 0 之 AND 相接）→ (等值 {欄: 值}, 元組 IN〔(欄序, [值列…]) 或 None〕)；條件三形＝
    `<欄> = <非 NULL 字面>`、`<欄> IS NULL`、`(<欄>, …) IN ((<非 NULL 字面>, …), …)`（至多一個）；欄重複或他形＝None。
    `<欄> = NULL` 與元組含 NULL 亦屬他形：SQL 之 `= NULL` 恆不成立、該列不匹配，當 IS NULL 比前值即假綠。"""
    conds, depth = [[]], 0
    for t in toks:
        depth += (t[:2] == ("p", "(")) - (t[:2] == ("p", ")"))
        if depth == 0 and _tok_shape(t) == "AND":
            conds.append([])
        else:
            conds[-1].append(t)
    eq, tin, seen = {}, None, []
    for c in conds:
        s = [_tok_shape(t) for t in c]
        col = _sql_ident(c[0]) if c else None
        lit = _sql_literal(c[2:]) if col and len(c) >= 3 and s[1] == "=" else None
        if lit is not None and lit[0] is not None:
            eq[col] = lit[0]
            seen.append(col)
        elif col and s[1:] == ["IS", "NULL"]:
            eq[col] = None
            seen.append(col)
        elif s[:1] == ["("] and tin is None:
            e = _tok_close(c, 0)
            if e is None or s[e + 1:e + 3] != ["IN", "("] or _tok_close(c, e + 2) != len(c) - 1:
                return None
            cols = [_sql_ident(p[0]) if len(p) == 1 else None for p in _tok_split(c[1:e], ",")]
            rows = []
            for tp in _tok_split(c[e + 3:-1], ","):
                if not tp or tp[0][:2] != ("p", "(") or _tok_close(tp, 0) != len(tp) - 1:
                    return None
                vals = [_sql_literal(p) for p in _tok_split(tp[1:-1], ",")]
                if None in vals or (None,) in vals or len(vals) != len(cols):
                    return None
                rows.append([v[0] for v in vals])
            if None in cols:
                return None
            tin = (cols, rows)
            seen += cols
        else:
            return None
    if len(seen) != len(set(seen)):
        return None
    return eq, tin


def _offline_dml_records(st, pk_cols):
    """判準①d（SQL 句形與 pk 定住；只 up 方向之 seed DML）：句形恰三種——
    `INSERT INTO <表> (<欄>, …) VALUES (<字面>, …)[, (…)]`、`UPDATE <表> SET <欄> = <字面>[, …] WHERE <條件>[ AND …]`、
    `DELETE FROM <表> WHERE <條件>[ AND …]`（條件見 [`_sql_where`]）；INSERT 欄清單與 WHERE（`=` 或元組 IN）須定住該表
    全部 pk 欄，元組 IN 每一元組展開為一筆。回展開筆 [{kind, table, pk, values|set, where（非 pk 欄）, at}]；
    句形超出或 pk 未定住＝GateError 指名。"""
    toks, s, table = st["toks"], [_tok_shape(t) for t in st["toks"]], st["info"]

    def bad(why):
        raise GateError(f"{st['at']}：seed DML {why}——句首「{_sql_head(st['text'])}」")

    shape_err = ("句形超出三形（INSERT … (欄…) VALUES (字面…)／UPDATE … SET 欄 = 字面 … WHERE …／"
                 "DELETE FROM … WHERE …；條件只認 = 非 NULL 字面、IS NULL、元組 IN〔元組不含 NULL〕——比空值須寫 IS NULL）")
    base = {"table": table, "at": st["at"]}
    if s[0] == "INSERT":
        e = _tok_close(toks, 3) if s[3:4] == ["("] else None
        cols = [_sql_ident(p[0]) if len(p) == 1 else None for p in _tok_split(toks[4:e], ",")] if e else [None]
        if None in cols or len(set(cols)) != len(cols) or s[e + 1:e + 2] != ["VALUES"]:
            bad(shape_err)
        rows, i = [], e + 2
        while True:
            e2 = _tok_close(toks, i) if s[i:i + 1] == ["("] else None
            vals = [_sql_literal(p) for p in _tok_split(toks[i + 1:e2], ",")] if e2 else [None]
            if None in vals or len(vals) != len(cols):
                bad(shape_err)
            rows.append(dict(zip(cols, [v[0] for v in vals])))
            i = e2 + 1
            if i == len(toks):
                break
            if s[i] != ",":
                bad(shape_err)
            i += 1
        missing = [c for c in pk_cols if c not in cols]
        if missing:
            bad(f"INSERT 欄清單未定住 {table} 全部 pk 欄 {pk_cols}（缺 {missing}）")
        return [dict(base, kind="seed_add", pk={c: r[c] for c in pk_cols}, values=r, where={}) for r in rows]
    if s[0] == "UPDATE":
        w = s.index("WHERE") if "WHERE" in s else None
        sets = {}
        for p in (_tok_split(toks[3:w], ",") if w and s[2:3] == ["SET"] else [[]]):
            col = _sql_ident(p[0]) if p else None
            lit = _sql_literal(p[2:]) if len(p) >= 3 and _tok_shape(p[1]) == "=" else None
            if col is None or lit is None or col in sets:
                bad(shape_err)
            sets[col] = lit[0]
        cond = _sql_where(toks[w + 1:])
    else:
        cond = _sql_where(toks[4:]) if s[3:4] == ["WHERE"] else None
    if cond is None:
        bad(shape_err)
    eq, tin = cond
    missing = [c for c in pk_cols if c not in eq and c not in (tin[0] if tin else ())]
    if missing:
        bad(f"WHERE 未以 `=` 或元組 IN 定住 {table} 全部 pk 欄 {pk_cols}（缺 {missing}）")
    combos = [{**eq, **dict(zip(tin[0], row))} for row in tin[1]] if tin else [dict(eq)]
    out = []
    for c in combos:
        rec = dict(base, pk={k: c[k] for k in pk_cols}, where={k: v for k, v in c.items() if k not in pk_cols})
        out.append(dict(rec, kind="seed_update", set=sets) if s[0] == "UPDATE" else dict(rec, kind="seed_delete"))
    return out


# ── 值正規化（依凍結 columns.json 欄型；③④ 共用）────────────────────────────────

_OFFLINE_FAMILIES = {"bigint": "int", "integer": "int", "smallint": "int", "boolean": "bool",
                     "text": "str", "character varying": "str", TS_TZ: "ts", "jsonb": "jsonb"}


def _offline_family(coltype):
    """判準①e（欄型未支援）：凍結 columns.json 欄型 → 值正規化族（int／bool／str／ts／jsonb；`character varying(n)`
    歸 str）；他欄型＝None（呼叫端轉 GateError 指名）。"""
    if coltype.startswith("character varying(") and coltype.endswith(")"):
        return "str"
    return _OFFLINE_FAMILIES.get(coltype)


# 判準①i（轉型之型與欄型同族）：型詞 → 值正規化族。PG 先依轉型之型解析字面、再以指派轉型落欄——異族時落值可≠字面
# （`::char` 截為 character(1)、jsonb 經 I/O 轉文字重排鍵並補空白、timestamptz 依 session 時區重輸出、`::timestamp`
# 丟棄 offset 再依 session 時區解讀落 timestamptz）。同族型詞與無轉型之字面同受判準①l（[`_offline_pg_exact`]）所核之
# 兩途徑：character varying(n) 欄值逾長、timestamptz 小數秒逾六位；數值溢位於遷移套用時報錯、非靜默改值。
_OFFLINE_CAST_FAMILIES = {"bigint": "int", "int8": "int", "integer": "int", "int": "int", "int4": "int",
                          "smallint": "int", "int2": "int", "boolean": "bool", "bool": "bool",
                          "text": "str", "varchar": "str", "timestamptz": "ts", "jsonb": "jsonb"}


def _offline_cast_ok(cast, fam):
    """判準①i：轉型之型詞（大小寫不敏感）屬欄型之值正規化族 fam＝True；他族與表外型詞（char、bpchar、name、json、
    timestamp、date、numeric 等）＝False（呼叫端轉 GateError＝rc 2）。"""
    return _OFFLINE_CAST_FAMILIES.get(cast.lower()) == fam


_OFFLINE_VARCHAR_N = "character varying("


def _offline_pg_exact(coltype, fam, v):
    """判準①l（PG 落值≠字面之值；fail-closed）：字串值 v 指派入該欄時 PG 會靜默改值、本腿正規化又與之不同者 → 指名途徑；
    否＝None。逐途徑：①character varying(n) 欄值長度（字元數）逾 n——PG 於超出部分全為空白時靜默截斷至 n、否則報錯，本腿
    不分二者一律拒收 ②timestamptz 值之小數秒（`.` 後之數字）逾六位——PG 依 rint 進位至微秒、datetime.fromisoformat 截斷，
    兩側落值不同。text 與無長度之 character varying 不限長；非字串值不察。"""
    if not isinstance(v, str):
        return None
    if fam == "str" and coltype.startswith(_OFFLINE_VARCHAR_N) and coltype.endswith(")"):
        n = int(coltype[len(_OFFLINE_VARCHAR_N):-1])
        if len(v) > n:
            return f"逾欄長 {n}（得 {len(v)} 字元；PG 於超出部分全為空白時靜默截斷、否則報錯）"
    if fam == "ts":
        for i, c in enumerate(v):
            if c == ".":
                k = i + 1
                while k < len(v) and v[k] in _DIGITS:
                    k += 1
                if k - i - 1 > 6:
                    return f"小數秒逾六位（得 {k - i - 1} 位；PG 依 rint 進位至微秒、本腿之解析截斷）"
    return None


def _offline_jsonb(x):
    """json.loads 結果 → 比較形：布林換為帶標記之二元組（Python 之 True == 1、False == 0，PG jsonb 之 true 與 1 不等）；
    串列與物件逐層遞迴、他值原樣（二元組不與 JSON 陣列所解之 list 相等，標記不撞任何 JSON 值）。"""
    if isinstance(x, bool):
        return ("\0bool", x)
    if isinstance(x, list):
        return [_offline_jsonb(y) for y in x]
    if isinstance(x, dict):
        return {k: _offline_jsonb(y) for k, y in x.items()}
    return x


def _offline_value(types, table, col, v):
    """一值依凍結 columns.json 該欄欄型正規化：整數族→int（容十進位字串）；boolean→bool（容 COPY t／f）；文字族→str；
    timestamptz→帶時區時刻（ISO 與 COPY 形同值、無時區＝不收）；jsonb→JSON 解析後語意（[`_offline_jsonb`]：布林與數字
    不同值；小數以 decimal.Decimal 解析＝依十進位值比、同 PG numeric）。None（SQL NULL／COPY `\\N`／JSON null）不查欄型。
    `'…'::<型>` 之值（[`_SqlCast`]）先核型詞與欄型同族（判準①i [`_offline_cast_ok`]），字串值再核 PG 落值＝此值（判準①l
    [`_offline_pg_exact`]）。凍結面無此欄、欄型未支援、轉型之型與欄型不同族、PG 落值≠此值、值不合欄型＝GateError（rc 2）。"""
    if v is None:
        return None
    coltype = types.get((table, col))
    if coltype is None:
        raise GateError(f"{table}.{col} 不在凍結 columns.json——offline 值比較之欄型無從得知"
                        "（結構演進之欄須擴本腿）")
    fam = _offline_family(coltype)
    if fam is None:
        raise GateError(f"{table}.{col} 之欄型 {coltype!r} 未支援（offline 值正規化只認整數族、boolean、文字族、"
                        "timestamptz、jsonb）")
    if isinstance(v, _SqlCast) and not _offline_cast_ok(v.cast, fam):
        raise GateError(f"{table}.{col}（{coltype}）之值 {str(v)!r} 帶轉型 ::{v.cast}，轉型之型與欄型不同族——句形超出"
                        "（PG 依轉型之型解析後指派落欄、落值可≠字面；同族型詞：整數族 bigint／int8／integer／int／int4"
                        "／smallint／int2、boolean／bool、文字族 text／varchar、timestamptz、jsonb）")
    inexact = _offline_pg_exact(coltype, fam, v)
    if inexact:
        raise GateError(f"{table}.{col}（{coltype}）之值 {str(v)!r} {inexact}——PG 落值≠此值、拒收（判準①l）")
    try:
        if fam == "int" and isinstance(v, (int, str)) and not isinstance(v, bool):
            return int(v)
        if fam == "bool" and isinstance(v, bool):
            return v
        if fam == "bool" and v in ("t", "f"):
            return v == "t"
        if fam == "str" and isinstance(v, str):
            return v
        if fam == "ts" and isinstance(v, str):
            ts = datetime.datetime.fromisoformat(v)
            if ts.tzinfo is not None:
                return ts
        if fam == "jsonb" and isinstance(v, str):
            return _offline_jsonb(json.loads(v, parse_float=decimal.Decimal))
    except ValueError:
        pass
    raise GateError(f"{table}.{col}（{coltype}）之值 {v!r} 無法正規化")


_COPY_ESCAPES = {"\\": "\\", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v"}


def _copy_value(cell):
    """COPY text 格 → python 值：`\\N`＝None；反斜線跳脫還原（pg_dump 文字輸出之七形；他形＝GateError）。"""
    if cell == "\\N":
        return None
    out, i = [], 0
    while i < len(cell):
        if cell[i] != "\\":
            out.append(cell[i])
            i += 1
            continue
        e = cell[i + 1:i + 2]
        if e not in _COPY_ESCAPES:
            raise GateError(f"COPY 格含未支援之跳脫 \\{e}（{cell[:40]!r}）")
        out.append(_COPY_ESCAPES[e])
        i += 2
    return "".join(out)


def _offline_pk_map(fixtures):
    """凍結 constraints.json 之 `PRIMARY KEY (…)` → {表: [pk 欄…]}。"""
    out = {}
    for r in fixtures["constraints"]:
        d = r["definition"]
        if d.startswith("PRIMARY KEY (") and d.endswith(")"):
            out[r["table"]] = [c.strip().strip('"') for c in d[len("PRIMARY KEY ("):-1].split(",")]
    return out


def _offline_pk_cols(pk_map, table):
    if table not in pk_map:
        raise GateError(f"表 {table} 於凍結 constraints.json 無 PRIMARY KEY——offline 無從定列")
    return pk_map[table]


# ── 判準③④⑧：配對、對賬、前值、前序配對合成 ─────────────────────────────────────

def _offline_rec_key(rec, types):
    return (rec["kind"], rec["table"],
            tuple(sorted((c, _offline_value(types, rec["table"], c, v)) for c, v in rec["pk"].items())))


def _offline_entry_key(e, pk_map, types):
    """登記之鍵（kind、表、pk）：seed_add 取 values 中該表 pk 欄之值；seed_update／seed_delete 取 detail.pk 全部欄。"""
    t, d = e["table"], e["detail"]
    if e["kind"] == "seed_add":
        pk = {c: d["values"].get(c) for c in _offline_pk_cols(pk_map, t)}
    else:
        pk = d["pk"]
    return (e["kind"], t, tuple(sorted((c, _offline_value(types, t, c, v)) for c, v in pk.items())))


def _offline_pair(recs, segment, pk_map, types):
    """一支 delta 之展開筆與其帳段依（kind、表、pk）配對（同鍵多筆依序配）→ (配對 [(筆, 登記)], 落單筆, 落單登記)。"""
    pool = {}
    for e in segment:
        pool.setdefault(_offline_entry_key(e, pk_map, types), []).append(e)
    pairs, lone = [], []
    for r in recs:
        q = pool.get(_offline_rec_key(r, types))
        if q:
            pairs.append((r, q.pop(0)))
        else:
            lone.append(r)
    used = {id(e) for _r, e in pairs}
    return pairs, lone, [e for e in segment if id(e) not in used]


def _offline_pk_text(pk):
    return "、".join(f"{c}={v!r}" for c, v in pk.items())


def _offline_ledger_findings(pairs, lone_recs, lone_entries, pk_map, types):
    """判準⑤（③款：seed DML ↔ 演進帳逐筆）：配對者比 seed_add 之 pk 欄名清單（須＝該表 pk 欄）與 values 全欄、
    seed_update 之 set 欄集與值；落單之句（未登）與落單之登記（多出）逐一指名。回 findings（rc 1）。"""
    out = []
    for r, e in pairs:
        t, d = e["table"], e["detail"]
        tag = f"[offline·對賬] {e['id']}（{e['kind']} {t} {_offline_pk_text(r['pk'])}；{r['at']}）"
        if e["kind"] == "seed_add":
            if d["pk"] != _offline_pk_cols(pk_map, t):
                out.append(f"{tag}｜pk 欄名清單＝{d['pk']}、該表 pk 欄＝{_offline_pk_cols(pk_map, t)}")
            mine, theirs = r["values"], d["values"]
        elif e["kind"] == "seed_update":
            mine, theirs = r["set"], d["set"]
        else:
            continue
        for c in sorted(set(mine) | set(theirs)):
            if c not in theirs:
                out.append(f"{tag}｜欄 {c}：migration 有、演進帳缺")
            elif c not in mine:
                out.append(f"{tag}｜欄 {c}：演進帳有、migration 缺")
            elif _offline_value(types, t, c, mine[c]) != _offline_value(types, t, c, theirs[c]):
                out.append(f"{tag}｜欄 {c}：migration＝{mine[c]!r}、演進帳＝{theirs[c]!r}")
    for r in lone_recs:
        out.append(f"[offline·對賬] 未登之句：{r['at']} {r['kind']} {r['table']} {_offline_pk_text(r['pk'])}"
                   "——演進帳無對應之 seed_* 登記")
    for e in lone_entries:
        out.append(f"[offline·對賬] 多出之登記 {e['id']}（{e['kind']} {e['table']}）——delta migration 無對應之句")
    return out


def _offline_left_row(left, rec, types):
    """左源（normalize 後 seed 文字）中 rec 所指 pk 之列 → {欄: COPY 解碼值}（未正規化）；表無 COPY 段或 pk 不命中＝None。"""
    lines = left.splitlines()
    blocks = _copy_blocks(lines)
    if rec["table"] not in blocks:
        return None
    t = rec["table"]
    cols, start, end = blocks[t]
    want = {c: _offline_value(types, t, c, v) for c, v in rec["pk"].items()}
    for ln in lines[start:end]:
        row = dict(zip(cols, map(_copy_value, ln.split("\t"))))
        if all(_offline_value(types, t, c, row.get(c)) == w for c, w in want.items()):
            return row
    return None


def _offline_prevalue_findings(rec, row, types):
    """判準⑥（④款：前值 ↔ 凍結 seed ⊕ 前序配對登記；只 up 方向之 UPDATE／DELETE）：WHERE 所列非 pk 欄（含元組 IN 之
    非 pk 位與 IS NULL）逐欄須等於左源該 pk 列之值——不要求 WHERE 列全欄；pk 不命中左源亦紅。回 findings（rc 1）。"""
    tag = f"[offline·前值] {rec['at']} {rec['kind']} {rec['table']} {_offline_pk_text(rec['pk'])}"
    if row is None:
        return [f"{tag}｜pk 不命中左源（凍結 seed ⊕ 前序已配對之登記）"]
    out = []
    for c, v in rec["where"].items():
        want = _offline_value(types, rec["table"], c, v)
        if c not in row or _offline_value(types, rec["table"], c, row[c]) != want:
            out.append(f"{tag}｜欄 {c}：WHERE＝{v!r}、左源＝{row.get(c)!r}")
    return out


def _offline_advance_left(left, entry):
    """判準⑧（前序配對合成）：把一筆已配對之登記經既有 [`apply_seed_entries`] 疊上左源——其後之句（含後序 delta）
    改到同列時，前值即其改後值。"""
    return apply_seed_entries(left, [entry])


def offline_report(root):
    """offline 全程（純讀檔、零 docker）→ (findings, 摘要)；結構異常（解析他形、句形超出、fixtures 或演進帳缺席壞形、
    比對面為空）＝GateError（rc 2）。摘要＝{files, stmts{檔: {方向: Counter(類)}}, perm{檔: {方向: {kinds, roles,
    objects}}}, pair_ids, prev}。"""
    tree = offline_parse_tree(root)
    ledger = load_ledger(root)
    fixtures = load_fixtures(root)
    frozen = normalize_seed_dump(fixtures["seed"])
    seed_tables = set(_copy_blocks(frozen.splitlines()))
    types = {(c["table"], c["column"]): c["type"] for c in fixtures["columns"]}
    pk_map = _offline_pk_map(fixtures)
    entries = [e for e in ledger["entries"] if e["kind"].startswith("seed_")]
    findings, pairs_all, lone_recs, lone_entries = [], [], [], []
    summary = {"files": [], "stmts": {}, "perm": {}, "pair_ids": [], "prev": 0}
    left, cursor = frozen, 0
    for name, parsed in tree:
        stmts, recs = [], []
        summary["files"].append(name)
        summary["stmts"][name] = {}
        summary["perm"][name] = {}
        for d in ("up", "down"):
            counts = collections.Counter()
            perm = {"kinds": collections.Counter(), "roles": set(), "objects": {}}
            for n, (src, text, toks) in enumerate(parsed[d], 1):
                at = f"{name}.rs {d} 第 {n} 句（{src}）"
                cat, info = _offline_classify(toks, seed_tables, at)
                st = {"at": at, "text": text, "toks": toks, "cat": cat, "info": info}
                stmts.append(st)
                counts[cat or "未分類"] += 1
                if cat == "權限面":
                    perm["kinds"][info["kind"]] += 1
                    perm["roles"].update({info["role"]} - {None})
                    for obj, privs in info["objects"].items():
                        perm["objects"].setdefault(obj, set()).update(privs)
                if cat == "seed DML" and d == "up":
                    recs += _offline_dml_records(st, _offline_pk_cols(pk_map, info))
            summary["stmts"][name][d] = counts
            summary["perm"][name][d] = perm
        findings += _offline_classify_findings(stmts)
        segment = entries[cursor:cursor + len(recs)]
        cursor += len(segment)
        pairs, lone_r, lone_e = _offline_pair(recs, segment, pk_map, types)
        pairs_all += pairs
        lone_recs += lone_r
        lone_entries += lone_e
        paired = {id(r): e for r, e in pairs}
        for r in recs:    # ④＋⑧：依呼叫序逐筆比前值，再把該筆之配對登記疊上左源
            if r["kind"] != "seed_add":
                row = _offline_left_row(left, r, types)
                findings += _offline_prevalue_findings(r, row, types)
                summary["prev"] += 1
                if row is None:
                    continue
            if id(r) in paired:
                left = _offline_advance_left(left, paired[id(r)])
    lone_entries += entries[cursor:]
    findings += _offline_ledger_findings(pairs_all, lone_recs, lone_entries, pk_map, types)
    summary["pair_ids"] = sorted((e["id"] for _r, e in pairs_all), key=lambda x: int(x[2:]))
    return findings, summary


def _offline_summary_lines(summary):
    lines = [f"[offline] delta {len(summary['files'])} 支：{'、'.join(summary['files'])}"]
    order = ("seed DML", "序列", "權限面", "未分類")
    for name in summary["files"]:
        parts = []
        for d in ("up", "down"):
            c = summary["stmts"][name][d]
            detail = "、".join(f"{k} {c[k]}" for k in order if c[k])
            parts.append(f"{d} {sum(c.values())} 句（{detail or '零句'}）")
        lines.append(f"[offline] {name}｜{'／'.join(parts)}")
    ids = summary["pair_ids"]
    lines.append(f"[offline] seed DML ↔ 演進帳：配對 {len(ids)} 筆"
                 + (f"（{ids[0]}～{ids[-1]}）" if ids else ""))
    lines.append(f"[offline] 前值 ↔ 凍結 seed ⊕ 前序配對登記：比對 {summary['prev']} 筆")
    for name in summary["files"]:
        for d in ("up", "down"):
            p = summary["perm"][name][d]
            if not p["kinds"]:
                lines.append(f"[offline] 權限面（只列不對賬）{name}｜{d} 無")
                continue
            kinds = "、".join(f"{k} {v}" for k, v in sorted(p["kinds"].items()))
            objs = "、".join(f"{kind} {obj}（{', '.join(sorted(privs))}）"
                            for (kind, obj), privs in sorted(p["objects"].items()))
            lines.append(f"[offline] 權限面（只列不對賬）{name}｜{d}：{kinds}；角色 "
                         f"{'、'.join(sorted(p['roles'])) or '無'}；受權物件 {len(p['objects'])}"
                         + (f"＝{objs}" if objs else ""))
    return lines


def cmd_offline(root=REPO_ROOT):
    """offline 子命令（純讀檔、零 docker）：rc 0 全綠／1 finding（[offline·分類]／[offline·對賬]／[offline·前值]）／
    2 結構異常。"""
    try:
        findings, summary = offline_report(root)
    except GateError as ex:
        print(f"[offline] ✗ {ex}", file=sys.stderr)
        return 2
    for line in _offline_summary_lines(summary):
        print(line)
    if findings:
        print(f"[offline] ✗ {len(findings)} 項 finding（逐項指名；處置：未分類句＝改 migration 或擴本腿、"
              "對賬不符＝改 migration 或登記 schema-evolution.json、前值不符＝核 WHERE 前值）：", file=sys.stderr)
        for x in findings:
            print(f"    {x}", file=sys.stderr)
        return 1
    print("[offline] ✓ 全綠（解析、分類、seed DML ↔ 演進帳、前值 ↔ 凍結 seed ⊕ 前序配對；權限面只列）")
    return 0


# ---------------------------------------------------------------------------
# 自帶測試（unittest、離線——不觸 docker、不讀實庫）
# ---------------------------------------------------------------------------

_VALID_LEDGER = {"next_id": 1, "entries": []}


def _entry(**kw):
    e = {"id": "E-001", "knife": "001-schema-baseline", "kind": "add_column",
         "table": "sys_user",
         "detail": {"column": "tmp_x", "type": "text", "nullable": True,
                    "default": None, "position": "末位"},
         "date": "2026-08-05"}
    e.update(kw)
    return e


def _write_ledger(d, data):
    path = os.path.join(d, LEDGER)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)


class TestSelfTest(unittest.TestCase):
    def test_self_test_passes(self):
        check_self_test()   # 不 raise 即綠（健康對＋四類注入內含）


class TestNegativeInjection(unittest.TestCase):
    """SC-003 五類假漂移注入、全數必紅（比對器先自證；test 子命令承載面）：①結構②欄序
    ③seed 值④sequence 落值⑤假 delta 登記合成（對真凍結面、test_5；seed_add 序號姊妹案
    ＝test_5b、真演進帳之序號推進鏈＝test_5c）。"""

    def setUp(self):
        self.fix = _st_fixtures()
        self.healthy = synth_expected(self.fix, [])
        self.norm = normalize_seed_dump(_ST_DUMP)

    def test_1_structure_add_column_red(self):
        drifted = json.loads(json.dumps(self.healthy))
        drifted["columns"].append({"table": "t_ok", "column": "ghost", "ordinal": 3,
                                   "type": "text", "nullable": True, "default": None})
        f = compare_structure(synth_expected(self.fix, []), drifted)
        self.assertTrue(any("columns/t_ok/ghost" in x and "未登記" in x for x in f))

    def test_1b_structure_type_change_red(self):
        mutated = json.loads(json.dumps(self.healthy))
        mutated["columns"][2]["type"] = "integer"
        f = compare_structure(synth_expected(self.fix, []), mutated)
        self.assertTrue(any("columns/t_ok/id" in x for x in f))

    def test_1c_structure_index_missing_red(self):
        """gate1 indexes 節：期望有、實庫無（spec-compliance-001 review I-2）。"""
        drifted = json.loads(json.dumps(self.healthy))
        drifted["indexes"] = []
        f = compare_structure(synth_expected(self.fix, []), drifted)
        self.assertTrue(any("indexes/t_ok/t_ok_pkey" in x for x in f), f)

    def test_1d_structure_constraint_def_change_red(self):
        """gate1 constraints 節：定義字串異（spec-compliance-001 review I-2）。"""
        drifted = json.loads(json.dumps(self.healthy))
        drifted["constraints"][0]["definition"] = "PRIMARY KEY (name)"
        f = compare_structure(synth_expected(self.fix, []), drifted)
        self.assertTrue(any("constraints/t_ok/t_ok_pkey" in x for x in f), f)

    def test_1e_structure_index_unregistered_red(self):
        """gate1 indexes 節：實庫有、期望無（spec-compliance-001 review I-2）。"""
        drifted = json.loads(json.dumps(self.healthy))
        drifted["indexes"].append({"table": "t_ok", "name": "t_ok_ghost_idx",
                                   "definition": "CREATE INDEX t_ok_ghost_idx ON public.t_ok USING btree (name)"})
        f = compare_structure(synth_expected(self.fix, []), drifted)
        self.assertTrue(any("indexes/t_ok/t_ok_ghost_idx" in x for x in f), f)

    def test_2_column_order_swap_red(self):
        swapped = json.loads(json.dumps(self.healthy["columns"]))
        for c in swapped:
            if c["table"] == "t_ok":
                c["ordinal"] = 3 - c["ordinal"]
        f = compare_column_order({"t_ok": ["id", "name"]}, [], swapped)
        self.assertTrue(any("[gate2·欄序] t_ok" in x for x in f))

    def test_3_seed_value_red(self):
        f = compare_seed(self.norm, self.norm.replace("1\ta", "1\tX"))
        self.assertTrue(f and "diff 非零" in f[0])

    def test_4_setval_red(self):
        f = compare_seed(self.norm, self.norm.replace("', 2, true);", "', 1, true);"))
        self.assertTrue(f and "setval" in f[0])

    def test_registered_then_green(self):
        """演進帳往返縮影：注入紅→登記綠（SC-004 之離線半；合成 fixtures）。"""
        drifted = json.loads(json.dumps(self.healthy))
        drifted["columns"].append({"table": "t_ok", "column": "ghost", "ordinal": 3,
                                   "type": "text", "nullable": True, "default": None})
        entry = _entry(table="t_ok",
                       detail={"column": "ghost", "type": "text", "nullable": True,
                               "default": None, "position": "末位"})
        self.assertEqual(compare_structure(synth_expected(self.fix, [entry]),
                                           drifted), [])
        f = compare_column_order({"t_ok": ["id", "name"]}, [entry],
                                 drifted["columns"])
        self.assertEqual(f, [])

    def test_5_fake_delta_synth_real_fixtures(self):
        """第五案（`docs/ops/reference-src/schema-gates.md` §4 ⑤、spec FR-009、research R7）：對**真凍結 fixtures**
        登記一筆假 add_column（sys_user.tmp_x text 可空、末位）——合成期望值必與「注入後實庫
        照相」全等（結構面＋欄序面＋seed 面三面皆綠）；同一注入未登記則三面皆紅、指名
        sys_user／tmp_x。rev5 終態登記零筆、此為合成邏輯對真凍結面的首次實證。"""
        fx = load_fixtures(REPO_ROOT)
        dm = load_data_model_order(REPO_ROOT)
        entry = _entry()                       # sys_user.tmp_x text nullable 末位
        # 注入後實庫照相（結構面）＝凍結 columns ⊕ sys_user 末位新欄
        injected = json.loads(json.dumps(synth_expected(fx, [])))
        last = max(c["ordinal"] for c in injected["columns"] if c["table"] == "sys_user")
        injected["columns"].append({"table": "sys_user", "column": "tmp_x",
                                    "ordinal": last + 1, "type": "text",
                                    "nullable": True, "default": None})
        injected["columns"].sort(key=lambda r: (r["table"], r["ordinal"]))
        # 注入後 pg_dump（seed 面）＝COPY 段首欄清單接末位＋既有列補 \N（獨立於合成器構造）
        frozen_norm = normalize_seed_dump(fx["seed"])
        lines = frozen_norm.splitlines()
        _cols, start, end = _copy_blocks(lines)["sys_user"]
        lines[start - 1] = lines[start - 1].replace(") FROM stdin;", ", tmp_x) FROM stdin;")
        lines[start:end] = [r + "\t\\N" for r in lines[start:end]]
        injected_dump = normalize_seed_dump("\n".join(lines) + "\n")
        # 未登記＝三面皆紅、指名
        red = compare_structure(synth_expected(fx, []), injected)
        self.assertTrue(any("columns/sys_user/tmp_x" in x and "未登記" in x for x in red),
                        msg=red)
        red_order = compare_column_order(dm, [], injected["columns"])
        self.assertTrue(any("sys_user 第 18 位" in x and "tmp_x" in x for x in red_order),
                        msg=red_order)
        red_seed = compare_seed(frozen_norm, injected_dump)
        self.assertTrue(red_seed and "sys_user" in red_seed[0], msg=red_seed)
        # 登記後＝三面皆綠（合成期望值＝注入後實庫）
        self.assertEqual(compare_structure(synth_expected(fx, [entry]), injected), [])
        self.assertEqual(compare_column_order(dm, [entry], injected["columns"]), [])
        self.assertEqual(compare_seed(apply_seed_entries(frozen_norm, [entry]),
                                      injected_dump), [])

    def test_5b_fake_seed_add_sequence_synth_real_fixtures(self):
        """第五案之 seed_add 序號姊妹案（GR9；ADR-00085 決定 7）：對**真凍結 fixtures** 登記
        一筆假 seed_add（casbin_rule id 164、十一欄 COPY 文字形）——注入後 dump 獨立構造
        （COPY 列與 setval 行皆手寫、不經合成器）：資料列附入該段＋`casbin_rule_id_seq`
        由 (163, true) 前進至 (164, true)＝實庫跑 seed_add migration 收尾
        `setval(…, GREATEST(164, last_value), true)` 之形。未登記＝紅（列與序列兩處皆
        指名）；登記後合成期望＝注入後 dump（拆掉序號推進＝setval 行留 163 而紅）。"""
        fx = load_fixtures(REPO_ROOT)
        frozen_norm = normalize_seed_dump(fx["seed"])
        old_sv = "SELECT pg_catalog.setval('public.casbin_rule_id_seq', 163, true);"
        new_sv = "SELECT pg_catalog.setval('public.casbin_rule_id_seq', 164, true);"
        self.assertIn(old_sv, frozen_norm.splitlines())
        row = "164\tp\tR_SUPER\tipRule:unlock\tbutton\t\t\t\tf\t2026-08-05 00:00:00+00\t\\N"
        lines = frozen_norm.splitlines()
        _cols, _start, end = _copy_blocks(lines)["casbin_rule"]
        lines.insert(end, row)
        injected_dump = normalize_seed_dump(
            "\n".join(new_sv if ln == old_sv else ln for ln in lines) + "\n")
        entry = _entry(kind="seed_add", table="casbin_rule", detail={
            "pk": ["id"],
            "values": {"id": 164, "ptype": "p", "v0": "R_SUPER", "v1": "ipRule:unlock",
                       "v2": "button", "v3": "", "v4": "", "v5": "", "protected": False,
                       "created_at": "2026-08-05 00:00:00+00", "created_by": None}})
        # 未登記＝紅、列與序列兩處皆指名
        red = compare_seed(frozen_norm, injected_dump)
        self.assertTrue(red and row in red[0] and new_sv in red[0], msg=red)
        # 登記後＝綠（合成期望之資料列與序列落值皆＝注入後 dump）
        self.assertEqual(compare_seed(apply_seed_entries(frozen_norm, [entry]),
                                      injected_dump), [])

    def test_5c_real_ledger_seed_add_chain_advances_sequence(self):
        """第五案之真帳姊妹案（008 刀 U4a、T032 ③；GR9 形同 test_5b）：**真凍結 fixtures ⊕ 真演進帳全部 entries** 經
        apply_seed_entries 後三件成立——①`casbin_rule_id_seq` 之 setval 期望行恰一行＝(取大值, true)，取大值＝凍結落值與帳上
        casbin_rule 各筆 seed_add 之 values.id 之最大者（期望側以帳現算、不寫死；且須高於凍結落值＝帳上確有推進）②合成 COPY 段
        含每筆 seed_add 之列（依該段欄序之 COPY 文字形）③sys_menu 列 77 之 buttons 欄＝帳上該列 seed_update 之 set 值。
        拆 apply_seed_entries 內之序號推進一句＝①紅（setval 留凍結落值）。"""
        fx = load_fixtures(REPO_ROOT)
        entries = load_ledger(REPO_ROOT)["entries"]
        frozen_norm = normalize_seed_dump(fx["seed"])
        frozen_sv = [m for m in map(RE_SETVAL.match, frozen_norm.splitlines())
                     if m and m.group(1) == "casbin_rule_id_seq"]
        self.assertEqual(len(frozen_sv), 1)
        self.assertEqual(frozen_sv[0].group(3), "true")       # 凍結形已發（取大值之凍結端＝其落值）
        adds = [e for e in entries if e["kind"] == "seed_add" and e["table"] == "casbin_rule"]
        want = max([int(frozen_sv[0].group(2))] + [e["detail"]["values"]["id"] for e in adds])
        self.assertGreater(want, int(frozen_sv[0].group(2)), msg="帳上無高於凍結落值之 casbin_rule seed_add——本案 vacuous")
        lines = apply_seed_entries(frozen_norm, entries).splitlines()
        got_sv = [m.group(0) for m in map(RE_SETVAL.match, lines) if m and m.group(1) == "casbin_rule_id_seq"]
        self.assertEqual(got_sv, [f"SELECT pg_catalog.setval('public.casbin_rule_id_seq', {want}, true);"])
        blocks = _copy_blocks(lines)
        for e in (e for e in entries if e["kind"] == "seed_add"):
            cols, start, end = blocks[e["table"]]
            self.assertIn("\t".join(copy_literal(e["detail"]["values"][c]) for c in cols), lines[start:end], msg=e["id"])
        menu77 = [e for e in entries
                  if e["kind"] == "seed_update" and e["table"] == "sys_menu" and e["detail"]["pk"] == {"id": 77}]
        self.assertEqual(len(menu77), 1)
        cols, start, end = blocks["sys_menu"]
        rows = [r.split("\t") for r in lines[start:end] if r.split("\t")[cols.index("id")] == "77"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][cols.index("buttons")], copy_literal(menu77[0]["detail"]["set"]["buttons"]))


class TestLedgerAssertions(unittest.TestCase):
    """登記檔啟動斷言七條（`docs/ops/reference-src/schema-evolution-contract.md` §2）＝rc 2 fail-loud。"""

    def _load(self, data):
        with tempfile.TemporaryDirectory() as d:
            _write_ledger(d, data)
            return load_ledger(d)

    def test_baseline_form_green(self):
        self.assertEqual(self._load(_VALID_LEDGER)["entries"], [])
        got = self._load({"next_id": 2, "entries": [_entry()]})
        self.assertEqual(got["entries"][0]["id"], "E-001")

    def test_knife_format_bad(self):
        with self.assertRaisesRegex(GateError, "斷言④.*knife"):
            self._load({"next_id": 2, "entries": [_entry(knife="902_bad_slug")]})

    def test_kind_not_in_enum(self):
        with self.assertRaisesRegex(GateError, "斷言⑤.*kind"):
            self._load({"next_id": 2, "entries": [_entry(kind="rename_column")]})

    def test_drop_kind_named(self):
        with self.assertRaisesRegex(GateError, "斷言⑥.*基線翻案"):
            self._load({"next_id": 2, "entries": [_entry(kind="drop_column")]})

    def test_id_not_ascending(self):
        with self.assertRaisesRegex(GateError, "斷言③.*遞增"):
            self._load({"next_id": 904, "entries": [
                _entry(id="E-903"),
                _entry(id="E-902", kind="add_index", table="sys_role",
                       detail={"name": "x", "definition": "y"})]})

    def test_missing_date_field(self):
        e = _entry()
        del e["date"]
        with self.assertRaisesRegex(GateError, "斷言②.*date"):
            self._load({"next_id": 2, "entries": [e]})

    def test_top_level_keys_exact(self):
        with self.assertRaisesRegex(GateError, "斷言①"):
            self._load({"next_id": 1, "entries": [], "extra": 1})

    def test_next_id_mismatch(self):
        with self.assertRaisesRegex(GateError, "斷言③.*next_id"):
            self._load({"next_id": 9, "entries": [_entry()]})

    def test_json_malformed_caught(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, LEDGER)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("{broken")
            with self.assertRaisesRegex(GateError, "JSON 壞形"):
                load_ledger(d)


# 斷言⑦測試樣本：八 kind 各一筆合法 detail（缺鍵樣本＝逐 kind 刪首個必備鍵派生）。
_LEGAL_DETAIL = {
    "add_table": {"columns": [{"column": "id", "type": "bigint", "nullable": False,
                               "default": None}]},
    "add_column": {"column": "x", "type": "text", "nullable": True, "default": None,
                   "position": "末位"},
    "alter_column": {"column": "x", "nullable": False},
    "add_index": {"name": "i_x", "definition": "CREATE INDEX i_x ON public.t (x)"},
    "add_constraint": {"name": "c_x", "definition": "CHECK (x > 0)"},
    "seed_add": {"pk": ["id"], "values": {"id": 1}},
    "seed_update": {"pk": {"id": 1}, "set": {"name": "v"}},
    "seed_delete": {"pk": {"id": 1}},
}


class TestDetailKeyTable(unittest.TestCase):
    """斷言⑦（kind×detail 必備鍵表、rev5:B-006）：八 kind 各一筆合法／缺鍵樣本＝16 案
    （方法由下方 setattr 迴圈逐 kind 生成）。"""

    def _load(self, kind, detail):
        with tempfile.TemporaryDirectory() as d:
            _write_ledger(d, {"next_id": 2,
                              "entries": [_entry(kind=kind, detail=detail)]})
            return load_ledger(d)


def _mk_legal(kind):
    def test(self):
        got = self._load(kind, json.loads(json.dumps(_LEGAL_DETAIL[kind])))
        self.assertEqual(got["entries"][0]["kind"], kind)
    test.__doc__ = f"斷言⑦：{kind} 合法樣本必過。"
    return test


def _mk_missing(kind):
    key = DETAIL_KEYS[kind][0]

    def test(self):
        detail = json.loads(json.dumps(_LEGAL_DETAIL[kind]))
        del detail[key]
        if not detail:                    # 空 detail 會先撞斷言②——補墊鍵讓⑦說話
            detail = {"pad": 1}
        with self.assertRaisesRegex(GateError, "斷言⑦.*" + key):
            self._load(kind, detail)
    test.__doc__ = f"斷言⑦：{kind} 缺必備鍵 {key} 必紅。"
    return test


for _k in KINDS:
    setattr(TestDetailKeyTable, f"test_legal_{_k}", _mk_legal(_k))
    setattr(TestDetailKeyTable, f"test_missing_{_k}", _mk_missing(_k))


class TestDetailBadForms(unittest.TestCase):
    """rev5:B-006 四壞形改判 rc 2：rev5 前世逸出裸例外（ValueError／AttributeError／TypeError→
    解譯器崩潰、殼層收 rc 1）——契約 gates.md §0 rc 語意＝1 漂移／2 環境或結構異常，
    壞形屬後者。紅綠方向：改判前本組全紅（裸例外非 GateError）、改判後全綠。
    ★壞形①另帶 seed_add 姊妹案：契約「`pk`／`set`／`values` 欄名 ⊆ COPY 欄集」括號只
    豁免 `values` 的「恰等」強度、未豁免 `pk`——seed_add 分支同須驗，否則契約過度宣稱。"""

    def setUp(self):
        self.norm = normalize_seed_dump(_ST_DUMP)

    def test_row_order_swap_red(self):
        """多重集不變、逐列序改變＝必紅：`compare_seed` 判準「normalize 後未排序逐列 diff、★禁全檔排序」
        的唯一載體（BL-00018；改 sorted() 後既有案仍全綠、故非 vacuous 的只有本案）。"""
        norm = normalize_seed_dump(_ST_DUMP)
        lines = norm.split("\n")
        i, j = lines.index("1\ta"), lines.index("2\tb")
        swapped = list(lines)
        swapped[i], swapped[j] = swapped[j], swapped[i]
        self.assertEqual(sorted(lines), sorted(swapped))              # 多重集確實不變
        self.assertTrue(compare_seed(norm, "\n".join(swapped)))       # 逐列序變即紅

    def test_bad1b_seed_add_values_col_set_mismatch(self):
        """壞形①姊妹案：seed_add 的 values 欄集 ≠ COPY 欄集（前世 d["values"][c] 拋 KeyError；spec-compliance-001 review M-3）。"""
        e = _entry(kind="seed_add", table="t_ok", detail={"pk": ["id"], "values": {"id": 9}})
        with self.assertRaisesRegex(GateError, "values 欄集"):
            apply_seed_entries(self.norm, [e])

    def test_bad1_pk_col_not_in_copy_set(self):
        """壞形①：pk 欄名 ∉ COPY 欄集（前世 cols.index 拋 ValueError）。"""
        e = _entry(kind="seed_update", table="t_ok",
                   detail={"pk": {"ghost": 1}, "set": {"name": "z"}})
        with self.assertRaisesRegex(GateError, "不在 t_ok COPY 欄集"):
            apply_seed_entries(self.norm, [e])

    def test_bad1b_seed_add_pk_col_not_in_copy_set(self):
        """壞形①姊妹案：seed_add 之 pk 欄名 ∉ COPY 欄集（values 欄集合法亦須紅）——
        補檢前靜默通過（契約寫 A、工具驗 B），補檢後 GateError→rc 2。"""
        e = _entry(kind="seed_add", table="t_ok",
                   detail={"pk": ["ghost_col"], "values": {"id": 9, "name": "z"}})
        with self.assertRaisesRegex(GateError, "不在 t_ok COPY 欄集"):
            apply_seed_entries(self.norm, [e])

    def test_bad1c_seed_add_pk_not_list(self):
        """壞形①旁支：seed_add pk 非清單（直呼合成路徑兜底——否則 set() 逐字元拆解、
        錯誤訊息失真）。"""
        e = _entry(kind="seed_add", table="t_ok",
                   detail={"pk": "id", "values": {"id": 9, "name": "z"}})
        with self.assertRaisesRegex(GateError, "pk 須為主鍵欄名非空清單"):
            apply_seed_entries(self.norm, [e])

    def test_bad2_pk_not_object(self):
        """壞形②：pk 非物件（前世 pk_map.items() 拋 AttributeError）；load 斷言⑦同攔。"""
        e = _entry(kind="seed_update", table="t_ok",
                   detail={"pk": [{"id": 1}], "set": {"name": "z"}})
        with self.assertRaisesRegex(GateError, "pk 須為非空物件"):
            apply_seed_entries(self.norm, [e])
        with tempfile.TemporaryDirectory() as d:
            _write_ledger(d, {"next_id": 2, "entries": [e]})
            with self.assertRaisesRegex(GateError, "斷言⑦"):
                load_ledger(d)

    def test_bad3_set_not_object(self):
        """壞形③：set 非物件（前世 d["set"].items() 拋 AttributeError）。"""
        e = _entry(kind="seed_update", table="t_ok",
                   detail={"pk": {"id": 1}, "set": ["name"]})
        with self.assertRaisesRegex(GateError, "set 須為非空物件"):
            apply_seed_entries(self.norm, [e])

    def test_bad4_values_not_object(self):
        """壞形④：seed_add values 非物件（前世 set(d["values"]) 拋 TypeError）。"""
        e = _entry(kind="seed_add", table="t_ok",
                   detail={"pk": ["id"], "values": 7})
        with self.assertRaisesRegex(GateError, "values 須為物件"):
            apply_seed_entries(self.norm, [e])


class TestDuplicateRegistration(unittest.TestCase):
    """rev5:B-006 值域斷言：同名 index/constraint 重複登記攔——rev5 前世 synth 靜默附掛、compare
    面 (table,name) 字典鍵合併＝重複被吞、閘照綠。"""

    def test_add_index_duplicate(self):
        e = _entry(kind="add_index", table="t_ok",
                   detail={"name": "t_ok_pkey", "definition": "CREATE INDEX x"})
        with self.assertRaisesRegex(GateError, "重複登記"):
            synth_expected(_st_fixtures(), [e])

    def test_add_constraint_duplicate(self):
        e = _entry(kind="add_constraint", table="t_ok",
                   detail={"name": "t_ok_pkey", "definition": "PRIMARY KEY (id)"})
        with self.assertRaisesRegex(GateError, "重複登記"):
            synth_expected(_st_fixtures(), [e])


class TestFixturesMissing(unittest.TestCase):
    def test_check_rc2_with_remedy(self):
        """fixtures 缺席＝check rc 2 附補救提示（凍結面缺席場景驗收面；self-test＋登記檔綠後即攔、
        零 docker）。"""
        with tempfile.TemporaryDirectory() as d:
            _write_ledger(d, _VALID_LEDGER)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(cmd_check(root=d), 2)
            self.assertIn("fixtures/columns.json 缺席", err.getvalue())
            self.assertIn("補救", err.getvalue())


class TestSeedSynthesis(unittest.TestCase):
    def setUp(self):
        self.norm = normalize_seed_dump(_ST_DUMP)

    def test_seed_add(self):
        e = _entry(kind="seed_add", table="t_ok",
                   detail={"pk": ["id"], "values": {"id": 3, "name": "c"}})
        out = apply_seed_entries(self.norm, [e])
        self.assertIn("3\tc", out)
        self.assertEqual(compare_seed(out, normalize_seed_dump(out)), [])

    def test_seed_update(self):
        e = _entry(kind="seed_update", table="t_ok",
                   detail={"pk": {"id": 1}, "set": {"name": "z"}})
        out = apply_seed_entries(self.norm, [e])
        self.assertIn("1\tz", out)
        self.assertNotIn("1\ta", out)

    def test_seed_delete(self):
        e = _entry(kind="seed_delete", table="t_ok", detail={"pk": {"id": 2}})
        out = apply_seed_entries(self.norm, [e])
        self.assertNotIn("2\tb", out)

    def test_seed_update_pk_miss_fail_loud(self):
        e = _entry(kind="seed_update", table="t_ok",
                   detail={"pk": {"id": 99}, "set": {"name": "z"}})
        with self.assertRaisesRegex(GateError, "命中 0 列"):
            apply_seed_entries(self.norm, [e])

    def test_null_literal(self):
        self.assertEqual(copy_literal(None), "\\N")
        self.assertEqual(copy_literal(True), "t")
        self.assertEqual(copy_literal("a\tb"), "a\\tb")

    def test_sequence_roster_from_seed(self):
        """名冊自凍結 seed setval 行解析（rev6：唯一源）；零 setval 行／重名＝GateError。"""
        self.assertEqual(sequence_roster(self.norm), ["t_ok_id_seq"])
        with self.assertRaisesRegex(GateError, "零 setval 行"):
            sequence_roster("COPY public.t_ok (id) FROM stdin;\n\\.\n")
        dup = self.norm + "SELECT pg_catalog.setval('public.t_ok_id_seq', 5, true);\n"
        with self.assertRaisesRegex(GateError, "名冊重複"):
            sequence_roster(dup)

    def test_add_column_header_and_fill(self):
        out = apply_seed_entries(self.norm, [_entry(table="t_ok")])
        self.assertIn("COPY public.t_ok (id, name, tmp_x) FROM stdin;", out)
        self.assertIn("1\ta\t\\N", out)

    def test_add_column_with_default_fail_loud(self):
        e = _entry(table="t_ok",
                   detail={"column": "x", "type": "text", "nullable": True,
                           "default": "'v'::text", "position": "末位"})
        with self.assertRaisesRegex(GateError, "僅支援 nullable 無 default"):
            apply_seed_entries(self.norm, [e])

    def test_add_table_seed_face_fail_loud(self):
        e = _entry(kind="add_table", table="t_new",
                   detail={"columns": [{"column": "id", "type": "bigint",
                                        "nullable": False}]})
        with self.assertRaisesRegex(GateError, "add_table.*seed 面"):
            apply_seed_entries(self.norm, [e])

    # ── seed_add 序號合成（GR9；ADR-00085 決定 7；docs/ops/reference-src/schema-gates.md §2）──
    # 期望已發最大值 M＝N（is_called 真）或 N−1（假）；新 id > M ⇒ setval 行推至 (新 id, true)。

    @staticmethod
    def _setval(seq, n, called):
        return f"SELECT pg_catalog.setval('public.{seq}', {n}, {'true' if called else 'false'});"

    def test_seed_add_advances_sequence_above_issued_max(self):
        """t_ok 序列 (2, true)＝已發 2；加 id 3（＝M＋1）⇒ 期望推至 (3, true)、舊行不留。"""
        e = _entry(kind="seed_add", table="t_ok",
                   detail={"pk": ["id"], "values": {"id": 3, "name": "c"}})
        out = apply_seed_entries(self.norm, [e])
        self.assertIn(self._setval("t_ok_id_seq", 3, True), out.splitlines())
        self.assertNotIn(self._setval("t_ok_id_seq", 2, True), out.splitlines())

    def test_seed_add_not_above_issued_max_leaves_sequence(self):
        """新 id ≤ M＝不動（先刪後補 id 2＝M）：①(2, true)＝已發 2 ②(3, false)＝已發 2。"""
        readd = [_entry(kind="seed_delete", table="t_ok", detail={"pk": {"id": 2}}),
                 _entry(id="E-002", kind="seed_add", table="t_ok",
                        detail={"pk": ["id"], "values": {"id": 2, "name": "c"}})]
        out = apply_seed_entries(self.norm, readd)
        self.assertIn("2\tc", out)
        self.assertIn(self._setval("t_ok_id_seq", 2, True), out.splitlines())
        uncalled = self.norm.replace(self._setval("t_ok_id_seq", 2, True),
                                     self._setval("t_ok_id_seq", 3, False))
        out = apply_seed_entries(uncalled, readd)
        self.assertIn(self._setval("t_ok_id_seq", 3, False), out.splitlines())

    def test_seed_add_is_called_false_real_seed_sys_ip_rule(self):
        """真凍結 seed 之 sys_ip_rule_id_seq＝(1, false)＝未動用、已發 0；加 id 1 ⇒ (1, true)；
        他序列行逐字不動。"""
        frozen = normalize_seed_dump(load_fixtures(REPO_ROOT)["seed"])
        self.assertIn(self._setval("sys_ip_rule_id_seq", 1, False), frozen.splitlines())
        values = {"id": 1, "created_at": "2026-08-05 00:00:00+00", "created_by": None,
                  "updated_at": None, "updated_by": None, "deleted_at": None,
                  "deleted_by": None, "order": 1, "wbip_type": 1,
                  "wbip_cidr": "192.0.2.0/24", "wbip_memo": None}
        e = _entry(kind="seed_add", table="sys_ip_rule",
                   detail={"pk": ["id"], "values": values})
        out = apply_seed_entries(frozen, [e])
        self.assertIn(self._setval("sys_ip_rule_id_seq", 1, True), out.splitlines())

        def others(txt):
            return [ln for ln in txt.splitlines()
                    if RE_SETVAL.match(ln) and "sys_ip_rule_id_seq" not in ln]
        self.assertEqual(others(out), others(frozen))
        self.assertEqual(len(others(frozen)), len(sequence_roster(frozen)) - 1)

    def test_seed_add_table_without_sequence_line_untouched(self):
        """無 `<表>_<pk>_seq` 之 setval 行（非序號主鍵，如文字 pk）＝不推進、不補行、不驗整數。"""
        norm = normalize_seed_dump(_ST_DUMP.replace(
            "SELECT pg_catalog.setval",
            "COPY public.t_kv (k, v) FROM stdin;\nk1\tx\n\\.\n\nSELECT pg_catalog.setval"))
        e = _entry(kind="seed_add", table="t_kv",
                   detail={"pk": ["k"], "values": {"k": "k2", "v": "y"}})
        out = apply_seed_entries(norm, [e])
        self.assertIn("k2\ty", out)
        setvals = [ln for ln in out.splitlines() if "setval" in ln]
        self.assertEqual(setvals, [self._setval("t_ok_id_seq", 2, True)])

    def test_seed_add_multi_column_pk_no_advance(self):
        """pk 多欄＝不推進（即使首欄恰有同名序列行）。"""
        e = _entry(kind="seed_add", table="t_ok",
                   detail={"pk": ["id", "name"], "values": {"id": 9, "name": "z"}})
        out = apply_seed_entries(self.norm, [e])
        self.assertIn("9\tz", out)
        self.assertIn(self._setval("t_ok_id_seq", 2, True), out.splitlines())

    def test_seed_add_non_integer_pk_value_fail_loud(self):
        """有序列行而 pk 值非整數（字串、布林、浮點）＝GateError（呼叫端 rc 2）。"""
        for bad in ("3", True, 3.0):
            e = _entry(kind="seed_add", table="t_ok",
                       detail={"pk": ["id"], "values": {"id": bad, "name": "c"}})
            with self.subTest(value=bad):
                with self.assertRaisesRegex(GateError, r"t_ok\.id.*非整數.*t_ok_id_seq"):
                    apply_seed_entries(self.norm, [e])

    def test_seed_add_multiple_entries_advance_in_order_take_max(self):
        """多筆依 entries 序逐筆推進取大：[5, 4]＝(5, true)（後筆較小不倒退）；[3, 4]＝(4, true)。"""
        def add(eid, i):
            return _entry(id=eid, kind="seed_add", table="t_ok",
                          detail={"pk": ["id"], "values": {"id": i, "name": f"n{i}"}})
        out = apply_seed_entries(self.norm, [add("E-001", 5), add("E-002", 4)])
        self.assertIn(self._setval("t_ok_id_seq", 5, True), out.splitlines())
        out = apply_seed_entries(self.norm, [add("E-001", 3), add("E-002", 4)])
        self.assertIn(self._setval("t_ok_id_seq", 4, True), out.splitlines())

    def test_seed_update_delete_leave_sequence(self):
        """seed_update／seed_delete 不動序列（刪列不回捲＝與 PG 行為一致）。"""
        for e in (_entry(kind="seed_delete", table="t_ok", detail={"pk": {"id": 2}}),
                  _entry(kind="seed_update", table="t_ok",
                         detail={"pk": {"id": 2}, "set": {"id": 7}})):
            with self.subTest(kind=e["kind"]):
                out = apply_seed_entries(self.norm, [e])
                self.assertIn(self._setval("t_ok_id_seq", 2, True), out.splitlines())


class TestRuntimeAppendNarrow(unittest.TestCase):
    """rev5:B-065 表級收窄九臂紅綠（rev5 2026-08-11 拍板「收窄寫死工具內」形、rev6 承襲；①～⑧離線合成
    dump、⑨用真凍結 seed，皆不碰真庫）：①收窄表 actual 側 runtime 列→綠②seed 側塞列→紅（必空斷言、
    具名）③非收窄表列漂移→照紅（不外溢）④setval 值異→綠、整行消失→紅⑤收窄表
    COPY 段首欄名變動→照紅（結構面仍守）⑥normalize＋收窄全管線冪等⑦前綴鄰接表
    sys_token_x 之列與 setval 值原樣保留（成員判定＝全名全等、退化成前綴匹配即紅）
    ⑧收窄表 COPY 段整段缺席→必空斷言跳過不誤報、缺段由收窄後 diff 自紅（降級腿
    論證的機器載體、rev5:L-019）⑨sys_access_log 入集（ADR-00100 決定 8）：真凍結 seed 之該段實庫側塞列
    且序列前進→綠、seed 側塞列→必空斷言指名。"""

    @staticmethod
    def _full(text):
        return narrow_runtime_append(normalize_seed_dump(text))

    def setUp(self):
        self.left = self._full(_RT_DUMP)

    def test_1_runtime_rows_green(self):
        act = (_RT_DUMP
               .replace("COPY public.session_event (id, event_type) FROM stdin;\n",
                        "COPY public.session_event (id, event_type) FROM stdin;\n"
                        "7\tlogin\n8\tlogout\n")
               .replace("COPY public.sys_token (id, status) FROM stdin;\n",
                        "COPY public.sys_token (id, status) FROM stdin;\n3\tactive\n")
               .replace("'public.session_event_id_seq', 1, false",
                        "'public.session_event_id_seq', 8, true"))
        self.assertEqual(compare_seed(self.left, self._full(act)), [])

    def test_2_seed_side_row_red_named(self):
        stuffed = normalize_seed_dump(_RT_DUMP.replace(
            "COPY public.sys_login_attempt (id, success) FROM stdin;\n",
            "COPY public.sys_login_attempt (id, success) FROM stdin;\n1\tt\n"))
        f = runtime_seed_empty_findings(stuffed)
        self.assertEqual(len(f), 1, msg=f)       # 其餘兩表零列勿誤報
        self.assertIn("sys_login_attempt", f[0])
        self.assertIn("1 列", f[0])
        self.assertIn("必空", f[0])

    def test_3_non_narrowed_drift_still_red(self):
        f = compare_seed(self.left, self._full(_RT_DUMP.replace("1\ta", "1\tX")))
        self.assertTrue(f and "diff 非零" in f[0], msg=f)

    def test_4_setval_value_green_line_missing_red(self):
        act = _RT_DUMP.replace("'public.sys_token_id_seq', 1, false",
                               "'public.sys_token_id_seq', 42, true")
        self.assertEqual(compare_seed(self.left, self._full(act)), [])
        gone = _RT_DUMP.replace(
            "SELECT pg_catalog.setval('public.sys_token_id_seq', 1, false);\n", "")
        f = compare_seed(self.left, self._full(gone))
        self.assertTrue(f and "sys_token_id_seq" in f[0], msg=f)
        # ★承 rev5 確認輪補釘：上面的子字串斷言會被 diff context 行（⑦臂貼界線 fixture
        #   sys_token_id_seq_x）巧合撐綠——佔位若丟 sequence 名（寫死 <seq>），刪除行
        #   不再含名、context 行仍在＝變異存活。此處直釘「收窄後左源保留 per-sequence
        #   佔位行」的字面（沿用常數、不手抄佔位），把「行存在仍比、且知道是哪一支」
        #   的語意掛上非巧合的機器載體。
        self.assertIn(f"SELECT pg_catalog.setval('public.sys_token_id_seq', "
                      f"{_RT_SETVAL_PLACEHOLDER});", self.left)

    def test_5_copy_header_drift_red(self):
        act = _RT_DUMP.replace(
            "COPY public.session_event (id, event_type) FROM stdin;",
            "COPY public.session_event (id, event_type, extra) FROM stdin;")
        f = compare_seed(self.left, self._full(act))
        self.assertTrue(f and "session_event" in f[0], msg=f)

    def test_6_full_pipeline_idempotent(self):
        self.assertEqual(self._full(self.left), self.left)
        self.assertEqual(narrow_runtime_append(self.left), self.left)

    def test_7_prefix_adjacent_table_untouched(self):
        """rev5:L-020 貼界線：sys_token_x＝收窄表 sys_token 的前綴延伸、sys_token_id_seq_x
        ＝收窄 sequence sys_token_id_seq 的前綴延伸——[`RE_COPY_HDR`]／[`RE_SETVAL`]
        之 `(\\w+)` 全名捕獲＋dict／frozenset 全等成員判定若退化成前綴／子字串匹配，
        其列即被誤剝、其 setval 值即被誤佔位；此處釘住兩者收窄後逐字原樣
        （「收窄不外溢」宣稱的貼界線機器載體）。"""
        self.assertIn("9\tzz", self.left)
        self.assertIn(
            "SELECT pg_catalog.setval('public.sys_token_id_seq_x', 7, true);",
            self.left)

    def test_8_missing_copy_block_skip_then_diff_red(self):
        """rev5:L-019 補載體：[`runtime_seed_empty_findings`] 的「COPY 段缺席就跳過」腿
        （continue）與其推給 diff 的論證「缺段由 diff 自紅」原本雙雙零紅綠——有論證
        無覆蓋＝下一個人有充分理由把 continue「簡化」掉（拿掉即缺段側 KeyError、
        本測以紅擋下）。雙釘：(a) 缺段側必空斷言不 raise 且回空（其餘兩收窄表零列
        勿誤報）(b) 收窄後逐列 diff 非空且指名 sys_token（論證為真的機器載體）。"""
        i = _RT_DUMP.index("COPY public.sys_token (")
        j = _RT_DUMP.index("\\.\n", i) + len("\\.\n")
        norm = normalize_seed_dump(_RT_DUMP[:i] + _RT_DUMP[j:])
        self.assertEqual(runtime_seed_empty_findings(norm), [])
        f = compare_seed(self.left, narrow_runtime_append(norm))
        self.assertTrue(f and "sys_token" in f[0], msg=f)

    def test_9_access_log_member_narrowed_on_real_seed(self):
        """ADR-00100 決定 8：sys_access_log 入收窄集（存取日誌每筆已登入請求一列＝runtime 寫入、seed 恆零列）。用真凍結
        seed：實庫側該段塞兩列且其序列 setval 改 (2, true) → 收窄後 compare_seed 綠；seed 側該段塞一列 →
        runtime_seed_empty_findings 恰一條且指名該表。"""
        seed = load_fixtures(REPO_ROOT)["seed"]
        hdr = next(ln for ln in seed.splitlines() if ln.startswith("COPY public.sys_access_log (")) + "\n"
        setval = "SELECT pg_catalog.setval('public.sys_access_log_id_seq', 1, false);"
        self.assertEqual((seed.count(hdr), seed.count(setval)), (1, 1))
        rows = ["\t".join([str(i), "2026-10-23 00:00:00+00", "1", "200", "GET", "/x", "127.0.0.1",
                            "\\N", "\\N", "\\N", "\\N", "\\N"]) + "\n" for i in (1, 2)]
        actual = seed.replace(hdr, hdr + "".join(rows)).replace(
            setval, "SELECT pg_catalog.setval('public.sys_access_log_id_seq', 2, true);")
        self.assertEqual(compare_seed(self._full(seed), self._full(actual)), [])
        f = runtime_seed_empty_findings(normalize_seed_dump(seed.replace(hdr, hdr + rows[0])))
        self.assertEqual(len(f), 1, msg=f)
        self.assertIn("runtime-append 表 sys_access_log", f[0])


class TestPgDumpArgv(unittest.TestCase):
    """pg_dump 旗標渲染回歸：-e PGTZ=UTC 必掛 exec 子命令之後（兩形皆然）。
    曾有缺陷：compose 形把 -e 插在 docker compose 頂層 → `unknown shorthand flag: 'e'`
    rc 1 → check 對 dev stack 永遠 rc 2（rev5 實證；quickstart D／RUNBOOK §10 裸 check 不可用）。"""

    class _R:
        returncode, stdout, stderr = 0, "x", ""

    def _rendered(self, container):
        seen = {}

        def fake_run(cmd, **kw):
            seen["cmd"] = cmd
            return self._R()

        pg_dump_data(container=container, run=fake_run)
        return seen["cmd"]

    def test_compose_form_env_after_exec(self):
        cmd = self._rendered(None)
        i = cmd.index("exec")
        self.assertEqual(cmd[i + 1:i + 3], ["-e", "PGTZ=UTC"])
        self.assertNotIn("-e", cmd[:i])      # docker compose 頂層絕無 -e

    def test_container_form_env_after_exec(self):
        self.assertEqual(self._rendered("pristine-pg")[:6],
                         ["docker", "exec", "-e", "PGTZ=UTC", "-i", "pristine-pg"])


class TestCmdCheckGreenPath(unittest.TestCase):
    """rev5:B-013 缺口①：cmd_check 綠路徑離線全程（時區前置→照相→合成→三閘＋時間欄型別→
    六行摘要→rc 0）。樁沿 TestPgDumpArgv fake_run 法：SHOW timezone 回 UTC、按 SQL 常數分派
    fixtures 三節 JSON（時區來源回伺服器側）、pg_dump 回凍結 seed.sql。★驗 SQL 分派正確（時區值與來源兩查詢居首）＋六行摘要
    格式計數＋rc 0；比對器邏輯歸 check_self_test 承載、此處刻意不重驗（分工）。凍結基線複製入
    暫存 root＋空演進帳＝真登記檔日後長 entries 也不影響本測（凍結面永不改寫、字面計數可釘）。"""

    _COPY = ("specs/001-schema-baseline/fixtures/columns.json",
             "specs/001-schema-baseline/fixtures/indexes.json",
             "specs/001-schema-baseline/fixtures/constraints.json",
             "specs/001-schema-baseline/fixtures/seed.sql",
             "docs/ops/reference-src/schema-definition.md",
             "docs/ops/reference-src/archetype-map.json")

    def test_green_path_sql_dispatch_summary_rc0(self):
        fx = load_fixtures(REPO_ROOT)
        dispatch = {SQL_COLUMNS: fx["columns"], SQL_INDEXES: fx["indexes"],
                    SQL_CONSTRAINTS: fx["constraints"]}
        calls = []

        class _R:
            returncode, stderr = 0, ""

            def __init__(self, out):
                self.stdout = out

        def fake_run(cmd, **kw):
            if "pg_dump" in cmd:
                calls.append("pg_dump")
                return _R(fx["seed"])
            sql = cmd[-1]
            if sql == SQL_TIMEZONE:
                calls.append(sql)
                return _R("UTC\n")
            if sql == SQL_TIMEZONE_SOURCE:
                calls.append(sql)
                return _R("command line\n")
            if sql not in dispatch:
                raise AssertionError(f"樁收到未知 SQL（分派錯）：{sql[:80]}")
            calls.append(sql)
            return _R(json.dumps(dispatch[sql]))

        with tempfile.TemporaryDirectory() as d:
            for rel in self._COPY:
                dst = os.path.join(d, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(os.path.join(REPO_ROOT, rel), dst)
            _write_ledger(d, _VALID_LEDGER)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = cmd_check(root=d, run=fake_run)
        self.assertEqual(rc, 0)
        # SQL 分派：時區值與其來源兩查詢居首（ADR-00059 決定 3）、三查詢恰各一次、序＝columns→indexes→
        # constraints，殿後 pg_dump
        self.assertEqual(calls, [SQL_TIMEZONE, SQL_TIMEZONE_SOURCE, SQL_COLUMNS, SQL_INDEXES,
                                 SQL_CONSTRAINTS, "pg_dump"])
        lines = out.getvalue().splitlines()
        self.assertEqual(len(lines), 6)
        self.assertTrue(all(ln.startswith("[check] ✓") for ln in lines), msg=lines)
        self.assertIn("時區：SHOW timezone＝UTC（source＝command line）", lines[0])
        self.assertIn("gate1 結構：columns 169／indexes 38／constraints 101 全等",
                      lines[1])
        self.assertIn("演進帳合成 0 筆", lines[1])
        self.assertIn("gate2 欄序：14 親排表逐位全等", lines[2])
        self.assertIn("casbin_rule 豁免", lines[2])
        # rev5:B-065 收窄後比對面行數：收窄各表 seed 側本就零列、setval 行原位改佔位——
        # 行數與未收窄時相等（凍結面字面可釘）
        n = len(narrow_runtime_append(normalize_seed_dump(fx["seed"])).splitlines())
        self.assertEqual(n, len(normalize_seed_dump(fx["seed"]).splitlines()))
        self.assertIn(f"gate2 seed：normalize 後 {n} 行逐列零差異（setval 名冊 11 支；"
                      "runtime-append 收窄 5 表）", lines[3])
        self.assertIn("audit archetype：15/15 綠", lines[4])
        # 凍結 columns.json 之時間欄恰 29 欄、全為 timestamptz（ADR-00060 背景之現況計數）
        self.assertIn("時間欄型別：29 欄 timestamptz、date 登記 0", lines[5])


class TestCmdCheckSeedEmptyWiring(unittest.TestCase):
    """rev5:B-065 佈線守門（[`cmd_check`] 面）：必空斷言「先於剝列」且「吃左源」原本只有
    註解宣稱、無機器紅綠——次序反轉（先 [`narrow_runtime_append`] 再餵
    [`runtime_seed_empty_findings`]）＝左源恆零列、恆綠假閘；左右搞反（改餵實庫 dump
    右源）＝語意整個倒轉——runtime 寫入照樣紅、seed 塞列反而恆綠（rev5:L-018／rev5:L-019 同形；
    [`compare_dump_owner`] 同款輸入陷阱有零 Owner 行 GateError 兜底、此處全靠本測）。
    既有測試皆直呼兩函式、繞過佈線，故另立本類。合成形：temp root 之 seed.sql
    **副本**在 session_event COPY 段塞一列，pg_dump 樁回**乾淨原文**——★左右可辨：
    塞列位於收窄表 COPY 段、兩側剝列後逐列 diff 仍恰空、唯一紅源＝必空斷言吃到塞列
    左源。現行佈線 rc 1＋具名 finding；次序反轉或左右搞反皆 rc 0 即本測紅。
    不碰 specs/ 真檔。"""

    def test_empty_assert_precedes_narrow_rc1_named(self):
        fx = load_fixtures(REPO_ROOT)
        dispatch = {SQL_COLUMNS: fx["columns"], SQL_INDEXES: fx["indexes"],
                    SQL_CONSTRAINTS: fx["constraints"]}
        lines = fx["seed"].splitlines(keepends=True)
        i = next(k for k, ln in enumerate(lines)
                 if ln.startswith("COPY public.session_event ("))
        stuffed = "".join(lines[:i + 1] + ["9\taudit\n"] + lines[i + 1:])

        class _R:
            returncode, stderr = 0, ""

            def __init__(self, out):
                self.stdout = out

        def fake_run(cmd, **kw):
            if "pg_dump" in cmd:
                return _R(fx["seed"])    # 右源＝乾淨原文（左右可辨、餵右源即恆綠可測）
            if cmd[-1] == SQL_TIMEZONE:
                return _R("UTC\n")       # 時區前置放行（ADR-00059）
            if cmd[-1] == SQL_TIMEZONE_SOURCE:
                return _R("command line\n")   # 時區來源＝伺服器側、放行
            return _R(json.dumps(dispatch[cmd[-1]]))

        with tempfile.TemporaryDirectory() as d:
            for rel in TestCmdCheckGreenPath._COPY:
                dst = os.path.join(d, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(os.path.join(REPO_ROOT, rel), dst)
            with open(os.path.join(d, "specs/001-schema-baseline/fixtures/seed.sql"),
                      "w", encoding="utf-8") as fh:
                fh.write(stuffed)        # 左源副本＝同一份塞列文本
            _write_ledger(d, _VALID_LEDGER)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = cmd_check(root=d, run=fake_run)
        msg = err.getvalue()
        self.assertEqual(rc, 1, msg=msg)
        self.assertIn("runtime-append 表 session_event", msg)
        self.assertIn("seed 側有 1 列", msg)
        # ★鑑別力自保：塞列在收窄表 COPY 段內、兩側剝列後 diff 必不紅——若此處也紅，
        # 次序反轉／左右搞反版同樣 rc 1、本測即失去判別力
        self.assertNotIn("diff 非零", msg)


def _check_fake(tz="UTC", columns=None, source="command line"):
    """cmd_check 佈線測之共用樁：回 (calls, fake_run, root_ctx)。SHOW timezone 回 tz、時區來源查詢
    回 source、三照相查詢回凍結 fixtures（columns 可替換）、pg_dump 回凍結 seed.sql；root_ctx＝凍結
    基線副本＋空演進帳之暫存 root（同 TestCmdCheckGreenPath 形）。calls 依序記錄收到之查詢。"""
    fx = load_fixtures(REPO_ROOT)
    dispatch = {SQL_COLUMNS: fx["columns"] if columns is None else columns,
                SQL_INDEXES: fx["indexes"], SQL_CONSTRAINTS: fx["constraints"]}
    calls = []

    class _R:
        returncode, stderr = 0, ""

        def __init__(self, out):
            self.stdout = out

    def fake_run(cmd, **kw):
        if "pg_dump" in cmd:
            calls.append("pg_dump")
            return _R(fx["seed"])
        calls.append(cmd[-1])
        if cmd[-1] == SQL_TIMEZONE:
            return _R(tz + "\n")
        if cmd[-1] == SQL_TIMEZONE_SOURCE:
            return _R(source + "\n")
        return _R(json.dumps(dispatch[cmd[-1]]))

    @contextlib.contextmanager
    def root_ctx():
        with tempfile.TemporaryDirectory() as d:
            for rel in TestCmdCheckGreenPath._COPY:
                dst = os.path.join(d, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(os.path.join(REPO_ROOT, rel), dst)
            _write_ledger(d, _VALID_LEDGER)
            yield d

    return calls, fake_run, root_ctx


class TestTimezonePrecheck(unittest.TestCase):
    """時區前置（ADR-00059 決定 3）：右源照相段最先取 SHOW timezone；值≠UTC＝rc 2 附修法、
    不往下照相比對（零照相查詢、零 pg_dump、零 ✓ 行）；＝UTC 放行（綠路徑全序與「✓ 時區」行由
    TestCmdCheckGreenPath 逐位釘；本類之 UTC 案只作前置判準之正例對照）。判準＝字面全等 UTC——同義名（Etc/UTC）亦不放行（ADR-00059
    決定 3 之「＝UTC」；compose 命令列固定值即此字面，postgres:18.4-alpine 映像 initdb 寫入
    設定檔之值亦同——一次性容器不帶 -c 亦過）。"""

    def test_judgement_utc_passes(self):
        self.assertIsNone(timezone_problem("UTC"))

    def test_judgement_non_utc_named_with_remedy(self):
        for bad in ("Asia/Tokyo", "Etc/UTC", "UTC+9", "GMT", ""):
            msg = timezone_problem(bad)
            self.assertIsNotNone(msg, msg=bad)
            self.assertIn(f"SHOW timezone＝{bad!r}", msg)
            self.assertIn("期望＝'UTC'", msg)
            self.assertIn("ADR-00059", msg)
            self.assertIn("docker-compose.yml", msg)
            self.assertIn("-c timezone=UTC", msg)
            self.assertIn("-c log_timezone=UTC", msg)  # 只在 compose 命令列修法句出現
            # 值判準先於來源判準：容器環境帶 PGTZ／PGOPTIONS 時先紅在此——補救須指到連線端覆蓋
            self.assertIn("PGTZ／PGOPTIONS", msg)

    def test_cmd_check_non_utc_rc2_before_snapshot(self):
        calls, run, root_ctx = _check_fake(tz="Asia/Tokyo")
        err, out = io.StringIO(), io.StringIO()
        with root_ctx() as d, contextlib.redirect_stderr(err), \
                contextlib.redirect_stdout(out):
            rc = cmd_check(root=d, run=run)
        msg = err.getvalue()
        self.assertEqual(rc, 2, msg=msg)
        self.assertEqual(calls, [SQL_TIMEZONE])          # 最先、且不往下照相／dump
        self.assertIn("SHOW timezone＝'Asia/Tokyo'", msg)
        self.assertIn("ADR-00059", msg)
        self.assertNotIn("self-test", msg)               # 鑑別力自保：rc 2 來自時區前置
        self.assertEqual(out.getvalue(), "")

    def test_cmd_check_utc_proceeds_rc0(self):
        calls, run, root_ctx = _check_fake(tz="UTC")
        out = io.StringIO()
        with root_ctx() as d, contextlib.redirect_stdout(out):
            rc = cmd_check(root=d, run=run)
        self.assertEqual(rc, 0)
        self.assertEqual(calls[0], SQL_TIMEZONE)
        self.assertIn("[check] ✓ 時區：SHOW timezone＝UTC", out.getvalue())

    def test_show_timezone_argv_reads_server_side(self):
        """時區值與來源兩查詢之撈取「必不帶」PGTZ／PGOPTIONS／子行程 env（與 TestPgDumpArgv 釘
        pg_dump「必帶」成對）：session 時區一經強制為 UTC（-e PGTZ=UTC、-e PGOPTIONS=-c timezone=UTC、
        env、連線字串 options）＝SHOW timezone 恆讀 UTC、前置斷言淪為恆綠假閘，而其餘樁只看
        cmd[-1] 分派、察覺不到。兩形（compose／--container）各跑一次 cmd_check，截下兩查詢各一次
        呼叫之完整 argv 逐位釘死（含 -X＝不讀 psqlrc：psqlrc 之 SET timezone 會把 session 值塞進
        SHOW）＋逐元素掃 PGTZ／PGOPTIONS（_db_base 本身被塞 -e 時逐位釘值跟著變、靠此掃描抓）＋
        kw 不得帶 env；另掃同一 run 之全部 psql 呼叫皆緊接 -X（helper 單支、照相查詢同形）。"""
        for container in (None, "pristine-pg"):
            with self.subTest(container=container):
                _, run, root_ctx = _check_fake(tz="UTC")
                seen = []

                def spy(cmd, **kw):
                    seen.append((list(cmd), dict(kw)))
                    return run(cmd, **kw)

                with root_ctx() as d, contextlib.redirect_stdout(io.StringIO()):
                    rc = cmd_check(root=d, container=container, run=spy)
                self.assertEqual(rc, 0)
                for sql in (SQL_TIMEZONE, SQL_TIMEZONE_SOURCE):
                    tz = [(c, kw) for c, kw in seen if c[-1] == sql]
                    self.assertEqual(len(tz), 1, msg=seen)
                    cmd, kw = tz[0]
                    self.assertEqual(cmd, _db_base(container) + [
                        "psql", "-X", "-U", DB_USER, "-d", DB_NAME, "-tA", "-v",
                        "ON_ERROR_STOP=1", "-c", sql])
                    self.assertEqual([x for x in cmd if "PGTZ" in x or "PGOPTIONS" in x], [])
                    self.assertNotIn("env", kw)
                psqls = [c for c, _ in seen if "psql" in c]
                self.assertEqual(len(psqls), 5, msg=seen)
                self.assertTrue(all(c[c.index("psql") + 1] == "-X" for c in psqls), msg=psqls)
                # 鑑別力自保：同一 run 之 pg_dump 呼叫確帶 PGTZ=UTC——掃描法看得見 PGTZ
                dumps = [c for c, _ in seen if "pg_dump" in c]
                self.assertEqual(len(dumps), 1)
                self.assertIn("PGTZ=UTC", dumps[0])


class TestTimezoneSource(unittest.TestCase):
    """時區來源前置（ADR-00059 決定 3 之判準前提）：SHOW timezone 讀的是 session 生效值——psql 在容器內
    繼承容器環境，目標容器環境帶 PGTZ 或 PGOPTIONS（-c timezone=…）時連線啟動參數即以連線端值覆蓋、
    pg_settings 之 source＝client；psqlrc 之 SET timezone 則 source＝session。兩者皆使伺服器非 UTC 而
    SHOW 讀到 UTC、值判準恆綠。故 SHOW 之後緊接查來源：client／session＝rc 2 附補救、不往下照相比對；
    伺服器側來源（命令列、設定檔、ALTER DATABASE／ALTER ROLE、預設值）放行、值由 SHOW 判準判。
    撈取為空＝判準失準、同紅（掃描面空集合即紅）。"""

    SERVER_SIDE = ("command line", "configuration file", "default", "database", "user",
                   "database user")

    def test_judgement_server_side_sources_pass(self):
        for source in self.SERVER_SIDE:
            with self.subTest(source=source):
                self.assertIsNone(timezone_source_problem(source))

    def test_judgement_client_side_sources_red_with_remedy(self):
        for source in ("client", "session"):
            with self.subTest(source=source):
                msg = timezone_source_problem(source)
                self.assertIsNotNone(msg)
                self.assertIn(f"source＝{source!r}", msg)
                self.assertIn("連線端", msg)
                self.assertIn("PGTZ", msg)
                self.assertIn("PGOPTIONS", msg)
                self.assertIn("psqlrc", msg)
                self.assertIn("ADR-00059", msg)

    def test_judgement_empty_red(self):
        msg = timezone_source_problem("")
        self.assertIsNotNone(msg)
        self.assertIn("為空", msg)

    def test_cmd_check_client_side_source_rc2_before_snapshot(self):
        for source in ("client", "session"):
            with self.subTest(source=source):
                calls, run, root_ctx = _check_fake(tz="UTC", source=source)
                err, out = io.StringIO(), io.StringIO()
                with root_ctx() as d, contextlib.redirect_stderr(err), \
                        contextlib.redirect_stdout(out):
                    rc = cmd_check(root=d, run=run)
                msg = err.getvalue()
                self.assertEqual(rc, 2, msg=msg)
                # SHOW 之後緊接來源查詢、且不往下照相／dump
                self.assertEqual(calls, [SQL_TIMEZONE, SQL_TIMEZONE_SOURCE])
                self.assertIn(f"source＝{source!r}", msg)
                self.assertNotIn("self-test", msg)       # 鑑別力自保：rc 2 來自來源前置
                self.assertEqual(out.getvalue(), "")

    def test_cmd_check_server_side_source_proceeds_rc0(self):
        calls, run, root_ctx = _check_fake(tz="UTC", source="configuration file")
        out = io.StringIO()
        with root_ctx() as d, contextlib.redirect_stdout(out):
            rc = cmd_check(root=d, run=run)
        self.assertEqual(rc, 0)
        self.assertEqual(calls[:3], [SQL_TIMEZONE, SQL_TIMEZONE_SOURCE, SQL_COLUMNS])
        self.assertIn("[check] ✓ 時區：SHOW timezone＝UTC（source＝configuration file）",
                      out.getvalue())


class TestTimeColumnTypes(unittest.TestCase):
    """全時間欄型別斷言（憲法 §I.6 時間點欄通則、ADR-00060 決定 2）：以右源 columns 照相判定——
    無時區 timestamp（含精度與陣列形）一律紅；date（含陣列形）須列於 DATE_COLUMNS_REGISTERED
    （鍵＝(表, 欄)）方過；timestamptz 綠且計數；time／interval 不在射程。"""

    @staticmethod
    def _c(t, c, typ):
        return {"table": t, "column": c, "ordinal": 1, "type": typ,
                "nullable": True, "default": None}

    def test_timestamptz_green_and_counted(self):
        cols = [self._c("t", "a", TS_TZ), self._c("t", "b", "timestamp(3) with time zone"),
                self._c("t", "c", "timestamp with time zone[]"), self._c("t", "id", "bigint"),
                self._c("t", "d", "time without time zone"),
                self._c("t", "e", "time with time zone"), self._c("t", "f", "interval"),
                self._c("t", "g", "daterange"), self._c("t", "h", "datemultirange")]
        self.assertEqual(audit_time_columns(cols, {}), ([], 3, 0))

    def test_naive_timestamp_red_all_forms(self):
        for typ in ("timestamp without time zone", "timestamp(3) without time zone",
                    "timestamp without time zone[]", "timestamp(6) without time zone[]"):
            fnd, n_tz, _ = audit_time_columns([self._c("t_x", "happened_at", typ)], {})
            self.assertEqual(len(fnd), 1, msg=typ)
            self.assertIn("t_x.happened_at", fnd[0])
            self.assertIn(typ, fnd[0])
            self.assertIn("憲法 §I.6 時間點欄通則", fnd[0])
            self.assertIn("ADR-00060", fnd[0])
            self.assertEqual(n_tz, 0)

    def test_naive_timestamp_not_legalized_by_date_roster(self):
        fnd, _, _ = audit_time_columns(
            [self._c("t_x", "happened_at", "timestamp without time zone")],
            {("t_x", "happened_at"): "specs/999-x/spec.md FR-001"})
        self.assertEqual(len(fnd), 1)

    def test_unregistered_date_red(self):
        for typ in ("date", "date[]"):
            fnd, _, n_date = audit_time_columns([self._c("t_x", "birthday", typ)], {})
            self.assertEqual(len(fnd), 1, msg=typ)
            self.assertIn("t_x.birthday", fnd[0])
            self.assertIn("未登記", fnd[0])
            self.assertIn("DATE_COLUMNS_REGISTERED", fnd[0])
            self.assertIn("非演進帳", fnd[0])
            self.assertIn("憲法 §I.6 時間點欄通則", fnd[0])
            self.assertIn("ADR-00060", fnd[0])
            self.assertEqual(n_date, 0)

    def test_registered_date_green_and_counted(self):
        reg = {("t_x", "birthday"): "specs/999-x/spec.md FR-001"}
        self.assertEqual(
            audit_time_columns([self._c("t_x", "birthday", "date"),
                                self._c("t_x", "created_at", TS_TZ)], reg), ([], 1, 1))

    def test_registration_keyed_by_table_and_column(self):
        reg = {("t_x", "birthday"): "specs/999-x/spec.md FR-001"}
        fnd, _, _ = audit_time_columns([self._c("t_y", "birthday", "date")], reg)
        self.assertEqual(len(fnd), 1)
        self.assertIn("t_y.birthday", fnd[0])

    def test_default_roster_is_module_constant(self):
        fnd, _, _ = audit_time_columns([self._c("t_x", "birthday", "date")])
        self.assertEqual(len(fnd), 1)        # 名冊現為空：未傳 registered＝讀本檔常數

    def test_cmd_check_wiring_naive_red_rc1(self):
        fx = load_fixtures(REPO_ROOT)
        cols = json.loads(json.dumps(fx["columns"]))
        hit = [c for c in cols if (c["table"], c["column"]) == ("sys_token", "expires_at")]
        self.assertEqual(len(hit), 1)
        hit[0]["type"] = "timestamp without time zone"
        _calls, run, root_ctx = _check_fake(columns=cols)
        err = io.StringIO()
        with root_ctx() as d, contextlib.redirect_stderr(err), \
                contextlib.redirect_stdout(io.StringIO()):
            rc = cmd_check(root=d, run=run)
        msg = err.getvalue()
        self.assertEqual(rc, 1, msg=msg)
        self.assertIn("DRIFT [時間欄] sys_token.expires_at", msg)
        self.assertIn("ADR-00060", msg)
        self.assertIn("[時間欄] 項除外", msg)      # 漂移總述不對本項宣稱演進帳為合法化路徑


class TestDockerUnavailable(unittest.TestCase):
    """docker 不可執行（OSError；不在 PATH／CLI 缺）＝環境異常 GateError→rc 2——
    非 rc 1 漂移、非裸 traceback（契約 gates.md §0；RUNBOOK §12 依碼判讀之根據）。
    注意與 daemon 停擺區分：後者 docker 有跑、回非零、走既有 rc≠0 分支。"""

    @staticmethod
    def _no_docker(cmd, **kw):
        raise FileNotFoundError(2, "No such file or directory", "docker")

    def test_psql_oserror_to_gateerror(self):
        with self.assertRaisesRegex(GateError, "無法執行 docker"):
            psql("SELECT 1", parse=True, run=self._no_docker)

    def test_pg_dump_oserror_to_gateerror(self):
        with self.assertRaisesRegex(GateError, "無法執行 docker"):
            pg_dump_data(run=self._no_docker)

    def test_cmd_check_rc2_with_remedy(self):
        """cmd_check 層：左源全綠後右源照相撞 OSError → rc 2 附補救、絕不判漂移。"""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(cmd_check(run=self._no_docker), 2)
        self.assertIn("無法執行 docker", err.getvalue())
        self.assertIn("--container", err.getvalue())


class TestDataModelParse(unittest.TestCase):
    DM = ("## 2. 逐表欄序定稿\n\n### t_a（2 欄；變體 A）\n\n"
          "| # | 欄 | 型別 | NULL | default | 註 |\n|---|---|---|---|---|---|\n"
          "| 1 | id | bigint | NN | —— |  |\n| 2 | name | text | 可空 | —— |  |\n\n"
          + "".join(f"### t_{c}（1 欄）\n\n| # | 欄 | 型別 | NULL | default | 註 |\n"
                    "|---|---|---|---|---|---|\n| 1 | id | bigint | NN | —— |  |\n\n"
                    for c in "bcdefghijklmn")
          + "## 3. 史料\n")

    def test_parse_and_self_check(self):
        got = parse_data_model_order(self.DM)
        self.assertEqual(got["t_a"], ["id", "name"])
        self.assertEqual(len(got), 14)

    def test_declared_count_mismatch_fail_loud(self):
        with self.assertRaisesRegex(GateError, "解析自檢敗"):
            parse_data_model_order(self.DM.replace("t_a（2 欄", "t_a（3 欄"))

    def test_real_data_model_parses(self):
        """對現庫 data-model 實解析：14 親排表、總欄 158（凍結定稿字面）。"""
        got = load_data_model_order(REPO_ROOT)
        self.assertEqual(len(got), 14)
        self.assertEqual(sum(len(v) for v in got.values()), 158)
        self.assertEqual(len(got["sys_user"]), 17)


class TestAuditEngine(unittest.TestCase):
    def test_unknown_c_subtype_fail_loud(self):
        amap = [{"table": "t_mystery", "label": "C join·狀態機",
                 "active_unique": None, "note": ""}]
        cols = [{"table": "t_mystery", "column": "id", "ordinal": 1,
                 "type": "bigint", "nullable": False, "default": None}]
        with self.assertRaisesRegex(GateError, "子型規則未硬編碼"):
            audit_archetype(amap, cols, [], [])

    def test_table_guard_both_ways(self):
        amap = [{"table": "t_biz", "label": "A 業務全六欄",
                 "active_unique": None, "note": ""}]
        cols = [{"table": "t_other", "column": "id", "ordinal": 1,
                 "type": "bigint", "nullable": False, "default": None}]
        f = audit_archetype(amap, cols, [], [])
        self.assertTrue(any("t_other 未登記" in x for x in f))
        # 補救指向歸屬帳＋演進帳 add_table（schema-definition §1 留 001 基線＝ADR-00087 決定 7）
        self.assertTrue(any("t_other 未登記" in x and "archetype-map.json" in x
                            and "add_table" in x and "ADR-00087" in x for x in f), f)
        self.assertTrue(any("t_biz 不在實庫" in x for x in f))

    def test_created_by_nn_roster_enforced(self):
        """created_by 可空性顯式驗：非 NN 四表卻 NN＝紅。"""
        amap = [{"table": "t_log2", "label": "B append-only",
                 "active_unique": None, "note": ""}]
        cols = [
            {"table": "t_log2", "column": "created_at", "ordinal": 1, "type": TS_TZ,
             "nullable": False, "default": "now()"},
            {"table": "t_log2", "column": "created_by", "ordinal": 2,
             "type": "bigint", "nullable": False, "default": None},
        ]
        f = audit_archetype(amap, cols, [], [])
        self.assertTrue(any("created_by｜可空性顯式驗不符" in x for x in f))


class TestAuditBForbiddenPrefix(unittest.TestCase):
    """rev5:B-012（rev5:ADR 0016）變體 B 禁欄三向紅綠：①前綴新欄（updated_fields）紅——具名四欄
    時代的漏網形；②具名豁免清單加列後綠——正規出口；③具名四欄仍紅——前綴判準涵蓋原
    判準、守門不縮水。"""

    A_MAP = [{"table": "t_log2", "label": "B append-only",
              "active_unique": None, "note": ""}]

    def _cols(self, extra):
        return [
            {"table": "t_log2", "column": "id", "ordinal": 1, "type": "bigint",
             "nullable": False, "default": None},
            {"table": "t_log2", "column": "created_at", "ordinal": 2, "type": TS_TZ,
             "nullable": False, "default": "now()"},
            {"table": "t_log2", "column": "created_by", "ordinal": 3, "type": "bigint",
             "nullable": True, "default": None},
            {"table": "t_log2", "column": extra, "ordinal": 4, "type": "jsonb",
             "nullable": True, "default": None},
        ]

    def test_1_prefix_new_column_red(self):
        for col in ("updated_fields", "deleted_flag"):
            f = audit_archetype(self.A_MAP, self._cols(col), [], [])
            self.assertTrue(any(f"禁欄 {col}" in x for x in f), msg=(col, f))

    def test_2_exempt_listed_then_green(self):
        key = ("t_log2", "updated_fields")
        AUDIT_B_EXEMPT[key] = "測試豁免：payload 欄（jsonb 記變更欄集）——非審計欄"
        try:
            f = audit_archetype(self.A_MAP, self._cols("updated_fields"), [], [])
            self.assertEqual([x for x in f if "禁欄" in x], [])
        finally:
            del AUDIT_B_EXEMPT[key]

    def test_3_named_four_still_red(self):
        for col in ("updated_at", "updated_by", "deleted_at", "deleted_by"):
            f = audit_archetype(self.A_MAP, self._cols(col), [], [])
            self.assertTrue(any(f"禁欄 {col}" in x for x in f), msg=(col, f))


class TestMapAssertions(unittest.TestCase):
    def _map(self, tables):
        return {"lineage": "x", "usage": "y", "tables": tables}

    def _load(self, data):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, ARCHETYPE_MAP)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False)
            return load_archetype_map(d)

    def test_label_out_of_domain(self):
        with self.assertRaisesRegex(GateError, "值域外"):
            self._load(self._map([{"table": "t", "label": "E 神秘",
                                   "active_unique": None, "note": ""}]))

    def test_duplicate_table(self):
        row = {"table": "t", "label": "D 治理", "active_unique": None, "note": ""}
        with self.assertRaisesRegex(GateError, "重複登記"):
            self._load(self._map([row, dict(row)]))

    def test_missing_key(self):
        with self.assertRaisesRegex(GateError, "鍵集須恰為"):
            self._load(self._map([{"table": "t", "label": "D 治理"}]))

    def test_real_map_day1_form(self):
        """現庫 archetype-map 實載：恰 15 筆（gates.md §3 Day-1 形）＋load 斷言全過。"""
        rows = load_archetype_map(REPO_ROOT)
        self.assertEqual(len(rows), 15)
        self.assertEqual(sorted(r["table"] for r in rows if r["label"] == LABELS[0]),
                         ["sys_ip_rule", "sys_menu", "sys_role", "sys_user",
                          "system_settings"])


class TestAuditArchetypeNegative(unittest.TestCase):
    """audit 變體判準的負向覆蓋（RL-0080「變異要打在判準上」；`docs/ops/reference-src/schema-gates.md` §4 negative 第六類）。
    右源＝真凍結 fixtures ⊕ 真 archetype-map，離線注入假漂移逐條必紅：判準面任一腿被拿掉即有案轉紅。
    ★不同於本檔其餘 negative 組：那些注入的是「實庫漂移」、本組注入的是「變體驗則會不會抓」。"""

    @classmethod
    def setUpClass(cls):
        cls.fix = load_fixtures(REPO_ROOT)
        cls.map_rows = load_archetype_map(REPO_ROOT)

    def _run(self, mutate=None):
        cols = json.loads(json.dumps(self.fix["columns"]))
        idxs = json.loads(json.dumps(self.fix["indexes"]))
        cons = json.loads(json.dumps(self.fix["constraints"]))
        if mutate:
            mutate(cols, idxs, cons)
        return audit_archetype(self.map_rows, cols, idxs, cons)

    @staticmethod
    def _col(cols, table, name):
        for c in cols:
            if c["table"] == table and c["column"] == name:
                return c
        raise AssertionError(f"{table}.{name} 不在凍結 fixtures（測試前提壞了）")

    def _red(self, mutate, *needles):
        f = self._run(mutate)
        self.assertTrue(any(all(n in x for n in needles) for x in f),
                        f"期望命中 {needles}、實得 {f}")

    def test_0_real_fixtures_green(self):
        self.assertEqual(self._run(), [])

    def test_a_type_leg(self):
        self._red(lambda c, i, n: self._col(c, "sys_user", "deleted_at").update(type="text"),
                  "sys_user.deleted_at", "型別")

    def test_a_nullable_leg(self):
        self._red(lambda c, i, n: self._col(c, "sys_user", "created_at").update(nullable=True),
                  "sys_user.created_at", "可空性")

    def test_a_default_leg(self):
        self._red(lambda c, i, n: self._col(c, "sys_user", "created_at").update(default="nope()"),
                  "sys_user.created_at", "default")

    def test_a_column_absent_leg(self):
        def mut(c, i, n):
            c[:] = [x for x in c if not (x["table"] == "sys_user" and x["column"] == "updated_by")]
        self._red(mut, "sys_user", "欄 updated_by 缺席")

    def test_a_active_unique_absent_leg(self):
        def mut(c, i, n):
            i[:] = [x for x in i if x["name"] != "sys_user_user_name_active_uniq"]
        self._red(mut, "sys_user", "活性唯一索引", "不在實庫")

    def test_a_active_unique_reverse_completeness(self):
        """反向完整性（BL-00020）：實庫多一支活性唯一 partial index 而 map 未登記＝紅。"""
        def mut(c, i, n):
            i.append({"table": "sys_user", "name": "sys_user_ghost_active_uniq",
                      "definition": "CREATE UNIQUE INDEX sys_user_ghost_active_uniq ON public.sys_user "
                                    "USING btree (nick_name) WHERE (deleted_at IS NULL)"})
        self._red(mut, "sys_user", "sys_user_ghost_active_uniq", "未登進")
        # 正例：非 partial（無 WHERE）或非 UNIQUE 的索引不入本腿射程
        def mut2(c, i, n):
            i.append({"table": "sys_user", "name": "sys_user_plain_idx",
                      "definition": "CREATE INDEX sys_user_plain_idx ON public.sys_user USING btree (nick_name)"})
        self.assertEqual([x for x in self._run(mut2) if "未登進" in x], [])

    def test_a_active_unique_where_leg(self):
        def mut(c, i, n):
            for x in i:
                if x["name"] == "sys_user_user_name_active_uniq":
                    x["definition"] = x["definition"].split(" WHERE ")[0]
        self._red(mut, "sys_user", "定義缺 WHERE")

    def test_c_subtype_composite_pk_leg(self):
        def mut(c, i, n):
            for x in n:
                if x["table"] == "sys_pwd_custody" and x["definition"].startswith("PRIMARY KEY"):
                    x["definition"] = "PRIMARY KEY (user_id)"
        self._red(mut, "sys_pwd_custody", "複合 PK 期望")

    def test_d_casbin_protected_leg(self):
        self._red(lambda c, i, n: self._col(c, "casbin_rule", "protected").update(default="true"),
                  "casbin_rule.protected", "default")

    def test_d_archive_archived_by_leg(self):
        """憲法 §I.6 變體 D 明列 archive 表帶 archived_by——spec-compliance-001 review M-1 補入驗則。"""
        self._red(lambda c, i, n: self._col(c, "sys_casbin_policy_archive", "archived_by").update(type="text"),
                  "sys_casbin_policy_archive.archived_by", "型別")

    def test_created_by_explicit_nullability_leg(self):
        def mut(c, i, n):
            for x in c:
                if x["column"] == "created_by":
                    x["nullable"] = not x["nullable"]
        self._red(mut, "created_by", "可空性顯式驗不符")


class TestDocCheck(unittest.TestCase):
    """承 rev5:B-010：data-model 文件面（§2 五元組／§6 索引約束／§9 sequences）vs 凍結 fixtures
    機器對賬——兩個已實證解析陷阱之負向測試＋比對器非恆綠自證＋今日真 repo 基線全綠。"""

    DM2 = ("## 2. 逐表欄序定稿\n\n### t_a（2 欄）\n\n"
           "| # | 欄 | 型別 | NULL | default | 註 |\n|---|---|---|---|---|---|\n"
           "| 1 | id | bigint | NN | nextval('s'::regclass) |  |\n"
           "| 2 | memo | text | 可空 | —— |  |\n\n"
           + "".join(f"### t_{c}（1 欄）\n\n| # | 欄 | 型別 | NULL | default | 註 |\n"
                     "|---|---|---|---|---|---|\n| 1 | id | bigint | NN | —— |  |\n\n"
                     for c in "bcdefghijklmn")
           + "## 3. 史料\n")

    DM6 = ("## 6. 索引與約束\n\n總計：索引 1 支、約束 2 條（含 NOT NULL 逐欄形）。\n\n"
           "### t_a\n\n索引（1）：\n\n"
           "- `t_a_pkey`：`CREATE UNIQUE INDEX t_a_pkey ON public.t_a USING btree (id)`\n"
           "\n約束（2）：\n\n"
           "- `t_a_pkey`：`PRIMARY KEY (id)`\n"
           "- `t_a_real_ip_not_null`：`NOT NULL real_ip`（★§4 定稿差異新增、rev4 無）\n\n"
           "## 7. casbin_rule\n")

    DM9 = ("## 9. sequences 落值\n\n| sequence | 落值 |\n|---|---|\n"
           "| t_a_id_seq | 5 |\n"
           "| 其餘 2 支（t_b／t_c） | 未動用（不 setval） |\n\n"
           "## 10. 防回歸\n")
    SEED9 = ("SELECT pg_catalog.setval('public.t_a_id_seq', 5, true);\n"
             "SELECT pg_catalog.setval('public.t_b_id_seq', 1, false);\n"
             "SELECT pg_catalog.setval('public.t_c_id_seq', 1, false);\n")

    def _fx(self):
        cols = [{"table": "t_a", "column": "id", "ordinal": 1, "type": "bigint",
                 "nullable": False, "default": "nextval('s'::regclass)"},
                {"table": "t_a", "column": "memo", "ordinal": 2, "type": "text",
                 "nullable": True, "default": None}]
        for c in "bcdefghijklmn":
            cols.append({"table": f"t_{c}", "column": "id", "ordinal": 1,
                         "type": "bigint", "nullable": False, "default": None})
        return {"columns": cols,
                "indexes": [{"table": "t_a", "name": "t_a_pkey",
                             "definition": "CREATE UNIQUE INDEX t_a_pkey ON public.t_a"
                                           " USING btree (id)"}],
                "constraints": [{"table": "t_a", "name": "t_a_pkey",
                                 "definition": "PRIMARY KEY (id)"},
                                {"table": "t_a", "name": "t_a_real_ip_not_null",
                                 "definition": "NOT NULL real_ip"}]}

    def test_missing_fixtures_root_is_rc2(self):
        """負向：fixtures 缺席＝環境／結構異常 rc 2（GateError 路徑、非裸例外）。"""
        with tempfile.TemporaryDirectory() as td, \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cmd_doccheck(root=td), 2)

    def test_trap1_dash_default_is_none(self):
        """陷阱①：§2 default 欄「——」＝無 default（None）——取字面比對即全表假紅。"""
        five = parse_data_model_five(self.DM2)
        self.assertEqual(five["t_a"][1], (2, "memo", "text", True, None))
        self.assertEqual(five["t_a"][0],
                         (1, "id", "bigint", False, "nextval('s'::regclass)"))

    def test_trap2_trailing_note_parsed(self):
        """陷阱②：§6 條目行可帶尾註（實例＝sys_operation_log_real_ip_not_null 行帶
        「（★§4 定稿差異新增、rev4 無）」）——嚴格行尾錨會少數一條、宣告支數自檢連帶炸。"""
        idx, con = parse_data_model_defs(self.DM6)
        self.assertEqual(len(idx), 1)
        self.assertEqual(con[("t_a", "t_a_real_ip_not_null")], "NOT NULL real_ip")

    def test_declared_count_mismatch_fail_loud(self):
        with self.assertRaisesRegex(GateError, "自檢敗"):
            parse_data_model_defs(self.DM6.replace("約束（2）", "約束（3）"))

    def test_comparator_red_on_single_field(self):
        """比對器非恆綠自證：單格改動即紅、逐項指名（§2 型別格＋§6 定義文字各一）。"""
        five = parse_data_model_five(self.DM2)
        idx, con = parse_data_model_defs(self.DM6)
        fx = self._fx()
        self.assertEqual(doccheck_findings(five, idx, con, fx), [])   # 健康對綠
        fx["columns"][0]["type"] = "integer"
        f = doccheck_findings(five, idx, con, fx)
        self.assertTrue(any("[doccheck·§2] t_a.id" in x for x in f), msg=f)
        fx2 = self._fx()
        fx2["constraints"][0]["definition"] = "PRIMARY KEY (memo)"
        f2 = doccheck_findings(five, idx, con, fx2)
        self.assertTrue(any("[doccheck·§6] constraints/t_a/t_a_pkey" in x
                            for x in f2), msg=f2)

    def test_order_exempt_not_false_reported(self):
        """casbin_rule 依 §7／ORDER_EXEMPT 本就不在 §2——fixtures 面豁免、勿誤報。"""
        five = parse_data_model_five(self.DM2)
        idx, con = parse_data_model_defs(self.DM6)
        fx = self._fx()
        fx["columns"].append({"table": "casbin_rule", "column": "id", "ordinal": 1,
                              "type": "bigint", "nullable": False, "default": None})
        self.assertEqual([x for x in doccheck_findings(five, idx, con, fx)
                          if "§2" in x], [])

    def test_9_parse_and_self_check(self):
        """§9 解析：具名落值＋其餘表名清單；[`parse_data_model_sequences`] 之**七條** fail-loud
        判準逐條打紅（缺一即該判準零紅綠載體、被「簡化」掉時零徵狀）：①段落定位失敗 ②具名列
        重複 ③「其餘 N 支」列重複 ④「其餘 N 支」列缺席 ⑤零具名落值列 ⑥宣告數 vs 解析數自檢
        ⑦具名列與其餘列重疊。⑦尤關鍵——它是「同一支既列具名落值、又列入其餘未動用」這種
        §9 自相矛盾的唯一守門：拆掉後 [`doccheck_sequence_findings`] 會以 (1, false) 靜默覆寫
        具名落值、findings 回空而判綠（契約 gates.md §0 防恆綠假閘）。
        各案皆以 DM9 合成字串就地變形、不碰 specs/ 真檔；replace 若失錨＝退回健康 DM9、解析
        成功、assertRaises 落空＝本測紅（錨自保、無須另設 count 斷言）。"""
        named, rest = parse_data_model_sequences(self.DM9)
        self.assertEqual(named, {"t_a_id_seq": 5})
        self.assertEqual(rest, ["t_b", "t_c"])
        with self.assertRaisesRegex(GateError, "§9 解析自檢敗"):
            parse_data_model_sequences(self.DM9.replace("其餘 2 支", "其餘 3 支"))
        with self.assertRaisesRegex(GateError, "§9 段落定位失敗"):
            parse_data_model_sequences(self.DM2)
        with self.assertRaisesRegex(GateError, "零具名 sequence 落值列"):
            parse_data_model_sequences(self.DM9.replace("| t_a_id_seq | 5 |\n", ""))
        with self.assertRaisesRegex(GateError, "§9 重複條目"):
            parse_data_model_sequences(self.DM9.replace(
                "| t_a_id_seq | 5 |\n", "| t_a_id_seq | 5 |\n| t_a_id_seq | 6 |\n"))
        with self.assertRaisesRegex(GateError, "「其餘 N 支」列重複"):
            parse_data_model_sequences(self.DM9.replace(
                "| 其餘 2 支（t_b／t_c） | 未動用（不 setval） |\n",
                "| 其餘 2 支（t_b／t_c） | 未動用（不 setval） |\n"
                "| 其餘 2 支（t_b／t_c） | 未動用（不 setval） |\n"))
        with self.assertRaisesRegex(GateError, "列缺席"):
            parse_data_model_sequences(self.DM9.replace(
                "| 其餘 2 支（t_b／t_c） | 未動用（不 setval） |\n", ""))
        with self.assertRaisesRegex(GateError, "具名列與其餘列重疊"):
            parse_data_model_sequences(self.DM9.replace(
                "其餘 2 支（t_b／t_c）", "其餘 3 支（t_a／t_b／t_c）"))

    def test_9_comparator_red_on_value_and_roster(self):
        """§9 比對器非恆綠自證：健康對綠；具名落值改一格紅；其餘支 seed 側非 (1,false) 紅；
        名冊單邊多出／缺少各紅；seed 側零 setval 行＝GateError。"""
        named, rest = parse_data_model_sequences(self.DM9)
        self.assertEqual(doccheck_sequence_findings(named, rest, self.SEED9), [])
        f = doccheck_sequence_findings({"t_a_id_seq": 6}, rest, self.SEED9)
        self.assertTrue(f and "[doccheck·§9] t_a_id_seq" in f[0] and "文件=(6, 'true')" in f[0],
                        msg=f)
        used = self.SEED9.replace("'public.t_b_id_seq', 1, false", "'public.t_b_id_seq', 2, true")
        f = doccheck_sequence_findings(named, rest, used)
        self.assertTrue(f and "t_b_id_seq" in f[0] and "fixtures=(2, 'true')" in f[0], msg=f)
        f = doccheck_sequence_findings(named, rest + ["t_d"], self.SEED9)
        self.assertEqual(f, ["[doccheck·§9] t_d_id_seq｜文件有、fixtures 無"])
        f = doccheck_sequence_findings(named, rest[:1], self.SEED9)
        self.assertEqual(f, ["[doccheck·§9] t_c_id_seq｜fixtures 有、文件無"])
        with self.assertRaisesRegex(GateError, "零 setval 行"):
            doccheck_sequence_findings(named, rest, "COPY public.t_a (id) FROM stdin;\n\\.\n")

    def test_real_repo_green_rc0(self):
        """今日基線必須全綠（§2 14 表 158 欄、§6 索引 38／約束 101、§9 具名 4＋其餘 7 全等）。"""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cmd_doccheck(REPO_ROOT), 0)
        self.assertIn("§2 五元組：14 親排表 158 欄", out.getvalue())
        self.assertIn("§6 索引 38 支／約束 101 條", out.getvalue())
        self.assertIn("§9 sequences：具名 4 支落值＋其餘 7 支未動用", out.getvalue())
        self.assertIn("名冊 11 支", out.getvalue())


class TestCmdDoccheckWiring(unittest.TestCase):
    """佈線守門（[`cmd_doccheck`] 面）：三個對賬面（§2／§6／§9）的 findings 併入原本只有
    註解宣稱、無機器紅綠——既有測試皆直呼 [`doccheck_findings`]／
    [`doccheck_sequence_findings`] 兩純函數、繞過佈線，故刪掉併入行（或把併入結果換成空
    列）後整套自測照樣全綠、真 repo doccheck 照樣 rc 0、三行摘要照印（摘要只由 parse 結果
    推導、與 findings 併入無關）。本類另立以釘死該佈線（慣例同
    [`TestCmdCheckSeedEmptyWiring`]；rev5:L-018／rev5:L-019 同形；契約 gates.md §0 防恆綠
    假閘）。合成形：凍結基線四件＋data-model 複製入暫存 root、每案只改**文件側**一格 →
    現行佈線 rc 1＋具名 finding；併入行被拆＝本測紅。不碰 specs/ 真檔。"""

    def _root(self, d, edits=()):
        """凍結基線＋data-model 複製入 d；edits＝文件側單格改動（唯一命中自保）。"""
        for rel in TestCmdCheckGreenPath._COPY:
            dst = os.path.join(d, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(REPO_ROOT, rel), dst)
        if edits:
            path = os.path.join(d, DATA_MODEL)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for old, new in edits:
                # 錨自保：改點在真 data-model 失效＝本測紅（非「改了個不存在的字串」假綠）
                self.assertEqual(text.count(old), 1, msg=f"改點非唯一命中：{old}")
                text = text.replace(old, new)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
        return d

    def _run(self, d):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cmd_doccheck(root=d)
        return rc, out.getvalue() + err.getvalue()

    def test_untouched_copy_is_rc0(self):
        """對照組：暫存 root 原封不動＝rc 0——否則以下兩案之紅無鑑別力（複製漏檔也會紅）。"""
        with tempfile.TemporaryDirectory() as d:
            rc, msg = self._run(self._root(d))
        self.assertEqual(rc, 0, msg=msg)

    def test_9_value_edit_reaches_rc1(self):
        """§9 併入行（rev6 新增面）被拆＝本測紅：文件側具名落值改一格 → rc 1 且逐項指名。"""
        with tempfile.TemporaryDirectory() as d:
            rc, msg = self._run(self._root(
                d, [("| casbin_rule_id_seq | 163 |",
                     "| casbin_rule_id_seq | 164 |")]))
        self.assertEqual(rc, 1, msg=msg)
        self.assertIn("[doccheck·§9] casbin_rule_id_seq", msg)

    def test_2_and_6_edits_reach_rc1(self):
        """§2／§6 併入行（承 rev5 既有面、同款未釘）一併釘死：型別格＋約束定義各改一格
        → rc 1 且兩面各自具名。"""
        with tempfile.TemporaryDirectory() as d:
            rc, msg = self._run(self._root(d, [
                ("| 13 | session_policy | character varying(20) | NN |",
                 "| 13 | session_policy | text | NN |"),
                ("- `sys_user_pkey`：`PRIMARY KEY (id)`",
                 "- `sys_user_pkey`：`PRIMARY KEY (user_name)`")]))
        self.assertEqual(rc, 1, msg=msg)
        self.assertIn("[doccheck·§2] sys_user.session_policy", msg)
        self.assertIn("[doccheck·§6] constraints/sys_user/sys_user_pkey",
                      msg)


# ── offline 自測共用件（植入一律在暫存根、真檔零改）──────────────────────────
_OFFLINE_M0003 = os.path.join(OFFLINE_MIGRATION_DIR, "m0003_seed_button_governance.rs")

# m0003 三常數展開之期望字面——逐字手寫自真檔原文（續行吃掉換行與次行前導空白、raw 字串原樣、
# concat! 依項序串接），不自受測函式衍生（T006 ①）。
_M0003_UP_1 = ("UPDATE casbin_rule SET protected = TRUE WHERE (id, v1) IN "
               "((58, 'role:add'), (59, 'role:edit'), (60, 'role:delete'), "
               "(61, 'menu:add'), (62, 'menu:edit'), (63, 'menu:delete'))"
               " AND ptype = 'p' AND v0 = 'R_SUPER' AND v2 = 'button' AND protected = FALSE")
_M0003_UP_3 = ("INSERT INTO casbin_rule "
               "(id, ptype, v0, v1, v2, v3, v4, v5, protected, created_at, created_by) "
               "VALUES (164, 'p', 'R_SUPER', 'ipRule:unlock', 'button', '', '', '', FALSE, "
               "'2026-08-05T00:00:00+00:00', NULL)")
_M0003_MENU_78_BEFORE = (
    '[{"code":"ipRule:add","desc":"新增IP規則"},{"code":"ipRule:edit","desc":"編輯IP規則"},'
    '{"code":"ipRule:delete","desc":"刪除IP規則"},{"code":"ipRule:restore","desc":"恢復IP規則"}]')
_M0003_MENU_78_AFTER = (
    '[{"code":"ipRule:add","desc":"新增IP規則"},{"code":"ipRule:edit","desc":"編輯IP規則"},'
    '{"code":"ipRule:delete","desc":"刪除IP規則"},{"code":"ipRule:restore","desc":"恢復IP規則"},'
    '{"code":"ipRule:unlock","desc":"解鎖來源IP"}]')
_M0003_UP_4 = (f"UPDATE sys_menu SET buttons = '{_M0003_MENU_78_AFTER}'::jsonb WHERE id = 78 "
               f"AND buttons = '{_M0003_MENU_78_BEFORE}'::jsonb")

# 合法最小 delta 樣本（四句形各一：let／execute_unprepared 字面／expect_rows 常數／Ok）
_OFFLINE_MINIMAL_RS = '''use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        let db = manager.get_connection();
        db.execute_unprepared("SELECT setval('casbin_rule_id_seq', 164, true)").await?;
        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        let db = manager.get_connection();
        expect_rows(db, "down", DOWN_SQL, 0, TAIL).await?;
        Ok(())
    }
}

const TAIL: &str = "尾句";
const DOWN_SQL: &str = "SELECT setval('casbin_rule_id_seq', 163, true)";
'''


def _offline_write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def _offline_edited(tc, rel, edits, src_root=REPO_ROOT):
    """讀 src_root 之 rel 原文、依 edits（[(舊, 新)]）逐一替換後回文——舊字串須唯一命中（錨自保：改點失效＝
    該案紅、非「改了個不存在的字串」假綠）。"""
    with open(os.path.join(src_root, rel), encoding="utf-8") as fh:
        text = fh.read()
    for old, new in edits:
        tc.assertEqual(text.count(old), 1, msg=f"改點非唯一命中：{old[:80]}")
        text = text.replace(old, new)
    return text


# 判準①k 植入（m0003 副本之 edits）：six_button_rows! 之定義不在 UP_1_PROTECT_SIX 之文本作用域——①定義在後（UP_1_PROTECT_SIX
# 移至定義之前、原處改名 UP_1_OLD；配 `use … as six_button_rows` 匯入＝Rust 循路徑綁到匯入者）②定義移入 inline mod ③定義移入函式本體
_M0003_UP_1_HEAD = "const UP_1_PROTECT_SIX: &str = concat!("
_M0003_SIX_HEAD = "macro_rules! six_button_rows {\n"
_M0003_SIX_TAIL = "         (61, 'menu:add'), (62, 'menu:edit'), (63, 'menu:delete'))\"\n    };\n}\n"
_M0003_USE_LINE = "use sea_orm_migration::sea_orm::ConnectionTrait;\n"
_OFFLINE_MACRO_SCOPE_EDITS = (
    ("定義在後（配 use 匯入）", [
        (_M0003_USE_LINE, _M0003_USE_LINE + "use crate::evil_six as six_button_rows;\n"),
        (_M0003_UP_1_HEAD, "const UP_1_OLD: &str = concat!("),
        ("/// 六碼之 `(id, v1)` 逐對",
         _M0003_UP_1_HEAD + '\n    "UPDATE casbin_rule SET protected = TRUE WHERE (id, v1) IN ",\n    six_button_rows!(),\n'
         "    \" AND ptype = 'p' AND v0 = 'R_SUPER' AND v2 = 'button' AND protected = FALSE\"\n);\n\n"
         "/// 六碼之 `(id, v1)` 逐對")]),
    ("inline mod 內", [(_M0003_SIX_HEAD, "mod inner {\n" + _M0003_SIX_HEAD), (_M0003_SIX_TAIL, _M0003_SIX_TAIL + "}\n")]),
    ("函式本體內", [(_M0003_SIX_HEAD, "fn helper() {\n" + _M0003_SIX_HEAD), (_M0003_SIX_TAIL, _M0003_SIX_TAIL + "}\n")]),
)

# 判準①m 植入（m0003 副本之 edits；(標籤, edits, 指名字樣)）：前四組各只觸一款（①頂層唯一 impl ②MigrationTrait 之綁定
# ③Migration 之綁定 ④零 cfg），末三組＝審查所植之替身實作（多款併觸）。「head 冠 #[cfg(test)]」＝遷移二進位所跑之實作在他檔
# （lib.rs 等；本腿不讀）之途徑。
_M0003_HEAD = "#[async_trait::async_trait]\nimpl MigrationTrait for Migration {"
_M0003_STRUCT = "#[derive(DeriveMigrationName)]\npub struct Migration;"
_M0003_PRELUDE = "use sea_orm_migration::prelude::*;\n"
_M0003_IMPL_END = "        Ok(())\n    }\n}\n\n/// `up` 失敗訊息尾句"
_OFFLINE_EVIL_UP = ('    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {\n'
                    '        let db = manager.get_connection();\n'
                    '        db.execute_unprepared("DELETE FROM sys_user WHERE id = 1; DROP TABLE sys_role").await?;\n'
                    '        Ok(())\n    }\n'
                    '    async fn down(&self, _m: &SchemaManager) -> Result<(), DbErr> {\n        Ok(())\n    }\n')
_OFFLINE_EVIL_QUALIFIED = ("#[cfg(not(test))]\n#[async_trait::async_trait]\n"
                           "impl sea_orm_migration::MigrationTrait for Migration {\n" + _OFFLINE_EVIL_UP + "}\n\n")
_OFFLINE_EVIL_MOD = ("mod real {\n    use sea_orm_migration::prelude::*;\n    pub struct Real;\n"
                     '    impl MigrationName for Real {\n        fn name(&self) -> &str {\n'
                     '            "m0003_seed_button_governance"\n        }\n    }\n'
                     "    #[async_trait::async_trait]\n    impl MigrationTrait for Real {\n" + _OFFLINE_EVIL_UP + "    }\n}\n"
                     "#[cfg(not(test))]\npub use real::Real as Migration;\n\n")
# 判準①j／①n 植入之檔外巨集檔：同名 six_button_rows! 之展開閉合元組 IN 後藏一句 DELETE（遷移二進位所編者）
_OFFLINE_EVIL_SIX = ('macro_rules! six_button_rows {\n    () => {\n        "((58, \'role:add\'))) ; DELETE FROM sys_user '
                     'WHERE (1, 1) IN ((1, 1)"\n    };\n}\n')
_OFFLINE_IMPL_BINDING_EDITS = (
    ("inherent impl", [(_M0003_UP_1_HEAD, "struct Holder;\nimpl Holder {}\n\n" + _M0003_UP_1_HEAD)], "`impl` 詞素須恰一"),
    ("型別位置之 impl Trait", [(_M0003_UP_1_HEAD, "fn helper(_x: impl Sized) {}\n\n" + _M0003_UP_1_HEAD)],
     "`impl` 詞素須恰一"),
    ("head 移入 inline mod", [(_M0003_HEAD, "mod inner {\nuse super::*;\n" + _M0003_HEAD),
                            (_M0003_IMPL_END, "        Ok(())\n    }\n}\n}\n\n/// `up` 失敗訊息尾句")], "須在檔案頂層"),
    ("不改名之他路徑匯入", [(_M0003_USE_LINE, _M0003_USE_LINE + "use crate::fake::MigrationTrait;\n")],
     "MigrationTrait 須只出現於 head"),
    ("use … as MigrationTrait", [(_M0003_USE_LINE, _M0003_USE_LINE + "use crate::fake::Other as MigrationTrait;\n")],
     "MigrationTrait 須只出現於 head"),
    ("檔內 trait MigrationTrait", [(_M0003_UP_1_HEAD, "trait MigrationTrait {}\n\n" + _M0003_UP_1_HEAD)],
     "MigrationTrait 須只出現於 head"),
    ("prelude 匯入換為他 glob", [(_M0003_PRELUDE, "use crate::fake::*;\n")], "缺頂層 `use sea_orm_migration::prelude::*;`"),
    ("prelude 匯入在 inline mod 內", [(_M0003_PRELUDE, "mod p {\n    use sea_orm_migration::prelude::*;\n}\nuse crate::fake::*;\n")],
     "缺頂層 `use sea_orm_migration::prelude::*;`"),
    ("use …::Migration 替身", [(_M0003_STRUCT, "pub use crate::m0003_impl::Migration;")], "識別字 Migration 須恰二處"),
    ("use … as Migration", [(_M0003_STRUCT, "pub struct Real;\npub use Real as Migration;")], "識別字 Migration 須恰二處"),
    ("type Migration", [(_M0003_STRUCT, "pub struct Real;\ntype Migration = Real;")], "識別字 Migration 須恰二處"),
    ("他處第二 struct Migration", [(_M0003_UP_1_HEAD, "mod shadow_m {\n    pub struct Migration;\n}\n\n" + _M0003_UP_1_HEAD)],
     "識別字 Migration 須恰二處"),
    ("struct Migration 移入 inline mod", [(_M0003_STRUCT, "mod m {\n    #[derive(DeriveMigrationName)]\n"
                                                         "    pub struct Migration;\n}\npub use m::*;")],
     "識別字 Migration 須恰二處"),
    ("head 冠 #[cfg(test)]", [(_M0003_HEAD, "#[cfg(test)]\n" + _M0003_HEAD)], "含 cfg"),
    ("#[cfg_attr]", [(_M0003_STRUCT, "#[cfg_attr(test, derive(Debug))]\n" + _M0003_STRUCT)], "含 cfg_attr"),
    ("#![cfg]", [(_M0003_PRELUDE, "#![cfg(not(test))]\n" + _M0003_PRELUDE)], "含 cfg"),
    ("cfg!", [(_M0003_UP_1_HEAD, "fn flag() -> bool {\n    cfg!(test)\n}\n\n" + _M0003_UP_1_HEAD)], "含 cfg"),
    ("審查①：cfg 互斥之限定路徑 trait impl", [(_M0003_HEAD, "#[cfg(test)]\n" + _M0003_HEAD),
                                     (_M0003_UP_1_HEAD, _OFFLINE_EVIL_QUALIFIED + _M0003_UP_1_HEAD)], "impl 綁定"),
    ("審查②：cfg 互斥之 inline mod 替身", [(_M0003_STRUCT, "#[cfg(test)]\n" + _M0003_STRUCT),
                                    (_M0003_HEAD, "#[cfg(test)]\n" + _M0003_HEAD),
                                    (_M0003_UP_1_HEAD, _OFFLINE_EVIL_MOD + _M0003_UP_1_HEAD)], "impl 綁定"),
    ("審查③：cfg 互斥之他檔替身", [(_M0003_STRUCT, "#[cfg(test)]\n" + _M0003_STRUCT
                                + "\n#[cfg(not(test))]\npub use crate::m0003_impl::Migration;"),
                               (_M0003_HEAD, "#[cfg(test)]\n" + _M0003_HEAD)], "impl 綁定"),
)


class TestOfflineParse(unittest.TestCase):
    """offline 判準①（解析層；T006）：delta 檔集、Rust 詞素與三件解析（const 右式三形、macro_rules! 單規則
    零引數、impl 內 up／down 本體四句形）、SQL 頂層分句。合成檔一律寫入暫存目錄、真檔零改；
    rc 2 之載體＝GateError（cmd_offline 轉 rc 2；佈線另由 TestOfflineLeg 釘）。"""

    def _parse_edited(self, edits):
        """m0003 真檔副本套 edits 後寫入暫存目錄並解析。"""
        with tempfile.TemporaryDirectory() as d:
            path = _offline_write(d, _OFFLINE_M0003, _offline_edited(self, _OFFLINE_M0003, edits))
            return offline_parse_file(path)

    def _rc2(self, edits, *needles):
        with self.assertRaises(GateError) as cm:
            self._parse_edited(edits)
        for needle in needles:
            self.assertIn(needle, str(cm.exception))
        return str(cm.exception)

    def test_constants_pinned(self):
        self.assertEqual(OFFLINE_MIGRATION_DIR, os.path.join("rust-api", "migration", "src"))
        self.assertEqual(OFFLINE_FIRST_DELTA, 3)

    def test_1_real_m0003_up5_down5_sources_in_call_order(self):
        """①m0003 真檔（現算）：up 5 句、down 5 句，依呼叫序帶來源常數名；未被引用之 UP_FAIL_TAIL／
        DOWN_FAIL_TAIL 不入序列。"""
        got = offline_parse_file(os.path.join(REPO_ROOT, _OFFLINE_M0003))
        self.assertEqual([src for src, _text, _toks in got["up"]],
                         ["UP_1_PROTECT_SIX", "UP_2_DELETE_44", "UP_3_INSERT_164",
                          "UP_4_MENU_78", "UP_5_SETVAL"])
        self.assertEqual([src for src, _text, _toks in got["down"]],
                         ["DOWN_4_MENU_78", "DOWN_3_DELETE_164", "DOWN_2_REINSERT_44",
                          "DOWN_1_UNPROTECT_SIX", "DOWN_5_SETVAL"])

    def test_1_expansions_equal_handwritten_literals(self):
        """①concat!＋巨集（UP_1）、raw 字串巨集兩支（UP_4）、`\\` 續行（UP_2、UP_3）之展開逐字等於手寫期望。"""
        up = {src: text for src, text, _toks in
              offline_parse_file(os.path.join(REPO_ROOT, _OFFLINE_M0003))["up"]}
        self.assertEqual(up["UP_1_PROTECT_SIX"], _M0003_UP_1)
        self.assertEqual(up["UP_3_INSERT_164"], _M0003_UP_3)
        self.assertEqual(up["UP_4_MENU_78"], _M0003_UP_4)
        self.assertEqual(up["UP_2_DELETE_44"],
                         "DELETE FROM casbin_rule WHERE id = 44 AND ptype = 'p' AND v0 = 'R_ADMIN' "
                         "AND v1 = 'user:edit' AND v2 = 'button'")

    def test_1_bare_macro_zero_arg_rhs_positive(self):
        """①右式第二形（檔內巨集零引數呼叫 `<名>!()`）之一正：m0003 真檔無實例，副本把 UP_3_INSERT_164 之右式
        改為 `insert_164!()`、巨集合②之形（RL-0080 一正）→ 展開照算、等於手寫期望。"""
        got = self._parse_edited([(
            'const UP_3_INSERT_164: &str = "INSERT INTO casbin_rule \\\n',
            'macro_rules! insert_164 {\n    () => {\n        "INSERT INTO casbin_rule \\\n'),
            ("'ipRule:unlock', 'button', '', '', '', FALSE, \\\n"
             "     '2026-08-05T00:00:00+00:00', NULL)\";\n",
             "'ipRule:unlock', 'button', '', '', '', FALSE, \\\n"
             "     '2026-08-05T00:00:00+00:00', NULL)\"\n    };\n}\n\n"
             "const UP_3_INSERT_164: &str = insert_164!();\n")])
        self.assertEqual([text for src, text, _t in got["up"] if src == "UP_3_INSERT_164"],
                         [_M0003_UP_3])

    def test_1_literal_sql_arg_trailing_comma_and_folded_call(self):
        """①本體四句形之變體：execute_unprepared 之字面引數（來源記「字面」）、rustfmt 直排引數之尾逗號與
        `.await?` 折行（m0003 之 DOWN_1_UNPROTECT_SIX 即折行形、真檔案已涵蓋）。"""
        with tempfile.TemporaryDirectory() as d:
            path = _offline_write(d, os.path.join(OFFLINE_MIGRATION_DIR, "m0004_x.rs"),
                                  _OFFLINE_MINIMAL_RS.replace(
                                      'expect_rows(db, "down", DOWN_SQL, 0, TAIL).await?;',
                                      'expect_rows(\n            db,\n            "down",\n'
                                      '            DOWN_SQL,\n            0,\n            TAIL,\n'
                                      '        )\n        .await?;'))
            got = offline_parse_file(path)
        self.assertEqual([(s, t) for s, t, _k in got["up"]],
                         [("字面", "SELECT setval('casbin_rule_id_seq', 164, true)")])
        self.assertEqual([(s, t) for s, t, _k in got["down"]],
                         [("DOWN_SQL", "SELECT setval('casbin_rule_id_seq', 163, true)")])

    def test_1_string_escapes_and_nested_block_comment(self):
        """①掃描器之一般字串跳脫逐形還原（`\\"`、`\\'`、`\\\\`、`\\n`、`\\r`、`\\t`、`\\0`、`\\x41`、`\\u{4E2D}` 與帶底線之
        `\\u{4E_2D}`；m0003 真檔字串只有續行、無他跳脫）與巢狀塊註解（內層 `/* */` 計深、外層閉合前之句不入序列）：
        展開逐字等於手寫期望；未支援之跳脫與 `\\u{…}` 壞形＝rc 2 指名。"""
        anchor = "        Ok(())\n    }\n\n    async fn down"
        self.assertEqual(_OFFLINE_MINIMAL_RS.count(anchor), 1)
        rs = _OFFLINE_MINIMAL_RS.replace(
            anchor, "        /* /* 內層 */ db.execute_unprepared(UP_HIDDEN).await?; */\n"
                    "        db.execute_unprepared(UP_ESC).await?;\n" + anchor)
        rs += (r'''const UP_ESC: &str = "UPDATE sys_menu SET buttons = '[{\"code\":\"x\"}]'::jsonb, '''
               r'''menu_name = \'a\\b\nc\rd\te\0f\x41\u{4E2D}\u{4E_2D}\' WHERE id = 1";''' "\n"
               'const UP_HIDDEN: &str = "ALTER TABLE sys_user ADD COLUMN x text";\n')
        want = ("UPDATE sys_menu SET buttons = '[{\"code\":\"x\"}]'::jsonb, "
                "menu_name = 'a\\b\nc\rd\te\0fA中中' WHERE id = 1")
        rel = os.path.join(OFFLINE_MIGRATION_DIR, "m0004_x.rs")
        with tempfile.TemporaryDirectory() as d:
            got = offline_parse_file(_offline_write(d, rel, rs))
        self.assertEqual([(s, t) for s, t, _k in got["up"]],
                         [("字面", "SELECT setval('casbin_rule_id_seq', 164, true)"), ("UP_ESC", want)])
        for bad, needle in (('"a\\qb"', "未支援之跳脫 \\q"), ('"\\u{}"', "\\u{…} 跳脫壞形"),
                            ('"\\u{zz}"', "\\u{…} 跳脫壞形")):
            with self.subTest(bad=bad):
                with tempfile.TemporaryDirectory() as d:
                    path = _offline_write(d, rel, rs + f"const BAD: &str = {bad};\n")
                    with self.assertRaises(GateError) as cm:
                        offline_parse_file(path)
                self.assertIn(needle, str(cm.exception))
                self.assertIn("m0004_x.rs", str(cm.exception))

    def test_1_char_literal_and_lifetime_lexemes(self):
        """①掃描器之字元字面與 lifetime（[`_rust_tokens`] 之 `'` 分支；RL-0080 逐途徑）：字元字面 `'"'`、`'\\''`、`'\\\\'`、
        `'\\u{22}'`、`'a'` 各切為單一詞素（不起字串、不提早閉合、不吞後文）；lifetime `'a`、`'static`、`'_` 止於識別字字元。
        佈線：m0003 副本植 `const Q: char = '"';`，其後接 `#[cfg(not(test))]` 之同名 UP_5_SETVAL 第二宣告（行尾註解含 `"`）
        → rc 2 指名重複定義（字元字面之 `"` 若起字串＝吞掉該宣告、判準①f 被繞過而假綠）。"""
        for src, want in (
                ("'\"' \"s\"", [("other", "'\"'"), ("str", "s")]),
                ("'\\'' \"s\"", [("other", "'\\''"), ("str", "s")]),
                ("'\\\\' \"s\"", [("other", "'\\\\'"), ("str", "s")]),
                ("'\\u{22}' \"s\"", [("other", "'\\u{22}'"), ("str", "s")]),
                ("'a' \"s\"", [("other", "'a'"), ("str", "s")]),
                ("&'a str", [("p", "&"), ("other", "'a"), ("id", "str")]),
                ("'static \"s\"", [("other", "'static"), ("str", "s")]),
                ("<'_> \"s\"", [("p", "<"), ("other", "'_"), ("p", ">"), ("str", "s")])):
            with self.subTest(src=src):
                self.assertEqual([t[:2] for t in _rust_tokens(src, "合成")], want)
        self._rc2([("const UP_FAIL_TAIL: &str =",
                    "const Q: char = '\"';\n#[cfg(not(test))]\n"
                    "const UP_5_SETVAL: &str = \"DELETE FROM sys_role WHERE id = 1\"; // \"\n"
                    "const UP_FAIL_TAIL: &str =")],
                  "m0003_seed_button_governance.rs", "常數 UP_5_SETVAL", "重複定義")

    def test_1_raw_forms_and_continuation_blank_lines(self):
        """①掃描器三途徑（[`_rust_tokens`]／[`_rust_string`]；RL-0080 逐途徑——m0003 真檔只經單個 `#` 之 raw 字串、續行後接非空行、
        無 raw 識別字）：①raw 字串任意個 `#`——`r##"…"##` 內含 `"#` 不提早閉合、值逐字＝手寫期望 ②raw 識別字 `r#<名>` 切為單一識別字
        詞素（佈線：`mod r#shadow;` 照判準①j rc 2 指名，見檔外巨集引入案）③`\\` 續行吃掉換行與其後全部空格、`\\t`、`\\r`、`\\n`（含空行；
        同 rustc 之續行略過集，跨多行只警告、照略）。"""
        self.assertEqual([t[:2] for t in _rust_tokens('r##"UPDATE t SET a = \'"#\' WHERE id = 1"##', "合成")],
                         [("str", "UPDATE t SET a = '\"#' WHERE id = 1")])
        self.assertEqual([t[:2] for t in _rust_tokens("mod r#shadow;", "合成")],
                         [("id", "mod"), ("id", "shadow"), ("p", ";")])
        self.assertEqual([t[:2] for t in _rust_tokens('"p\\\n\n\t\n    q"', "合成")], [("str", "pq")])

    def test_2_rc2_unsupported_char_outside_literals_named(self):
        """②字串、字元字面與註解之外之未支援字元（判準①n [`_rust_unsupported`]）＝rc 2、指名檔、行與碼位——rustc 之切法與本掃描器
        不同處，詞素錯位即可繞過以詞素形比對之判準（例：判準①j 之 `mod`、識別字、`;` 三詞素比對落空）。逐途徑（rustc 皆收、植於
        `#[macro_use]` 檔案模組宣告）：非 ASCII 識別字字元（`#[path]` 配 `mod 影;`、`mod shadow影;`——rustc 依 Unicode XID 收）、rustc
        視為空白而本掃描器不收者介於 `mod` 與名之間（`\\x0b`、`\\x0c`、U+0085、U+200E、U+200F、U+2028、U+2029）；rustc 亦拒之字元
        （他控制字元 `\\x00`、非 ASCII 標點全形分號、反斜線）於詞素層同拒。對照組（照解析、up 五句）：非 ASCII 只在字串、raw 字串、
        字元字面、行註解與塊註解內。"""
        anchor = _M0003_UP_1_HEAD
        decls = [('#[path = "shadow.rs"]\nmod 影;', "U+5F71"), ('#[path = "shadow.rs"]\nmod shadow影;', "U+5F71")]
        decls += [(f"mod{c}shadow;", f"U+{ord(c):04X}")
                  for c in ("\x0b", "\x0c", "\u0085", "\u200e", "\u200f", "\u2028", "\u2029")]
        for decl, needle in decls:
            with self.subTest(decl=decl):
                self._rc2([(anchor, "#[macro_use]\n" + decl + "\n\n" + anchor)],
                          "m0003_seed_button_governance.rs", "未支援字元", needle)
        for src, needle in (("a\x00b", "U+0000"), ("a；", "U+FF1B"), ("a \\ b", "U+005C")):
            with self.subTest(src=src):
                with self.assertRaises(GateError) as cm:
                    _rust_tokens(src, "合成")
                self.assertIn(needle, str(cm.exception))
        got = self._parse_edited([(anchor, "// 影\n/* 影 /* 影 */ */\nconst Q: char = '影';\n"
                                           'const R: &str = r#"影"#;\nconst S: &str = "影\\u{5F71}";\n\n' + anchor)])
        self.assertEqual([src for src, _text, _toks in got["up"]],
                         ["UP_1_PROTECT_SIX", "UP_2_DELETE_44", "UP_3_INSERT_164", "UP_4_MENU_78", "UP_5_SETVAL"])

    def test_1_split_top_level_semicolons_only(self):
        """SQL 依頂層 `;` 分句：單引號字串（含 `''` 跳脫）與 `$$` 內不切、空句略過。"""
        stmts = [text for text, _toks in _offline_split_sql(
            "DO $$ BEGIN x; END $$;; UPDATE t SET a = 'x;''y' WHERE id = 1 ; ", "合成")]
        self.assertEqual(stmts, ["DO $$ BEGIN x; END $$", "UPDATE t SET a = 'x;''y' WHERE id = 1"])

    def test_1_sql_lexeme_boundaries_follow_pg(self):
        """SQL 詞素邊界與 PG 同切（[`_sql_tokens`]；RL-0080 逐途徑）：①`''` 跳脫解為一個單引號；②SQL 註解
        （[`_sql_comment_end`]：`--` 至行尾〔`\\n` 或 `\\r`〕、`/* */` 可巢狀）切為單一註解詞素，其內之 `;`、引號與 `$$` 不起
        作用；③未支援之 SQL 詞素（[`_sql_unsupported`]）＝GateError 指名，逐途徑：標籤式 dollar 引號 `$<標籤>$`、位置
        參數 `$<n>`、`$$` 緊貼識別字字元（ASCII 字母數字底線、非 ASCII 字元）、前綴字串（單引號緊貼識別字字元、或緊貼
        「識別字字元＋`&`」：`E'…'`／`e'…'`、`B'…'`、`X'…'`、`N'…'`、`U&'…'`／`u&'…'`）；④塊註解未閉合（含內層閉合而外層未閉合）＝GateError。
        對照組：同形隔以空白（`E 'a'`、`x $$ b $$`、`U & 'c'`）照常切詞。"""
        self.assertEqual([t[:2] for t in _sql_tokens("'it''s'", "合成")], [("s", "it's")])
        self.assertEqual([t for t, _k in _offline_split_sql(
            "A -- x; 'y $$\n; B /* p /* q; ' */ \" $$ */ C; D -- e\r; F", "合成")],
            ["A -- x; 'y $$", "B /* p /* q; ' */ \" $$ */ C", "D -- e", "F"])
        self.assertEqual([t[:2] for t in _sql_tokens("E 'a', x $$ b $$, U & 'c'", "合成")],
                         [("w", "E"), ("s", "a"), ("p", ","), ("w", "x"), ("d", " b "), ("p", ","),
                          ("w", "U"), ("p", "&"), ("s", "c")])
        for sql, needle in (("SELECT $q$a$q$", "標籤式 dollar 引號"), ("SELECT $1", "位置參數"),
                            ("SELECT x$$ a $$", "`$$` 緊貼識別字字元"), ("SELECT x_1$$ a $$", "`$$` 緊貼識別字字元"),
                            ("SELECT 中$$ a $$", "`$$` 緊貼識別字字元"),
                            ("SELECT E'a'", "前綴字串"), ("SELECT e'\\''", "前綴字串"), ("SELECT B'1'", "前綴字串"),
                            ("SELECT X'1F'", "前綴字串"), ("SELECT N'a'", "前綴字串"), ("SELECT U&'a'", "前綴字串"),
                            ("SELECT u&'a'", "前綴字串"),
                            ("SELECT 1 /* a", "塊註解未閉合"), ("SELECT 1 /* a /* b */", "塊註解未閉合")):
            with self.subTest(sql=sql):
                with self.assertRaises(GateError) as cm:
                    _sql_tokens(sql, "合成")
                self.assertIn(needle, str(cm.exception))

    def test_2_rc2_const_rhs_other_forms_named(self):
        """②右式他形＝rc 2、指名檔、常數名與構造（未被 up／down 引用亦然：右式三形之判逐常數皆做）。"""
        anchor = 'const UP_FAIL_TAIL: &str ='
        cases = (
            ('include_str!("x.sql")', "include_str!"),
            ('format!("{}", 1)', "format!"),
            ("UP_FAIL_TAIL", "引用他常數 UP_FAIL_TAIL"),
            ("make_sql()", "函式呼叫 make_sql("),
            ('concat!("a", UP_FAIL_TAIL)', "concat!"),
        )
        for rhs, needle in cases:
            with self.subTest(rhs=rhs):
                msg = self._rc2([(anchor, f"const X_SQL: &str = {rhs};\n{anchor}")],
                                "m0003_seed_button_governance.rs", "X_SQL", needle)
                if rhs.startswith("concat!"):
                    self.assertIn("UP_FAIL_TAIL", msg)

    def test_2_rc2_macro_rules_with_argument_named(self):
        """②帶引數之 macro_rules!（他形）＝rc 2、指名巨集名。"""
        self._rc2([("/// ① 六碼改受保護", 'macro_rules! with_arg {\n    ($x:expr) => {\n        "a"\n'
                                         '    };\n}\n\n/// ① 六碼改受保護')],
                  "macro_rules! with_arg")

    def test_2_rc2_up_manager_create_table_named(self):
        """②up 內 `manager.create_table(` 一句（本體他句形）＝rc 2、指名其句首。"""
        self._rc2([("        let db = manager.get_connection();\n        expect_rows(db, \"up ①",
                    "        let db = manager.get_connection();\n"
                    "        manager.create_table(Table::create().table(Alias::new(\"x\")).to_owned())"
                    ".await?;\n        expect_rows(db, \"up ①")],
                  "fn up", "manager.create_table(")

    def test_2_rc2_up_file_helper_call_named(self):
        """②up 內呼叫檔內 helper（SQL 之家以外之途徑）＝rc 2、指名其句首。"""
        self._rc2([("        db.execute_unprepared(UP_5_SETVAL).await?;",
                    "        run_sql(db, UP_5_SETVAL).await?;")],
                  "fn up", "run_sql(")

    def test_2_rc2_missing_fn_down_named(self):
        """②缺 `fn down`＝rc 2。"""
        self._rc2([("async fn down(", "async fn rollback(")], "async fn down")

    def test_2_rc2_duplicate_name_any_scope_named(self):
        """②同名第二次宣告（常數名冊與 macro_rules! 名冊各自判；不論所在 scope 或 `#[cfg]`）＝rc 2、指名檔與名——
        Rust 依 scope／cfg 擇一綁定、本腿不辨二者，取文本序之任一皆可綁錯定義而假綠。逐途徑：`#[cfg]` 互斥雙宣告
        （兩序）、巢狀 `mod` 內、他函式本體內、`impl Migration` 關聯常數、非 `&str` 同名常數、macro_rules! 同名。"""
        anchor = "const UP_FAIL_TAIL: &str ="
        dml = '"DELETE FROM sys_role WHERE id = 1"'
        seq = "\"SELECT setval('casbin_rule_id_seq', 164, true)\""
        cases = (
            ("cfg 互斥雙宣告", f"#[cfg(not(test))]\nconst UP_6_X: &str = {dml};\n"
                             f"#[cfg(test)]\nconst UP_6_X: &str = {seq};\n", "常數 UP_6_X"),
            ("cfg 互斥雙宣告換序", f"#[cfg(test)]\nconst UP_6_X: &str = {seq};\n"
                                 f"#[cfg(not(test))]\nconst UP_6_X: &str = {dml};\n", "常數 UP_6_X"),
            ("巢狀 mod", f"#[cfg(test)]\nmod t {{\n    const UP_5_SETVAL: &str = {dml};\n}}\n",
             "常數 UP_5_SETVAL"),
            ("他函式本體", f"fn helper() {{\n    const UP_5_SETVAL: &str = {dml};\n}}\n", "常數 UP_5_SETVAL"),
            ("impl 關聯常數", f"impl Migration {{\n    const UP_5_SETVAL: &str = {dml};\n}}\n",
             "常數 UP_5_SETVAL"),
            ("非 &str 同名", "mod t {\n    const UP_5_SETVAL: i32 = 1;\n}\n", "常數 UP_5_SETVAL"),
            ("macro_rules! 同名", 'macro_rules! dup_m {\n    () => {\n        "a"\n    };\n}\n'
                                 'macro_rules! dup_m {\n    () => {\n        "b"\n    };\n}\n', "macro_rules! dup_m"),
        )
        for label, decl, needle in cases:
            with self.subTest(label=label):
                self._rc2([(anchor, f"{decl}{anchor}")],
                          "m0003_seed_button_governance.rs", needle, "重複定義")

    def test_2_rc2_foreign_macro_scope_named(self):
        """②檔外巨集引入（判準①j [`_offline_foreign_scope`]）＝rc 2、指名檔與途徑，逐途徑：檔案模組宣告 `mod <名>;`（`#[macro_use]`
        形＝其檔之同名 macro_rules! 遮蔽檔內巨集、`#[path]` 配可見性修飾形、無屬性形、名為 raw 識別字 `r#<名>` 形）、`use` 宣告含識別字
        `concat`（`as concat` 改名形、清單形）。歸屬：`mod` 與名之間或名內含掃描器白名單外字元者（非 ASCII 名、rustc 空白）＝判準①n；
        `#[macro_use]` 不另判、inline mod 之內容照掃——inline `#[macro_use] mod` 內之同名定義＝判準①f、帶引數之定義（意圖遮蔽內建
        concat!）＝判準①b。對照組（照解析、up 五句）：inline `mod <名> { … }`、`use` 之識別字僅含 concat 字樣（`concat_ws`）。"""
        anchor, use_line = _M0003_UP_1_HEAD, _M0003_USE_LINE
        cases = (
            ("#[macro_use] mod", [(anchor, "#[macro_use]\nmod shadow;\n\n" + anchor)], "檔案模組宣告 mod shadow;"),
            ("#[macro_use] mod r#<名>", [(anchor, "#[macro_use]\nmod r#shadow;\n\n" + anchor)], "檔案模組宣告 mod shadow;"),
            ("#[path] pub(crate) mod", [(anchor, '#[path = "evil.rs"]\npub(crate) mod shadow;\n\n' + anchor)],
             "檔案模組宣告 mod shadow;"),
            ("無屬性 mod", [(anchor, "mod tests;\n\n" + anchor)], "檔案模組宣告 mod tests;"),
            ("use … as concat", [(use_line, use_line + "use crate::evil as concat;\n")], "use 宣告含 concat"),
            ("use 清單形", [(use_line, use_line + "use crate::helpers::{concat, other};\n")], "use 宣告含 concat"),
        )
        for label, edits, needle in cases:
            with self.subTest(label=label):
                self._rc2(edits, "m0003_seed_button_governance.rs", needle)
        inline = "#[macro_use]\nmod inner {{\n    macro_rules! {} {{\n        {} => {{\n            \"x\"\n        }};\n    }}\n}}\n\n"
        for label, decl, needle in (
                ("inline #[macro_use] mod 同名", inline.format("six_button_rows", "()"),
                 "macro_rules! six_button_rows 重複定義"),
                ("inline #[macro_use] mod 帶引數 concat", inline.format("concat", "($($t:tt)*)"),
                 "macro_rules! concat 非「單規則、零引數、展開恰一字面」形")):
            with self.subTest(label=label):
                self._rc2([(anchor, decl + anchor)], "m0003_seed_button_governance.rs", needle)
        got = self._parse_edited([(anchor, "mod inner {\n    const Z: i32 = 1;\n}\n\n" + anchor),
                                  (use_line, use_line + "use crate::helpers::concat_ws;\n")])
        self.assertEqual([src for src, _text, _toks in got["up"]],
                         ["UP_1_PROTECT_SIX", "UP_2_DELETE_44", "UP_3_INSERT_164", "UP_4_MENU_78", "UP_5_SETVAL"])

    def test_2_rc2_macro_outside_textual_scope_named(self):
        """②右式所呼叫之檔內巨集不在該常數之文本作用域（判準①k [`_offline_macro_reach`]）＝rc 2、指名常數與巨集名——Rust 先查
        文本作用域、查無才循路徑解析（`use` 匯入、`#[macro_export]`），本腿所展開之檔內定義即非其所綁。逐途徑：定義在呼叫之常數
        之後（配 `use … as six_button_rows` 匯入）、定義於 inline `mod` 內、定義於函式本體內。"""
        for label, edits in _OFFLINE_MACRO_SCOPE_EDITS:
            with self.subTest(label=label):
                self._rc2(edits, "m0003_seed_button_governance.rs", "常數 UP_1_PROTECT_SIX",
                          "six_button_rows!", "文本作用域")

    def test_2_rc2_impl_binding_named(self):
        """②impl 綁定（判準①m [`_offline_impl_binding`]）＝rc 2、指名檔與款——本腿只解析字面 head 之 up／down，遷移二進位所跑之
        MigrationTrait 實作須即此 head。逐途徑（`_OFFLINE_IMPL_BINDING_EDITS`；前四組各只觸一款）：①`impl` 詞素恰一且在頂層——
        inherent impl、型別位置之 `impl Trait`、head 移入 inline mod ②`MigrationTrait` 只出現於 head 且頂層有
        `use sea_orm_migration::prelude::*;`——不改名之他路徑匯入、`use … as MigrationTrait`、檔內 `trait MigrationTrait`、prelude 匯入
        換為他 glob、prelude 匯入在 inline mod 內 ③`Migration` 恰二＝頂層 `struct Migration` 與 head——`use …::Migration` 替身、
        `use … as Migration`、`type Migration`、他處第二 `struct Migration`、`struct Migration` 移入 inline mod ④`cfg`／`cfg_attr` 零——head 冠 `#[cfg(test)]`（遷移二進位
        所跑者在他檔）、`#[cfg_attr]`、`#![cfg]`、`cfg!`；另審查三植入（cfg 互斥之限定路徑 trait impl、inline mod 替身、他檔替身）。
        對照組（照解析、up 五句）：三識別字與 cfg 只見於註解、字串字面或為他識別字之一部分。"""
        for label, edits, needle in _OFFLINE_IMPL_BINDING_EDITS:
            with self.subTest(label=label):
                self._rc2(edits, "m0003_seed_button_governance.rs", "impl 綁定", needle)
        got = self._parse_edited([(_M0003_UP_1_HEAD, "// impl MigrationTrait for Migration #[cfg(test)]\n"
                                   'const NOTE_X: &str = "impl Migration cfg cfg_attr MigrationTrait";\n'
                                   "fn migration_cfg_note(_m: MigrationTraitLike, _n: Migrations) {}\n\n"
                                   + _M0003_UP_1_HEAD)])
        self.assertEqual([src for src, _text, _toks in got["up"]],
                         ["UP_1_PROTECT_SIX", "UP_2_DELETE_44", "UP_3_INSERT_164", "UP_4_MENU_78", "UP_5_SETVAL"])

    def test_3_zero_delta_rc2(self):
        """③零支 delta（只有基線兩支與 lib.rs）＝比對面為空 rc 2。"""
        with tempfile.TemporaryDirectory() as d:
            for name in ("lib.rs", "m0001_baseline_schema.rs", "m0002_baseline_seeds.rs"):
                _offline_write(d, os.path.join(OFFLINE_MIGRATION_DIR, name), "")
            with self.assertRaises(GateError) as cm:
                offline_parse_tree(d)
        self.assertIn("比對面為空", str(cm.exception))

    def test_3_dir_absent_rc2(self):
        """③目錄缺席＝rc 2（本工具不設環境跳過分支）。"""
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(GateError) as cm:
                offline_parse_tree(d)
        self.assertIn("缺席", str(cm.exception))

    def test_3_m0010_in_range_baselines_and_off_form_out(self):
        """③四碼泛形：m0010 入射程且排在 m0003 之後；m0001／m0002 基線與不合檔名形者（三碼、大寫、非 .rs）不入。"""
        with tempfile.TemporaryDirectory() as d:
            shutil.copyfile(os.path.join(REPO_ROOT, _OFFLINE_M0003),
                            _offline_write(d, _OFFLINE_M0003, ""))
            for name in ("m0010_x.rs", "m0002_baseline_seeds.rs", "m0001_baseline_schema.rs",
                         "m004_x.rs", "m0005_X.rs", "m0006_x.txt", "lib.rs"):
                _offline_write(d, os.path.join(OFFLINE_MIGRATION_DIR, name), _OFFLINE_MINIMAL_RS)
            files = [os.path.basename(p) for p in offline_delta_files(d)]
            names = [name for name, _parsed in offline_parse_tree(d)]
        self.assertEqual(files, ["m0003_seed_button_governance.rs", "m0010_x.rs"])
        self.assertEqual(names, ["m0003_seed_button_governance", "m0010_x"])


# m0003 之帳段＝演進帳中該刀名之登記（E-001～E-009）：帳只增不改、號碼永不回收，以刀名濾出即永久固定——
# 植入案之暫存根不隨真帳日後增列而變形。
_OFFLINE_M0003_KNIFE = "007-user-password-admin"
_OFFLINE_FIXTURES = ("columns.json", "indexes.json", "constraints.json", "seed.sql")

# 合成 m0004 形樣本（research R12.1 之 S1～S10 與 down 反序；T007 ⑥）：GRANT 六條（schema、sys_token、四稽核表、
# sys_operation_log INSERT、其序列、授權域三表）、DO 包裝兩形、選單 77 與列 165、序列只進不退。
_OFFLINE_M0004_RS = r'''use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        let db = manager.get_connection();
        db.execute_unprepared(UP_1_ROLE).await?;
        db.execute_unprepared(UP_2_GRANTS).await?;
        expect_rows(db, "up S8", UP_8_MENU_77, 1, UP_TAIL).await?;
        expect_rows(db, "up S9", UP_9_INSERT_165, 1, UP_TAIL).await?;
        db.execute_unprepared(UP_10_SETVAL).await?;
        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        let db = manager.get_connection();
        expect_rows(db, "down S9", DOWN_9_DELETE_165, 1, DOWN_TAIL).await?;
        expect_rows(db, "down S8", DOWN_8_MENU_77, 1, DOWN_TAIL).await?;
        db.execute_unprepared(DOWN_2_REVOKES).await?;
        db.execute_unprepared(DOWN_1_ROLE).await?;
        db.execute_unprepared(DOWN_10_SETVAL).await?;
        Ok(())
    }
}

const UP_TAIL: &str = "前置不符、整支回滾";
const DOWN_TAIL: &str = "前置不符、回退整支回滾";

const UP_1_ROLE: &str =
    "DO $$ BEGIN CREATE ROLE reaper NOLOGIN; EXCEPTION WHEN duplicate_object THEN NULL; END $$";

const UP_2_GRANTS: &str = concat!(
    "GRANT USAGE ON SCHEMA public TO reaper; ",
    "GRANT SELECT, DELETE ON TABLE sys_token TO reaper; ",
    "GRANT SELECT, DELETE ON sys_operation_log, sys_access_log, sys_login_attempt, session_event TO reaper; ",
    "GRANT INSERT ON TABLE sys_operation_log TO reaper; ",
    "GRANT USAGE ON SEQUENCE sys_operation_log_id_seq TO reaper; ",
    "GRANT SELECT ON casbin_rule, sys_menu, sys_role TO reaper",
);

const UP_8_MENU_77: &str = r#"UPDATE sys_menu SET buttons = '[{"code":"audit:purge","desc":"清理日誌"}]'::jsonb WHERE id = 77 AND buttons IS NULL"#;

const UP_9_INSERT_165: &str = "INSERT INTO casbin_rule (id, ptype, v0, v1, v2, v3, v4, v5, protected, created_at, created_by) VALUES (165, 'p', 'R_SUPER', 'audit:purge', 'button', '', '', '', FALSE, '2026-08-05T00:00:00+00:00', NULL)";

const UP_10_SETVAL: &str = "SELECT setval('casbin_rule_id_seq', GREATEST(165, (SELECT last_value FROM casbin_rule_id_seq)), true)";

const DOWN_9_DELETE_165: &str = "DELETE FROM casbin_rule WHERE id = 165 AND ptype = 'p' AND v0 = 'R_SUPER' AND v1 = 'audit:purge' AND v2 = 'button' AND v3 = '' AND v4 = '' AND v5 = '' AND protected = FALSE AND created_at = '2026-08-05T00:00:00+00:00' AND created_by IS NULL";

const DOWN_8_MENU_77: &str = r#"UPDATE sys_menu SET buttons = NULL WHERE id = 77 AND buttons = '[{"code":"audit:purge","desc":"清理日誌"}]'::jsonb"#;

const DOWN_2_REVOKES: &str = concat!(
    "REVOKE SELECT ON casbin_rule, sys_menu, sys_role FROM reaper; ",
    "REVOKE USAGE ON SEQUENCE sys_operation_log_id_seq FROM reaper; ",
    "REVOKE INSERT ON TABLE sys_operation_log FROM reaper; ",
    "REVOKE SELECT, DELETE ON sys_operation_log, sys_access_log, sys_login_attempt, session_event FROM reaper; ",
    "REVOKE SELECT, DELETE ON TABLE sys_token FROM reaper; ",
    "REVOKE USAGE ON SCHEMA public FROM reaper"
);

const DOWN_1_ROLE: &str = "DO $$ BEGIN DROP ROLE IF EXISTS reaper; EXCEPTION WHEN dependent_objects_still_exist THEN RAISE NOTICE 'reaper 仍有依賴、略過刪除'; END $$";

const DOWN_10_SETVAL: &str = "SELECT setval('casbin_rule_id_seq', GREATEST(164, (SELECT COALESCE(max(id), 0) FROM casbin_rule)), true)";
'''
_OFFLINE_M0004 = os.path.join(OFFLINE_MIGRATION_DIR, "m0004_reaper_role_sample.rs")
# 合成樣本之帳兩筆（形照 E-010／E-011 之登記形；knife 取本檔自測慣用之合成值，同 _entry）
_OFFLINE_M0004_ENTRIES = [
    {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": "sys_menu",
     "detail": {"pk": {"id": 77},
                "set": {"buttons": "[{\"code\": \"audit:purge\", \"desc\": \"清理日誌\"}]"}},
     "date": "2026-10-23"},
    {"id": "E-011", "knife": "001-schema-baseline", "kind": "seed_add", "table": "casbin_rule",
     "detail": {"pk": ["id"],
                "values": {"id": 165, "ptype": "p", "v0": "R_SUPER", "v1": "audit:purge",
                           "v2": "button", "v3": "", "v4": "", "v5": "", "protected": False,
                           "created_at": "2026-08-05 00:00:00+00", "created_by": None}},
     "date": "2026-10-23"},
]
# ⑥b：同樣本另加一句改選單 78（WHERE 前值＝m0003 改後值）與其登記
_OFFLINE_MENU_78_NEXT = _M0003_MENU_78_AFTER[:-1] + ',{"code":"ipRule:x","desc":"合成碼"}]'
_OFFLINE_M0004_MENU_78 = (
    "        db.execute_unprepared(UP_10_SETVAL).await?;\n",
    "        expect_rows(db, \"up S8b\", UP_8B_MENU_78, 1, UP_TAIL).await?;\n"
    "        db.execute_unprepared(UP_10_SETVAL).await?;\n")

# 真 m0004（008 刀 U4a、T032 ②）：真檔副本之暫存根另抄 m0004 真檔與 008 刀帳段（真帳濾刀名＝E-010～E-011；理由同
# _OFFLINE_M0003_KNIFE）。合成樣本（_OFFLINE_M0004_RS）承載形制之一正多反；本組承載「真檔＋真帳」之綠與變造即紅。
_OFFLINE_M0004_REAL = os.path.join(OFFLINE_MIGRATION_DIR, "m0004_reaper_role_and_audit_purge.rs")
_OFFLINE_M0004_KNIFE = "008-audit-settings-pages"


def _offline_base(tc, d, rs_edits=(), seed_edits=()):
    """植入用暫存根：m0003 真檔副本（套 rs_edits）、凍結 fixtures 四件（seed_edits 套 seed.sql）、演進帳之 m0003
    帳段（真帳濾刀名）；回 d。"""
    _offline_write(d, _OFFLINE_M0003, _offline_edited(tc, _OFFLINE_M0003, rs_edits))
    for name in _OFFLINE_FIXTURES:
        rel = os.path.join(FIXTURES_DIR, name)
        edits = seed_edits if name == "seed.sql" else ()
        _offline_write(d, rel, _offline_edited(tc, rel, edits))
    data = _load_json(os.path.join(REPO_ROOT, LEDGER), "演進帳")
    entries = [e for e in data["entries"] if e["knife"] == _OFFLINE_M0003_KNIFE]
    _offline_set_ledger(d, entries)
    return d


def _offline_set_ledger(d, entries):
    """暫存根之演進帳整檔改寫：next_id＝最大號＋1（空帳＝1）。"""
    nums = [int(e["id"][2:]) for e in entries]
    _write_ledger(d, {"next_id": (max(nums) + 1) if nums else 1, "entries": entries})


def _offline_ledger(d):
    return _load_json(os.path.join(d, LEDGER), "演進帳")["entries"]


def _offline_run(d=None):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = cmd_offline() if d is None else cmd_offline(root=d)
    return rc, out.getvalue() + err.getvalue()


def _offline_plant_up(tc, d, const_name, sql, direction="up"):
    """於暫存根之 m0003 副本 up 尾端（UP_5 之後；direction="down"＝down 尾端、DOWN_5 之後）植一句
    `db.execute_unprepared(<常數>)` 並宣告該常數。"""
    path = os.path.join(d, _OFFLINE_M0003)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    anchor = f"        db.execute_unprepared({direction.upper()}_5_SETVAL).await?;\n"
    tc.assertEqual(text.count(anchor), 1)
    text = text.replace(anchor, anchor + f"        db.execute_unprepared({const_name}).await?;\n")
    text += f"\nconst {const_name}: &str = {json.dumps(sql, ensure_ascii=False)};\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class _OfflineRoots:
    """植入用暫存根之建置（TestOfflineLeg 與 TestOfflineCriterionMutants 共用；暫存目錄隨案收尾清除）。"""

    def _plant(self, rs_edits=(), seed_edits=(), ledger=None, extra=None):
        d = self.enterContext(tempfile.TemporaryDirectory())
        _offline_base(self, d, rs_edits, seed_edits)
        if ledger is not None:
            _offline_set_ledger(d, ledger(_offline_ledger(d)))
        for rel, text in (extra or {}).items():
            _offline_write(d, rel, text)
        return d

    def _m0004(self, rs_edits=(), more_entries=(), seed_edits=()):
        """暫存根＋合成 m0004 樣本＋其帳兩筆（more_entries 再追加；seed_edits 套凍結 seed.sql 副本）。"""
        d = self._plant(seed_edits=seed_edits,
                        ledger=lambda es: es + _OFFLINE_M0004_ENTRIES + list(more_entries))
        text = _OFFLINE_M0004_RS
        for old, new in rs_edits:
            self.assertEqual(text.count(old), 1, msg=old)
            text = text.replace(old, new)
        _offline_write(d, _OFFLINE_M0004, text)
        return d

    def _real_m0004(self, rs_edits=(), ledger=None):
        """暫存根＋真 m0004 副本（套 rs_edits；改點須唯一命中）＋演進帳之 m0003 與 008 刀帳段（ledger 再改寫）。"""
        d = self._plant()
        _offline_write(d, _OFFLINE_M0004_REAL, _offline_edited(self, _OFFLINE_M0004_REAL, rs_edits))
        data = _load_json(os.path.join(REPO_ROOT, LEDGER), "演進帳")
        entries = [e for e in data["entries"] if e["knife"] in (_OFFLINE_M0003_KNIFE, _OFFLINE_M0004_KNIFE)]
        _offline_set_ledger(d, ledger(entries) if ledger else entries)
        return d


class TestOfflineLeg(_OfflineRoots, unittest.TestCase):
    """offline 判準②～⑤＋cmd_offline 佈線（T007）：真 repo 案讀真檔；植入案一律於暫存根（m0003 副本、演進帳之
    m0003 帳段、凍結 fixtures 四件；真 m0004 案另抄 m0004 真檔與 008 刀帳段）改副本後以 cmd_offline(root=暫存根) 跑，
    真檔零改。"""

    def test_0_planted_base_green(self):
        """對照組：暫存根原封不動＝rc 0（否則以下各植入案之紅無鑑別力）。"""
        rc, msg = _offline_run(self._plant())
        self.assertEqual(rc, 0, msg=msg)

    def test_1_real_repo_green_counts(self):
        """①真 repo 綠：rc 0；配對筆數＝演進帳 seed_* 筆數且 >0（現算）；前值比對筆數 >0。"""
        findings, summary = offline_report(REPO_ROOT)
        self.assertEqual(findings, [])
        n_seed = sum(1 for e in load_ledger(REPO_ROOT)["entries"] if e["kind"].startswith("seed_"))
        self.assertGreater(n_seed, 0)
        self.assertEqual(len(summary["pair_ids"]), n_seed)
        self.assertGreater(summary["prev"], 0)
        rc, msg = _offline_run()
        self.assertEqual(rc, 0, msg=msg)
        self.assertIn("[offline] ✓", msg)

    def test_1b_bare_macro_rhs_paired_rc0(self):
        """右式第二形（檔內巨集零引數呼叫）之 cmd 一正（RL-0080）：副本 UP_3_INSERT_164 改 `insert_164!()` → rc 0 且
        配對照算（9 筆）。"""
        d = self._plant(rs_edits=[
            ('const UP_3_INSERT_164: &str = "INSERT INTO casbin_rule \\\n',
             'macro_rules! insert_164 {\n    () => {\n        "INSERT INTO casbin_rule \\\n'),
            ("'ipRule:unlock', 'button', '', '', '', FALSE, \\\n"
             "     '2026-08-05T00:00:00+00:00', NULL)\";\n",
             "'ipRule:unlock', 'button', '', '', '', FALSE, \\\n"
             "     '2026-08-05T00:00:00+00:00', NULL)\"\n    };\n}\n\n"
             "const UP_3_INSERT_164: &str = insert_164!();\n")])
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 0, msg=msg)
        self.assertEqual(len(offline_report(d)[1]["pair_ids"]), 9)

    def test_2_bad_const_value_rc1_names_e008_v1(self):
        """②改壞常數值（UP_3_INSERT_164 之 'ipRule:unlock' 改一字）→ rc 1，指名 E-008 與欄 v1。"""
        rc, msg = _offline_run(self._plant(rs_edits=[(
            "'ipRule:unlock', 'button', '', '', '', FALSE, \\\n",
            "'ipRule:unlocX', 'button', '', '', '', FALSE, \\\n")]))
        self.assertEqual(rc, 1, msg=msg)
        self.assertIn("[offline·對賬] E-008", msg)
        self.assertIn("欄 v1", msg)

    def test_3_unregistered_statement_rc1_named(self):
        """③少登一筆（副本帳刪 E-009 並調 next_id）→ rc 1，指名未登之句。"""
        rc, msg = _offline_run(self._plant(ledger=lambda es: [e for e in es if e["id"] != "E-009"]))
        self.assertEqual(rc, 1, msg=msg)
        self.assertIn("未登之句", msg)
        self.assertIn("UP_4_MENU_78", msg)

    def test_3b_surplus_entry_and_field_mismatch_rc1_named(self):
        """③帳多出之登記（逐一指名 id）、seed_add 之 pk 欄名清單≠表 pk、seed_update 之 set 欄集多一欄 → 各 rc 1。"""
        extra = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_delete",
                 "table": "casbin_rule", "detail": {"pk": {"id": 1}}, "date": "2026-10-23"}

        def pk_list(es):
            for e in es:
                if e["id"] == "E-008":
                    e["detail"]["pk"] = ["id", "v1"]
            return es

        def set_extra(es):
            for e in es:
                if e["id"] == "E-009":
                    e["detail"]["set"]["hide_in_menu"] = True
            return es

        for fn, needles in ((lambda es: es + [extra], ("多出之登記 E-010",)),
                            (pk_list, ("E-008", "pk 欄名清單")),
                            (set_extra, ("E-009", "欄 hide_in_menu", "演進帳有、migration 缺"))):
            with self.subTest(needles=needles):
                rc, msg = _offline_run(self._plant(ledger=fn))
                self.assertEqual(rc, 1, msg=msg)
                for needle in needles:
                    self.assertIn(needle, msg)

    def test_3c_pairing_key_kind_and_table(self):
        """③配對鍵（kind、表、pk）之 kind 與表兩成分逐一補紅（RL-0080；筆數不變、只鍵之一成分不同）：副本帳①E-009 改登
        seed_delete（pk 照舊 id 78）②E-007 之表改登 sys_menu（kind、pk 照舊）→ 各 rc 1、恰兩條 finding——未登之句
        （指名句、kind、表、pk）與多出之登記（指名 id、kind、表）。"""
        def rekind(es):
            for e in es:
                if e["id"] == "E-009":
                    e["kind"], e["detail"] = "seed_delete", {"pk": e["detail"]["pk"]}
            return es

        def retable(es):
            for e in es:
                if e["id"] == "E-007":
                    e["table"] = "sys_menu"
            return es

        for fn, needles in (
                (rekind, ("未登之句：m0003_seed_button_governance.rs up 第 4 句（UP_4_MENU_78） seed_update sys_menu id=78",
                          "多出之登記 E-009（seed_delete sys_menu）")),
                (retable, ("未登之句：m0003_seed_button_governance.rs up 第 2 句（UP_2_DELETE_44） seed_delete casbin_rule id=44",
                           "多出之登記 E-007（seed_delete sys_menu）"))):
            with self.subTest(needles=needles):
                rc, msg = _offline_run(self._plant(ledger=fn))
                self.assertEqual(rc, 1, msg=msg)
                self.assertEqual(msg.count("    [offline·"), 2, msg=msg)
                for needle in needles:
                    self.assertIn(needle, msg)

    def test_3d_pairing_key_ledger_pk_column_set(self):
        """③配對鍵之 pk 成分取帳側 detail.pk 之全部欄（[`_offline_entry_key`]；RL-0080 逐途徑）：植一句 seed_update 或
        seed_delete 並補其登記——detail.pk 欄集＝該表 pk 欄＝rc 0（對照組）；欄集≠該表 pk 逐途徑＝rc 1、恰兩條 finding
        （未登之句與多出之登記 E-010）：①多列非 pk 欄（sys_menu 之 detail.pk 另列 route_name；seed_update、seed_delete
        各一）②缺 pk 欄（複合 pk 表 sys_user_role 之 detail.pk 只列 user_id；seed_update、seed_delete 各一）。"""
        m78 = {"id": 78, "route_name": "manage_ip-rule"}
        ur = {"user_id": 2, "role_id": 2}
        cases = (
            ("seed_update", "sys_menu", "UPDATE sys_menu SET hide_in_menu = TRUE WHERE id = 78",
             {"set": {"hide_in_menu": True}}, {"id": 78}, m78, "id=78"),
            ("seed_delete", "sys_menu", "DELETE FROM sys_menu WHERE id = 78", {}, {"id": 78}, m78, "id=78"),
            ("seed_update", "sys_user_role", "UPDATE sys_user_role SET role_id = 3 WHERE user_id = 2 AND role_id = 2",
             {"set": {"role_id": 3}}, ur, {"user_id": 2}, "user_id=2、role_id=2"),
            ("seed_delete", "sys_user_role", "DELETE FROM sys_user_role WHERE user_id = 2 AND role_id = 2", {},
             ur, {"user_id": 2}, "user_id=2、role_id=2"),
        )
        for kind, table, sql, extra, good_pk, bad_pk, pk_text in cases:
            for pk, want in ((good_pk, 0), (bad_pk, 1)):
                with self.subTest(kind=kind, table=table, pk=pk):
                    entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": kind, "table": table,
                             "detail": dict({"pk": pk}, **extra), "date": "2026-10-23"}
                    d = self._plant(ledger=lambda es, entry=entry: es + [entry])
                    _offline_plant_up(self, d, "UP_6_KEY", sql)
                    rc, msg = _offline_run(d)
                    self.assertEqual(rc, want, msg=msg)
                    if want:
                        self.assertEqual(msg.count("    [offline·"), 2, msg=msg)
                        self.assertIn(f"未登之句：m0003_seed_button_governance.rs up 第 6 句（UP_6_KEY） {kind} {table} "
                                      f"{pk_text}", msg)
                        self.assertIn(f"多出之登記 E-010（{kind} {table}）", msg)

    def test_3e_quote_doubling_value_decoded(self):
        """③單引號字串之 `''` 跳脫解為一個單引號後才比值（[`_sql_tokens`]；RL-0080）：植
        `UPDATE sys_menu SET menu_name = 'it''s' WHERE id = 78` 並補其登記——帳 set menu_name＝"it's" → rc 0；
        ＝"it''s"（未解跳脫之形）→ rc 1 指名 E-010 欄 menu_name 兩值（雙寫保留或不解即判反）。"""
        for v, want in (("it's", 0), ("it''s", 1)):
            with self.subTest(ledger=v):
                entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": "sys_menu",
                         "detail": {"pk": {"id": 78}, "set": {"menu_name": v}}, "date": "2026-10-23"}
                d = self._plant(ledger=lambda es, entry=entry: es + [entry])
                _offline_plant_up(self, d, "UP_6_QUOTE", "UPDATE sys_menu SET menu_name = 'it''s' WHERE id = 78")
                rc, msg = _offline_run(d)
                self.assertEqual(rc, want, msg=msg)
                if want:
                    self.assertEqual(msg.count("    [offline·"), 1, msg=msg)
                    self.assertIn("[offline·對賬] E-010（seed_update sys_menu id=78；m0003_seed_button_governance.rs "
                                  "up 第 6 句（UP_6_QUOTE））｜欄 menu_name：migration＝\"it's\"、演進帳＝\"it''s\"", msg)

    def test_3f_set_column_missing_in_ledger(self):
        """③seed_update 之 set 欄集「migration 有、演進帳缺」（[`_offline_ledger_findings`]；③b 案為反向「演進帳有、migration 缺」；
        RL-0080 逐途徑）：植 `UPDATE sys_menu SET hide_in_menu = TRUE, menu_name = 'x' WHERE id = 78` 並補其登記——帳 set 登兩欄
        → rc 0；只登 hide_in_menu → rc 1 恰一條指名 E-010、欄 menu_name 與「migration 有、演進帳缺」（seed_update 之少登
        一欄無他判兜底：apply_seed_entries 只套帳側所登之欄）。"""
        for setv, want in (({"hide_in_menu": True, "menu_name": "x"}, 0), ({"hide_in_menu": True}, 1)):
            with self.subTest(set=setv):
                entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": "sys_menu",
                         "detail": {"pk": {"id": 78}, "set": setv}, "date": "2026-10-23"}
                d = self._plant(ledger=lambda es, entry=entry: es + [entry])
                _offline_plant_up(self, d, "UP_6_SETX",
                                  "UPDATE sys_menu SET hide_in_menu = TRUE, menu_name = 'x' WHERE id = 78")
                rc, msg = _offline_run(d)
                self.assertEqual(rc, want, msg=msg)
                if want:
                    self.assertEqual(msg.count("    [offline·"), 1, msg=msg)
                    self.assertIn("[offline·對賬] E-010（seed_update sys_menu id=78；m0003_seed_button_governance.rs "
                                  "up 第 6 句（UP_6_SETX））｜欄 menu_name：migration 有、演進帳缺", msg)

    def test_4_bad_frozen_prevalue_rc1(self):
        """④改壞凍結前值（副本 seed.sql 之 casbin_rule 列 44 v1、或選單 78 buttons 改一字）→ rc 1 [offline·前值]。"""
        for edit, col in (("44\tp\tR_ADMIN\tuser:edit\t", "欄 v1"),
                          ('{"code": "ipRule:restore", "desc": "恢復IP規則"}]', "欄 buttons")):
            with self.subTest(col=col):
                new = edit.replace("user:edit", "user:ediX").replace("恢復IP規則", "恢復IP規X")
                rc, msg = _offline_run(self._plant(seed_edits=[(edit, new)]))
                self.assertEqual(rc, 1, msg=msg)
                self.assertIn("[offline·前值] m0003_seed_button_governance.rs up 第", msg)
                self.assertIn(col, msg)

    def test_4b_prevalue_tuple_in_is_null_and_pk_miss_rc1(self):
        """④前值逐途徑補紅（RL-0080；各案前值為唯一 finding、拆該途徑即綠）：①元組 IN 之非 pk 位——副本 seed 改列 58
        之 v1（UP_1 以 `(id, v1) IN` 定列）②IS NULL——合成 m0004 樣本、副本 seed 之選單 77 buttons 改非 NULL（S8 以
        `buttons IS NULL` 定列）③pk 不命中左源——植一句 UPDATE 指向 sys_menu id 999（凍結 seed 無此列）並補其登記。
        各 rc 1 [offline·前值] 指名。"""
        ghost = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": "sys_menu",
                 "detail": {"pk": {"id": 999}, "set": {"hide_in_menu": True}}, "date": "2026-10-23"}
        d_ghost = self._plant(ledger=lambda es: es + [ghost])
        _offline_plant_up(self, d_ghost, "UP_6_GHOST", "UPDATE sys_menu SET hide_in_menu = TRUE WHERE id = 999")
        cases = (
            ("元組 IN 非 pk 位", self._plant(seed_edits=[("58\tp\tR_SUPER\trole:add\t", "58\tp\tR_SUPER\trole:adX\t")]),
             ("m0003_seed_button_governance.rs up 第 1 句（UP_1_PROTECT_SIX）", "欄 v1")),
            ("IS NULL", self._m0004(seed_edits=[("\troute.manage_audit\t\\N\t\\N\t\\N\t\\N\t\\N\n",
                                                 "\troute.manage_audit\t\\N\t\\N\t\\N\t\\N\t[]\n")]),
             ("m0004_reaper_role_sample.rs up 第 8 句（UP_8_MENU_77）", "欄 buttons：WHERE＝None")),
            ("pk 不命中", d_ghost,
             ("m0003_seed_button_governance.rs up 第 6 句（UP_6_GHOST）", "pk 不命中左源")),
        )
        for label, d, needles in cases:
            with self.subTest(label=label):
                rc, msg = _offline_run(d)
                self.assertEqual(rc, 1, msg=msg)
                self.assertEqual(msg.count("    [offline·"), 1, msg=msg)
                self.assertIn("[offline·前值]", msg)
                for needle in needles:
                    self.assertIn(needle, msg)

    def test_4c_prevalue_same_file_cumulative(self):
        """④前值左源之同支逐筆累進（RL-0080 逐途徑；跨支途徑見 ⑥b）：m0003 副本 up 尾植一句改選單 78（UP_4 之後），
        副本帳補其登記——WHERE buttons 取 UP_4 改後值 → rc 0；取凍結值 → rc 1 恰一條 [offline·前值] 指名欄 buttons
        （同支內前值恆取支首左源＝本案判反）。"""
        entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": "sys_menu",
                 "detail": {"pk": {"id": 78}, "set": {"hide_in_menu": True}}, "date": "2026-10-23"}
        for before, want in ((_M0003_MENU_78_AFTER, 0), (_M0003_MENU_78_BEFORE, 1)):
            with self.subTest(want=want):
                d = self._plant(ledger=lambda es: es + [entry])
                _offline_plant_up(self, d, "UP_6_MENU_78",
                                  f"UPDATE sys_menu SET hide_in_menu = TRUE WHERE id = 78 AND buttons = '{before}'::jsonb")
                rc, msg = _offline_run(d)
                self.assertEqual(rc, want, msg=msg)
                if want:
                    self.assertEqual(msg.count("    [offline·"), 1, msg=msg)
                    self.assertIn("[offline·前值] m0003_seed_button_governance.rs up 第 6 句（UP_6_MENU_78）", msg)
                    self.assertIn("欄 buttons", msg)

    def test_4d_prevalue_composite_pk_all_columns(self):
        """④前值左源之 pk 命中須該表 pk 全部欄皆等（[`_offline_left_row`]；複合 pk 表 sys_user_role〔user_id, role_id〕；
        RL-0080 逐途徑）：植 `DELETE FROM sys_user_role WHERE user_id = 2 AND role_id = <r>` 並補其登記——兩欄皆命中凍結
        seed 之列 (2, 2) → rc 0；只 user_id 命中、role_id＝3 錯配 → rc 1 恰一條 [offline·前值] pk 不命中左源（任一欄命中
        即算＝本案判反）。"""
        for role, want in ((2, 0), (3, 1)):
            with self.subTest(role_id=role):
                entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_delete", "table": "sys_user_role",
                         "detail": {"pk": {"user_id": 2, "role_id": role}}, "date": "2026-10-23"}
                d = self._plant(ledger=lambda es, entry=entry: es + [entry])
                _offline_plant_up(self, d, "UP_6_UR", f"DELETE FROM sys_user_role WHERE user_id = 2 AND role_id = {role}")
                rc, msg = _offline_run(d)
                self.assertEqual(rc, want, msg=msg)
                if want:
                    self.assertEqual(msg.count("    [offline·"), 1, msg=msg)
                    self.assertIn("[offline·前值] m0003_seed_button_governance.rs up 第 6 句（UP_6_UR） seed_delete "
                                  "sys_user_role user_id=2、role_id=3｜pk 不命中左源", msg)

    def test_5_unclassified_ddl_rc1(self):
        """⑤植未分類 DDL（副本增常數 ALTER TABLE 並於 up 以 execute_unprepared 呼之）→ rc 1 [offline·分類]。"""
        d = self._plant()
        _offline_plant_up(self, d, "UP_6_ALTER", "ALTER TABLE sys_user ADD COLUMN x text")
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 1, msg=msg)
        self.assertIn("[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_ALTER） 未分類——句首「ALTER TABLE sys_user", msg)

    def test_6_m0004_sample_green_and_permission_listing(self):
        """⑥合成 m0004 形樣本＋帳兩筆 → rc 0；權限面列出 up CREATE ROLE 1／GRANT 6、down REVOKE 6／DROP ROLE 1；
        受權物件集恰 10（schema public、sys_token、四稽核表、sys_operation_log_id_seq、授權域三表）。"""
        d = self._m0004()
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 0, msg=msg)
        findings, summary = offline_report(d)
        perm = summary["perm"]["m0004_reaper_role_sample"]
        self.assertEqual(dict(perm["up"]["kinds"]), {"CREATE ROLE": 1, "GRANT": 6})
        self.assertEqual(dict(perm["down"]["kinds"]), {"REVOKE": 6, "DROP ROLE": 1})
        want = {("SCHEMA", "public"), ("TABLE", "sys_token"), ("TABLE", "sys_operation_log"),
                ("TABLE", "sys_access_log"), ("TABLE", "sys_login_attempt"), ("TABLE", "session_event"),
                ("SEQUENCE", "sys_operation_log_id_seq"), ("TABLE", "casbin_rule"),
                ("TABLE", "sys_menu"), ("TABLE", "sys_role")}
        self.assertEqual(set(perm["up"]["objects"]), want)
        self.assertEqual(set(perm["down"]["objects"]), want)
        self.assertEqual(perm["up"]["objects"][("TABLE", "sys_operation_log")], {"SELECT", "DELETE", "INSERT"})
        self.assertEqual(perm["up"]["roles"], {"reaper"})
        self.assertEqual(summary["pair_ids"], [f"E-{i:03d}" for i in range(1, 12)])
        self.assertIn("權限面", msg)
        self.assertIn("受權物件 10", msg)

    def test_6b_followup_update_prevalue_from_prior_pairing(self):
        """⑥b 同樣本另加一句改選單 78：WHERE 前值取 m0003 改後值、副本帳補其登記 → 綠；WHERE 改取凍結值 → rc 1
        （承載前序配對合成：後序 delta 改到前序已改之列時，前值即其改後值）。"""
        entry = {"id": "E-012", "knife": "001-schema-baseline", "kind": "seed_update", "table": "sys_menu",
                 "detail": {"pk": {"id": 78}, "set": {"buttons": _OFFLINE_MENU_78_NEXT}},
                 "date": "2026-10-23"}
        for before, want_rc in ((_M0003_MENU_78_AFTER, 0), (_M0003_MENU_78_BEFORE, 1)):
            with self.subTest(want_rc=want_rc):
                sql = (f"UPDATE sys_menu SET buttons = '{_OFFLINE_MENU_78_NEXT}'::jsonb "
                       f"WHERE id = 78 AND buttons = '{before}'::jsonb")
                d = self._m0004(rs_edits=[
                    _OFFLINE_M0004_MENU_78,
                    ("const UP_10_SETVAL: &str",
                     f"const UP_8B_MENU_78: &str = r#\"{sql}\"#;\n\nconst UP_10_SETVAL: &str")],
                    more_entries=[entry])
                rc, msg = _offline_run(d)
                self.assertEqual(rc, want_rc, msg=msg)
                if want_rc:
                    self.assertIn("[offline·前值] m0004_reaper_role_sample.rs up 第 10 句（UP_8B_MENU_78）", msg)
                    self.assertIn("欄 buttons", msg)

    def test_offline_real_m0004_green_and_mutants_red(self):
        """真 m0004（008 刀 U4a、T032 ②）：暫存根抄 m0003 與 m0004 真檔、凍結 fixtures 四件與演進帳之 007／008 刀帳段，真檔零改。
        ①原封＝rc 0、零 finding、兩帳段之 seed_* 全數配對（008 刀帳段恰 E-010、E-011）；權限面結構化列出 up＝CREATE ROLE 1＋
        GRANT 6、down＝REVOKE 6＋DROP ROLE 1，受權物件→權限整份恰為所列（物件 10＝schema public、sys_token、四稽核表〔sys_operation_log 之 INSERT
        計於同一物件〕、sys_operation_log_id_seq、授權域三表）。②變造五發（各一暫存根）各 rc 1、finding 數恰為所列且逐條指名：
        帳刪 E-011（列 165 之 seed DML 無登記）、S8 新值改一字（與 E-010 set 不符）、S8 前值改非 NULL 字面（與凍結 seed 選單 77
        之 \\N 不符）、植一句 ALTER TABLE 常數（未分類）、S9 之 id 改 166（與 E-011 values.id 不符＝未登之句＋多出之登記）。"""
        name = "m0004_reaper_role_and_audit_purge"
        d = self._real_m0004()
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 0, msg=msg)
        findings, summary = offline_report(d)
        self.assertEqual(findings, [])
        self.assertEqual(summary["files"], ["m0003_seed_button_governance", name])
        ledger = _offline_ledger(d)
        self.assertEqual([e["id"] for e in ledger if e["knife"] == _OFFLINE_M0004_KNIFE], ["E-010", "E-011"])
        self.assertEqual(summary["pair_ids"], [e["id"] for e in ledger if e["kind"].startswith("seed_")])
        perm = summary["perm"][name]
        self.assertEqual(dict(perm["up"]["kinds"]), {"CREATE ROLE": 1, "GRANT": 6})
        self.assertEqual(dict(perm["down"]["kinds"]), {"REVOKE": 6, "DROP ROLE": 1})
        sd = {"SELECT", "DELETE"}
        want = {("SCHEMA", "public"): {"USAGE"}, ("TABLE", "sys_token"): sd,
                ("TABLE", "sys_operation_log"): sd | {"INSERT"}, ("TABLE", "sys_access_log"): sd,
                ("TABLE", "sys_login_attempt"): sd, ("TABLE", "session_event"): sd,
                ("SEQUENCE", "sys_operation_log_id_seq"): {"USAGE"}, ("TABLE", "casbin_rule"): {"SELECT"},
                ("TABLE", "sys_menu"): {"SELECT"}, ("TABLE", "sys_role"): {"SELECT"}}
        self.assertEqual(dict(perm["up"]["objects"]), want)       # 物件→權限整份釘死（多授一權即紅）
        self.assertEqual(dict(perm["down"]["objects"]), want)
        self.assertEqual((perm["up"]["roles"], perm["down"]["roles"]), ({"reaper"}, {"reaper"}))
        self.assertIn(f"權限面（只列不對賬）{name}｜up：CREATE ROLE 1、GRANT 6；角色 reaper；受權物件 10＝", msg)
        s10 = "        db.execute_unprepared(UP_S10_SETVAL).await?;\n"
        cases = (
            ("帳刪 E-011", dict(ledger=lambda es: [e for e in es if e["id"] != "E-011"]),
             [f"[offline·對賬] 未登之句：{name}.rs up 第 9 句（UP_S9_INSERT_165） seed_add casbin_rule id=165"]),
            ("S8 新值改一字", dict(rs_edits=[('r#"[{"code":"audit:purge","desc":"清理日誌"}]"#',
                                          'r#"[{"code":"audit:purgX","desc":"清理日誌"}]"#')]),
             [f"[offline·對賬] E-010（seed_update sys_menu id=77；{name}.rs up 第 8 句（UP_S8_MENU_77））｜欄 buttons："]),
            ("S8 前值改非 NULL 字面", dict(rs_edits=[("AND buttons IS NULL\"", "AND buttons = '[]'::jsonb\"")]),
             [f"[offline·前值] {name}.rs up 第 8 句（UP_S8_MENU_77） seed_update sys_menu id=77｜欄 buttons：WHERE＝'[]'、"
              "左源＝None"]),
            ("植未分類 ALTER 常數", dict(rs_edits=[
                (s10, s10 + "        db.execute_unprepared(UP_X_ALTER).await?;\n"),
                ("const DOWN_5_SETVAL: &str", 'const UP_X_ALTER: &str = "ALTER TABLE sys_menu ADD COLUMN x int";\n\n'
                                              "const DOWN_5_SETVAL: &str")]),
             [f"[offline·分類] {name}.rs up 第 11 句（UP_X_ALTER） 未分類——句首「ALTER TABLE sys_menu ADD COLUMN x int」"]),
            ("S9 之 id 改 166", dict(rs_edits=[("VALUES (165, 'p'", "VALUES (166, 'p'")]),
             [f"[offline·對賬] 未登之句：{name}.rs up 第 9 句（UP_S9_INSERT_165） seed_add casbin_rule id=166",
              "[offline·對賬] 多出之登記 E-011（seed_add casbin_rule）"]),
        )
        for label, kw, needles in cases:
            with self.subTest(label=label):
                rc, msg = _offline_run(self._real_m0004(**kw))
                self.assertEqual(rc, 1, msg=msg)
                self.assertEqual(msg.count("    [offline·"), len(needles), msg=msg)
                for needle in needles:
                    self.assertIn(needle, msg)

    def test_7_do_block_hiding_dml_unclassified(self):
        """⑦`DO $$ BEGIN UPDATE sys_menu …; END $$` 藏 DML → rc 1 未分類。"""
        d = self._plant()
        _offline_plant_up(self, d, "UP_6_DO",
                          "DO $$ BEGIN UPDATE sys_menu SET hide_in_menu = TRUE WHERE id = 78; END $$")
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 1, msg=msg)
        self.assertIn("[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_DO） 未分類", msg)

    def test_7b_do_block_tail_strict(self):
        """⑦b DO 包裝兩形之尾段嚴格比對（RL-0080 逐途徑；`_OFFLINE_DO_CREATE_TAIL`／`_OFFLINE_DO_DROP_TAIL`）：塊本體詞素數
        與嚴格形相等、首段與角色照舊、只尾段不同者逐途徑＝未分類——①例外名改 others（CREATE 形 `… WHEN others THEN
        NULL; END`、DROP 形 `… WHEN others THEN RAISE NOTICE 'x'; END`）②尾段換為塊內藏 DML（CREATE 形 `NOLOGIN;
        DELETE FROM sys_menu WHERE TRUE; END`、DROP 形 `reaper; DELETE FROM sys_menu WHERE id = 1; END`）；另③嚴格尾段照舊、
        其前插入塊內 DML（兩形各 `DELETE FROM sys_user WHERE TRUE;`；CREATE 形由選項尾段白名單擋、DROP 形由塊本體詞素數恰 16
        與首段之後尾段全等擋）＝未分類。對照組＝同角色、同選項之嚴格形歸權限面；佈線另以植入案證（②③兩形藏 DML 各 rc 1 指名
        第 6 句）。"""
        def classify(sql):
            return _offline_classify(_sql_tokens(sql, "合成"), {"sys_menu"}, "合成")

        def body_len(sql):
            return len(_sql_tokens(_sql_tokens(sql, "合成")[1][1], "合成"))

        create = "DO $$ BEGIN CREATE ROLE reaper NOLOGIN; {} END $$"
        drop = "DO $$ BEGIN DROP ROLE IF EXISTS reaper; {} END $$"
        strict = (
            (create.format("EXCEPTION WHEN duplicate_object THEN NULL;"), "CREATE ROLE"),
            (drop.format("EXCEPTION WHEN dependent_objects_still_exist THEN RAISE NOTICE 'x';"), "DROP ROLE"))
        for sql, kind in strict:
            with self.subTest(strict=sql):
                self.assertEqual(classify(sql), ("權限面", {"kind": kind, "role": "reaper", "objects": {}}))
        hidden = (create.format("DELETE FROM sys_menu WHERE TRUE;"), drop.format("DELETE FROM sys_menu WHERE id = 1;"))
        others = (create.format("EXCEPTION WHEN others THEN NULL;"),
                  drop.format("EXCEPTION WHEN others THEN RAISE NOTICE 'x';"))
        for (ref, _kind), beyond in zip(strict * 2, others + hidden):
            with self.subTest(beyond=beyond):
                self.assertEqual(body_len(beyond), body_len(ref))
                self.assertEqual(classify(beyond), (None, None))
        inserted = tuple(ref.replace("EXCEPTION", "DELETE FROM sys_user WHERE TRUE; EXCEPTION", 1) for ref, _kind in strict)
        for sql in inserted:
            with self.subTest(inserted=sql):
                self.assertIn("; DELETE FROM sys_user WHERE TRUE; EXCEPTION WHEN", sql)
                self.assertEqual(classify(sql), (None, None))
        for sql in hidden + inserted:
            with self.subTest(wired=sql):
                d = self._plant()
                _offline_plant_up(self, d, "UP_6_DO", sql)
                rc, msg = _offline_run(d)
                self.assertEqual(rc, 1, msg=msg)
                self.assertIn("[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_DO） 未分類", msg)

    def test_8_grant_on_all_tables_in_schema_unclassified(self):
        """⑧`GRANT ALL ON ALL TABLES IN SCHEMA public TO reaper` → rc 1 未分類（同理 WITH GRANT OPTION、角色成員授予之
        GRANT 形；CREATE ROLE 之成員子句見 ⑧b）。"""
        for sql in ("GRANT ALL ON ALL TABLES IN SCHEMA public TO reaper",
                    "GRANT SELECT ON sys_menu TO reaper WITH GRANT OPTION",
                    "GRANT pg_read_all_data TO reaper"):
            with self.subTest(sql=sql):
                d = self._plant()
                _offline_plant_up(self, d, "UP_6_GRANT", sql)
                rc, msg = _offline_run(d)
                self.assertEqual(rc, 1, msg=msg)
                self.assertIn("[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_GRANT） 未分類", msg)

    def test_8b_create_role_option_tail_whitelist(self):
        """⑧b CREATE ROLE 選項尾段（裸形與 DO 包裝形同判 [`_offline_role_options`]）：`<角色>` 之後只收白名單屬性詞
        （PG 預設值或減權：NOLOGIN／NOSUPERUSER／NOCREATEDB／NOCREATEROLE／NOREPLICATION／NOBYPASSRLS／INHERIT／NOINHERIT；
        不分大小寫；裸形可零個、DO 包裝形至少一個）＝權限面。白名單外逐途徑＝未分類：角色成員子句（IN ROLE／IN GROUP／
        ROLE／USER／ADMIN）、白名單外屬性詞（SUPERUSER／CREATEDB／CREATEROLE／REPLICATION／BYPASSRLS／LOGIN）、WITH、SYSID、
        CONNECTION LIMIT、[ENCRYPTED] PASSWORD、VALID UNTIL、引號形屬性詞（`"…"`、`'…'`）、SQL 註解（`--`、`/* */`）、
        DO 包裝形零選項。佈線另以植入案證
        （白名單外 rc 1 指名、白名單內 rc 0 且權限面列出）。"""
        def forms(tail):
            out = [f"CREATE ROLE reaper {tail}".rstrip()]
            if tail:
                out.append(f"DO $$ BEGIN CREATE ROLE reaper {tail}; EXCEPTION WHEN duplicate_object THEN NULL; END $$")
            return out

        def classify(sql):
            return _offline_classify(_sql_tokens(sql, "合成"), set(), "合成")

        want = ("權限面", {"kind": "CREATE ROLE", "role": "reaper", "objects": {}})
        for tail in ("", "NOLOGIN", "NOSUPERUSER", "NOCREATEDB", "NOCREATEROLE", "NOREPLICATION", "NOBYPASSRLS",
                     "INHERIT", "NOINHERIT", "nologin noinherit",
                     "NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT"):
            for sql in forms(tail):
                with self.subTest(whitelisted=sql):
                    self.assertEqual(classify(sql), want)
        for tail in ("IN ROLE pg_write_all_data", "IN GROUP pg_write_all_data", "ROLE app_user", "USER app_user",
                     "ADMIN app_user", "SUPERUSER", "CREATEDB", "CREATEROLE", "REPLICATION", "BYPASSRLS", "LOGIN",
                     "WITH NOLOGIN", "SYSID 5", "CONNECTION LIMIT 1", "PASSWORD NULL", "ENCRYPTED PASSWORD NULL",
                     "VALID UNTIL 'infinity'", "\"NOLOGIN\"", "'NOLOGIN'", "-- 註解", "/* 註解 */ NOLOGIN",
                     "NOLOGIN -- 註解"):
            for sql in forms(tail):
                with self.subTest(beyond=sql):
                    self.assertEqual(classify(sql), (None, None))
        self.assertEqual(classify("DO $$ BEGIN CREATE ROLE reaper; EXCEPTION WHEN duplicate_object THEN NULL; END $$"),
                         (None, None))
        for sql in ("CREATE ROLE reaper -- 註解", "CREATE ROLE reaper IN ROLE pg_write_all_data",
                    forms("IN ROLE pg_write_all_data")[1]):
            with self.subTest(wired=sql):
                d = self._plant()
                _offline_plant_up(self, d, "UP_6_ROLE", sql)
                rc, msg = _offline_run(d)
                self.assertEqual(rc, 1, msg=msg)
                self.assertIn("[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_ROLE） 未分類", msg)
        d = self._plant()
        _offline_plant_up(self, d, "UP_6_ROLE", "CREATE ROLE reaper NOLOGIN")
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 0, msg=msg)
        self.assertIn("up：CREATE ROLE 1；角色 reaper；受權物件 0", msg)

    def test_8c_sql_comment_paths(self):
        """SQL 註解（[`_sql_comment_end`]：切為單一註解詞素、內容不入判準）逐途徑：①未分類——句首、seed DML 標的表之前、
        權限面五形之句內或句尾、setval 呼叫第二引數之前或整句之後 ②句形超出（rc 2）——up 方向 seed DML 標的表之後
        ③不察（射程外）——setval 第二引數以後、down 方向 seed DML 標的表之後（down 只分類；植入案 rc 0）④註解內之單引號、
        雙引號與 `$$` 不起詞素作用（同 PG；所在句照①判未分類、不報未閉合）。"""
        def classify(sql):
            return _offline_classify(_sql_tokens(sql, "合成"), {"casbin_rule", "sys_menu"}, "合成")

        for sql in ("/* 註解 */ GRANT SELECT ON sys_menu TO reaper",
                    "INSERT INTO /* 註解 */ casbin_rule (id) VALUES (165)",
                    "GRANT SELECT /* 註解 */ ON sys_menu TO reaper",
                    "GRANT SELECT ON sys_menu TO reaper -- 註解",
                    "REVOKE SELECT ON sys_menu FROM reaper -- 註解",
                    "CREATE ROLE reaper NOLOGIN -- 註解",
                    "DROP ROLE IF EXISTS reaper -- 註解",
                    "DO $$ BEGIN CREATE ROLE reaper NOLOGIN; -- 註解\n EXCEPTION WHEN duplicate_object THEN NULL; END $$",
                    "DO $$ BEGIN DROP ROLE IF EXISTS reaper; EXCEPTION WHEN dependent_objects_still_exist "
                    "THEN RAISE NOTICE 'x'; /* 註解 */ END $$",
                    "SELECT setval(/* 註解 */ 'casbin_rule_id_seq', 164, true)",
                    "SELECT setval('casbin_rule_id_seq', 164, true) -- 註解"):
            with self.subTest(unclassified=sql):
                self.assertEqual(classify(sql), (None, None))
        for sql in ("INSERT INTO casbin_rule (id) VALUES (165) -- 註解",
                    "INSERT INTO casbin_rule (id /* 註解 */) VALUES (165)",
                    "UPDATE casbin_rule SET v1 = 'x' WHERE id = 44 -- 註解",
                    "DELETE FROM casbin_rule WHERE id = 44 /* 註解 */"):
            with self.subTest(shape=sql):
                self.assertEqual(classify(sql), ("seed DML", "casbin_rule"))
                st = {"at": "合成", "text": sql, "toks": _sql_tokens(sql, "合成"), "info": "casbin_rule"}
                with self.assertRaises(GateError) as cm:
                    _offline_dml_records(st, ["id"])
                self.assertIn("句形超出", str(cm.exception))
        self.assertEqual(classify("SELECT setval('casbin_rule_id_seq', 164 /* 註解 */, true)"),
                         ("序列", "casbin_rule_id_seq"))
        anchor = "        db.execute_unprepared(DOWN_5_SETVAL).await?;\n"
        d = self._plant(rs_edits=[(anchor, anchor + "        db.execute_unprepared(DOWN_6_NOTE).await?;\n")])
        with open(os.path.join(d, _OFFLINE_M0003), "a", encoding="utf-8") as fh:
            fh.write('\nconst DOWN_6_NOTE: &str = "DELETE FROM casbin_rule WHERE id = 165 -- 註解";\n')
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 0, msg=msg)
        self.assertIn("down 6 句（seed DML 5、序列 1）", msg)
        for sql in ("GRANT SELECT ON sys_menu TO reaper -- it's", 'GRANT SELECT ON sys_menu TO reaper -- "x',
                    "GRANT SELECT ON sys_menu TO reaper -- $$", "GRANT SELECT ON sys_menu TO reaper /* it's */"):
            with self.subTest(inert=sql):
                self.assertEqual(classify(sql), (None, None))

    def test_8d_sql_lexeme_desync_paths(self):
        """SQL 詞素邊界錯位逐途徑（PG 切法與本詞素器不同、單引號或 `$$` 配對錯位即可把頂層 `;` 吞進「字串」而併句、藏住
        後方 ALTER；RL-0080）：①未支援之 SQL 詞素＝rc 2 指名（fail-closed；[`_sql_unsupported`]）——down 方向 seed DML
        之 SET 值用標籤式 dollar 引號 `$q$…$q$`、同處用前綴字串 `E'\\''`（PG 之 `\\'` 為跳脫）、up 方向 setval 第二引數用
        `$q$…$q$`、up 方向 setval 第二引數之子查詢別名 `x$$`（PG 將 `$$` 併入識別字）②SQL 註解內之引號不起作用
        （[`_sql_comment_end`]）——down 方向 seed DML 標的表之後之 `--` 註解、up 方向 setval 第二引數之 `/* */` 註解各含
        單引號且成對：後方 ALTER 照分句＝rc 1 恰一條 [offline·分類] 指名。"""
        alter = "ALTER TABLE sys_user ADD COLUMN x text"
        lexeme = (
            ("down", f"UPDATE casbin_rule SET v3 = $q$a'b$q$ WHERE id = 165; {alter}; "
                     "UPDATE casbin_rule SET v3 = $q$c'd$q$ WHERE id = 165", "標籤式 dollar 引號"),
            ("down", f"UPDATE casbin_rule SET v3 = E'\\'' WHERE id = 165; {alter}; "
                     "UPDATE casbin_rule SET v3 = E'\\'' WHERE id = 165", "前綴字串"),
            ("up", f"SELECT setval('casbin_rule_id_seq', $q$1'$q$::bigint); {alter}; "
                   "SELECT setval('casbin_rule_id_seq', $q$'1$q$::bigint)", "標籤式 dollar 引號"),
            ("up", f"SELECT setval('casbin_rule_id_seq', (SELECT 164 AS x$$)); {alter}; "
                   "SELECT setval('casbin_rule_id_seq', (SELECT 164 AS y$$))", "`$$` 緊貼識別字字元"),
        )
        for direction, sql, needle in lexeme:
            with self.subTest(lexeme=sql):
                d = self._plant()
                const = f"{direction.upper()}_6_LEX"
                _offline_plant_up(self, d, const, sql, direction=direction)
                rc, msg = _offline_run(d)
                self.assertEqual(rc, 2, msg=msg)
                self.assertIn("[offline] ✗", msg)
                self.assertIn(f"fn {direction} 第 7 句（{const}）：未支援之 SQL 詞素", msg)
                self.assertIn(needle, msg)
        comment = (
            ("down", f"DELETE FROM casbin_rule WHERE id = 165 -- '\n; {alter} -- '", 7),
            ("up", f"SELECT setval('casbin_rule_id_seq', 164 /* ' */, true); {alter}; "
                   "SELECT setval('casbin_rule_id_seq', 164 /* ' */, true)", 7),
        )
        for direction, sql, n in comment:
            with self.subTest(comment=sql):
                d = self._plant()
                const = f"{direction.upper()}_6_CMT"
                _offline_plant_up(self, d, const, sql, direction=direction)
                rc, msg = _offline_run(d)
                self.assertEqual(rc, 1, msg=msg)
                self.assertEqual(msg.count("    [offline·"), 1, msg=msg)
                self.assertIn(f"[offline·分類] m0003_seed_button_governance.rs {direction} 第 {n} 句（{const}） 未分類"
                              f"——句首「{alter}", msg)

    def test_9_insert_into_narrowed_table_unclassified(self):
        """⑨對收窄表 sys_operation_log（現行收窄集成員）之 INSERT → rc 1 未分類（收窄表 seed 必空）。"""
        d = self._plant()
        _offline_plant_up(self, d, "UP_6_OPLOG", _OFFLINE_OPLOG_INSERT)
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 1, msg=msg)
        self.assertIn("[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_OPLOG） 未分類", msg)

    def test_9b_insert_into_access_log_unclassified(self):
        """⑨（runtime-append 擴集後同類補一案；ADR-00100 決定 8）：對 sys_access_log 之 INSERT → rc 1 未分類。"""
        d = self._plant()
        _offline_plant_up(self, d, "UP_6_ACCESS",
                          "INSERT INTO sys_access_log (id, created_at, created_by, http_status, http_method, "
                          "http_path, real_ip) VALUES (1, '2026-08-05T00:00:00+00:00', 1, 200, 'GET', '/x', NULL)")
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 1, msg=msg)
        self.assertIn("[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_ACCESS） 未分類", msg)

    def test_9c_dml_target_outside_seed_tables_unclassified(self):
        """⑨c 標的表不屬凍結 seed 有 COPY 段之表（判準④b [`_offline_seed_table`]；RL-0080 逐途徑）：up 與 down 兩方向各植——
        凍結 seed 外之表名（seaql_migrations）、schema 限定名（`public.sys_menu`：標的位首詞素為 schema 名 public）→ 各 rc 1
        恰一條 [offline·分類] 指名該句。對照組：down 方向同句去 schema 限定（`DELETE FROM sys_menu …`）＝seed DML、rc 0
        （down 只分類）。"""
        cases = (
            ("down", "DELETE FROM seaql_migrations WHERE version = 'm0003_seed_button_governance'"),
            ("down", "DELETE FROM public.sys_menu WHERE id = 1"),
            ("up", "INSERT INTO seaql_migrations (version, applied_at) VALUES ('m0099_x', 1)"),
            ("up", "UPDATE public.sys_menu SET hide_in_menu = TRUE WHERE id = 78"),
        )
        for direction, sql in cases:
            with self.subTest(direction=direction, sql=sql):
                d = self._plant()
                const = f"{direction.upper()}_6_TGT"
                _offline_plant_up(self, d, const, sql, direction=direction)
                rc, msg = _offline_run(d)
                self.assertEqual(rc, 1, msg=msg)
                self.assertEqual(msg.count("    [offline·"), 1, msg=msg)
                self.assertIn(f"[offline·分類] m0003_seed_button_governance.rs {direction} 第 6 句（{const}） 未分類"
                              f"——句首「{sql[:20]}", msg)
        d = self._plant()
        _offline_plant_up(self, d, "DOWN_6_TGT", "DELETE FROM sys_menu WHERE id = 1", direction="down")
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 0, msg=msg)
        self.assertIn("down 6 句（seed DML 5、序列 1）", msg)

    def test_10_pk_undetermined_update_rc2(self):
        """⑩pk 未定住之 UPDATE（WHERE 只以非 pk 欄定列）→ rc 2 指名。"""
        d = self._plant()
        _offline_plant_up(self, d, "UP_6_LOOSE",
                          "UPDATE sys_menu SET hide_in_menu = TRUE WHERE route_name = 'manage_ip-rule'")
        rc, msg = _offline_run(d)
        self.assertEqual(rc, 2, msg=msg)
        self.assertIn("pk", msg)
        self.assertIn("UP_6_LOOSE", msg)

    def test_10b_dml_shape_beyond_paths_rc2(self):
        """⑩b 句形超出與 pk 未定住之他途徑（RL-0080 逐途徑）：UPDATE SET 右式非字面（欄參照串接、轉型字面後再串接）、
        `'…'::<多詞型>`、INSERT 欄清單缺 pk 欄、WHERE 同欄重複、WHERE 之 `<欄> = NULL`（SQL 恆不成立、該列不匹配）、
        元組 IN 之元組含 NULL（同理）、WHERE 第二個元組 IN（元組 IN 至多一個；容其覆寫前者＝前者所列前值不再比對）
        → 各 rc 2 指名其常數名。"""
        cases = (
            ("UP_6_SETCOL", "UPDATE sys_menu SET buttons = buttons || '[]'::jsonb WHERE id = 78", "句形超出"),
            ("UP_6_SETCAT", "UPDATE sys_menu SET menu_name = 'a'::text || 'b' WHERE id = 78", "句形超出"),
            ("UP_6_CASTMW", "UPDATE sys_menu SET menu_name = 'a'::character varying WHERE id = 78", "句形超出"),
            ("UP_6_INSPK", "INSERT INTO casbin_rule (ptype, v0) VALUES ('p', 'x')", "INSERT 欄清單未定住"),
            ("UP_6_DUPCOL", "UPDATE sys_menu SET hide_in_menu = TRUE WHERE id = 78 AND id = 79", "句形超出"),
            ("UP_6_EQNULL", "UPDATE sys_menu SET hide_in_menu = TRUE WHERE id = 77 AND buttons = NULL", "句形超出"),
            ("UP_6_INNULL", "UPDATE casbin_rule SET protected = TRUE WHERE (id, v1) IN ((58, NULL))", "句形超出"),
            ("UP_6_TWOIN", "UPDATE casbin_rule SET v5 = 'z' WHERE (v1, v2) IN (('nope', 'button')) "
                           "AND (id, v0) IN ((58, 'R_SUPER'))", "句形超出"),
        )
        for const_name, sql, needle in cases:
            with self.subTest(const_name=const_name):
                d = self._plant()
                _offline_plant_up(self, d, const_name, sql)
                rc, msg = _offline_run(d)
                self.assertEqual(rc, 2, msg=msg)
                self.assertIn(const_name, msg)
                self.assertIn(needle, msg)

    def test_10c_negative_integer_literal(self):
        """⑩c 整數字面帶負號（[`_sql_literal`] 之 `-<數>` 形；RL-0080 逐途徑）：直判 `-5`＝(-5,)；佈線植一句
        `UPDATE casbin_rule SET created_by = -1 WHERE id = 58` 並補其登記——帳 set created_by＝-1 → rc 0、＝1 → rc 1 指名
        E-010 與欄 created_by 兩值（負號被吞＝兩值同為 1 即假綠）。"""
        self.assertEqual(_sql_literal(_sql_tokens("-5", "合成")), (-5,))
        for v, want in ((-1, 0), (1, 1)):
            with self.subTest(ledger=v):
                entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": "casbin_rule",
                         "detail": {"pk": {"id": 58}, "set": {"created_by": v}}, "date": "2026-10-23"}
                d = self._plant(ledger=lambda es, entry=entry: es + [entry])
                _offline_plant_up(self, d, "UP_6_NEG", "UPDATE casbin_rule SET created_by = -1 WHERE id = 58")
                rc, msg = _offline_run(d)
                self.assertEqual(rc, want, msg=msg)
                if want:
                    self.assertIn("[offline·對賬] E-010（seed_update casbin_rule id=58；m0003_seed_button_governance.rs "
                                  "up 第 6 句（UP_6_NEG））｜欄 created_by：migration＝-1、演進帳＝1", msg)

    def test_10d_sql_identifier_quoting_and_folding(self):
        """⑩d SQL 識別字兩途徑（同 PG；[`_sql_tokens`] 之 q 詞素、[`_sql_ident`]；RL-0080 逐途徑）：①雙引號識別字＝欄參照、
        非字串字面——SET 右式、WHERE 右式、VALUES 項之 `"…"` 各 rc 2 句形超出（帳照字面登、當字串即假綠）②未加引號者摺小寫、
        雙引號者原樣——`UPDATE "sys_menu" SET HIDE_IN_MENU = TRUE WHERE ID = 78`、`UPDATE Sys_Menu SET "order" = 8 WHERE "id" = 78`
        配帳 → rc 0 且配對 10 筆；`UPDATE "SYS_MENU" …`（雙引號大寫＝凍結 seed 外之表）→ rc 1 未分類；
        `UPDATE sys_menu SET "HIDE_IN_MENU" = TRUE …`（雙引號大寫欄）配帳 hide_in_menu → rc 1 指名欄 HIDE_IN_MENU。"""
        def run(sql, setv):
            entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": "sys_menu",
                     "detail": {"pk": {"id": 78}, "set": setv}, "date": "2026-10-23"}
            d = self._plant(ledger=lambda es: es + [entry])
            _offline_plant_up(self, d, "UP_6_IDENT", sql)
            return d, _offline_run(d)

        for sql, setv in (
                ("UPDATE sys_menu SET menu_name = \"route_name\" WHERE id = 78", {"menu_name": "route_name"}),
                ("UPDATE sys_menu SET hide_in_menu = TRUE WHERE id = 78 AND route_name = \"manage_ip-rule\"",
                 {"hide_in_menu": True})):
            with self.subTest(quoted_value=sql):
                _d, (rc, msg) = run(sql, setv)
                self.assertEqual(rc, 2, msg=msg)
                self.assertIn("UP_6_IDENT", msg)
                self.assertIn("句形超出", msg)
        with self.subTest(quoted_value="VALUES"):
            rc, msg = _offline_run(self._plant(rs_edits=[(
                "'ipRule:unlock', 'button', '', '', '', FALSE, \\\n",
                "'ipRule:unlock', \\\"button\\\", '', '', '', FALSE, \\\n")]))
            self.assertEqual(rc, 2, msg=msg)
            self.assertIn("UP_3_INSERT_164", msg)
            self.assertIn("句形超出", msg)
        for sql, setv in (("UPDATE \"sys_menu\" SET HIDE_IN_MENU = TRUE WHERE ID = 78", {"hide_in_menu": True}),
                          ("UPDATE Sys_Menu SET \"order\" = 8 WHERE \"id\" = 78", {"order": 8})):
            with self.subTest(folded=sql):
                d, (rc, msg) = run(sql, setv)
                self.assertEqual(rc, 0, msg=msg)
                self.assertEqual(len(offline_report(d)[1]["pair_ids"]), 10)
        with self.subTest(quoted_upper="表"):
            _d, (rc, msg) = run("UPDATE \"SYS_MENU\" SET hide_in_menu = TRUE WHERE id = 78", {"hide_in_menu": True})
            self.assertEqual(rc, 1, msg=msg)
            self.assertIn("[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_IDENT） 未分類", msg)
        with self.subTest(quoted_upper="欄"):
            _d, (rc, msg) = run("UPDATE sys_menu SET \"HIDE_IN_MENU\" = TRUE WHERE id = 78", {"hide_in_menu": True})
            self.assertEqual(rc, 1, msg=msg)
            self.assertIn("｜欄 HIDE_IN_MENU：migration 有、演進帳缺", msg)

    def test_11_normalization_equivalences(self):
        """⑪正規化等價：元組 IN 換序綠；jsonb 緊湊與帶空白形綠；ISO 與 COPY 時戳形綠（真檔 SQL 為 ISO 形、帳為 COPY
        形；帳改他時區之同一時刻亦綠）；jsonb 語意不等（改一碼）紅。"""
        swap = [("        \"((58, 'role:add'), (59, 'role:edit'), (60, 'role:delete'), \\\n"
                 "         (61, 'menu:add'), (62, 'menu:edit'), (63, 'menu:delete'))\"",
                 "        \"((63, 'menu:delete'), (59, 'role:edit'), (60, 'role:delete'), \\\n"
                 "         (61, 'menu:add'), (62, 'menu:edit'), (58, 'role:add'))\"")]
        spaced = [('{"code":"ipRule:restore","desc":"恢復IP規則"},{"code":"ipRule:unlock","desc":"解鎖來源IP"}]',
                   '{"code":"ipRule:restore","desc":"恢復IP規則"}, {"code": "ipRule:unlock", "desc": "解鎖來源IP"} ]')]
        onechar = [('{"code":"ipRule:unlock","desc":"解鎖來源IP"}]"#',
                    '{"code":"ipRule:unlock","desc":"解鎖來源IQ"}]"#')]

        def tz_shift(es):
            for e in es:
                if e["id"] == "E-008":
                    self.assertEqual(e["detail"]["values"]["created_at"], "2026-08-05 00:00:00+00")
                    e["detail"]["values"]["created_at"] = "2026-08-05T08:00:00+08:00"
            return es

        self.assertIn("'2026-08-05T00:00:00+00:00'", _M0003_UP_3)     # SQL 側 ISO 形（帳側 COPY 形見 tz_shift）
        for kw, want in ((dict(rs_edits=swap), 0), (dict(rs_edits=spaced), 0), (dict(), 0),
                         (dict(ledger=tz_shift), 0), (dict(rs_edits=onechar), 1)):
            with self.subTest(case=kw, want=want):
                rc, msg = _offline_run(self._plant(**kw))
                self.assertEqual(rc, want, msg=msg)
        rc, msg = _offline_run(self._plant(rs_edits=onechar))
        self.assertIn("E-009", msg)
        self.assertIn("欄 buttons", msg)

    def test_11b_value_normalization_unit(self):
        """值正規化口徑逐族（直呼）：整數族、boolean（COPY t／f、SQL TRUE／FALSE、JSON 布林）、文字族（含帶長度形）、
        timestamptz（帶時區時刻；無時區＝rc 2）、jsonb（JSON 解析後語意：布林與數字不同值、數字依十進位值）、NULL
        三形、COPY 格跳脫還原（七形與 `\\N`；他形＝rc 2）；他欄型與凍結面無之欄＝rc 2；值不合欄型＝rc 2（整數族收布林／
        小數／非整數字串、boolean 收整數與 t／f 外之字串、文字族收整數／布林、timestamptz 收無時區、jsonb 收非字串值與壞
        JSON）。"""
        types = {("t", "i"): "bigint", ("t", "b"): "boolean", ("t", "s"): "character varying(20)",
                 ("t", "x"): "text", ("t", "ts"): TS_TZ, ("t", "j"): "jsonb", ("t", "ip"): "inet",
                 ("t", "si"): "smallint", ("t", "n"): "integer"}
        v = _offline_value
        self.assertEqual(v(types, "t", "i", "58"), v(types, "t", "i", 58))
        self.assertEqual(v(types, "t", "si", 7), 7)
        self.assertEqual(v(types, "t", "n", "7"), 7)
        self.assertIs(v(types, "t", "b", "t"), True)
        self.assertIs(v(types, "t", "b", False), False)
        self.assertEqual(v(types, "t", "s", "a"), "a")
        self.assertEqual(v(types, "t", "x", ""), "")
        self.assertEqual(v(types, "t", "ts", "2026-08-05 00:00:00+00"),
                         v(types, "t", "ts", "2026-08-05T00:00:00+00:00"))
        self.assertNotEqual(v(types, "t", "ts", "2026-08-05 00:00:00+00"),
                            v(types, "t", "ts", "2026-08-05 00:00:01+00"))
        self.assertEqual(v(types, "t", "j", '[{"a": 1}]'), v(types, "t", "j", '[{"a":1}]'))
        # jsonb 之布林與數字不同值（PG jsonb 之 true≠1、false≠0；Python 之 True == 1 不得帶入），逐層皆然；數字依
        # 十進位值比（PG numeric 語意：1 與 1.0、1e2 與 100 同值，逾雙精度之位數照比）
        for a, b in (('[{"a": true}]', '[{"a": 1}]'), ('{"a": false}', '{"a": 0}'), ("true", "1"),
                     ("[[false]]", "[[0]]"), ("[1.00000000000000001]", "[1]")):
            with self.subTest(jsonb_ne=(a, b)):
                self.assertNotEqual(v(types, "t", "j", a), v(types, "t", "j", b))
        for a, b in (('[{"a": true}]', '[{"a":true}]'), ('{"a": 1}', '{"a": 1.0}'), ("[1e2]", "[100]"),
                     ('{"b": [false, null], "a": 2}', '{"a": 2, "b": [false, null]}')):
            with self.subTest(jsonb_eq=(a, b)):
                self.assertEqual(v(types, "t", "j", a), v(types, "t", "j", b))
        # COPY text 格（左源讀面）：`\N`＝None；pg_dump 文字輸出之反斜線跳脫七形逐一還原；他形與孤立反斜線＝rc 2 指名
        self.assertIsNone(_copy_value("\\N"))
        self.assertEqual(_copy_value("plain"), "plain")
        self.assertEqual(_copy_value("a\\\\b\\tc\\nd\\re\\bf\\fg\\vh"), "a\\b\tc\nd\re\bf\fg\vh")
        for bad in ("\\q", "a\\Nb", "a\\"):
            with self.subTest(copy_bad=bad):
                with self.assertRaises(GateError) as cm:
                    _copy_value(bad)
                self.assertIn("未支援之跳脫", str(cm.exception))
        for col in ("i", "ip", "j"):
            self.assertIsNone(v(types, "t", col, None))
        # 值不合欄型＝rc 2：逐族釘寬收途徑之反例——Python 之 True == 1、int(8.7) == 8、jsonb 原生值經 _offline_jsonb
        # 即與字串解析同形，寬收任一途徑皆令型別錯置之帳值假綠
        for col, bad, needle in (("ip", "10.0.0.1", "未支援"), ("zz", 1, "不在凍結 columns.json"),
                                 ("ts", "2026-08-05 00:00:00", "無法正規化"), ("i", True, "無法正規化"),
                                 ("i", 8.7, "無法正規化"), ("n", 8.0, "無法正規化"), ("i", "8.7", "無法正規化"),
                                 ("b", "yes", "無法正規化"), ("b", 1, "無法正規化"), ("b", 0, "無法正規化"),
                                 ("x", 5, "無法正規化"), ("x", True, "無法正規化"), ("j", "{bad", "無法正規化"),
                                 ("j", True, "無法正規化"), ("j", 5, "無法正規化"), ("j", [1], "無法正規化")):
            with self.subTest(col=col, bad=bad):
                with self.assertRaises(GateError) as cm:
                    v(types, "t", col, bad)
                self.assertIn(needle, str(cm.exception))

    def test_11c_jsonb_bool_vs_number_rc1(self):
        """⑪c jsonb 布林與數字之區辨佈線：副本 UP_4 新值之末元素加 `"on":1`、帳 E-009 同位登 `"on": true` → rc 1 指名 E-009
        欄 buttons（PG jsonb 之 true 與 1 不等）；對照組帳同登 `"on": 1` → rc 0。"""
        rs = [('{"code":"ipRule:unlock","desc":"解鎖來源IP"}]"#', '{"code":"ipRule:unlock","desc":"解鎖來源IP","on":1}]"#')]

        def on(val):
            def edit(es):
                for e in es:
                    if e["id"] == "E-009":
                        b = e["detail"]["set"]["buttons"]
                        self.assertTrue(b.endswith('"}]'), msg=b)
                        e["detail"]["set"]["buttons"] = b[:-2] + f', "on": {val}}}]'
                return es
            return edit

        for val, want in (("true", 1), ("1", 0)):
            with self.subTest(val=val):
                rc, msg = _offline_run(self._plant(rs_edits=rs, ledger=on(val)))
                self.assertEqual(rc, want, msg=msg)
                if want:
                    self.assertIn("[offline·對賬] E-009", msg)
                    self.assertIn("欄 buttons", msg)

    def test_11d_cast_family_must_match_column(self):
        """⑪d 轉型之型與欄型同族（判準①i）：`'…'::<型>` 之型詞須屬該欄之值正規化族——PG 先依轉型之型解析字面、再以指派
        轉型落欄，異族時落值可≠字面，照字面比即假綠。副本 UP 尾植一句改選單 78、帳補 E-010：同族（`::VARCHAR`；型詞
        大小寫不敏感）＝rc 0；異族＝rc 2 指名型詞——SET 側 `::char`（PG 截為 character(1)）、`::jsonb` 與 `::timestamptz`
        入文字欄（經 I/O 轉文字＝重排鍵並補空白、依 session 時區重輸出）、`::timestamp` 入 timestamptz 欄（丟 offset）；
        WHERE 前值側 `::char`；pk 側 `'78'::text`（配對鍵）。真檔 UP_4 之 `::jsonb` 入 jsonb 欄＝真 repo 綠案承擔。"""
        def run(sql, setv):
            entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": "sys_menu",
                     "detail": {"pk": {"id": 78}, "set": setv}, "date": "2026-10-23"}
            d = self._plant(ledger=lambda es: es + [entry])
            _offline_plant_up(self, d, "UP_6_CAST", sql)
            return _offline_run(d)

        rc, msg = run("UPDATE sys_menu SET menu_name = 'abc'::VARCHAR WHERE id = 78", {"menu_name": "abc"})
        self.assertEqual(rc, 0, msg=msg)
        for sql, setv, word in (
                ("UPDATE sys_menu SET menu_name = 'abc'::char WHERE id = 78", {"menu_name": "abc"}, "char"),
                ("UPDATE sys_menu SET menu_name = '{\"bb\":1,\"a\":2}'::jsonb WHERE id = 78",
                 {"menu_name": "{\"bb\":1,\"a\":2}"}, "jsonb"),
                ("UPDATE sys_menu SET menu_name = '2026-08-05T08:00:00+08:00'::timestamptz WHERE id = 78",
                 {"menu_name": "2026-08-05T08:00:00+08:00"}, "timestamptz"),
                ("UPDATE sys_menu SET updated_at = '2026-08-05 00:00:00+08'::timestamp WHERE id = 78",
                 {"updated_at": "2026-08-05 00:00:00+08"}, "timestamp"),
                ("UPDATE sys_menu SET menu_name = 'abc' WHERE id = 78 AND menu_name = 'x'::char",
                 {"menu_name": "abc"}, "char"),
                ("UPDATE sys_menu SET menu_name = 'abc' WHERE id = '78'::text", {"menu_name": "abc"}, "text")):
            with self.subTest(sql=sql):
                rc, msg = run(sql, setv)
                self.assertEqual(rc, 2, msg=msg)
                self.assertIn("[offline] ✗", msg)
                self.assertIn(f"帶轉型 ::{word}，", msg)
                self.assertIn("不同族", msg)

    def test_11e_cast_family_unit_matrix(self):
        """⑪e 判準①i 逐型詞（直呼 [`_offline_value`]）：同族型詞照正規化、與無轉型之同值相等（int 族 bigint／int8／
        integer／int／int4／smallint／int2；boolean／bool；text／varchar；timestamptz；jsonb；大小寫不敏感）；他族型詞與
        表外型詞（char、bpchar、name、json、timestamp、date、numeric、float8、uuid、inet）＝rc 2 指名型詞；無轉型之字串
        值不查型詞。"""
        types = {("t", "i"): "bigint", ("t", "si"): "smallint", ("t", "b"): "boolean",
                 ("t", "s"): "character varying", ("t", "x"): "text", ("t", "ts"): TS_TZ, ("t", "j"): "jsonb"}
        sample = {"i": "5", "si": "5", "b": "t", "s": "a", "x": "a", "ts": "2026-08-05 00:00:00+00", "j": "[1]"}
        cols = {"i": "int", "si": "int", "b": "bool", "s": "str", "x": "str", "ts": "ts", "j": "jsonb"}
        fams = {"int": ("bigint", "int8", "integer", "int", "int4", "smallint", "int2"), "bool": ("boolean", "bool"),
                "str": ("text", "varchar"), "ts": ("timestamptz",), "jsonb": ("jsonb",)}
        outside = ("char", "bpchar", "name", "json", "timestamp", "date", "numeric", "float8", "uuid", "inet")
        v = _offline_value
        for col, fam in cols.items():
            plain = v(types, "t", col, sample[col])
            for f2, words in fams.items():
                for w in words + (words[0].upper(),):
                    with self.subTest(col=col, word=w):
                        if f2 == fam:
                            self.assertEqual(v(types, "t", col, _SqlCast(sample[col], w)), plain)
                        else:
                            with self.assertRaises(GateError) as cm:
                                v(types, "t", col, _SqlCast(sample[col], w))
                            self.assertIn(f"帶轉型 ::{w}，", str(cm.exception))
                            self.assertIn("不同族", str(cm.exception))
            for w in outside:
                with self.subTest(col=col, outside=w):
                    with self.assertRaises(GateError) as cm:
                        v(types, "t", col, _SqlCast(sample[col], w))
                    self.assertIn(f"帶轉型 ::{w}，", str(cm.exception))
        self.assertEqual(v(types, "t", "s", "abc"), "abc")
        self.assertEqual(_sql_literal([("s", "abc", 0, 5), ("p", "::", 5, 7), ("w", "Text", 7, 11)]), ("abc",))
        self.assertEqual(_sql_literal([("s", "abc", 0, 5), ("p", "::", 5, 7), ("w", "Text", 7, 11)])[0].cast, "Text")

    def test_11f_pg_silent_value_change_rejected(self):
        """⑪f PG 落值≠字面之值（判準①l [`_offline_pg_exact`]；fail-closed、RL-0080 逐途徑）：①timestamptz 小數秒逾六位——PG 依
        rint 進位至微秒（`.0000007`→`.000001`）、Python fromisoformat 截斷（→`.000000`），照比即假綠 ②character varying(n) 欄值長度
        逾 n——PG 於超出部分全為空白時靜默截斷至 n（否則報錯）。佈線：植一句 UPDATE 並補同值之登記 → rc 2 指名欄與途徑；對照組
        （恰六位小數秒、恰 n 字元）→ rc 0。直呼：COPY 形與 ISO 形同判、無長度之 character varying 與 text 不限長、超出部分非空白
        亦拒、非字串值不入本判（照「值不合欄型」rc 2）。"""
        pad = "p" + " " * 30
        cases = (
            ("sys_menu", 78, "updated_at", "'2026-08-05 00:00:00.0000007+00'", "2026-08-05 00:00:00+00", 2,
             "小數秒逾六位"),
            ("sys_menu", 78, "updated_at", "'2026-08-05 00:00:00.000001+00'", "2026-08-05 00:00:00.000001+00", 0, None),
            ("casbin_rule", 58, "ptype", f"'{pad}'", pad, 2, "逾欄長 18"),
            ("casbin_rule", 58, "ptype", f"'{pad[:18]}'", pad[:18], 0, None),
        )
        for table, pk, col, lit, ledger_v, want, needle in cases:
            with self.subTest(col=col, lit=lit):
                entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": table,
                         "detail": {"pk": {"id": pk}, "set": {col: ledger_v}}, "date": "2026-10-23"}
                d = self._plant(ledger=lambda es, entry=entry: es + [entry])
                _offline_plant_up(self, d, "UP_6_EXACT", f"UPDATE {table} SET {col} = {lit} WHERE id = {pk}")
                rc, msg = _offline_run(d)
                self.assertEqual(rc, want, msg=msg)
                if needle:
                    self.assertIn("[offline] ✗", msg)
                    self.assertIn(f"{table}.{col}", msg)
                    self.assertIn(needle, msg)
        types = {("t", "ts"): TS_TZ, ("t", "s"): "character varying(3)", ("t", "u"): "character varying",
                 ("t", "x"): "text"}
        v = _offline_value
        self.assertEqual(v(types, "t", "ts", "2026-08-05T00:00:00.123456+00:00"),
                         v(types, "t", "ts", "2026-08-05 00:00:00.123456+00"))
        self.assertEqual(v(types, "t", "s", "abc"), "abc")
        self.assertEqual(v(types, "t", "u", "a" * 300), "a" * 300)
        self.assertEqual(v(types, "t", "x", "a" * 300), "a" * 300)
        for col, bad, needle in (("ts", "2026-08-05T00:00:00.1234567+00:00", "小數秒逾六位"),
                                 ("ts", "2026-08-05 00:00:00.0000001+00", "小數秒逾六位"),
                                 ("s", "abc ", "逾欄長 3"), ("s", "abcd", "逾欄長 3"),
                                 ("s", _SqlCast("ab  ", "varchar"), "逾欄長 3"),
                                 ("s", 5, "無法正規化"), ("ts", 5, "無法正規化")):
            with self.subTest(col=col, bad=bad):
                with self.assertRaises(GateError) as cm:
                    v(types, "t", col, bad)
                self.assertIn(needle, str(cm.exception))

    def test_12_cmd_rc2_wiring(self):
        """rc 2 佈線：delta 目錄缺席、演進帳缺席、fixtures 缺席、解析他形（include_str!）皆 rc 2、訊息帶 [offline] ✗。"""
        def no_dir(d):
            shutil.rmtree(os.path.join(d, OFFLINE_MIGRATION_DIR))

        def no_ledger(d):
            os.remove(os.path.join(d, LEDGER))

        def no_seed(d):
            os.remove(os.path.join(d, FIXTURES_DIR, "seed.sql"))

        for fn, needle in ((no_dir, "缺席"), (no_ledger, "schema-evolution.json"), (no_seed, "seed.sql")):
            with self.subTest(needle=needle):
                d = self._plant()
                fn(d)
                rc, msg = _offline_run(d)
                self.assertEqual(rc, 2, msg=msg)
                self.assertIn("[offline] ✗", msg)
                self.assertIn(needle, msg)
        rc, msg = _offline_run(self._plant(rs_edits=[(
            "const UP_FAIL_TAIL: &str =", 'const X_SQL: &str = include_str!("x.sql");\nconst UP_FAIL_TAIL: &str =')]))
        self.assertEqual(rc, 2, msg=msg)
        self.assertIn("include_str!", msg)

    def test_13_zero_docker(self):
        """⑬零 docker（BL-00148 常跑鏈前提）：_run_docker 換為呼叫即 raise 之樁、subprocess.run／Popen 包裝為 argv[0]＝
        docker 即 raise（他 argv 照轉），真 repo cmd_offline() 仍 rc 0 且樁零呼叫。"""
        mod = sys.modules[__name__]
        calls = []

        def docker_stub(*a, **kw):
            calls.append(("_run_docker", a))
            raise AssertionError("offline 觸及 _run_docker（須零 docker）")

        def guard(orig):
            def wrapped(argv, *a, **kw):
                head = argv[0] if isinstance(argv, (list, tuple)) and argv else argv
                if isinstance(head, str) and os.path.basename(head.split()[0] if head else "") == "docker":
                    calls.append(("subprocess", argv))
                    raise AssertionError(f"offline 起 docker 子行程：{argv}")
                return orig(argv, *a, **kw)
            return wrapped

        with unittest.mock.patch.object(mod, "_run_docker", docker_stub), \
                unittest.mock.patch.object(subprocess, "run", guard(subprocess.run)), \
                unittest.mock.patch.object(subprocess, "Popen", guard(subprocess.Popen)):
            rc, msg = _offline_run()
        self.assertEqual(rc, 0, msg=msg)
        self.assertEqual(calls, [])


# ⑨／④停用之植入句：對收窄表 sys_operation_log 之 INSERT（全欄；inet 欄給 NULL——NULL 不查欄型）
_OFFLINE_OPLOG_COLS = ("id", "created_at", "created_by", "operation", "entity_table", "entity_id",
                       "payload_before", "payload_after", "real_ip", "peer_ip", "x_forwarded_for",
                       "ip_confidence", "region", "trace_id")
_OFFLINE_OPLOG_INSERT = (f"INSERT INTO sys_operation_log ({', '.join(_OFFLINE_OPLOG_COLS)}) VALUES "
                         "(1, '2026-08-05T00:00:00+00:00', NULL, 'update', 'sys_menu', NULL, NULL, NULL, "
                         "NULL, NULL, NULL, NULL, NULL, NULL)")


def _offline_lenient(orig, fallback):
    """恆放行之樁（判準停用）：原函式照跑，其 GateError（他形＝rc 2 之判）一律吞為 fallback——合形者照常產出，
    只拆掉「他形即紅」這一條判準。"""
    def stub(*a):
        try:
            return orig(*a)
        except GateError:
            return fallback
    return stub


class TestOfflineCriterionMutants(_OfflineRoots, unittest.TestCase):
    """offline 逐判準停用變異（RL-0080；T008）：每判準一案、各案只停一支、不疊加。做法＝以 unittest.mock.patch.object
    把該判準函式換為恆放行之樁，重跑其專屬植入案：未停用下判紅（rc 與前綴指名）、停用下判綠（rc 0）——
    ＝原植入案轉紅之機器載體（拆掉該判準即本類對應案紅）。判準 → 函式：①a 常數右式他形 [`_offline_const_rhs`]
    ／①b macro_rules! 他形 [`_offline_macro_body`]／①c up／down 句形 [`_offline_body_stmt`]／①d SQL 句形與 pk 定住
    [`_offline_dml_records`]／①e 欄型未支援 [`_offline_family`]／①f 同名重複宣告 [`_offline_unique_name`]（常數與
    macro_rules! 兩名冊各一植入）／①g 未支援之 SQL 詞素 [`_sql_unsupported`]／①h SQL 註解切為單一詞素
    [`_sql_comment_end`]／①i 轉型之型與欄型同族 [`_offline_cast_ok`]／①j 檔外巨集引入 [`_offline_foreign_scope`]（檔案模組
    與 use 含 concat 兩途徑各一植入）／①k 檔內巨集之文本作用域 [`_offline_macro_reach`]（定義在後與 inline mod 兩途徑各一植入）
    ／①l PG 落值≠字面之值 [`_offline_pg_exact`]（varchar(n) 逾長與 timestamptz 小數秒逾六位兩途徑各一植入）
    ／①m impl 綁定 [`_offline_impl_binding`]（TestOfflineParse impl 綁定案之四款逐途徑與審查三植入各一植入）
    ／①n 字串、字元字面與註解之外之字元白名單 [`_rust_unsupported`]（非 ASCII 名與 rustc 空白兩途徑各一植入）
    ／②分類器之未分類即紅 [`_offline_classify_findings`]
    ／③DO 塊嚴格形 [`_offline_do_block`]／③b CREATE ROLE 選項尾段白名單 [`_offline_role_options`]（裸形與 DO 包裝形
    兩呼叫點）／④收窄表 DML 排除 [`_offline_narrowed_table`]／④b seed 表成員 [`_offline_seed_table`]（凍結 seed 外之表名與
    schema 限定名兩途徑各一植入）／⑤DML↔帳對賬 [`_offline_ledger_findings`]（兩案）
    ／⑥前值對賬 [`_offline_prevalue_findings`]／⑦比對面為空
    [`_offline_assert_nonempty`]／⑧前序配對合成 [`_offline_advance_left`]。與既有判準共用之件（load_ledger 啟動
    斷言、apply_seed_entries 之 GateError）由既有案承擔。"""

    def _flip(self, root, name, stub, want_rc, needle):
        rc, msg = _offline_run(root)
        self.assertEqual(rc, want_rc, msg=msg)
        self.assertIn(needle, msg)
        with unittest.mock.patch.object(sys.modules[__name__], name, stub):
            rc, msg = _offline_run(root)
        self.assertEqual(rc, 0, msg=f"停用 {name} 後應判綠：\n{msg}")

    def _plant_up(self, const_name, sql, **kw):
        d = self._plant(**kw)
        _offline_plant_up(self, d, const_name, sql)
        return d

    def test_1a_const_rhs_other_form(self):
        d = self._plant(rs_edits=[("const UP_FAIL_TAIL: &str =",
                                   'const X_SQL: &str = include_str!("x.sql");\nconst UP_FAIL_TAIL: &str =')])
        self._flip(d, "_offline_const_rhs", _offline_lenient(_offline_const_rhs, ""), 2, "include_str!")

    def test_1b_macro_rules_other_form(self):
        d = self._plant(rs_edits=[("/// ① 六碼改受保護", 'macro_rules! with_arg {\n    ($x:expr) => {\n'
                                                       '        "a"\n    };\n}\n\n/// ① 六碼改受保護')])
        self._flip(d, "_offline_macro_body", _offline_lenient(_offline_macro_body, ""), 2,
                   "macro_rules! with_arg")

    def test_1f_duplicate_name(self):
        """同名第二次宣告（常數與 macro_rules! 兩名冊共用一判）：常數案＝模組層與他函式本體內之同名雙宣告、up 所綁者為模組層
        之前者＝未登之 seed DML——停用＝退回文本序後者勝出（setval 序列句）→ 判綠（`#[cfg]` 互斥雙宣告形另觸判準①m 之零 cfg 款、
        不作本案載體；其 rc 2 由 TestOfflineParse 同名重複宣告案釘）；macro_rules! 同名兩宣告未被引用、停用下照綠。"""
        anchor = "const UP_FAIL_TAIL: &str ="
        up5 = "        db.execute_unprepared(UP_5_SETVAL).await?;\n"
        cases = (
            ("常數", [(up5, up5 + "        db.execute_unprepared(UP_6_X).await?;\n"),
                      (anchor, 'const UP_6_X: &str = "DELETE FROM sys_role WHERE id = 1";\n'
                               "fn helper() {\n"
                               "    const UP_6_X: &str = \"SELECT setval('casbin_rule_id_seq', 164, true)\";\n}\n"
                               + anchor)],
             "常數 UP_6_X 重複定義"),
            ("macro_rules!", [(anchor, 'macro_rules! dup_m {\n    () => {\n        "a"\n    };\n}\n'
                                       'macro_rules! dup_m {\n    () => {\n        "b"\n    };\n}\n' + anchor)],
             "macro_rules! dup_m 重複定義"),
        )
        for label, edits, needle in cases:
            with self.subTest(label=label):
                d = self._plant(rs_edits=edits)
                self._flip(d, "_offline_unique_name", lambda *a: None, 2, needle)

    def test_1c_body_statement_form(self):
        d = self._plant(rs_edits=[("        db.execute_unprepared(UP_5_SETVAL).await?;\n",
                                   "        db.execute_unprepared(UP_5_SETVAL).await?;\n"
                                   "        manager.create_table(Table::create().to_owned()).await?;\n")])
        self._flip(d, "_offline_body_stmt", _offline_lenient(_offline_body_stmt, []), 2,
                   "manager.create_table(")

    def test_1d_dml_shape_and_pk_pinned(self):
        d = self._plant_up("UP_6_LOOSE", "UPDATE sys_menu SET hide_in_menu = TRUE WHERE route_name = 'x'")
        self._flip(d, "_offline_dml_records", _offline_lenient(_offline_dml_records, []), 2, "定住")

    def test_1e_unsupported_column_type(self):
        d = self._plant()
        path = os.path.join(d, FIXTURES_DIR, "columns.json")
        cols = _load_json(path, "columns.json")
        hit = [c for c in cols if (c["table"], c["column"]) == ("casbin_rule", "v3")]
        self.assertEqual(len(hit), 1)
        hit[0]["type"] = "inet"           # 未支援欄型；E-008 之 values 比到 v3（'' 對 ''）
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(cols, fh, ensure_ascii=False)
        orig = _offline_family
        self._flip(d, "_offline_family", lambda t: orig(t) or "str", 2, "未支援")

    def test_1g_unsupported_sql_lexeme(self):
        """down 方向 seed DML 之 SET 值以標籤式 dollar 引號藏一句 ALTER（TestOfflineLeg ⑧d 首例）：停用＝`$` 照標點切、單引號照常
        配對 → 三句併一句、歸 seed DML（down 只分類）→ 判綠。"""
        d = self._plant()
        _offline_plant_up(self, d, "DOWN_6_LEX", "UPDATE casbin_rule SET v3 = $q$a'b$q$ WHERE id = 165; "
                          "ALTER TABLE sys_user ADD COLUMN x text; UPDATE casbin_rule SET v3 = $q$c'd$q$ WHERE id = 165",
                          direction="down")
        self._flip(d, "_sql_unsupported", lambda sql, i: None, 2, "未支援之 SQL 詞素")

    def test_1h_sql_comment_single_lexeme(self):
        """down 方向 seed DML 之 `--` 註解含單引號、與次句句尾之註解成對（TestOfflineLeg ⑧d 註解例）：停用＝註解字元照標點切 →
        兩引號配成「字串」吞下頂層 `;` → 兩句併一句、歸 seed DML → 判綠。"""
        d = self._plant()
        _offline_plant_up(self, d, "DOWN_6_CMT", "DELETE FROM casbin_rule WHERE id = 165 -- '\n; "
                          "ALTER TABLE sys_user ADD COLUMN x text -- '", direction="down")
        self._flip(d, "_sql_comment_end", lambda sql, i, where: None, 1,
                   "[offline·分類] m0003_seed_button_governance.rs down 第 7 句（DOWN_6_CMT）")

    def test_1i_cast_family(self):
        """判準①i（轉型之型與欄型同族；TestOfflineLeg ⑪d 首例）：副本 UP 尾植 `menu_name = 'abc'::char`、帳補 E-010 set
        'abc'——停用＝轉型註記透明、照字面比 → 判綠。"""
        entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": "sys_menu",
                 "detail": {"pk": {"id": 78}, "set": {"menu_name": "abc"}}, "date": "2026-10-23"}
        d = self._plant_up("UP_6_CAST", "UPDATE sys_menu SET menu_name = 'abc'::char WHERE id = 78",
                           ledger=lambda es: es + [entry])
        self._flip(d, "_offline_cast_ok", lambda cast, fam: True, 2, "帶轉型 ::char，")

    def test_1l_pg_exact_value(self):
        """判準①l（PG 落值≠字面之值；TestOfflineLeg ⑪f 兩途徑各一植入）：①timestamptz 小數秒七位、帳登截斷後之值 ②character
        varying(18) 欄植 31 字元（超出部分全為空白）、帳登同值——停用＝照 Python 解析值比 → 判綠。"""
        pad = "p" + " " * 30
        for table, pk, col, lit, ledger_v, needle in (
                ("sys_menu", 78, "updated_at", "'2026-08-05 00:00:00.0000007+00'", "2026-08-05 00:00:00+00",
                 "小數秒逾六位"),
                ("casbin_rule", 58, "ptype", f"'{pad}'", pad, "逾欄長 18")):
            with self.subTest(col=col):
                entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_update", "table": table,
                         "detail": {"pk": {"id": pk}, "set": {col: ledger_v}}, "date": "2026-10-23"}
                d = self._plant_up("UP_6_EXACT", f"UPDATE {table} SET {col} = {lit} WHERE id = {pk}",
                                   ledger=lambda es, entry=entry: es + [entry])
                self._flip(d, "_offline_pg_exact", lambda coltype, fam, v: None, 2, needle)

    def test_1j_foreign_macro_scope(self):
        """判準①j（檔外巨集引入；TestOfflineParse 檔外巨集引入案之兩途徑）：①`#[macro_use] mod shadow;`（另一子案名為 raw 識別字
        `r#shadow`）植於 UP_1_PROTECT_SIX 之前、shadow.rs 之同名 six_button_rows! 展開藏一句 DELETE（遷移二進位所編者）
        ②`use crate::evil as concat;`（內建 concat! 被匯入者遮蔽）——停用＝本腿照檔內定義與內建 concat! 展開 → 判綠。"""
        shadow = {os.path.join(OFFLINE_MIGRATION_DIR, "m0003_seed_button_governance", "shadow.rs"): _OFFLINE_EVIL_SIX}
        cases = (
            ("檔案模組", dict(rs_edits=[(_M0003_UP_1_HEAD, "#[macro_use]\nmod shadow;\n\n" + _M0003_UP_1_HEAD)],
                          extra=shadow),
             "檔案模組宣告 mod shadow;"),
            ("檔案模組 r#<名>", dict(rs_edits=[(_M0003_UP_1_HEAD, "#[macro_use]\nmod r#shadow;\n\n" + _M0003_UP_1_HEAD)],
                                 extra=shadow),
             "檔案模組宣告 mod shadow;"),
            ("use … as concat", dict(rs_edits=[(_M0003_USE_LINE, _M0003_USE_LINE + "use crate::evil as concat;\n")]),
             "use 宣告含 concat"),
        )
        for label, kw, needle in cases:
            with self.subTest(label=label):
                self._flip(self._plant(**kw), "_offline_foreign_scope", lambda *a: None, 2, needle)

    def test_1n_unsupported_char(self):
        """判準①n（字串、字元字面與註解之外之字元白名單；TestOfflineParse 未支援字元案之兩類途徑各一植入）：`#[macro_use]` 檔案模組
        宣告植於 UP_1_PROTECT_SIX 之前、所引入之檔之同名 six_button_rows! 展開藏一句 DELETE——①非 ASCII 名（`#[path = "shadow.rs"]
        mod 影;`）②`mod` 與名之間為 rustc 空白 U+200E——停用＝白名單外字元照標點切、判準①j 之三詞素比對落空 → 判綠。"""
        src = OFFLINE_MIGRATION_DIR
        for decl, extra in (('#[path = "shadow.rs"]\nmod 影;', os.path.join(src, "shadow.rs")),
                            ("mod\u200eshadow;", os.path.join(src, "m0003_seed_button_governance", "shadow.rs"))):
            with self.subTest(decl=decl):
                d = self._plant(rs_edits=[(_M0003_UP_1_HEAD, "#[macro_use]\n" + decl + "\n\n" + _M0003_UP_1_HEAD)],
                                extra={extra: _OFFLINE_EVIL_SIX})
                self._flip(d, "_rust_unsupported", lambda c: None, 2, "未支援字元")

    def test_1k_macro_textual_scope(self):
        """判準①k（檔內巨集之文本作用域；TestOfflineParse 文本作用域案之前兩途徑）：①UP_1_PROTECT_SIX 移至 six_button_rows! 定義
        之前、配 `use crate::evil_six as six_button_rows;`（Rust 循路徑綁到匯入者）②six_button_rows! 定義移入 inline mod——停用＝
        本腿照檔內定義展開 → 判綠。"""
        for label, edits in _OFFLINE_MACRO_SCOPE_EDITS[:2]:
            with self.subTest(label=label):
                self._flip(self._plant(rs_edits=edits), "_offline_macro_reach", lambda *a: None, 2,
                           "常數 UP_1_PROTECT_SIX 呼叫之檔內巨集 six_button_rows!")

    def test_1m_impl_binding(self):
        """判準①m（impl 綁定；TestOfflineParse impl 綁定案之全部途徑各一植入）：停用＝本腿照字面 head 之 up／down 解析 → 判綠。
        各案暫存根另寫入 lib.rs 之 `#[cfg(not(test))]` 限定路徑實作（「head 冠 #[cfg(test)]」案之遷移二進位所跑者；本腿不讀 lib.rs）。"""
        lib_rs = ("#[cfg(not(test))]\n#[async_trait::async_trait]\n"
                  "impl sea_orm_migration::MigrationTrait for m0003_seed_button_governance::Migration {\n"
                  + _OFFLINE_EVIL_UP + "}\n")
        for label, edits, _needle in _OFFLINE_IMPL_BINDING_EDITS:
            with self.subTest(label=label):
                d = self._plant(rs_edits=edits, extra={os.path.join(OFFLINE_MIGRATION_DIR, "lib.rs"): lib_rs})
                self._flip(d, "_offline_impl_binding", lambda *a: None, 2, "impl 綁定")

    def test_2_classifier_unclassified_red(self):
        d = self._plant_up("UP_6_ALTER", "ALTER TABLE sys_user ADD COLUMN x text")
        self._flip(d, "_offline_classify_findings", lambda stmts: [], 1, "[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_ALTER）")

    def test_3_do_block_strict_form(self):
        d = self._plant_up("UP_6_DO", "DO $$ BEGIN UPDATE sys_menu SET hide_in_menu = TRUE WHERE id = 78; END $$")
        self._flip(d, "_offline_do_block", lambda body, where: {"kind": "DO", "role": None, "objects": {}}, 1,
                   "[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_DO）")

    def test_3b_create_role_option_tail(self):
        """CREATE ROLE 選項尾段白名單（裸形與 DO 包裝形兩呼叫點各一植入：成員子句＋註解）。"""
        for sql in ("CREATE ROLE reaper IN ROLE pg_write_all_data", "CREATE ROLE reaper -- 註解",
                    "DO $$ BEGIN CREATE ROLE reaper IN ROLE pg_write_all_data; "
                    "EXCEPTION WHEN duplicate_object THEN NULL; END $$"):
            with self.subTest(sql=sql):
                d = self._plant_up("UP_6_ROLE", sql)
                self._flip(d, "_offline_role_options", lambda opts: True, 1,
                           "[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_ROLE）")

    def test_4_narrowed_table_dml_excluded(self):
        """植入副本帳同補該句之 seed_add 登記：停用後該句改歸 seed DML 時⑤對賬亦綠（停用下判綠不被⑤遮蔽）。"""
        entry = {"id": "E-010", "knife": "001-schema-baseline", "kind": "seed_add", "table": "sys_operation_log",
                 "detail": {"pk": ["id"], "values": {c: None for c in _OFFLINE_OPLOG_COLS}},
                 "date": "2026-10-23"}
        entry["detail"]["values"].update({"id": 1, "created_at": "2026-08-05 00:00:00+00",
                                          "operation": "update", "entity_table": "sys_menu"})
        d = self._plant_up("UP_6_OPLOG", _OFFLINE_OPLOG_INSERT, ledger=lambda es: es + [entry])
        self._flip(d, "_offline_narrowed_table", lambda table: False, 1, "[offline·分類] m0003_seed_button_governance.rs up 第 6 句（UP_6_OPLOG）")

    def test_4b_seed_table_member(self):
        """判準④b（seed 表成員；TestOfflineLeg ⑨c 之 down 兩途徑）：down 方向植對 seaql_migrations 或 schema 限定名
        `public.sys_menu` 之 DELETE——停用＝凡 DML 標的皆歸 seed DML（down 只分類）→ 判綠。"""
        for sql in ("DELETE FROM seaql_migrations WHERE version = 'm0003_seed_button_governance'",
                    "DELETE FROM public.sys_menu WHERE id = 1"):
            with self.subTest(sql=sql):
                d = self._plant()
                _offline_plant_up(self, d, "DOWN_6_TGT", sql, direction="down")
                self._flip(d, "_offline_seed_table", lambda table, seed_tables: True, 1,
                           "[offline·分類] m0003_seed_button_governance.rs down 第 6 句（DOWN_6_TGT）")

    def test_5a_ledger_value_mismatch(self):
        d = self._plant(rs_edits=[("'ipRule:unlock', 'button', '', '', '', FALSE, \\\n",
                                   "'ipRule:unlocX', 'button', '', '', '', FALSE, \\\n")])
        self._flip(d, "_offline_ledger_findings", lambda *a: [], 1, "[offline·對賬] E-008")

    def test_5b_ledger_missing_entry(self):
        d = self._plant(ledger=lambda es: [e for e in es if e["id"] != "E-009"])
        self._flip(d, "_offline_ledger_findings", lambda *a: [], 1, "未登之句")

    def test_6_prevalue(self):
        d = self._plant(seed_edits=[("44\tp\tR_ADMIN\tuser:edit\t", "44\tp\tR_ADMIN\tuser:ediX\t")])
        self._flip(d, "_offline_prevalue_findings", lambda *a: [], 1,
                   "[offline·前值] m0003_seed_button_governance.rs up 第 2 句（UP_2_DELETE_44）")

    def test_7_empty_comparison_surface(self):
        d = self.enterContext(tempfile.TemporaryDirectory())
        for name in _OFFLINE_FIXTURES:
            rel = os.path.join(FIXTURES_DIR, name)
            _offline_write(d, rel, _offline_edited(self, rel, ()))
        _offline_set_ledger(d, [])
        for name in ("lib.rs", "m0001_baseline_schema.rs", "m0002_baseline_seeds.rs"):
            _offline_write(d, os.path.join(OFFLINE_MIGRATION_DIR, name), "")
        self._flip(d, "_offline_assert_nonempty", lambda paths, root: None, 2, "比對面為空")

    def test_8_prior_pairing_synthesis(self):
        """T007 ⑥b 之紅變體（後序 m0004 樣本改選單 78、WHERE 取凍結值）：停用＝前值左源恆取純凍結 seed → 判綠。"""
        entry = {"id": "E-012", "knife": "001-schema-baseline", "kind": "seed_update", "table": "sys_menu",
                 "detail": {"pk": {"id": 78}, "set": {"buttons": _OFFLINE_MENU_78_NEXT}}, "date": "2026-10-23"}
        sql = (f"UPDATE sys_menu SET buttons = '{_OFFLINE_MENU_78_NEXT}'::jsonb "
               f"WHERE id = 78 AND buttons = '{_M0003_MENU_78_BEFORE}'::jsonb")
        d = self._m0004(rs_edits=[
            _OFFLINE_M0004_MENU_78,
            ("const UP_10_SETVAL: &str", f"const UP_8B_MENU_78: &str = r#\"{sql}\"#;\n\nconst UP_10_SETVAL: &str")],
            more_entries=[entry])
        self._flip(d, "_offline_advance_left", lambda left, entry: left, 1,
                   "[offline·前值] m0004_reaper_role_sample.rs up 第 10 句（UP_8B_MENU_78）")


class TestConstantsPinned(unittest.TestCase):
    """治理常數字面釘死（慣例承 entity-drift-gate TestGovernanceConstantsPinned）：常數縮水＝斷言跟縮
    的套套邏輯在此擋。"""

    def test_offline_role_options_pinned(self):
        self.assertEqual(_OFFLINE_ROLE_OPTIONS, frozenset({
            "NOLOGIN", "NOSUPERUSER", "NOCREATEDB", "NOCREATEROLE", "NOREPLICATION", "NOBYPASSRLS",
            "INHERIT", "NOINHERIT"}))

    def test_rust_punct_pinned(self):
        """判準①n 之標點白名單逐字釘死（Rust 標點字元全集；縮員＝合法標點誤紅、擴員＝白名單外字元照標點切而假綠）。"""
        self.assertEqual(_RUST_PUNCT, "+-*/%^!&|=<>@.,;:#$?~()[]{}")

    def test_kinds_exactly_eight(self):
        self.assertEqual(KINDS, ("add_table", "add_column", "alter_column",
                                 "add_index", "add_constraint",
                                 "seed_add", "seed_update", "seed_delete"))

    def test_labels_four(self):
        self.assertEqual(LABELS, ("A 業務全六欄", "B append-only",
                                  "C join·狀態機", "D 治理"))

    def test_created_by_nn_four(self):
        self.assertEqual(CREATED_BY_NN, ("sys_access_log", "sys_token",
                                         "sys_pwd_custody", "sys_user_email_verify"))

    def test_detail_keys_and_audit_b_pinned(self):
        """rev5:B-006／rev5:B-012 治理常數逐字釘死——TestDetailKeyTable 樣本與豁免出口皆由其派生，
        縮水即套套邏輯（實證：DETAIL_KEYS 縮鍵後 _assert_detail 逸出裸 KeyError 回 rc 1
        形而 85 案全綠）；AUDIT_B_EXEMPT 每筆形制機器強制（(表,欄) tuple＋非空理由）。"""
        self.assertEqual(DETAIL_KEYS, {
            "add_table": ("columns",),
            "add_column": ("column", "type", "nullable"),
            "alter_column": ("column",),
            "add_index": ("name", "definition"),
            "add_constraint": ("name", "definition"),
            "seed_add": ("pk", "values"),
            "seed_update": ("pk", "set"),
            "seed_delete": ("pk",),
        })
        self.assertEqual(AUDIT_B_FORBIDDEN_PREFIXES, ("updated_", "deleted_"))
        self.assertEqual(AUDIT_B_EXEMPT, {})   # Day-1 空集；加列＝同 commit 改本案＋附理由
        for key, reason in AUDIT_B_EXEMPT.items():
            self.assertIsInstance(key, tuple)
            self.assertEqual(len(key), 2)
            self.assertTrue(all(isinstance(x, str) and x for x in key))
            self.assertTrue(isinstance(reason, str) and reason.strip())

    def test_time_constants_pinned(self):
        """ADR-00059／ADR-00060 治理常數釘死：時區查詢字面、期望值、時區來源查詢字面與連線端來源集；
        date 登記名冊現為空集——
        加列＝引入該 date 欄之刀同 commit 改本案＋附 spec 出處；每筆形制機器強制
        （(表, 欄) tuple＋非空出處字串）。"""
        self.assertEqual(SQL_TIMEZONE, "SHOW timezone")
        self.assertEqual(EXPECTED_TIMEZONE, "UTC")
        self.assertEqual(SQL_TIMEZONE_SOURCE,
                         "SELECT source FROM pg_settings WHERE name = 'TimeZone'")
        self.assertEqual(CLIENT_TIMEZONE_SOURCES, ("client", "session"))
        self.assertEqual(DATE_COLUMNS_REGISTERED, {})
        for key, source in DATE_COLUMNS_REGISTERED.items():
            self.assertIsInstance(key, tuple)
            self.assertEqual(len(key), 2)
            self.assertTrue(all(isinstance(x, str) and x for x in key))
            self.assertTrue(isinstance(source, str) and source.strip())

    def test_runtime_append_tables_pinned(self):
        """rev5:B-065 收窄集字面釘死（表→sequence 名、自 fixtures/seed.sql setval 行讀出）；
        擴集＝同 commit 改本案＋常數註解射程論證——防常數縮水後六臂自測跟縮的套套
        邏輯，並釘 sys_user_role 永不入集（有 seed 列的 join 表、收窄＝弱化真 seed 面）。
        ★rev5:004-ip-trust-anchor T037：sys_operation_log 入集（該刀 spec FR-042 排定；rev6 承襲）。
        ★ADR-00100 決定 8：sys_access_log 入集（存取日誌每筆已登入請求一列＝runtime 寫入、seed 恆零列；
        論證形同 sys_operation_log 入集）。
        ★同案釘死 sys_ip_rule **永不入集**——它是變體 A 業務表、列內容即真 seed 面
        （zero-seed 亦是宣告）；誤加進收窄集時本案當場紅，這正是該誤加唯一的機器守
        （收窄之後 gate2 對該表的資料列全無感，錯誤本身零徵狀）。"""
        self.assertEqual(RUNTIME_APPEND_TABLES, {
            "session_event": "session_event_id_seq",
            "sys_access_log": "sys_access_log_id_seq",
            "sys_login_attempt": "sys_login_attempt_id_seq",
            "sys_operation_log": "sys_operation_log_id_seq",
            "sys_token": "sys_token_id_seq"})
        self.assertNotIn("sys_user_role", RUNTIME_APPEND_TABLES)
        self.assertNotIn("sys_ip_rule", RUNTIME_APPEND_TABLES)

    def test_runtime_append_seq_names_ledgered(self):
        """rev5:B-065 值欄（sequence 名）機器對賬：鍵欄（表名）有「seed 必空」斷言自動守門，
        值欄作用面（setval 佔位）與其獨立——擴集手抄錯名（如 sys_token→
        sys_ip_rule_id_seq）＝**非收窄表**的 setval 落值守門靜默弱化（誤配線版對
        rev5:L-015 之「刪列救不回 setval」形照綠、rev5 已離線實證），而字面 pin 測擴集者本來就要
        改、改完照樣綠。左源＝凍結 columns.json 之 nextval default（11 表精確歸屬）；
        另斷言值欄無重複（兩表同 sequence＝其一必錯）。"""
        cols = load_fixtures(REPO_ROOT)["columns"]
        for t, seq in RUNTIME_APPEND_TABLES.items():
            want = f"nextval('{seq}'::regclass)"
            self.assertTrue(
                any(c["table"] == t and want in (c["default"] or "") for c in cols),
                msg=f"RUNTIME_APPEND_TABLES 值欄對賬敗：凍結 columns.json 無"
                    f"「table={t} 且 default 含 {want}」之欄——sequence 名 {seq} "
                    f"非表 {t} 所屬（手抄錯名＝非收窄表 setval 守門靜默弱化）")
        vals = list(RUNTIME_APPEND_TABLES.values())
        self.assertEqual(len(vals), len(set(vals)),
                         msg=f"RUNTIME_APPEND_TABLES 值欄重複：{sorted(vals)}")

    def test_paths_are_rev6_001_coordinates(self):
        """rev6 座標釘死：**凍結面**（fixtures）指 specs/001-schema-baseline＝該刀當下史料；
        **跨刀活體**（定稿左源／登記檔／歸屬帳）一律指 docs/ops/reference-src（BL-00022 抽取模式）。
        工具零 rev5 專屬 seed 決策 json 依賴（名冊自凍結 seed 取）。"""
        self.assertIn("001-schema-baseline", FIXTURES_DIR)
        for p in (DATA_MODEL, LEDGER, ARCHETYPE_MAP):
            self.assertTrue(p.startswith(os.path.join("docs", "ops", "reference-src")), p)
        self.assertTrue(DATA_MODEL.endswith("schema-definition.md"), DATA_MODEL)


class TestUsage(unittest.TestCase):
    def test_no_args_exit64(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["schema-gate.py"]), 64)

    def test_unknown_subcommand_exit64(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["schema-gate.py", "gate1"]), 64)

    def test_check_unknown_flag_exit64(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["schema-gate.py", "check", "--bogus"]), 64)

    def test_check_flag_missing_value_exit64(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["schema-gate.py", "check", "--container"]), 64)

    def test_doccheck_extra_arg_exit64(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["schema-gate.py", "doccheck", "x"]), 64)

    def test_offline_extra_arg_exit64(self):
        """offline 不收引數（T007 ⑫）：多引數＝64，且訊息出自 offline 分派（非「未知子命令」之 64）。"""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(main(["schema-gate.py", "offline", "x"]), 64)
        self.assertIn("offline 不收引數", err.getvalue())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def usage(msg=None):
    if msg:
        print(msg, file=sys.stderr)
    print(__doc__, file=sys.stderr)
    return 64


def main(argv):
    if len(argv) < 2:
        return usage()
    cmd = argv[1]
    if cmd == "test":
        result = unittest.main(argv=[argv[0]], exit=False, verbosity=1).result
        return 0 if result.wasSuccessful() else 1
    if cmd == "doccheck":
        if len(argv) > 2:
            return usage(f"doccheck 不收引數（得 {argv[2:]}）")
        return cmd_doccheck()
    if cmd == "offline":
        if len(argv) > 2:
            return usage(f"offline 不收引數（得 {argv[2:]}）")
        return cmd_offline()
    if cmd == "check":
        container, user, db = None, DB_USER, DB_NAME
        args = argv[2:]
        i = 0
        while i < len(args):
            flag = args[i]
            if flag not in ("--container", "--user", "--db"):
                return usage(f"未知旗標：{flag}")
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                return usage(f"旗標 {flag} 缺值")
            val = args[i + 1]
            if flag == "--container":
                container = val
            elif flag == "--user":
                user = val
            else:
                db = val
            i += 2
        return cmd_check(container=container, user=user, db=db)
    return usage(f"未知子命令：{cmd}")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
