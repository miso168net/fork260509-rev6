---
id: "LL-00092"
rule_id: "none：環境負載坑——效能劣化閘（全鏈 90 秒硬上限）之處置寫法，非規則面；調門檻須立 ADR"
promotion_surface: none
---
LL-00092｜pre-commit 全鏈撞 90 秒硬上限而各檢查皆過——dev 容器經 bind mount 輪詢 /mnt/d，拖慢整套 docsync 自測（007 刀 U21 收單顆；2026-10-14）

**徵狀**：staged 含 `tools/docsync/**` 之 commit，pre-commit 報全鏈耗時 147 秒、超出硬上限 90 秒而擋下，各段檢查全過；當時機器 load 約 18、`top` 系統態 CPU 約 27%，整套 docsync 自測（404 案）耗時約 150 秒。同日早上同類 commit 在 90 秒內。

**成因**：rev6 與 rev5 兩個 stack 的 dev 容器（base-web 之 vite、rust-api 之 watchexec）經 bind mount 輪詢 WSL drvfs（/mnt/d）上的源碼樹，吃掉大量系統態 CPU；pre-commit 於 `tools/docsync/**` 或 `.githooks/**` staged 時跑整套 docsync 自測，對 CPU 爭用最敏感。`.githooks/pre-commit` 檔頭雙錨（WARN 45、FAIL 90）是效能劣化閘，不是檢查失敗。

**處置**：暫停 rev6 與 rev5 的 `base-web`、`rust-api` 容器（rev5 只准 up／stop／ps）後原樣重試，全鏈 79 秒放行；事後 up 回來。未調門檻、未 `--no-verify`。

**晉升面**：none——環境負載坑；調高 FAIL 門檻會掩蓋真劣化（須立 ADR），不採。

**再犯面與守法**：pre-commit 報全鏈耗時超出硬上限而各檢查皆過時，先看 `top` 的系統態與 `docker stats`，暫停 dev-watch 容器（rev6／rev5 之 base-web、rust-api）再原樣重試；通過後把容器 up 回來。絕不 `--no-verify`；門檻要調先立 ADR。`precommit_chain` perf 事件之量法見 RUNBOOK §12b。
