# BACKLOG-DEFERRED — 滯後卷

條目形同主檔 `BACKLOG.md`；本卷收 user 拍板滯後的待辦——不排入 NOTES 近期 roadmap、STATE 分開計數（滯後≠完成；配號計入 GT-05 家族）。
配號永遠只在主檔（本卷無 next-id）；移入／移回＝整行搬＋滯後戳記（`★滯後 <日期> user 拍板：<理由>`）；完成＝刪列＋事件 `backlog_done`；各條目觸發欄寫回收時點。

- BL-00029｜product｜寫端 `update_system_setting` 為「不對已消失的列寫入」多查一次（handler 查 setting_type 供一致性守衛、facade `update_by_key` 內再查在場）——16 鍵低頻治理端點划算（research R11 last-write-wins、不驗併發）；高頻化時改 existing 下傳＋`UPDATE … WHERE deleted_at IS NULL` 以 rows_affected 判在場、省第二次 SELECT｜觸發＝該端點轉高頻或出現併發寫入需求時｜★滯後 2026-09-08 user 拍板：16 鍵治理端點只有超管能寫、無併發場景，觸發極可能永不到期；技術結論本身仍成立、回收時點見觸發欄
- BL-00049｜product｜登入頁三顆快速登入鈕與表單預填密碼暴露 dev seed 帳密（003 auth-session 刀 Q4：user 拍板保留、與 rev5 UI 對照零差異且一鍵切三帳號為 US1 驗收項；承 `rev5:B-053` 同型已知態）：`base-web/src/views/_builtin/login/modules/pwd-login.vue` 之表單預填與三顆鈕各自帶 seed 帳號與同一組密碼，皆 upstream `example` 基線既有、本刀零 inline；轉 prod 前必須拆除｜觸發＝RUNBOOK §16 之 prod 硬化拍板成立時（該節現寫「prod 不入 roadmap、若要做 prod 先立 ADR」）｜★滯後 2026-09-08 user 拍板：觸發本質不可到期（prod 不入 roadmap），不佔開放帳
