> 定稿複本（原 session 工作檔 tmp/000-w7-rev6-review.md；收單 2026-09-04；grilling 22 題裁定與執行紀錄見 §11、§13）

# 000-w7-rev6-review — rev6 文件治理架構體檢計畫（草案 v0.1、待 grilling）

> 性質：**輕量軌維護批**（RULES 名詞段：不動 schema、不新增能力面）之「不定期獨立 review 輪」（RL-0073）。
> 產出＝`docs/reviews/<日期>-doc-governance.md`＋一筆 review 事件＋findings 三分流（修／BL／won't-fix ADR）。
> 本檔住 `tmp/`（gitignored、session 工作檔）、非史料面；grilling 拍板結論回寫 §11「裁定」欄。
> 執筆＝主線 Claude Fable 5.1（2026-09-03）。發射前提＝§11 逐題拍板＋user 明說「發射」。
> user 指示（2026-09-03）：commit 328f366（001 brainstorm）不入體檢對象；分支自 rev6-admin-root @ 8a50ffe 開出（rev6-admin-root 本身仍指 328f366、未動）。
> grilling round 1（2026-09-03、/grill-with-docs）：§11 十八題全數裁 A；round 2 四題全數裁 A（§11.2）；頻域已空、待 user 確認共識後進 T0（R2-2）。名詞收斂見 §13。分支＝`000-r1-doc-governance`、報告 scope＝`doc-governance`。本 session 不做 001 刀；至此只做唯讀勘查、零 tracked 檔改動。

## 0. 一段話

三支各 ≤24 支 agent 的 Workflow（全數 `{ model: 'opus[1m]', effort: 'xhigh' }`、唯讀）分「探索 → 對抗驗證 → 補漏」跑完體檢；主線（我）只做 dedup／分批／取證／滙總，最後由我寫報告。user 的三個核心問題各有專屬 lens 與可量化產出：

| 問題 | lens | 可量化產出 |
|---|---|---|
| 所有記下的事件都有家嗎 | L1 | 事件型 × 欄位 × 消費面矩陣；「無家」列即候選 finding |
| 新 session 能否容易檢索 | P1～P4＋grader | 15 題冷啟動探針：命中率、平均 hops、3 跳內比例、答錯數、缺口清單 |
| rev5 拷貝註解哪些要調 | L5a／L5b／L5c | 27 檔相似度清冊（Jaccard、共享註解數）＋失效引用逐條＋處置 |

## 1. 目標與成功準則（可驗證）

| # | 準則 | 機器判／證據 |
|---|---|---|
| G1 | 報告落地，每筆 finding 帶 file、locator、證據命令＋輸出摘錄、兩鏡驗證票、三分流 | 報告 §1 表逐欄非空；被駁回 findings 列附錄（零靜默消失） |
| G2 | 事件×家矩陣完整 | 五型事件（feature_close／misc／review／erratum／perf）× 每個 required／optional 欄 → 消費面（STATE／MILESTONES／perf／DECISIONS-INDEX／metrics／無） |
| G3 | 探針指標落地 | 15 題逐題：找到否／hops／路徑／grader 判定；缺口→處置（README 表列／指針句／實文） |
| G4 | rev5 拷貝清冊落地 | tools／deploy／hooks 同路徑 27 檔＋docs 對照檔；每檔 Jaccard、共享註解數、失效引用數、處置 |
| G5 | 守門全綠 | `docsync lint` 0 錯 0 警（跳過≤1＝GT-08，首條 LL 落地則 0）；`check` 零漂移；`test` 綠；閘 12；三 repo porcelain＝本批改動集；rev5 三 SHA 不變＋零改動（bootstrap 斷言） |
| G6 | 事件守恆 | review 事件 total＝fixed＋len(to_backlog)＋len(wontfix_adr)（GT-02 腿）；BL 條目帶觸發條件；新 ADR（若有）proposed→accepted |
| G7 | agent 零寫入 | 每支 run 結束後外層／base-web／rust-api／`../fork260509-rev5/` 四處 `status --porcelain` 與 run 前快照相同 |

## 2. 範圍與邊界

**入**：`docs/**`（活書家族、ops 帳本、generated；brainstorms 史料只作對照源）、`README.md`、`CLAUDE.md`、`.specify/memory/constitution.md`、`tools/docsync/**`、`tools/orchestration/**`、`tools/wf-watchdog.py`、`tools/bootstrap.sh`、`.githooks/**`、`.githooks-submodule/**`、`.claude/hooks/**`＋`settings.json`；`deploy/*.py`／`*.sh`（只進 L5 拷貝 lens；註解＋字串字面皆判、程式邏輯不判〔Q15〕）；`.specify/templates`／`scripts`（只進 L6 工作流 lens）。

**併行（Q12）**：本批期間 repo 寫入獨占——001 不起手或不落 tracked 檔，user 負責告知 RAD4AI session；體檢對象單一 SHA `8a50ffe`。

**不入**：base-web／rust-api 內容（首 commit、無碼）；deploy runtime 設定語意（compose／grafana／nginx 只作 L8 活書對賬的事實源）；RAD-AI 分數重評（w5 已做、隨刀變）；001 刀本體。

**唯讀邊界（逐字烤進每支 prompt）**：不建／改／刪任何檔；禁 Edit／Write／NotebookEdit；禁 `python3 tools/docsync generate`（會寫 docs/generated）、`bash tools/bootstrap.sh`、任何 `docker`、git 寫入形（add／commit／checkout／stash／reset／submodule／worktree）；`../fork260509-rev5/` 絕不寫入（RL-0064）。允許：Read／Grep／Glob；`cat`／`sed -n`／`grep`／`find`／`diff`／`wc`／`python3 -c`（只讀）；`git log`／`show`／`ls-tree`／`diff`／`rev-parse`；`python3 tools/docsync lint|check|rules emit|errata <詞>`；`python3 tools/wf-watchdog.py test`（離線自測）。findings 只放回傳訊息（RL-0043）。

## 3. 勘查樣本（2026-09-03 實跑取得；lens 起點、非結論，全部待 workflow 對抗驗證）

