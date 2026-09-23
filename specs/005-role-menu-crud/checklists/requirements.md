# Specification Quality Checklist: 005 role＋menu 管理 CRUD 寫端——角色與選單接真、選單域序列化、判定面同步、授權歸檔寫入面、島 H 入憲

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-23
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
- 本 spec 為 005 之第二次 specify（第一次產物之分支已由 user 改名保留作本機對照、不入帳；brainstorm 於重做前再經 grill 第二輪、十二題拍板與工程判斷 21～43 定案）。
  驗證紀錄（2026-09-23）：初稿後以唯讀查證 workflow 四鏡（brainstorm 忠實度／事實／自洽與可測性／rev5 沉默項與 BACKLOG 涵蓋）＋逐鏡對抗複核審一輪——61 筆、60 成立、1 推翻；
  已逐筆改入（要項：選單治理清單「壞形＝視同沒帶＝全取」之邊界、CDP 排除清單補 006～008 增量、`protectedMenu` 譯文改寫義務、addMenu 守門序回復 rev5 固定序並定 addRole／updateRole／updateMenu 固定序、
  停用雙護欄 self→super、`casbin_rule` 造列例外與「先種 live 授權」防恆綠、頂層 `parentId` 0↔NULL 對應、角色新增與更新可帶首頁路由名、updateRoleHome 非部分更新、id 缺席收斂 `notFound`、
  名冊守恆射程限生產區、被取代 ADR 之現在式引用改指、Given／When／Then 補齊）；改後自驗：FR-001～FR-079 連續、交叉引用全數可解、每條驗收情境皆具 When 與 Then、零 [NEEDS CLARIFICATION]、零 `tmp/` 路徑、零裸刀名。
- 判定原則承 001～004 前例：本刀 stakeholder＝admin 後台超級管理員與 workspace 維護者（技術身分即業主身分）；spec 中的端點路徑（`/systemManage/*`）、碼（`2222`／`5003`／`4040`／`5000`）、
  政策座標與 seed 列號、★ 軌道名與用途識別符、閘與工具名、msg 鍵、常數、檔名，係交付物座標（WHAT）與治理設施引用，非實作技術選型（HOW）；「容器內 serial」「前端型別檢查」屬憲法與 CLAUDE.md 既定紀律引用。
- **clarify 必問四項**（brainstorm R1-Q1）暫依 rev5 as-built 寫入並於 Assumptions 標明：①清除常量性時存常量後代是否拒（FR-021）②角色掛載計數是否濾使用者狀態（FR-014）③批次含查無 id（FR-037）④批次重複 id（FR-037）；
  `/speckit-clarify` 依專案紀律一題一問（不採內建一次三題形）。另「新增路徑名稱空字串亦拒」為 R1-Q3 之延伸（Assumptions 載明、UI 零差異），clarify 可視需要確認。
- 「零 migration、零 seed 變更」係事實（FR-002）；clarify／plan 若冒 DDL＝範圍翻案。
- ★ 軌道逐處登記表之風險等級以 2026-09-23 對 base-web upstream `example` tip `8be6f9ba` 實測 commit 數覆算（判準寫在表前、可重跑）。
- brainstorm 之 Q1～Q5、G1～G4、R1／R2 十二題之 user 拍板不重述為 Clarifications 節（該節留給 `/speckit-clarify`）；其中改變 user 可見行為者（getAllPages 提前、表頭 prop 形、治理清單無 size 全取、
  刪角色實際歸檔才同步、空字串語意、受保護選單兩腿、href 與按鈕碼形制、授權彈窗已知態、hideInMenu 釋義）已落 FR 與 US 場景。
