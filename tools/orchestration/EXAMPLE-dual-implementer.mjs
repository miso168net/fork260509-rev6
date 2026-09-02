export const meta = {
  name: 'u4-purge-endpoint-008',
  description: '008 U4（T014~T017）：purge 端點——守門固定序＋詞彙第九值＋msg 三語＋router 65→66＋purge definition 裁判',
  phases: [
    { title: 'Impl1', detail: 'implementer-1：purge handler＋AuditOperation 第九值連動＋error.rs 射程句（T014）' },
    { title: 'Impl2', detail: 'implementer-2：msg 三語＋router#5＋contract#5＋purge 裁判（T015~T017）' },
    { title: 'SpecReview', detail: '規格對照審查＋fix 迴圈' },
    { title: 'CodeQualityReview', detail: '碼品質審查＋fix 迴圈' },
  ],
}

const UNIT = 'U4'
const PH1 = 'Impl1'
const PH2 = 'Impl2'
const LBL1 = 'u4:implementer-1-purge'
const LBL2 = 'u4:implementer-2-wire'
const START_LOG = 'U4 起手（T014~T017）：implementer-1 落 purge 守門固定序＋詞彙第九值'

if (typeof args !== 'undefined' && args !== null) {
  throw new Error('防呆①：本 script 不接受 args——一切邊界寫死於 script 常數')
}

const MAX_FIX_ROUNDS = 3
const CYCLES = 2
const IMPLEMENTERS = 2
const WORST = IMPLEMENTERS + CYCLES * (2 * MAX_FIX_ROUNDS + 1)
const AGENT_FUSE = Math.min(20, WORST + 1)
if (AGENT_FUSE < WORST) {
  throw new Error('防呆③：保險絲 ' + AGENT_FUSE + ' 低於結構最壞值 ' + WORST)
}
let spawned = 0

const IMPL_OPTS = { model: 'fable[1m]', effort: 'xhigh' }
const REVIEW_OPTS = { model: 'opus[1m]', effort: 'xhigh' }
const FIX_OPTS = { model: 'opus[1m]', effort: 'xhigh' }

function guard(p, label) {
  if (typeof p !== 'string') throw new Error('防呆②：prompt 非字串（label=' + label + '）')
  if (p.length < 400) throw new Error('防呆②：prompt 過短 ' + p.length + '（label=' + label + '）')
  if (p.startsWith('undefined') || p.startsWith('null')) throw new Error('防呆②：prompt 開頭為 undefined／null（label=' + label + '）')
  if (!p.includes('zh-TW')) throw new Error('防呆②：prompt 缺 zh-TW 字面（label=' + label + '）')
  return p
}

async function spawn(prompt, opts) {
  spawned += 1
  if (spawned > AGENT_FUSE) throw new Error('防呆③：agent 保險絲觸發——已派 ' + spawned + ' 支、上限 ' + AGENT_FUSE)
  return await agent(guard(prompt, opts.label), opts)
}

const WORK_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['status', 'report', 'filesChanged'],
  properties: {
    status: { type: 'string', enum: ['ok', 'blocked', 'done_with_escalation'] },
    report: { type: 'string', description: 'zh-TW 交付報告：做了什麼、關鍵設計決定與依據、自驗命令與其實際輸出摘要（測試通過數逐項）' },
    filesChanged: { type: 'array', items: { type: 'string' } },
    escalations: { type: 'array', items: { type: 'string' } },
    rejectedFindings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['file', 'summary', 'why'],
        properties: { file: { type: 'string' }, summary: { type: 'string' }, why: { type: 'string' } },
      },
    },
  },
}

const REVIEW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['agentStatus', 'blockers'],
  properties: {
    agentStatus: { type: 'string', enum: ['ok', 'failed'], description: '★只表審查 agent 自身能否完成審查；審查有 blocker 仍是 ok' },
    blockers: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['file', 'summary', 'detail'],
        properties: {
          file: { type: 'string' },
          summary: { type: 'string', description: '一句話缺陷陳述（結構化比較鍵、跨輪次勿改寫措辭）' },
          detail: { type: 'string', description: 'zh-TW 證據與修法建議' },
        },
      },
    },
    notes: { type: 'string' },
  },
}


