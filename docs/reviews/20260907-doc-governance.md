# 文件治理架構第二輪體檢（doc-governance、2026-09-07）

範圍＝rev6 文件治理架構（活書家族、ops 帳本、generated、README／CLAUDE.md／憲法、`tools/docsync`、`tools/orchestration`、碼面閘六支、`.githooks`、`.claude/hooks` 與 `.claude/skills`、`.specify/scripts`／`templates`、`docs/ops/reference-src`、LESSONS 12 檔；`rust-api/server` 與 base-web 新增檔只作 L5／L8／L11 之對賬事實源）；對象＝分支 `000-r2-doc-governance` @ `7b734e1`（開出點＝default `rev6-admin-root` @ `c097c48`，其上僅一顆計畫檔 T0 更正 commit＝史料面、不入判準）。計畫＝`docs/brainstorms/000-r2-doc-governance.md`（v0.3；§11 十題＋§11.2／§11.3 grilling 兩輪 Q11～Q19 全數裁定）。

## 0. 方法與取證

| run | runId | agent 數 | 內容 | 零寫入對賬 |
|---|---|---|---|---|
| A 探索 | `wf_57ff815d-4c9` | 18 | 12 lens（L1 事件與帳本的家／L2 權威鏈／L3 閘與規則覆蓋／L4 生成器與名冊／L5 rev5 承襲〔縮〕／L6 工作流可執行性／L7 時態鏡像／L8 活書事實／L9a・L9b 主張×閘×真源矩陣／L10 未讀面補掃／L11 碼面治理）＋6 探針；findings 95 | 外層／base-web／rust-api／rev5 四處 porcelain 前後相同 |
| B1 驗證 | `wf_2ed23344-8e1` | 22 | 批 1～11（54 筆）× R-real／R-decided 兩鏡三態 | 同上 |
| B2 驗證 | `wf_415d9f87-8d7` | 22 | 批 12～16（23 筆）× 兩鏡＋6 探針 grader→refuter＋完整性 critic | 同上 |
| C 補漏 | `wf_4bb5c3e8-cfc` | 9 | critic 缺口三支 lens（未讀面＋承襲射程／主張候選集完整性／檔→事件反向缺席）＋ inline 兩鏡 | 同上 |
| D 修單 | `wf_f3bbe7d9-c4a` | 14 | U-r2-gates：implementer→規格對照審查→fix 迴圈→碼品質審查→fix 迴圈 | 改動集 14 檔 ⊆ 允許清單；子庫與 rev5 樹 porcelain 空 |

- **model／effort**：review 家族（lens／mirror／grader／refuter／critic）與 fix 全 `opus[1m]`／`xhigh`＋`DEEP_THINK`；D 之 implementer 亦為 `opus[1m]`／`xhigh`（user 指示 2026-09-07：不改 tracked 骨架真源、只在發射前調整已組裝成品之 `IMPL_OPTS`）。
- **冒煙 token**：A `r2-explore-a7c1`／B1 `r2-verify-b1-5d2e`／B2 `r2-verify-b2-7a91`／C `r2-gap-c8b3`／D `r2-fix-gates-3e9b`；五支皆 launch 與看門狗 Monitor 同回合原子成對、完成即 TaskStop。
- **組裝**：一律 `python3 tools/orchestration/assemble.py <unitdef.py> <out.mjs>`（三道自檢：RULES-VERSION 對賬／`node --check`／harness）；A・B・C 過 harness-review 九案、D 過 harness-test 十五案×2。RULES-VERSION：A～C 與 D 之間因本輪改 RULES 而自 `741ae996dc61` 前進至 `89ec0586d6a9`，D 組裝時已吃新值。
- **存活規則**：兩鏡皆「確認」→confirmed；任一「駁回」→附錄 A；其餘→uncertain、主線親自重跑證據裁定。
- **主線復驗**：88 筆 confirmed 逐筆重跑證據命令——**零輸出 0 筆**（無失效證據）；6 筆非唯讀形已人工補驗、全數成立。
- **三指標張力**（同 r1 S9）：本輪為治理批，收單後「治理批對 feature 比」自 7.5 升至 8.0；設計張力、不改算式。

### §1 findings 總表（102 筆；confirmed 88／refuted 12／uncertain 2）

