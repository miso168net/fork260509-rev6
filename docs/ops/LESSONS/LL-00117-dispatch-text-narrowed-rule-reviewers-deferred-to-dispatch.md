---
id: "LL-00117"
rule_id: "RL-0026"
promotion_surface: none
---
LL-00117｜派發文自訂之計數判準收窄了 RULES 條（RL-0026 三形聯集→「完整呼叫形」），implementer 照派發文實作、兩道審查亦以派發文為準只列射程外建議（008 刀 final holistic review 碼修 run）

**徵狀**：
1. final holistic review L1-1 之碼修，主線派發文要求 `handler/audit.rs` 新增讀出點名冊腿：「完整呼叫形 `sys_operation_log::list(` 須恰 1 處且在本檔」。
2. implementer 照寫、只數後接 `(` 之形。品質審查指出它比同模組既有 `call_forms`（RL-0026 三形聯集）窄、以值傳遞與 turbofish 等形漏數，卻以「派發文明定完整呼叫形」為由列為射程外建議、非 blocker。
3. 主線收件復核時對照 RL-0026（「驗呼叫處恰 N 處取 `name(`／`(name)`／`::name` 三形聯集」）判為違規，於收單前改為完整 token 計數並補樣本與變異自證。

**成因**：主線擬派發文時以自然語言重述判準，未與烤入 prompt 之 RULES 塊逐條比對；審查 agent 把派發文當成最高依據，未依權威鏈（RULES 高於派發文）把兩者衝突列為 blocker。

**處置**：主線改 `list_calls` 為路徑 token 之完整 token 計數（前後皆非識別字元），增黏後綴、以值傳遞、括號包住、turbofish、匯入句等樣本，變異自證「退回只認後接 `(`」轉紅。

**晉升面**：none。RL-0026 本身完備；缺口在派發文與審查之執行面，守法住本檔。

**再犯面與守法**：
- 派發文凡定義計數、名冊或處數型判準，擬稿後逐條對照該單元 RULES emit 塊；與 RULES 不同處只許更嚴，並在派發文內寫明所依 RL 號。
- 審查發現派發文判準比 RULES 寬或窄時，依權威鏈以 RULES 為準列 blocker，不以「派發文明定」降為建議。
- 收件復核時，對審查列為「射程外建議」之條目逐條問：其射程是否由派發文自訂；是則回查 RULES。
