#!/usr/bin/env python3
"""tools/orchestration/assemble.py — Workflow script 組裝器（BL-00001 單一骨架；BL-00006 自 tmp/001-assemble.py 入庫並加 review 模式）。
用法：python3 tools/orchestration/assemble.py <unitdef.py> <out.mjs>

unitdef.py＝python 模組，以字串常數給各變動段的 JS 原文：
  共同：MODE（'tdd' 預設｜'review'）、VARS（meta＋UNIT／FEATURE／SMOKE／START_LOG＋模式常數）、CONTEXT、可選 RESIDUE（不得殘留字樣清單）
  tdd  ：IMPLEMENTERS 住 VARS；ALLOWED（ALLOWED_BLOCK）、PROMPTS（IMPL_STAGES／SPEC_REVIEW_PROMPT／QUALITY_REVIEW_PROMPT／FIX_SELFCHECK）
         拼接序＝vars + head + allowed + rules + context + prompts + cycle + main
  review：REVIEW_STAGE／INLINE_VERIFY／FINDING_CATEGORIES 住 VARS；PLAN（LENSES／PROBES 或 BATCHES／PROBES／CRITIC）；CONTEXT 另含 DECISIONS_BLOCK
         拼接序＝vars + plan + head + rules + context + review（★plan 先於 head＝保險絲據其常數推導）
拼完三道（任一紅＝非零退出、不留產物）：
  ①RULES-VERSION 對賬（script 內每個版本串＝rules emit 現算；同 .claude/hooks/pre-workflow-gate.py 判準）＋zh-TW 字面＋RESIDUE 殘留
  ②node --check（包 async fn、export const meta→const meta）
  ③harness：tdd＝harness-test.mjs spec＋quality 雙模式；review＝harness-review.mjs（六案）
"""
import importlib.util
import os
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent

TDD_ORDER = ('VARS', '_sk_head.js', 'ALLOWED', '_sk_rules.js', 'CONTEXT', 'PROMPTS', '_sk_cycle.js', '_sk_main.js')
REVIEW_ORDER = ('VARS', 'PLAN', '_sk_head.js', '_sk_rules.js', 'CONTEXT', '_sk_review.js')


def load(path):
    spec = importlib.util.spec_from_file_location('unitdef', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sh(cmd, **kw):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, **kw)


def segments(u, mode):
    order = REVIEW_ORDER if mode == 'review' else TDD_ORDER
    out = []
    for name in order:
        if name.startswith('_sk_'):
            out.append((HERE / name).read_text(encoding='utf-8'))
        else:
            seg = getattr(u, name, None)
            if not isinstance(seg, str) or not seg.strip():
                raise SystemExit(f'✗ unitdef 缺 {name} 段（{mode} 模式必填、非空字串）')
            out.append(seg)
    return out


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    u = load(sys.argv[1])
    out = pathlib.Path(sys.argv[2])
    mode = getattr(u, 'MODE', 'tdd')
    if mode not in ('tdd', 'review'):
        print(f'✗ MODE 須為 tdd 或 review（現值 {mode!r}）')
        return 1
    script = '\n\n'.join(s.rstrip('\n') for s in segments(u, mode)) + '\n'
    # ① RULES-VERSION 對賬（同 .claude/hooks/pre-workflow-gate.py 判準）＋zh-TW＋殘留字樣
    cur = sh('python3 tools/docsync rules emit --scope implementer').stdout.rstrip('\n').splitlines()[-1].split()[-1]
    found = set(re.findall(r'RULES-VERSION:\s*([0-9a-f]{12})', script))
    if found != {cur}:
        print(f'✗ RULES-VERSION 不符：script {sorted(found)}、現算 {cur}——先 python3 tools/docsync generate')
        return 1
    if 'zh-TW' not in script:
        print('✗ 缺 zh-TW 字面')
        return 1
    for pat in getattr(u, 'RESIDUE', []):
        if pat in script:
            print(f'✗ 殘留字樣：{pat!r}')
            return 1
    # ② 語法
    with tempfile.NamedTemporaryFile('w', suffix='.mjs', delete=False, encoding='utf-8') as f:
        f.write('(async function (phase, log, parallel, pipeline, agent, args) {\n' + script.replace('export const meta', 'const meta', 1) + '\n})\n')
        tmp = f.name
    r = sh(f'node --check {tmp}')
    os.unlink(tmp)
    if r.returncode != 0:
        print('✗ node --check：\n' + r.stderr[-1500:])
        return 1
    out.write_text(script, encoding='utf-8')
    # ③ harness（模式對應）
    runs = [f'node tools/orchestration/harness-test.mjs {out} {tag}' for tag in ('spec', 'quality')] if mode == 'tdd' \
        else [f'node tools/orchestration/harness-review.mjs {out}']
    for cmd in runs:
        r = sh(cmd)
        last = (r.stdout.strip().splitlines() or [''])[-1]
        if r.returncode != 0:
            print(r.stdout[-3000:])
            print(f'✗ harness rc={r.returncode}：{cmd}')
            out.unlink(missing_ok=True)
            return 1
        print(f'  {last}')
    print(f'✓ 組裝完成 {out}（{mode} 模式、{len(script.splitlines())} 行、RULES-VERSION {cur}）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
