# Contract — 機器守、治理面與帳本（006）

> 本檔凍結本刀新增或擴充之機器守之施工面、名冊守恆、測試基建與走查工具契約、觀測面與 ADR／帳本兌現面。決定本體住 ADR（Amendment＝ADR-00063、觸發列與兩窗＝ADR-00067、seed-view-gate＝ADR-00071 等），本檔只寫施工；理由與替代案見 research；端點行為見兩支 wire 契約、拒因鍵見 `contracts/msg-keys.md`。
> 基線座標：base-web 本刀起點 pin `2248b89`（upstream `example` 基線 `8be6f9ba`）、rust-api pin `8c8b5e1`、憲法 1.6.0→1.7.0（收刀前 PATCH 實數化後 1.7.x＝§8.1）。本檔凡寫「單元」皆以描述指稱（「治理單元」「CDP 三方對照單元」「收刀前承載體檢單元」「首個觸及 base-web 既有檔之單元」等），單元號以 tasks 為準。

## §1 fork-delta：★BASE-WEB-MANAGE-PAGE-WIRING 用途 (iii)(iv)

### 1.1 授權來源與硬序

- 授權來源＝本刀 U0 之 Amendment（ADR-00063 決定二：(iii) 三顆授權彈窗接真、(iv) 授權回收桶頁進場）。本節依親決題 III-a（範圍欄以「預估 N」填列）、III-b（(iv) 不重列產物四檔、授權沿 (i) 列）、III-c（(ii) 列兩彈窗句同顆改寫）之建議形書寫；U0 取非建議項者，同批改本節。
- ★硬閘（spec FR-040⑥／SC-012）：Amendment 顆落地前 base-web 既有檔零 diff。機器斷言（U0 出口與收刀前承載體檢單元各一次）：`git ls-tree <Amendment 顆> base-web` 之 gitlink＝`2248b89`。純新增檔依表外宣告 3 本不受此閘，本刀單元序亦使其落在 Amendment 之後。
- Amendment 顆落地前主線親跑 `python3 tools/fork-delta-lint.py` rc 0（新列入名冊無解析錯）與 `python3 tools/route-artifact-gate.py check` rc 0（新列不干擾 (i) 列產物檔組），關鍵行入 commit 訊息（ADR-00063 決定六）。
- **名冊載入變異自證**（首個觸及 base-web 既有檔之單元順做；ADR-00063 決定六）：暫把 (iii) 列範圍欄任一反引號路徑之反引號內字面改為不含 `/` 之非路徑 token → `python3 tools/fork-delta-lint.py` 當場 rc 2（`load_roster` 路徑形斷言 die）→ 以存原文寫回（RL-0019）→ `git diff --name-only` 零殘留；(iv) 列同形另跑一發、不疊加（RL-0005）。

### 1.2 ★ 軌道逐處登記表 12 列之紀律與出口應有值

應有值欄＝`grep -c ' START]' <檔>`／`grep -c '原行:' <檔>`，「現值 → 本刀承載單元皆落地後」；★標「預估」者以 ADR-00063 決定二之預估值為準、至收刀前 PATCH 實數化為止。

| # | 檔（`base-web/` 下） | 用途 | 紀律 | 應有值 |
|---|---|---|---|---|
| 1 | `src/views/manage/role/modules/menu-auth-modal.vue` | (iii) 修改型＋新增型 | 修改型逐行 `原行:`——★含以程式行替換佔位註解行之處（rev5 該形未帶 `原行:`、rev6 逐處補帶）；模板勾選雙向綁定一行不動、受控勾選集以可寫 computed 承接（樹節點 disabled 經 computed 注入、模板資料繫結一行不動）；首頁讀寫直接消費 005 刀既有之 `fetchGetRoleHome`／`fetchUpdateRoleHome`（`src/service/api/rev6-role-admin.ts`、不另包）；開標籤內之改動依 §III 修改型 Vue 模板屬性行變體句（BL-00135；ADR-00063 決定三） | 0／0 → 7／14（預估） |
| 2 | `src/views/manage/role/modules/button-auth-modal.vue` | (iii) 修改型＋新增型 | 同 #1 之標記紀律；初始化改隨彈窗開啟觸發（基線於 setup 直跑） | 0／0 → 3／23（預估） |
| 3 | `src/views/manage/role/modules/role-operate-drawer.vue` | (iii) 新增型＋(ii) 圈界內改寫 | (iii) 恰 3 塊新增型（引入端點權限彈窗、第三顆彈窗之顯隱狀態、模板觸發鈕＋掛載）、(iii) 零修改型；BL-00131 修法（ADR-00070 決定 1／決定 2）落在 (ii) 既有 `handleSubmit` 圈界塊內、不新增塊與修改型——(ii) 實數 6 處＋4 塊不變；標記各帶其用途號 | 4／6 → 7（預估）／6 |
| 4 | `src/locales/langs/en-us.ts` | (iii)＋(iv)＋I18N(ii) | (iii) 1 塊＝`page.manage.role` 補抽屜第三鈕一鍵；(iv) 2 塊＝`route:` 鍵 `manage_policy-archive`、`page:` 子樹 `manage.policyArchive`；msg 三鍵落既有 I18N(ii) 塊內、不增塊（`contracts/msg-keys.md` §4）；★插入位置不得落在物件最末項之後（免改既有行；005 刀 research R14 判準） | 7／0 → 10（預估）／0 |
| 5 | `src/locales/langs/zh-cn.ts` | 同 #4 | 同 #4（簡中）；兩語鍵集相等由兩檔標型 `App.I18n.Schema`＋`pnpm typecheck` 承擔 | 7／0 → 10（預估）／0 |
| 6 | `src/typings/app.d.ts` | (iii)＋(iv)＋I18N(iii) | (iii) 1 塊＝`Schema.page` 之 `manage.role` 第三鈕型；(iv) 1 塊＝`manage.policyArchive` 型節（★必需）；backend 型節之三鍵落既有 I18N(iii) 塊內 | 6／0 → 8（預估）／0 |
| 7～10 | `src/router/elegant/{imports,routes,transform}.ts`＋`src/typings/elegant-router.d.ts` | (i) 列之產物檔紀律 | 回收桶頁 view 落地即由 dev server 內之路由外掛重算（`pnpm gen-route` 不重算）、禁手改、零標記；該單元於 base-web 容器在場下實跑 `python3 tools/route-artifact-gate.py check` rc 0（具名跳過不算驗收）；(iv) 列不重列（`tools/route-artifact-gate.py` 之 `TRACK, PURPOSE` 寫死只讀 (i) 列） | 零標記 |
| 11 | `src/typings/components.d.ts` | §III 生成檔紀律（不入用途名單） | 預期零變動（rev5 同形頁所用 naive 元件於本檔皆已登記）；有變只許 unplugin 重算之宣告行增刪、與引入該元件之檔同 commit | —— |
| 12 | `src/locales/langs/zh-tw.ts` | I18N 錨點檔（rev6 自有、單行形） | `backend` 子樹補三鍵；檔頭單行標記不動 | `rev6-inline` 恰 1 行 |

- 應有值判準（ADR-00063 決定二「預估依據」）：實數項取實數；預估項於其承載單元落地後取預估、之前計 0；新增型以全檔各項之和比對。**凡觸及 #1～#6 任一檔之單元**（含依 spec FR-004 落鍵之後端單元）出口逐檔斷言，不等即停手升級主線（user 定當刀 PATCH 或延至收刀前 PATCH）；用途分項以 `grep -c 'MANAGE-PAGE-WIRING(iii)'` 等形複核。
- 收刀前承載體檢單元：(iii)(iv) 預估值以 §V.2 PATCH Amendment 實數化（ADR-00063 翻案觸發器之 PATCH 條；前例 ADR-00051）；實數化後 §2.1 對賬腿自動納入。

### 1.3 新增型新檔五支（不入表、檔頭一行標記）

