# code-gate-contracts.md — 碼面閘行為契約（跨刀活體；跨刀名冊＝RUNBOOK §12 碼面閘表）

> **本檔＝下列碼面閘的跨刀活體行為契約家**（ADR-00041）：閘還在跑、契約就還在前進，現在式面一律引本檔。
> 凍結存證＝各刀 spec 目錄的對應節（逐節於下方標出處、不再前進）。形制承 ADR-00012。
> ★收錄判準＝「該閘是跨刀常設、其行為契約會隨刀前進」；各刀 spec 的施工面節（pre-commit 改動、ADR 清單、帳本）不收、留在該刀。

## §1 `tools/wire-schema.py` 行為契約

> 凍結存證＝`specs/002-system-settings/contracts/code-gates.md` §1.2；跨子庫純讀檔錨兩腿＝`specs/005-role-menu-crud/contracts/code-gates.md` §4。


- 子命令：`extract`（base-web 容器內 `npx -y typescript-json-schema@0.67.4 "src/typings/{common,api/*}.d.ts" "*" --ignoreErrors --required --strictNullChecks` → draft-07 快照、原子替換寫 `rust-api/server/tests/fixtures/wire-schema.json`；需 stack 在跑；輸出確定性）；`check [--staged-gate]`（依序：合成 self-test → 跨子庫純讀檔錨兩腿〔下條〕→ `--staged-gate` 收窄＝兩側 pin 區間皆零變動〔base-web 區間零 typings 變動＋rust-api 區間零快照變動〕才跳過重抽比對 → 容器探測 → 重抽至暫存、與工作樹快照 byte 比對、絕不覆寫）；`test`。
- 跨子庫純讀檔錨兩腿（005 刀 U11；該刀 spec FR-057、ADR-00044 決定 8）：
  - 位置＝合成 self-test 之後、收窄與容器探測之前**無條件**執行；只讀工作樹檔、不觸 docker／git——pin 區間有無變動、stack 有無在跑皆不能讓它跳過（self-test 釘：staged-gate 判跳過與容器不可用時兩腿照跑照紅）；收窄 pathspec 不擴（擴了即牽動 pre-commit submodule-sync 段）。
  - BL-00109 qs 前提腿：`base-web/packages/axios/src/options.ts` 去 TS 註解後 ①`stringify` 恰以 `import { stringify } from 'qs'` 匯入一次 ②`paramsSerializer` 恰一處生效碼、且為無選項 `params => stringify(params)`（表達式體或區塊體皆可）；③`base-web/packages/axios/package.json` 之 `dependencies.qs` 恰為工具常數 `QS_PINNED_VERSION`。理由：`rust-api/server/tests/wire_schema.rs` 之真串常數以此前提（qs 預設 `strictNullHandling: false` ⇒ null 渲染成 `k=`）於 base-web 容器實跑產出，前提一改（序列化器傳選項、拿掉序列化器回 axios 預設、換 qs 版）常數即不再是前端真送的串而照綠。補救＝同批以新前提實跑重取各真串常數、再改釘值。
  - 保留路由名對賬腿：`rust-api/server/src/model/facade/sys_menu.rs` 去 rust 註解後 `const RESERVED_ROUTE_NAMES: [&str; N] = [...];` 宣告恰一處，其成員集 MUST ＝ `base-web/src/router/elegant/routes.ts` 與 `base-web/src/router/routes/index.ts` 之 `customRoutes` 陣列字面兩處之 `meta.constant: true` 路由名集 ∪ `base-web/src/router/routes/builtin.ts` 之路由名集（路由物件＝直屬 `name: '<字串>'` 之物件字面、去 TS 註解後判；`customRoutes` 讀面限該陣列字面＝`createStaticRoutes` 實際組成，憲法 §I.2、ADR-00044 決定 8）；rust、`routes.ts` 常量路由、`builtin.ts` 任一側零成員＝解析面空、括號不成對＝解析失準，皆為違規；`customRoutes` 零常量路由屬正常，其陣列宣告須恰一處且括號成對（否則＝解析失準）。補救＝同批改該常數或還原前端路由定義。
  - 錨檔六支任一缺席或讀不了＝違規（fail-loud、不當跳過）；違規逐條走 stderr、`check` 即回 2。已知邊界（讀工作樹不讀 pin 樹；呼叫端覆寫序列化器不在讀面）＝RUNBOOK §12 該列。
