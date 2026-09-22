<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# MILESTONES — 事件表（新在前）——perf 型另居 reference/perf.md

| date | type | 標的 | summary | merge | adrs | arch |
|---|---|---|---|---|---|---|
| 2026-09-22 | misc | governance｜maint-trust-model-bind-mount | 輕量軌 maint-trust-model-bind-mount 收單（macOS 第二台開發機 pull 時實證、主線直改零 cargo）：LL-00033 單檔 bind mount（deploy/trust-model.dev.toml）於 git 換 inode 後在容器內懸空、信任模型照契約退零網段而零紅燈；RUNBOOK §2 補固定起手句（動到該檔→up -d --force-recreate --no-deps rust-api）。LESSONS 32→33；RULES／ADR／閘數皆未動。 | 7beaa46 | — | — |
| 2026-09-22 | misc | governance｜maint-backlog-103-104-114-121-122 | 005 前第 8 支維護批（user 2026-09-22 依 BACKLOG 分類體檢裁定、python／doc 面五條、主線直改零 cargo）：perf 表列依 date 穩定排序；schema-definition 三行四處「本刀」改刀名形；GT-06 補折行拼接與懸空前綴兩腿；GT-12 新腿對賬走查工具與 rust-api 的門鈴頻道字面；route-artifact-gate 沙盒旗標前移。五條刪列、零新記。final review 12 筆＝修 9／駁回 3。 | 092cc52 | — | — |
| 2026-09-22 | misc | governance｜maint-spec-compliance-004 | 004 刀附屬規格對照審查輪（spec-compliance-004）修單收單：防自鎖更新腿與來源信心八態兩支保護腿補齊（皆變異自證）；跨刀活體契約 code-gate-contracts 六處改對；trust-model.dev.toml 折行死指針、obs.rs 五處碼註、活書 08 量法與活書 10 UI 判準、RUNBOOK §13 防自鎖座標；dev 可達態三處加 ADR-00040 對沖註。零 blocker、零 wire 行為缺陷。 | 1a9db89 | — | — |
| 2026-09-22 | review | 004-ip-trust-anchor | findings 24（修 12／BL 12／ADR 0）；BL-00114、BL-00115、BL-00116、BL-00117、BL-00118、BL-00119、BL-00120、BL-00121、BL-00122、BL-00123、BL-00124、BL-00125 | — | — | — |
| 2026-09-22 | misc | governance｜maint-backlog-86-90 | 005 前維護批第 7／7 支（末支、本輪唯一真改 production 碼者）：PageRes<T> 上移 envelope.rs（欄形與 serde 屬性逐字不動、wire 輸出 hex 逐位元比對不變）＋handler 共用件收攏為 handler/common.rs（tracing::error! 留呼叫點、兩域 target 不併）。兩條刪列。另修掉源碼掃描腿切面法的真缺陷：非行首切點被 doc 散文提前截斷，全樹非行首形清零。 | a0b8672 | — | — |
| 2026-09-22 | misc | governance｜maint-backlog-89-83-85 | 005 前維護批第 6／7 支：測試清理面收攏＋門鈴量測去全域相依＋IP 閘兩處回歸錨——BL-00089 ①② 三支守衛 Drop 還原殼收攏為一支 run_restore（還原計畫抽成純資料、等價性由純資料斷言釘死）＋observed_msgs_real_db 兩 sid 改掛 RAII 清鍵；BL-00083 精確等值量測改走區域量表＋兩支守門；BL-00085 ①ipgate_blocked 發射點恰一處之靜態掃描腿 ②ChainRejected 來源被閘擋之案。三條刪列。 | dc32264 | — | — |
| 2026-09-21 | misc | governance｜maint-backlog-92-97 | 005 前維護批第 5／7 支（rust 三支之首）：wire i64 守衛 lint 進場＋wire 裁判補 IP 規則請求型錨——BL-00092 新增 tests/wire_i64_guard_lint.rs（29 案、全樹靜態掃描，封住快照裁判對 2^53 守衛掛沒掛結構性無感的盲區；未掃出漏掛故 src 零改）、BL-00097 wire_schema.rs 24→44 案收 Api.IpRule 三支寫端請求型與清單 query（後者走查詢串真路徑）。兩條刪列。 | d4f33b7 | — | — |
| 2026-09-21 | misc | governance｜maint-backlog-80-88-94-99 | 005 前維護批第 4／7 支：三支 python 工具微修＋msg 面板指針形——BL-00080 量尺補 .py／.sh 面（tokenize＋ast 取 # 與真 docstring）、BL-00088 綠訊息改由實跑腿推導與沙盒失敗路徑補清、BL-00094 restore 清前有列即自動 PUBLISH ipgate:invalidate（排在 pg 交易之後）、BL-00099 Grafana 拒因字典改指針形。四條刪列。 | f91ba0d | — | — |
| 2026-09-21 | misc | governance｜maint-backlog-42 | 005 前維護批第 3／7 支：跨刀活體契約自 spec 目錄抽至 docs/ops/reference-src/（BL-00042、ADR-00041）——五份新家（四份整檔搬＋一份六節併入）、specs 原檔零改動留凍結存證、四十二處引用改指新家；GT-06 加腿同時守絕對形與裸相對形（後者為 repo 主流寫法、首版漏掃＝該腿原本 vacuous）。 | fdf181f | ADR-00041 | — |
| 2026-09-21 | misc | governance｜maint-backlog-35 | 005 前維護批第 2／7 支：事件帳守衛兩腿（BL-00035②④）——GT-02 加 append-only HEAD 對比腿（HEAD 版須為現版逐行前綴；刪列／改寫／疑中間插入三態各自指名，形制承 GT-04），GT-03 改為「有無效列即指名首列並中止下游判讀」（原本無效列被丟棄⇒在途與完整性腿對不存在的事件續判＝整片假報）。自測 280→282 案、閘數維持 12/12。 | 9b932d8 | — | — |
| 2026-09-21 | misc | governance｜maint-backlog-79 | 005 前維護批第 1／7 支：Workflow 看門狗改雙掛形——`wf-watchdog.py` 加 `--bg` 背景任務模式（RUNAWAY 由告警不退出改告警即退出，因背景任務只有退出才通知主線；rev5:B-069 契約的具名例外），CLAUDE.md §2／RL-0016／RL-0017／RL-0061／PostToolUse hook 提醒文字同步雙掛分工；自測 35→38 案。BL-00064／BL-00067 依 user 裁定移滯後卷。 | fd682da | — | — |
| 2026-09-20 | misc | governance｜maint-no-tmp-refs | 受版控文件禁寫 tmp 具名路徑（user 2026-09-20 指示、射程裁定＝只綁現在式面）：立 RL-0077、GT-06 加 `_tmp_refs` 腿（不新增閘、閘數仍 12/12；佔位／glob 與 OS /tmp/ 不入射程，史料面與 ADR body／events／generated 豁免）、LL-00030 一坑一檔、CLAUDE.md §4 指針行；現在式面十處修正（LESSONS 三筆、tools/orchestration 三處、deploy/sops.sh 用法例）。 | 119f1d4 | — | — |
| 2026-09-20 | feature_close | 004-ip-trust-anchor | 004 ip-trust-anchor 收單（rev6 第四刀）：信任錨真實來源還原／請求上下文／IP 存取閘／IP 規則五端點＋防自鎖＋操作稽核首寫／來源維登入節流（兩維、每次由 PG 定案、拔負快取）／管理員解鎖端點／IP 規則管理頁＋★軌道 BASE-WEB-MANAGE-PAGE-WIRING／兩支新碼面閘／RUNBOOK §16；零 migration；憲法 1.4.0；ROUTES 22、contract 24、MSG_KEYS 19、後端全量 679 passed。 | 990c4a7 | ADR-00034、ADR-00035、ADR-00036、ADR-00037、ADR-00038、ADR-00039、ADR-00040 | §3、§5、§6、§8、§10、§11、§12 |
| 2026-09-15 | misc | governance｜maint-spec-compliance-003 | 003 刀附屬規格對照審查輪（spec-compliance-003）修單收單：login／refresh／route 六處測試保護補案（⑥TTL 兩腿、last_activity 兩寫端 TTL、驗章前擋與⑩臂源序守、idle 門檻隨現值、home 兜底）；msg-key-gate 斷言 2 同義構造形、fork-delta-lint template 形與樓地板守、hook 守衛補子庫 pre-commit；活書 08 §8.4 標記定形與四處現在式勘誤；ADR-00033 logout 舊票 no-op by-design。 | 8df3efd | ADR-00033 | — |
| 2026-09-15 | review | 003-auth-session | findings 21（修 16／BL 4／ADR 1）；BL-00042、BL-00066、BL-00077、BL-00078、ADR-00033 | — | — | — |
| 2026-09-15 | misc | governance｜maint-spec-compliance-002 | 002 刀附屬規格對照審查輪（spec-compliance-002）修單收單：facade 同值更新審計欄成對純測、description 型別不符 rust 側拒收案、contract 覆蓋閘判準自證；wire-schema.py 兩處註解、RUNBOOK §12 名冊現值鏡像改指針、arc42 05 真 DB 端點案住所改現在式；RULES 名詞段碼面閘環境缺席語意改逐支見表（ADR-00032 supersedes ADR-00016）；BL-00028 條文併入 seed 值↔REGISTRY 界值零守。 | 37461af | ADR-00032 | — |
| 2026-09-15 | review | 002-system-settings | findings 8（修 8／BL 0／ADR 0） | — | — | — |
| 2026-09-15 | misc | governance｜maint-backlog-71-46-76 | 輕量軌 maint-backlog-71-46-76 收單（004 刀前第二支維護批）：comment-overlap 量尺擴充——`/** */` 與 `.vue` HTML 註解解析、rev6-↔rev5- 對應檔映射、反引號 span 與 doctest 圍欄豁免全路徑；base-web 註解改寫（BL-00071＋新量尺浮出之超標）與 wire-schema 快照 description 重抽；rust-api entity 關聯宣告只映真 DB FK 之機器腿、復原 A3 拆碎字面；BACKLOG 條文勘誤十列。 | cf1541b | — | — |
| 2026-09-14 | misc | governance｜maint-backlog-pre-004 | 輕量軌 maint-backlog-pre-004 收單（003 刀收刀後、004 刀前；四單元）：A1 rust-api 測試側補強＋JWT 兩鑰 boot 斷言（ADR-00031）；A2a pre-commit 段序鏡像腿／submodule-sync／bootstrap-roster；A2b walkthrough restore／帳號快照投影腿／comment-overlap fork-delta 豁免／msg-key-gate 前端消費點腿；A3 rust-api 註解改寫 21 檔（comment-overlap rc 0）。 | db25165 | ADR-00031 | — |
| 2026-09-14 | feature_close | 003-auth-session | 003 auth-session 收單（rev6 第三刀）：真登入／續期 rotation＋grace／撤銷三型＋denylist 四級降級／節流三區＋captcha／替代登入 stub／i18n 跨端閘 msg-key-gate／治理六項；零 migration；憲法 1.3.0；ROUTES 16、contract 16、MSG_KEYS 13；SC-012「RULES 零改動」子句失效＝三處 RULES 改動皆 LL promotion；backlog_add 以在途 GT-03 全集為準；final review 分流見 51ab7c7。 | 0e74551 | ADR-00026、ADR-00027、ADR-00028、ADR-00029、ADR-00030 | §5、§6、§8、§10、§11、§12 |
| 2026-09-08 | misc | governance｜maint-py313-docstring-dedent | 輕量軌 maint-py313-docstring-dedent 收單：閘區塊 regex 去掉對 docstring 縮排的依賴。Python ≥3.13 編譯期剝掉 docstring 共同縮排後 gate_id() 對 12 支閘全回 None——GATES.md 算成無列空表（GT-01 漂移）、GT-05 的 ID 存在性真源成單元素 None 集（閘號引用 322 筆假紅）、docsync 自測 10 案連坐、bootstrap exit 2。`[ \t]+` → `[ \t]*` 還原原意＋補迴歸案；LESSONS 12→14。 | 9e420a2 | — | — |
| 2026-09-07 | misc | governance｜maint-backlog-40-39-37 | 輕量軌 maint-backlog-40-39-37 收單（003 開刀前治理維護、三條合一顆）：BL-00040 探針題庫隔離全收（否定對照表刪「真相」欄、r3 起真相烤進 grader prompt 不落 tracked）；BL-00039① 編排骨架五常數型別＋非空斷言（harness-test 十五→十八案）；BL-00037③ wire 契約閘雙側觸發（pre-commit 觸發字面＋wire-schema.py 快照側 pin 區間收窄、自測 27→31 案）。BACKLOG 15→14；閘數 12 與 RULES 未動。 | 4844b15 | — | — |
| 2026-09-07 | misc | governance｜000-r2-doc-governance | 獨立輪 000-r2 文件治理架構第二輪體檢收單：五支 Workflow 85 支 agent、findings 102（confirmed 88）、修 69／BL 8 條／ADR 4 支；BL-00003 閘補腿群三腿全落地（GT-03 BL 存在性腿／SKIP 分類＋ENV_SKIPS＋GT-12 登記腿／主張閘兩腿，閘數維持 12）；憲法 1.1.0→1.2.0；檢索性第四指標 0.48→0.76。 | acc11a7 | ADR-00022、ADR-00023、ADR-00024、ADR-00025 | — |
| 2026-09-07 | review | doc-governance | findings 81（修 69／BL 8／ADR 4）；BL-00035、BL-00036、BL-00037、BL-00038、BL-00039、BL-00040、BL-00041、BL-00042、ADR-00022、ADR-00023、ADR-00024、ADR-00025 | — | — | — |
| 2026-09-07 | misc | governance｜maint-backlog-7 | 輕量軌 maint-backlog-7 收單：BL-00007 檢索性第四指標——ADR-00021：review 事件 optional probe 欄（冷啟動探針＋否定對照題四值計數、grader 最短 hops 平均）為資料源、GT-02 形檢、erratum 欄集加 probe、STATE 治理指標表第四列比例現算（目標＝找不到＋答錯＝0、≤3 跳比例輪間不降）；000-r1 以 erratum 回填為基準。 | b6e62e3 | ADR-00021 | — |
| 2026-09-07 | erratum | 行 13 | ADR-00021 回填：000-r1 探針結果自報告 §3 逐題表回算（冷啟動 25 題＋否定對照 7 題、grader 最短 hops 平均）——當時 review 事件無 probe 欄、只落 notes 自由文 | — | — | — |
| 2026-09-07 | misc | governance｜maint-backlog-21 | 輕量軌 maint-backlog-21 收單：BL-00021 憲法 §I.5 例外②邊界定性——RUNBOOK §10 補一句「migration／entity 兩 crate 之 main.rs／lib.rs／Cargo.toml 五檔為承形自寫之自然收斂（去註解後只差改名級差異）、不屬例外②射程亦非未登記拷貝、稽核以 ADR-00009 之 17 檔為準」；ADR-00009／憲法不動。 | 3b42b40 | — | — |
| 2026-09-07 | misc | governance｜maint-backlog-25 | 輕量軌 maint-backlog-25 收單：BL-00025 憲法 §I.5 例外① 自證腿——docsync vendored-check（rust-api/sea-orm-adapter 全部 tracked 檔去整行註解後 diff rev5 凍結樹、差異須逐對在 tools/docsync/vendored.py 具名 ALLOWLIST 附理由、rev5 側存雜湊）＋bootstrap 3c 步每台機器體檢；ADR-00009 不動；LL-00012。 | c705ab2 | — | — |
| 2026-09-07 | misc | governance｜maint-backlog-23 | 輕量軌 maint-backlog-23 收單：BL-00023 pre-commit 接線機器守衛——tools/docsync/tests/test_hook_wiring.py 純函式對賬固定鏈、七條件段觸發／命令字面、for 自測名冊 ⊇ 碼面閘表∪NON_GATE_TOOLS、未登記段即紅（一正六反）；hook 新段 orchestration（tools/orchestration 之 js\|mjs\|py staged→三支入庫範例組裝＋harness）；hook 本體 staged 亦跑 docsync test。 | 24d4e2a | — | — |
| 2026-09-07 | misc | governance｜maint-backlog-6 | 輕量軌 maint-backlog-6 收單：BL-00006 review 骨架入庫——_sk_review.js（lens／兩鏡三態／grader／critic）與 TDD 形共用 _sk_head.js、assemble.py 雙模式組裝器、harness-test 十五案／harness-review 九案、三支單元定義範例、agents.md 七角色入冊；dogfood 自審一輪三分流；ADR-00020 GT-09 子名冊腿；BL-00032～34 當批收掉、BL-00034 併 BL-00023。 | eda591d | ADR-00020 | — |
| 2026-09-06 | feature_close | 002-system-settings | 002 system-settings 收單（server crate 進場首刀）：rust-api server crate 從零（router／auth／handler／validation／facade／error 13 碼矩陣）＋契約機器化（wire-schema 快照裁判、contract 雙向覆蓋閘、msg 名冊後端閉環）＋endpoint_tests 32＋1 案；base-web 兩支新增型新檔；三支碼面閘＋RUNBOOK §12 碼面閘表＋GT-12 腿；零 migration、憲法零 Amendment；ADR-00013～00019；活書 05／08 as-built。 | ecea8ee | ADR-00013、ADR-00014、ADR-00015、ADR-00016、ADR-00017、ADR-00018、ADR-00019 | §5、§8 |
| 2026-09-05 | misc | governance | 002 開分支前 BACKLOG 清償：A＋B 十二條一批收掉（BACKLOG 20→8）——RULES 三條、活書一條、docsync 四條、schema-gate 兩條、生成器補全群與 schema 定稿抽出；RULES-VERSION bump、rev6 首筆 erratum、ADR-00012 accepted。 | 2c35da6 | ADR-00012 | — |
| 2026-09-05 | erratum | 行 19 | 該筆收單漏記 adrs（misc 當時無此欄）——DECISIONS-INDEX 之 feature 欄因而對 ADR-00011 印裸「輕量軌」；BL-00004 補欄後以本筆更正 | — | — | — |
| 2026-09-04 | misc | governance | 001 刀規格對照審查（獨立輪 spec-compliance-001）修單收單：schema-gate 自帶測試 103→118 案補回歸保護（audit 變體驗則面、gate1 索引與約束兩節、seed_add 欄集）、D 變體補 archived_by、pre-commit 加 schema-frozen 條件段、contracts/gates.md §4 negative 義務五類擴為六類。 | 39232de | — | — |
| 2026-09-04 | review | 001-schema-baseline | findings 8（修 6／BL 2／ADR 0）；BL-00020、BL-00021 | — | — | — |
| 2026-09-04 | misc | governance | 數量預算改為只警告不擋（ADR-00011 supersede ADR-00004）：BACKLOG 開放取消上限、改觀測值只報表；閘數 12 與 RULES 總／per-scope 上限保留數值但超限一律 WARN、不進 lint 退出碼、不擋 commit；pre-commit 硬擋機制不動。 | 1e0d89b | ADR-00011 | — |
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

