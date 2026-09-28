---
id: "LL-00043"
rule_id: "none：資料形事實（vendored adapter 的欄定義），非流程規則"
promotion_surface: none
---
LL-00043｜手寫 `casbin_rule` INSERT 只給用到的欄、省略 v3～v5 就失敗——這幾欄是 NOT NULL（005 刀手寫 SQL 植入政策列時）

**徵狀**：以手寫 SQL 植入 casbin 政策列時只給 ptype 與 v0～v2，INSERT 因違反 NOT NULL 而失敗。

**成因**：`casbin_rule` 的 8 欄基底由 vendored `sea_orm_adapter` 的 migration 建立（m0001 委派），ptype 與 v0～v5 全是 `not_null()`；adapter 的 entity 欄型是 `String`（非 `Option`），經 adapter 寫入的未用欄是空字串，手寫 SQL 不會自動補。

**處置**：未用的 v3／v4／v5 一律填 `''`，不省略、不給 NULL。

**晉升面**：none——資料形事實，住 adapter 原始碼與本檔。

**再犯面與守法**：手寫任何 `casbin_rule` 列（植入、比對、清除條件）先對照 `rust-api/sea-orm-adapter/src/migration.rs` 的欄定義；比對與刪除條件用 `= ''`、不用 `IS NULL`。
