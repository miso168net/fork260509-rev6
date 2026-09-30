# 006-authz-governance — 授權治理（三維授權＋結構性封死＋授權回收桶＋島 G 入憲）brainstorm（階段 0）

- 日期：2026-10-01｜狀態：理解校正＋範圍與承載十一題（Q1～Q11）＋設計四節皆已過 user 核可（Mac 端 user 親決、一題一問、首選項皆為建議）；下一步＝**手動** `/speckit-specify`（本檔為其 input；不自動觸發——否則 before_specify hook 不跑、分支不建）。
- 一句話：把角色頁三顆授權彈窗（選單維／按鈕維／端點維；第三顆為新檔）與授權回收桶頁自 demo 殼接成真——10 支端點（三維讀寫 6＋候選讀 2＋回收桶 2；ROUTES 39→49、GET 6／POST 4、全為 Policy 只授 R_SUPER、seed 皆 protected=TRUE）、零 migration、零 seed 變更；結構性封死（G6）、全量替換射程＝候選集、手動撤銷之選單／按鈕維不可復原；憲法一次 MINOR 1.6.0→1.7.0（島 G 入憲＋§III.2 新用途兩列＋BL-00135／BL-00132 併入＋島 H 連動）；ADR 九支。
- 交付價值：超管首次能在 UI 上真的設定每個角色看得到哪些選單、能用哪些按鈕、能呼叫哪些 API，改完即時生效；撤掉的授權進回收桶可查、端點維可一鍵復原；受保護端點結構上授不出去。BACKLOG 開放 17 條中 5 條隨本刀收、3 條收窄，同批新記 2 條（本窗淨 −3）。

> 輸入：`docs/ops/NOTES.md` 下一步（006 條，含 v7 體檢之必帶七條與反向確認兩條）、憲法 §I.7（島 H 序言之 G 位保留與凍結位句、H1／H2、承襲指針表 G／I 列）／§III.2（用途 (ii) 明文兩彈窗不入名單、表外宣告三項、生成檔紀律）／§IV／§V.2～§V.3、`docs/ops/BACKLOG.md` 開放 17 條與滯後卷 3 條、主線 BACKLOG 分類體檢工作檔（2026-09-30 v7、跨機交接版、gitignored、不入帳；其必帶項與題面為本檔 §2 底稿）、ADR-00014／ADR-00042～ADR-00047／ADR-00055～ADR-00058、`deploy/grafana-provisioning/alerting/rules.yml`（casbin-reload-anomaly）、rev6 碼面現況（pins base-web `2248b89`／rust-api `8c8b5e1`）、rev5 藍本 `rev5:006-authz-governance` 全套（brainstorm §0／§2／§10／§11、spec US1～US4、plan、research、data-model、contracts、tasks、quickstart）與其 as-built（rust-api 13 顆、base-web 7 顆；rev5 HEAD 另含 006 後之 `rev5:B-116`／`rev5:B-129` 等修正）。
> 取證：唯讀探勘 workflow（六鏡＋逐鏡反駁＋完備性評審、13 支、opus[1m] xhigh；關鍵主張 112 條＝確認 104／推翻 8〔更正已併入本檔〕／不確定 0）＋主線逐項親驗（seed protected 分布、ROUTES 缺席、兩彈窗與基線逐位元相同、還原工具射程、原因值否定表、憲法原文）。

## 0. 拍板紀錄（全數 user 拍板 2026-10-01、一題一問；首選項皆為建議）

