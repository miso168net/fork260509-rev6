"""守 RL-0049／RL-0053：generate／check／lint／rules／errata／test 六子命令單一入口。

用法：python3 tools/docsync <子命令> …（以目錄執行；sys.path 先補 tools/ 使 `docsync` 可 import）。
"""
import argparse
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docsync import ROOT, VERSION  # noqa: E402


def _not_implemented(_args):
    print("尚未實作", file=sys.stderr)
    return 2


def _cmd_rules_emit(args):
    from docsync import RULES, rules
    text = open(os.path.join(ROOT, RULES), encoding="utf-8").read()
    if args.format == "js":
        sys.stdout.write(rules.emit_js(text))
    else:
        if args.scope not in rules.SCOPES:
            print(f"scope 值域外：{args.scope}（可用：{'／'.join(rules.SCOPES)}）", file=sys.stderr)
            return 2
        sys.stdout.write(rules.emit(text, args.scope))
    return 0


def _cmd_errata(args):
    from docsync import SUBMODULES, book
    from docsync.common import Ctx
    ctx = Ctx(ROOT)
    hits = book.errata_scan(ctx, args.term)
    for rel, n, line in hits:
        print(f"{rel}:行 {n}｜{line.strip()}")
    rc = 0
    for sub in SUBMODULES:
        if not ctx.exists(os.path.join(sub, ".git")):
            print(f"⚠ {sub} 不在工作樹、碼面掃描未執行（未執行≠零命中）", file=sys.stderr)
            rc = 3
    print("零命中" if not hits else f"errata「{args.term}」：{len(hits)} 處命中（逐處處置、勿只修被點名那一處）")
    return rc


def _cmd_test(_args):
    tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    suite = unittest.defaultTestLoader.discover(tests_dir, top_level_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


def build_parser():
    p = argparse.ArgumentParser(prog="docsync", description=f"rev6 治理工具 {VERSION}（root={ROOT}）")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("generate", help="由真源重算 docs/generated/").set_defaults(fn=_not_implemented)
    sub.add_parser("check", help="generated 零漂移比對（GT-01）").set_defaults(fn=_not_implemented)
    sub.add_parser("lint", help="跑 GT-01～GT-12").set_defaults(fn=_not_implemented)
    rules = sub.add_parser("rules", help="RULES.md 工具")
    rsub = rules.add_subparsers(dest="rules_cmd", required=True)
    emit = rsub.add_parser("emit", help="依 scope 輸出規則塊＋RULES-VERSION")
    emit.add_argument("--scope", default="implementer", help="implementer／review／fix／主線／人（--format js 時忽略）")
    emit.add_argument("--format", choices=("text", "js"), default="text")
    emit.set_defaults(fn=_cmd_rules_emit)
    errata = sub.add_parser("errata", help="跨檔假述枚舉")
    errata.add_argument("term")
    errata.set_defaults(fn=_cmd_errata)
    sub.add_parser("test", help="跑 tools/docsync/tests").set_defaults(fn=_cmd_test)
    return p


def main(argv):
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
