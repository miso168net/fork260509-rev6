<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# MILESTONES — 事件表（新在前）——perf 型另居 reference/perf.md

| date | type | 標的 | summary | merge | adrs | arch |
|---|---|---|---|---|---|---|
| 2026-09-04 | misc | governance | 001 刀規格對照審查（獨立輪 spec-compliance-001）修單收單：schema-gate 自帶測試 103→118 案補回歸保護（audit 變體驗則面、gate1 索引與約束兩節、seed_add 欄集）、D 變體補 archived_by、pre-commit 加 schema-frozen 條件段、contracts/gates.md §4 negative 義務五類擴為六類。 | 39232de | — | — |
| 2026-09-04 | review | 001-schema-baseline | findings 8（修 6／BL 2／ADR 0）；BL-00020、BL-00021 | — | — | — |
| 2026-09-04 | misc | governance | 數量預算改為只警告不擋（ADR-00011 supersede ADR-00004）：BACKLOG 開放取消上限、改觀測值只報表；閘數 12 與 RULES 總／per-scope 上限保留數值但超限一律 WARN、不進 lint 退出碼、不擋 commit；pre-commit 硬擋機制不動。 | 1e0d89b | — | — |
| 2026-09-04 | feature_close｜horizontal | 001-schema-baseline | 001 schema 基線刀收單：rust-api workspace 三 crate＋m0001／m0002＋entity 15 檔逐位元承襲（憲法 §I.5 例外②）、sea-orm-adapter 例外①；schema 三閘＋entity 漂移閘隨遷並自證；凍結 fixtures 四件雙源互證；docsync refresh 照相＋兩張正典真表；pre-commit entity-drift 條件實跑段。 | d04a41c | ADR-00009、ADR-00010 | §5、§8、§11 |
| 2026-09-04 | misc | governance｜000-r1-doc-governance | rev6 獨立 review 輪 000-r1 文件治理架構體檢收單：四支唯讀 Workflow（探索 14／驗證 41／補漏 12）＋修單 run 8 支；confirmed 86＝修 75／BL 4 條／ADR-00008／none 2；報告 docs/reviews/20260904-doc-governance.md＋review 事件（total 80）；RULES 74（名詞段獨立輪／隨遷工具／其他面、RL-0074）、RULES-VERSION 064380371fc0；BACKLOG 開放 7；merge --no-ff 回 rev6-admin-root | 5459c9d | — | — |
| 2026-09-04 | review | doc-governance | findings 80（修 75／BL 4／ADR 1）；BL-00001、BL-00003、BL-00004、BL-00005、ADR-00008 | — | — | — |
| 2026-09-03 | misc | governance | rev6 波 5 文件創世驗收收單：DoD A 六條全勾（報告 docs/reviews/20260903-doc-genesis.md＋首筆 review 事件、§7 自評十三列：系統層全不適用、流程層 2×7／1×4）；GT-03 Day-1 豁免解除（gates.py 移鍵、零 close 事件改 ERROR、Day-1 餘 GT-08 一筆）；tmp 交接包與憲法 diff 已清；外層 origin 已設；波標記 6＝文件創世收官、波 6 起為刀；merge --no-ff 回 rev6-admin-root | 5bae24c | — | — |
| 2026-09-03 | review | doc-genesis | findings 0（修 0／BL 0／ADR 0） | — | — | — |
| 2026-09-03 | misc | governance | rev6 波 4 RAD-AI 取捨 ADR 收單：ADR-00007 accepted（附錄 A 19 列涵蓋 F01～F24；射程＝系統層形制、流程層以類比張力宣告偏離、D15 在活書正文零例外＋機器自證）；附錄 A 對 as-built 對賬零未決（證據段住 ADR）；活書四處（P-E1 指向 C4-E3、C4-E1 必填性質指針與導言中文化、§9.1 對映表改欄序）；波標記 5；merge --no-ff 回 rev6-admin-root | 1089a23 | — | — |
| 2026-09-03 | misc | governance | rev6 波 3 活書填實收單：arc42 官方子節 28 處自 rev5 藍本消化、C4-E 三檔 16 處、流程層 51 子節類比張力真句（P-E7 九欄登記表）、rev5 藍本對照表 20 列四項皆零（frontmatter rev5_blueprint 真源、ADR-00006）、reference/agents.md 15 列、GENERATED_FILES 12；TODO(波 3) 歸零、波標記 4；merge --no-ff 回 rev6-admin-root | 678705e | — | — |
| 2026-09-03 | misc | governance | rev6 波 2 活書骨架收單：arc42 十三檔＋ARCHITECTURE 索引、C4 五檔、compliance 23 鍵不適用、process 八檔 51 子節、ops 帳本三檔、生成器三支（ADR-00005）、GT-10 第八腿；Day-1 6→2、波標記 3；merge --no-ff 回 rev6-admin-root | 6e5f48c | — | — |
| 2026-09-03 | misc | governance｜000-w1-governance-tooling | rev6 波 1 後段收單：憲法 1.0.0（ADR-00003）＋RULES 首版 73 條（ADR-00004）＋tools/docsync（GT-01～GT-12、generate／check／lint／rules emit／errata）＋掃描防線（.gitleaks.toml、.githooks、bootstrap 回填）＋hook RULES-VERSION 對賬＋README／CLAUDE.md 正式版；merge --no-ff 回 rev6-admin-root | 4f892fc | — | — |
| 2026-09-03 | misc | governance | rev6 波 1 創世：守門五件（49f37d2）＋源倉 gitlink（881c621）＋啟動書搬入（7f34015）＋compose 3xxxx 與 deploy 遷入（8a20aaa）＋bootstrap 凍結斷言（4c24966）＋ADR-00001/00002（a31cb54）＋機密管線首建（ce6cfff／5e8e69f） | — | — | — |

