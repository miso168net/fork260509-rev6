// ─────────────────── 主流程（serial；單一骨架：implementer 支數＝IMPLEMENTERS、逐支 prompt 由 _prompts 段的 IMPL_STAGES 供；0 支＝續跑形、直入審查段） ───────────────────
// IMPL_STAGES＝[{ label, phase, prompt(reports) }, …]：label 必含 implementer 字樣（harness 樁與看門狗冒煙皆以此辨識）；
//   prompt 收前面各支的 report 陣列（首支得空陣列、第 i 支得 i−1 份、原文轉交）；支數與 IMPLEMENTERS 自我斷言（保險絲推導同源、RL-0062）。
//   ★續跑形（RL-0010：需某階段重跑＝新開一支只跑該階段的 workflow、新 runId）：IMPLEMENTERS=0、IMPL_STAGES=[]，
//   已完成結論與勿重報清單寫進 CONTEXT；本段跳過 implementer 迴圈、直入 SpecReview→CodeQualityReview。
//   另引用 START_LOG（_vars 段）、SPEC_REVIEW_PROMPT／QUALITY_REVIEW_PROMPT／FIX_SELFCHECK（_prompts 段）。
// ★_context／_allowed 兩段常數（BL-00039①；判準同 review 形 `_sk_review.js` 首段之 CONTEXT 腿）。
//   ★為何在此段而非 `_sk_head.js`：TDD 拼接序＝vars→head→allowed→rules→context→prompts→cycle→main，head 早於此二段宣告，
//   於 head 取值會落在 const 的暫時死區（`typeof` 亦拋 ReferenceError）；main 是 TDD 形最後一段、且早於任何 spawn，零派發性質不變。
//   ★破口：ALLOWED_BLOCK 空值不會被 guard 攔（prompt 其餘段落已足 400 字元且含 zh-TW／冒煙 token／RULES-VERSION），
//   fix agent 遂拿到沒有允許清單的 prompt、六件套⑥ 空間邊界靜默失效；續跑形（IMPLEMENTERS=0）更晚到 fix 輪才可能顯形。
if (typeof CONTEXT !== 'string' || CONTEXT.length < 80 || !CONTEXT.includes(SMOKE) || !CONTEXT.includes('zh-TW')) {
  throw new Error('防呆②：CONTEXT 須為 ≥80 字元字串且含冒煙 token 與 zh-TW 字面（_context 段；RL-0018）')
}
if (typeof ALLOWED_BLOCK !== 'string' || ALLOWED_BLOCK.length < 40) {
  throw new Error('防呆②：ALLOWED_BLOCK 須為 ≥40 字元字串（_allowed 段；fix agent 允許檔案清單＝防呆六件套⑥ 空間邊界）')
}
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
  const r = await spawn([DEEP_THINK, st.prompt(reportsSoFar())].join('\n'), Object.assign({ label: st.label, phase: st.phase, schema: WORK_SCHEMA }, IMPL_OPTS))
  if (!r) return { unit: UNIT, status: 'failed', stage: st.phase, reason: who + ' 回傳 null（終止型故障）', implReports: reportsSoFar(), agentsSpawned: spawned }
  if (r.status === 'blocked') {
    return { unit: UNIT, status: 'blocked', stage: st.phase, reason: who + ' 受阻', report: r.report, escalations: r.escalations || [], implReports: reportsSoFar(), agentsSpawned: spawned }
  }
  impls.push(r)
  log(who + ' 完成（status=' + r.status + '、改檔 ' + (r.filesChanged || []).length + ' 支）' + (i + 1 < IMPL_STAGES.length ? '→ 進下一支 implementer' : '→ 進規格對照審查'))
}
if (IMPL_STAGES.length === 0) log(START_LOG)

phase('SpecReview')
const c1 = await cycle('SpecReview', SPEC_REVIEW_PROMPT, 'spec')
if (!c1.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'SpecReview', reason: c1.reason, blockers: c1.blockers, rejected: c1.rejected, escalations: c1.escalations || [], escalatedBlockers: c1.escalated || [], implReports: reportsSoFar(), agentsSpawned: spawned }
}
log('規格對照審查收斂（' + c1.rounds + ' 輪' + ((c1.escalated || []).length ? '、' + c1.escalated.length + ' 項清單外升級主線〔RL-0025〕' : '') + '）→ 進碼品質審查')

phase('CodeQualityReview')
const c2 = await cycle('CodeQualityReview', QUALITY_REVIEW_PROMPT, 'quality')
if (!c2.converged) {
  return { unit: UNIT, status: 'unresolved', stage: 'CodeQualityReview', reason: c2.reason, blockers: c2.blockers, rejected: c2.rejected, escalations: (c1.escalations || []).concat(c2.escalations || []), escalatedBlockers: (c1.escalated || []).concat(c2.escalated || []), implReports: reportsSoFar(), specNotes: c1.notes, agentsSpawned: spawned }
}

return {
  unit: UNIT,
  status: 'ok',
  implStatuses: impls.map(function (x) { return x.status }),
  implReports: reportsSoFar(),
  filesChanged: impls.reduce(function (a, x) { return a.concat(x.filesChanged || []) }, []),
  escalations: impls.reduce(function (a, x) { return a.concat(x.escalations || []) }, []).concat(c1.escalations || [], c2.escalations || []),
  // ★RL-0025／ADR-00013：兩審查段中「成立但落允許清單外、零改動升級」的 blockers（主線收尾 commit 處理）；escalatedStages 標出處。
  escalatedBlockers: (c1.escalated || []).concat(c2.escalated || []),
  escalatedStages: [].concat((c1.escalated || []).length ? ['SpecReview'] : [], (c2.escalated || []).length ? ['CodeQualityReview'] : []),
  specReviewRounds: c1.rounds,
  specReviewNotes: c1.notes,
  qualityReviewRounds: c2.rounds,
  qualityReviewNotes: c2.notes,
  agentsSpawned: spawned,
}
