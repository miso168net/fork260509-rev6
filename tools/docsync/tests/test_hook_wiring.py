"""語料面：hook 接線機器守衛（BL-00023；承 rev5:tools/docs-sync.py TestGateWiring 乾跑案形）——讀真四檔（HOOKS 名冊＝.githooks/pre-commit／
.githooks/pre-push／.githooks-submodule/pre-push／.githooks/lib/scan-range.sh）與真 tools/bootstrap.sh，三支純函式各守一面：
①pre-commit 面 check_hook_wiring(text, codegate_tools, non_gate_tools) 逐段斷言：固定鏈（betterleaks→docsync check＋lint→staged 取得→pc_join→雙錨常數）、
八條件段（selftest-docsync／rust-fmt／wire-schema〔雙側：base-web typings 面＋rust-api 快照面〕／fork-delta／msg-key-gate／entity-drift／schema-frozen／orchestration）各自的觸發字面（同段 `if echo "$staged" | grep` 行）
與命令字面（`pc_run` 行）、`for` 自測名冊 ⊇ RUNBOOK 碼面閘表工具集 ∪ NON_GATE_TOOLS、pc_run 標籤集＝登記集（未登記段即紅＝新段須同批入本名冊）。
一正（真檔零 finding）多反（刪段／改觸發字面／抽名冊一支／改命令子命令／幽靈段／刪 pc_join→紅指名）。
②pre-push 面 check_push_hooks(outer, sub, lib)（BL-00037①；憲法 §I.8 並列為機器閘）：外層／子庫 pre-push 各三字面（source lib 相對路徑形／SCAN_CONFIG／
scan_push_ranges || exit 1）＋lib 之 betterleaks 呼叫與四種範圍推導字面；一正多反（刪任一字面→紅指名檔與字面、他檔不誤紅）。
③bootstrap 名冊面 check_bootstrap_roster(text, tracked)（BL-00037②）：推導行（含 `:(glob)` 與兩排除）／執行期非空守衛與迴圈行／docsync 三段／閘數斷言／vendored-check／Day-1 分支字面
＋推導行套 tracked 清單只得頂層檔（去 `:(glob)` 即跨層命中 tools/orchestration/assemble.py→紅）。
★hook 本體 staged 時 pre-commit 自跑 docsync test（本案隨之）；bootstrap 體檢亦跑；接線不再只靠人記得（002 刀 U0 變異實測：刪三段 lint 仍綠）。"""
import os
import re
import subprocess
import unittest

from docsync import ROOT, common, gates

# 四檔名冊（BL-00037①）：pre-commit 面＋pre-push 面三檔（外層／子庫 hook 與共用 lib）；鍵＝短名、值＝repo 相對路徑
HOOKS_REL = {
    "pre-commit": ".githooks/pre-commit",
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
    ("rust-fmt", ["-e 'rust-api'", "-e 'tools/rust-fmt-gate.py'"], 'python3 "$HOOK_DIR/../tools/rust-fmt-gate.py" check'),
    ("wire-schema", ["-e 'base-web'", "-e 'rust-api'"], 'python3 "$HOOK_DIR/../tools/wire-schema.py" check --staged-gate'),
    ("fork-delta", ["-e 'base-web'", "-e 'tools/fork-delta-lint.py'", "-e '.specify/memory/constitution.md'"], 'python3 "$HOOK_DIR/../tools/fork-delta-lint.py"'),
    ("msg-key-gate", ["-e 'rust-api'", "-e 'base-web'", "-e 'tools/msg-key-gate.py'"], 'python3 "$HOOK_DIR/../tools/msg-key-gate.py" check'),
    ("entity-drift", ["-e 'rust-api'", "-e 'docs/ops/reference-src/schema-snapshot.json'"], 'python3 "$HOOK_DIR/../tools/entity-drift-gate.py" check'),
    ("schema-frozen", ["'^(specs/001-schema-baseline/(fixtures/|data-model\\.md$)|docs/ops/reference-src/schema-definition\\.md$)'"], 'python3 "$HOOK_DIR/../tools/schema-gate.py" test'),
    ("orchestration", ["'^tools/orchestration/.*\\.(js|mjs|py)$'"], "tools/orchestration/assemble.py"),
)
ORCH_EXAMPLES = ("EXAMPLE-tdd-unitdef", "EXAMPLE-review-unitdef", "EXAMPLE-review-verify-unitdef")
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
    expected = {s[0] for s in SEGMENTS} | {"docsync-check", "docsync-lint"}
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


def check_push_hooks(outer_text, sub_text, lib_text):
    """回 findings（字串清單）；空＝pre-push 面三檔字面齊全。每條指名檔（repo 相對路徑）與字面。"""
    out = []
    for key, text in zip(PUSH_KEYS, (outer_text, sub_text, lib_text)):
        out += [f"{HOOKS_REL[key]} 缺「{label}」：{literal}" for label, literal in PUSH_LITERALS[key] if literal not in text]
    return out


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
        for label in ("rust-fmt", "wire-schema", "fork-delta", "schema-frozen", "orchestration", "selftest-docsync"):
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


class TestPushHooksWiring(unittest.TestCase):
    """pre-push 面（BL-00037①）：四檔名冊皆在檔；真三檔零 finding；刪任一字面→紅指名該檔與字面、他檔不誤紅。"""

    def test_hooks_roster_files_exist(self):
        self.assertEqual(set(HOOKS), {"pre-commit", "pre-push", "sub-pre-push", "scan-range"})
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
