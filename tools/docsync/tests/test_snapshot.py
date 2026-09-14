"""語料面：snapshot 快照管線的正反自證——合成六撈→兩快照（確定性、白名單投影、零密碼欄）→ refresh（原子落檔、任一撈失敗零寫入）
→ psql_fetch 三種環境失敗 fail-loud 帶啟動提示 → 兩生成器（表×變體節、欄表、索引／約束清單、帳號綁定；缺檔／壞 JSON／map 缺表／缺 label／綁定懸空＝fail-loud）
→ ★三 SQL 常數與 tools/schema-gate.py 同構對賬（importlib 依路徑載入單檔、逐一相等；承 rev5:TestSnapshotIsomorphism 回填條）。
"""
import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest

from docsync import REFERENCE_SRC_DIR, snapshot, common, references, ROOT, SCHEMA_SNAPSHOT, ACCOUNTS_SNAPSHOT, ARCHETYPE_MAP
from docsync.tests.test_book_ids import stub

# 合成六撈（rev6 基線表名；刻意亂序＝排序自證用）
SYN_COLS = [
    {"table": "sys_role", "column": "role_code", "ordinal": 2, "type": "character varying(64)", "nullable": False, "default": None},
    {"table": "sys_role", "column": "id", "ordinal": 1, "type": "bigint", "nullable": False, "default": "nextval('sys_role_id_seq'::regclass)"},
    {"table": "sys_role", "column": "deleted_at", "ordinal": 3, "type": "timestamp with time zone", "nullable": True, "default": None},
    {"table": "casbin_rule", "column": "id", "ordinal": 1, "type": "bigint", "nullable": False, "default": "nextval('casbin_rule_id_seq'::regclass)"},
]
SYN_IDX = [
    {"table": "sys_role", "name": "sys_role_pkey", "definition": "CREATE UNIQUE INDEX sys_role_pkey ON public.sys_role USING btree (id)"},
    {"table": "sys_role", "name": "sys_role_code_active_uniq", "definition": "CREATE UNIQUE INDEX sys_role_code_active_uniq ON public.sys_role USING btree (role_code) WHERE (deleted_at IS NULL)"},
    {"table": "casbin_rule", "name": "casbin_rule_pkey", "definition": "CREATE UNIQUE INDEX casbin_rule_pkey ON public.casbin_rule USING btree (id)"},
]
SYN_CONS = [
    {"table": "sys_role", "name": "sys_role_pkey", "definition": "PRIMARY KEY (id)"},
    {"table": "casbin_rule", "name": "casbin_rule_pkey", "definition": "PRIMARY KEY (id)"},
]
SYN_USERS = [
    {"id": 3, "user_name": "User", "nick_name": "User01", "status": 1},
    {"id": 1, "user_name": "Super", "nick_name": "Super", "status": 1},
    {"id": 2, "user_name": "Admin", "nick_name": "Admin", "status": 1},
]
SYN_ROLES = [
    {"id": 2, "role_code": "R_ADMIN", "role_name": "管理員", "status": 1},
    {"id": 3, "role_code": "R_USER_COMMON", "role_name": "普通用戶", "status": 1},
    {"id": 1, "role_code": "R_SUPER", "role_name": "超級管理員", "status": 1},
]
SYN_BINDS = [{"user_id": 3, "role_id": 3}, {"user_id": 1, "role_id": 1}, {"user_id": 2, "role_id": 2}]
SYN_MAP = {"tables": [{"table": "sys_role", "label": "A 業務全六欄", "active_unique": ["sys_role_code_active_uniq"], "note": "n"},
                      {"table": "casbin_rule", "label": "D 治理", "active_unique": None, "note": "n"}]}


def fake_fetch(sql, root=None):
    """canned fetch：依 SQL 本文分派六撈（sys_user_role 先於 sys_user 判、否則前綴誤中）。"""
    for needle, rows in (("information_schema.columns", SYN_COLS), ("pg_indexes", SYN_IDX), ("pg_constraint", SYN_CONS),
                         ("sys_user_role", SYN_BINDS), ("sys_user", SYN_USERS), ("sys_role", SYN_ROLES)):
        if needle in sql:
            return list(rows)
    raise AssertionError("未知 SQL：" + sql)


def syn_pwd():
    """合成密碼雜湊樣本（RL-0054：執行期串接、不落完整字面）。"""
    return "$argon2id$" + "合成假雜湊-" + "a2b"


