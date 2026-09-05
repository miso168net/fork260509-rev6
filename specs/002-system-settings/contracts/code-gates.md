# Contract — 碼面閘進場與治理組合拳（002-system-settings U0／U1）

> 本刀治理面的行為契約（spec FR-025～FR-030、US6）。三支工具本體＝RULES 名詞段「隨遷工具」自 rev5 整檔搬運（逐字允許、註解與字串之四型失效引用 rev6 化）；
> 名冊＝RUNBOOK §12 碼面閘表；「碼面閘」一詞入 RULES 名詞段（brainstorm Q8）。rc 慣例沿 RUNBOOK §12：0 綠或具名跳過／1 受測物紅／2 環境或結構異常／64 用法錯。

## §1 三支碼面閘行為契約

### §1.1 `tools/rust-fmt-gate.py`（承 rev5 427 行；rev5:ADR 0057 決定 3）

- 子命令：`check`（預設）＝容器內 `docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo fmt --all --check`（唯讀、絕不寫檔）；`test`＝離線 self-test（subprocess 全樁、毫秒級）。
- rc：0＝全格式化、或具名跳過（docker 不在 PATH／repo 根缺 compose 兩檔／`rust-api` 容器未在跑——印一行「⤳ 跳過：…」；clarify Q5）；1＝未格式化（逐段計數＋前幾行 diff 摘要＋補救命令 `… exec -T rust-api cargo fmt --all`）；2＝容器在而 cargo-fmt 缺（fail-loud；rev6 映像已裝 rustfmt component、預期不發生）。
- ★首跑守則：對 001 逐位元承襲 17 檔若紅→停手升 user（格式化即破 ADR-00009 條件①）；預期綠（rev5 92919b9 存量已 fmt、toolchain 1.96.1 同版）。
- pre-commit 觸發：staged 含 `rust-api`（gitlink）或 `tools/rust-fmt-gate.py`。

### §1.2 `tools/wire-schema.py`（承 rev5 650 行）

- 子命令：`extract`（base-web 容器內 `npx -y typescript-json-schema@0.67.4 "src/typings/{common,api/*}.d.ts" "*" --ignoreErrors --required --strictNullChecks` → draft-07 快照、原子替換寫 `rust-api/server/tests/fixtures/wire-schema.json`；需 stack 在跑；輸出確定性）；`check [--staged-gate]`（重抽至暫存、與工作樹快照 byte 比對、絕不覆寫；`--staged-gate`＝staged base-web gitlink 區間零 typings 變動即跳過）；`test`。
- 唯讀鐵則：npx 一次性、不碰 base-web 工作樹／package.json／pnpm lock；前端 porcelain 前後皆空。
- rc：check 0＝一致或具名跳過（docker 缺／`base-web` 容器未起／staged-gate 零變動；clarify Q5）；2＝重抽失敗或不一致；extract 2＝stack 不在或 npx 非零（不寫部分結果）；64 用法錯。
- rev6 座標核對＝compose 兩檔名、`base-web` 服務名與 `-w /app`（皆同 rev5）；typings glob 零改（已涵蓋 `api/rev6-*.d.ts`）。
- pre-commit 觸發：staged 含 `base-web`（gitlink）即 `check --staged-gate`。

### §1.3 `tools/fork-delta-lint.py`（承 rev5 1108 行）