| 檔（`base-web/` 下） | 檔頭標記 |
|---|---|
| `src/views/manage/role/modules/endpoint-auth-modal.vue` | `[rev6-inline MANAGE-ROLE-AUTH-VIEW+ 006-authz-governance]` |
| `src/views/manage/policy-archive/index.vue` | `[rev6-inline MANAGE-POLICY-ARCHIVE-VIEW+ 006-authz-governance]` |
| `src/views/manage/policy-archive/modules/policy-archive-search.vue` | 同上 |
| `src/service/api/rev6-authz.ts` | `[rev6-inline BASE-WEB-WRAPPER+ 006-authz-governance]`（§III.1；路徑須落 `src/service/api/rev6-*.ts`＝`S1_NEW_FILE_FACE`） |
| `src/typings/api/rev6-authz.d.ts` | `[rev6-inline BASE-WEB-ADAPT+ 006-authz-governance]`（§III.1；`src/typings/api/`；單一命名空間 `Api.Authz`） |

- 定形先例＝`src/views/manage/ip-rule/index.vue` 之 `MANAGE-IP-RULE-VIEW+ 004-ip-trust-anchor`、`rev6-role-admin.{ts,d.ts}` 之檔頭；註解引導依檔型：`.vue` 新檔之標記＝首行 `<!-- … -->`、置於 `<script setup>` 之前（ip-rule 先例）；`.ts`／`.d.ts` 新檔首行用 `//`。★`tools/fork-delta-lint.py` 之 `find_new_file_marker` 只認首個實質碼行之前之空白／註解行為檔頭區，`<script setup …>` 即實質碼行——rev5 端點彈窗把標記寫在 `<script setup>` 開標籤之後（script 區內）之形不帶（照搬即判缺檔頭標記而紅）。★rev5 之 `BASE-WEB-MANAGE-PAGE-WIRING(iii)+`／`(iv)+` 檔頭形不可沿用：`new_file_track_issue` 要求軌道名後緊接 `+`、帶用途後綴即紅（自測 NF18 同型反例）。
- 回收桶頁目錄＝seed sys_menu 列 10 之 component `view.manage_policy-archive` 所決定之 `src/views/manage/policy-archive/`；三支 view 新檔與 #1／#2 皆入 `tools/view-render-guard.py` 射程（`src/views/manage/**`、註解內亦不得寫出被禁字面）。

### 1.4 變更檔集機器斷言（檔級硬邊界之機器半邊；base-web 各單元出口＋收刀全量閘復跑）

- `git -C base-web diff --name-only --diff-filter=M 2248b89..HEAD` ⊆ §1.2 之 12 檔 ∪ {upstream `example` 基線 `8be6f9ba` 不存在之檔}（後者＝fork-delta 意義之新增檔、spec FR-039「＋新增檔」；逐檔以 `git -C base-web cat-file -e 8be6f9ba:<路徑>` 判、rc 非 0＝屬之）——全集機器可判、不設人工指名之追加集。
- `--diff-filter=A` 恰為 §1.3 五檔；`--diff-filter=DR` 為空。
- `git -C base-web diff 2248b89..HEAD -- src/views/manage/role/index.vue` 零輸出（角色頁主檔一行不動＝spec FR-033、(iii) 列紀律欄）。
- 修改型標記只出現於授權三元組＝`tools/fork-delta-lint.py` 授權判定腿；(ii) 用途之修改型標記出現於兩彈窗＝紅（(ii) 列紀律欄改寫句之三元組判定）。

### 1.5 新增圈界塊「拔標記必紅」

本刀每一新增圈界塊（#1／#2 之新增型、#3 之 (iii) 三塊、#4～#6 之 (iii)(iv) 塊）逐塊暫拔 START／END → fork-delta-lint 報未圈界新增 → 寫回 → `git -C base-web status --porcelain` 回基準（RL-0005）；msg 三鍵落既有塊內、不新增塊、不另做。

## §2 新閘與新腿

### 2.1 fork-delta-lint 範圍欄對賬腿（BL-00132；spec FR-042；ADR-00063 決定四）

- **落點**：`tools/fork-delta-lint.py` 新腿（注記解析與實數計數為新建函式，名由施工單元定）。★`load_roster` 之回傳形 `(s1, s2)` 與 `_expand_range_files` 之簽章 MUST NOT 改——`tools/route-artifact-gate.py` 之 `load_declared` 以 importlib 解包兩值並取用後者；新腿另讀同一憲法檔（同受 `--constitution` 引數）。
- **解析面**：憲法 §III.2 表每列範圍欄之（…）注記；注記轄其前一段（自上一注記之後至本注記之前之反引號路徑；brace 展開沿 `_expand_range_files`）——分群判準同 route-artifact-gate 之 `artifact_group`。注記之數量段＝第一個「；」或「：」之前，其後為說明、不解析。數量段形為**閉集**：
  - 「N 處，修改型」／「各 N 處，修改型」
  - 「N 處修改型＋M 塊新增型」
  - 「N 塊，新增型」／「各 N 塊，新增型」
  - 預估形＝數量段以「預估」或「各預估」起首之上列任一形（該項整體為預估；例 ADR-00063 提案之「預估 14 處修改型＋7 塊新增型」「各預估 1 塊，新增型」「預估 3 塊，新增型」）
  - 不預估形＝注記含「不預估」（例 1.5.2 前 (ii) 列之「（六支，修改型＋新增型；處數與塊數 Amendment 時不預估、實數以標記為準）」）
  - 產物檔形＝「產物檔 N 支」→ 跳過（route-artifact-gate 之射程）
  - 其餘形＝rc 2 指名列與注記原文（未識別即 fail-loud、不靜默跳過）
- **實數面**（同次執行、讀 base-web 工作樹）：修改型＝逐（軌道, 用途, 檔）計含 `原行:`（`MARKER`）且所帶 `TRACK` 標記之軌道與用途相符之行；新增型＝逐檔計 `BLOCK_EDGE` 之 START 行（不分軌道與用途——用途後綴非必帶，例 `pwd-login.vue` 兩塊 START 缺 `(i)`）。
- **判準**：
  - 修改型逐三元組：注記處數（新增型-only 注記＝0）＝實數；該項為預估或不預估＝跳過該三元組；不等＝rc 1 指名（軌道, 用途, 檔, 注記值, 實數）。
  - 新增型逐檔：Σ 各列對該檔之注記塊數（修改型-only 注記＝0）＝實數；該檔任一項為預估或不預估＝整檔跳過；不等＝rc 1 指名檔與各列分項。
  - 跳過粒度同表外宣告 3 新句（ADR-00063 決定四）：修改型逐三元組、新增型逐檔——例：1.7.0 下角色抽屜 (ii)「6 處修改型＋4 塊新增型」與 (iii)「預估 3 塊，新增型」⇒ 該檔新增型整檔跳過、(ii) 之 6 處照對。
  - 零解析即紅：解析出之注記項為零、或非跳過之對賬項為零＝rc 2（RL-0051）；輸出印對賬項數與跳過項數（RL-0029 之進入受檢面自證）。
- **首跑期望**：1.7.0 下 (iii)(iv) 以外各列實數全符（量法＝本腿首跑輸出、本檔不抄數）；含預估項之 #1～#6 只對其修改型實數三元組（非零者現僅角色抽屜 (ii) 之 6 處；其餘為新增型-only 注記之 0 處對實數 0）。
- **自證**：
  - `self_test()` 合成案（走真解析鏈、比照既有 RG 系列以合成憲法文本走 `load_roster` 之形）：全符綠／改一處數紅並指名／改一塊數紅並指名／預估項跳過（含同檔他列實數塊之整檔跳過、修改型照對）／不預估項跳過／產物檔注記跳過／未識別注記 rc 2／零解析 rc 2／新增型-only 項出現修改型標記紅／「各」展開逐檔。
  - 真檔就地變異（RL-0021；存原文寫回＝RL-0019；兩發單獨跑不疊加＝RL-0005）：暫改憲法 §III.2 (ii) 列 `src/views/manage/role/index.vue` 之處數 → rc 1 指名該三元組 → 寫回；暫改同列 `src/components/advanced/table-header-operation.vue` 之塊數 → rc 1 指名該檔 → 寫回；兩發後 `git diff --name-only` 零殘留。
