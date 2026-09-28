---
id: "LL-00034"
rule_id: "RL-0011"
promotion_surface: none
---
LL-00034｜tests/ 共用件 doc 以窮舉形寫「消費者＝…」——每進一個新消費者即成名冊假述，而共用件檔多不在該單元允許清單內、agent 只能升級（005 刀 U1、U2 連兩單元同坑）

**徵狀**：005 刀 U1 新增真 seed 案 `role_menu_authz_matrix_real_seed` 後，`rust-api/server/tests/common/mod.rs` 三個共用件（`real_seed_app_with_cache_and_db`、`SessionKeysGuard`、`send_with_headers`）doc 的「消費者＝」窮舉皆未列新案，implementer 因檔在允許清單外升級、主線收尾自改（兩句補列、`send_with_headers` 一句改不枚舉形）。緊接的 005 刀 U2 新增 `ip_rule_list_paging_real_seed`，同檔三句（`real_seed_app_with_cache_and_db`、`IpRuleWriteGuard`、`SessionKeysGuard`）再度全數漏列——規格審查第二輪的唯一 blocker 就是它，fix agent 仍因檔在清單外只能 `done_with_escalation`、該輪 fix 空轉。

**成因**：窮舉形名冊句住共用件檔，真相卻住消費端檔：新消費者在消費端落地時，共用件檔不在（或只以限定式在）該單元允許清單內，RL-0022 使 agent 只能升級；RL-0011 的種子③④偏重同檔鏡像，跨檔的消費者名冊要以共用件名 grep 才撈得到，implementer 常漏這一腿。U1 主線補列時保留了窮舉形，下一單元照樣漂——補列只修當次、不修成因。

**處置**：005 刀 U2 收尾主線把三句一律改不枚舉形（「消費者＝tests/contract.rs 的某類真 DB 案（逐處以 grep 為準、本句不枚舉）」），併入該單元 rust-api commit；後續單元的單元定義 CONTEXT 烤入同一寫法（新共用件的 doc 亦同）。

**晉升面**：none——RL-0011 已含名冊假述義務；本坑＝寫法，記本檔守法即可。

**再犯面與守法**：多消費者共用件（`tests/common`、`test_kit` 之類）的 doc 一律不枚舉消費者：寫消費者的類別描述＋「以 grep 為準」；確實需要守住的消費者集合改用名冊常數＋測試對賬（RL-0026），不寫散文枚舉。主線或 fix 碰到他人漏列的窮舉句時，改寫成不枚舉形、不補列。
