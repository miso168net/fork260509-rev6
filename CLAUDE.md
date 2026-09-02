# CLAUDE.md — rev6 workspace 過渡版操作手冊（波 1 用）

★本檔為**過渡版**（啟動書 D10）：只承 rev5 CLAUDE.md 的 §2 編排紀律與 §6 硬禁令、改為 rev6 語境；
節號刻意保留 §2／§6（三支 hook 的訊息指向 `CLAUDE.md §2`），§1／§3～§5／§7 留給波 1 末的正式版。
啟動書＝`tmp/rev5-handoff/rev6-000-doc-architecture.md`（波 0 搬入 `docs/brainstorms/000-*.md` 後改指該處）。
本檔引用的 `tools/docs-sync.py`、`docs/ops/events.jsonl`、三閘、RUNBOOK 等載體在波 1 內逐步落地；
未落地前該步驟不可執行——以人紀律記帳、正式版校正。行數只報表不擋（D8）。
引 rev5 帳本一律 `rev5:` 前綴（D4）；rev5 四本帳不遷入、唯讀引用（D5）。

## 2. feature 工作流

階段 0 brainstorm → SDD 5 步 → TDD 實作（Workflow 編排）→ finishing → 收刀簿記三步＋perf 第四步。

- **階段 0 brainstorm**（superpowers:brainstorming）：產出存 `docs/brainstorms/<NNN>-<feature-name>.md`
  （此行即覆蓋 skill 預設路徑）。期間拍板→ADR draft。rev5 承襲候選——rev6 啟動書 §5 波次表、
  `tmp/rev5-rules-digest.md`／`tmp/rev5-adr-digest.md` 兩份備用摘要（D5）與 BACKLOG 帶 `rev5:` 標註項——是
  brainstorm 的直接輸入：沿用項照已驗證結論施工、翻案項用新設計。★系統重寫刀序由首刀 brainstorm 決定（D13）。
- **SDD 5 步**：`/speckit-specify`（input＝brainstorm 檔）→ `/speckit-clarify` → `/speckit-plan` →
  `/speckit-tasks` → `/speckit-analyze`；每步後 commit。plan 之 research 必列
  「rev5 對應碼清單＋rev6 拍板差異點」（承 rev5:ADR 0019）。棄案論證寫完 MUST 回頭對所選方案跑
  同一反例（rev5:L-037）。
  specify 必**手動**起手、不排進 brainstorm 流程內自動觸發——否則 feature-branch pre-hook 不會跑、
  spec 會落在 default branch 上。