const ALLOWED_BLOCK = [
  '★允許檔案清單（本單元唯一可寫面）：',
  '  【rust-api】',
  '  1. `server/src/handler/audit.rs`——**加** purge handler＋其 stub-DB 守門測（既有四讀端與 `mod tests`／`mod endpoint_tests` 不動）',
  '  2. `server/src/model/audit.rs`——★**只准**做 rev5:ADR 0079 決定 2 的三處連動＋「八」假述面現算改對（詳交付段）；其餘一字不動',
  '  3. `server/src/error.rs`——★**只准**改 BizData 射程句**兩處**（:42 與 :60 之「射程嚴限密碼二鍵」）；其餘一字不動',
  '  4. `server/src/router.rs`——第 5 條 RouteDef＋`ROUTES_COUNT` 65→66＋逐刀 bump 帳註＋casbin 對賬測補 purge 條',
  '  5. `server/src/handler/role.rs`——★**只准**改**兩處**手寫釘：`POLICY_ENDPOINT_COUNT` 49→50、同測②之 `got.last()` 逐字釘；其餘一字不動',
  '  6. `server/tests/contract.rs`——第 5 case 登記＋其 verify fn',
  '  7. `server/tests/wire_schema.rs`——purge **三支** definition 裁判（`PurgeAuditTable`／`PurgeAuditLogReq`／`PurgeAuditLogRes`）＋節註射程更新',
  '  【base-web】★皆屬**既有** I18N-WIRING (ii)(iii) 射程（非新用途、零修憲需求）',
  '  8. `src/locales/langs/zh-tw.ts`——★**只准**於 `biz:` 節內依字母序（`auth` 前）插 `audit` 二鍵',
  '  9. `src/locales/langs/zh-cn.ts`——★**只准**於 backend 樹插同二鍵',
  '  10. `src/locales/langs/en-us.ts`——★**只准**於 backend 樹插同二鍵',
  '  11. `src/typings/app.d.ts`——★**只准**於 `App.I18n.Schema.backend` 型節補 `audit` 二鍵（新增型圈界標記）',
  '★★**限定式項的分值語意（rev5:L-075）**：上列凡帶「只准…／其餘一字不動」限定語者，**不是**檔案級授權而是**改動面級**授權——該檔之限定外改動＝**視同清單外改動**，MUST 依 status 分值升級（`done_with_escalation`＋escalations 逐條列明），★**不得**因為「檔在清單內」就回 `status: ok`。',
  '★清單外明確不得動：',
  '  - `server/src/model/audit_query.rs`／`model/facade/**`／`envelope.rs`＝前置單元已交付（發現缺陷＝升級主線、不擅改）',
  '  - `server/tests/fixtures/wire-schema.json`＝機器抽取產物、**絕不手改**；本單元**不動 typings 的型**（purge 三支 U1 已抽妥在快照內）⇒ **不需重抽**',
  '  - `base-web/src/typings/api/**`／`src/views/**`／`src/locales` 的 `route:`／`page:` 兩樹＝WIRING (vii)(viii) 面歸 U6／U7',
  '  - `docs/**`、`.specify/**`、`tools/**`、`specs/**`（tasks.md 勾選＝主線收尾做）',
  '  - `rust-api/migration/**`＝本刀零 migration 零 seed 變更（spec FR-A01）',
].join('\n')


const RULES = [
  '★不可違反項（全數烤入、違反即單元失敗）：',
  '1. 一切書面產物（report／blocker／**程式碼註解**／文件）**一律 zh-TW**（繁體中文；識別字、程式碼、路徑保留原形）。',
  '2. **絕不 push／merge／git commit**——只改工作樹，git 操作由主線負責。',
  '3. **絕不寫入 `../fork260509-rev5/`**（含子庫與源倉）——rev5 是唯讀對照基準、硬禁令唯讀；讀取允許且**必要**。',
  '4. rust build／test **一律容器內、全程 serial**。正確命令形（quickstart 的簡寫形缺 `-f` 會報 invalid compose project）：',
  '   `docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1`',
  '5. rust 碼完工前 MUST 於容器內跑 `docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo fmt --all`（rev5:ADR 0057）。',
  '6. 空間邊界：只准動允許清單內的檔；清單外需要動＝**絕不擅改**，依 status 分值升級。',
  '7. status 分值語意（★兩值反應相反）：`blocked`＝整件做不下去、主線須立刻接手；`done_with_escalation`＝交付已完成、只是有清單外待辦（附 escalations）。',
  '8. 凡改變某數字／集合／方向／名稱／單一權威，MUST `grep -rn` 枚舉全 repo 同語意命中、逐處回報。★**枚舉後逐處判別、不得用 `grep -v` 過濾整行**——同一行可能同時含該改與不該改的 token（rev5:L-076 實暴）。史述保留、現在式改對（rev5:L-032）。',
  '9. 提及前代（rev5／rev4／rev3）編號一律帶 `rev5:` 之類前綴（GT-05；承 rev5:Lint25、rev5:ADR 0012）。',
  '10. ★**實作先讀 rev5 對應碼**（唯讀）、高度參照但**重打字消化不拷貝**；註解**一律重寫**（rev5 出處帶 `rev5:` 前綴）；rev6 拍板差異點**不得帶回**（承 rev5:ADR 0019）。',
  '11. ★**TDD：先紅後綠**。每個可測面先寫會紅的測、跑到真的紅、再寫實作到綠。★分階段推進：每完成一階段就在容器內 serial 跑一次測試確認綠，再進下一階段——不要全部寫完才第一次編譯。',
].join('\n')


