---
id: "LL-00109"
rule_id: "RL-0028"
promotion_surface: none
recurrence_of: "LL-00083"
---
LL-00109｜派發前裁定註之事實宣稱照偵查 agent 之推理字面寫入、未對碼面與 ADR 原文取證：一則把分頁欄之解析行為推廣到過濾欄、一則把所引 ADR 之後果寫反——implementer 照註逐字落活書、DoD 只驗字面在場而不轉紅，碼品質審查兩輪各抓一則（008 刀 U17）

**徵狀**：
1. tasks T151 之★U17 派發前裁定註④寫「型別不符與負數（分頁兩欄與過濾欄皆然）＝該欄未設」。as-built 只有分頁兩欄經 `u64` 解析、負數＝未設；`httpStatus` 以 `i32`、`operatorId`／`userId` 以 `i64` 解析，負數照值過濾。註之出處是派發前偵查 run 之駁回理由句「型別不符與負數經 wire_u64 逐欄判為 None」，主線把分頁欄的解析件推廣成全欄。
2. tasks T152 之★U17 派發前裁定註③寫「回應產生前即被丟棄與停機在途之寫入零列＝ADR-00100 後果之已知態」。ADR-00100 後果節原句是「等候許可者該列不落、寫入中者視 INSERT 是否已送達庫端而定（已送達者仍可能落列、照計失敗）」，註把所引出處寫反。
3. implementer 照註逐字寫進活書 08 §8.2 與 12「存取日誌」條；兩 task 之 DoD 只驗字面在場與「不寫恆落一列」，皆綠。碼品質審查第 1 輪抓 08、第 2 輪抓 12，各耗一輪 fix 與一輪複審；兩支 fix 皆以 `done_with_escalation` 請主線補 tasks 勘誤註。

**成因**：裁定註是派發前烤進 prompt 的不可違反項，agent 只能照字面寫。主線把偵查 agent 之推理文字與自己的轉述當成事實，沒有逐條回到碼面與 ADR 原句取證；註內也沒有附碼錨或 ADR 行號可供 implementer 對照。

**處置**：fix 第 1、2 輪依碼面與 ADR-00100 改寫 08 §8.2 與 12「存取日誌」條；Run A 收尾①主線讀碼（`handler/audit.rs` 之 `wire_u64`／`wire_http_status`、`model/audit_query.rs` 之 `resolve_person_filter`、`middleware/mod.rs` 之 `PendingAccessLogWrite` doc）與 ADR-00100 後果節核實後，於 tasks 兩則裁定註後補勘誤註。

**晉升面**：none。判準同 RL-0028（prompt 之事實接地每條附出處、不憑印象寫）；守法落在主線撰寫裁定註時。

**再犯面與守法**：
- 裁定註凡寫碼面行為或引述 ADR，逐條附碼錨（檔與符號）或 ADR 原句；引述 ADR 一律摘原句、不改寫語意。
- 偵查 agent 之理由句只當線索：寫進裁定註前，回碼面讀到該行為的實作處、確認射程（哪些欄、哪些路徑）再寫。
- 裁定註要 implementer 逐字落入文件之句，DoD 另加「與所引真源同義」之核，或改寫成「依 as-built 寫、先實證」。