- **TDD 實作**：以 superpowers:executing-plans 讀 tasks 起手、批判審查分執行單元；
  **從不使用 spec-kit 的 implement 指令**。編排驅動提示詞範本：

  ```text
★skill 限 superpowers:*
以下提到 <NNN>-<feature-name> 即當前 git branch 名稱。
讀 specs/<NNN>-<feature-name>/tasks.md → act-on-code 接地、依實際相依把 tasks 分執行單元；驗收對照 spec.md。
★編排用 Workflow 工具：每執行單元一支，內部 serial 跑
　implementer(TDD) → spec-compliance review → fix 迴圈 → code-quality review → fix 迴圈。
　★fix 後次輪 review prompt 必附前輪已駁回 findings 清單（file×summary＋駁回理由）、明令勿沿用
　被駁論據重報；同一 finding 再報須附新證據，否則直接計入⑤收斂判定。
　★code-quality review prompt 烤進審查面：可見性放寬（私有→pub）先查函式體內有無被 token 掃描閘守著的呼叫、有則以 finding 要求同批補消費者名冊閘（由 fix 輪落地；rev5:L-069）。
　每個 agent prompt 烤進不可違反項：★書面產物（report／blocker／程式碼註解／文件）一律 zh-TW、
　rust 全程 serial、容器內 build/test、★rust 碼完工前容器內 `cargo fmt --all`（rev5:ADR 0057）、
　review agent 只讀不寫 repo 檔、★絕不 push/merge、★變異紅證必附 skipped=0（探針勿自 repo 外載入 mutant、rev5:L-073）、
　★變異前提＝被守面已有實例——零實例＝測空集合、紅證結構性 vacuous（rev5:L-063）、破壞性守門變異先有還原守衛（快照還原式、rev5:L-065）、負向樣本業務鍵也帶清理鍵前綴（守門被改壞那一發會真落庫、rev5:L-066）、
　★凡改變某數字／集合／方向／名稱／單一權威＝`grep -rn` 枚舉全 repo 同語意命中逐處回報——允許清單內自改、清單外升級主線（其餘交付做得完＝done_with_escalation、整件做不下去才 blocked）、史述保留現在式改對（rev5:L-032）、
　★實作先讀 rev5 對應碼（../fork260509-rev5/ 直讀、★該樹絕不寫入）高度參照但重打字消化不拷貝、註解一律重寫
　（rev5 出處帶 rev5: 前綴）、rev6 拍板差異點不得帶回（承 rev5:ADR 0019）。
★workflow script 防呆六件套（缺一不發射）：
　①agent prompt 全數烤進 script 本體模板字串；args 只傳短純量、script 首段逐欄斷言
　　（型別＋非空），不符→零派發即 throw——防 args 以 JSON 字串抵達、屬性讀出 undefined。
　②派發前斷言渲染後 prompt 非空、長度合理、開頭不含字面 "undefined"／"null"、★必含 "zh-TW"
　　字面（語言強制令漏烤→零派發即 throw；另有 PreToolUse hook 機器擋）。
　③一切邊界寫死在 script 常數、絕不取自 args：fix 迴圈用 for 上限 ≤3 輪；
　　單元 agent 總數保險絲 ≤20 支，超限 throw（fail-loud 讓主線立刻收到完成通知）；
　　★保險絲值 MUST ≥ 結構最壞值、由同檔 script 常數推導＋自我斷言、不得手挑（rev5:L-068）。
　④implementer／fix 一律 schema 回傳 {status, report}；status≠ok→立即 return 升級主線、不進 review。
　　★review agent **不得共用該 status 欄**：「agent 受阻」與「審查有 blocker」是兩件事，
　　共用一欄則 script 把後者當前者、當場 return 而 fix 迴圈整個不跑（rev5:L-011 變形①實暴）。
　　★**⑥的升級不得一律寫成 `blocked`**：「我做不下去了」與「我做完了但有清單外待辦」對 script
　　的正確反應相反（前者立即 return、後者**照常跑完審查**再連同升級項回）。故 status 分
　　`blocked`／`done_with_escalation` 兩值，只有前者觸發立即 return（rev5:L-035 實暴：五條全交付
　　的單元因兩行文件失真而整個審查階段零輪次）。徵狀＝完成通知 agent_count=1。
　⑤收斂偵測：review 連兩輪 blocker 集合（file×summary 結構化比較、勿比自由文字）相同、
　　或 fix 連兩輪零改動→return 判不收斂；unresolved 一律帶 findings 回主線。
　　★fix 迴圈跑滿上限後必有**確認輪**（再 review 一次、空 blocker 即判收斂）：直接 return
　　迴圈內的舊 blockers＝把最後一輪 fix 已修好的成果誤報成 unresolved（rev5:L-011 變形②實暴）。
　⑥空間邊界：fix agent prompt 烤進允許檔案清單（＝該執行單元 tasks 涉檔＋review findings
　　指涉檔的聯集、寫死 script 常數不取自 args）；清單外檔案需要動→絕不擅改、依④分值升級
　　（整件做不下去＝blocked；其餘交付已完成＝done_with_escalation 附清單）；次輪清單只縮不擴。
　　★清單另納會因本單元改動而連動的釘值測所在檔；清單答「碰得到什麼」而非 task 寫了什麼——對實碼查（值域／建構點／下游消費）、寧可多列（rev5:L-022／rev5:L-042／rev5:L-052）。
★主線看門狗（非終止型故障不會有完成通知）：★Workflow launch 與 Monitor 看門狗
　**同一回合原子成對**發射、兩 call 間零其他動作——「發射後再掛」＝結構性漏掛（已實證）。
　Monitor command＝`python3 tools/wf-watchdog.py <冒煙token> [wf目錄|runId]`（缺目標＝自動發現最新 wf 目錄、毋需 launch 回傳值故可同回合並發；
　帶目標＝輪詢待其出現後鎖定、resume 沿用原 runId、launch 被擋重發＝TaskStop 舊 Monitor 改帶新 runId 重掛（rev5:L-049）；ARMED 首行夾帶冒煙、stall/runaway 保險絲、happy-path 靜默）；
　完成通知＋Monitor 雙訊號全覆蓋、毋需輪詢；完成通知一到→TaskStop 該 Monitor（防誤觸 stall）。
　判死迴圈／卡死→TaskStop→修 script→以 resumeFromRunId 續跑（已完成 agent 走快取不重跑）。
　★resume **只用於故障續跑、不是「讓某支 agent 重跑」的手段**（rev5:L-027）：快取判定不逐字比
　prompt（實測改 script 後 resume 仍全數快取回放、tokens=0），且改共用的 fixPrompt 會讓前幾輪
　已完成的 fix 一併重跑、看到自己已修好的檔案而回零改動→誤觸⑤不收斂。需某階段重跑＝**新開
　一支只跑該階段的 workflow**（新 runId、零快取糾纏），CONTEXT 寫清已完成階段結論與勿重報清單。
　hook 兜底：PostToolUse(Workflow) 注入配對提醒、PreToolUse(Workflow) 擋缺 zh-TW 之 script。
主線例行只在單元邊界醒（看門狗告警除外）。★單元收尾**六步序、次序不可反**：
　①復核 agent 回報（逐項自 grep 驗證、不採信；凡本單元改變的字面→`grep -rn`／`docs-sync.py errata`
　　跨檔假述枚舉、改完復掃確認活面零命中，rev5:L-032）②load-bearing 自驗（容器內看 rc＋三閘；
　　rust 單元另跑 `docs-sync.py lint`——cargo 綠與 lint 綠是兩件事、rev5:L-064）
　★③落帳（＝「隨做隨記」的 TDD 期時點）：本單元發現的衍生工作→BACKLOG append、踩坑→
　　LESSONS append、tasks.md 把該單元涵蓋的 T **全勾**——主動做、不等 user 問
　④子庫 commit ⑤`git add <子庫>`→`docs-sync.py generate`→`git add docs/generated`
　⑥一顆外層 commit → 啟下一支（★派發前對其 tasks 逐條問「它 import／呼叫／宣告的東西存在
　　嗎」、不存在就往前追是誰該建——沒有任何 task 建＝派工單缺口；★agent 回 blocked 時先判
　　允許清單有無缺口，rev5:L-022）。
　★③必須早於⑤：STATE.md 的帳面統計與 pins 皆由 generate 現讀，反序即產出舊值**且無 diff
　　可察**（同 pin／generate 次序陷阱；成因與危害見 rev5:L-018）。
★單元一支接一支連續跑完、**不停下來等 user 首肯**；唯三種情形停：①拍板級問題（判準：schema／scope／破紀律／user 可見行為，承 rev5:CLAUDE.md §5）
　②到了需要 push/merge 的時點③觸及 §6 硬禁令。
全單元完成 → final holistic review → finishing-a-development-branch（push/merge 需 user 同意）→ 收刀簿記三步（events append＋NOTES＋tools/docs-sync.py generate）→ ★第四步（不在簿記那顆內、易漏）：該簿記 commit 落地後量其牆鐘、append 一筆 close_bookkeeping perf 事件（隨下一顆 commit 入帳；量測法＝rev5:RUNBOOK §12.1、承載處＝rev5:ADR 0070、出處＝rev5:ADR 0044 引信）。
  ```

  ★wf-watchdog 的 runaway 判準＝數**不重複 agent key**（非 journal 行數）——勿以行數直覺判保險絲。