### 2026-09-22｜misc｜governance｜maint-trust-model-bind-mount

★取證：容器內 ls -la 列出檔但 link count 0、size 為舊版；讀取 ENOENT；boot 日誌 kind=Missing→NoTrustedNetwork、warnings:2 internal_default:0；重建容器後 warnings:0 internal_default:1（172.16.0.0/12）。★載入器行為與 reference-src/trust-model-config.md「檔案讀不到→扁平退路」契約一致，缺陷在 mount 不在碼、故不動碼不立閘；rule_id none、promotion_surface none。★同家族 LL-00005／LL-00032：容器對 host 檔的視圖與實況分叉、皆以綠呈現。★自驗：docsync check 零漂移／lint 0 錯 0 警 0 跳過／test 301 案 OK。實作顆 7e6437a。

### 2026-09-22｜misc｜governance｜maint-backlog-103-104-114-121-122

2 顆：直改 fbce710（含 amend：案數假述 12→11、三處→三行四處）＋final review 收單 1b14a30（run wf_5528f512-b12、6 支、36 分鐘；12 筆＝修 9／駁回 3；L1-1 兩鏡建議轉 BL、主線改判當批收＝懸空前綴腿現況零命中零假陽、嚴格形裸露前綴一律紅；駁回三筆＝L2-4「RL-0020 無機器承載」在 RULES carrier 欄有家、L2-5 NOTES 區間為 004 輪史述且 BL 引用刻意不入 GT-05、L2-6「七支」為 09-21 裁定之集合基數）。★rust-api／base-web 零改動、pins 不動。★兩顆收單訊息各數錯一次新增案數（12→11、6→7）皆未推即 amend；教訓＝案數以 git ls-tree 逐檔數 def test_ 差值現算、不手數。rust 測試側四條 BL-00107／BL-00110／BL-00123／BL-00115 與 BL-00106 同批留 005 收刀前承載體檢。淨流量：本批 −5 落 005 收刀窗（rolling-3 至該窗關帳才入帳）。

