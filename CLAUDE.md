# CLAUDE.md — rev6 workspace 操作規則書

本檔＝程序與指針；**規則本體住 `docs/ops/RULES.md`**（RL-NNNN、名詞段）、凍結權威住 `.specify/memory/constitution.md`、
設計依據住啟動書 `docs/brainstorms/000-doc-architecture.md`（史料面）。行數只由 STATE.md 報表、不擋。
引 rev5 帳本一律 `rev5:` 前綴；rev5 四本帳不遷入、唯讀引用（RL-0046 前綴；RL-0064 唯讀不寫入）。

## 1. workspace 用途與 repo 拓樸

- 本 repo＝rev6 傘狀 workspace：admin 後台系統的文件、規則、spec、編排中樞；default branch `rev6-admin-root`。
- 程式碼住兩個 submodule 目錄，各有雙身分（本機＝源倉的 git worktree；對外層＝submodule gitlink）：
  - `base-web/`：分支長名 `rev6-admin-base-web`；前端（soybean-admin fork）；基線＝upstream `example` tip `8be6f9ba`（D14、與 rev5 同 SHA）。
  - `rust-api/`：分支長名 `rev6-admin-rust-api`；後端（rust；自源倉 main `32c5254` 全新寫〔憲法 §I.5〕）。
- ★應用碼實作高度參照 **rev5** 為預設藍本（rev4 溯源）：動工前先讀 rev5 對應碼（對照環境→§7、唯讀）；重打字消化、拷貝禁止；
  註解一律重寫（rev6 語境、rev5 出處帶 `rev5:` 前綴）；rev6 拍板已推翻的行為不得帶回（憲法 §I.5；RL-0065）。
- 短名／長名分工：目錄與口語用短名；git branch／push 一律用長名。
- fork 源倉目錄（repo 根下 `fork260509-soybean-admin-base/` 與 `fork260509-rev2-anew-rust-api/`、gitignored）必須保留——worktree 的 `.git` 檔指向它。
- **最原始源**（base-web fork-delta「原行」基線）＝upstream `soybeanjs/soybean-admin` 的 `example` 分支＝本機源倉恆切在 `example` tip（bootstrap 斷言）。
  base-web 修改型 inline 標記必含 `原行:`、新增型走圈界、token `rev6-inline`——紀律上位＝憲法 §III；機器強制＝`tools/fork-delta-lint.py`（pre-commit fork-delta 段；名冊＝RUNBOOK §12 碼面閘表）。
- 外層只記 gitlink SHA（pin）；worktree 模式下 `git submodule status` 行首「-」永遠出現、屬正常。
- host 埠世代 3xxxx（ADR-00001；真表＝`docs/generated/reference/ports.md`）；rev5 對照 stack 常駐 2xxxx、兩 stack 併行是預期形（§7）。

## 2. feature 工作流

階段 0 brainstorm → SDD 5 步 → TDD 實作（Workflow 編排）→ finishing → 收刀簿記三步＋perf 第四步。功能刀（spec-kit feature）走全程；維護批走輕量軌（判準＝RULES 名詞段）。

- **階段 0 brainstorm**（superpowers:brainstorming）：產出存 `docs/brainstorms/<NNN>-<feature-name>.md`（此行即覆蓋 skill 預設路徑）。
  期間拍板→ADR draft。rev5 承襲候選——啟動書 §5 波次表、憲法 §I.7／§III.2 承襲指針、BACKLOG 帶 `rev5:` 標註項——是 brainstorm 的直接輸入：
  沿用項照已驗證結論施工、翻案項用新設計。★系統重寫刀序由首刀 brainstorm 決定（D13）。