- 掃描面：base-web `src/` 之 .ts／.vue＋`build/` 之 .ts＋根層 `.env*`；基線＝源倉 `fork260509-soybean-admin-base/` @ `example` tip（bootstrap 斷言在場）。
- 兩腿：修改型缺「原行:」（本刀 vacuous——零 inline）；新增型缺圈界標記（本刀兩新檔）。授權判定＝憲法 §III.2 ★軌道（軌道×用途×檔案）三元組硬邊界＋§III.1 三軌道範圍收窄（ADAPT 修改型限根層 `.env*`；WRAPPER 掃描面內不可修改型）；新增檔標記所稱軌道與檔路徑不符＝紅。
- ★標記字面（新增型檔頭一行、契約定形）：`// [rev6-inline <軌道名>+ <刀名>] <一句話理由>`——token `rev6-inline`（CLAUDE.md §1）、`+` 尾綴＝新增型、軌道名 ∈ 憲法 §III.1 表首欄字面（`BASE-WEB-ADAPT`／`BASE-WEB-WRAPPER`）、刀名＝`002-system-settings`。
- ★結構斷言改形（brainstorm Q5）：名冊載入對 §III.2 ★段——零資料列時 MUST 命中哨兵句字面「（空表——尚無 ★ 軌道；首列隨首刀 Amendment 落入。）」、否則 ≥1 列；§III.1 恰 3 列與其餘斷言不變；self-test 一正一反：合成憲法文本「零列＋哨兵句」＝綠、「零列＋無哨兵句」＝紅（守不消失）。日常一律用預設憲法路徑，`--constitution` 只供自身變異驗證。
- rc：0 綠／1 缺標記、缺原行或軌道外／2 結構斷言敗（名冊載入失敗）；源倉缺席或未切在 `example`＝rc 2 fail-loud（`assert_baseline` die；bootstrap 已斷言在場、正常不觸——as-built 校正 2026-09-05 U0：原句「具名跳過」與碼相反，rev5 原檔同為 die、fail-loud 方向較安全）。
- pre-commit 觸發：staged 含 `base-web`、`tools/fork-delta-lint.py` 或 `.specify/memory/constitution.md`。

## §2 pre-commit 六處改動契約（`.githooks/pre-commit`；雙錨 45／90 秒與並行 harness 不動）

| # | 段 | 觸發條件 | 命令 | rc 語意 |
|---|---|---|---|---|
| ① | 自測迴圈 for 名冊 | staged 含該工具本體 | `python3 <tool> test` | 紅即擋 |
| ② | rust-fmt | staged 含 `rust-api` 或該工具 | `python3 tools/rust-fmt-gate.py check` | §1.1 |
| ③ | wire-schema | staged 含 `base-web` | `python3 tools/wire-schema.py check --staged-gate` | §1.2 |
| ④ | fork-delta | staged 含 `base-web`、該工具或憲法 | `python3 tools/fork-delta-lint.py` | §1.3 |
| ⑤ | entity-drift | staged 含 `rust-api` 或快照 | 快照在場＝`entity-drift-gate.py check`；★快照缺席＝rc 2＋提示「跑 `python3 tools/docsync refresh` 照相」（BL-00010；原具名跳過分支移除） | 缺席即紅 |
| ⑥ | 檔頭第 2 行 | — | schema-frozen 觸發面陳述補 `schema-definition.md`（失準修單） | — |

- hook 面真演練（U0 收尾、LL-00003 形）：`git mv`／移走快照→`git add`→commit 被 ⑤ 擋且訊息含補救提示→`git checkout HEAD -- <快照>`→`git status --porcelain` 零差異。
- 失準修單射程＝`python3 tools/docsync errata schema-frozen` 全 repo 枚舉：現知 `.githooks/pre-commit` 檔頭第 2 行、README 守門句；`docs/process/P-E1-boundary.md`、`docs/process/P-C4-E3-materials-boundary.md` 只列段名未寫觸發面（掃後定、不動即記「非失準」）。

## §3 RUNBOOK §12 碼面閘表＋GT-12 新腿＋名詞段定義

- **表形**（§12 末段散文改表、置於工具鏈速查表之後）：`| 工具檔 | 守什麼 | 觸發時機（含環境缺席語意） | 根據 ADR |`；資料列＝`tools/schema-gate.py`、`tools/entity-drift-gate.py`、`tools/rust-fmt-gate.py`、`tools/wire-schema.py`、`tools/fork-delta-lint.py`（首欄反引號路徑）；另一列註記「msg key 跨端閘：延前端 i18n 刀、BACKLOG 承載」（首欄非路徑、GT-12 腿不計）。
- **GT-12 新腿判準**（`tools/docsync/gates.py` gt_12）：S_tools＝`tools/` 頂層 `*.py` tracked 檔集 − `NON_GATE_TOOLS`（常數、初值 `{"tools/wf-watchdog.py"}`）；S_table＝碼面閘表首欄反引號 `tools/…py` 集；S_tools ≠ S_table＝ERROR 雙向指名（多列／漏列）；表缺席或零資料列＝ERROR（RL-0051 掃描面空集合即紅）。docstring `face=` 加「RUNBOOK 碼面閘表」（GT-12 名冊同源、GATES.md 由 generate 重產）。`tests/test_gates.py` 一正一反（合成 RUNBOOK 含五列＝綠；刪一列／加幽靈列＝紅指名）。
- **名詞段定義字面**（brainstorm Q8；主線於 U0 派發前直改 `docs/ops/RULES.md` 名詞段、bump RULES-VERSION、`generate` 重產 `_sk_rules.js`）：
  「**碼面閘**＝`tools/` 頂層對子庫碼或跨端契約做 check 的系統面機器閘（隨刀進場、不計入 GT-12 治理閘預算、名冊＝RUNBOOK §12 碼面閘表；環境缺席＝具名跳過、工具缺席＝fail-loud）；**治理閘**＝GT-NN（名冊＝GATES.md）。」

