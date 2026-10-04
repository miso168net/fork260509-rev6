---
id: "LL-00062"
rule_id: "none：屬 git 本身語意（merge 前 index 須等於 HEAD）與 CLAUDE.md §3 健檢判讀的適用邊界；守法寫於本檔，未晉升規則"
promotion_surface: none
---
LL-00062｜收刀 merge 前 checkout default，兩個 gitlink 暫顯 ` M`：這是正常暫態，不可照健檢判讀①去 bump pin（006 刀收刀、2026-10-04）

**徵狀**：006 刀收刀時，`git checkout rev6-admin-root` 之後、`git merge --no-ff 006-authz-governance` 之前，外層 `git status --porcelain` 出現 ` M base-web` 與 ` M rust-api`。形狀和 CLAUDE.md §3 session 健檢判讀①「worktree 在前（pin 落後）」一模一樣，照字面會去 `git add <子庫>` bump pin。

**成因**：
- 兩個子庫是 git worktree，切換外層分支不會移動子庫 HEAD。子庫仍停在 feature 分支推進後的 commit，而 default 分支上的 gitlink 還是開刀前的舊 pin；舊 pin 是現 worktree HEAD 的祖先，所以呈「worktree 在前」。
- 這個差距正是待 merge 進來的內容：feature 分支的 gitlink 已等於現 worktree HEAD，merge 完自然歸零。
- 此時若照判讀① bump pin，index 就和 HEAD 不一致。依 git 文件，`git merge` 在 index 對 HEAD 有已登錄變更時會直接中止（避免把無關變更記進 merge commit）。當時依此預判而未照做，未實際觸發中止。

**處置**：不 bump、不 `submodule update`，直接 merge；merge 後兩個 gitlink 等於 worktree HEAD，porcelain 回到空。

**晉升面**：none——只在收刀 merge 這一步出現，判讀①的適用邊界記於本檔。

**再犯面與守法**：
- ①收刀時「checkout default → merge」之間看到兩個 gitlink ` M`，先確認 feature 分支 HEAD 的 gitlink 等於 worktree HEAD（`git ls-tree <feature> base-web rust-api` 對照 `git -C <子庫> rev-parse HEAD`），相等即直接 merge。
- ②CLAUDE.md §3 的判讀①／②只用於 session 健檢那種「外層停在同一分支上的分歧」，不用於切分支後、merge 前的暫態。
- ③submodule update 在任何情境都禁止（CLAUDE.md §3／§6）。
