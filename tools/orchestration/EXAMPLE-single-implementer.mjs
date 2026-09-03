// 本檔＝rev5:008-audit-settings-pages U4b 組裝成品原樣：內含 rev5／rev4 座標與事實
// （憲法版號 1.10.0、島 J3、rev5:008-audit-settings-pages 的 specs/ 路徑、tools/docs-sync.py 等工具名、../fork260509-rev4/ 樹、
// 行號形引用）；非 rev6 現況、勿照抄執行；rev6 首個含 Workflow 的刀重組時替換（BL-00001）。
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


// 機器生成：python3 tools/docsync generate（自 docs/ops/RULES.md 之 rules emit）——嚴禁手改；差異由 pre-commit check 攔下
const RULES = `=== RULES scope=implementer（38 條）===
RL-0001｜拍板級條目施工前先查拍板紀錄（ADR／events／NOTES）；查無即先問、不以概括指示豁免。勘誤一律以 \`python3 tools/docsync errata <詞>\` 機器枚舉全 repo 逐處處置、禁止只修被點名處；自擬樣式只取最短公共子串。
RL-0002｜世代字串殘留掃描同列三形（連字號後綴／黏斜線路徑段／裸詞邊界）；先證樣式集完備、再證零命中——只證所列樣式零命中不算零殘留。
RL-0005｜子庫 git 操作一律 \`git -C <子庫>\` 形、不 cd 進子庫；破壞性驗證每項還原後立即 \`git -C <子庫> status --porcelain\` 確認回基準態、單獨跑不疊加。
RL-0007｜非零退出先看首行輸出：\`error:\` 起首＝工具層拒跑、\`FAILED\`／\`panicked\`＝受測物真失敗；迴圈跑測試連首行錯誤一併印。
RL-0011｜凡改變某數字／集合／方向／名稱／單一權威＝\`grep -rn\` 枚舉全 repo 同語意命中逐處回報；允許清單內自改、清單外依 status 分值升級；史述保留、現在式改對。
RL-0012｜agent status 分 \`blocked\`（整件做不下去、主線立刻接手）與 \`done_with_escalation\`（交付已完成、只有清單外待辦、附 escalations）兩值；只有前者觸發 script 立即 return、後者照常進審查。
RL-0015｜預告必標成預告並附回填義務（該刀 tasks 同批加回填條）；活書家族零未來式，覆核把「屆時／日後／將由」當同義集掃。
RL-0019｜暫改真檔驗紅後以存原文寫回還原、禁 \`git checkout\` 整檔還原（會丟該檔其它未 commit 改動）；還原後 \`git diff --name-only\` 證零殘留。
RL-0020｜ops 帳本提及刀號／單元輪次一律寫「本刀 U2」形、不寫裸刀號；新建 ops 檔先 \`git add\` 再驗 lint 才進掃描面。
RL-0021｜變異紅證必印 skipped=0；探針就地變異或改寫 ROOT、不自 repo 外載入 mutant。
RL-0022｜只准動允許檔清單內的檔；清單外需要動＝絕不擅改、依 status 分值升級；限定式清單項附「本檔之限定外改動＝清單外、走 done_with_escalation」；主線復核看 \`git diff\` 實際改動面、不看 escalations 欄下結論。
RL-0023｜枚舉同語意命中逐行剝 token 再判、不 \`grep -v\` 過濾整行（同行雙 token 會漏）；枚舉筆數要有第二來源對賬。
RL-0024｜對賬 schema 真源腳本化：真源與文件各拉 {欄名:可空性} 比對；可空性以 migration／entity 為準；同檔同型欄寫法不一致即失真訊號。
RL-0026｜驗「呼叫處恰 N 處」取 \`name(\`／\`(name)\`／\`::name\` 三形聯集，或改名讓編譯器列出真實使用點；處數型驗收由測試釘、不由人 grep。
RL-0027｜連動面盤點數字釘與手抄名冊釘並行（新增一個檔本身就是集合改變）；新增檔的單元把全量測試排在實作早期。
RL-0029｜變異注入前先讀 detector 排除條件、變異要打在該閘判準上；未紅先印 scanned/hits 自證進入受檢面；閘的 doc 自陳該注入什麼形。
RL-0031｜走查還原的清理面含被改列的審計欄（改回值≠改回痕）；\`setval\` 等還原值自本次 baseline 現讀、不沿用上次指令；baseline 對賬與閘綠是兩道網、都綠才算還原。
RL-0035｜模板是起手結構不是表單：每節依實況寫，無實體即一句「目前無」附理由；不填樣板文、不留佔位符。
RL-0037｜每個 AI 元件至少一條可量測品質情境（來源／刺激／環境／回應，含門檻與期限）。
RL-0039｜記錄跨元件相依與連鎖漂移路徑；不孤立描述單一元件。
RL-0041｜活書 frontmatter 帶 \`rad_ai_map\` 對照鍵；正文子節名一律中文改寫、RAD-AI 文字不逐字複製（只在 README 一句參考來源）；對照總表由 generate 產、不手維護。
RL-0042｜一切書面產物（report／blocker／程式碼註解／文件／commit 訊息）一律 zh-TW；識別字、程式碼、路徑保留原形；每支 agent prompt 必含「zh-TW」字面。
RL-0045｜rust build／test 一律容器內、全程 serial（\`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1\`）；rust 碼完工前容器內 \`cargo fmt --all\`。
RL-0046｜引前代編號一律帶 \`rev5:\`／\`rev4:\` 前綴（ADR、L、B、Lint、刀名皆同）；rev6 新形原生（BL／LL／ADR 五碼、RL 四碼、GT 二碼）；裸刀號禁、\`000-\` 創世家族除外。
RL-0048｜時態分離：活書家族永遠現在式、未來式住 ops、過去式住 git＋events；完成即刪、git 即史；跨檔引用不用行號、不 deep-link 帳本內部錨、不引 per-machine 路徑。
RL-0049｜人寫／事件源／機器生成三材質各有唯一的家；鏡像不是機器生成就是不存在；\`docs/generated/**\` 與 GENERATED_FILES 名冊檔禁手改、只由 generate 重算。
RL-0050｜BL／LL／RL 配號取檔頭 \`<!-- next: -->\` 後 bump、單調遞增、號碼永不回收；刪條目前先掃現在式引用。
RL-0051｜每條閘一正一反自證、掃描面空集合即紅、變異要打在判準上；Day-1 豁免逐筆具名帶解除謂詞、到期即紅。
RL-0054｜機密實值與憑證樣式永不入版控面（含史料面與 tests）；合成樣本執行期串接、不落完整字面；\`CHANGE-ME\` 起首佔位值不算機密。
RL-0056｜bash 內 \`$VAR\` 後不得緊接非 ASCII（bash 3.2 會黏進變數名）；shebang 只用白名單形。
RL-0057｜README 目錄樹、hook 註冊、exec bit 名冊與實檔集機器對賬；名冊改動同刀改齊；子庫任一 pnpm install 後重跑 bootstrap 驗 hooks 指紋。
RL-0063｜agent 絕不 push／merge／git commit／git checkout；只改工作樹，git 操作由主線負責。
RL-0064｜絕不寫入 \`../fork260509-rev5/\`（含子庫與源倉；凍結 SHA 由 bootstrap 斷言）；讀取允許且必要；rev5 stack（埠 2xxxx）不做 schema／seed／設定變更或 \`down -v\`，rev6 走 3xxxx。
RL-0065｜實作先讀 rev5 對應碼（唯讀）、高度參照但重打字消化不拷貝；註解一律重寫、rev5 出處帶 \`rev5:\` 前綴；rev6 拍板已推翻的行為不得帶回。
RL-0066｜TDD 先紅後綠：每個可測面先寫會紅的測、跑到真的紅、再寫實作到綠；分階段推進，每階段容器內 serial 跑一次測試確認綠再進下一階段。
RL-0067｜變異自證前提＝被守面已有實例；零實例＝測空集合、紅證結構性 vacuous——延後到實例出現後補做並在 tasks 記回填條。
RL-0068｜對破壞性守門做變異測試先掛快照還原式守衛（arm 拍快照、drop 還原）；刪除式清理守衛救不了 seed 列。
RL-0069｜「應該被拒」的負向樣本業務鍵也帶清理鍵前綴（帶前綴但仍違規的構造），否則守門被改壞那一發的殘列圈不到。
RULES-VERSION: c7a137209e0e
`;
const RULES_REVIEW = `=== RULES scope=review（14 條）===
RL-0011｜凡改變某數字／集合／方向／名稱／單一權威＝\`grep -rn\` 枚舉全 repo 同語意命中逐處回報；允許清單內自改、清單外依 status 分值升級；史述保留、現在式改對。
RL-0015｜預告必標成預告並附回填義務（該刀 tasks 同批加回填條）；活書家族零未來式，覆核把「屆時／日後／將由」當同義集掃。
RL-0026｜驗「呼叫處恰 N 處」取 \`name(\`／\`(name)\`／\`::name\` 三形聯集，或改名讓編譯器列出真實使用點；處數型驗收由測試釘、不由人 grep。
RL-0033｜走查回報「無可觀察實例」或「契約豁免」須附機器反證（psql／grep／原文行號），否則 redo、不得記已知態。
RL-0035｜模板是起手結構不是表單：每節依實況寫，無實體即一句「目前無」附理由；不填樣板文、不留佔位符。
RL-0042｜一切書面產物（report／blocker／程式碼註解／文件／commit 訊息）一律 zh-TW；識別字、程式碼、路徑保留原形；每支 agent prompt 必含「zh-TW」字面。
RL-0043｜review agent 只讀不寫 repo 檔；findings 只放回傳訊息。
RL-0046｜引前代編號一律帶 \`rev5:\`／\`rev4:\` 前綴（ADR、L、B、Lint、刀名皆同）；rev6 新形原生（BL／LL／ADR 五碼、RL 四碼、GT 二碼）；裸刀號禁、\`000-\` 創世家族除外。
RL-0048｜時態分離：活書家族永遠現在式、未來式住 ops、過去式住 git＋events；完成即刪、git 即史；跨檔引用不用行號、不 deep-link 帳本內部錨、不引 per-machine 路徑。
RL-0051｜每條閘一正一反自證、掃描面空集合即紅、變異要打在判準上；Day-1 豁免逐筆具名帶解除謂詞、到期即紅。
RL-0063｜agent 絕不 push／merge／git commit／git checkout；只改工作樹，git 操作由主線負責。
RL-0070｜可見性放寬（私有→pub）前先 grep 函式體內有無被 token 掃描閘守著的呼叫；有則以 finding 要求同批補消費者名冊閘、由 fix 輪落地。
RL-0071｜fix 後次輪 review prompt 必附前輪已駁回 findings 清單（file×summary＋駁回理由）、明令勿沿用被駁論據重報；同一 finding 再報須附新證據，否則計入收斂判定。
RL-0073｜review findings 一律三分流（修／轉 BL-NNNNN／won't-fix 立 ADR）；承載處二分：不定期獨立輪落 \`docs/reviews/\` 報告＋review 事件，feature 收刀之 final holistic review 不落報告、以收單 commit 訊息逐項列處置。
RULES-VERSION: c7a137209e0e
`;
const RULES_FIX = `=== RULES scope=fix（15 條）===
RL-0005｜子庫 git 操作一律 \`git -C <子庫>\` 形、不 cd 進子庫；破壞性驗證每項還原後立即 \`git -C <子庫> status --porcelain\` 確認回基準態、單獨跑不疊加。
RL-0007｜非零退出先看首行輸出：\`error:\` 起首＝工具層拒跑、\`FAILED\`／\`panicked\`＝受測物真失敗；迴圈跑測試連首行錯誤一併印。
RL-0011｜凡改變某數字／集合／方向／名稱／單一權威＝\`grep -rn\` 枚舉全 repo 同語意命中逐處回報；允許清單內自改、清單外依 status 分值升級；史述保留、現在式改對。
RL-0012｜agent status 分 \`blocked\`（整件做不下去、主線立刻接手）與 \`done_with_escalation\`（交付已完成、只有清單外待辦、附 escalations）兩值；只有前者觸發 script 立即 return、後者照常進審查。
RL-0019｜暫改真檔驗紅後以存原文寫回還原、禁 \`git checkout\` 整檔還原（會丟該檔其它未 commit 改動）；還原後 \`git diff --name-only\` 證零殘留。
RL-0022｜只准動允許檔清單內的檔；清單外需要動＝絕不擅改、依 status 分值升級；限定式清單項附「本檔之限定外改動＝清單外、走 done_with_escalation」；主線復核看 \`git diff\` 實際改動面、不看 escalations 欄下結論。
RL-0023｜枚舉同語意命中逐行剝 token 再判、不 \`grep -v\` 過濾整行（同行雙 token 會漏）；枚舉筆數要有第二來源對賬。
RL-0042｜一切書面產物（report／blocker／程式碼註解／文件／commit 訊息）一律 zh-TW；識別字、程式碼、路徑保留原形；每支 agent prompt 必含「zh-TW」字面。
RL-0045｜rust build／test 一律容器內、全程 serial（\`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1\`）；rust 碼完工前容器內 \`cargo fmt --all\`。
RL-0054｜機密實值與憑證樣式永不入版控面（含史料面與 tests）；合成樣本執行期串接、不落完整字面；\`CHANGE-ME\` 起首佔位值不算機密。
RL-0056｜bash 內 \`$VAR\` 後不得緊接非 ASCII（bash 3.2 會黏進變數名）；shebang 只用白名單形。
RL-0063｜agent 絕不 push／merge／git commit／git checkout；只改工作樹，git 操作由主線負責。
RL-0064｜絕不寫入 \`../fork260509-rev5/\`（含子庫與源倉；凍結 SHA 由 bootstrap 斷言）；讀取允許且必要；rev5 stack（埠 2xxxx）不做 schema／seed／設定變更或 \`down -v\`，rev6 走 3xxxx。
RL-0066｜TDD 先紅後綠：每個可測面先寫會紅的測、跑到真的紅、再寫實作到綠；分階段推進，每階段容器內 serial 跑一次測試確認綠再進下一階段。
RL-0070｜可見性放寬（私有→pub）前先 grep 函式體內有無被 token 掃描閘守著的呼叫；有則以 finding 要求同批補消費者名冊閘、由 fix 輪落地。
RULES-VERSION: c7a137209e0e
`;


const CONTEXT = [
  '=== 專案與本單元定位 ===',
  '工作區＝rev6-admin 傘狀 workspace（`<repo 根>`），操作手冊＝根目錄 `CLAUDE.md`（★先讀 §6 硬禁令）。後端＝`rust-api/`（git worktree 子庫）。',
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