def syn_seed(users, roles, binds, pwd=None):
    """合成凍結 seed.sql 三 COPY 段（欄序刻意與快照投影鍵序不同、sys_user 帶 password 欄＝紅線自證用）。"""
    pwd = syn_pwd() if pwd is None else pwd
    out = ["--\n-- Data for Name: sys_role; Type: TABLE DATA; Schema: public; Owner: soybean\n--\n\n",
           "COPY public.sys_role (id, created_at, status, role_code, role_name, role_home) FROM stdin;\n"]
    out += [f"{r['id']}\t2026-08-05 00:00:00+00\t{r['status']}\t{r['role_code']}\t{r['role_name']}\thome\n" for r in roles]
    out.append("\\.\n\n\nCOPY public.sys_user (id, created_at, status, user_name, password, nick_name, session_id) FROM stdin;\n")
    out += [f"{u['id']}\t2026-08-05 00:00:00+00\t{u['status']}\t{u['user_name']}\t{pwd}\t{u['nick_name']}\t\\N\n" for u in users]
    out.append("\\.\n\n\nCOPY public.sys_user_role (user_id, role_id) FROM stdin;\n")
    out += [f"{b['user_id']}\t{b['role_id']}\n" for b in binds]
    out.append("\\.\n")
    return "".join(out)


EMPTY_LEDGER = '{\n  "next_id": 1,\n  "entries": []\n}\n'


def syn_ledger(*entries):
    """合成演進登記檔（id／knife／date 自動補、形同 tools/schema-gate.py 登記檔斷言）。"""
    full = [dict(e, id=f"E-{i:03d}", knife="004-ip-trust-anchor", date="2026-09-14") for i, e in enumerate(entries, 1)]
    return json.dumps({"next_id": len(full) + 1, "entries": full}, ensure_ascii=False)


def src_files(schema=True, accounts=True, amap=True, seed=True, ledger=True, **override):
    """stub 用 reference-src 三檔＋帳號投影對賬兩左源（凍結 seed.sql、演進登記檔）；override 可換任一檔的原文（壞 JSON 案）。"""
    files = {}
    if schema:
        files[SCHEMA_SNAPSHOT] = snapshot.snapshot_dumps(snapshot.build_schema_snapshot(SYN_COLS, SYN_IDX, SYN_CONS))
    if accounts:
        files[ACCOUNTS_SNAPSHOT] = snapshot.snapshot_dumps(snapshot.build_accounts_snapshot(SYN_USERS, SYN_ROLES, SYN_BINDS))
    if amap:
        files[ARCHETYPE_MAP] = json.dumps(SYN_MAP, ensure_ascii=False)
    if seed:
        files[snapshot.SEED_FIXTURE] = syn_seed(SYN_USERS, SYN_ROLES, SYN_BINDS)
    if ledger:
        files[snapshot.SCHEMA_EVOLUTION] = EMPTY_LEDGER
    files.update(override)
    return files


class TestSchemaSnapshot(unittest.TestCase):
    def test_dumps_form_pinned(self):
        """序列化形＝indent 2、非 ASCII 原樣、結尾單一換行——改壞會整檔重寫兩份 tracked 快照。"""
        self.assertEqual(snapshot.snapshot_dumps({"k": ["中文"]}), '{\n  "k": [\n    "中文"\n  ]\n}\n')

    def test_sorted_and_deterministic(self):
        a = snapshot.snapshot_dumps(snapshot.build_schema_snapshot(SYN_COLS, SYN_IDX, SYN_CONS))
        b = snapshot.snapshot_dumps(snapshot.build_schema_snapshot(list(reversed(SYN_COLS)), list(reversed(SYN_IDX)), list(reversed(SYN_CONS))))
        self.assertEqual(a, b)
        self.assertTrue(a.endswith("}\n") and not a.endswith("\n\n"))
        snap = json.loads(a)
        self.assertEqual(list(snap), ["columns", "indexes", "constraints"])
        self.assertEqual([(c["table"], c["ordinal"]) for c in snap["columns"]], [("casbin_rule", 1), ("sys_role", 1), ("sys_role", 2), ("sys_role", 3)])
        self.assertEqual([i["name"] for i in snap["indexes"]], ["casbin_rule_pkey", "sys_role_code_active_uniq", "sys_role_pkey"])
        self.assertEqual(list(snap["columns"][0]), ["table", "column", "ordinal", "type", "nullable", "default"])

    def test_excludes_seaql_migrations(self):
        cols = SYN_COLS + [{"table": "seaql_migrations", "column": "version", "ordinal": 1, "type": "character varying", "nullable": False, "default": None}]
        idx = SYN_IDX + [{"table": "seaql_migrations", "name": "seaql_migrations_pkey", "definition": "CREATE UNIQUE INDEX …"}]
        cons = SYN_CONS + [{"table": "seaql_migrations", "name": "seaql_migrations_pkey", "definition": "PRIMARY KEY (version)"}]
        self.assertNotIn("seaql_migrations", snapshot.snapshot_dumps(snapshot.build_schema_snapshot(cols, idx, cons)))

    def test_row_shape_fail_loud(self):
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.build_schema_snapshot([{"table": "t", "column": "c"}], [], [])                 # 缺欄
        extra = dict(SYN_IDX[0], comment="走私欄")
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.build_schema_snapshot([], [extra], [])                                          # 多欄
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.build_schema_snapshot([], [], ["非 object"])


