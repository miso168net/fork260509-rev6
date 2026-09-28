#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/walkthrough-baseline.py — CDP 真登入走查前後的全表基準對賬（rev5:B-147；rev5:L-071 防法①的機制化）

子命令：
  snapshot <檔>   取 rev6 dev stack 實庫＋redis 現況三面＋角色／選單域兩欄、寫成 JSON 基準檔（走查**前**跑；四表上界高於
                  其序列位置＝stderr 告警〔以之 restore 將拒跑〕、rc 仍 0——見 restore 安全帶）
  diff <檔>       重取現況、與基準檔逐值比對（含兩欄：上界差、鍵集差逐對）、只列有差者＋末行摘要（走查**後**清理完跑；
                  ★rc 0 才算「環境已還原」——三閘綠不算，rev5:L-055／rev5:L-071 招牌徵狀＝三閘綠而全量紅）
                  ★序列面例外一項：runtime-append 四表（RUNTIME_APPEND_TABLES、與 tools/schema-gate.py 同名常數同值）
                    之 id 序列只比**存在性**、不比值——同 gate2 對其 setval 值正規化之口徑；這四支只進不退
                    （rust-api 測試守衛只清自寫列、序列不復位），逐值比則每跑一次全量測試 diff 即恆有差
  restore <檔>    走查後清理（RUNBOOK §9c 第 3 步之順序機器化；寫面恰為下列、次序固定）：
                  ①system_settings 對凍結 seed（specs/001-schema-baseline/fixtures/seed.sql 之 COPY 段）——值≠seed
                    （含鍵缺／鍵多）即 fail-loud 指名、**不自動改值**（值還原走 002 刀寫端＝人工前置）；值＝seed 而
                    審計欄 updated_at／updated_by 非 NULL 者歸 NULL（改回值≠改回痕）；★左源未合成演進帳——
                    docs/ops/reference-src/schema-evolution.json 有 system_settings 之 seed_* 登記即拒跑、指名登記 id
                    （凍結段已非期望 seed；先擴充本工具）
                  ②DELETE 清理面五表（RESTORE_TABLES＝會話三表＋sys_ip_rule＋sys_operation_log）全表
                    ＋sys_user.session_id 歸 NULL
                  ③五支 setval（RESTORE_SEQUENCES＝上列五表之 id 序列）值自基準檔現讀
                  ③b角色／選單域寫面（接在③之後）：sys_user_role 以目標鍵集差刪除（現況有而目標無之對；其 role_id
                    外鍵 ON DELETE RESTRICT 指 sys_role、故先於四表）→ BOUNDED_TABLES 四表（sys_role／sys_menu／
                    casbin_rule／sys_casbin_policy_archive；四表間無外鍵、次序取名冊序）刪 id > 目標上界之列 → 四支序列
                    setval 回目標值；目標＝基準檔 id_bounds／user_role_keys 與序列面現讀值。★seed 有列＝不 DELETE 全表、
                    不套列數安全帶（改守上界對序列之前置、見安全帶）；★射程界＝只刪上界以上列與鍵集差、不補不改——id ≤ 上界之列
                    （含 seed 列）之就地改寫或被刪、指派對被刪，restore 皆不還原：列數與鍵集差由收尾比對報出、欄值改寫由
                    tools/schema-gate.py check 之 gate2 逐列兜；上界本身被取樣時之顯式 id 殘列抬高者＝該前置拒跑、不在射程內硬做
                    ——①～③b 同一交易（BEGIN…COMMIT、ON_ERROR_STOP=1；任一句敗即整筆回滾、不進④）
                  ④b門鈴（BL-00094；交易提交後、④之前）：清前 sys_ip_rule 列數非 0＝PUBLISH ipgate:invalidate 一次並
                    回報訂閱者數；回非整數＝拋錯並附可照抄之人工按鈴命令（doorbell_cli）；清前 0 列＝不按
                  ④redis 以 `--scan --pattern` 取 session:*／throttle:* 鍵、逐鍵指名 DEL（每批 ≤REDIS_DEL_BATCH
                    把；絕不 FLUSHDB、絕不以樣式刪）
                  ⑤收尾自動跑一次 diff、其 rc 即 restore 之 rc（0＝已還原）
                  ⑥重啟句：③b 實際刪過 casbin_rule 列或改過其序列（交易前以 SQL_CASBIN_STATE 現讀判）＝收尾輸出
                    CASBIN_RESTART_HINT（MUST 重啟 rust-api、附可照抄之 compose restart 命令；判定面無外部通知管道）
                    ——提交後任一步失敗之路徑亦輸出；未動 casbin 者不輸出
                  ★安全帶：基準檔清理面五表列數或 session／throttle 前綴鍵數非 0＝拒絕執行 rc 2、零寫入（DELETE 全表
                    會毀掉基準資料——restore 只服務「走查前為空基準」之形；無空基準檔可用＝改跑 seed 模式）；角色／選單域
                    五表不套（其寫面不毀目標態之列）、改守前置：基準檔四表任一之上界高於其序列位置（nextval 已發出之最大值：
                    is_called 真＝last_value、假＝last_value-1）＝拒跑 rc 2、零寫入——取樣時已有顯式 id 殘列越過序列、走查以
                    nextval 造之列落在序列與上界之間＝刪不到、序列卻被 setval 回其下＝下一次 nextval 撞 PK（補救＝seed 模式；
                    snapshot 遇同條件即告警）；安全帶、seed 比對與重啟句判準之現讀皆在任何寫入之前
  restore --seed  同上清理、但無須基準檔：目標態＝凍結 seed（BL-00075；走查外殘列——被殺測試留下之列與鍵——
                  產生時通常無空基準 snapshot 可用）。與基準檔模式之差恰三處：
                  (a)安全帶改對凍結 seed：清理面五表之 COPY 段須在場且零列、五支序列之 setval 行須在場；角色／選單域
                    五表之 COPY 段與四支序列之 setval 行須在場（不論列數；段首缺欄、列欄數不符、id 非整數＝凍結面受損）；
                    演進帳拒跑判定由 system_settings 擴及清理面五表與角色／選單域五表（有其 seed_* 登記＝凍結段非期望
                    seed、照清會毀 seed 列）；上界對序列之前置照套、對象改為凍結 seed（COPY 列 id 最大值高於其 setval 位置＝
                    凍結面受損 rc 2；真檔恰相等、自測釘住＝不觸發）
                  (b)③只 setval sys_ip_rule_id_seq 一支（SEED_SETVAL_SEQUENCES＝清理面序列扣掉 runtime-append 者）、
                    值自凍結 seed 之 setval 行現讀；runtime-append 四支序列**不復位**；③b 目標＝凍結 seed：四表上界＝COPY
                    列 id 最大值（零列記 0）、四支 setval 值＝其 setval 行、指派鍵集＝COPY 鍵集
                  (c)⑤收尾比對之判準面＝清理面與角色／選單域對 seed 目標值（清理面五表 0 列、sys_ip_rule_id_seq＝seed 值、
                    runtime-append 序列在場、兩前綴 0 鍵；角色／選單域五表列數、四表上界與序列、指派鍵集）；其餘面無基準
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
    前綴名冊亦不手抄——rust-api 現行 session:／throttle: 兩前綴只是今天的值）
  基準檔另帶 taken_at（UTC ISO）與 schema_version（檔形演進用）；diff 忽略 taken_at。
  另帶角色／選單域兩欄（檔形 v2；restore ③b 之目標值、非比對面之名冊式防法——全表列數仍由①現算）：id_bounds＝
    BOUNDED_TABLES 四表之 max(id)（空表記 0）、user_role_keys＝sys_user_role 之 [user_id, role_id] 有序清單；
    diff 亦比兩欄。v1 基準檔（無兩欄）diff／restore 皆 rc 2 指名重新 snapshot。

