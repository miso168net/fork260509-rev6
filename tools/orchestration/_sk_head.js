// 骨架首段（單一骨架、BL-00001 收斂；BL-00006 起兩種主流程共用同一首段）：防呆①args 斷言／②guard（長度、zh-TW、冒煙 token、規則塊版本串）／
//   ③保險絲推導＋自我斷言／④兩套 schema（WORK＝status，REVIEW＝agentStatus）。
// ★模式偵測＝看 _vars 段定義了誰：`IMPLEMENTERS`＝TDD 形（拼接 _sk_cycle＋_sk_main；0＝續跑形、只跑審查段、RL-0010）；
//   `REVIEW_STAGE`＝review 形（拼接 _sk_review：explore＝lens∥probe〔可選 INLINE_VERIFY 兩鏡〕／verify＝批×兩鏡＋探針 grader→refuter＋可選 critic）。
//   兩者互斥、皆缺即 throw；保險絲各依其結構最壞值推導（RL-0062）。
// ★SMOKE（冒煙 token；RL-0018 置於各 prompt 共用段、RL-0059 派發前斷言；★不可取字面 test＝wf-watchdog 會當自測子命令）。
if (typeof args !== 'undefined' && args !== null) {
  throw new Error('防呆①：本 script 不接受 args——一切邊界寫死於 script 常數')
}
const MODE = (typeof REVIEW_STAGE !== 'undefined') ? 'review' : 'tdd'
if (MODE === 'tdd') {
  if (typeof IMPLEMENTERS !== 'number' || !Number.isInteger(IMPLEMENTERS) || IMPLEMENTERS < 0) {
    throw new Error('防呆③：IMPLEMENTERS 須為 ≥0 的整數（0＝續跑形、只跑審查段）、由 _vars 段定義（現值 ' + String(typeof IMPLEMENTERS === 'undefined' ? 'undefined' : IMPLEMENTERS) + '）；review 形改定義 REVIEW_STAGE')
  }
} else {
  if (typeof IMPLEMENTERS !== 'undefined') {
    throw new Error('防呆③：REVIEW_STAGE 與 IMPLEMENTERS 互斥——一支 script 只走一種主流程')
  }
  if (REVIEW_STAGE !== 'explore' && REVIEW_STAGE !== 'verify') {
    throw new Error('防呆③：REVIEW_STAGE 須為 explore 或 verify（現值 ' + String(REVIEW_STAGE) + '）')
  }
}
if (typeof SMOKE !== 'string' || SMOKE.length < 6 || SMOKE === 'test') {
  throw new Error('防呆②：SMOKE 冒煙 token 須為 ≥6 字元字串且不可取字面 test、由 _vars 段定義（現值 ' + String(SMOKE) + '）')
}
// ★_vars 段三常數（兩形共用；BL-00039①：原僅 review 形於其主流程段自驗、TDD 形零斷言。空值不會被 guard 攔下——
//   prompt 其餘段落已足 400 字元且含 zh-TW／冒煙 token／RULES-VERSION，身分句只是少了單元名，靜默失真）。
//   ★逐個以 typeof 短路取值：常數名整個打錯時直接引用會 ReferenceError，訊息就不是防呆②了。
;[
  ['UNIT', typeof UNIT === 'undefined' ? undefined : UNIT],
  ['FEATURE', typeof FEATURE === 'undefined' ? undefined : FEATURE],
  ['START_LOG', typeof START_LOG === 'undefined' ? undefined : START_LOG],
].forEach(function (kv) {
  if (typeof kv[1] !== 'string' || kv[1].length === 0) {
    throw new Error('防呆②：' + kv[0] + ' 須為非空字串、由 _vars 段定義（現值 ' + String(kv[1]) + '）')
  }
})