const CONTEXT = [
  '=== 專案與本單元定位 ===',
  '工作區＝rev6-admin 傘狀 workspace（`/mnt/d/AnewSpaces/x_Project/fork260509-rev6`），操作手冊＝根目錄 `CLAUDE.md`（★先完整讀，尤其 §6 硬禁令）。後端＝`rust-api/`、前端＝`base-web/`（皆 git worktree 子庫）。',
  '本刀＝`008-audit-settings-pages`。本執行單元＝**U4**，涵蓋 tasks.md 的 **T014～T017**＝audit 第五支端點（purge，破壞性寫端）全鏈。',
  '★**已完成的前置**：U0 修憲（憲法 1.10.0、島 J 入憲、**rev5:ADR 0079 已 accepted**＝T014 的開工前提）／U1 契約錨（`Api.Audit` 十一支型、快照 101 definitions，purge 三支已在內）／U2 讀面全鏈（ROUTES 65）／U3 讀面兩層裁判（全量 1080）。',
  '',
  '=== 必讀 ===',
  '1. `CLAUDE.md`（根目錄）',
  '2. `specs/008-audit-settings-pages/spec.md`（★FR-C01～FR-C04、FR-A01／A03／A07、FR-H01）',
  '3. `specs/008-audit-settings-pages/data-model.md` **§3 清理模型**（守門固定序逐字＋自記 payload 三欄）',
  '4. `specs/008-audit-settings-pages/contracts/wire-audit.md`（§1 端點表第 5 列、§3 錯誤碼表）與 ★`contracts/msg-keys.md`（**譯文權威**：兩鍵三語逐字）',
  '5. ★`docs/arc42/decisions/0079-audit-operation-vocabulary-adds-ninth-value-purge.md`（**本單元的詞彙拍板**：決定 2 逐條列了三處連動的做法）與 `docs/arc42/decisions/0078-bizdata-scope-adds-purge-below-floor.md`（BizData 射程擴一鍵、error.rs doc 改對歸本單元）',
  '6. `rust-api/server/src/handler/audit.rs`（U2／U3 交付＝你要續建的檔）',
  '7. ★**rev4 藍本（唯讀）**：`../fork260509-rev4/rust-api/server/src/handler/audit.rs` 之 purge 段（`PurgeAuditLogReq`／`de_before_days`／`PurgeAuditTable` 的 `from_wire`／`wire`／`entity_table`／`purge_before`／mod tests 測 11~14）。**絕不寫入該樹**。',
  '',
  '=== 事實接地（★每條附出處；本段與碼衝突時**以碼為準**並在 report 指出哪一條錯）===',
  '',
  '**A. 詞彙第九值（rev5:ADR 0079 決定 2、開工前提已滿足）**——`rust-api/server/src/model/audit.rs`：',
  '  · `audit_operation_vocabulary!` 呼叫點現恰八 variant、末位 `ChangePassword => "change_password"`（:112-138 區間）⇒ **末位加** `Purge => "purge"`（★**小寫**；`WHY_UPPERCASE` 逐字「rev4 大寫 DB 動詞形不得帶回」，:312 附近）。',
  '  · `EXPECTED_LITERALS: [&str; 8]`（:228 附近）⇒ 增為 `[&str; 9]`、新字面 `"purge"` **插末位**（與 `ALL` **恰等含序**比對，插錯位即紅）。',
  '  · 測 `t013_user_password_family_adds_three_vocabulary_stays_eight`（:341）之 `ALL.len()` 期望 8→9，★**測名與斷言訊息連同改寫**（新定案出處＝rev5:ADR 0079）。',
  '  · ★**同檔「八」假述面現算改對**：主線實測 `grep -n "八" rust-api/server/src/model/audit.rs` 得 **11 行**，其中 **10 行屬詞彙集假述**（:40／:106／:199／:267／:292／:316／:320／:345／:377／:381）須改對；**:167 是 `ip_confidence` 來源信心八態＝他軸、不動**（rev5:ADR 0079 已明文排除）。改完以同指令復掃、逐行判別驗收。',
  '',
  '**B. 連動釘值（主線已用兩路並行法盤點；★漏改任一個，自驗會紅在看似無關的檔上）**：',
  '  · `server/src/router.rs:786` `ROUTES_COUNT` **65→66**',
  '  · `server/src/handler/role.rs:1449` `POLICY_ENDPOINT_COUNT` **49→50**',
  '  · `server/src/handler/role.rs:1472` 同測②之 `got.last()` 逐字釘：現為 `/systemManage/getSessionEvent` ⇒ 改為 **`/systemManage/purgeAuditLog`**（purge 註冊於 ROUTES 表尾）',
  '  · **名冊釘＝無連動**（主線已查證）：`envelope.rs` 的 `B043_SCAN_FILES` 已含 `handler/audit.rs`（U2 補）、本單元不新增檔；`tests/common/mod.rs` 的 `collect_rs_files` 是遞迴掃描器非手抄名冊。',
  '',
  '**C. BizData 射程句（rev5:ADR 0078 承載、本單元改對）**——`server/src/error.rs` **兩處**：`:42` 與 `:60` 之「射程嚴限密碼二鍵」。改為三鍵形並指向 rev5:ADR 0078（★逐字內容自行讀 rev5:ADR 0078 決定一之射程表後撰寫）。',
  '',
  '**D. rev5:Lint24 孤兒鍵約束**：rev5:Lint24 掃描面＝`rust-api/server/src` 全樹＋`error.rs`（`tools/docs-sync.py:4243-4244`）⇒ T014 一落 `biz.audit.*` 兩構造點，**msg 鍵三檔（T015）必須同批落地**，否則 `docs-sync.py lint` 孤兒鍵紅。兩者在**同一單元內**、無跨 commit 風險。',
  '  · ★rev5:ADR 0078 決定四已誠實揭露「裸奔時窗」：第三攜參鍵之**佔位符**守門（rev5:Lint24 第三腿）於 **T021／U5** 才建——本刀內的既定次序、非缺陷，**不要**在本單元順手做 rev5:Lint24 擴腿。',
  '',
  '**E. HTTP status（★U3 曾因主線摘要寫錯而被 implementer 接住，此處給出處）**：`server/src/error.rs:137` 凍結 13 碼矩陣逐字「HTTP status——例外恰二：4040→404、**5003→403**；其餘…」⇒ 業務碼 `2222` 走 **HTTP 200＋統一信封**。',
  '',
  '**F. 基線**：容器內全量 serial 現況＝**1080 passed／0 failed／2 ignored**（U3 後）。',
  '',
  '=== rev5 拍板差異點（★不得帶回 rev4 形）===',
  '· 詞彙值 **`purge` 小寫**（rev4 為大寫 `PURGE`）——條文與碼皆然。',
  '· 拒因走 `AppError::BizData` 攜 `{"minDays": 30}`（rev5:ADR 0078 授權的第三攜參鍵）。',
  '· `Api.Audit` 獨立命名空間（rev4 併入 `Api.SystemManage` 之形不帶回）。',
].join('\n')


