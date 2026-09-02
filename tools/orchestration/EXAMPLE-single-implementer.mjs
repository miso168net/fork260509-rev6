export const meta = {
  name: 'u4b-purge-sink-to-facade-008',
  description: '008 U4b（user 親決取 (a)）：purge 水平線 DELETE 自 handler raw SQL 下沉至四源 facade 之 purge_before；facade 檔頭 delete 禁令據憲法島 J3 改述',
  phases: [
    { title: 'Impl1', detail: 'implementer：四 facade 補 purge_before＋handler 改 match 分派＋檔頭據島 J3 改述' },
    { title: 'SpecReview', detail: '規格對照審查＋fix 迴圈' },
    { title: 'CodeQualityReview', detail: '碼品質審查＋fix 迴圈' },
  ],
}

const UNIT = 'U4b'
const PH1 = 'Impl1'
const LBL1 = 'u4b:implementer-sink'
const START_LOG = 'U4b 起手（user 親決取 (a) 下沉 facade）：purge DELETE 自 handler raw SQL 下沉至四源 facade'

if (typeof args !== 'undefined' && args !== null) {
  throw new Error('防呆①：本 script 不接受 args——一切邊界寫死於 script 常數')
}

const MAX_FIX_ROUNDS = 3
const CYCLES = 2
const IMPLEMENTERS = 1
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
  '★允許檔案清單（本單元唯一可寫面；皆在 `rust-api/` 子庫內）：',
  '  1. `server/src/model/facade/sys_operation_log.rs`——補 `purge_before`＋**檔頭 delete 禁令據島 J3 改述**',
  '  2. `server/src/model/facade/sys_access_log.rs`——補 `purge_before`＋**改對 `:8` 那句「亦不預開 purge（歸 008 T014／U4）」的前指標**（U4 已完工、該句現指向空處）',
  '  3. `server/src/model/facade/sys_login_attempt.rs`——補 `purge_before`（＋檔頭同族禁令若有，一併據島 J3 改述）',
  '  4. `server/src/model/facade/session_event.rs`——補 `purge_before`（同上）',
  '  5. `server/src/handler/audit.rs`——★**只准**改 `PurgeAuditTable::purge_before` 的**實作本體**（raw SQL → match 分派至 facade）＋其相關碼註（含 `:561-585` 節首那段自陳「零 ADR／spec 承載、待主線裁決」的★★段——now 已由 user 親決取下沉形，該段須改寫為現形的說明，不留待決字樣）。★守門固定序、DTO、msg key、`PURGE_MIN_DAYS`、既有測試 mod **一字不動**。',
  '★★**限定式項的分值語意（rev5:L-075）**：第 5 項帶「只准…／一字不動」限定語＝**改動面級**授權，該檔之限定外改動＝視同清單外，MUST 走 `done_with_escalation`，★不得因「檔在清單內」就回 `status: ok`。',
  '★清單外明確不得動：`server/src/model/audit_query.rs`／`router.rs`／`handler/role.rs`／`error.rs`／`model/audit.rs`／`tests/**`／`base-web/**`／`docs/**`／`specs/**`／`tools/**`（皆 U4 已交付或歸他單元；發現缺陷＝升級主線）。',
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
  '工作區＝rev6-admin 傘狀 workspace（`/mnt/d/AnewSpaces/x_Project/fork260509-rev6`），操作手冊＝根目錄 `CLAUDE.md`（★先讀 §6 硬禁令）。後端＝`rust-api/`（git worktree 子庫）。',
  '本刀＝`008-audit-settings-pages`。本執行單元＝**U4b**＝U4 碼品質審查抓出的**分層破例修正**，經 user 親決取「下沉 facade」形（2026-09-01）。',
  '',
  '=== 為什麼有這一支（背景，逐條有出處）===',
  'U4 落 purge 端點時，水平線 DELETE 被寫成 **handler 內的 raw SQL**（`server/src/handler/audit.rs:708-719`，四張表各一條 `DELETE FROM …`），繞過 facade 層。成因是**主線的允許清單缺口**（U4 沒把 `model/facade/**` 列進可寫面），implementer 在受限下選了 raw SQL 並在碼註誠實標記「本佈局零 ADR／spec 承載、待主線裁決」。',
  '主線查證四項事實後提請 user 拍板：',
  '  ①**rev4 藍本是走 facade 的**——`../fork260509-rev4/rust-api/server/src/model/facade/{sys_operation_log,sys_access_log,sys_login_attempt,session_event}.rs` 各有 `pub async fn purge_before`，handler 側（rev4:handler/audit.rs:529-539）只是 `match self` 分派。',
  '  ②`specs/008-audit-settings-pages/research.md` D2 把「handler 內散裝 SQL」逐字記為**棄案**、理由「違 facade 慣例」。',
  '  ③`specs/008-audit-settings-pages/plan.md:115` 逐字寫 purge 採「rev4 藍本形」。',
  '  ④`rust-api/server/tests/entity_access_lint.rs` 只掃 path-root `entity::` token ⇒ **raw SQL 掃不到**，該破例目前**零機器守**、全測是綠的。',
  '★**user 親決＝(a) 下沉 facade**。本單元執行該決定。',
  '',
  '=== ★關鍵：facade 檔頭的 delete 禁令要據憲法島 J3 改述（不是破例）===',
  '`server/src/model/facade/sys_operation_log.rs:5` 現逐字：「…**不可竄改** ⇒ 本檔恰一支寫端 [`write_in_txn`]，**MUST NOT** 長出 update／delete…」（憲法 §I.6 append-only 變體 B 紀律）。',
  '而本刀 U0 剛入憲的 **§I.7 島 J3** 逐字：「水平線 retention 刪除不屬 §I.6 變體 B 所禁之『竄改』——**本條為其權威釋義**。」',
  '⇒ 補 `purge_before` **有憲法依據**，不是破例；但那句檔頭禁令現在**不完整**（它寫成無例外的絕對句），MUST 據島 J3 改述為「禁 update／任意 delete；**水平線 retention 刪除除外**（憲法 §I.7 島 J3 之權威釋義）」之類的形——★逐字自行斟酌，但必須①保留原禁令的力度②指名島 J3 為例外依據③讓下一個讀者不會以為 purge 是偷渡的。',
  '另 `server/src/model/facade/sys_access_log.rs:8` 逐字「亦不預開 purge（歸 008 T014／U4）」——U4 已完工而 facade 一直沒有 purge，**該前指標現在指向空處**、須同批改對。',
  '',
  '=== 事實接地（每條附出處；★本段與碼衝突時以碼為準並在 report 指出）===',
  '· 現行 handler 側分派器＝`server/src/handler/audit.rs` 的 `impl PurgeAuditTable` 內 `purge_before`（raw SQL 本體在 :708-719 附近；`Statement::from_sql_and_values` 形）。op-log 那條帶 `operation <> $2` 豁免、字面接 `AuditOperation::Purge.as_str()`（★**單一權威、勿改成手抄字面**）。',
  '· 四張表的 DELETE 條件皆為 `created_at < now() - ($1 * interval \x271 day\x27)`；op-log 版多一個豁免臂。',
  '· facade 既有形參照：同目錄各檔的 `pub(crate) async fn list<C: ConnectionTrait>(…)`（U2 交付）＝簽章與 doc 密度的範本。',
  '· rev4 對應物（唯讀藍本）：`../fork260509-rev4/rust-api/server/src/model/facade/sys_operation_log.rs:162-176` 等四支。★**絕不寫入 rev4 樹**；重打字消化、註解重寫帶 `rev4:` 前綴。',
  '· 基線：容器內全量 serial 現況＝**1093 passed／0 failed／2 ignored**（U4 後）。本單元是**重構**（行為不變）⇒ 完工後測試數應**不變**、且全綠。',
].join('\n')

