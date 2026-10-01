---
id: "ADR-00069"
title: IP 域已知態集（續行 ADR-00046）——款 1、2、4～7 續行（款 1 刀射程句座標改寫）、款 3 操作稽核寫入者集擴列三維授權寫端（update）與授權回收桶復原（restore）並以現行全集重述＋新款：IP 存取閘每次阻擋恰一則結構化 warn、不設節流（BL-00084 by-design）
date: 2026-10-01
status: proposed
supersedes: []
superseded_by: []
provenance: "006-authz-governance 之 spec FR-041⑦、FR-006、FR-030、FR-046（BL-00084 收刀 `backlog_done`）、FR-047（「七款」→「八款」、「限 R_SUPER」類）、SC-014（本刀 ADR 全數 accepted＝收刀帳本結清之一）；brainstorm §0 Q10、§2 BACKLOG 處置（BL-00084 收）、§3 §1 ADR 待立⑦、§3 §4 現在式假述掃除；被續行面＝ADR-00046 七款（body 已 accepted 不可變、rev6 無部分翻案機制＝ADR-00011 決定 5 先例；ADR-00046 之於 ADR-00040 為同形前例）；新款承載原住 005 刀 spec Out of Scope（觀測面「觀測 profile 首起」），因 ADR-00046 替代案 2 已否決單款 ADR 且本刀本須整顆續行而改由本檔承載；新款判準出處＝004 刀 spec FR-024＋BL-00084＋`middleware::ip_gate_mw` fn doc 之阻擋告警代價段；前代出處＝rev5:ADR 0042（rev5:004 已知態集，經 ADR-00046 對應本檔款 1／2／3／5／6）、rev5:server/src/middleware/mod.rs 模組 doc（每次阻擋一則 warn、零節奏 gate 與其代價）、rev5:006 as-built 稽核覆蓋（三維寫端 Applied 含空 diff 一列、復原 NoOp 零稽核）；draft 於 plan 期落 feature branch、user 親決於治理單元（accepted 同顆補 supersedes 並改 ADR-00046 狀態）"
tags: [ip-trust-anchor, authz-governance, known-state, wont-fix, by-design]
---

## 背景

- ADR-00046 集中承載 IP 域七款已知態（續行 ADR-00040）。本刀（006 authz-governance）使其款 3 之寫入者集字面成假述：三維授權寫端（updateRoleMenu／updateRoleButton／updateRoleEndpoints）與授權回收桶復原（restorePolicy）新增為 `sys_operation_log` 寫入者（spec FR-006）。ADR body 已 accepted 不可變（GT-04），只改活書會讓現在式面與 ADR-00046 字面相悖（權威鏈倒掛、RL-0047）；rev6 無部分翻案機制（ADR-00011 決定 5）⇒ 整顆續行。
- BL-00084（IP 存取閘每次阻擋皆發一則結構化 warn、無節流無抑制）於 brainstorm Q10 定為 by-design、併本續行承載：該條原由 005 刀 spec Out of Scope 之觀測面推往「觀測 profile 首起」，而 ADR-00046 替代案 2 已否決「獨立立一支單款 won't-fix ADR」、本刀又本須整顆續行 ADR-00046。
- 現在式面量測（2026-10-01；只供背景、施工以決定 2 之指令現算為準）：`python3 tools/docsync errata ADR-00046` 全 repo 46 處命中（量測當下本 ADR 與 ADR-00068 兩草稿尚未入版控、不在其內；入版控後其命中屬決定 2 之扣除面）；扣除史料面（brainstorms、specs、reviews）、生成鏡像（`docs/generated/`）、事件源與 ADR 檔（`docs/arc42/decisions/`）後，現在式面＝11 檔 20 處（逐檔 `grep -o`／`git -C <子庫> grep -o` 計）——外層 8 檔 16 處：`docs/arc42/06-runtime-view.md` 2、`docs/arc42/08-crosscutting-concepts.md` 3、`docs/arc42/11-risks-and-technical-debt.md` 3、`docs/arc42/12-glossary.md` 1、`docs/ops/RUNBOOK.md` 3、`docs/ops/BACKLOG.md` 2（BL-00043／BL-00091 條文）、`docs/ops/reference-src/trust-model-config.md` 1、`deploy/trust-model.dev.toml` 1；rust-api 2 檔 3 處：`server/src/middleware/mod.rs` 1、`server/tests/wire_schema.rs` 2；base-web 1 檔 1 處：`src/views/manage/ip-rule/index.vue` 1；另史述待判讀 1 處（`docs/ops/NOTES.md` 之 005 收刀條）。「七款」現在式 1 處（活書 11 IP 域已知態列標題；兩子庫 0）＋同一 NOTES 史述 1 處待判讀。其中活書 06、活書 12、RUNBOOK 各有一處引「ADR-00046 款 1」之同句含「限 `R_SUPER`」（決定 2 之「限 `R_SUPER`」★句）。

