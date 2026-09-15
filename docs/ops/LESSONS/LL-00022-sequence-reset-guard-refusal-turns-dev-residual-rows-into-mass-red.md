---
id: "LL-00022"
rule_id: "none：結構解已排入 004 ip-trust-anchor（brainstorm grill 輪 G6：廢除 SequenceResetGuard、walkthrough-baseline 之 runtime-append 表序列只比存在性）；過渡防法屬操作紀律（跑真 DB 案前先 walkthrough-baseline diff），無新規則句"
promotion_surface: code
---
LL-00022｜序列重設守衛的「殘列即拒跑」硬化，把 dev 庫一次真登入的殘列放大成會話面全量連坐紅

**徵狀**：spec-compliance 對照審查輪（2026-09-15）跑容器內全量 `cargo test --workspace -- --test-threads=1`，會話面真 DB 案大片紅（交接紀錄約 65 支），錯誤皆為 `SequenceResetGuard 拒絕重設：三表仍有殘列…`，與當輪改動無關；根源是前一日一次瀏覽器真登入在 `sys_token`／`sys_login_attempt` 各留一列。清掉殘列須跑 `walkthrough-baseline restore`，而該指令會被 auto mode 分類器以「不可逆本機破壞」擋下、得請 user 以 `!` 自跑。

**成因**：LL-00017 的處置②把 `SequenceResetGuard` 的 Drop 改為「先數 `sys_token`／`session_event`／`sys_login_attempt` 三表**全部**列數、非零即拒重設並 panic」，以免序列歸 1 撞殘列 id（PK 23505）。但計數對象是全表、不分殘列來源：dev 走查的真帳號列與測試漏列同樣觸發 panic，且每支掛該守衛的測試各自 panic 一次＝一個走查殘列連坐全部會話面案。守衛的立論（測後庫態＝seed 態之可重跑性）本身不承重：三表皆在 schema-gate runtime-append 收窄集、序列值已正規化，序列前進不會讓任何閘紅；前代同一守衛已以同理由廢除（`rev5:B-121`，前身坑 `rev5:L-055`）。

**處置**：過渡——跑真 DB 案前先 `python3 tools/walkthrough-baseline.py diff <基準檔>` 確認庫態、殘列在場時先請 user 以 `!` 跑 restore；結構解——004 ip-trust-anchor 廢除 `SequenceResetGuard`（runtime-append 表序列不重設、各案只清自己寫的列＝`SessionRowsGuard` id 水位形），並把 `walkthrough-baseline diff` 對 runtime-append 四表之序列改比存在性（與 gate2 同口徑）。

**再犯面與守法**：凡「測後復位共享狀態」類守衛，先問其立論在現行閘口徑下是否仍承重，不承重即以「只清自己寫的東西」取代「復位全域狀態」；凡守衛以全表計數當前提，須分辨「本測造成」與「共庫他源」——前者 fail-loud、後者不得連坐。相關：LL-00017（本坑為其處置②的二階後果、非同坑再犯）。