const IMPL1_PROMPT = [
  '你是 rev5:008-audit-settings-pages 之 **U4b 執行單元**的 implementer。本單元是**行為不變的重構**：把已經在跑的 purge DELETE 從 handler 下沉到 facade。',
  '',
  CONTEXT,
  '',
  '=== 你的交付 ===',
  '1. **四張 facade 各補一支 `purge_before`**（簽章形照 rev4 藍本與同目錄既有 `list`：泛型 `C: ConnectionTrait`、收 `before_days`、回 `Result<u64, DbErr>`＝刪除列數）。SQL 本體自 handler 原樣搬下（★行為零變更：條件、型別、op-log 的 `operation <> …` 豁免臂皆不動；豁免臂的字面**繼續接** `AuditOperation::Purge.as_str()` 這個單一權威、勿改手抄）。',
  '2. **handler 的 `PurgeAuditTable::purge_before` 改為 `match self` 分派**至四支 facade（形照 rev4:handler/audit.rs:529-539）。handler 自此零 raw SQL。',
  '3. **facade 檔頭的 delete 禁令據島 J3 改述**（見上「關鍵」段）；`sys_access_log.rs:8` 的前指標改對。',
  '4. **`handler/audit.rs` 節首那段自陳「零 ADR／spec 承載、待主線裁決」的★★段改寫**——現已由 user 親決取下沉形，該段須改成現形的說明（分派至 facade、依島 J3），**不留任何待決字樣**。',
  '5. ★**測試**：四支 facade fn 各補行為測（水平線邊界：剛好等於界的列不刪／早於界的列刪；op-log 版另測**自記豁免**——`operation = \x27purge\x27` 的舊列即使早於水平線也不刪）。★先紅後綠。',
  '',
  '=== 完工前自驗（逐項實跑、實際輸出寫進 report）===',
  '1. 容器內 `cargo fmt --all`',
  '2. 容器內全量 serial `cargo test --workspace -- --test-threads=1` → **0 failed**；★因本單元是重構，既有 purge 測（`purge_tests`／endpoint 面）**必須原樣通過**——它們是行為不變的證據。',
  '3. `grep -n "DELETE FROM" rust-api/server/src/handler/audit.rs` → **零命中**（下沉完成的機器證）',
  '4. `python3 tools/docs-sync.py lint` → 零新增紅',
  '5. `grep -rn "待主線裁決\\|待決" rust-api/server/src/handler/audit.rs` → 零命中',
  '',
  RULES,
  '',
  ALLOWED_BLOCK,
  '',
  '=== 回傳 ===',
  '以 StructuredOutput 回 `{status, report, filesChanged, escalations?, rejectedFindings?}`。`report` 用 zh-TW 寫清四支 facade fn 的簽章、檔頭改述的逐字、五項自驗的實際輸出。',
].join('\n')

