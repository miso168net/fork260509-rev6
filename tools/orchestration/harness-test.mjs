import fs from 'fs'
const SCRIPT = process.argv[2]
const src = fs.readFileSync(SCRIPT, 'utf8').replace(/^export const meta/m, 'const meta')
const AsyncFn = Object.getPrototypeOf(async function () {}).constructor

async function run(name, agentImpl) {
  const calls = []
  const agent = async (p, o) => { calls.push(o.label); return agentImpl(o.label, calls.length) }
  const fn = new AsyncFn('phase', 'log', 'parallel', 'agent', 'args', src)
  let r, err = null
  try { r = await fn(() => {}, () => {}, async (t) => Promise.all(t.map(f => f())), agent, undefined) }
  catch (e) { err = e.message }
  console.log('\n【' + name + '】')
  console.log('  派發 ' + calls.length + ' 支：' + calls.join(' → '))
  if (err) console.log('  throw: ' + err)
  else console.log('  return: status=' + r.status + (r.stage ? ' stage=' + r.stage : '') + (r.reason ? ' reason=' + r.reason.slice(0, 60) : ''))
  return { calls, r, err }
}

const OKW = { status: 'ok', report: 'r', filesChanged: ['f.ts'] }
const B = (s) => ({ agentStatus: 'ok', blockers: [{ file: 'a.ts', summary: s, detail: 'd' }], notes: '' })
const CLEAN = { agentStatus: 'ok', blockers: [], notes: 'clean' }

// 案1：每輪不同 blocker、確認輪清空 → 應收斂，spec 段用滿 4review+3fix=7 支
let n1 = 0
await run('案1 fix 迴圈跑滿→確認輪清空→判收斂（rev5:L-011 變形②：不得把已修好報成 unresolved）', (label) => {
  if (label.includes('implementer')) return OKW
  if (label.startsWith('spec:review')) { n1++; return n1 <= 3 ? B('缺陷' + n1) : CLEAN }
  if (label.startsWith('spec:fix')) return OKW
  return CLEAN
})

// 案2：review 連兩輪同一 blocker → 收斂偵測應攔
let n2 = 0
await run('案2 連兩輪同 blocker（file×summary 相同）→ 判不收斂', (label) => {
  if (label.includes('implementer')) return OKW
  if (label.startsWith('spec:review')) { n2++; return B('同一句摘要') }
  if (label.startsWith('spec:fix')) return OKW
  return CLEAN
})

// 案3：fix 連兩輪零改動 → 應攔
let n3 = 0
await run('案3 fix 連兩輪零改動 → 判不收斂', (label) => {
  if (label.includes('implementer')) return OKW
  if (label.startsWith('spec:review')) { n3++; return B('缺陷' + n3) }
  if (label.startsWith('spec:fix')) return { status: 'ok', report: 'r', filesChanged: [] }
  return CLEAN
})

// 案4：review agent 自陳受阻 → 立即 return（且 fix 一支都不該跑）
await run('案4 review agentStatus=failed → 立即 return', (label) => {
  if (label.includes('implementer')) return OKW
  if (label.startsWith('spec:review')) return { agentStatus: 'failed', blockers: [], notes: '工具壞了' }
  return CLEAN
})

// 案5：★rev5:L-011 變形①——review 回 blocker 絕不可被當成 agent 受阻（fix 必須真的跑）
await run('案5 review 有 blocker（agentStatus=ok）→ fix 必須跑（變形①）', (label) => {
  if (label.includes('implementer')) return OKW
  if (label.startsWith('spec:review')) return B('固定缺陷')
  if (label.startsWith('spec:fix')) return OKW
  return CLEAN
})

// 案6：★rev5:L-035——implementer 回 done_with_escalation → 必須照常跑完審查（不得立即 return）
await run('案6 implementer done_with_escalation → 照常跑完審查（rev5:L-035）', (label) => {
  if (label.includes('implementer')) return { status: 'done_with_escalation', report: 'r', filesChanged: ['f.ts'], escalations: ['清單外待辦一條'] }
  return CLEAN
})

// 案7：implementer blocked → 立即 return、零審查
await run('案7 implementer blocked → 立即 return、零審查', (label) => {
  if (label.includes('implementer')) return { status: 'blocked', report: '做不下去', filesChanged: [], escalations: ['x'] }
  return CLEAN
})

// 案8：fix agent blocked → 立即 return
let n8 = 0
await run('案8 fix agent blocked → 立即 return', (label) => {
  if (label.includes('implementer')) return OKW
  if (label.startsWith('spec:review')) { n8++; return B('缺陷' + n8) }
  if (label.startsWith('spec:fix')) return { status: 'blocked', report: '要動清單外檔', filesChanged: [], escalations: ['x'] }
  return CLEAN
})

// 案9：保險絲——review 每輪不同 blocker、兩段都跑滿且確認輪仍有 blocker
let n9 = 0
await run('案9 兩段皆跑滿（確認輪仍有 blocker）→ 應在 spec 段就 return、不逾保險絲', (label) => {
  if (label.includes('implementer')) return OKW
  if (label.includes('review')) { n9++; return B('缺陷' + n9) }
  return OKW
})

// 案10：★rev5:L-078——fix 回 done_with_escalation 且零改動 → 應「當場 return 升級」而非判不收斂
let n10 = 0
await run('案10 fix done_with_escalation＋零改動 → 當場 return 升級（rev5:L-078，非不收斂）', (label) => {
  if (label.includes('implementer')) return OKW
  if (label.startsWith('spec:review')) { n10++; return B('清單外檔的缺陷' + n10) }
  if (label.startsWith('spec:fix')) return { status: 'done_with_escalation', report: '該檔在不得動清單', filesChanged: [], escalations: ['data-model.md 那列要主線改'] }
  return CLEAN
})