- **SDD 5 步**：`/speckit-specify`（input＝brainstorm 檔）→ `/speckit-clarify` → `/speckit-plan`（對照憲法 §IV 九題）→ `/speckit-tasks` → `/speckit-analyze`；
  每步後 commit（spec-kit git extension auto-commit、ADR-00003；其 `[Spec Kit]` 英文固定訊息與 specify 自產 `checklists/requirements.md` 之檢核項文字＝RL-0042 兩項具名例外、授權住 RULES）。plan 之 research 必列「rev5 對應碼清單＋rev6 拍板差異點」（承 rev5:ADR 0019）。
  棄案論證寫完 MUST 回頭對所選方案跑同一反例（RL-0013）。specify 必以 `/speckit-specify` 顯式起手（其 Pre-Execution Checks 才會跑 before_specify hook 建分支）、不排進 brainstorm 流程內自動觸發；其內建 NEEDS CLARIFICATION 一次呈三題之形不採用，一律改走 §5 一題一問。
  ★分支名≠feature 身分真源：分支由 hook 之 speckit.git.feature 建（序號＝腳本先 `git fetch --all --prune`、再取 `git branch -a`〔含遠端追蹤分支〕之 `NNN-` 與 `specs/` 目錄兩者最大號＋1——起手會連帶觸發一次全 remote fetch，屬預期、非越權；設定住 `.specify/extensions/git/git-config.yml`、`.specify/init-options.json`）、
  `specs/<NNN>-<slug>/` 由 specify 自建並寫入 gitignored 的 `.specify/feature.json`（per-checkout；換機／切回舊分支先 `export SPECIFY_FEATURE_DIRECTORY=specs/<本刀目錄>`）——
  specify 收工後主線必核 `git branch --show-current` 與 feature.json 的目錄名相等、不等即當場擇一改名對齊（否則 §2 範本「<NNN>-<feature-name> 即分支名」與 events `feature` 欄同時失準）。
