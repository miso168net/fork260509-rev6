---
id: "LL-00061"
rule_id: "none：同 LL-00032／LL-00056（cargo 以 mtime 判新舊之假綠）；本則補的是「寫回端」與 dev 伺服器（watchexec）之形，守法寫進本檔與演練腳本"
promotion_surface: none
recurrence_of: "LL-00056"
---
LL-00061｜變異演練以 `cp -p` 寫回原檔，連 mtime 也還原成舊值：dev 伺服器在變異寫入時已被 watchexec 重編，寫回後 cargo 判新鮮不重編，之後的 API 走查一直打在拆掉守門的二進位上（006 刀 U18）

**徵狀**：006 刀 U18 T087 quickstart 走查 §3，對自建的非 R_SUPER 角色以 updateRoleEndpoints 授予封死集端點（`updateRoleEndpoints POST`），得 `0000`、新授 1，期望是 `2222 biz.role.protectedGrant`。§5 的回收桶清單與復原因此連鎖偏差。同一時段的兩次容器內全量（T086 ⑤、T087 §9）卻全綠，封死三案也在其中；只有打 dev 伺服器的 API 走查放行。

**成因**：
- T086 ④ 把封死守門改成恆假、寫入 `sys_casbin_policy.rs` 的當下，dev 容器的 watchexec 就觸發 `cargo run`，重編出含變異的 dev 二進位。
- 演練腳本以 `cp -p` 寫回原文：內容還原了，mtime 也還原成前一天的舊值。cargo 以 mtime 判新舊，舊 mtime 早於變異產物，於是判「無事可做」。之後兩次重啟 rust-api（T086 ⑤、T087 §10），`cargo run` 都只見 `Finished`、零 `Compiling`，續跑變異碼。
- 測試面沒被波及：演練以 `cargo test -p server …` 建置，全量以 `--workspace` 建置，兩者產物不同組；後者最後一次編譯在演練之前（T085），兩次全量用的都是乾淨產物。中招的只有 dev 伺服器，所以只有 API 走查看得到。
- LL-00032／LL-00056 的守法框在「改檔後要讓 cargo 看見新 mtime」。本形出在寫回端：寫回也是一次改檔，`-p` 把讓 cargo 看見的那一下抹掉了。

**處置**：
- 系統化取證：被變異檔 mtime 停在前一天；dev 二進位建於 ④ 變異窗內；容器 log 中變異寫入時有 `Compiling server`，其後兩次重啟皆無。
- 修復：touch 四支演練檔，watchexec 觸發 `Compiling server`，換上新二進位。
- 驗證：T087 整支重跑，§3 封死授予得 `2222 biz.role.protectedGrant`、零同步，§5 連鎖各項皆符期望；首跑的錯授列已於該次 §10 restore 清回基準（diff rc 0）。
- 演練腳本寫回改為不帶 `-p` 之 `cp`，並於寫回後 touch。

**晉升面**：none——守法寫進本檔與演練腳本。這是同一機制的第三次（LL-00032、LL-00056、本則）；要不要晉升為規則，交收刀時裁定。

**再犯面與守法**：
- ①演練寫回一律不保 mtime（`cp` 不帶 `-p`，或寫回後 `touch`），讓 cargo 看見寫回這一下。
- ②變異演練之後、任何打 dev 伺服器的走查之前，先自證伺服器已是乾淨碼：dev 容器 log 在寫回之後見 `Compiling server`，或 `target/debug/server` 的 mtime 晚於寫回時刻。
- ③走查中封死、受保護拒等安全面斷言意外放行時，先查 dev 二進位是否為變異殘留，再查產品碼。