- **時序**：本刀 U0 之後、首個觸及 base-web 既有檔之單元之前（含依 spec FR-004 把新拒因鍵落入三檔 locale 與 `app.d.ts` 之後端單元）；碼面閘加腿、不佔 GT 名額；pre-commit fork-delta 段觸發字面不變（`base-web`／本體／憲法 staged）、`test_hook_wiring` 之 `SEGMENTS` 不動。
- **同批文件面**（RL-0011 種子③④）：工具檔頭 docstring 與 `main()` 之 `test` 成功訊息；`.githooks/pre-commit` fork-delta 段註解之擋因列舉（補範圍欄計數不等即擋）與憲法觸發源理由句（補範圍欄對賬；該段註解不在 `test_hook_wiring` 之 `SEGMENTS` 觸發字面內、改之不動 `SEGMENTS`）；RUNBOOK §12 工具鏈速查表與碼面閘表之 fork-delta-lint 兩列；`docs/ops/reference-src/code-gate-contracts.md` §4（「兩腿」改寫、補對賬腿契約）；README 樹之 fork-delta-lint 行；活書 08 §8.4 之「新增型只驗圈界 token 在場…不過三元組判定」機器守射程句（ADR-00063 決定四）；`find_unmarked_additions` 已知可接受殘留①之碼註補指 §III 修改型 Vue 模板屬性行變體句（ADR-00063 決定三）。
- 本工具為隨遷工具：RL-0076 之 comment-overlap rc 0 要求不適用；新腿碼註以 rev6 語境書寫。

### 2.2 seed-view-gate（ADR-00071）

- 決定本體＝ADR-00071 決定 1～9（判準、豁免恰兩列與到期／幽靈語意、python 實作、退出碼與缺席語意、讀面 (a)／(b)、接線、自證、不佔 GT、跨刀活體契約）；本節只寫施工面。
- 新建 `tools/seed-view-gate.py`；藍本＝rev5 `9d709d4:tools/seed-view-gate.py`（豁免表恰兩列之原始版）——不取 rev5 HEAD 版（其豁免表已歸零、自測斷言空表，與 spec FR-043 相衝）。rev6 改寫點：seed 檔 `rust-api/migration/src/m0002_baseline_seeds.rs`；豁免指針 BL-00045；tracked 面缺席 rc 2、不設具名跳過；`test` 子命令入 pre-commit `for` 自測迴圈；`check` 不連帶跑自測（ADR-00071 決定 6②）；名冊權威 RUNBOOK §12 碼面閘表；讀面型標註。非隨遷工具 ⇒ 交付前 `python3 tools/comment-overlap.py tools/seed-view-gate.py` rc 0（RL-0076；rev5 同相對路徑檔在）。
- **接線**（同一單元、同一顆外層 commit；ADR-00071 決定 6）：

| 面 | 施工 |
|---|---|
| `.githooks/pre-commit` 條件段 | 新段標籤 `seed-view-gate`：觸發 `-e 'base-web' -e 'rust-api' -e 'tools/seed-view-gate.py'`、命令 `python3 "$HOOK_DIR/../tools/seed-view-gate.py" check`、段內零條件判斷；段位＝route-artifact-gate 段之後、submodule-sync 段之前（碼面閘段群之尾） |
| `for t in …` 自測迴圈 | 加 `tools/seed-view-gate.py`（`check_hook_wiring` 強制碼面閘表全員入迴圈） |
| `tools/docsync/tests/test_hook_wiring.py` | `SEGMENTS` 增一元組（標籤、三觸發字面、命令字面同上）；`MIRROR_WORDS` 增 `"seed-view-gate": "seed-view-gate"`；`MIRRORS` 所列三處人寫鏡像行（pre-commit 檔頭段序行、README `├── .githooks/` 行、README `- **守門**：` 行）各補字樣恰一次；模組 docstring 之「十二條件段」與其段名列舉同改 |
| `tools/bootstrap.sh` | 隨遷工具自測名冊由 tracked 檔推導、不加行；名冊註解「六支碼面閘」與其列名括號同改 |
| `docs/ops/RUNBOOK.md` §12 | 工具鏈速查表一列＋碼面閘表一列（觸發時機欄尾分標：(a) base-web `src/views/**` 與 `src/router/elegant/imports.ts`、(b) `rust-api/migration/src/m0002_baseline_seeds.rs`；根據 ADR＝ADR-00071＋ADR-00055 決定 3＋ADR-00019 決定 3／決定 4）——GT-12 腿雙向對賬 |
| README 工具樹 | 一行（GT-09 對賬） |
| 活書 05 建構塊視圖之 `tools/` 列 | 補一項 |
| `docs/ops/reference-src/code-gate-contracts.md` | 新增一節：行為契約（判準、豁免與到期語意、退出碼、讀面型；ADR-00071 決定 9）；接線落點不收（ADR-00041 決定 2） |
| 其餘工具逐支列舉之現在式面 | 以 `git grep -n route-artifact-gate` 現量枚舉、逐處判讀補列 |

- **RL-0011 種子**：「六支碼面閘」（`.githooks/pre-commit` 碼面閘段首句、`tools/bootstrap.sh` 名冊註解）、「十二條件段」（`test_hook_wiring.py` 模組 docstring）——處數以 `python3 tools/docsync errata 六支碼面閘`、`python3 tools/docsync errata 十二條件段` 現量（兩子庫 pin 樹在內）、不寫死。
- **時序**：不早於回收桶頁 view 落地（同單元或其後；`view.manage_policy-archive` 不入豁免、不以暫列第三列過渡）；ADR-00071 不晚於接線單元同顆 accepted（RUNBOOK §12「根據 ADR」欄只收 accepted 號）。
- **一正一反**（ADR-00071 決定 7）：正＝真 repo `check` rc 0、輸出列豁免兩鍵；反（合成）＝`test` 全案；反（真檔暫改、變異打在 view 側）逐步：
  1. `docker compose -f docker-compose.yml -f docker-compose.dev.yml stop base-web`（停 vite dev 之檔樹輪詢，免外掛隨暫移與移回重算產物四檔）。
  2. 暫移一支 seed 所引且不在豁免表之 view 目錄至 base-web 工作樹外（例 `base-web/src/views/about/`＝seed sys_menu 列 11 之 `layout.base$view.about`，兼驗帶佈局形）。
  3. `python3 tools/seed-view-gate.py check` → rc 1，指名 `view.about` 與 seed 列 id（缺 view 腿），並報導出集≠`imports.ts`（結構腿）。
  4. 移回原處 → `git -C base-web status --porcelain` 回基準（RL-0005）。
  5. `docker compose -f docker-compose.yml -f docker-compose.dev.yml start base-web` → 再以 `git -C base-web status --porcelain` 與 `python3 tools/route-artifact-gate.py check` 復核仍回基準。
  - seed 側不作真檔暫改（憲法 §I.5 例外② 鎖定檔）、由合成案承擔。

## §3 既有閘與名冊擴充

