# Contract — 治理面：fork-delta 標記、跨端閘、走查基準工具、hook 接線守衛、名冊登記、ADR（003-auth-session）

本檔＝治理與工具面的行為契約（spec FR-027～FR-039）；設計理由住 `../research.md` R8～R12、不重複。憲法 Amendment 的**條文全文**住 ADR-00026 draft（`docs/arc42/decisions/ADR-00026-constitution-amendment-star-tracks-and-behavior-islands.md`、status proposed）。

## §1 fork-delta 標記字面（憲法 §III；機器強制＝`tools/fork-delta-lint.py`）

| 型 | 檔類 | 標記形（逐字） |
|---|---|---|
| 修改型（★軌道） | `.ts`／`.vue` script | `// [rev6-inline BASE-WEB-AUTH-WIRING(a) 003-auth-session] 原行: <基線該行原文>`（緊鄰新行之上） |
| 修改型（★軌道） | `.vue` template | `<!-- [rev6-inline BASE-WEB-LOGIN-CAPTCHA-WIRING(i) 003-auth-session] 原行: <基線該行原文> -->` |
| 修改型（ADAPT） | `.env`／`.env.test`／`.env.prod` | `# [rev6-inline BASE-WEB-ADAPT 003-auth-session] 原行: VITE_AUTH_ROUTE_MODE=static`（裸形、無用途後綴） |
| 新增型（區塊） | 既有檔內插入塊 | 塊首 `// [rev6-inline BASE-WEB-I18N-WIRING(ii)+ 003-auth-session] <理由>`、塊尾 `// [/rev6-inline]`（圈界形沿 002 既有慣例） |
| 新增型（新檔） | `rev6-auth.d.ts`／`rev6-auth.ts`／`zh-tw.ts` | 檔頭一行 `// [rev6-inline BASE-WEB-ADAPT+ 003-auth-session] …`／`BASE-WEB-WRAPPER+`／`BASE-WEB-I18N-WIRING+`（不入名冊） |

- 用途識別符 MUST ∈ ADR-00026 表列（AUTH a／b／c、LOGIN-CAPTCHA i、I18N i／ii／iii、LOGOUT-UX i）；檔 MUST ∈ 該用途範圍欄——三元組硬邊界、違者 rc 1。
- `.env*` 在射程內（`S1_NEW_FILE_FACE` 含根層 `.env*`）＝機器守；`原行:` 後內容＝基線該行（正規化後相等）。
- 自證四腿（spec FR-030／SC-009；tasks 排入、每腿還原後 `git -C base-web status --porcelain` 零差異＝RL-0005）：①名冊內過＝真 repo 首跑 rc 0 ②名冊外攔＝某修改型標記軌道名改名冊外之名（如 `BASE-WEB-MANAGE-PAGE-WIRING`）→ rc 1 ③用途外攔＝`(a)`→`(z)` → rc 1 ④檔外攔＝把 `BASE-WEB-AUTH-WIRING(a)` 標記搬到範圍欄外的既有檔（如 `src/hooks/business/captcha.ts`）→ rc 1。

## §2 msg key 跨端閘 `tools/msg-key-gate.py`（碼面閘；research R9；ADR 隨落）

