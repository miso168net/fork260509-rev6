---
id: "ADR-00071"
title: seed-view-gate 碼面閘——seed 選單 component 之 view 集 ⊆ base-web view 集、具名豁免恰兩列（system-settings／audit、附 BL-00045、到期即紅）、python 實作避開 BL-00108 第三份、讀面分型 (a)／(b)（ADR-00055 決定 3 之首例）
date: 2026-10-01
status: accepted
supersedes: []
superseded_by: []
provenance: "006-authz-governance 之 spec FR-041⑨、FR-043、US5 AS4 與其 Independent Test（刪一個 view 證必紅、具名豁免兩列照綠）、SC-011（seed-view-gate 綠且變異自證）、FR-054（收刀 DoD）、Edge Cases（自建選單不在其射程）；brainstorm §0 主線工程判斷④（seed-view-gate 照建）、§1 承襲盤點（seed-view-gate 順捎＝`rev5:006` §11-20）、§3 §3 前端節之 seed-view-gate 條（判準、具名豁免兩列附 BL-00045、接線四處）、§3 §4 工具節；BL-00045（豁免指針；本刀交付 policy-archive 頁後條文收窄為 008 刀兩頁）、BL-00108（rust 側 char 級解析工具組第三份之觸發）；ADR-00055 決定 3（新讀子庫工作樹之碼面閘進場同刀標讀面型，首例即本閘）、ADR-00019 決定 3／決定 4（hook 段零條件判斷；tracked 面缺席 rc 2、方向不類推）、ADR-00041 決定 2（跨刀活體契約收錄判準）；前代出處＝rev5 `tools/seed-view-gate.py` 之 `rev5:006` U7b 原始版（rev5 commit `9d709d4`；`rev5:B-088` 對賬閘、豁免指針 `rev5:B-008`、真檔暫改驗證依 `rev5:ADR 0024`）——不取 rev5 HEAD 版（`rev5:008` 刀已歸零豁免表、其自測斷言豁免表為空，與 FR-043 相衝）；draft 於 plan 期落 feature branch，accepted 時點依本刀 research 之 ADR 配號與親決時點表、上限見決定 6④"
tags: [code-gate, governance, base-web, roster, authz-governance]
---

## 背景

- 後端 seed 之 `sys_menu.component`（`view.<鍵>` 形；帶佈局者為 `layout.base$view.<鍵>` 形）是側欄選單項與前端頁面之唯一綁定，而它只是字串：seed 指向不存在之 view、或前端搬走／改名 view 而 seed 未動，兩向皆全套閘綠；症狀＝側欄出現點擊零反應之項、直打網址 404、選單標題顯路由裸鍵（BL-00045 條文）。
- 現況量測（量法＝`rust-api/migration/src/m0002_baseline_seeds.rs` 之 `SEED_SYS_MENU` raw 字串塊內 `\bview\.[A-Za-z0-9_-]+` 取相異鍵；`base-web/src/router/elegant/imports.ts` 之 views 匯入鍵取集合；本刀 plan 期現量）：seed 選單 78 列、帶 view 鍵之列 60、相異鍵 51；imports.ts views 鍵 49；seed 有而 base-web 無恰三鍵＝`view.manage_system-settings`（sys_menu 列 9）、`view.manage_policy-archive`（列 10）、`view.manage_audit`（列 77）；base-web 有而 seed 無恰 `login`（合法不對稱）。本刀交付 policy-archive 頁後剩兩鍵，屬 008 刀（BL-00045 收窄後之射程）。
- rev5 同名刀已建同閘，其原始版具名豁免恰兩列（同上兩鍵）；rev5 HEAD 版於其後刀兩頁兌現時歸零豁免表、自測改斷言空表。
- rev6 碼面閘既有形制：名冊唯一權威＝RUNBOOK §12 碼面閘表，GT-12 腿以「`tools/` 頂層 tracked `*.py` − `NON_GATE_TOOLS`」⇔ 表首欄路徑集雙向對賬；pre-commit 之 `for t in …` 自測迴圈須含碼面閘表 ∪ `NON_GATE_TOOLS` 全員（`tools/docsync/tests/test_hook_wiring.py` 之 `check_hook_wiring` 機器守）——rev5 讓本閘不進自測迴圈之具名豁免機制（rev5 `HOOK_TEST_LOOP_EXEMPT`）rev6 不存在；`tools/bootstrap.sh` 之隨遷工具自測名冊由 tracked 檔推導。
- ADR-00055 決定 3 預告：新讀子庫工作樹之碼面閘進場時同刀標 (a)／(b)；讀面落在閘面外且屬必須兜底者，於該刀另議擴閘面。
- BL-00108：rust 側 char 級源碼解析工具組已有第二份且分岔（`rust-api/server/tests/entity_behavior_lint.rs` 與 `wire_i64_guard_lint.rs` 各持一組），第三份出現即觸發收攏。

