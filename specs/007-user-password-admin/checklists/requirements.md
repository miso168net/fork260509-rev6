# Specification Quality Checklist: 007 使用者管理與密碼治理——使用者頁全套、斷權、密碼政策與自助改密、委派治理、繁中介面、島 I 入憲

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-05
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
- 驗證紀錄（2026-10-05、主線自驗一輪）：FR-001～FR-066、SC-001～SC-014 連號且交叉引用全數可解；US1～US6 每段 Given 皆具 When 與 Then（初稿缺者兩處已補：US4 第 3、7 條）；零 [NEEDS CLARIFICATION]、零 `tmp/` 路徑、零檔案行號引用；引用之 BL／ADR 編號逐一核在冊。
  自驗另修五處：★ 軌道表列數字面 18→19；FR-004 新拒因鍵名預設沿 `rev5:007` 名冊；FR-007 兩支清單固定序寫明；008 前無設定頁畫面＝US3 獨立測試與 SC-006 改以系統設定寫端調政策；走查角色（User 無使用者頁；角色與選單頁以自建角色帳號實測）。
- 事實面親核（非沿用 brainstorm 轉述）：seed 使用者域政策列（getUserList 授 R_SUPER 與 R_ADMIN、deleteUser 與 batchDeleteUser 為 DELETE、updateUserSessionPolicy 受保護）；`manage_user` 七碼字面（含 `user:reset-pwd`）與 R_SUPER／R_ADMIN 之按鈕列；`MSG_KEYS` 現 46；錯誤變體現 9；節流降級來源值集現恰十；稽核動作詞現五；ROUTES 現 49；IP 規則頁為 rev6 自有檔（upstream 無）；README 已改指針、不鏡像憲法版本；★ 軌道登記表之 commit 數以 2026-10-05 對 upstream `example` tip `8be6f9ba` 實測。
  ★更正 brainstorm 轉述一處：brainstorm §3 §2 之「不得含帳號名」與 rev5 as-built（大小寫不敏感**相等**、非子串）及 rev6 seed 設定說明「禁止密碼與帳號相同」不符——本 spec 以後兩者為準（FR-032、US3 第 2 條、Key Entities）；屬沿用 rev5 項之字面精確化、非新拍板。
- 判定原則承 001～006 刀前例：本刀 stakeholder＝admin 後台超級管理員、被委派之管理員、自助改密之一般使用者與 workspace 維護者；spec 中的端點路徑、碼（`2222`／`5003`／`7777`／`8888`／`1000`／`4040`／`5000`）、seed 列號與政策座標、★ 軌道名與用途識別符、閘與工具名、msg 鍵、檔名、計數載體，係交付物座標（WHAT）與治理設施引用，非實作技術選型（HOW）；「容器內 serial」「前端型別檢查」屬憲法與 CLAUDE.md 既定紀律引用。
- brainstorm 之 Q1～Q22 與 grilling GR1～GR9 之 user 拍板不重述為 Clarifications 節（該節留給 `/speckit-clarify`）；其中改變 user 可見行為者（灰色保留選項、搜尋卡放寬、兩處解鎖入口與列解鎖呈現、三頁按鈕碼、預設繁中、空字串清空、同值不寫不記、自鎖防護、Admin 預設只見清單）已落 FR、US 場景與刻意分岔登記表。
- 剩餘 clarify 候選兩題（皆非範圍或安全級、spec 以預設形承載）：違規子鍵命名空間（兩頁共用或分置）、政策矛盾告警出口形（新計數族或新來源值）。
- m0003 屬一次性 seed 遷移：Risk／Guard／Rollback 三欄表已附（CLAUDE.md §2）；新列 id 與冪等形留 plan 期定。
- 憲法條文字面（島 I 各款、I6 空缺寫法、I7 是否具名 R_SUPER、島 B／C 改述、H2 補句與否、新用途號）不在本 spec 定稿：FR-055 只定範圍與必含項，字面於 U0 由 user 逐款親決。
- clarify 後增補（2026-10-05）：側邊提醒「舊走查基準可能把 m0003 改回去」經主線親核成立（以 006 刀終態基準呼叫走查還原工具之純函式模擬、零 docker 零寫入：刪列 164、補回列 44、序號撥回 163，列 58～63 與選單 78 不還原、遷移帳仍記 m0003）；另揭 m0003 登記演進帳後 seed 模式拒跑。處置：FR-057 增 (a) 遷移帳前置（主線工程判斷）、(b) seed 模式合成演進登記（範圍＝user 裁定本刀做）、(c) 自測與次序；連動 Summary、US6（敘述、獨立測試、場景 4～6、原場景 4 改 7）、Edge Cases 三條、FR-056 ⑬、SC-008、m0003 三欄表（首列 Rollback 改寫、增兩列）。檢核表 16／16 不變。
- 再增補（2026-10-05、user 納入）：側邊提醒指出 (b) 原只合成角色／選單／使用者域、系統設定一有演進登記兩模式仍拒跑，與選項所述「之後每支 migration 都不必再處理」不符；FR-057 (b) 擴及兩模式之系統設定比對、合成所涉之表有登記時才驗 repo 與現庫遷移同步；唯一仍拒跑之演進形（往清理面五表塞 seed 列）明列為邊界。連動 Summary、US6（敘述、獨立測試、場景 7，原場景 7 改 8）、Edge Cases（改一增一）、SC-008、m0003 三欄表 seed 模式列。檢核表 16／16 不變。
