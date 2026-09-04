// 骨架首段（單一骨架、BL-00001 收斂）：防呆①args 斷言／②guard／③保險絲推導＋自我斷言／④兩套 schema（WORK＝status，REVIEW＝agentStatus）。
// ★引用 _vars 段的模板常數：IMPLEMENTERS（本單元 serial implementer 支數、與 _prompts 段 IMPL_STAGES 支數由 _sk_main.js 自我斷言；0＝續跑形＝只跑審查段、RL-0010）、
//   SMOKE（冒煙 token；RL-0018 置於各 prompt 共用段、RL-0059 派發前斷言；★不可取字面 test＝wf-watchdog 會當自測子命令）。
if (typeof args !== 'undefined' && args !== null) {
  throw new Error('防呆①：本 script 不接受 args——一切邊界寫死於 script 常數')
}
if (typeof IMPLEMENTERS !== 'number' || !Number.isInteger(IMPLEMENTERS) || IMPLEMENTERS < 0) {
  throw new Error('防呆③：IMPLEMENTERS 須為 ≥0 的整數（0＝續跑形、只跑審查段）、由 _vars 段定義（現值 ' + String(IMPLEMENTERS) + '）')
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
