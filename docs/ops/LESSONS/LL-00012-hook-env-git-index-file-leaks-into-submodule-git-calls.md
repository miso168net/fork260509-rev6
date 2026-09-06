---
id: "LL-00012"
rule_id: "none：hook 期間子行程 git 的環境隔離屬工具實作面、非流程規則；守法寫進 docsync 呼叫慣例與本檔"
promotion_surface: code
---
LL-00012｜pre-commit 期間 git 匯出的 `GIT_INDEX_FILE`／`GIT_DIR` 指外層 repo——子庫 `git -C <子庫> ls-files` 讀到外層 index 回空，測試直跑綠、hook 內紅

**徵狀**：maint-backlog-25 落 `tools/docsync/vendored.py`（例外①自證）後，`python3 tools/docsync test` 直跑 174 案全綠、`vendored-check` 綠；同一批 `git commit` 時 pre-commit 之 selftest-docsync 紅在 `test_real_adapter_matches_rev5_with_named_exceptions`：`tracked_files()` 之 `git -C rust-api ls-files sea-orm-adapter` 回空清單→「掃描面空集合」。

**成因**：git 執行 hook 時匯出 `GIT_INDEX_FILE`（有時含 `GIT_DIR`／`GIT_WORK_TREE`）指向**外層** repo 的 index；子行程對子庫下 `git -C rust-api …` 會沿用該環境、對外層 index 查詢子庫路徑＝零命中。既有 docsync 之 `Ctx.git` 只對外層 repo 操作、恰好不受影響，故此坑到首個「hook 內對子庫呼叫 git」的工具才現形（hook 檔頭記的是反向坑：容器不帶 `GIT_INDEX_FILE`→`git commit -a` 掃 0 bytes）。

**處置**：`vendored.tracked_files` 子行程改用剝掉一切 `GIT_*` 的環境（`{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}`）；以 `GIT_INDEX_FILE=<外層 index> GIT_DIR=<外層 .git>` 模擬 hook 環境直跑真 repo 案綠、再 commit 過（hook 內 174 案 OK）。

**晉升面**：code（`tools/docsync/vendored.py`）＋本檔守法；不立規則。

**再犯面與守法**：凡工具可能在 hook 內執行且對**子庫**下 git（`git -C base-web|rust-api …`），子行程一律剝 `GIT_*` 環境；新增此類呼叫時以 `GIT_INDEX_FILE="$PWD/.git/index" GIT_DIR="$PWD/.git" python3 …` 直跑一次當反例證。診斷捷徑：「直跑綠、hook 內紅」＋涉子庫 git ＝先查環境變數、不是查邏輯。