class TestAccountsSnapshot(unittest.TestCase):
    def test_sorted_and_deterministic(self):
        a = snapshot.snapshot_dumps(snapshot.build_accounts_snapshot(SYN_USERS, SYN_ROLES, SYN_BINDS))
        b = snapshot.snapshot_dumps(snapshot.build_accounts_snapshot(list(reversed(SYN_USERS)), list(reversed(SYN_ROLES)), list(reversed(SYN_BINDS))))
        self.assertEqual(a, b)
        snap = json.loads(a)
        self.assertEqual(list(snap), ["users", "roles", "bindings"])
        self.assertEqual([u["id"] for u in snap["users"]], [1, 2, 3])
        self.assertEqual([r["role_code"] for r in snap["roles"]], ["R_SUPER", "R_ADMIN", "R_USER_COMMON"])
        self.assertEqual([(b["user_id"], b["role_id"]) for b in snap["bindings"]], [(1, 1), (2, 2), (3, 3)])

    def test_password_column_is_secret_red_line(self):
        leaked = dict(SYN_USERS[0], password="$argon2id$" + "假雜湊")
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.build_accounts_snapshot([leaked], SYN_ROLES, SYN_BINDS)
        self.assertIn("password", str(cm.exception))
        self.assertIn("機密紀律", str(cm.exception))                                                 # 釘顯式守衛本身（非 _project 多鍵分支的泛訊息）
        self.assertNotIn("argon2", str(cm.exception))                                                # 錯誤訊息也不回顯值
        text = snapshot.snapshot_dumps(snapshot.build_accounts_snapshot(SYN_USERS, SYN_ROLES, SYN_BINDS))
        self.assertNotIn("password", text)
        self.assertNotIn("argon2", text)
        self.assertNotIn("SELECT *", snapshot.SQL_USERS.upper().replace("  ", " "))
        self.assertIn("SELECT id, user_name, nick_name, status FROM sys_user", snapshot.SQL_USERS)