## 決策驅動因子

- IP 域已知態單一出處；BL-00084 於翻案時一併結清（收刀 `backlog_done`）。
- 款 3 以現行 `sys_operation_log` 寫入者全集重述、不以增量句疊加——寫入者全集一句可逐項對碼核對。
- 現在式鏡像以機器枚舉逐處改指（款號一對一）、不留對沖註。

## 考慮過的替代案

1. **BL-00084 另立單款 won't-fix ADR**：IP 域已知態散住兩支（ADR-00046 替代案 2 同判）；棄。
2. **款 3 擴列改寫進角色與選單之已知態 ADR（ADR-00068）**：稽核覆蓋不對稱之款住 IP 域 ADR 已兩代（ADR-00040 款 3→ADR-00046 款 3），拆開則寫入者全集散住兩支；棄（ADR-00068 款 12 之 NoOp 零稽核以互引連結）。
3. **替阻擋 warn 補節流、或替 `ipgate_blocked_total` 補 label 換取可抑制粒度**：須改 004 刀 FR-024 之粒度＝拍板級，Q10 已取 by-design；棄。
4. **只改活書與 RUNBOOK、不續行**：現在式面與 accepted 之 ADR-00046 款 3 字面相悖；棄。

對所選方案跑同一反例（RL-0013）：整顆續行是否讓 ADR-00046 七款失去原拍板時點之可追溯性？不會——ADR-00046 body 不動、轉 superseded 後仍可讀；本檔逐款標明「續行／改寫」並附款號對照表；成立。

## 決定

1. **ADR-00046 之款 1、2、4、5、6、7 原意續行**，現行依據＝本決定同號款（字面沿 ADR-00046、只做座標改寫：刀射程句改含 006 刀、交叉引用補本刀 ADR 號）；**款 3 改寫**如下；另增**款 8**。
2. **現在式面改指**：現在式面引用 ADR-00046 之處改指本 ADR 同號款（款號一對一；同句另含現況假述者依本決定之「限 `R_SUPER`」★句〔緊接下句〕一併改寫、不只換 ADR 號）；★改指「ADR-00046 款 N」之句另含「限 `R_SUPER`」者（例：解鎖端點之 API-only 敘述）併入 spec FR-047 之「限 R_SUPER」類種子逐處判讀——能力限定句改寫為現況（seed 預設只屬 R_SUPER、自本刀起可經端點權限彈窗授出非 R_SUPER＝本 ADR 款 1、ADR-00068 款 9）、seed 事實句保留；改指與此判讀同處施工、互為前提（只換號＝指針旁留假述；只判讀不改指＝仍指舊 ADR）；「限 R_SUPER」類處數以 ``python3 tools/docsync errata '限 `R_SUPER`'`` 與裸詞形並掃現量、tasks 逐處列；IP 域已知態計數句「七款」改「八款」並指本 ADR——★同詞「八款」在本刀前指角色與選單域之 ADR-00045（其計數句依 ADR-00068 決定 2 另改），兩域計數句一律帶 ADR 號；枚舉時 ADR 號與舊數量詞（「八款」「七款」）並掃、命中後以同句 ADR 號判定歸屬（RL-0011 四形）；活書 11 IP 域已知態列之款 3 寫入者集敘述與新款摘要同批改；ADR 檔（例：accepted 之 ADR-00057）與史料面不動（扣除面見下）。★史述逐處判讀：`docs/ops/NOTES.md` 之 005 收刀條（「本刀新增之已知態集中於…ADR-00046（IP 域七款）」，句中「本刀」＝005 刀、005 刀未產出款 8）屬 005 收刀史述，不預先要求改指與改款數——保留原 ADR 號與款數，或於收刀改寫 NOTES 時整句重寫。現在式面之判定＝`python3 tools/docsync errata ADR-00046` 全 repo 命中（含兩子庫，另以 `git -C <子庫> grep -o ADR-00046` 對賬）扣除史料面（brainstorms、specs、reviews）、生成鏡像（`docs/generated/`）、事件源與 ADR 檔（`docs/arc42/decisions/`；accepted body 不可變，含本刀續行 ADR 草稿自身——ADR-00068 與 ADR-00069——其對被續行者之引用屬續行面本身）；處數以施工時同指令現算為準、改完復掃（plan 期量測值住背景、不作施工基準）；實際改指屬本刀治理單元（兩子庫只改註、走兩段式 commit）。