| 題 | 拍定 | 要點 |
|---|---|---|
| 理解校正 | 正確 | 目標／規模（10 端點、零 migration）／成功準則（島 G／H 不變式全過＋CDP 對照 rev5 HEAD 行為一致＋走查基準六步還原＋BACKLOG 收 4〔Q9 後為 5〕收窄 3）／四項假設：rev5 22 題拍板預設沿用、只在 rev6 事實不同處問；與 rev5 HEAD 一致之 UI 行為直接沿用；還原工具擴至能補回被撤之 seed 授權列 |
| Q1 整體形狀 | **單刀、rev5 四 US 全帶** | US1 三維授權、US2 結構性封死、US3 授權回收桶頁、US4 三顆彈窗接真（端點彈窗新檔＋角色抽屜第三鈕）＋島 G 入憲；BL-00045 收窄至 008 兩頁 |
| Q2 手動撤銷可否復原 | **照 rev5：不可復原** | 選單／按鈕維手動撤銷入不可復原集（不可復原集 3→5、原因值共 6、唯 `endpoint_revoke` 可復原）；零 migration；BL-00047 不到期 |
| Q3 封死射程 | **照 rev5：只封 protected=TRUE** | G6 謂詞圈出端點維 15 支；現役 25 支 Policy 端點中 21 支（FALSE）可授出——入已知態（ADR-00045 續行）逐支記授出後效果＋翻案觸發（例：首次出現多層管理員需求）；UI 不加警示 |
| Q4 no-escalation | **照 rev5：留 007** | 掛點不動；BL-00048 觸發收窄 007、列不刪；unlockLogin 授出後無帳號維守門併入已知態；碼註「授權治理島」之歸屬措辭勘誤為島 I（ADR-00014 body 不可變、BL-00048 對沖） |
| Q5 停用雙護欄入憲 | **照 rev5：不入條文** | 續由 ADR-00044 決定 3 承載；島 G ADR 寫明此款不轉正與理由（護欄觸發口徑之改動免修憲） |
| Q6 BL-00134 過渡窗 | **記窗** | H2（與島 G 對應條）如實記兩窗：commit→換上之有界過渡窗、重試耗盡窗；含端點維撤銷及於 API 授權與授予面反向症狀（新授權仍回 5003）；新 ADR 補述 ADR-00043 決定 9 並聲明 ADR-00042 body 內兩處同字面被取代；零碼改 |
| Q7 BL-00132 | **整條做** | Amendment 同顆改表外宣告 3（塊數入對賬射程）＋首個 base-web 單元前於 `tools/fork-delta-lint.py` 加範圍欄對賬腿 |
| Q8 撤銷射程 | **＝候選集**（`rev5:ADR 0056` 形、本刀預拍） | 候選外現役列不撤、不授、不入現況回應 |
| Q9 BL-00131 | **本刀前端修** | 抽屜只在 status≠回填值時才帶 status；與 rev5 分岔立小 ADR；2026-09-30 之裁定射程為「006 前不開維護批」、本題為 006 內承接 |
| Q10 BL-00084 | **併 ADR-00046 續行為 by-design 款** | 每次阻擋恰一則 warn、不設節流＝004 刀 FR-024 直接推論；承載由 005 刀 spec Out of Scope「觀測 profile 首起」改為本刀續行（理由：ADR-00046 替代案 2 否決單款 ADR、本刀本須整顆續行） |
| Q11 旁支孤兒義務 | **合併立 BL-00138** | 003 刀延至「前端 UI 刀」兩項（刀序表無此刀、帳本零承載）：①LangType 擴充與 zh-TW 語系註冊、`zh-tw.ts` 標型重構 ②自助頁手機驗證從零建頁；觸發＝007 brainstorm 起手前重評 |
| 設計四節 | 全核可 | 節 1 方案與範圍／節 2 後端／節 3 前端／節 4 測試、工具、驗收（即 §3） |

**主線工程判斷**（CLAUDE.md §5 自拍、回報備查）：①方案 A 分層、先底座後消費（005 同形；B 按 US 垂直切片——共用底座首片即須完整、範圍欄實數多次變動，C 後端全先——前端單元過大、CDP 最晚，皆棄）②回收桶頁沿 rev5 8 欄、不加 method 欄——seed 端點維 50 相異路徑、同路徑多方法 0（逐列核）③選單維受保護四列不封（`rev5:006` §11-8）④seed-view-gate 照建（`rev5:006` §11-20；ADR-00055 決定 3 預告首例）⑤三彈窗就緒守／請求世代／換角色清狀態、首頁下拉接 roleHome、protected 讀端帶旗標、授予面 Applied 即觸發（含空 diff）皆照 rev5 HEAD ⑥觸發列以新 ADR 增列、不 supersede ADR-00043（其決定 7 字面「由該刀 ADR 增列」）⑦BL-00136 形①：授予經 facade INSERT 落 `created_by`＝操作者、兩案改錨 seed 政策列 ⑧還原工具與測試守衛擴至能補回被撤 seed 授權列（評審高嚴重度缺口；005 刀 U15 前例）。

## 1. rev5 承襲盤點（沿用項照已驗證結論施工、翻案項用新設計；CLAUDE.md §2）