class TestRefresh(unittest.TestCase):
    def test_writes_both_and_rerun_byte_identical(self):
        with tempfile.TemporaryDirectory() as root:
            written = snapshot.cmd_refresh(root, fetch=fake_fetch)
            self.assertEqual([rel for rel, _ in written], [SCHEMA_SNAPSHOT, ACCOUNTS_SNAPSHOT])
            first = {rel: open(os.path.join(root, rel), encoding="utf-8").read() for rel, _ in written}
            self.assertEqual({rel: len(t.splitlines()) for rel, t in first.items()}, dict(written))
            self.assertEqual(list(json.loads(first[SCHEMA_SNAPSHOT])), ["columns", "indexes", "constraints"])
            self.assertEqual(list(json.loads(first[ACCOUNTS_SNAPSHOT])), ["users", "roles", "bindings"])
            snapshot.cmd_refresh(root, fetch=fake_fetch)                                                # 同庫重跑
            self.assertEqual({rel: open(os.path.join(root, rel), encoding="utf-8").read() for rel in first}, first)
            self.assertEqual(sorted(os.listdir(os.path.join(root, REFERENCE_SRC_DIR))),
                             sorted(os.path.basename(r) for r in first))                             # 無殘留暫存檔

    def test_any_fetch_failure_writes_nothing(self):
        for fail_at in (1, 3, 4, 6):                                                                  # 首撈／schema 末撈／accounts 首撈／末撈
            calls = {"n": 0}

            def flaky(sql, root=None):
                calls["n"] += 1
                if calls["n"] == fail_at:
                    raise snapshot.SnapshotError("psql 撈取失敗（模擬）")
                return fake_fetch(sql, root)
            with tempfile.TemporaryDirectory() as root:
                with self.assertRaises(snapshot.SnapshotError):
                    snapshot.cmd_refresh(root, fetch=flaky)
                self.assertFalse(os.path.exists(os.path.join(root, REFERENCE_SRC_DIR)), fail_at)   # 同目錄零檔
                self.assertEqual(calls["n"], fail_at)                                                 # 失敗即停、不續撈

    def test_bad_shape_writes_nothing(self):
        def leaky(sql, root=None):
            rows = fake_fetch(sql, root)
            return [dict(rows[0], password="x")] + rows[1:] if "FROM sys_user " in sql else rows
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(snapshot.SnapshotError):
                snapshot.cmd_refresh(root, fetch=leaky)
            self.assertFalse(os.path.exists(os.path.join(root, REFERENCE_SRC_DIR)))


class TestPsqlFetch(unittest.TestCase):
    class Proc:
        def __init__(self, rc, out="", err=""):
            self.returncode, self.stdout, self.stderr = rc, out, err

    def test_docker_missing_fail_loud_with_hint(self):
        def boom(*a, **k):
            raise OSError("No such file or directory: 'docker'")
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.psql_fetch("SELECT 1", ROOT, run=boom)
        self.assertIn(snapshot.STACK_HINT, str(cm.exception))
        self.assertIn("docker", str(cm.exception))

    def test_stack_down_fail_loud_with_hint(self):
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.psql_fetch("SELECT 1", ROOT, run=lambda *a, **k: self.Proc(1, err='service "postgres" is not running'))
        self.assertIn(snapshot.STACK_HINT, str(cm.exception))
        self.assertIn("is not running", str(cm.exception))

    def test_non_json_and_non_array_fail_loud(self):
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.psql_fetch("SELECT 1", ROOT, run=lambda *a, **k: self.Proc(0, out="not json"))
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.psql_fetch("SELECT 1", ROOT, run=lambda *a, **k: self.Proc(0, out='{"a": 1}'))

    def test_command_form_and_rows(self):
        seen = {}

        def spy(cmd, **kw):
            seen["cmd"], seen["kw"] = cmd, kw
            return self.Proc(0, out='[{"id": 1}]')
        self.assertEqual(snapshot.psql_fetch("SELECT 1", "/some/root", run=spy), [{"id": 1}])
        cmd = seen["cmd"]
        self.assertEqual(cmd[:9], ["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.dev.yml", "exec", "-T", "postgres"])
        self.assertEqual(cmd[9:], ["psql", "-U", "soybean", "-d", "soybean_admin_rust", "-v", "ON_ERROR_STOP=1", "-qAt", "-c", "SELECT 1"])
        self.assertEqual(seen["kw"].get("cwd"), "/some/root")
        self.assertTrue(seen["kw"].get("capture_output") and seen["kw"].get("text"))
        self.assertEqual(seen["kw"].get("encoding"), "utf-8")                                          # locale 無關（C／POSIX shell 下中文角色名不得裸拋 UnicodeDecodeError）