| # | 樣本 | 證據命令 | 餵給 |
|---|---|---|---|
| S1 | `tools/wf-watchdog.py` 第 51／60／731 行引「CLAUDE.md §9」；rev6 與 rev5 的 repo CLAUDE.md 皆只有 §1～§7，§9 實為 user 全域 `~/.claude/CLAUDE.md` 的節（repo 外權威、新機不可解） | `grep -n 'CLAUDE\.md §9' tools/wf-watchdog.py`；`grep -n '^## ' CLAUDE.md` | L5b／L2 |
| S2 | `deploy/backup-db.py` 引「RUNBOOK §6.2」七處、無 `rev5:` 前綴；rev6 RUNBOOK §6 存在但無 §6.2 子節 | `grep -n 'RUNBOOK §6' deploy/backup-db.py`；`grep -n '^### 6' docs/ops/RUNBOOK.md`（空） | L5a |
| S3 | `tools/orchestration/EXAMPLE-*.mjs` 引 `tools/docs-sync.py`／`tools/fork-delta-lint.py`（rev6 不存在：docsync 取代前者、後者隨子庫刀進場）；U4 組裝成品範例、新 session 照抄即壞 | `grep -n 'docs-sync\.py\|fork-delta-lint' tools/orchestration/EXAMPLE-*.mjs` | L5b／L6 |
| S4 | deploy 五支 `.py` 與 rev5 同路徑檔行集合 Jaccard 0.91～0.97、共享註解 48～161 行；`wf-watchdog.py` 0.92／76 行（D10／啟動書 §4.5 授權隨遷；問題只在失效引用） | §6 pre-scan 腳本 | L5a／L5b |
| S5 | STATE「最近事件」perf／review 列 summary 空白（`- 2026-09-03｜perf｜—｜`）；MILESTONES review 列 summary 欄＝Python dict 字面 `{'total': 0, …}` | `tail -4 docs/generated/STATE.md`；`grep review docs/generated/MILESTONES.md` | L1／L4 |
| S6 | README 樹列 `docs/ops/LESSONS/`、`specs/<NNN>-…` 尚不存在；GT-09 對賬面只含 tools／deploy／.githooks／.claude——樹對 docs 是「地圖」還是「實檔對賬面」未定義 | `ls docs/ops/LESSONS specs`（皆不存在） | L7 |
| S7 | 啟動書 D1～D17（§1.1／1.2、史料面 60 KB）只部分有 ADR（ADR-00001～7）；例：D14 基線 SHA 8be6f9ba 的拍板只在啟動書＋bootstrap 斷言＋README 一句——新 session 問「為什麼」要翻史料 | `grep -n 'D14' docs/brainstorms/000-doc-architecture.md docs/arc42/decisions/*.md` | L2／P3 |
| S8 | 名詞段「波＝啟動書 §5 的階段」、§5 表止於「6～ 刀」；本批標籤 w7 與之衝突 | `sed -n '88p' docs/ops/RULES.md` | §11 Q1 |
| S9 | 三指標「治理批對 feature 比」現 6/0＝n/a；本批再＋1 治理 misc（設計張力、非缺陷；報告記） | `python3 -c` 數 events | 報告 §0 |
| S10 | GT-05 現在式面含 tools／deploy（裸編號有閘守），但「章節號引用（§N）」與「檔名引用」無閘——S1～S3 皆此型 | `sed -n '23p' tools/docsync/book.py` | L3 |
| S11 | `misc.workflow`（optional）與 `review` 的 `feature`（optional）欄無任何 generated 面渲染；`erratum` 型只有 `_erratum_view` 修正投影、無人讀列 | `grep -n 'workflow\|erratum' tools/docsync/references.py` | L1 |

## 4. 方法架構

### 4.1 為何三支 run、每支 ≤24 支

`tools/wf-watchdog.py`：RUNAWAY 上限＝`max(25, 2×AGENT_FUSE)`，但 AGENT_FUSE 自 launch 快照 json 讀、該 json 於 **run 結束後**才落地 → 進行中的 run 恆用底線 25（檔頭註解明載）。超過即 RUNAWAY 告警（非終止、只叫一次，但屬噪音且違 §2「勿以行數直覺判保險絲」精神）。故每支 run 的不重複 agent 數釘 ≤24、AGENT_FUSE ≤24、script 自我斷言。分段的第二個好處：主線在「探索→驗證」之間做 code 級 dedup 與分批（正是 pipeline 說明中唯一合理的 barrier：跨項 dedup）。

| run | 內容 | agent 數（結構最壞值） | AGENT_FUSE |
|---|---|---|---|
| A 探索 | 10 lens＋4 探針，全平行 | 14 | 15 |
| B 驗證 | finding 批 ≤7 × 2 鏡＋4 探針 ×（grader＋refuter）＋1 critic | ≤23 | 24；批 >7 → 拆 B1／B2（主線判、log 拆點） |
| C 補漏（有界、可跳過） | critic 缺口 lens ≤4＋其 findings 批 ≤2×2 | ≤8 | 9；只跑一輪（常數 MAX_GAP_ROUNDS=1） |

總數 ≤46（session 指引 <50）。model／effort 全 `opus[1m]`／`xhigh`（本 repo 骨架既有字串形，orchestration README 記已冒煙實證；claude-api skill 證實 Opus 5 原生 1M）。

### 4.2 共同烤入塊（每支 prompt 開頭；guard 斷言含 `zh-TW` 與冒煙 token）

1. 身分與任務一句＋冒煙 token 字面（常數 `SMOKE`，非 `test`）。
2. `python3 tools/docsync rules emit --scope review` 整塊（14 條＋末行 `RULES-VERSION: c7a137209e0e`；PreToolUse hook 對賬）。
3. §2 唯讀邊界全文＋允許命令清單。
4. 取證紀律：每筆 finding 必附可重跑命令＋輸出摘錄（RL-0033）；不採信文件自述、實跑；**報前先查拍板紀錄**（憲法、ADR-00001～7、RULES 名詞段、啟動書 D1～D17／§3.8／§4.2、BL-00001／00002、Day-1 GT-08）——已拍板者不報為缺陷、改填 `already_decided_by`。
5. 產出契約：只回 schema（附錄 A）、`agentStatus` 只表自身能否完成（有 finding 仍是 ok；rev5:L-011 變形①）、summary 一句話結構化鍵（跨輪不改寫）。
6. 書面產物一律 zh-TW（RL-0042）；識別字／路徑保留原形。

### 4.3 Workflow A 探索：lens 表

