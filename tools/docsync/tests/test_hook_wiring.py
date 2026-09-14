"""語料面：hook 接線機器守衛（BL-00023；承 rev5:tools/docs-sync.py TestGateWiring 乾跑案形）——讀真五檔（HOOKS 名冊＝.githooks/pre-commit／
.githooks/pre-push／.githooks-submodule/pre-commit／.githooks-submodule/pre-push／.githooks/lib/scan-range.sh）、真 tools/bootstrap.sh、真 README.md 與兩支雙側閘工具常數，六支純函式各守一面：
①pre-commit 面 check_hook_wiring(text, codegate_tools, non_gate_tools) 逐段斷言：固定鏈（betterleaks→docsync check＋lint→staged 取得→pc_join→雙錨常數）、
十條件段（selftest-docsync／bootstrap-roster〔tools/bootstrap.sh staged 時只跑本檔〕／rust-fmt／wire-schema〔雙側：base-web typings 面＋rust-api 快照面〕／fork-delta／msg-key-gate／
submodule-sync〔跨子庫同步律：兩子庫雙側閘閘面須無未 commit 改動（含未追蹤新檔）〕／entity-drift／schema-frozen／orchestration）各自的觸發字面（同段 `if echo "$staged" | grep` 行）
與命令字面（`pc_run` 行）、`for` 自測名冊 ⊇ RUNBOOK 碼面閘表工具集 ∪ NON_GATE_TOOLS、pc_run 標籤集＝登記集（未登記段即紅＝新段須同批入本名冊）。
一正（真檔零 finding）多反（刪段／改觸發字面／抽名冊一支／改命令子命令／幽靈段／刪 pc_join→紅指名）。
②pre-push 面 check_push_hooks(outer, sub, lib)（BL-00037①；憲法 §I.8 並列為機器閘）：外層／子庫 pre-push 各三字面（source lib 相對路徑形／SCAN_CONFIG／
scan_push_ranges || exit 1）＋lib 之 betterleaks 呼叫與四種範圍推導字面；一正多反（刪任一字面→紅指名檔與字面、他檔不誤紅）。
③bootstrap 名冊面 check_bootstrap_roster(text, tracked)（BL-00037②）：推導行（含 `:(glob)` 與兩排除）／執行期非空守衛與迴圈行／docsync 三段／閘數斷言／vendored-check／Day-1 分支字面
＋推導行套 tracked 清單只得頂層檔（去 `:(glob)` 即跨層命中 tools/orchestration/assemble.py→紅）。
④段序枚舉鏡像面 check_mirror_words(hook, readme)（BL-00055）：段名冊 MIRROR_LABELS（FIXED 之 pc_run 固定段＋SEGMENTS；hook 靜態 pc_run 標籤須 ⊆ 之）每段之字樣（MIRROR_WORDS）
須在三處人寫鏡像行（pre-commit 檔頭段序／README 樹 `.githooks/` 列／README 守門條目）各恰出現一次（ASCII 詞界計數）；一正多反（逐面×逐段刪該一處→恰一條紅指名檔、面與段／
他段夾帶→紅／路徑內嵌不計／鏡像行缺席／段未宣告字樣／hook 段未入名冊）。
⑤跨子庫同步律段閘面路徑對賬 check_sync_paths(hook, want)（BL-00057）：submodule-sync 段路徑字面集 ⇔ msg-key-gate DEFAULT_RUST／DEFAULT_LOCALES／DEFAULT_SRC（前端消費點掃描面）
∪ wire-schema TYPINGS_PATHSPECS／SNAPSHOT_PATHSPECS（正規化為 repo 根相對）；一正多反（hook 少一／多一／常數多一／段缺席）。
⑥子庫 pre-commit 面 check_sub_precommit(text)（spec-compliance-003 L3-2）：兩源倉 commit 期唯一機密掃描——betterleaks 呼叫緊接 `rc=$?`、rc 0 放行、
rc 2 命中分支、非零收尾 `exit 1`；一正多反（刪任一字面→紅指名該檔與字面）。
★hook 本體 staged 時 pre-commit 自跑 docsync test（本案隨之）；tools/bootstrap.sh staged 時 bootstrap-roster 段只跑本檔（BL-00059）；bootstrap 體檢亦跑；接線不再只靠人記得（002 刀 U0 變異實測：刪三段 lint 仍綠）。"""
import importlib.util
import os
import re
import subprocess
import unittest

from docsync import ROOT, common, gates

# 五檔名冊（BL-00037①；子庫 pre-commit＝spec-compliance-003 L3-2 補）：外層與子庫 pre-commit 面＋pre-push 面三檔（外層／子庫 hook 與共用 lib）；鍵＝短名、值＝repo 相對路徑
HOOKS_REL = {
    "pre-commit": ".githooks/pre-commit",
    "sub-pre-commit": ".githooks-submodule/pre-commit",
    "pre-push": ".githooks/pre-push",
    "sub-pre-push": ".githooks-submodule/pre-push",
    "scan-range": ".githooks/lib/scan-range.sh",
}
HOOKS = {k: os.path.join(ROOT, *rel.split("/")) for k, rel in HOOKS_REL.items()}
RUNBOOK = os.path.join(ROOT, gates.RUNBOOK)
BOOTSTRAP = os.path.join(ROOT, "tools", "bootstrap.sh")