class TestGenReferenceSchema(unittest.TestCase):
    def test_sections_columns_indexes_constraints(self):
        out = snapshot.gen_reference_schema(stub(src_files()))
        self.assertTrue(out.startswith(common.GENERATED_HEADER + "\n# reference/schema — 全量正典表\n"))
        self.assertIn(SCHEMA_SNAPSHOT, out); self.assertIn(ARCHETYPE_MAP, out)
        self.assertLess(out.index("## casbin_rule（archetype D 治理）"), out.index("## sys_role（archetype A 業務全六欄）"))   # 表名序、變體標註
        self.assertIn("| 欄 | 型別 | 可空 | 預設 |\n|---|---|---|---|\n| id | bigint | 否 | nextval('sys_role_id_seq'::regclass) |\n"
                      "| role_code | character varying(64) | 否 | — |\n| deleted_at | timestamp with time zone | 是 | — |\n", out)   # ordinal 序、可空／預設渲染
        self.assertIn("索引：\n- sys_role_code_active_uniq｜CREATE UNIQUE INDEX sys_role_code_active_uniq", out)
        self.assertIn("約束：\n- sys_role_pkey｜PRIMARY KEY (id)\n", out)

    def test_pipe_in_cell_escaped(self):
        cols = [dict(c) for c in SYN_COLS]; cols[0]["default"] = "'a|b'::text"
        files = src_files(); files[SCHEMA_SNAPSHOT] = snapshot.snapshot_dumps(snapshot.build_schema_snapshot(cols, SYN_IDX, SYN_CONS))
        out = snapshot.gen_reference_schema(stub(files))
        self.assertIn("'a\\|b'::text", out); self.assertNotIn("'a|b'", out)                             # 格內 | 必轉義、否則表欄錯位

    def test_top_level_not_object_fail_loud(self):
        files = src_files(); files[ARCHETYPE_MAP] = "[]"
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.gen_reference_schema(stub(files))
        self.assertIn(ARCHETYPE_MAP, str(cm.exception))                                                  # 人寫檔手改成頂層陣列＝具名 fail-loud、非 AttributeError

    def test_deterministic_same_bytes(self):
        rev = {"tables": list(reversed(SYN_MAP["tables"]))}
        files = src_files(**{SCHEMA_SNAPSHOT: snapshot.snapshot_dumps(snapshot.build_schema_snapshot(list(reversed(SYN_COLS)), list(reversed(SYN_IDX)), list(reversed(SYN_CONS)))),
                             ARCHETYPE_MAP: json.dumps(rev, ensure_ascii=False)})
        self.assertEqual(snapshot.gen_reference_schema(stub(src_files())), snapshot.gen_reference_schema(stub(files)))

    def test_map_missing_table_or_label_fail_loud(self):
        only_role = {"tables": [SYN_MAP["tables"][0]]}
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.gen_reference_schema(stub(src_files(**{ARCHETYPE_MAP: json.dumps(only_role)})))
        self.assertIn("casbin_rule", str(cm.exception)); self.assertIn(ARCHETYPE_MAP, str(cm.exception))
        no_label = {"tables": [dict(SYN_MAP["tables"][0], label=""), SYN_MAP["tables"][1]]}
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.gen_reference_schema(stub(src_files(**{ARCHETYPE_MAP: json.dumps(no_label)})))
        self.assertIn("sys_role", str(cm.exception)); self.assertIn("label", str(cm.exception))

    def test_snapshot_or_map_missing_or_broken_fail_loud(self):
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.gen_reference_schema(stub(src_files(schema=False)))
        self.assertIn(SCHEMA_SNAPSHOT, str(cm.exception)); self.assertIn("python3 tools/docsync refresh", str(cm.exception))
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.gen_reference_schema(stub(src_files(**{SCHEMA_SNAPSHOT: "{壞"})))
        self.assertIn(SCHEMA_SNAPSHOT, str(cm.exception)); self.assertIn("python3 tools/docsync refresh", str(cm.exception))
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.gen_reference_schema(stub(src_files(amap=False)))
        self.assertIn(ARCHETYPE_MAP, str(cm.exception))


