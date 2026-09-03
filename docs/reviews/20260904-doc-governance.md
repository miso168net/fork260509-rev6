# 文件治理架構體檢（doc-governance、2026-09-04）

範圍＝rev6 文件治理架構（活書家族、ops 帳本、generated、README／CLAUDE.md／憲法、tools/docsync、tools/orchestration、wf-watchdog、bootstrap、hooks；deploy 只進 rev5 拷貝 lens）；對象＝`rev6-admin-root` @ 8a50ffe（獨立 review 輪 `000-r1-doc-governance`、自該 commit 開出、零 commit 下體檢；default 於體檢期間指向 328f366＝對象＋001 brainstorm 一檔，user 裁定保留、不入對象）；評估者＝三支唯讀 Workflow（全數 `opus[1m]`／`xhigh`）＋主線 Claude 滙總與親驗；拍板＝user。計畫＝`docs/brainstorms/000-r1-doc-governance.md`（§11 二十三項裁定）。

## 0. 方法與取證

| run | runId | agent 數 | 內容 | 零寫入對賬 |
|---|---|---|---|---|
| A 探索 | `wf_4a1a8dff-de0` | 14 | 10 lens（L1 事件與帳本的家／L2 權威鏈／L3 閘覆蓋／L4 生成器／L5a-b-c rev5 拷貝／L6 工作流／L7 時態鏡像／L8 活書事實）＋4 冷啟動探針；findings 99 → 主線合併 21 → 78 | 外層／base-web／rust-api／rev5 四處 porcelain 前後相同 |
| B1 驗證 | `wf_47c72e0c-6f9` | 22 | 7 批×（R-real 重現證據＋R-decided 查拍板）兩鏡三態＋4 探針×（grader→R-decided） | 同上 |
| B2 驗證 | `wf_d94b500c-f4d` | 19 | 9 批×兩鏡＋完整性 critic | 同上 |
| C 補漏 | `wf_f5a754a3-d80` | 12 | critic 缺口：C1 spec-kit 承載面／C2 infra 全型別拷貝對賬／C3 閘覆蓋率矩陣（各接兩鏡）＋C4 否定對照探針（grader→R-decided） | 同上 |
| D 修單 | `wf_7abb0ce4-1bf` | 8 | U-deploy（21 筆）／U-orch（13 筆）兩實作單元：implementer→review→fix→確認輪，允許檔清單寫死；最終審查零 blocker；主線收三筆升級 | 改動集 ⊆ 允許清單；子庫與 rev5 零改動 |

存活規則（計畫 §4.5、Q25）：兩鏡皆「確認」→confirmed；任一「駁回」→附錄 A（附兩鏡理由）；其餘→不確定、主線親自重跑證據裁定。主線另對全部 confirmed 逐筆重跑首條證據命令（寫入形黑名單、逐條 timeout）——B1 29 筆全部相符。冒煙 token：A `r1體檢-9c4e`、B1 `r1驗證B1-3e7d`、B2 `r1驗證B2-51a9`；script 住 `tmp/`（Q2；組裝器 `tmp/000-r1-assemble-find.py`、`tmp/000-r1-assemble-verify.py`）。三指標張力：本批＝治理批（misc governance），「治理批對 feature 比」分子再＋1、分母仍 0（n/a）。

## 1. findings 總表（confirmed；ID 為報告局部編號、非 ID 家族）

