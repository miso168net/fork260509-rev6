#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/walkthrough-baseline.py — CDP 真登入走查前後的全表基準對賬（rev5:B-147；rev5:L-071 防法①的機制化）

子命令：
  snapshot <檔>   取 rev6 dev stack 實庫＋redis 現況三面、寫成 JSON 基準檔（走查**前**跑）
  diff <檔>       重取現況、與基準檔逐值比對、只列有差者＋末行摘要（走查**後**清理完跑；
                  ★rc 0 才算「環境已還原」——三閘綠不算，rev5:L-055／rev5:L-071 招牌徵狀＝三閘綠而全量紅）
  restore <檔>    走查後清理（RUNBOOK §9c 第 3 步之順序機器化；寫面恰為下列、次序固定）：
                  ①system_settings 對凍結 seed（specs/001-schema-baseline/fixtures/seed.sql 之 COPY 段）——值≠seed
                    （含鍵缺／鍵多）即 fail-loud 指名、**不自動改值**（值還原走 002 刀寫端＝人工前置）；值＝seed 而
                    審計欄 updated_at／updated_by 非 NULL 者歸 NULL（改回值≠改回痕）；★左源未合成演進帳——
                    docs/ops/reference-src/schema-evolution.json 有 system_settings 之 seed_* 登記即拒跑、指名登記 id
                    （凍結段已非期望 seed；先擴充本工具）
                  ②DELETE session_event／sys_token／sys_login_attempt 全表＋sys_user.session_id 歸 NULL
                  ③三支 setval（sys_token_id_seq／session_event_id_seq／sys_login_attempt_id_seq）值自基準檔現讀
                    ——①～③ 同一交易（BEGIN…COMMIT、ON_ERROR_STOP=1；任一句敗即整筆回滾、不進④）
                  ④redis 以 `--scan --pattern` 取 session:*／throttle:* 鍵、逐鍵指名 DEL（每批 ≤REDIS_DEL_BATCH
                    把；絕不 FLUSHDB、絕不以樣式刪）
                  ⑤收尾自動跑一次 diff、其 rc 即 restore 之 rc（0＝已還原）
                  ★安全帶：基準檔三表列數或 session／throttle 前綴鍵數非 0＝拒絕執行 rc 2、零寫入（DELETE 全表
                    會毀掉基準資料——restore 只服務「走查前為空基準」之形）；安全帶與 seed 比對皆在任何寫入之前
  test            自帶 self-test（unittest、離線、零 docker；subprocess 全樁）
  選項（snapshot／diff／restore 共用）：`--user U`／`--db D`（預設同 tools/schema-gate.py 常數）。
  `<檔>` 為必填位置引數、無隱含預設落點（契約用法落 tmp/、見 RUNBOOK §9c）。

三面（★全部現算、零手抄名冊——清單式防法已被 rev5:L-071 證偽：rev5:006 的清單擋不住 rev5:007 的組合）：
  ①表：public schema **全部**表的列數（表清單自 information_schema.tables 現算、逐表 count(*)
    以單一 UNION ALL 一次撈；含 seaql_migrations——它也是一張表、不豁免）
  ②序列：public schema **全部**序列的 last_value＋is_called（清單自 pg_class relkind='S' 現算）
  ③redis：DBSIZE 總數＋逐前綴鍵數（`--scan` 全鍵**去重後**分組——SCAN 只保證「至少一次」；
    DBSIZE 與去重鍵數互證、不等出提示；前綴＝鍵第一個冒號前段、無冒號者歸「(無前綴)」；
    前綴名冊亦不手抄——rust-api 現行 session:／throttle: 兩前綴只是今天的值）
  基準檔另帶 taken_at（UTC ISO）與 schema_version（檔形演進用）；diff 忽略 taken_at。

退出碼：0 全等／1 有差／2 環境或結構異常（docker 不可執行、psql／redis 失敗、基準檔缺席或壞形、
★比對面為空＝零表或零序列——空面的全綠是假綠、同 schema-gate 紀律，snapshot 與 diff 皆然；restore 另含
安全帶拒跑、基準檔缺清理面之表或序列、seed 左源缺席或不可解、演進登記檔缺席或壞形、system_settings 有 seed_*
演進登記、system_settings 值≠seed）／
64 用法錯（usage 走 stderr）。restore 之 0／1 即其收尾 diff 之 rc。

