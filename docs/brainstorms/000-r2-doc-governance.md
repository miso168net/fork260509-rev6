> 000-r2 的做法可以一句話講完：沿用 r1 的骨幹，換上已入庫的 review 骨架，再把三件新輸入接進去。細節如下。

# 000-r2-doc-governance — rev6 文件治理架構體檢第二輪計畫（v0.3、§11 十題＋grilling 兩輪 Q11～Q19 已裁定）

> 性質：**輕量軌維護批**之「不定期獨立 review 輪」（RL-0073；RULES 名詞段「獨立輪」＝分支與 misc 事件 workflow 欄 `000-rN-<scope>`、報告 `docs/reviews/YYYYMMDD-<scope>.md`＋一筆 review 事件）。
> 產出＝`docs/reviews/<日期>-doc-governance.md`＋review 事件（含 ADR-00021 `probe` 欄）＋findings 三分流（修／BL／won't-fix ADR）＋主張×閘×真源矩陣（BL-00003 ③ 拍板輸入）。
> 骨幹＝r1 計畫檔 `docs/brainstorms/000-r1-doc-governance.md`；本檔**只寫差集**，共通處回指 r1 章節、不重抄（RL-0049 一個家）。r1 已由 grilling 裁定且本輪沿用者列 §11.1、不再問。
> 執筆＝主線 Claude Fable 5.1（2026-09-07、default `rev6-admin-root @ ef37e61`、BACKLOG 開放 8）。grilling（2026-09-07、一題一問）：§11 十題裁定＝Q1～Q9 皆 A、Q10 B（收單後再 push）；grill-with-docs 兩輪（§11.2／§11.3）Q11～Q19 皆 ①。發射前提＝user 確認共識後進 T0（R2-2 沿用：做到發射前即停）＋user 明說「發射」。

## 0. 一段話

四支 Workflow（三支唯讀 review 形＋一支 TDD 形修單）、每支 ≤24 支 agent、review 角色全 `opus[1m]`／`xhigh`、implementer `fable[1m]`／`xhigh`（`tools/orchestration/_sk_head.js` 之 IMPL_OPTS／REVIEW_OPTS／FIX_OPTS 字面）；主線只做 dedup／分批／取證／滙總／寫報告。本輪回答四個問題，各有專屬 lens 與可量化產出：

| 問題 | lens／探針 | 可量化產出 |
|---|---|---|
| 兩刀之後（8a50ffe→ef37e61：87 顆、文件與工具面 120 檔 +15,252／−1,361）文件治理是否仍自洽 | L1／L2／L4／L6／L7／L8 | confirmed findings 表；活書 as-built 對賬表；生成面每數字重算 |
| 檢索性有沒有退步（第四指標首次輪間比較） | P1～P4＋grader | review 事件 `probe` 欄兩組；STATE 第四列 r1 基準 vs r2；缺口清單 |
| 「說有閘守」是否真守（BL-00003 三腿） | L3／L9／D 修單 | 主張×閘×真源矩陣（§6、含獨家清單）；GT-03 BL 存在性腿（events-only）、SKIP 分類（八處 ERROR／三處 `ENV_SKIPS`）、GT-12 登記腿各一正一反落地 |
| r1 critic 留下的缺口有沒有被讀到 | L10＋L11 | 附錄 B 十條缺口逐條「已覆蓋／finding／仍缺口」 |

## 1. 目標與成功準則（可驗證）

| # | 準則 | 機器判／證據 |
|---|---|---|
| G1 | 報告落地，每筆 finding 帶 file、locator、證據命令＋輸出摘錄、兩鏡三態票、三分流 | 同 r1 G1；被駁回入附錄、零靜默消失 |
| G2 | 探針指標結構化入帳 | review 事件 `probe`＝`{questions 25, found, detour, not_found, wrong, avg_min_hops, negative{7 題同形}}`；GT-02 形檢綠（守恆）；STATE 第四列由 generate 現算、與報告 §3 表逐題可重算；題文 diff r1 報告 §3 表＝僅 P4「首刀」→「下一刀」一詞（Q15、可比性）；缺答依 Q17 |
| G3 | 主張矩陣落地 | CLAUDE.md＋憲法每條可機器對賬主張一列（§6 形）；「無閘」與「獨家」列彙總成停點①的一題拍板 |
| G4 | BL-00003 ①② 落地 | `gt_03` BL 引用存在性腿（events-only 不變式、Q14）＋Day-1 型八處改 ERROR＋環境型三處 `ENV_SKIPS` 具名跳過＋GT-12「SKIP 鍵 ⊆ 登記集」腿（Q13／Q19），各一正一反（`tools/docsync/tests/`）；`docsync test` 全綠 |
| G5 | 守門全綠 | `docsync lint` 0／0／0、`check` 零漂移、`test` 綠、閘數 12（不新增閘；一進一出若拍板另立 ADR）、bootstrap 純體檢 rc 0、rev5 三 SHA 不變 |
| G6 | 事件守恆 | review 事件 total＝fixed＋len(to_backlog)＋len(wontfix_adr)；misc 收單帶 backlog_add／backlog_done／adrs；BL 條目帶觸發 |
| G7 | agent 零寫入 | 每支 run 前後外層／base-web／rust-api／`../fork260509-rev5/` 四處 `status --porcelain` 相同；D 修單改動集 ⊆ 允許檔清單 |
| G8 | r1 critic 十條缺口逐條有處置 | 報告附錄 B 表：已覆蓋（哪支 lens 讀了哪些檔）／finding／仍缺口→BL |

## 2. 範圍與邊界

**入**（r1 §2 全部＋新面）：r1 面（`docs/**`、`README.md`、`CLAUDE.md`、`.specify/memory/constitution.md`、`tools/docsync/**`、`tools/orchestration/**`、`tools/wf-watchdog.py`、`tools/bootstrap.sh`、`.githooks/**`、`.githooks-submodule/**`、`.claude/hooks/**`＋`settings.json`）＋新面：碼面閘三支與 `tools/docsync/vendored.py`（RUNBOOK §12 碼面閘表對象）、`tools/orchestration/` 13 檔（骨架與範本）、ADR-00008～ADR-00021、`docs/generated/reference/{routes,schema,accounts,rev5-blueprint-map,agents,perf}.md`、`docs/ops/LESSONS/` 12 檔、`.claude/skills/` 15 支 SKILL.md（2,784 行；r1 只讀 3 支）、`.specify/scripts/`（6）＋`.specify/templates/`（5）、`specs/001-*`／`specs/002-*`（只作活書 as-built 與事件的**事實源**、不審 spec 本體）。