| ID | 嚴重度 | 類別 | file | locator | summary | 證據命令（首條） | 票 real／decided | 處置 |
|---|---|---|---|---|---|---|---|---|
| R1-001 | blocker | 閘覆蓋缺口 | `tools/docsync/events.py` | gt_03（events.py:296-328）／docs/generated/GATES.md 第10行 | GT-03 不驗 review.findings.to_backlog 的 BL 引用存在性，但 GATES.md 宣稱其守「分流引用斷鏈」 | `python3 -c " ⏎ import sys;sys.path.insert(0,'tools') ⏎ from docsync import events as ev ⏎ from docsync.common import Ctx…` | 確認／確認 | BL（BL-gate-legs） |
| R1-002 | major | 閘覆蓋缺口 | `docs/ops/BACKLOG-DEFERRED.md` | BACKLOG-DEFERRED.md 第3行／BACKLOG.md 第5行 | 帳本宣稱滯後卷「lint 一律視為仍開放」，但 GT-12 的 BACKLOG 開放 ≤25 上限只數 BACKLOG.md、不數滯後卷 | `sed -n '3p' docs/ops/BACKLOG-DEFERRED.md; sed -n '5p' docs/ops/BACKLOG.md; sed -n '359,363p' tools/docsync/gates.py; gre…` | 確認／確認 | 修 |
| R1-003 | major | 生成器缺陷 | `tools/docsync/references.py` | compute_generated（references.py:362）／gen_state（:322）；_erratu… | erratum 型的更正不套用於任何 generated 人讀面，MILESTONES／perf.md／STATE 續印被更正掉的舊 SHA | `python3 - <<'EOF' ⏎ import sys ⏎ sys.path.insert(0,'tools') ⏎ from docsync import events as ev, references as rf ⏎ text=…` | 確認／確認 | BL（BL-generators） |
| R1-004 | major | 生成器缺陷 | `tools/docsync/references.py` | gen_milestones（references.py:112） | MILESTONES 標題宣稱「新在前」，但同日事件因 stable sort 保持 append 序而呈舊在前 | `sed -n '112p' tools/docsync/references.py; sed -n '2p' docs/generated/MILESTONES.md; sed -n '6p;12p' docs/generated/MILE…` | 確認／確認 | 修 |
| R1-005 | minor | 生成器缺陷 | `tools/docsync/references.py` | gen_milestones（references.py:113）／docs/generated/MILESTONES.… | MILESTONES 的 review 列 summary 欄直出 Python dict 字面 str(findings) | `sed -n '113p' tools/docsync/references.py; sed -n '11p' docs/generated/MILESTONES.md; sed -n '100p' README.md` | 確認／確認 | 修 |
| R1-006 | minor | 生成器缺陷 | `tools/docsync/references.py` | gen_state（references.py:355-356）／docs/generated/STATE.md 第41行-… | STATE「最近事件」對 perf／review 型印空白 summary（perf 另印「—」標的），且與 MILESTONES「perf 型另居」的分面約定不一致 | `sed -n '41,44p' docs/generated/STATE.md; sed -n '355,356p' tools/docsync/references.py; sed -n '105p' tools/docsync/refe…` | 確認／確認 | 修 |
| R1-007 | major | 生成器缺陷 | `tools/docsync/references.py` | references.py:44 vs tools/docsync/gates.py:35 | STATE 數量預算表的「上限」欄取 references.py 自有硬編 12／25，與 GT-12 執行用的 gates.py 常數形成雙真源 | `grep -n '^BUDGET_GATES' tools/docsync/gates.py tools/docsync/references.py; sed -n '302,317p' tools/docsync/references.p…` | 確認／確認 | 修 |
| R1-008 | major | 生成器缺陷 | `tools/docsync/adr.py` | gen_decisions_index（adr.py:171、181）／docs/generated/DECISIONS… | DECISIONS-INDEX 的 feature 欄只自 feature_close.adrs 反查，misc 型收單所立的 ADR 一律落到硬編字面「輕量軌」 | `grep -n '輕量軌' tools/docsync/adr.py; grep -c '輕量軌' docs/generated/DECISIONS-INDEX.md; grep -n 'ADR-00003' docs/ops/events…` | 確認／確認 | BL（BL-generators） |
| R1-009 | minor | 事件無家 | `tools/docsync/events.py` | EVENT_SCHEMAS["misc"].optional（events.py:34）；實例＝docs/ops/eve… | misc.workflow 欄零渲染面零指標消費，行 2 已有實資料「000-w1-governance-tooling」無任何人讀出口 | `grep -rn 'workflow' tools/docsync/*.py; grep -c '000-w1-governance-tooling' docs/generated/MILESTONES.md docs/generated/…` | 確認／確認 | BL（BL-event-fields） |
| R1-010 | minor | 事件無家 | `tools/docsync/events.py` | EVENT_SCHEMAS（events.py:30、34、38、42） | feature_close.kind／feature_close.spec_supersessions 與非 perf 型的 notes 欄皆零渲染面零指標消費 | `grep -rn 'spec_supersessions\｜"kind"' tools/docsync/references.py tools/docsync/adr.py; grep -n 'notes' tools/docsync/re…` | 確認／確認 | BL（BL-event-fields） |
| R1-012 | minor | rev5拷貝失效 | `docs/brainstorms/000-doc-architecture.md` | §4.3 表後「events schema（rev6）」段（000-doc-architecture.md 第298行） | 啟動書稱 feature_close＝「rev5 十一欄＋window」，rev5 實為 required 10 欄／全欄 13，任一口徑皆不等 11 | `sed -n '298p' docs/brainstorms/000-doc-architecture.md; sed -n '137,152p' ../fork260509-rev5/tools/docs-sync.py; sed -n …` | 確認／確認 | none |
| R1-013 | minor | 生成器缺陷 | `tools/docsync/references.py` | gen_state（references.py:340）／tools/docsync/__init__.py:21 | STATE「## git」的 default branch 欄取硬編常數 DEFAULT_BRANCH，非自 git 或任一真源檔讀 | `grep -n 'DEFAULT_BRANCH' tools/docsync/__init__.py tools/docsync/references.py; sed -n '4,6p' docs/generated/STATE.md; g…` | 確認／確認 | 修 |
| R1-015 | major | 活書事實 | `README.md` | ## 這裡的文件系統怎麼運作（30 秒版）第 1 點（README.md 第66行） | README 三種材質句把機器生成面寫成「docs/generated/ 與 _sk_rules.js」，漏 ADR-00005 立的例外註冊兩件，與同檔第 20／95 行自相矛盾 | `python3 -c "import sys; sys.path.insert(0,'tools'); from docsync.references import GENERATED_FILES; print(len(GENERATED_…` | 確認／確認 | 修 |
| R1-016 | major | 閘覆蓋缺口 | `docs/generated/GATES.md` | 表 GT-01 列（GATES.md 第8行）之「掃描面」欄；真源＝tools/docsync/gates.py:98 do… | GT-01 名冊掃描面欄漏列例外註冊兩件，與 GENERATED_FILES 12 檔的實際掃描面不符 | `sed -n '8p' docs/generated/GATES.md && sed -n '93,99p' tools/docsync/gates.py && python3 -c "import sys; sys.path.insert…` | 確認／確認 | 修 |
| R1-017 | major | 權威鏈矛盾 | `docs/ops/RULES.md` | 全表（RL-0001～RL-0073）；對照 tools/docsync/adr.py:74 之 `rule=RL-00… | GT-04 宣稱守 RL-0047（權威鏈），但 RULES 全表無「ADR accepted 後 body 不可變／supersede 對稱／禁刪除」條——該規範在規則層無家 | `grep -n "不可變\｜supersede\｜翻案" docs/ops/RULES.md; echo "RC=$?"; sed -n '70,80p' tools/docsync/adr.py; sed -n '11p' docs/ge…` | 確認／確認 | 修 |
| R1-018 | minor | 閘覆蓋缺口 | `docs/generated/GATES.md` | 表 GT-08 列（GATES.md 第15行）之「守哪條 RULES／ADR」與「拿掉會壞什麼」欄；真源＝tools/do… | GT-08 名冊宣稱守 RL-0049 且拿掉會「可超上限」，但 gt_08 實作只查 source／scope／≤2 行／LESSONS 對賬，上限腿在 GT-12 | `sed -n '15p' docs/generated/GATES.md; sed -n '86,118p' tools/docsync/rules.py ｜ grep -n "rule=\｜breaks-if-removed\｜上限\｜s…` | 確認／確認 | 修 |
| R1-019 | major | 檢索性 | `tools/wf-watchdog.py` | tools/wf-watchdog.py:51、:60、:731 | 看門狗三處引「CLAUDE.md §9」，但 rev6（與 rev5）CLAUDE.md 只有 §1～§7——實際所指是 user 私有全域 CLAUDE.md | `grep -n "CLAUDE.md §9" tools/wf-watchdog.py; grep -n "^## " CLAUDE.md` | 確認／確認 | 修 |
| R1-024 | minor | 檢索性 | `CLAUDE.md` | 檔頭第 5 行（引言段「引 rev5 帳本一律 `rev5:` 前綴；rev5 四本帳不遷入、唯讀引用（RL-0046／… | CLAUDE.md 為「四本帳不遷入、唯讀引用」引 RL-0065，語意不符——RL-0065 講實作參照 rev5 碼，禁寫入是 RL-0064 | `sed -n '5p' CLAUDE.md; sed -n '74,75p' docs/ops/RULES.md; grep -n "四本帳不遷入" docs/arc42/02-architecture-constraints.md` | 確認／確認 | 修 |
| R1-026 | minor | 生成器缺陷 | `tools/docsync/gates.py` | gates.py:407（gen_gates_md） | GATES.md Day-1 豁免表的「解除謂詞」欄是硬編字串「檔／事件存在（見 gates.py）」，不由 Day1Exemption 逐筆推導 | `grep -n "檔／事件存在" tools/docsync/gates.py docs/generated/GATES.md` | 確認／確認 | 修 |
| R1-027 | major | 閘覆蓋缺口 | `tools/docsync/gates.py` | DAY1_EXEMPTIONS（gates.py:83-85）對 7 處自稱 Day-1 的 SKIP 分支 | 七個訊息自稱 Day-1 的 SKIP 分支未登記於 DAY1_EXEMPTIONS，掃描面回歸為空時只出 WARN 不出 ERROR，與 RL-0051「掃描面空集合即紅」及啟動書 §4.6 逐筆登記不符 | `grep -n "Day-1；" tools/docsync/*.py; sed -n '/^DAY1_EXEMPTIONS/,/^}/p' tools/docsync/gates.py` | 確認／確認 | BL（BL-gate-legs） |
| R1-028 | minor | 活書事實 | `README.md` | README.md 第69行「## 這裡的文件系統怎麼運作（30 秒版）」守門列（同型：docs/ops/RUNBOOK.m… | README 與 RUNBOOK 稱 docsync lint 只跑 GT-02～GT-12，實際 ROSTER 含 GT-01、lint 跑滿十二閘 | `grep -n "GT-02～GT-12" README.md docs/ops/RUNBOOK.md; python3 -c "import sys; sys.path.insert(0,'tools'); from docsync im…` | 確認／確認 | 修 |
| R1-042 | major | rev5拷貝失效 | `deploy/grafana-provisioning/dashboards/json/backend-msg-dict.json` | line 4／30／42（三處 description／content 檔頭句） | backend-msg-dict.json 三處宣稱由 tools/docs-sync.py generate 產出且差異受 pre-commit check 攔下，但 rev6 無該工具、該檔亦不在 GENERATED_FILES | `grep -on 'tools/docs-sync.py' deploy/grafana-provisioning/dashboards/json/backend-msg-dict.json; ls tools/; ls tools/doc…` | 確認／確認 | 修 |
| R1-043 | major | rev5拷貝失效 | `deploy/backup-db.py` | line 16／37（§6）；line 66／79／197／246／396／714（§6.2） | backup-db.py 六處引 RUNBOOK §6.2、兩處引 RUNBOOK §6，但 rev6 RUNBOOK 只有兩行的 ## 6、無任何 ### 6.x 子節 | `grep -n 'RUNBOOK §' deploy/backup-db.py; grep -n '^## 6\.\｜^### 6\.' docs/ops/RUNBOOK.md; sed -n '34,36p' docs/ops/RUNBO…` | 確認／確認 | 修 |
| R1-044 | major | rev5拷貝失效 | `deploy/generate-age-key.sh` | line 4／10／12／21／65／74／140／143（§15.2）；line 12／20（§15.3）；line … | generate-age-key.sh 引 RUNBOOK §15.3／§15.5（rev6 無此節）與 §15.2 的「步驟 1 註記／步驟 3~4／末條」（rev6 §15.2 僅一句指針），其中三處是印給 operator 的執行期訊息 | `grep -n '§15' deploy/generate-age-key.sh; grep -n '^## 15\｜^### 15' docs/ops/RUNBOOK.md; sed -n '109,115p' docs/ops/RUNB…` | 確認／確認 | 修 |
| R1-045 | major | rev5拷貝失效 | `deploy/preflight-secrets.py` | line 292～293（佔位值 WARN 分支的兩行 stdout） | preflight-secrets.py 印給 operator 的「填真值走 RUNBOOK §7 對應列」在 rev6 落空——rev6 RUNBOOK §7 只有取值片段抬頭、十三機密對照表已搬到 deploy/secrets/README.md | `sed -n '288,294p' deploy/preflight-secrets.py; sed -n '38,47p' docs/ops/RUNBOOK.md` | 確認／確認 | 修 |
| R1-046 | major | rev5拷貝失效 | `deploy/decrypt-secrets.py` | line 608（預告行 stdout）；line 758（.new 警示 stderr） | decrypt-secrets.py 兩處 operator 訊息指向 RUNBOOK §15.2「失敗訊息判讀」與「RUNBOOK 輪替程序」，rev6 §15.2 為一句指針、§15 無輪替程序實文 | `sed -n '604,609p;754,760p' deploy/decrypt-secrets.py; sed -n '109,116p' docs/ops/RUNBOOK.md` | 確認／確認 | 修 |
| R1-049 | major | rev5拷貝失效 | `deploy/secrets/README.md` | 「佔位值黑名單」節（line 91～96、116～123）與十三機密對照表消費服務欄 | secrets/README.md 以現在式陳述 rust-api／migration／reaper 的 CHANGE-ME 前綴守衛與消費關係，但 rev6 rust-api 全樹只有 3 個檔、無任何該等實作 | `sed -n '91,96p;116,120p' deploy/secrets/README.md; git -C rust-api ls-files; grep -rn 'CHANGE-ME' rust-api/` | 確認／確認 | 修 |
| R1-050 | minor | rev5拷貝失效 | `deploy/secrets/README.md` | line 73（十三機密對照表 smtp_password 列） | secrets/README.md 的 smtp_password 列引「填法依 RUNBOOK Gmail 節」，rev6 RUNBOOK 全檔零個 Gmail 標題 | `grep -n 'Gmail' deploy/secrets/README.md docs/ops/RUNBOOK.md; grep -n 'Gmail' ../fork260509-rev5/docs/ops/RUNBOOK.md` | 確認／確認 | 修 |
| R1-051 | minor | rev5拷貝失效 | `deploy/grafana-provisioning/alerting/rules.yml` | line 253（⑧ throttle-degraded 的 14 label 註解） | rules.yml 引「判讀口徑見 RUNBOOK Gmail 節」，rev6 RUNBOOK 無 Gmail 標題 | `sed -n '250,255p' deploy/grafana-provisioning/alerting/rules.yml; grep -c 'Gmail' docs/ops/RUNBOOK.md` | 確認／確認 | 修 |
| R1-052 | minor | rev5拷貝失效 | `deploy/grafana-provisioning/alerting/rules.yml` | line 1／3／536／594／651／710（契約指針） | deploy/ 觀測與 nginx 面共 11 處以 specs/rev4:NNN-…/contracts/… 或裸 contracts/… 宣告契約來源，rev6 無 specs/ 目錄、也無這些契約檔的家 | `grep -rn 'contracts/' deploy/ ｜ grep -v __pycache__ ｜ grep -v dashboards/json; ls specs/` | 確認／確認 | 修 |
| R1-053 | minor | rev5拷貝失效 | `deploy/sops.sh` | line 14／16（rev4:P1.2 契約要點註） | sops.sh 兩處引 RUNBOOK §15.7「步驟 1／步驟 3」的手動 wrapper 正規化片段，rev6 RUNBOOK 無 15.7 節 | `grep -n '§15.7' deploy/sops.sh; grep -n '^### 15' docs/ops/RUNBOOK.md; sed -n '107p' docs/ops/RUNBOOK.md` | 確認／確認 | 修 |
| R1-054 | minor | rev5拷貝失效 | `deploy/setup-reaper-role.py` | line 10（分工段檔頭） | setup-reaper-role.py 以無前綴的「data-model §5」宣告 migration 與腳本的分工來源，rev6 無 data-model.md 可解析 | `sed -n '10,12p' deploy/setup-reaper-role.py; find . -name 'data-model*.md' -not -path './.git/*'` | 確認／確認 | 修 |
| R1-055 | minor | rev5拷貝失效 | `deploy/loki-config.yml` | line 2（檔頭第二行） | loki-config.yml 以無前綴的「data-model §7」宣告 72h 保留期來源，rev6 無 data-model.md 可解析 | `sed -n '1,3p' deploy/loki-config.yml; find . -name 'data-model*.md' -not -path './.git/*' ｜ wc -l` | 確認／確認 | 修 |
| R1-057 | major | rev5拷貝失效 | `tools/wf-watchdog.py` | tools/wf-watchdog.py:295,703 | wf-watchdog.py 兩處引「提案 §5」作為行為契約出處，該提案檔在 rev6 repo 不存在 | `grep -n '提案 §5' tools/wf-watchdog.py; find . -maxdepth 3 -name '*提案*' -not -path './.git/*' ｜ wc -l` | 確認／確認 | 修 |
| R1-058 | major | rev5拷貝失效 | `tools/bootstrap.sh` | tools/bootstrap.sh:26,41,156 | bootstrap.sh 三處（含兩則 die 處置訊息）指向 README-rev6-handoff，該檔在 rev6 repo 不存在 | `grep -n 'README-rev6-handoff' tools/bootstrap.sh; grep -rln 'README-rev6-handoff' --exclude-dir=.git . ｜ wc -l` | 確認／確認 | 修 |
| R1-059 | major | rev5拷貝失效 | `tools/orchestration/EXAMPLE-dual-implementer.mjs` | tools/orchestration/EXAMPLE-dual-implementer.mjs:203,204,208… | EXAMPLE-dual 烤進 agent prompt 的驗收命令與資料源指向 rev6 不存在的工具、specs 路徑與憲法版本 | `grep -n 'docs-sync\.py\｜fork-delta-lint\.py\｜wire-schema\.py\｜specs/008-\｜憲法 1\.10\.0' tools/orchestration/EXAMPLE-dual-…` | 確認／確認 | 修（BL-00001） |
| R1-060 | major | rev5拷貝失效 | `tools/orchestration/EXAMPLE-dual-implementer.mjs` | tools/orchestration/EXAMPLE-dual-implementer.mjs:202,213 | EXAMPLE-dual 烤進 per-machine 絕對路徑與 ../fork260509-rev4/ 樹，兩者皆為 repo 外且非 rev6 環境的一部分 | `grep -n 'fork260509-rev4\｜/mnt/d/AnewSpaces' tools/orchestration/EXAMPLE-dual-implementer.mjs; grep -n '^## 7' CLAUDE.md` | 確認／確認 | 修（BL-00001） |
| R1-062 | major | rev5拷貝失效 | `tools/orchestration/EXAMPLE-single-implementer.mjs` | tools/orchestration/EXAMPLE-single-implementer.mjs:3,5,95,97… | EXAMPLE-single 十二處以「憲法島 J3／§I.7 島 J3」為施工與審查依據，rev6 憲法 §I.7 目前無任何島體 | `grep -n '島 J3\｜§I\.7' tools/orchestration/EXAMPLE-single-implementer.mjs ｜ head -6; sed -n '82p;88,92p' .specify/memory/…` | 確認／確認 | 修（BL-00001） |
| R1-064 | blocker | rev5拷貝失效 | `tools/orchestration/_sk_cycle.js` | tools/orchestration/_sk_cycle.js:21 | 可複用骨架 _sk_cycle.js 的 fixPrompt 硬編前代刀名 rev5:008-audit-settings-pages，而 README 組裝法只列 UNIT 需參數化 | `sed -n '21p' tools/orchestration/_sk_cycle.js; grep -n '_sk_cycle' tools/orchestration/README.md` | 確認／確認 | 修 |
| R1-065 | major | rev5拷貝失效 | `tools/orchestration/README.md` | ## 檔 | orchestration README 檔表漏列四支實存檔（_sk_head3.js、_sk_main3.js、cdp.mjs、harness-test-quality-only.mjs），組裝法與「拼完必跑三道」亦只認 harness-test.mjs | `ls tools/orchestration/; grep -oE '`[_A-Za-z0-9.-]+\.(js｜mjs)`' tools/orchestration/README.md ｜ sort -u` | 確認／確認 | 修 |
| R1-066 | minor | rev5拷貝失效 | `tools/orchestration/README.md` | tools/orchestration/README.md 第1行 | orchestration README 標題以「承 rev5 008 刀骨架」引前代刀號，未用 RL-0046 要求的 rev5: 冒號前綴形 | `sed -n '1p' tools/orchestration/README.md; grep -n 'RL-0046' docs/ops/RULES.md` | 確認／確認 | 修 |
| R1-068 | minor | 其他 | `tools/docsync/book.py` | tools/docsync/book.py:323 | book.py 節首註解宣稱 GT-10 帶 Day-1 豁免 GT-10.doc-skeleton-absent，該筆已自 DAY1_EXEMPTIONS 移除、GATES.md 該欄為「—」 | `sed -n '323p' tools/docsync/book.py; sed -n '83,85p' tools/docsync/gates.py; sed -n '17p;25p' docs/generated/GATES.md` | 確認／確認 | 修 |
| R1-072 | major | rev5拷貝失效 | `docs/compliance/annex-iv-mapping.md` | 導言段（L7） | 活書現在式面以 gitignored 且已不存在的 tmp/rev5-handoff/annex-iv-2e-check.md 為節號錯位判定的唯一佐證 | `grep -n 'tmp/' docs/compliance/annex-iv-mapping.md; ls tmp/; sed -n '131p' .gitignore; git ls-files tmp ｜ wc -l` | 確認／確認 | 修 |
| R1-073 | major | 權威鏈矛盾 | `docs/ops/RUNBOOK.md` | ## 16. 部署 checklist（L119） | 以 rev5:ADR 0014 單獨承載「prod 不入 roadmap」這一 rev6 scope 拍板，該 ADR 自陳射程為 rev5 roadmap、rev6 側零拍板紀錄 | `sed -n '117,119p' docs/ops/RUNBOOK.md; sed -n '3p' ../fork260509-rev5/docs/arc42/decisions/0014-prod-not-in-rev5-roadmap…` | 確認／確認 | 修 |
| R1-074 | minor | 檢索性 | `docs/ops/RUNBOOK.md` | ## 15. SOPS 機密營運 — 資產段（L106） | 離線復原鑰義務只引 rev5:B-041，而該編號是 rev5 已刪除的 BACKLOG 條目、耐久的家是 rev5:ADR 0015 子題三 | `sed -n '106p' docs/ops/RUNBOOK.md; grep -c 'B-041' ../fork260509-rev5/docs/ops/BACKLOG.md ../fork260509-rev5/docs/ops/BA…` | 確認／確認 | 修 |
| R1-075 | minor | 檢索性 | `docs/arc42/decisions/ADR-00003-constitution-1.0.0.md` | frontmatter provenance（L8）、決定段導言（L26）、承襲表 §II 列（L36）；同型另見 AD… | 創世 ADR 的 provenance 與逐條核對證據指向 gitignored 且已不存在的 tmp/ 交接包檔，新 session 無法覆核 | `grep -n 'tmp/' docs/arc42/decisions/*.md; ls tmp/` | 確認／確認 | none |
| R1-077 | major | 工作流失效 | `docs/ops/RUNBOOK.md` | docs/ops/RUNBOOK.md 第82行（§12 工具鏈速查表 harness 列） | RUNBOOK §12 的 harness 自測命令字面缺必要的 script 參數、照抄即因 readFileSync(undefined) 拋錯 | `sed -n '82p' docs/ops/RUNBOOK.md; sed -n '2,3p' tools/orchestration/harness-test.mjs` | 確認／確認 | 修 |
| R1-080 | major | 權威鏈矛盾 | `CLAUDE.md` | CLAUDE.md 第40行、42（§2 TDD 實作編排範本） | CLAUDE.md 要求每個 agent prompt 烤入對應 scope 規則塊且 code-quality review 烤入 RL-0070，但骨架與兩支 EXAMPLE 的 review prompt 零規則塊、fix prompt 用 implementer 塊 | `grep -n "RULES_FIX\｜RULES_REVIEW\｜^  RULES,\｜^    RULES,\｜_REVIEW_PROMPT = \[" tools/orchestration/_sk_cycle.js tools/or…` | 確認／確認 | BL（BL-00001） |
| R1-081 | major | 工作流失效 | `CLAUDE.md` | CLAUDE.md 第36–37行（§2 編排驅動提示詞範本首兩句） | §2 範本假設 git branch 名等同 specs 目錄名，但 speckit-specify SKILL 明言分支名不決定 spec 目錄名、兩者短名由不同步驟各自生成 | `sed -n '36,37p' CLAUDE.md; sed -n '78p' .claude/skills/speckit-specify/SKILL.md` | 確認／確認 | 修 |
| R1-082 | major | 閘覆蓋缺口 | `tools/orchestration/README.md` | tools/orchestration/README.md 第30行（組裝法「拼完必跑三道」第③道） | 組裝驗收第三道宣稱 harness 十案全過，但 harness 無任何斷言與退出碼、pre-commit 亦不跑，全過與否無機器判定 | `grep -cE "assert｜process\.exit｜throw new" tools/orchestration/harness-test.mjs; grep -c "orchestration" .githooks/pre-co…` | 確認／確認 | BL（BL-00001） |
| R1-085 | minor | 工作流失效 | `CLAUDE.md` | CLAUDE.md §2「主線看門狗」段 Monitor command 描述句 | §2 未載 wf-watchdog 冒煙 token 不可取字面 test 的限制、取到即靜默改跑自測而非監看 | `grep -c "不可取字面 test" CLAUDE.md docs/ops/RULES.md; grep -n 'cmd == "test"' tools/wf-watchdog.py` | 確認／確認 | 修 |
| R1-087 | minor | 時態鏡像 | `tools/orchestration/EXAMPLE-single-implementer.mjs` | L190／L192／L194／L199／L208／L219（另 EXAMPLE-dual-implementer.mjs… | 編排 EXAMPLE 兩檔以行號形跨檔引用（plan.md 第115行、audit.rs:708-719 等），違反 RL-0048「跨檔引用不用行號」 | `grep -n "plan.md 第115行\｜audit.rs:708-719\｜docs-sync.py:4243\｜sys_operation_log.rs:5\｜audit.rs:529-539\｜sys_operation_log.r…` | 確認／確認 | 修（BL-00001） |
| R1-088 | major | rev5拷貝失效 | `tools/orchestration/EXAMPLE-dual-implementer.mjs` | CONTEXT 段 L202～L213（另 EXAMPLE-single-implementer.mjs:186～208… | EXAMPLE 兩檔的 CONTEXT 把已改寫成 rev6 的工作區路徑與整段未標記的 rev5 事實混寫，檔內無「非 rev6 現況」聲明 | `grep -n "憲法 1.10.0\｜0079-audit\｜specs/008-audit\｜fork260509-rev4" tools/orchestration/EXAMPLE-dual-implementer.mjs ｜ cut…` | 確認／確認 | 修（BL-00001） |
| R1-090 | major | 權威鏈矛盾 | `docs/ops/RULES.md` | ## 名詞（L90） | 名詞段「現在式面」清單未含 docs/arc42/decisions/，但 book.py 的 face_of 判其為 present 面並使其受 GT-05 裸編號掃描 | `sed -n '90p' docs/ops/RULES.md ｜ cut -c1-160; sed -n '28,29p' tools/docsync/book.py; python3 -c "import sys;sys.path.ins…` | 確認／確認 | 修 |
| R1-091 | minor | 閘覆蓋缺口 | `docs/ops/RULES.md` | ## 名詞（L90） | 名詞段五面不覆蓋全 tracked 檔集：14 個 tracked 檔 face 判為 None，既非具名豁免面亦不受 GT-05 現在式面掃描 | `python3 -c "import sys,subprocess;sys.path.insert(0,'tools');from docsync.book import face_of;rels=subprocess.run(['git'…` | 確認／確認 | 修 |
| R1-092 | major | 時態鏡像 | `docs/ops/NOTES.md` | ## 現況（L4～L7） | NOTES 現況段是波 5 已完成事件的史述，與 generated 的 MILESTONES 同筆內容重複，違反 RL-0048「過去式住 git＋events」與 RL-0049「鏡像不是機器生成就是不存在」 | `grep -n "波 5 文件創世驗收" docs/ops/NOTES.md docs/generated/MILESTONES.md ｜ cut -c1-130` | 確認／確認 | 修 |
| R1-093 | minor | 檢索性 | `README.md` | 文件系統地圖（L19；對照 L26） | README 樹列 docs/ops/LESSONS/ 但該目錄不存在，且未如同樹的 specs/ 標「首刀時出現」，地圖列項的存在性標註不一致 | `sed -n '12p;19p;26p' README.md ｜ cut -c1-120; ls -d docs/ops/LESSONS; sed -n '32p' tools/docsync/gates.py` | 確認／確認 | 修 |
| R1-095 | major | 活書事實 | `docs/process/P-E6-quality-scenarios.md` | ### 品質屬性定義（L24；另 docs/arc42/11-risks-and-technical-debt.md 第2行… | 活書家族「現況」欄手寫 GATES.md Day-1 表的可漂移值「豁免一筆」，GT-08 解除後即靜默失真且無機器守 | `sed -n '23,26p' docs/process/P-E6-quality-scenarios.md ｜ cut -c1-150; sed -n '4p;25p' docs/generated/GATES.md; sed -n '2…` | 確認／確認 | 修 |
| R1-096 | major | 時態鏡像 | `docs/arc42/05-building-block-view.md` | docs/arc42/05-building-block-view.md 第21行（連帶 docs/c4/C4-L2-con… | compose service 總數「17」手寫在三處活書、無閘守數字，新增或移除 service 時三處靜默過期 | `grep -rn '17 個 service\｜17 節點' docs/arc42 docs/c4; grep -n '節點 ⊇ compose 三檔 services' tools/docsync/book.py` | 確認／確認 | 修 |
| R1-098 | minor | 活書事實 | `docs/arc42/05-building-block-view.md` | §5.1 表 `deploy/` 列（:17）、`docs/` 列（:19）；§5.2 base-web 條（:25） | §5 白盒枚舉三處與實存樹不齊：deploy 漏 loki-config.yml、docs 漏 brainstorms 與 reviews、base-web 第二層漏 pnpm workspace packages/ | `sed -n '17p;19p;25p' docs/arc42/05-building-block-view.md; ls docs; ls base-web/packages ｜ tr '\n' ' '; grep -n 'loki-co…` | 確認／確認 | 修 |
| R1-C101 | blocker | 工作流失效 | `CLAUDE.md` | §2 feature 工作流：L31（「specify 必手動起手……否則 feature-branch pre-hoo… | §2 把 git 分支名當作 feature 身分的真源，但 spec-kit 1.0.3 的分支名與 specs/ 目錄名由兩條互不相干的路徑各自生成、下游一律改用 machine-local 的 .specify/feature.json 找回目錄，三處陳述皆無承載機制保證。 | `sed -n '31p;36p;37p' CLAUDE.md; grep -n 'not\*\* dictate\｜are independent\｜next available 3-digit\｜without relying on gi…` | 確認／確認 | 修 |
| R1-C102 | major | 檢索性 | `README.md` | 「文件系統地圖」L26 `specs/<NNN>-<feature-name>/` 一列；連同 CLAUDE.md §2… | 「feature 分支由誰建、NNN 序號怎麼算」這條刀前必備事實在 rev6 現在式面完全無家：README／CLAUDE.md／RUNBOOK／RULES 對 create-new-feature-branch.sh、before_specify hook、speckit-g… | `grep -rn 'create-new-feature\｜before_specify\｜speckit-git-feature\｜序號怎麼算\｜分支由' README.md CLAUDE.md docs/ops/RUNBOOK.md d…` | 確認／確認 | 修 |
| R1-C103 | major | 閘覆蓋缺口 | `CLAUDE.md` | §6 不要做的事：L32／L137「絕不用 spec-kit implement 指令」 | §6 名單只點名 implement，但 10 支核心 speckit 技能全數 `disable-model-invocation: false`（可被模型自動叫用），其中 converge／checklist／taskstoissues／constitution 在 rev6… | `grep -l 'disable-model-invocation: false' .claude/skills/*/SKILL.md ｜ sed 's｜.claude/skills/｜｜;s｜/SKILL.md｜｜' ｜ tr '\n' …` | 確認／確認 | 修 |
| R1-C104 | minor | 權威鏈矛盾 | `docs/ops/RULES.md` | RL-0042（表列第 52 行） | RL-0042 宣告「一切書面產物……commit 訊息一律 zh-TW」且 scope 含「主線」，但 ADR-00003 已拍板 spec-kit auto-commit 保留 1.0.3 出廠英文 fixed 訊息（`[Spec Kit] …`），RULES 未標此例外，形… | `sed -n '52p' docs/ops/RULES.md; sed -n '61,62p' docs/arc42/decisions/ADR-00003-constitution-1.0.0.md; grep -n 'message:'…` | 確認／確認 | 修 |
| R1-C201 | minor | rev5拷貝失效 | `.env.example` | .env.example:7,23 | 檔頭宣稱「tools/secret-value-guard.py 違反即 FAIL、guard 回 1 → .githooks/pre-commit 擋下該次 commit」，但 rev6 無此檔、pre-commit 亦無該腿；同檔又把七處消費者的「唯一權威清單」指向 rev6… | `grep -n 'secret-value-guard\｜唯一權威清單' .env.example; ls tools/; grep -n 'guard' .githooks/pre-commit; ls -d specs` | 確認／確認 | 修 |
| R1-C202 | major | 權威鏈矛盾 | `deploy/secrets_common.py` | deploy/secrets_common.py:4,10,14 | 消費者名冊把不存在的 tools/secret-value-guard 列為五消費者之一、卻漏列 rev6 真正的新消費者 tools/docsync/gates.py（GT-07 以 importlib 動態載入本檔），且宣稱「既有測試留在 tools/secret-value… | `grep -n 'secret-value-guard' deploy/secrets_common.py; sed -n '114,120p' tools/docsync/gates.py; sed -n '63p' .githooks/…` | 確認／確認 | 修 |
| R1-C203 | major | 閘覆蓋缺口 | `deploy/grafana-provisioning/dashboards/json/backend-msg-dict.json` | deploy/grafana-provisioning/dashboards/json/backend-msg-dict… | 補：三處自稱「機器生成：tools/docs-sync.py generate……嚴禁手改；差異由 pre-commit check 攔下」，但 rev6 無 tools/docs-sync.py、本檔不在 GENERATED_FILES 12 件名冊內、GT-01 掃描面不含它… | `grep -c 'tools/docs-sync.py generate' deploy/grafana-provisioning/dashboards/json/backend-msg-dict.json; sed -n '19,25p'…` | 確認／確認 | 併入 R1-042 |
| R1-C204 | minor | rev5拷貝失效 | `deploy/backup-db.py` | deploy/backup-db.py:66,79,197,246,396,714 | 補（§ref 型）：六處以裸「RUNBOOK §6.2」指引操作者，但 rev6 docs/ops/RUNBOOK.md §6 只有一段佔位文、無 6.2 子節（rev6 全檔僅有 15.2／15.4 兩個子節）；另 :80／:715 引不存在的 tools/schema-gat… | `grep -n '§6\.2' deploy/backup-db.py; grep -n '^## \｜^### ' docs/ops/RUNBOOK.md ｜ sed -n '6,8p;15,18p'` | 確認／確認 | 併入 R1-043 |
| R1-C205 | minor | 閘覆蓋缺口 | `deploy/Dockerfile.rust-api` | deploy/Dockerfile.rust-api:11-13 | 註解宣稱「pre-commit 的 rust 格式守門＝tools/rust-fmt-gate.py 即呼叫本容器」，但 rev6 無此檔、.githooks/pre-commit 無此腿、GATES.md 12 閘亦無 rust fmt 閘——讀者會以為 cargo fmt 已… | `grep -n 'rust-fmt-gate' deploy/Dockerfile.rust-api; ls tools/; grep -c 'fmt' .githooks/pre-commit; grep -c 'fmt' docs/ge…` | 確認／確認 | 修 |
| R1-C206 | major | 權威鏈矛盾 | `.gitignore` | .gitignore:38 | rev6 自寫的指針說「操作手冊承 rev5:CLAUDE.md §3（rev6 正式版待補）」，但 rev6 CLAUDE.md §3「git／submodule 操作手冊」已存在且是本代權威——此行把新 session 導向權威鏈外的 rev5 文件，且 rev5 之前的原句… | `sed -n '38p' .gitignore; grep -n '^## 3\.' CLAUDE.md; diff -u ../fork260509-rev5/.gitignore .gitignore ｜ grep '操作手冊'` | 確認／確認 | 修 |
| R1-C207 | major | rev5拷貝失效 | `deploy/alloy/alloy-config.alloy` | deploy/alloy/alloy-config.alloy:6 | 檔頭第 2 行已改為「compose project 逐代改名（rev5-admin→rev6-admin）」，第 6 行卻仍留「本機 rev3-admin 全套並行運行＝活對照」——rev6 的並行對照 stack 是 rev5（埠 2xxxx，CLAUDE.md §7），re… | `sed -n '1,7p' deploy/alloy/alloy-config.alloy; grep -n 'rev3-admin' deploy/alloy/alloy-config.alloy; grep -n '22080' CLA…` | 確認／確認 | 修 |
| R1-C210 | major | 時態鏡像 | `.sops.yaml` | .sops.yaml:1,9-11 | 首行契約源指向 rev6 不存在的 rev4:019-secrets-sops contracts/secret-pipeline.md；第 9～11 行的 rev6 自寫段仍是未執行語氣（「首把由 generate-age-key.sh 產出後填入下列 age 清單，再依 RE… | `sed -n '1,18p' .sops.yaml; grep -n 'recipient:' deploy/secrets.dev.enc.yaml` | 確認／確認 | 修 |
| R1-C212 | minor | rev5拷貝失效 | `deploy/generate-age-key.sh` | deploy/generate-age-key.sh:12,13,16,20 | 補（§ref 型）：四處以裸 §15.3（撤銷演練）／§15.5（金鑰遺失後重新加入、離線備份義務）指引操作者，但 rev6 docs/ops/RUNBOOK.md §15 只有 15.2 與 15.4 兩個子節——災難路徑的指引落空。 | `grep -n '§15\.[357]' deploy/generate-age-key.sh; grep -n '^### 15' docs/ops/RUNBOOK.md` | 確認／確認 | 併入 R1-044 |
| R1-C213 | minor | rev5拷貝失效 | `deploy/sops.sh` | deploy/sops.sh:14,16 | 補（§ref 型）：兩處引「RUNBOOK §15.7 步驟 1／步驟 3」的正規化片段，rev6 RUNBOOK §15 無 15.7 子節。 | `grep -n '§15\.7' deploy/sops.sh; grep -n '^### 15' docs/ops/RUNBOOK.md` | 確認／確認 | 併入 R1-053 |
| R1-C216 | minor | rev5拷貝失效 | `deploy/setup-reaper-role.py` | deploy/setup-reaper-role.py:72,275 | 補：:72 稱 psql 調用「沿 tools/schema-gate.py 的 exec -T 慣例」、:275 稱憑證掃描面含「tools/secret-value-guard.py」——兩支 rev5 工具在 rev6 皆不存在，掃描面實況只有 .githooks pre-… | `grep -n 'schema-gate\｜secret-value-guard' deploy/setup-reaper-role.py; ls tools/` | 確認／確認 | 修 |
| R1-C217 | minor | rev5拷貝失效 | `.gitattributes` | .gitattributes:11 | 末行 `deploy/.env.example text eol=lf` 指向不存在的路徑（rev6 與 rev5 皆只有 repo 根 .env.example），該規則掃描面恆為空集合——RL-0051「掃描面空集合即紅」的同類問題在設定檔面的表現。 | `sed -n '11p' .gitattributes; ls deploy/.env.example ../fork260509-rev5/deploy/.env.example; git ls-files ｜ grep 'env.exa…` | 確認／確認 | 修 |
| R1-C219 | minor | 檢索性 | `.claude/hooks/pre-workflow-gate.py` | .claude/hooks/pre-workflow-gate.py:6 | 腿②的依據寫成「rev6 §3.6、R2-F21」未指檔——rev6 同時有 CLAUDE.md §3（無 3.6 子節）與啟動書 docs/brainstorms/000-doc-architecture.md §3.6 兩個候選，讀者無從判定；同檔 :52 的錯誤訊息也對使用… | `sed -n '6p;52p' .claude/hooks/pre-workflow-gate.py; grep -n '^### 3\.6' docs/brainstorms/000-doc-architecture.md; grep -…` | 確認／確認 | 修 |
| R1-C301 | major | 閘覆蓋缺口 | `CLAUDE.md` | CLAUDE.md 全檔（矩陣列：GT-01*真源｜GT-05/形(裸編號)｜GT-06/形｜GT-07/機密） | CLAUDE.md 與 .specify/memory/constitution.md 是現在式面 134 檔中唯二「無任何內容型閘」的檔——GT-01 只抽 CLAUDE.md 的行數／constitution 的版本字串，GT-05／GT-06 對 CLAUDE.md 的有效… | `python3 -c 'import sys,os,re; sys.path.insert(0,"tools") ⏎ from docsync import book, common ⏎ ctx=common.Ctx(os.getcwd()…` | 確認／確認 | BL（BL-gate-legs） |
| R1-C302 | major | 閘覆蓋缺口 | `docs/ops/RUNBOOK.md` | docs/ops/RUNBOOK.md 第76行（同型：README.md 第69行、docs/process/P-E1-bou… | 三處現在式面文件稱 `python3 tools/docsync lint`＝「其餘閘 GT-02～GT-12」，但 gates.run_lint 迭代 ROSTER 且 ROSTER[0]＝gt_01，lint 實跑 GT-01～GT-12；README.md 自身行 30 與… | `python3 -c "import sys; sys.path.insert(0,'tools') ⏎ from docsync import gates ⏎ print('ROSTER 閘 id：', [gates.gate_id(g)…` | 確認／確認 | 併入 R1-028 |
| R1-C303 | major | 檢索性 | `tools/wf-watchdog.py` | tools/wf-watchdog.py:51、:60、:731 | 三處註解引用 `CLAUDE.md §9`（安全邊界不得與呼叫端同源／cap 失格形），但 rev6 repo 的 CLAUDE.md 只有 §1～§7——該 §9 實為 user 每機私有的全域 CLAUDE.md，屬 RL-0048 禁的 per-machine 引用；GT-… | `grep -n 'CLAUDE.md §9' tools/wf-watchdog.py ; grep -n '^## ' CLAUDE.md` | 確認／確認 | 併入 R1-019 |
| R1-C304 | minor | 閘覆蓋缺口 | `CLAUDE.md` | CLAUDE.md 第115行（同型：README.md 第48行） | pre-commit 全鏈雙錨門檻 45／90 秒的真源是 .githooks/pre-commit 的 PRECOMMIT_WARN_SEC／PRECOMMIT_FAIL_SEC 常數，CLAUDE.md 行 115 與 README.md 行 48 各抄一份字面；三處無任何閘… | `grep -n 'PRECOMMIT_WARN_SEC\｜PRECOMMIT_FAIL_SEC\｜雙錨' .githooks/pre-commit CLAUDE.md README.md` | 確認／確認 | 修 |
| R1-P01 | major | 檢索性（探針 P1） | `CLAUDE.md` | §2 feature 工作流「隨做隨記」條（併看 docs/ops/RULES.md RL-0053） | 「隨做隨記」清單列了 ADR／活書／LESSONS／BACKLOG／pin 五項，獨缺 NOTES「下一步」；規則層對 NOTES 的唯一更新義務是 RL-0053 的收刀簿記，因此階段 0 定稿等刀中里程碑不會刷新 NOTES——而 NOTES 是 README 入口表與 Se… | `grep -n "隨做隨記" CLAUDE.md; grep -n "NOTES" docs/ops/RULES.md ｜ cut -c1-90; git diff --stat 8a50ffe rev6-admin-root` | grader／確認 | 修 |
| R1-P02 | minor | 檢索性（探針 P1） | `tools/docsync/rules.py` | gt_08 docstring 的 breaks-if-removed 欄（渲染面＝docs/generated/GAT… | GT-08 的「拿掉會壞什麼」寫著「規則層可無來源、可超上限、教訓可不指向規則」，但數量預算實際只由 GT-12 判與報（同檔 budget_counts docstring 自陳「本閘不報上限」，gates.py 三處「超上限」finding 全掛 GT-12）；名冊敘述與程式… | `grep -n "breaks-if-removed" tools/docsync/rules.py; grep -n "本閘不報上限" tools/docsync/rules.py; grep -n "超上限" tools/docsync…` | grader／確認 | 修 |
| R1-P04 | minor | 檢索性（探針 P1） | `README.md` | 「想知道 X，看 Y」表（11 列） | 入口表無 git／submodule 操作一列；最接近的「怎麼操作（起停、機密、工具）→ docs/ops/RUNBOOK.md」把讀者送進 RUNBOOK，而 RUNBOOK §13 只有一句指路 LESSONS（現 0 筆），pin↔worktree 判方向的唯一權威（CLA… | `sed -n '87,101p' README.md; grep -n "submodule" README.md ｜ cut -c1-90; sed -n '95,97p' docs/ops/RUNBOOK.md` | grader／確認 | 修 |
| R1-P09 | minor | 檢索性（探針 P3） | `docs/generated/GATES.md` | 〈Day-1 豁免登記〉表 GT-08.lessons-absent 列「解除謂詞」欄（生成器＝tools/docsyn… | 人可讀面的解除謂詞欄印的是與逐筆無關的固定字面「檔／事件存在（見 gates.py）」，與實碼 `lambda ctx: ctx.exists(LESSONS_DIR)`（只查 `docs/ops/LESSONS/` 目錄存在、不查任何事件）不符；RL-0051「Day-1 豁免… | `sed -n '85p;406p' tools/docsync/gates.py; grep -n "^LESSONS_DIR" tools/docsync/__init__.py` | grader／確認 | 修 |
| R1-P13 | major | 檢索性（探針 P4） | `CLAUDE.md` | §2 feature 工作流 →「SDD 5 步」行之 `/speckit-specify` | 分支序號的真源（誰建分支、序號怎麼算、設定住哪）在 rev6 自家的現在式面完全缺席——CLAUDE.md／README／RUNBOOK／RULES／constitution 對 `before_specify` hook、`speckit.git.feature`、`branc… | `grep -rn "speckit.git.feature\｜before_specify\｜branch_numbering\｜create-new-feature" --include=*.md docs/ CLAUDE.md READ…` | grader／確認 | 修 |
| R1-P14 | minor | 檢索性（探針 P4） | `.claude/hooks/session-start.sh` | 「=== git 健檢 ===」段（branch／git status --short／git submodule st… | SessionStart 健檢只報本分支名、工作樹髒污與 submodule pin 方向，不報「本分支 vs default branch 領先／落後幾顆」。本輪即為活證：工作樹 000-r1-doc-governance @ 8a50ffe 落後 default rev6-a… | `grep -c "rev-list\｜rev6-admin-root\｜default" .claude/hooks/session-start.sh; git rev-list --count HEAD..rev6-admin-root;…` | grader／確認 | 修 |
| R1-P15 | minor | 檢索性（探針 P4） | `README.md` | 「## 想知道 X，看 Y」表（11 資料列） | README 兩個導覽面——「第一次來，照這個順序讀」5 步與「想知道 X，看 Y」11 列——全部是查現況／查依據向；「操作快速入口」4 條則是新機重建、治理工具、機密、dev stack 等營運命令。整份 README 沒有任何一列回答「我要開一把新刀，從哪起手」，該路徑只能… | `sed -n '/## 想知道 X，看 Y/,$p' README.md ｜ grep '^｜' ｜ cut -d'｜' -f2` | grader／確認 | 修 |
| R1-P16 | minor | 檢索性（探針 P4） | `docs/ops/RUNBOOK.md` | §12 工具鏈速查 → 表後末句「碼面閘（…）隨子庫刀進場、進場時入本表。」 | 「碼面閘不計入 GT-12 的 ≤12 治理閘預算」這條拍板只寫在史料面的啟動書 §4.2；現在式面三處承載（RULES.md RL-0052「閘 ≤12…超限只擋新增、不可調數字」、GATES.md「閘數 12／上限 12（一進一出）」、RUNBOOK §12 末句列出的八支碼… | `grep -rn "不計入" --include=*.md docs/ CLAUDE.md README.md .specify/memory/` | grader／確認 | 修 |
| R1-P17 | minor | 檢索性（探針 P4） | `docs/ops/NOTES.md` | 「## 下一步」段（首刀那一行） | NOTES「下一步」逐項點名了首刀前要消化的事（D13 刀序、blueprint-map、憲法 §I.7 島進場、BL-00002、三指標），讀起來像窮舉，卻漏了同樣卡在首刀的 BL-00001（觸發＝「首個含 Workflow script 的刀開分支時」）。兩條 BL 到期時… | `grep -o "BL-000[0-9][0-9]" docs/ops/NOTES.md docs/ops/BACKLOG.md ｜ sort ｜ uniq -c` | grader／確認 | 修 |
| R1-C4P02 | major | 檢索性（探針 C4） | `deploy/grafana-provisioning/alerting/contact-points.yml` | 檔首註解「★誠實登記（rev4:019 U6）」段（另一處同語意在 docker-compose.yml grafana… | 兩處註解宣稱佔位現值「仍可由 deploy/dev-webhook-sink.sh 的 NAME 常數＋埠＋路徑推導」，但該檔在 rev6 不存在，且 rev6 佔位值是不可達的 .invalid 保留域、根本不是 dev 收器位址——自 rev4 搬檔留下的真假述，會誘導讀者以… | `python3 tools/docsync errata dev-webhook-sink; ls deploy/; grep -n PLACEHOLDER_VALUE deploy/generate-secrets.py` | grader／確認 | 修 |
| R1-C4P04 | major | 檢索性（探針 C4） | `docs/brainstorms/000-doc-architecture.md` | §1.2 D4「新碼制」列與附錄對照表「migration 短號」列（對造＝git show rev6-admin-ro… | migration 短號的兩個史料面拍板互相矛盾且無現在式面仲裁：啟動書 D4 拍「migration `m0001`（四碼）」，而 default head 的 001-schema-baseline.md 通篇用三碼 `m001_baseline_schema`／`m002_… | `grep -n "m0001" docs/brainstorms/000-doc-architecture.md; git show rev6-admin-root:docs/brainstorms/001-schema-baseline.…` | grader／確認 | ADR |
| R1-M01 | major | 權威鏈矛盾（主線） | `.specify/memory/constitution.md` | §I.5／RULES RL-0065／啟動書 D10、§4.5 | 拷貝紀律的規則層射程只及應用碼（憲法 §I.5、RL-0065）；隨遷 infra（deploy/、hooks、骨架）整檔搬運的授權只住史料（D10／§4.5），現在式面無家 | `grep -n "拷貝\｜重打字\｜搬運" .specify/memory/constitution.md docs/ops/RULES.md CLAUDE.md README.md；grep -n "隨遷" docs/brainstorm…` | 主線 | 修 |