| ID | 來源 | 嚴重度 | 類別 | 檔 | 一句話 | 三態 | 處置 |
|---|---|---|---|---|---|---|---|
| L1-01 | A/B | maj | 生成器缺陷 | `tools/docsync/references.py` | gen_milestones 的 merge 欄對 field=adrs／probe 之 erratum 直接 str() 後截前 7 字，印出 Python 字面碎片 | confirmed | 修-D |
| L1-02 | A/B | maj | 生成器缺陷 | `docs/generated/MILESTONES.md` | 事件 summary 內未逸脫的 ASCII 管線符把 MILESTONES 表格列撐成 9 欄、與 7 欄表頭錯位 | confirmed | 修-D |
| L1-03 | A/B | maj | 事件無家 | `tools/docsync/adr.py` | gen_decisions_index 只自 feature_close／misc 的 adrs 欄反查來源，未讀 review 事件 findings.wontfix_adr，won't-fix ADR 因而 | confirmed | 修-D |
| L1-04 | A/B | maj | 生成器缺陷 | `tools/docsync/adr.py` | DECISIONS-INDEX feature 欄的查無 fallback 硬編「輕量軌」，把創世波次與獨立輪所立的八支 ADR 標成輕量軌來源 | confirmed | 修-D |
| L1-05 | A/B | maj | 事件無家 | `tools/docsync/events.py` | probe.avg_min_hops 受 GT-02 形檢卻無任何渲染面或指標消費＝欄無家 | confirmed | 修-D |
| L1-06 | A/B | maj | 閘覆蓋缺口 | `tools/docsync/events.py` | 事件 summary／reason 同樣全文進 MILESTONES 與 STATE 卻無 notes 那道真源側守衛，且不在 ERRATUM_FIELDS 內＝寫壞無補救 | confirmed | BL |
| L1-07 | A/B | maj | 閘覆蓋缺口 | `tools/docsync/events.py` | events.jsonl 宣稱 append 型單一事實源，但無任何閘比對 HEAD 版，既有列可被靜默改寫 | confirmed | BL |
| L1-11 | A/B | min | 生成器缺陷 | `tools/docsync/references.py` | STATE 最近事件三列以 [:80] 硬截斷、無省略記號，句子中斷且括號不成對 | confirmed | 修-D |
| L3-01 | A/B | blo | 權威鏈矛盾 | `tools/docsync/events.py` | GT-03 宣稱守 RL-0053，但 RL-0053 carrier=checklist 且其簿記三步序與牆鐘量法與 GT-03 實掃（引用存在性）零交集 | confirmed | 修-D |
| L3-02 | A/B | maj | 閘覆蓋缺口 | `tools/docsync/events.py` | GT-03 只驗 feature_close／review 的 ADR 引用，misc 事件 adrs 欄零存在性驗證，指向不存在 ADR 時 lint 全綠 | confirmed | BL |
| L3-04 | A/B | maj | 閘覆蓋缺口 | `tools/docsync/gates.py` | 閘 docstring 的 rule 欄與 RULES carrier 欄零機器對賬：carrier=lint 四條無任何閘指名、GT-03 指名的 RL-0053 carrier=checklist | confirmed | BL |
| L3-07 | A/B | min | 閘覆蓋缺口 | `tools/docsync/gates.py` | hooks_absent 分支以 startswith(".githooks")（缺尾斜線）連帶豁免 .githooks-submodule/* 的 EXEC_REQUIRED 檢查，與同筆 SKIP 訊息「其 | confirmed | 修-D |
| L3-08 | A/B | min | 生成器缺陷 | `tools/docsync/gates.py` | README 樹「、」多檔行在深度 0 時失去目錄前綴，BACKLOG-DEFERRED.md 與 LESSONS/ 被解析成根層路徑、後者還誤入 leaf_dirs 覆蓋集 | confirmed | 修-D |
| L3-09 | A/B | min | 閘覆蓋缺口 | `tools/docsync/events.py` | review.report 只驗 endswith(".md")，錯誤訊息卻宣稱形制為 docs/reviews/YYYYMMDD-<scope>.md，任意路徑 .md 皆過 | confirmed | 修-D |
| L3-10 | A/B | min | 生成器缺陷 | `tools/docsync/references.py` | compute_generated 以 except ImportError: pass 吞掉 gates 匯入失敗，GATES.md 會靜默退出 GT-01 的計算面而 check 仍報零漂移 | confirmed | 修-D |
| L4-06 | A/B | maj | 其他 | `tools/docsync/__main__.py` | docsync 入口 docstring 自稱「七子命令」且未列 vendored-check，與同檔 build_parser 註冊的八支不符 | confirmed | 修-主線 |
| L4-08 | A/B | min | 生成器缺陷 | `tools/docsync/references.py` | agents.md 生成器在零命中時輸出全破折號佔位列而非「目前無」句，且 *_OPTS 字面形一改即靜默縮小掃描面、無空集合警示 | confirmed | 修-D |
| L5-02 | A/B | maj | 閘覆蓋缺口 | `tools/docsync/book.py` | GT-05 的 BARE_REV5 正則只認完整刀名 slug、不認裸三碼刀號，故 R1-066 同型復發時 lint 全綠、零機器腿 | confirmed | 修-D |
| L5-04 | A/B | maj | 權威鏈矛盾 | `tools/docsync/snapshot.py` | archetype-map 缺表歸屬的 fail-loud 補救訊息寫「先補 data-model §1」，與 RUNBOOK §10 明寫的 schema-definition.md §1 矛盾、會把操作者導 | confirmed | 修-主線 |
| L1-09 | A/B | min | 檢索性 | `README.md` | README 與 12-glossary 都稱 events 的人讀面只有 MILESTONES 與 reference/perf，漏 STATE 與 DECISIONS-INDEX 兩個實際消費面 | confirmed | 修-主線 |
| L1-10 | A/B | min | 生成器缺陷 | `docs/generated/STATE.md` | 治理指標表只有值與自由文字目標、無狀態欄，且只渲染最近一筆 probe，ADR-00021 的「輪間不降」目標在帳面上不可判 | confirmed | 修-D |
| L4-09 | A/B | min | 權威鏈矛盾 | `docs/generated/reference/agents.md` | agents.md 同時列出骨架與已組裝成品兩份 *_OPTS 複本，與 tools/orchestration/README.md「模型家單一真源＝_sk_head.js」之宣稱相牴觸 | confirmed | 修-主線 |
| L2-01 | A/B | maj | 權威鏈矛盾 | `README.md` | README 文件地圖把 RULES 上限的權威指向已 superseded 的 ADR-00004，未指現行 ADR-00011 | confirmed | 修-主線 |
| L4-05 | A/B | maj | 檢索性 | `README.md` | README 操作快速入口列七支 docsync 子命令、漏 vendored-check，與實際八支子命令不符 | confirmed | 修-主線 |
| L4-07 | A/B | min | 檢索性 | `README.md` | README 對 bootstrap.sh 的步驟列舉漏「例外①自證」，與 CLAUDE.md §3 及 bootstrap.sh 自身完成行不一致 | uncertain | — |
| L7-04 | A/B | maj | 檢索性 | `README.md` | README 文件系統地圖樹缺 docs/ops/reference-src/ 一列，而同檔查詢表兩列以它為真源 | confirmed | 修-主線 |
| L7-06 | A/B | min | 檢索性 | `README.md` | README 查詢表無碼面閘列——「哪些規則、誰守」導向的 GATES.md 依 ADR-00016 不收碼面閘，讀者在查詢面到不了 RUNBOOK §12 碼面閘表 | confirmed | 修-主線 |
| L7-07 | A/B | min | 檢索性 | `README.md` | README 讀序與查詢表皆無 LESSONS（踩過的坑）與 BACKLOG（待辦）兩本 ops 帳本的入口列 | confirmed | 修-主線 |
| L6-02 | A/B | maj | 工作流失效 | `CLAUDE.md` | CLAUDE.md 兩處 generate 後的 git add 清單漏 GENERATED_FILES 成員 tools/orchestration/_sk_rules.js | confirmed | 修-主線 |
| L9a-03 | A/B | maj | 權威鏈矛盾 | `CLAUDE.md` | §4 宣告「細則全在 docs/ops/RULES.md（RL-0047～RL-0055）」，但同節逐條引用的 RL 有四條落在該範圍外（RL-0001／RL-0020／RL-0046），且 ADR 條之真源為 | confirmed | 修-主線 |
| L7-11 | A/B | min | 其他 | `CLAUDE.md` | 單一禁令條目 397 字塞入三件互不相干的禁令（手改生成物／spec-kit 技能白名單與六支不叫用理由／specify 不進 brainstorm） | refuted | — |
| L9a-01 | A/B | maj | 權威鏈矛盾 | `CLAUDE.md` | §4 稱 ops 帳本寫「本刀 U2」形，與 RL-0020 ★ 句（BACKLOG／LESSONS 須寫刀名形「001 刀 U2」、「本刀」只限該刀分支內 tasks／NOTES／commit 訊息）相反 | confirmed | 修-主線 |
| L9a-04 | A/B | maj | 時態鏡像 | `CLAUDE.md` | 五處基線／凍結 SHA 字面（8be6f9ba／32c5254／7eab28a／9833308／92919b9）是 tools/bootstrap.sh 常數的手寫鏡像，無任何腿對賬 CLAUDE.md 這一份 | confirmed | 修-D |
| L9a-05 | A/B | min | 權威鏈矛盾 | `CLAUDE.md` | review 形範本以 glob `tools/orchestration/EXAMPLE-review-*-unitdef.py` 指路，該樣式只匹配兩支範本中的 verify 一支、漏掉 explore 範 | confirmed | 修-主線 |
| L9a-06 | A/B | min | 權威鏈矛盾 | `CLAUDE.md` | 同檔對 `git submodule update` 同時下絕對禁令與具名例外，兩處互不指涉、例外的限定條件（--init 且無既有 worktree）未寫在禁令側 | confirmed | 修-主線 |
| L9a-07 | A/B | min | 權威鏈矛盾 | `CLAUDE.md` | CLAUDE.md 宣告 `[Spec Kit]` 英文固定訊息為「RL-0042 zh-TW 之具名例外」，但 RL-0042 條文無例外款、ADR-00003 亦未以該名承載，例外只住權威鏈低於 RULES | confirmed | 修-主線 |
| L10-05 | A/B | min | 規則承載缺口 | `CLAUDE.md` | §6 的 spec-kit 名冊只點名 11 支（五支白名單＋六支禁用），speckit-git-remote 與 speckit-git-validate 兩支在全 repo 治理文件零處置 | refuted | — |
| L10-06 | A/B | min | 工作流失效 | `CLAUDE.md` | speckit-specify 內建的 NEEDS CLARIFICATION 提問形是一次呈上最多三題，與 CLAUDE.md §5「一題一問」相衝且無具名例外 | confirmed | 修-主線 |
| L10-07 | A/B | min | 工作流失效 | `CLAUDE.md` | spec-kit auto-commit 以 git add . 掃全樹，§2 未載「每步起手前工作樹須乾淨」前提，實際已產生訊息與內容不符的 commit | refuted | — |
| L1-08 | A/B | maj | 規則承載缺口 | `docs/ops/RUNBOOK.md` | erratum 更正機制在現在式面無程序家，且「勘誤」一詞已被 docsync errata 佔滿、檢索必然落錯 | confirmed | 修-主線 |
| L2-03 | A/B | maj | 規則承載缺口 | `docs/ops/RULES.md` | RL-0011 的枚舉義務 scope 不含「主線」，而 LESSONS 三筆再犯的行為主體全是主線，其四形掃描種子只住 LESSONS 檔、無 prompt 面亦無閘面承載 | confirmed | 修-主線 |
| L2-04 | A/B | maj | 規則承載缺口 | `docs/ops/RULES.md` | RL-0015 標 carrier=lint 但閘只掃其同義集五詞中的三詞且僅 WARN，「隨…刀進場／尚無…」兩形零覆蓋、活書 11 處命中而 lint 全綠 | confirmed | BL |
| L2-05 | A/B | maj | 權威鏈矛盾 | `.specify/memory/constitution.md` | 憲法 §I.5 例外①列名的 `xdb` 工具性 crate 在 rev5 凍結樹與 rev6 皆不存在，自證腿 vendored-check 只涵蓋 sea-orm-adapter | refuted | — |
| L2-06 | A/B | maj | 規則承載缺口 | `.specify/memory/constitution.md` | 憲法 §I.5「註解一律重寫、不拷前代註解」對例外①無豁免條款，實況 63 行註解中 50 行與 rev5 逐字同文、自證腿刻意剝註解不判 | confirmed | ADR |
| L2-07 | A/B | min | 活書事實 | `docs/process/P-E7-agent-debt.md` | P-E7 對 RL-0011／RL-0014 兩列標「已守」，與 002 刀後 LESSONS 三筆再犯記錄相矛盾，且該表「次個編排刀收刀」覆審條件未兌現 | confirmed | 修-主線 |
| L2-08 | A/B | min | 規則承載缺口 | `docs/ops/RULES.md` | RL-0030 標 carrier=checklist、scope 含主線，卻是全 74 條中唯一在 RULES.md 以外的現在式面零引用、零對應句者 | refuted | — |
| L3-03 | A/B | maj | 閘覆蓋缺口 | `docs/ops/RULES.md` | RL-0051「每條閘一正一反自證」與「變異要打在判準上」carrier=lint 卻無任何閘或測試實作，12 閘的正反測試存在性只靠人工枚舉 | confirmed | BL |
| L2-02 | A/B | maj | 權威鏈矛盾 | `docs/ops/reference-src/schema-definition.md` | 跨刀活體定稿檔頭仍寫「ADR 待立」，而承載該二分的 ADR-00012 已 accepted | confirmed | 修-主線 |
| L7-02 | A/B | maj | 時態鏡像 | `docs/ops/NOTES.md` | NOTES 下一步段前兩點是 001／002 feature_close 事件的逐項重述（merge SHA、ADR 清單、backlog_done、交付清冊），與 events／MILESTONES 同筆重複 | confirmed | 修-主線 |
| L7-03 | A/B | maj | 時態鏡像 | `docs/ops/RUNBOOK.md` | RUNBOOK 檔頭的章節現況名冊漏 §4 與 §12b（皆已補實文）與 §9c（指針章），且同一事實同時住 RUNBOOK 與 README 兩處人寫檔 | confirmed | 修-主線 |
| L9b-01 | A/B | maj | rev5拷貝失效 | `.specify/memory/constitution.md` | §III 生成檔紀律引用「§III.2 表內『路由外掛產物四檔』」，但 §III.2 為空表、全 repo 僅此一處提及該詞＝失效引用 | confirmed | ADR |
| L9b-02 | A/B | maj | 權威鏈矛盾 | `.specify/memory/constitution.md` | 憲法 §I.5 之 rev5 凍結 SHA 為鏡像值，下游改值程序三處各式且皆漏憲法 §V.2 Amendment，bootstrap die 訊息更指向史料面啟動書與 accepted ADR body | confirmed | 修-主線 |
| L9b-03 | A/B | maj | 權威鏈矛盾 | `.specify/memory/constitution.md` | 憲法兩處載基線 SHA `8be6f9ba` 為鏡像值，但前進程序（CLAUDE.md §3、bootstrap die）只寫「先立 ADR 再改 bootstrap 基線 SHA」、漏憲法 Amendment | confirmed | 修-主線 |
| L9b-05 | A/B | min | 權威鏈矛盾 | `.specify/memory/constitution.md` | 憲法列舉之 wire 唯一權威面為 `typings/api/*.d.ts` 等四項，契約裁判快照的抽取面 TYPINGS_GLOB 却另含非 wire 的 `src/typings/common.d.ts` | refuted | — |
| L10-04 | A/B | min | 規則承載缺口 | `specs/002-system-settings/checklists/requirements.md` | /speckit-specify 產出的 checklists/requirements.md 通篇英文檢核項，RL-0042 與 CLAUDE.md 皆未列它為 zh-TW 之具名例外 | confirmed | ADR |
| L11-01 | A/B | maj | 權威鏈矛盾 | `docs/ops/RUNBOOK.md` | RUNBOOK 碼面閘表 msg key 註記列的守備方向寫成雙向「⇔」，與 ADR-00017 決定 3、arc42 08、BL-00030 一致採用的單向「⊆」相反 | confirmed | 修-主線 |
| L11-05 | A/B | min | 活書事實 | `docs/ops/RUNBOOK.md` | 碼面閘表表頭定義「根據 ADR」欄＝該閘之 rev6 ADR 序號（accepted），但 fork-delta-lint 列填的是憲法節與 research 條目、無 ADR 序號 | confirmed | 修-主線 |
| L11-08 | A/B | min | 活書事實 | `docs/ops/RUNBOOK.md` | 工具鏈速查表 wf-watchdog 列未列 test 子命令，而 pre-commit 自測迴圈與 bootstrap 名冊都以 test 呼叫它 | confirmed | 修-主線 |
| L3-06 | A/B | maj | 閘覆蓋缺口 | `tools/bootstrap.sh` | bootstrap.sh 的呼叫名冊（docsync 三段／閘數斷言／九支 run_tool_test／vendored-check）零機器守衛，刪任一行不紅 | confirmed | BL |
| L5-01 | A/B | maj | rev5拷貝失效 | `rust-api/server/src/model/facade/test_kit.rs` | 裸前代刀號「rev5 002」「rev5 001」五處未用 RL-0046 的 `rev5:` 冒號前綴形（R1-066 已判同型、修後復發） | confirmed | 修-主線＋BL |
| L5-03 | A/B | maj | rev5拷貝失效 | `tools/schema-gate.py` | 隨遷工具 schema-gate.py 註解仍以「data-model §N」稱其左源，但 ADR-00012 已把 DATA_MODEL 改指 schema-definition.md、其中「data-mod | confirmed | 修-主線 |
| L5-05 | A/B | min | rev5拷貝失效 | `tools/orchestration/EXAMPLE-dual-implementer.mjs` | 範例把 `002-system-settings` 舉為「rev5 刀名、不可裸寫」，但該名已是 rev6 自家刀名並落在 GT-05 的 rev6 刀集豁免內 | refuted | — |
| L6-01 | A/B | maj | 工作流失效 | `tools/rust-fmt-gate.py` | rust-fmt-gate 檔頭仍宣稱 pre-commit 條件段接線「無機器守衛」並以已收掉的 BL-00023 為單一承載處 | confirmed | 修-主線 |
| L6-03 | A/B | maj | 工作流失效 | `tools/orchestration/EXAMPLE-review-unitdef.py` | 兩支 review 範本的 DECISIONS_BLOCK 把已收掉的 BL-00007 當現行 BACKLOG 條目指路 | confirmed | 修-主線 |
| L6-04 | A/B | maj | 權威鏈矛盾 | `docs/process/P-E2-agent-registry.md` | P-E2 探針列仍寫「檢索性指標候選＝BL-00007」，與已 accepted 的 ADR-00021 及 BL-00007 已收相矛盾 | confirmed | 修-主線 |
| L6-07 | A/B | min | 規則承載缺口 | `tools/orchestration/_sk_head.js` | TDD 形骨架首段未對 _vars 之 UNIT／FEATURE／START_LOG／CONTEXT／ALLOWED_BLOCK 做型別＋非空斷言，僅 review 形有 | confirmed | BL |
| L11-06 | A/B | maj | 規則承載缺口 | `tools/orchestration/EXAMPLE-dual-implementer.mjs` | 入庫的組裝成品範例內嵌三份過期 RULES 塊（RULES-VERSION 064380371fc0 vs 現算 741ae996dc61），是現在式面零閘的可漂移規則鏡像 | refuted | — |
| L7-12 | A/B | min | 時態鏡像 | `deploy/decrypt-secrets.py` | 兩處以「舊檔 :195-220」行號區間引用 rev6 不存在的 bash 舊版工具，屬 RL-0048 禁的行號形跨檔引用兼隨遷工具四型失效引用 | confirmed | 修-主線 |
| L8-01 | A/B | maj | 活書事實 | `docs/c4/C4-E2-data-lineage-overlay.md` | C4-E2 資料源清冊稱三項系統資料源「皆列於 C4-L2 表」，但「compose 設定檔（deploy/）」不在 C4-L2 表 17 列任一列 | confirmed | 修-主線 |
| L7-01 | A/B | maj | 時態鏡像 | `docs/arc42/04-solution-strategy.md` | 活書三處對「契約守恆」的守門陳述互相矛盾：§10.1 已 as-built 指名 tools/wire-schema.py，arc42 04 兩處與 01 §1.2 仍寫「隨 wire 地基刀落地／碼面閘隨 w | confirmed | 修-主線 |
| L8-04 | A/B | min | 活書事實 | `docs/arc42/05-building-block-view.md` | server crate 20 支實檔中 model/facade/test_kit.rs 在活書家族零提及且無「設計上不列測試工具」說明 | confirmed | 修-主線 |
| L8-05 | A/B | min | 活書事實 | `docs/arc42/06-runtime-view.md` | §6.1 情境格式規定參與者節點名＝C4-L2 表首欄字面，但同欄允許的「模組」與 prod「外部系統」皆不在該表 | confirmed | 修-主線 |
| L8-06 | A/B | min | 活書事實 | `docs/arc42/05-building-block-view.md` | §5.1 deploy/ 區塊「內含」欄逐項列名卻漏列兩支 Dockerfile 與八支機密／維運 CLI | confirmed | 修-主線 |
| L9b-04 | A/B | maj | 活書事實 | `docs/arc42/05-building-block-view.md` | 活書 05 把憲法 §II #2 拍板值 dynamic 寫成 base-web as-built，實際 `base-web/.env` 為 static、翻 dynamic 明載延至 003 | confirmed | 修-主線 |
| L11-03 | A/B | maj | 權威鏈矛盾 | `rust-api/server/tests/contract.rs` | contract.rs 檔頭自述保留碼零發出「本檔不重寫第三份」，與憲法 §I.3「4 保留碼…contract test 斷言後端從不發出」相反且無 Amendment／ADR 授權 | confirmed | ADR |
| L11-04 | A/B | maj | 權威鏈矛盾 | `tools/bootstrap.sh` | bootstrap 閘數斷言硬編字面 12 且不符即 die，與 ADR-00011 決定 2「閘數上限一律 WARN、不擋」相反，且同段註解自述「不落字面」 | confirmed | 修-主線 |
| L11-07 | A/B | maj | 閘覆蓋缺口 | `.githooks/pre-commit` | wire-schema 閘只在 base-web pin bump 觸發，快照側（rust-api pin bump 或快照本身 staged）無觸發腿，與 entity-drift 的雙側觸發不對稱 | confirmed | BL |
| P1-P1 | probe | min | 權威鏈矛盾 | `README.md` | README 入口表以已 superseded 的 ADR-00004 為 RULES 上限的權威，與 RULES.md 檔頭現行的 ADR-00011 相矛盾 | confirmed | 修-主線 |
| P1-P2 | probe | min | 規則承載缺口 | `docs/ops/RULES.md` | GT-08 機器強制的「規則句 ≤2 行」在現在式面無家，唯一載處是已 superseded 的 ADR-00004 與史料面啟動書 | confirmed | 修-主線 |
| P1-P3 | probe | min | 檢索性 | `docs/ops/RUNBOOK.md` | RUNBOOK 章節現況名冊兩處皆未列已補實文的 §12b，讀者依名冊會把它歸入「其餘隨刀補實」 | confirmed | 修-主線 |
| P3-P1 | probe | min | 其他 | `docs/ops/events.jsonl` | 000-r1 review 事件 notes 的分流計數自相矛盾：稱 confirmed 86 卻列出修 75／BL 9／ADR 1／none 2（相加 87），且與報告 §5 的「修 74」不一致（報告主表實 | confirmed | BL |
| P3-P2 | probe | min | 檢索性 | `.specify/memory/constitution.md` | 基線 SHA 8be6f9ba 的「為什麼」在現在式面無家：四處現在式面只帶值＋「啟動書 D14」指針，理由句只存於史料面 brainstorm，冷啟動要答「為什麼是它」必須翻史料 | refuted | — |
| P3-P3 | probe | min | 規則承載缺口 | `docs/ops/RULES.md` | RL-0073 承載處二分與名詞段「獨立輪」定義未涵蓋既有第三類 review 事件——附屬某刀而落報告＋事件的臨時對照輪；其判別實際由 review 事件 optional feature 欄承擔但無規則記載 | confirmed | 修-主線 |
| P3-P4 | probe | min | 檢索性 | `docs/ops/RUNBOOK.md` | 「Day-1」在治理面為同名不同物（閘的 Day-1 豁免 vs migration 刀的 Day-1 登記紀律），RUNBOOK 同一檔內兩義並存且名詞段兩者皆未定義，冷啟動 grep 必混讀 | confirmed | 修-主線 |
| P4-P1 | probe | min | 工作流失效 | `CLAUDE.md` | CLAUDE.md §2 分支序號規則只寫「既有 NNN- 分支與 specs/ 目錄最大號＋1」，未載實碼在 hook 實際呼叫路徑會先跑 `git fetch --all --prune` 並把遠端分支計入 | confirmed | 修-主線 |
| P4-P2 | probe | min | 檢索性 | `docs/ops/NOTES.md` | 開刀入口鏈（README「我要開新刀」→NOTES 下一步→CLAUDE.md §2 階段 0）對「觸發已到的 BACKLOG 條目」零指針：NOTES 003 行窮舉狀列了 .env 兩件卻未點名觸發明寫 0 | confirmed | 修-主線 |
| P5-P1 | probe | maj | 工作流失效 | `tools/orchestration/_sk_review.js` | 探針 hops 口徑未明示「ls／find／grep／git log 等機器反證不計」，使應查無題的自報跳數系統性膨脹、≤3 跳比例輪間不可比（本輪 P5：自報口徑 1/7 vs 開檔口徑 6/7） | confirmed | BL |
| P5-P2 | probe | maj | 工作流失效 | `docs/brainstorms/000-r2-doc-governance.md` | 探針題庫連同「真相（grader 用）」答案欄住 tracked 檔，冷啟動探針以題目關鍵詞常規 grep 即命中，ADR-00021 檢索性指標的冷啟動前提無隔離保護 | confirmed | BL |
| P5-P3 | probe | min | 閘覆蓋缺口 | `docs/ops/RUNBOOK.md` | 憲法 §I.5 例外①字面涵蓋 sea-orm-adapter 與 xdb 兩支 crate，自證腿射程只含前者，現在式面無一句交代 xdb 面（兩樹皆零實例、進場時須擴射程） | confirmed | 修-主線 |
| P6-P1 | probe | min | 檢索性 | `docs/ops/RUNBOOK.md` | 憲法 §I.5 例外②的「五檔非拷貝」邊界定性句只住 RUNBOOK §10，憲法／ADR-00009／活書 05 皆無前向指針，自憲法或 ADR 進場的稽核者查無此界線 | refuted | — |
| C1-1 | C | maj | 閘覆蓋缺口 | `tools/docsync/tests/test_hook_wiring.py` | 憲法 §I.8 並列為機器閘的 pre-push 面（兩支 pre-push hook＋共用 lib scan-range.sh）接線零機器守衛，接線守只覆蓋 pre-commit | confirmed | BL |
| C1-2 | C | maj | 權威鏈矛盾 | `docs/ops/RUNBOOK.md` | 工具鏈速查表把 schema-gate doccheck 的左源寫作 data-model，而 ADR-00012 已把該左源改指 docs/ops/reference-src/schema-definitio | confirmed | 修-主線 |
| C1-3 | C | maj | 規則承載缺口 | `docs/ops/RUNBOOK.md` | 跨刀常設的 Day-1 三步與演進登記檔形制契約仍住 specs/001 史料面，與 ADR-00012 為同型缺陷所立的「跨刀活體不住 spec 目錄」判準相牴觸 | uncertain | — |
| C1-4 | C | maj | 閘覆蓋缺口 | `docs/ops/reference-src/accounts-snapshot.json` | accounts-snapshot.json 是 fixtures/seed.sql 與實庫之外的第三份帳號鏡像，除餵 reference/accounts.md 外零機器對賬腿 | confirmed | BL |
| C1-5 | C | maj | 活書事實 | `docs/process/P-E6-quality-scenarios.md` | 「規則烤入一致性」的現況欄答「全數 script 帶版本字面」而非量測欄定義的「與現算版本相符」，repo 內唯一帶規則塊的入庫 script 其版本字面實為過期 | confirmed | 修-主線 |
| C2-1 | C | maj | 權威鏈矛盾 | `CLAUDE.md` | §4「ID 配號」把 LL 與 BL／RL 併列為「取檔頭 next 後 bump」，但 LL 的 next-id 住機器生成的 LESSONS.md、由 generate 自檔集最大號＋1 推導、人手不得 b | refuted | — |
| C2-2 | C | min | 時態鏡像 | `CLAUDE.md` | §5 末列括註「本波兩次靠實跑抓到問題」是寫於波 1 末的波束史述，現在波已 bump 至 6，「本波」指涉失真且無回填機制 | confirmed | 修-主線 |
| C2-3 | C | min | 權威鏈矛盾 | `.specify/memory/constitution.md` | 憲法三處以「隨首刀」為時點的進場預告在首刀 001 與 002 皆收刀後仍未兌現（憲法零 Amendment），且與 §II 排程性拍板註記「排程性結論不預載於本檔」相矛盾 | refuted | — |
| C3-1 | C | maj | 事件無家 | `docs/ops/events.jsonl` | 同一根因（misc.adrs 欄 2026-09-05 才上線）造成九筆 ADR 結構欄漏記，事件源只為 ADR-00011 補了一筆 erratum、ADR-00001～00007 七筆未補，更正政策自相不一 | confirmed | BL |
| C3-2 | C | maj | 檢索性 | `docs/ops/events.jsonl` | 縮寫 ID 形（`X-NNNNN/NNNNN`、`X-NNNN／NNNN`）使 ID 全字 grep 枚舉漏抓，現有五處真漏（ADR-00002／GT-07／RL-0044／RL-0012／BL-00010）， | confirmed | 修-D |
| C3-3 | C | maj | 閘覆蓋缺口 | `tools/docsync/events.py` | 「ADR 誕生必帶事件」不是不變式——misc.adrs 為 optional 且 gt_03 只走前向存在性，與本輪 Q14 為 BL 建立的 events-only 反向存在性不變式不同形，同形套用到 AD | confirmed | ADR |
| C3-4 | C | min | 生成器缺陷 | `tools/docsync/events.py` | `RE_LID`（LL-NNNNN 形檢正則）自 319ae30 誕生起全 repo 零消費者，是意圖中的 LL↔事件欄關聯從未落地的死常數 | confirmed | 修-D |

分流彙總： {'修-D': 17, 'BL': 15, '修-主線': 50, 'ADR': 5, '修-主線＋BL': 1}

## 2. 事件×家矩陣重算（L1）

r1 G2 矩陣以 r1 後新型實例重算：`feature_close` ×2、`erratum` ×2（含 `field=probe` 回填 000-r1）、`misc.adrs`／`misc.workflow`、`review.probe`（ADR-00021）、`perf` 之 `close_bookkeeping`／`precommit_chain` 皆有實例，五型全型覆蓋（r1 critic 第(6)條缺口就此消化）。欄級「無家」本輪剩一筆＝`probe.avg_min_hops`（受 GT-02 形檢為必填、卻零渲染面），已於 D 修單補上渲染面（`_probe_retrieval`→`_probe_row`）。erratum 更正視圖對 STATE／MILESTONES／DECISIONS-INDEX／perf 四面之套用經實測成立；但其**程序**在現在式面原本無家，本輪新增 `docs/ops/RUNBOOK.md` §12c 承載，並明寫與 `docsync errata`（RL-0001 跨檔假述枚舉）不是同一件事。

## 3. 探針結果與檢索性第四指標（ADR-00021）

### 3.1 核心 25 題（P1～P4；grader 獨立判定）

| 判定 | 題數 |
|---|---|
| 找得到（≤3 跳且答對） | 19 |
| 繞路（>3 跳但答對） | 6 |
| 找不到 | 0 |
| 答錯 | 0 |

`avg_min_hops`（grader 最短路徑平均）＝1.68。

### 3.2 否定對照 7 題（P5；5 應查無＋2 對照可答）

找得到 6／繞路 1／找不到 0／**答錯 0**；`avg_min_hops` 2.29。五題應查無（003 spec／zh-tw 字典／sys_token 實作／憲法例外③／m0003）皆正確判為查無並指出最近相關真源；兩題對照可答（002 範圍拍板／例外① 自證跑法）皆答對。

### 3.3 新面 8 題（P6；只入報告、不入 `probe` 欄）

找得到 3／繞路 5／找不到 0／答錯 0；`avg_min_hops` 1.12。繞路集中在「碼面閘三支怎麼自測」「fix 清單外升級為何不終止 run」「entity 唯一存取管道由哪支測試守」三類——皆為 002 刀後新面，入口尚未進 README 查詢表（本輪已補碼面閘一列）。

### 3.4 ★輪間比較（第四指標首次可比）

| 口徑 | r1（000-r1） | r2（000-r2） | 判 |
|---|---|---|---|
| 全 25 題（`probe` 欄值口徑） | ≤3 跳比例 **0.48**／答對率 1.0／hops 2.0 | ≤3 跳比例 **0.76**／答對率 1.0／hops 1.68 | 升 |
| 可比子集 20 題（排除下述五題） | ≤3 跳比例 **0.45** | ≤3 跳比例 **0.70** | 升 |
| 不可比 5 題 | 0.60 | 1.00 | — |

ADR-00021 兩個目標皆達成：「找不到＋答錯＝0」✅；「≤3 跳比例輪間不降」✅（**兩種口徑同向**）。

### 3.5 題文可比性偏差（揭露）

計畫附錄 C 對 #7／#8／#9／#14／#15 採「回退 r1 計畫 §5 原文」，但 r1 **實問文**是報告 §3 表的完整版（該五題在報告表截於 45 字）。主線逐字比對三源實測：**非截斷的 10 題三源逐字全同**，受影響者恰為該五題；其中 #15 的 r1 版多一個子問（「該節是實文（嗎）」），r2 版刪去該子問＝嚴格較易。故 §3.4 同列兩種口徑，結論在兩者下皆成立。**處置**：附錄 C 的五題題文改以 r1 實問版為真源（本輪同批改），r3 起即完全可比。另 B2 完整性 critic 指「十題非截斷者中有八題三源不同」一節，經主線實測**不成立**，已在此更正。

### 3.6 探針方法論的兩處污染揭露（轉 BL-00039／BL-00040）

①探針 hops 口徑未明示「`ls`／`find`／`grep`／`git log` 等存在性反證不計入」，使應查無題的自報跳數系統性膨脹（本輪 P5：自報口徑 1/7 在 ≤3 跳內 vs 開檔口徑 6/7）；`probe` 欄採 grader 開檔口徑，與 r1 基準同源。②否定對照題庫連同「真相（grader 用）」答案欄住 tracked 計畫檔，冷啟動探針以題目關鍵詞常規 grep 即可命中，ADR-00021 的冷啟動前提無隔離保護；r3 起真相欄改烤進 grader prompt、不落 tracked。

## 4. 活書 as-built 對賬（L8／L11）

- arc42 01 §1.2 與 04 兩處的「契約守恆」守門欄仍寫「隨 wire 地基刀落地」，而 §10.1 已 as-built 指名 `tools/wire-schema.py`；三處已對齊。
- 活書 05 把憲法 §II #2 的**拍板值** `dynamic` 寫成 base-web as-built，實際 `.env` 為 `static`、翻 dynamic 明載延至 003；已改為 as-built＋拍板指針二段式。
- 活書 05 §5.2 對 `model/facade/test_kit.rs` 零提及且無排除說明；已補共用測試件一句。§5.1 `deploy/` 列漏兩支 Dockerfile 與八支機密／維運 CLI；已補。
- arc42 06 §6.1 情境格式規定參與者節點名＝C4-L2 表首欄，但同欄允許的「模組」與 prod「外部系統」皆不在該表；已按類收窄為三類各指其表。
- C4-E2 資料源清冊稱三項系統資料源「皆列於 C4-L2 表」，而 `deploy/` compose 設定檔不在該表 17 列；已拆兩段事實。
- RUNBOOK §12 碼面閘表 msg key 註記列方向寫成雙向 `⇔`，與 ADR-00017 決定 3／arc42 08／BL-00030 一致採用的單向 `⊆` 相反（雙向會使前端字典側恆紅）；已改。

## 5. 分流彙總

| 去向 | 數 | 落地處 |
|---|---|---|
| 修（主線直改） | 51 | `739354a`（README 7＋CLAUDE.md 9）／`b2e5b75`（RUNBOOK 9＋活書 8＋process 3＋NOTES 2＋其餘）／`c3effa6`（工具檔文字面 7） |
| 修（D 修單 run） | 17 | `598b806`（含 BL-00003 三腿；docsync test 178 → 249 案） |
| BL | 15 | `979c046`：BL-00035～00042 八條（19 筆 findings 依 r1 Q11 同類合併；含 uncertain C1-3 之主線裁定） |
| ADR | 5 | `2b4d3f6`（ADR-00022／00023／00024＋憲法 1.1.0→1.2.0）／`4f7c8b1`（ADR-00025 won't-fix） |
| refuted | 12 | 附錄 A |
| uncertain | 2 | L4-07 主線裁定成立→併入修；C1-3 主線裁定→BL-00042 |

★BL-00003（閘補腿群三腿）三腿全數落地、收單時刪列。BACKLOG 開放 8 → 16 → 收單後 15（淨 +7）。

## 6. 主張×閘×真源矩陣（BL-00003③；停點① 拍板「補既有閘腿、不占閘數」）

- **射程**：`CLAUDE.md` 全檔（L9a、87 列）與 `.specify/memory/constitution.md` §I～§V（L9b、44 列），加 C2 補掃的中文數詞主張增量。★`docs/ops/RULES.md`／`RUNBOOK.md`／`README.md` 的**條級**主張不在射程（BL-00003③ 既定邊界），故「說有閘守是否真守」的答案只涵蓋四本現在式權威檔中的兩本。
- **判定分佈**（L9a）：一致有閘 29／一致有腿 7／一致無閘 37／鏡像含可漂移值 3／指針無值 3。
- **無閘清單最要緊三群**：①五處基線／凍結 SHA 字面是 `tools/bootstrap.sh` 常數的手寫鏡像 ②三個上限 `≤3`／`≤20`／`≤24` 對骨架常數零測試釘 ③三十餘處 `RL`／`GT`／`ADR` 引用的**存在性**零閘（GT-05 原只判「有無帶前綴」）。
- **獨家清單 10 條**（`CLAUDE.md` 以外無家）：六步序全序、唯三種停下情形、`git submodule status` 行首「-」屬正常、短名／長名分工、SDD 五步技能名單與六支不叫用名單、分支序號算法、implement 之具體副作用、`git add` 命令字面、一題一問問法紀律、CDP 三方比流程。
- **拍板與落地**：user 停點① 裁定①「補既有閘腿、不占閘數」；D 修單落地兩腿——GT-12 加「數值／SHA 主張 ⇄ 工具常數」腿（前兩群）、GT-05 加「ID 引用存在性」腿（第三群）。**閘數維持 12**。獨家 10 條為純敘述、無對賬面，本輪不設腿。

## 7. 憲法 Amendment（1.1.0 → 1.2.0）

三筆合一顆 commit（§V.2 步 4）、版本取最高級別 MINOR：①§I.5 例外① 射程補「含註解」（ADR-00022；實況 63 行註解中 50 行與 rev5 逐字同文，`vendored-check` 本就去註解比對，本次補的是凍結權威背書、工具行為零改動）②§I.3 四保留碼「從不發出」承載點自「contract test 斷言」改記為「型別層全變體窮舉＋`error.rs` 矩陣斷言雙錨」（ADR-00023；`contract.rs` 對該四碼零命中、實質守恆未失）③§III 生成檔紀律去除對空表 §III.2 的死引用（ADR-00024）。另立 ADR-00025（won't-fix）：ADR 方向不設「誕生必帶事件」反向不變式，理由＝ADR 的家是檔案本身、BL 完成即刪列故必帶事件；兩個同構 ID 家族刻意兩制。

## 附錄 A：被駁回 findings（12 筆）

| ID | 檔 | 一句話 | 駁回理由（R-decided 鏡） |
|---|---|---|---|
| L7-11 | `CLAUDE.md` | §6 單一禁令條目 397 字塞入三件互不相干的禁令 | 可讀性偏好、非缺陷 |
| L10-05 | `CLAUDE.md` | §6 spec-kit 名冊只點名 11 支、漏 git-remote／git-validate | 名冊射程為「主動叫用與明令不叫用」兩類，兩支皆非 |
| L10-07 | `CLAUDE.md` | §2 未載 auto-commit 前工作樹須乾淨之前提 | ADR-00003 已載機制與其掃全樹語意 |
| L2-05 | 憲法 | 例外① 列名之 `xdb` 在兩樹皆不存在、自證腿只涵蓋 sea-orm-adapter | 例外清單為授權面、非實存清單；已於 RUNBOOK §12 補射程定性句 |
| L2-08 | `docs/ops/RULES.md` | RL-0030 為全 74 條中唯一現在式面零引用者 | carrier=checklist 之條款不必然有引用面 |
| L9b-05 | 憲法 | §I.3 wire 權威面四項 vs `TYPINGS_GLOB` 另含 `common.d.ts` | 抽取面為實作細節、憲法列舉的是權威序 |
| L5-05 | `EXAMPLE-dual-implementer.mjs` | 把 `002-system-settings` 舉為「rev5 刀名、不可裸寫」 | 該名已落在 GT-05 的 rev6 刀集豁免內、範例語境仍成立 |
| L11-06 | `EXAMPLE-dual-implementer.mjs` | 內嵌三份過期 RULES 塊（064380371fc0 vs 現算） | 入庫成品範例＝組裝當日快照，為刻意的凍結參考品 |
| P3-P2 | 憲法 | 基線 SHA `8be6f9ba` 的「為什麼」在現在式面無家 | 四處現在式面帶值＋「啟動書 D14」指針，理由句住史料面屬設計 |
| P6-P1 | `docs/ops/RUNBOOK.md` | 例外② 五檔非拷貝之定性句只住 RUNBOOK §10 | 該落點正是 maint-backlog-21 之 user 拍板結果 |
| C2-1 | `CLAUDE.md` | §4 把 LL 與 BL／RL 併列為「取檔頭 next 後 bump」 | ADR-00005 後果段已就同一字面對 LL 明確裁定「仍為真」 |
| C2-3 | 憲法 | §I.7／§III.2 三處「隨首刀」預告在 001／002 收刀後未兌現 | 兩處明寫條件式進場（「隨**其刀**」「對應接線需求出現時」），非落在 001 的排程承諾 |

## 附錄 B：完整性 critic 缺口與處置（G8）

B2 之 critic 交回 5 缺口＋8 條未驗證主張。

| # | 缺口 | 處置 |
|---|---|---|
| GAP 1 | D 修單允許清單漏 `tools/docsync/rules.py`（Day-1 型八處之一住該檔）；計畫 §3 S2 之「book.py 4／gates.py 7」與 BACKLOG BL-00003② 之「七個」皆失準 | **主線實算更正**：全 repo `finding(SKIP, "GT-…")` 恰 11 處＝book.py 4／gates.py 5／events.py 1／rules.py 1；環境型 3、Day-1 型 8。允許清單已補、D run 因此未撞牆 |
| GAP 2 | 探針五題題文不可比 | **主線實算釐清**：見 §3.5（critic 之「非截斷八題亦不同」一節不成立）；兩口徑同列、附錄 C 題文改真源 |
| GAP 3 | 檔→事件反向缺席 {ADR-00001…8, 00011} 九筆超出 L10 豁免射程 | C3 lens 產出四筆 findings；形制問題由 **ADR-00025** 拍定（不設反向不變式）；生成面歸屬由 D 修單之 I 項處理 |
| GAP 4 | 範圍面 207 檔對 files_read 聯集差 27 檔零讀，9 檔在核心承載面 | C1 lens 全文讀該 9 檔，產出五筆 findings（pre-push 接線零守／doccheck 左源失準／contracts 跨刀活體／accounts-snapshot 零對賬／P-E6 現況欄失實） |
| GAP 5 | pre-scan 正則對中文數詞主張全盲（憲法 25 處、CLAUDE.md 4 處） | C2 lens 補掃，產出三筆（2 refuted、1 confirmed）＋主張候選增量表入 notes |

**8 條未驗證主張**中，第 6 條進本報告 §6（矩陣射程只涵蓋兩本權威檔）；第 7 條（r1 critic 第(3)條 infra 拷貝面殘量）本輪 §2 明列不入、未承接，留待日後獨立輪；其餘為 critic 自陳的資訊侷限。

### r1 critic 十條缺口對映（G8）

(1)(2) `.claude/skills`／`.specify/scripts` 未讀→**L10 已讀**；(3) infra 拷貝清冊→r1 C2 已收；(4) 拷貝射程無家→r1 收單名詞段「隨遷工具」已收；(5) 檔→事件反向→**L10＋C3 已做**；(6) 事件型別實資料 3/5→**本輪 5/5**；(7) 否定對照→r1 C4＋ADR-00021 已收；(8) 對照組→本輪 Q11 撤 P6、改由 L9 矩陣「CLAUDE.md 以外的家」欄靜態判；(9) 兩票分歧補證程序→維持 Q25 主線裁定（本輪 uncertain 僅 2 筆）；(10) 檔×閘覆蓋矩陣→**L3 notes 重算**。

## 附錄 C：未完成與已知侷限

- **矩陣射程**：只涵蓋 `CLAUDE.md` 與憲法兩本；RULES／RUNBOOK／README 的條級主張不在內（BL-00003③ 既定邊界）。
- **子庫面**：`rust-api` 兩處註解裸前代刀號（`test_kit.rs:2`、`handler/system_settings.rs:545`）屬 BL-00041，動子庫需 commit＋pin bump、超出本輪範圍；GT-05 裸三碼腿現只掃現在式面與 `tools/**`，子庫 pin 樹側（`SUB_SCAN`）待該刀併入。
- **GT-03 帳本側兩態**：號 ≤ max(誕生集) 判 ERROR、> max 判 WARN（在途落帳窗口）。本報告落筆時 8 筆 WARN（BL-00035～00042），收單事件補 `backlog_add` 後自動消失。
- **P 腿存量豁免**：`docs/generated/**` 整檔不掃；`docs/arc42/decisions/` 與 `docs/ops/events.jsonl` 以「該行逐字在 HEAD」為存量豁免（該三面共 8 處存量命中皆不可回頭改），新寫或改過的行照擋。
