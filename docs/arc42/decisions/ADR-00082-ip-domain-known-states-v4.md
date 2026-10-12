---
id: "ADR-00082"
title: IP 域已知態集（續行 ADR-00069）——款 1 解除（帳號維＝使用者列「解鎖登入」、來源維＝IP 規則頁「解鎖來源 IP」兩處入口共用同一包裝）、款 3 操作稽核寫入者集擴列使用者域寫端八支與個人中心改密並以現行全集重述（封閉詞彙五詞→八詞）、款 5 複核本刀新增之 redis 狀態皆可自癒、款 6 受審讀型擴列、款 2／4／7／8 續行（現行七款）
date: 2026-10-05
status: proposed
supersedes: []
superseded_by: []
provenance: "007-user-password-admin 之 spec FR-056⑨、FR-006（稽核同交易、動作詞彙封閉五詞→八詞）、FR-021（unlockLogin 帳號維掛包含規則）、FR-026～FR-027（撤票原因 `admin_kick`）、FR-036～FR-037（改密與改密舊密節流 redis 桶、窗自癒）、FR-040（兩處解鎖入口、ADR-00069 款 1 解除、BL-00091 收）、FR-041（m0003 增 `ipRule:unlock`）、FR-059（「無 UI 按鈕」句等現在式假述掃除）、FR-064（新讀型入受審名冊）、SC-014、US4 AS9、Edge Cases「包含規則與委派」「斷權與會話」；brainstorm §0 Q9（非建議項）／Q20、GR3、GR4（非建議項）、§3 §1 ADR 待立⑨；被續行面＝ADR-00069 八款（body 已 accepted 不可變、rev6 無部分翻案機制＝ADR-00011 決定 5；續行鏈 ADR-00040→ADR-00046→ADR-00069→本 ADR）；前代出處＝rev5:ADR 0067（解鎖入口歸屬之前代訂正：實落使用者管理頁頁首、雙維一處）、rev5:server/src/model/audit.rs（動作詞彙增 `kick`／`reset_password`／`change_password` 三詞與其分家理由）——rev6 解鎖入口改為帳號維使用者列、來源維 IP 規則頁（Q9）；draft 於 plan 期落 feature branch、續行款沿 006 刀字面、解除款與改寫款之證據於本刀 CDP 三方對照單元與整合測試觀察後定稿、user 親決於治理單元（accepted 同顆補 supersedes 並改 ADR-00069 狀態）；親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [ip-trust-anchor, user-password-admin, known-state, wont-fix, by-design]
---

## 背景

- ADR-00069 集中承載 IP 域八款已知態（續行 ADR-00046）。本刀（007 user-password-admin）使兩款到期：
  - **款 1**（解鎖端點 API-only、無 UI 按鈕；翻案觸發器＝使用者管理頁刀〔007 刀〕開工）：本刀開兩處解鎖入口（Q9、GR3、GR4；spec FR-040；BL-00091）。款 1 原文「按鈕權限碼已在 seed，使用者管理頁刀進場時零 seed 變更」於本刀只對帳號維入口成立（`user:unlock`＝seed 列 157）；來源維入口另以 m0003 增 `ipRule:unlock`（選單 78 之按鈕清單＋R_SUPER 按鈕授權列 164；GR4、ADR-00085）。
  - **款 3**（操作稽核寫入者全集、封閉五詞）：本刀新增使用者寫端八支與個人中心改密為寫入者，動作詞彙增 `kick`／`reset_password`／`change_password` 三詞（spec FR-006）。