- **TDD 實作**：以 superpowers:executing-plans 讀 tasks 起手、批判審查分執行單元；**從不使用 spec-kit 的 implement 指令**。編排驅動提示詞範本：

  ```text
★skill 限 superpowers:*
以下提到 <NNN>-<feature-name> 即當前 git branch 名稱。
讀 specs/<NNN>-<feature-name>/tasks.md → act-on-code 接地、依實際相依把 tasks 分執行單元；驗收對照 spec.md。
★編排用 Workflow 工具：每執行單元一支，內部 serial 跑
　implementer(TDD) → spec-compliance review → fix 迴圈 → code-quality review → fix 迴圈。
　★每個 agent prompt 烤進不可違反項＝`python3 tools/docsync rules emit --scope <implementer|review|fix>` 產出塊
　（整塊烤入、含末行 RULES-VERSION；PreToolUse hook 對賬、不符即擋；規則本體住 docs/ops/RULES.md、不在此重抄）。
　★單元定義→成品一律 `python3 tools/orchestration/assemble.py <uN.py> <uN.mjs>`（tdd／review 雙模式、三道自檢＝RULES-VERSION 對賬／node --check／harness；review 形骨架＝獨立輪與 final holistic review 用的 lens／兩鏡三態／grader／critic，範本＝`tools/orchestration/EXAMPLE-review-unitdef.py`（explore）與 `EXAMPLE-review-verify-unitdef.py`（verify））。
　★fix 後次輪 review prompt 必附前輪已駁回 findings 清單（RL-0071）；code-quality review 烤進可見性放寬審查面（RL-0070）。
★workflow script 防呆六件套（缺一不發射；RL-0058～RL-0062、RL-0004／RL-0012／RL-0025）：
　①agent prompt 全數烤進 script 本體模板字串；script 一律不接受 args（非 undefined／null 即零派發 throw），一切邊界與清單寫死 script 常數、`_vars`／`_plan` 段常數由首段逐欄斷言（型別＋非空），不符→零派發即 throw。
　②派發前斷言渲染後 prompt 非空、長度合理、開頭不含字面 "undefined"／"null"、必含 "zh-TW" 字面與冒煙 token。
　③一切邊界寫死在 script 常數、絕不取自 args：fix 迴圈 for 上限 ≤3 輪；TDD 執行單元 agent 總數保險絲 ≤20 支、review 形每 run ≤24 支（＝wf-watchdog 進行中 run 25 支 runaway 底線減 1），超限 throw；
　　保險絲值 MUST ≥ 結構最壞值、由同檔 script 常數推導＋自我斷言、不得手挑（rev5:L-068）。
　④implementer／fix 一律 schema 回傳 {status, report}；status≠ok→立即 return 升級主線、不進 review。
　　★review agent 不得共用該 status 欄（agent 受阻 vs 審查有 blocker 是兩件事；rev5:L-011 變形①）。
　　★升級分 `blocked`（立即 return）／`done_with_escalation`（照常跑完審查再連同升級項回；rev5:L-035）；徵狀＝完成通知 agent_count=1。
　⑤收斂偵測：review 連兩輪 blocker 集合（file×summary 結構化比較）相同、或 fix 連兩輪零改動→判不收斂；unresolved 一律帶 findings 回主線。
　　★fix 迴圈跑滿上限後必有確認輪（再 review 一次、空 blocker **且該輪審查確有執行**即判收斂；rev5:L-011 變形②。★空 blockers≠審查通過、判準＝RL-0079）。
　⑥空間邊界：fix agent prompt 烤進允許檔案清單（＝該單元 tasks 涉檔＋review findings 指涉檔的聯集、寫死 script 常數）；清單外檔案需要動→絕不擅改、依④分值升級；
　　次輪清單只縮不擴；清單另納連動釘值測所在檔、答「碰得到什麼」而非 task 寫了什麼（RL-0014／RL-0022）。
★主線看門狗（非終止型故障不會有完成通知；RL-0016／RL-0017／RL-0061／RL-0062）：★Workflow launch 與看門狗**雙掛**
　**同一回合原子成對**發射、三 call 間零其他動作——①Monitor＝`timeout_ms: 1800000`（30 分鐘＝harness 硬上限；**預設只有 5 分鐘、必須明給**）、每行即時推播＝冒煙與早期告警、**到期不重掛** ②Bash `run_in_background` 長尾腿＝同一支腳本帶 `--bg`、**例行**零重掛、退出即通知（五個出口在 `--bg` 下皆告警即退出）。★長尾腿因 RUNAWAY 退出＝主線判形態：扇出型（正當超標）→帶 `--bg --rearm` 重發長尾腿補回覆蓋、編排型→TaskStop wf；兩者皆不動 Monitor 腿。
　command＝`python3 tools/wf-watchdog.py <冒煙token> [wf目錄|runId] [--bg]`（★冒煙 token 不可取字面 `test`＝會被當自測子命令）
　（缺目標＝自動發現最新 wf 目錄；帶目標＝輪詢待其出現後鎖定、resume 沿用原 runId、launch 被擋重發＝TaskStop 舊 Monitor 與長尾腿、改帶新 runId 重發；rev5:L-049）；
　完成通知一到→TaskStop 該 Monitor（防誤觸 stall；rev5:L-051）；長尾腿由 DONE 腿自行退出、毋需 TaskStop。判死迴圈／卡死→TaskStop→修 script→以 resumeFromRunId 續跑。
　★resume 只用於故障續跑、不是讓某支 agent 重跑的手段（rev5:L-027、RL-0010）；續跑冒煙改看最新 agent 檔（RL-0009）。
　hook 兜底：PostToolUse(Workflow) 注入配對提醒、PreToolUse(Workflow) 擋缺 zh-TW／缺或錯 RULES-VERSION 之 script。
主線例行只在單元邊界醒（看門狗告警除外）。★單元收尾**六步序、次序不可反**（RL-0006／RL-0011／RL-0022／RL-0072）：
　①復核 agent 回報（逐項自 grep 驗證、不採信；凡本單元改變的字面→`python3 tools/docsync errata <詞>` 跨檔假述枚舉、改完復掃）
　②load-bearing 自驗（容器內看 rc＋`python3 tools/docsync lint`——cargo 綠與 lint 綠是兩件事）
　★③落帳（衍生工作→BACKLOG append、踩坑→LESSONS 一坑一檔（索引與 next-id 由 generate 產）、tasks 該單元涵蓋的 T 全勾、新拍板→ADR）——主動做、不等 user 問
　④子庫 commit ⑤`git add <子庫>`→`python3 tools/docsync generate`→`git add docs/generated docs/arc42/ARCHITECTURE.md docs/ops/LESSONS.md tools/orchestration/_sk_rules.js`（後三件＝`docs/generated/` 之外的 GENERATED_FILES 成員；`_sk_rules.js` 於 RULES 改動時才變）
　⑥一顆外層 commit → 啟下一支（★派發前對其 tasks 逐條問「它 import／呼叫／宣告的東西存在嗎」，rev5:L-022、RL-0008）。
　★③必須早於⑤：STATE.md 帳面統計與 pins 由 generate 現讀，反序即產出舊值且無 diff 可察（rev5:L-018）。
★單元一支接一支連續跑完、**不停下來等 user 首肯**；唯三種情形停：①拍板級問題（判準＝RULES 名詞段「拍板級」）②到了需要 push/merge 的時點③觸及 §6 硬禁令。
全單元完成 → final holistic review → finishing-a-development-branch（push/merge 需 user 同意）→ 收刀簿記三步（events append＋NOTES＋generate）→
★第四步（不在簿記那顆內、易漏）：簿記 commit 落地後量其牆鐘、append 一筆 close_bookkeeping perf 事件（隨下一顆 commit 入帳；RL-0053）。
  ```

  ★wf-watchdog 的 runaway 判準＝數**不重複 agent key**（非 journal 行數）——勿以行數直覺判保險絲。