## §4 docsync routes 生成器契約（U1；`tools/docsync/references.py`）

- 來源＝`rust-api/server/src/router.rs` 之 `ROUTES` const；解析窄假設＝data-model §4 機器契約（精確開頭、每欄一行、枚舉字面）；來源檔缺席或任一偏離＝raise（fail-loud、generate 非零、GT-01 連帶紅）——U1 落地後 router.rs 永不缺席、不設 Day-1 豁免。
- 輸出＝`docs/generated/reference/routes.md`：生成標記檔頭＋「來源＝… ROUTES const（generate 重算；handler 閉包不入表）」＋表 `| path | method | protection | case_key | envelope 例外 |`（列序＝ROUTES 宣告序）。
- 名冊：GENERATED_FILES 14→15；README `docs/generated/` 成員行加 `routes`（GT-09 成員對賬腿守）；`tests/test_references.py` 一正一反（合成四條 ROUTES 文本→表；缺精確開頭／未知枚舉→raise）。

## §5 entity_behavior_lint 機器錨契約（U1；BL-00008）

- 位置 `rust-api/server/tests/entity_behavior_lint.rs`（cargo test 形、容器內 serial）；受掃＝`rust-api/entity/src/` 全部 .rs。
- 判準：每個 `impl ActiveModelBehavior for ActiveModel` 體 MUST 為空（strip 行註解／文件註解／字串常值後再判；判頭同時錨 `impl` 前導與 `for` 後隨）；站點數 MUST 等於帶 `DeriveEntityModel` 之檔數（等式形、非字面常數）；關鍵檔逐檔指名在掃描面內（`sys_user.rs`、`system_settings.rs`）。
- 非 vacuous 防線：合成正例（塞 `fn before_save`／自訂 `new()`）必紅並指名檔與行；空集防線。

## §6 ADR 六筆（一決策一檔；序號自 ADR-00013 起於落檔時取；皆帶 rev5 provenance；刀內 proposed→accepted）

| # | 題名 | 承載決策 | provenance | 翻案觸發器 |
|---|---|---|---|---|
| ① | 部分更新三態約定（envelope 級） | data-model §8 | rev5:ADR 0023、brainstorm Q1 | create 語意也要鎖＝新 ADR |
| ② | 授權拒絕語意＋no-escalation seam | 5003＋純 key＋不揭露；掛點簽章 | rev5:ADR 0022 | 業務錯誤明細受眾邊界重評（no-escalation 本體刀） |
| ③ | 碼面閘名冊承載於 RUNBOOK §12＋GT-12 腿 | §3 | BL-00011、brainstorm Q3 | 碼面閘 ≥8 支或名冊需機器生成時另立生成檔 |
| ④ | msg key 跨端契約延前端 i18n 刀、002 後端側閉環 | data-model §6 名冊 | brainstorm Q4、rev5:Lint24 | 首個接 i18n 的前端刀進場 |
| ⑤ | entity 漂移段快照缺席即紅 | §2 ⑤ | BL-00010、brainstorm Q2 | docsync 改為捕例外即失去補償控制＝仍紅、無翻案 |
| ⑥ | 容器依賴型碼面閘之環境缺席語意＝具名跳過、工具缺席＝fail-loud | §1.1／§1.2 | clarify Q5、rev5:ADR 0057 決定 3 | pre-commit 改為需 stack 常駐時反轉 |