class TestGenReferenceAccounts(unittest.TestCase):
    def test_accounts_rows_roles_and_zero_password(self):
        out = snapshot.gen_reference_accounts(stub(src_files()))
        self.assertTrue(out.startswith(common.GENERATED_HEADER + "\n# reference/accounts — 全量正典表\n"))
        self.assertIn(ACCOUNTS_SNAPSHOT, out)
        self.assertIn("## 帳號\n\n| 帳號 | 暱稱 | 狀態 | 角色綁定 |\n|---|---|---|---|\n| Super | Super | 1 | R_SUPER |\n| Admin | Admin | 1 | R_ADMIN |\n| User | User01 | 1 | R_USER_COMMON |\n", out)
        self.assertIn("## 角色\n\n| 角色碼 | 角色名 | 狀態 |\n|---|---|---|\n| R_SUPER | 超級管理員 | 1 |\n| R_ADMIN | 管理員 | 1 |\n| R_USER_COMMON | 普通用戶 | 1 |\n", out)
        self.assertNotIn("password", out); self.assertNotIn("argon2", out)

    def test_multi_binding_sorted_and_unbound_dash(self):
        binds = SYN_BINDS + [{"user_id": 1, "role_id": 2}]
        users = SYN_USERS + [{"id": 4, "user_name": "Ghost", "nick_name": "G", "status": 0}]
        files = src_files(**{ACCOUNTS_SNAPSHOT: snapshot.snapshot_dumps(snapshot.build_accounts_snapshot(users, SYN_ROLES, binds)),
                             snapshot.SEED_FIXTURE: syn_seed(users, SYN_ROLES, binds)})                  # seed 同步＝投影對賬面全等、本案只驗渲染
        out = snapshot.gen_reference_accounts(stub(files))
        self.assertIn("| Super | Super | 1 | R_ADMIN、R_SUPER |", out)
        self.assertIn("| Ghost | G | 0 | — |", out)

    def test_dangling_binding_fail_loud(self):
        files = src_files(**{ACCOUNTS_SNAPSHOT: snapshot.snapshot_dumps(snapshot.build_accounts_snapshot(SYN_USERS, SYN_ROLES, SYN_BINDS + [{"user_id": 1, "role_id": 99}]))})
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.gen_reference_accounts(stub(files))
        self.assertIn("99", str(cm.exception)); self.assertIn("python3 tools/docsync refresh", str(cm.exception))

    def test_snapshot_missing_or_broken_fail_loud(self):
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.gen_reference_accounts(stub(src_files(accounts=False)))
        self.assertIn(ACCOUNTS_SNAPSHOT, str(cm.exception)); self.assertIn("python3 tools/docsync refresh", str(cm.exception))
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.gen_reference_accounts(stub(src_files(**{ACCOUNTS_SNAPSHOT: "[壞"})))