| key | 目的 | 輸入面 | 對賬動作（摘要；prompt 內逐條展開） | finding 判準 | 非 finding |
|---|---|---|---|---|---|
| L1 事件與帳本的家 | 答「事件都有家嗎」 | `events.py` EVENT_SCHEMAS、`references.py` gen_state／gen_milestones／gen_reference_perf、`adr.py` gen_decisions_index、`metrics`；啟動書 §4.3；README events 行 | ①五型×欄位→消費面矩陣；②反向：每個 generated 面的每欄→資料源；③metrics 算式 vs §4.3 字面（分母、rolling 窗、recurrence_of）；④BACKLOG／DEFERRED／LESSONS／NOTES 未決／ADR proposed 各自的「記→出口」閉環；⑤渲染缺陷（S5） | 欄級（Q13）：任一 required／optional 欄無 generated 面渲染且無指標消費、面無真源、算式與 §4.3 不一致、渲染不可讀 | perf 另居 perf.md（README 明載）；notes 欄若被任一面渲染即有家 |
| L2 權威鏈與拍板落點 | 五處重述是否鏡像；拍板是否找得到 | 憲法／ADR／RULES／CLAUDE.md／README／活書 §9／§12 | ①同一規則多處重述→鏡像判準＝含可漂移具體值（數字、清單、路徑）；②D1～D17／§3.8／§4.2 vs ADR 覆蓋表（S7）；③RL／ADR／GT／BL／§號引用存在且語意相符（CLAUDE.md §2 引 RL-0058～0062 六件套條文真是那些嗎）；④RULES scope／carrier 欄 vs 實承載（carrier=gate 者真有閘；carrier=prompt 者在對應 scope emit 出現） | 鏡像含具體值、引用指錯、拍板只住史料且無指針（處置形＝Q19：史料不改、現在式面加指針） | 指針句（只指路、無值）；史料面重述 |
| L3 閘與規則覆蓋 | 「說有閘守」是否真守 | `gates.py`／`book.py`／`events.py`／`adr.py`／`references.py` GATE docstring、`tests/`、GATES.md、hooks | ①每閘宣稱掃描面 vs 程式實掃；②一正一反測試存在（RL-0051）；③Day-1 謂詞可機判；④「紀律上位、機器未強制」清單（§號／檔名引用、README 表完整性、tools 面…）是否有登記去處（RULES／P-E6 閘可見性列）；⑤pre-commit 檔頭名冊、pre-push 範圍、submodule hooks 行為 vs README 描述 | 宣稱與實掃不符、無反向測試、未守紀律無登記 | 閘數上限 12 一進一出（ADR-00004 拍板） |
| L4 生成器與名冊 | 生成面正確與冪等 | `references.py` GENERATED_FILES、各 gen_*、STATE 統計、預算表 | ①名冊 12 vs 實檔（含例外註冊二件）；②README「真源」欄 vs 程式真源；③STATE 每個數字用 grep／jq 獨立重算；④預算上限來源＝ADR-00004 字面；⑤渲染缺陷（S5）；冪等一次由 `check` 零漂移已證、二次由主線 T5 實跑（agent 不得跑 generate） | 數字對不上、真源欄錯、名冊漏檔 | — |
| L5a rev5 拷貝：deploy | 失效引用清冊 | `deploy/*.py`／`*.sh`／`secrets/README.md` vs rev5 同路徑（唯讀） | 以 §6 pre-scan 表為起點：逐檔 `diff`，對每條共享註解問「rev6 語境仍真？」：§號→rev6 RUNBOOK 該節存在？無前綴前代編號？rev5 專屬事實（2xxxx、rev5 分支名、rev5 路徑、工具名）？repo 外權威？ | 失效引用、rev5 語境事實、repo 外權威 | 逐字承襲本身（D10／§4.5 授權；§11 Q5 可翻） |
| L5b rev5 拷貝：tools／hooks／orchestration | 同上 | `tools/wf-watchdog.py`、`bootstrap.sh`、`.githooks*`、`.claude/hooks`、`tools/orchestration/*`（EXAMPLE 兩支＋README＋`_sk_*`） | 同 L5a；另查 EXAMPLE 引用工具實存（S3）、orchestration README 對 rev6 骨架敘述是否仍真 | 同上 | 同上 |
| L5c rev5 承襲：docs | 文件面的 rev5 語境殘留 | RUNBOOK（章節承 rev5）、RULES、憲法、CLAUDE.md、README、arc42 正文、C4、process | ①「承 rev5」句逐句：指到的 rev5 節帶前綴否、rev6 對應去處存在否；②rev5 專屬事實（埠、分支名、路徑、`docs-sync.py`）在現在式面；③RUNBOOK 指針節（§1／§7／§12／§14／§15）指到 rev5 的節是否可解；④憲法引 rev5 ADR 前綴 | 同上 | blueprint-map 已機器對賬的標題層 |
| L6 工作流可執行性 | CLAUDE.md §2 範本能不能照著跑 | CLAUDE.md §2／§3／§4、orchestration README、`wf-watchdog.py` 介面、hooks、`.specify` 模板與 scripts、docsync CLI | 逐句對工具：`rules emit --scope` 五值；watchdog 參數／退出碼；hook 判準；`harness-test.mjs` 十案可跑；`_sk_*` 組裝法 vs 實檔；`docsync errata` 行為；bootstrap 宣稱 vs 實作；spec-kit 接線（`/speckit-specify` 手動起手的 feature-branch pre-hook 存在？plan 模板吃憲法 §IV 九題？） | 指令不存在、參數不符、宣稱行為與實作不符 | — |
| L7 時態／鏡像／可讀性 | 閘外的衛生 | 現在式面全體 | ①「波 k」史述殘留在現在式（NOTES 現況段長段史述 vs RL-0048）；②per-machine 路徑、deep-link 錨；③未來式同義集在活書；④README 樹 vs 實檔（S6）；⑤CLAUDE.md 156 行可讀性（一句多義、括號巢狀、指針密度）→ 只出 minor 建議 | 時態違規、鏡像、樹列不存在路徑 | 史料面 |
| L8 活書事實對賬（§11 Q6 納入時） | 活書「可機器對賬的事實」 | arc42 §5／§7／§12、C4-L1／L2、ports.md vs compose、repo 樹、RULES 名詞段 | 埠（ports.md／compose／CLAUDE.md §7 三處）、C4-L2 容器 vs compose 服務、§5 vs 目錄樹、§12 名詞表 vs RULES 名詞段重疊（鏡像？） | 值不一致、鏡像 | 抽象敘述 |
| P1～P3 冷啟動探針 | 量檢索性 | 只給「新 session 看得到的」：SessionStart 注入（健檢／NOTES／STATE）＋README＋CLAUDE.md 為起點；可 grep 全 repo | 各答 5～6 題（§5 題庫；共同題 1 題三支都答）；**先記路徑再作答**：打開檔案順序、hops、是否 3 跳內、歧義、死路、建議指針位置；禁用 repo 外知識 | （不出 finding；只回 PROBE schema） | — |
| P4 自由探索 | 真實任務形 | 同上 | 「你要開始首刀：先階段 0 brainstorm、再手動 `/speckit-specify`。列出事先需知的一切（brainstorm 產出位置與命名、rev5 承襲候選來源、首刀前必先消化事項、分支建立規則與序號來源、憲法自查九題、rev5 對照唯讀紀律、閘與 hook、分支建立後第一步），逐項標明找到的檔與 hops；找不到的列缺口」 | 同上 | — |

