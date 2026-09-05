#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/schema-gate.py — 三閘 schema 驗證閘（001-schema-baseline 基線；Day-1 受管演進帳）

隨遷工具（承 rev5:tools/schema-gate.py 逐字承襲、改 rev6 座標；RULES 名詞段「隨遷工具」）。

子命令：
  check [--container 名] [--user U] [--db D]
        三閘全跑（gate1 結構＋gate2 欄序/seed＋audit archetype）；入口無條件先跑合成
        self-test（敗＝rc 2、不讀任何真檔）。預設對 dev stack（compose exec postgres）；
        `--container` 指向一次性 pristine 容器（fixtures 產製／演進帳往返驗證場景）。
  test  跑自帶測試（unittest、離線、零 docker）——含 SC-003 五類 negative 注入
        （結構／欄序／seed 值／sequence 落值／假 delta 登記合成）與登記檔壞形自測。
  doccheck  data-model.md 文件面（§2 欄五元組＋§6 索引約束＋§9 sequences 落值）vs 凍結
        fixtures 機器對賬（承 rev5:B-010；離線零 docker、不讀庫；★不入 pre-commit 常跑鏈——
        手動／review 輪跑）。

契約＝specs/001-schema-baseline/contracts/gates.md（行為）＋contracts/schema-evolution.md
（登記檔形＋啟動斷言七條）＋contracts/fixtures.md（凍結面）。零容差語意：一切比對＝全等，
「容差」合法形恰兩種＝①演進帳登記（docs/ops/reference-src/schema-evolution.json）
②rev5:B-065 表級收窄（RUNTIME_APPEND_TABLES 寫死本檔、配 seed 必空斷言；見下 gate2 seed 段）；
除此之外一律全等。

三閘：
  gate1 結構——左源＝specs/001-schema-baseline/fixtures/{columns,indexes,constraints}.json
        （凍結面）⊕ 演進帳合成期望；右源＝實庫照相三節（與 python3 tools/docsync refresh
        同構三查詢、排除 seaql_migrations、確定性排序）；三節逐列全等，未登記差異＝紅
        （指名 section／table／名稱／左右值）、登記超前（登記了實庫沒有）同紅。
  gate2 欄序——左源＝data-model.md §2 逐表欄序（解析「| # | 欄 |」表體）＋演進帳
        add_column 接末位；右源＝實庫 ordinal；14 親排表逐位全等、casbin_rule 豁免。
  gate2 seed——左源＝fixtures/seed.sql ⊕ seed_* 演進合成；右源＝實庫 pg_dump --data-only；
        兩側同一 normalize（COPY 段整列排序＋setval 原位＋剝除 \\restrict／\\unrestrict
        token 行＋seaql_migrations COPY 段＋pg_dump 版本兩行＋Owner 值正規化）後
        **未排序逐列 diff**（含 id 欄）；★禁全檔排序後雜湊（會掩蓋 sequence 落值漂移與
        真差異）。sequence 名冊＝凍結 fixtures/seed.sql 之 setval 行（RE_SETVAL 解析、勿手抄
        名字面；rev5 另讀其 seed 決策 json、rev6 不搬該檔——名冊與凍結 seed 同源）。
        ★rev5:B-065 表級收窄：RUNTIME_APPEND_TABLES 四表（session_event／sys_login_attempt／
        sys_token／sys_operation_log——末者於 rev5:004-ip-trust-anchor 入集）
        兩側再剝其 COPY 資料列（段首欄名行照比＝結構漂移仍紅）＋其 sequence 之
        setval 值正規化為佔位（行存在仍比、整行消失＝紅），並另斷言 seed 側此類表
        必 0 列——runtime 寫入不再紅、往 seed 塞稽核列照樣紅。
  audit archetype——左源＝docs/ops/reference-src/archetype-map.json（15 表歸屬、形契約
        gates.md §3）；對實庫照相逐表驗四變體規則（C／D 子型硬編碼於工具、map note＝
        人讀註記）；created_by 可空性顯式驗（NN 恰四表）；表清單守門（實庫表集≠map
        表集＝紅）。

