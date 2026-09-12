---
id: "LL-00017"
rule_id: "none：守法已落碼——test_kit 兩支守衛硬化（合成 uid 無水位清列、序列重設前檢殘列拒絕）＋自證兩案；無新規則句"
promotion_surface: code
---
LL-00017｜真 DB 測試守衛以「arm 水位」清列、合成帳號的殘列漏在水位之前，序列守衛照樣歸 1，下一跑 PK 23505 連環紅且自我延續

**徵狀**：003 刀 U4（run `wf_b02d894e-b57`）碼品質 fix 輪連跑兩次全量 `cargo test --workspace -- --test-threads=1`：第一次全綠、第二次 8 支紅（`sys_token::tests` 六支＋`test_kit::tests` 二支），首行錯誤＝`duplicate key value violates unique constraint "sys_token_pkey"`、`Key (id)=(1) already exists`；庫中殘留一列 `created_by = 9300000001`（合成 uid）、`created_at` 落在前一次全量跑內。同一單元第 3 輪 fix 再撞一次：`session_event` 殘留兩列（`user_id = 9300000015`＝合成 uid、`session_event::tests` 的 kicked／logout 兩事件），`session_event_id_seq` 停在 seed 值 `(1, false)`，`nextval` 第二發即撞 PK；agent 因權限無法 DELETE、自驗停擺、整輪升級。兩案皆非 U4 改動所致（`session_event.rs`／`sys_token.rs`／兩支守衛零 diff）。

**成因**：`SessionRowsGuard` 的清列條件是「鍵集 ∧ `created_at ≥ arm 時 DB `now()` 水位」——設計目的是不誤刪 dev 走查留下的真列。但兩件事疊在一起：①水位形對「並發交易」與「被中斷的跑次」不穩——`concurrent_txns_second_active_insert_yields_identifiable_db_err` 的 committed 列間歇性落在水位之前（交易時鐘與 arm 時鐘的邊界）、被殺的 cargo 跑次則 Drop 根本沒跑；②`SequenceResetGuard` 在 Drop 時**無條件** `setval(seq, 1, false)`，殘列與序列歸 1 併存＝下一次 `nextval` 落在殘列 id 上。更糟的是水位形**永遠掃不回舊殘列**（每次 arm 的水位都在殘列之後），故一旦漏一列就每輪必紅、自我延續，只能靠人手 psql 清。rev5 的 `rev5:L-055` 已記過同一機制，rev6 承襲時只在 `SequenceResetGuard` doc 寫了「只在三表測後零列前提下成立」的代價句、沒有機器守。

**處置**：主線於 U4 收尾硬化 `test_kit.rs` 兩支守衛（碼面）：①`SessionRowsGuard` 對合成 uid（≥ `SYNTHETIC_UID_FLOOR = 9_300_000_000`，各案自造的假帳號一律落此界）**不套水位、無條件清列**——合成帳號不可能有 dev 走查真列，故 blanket DELETE 對它安全；真帳號（seed uid 1／2／3）維持水位形；②`SequenceResetGuard` Drop **先數三表**，任一表非零即拒絕重設並 fail-loud 指名列數（不重設則 id 續走、不連坐後續跑次），三表皆零才 `setval`。自證兩案：合成 uid 之 arm 前一小時列於 Drop 清掉／有殘列時 Drop panic 且序列不動。當次殘列與 redis 測試殘鍵由主線 psql／redis-cli 清掉。

**再犯面與守法**：凡「清理守衛靠時間水位」的設計，對測試自造的合成身分一律改用身分條件（無水位）、水位只留給與真資料共庫的真身分；凡「重設序列」類守衛一律先驗證前提（表空）再動手、前提不成立即 fail-loud 而非靜默執行——把「間歇性連環紅」變成「當場一案紅、訊息指名列數」。守法已落碼（`test_kit.rs` 兩支守衛＋自證案），無新規則句；dev 走查後的清理紀律仍＝data-model §9／RUNBOOK §9c。
