# Specification Quality Checklist: 008 稽核與系統設定頁進場——系統設定頁、稽核頁四源與清理、存取日誌寫入、reaper 三 job、島 J 入憲

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-20
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
- 驗證紀錄（2026-10-20、主線自驗一輪＋機器核）：FR-001～FR-075、SC-001～SC-016 連號且交叉引用全數可解；US1～US6 共 47 條驗收場景皆具 Given／When／Then；零 [NEEDS CLARIFICATION]、零 `tmp/` 路徑、零檔案行號引用；引用之 BL（14 條）、ADR（25 支）、LL、RL 編號逐一核在冊；前代編號皆帶 `rev5:`／`rev4:` 前綴；`python3 tools/docsync lint` 0 錯誤（1 警告＝既有 GT-12）、`check` 零漂移。
  自驗另修兩處：設定頁四組之歸組規則寫成 rev5 實形（`password_`／`ip_`／`login_throttle_` 三前綴、其餘歸工作階段）；US1 獨立測試補「先載入政策快取」一步，使改政策即清快取可被觀察。
- 事實面親核（非沿用 brainstorm 轉述）：ROUTES 現 61（公開 11／政策保護 45／登入即可 5）；seed 列 139／140／141／158（GET）與 159（POST）皆 R_SUPER、非受保護；選單 9（`manage_system-settings`；選單維政策列 69 受保護）與 77（`manage_audit`；按鈕清單現 NULL；選單維政策列 142 非受保護）；設定兩端點（列 66／67）受保護；授權列現 163、最大 id 164、受保護 25、R_SUPER 按鈕碼 21；演進帳 E-001～E-009（下一號 E-010）；`MSG_KEYS` 現 68；錯誤變體現 11；攜參射程現二鍵；動作詞現八；設定登記表 16 鍵與其界值；設定讀 wire 現四欄；四稽核表欄形（存取日誌之操作者與來源位址 NOT NULL、操作日誌之標的 id 為整數而操作者可空、會話事件表名為 `session_event` 且來源 IP 為文字欄）；信心值八值＋舊 `nginx_peer`；XFF 上限 1024；rev6 使用者寫端快照之手機與信箱鍵＝`userPhone`／`userEmail`；compose 既有 reaper（jobs profile）與 pushgateway（metrics profile）；告警 ③d／④／⑤⑤b／⑥⑥b 之現況註；runtime-append 現四表；存取日誌 facade 現不存在；ADR-00081 可授出集 30 與現行十八款；未帶權杖回 `8888`、權杖過期回 `3333`；★ 軌道表之 commit 數以 2026-10-20 對 upstream `example` tip `8be6f9ba` 實測；兩頁 view 目錄 upstream 無。
- ★更正 brainstorm 轉述兩處（皆屬沿用項之字面精確化、非新拍板）：①brainstorm §3 §2「存取／登入兩源 realIp 精確等值」與 rev5 as-built 不符——rev5 存取日誌之查詢參數與搜尋卡皆無來源 IP 欄、只登入嘗試有；本 spec 以 rev5 為準（FR-009、FR-010、Edge Cases、Out of Scope）。②brainstorm D1 與工程判斷⑭所稱「ADR-00047 觸發器」之現行承載為 ADR-00080（續行並取代 ADR-00047；「系統設定寫端被重寫」之翻案觸發器沿 ADR-00047 列於 ADR-00080）；FR-028 改指 ADR-00080。
- 判定原則承 001～007 刀前例：本刀 stakeholder＝admin 後台超級管理員、被委派之管理員、維運者與 workspace 維護者；spec 中的端點路徑、碼（`2222`／`4040`／`5000`／`5003`／`8888`／`3333`／`7777`）、seed 列號、環境變數名、★ 軌道名與用途識別符、閘與工具名、msg 鍵、檔名、計數載體與 metric 名，係交付物座標（WHAT）與治理設施引用，非實作技術選型（HOW）；pushgateway 推送之兩種實作只列為 plan 期比較題、不在本 spec 定案；「容器內 serial」「前端型別檢查」屬憲法與 CLAUDE.md 既定紀律引用。
- brainstorm 之 B1～B5、D1～D12 與 grilling g1～g5 之 user 拍板不重述為 Clarifications 節（該節留給 `/speckit-clarify`）；其中改變 user 可見行為者（存取分頁有資料、設定變更入操作日誌、跨鍵矛盾提示、政策快取清除、`audit:purge` 碼、排程清理自記列形、繁中全頁審讀）已落 FR、US 場景與刻意分岔登記表。
- spec 起草時主線自拍之工程判斷（回報備查）：①同值設定寫入照寫並照落一列稽核（FR-028；預設形、列 clarify 候選）——理由＝D1 字面「每次 updateSystemSetting 同交易落一列」＋ADR-00080 設定域「同值照寫」，本刀起與角色選單域同形；②授權對賬有無 `--execute` 皆零寫入（FR-035）——理由＝B4「只報不刪」；③reaper role 之授權域讀權表＝`casbin_rule`、`sys_menu`、`sys_role`（FR-039）——理由＝三維候選集與角色代碼對賬所需之最小集。
- 剩餘 clarify 候選四題（皆非範圍或安全級、spec 以預設形承載）：對賬計數 metric 與告警規則之名稱與門檻；m0004 拆不拆兩支；pushgateway 推送之 HTTP 實作甲乙（若引入新依賴、版本另依全域 §6 兩源比對）；同值設定寫入照落稽核列。
- brainstorm §6 所稱「spec 須含子句層需求追溯表」依 007 前例讀為：spec 以 FR-071 規定射程（全四類）與自證義務（ADR-00097 決定 2b），子句表本體住 tasks.md（承載對映於 tasks 期方可成表）。
- m0004 屬一次性遷移：Risk／Guard／Rollback 三欄表已附（CLAUDE.md §2）；新列 id、冪等形與拆分與否留 plan 期定。
- 憲法條文字面（島 J 各款、J2 回填字面、§I.6 括號句、用途 (ix)(x) 之範圍欄初值）不在本 spec 定稿：FR-060 只定範圍與必含項，字面由 user 逐款親決（plan 期：user 2026-10-21 裁定、依 ADR-00089 決定 4／7）。
- plan 期更正（2026-10-21；research R24）：上列第②點所稱設定域觸發器之「現行承載為 ADR-00080」已失準——ADR-00080 已被 ADR-00091 supersede，現行承載＝ADR-00091（spec FR-028 等處同改）；另 plan 期補 spec 修補 E2～E6（I18N (i) 三鍵入 Amendment、★軌道表補 `request/index.ts`、reaper 權限測形、心跳 metric 名、款數十七）。檢核項狀態不變。
