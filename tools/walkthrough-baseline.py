#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/walkthrough-baseline.py — CDP 真登入走查前後的全表基準對賬（rev5:B-147；rev5:L-071 防法①的機制化）

子命令：
  snapshot <檔>   取 rev6 dev stack 實庫＋redis 現況三面＋角色／選單／使用者域與遷移帳六欄、寫成 JSON 基準檔（走查**前**跑；
                  五表上界高於其序列位置＝stderr 告警〔以之 restore 將拒跑〕；現庫遷移帳≠repo migration 清單〔或該清單解析
                  失敗〕＝stderr 告警〔未套用者於下次 stack 起動由一次性 migrate 服務套用、本基準隨即被 restore 之遷移帳前置拒用〕
                  ——兩者 rc 仍 0：快照只讀庫況、不因 repo 面而失效。見 restore 安全帶與 (a)）
  diff <檔>       重取現況、與基準檔逐值比對（含六欄：上界差、鍵集差逐對、授權列／角色列／使用者列上界以內逐列逐欄、遷移帳逐
                  版本兩向差；★使用者列之 password 欄只報「不等」、兩值以遮蔽字面呈現、不印雜湊原文）、只列有差者＋末行摘要
                  （走查**後**清理完跑；
                  ★rc 0 才算「環境已還原」——三閘綠不算，rev5:L-055／rev5:L-071 招牌徵狀＝三閘綠而全量紅）
                  ★序列面例外一項：runtime-append 五表（RUNTIME_APPEND_TABLES、與 tools/schema-gate.py 同名常數同值）
                    之 id 序列只比**存在性**、不比值——同 gate2 對其 setval 值正規化之口徑；這五支只進不退
                    （rust-api 測試守衛只清自寫列、序列不復位），逐值比則每跑一次全量測試 diff 即恆有差
  restore <檔>    走查後清理（RUNBOOK §9c 第 3 步之順序機器化；寫面恰為下列、次序固定）：
                  (a)遷移帳前置：結構安全帶之後、門鈴清前計數／①比對／⑥重啟句判準之現讀與一切寫入之前，以單句現讀
                    seaql_migrations、與基準檔 migrations 比——不等＝拒跑 rc 2、零寫入、逐版本指名「基準有現庫無」／「現庫有
                    基準無」並指示補救（走查尚未開始＝重新 snapshot；走查已發生而無同遷移狀態之基準＝改跑 restore --seed）：以遷移
                    前後不同之基準照跑＝反做該遷移之增刪列而不還原其欄值改動、遷移帳仍記已跑＝無工具修路之混合態
                  (b)repo↔現庫遷移同步前置（兩模式；(a) 之後、同在上列現讀與一切寫入之前）：合成射程（見下「演進合成」）之表於
                    演進帳有 seed_* 登記時才驗——repo migration 清單（見下；不可解＝拒跑 rc 2）須恰等現庫遷移帳（基準檔模式沿用
                    (a) 之現讀、seed 模式單句現讀）；不等＝拒跑 rc 2、零寫入、指名「repo 有現庫無＝未套用」／「現庫有 repo 無」之
                    遷移與觸發之登記 id 並附補救（重起 stack 由一次性 migrate 服務套用〔dev 庫寫入、需放行〕／工作樹切回含該遷移之
                    分支）：期望 seed 依 repo 之演進帳合成、庫況未同步即合成目標不可用；無涉表登記＝不驗
                  ①system_settings 對期望 seed（左源＝凍結 seed〔specs/001-schema-baseline/fixtures/seed.sql 之 COPY 段〕⊕ 演進
                    登記合成、見下「演進合成」）——值≠期望（含鍵缺／鍵多）即 fail-loud 指名、**不自動改值**（值還原走 002 刀
                    寫端＝人工前置）；值＝期望而審計欄 updated_at／updated_by 非 NULL 者歸 NULL（改回值≠改回痕）
                  ②DELETE 清理面七表（RESTORE_TABLES＝會話三表＋sys_ip_rule＋sys_operation_log＋sys_pwd_custody＋sys_access_log）全表
                    ＋sys_user.session_id 歸 NULL
                  ③六支 setval（RESTORE_SEQUENCES＝清理面有 id 序列之六表之序列；sys_pwd_custody 無序列）值自基準檔現讀
                  ③b角色／選單／使用者域寫面（接在③之後）：sys_user_role 以目標鍵集差刪除（現況有而目標無之對；其 user_id／
                    role_id 外鍵 ON DELETE RESTRICT 指 sys_user／sys_role、故先於上界刪除）→ BOUNDED_TABLES 五表（sys_role／
                    sys_menu／casbin_rule／sys_casbin_policy_archive／sys_user；sys_user 居末、其餘次序取名冊序）刪 id > 目標上界之
                    列 → casbin_rule 回補目標列（原 id 原值全欄、ON CONFLICT DO NOTHING＝只補目標有而現況無之列；★排在刪上界列之後
                    ——走查復原以新 id 回插同身分列時、先補則被身分鍵吞掉而新列隨後被刪＝該列永久缺席）→ sys_user_role 回補目標鍵集
                    （ON CONFLICT DO NOTHING＝只補目標有而現況無之對；★排在一切刪除之後——外鍵 RESTRICT）→ sys_role 可變欄與目標
                    不等之列回寫目標值（含審計欄 updated_at／updated_by：改回值≠改回痕）→ sys_user 可變欄與目標不等之列回寫目標值
                    （含密碼雜湊、審計欄與軟刪兩欄：基準內帳號被軟刪＝寫回未刪、其指派隨上一步回補）→ 五支序列 setval 回目標值；
                    目標＝基準檔六欄與序列面現讀值。★seed 有列＝不 DELETE 全表、不套列數安全帶（改守上界對序列之前置、見安全帶）；
                    ★射程界＝補回被刪之授權列與指派對、回寫角色列與使用者列可變欄；其餘欄之就地改寫（含 sys_role.role_code、
                    sys_user.user_name 與兩表建立欄）與他表 id ≤ 上界列之被刪（含歸檔表界下列被復原消費）restore 皆不還原：列數與
                    逐欄差由收尾比對報出、seed 列欄值另由 tools/schema-gate.py check 之 gate2 逐列兜；上界本身被取樣時之顯式 id
                    殘列抬高者＝該前置拒跑、不在射程內硬做
                    ——①～③b 同一交易（BEGIN…COMMIT、ON_ERROR_STOP=1；任一句敗即整筆回滾、不進④；失敗之 psql 錯誤文轉述前剔除
                    SQL 回顯行、遮蔽失敗列值與密碼欄值）
                  ④b門鈴（BL-00094；交易提交後、④之前）：清前 sys_ip_rule 列數非 0＝PUBLISH ipgate:invalidate 一次並
                    回報訂閱者數；回非整數＝拋錯並附可照抄之人工按鈴命令（doorbell_cli）；清前 0 列＝不按
                  ④redis 以 `--scan --pattern` 取 session:*／throttle:*／cpwd:* 鍵、逐鍵指名 DEL（每批 ≤REDIS_DEL_BATCH
                    把；絕不 FLUSHDB、絕不以樣式刪）
                  ⑤收尾自動跑一次 diff、其 rc 即 restore 之 rc（0＝已還原）
                  ⑥重啟句：③b 實際刪過 casbin_rule 列、改過其序列或將回補 ≥1 列（交易前以 SQL_CASBIN_STATE 現讀判）＝收尾輸出
                    CASBIN_RESTART_HINT（MUST 重啟 rust-api、附可照抄之 compose restart 命令；判定面無外部通知管道）
                    ——提交後任一步失敗之路徑亦輸出；未動 casbin 者不輸出（sys_role、sys_user 回寫與指派回補不需重啟：角色成員與
                    首頁每請求自庫讀、帳號活性於登入與換發自庫讀）
                  ★安全帶：基準檔清理面七表列數或 session／throttle／cpwd 前綴鍵數非 0＝拒絕執行 rc 2、零寫入（DELETE 全表
                    會毀掉基準資料——restore 只服務「走查前為空基準」之形；無空基準檔可用＝改跑 seed 模式）；角色／選單／使用者域
                    六表不套（其寫面不毀目標態之列）、改守前置：基準檔五表任一之上界高於其序列位置（nextval 已發出之最大值：
                    is_called 真＝last_value、假＝last_value-1）＝拒跑 rc 2、零寫入——取樣時已有顯式 id 殘列越過序列、走查以
                    nextval 造之列落在序列與上界之間＝刪不到、序列卻被 setval 回其下＝下一次 nextval 撞 PK（補救＝seed 模式；
                    snapshot 遇同條件即告警）；安全帶、(a)、(b)、讀帳與演進合成、seed 比對與重啟句判準之現讀皆在任何寫入之前
  restore --seed  同上清理、但無須基準檔：目標態＝凍結 seed ⊕ 演進合成（合成射程＝system_settings＋角色／選單／使用者域六表；
                  BL-00075；走查外殘列——被殺測試留下之列與鍵——產生時通常無空基準 snapshot 可用；無基準檔＝無 (a) 遷移帳
                  前置、(b) 照驗）。與基準檔模式之差恰三處：
                  (甲)安全帶改對合成目標：清理面七表之 COPY 段須在場且零列、六支序列之 setval 行須在場；角色／選單／使用者域
                    六表之 COPY 段與五支序列之 setval 行須在場（不論列數；段首缺欄、列欄數不符、id 非整數、授權列／角色列／使用者列
                    之值不合欄型＝凍結面受損；含遮蔽欄之表其錯誤訊息只引段內列序、不引列文）；
                    演進帳拒跑判定只剩清理面七表（有其 seed_* 登記＝仍拒跑之演進形①、見下）；上界對序列之前置照套、對象改為
                    合成目標（COPY 列 id 最大值高於其 setval 位置＝凍結面受損或合成未推進序號 rc 2；真檔恰相等、自測釘住＝不觸發）
                  (乙)③只 setval sys_ip_rule_id_seq 一支（SEED_SETVAL_SEQUENCES＝清理面序列扣掉 runtime-append 者）、
                    值自合成文字之 setval 行現讀；runtime-append 五支序列**不復位**；③b 目標＝合成目標：五表上界＝合成後
                    COPY 列 id 最大值（零列記 0）、五支 setval 值＝合成後 setval 行（seed_add 新列推進者隨之）、指派鍵集＝COPY
                    鍵集、授權列＝casbin_rule COPY 全欄列、角色列與使用者列可變欄＝sys_role／sys_user COPY 之可變欄（同經
                    _seed_copy_rows 取段、依欄型轉型）
                  (丙)⑤收尾比對之判準面＝清理面與角色／選單／使用者域對合成目標值（清理面七表 0 列、sys_ip_rule_id_seq＝seed 值、
                    runtime-append 序列在場、三前綴 0 鍵；該域六表列數、五表上界與序列、指派鍵集、授權列／角色列／使用者列
                    可變欄）；其餘面（含遷移帳）無基準
                    可比＝不判——pg 殘留由 tools/schema-gate.py check 之 gate2 逐列兜
  test            自帶 self-test（unittest、離線、零 docker；subprocess 全樁）
  選項（snapshot／diff／restore 共用）：`--user U`／`--db D`（預設同 tools/schema-gate.py 常數）。
  `<檔>` 為必填位置引數、無隱含預設落點（契約用法落 tmp/、見 RUNBOOK §9c）；唯 restore 得以 `--seed` 取代之
  （兩者擇一、並帶＝用法錯 rc 64）。

三面（★全部現算、零手抄名冊——清單式防法已被 rev5:L-071 證偽：rev5:006 的清單擋不住 rev5:007 的組合）：
  ①表：public schema **全部**表的列數（表清單自 information_schema.tables 現算、逐表 count(*)
    以單一 UNION ALL 一次撈；含 seaql_migrations——它也是一張表、不豁免）
  ②序列：public schema **全部**序列的 last_value＋is_called（清單自 pg_class relkind='S' 現算）
  ③redis：DBSIZE 總數＋逐前綴鍵數（`--scan` 全鍵**去重後**分組——SCAN 只保證「至少一次」；
    DBSIZE 與去重鍵數互證、不等出提示；前綴＝鍵第一個冒號前段、無冒號者歸「(無前綴)」；
    前綴名冊亦不手抄——rust-api 現行之鍵前綴只是今天的值）
  基準檔另帶 taken_at（UTC ISO）與 schema_version（檔形演進用）；diff 忽略 taken_at。
  另帶角色／選單／使用者域與遷移帳六欄（檔形 v4；restore ③b 之目標值與 (a) 之比對左源、非比對面之名冊式防法——全表列數仍由①
  現算；六欄同一句撈取＝同一快照）：id_bounds＝BOUNDED_TABLES 五表之 max(id)（空表記 0）、user_role_keys＝sys_user_role 之
    [user_id, role_id] 有序清單、casbin_rule_rows＝casbin_rule 之 id ≤ 上界全欄列、sys_role_rows＝sys_role 之 id ≤ 上界列之
    id＋可變欄、sys_user_rows＝sys_user 之 id ≤ 上界列之 id＋可變欄（暱稱、性別、手機、信箱、狀態、會話政策、記事、密碼雜湊、
    審計欄與軟刪兩欄；user_name、建立兩欄與 session_id 不在面內——不可變／不經寫端改／清理句全域歸 NULL）、migrations＝
    seaql_migrations.version 依名排序之清單（非空、互異；空＝比對面為空 rc 2）；列面之欄名冊與欄型＝ROW_FACES（射程刻意取
    「取樣時已在之列」＝seed 列之超集、不另立 seed 識別條件；時間欄存正規形）；diff 亦比六欄。
    v3／v2／v1 基準檔（缺欄；v3 以前之舊檔形不載遷移帳、無從判遷移差）diff／restore 皆 rc 2 指名重新 snapshot。
    ★基準檔含 seed 帳號密碼雜湊＝只落 gitignored 工作區（RUNBOOK §9c 落點）；本工具任何輸出（diff、錯誤訊息）一律不印雜湊與其
    片段、長度（遮蔽名冊＝MASKED_COLUMNS）。
  repo migration 清單（repo_migrations；snapshot 告警之料源、restore 前置共用）＝`rust-api/migration/src/lib.rs` 之 migrations()
    向量內 Box::new(<模組>::Migration) 依序之模組名（＝DeriveMigrationName 取之 seaql_migrations.version）；單行與 rustfmt 折行兩形
    皆解、各須有 mod 宣告與同名 .rs 實檔；零命中或不一致＝rc 2（snapshot 下降為告警）。

演進合成（synthesize_seed；兩模式 restore 之 seed 左源、ADR-00085 決定 9 (b)）：期望 seed＝凍結 seed ⊕ 演進帳
  （docs/ops/reference-src/schema-evolution.json）中合成射程各表之登記——執行期依路徑載入 tools/schema-gate.py、取 gate2 期望 seed
  之同一合成鏈（normalize_seed_dump → apply_seed_entries：seed_add 全欄附列並推進該表序號期望行〔新 id 高於已發最大值才推、只進
  不退〕、seed_update／seed_delete 以 pk 恰命中一列改或刪、add_column 之 nullable 無 default 形補欄），再以 seed_restore_target／
  seed_settings 讀合成文字——本工具不自持第二份合成；載入失敗或 GateError＝rc 2、原訊息照轉。合成射程：基準檔模式＝
  system_settings（SYNTH_TABLES_BASELINE；其餘目標態取基準檔）；seed 模式＝其＋角色／選單／使用者域六表（SYNTH_TABLES_SEED）。
  射程外之表之登記（含未內建之 add_table）不餵、不擋。
  ★射程界：seed_* 演進（清理面各表除外）由合成承接、不須再擴本工具。仍拒跑之演進形恰兩種：①清理面各表（會話三表、IP 規則、
    操作紀錄、經手表、存取日誌）之 seed_* 登記——seed 模式 rc 2 指名登記 id（整表清空以 seed 恆零列為前提；基準檔模式由清理面須零列之
    安全帶承擔同一邊界）②合成面表之結構演進屬 schema 閘合成未內建之形（add_column 帶 default 或 NOT NULL）——與 gate2 同
    rc 2、於 tools/schema-gate.py 同一擴充點補齊即兩工具同時恢復。其餘拒跑屬前置不符（(a) 基準檔遷移帳≠現庫、(b) repo↔現庫
    遷移不同步）：重拍基準或套遷移即解；其餘結構類演進不使本工具拒跑（以欄名取值、新欄不入回寫射程、新表不入清理面）。

退出碼：0 全等／1 有差／2 環境或結構異常（docker 不可執行、psql／redis 失敗、基準檔缺席或壞形、
★比對面為空＝零表或零序列——空面的全綠是假綠、同 schema-gate 紀律，snapshot 與 diff 皆然；restore 另含
安全帶拒跑（含目標態五表上界高於其序列位置）、基準檔遷移帳≠現庫（(a)；含現庫遷移帳撈取壞形）、合成射程有 seed_* 登記而 repo
migration 清單≠現庫遷移帳或該清單不可解（(b)）、基準檔缺清理面之表或序列、seed 左源缺席或不可解、演進登記檔缺席或壞形、演進合成鏈
載入失敗或合成失敗（GateError：pk 命中≠1、values 欄集不符、未內建之結構演進形等）、system_settings 值≠期望 seed、casbin_rule 現態
撈取壞形；seed 模式另含凍結 seed 缺清理面或角色／選單／使用者域之 COPY 段或 setval 行、該面 COPY 段受損、清理面七表有 seed_* 演進
登記；基準檔壞形含 v3／v2／v1 舊檔形）／64 用法錯（usage 走 stderr）。restore 之 0／1 即其收尾 diff 之 rc。

唯讀紀律（self-test 逐字釘住）：snapshot／diff 唯讀——pg 只下 SELECT（含目錄視圖）、redis 只下 DBSIZE／--scan；
restore 之寫面恰為上列①～④（含④b；交易句逐字、redis 只 PUBLISH 門鈴與 DEL 指名鍵），其餘撈取同唯讀判準；
pg 走 `docker compose … exec -T postgres psql -U … -d … -At -F <分隔>`；redis 走
`exec -T redis sh -c` 以 `$(cat /run/secrets/redis_password)` 取密（同 compose healthcheck 形、
`--no-auth-warning`）——密碼值只在容器內 sh 展開，host argv 與本工具任何輸出皆不含。
★只准指向 rev6 dev stack（compose 專案＝倉庫根、埠 3xxxx）；絕不指向 rev5 對照 stack（2xxxx）。

出處：rev5:B-147 候選①；rev5:L-071 防法①（走查前取全表基準、後逐值比對——不變式取代清單）＋②（清理面
的定義＝走查期間被寫過的一切、與任何閘的射程無關）；rev5:L-055（runtime-append 殘列兩條爆線）。
入冊（rev6 登記面）：tools/docsync/gates.py 之 NON_GATE_TOOLS（非碼面閘、GT-12 腿對賬）＋pre-commit
`for t in …` 自測名冊＋bootstrap run_tool_test 名冊＋README 樹＋RUNBOOK §12 工具鏈速查；★不掛 pre-commit
條件觸發（要 dev stack、且走查收尾才有意義）——走查前後手動跑。stdlib-only（rev5:ADR 0010）；連字檔名＝CLI、
不可 import。隨遷自 rev5:tools/walkthrough-baseline.py（003 刀 U10a；四型失效引用 rev6 化、其餘逐字承襲）。
restore 子命令＝BL-00053（maint-backlog-pre-004 A2b 新增、rev5 無對應）：取代 003 刀 U6／U7／U11 各自手寫之 tmp
清理腳本；寫面由 self-test 逐字釘住（多一句即紅）。清理面擴及 sys_ip_rule／sys_operation_log、seed 模式、
runtime-append 序列存在性口徑＝BL-00075（004 刀 U3；rev5 同名工具無此三項）。角色／選單域寫面（③b）、上界與鍵集
兩欄與重啟句（⑥）＝005 刀 U15（T088；rev5 同名工具無此面、無藍本）；授權列回補與角色列回寫（③b 擴面）、檔形 v3 兩欄與重啟句
回補腿＝006 刀 U15（T072；同無藍本）；檔形 v4（遷移帳與使用者列兩欄、sys_user 入上界面）、(a) 遷移帳前置、repo migration 清單解析、
使用者域寫面（指派回補、使用者列回寫）、清理面擴經手表與 cpwd 前綴、password 遮蔽、演進合成（schema-gate 同一合成鏈；兩模式 seed 左源與
seed 模式目標態）與 (b) repo↔現庫遷移同步前置＝007 刀 U1（T005～T007；同無藍本）。runtime-append 名冊與清理面擴
sys_access_log（清理面七表、六支序列）＝008 刀 U1（ADR-00100 決定 8；同無藍本）。
"""
import contextlib
import copy
import datetime
import importlib.util
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DB 身分：與 tools/schema-gate.py 之 DB_USER／DB_NAME **同值**（連字檔名 CLI 不可 import、故自帶；
# 兩處若分歧，本工具會對著不存在的庫報 rc 2、不會靜默比錯庫）。
DB_USER = "soybean"
DB_NAME = "soybean_admin_rust"
# compose 前綴同 schema-gate 形（兩個 -f 缺一即讀不到 dev 覆寫）；`-T` 必帶（非 tty、hook／管道可跑）。
COMPOSE_EXEC = ["docker", "compose", "-f", "docker-compose.yml",
                "-f", "docker-compose.dev.yml", "exec", "-T"]
PG_SERVICE = "postgres"
REDIS_SERVICE = "redis"
REDIS_PASSWORD_FILE = "/run/secrets/redis_password"
# ★密碼只在容器內 sh 展開（同 docker-compose.yml redis healthcheck 形）；host 端只見這行字面。
REDIS_CLI = f'redis-cli -a "$(cat {REDIS_PASSWORD_FILE})" --no-auth-warning'
PSQL_SEP = "\t"          # psql -F 分隔（表名／序列名不含 tab）
SCHEMA_VERSION = 4       # 基準檔形版本；改檔形即 bump、舊檔 diff／restore 走 rc 2 而非誤比（v2＝005 刀 U15 加上界與鍵集兩欄、
                         # v3＝006 刀 U15 加授權列與角色列兩欄、v4＝007 刀 U1 加遷移帳與使用者列兩欄並擴 sys_user 上界）
NO_PREFIX = "(無前綴)"
STARTUP_HINT = ("docker compose -f docker-compose.yml -f docker-compose.dev.yml "
                "up -d --wait postgres redis")

RC_OK, RC_DIFF, RC_ENV, RC_USAGE = 0, 1, 2, 64
PROG = "tools/walkthrough-baseline.py"

SQL_TABLES = ("SELECT table_name FROM information_schema.tables "
              "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY 1")
SQL_SEQUENCES = ("SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                 "WHERE c.relkind='S' AND n.nspname='public' ORDER BY 1")

# ── restore 清理面（BL-00053、BL-00075；次序＝RUNBOOK §9c 第 3 步）────────────────
# seed 左源＝凍結 fixture 之 system_settings COPY 段（唯讀、REPO_ROOT 相對）
SEED_FIXTURE = os.path.join("specs", "001-schema-baseline", "fixtures", "seed.sql")
# 演進登記檔（形斷言權威＝tools/schema-gate.py）：期望 seed＝凍結 ⊕ 演進。本工具之 seed 左源＝凍結段經 schema-gate 之同一合成鏈
# 施以合成射程內之登記（synthesize_seed）；清理面七表之 seed_* 登記於 seed 模式拒跑（check_seed_evolution：整表清空以 seed 恆零列為前提）
SCHEMA_EVOLUTION = os.path.join("docs", "ops", "reference-src", "schema-evolution.json")
SEED_EVOLUTION_KINDS = ("seed_add", "seed_update", "seed_delete")
# 合成鏈之單一來源（gate2 期望 seed 之 normalize_seed_dump → apply_seed_entries、seed_add 序號推進含於其內）：連字檔名不可 import、
# 執行期依路徑載入（REPO_ROOT 相對）；本工具不自持第二份 COPY 合成或序號推進——schema 閘之合成一擴充即兩工具同時生效
SCHEMA_GATE = os.path.join("tools", "schema-gate.py")
# runtime-append 五表→其 id 序列：與 tools/schema-gate.py 之 RUNTIME_APPEND_TABLES **同值**（連字檔名 CLI 不可 import、
# 故自帶；自測以 importlib 依路徑載入該檔、對賬兩者逐項相等；sys_access_log 依 ADR-00100 決定 8 入集）。這五支序列只進不退
# ——rust-api 測試守衛只清自寫列、不復位（004 刀 U3 廢序列復位守衛；LL-00017／LL-00022）——故 diff 對其只比存在性、seed 模式
# 亦不 setval。
RUNTIME_APPEND_TABLES = {
    "session_event": "session_event_id_seq",
    "sys_access_log": "sys_access_log_id_seq",
    "sys_login_attempt": "sys_login_attempt_id_seq",
    "sys_operation_log": "sys_operation_log_id_seq",
    "sys_token": "sys_token_id_seq",
}
# 清理面七表（DELETE 全表；次序即語句序）：會話三表＋sys_ip_rule（業務表、zero-seed）＋sys_operation_log＋sys_pwd_custody
# （經手表：seed 零列、無序列＝不入 RESTORE_SEQUENCES）＋sys_access_log（無外鍵、seed 零列＝整表清空前提成立；置尾＝既有語句序
# 前綴不動）
RESTORE_TABLES = ("session_event", "sys_token", "sys_login_attempt", "sys_ip_rule", "sys_operation_log", "sys_pwd_custody",
                  "sys_access_log")
# 門鈴（BL-00094）：restore 以 SQL 直清 sys_ip_rule、不經規則寫端⇒執行中的 rust-api 判定面仍持舊規則集。
# 清前列數非 0 時自動補按；★payload 不帶語意、收訊端只認頻道（rust-api `ipgate::IPGATE_INVALIDATE_CHANNEL` 之契約）。
IPGATE_CHANNEL = "ipgate:invalidate"
IPGATE_DOORBELL_PAYLOAD = "1"
SQL_IP_RULE_ROWS = 'SELECT json_agg(t) FROM (SELECT count(*) AS n FROM "sys_ip_rule") t'
# 基準檔模式 setval 之序列（清理面有 id 序列之六表、六支皆依基準檔現讀）；seed 模式只 setval 其中非 runtime-append 者
RESTORE_SEQUENCES = ("sys_token_id_seq", "session_event_id_seq", "sys_login_attempt_id_seq",
                     "sys_ip_rule_id_seq", "sys_operation_log_id_seq", "sys_access_log_id_seq")
SEED_SETVAL_SEQUENCES = tuple(s for s in RESTORE_SEQUENCES if s not in RUNTIME_APPEND_TABLES.values())
# redis 清理前綴：會話、節流與改密節流（cpwd＝改密節流桶之獨立前綴）
RESTORE_REDIS_PREFIXES = ("session", "throttle", "cpwd")
# 一次 DEL 指名的鍵數上限：逐鍵指名、分批送（免每把鍵各一次 docker exec；也免 sh -c 參數過長）
REDIS_DEL_BATCH = 100
SQL_SETTINGS = ("SELECT COALESCE(json_agg(t ORDER BY t.setting_key), '[]'::json) FROM "
                "(SELECT setting_key, setting_value, "
                "(updated_at IS NOT NULL OR updated_by IS NOT NULL) AS stamped "
                "FROM system_settings) t")
SQL_RESTORE_AUDIT = ("UPDATE system_settings SET updated_at = NULL, updated_by = NULL "
                     "WHERE updated_at IS NOT NULL OR updated_by IS NOT NULL;")
SQL_RESTORE_CLEAR = tuple(f"DELETE FROM {t};" for t in RESTORE_TABLES) + (
    "UPDATE sys_user SET session_id = NULL WHERE session_id IS NOT NULL;",)

# ── 角色／選單／使用者域寫面（005 刀 U15、T088；007 刀 U1 擴使用者域；restore ③b）──────────────
# id 上界五表→其 id 序列（dict 序即刪除序）：seed 有列（archive 於 seed 零列、同形處置）＝不可 DELETE 全表、不套「基準列數非 0
# 即拒」——restore 只刪 id > 目標上界之列、序列 setval 回目標值；目標上界＝基準檔 id_bounds（max(id)、空表記 0）或凍結 seed 之
# COPY 列 id 最大值（零列記 0）。sys_user 居末：其列被指派表之 user_id 外鍵（ON DELETE RESTRICT）指向、指派先刪。
BOUNDED_TABLES = {
    "sys_role": "sys_role_id_seq",
    "sys_menu": "sys_menu_id_seq",
    "casbin_rule": "casbin_rule_id_seq",
    "sys_casbin_policy_archive": "sys_casbin_policy_archive_id_seq",
    "sys_user": "sys_user_id_seq",
}
# 指派表（複合主鍵 (user_id, role_id)、無 id 與序列）：以鍵集差刪除（現況有而目標無之對）、以目標鍵集回補（目標有而現況無之對）。
# 其 user_id／role_id 外鍵 ON DELETE RESTRICT 指 sys_user／sys_role（全 schema 恰此兩條）⇒ 刪除排在五表之前、回補排在一切刪除之後；
# 五表間之其餘關係無外鍵（005 刀 U15 以 pg_constraint 現查）、次序取名冊序。
USER_ROLE_TABLE = "sys_user_role"
# 角色／選單／使用者域六表（③b 寫面；seed 模式合成射程之一部）
DOMAIN_TABLES = tuple(BOUNDED_TABLES) + (USER_ROLE_TABLE,)
# 合成射程（左源＝凍結 seed ⊕ 射程內之演進登記）：基準檔模式只 system_settings（其餘目標態取基準檔）；seed 模式另含角色／選單／使用者域
# 六表。射程外之表之登記不餵、不擋（各筆只作用於自表 COPY 段與自表序列＝逐表獨立）；射程內有 seed_* 登記＝repo↔現庫遷移同步前置照驗
SYNTH_TABLES_BASELINE = ("system_settings",)
SYNTH_TABLES_SEED = SYNTH_TABLES_BASELINE + DOMAIN_TABLES
# 基準檔 v3／v4 列面（006 刀 U15、T072；007 刀 U1；restore ③b 授權列回補與角色列、使用者列回寫之目標）：欄名→欄型（dict 序＝撈取、寫句與
# seed COPY 取欄之欄序）。欄型：int／text／bool／ts（timestamptz、存正規形＝_canon_ts）；尾綴「?」＝可為 NULL。授權列取全欄（回補＝原 id
# 原值整列）；角色列只取 id＋可變欄（首頁、狀態、名稱、描述、備註與審計欄 updated_at／updated_by——role_code 與建立、刪除兩組欄不在回寫
# 射程）；使用者列只取 id＋可變欄（暱稱、性別、手機、信箱、狀態、會話政策、記事、密碼雜湊、審計欄與軟刪兩欄——user_name 建後不可變、
# 建立兩欄不經寫端改、session_id 由清理句全域歸 NULL，皆不在面內；軟刪兩欄入面＝基準內帳號被軟刪即寫回未刪、其指派隨回補）。
CASBIN_RULE_COLUMNS = {"id": "int", "ptype": "text", "v0": "text", "v1": "text", "v2": "text", "v3": "text",
                       "v4": "text", "v5": "text", "protected": "bool", "created_at": "ts", "created_by": "int?"}
SYS_ROLE_MUTABLE_COLUMNS = {"role_home": "text?", "status": "int?", "role_name": "text", "role_desc": "text?",
                            "role_memo": "text?", "updated_at": "ts?", "updated_by": "int?"}
SYS_USER_MUTABLE_COLUMNS = {"nick_name": "text?", "user_gender": "int?", "user_phone": "text?", "user_email": "text?",
                            "status": "int?", "session_policy": "text", "user_memo": "text?", "password": "text",
                            "updated_at": "ts?", "updated_by": "int?", "deleted_at": "ts?", "deleted_by": "int?"}
# 列面之基準檔鍵 →（表, diff 面名, 欄名冊）；射程＝取樣時該表 id ≤ 上界之全部列（與上界同一句撈取＝同一快照、恆在上界以內）
ROW_FACES = {"casbin_rule_rows": ("casbin_rule", "授權列", CASBIN_RULE_COLUMNS),
             "sys_role_rows": ("sys_role", "角色列", dict({"id": "int"}, **SYS_ROLE_MUTABLE_COLUMNS)),
             "sys_user_rows": ("sys_user", "使用者列", dict({"id": "int"}, **SYS_USER_MUTABLE_COLUMNS))}
# 遮蔽名冊（島 I5 三重不洩延伸至維運工具輸出）：表→欄。diff 只報「不等」、值一律以 MASK 呈現；錯誤訊息不引含此類欄之列文、
# restore 交易失敗之 psql 錯誤文剔除 SQL 回顯與失敗列值——雜湊原文、片段與長度皆不出本工具任何輸出（基準檔本身含雜湊、只落 gitignored
# 工作區）。
MASKED_COLUMNS = {"sys_user": ("password",)}
MASK = "（遮蔽）"
# 遷移帳（v4；seaql_migrations.version＝DeriveMigrationName 取之 migration 檔名主幹）：基準檔欄 migrations 之撈取併入 SQL_BOUND_FACES
# 之單句；SQL_MIGRATIONS＝restore 遷移帳前置之現讀句（同一聚合式）
SQL_MIGRATIONS = "SELECT COALESCE(json_agg(version ORDER BY version), '[]'::json) FROM seaql_migrations"
# repo migration 清單之料源（rust-api 子庫之 migration crate；REPO_ROOT 相對）與模組名形
MIGRATION_LIB = os.path.join("rust-api", "migration", "src", "lib.rs")
_MIGRATION_MODULE = re.compile(r"^m[0-9]{4}_[a-z0-9_]+$")


def _rows_json_sql(table, columns):
    """一表之列 → json 陣列子查詢（欄名即鍵、依 id 排序、空表 '[]'）。"""
    pairs = ", ".join(f"'{c}', {c}" for c in columns)
    return f"(SELECT COALESCE(json_agg(json_build_object({pairs}) ORDER BY id), '[]'::json) FROM {table})"


# 基準檔角色／選單／使用者域與遷移帳六欄之撈取（單句＝同一快照、唯讀）：五表 id 上界＋指派鍵集（依 user_id, role_id 排序）＋授權列、
# 角色列與使用者列三欄＋遷移帳（依名排序）
SQL_BOUND_FACES = (
    "SELECT json_build_object('id_bounds', json_build_object("
    + ", ".join(f"'{t}', (SELECT COALESCE(max(id), 0) FROM {t})" for t in BOUNDED_TABLES)
    + f"), 'user_role_keys', (SELECT COALESCE(json_agg(json_build_array(user_id, role_id) "
      f"ORDER BY user_id, role_id), '[]'::json) FROM {USER_ROLE_TABLE}), "
    + ", ".join(f"'{key}', {_rows_json_sql(t, cols)}" for key, (t, _face, cols) in ROW_FACES.items())
    + ", 'migrations', (" + SQL_MIGRATIONS + "))")
# 重啟句判準之現讀（寫入前、唯讀）：casbin_rule 現況上界、現況 id 集與其序列
SQL_CASBIN_STATE = ("SELECT json_build_object('max_id', (SELECT COALESCE(max(id), 0) FROM casbin_rule), "
                    "'ids', (SELECT COALESCE(json_agg(id ORDER BY id), '[]'::json) FROM casbin_rule), "
                    "'seq', (SELECT json_build_object('last_value', last_value, 'is_called', is_called) "
                    "FROM casbin_rule_id_seq))")
# 重啟句（restore 實際刪過 casbin_rule 列、改過其序列或將回補其列時收尾輸出；self-test 逐字釘住）：判定面只在 rust-api 開機與
# 自身寫端同步時自庫載入、SQL 直改無外部通知管道。
RUST_API_RESTART_CLI = "docker compose -f docker-compose.yml -f docker-compose.dev.yml restart rust-api"
CASBIN_RESTART_HINT = ("[walkthrough-baseline] ★MUST 重啟 rust-api：本次 restore 以 SQL 直改 casbin_rule（刪列、回補列或改序列）、"
                       "判定面無外部通知管道——執行中的 rust-api 仍持 restore 前之政策集、重啟即自庫重載；照抄："
                       + RUST_API_RESTART_CLI)


class BaselineError(Exception):
    """環境或結構異常（docker 不可執行、psql／redis 失敗、基準檔缺席或壞形、比對面為空）→ rc 2。"""


def _say(msg, err=False):
    """單一輸出咽喉：每行即時 flush（接管道時塊緩衝會讓輸出錯序；同 rust-fmt-gate 慣例）。"""
    print(msg, file=sys.stderr if err else sys.stdout, flush=True)


# ── 外部呼叫（唯讀）──────────────────────────────────────────────────────────

def _run_docker(argv, run):
    """docker 子行程統一入口：docker 執行不起來（OSError）＝環境異常 rc 2、附啟動命令。"""
    try:
        return run(argv, capture_output=True, text=True, cwd=REPO_ROOT)
    except OSError as ex:
        raise BaselineError(f"無法執行 docker（{ex}）——本工具需 rev6 dev stack 在跑；"
                            f"啟動：{STARTUP_HINT}") from None


def psql_argv(sql, user=DB_USER, db=DB_NAME):
    """psql 唯讀撈取的 argv（`-At` 無表頭純值、`-F` 指定欄分隔、ON_ERROR_STOP 讓 SQL 錯即非零）。"""
    return COMPOSE_EXEC + [PG_SERVICE, "psql", "-U", user, "-d", db, "-At", "-F", PSQL_SEP,
                          "-v", "ON_ERROR_STOP=1", "-c", sql]


def psql_rows(sql, user, db, run):
    """跑一句 SELECT → 列表（每列＝依 PSQL_SEP 切欄的 list）；psql 非零＝rc 2。"""
    r = _run_docker(psql_argv(sql, user, db), run)
    if r.returncode != 0:
        raise BaselineError(f"psql 失敗（rc={r.returncode}）：{(r.stderr or '').strip()[:300]}"
                            f"——補救：dev stack 未起→{STARTUP_HINT}")
    return [ln.split(PSQL_SEP) for ln in (r.stdout or "").splitlines() if ln.strip()]


def redis_argv(command):
    """redis-cli 讀命令的 argv：`exec -T redis sh -c '<REDIS_CLI> <command>'`——密碼由容器內 sh 取。"""
    return COMPOSE_EXEC + [REDIS_SERVICE, "sh", "-c", f"{REDIS_CLI} {command}"]


def redis_out(command, run):
    """跑一個 redis 命令 → stdout 原文；非零＝rc 2。★射程含 restore 的三種寫命令（DEL 與 ④b 門鈴之
    PUBLISH）——唯讀判準由 `_redis_write_offenders` 逐命令判，不由本函式名擔保。"""
    r = _run_docker(redis_argv(command), run)
    if r.returncode != 0:
        raise BaselineError(f"redis-cli 失敗（rc={r.returncode}）："
                            f"{(r.stderr or '').strip()[:300]}——補救：dev stack 未起→{STARTUP_HINT}")
    return r.stdout or ""


def _ident(name):
    """雙引號識別字（表名／序列名來自目錄、仍照規矩引住）。"""
    return '"' + name.replace('"', '""') + '"'


def _literal(name):
    """單引號字串常值（UNION ALL 各列的自帶名欄；③b 寫句之字串值）。"""
    return "'" + name.replace("'", "''") + "'"


_TS_TEXT = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?(Z|[+-]\d{2}(?::?\d{2})?)$")


def _canon_ts(text):
    """timestamptz 文字 → 正規形（UTC isoformat）。兩料源字形不同——pg json 輸出形 `…T…+00:00`（隨連線時區）、凍結 seed
    COPY 形 `… …+00`——正規化後才可逐值比對；寫回時正規形即合法 timestamptz 字面。手寫解析、不倚新版 fromisoformat 之擴形。
    無時區、日期越界或不可解 → BaselineError（rc 2）。"""
    m = _TS_TEXT.match(text) if isinstance(text, str) else None
    if not m:
        raise BaselineError(f"時間欄不可解（須為帶時區之 timestamptz 文字）：{text!r}")
    y, mo, d, h, mi, s, frac, tz = m.groups()
    off = 0 if tz == "Z" else (-1 if tz[0] == "-" else 1) * (int(tz[1:3]) * 60 + (int(tz[-2:]) if len(tz) > 3 else 0))
    try:
        stamp = datetime.datetime(int(y), int(mo), int(d), int(h), int(mi), int(s), int((frac or "0").ljust(6, "0")),
                                  tzinfo=datetime.timezone(datetime.timedelta(minutes=off)))
    except ValueError:
        raise BaselineError(f"時間欄不可解（日期、時刻或時區越界）：{text!r}") from None
    return stamp.astimezone(datetime.timezone.utc).isoformat()


def _cell_ok(kind, v):
    """欄型斷言（ROW_FACES 欄名冊之欄型；基準檔、現況撈取共用）：ts 須已是正規形。"""
    if v is None:
        return kind.endswith("?")
    kind = kind.rstrip("?")
    if kind == "int":
        return isinstance(v, int) and not isinstance(v, bool)
    if kind == "bool":
        return isinstance(v, bool)
    if kind == "ts":
        try:
            return _canon_ts(v) == v
        except BaselineError:
            return False
    return isinstance(v, str)


# ── 三面現算 ────────────────────────────────────────────────────────────────

def fetch_tables(user, db, run):
    """①表面：public 全部表 → {表名: 列數}。零表＝比對面為空 → rc 2。"""
    names = [row[0] for row in psql_rows(SQL_TABLES, user, db, run)]
    if not names:
        raise BaselineError("比對面為空：public schema 零表——空面的全等是假綠（庫錯、schema 未建）")
    sql = " UNION ALL ".join(f"SELECT {_literal(n)}, count(*) FROM {_ident(n)}" for n in names)
    rows = psql_rows(sql, user, db, run)
    try:
        got = {row[0]: int(row[1]) for row in rows}
    except (ValueError, IndexError):
        raise BaselineError("表列數輸出不可解（psql -At 每列應為「表名<分隔>列數」）："
                            f"{rows[:3]!r}——輸出被污染或 psql 形改變") from None
    if sorted(got) != sorted(names):
        raise BaselineError(f"表列數撈取不完整：清單 {len(names)} 表、撈得 {len(got)} 表")
    return got


def fetch_sequences(user, db, run):
    """②序列面：public 全部序列 → {序列名: {last_value, is_called}}。零序列 → rc 2。"""
    names = [row[0] for row in psql_rows(SQL_SEQUENCES, user, db, run)]
    if not names:
        raise BaselineError("比對面為空：public schema 零序列——空面的全等是假綠")
    sql = " UNION ALL ".join(
        f"SELECT {_literal(n)}, last_value, is_called FROM {_ident(n)}" for n in names)
    rows = psql_rows(sql, user, db, run)
    try:
        got = {row[0]: {"last_value": int(row[1]), "is_called": row[2] == "t"} for row in rows}
    except (ValueError, IndexError):
        raise BaselineError("序列值輸出不可解（psql -At 每列應為「序列名<分隔>last_value"
                            f"<分隔>is_called」）：{rows[:3]!r}——輸出被污染或 psql 形改變") from None
    if sorted(got) != sorted(names):
        raise BaselineError(f"序列撈取不完整：清單 {len(names)} 序列、撈得 {len(got)} 序列")
    return got


def group_prefixes(keys):
    """redis 鍵 → {前綴: 鍵數}；前綴＝第一個冒號前段、無冒號者歸 NO_PREFIX；空行略。"""
    out = {}
    for k in keys:
        k = k.strip()
        if not k:
            continue
        prefix = k.split(":", 1)[0] if ":" in k else NO_PREFIX
        out[prefix or NO_PREFIX] = out.get(prefix or NO_PREFIX, 0) + 1
    return out


def fetch_redis(run):
    """③redis 面：DBSIZE 總數＋ --scan 全鍵**去重後**逐前綴分組；零鍵是合法狀態、不算空面。

    ★去重不可省：SCAN 契約只保證「全程存在的鍵至少回傳一次」——rehash 期間會重複回傳同一把，
    逐行累加即把一把算成多把；走查前後兩次取樣重複度不同時，diff 報出實際不存在的殘鍵＝假紅。
    ★DBSIZE 另取並與去重鍵數互證（不等即出提示、不改 rc——取樣間有鍵過期或寫入屬正常，
    嚴格相等會偶發不成立；長期偏離＝SCAN 被截斷之徵）。
    """
    raw = redis_out("DBSIZE", run).strip()
    try:
        dbsize = int(raw)
    except ValueError:
        raise BaselineError(f"redis DBSIZE 回非整數：{raw[:80]!r}") from None
    keys = sorted({k.strip() for k in redis_out("--scan", run).splitlines() if k.strip()})
    prefixes = group_prefixes(keys)
    total = sum(prefixes.values())
    if total != dbsize:
        _say(f"[walkthrough-baseline] 提示：--scan 去重後 {total} 鍵、DBSIZE {dbsize}——兩面不等"
             "（取樣間有鍵過期或寫入即屬正常；長期偏離請查 SCAN 是否被截斷）", err=True)
    return {"dbsize": dbsize, "prefixes": prefixes}


def _check_bound_faces(obj, what):
    """角色／選單／使用者域與遷移帳六欄形斷言（基準檔與現況撈取共用）：id_bounds＝恰 BOUNDED_TABLES 五鍵、值為非負整數（空表記 0）；
    user_role_keys＝[[user_id, role_id], …] 整數對；ROW_FACES 三欄＝列物件 list、每列恰其欄名冊之欄且合欄型、id 互異且不高於
    該表上界；migrations＝非空、互異、依名排序之版本字串清單（空＝比對面為空）。不符 → BaselineError（rc 2；訊息只指欄名與欄型、
    不引欄值＝遮蔽欄之值不出輸出）。"""
    def _int(v):
        return isinstance(v, int) and not isinstance(v, bool)

    bounds = obj.get("id_bounds")
    if not isinstance(bounds, dict) or set(bounds) != set(BOUNDED_TABLES) \
            or not all(_int(v) and v >= 0 for v in bounds.values()):
        raise BaselineError(f"{what}：id_bounds 須為 {{{'／'.join(BOUNDED_TABLES)}: 非負整數上界}}（空表記 0）")
    keys = obj.get("user_role_keys")
    if not isinstance(keys, list) or not all(
            isinstance(k, list) and len(k) == 2 and all(_int(x) for x in k) for k in keys):
        raise BaselineError(f"{what}：user_role_keys 須為 [[user_id, role_id], …]（整數對）")
    for key, (table, _face, cols) in ROW_FACES.items():
        rows = obj.get(key)
        if not isinstance(rows, list) or not all(
                isinstance(r, dict) and set(r) == set(cols) and all(_cell_ok(k, r[c]) for c, k in cols.items())
                for r in rows):
            raise BaselineError(f"{what}：{key} 須為 [{{{'／'.join(f'{c}: {k}' for c, k in cols.items())}}}, …]"
                                "（ts＝正規形 timestamptz、尾綴 ?＝可為 NULL）")
        ids = [r["id"] for r in rows]
        if len(set(ids)) != len(ids) or any(i > bounds[table] for i in ids):
            raise BaselineError(f"{what}：{key} 之 id 須互異且不高於 {table} 上界 {bounds[table]}")
    migs = obj.get("migrations")
    if not isinstance(migs, list) or not migs or not all(isinstance(v, str) and v for v in migs) \
            or len(set(migs)) != len(migs) or migs != sorted(migs):
        raise BaselineError(f"{what}：migrations 須為非空、互異、依名排序之遷移版本字串清單（seaql_migrations.version；"
                            "空＝比對面為空）")


def _canon_ts_cells(rows, cols):
    """列內時間欄（ts／ts?、字串者）就地正規化；非字串或列形不符者原樣留給 _check_bound_faces 指名，字串不可解者由 _canon_ts
    當場拋 BaselineError（rc 2；訊息帶原字面、不帶面名）。"""
    for r in rows if isinstance(rows, list) else ():
        for c, k in cols.items():
            if k.rstrip("?") == "ts" and isinstance(r, dict) and isinstance(r.get(c), str):
                r[c] = _canon_ts(r[c])


def fetch_bound_faces(user, db, run):
    """基準檔角色／選單／使用者域與遷移帳六欄（restore ③b 之目標值與 (a) 遷移帳前置之左源；非比對面之名冊式防法——全表列數仍由①
    現算）：五表 id 上界＋sys_user_role 鍵集（排序）＋授權列全欄、角色列與使用者列可變欄（依 id 排序、時間欄正規化）＋遷移帳（依名
    排序；先排再驗＝不倚庫之定序規則）。六欄同一句撈取＝同一快照、列面之列恆在上界以內。輸出形不符 → rc 2。"""
    got = psql_json(SQL_BOUND_FACES, user, db, run)
    what = "角色／選單／使用者域與遷移帳六欄撈取輸出形不符"
    if not isinstance(got, dict):
        raise BaselineError(f"{what}：須為 {{id_bounds, user_role_keys, {', '.join(ROW_FACES)}, migrations}} 物件")
    for key, (_t, _face, cols) in ROW_FACES.items():
        _canon_ts_cells(got.get(key), cols)
    migs = got.get("migrations")
    if isinstance(migs, list) and all(isinstance(v, str) for v in migs):
        got["migrations"] = sorted(migs)
    _check_bound_faces(got, what)
    return dict({"id_bounds": dict(got["id_bounds"]), "user_role_keys": sorted(got["user_role_keys"]),
                 "migrations": list(got["migrations"])},
                **{key: sorted(got[key], key=lambda r: r["id"]) for key in ROW_FACES})


def snapshot_live(user=DB_USER, db=DB_NAME, run=subprocess.run, now=None):
    """三面現算＋角色／選單／使用者域與遷移帳六欄 → 基準 dict（含 taken_at UTC ISO＋schema_version）。"""
    taken = now or datetime.datetime.now(datetime.timezone.utc)
    snap = {
        "schema_version": SCHEMA_VERSION,
        "taken_at": taken.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tables": fetch_tables(user, db, run),
        "sequences": fetch_sequences(user, db, run),
        "redis": fetch_redis(run),
    }
    snap.update(fetch_bound_faces(user, db, run))
    return snap


# ── 基準檔 ──────────────────────────────────────────────────────────────────

def validate_snapshot(obj):
    """檔形斷言（fail-loud）：缺鍵／型別錯／版本不符／零表零序列 → BaselineError。"""
    if not isinstance(obj, dict):
        raise BaselineError("基準檔壞形：頂層非 object")
    version = obj.get("schema_version")
    if version != SCHEMA_VERSION:
        old = isinstance(version, int) and not isinstance(version, bool) and 1 <= version < 4
        raise BaselineError(f"基準檔壞形：schema_version={version!r}、本工具只認 {SCHEMA_VERSION}"
                            + ("——v3 以前之舊檔形不載遷移帳、無從判遷移差" if old else "") + "（重新 snapshot）")
    tables = obj.get("tables")
    if not isinstance(tables, dict) or not tables \
            or not all(isinstance(v, int) and not isinstance(v, bool) for v in tables.values()):
        raise BaselineError("基準檔壞形：tables 須為非空 {表名: 整數列數}")
    seqs = obj.get("sequences")
    if not isinstance(seqs, dict) or not seqs or not all(
            isinstance(v, dict) and isinstance(v.get("last_value"), int)
            and isinstance(v.get("is_called"), bool) for v in seqs.values()):
        raise BaselineError("基準檔壞形：sequences 須為非空 {序列名: {last_value, is_called}}")
    redis = obj.get("redis")
    if not isinstance(redis, dict) or not isinstance(redis.get("dbsize"), int) \
            or not isinstance(redis.get("prefixes"), dict) \
            or not all(isinstance(v, int) for v in redis["prefixes"].values()):
        raise BaselineError("基準檔壞形：redis 須為 {dbsize: 整數, prefixes: {前綴: 整數}}")
    _check_bound_faces(obj, "基準檔壞形")
    return obj


def load_snapshot(path):
    """讀基準檔：缺席／非 JSON／壞形 → BaselineError（rc 2）。"""
    try:
        with open(path, encoding="utf-8") as fh:
            obj = json.load(fh)
    except FileNotFoundError:
        raise BaselineError(f"基準檔缺席：{path}——走查前須先 snapshot") from None
    except (OSError, json.JSONDecodeError) as ex:
        raise BaselineError(f"基準檔讀取或解析失敗：{path}：{ex}") from None
    return validate_snapshot(obj)


def dump_snapshot(snap, path):
    """寫基準檔（indent＋sort_keys＝可讀、可 diff）；寫入失敗 → BaselineError。"""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(snap, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
    except OSError as ex:
        raise BaselineError(f"基準檔寫入失敗：{path}：{ex}") from None


# ── repo migration 清單（v4；snapshot 告警與 restore 前置共用之單一解析件）──────────────────────

def repo_migrations(lib_path=None):
    """repo migration 清單＝`rust-api/migration/src/lib.rs` 之 migrations() 向量內 `Box::new(<模組>::Migration)` 依序之模組名
    （DeriveMigrationName 取檔名主幹＝seaql_migrations.version；001 刀重放實證之版本名即模組名）。單行與 rustfmt 折行兩形皆解、
    註解內之項不計；斷言：向量內恰為此形之項（殘餘＝不可解）、非零命中、模組名形 ^m[0-9]{4}_[a-z0-9_]+$、互異、各有 `mod <模組>;`
    宣告與同目錄同名 .rs 實檔。不取目錄 glob：未註冊進向量之檔不是遷移。檔缺席或任一不符 → BaselineError（rc 2）。"""
    path = lib_path or os.path.join(REPO_ROOT, MIGRATION_LIB)
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as ex:
        raise BaselineError(f"repo migration 清單讀取失敗：{path}：{ex}") from None
    code = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", " ", text, flags=re.S))
    m = re.search(r"\bfn\s+migrations\s*\(\s*\)[^{]*\{\s*vec!\s*\[(.*?)\]", code, re.S)
    if not m:
        raise BaselineError(f"repo migration 清單零解析：{path} 找不到 migrations() 之 vec![…] 向量")
    entry = r"Box::new\(\s*([A-Za-z0-9_]+)\s*::\s*Migration\s*\)"
    names = re.findall(entry, m.group(1))
    residue = re.sub(entry, "", m.group(1)).replace(",", "").strip()
    if residue:
        raise BaselineError(f"repo migration 清單不可解：{path} 之 migrations() 向量內有非 Box::new(<模組>::Migration) "
                            f"形之項：{residue[:80]!r}")
    if not names:
        raise BaselineError(f"repo migration 清單零命中：{path} 之 migrations() 向量為空")
    src = os.path.dirname(path)
    problems = [f"模組名形不符 ^m[0-9]{{4}}_[a-z0-9_]+$：{n}" for n in names if not _MIGRATION_MODULE.match(n)] + \
               [f"重複：{n}" for n in sorted({n for n in names if names.count(n) > 1})] + \
               [f"缺宣告 mod {n};" for n in dict.fromkeys(names)
                if not re.search(r"^\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+" + re.escape(n) + r"\s*;", code, re.M)] + \
               [f"缺實檔 {n}.rs" for n in dict.fromkeys(names) if not os.path.isfile(os.path.join(src, n + ".rs"))]
    if problems:
        raise BaselineError(f"repo migration 清單不一致（{path}）：" + "；".join(problems))
    return names


def _migration_gap(left, right, left_only, right_only):
    """兩份遷移版本清單之逐版本兩向差 → 指名字串（相等＝空字串）；left_only／right_only＝兩向之標籤。"""
    a = sorted(set(left) - set(right))
    b = sorted(set(right) - set(left))
    return "；".join(([f"{left_only}：{'、'.join(a)}"] if a else []) + ([f"{right_only}：{'、'.join(b)}"] if b else []))


# ── 比對（純函式）───────────────────────────────────────────────────────────

def _seq_text(v):
    return f"last_value={v['last_value']},is_called={'t' if v['is_called'] else 'f'}"


def diff_snapshots(base, live):
    """逐值比對 → 差異列（dict：face／name／base／live／delta）；只列有差者、忽略 taken_at。
    ★例外一項：RUNTIME_APPEND_TABLES 之序列只比存在性（同 tools/schema-gate.py gate2 對其 setval 值正規化之口徑）
    ——逐值比則每跑一次全量測試即恆有差、rc 0 失去判別力；一側缺席仍照報。"""
    rows = []
    absent = "（無）"

    def _int_rows(face, bmap, lmap, missing=None):
        """missing=None＝缺席即「（無）」（表不存在≠0 列）；redis 前綴缺席＝0 鍵、傳 0。"""
        for name in sorted(set(bmap) | set(lmap)):
            b, l = bmap.get(name, missing), lmap.get(name, missing)
            if b != l:
                rows.append({"face": face, "name": name,
                             "base": absent if b is None else b,
                             "live": absent if l is None else l,
                             "delta": (l - b) if (b is not None and l is not None) else "—"})

    _int_rows("表", base["tables"], live["tables"])
    existence_only = frozenset(RUNTIME_APPEND_TABLES.values())
    for name in sorted(set(base["sequences"]) | set(live["sequences"])):
        b, l = base["sequences"].get(name), live["sequences"].get(name)
        if name in existence_only and b is not None and l is not None:
            continue                       # runtime-append 序列：兩側皆在即等、不比值
        if b != l:
            rows.append({"face": "序列", "name": name,
                         "base": absent if b is None else _seq_text(b),
                         "live": absent if l is None else _seq_text(l),
                         "delta": (l["last_value"] - b["last_value"]) if (b and l) else "—"})
    if base["redis"]["dbsize"] != live["redis"]["dbsize"]:
        rows.append({"face": "redis", "name": "DBSIZE",
                     "base": base["redis"]["dbsize"], "live": live["redis"]["dbsize"],
                     "delta": live["redis"]["dbsize"] - base["redis"]["dbsize"]})
    _int_rows("redis", base["redis"]["prefixes"], live["redis"]["prefixes"], missing=0)
    _int_rows("上界", base["id_bounds"], live["id_bounds"])
    bk = {tuple(k) for k in base["user_role_keys"]}
    lk = {tuple(k) for k in live["user_role_keys"]}
    for u, r in sorted(bk ^ lk):                      # 鍵集差逐對一列：現況多＝+1、現況少＝-1
        has = (u, r) in lk
        rows.append({"face": "鍵集", "name": f"{USER_ROLE_TABLE}({u},{r})",
                     "base": absent if has else "有", "live": "有" if has else absent,
                     "delta": 1 if has else -1})
    # 授權列／角色列／使用者列：基準上界以內逐列（缺一列＝-1、多一列＝+1）、同 id 逐欄（值以 json 字面呈現；★遮蔽欄只報「不等」、
    # 兩值皆以 MASK 呈現）；上界以上之列歸上界面與列數面
    for key, (table, face, _cols) in ROW_FACES.items():
        bound = base["id_bounds"][table]
        masked = MASKED_COLUMNS.get(table, ())
        bmap = {r["id"]: r for r in base[key]}
        lmap = {r["id"]: r for r in live[key] if r["id"] <= bound}
        for i in sorted(set(bmap) | set(lmap)):
            b, l = bmap.get(i), lmap.get(i)
            if b is None or l is None:
                rows.append({"face": face, "name": f"{table}(id={i})", "base": "有" if b else absent,
                             "live": "有" if l else absent, "delta": 1 if l else -1})
                continue
            rows += [{"face": face, "name": f"{table}(id={i}).{c}", "base": MASK, "live": MASK, "delta": "不等"}
                     if c in masked else
                     {"face": face, "name": f"{table}(id={i}).{c}", "base": json.dumps(b[c], ensure_ascii=False),
                      "live": json.dumps(l[c], ensure_ascii=False), "delta": "—"} for c in b if b[c] != l[c]]
    # 遷移帳：逐版本兩向差（現況多＝+1、現況少＝-1）
    bm, lm = set(base["migrations"]), set(live["migrations"])
    for v in sorted(bm ^ lm):
        has = v in lm
        rows.append({"face": "遷移帳", "name": v, "base": absent if has else "有", "live": "有" if has else absent,
                     "delta": 1 if has else -1})
    return rows


def _face_counts(snap):
    return (len(snap["tables"]), len(snap["sequences"]), snap["redis"]["dbsize"],
            len(snap["redis"]["prefixes"]))


def render_diff(rows, live):
    """差異列 → 輸出行；空差異＝一行「全等」（附三面規模，證明比對面非空）。"""
    t, s, k, p = _face_counts(live)
    if not rows:
        return [f"[walkthrough-baseline] ✓ 全等（表 {t}／序列 {s}／redis {k} 鍵、{p} 前綴）"]
    lines = ["[walkthrough-baseline] ✗ 與基準有差——面｜名｜基準值｜現值｜差"]
    lines += [f"  {r['face']}｜{r['name']}｜{r['base']}｜{r['live']}｜{r['delta']}" for r in rows]
    n = {face: sum(1 for r in rows if r["face"] == face)
         for face in ("表", "序列", "redis", "上界", "鍵集", "授權列", "角色列", "使用者列", "遷移帳")}
    lines.append(f"[walkthrough-baseline] 摘要：表 {n['表']} 項差／序列 {n['序列']} 項差／"
                 f"redis {n['redis']} 項差／上界 {n['上界']} 項差／鍵集 {n['鍵集']} 項差／"
                 f"授權列 {n['授權列']} 項差／角色列 {n['角色列']} 項差／使用者列 {n['使用者列']} 項差／"
                 f"遷移帳 {n['遷移帳']} 項差"
                 f"（比對面：表 {t}／序列 {s}／redis {k} 鍵、{p} 前綴）")
    return lines


# ── 子命令 ──────────────────────────────────────────────────────────────────

def cmd_snapshot(path, user, db, run=subprocess.run, lib_path=None):
    snap = snapshot_live(user, db, run)
    dump_snapshot(snap, path)
    t, s, k, p = _face_counts(snap)
    _say(f"[walkthrough-baseline] ✓ 基準已寫：{path}（表 {t}／序列 {s}／redis {k} 鍵、{p} 前綴；"
         f"遷移帳 {len(snap['migrations'])} 支；taken_at {snap['taken_at']}）")
    # 走查**前**即告知 restore 前置不成立（restore 時才拒已在走查之後）；基準檔仍可供 diff、rc 不變
    high = bounds_above_sequence(snap)
    if high:
        _say("[walkthrough-baseline] ★告警：角色／選單／使用者域上界高於其序列位置（" + "、".join(high) + "）——本基準檔可供 "
             "diff、但以之 restore 將 rc 2 拒跑（取樣時已有顯式 id 殘列越過序列）；走查前先跑 "
             f"`python3 {PROG} restore --seed` 清殘列後重新 snapshot", err=True)
    # 現庫遷移帳 vs repo migration 清單（快照只讀庫況、不因 repo 面失敗而失效＝告警、rc 不變）：stack 重起即由一次性 migrate 服務
    # 套用未跑者、本基準隨即被 restore 之遷移帳前置拒用
    try:
        gap = _migration_gap(repo_migrations(lib_path), snap["migrations"], "repo 有現庫無＝未套用", "現庫有 repo 無")
    except BaselineError as ex:
        _say(f"[walkthrough-baseline] ★告警：repo migration 清單解析失敗（{ex}）——無從比對現庫遷移帳與 repo；"
             "基準檔照寫、rc 不變", err=True)
    else:
        if gap:
            _say(f"[walkthrough-baseline] ★告警：現庫遷移帳≠repo migration 清單（{gap}）——未套用者於下次 stack 起動由 "
                 "migrate 服務套用、本基準隨即被 restore 之遷移帳前置拒用（套用後即重新 snapshot）；現庫有 repo 無＝工作樹"
                 "分支落後於庫；基準檔照寫、rc 不變", err=True)
    return RC_OK


def cmd_diff(path, user, db, run=subprocess.run):
    base = load_snapshot(path)
    # 現況**不**再過 validate_snapshot：它檢查的每一項在這條路徑上都是恆真（schema_version 由
    # snapshot_live 自己塞、零表零序列已由 fetch_* fail-loud、值型別由 int()／建構過程保證），
    # 沒有任何輸入能讓它拒絕——讀起來像第二道防線、實際是空轉（變異測試殺不死）。真正的守門
    # 在 fetch_tables／fetch_sequences／fetch_redis 各自的 fail-loud，放寬那裡就是真的沒有兜底。
    return _report_diff(base, snapshot_live(user, db, run))


def _report_diff(base, live):
    rows = diff_snapshots(base, live)
    for ln in render_diff(rows, live):
        _say(ln, err=bool(rows))
    return RC_DIFF if rows else RC_OK


# ── restore（寫面恰為列舉語句；安全帶與 seed 比對全在任何寫入之前）────────────────

def _copy_unescape(text):
    """pg COPY text 格 → python 值（`\\N`＝None；反斜線跳脫還原）。"""
    if text == "\\N":
        return None
    return re.sub(r"\\(.)", lambda m: {"t": "\t", "n": "\n", "r": "\r"}.get(m.group(1), m.group(1)), text)


def _seed_copy_rows(lines, table):
    """seed.sql 之 `COPY public.<表>` 段 → (段首欄名串, 資料列 list)；段缺席回 None。"""
    head = re.compile(r"^COPY public\." + re.escape(table) + r" \(([^)]*)\) FROM stdin;$")
    for i, ln in enumerate(lines):
        m = head.match(ln)
        if m:
            rows = []
            for row in lines[i + 1:]:
                if row == "\\.":
                    break
                rows.append(row)
            return m.group(1), rows
    return None


def _seed_copy_fields(blk, table, want):
    """COPY 段（_seed_copy_rows 之回傳）→ 逐列 (want 欄原文 tuple, 該列之錯誤訊息引文)（未跳脫還原）。段首缺欄／列欄數不符＝凍結面
    受損 rc 2。引文＝列文前 80 字；★遮蔽名冊之表（列含密碼雜湊）改為段內列序、不引列文。"""
    cols = [c.strip().strip('"') for c in blk[0].split(",")]
    missing = [c for c in want if c not in cols]
    if missing:
        raise BaselineError(f"seed {table} 段首缺 {'／'.join(missing)} 欄：{cols}——凍結面受損")
    idx = [cols.index(c) for c in want]
    out = []
    for n, row in enumerate(blk[1], 1):
        hint = f"段內第 {n} 列（列含遮蔽欄、列文不印）" if table in MASKED_COLUMNS else repr(row[:80])
        vals = row.split("\t")
        if len(vals) != len(cols):
            raise BaselineError(f"seed {table} 列欄數 {len(vals)} ≠ 段首 {len(cols)}：{hint}——凍結面受損")
        out.append((tuple(vals[i] for i in idx), hint))
    return out


def _seed_copy_ints(blk, table, want):
    """COPY 段 → 逐列取 want 欄之整數 tuple。段首缺欄／列欄數不符／值非整數＝凍結面受損 rc 2。"""
    out = []
    for vals, hint in _seed_copy_fields(blk, table, want):
        try:
            out.append(tuple(int(v) for v in vals))
        except ValueError:
            raise BaselineError(f"seed {table} 列之 {'／'.join(want)} 非整數：{hint}——凍結面受損") from None
    return out


def _copy_cell(kind, text):
    """COPY 格原文 → 合欄型之值（\\N＝NULL、bool＝t／f、ts 正規化）；不合 → ValueError。"""
    v = _copy_unescape(text)
    if v is None:
        if not kind.endswith("?"):
            raise ValueError("非空欄為 NULL")
        return None
    kind = kind.rstrip("?")
    if kind == "int":
        return int(v)
    if kind == "bool":
        return {"t": True, "f": False}[v]
    if kind == "ts":
        return _canon_ts(v)
    return v


def _seed_copy_records(blk, table, cols):
    """COPY 段 → 逐列 {欄: 值}（取 cols 欄名冊之欄、依欄型轉型）、依 id 排序。段首缺欄／列欄數不符／值不合欄型＝凍結面受損 rc 2。"""
    out = []
    for vals, hint in _seed_copy_fields(blk, table, tuple(cols)):
        rec = {}
        for (c, kind), text in zip(cols.items(), vals):
            try:
                rec[c] = _copy_cell(kind, text)
            except (ValueError, KeyError, BaselineError):
                raise BaselineError(f"seed {table} 列之 {c} 不合欄型 {kind}：{hint}——凍結面受損") from None
        out.append(rec)
    return sorted(out, key=lambda r: r["id"])


def seed_restore_target(seed_text):
    """seed 模式之目標態（形同基準檔之清理面子集、供 check_restore_baseline／restore_sql 同一套判定）；seed_text＝凍結 seed ⊕ 演進
    合成之文字（synthesize_seed；空帳＝凍結段之 normalize 形）：tables＝清理面各表與角色／選單／使用者域六表於該文字之 COPY 段列數；sequences＝清理面各序列與 BOUNDED_TABLES 五支之
    setval 行值；id_bounds＝五表 COPY 列 id 最大值（零列記 0）；user_role_keys＝sys_user_role COPY 鍵集（段缺席＝None）；
    ROW_FACES 三欄＝casbin_rule COPY 全欄列、sys_role 與 sys_user COPY 之 id＋可變欄（依欄型轉型、時間欄正規化；段缺席＝空——
    該表上界同缺、由 check_restore_baseline 指名）。段或行缺席者不入 dict（由 check_restore_baseline 指名為清理面缺席）；redis 於
    seed 無載體＝三前綴目標恆 0 鍵；遷移帳於 seed 無載體＝不入目標（seed 模式無 (a) 遷移帳前置、收尾不判該面）。"""
    lines = seed_text.splitlines()
    tables, seqs, bounds, keys = {}, {}, {}, None
    faces = {key: [] for key in ROW_FACES}
    for key, (table, _face, cols) in ROW_FACES.items():
        blk = _seed_copy_rows(lines, table)
        if blk is not None:
            faces[key] = _seed_copy_records(blk, table, cols)
    for t in RESTORE_TABLES:
        blk = _seed_copy_rows(lines, t)
        if blk is not None:
            tables[t] = len(blk[1])
    for t in BOUNDED_TABLES:
        blk = _seed_copy_rows(lines, t)
        if blk is not None:
            ids = [row[0] for row in _seed_copy_ints(blk, t, ("id",))]
            tables[t], bounds[t] = len(ids), max(ids, default=0)
    blk = _seed_copy_rows(lines, USER_ROLE_TABLE)
    if blk is not None:
        pairs = _seed_copy_ints(blk, USER_ROLE_TABLE, ("user_id", "role_id"))
        tables[USER_ROLE_TABLE], keys = len(pairs), sorted([list(p) for p in pairs])
    wanted = set(RESTORE_SEQUENCES) | set(BOUNDED_TABLES.values())
    for m in re.finditer(r"^SELECT pg_catalog\.setval\('public\.(\w+)', (\d+), (true|false)\);$",
                         seed_text, re.M):
        if m.group(1) in wanted:
            seqs[m.group(1)] = {"last_value": int(m.group(2)), "is_called": m.group(3) == "true"}
    return dict({"tables": tables, "sequences": seqs, "redis": {"dbsize": 0, "prefixes": {}},
                 "id_bounds": bounds, "user_role_keys": keys}, **faces)


def seed_mode_baseline(live, target):
    """seed 模式無基準檔：以現況為底、只把清理面與角色／選單／使用者域覆寫成 seed 目標值（清理面七表列數、六支序列、三前綴 0 鍵；
    該域六表列數、五表上界與序列、指派鍵集、授權列／角色列／使用者列可變欄）→ 交 diff_snapshots 比。其餘面（含遷移帳）恆等於現況
    ＝不入判準（無基準可比；該面之 pg 殘留由 tools/schema-gate.py check 之 gate2 逐列兜）。"""
    prefixes = {p: n for p, n in live["redis"]["prefixes"].items() if p not in RESTORE_REDIS_PREFIXES}
    cleared = sum(live["redis"]["prefixes"].get(p, 0) for p in RESTORE_REDIS_PREFIXES)
    return dict({"tables": dict(live["tables"], **target["tables"]),
                 "sequences": dict(live["sequences"], **target["sequences"]),
                 "redis": {"dbsize": live["redis"]["dbsize"] - cleared, "prefixes": prefixes},
                 "id_bounds": dict(target["id_bounds"]), "user_role_keys": target["user_role_keys"],
                 "migrations": list(live["migrations"])},
                **{key: list(target[key]) for key in ROW_FACES})


def seed_settings(seed_text):
    """seed 文字（凍結 seed.sql 或其 ⊕ 演進合成）之 `COPY public.system_settings` 段 → {setting_key: setting_value}。
    段缺席／零列＝比對面為空、段首缺鍵或值欄／列欄數不符＝凍結面受損，皆 BaselineError（rc 2）。"""
    blk = _seed_copy_rows(seed_text.splitlines(), "system_settings")
    if blk is not None:
        cols = [c.strip().strip('"') for c in blk[0].split(",")]
        if "setting_key" not in cols or "setting_value" not in cols:
            raise BaselineError(f"seed system_settings 段首缺 setting_key／setting_value 欄：{cols}")
        ki, vi = cols.index("setting_key"), cols.index("setting_value")
        got = {}
        for row in blk[1]:
            vals = row.split("\t")
            if len(vals) != len(cols):
                raise BaselineError(f"seed system_settings 列欄數 {len(vals)} ≠ 段首 {len(cols)}："
                                    f"{row[:80]!r}——凍結面受損")
            got[_copy_unescape(vals[ki])] = _copy_unescape(vals[vi])
        if not got:
            raise BaselineError("seed system_settings 段零列——比對面為空、不得靜默判綠")
        return got
    raise BaselineError("seed 缺 COPY public.system_settings 段——比對面為空、不得靜默判綠")


def check_seed_evolution(ledger_path, tables):
    """讀演進帳 → entries（供 synthesize_seed 合成與 repo↔現庫遷移同步前置判定）；`tables` 任一表有 seed_* 登記＝拒跑 rc 2、指名登記
    id 與表。cmd_restore 只於 seed 模式傳清理面七表（RESTORE_TABLES；仍拒跑之演進形①）：其還原為 DELETE 全表、以 seed 恆零列為前提，
    照清會把演進帳定義之 seed 列一併刪除；基準檔模式傳空（同一邊界由基準檔清理面須零列之安全帶承擔）。結構性 kind（add_column 等）不在
    此擋——合成面表之結構演進由合成鏈判（未內建形＝GateError）。登記檔缺席／非 JSON／entries 非 list 或含非物件項＝rc 2（形之完整
    斷言權威在 schema-gate、此處只驗讀帳所需）。"""
    try:
        with open(ledger_path, encoding="utf-8") as fh:
            ledger = json.load(fh)
    except FileNotFoundError:
        raise BaselineError(f"演進登記檔缺席：{ledger_path}（{SCHEMA_EVOLUTION}）——無從判定凍結 seed 是否仍為"
                            "期望 seed") from None
    except (OSError, json.JSONDecodeError) as ex:
        raise BaselineError(f"演進登記檔讀取或解析失敗：{ledger_path}（{SCHEMA_EVOLUTION}）：{ex}") from None
    entries = ledger.get("entries") if isinstance(ledger, dict) else None
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        raise BaselineError(f"演進登記檔壞形：{ledger_path}（{SCHEMA_EVOLUTION}）entries 須為物件 list"
                            "——形＝docs/ops/reference-src/schema-evolution-contract.md §2")
    hits = [f"{e.get('id', '?')}（{e.get('kind')}、{e.get('table')}）" for e in entries
            if e.get("table") in tables and e.get("kind") in SEED_EVOLUTION_KINDS]
    if hits:
        raise BaselineError(f"{SCHEMA_EVOLUTION} 有清理面之 seed_* 演進登記：{'、'.join(hits)}——seed 模式之清理面以 DELETE 全表"
                            "還原、前提為 seed 恆零列，照清會把演進帳定義之 seed 列一併刪除（不入合成）；先擴充本工具之清理面"
                            "（改為只刪非 seed 列）、再跑 restore；拒絕執行、零寫入")
    return entries


def load_schema_gate(path):
    """依路徑載入 tools/schema-gate.py（連字檔名不可 import）→ 模組；須帶合成鏈三件（normalize_seed_dump、apply_seed_entries、
    GateError）。載入失敗（檔缺席、模組執行期拋錯、缺件）＝BaselineError（rc 2、原訊息照轉）。不快取（快取由 _schema_gate 承擔）。"""
    try:
        spec = importlib.util.spec_from_file_location("_walkthrough_seed_synth_chain", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        missing = [n for n in ("normalize_seed_dump", "apply_seed_entries", "GateError") if not hasattr(mod, n)]
        if missing:
            raise AttributeError(f"缺合成件 {'、'.join(missing)}")
    except Exception as ex:   # noqa: BLE001 — 載入期之任一失敗皆＝合成鏈不可用、rc 2 原訊息照轉
        raise BaselineError(f"演進合成鏈載入失敗：{path}（{type(ex).__name__}：{ex}）——左源無從合成（期望 seed＝凍結 ⊕ 演進）；"
                            "拒絕執行、零寫入") from None
    return mod


_SCHEMA_GATE_CACHE = {}


def _schema_gate():
    """合成鏈模組（REPO_ROOT 之 SCHEMA_GATE；行程內載入一次）。"""
    if "mod" not in _SCHEMA_GATE_CACHE:
        _SCHEMA_GATE_CACHE["mod"] = load_schema_gate(os.path.join(REPO_ROOT, SCHEMA_GATE))
    return _SCHEMA_GATE_CACHE["mod"]


def synthesize_seed(seed_text, entries, tables):
    """期望 seed 文字＝凍結 seed ⊕ 演進帳中 `tables`（合成射程）各表之登記，經 tools/schema-gate.py 之 gate2 同一合成鏈
    （normalize_seed_dump → apply_seed_entries：seed_add 增列並推進該表序號期望行、seed_update／seed_delete 以 pk 恰命中一列改或刪、
    add_column 之 nullable 無 default 形補欄）——本工具不自持第二份合成。射程外之表之登記不餵（含未內建之 add_table）。合成鏈拋
    GateError（pk 命中≠1、values 欄集不符、值型不支援、add_column 帶 default 或 NOT NULL 等未內建形）＝BaselineError（rc 2、原訊息
    照轉：與 schema 閘同停、於其同一擴充點補齊即兩者同時恢復）。輸出為 normalize 後文字（段內列序重排、setval 原位），交既有解析件
    （seed_restore_target、seed_settings）讀。"""
    gate = _schema_gate()
    feed = [e for e in entries if e.get("table") in tables]
    bad = [str(e.get("id", "?")) for e in feed
           if not (isinstance(e.get("kind"), str) and isinstance(e.get("detail"), dict) and "id" in e)]
    if bad:
        raise BaselineError(f"{SCHEMA_EVOLUTION} 合成射程內之登記項壞形（須帶 id、kind 字串與 detail 物件）：{'、'.join(bad)}"
                            "——形＝docs/ops/reference-src/schema-evolution-contract.md §2；拒絕執行、零寫入")
    try:
        return gate.apply_seed_entries(gate.normalize_seed_dump(seed_text), feed)
    except gate.GateError as ex:
        raise BaselineError(f"演進登記合成失敗（{SCHEMA_GATE} 之 gate2 合成鏈拋 GateError、與 schema 閘同停）：{ex}——拒絕執行、"
                            "零寫入；補救＝於 schema 閘合成鏈同一擴充點補齊該形（兩工具同時恢復）或修正登記") from None


def bounds_above_sequence(snap):
    """③b 前置之判定（純函式；snapshot 告警與 restore 兩模式拒跑共用）：BOUNDED_TABLES 五表之 id 上界高於其序列位置
    （nextval 已發出之最大值：is_called 真＝last_value、假＝last_value-1）者 → 指名字串 list。基準檔上成立＝取樣時已有顯式
    id 殘列越過序列（號段殘列）：走查以 nextval 造之列落在序列與上界之間、`id >` 上界刪不到，序列卻被 setval 回其下＝下一次
    nextval 撞 PK；seed 模式之合成目標上成立＝凍結面受損或演進合成未推進序號。序列缺席者略（缺席由 check_restore_baseline 另判）。"""
    high = []
    for t, s in BOUNDED_TABLES.items():
        v = snap["sequences"].get(s)
        if v is not None and snap["id_bounds"][t] > v["last_value"] - (0 if v["is_called"] else 1):
            high.append(f"{t} 上界 {snap['id_bounds'][t]}＞{s}（{_seq_text(v)}）")
    return high


def check_restore_baseline(snap, seed_mode=False):
    """安全帶：清理面或角色／選單／使用者域之表、序列、上界、鍵集不在目標態（基準檔；seed 模式＝凍結 seed ⊕ 演進合成）＝結構異常；清理面各表
    列數或 session／throttle／cpwd 前綴鍵數非 0＝拒跑。restore 只服務「目標態之清理面為空」之形——DELETE 全表對非空目標會連
    其資料一起毀掉、diff 還報不出來。★角色／選單／使用者域六表不套列數拒跑：其寫面只刪上界以上列與鍵集差、回補與回寫目標列、不毀目標態
    之列；改拒「目標態五表上界高於其序列位置」（bounds_above_sequence）：基準檔模式＝取樣時已有顯式 id 殘列越過序列、補救指
    seed 模式；seed 模式＝凍結面受損或演進合成未推進序號（真檔之 COPY 列 id 最大值恰等於其 setval 位置、自測釘住＝不觸發）。"""
    # zh-TW 排版：以拉丁詞收尾的 origin（`凍結 seed`）與後接中文之間須有分隔空格，純中文者不須
    origin, sep = ("凍結 seed", " ") if seed_mode else ("基準檔", "")
    absent = [t for t in RESTORE_TABLES if t not in snap["tables"]] + \
             [s for s in RESTORE_SEQUENCES if s not in snap["sequences"]] + \
             [t for t in BOUNDED_TABLES if t not in snap["id_bounds"]] + \
             ([USER_ROLE_TABLE] if snap["user_role_keys"] is None else []) + \
             [s for s in BOUNDED_TABLES.values() if s not in snap["sequences"]]
    if absent:
        why = "凍結面受損或清理面名冊與 schema 不符" if seed_mode else "庫錯或基準檔非本 schema 所取"
        raise BaselineError(f"{origin}{sep}缺 restore 清理面：{'、'.join(absent)}——{why}")
    loaded = [f"{t} {snap['tables'][t]} 列" for t in RESTORE_TABLES if snap["tables"][t]] + \
             [f"{p} 前綴 {snap['redis']['prefixes'][p]} 鍵" for p in RESTORE_REDIS_PREFIXES
              if snap["redis"]["prefixes"].get(p)]
    if loaded and seed_mode:
        raise BaselineError(f"{origin}{sep}之清理面非空、DELETE 全表會毀掉 seed 資料（" + "、".join(loaded) +
                            "）——seed 模式只服務清理面於 seed 為零列之形；拒絕執行、零寫入（先擴充本工具）")
    if loaded:
        raise BaselineError("基準非空、DELETE 全表會毀掉基準資料（" + "、".join(loaded) +
                            "）——restore 只服務走查前為空基準之形；拒絕執行、零寫入。補救：手上有取於空基準之較早 "
                            f"snapshot 檔＝改以該檔跑 restore；無此檔＝改跑 `python3 {PROG} restore --seed`"
                            "（以凍結 seed ⊕ 演進合成為目標態、無須基準檔）")
    high = bounds_above_sequence(snap)
    if high and seed_mode:
        raise BaselineError(f"{origin}{sep}之角色／選單／使用者域上界高於其序列位置（" + "、".join(high) + "）——凍結面受損或演進"
                            "合成未推進序號（seed_add 新列 id 高於期望序號而序號行未隨之推進）：照跑則序列 setval 回 seed 值後、下一次 "
                            "nextval 撞 seed 列 PK；拒絕執行、零寫入")
    if high:
        raise BaselineError("基準檔之角色／選單／使用者域上界高於其序列位置（" + "、".join(high) + "）——取樣時已有顯式 id 殘列越過"
                            "序列：走查以 nextval 造之列落在序列與上界之間、刪不到，序列卻被 setval 回其下＝下一次 nextval 撞 PK；"
                            f"拒絕執行、零寫入。補救：改跑 `python3 {PROG} restore --seed`（目標態＝凍結 seed ⊕ 演進合成、殘列一併刪除）；"
                            "下次走查前先清殘列再 snapshot")


def psql_json(sql, user, db, run):
    """跑一句回單值 JSON 的 SELECT → 解析後的值；psql 非零或輸出非 JSON＝rc 2。"""
    r = _run_docker(psql_argv(sql, user, db), run)
    if r.returncode != 0:
        raise BaselineError(f"psql 失敗（rc={r.returncode}）：{(r.stderr or '').strip()[:300]}"
                            f"——補救：dev stack 未起→{STARTUP_HINT}")
    try:
        return json.loads((r.stdout or "").strip() or "[]")
    except json.JSONDecodeError as ex:
        raise BaselineError(f"psql JSON 輸出不可解（{ex.msg}）——輸出被污染或查詢形改變") from None


def check_settings_against_seed(live_rows, seed):
    """①system_settings 現況 vs 期望 seed（seed＝synthesize_seed 合成文字之 seed_settings；凍結 ⊕ 演進）：鍵缺／鍵多／值不等＝
    fail-loud 指名（restore 不改值）；回審計欄非 NULL 之列數。"""
    need = {"setting_key", "setting_value", "stamped"}
    if not isinstance(live_rows, list) or not all(isinstance(r, dict) and need <= set(r) for r in live_rows):
        raise BaselineError("system_settings 撈取輸出形不符（須為 [{setting_key, setting_value, stamped}]）")
    live = {r["setting_key"]: r["setting_value"] for r in live_rows}
    bad = [f"{k} 現值缺席／seed {seed[k]!r}" for k in sorted(set(seed) - set(live))] + \
          [f"{k} 現值 {live[k]!r}／seed 無此鍵" for k in sorted(set(live) - set(seed))] + \
          [f"{k} 現值 {live[k]!r}／seed {seed[k]!r}" for k in sorted(set(seed) & set(live))
           if live[k] != seed[k]]
    if bad:
        raise BaselineError("system_settings 與期望 seed（凍結 seed ⊕ 演進登記合成）不等——restore 不自動改值（先以 002 刀 "
                            "system_settings 寫端改回期望值、再跑 restore）：" + "；".join(bad))
    return sum(1 for r in live_rows if r["stamped"])


def _setval_sql(name, v):
    return f"SELECT setval('{name}', {v['last_value']}, {'true' if v['is_called'] else 'false'});"


def restore_sql(snap, sequences=RESTORE_SEQUENCES, seed_surface=()):
    """②③ 單交易寫句：審計欄歸 NULL → 清理面七表 DELETE＋session_id 歸 NULL → setval（值自目標態 snap 現讀；
    基準檔模式＝RESTORE_SEQUENCES 六支、seed 模式＝SEED_SETVAL_SEQUENCES——runtime-append 序列不復位）→ seed_surface
    （③b 角色／選單／使用者域寫句、seed_surface_sql 產；cmd_restore 兩模式恆帶、接在 COMMIT 之前）。"""
    seqs = snap["sequences"]
    setvals = tuple(_setval_sql(n, seqs[n]) for n in sequences)
    return " ".join(("BEGIN;", SQL_RESTORE_AUDIT) + SQL_RESTORE_CLEAR + setvals + tuple(seed_surface) + ("COMMIT;",))


def _sql_value(v):
    """③b 寫句之值字面：None＝NULL、bool＝true／false、整數原樣、字串（含時間欄正規形）經 _literal。"""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return _literal(v)


def _writeback_sql(table, cols, r):
    """③b 可變欄回寫句（角色列與使用者列同形）：設回目標值、且只在 id 相符而可變欄與目標不等（IS DISTINCT FROM）時寫——改回值＝
    改回痕（審計欄同列）。"""
    return (f"UPDATE {table} SET {', '.join(f'{c} = {_sql_value(r[c])}' for c in cols)} "
            f"WHERE id = {r['id']} AND ({', '.join(cols)}) IS DISTINCT FROM "
            f"({', '.join(_sql_value(r[c]) for c in cols)});")


def seed_surface_sql(snap):
    """③b 角色／選單／使用者域寫句（值自目標態 snap 現讀：基準檔六欄＋序列面，或 seed_restore_target）：sys_user_role 鍵集差
    刪除（現況有而目標無之對；目標鍵集空＝全清）→ BOUNDED_TABLES 五表依名冊序刪 `id >` 上界（sys_user 居末）→ casbin_rule 回補
    目標列（一句 INSERT、原 id 原值全欄、ON CONFLICT DO NOTHING＝現況已有者〔主鍵或身分鍵 (ptype, v0～v5) 相撞〕不動、只補基準有而
    現況無之列）→ sys_user_role 回補目標鍵集（一句 INSERT、ON CONFLICT DO NOTHING＝只補目標有而現況無之對）→ sys_role 逐目標列回寫
    可變欄（含審計欄）→ sys_user 逐目標列回寫可變欄（含密碼雜湊、審計欄與軟刪兩欄）→ 五支 setval 回目標值。
    ★授權列回補排在刪上界列之後（理同測試守衛授權腿之 Drop 序）：走查復原以新 id 回插同身分列，先補則被身分鍵吞掉、新列隨後被刪＝
    該列永久缺席。★指派回補排在一切刪除之後：指派之外鍵 RESTRICT 指帳號列與角色列——先補則新帳號（id > 上界）之指派可能被補回、
    其列隨後之刪除撞外鍵；基準內帳號被軟刪而其指派被硬刪者，指派回補與軟刪兩欄寫回同交易（外鍵只問列存在、不問軟刪）。★五表絕不
    DELETE 全表（seed 有列）；射程界＝補回被刪之授權列與指派對、回寫角色列與使用者列可變欄——其餘欄之就地改寫與他表 id ≤ 上界列之
    被刪不還原。目標之列面或鍵集為空＝不出對應之回補句、回寫句。"""
    keys = sorted(tuple(k) for k in snap["user_role_keys"])
    if keys:
        keep = ", ".join(f"({u}, {r})" for u, r in keys)
        user_role = f"DELETE FROM {USER_ROLE_TABLE} WHERE (user_id, role_id) NOT IN (VALUES {keep});"
    else:
        user_role = f"DELETE FROM {USER_ROLE_TABLE};"
    deletes = tuple(f"DELETE FROM {t} WHERE id > {snap['id_bounds'][t]};" for t in BOUNDED_TABLES)
    backfill = ()
    if snap["casbin_rule_rows"]:
        values = ", ".join("(" + ", ".join(_sql_value(r[c]) for c in CASBIN_RULE_COLUMNS) + ")"
                           for r in snap["casbin_rule_rows"])
        backfill = (f"INSERT INTO casbin_rule ({', '.join(CASBIN_RULE_COLUMNS)}) VALUES {values} "
                    "ON CONFLICT DO NOTHING;",)
    if keys:
        backfill += (f"INSERT INTO {USER_ROLE_TABLE} (user_id, role_id) VALUES {keep} ON CONFLICT DO NOTHING;",)
    writebacks = tuple(_writeback_sql("sys_role", SYS_ROLE_MUTABLE_COLUMNS, r) for r in snap["sys_role_rows"]) + \
        tuple(_writeback_sql("sys_user", SYS_USER_MUTABLE_COLUMNS, r) for r in snap["sys_user_rows"])
    setvals = tuple(_setval_sql(s, snap["sequences"][s]) for s in BOUNDED_TABLES.values())
    return (user_role,) + deletes + backfill + writebacks + setvals


def casbin_restore_touches(state, target):
    """⑥重啟句判準（寫入前現讀 SQL_CASBIN_STATE）：現況 casbin_rule 有 id > 目標上界之列（③b 會刪）、其序列≠目標值
    （③b 會 setval 改值）或目標授權列之 id 有不在現況者（③b 將回補 ≥1 列）＝本次 restore 直改判定面左源。回 (是否觸及,
    將回補之 id 清單)；輸出形不符 → rc 2（仍在任何寫入之前）。"""
    seq = state.get("seq") if isinstance(state, dict) else None
    ids = state.get("ids") if isinstance(state, dict) else None
    if not (isinstance(seq, dict) and isinstance(state.get("max_id"), int)
            and not isinstance(state["max_id"], bool) and isinstance(seq.get("last_value"), int)
            and isinstance(seq.get("is_called"), bool)
            and isinstance(ids, list) and all(_cell_ok("int", i) for i in ids)):
        raise BaselineError("casbin_rule 現態撈取輸出形不符（須為 {max_id, ids: [整數…], seq: {last_value, is_called}}）"
                            "——輸出被污染或查詢形改變；拒絕執行、零寫入")
    want = target["sequences"][BOUNDED_TABLES["casbin_rule"]]
    missing = sorted({r["id"] for r in target["casbin_rule_rows"]} - set(ids))
    touched = state["max_id"] > target["id_bounds"]["casbin_rule"] or \
        (seq["last_value"], seq["is_called"]) != (want["last_value"], want["is_called"]) or bool(missing)
    return touched, missing


def redis_clear_prefixes(run):
    """④依前綴 `--scan --pattern` 取鍵（去重、排序）→ 逐鍵指名 DEL（每批 ≤REDIS_DEL_BATCH；零鍵不送 DEL）。
    回 ({前綴: 鍵數}, DEL 回報刪除數)；DEL 回非整數＝rc 2。"""
    found, keys, deleted = {}, [], 0
    for p in RESTORE_REDIS_PREFIXES:
        got = sorted({k.strip() for k in
                      redis_out(f"--scan --pattern {shlex.quote(p + ':*')}", run).splitlines()
                      if k.strip()})
        found[p] = len(got)
        keys += got
    for i in range(0, len(keys), REDIS_DEL_BATCH):
        raw = redis_out("DEL " + " ".join(shlex.quote(k) for k in keys[i:i + REDIS_DEL_BATCH]),
                        run).strip()
        try:
            deleted += int(raw)
        except ValueError:
            raise BaselineError(f"redis DEL 回非整數：{raw[:80]!r}——pg 交易已提交、redis 殘鍵未必清完；"
                                "補救：確認 redis 容器可用後重跑同一 restore（冪等：pg 面已空、只剩前綴鍵待清；"
                                "★④b 門鈴已排在本步之前、不受影響）") from None
    return found, deleted


def _read_seed(seed_path):
    try:
        with open(seed_path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as ex:
        raise BaselineError(f"seed 左源讀取失敗：{seed_path}：{ex}") from None


def doorbell_cli():
    """人工補按門鈴的完整命令（工具自己按不到時、輸出給人照抄）。"""
    return (f"{' '.join(COMPOSE_EXEC)} {REDIS_SERVICE} "
            f"sh -lc 'redis-cli -a \"$(cat {REDIS_PASSWORD_FILE})\" --no-auth-warning "
            f"PUBLISH {IPGATE_CHANNEL} {IPGATE_DOORBELL_PAYLOAD}'")


def ring_doorbell(ip_rows, run):
    """④b門鈴（BL-00094）：清前 sys_ip_rule 有列＝規則集已被本次 restore 清掉⇒判定面必須換版。
    清前 0 列＝規則集本就是空的、判定面與庫一致，不按（避免無謂喚醒）。
    ★PUBLISH 失敗＝pg 已提交而門鈴未響：拋出並附可照抄的人工命令（重跑 restore 補不回來——屆時清前已 0 列）。"""
    if not ip_rows:
        _say("[walkthrough-baseline] restore ④b門鈴：清前 sys_ip_rule 0 列＝該表本就是空的、"
             "判定面與庫一致，不按（避免無謂喚醒）")
        return 0
    raw = redis_out(f"PUBLISH {IPGATE_CHANNEL} {IPGATE_DOORBELL_PAYLOAD}", run).strip()
    try:
        subs = int(raw)
    except ValueError:
        raise BaselineError(f"redis PUBLISH 回非整數：{raw[:80]!r}——pg 交易已提交（規則列已清）而門鈴未響、"
                            "執行中的 rust-api 判定面仍持舊規則集；★重跑 restore 補不回來（屆時清前已 0 列）、"
                            f"請手按一次：{doorbell_cli()}") from None
    tail = "" if subs else "（★0＝無 watcher 在訂：rust-api 未起或 watcher 未啟；其判定面於下次啟動時才換版）"
    _say(f"[walkthrough-baseline] restore ④b門鈴：清前 sys_ip_rule {ip_rows} 列⇒"
         f"PUBLISH {IPGATE_CHANNEL} 已送、訂閱者 {subs}{tail}")
    return subs


def fetch_live_migrations(user, db, run):
    """現庫遷移帳之單句現讀（restore 之 (a) 遷移帳前置與 (b) repo↔現庫遷移同步前置共用、同一次 restore 至多一讀；唯讀）→ 版本字串
    list；撈取輸出形不符＝rc 2（仍在任何寫入之前）。"""
    live = psql_json(SQL_MIGRATIONS, user, db, run)
    if not isinstance(live, list) or not all(isinstance(v, str) and v for v in live):
        raise BaselineError("現庫遷移帳撈取輸出形不符（須為 seaql_migrations.version 字串 list）——輸出被污染或查詢形改變；"
                            "拒絕執行、零寫入")
    return live


def check_migrations_against_baseline(base, user, db, run):
    """(a) 遷移帳前置（基準檔模式；結構安全帶之後、任何寫入與門鈴、settings、重啟句之現讀之前）：單句現讀 seaql_migrations、與基準檔
    migrations 比——不等＝rc 2、零寫入、逐版本指名兩向差並指示補救。以遷移前後不同之基準照跑＝反做該遷移之增刪列（刪其新列、補回其
    刪列、序列撥回）而不還原其欄值改動、遷移帳仍記已跑＝無工具修路之混合態；寫入前擋下是唯一不留混合態之點。回現庫遷移帳（供 (b)
    共用、免二讀）；撈取輸出形不符＝rc 2（仍在任何寫入之前）。"""
    live = fetch_live_migrations(user, db, run)
    gap = _migration_gap(base["migrations"], live, "基準有現庫無", "現庫有基準無")
    if gap:
        raise BaselineError(f"基準檔遷移帳≠現庫（{gap}）——以遷移前後不同之基準還原＝反做該遷移之增刪列而不還原其欄值改動、"
                            "遷移帳仍記已跑＝無工具修路之混合態；拒絕執行、零寫入。補救：走查尚未開始＝重新 snapshot 取本次基準；"
                            f"走查已發生而無同遷移狀態之基準＝改跑 `python3 {PROG} restore --seed`")
    return live


def check_repo_migration_sync(entries, tables, live, user, db, run, lib_path=None):
    """(b) repo↔現庫遷移同步前置（兩模式；(a) 之後〔seed 模式無 (a)〕、門鈴、settings、重啟句之現讀與一切寫入之前）：合成射程 `tables`
    之表於演進帳有 seed_* 登記時才驗——repo migration 清單（repo_migrations；解析失敗＝rc 2、先於現讀）須恰等現庫遷移帳（live＝(a)
    已讀者、None＝本處單句現讀）。期望 seed 依 repo 之演進帳合成，現庫未套用（或多出）對應遷移＝合成目標與庫況不同步：照跑即把未套用之
    遷移效果硬寫進庫（或反做已套用者）——不等＝rc 2、零寫入、指名未套用與 repo 外之遷移並附補救。無涉表登記＝不驗、回 None；驗過回
    repo 清單支數。"""
    hits = [f"{e.get('id', '?')}（{e.get('kind')}、{e.get('table')}）" for e in entries
            if e.get("table") in tables and e.get("kind") in SEED_EVOLUTION_KINDS]
    if not hits:
        return None
    repo = repo_migrations(lib_path)
    if live is None:
        live = fetch_live_migrations(user, db, run)
    gap = _migration_gap(repo, live, "repo 有現庫無＝未套用", "現庫有 repo 無")
    if gap:
        raise BaselineError(f"repo migration 清單≠現庫遷移帳（{gap}）——合成射程之表有 seed_* 演進登記（{'、'.join(hits)}）：期望 seed "
                            "依 repo 之演進帳合成、庫況未同步＝合成目標不可用（照跑即把未套用之遷移效果硬寫進庫、或反做已套用者）；拒絕"
                            "執行、零寫入。補救：repo 有現庫無＝重起 stack 由一次性 migrate 服務套用（dev 庫寫入、需放行）後再跑；現庫有 "
                            "repo 無＝工作樹切回含該遷移之分支後再跑")
    return len(repo)


_PSQL_ECHO = re.compile(r"^(LINE \d+:|\s*\^\s*$)")
_FAILING_ROW = re.compile(r"(Failing row contains )\(.*\)")


def _scrub_psql_error(text, snap):
    """restore 交易失敗之 psql 錯誤文 → 可轉述形：剔除 SQL 回顯行與游標行（psql 對帶位置之錯誤回顯所送 SQL 片段——含使用者列回寫之
    密碼雜湊）、遮蔽失敗列值（DETAIL Failing row contains；PG 對長值截斷＝片段）、再把目標態遮蔽欄之值換成 MASK——雜湊原文與其片段
    皆不出工具輸出；ERROR／DETAIL 其餘行照轉。"""
    out = "\n".join(ln for ln in text.splitlines() if not _PSQL_ECHO.match(ln))
    out = _FAILING_ROW.sub(r"\1(" + MASK + "：失敗列值不印)", out)
    secrets = {r[c] for key, (table, _face, _cols) in ROW_FACES.items() for c in MASKED_COLUMNS.get(table, ())
               for r in snap.get(key, ()) if isinstance(r.get(c), str) and r[c]}
    for v in sorted(secrets, key=len, reverse=True):
        out = out.replace(v, MASK)
    return out


def cmd_restore(path, user, db, run=subprocess.run, seed_path=None, ledger_path=None, lib_path=None):
    """path＝基準檔（目標態＝該檔、清理面六支＋角色／選單／使用者域五支序列依檔 setval、收尾＝對該檔 diff；寫入前另過 (a) 遷移帳前置）；
    path=None＝seed 模式（目標態＝凍結 seed ⊕ 演進合成之清理面與角色／選單／使用者域、清理面只 setval SEED_SETVAL_SEQUENCES＋該域
    五支、收尾＝兩面對合成目標值之比對）。兩模式之 system_settings 比對左源＝合成文字；合成射程有 seed_* 登記時另過 (b) repo↔現庫遷移
    同步前置（lib_path＝repo migration 清單料源、None＝真 repo）。讀帳、合成、前置判定與重啟句判準之現讀皆在任何寫入之前；重啟句於收尾
    （含提交後失敗路徑）輸出。"""
    seed_mode = path is None
    seed_text = _read_seed(seed_path or os.path.join(REPO_ROOT, SEED_FIXTURE))
    base = None if seed_mode else load_snapshot(path)
    entries = check_seed_evolution(ledger_path or os.path.join(REPO_ROOT, SCHEMA_EVOLUTION),
                                   RESTORE_TABLES if seed_mode else ())
    synth_tables = SYNTH_TABLES_SEED if seed_mode else SYNTH_TABLES_BASELINE
    synth_text = synthesize_seed(seed_text, entries, synth_tables)
    fed = sum(1 for e in entries if e.get("table") in synth_tables)
    if seed_mode:
        base = seed_restore_target(synth_text)
    check_restore_baseline(base, seed_mode)
    sequences = SEED_SETVAL_SEQUENCES if seed_mode else RESTORE_SEQUENCES
    seed = seed_settings(synth_text)
    live_migrations = None
    if not seed_mode:
        live_migrations = check_migrations_against_baseline(base, user, db, run)
        _say(f"[walkthrough-baseline] restore (a)遷移帳前置：基準＝現庫（{len(live_migrations)} 支）")
    synced = check_repo_migration_sync(entries, synth_tables, live_migrations, user, db, run, lib_path)
    if synced is not None:
        _say(f"[walkthrough-baseline] restore (b)repo↔現庫遷移同步前置：合成射程有 seed_* 登記、repo＝現庫（{synced} 支）")
    # 門鈴判準（BL-00094）：清前列數須在任何寫入之前取——DELETE 之後就再也問不到「規則集有沒有變」。
    # ★`sys_ip_rule` 在 RESTORE_TABLES 內由 test_restore_surface_is_six_tables_five_sequences_and_three_prefixes 釘住，此處不再寫
    # 常真守衛（mb4t review L1-10）。
    ip_rows = int((psql_json(SQL_IP_RULE_ROWS, user, db, run) or [{"n": 0}])[0]["n"])
    stamped = check_settings_against_seed(psql_json(SQL_SETTINGS, user, db, run), seed)
    _say(f"[walkthrough-baseline] restore ①system_settings：{len(seed)} 鍵值＝期望 seed（凍結 seed ⊕ 演進合成：射程 "
         f"{'／'.join(synth_tables)}、餵入 {fed} 筆登記）；審計欄非 NULL {stamped} 列（交易內歸 NULL）")
    # 重啟句判準（⑥）須在任何寫入之前現讀——交易提交後就再也問不到「有沒有刪過 casbin_rule 列、改過其序列、回補過其列」。
    casbin_touched, backfill_ids = casbin_restore_touches(psql_json(SQL_CASBIN_STATE, user, db, run), base)
    r = _run_docker(psql_argv(restore_sql(base, sequences, seed_surface_sql(base)), user, db), run)
    if r.returncode != 0:
        raise BaselineError(f"restore 交易失敗（rc={r.returncode}、整筆回滾、未動 redis）："
                            f"{_scrub_psql_error((r.stderr or '').strip(), base)[:300]}"
                            "；補救：依上列 psql 錯誤修正（常見＝postgres 容器未起）後重跑同一 restore（交易已回滾、可安全重跑）")
    try:
        seqs = "、".join(f"{n}（{_seq_text(base['sequences'][n])}）" for n in sequences)
        _say(f"[walkthrough-baseline] restore ②③pg 單交易已提交：DELETE {'／'.join(RESTORE_TABLES)}＋"
             f"sys_user.session_id 歸 NULL＋setval（{seqs}）")
        bounds = "／".join(f"{t} ≤{base['id_bounds'][t]}" for t in BOUNDED_TABLES)
        role_seqs = "、".join(f"{s}（{_seq_text(base['sequences'][s])}）" for s in BOUNDED_TABLES.values())
        _say(f"[walkthrough-baseline] restore ③b（同一交易）：{USER_ROLE_TABLE} 鍵集差刪除（目標 "
             f"{len(base['user_role_keys'])} 對之外）→ 刪 id > 上界（{bounds}）→ casbin_rule 回補目標列（目標 "
             f"{len(base['casbin_rule_rows'])} 列、原 id 原值、ON CONFLICT DO NOTHING；寫入前現讀缺 {len(backfill_ids)} 列）"
             f"→ {USER_ROLE_TABLE} 回補目標鍵集（目標 {len(base['user_role_keys'])} 對、ON CONFLICT DO NOTHING）"
             f"→ sys_role 可變欄回寫（目標 {len(base['sys_role_rows'])} 列、含審計欄、只寫與目標不等者）"
             f"→ sys_user 可變欄回寫（目標 {len(base['sys_user_rows'])} 列、含密碼雜湊、審計欄與軟刪兩欄、只寫與目標不等者）"
             f"＋setval（{role_seqs}）")
        # ★門鈴排在 pg 交易之後、redis 清理之前（mb4t review L1-1）：規則列此刻已從庫裡消失，判定面必須換版；
        # 排在 redis 清理之後會被「DEL 失敗即拋」吃掉，而依其補救訊息重跑時清前列數已是 0＝永遠補不回來。
        ring_doorbell(ip_rows, run)
        found, deleted = redis_clear_prefixes(run)
        counts = "／".join(f"{p} 前綴 {n} 鍵" for p, n in found.items())
        _say(f"[walkthrough-baseline] restore ④redis：{counts}、DEL 回報 {deleted} 鍵（逐鍵指名）")
        if seed_mode:
            _say("[walkthrough-baseline] restore ⑤收尾比對（seed 模式：判準面＝清理面與角色／選單／使用者域對合成目標值、"
                 "其 rc 即 restore 之 rc；其餘面無基準可比＝不判，pg 殘留另跑 python3 tools/schema-gate.py check）：")
            live = snapshot_live(user, db, run)
            return _report_diff(seed_mode_baseline(live, base), live)
        _say("[walkthrough-baseline] restore ⑤收尾 diff（其 rc 即 restore 之 rc；0＝已還原）：")
        return cmd_diff(path, user, db, run)
    finally:
        # ⑥重啟句收尾輸出——含提交後任一步失敗之路徑：判定面左源已被改，而依補救重跑 restore 時現讀已等於目標＝不再輸出。
        if casbin_touched:
            _say(CASBIN_RESTART_HINT)


def usage(msg=None):
    if msg:
        _say(f"[walkthrough-baseline] 用法錯：{msg}", err=True)
    _say(f"用法：python3 {PROG} snapshot <檔> [--user U] [--db D]\n"
         f"      python3 {PROG} diff <檔> [--user U] [--db D]\n"
         f"      python3 {PROG} restore <檔>｜--seed [--user U] [--db D]\n"
         f"      python3 {PROG} test\n"
         f"  snapshot＝走查前取三面基準寫 JSON；diff＝走查後重取現況逐值比對（rc 0 才算環境已還原；"
         f"runtime-append 表之序列只比存在性）；"
         f"restore <檔>＝走查後清理（安全帶：清理面七表與三前綴之基準須為空、角色／選單／使用者域五表之基準上界須不高於其序列、"
         f"基準檔遷移帳須等於現庫、合成射程有 seed_* 演進登記時 repo migration 清單須等於現庫遷移帳；system_settings 左源＝凍結 seed "
         f"⊕ 演進合成；該域刪上界以上列與鍵集差、補回被刪之 casbin_rule 列與指派對、回寫 sys_role／sys_user 可變欄）"
         f"＋收尾 diff（rc 即 diff 之 rc；動過 casbin_rule〔刪列、回補或改序列〕即輸出重啟 rust-api 句）；"
         f"restore --seed＝無基準檔、清理面與角色／選單／使用者域還原到凍結 seed ⊕ 演進合成之目標態（runtime-append 序列不復位；"
         f"清理面各表有 seed_* 演進登記即拒跑）；"
         f"退出碼 0 全等／1 有差／2 環境或結構異常（restore 含拒跑）／64 用法錯", err=True)
    return RC_USAGE


def _parse_opts(args):
    """`--user U`／`--db D` 手寫解析（沿 schema-gate 形）；回 (user, db) 或 usage 錯誤訊息。"""
    user, db = DB_USER, DB_NAME
    i = 0
    while i < len(args):
        flag = args[i]
        if flag not in ("--user", "--db"):
            return None, f"未知旗標或多餘引數：{flag}"
        if i + 1 >= len(args) or args[i + 1].startswith("--"):
            return None, f"旗標 {flag} 缺值"
        if flag == "--user":
            user = args[i + 1]
        else:
            db = args[i + 1]
        i += 2
    return (user, db), None


def main(argv, run=subprocess.run):
    if len(argv) < 2:
        return usage()
    cmd = argv[1]
    if cmd == "test":
        result = unittest.main(argv=[argv[0]], exit=False, verbosity=1).result
        if result.wasSuccessful():
            _say(f"[walkthrough-baseline] ✓ self-test 過（{result.testsRun} 案：diff 純函式六形、"
                 "前綴分組與 SCAN 去重、DBSIZE 互證、JSON 往返、基準檔缺席／壞形（含型別）、"
                 "空面與撈取截斷 rc 2、"
                 "psql 輸出不可解 rc 2、退出碼四態＋字面契約、用法、psql／redis 命令構造與 snapshot／diff 唯讀、"
                 "目錄 SQL 與 count 腿抗窄化、密碼不出 argv、print 全 flush；runtime-append 序列只比存在性＋"
                 "名冊對賬 schema-gate；restore 寫面逐字＋次序、清理面七表（含經手表與存取日誌）六序列三前綴（含 cpwd）、"
                 "setval 自基準現讀、安全帶拒跑零呼叫、清理面缺席、settings 值≠期望 seed（含值≠合成值）零寫入、收尾 diff rc、"
                 "失敗即停、DEL 分批、seed 解析與空面、合成面外之登記與已內建之結構性登記兩模式不擋／"
                 "登記檔缺席壞形、合成射程內登記項壞形（缺 detail／id／kind）兩模式 rc 2 指名零呼叫（射程外壞形不餵不擋）、"
                 "預設左源＝真凍結 seed ⊕ 真演進帳與 --user／--db；seed 模式寫面逐字＋清理面只 setval 非 runtime-append 序列、"
                 "seed 模式前置拒跑零寫入（清理面登記拒跑）、seed 模式走真凍結 seed；上界與鍵集兩欄（空表上界 0、鍵集排序、v1 拒收、壞形）＋"
                 "diff 比兩欄、③b 角色／選單／使用者域寫面逐字＋次序＋值自基準現讀＋空鍵集形、安全帶不攔有列之該面、"
                 "基準上界高於序列即拒零呼叫＋snapshot 告警＋seed 模式可收、"
                 "重啟句字面與出現（只刪列／只改序列兩腿各自成案、序列腿前進／後退／is_called 異三形、兩腿參照值＝目標上界／"
                 "目標序列值各自區辨）／不出現、seed 模式該面目標自凍結 seed 與受損／缺段、該域六表登記入合成不拒跑；檔形 v3 兩欄（v2 拒收、"
                 "欄形一正多反、時間欄兩料源正規化、diff 逐列逐欄）、授權列回補排在刪上界列之後之序釘、回補句與角色列回寫句字面、"
                 "只有回補時之重啟句、真凍結 seed 兩段解析與受損、seed 模式收尾判準含兩欄（授權列就地改寫／角色列被刪＝rc 1 指名）、"
                 "seed 授權列被撤＋新 id 回插＋seed 角色列被改之合成案兩模式 diff 歸零；檔形 v4 兩欄（v3 拒收且指名不載遷移帳、"
                 "欄名冊與遮蔽名冊釘值、單句撈取、欄形一正多反、diff 遷移帳兩向與使用者列逐欄、password 只報不等且遮蔽）、"
                 "snapshot 遷移帳對 repo 清單告警（兩向、解析失敗）rc 0、repo migration 清單解析（單行／折行兩形、註解項不計、"
                 "零命中／殘餘／名形／重複／mod 缺／.rs 缺／檔缺席、真 repo＝實檔主幹集）、使用者域回基準（指派回補、新帳號列與指派刪除、"
                 "序列回值、seed 帳號欄值寫回、經手表與 cpwd 清除；寫句逐字＝固定序）、基準內帳號被軟刪之寫回與指派回補、"
                 "遷移帳前置兩向 rc 2 只讀一句零寫入＋撈取壞形、交易失敗訊息剔除 SQL 回顯、遮蔽失敗列值片段與整值替換目標態密碼（三層各有樁形）、seed 使用者域解析與受損訊息不引列文、"
                 "seed 指派對被刪＝回補 rc 0、sys_user 多一列＝刪列 rc 0；演進合成〔schema-gate 同一合成鏈：載入失敗 rc 2 原訊息照轉、"
                 "射程名冊與單一來源釘值、只餵合成面＝不濾於合成面全等、docsync 帳號投影三節交叉對賬、真凍結 seed ⊕ 真演進帳可解且上界不高於"
                 "序列〕、seed 模式 m0003 九筆形合成目標（列 44 不在／164 在／58～63 受保護／序列 (164, true)、殘列清除收尾 rc 0、凍結 163／"
                 "合成上界 164）、拆共用鏈序號推進＝上界前置拒跑、system_settings 增改刪合成兩模式不報差、repo↔現庫遷移同步前置（兩向 rc 2 "
                 "只讀一句、清單不可解零呼叫、基準檔模式指名未套用而非值差、合成射程外之登記不驗）、合成面未內建之 add_column 兩形兩模式 "
                 "rc 2 帶 GateError 原文零呼叫、seed 模式收尾判準含使用者域）")
            return RC_OK
        return RC_DIFF
    if cmd in ("snapshot", "diff", "restore"):
        seed_mode = cmd == "restore" and argv[2:3] == ["--seed"]
        if not seed_mode and (len(argv) < 3 or argv[2].startswith("--")):
            return usage(f"{cmd} 需要 <檔> 位置引數（無隱含預設落點；restore 另可改帶 --seed）")
        opts, err = _parse_opts(argv[3:])
        if err:
            return usage(err)
        user, db = opts
        try:
            if cmd == "snapshot":
                return cmd_snapshot(argv[2], user, db, run)
            if cmd == "restore":
                return cmd_restore(None if seed_mode else argv[2], user, db, run)
            return cmd_diff(argv[2], user, db, run)
        except BaselineError as ex:
            _say(f"[walkthrough-baseline] ✗ 環境或結構異常：{ex}", err=True)
            return RC_ENV
    return usage(f"未知子命令：{cmd}")


# ── self-test（離線、subprocess 全樁、零 docker）──────────────────────────────

FAKE_TABLES = {"sys_user": 3, "sys_token": 0, "seaql_migrations": 7}
FAKE_SEQS = {"sys_user_id_seq": (3, "t"), "sys_token_id_seq": (1, "f")}
FAKE_KEYS = ["session:sid-a:last_activity", "session:denylist:sid-b", "throttle:unlock:user:x",
             "plainkey"]
# 角色／選單／使用者域樁（005 刀 U15；007 刀 U1 擴 sys_user）：五表之 id 集＋指派鍵集，形同凍結 seed（3／78／163／0／3 列、指派 3 對）。
# 表名手寫、不自受測常數衍生。
STUB_BOUNDED_IDS = {"sys_role": tuple(range(1, 4)), "sys_menu": tuple(range(1, 79)),
                    "casbin_rule": tuple(range(1, 164)), "sys_casbin_policy_archive": (), "sys_user": tuple(range(1, 4))}
STUB_USER_ROLES = ((1, 1), (2, 2), (3, 3))
# 檔形 v4 之遷移帳樁（_snap 用；_StubRun 之預設另取真 repo 清單＝現庫與 repo 同步之健康態）
STUB_MIGRATIONS = ("m0001_baseline_schema", "m0002_baseline_seeds")
# 授權列全欄與角色列可變欄樁（006 刀 U15、T072）：形同凍結 seed（casbin_rule 163 列、sys_role 3 列）；欄名與值手寫、不自受測常數衍生。
# 時間欄三形：樁之 pg 現況撈取＝json 輸出形（STUB_TS_JSON）、樁之凍結 seed＝COPY 文字形（STUB_TS_COPY）；兩者於工具正規化後同值
# （正規形＝UTC isoformat、本值下恰與 json 輸出形同字）。
STUB_TS_JSON = "2026-08-05T00:00:00+00:00"
STUB_TS_COPY = "2026-08-05 00:00:00+00"
STUB_CASBIN_COLUMNS = ("id", "ptype", "v0", "v1", "v2", "v3", "v4", "v5", "protected", "created_at", "created_by")
STUB_ROLE_MUTABLE = ("role_home", "status", "role_name", "role_desc", "role_memo", "updated_at", "updated_by")
STUB_ROLE_ROWS = {
    1: {"role_home": "home", "status": 1, "role_name": "超級管理員", "role_desc": None, "role_memo": None,
        "updated_at": None, "updated_by": None},
    2: {"role_home": "home", "status": 1, "role_name": "管理員", "role_desc": None, "role_memo": "備註",
        "updated_at": None, "updated_by": None},
    3: {"role_home": "home", "status": 1, "role_name": "普通用戶", "role_desc": "it's 描述", "role_memo": None,
        "updated_at": None, "updated_by": None},
}


def _stub_pw(i):
    """樁密碼雜湊欄值：非 PHC 形之合成佔位字面（RL-0054；免撞機密樣式掃描）。"""
    return f"樁雜湊佔位{i}"


# 使用者列可變欄樁（007 刀 U1、T005／T006）：形同凍結 seed 三帳號（暱稱、狀態、會話政策同真檔；密碼欄＝_stub_pw）；欄名與值手寫、
# 不自受測常數衍生。帳號 2 之記事帶單引號（驗字面跳脫）。
STUB_USER_MUTABLE = ("nick_name", "user_gender", "user_phone", "user_email", "status", "session_policy", "user_memo",
                     "password", "updated_at", "updated_by", "deleted_at", "deleted_by")
STUB_USER_NAMES = {1: "Super", 2: "Admin", 3: "User"}


def _stub_user_row(i):
    """樁 sys_user 第 i 列之可變欄（1～3＝seed 三帳號形；其餘＝走查新建帳號形）。"""
    nick = {1: "Super", 2: "Admin", 3: "User01"}.get(i, f"走查帳號{i}")
    return {"nick_name": nick, "user_gender": None, "user_phone": None, "user_email": None, "status": 1,
            "session_policy": "inherit", "user_memo": "o'memo" if i == 2 else None, "password": _stub_pw(i),
            "updated_at": None, "updated_by": None, "deleted_at": None, "deleted_by": None}


STUB_USER_ROWS = {i: _stub_user_row(i) for i in (1, 2, 3)}


def _stub_casbin_row(i, ts=STUB_TS_JSON):
    """樁 casbin_rule 第 i 列全欄：身分鍵 (ptype, v0～v5) 逐 id 相異＝不撞唯一鍵；第 7 列 v1 帶單引號（驗字面跳脫）、
    第 10／11 列受保護。"""
    return {"id": i, "ptype": "p", "v0": "R_SUPER", "v1": "/stub/o'api7" if i == 7 else f"/stub/api{i}",
            "v2": "GET", "v3": "", "v4": "", "v5": "", "protected": i in (10, 11), "created_at": ts,
            "created_by": None}


def _stub_role_row(i):
    """樁 sys_role 第 i 列之可變欄（1～3＝STUB_ROLE_ROWS；其餘＝走查新建角色形）。"""
    return dict(STUB_ROLE_ROWS.get(i) or {"role_home": "home", "status": 1, "role_name": f"走查角色{i}",
                                          "role_desc": None, "role_memo": None, "updated_at": None,
                                          "updated_by": None})


def _t_lit(v):
    """測試側寫句字面（手寫、不呼叫受測之字面函式）。"""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return "'" + v.replace("'", "''") + "'"


def _t_casbin_insert(rows):
    """回補句之測試側期望（欄序手寫）。"""
    return ("INSERT INTO casbin_rule (id, ptype, v0, v1, v2, v3, v4, v5, protected, created_at, created_by) VALUES "
            + ", ".join("(" + ", ".join(_t_lit(r[c]) for c in STUB_CASBIN_COLUMNS) + ")" for r in rows)
            + " ON CONFLICT DO NOTHING;")


def _t_role_update(i, r):
    """角色列回寫句之測試側期望（欄序手寫）。"""
    return ("UPDATE sys_role SET " + ", ".join(f"{c} = {_t_lit(r[c])}" for c in STUB_ROLE_MUTABLE)
            + f" WHERE id = {i} AND ({', '.join(STUB_ROLE_MUTABLE)}) IS DISTINCT FROM ("
            + ", ".join(_t_lit(r[c]) for c in STUB_ROLE_MUTABLE) + ");")


def _t_user_update(i, r):
    """使用者列回寫句之測試側期望（欄序手寫）。"""
    return ("UPDATE sys_user SET " + ", ".join(f"{c} = {_t_lit(r[c])}" for c in STUB_USER_MUTABLE)
            + f" WHERE id = {i} AND ({', '.join(STUB_USER_MUTABLE)}) IS DISTINCT FROM ("
            + ", ".join(_t_lit(r[c]) for c in STUB_USER_MUTABLE) + ");")


def _t_user_role_insert(pairs):
    """指派回補句之測試側期望（手寫）。"""
    return ("INSERT INTO sys_user_role (user_id, role_id) VALUES " + ", ".join(f"({u}, {r})" for u, r in pairs)
            + " ON CONFLICT DO NOTHING;")


def _t_copy(v):
    """測試側 COPY 文字（樁值不含 tab／換行／反斜線、故不跳脫）。"""
    if v is None:
        return "\\N"
    if isinstance(v, bool):
        return "t" if v else "f"
    return str(v)


class _StubSqlError(Exception):
    """樁交易句失敗（模擬 pg 錯誤＝整筆回滾）。"""


_STUB_TOKEN = re.compile(r"\s*('(?:[^']|'')*'|-?\d+|[A-Za-z_]\w*|[(),=])")


def _stub_tokens(text):
    out, pos, text = [], 0, text.strip()
    while pos < len(text):
        m = _STUB_TOKEN.match(text, pos)
        if not m:
            raise _StubSqlError(f"樁解析不了：{text[pos:pos + 40]!r}")
        out.append(m.group(1))
        pos = m.end()
    return out


def _stub_value(tok):
    if tok.startswith("'"):
        return tok[1:-1].replace("''", "'")
    if re.fullmatch(r"-?\d+", tok):
        return int(tok)
    if tok in ("true", "false"):
        return tok == "true"
    if tok == "NULL":
        return None
    raise _StubSqlError(f"樁不認得之值：{tok!r}")


def _stub_tuples(text):
    """`(v, v), (v, v)` → [(值…), …]。"""
    rows, cur = [], None
    for tok in _stub_tokens(text):
        if tok == "(":
            cur = []
        elif tok == ")":
            rows.append(tuple(cur))
            cur = None
        elif tok != ",":
            cur.append(_stub_value(tok))
    return rows


def _stub_split_sql(sql):
    """交易文字 → 逐句（以引號外之分號切）。"""
    out, cur, quoted = [], [], False
    for ch in sql:
        if ch == "'":
            quoted = not quoted
        if ch == ";" and not quoted:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        out.append("".join(cur).strip())
    return out


def _completed(argv, rc, stdout="", stderr=""):
    return subprocess.CompletedProcess(argv, rc, stdout, stderr)


class _StubRun:
    """樁 subprocess.run：依 argv 分流 psql（依 SQL 內容）／redis（依命令）；記錄每次 argv。
    restore 路徑另模擬寫面：交易句逐句依序套用（DELETE／setval／審計 UPDATE／授權列回補 INSERT〔衝突面＝主鍵與身分鍵、
    無 ON CONFLICT DO NOTHING 即失敗〕／指派回補 INSERT〔衝突面＝主鍵；外鍵＝帳號與角色須在〕／角色列與使用者列回寫 UPDATE
    〔IS DISTINCT FROM 判〕；刪仍被指派引用之角色列或帳號列＝外鍵 RESTRICT 失敗）、任一句失敗＝整筆回滾；DEL 刪樁內鍵——
    收尾 diff 因此對著「被 restore 改過的樁」算，rc 0／1 皆真實走過、句序即語意序。"""

    def __init__(self, tables=None, seqs=None, keys=None, dbsize=None, fail=None, garble=None,
                 truncate=None, settings=None, subs=1, ids=None, user_roles=None, migrations=None):
        self.tables = dict(FAKE_TABLES if tables is None else tables)
        self.seqs = dict(FAKE_SEQS if seqs is None else seqs)
        self.keys = list(FAKE_KEYS if keys is None else keys)
        # 角色／選單／使用者域五表之 id 集與指派鍵集（SQL_BOUND_FACES／SQL_CASBIN_STATE 依此回；交易之上界刪除、鍵集差刪除與回補改之）
        self.ids = {t: list(v) for t, v in (STUB_BOUNDED_IDS if ids is None else ids).items()}
        self.user_roles = [tuple(k) for k in (STUB_USER_ROLES if user_roles is None else user_roles)]
        # 授權列、角色列與使用者列之內容覆寫（id → 列）；未覆寫之 id 取 _stub_casbin_row／_stub_role_row／_stub_user_row
        # （列之存在與否仍以 self.ids 為準）
        self.casbin, self.roles, self.users = {}, {}, {}
        # 現庫遷移帳（v4）：預設＝真 repo migration 清單（現庫與 repo 同步之健康態）；不同步形由各案顯式給
        self.migrations = list(repo_migrations() if migrations is None else migrations)
        self._dbsize = dbsize       # None＝隨現存鍵數（DEL 後同步變小）
        self.settings = [dict(s) for s in (settings or [])]
        self.subs = subs            # PUBLISH 回報之訂閱者數（門鈴腿；0＝無 watcher 在訂）
        # "psql"／"redis"＝該支非零退出；"tx"＝交易句失敗；"tx_echo"＝交易句失敗且 stderr 回顯所送 SQL（psql 帶位置錯誤之 LINE 形）、
        # 失敗列值（DETAIL Failing row contains 形、密碼欄為截斷片段）與引所送語句之 CONTEXT 行；"del"＝DEL 回非整數
        self.fail = fail
        # "tables"／"seqs"／"settings"／"bounds"／"casbin"／"migrations"＝該面回不可解輸出（缺欄／非整數／非 JSON／非清單）
        self.garble = garble
        self.truncate = truncate    # "tables"／"seqs"＝該面值腿少回一列（輸出被截斷／撈取不完整）
        self.log = []

    def casbin_row(self, i):
        return dict(self.casbin.get(i) or _stub_casbin_row(i))

    def role_row(self, i):
        return dict(self.roles.get(i) or _stub_role_row(i))

    def user_row(self, i):
        return dict(self.users.get(i) or _stub_user_row(i))

    def _run_tx(self, argv, sql):
        """交易句逐句依序套用；任一句失敗＝狀態還原（整筆回滾）、回 rc 3。"""
        names = ("tables", "seqs", "ids", "user_roles", "casbin", "roles", "users", "settings")
        saved = copy.deepcopy([getattr(self, n) for n in names])
        try:
            for stmt in _stub_split_sql(sql):
                self._apply(stmt)
        except _StubSqlError as ex:
            for n, v in zip(names, saved):
                setattr(self, n, v)
            return _completed(argv, 3, "", f"ERROR:  {ex}")
        return _completed(argv, 0, "COMMIT\n", "")

    def _drop_ids(self, table, gone):
        # 外鍵 RESTRICT（sys_user_role → sys_user、sys_role）：刪仍被指派引用之列＝失敗
        side = {"sys_user": 0, "sys_role": 1}.get(table)
        if side is not None and any(k[side] in gone for k in self.user_roles):
            raise _StubSqlError(f"update or delete on table \"{table}\" violates foreign key constraint")
        self.ids[table] = [i for i in self.ids.get(table, []) if i not in gone]
        if table in self.tables:
            self.tables[table] -= len(gone)
        store = {"casbin_rule": self.casbin, "sys_role": self.roles, "sys_user": self.users}.get(table, {})
        for i in gone:
            store.pop(i, None)

    def _apply(self, stmt):
        """單句寫句之最小模擬（不認得者＝失敗：寫面多一種句形即紅）。"""
        if stmt in ("BEGIN", "COMMIT") or stmt == "UPDATE sys_user SET session_id = NULL WHERE session_id IS NOT NULL":
            return
        if stmt == ("UPDATE system_settings SET updated_at = NULL, updated_by = NULL "
                    "WHERE updated_at IS NOT NULL OR updated_by IS NOT NULL"):
            for s in self.settings:
                s["stamped"] = False
            return
        m = re.fullmatch(r"DELETE FROM (\w+)", stmt)
        if m:
            t = m.group(1)
            if t in self.ids:
                self._drop_ids(t, set(self.ids[t]))
            self.tables[t] = 0
            if t == "sys_user_role":
                self.user_roles = []
            return
        m = re.fullmatch(r"DELETE FROM sys_user_role WHERE \(user_id, role_id\) NOT IN \(VALUES (.*)\)", stmt)
        if m:
            keep = set(_stub_tuples(m.group(1)))
            gone = [k for k in self.user_roles if k not in keep]
            self.user_roles = [k for k in self.user_roles if k in keep]
            self.tables["sys_user_role"] = self.tables.get("sys_user_role", 0) - len(gone)
            return
        m = re.fullmatch(r"DELETE FROM (\w+) WHERE id > (\d+)", stmt)
        if m:
            self._drop_ids(m.group(1), {i for i in self.ids.get(m.group(1), []) if i > int(m.group(2))})
            return
        m = re.fullmatch(r"SELECT setval\('(\w+)', (\d+), (true|false)\)", stmt)
        if m:
            self.seqs[m.group(1)] = (int(m.group(2)), "t" if m.group(3) == "true" else "f")
            return
        m = re.fullmatch(r"INSERT INTO casbin_rule \(([^)]*)\) VALUES (.*?)( ON CONFLICT DO NOTHING)?", stmt, re.S)
        if m:
            cols = [c.strip() for c in m.group(1).split(",")]
            ident = lambda r: tuple(r[c] for c in ("ptype", "v0", "v1", "v2", "v3", "v4", "v5"))  # noqa: E731
            taken = {ident(self.casbin_row(i)) for i in self.ids["casbin_rule"]}
            for tup in _stub_tuples(m.group(2)):
                row = dict(zip(cols, tup))
                if row["id"] in self.ids["casbin_rule"] or ident(row) in taken:
                    if not m.group(3):
                        raise _StubSqlError("duplicate key value violates unique constraint")
                    continue
                self.ids["casbin_rule"] = sorted(self.ids["casbin_rule"] + [row["id"]])
                self.casbin[row["id"]] = row
                self.tables["casbin_rule"] = self.tables.get("casbin_rule", 0) + 1
                taken.add(ident(row))
            return
        m = re.fullmatch(r"INSERT INTO sys_user_role \(user_id, role_id\) VALUES (.*?)( ON CONFLICT DO NOTHING)?",
                         stmt, re.S)
        if m:
            for pair in _stub_tuples(m.group(1)):
                if pair in self.user_roles:
                    if not m.group(2):
                        raise _StubSqlError("duplicate key value violates unique constraint \"sys_user_role_pkey\"")
                    continue
                if pair[0] not in self.ids.get("sys_user", []) or pair[1] not in self.ids.get("sys_role", []):
                    raise _StubSqlError("insert or update on table \"sys_user_role\" violates foreign key constraint")
                self.user_roles.append(pair)
                self.tables["sys_user_role"] = self.tables.get("sys_user_role", 0) + 1
            return
        m = re.fullmatch(r"UPDATE (sys_role|sys_user) SET (.*) WHERE id = (\d+) AND \(([^)]*)\) IS DISTINCT FROM \((.*)\)",
                         stmt, re.S)
        if m:
            table, store, read = m.group(1), *{"sys_role": (self.roles, self.role_row),
                                               "sys_user": (self.users, self.user_row)}[m.group(1)]
            toks = _stub_tokens(m.group(2))
            sets = {toks[k]: _stub_value(toks[k + 2]) for k in range(0, len(toks), 4) if toks[k + 1] == "="}
            cols = [c.strip() for c in m.group(4).split(",")]
            want = _stub_tuples("(" + m.group(5) + ")")[0]
            i = int(m.group(3))
            if i in self.ids.get(table, []):
                cur = read(i)
                if tuple(cur[c] for c in cols) != want:
                    cur.update(sets)
                    store[i] = cur
            return
        raise _StubSqlError(f"樁不認得之寫句：{stmt[:80]!r}")

    def __call__(self, argv, **_kw):
        self.log.append(list(argv))
        if "psql" in argv:
            if self.fail == "psql":
                return _completed(argv, 2, "", "psql: error: connection refused")
            sql = argv[-1]
            if sql == SQL_TABLES:
                out = "\n".join(sorted(self.tables))
            elif sql == SQL_SEQUENCES:
                out = "\n".join(sorted(self.seqs))
            elif sql == SQL_SETTINGS:
                if self.garble == "settings":
                    return _completed(argv, 0, "not json\n", "")
                return _completed(argv, 0, json.dumps(self.settings, ensure_ascii=False) + "\n", "")
            elif sql.startswith("BEGIN;"):
                if self.fail == "tx":
                    return _completed(argv, 3, "", "ERROR:  simulated failure")
                if self.fail == "tx_echo":                       # psql 對帶位置之錯誤回顯錯誤點附近之 SQL 窗口＋失敗列值
                    # 三層遮蔽各有樁形可打：LINE 形回顯（剔行層）；失敗列＝新列值、PG 對逾 64 位元組之值截斷並附「...」＝目標值片段
                    # （樁取目標值前 4 字＋...：非目標值之超字串、整值替換遮不到＝只有失敗列遮蔽層擋得住）；CONTEXT 行引所送語句＝
                    # 目標值全文、非回顯形亦非失敗列形（只有整值替換層擋得住）。目標值＝_stub_pw(2)（基準取於弄髒之前）。
                    row = ", ".join(str(v) for v in dict(self.user_row(2), password=_stub_pw(2)[:4] + "...").values())
                    at = sql.index("UPDATE sys_user SET nick_name")
                    return _completed(argv, 3, "", f"ERROR:  column \"x\" does not exist\nLINE 1: ...{sql[at:at + 240]}...\n"
                                                   f"                ^\nDETAIL:  Failing row contains (2, {row}).\n"
                                                   f"CONTEXT:  SQL statement \"UPDATE sys_user SET password = '{_stub_pw(2)}' "
                                                   "WHERE id = 2\"\n")
                return self._run_tx(argv, sql)
            elif sql == SQL_IP_RULE_ROWS:
                return _completed(argv, 0, json.dumps([{"n": self.tables.get("sys_ip_rule", 0)}]) + "\n", "")
            elif sql == SQL_MIGRATIONS:
                if self.garble == "migrations":
                    return _completed(argv, 0, json.dumps({"version": 1}) + "\n", "")
                return _completed(argv, 0, json.dumps(self.migrations) + "\n", "")
            elif sql == SQL_BOUND_FACES:
                if self.garble == "bounds":
                    return _completed(argv, 0, json.dumps({"id_bounds": {"sys_role": "3"}}) + "\n", "")
                return _completed(argv, 0, json.dumps({
                    "id_bounds": {t: max(v, default=0) for t, v in self.ids.items()},
                    "user_role_keys": [list(k) for k in sorted(self.user_roles)],
                    "casbin_rule_rows": [self.casbin_row(i) for i in sorted(self.ids.get("casbin_rule", []))],
                    "sys_role_rows": [dict({"id": i}, **self.role_row(i))
                                      for i in sorted(self.ids.get("sys_role", []))],
                    "sys_user_rows": [dict({"id": i}, **self.user_row(i))
                                      for i in sorted(self.ids.get("sys_user", []))],
                    "migrations": list(self.migrations)},
                    ensure_ascii=False) + "\n", "")
            elif sql == SQL_CASBIN_STATE:
                if self.garble == "casbin":
                    return _completed(argv, 0, json.dumps({"max_id": 1}) + "\n", "")
                v, called = self.seqs.get("casbin_rule_id_seq", (1, "f"))
                ids = sorted(self.ids.get("casbin_rule", []))
                return _completed(argv, 0, json.dumps({
                    "max_id": max(ids, default=0), "ids": "1" if self.garble == "casbin_ids" else ids,
                    "seq": {"last_value": v, "is_called": called == "t"}}) + "\n", "")
            elif "count(*)" in sql:
                if self.garble == "tables":
                    return _completed(argv, 0, "sys_user\n", "")           # 缺列數欄
                items = sorted(self.tables.items())
                out = "\n".join(f"{n}{PSQL_SEP}{c}"
                                for n, c in (items[:-1] if self.truncate == "tables" else items))
            else:
                if self.garble == "seqs":
                    return _completed(argv, 0, f"sys_user_id_seq{PSQL_SEP}?{PSQL_SEP}t\n", "")
                items = sorted(self.seqs.items())
                out = "\n".join(f"{n}{PSQL_SEP}{v[0]}{PSQL_SEP}{v[1]}"
                                for n, v in (items[:-1] if self.truncate == "seqs" else items))
            return _completed(argv, 0, out + "\n", "")
        if self.fail == "redis":
            return _completed(argv, 1, "", "NOAUTH Authentication required.")
        cmd = argv[-1]
        if cmd.endswith(" DBSIZE"):
            size = len(self.keys) if self._dbsize is None else self._dbsize
            return _completed(argv, 0, f"{size}\n", "")
        if " PUBLISH " in cmd:
            return _completed(argv, 0, f"{self.subs}\n", "")
        if " DEL " in cmd:
            if self.fail == "del":
                return _completed(argv, 0, "ERR simulated\n", "")
            names = shlex.split(cmd.split(" DEL ", 1)[1])
            hit = sum(1 for k in names if k in self.keys)
            self.keys = [k for k in self.keys if k not in names]
            return _completed(argv, 0, f"{hit}\n", "")
        if " --scan --pattern " in cmd:
            pattern = shlex.split(cmd.split(" --scan --pattern ", 1)[1])[0]
            stem = pattern[:-1] if pattern.endswith("*") else pattern
            return _completed(argv, 0, "".join(k + "\n" for k in self.keys if k.startswith(stem)), "")
        return _completed(argv, 0, "".join(k + "\n" for k in self.keys), "")


def _snap(**over):
    """合成基準 dict（可覆寫任一面）。"""
    base = {"schema_version": SCHEMA_VERSION, "taken_at": "2026-08-30T00:00:00Z",
            "tables": {"sys_user": 3, "sys_token": 0},
            "sequences": {"sys_user_id_seq": {"last_value": 3, "is_called": True}},
            "redis": {"dbsize": 2, "prefixes": {"session": 2}},
            "id_bounds": {"sys_role": 3, "sys_menu": 78, "casbin_rule": 163, "sys_casbin_policy_archive": 0,
                          "sys_user": 3},
            "user_role_keys": [[1, 1], [2, 2], [3, 3]],
            "casbin_rule_rows": [_stub_casbin_row(i) for i in range(1, 164)],
            "sys_role_rows": [dict({"id": i}, **STUB_ROLE_ROWS[i]) for i in (1, 2, 3)],
            "sys_user_rows": [dict({"id": i}, **STUB_USER_ROWS[i]) for i in (1, 2, 3)],
            "migrations": list(STUB_MIGRATIONS)}
    base.update(over)
    return base


class TestDiffPure(unittest.TestCase):
    """diff 純函式六形：全等／列數差／表多／表少／序列差／redis 前綴差（＋taken_at 忽略）。"""

    def test_equal_snapshots_yield_no_rows_and_ignore_taken_at(self):
        a, b = _snap(), _snap(taken_at="2026-08-30T23:59:59Z")
        self.assertEqual(diff_snapshots(a, b), [])

    def test_row_count_drift(self):
        rows = diff_snapshots(_snap(), _snap(tables={"sys_user": 3, "sys_token": 2}))
        self.assertEqual(rows, [{"face": "表", "name": "sys_token", "base": 0, "live": 2,
                                 "delta": 2}])

    def test_extra_table_in_live(self):
        rows = diff_snapshots(_snap(), _snap(tables={"sys_user": 3, "sys_token": 0, "tmp_x": 1}))
        self.assertEqual([(r["name"], r["base"], r["live"], r["delta"]) for r in rows],
                         [("tmp_x", "（無）", 1, "—")])

    def test_missing_table_in_live(self):
        rows = diff_snapshots(_snap(), _snap(tables={"sys_user": 3}))
        self.assertEqual([(r["face"], r["name"], r["base"], r["live"]) for r in rows],
                         [("表", "sys_token", 0, "（無）")])

    def test_sequence_drift_last_value_and_is_called(self):
        live = _snap(sequences={"sys_user_id_seq": {"last_value": 4, "is_called": True}})
        rows = diff_snapshots(_snap(), live)
        self.assertEqual(rows, [{"face": "序列", "name": "sys_user_id_seq",
                                 "base": "last_value=3,is_called=t",
                                 "live": "last_value=4,is_called=t", "delta": 1}])
        live = _snap(sequences={"sys_user_id_seq": {"last_value": 3, "is_called": False}})
        self.assertEqual(len(diff_snapshots(_snap(), live)), 1)   # 只差 is_called 也算差

    def test_runtime_append_sequences_compare_by_existence_only(self):
        """★runtime-append 五表之 id 序列只比存在性、不比值（同 tools/schema-gate.py gate2 對其 setval 值正規化之口徑）：
        這五支序列在測試與走查中只進不退（rust-api 測試守衛只清自寫列、序列不復位），逐值比＝每跑一次全量測試
        diff 即恆紅、「rc 0 才算環境已還原」失去判別力。三腿：①五支值皆不同→全等 ②其一於現況或基準缺席→有差
        ③名冊外序列（含 sys_ip_rule_id_seq＝業務表、序列值在比對面內）值不同→照報。"""
        names = ("session_event_id_seq", "sys_access_log_id_seq", "sys_login_attempt_id_seq",
                 "sys_operation_log_id_seq", "sys_token_id_seq")

        def seqs(**over):
            got = {s: {"last_value": 1, "is_called": False} for s in names + ("sys_ip_rule_id_seq",)}
            got.update(over)
            return got

        moved = {s: {"last_value": 100 + i, "is_called": True} for i, s in enumerate(names)}
        self.assertEqual(diff_snapshots(_snap(sequences=seqs()), _snap(sequences=seqs(**moved))), [])
        for gone in names:
            short = seqs(**moved)
            del short[gone]
            rows = diff_snapshots(_snap(sequences=seqs()), _snap(sequences=short))
            self.assertEqual([(r["face"], r["name"], r["base"], r["live"], r["delta"]) for r in rows],
                             [("序列", gone, "last_value=1,is_called=f", "（無）", "—")])
            rows = diff_snapshots(_snap(sequences=short), _snap(sequences=seqs()))   # 反向：基準缺、現況有
            self.assertEqual([(r["name"], r["base"], r["live"]) for r in rows],
                             [(gone, "（無）", "last_value=1,is_called=f")])
        live = seqs(sys_ip_rule_id_seq={"last_value": 4, "is_called": True}, **moved)
        rows = diff_snapshots(_snap(sequences=seqs()), _snap(sequences=live))
        self.assertEqual([(r["name"], r["delta"]) for r in rows], [("sys_ip_rule_id_seq", 3)])

    def test_runtime_append_roster_equals_schema_gate_constant(self):
        """名冊對賬：本檔 RUNTIME_APPEND_TABLES 與 tools/schema-gate.py 同名常數逐項相等（連字檔名不可 import、
        故依路徑以 importlib 載入單檔）。schema-gate 擴集而本檔未跟＝新成員序列照舊逐值比、diff 恆紅；本檔多列
        一支＝該序列之值漂移靜默不報——兩向皆由本案指名。另釘 restore 清理面與名冊之關係：五表全在清理面、
        清理面序列扣掉名冊恰剩 seed 模式唯一 setval 者。"""
        path = os.path.join(REPO_ROOT, "tools", "schema-gate.py")
        spec = importlib.util.spec_from_file_location("schema_gate_roster_source", path)
        mod = importlib.util.module_from_spec(spec)
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(mod)
        self.assertTrue(mod.RUNTIME_APPEND_TABLES)                     # 空名冊的相等是假綠
        self.assertEqual(RUNTIME_APPEND_TABLES, mod.RUNTIME_APPEND_TABLES)
        self.assertLessEqual(set(RUNTIME_APPEND_TABLES), set(RESTORE_TABLES))
        self.assertEqual(tuple(s for s in RESTORE_SEQUENCES if s not in RUNTIME_APPEND_TABLES.values()),
                         ("sys_ip_rule_id_seq",))
        self.assertEqual(SEED_SETVAL_SEQUENCES, ("sys_ip_rule_id_seq",))

    def test_redis_prefix_and_dbsize_drift(self):
        live = _snap(redis={"dbsize": 3, "prefixes": {"session": 2, "sample": 1}})
        rows = diff_snapshots(_snap(), live)
        self.assertEqual([(r["face"], r["name"], r["base"], r["live"], r["delta"]) for r in rows],
                         [("redis", "DBSIZE", 2, 3, 1), ("redis", "sample", 0, 1, 1)])

    def test_render_lists_only_diffs_with_summary_line(self):
        live = _snap(tables={"sys_user": 4, "sys_token": 0},
                     redis={"dbsize": 3, "prefixes": {"session": 3}})
        lines = render_diff(diff_snapshots(_snap(), live), live)
        self.assertIn("  表｜sys_user｜3｜4｜1", lines)
        self.assertNotIn("sys_token", "\n".join(lines))
        self.assertTrue(lines[-1].startswith("[walkthrough-baseline] 摘要：表 1 項差／序列 0 項差／"
                                              "redis 2 項差"), msg=lines[-1])
        self.assertIn("✓ 全等（表 2／序列 1／redis 2 鍵、1 前綴）", render_diff([], _snap())[0])


class TestPrefixGrouping(unittest.TestCase):
    def test_prefix_is_segment_before_first_colon_and_colonless_goes_to_no_prefix(self):
        got = group_prefixes(["session:a:b", "session:c", "throttle:unlock:user:x", "plain",
                              "", "  ", "sample:7"])
        self.assertEqual(got, {"session": 2, "throttle": 1, "sample": 1, NO_PREFIX: 1})
        self.assertEqual(group_prefixes([]), {})

    def test_scan_duplicates_are_deduped_before_counting(self):
        """★SCAN 契約只保證「至少一次」（rehash 期間重複回傳同一把鍵）——逐行累加會把一把
        算成多把；走查前後兩次取樣重複度不同時，diff 即報出實際不存在的殘鍵＝假紅，
        而 §9c 步驟 4 的操作者會照著去找一把不存在的殘鍵。"""
        stub = _StubRun(keys=["session:a", "session:a", "session:b", "session:a"], dbsize=2)
        self.assertEqual(snapshot_live(run=stub)["redis"], {"dbsize": 2, "prefixes": {"session": 2}})

    def test_dbsize_is_cross_checked_against_deduped_scan_key_count(self):
        """「DBSIZE 另取以互證」須真的發生（rev5:B-147 條目原話）：不等即出提示——但**不改 rc**
        （取樣間有鍵 TTL 到期屬正常，嚴格相等會偶發不成立、rc 2 即假紅）。"""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            snap = snapshot_live(run=_StubRun(keys=["session:a", "session:b"], dbsize=5))
        self.assertIn("--scan 去重後 2 鍵、DBSIZE 5", err.getvalue())
        self.assertEqual(snap["redis"], {"dbsize": 5, "prefixes": {"session": 2}})
        quiet = io.StringIO()
        with contextlib.redirect_stderr(quiet):
            snapshot_live(run=_StubRun())                    # 相等即靜默
        self.assertEqual(quiet.getvalue(), "")


class TestSnapshotFileAndForm(unittest.TestCase):
    """JSON 往返、基準檔缺席／壞形（`{}`、非 JSON、版本不符、空表面）＝rc 2。"""

    def test_json_round_trip_diffs_empty(self):
        snap = snapshot_live(run=_StubRun(), now=datetime.datetime(2026, 8, 30, 1, 2, 3,
                                                                   tzinfo=datetime.timezone.utc))
        self.assertEqual(snap["taken_at"], "2026-08-30T01:02:03Z")
        self.assertEqual(snap["schema_version"], SCHEMA_VERSION)
        self.assertEqual(snap["tables"], FAKE_TABLES)
        self.assertEqual(snap["sequences"]["sys_token_id_seq"], {"last_value": 1, "is_called": False})
        self.assertEqual(snap["redis"], {"dbsize": 4, "prefixes": {"session": 2, "throttle": 1,
                                                                    NO_PREFIX: 1}})
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "b.json")
            dump_snapshot(snap, path)
            self.assertEqual(diff_snapshots(load_snapshot(path), snap), [])

    def test_missing_and_malformed_baseline_are_env_errors(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(BaselineError):
                load_snapshot(os.path.join(d, "nope.json"))
            for body in ("{}", "not json", "[]", json.dumps(_snap(schema_version=99)),
                         json.dumps(_snap(tables={})), json.dumps(_snap(sequences={})),
                         json.dumps(_snap(tables={"t": "3"})),
                         json.dumps(_snap(redis={"dbsize": 0})),
                         json.dumps(_snap(redis={"dbsize": "5", "prefixes": {}})),
                         json.dumps(_snap(redis={"dbsize": 0, "prefixes": {"session": "2"}})),
                         json.dumps(_snap(sequences={"s": {"last_value": "3",
                                                           "is_called": True}})),
                         json.dumps(_snap(sequences={"s": {"last_value": 3,
                                                           "is_called": "t"}}))):
                path = os.path.join(d, "bad.json")
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(body)
                with self.assertRaises(BaselineError, msg=body):
                    load_snapshot(path)

    def test_incomplete_fetch_is_env_error_not_a_silently_short_baseline(self):
        """★撈取完整性守門（清單 N 個、值腿只回 N-1 列＝psql 輸出被截斷）：不 fail-loud 的話，
        少掉的那張表／那條序列會靜默不進基準檔，走查後 diff 對它恆「全等」＝假綠——與「比對面
        為空」同一家族（空面是全部漏、截斷是部分漏）。兩面各自釘訊息，只拆掉一道也照樣紅。"""
        for face, word in (("tables", "表列數撈取不完整"), ("seqs", "序列撈取不完整")):
            with self.assertRaises(BaselineError, msg=face) as ctx:
                snapshot_live(run=_StubRun(truncate=face))
            self.assertIn(word, str(ctx.exception))

    def test_empty_comparison_face_is_env_error_not_green(self):
        """★零表或零序列＝rc 2（空面的全綠是假綠）——snapshot 與 diff 兩路皆然。"""
        with self.assertRaises(BaselineError):
            snapshot_live(run=_StubRun(tables={}))
        with self.assertRaises(BaselineError):
            snapshot_live(run=_StubRun(seqs={}))
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "b.json")
            dump_snapshot(snapshot_live(run=_StubRun()), path)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = main([PROG, "diff", path], run=_StubRun(tables={}))
            self.assertEqual(rc, RC_ENV)
            self.assertIn("比對面為空", err.getvalue())
        # 零 redis 鍵是合法狀態、不是空面
        self.assertEqual(snapshot_live(run=_StubRun(keys=[]))["redis"],
                         {"dbsize": 0, "prefixes": {}})

    def test_unparsable_psql_output_is_env_error_not_a_bare_traceback(self):
        """★psql -At 輸出不可解（缺欄 IndexError／非整數 ValueError）＝結構異常 rc 2。
        裸 traceback 會讓行程落在 **1＝契約中的「有差」**：走查收尾照 §9c 步驟 4 判 rc 的人
        會把「工具沒讀懂輸出」讀成「環境沒還原」（或反過來把 traceback 當雜訊忽略）
        ——兩種誤讀都在 rev5:L-055／rev5:L-071 的錯誤家族裡。"""
        for garble in ("tables", "seqs"):
            with self.assertRaises(BaselineError, msg=garble):
                snapshot_live(run=_StubRun(garble=garble))
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "b.json")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(main([PROG, "snapshot", path], run=_StubRun(garble="tables")),
                                 RC_ENV)
            self.assertIn("不可解", err.getvalue())
            self.assertFalse(os.path.exists(path))


class TestSnapshotV2(unittest.TestCase):
    """上界與鍵集兩欄（005 刀 U15、T088①；檔形 v2 起）：角色／選單域四表（007 刀 U1 起擴 sys_user＝五表）id 上界欄（max(id)、空表記 0）＋sys_user_role 鍵集欄；
    v1 檔 diff／restore 一律 rc 2 指名重新 snapshot；diff 比對兩新欄。"""

    def test_schema_version_rosters_and_bound_sqls_are_pinned(self):
        """版本、名冊（dict 序＝刪除序）與三句撈取 SQL 逐字釘（006 刀 U15：v3＝撈取句另帶授權列全欄與角色列可變欄、現態句另帶
        casbin_rule 現況 id 集；007 刀 U1：v4＝五表上界〔sys_user 居末〕、撈取句另帶使用者列可變欄與遷移帳、遷移帳前置之現讀句）；
        三句皆過唯讀判準。"""
        self.assertEqual(SCHEMA_VERSION, 4)
        self.assertEqual(BOUNDED_TABLES, {"sys_role": "sys_role_id_seq", "sys_menu": "sys_menu_id_seq",
                                          "casbin_rule": "casbin_rule_id_seq",
                                          "sys_casbin_policy_archive": "sys_casbin_policy_archive_id_seq",
                                          "sys_user": "sys_user_id_seq"})
        self.assertEqual(list(BOUNDED_TABLES), ["sys_role", "sys_menu", "casbin_rule", "sys_casbin_policy_archive",
                                                "sys_user"])
        self.assertEqual(USER_ROLE_TABLE, "sys_user_role")
        self.assertEqual(DOMAIN_TABLES, ("sys_role", "sys_menu", "casbin_rule", "sys_casbin_policy_archive", "sys_user",
                                         "sys_user_role"))
        self.assertEqual(SQL_BOUND_FACES,
                         "SELECT json_build_object('id_bounds', json_build_object("
                         "'sys_role', (SELECT COALESCE(max(id), 0) FROM sys_role), "
                         "'sys_menu', (SELECT COALESCE(max(id), 0) FROM sys_menu), "
                         "'casbin_rule', (SELECT COALESCE(max(id), 0) FROM casbin_rule), "
                         "'sys_casbin_policy_archive', (SELECT COALESCE(max(id), 0) FROM sys_casbin_policy_archive), "
                         "'sys_user', (SELECT COALESCE(max(id), 0) FROM sys_user)), "
                         "'user_role_keys', (SELECT COALESCE(json_agg(json_build_array(user_id, role_id) "
                         "ORDER BY user_id, role_id), '[]'::json) FROM sys_user_role), "
                         "'casbin_rule_rows', (SELECT COALESCE(json_agg(json_build_object('id', id, 'ptype', ptype, "
                         "'v0', v0, 'v1', v1, 'v2', v2, 'v3', v3, 'v4', v4, 'v5', v5, 'protected', protected, "
                         "'created_at', created_at, 'created_by', created_by) ORDER BY id), '[]'::json) FROM casbin_rule), "
                         "'sys_role_rows', (SELECT COALESCE(json_agg(json_build_object('id', id, 'role_home', role_home, "
                         "'status', status, 'role_name', role_name, 'role_desc', role_desc, 'role_memo', role_memo, "
                         "'updated_at', updated_at, 'updated_by', updated_by) ORDER BY id), '[]'::json) FROM sys_role), "
                         "'sys_user_rows', (SELECT COALESCE(json_agg(json_build_object('id', id, 'nick_name', nick_name, "
                         "'user_gender', user_gender, 'user_phone', user_phone, 'user_email', user_email, 'status', status, "
                         "'session_policy', session_policy, 'user_memo', user_memo, 'password', password, "
                         "'updated_at', updated_at, 'updated_by', updated_by, 'deleted_at', deleted_at, "
                         "'deleted_by', deleted_by) ORDER BY id), '[]'::json) FROM sys_user), "
                         "'migrations', (SELECT COALESCE(json_agg(version ORDER BY version), '[]'::json) "
                         "FROM seaql_migrations))")
        self.assertEqual(SQL_MIGRATIONS,
                         "SELECT COALESCE(json_agg(version ORDER BY version), '[]'::json) FROM seaql_migrations")
        self.assertEqual(SQL_CASBIN_STATE,
                         "SELECT json_build_object('max_id', (SELECT COALESCE(max(id), 0) FROM casbin_rule), "
                         "'ids', (SELECT COALESCE(json_agg(id ORDER BY id), '[]'::json) FROM casbin_rule), "
                         "'seq', (SELECT json_build_object('last_value', last_value, 'is_called', is_called) "
                         "FROM casbin_rule_id_seq))")
        self.assertEqual(_pg_write_offenders([SQL_BOUND_FACES, SQL_CASBIN_STATE, SQL_MIGRATIONS]), [])

    def test_snapshot_carries_id_bounds_with_empty_table_as_0_and_sorted_user_role_keys(self):
        """★空表之上界定形為 0（非 null）：restore 以 `id > 0` 刪、語意＝走查前空表之新列全清；鍵集依 (user_id, role_id) 排序。"""
        stub = _StubRun(ids={"sys_role": (1, 2, 5), "sys_menu": (1,), "casbin_rule": (1, 2),
                             "sys_casbin_policy_archive": (), "sys_user": (1, 3)}, user_roles=((3, 3), (1, 5), (1, 1)))
        snap = snapshot_live(run=stub)
        self.assertEqual(snap["schema_version"], 4)
        self.assertEqual(snap["id_bounds"], {"sys_role": 5, "sys_menu": 1, "casbin_rule": 2,
                                             "sys_casbin_policy_archive": 0, "sys_user": 3})
        self.assertEqual(snap["user_role_keys"], [[1, 1], [1, 5], [3, 3]])
        self.assertIn(SQL_BOUND_FACES, [a[-1] for a in stub.log if "psql" in a])
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "b.json")
            dump_snapshot(snap, path)
            back = load_snapshot(path)
            self.assertEqual((back["id_bounds"], back["user_role_keys"]), (snap["id_bounds"], snap["user_role_keys"]))
            self.assertEqual(diff_snapshots(back, snap), [])

    def test_v1_baseline_is_refused_rc2_naming_resnapshot_with_zero_docker_calls(self):
        """v1 基準檔（無兩新欄）：diff 與 restore 皆 rc 2、訊息指名重新 snapshot、零 docker 呼叫＝零寫入。"""
        v1 = _snap(schema_version=1)
        del v1["id_bounds"], v1["user_role_keys"], v1["casbin_rule_rows"], v1["sys_role_rows"], v1["sys_user_rows"]
        del v1["migrations"]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "v1.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(v1, fh)
            for cmd in ("diff", "restore"):
                stub, err = _StubRun(), io.StringIO()
                with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main([PROG, cmd, path], run=stub), RC_ENV, msg=cmd)
                self.assertIn("schema_version=1", err.getvalue(), msg=cmd)
                self.assertIn("重新 snapshot", err.getvalue(), msg=cmd)
                self.assertEqual(stub.log, [], msg=cmd)

    def test_malformed_bound_faces_are_env_errors(self):
        """兩新欄壞形（缺欄、表名集不等、值非非負整數、鍵對形錯）＝rc 2；現況撈取輸出壞形亦 rc 2。"""
        good = _snap()
        bad_bounds = (None, [], {"sys_role": 3}, dict(good["id_bounds"], extra=1),
                      dict(good["id_bounds"], sys_role="3"), dict(good["id_bounds"], sys_role=True),
                      dict(good["id_bounds"], sys_role=-1), dict(good["id_bounds"], sys_role=None))
        bad_keys = (None, {}, [[1]], [[1, 2, 3]], [["1", 2]], [[True, 2]], [(1, 2), "x"])
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bad.json")
            for field, values in (("id_bounds", bad_bounds), ("user_role_keys", bad_keys)):
                for v in values:
                    snap = _snap()
                    if v is None:
                        del snap[field]
                    else:
                        snap[field] = v
                    with open(path, "w", encoding="utf-8") as fh:
                        json.dump(snap, fh)
                    with self.assertRaises(BaselineError, msg=(field, v)) as ctx:
                        load_snapshot(path)
                    self.assertIn(field, str(ctx.exception), msg=(field, v))
        with self.assertRaises(BaselineError) as ctx:
            snapshot_live(run=_StubRun(garble="bounds"))
        self.assertIn("id_bounds", str(ctx.exception))

    def test_diff_reports_id_bound_and_user_role_key_drift(self):
        """diff 比對兩新欄：上界差＝一列（附差值）、鍵集差＝逐對一列（現況多＝+1、現況少＝-1）；摘要行附兩面計數。"""
        base = _snap()
        live = _snap(id_bounds=dict(base["id_bounds"], sys_role=4, sys_casbin_policy_archive=2),
                     user_role_keys=[[1, 1], [1, 4], [3, 3]])
        rows = diff_snapshots(base, live)
        self.assertEqual([(r["face"], r["name"], r["base"], r["live"], r["delta"]) for r in rows], [
            ("上界", "sys_casbin_policy_archive", 0, 2, 2), ("上界", "sys_role", 3, 4, 1),
            ("鍵集", "sys_user_role(1,4)", "（無）", "有", 1), ("鍵集", "sys_user_role(2,2)", "有", "（無）", -1)])
        lines = render_diff(rows, live)
        self.assertIn("  上界｜sys_role｜3｜4｜1", lines)
        self.assertIn("  鍵集｜sys_user_role(2,2)｜有｜（無）｜-1", lines)
        self.assertIn("／上界 2 項差／鍵集 2 項差", lines[-1])
        self.assertEqual(diff_snapshots(base, _snap()), [])


class TestSnapshotV3(unittest.TestCase):
    """基準檔形 v3（006 刀 U15、T072①）：另帶授權列全欄（casbin_rule_rows）與角色列可變欄（sys_role_rows）兩欄；v2／v1 舊檔
    diff／restore 一律 rc 2 指名重新 snapshot；validate_snapshot 同驗兩欄之形；時間欄兩料源正規化；diff 逐列逐欄比對兩欄。"""

    def test_v2_baseline_is_refused_rc2_naming_resnapshot_with_zero_docker_calls(self):
        """v2 基準檔（有四表上界與鍵集兩欄、無授權列與角色列兩欄、無 v4 之遷移帳與使用者列）：diff 與 restore 皆 rc 2、訊息指名
        版本、「只認 4」、舊檔形不載遷移帳與重新 snapshot、零 docker 呼叫＝零寫入（以 v2 檔 restore 會漏補被撤之 seed 授權列、漏回寫
        角色列＝不得靜默降級）。v3 檔（006 刀終態檔形）同判、另案釘（TestSnapshotV4）。"""
        v2 = _snap(schema_version=2)
        del v2["casbin_rule_rows"], v2["sys_role_rows"], v2["sys_user_rows"], v2["migrations"], v2["id_bounds"]["sys_user"]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "v2.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(v2, fh)
            for cmd in ("diff", "restore"):
                stub, err = _StubRun(), io.StringIO()
                with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main([PROG, cmd, path], run=stub), RC_ENV, msg=cmd)
                self.assertIn("schema_version=2", err.getvalue(), msg=cmd)
                self.assertIn("只認 4", err.getvalue(), msg=cmd)
                self.assertIn("不載遷移帳", err.getvalue(), msg=cmd)
                self.assertIn("重新 snapshot", err.getvalue(), msg=cmd)
                self.assertEqual(stub.log, [], msg=cmd)

    def test_row_faces_shape_one_positive_many_negatives(self):
        """兩欄形斷言（一正多反）：正＝樁形（含非 NULL 審計欄、微秒時間、NULL 狀態）可讀回；反＝缺欄、非 list、列非物件、
        列缺欄／多欄、各欄型錯（id 字串、非空文字欄 NULL、bool 以 0、時間非正規形或不可解、可空整數欄以 bool）、id 重複、
        id 高於該表上界——皆 rc 2 且訊息指名該欄。"""
        stamped = dict({"id": 2}, **dict(STUB_ROLE_ROWS[2], status=None, updated_by=1,
                                          updated_at="2026-10-04T08:00:00.500000+00:00"))
        good = _snap(sys_role_rows=[dict({"id": 1}, **STUB_ROLE_ROWS[1]), stamped, dict({"id": 3}, **STUB_ROLE_ROWS[3])])
        rows = good["casbin_rule_rows"]
        roles = good["sys_role_rows"]

        def casbin(i=0, **over):
            out = [dict(r) for r in rows]
            out[i].update(over)
            return out

        def role(i=0, **over):
            out = [dict(r) for r in roles]
            out[i].update(over)
            return out

        dropped = [dict(r) for r in rows]
        del dropped[0]["protected"]
        role_dropped = [dict(r) for r in roles]
        del role_dropped[1]["updated_by"]
        bad = (("casbin_rule_rows", None), ("casbin_rule_rows", {}), ("casbin_rule_rows", ["x"]),
               ("casbin_rule_rows", dropped), ("casbin_rule_rows", casbin(v6="")),
               ("casbin_rule_rows", casbin(id="1")), ("casbin_rule_rows", casbin(ptype=None)),
               ("casbin_rule_rows", casbin(protected=0)), ("casbin_rule_rows", casbin(created_at=STUB_TS_COPY)),
               ("casbin_rule_rows", casbin(created_at="yesterday")), ("casbin_rule_rows", casbin(created_by=True)),
               ("casbin_rule_rows", casbin(1, id=1)), ("casbin_rule_rows", casbin(162, id=164)),
               ("sys_role_rows", None), ("sys_role_rows", role_dropped), ("sys_role_rows", role(status="1")),
               ("sys_role_rows", role(role_name=None)), ("sys_role_rows", role(updated_at="2026-10-04 08:00:00")),
               ("sys_role_rows", role(2, id=4)), ("sys_role_rows", role(role_code="R_SUPER")))
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "b.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(good, fh, ensure_ascii=False)
            back = load_snapshot(path)                              # 正
            self.assertEqual((back["casbin_rule_rows"], back["sys_role_rows"]), (rows, roles))
            for field, value in bad:
                snap = _snap(sys_role_rows=roles)
                if value is None:
                    del snap[field]
                else:
                    snap[field] = value
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(snap, fh, ensure_ascii=False)
                with self.assertRaises(BaselineError, msg=(field, str(value)[:120])) as ctx:
                    load_snapshot(path)
                self.assertIn(field, str(ctx.exception), msg=(field, str(value)[:120]))

    def test_timestamps_from_both_sources_are_canonicalised(self):
        """時間欄兩料源字形不同（pg json 輸出形 `…T…+00:00`、COPY 形 `… …+00`）：一律正規化為 UTC isoformat 後才存、比、寫；
        帶非 UTC 時區與小數秒之現況撈取亦同；無時區或不可解＝rc 2。"""
        for text, want in (("2026-08-05 00:00:00+00", "2026-08-05T00:00:00+00:00"),
                           ("2026-08-05T00:00:00+00:00", "2026-08-05T00:00:00+00:00"),
                           ("2026-10-04T16:00:00.5+08:00", "2026-10-04T08:00:00.500000+00:00"),
                           ("2026-10-04 08:00:00.123456-0130", "2026-10-04T09:30:00.123456+00:00"),
                           ("2026-10-04T08:00:00Z", "2026-10-04T08:00:00+00:00")):
            self.assertEqual(_canon_ts(text), want, msg=text)
        for text in ("2026-10-04 08:00:00", "yesterday", "", "2026-13-04 08:00:00+00", None):
            with self.assertRaises(BaselineError, msg=text):
                _canon_ts(text)
        stub = _StubRun()
        stub.roles[2] = dict(STUB_ROLE_ROWS[2], updated_at="2026-10-04T16:00:00.5+08:00", updated_by=1)
        stub.casbin[5] = dict(_stub_casbin_row(5), created_at="2026-10-04T16:00:00+08:00")
        snap = snapshot_live(run=stub)
        self.assertEqual(snap["sys_role_rows"][1]["updated_at"], "2026-10-04T08:00:00.500000+00:00")
        self.assertEqual(snap["casbin_rule_rows"][4]["created_at"], "2026-10-04T08:00:00+00:00")
        stub.roles[2]["updated_at"] = "not a time"
        with self.assertRaises(BaselineError):
            snapshot_live(run=stub)

    def test_diff_reports_row_face_drift_by_row_and_column(self):
        """diff 比對兩欄：上界以內逐列（現況少＝-1、現況多＝+1）、同 id 逐欄（值以 json 字面呈現：字串帶引號、NULL＝null）；
        上界以上之列不入兩欄（歸上界面與列數面）；摘要行附兩欄計數。"""
        base = _snap()
        live_casbin = [r for r in base["casbin_rule_rows"] if r["id"] != 50] + [
            dict(_stub_casbin_row(50), id=164)]
        live_roles = [dict(r) for r in base["sys_role_rows"]]
        live_roles[1].update(role_home="manage_role", updated_by=1)
        live = _snap(casbin_rule_rows=live_casbin, sys_role_rows=live_roles)
        rows = diff_snapshots(base, live)
        self.assertEqual([(r["face"], r["name"], r["base"], r["live"], r["delta"]) for r in rows], [
            ("授權列", "casbin_rule(id=50)", "有", "（無）", -1),
            ("角色列", "sys_role(id=2).role_home", '"home"', '"manage_role"', "—"),
            ("角色列", "sys_role(id=2).updated_by", "null", "1", "—")])
        lines = render_diff(rows, live)
        self.assertIn("／授權列 1 項差／角色列 2 項差", lines[-1])
        extra = _snap(sys_role_rows=base["sys_role_rows"][:2], id_bounds=dict(base["id_bounds"]))
        self.assertEqual([(r["name"], r["base"], r["live"], r["delta"]) for r in diff_snapshots(extra, base)],
                         [("sys_role(id=3)", "（無）", "有", 1)])
        self.assertEqual(diff_snapshots(base, _snap()), [])


def _write_migration_src(root, modules, layout="single", declare=None, files=None, extra=""):
    """合成 migration src 目錄（lib.rs＋各模組 .rs 實檔）→ lib.rs 路徑。layout＝single（單行向量）／multi（rustfmt 折行形、尾逗號）；
    declare／files 預設＝modules（可另給以造「mod 缺」「.rs 缺」）；extra＝接在向量項之後之額外文字（造殘餘或註解項）。"""
    src = os.path.join(root, "src")
    os.makedirs(src, exist_ok=True)
    entries = [f"Box::new({m}::Migration)" for m in modules]
    if layout == "single":
        vec = "vec![" + ", ".join(entries) + extra + "]"
    else:
        vec = "vec![\n" + "".join(f"            {e},\n" for e in entries) + extra + "        ]"
    text = ("pub use sea_orm_migration::prelude::*;\n\n" + "".join(f"mod {m};\n" for m in (
        modules if declare is None else declare)) + "\n/// 後續 delta 依序 append 於本向量（註解內之 Box::new(m0009_doc::Migration) 不計）\n"
            "pub struct Migrator;\n\n#[async_trait::async_trait]\nimpl MigratorTrait for Migrator {\n"
            "    fn migrations() -> Vec<Box<dyn MigrationTrait>> {\n        " + vec + "\n    }\n}\n")
    for m in (modules if files is None else files):
        with open(os.path.join(src, m + ".rs"), "w", encoding="utf-8") as fh:
            fh.write("// 樁\n")
    lib = os.path.join(src, "lib.rs")
    with open(lib, "w", encoding="utf-8") as fh:
        fh.write(text)
    return lib


class TestSnapshotV4(unittest.TestCase):
    """檔形 v4（007 刀 U1、T005）：另帶遷移帳（migrations）與使用者列（sys_user_rows）兩欄、sys_user 入上界面；v3／v2／v1 舊檔
    diff／restore 一律 rc 2 指名「舊檔形不載遷移帳、重新 snapshot」；validate_snapshot 同驗兩新欄之形；diff 增「遷移帳」「使用者列」兩面、
    password 欄只報不等且遮蔽；snapshot 時現庫遷移帳≠repo migration 清單（或清單解析失敗）＝stderr 告警、rc 仍 0。"""

    def test_v3_baseline_is_refused_rc2_naming_resnapshot_with_zero_docker_calls(self):
        """v3 基準檔（006 刀終態檔形：四表上界、鍵集、授權列與角色列；無遷移帳與使用者列）：diff 與 restore 各一發皆 rc 2、訊息指名
        版本、只認 4、舊檔形不載遷移帳（無從判遷移差）與重新 snapshot、樁紀錄零 docker 呼叫＝零寫入。"""
        v3 = _snap(schema_version=3)
        del v3["sys_user_rows"], v3["migrations"], v3["id_bounds"]["sys_user"]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "v3.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(v3, fh)
            for cmd in ("diff", "restore"):
                stub, err = _StubRun(), io.StringIO()
                with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main([PROG, cmd, path], run=stub), RC_ENV, msg=cmd)
                for needle in ("schema_version=3", "只認 4", "不載遷移帳", "無從判遷移差", "重新 snapshot"):
                    self.assertIn(needle, err.getvalue(), msg=(cmd, needle))
                self.assertEqual(stub.log, [], msg=cmd)

    def test_user_row_face_roster_and_mask_are_pinned(self):
        """使用者列欄名冊（欄序＝撈取、寫句與 seed COPY 取欄之欄序）與欄型逐字釘；user_name、建立兩欄、session_id 不在面內；
        面名「使用者列」；遮蔽名冊＝sys_user 之 password、遮蔽字面固定。"""
        self.assertEqual(list(SYS_USER_MUTABLE_COLUMNS.items()), [
            ("nick_name", "text?"), ("user_gender", "int?"), ("user_phone", "text?"), ("user_email", "text?"),
            ("status", "int?"), ("session_policy", "text"), ("user_memo", "text?"), ("password", "text"),
            ("updated_at", "ts?"), ("updated_by", "int?"), ("deleted_at", "ts?"), ("deleted_by", "int?")])
        for c in ("user_name", "created_at", "created_by", "session_id"):
            self.assertNotIn(c, SYS_USER_MUTABLE_COLUMNS)
        self.assertEqual(list(ROW_FACES), ["casbin_rule_rows", "sys_role_rows", "sys_user_rows"])
        self.assertEqual(ROW_FACES["sys_user_rows"], ("sys_user", "使用者列", dict({"id": "int"}, **SYS_USER_MUTABLE_COLUMNS)))
        self.assertEqual(MASKED_COLUMNS, {"sys_user": ("password",)})
        self.assertEqual(MASK, "（遮蔽）")

    def test_snapshot_carries_migrations_and_user_rows_from_the_single_bound_faces_statement(self):
        """新兩欄併入角色／選單域撈取之單句（同一快照、psql 撈取仍恰 5 句）：遷移帳依名排序存檔（撈取序亂亦然）、sys_user 上界、使用者列
        依 id 排序且時間欄正規化；JSON 往返後 diff 全等。"""
        stub = _StubRun(migrations=["m0002_baseline_seeds", "m0001_baseline_schema"])
        stub.users[2] = dict(_stub_user_row(2), updated_at="2026-10-06T16:00:00+08:00", updated_by=1)
        snap = snapshot_live(run=stub)
        self.assertEqual(snap["schema_version"], 4)
        self.assertEqual(snap["migrations"], ["m0001_baseline_schema", "m0002_baseline_seeds"])
        self.assertEqual(snap["id_bounds"]["sys_user"], 3)
        self.assertEqual([r["id"] for r in snap["sys_user_rows"]], [1, 2, 3])
        self.assertEqual(snap["sys_user_rows"][1]["updated_at"], "2026-10-06T08:00:00+00:00")
        sqls = [a[-1] for a in stub.log if "psql" in a]
        self.assertEqual((len(sqls), sqls.count(SQL_BOUND_FACES)), (5, 1))
        self.assertNotIn(SQL_MIGRATIONS, sqls)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "b.json")
            dump_snapshot(snap, path)
            self.assertEqual(diff_snapshots(load_snapshot(path), snap), [])

    def test_new_fields_malformed_are_env_errors_without_printing_password_values(self):
        """新兩欄壞形（一正多反）：migrations 缺欄／非 list／空（比對面為空）／空字串／非字串／未依名排序／重複；sys_user_rows 缺欄／列缺
        password／列多 user_name／password 為 NULL／session_policy 為 NULL／status 字串／user_gender 為 bool／deleted_at 非正規形／id 高於
        上界；id_bounds 缺 sys_user——皆 rc 2 且訊息指名該欄、不含任何密碼欄值；現況撈取之遷移帳為空亦 rc 2。"""
        good = _snap()
        users = good["sys_user_rows"]

        def user(i=0, drop=None, **over):
            out = [dict(r) for r in users]
            out[i].update(over)
            if drop:
                del out[i][drop]
            return out

        bad = (("migrations", None), ("migrations", {}), ("migrations", []), ("migrations", [""]),
               ("migrations", [1]), ("migrations", ["m0002_baseline_seeds", "m0001_baseline_schema"]),
               ("migrations", ["m0001_baseline_schema", "m0001_baseline_schema"]),
               ("sys_user_rows", None), ("sys_user_rows", user(drop="password")), ("sys_user_rows", user(user_name="Super")),
               ("sys_user_rows", user(password=None)), ("sys_user_rows", user(session_policy=None)),
               ("sys_user_rows", user(status="1")), ("sys_user_rows", user(user_gender=True)),
               ("sys_user_rows", user(deleted_at="2026-10-06 08:00:00+00")), ("sys_user_rows", user(2, id=4)),
               ("id_bounds", {k: v for k, v in good["id_bounds"].items() if k != "sys_user"}))
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "b.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(good, fh, ensure_ascii=False)
            self.assertEqual(load_snapshot(path)["sys_user_rows"], users)              # 正
            for field, value in bad:
                snap = _snap()
                if value is None:
                    del snap[field]
                else:
                    snap[field] = value
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(snap, fh, ensure_ascii=False)
                with self.assertRaises(BaselineError, msg=(field, str(value)[:80])) as ctx:
                    load_snapshot(path)
                self.assertIn(field, str(ctx.exception), msg=(field, str(value)[:80]))
                self.assertNotIn("樁雜湊", str(ctx.exception), msg=(field, str(value)[:80]))
        with self.assertRaises(BaselineError) as ctx:
            snapshot_live(run=_StubRun(migrations=[]))
        self.assertIn("migrations", str(ctx.exception))

    def test_diff_reports_migration_ledger_and_user_row_faces_with_password_masked(self):
        """diff 新兩面：「遷移帳」逐版本兩向差（現況多＝+1、現況少＝-1）、「使用者列」同 id 逐欄；★password 欄只報「不等」、基準值與現值
        皆以遮蔽字面呈現——差異列、渲染行與其 json 形皆不含雜湊原文或其片段；摘要行附兩面計數。CLI 一發 rc 1。"""
        base = _snap()
        users = [dict(r) for r in base["sys_user_rows"]]
        users[1].update(nick_name="走查改名", password=_stub_pw(2) + "改", updated_by=1)
        live = _snap(migrations=list(STUB_MIGRATIONS) + ["m0003_seed_button_governance"], sys_user_rows=users)
        rows = diff_snapshots(base, live)
        self.assertEqual([(r["face"], r["name"], r["base"], r["live"], r["delta"]) for r in rows], [
            ("使用者列", "sys_user(id=2).nick_name", '"Admin"', '"走查改名"', "—"),
            ("使用者列", "sys_user(id=2).password", "（遮蔽）", "（遮蔽）", "不等"),
            ("使用者列", "sys_user(id=2).updated_by", "null", "1", "—"),
            ("遷移帳", "m0003_seed_button_governance", "（無）", "有", 1)])
        lines = render_diff(rows, live)
        self.assertIn("  使用者列｜sys_user(id=2).password｜（遮蔽）｜（遮蔽）｜不等", lines)
        self.assertIn("  遷移帳｜m0003_seed_button_governance｜（無）｜有｜1", lines)
        self.assertIn("／角色列 0 項差／使用者列 3 項差／遷移帳 1 項差", lines[-1])
        blob = "\n".join(lines) + json.dumps(rows, ensure_ascii=False)
        self.assertNotIn("樁雜湊", blob)
        self.assertEqual([(r["face"], r["base"], r["live"], r["delta"]) for r in diff_snapshots(live, base)
                          if r["face"] == "遷移帳"], [("遷移帳", "有", "（無）", -1)])
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "b.json")
            dump_snapshot(base, path)
            stub = _StubRun(migrations=live["migrations"])
            stub.users[2] = dict(_stub_user_row(2), password=_stub_pw(2) + "改")
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([PROG, "diff", path], run=stub), RC_DIFF)
            self.assertIn("遷移帳｜m0003_seed_button_governance｜（無）｜有｜1", err.getvalue())
            self.assertIn("使用者列｜sys_user(id=2).password｜（遮蔽）｜（遮蔽）｜不等", err.getvalue())
            self.assertNotIn("樁雜湊", err.getvalue())

    def test_snapshot_warns_on_live_vs_repo_migration_gap_or_parse_failure_and_keeps_rc_0(self):
        """snapshot 時現庫遷移帳≠repo migration 清單＝stderr 告警（逐版本指名 repo 有現庫無＝未套用／現庫有 repo 無）、基準檔照寫、rc 0；
        repo 清單解析失敗＝stderr 告警、rc 0（快照只讀庫況、不因 repo 面失敗而失效）；相等＝不告警。"""
        two, three = list(STUB_MIGRATIONS), list(STUB_MIGRATIONS) + ["m0003_seed_button_governance"]
        with tempfile.TemporaryDirectory() as d:
            lib2 = _write_migration_src(os.path.join(d, "r2"), two)
            lib3 = _write_migration_src(os.path.join(d, "r3"), three, "multi")
            for i, (live, lib, needles) in enumerate((
                    (two, lib3, ("告警", "repo 有現庫無", "未套用", "m0003_seed_button_governance")),
                    (three, lib2, ("告警", "現庫有 repo 無", "m0003_seed_button_governance")),
                    (two, os.path.join(d, "nope", "lib.rs"), ("告警", "解析失敗")),
                    (two, lib2, ()))):
                path = os.path.join(d, f"b{i}.json")
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc = cmd_snapshot(path, DB_USER, DB_NAME, _StubRun(migrations=live), lib_path=lib)
                self.assertEqual(rc, RC_OK, msg=i)
                self.assertIn("基準已寫", out.getvalue(), msg=i)
                self.assertEqual(load_snapshot(path)["migrations"], live, msg=i)
                for needle in needles:
                    self.assertIn(needle, err.getvalue(), msg=(i, needle))
                if not needles:
                    self.assertEqual(err.getvalue(), "", msg=i)


class TestRepoMigrations(unittest.TestCase):
    """repo migration 清單解析器（007 刀 U1；單一函式、snapshot 告警與 restore 前置共用）：lib.rs 之 migrations() 向量內
    Box::new(<模組>::Migration) 依序之模組名；單行與 rustfmt 折行兩形皆解、註解內之項不計；零命中、殘餘、模組名形不符、重複、
    mod 缺、.rs 缺、檔缺席＝rc 2。"""

    def test_single_line_and_multi_line_vector_forms_parse_in_declared_order(self):
        two, three = list(STUB_MIGRATIONS), list(STUB_MIGRATIONS) + ["m0003_seed_button_governance"]
        with tempfile.TemporaryDirectory() as d:
            for i, (layout, mods) in enumerate((("single", two), ("multi", three), ("single", three),
                                                ("multi", list(reversed(three))))):
                self.assertEqual(repo_migrations(_write_migration_src(os.path.join(d, str(i)), mods, layout)), mods,
                                 msg=(layout, mods))
            lib = _write_migration_src(os.path.join(d, "c"), three, "multi",
                                       extra="            // Box::new(m0009_off::Migration),\n")
            self.assertEqual(repo_migrations(lib), three)

    def test_zero_hits_residue_bad_names_duplicates_missing_mod_or_file_are_errors(self):
        two = list(STUB_MIGRATIONS)
        with tempfile.TemporaryDirectory() as d:
            cases = (
                (dict(modules=[]), "零命中"),
                (dict(modules=two, extra=", Box::new(other::path::Migration)"), "不可解"),
                (dict(modules=two + ["m003_short"]), "模組名形"),
                (dict(modules=two + ["M0003_Upper"]), "模組名形"),
                (dict(modules=two + ["m0001_baseline_schema"], declare=two, files=two), "重複"),
                (dict(modules=two, declare=two[:1]), "mod m0002_baseline_seeds;"),
                (dict(modules=two, files=two[:1]), "m0002_baseline_seeds.rs"))
            for i, (kw, needle) in enumerate(cases):
                lib = _write_migration_src(os.path.join(d, str(i)), **kw)
                with self.assertRaises(BaselineError, msg=needle) as ctx:
                    repo_migrations(lib)
                self.assertIn(needle, str(ctx.exception))
            with self.assertRaises(BaselineError) as ctx:
                repo_migrations(os.path.join(d, "nope", "lib.rs"))
            self.assertIn("讀取失敗", str(ctx.exception))
            lib = _write_migration_src(os.path.join(d, "nofn"), two)
            with open(lib, encoding="utf-8") as fh:
                text = fh.read().replace("fn migrations()", "fn other()")
            with open(lib, "w", encoding="utf-8") as fh:
                fh.write(text)
            with self.assertRaises(BaselineError) as ctx:
                repo_migrations(lib)
            self.assertIn("零解析", str(ctx.exception))

    def test_real_repo_list_equals_migration_file_stems_and_is_nonempty(self):
        """真 repo：解析結果＝`rust-api/migration/src/` 之 `m[0-9]{4}_*.rs` 實檔主幹集且非空（未註冊之檔即在此露出）。"""
        got = repo_migrations()
        src = os.path.join(REPO_ROOT, "rust-api", "migration", "src")
        stems = {f[:-3] for f in os.listdir(src) if re.fullmatch(r"m[0-9]{4}_[a-z0-9_]+\.rs", f)}
        self.assertTrue(got)
        self.assertEqual(set(got), stems)
        self.assertEqual(len(got), len(stems))


class TestExitCodes(unittest.TestCase):
    """退出碼四態：0 全等／1 有差／2 環境（docker 不可執行、psql／redis 失敗）／64 用法。"""

    def _baseline(self, d):
        path = os.path.join(d, "b.json")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main([PROG, "snapshot", path], run=_StubRun()), RC_OK)
        self.assertIn("基準已寫", out.getvalue())
        return path

    def test_equal_is_0_and_drift_is_1(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._baseline(d)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(main([PROG, "diff", path], run=_StubRun()), RC_OK)
            self.assertIn("✓ 全等", out.getvalue())
            drift = _StubRun(keys=FAKE_KEYS + ["walkthrough-baseline-selftest:probe"])
            with contextlib.redirect_stderr(err):
                self.assertEqual(main([PROG, "diff", path], run=drift), RC_DIFF)
            text = err.getvalue()
            self.assertIn("redis｜DBSIZE｜4｜5｜1", text)
            self.assertIn("redis｜walkthrough-baseline-selftest｜0｜1｜1", text)   # 前綴缺席＝0 鍵
            self.assertIn("摘要：表 0 項差／序列 0 項差／redis 2 項差", text)

    def test_env_failures_are_2_with_startup_hint(self):
        def no_docker(argv, **_kw):
            raise OSError("[Errno 2] No such file or directory: 'docker'")
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "b.json")
            for run in (no_docker, _StubRun(fail="psql"), _StubRun(fail="redis")):
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    self.assertEqual(main([PROG, "snapshot", path], run=run), RC_ENV)
                self.assertIn(STARTUP_HINT, err.getvalue())
                self.assertFalse(os.path.exists(path))   # 環境異常不得留下半成品基準檔
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(main([PROG, "diff", path], run=_StubRun()), RC_ENV)
            self.assertIn("基準檔缺席", err.getvalue())

    def test_exit_code_numerals_are_the_published_contract(self):
        """★本類其餘各案一律拿常數與自己比（assertEqual(main(...), RC_*)），只驗分流路徑、
        不驗契約數值——RC_ENV 由 2 改 3、RC_USAGE 由 64 改 2 皆全綠，而 RUNBOOK §12 退出碼段
        仍逐碼寫 2／64＝手冊與工具各說各話。退出碼是本工具唯一的對外契約（§9c 步驟 4
        「rc 0 為準」），故照 rust-fmt-gate 慣例釘字面。"""
        self.assertEqual((RC_OK, RC_DIFF, RC_ENV, RC_USAGE), (0, 1, 2, 64))

    def test_usage_is_64_on_stderr(self):
        for argv in ([PROG], [PROG, "nope"], [PROG, "snapshot"], [PROG, "diff", "--user", "x"],
                     [PROG, "diff", "f.json", "--bogus"], [PROG, "diff", "f.json", "--user"],
                     [PROG, "restore"], [PROG, "restore", "--db", "x"],
                     [PROG, "restore", "f.json", "--bogus"],
                     [PROG, "restore", "--seed", "f.json"], [PROG, "restore", "f.json", "--seed"],
                     [PROG, "restore", "--seed", "--user"], [PROG, "restore", "--seed", "--seed"],
                     [PROG, "snapshot", "--seed"], [PROG, "diff", "--seed"]):
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(argv, run=_StubRun()), RC_USAGE, msg=str(argv))
            self.assertIn("用法：", err.getvalue(), msg=str(argv))


class TestCommandForms(unittest.TestCase):
    """psql／redis 命令構造與唯讀紀律逐字釘死；密碼不出現在 host argv。"""

    def test_psql_argv_form_and_user_db_options(self):
        argv = psql_argv("SELECT 1", "u1", "d1")
        self.assertEqual(argv[:8], ["docker", "compose", "-f", "docker-compose.yml",
                                    "-f", "docker-compose.dev.yml", "exec", "-T"])
        self.assertEqual(argv[8:10], ["postgres", "psql"])
        for tok in ("-U", "u1", "-d", "d1", "-At", "-F", PSQL_SEP, "ON_ERROR_STOP=1"):
            self.assertIn(tok, argv)
        self.assertEqual(argv[-1], "SELECT 1")
        stub = _StubRun()
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stdout(io.StringIO()):
                main([PROG, "snapshot", os.path.join(d, "b.json"), "--user", "u9", "--db", "d9"],
                     run=stub)
        psqls = [a for a in stub.log if "psql" in a]
        self.assertTrue(psqls and all(a[a.index("-U") + 1] == "u9" and a[a.index("-d") + 1] == "d9"
                                      for a in psqls))

    def test_snapshot_and_diff_are_read_only(self):
        """★唯讀紀律的射程＝snapshot 與 diff 兩路（restore 的寫面另由 TestRestore 逐字釘死）：
        兩路任一混入寫句（非 SELECT 起首、或含寫入字詞）或非讀 redis 命令即紅。"""
        stub = _StubRun()
        snapshot_live(run=stub)
        sqls = [a[-1] for a in stub.log if "psql" in a]
        self.assertEqual(len(sqls), 5)                   # 表清單／表列數／序列清單／序列值／角色選單使用者域與遷移帳六欄（v4）
        self.assertEqual(_pg_write_offenders(sqls), [])
        redis_cmds = [a[-1] for a in stub.log if "sh" in a]
        self.assertEqual(len(redis_cmds), 2)
        self.assertEqual(_redis_write_offenders(redis_cmds), [])
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "b.json")
            dump_snapshot(snapshot_live(run=_StubRun()), path)
            diff_stub = _StubRun()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cmd_diff(path, DB_USER, DB_NAME, diff_stub), RC_OK)
        diff_sqls = [a[-1] for a in diff_stub.log if "psql" in a]
        diff_redis = [a[-1] for a in diff_stub.log if "sh" in a]
        self.assertEqual((len(diff_sqls), len(diff_redis)), (5, 2))
        self.assertEqual(_pg_write_offenders(diff_sqls), [])
        self.assertEqual(_redis_write_offenders(diff_redis), [])
        # 判準本身抓得到寫句（含「SELECT 起首卻夾帶寫句」形）、且不被 updated_at 之類欄名誤觸
        self.assertEqual(len(_pg_write_offenders(["DELETE FROM sys_token", "SELECT 1; DELETE FROM x",
                                                  "SELECT setval('s', 1, false)",
                                                  "SELECT updated_at, deleted_at FROM t"])), 3)
        self.assertEqual(len(_redis_write_offenders([f"{REDIS_CLI} DEL k", f"{REDIS_CLI} FLUSHDB",
                                                     f"{REDIS_CLI} --scan"])), 2)
        # 表名照規矩雙引號、名欄單引號（UNION ALL 一次撈）
        self.assertIn('SELECT \'sys_user\', count(*) FROM "sys_user"', sqls[1])
        self.assertIn(" UNION ALL ", sqls[1])
        self.assertIn('SELECT \'sys_user_id_seq\', last_value, is_called FROM "sys_user_id_seq"',
                      sqls[3])

    def test_catalog_sql_and_count_legs_are_pinned_against_narrowing(self):
        """★「零手抄名冊」不變式的唯一機器載體（同 schema-gate 三 SQL 常數位元釘死之形）：
        樁 _StubRun 以**常數同一性**分流（`sql == SQL_TABLES`）、回傳的假資料與 SQL 文字無關，
        故目錄 SQL 被窄化時其餘各案照樣全綠——本工具存在的理由（清單式防法已被 rev5:L-071 證偽）
        可被靜默拆掉。四種實測窄化：①排除 seaql_migrations（檔頭明文承諾不豁免）
        ②改掃 pg_catalog ③序列面 LIKE 'sys_token%'（退化成手抄四表）④count 腿 WHERE false
        （整個表面恆讀 0＝走查後 diff 永遠全等的假綠機器）。逐字全等＋結構不變式雙釘。"""
        self.assertEqual(SQL_TABLES,
                         "SELECT table_name FROM information_schema.tables "
                         "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY 1")
        self.assertEqual(SQL_SEQUENCES,
                         "SELECT c.relname FROM pg_class c "
                         "JOIN pg_namespace n ON n.oid=c.relnamespace "
                         "WHERE c.relkind='S' AND n.nspname='public' ORDER BY 1")
        for sql in (SQL_TABLES, SQL_SEQUENCES):
            # 結構不變式（連同期望字面一起被改寫時仍成立）：只准一個 AND、不得有名冊式篩選
            self.assertEqual(sql.upper().count(" AND "), 1, msg=sql)
            for banned in (" LIKE ", "<>", "!=", " NOT IN ", " IN ("):
                self.assertNotIn(banned, sql.upper(), msg=sql)
        stub = _StubRun()
        snapshot_live(run=stub)
        sqls = [a[-1] for a in stub.log if "psql" in a]
        self.assertEqual(sqls[0], SQL_TABLES)
        self.assertEqual(sqls[2], SQL_SEQUENCES)
        # count／序列腿：**全等**比對（非 assertIn）＋腿數＝清單長度、且不得帶 WHERE
        self.assertEqual(sqls[1], " UNION ALL ".join(
            f'SELECT \'{n}\', count(*) FROM "{n}"' for n in sorted(FAKE_TABLES)))
        self.assertEqual(sqls[3], " UNION ALL ".join(
            f'SELECT \'{n}\', last_value, is_called FROM "{n}"' for n in sorted(FAKE_SEQS)))
        for leg_sql, names in ((sqls[1], FAKE_TABLES), (sqls[3], FAKE_SEQS)):
            self.assertEqual(leg_sql.count(" UNION ALL "), len(names) - 1, msg=leg_sql)
            self.assertNotIn("WHERE", leg_sql.upper(), msg=leg_sql)

    def test_redis_argv_takes_password_inside_container_shell_only(self):
        argv = redis_argv("DBSIZE")
        self.assertEqual(argv[:8], COMPOSE_EXEC)
        self.assertEqual(argv[8:11], ["redis", "sh", "-c"])
        script = argv[-1]
        self.assertIn(f'-a "$(cat {REDIS_PASSWORD_FILE})"', script)
        self.assertIn("--no-auth-warning", script)
        self.assertTrue(script.endswith(" DBSIZE"))
        # host argv 只出現「$(cat …)」字面：除 sh -c 的 script 外沒有任何元素提到密碼檔，
        # 且 script 內密碼檔只以命令替換形出現（沒有任何已展開的值可洩）。
        self.assertEqual([a for a in argv if "redis_password" in a], [script])
        self.assertEqual(script.count("redis_password"), script.count("$(cat /run/secrets/redis_password)"))

    def test_every_print_flushes(self):
        """輸出紀律檔文釘死（同 rust-fmt-gate／wf-watchdog）：每個 print 皆帶 flush=True。"""
        with open(__file__, encoding="utf-8") as fh:
            src = fh.read()
        offenders = [ln for ln in src.splitlines() if "print(" in ln and "flush=True" not in ln]
        self.assertEqual(offenders, [], msg=str(offenders))


# ── restore 自測（BL-00053）──────────────────────────────────────────────────

_WRITE_WORDS = re.compile(r"\b(INSERT|UPDATE|DELETE|TRUNCATE|SETVAL|ALTER|DROP|CREATE|BEGIN|COMMIT|"
                          r"COPY|GRANT)\b")
_REDIS_READ_SUFFIXES = (" DBSIZE", " --scan", " --scan --pattern 'session:*'",
                        " --scan --pattern 'throttle:*'", " --scan --pattern 'cpwd:*'")


def _pg_write_offenders(sqls):
    """唯讀判準：非 SELECT 起首、或含寫入字詞（字詞邊界比對——updated_at 之類欄名不誤觸）者皆列出。"""
    return [s for s in sqls if not s.startswith("SELECT ") or _WRITE_WORDS.search(s.upper())]


def _redis_write_offenders(cmds):
    """唯讀判準：redis 命令只准 DBSIZE／--scan（含 restore 三前綴樣式掃描）；其餘一律列出。"""
    return [c for c in cmds if not c.endswith(_REDIS_READ_SUFFIXES)]


RESTORE_FAKE_TABLES = {"sys_user": 3, "sys_token": 0, "session_event": 0, "sys_login_attempt": 0,
                       "sys_ip_rule": 0, "sys_operation_log": 0, "sys_pwd_custody": 0, "sys_access_log": 0,
                       "sys_user_email_verify": 0, "system_settings": 2, "seaql_migrations": 7,
                       "sys_role": 3, "sys_menu": 78, "casbin_rule": 163, "sys_casbin_policy_archive": 0,
                       "sys_user_role": 3}
RESTORE_FAKE_SEQS = {"sys_user_id_seq": (3, "t"), "sys_token_id_seq": (1, "f"),
                     "session_event_id_seq": (1, "f"), "sys_login_attempt_id_seq": (1, "f"),
                     "sys_ip_rule_id_seq": (1, "f"), "sys_operation_log_id_seq": (1, "f"),
                     "sys_access_log_id_seq": (1, "f"),
                     "sys_role_id_seq": (3, "t"), "sys_menu_id_seq": (78, "t"), "casbin_rule_id_seq": (163, "t"),
                     "sys_casbin_policy_archive_id_seq": (1, "f")}
SEED_SETTINGS_TEXT = (
    "--\n-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: soybean\n--\n\n"
    "COPY public.system_settings (setting_key, created_at, updated_at, updated_by, setting_type, "
    "setting_value, description) FROM stdin;\n"
    "session_idle_timeout\t2026-08-05 00:00:00+00\t\\N\t\\N\tnumber\t60\t閒置逾時\n"
    "single_session_default\t2026-08-05 00:00:00+00\t\\N\t\\N\tenum:on,off\toff\t全站單一-session 預設\n"
    "\\.\n")

# 清理面七表之測試側手寫名冊（不自受測常數 RESTORE_TABLES 衍生——常數縮水時跟著縮＝套套邏輯）
CLEAR_TABLES = ("session_event", "sys_token", "sys_login_attempt", "sys_ip_rule", "sys_operation_log", "sys_pwd_custody",
                "sys_access_log")
# ③b 角色／選單／使用者域寫面於「目標＝seed 形（3／78／163／0／3、指派 3 對；授權列、角色列與使用者列＝樁值）」時之逐字期望（005 刀
# U15、006 刀 U15、007 刀 U1；手寫、不自受測常數衍生）：指派鍵集差刪除先於五表、五表刪上界以上列（sys_user 居末）、授權列回補
# （排在刪上界列之後）、指派回補（排在一切刪除之後）、角色列回寫、使用者列回寫、五支 setval——接在清理面 setval 之後、COMMIT 之前
BOUNDED_SURFACE_AT_SEED = (
    "DELETE FROM sys_user_role WHERE (user_id, role_id) NOT IN (VALUES (1, 1), (2, 2), (3, 3)); "
    "DELETE FROM sys_role WHERE id > 3; "
    "DELETE FROM sys_menu WHERE id > 78; "
    "DELETE FROM casbin_rule WHERE id > 163; "
    "DELETE FROM sys_casbin_policy_archive WHERE id > 0; "
    "DELETE FROM sys_user WHERE id > 3; "
    + _t_casbin_insert([_stub_casbin_row(i) for i in range(1, 164)]) + " "
    + _t_user_role_insert(STUB_USER_ROLES) + " "
    + "".join(_t_role_update(i, STUB_ROLE_ROWS[i]) + " " for i in (1, 2, 3))
    + "".join(_t_user_update(i, STUB_USER_ROWS[i]) + " " for i in (1, 2, 3)) +
    "SELECT setval('sys_role_id_seq', 3, true); "
    "SELECT setval('sys_menu_id_seq', 78, true); "
    "SELECT setval('casbin_rule_id_seq', 163, true); "
    "SELECT setval('sys_casbin_policy_archive_id_seq', 1, false); "
    "SELECT setval('sys_user_id_seq', 3, true); ")
# seed 模式左源樁：上段＋清理面七表之零列 COPY 段（經手表欄形同真檔、無 id）＋六支 setval 行。表名與序列名字面手寫、不自受測常數衍生
# （常數縮水時樁跟著縮＝套套邏輯）；sys_ip_rule_id_seq 刻意取非預設值、證 setval 值自 seed 現讀而非寫死。
SEED_RESTORE_TEXT = SEED_SETTINGS_TEXT + "".join(
    f"\nCOPY public.{t} (id, created_at) FROM stdin;\n\\.\n"
    for t in CLEAR_TABLES[:5]) + "\nCOPY public.sys_pwd_custody (user_id, created_at, created_by) FROM stdin;\n\\.\n" + (
    "\nCOPY public.sys_access_log (id, created_at) FROM stdin;\n\\.\n") + "".join(
    f"\nSELECT pg_catalog.setval('public.{s}', {v});\n"
    for s, v in (("session_event_id_seq", "1, false"), ("sys_access_log_id_seq", "1, false"),
                 ("sys_ip_rule_id_seq", "7, true"), ("sys_login_attempt_id_seq", "1, false"),
                 ("sys_operation_log_id_seq", "1, false"), ("sys_token_id_seq", "1, false"))) + (
    # 角色／選單域五表（005 刀 U15）：形同真凍結 seed（3／78／163／0 列、指派 3 對、四支 setval；007 刀 U1 另加 sys_user 段與其
    # setval 行、見下）；表名與序列名手寫。
    # 006 刀 U15：casbin_rule 段擴全欄（欄序同真檔）、sys_role 段擴含七個可變欄（欄序刻意打亂、證依段首欄名取值）——值＝樁現況值
    "\nCOPY public.sys_role (id, created_at, role_code, updated_by, role_name, status, role_memo, role_home, "
    "updated_at, role_desc) FROM stdin;\n"
    + "".join("\t".join([str(i), STUB_TS_COPY, f"R_{i}"] + [_t_copy(STUB_ROLE_ROWS[i][c]) for c in (
        "updated_by", "role_name", "status", "role_memo", "role_home", "updated_at", "role_desc")]) + "\n"
        for i in range(1, 4)) + "\\.\n"
    "\nCOPY public.sys_menu (id, \"order\", menu_name) FROM stdin;\n"
    + "".join(f"{i}\t{i}\tm{i}\n" for i in range(1, 79)) + "\\.\n"
    "\nCOPY public.casbin_rule (id, ptype, v0, v1, v2, v3, v4, v5, protected, created_at, created_by) FROM stdin;\n"
    + "".join("\t".join(_t_copy(_stub_casbin_row(i, STUB_TS_COPY)[c]) for c in STUB_CASBIN_COLUMNS) + "\n"
              for i in range(1, 164)) + "\\.\n"
    "\nCOPY public.sys_casbin_policy_archive (id, role_id, ptype) FROM stdin;\n\\.\n"
    "\nCOPY public.sys_user_role (user_id, role_id) FROM stdin;\n1\t1\n2\t2\n3\t3\n\\.\n"
    # 007 刀 U1：sys_user 段全欄（欄序同真檔；密碼欄＝_stub_pw 合成佔位、非 PHC 形）＋其 setval 行
    "\nCOPY public.sys_user (id, created_at, created_by, updated_at, updated_by, deleted_at, deleted_by, status, user_gender, "
    "user_name, password, nick_name, session_policy, session_id, user_phone, user_email, user_memo) FROM stdin;\n"
    + "".join("\t".join([str(i), STUB_TS_COPY, "\\N"] + [_t_copy(STUB_USER_ROWS[i][c]) for c in (
        "updated_at", "updated_by", "deleted_at", "deleted_by", "status", "user_gender")] + [STUB_USER_NAMES[i]]
        + [_t_copy(STUB_USER_ROWS[i][c]) for c in ("password", "nick_name", "session_policy")] + ["\\N"]
        + [_t_copy(STUB_USER_ROWS[i][c]) for c in ("user_phone", "user_email", "user_memo")]) + "\n"
        for i in range(1, 4)) + "\\.\n"
    "\nSELECT pg_catalog.setval('public.sys_role_id_seq', 3, true);\n"
    "\nSELECT pg_catalog.setval('public.sys_menu_id_seq', 78, true);\n"
    "\nSELECT pg_catalog.setval('public.casbin_rule_id_seq', 163, true);\n"
    "\nSELECT pg_catalog.setval('public.sys_casbin_policy_archive_id_seq', 1, false);\n"
    "\nSELECT pg_catalog.setval('public.sys_user_id_seq', 3, true);\n")


def _seed_settings_rows(**value_over):
    """樁 system_settings 現況列（值＝SEED_SETTINGS_TEXT、審計欄全 NULL）；可覆寫個別鍵的值。"""
    rows = [{"setting_key": "session_idle_timeout", "setting_value": "60", "stamped": False},
            {"setting_key": "single_session_default", "setting_value": "off", "stamped": False}]
    for r in rows:
        r["setting_value"] = value_over.get(r["setting_key"], r["setting_value"])
    return rows


def _restore_stub(**over):
    kw = {"tables": RESTORE_FAKE_TABLES, "seqs": RESTORE_FAKE_SEQS, "keys": ["plainkey"],
          "settings": _seed_settings_rows()}
    kw.update(over)
    return _StubRun(**kw)


def _ledger_entry(eid, kind, table, detail):
    """合成演進登記項（欄位齊同 docs/ops/reference-src/schema-evolution-contract.md §2）。"""
    return {"id": eid, "knife": "001-schema-baseline", "kind": kind, "table": table,
            "detail": detail, "date": "2026-09-14"}


# m0003 形之合成登記九筆（007 刀 U1、T007；形照 specs/007-user-password-admin/data-model.md §9.2 手寫、不自受測常數衍生）：
# 六碼改受保護（58～63）、刪列 44、增列 164（created_at 取 COPY 文字形）、選單 78 之 buttons（jsonb 正規輸出形）。
M0003_MODULES = ("m0001_baseline_schema", "m0002_baseline_seeds", "m0003_seed_button_governance")
M0003_BUTTONS = ('[{"code": "ipRule:add", "desc": "新增IP規則"}, {"code": "ipRule:edit", "desc": "編輯IP規則"}, '
                 '{"code": "ipRule:delete", "desc": "刪除IP規則"}, {"code": "ipRule:restore", "desc": "恢復IP規則"}, '
                 '{"code": "ipRule:unlock", "desc": "解鎖來源IP"}]')
M0003_ENTRIES = tuple(
    [dict(_ledger_entry(f"E-00{n - 57}", "seed_update", "casbin_rule", {"pk": {"id": n}, "set": {"protected": True}}),
          knife="007-user-password-admin") for n in range(58, 64)]
    + [dict(_ledger_entry("E-007", "seed_delete", "casbin_rule", {"pk": {"id": 44}}), knife="007-user-password-admin"),
       dict(_ledger_entry("E-008", "seed_add", "casbin_rule", {"pk": ["id"], "values": {
           "id": 164, "ptype": "p", "v0": "R_SUPER", "v1": "ipRule:unlock", "v2": "button", "v3": "", "v4": "", "v5": "",
           "protected": False, "created_at": "2026-08-05 00:00:00+00", "created_by": None}}),
            knife="007-user-password-admin"),
       dict(_ledger_entry("E-009", "seed_update", "sys_menu", {"pk": {"id": 78}, "set": {"buttons": M0003_BUTTONS}}),
            knife="007-user-password-admin")])


class TestRestore(unittest.TestCase):
    """restore 諸步：讀帳與演進合成→安全帶（清理面七表之基準須為空）→遷移帳前置（基準檔＝現庫）→repo↔現庫遷移同步前置（合成射程有
    seed_* 登記時）→system_settings 對期望 seed（凍結 ⊕ 演進合成；值不等 fail-loud、不改值）→pg 單交易（寫句恰為列舉、setval 自
    基準檔現讀）→redis 三前綴逐鍵指名 DEL（絕不 FLUSHDB）→收尾 diff 之 rc 即 restore 之 rc。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = self._tmp.name
        self.seed = os.path.join(self.d, "seed.sql")
        with open(self.seed, "w", encoding="utf-8") as fh:
            fh.write(SEED_SETTINGS_TEXT)
        self.ledger = os.path.join(self.d, "schema-evolution.json")
        self._write_ledger()                        # 各案預設空帳（＝基線初始態）、與真 repo 登記檔隔離

    def tearDown(self):
        self._tmp.cleanup()

    def _write_ledger(self, *entries):
        with open(self.ledger, "w", encoding="utf-8") as fh:
            json.dump({"next_id": len(entries) + 1, "entries": list(entries)}, fh, ensure_ascii=False)

    def _baseline(self, stub):
        path = os.path.join(self.d, "walk.json")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cmd_snapshot(path, DB_USER, DB_NAME, stub), RC_OK)
        stub.log.clear()
        return path

    def _restore(self, path, stub, lib_path=None):
        """基準檔模式；lib_path＝repo migration 清單之料源（None＝真 repo；同步前置之合成案另給樁 lib.rs）。"""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger, lib_path=lib_path)
        return rc, out.getvalue() + err.getvalue()

    def _restore_seed(self, stub, seed_text=SEED_RESTORE_TEXT, lib_path=None):
        """seed 模式（path=None＝無基準檔）；左源＝樁 seed 檔（⊕ 樁演進帳之合成）。"""
        with open(self.seed, "w", encoding="utf-8") as fh:
            fh.write(seed_text)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cmd_restore(None, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger, lib_path=lib_path)
        return rc, out.getvalue() + err.getvalue()

    @staticmethod
    def _dirty(stub):
        """模擬走查殘留：五表列＋序列推進＋session／throttle 鍵（含須引號的鍵名）＋審計欄被寫。"""
        stub.tables.update(sys_token=2, session_event=3, sys_login_attempt=1, sys_ip_rule=2,
                           sys_operation_log=5)
        stub.seqs.update(sys_token_id_seq=(33, "t"), session_event_id_seq=(4, "t"),
                         sys_login_attempt_id_seq=(9, "t"), sys_ip_rule_id_seq=(3, "t"),
                         sys_operation_log_id_seq=(6, "t"))
        stub.keys += ["session:sid-a:last_activity", "throttle:unlock:user:走查 探針",
                      "session:denylist:sid-b"]
        stub.settings[1]["stamped"] = True

    @staticmethod
    def _dirty_user_domain(stub):
        """模擬使用者域走查殘留（US6 場景 3；表名與序列名手寫）：seed 指派 (2, 2) 被刪、新帳號列（走 nextval、序列推進）與其指派
        （新帳號×角色 3）、seed 帳號 2 之暱稱與密碼雜湊被改（寫端同交易蓋審計欄）、經手表一列、該新帳號之改密節流鍵一把。回新帳號 id。"""
        stub.user_roles.remove((2, 2))
        stub.tables["sys_user_role"] -= 1
        last, called = stub.seqs["sys_user_id_seq"]
        new = last + 1 if called == "t" else last
        stub.ids["sys_user"].append(new)
        stub.tables["sys_user"] += 1
        stub.seqs["sys_user_id_seq"] = (new, "t")
        stub.user_roles.append((new, 3))
        stub.tables["sys_user_role"] += 1
        stub.users[2] = dict(stub.user_row(2), nick_name="走查改名", password=_stub_pw(2) + "改",
                             updated_at="2026-10-06T09:00:00+00:00", updated_by=1)
        stub.tables["sys_pwd_custody"] = 1
        stub.keys.append(f"cpwd:{new}")
        return new

    def test_doorbell_rung_only_when_ip_rules_were_present_and_reports_subscribers(self):
        """BL-00094：restore 以 SQL 直清 sys_ip_rule＝不經規則寫端、不按門鈴⇒執行中的 rust-api 判定面持舊規則集
        （004 刀 T047／T067 兩次走查實際踩到、當時由 RUNBOOK 手動步驟承載）。
        ①清前有列＝按一次並回報訂閱者數 ②訂閱者 0＝附告警尾句 ③清前 0 列＝不按（反例、避免無謂喚醒）。"""
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)                                  # _dirty 會把 sys_ip_rule 寫成非 0
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        pubs = [c for c in (a[-1] for a in stub.log if "sh" in a) if " PUBLISH " in c]
        self.assertEqual(len(pubs), 1, pubs)
        self.assertIn(f"PUBLISH {IPGATE_CHANNEL} {IPGATE_DOORBELL_PAYLOAD}", pubs[0])
        self.assertIn("訂閱者 1", text)
        self.assertNotIn("無 watcher 在訂", text)

        stub = _restore_stub(subs=0)                        # ②無 watcher 在訂＝按了但沒人收
        path = self._baseline(stub)
        self._dirty(stub)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertIn("訂閱者 0", text)
        self.assertIn("無 watcher 在訂", text)

        # ★L1-1：redis 清理失敗時門鈴仍已按過（門鈴排在 pg 交易之後、DEL 之前）——
        # 舊形把門鈴排在 DEL 之後，DEL 一失敗即拋，而依其補救訊息重跑時清前已 0 列＝永遠補不回來。
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)
        stub.fail = "del"
        with self.assertRaises(BaselineError) as ctx:
            self._restore(path, stub)
        self.assertIn("門鈴已排在本步之前", str(ctx.exception))
        self.assertEqual(len([c for c in (a[-1] for a in stub.log if "sh" in a) if " PUBLISH " in c]), 1)

        stub = _restore_stub()                              # ③清前 0 列（走查沒動過 IP 規則）＝不按
        path = self._baseline(stub)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertEqual([c for c in (a[-1] for a in stub.log if "sh" in a) if " PUBLISH " in c], [])
        self.assertIn("0 列＝該表本就是空的", text)

    def test_doorbell_failure_hands_over_the_runbook_manual_command_verbatim(self):
        """PUBLISH 回非整數＝pg 已提交而門鈴未響：拋出之訊息須附可照抄的人工按鈴命令、且與 RUNBOOK §9c 所列逐字相同
        （005 刀 U15 揭出：組命令處引用未定義名、此路徑以 NameError traceback 結束、照抄命令遺失）。"""
        stub = _restore_stub(subs="OK")
        path = self._baseline(stub)
        self._dirty(stub)
        with self.assertRaises(BaselineError) as ctx:
            self._restore(path, stub)
        self.assertIn("docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T redis sh -lc "
                      "'redis-cli -a \"$(cat /run/secrets/redis_password)\" --no-auth-warning "
                      "PUBLISH ipgate:invalidate 1'", str(ctx.exception))

    def test_write_statements_are_exactly_the_enumerated_transaction_and_del(self):
        """★寫面逐字釘死（多一句、少一句、換序皆紅）；其餘 pg 句與 redis 命令一律過唯讀判準。"""
        stub = _restore_stub(seqs=dict(RESTORE_FAKE_SEQS, sys_token_id_seq=(5, "t")))
        path = self._baseline(stub)
        self._dirty(stub)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        sqls = [a[-1] for a in stub.log if "psql" in a]
        writes = [s for s in sqls if _pg_write_offenders([s])]
        self.assertEqual(writes, [
            "BEGIN; "
            "UPDATE system_settings SET updated_at = NULL, updated_by = NULL "
            "WHERE updated_at IS NOT NULL OR updated_by IS NOT NULL; "
            "DELETE FROM session_event; DELETE FROM sys_token; DELETE FROM sys_login_attempt; "
            "DELETE FROM sys_ip_rule; DELETE FROM sys_operation_log; DELETE FROM sys_pwd_custody; "
            "DELETE FROM sys_access_log; "
            "UPDATE sys_user SET session_id = NULL WHERE session_id IS NOT NULL; "
            "SELECT setval('sys_token_id_seq', 5, true); "
            "SELECT setval('session_event_id_seq', 1, false); "
            "SELECT setval('sys_login_attempt_id_seq', 1, false); "
            "SELECT setval('sys_ip_rule_id_seq', 1, false); "
            "SELECT setval('sys_operation_log_id_seq', 1, false); "
            "SELECT setval('sys_access_log_id_seq', 1, false); "
            + BOUNDED_SURFACE_AT_SEED +
            "COMMIT;"])
        redis_cmds = [a[-1] for a in stub.log if "sh" in a]
        self.assertEqual(_redis_write_offenders(redis_cmds), [
            f"{REDIS_CLI} PUBLISH {IPGATE_CHANNEL} {IPGATE_DOORBELL_PAYLOAD}",   # ★門鈴排在 DEL 之前（L1-1）
            f"{REDIS_CLI} DEL session:denylist:sid-b session:sid-a:last_activity "
            "'throttle:unlock:user:走查 探針'"])
        self.assertFalse(any("FLUSH" in c.upper() for c in redis_cmds))
        self.assertEqual(stub.keys, ["plainkey"])                      # 非清理前綴之鍵不動
        self.assertFalse(any(s["stamped"] for s in stub.settings))     # 審計欄已歸 NULL
        # 次序：遷移帳前置讀 → settings 讀 → 交易 → 前綴掃 → DEL → 收尾 diff 取樣
        flat = [a[-1] for a in stub.log]
        order = (flat.index(SQL_MIGRATIONS), flat.index(SQL_SETTINGS), flat.index(writes[0]),
                 min(i for i, c in enumerate(flat) if " --scan --pattern " in c),
                 min(i for i, c in enumerate(flat) if " DEL " in c),
                 max(i for i, c in enumerate(flat) if c == SQL_TABLES))
        self.assertEqual(list(order), sorted(order), msg=order)
        self.assertIn("✓ 全等", text)

    def test_setval_values_are_read_from_the_baseline_file_not_hardcoded(self):
        snap = _snap(tables={t: 0 for t in RESTORE_TABLES},
                     sequences={"sys_token_id_seq": {"last_value": 9, "is_called": True},
                                "session_event_id_seq": {"last_value": 8, "is_called": False},
                                "sys_login_attempt_id_seq": {"last_value": 7, "is_called": True},
                                "sys_ip_rule_id_seq": {"last_value": 6, "is_called": True},
                                "sys_operation_log_id_seq": {"last_value": 5, "is_called": False},
                                "sys_access_log_id_seq": {"last_value": 4, "is_called": True}},
                     redis={"dbsize": 0, "prefixes": {}})
        sql = restore_sql(snap)
        self.assertTrue(sql.endswith("SELECT setval('sys_token_id_seq', 9, true); "
                                     "SELECT setval('session_event_id_seq', 8, false); "
                                     "SELECT setval('sys_login_attempt_id_seq', 7, true); "
                                     "SELECT setval('sys_ip_rule_id_seq', 6, true); "
                                     "SELECT setval('sys_operation_log_id_seq', 5, false); "
                                     "SELECT setval('sys_access_log_id_seq', 4, true); COMMIT;"),
                        msg=sql)
        self.assertEqual(sql.count("setval("), 6)

    def test_nonempty_baseline_refuses_rc2_before_any_docker_call(self):
        """★安全帶：基準檔清理面任一表列數或 session／throttle／cpwd 前綴鍵數非 0＝rc 2、零 docker 呼叫＝零寫入
        （本案走會話三表與三前綴；sys_ip_rule／sys_operation_log／sys_pwd_custody／sys_access_log 四表由擴面案走）。"""
        for over in ({"tables": dict(RESTORE_FAKE_TABLES, sys_token=2)},
                     {"tables": dict(RESTORE_FAKE_TABLES, session_event=1)},
                     {"tables": dict(RESTORE_FAKE_TABLES, sys_login_attempt=4)},
                     {"keys": ["plainkey", "session:sid-x"]},
                     {"keys": ["throttle:unlock:ip:203.0.113.9"]},
                     {"keys": ["cpwd:4"]}):
            stub = _restore_stub(**over)
            path = self._baseline(stub)
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = main([PROG, "restore", path], run=stub)
            self.assertEqual(rc, RC_ENV, msg=over)
            self.assertIn("基準非空、DELETE 全表會毀掉基準資料", err.getvalue(), msg=over)
            self.assertEqual(stub.log, [], msg=over)

    def test_baseline_lacking_restore_tables_or_sequences_is_env_error(self):
        for over, needle in (({"tables": {"sys_user": 3, "sys_token": 0, "session_event": 0}},
                              "sys_login_attempt"),
                             ({"seqs": {k: v for k, v in RESTORE_FAKE_SEQS.items()
                                        if k != "session_event_id_seq"}}, "session_event_id_seq")):
            stub = _restore_stub(**over)
            path = self._baseline(stub)
            with self.assertRaises(BaselineError) as ctx:
                cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
            self.assertIn(needle, str(ctx.exception))
            self.assertEqual(stub.log, [])

    def test_settings_value_drift_fails_loud_by_name_and_writes_nothing(self):
        """值≠期望 seed（含鍵缺／鍵多）＝fail-loud 指名、不自動改值；只讀過遷移帳前置、門鈴清前計數與 settings 三句、零寫入。
        ★左源＝凍結 seed ⊕ 演進合成（007 刀 U1、T007）：帳上已登記 system_settings 之 seed_update 而現值仍為凍結值＝值≠合成值、
        指名合成值（判準不變：值≠期望才 rc 2；左源若退回凍結段，本腿現值＝凍結值即照跑寫入）。"""
        self._write_ledger(_ledger_entry("E-001", "seed_update", "system_settings",
                                         {"pk": {"setting_key": "session_idle_timeout"}, "set": {"setting_value": "30"}}))
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        for needle in ("session_idle_timeout 現值 '60'", "'30'", "002 刀"):
            self.assertIn(needle, str(ctx.exception))
        self.assertEqual([a[-1] for a in stub.log], [SQL_MIGRATIONS, SQL_IP_RULE_ROWS, SQL_SETTINGS])
        self._write_ledger()
        extra = {"setting_key": "zz_extra", "setting_value": "1", "stamped": False}
        for rows, needles in ((_seed_settings_rows(single_session_default="on"),
                               ("single_session_default", "'on'", "'off'")),
                              (_seed_settings_rows()[:1], ("single_session_default",)),
                              (_seed_settings_rows() + [extra], ("zz_extra",))):
            stub = _restore_stub()
            path = self._baseline(stub)
            self._dirty(stub)
            stub.settings = rows
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
            for needle in needles + ("002 刀",):
                self.assertIn(needle, str(ctx.exception))
            # 遷移帳前置排在一切現讀之前（v4）；清前計數為讀、排在 settings 讀之前（BL-00094）
            self.assertEqual([a[-1] for a in stub.log], [SQL_MIGRATIONS, SQL_IP_RULE_ROWS, SQL_SETTINGS])

    def test_restore_rc_is_the_final_diff_rc(self):
        """收尾 diff 之 rc 即 restore 之 rc：清理面與角色／選單／使用者域之外的殘留（sys_user_email_verify 多一列；seed 零列）restore
        不碰、收尾 diff 照報 rc 1；★sys_user 多一列（顯式 id 直植、序列未動）＝007 刀 U1 起入上界面＝刪列、收尾 rc 0（舊形「sys_user
        多一列不碰、收尾照報」翻轉）。"""
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)
        stub.tables["sys_user_email_verify"] = 1    # 清理面與該域之外的殘留：restore 不碰、收尾 diff 照報
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_DIFF)
        self.assertIn("表｜sys_user_email_verify｜0｜1｜1", text)
        self.assertEqual((stub.tables["sys_token"], stub.keys), (0, ["plainkey"]))
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)
        stub.ids["sys_user"].append(4)
        stub.tables["sys_user"] += 1
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertIn("DELETE FROM sys_user WHERE id > 3;", self._tx(stub))
        self.assertEqual((stub.ids["sys_user"], stub.tables["sys_user"]), ([1, 2, 3], 3))

    def test_failures_are_env_errors_and_stop_before_later_steps(self):
        stub = _restore_stub()                      # 交易失敗 → 不進 redis
        path = self._baseline(stub)
        self._dirty(stub)
        stub.fail = "tx"
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError):
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        self.assertFalse(any(" --scan --pattern " in a[-1] or " DEL " in a[-1] for a in stub.log))
        stub = _restore_stub()                      # DEL 回非整數 → 不進收尾 diff
        path = self._baseline(stub)
        self._dirty(stub)
        stub.fail = "del"
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError):
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        self.assertNotIn(SQL_TABLES, [a[-1] for a in stub.log])
        stub = _restore_stub(garble="settings")     # settings 輸出不可解 → 零寫入
        path = self._baseline(stub)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError):
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        self.assertEqual(_pg_write_offenders([a[-1] for a in stub.log if "psql" in a]), [])
        stub = _restore_stub()                      # seed 缺席 → 零 docker 呼叫
        path = self._baseline(stub)
        with self.assertRaises(BaselineError) as ctx:
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=os.path.join(self.d, "nope.sql"),
                        ledger_path=self.ledger)
        self.assertIn("nope.sql", str(ctx.exception))
        self.assertEqual(stub.log, [])

    def test_system_settings_seed_entries_are_synthesized_in_both_modes_and_synthesized_values_pass(self):
        """★US6 場景 7（T007⑤；007 刀 U1 翻轉舊形「system_settings 有 seed_* 登記即拒跑」）：帳上 system_settings 之增鍵、改值、刪鍵
        各一（＋合成面外之他表登記一筆）且現庫已套用（現值＝合成值）→ 基準檔模式與 seed 模式各一發：比對左源＝凍結 seed ⊕ 演進合成、
        值等於合成值者不報差且不拒跑、restore 不動其值（只把審計欄歸 NULL）、收尾 rc 0。左源若退回凍結段＝兩發皆報值≠seed 而 rc 2。"""
        self._write_ledger(
            _ledger_entry("E-001", "seed_add", "system_settings", {"pk": ["setting_key"], "values": {
                "setting_key": "password_min_length", "created_at": STUB_TS_COPY, "updated_at": None, "updated_by": None,
                "setting_type": "number", "setting_value": "8", "description": "密碼最短長度"}}),
            _ledger_entry("E-002", "seed_update", "system_settings",
                          {"pk": {"setting_key": "session_idle_timeout"}, "set": {"setting_value": "30"}}),
            _ledger_entry("E-003", "seed_delete", "system_settings", {"pk": {"setting_key": "single_session_default"}}),
            _ledger_entry("E-004", "seed_update", "sys_user_email_verify",
                          {"pk": {"user_id": 3}, "set": {"verified_email": "u3@example.test"}}))
        applied = {"password_min_length": "8", "session_idle_timeout": "30"}
        for seed_mode in (False, True):
            stub = _restore_stub(settings=[{"setting_key": k, "setting_value": v, "stamped": False}
                                           for k, v in sorted(applied.items())])
            path = None if seed_mode else self._baseline(stub)
            self._dirty(stub)                                   # 另把第 2 列之審計欄蓋上
            rc, text = self._restore_seed(stub) if seed_mode else self._restore(path, stub)
            self.assertEqual(rc, RC_OK, msg=(seed_mode, text))
            self.assertIn("restore ①system_settings：2 鍵值＝期望 seed", text, msg=seed_mode)
            self.assertEqual({s["setting_key"]: s["setting_value"] for s in stub.settings}, applied, msg=seed_mode)
            self.assertFalse(any(s["stamped"] for s in stub.settings), msg=seed_mode)
            self.assertIn("✓ 全等", text, msg=seed_mode)

    def test_entries_outside_the_synthesis_face_and_supported_structural_kinds_do_not_block_in_both_modes(self):
        """反面（兩模式）：合成面外之表之登記（sys_user_email_verify 之 seed_update、未內建之 add_table）不餵、不擋；合成面表之結構性登記
        之已內建形（system_settings 之 add_column＝nullable 無 default：段首加欄、既有列補 NULL、不改鍵值集）照合成、不擋——restore 照常
        清理、收尾 rc 0；無合成面之 seed_* 登記＝repo↔現庫遷移同步前置不驗（遷移帳現讀至多 (a) 一句）。"""
        self._write_ledger(
            _ledger_entry("E-001", "seed_update", "sys_user_email_verify",
                          {"pk": {"user_id": 3}, "set": {"verified_email": "u3@example.test"}}),
            _ledger_entry("E-002", "add_table", "sys_walk_probe", {"columns": [{"column": "id", "type": "bigint"}]}),
            _ledger_entry("E-003", "add_column", "system_settings",
                          {"column": "note", "type": "text", "nullable": True}))
        for seed_mode in (False, True):
            stub = _restore_stub()
            path = None if seed_mode else self._baseline(stub)
            self._dirty(stub)
            rc, text = self._restore_seed(stub) if seed_mode else self._restore(path, stub)
            self.assertEqual(rc, RC_OK, msg=(seed_mode, text))
            self.assertEqual((stub.tables["sys_token"], stub.keys), (0, ["plainkey"]), msg=seed_mode)
            self.assertEqual([a[-1] for a in stub.log].count(SQL_MIGRATIONS), 0 if seed_mode else 1, msg=seed_mode)

    def test_ledger_missing_or_malformed_is_env_error_before_any_docker_call(self):
        """演進登記檔缺席／非 JSON／entries 非 list／含非物件項＝rc 2、零 docker 呼叫（讀不懂帳＝不知左源是否仍為期望 seed）。"""
        for body in (None, "not json", '{"next_id": 1}', '{"next_id": 1, "entries": {}}',
                     '{"next_id": 2, "entries": ["E-001"]}'):
            if body is None:
                os.remove(self.ledger)
            else:
                with open(self.ledger, "w", encoding="utf-8") as fh:
                    fh.write(body)
            stub = _restore_stub()
            path = self._baseline(stub)
            with self.assertRaises(BaselineError, msg=body) as ctx:
                cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
            self.assertIn("schema-evolution.json", str(ctx.exception), msg=body)
            self.assertEqual(stub.log, [], msg=body)

    def test_malformed_entries_inside_the_synthesis_face_are_env_error_before_any_docker_call_in_both_modes(self):
        """合成射程內之登記項壞形（system_settings 之 seed_update 缺 detail、缺 id、缺 kind 各一）＝兩模式各 BaselineError（rc 2）、訊息
        含「登記項壞形」並指名該筆（缺 id 者記「?」）、零 docker 呼叫——此守門缺席時合成鏈以 KeyError／AttributeError 崩出（traceback
        之 rc 1 與「有差」混同）。反面：射程外之同形壞登記（sys_user_email_verify 缺 detail、缺 id）不餵、不擋——兩模式照常清理、收尾 rc 0。"""
        def drop(entry, key):
            return {k: v for k, v in entry.items() if k != key}

        def upd(eid, table):
            return _ledger_entry(eid, "seed_update", table, {"pk": {"setting_key": "session_idle_timeout"},
                                                             "set": {"setting_value": "30"}})

        for entry, shown in ((drop(upd("E-001", "system_settings"), "detail"), "E-001"),
                             (drop(upd("E-002", "system_settings"), "id"), "?"),
                             (drop(upd("E-003", "system_settings"), "kind"), "E-003")):
            self._write_ledger(entry)
            for seed_mode in (False, True):
                stub = _restore_stub()
                path = None if seed_mode else self._baseline(stub)
                with self.assertRaises(BaselineError, msg=(shown, seed_mode)) as ctx:
                    if seed_mode:
                        self._restore_seed(stub)
                    else:
                        self._restore(path, stub)
                self.assertIn(f"合成射程內之登記項壞形（須帶 id、kind 字串與 detail 物件）：{shown}——", str(ctx.exception),
                              msg=(shown, seed_mode))
                self.assertEqual(stub.log, [], msg=(shown, seed_mode))
        other = _ledger_entry("E-001", "seed_update", "sys_user_email_verify",
                              {"pk": {"user_id": 3}, "set": {"verified_email": "u3@example.test"}})
        self._write_ledger(drop(other, "detail"), drop(dict(other, id="E-002"), "id"))
        for seed_mode in (False, True):
            stub = _restore_stub()
            path = None if seed_mode else self._baseline(stub)
            self._dirty(stub)
            rc, text = self._restore_seed(stub) if seed_mode else self._restore(path, stub)
            self.assertEqual(rc, RC_OK, msg=(seed_mode, text))
            self.assertEqual((stub.tables["sys_token"], stub.keys), (0, ["plainkey"]), msg=seed_mode)

    def test_restore_surface_is_seven_tables_six_sequences_and_three_prefixes(self):
        """★擴面（BL-00075；004 刀 U3／007 刀 U1／008 刀 U1）：清理面＝會話三表＋sys_ip_rule＋sys_operation_log＋sys_pwd_custody（經手表：
        全表清空、無序列＝不入 setval 名冊）＋sys_access_log（ADR-00100 決定 8；無外鍵、seed 零列、置尾）與六支 id 序列、redis 三前綴
        （session／throttle／cpwd）。名冊與清列句逐字釘（多一表、少一表、換序皆紅）；安全帶與清理面缺席判定同步涵蓋會話三表以外之擴入各表與其序列；
        走一趟後七表歸零、六支序列回到基準檔之值（基準檔模式仍依檔 setval——runtime-append 五支亦然）。"""
        self.assertEqual(RESTORE_TABLES, CLEAR_TABLES)
        self.assertEqual(RESTORE_SEQUENCES, ("sys_token_id_seq", "session_event_id_seq",
                                             "sys_login_attempt_id_seq", "sys_ip_rule_id_seq",
                                             "sys_operation_log_id_seq", "sys_access_log_id_seq"))
        self.assertEqual(RESTORE_REDIS_PREFIXES, ("session", "throttle", "cpwd"))
        self.assertEqual(SQL_RESTORE_CLEAR, (
            "DELETE FROM session_event;", "DELETE FROM sys_token;", "DELETE FROM sys_login_attempt;",
            "DELETE FROM sys_ip_rule;", "DELETE FROM sys_operation_log;", "DELETE FROM sys_pwd_custody;",
            "DELETE FROM sys_access_log;",
            "UPDATE sys_user SET session_id = NULL WHERE session_id IS NOT NULL;"))
        for over in ({"tables": dict(RESTORE_FAKE_TABLES, sys_ip_rule=1)},
                     {"tables": dict(RESTORE_FAKE_TABLES, sys_operation_log=2)},
                     {"tables": dict(RESTORE_FAKE_TABLES, sys_pwd_custody=1)},
                     {"tables": dict(RESTORE_FAKE_TABLES, sys_access_log=1)}):
            stub = _restore_stub(**over)
            path = self._baseline(stub)
            with self.assertRaises(BaselineError, msg=over) as ctx:
                cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
            self.assertIn("基準非空、DELETE 全表會毀掉基準資料", str(ctx.exception), msg=over)
            self.assertIn("restore --seed", str(ctx.exception), msg=over)     # 補救指向 seed 模式
            self.assertEqual(stub.log, [], msg=over)
        for over, needle in (({"tables": {k: v for k, v in RESTORE_FAKE_TABLES.items()
                                          if k != "sys_ip_rule"}}, "sys_ip_rule"),
                             ({"tables": {k: v for k, v in RESTORE_FAKE_TABLES.items()
                                          if k != "sys_pwd_custody"}}, "sys_pwd_custody"),
                             ({"seqs": {k: v for k, v in RESTORE_FAKE_SEQS.items()
                                        if k != "sys_operation_log_id_seq"}}, "sys_operation_log_id_seq"),
                             ({"tables": {k: v for k, v in RESTORE_FAKE_TABLES.items()
                                          if k != "sys_access_log"}}, "sys_access_log"),
                             ({"seqs": {k: v for k, v in RESTORE_FAKE_SEQS.items()
                                        if k != "sys_access_log_id_seq"}}, "sys_access_log_id_seq")):
            stub = _restore_stub(**over)
            path = self._baseline(stub)
            with self.assertRaises(BaselineError, msg=needle) as ctx:
                cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
            self.assertIn(needle, str(ctx.exception))
            self.assertEqual(stub.log, [])
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)
        stub.tables["sys_pwd_custody"] = 2
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertEqual([stub.tables[t] for t in CLEAR_TABLES], [0] * 7)
        self.assertEqual(stub.seqs, RESTORE_FAKE_SEQS)

    def test_seed_mode_clears_seven_tables_and_setvals_only_the_ip_rule_sequence_from_seed(self):
        """★seed 模式（`restore --seed`；BL-00075 候選①）：無基準檔、目標態＝凍結 seed ⊕ 演進合成（本案演進帳空＝凍結 seed）。寫面逐字釘——清列句同基準檔
        模式之七表；清理面之序列 setval **只有** sys_ip_rule_id_seq 一支、值自 seed 之 setval 行現讀（樁取 7,true 非預設值；
        角色／選單／使用者域五支序列屬 ③b、逐字見同句）；
        runtime-append 五支序列不復位（走完仍是髒值）而收尾比對照樣 rc 0（只比存在性）。★清理面與該域之外不入 seed
        模式判準（無基準檔可比；該面之 pg 殘留由 tools/schema-gate.py check 之 gate2 逐列兜）。007 刀 U1：使用者域殘留（seed 指派被刪、
        新帳號列與其指派、seed 帳號欄值被改、經手表列、cpwd 鍵）一併還原至凍結 seed 目標（指派回補、使用者列回寫、sys_user 上界與序列）。"""
        stub = _restore_stub()
        self._dirty(stub)
        new = self._dirty_user_domain(stub)
        stub.tables["sys_user_email_verify"] = 1    # 清理面與該域之外：seed 模式不判
        rc, text = self._restore_seed(stub)
        self.assertEqual(rc, RC_OK, msg=text)
        sqls = [a[-1] for a in stub.log if "psql" in a]
        self.assertEqual([s for s in sqls if _pg_write_offenders([s])], [
            "BEGIN; "
            "UPDATE system_settings SET updated_at = NULL, updated_by = NULL "
            "WHERE updated_at IS NOT NULL OR updated_by IS NOT NULL; "
            "DELETE FROM session_event; DELETE FROM sys_token; DELETE FROM sys_login_attempt; "
            "DELETE FROM sys_ip_rule; DELETE FROM sys_operation_log; DELETE FROM sys_pwd_custody; "
            "DELETE FROM sys_access_log; "
            "UPDATE sys_user SET session_id = NULL WHERE session_id IS NOT NULL; "
            "SELECT setval('sys_ip_rule_id_seq', 7, true); "
            + BOUNDED_SURFACE_AT_SEED +
            "COMMIT;"])
        redis_cmds = [a[-1] for a in stub.log if "sh" in a]
        self.assertEqual(_redis_write_offenders(redis_cmds), [
            f"{REDIS_CLI} PUBLISH {IPGATE_CHANNEL} {IPGATE_DOORBELL_PAYLOAD}",   # ★門鈴排在 DEL 之前（L1-1）
            f"{REDIS_CLI} DEL session:denylist:sid-b session:sid-a:last_activity "
            f"'throttle:unlock:user:走查 探針' cpwd:{new}"])
        self.assertEqual([stub.tables[t] for t in CLEAR_TABLES], [0] * 7)
        self.assertEqual((sorted(stub.user_roles), stub.ids["sys_user"]), (list(STUB_USER_ROLES), [1, 2, 3]))
        self.assertEqual(stub.user_row(2), STUB_USER_ROWS[2])
        self.assertEqual(stub.seqs, dict(RESTORE_FAKE_SEQS, sys_ip_rule_id_seq=(7, "t"),
                                         sys_token_id_seq=(33, "t"), session_event_id_seq=(4, "t"),
                                         sys_login_attempt_id_seq=(9, "t"),
                                         sys_operation_log_id_seq=(6, "t")))
        self.assertEqual(stub.keys, ["plainkey"])
        self.assertFalse(any(s["stamped"] for s in stub.settings))
        self.assertIn("✓ 全等", text)
        self.assertIn("seed 模式", text)
        # 收尾 rc 1：清理面未達 seed 目標（runtime-append 序列於現況缺席＝存在性有差）
        stub = _restore_stub(seqs={k: v for k, v in RESTORE_FAKE_SEQS.items()
                                   if k != "sys_operation_log_id_seq"})
        self._dirty(stub)
        del stub.seqs["sys_operation_log_id_seq"]
        rc, text = self._restore_seed(stub)
        self.assertEqual(rc, RC_DIFF, msg=text)
        self.assertIn("序列｜sys_operation_log_id_seq｜last_value=1,is_called=f｜（無）｜—", text)

    def test_access_log_rows_and_advanced_sequence_are_cleared_in_both_modes(self):
        """存取日誌（ADR-00100 決定 8；008 刀 U1）：基準 0 列而現況 sys_access_log 3 列、sys_access_log_id_seq 前進 → 兩模式 restore 皆
        DELETE 全表清列、收尾 diff rc 0。基準檔模式另 setval 回基準檔之值（樁取 5,true 非預設值、證值自基準檔現讀）；seed 模式不復位
        該序列（runtime-append 序列；走完仍是前進後之值、收尾只比存在性）。表名與序列名手寫。"""
        stub = _restore_stub(seqs=dict(RESTORE_FAKE_SEQS, sys_access_log_id_seq=(5, "t")))
        path = self._baseline(stub)
        stub.tables["sys_access_log"] = 3
        stub.seqs["sys_access_log_id_seq"] = (8, "t")
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        tx = self._tx(stub)
        self.assertIn("DELETE FROM sys_access_log; ", tx)
        self.assertIn("SELECT setval('sys_access_log_id_seq', 5, true); ", tx)
        self.assertEqual((stub.tables["sys_access_log"], stub.seqs["sys_access_log_id_seq"]), (0, (5, "t")))
        self.assertIn("✓ 全等", text)
        stub = _restore_stub()
        stub.tables["sys_access_log"] = 3
        stub.seqs["sys_access_log_id_seq"] = (3, "t")
        rc, text = self._restore_seed(stub)
        self.assertEqual(rc, RC_OK, msg=text)
        tx = self._tx(stub)
        self.assertIn("DELETE FROM sys_access_log; ", tx)
        self.assertNotIn("sys_access_log_id_seq", tx)
        self.assertEqual((stub.tables["sys_access_log"], stub.seqs["sys_access_log_id_seq"]), (0, (3, "t")))
        self.assertIn("✓ 全等", text)

    def test_seed_mode_preconditions_refuse_before_any_write(self):
        """seed 模式之安全帶語意沿用（目標態換成凍結 seed ⊕ 演進合成）：①seed 於清理面任一表有列＝DELETE 全表會毀掉 seed 資料（含
        經手表）②seed 缺清理面之 COPY 段或 setval 行（含經手表段）③演進帳有清理面七表（含 sys_pwd_custody）之 seed_* 登記（仍拒跑之
        演進形①：整表清空面以 seed 恆零列為前提、不入合成；007 刀 U1 起 system_settings 改入合成、不在此拒）——皆 rc 2、零 docker
        呼叫；他表（合成面外之 sys_user_email_verify）登記不擋；④system_settings 值≠期望 seed＝fail-loud 指名、只讀過門鈴清前計數與
        settings 兩句、零寫入。"""
        rowed = SEED_RESTORE_TEXT.replace(
            "COPY public.sys_ip_rule (id, created_at) FROM stdin;\n",
            "COPY public.sys_ip_rule (id, created_at) FROM stdin;\n1\t2026-08-05 00:00:00+00\n")
        self.assertNotEqual(rowed, SEED_RESTORE_TEXT)
        custody_head = "COPY public.sys_pwd_custody (user_id, created_at, created_by) FROM stdin;\n"
        custody_rowed = SEED_RESTORE_TEXT.replace(custody_head, custody_head + "4\t2026-08-05 00:00:00+00\t1\n")
        self.assertNotEqual(custody_rowed, SEED_RESTORE_TEXT)
        for text, needles in (
                (rowed, ("凍結 seed 之清理面非空", "sys_ip_rule 1 列", "seed 模式只服務", "零寫入")),
                (custody_rowed, ("凍結 seed 之清理面非空", "sys_pwd_custody 1 列", "零寫入")),
                (SEED_RESTORE_TEXT.replace("COPY public.sys_operation_log ", "COPY public.other_log "),
                 ("凍結 seed 缺 restore 清理面", "sys_operation_log")),
                (SEED_RESTORE_TEXT.replace("COPY public.sys_pwd_custody ", "COPY public.other_custody "),
                 ("凍結 seed 缺 restore 清理面", "sys_pwd_custody")),
                (SEED_RESTORE_TEXT.replace("public.sys_ip_rule_id_seq'", "public.other_id_seq'"),
                 ("凍結 seed 缺 restore 清理面", "sys_ip_rule_id_seq"))):
            stub = _restore_stub()
            self._dirty(stub)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                self._restore_seed(stub, text)
            for needle in needles:
                self.assertIn(needle, str(ctx.exception), msg=needles)
            self.assertNotIn("restore --seed", str(ctx.exception), msg=needles)   # 補救不得指回自己
            self.assertEqual(stub.log, [], msg=needles)
        other = _ledger_entry("E-001", "seed_update", "sys_user_email_verify",
                              {"pk": {"user_id": 3}, "set": {"verified_email": "u3@example.test"}})
        for eid, table in (("E-002", "sys_ip_rule"), ("E-003", "sys_token"), ("E-004", "sys_pwd_custody")):
            self._write_ledger(other, _ledger_entry(eid, "seed_add", table, {"pk": ["id"], "values": {"id": 1}}))
            stub = _restore_stub()
            self._dirty(stub)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                self._restore_seed(stub)
            for needle in (eid, table, "先擴充本工具", "零寫入"):
                self.assertIn(needle, str(ctx.exception), msg=table)
            self.assertNotIn("E-001", str(ctx.exception), msg=table)
            self.assertEqual(stub.log, [], msg=table)
        self._write_ledger(other)                   # 他表登記不擋
        stub = _restore_stub()
        self._dirty(stub)
        rc, text = self._restore_seed(stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self._write_ledger()
        stub = _restore_stub(settings=_seed_settings_rows(single_session_default="on"))
        self._dirty(stub)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
            self._restore_seed(stub)
        for needle in ("single_session_default", "'on'", "'off'", "002 刀"):
            self.assertIn(needle, str(ctx.exception))
        self.assertEqual([a[-1] for a in stub.log], [SQL_IP_RULE_ROWS, SQL_SETTINGS])   # 清前計數為讀、排在 settings 讀之前（BL-00094）

    def test_main_restore_seed_reads_the_real_frozen_seed_and_honours_user_db(self):
        """main 之 `restore --seed` 走預設左源＝真 repo 凍結 seed ⊕ 真 repo 演進登記檔之合成、零基準檔引數；setval 值＝合成文字
        sys_ip_rule_id_seq 之 setval 行現值（本案以獨立 regex 另讀一次對賬、不寫死數字）。006 刀 U15：樁授權表起手為空、角色列可變欄
        取樁值（≠真檔）——restore 回補合成目標之全數授權列（首列字面手寫對賬；id 集取合成目標、帳上登記演進即隨之）、自 sys_role COPY 段
        回寫三列可變欄，收尾對合成目標之逐列逐欄比對 rc 0（真檔解析＋合成＋寫句＋回讀正規化之端到端）。樁 settings 取合成值、遷移帳
        取真 repo 清單（帳上有合成面之登記時同步前置照驗、恆同步）。"""
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh:
            frozen_text = fh.read()
        with open(os.path.join(REPO_ROOT, SCHEMA_EVOLUTION), encoding="utf-8") as fh:
            real_text = synthesize_seed(frozen_text, json.load(fh)["entries"], SYNTH_TABLES_SEED)
        m = re.search(r"setval\('public\.sys_ip_rule_id_seq', (\d+), (true|false)\)", real_text)
        self.assertIsNotNone(m)
        stub = _restore_stub(settings=[{"setting_key": k, "setting_value": v, "stamped": False}
                                       for k, v in sorted(seed_settings(real_text).items())],
                             ids=dict(STUB_BOUNDED_IDS, casbin_rule=()),
                             tables=dict(RESTORE_FAKE_TABLES, casbin_rule=0))
        self._dirty(stub)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = main([PROG, "restore", "--seed", "--user", "u9", "--db", "d9"], run=stub)
        self.assertEqual(rc, RC_OK, msg=err.getvalue())
        writes = [a[-1] for a in stub.log if "psql" in a and _pg_write_offenders([a[-1]])]
        self.assertEqual(len(writes), 1)
        self.assertIn("INSERT INTO casbin_rule (id, ptype, v0, v1, v2, v3, v4, v5, protected, created_at, created_by) "
                      "VALUES (1, 'p', 'R_SUPER', '/systemManage/getUserList', 'GET', '', '', '', false, "
                      "'2026-08-05T00:00:00+00:00', NULL), (2, ", writes[0])
        want_ids = [r["id"] for r in seed_restore_target(real_text)["casbin_rule_rows"]]
        self.assertTrue(want_ids)
        self.assertEqual((sorted(stub.ids["casbin_rule"]), stub.tables["casbin_rule"]), (want_ids, len(want_ids)))
        self.assertEqual(stub.role_row(1), {"role_home": "home", "status": 1, "role_name": "超級管理員", "role_desc": None,
                                            "role_memo": None, "updated_at": None, "updated_by": None})
        self.assertIn(CASBIN_RESTART_HINT, out.getvalue())
        # 角色／選單／使用者域五支序列（③b）亦自真檔 setval 行現讀：本案以獨立 regex 逐支另讀一次對賬（序列名手寫）
        want = [f"SELECT setval('sys_ip_rule_id_seq', {m.group(1)}, {m.group(2)});"]
        for s in ("sys_role_id_seq", "sys_menu_id_seq", "casbin_rule_id_seq", "sys_casbin_policy_archive_id_seq",
                  "sys_user_id_seq"):
            ms = re.search(r"setval\('public\." + s + r"', (\d+), (true|false)\)", real_text)
            self.assertIsNotNone(ms, msg=s)
            want.append(f"SELECT setval('{s}', {ms.group(1)}, {ms.group(2)});")
        self.assertEqual(re.findall(r"SELECT setval\([^)]*\);", writes[0]), want)
        psqls = [a for a in stub.log if "psql" in a]
        self.assertTrue(psqls and all(a[a.index("-U") + 1] == "u9" and a[a.index("-d") + 1] == "d9"
                                      for a in psqls))

    def test_del_is_named_keys_in_bounded_batches_and_skipped_when_none(self):
        stub = _restore_stub()
        path = self._baseline(stub)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertFalse(any(" DEL " in a[-1] for a in stub.log))   # 零鍵不送空 DEL
        names = [f"throttle:fail:user:u{i:03d}" for i in range(2 * REDIS_DEL_BATCH + 5)]
        stub.keys += names
        stub.log.clear()
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        batches = [shlex.split(a[-1].split(" DEL ", 1)[1]) for a in stub.log if " DEL " in a[-1]]
        self.assertEqual([len(b) for b in batches], [REDIS_DEL_BATCH, REDIS_DEL_BATCH, 5])
        self.assertEqual(sorted(k for b in batches for k in b), sorted(names))

    def test_seed_settings_parse_and_empty_surface(self):
        self.assertEqual(seed_settings(SEED_SETTINGS_TEXT),
                         {"session_idle_timeout": "60", "single_session_default": "off"})
        escaped = SEED_SETTINGS_TEXT.replace("\toff\t", "\ta\\tb\\\\c\t").replace("\t60\t", "\t\\N\t")
        self.assertEqual(seed_settings(escaped),
                         {"session_idle_timeout": None, "single_session_default": "a\tb\\c"})
        for bad in ("",
                    SEED_SETTINGS_TEXT.replace("COPY public.system_settings", "COPY public.other"),
                    SEED_SETTINGS_TEXT.split("session_idle_timeout")[0] + "\\.\n",     # 零列
                    SEED_SETTINGS_TEXT.replace("\tnumber\t60", "\t60"),                # 欄數不符
                    SEED_SETTINGS_TEXT.replace("setting_value", "value")):            # 缺值欄
            with self.assertRaises(BaselineError, msg=bad[:80]):
                seed_settings(bad)
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh:
            real = seed_settings(fh.read())
        self.assertEqual((len(real), real["single_session_default"]), (16, "off"))

    def test_main_restore_defaults_to_frozen_seed_and_honours_user_db(self):
        """main 走預設左源＝真 repo 凍結 seed ⊕ 真 repo 演進登記檔之合成（基準檔模式之合成射程＝system_settings）；樁 settings 取該
        合成值——帳上日後登記 system_settings 之 seed_* 亦綠（左源隨帳合成、007 刀 U1 起不再以拒跑逼擴本工具）。"""
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh, \
                open(os.path.join(REPO_ROOT, SCHEMA_EVOLUTION), encoding="utf-8") as lh:
            real = seed_settings(synthesize_seed(fh.read(), json.load(lh)["entries"], SYNTH_TABLES_BASELINE))
        stub = _restore_stub(settings=[{"setting_key": k, "setting_value": v, "stamped": False}
                                       for k, v in sorted(real.items())])
        path = self._baseline(stub)
        self._dirty(stub)
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = main([PROG, "restore", path, "--user", "u9", "--db", "d9"], run=stub)
        self.assertEqual(rc, RC_OK, msg=err.getvalue())
        psqls = [a for a in stub.log if "psql" in a]
        self.assertTrue(psqls and all(a[a.index("-U") + 1] == "u9" and a[a.index("-d") + 1] == "d9"
                                      for a in psqls))

    # ── 角色／選單域寫面（005 刀 U15、T088②～④）────────────────────────────────

    @staticmethod
    def _dirty_role_menu(stub, casbin=True):
        """模擬角色／選單域走查殘留（走 nextval 形、同 pg：新 id 只看序列——is_called 真＝last_value+1、假＝last_value——不看
        max(id)；序列推進到新 id）：角色／選單／歸檔各一新列＋指派一對（新角色×uid 1）；casbin=True 另加兩列授權。表名與序列名手寫。"""
        def grow(table, seq, n):
            last, called = stub.seqs[seq]
            start = last + 1 if called == "t" else last
            new = list(range(start, start + n))
            stub.ids[table] += new
            stub.tables[table] += n
            stub.seqs[seq] = (new[-1], "t")
            return new

        role = grow("sys_role", "sys_role_id_seq", 1)[0]
        grow("sys_menu", "sys_menu_id_seq", 1)
        grow("sys_casbin_policy_archive", "sys_casbin_policy_archive_id_seq", 1)
        stub.user_roles.append((1, role))
        stub.tables["sys_user_role"] += 1
        if casbin:
            grow("casbin_rule", "casbin_rule_id_seq", 2)

    @staticmethod
    def _tx(stub):
        writes = [a[-1] for a in stub.log if "psql" in a and _pg_write_offenders([a[-1]])]
        assert len(writes) == 1, writes
        return writes[0]

    def test_role_menu_surface_is_bounded_deletes_after_user_role_key_diff_then_setvals(self):
        """③b 寫面逐字＋次序（T088②；007 刀 U1 擴 sys_user）：接在清理面 setval 之後、同一交易；指派鍵集差刪除先於五表（user_id／
        role_id 外鍵 RESTRICT）、五表刪 `id >` 上界（sys_user 居末）、五支 setval 值自基準檔現讀；五表與指派表皆無 DELETE 全表形；
        走完各面回基準、收尾 diff rc 0。"""
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)
        self._dirty_role_menu(stub)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        tx = self._tx(stub)
        self.assertTrue(tx.endswith("SELECT setval('sys_access_log_id_seq', 1, false); "
                                    + BOUNDED_SURFACE_AT_SEED + "COMMIT;"), msg=tx)
        order = [tx.index(s) for s in ("DELETE FROM sys_user_role WHERE", "DELETE FROM sys_role WHERE",
                                       "DELETE FROM sys_menu WHERE", "DELETE FROM casbin_rule WHERE",
                                       "DELETE FROM sys_casbin_policy_archive WHERE", "DELETE FROM sys_user WHERE",
                                       "SELECT setval('sys_role_id_seq'")]
        self.assertEqual(order, sorted(order), msg=order)
        for t in ("sys_role", "sys_menu", "casbin_rule", "sys_casbin_policy_archive", "sys_user", "sys_user_role"):
            self.assertNotIn(f"DELETE FROM {t};", tx)
        self.assertEqual(stub.ids, {t: list(v) for t, v in STUB_BOUNDED_IDS.items()})
        self.assertEqual(sorted(stub.user_roles), list(STUB_USER_ROLES))
        self.assertEqual({t: stub.tables[t] for t in DOMAIN_TABLES},
                         {t: RESTORE_FAKE_TABLES[t] for t in DOMAIN_TABLES})
        self.assertEqual(stub.seqs, RESTORE_FAKE_SEQS)
        self.assertIn("restore ③b", text)
        self.assertIn("✓ 全等", text)

    def test_role_menu_bounds_keys_and_setvals_are_read_from_the_baseline_and_empty_key_set_form(self):
        """上界、鍵集與 setval 值皆自基準檔現讀（樁取非 seed 值）；空鍵集＝`DELETE FROM sys_user_role;`（目標為空表＝全清即正解）；
        archive 上界非 0 時照刪 `id >` 上界（不因 seed 零列而改 DELETE 全表形）。"""
        ids = {"sys_role": (1, 2, 3, 9), "sys_menu": (1, 2), "casbin_rule": (5,), "sys_casbin_policy_archive": (7,),
               "sys_user": (1, 2, 3)}
        stub = _restore_stub(ids=ids, user_roles=((2, 9),),
                             tables=dict(RESTORE_FAKE_TABLES, sys_role=4, sys_menu=2, casbin_rule=1,
                                         sys_casbin_policy_archive=1, sys_user_role=1),
                             seqs=dict(RESTORE_FAKE_SEQS, sys_role_id_seq=(12, "t"), sys_menu_id_seq=(2, "t"),
                                       casbin_rule_id_seq=(5, "t"), sys_casbin_policy_archive_id_seq=(7, "t")))
        path = self._baseline(stub)
        self._dirty_role_menu(stub)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertTrue(self._tx(stub).endswith(
            "DELETE FROM sys_user_role WHERE (user_id, role_id) NOT IN (VALUES (2, 9)); "
            "DELETE FROM sys_role WHERE id > 9; DELETE FROM sys_menu WHERE id > 2; "
            "DELETE FROM casbin_rule WHERE id > 5; DELETE FROM sys_casbin_policy_archive WHERE id > 7; "
            "DELETE FROM sys_user WHERE id > 3; "
            + _t_casbin_insert([_stub_casbin_row(5)]) + " " + _t_user_role_insert(((2, 9),)) + " "
            + "".join(_t_role_update(i, _stub_role_row(i)) + " " for i in (1, 2, 3, 9))
            + "".join(_t_user_update(i, STUB_USER_ROWS[i]) + " " for i in (1, 2, 3)) +
            "SELECT setval('sys_role_id_seq', 12, true); SELECT setval('sys_menu_id_seq', 2, true); "
            "SELECT setval('casbin_rule_id_seq', 5, true); SELECT setval('sys_casbin_policy_archive_id_seq', 7, true); "
            "SELECT setval('sys_user_id_seq', 3, true); "
            "COMMIT;"), msg=self._tx(stub))
        seqs = {s: {"last_value": 1, "is_called": False} for s in BOUNDED_TABLES.values()}
        self.assertEqual(seed_surface_sql(_snap(user_role_keys=[], sequences=seqs))[0], "DELETE FROM sys_user_role;")
        self.assertEqual(seed_surface_sql(_snap(user_role_keys=[[3, 1], [1, 2]], sequences=seqs))[0],
                         "DELETE FROM sys_user_role WHERE (user_id, role_id) NOT IN (VALUES (1, 2), (3, 1));")

    def test_safety_belt_does_not_refuse_role_menu_tables_that_have_rows(self):
        """安全帶「列數非 0 即拒」只套清理面七表：基準檔五表／指派表有列（含 archive 2 列）與凍結 seed 之該面 COPY 有列
        皆照常 restore、不出拒跑句。"""
        stub = _restore_stub(ids=dict(STUB_BOUNDED_IDS, sys_casbin_policy_archive=(1, 2)),
                             tables=dict(RESTORE_FAKE_TABLES, sys_casbin_policy_archive=2),
                             seqs=dict(RESTORE_FAKE_SEQS, sys_casbin_policy_archive_id_seq=(2, "t")))
        path = self._baseline(stub)
        check_restore_baseline(load_snapshot(path))                 # 不拋
        self._dirty_role_menu(stub, casbin=False)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertNotIn("基準非空", text)
        self.assertIn("DELETE FROM sys_casbin_policy_archive WHERE id > 2;", self._tx(stub))
        self.assertEqual(stub.ids["sys_casbin_policy_archive"], [1, 2])
        check_restore_baseline(seed_restore_target(SEED_RESTORE_TEXT), seed_mode=True)   # 不拋
        rc, text = self._restore_seed(_restore_stub())
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertNotIn("清理面非空", text)

    def test_baseline_bound_above_its_sequence_refuses_rc2_and_snapshot_warns(self):
        """★③b 前置（基準檔模式）：基準檔五表任一之 id 上界高於其序列位置（is_called 真＝last_value、假＝last_value-1＝nextval
        已發出之最大值）＝取樣時已有顯式 id 殘列越過序列——照跑則走查以 nextval 造之列落在序列與上界之間、`id >` 上界刪不到，
        序列卻被 setval 回其下＝下一次 nextval 撞 PK。五表逐一（殘列取號段形大 id；007 刀 U1 擴 sys_user）：snapshot rc 0 照寫、stderr
        告警指名；走查後 restore rc 2 指名、零 docker 呼叫＝零寫入；補救句所指之 `restore --seed` 實跑可收（殘列與走查列一併刪、五支序列
        回 seed 值、rc 0）。另釘 is_called 假之邊界（上界 1 對 (1,f)＝nextval 下一值恰為既存之 1）同拒；上界＝序列位置（seed 形）
        不告警；seed 模式同判準、對象＝凍結 seed（setval 低於 COPY 列 id 最大值＝凍結面受損 rc 2、補救不指回自己、零 docker 呼叫）。
        表名與序列名手寫。"""
        big = 9_300_000_001
        seed_ids = {t: list(v) for t, v in STUB_BOUNDED_IDS.items()}
        seed_seqs = {"sys_role_id_seq": (3, "t"), "sys_menu_id_seq": (78, "t"), "casbin_rule_id_seq": (163, "t"),
                     "sys_casbin_policy_archive_id_seq": (1, "f"), "sys_user_id_seq": (3, "t")}

        def snapshot(stub):
            path = os.path.join(self.d, "walk.json")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(main([PROG, "snapshot", path], run=stub), RC_OK)
            self.assertIn("基準已寫", out.getvalue())
            return path, err.getvalue()

        def refused(stub, path, table, seq, bound):
            stub.log.clear()
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([PROG, "restore", path], run=stub), RC_ENV, msg=table)
            for needle in (f"{table} 上界 {bound}", seq, "撞 PK", "零寫入", "restore --seed"):
                self.assertIn(needle, err.getvalue(), msg=(table, needle))
            self.assertEqual(stub.log, [], msg=table)

        for table, seq, ids in (("sys_role", "sys_role_id_seq", (1, 2, 3, big)),
                                ("sys_menu", "sys_menu_id_seq", tuple(range(1, 79)) + (big,)),
                                ("casbin_rule", "casbin_rule_id_seq", tuple(range(1, 164)) + (big,)),
                                ("sys_casbin_policy_archive", "sys_casbin_policy_archive_id_seq", (big,)),
                                ("sys_user", "sys_user_id_seq", (1, 2, 3, big))):
            stub = _restore_stub(ids=dict(STUB_BOUNDED_IDS, **{table: ids}),
                                 tables=dict(RESTORE_FAKE_TABLES, **{table: len(ids)}))
            path, warned = snapshot(stub)
            for needle in ("告警", f"{table} 上界 {big}", seq, "restore --seed"):
                self.assertIn(needle, warned, msg=(table, needle))
            self._dirty_role_menu(stub)                     # 走查以 nextval 造列：新 id 落在序列與上界之間
            refused(stub, path, table, seq, big)
            rc, text = self._restore_seed(stub)             # 補救句所指之 seed 模式實跑可收
            self.assertEqual(rc, RC_OK, msg=(table, text))
            self.assertEqual(stub.ids, seed_ids, msg=table)
            self.assertEqual({s: stub.seqs[s] for s in seed_seqs}, seed_seqs, msg=table)
        stub = _restore_stub(ids=dict(STUB_BOUNDED_IDS, sys_casbin_policy_archive=(1,)),
                             tables=dict(RESTORE_FAKE_TABLES, sys_casbin_policy_archive=1))
        path, warned = snapshot(stub)
        self.assertIn("sys_casbin_policy_archive 上界 1", warned)
        refused(stub, path, "sys_casbin_policy_archive", "sys_casbin_policy_archive_id_seq", 1)
        _, warned = snapshot(_restore_stub())               # 上界＝序列位置（seed 形）＝不告警
        self.assertEqual(warned, "")
        damaged = SEED_RESTORE_TEXT.replace("setval('public.sys_menu_id_seq', 78, true)",
                                            "setval('public.sys_menu_id_seq', 77, true)")
        self.assertNotEqual(damaged, SEED_RESTORE_TEXT)
        stub = _restore_stub()                              # seed 模式：凍結 seed 之上界高於其 setval 位置＝凍結面受損
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
            self._restore_seed(stub, damaged)
        for needle in ("凍結 seed 之角色／選單／使用者域上界高於其序列位置", "sys_menu 上界 78", "凍結面受損", "零寫入"):
            self.assertIn(needle, str(ctx.exception))
        self.assertNotIn("restore --seed", str(ctx.exception))   # 補救不得指回自己
        self.assertEqual(stub.log, [])

    def test_restart_hint_iff_restore_deleted_casbin_rows_or_changed_its_sequence(self):
        """T088④重啟句（restore 步⑥）：字面逐字釘；刪過 casbin_rule 列或改過其序列＝收尾輸出一次（兩模式皆然）——兩腿各自獨立成案：「只刪列」
        ＝顯式 id 直插、序列停在目標值（走查以 psql 顯式 id 直植 casbin_rule 之形、不經 nextval），「只改序列」＝列未增、序列三形各自
        成案——前進（170,t）／後退（160,t）／is_called 異（163,f）（判準是 (last_value, is_called) 元組之「≠」、不是「前進」：
        只比 last_value 或只判大於之判準會漏後兩形）；兩腿之參照值＝目標上界／目標序列值各自區辨：上列各形之目標皆上界 163＝序列
        (163,t)、比錯參照也測不出，另設目標上界 163＜序列 (166,t) 之形（上界低於序列位置＝合法基準、bounds_above_sequence 不拒；
        基準檔模式取自樁、seed 模式以改過 setval 行之樁 seed 造出）——顯式 id 165 直插（落在兩參照值之間）、序列未動＝輸出一次
        （刪列腿誤比目標序列值會漏）、全未動＝不輸出（序列腿誤比目標上界會誤報）；只動角色／選單／歸檔／指派或全未動＝不輸出；
        交易失敗（整筆回滾）＝不輸出；提交後步驟失敗（DEL 回非整數）＝仍輸出（finally）。"""
        self.assertEqual(RUST_API_RESTART_CLI,
                         "docker compose -f docker-compose.yml -f docker-compose.dev.yml restart rust-api")
        self.assertEqual(CASBIN_RESTART_HINT,
                         "[walkthrough-baseline] ★MUST 重啟 rust-api：本次 restore 以 SQL 直改 casbin_rule（刪列、回補列或改序列）、"
                         "判定面無外部通知管道——執行中的 rust-api 仍持 restore 前之政策集、重啟即自庫重載；照抄："
                         "docker compose -f docker-compose.yml -f docker-compose.dev.yml restart rust-api")

        def seq_only(value):
            def dirt(stub):
                self.assertEqual(stub.seqs["casbin_rule_id_seq"], (163, "t"))   # 前置自證：目標值、髒形須與之異
                stub.seqs["casbin_rule_id_seq"] = value
            return dirt

        def rows_only(stub):
            # 顯式大 id 直插、不經 nextval：列 id > 上界 163、序列停在目標值＝只「刪列」腿成立（前置自證、免本案退化成兩腿齊成立）
            stub.ids["casbin_rule"] += [900, 901]
            stub.tables["casbin_rule"] += 2
            self.assertEqual(stub.seqs["casbin_rule_id_seq"], (163, "t"))

        for label, dirt, want in (("casbin 列＋序列（nextval 形）", lambda s: self._dirty_role_menu(s), 1),
                                  ("casbin 只刪列（顯式 id、序列未動）", rows_only, 1),
                                  ("casbin 只改序列：前進", seq_only((170, "t")), 1),
                                  ("casbin 只改序列：後退", seq_only((160, "t")), 1),
                                  ("casbin 只改序列：is_called 異", seq_only((163, "f")), 1),
                                  ("非 casbin 面", lambda s: self._dirty_role_menu(s, casbin=False), 0),
                                  ("全未動", lambda s: None, 0)):
            stub = _restore_stub()
            path = self._baseline(stub)
            dirt(stub)
            rc, text = self._restore(path, stub)
            self.assertEqual(rc, RC_OK, msg=(label, text))
            self.assertEqual(text.count("MUST 重啟 rust-api"), want, msg=label)
            self.assertIn("DELETE FROM casbin_rule WHERE id > 163;", self._tx(stub), msg=label)
            self.assertEqual(stub.ids["casbin_rule"], list(range(1, 164)), msg=label)
            if want:
                self.assertTrue(text.rstrip("\n").endswith(CASBIN_RESTART_HINT), msg=(label, text))
                self.assertEqual(stub.seqs["casbin_rule_id_seq"], (163, "t"), msg=label)
            stub = _restore_stub()                              # seed 模式同判準
            dirt(stub)
            rc, text = self._restore_seed(stub)
            self.assertEqual(rc, RC_OK, msg=(label, text))
            self.assertEqual(text.count("MUST 重啟 rust-api"), want, msg=("seed", label))
            self.assertEqual(text.count(CASBIN_RESTART_HINT), want, msg=("seed", label))
            self.assertIn("DELETE FROM casbin_rule WHERE id > 163;", self._tx(stub), msg=("seed", label))
            self.assertEqual(stub.ids["casbin_rule"], list(range(1, 164)), msg=("seed", label))
        # 兩參照值各自區辨：目標上界 163＜目標序列 (166,t)；顯式 id 165 落在兩值之間（高於上界、不高於序列值）
        gap_seed = SEED_RESTORE_TEXT.replace("setval('public.casbin_rule_id_seq', 163, true)",
                                             "setval('public.casbin_rule_id_seq', 166, true)")
        self.assertNotEqual(gap_seed, SEED_RESTORE_TEXT)
        for label, explicit, want in (("上界＜序列：只刪列（顯式 id 165、序列未動）", [165], 1),
                                      ("上界＜序列：全未動", [], 0)):
            for seed_mode in (False, True):
                msg = (label, "seed" if seed_mode else "基準檔")
                stub = _restore_stub(seqs=dict(RESTORE_FAKE_SEQS, casbin_rule_id_seq=(166, "t")))
                path = None if seed_mode else self._baseline(stub)
                stub.ids["casbin_rule"] += explicit
                stub.tables["casbin_rule"] += len(explicit)
                rc, text = self._restore_seed(stub, gap_seed) if seed_mode else self._restore(path, stub)
                self.assertEqual(rc, RC_OK, msg=(msg, text))
                self.assertEqual(text.count("MUST 重啟 rust-api"), want, msg=msg)
                self.assertEqual(text.count(CASBIN_RESTART_HINT), want, msg=msg)
                tx = self._tx(stub)
                self.assertIn("DELETE FROM casbin_rule WHERE id > 163;", tx, msg=msg)
                self.assertIn("SELECT setval('casbin_rule_id_seq', 166, true);", tx, msg=msg)
                self.assertEqual(stub.ids["casbin_rule"], list(range(1, 164)), msg=msg)
                self.assertEqual(stub.seqs["casbin_rule_id_seq"], (166, "t"), msg=msg)
        stub = _restore_stub()                                  # 交易失敗＝整筆回滾＝未動
        path = self._baseline(stub)
        self._dirty_role_menu(stub)
        stub.fail = "tx"
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(BaselineError):
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        self.assertNotIn("MUST 重啟 rust-api", out.getvalue())
        stub = _restore_stub()                                  # 提交後失敗＝已動、仍須重啟
        path = self._baseline(stub)
        self._dirty(stub)
        self._dirty_role_menu(stub)
        stub.fail = "del"
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(BaselineError):
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        self.assertIn(CASBIN_RESTART_HINT, out.getvalue())
        stub = _restore_stub(garble="casbin")                   # 現讀輸出壞形＝寫入前 rc 2
        path = self._baseline(stub)
        self._dirty_role_menu(stub)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        self.assertIn("casbin_rule", str(ctx.exception))
        self.assertEqual(_pg_write_offenders([a[-1] for a in stub.log if "psql" in a]), [])

    def test_seed_mode_role_menu_surface_targets_frozen_seed_bounds_keys_and_setvals(self):
        """seed 模式新腿（T088③）：目標上界＝seed COPY 列 id 最大值、setval 值＝seed setval 行（樁把 sys_role_id_seq 改
        9,true≠上界 3，證兩值各自現讀）、指派鍵集＝seed COPY 鍵集；寫面逐字；走完五表回 seed 形、收尾 rc 0。"""
        text = SEED_RESTORE_TEXT.replace("setval('public.sys_role_id_seq', 3, true)",
                                         "setval('public.sys_role_id_seq', 9, true)")
        self.assertNotEqual(text, SEED_RESTORE_TEXT)
        stub = _restore_stub()
        self._dirty(stub)
        self._dirty_role_menu(stub)
        rc, out = self._restore_seed(stub, text)
        self.assertEqual(rc, RC_OK, msg=out)
        self.assertTrue(self._tx(stub).endswith(
            "SELECT setval('sys_ip_rule_id_seq', 7, true); "
            + BOUNDED_SURFACE_AT_SEED.replace("setval('sys_role_id_seq', 3, true)", "setval('sys_role_id_seq', 9, true)")
            + "COMMIT;"), msg=self._tx(stub))
        self.assertEqual(stub.ids, {t: list(v) for t, v in STUB_BOUNDED_IDS.items()})
        self.assertEqual(sorted(stub.user_roles), list(STUB_USER_ROLES))
        self.assertEqual(stub.seqs["sys_role_id_seq"], (9, "t"))
        self.assertIn(CASBIN_RESTART_HINT, out)
        # 收尾判準面含該面：seed 選單列被硬刪（不在回補射程）＝rc 1 指名；★seed 指派對被刪＝回補、收尾不再報（007 刀 U1 翻轉：
        # 舊形「指派對被刪不在回補射程＝rc 1」）
        stub = _restore_stub()
        stub.ids["sys_menu"].remove(5)
        stub.tables["sys_menu"] -= 1
        stub.user_roles.remove((2, 2))
        stub.tables["sys_user_role"] -= 1
        rc, out = self._restore_seed(stub)
        self.assertEqual(rc, RC_DIFF, msg=out)
        self.assertIn("表｜sys_menu｜78｜77｜-1", out)
        self.assertNotIn("sys_user_role(2,2)", out)
        self.assertIn((2, 2), stub.user_roles)
        stub = _restore_stub()
        stub.user_roles.remove((2, 2))
        stub.tables["sys_user_role"] -= 1
        rc, out = self._restore_seed(stub)
        self.assertEqual(rc, RC_OK, msg=out)
        self.assertEqual(sorted(stub.user_roles), list(STUB_USER_ROLES))

    def test_seed_mode_closing_check_reports_rule_and_role_row_residue(self):
        """seed 模式⑤收尾判準面含授權列與角色列兩欄（T072；反向腿、兩欄各自成案）：射程外殘差＝rc 1 並逐列逐欄指名——
        ①seed 授權列 10 之 protected 被就地改寫（回補 ON CONFLICT DO NOTHING 不還原之形）；②seed 角色列 3 被硬刪（回寫只改
        在場之列；真庫外鍵 RESTRICT＝其指派對先刪）。判準面若改取現況值＝兩殘差皆看不見、收尾假綠。②之樁 seed 去掉 (3, 3) 指派
        （007 刀 U1 起指派回補排在一切刪除之後：目標含 (3, 3) 而角色 3 已不在＝回補撞外鍵、整筆回滾 rc 2，非本案所驗之收尾面）。"""
        stub = _restore_stub()
        stub.casbin[10] = dict(_stub_casbin_row(10), protected=False)
        rc, out = self._restore_seed(stub)
        self.assertEqual(rc, RC_DIFF, msg=out)
        self.assertIn("授權列｜casbin_rule(id=10).protected｜true｜false｜—", out)
        no33 = SEED_RESTORE_TEXT.replace("\n1\t1\n2\t2\n3\t3\n", "\n1\t1\n2\t2\n")
        self.assertNotEqual(no33, SEED_RESTORE_TEXT)
        stub = _restore_stub()
        stub.user_roles.remove((3, 3))
        stub.tables["sys_user_role"] -= 1
        stub.ids["sys_role"].remove(3)
        stub.tables["sys_role"] -= 1
        rc, out = self._restore_seed(stub, no33)
        self.assertEqual(rc, RC_DIFF, msg=out)
        self.assertIn("角色列｜sys_role(id=3)｜有｜（無）｜-1", out)

    def test_seed_target_parses_role_menu_copy_segments_and_refuses_damage(self):
        """凍結 seed 之角色／選單／使用者域六段解析（樁＋真檔皆 3／78／163／0／3 列、指派 3 對）；段首缺 id 欄／id 非整數／指派列欄數
        不符＝凍結面受損 rc 2；缺 COPY 段或 setval 行＝指名清理面缺席；皆零 docker 呼叫。"""
        want_bounds = {"sys_role": 3, "sys_menu": 78, "casbin_rule": 163, "sys_casbin_policy_archive": 0, "sys_user": 3}
        want_seqs = {"sys_role_id_seq": {"last_value": 3, "is_called": True},
                     "sys_menu_id_seq": {"last_value": 78, "is_called": True},
                     "casbin_rule_id_seq": {"last_value": 163, "is_called": True},
                     "sys_casbin_policy_archive_id_seq": {"last_value": 1, "is_called": False},
                     "sys_user_id_seq": {"last_value": 3, "is_called": True}}
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh:
            real_text = fh.read()
        for text in (SEED_RESTORE_TEXT, real_text):
            target = seed_restore_target(text)
            self.assertEqual(target["id_bounds"], want_bounds)
            self.assertEqual(target["user_role_keys"], [[1, 1], [2, 2], [3, 3]])
            self.assertEqual({t: target["tables"][t] for t in DOMAIN_TABLES},
                             {"sys_role": 3, "sys_menu": 78, "casbin_rule": 163, "sys_casbin_policy_archive": 0,
                              "sys_user": 3, "sys_user_role": 3})
            self.assertEqual({s: target["sequences"][s] for s in want_seqs}, want_seqs)
            # 006 刀 U15：授權列全欄 163 列（依 id 排序；COPY 段之文字序非數字序）、角色列 3 列之可變欄；時間欄＝正規形
            self.assertEqual([r["id"] for r in target["casbin_rule_rows"]], list(range(1, 164)))
            self.assertEqual([r["id"] for r in target["sys_role_rows"]], [1, 2, 3])
        self.assertEqual(seed_restore_target(SEED_RESTORE_TEXT)["casbin_rule_rows"],
                         [_stub_casbin_row(i) for i in range(1, 164)])
        self.assertEqual(seed_restore_target(SEED_RESTORE_TEXT)["sys_role_rows"],
                         [dict({"id": i}, **STUB_ROLE_ROWS[i]) for i in (1, 2, 3)])
        real = seed_restore_target(real_text)
        self.assertEqual(real["casbin_rule_rows"][9], {
            "id": 10, "ptype": "p", "v0": "R_SUPER", "v1": "manage_role", "v2": "menu", "v3": "", "v4": "", "v5": "",
            "protected": True, "created_at": "2026-08-05T00:00:00+00:00", "created_by": None})
        self.assertEqual(real["sys_role_rows"][2], {
            "id": 3, "role_home": "home", "status": 1, "role_name": "普通用戶", "role_desc": None, "role_memo": None,
            "updated_at": None, "updated_by": None})
        casbin_head = ("COPY public.casbin_rule (id, ptype, v0, v1, v2, v3, v4, v5, protected, created_at, created_by) "
                       "FROM stdin;\n")
        row9 = "\t".join(_t_copy(_stub_casbin_row(9, STUB_TS_COPY)[c]) for c in STUB_CASBIN_COLUMNS) + "\n"
        self.assertIn(row9, SEED_RESTORE_TEXT)
        for bad, needle in (
                (SEED_RESTORE_TEXT.replace("COPY public.sys_role (id, ", "COPY public.sys_role (rid, "), "sys_role"),
                (SEED_RESTORE_TEXT.replace("\n2\t2026-08-05 00:00:00+00\tR_2\t", "\nx\t2026-08-05 00:00:00+00\tR_2\t"),
                 "sys_role"),
                (SEED_RESTORE_TEXT.replace("\n2\t2\n3\t3\n", "\n2\t2\t9\n3\t3\n"), "sys_user_role"),
                # 006 刀 U15：授權列與角色列兩段之欄型受損（段首缺欄、bool 非 t／f、時間不可解、非空欄為 \N、整數欄非整數）
                (SEED_RESTORE_TEXT.replace(casbin_head, casbin_head.replace("protected, ", "")), "casbin_rule"),
                (SEED_RESTORE_TEXT.replace(row9, row9.replace("\tf\t2026", "\tx\t2026")), "casbin_rule"),
                (SEED_RESTORE_TEXT.replace(row9, row9.replace(STUB_TS_COPY, "2026-08-05 00:00:00")), "casbin_rule"),
                (SEED_RESTORE_TEXT.replace(row9, row9.replace("\tGET\t", "\t\\N\t")), "casbin_rule"),
                (SEED_RESTORE_TEXT.replace("\tR_2\t\\N\t管理員\t1\t", "\tR_2\t\\N\t管理員\tone\t"), "sys_role")):
            self.assertNotEqual(bad, SEED_RESTORE_TEXT)
            with self.assertRaises(BaselineError, msg=needle) as ctx:
                seed_restore_target(bad)
            self.assertIn(needle, str(ctx.exception))
            self.assertIn("凍結面受損", str(ctx.exception))
        for bad, needle in (
                (SEED_RESTORE_TEXT.replace("COPY public.sys_menu ", "COPY public.other_menu "), "sys_menu"),
                (SEED_RESTORE_TEXT.replace("COPY public.sys_user_role ", "COPY public.other_ur "), "sys_user_role"),
                (SEED_RESTORE_TEXT.replace("public.casbin_rule_id_seq'", "public.other_id_seq'"), "casbin_rule_id_seq")):
            self.assertNotEqual(bad, SEED_RESTORE_TEXT)
            stub = _restore_stub()
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                self._restore_seed(stub, bad)
            self.assertIn("凍結 seed 缺 restore 清理面", str(ctx.exception))
            self.assertIn(needle, str(ctx.exception))
            self.assertEqual(stub.log, [])

    def test_seed_mode_domain_table_seed_entries_are_synthesized_not_refused(self):
        """seed 模式之角色／選單／使用者域六表 seed_* 登記＝入合成、不拒跑（007 刀 U1 翻轉舊形「該域有登記即拒」）：六表各一筆（角色列改名、
        選單增列、授權列刪列、歸檔增列、指派增對、帳號改暱稱）且現庫已套用＋走查殘列 → 目標態＝凍結 seed ⊕ 合成：遷移定義之列與欄值皆
        保留（不被回補、刪除或回寫成凍結值）、增列之序列隨 GR9 推進（選單 (79, true)、歸檔 (1, false)→(1, true)）、殘列清除、收尾 rc 0。
        左源若退回凍結段＝restore 把上列遷移效果逐一反做（本案逐表斷言其存續）。"""
        self._write_ledger(
            _ledger_entry("E-001", "seed_update", "sys_role", {"pk": {"id": 2}, "set": {"role_name": "管理員（演進）"}}),
            _ledger_entry("E-002", "seed_add", "sys_menu", {"pk": ["id"], "values": {"id": 79, "order": 79, "menu_name": "m79"}}),
            _ledger_entry("E-003", "seed_delete", "casbin_rule", {"pk": {"id": 50}}),
            _ledger_entry("E-004", "seed_add", "sys_casbin_policy_archive",
                          {"pk": ["id"], "values": {"id": 1, "role_id": 1, "ptype": "p"}}),
            _ledger_entry("E-005", "seed_add", "sys_user_role", {"pk": ["user_id", "role_id"],
                                                                 "values": {"user_id": 1, "role_id": 2}}),
            _ledger_entry("E-006", "seed_update", "sys_user", {"pk": {"id": 3}, "set": {"nick_name": "User03"}}))
        stub = _restore_stub()
        stub.roles[2] = dict(stub.role_row(2), role_name="管理員（演進）")      # 現庫已套用（樁上手寫施作）
        stub.ids["sys_menu"].append(79)
        stub.tables["sys_menu"] += 1
        stub.seqs["sys_menu_id_seq"] = (79, "t")
        stub.ids["casbin_rule"].remove(50)
        stub.tables["casbin_rule"] -= 1
        stub.ids["sys_casbin_policy_archive"].append(1)
        stub.tables["sys_casbin_policy_archive"] += 1
        stub.seqs["sys_casbin_policy_archive_id_seq"] = (1, "t")
        stub.user_roles.append((1, 2))
        stub.tables["sys_user_role"] += 1
        stub.users[3] = dict(stub.user_row(3), nick_name="User03")
        self._dirty(stub)
        self._dirty_user_domain(stub)                                           # 走查殘列（帳號 4、指派、經手表、cpwd）
        rc, text = self._restore_seed(stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertEqual(stub.role_row(2)["role_name"], "管理員（演進）")
        self.assertEqual((max(stub.ids["sys_menu"]), stub.seqs["sys_menu_id_seq"]), (79, (79, "t")))
        self.assertNotIn(50, stub.ids["casbin_rule"])
        self.assertEqual((stub.ids["sys_casbin_policy_archive"], stub.seqs["sys_casbin_policy_archive_id_seq"]), ([1], (1, "t")))
        self.assertEqual(sorted(stub.user_roles), [(1, 1), (1, 2), (2, 2), (3, 3)])
        self.assertEqual((stub.user_row(3)["nick_name"], stub.ids["sys_user"]), ("User03", [1, 2, 3]))
        tx = self._tx(stub)
        for s in ("DELETE FROM sys_menu WHERE id > 79;", "DELETE FROM sys_casbin_policy_archive WHERE id > 1;",
                  "SELECT setval('sys_menu_id_seq', 79, true);", "SELECT setval('sys_casbin_policy_archive_id_seq', 1, true);"):
            self.assertIn(s, tx)
        self.assertIn("✓ 全等", text)

    # ── 授權列回補與角色列回寫（006 刀 U15、T072②～⑤）──────────────────────────────

    def test_casbin_backfill_follows_bounded_deletes_then_role_writeback_then_setvals(self):
        """★序釘（T072②；理同測試守衛之授權腿 Drop 序）：回補句排在五表刪上界列之後——走查復原以新 id 回插同身分列時，先補則
        `ON CONFLICT DO NOTHING` 被身分鍵吞掉、新列隨後被刪＝seed 列永久缺席；★指派回補（007 刀 U1）排在一切刪除與授權列回補之後
        （先補再刪＝新帳號之指派先被補、其列卻要刪＝外鍵 RESTRICT）；角色列回寫、使用者列回寫依序接在其後、五支 setval 之前；兩種回補句
        各恰一句、回寫句恰每目標列一句。"""
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty_role_menu(stub)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        tx = self._tx(stub)
        marks = ("DELETE FROM sys_user_role WHERE", "DELETE FROM sys_role WHERE id >", "DELETE FROM sys_menu WHERE id >",
                 "DELETE FROM casbin_rule WHERE id >", "DELETE FROM sys_casbin_policy_archive WHERE id >",
                 "DELETE FROM sys_user WHERE id >", "INSERT INTO casbin_rule ", "INSERT INTO sys_user_role ",
                 "UPDATE sys_role SET ", "UPDATE sys_user SET nick_name", "SELECT setval('sys_role_id_seq'")
        order = [tx.index(s) for s in marks]
        self.assertEqual(order, sorted(order), msg=order)
        self.assertEqual((tx.count("INSERT INTO casbin_rule "), tx.count("INSERT INTO sys_user_role "),
                          tx.count("UPDATE sys_role SET "), tx.count("UPDATE sys_user SET nick_name")), (1, 1, 3, 3))
        self.assertLess(tx.rindex("UPDATE sys_role SET "), tx.index("UPDATE sys_user SET nick_name"))
        self.assertLess(tx.rindex("UPDATE sys_user SET nick_name"), tx.index("SELECT setval('sys_role_id_seq'"))
        self.assertTrue(tx.index("ON CONFLICT DO NOTHING;") < tx.index("UPDATE sys_role SET "))

    def test_backfill_and_role_writeback_statement_forms(self):
        """回補句與回寫句字面（T072②；007 刀 U1 擴指派回補與使用者列回寫）：回補＝目標列全欄原值（原 id、字串經跳脫、bool／NULL
        字面）＋ON CONFLICT DO NOTHING；指派回補＝目標鍵集一句＋ON CONFLICT DO NOTHING；回寫＝可變欄（角色列七欄、使用者列十二欄——
        含密碼雜湊、審計欄與軟刪兩欄）設回目標值、且只在 id 相符而可變欄與目標不等（IS DISTINCT FROM）時寫；目標各欄為空＝不出回補句
        與回寫句。"""
        seqs = {s: {"last_value": 1, "is_called": False} for s in BOUNDED_TABLES.values()}
        stamped = dict({"id": 2}, **dict(STUB_ROLE_ROWS[2], status=None, updated_by=1,
                                          updated_at="2026-10-04T08:00:00.500000+00:00"))
        snap = _snap(sequences=seqs, casbin_rule_rows=[_stub_casbin_row(7), dict(_stub_casbin_row(10), created_by=5)],
                     sys_role_rows=[stamped, dict({"id": 3}, **STUB_ROLE_ROWS[3])])
        surface = seed_surface_sql(snap)
        self.assertIn(
            "INSERT INTO casbin_rule (id, ptype, v0, v1, v2, v3, v4, v5, protected, created_at, created_by) VALUES "
            "(7, 'p', 'R_SUPER', '/stub/o''api7', 'GET', '', '', '', false, '2026-08-05T00:00:00+00:00', NULL), "
            "(10, 'p', 'R_SUPER', '/stub/api10', 'GET', '', '', '', true, '2026-08-05T00:00:00+00:00', 5) "
            "ON CONFLICT DO NOTHING;", surface)
        self.assertIn(
            "UPDATE sys_role SET role_home = 'home', status = NULL, role_name = '管理員', role_desc = NULL, "
            "role_memo = '備註', updated_at = '2026-10-04T08:00:00.500000+00:00', updated_by = 1 WHERE id = 2 AND "
            "(role_home, status, role_name, role_desc, role_memo, updated_at, updated_by) IS DISTINCT FROM "
            "('home', NULL, '管理員', NULL, '備註', '2026-10-04T08:00:00.500000+00:00', 1);", surface)
        self.assertIn(
            "UPDATE sys_role SET role_home = 'home', status = 1, role_name = '普通用戶', role_desc = 'it''s 描述', "
            "role_memo = NULL, updated_at = NULL, updated_by = NULL WHERE id = 3 AND "
            "(role_home, status, role_name, role_desc, role_memo, updated_at, updated_by) IS DISTINCT FROM "
            "('home', 1, '普通用戶', 'it''s 描述', NULL, NULL, NULL);", surface)
        self.assertIn("INSERT INTO sys_user_role (user_id, role_id) VALUES (1, 1), (2, 2), (3, 3) ON CONFLICT DO NOTHING;",
                      surface)
        deleted = dict({"id": 4}, **dict(_stub_user_row(4), user_gender=2, user_phone="0912", user_email="u4@example.test",
                                          status=2, session_policy="single", user_memo="it's 記事",
                                          updated_at="2026-10-06T09:00:00+00:00", updated_by=1,
                                          deleted_at="2026-10-06T09:30:00.250000+00:00", deleted_by=1))
        surface = seed_surface_sql(_snap(sequences=seqs, sys_user_rows=[deleted],
                                         id_bounds=dict(_snap()["id_bounds"], sys_user=4)))
        self.assertIn(
            "UPDATE sys_user SET nick_name = '走查帳號4', user_gender = 2, user_phone = '0912', "
            "user_email = 'u4@example.test', status = 2, session_policy = 'single', user_memo = 'it''s 記事', "
            f"password = '{_stub_pw(4)}', updated_at = '2026-10-06T09:00:00+00:00', updated_by = 1, "
            "deleted_at = '2026-10-06T09:30:00.250000+00:00', deleted_by = 1 WHERE id = 4 AND "
            "(nick_name, user_gender, user_phone, user_email, status, session_policy, user_memo, password, updated_at, "
            "updated_by, deleted_at, deleted_by) IS DISTINCT FROM ('走查帳號4', 2, '0912', 'u4@example.test', 2, 'single', "
            f"'it''s 記事', '{_stub_pw(4)}', '2026-10-06T09:00:00+00:00', 1, '2026-10-06T09:30:00.250000+00:00', 1);",
            surface)
        empty = seed_surface_sql(_snap(sequences=seqs, casbin_rule_rows=[], sys_role_rows=[], sys_user_rows=[],
                                       user_role_keys=[]))
        self.assertFalse([s for s in empty if s.startswith(("INSERT", "UPDATE"))], msg=empty)
        self.assertEqual(len(empty), 1 + 5 + 5)

    def test_restart_hint_when_only_a_backfill_is_pending(self):
        """T072④：casbin_rule 無上界以上之列、序列未動（＝刪列與改序列兩腿皆不成立、前置自證）而目標授權列有被刪者（寫入前現讀
        判「將回補 ≥1 列」）＝收尾輸出重啟句恰一次、並報缺列數；被刪列取中段（50）與上界列（163：現況 max 降為 162、仍不高於目標
        上界）兩形；兩模式皆然；回補後該列原 id 在。"""
        for victim in (50, 163):
            for seed_mode in (False, True):
                msg = (victim, "seed" if seed_mode else "基準檔")
                stub = _restore_stub()
                path = None if seed_mode else self._baseline(stub)
                stub.ids["casbin_rule"].remove(victim)
                stub.tables["casbin_rule"] -= 1
                self.assertEqual(stub.seqs["casbin_rule_id_seq"], (163, "t"), msg=msg)
                self.assertLessEqual(max(stub.ids["casbin_rule"]), 163, msg=msg)
                rc, text = self._restore_seed(stub) if seed_mode else self._restore(path, stub)
                self.assertEqual(rc, RC_OK, msg=(msg, text))
                self.assertEqual(text.count(CASBIN_RESTART_HINT), 1, msg=msg)
                self.assertIn("寫入前現讀缺 1 列", text, msg=msg)
                self.assertIn(victim, stub.ids["casbin_rule"], msg=msg)
        stub = _restore_stub(garble="casbin_ids")                 # 現讀 id 集壞形＝寫入前 rc 2
        path = self._baseline(stub)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        self.assertIn("ids", str(ctx.exception))
        self.assertEqual(_pg_write_offenders([a[-1] for a in stub.log if "psql" in a]), [])

    def test_revoked_seed_grant_reinserted_with_new_id_and_edited_seed_role_restore_to_zero_diff(self):
        """★US5 AS2 之工具面合成案（T072⑤；走查本身不撤 seed 列＝spec Clarifications 第六題）：seed 授權列 50 被撤（硬刪＋歸檔表
        nextval 一列）→ 以新 id 回插同身分列（復原之形：nextval 164、建立時點與建立者換新）＋seed 角色列 2 可變欄被改（首頁、狀態
        與審計欄）＋清理面殘留。restore 前 diff 看得見兩欄之差（rc 1）；restore 後列 50 原 id 原值在、新 id 列無、角色列 2 回目標值
        與目標審計欄、序列回目標值、重啟句出現、收尾 diff rc 0＝全等；兩模式（基準檔／seed）皆然。"""
        def nextval(stub, table, seq):
            last, called = stub.seqs[seq]
            new = last + 1 if called == "t" else last
            stub.ids[table].append(new)
            stub.tables[table] += 1
            stub.seqs[seq] = (new, "t")
            return new

        for seed_mode in (False, True):
            label = "seed" if seed_mode else "基準檔"
            stub = _restore_stub()
            path = None if seed_mode else self._baseline(stub)
            want50, want2 = stub.casbin_row(50), stub.role_row(2)
            self._dirty(stub)
            stub.ids["casbin_rule"].remove(50)                    # 撤銷：seed 列 50 刪除、歸檔一列
            stub.tables["casbin_rule"] -= 1
            nextval(stub, "sys_casbin_policy_archive", "sys_casbin_policy_archive_id_seq")
            new = nextval(stub, "casbin_rule", "casbin_rule_id_seq")   # 復原：同身分以新 id 回插
            self.assertEqual(new, 164, msg=label)
            stub.casbin[new] = dict(want50, id=new, created_at="2026-10-04T09:30:00.123456+00:00", created_by=1)
            stub.roles[2] = dict(want2, role_home="manage_role", status=2,
                                 updated_at="2026-10-04T09:31:00+00:00", updated_by=1)
            if not seed_mode:
                err = io.StringIO()
                with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main([PROG, "diff", path], run=stub), RC_DIFF)
                for needle in ("授權列｜casbin_rule(id=50)｜有｜（無）｜-1",
                               '角色列｜sys_role(id=2).role_home｜"home"｜"manage_role"｜—',
                               "角色列｜sys_role(id=2).updated_by｜null｜1｜—"):
                    self.assertIn(needle, err.getvalue())
                stub.log.clear()
            rc, text = self._restore_seed(stub) if seed_mode else self._restore(path, stub)
            self.assertEqual(rc, RC_OK, msg=(label, text))
            self.assertIn("✓ 全等", text, msg=label)
            self.assertEqual(stub.casbin_row(50), want50, msg=label)
            self.assertNotIn(new, stub.ids["casbin_rule"], msg=label)
            self.assertEqual(sorted(stub.ids["casbin_rule"]), list(range(1, 164)), msg=label)
            self.assertEqual(stub.role_row(2), want2, msg=label)
            self.assertEqual(stub.role_row(1), dict(STUB_ROLE_ROWS[1]), msg=label)
            self.assertEqual(stub.seqs["casbin_rule_id_seq"], (163, "t"), msg=label)
            self.assertEqual(text.count(CASBIN_RESTART_HINT), 1, msg=label)

    # ── 使用者域寫面與遷移帳前置（007 刀 U1、T006）────────────────────────────────

    def test_user_domain_restores_to_baseline_with_exact_statements_in_fixed_order(self):
        """★US6 場景 3（T006①）：基準＝seed 三帳號、鍵集 [[1,1],[2,2],[3,3]]、經手表 0、cpwd 0；現況＝(2, 2) 被刪、新帳號列 id 4 與其
        指派、seed 帳號 2 之 nick_name 與 password 被改、經手表一列、cpwd:4 一鍵 → restore 寫句逐字＝清理面七表 DELETE→session_id 歸
        NULL→六支 setval→指派鍵集差刪除→五表刪上界以上列（sys_user 居末）→授權列回補→指派回補→角色列回寫→使用者列回寫→五支 setval，
        收尾 diff rc 0；seed 指派按原值補回、新帳號列與其指派清除、序列回值、帳號 2 可變欄寫回基準值、經手表與 cpwd 鍵清除；輸出不含
        任何密碼欄值；不動 casbin＝不出重啟句。"""
        stub = _restore_stub()
        path = self._baseline(stub)
        want2 = stub.user_row(2)
        new = self._dirty_user_domain(stub)
        self.assertEqual(new, 4)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertEqual(self._tx(stub), (
            "BEGIN; "
            "UPDATE system_settings SET updated_at = NULL, updated_by = NULL "
            "WHERE updated_at IS NOT NULL OR updated_by IS NOT NULL; "
            "DELETE FROM session_event; DELETE FROM sys_token; DELETE FROM sys_login_attempt; "
            "DELETE FROM sys_ip_rule; DELETE FROM sys_operation_log; DELETE FROM sys_pwd_custody; "
            "DELETE FROM sys_access_log; "
            "UPDATE sys_user SET session_id = NULL WHERE session_id IS NOT NULL; "
            "SELECT setval('sys_token_id_seq', 1, false); "
            "SELECT setval('session_event_id_seq', 1, false); "
            "SELECT setval('sys_login_attempt_id_seq', 1, false); "
            "SELECT setval('sys_ip_rule_id_seq', 1, false); "
            "SELECT setval('sys_operation_log_id_seq', 1, false); "
            "SELECT setval('sys_access_log_id_seq', 1, false); "
            + BOUNDED_SURFACE_AT_SEED + "COMMIT;"))
        self.assertEqual(sorted(stub.user_roles), list(STUB_USER_ROLES))
        self.assertEqual((stub.ids["sys_user"], stub.tables["sys_user"]), ([1, 2, 3], 3))
        self.assertEqual(stub.user_row(2), want2)
        self.assertEqual(stub.seqs["sys_user_id_seq"], (3, "t"))
        self.assertEqual(stub.tables["sys_pwd_custody"], 0)
        self.assertEqual(stub.keys, ["plainkey"])
        self.assertIn("✓ 全等", text)
        self.assertNotIn("樁雜湊", text)
        self.assertNotIn("MUST 重啟 rust-api", text)

    def test_soft_deleted_baseline_account_is_written_back_undeleted_and_its_assignment_backfilled(self):
        """T006①b：基準含自建帳號（id 4＋其指派 (4, 3)）；現況該帳號被軟刪（deleted_at／deleted_by 成對寫、同交易硬刪其指派）→
        軟刪兩欄寫回 NULL（改回值＝改回痕）、指派回補（排在使用者列回寫之前：外鍵只問帳號列存在、不問軟刪）、收尾 diff rc 0。"""
        stub = _restore_stub(ids=dict(STUB_BOUNDED_IDS, sys_user=(1, 2, 3, 4)), user_roles=STUB_USER_ROLES + ((4, 3),),
                             tables=dict(RESTORE_FAKE_TABLES, sys_user=4, sys_user_role=4),
                             seqs=dict(RESTORE_FAKE_SEQS, sys_user_id_seq=(4, "t")))
        path = self._baseline(stub)
        want4 = stub.user_row(4)
        stub.users[4] = dict(want4, deleted_at="2026-10-06T09:00:00+00:00", deleted_by=1)
        stub.user_roles.remove((4, 3))
        stub.tables["sys_user_role"] -= 1
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        tx = self._tx(stub)
        self.assertIn(_t_user_role_insert(STUB_USER_ROLES + ((4, 3),)), tx)
        self.assertIn(_t_user_update(4, want4), tx)
        self.assertLess(tx.index("INSERT INTO sys_user_role "), tx.index("UPDATE sys_user SET nick_name"))
        self.assertEqual(stub.user_row(4), want4)
        self.assertIn((4, 3), stub.user_roles)
        self.assertIn("✓ 全等", text)

    def test_migration_ledger_precondition_refuses_rc2_with_zero_writes_in_both_directions(self):
        """★US6 場景 4（T006②＋反向一案；spec FR-057 (a)）：v4 基準之 migrations 與現庫不等＝rc 2、零 docker 寫入呼叫（只讀過遷移帳
        一句——結構安全帶之後、門鈴清前計數、settings 與重啟句現讀之前）、訊息逐版本指名差集並含重拍與 seed 模式補救——①基準少於現況
        （基準取於 m0003 套用前、現庫已套）＝「現庫有基準無」②基準多於現況（基準含 m0003 而現庫只 m0001／m0002）＝「基準有現庫無」；
        ③現庫遷移帳撈取壞形＝rc 2、零寫入；相等＝放行（其餘各案皆走此形）。"""
        two, three = list(STUB_MIGRATIONS), list(STUB_MIGRATIONS) + ["m0003_seed_button_governance"]
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh:
            real = seed_settings(fh.read())
        settings = [{"setting_key": k, "setting_value": v, "stamped": False} for k, v in sorted(real.items())]
        for base_m, live_m, needle in ((two, three, "現庫有基準無：m0003_seed_button_governance"),
                                       (three, two, "基準有現庫無：m0003_seed_button_governance")):
            stub = _restore_stub(migrations=base_m, settings=settings)   # settings＝真 seed 值：拆前置則一路走到寫句
            path = self._baseline(stub)
            self._dirty(stub)
            self._dirty_user_domain(stub)
            stub.migrations = list(live_m)
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([PROG, "restore", path], run=stub), RC_ENV, msg=needle)
            for want in (needle, "基準檔遷移帳≠現庫", "重新 snapshot", "restore --seed", "零寫入"):
                self.assertIn(want, err.getvalue(), msg=(needle, want))
            self.assertEqual([a[-1] for a in stub.log], [SQL_MIGRATIONS], msg=needle)
        stub = _restore_stub()
        path = self._baseline(stub)
        stub.garble = "migrations"
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        self.assertIn("遷移帳", str(ctx.exception))
        self.assertEqual([a[-1] for a in stub.log], [SQL_MIGRATIONS])

    def test_restore_tx_failure_message_never_echoes_password_values(self):
        """★島 I5 三重不洩延伸至維運工具輸出（password 欄）：交易失敗時 psql 回顯所送 SQL（LINE 形、含使用者列回寫之密碼值）、失敗列
        值（DETAIL Failing row contains 形；PG 對長值截斷附「...」＝目標值片段、整值替換遮不到）與引所送語句之 CONTEXT 行（目標值全文、
        非回顯形）——工具轉述之錯誤訊息剔除回顯行與游標行、遮蔽失敗列值、整值替換目標態密碼值，密碼欄值與其片段皆不出現（三層各有
        樁形可打、拆任一層即紅；CONTEXT 行之遮蔽形須在轉述截斷窗內出現＝整值替換層之斷言非因截斷而空過）；ERROR 行照轉、交易回滾後
        不進 redis。"""
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty_user_domain(stub)
        stub.fail = "tx_echo"
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
            cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        msg = str(ctx.exception)
        self.assertNotIn("樁雜湊", msg)
        self.assertNotIn("LINE 1:", msg)
        self.assertIn("restore 交易失敗", msg)
        self.assertIn('column "x" does not exist', msg)
        self.assertIn("Failing row contains", msg)
        self.assertIn(f"SQL statement \"UPDATE sys_user SET password = '{MASK}' WHERE id = 2\"", msg)
        self.assertFalse(any(" DEL " in a[-1] for a in stub.log))

    def test_seed_target_parses_user_domain_and_damage_messages_never_print_row_text(self):
        """seed 模式之使用者域目標（T006；凍結段）：樁與真檔之 sys_user COPY 段解析為上界 3、序列 (3, true)、三列可變欄（真檔暱稱
        Super／Admin／User01、狀態 1、會話政策 inherit、軟刪兩欄 NULL、密碼欄為非空字串——本案不印亦不釘其值）、經手表段零列；sys_user
        段受損（列欄數不符、id 非整數、狀態非整數、非空欄為 \\N）＝凍結面受損 rc 2，且訊息不含該段列文（密碼雜湊與其片段不出工具輸出）。"""
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh:
            real_text = fh.read()
        stub_target = seed_restore_target(SEED_RESTORE_TEXT)
        self.assertEqual(stub_target["sys_user_rows"], [dict({"id": i}, **STUB_USER_ROWS[i]) for i in (1, 2, 3)])
        real = seed_restore_target(real_text)
        self.assertEqual((real["id_bounds"]["sys_user"], real["sequences"]["sys_user_id_seq"], real["tables"]["sys_pwd_custody"]),
                         (3, {"last_value": 3, "is_called": True}, 0))
        self.assertEqual([(r["id"], r["nick_name"], r["status"], r["session_policy"], r["deleted_at"], r["deleted_by"])
                          for r in real["sys_user_rows"]],
                         [(1, "Super", 1, "inherit", None, None), (2, "Admin", 1, "inherit", None, None),
                          (3, "User01", 1, "inherit", None, None)])
        hashes = {r["password"] for r in real["sys_user_rows"]}
        self.assertTrue(hashes and all(isinstance(h, str) and h for h in hashes))
        row2 = next(ln for ln in SEED_RESTORE_TEXT.splitlines() if ln.startswith("2\t") and "\tAdmin\t" in ln)
        for bad in (SEED_RESTORE_TEXT.replace(row2, row2 + "\textra"),
                    SEED_RESTORE_TEXT.replace(row2, "x" + row2[1:]),
                    SEED_RESTORE_TEXT.replace(row2, row2.replace("\t1\t\\N\tAdmin\t", "\tone\t\\N\tAdmin\t")),
                    SEED_RESTORE_TEXT.replace(row2, row2.replace(f"\t{_stub_pw(2)}\t", "\t\\N\t"))):
            self.assertNotEqual(bad, SEED_RESTORE_TEXT)
            with self.assertRaises(BaselineError) as ctx:
                seed_restore_target(bad)
            for needle in ("sys_user", "凍結面受損"):
                self.assertIn(needle, str(ctx.exception))
            self.assertNotIn("樁雜湊", str(ctx.exception))
            self.assertNotIn("Admin", str(ctx.exception))
        real_row = next(ln for ln in real_text.splitlines() if ln.startswith("1\t") and "\tSuper\t" in ln)
        with self.assertRaises(BaselineError) as ctx:
            seed_restore_target(real_text.replace(real_row, real_row + "\textra"))
        self.assertFalse([h for h in hashes if h in str(ctx.exception) or h[8:24] in str(ctx.exception)])

    # ── 演進登記合成、repo↔現庫遷移同步前置與 seed 模式合成目標（007 刀 U1、T007）────────────────────────

    @staticmethod
    def _real_seed():
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh:
            return fh.read()

    @staticmethod
    def _settings_rows_of(seed_text):
        return [{"setting_key": k, "setting_value": v, "stamped": False} for k, v in sorted(seed_settings(seed_text).items())]

    def _m0003_applied_stub(self, frozen_text, migrations):
        """現況＝已套 m0003：授權列以 data-model §9.1 手寫施於凍結 seed 之解析結果（與受測之合成鏈互為獨立來源）——列 44 不在、列 58～63
        受保護、列 164 在、casbin_rule_id_seq＝(164, true)；system_settings＝真凍結值（m0003 不動）；其餘面同樁預設。"""
        casbin = {r["id"]: dict(r) for r in seed_restore_target(frozen_text)["casbin_rule_rows"]}
        del casbin[44]
        for i in range(58, 64):
            casbin[i]["protected"] = True
        casbin[164] = {"id": 164, "ptype": "p", "v0": "R_SUPER", "v1": "ipRule:unlock", "v2": "button", "v3": "", "v4": "",
                       "v5": "", "protected": False, "created_at": STUB_TS_JSON, "created_by": None}
        stub = _restore_stub(settings=self._settings_rows_of(frozen_text), migrations=migrations,
                             ids=dict(STUB_BOUNDED_IDS, casbin_rule=tuple(sorted(casbin))),
                             seqs=dict(RESTORE_FAKE_SEQS, casbin_rule_id_seq=(164, "t")))
        stub.casbin = casbin
        return stub

    def test_seed_mode_targets_frozen_seed_synthesized_with_m0003_shaped_entries(self):
        """★US6 場景 5（T007③）：演進帳＝m0003 九筆形、現庫已套用（遷移帳＝repo 三支）並留走查殘列（清理面、角色／選單／歸檔／指派、授權列
        165～166〔nextval 自 164〕、使用者域）→ seed 模式目標態＝真凍結 seed ⊕ 九筆合成：列 44 不在（不回補）、列 164 在（上界 164＝不刪）、
        列 58～63 受保護、casbin_rule_id_seq＝(164, true)、殘列清除、收尾 rc 0。R22 種子「163 列」判讀：凍結目標 163 列／上界 163，合成目標
        163 列（刪 44、增 164）／上界 164。左源若退回凍結段＝列 44 被回補、列 164 被刪、58～63 收尾報不等（rc≠0）。"""
        real = self._real_seed()
        self._write_ledger(*M0003_ENTRIES)
        with tempfile.TemporaryDirectory() as d:
            lib = _write_migration_src(d, M0003_MODULES, "multi")
            stub = self._m0003_applied_stub(real, M0003_MODULES)
            self._dirty(stub)
            self._dirty_role_menu(stub)
            self._dirty_user_domain(stub)
            self.assertEqual(sorted(stub.ids["casbin_rule"])[-3:], [164, 165, 166])   # 前置自證：殘列在上界 164 之上
            rc, text = self._restore_seed(stub, real, lib)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertEqual(sorted(stub.ids["casbin_rule"]), sorted(set(range(1, 165)) - {44}))
        self.assertTrue(all(stub.casbin_row(i)["protected"] for i in range(58, 64)))
        self.assertEqual(stub.seqs["casbin_rule_id_seq"], (164, "t"))
        self.assertEqual((sorted(stub.user_roles), stub.ids["sys_user"], stub.tables["sys_pwd_custody"], stub.keys),
                         (list(STUB_USER_ROLES), [1, 2, 3], 0, ["plainkey"]))
        tx = self._tx(stub)
        self.assertIn("DELETE FROM casbin_rule WHERE id > 164;", tx)
        self.assertIn("SELECT setval('casbin_rule_id_seq', 164, true);", tx)
        self.assertIn("(164, 'p', 'R_SUPER', 'ipRule:unlock', 'button', '', '', '', false, '2026-08-05T00:00:00+00:00', NULL)",
                      tx)
        self.assertIn("(58, 'p', 'R_SUPER', 'role:add', 'button', '', '', '', true, ", tx)
        self.assertNotIn("'R_ADMIN', 'user:edit'", tx)
        self.assertIn("✓ 全等", text)
        self.assertIn(CASBIN_RESTART_HINT, text)
        frozen = seed_restore_target(real)
        synth = seed_restore_target(synthesize_seed(real, M0003_ENTRIES, SYNTH_TABLES_SEED))
        self.assertEqual((frozen["tables"]["casbin_rule"], frozen["id_bounds"]["casbin_rule"]), (163, 163))
        self.assertEqual((synth["tables"]["casbin_rule"], synth["id_bounds"]["casbin_rule"],
                          synth["sequences"]["casbin_rule_id_seq"]), (163, 164, {"last_value": 164, "is_called": True}))

    def test_seed_mode_without_the_shared_sequence_advance_is_refused_by_the_bound_precondition(self):
        """T007③ 之序號腿：以 monkeypatch 拆共用合成鏈（tools/schema-gate.py 之 _advance_seed_sequence）之序號推進 → 合成目標之 casbin_rule
        上界 164 高於其序列 (163, true) → 上界對序列之前置拒跑 rc 2、零 docker 呼叫（照跑則序列 setval 回 163、下一次 nextval 撞列 164
        PK）；寫回後同一登記之合成目標序列＝(164, true)。"""
        real = self._real_seed()
        self._write_ledger(*M0003_ENTRIES)
        gate = _schema_gate()
        saved = gate._advance_seed_sequence
        gate._advance_seed_sequence = lambda *_a: None
        try:
            with tempfile.TemporaryDirectory() as d:
                lib = _write_migration_src(d, M0003_MODULES, "multi")
                stub = self._m0003_applied_stub(real, M0003_MODULES)
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                    self._restore_seed(stub, real, lib)
        finally:
            gate._advance_seed_sequence = saved
        for needle in ("casbin_rule 上界 164＞casbin_rule_id_seq（last_value=163,is_called=t）", "撞", "零寫入"):
            self.assertIn(needle, str(ctx.exception))
        self.assertEqual(stub.log, [])
        self.assertEqual(seed_restore_target(synthesize_seed(real, M0003_ENTRIES, SYNTH_TABLES_SEED))["sequences"]
                         ["casbin_rule_id_seq"], {"last_value": 164, "is_called": True})

    def test_repo_vs_live_migration_sync_precondition_refuses_rc2_with_zero_writes(self):
        """★US6 場景 6（T007④＋反向一案；spec FR-057 (b)）：seed 模式、合成面有 seed_* 登記（m0003 九筆形）→ 寫入前比對 repo migration 清單
        與現庫遷移帳：①repo 三支而現庫兩支＝「repo 有現庫無＝未套用」②現庫三支而 repo 兩支＝「現庫有 repo 無」——皆 rc 2、只讀過遷移帳一句
        （零寫入）、訊息指名差異版本與觸發之登記 id 並附補救；③repo 清單不可解＝rc 2、零 docker 呼叫（repo 面先於現讀）。樁 settings＝真
        凍結值、現況未套用：拆前置則一路走到寫句（本案以讀句清單釘死）。"""
        real = self._real_seed()
        self._write_ledger(*M0003_ENTRIES)
        two = list(STUB_MIGRATIONS)
        with tempfile.TemporaryDirectory() as d:
            lib2 = _write_migration_src(os.path.join(d, "r2"), two)
            lib3 = _write_migration_src(os.path.join(d, "r3"), list(M0003_MODULES), "multi")
            for lib, live, needle in ((lib3, two, "repo 有現庫無＝未套用：m0003_seed_button_governance"),
                                      (lib2, list(M0003_MODULES), "現庫有 repo 無：m0003_seed_button_governance")):
                stub = _restore_stub(settings=self._settings_rows_of(real), migrations=live)
                self._dirty(stub)
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                    self._restore_seed(stub, real, lib)
                msg = str(ctx.exception)
                for want in (needle, "repo migration 清單≠現庫遷移帳", "E-001", "E-009", "零寫入", "補救"):
                    self.assertIn(want, msg, msg=(needle, want))
                self.assertEqual([a[-1] for a in stub.log], [SQL_MIGRATIONS], msg=needle)
            stub = _restore_stub(settings=self._settings_rows_of(real), migrations=two)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                self._restore_seed(stub, real, os.path.join(d, "nope", "lib.rs"))
            self.assertIn("repo migration 清單讀取失敗", str(ctx.exception))
            self.assertEqual(stub.log, [])

    def test_baseline_mode_repo_ahead_of_live_with_a_settings_entry_refuses_naming_the_unapplied_migration(self):
        """T007④b：基準檔模式、合成登記僅 system_settings 一筆 seed_update、基準檔 migrations＝現庫兩支（(a) 放行）、repo 清單三支 →
        rc 2、訊息指名未套用之遷移（而非 system_settings 值差——現值仍為凍結值、拆前置則改報值≠期望）、只讀過遷移帳一句（(a) 與同步前置共用、
        零寫入）。"""
        self._write_ledger(_ledger_entry("E-001", "seed_update", "system_settings",
                                         {"pk": {"setting_key": "session_idle_timeout"}, "set": {"setting_value": "30"}}))
        with tempfile.TemporaryDirectory() as d:
            lib3 = _write_migration_src(d, list(M0003_MODULES), "multi")
            stub = _restore_stub(migrations=list(STUB_MIGRATIONS))
            path = self._baseline(stub)
            self._dirty(stub)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                self._restore(path, stub, lib3)
        msg = str(ctx.exception)
        for want in ("repo 有現庫無＝未套用：m0003_seed_button_governance", "E-001", "system_settings", "零寫入"):
            self.assertIn(want, msg)
        for unwanted in ("002 刀", "現值"):
            self.assertNotIn(unwanted, msg)
        self.assertEqual([a[-1] for a in stub.log], [SQL_MIGRATIONS])

    def test_baseline_mode_ignores_domain_entries_outside_its_synthesis_face_even_when_repo_is_ahead(self):
        """基準檔模式之合成射程＝system_settings：帳上只有角色／選單域登記（m0003 九筆形）＋repo 領先現庫（三支對兩支）＝同步前置不驗
        （T023 ② 以 m0003 前之 v4 基準還原 dev 庫之前提）→ 照常還原、收尾 rc 0、遷移帳只 (a) 一讀。"""
        self._write_ledger(*M0003_ENTRIES)
        with tempfile.TemporaryDirectory() as d:
            lib3 = _write_migration_src(d, list(M0003_MODULES), "multi")
            stub = _restore_stub(migrations=list(STUB_MIGRATIONS))
            path = self._baseline(stub)
            self._dirty(stub)
            self._dirty_user_domain(stub)
            rc, text = self._restore(path, stub, lib3)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertEqual([a[-1] for a in stub.log].count(SQL_MIGRATIONS), 1)
        self.assertIn("✓ 全等", text)

    def test_unsupported_add_column_on_the_synthesis_face_refuses_rc2_with_the_gate_error_in_both_modes(self):
        """仍拒跑之演進形②（T007）：合成面表登記 add_column 帶 default 一筆、NOT NULL 無 default 一筆（seed 模式取 sys_role、基準檔模式取
        system_settings）→ 兩模式各 rc 2、訊息含 schema 閘 GateError 原文、零 docker 呼叫；同一登記餵 tools/schema-gate.py 之
        apply_seed_entries 亦拋 GateError（兩工具同時拒跑、於其同一擴充點補齊即同時恢復）。"""
        gate = _schema_gate()
        for detail in ({"column": "x", "type": "text", "nullable": True, "default": "'v'::text", "position": "末位"},
                       {"column": "y", "type": "text", "nullable": False, "default": None, "position": "末位"}):
            for seed_mode, table, seed_text in ((True, "sys_role", SEED_RESTORE_TEXT), (False, "system_settings", SEED_SETTINGS_TEXT)):
                entry = _ledger_entry("E-001", "add_column", table, detail)
                with self.assertRaises(gate.GateError) as g:
                    gate.apply_seed_entries(gate.normalize_seed_dump(seed_text), [entry])
                self._write_ledger(entry)
                stub = _restore_stub()
                path = None if seed_mode else self._baseline(stub)
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                    if seed_mode:
                        self._restore_seed(stub)
                    else:
                        cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
                self.assertIn(str(g.exception), str(ctx.exception), msg=(table, detail))
                self.assertIn("GateError", str(ctx.exception), msg=(table, detail))
                self.assertEqual(stub.log, [], msg=(table, detail))

    def test_seed_mode_closing_check_covers_the_user_domain(self):
        """seed 模式⑤收尾判準面擴及使用者域（T007）：seed 帳號列 3 被硬刪（射程外＝回寫只改在場之列；樁 seed 去掉 (3, 3) 指派、免回補撞
        外鍵）→ rc 1、逐面指名 sys_user 列數、上界與使用者列缺列。判準面若改取現況值＝三殘差皆看不見、收尾假綠。"""
        no33 = SEED_RESTORE_TEXT.replace("\n1\t1\n2\t2\n3\t3\n", "\n1\t1\n2\t2\n")
        self.assertNotEqual(no33, SEED_RESTORE_TEXT)
        stub = _restore_stub()
        stub.user_roles.remove((3, 3))
        stub.tables["sys_user_role"] -= 1
        stub.ids["sys_user"].remove(3)
        stub.tables["sys_user"] -= 1
        rc, out = self._restore_seed(stub, no33)
        self.assertEqual(rc, RC_DIFF, msg=out)
        for needle in ("表｜sys_user｜3｜2｜-1", "上界｜sys_user｜3｜2｜-1", "使用者列｜sys_user(id=3)｜有｜（無）｜-1"):
            self.assertIn(needle, out)


class TestEvolutionSynthesis(unittest.TestCase):
    """演進登記合成之單一來源（007 刀 U1、T007；ADR-00085 決定 9 (b)）：執行期依路徑載入 tools/schema-gate.py、取 gate2 之同一合成鏈
    （normalize_seed_dump → apply_seed_entries，序號推進含於其內）；只餵合成射程之表；載入失敗＝rc 2 原訊息照轉；與 docsync 帳號快照投影
    交叉對賬；真凍結 seed ⊕ 真演進帳可解。"""

    @staticmethod
    def _real_seed():
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh:
            return fh.read()

    def test_schema_gate_chain_load_failure_is_env_error_carrying_the_original_message(self):
        """合成鏈載入失敗（檔缺席、模組執行期拋錯、缺合成件）＝BaselineError（rc 2）、原訊息照轉；真檔載入得三件。"""
        with tempfile.TemporaryDirectory() as d:
            boom, bare = os.path.join(d, "boom.py"), os.path.join(d, "bare.py")
            with open(boom, "w", encoding="utf-8") as fh:
                fh.write("raise RuntimeError('樁載入炸點')\n")
            with open(bare, "w", encoding="utf-8") as fh:
                fh.write("X = 1\n")
            for path, needle in ((os.path.join(d, "nope.py"), "nope.py"), (boom, "樁載入炸點"), (bare, "apply_seed_entries")):
                with self.assertRaises(BaselineError, msg=needle) as ctx:
                    load_schema_gate(path)
                self.assertIn(needle, str(ctx.exception))
                self.assertIn("合成鏈載入失敗", str(ctx.exception))
        gate = load_schema_gate(os.path.join(REPO_ROOT, SCHEMA_GATE))
        self.assertTrue(callable(gate.apply_seed_entries) and callable(gate.normalize_seed_dump))
        self.assertTrue(issubclass(gate.GateError, Exception))

    def test_synthesis_rosters_and_single_source_are_pinned(self):
        """合成射程名冊逐字釘（基準檔模式＝system_settings；seed 模式＝其＋角色／選單／使用者域六表）；合成鏈料源＝tools/schema-gate.py；
        本檔不自持第二份 COPY 合成或序號推進（其函式名不在本模組）。"""
        self.assertEqual(SYNTH_TABLES_BASELINE, ("system_settings",))
        self.assertEqual(SYNTH_TABLES_SEED, ("system_settings", "sys_role", "sys_menu", "casbin_rule", "sys_casbin_policy_archive",
                                             "sys_user", "sys_user_role"))
        self.assertEqual(SCHEMA_GATE, os.path.join("tools", "schema-gate.py"))
        for name in ("apply_seed_entries", "normalize_seed_dump", "_advance_seed_sequence", "copy_literal"):
            self.assertNotIn(name, globals())

    def test_feeding_only_face_tables_equals_unfiltered_synthesis_on_the_face(self):
        """各筆只作用於自表 COPY 段與自表序列＝逐表獨立：m0003 九筆＋合成面外一筆（sys_user_email_verify 增列）——本工具（只餵合成面）與
        gate2 鏈不濾全餵，於合成面（上界、鍵集、列面、該域序列、system_settings）全等；面外之段確實未餵（兩文字不等）。"""
        real = self._real_seed()
        extra = _ledger_entry("E-010", "seed_add", "sys_user_email_verify", {"pk": ["user_id"], "values": {
            "user_id": 3, "created_at": "2026-08-05 00:00:00+00", "created_by": 1, "verified_at": "2026-08-05 00:00:00+00",
            "verified_email": "u3@example.test"}})
        entries = list(M0003_ENTRIES) + [extra]
        gate = _schema_gate()
        whole = gate.apply_seed_entries(gate.normalize_seed_dump(real), entries)
        ours = synthesize_seed(real, entries, SYNTH_TABLES_SEED)
        self.assertNotEqual(whole, ours)
        a, b = seed_restore_target(whole), seed_restore_target(ours)
        keys = ("id_bounds", "user_role_keys") + tuple(ROW_FACES)
        self.assertEqual({k: a[k] for k in keys}, {k: b[k] for k in keys})
        self.assertEqual({s: a["sequences"][s] for s in BOUNDED_TABLES.values()},
                         {s: b["sequences"][s] for s in BOUNDED_TABLES.values()})
        self.assertEqual(seed_settings(whole), seed_settings(ours))

    def test_synthesis_cross_checks_with_docsync_account_projection(self):
        """★合成語意對賬（T007⑦；spec FR-057#14）：sys_user／sys_role／sys_user_role 三表各以 seed_add、seed_update、seed_delete 三 kind
        各一（增列另多一列供刪）之合成登記，餵本工具之合成鏈與獨立重寫之 docsync.snapshot.seed_account_projection——本工具合成面投影至
        USER_KEYS／ROLE_KEYS／BINDING_KEYS 逐節全等（COPY 文字形）；合成確有作用（帳號 4、角色 4、指派變更皆在）；序號只進不退（帳號 5 增後
        刪、sys_user_id_seq 仍推至 5）且上界不高於序列。密碼欄取非 PHC 形之樁佔位（RL-0054）。"""
        real = self._real_seed()

        def user(i, name):
            return {"id": i, "created_at": STUB_TS_COPY, "created_by": None, "updated_at": None, "updated_by": None,
                    "deleted_at": None, "deleted_by": None, "status": 1, "user_gender": None, "user_name": name,
                    "password": _stub_pw(i), "nick_name": name, "session_policy": "inherit", "session_id": None,
                    "user_phone": None, "user_email": None, "user_memo": None}

        def role(i, code):
            return {"id": i, "created_at": STUB_TS_COPY, "created_by": None, "updated_at": None, "updated_by": None,
                    "deleted_at": None, "deleted_by": None, "status": 1, "role_code": code, "role_name": f"演進角色{i}",
                    "role_memo": None, "role_home": "home", "role_desc": None}

        entries = [
            _ledger_entry("E-001", "seed_add", "sys_user", {"pk": ["id"], "values": user(4, "Auditor")}),
            _ledger_entry("E-002", "seed_add", "sys_user", {"pk": ["id"], "values": user(5, "Temp")}),
            _ledger_entry("E-003", "seed_update", "sys_user", {"pk": {"id": 3}, "set": {"nick_name": "User03", "status": 2}}),
            _ledger_entry("E-004", "seed_delete", "sys_user", {"pk": {"id": 5}}),
            _ledger_entry("E-005", "seed_add", "sys_role", {"pk": ["id"], "values": role(4, "R_AUDIT")}),
            _ledger_entry("E-006", "seed_add", "sys_role", {"pk": ["id"], "values": role(5, "R_TEMP")}),
            _ledger_entry("E-007", "seed_update", "sys_role", {"pk": {"id": 2}, "set": {"role_name": "管理員（演進）"}}),
            _ledger_entry("E-008", "seed_delete", "sys_role", {"pk": {"id": 5}}),
            _ledger_entry("E-009", "seed_add", "sys_user_role", {"pk": ["user_id", "role_id"],
                                                                 "values": {"user_id": 4, "role_id": 4}}),
            _ledger_entry("E-010", "seed_update", "sys_user_role", {"pk": {"user_id": 3, "role_id": 3}, "set": {"role_id": 4}}),
            _ledger_entry("E-011", "seed_delete", "sys_user_role", {"pk": {"user_id": 2, "role_id": 2}})]
        text = synthesize_seed(real, entries, SYNTH_TABLES_SEED)
        target = seed_restore_target(text)
        lines = text.splitlines()
        names = {r["id"]: r["user_name"] for r in _seed_copy_records(_seed_copy_rows(lines, "sys_user"), "sys_user",
                                                                       {"id": "int", "user_name": "text"})}
        codes = {r["id"]: r["role_code"] for r in _seed_copy_records(_seed_copy_rows(lines, "sys_role"), "sys_role",
                                                                       {"id": "int", "role_code": "text"})}

        def c(v):
            return "\\N" if v is None else str(v)

        tools_dir = os.path.join(REPO_ROOT, "tools")
        added = tools_dir not in sys.path
        if added:
            sys.path.insert(0, tools_dir)
        try:
            from docsync import snapshot as ds
        finally:
            if added:
                sys.path.remove(tools_dir)
        ours = {"users": [{k: c(dict(r, user_name=names[r["id"]])[k]) for k in ds.USER_KEYS} for r in target["sys_user_rows"]],
                "roles": [{k: c(dict(r, role_code=codes[r["id"]])[k]) for k in ds.ROLE_KEYS} for r in target["sys_role_rows"]],
                "bindings": [dict(zip(ds.BINDING_KEYS, map(c, k))) for k in target["user_role_keys"]]}
        theirs = ds.seed_account_projection(real, entries)
        for section, ident in (("users", ("id",)), ("roles", ("id",)), ("bindings", ds.BINDING_KEYS)):
            def order(r, ident=ident):
                return tuple(int(r[k]) for k in ident)
            self.assertEqual(sorted(theirs[section], key=order), sorted(ours[section], key=order), msg=section)
        self.assertEqual([(r["id"], r["user_name"]) for r in ours["users"] if r["id"] in ("3", "4")],
                         [("3", "User"), ("4", "Auditor")])
        self.assertEqual(sorted(target["user_role_keys"]), [[1, 1], [3, 4], [4, 4]])
        self.assertEqual((target["id_bounds"]["sys_user"], target["sequences"]["sys_user_id_seq"]),
                         (4, {"last_value": 5, "is_called": True}))
        self.assertEqual(bounds_above_sequence(target), [])

    def test_real_frozen_seed_with_the_real_ledger_synthesizes_with_bounds_not_above_sequences(self):
        """真 repo：凍結 seed ⊕ 真演進帳（docs/ops/reference-src/schema-evolution.json）於兩模式之合成射程皆可解；seed 模式合成目標之
        五表上界皆不高於其序列位置、seed 模式前置全過（不釘實值——帳上登記演進即隨之）。"""
        real = self._real_seed()
        with open(os.path.join(REPO_ROOT, SCHEMA_EVOLUTION), encoding="utf-8") as fh:
            entries = json.load(fh)["entries"]
        for tables in (SYNTH_TABLES_BASELINE, SYNTH_TABLES_SEED):
            self.assertTrue(seed_settings(synthesize_seed(real, entries, tables)), msg=tables)
        target = seed_restore_target(synthesize_seed(real, entries, SYNTH_TABLES_SEED))
        self.assertEqual(set(target["id_bounds"]), set(BOUNDED_TABLES))
        self.assertEqual(bounds_above_sequence(target), [])
        check_restore_baseline(target, seed_mode=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