## 決策驅動因子

- 兩向失配要有 commit 級機器訊號（本刀起管理頁軌道會反覆增刪 view）。
- 豁免只能縮、不能養；到期必紅、機器強制。
- 不新增 rust 側 char 級解析第三份（spec FR-043 之 MUST NOT）。
- 讀面型照實登記、不宣稱有兜底（ADR-00055）。
- 零 docker、離線、毫秒級——可進 pre-commit 條件段與 bootstrap 體檢。

## 考慮過的替代案

1. **rust 側整合測試實作**（讀 seed 常數、掃 base-web 檔樹）：base-web 側須在 rust 內另寫 imports.ts 與 view 檔樹之文字解析＝BL-00108 所稱第三份；rust 測試一律容器內跑（RL-0045），而 rust-api 容器之 bind 掛載不含 base-web 樹（`docker-compose.dev.yml` 之 rust-api 服務 volumes）、讀不到 base-web 檔；且容器依賴使其進不了 pre-commit 常跑鏈。否決。
2. **不設閘、靠 CDP 對照抓**：CDP 只在收刀對照時跑、非每 commit；只覆蓋走查者點到之項；既有死項（008 刀兩頁）本就在 CDP 排除清單，新死項混入時結構上看不到；對無 rev5 對照之 rev6 新頁無基準。否決。
3. **豁免表為空**（rev5 HEAD 形）：本刀後 system-settings／audit 兩 view 仍缺 ⇒ 閘開場即紅；若為轉綠而刪 seed 兩列＝動 `m0002` 程式內容、越憲法 §I.5 例外②；與 FR-043「具名豁免恰兩列」相衝。否決。
4. **只以 imports.ts 鍵集當 view 集**（不自 view 檔樹導出）：imports.ts 是路由外掛產物，外掛未重算或產物未 commit 時判的是舊產物；route-artifact-gate 雖守重算冪等，但依賴 base-web 容器、未起＝具名跳過，離線時無守。雙源導出＋結構自證同時攔「加了 view 卻沒重算」。否決。

對所選方案跑同一反例（RL-0013）：①新增一支 seed 未引用之 view（例：未上選單之頁）→ 單向包含、不紅，成立。②搬走 policy-archive 頁 → 缺 view 紅；產物未重算時導出集≠imports.ts 另紅（外掛已重算則結構腿綠、缺 view 腿仍紅），成立。③008 刀交付 system-settings 頁而忘摘豁免 → 到期即紅，成立。④養第三列豁免蓋掉真缺頁 → 自測之豁免表恆定斷言紅，成立。⑤seed 檔有未 commit 改動而外層單獨 commit → 判的是工作樹＝ADR-00055 已登記之 (b) 型已知態（本 ADR 決定 5），不宣稱有兜底，成立。⑥超管自建選單指向不存在之 view → 射程外（seed 限定）、已知態＝ADR-00068 款 14（spec Edge Cases），成立。

## 決定