**併行**：本輪期間 repo 寫入獨占（r1 Q12 形）；對象＝分支開出點 SHA（T0 填入報告 §0）。

**不入**：rust-api／base-web 業務邏輯與測試本體（每刀 spec-compliance 輪與碼面閘之責；Q2 若納 L11 亦只審治理面）；deploy runtime 語意；rev5 拷貝清冊重跑（r1 G4 已清、四型失效引用只對 r1 後新增／改動檔重查，併入 L5）；003 本體（Q1＝A 時尚不存在）。

**唯讀邊界**＝r1 §2 全文逐字烤進每支 review prompt（由 `_sk_review.js` READONLY 段供）；本輪新增允許：`python3 tools/docsync vendored-check`（只讀比對）；新增禁止：`python3 tools/orchestration/assemble.py`（寫 .mjs）、`python3 tools/docsync refresh`（寫快照）。D 修單 implementer／fix 的寫入面＝允許檔清單（§4.7）。

## 3. 勘查樣本（2026-09-07 於 ef37e61 實跑取得；lens 起點、非結論）

| # | 樣本 | 證據命令 | 餵給 |
|---|---|---|---|
| S1 | 基線／凍結 SHA 四值分佈：`8be6f9ba` 在 CLAUDE.md／憲法／bootstrap 三處；`7eab28a` 四處（＋README）；`92919b9` 三處；`9833308` 兩處（CLAUDE.md／bootstrap、憲法無）。r1 報告零 finding 提及＝r1 未判；「家」是憲法 §I.5／ADR-00002 還是 bootstrap 斷言常數、其餘處是鏡像含值還是指針，待矩陣定 | `for s in 8be6f9ba 7eab28a 92919b9 9833308; do grep -l $s CLAUDE.md README.md .specify/memory/constitution.md tools/bootstrap.sh; done` | L9 |
| S2 | `DAY1_EXEMPTIONS` 零筆；docsync 內 11 處 `finding(SKIP, "GT-…")` 分支（book.py 4／gates.py 7）、訊息多自稱「Day-1」；GATES.md Day-1 豁免表空 → R1-027 仍在（BL-00003 ②）；問題＝這些「面缺席」分支在 Day-1 已過的今天該登記解除謂詞還是改 ERROR（RL-0051） | `sed -n '/^DAY1_EXEMPTIONS/,/^}/p' tools/docsync/gates.py; grep -c 'SKIP, "GT-' tools/docsync/*.py` | L3／D |
| S3 | `gt_03` 對 backlog_add／backlog_done／to_backlog 只驗形（`_id_list_ok(…, RE_BID)`）；實算現帳：事件 add 34／done 26／to_backlog 6、現行 8、git 史曾為列 35；三類斷鏈皆空集合 → 腿 ① 今日綠、判準＝「曾 backlog_add 或 git 史曾為列」（BL-00003 ① 設計註：done 指向已刪列） | 附錄 B 之 python 實算 | L3／D |
| S4 | r1 否定對照題今況：Q4「rust-api 第一支 crate 建了嗎」→ 四 crate 在場；Q5「002 是什麼」→ `specs/002-system-settings/` 在場——兩題已由「應查無」變「可答」→ 否定對照題庫每輪必重選（§5.2） | `git -C rust-api ls-files \| cut -d/ -f1 \| sort -u; ls specs/` | P4 |
| S5 | LESSONS 重複率 0.25＝LL-00006（recurrence_of LL-00004）／LL-00007（LL-00002）／LL-00011（LL-00006）；目標 0 的釋義＝「晉升後再踩＝規則層 bug」→ lens 問：三筆再踩的規則承載是否真在對應 scope 的 prompt 面（如 RL-0011 在 implementer scope？） | `grep -n recurrence_of docs/ops/LESSONS/*.md` | L2 |
| S6 | 活書 05 對 server crate 模組提及數：auth 3／handler 2／facade 2／validation 2／router 3／obs 1／request_context 1／envelope 2／error 1／config 1／state 1；`dev_identity`／`test_kit` 0（實檔 19 支）；GT-10 只驗子項名冊鍵集與圖表對賬、不驗「模組敘述 vs 實檔」 | `git -C rust-api ls-files 'server/src/**/*.rs'; grep -c <模組名> docs/arc42/05-building-block-view.md` | L8 |
| S7 | `rev5-blueprint-map` 4 列「隨刀」（島 A～D／E／F／I 進場刀）；003 會消費島 A～D＋E → 否定題「sys_token 在 rev6 哪個 crate」應查無且 map 應指「隨刀」 | `grep -n 隨刀 docs/generated/reference/rev5-blueprint-map.md` | P4／L8 |
| S8 | 治理指標現值：治理比 7.5（15/2）、LESSONS 重複率 0.25、淨流量 n/a、檢索性＝r1 基準列（≤3 跳 0.48／答對 1.0／0／0）；本輪 +1 governance misc → 8.0（設計張力同 r1 S9、報告 §0 記、不改算式） | `sed -n '/## 治理指標/,/## 數量/p' docs/generated/STATE.md` | 報告 §0 |
| S9 | 規模：tracked 296、docs md 93、CLAUDE.md 160 行（r1 時 156）、RULES 74、ADR 21、LESSONS 12、events 41；`.claude/skills` 15 支 SKILL.md 2,784 行；`.specify/scripts` 6、`templates` 5 | `git ls-files \| wc -l` 等 | L10／L7 |
| S10 | 骨架常數：`MAX_AGENTS_PER_RUN 24`；explore WORST＝nL＋nP（inline 時＋2nL＋2nP）、verify WORST＝2nB＋2nP＋critic；`AGENT_FUSE＝WORST＋1`、超 24 即 throw；`RULES-VERSION 741ae996dc61`；wf-watchdog `RUNAWAY_FLOOR 25` | `grep -n 'WORST\|FUSE\|OPTS' tools/orchestration/_sk_head.js; python3 tools/docsync rules emit --scope review \| tail -1` | §4 |

## 4. 方法架構

### 4.1 四支 run 與支數（每支 ≤24＝RL-0060、r1 §4.1 理由不變）