退出碼：0 全綠／1 漂移（逐項指名）／2 環境或結構異常（fixtures 缺、登記檔壞形、庫不可達、
比對面為空、self-test 敗——附補救提示）／64 用法錯誤（usage 走 stderr）。
只跑唯讀查詢與 pg_dump、絕不寫庫；pg_dump 帶 PGTZ=UTC（閘不依賴 session timezone、
data-model §4 UTC+0 拍板）；輸出不含 deploy 機密值（seed 定稿值〔含 PHC 常數〕本在
版控、gate2 seed diff 可回顯——非洩密面）。

雙源互證（rev6 pristine 萃取之 fixtures vs rev5 同名檔逐位元全等；contracts/gates.md §2）＝
fixtures 產製之一次性驗證（紀錄住 fixtures/provenance.md）、非三閘常態比對面；工具不內建
rename 映射（rev5 有、供其 rev4 血緣對賬；rev6 無此場景、research R6）。
"""

import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

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

# 登記檔（contracts/schema-evolution.md）：kind 枚舉恰八值；id／knife／date 格式
KINDS = ("add_table", "add_column", "alter_column", "add_index", "add_constraint",
         "seed_add", "seed_update", "seed_delete")
# 斷言⑦（rev5:B-006；contracts/schema-evolution.md §2 第 7 條）：kind×detail 必備鍵表——八 kind
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
# 射程＝恰四表：rev5:003 實痛三表（該刀走查收尾清的正是那三表三 sequence）＋
# ★sys_operation_log（rev5:004-ip-trust-anchor T037／其 spec FR-042 **明列的排程工作項**）。
# ★末者入集的時點理由：該表在 rev5:004 之前是**零寫入者**，該刀的 IP 規則四寫端使它取得
# rev5 首個寫入者——寫端一落列，gate2 對它的 seed 逐列 diff 即紅，那是**預期的**、
# 不是回歸；入集是 spec 排定的處置，不得當 bug 追。rev6 資料形狀同 rev5、server 刀後即
# 需要同一收窄（research R6：保留）。
# ★sys_ip_rule **MUST NOT 入集**：它是 archetype 變體 A 業務表、列內容即真 seed 面
# （zero-seed 亦是一種 seed 面宣告），收窄它＝管理面誤寫一列規則不再被閘看見。
# 該表的 runtime 測試殘留一律走走查還原紀律（TRUNCATE＋setval 收尾；RL-0031）。
# ★sys_user_role 絕不入集——archetype 同標變體 C 但屬**有 seed 列的 join 表**（種子
# 使用者的角色掛載），收窄它＝真 seed 面被弱化。其餘變體 B/C 零 seed 表
# （sys_access_log／sys_pwd_custody／sys_user_email_verify）未實暴
# runtime 寫入、暫不入集——日後要擴＝本常數加一行：鍵欄（表名）之「seed 必空」斷言
# 對新成員自動生效；值欄（sequence 名）由凍結 columns.json 之 nextval default 機器
# 對賬（TestConstantsPinned 值欄對賬測——值欄作用面＝setval 佔位、與鍵欄作用面＝剝列
# 互相獨立，手抄錯名＝非收窄表的 setval 落值守門靜默弱化，該測指名紅、勿臆測手抄）。
# ★安全邊界紀律：清單寫死本檔、絕不取自呼叫端——另一候選「runtime-tolerant 呼叫旗標」
# 已於 rev5 被否決：旗標＝呼叫端控制安全邊界（任何呼叫都能帶旗標把守門面調弱、閘形同
# 虛設）。收窄語意權威＝rev5 隨 rev5:B-065 所立之 ADR；rev6 承襲點＝research R6、本註解為
# 工具面記載。
RUNTIME_APPEND_TABLES = {
    "session_event": "session_event_id_seq",
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


class GateError(Exception):
    """環境／結構異常（fixtures 缺、登記檔壞形、庫不可達、比對面為空）——rc 2 fail-loud。"""


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
    cmd = _db_base(container) + ["psql", "-U", user, "-d", db,
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
    （呼叫端轉 rc 2）；contracts/schema-evolution.md §2 第 7 條。"""
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
    """演進登記檔＋啟動斷言七條（contracts/schema-evolution.md §2）；任一敗＝GateError。"""
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
              "contracts/fixtures.md）；未產製→依 §2 產製程序（pristine 重放＋三驗後照相"
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