唯讀紀律（self-test 逐字釘住）：snapshot／diff 唯讀——pg 只下 SELECT（含目錄視圖）、redis 只下 DBSIZE／--scan；
restore 之寫面恰為上列①～④（交易句逐字、redis 只 DEL 指名鍵），其餘撈取同唯讀判準；
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
清理腳本；寫面由 self-test 逐字釘住（多一句即紅）。
"""
import contextlib
import datetime
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
SCHEMA_VERSION = 1       # 基準檔形版本；改檔形即 bump、舊檔 diff 走 rc 2 而非誤比
NO_PREFIX = "(無前綴)"
STARTUP_HINT = ("docker compose -f docker-compose.yml -f docker-compose.dev.yml "
                "up -d --wait postgres redis")

RC_OK, RC_DIFF, RC_ENV, RC_USAGE = 0, 1, 2, 64
PROG = "tools/walkthrough-baseline.py"

SQL_TABLES = ("SELECT table_name FROM information_schema.tables "
              "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY 1")
SQL_SEQUENCES = ("SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                 "WHERE c.relkind='S' AND n.nspname='public' ORDER BY 1")

# ── restore 清理面（BL-00053；次序＝RUNBOOK §9c 第 3 步）──────────────────────────
# seed 左源＝凍結 fixture 之 system_settings COPY 段（唯讀、REPO_ROOT 相對）
SEED_FIXTURE = os.path.join("specs", "001-schema-baseline", "fixtures", "seed.sql")
# 演進登記檔（形斷言權威＝tools/schema-gate.py）：期望 seed＝凍結 ⊕ 演進；本工具左源只讀凍結段、未合成演進，
# 故帳上有 system_settings 之 seed 面登記即拒跑（check_settings_seed_evolution）
SCHEMA_EVOLUTION = os.path.join("docs", "ops", "reference-src", "schema-evolution.json")
SEED_EVOLUTION_KINDS = ("seed_add", "seed_update", "seed_delete")
RESTORE_TABLES = ("session_event", "sys_token", "sys_login_attempt")        # DELETE 全表；次序即語句序
RESTORE_SEQUENCES = ("sys_token_id_seq", "session_event_id_seq", "sys_login_attempt_id_seq")
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
    """跑一個 redis 讀命令 → stdout 原文；非零＝rc 2。"""
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


def snapshot_live(user=DB_USER, db=DB_NAME, run=subprocess.run, now=None):
    """三面現算 → 基準 dict（含 taken_at UTC ISO＋schema_version）。"""
    taken = now or datetime.datetime.now(datetime.timezone.utc)
    return {
        "schema_version": SCHEMA_VERSION,
        "taken_at": taken.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tables": fetch_tables(user, db, run),
        "sequences": fetch_sequences(user, db, run),
        "redis": fetch_redis(run),
    }


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
    """逐值比對 → 差異列（dict：face／name／base／live／delta）；只列有差者、忽略 taken_at。"""
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
    for name in sorted(set(base["sequences"]) | set(live["sequences"])):
        b, l = base["sequences"].get(name), live["sequences"].get(name)
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
    n = {face: sum(1 for r in rows if r["face"] == face) for face in ("表", "序列", "redis")}
    lines.append(f"[walkthrough-baseline] 摘要：表 {n['表']} 項差／序列 {n['序列']} 項差／"
                 f"redis {n['redis']} 項差（比對面：表 {t}／序列 {s}／redis {k} 鍵、{p} 前綴）")
    return lines


# ── 子命令 ──────────────────────────────────────────────────────────────────

def cmd_snapshot(path, user, db, run=subprocess.run):
    snap = snapshot_live(user, db, run)
    dump_snapshot(snap, path)
    t, s, k, p = _face_counts(snap)
    _say(f"[walkthrough-baseline] ✓ 基準已寫：{path}（表 {t}／序列 {s}／redis {k} 鍵、{p} 前綴；"
         f"taken_at {snap['taken_at']}）")
    return RC_OK


def cmd_diff(path, user, db, run=subprocess.run):
    base = load_snapshot(path)
    # 現況**不**再過 validate_snapshot：它檢查的每一項在這條路徑上都是恆真（schema_version 由
    # snapshot_live 自己塞、零表零序列已由 fetch_* fail-loud、值型別由 int()／建構過程保證），
    # 沒有任何輸入能讓它拒絕——讀起來像第二道防線、實際是空轉（變異測試殺不死）。真正的守門
    # 在 fetch_tables／fetch_sequences／fetch_redis 各自的 fail-loud，放寬那裡就是真的沒有兜底。
    live = snapshot_live(user, db, run)
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


def seed_settings(seed_text):
    """凍結 seed.sql 之 `COPY public.system_settings` 段 → {setting_key: setting_value}。
    段缺席／零列＝比對面為空、段首缺鍵或值欄／列欄數不符＝凍結面受損，皆 BaselineError（rc 2）。"""
    lines = seed_text.splitlines()
    for i, ln in enumerate(lines):
        m = re.match(r"^COPY public\.system_settings \(([^)]*)\) FROM stdin;$", ln)
        if not m:
            continue
        cols = [c.strip().strip('"') for c in m.group(1).split(",")]
        if "setting_key" not in cols or "setting_value" not in cols:
            raise BaselineError(f"seed system_settings 段首缺 setting_key／setting_value 欄：{cols}")
        ki, vi = cols.index("setting_key"), cols.index("setting_value")
        got = {}
        for row in lines[i + 1:]:
            if row == "\\.":
                break
            vals = row.split("\t")
            if len(vals) != len(cols):
                raise BaselineError(f"seed system_settings 列欄數 {len(vals)} ≠ 段首 {len(cols)}："
                                    f"{row[:80]!r}——凍結面受損")
            got[_copy_unescape(vals[ki])] = _copy_unescape(vals[vi])
        if not got:
            raise BaselineError("seed system_settings 段零列——比對面為空、不得靜默判綠")
        return got
    raise BaselineError("seed 缺 COPY public.system_settings 段——比對面為空、不得靜默判綠")


def check_settings_seed_evolution(ledger_path):
    """演進帳有 system_settings 之 seed_* 登記＝凍結 COPY 段已非期望 seed（期望＝凍結 ⊕ 演進、同 tools/schema-gate.py
    gate2 之 apply_seed_entries）。本工具左源未合成演進——照比會把 migration 定義的合法值誤報為值≠seed、並給出
    「以寫端改回」的錯誤補救——故拒跑 rc 2、指名登記 id。結構性 kind（add_column 等）不擋：不改 setting_key／
    setting_value 鍵值集。登記檔缺席／非 JSON／entries 非 list 或含非物件項＝rc 2（形之完整斷言權威在 schema-gate、
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
                            "——形＝specs/001-schema-baseline/contracts/schema-evolution.md §2")
    hits = [f"{e.get('id', '?')}（{e.get('kind')}）" for e in entries
            if e.get("table") == "system_settings" and e.get("kind") in SEED_EVOLUTION_KINDS]
    if hits:
        raise BaselineError(f"{SCHEMA_EVOLUTION} 有 system_settings 之 seed 演進登記：{'、'.join(hits)}——restore 之 "
                            "seed 左源只讀凍結 COPY 段、未合成演進（期望 seed＝凍結 ⊕ 演進），照比會把合法值誤報為值≠seed；"
                            "先擴充本工具之 seed 左源合成、再跑 restore；拒絕執行、零寫入")


