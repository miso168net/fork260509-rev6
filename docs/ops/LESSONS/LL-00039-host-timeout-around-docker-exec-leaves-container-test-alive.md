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