const IMPL1_PROMPT = [
  '你是 008-audit-settings-pages 之 **U4 執行單元**的 **implementer-1（purge 本體）**。本單元分兩支 serial implementer，你做前半：**T014**。',
  '',
  CONTEXT,
  '',
  '=== 你的交付（T014）===',
  '',
  '【一】`model/audit.rs` 詞彙第九值三處連動＋假述面改對（★開工第一件事；rev5:ADR 0079 決定 2）',
  '見事實接地 A 逐條。★做完先在容器內跑一次測試——`t013_…` 與字面契約釘會立刻告訴你有沒有插對位。',
  '',
  '【二】`handler/audit.rs` 補 purge 端點（既有四讀端與兩個測試 mod 不動）',
  '· **守門固定序**（data-model §3 逐字、次序不可反）：',
  '   ①`table` 四值白名單（`operationLog`／`accessLog`／`loginAttempt`／`sessionEvent`）→ 違反＝`2222` ＋ msg key `biz.audit.invalidTable`（純 key、零 payload）',
  '   ②`beforeDays` ≥ `PURGE_MIN_DAYS`（**＝30**、後端權威常數）→ 違反＝`2222` ＋ `biz.audit.purgeBelowFloor` ＋ **`AppError::BizData(json!({"minDays": 30}))`**（★頂層鍵逐字 `minDays`——它是 rev5:Lint24 第三腿日後的對賬面）',
  '   ③**單一交易**：水平線 `DELETE`（早於 `now() − beforeDays`）＋**同交易**操作日誌自記（`operation` ＝第九值、payload_after ＝ `{table, before_days, deleted_count}` 三欄）；★op-log 版的 DELETE MUST 帶 **`operation <> \x27purge\x27` 豁免**（歷史清理自記列永久保留）',
  '· **`PurgeAuditLogReq` 寬鬆反序列化**：`beforeDays` 畸形／空／型別不符 → 視同缺席 → 被下限擋下，**恆不裸 400**（照 rev4 的 `de_before_days` 形重打字）。',
  '· **回傳**：`PurgeAuditLogRes { deletedCount }`；成功碼 `0000`。',
  '· **stub-DB 守門測**（先紅後綠、照 rev4 測 11~14 形）：白名單違反／下限違反皆須**零 DB 副作用**（守門在觸 DB 前就擋下）、固定序可辨（先驗 table 再驗天數）、`{minDays}` 明細確實在 data 內。',
  '· ★**本單元不做** fault-injection 原子性測（歸 T019／U5）——但你的實作必須讓那支測寫得出來：自記失敗 MUST 使整筆回滾（零刪除、零自記、回錯誤），不要用 `.ok()` 吞掉自記錯誤。',
  '',
  '【三】`error.rs` BizData 射程句兩處改對（見事實接地 C；逐字內容依 rev5:ADR 0078 決定一之射程表）',
  '',
  '=== 完工前自驗（逐項實跑、實際輸出寫進 report）===',
  '1. 容器內 `cargo fmt --all`',
  '2. 容器內全量 serial `cargo test --workspace -- --test-threads=1` → **0 failed**',
  '   ★**預期會紅一項**：`docs-sync.py lint` 的 rev5:Lint24 孤兒鍵（`biz.audit.*` 構造點已在、msg 鍵三檔尚未落）——那是 implementer-2 的 T015，**屬本單元內的既定次序、不是你的缺陷**；請在 report 註明「rev5:Lint24 孤兒鍵待 T015 補齊」，**不要**自己去改 base-web（那在你的清單外）。',
  '3. `grep -n "八" rust-api/server/src/model/audit.rs` 復掃：逐行判別、確認詞彙集假述面已清（`ip_confidence` 那行仍在＝正確）。',
  '',
  RULES,
  '',
  ALLOWED_BLOCK,
  '',
  '=== 回傳 ===',
  '以 StructuredOutput 回 `{status, report, filesChanged, escalations?, rejectedFindings?}`。',
  '★`report` 會**原文轉交 implementer-2**——請寫清：purge handler fn 名與簽章、`PURGE_MIN_DAYS` 常數位置、兩個 msg key 的**構造點檔:行**（T015 要對賬）、`PurgeAuditTable` 的 rust 側四值字面（T017 的裁判要接它）。',
].join('\n')