## 備註（notes）

### 2026-09-04｜misc｜governance

審查形式＝一支唯讀 agent（opus[1m]、ultrathink）、對象 16358f1..432e47b、烤入 RULES scope=review 全塊；零 Critical、8 筆三分流＝修 6／轉 BL 2／won't-fix 0；報告見 docs/reviews/20260904-spec-compliance-001.md。
主線依 CLAUDE.md §5 獨立復現：廢 _check_col 型別腿／gate1 索引·約束整節／seed_add 欄集斷言，自帶 103 案皆照綠——三處判準是憲法 §I.6 六審計欄與 ADR-00010 決定 7 的唯一機器載體，可被無聲拿掉。
驗證分兩形（不可混稱）：archived_by 一項為真先紅後綠（驗則原不存在）；其餘判準本就正確、加案即綠，故改以十發變異探針逐一打在對應判準腿上驗紅（全數轉紅、在同構目錄副本上做、repo 零寫入）。hook 面另做真演練：注入假漂移→git add→commit 被 schema-frozen 擋下、HEAD 未動。
契約側同批：I-1／I-2 同時是 spec 自身未列義務（§4 只列五類、且「結構」字面只涵蓋 columns 節），實作是照 spec 做的，故擴為六類並註明⑥與①～⑤的差別（前五類注入實庫漂移、第六類注入驗則會不會抓）。
LL-00003 為本批演練踩坑：git checkout -- <路徑> 在檔案已 staged 時從 index 取而非 HEAD，還原等於沒還原；靠 RL-0005 的還原後 porcelain 對賬當場抓到，凍結面四檔已對 rev5 逐位元還原、sha256 合 provenance §4。

### 2026-09-04｜review｜001-schema-baseline

user 於 001 收刀後臨時發起的規格對照輪（superpowers:requesting-code-review 形）：一支唯讀審查 agent、對象 16358f1..432e47b、烤入 RULES scope=review 全塊（RULES-VERSION e41e0f177ef3）。零 Critical。
審查員 41 發變異探針、13 發空轉，全數集中在 schema-gate 的 audit 變體引擎（9）、gate1 索引·約束節（3）、seed_add 欄集（1）——主線依 CLAUDE.md §5 抽三發獨立復現屬實。本輪修單把 103 案補到 118 案，十發驗紅逐一打在對應判準腿上。
同批修正契約側缺口：`contracts/gates.md` §4 negative 義務由五類擴為六類（①註明 indexes／constraints 與 columns 同義務、新增⑥ audit 變體驗則面），因 I-1／I-2 同時是 spec 自身未列義務、實作照 spec 做。另補 §3 之 `archived_by`。
衍生條目 BL-00022（specs/001 目錄定位、觸發 002 開分支前）非 findings 三分流所出、係審查建議 1。

### 2026-09-04｜misc｜governance