- **隨做隨記**：新拍板→ADR draft→accepted；階段 0 定稿與 SDD 步進→NOTES「下一步」同批更新（當前意圖真源）；架構影響→活書對應節【就在 feature branch 內改】；踩坑→LESSONS 一坑一檔（索引與 next-id 由 generate 產）；衍生工作→BACKLOG append；per-unit pin 即時 bump。
  一次性遷移（改名／搬移／基線前進／拓樸調整）之 brainstorm 或 spec 附 Risk／Guard／Rollback 三欄表。
- **輕量軌**（維護項不開 SDD）：判準＝維護／小修——單點缺陷修復、文件與設定調整、既有機制的小幅完備化；不動 schema、不新增能力面。
  程序＝開分支 → 編排單元（或直改）→ `merge --no-ff` 回 default（需 user 同意）→ misc 事件收單（消化 BACKLOG 條目時帶 backlog_done 欄）。拿不準走哪軌：涉拍板級＝開 SDD。
- **收刀**：`merge --no-ff` 回 default（保留 feature branch 不清理）→ ①`docs/ops/events.jsonl` append feature_close（window＝序號）②NOTES 改下一步 ③`python3 tools/docsync generate`＋`git add docs/generated docs/arc42/ARCHITECTURE.md docs/ops/LESSONS.md tools/orchestration/_sk_rules.js`
  → 一筆簿記 commit、lint 全綠放行。簿記一律排在 merge 之後。④簿記 commit 落地後量該顆牆鐘、append 一筆 `close_bookkeeping` perf 事件（隨下一顆 commit 入帳）。
- **review 輪**：findings 一律三分流（修／轉 BL-NNNNN／won't-fix ADR）；承載處二分——不定期獨立輪落報告 `docs/reviews/YYYYMMDD-<scope>.md`＋一筆 review 事件；
  feature／維護批收刀之 final holistic review 不落報告不落事件、以收單 commit 訊息逐項列處置（RL-0073、承 rev5:ADR 0075）。

## 3. git／submodule 操作手冊

- **兩段式 commit**：①worktree 內 commit → ②立即回外層 `git add base-web`（或 `rust-api`）bump pin＋外層 commit。pin bump 在單元邊界即時做、不延到收刀；GT-02 斷言 gitlink＝worktree HEAD。
- 子庫 git 操作一律 `git -C <子庫>` 形、不 `cd` 進子庫——外層還原子庫檔＝靜默零還原（rev5:L-012）、cwd 跨工具呼叫持久化會讓相對路徑錯位、
  路徑類錯誤先 `pwd` 自證（rev5:L-070）；★/mnt/d drvfs 跑過 docker bind mount（sops.sh、compose）後同 shell 先重新 `cd` 再跑 python／git（getcwd ENOENT）；
  破壞性驗證每項還原後立即 `git -C <子庫> status --porcelain` 確認回基準態再進下一項（RL-0005）。
