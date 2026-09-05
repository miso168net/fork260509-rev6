<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
<!-- next: LL-00010 -->
# LESSONS — 教訓索引（機器生成；一坑一檔住 LESSONS/LL-NNNNN-<slug>.md）

配號＝本檔頭 next（自檔集最大號＋1 推導；ADR-00005）→ 建檔 → `python3 tools/docsync generate`。條目檔 frontmatter：`id`、`rule_id`（RL-NNNN 或 none：理由）、`promotion_surface`（rules／gate／code／none）、選填 `recurrence_of`；正文首行 `LL-NNNNN｜坑名`（GT-08 對賬）。

| LL | 坑名 | rule_id | promotion_surface | 檔 |
|---|---|---|---|---|
| LL-00001 | 零種子 fresh resolve 讓 Cargo.lock 拉到 toolchain 不支援的新版 crate（tinyvec 1.13.0 vs rustc 1.96.1） | none：Cargo.lock 已入版控後，後續單元的 cargo 自然以現有 lock 為種子、零種子情境只出現在 workspace 首建；再犯面極窄（新 workspace 或刻意刪 lock）、不值一條規則，留本檔供 002 刀 server crate 進場時對照 | none | [LL-00001-cargo-lock-zero-seed-resolve.md](LESSONS/LL-00001-cargo-lock-zero-seed-resolve.md) |
| LL-00002 | fix 升級後的續跑：骨架不支援只跑審查段、主線落地又未先自掃同語意列舉——兩支續跑 run 各被 README 一行打回 | none：RL-0010（續跑＝新開只跑該階段的 run）與 RL-0011（同語意命中逐處改對）條文已在；本坑＝主線落地升級項後未先自掃就發射續跑、兩條未被串起——守法寫進本檔與組裝流程，不加規則 | none | [LL-00002-review-only-continuation-and-enumeration-sweep.md](LESSONS/LL-00002-review-only-continuation-and-enumeration-sweep.md) |
| LL-00003 | hook 面演練還原用 `git checkout -- <路徑>`，檔案已 staged 時是從 index 取、不是從 HEAD 取 | RL-0005 | none | [LL-00003-checkout-restores-from-index-not-head.md](LESSONS/LL-00003-checkout-restores-from-index-not-head.md) |
| LL-00004 | 能力落地的單元只掃了字面詞、沒掃「隨…刀進場／尚無…」形——現在式面留下五處假述，多花一輪審查與升級 | RL-0015 | rules | [LL-00004-capability-landing-future-tense-sweep.md](LESSONS/LL-00004-capability-landing-future-tense-sweep.md) |
| LL-00005 | bind-mount 來源檔缺席時 compose 代建目錄佔位，補上真檔後舊容器仍掛目錄形——`up -d --wait` 報 mount source path 已存在 | none：環境層一次性坑（drvfs＋Docker Desktop bind-mount 的目錄佔位快取）、非流程規則可承；解法記於本檔與 RUNBOOK §1 步驟 4 徵狀句即可 | none | [LL-00005-compose-bind-mount-dir-placeholder-stale-cache.md](LESSONS/LL-00005-compose-bind-mount-dir-placeholder-stale-cache.md) |
| LL-00006 | 能力落地後只掃了能力名與未來式短語、沒掃「數量詞」——同一檔 §5.1 改對、§5.2「三 crate」留假述，確認輪多跑一輪 | RL-0011 | none | [LL-00006-count-word-sweep-missed-in-same-file.md](LESSONS/LL-00006-count-word-sweep-missed-in-same-file.md) |
| LL-00007 | 生成物名冊 14→15 時 README 只補了 tasks 條指名的樹行、「想知道 X 看 Y」查詢表漏列——LL-00002 點名的三處列舉面再犯一處 | RL-0011 | none | [LL-00007-readme-lookup-table-missed-on-roster-growth.md](LESSONS/LL-00007-readme-lookup-table-missed-on-roster-growth.md) |
| LL-00008 | 碼內具名預告的回填條靠審查員清單補、未自行機器枚舉——第二輪補四條、第三輪又抓一組 | RL-0015 | none | [LL-00008-foretold-backfill-inventory-by-grep.md](LESSONS/LL-00008-foretold-backfill-inventory-by-grep.md) |
| LL-00009 | fix 輪新寫的 tracing 捕捉測 flaky——scoped `set_default` 與並行測試共用 callsite 的 Interest 快取競態 | none：本坑＝碼面測試件設計（tracing scoped dispatcher 與行程級 Interest 快取相剋），防法已落 test_kit 本體與其 doc；連跑判準寫進本檔守法、不加規則 | code | [LL-00009-scoped-tracing-capture-flaky-under-parallel-tests.md](LESSONS/LL-00009-scoped-tracing-capture-flaky-under-parallel-tests.md) |