| run | 形 | 內容 | WORST／FUSE |
|---|---|---|---|
| A 探索 | review／explore、`INLINE_VERIFY=false` | lens 12（§4.3；L9 拆 a／b）＋探針 6（核心 4 支 P1～P4〔含 r1 P4 自由探索〕＋否定對照 1＋新面 1；T0 更正：v0.3 漏算 P4 自由探索）；全平行 | 18／19 |
| B 驗證 | review／verify | findings 批 ≤5 × 兩鏡＋探針 6 ×（grader→refuter）＋critic 1 | 23／24；批 >5 → 主線依 24 上限切成 N 支批 run（末支帶 critic）、探針獨立一支、`log()` 拆點 |
| C 補漏（有界、可跳過） | review／explore、`INLINE_VERIFY=true` | critic 缺口 lens ≤4、就地兩鏡 | 12／13；只跑一輪 |
| D 修單 | tdd（`_sk_main.js`） | U-r2-gates：implementer→spec review→fix 迴圈→code-quality review→fix 迴圈；`IMPLEMENTERS=1、CYCLES=2、MAX_FIX_ROUNDS=3` | 15／16（≤20） |

總數 ≤65；主線在 A→B 之間做 code 級 dedup／分批（r1 §4.4 原樣）。

### 4.2 共同烤入塊

同 r1 §4.2 六項；差異：①規則塊由 `assemble.py` 自 `tools/orchestration/_sk_rules.js` 原樣併入（含末行 RULES-VERSION；T5 若改 RULES 字面須 `generate` 重算再重組，否則 `.claude/hooks/pre-workflow-gate.py` 擋）；②唯讀邊界／取證／回傳段由 `_sk_review.js` 供、本輪 unitdef 只寫 `CONTEXT`（對象、範圍、冒煙 token）與 `DECISIONS_BLOCK`（拍板紀錄清單：憲法 1.1.0、ADR-00001～21、RULES 名詞段、BL 現行 8 條之拍板句、events 收單 notes、Day-1 現況；verify 另加 P4 應查無題判準段＋§5.2 真相表＝Q12）；③探針 task 刻意不烤 `CONTEXT`（只有「新 session 看得到的」：SessionStart 三段＋README＋CLAUDE.md 全文＝r1 Q7）。

### 4.3 Workflow A：lens 表（r1 §4.3 為底；「同 r1」＝對賬動作與判準原樣、只縮輸入面）

| key | 目的 | 輸入面（差集） | 對賬動作 | finding 判準／非 finding |
|---|---|---|---|---|
| L1 事件與帳本的家 | r1 G2 矩陣重算 | r1 後新型實例：feature_close ×2、erratum ×2、misc.adrs／workflow、review.probe、close_bookkeeping／precommit_chain perf | 同 r1；另核 erratum 更正視圖真的套到 STATE／MILESTONES／DECISIONS-INDEX／perf 四面 | 同 r1 Q13 欄級 |
| L2 權威鏈與拍板落點 | 鏡像／指針／承載 | ADR-00008～21 vs 現在式面重述；憲法例外①②自證腿（`vendored-check`、ADR-00009 條件①）vs 字面；RULES 74 條 carrier 欄 vs 實承載；S5 三筆再踩的規則承載 | 同 r1 | 同 r1；含具體值之重述由 L9 矩陣收、L2 不重報 |
| L3 閘與規則覆蓋 | 「說有閘守」 | 12 閘 GATE docstring vs 實掃；S2 Day-1 SKIP 分支逐鍵；S3 gt_03 BL 存在性；碼面閘三支＋`vendored-check` 的名冊（RUNBOOK §12）與自測；`test_hook_wiring` 名冊 vs hook | 同 r1；BL-00003 ①② 只出「修單規格」不重報缺口；另於 `notes` 輸出「現在式面檔 × 掃到它的閘」覆蓋表（r1 C3 重算、Q16） | 已拍板者引 `already_decided_by`（ADR-00004／00011／00018／00019／00020） |
| L4 生成器與名冊 | 生成面正確 | GENERATED_FILES 15 vs 實檔；STATE 每數字（含第四列）獨立重算；DECISIONS-INDEX feature 欄自 misc.adrs 反查；reference 三表（routes／schema／accounts）真源與 `refresh` 流程敘述；agents.md vs `_sk_head.js` 字面 | 同 r1 | — |
| L5 rev5 承襲（縮） | 四型失效引用 | 只查 r1 後新增／改動之 tools／hooks／docs 檔＋`rust-api/server` 與 `base-web` 新增檔的註解紀律（`rev5:` 前綴、RL-0065 防回歸句） | 同 r1 §6 四型；程式邏輯不判（Q15） | 逐字承襲非 finding（Q5） |
| L6 工作流可執行性 | CLAUDE.md §2／§3 範本可照跑 | `assemble.py` 三道自檢、`EXAMPLE-*-unitdef.py` 範本、harness 兩支案數、wf-watchdog 介面、bootstrap 3c、RUNBOOK §12b 量法、spec-kit 五支接線（以 002 實跑史為證）、hook 三支 | 同 r1 | — |
| L7 時態／鏡像／可讀性 | 閘外衛生 | NOTES 現況段（002 後）、CLAUDE.md 160 行、README 讀序與查詢表、per-machine 路徑、deep-link | 同 r1 | 史料面 |
| L8 活書事實對賬 | as-built 真不真 | arc42 05／08 vs `rust-api/server/src` 19 檔與 base-web 新增檔（S6）；06 vs blueprint-map「隨刀」列（S7）；C4；ports vs compose；§12 名詞表 vs RULES 名詞段 | 值不一致、模組敘述缺實檔、鏡像 | 抽象敘述；設計上不列之測試工具（須有一句說明） |
| L9a／L9b 主張×閘×真源矩陣（新；a＝CLAUDE.md、b＝憲法 §I～§V） | BL-00003 ③ 輸入 | 主線 T0 pre-scan 候選表烤入 | §6 規格：逐條主張→真源→守它的閘或腿→「CLAUDE.md 以外的家」→判定；矩陣寫回傳 `notes` | findings 只出「矛盾」「鏡像含可漂移值」；「無閘」列與「獨家」列不出 finding、彙總成停點①一題 |
| L10 未讀面補掃（新） | r1 critic 缺口 | `.claude/skills` 15 支 vs CLAUDE.md §2／§6 對 spec-kit 五支＋自動 hook 的敘述；`.specify/scripts`＋`templates` vs 分支序號／feature.json 敘述；「檔→事件」反向：`docs/reviews/*`、`docs/arc42/decisions/*` 每檔 ↔ 事件（review.report／feature_close.adrs／misc.adrs）存在 | 敘述與實檔不符、反向缺席 | 六支不主動叫用之 skill 內容本身不審（只審「不叫用」敘述是否成立）；創世 ADR-00001～7 之反向缺席引 `already_decided_by`（adrs 欄晚於它們、BL-00004） |
| L11 碼面治理（Q2 A） | 治理面、非業務邏輯 | RUNBOOK §12 碼面閘表 ↔ `tools/` 三支與其 `test` 子命令；`entity_access_lint`／`wire_schema` 等契約測試面之自述 vs 憲法 §II 島條文；rust-api 三 crate 檔頭「守哪條」句 vs RULES | 名冊漂移、自述與條文相反 | 已由 GT-12／GT-09 腿機器對賬者不報 |