- **session 健檢判讀**（SessionStart hook 自動注入）：pin 與 worktree HEAD 分歧**先判方向**——兩向處置相反、照錯邊會抹掉真 commit（RL-0003）。
  ①**worktree 在前**（本機剛在子庫 commit、pin 落後）→ 回外層 `git add <子庫>` bump pin。②**pin 在前**（他機推了子庫 commit、外層 pull 帶進新 pin）→
  在 **worktree 內**顯式前進：`git -C <子庫> fetch origin <長名>` → `git -C <子庫> merge --ff-only <pin>`；★此時回外層 bump pin＝把 pin 倒回舊值。
  機判：`git -C <子庫> merge-base --is-ancestor <worktree HEAD> <pin>` 成立＝②、反向成立＝①、兩者皆不成立＝真分叉、停手問 user；pin object 不在本地＝先 fetch 再判。
  ★兩向皆**永不 `submodule update`**（會 reset worktree）。
- **初始化／新機器**：clone 外層後跑 **`bash tools/bootstrap.sh`**（一鍵幂等：源倉 clone＋worktree 重建＋hooksPath＋betterleaks 釘版＋hooks 指紋＋rev5 凍結斷言＋例外①自證＋
  docsync test／check／lint＋閘數＋secrets 體檢；舊機重跑＝純體檢）。`git submodule update --init` 僅限唯讀快速看碼捷徑，且只適用**尚無 worktree 的全新 clone**（已有 worktree 者永不 update、見本節上一條）——該模式無源倉＝無基線、不可做 base-web 開發。
- **upstream rebase**（base-web）：fetch 前 `git remote -v` 確認 upstream push URL 已設 no_push；rebase＋force-with-lease push 後**立即**回外層 bump pin；
  基線前進＝拍板級（D14；先立 ADR＋走憲法 §V.2 Amendment 改 §I.1／§III 基線 SHA，再改 bootstrap 的 BASEWEB_BASE_SHA），`原行:` 註解同步更新為 upstream 現行版（憲法 §III rebase 同步紀律）。
- 子庫 push 一律顯式 `git -C <子庫>` 形＋長名；push／merge 回 default 需 user 當次明確同意（憲法 §I.8、RL-0044）。
- exec bit 在 drvfs 上以 `git update-index --chmod=+x` 落 index（GT-09 名冊斷言 100755）。
- 故障排除→`docs/ops/LESSONS.md`（rev6 自零起）；前代候選＝rev5 `docs/ops/LESSONS.md`（唯讀、引用帶 `rev5:`）。

## 4. 文件系統規則

細則全在 `docs/ops/RULES.md`；本節只列指針（各條逐處標明所引 RL 號）：

- **三材質**：人寫／事件源（`docs/ops/events.jsonl`）／機器生成（`docs/generated/**`＋`tools/orchestration/_sk_rules.js`＋例外註冊 `docs/arc42/ARCHITECTURE.md`、`docs/ops/LESSONS.md`；名冊＝GENERATED_FILES、嚴禁手改）。
  每個事實只有一個人寫的家；鏡像不是機器生成、就是不存在（RL-0049；GT-01 零漂移）。
- **權威鏈**：constitution ＞ ADR accepted ＞ RULES ＞ 活書家族 ＞ generated（RL-0047）。
- **時態分離**：活書家族永遠現在式；未來式住 ops/；過去式住 git＋events（RL-0048；GT-06）。完成即刪、git 即史；刪列前先掃現在式引用（RL-0050）。
- **ADR**：一決策一檔 `docs/arc42/decisions/ADR-NNNNN-<slug>.md`；accepted 後 body 不可變、翻案＝新檔 `supersedes: [舊號]`、`superseded_by` 由 generate 回填（GT-04）；
  won't-fix／by-design 也立 ADR；as-built 不回灌 ADR（拍板歸 ADR、實作結果歸收刀事件）。
