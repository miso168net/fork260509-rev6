"""tools/orchestration/EXAMPLE-review-verify-unitdef.py — review 形單元定義範例（BL-00006；verify 階段＝主線合併去重後的批次兩鏡三態＋探針 grader→refuter＋完整性 critic）。
組裝：python3 tools/orchestration/assemble.py tools/orchestration/EXAMPLE-review-verify-unitdef.py tmp/<out>.mjs
真跑時 BATCHES.text／PROBES.answers／CRITIC.prior 由主線自探索 run 的 journal 結果渲染（每筆 finding 首行「■ <id>｜<severity>｜<category>」、其餘欄縮排兩格）；
本檔的兩批四筆與一份作答為形制樣本（harness-review 九案據此乾跑），發射前照抄到 tmp/ 換成真資料並改 SMOKE。"""
MODE = 'review'
SMOKE = 'r-orch-verify-9e3d'

VARS = r"""export const meta = {
  name: 'example-review-verify',
  description: 'review 形範例（verify）：兩批 findings×R-real／R-decided 兩鏡三態＋一支探針 grader→refuter＋完整性 critic；唯讀、zh-TW',
  phases: [
    { title: '驗證', detail: '每批 R-real＋R-decided 兩鏡' },
    { title: '探針評分', detail: 'grader→R-decided（refuter）' },
    { title: 'critic', detail: '完整性：漏讀檔／未覆蓋宣稱／該補的 lens' },
  ],
}

const UNIT = 'R-EXAMPLE'
const FEATURE = '000-rN-orchestration-smoke'
const SMOKE = 'r-orch-verify-9e3d'
const REVIEW_STAGE = 'verify'
const FINDING_CATEGORIES = ['檢索性', '活書事實', '時態鏡像', '閘覆蓋缺口', '規則承載缺口', '其他']
const START_LOG = 'review 範例（verify）起手：兩批四筆 findings 進兩鏡三態、一支探針作答進 grader→refuter、末支 critic 找漏'"""

PLAN = r"""const BATCHES = [
  {
    batch: 'G1',
    ids: ['R-001', 'R-002'],
    text: [
      '■ R-001｜major｜檢索性',
      '  file: README.md',
      '  locator: 查詢表「編排 agent 用哪個模型」列',
      '  summary: 查詢表只指 agents.md、未指 tools/orchestration/README.md 的組裝法',
      '  evidence command: grep -n "編排 agent 用哪個模型" README.md',
      '  evidence output: | 編排 agent 用哪個模型 | `docs/generated/reference/agents.md`（…） |',
      '  proposed: 修｜查詢表加一列「怎麼組一支 Workflow script」指 tools/orchestration/README.md',
      '  confidence: 0.8',
      '',
      '■ R-002｜minor｜活書事實',
      '  file: docs/arc42/05-building-block-view.md',
      '  locator: §5.1 白盒表 tools/ 列',
      '  summary: tools/ 列描述 orchestration 只提 _sk_*.js 與 harness-test、未提 review 形與組裝器',
      '  evidence command: grep -n "orchestration" docs/arc42/05-building-block-view.md',
      '  evidence output: | `tools/` | `docsync`（…）、`orchestration/`（`_sk_*.js` 單一骨架…）',
      '  proposed: 修｜同批補一句 review 形與 assemble.py',
      '  confidence: 0.6',
    ].join('\n'),
  },
  {
    batch: 'G2',
    ids: ['R-003', 'R-004'],
    text: [
      '■ R-003｜blocker｜規則承載缺口',
      '  file: tools/orchestration/_sk_head.js',
      '  locator: guard()',
      '  summary: RL-0058 要求規則塊整塊烤入每支 prompt，guard 未斷言 RULES-VERSION 字串',
      '  evidence command: grep -n "RULES-VERSION" tools/orchestration/_sk_head.js',
      '  evidence output: （命中或零命中）',
      '  proposed: 修｜guard 加一行正則斷言',
      '  confidence: 0.7',
      '',
      '■ R-004｜minor｜其他',
      '  file: docs/ops/RUNBOOK.md',
      '  locator: §12 工具鏈速查表',
      '  summary: 速查表缺 assemble.py 與 harness-review.mjs 兩列',
      '  evidence command: grep -n "orchestration" docs/ops/RUNBOOK.md',
      '  evidence output: （列出現況兩列）',
      '  proposed: 修｜補兩列',
      '  confidence: 0.9',
    ].join('\n'),
  },
]
const PROBES = [
  {
    key: 'P1',
    answers: [
      '=== 探針 P1 作答紀錄（overall_notes：三題皆自 README 查詢表起手）===',
      'Q1: 要組一支 review 形的 Workflow script，該從哪個檔起手、用什麼命令組裝與自測？',
      '  answer: tools/orchestration/README.md 組裝法；python3 tools/orchestration/assemble.py <unitdef.py> <out.mjs>；harness-review.mjs',
      '  path: ["README.md", "tools/orchestration/README.md"]',
      '  hops: 2｜found: true｜confidence: 0.9',
      '  ambiguity: ',
      '  dead_ends: []',
      '  suggestion: README 查詢表可直接指組裝法',
    ].join('\n'),
  },
]
const CRITIC = {
  scope: '範圍＝tools/orchestration/**、README.md、docs/ops/RUNBOOK.md §12、docs/ops/RULES.md、CLAUDE.md §2、docs/generated/reference/agents.md、docs/process/P-E2-agent-registry.md。',
  prior: '=== 探索 run 讀檔聯集（樣本）===\nREADME.md、docs/ops/RUNBOOK.md、tools/orchestration/README.md、tools/orchestration/_sk_head.js、tools/orchestration/_sk_review.js',
}"""

CONTEXT = r"""const CONTEXT = [
  '=== 身分與對象 ===',
  '工作區＝rev6-admin 傘狀 workspace（repo 根＝`CLAUDE.md` 所在；先讀 §1／§3／§6／§7）。本輪＝' + FEATURE + '（review 形範例、verify 階段）；對象＝當前工作樹 HEAD（`git rev-parse --short HEAD` 自取、勿假設任何後續改動）；前代對照樹＝../fork260509-rev5/（唯讀）。',
  '範圍＝tools/orchestration/**、README.md、docs/ops/RUNBOOK.md §12、docs/ops/RULES.md、CLAUDE.md §2、docs/generated/reference/agents.md、docs/process/P-E2-agent-registry.md。',
  '冒煙 token＝' + SMOKE + '。一切書面產物（findings、verdicts、notes、任何解釋）一律 zh-TW；識別字、路徑、命令、程式碼保留原形。',
].join('\n')
const DECISIONS_BLOCK = [
  '拍板紀錄去處：.specify/memory/constitution.md；docs/arc42/decisions/（ADR-00004 六件套、ADR-00013 fix 清單外升級不終止 run）；docs/ops/RULES.md（表＋名詞段）；docs/ops/BACKLOG.md（BL-00006 review 骨架入庫、BL-00007 檢索性第四指標）；docs/generated/GATES.md。',
].join('\n')"""

RESIDUE = ['U0 執行單元', 'u0-govgate-7c2e']
