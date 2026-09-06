"""憲法 §I.5 例外① 自證（BL-00025；user 拍板 2026-09-07 口徑①、輕量軌 maint-backlog-25）：
`rust-api/sea-orm-adapter` 全部 tracked 檔去整行註解後與 rev5 凍結樹（ADR-00002：rust-api @ 92919b9）逐檔 diff，
差異只准「逐行替換」且逐對登記於 ALLOWLIST（附理由）；多一行／少一行／對不上 allowlist／allowlist 未消費（例外已不存在＝漂移）／
rev5 檔缺席／掃描面空集合皆為 finding。非治理閘、不入 GATES 名冊：bootstrap 3c 步呼叫（每台機器體檢）、子命令 `python3 tools/docsync vendored-check`。
★ADR-00009 條件①（去註解後逐位元）只鎖例外②（migration／entity 17 檔）；例外①口徑住本檔＋maint-backlog-25 收單事件，ADR-00009 不動。
★改 adapter 任何非註解行＝同批改 ALLOWLIST（否則下一次 bootstrap 紅）；例外增多到需要「理由以外的判準」時＝另立 ADR。"""
import difflib
import hashlib
import os
import subprocess

VENDORED_SUB = "rust-api"          # 子庫（tracked 檔集自其 git ls-files 取）
VENDORED_DIR = "sea-orm-adapter"   # 相對子庫根
COMMENT_PREFIX = {".rs": "//", ".toml": "#", ".conf": "#", ".csv": None}   # 整行註解前綴（None＝不剝）

# 具名例外：(檔〔相對 sea-orm-adapter〕, rev6 行〔strip 後、可讀〕, rev5 行之 sha256 前 12 碼〔★不落 rev5 字面——RL-0054：rev5 該行含合成連線字串〕, 理由)。
# 同形差異出現幾次就登記幾筆（逐次消費、多出即紅）；新增例外＝`python3 -c` 對 rev5 該行 strip 後取 hashlib.sha256(...).hexdigest()[:12]。
ALLOWLIST = (
    ("src/adapter.rs",
     '#[ignore = "需 live postgres（env DATABASE_URL）；★專用空庫限定——本測會清空 casbin_rule，對 rev6 dev 庫跑即毀掉 m0002 基線 seed 政策"]',
     "5eb17ed65d19",
     "測試 ignore 理由字串改 rev6 座標（m0002 基線 seed）；rev5 為「…對 rev5 dev 庫跑即毀掉 seed 政策」；屬性字串、非邏輯（第一處：postgres 案）"),
    ("src/adapter.rs",
     'format!("mysql://{}:{}@localhost:3306/casbin", "root", "123456")',
     "b3f50c62efca",
     "RL-0054：合成機密樣本執行期串接、tracked 檔不落完整字面（rev5 為含帳密的字面連線字串——故本表只存其雜湊）"),
    ("src/adapter.rs",
     '#[ignore = "需 live postgres（env DATABASE_URL）；★專用空庫限定——本測會清空 casbin_rule，對 rev6 dev 庫跑即毀掉 m0002 基線 seed 政策"]',
     "5eb17ed65d19",
     "同第一筆理由（第二處：postgres 含 domain 案）"),
)


def line_hash(line):
    """allowlist 之 rev5 側比對鍵＝strip 後行文的 sha256 前 12 碼（rev5 字面不落 tracked 檔）。"""
    return hashlib.sha256(line.encode("utf-8")).hexdigest()[:12]


def default_rev5_root(root):
    return os.path.normpath(os.path.join(root, "..", "fork260509-rev5"))


def strip_comments(text, ext):
    """去整行註解（首個非空白字元為該副檔名之註解前綴的整行；.rs 含 ///、//!）；回行清單（不含換行）。"""
    pref = COMMENT_PREFIX.get(ext)
    out = []
    for ln in text.split("\n"):
        if pref is not None and ln.lstrip().startswith(pref):
            continue
        out.append(ln)
    return out


