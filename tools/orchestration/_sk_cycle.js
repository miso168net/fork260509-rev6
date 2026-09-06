// ★本段引用模板常數：UNIT（執行單元標籤，如 U2）、FEATURE（該刀 feature 分支長名）、CONTEXT、ALLOWED_BLOCK（_context／_allowed 段）、
//   FIX_SELFCHECK（fix 修完必跑的自驗命令一句；_prompts 段）——組裝時定義，缺之即 ReferenceError；
//   RULES_REVIEW／RULES_FIX 由 _sk_rules.js（generate 產物）供：review prompt 一律烤 RULES_REVIEW、fix prompt 一律烤 RULES_FIX（R1-080）；
//   DEEP_THINK 由 _sk_head.js 供、烤在 review／fix prompt 首行（user 拍板 2026-09-04）。
function rejectedBlock(rejected) {
  if (!rejected.length) return ''
  const lines = [
    '',
    '=== ★前輪已駁回 findings 清單（勿沿用被駁論據重報）===',
    '下列 findings 已由前輪 fix 判定不成立並附理由。**明令**：不得以同一論據重報；同一 finding 若要再報，MUST 附**新證據**（新的 grep 命中、新的碼引用、新的測試輸出），否則該報將直接計入收斂判定、視為未推進。',
  ]
  rejected.forEach(function (x, i) {
    lines.push('' + (i + 1) + '. 檔案：' + x.file)
    lines.push('   摘要：' + x.summary)
    lines.push('   駁回理由：' + x.why)
  })
  return lines.join('\n')
}

// ★RL-0025（ADR-00013）：前輪 fix 判成立、但落允許清單外而零改動升級主線的 findings——審查員勿重報（重報＝同 file×summary 者由 script 過濾、
//   不計入收斂比較、不進 fix）；主線於收尾 commit 處理。同檔若另有**新**缺陷，以新 summary 報。
function escalatedBlock(escalated) {
  if (!escalated.length) return ''
  const lines = [
    '',
    '=== ★前輪已升級主線之 findings 清單（成立、但落允許清單外；主線收尾處理、本輪勿重報）===',
    '下列 findings 已由前輪 fix 判定成立、惟修法落在本單元允許檔清單外，已依 RL-0022 零改動升級主線。**明令**：本輪不得重報（同 file×summary 之重報將被 script 過濾、不計入）；同檔另有新缺陷則以**新的 summary** 報。',
  ]
  escalated.forEach(function (x, i) {
    lines.push('' + (i + 1) + '. 檔案：' + x.file)
    lines.push('   摘要：' + x.summary)
  })
  return lines.join('\n')
}

function fixPrompt(blockers, roundNo) {
  const items = blockers.map(function (b, i) {
    return '' + (i + 1) + '. 檔案：' + b.file + '\n   缺陷：' + b.summary + '\n   證據與建議：' + b.detail
  })
  return [
    DEEP_THINK,
    '你是 ' + FEATURE + ' 之 **' + UNIT + ' 執行單元**的 **fix agent**（第 ' + roundNo + ' 輪修復）。',
    '',
    CONTEXT,
    '',
    '=== 本輪待處理 findings ===',
    items.join('\n'),
    '',
    '=== 處置紀律 ===',
    '· 逐條判斷 finding 是否**真的成立**——審查員也會出錯（★審查 prompt 末段「勿誤報」所列項是最常見的誤報源）。成立就修；**不成立就據實駁回**，放進 `rejectedFindings`（附 `file`／`summary`〔逐字沿用上面那句摘要〕／`why`）。',
    '· ★不要為了讓審查通過而做「表面修改」——那會讓下一輪重報同一問題、觸發不收斂判定。',
    '· ★**補守門一律做變異測試**：把被指的那行改壞→跑測確認會紅→還原。不做這步，補的就是另一個裝飾性守門。',
    '· 修改一律限在允許清單內。清單外需要動＝**絕不擅改**，依 status 分值升級（`done_with_escalation`＋`escalations` 逐條附修法；★零改動升級不會終止 run——該批 finding 記為已升級主線、審查段照常進行，RL-0025）。★升級的 finding MUST 同時以 `escalatedFindings` 結構化指名（`file`／`summary` 逐字沿用上面那句摘要）——script 據此讓下一輪審查不再重報；只寫在 `escalations` 自由文字＝script 看不見、次輪必重報（LL-00010）。',
    '· 修完 MUST 重跑自驗（' + FIX_SELFCHECK + '），實際輸出摘要寫進 report。',
    '',
    RULES_FIX,
    '',
    ALLOWED_BLOCK,
    '',
    '=== 回傳 ===',
    '以 StructuredOutput 回 `{status, report, filesChanged, escalations?, rejectedFindings?, escalatedFindings?}`。',
    '`filesChanged` MUST 據實填本輪**實際寫入**的檔（一個字都沒改就填空陣列——script 以連兩輪零改動作為不收斂訊號）。',
  ].join('\n')
}