# 固定鏈：每項一句必含字面（標籤, 字面）
FIXED = (
    ("betterleaks", 'betterleaks git --config "$HOOK_DIR/../.gitleaks.toml" --pre-commit --staged --redact --verbose --exit-code 2'),
    ("docsync-check", 'pc_run "docsync-check" python3 "$HOOK_DIR/../tools/docsync" check'),
    ("docsync-lint", 'pc_run "docsync-lint" python3 "$HOOK_DIR/../tools/docsync" lint'),
    ("staged", 'staged=$(git diff --cached --name-only)'),
    ("pc_join", "pc_join || exit 1"),
    ("warn", "PRECOMMIT_WARN_SEC=45"),
    ("fail", "PRECOMMIT_FAIL_SEC=90"),
)
# 條件段：(pc_run 標籤, 觸發字面清單〔皆須在同段 `if echo "$staged" | grep` 行〕, 命令字面〔須在 pc_run 行〕)
SEGMENTS = (
    ("selftest-docsync", ["'^tools/docsync/\\|^\\.githooks/\\|^\\.githooks-submodule/'"], 'python3 "$HOOK_DIR/../tools/docsync" test'),
    ("bootstrap-roster", ["grep -qxF -e 'tools/bootstrap.sh'"], 'python3 -m unittest discover -s "$HOOK_DIR/../tools/docsync/tests" -t "$HOOK_DIR/../tools" -p test_hook_wiring.py'),
    ("rust-fmt", ["-e 'rust-api'", "-e 'tools/rust-fmt-gate.py'"], 'python3 "$HOOK_DIR/../tools/rust-fmt-gate.py" check'),
    ("wire-schema", ["-e 'base-web'", "-e 'rust-api'"], 'python3 "$HOOK_DIR/../tools/wire-schema.py" check --staged-gate'),
    ("fork-delta", ["-e 'base-web'", "-e 'tools/fork-delta-lint.py'", "-e '.specify/memory/constitution.md'"], 'python3 "$HOOK_DIR/../tools/fork-delta-lint.py"'),
    ("msg-key-gate", ["-e 'rust-api'", "-e 'base-web'", "-e 'tools/msg-key-gate.py'"], 'python3 "$HOOK_DIR/../tools/msg-key-gate.py" check'),
    # 命令字面同時釘 LL-00012 環境剝除（unset 本機 GIT_* 名冊）與唯讀（--no-optional-locks）兩要件
    ("submodule-sync", ["-e 'rust-api'", "-e 'base-web'"], 'unset $(git rev-parse --local-env-vars); git --no-optional-locks -C "$h/../$s" status --porcelain --untracked-files=all -- $ps'),
    ("entity-drift", ["-e 'rust-api'", "-e 'docs/ops/reference-src/schema-snapshot.json'"], 'python3 "$HOOK_DIR/../tools/entity-drift-gate.py" check'),
    ("schema-frozen", ["'^(specs/001-schema-baseline/(fixtures/|data-model\\.md$)|docs/ops/reference-src/schema-definition\\.md$)'"], 'python3 "$HOOK_DIR/../tools/schema-gate.py" test'),
    ("orchestration", ["'^tools/orchestration/.*\\.(js|mjs|py)$'"], "tools/orchestration/assemble.py"),
)
ORCH_EXAMPLES = ("EXAMPLE-tdd-unitdef", "EXAMPLE-review-unitdef", "EXAMPLE-review-verify-unitdef")
# 段序枚舉鏡像面（BL-00055）：固定鏈 pc_run 段（docsync check／lint）與 SEGMENTS 每段各宣告一個「段序枚舉字樣」，須在 MIRRORS 三處人寫鏡像行各恰出現一次。
# ★字樣取法＝每段一個、三處共用（不按鏡像面分列），理由：①按面分列＝把三處散文逐字抄進本檔、成無對賬之第四份鏡像（RL-0049），
#   三處改寫措辭而段仍在時亦誤紅；②條件段字樣＝pc_run 標籤本身（三處皆逐字引用、辨識度高）；③docsync-check／docsync-lint／
#   selftest-docsync 三處措辭本不一（檔頭「docsync check」「staged 工具自測」、README 樹列「check＋lint」「條件自測」），取三處皆命中之
#   公共字樣 check／lint／自測。本腿所防＝新段落地時鏡像漏補（003 刀 U9 msg-key-gate 三處各漏一次）。
# ★恰一次、非「在場」：字樣可被他處夾帶而代為命中＝該段條目被刪仍綠（審查 r1 實證：守門條目 lint 條目內「GT-01 與 check 同源」夾帶 check；
#   檔頭 orchestration 條目內路徑 tools/orchestration/ 夾帶 orchestration）。故以 ASCII 詞界計數（mirror_word_re：前後不緊鄰 ASCII 英數／
#   `_`／`.`／`/`／`-`＝路徑與識別字內嵌不計；中文字樣前後恆非 ASCII、不受影響）並斷言恰 1——夾帶＝≥2 即紅、條目缺＝0 即紅。
#   殘餘射程：同一顆改動既刪某段條目、又在他段敘述夾帶其字樣（計數仍 1）＝substring 比對之固有邊界，由人審承接。
MIRROR_WORDS = {
    "docsync-check": "check",
    "docsync-lint": "lint",
    "selftest-docsync": "自測",
    "bootstrap-roster": "bootstrap-roster",
    "rust-fmt": "rust-fmt",
    "wire-schema": "wire-schema",
    "fork-delta": "fork-delta",
    "msg-key-gate": "msg-key-gate",
    "submodule-sync": "submodule-sync",
    "entity-drift": "entity-drift",
    "schema-frozen": "schema-frozen",
    "orchestration": "orchestration",
}
# 三處人寫鏡像：(面名, repo 相對路徑, 鏡像行起首字面)——各取首個以該字面起首之行為比對面；行缺席＝紅（掃描面空集合；RL-0051）。
MIRRORS = (
    ("檔頭段序", ".githooks/pre-commit", "# rev6 pre-commit："),
    ("樹列", "README.md", "├── .githooks/"),
    ("守門條目", "README.md", "- **守門**："),
)
# 跨子庫同步律段之閘面路徑對賬（BL-00057；閘面路徑不得成無對賬之第三份鏡像＝RL-0049）：hook submodule-sync 段 pc_run 行之單引號路徑字面集
# ⇔ 兩支雙側閘常數。★兩工具路徑基準不同、須正規化後比：msg-key-gate 之 DEFAULT_RUST／DEFAULT_LOCALES 以 os.path.join 組、相對 repo 根
# （含子庫名）；wire-schema 之 TYPINGS_PATHSPECS／SNAPSHOT_PATHSPECS 相對子庫根（`git -C <子庫>` 之 pathspec）——前者換 `/` 分隔、
# 後者前綴子庫名；hook 段字面取 repo 根相對形（段內自拆子庫名與子庫相對 pathspec）。
SYNC_LABEL = "submodule-sync"
RE_SYNC_PATH = re.compile(r"'((?:rust-api|base-web)/[^']+)'")
# pre-push 面（BL-00037①）：每檔一組必含字面（標籤, 字面）——外層／子庫 pre-push 各三（source lib 相對路徑形不同、餘同形）；
# lib＝betterleaks 呼叫（--config 顯式帶＋--redact＋--exit-code 2＋--log-opts=）＋四種範圍推導（契約表＝lib 檔頭：一般更新／新分支首推／退階／刪除分支跳過）＋入口函式
PUSH_LITERALS = {
    "pre-push": (
        ("source-lib", '. "$HOOK_DIR/lib/scan-range.sh"'),
        ("scan-config", 'SCAN_CONFIG="$HOOK_DIR/../.gitleaks.toml"'),
        ("run", "scan_push_ranges || exit 1"),
    ),
    "sub-pre-push": (
        ("source-lib", '. "$HOOK_DIR/../.githooks/lib/scan-range.sh"'),
        ("scan-config", 'SCAN_CONFIG="$HOOK_DIR/../.gitleaks.toml"'),
        ("run", "scan_push_ranges || exit 1"),
    ),
    "scan-range": (
        ("betterleaks", 'betterleaks git --config "$SCAN_CONFIG" --redact --verbose --exit-code 2 --log-opts='),
        ("一般更新", 'sr_opts="$sr_remote_oid..$sr_local_oid"'),
        ("新分支首推", 'sr_opts="$sr_local_oid --not --remotes=origin"'),
        ("退階", 'sr_opts="$sr_local_oid"'),
        ("刪除分支跳過", 'case "$sr_local_oid" in'),
        ("刪除分支跳過", "*) continue ;;"),
        ("入口", "scan_push_ranges() {"),
    ),
}
PUSH_KEYS = ("pre-push", "sub-pre-push", "scan-range")
# 子庫 pre-commit 面（spec-compliance-003 L3-2）：兩源倉 commit 期唯一機密掃描——刪 betterleaks 行則 `rc=$?` 取到 HOOK_DIR 賦值之 0、
# hook 靜默 exit 0；bootstrap hooks 指紋只比工作樹＝HEAD、commit 後即守不到。每項一句必含字面（標籤, 字面）。
SUB_PRECOMMIT_LITERALS = (
    ("betterleaks", 'betterleaks git --config "$HOOK_DIR/../.gitleaks.toml" --pre-commit --staged --redact --verbose --exit-code 2\nrc=$?'),
    ("rc0-放行", '[ "$rc" -eq 0 ] && exit 0'),
    ("rc2-命中分支", 'if [ "$rc" -eq 2 ]; then'),
    ("非零收尾", "\nexit 1"),
)
# bootstrap 名冊面（BL-00037②、003 刀 U10）：run_tool_test 名冊自 tracked 檔集推導（★裸 pathspec 的 `*` 跨 `/`——會撈進
# tools/docsync/*.py 與 tools/orchestration/*.py、後者 `assemble.py test` 回 2 即 die；`:(glob)` magic 令 `*` 不跨層）；
# 兩排除＝deploy/decrypt-secrets.py（Day-1 條件分支獨立處理）／deploy/secrets_common.py（無 `test` 子命令）。每項一句必含字面（標籤, 字面）。
BOOTSTRAP_DERIVE = ("tool_roster=\"$(git -C \"$ROOT\" ls-files ':(glob)tools/*.py' ':(glob)deploy/*.py'"
                    " | grep -v -e '^deploy/decrypt-secrets\\.py$' -e '^deploy/secrets_common\\.py$' || true)\"")