### 1.1 不確定（主線裁定）

| ID | real | decided | summary | 主線裁定與依據 |
|---|---|---|---|---|
| R1-099 | 確認 | 不確定 | §3.1 斷言系統對外只有 SMTP 一種外部依賴，但 obs profile 的 socket-proxy 掛 host /var/run/docker.sock、實為第二個外部系統依賴 | 主線裁定（不確定→修）：§3.1 加一子句「obs profile 另掛 host docker.sock、屬觀測層基礎設施」與 C4-L1 邊界一致 |

## 2. 事件都有家嗎——事件型 × 欄位 × 消費面矩陣（L1 lens 產出、B1 兩鏡確認；欄級判準＝Q13）

### 2.1 事件型 × 欄位 → 消費面矩陣（EVENT_SCHEMAS 五型全欄）

「消費面」只計 generated 渲染面與 §4.3 三指標；閘（GT-02／GT-03）另欄註記。粗體＝無家候選。

#### feature_close（required 11／optional 3；rev6 目前 0 筆實例）

| 欄 | 必／選 | 讀取函式 | 輸出面 | 閘消費 |
|---|---|---|---|---|
| type | 必 | gen_milestones、gen_state ev_counts、metrics | MILESTONES type 欄、STATE events 行、三指標分母 | — |
| date | 必 | gen_milestones（排序鍵＋欄）、gen_state | MILESTONES date 欄、STATE 最近事件 | — |
| feature | 必 | _target、gen_decisions_index、gt_03 | MILESTONES 標的、DECISIONS-INDEX feature 欄 | GT-03 spec.md 存在 |
| summary | 必 | gen_milestones、gen_state | MILESTONES summary、STATE 最近事件 | — |
| merge | 必 | gen_milestones | MILESTONES merge 欄 | GT-02 SHA 實證 |
| pins | 必 | 無 | **無 generated 面**（STATE pins 讀 `git ls-files -s`、非事件） | GT-02 子庫 SHA 實證 |
| adrs | 必 | gen_milestones、gen_decisions_index | MILESTONES adrs 欄、DECISIONS-INDEX feature 反查 | GT-03 ADR 檔存在 |
| arch_impact | 必 | gen_milestones | MILESTONES arch 欄 | — |
| backlog_add | 必 | metrics | STATE backlog_net | **BL 存在性零驗證** |
| backlog_done | 必 | metrics | STATE backlog_net | **BL 存在性零驗證** |
| window | 必 | 無 | **無 generated 面** | GT-02 序號＝第 k 筆 |
| notes | 選 | 無 | **無家** | — |
| kind | 選 | 無 | **無家** | — |
| spec_supersessions | 選 | 無 | **無家** | — |