### 4.4 主線 dedup／分批（code、非 agent）

- 鍵＝`file × normalize(summary)`（去標點空白、小寫）；語意重複由我讀全表合併（預期 40～80 筆），合併時保留所有來源 lens 與證據。
- 分批＝依目錄群（docs/ops／docs/generated＋tools/docsync／tools 其他／deploy／活書／CLAUDE＋README＋憲法）分、每批 ≤6 筆；批數 >7 → B 拆兩支、`log()` 拆點（無靜默上限）。
- 探針結果原樣進 B（不 dedup）。

### 4.5 Workflow B 對抗驗證

- **每批兩鏡、獨立**（票＝確認／駁回／不確定；不得為了省事把不確定寫成確認）：
  - R-real：逐筆重跑證據命令；重現不了、或 locator 錯、或嚴重度誇大→駁回／降級。
  - R-decided：逐筆對拍板紀錄（§4.2 第 4 點清單）；已拍板→`already_decided_by`＋駁回；**文件與該拍板相矛盾**→不駁回、改類別「權威鏈矛盾」。
- **存活規則（Q25 三態）**：兩鏡皆「確認」→confirmed；任一「駁回」→附錄「被駁回」（附理由）；其餘（含任一「不確定」）→uncertain、由主線 T4 親自重跑證據裁定、報告該列標「主線裁定」；R-real 降級以降級後嚴重度計。
- **探針**：`pipeline(PROBES, grader, refuter)`——grader 獨立找真相、判「找得到／繞路／找不到／答錯」、算最短 hops、提「檢索性」finding（缺口＋建議指針位置）；refuter 以 R-decided 鏡審該 finding（例：README 表已有列但探針沒看到＝探針問題非文件問題）。
- **critic（barrier 後一支）**：讀 confirmed＋refuted＋各 lens `files_read` 聯集→缺口：範圍內從未被讀的檔、三個核心問題未被回答的部分、未驗證的主張→輸出給 C。

### 4.6 Workflow C 補漏（有界）

只當 critic 列出缺口；每缺口一支 lens（≤4）→ findings 分批 ≤2 × 兩鏡；`MAX_GAP_ROUNDS = 1` 常數、不循環。

### 4.7 防呆六件套對照（CLAUDE.md §2；RL-0058～RL-0062）

| 件 | 落實 |
|---|---|
| ① prompt 全烤進 script；args 只短純量 | A／C 不接受 args（`args` 非 undefined 即 throw，承 `_sk_head.js`）；B 的 findings 清單**烤成 script 常數**（B script 由主線依 A 結果生成、`scriptPath` 發射），首段斷言：陣列非空、每筆有 file／summary／evidence 字串 |
| ② 派發前斷言 prompt | 承 `_sk_head.js` guard：字串、≥400 字、不以 undefined／null 起頭、含 `zh-TW`、**另加含 SMOKE** |
| ③ 邊界寫死常數、保險絲自推導 | `WORST` 由 lens／批數常數算、`AGENT_FUSE = WORST + 1`、斷言 `AGENT_FUSE ≥ WORST && AGENT_FUSE ≤ 24`；`MAX_GAP_ROUNDS = 1` |
| ④ schema 回傳、status 分離 | 所有 agent 回 schema；`agentStatus` ok／failed 只表自身；failed 或 null→主線列「未完成 lens」、最多重派 1 次（新小 run、非 resume；RL-0010） |
| ⑤ 收斂偵測 | 本體檢無 fix 迴圈；唯一迴圈＝C 的一輪常數；B 拆 B1／B2 時 findings 集合不重疊（主線斷言） |
| ⑥ 空間邊界 | 全 run 唯讀＝空間邊界為零集合；主線 G7 對賬四處 porcelain |

### 4.8 看門狗與冒煙

- 每支 launch 與 `Monitor`（command＝`python3 tools/wf-watchdog.py <SMOKE>`，無第二參數＝自動發現最新 wf 目錄）**同一回合原子成對**；完成通知→`TaskStop` 該 Monitor。Monitor／TaskStop 為 deferred tool，T1 前 `ToolSearch select:Monitor,TaskStop` 先載。
- 冒煙查核：ARMED 行冒煙命中數 >0；另看最新 `agent-*.jsonl` mtime 與 grep SMOKE（一次性、不輪詢）。
- 判死／卡：STALL 780 s 告警→`TaskStop`→修 script→`resumeFromRunId`（Monitor 改帶原 runId 重掛）。

## 5. 冷啟動探針題庫（15 題＋自由探索；§11 Q4 可增刪）

| # | 題 | 分配 | 預期揭露 |
|---|---|---|---|
| 1 | 現在是波幾？唯一真源是哪個檔的哪一行？ | 共同題（P1／P2／P3） | 一致性基線 |
| 2 | 兩子庫 pin 與 worktree HEAD 分歧時怎麼判方向、各自處置？ | P1 | CLAUDE.md §3 可達性 |
| 3 | rev6 對照 rev5 的 UI 兩個埠各多少？埠真表在哪？ | P1 | §7 與 ports.md 指針 |
| 4 | 新增一條 RL 規則：改哪檔、怎麼配號、上限多少、誰檢查？ | P1 | RULES 檔頭＋GT-08／GT-12 |
| 5 | 首刀是哪把、刀序由什麼決定？若尚未決定，哪份文件說明由誰、在哪一步決定、產出放哪？ | P1 | NOTES 下一步段＋CLAUDE.md §2 階段 0＋啟動書 D13 |
| 15 | `alert_webhook_url` 未決事項的處理步驟寫在哪節？ | P1 | RUNBOOK §15.4 是否實文 |
| 6 | 容器內跑 rust test 的標準命令與 serial 紀律寫在哪？ | P2 | RUNBOOK §12 是否夠 |
| 7 | 落一條 LESSONS：檔名形、frontmatter 必填欄、索引誰產？ | P2 | LESSONS.md 頭＋ADR-00005 |
| 8 | RULES-VERSION 是什麼、哪個命令產、哪個 hook 對賬、不符會怎樣？ | P2 | README／hook |
| 9 | rev5 活書「會話狀態機（sys_token）」節在 rev6 對應到哪？ | P2 | blueprint-map |
| 10 | base-web 基線 SHA 是多少、為什麼、拍板紀錄在哪？ | P3 | S7 |
| 11 | 收刀簿記第四步是什麼、事件型別與 kind、量法？ | P3 | CLAUDE.md §2 尾＋RL-0053 |
| 12 | 目前 Day-1 豁免有哪些、解除謂詞？ | P3 | GATES.md |
| 13 | 哪些檔嚴禁手改？名冊真源在哪個程式檔？ | P3 | README→references.py |
| 14 | 上次 review 報告在哪、findings 幾筆、review 事件形？ | P3 | MILESTONES／events |
| P4 | 自由探索：開始首刀（先階段 0 brainstorm、再手動 specify）前需知的一切 | P4 | 真實任務缺口 |

