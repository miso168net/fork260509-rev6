// review 形骨架 harness（六案；BL-00006 入庫）：以樁 agent 乾跑組裝好的 review script——驗派發數／label 唯一／三態聚合／零 findings 跳過／
//   null 與 agentStatus=failed 留帳不殺 run／保險絲與 guard（每支渲染後 prompt 的長度、zh-TW、冒煙 token、RULES-VERSION 在真 guard 下被驗）。
// 用法：node tools/orchestration/harness-review.mjs <組裝好的 script.mjs>
// 期望值不寫死：自 script 的 `const REVIEW_STAGE`／`const INLINE_VERIFY`／`const CRITIC = null`／`const SMOKE` 行與回傳結構（lenses／probes／batches 長度）推導；
//   樁走真 spawn／guard、只有 agent()／parallel()／pipeline() 被替換。
import fs from 'fs'
const SCRIPT = process.argv[2]
if (!SCRIPT) {
  console.error('用法：node harness-review.mjs <script.mjs>')
  process.exit(2)
}
const src = fs.readFileSync(SCRIPT, 'utf8').replace(/^export const meta/m, 'const meta')
const mStage = src.match(/^const REVIEW_STAGE = '(explore|verify)'\s*$/m)
if (!mStage) {
  console.error("script 缺 `const REVIEW_STAGE = 'explore'|'verify'` 行（_vars 段）——非 review 形 script（TDD 形請用 harness-test.mjs）")
  process.exit(2)
}
const mSmoke = src.match(/^const SMOKE = '([^']+)'\s*$/m)
if (!mSmoke) {
  console.error("script 缺 `const SMOKE = '…'` 行（_vars 段）")
  process.exit(2)
}
const STAGE = mStage[1]
const SMOKE = mSmoke[1]
const INLINE = STAGE === 'explore' && /^const INLINE_VERIFY = true\s*$/m.test(src)
const HAS_CRITIC = STAGE === 'verify' && !/^const CRITIC = null\s*$/m.test(src)
const AsyncFn = Object.getPrototypeOf(async function () {}).constructor

let failed = 0
function expect(cond, what, got) {
  if (cond) console.log('  ✓ ' + what)
  else { failed += 1; console.log('  ✗ ' + what + '（實得：' + String(got) + '）') }
}
const keysOf = (p) => [...p.matchAll(/^■ (\S+?)｜/gm)].map((m) => m[1])
const finding = (i) => ({ file: 'README.md', locator: '§' + i, summary: '測' + i, category: '檢索性', severity: 'minor', evidence: { command: 'grep -n x README.md', output: 'y' }, proposed: { disposition: '修', fix: 'f' }, confidence: 0.5 })
const lensResult = (n) => ({ agentStatus: 'ok', lens: 'L', findings: Array.from({ length: n }, (_, i) => finding(i + 1)), coverage: { files_read: ['README.md'], commands_run: [] } })
const probeResult = { agentStatus: 'ok', answers: [{ question: 'q', answer: 'a', path: ['README.md'], hops: 1, found: true, confidence: 0.9 }] }
const verdicts = (keys, fn) => ({ agentStatus: 'ok', lens: 'x', verdicts: keys.map((k, i) => ({ key: k, verdict: fn(k, i), reason: 'r', evidence: 'e' })).filter((v) => v.verdict !== null) })
const gradeResult = (n) => ({ agentStatus: 'ok', grades: [{ question: 'q', verdict: '找得到', truth: 't', truth_path: ['README.md'], min_hops: 1 }], findings: Array.from({ length: n }, (_, i) => finding(i + 1)) })
const criticResult = { agentStatus: 'ok', gaps: [], unverified: [] }

