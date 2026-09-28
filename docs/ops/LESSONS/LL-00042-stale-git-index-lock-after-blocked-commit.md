---
id: "LL-00042"
rule_id: "none：git 現場處置細節（先查行程再移鎖），判準住本檔即可承"
promotion_surface: none
---
LL-00042｜commit 被 pre-commit 擋下一次後重試，碰到殘留的 `.git/index.lock`（005 刀憲法 1.5.1 那顆、2026-09-27）

**徵狀**：第一次 commit 被 pre-commit 的 route-artifact-gate 擋下（當時 base-web 依賴重裝尚未完成）；修好重試時 git 報 `index.lock` 已存在、拒絕寫入。

**成因**：前一次 commit 中途失敗時殘留了鎖檔；當下並沒有任何 git 行程持有它。

**處置**：先確認沒有 git 行程在跑，再移除 `.git/index.lock`，重試後提交成功。

**晉升面**：none——一次性現場處置，判準在本檔。

**再犯面與守法**：看到 `index.lock` 先查行程（例：`pgrep -a git`）、不直接刪——有行程在跑時刪鎖會毀掉進行中的 index 寫入；子庫是源倉的 worktree，其 index 鎖在源倉 `.git/worktrees/<名>/` 下，照同法處理。