退出碼：0 全等／1 有差／2 環境或結構異常（docker 不可執行、psql／redis 失敗、基準檔缺席或壞形、
★比對面為空＝零表或零序列——空面的全綠是假綠、同 schema-gate 紀律，snapshot 與 diff 皆然；restore 另含
安全帶拒跑（含目標態四表上界高於其序列位置）、基準檔缺清理面之表或序列、seed 左源缺席或不可解、演進登記檔缺席或壞形、system_settings 有 seed_*
演進登記、system_settings 值≠seed、casbin_rule 現態撈取壞形；seed 模式另含凍結 seed 缺清理面或角色／選單域之 COPY
段或 setval 行、該面 COPY 段受損、清理面五表或角色／選單域五表有 seed_* 演進登記；基準檔壞形含 v1 舊檔形）／
64 用法錯（usage 走 stderr）。restore 之 0／1 即其收尾 diff 之 rc。

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
runtime-append 序列存在性口徑＝BL-00075（004 刀 U3；rev5 同名工具無此三項）。角色／選單域寫面（③b）、檔形 v2
兩欄與重啟句（⑥）＝005 刀 U15（T088；rev5 同名工具無此面、無藍本）。
"""
import contextlib
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
SCHEMA_VERSION = 2       # 基準檔形版本；改檔形即 bump、舊檔 diff／restore 走 rc 2 而非誤比（v2＝005 刀 U15 加兩欄）
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
# 演進登記檔（形斷言權威＝tools/schema-gate.py）：期望 seed＝凍結 ⊕ 演進；本工具左源只讀凍結段、未合成演進，
# 故帳上有 system_settings（seed 模式另含清理面五表與角色／選單域五表）之 seed 面登記即拒跑（check_seed_evolution）
SCHEMA_EVOLUTION = os.path.join("docs", "ops", "reference-src", "schema-evolution.json")
SEED_EVOLUTION_KINDS = ("seed_add", "seed_update", "seed_delete")
# runtime-append 四表→其 id 序列：與 tools/schema-gate.py 之 RUNTIME_APPEND_TABLES **同值**（連字檔名 CLI 不可 import、
# 故自帶；自測以 importlib 依路徑載入該檔、對賬兩者逐項相等）。這四支序列只進不退——rust-api 測試守衛只清自寫列、
# 不復位（004 刀 U3 廢序列復位守衛；LL-00017／LL-00022）——故 diff 對其只比存在性、seed 模式亦不 setval。
RUNTIME_APPEND_TABLES = {
    "session_event": "session_event_id_seq",
    "sys_login_attempt": "sys_login_attempt_id_seq",
    "sys_operation_log": "sys_operation_log_id_seq",
    "sys_token": "sys_token_id_seq",
}
# 清理面五表（DELETE 全表；次序即語句序）：會話三表＋sys_ip_rule（業務表、zero-seed）＋sys_operation_log
RESTORE_TABLES = ("session_event", "sys_token", "sys_login_attempt", "sys_ip_rule", "sys_operation_log")
# 門鈴（BL-00094）：restore 以 SQL 直清 sys_ip_rule、不經規則寫端⇒執行中的 rust-api 判定面仍持舊規則集。
# 清前列數非 0 時自動補按；★payload 不帶語意、收訊端只認頻道（rust-api `ipgate::IPGATE_INVALIDATE_CHANNEL` 之契約）。
IPGATE_CHANNEL = "ipgate:invalidate"
IPGATE_DOORBELL_PAYLOAD = "1"
SQL_IP_RULE_ROWS = 'SELECT json_agg(t) FROM (SELECT count(*) AS n FROM "sys_ip_rule") t'
# 基準檔模式 setval 之序列（五支皆依基準檔現讀）；seed 模式只 setval 其中非 runtime-append 者
RESTORE_SEQUENCES = ("sys_token_id_seq", "session_event_id_seq", "sys_login_attempt_id_seq",
                     "sys_ip_rule_id_seq", "sys_operation_log_id_seq")
SEED_SETVAL_SEQUENCES = tuple(s for s in RESTORE_SEQUENCES if s not in RUNTIME_APPEND_TABLES.values())
RESTORE_REDIS_PREFIXES = ("session", "throttle")
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

# ── 角色／選單域寫面（005 刀 U15、T088；restore ③b）──────────────────────────
# id 上界四表→其 id 序列（dict 序即刪除序）：seed 有列（archive 於 seed 零列、同形處置）＝不可 DELETE 全表、不套「基準列數非 0
# 即拒」——restore 只刪 id > 目標上界之列、序列 setval 回目標值；目標上界＝基準檔 id_bounds（max(id)、空表記 0）或凍結 seed 之
# COPY 列 id 最大值（零列記 0）。
BOUNDED_TABLES = {
    "sys_role": "sys_role_id_seq",
    "sys_menu": "sys_menu_id_seq",
    "casbin_rule": "casbin_rule_id_seq",
    "sys_casbin_policy_archive": "sys_casbin_policy_archive_id_seq",
}
# 指派表（複合主鍵 (user_id, role_id)、無 id 與序列）：以鍵集差刪除（現況有而目標無之對）。其 role_id 外鍵 ON DELETE RESTRICT
# 指 sys_role ⇒ 刪除排在四表之前；四表之間無外鍵（005 刀 U15 以 pg_constraint 現查）、次序取名冊序。
USER_ROLE_TABLE = "sys_user_role"
ROLE_MENU_TABLES = tuple(BOUNDED_TABLES) + (USER_ROLE_TABLE,)
# 基準檔 v2 兩欄之撈取（單句、唯讀）：四表 id 上界＋指派鍵集（依 user_id, role_id 排序）
SQL_BOUND_FACES = (
    "SELECT json_build_object('id_bounds', json_build_object("
    + ", ".join(f"'{t}', (SELECT COALESCE(max(id), 0) FROM {t})" for t in BOUNDED_TABLES)
    + f"), 'user_role_keys', (SELECT COALESCE(json_agg(json_build_array(user_id, role_id) "
      f"ORDER BY user_id, role_id), '[]'::json) FROM {USER_ROLE_TABLE}))")
# 重啟句判準之現讀（寫入前、唯讀）：casbin_rule 現況上界與其序列
SQL_CASBIN_STATE = ("SELECT json_build_object('max_id', (SELECT COALESCE(max(id), 0) FROM casbin_rule), "
                    "'seq', (SELECT json_build_object('last_value', last_value, 'is_called', is_called) "
                    "FROM casbin_rule_id_seq))")
# 重啟句（restore 實際刪過 casbin_rule 列或改過其序列時收尾輸出；self-test 逐字釘住）：判定面只在 rust-api 開機與自身寫端
# 同步時自庫載入、SQL 直改無外部通知管道。
RUST_API_RESTART_CLI = "docker compose -f docker-compose.yml -f docker-compose.dev.yml restart rust-api"
CASBIN_RESTART_HINT = ("[walkthrough-baseline] ★MUST 重啟 rust-api：本次 restore 以 SQL 直改 casbin_rule（刪列或改序列）、"
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
    """單引號字串常值（UNION ALL 各列的自帶名欄）。"""
    return "'" + name.replace("'", "''") + "'"


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
    """v2 兩欄形斷言（基準檔與現況撈取共用）：id_bounds＝恰 BOUNDED_TABLES 四鍵、值為非負整數（空表記 0）；
    user_role_keys＝[[user_id, role_id], …] 整數對。不符 → BaselineError（rc 2）。"""
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


def fetch_bound_faces(user, db, run):
    """基準檔 v2 兩欄（restore ③b 之目標值；非比對面之名冊式防法——全表列數仍由①現算）：四表 id 上界＋sys_user_role
    鍵集（排序）。輸出形不符 → rc 2。"""
    got = psql_json(SQL_BOUND_FACES, user, db, run)
    what = "角色／選單域兩欄撈取輸出形不符"
    if not isinstance(got, dict):
        raise BaselineError(f"{what}：須為 {{id_bounds, user_role_keys}} 物件")
    _check_bound_faces(got, what)
    return dict(got["id_bounds"]), sorted(got["user_role_keys"])


def snapshot_live(user=DB_USER, db=DB_NAME, run=subprocess.run, now=None):
    """三面現算＋v2 兩欄 → 基準 dict（含 taken_at UTC ISO＋schema_version）。"""
    taken = now or datetime.datetime.now(datetime.timezone.utc)
    snap = {
        "schema_version": SCHEMA_VERSION,
        "taken_at": taken.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tables": fetch_tables(user, db, run),
        "sequences": fetch_sequences(user, db, run),
        "redis": fetch_redis(run),
    }
    snap["id_bounds"], snap["user_role_keys"] = fetch_bound_faces(user, db, run)
    return snap


# ── 基準檔 ──────────────────────────────────────────────────────────────────

def validate_snapshot(obj):
    """檔形斷言（fail-loud）：缺鍵／型別錯／版本不符／零表零序列 → BaselineError。"""
    if not isinstance(obj, dict):
        raise BaselineError("基準檔壞形：頂層非 object")
    if obj.get("schema_version") != SCHEMA_VERSION:
        raise BaselineError(f"基準檔壞形：schema_version={obj.get('schema_version')!r}"
                            f"、本工具只認 {SCHEMA_VERSION}（重新 snapshot）")
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
    n = {face: sum(1 for r in rows if r["face"] == face) for face in ("表", "序列", "redis", "上界", "鍵集")}
    lines.append(f"[walkthrough-baseline] 摘要：表 {n['表']} 項差／序列 {n['序列']} 項差／"
                 f"redis {n['redis']} 項差／上界 {n['上界']} 項差／鍵集 {n['鍵集']} 項差"
                 f"（比對面：表 {t}／序列 {s}／redis {k} 鍵、{p} 前綴）")
    return lines


# ── 子命令 ──────────────────────────────────────────────────────────────────

def cmd_snapshot(path, user, db, run=subprocess.run):
    snap = snapshot_live(user, db, run)
    dump_snapshot(snap, path)
    t, s, k, p = _face_counts(snap)
    _say(f"[walkthrough-baseline] ✓ 基準已寫：{path}（表 {t}／序列 {s}／redis {k} 鍵、{p} 前綴；"
         f"taken_at {snap['taken_at']}）")
    # 走查**前**即告知 restore 前置不成立（restore 時才拒已在走查之後）；基準檔仍可供 diff、rc 不變
    high = bounds_above_sequence(snap)
    if high:
        _say("[walkthrough-baseline] ★告警：角色／選單域上界高於其序列位置（" + "、".join(high) + "）——本基準檔可供 diff、"
             "但以之 restore 將 rc 2 拒跑（取樣時已有顯式 id 殘列越過序列）；走查前先跑 "
             f"`python3 {PROG} restore --seed` 清殘列後重新 snapshot", err=True)
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


def _seed_copy_ints(blk, table, want):
    """COPY 段（_seed_copy_rows 之回傳）→ 逐列取 want 欄之整數 tuple。段首缺欄／列欄數不符／值非整數＝凍結面受損 rc 2。"""
    cols = [c.strip().strip('"') for c in blk[0].split(",")]
    missing = [c for c in want if c not in cols]
    if missing:
        raise BaselineError(f"seed {table} 段首缺 {'／'.join(missing)} 欄：{cols}——凍結面受損")
    idx = [cols.index(c) for c in want]
    out = []
    for row in blk[1]:
        vals = row.split("\t")
        if len(vals) != len(cols):
            raise BaselineError(f"seed {table} 列欄數 {len(vals)} ≠ 段首 {len(cols)}：{row[:80]!r}——凍結面受損")
        try:
            out.append(tuple(int(vals[i]) for i in idx))
        except ValueError:
            raise BaselineError(f"seed {table} 列之 {'／'.join(want)} 非整數：{row[:80]!r}——凍結面受損") from None
    return out


def seed_restore_target(seed_text):
    """seed 模式之目標態（形同基準檔之清理面子集、供 check_restore_baseline／restore_sql 同一套判定）：
    tables＝清理面各表與角色／選單域五表於凍結 seed 之 COPY 段列數；sequences＝清理面各序列與 BOUNDED_TABLES 四支之
    setval 行值；id_bounds＝四表 COPY 列 id 最大值（零列記 0）；user_role_keys＝sys_user_role COPY 鍵集（段缺席＝None）。
    段或行缺席者不入 dict（由 check_restore_baseline 指名為清理面缺席）；redis 於 seed 無載體＝兩前綴目標恆 0 鍵。"""
    lines = seed_text.splitlines()
    tables, seqs, bounds, keys = {}, {}, {}, None
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
    return {"tables": tables, "sequences": seqs, "redis": {"dbsize": 0, "prefixes": {}},
            "id_bounds": bounds, "user_role_keys": keys}


def seed_mode_baseline(live, target):
    """seed 模式無基準檔：以現況為底、只把清理面與角色／選單域覆寫成 seed 目標值（清理面五表列數、五支序列、兩前綴 0 鍵；
    角色／選單域五表列數、四表上界與序列、指派鍵集）→ 交 diff_snapshots 比。其餘面恆等於現況＝不入判準（無基準可比；
    該面之 pg 殘留由 tools/schema-gate.py check 之 gate2 逐列兜）。"""
    prefixes = {p: n for p, n in live["redis"]["prefixes"].items() if p not in RESTORE_REDIS_PREFIXES}
    cleared = sum(live["redis"]["prefixes"].get(p, 0) for p in RESTORE_REDIS_PREFIXES)
    return {"tables": dict(live["tables"], **target["tables"]),
            "sequences": dict(live["sequences"], **target["sequences"]),
            "redis": {"dbsize": live["redis"]["dbsize"] - cleared, "prefixes": prefixes},
            "id_bounds": dict(target["id_bounds"]), "user_role_keys": target["user_role_keys"]}


def seed_settings(seed_text):
    """凍結 seed.sql 之 `COPY public.system_settings` 段 → {setting_key: setting_value}。
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
    """演進帳有 `tables` 任一表之 seed_* 登記＝凍結 COPY 段已非期望 seed（期望＝凍結 ⊕ 演進、同 tools/schema-gate.py
    gate2 之 apply_seed_entries）。本工具左源未合成演進——system_settings 照比會把 migration 定義的合法值誤報為
    值≠seed、並給出「以寫端改回」的錯誤補救；seed 模式另以凍結段為清理面與角色／選單域之目標態（tables 加傳 RESTORE_TABLES
    與 ROLE_MENU_TABLES），照清會把演進帳定義的 seed 列一併 DELETE——故拒跑 rc 2、指名登記 id 與表。結構性 kind（add_column 等）不擋：
    不改列集與鍵值集。登記檔缺席／非 JSON／entries 非 list 或含非物件項＝rc 2（形之完整斷言權威在 schema-gate、
    此處只驗判定所需）。"""
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
        raise BaselineError(f"{SCHEMA_EVOLUTION} 有 restore 所倚 seed 面之演進登記：{'、'.join(hits)}——restore 之 "
                            "seed 左源只讀凍結 COPY 段、未合成演進（期望 seed＝凍結 ⊕ 演進），照比會把合法值誤報為值≠seed"
                            "（seed 模式另會把演進帳定義之 seed 列清掉）；先擴充本工具之 seed 左源合成、再跑 restore；"
                            "拒絕執行、零寫入")


