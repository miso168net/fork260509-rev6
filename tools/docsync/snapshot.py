"""守 RL-0049／RL-0054：快變字面值（schema／帳號）只住實庫快照、真表由 generate 重算；password 欄連雜湊都不入快照。

snapshot.py：refresh 快照管線（需 dev stack postgres）與兩張參考真表的生成器——
六撈 SQL 常數（★SQL_COLUMNS／SQL_INDEXES／SQL_CONSTRAINTS 與 tools/schema-gate.py 三常數位元相等＝gate1 照相面與快照面同構契約，
對賬面＝tests/test_snapshot.py）、psql_fetch（compose exec psql、stack 缺席 fail-loud＋啟動提示）、build_schema_snapshot／build_accounts_snapshot
（白名單投影＋確定性排序）、snapshot_dumps、cmd_refresh（六撈全成功才原子落兩檔、任一失敗零寫入）、gen_reference_schema／gen_reference_accounts
（Ctx 注入、讀 reference-src 三檔；缺檔／壞 JSON／map 缺表或缺 label／綁定懸空＝fail-loud）。
generate／check／lint 只讀快照、絕不碰 docker（承 rev5:docs-sync.py 快照管線、重打字為 package 形）。
"""
import json
import os
import subprocess
import tempfile

from . import ROOT, SCHEMA_SNAPSHOT, ACCOUNTS_SNAPSHOT, ARCHETYPE_MAP
from .common import GENERATED_HEADER

STACK_HINT = "docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait postgres"
REFRESH_HINT = "python3 tools/docsync refresh"
DB_USER = "soybean"
DB_NAME = "soybean_admin_rust"
COMPOSE_PSQL = ["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.dev.yml", "exec", "-T", "postgres"]

# 六撈皆唯讀（information_schema／pg_catalog／SELECT only）、各包 json_agg 回單值 JSON；seaql_migrations（框架帳表）SQL 層即排除、build_* 再濾一次。
# ★下三支與 tools/schema-gate.py 同名常數須位元相等（test_snapshot.TestIsomorphismWithSchemaGate 釘）——改一邊必同步另一邊。
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
# 帳號面三表；sys_user 逐欄點名——絕不 SELECT *（password 欄不得經任何路徑進快照）。
SQL_USERS = _JSON_WRAP.format("SELECT id, user_name, nick_name, status FROM sys_user ORDER BY id")
SQL_ROLES = _JSON_WRAP.format("SELECT id, role_code, role_name, status FROM sys_role ORDER BY id")
SQL_BINDINGS = _JSON_WRAP.format("SELECT user_id, role_id FROM sys_user_role ORDER BY user_id, role_id")

# 白名單投影鍵序＝快照 JSON 鍵序（entity-drift-gate 讀 columns 節同鍵集；schema-gate COL_KEYS／DEF_KEYS 同集）
COLUMN_KEYS = ("table", "column", "ordinal", "type", "nullable", "default")
DEF_KEYS = ("table", "name", "definition")
USER_KEYS = ("id", "user_name", "nick_name", "status")
ROLE_KEYS = ("id", "role_code", "role_name", "status")
BINDING_KEYS = ("user_id", "role_id")
FRAMEWORK_TABLE = "seaql_migrations"


class SnapshotError(Exception):
    """快照管線失敗（stack 不在、撈取列形不符、reference-src 檔缺或壞、歸屬缺、綁定懸空）——fail-loud、絕不寫部分結果。"""


def _project(row, keys, what):
    """逐列投影到白名單鍵集；多鍵／缺鍵／非 object＝fail-loud（多鍵即走私欄——含 password——的紅線）。"""
    if not isinstance(row, dict):
        raise SnapshotError(f"{what} 列須為 object：{row!r}")
    extra, missing = sorted(set(row) - set(keys)), [k for k in keys if k not in row]
    if extra or missing:
        raise SnapshotError(f"{what} 列鍵集不符白名單（多：{extra or '無'}／缺：{missing or '無'}）——refresh 拒寫；撈取 SQL 與白名單須同步改")
    return {k: row[k] for k in keys}


def _app_tables_only(rows):
    return [r for r in rows if not (isinstance(r, dict) and r.get("table") == FRAMEWORK_TABLE)]


def build_schema_snapshot(cols, idx, cons):
    """三撈 → {columns, indexes, constraints}：投影＋確定性排序（columns 依 表名→ordinal；索引／約束依 表名→名稱）；無產生時點欄。"""
    return {
        "columns": sorted((_project(r, COLUMN_KEYS, "columns") for r in _app_tables_only(cols)), key=lambda r: (r["table"], r["ordinal"])),
        "indexes": sorted((_project(r, DEF_KEYS, "indexes") for r in _app_tables_only(idx)), key=lambda r: (r["table"], r["name"])),
        "constraints": sorted((_project(r, DEF_KEYS, "constraints") for r in _app_tables_only(cons)), key=lambda r: (r["table"], r["name"])),
    }