1. **閘與判準**：新建碼面閘 `tools/seed-view-gate.py`（python 標準庫、零 docker、零網路）。判準＝**單向包含 seed 集 ⊆ views 集**：
   - seed 集＝`rust-api/migration/src/m0002_baseline_seeds.rs` 之 `SEED_SYS_MENU` raw 字串塊**內**全部 `view.<鍵>` 字面（去重；`layout.base$view.<鍵>` 形亦收；塊外字面不收）。
   - views 集＝`base-web/src/views/**` 依 elegant-router（`@elegant-router/vue` 0.3.8；`base-web/build/plugins/router.ts` 未覆寫頁檔規則）預設規則導出之鍵集。
   - **結構自證**：導出集 MUST 恰等 `base-web/src/router/elegant/imports.ts` 之 views 匯入鍵集，雙向差集即紅（導出規則與外掛脫節、或 view 已動而產物未重算）。
   - 方向單向：base-web 有而 seed 無（例 `login`）＝合法不對稱、不紅。
   - 射程限 seed：超管經選單管理自建之選單不在射程（已知態＝ADR-00068 款 14；spec Edge Cases）。
2. **具名豁免恰兩列**：`view.manage_system-settings`（seed 列 9）、`view.manage_audit`（seed 列 77），各附 BL-00045 指針與解除謂詞（該鍵之 view 出現於導出集＝到期）。豁免表住工具模組常數、**不得取自 args／env／讀檔**；**到期即紅**（view 已存在而豁免未摘）、**幽靈亦紅**（豁免鍵已不在 seed 集）；「恰兩列且各含 BL-00045」由自測機器釘死——增列＝同批改自測斷言、於 diff 現形＝拍板級可見（rev5 自測 I 組四釘之承襲形：鍵集恆定、呼叫點原封傳入、判定函式零外部取值形、呼叫端零就地改表）。`view.manage_policy-archive` 不入豁免：本閘進場不得早於 policy-archive 頁落地（同單元或其後），不以暫列第三列過渡。豁免為本閘自持之到期語意、不入 docsync `DAY1_EXEMPTIONS`（該名冊屬治理閘）。
3. **實作語言＝python**：seed 側以逐行掃 raw 字串塊＋正則取 token，base-web 側以檔樹走訪＋imports.ts 行級正則——不持 rust 側 char 級源碼解析工具組 ⇒ 非 BL-00108 所稱第三份、該條不到期。先例：msg-key-gate 以 python 純讀檔解析 `rust-api/server/src/error.rs` 之 `MSG_KEYS`、wire-schema 之保留路由名腿以 python 對賬 `rust-api/server/src/model/facade/sys_menu.rs` 之 `RESERVED_ROUTE_NAMES`。
4. **退出碼與缺席語意**：rc 0 綠｜rc 1 紅（缺 view 之鍵逐鍵指名 seed 檔行號與 sys_menu 列 id；豁免到期或幽靈；導出集≠imports.ts 雙向差集）｜rc 2 結構異常（seed 檔、`SEED_SYS_MENU` 塊、views 目錄、imports.ts 任一缺席，或任一側掃到空集＝掃描面空集合即紅、RL-0051）｜rc 64 用法錯。tracked 面缺席一律 rc 2 fail-loud、不設具名跳過（ADR-00019 決定 4 方向不類推；rev5 之「worktree 未就位具名跳過」不帶回——bootstrap 已斷言兩 worktree 在場）。
5. **讀面型（ADR-00055 決定 3 之首例）**：base-web `src/views/**` 與 `src/router/elegant/imports.ts`＝**(a) 閘面內**（pre-commit submodule-sync 段之 base-web 閘面含 `src`）、延後至下次 base-web pin bump 補抓；rust-api `migration/src/m0002_baseline_seeds.rs`＝**(b) 閘面外、無兜底**。★**不擴閘面**：該檔程式內容依憲法 §I.5 例外② 鎖 rev5 凍結版（ADR-00009），任何改動本身即越例外射程、須另立 ADR 翻案 ⇒ 不屬 ADR-00055 決定 3 所稱「必須兜底者」。RUNBOOK §12 碼面閘表該列之觸發時機欄尾照 (a)／(b) 分標。
6. **接線四處（同一單元落地）**：
   - ①`.githooks/pre-commit` 新增條件段：`base-web` 或 `rust-api` gitlink 變動（pin bump）、或本體 staged 時跑 `check`；段內零條件判斷、不設跳過分支（ADR-00019 決定 3）。
   - ②自測：`test` 子命令＝離線合成 fixtures（暫存目錄）；入 pre-commit `for t in …` 自測迴圈（`check_hook_wiring` 強制碼面閘表全員入迴圈）；`check` 不連帶跑自測。rev6 碼面閘於此分兩派：rust-fmt-gate／msg-key-gate／view-render-guard／route-artifact-gate 之 `check` 不跑自測；schema-gate／entity-drift-gate／wire-schema／fork-delta-lint 則於 `check` 內先跑自測。本閘取前一派，理由＝自測只用合成 fixtures、結果只隨工具本體而變，而本體 staged 時 `for` 迴圈必跑其 `test`（`check_hook_wiring` 強制入迴圈），於 `check` 內再跑屬重複。防恆綠由 pre-commit `for` 自測迴圈（本體 staged 時）與 bootstrap 體檢之自測（見 ③）承擔——與 rev5 藍本「self-test 每次隨 `check` 連帶跑（防恆綠）」之刻意分岔（rev5 以此換得不入自測迴圈之具名豁免，該機制 rev6 不存在，見背景）。
   - ③bootstrap 名冊：由 tracked 檔推導自動納入（`tools/bootstrap.sh` 之隨遷工具自測名冊推導式），不手增名冊行。
   - ④RUNBOOK §12 碼面閘表一列：工具檔／守什麼／觸發時機（含缺席語意與 (a)／(b)）／根據 ADR＝本 ADR（並列 ADR-00055 決定 3、ADR-00019 決定 3／決定 4）——GT-12 腿雙向對賬、漏列即紅。「根據 ADR」欄只收 accepted 號（RUNBOOK §12 碼面閘表導言）且該欄無機器守 ⇒ 本 ADR 須不晚於接線單元同顆 accepted。
   - 連動名冊同顆改齊（`test_hook_wiring` 之 `SEGMENTS`／`MIRROR_WORDS` 與三處人寫鏡像行、README 工具樹一行、RUNBOOK §12 工具鏈速查表一列、活書 05 建構塊視圖 `tools/` 列一項；其餘現在式面之工具逐支列舉處以 `git grep -n route-artifact-gate` 現量枚舉、不寫死處數），逐項落點由本刀 contracts（code-gates）定。