- 唯讀鐵則：npx 一次性、不碰 base-web 工作樹／package.json／pnpm lock；前端 porcelain 前後皆空。
- rc：check 0＝一致或具名跳過（docker 缺／`base-web` 容器未起／staged-gate 兩側零變動；clarify Q5）；2＝錨兩腿任一違規、重抽失敗、快照缺席或不一致；extract 2＝stack 不在或 npx 非零（不寫部分結果）；64 用法錯。
- rev6 座標核對＝compose 兩檔名、`base-web` 服務名與 `-w /app`（皆同 rev5）；typings glob 零改（已涵蓋 `api/rev6-*.d.ts`）。
- pre-commit 觸發：staged 含 `base-web` 或 `rust-api`（gitlink）即 `check --staged-gate`。

## §2 wire 快照與覆蓋閘契約

> 凍結存證＝`specs/002-system-settings/contracts/wire-settings.md` §4；★「受審 definitions」與「002 刀 case 集」兩項為 002 當下的枚舉、隨刀前進（現況查 `rust-api/server/tests/fixtures/wire-schema.json` 與 `server/tests/contract.rs`）。


- 快照產製：`python3 tools/wire-schema.py extract`（base-web 容器內 `npx typescript-json-schema@0.67.4` 唯讀抽取、`--strictNullChecks`、原子替換寫入
  `rust-api/server/tests/fixtures/wire-schema.json`；需 stack 在跑）；drift 閘＝`check`（重抽 byte 比對；pre-commit `--staged-gate` 收窄：兩側 pin 區間皆零變動才跳過〔判準＝§1〕；
  ★docker 缺或 `base-web` 容器未起＝具名跳過 rc 0、容器在而重抽失敗或不一致＝rc 2——clarify Q5）。
- 受審 definitions（002 刀新增）：`Api.SystemManage.SystemSetting`（讀端序列化輸出必過；★description 不含 null）＋`Api.SystemManage.UpdateSystemSettingReq`
  （service 送出形錨定；description 呈 `["null","string"]`）。
- 覆蓋閘：`server/tests/contract.rs` case registry 與 `router::ROUTES` 之 case_key **雙向**比對——每條 route 必有 case（缺即紅指名）、每個 case 必對 route（殭屍即紅指名）。002 刀 case 集恰四：health／metrics／get-system-settings／update-system-setting。
- 負向自證（DoD）：抽掉 update-system-setting 案→紅指名→還原全綠；加一殭屍案→紅指名→還原。

## §3 `tools/view-render-guard.py`／`tools/route-artifact-gate.py` 行為契約

> 凍結存證＝`specs/004-ip-trust-anchor/contracts/code-gates.md` §2。