const MAX_FIX_ROUNDS = 3
const CYCLES = 2
const MAX_AGENTS_PER_RUN = 24 // review 形每 run 上限：wf-watchdog 對進行中 run 恆用 25 支 runaway 底線（000-r1 實證、RL-0062）
let WORST
let AGENT_FUSE
if (MODE === 'tdd') {
  WORST = IMPLEMENTERS + CYCLES * (2 * MAX_FIX_ROUNDS + 1)
  AGENT_FUSE = Math.min(20, WORST + 1)
} else {
  // review 形結構最壞值由 _plan 段常數推導（explore：lens＋probe、INLINE_VERIFY 再＋2×lens 兩鏡＋2×probe〔grader＋refuter〕；verify：2×批＋2×探針＋critic 一支）。
  const _len = function (x) { return Array.isArray(x) ? x.length : 0 }
  const nL = typeof LENSES === 'undefined' ? 0 : _len(LENSES)
  const nP = typeof PROBES === 'undefined' ? 0 : _len(PROBES)
  const nB = typeof BATCHES === 'undefined' ? 0 : _len(BATCHES)
  const inline = typeof INLINE_VERIFY !== 'undefined' && INLINE_VERIFY === true
  const hasCritic = typeof CRITIC !== 'undefined' && CRITIC !== null
  WORST = REVIEW_STAGE === 'explore' ? (nL + nP + (inline ? 2 * nL + 2 * nP : 0)) : (2 * nB + 2 * nP + (hasCritic ? 1 : 0))
  if (WORST < 1) throw new Error('防呆③：review 形結構最壞值為 0——_plan 段零 lens／批（零派發即無事可做）')
  AGENT_FUSE = WORST + 1
  if (AGENT_FUSE > MAX_AGENTS_PER_RUN) {
    throw new Error('防呆③：保險絲 ' + AGENT_FUSE + ' 超過每 run 上限 ' + MAX_AGENTS_PER_RUN + '（結構最壞 ' + WORST + '）——分批成多支 run')
  }
}
if (AGENT_FUSE < WORST) {
  throw new Error('防呆③：保險絲 ' + AGENT_FUSE + ' 低於結構最壞值 ' + WORST)
}
let spawned = 0

// 模型家（單一真源；生成表＝docs/generated/reference/agents.md、換模史＝本檔 git log；user 拍板 2026-09-04）：
//   主線與 implementer＝fable 1M xhigh；其餘（review／fix 與 review 骨架四角色 lens／mirror／grader／critic）＝opus 1M xhigh、
//   且 prompt 首行帶 DEEP_THINK 字面（深思關鍵詞，由 _sk_cycle.js／_sk_review.js 烤入）。
const IMPL_OPTS = { model: 'fable[1m]', effort: 'xhigh' }
const REVIEW_OPTS = { model: 'opus[1m]', effort: 'xhigh' }
const FIX_OPTS = { model: 'opus[1m]', effort: 'xhigh' }
const LENS_OPTS = { model: 'opus[1m]', effort: 'xhigh' }
const MIRROR_OPTS = { model: 'opus[1m]', effort: 'xhigh' }
const GRADER_OPTS = { model: 'opus[1m]', effort: 'xhigh' }
const CRITIC_OPTS = { model: 'opus[1m]', effort: 'xhigh' }
const DEEP_THINK = 'ultrathink'

function guard(p, label) {
  if (typeof p !== 'string') throw new Error('防呆②：prompt 非字串（label=' + label + '）')
  if (p.length < 400) throw new Error('防呆②：prompt 過短 ' + p.length + '（label=' + label + '）')
  if (p.startsWith('undefined') || p.startsWith('null')) throw new Error('防呆②：prompt 開頭為 undefined／null（label=' + label + '）')
  if (!p.includes('zh-TW')) throw new Error('防呆②：prompt 缺 zh-TW 字面（label=' + label + '）')
  if (!p.includes(SMOKE)) throw new Error('防呆②：prompt 缺冒煙 token ' + SMOKE + '（label=' + label + '；RL-0018 置於共用段）')
  if (!/RULES-VERSION:\s*[0-9a-f]{12}/.test(p)) throw new Error('防呆②：prompt 缺規則塊版本串 RULES-VERSION（label=' + label + '；RL-0058 規則塊整塊烤入每支 prompt）')
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
    // ★LL-00010：升級的 finding 結構化指名（file×summary 逐字沿用摘要）——cycle 據此記入 escalated／過濾、不論本輪改動數。
    escalatedFindings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['file', 'summary'],
        properties: { file: { type: 'string' }, summary: { type: 'string' } },
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