def build_accounts_snapshot(users, roles, bindings):
    """三撈 → {users, roles, bindings}：投影＋確定性排序；sys_user 列帶 password 鍵＝機密紅線、先於投影點名拒寫（訊息不回顯值）。"""
    if any(isinstance(u, dict) and "password" in u for u in users):
        raise SnapshotError("機密紀律：sys_user 撈取含 password 欄——連雜湊值都不入快照，refresh 拒寫（SQL_USERS 須逐欄點名）")
    return {
        "users": sorted((_project(u, USER_KEYS, "sys_user") for u in users), key=lambda u: u["id"]),
        "roles": sorted((_project(r, ROLE_KEYS, "sys_role") for r in roles), key=lambda r: r["id"]),
        "bindings": sorted((_project(b, BINDING_KEYS, "sys_user_role") for b in bindings), key=lambda b: (b["user_id"], b["role_id"])),
    }


def snapshot_dumps(snap):
    """快照序列化：固定鍵序＋indent 2＋非 ASCII 原樣＋結尾換行——同輸入同 byte（同庫重跑零 diff）。"""
    return json.dumps(snap, ensure_ascii=False, indent=2) + "\n"


def _atomic_write(path, text):
    """同目錄暫存→os.replace 原子替換；中途失敗不留半成品。"""
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def psql_fetch(sql, root, run=subprocess.run):
    """compose exec psql 唯讀撈取、回 JSON rows（list）；docker 缺席／stack 不在／輸出非 JSON array＝SnapshotError 帶啟動提示。"""
    cmd = COMPOSE_PSQL + ["psql", "-U", DB_USER, "-d", DB_NAME, "-v", "ON_ERROR_STOP=1", "-qAt", "-c", sql]
    try:
        proc = run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=root)   # locale 無關：中文角色名在 C／POSIX shell 亦不裸拋
    except OSError as ex:
        raise SnapshotError(f"無法執行 docker（{ex}）——refresh 需 dev stack postgres 在跑；先啟動：{STACK_HINT}") from None
    if proc.returncode != 0:
        reason = (proc.stderr or proc.stdout).strip() or f"退出碼 {proc.returncode}"
        raise SnapshotError(f"psql 撈取失敗：{reason}——refresh 需 dev stack postgres 在跑；先啟動：{STACK_HINT}")
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError as ex:
        raise SnapshotError(f"psql 輸出非合法 JSON（{ex.msg}）——查詢形被改動？") from None
    if not isinstance(rows, list):
        raise SnapshotError("psql 輸出非 JSON array——查詢形被改動？")
    return rows


def cmd_refresh(root=ROOT, fetch=psql_fetch):
    """refresh：六撈依序全數成功→組兩快照→才逐檔原子落地（任一撈或組裝失敗即 raise、目錄零寫入）；回 [(rel, 行數)]。

    ★「零寫入」保證的射程＝撈取與組裝階段；兩檔各自 `_atomic_write`（同目錄 mkstemp→os.replace），
    非跨檔單一交易——前檔落地後後檔寫失敗（磁碟／權限）會留下前進一半的 reference-src，下一次 refresh 修正。
    """
    schema_text = snapshot_dumps(build_schema_snapshot(fetch(SQL_COLUMNS, root), fetch(SQL_INDEXES, root), fetch(SQL_CONSTRAINTS, root)))
    accounts_text = snapshot_dumps(build_accounts_snapshot(fetch(SQL_USERS, root), fetch(SQL_ROLES, root), fetch(SQL_BINDINGS, root)))
    written = []
    for rel, text in ((SCHEMA_SNAPSHOT, schema_text), (ACCOUNTS_SNAPSHOT, accounts_text)):
        _atomic_write(os.path.join(root, rel), text)
        written.append((rel, len(text.splitlines())))
    return written


def _load_json(ctx, rel, hint):
    """讀 reference-src 追蹤檔；缺檔／壞 JSON＝fail-loud 帶補救去處（真表的存在前提、不設 stub）。"""
    text = ctx.text(rel)
    if text is None:
        raise SnapshotError(f"{rel} 缺席——{hint}")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as ex:
        raise SnapshotError(f"{rel} 非合法 JSON（{ex.msg}）——{hint}") from None
    if not isinstance(obj, dict):
        raise SnapshotError(f"{rel} 頂層非 JSON object——{hint}")
    return obj