grader 判定值：找得到（≤3 跳且正確）／繞路（>3 跳但正確）／找不到／答錯；每題附 grader 自己的最短路徑。

## 6. rev5 拷貝 pre-scan 規格（主線 T0 實跑、輸出表烤進 L5a／L5b prompt）

- 對象：rev6 `tools/`、`deploy/`、`.githooks*`、`.claude/hooks` 下副檔名 `.py .sh .js .mjs .toml .yml .yaml .md`（排除 `__pycache__`）；rev5 對應＝同相對路徑（唯讀讀取；無同路徑者列「rev5 無」、不猜改名）。
- 每檔輸出：`rev6 路徑｜rev5 路徑｜行集合 Jaccard｜共享註解行數／rev6 註解行數`（註解行＝`#`／`//`／`<!--`／docstring 起首／`*`）。
- 勘查值（2026-09-03）：同路徑 27 檔，Jaccard ≥0.8 者 18 檔；`tools/docsync/**`、`tools/orchestration/**` 在 rev5 無同路徑（新寫或改名——L5b 對 `_sk_*`／EXAMPLE 以 rev5 `tools/orchestration/` 之外的來源另查，prompt 明說「不猜」）。
- 失效引用四型（L5 逐條標型）：`§ref`（章節號指到 rev6 不存在的節）、`id`（無前綴前代編號）、`fact`（rev5 語境事實：2xxxx、分支名、路徑、工具名、波次）、`ext`（repo 外權威，如全域 CLAUDE.md §9；Q14：以「只有 repo 內容」為準、一律 finding）。

## 7. 報告形與事件

`docs/reviews/<YYYYMMDD>-doc-governance.md`（史料面；路徑一律反引號、不放 Markdown 連結）：

0. 範圍與方法：三支 run 的 runId、agent 數、model／effort、SMOKE、script sha256、對象 SHA（`rev6-admin-root @ 8a50ffe`）、三指標張力一句（S9）。
1. findings 總表：`ID｜lens｜file｜locator｜summary｜證據命令｜嚴重度｜R-real｜R-decided｜三分流｜處置去向（commit／BL-NNNNN／ADR-NNNNN／already_decided_by）`。
2. 事件×家矩陣（G2）＋結論一句。
3. 探針結果：15 題表（找到否／hops／路徑／grader 判定）＋指標（命中率、平均 hops、3 跳內比例）＋P4 缺口→處置。
4. rev5 拷貝清冊（G4）：檔｜Jaccard｜共享註解｜失效引用（型：數）｜處置。
5. 分流彙總：修 N（列 commit）／BL N／ADR N／already-decided N。
6. 附錄：被駁回 findings（理由）；critic 缺口與 C 處置；未完成 lens（若有）。

事件：review `{type: review, date, scope: doc-governance, report: docs/reviews/<日期>-doc-governance.md, findings: {total, fixed, to_backlog: [...], wontfix_adr: [...]}, notes}`（守恆＝GT-02 腿）；收單另一筆 misc（§9）。

## 8. 執行步驟（每步 verify 只列非顯然者）

| T | 步 | verify |
|---|---|---|
| T0 | 開分支 `000-r1-doc-governance`（Q1）；跑 §6 pre-scan 存 scratchpad；題庫定稿；組 script A＝`tmp/000-r1-wf-find.mjs`（組裝器 `tmp/000-r1-assemble-find.py`、harness `tmp/000-r1-wf-harness.mjs`、pre-scan `tmp/000-r1-prescan.md`）；自檢 | `node --check`（包 async fn）；stub 乾跑（`agent` 以 stub 取代）：guard 全過、派發數＝14、schema 欄齊；`python3 .claude/hooks/pre-workflow-gate.py < <(echo '{"tool_input":{"scriptPath":"…"}}')` rc 0 |
| T1 | 四處 porcelain 快照；`ToolSearch select:Monitor,TaskStop`；**同一回合**：`Workflow({scriptPath})`＋`Monitor(wf-watchdog SMOKE)`；完成→`TaskStop`；復核 | ARMED 冒煙 >0；journal 逐 agent `agentStatus`；四處 porcelain＝快照；failed／null lens 重派 ≤1 次 |
| T2 | dedup／分批（§4.4）；生成 script B（findings 烤入）；自檢同 T0；launch B＋Monitor；復核 | 批數 ≤7 或已拆；存活集合＋被駁回集合＝輸入集合（守恆） |
| T3 | critic 缺口→決定 C（≤8 支）或跳過；launch C＋Monitor；復核 | 同上 |
| T4 | 主線滙總：報告草稿；**逐 confirmed finding 我自 grep 復驗**（§5 不採信）；三分流建議表 | 報告 §1 每列證據可重跑 |
| — | **停點①**（R2-1）：全表貼對話、user 回「照建議」或改 ID；需新 ADR／拍板級者逐項 AskUserQuestion | — |
| T5 | 執行「修」（同分支、逐項或合理分組 commit、每顆 lint 綠、改字面即 `docsync errata` 掃）；BL append（Q11 同類合併一條、檔頭 next bump；固定兩條：Q2 review 骨架入庫候選、Q27 檢索性第四指標候選）；RULES 名詞段補「獨立輪」一句（R2-3）→ `generate` 重算 `_sk_rules.js`；ADR draft（若有 won't-fix 需新 ADR）；LESSONS（若踩坑；首條即解 GT-08 Day-1→`gates.py` 移鍵同 commit）；review 事件 append；`generate`；commit | lint／check／test 綠；閘 12；RULES 若改字面→`generate` 重算 `_sk_rules.js`、RULES-VERSION 變則報告 §0 記新值 |
| T6 | final holistic review（我自做、不派）→ **停點②** merge `--no-ff`（user 同意）→ §9 簿記 | bootstrap 純體檢 rc 0、⚠ 0 |

只在停點①②與拍板級問題停；其餘連續跑。

## 9. 收單簿記（輕量軌四步）