探針（unitdef key）：P1～P3 核心題、P4 核心自由探索（§5.1）、P5 否定對照（§5.2）、P6 新面題（§5.3、只入報告）；對照組已撤（Q11、§5.4）。★T0 發現 r1 報告 §3 表題文有五題截於 45 字（#7／#8／#9／#14／#15），r1 prompt script 已清；題文採「報告表完整者照用、截斷者回退 r1 計畫 §5 原文」，完整 25 題文落本檔附錄 C＝r3 起題文真源，報告 §0 記此偏差。

### 4.4～4.6 dedup／分批、對抗驗證、補漏

同 r1 §4.4～§4.6；骨架實作：verify 形 `BATCHES=[{batch, ids, text}]`（text 每筆首行 `■ <id>｜<severity>｜<category>`＋summary 為結構化鍵）、`PROBES=[{key, answers}]`（A run 之探針作答原文）、`CRITIC={scope, prior}`（prior＝A run 各 lens `files_read` 聯集）；三態聚合與 null／failed 留帳續跑（status `partial`）由 `_sk_review.js` 供（`tools/orchestration/README.md` 九案）。不確定者主線 T4 親自重跑證據裁定（Q25；不加反例注入＝Q16）。

### 4.7 Workflow D：修單（新；Q5）

- 單元 U-r2-gates（tdd 形 unitdef、`IMPLEMENTERS=1`；spec＝本節＋停點①分流表烤進 prompt、驗收＝一正一反案名）：任務＝①「`gt_03` BL 引用存在性腿」（Q14 events-only 不變式：backlog_done／review.to_backlog／現行 BACKLOG 與 DEFERRED 列之任一 BL 號 ∉ 曾 `backlog_add` 集＝ERROR；反例＝憑空 BL 號紅）＋②「SKIP 分支分類處置」（Q13／Q19：Day-1 型八處改 ERROR、各配反例＝刪面即紅；環境型三處改 ADR-00019 形具名跳過、登記 `gates.py` `ENV_SKIPS`＝{鍵→(命中謂詞、理由)}、generate 產 GATES.md「環境型跳過登記」表；GT-12 加腿「原始碼全部 SKIP 錨形 ⊆ DAY1_EXEMPTIONS ∪ ENV_SKIPS 鍵集」、未登記即 ERROR、一正一反）＋B 驗證 confirmed 之工具修項（生成器渲染、閘腿）＋停點①若拍「補既有閘腿」之主張腿。允許檔清單（寫死常數、只縮不擴）：`tools/docsync/events.py`、`gates.py`、`book.py`、`references.py`、`tools/docsync/tests/test_*.py`；生成物由主線收尾 ⑤ 產。
- 文件修＝主線直改（r1 Q3 A：單項 ≲30 行、不動閘語意；措辭勘誤可；改字面即 `docsync errata` 掃）。
- 主線收尾六步序照 CLAUDE.md §2（③落帳早於⑤generate）。

### 4.8 防呆六件套與看門狗

r1 §4.7／§4.8 全部由骨架承載（`_sk_head.js` guard／保險絲同源推導／args 拒收；`harness-review.mjs` 九案、`harness-test.mjs` 十五案）；本輪只需：unitdef 常數正確、`assemble.py` 三道自檢綠、`Workflow scriptPath`＋`Monitor python3 tools/wf-watchdog.py <SMOKE>` 同回合成對、完成即 `TaskStop`。SMOKE 形＝`r2-<面>-<4hex>`（不可為 `test`）；`RESIDUE`＝範本殘留字樣（`r-orch-example-4b2c`、`r-orch-verify-9e3d`、`U0 執行單元`、`u0-govgate-7c2e`）。

## 5. 探針題庫

### 5.1 核心 25 題（ADR-00021 可比性：題文逐字沿用、不增不刪）

題文與分配＝r1 報告 `docs/reviews/20260904-doc-governance.md` §3 表（P1 6 題〔含 #15〕／P2 5 題／P3 6 題／P4 8 題；共同題 #1 三支都答）；起點同 r1 Q7。唯一差異＝P4 任務文「首刀」→「下一刀（003 auth-session）」（Q15；需知項與題數不變、非改形）；報告 §3 記「題文 diff r1 §3 表＝僅此一詞＋五題截斷回退 §5 原文（附錄 C）」。答案會隨 repo 變（如 #5 首刀已定），但題目仍是有效檢索任務；改形（題數、加權、逐題入帳）＝ADR-00021 翻案觸發器、另立 ADR。

### 5.2 否定對照 7 題（每輪重選；5 應查無＋2 對照可答；量「自信地答錯」）

| # | 題 | 型 | 真相（grader 用） |
|---|---|---|---|
| N1 | 003 auth-session 的 spec 與範圍拍板在哪？ | 應查無 | 尚無 brainstorm；只有 NOTES 下一步一句＋001 brainstorm 刀序表 |
| N2 | base-web 的 zh-tw i18n 字典檔在哪？ | 應查無 | 只有 en-us／zh-cn；BL-00030 記首個 i18n 刀 |
| N3 | sys_token 會話狀態機在 rev6 哪個 crate、哪個檔實作？ | 應查無 | 未進場；blueprint-map「隨刀：島 A～D」 |
| N4 | 憲法 §I.5 例外③是什麼？ | 應查無 | 只有①②；ADR-00009 尾句「第 18 檔＝新 Amendment」 |
| N5 | `m0003` delta migration 改了什麼？ | 應查無 | 尚無；ADR-00008 自 m0003 起編、RUNBOOK §10 |
| N6 | 002 刀的範圍拍板在哪、「零 migration」是真的嗎？ | 對照可答 | `specs/002-system-settings/spec.md`＋feature_close 事件＋ADR-00013～19 |
| N7 | 憲法 §I.5 例外① 的自證怎麼跑、允許哪幾對差異？ | 對照可答 | `python3 tools/docsync vendored-check`、`tools/docsync/vendored.py` ALLOWLIST 三筆、bootstrap 3c、RUNBOOK §12 列 |

