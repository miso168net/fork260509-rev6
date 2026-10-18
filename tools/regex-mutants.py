#!/usr/bin/env python3
"""正則變異枚舉器：解析模組層已編譯正則之原文、逐成分機械產生停用（放寬）與收窄變異，於獨立子行程替換該模組屬性後只跑指定測試，
列出存活之變異——對正則判準做逐成分變異自證時，以本工具產生之清單為機械全集（implementer 與審查員跑同一份清單；存活者逐支補殺案或記為等價變異）。

用法：
  python3 tools/regex-mutants.py list --path <目錄>… --module <模組> --const <常數>…
      印每支變異（ID、常數、算子、原成分與其位移、變異後全文；編譯失敗者標 ∅無效、與先產者同文者標 ≡去重）。
  python3 tools/regex-mutants.py run --path <目錄>… --module <模組> --const <常數>… --test <unittest 名>…
      先跑基線（零變異）須全綠且案數 >0；再逐支變異各起一個子行程：把模組屬性換成變異後之 `re.compile`（沿用原旗標）、只跑 `--test` 所列；
      任一案 fail 或 error＝殺（error 另標；子行程逾 CHILD_TIMEOUT_SEC 秒亦記殺、另標逾時）；全綠＝存活；判定之前先比案數、須等於基線
      （殺與存活兩路徑皆比、不等＝rc 2）。末段存活清單按「停用／收窄」分組。
  python3 tools/regex-mutants.py test
      合成樣本自測（暫存目錄內合成模組與兩套測試、用完即清；不依賴 repo 現況）。
  子行程：cwd＝第一個 `--path`、sys.path 前置全部 `--path`、`-B` 且 PYTHONDONTWRITEBYTECODE=1（不寫 bytecode）；本行程不 import 受測模組（取原文亦經子行程）。
  例（cwd＝repo 根）：`run --path tools --module docsync.gates --const RE_DQ_STR --test docsync.tests.test_gates.TestGt12RedisPrefixes`。

解析：自行分詞原始 pattern 字串、每一成分保留原文位移（變異＝就地改寫原文、報表直指原成分）。支援語法＝字面、跳脫（含 `\\xhh`／`\\uhhhh`／
  `\\Uhhhhhhhh`／`\\0` 起首之八進位與控制字元）、字元類（含否定、區間、類內跳脫與類別跳脫）、類別跳脫（`\\d\\D\\s\\S\\w\\W`）、錨（`^`／`$`／`\\A`／`\\Z`／`\\b`／`\\B`）、
  `.`、捕獲（含 `(?P<名>…)`）與非捕獲群組、前後瞻、量詞 `*`／`+`／`?`／`{m}`／`{m,}`／`{,n}`／`{m,n}` 與其懶惰形、分支 `|`。
  不支援＝rc 2 指名構造與位移、不靜默略過：行內旗標（`(?i)`、`(?i:…)`）、具名反向參照 `(?P=…)`、數字反向參照、首位非 0 之三位八進位跳脫
  （`\\123`）、類內數字跳脫、條件群組 `(?(…)…)`、原子群組 `(?>…)`、
  佔有量詞、註解群組 `(?#…)`、具名字元跳脫 `\\N{…}`、re.X 旗標。自我一致：解析所得捕獲群組數須等於 `re.compile(原文).groups`，不等＝rc 2。

算子（每支一變異；逐常數去重——變異後全文相同者只留先產之一支並註明；編譯失敗者報無效、不計殺或存活；已帶量詞之成分不另產「可省」）：
  停用（放寬）：
    ①錨拿掉（含前後瞻整段）；
    ②必含字面可省——未帶量詞之字面依序切 token：連續字詞字元（ASCII 英數與底線、未跳脫）為一 token，其餘每個字面字元（含空格與跳脫字元）各為
      一 token；改寫為 `(?:token)?`；
    ③否定字元類逐成員拿掉（區間與類別跳脫各為一成員；拿光＝改為任意字元 `[\\s\\S]`）；
      ③④⑧ 重組類內成員時，原文為裸 `-` 之成員一律改寫 `\\-`（防與兩側成員拼成新區間或成無效區間）；
    ④正字元類放寬兩形：空白類（成員皆屬空格、tab、`\\r\\f\\v`）加換行；ASCII 字母區間加另一大小寫之同區間（類內已有者略）；
    ⑤量詞下界歸零（`+`→`*`、`{m,n}`→`{0,n}`、`{m}`→`{0,m}`、`{m,}`→`{0,}`；懶惰形保留懶惰）；
    ⑥未帶量詞之既有群組整段可省（前後瞻除外）。
  收窄（正向覆蓋）：
    ⑦必含字面 token 刪去（切法同②）；⑧正字元類逐成員拿掉（僅一成員者略）；⑨`?` 改必要、`*`／`+` 改恰一次（懶惰形同）；
    ⑩字元類外之 `\\s` 改 `[ \\t]`；⑪分支逐支刪去（兩支以上者）。
  分組按算子、不按語意：位於負向前後瞻內之成分，停用算子實為收窄、收窄算子實為放寬。

射程外（不產變異；逐項）：
  - 相鄰成分間之插入（例：無字元類之處容空白或換行——`pub` 與 `(` 之間折行、`pub (crate)`、`& str` 之同行空白）；
  - 非既有群組之子序列整段可省或刪去（例：型別註記 `: &str` 整段可省）；
  - 帶量詞成分之整段刪去；未帶量詞之既有群組整段刪去（⑥ 整段可省之收窄對偶）；未帶量詞之字元類、類別跳脫與 `.` 之可省與刪去；
  - 字面替換為他字元；否定字元類加成員；正字元類 ④ 兩形以外之放寬；`\\s` 以外之類別跳脫與 `.` 之替換；錨之替換與新增；
    捕獲與非捕獲群組互換；前後瞻之正負互換與前瞻後瞻互換；分支新增；
  - 量詞下界提升（`*`→`+`、`{0,n}`→`{1,n}`、`{m,n}`→`{m+1,n}`；⑤ 下界歸零之收窄對偶——⑨ 改恰一次與之不等價：例 `[ \\t]*`→`[ \\t]+`
    只殺零空白、⑨ 之 `[ \\t]` 連多空白也殺；`{…}` 形量詞亦不受 ⑨）；量詞上界之增減（`{m,n}` 之 n、`?`→`*` 等）；懶惰與貪婪互換；
  - 正則以外之判準（呼叫端之命中計數、集合比較、字串切分與空白集等）；
  - 替換之前已被他處綁走之正則（執行期拼接、閉包或預設引數捕獲、他模組匯入期之 `from … import`）——替換模組屬性不生效＝全數存活、輸出照列；
  - `--test` 未列之測試（他處測試殺得掉之變異於此仍列存活）。

輸出：每常數先印變異總數（有效、無效與去重數）；逐支一行（✓殺／✗存活／∅無效＋ID＋算子＋原成分@位移）；末段存活清單按「停用／收窄」分組並附變異後全文。
退出碼：run＝0 零存活／1 有存活／2 結構異常（任一 `--path` 不存在或非目錄、匯入失敗、常數缺席或非已編譯之 str 正則、不支援語法、群組數自我一致不符、任一常數零變異、
  基線紅〔fail 或 error〕或零案、測試名載入失敗、逐支變異之子行程未跑成〔無結果行、載入失敗等〕、變異後案數≠基線〔殺與存活兩路徑
  皆比——例：只在該變異下多載入之案、該變異令 setUpClass 拋例外致其下各案未跑〕）；
  list＝0／2（2 之判準同 run 之前六項）；test＝0 全綠／1 有紅；argparse 用法錯 2。
"""
import argparse
import contextlib
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import warnings

CHILD_TIMEOUT_SEC = 300        # 單支子行程上限（GT-12 兩類基線實耗約 2～3 秒；逾時＝該變異令測試跑不完、記殺並另標）
MARK = "@@regex-mutants@@"      # 子行程結果行前綴（測試本身之輸出不含此字面）
OP_NAMES = {1: "①錨拿掉", 2: "②字面可省", 3: "③否定類去成員", 4: "④正類放寬", 5: "⑤下界歸零", 6: "⑥群組可省",
            7: "⑦字面刪去", 8: "⑧正類去成員", 9: "⑨量詞改必要", 10: "⑩\\s 改 [ \\t]", 11: "⑪分支刪去"}
RELAX_OPS = frozenset(range(1, 7))   # 停用（放寬）；其餘＝收窄