⓪ 計畫檔複製為 `docs/brainstorms/000-r1-doc-governance.md`（Q8；隨收單 commit）① `events.jsonl` append misc `{category: governance, summary, backlog_add: [BL-…], merge: <40 hex>, workflow: 000-r1-doc-governance, notes}` ② NOTES：現況段改一句、下一步不變（001 由 user 手動 specify）、§11 Q1 若拍 bump 則首行改 ③ `python3 tools/docsync generate` → 簿記 commit（`git commit -F`）④ 簿記 commit 落地後量牆鐘、append `close_bookkeeping` perf 事件（隨下一顆 commit）。

## 10. Risk／Guard／Rollback

| 風險 | Guard | Rollback |
|---|---|---|
| agent 誤寫 repo 檔 | prompt 唯讀令＋允許命令清單；每 run 前後四處 porcelain 對賬（G7） | tracked→`git checkout -- <檔>`、untracked→逐檔看過再刪；子庫以 `git -C` 形；每項還原後 porcelain 復核（RL-0005） |
| rev5 對照樹被動 | 同上＋bootstrap 凍結斷言（T6） | 停手問 user（CLAUDE.md §7） |
| watchdog RUNAWAY 誤報 | 每 run ≤24 支＋script 自斷言 | 告警非終止；主線核 journal 不重複 key 數後續行 |
| findings 過多、B 超 24 | 主線拆 B1／B2、`log()` 拆點、集合不重疊斷言 | — |
| hook 擋 script（RULES-VERSION 不符） | T0 用 `rules emit` 現算塊；T5 改 RULES 後重 emit | 重貼規則塊再發射 |
| lens 幻覺 finding | 兩鏡預設駁回＋主線 T4 逐筆 grep | 被駁回入附錄、不入分流 |
| 三指標 gov 比惡化 | 設計張力、報告 §0 明記；不改算式 | — |
| 首條 LL 觸發 GT-08 到期紅 | T5 同 commit 移 Day-1 鍵（承 w5 GT-03 解除形） | — |

## 11. 待拍板題（grilling；一題一問、首選＝建議）

| 題 | 選項（A＝建議） | 裁定 |
|---|---|---|
| Q1 波標記與批次名 | **A**：不 bump（名詞段「波＝啟動書 §5 階段」、§5 無波 7；本批＝波 6 刀期內維護批）；分支／事件 workflow 欄用 `000-r1-doc-governance`（r＝獨立 review 輪序號；`000-` 家族免裸刀名閘）、本計畫檔名照你指定留 tmp。**B**：bump 波標記 7、NOTES 改「波 7＝文件治理體檢；刀自波 8 起」、名詞段補「§5 外由 NOTES 登記的補充波」（動 RULES 一句、輕量軌可改）、分支 `000-w7-rev6-review`。**C**：分支叫 w7 但不 bump（名實不符，不建議）。 | **A**（2026-09-03 拍）|
| Q2 script 落點 | **A**：三支 script 住 `tmp/`（untracked），報告 §0 記 runId／sha256／關鍵常數；BL 一條「第二次獨立輪時把 review 骨架入 `tools/orchestration/`」。**B**：tracked `tools/orchestration/review-doc-governance-{find,verify}.mjs`（agents.md 自動入冊、README 樹加行、GT-09 對賬）。 | **A**（2026-09-03 拍）|
| Q3 「修」的射程（停點①的預設） | **A**：本批直修＝文件／註解／生成器渲染小修（不動閘語意、不動 RULES 條文語意；措辭勘誤可）、單項 diff ≲30 行；其餘→BL。**B**：本批零修、純報告＋BL。**C**：含工具邏輯修（gates／generate 語意）——逐項問。 | **A**（2026-09-03 拍）|
| Q4 探針題庫 | **A**：§5 的 15 題＋P4 照用。**B**：你加減題（請直接列）。 | **A**（2026-09-03 拍）|
| Q5 rev5 拷貝的「需要調整」判準 | **A**：只判四型失效引用（§ref／id／fact／ext）；逐字承襲不算 finding（D10／§4.5 授權）、但清冊附錄列比例供透明。**B**：逐字承襲也列為 minor finding（只 inventory、不分流）。**C**：視逐字承襲為違紀（需先 ADR 定憲法 §I.5 是否及於隨遷工具＝拍板級）。 | **A**（2026-09-03 拍）|
| Q6 活書事實對賬 lens（L8） | **A**：納入一支、限可機器對賬事實（埠、容器、目錄樹、名詞表重疊）。**B**：不納入、留給刀。 | **A**（2026-09-03 拍）|
| Q7 探針起點的真實度 | **A**：探針 prompt 附 SessionStart 注入的三段（健檢／NOTES／STATE）原文＝新 session 真實起點。**B**：只給 README＋CLAUDE.md。 | **A**（2026-09-03 拍）|

### 11.1 round 1 新增題（/grill-with-docs；皆裁 A）

| 題 | 裁定 |
|---|---|
| Q8 計畫檔歸宿 | **A**：收單時複製為 `docs/brainstorms/000-r1-doc-governance.md`（史料面；misc 事件 notes 與報告 §0 指向）；tmp 版留工作檔 |
| Q9 唯讀強制層級 | **A**：prompt 唯讀令＋每 run 前後四處 porcelain 對賬；發現寫入→還原、該 agent 產出作廢並列 finding；不用 isolation:'worktree'（空 gitlink 假 finding、rev5 相對路徑失效） |
| Q11 BL 條目粒度 | **A**：同類合併一條、清單住報告、BL 只放指針＋觸發（下次獨立輪前或該檔被刀動到時） |
| Q12 與 RAD4AI session／001 併行 | **A**：本批期間 repo 寫入獨占（001 不起手或不落 tracked 檔）；由 user 告知該 session、我不 SendMessage；體檢對象單一 SHA 8a50ffe |
| Q13 「有家」定義 | **A**：欄級——事件每個 required／optional 欄至少一個 generated 面渲染或一個指標消費，否則「無家」finding（minor；處置＝補渲染〔修〕或刪欄〔schema 變更＝BL〕） |
| Q14 「新 session」定義 | **A**：只有 repo 內容為準；引用 repo 外權威（全域 CLAUDE.md §N 等）＝ext 型 finding；探針＝workflow agent 即此形 |
| Q15 L5 射程 | **A**：註解／docstring＋字串字面（路徑、埠、名稱、訊息文）皆判四型失效引用；程式邏輯不判 |
| Q19 史料面處置形 | **A**：史料正文不改；誤導點→現在式面加一句指針或勘誤 |
| Q25 驗證票 | **A**：三態（確認／駁回／不確定）；不確定由主線 T4 親自重跑證據裁定、報告標「主線裁定」 |
| Q26 驗證粒度 | **A**：批次兩鏡、≤6 筆／批、同目錄群分批；一支 run |
| Q27 探針指標入帳 | **A**：只入報告 §3；BL 一條「檢索性第四指標候選、觸發＝第二次獨立輪」 |

