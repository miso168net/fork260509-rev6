// ─────────────────── review 形主流程（BL-00006 入庫；承 000-r1 四支 run 的可重用件：lens／兩鏡三態／grader／critic） ───────────────────
// 與 TDD 形共用 _sk_head.js（guard／spawn／保險絲／模型家）與 _sk_rules.js（RULES_REVIEW 整塊烤入每支 prompt）；本段只管 review 形的 prompt 組法、派發與三態聚合。
// ★引用模板常數（組裝時由變動段供、缺之即 throw）：
//   _vars：UNIT／FEATURE／SMOKE／START_LOG／REVIEW_STAGE（'explore'｜'verify'）／FINDING_CATEGORIES（非空陣列＝finding.category 枚舉）／INLINE_VERIFY（explore 專用布林）
//   _plan（置於 head 之前、保險絲據此推導）：
//     explore：LENSES＝[{ key, task }]（task＝該 lens 的任務段、純字串）；PROBES＝[{ key, task }]（冷啟動探針：★刻意不烤 CONTEXT、task 自帶冒煙 token 與 zh-TW 字面）
//     verify ：BATCHES＝[{ batch, ids, text }]（text＝主線合併去重後渲染的 findings 塊、每筆首行 `■ <id>｜…`）；PROBES＝[{ key, answers }]（探針作答紀錄原文）；CRITIC＝null｜{ scope, prior }
//   _context：CONTEXT（身分／對象 SHA／範圍／日期；★含冒煙 token 與 zh-TW）；DECISIONS_BLOCK（拍板紀錄清單、R-decided 鏡與 lens 報前必查；可為空字串）
// 三態存活規則（000-r1 計畫 §4.5、報告 §0）：兩鏡皆「確認」→confirmed；任一「駁回」→refuted；其餘（含不確定／缺答／null）→uncertain、主線親裁。
//   ★null／agentStatus=failed 不殺 run（同 ADR-00013 精神）：記入 nulls／failed、其餘照跑，status 回 partial 由主線判。
// ★UNIT／FEATURE／START_LOG 之型別＋非空斷言已上提 `_sk_head.js`（兩形共用；BL-00039① 同批）——此處不再重複。
if (typeof CONTEXT !== 'string' || CONTEXT.length < 80 || !CONTEXT.includes(SMOKE) || !CONTEXT.includes('zh-TW')) {
  throw new Error('防呆②：CONTEXT 須為 ≥80 字元字串且含冒煙 token 與 zh-TW 字面（RL-0018）')
}
if (typeof DECISIONS_BLOCK !== 'string') throw new Error('防呆②：DECISIONS_BLOCK 須為字串（可為空）')
if (!Array.isArray(FINDING_CATEGORIES) || FINDING_CATEGORIES.length === 0 || !FINDING_CATEGORIES.every(function (c) { return typeof c === 'string' && c.length > 0 })) {
  throw new Error('防呆②：FINDING_CATEGORIES 須為非空字串陣列（finding.category 枚舉）')
}
const REVIEW_INLINE = REVIEW_STAGE === 'explore' && typeof INLINE_VERIFY !== 'undefined' && INLINE_VERIFY === true
function assertKeys(list, name, fields) {
  if (!Array.isArray(list)) throw new Error('防呆①：' + name + ' 須為陣列')
  const seen = new Set()
  list.forEach(function (x, i) {
    if (!x || typeof x !== 'object') throw new Error('防呆①：' + name + '[' + i + '] 非物件')
    fields.forEach(function (f) {
      if (typeof x[f] !== 'string' || x[f].length === 0) throw new Error('防呆①：' + name + '[' + i + '].' + f + ' 須為非空字串')
    })
    const k = x.key !== undefined ? x.key : x.batch
    if (/[｜\s]/.test(k)) throw new Error('防呆①：' + name + '[' + i + '] 鍵含空白或「｜」（鍵是渲染與比對面）')
    if (seen.has(k)) throw new Error('防呆①：' + name + ' 鍵重複 ' + k)
    seen.add(k)
  })
}
if (REVIEW_STAGE === 'explore') {
  assertKeys(LENSES, 'LENSES', ['key', 'task'])
  assertKeys(typeof PROBES === 'undefined' ? [] : PROBES, 'PROBES', ['key', 'task'])
  if (LENSES.length === 0) throw new Error('防呆①：explore 形至少一支 lens')
} else {
  assertKeys(BATCHES, 'BATCHES', ['batch', 'text'])
  BATCHES.forEach(function (b, i) {
    if (!Array.isArray(b.ids) || b.ids.length === 0 || b.ids.length > 8) throw new Error('防呆①：BATCHES[' + i + '].ids 須為 1～8 個 finding id（批太大＝鏡的判準被稀釋）')
    b.ids.forEach(function (id) { if (!b.text.includes('■ ' + id + '｜')) throw new Error('防呆①：BATCHES[' + i + '] text 缺 id ' + id + ' 的首行「■ ' + id + '｜」') })
  })
  { const all = BATCHES.reduce(function (a, b) { return a.concat(b.ids) }, []); if (new Set(all).size !== all.length) throw new Error('防呆①：批間 finding id 重疊') }
  assertKeys(typeof PROBES === 'undefined' ? [] : PROBES, 'PROBES', ['key', 'answers'])
  if (typeof CRITIC !== 'undefined' && CRITIC !== null && (typeof CRITIC !== 'object' || typeof CRITIC.scope !== 'string' || typeof CRITIC.prior !== 'string')) {
    throw new Error('防呆①：CRITIC 須為 null 或 { scope, prior } 兩字串')
  }
}
const REVIEW_PROBES = typeof PROBES === 'undefined' ? [] : PROBES

