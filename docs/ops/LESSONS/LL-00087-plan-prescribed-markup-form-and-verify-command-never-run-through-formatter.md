---
id: "LL-00087"
rule_id: "none：同 LL-00082／LL-00085，計畫字面之寫法守在 tasks 撰寫與單元定義審讀，不另立規則"
promotion_surface: none
---
LL-00087｜計畫為 fork-delta 修改型指定排版與驗證命令時沒先過工具：「末個 prop 與自閉合符同行」一格式化就被拆回獨行，驗證命令 `pnpm lint` 自帶自動修正、會先改掉被驗的檔（007 刀 U19）

**徵狀**：
- 007 刀 U19（T087）：tasks 與 research R18 決定 13 指定角色頁表頭「兩 prop 排既有屬性之後、末個 prop 與自閉合符同行以取代基線獨行之 `/>`（`原行: />`）」。照做後 `pnpm exec oxfmt --check` rc 1：oxfmt 把 `/>` 改回獨行，兩 prop 就成了未圈界新增，fork-delta-lint 紅。implementer 改用空對標籤之閉合 `></TableHeaderOperation>` 當真被替換行，以 done_with_escalation 回報、請主線勘正字面。
- 同條寫「以 `pnpm lint` 與 fork-delta-lint 雙綠為準」。base-web 的 `pnpm lint`＝`oxlint --fix && eslint --fix .`。碼品質審查以 `eslint --fix-dry-run` 實證：`vue/attributes-order` 會把排在事件之後的兩 prop 移到事件之前，拆出被替換行所在的塊，fork-delta-lint 隨即紅。使用者頁與選單頁表頭也是這個排法，三頁同形。照字面跑這條驗證，被驗的檔先被改掉。
- 同條選單頁寫「JSX：`原行: render: row => (`」。render 行的改寫早由 005 刀 (ii) 標記記下，本用途真正替換的是新增子選單的條件行。照字面記 render 行，fork-delta-lint 報缺原行。

**成因**：
1. 計畫期只對照了 fork-delta 規則（新增屬性須與真被替換行同塊），沒拿格式化工具驗那個排版留不留得住。oxfmt 會把自閉合符正規化成獨行，「與自閉合符同行」的形一格式化就散了。
2. 驗證命令直接取 package.json 現成的 `pnpm lint`，沒看它的定義。這支腳本帶 `--fix`，是修正命令、不是檢查命令；eslint 的自動修正也不知道 fork-delta 圈界的同塊要求。
3. 指定 `原行:` 時沒查該行是否已被既有標記記過。
4. 上游原因與 LL-00082、LL-00085 相同：tasks 產出期與 analyze 期都不實跑計畫寫下的命令與施工形，要到單元出口才第一次暴露。三者機制各異（diff 上下文行、說明性出現被計數、工具改寫排版），故不設 recurrence_of。

**處置**：U19 收尾勘正 T087 與 research R18 決定 13 的字面，三處都附勘正註。角色頁表頭改為空對標籤之閉合：`原行: />` 不變；無子節點，渲染與自閉合相同；view-render-guard 判準 (b) 放行空標籤體。驗證命令改為不改檔的 `oxfmt --check`、`oxlint` 與 fork-delta-lint。選單頁 (viii) 的 `原行:` 改記新增子選單的條件行。

**晉升面**：none。守法落在 tasks 撰寫與單元定義審讀，不另立規則。

**再犯面與守法**：
- 計畫為 fork-delta 修改型指定排版（屬性排序、閉合符位置、行內併入）時，先把示意片段用 `pnpm exec oxfmt --stdin-filepath <檔名>` 格式化一次，確認被替換行與新增行仍在同一塊，再寫進 tasks。
- DoD 與驗證段只寫不改檔的檢查命令（`pnpm exec oxfmt --check`、`pnpm exec oxlint`、`pnpm typecheck`、`python3 tools/fork-delta-lint.py`）。`pnpm lint`、`pnpm fmt` 這類帶自動修正的腳本不得當驗證命令。
- 有人手動跑了 `pnpm lint`，三頁表頭的新屬性會被重排出塊。fork-delta-lint 會報未圈界新增（不會靜默放過）；處置是還原排序，不是補圈界。
- 指定 `原行:` 前，先查該行是否已被既有標記記過；已記過，就改記本用途真正替換的那一行。