| 面 | 契約 |
|---|---|
| 子命令 | `check`（預設）／`test`；`--rust <path>`／`--locales <dir>`（只供 self-test 注入、日常預設路徑） |
| 左源 | `rust-api/server/src/error.rs` 兩段解析（實碼形＝常數表＋常數引用陣列、零字面）：①`pub mod msg_key { pub const NAME: &str = "字面"; … }` 建 名稱→字面 映射 ②`pub const MSG_KEYS: [&str; N] = [ msg_key::NAME, … ];` 逐元素經映射解回字面（亦容直寫字面）；元素數≠N 或任一元素解不出（含常數表缺該名）＝rc 2 |
| 右源 | `base-web/src/locales/langs/{en-us,zh-cn,zh-tw}.ts` 各自 `backend: {` 區塊（錨＝獨佔一行、允許前置空白；brace 配對取塊；剝 `//`／`/* */` 註解與字串值後攤平鍵路徑以 `.` 串接） |
| 斷言 1 | 三檔各自 `set(backend) == set(MSG_KEYS)`；不等＝rc 1、逐檔指名「缺：…」「多：…」 |
| 斷言 2 | Biz 構造點守衛：`rust-api/server/src/**/*.rs` 生產區間（`#[cfg(test)]` 區塊以 brace 配對排除）內每處 `AppError::Biz(` MUST 緊接 `Cow::Borrowed(` 且引數為 ①字串字面 或 ②`msg_key::NAME` 常數（經左源映射解回字面）、解出之鍵 ∈ `MSG_KEYS`；動態構造（變數／`format!`／函式回傳）＝rc 1 指名檔:行。002 既有兩處（`validation.rs`）為常數形＝合法、零改動；本刀三個新 Biz 鍵亦用常數形 |
| rc | 0 綠／1 違規／2 結構異常（檔缺席、`MSG_KEYS` 解析失敗、backend 節缺席或 brace 不配對、比對面為空）／64 用法錯 |
| self-test | 合成樣本七案：三檔全等綠／某檔缺一鍵紅／某檔多一鍵紅／某檔缺 backend 節 rc 2／常數間接形解析成功／常數表缺該名 rc 2／動態 Biz 構造紅；真 repo 綠案（現行 `error.rs` 常數形） |
| 依賴 | Python 3 標準庫、零 docker |

**接線五處**：①`.githooks/pre-commit` 新段 `pc_run "msg-key-gate" python3 "$HOOK_DIR/../tools/msg-key-gate.py" check`（觸發＝`if echo "$staged" | grep -qxF -e 'rust-api' -e 'base-web' -e 'tools/msg-key-gate.py'`）②`tools/docsync/tests/test_hook_wiring.py` SEGMENTS 加列（新段須同批入名冊、否則「未登記段」紅）③★`.githooks/pre-commit` 之 `for t in …` 自測名冊加 `tools/msg-key-gate.py`（`test_hook_wiring` 斷言該名冊 ⊇ 碼面閘表 ∪ `NON_GATE_TOOLS`、缺即 docsync test 紅）④`tools/bootstrap.sh` 名冊（R11②推導後自動納入）⑤README 樹＋RUNBOOK §12 碼面閘表：註記列「msg key 跨端閘」改為工具檔列（首欄 `` `tools/msg-key-gate.py` ``、根據 ADR＝本刀跨端閘 ADR）——GT-12 碼面閘表腿自動對賬。

## §3 走查基準對賬工具 `tools/walkthrough-baseline.py`（隨遷工具；research R10；`NON_GATE_TOOLS`）

| 面 | 契約 |
|---|---|
| 子命令 | `snapshot <檔>`／`diff <檔>`／`test`；選項 `--user U`／`--db D`（預設同 `tools/schema-gate.py` 常數）；`<檔>` 必填、契約落點 `tmp/walkthrough-<日期>.json` |
| 三面 | ①public schema 全部表列數（表清單 information_schema 現算、單一 UNION ALL）②全部序列 `last_value`＋`is_called` ③redis `DBSIZE`＋逐前綴鍵數（SCAN 去重；前綴＝首個冒號前段） |
| 唯讀 | pg 只 SELECT（`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres psql …`）；redis 只 `DBSIZE`／`SCAN`（密碼只在容器內 sh 展開、host 零露出） |
| 目標 | ★只准指向 rev6 dev stack（compose 專案＝倉庫根、埠 3xxxx）；絕不指向 rev5 對照 stack（2xxxx） |
| rc | 0 全等／1 有差（列出差異表／序列／前綴＋末行摘要）／2 環境或結構異常（docker 不可執行、psql／redis 失敗、基準檔缺席或壞形、★比對面為空＝假綠）／64 用法錯 |
| 登記 | `tools/docsync/gates.py` `NON_GATE_TOOLS = ("tools/wf-watchdog.py", "tools/walkthrough-baseline.py")`；`tests/test_gates.py` 加一正一反（常數含該檔＝真 repo 綠；`patch.object` 抽掉＝GT-12 紅指名）；★`.githooks/pre-commit` 之 `for t in …` 自測名冊加列（進 `NON_GATE_TOOLS` 即落入 `test_hook_wiring` 聯集斷言）；bootstrap 名冊（R11②推導）；README 樹；RUNBOOK §12 工具鏈速查加列（需 stack＝snapshot／diff 是、test 否）＋§12 碼面閘表前言「`NON_GATE_TOOLS` 現＝`tools/wf-watchdog.py`」句改兩支＋檔頭「創世期章節現況」句之 §9c 自「指針章」移入「已補實文章」（人寫鏡像、`errata NON_GATE_TOOLS`／`errata 指針章` 復掃） |
| rev6 化 | 四型失效引用（research R10）：裸前代編號 `B-147`／`L-071`／`L-055`／`ADR 0010` → `rev5:` 前綴形，以 `book.py` 之 `BARE_REV5` 對遷入後全檔復掃零命中才算完成；「rev5 dev stack」→「rev6 dev stack」、「rev4 對照 stack」→「rev5 對照 stack」；前綴例句去 `cpwd:` |