pins／window 雖無渲染面，但各有實質閘消費，依判準不列無家。

#### misc（required 5／optional 4；6 筆實例）

| 欄 | 必／選 | 讀取函式 | 輸出面 | 閘消費 |
|---|---|---|---|---|
| type | 必 | 同上 | MILESTONES／STATE | — |
| date | 必 | 同上 | 同上 | — |
| summary | 必 | gen_milestones、gen_state | MILESTONES summary、STATE 最近事件 | — |
| category | 必 | _target、metrics | MILESTONES 標的、STATE 治理批比 | — |
| backlog_add | 必 | metrics | STATE backlog_net | **BL 存在性零驗證** |
| notes | 選 | 無 | **無家** | — |
| backlog_done | 選 | metrics | STATE backlog_net | 同上 |
| merge | 選 | gen_milestones | MILESTONES merge 欄 | GT-02 SHA 實證 |
| workflow | 選 | 無 | **無家（行 2 已有實資料）** | 僅非空字串驗證 |

#### review（required 5／optional 2；1 筆實例）

| 欄 | 必／選 | 讀取函式 | 輸出面 | 閘消費 |
|---|---|---|---|---|
| type／date | 必 | 同上 | MILESTONES／STATE | — |
| scope | 必 | _target | MILESTONES 標的 | GT-03 訊息 where |
| report | 必 | 無 | **無 generated 面** | GT-03 檔存在 |
| findings | 必 | gen_milestones（str(dict) 直出） | MILESTONES summary 欄（dict 字面） | GT-03 只驗 wontfix_adr、**to_backlog 零驗證**；schema 驗四鍵守恆 |
| feature | 選 | _target（優先於 scope） | MILESTONES 標的 | GT-03 格式驗 |
| notes | 選 | 無 | **無家** | — |

#### erratum（required 4／optional 1；0 筆實例）

| 欄 | 必／選 | 讀取函式 | 輸出面 | 閘消費 |
|---|---|---|---|---|
| target_line | 必 | _target | MILESTONES 標的「行 N」 | _erratum_view 定位 |
| field | 必 | 無 | **無 generated 面** | _erratum_view 選欄 |
| corrected | 必 | gen_milestones | MILESTONES merge 欄 | GT-02 SHA 實證＋覆寫 |
| reason | 必 | gen_milestones、gen_state | MILESTONES summary、STATE 最近事件 | — |
| notes | 選 | 無 | **無家** | — |

★關鍵：更正的**效果**只活在 GT-02 的視圖裡，generated 三面都讀未更正 events（見 finding 3）。

#### perf（required 5／optional 2；5 筆實例）

| 欄 | 讀取函式 | 輸出面 |
|---|---|---|
| date／kind／wall_s／rc／commit／notes | gen_reference_perf | perf.md 六欄全渲染（commit 取前 7 碼、notes 取首行） |
| type | gen_state ev_counts | STATE events 行 |

perf 不入 MILESTONES（標題明示「perf 型另居 reference/perf.md」），但**會**進 STATE 最近事件且 summary 空白（finding 6）。commit 欄無 GT-02 以外的實證面；rc 目前恆 0。


結論：五型事件型別皆有至少一個人讀面；欄級無家＝misc.workflow（已有實資料）、feature_close.kind／spec_supersessions、非 perf 型 notes（R1-009／R1-010）；BL 引用（backlog_add／backlog_done／to_backlog）三處零存在性驗證（R1-001）；erratum 更正不套用於人讀面（R1-003）；渲染缺陷四筆（R1-004～R1-006、R1-008）。

## 3. 新 session 能否檢索——冷啟動探針（15 題×3 支＋自由探索 1 支；起點＝SessionStart 三段＋CLAUDE.md 全文、只有 repo 內容；Q7／Q14）