- 另需複核兩款：款 5 之翻案觸發器之一為「新增不可自癒之 redis 狀態」——本刀新增改密舊密節流桶 `cpwd:{uid}`（ADR-00090）與失效名單之新原因值 `admin_kick`；款 6 要求表驅動之鍵集斷言涵蓋全部受審讀型——本刀新增使用者域讀型（spec FR-064）。
- ADR body 已 accepted 不可變（GT-04）；rev6 無部分翻案機制（ADR-00011 決定 5）⇒ 整顆續行。
- 現在式面量測（2026-10-05；只供背景、施工以決定 2 之指令現算為準）：`python3 tools/docsync errata ADR-00069` 全 repo 50 處命中；扣除史料面（brainstorms、specs、reviews）、生成鏡像（`docs/generated/`）、事件源與 ADR 檔（`docs/arc42/decisions/`）後——外層現在式 8 檔 17 處（逐檔 `grep -o` 計：`docs/arc42/06-runtime-view.md` 3、`docs/arc42/08-crosscutting-concepts.md` 3、`docs/arc42/11-risks-and-technical-debt.md` 3、`docs/arc42/12-glossary.md` 1、`docs/ops/BACKLOG.md` 2、`docs/ops/RUNBOOK.md` 3、`docs/ops/reference-src/trust-model-config.md` 1、`deploy/trust-model.dev.toml` 1）＋待判讀 2 檔 4 處（`docs/ops/NOTES.md` 之 006 刀收刀條 1、`docs/ops/LESSONS/` 一檔 3）；rust-api 2 檔 3 處（`server/src/middleware/mod.rs` 1、`server/tests/wire_schema.rs` 2）；base-web 1 檔 1 處（`src/views/manage/ip-rule/index.vue` 1）。「八款」現在式 1 處（活書 11 IP 域已知態列標題）＋NOTES 006 刀收刀條 1 處（現在式指針）。「無 UI 按鈕」「API-only」兩句形現在式各 5 檔（活書 06、活書 11、活書 12、BACKLOG〔BL-00091 條文〕、RUNBOOK）。

## 決策驅動因子

- IP 域已知態單一出處；款 3 以現行 `sys_operation_log` 寫入者全集重述、不以增量句疊加——寫入者全集一句可逐項對碼核對。
- 現在式鏡像以機器枚舉逐處改指（款號一對一）、不留對沖註；與 ADR-00081（角色與選單域續行）同句並存之現在式面同處施工。
- 新增之 redis 狀態與讀型逐一對既有款之翻案觸發器複核，不以「未觸發」默認。

## 考慮過的替代案

1. **只改活書與 RUNBOOK、不續行**：現在式面與 accepted 之 ADR-00069 款 1、款 3 字面相悖（權威鏈倒掛）；棄。
2. **款 3 之使用者域寫入者寫進使用者域語意 ADR（ADR-00080）**：稽核覆蓋不對稱之款住 IP 域 ADR 已三代（ADR-00040 款 3→ADR-00046 款 3→ADR-00069 款 3），拆開則寫入者全集散住兩支（ADR-00069 替代案 2 同判）；棄。
3. **款 1 只解一半**（帳號維入使用者列、來源維續 API-only）：Q9 已拍兩處入口、GR4 增碼；棄。

對所選方案跑同一反例（RL-0013）：款 1 解除後，來源維入口不套包含規則，是否使受讓 unlockLogin 者得經 IP 規則頁解除任意來源之鎖？是——此即 by-design（Q7：來源維無帳號持有者可比），其下放效果已入 ADR-00081 款 9 之 unlockLogin 列，未成新的無主面；整顆續行是否讓 ADR-00069 八款失去原拍板時點之可追溯性？不會——ADR-00069 body 不動、轉 superseded 後仍可讀，本檔逐款標明續行／解除／改寫並附款號對照表。成立。

## 決定

本 ADR 續行並將 supersede ADR-00069（本 ADR accepted 那一顆同批補 `supersedes: ["ADR-00069"]`、ADR-00069 之 status 改 superseded；`superseded_by` 由 `python3 tools/docsync generate` 回填）。