| 對象 | 擴充（同單元） |
|---|---|
| `rust-api/server/tests/authz_entrypoint_lint.rs` | ①`RELOAD_CALL_FILES` 加 `handler/policy_archive.rs`（路徑字典序 `handler/menu.rs` < `handler/policy_archive.rs` < `handler/role.rs`；與 restorePolicy 之同步接線同一 commit＝ADR-00067 決定 5），doc 之觸發門句（「實際歸檔 ≥1 列」）於授予面落地單元即改（授予面之門＝Applied；`handler/role.rs` 已在冊）、復原類與本擴列同顆補齊（research R10） ②`DOMAIN_LOCK_CALL_FILES` 不變（入域兩支住已在冊之 `handler/role.rs`；restorePolicy 不入域——`handler/policy_archive.rs` 生產面一出現 `enter_menu_domain` 即紅）③`DOMAIN_WRITE_SIDE_FILES` 加 `model/facade/sys_casbin_policy.rs`、型長 `[&str; 7]`→`[&str; 8]`，`planting_lock_uses_turns_leg_five_red` 內 per-user 鎖植入之逐檔清單七檔→八檔、常數 doc「七檔」同改——★漏列不轉紅（該常數只是 `leg_per_user_lock_in_domain` 之過濾集）＝靜默缺口、tasks 明列 ④植入案期望紅集字面：`planting_reload_use_turns_leg_one_red_outside_exempt_faces` 之 `&["handler/ip_rule.rs", "handler/menu.rs", "handler/role.rs"]` 依新檔入掃描面之實況補 `handler/policy_archive.rs`；`planting_lock_uses_turns_leg_five_red` 之域鎖期望紅集不變（名冊未變）⑤`ENFORCER_WRITE_FILES` 維持空冊 |
| `handler/common.rs::each_domain_keeps_its_own_log_literals` | 逐域表加 `policy_archive.rs` 一列（target `security.policy_archive`、拒寫 `refused = "request_context_absent"`／`endpoint`／`uid` 與本域訊息、本域專屬 `BODY_FALLBACK_MSG`〔行首 `const BODY_FALLBACK_MSG: &str = "…"`、不得與既有各域同字〕）；`role.rs` 列不變（三維授權沿 `security.role` 與其既有 `BODY_FALLBACK_MSG`）；新檔須有行首 `fn operator_from(`、拒寫以 `AppError::Internal` 收尾、body 取用以 `common::json_or_default(` 限定路徑形呼叫——★漏列不轉紅（`include_str!` 寫死之元組表）＝靜默缺口、tasks 明列 |
| `handler/ip_rule.rs::production_code_emits_no_degraded_field` | 射程檔集加 `policy_archive.rs`（錨＝行首 `fn operator_from(`）——★漏列不轉紅（同上、寫死之元組表）＝靜默缺口、tasks 明列 |
| `handler/role.rs::domain_write_ends_enter_the_domain_first_and_roll_back_explicitly` | 生產區 `reload_enforcer` 出現處之期望（現＝匯入句＋收場件內一處）隨授予面收場件同單元改寫（ADR-00067 後果「碼面連動」）；新入域兩支之「內層首句＝`enter_menu_domain`」源碼釘同檔補 |
| `handler/mod.rs` 檔頭 | 「業務 handler 八域」→九域；宣告行 ASCII 升冪句補 `policy_archive`（`menu` < `policy_archive` < `role`）；`role` 域之端點數句改寫；宣告 `pub mod policy_archive;` |
| `model/facade/mod.rs` 檔頭 | 「十一支對十二張表」→「十二支對十二張表」；「例外恰一」仍＝`sys_casbin_archive`（同寫授權表與歸檔表）；成員 ASCII 升冪句補 `sys_casbin_policy`（`sys_casbin_archive` < `sys_casbin_policy` < `sys_ip_rule`）；活書 05 同句同批 |
| `model/facade/sys_casbin_archive.rs` 具型交易機器守（模組 doc 之 `no_run` 正面孿生＋逐支 `compile_fail`） | 本刀新增之公開寫入入口（撤銷移入歸檔、復原）同批補正面孿生與各一段以 `&sea_orm::DatabaseConnection` 呼叫須編不過之段；新建 `model/facade/sys_casbin_policy.rs` 之公開寫入入口（授予 INSERT）同形補 |
| `error.rs` 名冊兩測 | `msg_keys_roster_is_pinned_and_unique`、`biz_keys_are_in_roster`（`contracts/msg-keys.md` §3） |
| ROUTES 釘值（★兩處 MUST 同單元） | `rust-api/server/src/router.rs` 之 `routes_block_literal_form_and_pinned_rows`（`ROUTES_COUNT` 39→49 與逐列斷言、斷言訊息之「三十九」）＋`ROUTES_COUNT` 常數與 ROUTES doc「現行三十九條」；外層 `tools/docsync/tests/test_references.py` 之 `TestRoutes::test_real_repo_pinned_rows` 兩份字面表（元組表與渲染行表）各 +10 列與其註解。10 列接表尾、依 rev5 表序之相對次序：get-role-menu、update-role-menu、get-role-button、update-role-button、get-role-endpoints、update-role-endpoints、get-archived-policies、restore-policy、get-all-buttons、get-all-endpoints（rev5 夾於其間之 get-all-pages 為 rev6 既有、不重列）。理由＝pre-commit 只在 staged 含 `tools/docsync/` 時才跑 docsync 自測，不同批即靜默紅（005 刀工程判斷 33 前例）；收尾跑 `python3 tools/docsync test`＋`python3 tools/docsync generate`（routes 生成表重算） |
| `rust-api/server/tests/contract.rs` | case registry 恰三十九→四十九（模組 doc 與 `registry` doc 同改）＋覆蓋閘兩向（`coverage_gate_every_route_has_case`／`coverage_gate_every_case_has_route`）；新十支各經 policy 驗證函式（形同 `verify_role_menu_policy`；其 doc「十七支皆經」同改或另立同形函式）；授權態矩陣新建一表（形同 `ROLE_MENU_AUTHZ`＋`role_menu_authz_matrix_real_seed`；新路由接表尾、既有 17 列之連續段不受擾）；`role_and_menu_write_refusals_add_no_context_absent_leg_real_seed` 擴及新四支 POST 寫端（spec FR-006「不增計降級計數」之機器面）；新三鍵發出段（`contracts/msg-keys.md` §4） |
| `tests/wire_schema.rs`／`tests/wire_i64_guard_lint.rs` | §4 |
| `envelope.rs::page_or_all_production_call_sites_match_the_roster` | 不動（getArchivedPolicies 直呼 `envelope::page_params`、不得用 `page_or_all`） |
| `model/audit.rs`／`model/facade/sys_operation_log.rs` | `EXPECTED_LITERALS` 五詞不動（零新變體）；`AuditEvent` doc 之 `entity_table` 列舉補授權寫端（標的表＝`sys_role`）；`sys_operation_log` 模組 doc 之寫入者列舉補三維授權寫端與 restorePolicy |
| `obs.rs` | `casbin_reload_total` 三值顯式零與「樣本行恰三」不動；`IP_DOMAIN_DEGRADED_SOURCES` 不動 |
| `tools/msg-key-gate.py`／`tools/route-artifact-gate.py`／`tools/view-render-guard.py` | 程式不動：msg-key-gate 之 `FRONTEND_MSG_CONSUMERS` 不動；route-artifact-gate 只讀 (i) 列、回收桶頁落地單元實跑 `check`；view-render-guard 射程自動涵蓋 §1.3 三支 view 新檔與兩顆彈窗 |
| `tests/entity_access_lint.rs`／`tests/test_module_tail_lint.rs` | 程式不動；兩新檔分述：①`handler/policy_archive.rs` 自動入 `entity_access_lint` 掃描面（src 全樹減 facade 一層＝零 path-root `entity::`），並經 `each_domain_keeps_its_own_log_literals`／`production_code_emits_no_degraded_field` 兩逐域名冊之 `("<名>.rs"` 形字面入 `test_module_tail_lint` 判準①射程 (b)（測試模組 MUST 居檔尾）②`model/facade/sys_casbin_policy.rs` 屬 `entity_access_lint` 之排除層（facade）、亦無名冊字面路徑入判準①射程，只受判準②（src 全樹生產面零 `obs::` 出口別名匯入）約束 |
| `test_kit::ID_RANGES` 等測試件 | §5.3 |