| 探針 | 題 | grader 判定 | grader 最短 hops |
|---|---|---|---|
| P1 | 1. 現在是波幾？唯一真源是哪個檔的哪一行？ | 找得到 | 2 |
| P1 | 2. 兩子庫 pin 與 worktree HEAD 分歧時，怎麼判方向、各自怎麼處置？ | 找得到 | 1 |
| P1 | 3. rev6 對照 rev5 的 UI 兩個埠各是多少？埠的真表在哪個檔？ | 找得到 | 1 |
| P1 | 4. 要新增一條 RL 規則：改哪個檔、怎麼配號、上限是多少、哪個閘檢查？ | 繞路 | 2 |
| P1 | 5. 首刀是哪把、刀序由什麼決定？若尚未決定，哪份文件說明由誰、在哪一步決定、產出放哪？ | 繞路 | 2 |
| P1 | 15. `alert_webhook_url` 未決事項的處理步驟寫在哪一節？該節是實文 | 找得到 | 2 |
| P2 | 1. 現在是波幾？唯一真源是哪個檔的哪一行？ | 找得到 | 2 |
| P2 | 6. 在容器內跑 rust test 的標準命令與「全程 serial」紀律寫在哪？ | 找得到 | 2 |
| P2 | 7. 踩到一個坑要落 LESSONS：檔名形、frontmatter 必填欄、索引由誰產 | 找得到 | 2 |
| P2 | 8. RULES-VERSION 是什麼、由哪個命令產、哪個 hook 對賬、不符會怎樣 | 繞路 | 2 |
| P2 | 9. rev5 活書「會話狀態機（sys_token）」節在 rev6 對應到哪一節或哪 | 找得到 | 2 |
| P3 | 1. 現在是波幾？唯一真源是哪個檔的哪一行？ | 找得到 | 2 |
| P3 | 10. base-web 的基線 SHA 是多少、為什麼是它、拍板紀錄在哪？ | 繞路 | 2 |
| P3 | 11. 收刀簿記的第四步是什麼、事件型別與 kind 叫什麼、量法為何？ | 繞路 | 2 |
| P3 | 12. 目前 Day-1 豁免有哪些、解除謂詞是什麼？ | 繞路 | 3 |
| P3 | 13. 哪些檔嚴禁手改？名冊的真源在哪個程式檔？ | 繞路 | 2 |
| P3 | 14. 上一次 review 報告在哪、findings 幾筆、review 事件長什麼 | 繞路 | 2 |
| P4 | Q1: brainstorm 產出的位置與命名 | 找得到 | 1 |
| P4 | Q2: rev5 承襲候選的來源（哪些表／哪些節） | 繞路 | 2 |
| P4 | Q3: 首刀前必須先消化的事項 | 繞路 | 2 |
| P4 | Q4: 分支建立規則與序號來源 | 繞路 | 4 |
| P4 | Q5: 憲法自查九題 | 找得到 | 1 |
| P4 | Q6: rev5 對照的讀法與唯讀紀律 | 繞路 | 2 |
| P4 | Q7: 會擋你的閘與 hook | 繞路 | 3 |
| P4 | Q8: 分支建立後第一步 | 找得到 | 2 |

指標：題數 25；找得到 12／繞路 13／找不到 0／答錯 0；探針自報 hops 平均 3.7、≤3 跳比例 12/25；grader 最短 hops 平均 2.0。探針衍生 findings 25 筆→R-decided 確認 11／駁回 14（確認者入 §1、駁回者入附錄 C）。

### 3.1 否定對照探針（C4：六題 rev6 應查無或尚未拍板＋一題對照；量「自信地答錯」）

