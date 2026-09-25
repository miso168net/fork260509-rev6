---
id: "LL-00035"
rule_id: "none：第三方庫（casbin 2.20.0）寫入次序之語意、非流程規則可守"
promotion_surface: code
---
LL-00035｜casbin 自動存檔下 `add_policy` 先寫轉接器、後加記憶體面——已存在之政策回 `Err`（唯一鍵違反）而非 `Ok(false)`，且 nextval 已被吃掉（005 刀 U3）

**徵狀**：005 刀 U3 的 `test_kit::plant_live_policy` doc 寫「已存在之政策（回 false＝未落庫）即 panic」，審查以變異（把 false 臂改成放行）打不紅、只列觀察；主線收尾追查才發現這句是假述：政策已存在時根本走不到回 false 那臂。

**成因**：casbin 2.20.0 `add_policy_internal` 在自動存檔開啟時**先**呼叫轉接器 `add_policy`、成功後才把規則加進記憶體 model；本 repo 轉接器（`rust-api/sea-orm-adapter`）的 `add_policy` 是一句 INSERT，撞 `casbin_rule` 的唯一索引 `unique_key_sea_orm_adapter`（`ptype, v0～v5`）即回 `Err`——`Ok(false)` 只在轉接器拒收列形（或庫面與記憶體面已分岔）時出現；`add_policies_internal` 同序。INSERT 失敗前 `id` 的 nextval 已取走，`casbin_rule_id_seq` 照樣前進。

**處置**：005 刀 U3 收尾把該 doc 改成實際語意（已存在＝轉接器回錯而 panic、序列已推進仍歸 caller 守衛收），並補一支 `should_panic` 自證案（seed 既有政策再植一次），變異「錯誤吞成放行」即紅。

**晉升面**：code——語意由上述自證案釘住。

**再犯面與守法**：經 enforcer 寫授權（`add_policy`／`add_policies`）之碼，不得以回傳 `false` 判「已存在」；批次寫入須先扣掉已持有之政策（`add_policies` 一列重複即整批 `Err`），失敗路徑一律視為序列已推進——測試掛 `CasbinRuleRowsGuard`（或組合守衛），生產面不以序列連號作任何判斷。