- **數量詞與現在式假述種子**：家＝research「R17 as-built 改寫義務」（RL-0011 四形；種子、現在式面分布與承載單元以該表為準；處數以 `python3 tools/docsync errata <詞>`〔含兩子庫 pin 樹〕＋施工中 `git -C <子庫> grep -n <詞>`〔工作樹〕現量、tasks 不寫死）。本節只另列該表未收、屬本檔施工面之種子：
  - 「七檔」：`tests/authz_entrypoint_lint.rs` 之 `DOMAIN_WRITE_SIDE_FILES` doc 與植入自證案 doc（本表該檔列 ③）。
  - `tests/common/mod.rs` 守衛族說明與 `RestorePlan` 系 doc 之還原描述（先刪 `id >` 水位、再 setval 回 arm 值；定位＝`git -C rust-api grep -n 'setval 回 arm 值' -- server/tests/common/mod.rs`）：授權腿與歸檔腿擴回補後失準（§5.1）；src 側 `test_kit.rs` 檔頭同語意句由 research R12 決定 1 承接。
  - 閘與工具面之同批清單分見 §2.1、§2.2、§6（其中該表未收者＝「兩腿」〔`docs/ops/reference-src/code-gate-contracts.md` §4〕、「不補不改」〔走查工具射程界句〕；「六支碼面閘」「十二條件段」「只刪不補」「刪上界以上列」「八端點」「八支皆已接真」與 `model/facade/sys_role.rs` 取件清單〔補 `active_code_of`／`active_ids_by_codes` 兩支〕已在該表、不另列）。

## §4 wire 裁判面（`rust-api/server/tests/wire_schema.rs`；spec FR-052）

- **受審名冊**＝`src/typings/api/rev6-authz.d.ts` 之 `Api.Authz` 節全部 wire 型（三維現況讀、三維寫端請求與回應、候選讀、回收桶列與查詢、復原請求；實數以抽取為準、型名與欄形依兩支 wire 契約）；每型一行 `const …_DEF: &str = "Api.Authz.<型>";`、依下表入 `AUDITED_READ_DEFS` 或 `AUDITED_REQUEST_DEFS`。
- **逐型側別**（兩冊不交＝`audited_roster_is_complete_and_present_in_snapshot` 之「同一 definition 不得同屬讀端冊與請求端冊」斷言 ⇒ 每型恰屬一側；判準＝該 definition 之主要受裁面——後端序列化輸出＝讀端冊、前端送出形之反序列化落點＝請求端冊；query 型屬請求端冊＝既有 `ROLE_HOME_QUERY_DEF`／`ROLE_LIST_QUERY_DEF` 先例）：

  | 側 | 型（`Api.Authz.` 前綴省略） |
  |---|---|
  | `AUDITED_READ_DEFS` | `RoleMenuItem`、`RoleButtonItem`、`RoleEndpointItem`、`RoleMenuGrantRes`、`RoleButtonGrantRes`、`RoleEndpointGrantRes`、`Endpoint`、`ArchivedPolicy`、`ArchivedPolicyDimension` |
  | `AUDITED_REQUEST_DEFS` | `UpdateRoleMenuReq`、`UpdateRoleButtonReq`、`UpdateRoleEndpointsReq`、`RoleIdQuery`、`ArchivedPolicyListQuery`、`RestorePolicyReq` |

  - 兩向使用之型擇一側之判準：`Endpoint`＝讀端冊（getAllEndpoints 回應項＝後端序列化輸出；其請求面由 `UpdateRoleEndpointsReq` 之逐欄簽名〔`endpoints` 元素指向本型〕與合法形反序列化承載）；`ArchivedPolicyDimension`＝讀端冊（後端唯一產出點＝`ArchivedPolicy.dimension`；查詢串之 `dimension` 後端以字串承接、未知值靜默不濾，請求面不裁值域——`ArchivedPolicyListQuery` 之逐欄簽名只釘其型與可空性）。
  - ★`ArchivedPolicyDimension` 為字串字面聯集、非 object：現行讀端鍵集表驅動案（`every_audited_read_type_serializes_to_exactly_its_snapshot_key_set`）要求讀端冊恰等於鍵集表、且逐型全欄形須為 JSON object ⇒ 施工單元同批為該表增「封閉字面聯集型」一類（判準＝快照 `enum` 值集恰等於釘值三值、rust 側三值逐值序列化過裁判、值域外／大小寫異形／非字串判否；rev5 同型裁判形）；MUST NOT 以略出名冊或改成 object 形迴避（讀端冊收後端產出之型；rev6 既有同形型 `Api.IpRule.RuleType` 不在受審名冊〔該節不受完備性腿約束、經 `$ref` 由請求型裁〕，本處為施工層判斷）。
- **完備性腿**：`in_role_menu_sections` 之前綴謂詞擴及 `Api.Authz.`（其 doc「本刀兩節」與 `audited_roster_is_complete_and_present_in_snapshot` doc③同改）——不擴＝新節之型漏審不紅。
- **每型正向＋反例**（藍本＝rev5 rust-api `dc1cc8c` 之 16 支裁判〔rev5 `Api.RoleAdmin` 12＋`Api.PolicyArchive` 4〕；其中首頁兩型之 rev6 對應已由 005 刀交付〔`ROLE_HOME_RES_DEF`／`ROLE_HOME_UPDATE_REQ_DEF`〕、不重列；rev5 之泛型寫端回應＋三具體別名改為三支具體型）：
  - 讀型：序列化鍵集＝快照 properties 鍵集（表驅動、005 形）＋逐型植入「多帶一欄」反例；★現況項之受保護旗標為必填布林——缺欄、非布林各一反例；候選讀型帶受保護欄即紅（spec FR-014「候選讀端不帶預標」之機器面）；端點鍵型缺方法、方法非字串；id 欄為字串即紅；回收桶列之可復原旗標非布林、維度值域外、歸檔者為數值（`null` 與字串為正）、時間欄非帶 `+00:00` 之 RFC3339 字串。
  - 請求型：逐欄簽名（欄名×required×型別正規形〔含可空性〕）一表釘值＋逐欄反例＋合法形反序列化進 rust DTO；★角色鍵以 `id` 以外之鍵（例 `roleId`）送即紅（spec FR-005「角色鍵一律 `id`」）；期望集元素型錯（選單維非數值、按鈕維非字串、端點維元素缺欄）各一。
  - 首屏真串：getArchivedPolicies 首屏 query 物件經 qs 6.15.1 容器內實跑之字面逐欄落點（形同 `FRONTEND_FIRST_SCREEN_QUERY` 案）、三支現況讀端之 wrapper `{ id }` 經序列化器產出之形；壞形收斂逐 query 型各一。
  - 分頁回應不另立 ListRes 型、直裁既有 `Api.Common.PaginatingQueryRecord`（實例化既有泛型＝005 形）。
- **`tests/wire_i64_guard_lint.rs`**：`GENERIC_WIRE_TYPES` 不變（仍恰 `envelope.rs::PageRes`／`envelope.rs::Res`；兩側皆不新宣告泛型 wire 型）；新 `Serialize` 型 MUST NOT 帶巢狀泛型 i64 欄（例 `Vec<i64>`）——絆線 `nested_generic_i64_fields_are_out_of_scope` 出現第一筆即紅＝當場拍板；id 一律具名欄經 `serialize_i64_number_guarded`；`generic_wire_types_are_not_instantiated_with_i64` 照綠。
- **快照**：`rev6-authz.d.ts` 自動入 `tools/wire-schema.py` 抽取面；`extract`（base-web 容器）重抽 `rust-api/server/tests/fixtures/wire-schema.json` 與 typings 同單元、兩 pin 同一顆外層 commit（wire-schema 段雙側觸發、submodule-sync 段閘面含兩者）；保留路由名對賬腿不受影響（回收桶頁非常量路由）。

