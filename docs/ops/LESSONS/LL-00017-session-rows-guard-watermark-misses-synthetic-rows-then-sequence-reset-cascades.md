---
id: "LL-00017"
rule_id: "none：守法已落碼——test_kit 守衛之水位清理（合成 uid 無水位清列、真帳號水位取序列 id）＋自證案；序列重設守衛已於 004 刀 U3 廢除（結構解見本檔補述段）；無新規則句"
promotion_surface: code
---
LL-00017｜真 DB 測試守衛以「arm 水位」清列、合成帳號的殘列漏在水位之前，序列守衛照樣歸 1，下一跑 PK 23505 連環紅且自我延續

**徵狀**：003 刀 U4（run `wf_b02d894e-b57`）碼品質 fix 輪連跑兩次全量 `cargo test --workspace -- --test-threads=1`：第一次全綠、第二次 8 支紅（`sys_token::tests` 六支＋`test_kit::tests` 二支），首行錯誤＝`duplicate key value violates unique constraint "sys_token_pkey"`、`Key (id)=(1) already exists`；庫中殘留一列 `created_by = 9300000001`（合成 uid）、`created_at` 落在前一次全量跑內。同一單元第 3 輪 fix 再撞一次：`session_event` 殘留兩列（`user_id = 9300000015`＝合成 uid、`session_event::tests` 的 kicked／logout 兩事件），`session_event_id_seq` 停在 seed 值 `(1, false)`，`nextval` 第二發即撞 PK；agent 因權限無法 DELETE、自驗停擺、整輪升級。兩案皆非 U4 改動所致（`session_event.rs`／`sys_token.rs`／兩支守衛零 diff）。

**成因**：`SessionRowsGuard` 的清列條件是「鍵集 ∧ `created_at ≥ arm 時 DB `now()` 水位」——設計目的是不誤刪 dev 走查留下的真列。但兩件事疊在一起：①水位形對「並發交易」與「被中斷的跑次」不穩——`concurrent_txns_second_active_insert_yields_identifiable_db_err` 的 committed 列間歇性落在水位之前（交易時鐘與 arm 時鐘的邊界）、被殺的 cargo 跑次則 Drop 根本沒跑；②`SequenceResetGuard` 在 Drop 時**無條件** `setval(seq, 1, false)`，殘列與序列歸 1 併存＝下一次 `nextval` 落在殘列 id 上。更糟的是水位形**永遠掃不回舊殘列**（每次 arm 的水位都在殘列之後），故一旦漏一列就每輪必紅、自我延續，只能靠人手 psql 清。rev5 的 `rev5:L-055` 已記過同一機制，rev6 承襲時只在 `SequenceResetGuard` doc 寫了「只在三表測後零列前提下成立」的代價句、沒有機器守。

**處置**：主線於 U4 收尾硬化 `test_kit.rs` 兩支守衛（碼面）：①`SessionRowsGuard` 對合成 uid（≥ `SYNTHETIC_UID_FLOOR = 9_300_000_000`，各案自造的假帳號一律落此界）**不套水位、無條件清列**——合成帳號不可能有 dev 走查真列，故 blanket DELETE 對它安全；真帳號（seed uid 1／2／3）維持水位形；②`SequenceResetGuard` Drop **先數三表**，任一表非零即拒絕重設並 fail-loud 指名列數（不重設則 id 續走、不連坐後續跑次），三表皆零才 `setval`。自證兩案：合成 uid 之 arm 前一小時列於 Drop 清掉／有殘列時 Drop panic 且序列不動。當次殘列與 redis 測試殘鍵由主線 psql／redis-cli 清掉。

**再犯面與守法**：凡「清理守衛靠時間水位」的設計，對測試自造的合成身分一律改用身分條件（無水位）、水位只留給與真資料共庫的真身分；凡「重設序列」類守衛一律先驗證前提（表空）再動手、前提不成立即 fail-loud 而非靜默執行——把「間歇性連環紅」變成「當場一案紅、訊息指名列數」。守法已落碼（`test_kit.rs` 兩支守衛＋自證案），無新規則句；dev 走查後的清理紀律仍＝data-model §9／RUNBOOK §9c。

**補記（003 刀 U5 收尾）**：真帳號腿的時間戳水位在同一單元再暴一次、根因更深——postgres 容器 `clock_timestamp()` **非單調**（WSL2／Docker Desktop 時鐘同步；fix 輪取樣 20 秒 59,609,479 次、倒退 2 次、最大 1.397636 秒；主線復測 15 秒 53,642,564 次零倒退＝倒退是間歇事件、不可靠重現）。決定性直證＝login 三帳號案某次紅跑：arm 水位 `07:42:36.876968`，其後**最後**登入者之 `sys_token` 列（id 最大）`created_at` 卻＝`07:42:36.230802`、早於水位 0.646 秒，先登入的兩列反被刪——id 遞增而時間戳倒序，排除測試邏輯錯序。後果鏈＝漏刪一列→撞上文②之殘列前檢 fail-loud→其後每支真 DB 測連鎖紅（單次 19～24 支）、殘列留庫下一跑起手即紅；乾淨基準全套四跑一紅。處置：`SessionRowsGuard` 水位自 DB 時間戳改為三表**序列 id 高水位**（arm 取各表 `COALESCE(max(id), 0)`、Drop 改 `id >` 水位；合成 uid 腿不變）——id 由 `nextval` 產、嚴格單調、對時鐘倒退免疫；自證案＝arm 後植入 `created_at` 早一小時之列於 Drop 仍清掉（時間戳形必紅、id 形綠，紅→綠實跑取證）。守法補一句：凡以「DB 時間戳 ≥ 某刻」界定「我寫的列」的清理與斷言，在容器時鐘可倒退的環境一律改以序列 id 定界；仍以牆鐘做窗的讀端與測試面另記 BL-00051、不在本坑內硬改。

**補述（004 刀 U3：G6 結構解）**：上文處置②「先數三表、有殘列即拒絕重設」的守衛本身成了下一個坑——dev 庫一列真登入殘列就連坐會話面全量紅（LL-00022）。004 刀 U3 以結構解收掉、三件：①**廢除守衛**——`SequenceResetGuard` 整支拿掉；它的立論「測後庫態＝seed 態」在 gate2 現行口徑下不承重（前代同一處置＝`rev5:B-121`）。②**水位清理**——會話三表與 `sys_operation_log` 屬 runtime-append 收窄集（名冊單一權威＝`tools/schema-gate.py` 之 `RUNTIME_APPEND_TABLES`），序列只前進、不復位，各案只清自己寫的列（`SessionRowsGuard`／`OpLogRowsGuard` 的 id 高水位形；合成 uid 腿不變）；收窄集外的業務表 `sys_ip_rule` 方向相反——序列落值在 gate2 比對面內，由 `IpRuleRowsGuard` 還原到 arm 當下現讀的 `(last_value, is_called)`；兩套紀律不可互相套用。③**序列存在性口徑**——`tools/walkthrough-baseline.py diff` 對 runtime-append 四表的 id 序列只比存在性、不比值（與 gate2 對其 setval 值正規化同口徑；名冊與 schema-gate 同值、由該工具自測對賬），`restore --seed` 也不復位這四支序列。紀律全文住 `rust-api/server/src/model/facade/test_kit.rs` 檔頭「序列紀律」段與 `specs/004-ip-trust-anchor/data-model.md` §7。守法隨之改句：上文「重設序列類守衛先驗前提再動手」已無對象，現行守法＝「只清自己寫的列、不復位共享序列；非復位不可的業務表序列，還原值取 arm 當下現讀」。