| rev5 項目 | 處置 | rev6 落點 |
|---|---|---|
| 四個 user story（US1 三維授權治理／US2 結構性封死／US3 授權回收桶／US4 三顆授權 modal 接真）與優先序 | 沿用（Q1） | 本刀範圍 |
| 11 支端點射程（`rev5:006` §2） | 沿用、扣 005 已交付之 getAllPages ⇒ 10 支；ROUTES 39→49（遞增鏈由 tasks 定） | router／handler |
| 刀縫 α（grant／revoke 寫 casbin_rule＝本刀）與 005 八件底座（選單域、rebuild-swap、`insert_archived`、reason gate 單點 fn、治理域讀端、common 共用件、測試基建、名冊閘） | 沿用；八件已由 005 刀以 rev6 形交付、本刀純消費 | 既有 facade／`auth/enforce.rs` |
| 結構性封死 G6（謂詞 `ptype=p ∧ protected=TRUE ∧ v2∈HTTP 動詞`、鎖內現查、條文不寫列數、掛點恰兩處、R_SUPER 豁免；`rev5:ADR 0054`） | 沿用（Q3）；兩代 seed 逐列相同、量測值同（端點維 15／選單維 4） | 島 G6、ADR②；已知態入 ADR⑥ |
| 選單／按鈕維手動撤銷不可復原（`rev5:006` §10-6 取 B、`rev5:ADR 0055`） | 沿用（Q2）；★rev6 現行 `is_non_restorable_reason` 為否定表、既有釘案斷言三撤銷原因「屬可復原」⇒ 負向臂同批翻 | `facade/sys_casbin_archive.rs`；ADR③ |
| 復原固定序五腿（gate→同實例→封死→端點在冊→停用不擋）＋列表 restorable 旗標＝①～④同判準（`rev5:006` clarify） | 沿用 | restorePolicy／getArchivedPolicies；ADR③ |
| 全量替換射程＝候選集（`rev5:ADR 0056`；rev5 實作期升級） | 沿用、改為 brainstorm 預拍（Q8） | 三維寫端；ADR④ |
| 授予面 Applied 即觸發（含空 diff、刻意例外；`rev5:006` §11-4） | 沿用；rev6 形＝新 ADR 增列觸發列（ADR-00043 決定 7） | ADR⑤ |
| restorePolicy 不入選單域（Q6 取 B 之連動） | 沿用（Q2 連動）；H1 括號改寫為該兩維復原分支結構性不可達 | 島 H1 字面 |
| 選單維受保護四列不納封死（§11-8）、roleHome UI 納入（§11-10）、protected 預標載體＝讀端帶旗標（§11-12）、§III.2 分列兩用途（§11-13）、seed 68 歸 007（§11-19）、seed-view-gate 順捎（§11-20） | 沿用（rev6 事實同形；user 已確認之假設） | 各節 |
| 停用雙護欄不入條文（`rev5:ADR 0053` Q5） | 沿用（Q5） | ADR-00044 決定 3 續承載 |
| no-escalation 掛點不填、本體隨 007（`rev5:006` FR-027；本體＝`rev5:007` 島 I7） | 沿用（Q4） | BL-00048 收窄 |
| 三 modal 就緒守（`rev5:006` U9b）＋請求世代（`rev5:B-116`）＋換角色清狀態（`rev5:B-129`）＋可寫 computed setter 與 TreeOption disabled 雙保險（`v-model:checked-keys` 不動） | 沿用 rev5 HEAD 形（CDP 基準） | 三彈窗 |
| 回收桶頁 8 欄（不顯 v2） | 沿用（工程判斷②） | policy-archive 頁 |
| grant INSERT 落 `created_by`＝操作者 | 沿用；rev6 另用作 BL-00136 形①改錨料源（rev5 未用於錨 seed） | facade；測試 |
| ★翻案不帶回（RL-0065）：①facade 自開交易／取域鎖／寫稽核 ②`audit_operator` 缺席拒寫帶 degraded 欄、借他島 target ③deleteRole 免同步 ④測試守衛寫死 setval 值 ⑤msg 鍵以字面 `Cow::Borrowed` 構造 | rev6 形：①handler 持交易、`<op>_in_txn` 首句入域（005 刀 FR-043／R6）②005 刀工程判斷 11 ③ADR-00043 決定 7（刪除家族實際歸檔才同步）④RL-0031、005 刀工程判斷 10 ⑤字面只住 `msg_key` | 全刀 |
| 已由 005 交付而消失之工作 | getAllPages、roleHome fetcher、common 收攏、wire 裁判補齊、`rev5:B-099`／`rev5:B-105` seam 等 | — |
| rev5 無藍本之 rev6 新題 | BL-00134 雙窗（Q6 記窗）、BL-00136 殘列不連坐、BL-00131（Q9）、還原工具補 seed 列（工程判斷⑧）、下放窗已知態（Q3）、BL-00132 對賬腿（Q7） | 各節 |