const SPEC_REVIEW_PROMPT = [
  '你是 rev5:008-audit-settings-pages 之 **U4b 執行單元**的**規格對照審查員**。本單元是行為不變的重構（purge DELETE 下沉 facade，user 親決取 (a)）。',
  '',
  CONTEXT,
  '',
  '=== 審查面（逐條驗；★自行讀碼／跑唯讀命令取證）===',
  '1. **下沉完整性**：`grep -n "DELETE FROM" rust-api/server/src/handler/audit.rs` 是否**零命中**？handler 是否只剩 `match self` 分派？',
  '2. **行為零變更**：四支 facade 的 SQL 條件、型別、op-log 豁免臂是否與原 handler 版**逐字等價**？★豁免臂的字面是否**仍接** `AuditOperation::Purge.as_str()`（改成手抄字面即 blocker——那會讓詞彙單一權威失效）？',
  '3. **既有測原樣通過**：U4 落的 `purge_tests` 與 endpoint 面測是否**未被改動**且全綠？（★它們是行為不變的證據；若被改了，要問為什麼）',
  '4. **檔頭改述**：facade 的 delete 禁令是否據**憲法島 J3** 改述、指名該條為例外依據？改述是否①保留原禁令力度②不讓讀者以為 purge 是偷渡的？`sys_access_log.rs:8` 的前指標是否改對？',
  '5. **待決字樣清除**：`handler/audit.rs` 是否已無「待主線裁決／待決」字樣？改寫後的說明是否正確反映現形（分派至 facade、依島 J3、user 親決）？',
  '6. **新測非 vacuous**：四支 facade 的行為測是否真能抓到漂移？★水平線邊界測是否有**剛好等於界**的樣本（只測「早於」與「晚於」抓不到 `<` 誤寫成 `<=`）？op-log 的自記豁免測是否真的 seed 了一列 `operation = \x27purge\x27` 的舊列（零實例＝測空集合、rev5:L-063）？',
  '7. **射程越界**：是否動了允許清單外的檔？★`handler/audit.rs` 的守門固定序、DTO、msg key、`PURGE_MIN_DAYS`、既有測試 mod 是否**一字未動**（`git diff` 逐行看）？',
  '',
  '=== 不可違反項 ===',
  '★你是**審查員：只讀不寫**；可跑唯讀命令取證，`cargo fmt` 務必帶 `--check`。',
  '★一切書面產物一律 **zh-TW**。★絕不 push／merge／commit。★絕不寫入 `../fork260509-rev5/`。',
  '★blocker 的 `summary` 是結構化比較鍵。★只報真缺陷；風格偏好放 `notes`。',
  '',
  '=== 回傳 ===',
  '以 StructuredOutput 回 `{agentStatus, blockers, notes}`。★`agentStatus` 只表你自己能否完成審查。',
].join('\n')