// ── 共用烤入塊（000-r1 通用段原樣入庫；只放「怎麼審」、不放刀事實——刀事實住 CONTEXT／DECISIONS_BLOCK） ──
const READONLY_BLOCK = [
  '=== 唯讀邊界（違反即本輪作廢；RL-0043／RL-0064）===',
  '- 你只讀不寫：不得建立、修改、刪除任何檔案；禁用 Edit／Write／NotebookEdit 工具；Bash 禁止一切寫入形：重導向 >、>>、tee、sed -i、mkdir、rm、mv、cp、touch、chmod、ln。',
  '- 禁止：任何 docker 命令；bash tools/bootstrap.sh；python3 tools/docsync generate（會重寫 docs/generated）；以 node 執行任何 script（node --check 除外）；npm／pnpm／cargo；git 的寫入形（add／commit／checkout／switch／stash／reset／merge／rebase／submodule／worktree／fetch／pull／push／config）。',
  '- ../fork260509-rev5/ 是可寫的真工作樹、無物理保護：只准 Read／Grep／Glob／cat／diff，絕不寫入、絕不對它做任何 git 操作。',
  '- 允許：Read／Grep／Glob 工具；Bash 只准 cat、head、tail、sed -n、grep、rg、find、ls、wc、diff、stat、sort、uniq、cut、awk（不輸出到檔）、python3 -c／python3 - <<\'EOF\'（只讀、不得 open(…,\'w\')／不得寫檔）、git log／show／ls-tree／ls-files／diff／rev-parse／status／branch --show-current、python3 tools/docsync lint、python3 tools/docsync check、python3 tools/docsync errata、python3 tools/docsync rules emit。',
  '- 不確定某命令是否唯讀→不要跑，改用 Read。findings／verdicts 只放回傳訊息（RL-0043）。',
].join('\n')
const EVIDENCE_BLOCK = [
  '=== 取證紀律 ===',
  '- 每筆 finding 必附可重跑的證據：evidence.command＝在 repo 根可直接執行的唯讀命令；evidence.output＝該命令實際輸出的關鍵摘錄（RL-0033）。不採信文件自述，實跑或實讀取證。',
  '- locator＝標題（如「§4.3」「## 名詞」）或行號（file:line）；summary＝一句話缺陷陳述、可作結構化比較鍵（不要寫成段落、不含證據細節）。',
  '- severity：blocker＝會讓新 session 做錯事（錯誤命令、錯誤方向判讀）或機器閘宣稱守而未守；major＝事實錯、無家、失效引用、鏡像含可漂移值；minor＝可讀性、風格、建議。',
  '- confidence 0～1＝你對「這是真缺陷」的把握，誠實填。',
].join('\n')
const DECIDED_RULE_BLOCK = [
  '=== 報前必查拍板紀錄（已拍板者不是缺陷）===',
  '凡查到現況是某拍板的結果：不列為缺陷，改在該筆填 already_decided_by（引用處）並把 proposed.disposition 設為 none；但若文件與該拍板相矛盾，仍列 finding。',
  '處置合規（RL-0073 三分流）：修＝允許直改的現在式面小修；BL＝衍生工作（需新能力面／schema／事件欄／新閘者一律 BL 或 ADR、不得為「修」）；ADR＝需拍板或 won\'t-fix；none＝已拍板。史料面（docs/brainstorms、docs/reviews、specs）本身不改、只能在現在式面加指針。',
].join('\n')
const FINDINGS_OUT = [
  '=== 回傳 ===',
  '以 StructuredOutput 回傳（schema 由工具提供）：agentStatus 只表「你自身能否完成本 lens 的審查」——有 finding 仍是 ok；只有讀不到必要檔、工具失效、被迫中止才是 failed（在 notes 說明）。',
  'findings 可為空陣列（附 notes 說明你查了什麼、為何零）。coverage.files_read＝你實際讀過的檔（相對路徑）、commands_run＝你實際跑過的命令（原文）——完整性 critic 據此找「從未被讀過的檔」。',
].join('\n')
const PROBE_OUT = [
  '=== 回傳 ===',
  '以 StructuredOutput 回傳：answers 每題一元素（question 抄原文、answer、path＝你依序開的檔、hops＝開檔次數、found、confidence、ambiguity／dead_ends／suggestion 選填）；agentStatus 只表你自身能否完成。',
].join('\n')
const VERDICT_OUT = [
  '=== 回傳 ===',
  'VERDICT schema：agentStatus 只表你自身能否完成（有駁回仍是 ok）；lens 填你的鏡名；verdicts 每筆一元素、key＝finding 的鍵（每筆首行「■ <鍵>｜」；逐筆都要、不得漏）；verdict 三態＝確認／駁回／不確定；reason 一句；evidence＝你的命令＋輸出摘錄（不確定亦要說明缺什麼）。不得為了省事把不確定寫成確認或駁回。',
].join('\n')
const GRADE_OUT = [
  '=== 回傳 ===',
  'GRADE schema：grades 每題一元素（question 抄原文、verdict 四值＝找得到／繞路／找不到／答錯、truth、truth_path、min_hops、note）；findings 依 FINDING 形（file／locator／summary／category／severity／evidence／proposed／confidence）、只報文件面缺口（入口表缺列、指針缺席或指錯、文件互相矛盾、真源座標缺席）、不報探針個人失誤；agentStatus 只表你自身能否完成。',
].join('\n')
const CRITIC_OUT = [
  '=== 回傳 ===',
  'CRITIC schema：gaps 每筆 { what（漏了什麼）, why（為何該查）, lens_prompt_hint（補漏 lens 的任務句） }；unverified＝仍未被任何證據覆蓋的宣稱清單；agentStatus 只表你自身能否完成。',
].join('\n')