- **ID 配號**：BL／LL／RL 取檔頭 `<!-- next: -->` 後 bump、永不回收；ADR 編號＝檔名、永不重用（GT-05）。ops 帳本之跨刀存活面（BACKLOG／LESSONS）寫刀名形「001 刀 U2」；「本刀」只用於該刀分支內的 tasks／NOTES／commit 訊息；一律不寫裸刀號（RL-0020）。
- **前代編號**：一律 `rev5:`／`rev4:` 前綴；提及形（反引號或「」內）不算使用（RL-0046；GT-05）。
- **勘誤**：`python3 tools/docsync errata <詞>` 機器枚舉全 repo（含兩子庫 pin 樹）逐處處置後才 commit（RL-0001）。
- **tmp 工作區**：`tmp/` 為 gitignored 工作區兼跨刀資產庫（RL-0032）；**受版控文件一律不得寫 `tmp/` 具名路徑**（RL-0077、GT-06 機器守）——指範本改指入庫落點（`tools/orchestration/EXAMPLE-*.py`）或寫成不綁路徑的描述，形制句用佔位形；既有違規拿掉路徑、不是更新路徑。
- **lint 運作模式**：pre-commit 一次跑完、秒級（雙錨門檻＝`.githooks/pre-commit` 檔頭常數）；被擋的是 Claude、同回合修復（錯誤訊息附去處）；user 僅介入 lint 抓到真決策或調規拍板。
  閘名冊＝`docs/generated/GATES.md`；Day-1 豁免逐筆具名、帶解除謂詞、到期即紅（RL-0051／RL-0052）。
- **波標記**：`docs/ops/NOTES.md` 首行 `<!-- wave: N -->`＝現在波唯一真源；bump＝波次出口動作（GT-10／GT-12 判準）。
- **constitution**：`.specify/memory/constitution.md` 唯一權威、不設鏡像；amendment＝ADR＋版本 bump（§V.2）。

## 5. 提問／決策紀律

- 純工程「怎麼做」（優化手法、模組拆法、DTO 映射、命名、測試策略）自己拍、回報備查。
- 拍板級才問：動 schema／加 migration、feature scope 邊界、破紀律例外、user 可見行為變更（RULES 名詞段）。
- 拍板級條目動工前先查拍板紀錄（ADR／events／NOTES）、查無紀錄＝先問；承諾過目的事項單獨兌現、不以概括指示自行豁免（RL-0001）。
- 問法：一題一問、每題 2～3 選項、第一個為建議；大白話、每選項串回 user 核心目標；trade-off 主張先 grep 實證；行為類拍板附前後對照範例；正交維度拆開問。
- 不採信 agent 或自己的回報：一律 grep／實跑取證。

## 6. 不要做的事（精選硬禁令）

- ★絕不在 finishing 收尾階段之前 push/merge；push 前需 user 明確同意；tasks 清單不得排入 push/merge。
- ★絕不在掃描防線就位前落任何 commit（含子庫與新機器；`bash tools/bootstrap.sh` 驗證通過＝就位）。
- 絕不 `git submodule update`（會 reset worktree；唯一例外＝全新 clone 且尚無 worktree 時的 `--init` 唯讀看碼捷徑，見 §3——該模式無源倉、不可開發）；絕不 `git submodule add`（與 worktree 衝突；submodule 設定手寫 `.gitmodules`）。
- 絕不直接編輯 fork 源倉；前後端改動一律走 `base-web/`、`rust-api/` worktree。
- 絕不寫入 `../fork260509-rev5/`（含其子庫與兩份源倉）——唯讀對照基準（凍結 SHA：外層 `7eab28a`／base-web `9833308`／rust-api `92919b9`，由 bootstrap 斷言、ADR-00002）；
  亦絕不對 rev5 stack（埠 2xxxx）做 schema／seed／設定變更或 `down -v`；rev6 stack 走 3xxxx（ADR-00001）。
