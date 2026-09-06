// 編排骨架 harness（控制流十五案＝十二正例＋三反例；BL-00001 起帶斷言與退出碼＝000-r1 R1-082 處置、反例＝BL-00033 於 maint-backlog-6 收掉）。
// 用法：node tools/orchestration/harness-test.mjs <組裝好的 script.mjs> [spec|quality]
//   spec（預設）＝樁把 blocker 打在規格對照段；quality＝打在碼品質段（原 quality-only 變體併入、以第二參數切換）。
// 期望值自 script 的 `const IMPLEMENTERS = <n>` 行推導（樁對每支 implementer 回同一形；n=0＝續跑形、案7 改驗零 implementer 直入審查）；任一斷言不符→逐項列出、exit 1；用法錯 exit 2。
// 樁走真 spawn／guard（prompt 長度、zh-TW、冒煙 token、RULES-VERSION 皆在此被驗），只有 agent() 被替換；樁另記每支 prompt 原文供內容斷言（案 11／12：已駁回／已升級清單的渲染面）。
import fs from 'fs'
const SCRIPT = process.argv[2]
const TAG = process.argv[3] || 'spec'
if (!SCRIPT || (TAG !== 'spec' && TAG !== 'quality')) {
  console.error('用法：node harness-test.mjs <script.mjs> [spec|quality]')
  process.exit(2)
}
const src = fs.readFileSync(SCRIPT, 'utf8').replace(/^export const meta/m, 'const meta')
const mImpl = src.match(/^const IMPLEMENTERS = (\d+)\s*$/m)
if (!mImpl) {
  console.error('script 缺 `const IMPLEMENTERS = <n>` 行（_vars 段）——期望值無從推導')
  process.exit(2)
}
const N = Number(mImpl[1])
const PRE = N + (TAG === 'quality' ? 1 : 0) // quality 模式：規格段一支 review 即收斂、blocker 打在品質段
const STAGE = TAG === 'quality' ? 'CodeQualityReview' : 'SpecReview'
const ROUNDS_KEY = TAG === 'quality' ? 'qualityReviewRounds' : 'specReviewRounds'
const isRev = (l) => l.startsWith(TAG + ':review')
const isFix = (l) => l.startsWith(TAG + ':fix')
const AsyncFn = Object.getPrototypeOf(async function () {}).constructor

let failed = 0
function expect(cond, what, got) {
  if (cond) console.log('  ✓ ' + what)
  else { failed += 1; console.log('  ✗ ' + what + '（實得：' + String(got) + '）') }
}
async function run(name, agentImpl, check) {
  const calls = []
  const prompts = []
  const agent = async (p, o) => { calls.push(o.label); prompts.push(p); return agentImpl(o.label, calls.length) }
  const fn = new AsyncFn('phase', 'log', 'parallel', 'agent', 'args', src)
  let r = null, err = null
  try { r = await fn(() => {}, () => {}, async (t) => Promise.all(t.map(f => f())), agent, undefined) }
  catch (e) { err = e.message }
  console.log('\n【' + name + '】')
  console.log('  派發 ' + calls.length + ' 支：' + calls.join(' → '))
  if (err) console.log('  throw: ' + err)
  else console.log('  return: status=' + r.status + (r.stage ? ' stage=' + r.stage : '') + (r.reason ? ' reason=' + r.reason.slice(0, 60) : ''))
  check({ calls, prompts, r: r || {}, err })
}
const noThrow = (o) => expect(o.err === null, '不 throw', o.err)
const status = (o, s) => expect(o.r.status === s, 'status=' + s, o.r.status)
const stage = (o) => expect(o.r.stage === STAGE, 'stage=' + STAGE, o.r.stage)
const reason = (o, s) => expect(typeof o.r.reason === 'string' && o.r.reason.includes(s), 'reason 含「' + s + '」', o.r.reason)
const count = (o, n) => expect(o.calls.length === n, '派發恰 ' + n + ' 支', o.calls.length)

const OKW = { status: 'ok', report: 'r', filesChanged: ['f.ts'] }
const B = (s) => ({ agentStatus: 'ok', blockers: [{ file: 'a.ts', summary: s, detail: 'd' }], notes: '' })
const CLEAN = { agentStatus: 'ok', blockers: [], notes: 'clean' }