def _cell(v):
    s = str(v) if v not in (None, "", []) else "—"
    return s.replace("|", "\\|")


def gen_reference_schema(ctx):
    """reference/schema ← schema 快照＋archetype-map：逐表分節（表名序）、欄表（ordinal 序）、索引／約束清單（名稱序）。
    快照有表而 map 無歸屬或缺 label＝fail-loud 指名（先補 docs/ops/reference-src/schema-definition.md §1 再登記 map；ADR-00012）。"""
    refresh_hint = f"先跑 {REFRESH_HINT}（需 dev stack postgres 在跑）"
    snap = _load_json(ctx, SCHEMA_SNAPSHOT, refresh_hint)
    amap = _load_json(ctx, ARCHETYPE_MAP, "人寫歸屬檔、隨 schema 刀維護（初始內容＝data-model §1 轉錄）")
    archetypes = {t["table"]: t for t in amap.get("tables", []) if isinstance(t, dict) and "table" in t}
    tables = sorted({r["table"] for key in ("columns", "indexes", "constraints") for r in snap.get(key, [])})
    missing = [t for t in tables if t not in archetypes]
    if missing:
        raise SnapshotError("archetype-map 缺表歸屬：" + "、".join(missing) + f"——先補 docs/ops/reference-src/schema-definition.md §1（ADR-00012）再登記 {ARCHETYPE_MAP}")
    unlabeled = [t for t in tables if not archetypes[t].get("label")]
    if unlabeled:
        raise SnapshotError("archetype-map 條目缺 label：" + "、".join(unlabeled) + f"——補齊 {ARCHETYPE_MAP} 該表的 label 欄")
    parts = [f"{GENERATED_HEADER}\n# reference/schema — 全量正典表\n\n"
             f"來源＝{SCHEMA_SNAPSHOT}（{REFRESH_HINT} 自實庫撈）＋{ARCHETYPE_MAP}（變體歸屬）；由 generate 重算。{FRAMEWORK_TABLE} 除外。\n"]
    for table in tables:
        parts.append(f"\n## {table}（archetype {archetypes[table]['label']}）\n\n| 欄 | 型別 | 可空 | 預設 |\n|---|---|---|---|\n")
        parts.append("".join(f"| {_cell(c['column'])} | {_cell(c['type'])} | {'是' if c['nullable'] else '否'} | {_cell(c['default'])} |\n"
                             for c in sorted((c for c in snap.get("columns", []) if c["table"] == table), key=lambda c: c["ordinal"])))
        for label, key in (("索引", "indexes"), ("約束", "constraints")):
            rows = sorted((r for r in snap.get(key, []) if r["table"] == table), key=lambda r: r["name"])
            if rows:
                parts.append(f"\n{label}：\n" + "".join(f"- {r['name']}｜{r['definition']}\n" for r in rows))
    return "".join(parts)


def gen_reference_accounts(ctx):
    """reference/accounts ← accounts 快照：帳號｜暱稱｜狀態｜角色綁定（多綁依角色碼排序、無綁定「—」）＋角色表；綁定指向不存在 role＝fail-loud。"""
    snap = _load_json(ctx, ACCOUNTS_SNAPSHOT, f"先跑 {REFRESH_HINT}（需 dev stack postgres 在跑）")
    role_code = {r["id"]: r["role_code"] for r in snap.get("roles", [])}
    bound = {}
    for b in snap.get("bindings", []):
        if b["role_id"] not in role_code:
            raise SnapshotError(f"accounts 快照綁定指向不存在的 role id {b['role_id']}（user id {b['user_id']}）——重跑 {REFRESH_HINT}")
        bound.setdefault(b["user_id"], []).append(role_code[b["role_id"]])
    user_rows = "".join(f"| {_cell(u['user_name'])} | {_cell(u['nick_name'])} | {_cell(u['status'])} | {_cell('、'.join(sorted(bound.get(u['id'], []))))} |\n"
                        for u in snap.get("users", []))
    role_rows = "".join(f"| {_cell(r['role_code'])} | {_cell(r['role_name'])} | {_cell(r['status'])} |\n" for r in snap.get("roles", []))
    return (f"{GENERATED_HEADER}\n# reference/accounts — 全量正典表\n\n"
            f"來源＝{ACCOUNTS_SNAPSHOT}（{REFRESH_HINT} 自實庫撈；零密碼欄——契約明文）；由 generate 重算。\n\n"
            "## 帳號\n\n| 帳號 | 暱稱 | 狀態 | 角色綁定 |\n|---|---|---|---|\n" + user_rows +
            "\n## 角色\n\n| 角色碼 | 角色名 | 狀態 |\n|---|---|---|\n" + role_rows)