# ★執行期非空守衛與迴圈行（U10 fix 輪）：`set -euo pipefail` 下 for 字詞表內的命令替換失敗不觸發 set -e，
# 名冊推導成空集合時迴圈零圈、無訊息、rc 仍 0（＝CLAUDE.md §6 的「掃描防線就位」判準可在零自測下成立）。
# 上方 check_bootstrap_roster 的空集合判定是 Python 重算的模擬面，管不到 bootstrap 執行期真跑的那行——故兩層都要。
BOOTSTRAP_GUARD = '[ -n "$tool_roster" ] || die'
BOOTSTRAP_LOOP = 'for t in $tool_roster; do run_tool_test "$t"; done'
BOOTSTRAP_EXCLUDED = ("deploy/decrypt-secrets.py", "deploy/secrets_common.py")
BOOTSTRAP_LITERALS = (
    ("推導行", BOOTSTRAP_DERIVE),
    ("空集合守衛", BOOTSTRAP_GUARD),
    ("自測迴圈", BOOTSTRAP_LOOP),
    ("docsync-test", 'python3 "$ROOT/tools/docsync" test'),
    ("docsync-check", 'python3 "$ROOT/tools/docsync" check'),
    ("docsync-lint", 'python3 "$ROOT/tools/docsync" lint'),
    ("閘數斷言", '[ "$GATE_COUNT" = "12" ]'),
    ("vendored-check", 'python3 "$ROOT/tools/docsync" vendored-check'),
    ("Day-1 分支", "run_tool_test deploy/decrypt-secrets.py"),
)
RE_DERIVE = re.compile(r'^tool_roster="\$\(git -C "\$ROOT" ls-files (.+?) \| grep -v (.+?) \|\| true\)"$', re.M)
ENTITY_DRIFT_ABSENT = "schema-snapshot.json 缺席"
RE_PC_RUN = re.compile(r'pc_run "([^"]+)"')
RE_FOR = re.compile(r"^for t in (.+); do\s*$", re.M)
RE_TRIGGER = re.compile(r'^\s*if echo "\$staged" \| grep')


