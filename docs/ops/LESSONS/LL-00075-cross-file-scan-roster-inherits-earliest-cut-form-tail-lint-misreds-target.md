---
id: "LL-00075"
rule_id: "none：碼面閘判準之連帶面（test_module_tail_lint 對名冊檔取到達各形之最早切點）——守法句住本檔，並由主線烤入新增跨檔掃描腿之單元定義"
promotion_surface: none
---
LL-00075｜測試模組新增跨檔掃描腿（`include_str!` 他檔）後，test_module_tail_lint 對該被切檔誤紅：同檔既有三形切法會傳染給新名冊檔，被切檔改切在首個 item 級門控（007 刀 U11）

**徵狀**：007 刀 U11 在 `handler/auth/refresh.rs` 測試模組新增 `auth/enforce.rs` 生產面零 `sys_user` 之掃描案（`production_code(include_str!("../../auth/enforce.rs"))`）。全量首跑，`tests/test_module_tail_lint.rs` 紅 5 案：`every_column0_item_after_the_cut_is_test_gated` 實得 `[("auth/enforce.rs", [267, 292, 359, 422, 432, 447, 472])]`，`module_head_form_cuts_at_the_tests_module_head` 等四案連帶紅。implementer 首輪撞到後把該案撤出、升級主線；規格對照 fix-1 才落樹。

**成因**：本閘的射程 (b) 是名冊字面所指的被切檔，切點取「到達該檔之各形切點中、原文最早者」。refresh.rs 既有 `chain_conflict_arm_is_wired_to_reenter_dispatch_loop_not_5000` 以 `split("\n#[cfg(test)]")` 切面，屬三形之一。新的名冊字面進場後，enforce.rs 同時被三形與模組頭字面形到達，最早者是首個行首 `#[cfg(test)]`，也就是 `mod tests` 之前的 item 級 `thread_local!` 門控。其後的生產 item 因此全數被判為「切點後未門控」。閘取保守切點（只多檢不少檢）是設計；不顯眼的是同檔既有切法會傳染給新加入名冊的他檔。

**處置**：規格對照 fix-1 把 chain_conflict 案改走同檔的 `production_code`（模組頭字面形、去整行註解，斷言只會更嚴）。refresh.rs 不再含三形字面，enforce.rs 只被模組頭形到達，切點落在 `mod tests` 頭。lint 32 支全綠；該案以「重入臂改回 `Err`」變異自證仍紅。

**晉升面**：none——切點判準已載於該閘檔頭 doc，本條只記同檔切法傳染給名冊檔這一面。

**再犯面與守法**：凡在測試模組新增 `("<他檔>.rs"` 名冊字面（`include_str!` 跨檔掃描）者，先 grep 所在檔是否另含三形切法字面（`split`／`find`／`split_once` 配行首 `#[cfg(test)]`）。有就先把同檔切面腿統一為模組頭字面形，再看被切檔在 `mod tests` 之前有無 item 級門控。改以 `server/src` 遞迴掃描（不寫名冊字面）者不在射程 (b)。007 刀 U12a 的 rejection 日誌掃描跨十一檔，主線組裝其單元定義時烤入此句，並以 grep 核其在場（關鍵字＝「同檔切法傳染」）。