**RUNBOOK §9c 實文（契約草案、tasks 落）**：
1. 走查前 `python3 tools/walkthrough-baseline.py snapshot tmp/walkthrough-<日期>.json`（rc 0）。
2. 走查（CDP 接 `127.0.0.1:9229`、開 32080；勿於秒內狂打 auth 端點——nginx `auth_limit` 5r/s burst 40 回 429）。
3. 清理（順序固定）：`single_session_default` 若翻過→以 002 寫端翻回 `off`；psql：`DELETE FROM session_event; DELETE FROM sys_token; DELETE FROM sys_login_attempt; UPDATE sys_user SET session_id = NULL; SELECT setval('sys_token_id_seq',1,false); SELECT setval('session_event_id_seq',1,false); SELECT setval('sys_login_attempt_id_seq',1,false);`；redis：依 `session:`／`throttle:` 前綴 SCAN＋DEL（不 FLUSHDB）；`system_settings` 四欄若被寫端改動→還原 seed 值。
4. `python3 tools/walkthrough-baseline.py diff tmp/walkthrough-<日期>.json` **rc 0 才算環境已還原**（三閘綠不算、`rev5:L-071` 招牌徵狀＝三閘綠而全量紅）；之後才跑 `python3 tools/schema-gate.py check`。
5. 判準：diff 列出的任一序列 `last_value` 差＝清理漏 setval；任一 redis 前綴差＝漏 DEL；`sys_user` 列數不變但 diff 不報 `session_id`（列數面、非欄值）⇒ 第 3 步 `session_id` 還原由 gate2 seed 逐列比對兜底。

## §4 BL-00037 ①②（research R11）

- ①`test_hook_wiring.py`：`HOOK` → `HOOKS = {pre-commit, pre-push, submodule/pre-push, lib/scan-range.sh}`；pre-push 兩支各斷言 `. "$HOOK_DIR/lib/scan-range.sh"`（外層）／`. "$HOOK_DIR/../.githooks/lib/scan-range.sh"`（子庫）、`SCAN_CONFIG="$HOOK_DIR/…/.gitleaks.toml"`、`scan_push_ranges || exit 1`；lib 斷言 `betterleaks git --config "$SCAN_CONFIG" --redact --verbose --exit-code 2 --log-opts=` 與四種範圍推導（一般更新／新分支首推／退階／刪除分支跳過）字面；一正多反。pre-commit selftest-docsync 觸發放寬為 `'^tools/docsync/\|^\.githooks/\|^\.githooks-submodule/'`（SEGMENTS 同批）。
- ②`tools/bootstrap.sh`：`run_tool_test` 現行十行無條件硬編＋一行 Day-1 條件分支，改自 `git -C "$ROOT" ls-files ':(glob)tools/*.py' ':(glob)deploy/*.py' | grep -v -e '^deploy/decrypt-secrets\.py$' -e '^deploy/secrets_common\.py$'` 推導（★git pathspec 的 `*` 會跨 `/`——裸 `'tools/*.py'` 命中 `tools/docsync/*.py` 與 `tools/orchestration/*.py`、`assemble.py test` 回 2 即 die；`:(glob)` magic 令 `*` 不跨層；`deploy/decrypt-secrets.py`＝Day-1 條件分支獨立處理、`deploy/secrets_common.py` 無 `test` 子命令，兩者顯式排除並註明）；`test_hook_wiring.py` 加 bootstrap 面案：斷言推導行字面（含 `:(glob)` 與兩排除）、docsync 三段、閘數斷言、`vendored-check` 字面存在（刪任一即紅）＋反例（推導行去 `:(glob)`→合成名冊多出 `tools/orchestration/assemble.py`→紅）。