def check_hook_wiring(text, codegate_tools, non_gate_tools):
    """回 findings（字串清單）；空＝接線與登記名冊全等。"""
    out = []
    lines = text.split("\n")
    for label, literal in FIXED:
        if literal not in text:
            out.append(f"固定鏈缺「{label}」：{literal}")
    labels = RE_PC_RUN.findall(text)
    expected = set(MIRROR_LABELS)
    # for 迴圈的動態標籤 `selftest-$(basename "$t" .py)`：正則在內層引號截斷成 `selftest-$(basename `，以前綴辨識、不入未登記判定。
    for lab in sorted(set(labels) - expected):
        if lab.startswith("selftest-$("):
            continue
        out.append(f"未登記段 {lab}：pc_run 標籤不在接線名冊（新段須同批入 test_hook_wiring SEGMENTS）")
    for label, triggers, cmd in SEGMENTS:
        idx = [i for i, ln in enumerate(lines) if f'pc_run "{label}"' in ln and not ln.lstrip().startswith("#")]
        if not idx:
            out.append(f"缺段 {label}：無 pc_run \"{label}\" 行")
            continue
        if not any(cmd in lines[i] for i in idx):
            out.append(f"段 {label} 命令字面不符：須含 {cmd}")
        trig = None
        for back in range(idx[0], max(-1, idx[0] - 8), -1):
            if RE_TRIGGER.match(lines[back]):
                trig = lines[back]
                break
        if trig is None:
            out.append(f"段 {label} 缺條件觸發行（if echo \"$staged\" | grep …）")
            continue
        for t in triggers:
            if t not in trig:
                out.append(f"段 {label} 觸發字面缺 {t}")
    if ENTITY_DRIFT_ABSENT not in text:
        out.append(f"段 entity-drift 缺快照缺席分支（{ENTITY_DRIFT_ABSENT}）")
    for ex in ORCH_EXAMPLES:
        if ex not in text:
            out.append(f"段 orchestration 缺範例 {ex}")
    m = RE_FOR.search(text)
    if not m:
        out.append("缺 for 自測名冊行（for t in …; do）")
    else:
        roster = set(m.group(1).split())
        for t in sorted((set(codegate_tools or ()) | set(non_gate_tools or ())) - roster):
            out.append(f"for 自測名冊缺 {t}（碼面閘表∪NON_GATE_TOOLS 之成員）")
        if 'grep -qxF "$t"' not in text or 'python3 "$HOOK_DIR/../$t" test' not in text:
            out.append("for 自測迴圈本體缺 staged 精確比對或 test 命令字面")
    return out


# 鏡像腿段名冊（BL-00055）＝FIXED 內 pc_run 字面之標籤（固定鏈）＋SEGMENTS 標籤：單一推導，check_mirror_words 與其測試皆讀此、不另抄標籤字面。
FIXED_PC_LABELS = tuple(m.group(1) for m in (RE_PC_RUN.match(lit) for _, lit in FIXED) if m)
MIRROR_LABELS = FIXED_PC_LABELS + tuple(s[0] for s in SEGMENTS)


def mirror_word_re(word):
    """段序枚舉字樣之 ASCII 詞界正則（取法理由見 MIRROR_WORDS 上方註）。"""
    return re.compile(r"(?<![A-Za-z0-9_./-])" + re.escape(word) + r"(?![A-Za-z0-9_./-])")


def check_mirror_words(hook_text, readme_text, words=MIRROR_WORDS):
    """回 findings（字串清單）；空＝hook 靜態 pc_run 標籤 ⊆ 段名冊 MIRROR_LABELS、名冊每段皆宣告字樣、且字樣在三處鏡像行各恰出現一次。每條指名檔（repo 相對路徑）、面與段。"""
    labels = MIRROR_LABELS
    # hook 實際 pc_run 標籤反查段名冊：未入 FIXED／SEGMENTS 之段＝本腿不會要求其字樣、三處漏補照樣綠，故當場紅；標籤含 `$(`＝for 迴圈動態標籤、不計。
    out = [f".githooks/pre-commit 之 pc_run 段 {lab} 不在鏡像腿段名冊（無條件段須入 FIXED、條件段須入 SEGMENTS，並同批宣告 MIRROR_WORDS）"
           for lab in sorted(set(RE_PC_RUN.findall(hook_text)) - set(labels)) if "$(" not in lab]
    out += [f"段 {lab} 未宣告段序枚舉字樣（新段須同批入 test_hook_wiring MIRROR_WORDS）" for lab in labels if lab not in words]
    out += [f"MIRROR_WORDS 登記了非段 {lab}（FIXED 之 pc_run 段∪SEGMENTS 之外）" for lab in sorted(set(words) - set(labels))]
    texts = {".githooks/pre-commit": hook_text, "README.md": readme_text}
    for face, rel, prefix in MIRRORS:
        line = next((ln for ln in texts[rel].split("\n") if ln.startswith(prefix)), None)
        if line is None:
            out.append(f"{rel} 缺鏡像行（{face}：以「{prefix}」起首）")
            continue
        for lab in labels:
            if lab not in words:
                continue
            n = len(mirror_word_re(words[lab]).findall(line))
            if n == 0:
                out.append(f"{rel} 之{face}缺段 {lab}（字樣「{words[lab]}」；三處鏡像須同批補齊）")
            elif n > 1:
                out.append(f"{rel} 之{face}段 {lab} 字樣「{words[lab]}」出現 {n} 次（須恰 1：他段敘述夾帶該字樣＝該段條目被刪時由夾帶處代為命中之假綠；改寫夾帶處）")
    return out


