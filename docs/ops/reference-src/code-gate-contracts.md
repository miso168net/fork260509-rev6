# code-gate-contracts.md — 碼面閘行為契約（跨刀活體；跨刀名冊＝RUNBOOK §12 碼面閘表）

> **本檔＝下列碼面閘的跨刀活體行為契約家**（ADR-00041）：閘還在跑、契約就還在前進，現在式面一律引本檔。
> 凍結存證＝各刀 spec 目錄的對應節（逐節於下方標出處、不再前進）。形制承 ADR-00012。
> ★收錄判準＝「該閘是跨刀常設、其行為契約會隨刀前進」；各刀 spec 的施工面節（pre-commit 改動、ADR 清單、帳本）不收、留在該刀。

## §1 `tools/wire-schema.py` 行為契約

> 凍結存證＝`specs/002-system-settings/contracts/code-gates.md` §1.2。


- 子命令：`extract`（base-web 容器內 `npx -y typescript-json-schema@0.67.4 "src/typings/{common,api/*}.d.ts" "*" --ignoreErrors --required --strictNullChecks` → draft-07 快照、原子替換寫 `rust-api/server/tests/fixtures/wire-schema.json`；需 stack 在跑；輸出確定性）；`check [--staged-gate]`（重抽至暫存、與工作樹快照 byte 比對、絕不覆寫；`--staged-gate`＝staged base-web gitlink 區間零 typings 變動即跳過）；`test`。
- 唯讀鐵則：npx 一次性、不碰 base-web 工作樹／package.json／pnpm lock；前端 porcelain 前後皆空。
- rc：check 0＝一致或具名跳過（docker 缺／`base-web` 容器未起／staged-gate 零變動；clarify Q5）；2＝重抽失敗或不一致；extract 2＝stack 不在或 npx 非零（不寫部分結果）；64 用法錯。
- rev6 座標核對＝compose 兩檔名、`base-web` 服務名與 `-w /app`（皆同 rev5）；typings glob 零改（已涵蓋 `api/rev6-*.d.ts`）。
- pre-commit 觸發：staged 含 `base-web`（gitlink）即 `check --staged-gate`。

## §2 wire 快照與覆蓋閘契約

> 凍結存證＝`specs/002-system-settings/contracts/wire-settings.md` §4；★「受審 definitions」與「本刀 case 集」兩項為 002 當下的枚舉、隨刀前進（現況查 `rust-api/server/tests/fixtures/wire-schema.json` 與 `server/tests/contract.rs`）。


- 快照產製：`python3 tools/wire-schema.py extract`（base-web 容器內 `npx typescript-json-schema@0.67.4` 唯讀抽取、`--strictNullChecks`、原子替換寫入
  `rust-api/server/tests/fixtures/wire-schema.json`；需 stack 在跑）；drift 閘＝`check`（重抽 byte 比對；pre-commit `--staged-gate` 收窄：staged base-web gitlink 區間零 typings 變動即跳過；
  ★docker 缺或 `base-web` 容器未起＝具名跳過 rc 0、容器在而重抽失敗或不一致＝rc 2——clarify Q5）。
- 受審 definitions（002 刀新增）：`Api.SystemManage.SystemSetting`（讀端序列化輸出必過；★description 不含 null）＋`Api.SystemManage.UpdateSystemSettingReq`
  （service 送出形錨定；description 呈 `["null","string"]`）。
- 覆蓋閘：`server/tests/contract.rs` case registry 與 `router::ROUTES` 之 case_key **雙向**比對——每條 route 必有 case（缺即紅指名）、每個 case 必對 route（殭屍即紅指名）。002 刀 case 集恰四：health／metrics／get-system-settings／update-system-setting。
- 負向自證（DoD）：抽掉 update-system-setting 案→紅指名→還原全綠；加一殭屍案→紅指名→還原。

## §3 `tools/view-render-guard.py`／`tools/route-artifact-gate.py` 行為契約

> 凍結存證＝`specs/004-ip-trust-anchor/contracts/code-gates.md` §2。


① `tools/view-render-guard.py`（承 `rev5:tools/view-render-guard.py` 282 行、新寫）：射程 `base-web/src/views/manage/**`；零 `v-html`／`innerHTML`／`outerHTML` 用法；環境缺席語意＝base-web 工作樹缺席即 fail-loud（ADR-00019 形）。
② `tools/route-artifact-gate.py`（承 `rev5:tools/route-artifact-gate.py` 605 行、新寫）：於 base-web 容器內**沙盒**重跑路由外掛重算（不就地改工作樹＝pre-commit 各閘唯讀）後與版控產物四檔 byte 比對＝冪等，另以上游基線為種重算一腿承擔「手改一行即紅」（外掛對 `routes.ts` 為增量合併、版控為種時手改行存活；★勘誤 2026-09-20：原文「容器外以 `pnpm` 重跑…後 `git diff --quiet`」——`node_modules` 住容器、`pnpm gen-route` 為互動腳手架非重算指令〔`rev5:L-053`〕）；斷言「憲法 §III.2 該軌道列所列產物檔集＝外掛實際產出檔集」（雙向差集即紅）；環境缺席（無 node）＝具名跳過（pre-commit 條件段）。
★接線與名冊落點屬各刀施工面、不收進本檔（ADR-00041 決定 2）；現況真源＝RUNBOOK §12 碼面閘表與 `tools/docsync/tests/test_hook_wiring.py` 的 SEGMENTS。