def apply_seed_entries(norm_text, entries):
    """seed 面演進合成到左源（normalize 後施作、段內重排序）。消費四類 entries：
    seed_add＝{pk:[主鍵欄…], values:{欄:值 全欄}}／seed_update＝{pk:{欄:值}, set:{欄:值}}
    ／seed_delete＝{pk:{欄:值}}；★add_column 亦動 seed 面（pg_dump COPY 段首欄清單隨
    結構走）——僅支援 nullable 無 default 形（既有列補 \\N）；其它形與 add_table 之
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
    從此無感——而那正是 rev5:ADR 0008 那次逼 rev5 001 凍結 fixtures 重產一次的事實。本檢查把該
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
        fnd.append(f"[audit] 表清單守門｜實庫表 {t} 未登記 archetype 歸屬"
                   "（先補 data-model §1、再登記 archetype-map.json）")
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
    normalize 冪等＋rev5:B-065 收窄三點探針——任一敗＝AssertionError（呼叫端轉 rc 2、
    不讀真檔）。"""
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
    # rev5:B-065 runtime-append 收窄三點探針（八臂全測歸 TestRuntimeAppendNarrow；此處常駐
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
    # ③ 右源照相＋dump（唯讀）
    try:
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
    except GateError as ex:
        print(f"[check] ✗ {ex}", file=sys.stderr)
        return 2
    if findings:
        print(f"[check] ✗ {len(findings)} 項漂移（未登記差異一律紅；合法化唯一路徑＝"
              "schema-evolution.json 登記）：", file=sys.stderr)
        for x in findings:
            print(f"    DRIFT {x}", file=sys.stderr)
        return 1
    n_entries = len(ledger["entries"])
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
    ③seed 值④sequence 落值⑤假 delta 登記合成（對真凍結面、test_5）。"""

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
        """第五案（contracts/gates.md §4 ⑤、spec FR-009、research R7）：對**真凍結 fixtures**
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


class TestLedgerAssertions(unittest.TestCase):
    """登記檔啟動斷言七條（contracts/schema-evolution.md §2）＝rc 2 fail-loud。"""

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