## 2. BACKLOG 觸發項處置（動工前掃描、CLAUDE.md §2；17 開放＋3 滯後逐條對觸發欄；以 BACKLOG 現文為準）

| 分類 | 條目 | 006 的哪一步 |
|---|---|---|
| 收・本刀刪列 | BL-00084（Q10；ADR-00046 續行 by-design 款＋「七款」errata）｜BL-00131（Q9；前端修＋小 ADR）｜BL-00132（Q7；表外宣告 3＋lint 對賬腿）｜BL-00134（Q6；記窗）｜BL-00135（user 2026-09-30 已裁「下次 Amendment 併入」；§III 修改型補模板屬性行變體句＋活書 §8.4，須早於 base-web 單元） | U0 Amendment／各單元／收刀 |
| 收窄・留列 | BL-00045（本刀交付 policy-archive 頁；條文收窄為 008 之 system-settings／audit 兩頁）｜BL-00048（觸發收窄 007）｜BL-00136（形①本刀收：殘列不連坐 SC＋演練、授予落 `created_by`、兩案改錨；形②使用者角色指派→007） | 收刀改條文 |
| 反向確認 | BL-00133（本刀使歸檔表有消費面〔restore 刪列〕、新增撤銷原因⇒改寫其①②敘述、不消化）｜BL-00047（Q2 取不可復原⇒零 delta；收刀前確認 migration 目錄恰 m0001／m0002、演進帳 entries 空） | 收刀前體檢 |
| 不動（綁 007／008／外部） | BL-00031／BL-00065／BL-00091／BL-00124（007）｜BL-00043（008）｜BL-00108（條件式：本刀若於 rust 側新寫字元級解析 lint 即為第三份、當刀收攏——seed-view-gate 以 python 實作避開）｜BL-00002（user 2026-09-30 維持原觸發） | — |
| 滯後卷 | BL-00049（條件依賴：多角色 CDP 沿用登入頁快速登入鈕切帳號）｜BL-00064｜BL-00067 | — |
| 本檔同批新記 | BL-00137（壓縮 hook 之背景 task 目錄 fallback 於 macOS 推錯暫存根；user 2026-10-01 裁「記一條 BL」）｜BL-00138（Q11） | 本檔 commit |

淨效果（006 窗）：刪 5、新記 2＝−3；收窄 3 條不計。

## 3. 設計（四節、user 已核可）

### §1 方案、範圍、修憲、ADR