// ── schema（agentStatus 一律「只表自身」；finding.category 枚舉＝FINDING_CATEGORIES） ──
const FINDING_ITEM = {
  type: 'object', additionalProperties: false,
  required: ['file', 'locator', 'summary', 'category', 'severity', 'evidence', 'proposed', 'confidence'],
  properties: {
    file: { type: 'string' }, locator: { type: 'string' }, summary: { type: 'string', description: '一句話缺陷陳述＝結構化比較鍵' },
    category: { type: 'string', enum: FINDING_CATEGORIES }, severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
    evidence: { type: 'object', additionalProperties: false, required: ['command', 'output'], properties: { command: { type: 'string' }, output: { type: 'string' } } },
    proposed: { type: 'object', additionalProperties: false, required: ['disposition', 'fix'], properties: { disposition: { type: 'string', enum: ['修', 'BL', 'ADR', 'none'] }, fix: { type: 'string' } } },
    already_decided_by: { type: 'string' }, confidence: { type: 'number', minimum: 0, maximum: 1 },
  },
}
const FINDINGS_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['agentStatus', 'lens', 'findings', 'coverage'],
  properties: {
    agentStatus: { type: 'string', enum: ['ok', 'failed'] }, lens: { type: 'string' },
    findings: { type: 'array', items: FINDING_ITEM },
    coverage: { type: 'object', additionalProperties: false, required: ['files_read', 'commands_run'], properties: { files_read: { type: 'array', items: { type: 'string' } }, commands_run: { type: 'array', items: { type: 'string' } } } },
    notes: { type: 'string' },
  },
}
const PROBE_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['agentStatus', 'answers'],
  properties: {
    agentStatus: { type: 'string', enum: ['ok', 'failed'] },
    answers: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['question', 'answer', 'path', 'hops', 'found', 'confidence'],
      properties: { question: { type: 'string' }, answer: { type: 'string' }, path: { type: 'array', items: { type: 'string' } }, hops: { type: 'integer', minimum: 0 }, found: { type: 'boolean' }, confidence: { type: 'number', minimum: 0, maximum: 1 }, ambiguity: { type: 'string' }, dead_ends: { type: 'array', items: { type: 'string' } }, suggestion: { type: 'string' } } } },
    overall_notes: { type: 'string' },
  },
}
const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['agentStatus', 'lens', 'verdicts'],
  properties: {
    agentStatus: { type: 'string', enum: ['ok', 'failed'] }, lens: { type: 'string' },
    verdicts: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['key', 'verdict', 'reason', 'evidence'],
      properties: { key: { type: 'string' }, verdict: { type: 'string', enum: ['確認', '駁回', '不確定'] }, reason: { type: 'string' }, evidence: { type: 'string' },
        already_decided_by: { type: 'string' }, contradicts_decision: { type: 'boolean' },
        severity_override: { type: 'string', enum: ['blocker', 'major', 'minor'] }, disposition_override: { type: 'string', enum: ['修', 'BL', 'ADR', 'none'] } } } },
    notes: { type: 'string' },
  },
}
const GRADE_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['agentStatus', 'grades', 'findings'],
  properties: {
    agentStatus: { type: 'string', enum: ['ok', 'failed'] },
    grades: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['question', 'verdict', 'truth', 'truth_path', 'min_hops'],
      properties: { question: { type: 'string' }, verdict: { type: 'string', enum: ['找得到', '繞路', '找不到', '答錯'] }, truth: { type: 'string' }, truth_path: { type: 'array', items: { type: 'string' } }, min_hops: { type: 'integer', minimum: 0 }, note: { type: 'string' } } } },
    findings: { type: 'array', items: FINDING_ITEM }, notes: { type: 'string' },
  },
}
const CRITIC_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['agentStatus', 'gaps', 'unverified'],
  properties: {
    agentStatus: { type: 'string', enum: ['ok', 'failed'] },
    gaps: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['what', 'why', 'lens_prompt_hint'], properties: { what: { type: 'string' }, why: { type: 'string' }, lens_prompt_hint: { type: 'string' } } } },
    unverified: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' },
  },
}