### 11.2 round 2（皆裁 A）

| 題 | 裁定 |
|---|---|
| R2-1 停點①分流過目形式 | **A**：全表貼在對話（ID｜summary｜建議處置｜理由一句），你回「照建議」或列要改的 ID＋新處置；只有「需新 ADR 的 won't-fix」與「建議為拍板級」者另以 AskUserQuestion 逐項問 |
| R2-2 自動推進範圍 | **A**：計畫確認即做 T0（開分支、pre-scan、題庫、組 script A、自檢）並回報就緒狀態；停在發射前、等你一句「發射」 |
| R2-3 「獨立輪 000-rN」入名詞段 | **A**：T5 同批在 RULES 名詞段「刀」行後補一句「獨立輪＝RL-0073 的不定期 review 輪；分支與事件 workflow 欄 `000-rN-<scope>`、報告 `docs/reviews/YYYYMMDD-<scope>.md`」；RULES-VERSION 變→generate 重算 `_sk_rules.js`；零新閘 |
| R2-5 default 上 328f366 處置 | **保留不動**（user 2026-09-03）：rev6-admin-root 仍指 328f366（001 brainstorm 一檔、全 repo 零引用）；體檢對象仍 8a50ffe、分支自 8a50ffe 開出；收單 merge --no-ff 後 default 樹含該檔，與 NOTES「首刀 brainstorm 尚待做」的矛盾留待 001 重做時處理 |
| R2-4 BL-00001 | **A**：不消化、留給 001（原 brainstorm 曾排為 Task 0、重寫時沿用）；L6 若對骨架三變體出 finding→引 BL-00001 already-decided |

主線預設（未列題、可翻）：「修」的執行者＝主線直改（渲染邏輯修改先加測試、不派實作單元）；探針 prompt 除 SessionStart 三段外一併烤入 CLAUDE.md 全文（真實新 session 自動載入）；報告只落 md、不另發 Artifact（repo 是唯一家）；finding 編號 `R1-NN` 報告局部。

## 12. 工程判斷備查（可翻）

1. 三支 run 而非一支：§4.1（watchdog floor 25）。
2. 兩鏡批次驗證而非每筆三鏡：每批 ≤6 筆、兩鏡各自獨立且預設駁回；換來 B 在 24 支內；若你要每筆獨立三鏡，B 拆四支、agent 總數約 90（可做、只是輪次多）。
3. B 的 findings 烤成常數而非 args：六件套①字面要求；主線生成 script＝可審計（sha256 入報告）。
4. 探針只答不報 finding、由 grader 轉 finding：避免探針「為了有產出而報」；grader 獨立找真相才有對照。
5. critic 只跑一輪、C 只一輪：無界迴圈與 RL-0058 相悖；殘餘缺口列報告附錄、可入 BL。
6. 報告由主線寫、不派 synthesizer：user 指定；且分流是主線責任（RL-0073）。
7. 停點①（分流過目）放在寫報告之後、修之前：修的射程是 user 可見行為（文件面）之外的紀律問題，交 user。
8. 本批不改 watchdog 的「進行中恆 floor」限制：屬工具邏輯、非本批；若 lens 判為缺陷→BL。

## 13. 名詞收斂（grilling round 1；真源仍是 RULES 名詞段／arc42 §12，本節只記本批用法、不設鏡像）

- **家（事件）**＝schema 定義（`events.py` EVENT_SCHEMAS）＋人讀面；判到欄級（Q13）。與 RL-0049「人寫的家」是兩個概念：前者問「誰讀」、後者問「誰寫」。
- **新 session**＝只有 repo 內容的讀者（新機／他人／sub-agent）；同機全域 CLAUDE.md 與 memory 不算可解（Q14）。
- **獨立輪**＝RL-0073 的「不定期獨立 review 輪」；分支與事件 workflow 欄 `000-rN-<scope>`（r＝輪序號）、報告 `docs/reviews/YYYYMMDD-<scope>.md`；R2-3 裁定 T5 寫進 RULES 名詞段。
- **失效引用四型**＝§ref／id／fact／ext（§6）；**逐字承襲**本身非 finding（Q5；D10／§4.5 授權）。
- **驗證票**＝確認／駁回／不確定 三態（Q25）；**confirmed**＝兩鏡皆確認；**主線裁定**＝不確定者由主線重跑證據後定。
- **修／BL／ADR／already-decided**＝三分流（RL-0073）＋第四桶「已拍板、非缺陷」（引 `already_decided_by`、不計入 total）。
- finding 編號＝報告內局部（`R1-NN`）、非 ID 家族（附錄 E 不新增家族）。

## 附錄 A：schema（JSON Schema；agent 以 StructuredOutput 回）

