---
id: "LL-00039"
rule_id: "RL-0045"
promotion_surface: none
---
LL-00039｜在 host 端用 `timeout` 包 `docker compose exec … cargo test`，逾時只殺掉 exec 客戶端，容器內的測試程序照活、持鎖不放，守衛 Drop 也不會跑（005 刀 U18）

**徵狀**：005 刀 U18 的審查員在變異探針腳本裡以 host 端 `timeout 1500 docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test …` 跑測試。某支變異令測試自鎖、逾時觸發後，腳本以為該發已結束，接著跑下一發；之後所有碰 `sys_menu`／`casbin_rule` 的測試全數卡住（一輪卡了 28 分鐘）。收尾時 dev 庫 `casbin_rule_id_seq` 自 163 漂到 166，`schema-gate check` 與走查基準 `diff` 雙雙轉紅。

**成因**：`timeout` 送出的訊號只到 host 上的 `docker compose exec` 客戶端；容器內由 exec 起的 cargo 與測試二進位是另一個行程樹，客戶端被殺不會連帶終止它們。殘存的測試行程以「交易中閒置」連線持有列鎖，擋住後續測試；它既然沒被正常結束，帶界守衛的 Drop 就沒跑，植入的殘列與推進過的序列都留在庫裡（殘列其後被別的測試守衛清掉，序列回不去）。

**處置**：主線查容器 `/proc` 確認已無 `deps/` 測試行程、`pg_stat_activity` 無交易中閒置連線後，以空基準快照跑 `python3 tools/walkthrough-baseline.py restore <基準檔>` 讓序列回基線，依其輸出重啟 rust-api，再以 `diff` 與 `schema-gate.py check` 確認 rc 0。

**晉升面**：none——RL-0045 已規定 rust 測試一律容器內 serial；本坑是逾時的寫法，守法句寫進本檔與後續單元定義。

**再犯面與守法**：要替容器內測試設逾時，一律把 `timeout` 放進容器內（`docker compose … exec -T rust-api timeout <秒> cargo test …`），逾時的訊號才會送到容器內的 cargo。每發變異跑完後，先掃一次容器 `/proc`，確認沒有殘存的 `deps/` 行程，再進下一發；出現過逾時，就先查 `pg_stat_activity` 的交易中閒置連線、再對走查基準跑 `diff`。
- 同根之另一觸發形（006 刀 U1；2026-10-02）：主線以 TaskStop 停掉在飛 workflow，agent 經 `docker compose exec` 在容器內起的 cargo 照活（實測該審查員之 `cargo test --no-run` 續跑）。停 workflow 後先以容器 `/proc/*/cmdline` 列行程（rust-api 映像無 `ps`），只終止該 agent 起的那一串、絕不碰 PID 1 之 watchexec 與 `cargo run --bin server`，並刪其容器內 `/tmp` 副本與獨立 target（動輒數 GB）。
- 上列處置之 restore 一步，自 006 刀起可能被 auto mode 權限分類器拒絕（見 LL-00053）：被拒即不繞行，殘留依 LL-00053 之守法處置。
- 同根之另一觸發形（spec-compliance-007 修單 U1；2026-10-17）：逾時已照本條放進容器內，但值短於該次跑測之實耗。規格審查員以 `exec -T rust-api timeout 580 cargo test -p server --bins --tests …` 前景跑，server lib 單支即約 10 分；580 秒到時測試行程被終止、守衛 Drop 沒跑，test_kit 自證案 `nested_guards_reinsert_a_revoked_below_band_policy_row_with_its_original_id` 回插之 `casbin_rule` 列（id 166）與推進過的序列（164→166）留在 dev 庫，其後三支 agent 之走查 `diff` 皆 rc 1、只能升級。誘因＝單元定義「Bash 前景單命令控制在 600 秒內；長跑改丟背景」一句：審查員縮短容器內 timeout 去湊前景時限，沒有改丟背景。處置同上（`/proc` 無殘存行程、`pg_stat_activity` 無交易中閒置 → `restore` → 重啟 rust-api；本次 restore 未被分類器拒絕）。守法：容器內 timeout 須大於該次跑測之實耗上界（含 server lib 者以 1800 秒起），長跑一律丟背景、不得以縮短 timeout 湊前景時限；單元定義之前景時限句同句寫明此點。