const QUALITY_REVIEW_PROMPT = [
  '你是 rev5:008-audit-settings-pages 之 **U4b 執行單元**的**碼品質審查員**。前一輪規格對照審查已收斂。',
  '',
  CONTEXT,
  '',
  '=== 審查面 ===',
  '1. **★測試非 vacuous**：逐支新測問「把被守的那行改壞會不會紅」——特別查水平線比較運算子（`<` vs `<=`）與 op-log 豁免臂是否各有能抓到的樣本。',
  '2. **facade 層一致性**：四支 `purge_before` 的簽章、泛型、錯誤型、doc 密度是否與同目錄既有 fn（U2 落的 `list`）一致？是否有四份幾乎相同卻各自漂移的實作（可收攏卻沒收攏）？★若判定該收攏，說明收攏後誰是單一權威。',
  '3. **rev4 參照紀律**：註解提及 rev4 是否全帶 `rev4:` 前綴？有無整段照抄痕跡（要求重打字消化）？',
  '4. **註解品質**：`purge_before` 的 doc 是否寫明**為什麼 append-only 表可以有 delete**（指島 J3）？水平線語意（`created_at < now() - N days`）是否有註？',
  '5. **憲法一致性**：改述後的 facade 檔頭與憲法 §I.6 變體 B ＋ §I.7 島 J3 是否**兩邊都對得上**？有無製造新的懸空指涉？',
  '6. **lint 與 fmt**：★實跑 `python3 tools/docs-sync.py lint` 與容器內 `cargo fmt --all --check`，據實回報。',
  '7. **未竟事項留帳**：寫進 `notes` 供主線落 BACKLOG（★不要自己改 BACKLOG）。',
  '',
  '=== 不可違反項 ===',
  '★審查員：只讀不寫；`cargo fmt` 務必帶 `--check`。★一律 zh-TW。★絕不 push／merge／commit／寫入 rev5 樹。',
  '★blocker 的 `summary` 是結構化比較鍵。★只報真缺陷；風格偏好放 `notes`。',
  '',
  '=== 回傳 ===',
  '以 StructuredOutput 回 `{agentStatus, blockers, notes}`。',
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
    '你是 rev5:008-audit-settings-pages 之 **' + UNIT + ' 執行單元**的 **fix agent**（第 ' + roundNo + ' 輪修復）。',
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

const impl = await spawn(IMPL1_PROMPT, Object.assign({ label: LBL1, phase: PH1, schema: WORK_SCHEMA }, IMPL_OPTS))
if (!impl) return { unit: UNIT, status: 'failed', reason: 'implementer 回傳 null（終止型故障）', agentsSpawned: spawned }
if (impl.status === 'blocked') {
  return { unit: UNIT, status: 'blocked', reason: 'implementer 受阻', report: impl.report, escalations: impl.escalations || [], agentsSpawned: spawned }
}
log('implementer 完成（status=' + impl.status + '、改檔 ' + (impl.filesChanged || []).length + ' 支）→ 進契約對照審查')

phase('SpecReview')
const c1 = await cycle('SpecReview', SPEC_REVIEW_PROMPT, 'spec')
if (!c1.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'SpecReview', reason: c1.reason, blockers: c1.blockers, rejected: c1.rejected, implReport: impl.report, implStatus: impl.status, agentsSpawned: spawned }
}
log('契約對照審查收斂（' + c1.rounds + ' 輪）→ 進碼品質審查')

phase('CodeQualityReview')
const c2 = await cycle('CodeQualityReview', QUALITY_REVIEW_PROMPT, 'quality')
if (!c2.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'CodeQualityReview', reason: c2.reason, blockers: c2.blockers, rejected: c2.rejected, implReport: impl.report, implStatus: impl.status, specNotes: c1.notes, agentsSpawned: spawned }
}

return {
  unit: UNIT,
  status: 'ok',
  implStatus: impl.status,
  implReport: impl.report,
  filesChanged: impl.filesChanged || [],
  escalations: impl.escalations || [],
  specReviewRounds: c1.rounds,
  specReviewNotes: c1.notes,
  qualityReviewRounds: c2.rounds,
  qualityReviewNotes: c2.notes,
  agentsSpawned: spawned,
}