## §5 測試基建

### 5.1 被撤 seed 授權列與界下歸檔列回補（spec FR-044／FR-051；MUST 早於任一撤銷 seed 列之寫端單元）

- **src 側**（`rust-api/server/src/model/facade/test_kit.rs`）：`CasbinRuleRowsGuard` 與 `RoleMenuDomainRowsGuard` 之授權腿於 arm 時另以 `to_jsonb` 快照 `id ≤` 帶界水位之 `casbin_rule` 全欄列；授權腿 Drop 序 MUST 為 ①刪 `id >` 水位 ②回補 `INSERT INTO casbin_rule SELECT * FROM jsonb_populate_recordset(NULL::casbin_rule, $1) ON CONFLICT DO NOTHING`（原 id 原值；先例＝`tests/contract.rs` 之 `SeedMenuDeleteNet`）③setval 回 arm 值。★①先於②：復原以新 id 回插同身分列、`unique_key_sea_orm_adapter`（`ptype, v0～v5`）在——先回補則 `ON CONFLICT DO NOTHING` 吞掉原列、新列隨後被①刪＝seed 列永久缺席。組合殼 Drop 序不變（指派→歸檔→授權→選單→角色）。
- **tests 側**（`rust-api/server/tests/common/mod.rs`）：`CasbinRuleWriteGuard` 與 `RoleMenuDomainWriteGuard` 之 `RestorePlan`／`run_restore` 同語意、同序擴回補（該檔明文「語意與 src 側同族逐項一致」）；回補語句模板兩側自持時，同批新增一支 `include_str!` 逐字對賬案（形同 `self_held_synthetic_uid_floor_matches_src_verbatim`）。
- **歸檔腿同形擴回補**（src 側 `PolicyArchiveRowsGuard`、tests 側 `PolicyArchiveWriteGuard`，及兩組合殼之歸檔腿）：arm 時另以 `to_jsonb` 快照 `id ≤` 帶界水位之 `sys_casbin_policy_archive` 全欄列；Drop 序 ①刪 `id >` 水位 ②回補 `INSERT INTO sys_casbin_policy_archive SELECT * FROM jsonb_populate_recordset(NULL::sys_casbin_policy_archive, $1) ON CONFLICT DO NOTHING`（原 id 原值；該表衝突面只有主鍵）③setval 回 arm 值。理由＝restorePolicy 之 Applied／NoOp 皆刪歸檔列，arm 前已在之界下歸檔列（走查或中斷跑次之殘列）一經案消費即不復返；兩表守衛同語意（凍結 seed 該表零列、seed 比對不受影響）。tests 側回補語句兩表各與 src 側逐字對賬（上條之 `include_str!` 對賬案同批涵蓋）。
- **自證**（RL-0080；自建列代 seed 列、不碰 seed）：嵌套守衛形——外守衛 arm → 以 nextval 植一列（落外水位之上、合成 id 界之下）→ 內守衛 arm → 刪該列並以同身分 nextval 回插新列 → 內 Drop 後原 id 原值在、新 id 列無、序列回內 arm 值 → 外 Drop 清之；歸檔腿同形一發（外守衛 arm → 以 nextval 植一列歸檔列 → 內守衛 arm → 刪該列〔模擬復原消費〕→ 內 Drop 後原 id 原值在、序列回內 arm 值 → 外 Drop 清之）；兩族各入其自證表（src 側 `nested_guards_restore_below_band_only_and_innermost_drop_clears_band_rows` 族、tests 側 `role_menu_single_write_guards_restore_rows_and_sequences`／`role_menu_domain_write_guard_restores_rows_sequences_and_op_log` 族）；反向變異＝暫把授權腿 ①② 對調 → 自證案必紅 → 寫回（RL-0019）；歸檔腿另一發＝暫拔回補步 → 自證案必紅 → 寫回（兩發單獨跑、不疊加＝RL-0005）。
- **seed 角色列欄值**（spec FR-051「測試不留 seed 列變更」）：會改 seed 角色列可變欄之案（例以 updateRoleHome 改 R_SUPER 首頁）一律於測試交易內 rollback，或以 `RowFixupGuard` 形快照被寫欄＋`updated_at`／`updated_by` 並於 Drop 寫回；src 側凡經寫端 commit 之案同掛 `OpLogRowsGuard`；寫端單元收尾加跑 `python3 tools/schema-gate.py check`（gate2 逐列比對 seed）。

### 5.2 殘列不連坐（BL-00136 形①；spec FR-045、SC-009）

- **兩案改錨**：`handler/route.rs` 之 `user_routes_tree_differs_by_role_and_home_is_navigable_leaf` 與 `model/facade/sys_menu.rs` 之 `seed_role_trees_differ_by_role_and_nest`——兩檔各自之 `seed_names_by_sql`（現以 `sys_menu.created_by IS NULL` 錨）改錨 `casbin_rule.created_by IS NULL` 之 seed 政策列；兩案寫死 seed 名之前提斷言（例「manage 零 R_ADMIN menu 政策」）改以 seed 政策列現算；兩案 `seed_names_by_sql` 之 doc 中說明 seed 錨、殘授權仍計入與 `casbin_rule.created_by` 轉接器落庫不寫而錨不到政策層之括號句（連同其「不在本案殘列不連坐射程」結語）同改（定位＝`git -C rust-api grep -n 錨不到政策層`）。
- **直種現役政策一律落非 NULL 建立者**：`test_kit::plant_live_policy` 保留轉接器 `add_policy`（判定面記憶體同持、已存在即 panic＝LL-00035 自證語意），同件內再以 raw SQL 對剛植之列補寫 `created_by`（非 NULL 之合成操作者 uid）；`model/facade/sys_menu.rs` 測試模組之 `plant_role_residue`（現直呼 `enforcer.add_policy`）改走 `plant_live_policy` 或同形補寫。
- **`tests/contract.rs` 兩處 raw INSERT**（`super_cannot_disable_msg` 之 R_ADMIN 植列；`seed_menu_delete_net_rewrites_the_deletion_pair_and_reinserts_removed_grants` 之合成角色植列）：補非 NULL `created_by`（判定之家＝research R12 決定 2；判準＝「測試直種現役政策一律帶建立者」之一致不變式——跨 run 異常終止之殘列可能與改錨案共存，任一處留 NULL 即被改錨案誤算為 seed）。
- 授予寫入面本身落 `created_by`＝操作者（spec FR-012）＝改錨之料源。
- **殘列演練**（主線對 dev 庫手植、不落 commit；005 刀號段形＋nextval 形之續行）納「經寫端授予之殘列」形（spec FR-045、SC-009 前半）：
  1. 植列＝nextval 形（不帶 id 之 INSERT）一列 `casbin_rule`：`ptype='p'`、`v0`＝R_SUPER 以外之 seed 角色（例 R_ADMIN）、`v1`＝其未持有之 seed 選單路由名（例 `manage_role`＝觸 BL-00136 條文所列「manage 零 R_ADMIN menu 政策」前提）、`v2='menu'`、`v3`～`v5`＝`''`、`protected` FALSE、`created_by` 非 NULL（寫端授予之列形；不改 seed 帳號之角色指派＝形②不在射程）。★不取 `test_kit::RESIDUE_DRILL_OWNER` 號段：該號段落合成 id 界之上、任一帶界守衛 Drop 即清（`test_kit.rs` 帶界水位 doc：「帶界後號段內的列〔含 arm 前即在者〕恆被清」），兩改錨案跑到時殘列多半已被清＝非承重；號段形演練（守衛清殘列之能力）照 005 刀形另跑、非本形之承載。
  2. 容器內全量測試全程 serial 全綠（兩改錨案須照綠；任何轉紅之案＝另一支對 seed 選單殘授權敏感之案、同單元改錨或升級）。
  3. 拔除＝依 id 刪除、序列 setval 回植前現讀值，再以 `python3 tools/schema-gate.py check` 綠（植前取過走查基準者另跑 `diff` rc 0）證回基準；植列期間有判定面同步者，拔除後重啟 rust-api；結果記單元 commit 訊息（005 刀殘列演練同形）。
  - 走查面同形＝quickstart §11（ADR-00068 款 10 之觀察授 seed 角色可見受保護選單列後、`restore` 前跑全量測試；Clarifications 第五題之具名例外內）。