**各款（現行依據）**：

- **款 1 解鎖端點 API-only、無 UI 按鈕**：`POST /systemManage/unlockLogin` 只有後端端點；前端包裝與按鈕不建。理由：按鈕的自然位置在使用者管理頁，該頁不在 004～006 刀射程；憲法 §III.2 該軌道 (i) 列明文「解鎖按鈕與其包裝不在本次授權」。按鈕權限碼已在 seed，使用者管理頁刀進場時零 seed 變更。★本端點自 006 刀起可經端點權限彈窗授予非 R_SUPER 角色，授出後無帳號維守門（ADR-00068 款 9；no-escalation 本體屬 007 刀、BL-00048）。
- **款 2 dev 經反向代理可達來源信心三態**：`fallback`／`proxy_clean`（信任模型決定）＋`chain_rejected`（轉發鏈跳數逾上界之判準不依賴信任模型、送逾上界之轉發鏈即端到端可達：登入端點拒絕並落一列稽核）；其餘五態由整合測試直餵信任模型覆蓋。端到端走查之結論只對此三態成立；不得把整合層結論寫成端到端已驗。
- **款 3 操作稽核覆蓋不對稱**（改寫）：`sys_operation_log` 之寫入者全集＝IP 規則四寫端（`add`／`update`／`delete`／`restore`）＋解鎖（`unlock`）＋角色寫端（新增／更新／刪除／批刪／首頁寫入）＋選單寫端（新增／更新／刪除／批刪／復原）＋三維授權寫端（updateRoleMenu／updateRoleButton／updateRoleEndpoints；`update`，Applied 含空 diff 恰一列、Rejected 與查無角色零列）＋授權回收桶復原（restorePolicy；`restore`，Applied 恰一列、NoOp 零列〔已知態＝ADR-00068 款 12〕、不可復原零列〔ADR-00065 決定 7〕）；動作詞彙沿封閉五詞、零新詞；既有系統設定寫端維持不落稽核列（002 刀刻意決定）。⇒ 查詢端不得據此表宣稱「所有管理操作皆有稽核」。
- **款 4 logout 故障窗弱 oracle（won't-fix）**：DB 故障窗內 logout 對「簽章有效的票」回 `5000`、對垃圾票回 `0000`，可據以分辨票的簽章有效性。只在故障窗可見、只洩持票者手上那張票的有效性、refresh 端點對持票者本即回應可用性；保留 `5000` 使 API 呼叫端知道撤銷未成。折成 `0000` 會把「撤銷未成」回報為成功——不取。
- **款 5 redis 不開持久化**：解鎖標記遺失的後果＝至多少解鎖一次、可再解鎖自癒；節流判定面不依賴 redis（ADR-00038）；會話面暴險由島 C 封頂（PG 為權威）。維持現狀。
- **款 6 wire 裁判面不開嚴格模式**：抽出之快照零 `additionalProperties`；後端多帶欄位之防線＝裁判案以**表驅動**之「序列化鍵集＝快照 properties 鍵集」斷言涵蓋**全部受審讀型**（含分頁信封；交叉型佔位之一型具名豁免附理由）。全域開啟留待專項。
- **款 7 清單端點未知規則類型照原樣上 wire**：`wbip_type` 未知值只能源自直改庫（寫端守門使支援路徑只產二值）；`getIpRuleList` 照原樣上 wire（不過濾、不改契約與快照）；前端 ip-rule 頁對映射取不到之值**於標籤映射與翻譯呼叫之前**即退回顯原字串（不崩、不隱藏）；存取閘既有「略過＋告警」不變。
- **款 8（新）IP 存取閘每次阻擋恰一則結構化 warn、不設節流（by-design；BL-00084）**：`middleware::ip_gate_mw` 判出阻擋時＝`ipgate_blocked_total` 推一格＋一則帶命中網段之結構化 warn（target `security.ipgate`）、回 `5003`；不設任何節奏 gate 或抑制。判準＝004 刀 spec FR-024「每次阻擋 MUST 留下帶命中網段之結構化可觀測紀錄」之直接推論：計數器刻意無 label（`obs::ipgate_blocked`），warn 一經抑制、被抑制之阻擋連命中哪一段都不留。阻擋不是降級、不推 `ip_domain_degraded_total`。代價＝本層跑在驗章之前、來源維節流（只管登入）在其下游 ⇒ 被擋來源得以請求速率單方面驅動日誌寫入量與 stdout 寫入鎖爭用。要壓＝改 FR-024 之粒度、或替計數器補 label 換取可抑制之粒度——皆屬拍板級、不在碼品質層自行處置。