- 絕不逐字複製 RAD-AI 文字（D15）：子節名、欄位、檢核表列文字全部中文改寫；只在 README 一句參考來源；不設 NOTICE、不逐檔聲明。
- 絕不手改 `docs/generated/**` 與 `tools/orchestration/_sk_rules.js`；spec-kit 技能只用 §2 列名五支（specify／clarify／plan／tasks／analyze）＋其 before_*／after_* 自動 hook，其餘（implement、converge、checklist、taskstoissues、constitution、git-initialize）一律不主動叫用——taskstoissues 對共享 remote 建 issue（同 push 級、需 user 當次同意）、implement 改寫根 .gitignore／.dockerignore、constitution 依模板重寫凍結權威（憲法只走 §V.2 Amendment）；specify 不進 brainstorm 自動流程。
- 絕不 `--no-verify`（事件型檢查＝機密真進 git 歷史、不可逆；誤報→修 `.gitleaks.toml` allowlist 並雙向實證）。
- 合成機密樣本一律執行期串接、絕不落完整字面於任何 tracked 檔（含史料面與 tests；RL-0054）。
- rust build/test 一律容器內跑且全程 serial（host 無 toolchain；平行 cargo 互撞 target）。
- review agent 只讀不寫 repo 檔，findings 只放回傳訊息。
- NOTES／任何帳本不記「已push/未push」揮發狀態，只記 SHA；repo 文件不引用 per-machine 路徑；跨檔引用不用行號、不 deep-link BACKLOG/NOTES/STATE 的內部錨（GT-06）。
- commit 訊息含反引號時一律 `git commit -F -`＋quoted heredoc，絕不塞進 `-m "…"`（shell 命令替換會吃掉訊息、commit 靜默未落地）。

## 7. rev5 參照與對照環境（讀碼＋活體 UI 基準）

- rev5＝已收官的上一代：既是應用碼藍本（§1 紀律；憲法 §I.5），也是 UI 對照基準——rev6 做出來的 UI 須與其一致、以 CDP 對照驗收。
- **讀碼**：`../fork260509-rev5/` 之 `base-web/` 與 `rust-api/`＝切在 `rev5-admin-*` 的真 worktree（凍結 SHA 見 §6）。直接 Read／Grep／Glob，勝過 `git show` 逐檔撈。
  ★它是可寫的真工作樹、無物理唯讀保護：絕不寫入；派 agent 讀 rev5 時唯讀令必烤進 prompt（RL-0064）。bootstrap 斷言其三處 HEAD＝凍結 SHA、已追蹤檔零改動；不一致＝有人動過、停手問 user。
- **對照 stack**：於 `../fork260509-rev5/` 根跑 `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait`；例行只 up／stop／ps，
  拆除、機密、故障排除→rev5 自家 `docs/ops/RUNBOOK.md`。★絕不 `down -v`；runtime 使用屬正常，但絕不動其 schema／seed／設定；rev6 的 psql 絕不指向 rev5 庫。
- **端口**（皆 127.0.0.1）：22080＝rev5 UI（對照基準）｜22089＝soybean example 原版基線｜22079＝rev5 API｜25432／26379／28025＝pg／redis／mailpit。
  rev6 側 32080（UI）／32089（example）／32079（API）／35432／36379／38025——2xxxx 對 3xxxx 不衝突、兩 stack 併行是預期形。
- **UI 對照流程**：host 瀏覽器以 `--remote-debugging-port=9229` 起，CDP 接 `127.0.0.1:9229`（Node 24 內建 WebSocket；工具＝`tools/orchestration/cdp.mjs`），
  開分頁對照 22080（rev5）vs 32080（rev6）、必要時加 22089 三方比。★一律用 127.0.0.1、不用 localhost（origin 不同、token 不共享）；dev 帳號 Super／Admin／User。
  真登入走查前後的全表基準 snapshot／diff／restore 工具＝`tools/walkthrough-baseline.py`（承 rev5 同名工具、rev5:L-071；非碼面閘、只指向 rev6 stack），契約住 RUNBOOK §9c。