## §5 BL-00026／BL-00041（research R12）

- BL-00026：`main.rs` 改兩敘述形（`sqlx_logging_level` 回 `&mut Self`、不可鏈進 `connect` 引數）：`let mut connect_options = ConnectOptions::new(&database_url); connect_options.sqlx_logging_level(log::LevelFilter::Debug); Database::connect(connect_options)`；刪自陳註解；`errata 不引 log crate` 復掃零殘留；root `Cargo.toml` workspace.dependencies 加 `log = "0.4.34"`＋`server/Cargo.toml` 加 `log = { workspace = true }`。
- BL-00041：兩處註解皆改 `` `rev5:002` `` 提及形（`test_kit.rs` 檔頭與 `system_settings.rs`；實查兩處皆「rev5 002」、BACKLOG 條文「rev5 001」為誤記、收刀改條文時訂正）；`tools/docsync/book.py` `SUB_SCAN` 加 `rev[45] [0-9]{3}` 粗篩＋`BARE_PREV_KNIFE_NUM` 精判（提及形豁免同外層）、註解改寫；`tests/test_book_ids.py` 補子庫腿一正一反。★子庫改動與外層同批、一次 pin bump。

## §6 RUNBOOK／README／bootstrap 名冊落點總表

| 落點 | 跨端閘 | 走查工具 |
|---|---|---|
| RUNBOOK §12 碼面閘表 | 註記列→工具檔列 | — |
| RUNBOOK §12 工具鏈速查 | 加列 | 加列 |
| RUNBOOK §9c | — | 指針章→實文（§3） |
| `tools/bootstrap.sh` | 推導納入 | 推導納入 |
| README 樹 | 加行 | 加行 |
| `NON_GATE_TOOLS` | — | 加 |
| pre-commit | 新段 | — |
| `test_hook_wiring.py` | SEGMENTS | — |
| `test_gates.py` | — | 一正一反 |
| `.githooks/pre-commit` `for t in …` 自測名冊 | 加列 | 加列（`test_hook_wiring` 聯集斷言） |
| RUNBOOK §12 碼面閘表前言（`NON_GATE_TOOLS` 現值句） | — | 現值改兩支 |
| RUNBOOK 檔頭「創世期章節現況」句 | — | §9c 自指針章移入已補實文章 |
| README 第 14 行憲法版本鏡像（U0、與 Amendment 同 commit） | 1.2.0→1.3.0＝ADR-00026 | — |
| `tools/fork-delta-lint.py` self_test 註解「rev6 §III.2 現為空表」（U0） | 改現在式 | — |

## §7 ADR 五筆（一決策一檔；序號＝落檔時取、現況 next＝ADR-00027；皆帶 rev5 provenance；刀內 proposed→accepted）

| # | 主題 | 時點 | 要點 |
|---|---|---|---|
| ADR-00026 | 憲法 Amendment 1.2.0→1.3.0（★軌道四條八用途＋島 A～E） | **plan 期 draft 已落**（proposed）；tasks 首個主線任務 user 親決→accepted | 條文全文在該檔；後果段含三分碼射程（R4） |
| ② | `AppState` 恰兩欄封條翻案→五欄 | U1 | 決定文＝clarify Q1；提及 `rev5:ADR 0029` 同位 |
| ③ | root `Cargo.toml` 不引 argon2 翻案＋server 依賴清單 | U1 | R1 雙源表為附錄；五支取最新之拍板紀錄（D1～D5） |
| ④ | 快速登入鈕已知態（Q4 拍板；帳＝BL-00049） | U11 | 記「保留＋記帳」與棄案；觸發綁 RUNBOOK §16 |
| ⑤ | msg key 跨端閘形制＝逐檔雙向全等、無白名單 | U9 | 決定文＝clarify Q2；與 ADR-00017 射程關係（「雙向必恆紅」指整本字典） |

收刀 `feature_close.adrs` 列全五筆。憲法版本恰 bump 一次。
