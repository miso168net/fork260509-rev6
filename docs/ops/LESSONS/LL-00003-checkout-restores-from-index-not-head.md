---
id: "LL-00003"
rule_id: "RL-0005"
promotion_surface: none
---
LL-00003｜hook 面演練還原用 `git checkout -- <路徑>`，檔案已 staged 時是從 index 取、不是從 HEAD 取

**徵狀**：驗證 pre-commit 新增段是否真的會擋，做「注入假漂移 → `git add` → commit 應被擋 → 還原」四步演練。commit 確實被擋、HEAD 未動，四步看似成功；但還原後 `git status --porcelain` 仍有 1 行，且該檔對前代同名檔的 `cmp` 顯示不等——壞內容還留在工作樹裡。被注入的是凍結 fixtures，契約自稱其位元變更為「違憲級」。

**成因**：`git checkout -- <路徑>` 的來源是 **index**，不是 HEAD。演練第二步的 `git add` 已把壞內容寫進 index，所以第四步的 checkout 是拿壞內容覆蓋壞內容、等於沒還原。接著 `git reset` 只清 index、不碰工作樹，於是工作樹留下壞內容而 porcelain 從 0 變 1。演練的前三步全部正確、只有還原這步的命令選錯，而前三步的成功（commit 真的被擋）很容易讓人以為整套做完了。

**處置**：還原一律用 `git checkout HEAD -- <路徑>`（顯式指定來源），或先 `git reset` 再 checkout。本次以前者修正後，四份凍結檔對前代逐位元全等、`columns.json` 的 sha256 與 `fixtures/provenance.md` §4 表相符、工作樹回 0 行。

**晉升面**：RL-0005（破壞性驗證每項還原後立即 porcelain 對賬、確認回基準態再進下一項）已涵蓋本坑的偵測面、且正是它當場救回的——不另立規則；還原命令的正確形記於本檔。

**再犯面與守法**：凡「注入 → `git add` → 觀察閘擋 → 還原」形的演練都會踩到，而 hook 面演練的定義就含 `git add`（不 add 就不會觸發 staged 判定）。守法有二：①還原一律寫 `git checkout HEAD -- <路徑>`，不寫省略 HEAD 的形；②還原後照 RL-0005 立即 porcelain 對賬，凍結面另加對前代的 `cmp` 或 sha256 對賬——本次就是靠這道對賬當場抓到。目錄類演練（如 U3 暫移 `entity/src`）用 `mv` 一進一出、不經 index，不受此坑影響。