- **方案 A**：U0 修憲 → 後端底座（授權 facade、候選集、封死謂詞、原因值、觸發列）→ 三維端點 → 回收桶端點 → 前端三彈窗與抽屜 → 回收桶頁 → 工具與文件 → CDP → 收刀前承載體檢。
- **範圍**：getRoleMenu／updateRoleMenu、getRoleButton／updateRoleButton、getRoleEndpoints／updateRoleEndpoints、getAllButtons、getAllEndpoints、getArchivedPolicies、restorePolicy（seed 政策列 32／33、52～57、70／71 既在且皆 protected=TRUE；選單列 72 `manage_policy-archive` 亦既在）。
- **Out of Scope（逐條指承載）**：no-escalation 本體→007（BL-00048）；seed 68 updateUserSessionPolicy→007；system-settings／audit 兩頁→008（BL-00045）；使用者角色指派之殘列形→007（BL-00136 形②）；列表排序→ADR-00058 決定 3；008 設定頁之呈現→ADR-00057 後果；「前端 UI 刀」兩項→BL-00138。
- **憲法 Amendment（MINOR 1.6.0→1.7.0、一筆；條文字面於 U0 由 user 逐款親決）**：①島 G 入憲（G1～G6、G6 新立；停用雙護欄不轉正；G5 條文層級與島 G 標頭寫法於親決輪定）②§III.2 新用途兩列：(iii) 三顆授權彈窗接真（`menu-auth-modal.vue`／`button-auth-modal.vue`＋`role-operate-drawer.vue` 同檔雙用途＋locale／`app.d.ts`）、(iv) policy-archive 頁（`route:`／`page:` locale 塊、`app.d.ts` page 型節、路由產物四檔依產物檔紀律）；新檔（端點彈窗、回收桶頁本體、`rev6-authz.{ts,d.ts}`）不入表 ③BL-00135 變體句（§III 修改型；活書 08 §8.4 同批）④BL-00132 表外宣告 3（塊數入對賬射程）⑤島 H 連動：序言「島 G 入憲前凍結位」句改寫、H1 括號刪條件式預告並改寫為「回收桶復原之選單／按鈕維分支結構性不可達」、H2 記兩窗（Q6）、「七島」改八島、承襲指針 G 列補 rev6 入憲載體、README 憲法版本鏡像。H2「同步失敗保留上一份」方向句之落位（留 H2 或移 G1 互引）於親決輪定（ADR-00042 翻案觸發器要求複核）。
- **ADR 待立九支**（feature branch 內、plan 期起草；proposed 期不宣告 supersedes、accepted 同顆補）：①島 G 入憲（Amendment；provenance `rev5:ADR 0053`；含停用雙護欄不轉正、觸發方向面入憲而矩陣留 ADR）②G6 結構性封死（`rev5:ADR 0054`）③回收桶復原五腿＋不可復原集 3→5（`rev5:ADR 0055`；附 ADR-00044 決定 4 之復核結論＝選單維仍無可復原 reason、`menu_id` 同實例欄續 won't-use）④全量替換射程＝候選集（`rev5:ADR 0056`）⑤判定面同步觸發列增列＋記窗（補述 ADR-00043 決定 9；聲明 ADR-00042 兩處同字面被取代；不 supersede ADR-00043）⑥ADR-00045 續行（款 1／3／4／7 之解除或改述＋新已知態：21 支可授出端點與 unlockLogin 窗、選單維受保護四列「看得到、點不動」）⑦ADR-00046 續行（款 3 操作稽核寫入者擴列 update／restore＋BL-00084 by-design 款；改指 12 檔 21 處、含兩子庫碼註與 base-web 頁面）⑧BL-00131 前端修（與 rev5 行為分岔登記）⑨seed-view-gate 碼面閘（RUNBOOK §12 標讀面型、ADR-00055 決定 3）。

### §2 後端

- **交易與鎖**：handler 持交易、`<op>_in_txn` 首句入域；鎖序沿 005 定案 advisory→歸檔表列→sys_role 列→sys_menu 列→casbin_rule。updateRoleMenu／updateRoleButton 入選單序列化域（島 H1 終態成員）再鎖角色列；updateRoleEndpoints 不入域、角色列 FOR UPDATE 序列化；restorePolicy 不入域（只剩端點維可復原）、先鎖歸檔列再鎖角色列。
- **全量替換**：撤銷集＝（現況 ∩ 候選集）−期望；授予集＝期望 −現況；候選外現役列不撤、不授、不入現況回應。候選：選單維＝治理域選單（未刪含停用）、按鈕維＝治理域按鈕碼聯集（穩定序）、端點維＝ROUTES 中 Policy 全集（抽具名 `policy_endpoints()` 斷循環依賴）。
- **保護判定**：撤銷側三維皆適用——撤銷集觸及 protected 列＝整批拒（`protectedRevoke`；零變更、零稽核、零同步）；授予側＝G6（端點維）——非 R_SUPER 標的之授予集觸及封死集＝整批拒（`protectedGrant`）；updateRoleEndpoints 先判撤銷、再判授予；restorePolicy 第③腿同謂詞。拒因為 2222＋純 key。
- **歸檔與復原**：撤銷＝archive-move（原因 `menu_revoke`／`button_revoke`／`endpoint_revoke`；`role_id` 由函式內以 v0 反查）；不可復原集 3→5（否定表加兩值）；restorePolicy 五腿固定序、回插 casbin_rule（新 id）＋刪歸檔列＋稽核 `restore` 同交易；getArchivedPolicies 分頁（005 分頁通則）＋角色與維度兩篩選、每列帶 restorable（①～④）。
- **寫入形**：授予經 facade 直接 INSERT、落 `created_by`＝操作者；絕不走判定引擎管理 API（G1）、不走轉接器 `add_policy`（LL-00035：重複列回 Err 且吃序列）；操作稽核同交易、封閉五詞之 `update`（三維寫端）／`restore`。
- **判定面同步**：移除面維持「實際歸檔 ≥1 列」；授予面三支 Applied 即觸發（含空 diff、刻意例外、重建冪等）；restorePolicy 僅 Applied；Rejected／NoOp／不可復原不觸發。兩窗記入條文（Q6）、既有 `casbin_reload_total` 計數與 casbin-reload-anomaly 告警照舊。
- **其他**：新拒因 msg 鍵兩語同批、與 `MSG_KEYS` 跨端對賬；新命名空間補 wire-schema 錨；角色鍵名一律 `id`；`authz_entrypoint_lint` 之 `RELOAD_CALL_FILES` 擴列新寫端檔、`ENFORCER_WRITE_FILES` 維持空集；no-escalation 掛點不動。模組落點（工程判斷）：新 facade `sys_casbin_policy`（diff／候選集／封死謂詞）、擴 `sys_casbin_archive`（原因值／復原）、新 handler 兩組（三維授權、回收桶）。