① `tools/view-render-guard.py`（承 `rev5:tools/view-render-guard.py` 282 行、新寫）：射程 `base-web/src/views/manage/**`；零 `v-html`／`innerHTML`／`outerHTML`／`insertAdjacentHTML`／`document.write`（含 `writeln`）用法（禁用字面集＝工具常數 `FORBIDDEN`，以該常數為準、本檔不另釘值）；環境缺席語意＝base-web 工作樹缺席即 fail-loud（ADR-00019 形）。另一腿＝IP 規則頁表頭 prop 形正面錨（005 刀 U13；BL-00117、該刀 spec FR-062）：錨檔＝工具常數 `ANCHOR_REL`（`base-web/src/views/manage/ip-rule/index.vue`），三條皆對錨檔原文判（註解內字面同計）——(a) 每個 `<TableHeaderOperation` 開標籤帶工具常數 `ANCHOR_ATTRS` 兩屬性且值逐字相符（新增鈕綁新增按鈕碼權限、批刪鈕恆關；本檔不另釘值）(b) 該標籤自閉合（標籤體任何子節點即 default 插槽內容、自閉合即結構上無從覆寫）(c) 檔內零 `#default`／`v-slot:default` 字面；錨檔內零個該開標籤＝不成立（正面錨無實例不算綠）；開標籤終點＝引號外第一個 `>`。理由：呼叫端改回覆寫 default 插槽即脫離兩 prop 控制（覆寫成空時元件改渲染自帶備援按鈕）、無權帳號看見寫入口，而型別檢查照綠、seed 下無「有頁面權限、無新增權限」之帳號可走查觸到。射程外：同名 prop 之其他繫結寫法（靜態屬性、`v-bind` 物件展開、camelCase 別名）與錨屬性並存時之覆蓋序、kebab-case 標籤名之第二個表頭；確需具名插槽時 (b) 須同批改判準。rc：兩腿違規合併列出＝1（指名檔:行）；錨檔缺席＝2。
② `tools/route-artifact-gate.py`（承 `rev5:tools/route-artifact-gate.py` 605 行、新寫）：於 base-web 容器內**沙盒**重跑路由外掛重算（不就地改工作樹＝pre-commit 各閘唯讀）後與版控產物四檔 byte 比對＝冪等，另以上游基線為種重算一腿承擔「手改一行即紅」（外掛對 `routes.ts` 為增量合併、版控為種時手改行存活；★勘誤 2026-09-20：原文「容器外以 `pnpm` 重跑…後 `git diff --quiet`」——`node_modules` 住容器、`pnpm gen-route` 為互動腳手架非重算指令〔`rev5:L-053`〕）；斷言「憲法 §III.2 該軌道列所列產物檔集＝外掛實際產出檔集」（雙向差集即紅）；環境缺席＝具名跳過 rc 0，判準三項（工具 `observe` 段；ADR-00019）：`docker` 不在 PATH／compose 兩檔任一缺／base-web 容器未起；容器在而憲法列或基線種子不完整＝rc 2，基線源倉缺席＝只第三腿具名跳過並警告。
★接線與名冊落點屬各刀施工面、不收進本檔（ADR-00041 決定 2）；現況真源＝RUNBOOK §12 碼面閘表與 `tools/docsync/tests/test_hook_wiring.py` 的 SEGMENTS。

## §4 `tools/fork-delta-lint.py` 行為契約

> 凍結存證＝`specs/002-system-settings/contracts/code-gates.md` §1.3；範圍欄對賬腿＝`specs/006-authz-governance/contracts/code-gates.md` §2.1。

