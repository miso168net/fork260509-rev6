---
id: "LL-00009"
rule_id: "none：本坑＝碼面測試件設計（tracing scoped dispatcher 與行程級 Interest 快取相剋），防法已落 test_kit 本體與其 doc；連跑判準寫進本檔守法、不加規則"
promotion_surface: code
---
LL-00009｜fix 輪新寫的 tracing 捕捉測 flaky——scoped `set_default` 與並行測試共用 callsite 的 Interest 快取競態

**徵狀**：002 刀 U2 碼品質 fix 輪新寫 `rust-api/server/src/auth/enforce.rs` 之 `entrypoint_logs_root_cause_before_mapping_evaluation_failure_to_internal`，agent 回報單趟綠；主線收尾自驗第一趟綠、第二趟紅（捕得空字串 `""`）；`cargo test -p server --lib` 連跑十趟兩趟紅。同構的 facade 側 `roles_of_user_db_error_is_logged_before_internal` 從未紅。

**成因**：`test_kit::capture` 用 `tracing::subscriber::set_default`（thread-local scoped dispatcher）承接；tracing 的 callsite Interest 快取卻是**行程級**——那支 error! callsite 另被兩支不捕捉的測試（求值失敗翻 5000 案、三判定計數案）打到，並行下先由它們對「無 live dispatcher」註冊即算成 never 並快取，之後捕捉窗口內的事件在 macro 層 `!interest.is_never()` 就被丟掉。facade 側 callsite 只在捕捉窗口內被打、故從未紅。fix agent 單趟綠即回報、主線首趟也綠——單趟綠不是「非 flaky」的證據面。

**處置**：`capture` 改為行程唯一全域 subscriber（`Once`＋`init`、另有人裝全域即 panic 不靜默捕空）＋thread-local 緩衝（writer 依發出執行緒路由；`#[tokio::test]` current-thread runtime 保證 future 與緩衝同執行緒；他測事件落自己執行緒、無緩衝即丟棄）。改後連跑十趟零紅、workspace 全綠。

**晉升面**：code——防法住 `rust-api/server/src/model/facade/test_kit.rs` 本體與其 doc：凡「先落 log 再翻 5000」類斷言一律走 `capture`、不自建 scoped dispatcher。

**再犯面與守法**：凡單元新增的測試涉**行程級全域狀態**（tracing dispatcher／metrics recorder／thread-local 旗標／環境變數），收尾②自驗對該測試二進位連跑 ≥5 趟（`for i in 1 2 3 4 5; do cargo test -p server --lib || break; done`）、零紅才算綠；agent 回報「測試綠」一律視為單趟證據。
