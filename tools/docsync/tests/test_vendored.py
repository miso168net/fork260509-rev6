"""語料面：憲法 §I.5 例外① 自證（BL-00025、口徑①；allowlist 之 rev5 側＝行雜湊、不落字面）——vendored.compare_tree 之一正多反：註解差異不計＋具名 allowlist 逐對消費＝綠；
非 allowlist 替換行／插入或刪除行（行數差）／allowlist 未消費（漂移）／rev5 檔缺席／掃描面空集合＝紅指名。另對真 repo 跑（rev5 凍結樹在本機時）＝零 finding。"""
import os
import shutil
import tempfile
import unittest

from docsync import ROOT, vendored


def _mk(root, files):
    for rel, text in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)


class TestVendoredCompare(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="vendored-")
        self.a = os.path.join(self.tmp, "rev6")
        self.b = os.path.join(self.tmp, "rev5")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_green_comments_and_allowlist(self):
        _mk(self.a, {"src/x.rs": "// rev6 頭註\nfn a() {}\nlet u = format!(\"{}\", 1);\n", "Cargo.toml": "# rev6 座標\n[package]\nname = \"x\"\n"})
        _mk(self.b, {"src/x.rs": "// rev5 頭註\nfn a() {}\nlet u = \"1\";\n", "Cargo.toml": "# rev5 座標\n[package]\nname = \"x\"\n"})
        allow = (("src/x.rs", 'let u = format!("{}", 1);', vendored.line_hash('let u = "1";'), "RL-0054 執行期串接"),)
        fs, stats = vendored.compare_tree(self.a, self.b, ["src/x.rs", "Cargo.toml"], allow)
        self.assertEqual(fs, [])
        self.assertEqual(stats["files"], 2)
        self.assertEqual(stats["allow_consumed"], 1)

    def test_non_allowlisted_replace_red(self):
        _mk(self.a, {"src/x.rs": "fn a() {}\nlet v = 2;\n"})
        _mk(self.b, {"src/x.rs": "fn a() {}\nlet v = 1;\n"})
        fs, _ = vendored.compare_tree(self.a, self.b, ["src/x.rs"], ())
        self.assertTrue(any("src/x.rs" in f and "非 allowlist" in f for f in fs), fs)

    def test_insert_delete_red(self):
        _mk(self.a, {"src/x.rs": "fn a() {}\nfn extra() {}\n"})
        _mk(self.b, {"src/x.rs": "fn a() {}\n"})
        fs, _ = vendored.compare_tree(self.a, self.b, ["src/x.rs"], ())
        self.assertTrue(any("行數差異" in f for f in fs), fs)

    def test_allowlist_drift_red(self):
        _mk(self.a, {"src/x.rs": "fn a() {}\n"})
        _mk(self.b, {"src/x.rs": "fn a() {}\n"})
        allow = (("src/x.rs", "let u = 2;", vendored.line_hash("let u = 1;"), "已不存在的例外"),)
        fs, _ = vendored.compare_tree(self.a, self.b, ["src/x.rs"], allow)
        self.assertTrue(any("漂移" in f and "src/x.rs" in f for f in fs), fs)

    def test_missing_rev5_file_and_empty_scan_red(self):
        _mk(self.a, {"src/x.rs": "fn a() {}\n"})
        os.makedirs(self.b, exist_ok=True)
        fs, _ = vendored.compare_tree(self.a, self.b, ["src/x.rs"], ())
        self.assertTrue(any("缺此檔" in f for f in fs), fs)
        fs2, _ = vendored.compare_tree(self.a, self.b, [], ())
        self.assertTrue(any("掃描面空集合" in f for f in fs2), fs2)


class TestVendoredRealRepo(unittest.TestCase):
    def test_real_adapter_matches_rev5_with_named_exceptions(self):
        rev5 = vendored.default_rev5_root(ROOT)
        if not os.path.isdir(os.path.join(rev5, vendored.VENDORED_SUB, vendored.VENDORED_DIR)):
            self.skipTest(f"rev5 對照樹不在本機（{rev5}）——bootstrap 3c 為真閘門、本案無從取證")
        fs, stats = vendored.run(ROOT, rev5)
        self.assertEqual(fs, [])
        self.assertGreaterEqual(stats["files"], 5)
        self.assertEqual(stats["allow_consumed"], len(vendored.ALLOWLIST))