```js
const FINDINGS_SCHEMA = { type: 'object', additionalProperties: false,
  required: ['agentStatus', 'lens', 'findings', 'coverage'],
  properties: {
    agentStatus: { type: 'string', enum: ['ok', 'failed'] },   // 只表自身能否完成審查
    lens: { type: 'string' },
    findings: { type: 'array', items: { type: 'object', additionalProperties: false,
      required: ['file', 'locator', 'summary', 'category', 'severity', 'evidence', 'proposed', 'confidence'],
      properties: {
        file: { type: 'string' }, locator: { type: 'string' },             // 標題或行號（報告內可用行號；史料面）
        summary: { type: 'string' },                                        // 一句話、結構化鍵、跨輪不改寫
        category: { type: 'string', enum: ['事件無家','檢索性','rev5拷貝失效','權威鏈矛盾','閘覆蓋缺口','生成器缺陷','時態鏡像','工作流失效','活書事實','其他'] },
        severity: { type: 'string', enum: ['blocker','major','minor'] },
        evidence: { type: 'object', additionalProperties: false, required: ['command','output'],
          properties: { command: { type: 'string' }, output: { type: 'string' } } },
        proposed: { type: 'object', additionalProperties: false, required: ['disposition','fix'],
          properties: { disposition: { type: 'string', enum: ['修','BL','ADR','none'] }, fix: { type: 'string' } } },
        already_decided_by: { type: 'string' },                             // 查到拍板即填、並自降為 none
        confidence: { type: 'number', minimum: 0, maximum: 1 },
        ref_type: { type: 'string', enum: ['§ref','id','fact','ext'] },     // 只 L5 用
      } } },
    coverage: { type: 'object', additionalProperties: false, required: ['files_read','commands_run'],
      properties: { files_read: { type: 'array', items: { type: 'string' } }, commands_run: { type: 'array', items: { type: 'string' } } } },
    notes: { type: 'string' },
  } }

const PROBE_SCHEMA = { type: 'object', additionalProperties: false, required: ['agentStatus', 'answers'],
  properties: { agentStatus: { type: 'string', enum: ['ok','failed'] },
    answers: { type: 'array', items: { type: 'object', additionalProperties: false,
      required: ['question','answer','path','hops','found','confidence'],
      properties: { question: { type: 'string' }, answer: { type: 'string' },
        path: { type: 'array', items: { type: 'string' } }, hops: { type: 'integer', minimum: 0 },
        found: { type: 'boolean' }, confidence: { type: 'number', minimum: 0, maximum: 1 },
        ambiguity: { type: 'string' }, dead_ends: { type: 'array', items: { type: 'string' } }, suggestion: { type: 'string' } } } },
    overall_notes: { type: 'string' } } }

const VERDICT_SCHEMA = { type: 'object', additionalProperties: false, required: ['agentStatus','lens','verdicts'],
  properties: { agentStatus: { type: 'string', enum: ['ok','failed'] }, lens: { type: 'string', enum: ['real','decided'] },
    verdicts: { type: 'array', items: { type: 'object', additionalProperties: false,
      required: ['key','verdict','reason','evidence'],
      properties: { key: { type: 'string' }, verdict: { type: 'string', enum: ['確認','駁回','不確定'] }, reason: { type: 'string' }, evidence: { type: 'string' },
        already_decided_by: { type: 'string' }, contradicts_decision: { type: 'boolean' },
        severity_override: { type: 'string', enum: ['blocker','major','minor'] } } } } } }

const GRADE_SCHEMA = { /* 每題：verdict 找得到／繞路／找不到／答錯、truth、truth_path、min_hops、findings[]（FINDINGS 同形、category 固定 檢索性） */ }
const CRITIC_SCHEMA = { type: 'object', additionalProperties: false, required: ['agentStatus','gaps','unverified'],
  properties: { agentStatus: { type: 'string', enum: ['ok','failed'] },
    gaps: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['what','why','lens_prompt_hint'],
      properties: { what: { type: 'string' }, why: { type: 'string' }, lens_prompt_hint: { type: 'string' } } } },
    unverified: { type: 'array', items: { type: 'string' } } } }
```

## 附錄 B：script A 骨架（關鍵常數與斷言；prompts 於 T0 展開）

```js
export const meta = { name: 'w7-doc-governance-find', description: 'rev6 文件治理架構體檢：探索與冷啟動探針（唯讀）', phases: [{ title: '探索' }, { title: '探針' }] }
if (typeof args !== 'undefined' && args !== null) throw new Error('防呆①：本 script 不接受 args')
const SMOKE = 'w7體檢-<6hex>'                       // 常數；不可為 test
const DATE = '2026-09-0X'                            // 字面；script 內禁 Date.now()
const OPTS = { model: 'opus[1m]', effort: 'xhigh' }
const LENSES = [ /* {key, prompt} ×10 */ ]
const PROBES = [ /* {key, prompt} ×4 */ ]
const WORST = LENSES.length + PROBES.length          // 14
const AGENT_FUSE = WORST + 1                          // 15
if (AGENT_FUSE < WORST || AGENT_FUSE > 24) throw new Error('防呆③：保險絲 ' + AGENT_FUSE + ' 越界（結構最壞 ' + WORST + '、watchdog 底線 25）')
let spawned = 0
function guard(p, label) { /* 承 _sk_head.js：字串、≥400、不以 undefined/null 起頭、含 zh-TW、含 SMOKE */ }
async function spawn(prompt, opts) { spawned += 1; if (spawned > AGENT_FUSE) throw new Error('防呆③：保險絲觸發'); return await agent(guard(prompt, opts.label), opts) }
const RULES_REVIEW = `…python3 tools/docsync rules emit --scope review 整塊…\nRULES-VERSION: c7a137209e0e`
const READONLY_BLOCK = `…§2 唯讀邊界全文…`
phase('探索')
const lensJobs = LENSES.map(l => () => spawn(l.prompt, { ...OPTS, label: 'lens:' + l.key, phase: '探索', schema: FINDINGS_SCHEMA }))
const probeJobs = PROBES.map(p => () => spawn(p.prompt, { ...OPTS, label: 'probe:' + p.key, phase: '探針', schema: PROBE_SCHEMA }))
const all = await parallel([...lensJobs, ...probeJobs])   // barrier 合理：主線需全量做 dedup
log('探索完成：lens ' + LENSES.length + '、探針 ' + PROBES.length + '、null ' + all.filter(x => x === null).length)
return { lenses: all.slice(0, LENSES.length), probes: all.slice(LENSES.length), spawned }
```

script B 同骨架，差異：`const FINDINGS = [ … ]`（主線烤入；首段斷言非空與欄位）、`const BATCHES = …`（≤6／批）、`WORST = BATCHES.length*2 + PROBE_RESULTS.length*2 + 1`、`pipeline(BATCHES, b => parallel([R_real(b), R_decided(b)]))`＋`pipeline(PROBE_RESULTS, grader, refuter)`＋critic（barrier 後）。

## 附錄 C：本計畫接地用的勘查命令（可重跑）

```text
grep -n 'OPTS' tools/orchestration/_sk_head.js                       # model 字串形 opus[1m]／xhigh
sed -n '48,60p' tools/wf-watchdog.py                                  # RUNAWAY_FLOOR 25、快照落地時機
python3 tools/docsync rules emit --scope review | tail -1             # RULES-VERSION: c7a137209e0e
cat .claude/hooks/pre-workflow-gate.py                                # zh-TW＋RULES-VERSION 對賬、scriptPath 亦讀
sed -n '85,95p' docs/ops/RULES.md                                     # 名詞段（波／輕量軌／現在式面）
grep -n 'def gen_\|parse_events' tools/docsync/references.py          # 事件消費面
grep -rn 'CLAUDE\.md §9' tools/wf-watchdog.py                         # S1
grep -n 'RUNBOOK §6' deploy/backup-db.py; grep -n '^### 6' docs/ops/RUNBOOK.md   # S2
grep -n 'docs-sync\.py\|fork-delta-lint' tools/orchestration/EXAMPLE-*.mjs        # S3
（§6 pre-scan：python3 行集合 Jaccard 腳本，T0 存 scratchpad）
```