class TestRuntimeAppendNarrow(unittest.TestCase):
    """rev5:B-065 表級收窄八臂紅綠（rev5 2026-08-11 拍板「收窄寫死工具內」形、rev6 承襲；離線合成
    dump、不碰真庫）：①收窄表 actual 側 runtime 列→綠②seed 側塞列→紅（必空斷言、
    具名）③非收窄表列漂移→照紅（不外溢）④setval 值異→綠、整行消失→紅⑤收窄表
    COPY 段首欄名變動→照紅（結構面仍守）⑥normalize＋收窄全管線冪等⑦前綴鄰接表
    sys_token_x 之列與 setval 值原樣保留（成員判定＝全名全等、退化成前綴匹配即紅）
    ⑧收窄表 COPY 段整段缺席→必空斷言跳過不誤報、缺段由收窄後 diff 自紅（降級腿
    論證的機器載體、rev5:L-019）。"""

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
    """rev5:B-013 缺口①：cmd_check 綠路徑離線全程（照相→合成→三閘→四行摘要→rc 0）。樁沿
    TestPgDumpArgv fake_run 法：按 SQL 常數分派 fixtures 三節 JSON、pg_dump 回凍結
    seed.sql。★驗 SQL 分派正確＋四行摘要格式計數＋rc 0；比對器邏輯歸 check_self_test
    承載、此處刻意不重驗（分工）。凍結基線複製入暫存 root＋空演進帳＝真登記檔日後長
    entries 也不影響本測（凍結面永不改寫、字面計數可釘）。"""

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
        # SQL 分派：三查詢恰各一次、序＝columns→indexes→constraints，殿後 pg_dump
        self.assertEqual(calls, [SQL_COLUMNS, SQL_INDEXES, SQL_CONSTRAINTS, "pg_dump"])
        lines = out.getvalue().splitlines()
        self.assertEqual(len(lines), 4)
        self.assertTrue(all(ln.startswith("[check] ✓") for ln in lines), msg=lines)
        self.assertIn("gate1 結構：columns 169／indexes 38／constraints 101 全等",
                      lines[0])
        self.assertIn("演進帳合成 0 筆", lines[0])
        self.assertIn("gate2 欄序：14 親排表逐位全等", lines[1])
        self.assertIn("casbin_rule 豁免", lines[1])
        # rev5:B-065 收窄後比對面行數：收窄各表 seed 側本就零列、setval 行原位改佔位——
        # 行數與未收窄時相等（凍結面字面可釘）
        n = len(narrow_runtime_append(normalize_seed_dump(fx["seed"])).splitlines())
        self.assertEqual(n, len(normalize_seed_dump(fx["seed"]).splitlines()))
        self.assertIn(f"gate2 seed：normalize 後 {n} 行逐列零差異（setval 名冊 11 支；"
                      "runtime-append 收窄 4 表）", lines[2])
        self.assertIn("audit archetype：15/15 綠", lines[3])


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
    """audit 變體判準的負向覆蓋（RL-0051「變異要打在判準上」；contracts/gates.md §4 negative 第六類）。
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


class TestConstantsPinned(unittest.TestCase):
    """治理常數字面釘死（慣例承 entity-drift-gate TestGovernanceConstantsPinned）：常數縮水＝斷言跟縮
    的套套邏輯在此擋。"""

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

    def test_runtime_append_tables_pinned(self):
        """rev5:B-065 收窄集字面釘死（表→sequence 名、自 fixtures/seed.sql setval 行讀出）；
        擴集＝同 commit 改本案＋常數註解射程論證——防常數縮水後六臂自測跟縮的套套
        邏輯，並釘 sys_user_role 永不入集（有 seed 列的 join 表、收窄＝弱化真 seed 面）。
        ★rev5:004-ip-trust-anchor T037：sys_operation_log 入集（該刀 spec FR-042 排定；rev6 承襲）。
        ★同案釘死 sys_ip_rule **永不入集**——它是變體 A 業務表、列內容即真 seed 面
        （zero-seed 亦是宣告）；誤加進收窄集時本案當場紅，這正是該誤加唯一的機器守
        （收窄之後 gate2 對該表的資料列全無感，錯誤本身零徵狀）。"""
        self.assertEqual(RUNTIME_APPEND_TABLES, {
            "session_event": "session_event_id_seq",
            "sys_login_attempt": "sys_login_attempt_id_seq",
            "sys_operation_log": "sys_operation_log_id_seq",
            "sys_token": "sys_token_id_seq"})
        self.assertNotIn("sys_user_role", RUNTIME_APPEND_TABLES)
        self.assertNotIn("sys_ip_rule", RUNTIME_APPEND_TABLES)

    def test_runtime_append_seq_names_ledgered(self):
        """rev5:B-065 值欄（sequence 名）機器對賬：鍵欄（表名）有「seed 必空」斷言自動守門，
        值欄作用面（setval 佔位）與其獨立——擴集手抄錯名（如 sys_token→
        sys_access_log_id_seq）＝**非收窄表**的 setval 落值守門靜默弱化（誤配線版對
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