### 5.3 號段與共用測試件

- **`test_kit::ID_RANGES`**（現型長 `[IdRange; 22]`）：新測試以顯式 id 造列者先依「表×檔」登記號段、型長同批改（`id_ranges_sit_above_floor_and_do_not_overlap_within_a_table` 守不重疊）；歸屬 `tests/` 之號段由 `tests/common/mod.rs` 以同值字面自持、`self_held_id_ranges_match_src_registry_verbatim` 逐字對賬（`self_held_id_ranges` 型長同改）。
- **觸發矩陣計數件**：私有 `reload_counts(render) -> (u64, u64, u64)` 現有兩份（`handler/role.rs`、`handler/menu.rs` 之測試模組）；`handler/policy_archive.rs` 測試需要時即第三份——依 `handler/common.rs` 檔頭所載 BL-00090／BL-00113 之收攏與重評紀律判定自持一份或提升進 `handler/common.rs`（與回收桶讀端之操作者帳號名批次換算包裝件依同一紀律各自判定），research 記判定與判準。樣板案＝`handler/role.rs` 之 `deleting_granted_roles_syncs_the_face_once_and_zero_policy_deletes_do_not`、`a_role_delete_dropped_before_the_face_is_replaced_still_syncs_it`（取消安全）、`refused_or_empty_role_deletes_do_not_sync`。
- **域鎖等待機器證**（spec FR-049）：`handler/role.rs` 測試模組既有之 `contend`／`settled`（帶 `enters_domain` 參數）＋`sys_casbin_archive::menu_domain_waiter_count`（64-bit key 拆兩欄比對）；入域兩支各一等待案（形同 `delete_role_waits_behind_the_menu_domain_holder`），端點維寫端與 restorePolicy 各一不取域鎖案（形同 `add_role_passes_the_menu_domain_holder`）；restorePolicy 之案若住 `handler/policy_archive.rs`，其 helper 依上條同判。
- 手寫 `casbin_rule` 列（植入、比對、清除條件）v3～v5 一律 `''`、比對用 `= ''`（LL-00043）。

## §6 走查工具擴面（`tools/walkthrough-baseline.py`；spec FR-044、Clarifications 第五題）

- **基準檔 v3**：`SCHEMA_VERSION` 2→3；snapshot 另存兩欄：①`casbin_rule` 之 `id ≤` 上界全欄列（`id`、`ptype`、`v0`～`v5`、`protected`、`created_at`、`created_by`）②`sys_role` 之 `id ≤` 上界列之可變欄（`role_home`、`status`、`role_name`、`role_desc`、`role_memo`、`updated_at`、`updated_by`）——★射程刻意取「`id ≤` 上界之角色列」（seed 角色列之超集）：判準＝與①同一「取樣時已在之列」射程、工具不另立 seed 識別條件；必含 seed 三列＝ADR-00068 決定 4②、spec Clarifications 第五題所需之最小射程，取樣前已在之殘角色列一併回寫＝回基準之原意、無害；v2／v1 舊檔之 `diff`／`restore` rc 2、指名重新 snapshot；`validate_snapshot` 同驗新兩欄之形。
- **restore ③b 寫面**（同一交易、次序固定）：指派鍵集差刪除 → 四表刪 `id >` 上界 → ★`casbin_rule` 回補基準有而現況無之列（原 id 原值、`ON CONFLICT DO NOTHING`；★排在刪 `id >` 上界之後，理同 §5.1）→ `sys_role` 可變欄與基準不等之列回寫基準值（含審計欄：改回值也改回痕）→ 四支 setval。射程界改述為「補回被刪之授權列、回寫角色列可變欄；其餘欄之就地改寫與他表 `id ≤` 上界列之被刪不還原」——歸檔表 `id ≤` 上界之列被復原消費不在射程（凍結 seed 零列；基準檔模式下由收尾 `diff` 之列數報出）。
- **`restore --seed`**：目標＝凍結 seed（`specs/001-schema-baseline/fixtures/seed.sql`）之 `casbin_rule` COPY 163 列全欄與 `sys_role` COPY 之可變欄，經既有 `_seed_copy_rows` 解析；兩料源（該 COPY 段與 `rust-api/migration/src/m0002_baseline_seeds.rs` 之 `SEED_CASBIN_RULE`）163 列於 `id`、`ptype`、`v0`～`v5`、`protected`、`created_by` 逐列相同、`created_at` 同一時點。
- **重啟句**：`casbin_restore_touches` 擴及「將回補 ≥1 列」（寫入前現讀判）＝輸出 `CASBIN_RESTART_HINT`；`sys_role` 回寫不需重啟（角色成員與首頁每請求自 DB 讀）。
- **自測**：逐字釘之寫面常數（`ROLE_MENU_SURFACE_AT_SEED` 等）、`STUB_BOUNDED_IDS`、`SEED_RESTORE_TEXT` 之 casbin COPY 樁（現只三欄）擴為全欄、sys_role COPY 樁（現只 `id`／`created_at`／`role_code` 三欄）擴含 `role_home`／`status`／`role_name`／`role_desc`／`role_memo`／`updated_at`／`updated_by`，皆改為新寫面；新增：回補語句排在刪上界列之後之序釘、v2 舊檔 rc 2、只有回補時之重啟句輸出、角色列回寫語句、v3 欄形驗證之一正多反。
- **同批**（RL-0011 種子「只刪不補」「刪上界以上列」「不補不改」「v2」「兩欄」）：RUNBOOK §9c 契約與 §12 工具鏈速查表之 walkthrough-baseline 列、工具 docstring、README 工具樹該行、活書 05 同語意句。
- **時序**：早於 CDP 三方對照單元（spec FR-044）。CDP 已知態觀察步驟對 seed 角色之寫入（Clarifications 第五題、ADR-00068 決定 4）前後套本工具：觀察前 `snapshot`、觀察後 `restore`＋重啟 rust-api、`diff` rc 0＋`python3 tools/schema-gate.py check` 綠。

## §7 觀測與告警

- **零新序列、零新告警**（ADR-00067 決定 8）：`casbin_reload_total{outcome=ok|retry|exhausted}` 值集與開機預註冊不變；`deploy/grafana-provisioning/alerting/rules.yml` 之 `obs016-casbin-reload-anomaly` 之 uid、title、summary 與判準不變；其段錨註解「（島 H2；判定面同步＝ADR-00043）」依 ADR-00063 親決題 H-a 之結果改指（取建議①＝島 G1、H2 互引）並補引 ADR-00067，歸判定面同步觸發列增列之承載單元（ADR-00067 後果「碼面連動」）。
- 授予面 Applied（含空 diff）與 restorePolicy Applied 各觸發一次同步 ⇒ `ok` 每請求至多 +1；Rejected／NoOp／NotRestorable／查無角色零增（機器面＝觸發矩陣特性測，§5.3）。
- **RUNBOOK 同批**（ADR-00067 決定 9）：§11.2 `ok` 判讀句改三類觸發（字面同 ADR-00067 決定 1）；§13 補授予面反向症狀（新授之端點短暫仍回 `5003`、已撤之端點短暫仍放行——過渡窗有界自癒；耗盡窗沿既有四步處置）與排障錨；§13 步驟 1 之 log 字面列舉補授予面與復原之收場 task 被取消字面（字面由 tasks 定、與碼同批）；只寫實跑過之命令。
- 新 tracing target `security.policy_archive`（回收桶域拒寫事件）屬 operator 可見輸出：活書與 RUNBOOK 若有 target 列舉處同批補（以 `git grep -n 'security.role'` 現量枚舉）。