7. **一正一反自證（RL-0080）**：
   - 正：真 repo `check` rc 0，輸出列出豁免兩鍵。
   - 反（合成）：`test` 覆蓋缺 view 紅、豁免生效綠、豁免到期紅、幽靈豁免紅、導出≠imports.ts 兩向紅、各側空集 rc 2、豁免表恆定四釘。
   - 反（真檔暫改）：變異打在 **view 側**。施作前提＝施作期間路由外掛不重算：dev stack 之 base-web 服務跑 vite dev 且檔樹輪詢（`docker-compose.dev.yml` 之 `CHOKIDAR_USEPOLLING`），未停則外掛可能隨暫移與移回重算產物四檔——暫移時 imports.ts 隨之變而結構自證腿不紅；移回後 `routes.ts` 走增量合併、上游路由之自訂 meta（例 `manage_role` 之 `icon`／`order`／`roles`）未必復原、工作樹回不到基準 ⇒ 先停 base-web 服務。暫移一支 seed 所引之 view 目錄 → `check` rc 1 且指名該 `view.<鍵>` 與 seed 列 id（缺 view 腿），並報導出集≠imports.ts（結構腿）→ 以原檔寫回還原 → `git -C base-web status --porcelain` 回基準態（RL-0005、RL-0019）→ 再起 base-web 服務後以 `git -C base-web status --porcelain` 與 route-artifact-gate `check` 復核仍回基準。逐步命令形由本刀 contracts（code-gates）定。seed 側不作真檔暫改（例外② 鎖定檔），由合成案承擔。變異打在判準上、紅證以 rc 與指名字面為準（RL-0029）。
8. **碼面閘不佔 GT 名額**：本閘屬碼面閘（RULES 名詞段）——不入 GATES.md、不計 GT-12 之治理閘預算；治理閘數維持 12。
9. **跨刀活體契約**：本閘之行為契約（判準、豁免與到期語意、退出碼、讀面型）入 `docs/ops/reference-src/code-gate-contracts.md` 新節（ADR-00041 決定 2 收錄判準成立：豁免表隨 008 刀縮、契約隨刀前進）；RUNBOOK §12 該列之契約指針指該節；刀內施工面留本刀 contracts。