- 掃描面：base-web `src/` 之 .ts／.vue＋`build/` 之 .ts＋根層 `.env*`；基線＝源倉 `fork260509-soybean-admin-base/` @ `example` tip（bootstrap 斷言在場）。
- 標記兩判定：修改型缺「原行:」；新增型缺圈界標記。★兩者之現況實數不在本檔釘值，以 `grep -rc '原行:' base-web/src base-web/build base-web/.env*` 與 `grep -rhoE '\[rev6-inline [A-Z][A-Z0-9-]*(\([a-z]+\))?\+ [0-9]{3}-[a-z-]+( START| END)?\]' base-web/src base-web/build | wc -l` 現算（後者含圈界 START／END 兩端與單行形；塊數與單行形之分計量法住活書 §8.4）（002 刀進場當時修改型為零＝該判定彼時 vacuous，003／004 兩刀落地後已非）。授權判定＝憲法 §III.2 ★軌道（軌道×用途×檔案）三元組硬邊界＋§III.1 三軌道範圍收窄（ADAPT 修改型限根層 `.env*`；WRAPPER 掃描面內不可修改型）；新增檔標記所稱軌道與檔路徑不符＝紅。
- 範圍欄對賬腿（憲法 §III.2 表外宣告 3；ADR-00063 決定四）：解析面＝§III.2 表每列範圍欄之（…）注記，注記轄其前一段反引號路徑（brace 展開與注記內 token 不入集沿名冊載入之同一支展開器、分群判準同 `tools/route-artifact-gate.py`）；數量段＝注記內第一個「；」或「：」之前，形為閉集——「N 處，修改型」／「各 N 處，修改型」／「N 處修改型＋M 塊新增型」／「N 塊，新增型」／「各 N 塊，新增型」，冠「預估」或「各預估」＝預估形；注記含「不預估」＝不預估形；「產物檔 N 支」＝產物檔形（`tools/route-artifact-gate.py` 之射程）。實數面＝同次讀 base-web 工作樹：修改型逐（軌道, 用途, 檔）計含 `原行:` 且標記軌道與用途相符之行，新增型逐檔計圈界塊首 START 行（不分軌道與用途）。判準＝修改型逐三元組相等、新增型逐檔跨列加總相等；預估、不預估與產物檔形不入對賬（跳過粒度＝修改型逐三元組、新增型逐檔——該檔任一項為預估或不預估即整檔跳過），不等＝rc 1 指名三元組或檔與各列分項；解析失準＝rc 2 指名列與注記原文（數量段未識別、注記無所轄路徑、多檔共用一數而未寫「各」、路徑未被注記所轄、零解析、非跳過之對賬項為零）。綠訊息附對賬項數與跳過項數（修改型、新增型分列；兩數皆以現算為準、本檔不釘值）。
- ★標記字面（新增型檔頭一行、契約定形）：`<註解引導> [rev6-inline <軌道名>+ <刀名>] <一句話理由>`——token `rev6-inline`（CLAUDE.md §1）、`+` 尾綴＝新增型。★**註解引導依檔型而異**：`.ts` 與 `.vue` 的 script 區為 `//`、`.vue` 的 template 區為 `<!-- … -->`（工具吃五種標記形、不限單一註解形）。★**軌道名不限於憲法 §III.1 表首欄**：工具側判準＝`TRACK` 正則之 `[A-Z][A-Z0-9-]*`，§III.2 ★ 軌道與表外宣告 3 之頁進場標記（如 `MANAGE-IP-RULE-VIEW`）同樣合法，授權由三元組另判。刀名＝該檔進場刀之 `NNN-slug`。現況軌道名集與刀名集以 `grep -rhoE '\[rev6-inline [A-Z][A-Z0-9-]*(\([a-z]+\))?\+ [0-9]{3}-[a-z-]+( START| END)?\]' base-web/src base-web/build | sort | uniq -c` 現算（用途後綴與圈界形同計）。
- ★結構斷言改形（brainstorm Q5）：名冊載入對 §III.2 ★段——零資料列時 MUST 命中哨兵句字面「（空表——尚無 ★ 軌道；首列隨首刀 Amendment 落入。）」、否則 ≥1 列；§III.1 恰 3 列與其餘斷言不變＋第⑥道（as-built 2026-09-05 U0 審查補）＝§III.1 三實名列範圍欄之反引號 token 集 ⇔ 工具常數 `S1_RANGE_LITERAL`（次序不計）、不符即 rc 2——Amendment 改範圍欄即紅、與 pre-commit 憲法觸發源連動；self-test 一正一反：合成憲法文本「零列＋哨兵句」＝綠、「零列＋無哨兵句」＝紅（守不消失）。日常一律用預設憲法路徑，`--constitution` 只供自身變異驗證。
- rc：0 綠／1 缺標記、缺原行、軌道外或範圍欄計數不等／2 結構斷言敗（名冊載入失敗、範圍欄注記解析失準）；源倉缺席或未切在 `example`＝rc 2 fail-loud（`assert_baseline` die；bootstrap 已斷言在場、正常不觸——as-built 校正 2026-09-05 U0：原句「具名跳過」與碼相反，rev5 原檔同為 die、fail-loud 方向較安全）。
- pre-commit 觸發：staged 含 `base-web`、`tools/fork-delta-lint.py` 或 `.specify/memory/constitution.md`。

## §5 `tools/msg-key-gate.py` 跨端閘契約

> 凍結存證＝`specs/003-auth-session/contracts/code-gates.md` §2。