function impl2Prompt(impl1Report) {
  return [
    '你是 008-audit-settings-pages 之 **U4 執行單元**的 **implementer-2（接線與裁判）**。前一支已完成 T014（purge 本體＋詞彙第九值），你做 **T015～T017**。',
    '',
    CONTEXT,
    '',
    '=== ★implementer-1 的交付報告 ===',
    impl1Report,
    '★以上為自陳，**不要照單全收**；實際簽章與構造點位置以你自己讀碼為準，不符就在 report 指出。',
    '',
    '=== 你的交付 ===',
    '',
    '【T015】msg 鍵三檔＋型節（★與 T014 的構造點**同批**，否則 rev5:Lint24 孤兒鍵紅）',
    '· 譯文**逐字**＝`specs/008-audit-settings-pages/contracts/msg-keys.md` 的表（兩鍵 × 三語）。',
    '· `zh-tw.ts`：於 `biz:` 節內**依字母序**插 `audit`（在 `auth` **前**）。`zh-cn.ts`／`en-us.ts`：backend 樹同鍵。',
    '· `app.d.ts`：`App.I18n.Schema.backend` 型節補 `audit` 二鍵，帶**新增型圈界標記**（I18N-WIRING (iii) 射程；形照該檔既有 backend 型節的標記）。',
    '· ★三語鍵集 MUST 相等；`purgeBelowFloor` 的譯文**必含 `{minDays}` 佔位符**（三語皆是）——它是 rev5:Lint24 第三腿（T021／U5）日後的對賬面。',
    '',
    '【T016】`router.rs` 第 5 條＋計數＋`role.rs` 兩處釘＋`contract.rs` 第 5 case',
    '· RouteDef：path `/systemManage/purgeAuditLog`（逐字＝001 凍結 seed）、`HttpMethod::Post`、`Protection::Policy`、`envelope_exception: false`、`case_key: "purge-audit-log"`。註冊於 ROUTES **表尾**。',
    '· `ROUTES_COUNT` **65→66**＋逐刀 bump 帳註；casbin 對賬測補 purge 條。',
    '· ★`handler/role.rs` **兩處**手寫釘（事實接地 B）：`POLICY_ENDPOINT_COUNT` 49→**50**、`got.last()` 逐字釘改為 `/systemManage/purgeAuditLog`。',
    '· `contract.rs` 第 5 case＋verify fn（照既有 `verify_get_system_settings` 形；★POST 端點的未認證形同樣是 `8888`＋HTTP 200）。',
    '',
    '【T017】`wire_schema.rs` purge 三支 definition 裁判',
    '· `PurgeAuditTable`（★**枚舉集斷言接後端白名單常數**——contracts §4 逐字要求；不要手抄四值字面，要從 rust 側常數導出或至少與之對賬）／`PurgeAuditLogReq`／`PurgeAuditLogRes`。',
    '· 每支正反例成對、逐格指名（形照 U3 剛落的 008 讀面節）。反例至少含：`table` 值域外判否／`beforeDays` 給字串判否／`deletedCount` 缺席判否。',
    '· ★同批更新 U3 那節的**射程邊界註**（原寫「purge 三支歸 T017／U4 不裁」——現已裁，該句成假述、須改對）。',
    '',
    '=== 完工前自驗（逐項實跑、實際輸出寫進 report）===',
    '1. 容器內 `cargo fmt --all`',
    '2. 容器內全量 serial `cargo test --workspace -- --test-threads=1` → **0 failed**',
    '3. ★`python3 tools/docs-sync.py lint` → **零錯誤**（★T015 落地後 rev5:Lint24 孤兒鍵應已消——這是本單元 msg 鍵與構造點同批的驗收點）',
    '4. `python3 tools/fork-delta-lint.py` → 綠（base-web 四檔的圈界標記合規）',
    '5. base-web 容器內 `pnpm typecheck` → 綠',
    '6. ★`python3 tools/wire-schema.py check` → 綠（★本單元**不動 typings 的型** ⇒ 快照不該變；若它報不一致，代表有人動了型，停手回報）',
    '',
    RULES,
    '',
    ALLOWED_BLOCK,
    '',
    '=== 回傳 ===',
    '以 StructuredOutput 回 `{status, report, filesChanged, escalations?, rejectedFindings?}`。`report` 用 zh-TW 寫清設計決定與六項自驗的**實際輸出**。',
  ].join('\n')
}