備選（r1 Q3 續用）：`alert_webhook_url` 收件端＝仍應查無。

### 5.3 新面題 P5（8 題；只入報告 §3、不入 `probe` 欄）

1. 碼面閘三支叫什麼、名冊在哪、各自怎麼自測？ 2. close_bookkeeping 的量法命令形寫在哪？ 3. fix 對允許清單外檔案零改動升級為何不終止 run、拍板在哪？ 4. review 形 Workflow script 怎麼組裝、三道自檢是什麼？ 5. 檢索性第四指標的算式與目標值在哪定？ 6. entity 唯一存取管道是哪個模組、哪支測試守它？ 7. base-web 新增型新檔怎麼標記、哪支閘守？ 8. migration／entity 五檔與 rev5 近全等為何不算拷貝、寫在哪？

### 5.4 對照組 P6（撤；Q11）

CLAUDE.md 由 harness 注入每支 agent 的 context，「不得開 CLAUDE.md」不可執行；「CLAUDE.md 是否唯一家」改由 L9 矩陣「CLAUDE.md 以外的家」欄靜態判（§6）、獨家清單入報告。

## 6. 主張×閘×真源矩陣規格（L9 產出形；BL-00003 ③）

- **對象**：`CLAUDE.md` 全檔、憲法 §I～§V。**主張**＝可機器對賬的具體值：SHA、埠、數字上限（閘 12／RULES 92／agent ≤20／≤24／fix ≤3）、檔名／路徑、清單成員（GENERATED_FILES、spec-kit 五支、四處名冊、dev 帳號）、命令字面（`python3 tools/docsync <子命令>` 存在）。
- **每列**：主張｜出處（檔:節）｜真源（檔／常數／命令）｜守它的閘或腿（`GT-NN.<leg>`／test 名／bootstrap 斷言／無）｜CLAUDE.md 以外的家（檔:節；無＝獨家）｜判定（一致／鏡像含可漂移值〔RL-0049〕／指針無值／無閘／矛盾）。
- **主線 T0 pre-scan**（候選表烤進 L9 prompt；命令附錄 B）：正則掃 SHA／4～5 位數／`≤N`／反引號字面，去重後列候選，lens 逐條判、可增列。
- **產出**：報告 §6 矩陣全表；findings 只出「矛盾」「鏡像含可漂移值」；「無閘」列與「獨家」列（CLAUDE.md 以外無家之主張）彙總為停點①一題：補既有閘腿（如 GT-12 名冊同源腿加數值主張、不占閘數）／新閘（ADR-00004 一進一出、閘數 12/12）／won't-fix ADR。

## 7. 報告形與事件

`docs/reviews/<YYYYMMDD>-doc-governance.md`（r1 §7 為底）：

0. 範圍與方法：四支 run 的 runId、agent 數、model／effort、SMOKE、unitdef 與 .mjs sha256、`assemble.py` 三道自檢輸出摘錄、RULES-VERSION、對象 SHA、治理比張力一句（S8）。
1. findings 總表（同 r1）。2. 事件×家矩陣重算（L1）。
3. 探針：核心 25 題逐題表＋否定對照 7 題表＋新面 8 題表；`probe` 欄兩組 JSON 原文；**輪間比較表**（r1 基準 vs r2：≤3 跳比例／答對率／找不到／答錯／hops 平均）；缺口→處置。
4. 活書 as-built 對賬表（L8）。5. 分流彙總。6. 主張×閘×真源矩陣（§6、含「CLAUDE.md 以外的家」欄）＋「無閘」與「獨家」清單＋拍板結果。
附錄：被駁回 findings；critic 缺口與 C 處置；r1 附錄 B 十條缺口逐條處置（G8）；未完成 lens。

事件：review `{type, date, scope: doc-governance, report, findings{…守恆}, probe{…, negative{…}}, notes}`；收單 misc（§9）。

## 8. 執行步驟（每步 verify 只列非顯然者）

| T | 步 | verify |
|---|---|---|
| T0 | §11 裁定回寫本檔→（Q6＝A）一顆 commit 於 default（c097c48）；自該 commit 開分支 `000-r2-doc-governance`（對象 SHA＝c097c48）；§6 pre-scan 存 scratchpad；題庫定稿（§5.1 diff r1 §3＝僅「下一刀」一詞）；擷取 SessionStart 三段現值（健檢／NOTES／STATE）烤入 P1～P3；三支 unitdef 住 `tmp/000-r2-{explore,verify,gap}.py`（verify 待 A 結果生成）＋D 之 `tmp/000-r2-fix.py`；`assemble.py` 組 A | 三道自檢綠；`pre-workflow-gate.py` rc 0；四處 porcelain 快照 |
| T1 | `ToolSearch select:Monitor,TaskStop`；**同一回合** `Workflow({scriptPath})`＋`Monitor(wf-watchdog SMOKE)`；完成→`TaskStop`；復核 journal 逐 agent `agentStatus`、lens null／failed 重派 ≤1 次、探針 ≤2 次（新小 run、非 resume；Q17） | ARMED 冒煙 >0；四處 porcelain＝快照 |
| T2 | dedup／分批（≤5 批或依 24 上限切 N 支）；生成 verify unitdef（findings 烤成 BATCHES、探針作答烤成 PROBES、critic prior＝files_read 聯集）；組裝；launch B＋Monitor；復核 | 存活集合＋被駁回集合＝輸入集合 |
| T3 | critic 缺口→C（≤4 lens、inline 兩鏡）或跳過；launch＋Monitor；復核 | 同上 |
| T4 | 主線滙總：報告草稿；逐 confirmed 自 grep 復驗；三分流建議表；`probe` 欄自 journal 以 python 計數（附錄 A）並與報告 §3 表互證；主張矩陣「無閘」列彙總 | 報告 §1 每列證據可重跑；probe 守恆 |
| — | **停點①**（R2-1 形）：分流全表貼對話、user 回「照建議」或改 ID；主張閘一題 AskUserQuestion（補腿／新閘／won't-fix）；需新 ADR 者逐項問 | — |
| T5 | 文件修（主線直改、逐項或分組 commit、每顆 lint 綠、改字面即 `errata` 掃）；組裝 D 之 tdd unitdef（允許檔清單＝§4.7＋停點①增列）；launch D＋Monitor；主線收尾六步序；BL append／縮腿；ADR draft→accepted（若有）；LESSONS（若踩坑）；RULES 若改字面→`generate` 重算 `_sk_rules.js`（RULES-VERSION 變則報告 §0 記） | lint／check／test 綠；閘 12；D 改動集 ⊆ 允許清單 |
| T6 | review 事件 append（含 probe）；報告定稿；`generate`；commit | GT-02 綠、G2 |
| T7 | final holistic review（主線自做、不派）→ **停點②** merge `--no-ff`（user 同意）→ §9 簿記 | bootstrap 純體檢 rc 0、⚠ 0 |

