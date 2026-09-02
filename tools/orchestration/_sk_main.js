// ─────────────────── 主流程（serial） ───────────────────
phase(PH1)
log(START_LOG)

const impl1 = await spawn(IMPL1_PROMPT, Object.assign({ label: LBL1, phase: PH1, schema: WORK_SCHEMA }, IMPL_OPTS))
if (!impl1) return { unit: UNIT, status: 'failed', reason: 'implementer-1 回傳 null（終止型故障）', agentsSpawned: spawned }
if (impl1.status === 'blocked') {
  return { unit: UNIT, status: 'blocked', stage: PH1, reason: 'implementer-1 受阻', report: impl1.report, escalations: impl1.escalations || [], agentsSpawned: spawned }
}
log('implementer-1 完成（status=' + impl1.status + '、改檔 ' + (impl1.filesChanged || []).length + ' 支）→ 進接線層')

phase(PH2)
const impl2 = await spawn(impl2Prompt(impl1.report), Object.assign({ label: LBL2, phase: PH2, schema: WORK_SCHEMA }, IMPL_OPTS))
if (!impl2) return { unit: UNIT, status: 'failed', reason: 'implementer-2 回傳 null（終止型故障）', impl1Report: impl1.report, agentsSpawned: spawned }
if (impl2.status === 'blocked') {
  return { unit: UNIT, status: 'blocked', stage: PH2, reason: 'implementer-2 受阻', report: impl2.report, impl1Report: impl1.report, escalations: impl2.escalations || [], agentsSpawned: spawned }
}
log('implementer-2 完成（status=' + impl2.status + '、改檔 ' + (impl2.filesChanged || []).length + ' 支）→ 進規格對照審查')

phase('SpecReview')
const c1 = await cycle('SpecReview', SPEC_REVIEW_PROMPT, 'spec')
if (!c1.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'SpecReview', reason: c1.reason, blockers: c1.blockers, rejected: c1.rejected, impl1Report: impl1.report, impl2Report: impl2.report, agentsSpawned: spawned }
}
log('規格對照審查收斂（' + c1.rounds + ' 輪）→ 進碼品質審查')

phase('CodeQualityReview')
const c2 = await cycle('CodeQualityReview', QUALITY_REVIEW_PROMPT, 'quality')
if (!c2.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'CodeQualityReview', reason: c2.reason, blockers: c2.blockers, rejected: c2.rejected, impl1Report: impl1.report, impl2Report: impl2.report, specNotes: c1.notes, agentsSpawned: spawned }
}

return {
  unit: UNIT,
  status: 'ok',
  impl1Status: impl1.status,
  impl1Report: impl1.report,
  impl2Status: impl2.status,
  impl2Report: impl2.report,
  filesChanged: (impl1.filesChanged || []).concat(impl2.filesChanged || []),
  escalations: (impl1.escalations || []).concat(impl2.escalations || []),
  specReviewRounds: c1.rounds,
  specReviewNotes: c1.notes,
  qualityReviewRounds: c2.rounds,
  qualityReviewNotes: c2.notes,
  agentsSpawned: spawned,
}
