# Specification Quality Checklist: 003 auth 域整批——真登入、會話生命週期、節流＋驗證碼、dynamic 選單、i18n 轉譯

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-08
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`
- 驗證紀錄（2026-09-08、specify 自驗一輪即全過）：判定原則承 001／002 前例——本刀 stakeholder＝admin 後台使用者與 workspace 維護者（技術身分即業主身分）；
  spec 中的端點路徑（`/auth/login` 等）、碼（1000／2222／3333／7777／8888／4040）、casbin 座標、★軌道名與用途識別符、閘與工具名、`AppState` 欄數、`MSG_KEYS` 鍵數，
  係交付物座標（WHAT）與治理設施引用，非實作技術選型（HOW）；「容器內 serial」「cargo test 形」「pnpm typecheck」等屬憲法與 CLAUDE.md 既定紀律引用；
  六支新依賴之版本號出現於 Assumptions 係「釘版紀律」交付要求（全域版本紀律雙源核對）、非本 spec 選型拍板——選型早由「高度參照 rev5」拍定。
- brainstorm §5 列出的七個 clarify 候選（①三分碼措辭 ②跨端閘雙向形 ③`zh-tw.ts` 檔頭標記 ④走查工具 rc 語意 ⑤`AppState` 五欄欄集 ⑥六支依賴釘版 ⑦dev 模式 base URL 來源）
  皆已在 spec 以研判預設寫入 FR／Assumptions／Edge Cases、零 [NEEDS CLARIFICATION] 標記（承 002 前例、避免雙權威）；`/speckit-clarify` 可就此逐項確認或翻案、一題一問。
- 「零 migration」係硬預期（Q2；FR-002／Key Entities 皆據 001 基線）；clarify／plan 若冒 DDL＝範圍拍板翻案（BL-00042 觸發）＋RUNBOOK §10 三步。
- ★軌道逐處登記表之風險等級以 2026-09-08 對 base-web worktree（＝upstream `example` tip）實測 commit 數覆算（判準寫在表前、可重跑）；處數為估值、實作期以 `rev6-inline` 標記實數為準。
- 一項對 brainstorm §2 括號內用途標籤的精確化（工程判斷、非翻案）：`BASE-WEB-AUTH-WIRING` 三用途＝(a) constant routes 合併／(b) 三表單 stub／(c) captcha hook；auth store 的 login 簽名改動屬
  `BASE-WEB-LOGIN-CAPTCHA-WIRING(i)`——用途數（八）與檔案集與 brainstorm 一致、只是歸屬標籤對齊 rev5 已驗證形。
- brainstorm Q1～Q10 之 user 拍板不重述為 Clarifications 節（該節留給 `/speckit-clarify`）；其中改變 wire 行為者（Q9 島 B 翻轉不追溯）已落 FR-005／FR-031 與 US3 場景 3。
