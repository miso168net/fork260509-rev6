---
id: "LL-00013"
rule_id: "none：把 docstring 當資料讀的地方目前只有 gates.parse_gate_blocks 一處，守法已釘在該 regex 上方註解與 test_gate_id_survives_docstring_dedent；再犯面窄（新增同類解析器時才成立），不值一條規則"
promotion_surface: code
---
LL-00013｜把 docstring 當資料解析的 regex 強制行首縮排——Python ≥3.13 編譯期剝掉共同縮排後 12 支閘 id 全回 None、GATES.md 算成空表、GT-05 滿地「真源查無」假紅

**徵狀**：新機（macOS、Homebrew python3 3.14.4）跑 `bash tools/bootstrap.sh` 於 docsync 自測 exit 2：10 案紅、`GT-01` 對 `docs/generated/GATES.md` 報漂移、`GT-05` 報 322 筆「引用 GT-NN 但真源查無（gates ROSTER）」——連 `CLAUDE.md` 自己寫的 `GT-02` 都被判查無。表象像名冊全毀，實際上 `parse_gate_blocks` 對**原始碼文字**仍正確解出 12 個區塊。

**成因**：`RE_GATE_BLOCK` 以 `[ \t]+`（至少一個行首空白）匹配 `key=value` 行，而同一個 regex 吃兩種輸入——原始碼文字（縮排在）與 `gate_id()` 傳入的 `fn.__doc__`。Python 3.13 起編譯期會剝掉 docstring 的共同縮排（gh-81283），`fn.__doc__` 變成 `GATE:\nid=GT-01\n…` 零縮排，`gate_id()` 遂對 12 支閘全回 `None`：`gen_gates_md` 表身以 `gid + "."` 拼豁免鍵時先 `TypeError`（None + str），GATES.md 重算成無列空表→GT-01 漂移；`gt_05` 的 ID 存在性真源取自 `{gate_id(g) for g in ROSTER}`＝`{None}`→全 repo 每一處 GT-NN 引用都成假紅。單一根因、十案連坐。

**處置**：`[ \t]+` → `[ \t]*`（縮排 0 或多都吃；對 3.12 舊機語意不變）＋該行上方註解記明「同一 regex 吃兩種輸入」＋`test_gate_id_survives_docstring_dedent` 以合成 `__doc__` 釘死行為。取證：舊 regex 下新測案紅（`gate_id()` 回 `None`、取不到合成區塊的 id）、修正後 250 案全綠、`docsync check` 零漂移——零漂移即證明修正後產出與既有生成檔逐 byte 相同，是還原原意而非改變行為。

**晉升面**：code（`tools/docsync/gates.py` 之 regex 與註解、`tools/docsync/tests/test_gates.py` 之迴歸案）；不立規則。

**再犯面與守法**：凡把 `__doc__`／`__annotations__` 等**編譯期會被加工**的物件當資料解析者，測案一律以合成字串釘死行為、不要只靠「真 package 掃出來對不對」——後者在開發機的 python 版本上恆綠，換版本才炸（本坑的既有測案 `test_blocks_anchors_roster_on_real_package` 正是這一型）。診斷捷徑：ID 存在性類的閘一次噴上百筆、連文件自己寫的編號都判查無＝先懷疑「真源集合算成空的」，不是逐處去查引用。
