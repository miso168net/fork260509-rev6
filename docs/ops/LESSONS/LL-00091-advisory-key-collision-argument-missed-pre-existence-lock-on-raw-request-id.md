---
id: "LL-00091"
rule_id: "none：守法在 advisory key 空間論證之寫法（設計審查紀律）與碼面守門（`handler::user::guard_account_key`＋其整合案），不另立規則"
promotion_surface: none
---
LL-00091｜advisory key 不碰撞論證只看「真實 uid 的值域」，漏算取鎖早於存在性判定、key 直取請求原值——請求 id 恰等選單域 key 即取走域鎖（007 刀 final holistic review）

**徵狀**：
- 使用者域七支寫端（updateUser、deleteUser、batchDeleteUser、restoreUser、kickUser、resetUserPassword、updateUserSessionPolicy）在內層首句以標的 id 取帳號級 `pg_advisory_xact_lock`，之後才鎖讀現役列判查無。帳號鎖與選單序列化域鎖同屬單 bigint key 空間。
- research R7 第 6 款與活書 06 據「uid 由 bigserial 自個位數起配、域 key＝ASCII `rev6menu`≈8.2×10^18」推論 key 空間不碰撞、鎖集合零交集（ADR-00043 決定 8 前提①）。final holistic review 以 `{"id": 8243124669107236469}` 打 updateUser：回應仍是 `notFound`，但交易已取走選單域鎖、與並行之選單／角色刪除家族互相排隊；批刪夾一個真 uid 時更在同一交易兼持域鎖與帳號鎖。
- 補整合案（外部交易持域鎖→七支各以 id＝域 key 送出）在修前全數逾時排隊。

**成因**：
1. 碰撞論證的論域取「存在的帳號 id」，但取鎖的 key 是請求原值、且取鎖早於存在性判定（lock-then-redecide 形的固有次序）——請求可以送任何 i64。
2. 結構案只釘「首句取鎖、key＝標的 id 參數」之源碼形，不涉 key 的值域；wire 回應在碰撞與否時同為 `notFound`，行為案與走查都看不出來。

**處置**：七支外殼於 begin 前以 `guard_account_key` 把 id 限在 (0, 2^53]（上界＝wire 之 JSON number 可逆界、取 `envelope::MAX_SAFE_INTEGER`），域外＝`notFound`、零 begin 零鎖——wire 不變；`sys_user::advisory_lock_user` doc 補呼叫端義務；活書 06 兩句改述 key 來源；整合案 `account_write_ends_never_take_the_menu_domain_lock_for_a_colliding_request_id` 紅→綠。

**晉升面**：none。這是 key 空間論證的寫法紀律，碼面已由守門與整合案承載。

**再犯面與守法**：
- 寫「advisory key 空間不碰撞」時，論域必須是**實際送進 `pg_advisory_xact_lock` 的值**——取鎖早於存在性判定者，即請求原值的全域（含負值、0 與逾界值），不是資料表裡現存列的值域。
- 新增以請求原值為 key 的鎖點（任何新域），同批在 begin 前把 key 收斂到不與既有常數 key 相交之子域，並補一支「外部持他域鎖、送碰撞值不排隊」之整合案。
