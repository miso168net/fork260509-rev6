---
id: "LL-00068"
rule_id: "none：LL-00033 守法（RUNBOOK §2 起手句）已明列 merge；本坑＝收刀 merge 這一步沒有對照該守法，補法寫於本檔"
promotion_surface: none
recurrence_of: "LL-00033"
---
LL-00068｜006 刀收刀 merge 帶入 `deploy/trust-model.dev.toml` 的變動後沒有重建 rust-api 容器：信任模型檔在容器內懸空約 6 小時、橫跨一支維護批，直到下一次容器內全量測試的對賬案轉紅才浮出（spec-compliance-006；2026-10-05）

**徵狀**：
- spec-compliance-006 修單跑容器內全量測試時，server lib 的 `dev_trust_model_matches_the_delivered_file` 轉紅，訊息為「APP_TRUST_MODEL_PATH＝/etc/rev6/trust-model.toml 讀不到」。
- 容器內 `ls -la /etc/rev6/` 列出該檔，但屬性全是 `?`。
- host 檔 mtime 為 2026-10-04 20:16，恰是 006 收刀 merge `c1f072c` 的時刻；容器的起動時間早於此。
- 這段期間的 maint-backlog-137-133 沒跑 cargo，所以沒有觸發。

**成因**：
- 006 刀 T077（`5008edc`）改過該檔。收刀時 checkout default 再 `merge --no-ff`，把新版寫進工作樹（新 inode），而單檔 bind mount 仍指著舊 inode。
- LL-00033 的守法已明列 merge，但收刀流程（finishing → 簿記三步 → perf 第四步）裡沒有「查 merge 動了哪些 bind mount 來源」這一步，主線也沒有對照 RUNBOOK §2 的起手句。
- 偵測面只有 BL-00115 的對賬案，而它只在跑全量 cargo 時執行。
- 懸空期間信任模型退回扁平環境變數，降級方向是安全的。

**處置**：
- 依 RUNBOOK §2 重建 rust-api 容器（`up -d --force-recreate --no-deps`）。target 與 registry 是具名卷，編譯快取不會流失。
- 重建後容器內該檔可讀，boot 日誌為 `warnings:0 internal_default:1`；重跑全量 1259 passed、0 failed。
- user 2026-10-05 裁定只記 LESSONS、不加機制。

**晉升面**：none——偵測已在（全量 cargo 時對賬案轉紅，並附重建命令）。同形第三次即評估 post-merge／post-checkout 提示 hook。

**再犯面與守法**：
- ①任何 merge、checkout、pull 之後，用 `git diff --name-only HEAD@{1} HEAD -- deploy/trust-model.dev.toml` 查該檔是否變動。命中即依 RUNBOOK §2 重建 rust-api 容器，不是 `restart`。
- ②收刀 merge 屬於此類：merge 落地後當場查，不要等到下一次跑 cargo。
- ③全量 cargo 中 `dev_trust_model_matches_the_delivered_file` 轉紅時，先看 mount（`ls -la /etc/rev6/`），不要去改碼。
