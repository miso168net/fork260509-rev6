// 本檔＝001-schema-baseline U1 組裝成品原樣（rev6 首個 Workflow 單元、雙 implementer serial；tmp/001-assemble.py 拼接
// vars+head+allowed+rules+context+prompts+cycle+main、harness spec｜quality 雙模式全綠後發射；run 結果＝12 支 agent、
// spec 2 輪／quality 4 輪收斂）。供組裝法參考、勿照抄執行：事實接地為發射當時的主線實查，後經 fix／review 更正者
// （adapter 程式面差三行、entity 需改註解 9 檔）以該單元 rust-api commit 訊息為準。
export const meta = {
  name: 'u1-baseline-inherit-001',
  description: '001 U1（T003～T010、T014～T017、T022、T024）：rust-api 骨架＋17 檔逐位元承襲＋sea-orm-adapter 例外①＋容器內 build＋dev stack 重放＋註解改寫清單與機器閘證據',
  phases: [
    { title: 'Impl1', detail: 'implementer-1：三 Cargo＋toolchain／fmt＋adapter 10 檔＋entity 15 檔＋m0001／m0002＋lib／main 自寫＋容器內 build／fmt／lock＋17 檔 parity' },
    { title: 'Impl2', detail: 'implementer-2：dev stack migrate up 斷言＋註解改寫清單機器對賬＋裸編號自掃＋betterleaks／lint 證據＋parity 與 --locked 復驗' },
    { title: 'SpecReview', detail: '規格對照審查＋fix 迴圈' },
    { title: 'CodeQualityReview', detail: '碼品質審查＋fix 迴圈' },
  ],
}

const UNIT = 'U1'
const FEATURE = '001-schema-baseline'
const IMPLEMENTERS = 2
const SMOKE = 'u1-baseline-3f9a'
const START_LOG = 'U1 起手（T003～T010、T014～T017、T022、T024）：implementer-1 落 rust-api 骨架＋17 檔＋adapter、容器內 build'

// 骨架首段（單一骨架、BL-00001 收斂）：防呆①args 斷言／②guard／③保險絲推導＋自我斷言／④兩套 schema（WORK＝status，REVIEW＝agentStatus）。
// ★引用 _vars 段的模板常數：IMPLEMENTERS（本單元 serial implementer 支數、與 _prompts 段 IMPL_STAGES 支數由 _sk_main.js 自我斷言）、
//   SMOKE（冒煙 token；RL-0018 置於各 prompt 共用段、RL-0059 派發前斷言；★不可取字面 test＝wf-watchdog 會當自測子命令）。
if (typeof args !== 'undefined' && args !== null) {
  throw new Error('防呆①：本 script 不接受 args——一切邊界寫死於 script 常數')
}
if (typeof IMPLEMENTERS !== 'number' || !Number.isInteger(IMPLEMENTERS) || IMPLEMENTERS < 1) {
  throw new Error('防呆③：IMPLEMENTERS 須為 ≥1 的整數、由 _vars 段定義（現值 ' + String(IMPLEMENTERS) + '）')
}
if (typeof SMOKE !== 'string' || SMOKE.length < 6 || SMOKE === 'test') {
  throw new Error('防呆②：SMOKE 冒煙 token 須為 ≥6 字元字串且不可取字面 test、由 _vars 段定義（現值 ' + String(SMOKE) + '）')
}

const MAX_FIX_ROUNDS = 3
const CYCLES = 2
const WORST = IMPLEMENTERS + CYCLES * (2 * MAX_FIX_ROUNDS + 1)
const AGENT_FUSE = Math.min(20, WORST + 1)
if (AGENT_FUSE < WORST) {
  throw new Error('防呆③：保險絲 ' + AGENT_FUSE + ' 低於結構最壞值 ' + WORST)
}
let spawned = 0

// 模型家（單一真源；生成表＝docs/generated/reference/agents.md、換模史＝本檔 git log；user 拍板 2026-09-04）：
//   主線與 implementer＝fable 1M xhigh；review／fix＝opus 1M xhigh、且 prompt 首行帶 DEEP_THINK 字面（深思關鍵詞，由 _sk_cycle.js 烤入）。
const IMPL_OPTS = { model: 'fable[1m]', effort: 'xhigh' }
const REVIEW_OPTS = { model: 'opus[1m]', effort: 'xhigh' }
const FIX_OPTS = { model: 'opus[1m]', effort: 'xhigh' }
const DEEP_THINK = 'ultrathink'