| 面 | 契約 |
|---|---|
| 子命令 | `check`（預設）／`test`；`--rust <path>`／`--locales <dir>`（只供 self-test 注入、日常預設路徑） |
| 左源 | `rust-api/server/src/error.rs` 兩段解析（實碼形＝常數表＋常數引用陣列、零字面）：①`pub mod msg_key { pub const NAME: &str = "字面"; … }` 建 名稱→字面 映射 ②`pub const MSG_KEYS: [&str; N] = [ msg_key::NAME, … ];` 逐元素經映射解回字面（亦容直寫字面）；元素數≠N 或任一元素解不出（含常數表缺該名）＝rc 2 |
| 右源 | `base-web/src/locales/langs/{en-us,zh-cn,zh-tw}.ts` 各自 `backend: {` 區塊（錨＝獨佔一行、允許前置空白；brace 配對取塊；剝 `//`／`/* */` 註解與字串值後攤平鍵路徑以 `.` 串接） |
| 斷言 1 | 三檔各自 `set(backend) == set(MSG_KEYS)`；不等＝rc 1、逐檔指名「缺：…」「多：…」 |
| 斷言 2 | Biz 構造點守衛：`rust-api/server/src/**/*.rs` 生產區間（`#[cfg(test)]` 區塊以 brace 配對排除）內每處 `AppError::Biz(` MUST 緊接 `Cow::Borrowed(` 且引數為 ①字串字面 或 ②`msg_key::NAME` 常數（經左源映射解回字面）、解出之鍵 ∈ `MSG_KEYS`；動態構造（變數／`format!`／函式回傳）＝rc 1 指名檔:行。002 既有兩處（`validation.rs`）為常數形＝合法、零改動；002 刀三個新 Biz 鍵亦用常數形 |
| rc | 0 綠／1 違規／2 結構異常（檔缺席、`MSG_KEYS` 解析失敗、backend 節缺席或 brace 不配對、比對面為空）／64 用法錯 |
| self-test | 合成樣本七案：三檔全等綠／某檔缺一鍵紅／某檔多一鍵紅／某檔缺 backend 節 rc 2／常數間接形解析成功／常數表缺該名 rc 2／動態 Biz 構造紅；真 repo 綠案（現行 `error.rs` 常數形） |
| 依賴 | Python 3 標準庫、零 docker |

**接線落點**：屬施工面、不收進本檔（ADR-00041 決定 2）；現況真源＝RUNBOOK §12 碼面閘表與 `tools/docsync/tests/test_hook_wiring.py` 的 SEGMENTS（凍結存證那份列有 003 刀當時的五處清單）。

## §6 docsync routes 生成器契約

> 凍結存證＝`specs/002-system-settings/contracts/code-gates.md` §4。

- 來源＝`rust-api/server/src/router.rs` 之 `ROUTES` const；解析窄假設＝data-model §4 機器契約（精確開頭、每欄一行、枚舉字面）；來源檔缺席或任一偏離＝raise（fail-loud、generate 非零、GT-01 連帶紅）——U1 落地後 router.rs 永不缺席、不設 Day-1 豁免。
- 輸出＝`docs/generated/reference/routes.md`：生成標記檔頭＋「來源＝… ROUTES const（generate 重算；handler 閉包不入表）」＋表 `| path | method | protection | case_key | envelope 例外 |`（列序＝ROUTES 宣告序）。
- 名冊：GENERATED_FILES 14→15；README `docs/generated/` 成員行加 `routes`（GT-09 成員對賬腿守）；`tests/test_references.py` 一正一反（合成四條 ROUTES 文本→表；缺精確開頭／未知枚舉→raise）。

## §7 `tools/seed-view-gate.py` 行為契約

> 凍結存證＝`specs/006-authz-governance/contracts/code-gates.md` §2.2；決定本體＝ADR-00071。