## §8 ADR 與帳本

### 8.1 ADR 之 accepted 時點（plan 期九支＋收刀前 PATCH ADR 一支；詳表＝research「ADR 配號與親決時點表」）

| ADR | 主題 | accepted 時點約束 | accepted 同顆 |
|---|---|---|---|
| ADR-00063 | Amendment 1.7.0 | 本刀 U0：user 逐款親決（親決題索引＝ADR-00063 決定六）→ accepted＝獨立一顆 Amendment commit（內容清單＝ADR-00063 決定六「Amendment commit」條，含活書 08 §8.4 之變體引文〔決定三〕）；施工前提 | 親決紀錄（日期、所在任務、逐題結果）；改動提案字面者同步改寫決定節、差異附表與 Amendment log |
| ADR-00064 | G6 結構性封死 | 依 research 表；決定 1／決定 2 為島 G6 條文所指、U0 同一親決輪先定，accepted 前 MUST NOT 改動（確需＝停手升級、條文指針另走 §V.2） | —— |
| ADR-00065 | 復原五腿＋不可復原集 3→5 | 同上；決定 1／決定 3 凍結 | —— |
| ADR-00066 | 全量替換射程＝候選集 | 依 research 表 | —— |
| ADR-00067 | 觸發列增列＋兩窗 | 同上；決定 1／決定 2／決定 6 凍結 | —— |
| ADR-00068 | ADR-00045 續行 | 治理單元（CDP 三方對照單元之後）user 逐款親決 | `supersedes: [ADR-00045]`、ADR-00045 status→superseded |
| ADR-00069 | ADR-00046 續行 | 治理單元 | `supersedes: [ADR-00046]`、ADR-00046 status→superseded |
| ADR-00070 | BL-00131 前端修 | 不早於治理單元對 ADR-00068 決定 3 所列、出自本 ADR 後果殘餘面之兩款候選定案（ADR-00070 決定 6）；決定 1／決定 2 為 §III.2 (iii) 列紀律欄所指、accepted 前凍結 | 定案結果改寫本 ADR 決定 6 與後果之對應引用 |
| ADR-00071 | seed-view-gate | 不晚於接線單元同顆（ADR-00071 決定 6④） | —— |
| 收刀前 PATCH ADR（配號待定＝屆時下一號；plan 期不起草） | (iii)(iv) 範圍欄預估值實數化（前例 ADR-00051；ADR-00063 翻案觸發器第三條） | 收刀前承載體檢單元：user 親決後 accepted、與 Amendment 同一顆獨立 `docs(constitution): amend` commit（§V.2 步 3／4） | 憲法版本 1.7.0→1.7.x、Amendment log、README 憲法版本鏡像、generate |

- proposed 期 `supersedes: []`；續行型 accepted 那一顆補 supersedes 並改被續行者 status、`superseded_by` 由 `python3 tools/docsync generate` 回填，generate 後再 `git add docs/arc42/decisions`（LL-00044）；新 ADR 檔先 `git add` 再跑 lint（GT-05 只掃 tracked）。
- 現在式面指向 ADR-00045／ADR-00046 之引用：治理單元以 `python3 tools/docsync errata ADR-00045`／`python3 tools/docsync errata ADR-00046` 現算、逐處改指（扣除史料面、生成鏡像、事件源與 ADR 檔；兩子庫另以 `git -C <子庫> grep` 並掃）；「八款」「七款」兩域計數句一律帶 ADR 號判歸屬（ADR-00068／ADR-00069 後果）。ADR 間互引一律「號＋決定款／款號」。

### 8.2 帳本

- **本刀第一筆 events 事件**：`backlog_add`＝BL-00137／BL-00138（兩條已於 brainstorm 顆入 BACKLOG、事件帳尚無）；notes 補記 NOTES「未決」所載兩筆 user merge＋push 同意（spec-compliance-005 merge `78d4700`、maint-backlog-128-129-130 merge `704f743`），同顆刪該未決條（spec FR-046）。
- **收刀 `feature_close`**：`backlog_done` 5＝BL-00084／BL-00131／BL-00132／BL-00134／BL-00135；條文改寫 3＝BL-00045（收窄為 008 刀之 system-settings／audit 兩頁）、BL-00048（觸發收窄 007 刀）、BL-00136（只剩形②＝使用者角色指派之殘列形、007 刀）；敘述改寫 1＝BL-00133（歸檔表已有消費面〔復原刪列〕、撤銷原因新增）；`backlog_add` 零（已由第一筆事件帶）；`adrs`＝plan 期九支 ADR-00063～ADR-00071＋收刀前 PATCH ADR 一支（配號待定＝research「ADR 配號與親決時點表」末列；計數同 spec FR-041／FR-046／SC-014）；`arch_impact` 以收刀時 diff 現算之活書節號為準。
- **BL-00132 兌現射程**（spec FR-042）：憲法範圍欄入機器對賬（§2.1）；活書 08 §8.4 之逐檔數本已寫「兩數皆以現算為準」之命令形、不另對賬——收單事件註明此射程、不另立衍生 BL（此射程只指對賬腿；§8.4 as-built 實數與新檔清單之現在式改寫仍屬治理單元＝research R17）。
- **反向確認**（收刀前承載體檢單元、命令現算）：BL-00047——`rust-api/migration/src/` 之 migration 恰 `m0001_baseline_schema.rs`／`m0002_baseline_seeds.rs`、`docs/ops/reference-src/schema-evolution.json` 之 `entries` 為空；BL-00108——rust 側零第三份字元級解析組（seed-view-gate 以 python 實作；`tests/entity_behavior_lint.rs` 零 diff）；`FRONTEND_MSG_CONSUMERS` 仍恰 1 項；零新依賴（`rust-api/Cargo.lock`、`base-web/pnpm-lock.yaml` 自本刀起點 pin 起零 diff）。
- **收刀前承載體檢單元另複核**：憲法 H1 括號之兌現（選單維與按鈕維授權寫端已入域＝updateRoleMenu／updateRoleButton 兩支內層首句＝`sys_casbin_archive::enter_menu_domain` 之源碼釘〔`handler/role.rs` 之 `domain_write_ends_enter_the_domain_first_and_roll_back_explicitly`〕在案，且兩支入域等待案在案——`DOMAIN_LOCK_CALL_FILES` 含 `handler/role.rs` 自 005 刀即成立、不承重；不可復原集 3→5 已落地＝`sys_casbin_archive::is_non_restorable_reason` 五值成員測綠）（ADR-00063 後果「H1 括號之兌現窗」）；(iii)(iv) 範圍欄 PATCH 實數化（§1.2）；§1.4 變更檔集斷言全量復跑。
- **收刀 DoD 之機器面**（spec FR-054）：容器內後端全量測試全程 serial＋contract 49 case；`pnpm typecheck`；碼面閘表全員 `check` rc 0（名冊唯一權威＝RUNBOOK §12 碼面閘表；本刀後成員＝`python3 tools/schema-gate.py check`、`python3 tools/entity-drift-gate.py check`、`python3 tools/rust-fmt-gate.py check`、`python3 tools/wire-schema.py check`、`python3 tools/fork-delta-lint.py`〔含 §1.1 名冊載入變異自證、§2.1 對賬腿、修改型只在授權檔〕、`python3 tools/msg-key-gate.py check`、`python3 tools/view-render-guard.py check`、`python3 tools/route-artifact-gate.py check`〔容器在場〕、`python3 tools/seed-view-gate.py check`；容器依賴者具名跳過不算驗收）；`python3 tools/docsync check`／`lint` 零紅；走查基準 `diff` rc 0。