class Structural(Exception):
    """結構異常（rc 2）：訊息即輸出行。"""


class Unsupported(Structural):
    """不支援之正則構造（rc 2）：指名構造與位移。"""

    def __init__(self, name, offset):
        super().__init__(f"不支援之構造「{name}」@{offset}")
        self.name, self.offset = name, offset


class Mutant:
    __slots__ = ("id", "const", "op", "comp", "start", "detail", "text", "valid", "err", "dups")

    def __init__(self, const, op, comp, start, detail, text):
        self.id, self.const, self.op, self.comp, self.start, self.detail, self.text = None, const, op, comp, start, detail, text
        self.valid, self.err, self.dups = True, "", []


# ---------------------------------------------------------------------------
# 解析與變異產生
# ---------------------------------------------------------------------------
WORD = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
CLASS_ESC = frozenset("dDsSwW")
ANCHOR_ESC = frozenset("AZbB")
CTRL = {"a": "\a", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v"}
HEXLEN = {"x": 2, "u": 4, "U": 8}
OCT = frozenset("01234567")
WS_CLASS = frozenset(" \t\r\f\v")       # ④空白類之成員全集（不含換行）
LOOK = frozenset(("la", "nla", "lb", "nlb"))
RE_BRACE = re.compile(r"\{(\d*)(?:(,)(\d*))?\}")


class Node:
    """解析樹節點：kind∈lit／esc／dot／anchor／cls／group／rep；start／end＝原文位移（半開區間）。"""

    def __init__(self, kind, start, end, **kw):
        self.kind, self.start, self.end = kind, start, end
        self.__dict__.update(kw)

    def __repr__(self):
        return f"<{self.kind}@{self.start}:{self.end}>"


class _Parser:
    def __init__(self, p):
        self.p, self.i, self.n = p, 0, len(p)

    def alt(self):
        """分支串 → Node(alt)：branches＝[成分串]、spans＝各支原文區間。"""
        start, branches, spans = self.i, [], []
        while True:
            b = self.i
            branches.append(self.seq())
            spans.append((b, self.i))
            if self.i < self.n and self.p[self.i] == "|":
                self.i += 1
                continue
            return Node("alt", start, self.i, branches=branches, spans=spans)

    def seq(self):
        items = []
        while self.i < self.n and self.p[self.i] not in "|)":
            items.append(self.quant(self.atom()))
        return items

    def atom(self):
        p, i = self.p, self.i
        c = p[i]
        if c == "(":
            return self.group()
        if c == "[":
            return self.cls()
        if c == "\\":
            return self.escape()
        self.i += 1
        if c in "^$":
            return Node("anchor", i, i + 1)
        if c == ".":
            return Node("dot", i, i + 1)
        if c in "*+?" or (c == "{" and self.brace(i)):
            raise Unsupported("無前導成分之量詞", i)
        return Node("lit", i, i + 1, ch=c, word=c in WORD)

    def group(self):
        p, s = self.p, self.i
        if p.startswith("(?", s):
            head = p[s + 2:s + 4]
            if head[:1] == ":":
                kind, hdr = "ncap", 3
            elif head[:1] in "=!":
                kind, hdr = ("la" if head[0] == "=" else "nla"), 3
            elif head in ("<=", "<!"):
                kind, hdr = ("lb" if head[1] == "=" else "nlb"), 4
            elif head == "P<":
                close = p.find(">", s)
                kind, hdr = "cap", close + 1 - s
            elif head == "P=":
                raise Unsupported("具名反向參照 (?P=…)", s)
            elif head[:1] == "#":
                raise Unsupported("註解群組 (?#…)", s)
            elif head[:1] == "(":
                raise Unsupported("條件群組 (?(…)…)", s)
            elif head[:1] == ">":
                raise Unsupported("原子群組 (?>…)", s)
            else:
                raise Unsupported("行內旗標 (?…)", s)
        else:
            kind, hdr = "cap", 1
        self.i = s + hdr
        alt = self.alt()
        if self.i >= self.n or p[self.i] != ")":
            raise Unsupported("未閉合群組", s)
        self.i += 1
        return Node("group", s, self.i, gkind=kind, alt=alt)

    def char_escape(self, s, in_class):
        """跳脫字元 → (字元值, 終點)；類別跳脫與錨不由此處理。"""
        p = self.p
        c = p[s + 1] if s + 1 < self.n else ""
        if c == "":
            raise Unsupported("結尾孤立反斜線", s)
        if c in CTRL:
            return CTRL[c], s + 2
        if c == "b" and in_class:
            return "\b", s + 2
        if c in HEXLEN:
            e = s + 2 + HEXLEN[c]
            return chr(int(p[s + 2:e], 16)), e
        if c == "0":
            e = s + 2
            while e < self.n and e < s + 4 and p[e] in OCT:
                e += 1
            return chr(int(p[s + 1:e], 8)), e
        if c.isdigit():   # 類外同 sre：首位起連三位皆八進位＝八進位跳脫、其餘＝反向參照；類內一律拒
            if in_class:
                raise Unsupported("類內數字跳脫", s)
            octal = len(p[s + 1:s + 4]) == 3 and all(x in OCT for x in p[s + 1:s + 4])
            raise Unsupported("三位八進位跳脫 \\ooo" if octal else "數字反向參照 \\N", s)
        if c == "N":
            raise Unsupported("具名字元跳脫 \\N{…}", s)
        if c.isascii() and c.isalnum():
            raise Unsupported(f"未知跳脫 \\{c}", s)
        return c, s + 2

    def escape(self):
        s, c = self.i, self.p[self.i + 1:self.i + 2]
        if c in ANCHOR_ESC and c:
            self.i = s + 2
            return Node("anchor", s, s + 2)
        if c in CLASS_ESC and c:
            self.i = s + 2
            return Node("esc", s, s + 2, letter=c)
        ch, self.i = self.char_escape(s, False)
        return Node("lit", s, self.i, ch=ch, word=False)

    def cls_member(self, i):
        """類內一個端點 → (kind, 字元值｜類別字母, 終點)。"""
        if self.p[i] == "\\":
            c = self.p[i + 1:i + 2]
            if c in CLASS_ESC and c:
                return "esc", c, i + 2
            ch, e = self.char_escape(i, True)
            return "char", ch, e
        return "char", self.p[i], i + 1

    def cls(self):
        p, s = self.p, self.i
        i = s + 1
        neg = p[i:i + 1] == "^"
        i += neg
        items, first = [], True
        while True:
            if i >= self.n:
                raise Unsupported("未閉合字元類", s)
            if p[i] == "]" and not first:
                i += 1
                break
            first = False
            kind, val, e = self.cls_member(i)
            if kind == "char" and e + 1 < self.n and p[e] == "-" and p[e + 1] != "]":
                hkind, hval, he = self.cls_member(e + 1)
                if hkind != "char":
                    raise Unsupported("字元類區間端點為類別跳脫", i)
                items.append(Node("range", i, he, lo=val, hi=hval))
                i = he
            else:
                items.append(Node(kind, i, e, val=val))
                i = e
        self.i = i
        return Node("cls", s, i, neg=neg, items=items)

    def brace(self, i):
        """`{` 起首之量詞 → (min, max｜None, 終點)；不成量詞（`{}`、`{a}` 等＝字面）回 None。"""
        m = RE_BRACE.match(self.p, i)
        if not m or (not m.group(1) and not m.group(2)):
            return None
        lo = int(m.group(1)) if m.group(1) else 0
        hi = (int(m.group(3)) if m.group(3) else None) if m.group(2) else lo
        return lo, hi, m.end()

    def quant(self, atom):
        p, i = self.p, self.i
        if i >= self.n:
            return atom
        c = p[i]
        if c in "*+?":
            lo, hi, e = {"*": (0, None), "+": (1, None), "?": (0, 1)}[c] + (i + 1,)
        elif c == "{" and self.brace(i):
            lo, hi, e = self.brace(i)
        else:
            return atom
        lazy = e < self.n and p[e] == "?"
        if not lazy and e < self.n and p[e] == "+":
            raise Unsupported("佔有量詞", i)
        e += lazy
        self.i = e
        return Node("rep", atom.start, e, atom=atom, qstart=i, qmin=lo, qmax=hi, lazy=lazy)


def _count_groups(node):
    if node.kind == "alt":
        return sum(_count_groups(x) for seq in node.branches for x in seq)
    if node.kind == "rep":
        return _count_groups(node.atom)
    if node.kind == "group":
        return (node.gkind == "cap") + _count_groups(node.alt)
    return 0


def parse(pattern, flags=0, groups=None):
    """原文 → 解析樹（Node(alt)）；不支援構造＝Unsupported；`groups` 給定時捕獲群組數須相等（自我一致）、不等＝Structural。"""
    if flags & re.VERBOSE:
        raise Unsupported("re.X（VERBOSE）旗標", 0)
    ps = _Parser(pattern)
    tree = ps.alt()
    if ps.i != ps.n:
        raise Unsupported("未配對之右括號", ps.i)
    got = _count_groups(tree)
    if groups is not None and got != groups:
        raise Structural(f"群組數自我一致不符：解析得捕獲群組 {got} 個、re.compile(原文).groups＝{groups}")
    return tree


def generate(const, pattern, flags=0, groups=None):
    """原文 → (變異串, 去重併入數)：逐成分套十一算子、依 (位移, 算子) 排序、同文去重、逐支試編譯標有效性、配 ID `<常數>#<序>`。"""
    tree = parse(pattern, flags, groups)
    p, raw = pattern, []

    def add(op, comp_node_or_span, es, ee, repl, detail=""):
        s, e = comp_node_or_span
        raw.append(Mutant(const, op, p[s:e], s, detail, p[:es] + repl + p[ee:]))

    def walk_alt(alt):
        if len(alt.branches) >= 2:
            last = len(alt.spans) - 1
            for k, (bs, be) in enumerate(alt.spans):
                es, ee = (bs, alt.spans[k + 1][0]) if k < last else (alt.spans[k - 1][1], be)
                add(11, (bs, be), es, ee, "")
        for seq in alt.branches:
            walk_seq(seq)

    def walk_seq(seq):
        k = 0
        while k < len(seq):
            nd = seq[k]
            if nd.kind != "lit":
                walk_node(nd, False)
                k += 1
                continue
            j = k
            if nd.word:
                while j + 1 < len(seq) and seq[j + 1].kind == "lit" and seq[j + 1].word:
                    j += 1
            s, e = nd.start, seq[j].end
            add(2, (s, e), s, e, f"(?:{p[s:e]})?")
            add(7, (s, e), s, e, "")
            k = j + 1

    def walk_node(nd, quantified):
        if nd.kind == "rep":
            q = p[nd.qstart:nd.end]
            core, lz = (q[:-1], "?") if nd.lazy else (q, "")
            if nd.qmin > 0:
                new = "*" if core == "+" else "{0," + ("" if nd.qmax is None else str(nd.qmax)) + "}"
                add(5, (nd.start, nd.end), nd.qstart, nd.end, new + lz)
            if core in ("?", "*", "+"):
                add(9, (nd.start, nd.end), nd.qstart, nd.end, "")
            walk_node(nd.atom, True)
        elif nd.kind == "anchor":
            add(1, (nd.start, nd.end), nd.start, nd.end, "")
        elif nd.kind == "group":
            if nd.gkind in LOOK:
                add(1, (nd.start, nd.end), nd.start, nd.end, "")
            elif not quantified:
                add(6, (nd.start, nd.end), nd.end, nd.end, "?")
            walk_alt(nd.alt)
        elif nd.kind == "cls":
            walk_cls(nd)
        elif nd.kind == "esc" and nd.letter == "s":
            add(10, (nd.start, nd.end), nd.start, nd.end, r"[ \t]")

    def walk_cls(nd):
        items, txt = nd.items, p[nd.start:nd.end]

        def body(skip=None):
            # 原文為裸 `-` 之成員一律改寫 `\-`：拿掉鄰成員或於類尾附加區間後，裸 `-` 會與兩側成員拼成新區間（或成無效之區間）
            return "".join("\\-" if p[x.start:x.end] == "-" else p[x.start:x.end] for j, x in enumerate(items) if j != skip)
        if nd.neg:
            for k, it in enumerate(items):
                rest = body(k)
                add(3, (it.start, it.end), nd.start, nd.end, "[^" + rest + "]" if rest else r"[\s\S]", f"於「{txt}」@{nd.start}")
            return
        if all(it.kind == "char" and it.val in WS_CLASS for it in items):
            add(4, (nd.start, nd.end), nd.start, nd.end, "[" + body() + r"\n]", "加換行")
        ranges = {(x.lo, x.hi) for x in items if x.kind == "range"}
        for it in items:
            if (it.kind == "range" and it.lo.isascii() and it.hi.isascii() and it.lo.isalpha() and it.hi.isalpha()
                    and it.lo.isupper() == it.hi.isupper() and (it.lo.swapcase(), it.hi.swapcase()) not in ranges):
                other = f"{it.lo.swapcase()}-{it.hi.swapcase()}"
                add(4, (it.start, it.end), nd.start, nd.end, "[" + body() + other + "]", f"於「{txt}」@{nd.start} 加 {other}")
        if len(items) >= 2:
            for k, it in enumerate(items):
                rest = body(k)   # 拿掉首成員後以字面 `^` 起首＝重組會變否定類，改寫為 `\^`
                add(8, (it.start, it.end), nd.start, nd.end, "[" + ("\\" + rest if rest.startswith("^") else rest) + "]",
                    f"於「{txt}」@{nd.start}")

    walk_alt(tree)
    raw.sort(key=lambda m: (m.start, m.op))
    out, seen, dups = [], {pattern: None}, 0
    for m in raw:
        if m.text in seen:
            dups += 1
            first = seen[m.text]
            if first is not None:
                first.dups.append(f"{OP_NAMES[m.op]}「{m.comp}」@{m.start}")
            continue
        seen[m.text] = m
        out.append(m)
    for n, m in enumerate(out, 1):
        m.id = f"{const}#{n}"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                re.compile(m.text, flags)
            except re.error as e:
                m.valid, m.err = False, str(e)
    return out, dups


# ---------------------------------------------------------------------------
# 子行程與兩支子命令
# ---------------------------------------------------------------------------
# 子行程本體（`python3 -B -c`）：stdin 收 JSON 規格；probe＝取常數原文／旗標／群組數；run＝替換常數後載入並跑測試。
# 結果寫成一行 MARK＋JSON（測試本身之輸出照印、不干擾）。
CHILD = r'''
import importlib, json, re, sys, unittest
MARK = "@@regex-mutants@@"
def emit(obj):
    sys.stdout.write("\n" + MARK + json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    sys.exit(0)
spec = json.loads(sys.stdin.read())
for p in reversed(spec["paths"]):
    sys.path.insert(0, p)
try:
    mod = importlib.import_module(spec["module"])
except BaseException as e:
    emit({"stage": "import", "error": f"{type(e).__name__}: {e}"})
if spec["mode"] == "probe":
    info = {}
    for name in spec["consts"]:
        if not hasattr(mod, name):
            info[name] = {"error": "模組無此屬性"}
            continue
        obj = getattr(mod, name)
        if not isinstance(obj, re.Pattern) or not isinstance(obj.pattern, str):
            info[name] = {"error": f"非已編譯之 str 正則（型別 {type(obj).__name__}）"}
            continue
        info[name] = {"pattern": obj.pattern, "flags": obj.flags, "groups": obj.groups}
    emit({"stage": "probe", "consts": info})
for name, pat in spec["patch"].items():
    new = re.compile(pat, getattr(mod, name).flags)
    setattr(mod, name, new)
    if getattr(mod, name) is not new:
        emit({"stage": "patch", "error": f"{name} 替換後讀回非新物件"})
loader = unittest.TestLoader()
try:
    suite = loader.loadTestsFromNames(spec["tests"])
except BaseException as e:
    emit({"stage": "load", "error": f"{type(e).__name__}: {e}"})
if loader.errors:
    emit({"stage": "load", "error": " / ".join(str(x).strip().splitlines()[-1] for x in loader.errors)})
result = unittest.TestResult()
suite.run(result)
emit({"stage": "done", "run": result.testsRun, "failures": [t.id() for t, _ in result.failures],
      "errors": [t.id() for t, _ in result.errors], "skipped": len(result.skipped)})
'''


def _child(spec, paths):
    """起一個子行程 → (結果 dict, 實耗秒)；逾時回 stage=timeout、無結果行回 stage=crash（附 rc 與 stderr 末行）。"""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    t0 = time.monotonic()
    try:
        r = subprocess.run([sys.executable, "-B", "-c", CHILD], input=json.dumps(dict(spec, paths=paths)), cwd=paths[0],
                           capture_output=True, text=True, encoding="utf-8", env=env, timeout=CHILD_TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        return {"stage": "timeout"}, time.monotonic() - t0
    dt = time.monotonic() - t0
    for line in reversed(r.stdout.splitlines()):
        if line.startswith(MARK):
            return json.loads(line[len(MARK):]), dt
    tail = (r.stderr.strip().splitlines() or ["（無 stderr）"])[-1]
    return {"stage": "crash", "error": f"子行程 rc={r.returncode} 無結果行：{tail}"}, dt


def _flag_names(flags):
    names = [n for n, f in (("re.I", re.I), ("re.M", re.M), ("re.S", re.S), ("re.A", re.A), ("re.L", re.L)) if flags & f]
    return "／".join(names) or "無"


def _err(msg):
    print(f"error: {msg}", flush=True)


def _prepare(paths, module, consts):
    """probe 子行程取原文 → [(常數, 原文, 旗標, 變異串, 去重數)]；任一結構異常拋 Structural。"""
    for p in paths:   # 首個＝子行程 cwd（不存在即 subprocess 拋 OSError）、其餘＝sys.path 前置：打錯一律於此 rc 2、不落 traceback
        if not os.path.isdir(p):
            raise Structural(f"--path 不存在或非目錄：{p}")
    res, _ = _child({"mode": "probe", "module": module, "consts": consts}, paths)
    if res["stage"] != "probe":
        raise Structural(f"模組 {module} 匯入失敗：{res.get('error', res['stage'])}")
    out = []
    for name in consts:
        info = res["consts"][name]
        if "error" in info:
            raise Structural(f"{module}.{name}：{info['error']}")
        try:
            muts, dups = generate(name, info["pattern"], info["flags"], info["groups"])
        except Structural as e:
            raise Structural(f"{module}.{name}：{e}") from None
        if not muts:
            raise Structural(f"{module}.{name}：零變異（`{info['pattern']}` 無可施算子之成分）")
        out.append((name, info["pattern"], info["flags"], muts, dups))
    return out


def _header(name, pattern, flags, muts, dups):
    bad = sum(not m.valid for m in muts)
    print(f"== {name}：`{pattern}`（旗標 {_flag_names(flags)}）——變異 {len(muts) + dups} 支（有效 {len(muts) - bad}／無效 {bad}／"
          f"去重併入 {dups}）", flush=True)


def _label(m):
    return f"{m.id} {OP_NAMES[m.op]}「{m.comp}」@{m.start}" + (f"（{m.detail}）" if m.detail else "")


def _dup_note(m):
    return f"；同文併入：{'、'.join(m.dups)}" if m.dups else ""


def do_list(paths, module, consts):
    """list 子命令 → rc（0／2）。"""
    try:
        prepared = _prepare(paths, module, consts)
    except Structural as e:
        _err(str(e))
        return 2
    for name, pattern, flags, muts, dups in prepared:
        _header(name, pattern, flags, muts, dups)
        for m in muts:
            mark = "  " if m.valid else "∅無效 "
            print(f"  {mark}{_label(m)} → `{m.text}`{_dup_note(m)}" + (f"（編譯錯：{m.err}）" if not m.valid else ""), flush=True)
    return 0


def do_run(paths, module, consts, tests):
    """run 子命令 → (rc, 報表 dict{mutants, status})；status＝{ID: killed｜survived｜invalid}。"""
    rep = {"mutants": [], "status": {}}
    t_all = time.monotonic()
    try:
        prepared = _prepare(paths, module, consts)
    except Structural as e:
        _err(str(e))
        return 2, rep
    print(f"regex-mutants run：模組 {module}、常數 {len(consts)} 支、測試 {' '.join(tests)}；子行程 cwd＝{paths[0]}", flush=True)
    base, dt = _child({"mode": "run", "module": module, "patch": {}, "tests": tests}, paths)
    if base["stage"] != "done":
        _err(f"基線（零變異）未跑成：{base['stage']}——{base.get('error', '')}" + ("（測試名載入失敗）" if base["stage"] == "load" else ""))
        return 2, rep
    if base["failures"] or base["errors"]:
        _err(f"基線（零變異）紅：fail {len(base['failures'])}／error {len(base['errors'])}（{', '.join(base['failures'] + base['errors'])}）"
             "——基線須全綠才可判殺")
        return 2, rep
    if base["run"] == 0:
        _err("基線零案：指定測試載入後一案也沒跑——殺／存活無從判定")
        return 2, rep
    print(f"基線：✓ {base['run']} 案全綠（skipped={base['skipped']}；{dt:.1f}s）", flush=True)
    killed = survived = invalid = errored = timed = 0
    for name, pattern, flags, muts, dups in prepared:
        _header(name, pattern, flags, muts, dups)
        for m in muts:
            rep["mutants"].append(m)
            if not m.valid:
                rep["status"][m.id] = "invalid"
                invalid += 1
                print(f"  ∅無效 {_label(m)}（編譯錯：{m.err}）", flush=True)
                continue
            res, dt = _child({"mode": "run", "module": module, "patch": {name: m.text}, "tests": tests}, paths)
            if res["stage"] not in ("done", "timeout"):
                _err(f"{m.id}：子行程未跑成（{res['stage']}）——{res.get('error', '')}")
                return 2, rep
            if res["stage"] == "done" and res["run"] != base["run"]:   # 殺與存活兩路徑皆比、先於判定
                _err(f"{m.id}：案數 {res['run']} ≠ 基線 {base['run']}——載入面或類／模組層 setUp 隨變異改變、殺或存活之判定皆作廢")
                return 2, rep
            if res["stage"] == "done" and not res["failures"] and not res["errors"]:
                rep["status"][m.id] = "survived"
                survived += 1
                print(f"  ✗存活 {_label(m)}{_dup_note(m)}", flush=True)
                continue
            rep["status"][m.id] = "killed"
            killed += 1
            if res["stage"] == "timeout":
                timed += 1
                why = f"逾時 {CHILD_TIMEOUT_SEC}s"
            else:
                errored += bool(res["errors"])
                why = f"fail {len(res['failures'])}／error {len(res['errors'])}" + ("；含 error" if res["errors"] else "")
            print(f"  ✓殺 {_label(m)}（{why}）{_dup_note(m)}", flush=True)
    alive = [m for m in rep["mutants"] if rep["status"][m.id] == "survived"]
    print(f"== 存活清單（{len(alive)} 支）", flush=True)
    for title, ops in (("停用", RELAX_OPS), ("收窄", frozenset(OP_NAMES) - RELAX_OPS)):
        grp = [m for m in alive if m.op in ops]
        print(f"  {title}（{len(grp)} 支）：" + ("" if grp else "無"), flush=True)
        for m in grp:
            print(f"    {_label(m)} → `{m.text}`", flush=True)
    rc = 1 if alive else 0
    print(f"regex-mutants run：殺 {killed}（含 error {errored}、逾時 {timed}）／存活 {survived}／無效 {invalid}；"
          f"實耗 {time.monotonic() - t_all:.1f}s → rc {rc}", flush=True)
    return rc, rep


# ---------------------------------------------------------------------------
# 自測
# ---------------------------------------------------------------------------
SYN_TARGET = r'''import re
RE_P = re.compile(r"^k=([ab]+)$", re.M)
RE_Q = re.compile(r"(?<=ab)c|a|a")
RE_DOT = re.compile(r".")
RE_INL = re.compile(r"(?i)k")
RE_STR = "k"
RE_BYTES = re.compile(b"k")


def grab(text):
    return RE_P.findall(text)
'''
SYN_CLOSURE = r'''import re
RE_P = re.compile(r"^k=([ab]+)$", re.M)


def grab(text, rx=RE_P):
    return rx.findall(text)
'''
SYN_TESTS = r'''import os
import time
import unittest
import rmt_target
import rmt_closure

DROP_CARET = "k=([ab]+)$"   # RE_P#1（①拿掉 `^`）之變異後全文：Count／Crash／Slow 據此於該支之下改變行為


class Weak(unittest.TestCase):
    def test_hit(self):
        # 命中行非首行：子行程替換若丟掉 re.M，`^` 起首之變異全數轉殺、指定存活集即不符
        self.assertEqual(rmt_target.grab("x\nk=aa\n"), ["aa"])


class Err(unittest.TestCase):
    def test_hit(self):
        # 零命中時取 [0]＝IndexError：殺者全經 error、無 failure
        self.assertEqual(rmt_target.grab("k=ab\n")[0], "ab")


class BaseErr(unittest.TestCase):
    def test_err(self):
        raise RuntimeError("合成之基線 error")


class Count(unittest.TestCase):
    def test_hit(self):
        self.assertEqual(rmt_target.grab("k=ab\n"), ["ab"])

    if rmt_target.RE_P.pattern == DROP_CARET:   # 子行程先替換後載入：該支之下多一案
        def test_extra(self):
            pass


class CountKill(unittest.TestCase):
    def test_hit(self):
        self.assertEqual(rmt_target.grab("k=ab\n"), ["ab"])

    if rmt_target.RE_P.pattern == DROP_CARET:   # 該支之下多載入一案且該案紅、原案照綠：殺全來自基線不存在之案
        def test_extra(self):
            self.fail("基線不存在之案")


class SetupKill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if rmt_target.RE_P.pattern == DROP_CARET:   # 該支之下 setUpClass 拋例外：其下各案未跑＝案數 0、errors 只有類層一筆
            raise RuntimeError("合成之 setUpClass 失敗")

    def test_hit(self):
        self.assertEqual(rmt_target.grab("k=ab\n"), ["ab"])


class Crash(unittest.TestCase):
    def test_hit(self):
        if rmt_target.RE_P.pattern == DROP_CARET:
            os._exit(3)
        self.assertEqual(rmt_target.grab("k=ab\n"), ["ab"])


class Slow(unittest.TestCase):
    def test_hit(self):
        if rmt_target.RE_P.pattern == DROP_CARET:
            time.sleep(60)
        self.assertEqual(rmt_target.grab("k=ab\n"), ["ab"])


class QWeak(unittest.TestCase):
    def test_hit(self):
        self.assertTrue(rmt_target.RE_Q.search("abc"))


class Cwd(unittest.TestCase):
    def test_cwd(self):
        # 子行程 cwd＝首個 --path（合成目錄）；自測行程之 cwd 恆異於合成目錄、cwd 未設即基線紅
        self.assertEqual(os.path.realpath(os.getcwd()), os.path.realpath(os.path.dirname(rmt_target.__file__)))


class Strong(unittest.TestCase):
    grab = staticmethod(lambda text: rmt_target.grab(text))

    def test_hit(self):
        self.assertEqual(self.grab("k=ab\n"), ["ab"])

    def test_line_start(self):
        self.assertEqual(self.grab("xk=ab\n"), [])

    def test_line_end(self):
        self.assertEqual(self.grab("k=abx\n"), [])

    def test_key_required(self):
        self.assertEqual(self.grab("=ab\n"), [])

    def test_equals_required(self):
        self.assertEqual(self.grab("kab\n"), [])

    def test_value_nonempty(self):
        self.assertEqual(self.grab("k=\n"), [])


class ClosureStrong(Strong):
    grab = staticmethod(lambda text: rmt_closure.grab(text))


class Red(unittest.TestCase):
    def test_red(self):
        self.fail("合成之基線紅")


class Empty(unittest.TestCase):
    pass
'''
# RE_P＝`^k=([ab]+)$` 之十一支變異（op, 原成分）；弱測試集只殺 ⑦×2／⑧拿掉 a／⑨ 四支、存活停用六支＋收窄一支（⑧拿掉 b）；
# Err 集之殺者五支全經 error。RE_Q＝`(?<=ab)c|a|a`：十二支中無效一支（後瞻內 `ab` 可省＝變寬）、同文併入一支（末兩支分支刪去同文）。
SYN_ALL = {(1, "^"), (1, "$"), (2, "k"), (2, "="), (7, "k"), (7, "="), (6, "([ab]+)"), (5, "[ab]+"), (9, "[ab]+"), (8, "a"), (8, "b")}
SYN_WEAK_RELAX = {(1, "^"), (1, "$"), (2, "k"), (2, "="), (6, "([ab]+)"), (5, "[ab]+")}
SYN_WEAK_NARROW = {(8, "b")}
SYN_WEAK_SURVIVORS = SYN_WEAK_RELAX | SYN_WEAK_NARROW
SYN_ERR_KILLED = {(7, "k"), (7, "="), (8, "a"), (8, "b"), (9, "[ab]+")}
SYN_P_HEADER = "== RE_P：`^k=([ab]+)$`（旗標 re.M）——變異 11 支（有效 11／無效 0／去重併入 0）"
SYN_Q_HEADER = "== RE_Q：`(?<=ab)c|a|a`（旗標 無）——變異 12 支（有效 10／無效 1／去重併入 1）"


def self_test():
    """合成樣本逐案自證；任一案敗＝rc 1、指名案名與實得值。
    產生面（不起子行程）：十一算子各一案起、斷言原成分、位移與變異後全文（②另斷言帶量詞者不產可省、②⑦另斷言字詞 token 含底線與數字、
    ④另斷言空白類混他字元或含換行者與異大小寫字母區間不產、含 `\\r\\f\\v` 之空白類照產、⑤另斷言 `{m,}` 上界照留空與下界已為零者不產、⑥另斷言已可省者與前後瞻不產、
    ⑧另斷言單成員不產、拿掉首成員後以字面 `^` 起首者改寫 `\\^`、③④⑧另斷言類內裸 `-` 重組後改寫 `\\-` 且變異後字元集＝所標算子之語意、⑨另斷言懶惰形整段改恰一次與 `{…}` 形不產、⑩另斷言類內 `\\s` 與 `\\S`／`\\d` 不產）；無效變異（後瞻變寬）標無效、去重（`a|a`
    之兩支分支刪去同文）留一支並註明；支援語法全集之解析與群組數自我一致、群組數不符＝結構異常；類內首位 `]` 為字面成員、`\\0` 起首之八進位
    至多三位；不支援構造十形各指名構造與位移。
    執行面（暫存目錄合成模組與測試、子行程實跑）：弱測試集（命中行非首行＝丟 re.M 即轉紅）→指定之七支存活 rc 1、標頭全文、存活者各落
    「停用／收窄」正確區塊；強測試集→零存活 rc 0；子行程替換確實生效＝必殺變異（⑦刪 `k`）於強測試集被殺、而同一變異對閉包捕獲之模組存活
    （射程外句之實證、全數存活）；只拋例外之變異記殺並標含 error；子行程逾時記殺並標逾時；子行程 cwd＝首個 `--path`；probe 回報之群組數遭竄改→list 與 run 皆 rc 2
    （CLI 接線）；run 與 list 之無效支（∅無效、不計殺或存活）、同文併入註記與標頭去重數；rc 2 各形＝基線紅（failure 與只有 error 各一）、
    變異後案數≠基線（存活路徑、殺路徑之多載入案與 setUpClass 拋例外各一）、逐支變異之子行程未跑成、零案、零變異（list 與 run）、不支援語法、常數非正則（str 與 bytes）、常數缺席（指名「模組無此屬性」）、模組匯入失敗、
    測試名載入失敗、`--path` 不存在或非目錄（經 main 之 list 與 run；首個不存在、首個為檔案、第二個不存在各一）；list 之逐支輸出含 ID、原成分與變異後全文。"""
    cases = []

    def case(name, ok, detail):
        cases.append((name, bool(ok), detail))

    def guard(name, fn):
        try:
            ok, detail = fn()
        except Exception as e:  # noqa: BLE001——自測收斂點：例外即案敗、指名型別
            ok, detail = False, f"例外 {type(e).__name__}：{e}"
        case(name, ok, detail)

    def quads(pattern, flags=0):
        return {(m.op, m.comp, m.start, m.text) for m in generate("P", pattern, flags)[0]}

    def expect(pattern, want, absent=(), flags=0):
        """want＝須在之 (op, 原成分, 位移, 變異後全文)；absent＝不得出現之 (op, 原成分) 或 (op, 原成分, 位移)。"""
        def fn():
            got = quads(pattern, flags)
            miss = sorted(w for w in want if w not in got)
            extra = sorted(a for a in absent if any(g[:len(a)] == a for g in got))
            return not miss and not extra, f"缺 {miss}／不應有 {extra}／實得 {sorted(got)}"
        return fn

    # ── 產生面：十一算子 ──
    guard("①錨拿掉：`^`／`$`", expect(r"^a$", {(1, "^", 0, "a$"), (1, "$", 2, "^a")}))
    guard("①錨拿掉：`\\b` 與前瞻整段", expect(r"\bx(?=b)", {(1, r"\b", 0, r"x(?=b)"), (1, "(?=b)", 3, r"\bx")}))
    guard("②字面可省：字詞字元連續段一 token、跳脫字元與其他字面各一 token；帶量詞者不產",
          expect(r"ab\.c d?", {(2, "ab", 0, r"(?:ab)?\.c d?"), (2, r"\.", 2, r"ab(?:\.)?c d?"), (2, "c", 4, r"ab\.(?:c)? d?"),
                               (2, " ", 5, r"ab\.c(?: )?d?")}, absent={(2, "d"), (2, "d?")}))
    guard("②⑦字詞 token：ASCII 英數與底線之連續段為一 token（`a_1` 不拆成 `a`／`_`／`1`）",
          expect(r"a_1\.", {(2, "a_1", 0, r"(?:a_1)?\."), (7, "a_1", 0, r"\."), (2, r"\.", 3, r"a_1(?:\.)?"), (7, r"\.", 3, "a_1")},
                 absent={(op, t) for op in (2, 7) for t in ("a", "_", "1", "a_", "_1")}))
    guard("③否定類去成員：逐成員（含跳脫成員）；拿光＝任意字元",
          expect(r'[^"\\]x[^y]', {(3, '"', 2, r'[^\\]x[^y]'), (3, r"\\", 3, r'[^"]x[^y]'), (3, "y", 9, r'[^"\\]x[\s\S]')}))
    guard("④正類放寬：空白類加換行、ASCII 字母區間加另一大小寫（類內已有者略）",
          expect(r"[ \t][A-Z_][a-zA-Z]", {(4, r"[ \t]", 0, r"[ \t\n][A-Z_][a-zA-Z]"), (4, "A-Z", 6, r"[ \t][A-Z_a-z][a-zA-Z]")},
                 absent={(4, "a-z"), (4, "A-Z", 15)}))
    guard("④正類放寬之判定邊界：空白類須成員皆屬空格／tab／`\\r\\f\\v`（含 `\\r\\f\\v` 者產、混他字元或含換行者不產）；"
          "字母區間須兩端同大小寫（`A-z` 不產）",
          expect(r"[ a][A-z][ \n][\r\f\v]", {(4, r"[\r\f\v]", 14, r"[ a][A-z][ \n][\r\f\v\n]")},
                 absent={(4, "[ a]"), (4, "A-z"), (4, r"[ \n]")}))
    guard("⑤下界歸零：`+`／`{m,n}`／`{m}`／懶惰 `+?`／`{m,}`（上界照留空）",
          expect(r"a+b{2,3}c{2}d+?e{2,}", {(5, "a+", 0, r"a*b{2,3}c{2}d+?e{2,}"), (5, "b{2,3}", 2, r"a+b{0,3}c{2}d+?e{2,}"),
                                           (5, "c{2}", 8, r"a+b{2,3}c{0,2}d+?e{2,}"), (5, "d+?", 12, r"a+b{2,3}c{2}d*?e{2,}"),
                                           (5, "e{2,}", 15, r"a+b{2,3}c{2}d+?e{0,}")}))

    def t_qmin_zero():
        ms, dups = generate("P", r"x?y*z{0,2}w{,3}")
        op5 = [(m.comp, m.start, m.text) for m in ms if m.op == 5]
        return not op5 and dups == 0, f"⑤ 實得 {op5}／去重併入 {dups}（同原文之 `{{0,2}}` 會落去重）"

    guard("⑤下界已為零者不產：`?`／`*`／`{0,n}`／`{,n}`（無 ⑤ 支、亦無同原文落去重者）", t_qmin_zero)
    guard("⑥群組可省：未帶量詞之群組；已可省者與前瞻不產",
          expect(r"(?:ab)c(?:d)?(?=e)", {(6, "(?:ab)", 0, r"(?:ab)?c(?:d)?(?=e)")}, absent={(6, "(?:d)?"), (6, "(?:d)"), (6, "(?=e)")}))
    guard("⑦字面刪去：切法同②", expect(r"ab\.c", {(7, "ab", 0, r"\.c"), (7, r"\.", 2, "abc"), (7, "c", 4, r"ab\.")}))
    guard("⑧正類去成員：逐成員；單成員不產", expect(r"[ab][c]", {(8, "a", 1, "[b][c]"), (8, "b", 2, "[a][c]")}, absent={(8, "c")}))

    def t_caret():
        got = {(m.op, m.comp, m.start, m.text, m.valid) for m in generate("P", r"[a^b]x[a^]")[0] if m.op == 8}
        want = {(8, "a", 1, r"[\^b]x[a^]", True), (8, "^", 2, "[ab]x[a^]", True), (8, "b", 3, "[a^]x[a^]", True),
                (8, "a", 7, r"[a^b]x[\^]", True), (8, "^", 8, "[a^b]x[a]", True)}
        return got == want, f"缺 {sorted(want - got)}／多 {sorted(got - want)}"

    guard("⑧正類去成員：重組後以字面 `^` 起首者改寫 `\\^`（不得變成否定類或無效）", t_caret)
    guard("類內首位 `]` 為字面成員（不當類之結尾）：`[]a]` 之 ⑧ 逐成員", expect(r"[]a]", {(8, "]", 1, "[a]"), (8, "a", 2, "[]]")}))
    guard("`\\0` 起首之八進位跳脫至多三位（`\\0123`＝`\\012` 後接字面 `3`）：②依此切 token",
          expect(r"\0123", {(2, r"\012", 0, r"(?:\012)?3"), (2, "3", 4, r"\012(?:3)?")}))

    def charset(pat):
        rx = re.compile(pat)
        return frozenset(chr(c) for c in range(128) if rx.fullmatch(chr(c)))

    def dash_rows(rows):
        """rows＝(原文, 算子, 原成分, 變異後全文, 預期字元集〔ASCII〕)：類內裸 `-` 重組後須改寫 `\\-`、字元集＝所標算子之語意。"""
        def fn():
            bad = []
            for pattern, op, comp, text, want in rows:
                ms = [m for m in generate("P", pattern)[0] if m.op == op and m.comp == comp]
                got = [(m.text, m.valid, charset(m.text) == want if m.valid else m.err) for m in ms]
                if got != [(text, True, True)]:
                    bad.append((pattern, op, comp, got))
            return not bad, f"不符 {bad}"
        return fn

    lower, upper, digit = (frozenset(map(chr, range(a, b + 1))) for a, b in ((97, 122), (65, 90), (48, 57)))
    ascii_all = frozenset(map(chr, range(128)))
    guard("④正類放寬：類內裸 `-` 於附加區間後改寫 `\\-`（`[a-z0-9.-]` 加 A-Z 不得拼成 `.-A` 區間）",
          dash_rows([(r"[a-z0-9.-]", 4, "a-z", r"[a-z0-9.\-A-Z]", lower | digit | upper | {".", "-"})]))
    guard("③⑧類去成員：類內裸 `-` 於拿掉鄰成員後改寫 `\\-`（不得與兩側成員拼成新區間、亦不得成無效）",
          dash_rows([(r"[Z0-9-c]", 8, "0-9", r"[Z\-c]", {"Z", "-", "c"}),
                     (r"[^a0-9-z]", 3, "0-9", r"[^a\-z]", ascii_all - {"a", "-", "z"}),
                     (r'[\w0-9-"]', 8, "0-9", r'[\w\-"]', lower | upper | digit | {"_", "-", '"'})]))
    guard("⑨量詞改必要／恰一次：`?`／`*`／`+`",
          expect(r"a?b*c+", {(9, "a?", 0, "ab*c+"), (9, "b*", 2, "a?bc+"), (9, "c+", 4, "a?b*c")}))
    guard("⑨懶惰形整段改恰一次（`d+?`→`d`、不留 `?`）；`{…}` 形量詞不產",
          expect(r"d+?e{1,2}f{,2}", {(9, "d+?", 0, "de{1,2}f{,2}")}, absent={(9, "e{1,2}"), (9, "f{,2}")}))
    guard("⑩字元類外之 `\\s` 改 `[ \\t]`；類內 `\\s` 與 `\\s` 以外之類別跳脫（`\\S`／`\\d`）不產",
          expect(r"a\s*b[\s]\S\d", {(10, r"\s", 1, r"a[ \t]*b[\s]\S\d")}, absent={(10, r"\s", 6), (10, r"\S"), (10, r"\d")}))
    guard("⑪分支刪去：逐支（含首支、中支、末支）",
          expect(r"(?:x|y|z)", {(11, "x", 3, "(?:y|z)"), (11, "y", 5, "(?:x|z)"), (11, "z", 7, "(?:x|y)")}))

    def t_invalid():
        ms = generate("P", r"(?<=ab)c")[0]
        bad = [m for m in ms if not m.valid]
        return ([(m.op, m.comp, m.text) for m in bad] == [(2, "ab", r"(?<=(?:ab)?)c")] and all(m.err for m in bad)
                and any(m.op == 7 and m.valid for m in ms)), f"無效 {[(m.op, m.comp, m.text, m.err) for m in bad]}"

    def t_dedupe():
        ms, dups = generate("P", "a|a")
        kept = [m for m in ms if m.op == 11]
        return (len(ms) == 5 and len(kept) == 1 and kept[0].text == "a" and len(kept[0].dups) == 1 and dups == 1), \
            f"{len(ms)} 支／分支刪去 {[(m.comp, m.start, m.text, m.dups) for m in kept]}／去重 {dups}"

    guard("無效變異：後瞻內字面可省＝變寬＝編譯失敗→標無效並附錯誤（有效者照產）", t_invalid)
    guard("去重：`a|a` 兩支分支刪去同文→只留先產一支並註明併入者", t_dedupe)

    def t_full_syntax():
        pat = (r"^(?:pub(?:\([^)\n]*\))?[ \t]+)?(?:const|static)\b(?=x)(?!y)(?<=z)(?<!w)(?P<n>a)\.\x41\u0042\U00000043\0"
               r".{2,3}?b{2}c{,4}d{1,}\s*\S\d\D\w\W[\]\-a-c\s\b\x20]\A\Z\B$")
        tree = parse(pat, re.M, re.compile(pat, re.M).groups)
        return tree is not None and quads(pat, re.M), f"解析 {tree!r}"

    def t_groups_mismatch():
        try:
            parse("(a)(b)", 0, 3)
        except Structural as e:
            return "群組數" in str(e), str(e)
        return False, "未拋結構異常"

    guard("支援語法全集可解析、群組數自我一致", t_full_syntax)
    guard("群組數自我一致不符＝結構異常", t_groups_mismatch)
    for pat, flags, name, off in ((r"(?i)k", 0, "行內旗標", 0), (r"(?i:k)", 0, "行內旗標", 0), (r"(?P<n>a)(?P=n)", 0, "具名反向參照", 8),
                                  (r"(a)\1", 0, "數字反向參照", 3), (r"(a)?(?(1)b|c)", 0, "條件群組", 4), (r"(?>a)", 0, "原子群組", 0),
                                  (r"a\123", 0, "三位八進位跳脫", 1),
                                  (r"a*+", 0, "佔有量詞", 1), (r"(?#c)a", 0, "註解群組", 0), (r"\N{DIGIT ONE}", 0, "具名字元跳脫", 0),
                                  (r"a b", re.X, "re.X", 0)):
        def t_unsup(pat=pat, flags=flags, name=name, off=off):
            try:
                parse(pat, flags)
            except Unsupported as e:
                return name in e.name and e.offset == off, f"{e.name}@{e.offset}"
            return False, "未拋不支援"
        guard(f"不支援構造 `{pat}`→指名「{name}」@{off}", t_unsup)

    # ── 執行面：合成模組與測試、子行程實跑 ──
    with tempfile.TemporaryDirectory() as d:
        base = pathlib.Path(d)
        (base / "rmt_target.py").write_text(SYN_TARGET, encoding="utf-8")
        (base / "rmt_closure.py").write_text(SYN_CLOSURE, encoding="utf-8")
        (base / "rmt_tests.py").write_text(SYN_TESTS, encoding="utf-8")
        paths = [str(base)]

        def quiet(fn, *args):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                got = fn(*args)
            return got, buf.getvalue()

        def run_syn(module, consts, tests):
            return quiet(do_run, paths, module, consts, tests)

        def pairs(rep, status):
            return {(m.op, m.comp) for m in rep["mutants"] if rep["status"].get(m.id) == status}

        def ids_in(text):
            return set(re.findall(r"RE_[A-Z]+#\d+", text))

        def t_weak():
            (rc, rep), out = run_syn("rmt_target", ["RE_P"], ["rmt_tests.Weak"])
            surv = pairs(rep, "survived")
            by = {(m.op, m.comp): m.id for m in rep["mutants"]}
            tail = out.partition("== 存活清單（7 支）\n")[2]
            relax_blk, sep, narrow_blk = tail.partition("  收窄（1 支）：\n")
            grouped = (tail.startswith("  停用（6 支）：\n") and sep and ids_in(relax_blk) == {by[x] for x in SYN_WEAK_RELAX}
                       and ids_in(narrow_blk) == {by[x] for x in SYN_WEAK_NARROW})
            return (rc == 1 and surv == SYN_WEAK_SURVIVORS and pairs(rep, "killed") == SYN_ALL - SYN_WEAK_SURVIVORS
                    and SYN_P_HEADER in out and grouped), f"rc {rc}／存活 {sorted(surv)}\n{out}"

        def t_strong():
            (rc, rep), out = run_syn("rmt_target", ["RE_P"], ["rmt_tests.Strong"])
            return (rc == 0 and pairs(rep, "killed") == SYN_ALL and not pairs(rep, "survived")
                    and (7, "k") in pairs(rep, "killed")), f"rc {rc}／殺 {sorted(pairs(rep, 'killed'))}\n{out}"

        def t_closure():
            (rc, rep), out = run_syn("rmt_closure", ["RE_P"], ["rmt_tests.ClosureStrong"])
            return (rc == 1 and pairs(rep, "survived") == SYN_ALL and (7, "k") in pairs(rep, "survived")), \
                f"rc {rc}／存活 {sorted(pairs(rep, 'survived'))}\n{out}"

        def t_err():
            (rc, rep), out = run_syn("rmt_target", ["RE_P"], ["rmt_tests.Err"])
            kill_lines = [ln for ln in out.splitlines() if ln.startswith("  ✓殺 ")]
            return (rc == 1 and pairs(rep, "killed") == SYN_ERR_KILLED and pairs(rep, "survived") == SYN_ALL - SYN_ERR_KILLED
                    and len(kill_lines) == len(SYN_ERR_KILLED) and all("（fail 0／error 1；含 error）" in ln for ln in kill_lines)
                    and "殺 5（含 error 5、逾時 0）" in out), f"rc {rc}／殺 {sorted(pairs(rep, 'killed'))}\n{out}"

        def t_timeout():
            global CHILD_TIMEOUT_SEC
            saved, CHILD_TIMEOUT_SEC = CHILD_TIMEOUT_SEC, 2
            try:
                (rc, rep), out = run_syn("rmt_target", ["RE_P"], ["rmt_tests.Slow"])
            finally:
                CHILD_TIMEOUT_SEC = saved
            return (rep["status"].get("RE_P#1") == "killed" and "  ✓殺 RE_P#1 ①錨拿掉「^」@0（逾時 2s）" in out
                    and "、逾時 1）" in out), f"rc {rc}／{rep['status']}\n{out}"

        def t_groups_wired():
            real = _child

            def bumped(spec, paths):   # 竄改 probe 回報之 re.compile(原文).groups（+1）：CLI 路徑須據之判不符
                res, dt = real(spec, paths)
                if spec["mode"] == "probe":
                    for info in res["consts"].values():
                        info["groups"] = info.get("groups", 0) + 1
                return res, dt
            globals()["_child"] = bumped
            try:
                rc_l, out_l = quiet(do_list, paths, "rmt_target", ["RE_P"])
                (rc_r, _rep), out_r = run_syn("rmt_target", ["RE_P"], ["rmt_tests.Strong"])
            finally:
                globals()["_child"] = real
            needle = "群組數自我一致不符：解析得捕獲群組 1 個、re.compile(原文).groups＝2"
            return rc_l == 2 and rc_r == 2 and needle in out_l and needle in out_r, f"list rc {rc_l}：{out_l.strip()}／run rc {rc_r}：{out_r.strip()}"

        def t_q_run():
            (rc, rep), out = run_syn("rmt_target", ["RE_Q"], ["rmt_tests.QWeak"])
            st = rep["status"]
            bad = [(m.id, m.op, m.comp) for m in rep["mutants"] if st.get(m.id) == "invalid"]
            k, s = (sum(v == x for v in st.values()) for x in ("killed", "survived"))
            return (rc in (0, 1) and bad == [("RE_Q#3", 2, "ab")] and k + s == 10 and SYN_Q_HEADER in out
                    and "  ∅無效 RE_Q#3 ②字面可省「ab」@4（編譯錯：" in out and "RE_Q#9 ⑪分支刪去「a」@9" in out
                    and "；同文併入：⑪分支刪去「a」@11" in out and f"殺 {k}（" in out and f"存活 {s}／無效 1；" in out), \
                f"rc {rc}／無效 {bad}／殺 {k} 存活 {s}\n{out}"

        guard("弱測試集→指定之七支存活（停用六支＋收窄一支）、其餘四支被殺、rc 1；標頭全文；存活者各落正確分組（停用／收窄）", t_weak)
        guard("強測試集→十一支全殺、零存活 rc 0（含必殺變異⑦刪 `k`）", t_strong)
        guard("替換生效之對照：同一必殺變異對閉包捕獲之模組存活（射程外句實證：全數存活、輸出照列）", t_closure)
        guard("只拋例外（error）之變異記殺、逐支標「含 error」、末行計數含 error 5", t_err)
        guard("子行程逾時（CHILD_TIMEOUT_SEC 暫調 2s、指定變異之下 sleep）→記殺並標逾時、計數逾時 1", t_timeout)
        guard("群組數自我一致之 CLI 接線：probe 回報之 groups 遭竄改＋1→list 與 run 皆 rc 2 指名群組數", t_groups_wired)
        def t_cwd():
            (rc, rep), out = run_syn("rmt_target", ["RE_P"], ["rmt_tests.Cwd"])
            return rc == 1 and "基線：✓ 1 案全綠" in out and pairs(rep, "survived") == SYN_ALL, f"rc {rc}\n{out}"

        guard("run 之無效與去重：無效支標 ∅無效、不計殺或存活；同文併入註記；標頭總數＝有效＋無效＋去重", t_q_run)
        guard("子行程 cwd＝首個 `--path`：斷言 cwd 之合成案基線綠、十一支全存活 rc 1", t_cwd)

        for label, module, consts, tests, needle in (
                ("基線紅（failure）", "rmt_target", ["RE_P"], ["rmt_tests.Red"], "基線（零變異）紅：fail 1／error 0"),
                ("基線紅（只有 error）", "rmt_target", ["RE_P"], ["rmt_tests.BaseErr"], "基線（零變異）紅：fail 0／error 1"),
                ("變異後案數≠基線（存活路徑：多載入之案綠）", "rmt_target", ["RE_P"], ["rmt_tests.Count"], "RE_P#1：案數 2 ≠ 基線 1"),
                ("變異後案數≠基線（殺路徑：紅者只有多載入之案）", "rmt_target", ["RE_P"], ["rmt_tests.CountKill"],
                 "RE_P#1：案數 2 ≠ 基線 1"),
                ("變異後案數≠基線（殺路徑：setUpClass 拋例外致其下各案未跑）", "rmt_target", ["RE_P"], ["rmt_tests.SetupKill"],
                 "RE_P#1：案數 0 ≠ 基線 1"),
                ("逐支變異之子行程未跑成（os._exit）", "rmt_target", ["RE_P"], ["rmt_tests.Crash"], "RE_P#1：子行程未跑成（crash）——子行程 rc=3"),
                ("零案", "rmt_target", ["RE_P"], ["rmt_tests.Empty"], "零案"),
                ("零變異", "rmt_target", ["RE_P", "RE_DOT"], ["rmt_tests.Strong"], "零變異"),
                ("不支援語法", "rmt_target", ["RE_INL"], ["rmt_tests.Strong"], "行內旗標"),
                ("常數為 str", "rmt_target", ["RE_STR"], ["rmt_tests.Strong"], "非已編譯之 str 正則"),
                ("常數為 bytes 正則", "rmt_target", ["RE_BYTES"], ["rmt_tests.Strong"], "非已編譯之 str 正則"),
                ("常數缺席", "rmt_target", ["RE_NOPE"], ["rmt_tests.Strong"], "rmt_target.RE_NOPE：模組無此屬性"),
                ("模組匯入失敗", "rmt_nope", ["RE_P"], ["rmt_tests.Strong"], "匯入"),
                ("測試名載入失敗", "rmt_target", ["RE_P"], ["rmt_tests.NoSuch"], "載入")):
            def t_rc2(module=module, consts=consts, tests=tests, needle=needle):
                (rc, _rep), out = run_syn(module, consts, tests)
                return rc == 2 and needle in out and "error:" in out, f"rc {rc}：{out.strip()}"
            guard(f"run rc 2：{label}", t_rc2)

        def t_list():
            rc, out = quiet(do_list, paths, "rmt_target", ["RE_P"])
            lines = [ln for ln in out.splitlines() if "RE_P#" in ln]
            return (rc == 0 and SYN_P_HEADER in out and len(lines) == len(SYN_ALL)
                    and any("RE_P#1" in ln and "①錨拿掉" in ln and "「^」@0" in ln and "k=([ab]+)$" in ln for ln in lines)), out

        def t_list_q():
            rc, out = quiet(do_list, paths, "rmt_target", ["RE_Q"])
            return (rc == 0 and SYN_Q_HEADER in out and "  ∅無效 RE_Q#3 ②字面可省「ab」@4 → `(?<=(?:ab)?)c|a|a`（編譯錯：" in out
                    and "RE_Q#9 ⑪分支刪去「a」@9 → `(?<=ab)c|a`；同文併入：⑪分支刪去「a」@11" in out), out

        def t_list_zero():
            rc, out = quiet(do_list, paths, "rmt_target", ["RE_DOT"])
            return rc == 2 and "零變異" in out, f"rc {rc}：{out.strip()}"

        def t_bad_path():
            bad = []
            for ps in ([str(base / "rmt_nope_dir")], [str(base / "rmt_target.py")], [str(base), str(base / "rmt_nope_dir")]):
                for cmd, extra in (("list", []), ("run", ["--test", "rmt_tests.Strong"])):
                    argv = [cmd, "--path", *ps, "--module", "rmt_target", "--const", "RE_P", *extra]
                    rc, out = quiet(main, argv)
                    if rc != 2 or f"error: --path 不存在或非目錄：{pathlib.Path(ps[-1]).resolve()}" not in out:
                        bad.append((argv, rc, out.strip()))
            return not bad, f"不符 {bad}"

        guard("list：標頭全文、逐支印 ID、算子、原成分@位移、變異後全文，rc 0", t_list)
        guard("list 之無效與去重：標頭總數＝有效＋無效＋去重、∅無效支附編譯錯、同文併入註記", t_list_q)
        guard("list rc 2：零變異", t_list_zero)
        guard("list 與 run（經 main）rc 2：`--path` 不存在或非目錄——首個不存在、首個為檔案、第二個不存在，皆指名該路徑、不落 traceback", t_bad_path)

    failed = [c for c in cases if not c[1]]
    for i, (name, ok, detail) in enumerate(cases, 1):
        print(f"regex-mutants test {'✓' if ok else '✗'} 案{i} {name}", flush=True)
        if not ok:
            print(f"    實得：{detail}", flush=True)
    if failed:
        print(f"regex-mutants test：{len(failed)}／{len(cases)} 案敗", flush=True)
        return 1
    print(f"regex-mutants test：ok（{len(cases)} 案全綠）", flush=True)
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["test"]:
        return self_test()
    ap = argparse.ArgumentParser(description="正則變異枚舉器（list／run／test）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "run"):
        sp = sub.add_parser(name)
        sp.add_argument("--path", action="extend", nargs="+", required=True, help="sys.path 前置目錄（首個＝子行程 cwd）")
        sp.add_argument("--module", required=True, help="受測模組（含正則常數之模組，點分名）")
        sp.add_argument("--const", action="extend", nargs="+", required=True, help="模組層已編譯正則之屬性名")
        if name == "run":
            sp.add_argument("--test", action="extend", nargs="+", required=True, help="unittest 測試名（點分；模組、類或方法）")
    sub.add_parser("test")
    a = ap.parse_args(argv)
    paths = [str(pathlib.Path(p).resolve()) for p in a.path]
    if a.cmd == "list":
        return do_list(paths, a.module, a.const)
    return do_run(paths, a.module, a.const, a.test)[0]


if __name__ == "__main__":
    sys.exit(main())