### 2026-09-22｜misc｜governance｜maint-spec-compliance-004

報告 docs/reviews/20260922-spec-compliance-004.md；findings 35 筆原始、去重 30＝修 12／轉 BL 12／駁回 2／報告記載 7。兩支唯讀 Workflow：wf_b1d4020a-658（五鏡＋探針 18 支）、wf_13f0723b-e36（五鏡 15 支），皆零錯零 null。修單 commit 4a8dcc3（rust-api 246d5ff）；全量 cargo test 772 案綠 0 紅 2 ignored、走查基準前後全等。修 12 之逐項與駁回／記載理由見報告 §2；★兩筆主線改判＝dev 可達態改走對沖、rust-api 碼註引凍結 spec 依「已駁回者不得重報」駁回。★user 2026-09-22 兩題裁定：憲法 §III.2 量法與表列數、憲法 §I.7 段首計數，皆立 BL 併入下次 §V.2 Amendment、本輪不單獨開。

### 2026-09-22｜review｜004-ip-trust-anchor

user 2026-09-22 發起之 004 刀附屬對照輪（RL-0073 ②；HEAD fd9f99f 基準、收刀點只歸因、specs 本文不改；CONTEXT 烤入 002／003 兩輪經驗七條＋RL-0078 防污染）。兩支唯讀 Workflow：run A wf_b1d4020a-658（五鏡＋冷啟動探針、18 支、38.6 分）、run B wf_13f0723b-e36（五鏡、15 支、26.8 分），皆零錯零 null；切兩支之由＝FR 數為 003 的 1.75 倍且需專鏡核七支維護批對 004 碼面的改動。findings 35 筆原始、去重 30：修 12／轉 BL 12／駁回 2／報告記載 7（total 24 只計已處置者，駁回與記載見報告 §2）。零 blocker、零 wire 行為缺陷；七支維護批對 004 碼面之改動全部找得到承載，base-web 自 004 收刀後零改動。★兩筆主線改判：①dev 可達態由二改三之修法改為「三處加對沖註＋BL-00125」——ADR-00040 款 2 逐字寫二態、body 不可變（GT-04）；②rust-api 碼註引凍結 spec 一筆駁回——子庫面不在 ADR-00041 射程且 maint-backlog-42 final review 已兩鏡駁回。★兩支新保護腿皆變異自證：防自鎖更新腿判別案（廣義變異使既有案亦紅⇒軟刪腿另有覆蓋；改打 Update 臂則只有新案紅）、來源信心八態窮盡守（加第九態＋補 as_str arm 後僅一個 E0004，命中新守）。主線復核自查追加兩筆當批收掉（RL-0020 三處本刀、RL-0011 工具 docstring 同源假述）。探針三題皆 found、答錯 0、找不到 0，三題皆判繞路（最短兩跳），共同成因＝活書 §6.1 島 E／島 F 表格列過長；不填 probe 欄（理由同 002／003）。全量 772 案綠 0 紅 2 ignored、走查基準前後全等、rustfmt 綠且三個憲法例外面零改動自證。

