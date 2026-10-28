---
id: "LL-00116"
rule_id: "RL-0013"
promotion_surface: none
---
LL-00116｜修補選項只對 finding 所舉之觸發形設計與驗證，未以受保護資產為單位枚舉外露路徑：reaper 設密之「明文密碼落伺服器日誌」只擋了失敗語句一路，`log_statement` 為 ddl／all 時設密成功照落明文（008 刀 final holistic review L4-1）

**徵狀**：
1. final holistic review 之 L4-1 指出 `deploy/setup-reaper-role.py` 送 `ALTER ROLE reaper LOGIN PASSWORD '<明文>'`，語句失敗時明文以 STATEMENT 行落 PG 日誌。主線擬之拍板選項＝前置 `SET log_min_error_statement = panic`，ADR 草稿之決策驅動因子寫成「設密語句之任何失敗都不得讓明文落 log」，對所選方案跑的反例（角色不存在、引號語法錯、SET 失敗、非超級使用者）全取自失敗路徑。user 據此裁定。
2. user 轉來旁路提醒：`log_statement` 為 ddl／all 時 ALTER ROLE 成功亦整句入日誌。拋棄式 postgres:18.4（`log_statement=ddl`）實測屬實；另有慢查詢日誌、`pg_stat_activity`、pg_stat_statements／pgaudit 等路。PostgreSQL ALTER ROLE 文件本身即建議客端先算驗證碼（psql `\password`）。
3. 改裁為「客端先算 SCRAM-SHA-256 驗證碼」（ADR-00110）。原案只差一步就以 accepted ADR 入庫，入庫後即不可改。

**成因**：決策驅動因子照 finding 之觸發形收窄（「失敗時」），而不是照受保護之資產與目標（「明文密碼不進任何伺服器日誌」）。RL-0013 之同一反例因而只在收窄後之射程內跑，看不到成功路與其他記錄面；修法亦未先查該資產之官方建議做法。

**處置**：ADR-00110 改寫為客端先算驗證碼（明文不離開本行程），以拋棄式 PG 在 `log_statement=ddl` 下實打成功、失敗兩路與含引號之密碼，並以 RFC 7677 範例向量為已知答案；原案與「三句 SET」列為棄案並附實測。

**晉升面**：none。RL-0013 已要求對所選方案跑同一反例；本坑之缺口在反例之母集取錯，屬執行面，守法住本檔。

**再犯面與守法**：
- 擬資安類修補選項前，先寫出「受保護之資產」與「不得出現之處」，再枚舉該資產在系統內之全部外露路徑（成功與失敗、各記錄設定、監看視圖、擴充、下游收集），不以 finding 所舉那一條為母集。
- 決策驅動因子以資產與目標表述，不以觸發條件（「失敗時」「某設定下」）收窄；RL-0013 之反例自該母集逐條取。
- 先查該資產在官方文件中之建議做法（本例＝PostgreSQL ALTER ROLE 文件之 `\password` 指引），選項說明中載明是否採用與理由。
