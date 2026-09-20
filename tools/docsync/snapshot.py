"""守 RL-0049／RL-0054：快變字面值（schema／帳號）只住實庫快照、真表由 generate 重算；password 欄連雜湊都不入快照。

snapshot.py：refresh 快照管線（需 dev stack postgres）與兩張參考真表的生成器——
六撈 SQL 常數（★SQL_COLUMNS／SQL_INDEXES／SQL_CONSTRAINTS 與 tools/schema-gate.py 三常數位元相等＝gate1 照相面與快照面同構契約，
對賬面＝tests/test_snapshot.py）、psql_fetch（compose exec psql、stack 缺席 fail-loud＋啟動提示）、build_schema_snapshot／build_accounts_snapshot
（白名單投影＋確定性排序）、snapshot_dumps、cmd_refresh（六撈全成功才原子落兩檔、任一失敗零寫入）、gen_reference_schema／gen_reference_accounts
（Ctx 注入、讀 reference-src 三檔；缺檔／壞 JSON／map 缺表或缺 label／綁定懸空＝fail-loud）。
帳號快照投影對賬腿（BL-00038）：gen_reference_accounts 渲染前以 accounts_seed_findings 對賬快照 users／roles／bindings 三節 ⇔
凍結 specs/001-schema-baseline/fixtures/seed.sql 之 sys_user／sys_role／sys_user_role COPY 段投影（⊕ schema-evolution.json 之 seed_* 登記＝合法差額）；
不等、左源缺席或比對面為空＝SnapshotError——generate／check／lint 同經此路（每顆 commit 的 docsync check 即承接、不另占閘號）。
比對在 pg COPY 文字面做；seed 列之 password 欄只留在解析區域資料內、任何訊息只回顯投影鍵值。
generate／check／lint 只讀快照、絕不碰 docker（承 rev5:docs-sync.py 快照管線、重打字為 package 形）。
"""
import json
import os
import re
import subprocess
import tempfile

from . import ROOT, SCHEMA_SNAPSHOT, ACCOUNTS_SNAPSHOT, ARCHETYPE_MAP, REFERENCE_SRC_DIR
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

# 帳號快照投影對賬腿（BL-00038）之兩左源與節對照：(快照節, seed COPY 表, 投影鍵, 身分鍵)
SEED_FIXTURE = "specs/001-schema-baseline/fixtures/seed.sql"     # 凍結 fixture（唯讀；pg_dump --data-only 形）
SCHEMA_EVOLUTION = f"{REFERENCE_SRC_DIR}/schema-evolution.json"  # 演進登記檔（形斷言權威＝tools/schema-gate.py）
ACCOUNT_SECTIONS = (("users", "sys_user", USER_KEYS, ("id",)),
                    ("roles", "sys_role", ROLE_KEYS, ("id",)),
                    ("bindings", "sys_user_role", BINDING_KEYS, BINDING_KEYS))
SEED_KINDS = ("seed_add", "seed_update", "seed_delete")
_RE_COPY_HDR = re.compile(r"^COPY public\.(\w+) \(([^)]*)\) FROM stdin;$")


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


def _copy_text(v):
    """JSON 值 → pg COPY text 格（同 tools/schema-gate.py copy_literal 之則）：投影比對一律在 COPY 文字面做、免猜欄型別。"""
    if v is None:
        return "\\N"
    if isinstance(v, bool):
        return "t" if v else "f"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        return v.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")
    raise SnapshotError(f"帳號投影對賬不支援的值型別：{type(v).__name__}")


def _seed_copy_rows(seed_text, table, keys):
    """凍結 seed 取一表 COPY 段 → [{欄: COPY 文字}]（全欄；sys_user 含 password——只留在此區域資料內、壞列訊息只報列序不回顯列文）。
    段缺席／零列＝比對面為空、段首缺投影欄或列欄數不符＝凍結面受損，皆 fail-loud。"""
    lines = seed_text.splitlines()
    for i, ln in enumerate(lines):
        m = _RE_COPY_HDR.match(ln)
        if not (m and m.group(1) == table):
            continue
        cols = [c.strip().strip('"') for c in m.group(2).split(",")]
        missing = [k for k in keys if k not in cols]
        if missing:
            raise SnapshotError(f"{SEED_FIXTURE} COPY public.{table} 段首缺投影欄 {missing}——凍結面受損或投影鍵與 seed 分家")
        rows = []
        for body in lines[i + 1:]:
            if body == "\\.":
                break
            vals = body.split("\t")
            if len(vals) != len(cols):
                raise SnapshotError(f"{SEED_FIXTURE} COPY public.{table} 段第 {len(rows) + 1} 列欄數 {len(vals)} ≠ 段首 {len(cols)}"
                                    "（凍結面受損；列文含機密欄、不回顯）")
            rows.append(dict(zip(cols, vals)))
        if not rows:
            raise SnapshotError(f"{SEED_FIXTURE} COPY public.{table} 段零列——比對面為空、不得靜默判綠")
        return rows
    raise SnapshotError(f"{SEED_FIXTURE} 缺 COPY public.{table} 段——比對面為空、不得靜默判綠")