function guard(p, label) {
  if (typeof p !== 'string') throw new Error('防呆②：prompt 非字串（label=' + label + '）')
  if (p.length < 400) throw new Error('防呆②：prompt 過短 ' + p.length + '（label=' + label + '）')
  if (p.startsWith('undefined') || p.startsWith('null')) throw new Error('防呆②：prompt 開頭為 undefined／null（label=' + label + '）')
  if (!p.includes('zh-TW')) throw new Error('防呆②：prompt 缺 zh-TW 字面（label=' + label + '）')
  if (!p.includes(SMOKE)) throw new Error('防呆②：prompt 缺冒煙 token ' + SMOKE + '（label=' + label + '；RL-0018 置於共用段）')
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
  '★允許檔案清單（本單元唯一可寫面；皆在 `rust-api/` worktree 內、路徑相對 repo 根）：',
  '  1. `rust-api/Cargo.toml`（自寫）、`rust-api/Cargo.lock`（容器內 cargo 產、入版控）',
  '  2. `rust-api/rust-toolchain.toml`、`rust-api/rustfmt.toml`（自寫；rustfmt 三值承 rev5、註解重寫）',
  '  3. `rust-api/migration/Cargo.toml`、`rust-api/migration/src/lib.rs`、`rust-api/migration/src/main.rs`（自寫、重打字）',
  '  4. `rust-api/migration/src/m0001_baseline_schema.rs`、`rust-api/migration/src/m0002_baseline_seeds.rs`（憲法 §I.5 例外②：**程式零改、只改註解行**）',
  '  5. `rust-api/entity/Cargo.toml`、`rust-api/entity/src/lib.rs`（自寫）',
  '  6. `rust-api/entity/src/{casbin_rule,session_event,sys_access_log,sys_casbin_policy_archive,sys_ip_rule,sys_login_attempt,sys_menu,sys_operation_log,sys_pwd_custody,sys_role,sys_token,sys_user,sys_user_email_verify,sys_user_role,system_settings}.rs`（例外②：**程式零改、只改註解行**）',
  '  7. `rust-api/sea-orm-adapter/**`（憲法 §I.5 例外①整檔拷貝：`Cargo.toml`＋`src/{action,adapter,entity,lib,migration}.rs`＋`examples/{rbac_model.conf,rbac_policy.csv,rbac_with_domains_model.conf,rbac_with_domains_policy.csv}`；程式面**唯一**允許改動＝`src/adapter.rs` 測試模組那一處假 DSN 字面改執行期串接；其餘只改註解行）',
  '★★限定式項的分值語意（rev5:L-075）：第 4／6／7 項「程式零改」＝**改動面級**授權——程式面任何改動（第 7 項 DSN 那一處除外）＝視同清單外、MUST 走 `done_with_escalation`＋escalations 逐條列明，★不得因「檔在清單內」就回 `status: ok`。',
  '★清單外明確不得動：`rust-api/.gitignore`／`rust-api/LICENSE`／`rust-api/x_fork.branch-origin.md`（源倉既有）；外層一切（`docs/**`、`specs/**`、`tools/**`、`.gitleaks.toml`、`docker-compose*.yml`、`deploy/**`、`README.md`）＝主線收尾做；`../fork260509-rev5/**`＝**絕不寫入**（唯讀藍本、bootstrap 斷言凍結 SHA）。',
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
RL-0046｜引前代編號一律帶 \`rev5:\`／\`rev4:\` 前綴（ADR、L、B、Lint、刀名皆同）；rev6 新形原生（BL／LL／ADR 五碼、RL 四碼、GT 二碼、migration 短號 \`m\` 四碼＝ADR-00008）；裸刀號禁、\`000-\` 創世家族除外。
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
RULES-VERSION: 064380371fc0
`;
const RULES_REVIEW = `=== RULES scope=review（14 條）===
RL-0011｜凡改變某數字／集合／方向／名稱／單一權威＝\`grep -rn\` 枚舉全 repo 同語意命中逐處回報；允許清單內自改、清單外依 status 分值升級；史述保留、現在式改對。
RL-0015｜預告必標成預告並附回填義務（該刀 tasks 同批加回填條）；活書家族零未來式，覆核把「屆時／日後／將由」當同義集掃。
RL-0026｜驗「呼叫處恰 N 處」取 \`name(\`／\`(name)\`／\`::name\` 三形聯集，或改名讓編譯器列出真實使用點；處數型驗收由測試釘、不由人 grep。
RL-0033｜走查回報「無可觀察實例」或「契約豁免」須附機器反證（psql／grep／原文行號），否則 redo、不得記已知態。
RL-0035｜模板是起手結構不是表單：每節依實況寫，無實體即一句「目前無」附理由；不填樣板文、不留佔位符。
RL-0042｜一切書面產物（report／blocker／程式碼註解／文件／commit 訊息）一律 zh-TW；識別字、程式碼、路徑保留原形；每支 agent prompt 必含「zh-TW」字面。
RL-0043｜review agent 只讀不寫 repo 檔；findings 只放回傳訊息。
RL-0046｜引前代編號一律帶 \`rev5:\`／\`rev4:\` 前綴（ADR、L、B、Lint、刀名皆同）；rev6 新形原生（BL／LL／ADR 五碼、RL 四碼、GT 二碼、migration 短號 \`m\` 四碼＝ADR-00008）；裸刀號禁、\`000-\` 創世家族除外。
RL-0048｜時態分離：活書家族永遠現在式、未來式住 ops、過去式住 git＋events；完成即刪、git 即史；跨檔引用不用行號、不 deep-link 帳本內部錨、不引 per-machine 路徑。
RL-0051｜每條閘一正一反自證、掃描面空集合即紅、變異要打在判準上；Day-1 豁免逐筆具名帶解除謂詞、到期即紅。
RL-0063｜agent 絕不 push／merge／git commit／git checkout；只改工作樹，git 操作由主線負責。
RL-0070｜可見性放寬（私有→pub）前先 grep 函式體內有無被 token 掃描閘守著的呼叫；有則以 finding 要求同批補消費者名冊閘、由 fix 輪落地。
RL-0071｜fix 後次輪 review prompt 必附前輪已駁回 findings 清單（file×summary＋駁回理由）、明令勿沿用被駁論據重報；同一 finding 再報須附新證據，否則計入收斂判定。
RL-0073｜review findings 一律三分流（修／轉 BL-NNNNN／won't-fix 立 ADR）；承載處二分：不定期獨立輪落 \`docs/reviews/\` 報告＋review 事件，feature 收刀之 final holistic review 不落報告、以收單 commit 訊息逐項列處置。
RULES-VERSION: 064380371fc0
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
RULES-VERSION: 064380371fc0
`;

const CONTEXT = [
  '=== 專案與本單元定位 ===',
  '工作區＝rev6-admin 傘狀 workspace（repo 根＝`CLAUDE.md` 所在；★先讀 §1／§3／§6／§7）。後端＝`rust-api/`（git worktree 子庫、分支長名 `rev6-admin-rust-api`；現況＝源倉 Initial commit＋分支來源紀錄、**零 rust 碼**）。',
  '本刀＝`001-schema-baseline`。本執行單元＝**U1**＝tasks.md **T003～T010、T014～T017、T022、T024**。已完成前置：Task 0（編排骨架收斂）、T002（bootstrap 綠、`rev6-admin-rust-api:dev` 映像已 build、容器內 cargo 1.96.1、dev stack 機密已解密、cargo registry 卷已預熱）。',
  '冒煙 token＝u1-baseline-3f9a。一切書面產物（report／blocker／程式碼註解）一律 **zh-TW**；識別字、程式碼、路徑保留原形。',
  '',
  '=== 必讀（先讀再動手）===',
  '1. `CLAUDE.md` §1／§3／§6／§7',
  '2. `specs/001-schema-baseline/tasks.md`（本單元各 T 條目逐字）＋`spec.md`（FR-001～FR-007、Edge Cases）',
  '3. `specs/001-schema-baseline/research.md` R0～R4（rev5 對應碼清單、版本三源、施工形）＋`quickstart.md` A／B',
  '4. `docs/arc42/decisions/ADR-00009-data-shape-copy-exception.md`（四條件、自證命令形）＋`docs/arc42/decisions/ADR-00010-schema-baseline-and-gate-contract.md`（證據段待補項）',
  '5. `.specify/memory/constitution.md` §I.5（例外①②）；`docs/ops/RULES.md` 名詞段「隨遷工具」（四型失效引用＝註解重寫判準）',
  '6. ★rev5 藍本（**唯讀**、rust-api 凍結 SHA 92919b9）：`../fork260509-rev5/rust-api/` 之 `Cargo.toml`／`rust-toolchain.toml`／`rustfmt.toml`／`migration/`／`entity/`／`sea-orm-adapter/`。**絕不寫入該樹**；收工前 `git -C ../fork260509-rev5/rust-api status --porcelain` 須為空並寫進 report。',
  '',
  '=== 事實接地（★每條附出處；本段與碼衝突時以碼為準、並在 report 指出哪一條錯）===',
  '',
  '**A. 版本與骨架**（research R1；user 拍板 2026-09-04）：`[workspace.dependencies]` **恰五支**＝`sea-orm = { version = "1.1.20", default-features = false }`／`sea-orm-migration = "1.1.20"`／`tokio = "1.53.1"`／`async-trait = "0.1.92"`／`casbin = { version = "2.20.0", default-features = false }`；`members = ["migration", "entity", "sea-orm-adapter"]`（server 隨 002 刀、不列）；`resolver = "2"`；`[workspace.package] edition = "2024"`；`rust-toolchain.toml` channel `1.96.1`（＝`deploy/Dockerfile.rust-api` 之 `rust:1.96.1-slim`）。★不引 argon2、不引任何 auth／web／obs 依賴。',
  '**B. features 恰同 rev5**（R1）：migration＝`sea-orm-adapter = { path = "../sea-orm-adapter" }`＋`sea-orm-migration = { workspace = true, features = ["sqlx-postgres", "runtime-tokio-rustls", "cli"] }`＋`tokio = { workspace = true, features = ["rt-multi-thread", "net", "time"] }`；entity＝`sea-orm = { workspace = true, features = ["macros", "with-chrono", "with-json", "with-ipnetwork"] }`；adapter `Cargo.toml` 承 rev5 原樣（features 表位元不動、只改檔頭註解）。三 member 皆 `edition.workspace = true`（adapter 自帶 `edition = "2021"`、原樣）。',
  '**C. rustfmt.toml 三值**：`max_width = 100`／`use_small_heuristics = "Max"`／`style_edition = "2024"`；註解重寫、出處帶 `rev5:B-112`／`rev5:ADR 0057`（rust-fmt-gate 隨 002 刀）。',
  '**D. 例外②＝恰 17 檔**：`rev5:migration/src/m001_baseline_schema.rs`→`rust-api/migration/src/m0001_baseline_schema.rs`、`rev5:m002_baseline_seeds.rs`→`m0002_baseline_seeds.rs`、entity 15 檔同名。施工形＝`cp` 後**只改註解行**（首個非空白字元為 `//` 的整行，含 `///`／`//!`；rev5 三件零行內尾註解）；程式（含屬性巨集、字串字面、PHC 常數、`2026-08-05T00:00:00+00:00` 時戳字面、setval 值）**一個位元不動**。`m0003` 起 delta 與一切業務碼不適用例外。',
  "**E. parity 自證命令形**（ADR-00009 決定 2①、quickstart A；兩邊各自去註解）：",
  "   strip() { grep -vE '^[[:space:]]*//' \"$1\" | sed -E 's/[[:space:]]+$//' | sed '/^$/d'; }",
  "   diff <(strip ../fork260509-rev5/rust-api/migration/src/m001_baseline_schema.rs) <(strip rust-api/migration/src/m0001_baseline_schema.rs)   # m0002 與 15 entity 檔同形",
  '   期望 17 檔全零輸出（rc 0）；結果（檔數＋rc）寫進 report、由主線記 commit 訊息。',
  '**F. 註解重寫判準＝語意**（clarify 2026-09-04、ADR-00009 決定 2②）：四型失效引用**必改**——①無前綴前代編號（如 `002 FR-021`→`rev5:002` FR-021；`rev2 正確性修正(012 plan Deviation D-1)`→`rev2:012 plan Deviation D-1`）②rev5 語境事實（「rev5 dev 庫」「本檔由 transcribe-m002.py（T008②）自 seed-decision.json 機器轉錄」＝rev5 施工史→改寫成承襲語境並帶 `rev5:` 前綴）③章節號指到 rev6 不存在的節（rev6 data-model §1～§10 與 rev5 同號、多數可留；但 §3 rename map／§4 授權偏離在 rev6 為**史料**——語意改成「rev5 對 rev4 的定稿史、rev6 對 rev5 終態零偏離」）④repo 外權威（`https://github.com/casbin-rs/...` 為第三方原碼出處、可留）。**通用註解可與 rev5 同文**。★rev6 自己的 T 編號／單元號（T003、U1）**不寫進碼註解**（碼註解記設計、不記刀內程序）。',
  '   GT-05 機器兜底：present 面 regex＝`(?<![A-Za-z0-9:_/-])(B-\\d{3}|L-\\d{3}|ADR 0\\d{3}|Lint\\d{2}|\\d{3}-[a-z][a-z0-9]*(?:-[a-z0-9]+)+)(?![A-Za-z0-9-])`（反引號／「」內＝提及形不判；`001-schema-baseline` 為 rev6 刀名可裸寫、rev5 刀名如 `002-system-settings` 不可）；子庫碼面 regex＝`(^|[^A-Za-z0-9:_-])(B-[0-9]{3}|L-[0-9]{3})([^0-9]|$)`——★lint 對子庫掃的是 **HEAD 已 commit 樹**、本單元檔尚未 commit 看不到，實作者以 `grep -rnE` 兩式對 `rust-api/` 自掃、零命中寫進 report。',
  '   主線實查 rev5 原檔的前代引用命中（供逐條處置；★不保證完備、自己再 grep）：',
  '   · rev5:m001：檔頭 `//! m001 — 001-schema-baseline 結構基線…`（改 rev6 語境：`m0001`、承 `rev5:m001` 逐位元、憲法 §I.5 例外②／ADR-00009）；檔頭 §4 授權偏離／§10 防回歸句（改史料語意）；`承 rev4:m009 淨效果`（已前綴、可留）；索引段「idx_*_operator_time 名照 rev4 原樣保留」（語意改「承 rev5 定稿、名稱不動」）。',
  '   · rev5:m002：檔頭 `transcribe-m002.py（T008②）`／`seed-decision.json`／`FR-005`／`clarify Q1／Q2`／`research R3`＝rev5 施工史→改寫（帶 `rev5:` 前綴；rev6 seed 內容權威＝本檔本體、凍結證據＝`specs/001-schema-baseline/fixtures/seed.sql`、data-model §8）；sha256 字面屬 rev5 轉錄證據、以 `rev5:` 史料形保留或刪除皆可。',
  '   · entity：`sys_user_role.rs` 的 `002 FR-021`／`FR-022 拍板`→`rev5:002` FR-021／FR-022；`casbin_rule.rs` 的 `rev4:ADR 0015`（已前綴、可留）；session_event／sys_casbin_policy_archive／sys_pwd_custody／sys_user_email_verify 之「rev5 親排調序／rev5 調序」＝rev5 施工史（語意改「欄序＝rev5 定稿、data-model §2」）；sys_operation_log 的 `§3 rename map` 句（史料語意）。',
  '   · adapter：`Cargo.toml` 首行拷貝鏈→`拷貝自 rev5:rust-api/sea-orm-adapter @ 92919b9（憲法 §I.5 例外①；原鏈 rev4@2b8a101→rev2@1fa2ebd→rev1@0b64a57）`；`action.rs` 的 `rev2 正確性修正(012 plan …)`／`rev1 原碼`→`rev2:012`／`rev1:`；`adapter.rs` 測試模組 doc 之「rev5 dev 庫」「rev5 dev stack」「migration m001」→ rev6 dev 庫（rev6 stack、埠 35432）／`m0001`；★`adapter.rs` 測試模組的假 DSN 字面 （mysql 形、user root 帶六位數字密碼、host localhost:3306、db casbin；完整 URL 字面依 RL-0054 不落本檔）→**執行期串接**（RL-0054、analyze C1；如 `format!("mysql://{}:{}@localhost:3306/casbin", "root", "123456")` 或等價形），零 allowlist、`.gitleaks.toml` 不動；此為 adapter **唯一**程式面改動（與 rev5 差一行）。',
  '**G. 自寫件**（§I.5 先讀後寫、重打字、註解 rev6 語境）：`migration/src/lib.rs`（`pub use sea_orm_migration::prelude::*;`＋`mod m0001_baseline_schema; mod m0002_baseline_seeds;`＋`Migrator` 之 `migrations()` 依序兩支；doc 註解＝基線序列說明、承 `rev5:lib.rs` 形）、`migration/src/main.rs`（`APP_DATABASE_URL_FILE`→`APP_DATABASE_URL`→既有 `DATABASE_URL` 三級、secret 檔讀不到 panic、空值與 `CHANGE-ME` 起首拒啟、多執行緒 runtime、`sea_orm_migration::cli::run_cli(migration::Migrator)`；承 `rev5:main.rs` 形、`rev4:001-compose-stack` 契約引用帶前綴）、`entity/src/lib.rs`（15 `pub mod`；doc：欄序權威＝`specs/001-schema-baseline/data-model.md` §2、rename map＝rev5 史料（§3）、entity-drift 閘對其餘 14 表逐欄實比、casbin_rule 雙向豁免（委派 adapter 建基底、`rev4:ADR 0015`、§7））、三 Cargo.toml、toolchain／fmt。',
  '**H. 建置**（RL-0045；host 無 toolchain；一律容器內 serial）：`docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps --entrypoint cargo migrate build --workspace`（`--no-deps` 免起 postgres；容器 `/app`＝bind mount `./rust-api`、target 與 registry 走 named volume；crates.io 自容器可達、registry 卷已預熱 rev5 依賴集，仍會下載 async-trait 0.1.92）。★冷編可能超過單一 Bash 命令 600 秒上限：長命令一律 `run_in_background`＋log 檔、再以 `until` 迴圈輪詢 log 尾（每次 ≤ 500 秒）；★drvfs：跑過 docker 命令後，下一個命令開頭先 `cd -- "$PWD"`（getcwd ENOENT、CLAUDE.md §3）。完工前 `… --entrypoint cargo migrate fmt --all`（★fmt 後 17 檔 parity **必須仍零輸出**——rev5 存量已以同設定 fmt；若 fmt 動了 17 檔任一＝停手回報 `blocked`、不得「修」parity）。`Cargo.lock` 由 build 產於 `rust-api/`、入版控（不進 .gitignore）；預期與 `rev5:Cargo.lock` 差異＝`async-trait` 0.1.92（rev5 0.1.89）＋rev5 server 專屬條目缺席。',
  '**I. dev stack 重放**（T017、quickstart B；rev6 stack＝compose project `rev6-admin`、埠 3xxxx；與 rev5 stack（2xxxx）併行屬預期）：`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait postgres` → 先記 migrate 前表數 → `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm migrate`（dev override entrypoint＝`cargo run --bin migration`、command `up`；DSN 自 `/run/secrets/database_url`）→ 斷言：`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres psql -U soybean -d soybean_admin_rust -qAt -c "select version from seaql_migrations order by version"` 恰兩列 `m0001_baseline_schema`／`m0002_baseline_seeds`；`… -c "show timezone"`＝`UTC`；`… -c "select count(*) from information_schema.tables where table_schema=\'public\'"`＝16（15 表＋seaql_migrations）；`… -c "select count(*) from sys_user"`＝3。★rev6 psql 絕不指 rev5 庫（25432）；不 `down -v`。',
  '**J. 基線現況**：rust-api worktree 零 rust 碼（HEAD 512024e）；外層工作樹乾淨（Task 0 commit 07c0407）。',
  '',
  '=== rev6 拍板差異點（★不得帶回 rev5 形）===',
  '· `tokio = "1.53.1"`（非 rev5 manifest 的 `"1.52.3"` 下界）；`async-trait = "0.1.92"`（非 0.1.89）。',
  '· members 不含 server；`[workspace.dependencies]` 不含 rev5 的 auth／web／obs 依賴群（argon2／axum／redis／metrics／…）。',
  '· 檔名四碼 `m0001`／`m0002`（ADR-00008）；`seaql_migrations` 記錄名隨檔名、與 rev5 不同屬設計。',
  '· adapter 假 DSN 執行期串接（rev5 為字面、靠 allowlist）。',
  '· 註解：rev5 施工史（transcribe、seed-decision、clarify Q、T 編號）一律改成承襲語境＋`rev5:` 前綴；rev6 T 編號不進碼註解。',
].join('\n')

const IMPL_STAGES = [
  {
    label: 'u1:implementer-1-inherit',
    phase: 'Impl1',
    prompt: function (reports) {
      return [
        '你是 ' + FEATURE + ' 之 **U1 執行單元**的 **implementer-1（落檔＋建置）**。本單元分兩支 serial implementer，你做前半：**T003～T010、T014～T016**。',
        '',
        CONTEXT,
        '',
        '=== 你的交付（依序；每階段跑一次自驗再進下一階段、RL-0066）===',
        '',
        '【一】骨架（T003／T004／T005）：`rust-api/Cargo.toml`（事實接地 A；每支依賴一句 rev6 語境理由：版本三源、default-features 理由）、`rust-toolchain.toml`、`rustfmt.toml`（C）、`migration/Cargo.toml`、`entity/Cargo.toml`（B）。',
        '【二】adapter（T006）：整檔拷貝 `../fork260509-rev5/rust-api/sea-orm-adapter/` 十檔（Cargo.toml＋src 5＋examples 4）→ `rust-api/sea-orm-adapter/`；註解四型失效引用 rev6 化（F 之 adapter 條）；`src/adapter.rs` 假 DSN 改執行期串接（唯一程式面改動）；`betterleaks dir rust-api --config .gitleaks.toml --redact --exit-code 2` 零命中（rc 0）。',
        '【三】entity（T008／T009）：`cp` rev5 15 檔 → `rust-api/entity/src/`；逐檔只改註解（F 之 entity 條＋自己 grep）；自寫 `entity/src/lib.rs`（G）。',
        '【四】migration（T007／T014／T015）：`cp` rev5 `m001_baseline_schema.rs`→`m0001_baseline_schema.rs`、`m002_baseline_seeds.rs`→`m0002_baseline_seeds.rs`；逐檔只改註解（F 之 rev5:m001／rev5:m002 條）；自寫 `lib.rs`／`main.rs`（G）。',
        '【五】容器內 build＋fmt＋lock（T010）：事實接地 H——`cargo build --workspace` 綠（0 error；warning 數記 report）→ `cargo fmt --all` → 再 `cargo build --workspace --locked` 綠；`Cargo.lock` 在場、`grep -A1 \'name = "async-trait"\' rust-api/Cargo.lock` 得 0.1.92；`grep -c \'name = "argon2"\' rust-api/Cargo.lock`＝0。',
        '【六】parity（T016）：事實接地 E 對 17 檔逐檔跑、全零輸出；裸編號自掃（F 兩式 regex 對 `rust-api/` 零命中）；`git -C ../fork260509-rev5/rust-api status --porcelain` 為空；`git -C rust-api status --porcelain` 列出的檔集＝允許清單（逐行貼進 report）。',
        '',
        '=== 完工前自驗（逐項實跑、實際輸出摘要寫進 report）===',
        '1. 17 檔 parity：逐檔 rc 與總數（17/17 OK）',
        '2. 容器內 `cargo build --workspace --locked` 尾 3 行＋warning 計數；`cargo fmt --all --check` 零輸出',
        '3. `betterleaks dir rust-api --config .gitleaks.toml --redact --exit-code 2` rc 0',
        '4. 裸編號兩式 grep 零命中；rev5 樹 `status --porcelain` 空',
        '5. `git -C rust-api status --porcelain` 全文',
        '',
        RULES,
        '',
        ALLOWED_BLOCK,
        '',
        '=== 回傳 ===',
        '以 StructuredOutput 回 `{status, report, filesChanged, escalations?, rejectedFindings?}`。',
        '★`report` 會**原文轉交 implementer-2**（它做 T017 重放、T022 註解改寫清單機器對賬、T024 閘證據）——請寫清：①逐檔「原文→rev6 文」的註解改寫清單草稿（17 檔＋adapter；通用同文者免列；按檔分節）②build／fmt／lock／parity／betterleaks 的實際輸出摘要③你判斷仍有疑慮之處（如某句是否算 rev5 語境事實）。',
      ].join('\n')
    },
  },
  {
    label: 'u1:implementer-2-replay',
    phase: 'Impl2',
    prompt: function (reports) {
      return [
        '你是 ' + FEATURE + ' 之 **U1 執行單元**的 **implementer-2（重放＋證據）**。前一支已完成 T003～T010、T014～T016（骨架、17 檔、adapter、build、parity），你做 **T017、T022、T024**＋獨立復驗。',
        '',
        CONTEXT,
        '',
        '=== ★implementer-1 的交付報告（原文）===',
        reports[0],
        '★以上為自陳，**不要照單全收**；檔集、parity、build 以你自己實跑為準，不符就在 report 指出並（在允許清單內）修正。',
        '',
        '=== 你的交付 ===',
        '',
        '【T017】dev stack 重放：事實接地 I 逐步——`up -d --wait postgres` → 記 migrate 前 `information_schema.tables`（public）表數 → `run --rm migrate` → 四項斷言（seaql_migrations 恰兩列四碼名／timezone UTC／表數 16／sys_user 3 列）；★若 migrate 前庫內已有 `seaql_migrations` 或其它表＝非乾淨 dev 庫：不擅自 `down -v`、以 `done_with_escalation` 帶 escalations 回報並照常完成其餘項。migrate 全文輸出尾 10 行寫進 report。',
        '【T022】註解改寫清單機器對賬：對 17 檔＋adapter 六檔逐檔 `diff <(grep -nE \'^[[:space:]]*//\' <rev5 檔>) <(grep -nE \'^[[:space:]]*//\' <rev6 檔>)`（註解行差異＝改寫面）；比對 implementer-1 的草稿清單、補漏、剔除通用同文；逐檔核四型失效引用是否**全數**改妥（F 條＋自己 grep：`grep -rnE \'(^|[^:A-Za-z0-9])(rev[1-5])[^:0-9]\' rust-api --include=*.rs --include=*.toml` 逐行判是否為需前綴的編號引用、以及「seed-decision」「transcribe」「T0[0-9]{2}」「clarify Q」「research R[0-9]」殘留）；漏改者在允許清單內自行改妥（只動註解行）、改後重跑 parity。產出**最終清單**（按檔分節、每項「原文→rev6 文」、通用同文免列）——主線將其落 rust-api commit 訊息與 ADR-00010 證據段。',
        '【T024】機器閘證據：`python3 tools/docsync lint`（外層；★GT-05 子庫面掃 HEAD、本單元未 commit＝不會看到新檔，故另以 F 兩式 regex `grep -rnE` 對 `rust-api/` 自掃、零命中）；`betterleaks dir rust-api --config .gitleaks.toml --redact --exit-code 2` rc 0；`betterleaks git --config .gitleaks.toml --redact --exit-code 2`（外層全史）rc 0；三者輸出尾行寫進 report。',
        '【復驗】獨立重跑事實接地 E 的 17 檔 parity（全零輸出）；容器內 `cargo build --workspace --locked` 綠（lock 穩定＝零改動）；`cargo fmt --all --check` 零輸出；`git -C ../fork260509-rev5/rust-api status --porcelain` 空；`git -C rust-api status --porcelain` 檔集＝允許清單、外層 `git status --porcelain` 只有 ` M rust-api`。',
        '',
        '=== 完工前自驗（逐項實跑、實際輸出寫進 report）===',
        '1. T017 四項斷言的 psql 實際輸出',
        '2. T022 最終清單（完整、可直接貼進 commit 訊息）',
        '3. T024 三項 rc 與尾行',
        '4. 復驗四項',
        '',
        RULES,
        '',
        ALLOWED_BLOCK,
        '',
        '=== 回傳 ===',
        '以 StructuredOutput 回 `{status, report, filesChanged, escalations?, rejectedFindings?}`。`filesChanged` 據實填你本輪實際寫入的檔（只做對賬與重放而零改動＝空陣列，屬正常）。',
      ].join('\n')
    },
  },
]

const SPEC_REVIEW_PROMPT = [
  '你是 ' + FEATURE + ' 之 **U1 執行單元**的**規格對照審查員**。',
  '',
  CONTEXT,
  '',
  '=== 審查面（逐條驗；★自行讀碼／跑唯讀命令取證，不採信回報）===',
  '1. **檔集恰合**：`git -C rust-api status --porcelain` 所列 ＝ 允許清單七項（含 `Cargo.lock`）、無多無少；`.gitignore`／`LICENSE`／`x_fork.branch-origin.md` 未動；外層 `git status --porcelain` 只有 ` M rust-api`（`.gitleaks.toml`、docs、tools 零改動）。',
  '2. **FR-001／SC-001 逐位元**：親跑事實接地 E 對 17 檔（m0001／m0002＋15 entity）——全零輸出？（★這是本單元的硬門檻）',
  '3. **FR-004 骨架**：`Cargo.toml` members 恰三、resolver 2、edition 2024、`[workspace.dependencies]` **恰五支**且版本／`default-features` 逐字＝事實接地 A；`migration/Cargo.toml`／`entity/Cargo.toml` features 逐字＝B；`rust-toolchain.toml` 1.96.1；`rustfmt.toml` 三值＝C；無 argon2／server。',
  '4. **例外①②程式零改**：adapter 六檔（Cargo.toml＋src 5）以去註解 diff 對 rev5 同名檔——差異**恰一處**＝`adapter.rs` 假 DSN 改執行期串接、其餘零；examples 4 檔 `cmp` 全等。',
  '5. **FR-006 ②註解語意判準**：逐檔（17＋adapter 6）核四型失效引用是否全改（F 條逐項＋自己 grep：無前綴前代編號、rev5 施工史語句〔transcribe／seed-decision／clarify Q／T 編號／「rev5 dev 庫」〕、史料語意〔§3 rename map／§4 偏離〕）；rev6 自己的 T 編號／U1 是否誤入碼註解；GT-05 兩式 regex 對 `rust-api/` 零命中。',
  '6. **RL-0054 DSN**：`adapter.rs` 該處為執行期串接、非完整字面；`betterleaks dir rust-api --config .gitleaks.toml --redact --exit-code 2` 親跑 rc 0；`.gitleaks.toml` 零改動。',
  '7. **自寫件語意**：`migration/src/main.rs` 三級來源序、secret 檔讀取失敗 panic、空值／`CHANGE-ME` 拒啟、多執行緒 runtime、`run_cli`——與 `rev5:main.rs` 語意相同；`lib.rs` 兩支序正確、四碼 mod 名；`entity/src/lib.rs` 恰 15 `pub mod`（與 entity 檔集一一對應）。',
  '8. **T010 建置**：容器內 `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps --entrypoint cargo migrate build --workspace --locked` 綠（★`--locked` 才唯讀：lock 若需變動會直接錯、不會寫檔）；`Cargo.lock` 在場、async-trait 0.1.92、零 argon2／openssl 條目（`grep -c \'name = "openssl\' rust-api/Cargo.lock`＝0、rustls 路線）。',
  '9. **T017 重放**：親跑事實接地 I 的四條 psql 唯讀查詢（不跑 migrate、不改庫）：兩列四碼名／UTC／16 表／sys_user 3 列。',
  '10. **T022 清單**：implementer-2 report 的最終清單是否與你在第 5 項看到的改寫面一致（漏列＝blocker、附檔與原文）。',
  '11. **T024 證據**：`python3 tools/docsync lint` 親跑 0 錯（GT-05 子庫面掃 HEAD、本單元未 commit＝預期看不到新檔，非缺陷）；betterleaks dir／git 皆 rc 0。',
  '12. **rev5 唯讀**：`git -C ../fork260509-rev5/rust-api status --porcelain` 空；`git -C ../fork260509-rev5 status --porcelain --untracked-files=no` 空。',
  '13. **射程越界**：逐檔 `git -C rust-api diff`／新檔內容看實際改動面（**不看 escalations 欄下結論**）；17 檔是否有非註解行改動（parity 已證、仍逐檔抽查 `git diff --stat` 形）。',
  '',
  '=== 不可違反項 ===',
  '★你是**審查員：只讀不寫**——絕不修改 repo 內任何檔案；findings 只放回傳訊息。可跑唯讀命令取證：`cargo build … --locked`（不寫 lock、target 在 named volume）、`cargo fmt --all --check`（★帶 `--check` 才唯讀）、psql 唯讀查詢；**不得**跑 `migrate`、`cargo fmt` 不帶 `--check`、任何 `down`。',
  '★一切書面產物一律 **zh-TW**。★絕不 push／merge／commit。★絕不寫入 `../fork260509-rev5/`。★drvfs：docker 命令後下一命令先 `cd -- "$PWD"`。',
  '★blocker 的 `summary` 是結構化比較鍵（跨輪次勿改寫措辭）。★只報真缺陷；風格偏好放 `notes`。',
  '★**勿誤報**：`seaql_migrations` 記錄名與 rev5 不同（四碼）屬設計；`Cargo.lock` 相對 rev5 缺 server 專屬條目、async-trait 0.1.92 屬拍板；rev6 lint 對子庫掃 HEAD 看不到未 commit 檔屬機制、非缺陷；通用註解與 rev5 同文屬允許（語意判準、非逐行零同文）；examples 四檔零註解、原樣即正確；`cargo build` warning 非 blocker（記 notes）。',
  '',
  '=== 回傳 ===',
  '以 StructuredOutput 回 `{agentStatus, blockers, notes}`。★`agentStatus` 只表你自己能否完成審查。',
].join('\n')

const QUALITY_REVIEW_PROMPT = [
  '你是 ' + FEATURE + ' 之 **U1 執行單元**的**碼品質審查員**。前一輪規格對照審查已收斂，本輪看品質與可維護性。',
  '',
  CONTEXT,
  '',
  '=== 審查面（逐條驗）===',
  '1. **註解品質（17 檔＋adapter＋自寫件）**：rev6 語境是否自洽（讀者是 rev6 維護者、不需 rev5 歷史也看得懂）；zh-TW；`rev5:`／`rev4:`／`rev2:` 前綴形是否一致；有無「rev5 施工史」殘留（transcribe、seed-decision、clarify Q、T 編號、U 編號、「本刀」）；有無把 rev6 的刀內程序（T003、U1）寫進碼註解；史料語意（§3 rename map／§4 偏離）是否標明為 rev5 對 rev4 的定稿史。',
  '2. **自寫件重打字品質**：`main.rs`（錯誤訊息 zh-TW 且指名來源；`unsafe` 的 SAFETY 註解保留理由；無死碼）、`migration/src/lib.rs`／`entity/src/lib.rs`（doc 準確：entity-drift 閘與凍結 fixtures 於本刀後續單元落地——描述為契約可、寫成「已就位」的假述不可〔RL-0015〕）。',
  '3. **Cargo.toml 註解**：每支依賴一句 rationale（版本三源出處、`default-features = false` 理由）；無 rev5 的 002／003／004 刀敘事帶回；`tokio` 值註明「與 lock 同值、非下界」拍板。',
  '4. **DSN 改法**：執行期串接形是否最小改動（一行）、測試仍 `#[ignore]` 帶理由、未引入新依賴、未改測試語意。',
  '5. **fmt／build 衛生**：容器內 `cargo fmt --all --check` 零輸出；`cargo build --workspace --locked` warning 逐條列（notes）；`Cargo.lock` 無 openssl／native-tls 條目（rustls 路線）。',
  '6. **RL-0070 可見性放寬面**：本單元不應放寬任何既有可見性（全是新檔）；`entity/src/lib.rs` 的 `pub mod` 集合＝15 恰合、無多餘 `pub use`。',
  '7. **rev5 參照紀律**：註解提及前代編號是否全帶前綴；有無整段照抄 rev5 施工敘事的痕跡（例外②允許程式同文、註解須語意 rev6）。',
  '8. **變異前提**（RL-0067）：本單元零測試面（migration 重放即整合測試）；不要求補測，但 report 若宣稱「已測」須有實跑證據。',
  '9. **未竟事項留帳**：寫進 `notes` 供主線落 BACKLOG／LESSONS（★不要自己改 BACKLOG）。',
  '',
  '=== 不可違反項 ===',
  '★你是**審查員：只讀不寫**。可跑唯讀命令取證；`cargo fmt` 務必帶 `--check`、`cargo build` 務必帶 `--locked`；不跑 migrate、不改庫。',
  '★一切書面產物一律 **zh-TW**。★絕不 push／merge／commit。★絕不寫入 `../fork260509-rev5/`。★drvfs：docker 命令後下一命令先 `cd -- "$PWD"`。',
  '★blocker 的 `summary` 是結構化比較鍵。★只報真缺陷；風格偏好放 `notes`。',
  '★**勿誤報**：通用註解與 rev5 同文屬允許；examples 四檔零註解屬正確；`Cargo.lock` 差異屬拍板；build warning 非 blocker。',
  '',
  '=== 回傳 ===',
  '以 StructuredOutput 回 `{agentStatus, blockers, notes}`。`agentStatus` 只表你自己能否完成審查。',
].join('\n')

const FIX_SELFCHECK = '容器內 serial `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps --entrypoint cargo migrate build --workspace --locked` 綠＋`… fmt --all --check` 零輸出＋事實接地 E 之 17 檔 parity 全零輸出＋`betterleaks dir rust-api --config .gitleaks.toml --redact --exit-code 2` rc 0＋GT-05 兩式 regex 自掃零命中'

// ★本段引用模板常數：UNIT（執行單元標籤，如 U2）、FEATURE（該刀 feature 分支長名）、CONTEXT、ALLOWED_BLOCK（_context／_allowed 段）、
//   FIX_SELFCHECK（fix 修完必跑的自驗命令一句；_prompts 段）——組裝時定義，缺之即 ReferenceError；
//   RULES_REVIEW／RULES_FIX 由 _sk_rules.js（generate 產物）供：review prompt 一律烤 RULES_REVIEW、fix prompt 一律烤 RULES_FIX（R1-080）；
//   DEEP_THINK 由 _sk_head.js 供、烤在 review／fix prompt 首行（user 拍板 2026-09-04）。
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
    DEEP_THINK,
    '你是 ' + FEATURE + ' 之 **' + UNIT + ' 執行單元**的 **fix agent**（第 ' + roundNo + ' 輪修復）。',
    '',
    CONTEXT,
    '',
    '=== 本輪待處理 findings ===',
    items.join('\n'),
    '',
    '=== 處置紀律 ===',
    '· 逐條判斷 finding 是否**真的成立**——審查員也會出錯（★審查 prompt 末段「勿誤報」所列項是最常見的誤報源）。成立就修；**不成立就據實駁回**，放進 `rejectedFindings`（附 `file`／`summary`〔逐字沿用上面那句摘要〕／`why`）。',
    '· ★不要為了讓審查通過而做「表面修改」——那會讓下一輪重報同一問題、觸發不收斂判定。',
    '· ★**補守門一律做變異測試**：把被指的那行改壞→跑測確認會紅→還原。不做這步，補的就是另一個裝飾性守門。',
    '· 修改一律限在允許清單內。清單外需要動＝**絕不擅改**，依 status 分值升級。',
    '· 修完 MUST 重跑自驗（' + FIX_SELFCHECK + '），實際輸出摘要寫進 report。',
    '',
    RULES_FIX,
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
      [DEEP_THINK, head, '', reviewPrompt, '', RULES_REVIEW, rejectedBlock(rejected)].join('\n'),
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

// ─────────────────── 主流程（serial；單一骨架：implementer 支數＝IMPLEMENTERS、逐支 prompt 由 _prompts 段的 IMPL_STAGES 供） ───────────────────
// IMPL_STAGES＝[{ label, phase, prompt(reports) }, …]：label 必含 implementer 字樣（harness 樁與看門狗冒煙皆以此辨識）；
//   prompt 收前面各支的 report 陣列（首支得空陣列、第 i 支得 i−1 份、原文轉交）；支數與 IMPLEMENTERS 自我斷言（保險絲推導同源、RL-0062）。
//   另引用 START_LOG（_vars 段）、SPEC_REVIEW_PROMPT／QUALITY_REVIEW_PROMPT／FIX_SELFCHECK（_prompts 段）。
if (!Array.isArray(IMPL_STAGES) || IMPL_STAGES.length !== IMPLEMENTERS) {
  throw new Error('防呆③：IMPL_STAGES 支數（' + (Array.isArray(IMPL_STAGES) ? IMPL_STAGES.length : '非陣列') + '）≠ IMPLEMENTERS（' + IMPLEMENTERS + '）——保險絲推導失準、零派發')
}
IMPL_STAGES.forEach(function (st, i) {
  if (!st || typeof st.label !== 'string' || !st.label.includes('implementer') || typeof st.phase !== 'string' || typeof st.prompt !== 'function') {
    throw new Error('防呆②：IMPL_STAGES[' + i + '] 須含 label（含 implementer 字樣）／phase／prompt(reports) 函式')
  }
})
if (typeof FIX_SELFCHECK !== 'string' || FIX_SELFCHECK.length < 8) {
  throw new Error('防呆②：FIX_SELFCHECK（fix 修完必跑的自驗命令一句）須由 _prompts 段定義')
}

const impls = []
const reportsSoFar = function () { return impls.map(function (x) { return x.report }) }
for (let i = 0; i < IMPL_STAGES.length; i++) {
  const st = IMPL_STAGES[i]
  const who = 'implementer-' + (i + 1)
  phase(st.phase)
  if (i === 0) log(START_LOG)
  const r = await spawn(st.prompt(reportsSoFar()), Object.assign({ label: st.label, phase: st.phase, schema: WORK_SCHEMA }, IMPL_OPTS))
  if (!r) return { unit: UNIT, status: 'failed', stage: st.phase, reason: who + ' 回傳 null（終止型故障）', implReports: reportsSoFar(), agentsSpawned: spawned }
  if (r.status === 'blocked') {
    return { unit: UNIT, status: 'blocked', stage: st.phase, reason: who + ' 受阻', report: r.report, escalations: r.escalations || [], implReports: reportsSoFar(), agentsSpawned: spawned }
  }
  impls.push(r)
  log(who + ' 完成（status=' + r.status + '、改檔 ' + (r.filesChanged || []).length + ' 支）' + (i + 1 < IMPL_STAGES.length ? '→ 進下一支 implementer' : '→ 進規格對照審查'))
}

phase('SpecReview')
const c1 = await cycle('SpecReview', SPEC_REVIEW_PROMPT, 'spec')
if (!c1.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'SpecReview', reason: c1.reason, blockers: c1.blockers, rejected: c1.rejected, escalations: c1.escalations || [], implReports: reportsSoFar(), agentsSpawned: spawned }
}
log('規格對照審查收斂（' + c1.rounds + ' 輪）→ 進碼品質審查')

phase('CodeQualityReview')
const c2 = await cycle('CodeQualityReview', QUALITY_REVIEW_PROMPT, 'quality')
if (!c2.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'CodeQualityReview', reason: c2.reason, blockers: c2.blockers, rejected: c2.rejected, escalations: c2.escalations || [], implReports: reportsSoFar(), specNotes: c1.notes, agentsSpawned: spawned }
}

return {
  unit: UNIT,
  status: 'ok',
  implStatuses: impls.map(function (x) { return x.status }),
  implReports: reportsSoFar(),
  filesChanged: impls.reduce(function (a, x) { return a.concat(x.filesChanged || []) }, []),
  escalations: impls.reduce(function (a, x) { return a.concat(x.escalations || []) }, []),
  specReviewRounds: c1.rounds,
  specReviewNotes: c1.notes,
  qualityReviewRounds: c2.rounds,
  qualityReviewNotes: c2.notes,
  agentsSpawned: spawned,
}