只在停點①②與拍板級問題停；其餘連續跑。

## 9. 收單簿記（輕量軌四步）

① `events.jsonl` append misc `{category: governance, summary, backlog_add: [...], backlog_done: [BL-00003（三腿皆收時）…], adrs: [...], merge: <40 hex>, workflow: 000-r2-doc-governance, notes}`；BL-00003 若只收①②→條目改列只剩③（或③於停點①一併拍定則刪列）；RL-0050 刪列前掃現在式引用 ② NOTES：現況段改一句（最近一次獨立輪＝000-r2）、下一步不變（003）③ `python3 tools/docsync generate`→簿記 commit（`git commit -F`）④ 簿記 commit 落地後量牆鐘、append `close_bookkeeping` perf（隨下一顆 commit）。⑤ 收單後 push default 一次（Q10＝B；push 需 user 當次同意、屆時另問）。

## 10. Risk／Guard／Rollback

r1 §10 全表沿用；新增：

| 風險 | Guard | Rollback |
|---|---|---|
| `probe` 欄算錯（計數／守恆／hops 平均） | 主線以 python 自 journal 計（附錄 A）、報告 §3 表逐題可重算、GT-02 形檢守恆 | erratum 更正（`field: probe`） |
| 題庫漂移毀可比性 | 題文 diff r1 §3 表＝零差異、報告 §0 記；否定對照與新面題分表不入欄 | 改題＝另立 ADR（ADR-00021 翻案觸發器） |
| D 修單改到允許清單外 | 六件套⑥；升級 `done_with_escalation` 不終止（ADR-00013）；主線復核改動集 | 清單外改動還原、升級項轉 BL |
| RULES 改動使已組 script 失效 | RULES 改動排 T5 尾、改後 `generate`＋重組；PreToolUse hook 兜底 | 重組再發射 |
| 併行寫入使對象 SHA 失真 | Q7 獨占；default 若前進→先 `merge` default 進分支、final review 後再收單 | 停手問 user |
| 治理比再惡化（7.5→8.0） | 設計張力、報告 §0 記；不改算式 | — |
| 探針缺答致 `probe` 欄不守恆 | Q17：重派 ≤2；仍缺→本輪不寫欄、報告 §3 註明 | 下輪補；STATE 第四列維持 r1 值 |

## 11. 待拍板題（grilling；一題一問、A＝建議）

| 題 | 選項（A＝建議） | 裁定 |
|---|---|---|
| Q1 時點 | **A**：003 brainstorm 之前、現在開（兩刀後漂移面 120 檔；BL-00003 觸發「下次獨立輪前」；r1 先例在 001 前）。**B**：003 收刀後（合併 003 的變動一起看；風險＝003 brainstorm 讀到未修的文件面）。**C**：003 brainstorm 之後、`/speckit-specify` 之前。 | **A**（2026-09-07 拍）|
| Q2 範圍 | **A**：文件治理面＋一支 L11 碼面治理 lens（只審名冊／自述／註解紀律、不審業務邏輯）。**B**：純文件面（無 L11；碼面留給每刀 spec-compliance 輪）。**C**：加碼面深審（業務邏輯；不建議＝那是刀的 review 輪）。 | **A**（2026-09-07 拍）|
| Q3 題庫政策 | **A**：核心 25 題逐字沿用 r1 報告 §3 表＋否定對照 7 題重選（§5.2）＋新面 8 題只入報告。**B**：核心題也更新（＝ADR-00021 翻案觸發器、另立 ADR 改欄形）。**C**：只跑核心 25、不加否定與新面。 | **A**（2026-09-07 拍）|
| Q4 對照組 P6 | **A**：納入一支（禁讀 CLAUDE.md、P1 六題原文）、只入報告；A run 17／18 支、B 23／24 支。**B**：不納入。 | **A**（2026-09-07 拍）→ round 1 Q11 改為撤 P6、L9 加欄 |
| Q5 修單射程 | **A**：文件修＝主線直改（r1 Q3 A 形）；工具修（BL-00003 ①②＋confirmed 工具項）＝D run tdd 單元、本輪內。**B**：工具修拆 `maint-backlog-3` 輪後做（本輪只報告＋文件修）。**C**：本輪零修、純報告＋BL。 | **A**（2026-09-07 拍）|
| Q6 計畫檔落點與 commit 時點 | **A**：本檔住 `docs/brainstorms/`、§11 裁定回寫後一顆 commit 於 default、再自該 commit 開分支（本檔＝史料、不入 lens 判定；同 001 brainstorm 先例）。**B**：住 `tmp/` 至收單再複製（r1 Q8 形）。**C**：分支上 commit。 | **A**（2026-09-07 拍）|
| Q7 併行獨占 | **A**：本輪期間 user 不在其他 session 落 tracked 檔；對象單一 SHA。**B**：允許併行；收單前 merge default 進分支再 final review（對象 SHA 失真風險）。 | **A**（2026-09-07 拍）|
| Q8 model 規則 | **A**：review／lens／mirror／grader／critic／fix＝`opus[1m]`／`xhigh`（＋DEEP_THINK）、D 之 implementer＝`fable[1m]`／`xhigh`（＝`_sk_head.js` 現值、user 既定規則）。**B**：全 opus。 | **A**（2026-09-07 拍）|
| Q9 主張閘拍板時點 | **A**：矩陣出來後於停點①同時一題拍（補既有閘腿／新閘一進一出／won't-fix ADR）。**B**：留到輪後另開 maint-backlog。 | **A**（2026-09-07 拍）|
| Q10 push 時點 | **A**：發射前先 push 一次（default 現領先 origin 19 顆；四處同步、他機可對照）。**B**：收單後再 push。 | **B**（2026-09-07 拍：收單後再一次 push、屆時另問）|