def check_restore_baseline(snap):
    """安全帶：清理面之表或序列不在基準檔＝結構異常；三表列數或 session／throttle 前綴鍵數非 0＝拒跑。
    restore 只服務「走查前為空基準」之形——DELETE 全表對非空基準會連基準資料一起毀掉、diff 還報不出來。"""
    absent = [t for t in RESTORE_TABLES if t not in snap["tables"]] + \
             [s for s in RESTORE_SEQUENCES if s not in snap["sequences"]]
    if absent:
        raise BaselineError(f"基準檔缺 restore 清理面：{'、'.join(absent)}——庫錯或基準檔非本 schema 所取")
    loaded = [f"{t} {snap['tables'][t]} 列" for t in RESTORE_TABLES if snap["tables"][t]] + \
             [f"{p} 前綴 {snap['redis']['prefixes'][p]} 鍵" for p in RESTORE_REDIS_PREFIXES
              if snap["redis"]["prefixes"].get(p)]
    if loaded:
        raise BaselineError("基準非空、DELETE 全表會毀掉基準資料（" + "、".join(loaded) +
                            "）——restore 只服務走查前為空基準之形；拒絕執行、零寫入。補救：手上有取於空基準之較早 "
                            "snapshot 檔＝改以該檔跑 restore；無此檔＝本工具不承載，殘列須人工清至空基準後重取 snapshot")


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


