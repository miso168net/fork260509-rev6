---
id: "LL-00095"
rule_id: "none：守法已在 RUNBOOK §2 起手句與 LL-00068 守法②；本坑＝兩處文字守法皆未在收刀 merge 當下被對照，補法改為機器提示（外層 post-merge／post-checkout hook）"
promotion_surface: code
recurrence_of: "LL-00068"
---
LL-00095｜007 刀收刀 merge 再度帶入 `deploy/trust-model.dev.toml` 的變動而沒有重建 rust-api 容器：信任模型檔在容器內懸空約 29 小時、橫跨三支維護批，直到 spec-compliance-007 修單 U1 的全量測試對賬案轉紅才浮出（同形第三次；2026-10-17）

**徵狀**：
- spec-compliance-007 修單 U1 改動前的基線全量（2026-10-16 23:51）起，server lib 的 `dev_trust_model_matches_the_delivered_file` 每趟都紅（全量 rc 101），其餘全綠。
- 容器內 `ls -la /etc/rev6/` 列出 `trust-model.toml`，但屬性全是 `?`。
- host 檔 mtime 為 2026-10-15 18:29，恰是 007 收刀 checkout default（18:28:59）與 merge `8d8dc57`（18:29:00）的時刻；該檔於 007 刀 `df7335b` 改過，容器起動早於此。
- 期間 maint-backlog-142-146、maint-backlog-139-140-145-147、maint-adr-00094-wording 三支維護批都沒跑容器內全量 cargo，所以沒有觸發。

**成因**：
- 與 LL-00068 同形：收刀 checkout＋merge 把該檔寫成新 inode，單檔 bind mount 仍指著舊 inode。
- LL-00068 守法②（收刀 merge 落地後當場查）只住 LESSONS；收刀者照 CLAUDE.md §2 範本做、看不到它（LL-00067 同一種漏法）。RUNBOOK §2 起手句又只寫 pull／checkout、沒列 merge（LL-00068 rule_id 所稱「已明列 merge」指的是 LL-00033 的守法文）。
- 偵測面仍只有全量 cargo 時執行的對賬案。

**處置**：
- 依 RUNBOOK §2 重建 rust-api 容器（`up -d --force-recreate --no-deps`）。重建後容器內該檔可讀、boot 日誌為 `warnings:0 internal_default:1`；U1 自驗之容器內全量兩趟 rc 0。
- user 2026-10-17 裁定（LL-00068 晉升面「同形第三次即評估 post-merge／post-checkout 提示 hook」之評估）：本輪加提示 hook。外層 `.githooks/post-merge` 與 `.githooks/post-checkout` 在前後兩顆 commit 間該檔有變動時，於 stderr 印出 RUNBOOK §2 的重建命令；只提示、恆 rc 0。bootstrap hooks 指紋名冊、GT-09 `EXEC_REQUIRED` 與 README 檔樹同步加這兩檔，RUNBOOK §2 起手句補上 merge 與 hook。行為由 docsync tests 以臨時 repo 實跑兩支真 hook 機器守。

**晉升面**：code——上列兩支提示 hook。`git checkout -- <檔>` 的單檔還原（post-checkout 兩參數相同、不帶路徑資訊）與手改該檔不經 hook，仍靠 RUNBOOK §2 自查。

**再犯面與守法**：
- ①merge、pull、切分支後見到 hook 提示，即依 RUNBOOK §2 重建 rust-api，不是 `restart`。
- ②單檔還原或手改該檔後，自行重建。
- ③全量 cargo 中對賬案轉紅時先看 mount（`ls -la /etc/rev6/`），不要去改碼（同 LL-00068 ③）。
