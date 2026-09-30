# Specification Quality Checklist: 006 授權治理——三維授權接真、結構性封死、授權回收桶、島 G 入憲

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-01
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
- 驗證紀錄（2026-10-01、主線自驗一輪）：FR-001～FR-054、SC-001～SC-014 連號且交叉引用全數可解；US1～US5 每條驗收情境皆具 When 與 Then（初稿缺 When 者十處已補）；零 [NEEDS CLARIFICATION]、零 `tmp/` 路徑；引用之 BL／LL／ADR 編號逐一核在冊。
  事實面親核（非沿用 brainstorm 轉述）：ROUTES 39＝Policy 25＋Public 11＋Authed 3、Policy 中受保護 4／可授出 21（逐條列名核對）；`MSG_KEYS` 現 43；reason gate 現為三值之 `matches!`；seed 政策 163 列（R_SUPER 147）、受保護 19 列皆屬 R_SUPER、持 R_SUPER 之帳號恰 1、`single_session_default`＝off；
  rev5 as-built：三維寫端空 diff 仍一列稽核、復原 NoOp 零稽核且不重載；rev5 回收桶頁恰 8 欄；rev5 島 G 條文之 G4＝刪除守門與批次原子、G5＝復原同實例與全端點鎖序（rev5 spec FR-051 之 G4 敘述與其憲法不符，本 spec 以憲法字面為準）；★ 軌道登記表之 commit 數以 2026-10-01 對 upstream `example` tip `8be6f9ba` 實測。
- 判定原則承 001～005 刀前例：本刀 stakeholder＝admin 後台超級管理員與 workspace 維護者（技術身分即業主身分）；spec 中的端點路徑（`/systemManage/*`）、碼（`2222`／`5003`／`4040`／`5000`）、政策座標與 seed 列號、★ 軌道名與用途識別符、閘與工具名、msg 鍵、檔名，係交付物座標（WHAT）與治理設施引用，非實作技術選型（HOW）；「容器內 serial」「前端型別檢查」屬憲法與 CLAUDE.md 既定紀律引用。
- brainstorm 之 Q1～Q17 之 user 拍板不重述為 Clarifications 節（該節留給 `/speckit-clarify`）；其中改變 user 可見行為者（候選集射程、選單／按鈕維不可復原、封死射程與 21 支可授出、並行覆蓋已知態、生效兩層時點、超管自撤與自救、全撤、復原 NoOp、回收桶兩篩、BL-00131 修法）已落 FR 與 US 場景。
- 「零 migration、零 seed 變更」係事實（FR-002）；clarify／plan 若冒 DDL＝範圍翻案。
- 憲法條文字面（島 G 各款、H2 方向句落位、G5 條文層級與島 G 標頭寫法）不在本 spec 定稿：FR-040 只定範圍與必含項，字面於 U0 由 user 逐款親決。