def bounds_above_sequence(snap):
    """③b 前置之判定（純函式；snapshot 告警與 restore 兩模式拒跑共用）：BOUNDED_TABLES 四表之 id 上界高於其序列位置
    （nextval 已發出之最大值：is_called 真＝last_value、假＝last_value-1）者 → 指名字串 list。基準檔上成立＝取樣時已有顯式
    id 殘列越過序列（號段殘列）：走查以 nextval 造之列落在序列與上界之間、`id >` 上界刪不到，序列卻被 setval 回其下＝下一次
    nextval 撞 PK；凍結 seed 上成立＝凍結面受損。序列缺席者略（缺席由 check_restore_baseline 另判）。"""
    high = []
    for t, s in BOUNDED_TABLES.items():
        v = snap["sequences"].get(s)
        if v is not None and snap["id_bounds"][t] > v["last_value"] - (0 if v["is_called"] else 1):
            high.append(f"{t} 上界 {snap['id_bounds'][t]}＞{s}（{_seq_text(v)}）")
    return high


def check_restore_baseline(snap, seed_mode=False):
    """安全帶：清理面或角色／選單域之表、序列、上界、鍵集不在目標態（基準檔；seed 模式＝凍結 seed）＝結構異常；清理面各表
    列數或 session／throttle 前綴鍵數非 0＝拒跑。restore 只服務「目標態之清理面為空」之形——DELETE 全表對非空目標會連
    其資料一起毀掉、diff 還報不出來。★角色／選單域五表不套列數拒跑：其寫面只刪上界以上列與鍵集差、不毀目標態之列；
    改拒「目標態四表上界高於其序列位置」（bounds_above_sequence）：基準檔模式＝取樣時已有顯式 id 殘列越過序列、補救指
    seed 模式；seed 模式＝凍結面受損（真檔之 COPY 列 id 最大值恰等於其 setval 位置、自測釘住＝不觸發）。"""
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
                            "（以凍結 seed 為目標態、無須基準檔）")
    high = bounds_above_sequence(snap)
    if high and seed_mode:
        raise BaselineError(f"{origin}{sep}之角色／選單域上界高於其序列位置（" + "、".join(high) + "）——凍結面受損："
                            "照跑則序列 setval 回 seed 值後、下一次 nextval 撞 seed 列 PK；拒絕執行、零寫入")
    if high:
        raise BaselineError("基準檔之角色／選單域上界高於其序列位置（" + "、".join(high) + "）——取樣時已有顯式 id 殘列越過"
                            "序列：走查以 nextval 造之列落在序列與上界之間、刪不到，序列卻被 setval 回其下＝下一次 nextval 撞 PK；"
                            f"拒絕執行、零寫入。補救：改跑 `python3 {PROG} restore --seed`（目標態＝凍結 seed、殘列一併刪除）；"
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
    """①system_settings 現況 vs seed：鍵缺／鍵多／值不等＝fail-loud 指名（restore 不改值）；回審計欄非 NULL 之列數。"""
    need = {"setting_key", "setting_value", "stamped"}
    if not isinstance(live_rows, list) or not all(isinstance(r, dict) and need <= set(r) for r in live_rows):
        raise BaselineError("system_settings 撈取輸出形不符（須為 [{setting_key, setting_value, stamped}]）")
    live = {r["setting_key"]: r["setting_value"] for r in live_rows}
    bad = [f"{k} 現值缺席／seed {seed[k]!r}" for k in sorted(set(seed) - set(live))] + \
          [f"{k} 現值 {live[k]!r}／seed 無此鍵" for k in sorted(set(live) - set(seed))] + \
          [f"{k} 現值 {live[k]!r}／seed {seed[k]!r}" for k in sorted(set(seed) & set(live))
           if live[k] != seed[k]]
    if bad:
        raise BaselineError("system_settings 與 seed 不等——restore 不自動改值（先以 002 刀 system_settings "
                            "寫端改回 seed 值、再跑 restore）：" + "；".join(bad))
    return sum(1 for r in live_rows if r["stamped"])


def _setval_sql(name, v):
    return f"SELECT setval('{name}', {v['last_value']}, {'true' if v['is_called'] else 'false'});"


def restore_sql(snap, sequences=RESTORE_SEQUENCES, seed_surface=()):
    """②③ 單交易寫句：審計欄歸 NULL → 五表 DELETE＋session_id 歸 NULL → setval（值自目標態 snap 現讀；
    基準檔模式＝RESTORE_SEQUENCES 五支、seed 模式＝SEED_SETVAL_SEQUENCES——runtime-append 序列不復位）→ seed_surface
    （③b 角色／選單域寫句、seed_surface_sql 產；cmd_restore 兩模式恆帶、接在 COMMIT 之前）。"""
    seqs = snap["sequences"]
    setvals = tuple(_setval_sql(n, seqs[n]) for n in sequences)
    return " ".join(("BEGIN;", SQL_RESTORE_AUDIT) + SQL_RESTORE_CLEAR + setvals + tuple(seed_surface) + ("COMMIT;",))


def seed_surface_sql(snap):
    """③b 角色／選單域寫句（值自目標態 snap 現讀：基準檔 v2 兩欄＋序列面，或 seed_restore_target）：sys_user_role 鍵集差
    刪除（現況有而目標無之對；目標鍵集空＝全清）→ BOUNDED_TABLES 四表依名冊序刪 `id >` 上界 → 四支 setval 回目標值。
    ★四表絕不 DELETE 全表（seed 有列）；id ≤ 上界之列（含 seed 列）之就地改寫與被刪不在射程——只刪不補、不改欄值。"""
    keys = sorted(tuple(k) for k in snap["user_role_keys"])
    if keys:
        keep = ", ".join(f"({u}, {r})" for u, r in keys)
        user_role = f"DELETE FROM {USER_ROLE_TABLE} WHERE (user_id, role_id) NOT IN (VALUES {keep});"
    else:
        user_role = f"DELETE FROM {USER_ROLE_TABLE};"
    deletes = tuple(f"DELETE FROM {t} WHERE id > {snap['id_bounds'][t]};" for t in BOUNDED_TABLES)
    setvals = tuple(_setval_sql(s, snap["sequences"][s]) for s in BOUNDED_TABLES.values())
    return (user_role,) + deletes + setvals


def casbin_restore_touches(state, target):
    """⑥重啟句判準（寫入前現讀 SQL_CASBIN_STATE）：現況 casbin_rule 有 id > 目標上界之列（③b 會刪）或其序列≠目標值
    （③b 會 setval 改值）＝本次 restore 直改判定面左源。輸出形不符 → rc 2（仍在任何寫入之前）。"""
    seq = state.get("seq") if isinstance(state, dict) else None
    if not (isinstance(seq, dict) and isinstance(state.get("max_id"), int)
            and not isinstance(state["max_id"], bool) and isinstance(seq.get("last_value"), int)
            and isinstance(seq.get("is_called"), bool)):
        raise BaselineError("casbin_rule 現態撈取輸出形不符（須為 {max_id, seq: {last_value, is_called}}）"
                            "——輸出被污染或查詢形改變；拒絕執行、零寫入")
    want = target["sequences"][BOUNDED_TABLES["casbin_rule"]]
    return state["max_id"] > target["id_bounds"]["casbin_rule"] or \
        (seq["last_value"], seq["is_called"]) != (want["last_value"], want["is_called"])


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


def cmd_restore(path, user, db, run=subprocess.run, seed_path=None, ledger_path=None):
    """path＝基準檔（目標態＝該檔、清理面五支＋角色／選單域四支序列依檔 setval、收尾＝對該檔 diff）；path=None＝seed
    模式（目標態＝凍結 seed 之清理面與角色／選單域、清理面只 setval SEED_SETVAL_SEQUENCES＋角色／選單域四支、收尾＝兩面對
    seed 目標值之比對）。前置判定與重啟句判準之現讀皆在任何寫入之前；重啟句於收尾（含提交後失敗路徑）輸出。"""
    seed_mode = path is None
    seed_text = _read_seed(seed_path or os.path.join(REPO_ROOT, SEED_FIXTURE))
    base = seed_restore_target(seed_text) if seed_mode else load_snapshot(path)
    check_restore_baseline(base, seed_mode)
    check_seed_evolution(ledger_path or os.path.join(REPO_ROOT, SCHEMA_EVOLUTION),
                         ("system_settings",) + (RESTORE_TABLES + ROLE_MENU_TABLES if seed_mode else ()))
    sequences = SEED_SETVAL_SEQUENCES if seed_mode else RESTORE_SEQUENCES
    seed = seed_settings(seed_text)
    # 門鈴判準（BL-00094）：清前列數須在任何寫入之前取——DELETE 之後就再也問不到「規則集有沒有變」。
    # ★`sys_ip_rule` 在 RESTORE_TABLES 內由 test_restore_tables_roster 釘住，此處不再寫常真守衛（mb4t review L1-10）。
    ip_rows = int((psql_json(SQL_IP_RULE_ROWS, user, db, run) or [{"n": 0}])[0]["n"])
    stamped = check_settings_against_seed(psql_json(SQL_SETTINGS, user, db, run), seed)
    _say(f"[walkthrough-baseline] restore ①system_settings：{len(seed)} 鍵值＝seed；"
         f"審計欄非 NULL {stamped} 列（交易內歸 NULL）")
    # 重啟句判準（⑥）須在任何寫入之前現讀——交易提交後就再也問不到「有沒有刪過 casbin_rule 列、改過其序列」。
    casbin_touched = casbin_restore_touches(psql_json(SQL_CASBIN_STATE, user, db, run), base)
    r = _run_docker(psql_argv(restore_sql(base, sequences, seed_surface_sql(base)), user, db), run)
    if r.returncode != 0:
        raise BaselineError(f"restore 交易失敗（rc={r.returncode}、整筆回滾、未動 redis）："
                            f"{(r.stderr or '').strip()[:300]}"
                            "；補救：依上列 psql 錯誤修正（常見＝postgres 容器未起）後重跑同一 restore（交易已回滾、可安全重跑）")
    try:
        seqs = "、".join(f"{n}（{_seq_text(base['sequences'][n])}）" for n in sequences)
        _say(f"[walkthrough-baseline] restore ②③pg 單交易已提交：DELETE {'／'.join(RESTORE_TABLES)}＋"
             f"sys_user.session_id 歸 NULL＋setval（{seqs}）")
        bounds = "／".join(f"{t} ≤{base['id_bounds'][t]}" for t in BOUNDED_TABLES)
        role_seqs = "、".join(f"{s}（{_seq_text(base['sequences'][s])}）" for s in BOUNDED_TABLES.values())
        _say(f"[walkthrough-baseline] restore ③b（同一交易）：{USER_ROLE_TABLE} 鍵集差刪除（目標 "
             f"{len(base['user_role_keys'])} 對之外）→ 刪 id > 上界（{bounds}）＋setval（{role_seqs}）")
        # ★門鈴排在 pg 交易之後、redis 清理之前（mb4t review L1-1）：規則列此刻已從庫裡消失，判定面必須換版；
        # 排在 redis 清理之後會被「DEL 失敗即拋」吃掉，而依其補救訊息重跑時清前列數已是 0＝永遠補不回來。
        ring_doorbell(ip_rows, run)
        found, deleted = redis_clear_prefixes(run)
        counts = "／".join(f"{p} 前綴 {n} 鍵" for p, n in found.items())
        _say(f"[walkthrough-baseline] restore ④redis：{counts}、DEL 回報 {deleted} 鍵（逐鍵指名）")
        if seed_mode:
            _say("[walkthrough-baseline] restore ⑤收尾比對（seed 模式：判準面＝清理面與角色／選單域對凍結 seed 目標值、"
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
         f"restore <檔>＝走查後清理（安全帶：清理面五表之基準須為空、角色／選單域四表之基準上界須不高於其序列；"
         f"角色／選單域刪上界以上列與鍵集差）＋收尾 diff"
         f"（rc 即 diff 之 rc；動過 casbin_rule 即輸出重啟 rust-api 句）；"
         f"restore --seed＝無基準檔、清理面與角色／選單域還原到凍結 seed 態（runtime-append 序列不復位）；"
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
                 "名冊對賬 schema-gate；restore 寫面逐字＋次序、清理面五表五序列、"
                 "setval 自基準現讀、安全帶拒跑零呼叫、清理面缺席、settings 值≠seed 零寫入、收尾 diff rc、"
                 "失敗即停、DEL 分批、seed 解析與空面、演進帳 system_settings seed 登記拒跑／他表與結構性登記不擋／"
                 "登記檔缺席壞形、預設 seed 與演進帳哨兵與 --user／--db；seed 模式寫面逐字＋清理面只 setval 非 runtime-append 序列、"
                 "seed 模式前置拒跑零寫入、seed 模式走真凍結 seed；檔形 v2 兩欄（空表上界 0、鍵集排序、v1 拒收、壞形）＋"
                 "diff 比兩欄、③b 角色／選單域寫面逐字＋次序＋值自基準現讀＋空鍵集形、安全帶不攔有列之該面、"
                 "基準上界高於序列即拒零呼叫＋snapshot 告警＋seed 模式可收、"
                 "重啟句字面與出現（只刪列／只改序列兩腿各自成案、序列腿前進／後退／is_called 異三形、兩腿參照值＝目標上界／"
                 "目標序列值各自區辨）／不出現、seed 模式該面目標自凍結 seed 與受損／缺段／演進帳拒跑）")
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
# 角色／選單域樁（005 刀 U15）：四表之 id 集＋指派鍵集，形同凍結 seed（3／78／163／0 列、指派 3 對）。表名手寫、不自受測常數衍生。
STUB_BOUNDED_IDS = {"sys_role": tuple(range(1, 4)), "sys_menu": tuple(range(1, 79)),
                    "casbin_rule": tuple(range(1, 164)), "sys_casbin_policy_archive": ()}
STUB_USER_ROLES = ((1, 1), (2, 2), (3, 3))


def _completed(argv, rc, stdout="", stderr=""):
    return subprocess.CompletedProcess(argv, rc, stdout, stderr)


class _StubRun:
    """樁 subprocess.run：依 argv 分流 psql（依 SQL 內容）／redis（依命令）；記錄每次 argv。
    restore 路徑另模擬寫面：交易句依其 DELETE／setval／審計 UPDATE 改樁內狀態、DEL 刪樁內鍵——
    收尾 diff 因此對著「被 restore 改過的樁」算，rc 0／1 皆真實走過。"""

    def __init__(self, tables=None, seqs=None, keys=None, dbsize=None, fail=None, garble=None,
                 truncate=None, settings=None, subs=1, ids=None, user_roles=None):
        self.tables = dict(FAKE_TABLES if tables is None else tables)
        self.seqs = dict(FAKE_SEQS if seqs is None else seqs)
        self.keys = list(FAKE_KEYS if keys is None else keys)
        # 角色／選單域四表之 id 集與指派鍵集（SQL_BOUND_FACES／SQL_CASBIN_STATE 依此回；交易之上界刪除與鍵集差刪除改之）
        self.ids = {t: list(v) for t, v in (STUB_BOUNDED_IDS if ids is None else ids).items()}
        self.user_roles = [tuple(k) for k in (STUB_USER_ROLES if user_roles is None else user_roles)]
        self._dbsize = dbsize       # None＝隨現存鍵數（DEL 後同步變小）
        self.settings = [dict(s) for s in (settings or [])]
        self.subs = subs            # PUBLISH 回報之訂閱者數（門鈴腿；0＝無 watcher 在訂）
        self.fail = fail            # "psql"／"redis"＝該支非零退出；"tx"＝交易句失敗；"del"＝DEL 回非整數
        self.garble = garble        # "tables"／"seqs"／"settings"／"bounds"／"casbin"＝該面回不可解輸出（缺欄／非整數／非 JSON）
        self.truncate = truncate    # "tables"／"seqs"＝該面值腿少回一列（輸出被截斷／撈取不完整）
        self.log = []

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
                for t in re.findall(r"DELETE FROM (\w+);", sql):
                    self.tables[t] = 0
                    if t == "sys_user_role":
                        self.user_roles = []
                m = re.search(r"DELETE FROM sys_user_role WHERE \(user_id, role_id\) NOT IN \(VALUES (.*?)\);", sql)
                if m:
                    keep = {(int(u), int(r)) for u, r in re.findall(r"\((\d+), (\d+)\)", m.group(1))}
                    gone = [k for k in self.user_roles if k not in keep]
                    self.user_roles = [k for k in self.user_roles if k in keep]
                    self.tables["sys_user_role"] = self.tables.get("sys_user_role", 0) - len(gone)
                for t, bound in re.findall(r"DELETE FROM (\w+) WHERE id > (\d+);", sql):
                    gone = [i for i in self.ids.get(t, []) if i > int(bound)]
                    self.ids[t] = [i for i in self.ids.get(t, []) if i <= int(bound)]
                    if t in self.tables:
                        self.tables[t] -= len(gone)
                for name, v, called in re.findall(r"setval\('(\w+)', (\d+), (true|false)\)", sql):
                    self.seqs[name] = (int(v), "t" if called == "true" else "f")
                if sql.count("UPDATE system_settings SET updated_at = NULL, updated_by = NULL"):
                    for s in self.settings:
                        s["stamped"] = False
                return _completed(argv, 0, "COMMIT\n", "")
            elif sql == SQL_IP_RULE_ROWS:
                return _completed(argv, 0, json.dumps([{"n": self.tables.get("sys_ip_rule", 0)}]) + "\n", "")
            elif sql == SQL_BOUND_FACES:
                if self.garble == "bounds":
                    return _completed(argv, 0, json.dumps({"id_bounds": {"sys_role": "3"}}) + "\n", "")
                return _completed(argv, 0, json.dumps({
                    "id_bounds": {t: max(v, default=0) for t, v in self.ids.items()},
                    "user_role_keys": [list(k) for k in sorted(self.user_roles)]}) + "\n", "")
            elif sql == SQL_CASBIN_STATE:
                if self.garble == "casbin":
                    return _completed(argv, 0, json.dumps({"max_id": 1}) + "\n", "")
                v, called = self.seqs.get("casbin_rule_id_seq", (1, "f"))
                return _completed(argv, 0, json.dumps({
                    "max_id": max(self.ids.get("casbin_rule", []), default=0),
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
            "id_bounds": {"sys_role": 3, "sys_menu": 78, "casbin_rule": 163, "sys_casbin_policy_archive": 0},
            "user_role_keys": [[1, 1], [2, 2], [3, 3]]}
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
        """★runtime-append 四表之 id 序列只比存在性、不比值（同 tools/schema-gate.py gate2 對其 setval 值正規化之口徑）：
        這四支序列在測試與走查中只進不退（rust-api 測試守衛只清自寫列、序列不復位），逐值比＝每跑一次全量測試
        diff 即恆紅、「rc 0 才算環境已還原」失去判別力。三腿：①四支值皆不同→全等 ②其一於現況或基準缺席→有差
        ③名冊外序列（含 sys_ip_rule_id_seq＝業務表、序列值在比對面內）值不同→照報。"""
        names = ("session_event_id_seq", "sys_login_attempt_id_seq", "sys_operation_log_id_seq",
                 "sys_token_id_seq")

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
        一支＝該序列之值漂移靜默不報——兩向皆由本案指名。另釘 restore 清理面與名冊之關係：四表全在清理面、
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
    """基準檔形 v2（005 刀 U15、T088①）：角色／選單域四表 id 上界欄（max(id)、空表記 0）＋sys_user_role 鍵集欄；
    v1 檔 diff／restore 一律 rc 2 指名重新 snapshot；diff 比對兩新欄。"""

    def test_schema_version_rosters_and_bound_sqls_are_pinned(self):
        """版本、名冊（dict 序＝刪除序）與兩句撈取 SQL 逐字釘；兩句皆過唯讀判準。"""
        self.assertEqual(SCHEMA_VERSION, 2)
        self.assertEqual(BOUNDED_TABLES, {"sys_role": "sys_role_id_seq", "sys_menu": "sys_menu_id_seq",
                                          "casbin_rule": "casbin_rule_id_seq",
                                          "sys_casbin_policy_archive": "sys_casbin_policy_archive_id_seq"})
        self.assertEqual(list(BOUNDED_TABLES), ["sys_role", "sys_menu", "casbin_rule", "sys_casbin_policy_archive"])
        self.assertEqual(USER_ROLE_TABLE, "sys_user_role")
        self.assertEqual(ROLE_MENU_TABLES, ("sys_role", "sys_menu", "casbin_rule", "sys_casbin_policy_archive",
                                            "sys_user_role"))
        self.assertEqual(SQL_BOUND_FACES,
                         "SELECT json_build_object('id_bounds', json_build_object("
                         "'sys_role', (SELECT COALESCE(max(id), 0) FROM sys_role), "
                         "'sys_menu', (SELECT COALESCE(max(id), 0) FROM sys_menu), "
                         "'casbin_rule', (SELECT COALESCE(max(id), 0) FROM casbin_rule), "
                         "'sys_casbin_policy_archive', (SELECT COALESCE(max(id), 0) FROM sys_casbin_policy_archive)), "
                         "'user_role_keys', (SELECT COALESCE(json_agg(json_build_array(user_id, role_id) "
                         "ORDER BY user_id, role_id), '[]'::json) FROM sys_user_role))")
        self.assertEqual(SQL_CASBIN_STATE,
                         "SELECT json_build_object('max_id', (SELECT COALESCE(max(id), 0) FROM casbin_rule), "
                         "'seq', (SELECT json_build_object('last_value', last_value, 'is_called', is_called) "
                         "FROM casbin_rule_id_seq))")
        self.assertEqual(_pg_write_offenders([SQL_BOUND_FACES, SQL_CASBIN_STATE]), [])

    def test_snapshot_carries_id_bounds_with_empty_table_as_0_and_sorted_user_role_keys(self):
        """★空表之上界定形為 0（非 null）：restore 以 `id > 0` 刪、語意＝走查前空表之新列全清；鍵集依 (user_id, role_id) 排序。"""
        stub = _StubRun(ids={"sys_role": (1, 2, 5), "sys_menu": (1,), "casbin_rule": (1, 2),
                             "sys_casbin_policy_archive": ()}, user_roles=((3, 3), (1, 5), (1, 1)))
        snap = snapshot_live(run=stub)
        self.assertEqual(snap["schema_version"], 2)
        self.assertEqual(snap["id_bounds"], {"sys_role": 5, "sys_menu": 1, "casbin_rule": 2,
                                             "sys_casbin_policy_archive": 0})
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
        del v1["id_bounds"], v1["user_role_keys"]
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
        self.assertEqual(len(sqls), 5)                   # 表清單／表列數／序列清單／序列值／角色選單域兩欄（v2）
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
                        " --scan --pattern 'throttle:*'")


def _pg_write_offenders(sqls):
    """唯讀判準：非 SELECT 起首、或含寫入字詞（字詞邊界比對——updated_at 之類欄名不誤觸）者皆列出。"""
    return [s for s in sqls if not s.startswith("SELECT ") or _WRITE_WORDS.search(s.upper())]


def _redis_write_offenders(cmds):
    """唯讀判準：redis 命令只准 DBSIZE／--scan（含 restore 兩前綴樣式掃描）；其餘一律列出。"""
    return [c for c in cmds if not c.endswith(_REDIS_READ_SUFFIXES)]


RESTORE_FAKE_TABLES = {"sys_user": 3, "sys_token": 0, "session_event": 0, "sys_login_attempt": 0,
                       "sys_ip_rule": 0, "sys_operation_log": 0,
                       "system_settings": 2, "seaql_migrations": 7,
                       "sys_role": 3, "sys_menu": 78, "casbin_rule": 163, "sys_casbin_policy_archive": 0,
                       "sys_user_role": 3}
RESTORE_FAKE_SEQS = {"sys_user_id_seq": (3, "t"), "sys_token_id_seq": (1, "f"),
                     "session_event_id_seq": (1, "f"), "sys_login_attempt_id_seq": (1, "f"),
                     "sys_ip_rule_id_seq": (1, "f"), "sys_operation_log_id_seq": (1, "f"),
                     "sys_role_id_seq": (3, "t"), "sys_menu_id_seq": (78, "t"), "casbin_rule_id_seq": (163, "t"),
                     "sys_casbin_policy_archive_id_seq": (1, "f")}
SEED_SETTINGS_TEXT = (
    "--\n-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: soybean\n--\n\n"
    "COPY public.system_settings (setting_key, created_at, updated_at, updated_by, setting_type, "
    "setting_value, description) FROM stdin;\n"
    "session_idle_timeout\t2026-08-05 00:00:00+00\t\\N\t\\N\tnumber\t60\t閒置逾時\n"
    "single_session_default\t2026-08-05 00:00:00+00\t\\N\t\\N\tenum:on,off\toff\t全站單一-session 預設\n"
    "\\.\n")

# 清理面五表之測試側手寫名冊（不自受測常數 RESTORE_TABLES 衍生——常數縮水時跟著縮＝套套邏輯）
FIVE_TABLES = ("session_event", "sys_token", "sys_login_attempt", "sys_ip_rule", "sys_operation_log")
# ③b 角色／選單域寫面於「目標＝seed 形（3／78／163／0、指派 3 對）」時之逐字期望（005 刀 U15；手寫、不自受測常數衍生）：
# 指派鍵集差刪除先於四表、四表刪上界以上列、四支 setval——接在清理面 setval 之後、COMMIT 之前
ROLE_MENU_SURFACE_AT_SEED = (
    "DELETE FROM sys_user_role WHERE (user_id, role_id) NOT IN (VALUES (1, 1), (2, 2), (3, 3)); "
    "DELETE FROM sys_role WHERE id > 3; "
    "DELETE FROM sys_menu WHERE id > 78; "
    "DELETE FROM casbin_rule WHERE id > 163; "
    "DELETE FROM sys_casbin_policy_archive WHERE id > 0; "
    "SELECT setval('sys_role_id_seq', 3, true); "
    "SELECT setval('sys_menu_id_seq', 78, true); "
    "SELECT setval('casbin_rule_id_seq', 163, true); "
    "SELECT setval('sys_casbin_policy_archive_id_seq', 1, false); ")
# seed 模式左源樁：上段＋清理面五表之零列 COPY 段＋五支 setval 行。表名與序列名字面手寫、不自受測常數衍生
# （常數縮水時樁跟著縮＝套套邏輯）；sys_ip_rule_id_seq 刻意取非預設值、證 setval 值自 seed 現讀而非寫死。
SEED_RESTORE_TEXT = SEED_SETTINGS_TEXT + "".join(
    f"\nCOPY public.{t} (id, created_at) FROM stdin;\n\\.\n"
    for t in FIVE_TABLES) + "".join(
    f"\nSELECT pg_catalog.setval('public.{s}', {v});\n"
    for s, v in (("session_event_id_seq", "1, false"), ("sys_ip_rule_id_seq", "7, true"),
                 ("sys_login_attempt_id_seq", "1, false"), ("sys_operation_log_id_seq", "1, false"),
                 ("sys_token_id_seq", "1, false"))) + (
    # 角色／選單域五表（005 刀 U15）：形同真凍結 seed（3／78／163／0 列、指派 3 對、四支 setval）；表名與序列名手寫
    "\nCOPY public.sys_role (id, created_at, role_code) FROM stdin;\n"
    + "".join(f"{i}\t2026-08-05 00:00:00+00\tR_{i}\n" for i in range(1, 4)) + "\\.\n"
    "\nCOPY public.sys_menu (id, \"order\", menu_name) FROM stdin;\n"
    + "".join(f"{i}\t{i}\tm{i}\n" for i in range(1, 79)) + "\\.\n"
    "\nCOPY public.casbin_rule (id, ptype, v0) FROM stdin;\n"
    + "".join(f"{i}\tp\tR_1\n" for i in range(1, 164)) + "\\.\n"
    "\nCOPY public.sys_casbin_policy_archive (id, role_id, ptype) FROM stdin;\n\\.\n"
    "\nCOPY public.sys_user_role (user_id, role_id) FROM stdin;\n1\t1\n2\t2\n3\t3\n\\.\n"
    "\nSELECT pg_catalog.setval('public.sys_role_id_seq', 3, true);\n"
    "\nSELECT pg_catalog.setval('public.sys_menu_id_seq', 78, true);\n"
    "\nSELECT pg_catalog.setval('public.casbin_rule_id_seq', 163, true);\n"
    "\nSELECT pg_catalog.setval('public.sys_casbin_policy_archive_id_seq', 1, false);\n")


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


class TestRestore(unittest.TestCase):
    """restore 五步：安全帶（清理面五表之基準須為空）→system_settings 對 seed（值不等 fail-loud、不改值）→pg 單交易
    （寫句恰為列舉、setval 自基準檔現讀）→redis 兩前綴逐鍵指名 DEL（絕不 FLUSHDB）→收尾 diff 之 rc 即 restore 之 rc。"""

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
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cmd_snapshot(path, DB_USER, DB_NAME, stub), RC_OK)
        stub.log.clear()
        return path

    def _restore(self, path, stub):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
        return rc, out.getvalue() + err.getvalue()

    def _restore_seed(self, stub, seed_text=SEED_RESTORE_TEXT):
        """seed 模式（path=None＝無基準檔）；左源＝樁 seed 檔。"""
        with open(self.seed, "w", encoding="utf-8") as fh:
            fh.write(seed_text)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cmd_restore(None, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
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
            "DELETE FROM sys_ip_rule; DELETE FROM sys_operation_log; "
            "UPDATE sys_user SET session_id = NULL WHERE session_id IS NOT NULL; "
            "SELECT setval('sys_token_id_seq', 5, true); "
            "SELECT setval('session_event_id_seq', 1, false); "
            "SELECT setval('sys_login_attempt_id_seq', 1, false); "
            "SELECT setval('sys_ip_rule_id_seq', 1, false); "
            "SELECT setval('sys_operation_log_id_seq', 1, false); "
            + ROLE_MENU_SURFACE_AT_SEED +
            "COMMIT;"])
        redis_cmds = [a[-1] for a in stub.log if "sh" in a]
        self.assertEqual(_redis_write_offenders(redis_cmds), [
            f"{REDIS_CLI} PUBLISH {IPGATE_CHANNEL} {IPGATE_DOORBELL_PAYLOAD}",   # ★門鈴排在 DEL 之前（L1-1）
            f"{REDIS_CLI} DEL session:denylist:sid-b session:sid-a:last_activity "
            "'throttle:unlock:user:走查 探針'"])
        self.assertFalse(any("FLUSH" in c.upper() for c in redis_cmds))
        self.assertEqual(stub.keys, ["plainkey"])                      # 非清理前綴之鍵不動
        self.assertFalse(any(s["stamped"] for s in stub.settings))     # 審計欄已歸 NULL
        # 次序：settings 讀 → 交易 → 前綴掃 → DEL → 收尾 diff 取樣
        flat = [a[-1] for a in stub.log]
        order = (flat.index(SQL_SETTINGS), flat.index(writes[0]),
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
                                "sys_operation_log_id_seq": {"last_value": 5, "is_called": False}},
                     redis={"dbsize": 0, "prefixes": {}})
        sql = restore_sql(snap)
        self.assertTrue(sql.endswith("SELECT setval('sys_token_id_seq', 9, true); "
                                     "SELECT setval('session_event_id_seq', 8, false); "
                                     "SELECT setval('sys_login_attempt_id_seq', 7, true); "
                                     "SELECT setval('sys_ip_rule_id_seq', 6, true); "
                                     "SELECT setval('sys_operation_log_id_seq', 5, false); COMMIT;"),
                        msg=sql)
        self.assertEqual(sql.count("setval("), 5)

    def test_nonempty_baseline_refuses_rc2_before_any_docker_call(self):
        """★安全帶：基準檔清理面任一表列數或 session／throttle 前綴鍵數非 0＝rc 2、零 docker 呼叫＝零寫入
        （本案走會話三表與兩前綴；sys_ip_rule／sys_operation_log 兩表由擴面案走）。"""
        for over in ({"tables": dict(RESTORE_FAKE_TABLES, sys_token=2)},
                     {"tables": dict(RESTORE_FAKE_TABLES, session_event=1)},
                     {"tables": dict(RESTORE_FAKE_TABLES, sys_login_attempt=4)},
                     {"keys": ["plainkey", "session:sid-x"]},
                     {"keys": ["throttle:unlock:ip:203.0.113.9"]}):
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
        """值≠seed（含鍵缺／鍵多）＝fail-loud 指名、不自動改值；只讀過 settings 一句、零寫入。"""
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
            self.assertEqual([a[-1] for a in stub.log], [SQL_IP_RULE_ROWS, SQL_SETTINGS])   # 清前計數為讀、排在 settings 讀之前（BL-00094）

    def test_restore_rc_is_the_final_diff_rc(self):
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)
        stub.tables["sys_user"] = 4                 # 清理面之外的殘留：restore 不碰、收尾 diff 照報
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_DIFF)
        self.assertIn("表｜sys_user｜3｜4｜1", text)
        self.assertEqual((stub.tables["sys_token"], stub.keys), (0, ["plainkey"]))

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

    def test_system_settings_seed_evolution_entry_refuses_by_id_before_any_docker_call(self):
        """★seed 左源只讀凍結 COPY 段、未合成演進帳：帳上一有 system_settings 之 seed_* 登記，凍結段即非期望 seed
        （期望＝凍結 ⊕ 演進、同 tools/schema-gate.py gate2）——照比會把 migration 定義的合法值報成「值≠seed」、
        並叫操作者以 002 刀寫端改回（seed_add 之新鍵更無從經寫端刪除）。三 kind 任一＝指名登記 id、明說先擴充
        本工具、不出寫端補救句、零 docker 呼叫＝零寫入；同帳他表之登記不影響判定。"""
        other = _ledger_entry("E-001", "seed_update", "sys_user",
                              {"pk": {"id": 3}, "set": {"nick_name": "User01"}})
        for eid, kind, detail in (
                ("E-002", "seed_add", {"pk": ["setting_key"],
                                       "values": {"setting_key": "trusted_proxy_cidrs"}}),
                ("E-003", "seed_update", {"pk": {"setting_key": "session_idle_timeout"},
                                          "set": {"setting_value": "30"}}),
                ("E-004", "seed_delete", {"pk": {"setting_key": "single_session_default"}})):
            self._write_ledger(other, _ledger_entry(eid, kind, "system_settings", detail))
            stub = _restore_stub()
            path = self._baseline(stub)
            self._dirty(stub)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
            msg = str(ctx.exception)
            for needle in (eid, kind, "system_settings", "先擴充本工具", "零寫入"):
                self.assertIn(needle, msg, msg=kind)
            self.assertNotIn("E-001", msg, msg=kind)
            self.assertNotIn("002 刀", msg, msg=kind)
            self.assertEqual(stub.log, [], msg=kind)

    def test_evolution_entries_off_system_settings_seed_kinds_do_not_block(self):
        """反面：他表之 seed_* 登記、system_settings 之結構性登記（add_column＝nullable 無 default、不改鍵值集）
        皆不擋——restore 照常清理、收尾 diff rc 0。"""
        self._write_ledger(
            _ledger_entry("E-001", "seed_update", "sys_user", {"pk": {"id": 3}, "set": {"nick_name": "User01"}}),
            _ledger_entry("E-002", "add_column", "system_settings",
                          {"column": "note", "type": "text", "nullable": True}))
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertEqual((stub.tables["sys_token"], stub.keys), (0, ["plainkey"]))

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

    def test_restore_surface_is_five_tables_and_their_sequences(self):
        """★擴面（BL-00075；004 刀 U3）：清理面＝會話三表＋sys_ip_rule＋sys_operation_log 與其 id 序列。名冊與清列句
        逐字釘（多一表、少一表、換序皆紅）；安全帶與清理面缺席判定同步涵蓋新增之兩表兩序列；走一趟後五表歸零、
        五支序列回到基準檔之值（基準檔模式仍依檔 setval——runtime-append 四支亦然）。"""
        self.assertEqual(RESTORE_TABLES, FIVE_TABLES)
        self.assertEqual(RESTORE_SEQUENCES, ("sys_token_id_seq", "session_event_id_seq",
                                             "sys_login_attempt_id_seq", "sys_ip_rule_id_seq",
                                             "sys_operation_log_id_seq"))
        self.assertEqual(SQL_RESTORE_CLEAR, (
            "DELETE FROM session_event;", "DELETE FROM sys_token;", "DELETE FROM sys_login_attempt;",
            "DELETE FROM sys_ip_rule;", "DELETE FROM sys_operation_log;",
            "UPDATE sys_user SET session_id = NULL WHERE session_id IS NOT NULL;"))
        for over in ({"tables": dict(RESTORE_FAKE_TABLES, sys_ip_rule=1)},
                     {"tables": dict(RESTORE_FAKE_TABLES, sys_operation_log=2)}):
            stub = _restore_stub(**over)
            path = self._baseline(stub)
            with self.assertRaises(BaselineError, msg=over) as ctx:
                cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
            self.assertIn("基準非空、DELETE 全表會毀掉基準資料", str(ctx.exception), msg=over)
            self.assertIn("restore --seed", str(ctx.exception), msg=over)     # 補救指向 seed 模式
            self.assertEqual(stub.log, [], msg=over)
        for over, needle in (({"tables": {k: v for k, v in RESTORE_FAKE_TABLES.items()
                                          if k != "sys_ip_rule"}}, "sys_ip_rule"),
                             ({"seqs": {k: v for k, v in RESTORE_FAKE_SEQS.items()
                                        if k != "sys_operation_log_id_seq"}}, "sys_operation_log_id_seq")):
            stub = _restore_stub(**over)
            path = self._baseline(stub)
            with self.assertRaises(BaselineError, msg=needle) as ctx:
                cmd_restore(path, DB_USER, DB_NAME, stub, seed_path=self.seed, ledger_path=self.ledger)
            self.assertIn(needle, str(ctx.exception))
            self.assertEqual(stub.log, [])
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        self.assertEqual([stub.tables[t] for t in FIVE_TABLES], [0] * 5)
        self.assertEqual(stub.seqs, RESTORE_FAKE_SEQS)

    def test_seed_mode_clears_five_tables_and_setvals_only_the_ip_rule_sequence_from_seed(self):
        """★seed 模式（`restore --seed`；BL-00075 候選①）：無基準檔、目標態＝凍結 seed。寫面逐字釘——清列句同基準檔
        模式之五表；清理面五表之序列 setval **只有** sys_ip_rule_id_seq 一支、值自 seed 之 setval 行現讀（樁取 7,true 非預設值；
        角色／選單域四支序列屬 ③b、另案釘）；
        runtime-append 四支序列不復位（走完仍是髒值）而收尾比對照樣 rc 0（只比存在性）。★清理面之外不入 seed
        模式判準（無基準檔可比；該面之 pg 殘留由 tools/schema-gate.py check 之 gate2 逐列兜）。"""
        stub = _restore_stub()
        self._dirty(stub)
        stub.tables["sys_user"] = 4                 # 清理面之外：seed 模式不判
        rc, text = self._restore_seed(stub)
        self.assertEqual(rc, RC_OK, msg=text)
        sqls = [a[-1] for a in stub.log if "psql" in a]
        self.assertEqual([s for s in sqls if _pg_write_offenders([s])], [
            "BEGIN; "
            "UPDATE system_settings SET updated_at = NULL, updated_by = NULL "
            "WHERE updated_at IS NOT NULL OR updated_by IS NOT NULL; "
            "DELETE FROM session_event; DELETE FROM sys_token; DELETE FROM sys_login_attempt; "
            "DELETE FROM sys_ip_rule; DELETE FROM sys_operation_log; "
            "UPDATE sys_user SET session_id = NULL WHERE session_id IS NOT NULL; "
            "SELECT setval('sys_ip_rule_id_seq', 7, true); "
            + ROLE_MENU_SURFACE_AT_SEED +
            "COMMIT;"])
        redis_cmds = [a[-1] for a in stub.log if "sh" in a]
        self.assertEqual(_redis_write_offenders(redis_cmds), [
            f"{REDIS_CLI} PUBLISH {IPGATE_CHANNEL} {IPGATE_DOORBELL_PAYLOAD}",   # ★門鈴排在 DEL 之前（L1-1）
            f"{REDIS_CLI} DEL session:denylist:sid-b session:sid-a:last_activity "
            "'throttle:unlock:user:走查 探針'"])
        self.assertEqual([stub.tables[t] for t in FIVE_TABLES], [0] * 5)
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

    def test_seed_mode_preconditions_refuse_before_any_write(self):
        """seed 模式之安全帶語意沿用（目標態換成凍結 seed）：①seed 於清理面任一表有列＝DELETE 全表會毀掉 seed 資料
        ②seed 缺清理面之 COPY 段或 setval 行 ③演進帳有 system_settings 或清理面五表之 seed_* 登記（凍結段已非期望
        seed）——皆 rc 2、零 docker 呼叫；④system_settings 值≠seed＝fail-loud 指名、只讀過 settings 一句、零寫入。"""
        rowed = SEED_RESTORE_TEXT.replace(
            "COPY public.sys_ip_rule (id, created_at) FROM stdin;\n",
            "COPY public.sys_ip_rule (id, created_at) FROM stdin;\n1\t2026-08-05 00:00:00+00\n")
        self.assertNotEqual(rowed, SEED_RESTORE_TEXT)
        for text, needles in (
                (rowed, ("凍結 seed 之清理面非空", "sys_ip_rule 1 列", "seed 模式只服務", "零寫入")),
                (SEED_RESTORE_TEXT.replace("COPY public.sys_operation_log ", "COPY public.other_log "),
                 ("凍結 seed 缺 restore 清理面", "sys_operation_log")),
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
        other = _ledger_entry("E-001", "seed_update", "sys_user",
                              {"pk": {"id": 3}, "set": {"nick_name": "User01"}})
        for eid, table in (("E-002", "sys_ip_rule"), ("E-003", "system_settings")):
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
        """main 之 `restore --seed` 走預設左源＝真 repo 凍結 seed＋真 repo 演進登記檔、零基準檔引數；setval 值＝該檔
        sys_ip_rule_id_seq 之 setval 行現值（本案以獨立 regex 自真檔另讀一次對賬、不寫死數字）。"""
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh:
            real_text = fh.read()
        m = re.search(r"setval\('public\.sys_ip_rule_id_seq', (\d+), (true|false)\)", real_text)
        self.assertIsNotNone(m)
        stub = _restore_stub(settings=[{"setting_key": k, "setting_value": v, "stamped": False}
                                       for k, v in sorted(seed_settings(real_text).items())])
        self._dirty(stub)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = main([PROG, "restore", "--seed", "--user", "u9", "--db", "d9"], run=stub)
        self.assertEqual(rc, RC_OK, msg=err.getvalue())
        writes = [a[-1] for a in stub.log if "psql" in a and _pg_write_offenders([a[-1]])]
        self.assertEqual(len(writes), 1)
        # 角色／選單域四支序列（③b）亦自真檔 setval 行現讀：本案以獨立 regex 逐支另讀一次對賬（序列名手寫）
        want = [f"SELECT setval('sys_ip_rule_id_seq', {m.group(1)}, {m.group(2)});"]
        for s in ("sys_role_id_seq", "sys_menu_id_seq", "casbin_rule_id_seq", "sys_casbin_policy_archive_id_seq"):
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
        """main 走預設左源＝真 repo 凍結 seed＋真 repo 演進登記檔——演進帳登記 system_settings 之 seed_* 後本案即紅
        （rc 2、訊息指名登記 id）。★觸發面只有本檔 staged 時之 pre-commit 自測與 bash tools/bootstrap.sh 名冊：只登記演進帳之
        commit 不跑本案，首撞點可能延到走查當下 restore rc 2（前置斷言在任何寫入之前、零寫入）。"""
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh:
            real = seed_settings(fh.read())
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
        """③b 寫面逐字＋次序（T088②）：接在清理面 setval 之後、同一交易；指派鍵集差刪除先於四表（role_id 外鍵 RESTRICT）、
        四表刪 `id >` 上界、四支 setval 值自基準檔現讀；四表與指派表皆無 DELETE 全表形；走完各面回基準、收尾 diff rc 0。"""
        stub = _restore_stub()
        path = self._baseline(stub)
        self._dirty(stub)
        self._dirty_role_menu(stub)
        rc, text = self._restore(path, stub)
        self.assertEqual(rc, RC_OK, msg=text)
        tx = self._tx(stub)
        self.assertTrue(tx.endswith("SELECT setval('sys_operation_log_id_seq', 1, false); "
                                    + ROLE_MENU_SURFACE_AT_SEED + "COMMIT;"), msg=tx)
        order = [tx.index(s) for s in ("DELETE FROM sys_user_role WHERE", "DELETE FROM sys_role WHERE",
                                       "DELETE FROM sys_menu WHERE", "DELETE FROM casbin_rule WHERE",
                                       "DELETE FROM sys_casbin_policy_archive WHERE",
                                       "SELECT setval('sys_role_id_seq'")]
        self.assertEqual(order, sorted(order), msg=order)
        for t in ("sys_role", "sys_menu", "casbin_rule", "sys_casbin_policy_archive", "sys_user_role"):
            self.assertNotIn(f"DELETE FROM {t};", tx)
        self.assertEqual(stub.ids, {t: list(v) for t, v in STUB_BOUNDED_IDS.items()})
        self.assertEqual(sorted(stub.user_roles), list(STUB_USER_ROLES))
        self.assertEqual({t: stub.tables[t] for t in ROLE_MENU_TABLES},
                         {t: RESTORE_FAKE_TABLES[t] for t in ROLE_MENU_TABLES})
        self.assertEqual(stub.seqs, RESTORE_FAKE_SEQS)
        self.assertIn("restore ③b", text)
        self.assertIn("✓ 全等", text)

    def test_role_menu_bounds_keys_and_setvals_are_read_from_the_baseline_and_empty_key_set_form(self):
        """上界、鍵集與 setval 值皆自基準檔現讀（樁取非 seed 值）；空鍵集＝`DELETE FROM sys_user_role;`（目標為空表＝全清即正解）；
        archive 上界非 0 時照刪 `id >` 上界（不因 seed 零列而改 DELETE 全表形）。"""
        ids = {"sys_role": (1, 2, 3, 9), "sys_menu": (1, 2), "casbin_rule": (5,), "sys_casbin_policy_archive": (7,)}
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
            "SELECT setval('sys_role_id_seq', 12, true); SELECT setval('sys_menu_id_seq', 2, true); "
            "SELECT setval('casbin_rule_id_seq', 5, true); SELECT setval('sys_casbin_policy_archive_id_seq', 7, true); "
            "COMMIT;"), msg=self._tx(stub))
        seqs = {s: {"last_value": 1, "is_called": False} for s in BOUNDED_TABLES.values()}
        self.assertEqual(seed_surface_sql(_snap(user_role_keys=[], sequences=seqs))[0], "DELETE FROM sys_user_role;")
        self.assertEqual(seed_surface_sql(_snap(user_role_keys=[[3, 1], [1, 2]], sequences=seqs))[0],
                         "DELETE FROM sys_user_role WHERE (user_id, role_id) NOT IN (VALUES (1, 2), (3, 1));")

    def test_safety_belt_does_not_refuse_role_menu_tables_that_have_rows(self):
        """安全帶「列數非 0 即拒」只套清理面五表：基準檔四表／指派表有列（含 archive 2 列）與凍結 seed 之該面 COPY 有列
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
        """★③b 前置（基準檔模式）：基準檔四表任一之 id 上界高於其序列位置（is_called 真＝last_value、假＝last_value-1＝nextval
        已發出之最大值）＝取樣時已有顯式 id 殘列越過序列——照跑則走查以 nextval 造之列落在序列與上界之間、`id >` 上界刪不到，
        序列卻被 setval 回其下＝下一次 nextval 撞 PK。四表逐一（殘列取號段形大 id）：snapshot rc 0 照寫、stderr 告警指名；
        走查後 restore rc 2 指名、零 docker 呼叫＝零寫入；補救句所指之 `restore --seed` 實跑可收（殘列與走查列一併刪、四支序列
        回 seed 值、rc 0）。另釘 is_called 假之邊界（上界 1 對 (1,f)＝nextval 下一值恰為既存之 1）同拒；上界＝序列位置（seed 形）
        不告警；seed 模式同判準、對象＝凍結 seed（setval 低於 COPY 列 id 最大值＝凍結面受損 rc 2、補救不指回自己、零 docker 呼叫）。
        表名與序列名手寫。"""
        big = 9_300_000_001
        seed_ids = {t: list(v) for t, v in STUB_BOUNDED_IDS.items()}
        seed_seqs = {"sys_role_id_seq": (3, "t"), "sys_menu_id_seq": (78, "t"), "casbin_rule_id_seq": (163, "t"),
                     "sys_casbin_policy_archive_id_seq": (1, "f")}

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
                                ("sys_casbin_policy_archive", "sys_casbin_policy_archive_id_seq", (big,))):
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
        for needle in ("凍結 seed 之角色／選單域上界高於其序列位置", "sys_menu 上界 78", "凍結面受損", "零寫入"):
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
                         "[walkthrough-baseline] ★MUST 重啟 rust-api：本次 restore 以 SQL 直改 casbin_rule（刪列或改序列）、"
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
        9,true≠上界 3，證兩值各自現讀）、指派鍵集＝seed COPY 鍵集；寫面逐字；走完四表回 seed 形、收尾 rc 0。"""
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
            + ROLE_MENU_SURFACE_AT_SEED.replace("setval('sys_role_id_seq', 3, true)", "setval('sys_role_id_seq', 9, true)")
            + "COMMIT;"), msg=self._tx(stub))
        self.assertEqual(stub.ids, {t: list(v) for t, v in STUB_BOUNDED_IDS.items()})
        self.assertEqual(sorted(stub.user_roles), list(STUB_USER_ROLES))
        self.assertEqual(stub.seqs["sys_role_id_seq"], (9, "t"))
        self.assertIn(CASBIN_RESTART_HINT, out)
        # 收尾判準面含該面：seed 列被硬刪（restore 只刪不補）＝rc 1 指名
        stub = _restore_stub()
        stub.ids["sys_menu"].remove(5)
        stub.tables["sys_menu"] -= 1
        stub.user_roles.remove((2, 2))
        stub.tables["sys_user_role"] -= 1
        rc, out = self._restore_seed(stub)
        self.assertEqual(rc, RC_DIFF, msg=out)
        self.assertIn("表｜sys_menu｜78｜77｜-1", out)
        self.assertIn("鍵集｜sys_user_role(2,2)｜有｜（無）｜-1", out)

    def test_seed_target_parses_role_menu_copy_segments_and_refuses_damage(self):
        """凍結 seed 之角色／選單域五段解析（樁＋真檔皆 3／78／163／0 列、指派 3 對）；段首缺 id 欄／id 非整數／指派列欄數不符
        ＝凍結面受損 rc 2；缺 COPY 段或 setval 行＝指名清理面缺席；皆零 docker 呼叫。"""
        want_bounds = {"sys_role": 3, "sys_menu": 78, "casbin_rule": 163, "sys_casbin_policy_archive": 0}
        want_seqs = {"sys_role_id_seq": {"last_value": 3, "is_called": True},
                     "sys_menu_id_seq": {"last_value": 78, "is_called": True},
                     "casbin_rule_id_seq": {"last_value": 163, "is_called": True},
                     "sys_casbin_policy_archive_id_seq": {"last_value": 1, "is_called": False}}
        with open(os.path.join(REPO_ROOT, SEED_FIXTURE), encoding="utf-8") as fh:
            real_text = fh.read()
        for text in (SEED_RESTORE_TEXT, real_text):
            target = seed_restore_target(text)
            self.assertEqual(target["id_bounds"], want_bounds)
            self.assertEqual(target["user_role_keys"], [[1, 1], [2, 2], [3, 3]])
            self.assertEqual({t: target["tables"][t] for t in ROLE_MENU_TABLES},
                             {"sys_role": 3, "sys_menu": 78, "casbin_rule": 163, "sys_casbin_policy_archive": 0,
                              "sys_user_role": 3})
            self.assertEqual({s: target["sequences"][s] for s in want_seqs}, want_seqs)
        for bad, needle in (
                (SEED_RESTORE_TEXT.replace("COPY public.sys_role (id, ", "COPY public.sys_role (rid, "), "sys_role"),
                (SEED_RESTORE_TEXT.replace("\n2\t2026-08-05 00:00:00+00\tR_2\n", "\nx\t2026-08-05 00:00:00+00\tR_2\n"),
                 "sys_role"),
                (SEED_RESTORE_TEXT.replace("\n2\t2\n3\t3\n", "\n2\t2\t9\n3\t3\n"), "sys_user_role")):
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

    def test_seed_mode_evolution_entries_on_role_menu_tables_refuse_by_id(self):
        """seed 模式演進帳拒跑判定擴及角色／選單域五表（有其 seed_* 登記＝凍結段非期望 seed、照刪會毀演進帳定義之 seed 列）：
        逐表指名登記 id、零 docker 呼叫；基準檔模式之目標態＝基準檔、不因此拒跑。"""
        other = _ledger_entry("E-001", "seed_update", "sys_user", {"pk": {"id": 3}, "set": {"nick_name": "User01"}})
        for eid, table in (("E-002", "sys_role"), ("E-003", "sys_menu"), ("E-004", "casbin_rule"),
                           ("E-005", "sys_casbin_policy_archive"), ("E-006", "sys_user_role")):
            self._write_ledger(other, _ledger_entry(eid, "seed_add", table, {"pk": ["id"], "values": {"id": 999}}))
            stub = _restore_stub()
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(BaselineError) as ctx:
                self._restore_seed(stub)
            for needle in (eid, table, "先擴充本工具", "零寫入"):
                self.assertIn(needle, str(ctx.exception), msg=table)
            self.assertNotIn("E-001", str(ctx.exception), msg=table)
            self.assertEqual(stub.log, [], msg=table)
            stub = _restore_stub()
            path = self._baseline(stub)
            rc, text = self._restore(path, stub)
            self.assertEqual(rc, RC_OK, msg=(table, text))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