| 題 | grader 判定 | grader 最短 hops | note |
|---|---|---|---|
| Q1: rev6 要不要做 prod 部署？拍板紀錄在哪？ | 找得到 | 2 | 對照題（可答）。最短路徑僅 2 跳：grep prod 即命中 RUNBOOK §16（答案＋承襲來源），再查 DECISIONS-INDEX 確認 rev6 無自立 ADR。探針自報 5 跳，但其 path[0] 即為命中處，多出的三跳是… |
| Q2: migration 的短號（m0001 形）幾碼、怎麼配號？rev6 現在式面哪裡定義？ | 找得到 | 3 | 問句只問「rev6 現在式面哪裡定義」，答「查無＋去處 RL-0046／RUNBOOK §10」最短 2～3 跳即足；探針多走的兩跳是額外查獲三碼／四碼衝突，屬增益而非迷路。探針未把史料面 D4 的 `m0001` 當成 rev6 現況斷言… |
| Q3: `alert_webhook_url` 的收件端（哪個服務、哪個頻道）是什麼？ | 找得到 | 2 | 探針的兩層切分（Grafana contact point 名已定 vs 真實接收服務／頻道未拍板）與我的查證完全一致，且未把 rev4 註解裡的「dev 收器」當 rev6 現況——反而正確判為假述並提出勘誤。我以 `python3 to… |
| Q4: rust-api 的第一支 crate 叫什麼、已經建了嗎？ | 找得到 | 2 | 「已建了嗎」1 跳（ls-files）即硬證，「叫什麼未拍板」2 跳（arc42 §5.2）。探針自報 4 跳，含 constitution §I.5 的關鍵反混淆（例外清單≠members 清單）——這一跳有價值，正是本題最容易誤答之處，… |
| Q5: 002 刀是什麼？範圍拍板在哪？ | 繞路 | 3 | 判繞路而非找得到：探針結論正確（查無、且指出 002 連史料面都只有名字），但抵達「最近拍板點」的路徑實測超過 3 跳，且含一個隱藏跳——現在式面唯一的指針（NOTES「刀序與範圍由首刀 brainstorm 決定」）自 328f366 落… |
| Q6: reaper role 的密碼輪替週期是多久？ | 找得到 | 2 | 探針結論正確且守住了關鍵分界——明寫「本次守唯讀邊界未去 ../fork260509-rev5/ 查證，故不代 rev5 作答」，正是本題最容易誤答成「照 rev5 週期」的陷阱，未踩。一處量化瑕疵（不影響判定）：探針稱「全 repo gr… |
| Q7: 目前 LESSONS 有幾筆、最近一筆是什麼？ | 找得到 | 1 | 最短 1 跳（LESSONS.md 本身即含 next 與空表）。探針三源互證＋GT-08 第四重登記，數值與我逐項複驗完全一致，且其「無 ambiguity」判斷成立。探針把本題定位為全 repo 最佳的『尚未有』樣板（索引寫清配號三步＋… |

探針 C4 整體觀察：rev6 對「尚未拍板」的可辨識度明顯不均勻：最好的是閘層與活書層——GT-08.lessons-absent 具名帶解除謂詞、arc42 §5.2 直寫「rust-api 目前零碼；members 隨骨架刀進場」，新 session 一眼可判「已知的空」；ops 空章（RUNBOOK §7／§8／§10「隨對應刀補實文」）次之，看得出未定、卻分不出『未拍板』與『已拍板只是沒謄進來』（Q6 reaper 輪替週期就卡在這一層）。最弱的是編號家族與刀序：migration 短號的唯一拍板（啟動書 D4「`m0001` 四碼」）只住 brainstorm 史料面、且與同屬史料面的 001 brai…

探針整體觀察（四支 overall_notes 摘）：
- P1：本 repo 的檢索性整體很高：README「想知道 X，看 Y」＋CLAUDE.md 六節指針＋GATES.md 名冊三層互指，六題有五題在 ≤3 跳內拿到可引用的原文，且「唯一真源／鏡像」的標註紀律讓人不易誤信生成檔。主要缺口是跨代與跨層的最後一哩：真表只涵蓋 rev6（rev5 對照埠 2xxxx 無機器家）、指針章（RUNBOOK §15.4）自陳待補實而把讀者送進空殼、三閘分工只在 .py 裡拼得出來而名冊敘述已與程式碼輕微分叉。最需修的一處是 `docs/ops/NOTES.md`「下一步」落後於 default branch 的 001 brainstorm 定稿一個 commi…
- P2：本 repo 檢索性整體很好：README「文件系統地圖」＋「想知道 X，看 Y」表把五題中的四題在 1～2 跳內導到承載處，且「真源 vs 鏡像」幾乎每處都有回指句（NOTES 首行波標記、rev5-blueprint-map 回指 frontmatter、STATE 自述來源），沒有踩到互相矛盾的說法。唯一系統性缺口在「規則的家」與「操作手冊的家」之間：carrier=prompt 的規則（如 RL-0045 的容器內 rust test 命令）只住 RULES.md 給 agent 吃，主線或人臨時要手跑時翻 RUNBOOK §12 會撲空。次要缺口是 LESSONS 首筆落地流程只寫在…
- P3：本 repo 檢索性整體偏高：六題有五題可在 ≤3 跳內落地，靠的是「規則本體 RULES.md ＋ 機器名冊 GATES.md ＋ 生成帳 STATE/MILESTONES/perf.md」的三段式指針，加上 CLAUDE.md 大量內嵌識別字（RL-NNNN、GT-NN、D14）可直接 grep。最大的檢索斷點是**真源座標缺席**：`GENERATED_FILES`、Day-1 解除謂詞、close_bookkeeping 量法這三處，人可讀的那一面都寫「見 gates.py」「承 rev5:RUNBOOK §12.1」或根本不提檔名，逼人跨檔甚至跨代才拿得到真值。次要斷點是 `D14`…
- P4：檢索性整體偏高：CLAUDE.md §2／§7 與憲法 §IV 是密度極高的樞紐，八個需知項有六項在 ≤3 跳內落到可引用的明文，且 README 讀序、CLAUDE.md 指針、憲法檔頭三處對「九題」的指向完全一致。兩個系統性弱點：一是「我要動工」向的入口缺席——README「想知道 X 看 Y」11 列全是查現況／查依據，開刀路徑只能靠通讀 CLAUDE.md §2，而分支序號真源整個落在第三方面 `.specify/`（不在權威鏈上、四個檔才拼得出來）；二是 SessionStart 健檢只報 submodule pin 方向、不報本分支與 default 的落差，本次因此讓已在 def…

## 4. rev5 拷貝哪些要調——清冊（同路徑相似度＋四型失效引用；判準＝Q5／Q15）

相似度 pre-scan（行集合 Jaccard；共享註解／rev6 註解行；工具＝`tmp/000-r1-assemble-find.py` 的 prescan）：

#### deploy
| rev6 路徑 | rev5 對照 | 行集合 Jaccard | 共享註解／rev6 註解行 |
|---|---|---|---|
| `deploy/backup-db.py` | `deploy/backup-db.py` | 0.94 | 82／86 |
| `deploy/decrypt-secrets.py` | `deploy/decrypt-secrets.py` | 0.94 | 161／178 |
| `deploy/dev-certs/.gitkeep` | `deploy/dev-certs/.gitkeep` | 0.00 | 0／0 |
| `deploy/generate-age-key.sh` | `deploy/generate-age-key.sh` | 0.80 | 34／44 |
| `deploy/generate-dev-cert.sh` | `deploy/generate-dev-cert.sh` | 0.97 | 40／40 |
| `deploy/generate-secrets.py` | `deploy/generate-secrets.py` | 0.93 | 82／87 |
| `deploy/grafana-provisioning/alerting/contact-points.yml` | `deploy/grafana-provisioning/alerting/contact-points.yml` | 0.84 | 13／13 |
| `deploy/grafana-provisioning/alerting/notification-policies.yml` | `deploy/grafana-provisioning/alerting/notification-policies.yml` | 0.73 | 2／3 |
| `deploy/grafana-provisioning/alerting/rules.yml` | `deploy/grafana-provisioning/alerting/rules.yml` | 0.92 | 72／75 |
| `deploy/grafana-provisioning/dashboards/provider.yaml` | `deploy/grafana-provisioning/dashboards/provider.yaml` | 1.00 | 4／4 |
| `deploy/grafana-provisioning/datasources/loki.yml` | `deploy/grafana-provisioning/datasources/loki.yml` | 1.00 | 3／3 |
| `deploy/grafana-provisioning/datasources/prometheus.yml` | `deploy/grafana-provisioning/datasources/prometheus.yml` | 1.00 | 5／5 |
| `deploy/loki-config.yml` | `deploy/loki-config.yml` | 1.00 | 2／2 |
| `deploy/preflight-secrets.py` | `deploy/preflight-secrets.py` | 0.97 | 48／53 |
| `deploy/prometheus/prometheus.yml` | `deploy/prometheus/prometheus.yml` | 1.00 | 7／7 |
| `deploy/secrets/README.md` | `deploy/secrets/README.md` | 0.93 | 9／9 |
| `deploy/secrets.dev.enc.yaml` | `deploy/secrets.dev.enc.yaml` | 0.11 | 0／0 |
| `deploy/secrets_common.py` | `deploy/secrets_common.py` | 0.85 | 8／9 |
| `deploy/setup-reaper-role.py` | `deploy/setup-reaper-role.py` | 0.91 | 99／104 |
| `deploy/sops.sh` | `deploy/sops.sh` | 0.69 | 34／37 |
| `deploy/trust-model.dev.toml` | `deploy/trust-model.dev.toml` | 0.84 | 29／32 |

#### tools／hooks／orchestration
| rev6 路徑 | rev5 對照 | 行集合 Jaccard | 共享註解／rev6 註解行 |
|---|---|---|---|
| `tools/bootstrap.sh` | `tools/bootstrap.sh` | 0.29 | 9／38 |
| `tools/docsync/__init__.py` | `（rev5 無同路徑）` | — | —／3 |
| `tools/docsync/__main__.py` | `（rev5 無同路徑）` | — | —／2 |
| `tools/docsync/adr.py` | `（rev5 無同路徑）` | — | —／7 |
| `tools/docsync/book.py` | `（rev5 無同路徑）` | — | —／16 |
| `tools/docsync/common.py` | `（rev5 無同路徑）` | — | —／9 |
| `tools/docsync/events.py` | `（rev5 無同路徑）` | — | —／8 |
| `tools/docsync/gates.py` | `（rev5 無同路徑）` | — | —／18 |
| `tools/docsync/references.py` | `（rev5 無同路徑）` | — | —／14 |
| `tools/docsync/rules.py` | `（rev5 無同路徑）` | — | —／8 |
| `tools/docsync/tests/__init__.py` | `（rev5 無同路徑）` | — | —／0 |
| `tools/docsync/tests/test_adr.py` | `（rev5 無同路徑）` | — | —／1 |
| `tools/docsync/tests/test_book_form.py` | `（rev5 無同路徑）` | — | —／2 |
| `tools/docsync/tests/test_book_ids.py` | `（rev5 無同路徑）` | — | —／4 |
| `tools/docsync/tests/test_book_refs.py` | `（rev5 無同路徑）` | — | —／1 |
| `tools/docsync/tests/test_common.py` | `（rev5 無同路徑）` | — | —／1 |
| `tools/docsync/tests/test_events.py` | `（rev5 無同路徑）` | — | —／2 |
| `tools/docsync/tests/test_gates.py` | `（rev5 無同路徑）` | — | —／1 |
| `tools/docsync/tests/test_hook_gate.py` | `（rev5 無同路徑）` | — | —／1 |
| `tools/docsync/tests/test_references.py` | `（rev5 無同路徑）` | — | —／4 |
| `tools/docsync/tests/test_rules.py` | `（rev5 無同路徑）` | — | —／3 |
| `tools/orchestration/EXAMPLE-dual-implementer.mjs` | `tmp/wf-templates/008/EXAMPLE-dual-implementer.mjs` | 0.69 | 3／5 |
| `tools/orchestration/EXAMPLE-single-implementer.mjs` | `tmp/wf-templates/008/EXAMPLE-single-implementer.mjs` | 0.73 | 3／5 |
| `tools/orchestration/README.md` | `tmp/wf-templates/008/README.md` | 0.57 | 4／6 |
| `tools/orchestration/_sk_cycle.js` | `tmp/wf-templates/008/_sk_cycle.js` | 0.95 | 2／3 |
| `tools/orchestration/_sk_head.js` | `tmp/wf-templates/008/_sk_head.js` | 1.00 | 0／0 |
| `tools/orchestration/_sk_head1.js` | `tmp/wf-templates/008/_sk_head1.js` | 1.00 | 0／0 |
| `tools/orchestration/_sk_head3.js` | `tmp/wf-templates/008/_sk_head3.js` | 1.00 | 0／0 |
| `tools/orchestration/_sk_main.js` | `tmp/wf-templates/008/_sk_main.js` | 1.00 | 1／1 |
| `tools/orchestration/_sk_main1.js` | `tmp/wf-templates/008/_sk_main1.js` | 1.00 | 1／1 |
| `tools/orchestration/_sk_main3.js` | `tmp/wf-templates/008/_sk_main3.js` | 1.00 | 1／1 |
| `tools/orchestration/_sk_rules.js` | `tmp/wf-templates/008/_sk_rules.js` | 0.00 | 0／1 |
| `tools/orchestration/cdp.mjs` | `tmp/wf-templates/008/cdp.mjs` | 1.00 | 1／1 |
| `tools/orchestration/harness-test-quality-only.mjs` | `tmp/wf-templates/008/harness-test-quality-only.mjs` | 0.83 | 7／10 |
| `tools/orchestration/harness-test.mjs` | `tmp/wf-templates/008/harness-test.mjs` | 0.83 | 7／10 |
| `tools/wf-watchdog.py` | `tools/wf-watchdog.py` | 0.92 | 76／91 |
| `.githooks/lib/scan-range.sh` | `.githooks/lib/scan-range.sh` | 0.58 | 8／15 |
| `.githooks/pre-commit` | `.githooks/pre-commit` | 0.18 | 2／22 |
| `.githooks/pre-push` | `.githooks/pre-push` | 0.56 | 1／3 |
| `.githooks-submodule/pre-commit` | `.githooks-submodule/pre-commit` | 0.48 | 2／5 |
| `.githooks-submodule/pre-push` | `.githooks-submodule/pre-push` | 0.75 | 2／3 |
| `.claude/hooks/post-workflow-reminder.py` | `.claude/hooks/post-workflow-reminder.py` | 1.00 | 3／3 |
| `.claude/hooks/pre-workflow-gate.py` | `.claude/hooks/pre-workflow-gate.py` | 0.37 | 2／3 |
| `.claude/hooks/session-start.sh` | `.claude/hooks/session-start.sh` | 1.00 | 2／2 |
| `tools/docsync/__init__.py` | `tools/docs-sync.py（跨檔、逐字註解行）` | — | 0／1 |
| `tools/docsync/__main__.py` | `tools/docs-sync.py（跨檔、逐字註解行）` | — | 0／1 |
| `tools/docsync/adr.py` | `tools/docs-sync.py（跨檔、逐字註解行）` | — | 0／5 |
| `tools/docsync/book.py` | `tools/docs-sync.py（跨檔、逐字註解行）` | — | 4／17 |
| `tools/docsync/common.py` | `tools/docs-sync.py（跨檔、逐字註解行）` | — | 0／8 |
| `tools/docsync/events.py` | `tools/docs-sync.py（跨檔、逐字註解行）` | — | 0／6 |
| `tools/docsync/gates.py` | `tools/docs-sync.py（跨檔、逐字註解行）` | — | 14／23 |
| `tools/docsync/references.py` | `tools/docs-sync.py（跨檔、逐字註解行）` | — | 0／13 |
| `tools/docsync/rules.py` | `tools/docs-sync.py（跨檔、逐字註解行）` | — | 0／6 |


失效引用 findings（rev5拷貝失效類、confirmed）見 §1；四型：§ref＝章節號指到 rev6 不存在的節、id＝無前綴前代編號、fact＝rev5 語境事實、ext＝repo 外權威。逐字承襲本身不算 finding（D10／啟動書 §4.5 授權）。

## 5. 分流彙總

confirmed 共 86 筆（另併入同缺陷 6 筆、none 2 筆）：BL 9、修 74、none 2、ADR 1。

停點①（2026-09-04）user 裁定：全表照建議；R1-017 本批加 RL-0074；R1-073 加指針句不立 ADR；R1-097 採主線覆議修 minor；R1-M01 名詞段加「隨遷工具」句；R1-C4P04 立 ADR-00008（四碼 m0001 承 D4）；主線自判三項（R1-099 修、R1-052 只補裸 contracts 前綴、R1-097）一併確認。

| 桶 | 去向 |
|---|---|
| 修（deploy 面 21＋主線收尾 2） | commit `50c9ef7` fix(deploy) |
| 修（orchestration／tools／hooks 13） | commit `2b0e10c` fix(orchestration) |
| 修（docsync 生成器與閘名冊 11） | commit `2ff2f51` fix(docsync) |
| 修（治理文件 31＋RULES 兩句＋RL-0074＋ADR-00008） | commit `9b8129b` docs(governance) |
| BL | BL-00003 閘補腿群（R1-001／027／C301）；BL-00004 生成器補全群（R1-003／008）；BL-00005 事件欄無家群（R1-009／010）；BL-00001 註記併入（R1-080／082、EXAMPLE 重組 R1-059／060／062／087／088）；另 BL-00006 review 骨架入庫（Q2）、BL-00007 檢索性第四指標候選（Q27） |
| ADR | ADR-00008 migration 短號四碼（R1-C4P04） |
| none | R1-012（啟動書史料口徑錯、不改史料）；R1-075（ADR-00003 body 不可變、交接包原件在 rev5 tmp 唯讀） |

主線備查（非 finding、報告記）：①`deploy/secrets_common.py` 原句「驗證器不與被驗證者共用底座、永不併庫」（rev5:ADR 0010）與 GT-07 動態載入本模組形成設計張力——要納入該紀律或明文豁免屬拍板級、留待 GT-07 補腿（BL-00003）時一併問；②`docs/brainstorms/000-doc-architecture.md` §4.2 表 GT-07 列「Lint16＋secret-value-guard」為 rev5 對照欄（史料）、不改；③`tools/wf-watchdog.py` 檔頭與兩處「CLAUDE.md §2」為活引用（rev6 §2 存在）、非失效；④RULES-VERSION 由 c7a137209e0e 變為 064380371fc0（名詞段兩句＋RL-0074＋RL-0046 括號），`_sk_rules.js` 已重算，EXAMPLE 兩支內嵌的舊版本字面屬設計（R1-039 駁回）。

## 附錄 A：被駁回 findings（任一鏡駁回；附兩鏡理由）

| ID | summary | real | decided | 理由（摘） | already_decided_by |
|---|---|---|---|---|---|
| R1-011 | NOTES「未決」段是未經任何規則定義的第二個待辦家，無機器面、無出口事件、無 BL 配號 | 確認 | 駁回 | NOTES「未決」段留在 NOTES 而不轉 BACKLOG 是波 2 明載的工程判斷（判準＝「user 待拍的決定、不是可排程工項」），波 5 再度只移除 remote 一條、留 alert_webhook_url，現況正是該判斷的結果。 | docs/brainstorms/000-w2-book-skeleton.md §0.2 第 5 點（主線工程判斷、user 可翻）：未決兩條留 NOTES、非可排程工項；doc… |
| R1-014 | 權威鏈五級序列在五個現在式面各自展開重述、展開形不一致（RULES 檔頭與同檔 RL-0047 更是同檔重複） | 確認 | 駁回 | 五處中兩處（憲法 §V.1、RL-0047）是 ADR-00003／ADR-00004 拍板，另兩處（RULES.md 檔頭權威鏈行、README 權威鏈段）由波 1 計畫的檔案形制規格明載，CLAUDE.md 第108行 則是帶 RL-0047 號的指針句——現況即設計形，且三種展開語意等價（「活書家族」定義住 RULES 名詞段）、非矛盾。 | ADR-00003 決定表 §V 列（權威鏈納 RULES.md）＋ADR-00004（RL-0047 落表）＋docs/brainstorms/000-w1-governance… |
| R1-020 | CLAUDE.md §7 逐一列出六個 rev6 host 埠值，真表＝docs/generated/reference/ports.md（同檔 §1 已宣告真表），且列出的是 12 值中的 6 值 | 確認 | 駁回 | ADR-00001 已明載「真表落地後以真表為準、本 ADR 不再更新鏡像」並把全 repo 的字面埠交給勘誤紀律逐處枚舉同步，等於拍板容忍真表以外的字面埠存在，CLAUDE.md §7 的六值即該取捨下的操作用字面、不是未申報的鏡像。 | ADR-00001「配套紀律」段：真表＝docs/generated/reference/ports.md 且真表落地後以真表為準、其餘處字面埠以 errata 全 repo 枚舉… |
| R1-021 | RL-0052 內嵌「閘 ≤12」「BACKLOG 開放 ≤25」兩個數值，與 gates.py 常數並存兩家，未循 RULES 上限「工具讀檔頭」的單一家形 | 確認 | 駁回 | RL-0052 的字面值＝D8 數值拍板＋ADR-00004 決定 1（首版 73 條逐列、user 審表 2026-09-03）的產物；ADR-00004 決定 2 只為「RULES 條數／per-scope 上限」指定檔頭單一家形，從未把該形推及閘數與 BACKLOG 兩值，且以操作值直載規則句是首版通行形（RL-0045 直載 cargo 指令、RL-0060 直載 ≤3／≤20），非未經拍板的疏漏。 | docs/arc42/decisions/ADR-00004-rules-first-edition-and-budgets.md 決定 1／決定 2＋啟動書 §1.2 D8——數… |
| R1-022 | 憲法 §IV 九題無模板或機器承載：plan 模板的 Constitution Check 仍是 spec-kit 出廠佔位句，唯一承載是 speckit-plan 技能執行期讀憲法 | 確認 | 駁回 | 憲法標頭與 §IV 明文把 Constitution Check 的承載定在 `/speckit-plan` 命令執行期（SKILL.md 第 62／66 行即照辦），而 ADR-00003 拍板 spec-kit 產物屬第三方面、以 1.0.3 出廠形入版控且「升級 spec-kit＝diff 只允許工具重算形」——模板留佔位句正是拍板結果；閘數 12 已滿（ADR-00004 一進一出）故本題本就無機器閘位。P-E3 管線表「閘」欄… | ADR-00003（後果段：spec-kit 產物＝第三方面、1.0.3 出廠形入版控、升級 diff 只允許工具重算形）＋.specify/memory/constitution… |
| R1-023 | D4 的 migration 短號 m0001（四碼）只住啟動書附錄 E（史料），現在式面零命中，而首刀即 schema 刀需要配號 | 確認 | 駁回 | 啟動書附錄 E 標題自陳「編號家族的 rev6 處置（G05 名冊真源；D4 拍板 2026-09-03）」＝18 家族的單一家已拍給該表，book.py:14 as-built 註解亦寫「條目形＝家族真源（附錄 E 定 ID 形…）」；再者 summary 前提有兩處失實——AGT-／AIV- 在現在式面各有實例（非「編號家族現在式面零命中」的通例），且「首刀即 schema 刀」在 8a50ffe 未成立（D13 拍板刀序留待首刀 … | 啟動書 §1.2 D4＋附錄 E（自陳為 G05 名冊真源）——編號家族表的單一家拍給附錄 E，現在式面只在家族實際啟用時原生使用（RL-0046 只收已啟用的 BL／LL／ADR… |
| R1-029 | 反引號形的檔名／路徑引用無任何閘守，現在式面已有六處指向不存在檔的「隨刀生成」預告且無到期機制，此缺口未登記於 P-E6 閘可見性列或 BACKLOG | 確認 | 駁回 | 兩個半邊都落在拍板紀錄裡——反引號引用不入掃描面＝RULES 名詞段「提及」定義的直接後果（GT-06 docstring 明寫『提及原則』），「隨刀生成」預告無到期日＝D13「刀序留首刀 brainstorm」的連動形（§3.3 系統層欄只寫「隨刀填入」），故屬明載的設計取捨而非未察覺的缺口。 | docs/ops/RULES.md 名詞段「提及＝反引號或「」內的引用、不算使用」（＋GT-06 docstring 的「提及原則」實作）；docs/brainstorms/000… |
| R1-030 | GATES.md 與 GT-12 區塊自稱「三處名冊同源」，gt_12 實際對賬四處（package 源碼、GATES.md、pre-commit 檔頭、RUNBOOK 工具表） | 駁回 | 駁回 | 「三處名冊同源」是啟動書拍板的名詞用法：三處＝GATES.md／pre-commit 檔頭／RUNBOOK 工具表，源碼為真源不列入名冊面；finding 把 gt_12 的掃描面（含源碼、NOTES 波標記共五面）誤當名冊面計數，改「三處」為「四處」反而與拍板措辭分叉。 | docs/brainstorms/000-doc-architecture.md §4.1 與 §4.2 GT-12 列——「名冊 ↔ pre-commit 檔頭範圍字串 ↔ RU… |
| R1-032 | GT-09 的 README 樹雙向對賬前綴集不含 .githooks-submodule/，該目錄的實檔集與 README 樹分叉不會被抓 | 確認 | 駁回 | 對賬前綴集是拍板結果、非疏漏；且 README 樹首行已自我限定範圍（只宣告四前綴由 GT-09 雙向對賬），故現況無假述、finding 的備選「明寫不含」已然成立；該目錄實檔另由 EXEC_REQUIRED 兩支條目與 bootstrap hooks 指紋承載。處置應為 none；若真要擴面等同改閘掃描面語意、須走 ADR 而非直接「修」。 | docs/brainstorms/000-doc-architecture.md §4.2 GT-09 列（標題已註「已拍 2026-09-03 照表全收」）——「README 目… |
| R1-039 | EXAMPLE 兩支組裝成品內嵌 _sk_rules.js 全文逐字副本（含機器生成檔頭與三處 RULES-VERSION），為不在 GENERATED_FILES、GT-01 不掃的生成物鏡像 | 確認 | 駁回 | 「rules 段以 _sk_rules.js 原樣內嵌、末行帶 RULES-VERSION、由 PreToolUse hook 對賬」是明載的組裝設計，其版本字面耦合已具名登錄為技術債並指定去處，非未決缺陷；提案①更與該設計直接相牴。 | tools/orchestration/README.md「組裝法」段＋CLAUDE.md §2 編排驅動提示詞範本（rules 塊整塊原樣烤入、末行 RULES-VERSION、… |
| R1-041 | gates 模組匯入失敗時 compute_generated 靜默把 GATES.md 移出計算面，docsync check 仍回報「零漂移」 | 駁回 | 確認 | 前半（gates ImportError 時 GATES.md 靜默離開計算面）重現成立，但作為嚴重度依據的後半「docsync check 仍回報零漂移」被反證：同一次 import 失敗會讓 references.py:304 的 _budget_rows（except Exception，涵蓋 ImportError）把 STATE.md 閘數降為 n/a，與樹上 STATE.md 的「｜ 閘數 ｜ 12 ｜」不等，GT-01 立… |  |
| R1-047 | rev6 改寫時把刀名前綴塞進路徑中段、產出 specs/rev5:004-ip-trust-anchor/… 這條在任何 repo 都解析不到的路徑（rev5 原文是可解析的 specs/004-ip-trust-an… | 確認 | 駁回 | 現況是 RL-0046 的直接適用結果、且與 rev5 沿用至今的跨代形制一致（全 repo 14 處同形、其中 13 處逐字繼承自 rev5 對 rev4 的寫法），finding 以「閘沒逼＝過度套用」立論是把閘的射程當成規則的射程（權威鏈 RULES ＞ generated／閘），故不成立。 | docs/ops/RULES.md RL-0046（引前代編號一律帶 `rev5:`／`rev4:` 前綴、「ADR、L、B、Lint、刀名皆同」、裸刀號禁）——路徑段內的 rev… |
| R1-048 | secrets/README.md 把 SECRETS_DIR 三級口徑與 .new 守衛的「唯一權威清單／全文」指到 specs/rev4:019-secrets-sops/…，該路徑在 rev6 與 rev5 工作樹… | 確認 | 駁回 | L4／L87 的 `specs/rev4:019-secrets-sops/…` 與 rev5 原檔逐字相同（rev5 亦無該路徑、同句另存於 .env.example:23），是帶世代標籤的血緣指標而非失效的 rev6 路徑；而提案真正要動的「把唯一權威收回本檔」＝變更單一權威（RL-0011），屬拍板級須走 ADR 並同批處置 .env.example:23，故所填 修 亦不合規。 | docs/ops/RULES.md RL-0046（跨代引用一律帶前綴＝世代標籤，被標記者本就不是 rev6 可解析路徑）；該兩行與 rev5 原檔逐字相同，屬 8a20aaa「史… |
| R1-067 | submodule hook 檔頭沿用 rev5 的「兩源倉 core.hooksPath」口徑，rev6 bootstrap 已改為設在兩 worktree | 駁回 | 確認 | 檔頭字面與 rev6 bootstrap ok 訊息的措辭差異可重現，但 summary 的因果斷言「rev6 bootstrap 已改為設在兩 worktree」被反證：rev5 與 rev6 的佈署碼逐字相同，實作從未改變。 |  |
| R1-084 | vendored 的 speckit 全流程 workflow 內含 implement 步驟，與 CLAUDE.md §6 絕不用 spec-kit implement 指令硬禁令相衝且無機器閘擋 | 確認 | 駁回 | vendored spec-kit 全流程含 implement 步、且不設機器閘，正是已拍板的第三方面處置結果：ADR-00003 後果段拍板 spec-kit 產物入版控、屬第三方面、豁免掃描、升級只允許工具重算形；使用面禁令已由 CLAUDE.md §2「從不使用 spec-kit 的 implement 指令」與 §6 硬禁令涵蓋（不分呼叫路徑）。 | docs/arc42/decisions/ADR-00003-constitution-1.0.0.md 後果段＋docs/ops/RULES.md 第90行 名詞段：.specify… |
| R1-094 | CLAUDE.md 可讀性四類：15 句超 120 字、1 行括號巢狀 2 層、5 行含 3 個以上規則引用、同一指令在 §2 與 §3／§4 重述 | 確認 | 駁回 | 本筆四類判準（句長、括號巢深、單行規則引用數、跨節重述）正是拍板紀錄明載退役／指定的形：D8 拍「內容配額退役（無行數配額）」、ADR-00004 決策驅動因子拍「通道容量由條數管、不由行數管」且決定 4 拍「CLAUDE.md §2 只留步驟骨架＋指針」——一行多個 RL 號即該指針形本身，非缺陷；push／merge 的多面重述由 constitution §I.8 註明載為「方向性條款＝§I.8、程序承載＝CLAUDE.md 硬禁… | docs/brainstorms/000-doc-architecture.md §1.2 D8「內容配額退役（無行數配額）」＋docs/arc42/decisions/ADR-0… |
| R1-097 | §12「事件源」定義只列四型（收刀／review／勘誤／perf），漏 events schema 五型中的 misc，而 misc 是現有事件帳的最大宗 | 確認 | 駁回 | glossary 的「收刀」依 RULES 名詞段與 RL-0053 已涵蓋 misc，該列列的是收單場合類別（收刀／review／勘誤／perf）而非 events schema 的五個型別字面，故不存在「漏 misc」。 | docs/ops/RULES.md 名詞段（RULES:87「收刀＝merge --no-ff 回 default 後的簿記」）＋表列 RL-0053（收刀簿記＝events ap… |
| R1-C208 | dev 郵件常設 APP_MAIL_FROM／APP_MAIL_REPLY_TO 仍是前代世代域名字面 dev@rev4.local（全檔其餘世代標記——project name／image tag／網段／13 個埠——… | 確認 | 駁回 | ① 兩處郵址是 deploy/ 遷入當下明載的取捨、精確點名了這兩行與理由（沿 rev5 原值），不是漏網；同 commit 已列舉整代平移的字面集（rev5-admin→rev6-admin、fork260509-rev5→-rev6、RV5_→RV6_、/etc/rev5/→/etc/rev6/），郵址被刻意排除在外。要翻案須新證據或走拍板——proposed 自己也說「若視為 user 可見行為則先問」＝拍板級，不是 review… | commit 8a20aaa（chore(deploy): compose 三檔改 3xxxx 世代＋deploy/ 隨拓樸遷入）訊息末行逐字：「未動：dev@rev4.local… |
| R1-C209 | 零 rev6 化（逐位元組同 rev5）且首行把「路由契約」唯一指向 specs/rev4:001-compose-stack/contracts/http-surface.md——rev6 無 specs/ 樹，該契約… | 確認 | 駁回 | `rev4:` 前綴正是 RL-0046 規定的跨代引用形，「在 rev6 不可達」是跨代指針的定義而非缺陷——rev5 的同一行逐字相同、在 rev5 同樣不可達，該形制經 rev5 八刀與 29 條 lint 從未被判為缺陷，rev6 遷入時也明載保留。rev6 對 rev5 內容去處的機制是 ADR-00006 的藍本對照表（rev5 §3／§7 皆判「不承襲：rev5 空節；rev6 自 C4-L1／C4-L2 起手」＝路由契約… | commit 8a20aaa 遷入射程（「rev5 帳本引用補 rev5: 前綴、刀名補前綴；史實敘述句保留」——契約路徑本已帶 rev4: 前綴，刻意不動）；RL-0046 跨代… |
| R1-C211 | 「alert_webhook_url 佔位字面三處同字面記帳」在 rev6 只剩兩處：第三處 guard 白名單（tools/secret-value-guard.py 的 PLACEHOLDER_VALUES）在 re… | 確認 | 駁回 | finding 的核心事實主張錯誤：第三處佔位字面記帳在 rev6 仍在，位置是 `tools/docsync/gates.py:37` 的 `PLACEHOLDER_LITERALS`（隨 §4.2 的 Lint16＋guard→GT-07 一併遷入），只是 generate-secrets.py 仍用舊名 tools/secret-value-guard 指它。因此「只剩兩處」與 proposed「三處全部改口徑為兩處」都是新錯——… | 啟動書 §4.2「GT-07 ← Lint16＋secret-value-guard」——guard 的佔位白名單隨閘一起遷入 tools/docsync/gates.py，第三處… |
| R1-C214 | 兩支 alerting provisioning 檔的契約指針為裸 contracts/alerting-delivery.md，rev6 無 specs/ 樹、亦無該檔——投遞語意（重試、不影響規則狀態）在 rev6 … | 確認 | 駁回 | 與 C2-9 同類同裁。`contracts/alerting-delivery.md` 是相對路徑，其世代由同一行行首的 `rev4:016-observability rev4:T012` 給定——不是無標記的裸指針；rev5 同形、遷入時明載保留。投遞語意在 rev6「沒有可達權威來源」是跨代指針的常態，rev6 為它立家的機制是觀測刀的 spec（隨刀），不是本輪 finding。proposed 的「加前代可辨識形」實質上是把… | commit 8a20aaa 遷入射程（只補帳本／刀名前綴、史實敘述句保留）；RL-0046 跨代前綴形；啟動書 §5 波 6～「刀」（觀測面契約隨刀落家） |
| R1-C215 | reaper 姿態分派的契約指針指向 rev6 不存在的 specs/rev4:016-observability/contracts/reaper-cli.md 與 specs/rev4:017-audit-reten… | 確認 | 駁回 | 與 C2-9／C2-14 同類同裁：`specs/rev4:016-observability/contracts/reaper-cli.md` 等已是 RL-0046 合規的跨代形。且該註解真正的操作指令「三檔同步：本檔＋docker-compose.yml＋rules.yml」在 rev6 三檔俱在、可照做，沒有落空——不可達的只是背後的血緣契約，那是跨代指針的定義。若日後 reaper 姿態要在 rev6 立家，那是觀測／保留刀的… | commit 8a20aaa 遷入射程（史實敘述句保留、契約路徑已帶 rev4: 前綴故不動）；RL-0046 |
| R1-C218 | 限流三值（zone 名／size／rate）註記為「user 拍板 2026-07-10、沿用 rev3 實戰驗證值」，該拍板在 rev6 無任何可達紀錄（ADR／events／NOTES 皆無），且「user 拍板」未… | 確認 | 駁回 | 「讀來像本代拍板」的前提不成立：該句住在以「# rev4:007 登入節流（auth 功能刀兌現原裁剪聲明…）」起首的史實段內，同段另有「沿用 rev3 實戰驗證值」「rev4:008 分工補述」「429 為本刀新增（rev3 用預設 503）」——通篇 rev3／rev4 標記，世代脈絡由段落給定。整段是 8a20aaa 明載保留的史實敘述句、rev6 未動一字。且防線不靠這行註解：真要動這三值屬拍板級，RL-0001 已規定「查無紀… | commit 8a20aaa 遷入射程明載「史實敘述句保留」；且該段首行已帶 rev4:007 世代標記（rev6 與 rev5 該段逐字相同） |
| R1-C305 | GT-09 的 README 樹雙向對賬只認 ROSTER_PREFIXES 四個前綴（tools/、deploy/、.githooks/、.claude/），但同閘的 EXEC_REQUIRED 名冊含 .githoo… | 確認 | 駁回 | ROSTER_PREFIXES 的四目錄面正是啟動書 §4.2 GT-09 列逐字枚舉、user 2026-09-03「照表全收」的拍板結果，且 GATES.md face 欄如實分列「README 樹、tools/deploy/.githooks/.claude、settings.json、EXEC_REQUIRED」兩腿、與拍板無矛盾；殘餘風險屬實，但擴面＝改該拍板列，通道應為 ADR 而非 BL。 | 啟動書 docs/brainstorms/000-doc-architecture.md §4.2 GT-09 列（2026-09-03 user 照表全收）；施工面同源＝波 1 … |

## 附錄 B：完整性 critic 缺口與補漏處置

- 缺口：範圍內 37 個 tracked 檔從未被任何 lens 讀過；最大一塊＝.claude/skills/ 的 12 支 SKILL.md（2168 行未讀／全體 2784 行、僅讀 speckit-git-feature／plan／specify 三支 603 行），且計畫 §2 的掃描面清單根本沒列 .claude/skills/。｜為何重要：SDD 5 步的**可執行承載**就住這 15 支 SKILL.md，而 CLAUDE.md §2／§6 對它們下了硬禁令與流程假設：§6「絕不用 spec-kit implement 指令」對應的 speckit-implement/SKILL.md（229 行）整支沒讀；R1-084（vendored workfl…｜補派提示：派一支「工作流承載面 lens」（唯讀）：讀 .claude/skills/ 全部 15 支 SKILL.md 全文，逐支回答三問——①該 skill 的實際動作與 CLAUDE.md §2 五步描述是否一致（含它會不會自己開分支、自己 commit、自己呼叫別的 skill）；②有無任何一支的指示與 CLAUDE.m…
- 缺口：「工作流 lens」自己名下的 .specify/scripts（6 檔）與 .specify/templates（5 檔）只讀了 3 檔：create-new-feature.sh、plan-template.md、tasks-template.md；未讀 common.sh、check-prerequisites.sh、resolve-template.sh、setup-plan.sh、set…｜為何重要：R1-081 主張「branch 名 ≠ specs 目錄名、兩者短名由不同步驟各自生成」——這個判準的真源就是 common.sh（分支／目錄解析函式）與 setup-plan.sh／check-prerequisites.sh（下游步驟怎麼找回 spec 目錄），兩者皆未讀，等於該 finding 的因果鏈只驗了頭…｜補派提示：派一支「.specify 工作流腳本與模板 lens」（唯讀）：讀 .specify/scripts/bash/ 全 6 支與 .specify/templates/ 全 5 支。逐項回答——①從 create-new-feature.sh 到 setup-plan.sh／setup-tasks.sh，feature …
- 缺口：infra 拷貝面沒有任何「rev5 拷貝清單＋rev6 化處置」名冊，且 copy lens 的 scope 字面只框住 deploy/*.py／*.sh，把 deploy 下的 .yml／.json／.conf／.inc 與 docker-compose 三檔整批排除在拷貝問題之外。｜為何重要：我實測（diff 對 ../fork260509-rev5/ 同路徑）：20 個檔與 rev5 **逐位元組相同**＝零 rev6 化，其中 deploy/nginx/conf.d/_locations.inc 第 1 行仍寫「路由契約（specs/rev4:001-compose-stack/contracts/ht…｜補派提示：派一支「infra 拷貝對賬 lens」（唯讀；rev5 側只准 Read／Grep／cat／diff，絕不寫入、絕不對其做 git 操作，RL-0064）：對 deploy/**、docker-compose*.yml、.sops.yaml、.githooks/**、.githooks-submodule/**、.c…
- 缺口：拷貝紀律的射程只寫到應用碼，infra 拷貝在規則層無家。｜為何重要：我 grep 過全部四本現在式權威檔：憲法 §I.5 的射程字面是「rev6 rust-api 整棵樹」「實作以 rev5 對應碼為預設藍本」，例外清單是 sea-orm-adapter／xdb；RL-0065 的 scope 欄是 implementer，字面是「實作先讀 rev5 對應碼…註解一律重寫」；CLAUD…｜補派提示：派一支「拷貝紀律射程 lens」（唯讀）：以 grep 枚舉 .specify/memory/constitution.md、docs/ops/RULES.md、CLAUDE.md、README.md 中所有談拷貝／照搬／重打字／註解重寫的條文，逐條抄出其射程字面，做成「射程 × 實際拷貝面」矩陣，明確標出哪些實際拷貝…
- 缺口：user 第一問（事件都有家嗎）只驗了「事件→檔」單向；反向的「檔→事件」零檢查、零閘、也沒有任何 lens 掃過。｜為何重要：我讀了 GT-03 本體（tools/docsync/events.py 的 gt_03）：它遍歷 feature_close／review 事件，檢查 spec.md 存在、adrs 存在、report 存在、wontfix_adr 存在——全是事件指出去的腿。沒有任何一腿反過來問：docs/reviews/ 裡有沒…｜補派提示：派一支「反向對賬 lens」（唯讀）：以 python3 -c 讀 docs/ops/events.jsonl 與檔案樹，做三組反向集合差——①docs/reviews/*.md 減去 review 事件的 report 集合；②specs/*/ 目錄減去 feature_close 的 feature 集合；③doc…
- 缺口：事件型別的實資料覆蓋只有 3/5：events.jsonl 全部 12 列僅含 misc(6)／perf(5)／review(1)，feature_close 與 erratum **零實例**。｜為何重要：EVENT_SCHEMAS 定義五型。R1-003（erratum 更正不套用到 generated 人讀面）、R1-008（DECISIONS-INDEX 的 feature 欄自 feature_close.adrs 反查）、R1-010（feature_close.kind／spec_supersessions …｜補派提示：派一支「事件渲染反例 lens」（唯讀、絕不寫檔）：用 python3 heredoc 匯入 tools/docsync 的 events／references／adr 模組，在**記憶體中**把合成的 feature_close（含 kind、spec_supersessions、notes 全欄）與 erratum…
- 缺口：探針（P1～P4，27 題）方法論有兩個盲點：全部 27 題都有正解，計分只有「找得到／繞路」兩檔，沒有「答錯」檔位，也沒有任何一題是刻意無解的否定對照題。｜為何重要：「新 session 能否檢索」的風險有兩種：找不到（繞路），以及**自信地找到錯的**。第二種完全沒量。B1 的 R1-073 正好給出一個現成題型：「rev6 要不要做 prod 部署？」——rev6 側零拍板紀錄，但 rev5:ADR 0014 就躺在對照樹裡、標題自陳 prod-not-in-rev5-road…｜補派提示：派一支「否定對照探針 lens」（唯讀）：出 6 題，全部是 rev6 現在式面**應該查無**、但對照樹或史料面存在誘導性舊答案的題目，至少含——rev6 要不要做 prod 部署、migration 短號幾碼怎麼配、feature_close 事件必填幾欄、rev6 的 alert webhook 收件端是誰、ba…
- 缺口：沒有一組探針設「不含 CLAUDE.md」的對照組，而 CLAUDE.md 本身在內容層零閘覆蓋。｜為何重要：CLAUDE.md 由 harness 每個 session 自動注入，它一個人就把波標記位置、pin 分歧判向、rev5 埠表、簿記六步序、看門狗用法全部寫進了每個 agent 的 context。因此 27 題裡的「找得到」有多少歸功於文件樹本身、多少只是 CLAUDE.md 的複述，現有資料分不出來。同時我查過機…｜補派提示：派一支「CLAUDE.md 依賴度 lens」（唯讀）：從 27 題中挑 8 題判「這題的正解是否可只靠 CLAUDE.md 答出」，逐題標 CLAUDE.md-only／需下鑽文件樹／兩者皆無。再列一張表：CLAUDE.md 全文中所有可機器對賬的具體主張（埠值、閘數、規則編號、命令字面、事件型別欄位、簿記步數），逐…
- 缺口：至少 17 筆兩票分歧（real≠decided）與 1 筆「不確定」(R1-099) 沒有共同的補證程序；而其中兩筆我已當場確認機制存在，顯示這類分歧本可用唯讀反例注入定案。｜為何重要：分歧清單：R1-011／014／020／021／022／023／029／032／039／041／047／048／067／084／094／097 與不確定的 R1-099。我實地驗了兩筆：R1-041 的機制確實在 tools/docsync/references.py 的 compute_generated 尾端——`…｜補派提示：派一支「反例注入定案 lens」（唯讀、絕不寫檔、絕不 docsync generate）：對每一筆兩票分歧與不確定的 finding，構造最小反例並回報實際輸出。只准用 python3 -c／heredoc 在記憶體中操作（sys.modules 注入壞掉的模組、monkeypatch ctx.tracked／ctx…
- 缺口：從未做過「現在式面檔 × 守它的閘」覆蓋率矩陣；R1-091 只回答了 face 分類覆蓋（14 檔 face=None），沒回答「被幾條閘實際掃到」。順帶：文件互引路徑的存在性既無閘也沒有 lens 掃過。｜為何重要：face 分類與閘覆蓋是兩回事——一個檔可以被判為 present 面卻只吃到 GT-05／GT-06 兩條形制閘，內容主張全裸（CLAUDE.md 就是這個狀態，見上一條）。缺這張矩陣，「哪些檔的漂移沒人擋」這個問題只能逐案發現、不能系統回答，而 B1 的 G1／G2 兩批（29 筆中的多數）本質上都是這張矩陣的零星…｜補派提示：派一支「閘覆蓋率矩陣 lens」（唯讀）：讀 tools/docsync/*.py 全部 GATE: docstring 的 face 欄與各 gt_NN 實際掃描的檔集（以程式碼為準、不採信 docstring），對 git ls-files 的現在式面全集做交叉，產出矩陣：檔｜掃到它的閘｜這些閘驗的是形制還是內容。…

未驗證主張：
- B2 批（G2-4／G3／G4／G5 共 41 筆，R1-019～R1-099）只給了 id 與兩票 verdict、**未給 summary**。我因此無法判斷上列 10 條 gap 有沒有已被某筆 B2 finding 涵蓋，重疊風險存在；同理，第 9 條 gap 建議的反例注入 lens 若不先取得這 41 筆的 summary，無法逐筆構造反例。
- 10 支 lens 與 4 支探針的 prompt 原文、判準定義、以及「找得到／繞路」的計分規則我都沒看到。我對「lens 判準盲點」的判斷是從讀檔聯集與 findings 內容反推的，不是直接檢視 lens prompt——若某支 lens 的 prompt 其實已涵蓋某維而只是沒產出 finding，我會誤判為盲點。
- 探針執行時的 context 組成（是否含自動注入的 CLAUDE.md、MEMORY.md、SessionStart hook 輸出）未知。第 8 條 gap 的歸因（找得到率可能歸功於 CLAUDE.md 而非文件樹）是推論，需先查探針 prompt 才能定案。
- 「從未被讀」清單是拿計畫給的 208 檔讀檔聯集做集合差算出來的，前提是該聯集等於 lens 的實際接觸面。若某支 lens 是用 grep/rg 掃過某檔而該命中未計入讀檔聯集，我會**高估**未讀數量。37 檔這個數字應理解為上界。
- B1 的 27 題探針計分中「繞路」13 筆的實際作答內容我沒看到，只看到檔位。因此我無法判斷這 13 筆裡有沒有實際上是「答錯」而被寬鬆記為繞路的——第 7 條 gap 提出的三檔位重測正是為了消除這個不確定。
- 探索 run 是否讀過 base-web／rust-api 兩個子庫工作樹的內容未知（讀檔聯集只列了兩支 x_fork.branch-origin.md）。若 fork-delta inline 標記紀律（憲法 §III）有實體承載面在子庫內，該面在本輪體檢中是空白的。
- rev5 側的讀檔聯集（53 檔）是否等於該輪 lens 對 rev5 的實際比對面未知。我的第 3 條 gap 中「11+ 檔只讀 rev6 側」的計數同樣是以聯集為準的上界。

## 附錄 C：探針衍生 findings 被駁回（R-decided 理由）

| ID | 探針 | summary | 理由（摘） |
|---|---|---|---|
| R1-P03 | P1 | 兩處入口都把 ports.md 宣告為「埠全表／真相源」，但該表由 rev6 三份 compose 重算、12 列全為 3xxxx，零列 2xxxx；rev5 對照 stack 的 22080／22089／22079／2… | 「rev5 埠只住 CLAUDE.md §7 散文、該處無回頭指標」不成立：RUNBOOK §14 同一句已點名 ADR-00001，而 ADR-00001 的十二值全表就帶 rev5 host 欄（22080／22443／22081／22079／28025／25432／26379／23100／23000／29090／29091／22089），活書 02／03／07 與 12-glossary「對照 stack」列亦各有 2xxxx＋C… |
| R1-P05 | P2 | README 入口表「現在到哪、下一步」列同時列出 docs/generated/STATE.md（機器生成鏡像）與 docs/ops/NOTES.md 卻未標真源，體例與同表其餘三列（rev5-blueprint-ma… | 「體例不一致」前提不成立（同表另有三列指向機器生成檔亦未標真源），且 README 自身第 16 行與第 77 行已是先於該表的既有入口，明示 NOTES 首行 wave 為唯一真源、STATE 為現況帳。 |
| R1-P06 | P2 | 容器內 rust build／test 命令在文件面對「主線」與「人」兩個 scope 不可達：唯一的家 RULES RL-0045 之 carrier=prompt、scope 僅 implementer,fix（實測… | 事實面重現為真，但「不可達」與「無觸發點」兩個支撐論證皆不成立：命令的唯一人寫家 RULES RL-0045 對主線與人本就直接可讀（README 入口表第 93 列即指向 RULES.md），rules emit 的 scope 是 prompt 烤入通道、非人的檢索通道；且 §12 末句已列 rust-fmt-gate，rust 子庫刀進場時必然重訪 §12。 |
| R1-P07 | P2 | RL-0006 把「踩坑→LESSONS append」與同列「BACKLOG append」並置，字面指向 docs/ops/LESSONS.md 這個機器生成、第 1 行即宣告「嚴禁手改」的索引檔；實際機制是建 do… | 字面差異重現為真，但誤讀風險已被同一張 RULES 表的 RL-0049（scope 同含主線、明載 LESSONS.md 屬 GENERATED_FILES 名冊、禁手改）就地解消，CLAUDE.md §2 兩處與 LESSONS.md 檔頭又把「一坑一檔＋generate」寫全，手改索引另有 pre-commit check 攔下；相對於連動改 RULES-VERSION 並重烤三支編排檔的成本，不構成需本輪處置的缺口。 |
| R1-P08 | P3 | close_bookkeeping 量法在 rev6 現在式面零定義：RUNBOOK 全檔零命中「牆鐘／date +%s／close_bookkeeping」，唯一指針跨代外指 rev5:RUNBOOK §12.1，而該… | 「照 rev5:RUNBOOK §12.1 指針走會量錯、序列不可比」被 rev5 自身實踐反證——rev5 的 close_bookkeeping 資料點同樣是「包整條 git commit、單次」且 notes 逐筆自書「量測法＝RUNBOOK §12.1」，可見 §12.1 的「≥3 次取中位數」約束的是可重跑的工具基準、不是一刀一次的簿記 commit；rev6 換的只是計時器（date +%s.%N vs time.perf_… |
| R1-P10 | P3 | 識別字 `GENERATED_FILES` 在現在式面被 CLAUDE.md §4、RULES.md RL-0049 與名詞段、GATES.md GT-01 四處指涉，卻無一處給出檔案座標（真源＝tools/docsyn… | 賴以成立的前提「此為真源住程式碼的條目中唯一缺座標者」不成立——GATES.md 同表 GT-09 引 EXEC_REQUIRED、GT-10 引 BOOK_FACE，同樣是碼面常數、同樣未給檔案座標；README 那兩例屬「想知道 X 看 Y」查找表項、不是同一引用面。且 GENERATED_FILES 的內容在文件面已就地展開（GT-01 列列出 docs/generated/**＋tools/orchestration/_sk_r… |
| R1-P11 | P3 | CLAUDE.md 四處以裸 `D13`／`D14`／`D15` 引用啟動書決策編號，全篇未說明 D 編號表住哪；檔頭雖指出啟動書位置，卻未把「D 編號決策表」與該檔繫起來（相對地 constitution §I.1／§… | 既有入口已覆蓋：CLAUDE.md 檔頭第 4 行同檔即宣告「設計依據住啟動書 docs/brainstorms/000-doc-architecture.md（史料面）」，而 D1～D17 正住該檔 §1.1／§1.2，讀者一跳可達且該指針出現在首個 D 引用（行 11）之前；裸 D 形是全 repo 慣例而非 CLAUDE.md 獨有（多支 accepted ADR 同樣用裸 D），GT-05 的裸編號禁令射程是 rev5／rev4… |
| R1-P12 | P4 | CLAUDE.md §2 把 rev5 承襲候選寫成「啟動書 §5 波次表、憲法 §I.7／§III.2 承襲指針、BACKLOG 帶 rev5: 標註項」三項的封閉清單（破折號夾註「——是 brainstorm 的直接… | 探針前提「blueprint-map 只出現在 NOTES 下一步、隨首刀收單被覆寫即再也讀不到」不成立——README 有常駐入口列，且真源拍板另有 ADR-00006 承載，屬探針失誤而非文件缺口。 |
| R1-C4P01 | C4 | NOTES「下一步」仍寫「刀序與範圍由首刀 brainstorm 決定」，未隨 328f366 更新為指向已定稿的 docs/brainstorms/001-schema-baseline.md；現在式面唯一的刀序指針因… | 體檢對象 8a50ffe 該 commit 尚無 001 brainstorm（過期前提不成立），且 NOTES 改下一步依 RL-0053 屬收刀簿記步驟、不在 CLAUDE.md §2 隨做隨記清單內——brainstorm 階段單檔 commit 不動 NOTES 是照規則走。 |
| R1-C4P03 | C4 | migration 短號在 rev6 現在式面完全無定義、也無「尚未拍板」標記或去處指針：RL-0046 的原生編號家族列不含 migration、RUNBOOK §10 全章僅一句「隨首個 schema 刀補實文」、g… | migration 短號並非未定：啟動書 D4 已拍 `m0001` 四碼、附錄 E 表列且該附錄自稱「G05 名冊真源」；RL-0046 括號只列 GT-05 實際掃的四族（BL／LL／ADR／RL／GT），本就不是全家族註冊表——照提議把「尚未拍板」寫進 RUNBOOK §10 反而會製造新的權威鏈相撞，真問題由 C4-4 承載。 |
| R1-C4P05 | C4 | 「prod 不入 roadmap（承 rev5:ADR 0014）」與「隨對應刀補實文」同段並置，既未標明 rev6 未自立 ADR（權威源仍是前代）、也看不出是永久裁定還是待補事項；加上活書 §7.2 有「prod 形… | 「承 rev5:ADR 0014」正是 D5 立的承襲 provenance 慣例（＝承前代結論、rev6 未自立 ADR），不需另加註；prod 形已由憲法 §II #3 凍結、活書 §7.2 也已把形制與部署 checklist 分列指針，且憲法 §II 排程性拍板註記本就把「何時做」排除在凍結表外——現況即該拍板的結果。 |
| R1-C4P06 | C4 | 空章一律以「隨首個機密事件補實」「隨 jobs 軌刀補實文」收尾，讀者分不出「rev6 尚未拍板」與「已拍板只是還沒謄進來」——Q6（reaper 輪替週期）正卡在此層：全 repo 無任何週期數值，但現在式面沒有一句說… | 「本章隨首個機密事件補實」本身就是現在式面對 Q6 的答案（＝待該事件時定），且此形是 RUNBOOK 八處空章一致套用的預告＋回填觸發形（RL-0015／RL-0035），屬已決形制；提議只改 §7／§8 兩處亦違 RL-0011 的同形逐處枚舉要求。 |
| R1-C4P07 | C4 | 未決條只寫「佔位值→真值（RUNBOOK §15.4 形重加密）」，讀來像只差填一個字串；實際上收件端是哪個服務／哪個頻道本身也未拍板，現在式面無任何一處寫出這件事（Grafana contact point 名 rev… | NOTES「未決」段的語意在 w2 拍板時已明載＝「user 待拍的決定、不是可排程工項」，本就不是待填字串；contact point 名 rev6-webhook 也已在 provisioning 檔具名、無須 NOTES 重述。 |
| R1-C4P08 | C4 | 「workspace members（migration／entity／adapter／server 的分法）…隨 rust-api 骨架刀進場」括號內四個名字容易被當成已定的 members 清單；同時憲法 §I.5 … | §5.2 原句已自帶三重限定（「隨 rust-api 骨架刀進場」「以 rev5 活書 §5 為藍本」「憲法 §I.5」）＋§5.3「不預載模組拓樸」，讀不成已定清單；且提議要補的「sea-orm-adapter 非 members」與 001 brainstorm 已拍的 members 清單相反，照落會寫錯。 |

## 附錄 D：探索覆蓋

lens 讀檔聯集 208 檔、命令 398 條；各 lens findings 數：L1 13、L2 11、L3 8、L4 9、L5a 14、L5b 13、L5c 7、L6 10、L7 10、L8 4（合併前）。
