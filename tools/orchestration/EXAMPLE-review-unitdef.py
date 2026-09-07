"""tools/orchestration/EXAMPLE-review-unitdef.py — review 形單元定義範例（BL-00006；explore 階段＋inline 兩鏡＋一支冷啟動探針）。
組裝：python3 tools/orchestration/assemble.py tools/orchestration/EXAMPLE-review-unitdef.py tmp/<out>.mjs
發射前照抄到 tmp/ 改 UNIT／FEATURE／SMOKE／CONTEXT 對象與範圍；本例的 lens 任務＝「編排骨架名冊與規則承載一致性」——可原樣當每次骨架改動後的冒煙 review。
規則塊由 _sk_rules.js 供、READONLY／取證／回傳段由 _sk_review.js 供；本檔只寫刀事實（CONTEXT／DECISIONS_BLOCK）與各 lens／探針的任務句。"""
MODE = 'review'
SMOKE = 'r-orch-example-4b2c'

VARS = r"""export const meta = {
  name: 'example-review-explore',
  description: 'review 形範例：兩支探索 lens（編排骨架名冊一致性／規則×骨架承載）＋一支冷啟動探針；inline 兩鏡三態；唯讀、zh-TW',
  phases: [
    { title: '探索', detail: 'lens∥probe（唯讀）' },
    { title: '探索驗證', detail: '每支 lens 的 findings→R-real＋R-decided 兩鏡；探針→grader→refuter' },
  ],
}

const UNIT = 'R-EXAMPLE'
const FEATURE = '000-rN-orchestration-smoke'
const SMOKE = 'r-orch-example-4b2c'
const REVIEW_STAGE = 'explore'
const INLINE_VERIFY = true
const FINDING_CATEGORIES = ['檢索性', '活書事實', '時態鏡像', '閘覆蓋缺口', '規則承載缺口', '其他']
const START_LOG = 'review 範例起手：兩支 lens 探索編排骨架的名冊與規則承載、一支冷啟動探針測檢索性；findings 即刻進兩鏡三態'"""

PLAN = r"""const LENSES = [
  {
    key: 'L1',
    task: [
      '【L1 名冊一致性】對照 tools/orchestration/ 的 tracked 實檔（`git ls-files tools/orchestration`）與四處名冊：',
      '① README.md 樹的 `orchestration/` 目錄列描述；② README.md 查詢表「編排 agent 用哪個模型」列；③ docs/ops/RUNBOOK.md §12 工具鏈速查表之 node／assemble 列（用法字串須與各檔檔頭用法一致）；④ tools/orchestration/README.md 檔表。',
      '報：缺列／多列／描述失準（案數、檔名、用法、拼接序與實檔不符）。另核 docs/generated/reference/agents.md 之 *_OPTS 列與 _sk_head.js 字面是否全等（generate 產物、只讀比對、不得 generate）。',
    ].join('\n'),
  },
  {
    key: 'L2',
    task: [
      '【L2 規則×骨架承載】對照 docs/ops/RULES.md 之 RL-0018／RL-0025／RL-0058～RL-0062 與 CLAUDE.md §2「workflow script 防呆六件套」「主線看門狗」兩段，',
      '逐條在 tools/orchestration/_sk_head.js／_sk_cycle.js／_sk_review.js／harness-test.mjs／harness-review.mjs 找機器承載（guard／保險絲推導與自我斷言／收斂偵測／escalated 過濾／三態聚合／樁案）。',
      '報：「規則有、骨架無承載」或「骨架行為與規則字面相反」；有承載者不報、只在 notes 列對照表（規則→承載處）。',
    ].join('\n'),
  },
]
const PROBES = [
  {
    key: 'P1',
    task: [
      '【探針 P1｜冷啟動】你是一支只有 repo 內容、沒有任何對話脈絡的新 session（探針）。冒煙 token：r-orch-example-4b2c。一切書面產物一律 zh-TW；識別字、路徑、命令保留原形。',
      '規則：只准讀 repo（Read／Grep／Glob 與唯讀 Bash）；每題記你依序開的檔（path）與開檔次數（hops）；答不出就 found=false、寫 dead_ends；文件缺口寫 suggestion。',
      'Q1 要組一支 review 形的 Workflow script（探索 lens＋兩鏡驗證），該從 repo 哪個檔起手、用什麼命令組裝與自測？',
      'Q2 review 形各角色（lens／mirror／grader／critic）用哪個模型與 effort、真源在哪個檔？',
      'Q3 組好的 script 發射時，看門狗命令是什麼、冒煙 token 有什麼限制？',
    ].join('\n'),
  },
]"""

CONTEXT = r"""const CONTEXT = [
  '=== 身分與對象 ===',
  '工作區＝rev6-admin 傘狀 workspace（repo 根＝`CLAUDE.md` 所在；先讀 §1／§3／§6／§7）。本輪＝' + FEATURE + '（review 形範例）；對象＝當前工作樹 HEAD（`git rev-parse --short HEAD` 自取、勿假設任何後續改動）；前代對照樹＝../fork260509-rev5/（唯讀）。',
  '範圍＝tools/orchestration/**、README.md、docs/ops/RUNBOOK.md §12、docs/ops/RULES.md、CLAUDE.md §2、docs/generated/reference/agents.md、docs/process/P-E2-agent-registry.md。',
  '冒煙 token＝' + SMOKE + '。一切書面產物（findings、verdicts、notes、任何解釋）一律 zh-TW；識別字、路徑、命令、程式碼保留原形。',
].join('\n')
const DECISIONS_BLOCK = [
  '拍板紀錄去處：.specify/memory/constitution.md；docs/arc42/decisions/（ADR-00004 六件套、ADR-00013 fix 清單外升級不終止 run）；docs/ops/RULES.md（表＋名詞段）；docs/ops/BACKLOG.md（ADR-00021 檢索性第四指標；review 骨架入庫已收＝ADR-00020＋tools/orchestration/README.md）；docs/generated/GATES.md。',
].join('\n')"""

RESIDUE = ['U0 執行單元', 'u0-govgate-7c2e']