def tracked_files(root):
    """自子庫 git ls-files 取 sea-orm-adapter 下 tracked 檔（相對 sea-orm-adapter）；子庫不在工作樹＝空清單（呼叫端當掃描面空集合紅）。"""
    sub = os.path.join(root, VENDORED_SUB)
    # ★pre-commit 期間 git 匯出 GIT_INDEX_FILE／GIT_DIR（指外層 repo）——子庫 ls-files 會讀到外層 index 而回空；剝掉 GIT_* 再呼叫（hook 內自測即因此紅過）。
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        out = subprocess.run(["git", "-C", sub, "ls-files", VENDORED_DIR], capture_output=True, text=True, check=True, env=env).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    prefix = VENDORED_DIR + "/"
    return sorted(p[len(prefix):] for p in out.split("\n") if p.startswith(prefix))


def compare_tree(rev6_dir, rev5_dir, rel_files, allowlist):
    """逐檔去註解 diff；回 (findings, stats)。findings 空＝全等或差異全在 allowlist 且 allowlist 全數消費。"""
    findings = []
    stats = {"files": 0, "allow_consumed": 0}
    if not rel_files:
        return ["掃描面空集合：sea-orm-adapter 零 tracked 檔（子庫不在工作樹？）"], stats
    consumed = [False] * len(allowlist)
    for rel in rel_files:
        a_path = os.path.join(rev6_dir, rel)
        b_path = os.path.join(rev5_dir, rel)
        if not os.path.isfile(b_path):
            findings.append(f"{rel}：rev5 凍結樹缺此檔（例外①＝整檔拷貝、rev6 不得新增檔）")
            continue
        if not os.path.isfile(a_path):
            findings.append(f"{rel}：rev6 缺此檔（tracked 卻不在工作樹）")
            continue
        ext = os.path.splitext(rel)[1]
        a = strip_comments(open(a_path, encoding="utf-8").read(), ext)
        b = strip_comments(open(b_path, encoding="utf-8").read(), ext)
        stats["files"] += 1
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            if tag != "replace" or (i2 - i1) != (j2 - j1):
                findings.append(f"{rel}：行數差異（去註解後 rev6 第 {i1 + 1}～{i2} 行 vs rev5 第 {j1 + 1}～{j2} 行）——例外①只准逐行替換型具名差異")
                continue
            for k in range(i2 - i1):
                pair = (rel, a[i1 + k].strip(), line_hash(b[j1 + k].strip()))
                hit = next((n for n, e in enumerate(allowlist) if not consumed[n] and (e[0], e[1], e[2]) == pair), None)
                if hit is None:
                    dup = any((e[0], e[1], e[2]) == pair for e in allowlist)
                    # ★rev5 行不印原文（可能含合成機密字面）——只印雜湊；要看原文自行 diff 兩樹。
                    findings.append(f"{rel}：非 allowlist 差異{'（同形例外出現次數多於登記）' if dup else ''}：rev6「{pair[1][:80]}」 vs rev5 行雜湊 {pair[2]}")
                else:
                    consumed[hit] = True
                    stats["allow_consumed"] += 1
    for n, e in enumerate(allowlist):
        if not consumed[n]:
            findings.append(f"allowlist 漂移：{e[0]} 之具名例外已不存在（rev6「{e[1][:80]}」）——自 ALLOWLIST 移除或更新")
    return findings, stats


def run(root, rev5_root, files=None, allowlist=ALLOWLIST):
    rel_files = tracked_files(root) if files is None else list(files)
    rev6_dir = os.path.join(root, VENDORED_SUB, VENDORED_DIR)
    rev5_dir = os.path.join(rev5_root, VENDORED_SUB, VENDORED_DIR)
    return compare_tree(rev6_dir, rev5_dir, rel_files, allowlist)