user 拍板 2026-09-04（三題一題一問）：①BACKLOG 上限移除改只報表 ②閘數與 RULES 兩腿改永遠只警告 ③硬擋機制不動。理由＝三個預算腿性質不同：閘數與 RULES 數的是「我們主動加了幾條治理規則」、增長由自己控制；BACKLOG 開放數是「發現多少問題」的觀測值，壓低它只有真做掉或不記兩途，上限恰好在給後者誘因。
順帶修正 GT-12 兩種語意混用：BUDGET_GATES 原兼作無條件 ERROR 的結構等於斷言（len != BUDGET_GATES），只降級預算腿會讓「閘數只警告」形同虛設；現結構腿只驗 docstring 區塊集合 == ROSTER、數量交預算腿，pre-commit 檔頭範圍字串期望值改自 ROSTER 實算。BUDGET_ERROR_WAVE 更名 KNIFE_START_WAVE。
ADR-00004 依 GT-04 轉 superseded；其決定 1、3～8 與上限表數值仍為現行依據，rev6 無部分翻案機制、續行射程記於 ADR-00011 決定 5。RULES-VERSION 064380371fc0→e41e0f177ef3。
出口驗收：docsync test 126 綠（原 test_wave_lag_and_budget_levels 拆四案、先紅三案）、check 零漂移、lint 0／0／0、bootstrap rc 0 警告 0；errata 五詞現在式面零假述。

### 2026-09-04｜feature_close｜horizontal｜001-schema-baseline

逐位元自證（ADR-00009 決定 2①／SC-001；實跑結果不回灌 ADR、住此與各單元 commit 訊息）：17 檔（m0001_baseline_schema.rs／m0002_baseline_seeds.rs＋entity 15 表檔）對 rev5 rust-api @ 92919b9 去註解後 diff 17/17 零差異、rc 0；收刀前由 final holistic review 四支 lens 之二獨立復現同結果。
SC-007 行數落點：docsync package 2,603 行（`cat tools/docsync/*.py | wc -l`；spec 載基線 2,345、啟動書目標 ≤4,000）；pre-commit 全鏈 16.91 秒（perf 事件 precommit_chain、雙錨警戒 45 秒內）。
出口驗收：docsync test 123 綠、schema-gate test 103、entity-drift test 45；check 零漂移、lint 0 錯／0 警／0 閘跳過；閘數 12／12、GENERATED_FILES 14、ADR 10 全 accepted、RULES 74／92（RULES-VERSION 全刀未動）、LESSONS 2、bootstrap rc 0 警告 0。
單元對映：Task 0（BL-00001 骨架收斂）07c0407／U1（rust-api 骨架＋17 檔＋adapter＋dev stack 重放）add52e5＋子庫 c6c7d42／U2（兩閘工具隨遷＋fixtures 凍結＋ADR-00010 accepted）a8f5595／U3（snapshot.py＋兩快照＋兩真表＋entity-drift 段）9b8f02c／U4（RUNBOOK 與活書實文＋errata＋quickstart A～G）e47ccef＋子庫 d443278／U5（BL-00005 四欄渲染）429bf24／收單（final review 28 findings 三分流）be69543。
SC 對賬：SC-001 17 檔零差異；SC-002 fixtures 四檔對 rev5 逐位元＋sha256 合 provenance §4；SC-003 negative 五類；SC-004 演進帳往返 1→0→2→0；SC-005 DoD 鏈全綠＋entity 目錄缺席演練被 rc 2 擋；SC-006 憲法 1.1.0＋兩 ADR accepted；SC-007 見上。
教訓：LL-00001 零種子 Cargo.lock resolve；LL-00002 fix 升級後續跑（骨架 IMPLEMENTERS=0 續跑形＋主線先自掃同語意列舉）。

### 2026-09-04｜misc｜governance｜000-r1-doc-governance

計畫 docs/brainstorms/000-r1-doc-governance.md（grilling 22 題＋停點①②裁定）；final holistic review 零新 finding（bootstrap rc 0 ⚠ 0、91 測綠、lint 0／0／1、check 零漂移、四處 porcelain 乾淨）；分支 000-r1-doc-governance 保留供 audit；Day-1 仍 1（GT-08.lessons-absent）。user 指示（2026-09-04）：001 brainstorm 定稿 commit 重排到本收單之後（本機歷史重寫、未推），故 merge 第一父＝8a50ffe＝體檢對象。