- **隨做隨記**：新拍板→ADR draft→accepted；架構影響→活書對應節【就在 feature branch 內改】；
  踩坑→LESSONS append；衍生工作→BACKLOG append；per-unit pin 即時 bump。
  一次性遷移（改名／搬移／基線前進／拓樸調整）之 brainstorm 或 spec 附 Risk／Guard／Rollback
  三欄表。
- **輕量軌**（維護項不開 SDD）：判準＝維護／小修——單點缺陷修復、文件與設定調整、既有機制的
  小幅完備化；不動 schema、不新增能力面。程序＝開分支 → 編排單元（或直改）→ `merge --no-ff`
  回 default → misc 事件收單（消化 BACKLOG 條目時帶 backlog_done 欄）。
  拿不準走哪軌：涉拍板級（schema／scope／破紀律／user 可見行為）＝開 SDD。
- **收刀**：`merge --no-ff` 回 default（保留 feature branch 不清理）→
  ①`docs/ops/events.jsonl` append feature_close ②NOTES 改下一步 ③`tools/docs-sync.py generate`
  → 一筆簿記 commit、lint 全綠放行。簿記一律排在 merge 之後（merge SHA 與最終 pin 才確定）。
  ④簿記 commit 落地後量該顆牆鐘（量測法＝rev5:RUNBOOK §12.1）、append 一筆 `close_bookkeeping` perf
  事件（rev5:ADR 0044 引信之每刀例行量測、承載處＝rev5:ADR 0070；隨下一顆 commit 入帳）。