const SPEC_REVIEW_PROMPT = [
  '你是 008-audit-settings-pages 之 **U4 執行單元**的**規格對照審查員**。',
  '',
  CONTEXT,
  '',
  '=== 審查面（逐條驗；★自行讀碼／跑唯讀命令取證，不採信回報）===',
  '1. **FR-C01／C02 守門固定序**：是否①白名單→②下限→③交易，**次序不可反**？值域外與低於 30 是否皆 `2222`＋正確 msg key？`{minDays}` 頂層鍵是否逐字 `minDays`？★守門違反時是否**零 DB 副作用**（在觸 DB 前擋下）？',
  '2. **FR-C03 單交易＋自記＋豁免**：DELETE 與自記是否在**同一交易**？自記 payload 是否含 `{table, before_days, deleted_count}` 三欄？op-log 版 DELETE 是否帶 `operation <> \x27purge\x27` 豁免（★**小寫**）？',
  '3. **FR-C02 寬鬆反序列化**：`beforeDays` 畸形／空／型別不符是否視同缺席→被下限擋，**恆不裸 400**？',
  '4. **★rev5:ADR 0079 三處連動**：macro 末位加 `Purge => "purge"`？`EXPECTED_LITERALS` 增為 9 且新字面**插末位**（恰等含序）？`t013_…` 的期望值＋**測名＋訊息**皆改寫且出處指向 rev5:ADR 0079？',
  '5. **★「八」假述面**：`grep -n "八" rust-api/server/src/model/audit.rs` 逐行判別——詞彙集假述是否已清？`ip_confidence` 那行（來源信心八態＝他軸）是否**未被誤改**？',
  '6. **連動釘值**：`ROUTES_COUNT` 66？`POLICY_ENDPOINT_COUNT` 50？`got.last()` 改為 `purgeAuditLog`？★實跑那支測確認。',
  '7. **T015 三語對賬**：譯文是否**逐字**＝`contracts/msg-keys.md`？三語鍵集是否相等？`purgeBelowFloor` 三語是否**皆含 `{minDays}`**？app.d.ts 型節是否帶新增型圈界標記？',
  '8. **rev5:Lint24 零孤兒**：★實跑 `python3 tools/docs-sync.py lint` 確認**零錯誤**（構造點與 msg 鍵同批＝本單元的驗收點）。',
  '9. **T017 裁判**：三支是否皆有正反例？★`PurgeAuditTable` 的枚舉集是否**接後端白名單常數**（contracts §4 逐字要求）而非手抄字面？U3 那節的射程邊界註是否已改對（原說「歸 T017 不裁」現已成假述）？',
  '10. **contract 覆蓋**：第 5 case 是否登記？兩支覆蓋閘是否皆綠？',
  '11. **射程越界**：是否動了允許清單外的檔？★特別查 `error.rs` 是否**只**改了那兩處射程句、`role.rs` 是否**只**改了兩處釘、四個 base-web 檔是否**只**加了指定的鍵（逐檔 `git diff` 看實際改動面，**不看 escalations 欄下結論**）。',
  '12. **快照未動**：`wire-schema.py check` 是否綠（本單元不動 typings 的型）？',
  '',
  '=== 不可違反項 ===',
  '★你是**審查員：只讀不寫**——絕不修改 repo 內任何檔案；findings 只放回傳訊息。可跑唯讀命令取證，**不得**跑會寫 repo 檔的命令（`cargo fmt` 不帶 `--check` 會寫檔）。',
  '★一切書面產物一律 **zh-TW**。★絕不 push／merge／commit。★絕不寫入 `../fork260509-rev5/`。',
  '★blocker 的 `summary` 是結構化比較鍵。★只報真缺陷；風格偏好放 `notes`。',
  '★**勿誤報**：rev5:Lint24 **第三腿**（佔位符對賬）歸 T021／U5，本單元不做＝既定次序（rev5:ADR 0078 決定四已揭露該裸奔時窗）；fault-injection 原子性測歸 T019／U5。',
  '',
  '=== 回傳 ===',
  '以 StructuredOutput 回 `{agentStatus, blockers, notes}`。★`agentStatus` 只表你自己能否完成審查。',
].join('\n')

const QUALITY_REVIEW_PROMPT = [
  '你是 008-audit-settings-pages 之 **U4 執行單元**的**碼品質審查員**。前一輪規格對照審查已收斂，本輪看品質與可維護性。',
  '',
  CONTEXT,
  '',
  '=== 審查面（逐條驗）===',
  '1. **★測試非 vacuous**：逐支新測問「把被守的那行改壞，這支會不會紅？」——特別查 stub-DB 守門測是否真能分辨「守門在觸 DB 前擋下」與「進了 DB 才失敗」；`{minDays}` 明細測是否真斷言到 data 內容而非只看碼。',
  '2. **★變異前提**（rev5:L-063）：被守面是否已有實例？零實例＝測空集合。',
  '3. **詞彙第九值的釘子完整性**：`EXPECTED_LITERALS` 與 `ALL` 的恰等比對是否**含序**（插錯位要紅）？測名與訊息改寫後，是否仍能讓下一個想加第十值的人知道「須新 ADR」？',
  '4. **交易邊界**：purge 的 DELETE 與自記是否真在同一 `txn`？有沒有 `.ok()` 吞掉自記錯誤的路徑（★那會讓 T019 的 fault-injection 測寫不出來、且正是 rev5:B-125 的危害形）？',
  '5. **rev4 參照紀律**：註解提及 rev4 是否全帶 `rev4:` 前綴？有無整段照抄痕跡？`purge` 小寫的理由是否在註解裡寫明（防後人「修正」回大寫）？',
  '6. **註解品質**：守門固定序的**次序理由**是否有註（為何先驗 table 再驗天數）？自記豁免的理由（後設證據永久保留）是否有註？',
  '7. **i18n 圈界與一致性**：四個 base-web 檔的改動是否合乎 fork-delta-lint 解析形？★實跑 `python3 tools/fork-delta-lint.py` 據實回報。三語譯文的語氣是否與既有 backend 樹一致？',
  '8. **可見性與名冊閘**（rev5:L-069／rev5:L-080）：本單元若放寬可見性，查有無 token 掃描閘守著；★本單元**不新增檔**，但若你發現有以檔案/模組清單為受檢面的名冊會因本單元改動而失準，報出來。',
  '9. **lint 與 fmt**：★實跑 `python3 tools/docs-sync.py lint` 與容器內 `cargo fmt --all --check`（★帶 `--check` 才唯讀），據實回報。',
  '10. **未竟事項留帳**：寫進 `notes` 供主線落 BACKLOG（★不要自己改 BACKLOG）。',
  '',
  '=== 不可違反項 ===',
  '★你是**審查員：只讀不寫**。可跑唯讀命令取證；`cargo fmt` 務必帶 `--check`。',
  '★一切書面產物一律 **zh-TW**。★絕不 push／merge／commit。★絕不寫入 `../fork260509-rev5/`。',
  '★blocker 的 `summary` 是結構化比較鍵。★只報真缺陷；風格偏好放 `notes`。',
  '★**勿誤報**：rev5:Lint24 第三腿與 fault-injection 原子性測皆歸 U5，本單元不做＝既定次序。',
  '',
  '=== 回傳 ===',
  '以 StructuredOutput 回 `{agentStatus, blockers, notes}`。`agentStatus` 只表你自己能否完成審查。',
].join('\n')