class TestAccountsSeedProjection(unittest.TestCase):
    """BL-00038：accounts 快照三節 ⇔ 凍結 seed.sql 之 sys_user／sys_role／sys_user_role COPY 段投影全等（generate／check／lint 皆經
    gen_reference_accounts 此路）；schema-evolution.json 之 seed_* 登記＝合法差額、未登記差額即紅；password 欄不進任何輸出面。"""

    def _red(self, **override):
        with self.assertRaises(snapshot.SnapshotError) as cm:
            snapshot.gen_reference_accounts(stub(src_files(**override)))
        return str(cm.exception)

    def _green(self, **override):
        return snapshot.gen_reference_accounts(stub(src_files(**override)))

    def test_real_repo_snapshot_equals_seed_projection_on_non_empty_surface(self):
        ctx = common.Ctx(ROOT)
        seed_text = ctx.text(snapshot.SEED_FIXTURE)
        entries = json.loads(ctx.text(snapshot.SCHEMA_EVOLUTION))["entries"]
        proj = snapshot.seed_account_projection(seed_text, entries)
        # 比對面非空：三節皆在且各 ≥1 列——不釘列數，免得日後合法的 seed_add 登記把本案打紅
        self.assertEqual(set(proj), {"users", "roles", "bindings"})
        self.assertTrue(all(len(v) >= 1 for v in proj.values()), {k: len(v) for k, v in proj.items()})
        self.assertEqual({tuple(r) for rows in proj.values() for r in rows},
                         {snapshot.USER_KEYS, snapshot.ROLE_KEYS, snapshot.BINDING_KEYS})                   # 投影列只帶白名單鍵
        self.assertEqual(snapshot.accounts_seed_findings(json.loads(ctx.text(ACCOUNTS_SNAPSHOT)), seed_text, entries), [])

    def test_unregistered_diff_is_red_naming_section_and_row(self):
        msg = self._red(**{snapshot.SEED_FIXTURE: syn_seed([u for u in SYN_USERS if u["id"] != 3], SYN_ROLES, SYN_BINDS)})
        self.assertIn("users", msg); self.assertIn("id=3", msg)
        self.assertIn(snapshot.SCHEMA_EVOLUTION, msg)                                                          # 補救去處
        nick = [dict(u, nick_name="User02") if u["id"] == 3 else u for u in SYN_USERS]
        msg = self._red(**{snapshot.SEED_FIXTURE: syn_seed(nick, SYN_ROLES, SYN_BINDS)})
        for needle in ("users", "id=3", "nick_name", "User02"):
            self.assertIn(needle, msg)
        roles = [dict(r, role_name="管理者") if r["id"] == 2 else r for r in SYN_ROLES]
        msg = self._red(**{snapshot.SEED_FIXTURE: syn_seed(SYN_USERS, roles, SYN_BINDS)})
        for needle in ("roles", "id=2", "role_name", "管理者"):
            self.assertIn(needle, msg)
        msg = self._red(**{snapshot.SEED_FIXTURE: syn_seed(SYN_USERS, SYN_ROLES, SYN_BINDS + [{"user_id": 1, "role_id": 2}])})
        for needle in ("bindings", "user_id=1", "role_id=2"):
            self.assertIn(needle, msg)

    def test_registered_seed_evolution_is_tolerated_and_same_diff_unregistered_is_red(self):
        old = [dict(u, nick_name="Old01") if u["id"] == 3 else u for u in SYN_USERS]
        seed_old = syn_seed(old, SYN_ROLES, SYN_BINDS)
        upd = {"kind": "seed_update", "table": "sys_user", "detail": {"pk": {"id": 3}, "set": {"nick_name": "User01"}}}
        self._green(**{snapshot.SEED_FIXTURE: seed_old, snapshot.SCHEMA_EVOLUTION: syn_ledger(upd)})
        self.assertIn("id=3", self._red(**{snapshot.SEED_FIXTURE: seed_old}))
        other = dict(upd, table="sys_menu")                                                                   # 他表登記不外溢
        self.assertIn("id=3", self._red(**{snapshot.SEED_FIXTURE: seed_old, snapshot.SCHEMA_EVOLUTION: syn_ledger(other)}))
        ghost = {"id": 4, "user_name": "Ghost", "nick_name": "G", "status": 0}
        snap4 = snapshot.snapshot_dumps(snapshot.build_accounts_snapshot(SYN_USERS + [ghost], SYN_ROLES, SYN_BINDS + [{"user_id": 4, "role_id": 3}]))
        adds = ({"kind": "seed_add", "table": "sys_user",
                 "detail": {"pk": ["id"], "values": dict(ghost, created_at="2026-09-14 00:00:00+00", password=syn_pwd(), session_id=None)}},
                {"kind": "seed_add", "table": "sys_user_role", "detail": {"pk": ["user_id", "role_id"], "values": {"user_id": 4, "role_id": 3}}})
        self._green(**{ACCOUNTS_SNAPSHOT: snap4, snapshot.SCHEMA_EVOLUTION: syn_ledger(*adds)})
        msg = self._red(**{ACCOUNTS_SNAPSHOT: snap4, snapshot.SCHEMA_EVOLUTION: syn_ledger(adds[0])})
        self.assertIn("bindings", msg); self.assertIn("user_id=4", msg)
        seed_extra = syn_seed(SYN_USERS, SYN_ROLES + [{"id": 4, "role_code": "R_TMP", "role_name": "暫", "status": 1}], SYN_BINDS)
        dele = {"kind": "seed_delete", "table": "sys_role", "detail": {"pk": {"id": 4}}}
        self._green(**{snapshot.SEED_FIXTURE: seed_extra, snapshot.SCHEMA_EVOLUTION: syn_ledger(dele)})
        self.assertIn("R_TMP", self._red(**{snapshot.SEED_FIXTURE: seed_extra}))

    def test_password_column_never_reaches_any_output(self):
        pwd = syn_pwd()
        nick = [dict(u, nick_name="User02") if u["id"] == 3 else u for u in SYN_USERS]
        for files in ({snapshot.SEED_FIXTURE: syn_seed(nick, SYN_ROLES, SYN_BINDS, pwd=pwd)},                     # 列值不等
                      {snapshot.SEED_FIXTURE: syn_seed(SYN_USERS, SYN_ROLES, SYN_BINDS, pwd=pwd + "\textra")},    # 壞列（欄數不符）
                      {snapshot.SEED_FIXTURE: syn_seed(SYN_USERS[:1], SYN_ROLES, SYN_BINDS, pwd=pwd)},           # 缺列
                      {snapshot.SCHEMA_EVOLUTION: syn_ledger({"kind": "seed_update", "table": "sys_user",         # 登記以密碼欄當 pk、命中數≠1
                                                              "detail": {"pk": {"password": pwd}, "set": {"nick_name": "x"}}})}):
            msg = self._red(**files)
            self.assertNotIn(pwd, msg); self.assertNotIn("argon2", msg)
        out = self._green(**{snapshot.SCHEMA_EVOLUTION: syn_ledger({"kind": "seed_update", "table": "sys_user",   # 登記改雜湊＝投影面零差額
                                                                    "detail": {"pk": {"id": 1}, "set": {"password": pwd + "2"}}})})
        self.assertNotIn("argon2", out)
        leaked = json.loads(src_files()[ACCOUNTS_SNAPSHOT])
        leaked["users"][0]["password"] = pwd                                                                  # 快照檔被塞 password 鍵
        msg = self._red(**{ACCOUNTS_SNAPSHOT: json.dumps(leaked, ensure_ascii=False)})
        self.assertIn("password", msg); self.assertNotIn(pwd, msg)

    def test_missing_or_empty_left_source_fail_loud(self):
        self.assertIn(snapshot.SEED_FIXTURE, self._red(seed=False))
        no_binds = syn_seed(SYN_USERS, SYN_ROLES, SYN_BINDS).split("COPY public.sys_user_role")[0]
        msg = self._red(**{snapshot.SEED_FIXTURE: no_binds})
        self.assertIn("sys_user_role", msg); self.assertIn("比對面為空", msg)
        msg = self._red(**{snapshot.SEED_FIXTURE: syn_seed(SYN_USERS, [], SYN_BINDS)})
        self.assertIn("sys_role", msg); self.assertIn("比對面為空", msg)
        self.assertIn(snapshot.SCHEMA_EVOLUTION, self._red(ledger=False))
        self.assertIn(snapshot.SCHEMA_EVOLUTION, self._red(**{snapshot.SCHEMA_EVOLUTION: "{壞"}))
        self.assertIn("entries", self._red(**{snapshot.SCHEMA_EVOLUTION: '{"next_id": 1, "entries": {}}'}))
        msg = self._red(**{snapshot.SCHEMA_EVOLUTION: syn_ledger({"kind": "seed_delete", "table": "sys_role", "detail": {"pk": {"id": 99}}})})
        self.assertIn("E-001", msg); self.assertIn("命中 0 列", msg)