// ── 渲染與 prompt 組法 ──
function clip(s, n) { s = String(s === undefined ? '' : s); return s.length > n ? s.slice(0, n) + '…（節錄、原長 ' + s.length + ' 字）' : s }
function lensKeys(prefix, n) { return Array.from({ length: n }, function (_, i) { return prefix + '-' + (i + 1) }) }
function probeKeys(prefix, n) { return Array.from({ length: n }, function (_, i) { return prefix + '-P' + (i + 1) }) }
// ★渲染鍵與聚合鍵同源（keys 陣列）——鍵形一改只改 lensKeys／probeKeys 兩處。
function renderFindings(findings, keys) {
  return findings.map(function (f, i) {
    const key = keys[i]
    const lines = ['■ ' + key + '｜' + f.severity + '｜' + f.category, '  file: ' + f.file, '  locator: ' + f.locator, '  summary: ' + f.summary,
      '  evidence command: ' + f.evidence.command, '  evidence output: ' + clip(f.evidence.output, 1500),
      '  proposed: ' + f.proposed.disposition + '｜' + f.proposed.fix]
    if (f.already_decided_by) lines.push('  already_decided_by（探索 agent 自填）: ' + f.already_decided_by)
    lines.push('  confidence: ' + f.confidence)
    return lines.join('\n')
  }).join('\n\n')
}
function renderAnswers(key, r) {
  const lines = ['=== 探針 ' + key + ' 作答紀錄（overall_notes：' + (r.overall_notes || '') + '）===']
  ;(r.answers || []).forEach(function (a, i) {
    lines.push('Q' + (i + 1) + ': ' + a.question + '\n  answer: ' + a.answer + '\n  path: ' + JSON.stringify(a.path) + '\n  hops: ' + a.hops + '｜found: ' + a.found + '｜confidence: ' + a.confidence + '\n  ambiguity: ' + (a.ambiguity || '') + '\n  dead_ends: ' + JSON.stringify(a.dead_ends || []) + '\n  suggestion: ' + (a.suggestion || ''))
  })
  return lines.join('\n')
}
function who(role, key) { return '你是 ' + FEATURE + ' 之 **' + UNIT + '** review 輪的 **' + role + '（' + key + '）**（唯讀）。' }
function lensPrompt(l) {
  return [DEEP_THINK, who('探索 lens', l.key), '', CONTEXT, '', READONLY_BLOCK, '', EVIDENCE_BLOCK, '', DECIDED_RULE_BLOCK, DECISIONS_BLOCK, '', '=== 本 lens 任務 ===', l.task, '', FINDINGS_OUT, '', RULES_REVIEW].join('\n')
}
function probePrompt(p) {
  // 冷啟動探針：刻意不烤 CONTEXT（模擬只有 repo 內容的新 session）；task 自帶身分、冒煙 token、zh-TW 與題目。
  return [DEEP_THINK, p.task, '', READONLY_BLOCK, '', PROBE_OUT, '', RULES_REVIEW].join('\n')
}
function mirrorRealPrompt(key, text) {
  return [DEEP_THINK, who('對抗驗證 agent、R-real 鏡', key), '', CONTEXT, '', READONLY_BLOCK, '',
    '=== 任務：R-real 鏡——逐筆重現證據、只看真偽 ===',
    '對每筆獨立判：1. 在本工作樹重跑 evidence.command（只准唯讀形；含寫入形則改等價唯讀命令並註明）；輸出是否與 evidence.output 相符？',
    '2. file／locator 指對否；summary 的斷言是否被證據**充分**支持（要「就是這樣」、不是「有點像」）；嚴重度是否誇大或低估（blocker＝會讓新 session 做錯事或閘宣稱守而未守；major＝事實錯／無家／失效引用／鏡像含可漂移值；minor＝可讀性、風格）。',
    '3. 票：確認＝證據重現且斷言成立；駁回＝重現失敗、斷言不成立、或斷言與證據脫節（附反證命令與輸出）；不確定＝需要取不到的資訊或判準本身模糊（說明缺什麼）。',
    '4. severity_override 只在有明確理由時填；不評「該不該修」、不查拍板紀錄（那是另一鏡的事）。',
    '', '=== 本批 findings ===', text, '', VERDICT_OUT, '', RULES_REVIEW].join('\n')
}
function mirrorDecidedPrompt(key, text) {
  return [DEEP_THINK, who('對抗驗證 agent、R-decided 鏡', key), '', CONTEXT, '', READONLY_BLOCK, '', DECIDED_RULE_BLOCK, DECISIONS_BLOCK, '',
    '=== 任務：R-decided 鏡——逐筆查拍板紀錄與處置合規、不重跑證據 ===',
    '對每筆獨立判：1. 現況是否為某拍板的結果（含刻意的設計取捨）？逐筆查拍板紀錄；找到→票「駁回」並填 already_decided_by（檔＋節＋一句）；若文件與該拍板相矛盾→票「確認」並 contradicts_decision=true。',
    '2. proposed.disposition 是否合規（見上段處置合規）；不合規→disposition_override 填正確桶（修／BL／ADR／none）並在 reason 說明。',
    '3. 票：確認＝未拍板且屬真缺陷候選（處置桶可能需要 override）；駁回＝已拍板或屬明載的設計取捨；不確定＝拍板紀錄語意模糊、無法判定（說明何處模糊）。可讀檔核 summary 描述是否準確，但不重跑證據命令（那是另一鏡的事）。',
    '', '=== 本批 findings ===', text, '', VERDICT_OUT, '', RULES_REVIEW].join('\n')
}
function graderPrompt(key, answersText) {
  return [DEEP_THINK, who('探針評分 grader', key), '', CONTEXT, '', READONLY_BLOCK, '', DECIDED_RULE_BLOCK, DECISIONS_BLOCK, '',
    '=== 任務：探針評分 ===',
    '以下是一支「只有 repo 內容」的新 session（探針）對數題的作答紀錄。對每題：1. 你自己獨立找真相（唯讀），記你的最短路徑 truth_path（依序開檔）與 min_hops（開檔次數）；',
    '2. 判 verdict：找得到（探針 ≤3 跳且答對）／繞路（>3 跳但答對）／找不到（探針 found=false 或答不出）／答錯（答案與真相不符；說明哪裡錯）；',
    '3. 探針的 suggestion 逐條評：採納→寫成 finding；不採納→在 note 說理由；4. findings 只報文件面缺口、每筆附可重跑的唯讀證據命令與輸出摘錄。',
    '', answersText, '', GRADE_OUT, '', RULES_REVIEW].join('\n')
}
function refutePrompt(key, text) {
  return [DEEP_THINK, who('對抗驗證 agent、R-decided 鏡（探針衍生）', key), '', CONTEXT, '', READONLY_BLOCK, '', DECIDED_RULE_BLOCK, DECISIONS_BLOCK, '',
    '=== 任務：探針衍生 findings 反證 ===',
    '以下 findings 由探針評分 grader 提出。對每筆獨立判：1. 是否已有拍板／既有入口覆蓋（例：README 表已有列但探針沒看到＝探針失誤、非文件缺口→駁回並填 already_decided_by 或既有入口位置）；',
    '2. 證據命令重跑一次（唯讀）確認「缺列／矛盾」為真；3. 處置合規；不合規→disposition_override。票：確認／駁回／不確定，逐筆都要。',
    '', '=== 本批 findings ===', text, '', VERDICT_OUT, '', RULES_REVIEW].join('\n')
}
function criticPrompt(scope, prior, lines) {
  return [DEEP_THINK, who('完整性 critic', 'critic'), '', CONTEXT, '', READONLY_BLOCK, '',
    '=== 任務：找「還漏了什麼」===',
    '你不重審個別 finding，只回答：①範圍內從未被任何 lens 讀過的檔（掃描面 vs 各 lens coverage.files_read 聯集）；②仍未被證據覆蓋的宣稱；③該補哪些 lens（各給一句任務提示）。',
    '', '=== 範圍與前次結果 ===', scope, '', prior, '', '=== 本 run 驗證結果（批｜鍵｜real 票｜decided 票｜三態）===', lines.join('\n'), '', CRITIC_OUT, '', RULES_REVIEW].join('\n')
}