function rejectedBlock(rejected) {
  if (!rejected.length) return ''
  const lines = [
    '',
    '=== ★前輪已駁回 findings 清單（勿沿用被駁論據重報）===',
    '下列 findings 已由前輪 fix 判定不成立並附理由。**明令**：不得以同一論據重報；同一 finding 若要再報，MUST 附**新證據**（新的 grep 命中、新的碼引用、新的測試輸出），否則該報將直接計入收斂判定、視為未推進。',
  ]
  rejected.forEach(function (x, i) {
    lines.push('' + (i + 1) + '. 檔案：' + x.file)
    lines.push('   摘要：' + x.summary)
    lines.push('   駁回理由：' + x.why)
  })
  return lines.join('\n')
}

function fixPrompt(blockers, roundNo) {
  const items = blockers.map(function (b, i) {
    return '' + (i + 1) + '. 檔案：' + b.file + '\n   缺陷：' + b.summary + '\n   證據與建議：' + b.detail
  })
  return [
    '你是 008-audit-settings-pages 之 **' + UNIT + ' 執行單元**的 **fix agent**（第 ' + roundNo + ' 輪修復）。',
    '',
    CONTEXT,
    '',
    '=== 本輪待處理 findings ===',
    items.join('\n'),
    '',
    '=== 處置紀律 ===',
    '· 逐條判斷 finding 是否**真的成立**——審查員也會出錯（★勿誤報項見審查 prompt 末段）。成立就修；**不成立就據實駁回**，放進 `rejectedFindings`（附 `file`／`summary`〔逐字沿用上面那句摘要〕／`why`）。',
    '· ★不要為了讓審查通過而做「表面修改」——那會讓下一輪重報同一問題、觸發不收斂判定。',
    '· ★**補守門一律做變異測試**：把被指的那行改壞→跑測確認會紅→還原。不做這步，補的就是另一個裝飾性守門。',
    '· 修改一律限在允許清單內。清單外需要動＝**絕不擅改**，依 status 分值升級。',
    '· 修完 MUST 重跑自驗（容器內 `cargo fmt --all`＋全量 serial `cargo test`＋`docs-sync.py lint`），實際輸出摘要寫進 report。',
    '',
    RULES,
    '',
    ALLOWED_BLOCK,
    '',
    '=== 回傳 ===',
    '以 StructuredOutput 回 `{status, report, filesChanged, escalations?, rejectedFindings?}`。',
    '`filesChanged` MUST 據實填本輪**實際寫入**的檔（一個字都沒改就填空陣列——script 以連兩輪零改動作為不收斂訊號）。',
  ].join('\n')
}