// 案1：每輪不同 blocker、確認輪清空 → 應收斂，該段用滿 4review+3fix=7 支
let n1 = 0
await run('案1 fix 迴圈跑滿→確認輪清空→判收斂（rev5:L-011 變形②：不得把已修好報成 unresolved）', (label) => {
  if (label.includes('implementer')) return OKW
  if (isRev(label)) { n1++; return n1 <= 3 ? B('缺陷' + n1) : CLEAN }
  if (isFix(label)) return OKW
  return CLEAN
}, (o) => { noThrow(o); status(o, 'ok'); count(o, N + 8); expect(o.r[ROUNDS_KEY] === 4, ROUNDS_KEY + '=4', o.r[ROUNDS_KEY]) })

// 案2：review 連兩輪同一 blocker → 收斂偵測應攔
let n2 = 0
await run('案2 連兩輪同 blocker（file×summary 相同）→ 判不收斂', (label) => {
  if (label.includes('implementer')) return OKW
  if (isRev(label)) { n2++; return B('同一句摘要') }
  if (isFix(label)) return OKW
  return CLEAN
}, (o) => { noThrow(o); status(o, 'unresolved'); stage(o); reason(o, '連兩輪 blocker 集合'); count(o, PRE + 3) })

// 案3：fix 連兩輪零改動 → 應攔
let n3 = 0
await run('案3 fix 連兩輪零改動 → 判不收斂', (label) => {
  if (label.includes('implementer')) return OKW
  if (isRev(label)) { n3++; return B('缺陷' + n3) }
  if (isFix(label)) return { status: 'ok', report: 'r', filesChanged: [] }
  return CLEAN
}, (o) => { noThrow(o); status(o, 'unresolved'); stage(o); reason(o, '連兩輪零改動'); count(o, PRE + 4) })

// 案4：review agent 自陳受阻 → 立即 return（且 fix 一支都不該跑）
await run('案4 review agentStatus=failed → 立即 return', (label) => {
  if (label.includes('implementer')) return OKW
  if (isRev(label)) return { agentStatus: 'failed', blockers: [], notes: '工具壞了' }
  return CLEAN
}, (o) => { noThrow(o); status(o, 'unresolved'); stage(o); reason(o, 'agentStatus=failed'); count(o, PRE + 1); expect(!o.calls.some(isFix), '零 fix', o.calls.filter(isFix).join(',')) })

// 案5：★rev5:L-011 變形①——review 回 blocker 絕不可被當成 agent 受阻（fix 必須真的跑）
await run('案5 review 有 blocker（agentStatus=ok）→ fix 必須跑（變形①）', (label) => {
  if (label.includes('implementer')) return OKW
  if (isRev(label)) return B('固定缺陷')
  if (isFix(label)) return OKW
  return CLEAN
}, (o) => { noThrow(o); expect(o.calls.includes(TAG + ':fix-1'), 'fix-1 真的跑', o.calls.join(',')); status(o, 'unresolved'); count(o, PRE + 3) })

// 案6：★rev5:L-035——implementer 回 done_with_escalation → 必須照常跑完審查（不得立即 return）
await run('案6 implementer done_with_escalation → 照常跑完審查（rev5:L-035）', (label) => {
  if (label.includes('implementer')) return { status: 'done_with_escalation', report: 'r', filesChanged: ['f.ts'], escalations: ['清單外待辦一條'] }
  return CLEAN
}, (o) => {
  noThrow(o); status(o, 'ok'); count(o, N + 2)
  expect(Array.isArray(o.r.implStatuses) && o.r.implStatuses.length === N && o.r.implStatuses.every((s) => s === 'done_with_escalation'), 'implStatuses 全為 done_with_escalation', JSON.stringify(o.r.implStatuses))
  expect(Array.isArray(o.r.escalations) && o.r.escalations.length === N, 'escalations 逐支帶回', JSON.stringify(o.r.escalations))
})

// 案7：implementer blocked → 立即 return、零審查（★N=0 續跑形無 implementer 段：改驗零 implementer、直入審查、兩支即收斂）
if (N === 0) {
  await run('案7 續跑形（IMPLEMENTERS=0）→ 零 implementer、直入審查（RL-0010）', () => CLEAN, (o) => {
    noThrow(o); status(o, 'ok'); count(o, 2)
    expect(!o.calls.some((l) => l.includes('implementer')), '零 implementer', o.calls.join(','))
    expect(Array.isArray(o.r.implStatuses) && o.r.implStatuses.length === 0, 'implStatuses 空', JSON.stringify(o.r.implStatuses))
  })
} else {
  await run('案7 implementer blocked → 立即 return、零審查', (label) => {
    if (label.includes('implementer')) return { status: 'blocked', report: '做不下去', filesChanged: [], escalations: ['x'] }
    return CLEAN
  }, (o) => { noThrow(o); status(o, 'blocked'); count(o, 1); expect(!o.calls.some((l) => l.includes('review')), '零審查', o.calls.join(',')) })
}