**款號對照表**：

| ADR-00046 款 | 本 ADR 款 | 處置 |
|---|---|---|
| 1 解鎖無 UI 按鈕 | 1 | 續行（刀射程句改含 006 刀；補授出後無帳號維守門之互引） |
| 2 dev 可達三態 | 2 | 續行 |
| 3 稽核覆蓋不對稱 | 3 | 改寫（寫入者全集擴列三維授權寫端 `update` 與授權回收桶復原 `restore`） |
| 4 logout 弱 oracle | 4 | 續行 |
| 5 redis 不開持久化 | 5 | 續行 |
| 6 裁判面不開嚴格模式 | 6 | 續行 |
| 7 未知規則類型上 wire | 7 | 續行 |
| —— | 8 | 新增（阻擋 warn 不設節流＝BL-00084 by-design） |

## 後果

- ADR-00046 整顆轉 superseded：本 ADR accepted 那一顆同批補 `supersedes: [ADR-00046]`、把 ADR-00046 之 status 改為 superseded、`superseded_by` 由 `python3 tools/docsync generate` 回填（GT-04 對宣告者不看 status，故草稿期 supersedes 恆空）；續行鏈＝ADR-00040→ADR-00046→本 ADR，讀前兩者須併讀本 ADR。
- BL-00084 收（收刀事件 `backlog_done`；spec FR-046）；`middleware::ip_gate_mw` fn doc 之「要壓屬拍板級」句與本款同義、碼零改。
- 現在式改指、「七款」→「八款」、活書 11 IP 域已知態列之款 3 與新款摘要，依決定 2 之指令現算、改完復掃。
- 代價：多一顆 ADR；IP 域已知態之讀法多一層續行。

## 翻案觸發器

- 款 1：使用者管理頁刀（007 刀）開工。
- 款 2：dev 需要驗 CDN 相關信心態（例如引入本機 CDN 模擬）⇒ 重評 dev 信任模型。
- 款 3：稽核合規需求要求「一切設定變更可追溯」、系統設定寫端被重寫、或授權回收桶之 NoOp 移除須留痕（ADR-00068 款 12 翻案）。
- 款 4：logout 需向呼叫端隱匿撤銷結果之場景出現、或弱 oracle 被證明可組合成實際攻擊。
- 款 5：出現「redis 重啟後狀態遺失」之實際事故、或新增不可自癒之 redis 狀態。
- 款 6：出現一次後端欄位外洩而裁判案未擋下之事故、或受審型數量使表驅動斷言不可維護。
- 款 7：出現支援路徑產生未知類型之缺陷、或 `wbip_type` 值域擴充（屆時契約、快照、前端映射同批改）。
- 款 8：可觀測性整刀開刀時、或 dev／prod 日誌量因阻擋告警出現實際問題時（先到者；沿 BL-00084 原觸發）。