### 2026-09-04｜review｜doc-governance

000-r1 獨立 review 輪（分支 000-r1-doc-governance、對象 8a50ffe；四支唯讀 Workflow 探索 99→合併 78→兩鏡三態驗證＋補漏 C＋修單 D；confirmed 86＝修 75（含主線 R1-M01）／BL 9 筆歸四條／ADR 1／none 2、另併入同缺陷 6；守恆計 fixed 75＋BL 4 條＋ADR 1＝80，none 2 與併入 6 不入守恆）；探針 32 題找不到 0、答錯 0；被駁回 24＋探針衍生 14 入附錄。修落四顆 commit 50c9ef7／2b0e10c／9b8129b／2ff2f51；RULES-VERSION c7a137209e0e→064380371fc0。

### 2026-09-03｜misc｜governance

計畫 docs/brainstorms/000-w5-doc-genesis-acceptance.md（brainstorm 三題＋grill 一題拍板）；final review 零 finding；計畫 nit 三處列於收單 commit 訊息；分支 000-w5-doc-genesis-acceptance 保留供 audit；Day-1 餘 1（GT-08.lessons-absent）。

### 2026-09-03｜review｜doc-genesis

文件創世驗收：DoD A 六條全勾、§7 自評十三列（系統層全不適用、流程層 2×7／1×4、Annex IV 兩列不適用）；GT-03 Day-1 豁免同 commit 解除（gates.py 移鍵、零 close 事件改 ERROR）。

### 2026-09-03｜misc｜governance

計畫 docs/brainstorms/000-w4-rad-ai-tradeoffs.md（brainstorm 三題＋grill 一題拍板、皆 A）；final review 處置列於收單 commit 訊息（T1 謂詞 4 行對 2 行 won't-fix；附錄 A 列數 20→19 勘誤已於 T2 修）；分支 000-w4-rad-ai-tradeoffs 保留供 audit；Day-1 仍 2（GT-03／GT-08）；BL-00002 觸發＝首個 AI-ADR 開寫前。

### 2026-09-03｜misc｜governance

計畫 docs/brainstorms/000-w3-book-fill.md（brainstorm 兩題＋grill 兩題拍板）；final review 處置列於出口 commit 訊息（§12 四詞標記校正）；分支 000-w3-book-fill 保留供 audit；Day-1 仍 2（GT-03／GT-08）。

### 2026-09-03｜misc｜governance

計畫 docs/brainstorms/000-w2-book-skeleton.md（grill 三題拍板）；TODO(波 3) 殘留 95 處為波 3 出口面；分支 000-w2-book-skeleton 保留供 audit。

### 2026-09-03｜misc｜governance｜000-w1-governance-tooling

出口驗收：bootstrap rc 0（⚠ 僅 remote 未定）、79 測試綠、lint 0 錯誤／7 Day-1 跳過、check 零漂移、docsync 邏輯行 1,872／4,000；GT-12 首值 閘 12／12、RULES 73／92、BACKLOG 未建／25。分支 14 顆：6f53f83 docs: README 文件地圖（GT-09 對賬面、D15 參考來源）＋CL；a3a26ab feat(hooks): PreToolUse 升級為 RULES-VERSIO；e822e11 chore(gates): 掃描防線落地——.gitleaks.toml／.gi；5ce7b25 feat(docsync): gates 名冊＋GT-01／07／09／12＋D；dc851a7 feat(docsync): generate／check（GT-01 本體）＋；900d0ec feat(docsync): GT-10 文件形制閘七腿（§3.4；波 1 Da；f4ef4d2 feat(docsync): GT-06 引用健康＋GT-11 bash 面＋e；6e3ab37 feat(docsync): GT-05 ID 家族＋跨代裸編號＋子庫碼面；GT；a06e4ca feat(docsync): adr——GT-04 不可變／對稱／禁刪除＋DEC；319ae30 feat(docsync): events schema（rev6 欄位）＋GT；a6387f5 feat(rules): RULES.md 首版 73 條＋上限實算（ADR-0；5e4433b docs(constitution): rev6 1.0.0 定版（§3.8 逐；1acc81d feat(docsync): package 骨架——Finding／Ctx／f；f1a80eb docs(brainstorm): 計畫 grill 修訂——七題拍板（憲法先於

### 2026-09-03｜misc｜governance

波 1 前段；治理工具與憲法／RULES 於後續 commit 落地