### §3 前端

- **三彈窗**（rev5 HEAD 形重打字）：選單權限（修改型；治理域樹＋勾選＝getRoleMenu；首頁下拉接 getRoleHome／updateRoleHome——ADR-00045 款 1／7 到期）、按鈕權限（修改型；候選＝getAllButtons）、端點權限（新檔；候選＝getAllEndpoints、現況＝getRoleEndpoints；授予側不預標受保護端點、替非超管勾選者送出才拒）。共同守衛：三維現況讀端皆帶 protected 旗標、現況受保護列鎖住不可取消勾選（模板 `v-model:checked-keys` 不動、以可寫 computed 補回＋TreeOption disabled 雙保險；BL-00135 句入憲後依新句標記）；讀成功前確定鈕停用且每次開啟復位；請求世代丟棄遲到回應；切換角色清狀態。
- **角色抽屜**（同檔雙用途）：既有 `v-if="isEdit"` 區加第三鈕「端點權限」並掛新彈窗；BL-00131 修法（status≠回填值才帶）在既有新增型圈界內、(ii) 列實數不變。
- **授權回收桶頁**（新檔頁面＋搜尋模組）：8 欄、角色與維度篩選、分頁、restorable 才可復原、成功後重取；路由產物由外掛重算；兩語 locale 鍵集相等。
- **API 包裝與型別**：`src/service/api/rev6-authz.ts`、`src/typings/api/rev6-authz.d.ts`（§III.1 預設軌道）；後端拒因鍵落 `backend:` 樹（既有 I18N-WIRING (ii)／(iii) 射程）。
- **fork-delta 與修憲銜接**：(iii)／(iv) 範圍欄初值以「不預估」或預估填列、收刀前 PATCH 實數化（前例 ADR-00051）；BL-00132 新腿跳過不預估列、須早於首個 base-web 單元落地。
- **seed-view-gate**（新碼面閘、python）：seed 選單 component 之 view 集 ⊆ base-web view 集；具名豁免 system-settings／audit（附 BL-00045 指針）；pre-commit 段、自測、bootstrap 名冊、RUNBOOK §12 碼面閘表。

### §4 測試、工具、驗收