def restore_sql(snap):
    """②③ 單交易寫句：審計欄歸 NULL → 三表 DELETE＋session_id 歸 NULL → 三支 setval（值自基準檔現讀）。"""
    seqs = snap["sequences"]
    setvals = tuple(f"SELECT setval('{n}', {seqs[n]['last_value']}, "
                    f"{'true' if seqs[n]['is_called'] else 'false'});" for n in RESTORE_SEQUENCES)
    return " ".join(("BEGIN;", SQL_RESTORE_AUDIT) + SQL_RESTORE_CLEAR + setvals + ("COMMIT;",))


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
                                "補救：確認 redis 容器可用後重跑同一 restore（冪等：pg 面已空、只剩前綴鍵待清）") from None
    return found, deleted


def cmd_restore(path, user, db, run=subprocess.run, seed_path=None, ledger_path=None):
    base = load_snapshot(path)
    check_restore_baseline(base)
    check_settings_seed_evolution(ledger_path or os.path.join(REPO_ROOT, SCHEMA_EVOLUTION))
    seed_path = seed_path or os.path.join(REPO_ROOT, SEED_FIXTURE)
    try:
        with open(seed_path, encoding="utf-8") as fh:
            seed = seed_settings(fh.read())
    except OSError as ex:
        raise BaselineError(f"seed 左源讀取失敗：{seed_path}：{ex}") from None
    stamped = check_settings_against_seed(psql_json(SQL_SETTINGS, user, db, run), seed)
    _say(f"[walkthrough-baseline] restore ①system_settings：{len(seed)} 鍵值＝seed；"
         f"審計欄非 NULL {stamped} 列（交易內歸 NULL）")
    r = _run_docker(psql_argv(restore_sql(base), user, db), run)
    if r.returncode != 0:
        raise BaselineError(f"restore 交易失敗（rc={r.returncode}、整筆回滾、未動 redis）："
                            f"{(r.stderr or '').strip()[:300]}"
                            "；補救：依上列 psql 錯誤修正（常見＝postgres 容器未起）後重跑同一 restore（交易已回滾、可安全重跑）")
    seqs = "、".join(f"{n}（{_seq_text(base['sequences'][n])}）" for n in RESTORE_SEQUENCES)
    _say(f"[walkthrough-baseline] restore ②③pg 單交易已提交：DELETE {'／'.join(RESTORE_TABLES)}＋"
         f"sys_user.session_id 歸 NULL＋setval（{seqs}）")
    found, deleted = redis_clear_prefixes(run)
    counts = "／".join(f"{p} 前綴 {n} 鍵" for p, n in found.items())
    _say(f"[walkthrough-baseline] restore ④redis：{counts}、DEL 回報 {deleted} 鍵（逐鍵指名）")
    _say("[walkthrough-baseline] restore ⑤收尾 diff（其 rc 即 restore 之 rc；0＝已還原）：")
    return cmd_diff(path, user, db, run)