// 基準樁：lens 依派發序給 3／0／2… 筆 findings（第二支零＝驗跳過兩鏡）；real 鏡全「確認」；decided 鏡只答前兩鍵＝確認／駁回（第三鍵缺答＝uncertain）；
//   grader 2 筆；refuter 答 確認／不確定；critic ok。
function baseStub(state) {
  return (label, prompt) => {
    if (label.startsWith('lens:')) { state.lens += 1; return lensResult(state.lens === 1 ? 3 : (state.lens === 2 ? 0 : 2)) }
    if (label.startsWith('probe:')) return probeResult
    if (label.startsWith('real:')) return verdicts(keysOf(prompt), () => '確認')
    if (label.startsWith('decided:')) return verdicts(keysOf(prompt), (k, i) => (i === 0 ? '確認' : (i === 1 ? '駁回' : null)))
    if (label.startsWith('grader:')) return gradeResult(2)
    if (label.startsWith('refute:')) return verdicts(keysOf(prompt), (k, i) => (i === 0 ? '確認' : '不確定'))
    if (label === 'critic') return criticResult
    throw new Error('樁不認得 label ' + label)
  }
}
async function run(name, agentImpl, check) {
  const calls = []
  const agent = async (p, o) => { calls.push({ label: o.label, prompt: p, model: o.model, effort: o.effort, schema: !!o.schema }); return agentImpl(o.label, p) }
  const parallel = async (thunks) => Promise.all(thunks.map((t) => t()))
  const pipeline = async (items, ...stages) => Promise.all(items.map(async (it, i) => { let v = it; for (const s of stages) v = await s(v, it, i); return v }))
  const fn = new AsyncFn('phase', 'log', 'parallel', 'pipeline', 'agent', 'args', src)
  let r = null, err = null
  try { r = await fn(() => {}, () => {}, parallel, pipeline, agent, undefined) } catch (e) { err = e.message }
  console.log('\n【' + name + '】')
  console.log('  派發 ' + calls.length + ' 支：' + calls.map((c) => c.label).join(' → '))
  if (err) console.log('  throw: ' + err)
  else console.log('  return: status=' + r.status + ' stage=' + r.stage + ' nulls=' + JSON.stringify(r.nulls) + ' failed=' + JSON.stringify(r.failed))
  check({ calls, r: r || {}, err })
}
const noThrow = (o) => expect(o.err === null, '不 throw', o.err)
const status = (o, s) => expect(o.r.status === s, 'status=' + s, o.r.status)
const count = (o, n) => expect(o.calls.length === n, '派發恰 ' + n + ' 支', o.calls.length)
const labels = (o) => o.calls.map((c) => c.label)
const has = (o, l) => labels(o).includes(l)
const finals = (t) => (t || []).map((v) => v.final)
// 結構長度（自回傳推導；樁形固定、故期望派發數可由此算）
const L = (o) => (o.r.lenses || []).length
const P = (o) => (o.r.probes || []).length
const B = (o) => (o.r.batches || []).length
const lensWithFindings = (o) => (STAGE === 'explore' ? (L(o) >= 2 ? L(o) - 1 : L(o)) : 0)
const expectedBase = (o) => (STAGE === 'explore'
  ? L(o) + P(o) + (INLINE ? 2 * lensWithFindings(o) + 2 * P(o) : 0)
  : 2 * B(o) + 2 * P(o) + (HAS_CRITIC ? 1 : 0))
const worst = (o) => (STAGE === 'explore' ? L(o) + P(o) + (INLINE ? 2 * L(o) + 2 * P(o) : 0) : 2 * B(o) + 2 * P(o) + (HAS_CRITIC ? 1 : 0))
const firstLensKey = (o) => (o.r.lenses && o.r.lenses[0] ? o.r.lenses[0].key : null)
const firstBatchKey = (o) => (o.r.batches && o.r.batches[0] ? o.r.batches[0].batch : null)
const firstTable = (o) => (STAGE === 'explore' ? (o.r.lenses && o.r.lenses[0] && o.r.lenses[0].verify ? o.r.lenses[0].verify.verdicts : []) : (o.r.batches && o.r.batches[0] ? o.r.batches[0].verdicts : []))
const mirrorsExpected = STAGE === 'verify' || INLINE