// ── 三態聚合（結構化、供主線三分流；不靠自由文字） ──
function finalVerdict(rv, dv) {
  if (rv === '確認' && dv === '確認') return 'confirmed'
  if (rv === '駁回' || dv === '駁回') return 'refuted'
  return 'uncertain'
}
function singleVerdict(v) { return v === '確認' ? 'confirmed' : (v === '駁回' ? 'refuted' : 'uncertain') }
function indexVerdicts(res) {
  const m = {}
  ;((res && res.verdicts) || []).forEach(function (v) { m[v.key] = v })
  return m
}
function verdictTable(keys, real, decided) {
  const rv = indexVerdicts(real)
  const dv = indexVerdicts(decided)
  return keys.map(function (k) {
    const r = rv[k] || {}
    const d = dv[k] || {}
    return { key: k, real: r.verdict || '缺', decided: d.verdict || '缺', final: finalVerdict(r.verdict, d.verdict),
      reason_real: r.reason || '', reason_decided: d.reason || '', already_decided_by: d.already_decided_by || r.already_decided_by || '',
      contradicts_decision: !!d.contradicts_decision, severity_override: d.severity_override || r.severity_override || '', disposition_override: d.disposition_override || '' }
  })
}
function singleTable(keys, res) {
  const v = indexVerdicts(res)
  return keys.map(function (k) { const x = v[k] || {}; return { key: k, real: '—', decided: x.verdict || '缺', final: singleVerdict(x.verdict), reason_real: '', reason_decided: x.reason || '', already_decided_by: x.already_decided_by || '', contradicts_decision: !!x.contradicts_decision, severity_override: x.severity_override || '', disposition_override: x.disposition_override || '' } })
}

