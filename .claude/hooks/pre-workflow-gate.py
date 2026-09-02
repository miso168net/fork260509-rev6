#!/usr/bin/env python3
"""PreToolUse(Workflow) 閘：script 缺 zh-TW 書面強制令、或缺／錯 RULES-VERSION → 擋下（exit 2、stderr 回饋）。

腿①（承 rev4:L-113、rev5 防呆①②）：sub-agent 不繼承主線 CLAUDE.md／session 語言紀律，未明令即預設英文
寫 report/blocker/程式碼註解——強制令必須逐字烤進 script 本體，本 hook 為機器兜底。
腿②（rev6 §3.6、R2-F21；user 拍板：所有 Workflow script 一律必帶）：規則塊由 `python3 tools/docsync rules emit`
產出、末行 `RULES-VERSION: <sha256 前 12>`；本 hook 自 script 抽該串並與 docs/ops/RULES.md 現算值比對——
純字面斷言只證明有人打了那串字，對賬才證明規則塊是現行版。不符＝規則層已更新而骨架仍舊 → 擋。
以 {name:...} 呼叫之預存 workflow 無 script 可驗→放行；輸入異常不擋（fail-open：本閘是兜底、非唯一防線）。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RE_VERSION = re.compile(r"RULES-VERSION:\s*([0-9a-f]{12})")


def current_rules_version():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from docsync import RULES, rules  # noqa: E402
    with open(os.path.join(ROOT, RULES), encoding="utf-8") as f:
        return rules.rules_version(f.read())


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    ti = data.get("tool_input") or {}
    content = ti.get("script") or ""
    sp = ti.get("scriptPath")
    if not content and sp and os.path.isfile(sp):
        try:
            with open(sp, encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            return 0
    if not content:
        return 0
    if "zh-TW" not in content:
        sys.stderr.write(
            "[pre-workflow-gate] Workflow script 缺 zh-TW 書面強制令（CLAUDE.md §2 防呆①②、rev4:L-113）。"
            "把『★書面產物（report／blocker／程式碼註解／文件）一律 zh-TW』烤進每支 agent prompt 的不可違反項後再發射。"
        )
        return 2
    found = set(RE_VERSION.findall(content))
    if not found:
        sys.stderr.write(
            "[pre-workflow-gate] Workflow script 缺 RULES-VERSION（RL-0058／§3.6）：規則塊須由 "
            "`python3 tools/docsync rules emit --scope implementer` 產出並整塊烤進 script（末行 RULES-VERSION: <12hex>）；"
            "編排骨架用 `python3 tools/docsync generate` 重算 tools/orchestration/_sk_rules.js 後重組。所有 Workflow script 一律必帶。"
        )
        return 2
    try:
        cur = current_rules_version()
    except Exception as ex:
        sys.stderr.write(f"[pre-workflow-gate] RULES-VERSION 現算失敗（{ex}）——docs/ops/RULES.md 或 tools/docsync 異常，先跑 bash tools/bootstrap.sh")
        return 2
    if found != {cur}:
        sys.stderr.write(
            f"[pre-workflow-gate] RULES-VERSION 不符：script 帶 {sorted(found)}、RULES.md 現算 {cur}——規則層已更新而骨架仍舊；"
            "跑 `python3 tools/docsync generate` 重算 _sk_rules.js 後重組 script（或以 rules emit 重貼規則塊）再發射。"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