// 案8：fix agent blocked → 立即 return
let n8 = 0
await run('案8 fix agent blocked → 立即 return', (label) => {
  if (label.includes('implementer')) return OKW
  if (isRev(label)) { n8++; return B('缺陷' + n8) }
  if (isFix(label)) return { status: 'blocked', report: '要動清單外檔', filesChanged: [], escalations: ['x'] }
  return CLEAN
}, (o) => { noThrow(o); status(o, 'unresolved'); stage(o); reason(o, 'fix agent blocked'); count(o, PRE + 2) })

// 案9：保險絲——該段 review 每輪不同 blocker、跑滿且確認輪仍有 blocker → 在該段 return、不逾保險絲
let n9 = 0
await run('案9 該段跑滿（確認輪仍有 blocker）→ 在該段 return、不逾保險絲', (label) => {
  if (label.includes('implementer')) return OKW
  if (isRev(label)) { n9++; return B('缺陷' + n9) }
  if (isFix(label)) return OKW
  return CLEAN
}, (o) => { noThrow(o); status(o, 'unresolved'); stage(o); reason(o, '確認輪仍有 blocker'); count(o, PRE + 7) })

// 案10：★RL-0025（ADR-00013、承 rev5:L-078 改形）——fix 回 done_with_escalation 且零改動、零駁回 → 該段判收斂帶升級項、進下一段（不終止 run）
const AFTER = TAG === 'quality' ? 0 : 1 // spec 模式：規格段收斂後尚有品質段一支 review
let n10 = 0
await run('案10 fix done_with_escalation＋零改動＋零駁回 → 該段收斂帶升級、進下一段（RL-0025／ADR-00013）', (label) => {
  if (label.includes('implementer')) return OKW
  if (isRev(label)) { n10++; return B('清單外檔的缺陷' + n10) }
  if (isFix(label)) return { status: 'done_with_escalation', report: '該檔在不得動清單', filesChanged: [], escalations: ['data-model.md 那列要主線改'] }
  return CLEAN
}, (o) => {
  noThrow(o); status(o, 'ok'); count(o, PRE + 2 + AFTER)
  expect(o.r[ROUNDS_KEY] === 1, ROUNDS_KEY + '=1', o.r[ROUNDS_KEY])
  expect(Array.isArray(o.r.escalations) && o.r.escalations.length === 1, 'escalations 帶回 1 條', JSON.stringify(o.r.escalations))
  expect(Array.isArray(o.r.escalatedBlockers) && o.r.escalatedBlockers.length === 1, 'escalatedBlockers 帶回 1 條', JSON.stringify(o.r.escalatedBlockers))
  expect(Array.isArray(o.r.escalatedStages) && o.r.escalatedStages.includes(STAGE), 'escalatedStages 含 ' + STAGE, JSON.stringify(o.r.escalatedStages))
})

// 案11：★RL-0025——fix 零改動升級但駁回其一 → 續下一輪 review 核駁回（RL-0071）；已升級項被重報＝過濾不計、該段收斂
let n11 = 0
await run('案11 fix 零改動升級＋駁回一項 → 續審駁回、已升級項重報被過濾、該段收斂（RL-0025／RL-0071）', (label) => {
  if (label.includes('implementer')) return OKW
  if (isRev(label)) {
    n11++
    if (n11 === 1) return { agentStatus: 'ok', blockers: [{ file: 'a.ts', summary: '清單外真缺陷', detail: 'd' }, { file: 'b.ts', summary: '誤報', detail: 'd' }], notes: '' }
    return { agentStatus: 'ok', blockers: [{ file: 'a.ts', summary: '清單外真缺陷', detail: '重報' }], notes: '' }
  }
  if (isFix(label)) return { status: 'done_with_escalation', report: 'a.ts 清單外、b.ts 誤報', filesChanged: [], escalations: ['a.ts 那行要主線改'], rejectedFindings: [{ file: 'b.ts', summary: '誤報', why: '碼已如此' }] }
  return CLEAN
}, (o) => {
  noThrow(o); status(o, 'ok'); count(o, PRE + 3 + AFTER)
  expect(o.r[ROUNDS_KEY] === 2, ROUNDS_KEY + '=2', o.r[ROUNDS_KEY])
  expect(Array.isArray(o.r.escalatedBlockers) && o.r.escalatedBlockers.length === 1 && o.r.escalatedBlockers[0].file === 'a.ts', 'escalatedBlockers 恰 a.ts 一條', JSON.stringify(o.r.escalatedBlockers))
  const p2 = o.prompts[o.calls.indexOf(TAG + ':review-2')] || ''
  expect(p2.includes('前輪已駁回 findings 清單') && p2.includes('b.ts') && p2.includes('誤報') && p2.includes('碼已如此'), '次輪 review prompt 渲染已駁回清單（RL-0071：file／summary／why）', p2.length)
  expect(p2.includes('前輪已升級主線之 findings 清單') && p2.includes('a.ts') && p2.includes('清單外真缺陷'), '次輪 review prompt 渲染已升級清單（ADR-00013）', p2.length)
})