class TestWiring(unittest.TestCase):
    def test_roster_contains_two_new_keys(self):
        for rel in ("docs/generated/reference/schema.md", "docs/generated/reference/accounts.md"):
            self.assertIn(rel, references.GENERATED_FILES)
        self.assertEqual(len(references.GENERATED_FILES), 15)

    def test_real_repo_snapshots_present_and_generators_run(self):
        """快照為 tracked 檔、落地後恆在：真 repo 兩生成器可算、且 archetype-map 15 表全數入表。"""
        ctx = common.Ctx(ROOT)
        for rel in (SCHEMA_SNAPSHOT, ACCOUNTS_SNAPSHOT, ARCHETYPE_MAP):
            self.assertIsNotNone(ctx.text(rel), rel)
        out = snapshot.gen_reference_schema(ctx)
        self.assertEqual(out.count("\n## "), 15)
        self.assertIn("| Super | Super | 1 | R_SUPER |", snapshot.gen_reference_accounts(ctx))


class TestIsomorphismWithSchemaGate(unittest.TestCase):
    """三 SQL 常數＝schema-gate gate1 照相面與 refresh 快照面的同構契約：依路徑載入 tools/schema-gate.py、逐一位元相等。"""

    def test_three_sql_constants_identical(self):
        path = os.path.join(ROOT, "tools", "schema-gate.py")
        spec = importlib.util.spec_from_file_location("schema_gate_under_test", path)
        mod = importlib.util.module_from_spec(spec)
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(mod)
        for name in ("SQL_COLUMNS", "SQL_INDEXES", "SQL_CONSTRAINTS"):
            self.assertEqual(getattr(mod, name), getattr(snapshot, name), name)
        self.assertIn("seaql_migrations", snapshot.SQL_COLUMNS)
        self.assertEqual((mod.DB_USER, mod.DB_NAME), (snapshot.DB_USER, snapshot.DB_NAME))               # 執行形同構：DB 身分
        self.assertEqual(mod._db_base(None), snapshot.COMPOSE_PSQL)                                         # 執行形同構：compose exec 前綴


if __name__ == "__main__":
    unittest.main()
