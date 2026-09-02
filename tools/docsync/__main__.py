"""守 RL-（Task 3 定號後回填）：generate／check／lint／rules／errata／test 六子命令單一入口。

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
    emit.add_argument("--scope", required=True)
    emit.add_argument("--format", choices=("text", "js"), default="text")
    emit.set_defaults(fn=_not_implemented)
    errata = sub.add_parser("errata", help="跨檔假述枚舉")
    errata.add_argument("term")
    errata.set_defaults(fn=_not_implemented)
    sub.add_parser("test", help="跑 tools/docsync/tests").set_defaults(fn=_cmd_test)
    return p


def main(argv):
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
