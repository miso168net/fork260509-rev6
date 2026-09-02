"""守 RL-（Task 3 定號後回填）：閘回報一律 finding 錨形、機器生成檔一律帶固定檔頭。

共用底座：Finding 形、Ctx（工作樹／HEAD 讀檔＋git 助手）、front-matter 解析、Day-1 豁免載體。
"""
import os
import re
import subprocess

ERROR, WARN, SKIP = "ERROR", "WARN", "SKIP"

# Finding = (level, code, where, msg)；code 形 "GT-NN"
Finding = tuple


def finding(level, code, where, msg):
    return (level, code, where, msg)


class GitError(RuntimeError):
    pass


RE_FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def _scalar(raw):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [] if not inner else [_scalar(x) for x in inner.split(",")]
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return raw


def parse_front_matter(text):
    """回 (meta, body)；無 front-matter → ({}, text)。只認頂層 `key: value` 純量與 [a, b] 單行清單。"""
    m = RE_FM.match(text or "")
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            meta[k.strip()] = _scalar(v)
    return meta, text[m.end():]


class Ctx:
    """一次 lint／generate 的讀取上下文：root、tracked 名冊、工作樹讀檔快取、HEAD 讀檔。"""

    def __init__(self, root):
        self.root = root
        self._cache = {}
        inside = self.git("rev-parse", "--is-inside-work-tree") == "true"
        self.tracked = [t for t in self.git("ls-files").split("\n") if t] if inside else []

    def git(self, *args, cwd=None):
        """跑 git、回 stdout（去首尾空白；適合 SHA／布林／清單）。失敗→GitError。"""
        return self._git_raw(*args, cwd=cwd).strip()

    def _git_raw(self, *args, cwd=None):
        """同 git() 但不 strip——讀檔內容用（檔尾換行是比對的一部分）。"""
        p = subprocess.run(
            ["git", "-C", cwd or self.root, *args],
            capture_output=True, text=True, encoding="utf-8",
        )
        if p.returncode != 0:
            raise GitError(p.stderr.strip())
        return p.stdout

    def exists(self, rel):
        return os.path.exists(os.path.join(self.root, rel))

    def text(self, rel):
        if rel not in self._cache:
            p = os.path.join(self.root, rel)
            self._cache[rel] = open(p, encoding="utf-8").read() if os.path.isfile(p) else None
        return self._cache[rel]

    def head_text(self, rel):
        try:
            return self._git_raw("show", f"HEAD:{rel}")
        except GitError:
            return None

    def md_texts(self, prefixes=()):
        return {
            r: self.text(r)
            for r in self.tracked
            if r.endswith(".md") and (not prefixes or r.startswith(tuple(prefixes)))
        }


GENERATED_HEADER = "<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->"


class Day1Exemption:
    """Day-1 named exemption：key（"GT-NN.slug"）、reason、released(ctx)->bool 解除謂詞、registered 登記日。"""

    def __init__(self, key, reason, released, registered):
        self.key, self.reason, self.released, self.registered = key, reason, released, registered