def load_tool(name):
    """工具檔名含連字號（CLI、不可 import）——依路徑以 spec_from_file_location 載入 tools/<name>.py，只讀其模組層常數。"""
    spec = importlib.util.spec_from_file_location("_hook_wiring_" + name.replace("-", "_"), os.path.join(ROOT, "tools", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gate_face_paths(msg_key_gate, wire_schema):
    """兩雙側閘常數 → repo 根相對、`/` 分隔之閘面路徑集（正規化理由見 SYNC_LABEL 上方註）。"""
    return ({p.replace(os.sep, "/") for p in (msg_key_gate.DEFAULT_RUST, msg_key_gate.DEFAULT_LOCALES, msg_key_gate.DEFAULT_SRC)}
            | {"base-web/" + p for p in wire_schema.TYPINGS_PATHSPECS}
            | {"rust-api/" + p for p in wire_schema.SNAPSHOT_PATHSPECS})


def check_sync_paths(hook_text, want):
    """回 findings（字串清單）；空＝hook submodule-sync 段路徑字面集 ＝ want（兩工具常數正規化集）。段缺席或字面集為空＝紅。"""
    lines = [ln for ln in hook_text.split("\n") if f'pc_run "{SYNC_LABEL}"' in ln and not ln.lstrip().startswith("#")]
    got = set(RE_SYNC_PATH.findall("\n".join(lines)))
    if not got:
        return [f"段 {SYNC_LABEL} 閘面路徑字面集為空（段缺席或無 '<子庫>/<路徑>' 引數；掃描面空集合即紅＝RL-0051）"]
    return ([f"段 {SYNC_LABEL} 缺閘面路徑 {p}（兩雙側閘常數有、hook 段無）" for p in sorted(want - got)]
            + [f"段 {SYNC_LABEL} 多閘面路徑 {p}（hook 段有、兩雙側閘常數無）" for p in sorted(got - want)])


def check_push_hooks(outer_text, sub_text, lib_text):
    """回 findings（字串清單）；空＝pre-push 面三檔字面齊全。每條指名檔（repo 相對路徑）與字面。"""
    out = []
    for key, text in zip(PUSH_KEYS, (outer_text, sub_text, lib_text)):
        out += [f"{HOOKS_REL[key]} 缺「{label}」：{literal}" for label, literal in PUSH_LITERALS[key] if literal not in text]
    return out


def check_sub_precommit(text):
    """回 findings（字串清單）；空＝子庫 pre-commit 必含字面齊全。每條指名檔（repo 相對路徑）與字面。"""
    return [f"{HOOKS_REL['sub-pre-commit']} 缺「{label}」：{literal}" for label, literal in SUB_PRECOMMIT_LITERALS if literal not in text]


def real_push_texts():
    """依 HOOKS 名冊讀 pre-push 面三檔（名冊少列任一鍵＝KeyError 紅、非 vacuous 綠）。"""
    out = []
    for k in PUSH_KEYS:
        with open(HOOKS[k], encoding="utf-8") as f:
            out.append(f.read())
    return tuple(out)


def _pathspec_re(spec):
    """git pathspec → 全匹配正則：`:(glob)` magic 下 `*` 不跨 `/`（fnmatch 語意）；裸 pathspec 的 `*` 跨 `/`（git 預設 wildmatch）。"""
    glob = spec.startswith(":(glob)")
    pat = spec[len(":(glob)"):] if glob else spec
    out = ""
    for ch in pat:
        out += ("[^/]*" if glob else ".*") if ch == "*" else ("[^/]" if glob else ".") if ch == "?" else re.escape(ch)
    return re.compile("^" + out + "$")


def simulate_roster(derive_line, tracked):
    """把推導行套在一份 tracked 清單上（純函式、不呼 git）：ls-files pathspec 聯集 → grep -v 各 -e 排除；回排序後名冊。"""
    m = RE_DERIVE.match(derive_line)
    assert m, derive_line
    specs = re.findall(r"'([^']+)'", m.group(1))
    excludes = [re.compile(e) for e in re.findall(r"-e '([^']+)'", m.group(2))]
    res = [_pathspec_re(sp) for sp in specs]
    return sorted(p for p in tracked if any(r.match(p) for r in res) and not any(e.search(p) for e in excludes))


def check_bootstrap_roster(text, tracked):
    """回 findings（字串清單）；空＝名冊面字面齊全，且推導行套在 tracked 上只得 tools/／deploy/ 頂層檔、不含兩排除項、非空。"""
    out = [f"bootstrap 名冊面缺「{label}」：{literal}" for label, literal in BOOTSTRAP_LITERALS if literal not in text]
    m = RE_DERIVE.search(text)
    if not m:
        return out + ["bootstrap 缺推導行（tool_roster=\"$(git -C \"$ROOT\" ls-files … | grep -v … || true)\"）"]
    roster = simulate_roster(m.group(0), tracked)
    if not roster:
        out.append("推導名冊為空集合（掃描面空集合即紅；RL-0051）")
    out += [f"推導名冊跨層命中 {p}（pathspec `*` 跨 `/`——ls-files 須帶 `:(glob)`）" for p in roster if p.count("/") != 1]
    out += [f"推導名冊含應排除項 {p}（Day-1 分支獨立處理／無 test 子命令）" for p in roster if p in BOOTSTRAP_EXCLUDED]
    return out


def real_inputs():
    hook = open(HOOKS["pre-commit"], encoding="utf-8").read()
    runbook = open(RUNBOOK, encoding="utf-8").read()
    return hook, gates.runbook_codegate_tools(runbook), set(gates.NON_GATE_TOOLS)


class TestHookWiring(unittest.TestCase):
    def test_real_hook_green(self):
        hook, cg, ng = real_inputs()
        self.assertTrue(cg, "RUNBOOK 碼面閘表工具集不得為空（掃描面空集合）")
        self.assertEqual(check_hook_wiring(hook, cg, ng), [])

    def test_deleted_segment_red(self):
        hook, cg, ng = real_inputs()
        for label, *_ in SEGMENTS:
            mutated = "\n".join(ln for ln in hook.split("\n") if f'pc_run "{label}"' not in ln)
            msgs = " ".join(check_hook_wiring(mutated, cg, ng))
            self.assertIn(label, msgs, f"刪 {label} 段須紅指名")

    def test_trigger_literal_red(self):
        hook, cg, ng = real_inputs()
        mutated = hook.replace("-e 'docs/ops/reference-src/schema-snapshot.json'", "-e 'docs/ops/reference-src/schema-snapshot.jsonx'", 1)
        msgs = " ".join(check_hook_wiring(mutated, cg, ng))
        self.assertIn("entity-drift", msgs)
        self.assertIn("schema-snapshot.json", msgs)
        mutated2 = hook.replace("'^tools/orchestration/.*\\.(js|mjs|py)$'", "'^tools/orchestration/.*\\.(js|mjs)$'", 1)
        self.assertIn("orchestration", " ".join(check_hook_wiring(mutated2, cg, ng)))
        # ★BL-00037③ 雙側觸發：抽掉 wire-schema 段的快照側字面須紅指名（單側回頭＝快照改動零觸發）。
        mutated3 = hook.replace("grep -qxF -e 'base-web' -e 'rust-api'", "grep -qxF -e 'base-web'", 1)
        msgs3 = " ".join(check_hook_wiring(mutated3, cg, ng))
        self.assertIn("wire-schema", msgs3)
        self.assertIn("rust-api", msgs3)

    def test_roster_member_removed_red(self):
        hook, cg, ng = real_inputs()
        mutated = hook.replace(" tools/wire-schema.py ", " ", 1)
        self.assertIn("tools/wire-schema.py", " ".join(check_hook_wiring(mutated, cg, ng)))
        mutated2 = hook.replace(" tools/wf-watchdog.py ", " ", 1)
        self.assertIn("tools/wf-watchdog.py", " ".join(check_hook_wiring(mutated2, cg, ng)))

    def test_command_subcommand_red(self):
        hook, cg, ng = real_inputs()
        mutated = hook.replace('pc_run "schema-frozen" python3 "$HOOK_DIR/../tools/schema-gate.py" test', 'pc_run "schema-frozen" python3 "$HOOK_DIR/../tools/schema-gate.py" check', 1)
        self.assertIn("schema-frozen", " ".join(check_hook_wiring(mutated, cg, ng)))

    def test_ghost_segment_and_missing_join_red(self):
        hook, cg, ng = real_inputs()
        mutated = hook.replace("pc_join || exit 1", 'pc_run "ghost" true\npc_join || exit 1', 1)
        self.assertIn("未登記段 ghost", " ".join(check_hook_wiring(mutated, cg, ng)))
        mutated2 = hook.replace("pc_join || exit 1", "", 1)
        self.assertIn("pc_join", " ".join(check_hook_wiring(mutated2, cg, ng)))


def real_mirror_texts():
    with open(HOOKS["pre-commit"], encoding="utf-8") as f:
        hook = f.read()
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
        return hook, f.read()


class TestMirrorWords(unittest.TestCase):
    """段序枚舉鏡像面（BL-00055）：真檔零 finding；逐面×逐段刪該唯一一處字樣→恰一條紅指名該檔、該面與該段（同檔另一面與他檔不誤紅）；
    他段敘述夾帶字樣→紅（出現 2 次）；路徑／識別字內嵌不計；鏡像行缺席→紅；段未宣告字樣→紅指名該段；hook 有未入段名冊之 pc_run 段→紅指名。"""

    def _line(self, text, prefix):
        return next(ln for ln in text.split("\n") if ln.startswith(prefix))

    def test_real_mirrors_green(self):
        self.assertTrue(FIXED_PC_LABELS, "FIXED 推導之 pc_run 固定段為空集合（鏡像腿漏掃固定鏈；RL-0051）")
        self.assertEqual(FIXED_PC_LABELS, tuple(lab for lab, lit in FIXED if lit.startswith("pc_run ")), "FIXED 標籤欄須＝其 pc_run 字面標籤")
        self.assertEqual(set(MIRROR_WORDS), set(MIRROR_LABELS))
        self.assertEqual(check_mirror_words(*real_mirror_texts()), [])

    def test_each_word_removed_red_names_file_face_segment(self):
        hook, readme = real_mirror_texts()
        for face, rel, prefix in MIRRORS:
            for lab, word in MIRROR_WORDS.items():
                texts = {".githooks/pre-commit": hook, "README.md": readme}
                line = self._line(texts[rel], prefix)
                pat = mirror_word_re(word)
                self.assertEqual(len(pat.findall(line)), 1, (face, lab))
                texts[rel] = texts[rel].replace(line, pat.sub("", line, count=1), 1)   # 只刪一處（恰一次已由上行斷言）
                msgs = check_mirror_words(texts[".githooks/pre-commit"], texts["README.md"])
                self.assertEqual(len(msgs), 1, (face, lab, msgs))
                self.assertTrue(msgs[0].startswith(rel + " ") and face in msgs[0] and f"缺段 {lab}" in msgs[0], (face, lab, msgs))

    def test_carried_word_red(self):
        """夾帶反例（審查 r1 實證形）：守門條目 lint 條目內寫「與 check 同源」＝刪 docsync check 條目仍由夾帶處命中之假綠——須在夾帶當下即紅。"""
        hook, readme = real_mirror_texts()
        carried = readme.replace("`docsync lint`（", "`docsync lint`（與 check 同源；", 1)
        self.assertNotEqual(carried, readme)
        msgs = check_mirror_words(hook, carried)
        self.assertEqual(len(msgs), 1, msgs)
        self.assertTrue(msgs[0].startswith("README.md ") and "守門條目" in msgs[0] and "段 docsync-check" in msgs[0] and "出現 2 次" in msgs[0], msgs)
        carried2 = hook.replace("submodule-sync（", "submodule-sync（同 msg-key-gate 讀工作樹；", 1)
        self.assertNotEqual(carried2, hook)
        msgs2 = check_mirror_words(carried2, readme)
        self.assertEqual(len(msgs2), 1, msgs2)
        self.assertTrue(msgs2[0].startswith(".githooks/pre-commit ") and "檔頭段序" in msgs2[0] and "段 msg-key-gate" in msgs2[0] and "出現 2 次" in msgs2[0], msgs2)

    def test_path_or_identifier_embedding_not_counted(self):
        hook, readme = real_mirror_texts()
        embedded = readme.replace("→條件自測→", "→條件自測（tools/msg-key-gate.py、fork-delta-lint、wire-schema.json）→", 1)
        self.assertNotEqual(embedded, readme)
        self.assertEqual(check_mirror_words(hook, embedded), [])

    def test_unlisted_hook_segment_red(self):
        hook, readme = real_mirror_texts()
        mutated = hook.replace("pc_join || exit 1", 'pc_run "ghost-fixed" true\npc_join || exit 1', 1)
        msgs = check_mirror_words(mutated, readme)
        self.assertTrue(any(m.startswith(".githooks/pre-commit ") and "ghost-fixed" in m and "不在鏡像腿段名冊" in m for m in msgs), msgs)

    def test_mirror_line_absent_red(self):
        hook, readme = real_mirror_texts()
        msgs = check_mirror_words(hook.replace("# rev6 pre-commit：", "# rev6 hook：", 1), readme)
        self.assertTrue(any(m.startswith(".githooks/pre-commit ") and "檔頭段序" in m and "缺鏡像行" in m for m in msgs), msgs)
        msgs2 = check_mirror_words(hook, readme.replace("- **守門**：", "- **守衛**：", 1))
        self.assertTrue(any(m.startswith("README.md ") and "守門條目" in m and "缺鏡像行" in m for m in msgs2), msgs2)

    def test_undeclared_word_red(self):
        words = {k: v for k, v in MIRROR_WORDS.items() if k != "orchestration"}
        msgs = check_mirror_words(*real_mirror_texts(), words=words)
        self.assertTrue(any("orchestration" in m and "未宣告" in m for m in msgs), msgs)


class TestSubmoduleSyncPaths(unittest.TestCase):
    """跨子庫同步律段閘面路徑對賬（BL-00057）：真 hook 段字面集 ＝ 兩雙側閘常數正規化集（一正）；hook 少一／多一／工具常數多一／段缺席→紅指名（多反）。"""

    def _real(self):
        with open(HOOKS["pre-commit"], encoding="utf-8") as f:
            hook = f.read()
        msg, wire = load_tool("msg-key-gate"), load_tool("wire-schema")
        # 正規化前提實證：msg-key-gate 常數帶子庫名（repo 根相對）、wire-schema 常數不帶（子庫根相對）
        self.assertTrue(msg.DEFAULT_RUST.startswith("rust-api" + os.sep) and msg.DEFAULT_LOCALES.startswith("base-web" + os.sep))
        self.assertFalse(any(p.startswith(("rust-api/", "base-web/")) for p in wire.TYPINGS_PATHSPECS + wire.SNAPSHOT_PATHSPECS))
        return hook, gate_face_paths(msg, wire)

    def test_real_paths_match_tool_constants(self):
        hook, want = self._real()
        self.assertTrue(any(p.startswith("rust-api/") for p in want) and any(p.startswith("base-web/") for p in want), want)
        self.assertEqual(check_sync_paths(hook, want), [])

    def test_path_drift_red(self):
        hook, want = self._real()
        dropped = hook.replace(" 'base-web/src/typings/api'", "", 1)
        self.assertNotEqual(dropped, hook)
        self.assertIn(f"段 {SYNC_LABEL} 缺閘面路徑 base-web/src/typings/api（兩雙側閘常數有、hook 段無）", check_sync_paths(dropped, want))
        extra = hook.replace(" 'rust-api/server/src/error.rs'", " 'rust-api/server/src/error.rs' 'rust-api/server/src/lib.rs'", 1)
        self.assertIn(f"段 {SYNC_LABEL} 多閘面路徑 rust-api/server/src/lib.rs（hook 段有、兩雙側閘常數無）", check_sync_paths(extra, want))
        self.assertIn(f"段 {SYNC_LABEL} 缺閘面路徑 base-web/src/typings/app.d.ts（兩雙側閘常數有、hook 段無）",
                      check_sync_paths(hook, want | {"base-web/src/typings/app.d.ts"}))
        gone = "\n".join(ln for ln in hook.split("\n") if f'pc_run "{SYNC_LABEL}"' not in ln)
        self.assertTrue(any("字面集為空" in m for m in check_sync_paths(gone, want)))


class TestPushHooksWiring(unittest.TestCase):
    """pre-push 面（BL-00037①）：五檔名冊皆在檔；真三檔零 finding；刪任一字面→紅指名該檔與字面、他檔不誤紅。"""

    def test_hooks_roster_files_exist(self):
        self.assertEqual(set(HOOKS), {"pre-commit", "sub-pre-commit", "pre-push", "sub-pre-push", "scan-range"})
        for k, path in HOOKS.items():
            self.assertTrue(os.path.isfile(path), (k, path))

    def test_real_push_hooks_green(self):
        self.assertEqual(check_push_hooks(*real_push_texts()), [])

    def test_each_literal_removed_red_names_file_and_literal(self):
        texts = dict(zip(PUSH_KEYS, real_push_texts()))
        for key, pairs in PUSH_LITERALS.items():
            for label, literal in pairs:
                self.assertIn(literal, texts[key], (key, label))
                mutated = dict(texts, **{key: texts[key].replace(literal, "")})
                msgs = check_push_hooks(*(mutated[k] for k in PUSH_KEYS))
                self.assertTrue(any(m.startswith(HOOKS_REL[key] + " 缺") and literal in m for m in msgs), (key, label, msgs))
                self.assertFalse(any(m.startswith(HOOKS_REL[o] + " 缺") for o in PUSH_KEYS if o != key for m in msgs), (key, label, msgs))


class TestSubPrecommitWiring(unittest.TestCase):
    """子庫 pre-commit 面（spec-compliance-003 L3-2）：真檔零 finding；刪任一字面→紅指名該檔與字面。"""

    def _text(self):
        with open(HOOKS["sub-pre-commit"], encoding="utf-8") as f:
            return f.read()

    def test_real_sub_precommit_green(self):
        self.assertEqual(check_sub_precommit(self._text()), [])

    def test_each_literal_removed_red_names_file_and_literal(self):
        text = self._text()
        for label, literal in SUB_PRECOMMIT_LITERALS:
            self.assertIn(literal, text, label)
            msgs = check_sub_precommit(text.replace(literal, "", 1))
            self.assertTrue(any(m.startswith(".githooks-submodule/pre-commit 缺") and literal in m for m in msgs), (label, msgs))


class TestBootstrapRoster(unittest.TestCase):
    """bootstrap 名冊面（BL-00037②）：讀真 tools/bootstrap.sh——推導行（含 `:(glob)` 與兩排除）／執行期非空守衛／自測迴圈行／
    docsync 三段／閘數斷言／vendored-check／Day-1 分支九字面刪一即紅指名；反例＝推導行去 `:(glob)` 套合成 tracked 清單→名冊多出 tools/orchestration/assemble.py→紅指名；
    DoD 等式（RL-0026 處數由等式釘、不寫死支數）＝推導名冊 ≡ `git ls-files ':(glob)tools/*.py' ':(glob)deploy/*.py'` 去兩排除項。"""

    SYNTH = ["deploy/backup-db.py", "deploy/decrypt-secrets.py", "deploy/secrets_common.py",
             "tools/wf-watchdog.py", "tools/docsync/book.py", "tools/orchestration/assemble.py", "tools/docsync/tests/test_gates.py"]

    def _text(self):
        with open(BOOTSTRAP, encoding="utf-8") as f:
            return f.read()

    def _ls(self, *specs):
        return subprocess.run(["git", "-C", ROOT, "ls-files", *specs], capture_output=True, text=True, check=True).stdout.split()

    def test_real_bootstrap_green(self):
        self.assertEqual(check_bootstrap_roster(self._text(), common.Ctx(ROOT).tracked), [])

    def test_real_roster_equation(self):
        """推導名冊 ＝ git ls-files 兩 `:(glob)` pathspec 之全集去兩排除項（同時釘住「裸 `*` 跨 `/`」的根因主張）。"""
        tracked = common.Ctx(ROOT).tracked
        line = RE_DERIVE.search(self._text()).group(0)
        want = sorted(set(self._ls(":(glob)tools/*.py", ":(glob)deploy/*.py")) - set(BOOTSTRAP_EXCLUDED))
        self.assertTrue(want, "名冊空集合")
        self.assertEqual(simulate_roster(line, tracked), want)
        self.assertTrue(all(p.count("/") == 1 and p.endswith(".py") for p in want), want)
        bare = simulate_roster(line.replace(":(glob)", ""), tracked)
        self.assertEqual(bare, sorted(set(self._ls("tools/*.py", "deploy/*.py")) - set(BOOTSTRAP_EXCLUDED)))
        self.assertIn("tools/orchestration/assemble.py", bare)

    def test_each_literal_removed_red(self):
        text, tracked = self._text(), common.Ctx(ROOT).tracked
        for label, literal in BOOTSTRAP_LITERALS:
            self.assertIn(literal, text, label)
            msgs = " ".join(check_bootstrap_roster(text.replace(literal, ""), tracked))   # 全數刪（閘數斷言字面在 warn／ok 兩行各一）
            self.assertIn(label, msgs, f"刪「{label}」須紅指名")

    def test_derive_without_glob_names_nested_tool_red(self):
        text = self._text()
        self.assertEqual(check_bootstrap_roster(text, self.SYNTH), [])
        line = RE_DERIVE.search(text).group(0)
        self.assertEqual(simulate_roster(line, self.SYNTH), ["deploy/backup-db.py", "tools/wf-watchdog.py"])
        msgs = check_bootstrap_roster(text.replace(line, line.replace(":(glob)", ""), 1), self.SYNTH)
        self.assertTrue(any("tools/orchestration/assemble.py" in m and "跨層" in m for m in msgs), msgs)
        self.assertTrue(any("tools/docsync/book.py" in m for m in msgs), msgs)

    def test_excluded_item_leaking_into_roster_red(self):
        text = self._text()
        line = RE_DERIVE.search(text).group(0)
        loosened = line.replace(" -e '^deploy/secrets_common\\.py$'", "")
        msgs = check_bootstrap_roster(text.replace(line, loosened, 1), self.SYNTH)
        self.assertTrue(any("deploy/secrets_common.py" in m and "應排除" in m for m in msgs), msgs)


if __name__ == "__main__":
    unittest.main()