def usage(msg=None):
    if msg:
        _say(f"[walkthrough-baseline] 用法錯：{msg}", err=True)
    _say(f"用法：python3 {PROG} snapshot <檔> [--user U] [--db D]\n"
         f"      python3 {PROG} diff <檔> [--user U] [--db D]\n"
         f"      python3 {PROG} restore <檔> [--user U] [--db D]\n"
         f"      python3 {PROG} test\n"
         f"  snapshot＝走查前取三面基準寫 JSON；diff＝走查後重取現況逐值比對（rc 0 才算環境已還原）；"
         f"restore＝走查後清理（安全帶：基準須為空）＋收尾 diff（rc 即 diff 之 rc）；"
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
                 "目錄 SQL 與 count 腿抗窄化、密碼不出 argv、print 全 flush；restore 寫面逐字＋次序、"
                 "setval 自基準現讀、安全帶拒跑零呼叫、清理面缺席、settings 值≠seed 零寫入、收尾 diff rc、"
                 "失敗即停、DEL 分批、seed 解析與空面、演進帳 system_settings seed 登記拒跑／他表與結構性登記不擋／"
                 "登記檔缺席壞形、預設 seed 與演進帳哨兵與 --user／--db）")
            return RC_OK
        return RC_DIFF
    if cmd in ("snapshot", "diff", "restore"):
        if len(argv) < 3 or argv[2].startswith("--"):
            return usage(f"{cmd} 需要 <檔> 位置引數（無隱含預設落點）")
        opts, err = _parse_opts(argv[3:])
        if err:
            return usage(err)
        user, db = opts
        try:
            if cmd == "snapshot":
                return cmd_snapshot(argv[2], user, db, run)
            if cmd == "restore":
                return cmd_restore(argv[2], user, db, run)
            return cmd_diff(argv[2], user, db, run)
        except BaselineError as ex:
            _say(f"[walkthrough-baseline] ✗ 環境或結構異常：{ex}", err=True)
            return RC_ENV
    return usage(f"未知子命令：{cmd}")


# ── self-test（離線、subprocess 全樁、零 docker）──────────────────────────────

FAKE_TABLES = {"sys_user": 3, "sys_token": 0, "seaql_migrations": 7}
FAKE_SEQS = {"sys_user_id_seq": (3, "t"), "sys_token_id_seq": (1, "f")}
FAKE_KEYS = ["session:sid-a:last_activity", "session:denylist:sid-b", "throttle:lock:user:x",
             "plainkey"]


def _completed(argv, rc, stdout="", stderr=""):
    return subprocess.CompletedProcess(argv, rc, stdout, stderr)


class _StubRun:
    """樁 subprocess.run：依 argv 分流 psql（依 SQL 內容）／redis（依命令）；記錄每次 argv。
    restore 路徑另模擬寫面：交易句依其 DELETE／setval／審計 UPDATE 改樁內狀態、DEL 刪樁內鍵——
    收尾 diff 因此對著「被 restore 改過的樁」算，rc 0／1 皆真實走過。"""

    def __init__(self, tables=None, seqs=None, keys=None, dbsize=None, fail=None, garble=None,
                 truncate=None, settings=None):
        self.tables = dict(FAKE_TABLES if tables is None else tables)
        self.seqs = dict(FAKE_SEQS if seqs is None else seqs)
        self.keys = list(FAKE_KEYS if keys is None else keys)
        self._dbsize = dbsize       # None＝隨現存鍵數（DEL 後同步變小）
        self.settings = [dict(s) for s in (settings or [])]
        self.fail = fail            # "psql"／"redis"＝該支非零退出；"tx"＝交易句失敗；"del"＝DEL 回非整數
        self.garble = garble        # "tables"／"seqs"／"settings"＝該面回不可解輸出（缺欄／非整數／非 JSON）
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
                for name, v, called in re.findall(r"setval\('(\w+)', (\d+), (true|false)\)", sql):
                    self.seqs[name] = (int(v), "t" if called == "true" else "f")
                if sql.count("UPDATE system_settings SET updated_at = NULL, updated_by = NULL"):
                    for s in self.settings:
                        s["stamped"] = False
                return _completed(argv, 0, "COMMIT\n", "")
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
            "redis": {"dbsize": 2, "prefixes": {"session": 2}}}
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
        got = group_prefixes(["session:a:b", "session:c", "throttle:lock:user:x", "plain",
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
                     [PROG, "restore", "f.json", "--bogus"]):
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
        self.assertEqual(len(sqls), 4)                   # 表清單／表列數／序列清單／序列值
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
        self.assertEqual((len(diff_sqls), len(diff_redis)), (4, 2))
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
                       "system_settings": 2, "seaql_migrations": 7}