### 2026-09-22｜misc｜governance｜maint-backlog-86-90

3 顆：U1 9315176＋U2 7aef314＋final review 收單 af6b890。★兩條的解除謂詞皆未到期（PageRes 全樹恰一消費者、operator_from 恰兩份），user 2026-09-21 覆蓋裁定提前執行；碼內逐字記明提前、未暗示謂詞已到。審查合計 40 筆＝修 39／駁回 1（駁回者＝「json_or_default 收攏是 155 行掃描守的唯一成因」，兩鏡查出該守的拒寫維服務的是要保留的另一半）。★被修的切面法缺陷兩處：envelope.rs（負面斷言型、恆綠無聲，被 U1 自己的 PageRes doc 散文截斷使 pub struct PageRes 掉出射程）與 router.rs／login.rs 兩支／refresh.rs 的 split( 形（正面斷言型、fail-loud，其中兩支已實際截斷）。★final review 抓到主線自己兩筆 commit 訊息假述：U1 把新增 lib 案指名為全樹零命中的 former_host_keeps_no_pub_use_re_export_of_page_res（實為 page_res_wire_bytes_frozen）、U2 把 572→575 歸因錯；本輪第二次「抄 agent 自述未查證」，取證方式已改機器形。★BL-00111① 據實重寫為十二支腿／九檔、枚舉判準改可複算 grep——前輪漏抓 split( 形正是因為以人列清單為準（RL-0002 反例）。新立 LL-00032（drvfs 下 cargo 假綠）。

### 2026-09-22｜misc｜governance｜maint-backlog-89-83-85

3 顆：U1 b07435d＋U2 67e6289＋final review 收單 c1b5f03。★BL-00083 的條文成因經實測證偽：#[tokio::test] 每案自持 current_thread runtime、案尾 drop 即取消 spawn 的 watcher，跨案污染物理上不成立（主線以 agent 未用過的 shuffle seed 77／91 獨立複核）。真成因＝①同案內常駐 watcher，量測窗跨 .await 即輪得到它推格 ②libtest 預設並行。條文所列兩條修法（改不等式／給停機句柄）皆失去前提，改走第三條路。★final review 的 blocker 打的是主線自己：U2 commit 訊息抄了 agent 自述的「移除四處 watcher.abort()」而未 grep 查證，實況是全樹本就沒有 abort（四處實為 is_finished 常駐斷言）；因未推未被引用，已改寫歷史清掉（rust-api 65618a9→41aa1dd、外層 8677bd1→67e6289，內容零變動）。findings 合計 42 筆＝修 40／轉 BL 2／駁回 1。活書 §6.1 與 §10.2 兩張島 F 守門表同批補列本批四支新守。

### 2026-09-21｜misc｜governance｜maint-backlog-92-97

真全樹掃描結論（主線與兩位審查員各自獨立重算、三方一致）：derive(Serialize) 型 16／i64 與 Option<i64> 欄 10＝已守衛 6・具名豁免 4（JWT 與 captcha 票 payload）・名冊外未守衛 0・Nested 0。3 顆：U1 d453793＋U2 67d8497＋final review 收單 c329049。★U1 的 SpecReview 在首個 run（wf_69f9709c-aa2）被 prompt 污染整段落空——agent 把 context 內轉述的 user 進度提問當成優先指令、刻意不執行審查即回 agentStatus=failed 且 blockers 空（空 blockers 與審查通過在回傳形狀上不可分辨、只有 reason 分得出來），以續跑形補跑兩次（wf_e9646b9b-a78 規格 4 輪／wf_69c55fde-c1d 確認輪＋碼品質 4 輪）才收斂；立 LL-00031＋RL-0078（agent 那一半）＋RL-0079（主線那一半，同批修 RL-0004 與 CLAUDE.md §2 的「空 blocker 即收斂」字面）。findings 合計 32 筆＝修 21／轉 BL 5／駁回 6。ADR-00040 款 6 additionalProperties 全域開啟同批重評＝維持不開不翻 ADR（翻案觸發器皆未踩到），附帶查到的 as-built 落差轉 BL-00105。活書 05 契約測試面枚舉補列本 lint、08 契約機器化四件→五件且②句擴寫並各補裁判力邊界。RULES-VERSION a040f612a18a→0bbc9765d102。

### 2026-09-21｜misc｜governance｜maint-backlog-80-88-94-99

2 顆：實作 4fd9122＋final review 收單 754989b（run wf_05f10455-5af、6 支 agent、19 筆 findings＝修 18／駁回 1〔兩鏡 refuted〕）。★review 兩處要害：①BL-00080 首版以行首三引號猜 docstring，會把一般三引號字串收尾行之後的碼行整段吞進量測面（實測虛報 97.4%／40% 字元是碼），改 tokenize＋ast 後 83.5%；②BL-00094 首版把門鈴排在 redis DEL 之後，DEL 失敗即拋、重跑時清前已 0 列＝永遠補不回來，改排在 pg 交易之後。三支工具自測合計 +11 案；RULES RL-0076 補隨遷工具豁免字面（原只住工具檔頭、不在 emit 進 prompt 的條文）。

### 2026-09-21｜misc｜governance｜maint-backlog-42

1 顆 6652be5（實作＋final review 收單合一：review 指出 ADR-00041 三處失準，GT-04 禁 accepted ADR body 變更、該顆尚未 merge，依 review L1-8 提案以 git reset --soft HEAD^ 重打）。review run wf_7e59fecf-b26、6 支 agent、20 筆 findings 兩鏡 17 confirmed／2 refuted／1 uncertain → 修 18／轉 BL-00104／駁回 2。★根因：首版枚舉只掃絕對形，漏掉十七處裸相對形消費者與四個同樣跨刀常設的契約（001 fixtures、002 §1.3／§4、003 §2），射程自六份修正為七份來源檔。變異自證三層（拔腿／改回絕對形／改回裸相對形）皆紅、還原綠。

### 2026-09-21｜misc｜governance｜maint-backlog-35

2 顆：實作 3d7e4e0＋final review 收單 f48c279（run wf_ef82d105-eec、6 支 agent、14 筆 findings 三分流＝修 10／轉 BL-00102〔閘取值面與 HEAD 缺席口徑〕＋BL-00103〔perf 渲染依 date 排序〕／駁回 2〔兩鏡皆 refuted〕）。BL-00035 改列：②④ 收、①③ 留、子項編號不重排（碼面註解與測試 docstring 已引 BL-00035②／BL-00035④）。review 指出的兩個存活變異（逐行前綴→包含判準、有任何無效列→錯誤筆數≥2）在補案後雙雙轉紅。RUNBOOK §12c 補「一律尾端 append、不按日期插入」與 `git reset --soft HEAD^` 出路。

### 2026-09-21｜misc｜governance｜maint-backlog-79

2 顆：實作 64d633a＋final review 收單 c74179b（review run wf_314bbaac-867、6 支 agent、16 筆 findings 三分流＝修 14／轉 BL-00101／駁回 1〔兩鏡 decided 判 refuted〕）。BL-00064／BL-00067 移入 BACKLOG-DEFERRED（滯後 2→4、開放 36→34）。雙掛形於本支 review run 實跑驗證：三 call 原子成對、Monitor 腿推播 ARMED、背景長尾腿 DONE 自行退出。RULES-VERSION a040f612a18a→27645c71f1e0。user 2026-09-21 grilling 十三題裁定見該輪計畫（tmp、gitignored）。

### 2026-09-20｜misc｜governance｜maint-no-tmp-refs

單顆 0ed372e；RULES 76→77（implementer 41/48、主線 44/52）、RULES-VERSION a2721b391067→a040f612a18a；docsync test 279→280 案全綠、lint 0 錯 0 警 0 跳過；真 repo 變異自證（塞具名 tmp 路徑→GT-06 紅、還原→綠）；errata 復掃四個被移除字面、殘留僅測試反例 fixture。NOTES 下一步不變（仍＝005 role-menu-crud＋兩件留帳），依該檔自述「逐刀交付查 MILESTONES」不重述本批。

### 2026-09-20｜feature_close｜004-ip-trust-anchor

backlog_add 以在途 GT-03 全集為準（BL-00081／BL-00100 為刀內新增並兌現、兩欄同列；BL-00087 併入 BL-00080、未誕生）；BL-00079 依 user 2026-09-20 裁定緩裁；三層判定＋兩覆蓋＋轉發鏈逾限拒絕、存取閘熱重載與 keep-last-good、HTTP 層錯誤轉譯、rules.yml 12 條；final review 分流見 d8cff6a、finishing 停點 user 三項裁定兌現見 b15b96d。

### 2026-09-15｜misc｜governance｜maint-spec-compliance-003

報告 docs/reviews/20260915-spec-compliance-003.md；findings 26＝修 16／轉 BL 4（BL-00042 併入②、BL-00066 user 拍板留帳至 004 brainstorm、新記 BL-00077／BL-00078）／by-design ADR 1／駁回 4／併入 1。修單 commit bb0629e（rust-api 2ec9df7）；三輪變異抽驗各自只紅對應新案、全量 cargo test 440 綠。

### 2026-09-15｜review｜003-auth-session

user 2026-09-15 發起之 003 刀附屬對照輪（RL-0073 ②；HEAD 4f8d607 基準、收刀範圍只歸因、specs 本文不改；CONTEXT 烤入 002 輪經驗五條）。唯讀 Workflow wf_986564f0-f2d：六 lens＋一冷啟動探針、派 21 支零錯零 null；findings 26＝confirmed 21／refuted 4／uncertain 1。分流：修 16／轉 BL 4（BL-00042 併入②、BL-00066 user 拍板留帳至 004、新記 BL-00077／BL-00078）／by-design ADR 1（ADR-00033，user 拍板）／駁回 4／併入 1；守恆 total 21＝fixed 16＋to_backlog 4＋wontfix_adr 1。主線三輪變異抽驗：新增與加強之六案各自轉紅、同模組既有案全綠；全量 cargo test 440 綠。探針三題皆繞路、找不到 0、答錯 0（只入 notes、不填 probe 欄）。

### 2026-09-15｜misc｜governance｜maint-spec-compliance-002

報告 docs/reviews/20260915-spec-compliance-002.md；findings 11＝修 8／none 2／併入 1（review 事件 total 8＝fixed 8）。修單 commit 7f250b2（rust-api e907b53）。全量 cargo test 首跑 65 紅＝dev 庫 2026-09-14 18:27Z 真登入殘列使序列重設守衛拒跑，依 RUNBOOK §9c 以空基準快照 restore 後 435 綠。

### 2026-09-15｜review｜002-system-settings

user 2026-09-15 發起之 002 刀附屬對照輪（RL-0073 ②；HEAD f2f57a4 基準、收刀範圍只歸因、specs 本文不改）。唯讀 Workflow wf_7281df94-3c9：三 lens＋一冷啟動探針、派 12 支零錯零 null；findings 11 兩鏡 confirmed 11＝修 8（L2-3 經 user 拍板立 ADR-00032 supersedes ADR-00016）／none 2（data-model §2、§7 字面缺陷只記載）／探針衍生 1 併入 L2-1；守恆 total 8＝fixed 8。主線三發變異抽驗：新增三案各自轉紅、既有相關案全綠。探針三題皆繞路、找不到 0、答錯 0（只入 notes、不填 probe 欄）；seed 值↔REGISTRY 界值零守併入 BL-00028 條文。

### 2026-09-15｜misc｜governance｜maint-backlog-71-46-76

單元 commit：S1 2f47c35（BACKLOG 條文勘誤：BL-00028／BL-00036／BL-00039／BL-00047／BL-00048／BL-00062／BL-00065／BL-00070／BL-00076＋滯後卷 BL-00049 之 rev5 引用）；B1 57ede8a（comment-overlap 量尺：自測 16→35、量測 base-web 超標 4／rust-api 47 檔 0）；B2 base-web ff528496／rust-api 546dcb4／外層 c4ff83f（base-web 4 檔純註解改寫、wire-schema.json 2 處 description 重抽、雙 pin 同顆）；B3 rust-api b0db679／外層 2229152（BL-00046 entity 關聯宣告腿＋BL-00073 復原字面九處）；B3-fix rust-api b33b952／外層 759d633（B3 審查升級三項）；final holistic review 收單 eb4c520（13 筆＝修 11／駁回 2、零轉 BL）。user 2026-09-14 裁定：範圍＝桶 A 兩條＋comment-overlap 量尺群＋條文勘誤；`/** */` 盲區併入 BL-00076；`.vue` HTML 註解一併納入；code span／doctest 圍欄豁免全路徑套用；全部 agent＝opus[1m] xhigh（成品換模、骨架不動）。主線工程裁定：BL-00046 落 entity_behavior_lint.rs、宣告 ⊆ FK＋完整性等式＋原生 SQL 守衛；HTML 註解只解析 .vue；BL-00043／BL-00045 觸發拆面待 004 brainstorm。單元收尾主線處置：B1 補 M21 反例＋docstring 射程外（巢狀塊註解、跨註解行 code span）；B2 標記行只 token 不動、同行散文可改寫。B3 arc42 08／05 對應句；B3-fix strip 引擎合一（行為等價 probe 69 檔＋400000 次模糊輸入差異 0）、A3 拆碎字面餘四處、ADR-00009 條號（決定 2 之 ③）。final review 分流：修 11（comment-overlap `.vue` HTML 註解內圍欄反例＋行首塊註解未閉合之射程外句；entity_behavior_lint 原生 SQL 字樣整詞比對、未建模 FK 建立形〔add_foreign_key／TableForeignKey／ForeignKeyCreateStatement〕出現即紅、檔頭 ② 出處改為 rev5:002 FR-022 拍板①並使 ADR-00009 轉述同向；BACKLOG BL-00028／BL-00047／BL-00065 措辭；README 圍欄限定語）、駁回 2（`#` 註解檔型＝三形聯集窮舉已拍板；在途 BACKLOG 四列＝收單簿記刪列之既定程序）。已知態：comment-overlap 行首 `/*`／`<!--` 至檔尾未閉合時其後各行照註解收（docstring 射程外）。

### 2026-09-14｜misc｜governance｜maint-backlog-pre-004

單元 commit：S1 cc3a9fd（BACKLOG 檔頭「動 X」定義＝user grill Q5）；A1 rust-api 5ecdd98／外層 3a09e81；A2a 9ca8334；A2b 6f9fc1d；A3 rust-api 9e2acb3／外層 4992f7e；final holistic review 收單 e0dd22b（28 筆：修 18／轉 BL 5／駁回 5；探針三題皆找得到、開檔口徑 1 跳）。user 2026-09-14 grill 九題全裁（範圍 A1＋A2＋A3、BL-00059 新段只跑 test_hook_wiring、BL-00061 只比 JWT 兩鑰、BL-00050 射程＝扣例外①②之 21 檔、BL-00038／BL-00063 納入、BL-00039 留待 000-r3 前、BL-00051 以碼註明文收）；本批全部 agent＝opus[1m] xhigh（成品換模、骨架不動）。BL-00068 前提不成立（候選案自 002 刀 U2 即存在）、以 backlog_done 收；BL-00035 條文補子項④（事件單筆無效之下游代言）。新立 BL-00070（src 測試模組自持 oneshot 殼）／BL-00071（base-web 兩處我方散文與 rev5 同文）；final review 另立 BL-00072（main.rs 斷言接線守）／BL-00073（comment-overlap rust-api code span 豁免）／BL-00074（外層名冊⇔子庫工作樹同步面）／BL-00075（走查外殘列清理＝BL-00053 該用例移交）／BL-00076（rev6-↔rev5- 對應檔映射＝翻轉 A2b「承 rev5 之檔必有對應檔」前提）；新 LESSON LL-00021（drvfs 舊 .pyc 使變異假存活）。主線收尾裁定：submodule-sync `--untracked-files=all`＋閘面含 `base-web/src`；docs/process 兩表 pre-commit 列改指針句；envelope.rs doctest 圍欄註解行放寬改寫；comment-overlap 標記豁免收窄為只剝 token（final review）。已知態：只改 README 之 commit 不觸發鏡像腿（延遲一站）；restore 只比 setting_value（gate2 兜底）。

### 2026-09-08｜misc｜governance｜maint-py313-docstring-dedent

★成因細節：RE_GATE_BLOCK 以 `[ \t]+` 要求 kv 行有行首空白，而同一 regex 同時吃原始碼文字（縮排在）與 gate_id() 傳入的 fn.__doc__（3.13 起零縮排、gh-81283）；gate_id() 回 None 後 gen_gates_md 於 gid + "." 先 TypeError。★徵狀識別價值：ID 存在性類閘一次噴上百筆、連 CLAUDE.md 自己寫的閘號都判「真源查無」＝先懷疑真源集合算成空的，不是逐處查引用。★既有 test_blocks_anchors_roster_on_real_package 已含 {gate_id(g) for g in ROSTER} == set(blocks) 斷言，但它在開發機的 python 版本上恆綠、抓不到這一面；新案 test_gate_id_survives_docstring_dedent 改以合成 __doc__ 釘死、與跑測版本無關。★取證：舊 regex 下新測案紅（gate_id() 回 None）→ 修正後 docsync test 250 案 OK、check 零漂移、lint 0 錯 0 警 0 跳過（機密佈妥後 GT-07 由具名跳過轉為實值比對腿）、bash tools/bootstrap.sh rc=0／35 項 ✓／警告 0。零漂移即逐 byte 證明產出與既有生成檔相同＝還原原意、非改變行為。★併記一筆據實觀察：前一批 maint-backlog-40-39-37 的簿記顆 3173f4f 無對應 close_bookkeeping perf 事件（RL-0053 第四步漏做），牆鐘依 RUNBOOK §12b 無法回溯量測，故不補造、僅此記載。★兩筆 LESSONS：LL-00013 本坑、LL-00014 等長替換同秒還原使 pyc 判仍有效而沿用舊碼。★實作顆 2487507。

### 2026-09-07｜misc｜governance｜maint-backlog-40-39-37

★BL-00039 與 BL-00037 為部分收（子項）、故不入 backlog_done、改以條文改列承載：BL-00039 刪①留②（探針 hops 口徑，觸發欄不變＝下次動 tools/orchestration/** 或 000-r3 發射前）；BL-00037 刪③留①②（pre-push 接線、bootstrap 名冊）。★BL-00037③ 的關鍵發現：只在 .githooks/pre-commit 加 `-e 'rust-api'` 觸發字面是假腿——`wire-schema.py check --staged-gate` 原在 base-web gitlink 未 staged 時回 not-staged 直接 rc 0，rust-api pin bump 一次都跑不到；故同批把單側判定抽成 _pin_range_verdict(sub, pathspecs, …)、新增 staged_snapshot_verdict（rust-api pin 區間 × server/tests/fixtures/wire-schema.json）、cmd_check 改兩側合判（皆零變動才跳過）。取「pin 區間 × 快照 pathspec」而非「只要 rust-api staged 就重抽」＝避免每次 pin bump 都跑 npx 撞 pre-commit 雙錨門檻。四個新測試案含 pathspec 對 OUTPUT_PATH 的釘值（防打錯＝區間 diff 恆空＝恆判 no-change＝假腿）；變異實測兩發皆紅（pathspec 打錯／收窄退回單側）。★BL-00039① 的斷言分兩處：UNIT／FEATURE／START_LOG 上提 _sk_head.js（兩形共用、_sk_review.js 同判準三行刪去），CONTEXT／ALLOWED_BLOCK 置於 _sk_main.js——TDD 拼接序 vars→head→allowed→rules→context→prompts→cycle→main，在 head 取值會落在 const 暫時死區（typeof 亦拋 ReferenceError）；main 早於任何 spawn、零派發性質不變。harness 三反例取「值被清空」而非「常數名打錯」：後者在頂層引用處即 ReferenceError（已 fail-loud），前者才是過得了 guard 的靜默洞（ALLOWED_BLOCK 空＝fix agent 拿到沒有允許清單的 prompt、六件套⑥ 靜默失效）。★BL-00040 另處置 errata 兩處失效引用（§4.2 與 Q12 之「§5.2 真相表」）；殘留破口（「型」欄本身透露應查無與否）逐句揭露、刻意不另設閘。r2 判分結果住報告 §3.2 彙總形、刪欄不損可重算性。★現在式面同步：案數十五→十八（README、tools/orchestration/README、RUNBOOK §12、P-C4-E3、P-E7）、wire-schema 雙側觸發（RUNBOOK §12 兩列、README 兩處、test_hook_wiring SEGMENTS＋一反例）；史料面（reviews／MILESTONES／brainstorms 正文）依 RL-0048 不動，ADR-00019 body 依「as-built 不回灌 ADR」不改。★自驗：docsync test 249／check 零漂移／lint 0 錯 0 警 0 跳過／wire-schema 31 案／五支工具自測 rc 0／三支入庫範例組裝三道自檢綠（harness-test 十八案 ×2 模式、harness-review 九案 ×2 支）。實作顆 4556778。

### 2026-09-07｜misc｜governance｜000-r2-doc-governance

報告＝docs/reviews/20260907-doc-governance.md（248 行）；計畫＝docs/brainstorms/000-r2-doc-governance.md（v0.3、§11 十題＋grilling 兩輪 Q11～Q19 全裁定）。對象＝分支 @ 7b734e1（開出點 rev6-admin-root @ c097c48）。五支 run：A 探索 wf_57ff815d-4c9（18）／B1 wf_2ed23344-8e1（22）／B2 wf_415d9f87-8d7（22）／C 補漏 wf_4bb5c3e8-cfc（9）／D 修單 wf_f3bbe7d9-c4a（14）；四處 porcelain 全程零寫入。停點① user 逐題親決六題：主張閘①補既有閘腿不占閘數／L2-06①例外①含註解＋憲法 Amendment／L11-03①保留碼承載點改字面／C3-3②won't-fix ADR／L9b-01①§III 判準句併入 Amendment／L10-04①RL-0042 第二具名例外。停點② user 同意 merge --no-ff。final holistic review 零新 finding（八項對賬全綠、逐項列於 merge commit 訊息＝RL-0073 承載處③）。★方法論兩處自我揭露：①題文可比性——附錄 C 五題原誤回退 r1 計畫 §5 簡寫版而非 r1 實問版，主線逐字比對三源後更正、報告 §3.5 揭露並同列「全 25 題」與「可比子集 20 題」兩口徑（0.48→0.76 與 0.45→0.70、同向）②探針隔離——否定對照題庫連同真相答案欄住 tracked 計畫檔、冷啟動前提無保護（轉 BL-00040，r3 起真相改烤 grader prompt）。★GT-03 之 BL 存在性腿採在途兩態（號 ≤ max(誕生集)＝憑空／回收號 ERROR、> max＝配號已發而收單未落帳之在途窗口 WARN）：偏離計畫 §4.7 條文 A 之單態設計、由 implementer 升級、主線裁定接受——理由是條文 A 與 RL-0053（簿記排在 merge 之後）在同一輪內互斥，單態會把本輪自身的收尾 commit 擋死；殘留破口（落在 max(誕生集) 與帳本 next-id 之間的打錯號只 WARN）已載於程式 docstring，該區間之外由 GT-05 next 單調腿接手。docsync test 178→249；RULES-VERSION 741ae996dc61→89ec0586d6a9；BACKLOG 8→16→15（淨 +7）。

### 2026-09-07｜review｜doc-governance

獨立輪 000-r2（第二輪 doc-governance；對象＝分支 000-r2-doc-governance @ 7b734e1、開出點 rev6-admin-root @ c097c48）。五支 Workflow、85 支 agent 零錯零 null：A 探索 18（12 lens＋6 探針、findings 95）／B1 22（批 1～11、54 筆兩鏡三態）／B2 22（批 12～16 兩鏡＋6 探針 grader→refuter＋完整性 critic）／C 補漏 9（critic 三缺口 lens＋inline 兩鏡）／D 修單 14（U-r2-gates）。四處 porcelain 全程零寫入。findings 實得 102＝A 去重後 77＋探針衍生 13＋C 12；三態 confirmed 88／refuted 12／uncertain 2（守恆）。★本欄 total 81 為帳面條目數（同 r1 先例）：88 confirmed 中 15 筆依 r1 Q11 同類合併為 8 條 BL、4 筆立 ADR、其餘 69 筆為修。主線逐 confirmed 重跑證據命令：零輸出 0 筆、6 筆非唯讀形人工補驗全數成立。修之落地＝739354a／b2e5b75／c3effa6（主線直改 51）＋0d91224（RL-0042 第二具名例外）＋598b806（D run 17）；BL＝979c046；ADR＝2b4d3f6（憲法 Amendment 1.1.0→1.2.0：ADR-00022 例外①含註解／ADR-00023 保留碼承載點／ADR-00024 §III 判準句）與 4f7c8b1（ADR-00025 won't-fix：ADR 方向不設反向存在性不變式）。★BL-00003 閘補腿群三腿全落地：GT-03 BL 引用存在性腿（events-only 不變式；帳本側兩態＝憑空／回收號 ERROR、在途落帳 WARN）、SKIP 分類（Day-1 型八處改 ERROR、環境型三處改 ADR-00019 具名跳過＋gates.ENV_SKIPS 登記＋GT-12 登記腿）、主張閘（user 停點① 拍板『補既有閘腿、不占閘數』＝GT-12 數值／SHA 主張腿＋GT-05 ID 引用存在性腿）；閘數維持 12。docsync test 178→249 案。第四指標首次輪間比較：≤3 跳比例 r1 0.48→r2 0.76；排除五題題文不可比者之可比子集 20 題亦由 0.45→0.70，兩口徑同向；找不到與答錯兩輪皆 0、否定對照答錯 0。題文可比性偏差已於報告 §3.5 揭露並更正計畫附錄 C 為 r1 實問版（r3 起完全可比）。停點① user 逐題親決六題。RULES-VERSION 741ae996dc61→89ec0586d6a9。

### 2026-09-07｜misc｜governance｜maint-backlog-7

user 拍板 2026-09-07 口徑①（三選一：①現在立 ADR 定欄、r1 回填基準、r2 起結構化入帳／②等 000-r2 跑完再立 ADR／③降級 DEFERRED）；順序理由＝欄位若在 000-r2 之後才定、r2 探針數據又只能落 notes 再靠 erratum 補。欄形＝{questions, found, detour, not_found, wrong, avg_min_hops[, negative 同形]}、只存計數不存比例（RL-0049）；算式＝≤3 跳比例 found/questions、答對率 (found＋detour)/questions；窗口＝最近一筆帶 probe 的 review 事件（更正視圖）。000-r1 基準（報告 §3 逐題表回算）：冷啟動 25 題找得到 12／繞路 13／找不到 0／答錯 0、hops 2.0（≤3 跳 0.48、答對 1.0）；否定對照 7 題 6／1／0／0、hops 2.14。erratum 對 review 型容許目標列原無該欄（同 adrs 型 BL-00004 先例）。語料面四案（test 174→178）、不加閘不加生成檔、閘數 12 不動。000-r2 起收單自 review 骨架 probes[].grade.grades 計數寫欄（tools/orchestration/README.md 一句）。

### 2026-09-07｜misc｜governance｜maint-backlog-21

user 拍板 2026-09-07 口徑①（三選一：①RUNBOOK §10 一句＋本事件 notes、不動憲法／ADR／②新 ADR＋憲法 Amendment 記此定性／③won't-fix ADR）。實核（五檔去整行註解、去行尾空白、去空行後 diff rev5 凍結樹 rust-api 92919b9）：migration/src/main.rs 6 行＝變數 file_path→path；migration/src/lib.rs 6 行＝模組名 rev5:m001→m0001、rev5:m002→m0002；entity/src/lib.rs、migration/Cargo.toml、entity/Cargo.toml 各 0 行——與條目原述一致（001 刀收單 be69543 訊息載 main.rs 一項）。定性＝40 行 env 橋接與 manifest 座標「承形自寫」之自然收斂、非例外射程擴張；ADR-00009「日後任何第 18 檔要拷＝新 Amendment」尾句仍成立、五檔不計入。純文件變更、無測試面；驗證＝docsync check 零漂移／lint 0/0/0／pre-commit 全綠。

### 2026-09-07｜misc｜governance｜maint-backlog-25

user 拍板 2026-09-07 口徑①（三選一：①去註解 diff＋具名例外 allowlist、ADR-00009 不動／②新 ADR supersede ADR-00009 改條件①措辭／③維持人工）。實核更正：BL-00025 原述「5 支整檔拷貝」失準——src 四支去註解後全等、adapter.rs 差三對非註解行（兩個 #[ignore] 字串換 rev6 座標、一行 mysql 連線字面改 format! 執行期串接＝RL-0054）、Cargo.toml 只差 # 檔頭註解、examples 四檔全等；ADR-00009 條件①（去註解逐位元）只鎖例外②故不動，例外①口徑住 vendored.py docstring＋本事件。腿＝差異只准逐行替換且逐對消費 ALLOWLIST（多一行／少一行／對不上／同形多於登記／allowlist 漂移／rev5 缺檔／掃描面空集合皆紅）；真 repo 10 檔、3 對消費；bootstrap 體檢 rc 0 含 3c；非治理閘、GATES.md 不動。兩坑：allowlist 落 rev5 連線字面被 betterleaks 擋→rev5 側改 sha256[:12]（RL-0054）；hook 內 git -C rust-api ls-files 讀外層 index 回空→子行程剝 GIT_*（LL-00012）。

### 2026-09-07｜misc｜governance｜maint-backlog-23

一顆 bbcf44f。承 rev5:tools/docs-sync.py TestGateWiring 乾跑案形、改為讀真 hook 的純函式檢查器（語料面案、非 GT；新段須同批入 SEGMENTS 名冊否則紅）。活體證據＝orchestration 段一正一反（直呼 .githooks/pre-commit、不 commit：範例無害改動→三支組裝＋十五案／九案／九案綠；範例模組層 SMOKE 改壞→段 rc 1 指名兩處須同值；還原 cmp 全等）；bbcf44f 之 pre-commit 全鏈 34.4s 含 selftest-docsync 168 案（hook staged 觸發、雙錨 45 內）。GT-11 抓到 hook 註解 $VAR 後接全形標點→改 ${VAR}。BL-00023 原述之「rev5 TestGateWiring 隨遷未帶進」至此補齊；maint-backlog-6 併入之編排骨架段同批收。

### 2026-09-07｜misc｜governance｜maint-backlog-6

三顆 8731bb6／9231ce9／306eea0；002 改良折入 review 骨架（升級不殺 run 精神＝null／failed 留帳續跑 status partial、RULES 塊整塊烤入＋guard 逐支斷言 RULES-VERSION、保險絲同源推導 review 每 run ≤24、結構化三態聚合供主線三分流）；dogfood run wf_2d17e389-f37（9 支、13 筆＝12 confirmed／1 refuted；修 11／BL 3 當批收掉／駁回 1）；RULES RL-0058／RL-0060 與 CLAUDE.md §2①③ 同步實況、RULES-VERSION 88e0f431b504→741ae996dc61；BL-00034 併入 BL-00023（同族一併涵蓋）、三號碼消耗、next BL-00035；tmp/001-assemble.py／002-assemble.py 由 tools/orchestration/assemble.py 取代。

### 2026-09-05｜misc｜governance

分類體檢由另一 session 完成（工作檔 tmp/check-backlog.md、gitignored）：開放 20 條分四類，user 拍板 A＋B 合併一批。主線依 CLAUDE.md §5 復核其自陳三件並全部復現屬實。
BL-00022 採 user 提出的抽取模式而非分類檔建議的搬家：新增 docs/ops/reference-src/schema-definition.md（十節齊、會前進的七節抄實體、已成史的三節留指針），specs/001-schema-baseline/data-model.md 零改動留為凍結史料。抽取相對搬家的關鍵優勢＝m0001 等三處子庫註解所述「定稿憑據＝specs/001 之 data-model」是成品出處的歷史陳述、凍結存證原地保留下仍為真，故本批維持純外層、pin 不動、不觸憲法 §I.5 例外②射程。
BL-00017 差點做錯：條目只寫「子庫腿對齊五形」，實測粗篩命中六行、全是自家刀名 001-schema-baseline——只對齊正則不共用外層 rev6 刀集豁免會整批誤紅，故改為共用外層精判。
驗證形制：判準本就正確的條目一寫即綠、不得宣稱先紅後綠，改以變異探針逐條打在對應判準腿上驗紅（_check_col 四腿、活性唯一索引兩腿、C 複合 PK、created_by 顯式驗、gate1 索引與約束節、seed_add 欄集、compare_seed 排序、audit 反向腿）；唯 archived_by 與部分新增檢查為真先紅後綠。
兩條實查更正（非處置對象）：BL-00006 原述「報告 §0 記 sha256」失準、實記 runId 與 agent 數；BL-00010 補上補償控制實驗——快照缺席時 compute_generated 抛 SnapshotError 且 check 與 lint 均不捕、pre-commit 仍擋得下，曝險面遠小於條目原述，故維持留 002 brainstorm。
本筆之 adrs 欄為 BL-00004 新增能力的首次實用（misc 收單即立 ADR 的反查左源）。

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