- **親決紀錄**：user 親決 2026-10-04（006 刀 U14 派發前、tasks T071 之親決提前；AskUserQuestion 三輪逐款一題一問）——決定 1～9 皆照文定稿；零非建議項 ⇒ 決定節免改寫。

## 後果

- seed 與前端 view 之兩向失配自本刀起有 commit 級機器訊號；本刀交付 policy-archive 頁後，seed 對 base-web 之缺口只剩豁免兩列。
- 008 刀交付 system-settings／audit 兩頁時，本閘逐列到期即紅、同單元摘列；兩列摘盡後 BL-00045 收列——摘列須早於或同顆於 BL-00045 刪列（豁免值引 BL-00045；現行無機器守攔「tools 引用已刪列之 BL」（GT-05 之 ID 引用存在性腿只收 RL／GT／ADR／LL、GT-03 只核誕生集）——由刪列當顆以 `python3 tools/docsync errata BL-00045` 枚舉承擔（RL-0011））。
- 本閘非「隨遷工具」（RULES 名詞段；rev6 創世後新建）：承 rev5 藍本重打字、註解重寫（前代編號帶 `rev5:` 前綴；座標改 rev6：seed 檔名 `m0002_`、豁免指針 BL-00045、名冊權威 RUNBOOK §12），交付前 `python3 tools/comment-overlap.py` rc 0（RL-0076）。
- 施工面除工具本體外另涉下列他檔，逐項落點由本刀 contracts（code-gates）定、由 tasks 逐項收：`docs/ops/reference-src/code-gate-contracts.md` 新增一節（決定 9）；連動名冊＝決定 6 所列全數——`tools/docsync/tests/test_hook_wiring.py` 之 `SEGMENTS`／`MIRROR_WORDS` 與三處人寫鏡像行（pre-commit 檔頭段序、README 樹 `.githooks/` 列、README 守門條目）、README 工具樹、RUNBOOK §12 兩張表（工具鏈速查表、碼面閘表）、活書 05 建構塊視圖 `tools/` 列，及決定 6 所定 `git grep -n route-artifact-gate` 現量枚舉面；進場時序＝不早於回收桶頁落地（同單元或其後；決定 2）；RL-0011 勘誤種子「六支碼面閘」「十二條件段」（見下條）。
- RL-0011 勘誤種子：碼面閘支數字面（`.githooks/pre-commit` 碼面閘段首句、`tools/bootstrap.sh` 名冊註解之「六支碼面閘」與其列名括號）；條件段數字面（`tools/docsync/tests/test_hook_wiring.py` 模組 docstring 之「十二條件段」與其段名列舉）；處數以 `python3 tools/docsync errata 六支碼面閘`、`python3 tools/docsync errata 十二條件段` 現量、不寫死。
- (b) 讀面之已知邊界：seed 檔有未 commit 改動時判的是工作樹（ADR-00055 決定 1 同型）。
- 射程外：`m0003` 起之 delta migration 寫入或改動之選單列、超管自建選單。

## 翻案觸發器

- 首支寫入或改動 `sys_menu` 列 `component` 之 delta migration 進場 → 擴 seed 集讀面至該 migration（或改讀 schema 快照）、重審決定 1 與決定 5 之 (b) 判定。
- elegant-router 升版、或 `base-web/build/plugins/router.ts` 覆寫頁檔規則（`pageDir`／`pagePatterns`／`pageExcludePatterns`）→ 結構自證腿紅、重導導出規則。
- 豁免兩列之任一須延長至 008 刀以外（例：008 刀 brainstorm 翻 BL-00045 之射程）→ 同批改自測斷言並回本 ADR 決定 2 複核（拍板級）。
- (b) 型讀面實際漏網一次（以 commit 內容與閘判讀不一致為證）→ 重審決定 5 之不擴閘面。
- 超管自建選單指向不存在 view 之誤操作實際發生 → 評估於選單寫端驗 `component`（屬另一刀）。