1. **ADR-00069 之款 2、4、5、6、7、8 原意續行**，現行依據＝本決定同號款（字面沿 ADR-00069、只做座標改寫；款 5 改述節流射程句並補本刀複核句、款 6 補本刀複核句）；**款 1 解除**（號不再配）；**款 3 改寫**如下。現行款＝款 2～8（七款）。
2. **現在式面改指**：現在式面引用 ADR-00069 之處改指本 ADR 同號款（款號一對一）；引款 1 之句（「API-only」「無 UI 按鈕」及同句之「授出後無帳號維守門」）改寫為現況敘述——兩處 UI 入口、授出後帳號維受包含規則而來源維不套（後半之已知態承載＝ADR-00081 款 9；兩支 ADR 之改指同處施工、互為前提，只換號＝指針旁留假述）；IP 域已知態計數句「八款」改「七款」並指本 ADR——★同詞「七款」於 005 刀指 IP 域之 ADR-00046、「八款」於 005 刀指角色與選單域之 ADR-00045；兩域計數句一律帶 ADR 號，枚舉時 ADR 號與舊數量詞（「八款」「七款」「十九款」）並掃、命中後以同句 ADR 號判定歸屬（RL-0011 四形）；稽核詞彙之數量詞（「五詞」「恰五個」「這五個字面」「零新詞」）與款 3 寫入者集敘述同批改。★NOTES 之「006 已收刀」條（「…與 ADR-00069（IP 域八款；…），其翻案觸發器即後續刀之承接點」）為指向後續刀之現在式指針：本 ADR accepted 後即失準，MUST 於本刀收刀簿記同顆整句重寫或刪條（LL-00064 守法①）；`docs/ops/LESSONS/` 之命中屬事故史述、不改；BACKLOG 之 BL-00091 條文隨本刀收刀刪列（RL-0050）。判定＝`python3 tools/docsync errata ADR-00069` 全 repo 命中（含兩子庫，另以 `git -C <子庫> grep -o ADR-00069` 對賬）扣除史料面、生成鏡像、事件源與 ADR 檔（accepted body 不可變；本刀續行 ADR 草稿自身〔本 ADR 與 ADR-00081〕對被續行者之引用屬續行面本身）；處數以施工時同指令現算、改完復掃；實際改指屬本刀治理單元（兩子庫只改註、走兩段式 commit）。

**各款（現行依據）**：

- **款 1**：解除（本刀；號不再配）——`POST /systemManage/unlockLogin` 自本刀起有兩處 UI 入口、共用同一 API 包裝（`src/service/api/rev6-user-admin.ts` 之 `fetchUnlockLogin`；spec FR-040）：**帳號維**＝使用者清單列操作「解鎖登入」（`user:unlock` 顯隱；標的＝該列帳號；包含規則於上下文檢查之後、稽核之前判，拒＝零稽核；ADR-00075）；**來源維**＝IP 規則頁表頭前綴插槽「解鎖來源 IP」鈕（`ipRule:unlock` 顯隱）＋彈窗輸入 IP（不套包含規則）。兩入口皆不預查鎖定狀態（帳號維每列可按、來源維表頭鈕恆可按）；對未鎖之標的照回成功並落一列 `unlock`（GR3；端點語意不變）。端點本體與「稽核先於標記」（島 E）不變；帳號維自本刀起於交易內取 per-user advisory 後判包含規則。解除證據＝本刀 CDP 三方對照（spec 刻意分岔登記表「解鎖入口」列：rev5 HEAD 為使用者頁頁首彈窗雙維一處）。
- **款 2 dev 經反向代理可達來源信心三態**：`fallback`／`proxy_clean`（信任模型決定）＋`chain_rejected`（轉發鏈跳數逾上界之判準不依賴信任模型、送逾上界之轉發鏈即端到端可達：登入端點拒絕並落一列稽核）；其餘五態由整合測試直餵信任模型覆蓋。端到端走查之結論只對此三態成立；不得把整合層結論寫成端到端已驗。
- **款 3 操作稽核覆蓋不對稱**（改寫）：`sys_operation_log` 之寫入者全集＝
  - IP 規則四寫端（`add`／`update`／`delete`／`restore`）；
  - 解鎖 unlockLogin（`unlock`；帳號維自本刀起於稽核之前判包含規則、拒＝零列；對未鎖之標的照落一列＝GR3）；
  - 角色寫端（新增／更新／刪除／批刪／首頁寫入）；
  - 選單寫端（新增／更新／刪除／批刪／復原；本刀起選單編輯移除尚有受保護授權之按鈕碼＝整筆拒、零列〔ADR-00086〕）；
  - 三維授權寫端（updateRoleMenu／updateRoleButton／updateRoleEndpoints；`update`，Applied 含空 diff 恰一列、Rejected 與查無角色零列）；
  - 授權回收桶復原（restorePolicy；`restore`，Applied 恰一列、NoOp 零列〔已知態＝ADR-00081 款 12〕、不可復原零列〔ADR-00065 決定 7〕）；
  - ★使用者寫端（本刀）：addUser（`add`）、updateUser（`update`；同值＝零列＝ADR-00080 決定 3）、updateUserSessionPolicy（`update`；同值零列）、deleteUser（`delete`）、batchDeleteUser（`delete`，逐標的一列；空陣列與任一違規整批 rollback 皆零列）、restoreUser（`restore`）、kickUser（`kick`；標的記被踢帳號、使用者列零變更）、resetUserPassword（`reset_password`）；
  - ★個人中心改密 changePassword（`change_password`；操作者＝本人）。

  動作詞彙為封閉八詞（`add`／`update`／`delete`／`restore`／`unlock`／`kick`／`reset_password`／`change_password`；本刀由五詞增三詞、`AuditOperation` 5→8；`reset_password` 與 `change_password` 分家＝受眾〔管理員對他人／本人〕與授權面〔政策保護／登入即可用〕皆不同）；稽核 payload 不含密碼明文與雜湊（島 I5；spec FR-006）。非寫入者：既有系統設定寫端維持不落稽核列（002 刀刻意決定）；m0003 之 seed 基線層改列不落操作稽核（島 G 之 G2 末句；ADR-00085）；讀端（含 getPasswordPolicy）不落；包含規則、seed 保護、本人規則與各業務守門之拒絕腿皆零列。⇒ 查詢端不得據此表宣稱「所有管理操作皆有稽核」。
