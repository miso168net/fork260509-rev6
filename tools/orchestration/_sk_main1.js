// ─────────────────── 主流程（serial） ───────────────────
phase(PH1)
log(START_LOG)

const impl = await spawn(IMPL_PROMPT, Object.assign({ label: LBL1, phase: PH1, schema: WORK_SCHEMA }, IMPL_OPTS))
if (!impl) return { unit: UNIT, status: 'failed', reason: 'implementer 回傳 null（終止型故障）', agentsSpawned: spawned }
if (impl.status === 'blocked') {
  return { unit: UNIT, status: 'blocked', reason: 'implementer 受阻', report: impl.report, escalations: impl.escalations || [], agentsSpawned: spawned }
}
log('implementer 完成（status=' + impl.status + '、改檔 ' + (impl.filesChanged || []).length + ' 支）→ 進契約對照審查')

phase('SpecReview')
const c1 = await cycle('SpecReview', SPEC_REVIEW_PROMPT, 'spec')
if (!c1.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'SpecReview', reason: c1.reason, blockers: c1.blockers, rejected: c1.rejected, implReport: impl.report, implStatus: impl.status, agentsSpawned: spawned }
}
log('契約對照審查收斂（' + c1.rounds + ' 輪）→ 進碼品質審查')

phase('CodeQualityReview')
const c2 = await cycle('CodeQualityReview', QUALITY_REVIEW_PROMPT, 'quality')
if (!c2.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'CodeQualityReview', reason: c2.reason, blockers: c2.blockers, rejected: c2.rejected, implReport: impl.report, implStatus: impl.status, specNotes: c1.notes, agentsSpawned: spawned }
}

return {
  unit: UNIT,
  status: 'ok',
  implStatus: impl.status,
  implReport: impl.report,
  filesChanged: impl.filesChanged || [],
  escalations: impl.escalations || [],
  specReviewRounds: c1.rounds,
  specReviewNotes: c1.notes,
  qualityReviewRounds: c2.rounds,
  qualityReviewNotes: c2.notes,
  agentsSpawned: spawned,
}