- 子命令：`check`（預設）／`test`；多餘引數或未知子命令＝rc 64。`check` 不連帶跑自測（ADR-00071 決定 6②）。依賴＝Python 3 標準庫；零 docker、零網路、不呼叫 git。
- 判準＝單向包含 seed 集 ⊆ views 集，另加結構自證一腿；兩腿互不遮蔽、紅項合併列出：
  - seed 集＝`rust-api/migration/src/m0002_baseline_seeds.rs` 中行首 `const SEED_SYS_MENU: &str = r#"` 之後、至其後第一個 `"#` 為止之 raw 字串區間內全部 `view.<鍵>` 字面去重（帶佈局之 `layout.base$view.<鍵>` 形亦收）；區間外（他 seed 常數、doc 註解、收尾符同一行之後）不收。每鍵記 seed 檔行號與該行 sys_menu 列 id。
  - views 集＝`base-web/src/views/**` 依 elegant-router 0.3.8 預設頁檔規則導出：頁檔＝`index.vue` 或 `[<識別字>].vue`；名為 `components` 之目錄整棵排除；頁檔至少一層上層目錄、各層目錄名合外掛之 ASCII 合法式；鍵＝各層目錄名去掉 `_` 起首之分組層後以 `_` 串接並轉小寫。前提＝`base-web/build/plugins/router.ts` 未覆寫頁檔規則（覆寫或外掛升版＝ADR-00071 翻案觸發器）。
  - 結構自證：views 導出集 MUST 恰等 `base-web/src/router/elegant/imports.ts` 之 views 匯出塊鍵集（layouts 塊不收）；雙向差集分向指名——導出規則與外掛脫節、或頁目錄已動而產物未重算，皆在此現形。
  - 方向單向：base-web 有而 seed 無（例 `login`、未上選單之頁）屬合法不對稱、不紅。射程限 seed 檔：`m0003` 起之 delta migration 所寫選單列與超管自建選單不在射程（後者之已知態＝ADR-00068 款 14）。
- 具名豁免與到期語意：豁免表＝工具模組常數 `EXEMPT`（唯讀檢視；不得取自 args／env／讀檔），恰兩列＝`view.manage_system-settings`（seed 列 9）、`view.manage_audit`（seed 列 77），各附 BL-00045 指針與解除謂詞（該鍵之 view 出現於導出集＝到期）。豁免中之鍵缺 view 不紅、綠時逐列印出；**到期即紅**（頁已在而豁免未摘）、**幽靈亦紅**（豁免鍵已不在 seed 集）——表只會縮。「恰兩列且各含 BL-00045 與解除謂詞」與另三釘（呼叫點原封傳入、判定函式零外部取值形、呼叫端零就地改表）由自測機器守；增減列＝同批改自測斷言、於 diff 現形（拍板級）。豁免為本閘自持之到期語意、不入 docsync `DAY1_EXEMPTIONS`。
- rc：0 綠／1 紅（缺 view 逐鍵指名 seed 檔:行與 sys_menu 列 id；豁免到期或幽靈；導出集≠`imports.ts`）／2 結構異常（seed 檔、`SEED_SYS_MENU` 塊〔含未收尾〕、views 目錄、`imports.ts` 或其 views 匯出塊任一缺席，或任一側掃得空集＝掃描面空集合即紅、RL-0051）／64 用法錯。tracked 面缺席一律 rc 2 fail-loud、不設具名跳過（ADR-00019 決定 4）。
- 讀面型（ADR-00055 決定 3；進場同刀標型之首例）：base-web `src/views/**` 與 `src/router/elegant/imports.ts`＝(a) 閘面內、延後至下次 base-web pin bump 補抓；`rust-api/migration/src/m0002_baseline_seeds.rs`＝(b) 閘面外、無兜底——該檔程式內容依憲法 §I.5 例外② 鎖定（ADR-00009）、任何改動本身即須另立 ADR，故不擴閘面。
- self-test（`test`）：暫存目錄合成 fixtures、一律實跑生產函式——缺 view 紅、豁免生效綠、豁免到期紅、幽靈豁免紅、導出≠`imports.ts` 兩向各自紅、讀面缺席與各側空集 rc 2、豁免表恆定四釘；案數以 `test` 輸出為準、本檔不釘值。
- 實作＝python 行級掃描（seed 側 raw 字串塊＋正則、base-web 側檔樹走訪＋views 匯出塊行級正則）：不持 rust 側字元級源碼解析組、非 BL-00108 所稱第三份。

★接線與名冊落點屬各刀施工面、不收進本檔（ADR-00041 決定 2）；現況真源＝RUNBOOK §12 碼面閘表與 `tools/docsync/tests/test_hook_wiring.py` 的 SEGMENTS。