// 案12：★LL-00010——fix 部分改動＋以 escalatedFindings 結構化升級一項 → 次輪同 file×summary 重報被過濾、該段第 2 輪收斂帶升級
let n12 = 0
await run('案12 fix 部分改動＋結構化升級一項 → 次輪重報被過濾、第 2 輪收斂帶升級（RL-0025／LL-00010）', (label) => {
  if (label.includes('implementer')) return OKW
  if (isRev(label)) {
    n12++
    if (n12 === 1) return { agentStatus: 'ok', blockers: [{ file: 'a.ts', summary: '清單外真缺陷', detail: 'd' }, { file: 'c.ts', summary: '可修缺陷', detail: 'd' }], notes: '' }
    return { agentStatus: 'ok', blockers: [{ file: 'a.ts', summary: '清單外真缺陷', detail: '換措辭重報' }], notes: '' }
  }
  if (isFix(label)) return { status: 'done_with_escalation', report: 'c.ts 已修、a.ts 清單外', filesChanged: ['c.ts'], escalations: ['a.ts 那行要主線改'], escalatedFindings: [{ file: 'a.ts', summary: '清單外真缺陷' }] }
  return CLEAN
}, (o) => {
  noThrow(o); status(o, 'ok'); count(o, PRE + 3 + AFTER)
  expect(o.r[ROUNDS_KEY] === 2, ROUNDS_KEY + '=2', o.r[ROUNDS_KEY])
  expect(Array.isArray(o.r.escalatedBlockers) && o.r.escalatedBlockers.length === 1 && o.r.escalatedBlockers[0].file === 'a.ts' && o.r.escalatedBlockers[0].detail === 'd', 'escalatedBlockers 恰 a.ts 一條（帶原 detail）', JSON.stringify(o.r.escalatedBlockers))
  const p2 = o.prompts[o.calls.indexOf(TAG + ':review-2')] || ''
  expect(p2.includes('前輪已升級主線之 findings 清單') && p2.includes('a.ts') && p2.includes('清單外真缺陷'), '次輪 review prompt 渲染結構化升級項（LL-00010）', p2.length)
})

// 案13～15：反例（RL-0051 一正一反、變異打在 head 判準上、皆須零派發）——以讀進來的 src 就地變異或改 args 驅動。
async function runNegative(name, mutatedSrc, argsValue, fragment) {
  const calls = []
  const agent = async (p, o) => { calls.push(o.label); return CLEAN }
  let err = null
  try { await new AsyncFn('phase', 'log', 'parallel', 'agent', 'args', mutatedSrc)(() => {}, () => {}, async (t) => Promise.all(t.map(f => f())), agent, argsValue) } catch (e) { err = e.message }
  console.log('\n【' + name + '】')
  console.log('  throw: ' + (err === null ? '（無）' : err.slice(0, 120)))
  expect(err !== null && err.includes(fragment), 'throw 含「' + fragment + '」', err)
  expect(calls.length === 0, '零派發', calls.length)
}
await runNegative('案13 反例：args 非空 → 防呆① 零派發即 throw', src, { x: 1 }, '防呆①')
const mSmoke = src.match(/^const SMOKE = '([^']+)'\s*$/m)
await runNegative('案14 反例：SMOKE 取字面 test（看門狗會當自測子命令）→ 防呆② 零派發即 throw', mSmoke ? src.replace(mSmoke[0], "const SMOKE = 'test'") : src, undefined, '防呆②')
await runNegative('案15 反例：IMPLEMENTERS 灌到結構最壞值逾保險絲上限 20 → 防呆③ 零派發即 throw', src.replace(mImpl[0], 'const IMPLEMENTERS = 9'), undefined, '防呆③')

console.log('\n' + (failed ? '✗ harness：' + failed + ' 項斷言不符' : '✓ harness：十五案全過') + '（IMPLEMENTERS=' + N + '、模式=' + TAG + '）')
process.exit(failed ? 1 : 0)