async function cycle(phaseName, reviewPrompt, tag) {
  let prevKeys = null
  let emptyChangeStreak = 0
  const rejected = []
  const escalated = [] // 成立但落允許清單外、已升級主線的 blockers（RL-0025／ADR-00013）
  const escalatedKeys = new Set()
  const escalations = []
  let lastBlockers = []
  const keyOf = function (b) { return b.file + '||' + b.summary }
  for (let r = 0; r <= MAX_FIX_ROUNDS; r++) {
    const isConfirm = r === MAX_FIX_ROUNDS
    const head = isConfirm
      ? '★本輪＝**確認輪**（第 ' + (r + 1) + ' 輪、fix 迴圈已跑滿上限）：只審不修，若無 blocker 即判收斂。'
      : '★本輪＝第 ' + (r + 1) + ' 輪審查。'
    const rv = await spawn(
      [DEEP_THINK, head, '', reviewPrompt, '', RULES_REVIEW, rejectedBlock(rejected), escalatedBlock(escalated)].join('\n'),
      Object.assign({ label: tag + ':review-' + (r + 1), phase: phaseName, schema: REVIEW_SCHEMA }, REVIEW_OPTS)
    )
    if (!rv) return { converged: false, reason: 'review agent 回傳 null（終止型故障）', blockers: lastBlockers, rejected, escalated, escalations }
    if (rv.agentStatus === 'failed') {
      return { converged: false, reason: 'review agent 自陳受阻（agentStatus=failed）：' + (rv.notes || ''), blockers: lastBlockers, rejected, escalated, escalations }
    }
    // ★RL-0025：已升級主線之 blocker 被重報者過濾不計（主線收尾處理；不進 fix、不進收斂比較）。
    const blockers = (rv.blockers || []).filter(function (b) { return !escalatedKeys.has(keyOf(b)) })
    if (blockers.length === 0) return { converged: true, blockers: [], rounds: r + 1, rejected, notes: rv.notes || '', escalated, escalations }
    lastBlockers = blockers
    const keys = blockers.map(keyOf).sort().join('\n')
    if (prevKeys !== null && prevKeys === keys) {
      return { converged: false, reason: '⑤收斂偵測：連兩輪 blocker 集合（file×summary）完全相同', blockers, rejected, escalated, escalations }
    }
    prevKeys = keys
    if (isConfirm) return { converged: false, reason: '確認輪仍有 blocker', blockers, rejected, escalated, escalations }
    const fx = await spawn(
      fixPrompt(blockers, r + 1),
      Object.assign({ label: tag + ':fix-' + (r + 1), phase: phaseName, schema: WORK_SCHEMA }, FIX_OPTS)
    )
    if (!fx) return { converged: false, reason: 'fix agent 回傳 null（終止型故障）', blockers, rejected, escalated, escalations }
    if (fx.status === 'blocked') {
      return { converged: false, reason: 'fix agent blocked：' + fx.report, blockers, rejected, escalated, escalations: escalations.concat(fx.escalations || []) }
    }
    const rejNow = fx.rejectedFindings || []
    rejNow.forEach(function (x) { rejected.push(x) })
    ;(fx.escalations || []).forEach(function (e) { escalations.push(e) })
    // ★LL-00010：升級項以結構化 escalatedFindings 記入（不論本輪改動數）——部分改動＋升級時下方零改動分支不會觸發，
    //   不記則次輪審查合法重報、整輪白跑。零改動分支保留為兜底（agent 漏填 escalatedFindings 時仍成立）。
    ;(fx.escalatedFindings || []).forEach(function (e) {
      const k = keyOf(e)
      if (escalatedKeys.has(k)) return
      escalatedKeys.add(k)
      const orig = blockers.filter(function (b) { return keyOf(b) === k })[0]
      escalated.push(orig || { file: e.file, summary: e.summary, detail: '' })
    })
    const changed = (fx.filesChanged || []).length
    // ★RL-0025（承 rev5:L-078、ADR-00013 改形）：fix 因「findings 落允許清單外」而正確零改動＝該批未駁回之 blocker 已升級主線——
    //   既非不收斂、也不提前 return（原 rev5:L-078 分支＝當場 return，代價＝一項文件面缺口即終止 run、碼品質段跑不到）：
    //   記入 escalated、後續輪次過濾不計；本輪零駁回＝無事可再審→該段當場判收斂帶升級項、進下一段；有駁回＝續下一輪 review
    //   （帶已駁回清單 RL-0071）由審查員核駁回是否成立。此分支置於零改動偵測之前——零改動偵測只服務 status ok 的真空轉。
    if (fx.status === 'done_with_escalation' && changed === 0) {
      const rejKeys = new Set(rejNow.map(keyOf))
      blockers.forEach(function (b) { if (!rejKeys.has(keyOf(b)) && !escalatedKeys.has(keyOf(b))) { escalated.push(b); escalatedKeys.add(keyOf(b)) } })
      if (rejNow.length === 0) {
        return { converged: true, blockers: [], rounds: r + 1, rejected, notes: rv.notes || '', escalated, escalations, escalatedOnly: true }
      }
      continue
    }
    emptyChangeStreak = changed === 0 ? emptyChangeStreak + 1 : 0
    if (emptyChangeStreak >= 2) {
      return { converged: false, reason: '⑤收斂偵測：fix 連兩輪零改動', blockers, rejected, escalated, escalations }
    }
  }
  return { converged: false, reason: '迴圈異常結束（不應到達）', blockers: lastBlockers, rejected, escalated, escalations }
}
