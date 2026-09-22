---
id: "LL-00032"
rule_id: "none：既有紀律 CLAUDE.md §11（drvfs mtime 可能舊到產生假綠增量建置）已涵蓋判準，本則補的是 rust 容器面的具體徵狀與固定起手，不另立規則"
promotion_surface: none
---
LL-00032｜/mnt/d（drvfs）上 host 改檔後，容器內 `cargo build` 可能完全不重編——`Finished in 0.4s` 看起來是綠的，實際驗到的是舊碼

**徵狀**：`maint-backlog-86-90` U2 期間，host 側改完 `rust-api/server/src/**` 後，容器內 `cargo build --workspace --locked` 連跑兩次都回 `Finished dev profile … in 0.4s`、零 `Compiling server`；在容器內對同一檔 `touch` 之後再 build，才出現 `Compiling server`。若不察覺而直接跑 `cargo test`，測到的是改動前的碼——**綠得毫無異狀**。

**成因**：cargo 的 fingerprint 以 mtime 判新舊，而 drvfs（9p）跨 host↔容器的 mtime 傳遞不可靠（CLAUDE.md §11 已記「mtimes can be stale enough to produce false-green incremental builds」）。本則是該通則在 rust 容器面的具體落點：host 的寫入沒讓容器看見新的 mtime，cargo 遂判定「無事可做」。

**處置**：rust 驗證的固定起手改為「**先 touch 受改檔、再 build／test**」——`docker compose … exec -T rust-api sh -c 'touch <改過的檔…>; cargo …'`。本輪起本 repo 的 rust 自驗皆以此形跑，兩次全量測試都在強制重編後執行。

**再犯面與守法**：徵狀是**假綠**而非紅，所以不會有任何閘攔下來——唯一的防線是起手動作。凡「改完 rust 碼、容器內跑 cargo」這條路徑，看到 `Finished` 而沒有 `Compiling` 就要當成警訊；尤其是變異自證（暫改真檔→期待翻紅）那一類，假綠會讓人把「沒翻紅」誤判成「判準無自證」而去改判準，方向完全相反。
