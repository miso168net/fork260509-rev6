---
id: "LL-00059"
rule_id: "none：判準住 006 刀 quickstart §11 之全量步（只帶「授 seed 角色於 seed 選單列之殘授權」）；守法寫進本檔與後續觀察窗 prompt，不另立規則"
promotion_surface: none
---
LL-00059｜已知態觀察窗之全量測試步只該帶指定型殘列：觀察 prompt 未令撤回他款寫入，端點授予與「撤 seed 列再重授成新 id」一併帶進全量，四支 seed 斷言測試轉紅（006 刀 U16）

**徵狀**：006 刀 U16 觀察窗（quickstart §11）依序做完 ADR-00068 各款觀察後，在 restore 前跑容器內全量測試，lib 有 4 支紅：
- `handler::ip_rule` 之 `non_super_roles_are_forbidden_on_all_five_endpoints`：Admin 打 getIpRuleList 得 200，不是 403。
- `handler::throttle` 之 `non_super_roles_are_forbidden_and_write_nothing`：R_ADMIN 打 unlockLogin 得 200，不是 403。
- `handler::route` 之 `user_routes_tree_differs_by_role_and_home_is_navigable_leaf`：seed 可見列之頂層條數 Admin(2) 不大於 User(2)。
- `model::facade::sys_menu` 之 `seed_role_trees_differ_by_role_and_nest`：R_ADMIN 可見集之 seed 政策部分不再真包含 R_USER_COMMON。

**成因**：
- 該全量步的用意，是證明 dev 庫帶著「授 seed 角色於 seed 選單列之殘授權」（款 10 之授予）時仍全綠，即 BL-00136 形①之走查面。殘列形只應有這一型。
- 主線派給觀察 agent 的 prompt 只令「款 10 之授予不撤回」，其餘各款寫成「撤回與否由你依觀察需要」。agent 於是留下兩型額外殘列：
  - 款 9 授給 R_ADMIN 的端點：直接推翻「非超管被拒」兩支斷言。
  - 候選甲後半撤掉 R_ADMIN 的 seed 授權列（`home` 選單維、列 4）後重授：重授落成新 id。新 id 不屬 seed 判準，「seed 可見集」兩支斷言因此失效。
- 四支測試以真 dev 庫之 seed 授權為前提，本就不承受這兩型殘列。零支歸因於款 10 之授予。

**處置**：
- restore 觀察基準：被撤的 seed 列 4／13／44 以原 id 回補，即走查工具 v3 的回補面在真庫上的實證。
- 重啟 rust-api 後，主線以 API 只重建款 10 型殘列：Super 對 R_ADMIN 送 updateRoleMenu，內容為現況加上受保護四列（revoked 0／granted 4）。以 diff 核對殘列形：授權列面、角色列面皆零差，casbin 只多這 4 列。
- 重跑全量：1258 passed／2 ignored 全綠。之後 restore、重啟、兩顆基準 diff rc 0、schema-gate 綠。

**晉升面**：none——判準住 quickstart §11 之全量步，守法寫進本檔與後續觀察窗 prompt。

**再犯面與守法**：
- ①觀察窗 prompt 要明令：指定保留的殘列以外，每款觀察完即撤回其寫入；或令 agent 逐筆回報全部寫入，由主線在全量前 restore，再只重建指定殘列。
- ②全量步之前，先以 `walkthrough-baseline.py diff` 核殘列形只含指定型：授權列面、角色列面零差，授權表只多指定列。
- ③seed 授權列被撤後，一律留給 restore 以原 id 回補，不以重授代替：重授的新 id 不是 seed，以 seed 為前提之斷言照樣失效。
