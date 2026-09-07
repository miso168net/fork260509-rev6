"""語料面：pre-commit 接線機器守衛（BL-00023；承 rev5:tools/docs-sync.py TestGateWiring 乾跑案形）——讀真 .githooks/pre-commit，
純函式 check_hook_wiring(text, codegate_tools, non_gate_tools) 逐段斷言：固定鏈（betterleaks→docsync check＋lint→staged 取得→pc_join→雙錨常數）、
七條件段（selftest-docsync／rust-fmt／wire-schema〔雙側：base-web typings 面＋rust-api 快照面〕／fork-delta／entity-drift／schema-frozen／orchestration）各自的觸發字面（同段 `if echo "$staged" | grep` 行）
與命令字面（`pc_run` 行）、`for` 自測名冊 ⊇ RUNBOOK 碼面閘表工具集 ∪ NON_GATE_TOOLS、pc_run 標籤集＝登記集（未登記段即紅＝新段須同批入本名冊）。
一正（真檔零 finding）多反（刪段／改觸發字面／抽名冊一支／改命令子命令／幽靈段／刪 pc_join→紅指名）。
★hook 本體 staged 時 pre-commit 自跑 docsync test（本案隨之）；bootstrap 體檢亦跑；接線不再只靠人記得（002 刀 U0 變異實測：刪三段 lint 仍綠）。"""
import os
import re
import unittest

from docsync import ROOT, gates

HOOK = os.path.join(ROOT, ".githooks", "pre-commit")
RUNBOOK = os.path.join(ROOT, gates.RUNBOOK)

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
    ("selftest-docsync", ["'^tools/docsync/\\|^\\.githooks/pre-commit$'"], 'python3 "$HOOK_DIR/../tools/docsync" test'),
    ("rust-fmt", ["-e 'rust-api'", "-e 'tools/rust-fmt-gate.py'"], 'python3 "$HOOK_DIR/../tools/rust-fmt-gate.py" check'),
    ("wire-schema", ["-e 'base-web'", "-e 'rust-api'"], 'python3 "$HOOK_DIR/../tools/wire-schema.py" check --staged-gate'),
    ("fork-delta", ["-e 'base-web'", "-e 'tools/fork-delta-lint.py'", "-e '.specify/memory/constitution.md'"], 'python3 "$HOOK_DIR/../tools/fork-delta-lint.py"'),
    ("entity-drift", ["-e 'rust-api'", "-e 'docs/ops/reference-src/schema-snapshot.json'"], 'python3 "$HOOK_DIR/../tools/entity-drift-gate.py" check'),
    ("schema-frozen", ["'^(specs/001-schema-baseline/(fixtures/|data-model\\.md$)|docs/ops/reference-src/schema-definition\\.md$)'"], 'python3 "$HOOK_DIR/../tools/schema-gate.py" test'),
    ("orchestration", ["'^tools/orchestration/.*\\.(js|mjs|py)$'"], "tools/orchestration/assemble.py"),
)
ORCH_EXAMPLES = ("EXAMPLE-tdd-unitdef", "EXAMPLE-review-unitdef", "EXAMPLE-review-verify-unitdef")
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


def real_inputs():
    hook = open(HOOK, encoding="utf-8").read()
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


if __name__ == "__main__":
    unittest.main()