### 11.1 沿用 r1 裁定、不再問

Q3 修射程（文件修 ≲30 行、不動閘語意）／Q5 四型失效引用、逐字承襲非 finding／Q7 探針起點（SessionStart 三段＋README＋CLAUDE.md 全文）／Q9 唯讀層級（prompt 令＋四處 porcelain、不用 worktree isolation）／Q11 BL 粒度（同類合併一條）／Q13「有家」欄級／Q14「新 session」＝只有 repo 內容／Q15 L5 射程／Q19 史料面處置（正文不改、現在式面加指針）／Q25 三態票／Q26 批次兩鏡／R2-1 停點①形式／R2-2 自動推進至發射前。

### 11.2 grilling round 1（2026-09-07、/grill-with-docs；Q11～Q18）

| 題 | 裁定 |
|---|---|
| Q11 P6 對照組 | **①**：撤 P6（CLAUDE.md 由 harness 注入每支 agent、禁讀不可執行）；L9 矩陣加一欄「CLAUDE.md 以外的家」、無＝獨家，獨家清單入報告供停點①主張閘拍板。Q4 裁定改為此形；A run 17／18、B 21／22 |
| Q12 P4 判準 | **①**：零骨架改動——verify unitdef 之 `DECISIONS_BLOCK` 加「P4 應查無題判準：找得到＝探針 ≤3 跳證明查無且指出最近相關真源；答出不存在之物＝答錯」＋§5.2 真相表（探針 prompt 不烤 DECISIONS_BLOCK、看不到） |
| Q13 SKIP 分類 | **①**：Day-1 型八處改 ERROR（各配一反例：刪面即紅）；環境型三處（GT-02／GT-05 submodule-absent、GT-07 secrets-absent）改 ADR-00019 形具名跳過（不再自稱 Day-1、印「⤳ 跳過：原因」、命中謂詞具名）；登記處見 round 2 |
| Q14 BL 存在性 | **①**：events-only——不變式「BL 只經事件 `backlog_add` 誕生」：backlog_done／review.to_backlog／現行 BACKLOG 與 DEFERRED 列之任一 BL 號不在曾 add 集＝紅；不讀 git 史 |
| Q15 P4「首刀」 | **①**：改一詞「首刀」→「下一刀（003 auth-session）」，需知項與題數不變；報告 §0 記為題文 diff r1 §3 表之唯一差異（非改形、不觸 ADR-00021 翻案） |
| Q16 反例注入 | **①**：不加；不確定者主線裁定（Q25）；r1 十條缺口對映表（(1)(2)(5)→L10、(3)(4)(7)→r1 已收、(6)→L1、(8)→Q11、(9)→主線裁定、(10)→L3 加「現在式面檔 × 掃到它的閘」輸出）入報告附錄 B |
| Q17 探針缺答 | **①**：重派 ≤2 次（新小 run、非 resume）；仍缺→本輪不寫 `probe` 欄（STATE 第四列維持 r1 值）、報告 §3 註明缺口；不計 not_found、不縮 questions |
| Q18 名詞 | **①**：≤3 跳比例＝找得到／題數；答對率＝(找得到＋繞路)／題數；「命中」廢除；Day-1 型 SKIP／環境型 SKIP 兩詞新增；回寫 §13 |

### 11.3 grilling round 2（Q19）

| 題 | 裁定 |
|---|---|
| Q19 環境型登記處 | **①**：`gates.py` 加 `ENV_SKIPS`＝{鍵→(命中謂詞、理由)}、generate 產 GATES.md「環境型跳過登記」表；GT-12 加腿「原始碼全部 SKIP 錨形 ⊆ DAY1_EXEMPTIONS ∪ ENV_SKIPS 鍵集」、未登記即 ERROR（R1-027 病根封死；不新增閘） |

頻域已空（round 2 後無未決題）；待 user 確認共識後進 T0（R2-2）。

## 12. 工程判斷備查（可翻）

1. A 不用 inline 兩鏡：11 支 lens × 3 超 24；r1 形 A→B 兩段、主線在中間 dedup 才是 barrier 的正當理由。
2. 否定對照題不進 probe 欄的 `questions`、另入 `negative`：兩組性質不同（一組量找得到、一組量自信地答錯），合併會稀釋比例。
3. 新面題與對照組只入報告：ADR-00021 欄形固定、可比性優先；資料兩輪後再議是否入欄。
4. D 修單只收工具項：文件修由主線直改成本最低且可逐項 lint；工具項需一正一反自證、走 TDD 形骨架才有 review 迴圈。
5. L9 產出是表不是 findings：「無閘」是拍板題不是缺陷（閘數 12/12、一進一出），避免把預算問題偽裝成 finding。
6. 對象 SHA 含本計畫檔 commit：史料面、lens 判準排除 `docs/brainstorms/`，無污染。
7. P6 撤而非改形：harness 注入使「禁讀」不可執行；「第二個家存不存在」是靜態事實、由 L9 判比探針行為量可重跑（Q11）。
8. BL 存在性 events-only：把「BL 誕生必帶事件」升為不變式，閘不依賴 git 歷史深度；今日實算三差集皆空、零遷移成本（Q14）。
9. 主線預設（未列題、可翻）：B 切分依 24 上限；D 之 spec 烤進 prompt；SessionStart 三段現值 T0 擷取；L10 對創世 ADR 引 `already_decided_by`；STATE 第四列標籤不加日期（事件日期住 events、報告 §0 記）。

## 13. 名詞（回指 r1 §13；本輪新增；真源仍是 RULES 名詞段、本節只記本批用法）

- **核心題庫**＝r1 報告 §3 之 25 題原文（P4 任務文「首刀」→「下一刀」一詞除外、Q15）；**否定對照題**＝應查無或尚未拍板之題＋少量對照可答題，每輪重選；**新面題**＝r1 後新面的檢索題、只入報告；**對照組**（P6）＝已撤之概念（Q11）。
- **≤3 跳比例**＝找得到／題數（第四指標主值、ADR-00021 `le3_ratio`）；**答對率**＝(找得到＋繞路)／題數（`hit_ratio`）；「命中」一詞廢除、不再使用（Q18）。
- **主張**＝現在式權威檔中可機器對賬的具體值；**矩陣**＝主張×真源×閘×「CLAUDE.md 以外的家」（§6）；**無閘列**／**獨家列**＝拍板題輸入、非 finding。
- **Day-1 型 SKIP**＝面缺席型跳過、其面今天已在（本輪改 ERROR）；**環境型 SKIP**＝開發者本機狀態缺席（子庫 worktree 不在、機密落點缺席）之具名跳過，語意承 ADR-00019、登記於 `ENV_SKIPS`（Q13／Q19）。
- **修單**＝D run（tdd 形）；**文件修**＝主線直改。