- **測試**（rust 容器內 serial；base-web pnpm 容器內、逾時放容器內＝LL-00038／LL-00039）：島 G 不變式逐條；島 H 既有全綠（入域寫端各配 NOT-granted 等待測）；觸發矩陣含空 diff 與不觸發三態；保護判定（三維撤銷拒、授予拒之 R_SUPER 豁免、復原腿③、鎖內現查）；候選集；原因值負向臂翻；restorable 同判準；殘列不連坐（BL-00136 形①：兩案改錨 `created_by IS NULL` 之 seed 政策列、測試件 `plant_live_policy` 同步、殘列演練納此形）；wire-schema、msg 鍵跨端閘、authz_entrypoint_lint、route-artifact-gate、fork-delta-lint（含新腿）全綠。
- **工具**：`tools/walkthrough-baseline.py` restore 擴至能回補被撤之 seed casbin 列並清除復原回插之新 id 列（現行射程＝只刪上界以上列、id≤上界之 seed 列被刪不在射程）、test_kit 守衛同理、RUNBOOK §9c 契約同批；fork-delta-lint 對賬腿；seed-view-gate。
- **驗收**（啟動書 §0.3 B 世代 DoD）：觸及之島不變式全過；CDP 三方對照（22080 rev5 HEAD 對 32080，必要時加 22089；對照面＝三彈窗、抽屜第三鈕、首頁下拉、回收桶頁；CDP 一律 opus[1m] xhigh）、刻意分岔逐項登記（BL-00131 修法、deleteRole 觸發同步〔005 既有〕、實作期新發現者）；走查基準本機自取 snapshot、前後六步還原 diff rc 0。
- **現在式假述掃除**（RL-0011、逐處判讀）：「只由移除面寫端觸發」類（外層 12 處／9 檔、rust-api 11 處／5 檔；講觸發集合者改、講移除面類別者留）；RUNBOOK §13 補授予面反向症狀（新授權未生效、仍回 5003）與排障錨；「限 R_SUPER」類（外層 4、rust-api 12；seed 事實者留、能力限定者改）；「七款」→「八款」；「授權治理島」措辭→島 I（`python3 tools/docsync errata` 枚舉）；ADR-00045／ADR-00046 續行之改指。
- **單元草案**（約 19 支；tasks 定稿於 SDD）：U0 前置體檢＋Amendment 親決＋施工前提 ADR accepted → U1 骨架（ROUTES 39→49 空殼＋授權態矩陣＋routes 釘值）→ U2 測試基建（seed 授權列回補守衛、前移）→ U3 授權 facade → U4 不可復原集 3→5 → U5 讀端與候選讀 → U6 選單／按鈕維寫端（入域）→ U7 端點維寫端＋封死 → U8 回收桶兩端點 → U9 觸發矩陣＋lint 名冊＋同步計數 → U10 wire／msg 裁判面 → U11 fork-delta-lint 對賬腿 → U12 兩彈窗＋抽屜第三鈕＋BL-00131 → U13 端點彈窗 → U14 回收桶頁＋seed-view-gate → U15 走查還原工具擴面 → U16 文件、ADR 續行、假述掃除 → U17 CDP 三方對照 → U18 收刀前承載體檢＋範圍欄 PATCH 實數化。
- **風險**：R1 seed 授權列被撤後回不來（U2／U15）；R2 判定面雙窗（記窗＋既有告警）；R3 21 支可授出端點之下放窗（已知態 ADR）；R4 BL-00108 第三份（seed-view-gate 用 python）；R5 CDP 基準為 rev5 HEAD 形（照 HEAD 實作＋分岔登記）；R6 errata 面廣（四形種子＋`docsync errata`）；R7 LL-00035（facade INSERT）；R8 BL-00049 條件依賴（維持現狀）。

## 4. 憲法 §IV 九題預答（供 `/speckit-plan` Constitution Check 起手）

1. base-web 為權威：PASS——三彈窗與回收桶頁為 upstream demo 面、其呼叫之 10 支端點正是本刀補齊對象；wire 型別開獨立命名空間。2. base-web inline：**涉及——授權以 Amendment 先行取得**（§III.2 新用途 (iii)(iv)；BL-00135 變體句同顆；fork-delta 紀律與 `rev6-inline` token 照舊；新檔不入表）。3. casbin：PASS——選單維授權寫入 casbin_rule、使用者可見性由判定面導出；不啟用 hideInMenu 等前端隱藏機制；選單維受保護四列之「看得到、點不動」為已知態。4. §I.3：PASS——信封、逐欄 id 型、13 碼零觸碰（拒因復用 2222）、msg=key。5. 前代 source：否——重打字消化、不拷貝、不需 §I.5 例外；翻案五項不帶回（§1 末列）。6. §II：無抵觸。7. ★ 軌道：觸及——屬「新能力」（新用途兩列）、須 Amendment（§V.2；user 親決）。8. 建業務表／migration：否——零 migration、零 seed 變更（Q2）；BL-00047 不到期。9. §I.7：觸及——島 G 隨本刀以 MINOR 入憲（承襲指針表 G 列）；島 H 之序言／H1／H2 同顆連動；以狀態機鏡頭設計（授予／撤銷／歸檔／復原四態與觸發矩陣），非 CRUD 格子。

## 5. 給 `/speckit-specify` 的輸入摘要