def _row_text(row):
    return "、".join(f"{k}={v}" for k, v in row.items())


def seed_account_projection(seed_text, entries):
    """凍結 seed ⊕ seed_* 登記 → {快照節: [投影列（COPY 文字）]}。合成語意同 tools/schema-gate.py apply_seed_entries
    （登記檔形斷言權威在該閘、此處只驗合成所需）；三表以外或非 seed_* 之登記不動本面；登記 pk 只回顯投影鍵之值。"""
    if not isinstance(entries, list):
        raise SnapshotError(f"{SCHEMA_EVOLUTION} entries 須為 list——登記檔壞形（形＝docs/ops/reference-src/schema-evolution-contract.md §2）")
    rows = {table: _seed_copy_rows(seed_text, table, keys) for _, table, keys, _ in ACCOUNT_SECTIONS}
    shown = {table: keys for _, table, keys, _ in ACCOUNT_SECTIONS}
    for e in entries:
        if not isinstance(e, dict):
            raise SnapshotError(f"{SCHEMA_EVOLUTION} entries 含非物件項——登記檔壞形")
        table, kind = e.get("table"), e.get("kind")
        if table not in rows or kind not in SEED_KINDS:
            continue
        eid, d = e.get("id", "?"), e.get("detail") if isinstance(e.get("detail"), dict) else {}
        if kind == "seed_add":
            values = d.get("values")
            if not isinstance(values, dict) or any(k not in values for k in shown[table]):
                raise SnapshotError(f"{SCHEMA_EVOLUTION} {eid} seed_add {table}：detail.values 須為物件且含投影欄 {list(shown[table])}")
            rows[table].append({k: _copy_text(v) for k, v in values.items()})
            continue
        pk = d.get("pk")
        if not isinstance(pk, dict) or not pk:
            raise SnapshotError(f"{SCHEMA_EVOLUTION} {eid} {kind} {table}：detail.pk 須為非空物件（欄:值）")
        want = {k: _copy_text(v) for k, v in pk.items()}
        hits = [i for i, r in enumerate(rows[table]) if all(r.get(k) == v for k, v in want.items())]
        if len(hits) != 1:
            pk_text = _row_text({k: (v if k in shown[table] else "<略>") for k, v in want.items()})
            raise SnapshotError(f"{SCHEMA_EVOLUTION} {eid} {kind} {table}：pk（{pk_text}）命中 {len(hits)} 列（須恰 1）")
        if kind == "seed_delete":
            del rows[table][hits[0]]
            continue
        sets = d.get("set")
        if not isinstance(sets, dict) or not sets:
            raise SnapshotError(f"{SCHEMA_EVOLUTION} {eid} seed_update {table}：detail.set 須為非空物件（欄:值）")
        rows[table][hits[0]].update({k: _copy_text(v) for k, v in sets.items()})
    return {section: [{k: r[k] for k in keys} for r in rows[table]] for section, table, keys, _ in ACCOUNT_SECTIONS}


