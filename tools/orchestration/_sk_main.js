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