- **款 4 logout 故障窗弱 oracle（won't-fix）**：DB 故障窗內 logout 對「簽章有效的票」回 `5000`、對垃圾票回 `0000`，可據以分辨票的簽章有效性。只在故障窗可見、只洩持票者手上那張票的有效性、refresh 端點對持票者本即回應可用性；保留 `5000` 使 API 呼叫端知道撤銷未成。折成 `0000` 會把「撤銷未成」回報為成功——不取。
- **款 5 redis 不開持久化**：解鎖標記遺失的後果＝至多少解鎖一次、可再解鎖自癒；登入節流判定面不依賴 redis（ADR-00038；射程讀法＝ADR-00090 決定 5）；改密舊密節流之判定以 redis 計數桶為真源、桶遺失＝窗提前自癒（ADR-00090 決定 2、決定 6）；會話面暴險由島 C 封頂（PG 為權威）。維持現狀。★本刀新增之 redis 狀態皆可自癒、不觸發本款翻案觸發器：①改密舊密節流桶 `cpwd:{uid}`（窗 900 秒自癒；遺失＝該使用者計數歸零、至多再得一窗之嘗試次數，改密仍須舊密正確且須持本人會話；載體不可用時放行並計入節流降級計數＝ADR-00090，與持久化無涉）②失效名單之 `admin_kick` 原因條目（遺失＝被踢者之既有存取權杖至遲於到期失效、換發被資料庫撤票擋下＝島 C 封頂；與既有 `kicked`／`revoked` 條目同形）。
- **款 6 wire 裁判面不開嚴格模式**：抽出之快照零 `additionalProperties`；後端多帶欄位之防線＝裁判案以表驅動之「序列化鍵集＝快照 properties 鍵集」斷言涵蓋全部受審讀型（含分頁信封；交叉型佔位之一型具名豁免附理由）。全域開啟留待專項。★本刀新增之讀型（使用者清單列與回收桶清單、政策投影等；實數以抽取為準）入受審名冊、同受該表驅動斷言（spec FR-064）；upstream `Api.SystemManage.User` 只入偏離帳比對面（ADR-00083）。
- **款 7 清單端點未知規則類型照原樣上 wire**：`wbip_type` 未知值只能源自直改庫（寫端守門使支援路徑只產二值）；`getIpRuleList` 照原樣上 wire（不過濾、不改契約與快照）；前端 ip-rule 頁對映射取不到之值於標籤映射與翻譯呼叫之前即退回顯原字串（不崩、不隱藏）；存取閘既有「略過＋告警」不變。
- **款 8 IP 存取閘每次阻擋恰一則結構化 warn、不設節流（by-design；BL-00084 已收）**：`middleware::ip_gate_mw` 判出阻擋時＝`ipgate_blocked_total` 推一格＋一則帶命中網段之結構化 warn（target `security.ipgate`）、回 `5003`；不設任何節奏 gate 或抑制。判準＝004 刀 spec FR-024「每次阻擋 MUST 留下帶命中網段之結構化可觀測紀錄」之直接推論：計數器刻意無 label（`obs::ipgate_blocked`），warn 一經抑制、被抑制之阻擋連命中哪一段都不留。阻擋不是降級、不推 `ip_domain_degraded_total`。代價＝本層跑在驗章之前、來源維節流（只管登入）在其下游 ⇒ 被擋來源得以請求速率單方面驅動日誌寫入量與 stdout 寫入鎖爭用。要壓＝改 FR-024 之粒度、或替計數器補 label 換取可抑制之粒度——皆屬拍板級、不在碼品質層自行處置。