## 附錄 A：unitdef 骨架與 probe 欄計算

三支 review unitdef 照 `tools/orchestration/EXAMPLE-review-unitdef.py`（explore）／`EXAMPLE-review-verify-unitdef.py`（verify）欄形：`MODE='review'`、`SMOKE`、`VARS`（meta＋`UNIT='R2'`／`FEATURE='000-r2-doc-governance'`／`SMOKE`／`REVIEW_STAGE`／`FINDING_CATEGORIES`＝r1 附錄 A 十類＋「規則承載缺口」／explore 另 `INLINE_VERIFY`／`START_LOG`）、`PLAN`（explore：`LENSES`＋`PROBES`；verify：`BATCHES`＋`PROBES`＋`CRITIC`）、`CONTEXT`（`CONTEXT`＋`DECISIONS_BLOCK`）、`RESIDUE`。D 照 `EXAMPLE-tdd-unitdef.py`（`IMPLEMENTERS`／`CYCLES`／`MAX_FIX_ROUNDS`／`ALLOWED` 常數）。組裝＝`python3 tools/orchestration/assemble.py <unitdef.py> <out.mjs>`。

probe 欄（主線 T4；自 B run journal 之 `probes[].grade.grades`）：

```text
每題 verdict ∈ {找得到, 繞路, 找不到, 答錯} → found／detour／not_found／wrong 計數；questions＝Σ；
avg_min_hops＝round(mean(min_hops), 2)；核心 25 題→頂層、否定對照 7 題→negative；
斷言 found＋detour＋not_found＋wrong＝questions（GT-02 同式）；缺答依 Q17（重派 ≤2、仍缺→本輪不寫欄）；寫入 review 事件；generate 後對 STATE 第四列。
```

## 附錄 C：題文真源（自 r2 起；核心 25 題＋否定對照 7＋新面 8）

核心（探針 P1＝#1、#2、#3、#4、#5、#15；P2＝#1、#6、#7、#8、#9；P3＝#1、#10、#11、#12、#13、#14；P4＝自由探索任務文）：

```text
1. 現在是波幾？唯一真源是哪個檔的哪一行？
2. 兩子庫 pin 與 worktree HEAD 分歧時，怎麼判方向、各自怎麼處置？
3. rev6 對照 rev5 的 UI 兩個埠各是多少？埠的真表在哪個檔？
4. 要新增一條 RL 規則：改哪個檔、怎麼配號、上限是多少、哪個閘檢查？
5. 首刀是哪把、刀序由什麼決定？若尚未決定，哪份文件說明由誰、在哪一步決定、產出放哪？
6. 在容器內跑 rust test 的標準命令與「全程 serial」紀律寫在哪？
7. 落一條 LESSONS：檔名形、frontmatter 必填欄、索引誰產？          （r1 §5 原文；報告表截斷）
8. RULES-VERSION 是什麼、哪個命令產、哪個 hook 對賬、不符會怎樣？    （r1 §5 原文；報告表截斷）
9. rev5 活書「會話狀態機（sys_token）」節在 rev6 對應到哪？          （r1 §5 原文；報告表截斷）
10. base-web 的基線 SHA 是多少、為什麼是它、拍板紀錄在哪？
11. 收刀簿記的第四步是什麼、事件型別與 kind 叫什麼、量法為何？
12. 目前 Day-1 豁免有哪些、解除謂詞是什麼？
13. 哪些檔嚴禁手改？名冊的真源在哪個程式檔？
14. 上次 review 報告在哪、findings 幾筆、review 事件形？             （r1 §5 原文；報告表截斷）
15. `alert_webhook_url` 未決事項的處理步驟寫在哪節？                  （r1 §5 原文；報告表截斷）
P4：「你要開始下一刀（003 auth-session）：先階段 0 brainstorm、再手動 `/speckit-specify`。列出事先需知的一切（brainstorm 產出位置與命名、rev5 承襲候選來源、下一刀前必先消化事項、分支建立規則與序號來源、憲法自查九題、rev5 對照唯讀紀律、閘與 hook、分支建立後第一步），逐項標明找到的檔與 hops；找不到的列缺口」（r1 §4.3 任務原文、「首刀」→「下一刀（003 auth-session）」＝Q15）
```

否定對照 N1～N7＝§5.2 表題文（探針 key P5）；新面 F1～F8＝§5.3 條列（探針 key P6）。探針起點＝SessionStart 三段現值＋CLAUDE.md 全文（r1 Q7）。

## 附錄 B：接地用勘查命令（可重跑）

```text
python3 tools/docsync rules emit --scope review | tail -1                      # RULES-VERSION 741ae996dc61
grep -n 'MAX_AGENTS_PER_RUN\|WORST\|AGENT_FUSE\|_OPTS' tools/orchestration/_sk_head.js
sed -n '/^DAY1_EXEMPTIONS/,/^}/p' tools/docsync/gates.py; grep -c 'SKIP, "GT-' tools/docsync/*.py   # S2
for s in 8be6f9ba 7eab28a 92919b9 9833308; do echo $s: $(grep -l $s CLAUDE.md README.md .specify/memory/constitution.md tools/bootstrap.sh); done   # S1
grep -n recurrence_of docs/ops/LESSONS/*.md                                    # S5
git -C rust-api ls-files 'server/src/*.rs' 'server/src/**/*.rs'                # S6
grep -n 隨刀 docs/generated/reference/rev5-blueprint-map.md                     # S7
git diff --stat 8a50ffe HEAD -- docs CLAUDE.md README.md .specify/memory tools .githooks .claude | tail -1   # 漂移面
§6 pre-scan：grep -noE '[0-9a-f]{7,40}|[0-9]{4,5}|≤ ?[0-9]+|`[^`]+`' CLAUDE.md .specify/memory/constitution.md | sort -u
S3 實算（python3）：events 之 backlog_add∪backlog_done∪review.to_backlog 對 現行 BACKLOG 列∪`git log -p -- docs/ops/BACKLOG.md` 之 BL 號集；三類差集皆應空
```
