"""tools/orchestration/EXAMPLE-tdd-unitdef.py — TDD 形單元定義範例（BL-00006；單 implementer→規格對照審查→fix 迴圈→碼品質審查→fix 迴圈）。
組裝：python3 tools/orchestration/assemble.py tools/orchestration/EXAMPLE-tdd-unitdef.py tmp/<out>.mjs
發射前照抄到 tmp/<刀>-uN.py，改 UNIT／FEATURE／SMOKE（模組層與 VARS 內兩處同值、組裝器對賬）／ALLOWED／CONTEXT／PROMPTS（尖括號＝佔位、須換成刀事實）；
規則塊由 _sk_rules.js 供、fix prompt 與 cycle 由骨架供；本檔只寫刀事實與任務句。IMPLEMENTERS=0 即續跑形（RL-0010：IMPL_STAGES=[]、CONTEXT 寫已完成結論與勿重報清單）。"""
MODE = 'tdd'
SMOKE = 't-example-unit-5c1e'

VARS = r"""export const meta = {
  name: 'example-tdd-unit',
  description: 'TDD 形範例：單 implementer（TDD、容器內 serial）→規格對照審查→fix 迴圈→碼品質審查→fix 迴圈；zh-TW',
  phases: [
    { title: 'Impl1', detail: 'implementer：<T 編號> 先紅後綠、容器內 serial' },
    { title: 'SpecReview', detail: '規格對照審查＋fix 迴圈' },
    { title: 'CodeQualityReview', detail: '碼品質審查＋fix 迴圈' },
  ],
}

const UNIT = 'U-EXAMPLE'
const FEATURE = '<NNN>-<feature-name>'
const IMPLEMENTERS = 1
const SMOKE = 't-example-unit-5c1e'
const START_LOG = 'U-EXAMPLE 起手：implementer 依 tasks <T 編號> 先紅後綠'"""

ALLOWED = r"""const ALLOWED_BLOCK = [
  '★允許檔案清單（本單元唯一可寫面；路徑相對 repo 根；RL-0014 答「碰得到什麼」、寧可多列——含連動釘值測所在檔）：',
  '  1. `<子庫>/<路徑>`——★**只准** <限定面：哪些函式／測試模組可動>；其餘零改',
  '  2. `tmp/<刀>-uN-*`（session 工作檔、gitignored）',
  '★通用條款（RL-0015 能力名判、LL-00008）：前單元以他單元之名寫的預告句（「隨 <刀> Un…」「尚無消費者」等），若其能力於本單元落地，該句改現在式屬本單元授權面、不受限定式項限制——改後在 report 指明檔:行與新句；不得藉此改動同檔其他內容。',
  '★★限定式項的分值語意（rev5:L-075）：帶「只准」＝改動面級授權——限定外改動＝視同清單外、MUST 走 `done_with_escalation`＋`escalations` 逐條＋`escalatedFindings` 結構化指名，不得因「檔在清單內」就回 `status: ok`。',
  '★清單外明確不得動：`docs/**`（主線帳本）、`tools/**`、`.githooks/**`、`../fork260509-rev5/**`（絕不寫入）；★agent 絕不 commit、絕不 `--no-verify`。',
].join('\n')"""

CONTEXT = r"""const CONTEXT = [
  '=== 專案與本單元定位 ===',
  '工作區＝rev6-admin 傘狀 workspace（repo 根＝`CLAUDE.md` 所在；★先讀 §1／§3／§6／§7）。本刀＝`' + FEATURE + '`。本執行單元＝**' + UNIT + '**＝tasks.md **<T 編號>**：<一句話目標>。冒煙 token＝' + SMOKE + '。一切書面產物一律 **zh-TW**。',
  '',
  '=== 必讀 ===',
  '1. `specs/' + FEATURE + '/{spec,plan,tasks,data-model}.md`（本單元涵蓋的 T 逐字＝驗收條文）；contracts；quickstart 對應節。',
  '2. rev6 現況（★開工先 `git -C <子庫> log -5` 並讀碼、不採信本段）：<既有模組／助手名冊／案冊計數>。rev5 藍本＝`../fork260509-rev5/<路徑>`（唯讀；RL-0064、RL-0065：重打字消化、拷貝禁止、註解重寫）。',
  '',
  '=== 事實接地：環境與紀律（serial）===',
  '· rust build／test 一律容器內 serial（`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo …`、DoD `--test-threads=1`）；改庫必還原（RAII 守衛）；tracked 檔不得落 `Authorization: Bearer dev-` 完整字面；★新增測試涉行程級全域狀態→連跑 ≥5 趟（LL-00009）。',
  '· 先紅後綠（RL-0066）：案先落→紅（期望值）→實作→綠；「案綠→打壞判準→紅→還原」至少一次、記 report（RL-0019 存原文寫回、cmp 全等）。',
  '· 案冊計數（模組頭註「恰 N 支」）增案同批對齊；doc 註內勿寫測試屬性字面（免污染機器計數面）。',
].join('\n')"""