**款號對照表**：

| ADR-00069 款 | 本 ADR 款 | 處置 |
|---|---|---|
| 1 解鎖端點 API-only、無 UI 按鈕 | 1 | **解除**（兩處 UI 入口；號不再配） |
| 2 dev 可達三態 | 2 | 續行 |
| 3 稽核覆蓋不對稱 | 3 | 改寫（寫入者全集擴列使用者域寫端八支與個人中心改密；封閉詞彙五詞→八詞） |
| 4 logout 弱 oracle | 4 | 續行 |
| 5 redis 不開持久化 | 5 | 續行（改述節流射程句＝登入節流判定面；補本刀新增 redis 狀態之自癒複核） |
| 6 裁判面不開嚴格模式 | 6 | 續行（補本刀新增受審讀型） |
| 7 未知規則類型上 wire | 7 | 續行 |
| 8 阻擋 warn 不設節流 | 8 | 續行 |

## 後果

- ADR-00069 整顆轉 superseded：本 ADR accepted 那一顆同批補 `supersedes: ["ADR-00069"]`、把 ADR-00069 之 status 改為 superseded、`superseded_by` 由 generate 回填（GT-04 對宣告者不看 status，故草稿期 supersedes 恆空）；續行鏈＝ADR-00040→ADR-00046→ADR-00069→本 ADR，讀前三者須併讀本 ADR。
- BL-00091 收（收刀事件 `backlog_done`；spec FR-060）。
- 機器錨（本刀 tasks 承載）：`AuditOperation` 字面釘值測自五詞改八詞（期望字面另寫一份、不由 `AuditOperation::ALL` 導出）；使用者域各寫端之稽核列數斷言取水位窗（成功恰一列、同值與被拒零列、批刪逐標的一列）；unlockLogin 帳號維包含規則拒＝零稽核、對未鎖標的照落一列；解鎖兩入口之 CDP 對照。
- 現在式改指、「八款」→「七款」、活書 11 IP 域已知態列之款 1 解除與款 3 寫入者集敘述同批改；依決定 2 之指令現算、改完復掃。
- 代價：多一顆 ADR；款號保留使款 1 成空號（對照表可查）。

## 翻案觸發器

- 款 2：dev 需要驗 CDN 相關信心態（例如引入本機 CDN 模擬）⇒ 重評 dev 信任模型。
- 款 3：稽核合規需求要求「一切設定變更可追溯」、系統設定寫端被重寫（008 刀系統設定頁進場時複核）、授權回收桶之 NoOp 移除須留痕（ADR-00081 款 12 翻案）、或使用者域同值提交須留痕（ADR-00080 決定 3 翻案）。
- 款 4：logout 需向呼叫端隱匿撤銷結果之場景出現、或弱 oracle 被證明可組合成實際攻擊。
- 款 5：出現「redis 重啟後狀態遺失」之實際事故、或新增不可自癒之 redis 狀態。
- 款 6：出現一次後端欄位外洩而裁判案未擋下之事故、或受審型數量使表驅動斷言不可維護。
- 款 7：出現支援路徑產生未知類型之缺陷、或 `wbip_type` 值域擴充（屆時契約、快照、前端映射同批改）。
- 款 8：可觀測性整刀開刀時、或 dev／prod 日誌量因阻擋告警出現實際問題時（先到者）。