## §4 `tools/fork-delta-lint.py` 行為契約

> 凍結存證＝`specs/002-system-settings/contracts/code-gates.md` §1.3。

- 掃描面：base-web `src/` 之 .ts／.vue＋`build/` 之 .ts＋根層 `.env*`；基線＝源倉 `fork260509-soybean-admin-base/` @ `example` tip（bootstrap 斷言在場）。
- 兩腿：修改型缺「原行:」（002 刀 vacuous——零 inline）；新增型缺圈界標記（本刀兩新檔）。授權判定＝憲法 §III.2 ★軌道（軌道×用途×檔案）三元組硬邊界＋§III.1 三軌道範圍收窄（ADAPT 修改型限根層 `.env*`；WRAPPER 掃描面內不可修改型）；新增檔標記所稱軌道與檔路徑不符＝紅。
- ★標記字面（新增型檔頭一行、契約定形）：`// [rev6-inline <軌道名>+ <刀名>] <一句話理由>`——token `rev6-inline`（CLAUDE.md §1）、`+` 尾綴＝新增型、軌道名 ∈ 憲法 §III.1 表首欄字面（`BASE-WEB-ADAPT`／`BASE-WEB-WRAPPER`）、刀名＝`002-system-settings`。
- ★結構斷言改形（brainstorm Q5）：名冊載入對 §III.2 ★段——零資料列時 MUST 命中哨兵句字面「（空表——尚無 ★ 軌道；首列隨首刀 Amendment 落入。）」、否則 ≥1 列；§III.1 恰 3 列與其餘斷言不變＋第⑥道（as-built 2026-09-05 U0 審查補）＝§III.1 三實名列範圍欄之反引號 token 集 ⇔ 工具常數 `S1_RANGE_LITERAL`（次序不計）、不符即 rc 2——Amendment 改範圍欄即紅、與 pre-commit 憲法觸發源連動；self-test 一正一反：合成憲法文本「零列＋哨兵句」＝綠、「零列＋無哨兵句」＝紅（守不消失）。日常一律用預設憲法路徑，`--constitution` 只供自身變異驗證。
- rc：0 綠／1 缺標記、缺原行或軌道外／2 結構斷言敗（名冊載入失敗）；源倉缺席或未切在 `example`＝rc 2 fail-loud（`assert_baseline` die；bootstrap 已斷言在場、正常不觸——as-built 校正 2026-09-05 U0：原句「具名跳過」與碼相反，rev5 原檔同為 die、fail-loud 方向較安全）。
- pre-commit 觸發：staged 含 `base-web`、`tools/fork-delta-lint.py` 或 `.specify/memory/constitution.md`。

## §5 `tools/msg-key-gate.py` 跨端閘契約

> 凍結存證＝`specs/003-auth-session/contracts/code-gates.md` §2。

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

**接線落點**：屬施工面、不收進本檔（ADR-00041 決定 2）；現況真源＝RUNBOOK §12 碼面閘表與 `tools/docsync/tests/test_hook_wiring.py` 的 SEGMENTS（凍結存證那份列有 003 刀當時的五處清單）。

## §6 docsync routes 生成器契約

> 凍結存證＝`specs/002-system-settings/contracts/code-gates.md` §4。

- 來源＝`rust-api/server/src/router.rs` 之 `ROUTES` const；解析窄假設＝data-model §4 機器契約（精確開頭、每欄一行、枚舉字面）；來源檔缺席或任一偏離＝raise（fail-loud、generate 非零、GT-01 連帶紅）——U1 落地後 router.rs 永不缺席、不設 Day-1 豁免。
- 輸出＝`docs/generated/reference/routes.md`：生成標記檔頭＋「來源＝… ROUTES const（generate 重算；handler 閉包不入表）」＋表 `| path | method | protection | case_key | envelope 例外 |`（列序＝ROUTES 宣告序）。
- 名冊：GENERATED_FILES 14→15；README `docs/generated/` 成員行加 `routes`（GT-09 成員對賬腿守）；`tests/test_references.py` 一正一反（合成四條 ROUTES 文本→表；缺精確開頭／未知枚舉→raise）。