PROMPTS = r"""const IMPL_STAGES = [
  {
    label: 'u-example:implementer',
    phase: 'Impl1',
    prompt: function (reports) {
      return [
        '你是 ' + FEATURE + ' 之 **' + UNIT + ' 執行單元**的 **implementer（TDD）**：**<T 編號>**。',
        '',
        CONTEXT,
        '',
        '=== 你的交付（依序；RL-0066 先紅後綠）===',
        '【零】開工：讀 tasks 條文逐字；`git -C <子庫> log -5`；讀既有助手。',
        '【一】<案集>先寫→紅→綠；打壞判準演練一次、記 report。',
        '【二】收尾：容器內 build --locked／fmt --check／test 兩次 rc 0；GT-05 自掃零裸編號；三 porcelain（子庫恰允許清單、外層空、rev5 空）。',
        '',
        '=== 完工前自驗 ===',
        '1. 先紅→綠證據；2. 打壞判準演練；3. 三 porcelain 全文；4. report 含新增案清單',
        '',
        RULES,
        '',
        ALLOWED_BLOCK,
        '',
        '=== 回傳 ===',
        '以 StructuredOutput 回 `{status, report, filesChanged, escalations?, rejectedFindings?, escalatedFindings?}`。',
      ].join('\n')
    },
  },
]

const SPEC_REVIEW_PROMPT = [
  '你是 ' + FEATURE + ' 之 **' + UNIT + ' 執行單元**的**規格對照審查員**（唯讀；容器內 cargo test 自含還原可跑；serial）。',
  '',
  CONTEXT,
  '',
  '=== 審查面（對照 tasks <T 編號> 條文、spec 場景、SC、FR、契約）===',
  '1. 檔集恰合：子庫 porcelain 恰＝允許清單；外層零改；rev5 樹 porcelain 空。',
  '2. 案集齊：逐條對照條文；每案零寫入／還原腿；純測與真 DB 案分工。',
  '3. 非 vacuous：tmp 副本變異（打在判準上）→對應案紅；還原 md5／porcelain 雙面自證（RL-0005）。',
  '4. 紀律：GT-05；rev6 語境（RL-0046 前綴）；fmt；test 兩次綠；RL-0015 預告回填。',
  '',
  '=== 不可違反項 ===',
  '★只讀不寫；探針只在 `tmp/<刀>-uN-review-*`。★zh-TW。★絕不 push／merge／commit／git add。★cargo serial。★blocker summary＝比較鍵；只報真缺陷。★勿誤報：<已拍板者非缺陷清單>。',
  '',
  '=== 回傳 ===',
  '以 StructuredOutput 回 `{agentStatus, blockers, notes}`。',
].join('\n')

const QUALITY_REVIEW_PROMPT = [
  '你是 ' + FEATURE + ' 之 **' + UNIT + ' 執行單元**的**碼品質審查員**（前輪已收斂；唯讀；serial）。',
  '',
  CONTEXT,
  '',
  '=== 審查面 ===',
  '1. 重打字與註解（rev5 出處帶 `rev5:` 前綴、裸編號＝紅）。2. 共用助手單一實作、資料驅動、訊息指名。3. 可見性放寬審查面（RL-0070）。4. 文件內鏈與案冊計數自洽（RL-0011）。5. 未竟事項留 notes。',
  '',
  '=== 不可違反項 ===',
  '★只讀不寫；探針只在 `tmp/<刀>-uN-review-*`。★zh-TW。★絕不 push／merge／commit／git add。★cargo serial。★blocker summary＝比較鍵；只報真缺陷。',
  '',
  '=== 回傳 ===',
  '以 StructuredOutput 回 `{agentStatus, blockers, notes}`。',
].join('\n')

const FIX_SELFCHECK = '容器內 `cargo build --workspace --locked`＋`cargo fmt --all --check`＋`cargo test --workspace -- --test-threads=1`（兩次）皆 rc 0；`python3 tools/docsync check`／`lint` 綠；GT-05 自掃零裸編號；三 porcelain 對賬'"""

RESIDUE = ['u6-authz-matrix', 'U6 執行單元']