RESTORE_FAKE_SEQS = {"sys_user_id_seq": (3, "t"), "sys_token_id_seq": (1, "f"),
                     "session_event_id_seq": (1, "f"), "sys_login_attempt_id_seq": (1, "f")}
SEED_SETTINGS_TEXT = (
    "--\n-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: soybean\n--\n\n"
    "COPY public.system_settings (setting_key, created_at, updated_at, updated_by, setting_type, "
    "setting_value, description) FROM stdin;\n"
    "session_idle_timeout\t2026-08-05 00:00:00+00\t\\N\t\\N\tnumber\t60\t閒置逾時\n"
    "single_session_default\t2026-08-05 00:00:00+00\t\\N\t\\N\tenum:on,off\toff\t全站單一-session 預設\n"
    "\\.\n")


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
    """合成演進登記項（欄位齊同 specs/001-schema-baseline/contracts/schema-evolution.md §2）。"""
    return {"id": eid, "knife": "001-schema-baseline", "kind": kind, "table": table,
            "detail": detail, "date": "2026-09-14"}


class TestRestore(unittest.TestCase):
    """restore 五步：安全帶（基準須為空）→system_settings 對 seed（值不等 fail-loud、不改值）→pg 單交易
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

    @staticmethod
    def _dirty(stub):
        """模擬走查殘留：三表列＋序列推進＋session／throttle 鍵（含須引號的鍵名）＋審計欄被寫。"""
        stub.tables.update(sys_token=2, session_event=3, sys_login_attempt=1)
        stub.seqs.update(sys_token_id_seq=(33, "t"), session_event_id_seq=(4, "t"),
                         sys_login_attempt_id_seq=(9, "t"))
        stub.keys += ["session:sid-a:last_activity", "throttle:lock:user:走查 探針",
                      "session:denylist:sid-b"]
        stub.settings[1]["stamped"] = True

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
            "UPDATE sys_user SET session_id = NULL WHERE session_id IS NOT NULL; "
            "SELECT setval('sys_token_id_seq', 5, true); "
            "SELECT setval('session_event_id_seq', 1, false); "
            "SELECT setval('sys_login_attempt_id_seq', 1, false); "
            "COMMIT;"])
        redis_cmds = [a[-1] for a in stub.log if "sh" in a]
        self.assertEqual(_redis_write_offenders(redis_cmds), [
            f"{REDIS_CLI} DEL session:denylist:sid-b session:sid-a:last_activity "
            "'throttle:lock:user:走查 探針'"])
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
                                "sys_login_attempt_id_seq": {"last_value": 7, "is_called": True}},
                     redis={"dbsize": 0, "prefixes": {}})
        sql = restore_sql(snap)
        self.assertTrue(sql.endswith("SELECT setval('sys_token_id_seq', 9, true); "
                                     "SELECT setval('session_event_id_seq', 8, false); "
                                     "SELECT setval('sys_login_attempt_id_seq', 7, true); COMMIT;"),
                        msg=sql)
        self.assertEqual(sql.count("setval("), 3)

    def test_nonempty_baseline_refuses_rc2_before_any_docker_call(self):
        """★安全帶：基準檔三表任一列數或 session／throttle 前綴鍵數非 0＝rc 2、零 docker 呼叫＝零寫入。"""
        for over in ({"tables": dict(RESTORE_FAKE_TABLES, sys_token=2)},
                     {"tables": dict(RESTORE_FAKE_TABLES, session_event=1)},
                     {"tables": dict(RESTORE_FAKE_TABLES, sys_login_attempt=4)},
                     {"keys": ["plainkey", "session:sid-x"]},
                     {"keys": ["throttle:lock:ip:203.0.113.9"]}):
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
            self.assertEqual([a[-1] for a in stub.log], [SQL_SETTINGS])

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


if __name__ == "__main__":
    sys.exit(main(sys.argv))