- **review 輪**：findings 一律三分流（修／轉 BL-NNNNN／won't-fix ADR）；承載處二分——**不定期
  獨立輪**落報告 `docs/reviews/YYYYMMDD-<scope>.md`（front-matter 必含 `findings_total`）＋一筆
  review 事件；feature／維護批收刀之 final holistic review 不落報告不落事件、以收單 commit（訊息逐項列 findings 處置）承載（rev5:ADR 0075）。

## 6. 不要做的事（精選硬禁令）

- ★絕不在 finishing 收尾階段之前 push/merge；push 前需 user 明確同意；tasks 清單不得排入 push/merge。
- ★絕不在掃描防線就位前落任何 commit（含子庫與新機器；`bash tools/bootstrap.sh` 驗證通過＝就位）。
  ★D10 唯一例外：波 1 首顆 commit＝守門五件本身、於 bootstrap／hook 落地前以人紀律放行；其後恢復本條。
- 絕不 `git submodule update`（會 reset worktree）；絕不 `git submodule add`（與 worktree 衝突；
  submodule 設定手寫 `.gitmodules`）。
- 絕不直接編輯 fork 源倉；前後端改動一律走 `base-web/`、`rust-api/` worktree。
- 絕不寫入 `../fork260509-rev5/`（含其子庫與兩份源倉）——唯讀對照基準（凍結 SHA：外層 `7eab28a`／
  base-web `9833308`／rust-api `92919b9`，由 bootstrap 斷言）；亦絕不對 rev5 stack（埠 2xxxx）做
  schema／seed／設定變更或 `down -v`；rev6 stack 走 3xxxx（D12）。
- 絕不逐字複製 RAD-AI 文字（D15）：子節名、欄位、檢核表列文字全部中文改寫；只在 README 一句參考來源
  （`Oliver1703dk/RAD-AI @ afdd36d`）；不設 NOTICE、不逐檔聲明。
- 絕不手改 `docs/generated/**`；絕不用 spec-kit implement 指令；specify 不進 brainstorm 自動流程。
- rust build/test 一律容器內跑且全程 serial（host 無 toolchain；平行 cargo 互撞 target）。
- review agent 只讀不寫 repo 檔，findings 只放回傳訊息。
- NOTES／任何帳本不記「已push/未push」揮發狀態，只記 SHA；repo 文件不引用 per-machine memory
  路徑；跨檔引用不用行號、不 deep-link BACKLOG/NOTES/STATE 的內部錨（只可整檔引用）。
