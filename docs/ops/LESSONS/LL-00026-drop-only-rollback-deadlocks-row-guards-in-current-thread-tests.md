---
id: "LL-00026"
rule_id: "none：handler 交易收場形屬碼面慣例、由源碼釘測守（`handler::ip_rule` 之失敗腿 rollback 釘），無對應 RL 條目"
promotion_surface: code
---
LL-00026｜handler 鎖列後以 `?` 上拋、交易只靠 drop 收場→測試斷言一失敗，清列守衛即與未釋放的列鎖互鎖、整輪卡死而不轉紅

**徵狀**：004 刀 U7 對 IP 規則寫端做變異演練（`lock_target` 不驗狀態）時，預期該案轉紅，實得整輪測試卡住 622 秒、無任何 FAILED 訊息；看起來像測試框架或容器掛了，不像判準被打壞。

**成因**：handler 在交易內 `SELECT … FOR UPDATE` 鎖住標的列後回錯，交易物件隨 `?` 上拋被 drop。sea-orm 的 drop-rollback 不是同步送出 ROLLBACK，而是等連線歸池時才補送；`#[tokio::test]` 預設 current-thread runtime，測試本體緊接著斷言失敗→panic 展開→RAII 清列守衛在 Drop 裡對同一列發 DELETE——此時那條連線還沒機會被驅動歸池，列鎖未放，DELETE 等鎖、鎖等 runtime、runtime 被 Drop 裡的阻塞等待佔住＝互鎖。生產面不會卡死（多執行緒 runtime），但同一成因讓列鎖多掛到連線歸池，對併發寫端是無謂的等待。

**處置**：`handler::ip_rule::apply_write` 之失敗腿改為**顯式** `txn.rollback().await` 再回錯（與 login／logout／refresh 三支會話 handler 同形；撞唯一鍵衝突後交易已毒、本來也只能 rollback），並加一支源碼釘測（失敗腿須先 rollback 再 `return Err`——行為面量不到，只能釘源碼）。盤點結果：production 開交易的 handler 恰四支，皆已是顯式 rollback。防法＝凡 handler 在交易內取得列鎖或 advisory lock，失敗腿一律顯式 rollback、不倚賴 drop；新增此類 handler 時比照加源碼釘。測試整輪無訊息卡住時，先查「鎖後上拋＋守衛 Drop 發寫」這個形，再懷疑框架。