// 案1：正常路徑——派發數＝結構、label 唯一、status ok、每支 prompt 過 guard 且模型家一致
await run('案1 正常路徑：派發數＝結構、label 唯一、status ok、prompt 含冒煙／zh-TW／RULES-VERSION', baseStub({ lens: 0 }), (o) => {
  noThrow(o); status(o, 'ok'); count(o, expectedBase(o))
  expect(new Set(labels(o)).size === o.calls.length, 'label 唯一', labels(o).join(','))
  expect(o.calls.every((c) => c.prompt.includes(SMOKE) && c.prompt.includes('zh-TW') && /RULES-VERSION:\s*[0-9a-f]{12}/.test(c.prompt) && c.prompt.length >= 400), '每支 prompt 含冒煙 token／zh-TW／RULES-VERSION 且 ≥400 字', '')
  expect(o.calls.every((c) => c.model === 'opus[1m]' && c.effort === 'xhigh' && c.schema), '每支 opus[1m]／xhigh／帶 schema', JSON.stringify(o.calls.map((c) => [c.model, c.effort, c.schema])))
  expect(o.r.agentsSpawned === o.calls.length && o.calls.length <= worst(o) + 1, 'agentsSpawned＝派發數且 ≤ 結構最壞＋1（保險絲）', o.r.agentsSpawned + '/' + worst(o))
  expect(typeof o.r.summary === 'object' && typeof o.r.summary.findings === 'number', 'summary 結構化計數在', JSON.stringify(o.r.summary))
})

// 案2：三態聚合——兩鏡皆確認→confirmed；任一駁回→refuted；缺答／不確定→uncertain；探針單鏡 確認／不確定
await run('案2 三態聚合（confirmed／refuted／uncertain；探針單鏡）', baseStub({ lens: 0 }), (o) => {
  noThrow(o)
  if (!mirrorsExpected) {
    expect(o.r.summary.findings === 0 && finals(firstTable(o)).length === 0, '無 inline 兩鏡：零 verdict、summary.findings=0', JSON.stringify(o.r.summary))
    return
  }
  const f = finals(firstTable(o))
  expect(f[0] === 'confirmed', '首鍵兩鏡皆確認→confirmed', f[0])
  if (f.length >= 2) expect(f[1] === 'refuted', '次鍵 decided 駁回→refuted', f[1])
  if (f.length >= 3) expect(f.slice(2).every((x) => x === 'uncertain'), '第三鍵起 decided 缺答→uncertain', f.slice(2).join(','))
  const pt = (o.r.probes && o.r.probes[0]) ? finals(o.r.probes[0].verdicts) : []
  if (P(o) > 0) expect(pt[0] === 'confirmed' && pt[1] === 'uncertain', '探針衍生：refuter 確認／不確定→confirmed／uncertain', pt.join(','))
  else console.log('  （無探針、單鏡案空跑）')
  const sum = o.r.summary
  expect(sum.findings === sum.confirmed + sum.refuted + sum.uncertain, 'summary 三態加總＝findings', JSON.stringify(sum))
})

// 案3：零 findings 跳過——零 findings 的 lens 不派兩鏡；grader 零 findings 不派 refuter
await run('案3 零 findings 跳過（lens 零 findings→無兩鏡；grader 零 findings→無 refuter）', (label, prompt) => {
  const s = baseStub.__s || (baseStub.__s = { lens: 0 })
  if (label.startsWith('grader:')) return gradeResult(0)
  return baseStub(s)(label, prompt)
}, (o) => {
  baseStub.__s = null
  noThrow(o); status(o, 'ok')
  if (STAGE === 'explore' && INLINE && L(o) >= 2) {
    const k2 = o.r.lenses[1].key
    expect(!has(o, 'real:' + k2) && !has(o, 'decided:' + k2), '零 findings 的 lens 無兩鏡', labels(o).filter((l) => l.endsWith(':' + k2)).join(','))
  } else console.log('  （無 inline 兩鏡或不足兩支 lens、lens 跳過案空跑）')
  if (mirrorsExpected && P(o) > 0) {
    expect(!labels(o).some((l) => l.startsWith('refute:')), 'grader 零 findings→零 refuter', labels(o).filter((l) => l.startsWith('refute:')).join(','))
    count(o, expectedBase(o) - P(o))
  } else console.log('  （無探針、refuter 跳過案空跑）')
})