const nulls = []
const failed = []
function note(label, res) {
  if (res === null || res === undefined) { nulls.push(label); return false }
  if (res.agentStatus === 'failed') { failed.push(label); return false }
  return true
}
async function twoMirrors(key, keys, text, phaseName) {
  const pair = await parallel([
    function () { return spawn(mirrorRealPrompt(key, text), Object.assign({ label: 'real:' + key, phase: phaseName, schema: VERDICT_SCHEMA }, MIRROR_OPTS)) },
    function () { return spawn(mirrorDecidedPrompt(key, text), Object.assign({ label: 'decided:' + key, phase: phaseName, schema: VERDICT_SCHEMA }, MIRROR_OPTS)) },
  ])
  const real = pair[0] === undefined ? null : pair[0]
  const decided = pair[1] === undefined ? null : pair[1]
  note('real:' + key, real)
  note('decided:' + key, decided)
  return { real: real, decided: decided, verdicts: verdictTable(keys, real, decided) }
}
async function gradeProbe(key, answersText, phaseName) {
  const grade = await spawn(graderPrompt(key, answersText), Object.assign({ label: 'grader:' + key, phase: phaseName, schema: GRADE_SCHEMA }, GRADER_OPTS))
  const out = { grade: grade === undefined ? null : grade, refute: null, verdicts: [] }
  if (!note('grader:' + key, out.grade)) return out
  const fs = out.grade.findings || []
  if (fs.length === 0) { log('探針 ' + key + '：grader 零 findings、跳過 refuter'); return out }
  const keys = probeKeys(key, fs.length)
  const rf = await spawn(refutePrompt(key, renderFindings(fs, keys)), Object.assign({ label: 'refute:' + key, phase: phaseName, schema: VERDICT_SCHEMA }, MIRROR_OPTS))
  out.refute = rf === undefined ? null : rf
  note('refute:' + key, out.refute)
  out.verdicts = singleTable(keys, out.refute)
  return out
}
function tally(tables) {
  const s = { findings: 0, confirmed: 0, refuted: 0, uncertain: 0 }
  tables.forEach(function (t) { (t || []).forEach(function (v) { s.findings += 1; s[v.final] += 1 }) })
  return s
}