async function cycle(phaseName, reviewPrompt, tag) {
  let prevKeys = null
  let emptyChangeStreak = 0
  const rejected = []
  let lastBlockers = []
  for (let r = 0; r <= MAX_FIX_ROUNDS; r++) {
    const isConfirm = r === MAX_FIX_ROUNDS
    const head = isConfirm
      ? '★本輪＝**確認輪**（第 ' + (r + 1) + ' 輪、fix 迴圈已跑滿上限）：只審不修，若無 blocker 即判收斂。'
      : '★本輪＝第 ' + (r + 1) + ' 輪審查。'
    const rv = await spawn(
      [head, '', reviewPrompt, rejectedBlock(rejected)].join('\n'),
      Object.assign({ label: tag + ':review-' + (r + 1), phase: phaseName, schema: REVIEW_SCHEMA }, REVIEW_OPTS)
    )
    if (!rv) return { converged: false, reason: 'review agent 回傳 null（終止型故障）', blockers: lastBlockers, rejected }
    if (rv.agentStatus === 'failed') {
      return { converged: false, reason: 'review agent 自陳受阻（agentStatus=failed）：' + (rv.notes || ''), blockers: lastBlockers, rejected }
    }
    const blockers = rv.blockers || []
    if (blockers.length === 0) return { converged: true, blockers: [], rounds: r + 1, rejected, notes: rv.notes || '' }
    lastBlockers = blockers
    const keys = blockers.map(function (b) { return b.file + '||' + b.summary }).sort().join('\n')
    if (prevKeys !== null && prevKeys === keys) {
      return { converged: false, reason: '⑤收斂偵測：連兩輪 blocker 集合（file×summary）完全相同', blockers, rejected }
    }
    prevKeys = keys
    if (isConfirm) return { converged: false, reason: '確認輪仍有 blocker', blockers, rejected }
    const fx = await spawn(
      fixPrompt(blockers, r + 1),
      Object.assign({ label: tag + ':fix-' + (r + 1), phase: phaseName, schema: WORK_SCHEMA }, FIX_OPTS)
    )
    if (!fx) return { converged: false, reason: 'fix agent 回傳 null（終止型故障）', blockers, rejected }
    if (fx.status === 'blocked') {
      return { converged: false, reason: 'fix agent blocked：' + fx.report, blockers, rejected, escalations: fx.escalations || [] }
    }
    ;(fx.rejectedFindings || []).forEach(function (x) { rejected.push(x) })
    // ★rev5:L-078：fix 因「findings 全落允許清單外」而正確零改動時，當場 return 升級主線——
    //   不可讓它掉進下方「連兩輪零改動」偵測（那是為 status:ok 的真空轉設的，兩者外觀相同、
    //   差別只在 status），否則正確的防呆⑥反應會被判成故障、且白跑兩輪 review。
    if (fx.status === 'done_with_escalation' && (fx.filesChanged || []).length === 0) {
      return {
        converged: false,
        reason: 'fix 判本輪 findings 全落允許清單外、已升級主線（非不收斂；詳 escalations 與 blockers）',
        blockers, rejected, escalations: fx.escalations || [],
      }
    }
    const changed = (fx.filesChanged || []).length
    emptyChangeStreak = changed === 0 ? emptyChangeStreak + 1 : 0
    if (emptyChangeStreak >= 2) {
      return { converged: false, reason: '⑤收斂偵測：fix 連兩輪零改動', blockers, rejected }
    }
  }
  return { converged: false, reason: '迴圈異常結束（不應到達）', blockers: lastBlockers, rejected }
}


// ─────────────────── 主流程（serial） ───────────────────
phase(PH1)
log(START_LOG)

const impl1 = await spawn(IMPL1_PROMPT, Object.assign({ label: LBL1, phase: PH1, schema: WORK_SCHEMA }, IMPL_OPTS))
if (!impl1) return { unit: UNIT, status: 'failed', reason: 'implementer-1 回傳 null（終止型故障）', agentsSpawned: spawned }
if (impl1.status === 'blocked') {
  return { unit: UNIT, status: 'blocked', stage: PH1, reason: 'implementer-1 受阻', report: impl1.report, escalations: impl1.escalations || [], agentsSpawned: spawned }
}
log('implementer-1 完成（status=' + impl1.status + '、改檔 ' + (impl1.filesChanged || []).length + ' 支）→ 進接線層')

phase(PH2)
const impl2 = await spawn(impl2Prompt(impl1.report), Object.assign({ label: LBL2, phase: PH2, schema: WORK_SCHEMA }, IMPL_OPTS))
if (!impl2) return { unit: UNIT, status: 'failed', reason: 'implementer-2 回傳 null（終止型故障）', impl1Report: impl1.report, agentsSpawned: spawned }
if (impl2.status === 'blocked') {
  return { unit: UNIT, status: 'blocked', stage: PH2, reason: 'implementer-2 受阻', report: impl2.report, impl1Report: impl1.report, escalations: impl2.escalations || [], agentsSpawned: spawned }
}
log('implementer-2 完成（status=' + impl2.status + '、改檔 ' + (impl2.filesChanged || []).length + ' 支）→ 進規格對照審查')

phase('SpecReview')
const c1 = await cycle('SpecReview', SPEC_REVIEW_PROMPT, 'spec')
if (!c1.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'SpecReview', reason: c1.reason, blockers: c1.blockers, rejected: c1.rejected, impl1Report: impl1.report, impl2Report: impl2.report, agentsSpawned: spawned }
}
log('規格對照審查收斂（' + c1.rounds + ' 輪）→ 進碼品質審查')

phase('CodeQualityReview')
const c2 = await cycle('CodeQualityReview', QUALITY_REVIEW_PROMPT, 'quality')
if (!c2.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'CodeQualityReview', reason: c2.reason, blockers: c2.blockers, rejected: c2.rejected, impl1Report: impl1.report, impl2Report: impl2.report, specNotes: c1.notes, agentsSpawned: spawned }
}

return {
  unit: UNIT,
  status: 'ok',
  impl1Status: impl1.status,
  impl1Report: impl1.report,
  impl2Status: impl2.status,
  impl2Report: impl2.report,
  filesChanged: (impl1.filesChanged || []).concat(impl2.filesChanged || []),
  escalations: (impl1.escalations || []).concat(impl2.escalations || []),
  specReviewRounds: c1.rounds,
  specReviewNotes: c1.notes,
  qualityReviewRounds: c2.rounds,
  qualityReviewNotes: c2.notes,
  agentsSpawned: spawned,
}