// 案4：null 回傳不殺 run——首支 real 鏡（或無兩鏡時首支 lens）回 null → 不 throw、status partial、nulls 記入、其餘照跑
await run('案4 agent 回 null → 不 throw、status partial、nulls 留帳、其餘照跑', (label, prompt) => {
  const s = baseStub.__s || (baseStub.__s = { lens: 0, nulled: false })
  const target = mirrorsExpected ? 'real:' : 'lens:'
  if (label.startsWith(target) && !s.nulled) { s.nulled = true; return null }
  return baseStub(s)(label, prompt)
}, (o) => {
  baseStub.__s = null
  noThrow(o); status(o, 'partial')
  const nl = (o.r.nulls || [])[0] || ''
  expect(nl.startsWith(mirrorsExpected ? 'real:' : 'lens:'), 'nulls 首筆為被打 null 的 label', JSON.stringify(o.r.nulls))
  if (mirrorsExpected) {
    const key = nl.slice(nl.indexOf(':') + 1)
    const tbl = STAGE === 'explore' ? ((o.r.lenses.find((x) => x.key === key) || {}).verify || {}).verdicts : (o.r.batches.find((x) => x.batch === key) || {}).verdicts
    const f = finals(tbl)
    expect(f.length > 0 && f.every((x, i) => (i === 1 ? x === 'refuted' : x === 'uncertain')), 'real 缺答：decided 駁回鍵→refuted、其餘→uncertain', f.join(','))
    count(o, expectedBase(o))
  } else {
    count(o, expectedBase(o))
  }
})

// 案5：agentStatus=failed 不殺 run——首支 lens（explore）／首支 decided 鏡（verify）自陳 failed → status partial、failed 留帳
await run('案5 agentStatus=failed → 不 throw、status partial、failed 留帳', (label, prompt) => {
  const s = baseStub.__s || (baseStub.__s = { lens: 0, hit: false })
  const target = STAGE === 'explore' ? 'lens:' : 'decided:'
  if (label.startsWith(target) && !s.hit) { s.hit = true; const base = baseStub(s)(label, prompt); return Object.assign({}, base, { agentStatus: 'failed', notes: '工具壞了' }) }
  return baseStub(s)(label, prompt)
}, (o) => {
  baseStub.__s = null
  noThrow(o); status(o, 'partial')
  expect((o.r.failed || []).length === 1 && o.r.failed[0].startsWith(STAGE === 'explore' ? 'lens:' : 'decided:'), 'failed 恰一筆＝自陳受阻者', JSON.stringify(o.r.failed))
  if (STAGE === 'explore' && INLINE) {
    const k1 = firstLensKey(o)
    expect(!has(o, 'real:' + k1), 'failed 的 lens 不派兩鏡', labels(o).filter((l) => l.endsWith(':' + k1)).join(','))
    count(o, expectedBase(o) - 2)
  } else count(o, expectedBase(o))
})

// 案6：guard 真的擋——把某支 prompt 抽掉冒煙 token（樁在 agent() 前無從介入，改驗 script 常數面：SMOKE 不得為 test、每支 prompt 已在案1 逐支驗）；
//   另驗 status／stage／smoke 回傳鍵齊全＝主線三分流的結構化面。
await run('案6 回傳形（status／stage／smoke／nulls／failed／summary／agentsSpawned）齊全、smoke 回填', baseStub({ lens: 0 }), (o) => {
  noThrow(o)
  const keys = ['status', 'stage', 'smoke', 'nulls', 'failed', 'summary', 'agentsSpawned', STAGE === 'explore' ? 'lenses' : 'batches', 'probes']
  expect(keys.every((k) => k in o.r), '回傳鍵齊全 ' + keys.join('/'), Object.keys(o.r).join(','))
  expect(o.r.smoke === SMOKE && SMOKE !== 'test', 'smoke 回填＝script 常數且非 test', o.r.smoke)
  expect(o.r.stage === STAGE, 'stage=' + STAGE, o.r.stage)
  if (STAGE === 'verify') expect((o.r.critic !== null) === HAS_CRITIC, 'critic ' + (HAS_CRITIC ? '有' : '無') + '（與 script 常數一致）', o.r.critic)
})

console.log('\n' + (failed ? '✗ harness-review：' + failed + ' 項斷言不符' : '✓ harness-review：六案全過') + '（stage=' + STAGE + (INLINE ? '、inline 兩鏡' : '') + (HAS_CRITIC ? '、critic' : '') + '）')
process.exit(failed ? 1 : 0)