def accounts_seed_findings(snap, seed_text, entries):
    """accounts 快照三節 ⇔ seed 投影（⊕ seed_* 登記）逐節以身分鍵對齊比對 → 差異訊息列（空＝全等）。
    快照列鍵集須恰為白名單（多鍵——含 password——即 fail-loud、只報鍵名）；訊息只回顯投影鍵值。"""
    expected = seed_account_projection(seed_text, entries)
    out = []
    for section, _, keys, id_keys in ACCOUNT_SECTIONS:
        rows = snap.get(section)
        if not isinstance(rows, list):
            raise SnapshotError(f"{ACCOUNTS_SNAPSHOT} {section} 節須為 list——重跑 {REFRESH_HINT}")
        live = []
        for r in rows:
            if not isinstance(r, dict) or set(r) != set(keys):
                extra = sorted(set(r) - set(keys)) if isinstance(r, dict) else "非 object"
                raise SnapshotError(f"{ACCOUNTS_SNAPSHOT} {section} 節列鍵集不符白名單 {list(keys)}（多：{extra or '無'}）"
                                    f"——password 連雜湊都不入快照；重跑 {REFRESH_HINT}")
            live.append({k: _copy_text(r[k]) for k in keys})
        index = {}
        for side, side_rows in (("快照", live), ("seed", expected[section])):
            idx = index[side] = {}
            for r in side_rows:
                ident = tuple(r[k] for k in id_keys)
                if ident in idx:
                    out.append(f"{section} 節（{side}側）身分鍵重複：{_row_text({k: r[k] for k in id_keys})}")
                idx[ident] = r
        got, want = index["快照"], index["seed"]
        for ident in sorted(set(got) | set(want)):
            g, w = got.get(ident), want.get(ident)
            if w is None:
                out.append(f"{section} 節：快照有而 seed 無 {_row_text(g)}")
            elif g is None:
                out.append(f"{section} 節：seed 有而快照無 {_row_text(w)}")
            else:
                diffs = [f"{k} 快照 {g[k]!r}／seed {w[k]!r}" for k in keys if g[k] != w[k]]
                if diffs:
                    out.append(f"{section} 節 {_row_text({k: g[k] for k in id_keys})}：" + "；".join(diffs))
    return out


def gen_reference_accounts(ctx):
    """reference/accounts ← accounts 快照：帳號｜暱稱｜狀態｜角色綁定（多綁依角色碼排序、無綁定「—」）＋角色表；綁定指向不存在 role＝fail-loud；
    渲染前過帳號快照投影對賬腿（快照 ⇔ 凍結 seed ⊕ seed_* 登記；未登記差額、左源缺席或比對面為空＝fail-loud）。"""
    snap = _load_json(ctx, ACCOUNTS_SNAPSHOT, f"先跑 {REFRESH_HINT}（需 dev stack postgres 在跑）")
    role_code = {r["id"]: r["role_code"] for r in snap.get("roles", [])}
    bound = {}
    for b in snap.get("bindings", []):
        if b["role_id"] not in role_code:
            raise SnapshotError(f"accounts 快照綁定指向不存在的 role id {b['role_id']}（user id {b['user_id']}）——重跑 {REFRESH_HINT}")
        bound.setdefault(b["user_id"], []).append(role_code[b["role_id"]])
    seed_text = ctx.text(SEED_FIXTURE)
    if seed_text is None:
        raise SnapshotError(f"{SEED_FIXTURE} 缺席——帳號快照投影對賬之左源（凍結 fixture）不在場＝比對面為空；凍結面受損自 git 還原、絕不重產")
    ledger = _load_json(ctx, SCHEMA_EVOLUTION, "人寫演進登記檔（形＝docs/ops/reference-src/schema-evolution-contract.md §2）")
    findings = accounts_seed_findings(snap, seed_text, ledger.get("entries"))
    if findings:
        raise SnapshotError(f"{ACCOUNTS_SNAPSHOT} ⇔ {SEED_FIXTURE} 投影不等（{len(findings)} 項未登記差額）：" + "；".join(findings) +
                            f"——補救：seed 真變更→於 {SCHEMA_EVOLUTION} 登記 seed_* 演進；快照漂移→重跑 {REFRESH_HINT}（需 dev stack postgres）")
    user_rows = "".join(f"| {_cell(u['user_name'])} | {_cell(u['nick_name'])} | {_cell(u['status'])} | {_cell('、'.join(sorted(bound.get(u['id'], []))))} |\n"
                        for u in snap.get("users", []))
    role_rows = "".join(f"| {_cell(r['role_code'])} | {_cell(r['role_name'])} | {_cell(r['status'])} |\n" for r in snap.get("roles", []))
    return (f"{GENERATED_HEADER}\n# reference/accounts — 全量正典表\n\n"
            f"來源＝{ACCOUNTS_SNAPSHOT}（{REFRESH_HINT} 自實庫撈；零密碼欄——契約明文）；由 generate 重算。\n\n"
            "## 帳號\n\n| 帳號 | 暱稱 | 狀態 | 角色綁定 |\n|---|---|---|---|\n" + user_rows +
            "\n## 角色\n\n| 角色碼 | 角色名 | 狀態 |\n|---|---|---|\n" + role_rows)