- feature 名＝`006-authz-governance`；user 故事核心＝US1 超管以三顆彈窗設定角色之選單維／按鈕維／端點維授權、即時生效（全量替換＋候選集）／US2 受保護端點結構上授不出去、受保護列撤不掉（G6＋撤銷拒）／US3 撤銷進授權回收桶、端點維可一鍵復原、選單／按鈕維只可閱覽（五腿＋restorable）／US4 三顆彈窗與回收桶頁接真（就緒守、請求世代、換角色清狀態、抽屜第三鈕、BL-00131 修法）；10 支端點、零 migration、憲法 1.7.0、ADR 九支。
- 直接輸入：本檔＋§2 處置表所列 BL 條目（收 5／收窄 3／反向確認 2／Out of Scope）＋`rev5:006-authz-governance` spec 之 US1～US4、FR、SC、Edge Cases（rev6 座標改寫：10 支與 ROUTES 39→49、getAllPages 已交付、不可復原集 3→5 與否定表負向臂翻、handler 持交易形、rev6 水位守衛形、seed 政策列號與 protected 帳以 rev6 seed 現數、CDP 基準 rev5 HEAD）。
- FR 措辭要求：觸發矩陣寫成三類同一字面（移除面實際歸檔 ≥1／授予面 Applied 含空 diff／復原 Applied）；封死謂詞只寫謂詞不寫列數；撤銷拒與授予拒分列；候選集射程寫成三維同式 FR；雙窗寫成已知降級行為（含 API 授權面）；殘列不連坐 SC 含 BL-00136 形①；★spec 須含「★ 軌道逐處登記」表（憲法 §III.2 機制骨架）與「刻意分岔登記」表（CDP 對照用）。
- clarify 候選（一題一問、rev5 as-built 為建議項）：①回收桶頁篩選條件是否加原因值 ②全撤（期望空集）是否允許、R_SUPER 標的之非受保護列可否撤 ③restorePolicy 對「同一政策已現役存在」之處置（冪等成功或拒）。
- Out of Scope 逐條指承載（§3 §1 清單；ADR-00058 決定 3 之排序單題指該 ADR）。

## 6. 隨做隨記

- ADR 待立九支見 §3 §1；plan 期全數產 draft；親決時點：Amendment 顆只含 ADR①（島 G）與其連動條文、其餘另顆（005 刀工程判斷 12 形）；ADR-00045／ADR-00046 續行於改指與已知態定稿之單元（U16）accepted。
- 收刀 `backlog_done` 5 條（BL-00084／BL-00131／BL-00132／BL-00134／BL-00135）；改條文 3 條（BL-00045／BL-00048／BL-00136）；改敘述 1 條（BL-00133）；本檔同批 `backlog_add`＝BL-00137／BL-00138（隨下一筆 events 事件入帳）。
- 流程坑（承 005 實踩）：①GT-05 只掃 git ls-files——新增 ADR／spec 先 `git add` 再跑 lint ②rev6 刀集外刀名一律提及形；前代刀號一律帶冒號前綴 ③proposed ADR 不宣告 supersedes、accepted 同顆補、generate 後再 `git add docs/arc42/decisions`（LL-00044）。
- NOTES「下一步」：specify 起手後同批改為 006 進行中；收刀時改 007。事件帳待補記兩筆 user merge＋push 同意（NOTES「未決」）於本刀第一筆 events 事件之 notes 補記、同批刪該條。
- 依賴：零新依賴（casbin 2.20.0 既釘；naive-ui 既有元件）——毋須版本拍板。
- TDD 發射前置：組裝形 workflow 模型家由 ADR-00056 固定（opus[1m]／xhigh）；手寫 workflow 每支 agent 明給同值；CDP 單元一律 opus[1m] xhigh。本機若缺他機工作區之單元範本，由 `tools/orchestration/EXAMPLE-*-unitdef.py` 經 `assemble.py` 起手；unitdef 烤 LL-00038／LL-00039。
- 走查基準本機自取（首次真登入走查前 snapshot；契約 RUNBOOK §9c）；rev6 stack 走查前先 `docker compose ps` 實看、必要時重建；CDP 對照基準重取、不沿用 005 產出。
- 活書：§3 所列各節（04／05／06／08／10／11／12、RUNBOOK §9c／§11.2／§12／§13）於 feature branch 內改成現在式；C4-L2 拓樸不變（零新容器）。