let result
if (REVIEW_STAGE === 'explore') {
  phase('探索')
  log(START_LOG)
  const lensJob = function () {
    return pipeline(LENSES,
      function (l) { return spawn(lensPrompt(l), Object.assign({ label: 'lens:' + l.key, phase: '探索', schema: FINDINGS_SCHEMA }, LENS_OPTS)).then(function (r) { return { key: l.key, result: r === undefined ? null : r, verify: null } }) },
      async function (o) {
        if (!note('lens:' + o.key, o.result)) return o
        const fs = o.result.findings || []
        if (REVIEW_INLINE && fs.length > 0) {
          const keys = lensKeys(o.key, fs.length)
          o.verify = await twoMirrors(o.key, keys, renderFindings(fs, keys), '探索驗證')
        } else if (REVIEW_INLINE) log('lens ' + o.key + '：零 findings、跳過兩鏡')
        return o
      })
  }
  const probeJob = function () {
    return pipeline(REVIEW_PROBES,
      function (p) { return spawn(probePrompt(p), Object.assign({ label: 'probe:' + p.key, phase: '探索', schema: PROBE_SCHEMA }, LENS_OPTS)).then(function (r) { return { key: p.key, result: r === undefined ? null : r, grade: null, refute: null, verdicts: [] } }) },
      async function (o) {
        if (!note('probe:' + o.key, o.result)) return o
        if (REVIEW_INLINE) Object.assign(o, await gradeProbe(o.key, renderAnswers(o.key, o.result), '探索驗證'))
        return o
      })
  }
  const both = await parallel([lensJob, probeJob])
  const lenses = (both[0] || []).map(function (o, i) { return o || { key: LENSES[i].key, result: null, verify: null } })
  const probes = (both[1] || []).map(function (o, i) { return o || { key: REVIEW_PROBES[i].key, result: null, grade: null, refute: null, verdicts: [] } })
  lenses.forEach(function (o) { if (o.result === null && nulls.indexOf('lens:' + o.key) < 0 && failed.indexOf('lens:' + o.key) < 0) nulls.push('lens:' + o.key) })
  probes.forEach(function (o) { if (o.result === null && nulls.indexOf('probe:' + o.key) < 0 && failed.indexOf('probe:' + o.key) < 0) nulls.push('probe:' + o.key) })
  const summary = tally(lenses.map(function (o) { return o.verify ? o.verify.verdicts : [] }).concat(probes.map(function (o) { return o.verdicts })))
  summary.lensFindings = lenses.reduce(function (a, o) { return a + ((o.result && o.result.findings) || []).length }, 0)
  log('探索 run 完成：派 ' + spawned + ' 支、lens findings ' + summary.lensFindings + (REVIEW_INLINE ? '、三態 confirmed ' + summary.confirmed + '／refuted ' + summary.refuted + '／uncertain ' + summary.uncertain : '') + '、null ' + nulls.length + '、failed ' + failed.length)
  result = { unit: UNIT, stage: 'explore', inlineVerify: REVIEW_INLINE, lenses: lenses, probes: probes, summary: summary }
} else {
  phase('驗證')
  log(START_LOG)
  const batchJob = function () {
    return pipeline(BATCHES, async function (b) { const v = await twoMirrors(b.batch, b.ids, b.text, '驗證'); return { batch: b.batch, ids: b.ids, real: v.real, decided: v.decided, verdicts: v.verdicts } })
  }
  const probeJob = function () {
    return pipeline(REVIEW_PROBES, async function (p) { const g = await gradeProbe(p.key, p.answers, '探針評分'); return { key: p.key, grade: g.grade, refute: g.refute, verdicts: g.verdicts } })
  }
  const both = await parallel([batchJob, probeJob])
  const batches = (both[0] || []).map(function (o, i) { return o || { batch: BATCHES[i].batch, ids: BATCHES[i].ids, real: null, decided: null, verdicts: verdictTable(BATCHES[i].ids, null, null) } })
  const probes = (both[1] || []).map(function (o, i) { return o || { key: REVIEW_PROBES[i].key, grade: null, refute: null, verdicts: [] } })
  let critic = null
  if (typeof CRITIC !== 'undefined' && CRITIC !== null) {
    phase('critic')
    const lines = batches.reduce(function (a, b) { return a.concat(b.verdicts.map(function (v) { return b.batch + '｜' + v.key + '｜' + v.real + '｜' + v.decided + '｜' + v.final })) }, [])
    critic = await spawn(criticPrompt(CRITIC.scope, CRITIC.prior, lines), Object.assign({ label: 'critic', phase: 'critic', schema: CRITIC_SCHEMA }, CRITIC_OPTS))
    if (critic === undefined) critic = null
    note('critic', critic)
  }
  const summary = tally(batches.map(function (b) { return b.verdicts }).concat(probes.map(function (o) { return o.verdicts })))
  log('驗證 run 完成：派 ' + spawned + ' 支、三態 confirmed ' + summary.confirmed + '／refuted ' + summary.refuted + '／uncertain ' + summary.uncertain + '、null ' + nulls.length + '、failed ' + failed.length)
  result = { unit: UNIT, stage: 'verify', batches: batches, probes: probes, critic: critic, summary: summary }
}
result.status = (nulls.length || failed.length) ? 'partial' : 'ok'
result.smoke = SMOKE
result.nulls = nulls
result.failed = failed
result.agentsSpawned = spawned
return result
