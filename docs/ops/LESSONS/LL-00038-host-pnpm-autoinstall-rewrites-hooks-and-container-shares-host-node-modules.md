---
id: "LL-00038"
rule_id: "RL-0057"
promotion_surface: none
---
LL-00038｜在 host 跑 base-web 的 pnpm 指令會自動 install 並改寫外層 hooks；而 dev 容器實際共用 host 的 `base-web/node_modules`——具名 volume 在 9p bind 下沒掛上，刪 host 那份等於刪容器那份（005 刀 U13b）

**徵狀**：005 刀 U13b 的 implementer 在 host 直接跑 `pnpm typecheck` 驗型別。host 的 pnpm 是 11 版，發現沒裝依賴就自動 install，`prepare` 階段的 simple-git-hooks 因此改寫外層 `.githooks-submodule/` 的 hook 檔，同時在 drvfs 上長出 1.3G 的 `base-web/node_modules`。hook 檔由 agent 自行還原、主線驗指紋仍等於 HEAD；主線隨後依「容器以具名 volume 遮罩 `/app/node_modules`」的判讀提議刪掉 host 那份，刪完容器內 `/app/node_modules` 同時消失。

**成因**：①pnpm 11 在缺依賴時會自動 install，而 install 會觸發 `prepare` 腳本、改寫 hook 檔。②compose 雖宣告具名 volume 掛在 `/app/node_modules`，但 `/app` 本身是 9p bind，巢狀掛載沒有生效（容器 `/proc/mounts` 只有 `/app` 一條）。主線先前看到 volume 的 mount 計數為 0，卻讀成「有遮罩」，實際上是「沒掛上」。所以容器一直用 host 的 `base-web/node_modules`，而那份其實是 implementer 誤裝時產生的。

**處置**：在容器內以凍結 lockfile 重裝（`SKIP_INSTALL_SIMPLE_GIT_HOOKS=1 pnpm install --frozen-lockfile`、容器內 pnpm 10.34.3），裝回 738 項。重驗 hooks 五檔指紋等於 HEAD；容器內 `pnpm typecheck` rc 0；dev server 回 200。

**晉升面**：none——RL-0057 已要求子庫任一 pnpm install 後驗 hooks 指紋；本坑是執行面寫法，守法句寫進本檔與後續單元定義。

**再犯面與守法**：base-web 的 pnpm 指令（typecheck、lint、install）一律 `docker compose … exec -T base-web` 在容器內跑，不在 host 跑；誤跑之後照 RL-0057 驗 hooks 指紋。要刪或動 `base-web/node_modules` 之前，先在容器內查 `/proc/mounts`，確認 `/app/node_modules` 是否另有掛載；只有另有掛載時，host 那份才與容器無關。
