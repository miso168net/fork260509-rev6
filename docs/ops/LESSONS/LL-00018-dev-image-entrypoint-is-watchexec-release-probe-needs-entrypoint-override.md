---
id: "LL-00018"
rule_id: "none：一次性配方——release 探針正確形已寫入 U11 定義與本坑檔，非規則句"
promotion_surface: none
---
LL-00018｜「以 release 二進位起服務打 /health」的探針配方跑的其實是 debug 二進位——dev 映像的 ENTRYPOINT 是 watchexec，`compose run <svc> <路徑>` 只換得到 command

**徵狀**：003 刀 U4（run `wf_b02d894e-b57`）單元定義給 T021 release DoD 的配方＝`docker compose … run --rm --no-deps -d --name rev6-u4-release-probe rust-api /app/target/release/server`，implementer 照跑、`/dev/tcp` 探 `/health` 得 `ok`、report 判 release 首次可跑成立。規格審查第 1 輪自行複現：`docker logs` 原文 `[Running: cargo run --bin server /app/target/release/server]`、`Running \`target/debug/server /app/target/release/server\``；`docker inspect --format '{{json .Config.Entrypoint}}'` ＝ `["watchexec","-r","-e","rs,toml","--poll","1s","--","cargo","run","--bin","server"]`——release 路徑被當成 watchexec 的參數餵給 `cargo run`，起來的是 debug 二進位；release 二進位從未被執行過、DoD 的機器證是假的。

**成因**：dev override（`docker-compose.dev.yml`）給 rust-api 的是 watchexec 熱重載 ENTRYPOINT；`docker compose run <service> <args>` 的語意是「換 command、保留 entrypoint」，配方作者把它當成「直接執行那個路徑」。探針只看 `/health` 回 `ok`，而 debug 與 release 二進位的 `/health` 回包相同，探針本身分不出誰在跑——DoD 少了「證明跑的是 release 那支」的判別器。

**處置**：fix 輪改以 `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps -d --name <probe> --entrypoint /app/target/release/server rust-api` 起服務（entrypoint 覆寫、零 watchexec、零 cargo），`docker logs` 首行即 server boot log、無 `cargo run` 字樣，再自 dev 容器 `/dev/tcp` 探 `/health`；`docker stop` 後 `--rm` 自清。U4 單元定義的錯誤配方不改（已跑完的 tmp 工件）；正確配方寫入 U11（T076 release DoD）定義。

**再犯面與守法**：凡「在容器裡跑某支二進位」的配方，先 `docker inspect --format '{{json .Config.Entrypoint}}'` 看清 ENTRYPOINT，entrypoint 非 shell／非該二進位者一律加 `--entrypoint`；凡 DoD 是「某支二進位可跑」，探針 MUST 帶判別器（`docker logs` 無 `cargo run`／`Running \`target/debug/…\`` 字樣，或 `ps` 見該路徑），不得只看回包——debug 與 release 的回包本來就一樣。屬一次性配方、不立規則句；正確配方之家＝U11 定義（tmp）與本檔。
