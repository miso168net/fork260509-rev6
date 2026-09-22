# 004-ip-trust-anchor 規格對照審查（spec-compliance-004、2026-09-22）

範圍＝已收刀之 004 ip-trust-anchor 刀對 `specs/004-ip-trust-anchor/` 的兌現度：spec.md FR-001～FR-070、SC-001～SC-016、User Story 1～6、Clarifications Session 2026-09-15 三題、Edge Cases、Assumptions、Out of Scope，連同 data-model §1～§8、`contracts/` 五份（trust-model-config／wire-ip-rule／wire-throttle-unlock／wire-auth-delta／code-gates）、quickstart.md、tasks.md、checklists/requirements.md。對照基準＝HEAD 現況（外層 `fd9f99f`／rust-api `af9b2ec`／base-web `3fb3ea31`）；004 收刀範圍（外層 `bfaba0e..b15b96d`、merge `990c4a7`、簿記 `42d093e`、perf `ef03c80`）與其後 005 前維護批七支（merge `fd682da`／`9b932d8`／`fdf181f`／`f91ba0d`／`d4f33b7`／`dc32264`／`a0b8672`）只作歸因。偏離有憲法／ADR／BACKLOG／clarify／commit 所引拍板承載者不報。specs 本文不改（ADR-00012 定點快照；user 2026-09-22 裁定）。

## 0. 方法與取證

| 項 | 值 |
|---|---|
| 形式 | RL-0073 承載處②：user 2026-09-22 臨時發起、附屬 004 刀；分支 `maint-spec-compliance-004`（自 `rev6-admin-root @ fd9f99f`，即 005 前維護批七支收官後） |
| 編排 | **兩支唯讀 Workflow**（射程互斥；review 骨架 explore＋inline 兩鏡三態；全角色 `opus[1m]` xhigh、零 CDP）。run A＝`wf_b1d4020a-658`（五 lens＋一冷啟動探針；最壞 18／保險絲 19），派 18 支、零錯零 null、牆鐘 38.6 分；run B＝`wf_13f0723b-e36`（五 lens；最壞 15／保險絲 16），派 15 支、零錯零 null、牆鐘 26.8 分 |
| 切成兩支的理由 | 004 之 FR 數為 003 的 1.75 倍（70 vs 40）、契約多一份、另有管理頁進場與六支碼面閘；單 run 六鏡會使每鏡背約 12 條 FR（003 為 7 條）。★另需一支**專鏡**核「七支維護批對 004 碼面的改動有無承載」——003 那輪無此面 |
| run A lens | L1 信任錨與真實來源還原（FR-003～018、SC-001～003、data-model §1～§3、trust-model-config 契約）｜L2 IP 存取閘判定與韌性（FR-019～024、SC-004／005）｜L3 規則五端點與防自鎖與操作稽核（FR-025～029＋043、SC-006、wire-ip-rule）｜L4 來源維節流與 PG 定案與解鎖（FR-030～042＋045、SC-007～009、降級矩陣、wire-throttle-unlock／wire-auth-delta）｜L5 管理頁前端與 fork-delta×憲法 §III（FR-048～053＋055、SC-010、★軌道 (i)）｜P1 冷啟動探針三題 |
| run B lens | L6 五契約逐列與 wire 碼表（FR-001／002／044／049／054、SC-011、13 碼矩陣）｜L7 憲法 Amendment 與治理進場與帳本（FR-056～062＋066～069、SC-012／016、code-gates）｜**L8 收刀後變動承載歸因**（七支維護批；五處必查）｜L9 測試與閘保護力（不變式驅動變異推演）｜L10 Edge Cases 與 Assumptions 與 Out of Scope 與 checklists（FR-046／047、data-model §4／§7／§8、quickstart） |
| 前兩輪經驗 | CONTEXT 烤入七條：BL 到期落點須明寫／逐字出自 accepted ADR 或 specs 之句不得單改現在式面／evidence 可原樣重跑／不逐檔列易漂移名冊／★機器枚舉先證樣式集完備再證零命中（RL-0002）／★錨字面出現在解釋它的散文裡＝恆綠無聲／spec-compliance-002 與 003 已處置者不重報 |
| 規則塊 | `rules emit --scope review` 全塊烤入，RULES-VERSION `0bbc9765d102`；★另烤入 RL-0078 防污染條款 |
| 唯讀邊界 | agent 禁寫入形命令、禁 docker／cargo／pnpm／generate；rev5 樹只讀（各 lens 自陳僅唯讀 grep、零 git 寫入）；python 工具之保護力以記憶體內 exec 變異取證 |
| 主線復核 | 35 筆逐筆重讀證據與兩鏡理由，去重後 30 筆；★十筆機器複驗見 §3；★兩筆處置經主線改判（見「兩鏡分歧之主線裁定」） |
| 未覆蓋 | SC-010 之管理頁 CDP 端到端（承載＝004 刀 U12 走查 52 項）、SC-014 之反向代理雙來源實機演練（承載＝004 刀 T054／T067 走查）；本輪靜態為主、零 CDP |

## 1. 結論

**零 blocker、零 wire 行為缺陷。** 五份契約逐列與 HEAD 一致（碼／msg／HTTP 零偏離）；ROUTES 22、`MSG_KEYS` 19 與三檔 backend 子樹雙向全等、13 碼矩陣零新變體、零 migration 零 seed 變更皆實證兌現；島 F 八條、三層判定序與兩層覆蓋、存取閘六步序與白＞黑、防自鎖零寫入、節流兩維合成與每次讀設定現值、解鎖稽核先於生效——行為面逐條在案。★**七支維護批對 004 碼面的改動全部找得到承載**：`PageRes` 上移後 IP 規則清單的 wire 位元形逐欄未變、`handler/common.rs` 收攏後防自鎖與同交易稽核行為等價、i64 守衛 lint 未誤列 004 型、測試側 Drop 還原殼收攏後兩支寫端守衛等價；base-web 自 004 收刀後零改動。

要處置的集中在四類：①**現在式指針與權威歸屬失準**——`deploy/trust-model.dev.toml` 檔頭在 ADR-00041 抽家後留下折行死指針（且 GT-06 兩條正則皆為單行形、閘靜默）、`obs.rs` 四處把降級值名權威指向凍結 spec 而與活書相反、活書 10 的 UI 一致性量測欄未隨 clarify 第三題換判準；②**跨刀活體契約節過期**——`code-gate-contracts.md` 的 fork-delta-lint 節仍 002 原文（軌道名集／刀名／註解形／vacuous 前提四項皆與 as-built 不符）、view-render-guard 禁用字面少列兩條、route-artifact-gate 環境缺席語意寫錯；③**測試保護缺口**——防自鎖更新腿「移除舊值」半邊與來源信心「值域恰八態」皆零機器守（兩筆皆已補並變異自證）；④**兩筆與凍結權威相衝、只能對沖**——ADR-00040 款 2 的「dev 只可達二態」與 as-built 三態不符、ADR-00039 與 ADR-00040 零 rev5 provenance 與 FR-067 不符，兩者 body 皆不可變（GT-04），立 BACKLOG 對沖。

## 2. findings 與三分流（35 筆原始、去重 30 筆：修 12／轉 BL 12 條／駁回 2／報告記載 7）

> 去重＝`deploy/trust-model.dev.toml` 死指針由四支鏡各報一次（L1-1／P1-P1／L6-1／L10-4）、route-artifact-gate 契約語意兩支（L6-2／L8-2）、子庫碼註引凍結 spec 兩支（L8-1／P1-P2）。

| 編號 | 嚴重 | 類別 | 面 | 一句話 | 處置 |
|---|---|---|---|---|---|
| L1-1（＋P1-P1／L6-1／L10-4） | major | 現在式文件失準 | `deploy/trust-model.dev.toml` 檔頭 | 契約指針折成兩行，ADR-00041 抽家時只改第二行，兩行黏起來＝不存在的路徑；GT-06 兩正則皆單行形、lint 對該檔零命中 | 修（＋閘盲點轉 BL-00114） |
| L1-2 | minor | spec 自身缺陷 | spec FR-011 末句 | 「只認 IPv4-mapped 形不誤清 IPv4-compatible 以外的合法集合」前後兩半互斥 | 報告記載（real 鏡駁回、decided 鏡確認；主線裁定見下） |
| L1-3 | minor | 測試保護缺口 | `test_kit.rs::dev_trust_model()` | dev 信任模型網段值三份手抄鏡像、零機器對賬 | 轉 BL-00115 |
| L2-1 | minor | 現在式文件失準 | `obs.rs` 降級名冊碼註 | 列四種 `doorbell_subscribe` 觸發，實際發射五處 | 修 |
| **L3-1** | **major** | 測試保護缺口 | `handler/ip_rule.rs` 防自鎖 | FR-028 更新腿「移除舊值」半邊零機器守 | 修（新增判別案＋變異自證） |
| L3-2 | minor | 契約漂移 | `handler/ip_rule.rs` `MAX_CURRENT` | 清單端點對 `current` 加契約未宣告的上界 clamp | 轉 BL-00116 |
| L4-1 | minor | spec 自身缺陷 | wire-auth-delta 契約測試增斷言 | 要求 refresh／logout 各補「`peer_ip` 落欄」契約案，但兩端點寫的 `session_event` 無該欄＝義務結構上不可兌現 | 報告記載 |
| L4-2 | minor | spec 自身缺陷 | quickstart §4 | 宣稱可觀察來源維達 50 次 locked，但軟門檻 10 後每發皆被驗證碼閘擋在落列前、桶停在 10 | 報告記載 |
| L4-3 | minor | spec 自身缺陷 | spec FR-042 | 「帳號維計數查詢本體零改動」與同刀 FR-017 的 `chain_rejected` 排除過濾相衝 | 報告記載（decided 鏡駁回） |
| **L5-1** | **major** | 契約漂移 | `code-gate-contracts.md` §4 | 自稱跨刀活體的 fork-delta-lint 節仍 002 原文，四項與 as-built 不符 | 修 |
| **L5-2** | **major** | 現在式文件失準 | 活書 10 §10.1 | UI 一致性量測欄仍寫「CDP 三方比對零差異」，clarify 第三題已改判準且新判準現在式面零承載 | 修 |
| L5-3 | minor | 現在式文件失準 | 憲法 §III.2 vs 活書 08 | 「新增型圈界數」兩權威量法不同、同批標記給出不同數字 | 修（活書釘量法並分列）＋轉 BL-00118（憲法側；user 裁定） |
| L5-4 | minor | 測試保護缺口 | 管理頁 `#header-extra` | 「無權時不得退回渲染備援按鈕」零機器守零帳本承載 | 轉 BL-00117 |
| L5-5 | minor | spec 自身缺陷 | spec ★軌道收錄準則 | 稱管理頁三檔屬 §III.1 純新增檔，as-built 標記名不在 §III.1 三軌道 | 報告記載 |
| **L6-2（＋L8-2）** | **major** | 契約漂移 | `code-gate-contracts.md` §3② | route-artifact-gate 環境缺席語意寫「無 node」，as-built 為 docker／compose／容器三判準 | 修 |
| L6-3 | minor | 契約漂移 | `code-gate-contracts.md` §3① | view-render-guard 禁用字面列三條，`FORBIDDEN` 實為五條 | 修 |
| L7-1 | major | 現在式文件失準 | 憲法 §I.7 段首括號註 | 「rev6 增補恰四處」為 1.3.0 遺留，1.4.0 已改島 E 四處 | 轉 BL-00119（user 裁定） |
| L7-2 | minor | FR／SC 未兌現 | ADR-00039／00040 | FR-067 要求七支 ADR 皆帶 rev5 provenance，此二支零出處 | 轉 BL-00120 |
| L7-3 | minor | spec 自身缺陷 | spec FR-068 | 要求改 §01／§03 之「L1 敘述」，該二節 L1 全為 C4-L1 圖層名 | 報告記載（decided 鏡駁回） |
| L7-4 | minor | spec 自身缺陷 | spec SC-016 | 「backlog_done 八條、backlog_add 兩條」與 as-built（10／21）對不齊 | 報告記載（decided 鏡駁回） |
| L8-1（＋P1-P2） | major | 契約漂移 | rust-api 三處碼註 | 仍以 specs 凍結存證為 trust-model-config 契約權威 | **駁回**（見下） |
| L8-3 | major | 測試保護缺口 | `walkthrough-baseline.py` `IPGATE_CHANNEL` | 門鈴頻道字面第二個機器消費家、與 rust-api 單一宣告零錨 | 轉 BL-00121 |
| L8-4 | minor | 其他 | `route-artifact-gate.py` | 沙盒旗標 `box_live` 於 `observe()` 之後才置，窗內 GateError 使沙盒無人清 | 轉 BL-00122 |
| **L9-1** | **major** | 測試保護缺口 | `trust/mod.rs` 八態 | FR-007「值域恰八態」無機器腿釘變體數 | 修（窮盡守＋變異自證） |
| L9-2 | minor | 測試保護缺口 | `obs.rs` `request_context_absent` | 每請求腿數只有逐腿案、無總數案 | 轉 BL-00123 |
| **L10-1** | **major** | 現在式文件失準 | `obs.rs` 四處 | 把降級值名「單一權威」指向凍結 spec，與活書「值集單一權威＝`obs.rs` 常數」直接相反 | 修 |
| **L10-2** | **major** | 現在式文件失準 | RUNBOOK §16.1／活書 06／活書 11 | 三處宣稱 dev 端到端只可達二態，`chain_rejected` 為第三個可達態 | **改判**：三處加對沖註＋轉 BL-00125（見下） |
| L10-3 | minor | 無承載偏離 | spec Out of Scope 首條 | 「通用化節流 seam」在現在式帳本零承載 | 轉 BL-00124 |
| P1-P3 | minor | 檢索性 | RUNBOOK §13 403 分診 | 把誤擋導向改 IP 規則，該改動涵蓋自身會被 `selfLock` 拒絕，全檔零該字面 | 修 |
| P1-P4 | minor | 檢索性 | RUNBOOK §9 解鎖段 | 稱缺「誰正被鎖、該解哪一維」判斷入口 | **駁回**（refuter 鏡） |

### 兩鏡分歧之主線裁定（3 筆）

- **L1-2（real 駁回／decided 確認）→ 報告記載。** 兩半確實互斥（「只認 IPv4-mapped」推出 IPv4-compatible 不清，「不誤清 IPv4-compatible **以外**的合法集合」把它排除在保護面外），但 HEAD 取前半且有對照案 `trust_model_plain_v4_and_non_mapped_v6_literals_load_without_warning` 釘住、現在式權威 `docs/ops/reference-src/trust-model-config.md` 之載入失敗語意表亦只列 IPv4-mapped 一形——現在式面無需變更、亦無須新 ADR。記載之目的＝避免後刀照後半讀法把判準放寬成 `to_ipv4()` 而誤清合法集合。
- **L4-3／L7-3／L7-4（decided 鏡駁回）→ 報告記載。** 三筆皆為 spec 內部措辭與 as-built 的對不齊，無現在式面後果、無後刀義務。
- **L8-1＋P1-P2（decided 鏡駁回／refuter 鏡確認）→ 駁回。** RULES 名詞段把兩 gitlink（子庫工作樹）明文排除在「現在式面」之外，ADR-00041 決定 4 之涉及檔與決定 5 之 GT-06 新腿射程皆只及現在式面；**同一件事已於 `maint-backlog-42` 的 final holistic review 由兩鏡一致駁回**（理由＝子庫面不在該 ADR 射程）。本筆未附新證據證明該處置未落地或落地錯——「三處對一處」只是數量差、不動「不在射程」的類別判準——依「已駁回者不得重報」駁回。★區辨：同屬子庫碼註的 **L10-1 不在此列**，其問題不是指標指向凍結存證，而是與活書對**同一值集**各自宣稱「單一權威」，屬 RL-0049 面、故修。

### 修（12 筆，本輪落地）

- **L1-1**：刪 `deploy/trust-model.dev.toml` 檔頭第一行行尾殘留的目錄前綴，只留第二行的活體家路徑。成因＝ADR-00041 之四十二處改指只換掉帶檔名的那一行、漏掉拆在上一行行尾的目錄前綴。閘盲點另轉 BL-00114（屬新判準面、不併入本修）。
- **L2-1**：`obs.rs` 之 `doorbell_subscribe` 觸發枚舉補第五種（watcher 啟動時 redis URL 解析失敗），並改為「發射處數以 grep 現算、本註不釘值」。
- **L3-1**：`handler/ip_rule.rs` 新增 `update_self_lock_guard_drops_the_target_row_before_judging`——佈局 allow 涵蓋自己（墊底）＋同段 deny，再把該 allow 改到別段；正解為 after 集合移出 allow、只剩 deny ⇒ 自鎖拒寫，漏移除則白＞黑誤放。變異取證見 §3。★附帶查清（lens 未述）：**軟刪腿的 `gone` 其實有既有案守著**，缺口專屬更新腿。
- **L5-1**：`code-gate-contracts.md` §4 四項改對——兩腿之現況實數改為 grep 現算形（不再釘「002 刀 vacuous」歷史值）、註解引導改為依檔型而異（`.vue` template 為 `<!-- -->`）、軌道名改為工具側 `TRACK` 正則且明載 §III.2 表外宣告 3 之頁進場標記同樣合法、刀名改為「該檔進場刀之 `NNN-slug`」。
- **L5-2**：活書 10 §10.1 UI 一致性量測欄改為 clarify 第三題之判準（結構清單七項逐項全等才綠；截圖間距、字體、顏色差異只記不擋），已知例外句保留。
- **L5-3（修半）**：活書 08 §8.4 釘死量法——圈界形（`START]`／`END]` 成對計一塊）與單行形分計、憲法範圍欄之「新增型圈界數」只數圈界形塊；逐檔改為兩欄形，合計以現算為準（圈界塊 13／單行形 23／修改型 15，與 `grep -c ' START]'` 及 `grep -c '原行:'` 交叉對上）。
- **L6-2（＋L8-2）**：§3② 環境缺席語意改為 as-built 三判準（`docker` 不在 PATH／compose 兩檔任一缺／base-web 容器未起＝具名跳過 rc 0；容器在而憲法列或基線種子不完整＝rc 2；基線源倉缺席＝只第三腿跳過並警告）。
- **L6-3**：§3① 禁用字面補足五條並改為「以工具常數 `FORBIDDEN` 為準、本檔不另釘值」。
- **L9-1**：`trust/mod.rs` 測試模組新增 `CONFIDENCE_ALL` 八元名冊＋`confidence_ordinal` 窮盡 match＋`confidence_value_domain_is_exhaustively_pinned_at_eight`。新增變體 ⇒ 該 match 不再窮盡 ⇒ 測試目標編譯失敗。
- **L10-1**：`obs.rs` 四處改為「值名以本常數為準＝現在式單一權威（活書同判），004 當時枚舉之凍結存證＝spec data-model §5」。
- **L10-2（現在式面半）**：RUNBOOK §16.1、活書 06 島 F ⑧、活書 11 已知態列三處加對沖註，指 BL-00125；「二態」字面不動（忠實於 ADR-00040 款 2）。
- **P1-P3**：RUNBOOK §13 403 分診末句補防自鎖座標（`2222`／`biz.ipRule.selfLock`、規則列與稽核列皆零寫入、須改自其他來源），事實指向活書既有兩處家，符合該段「只給座標」形制。

### 主線復核自查追加（2 筆，lens 未報）

- **RL-0020 違規**：`code-gate-contracts.md` 三處沿用「本刀」字面，而該檔屬跨刀存活面。三處改為「002 刀」形。★BL-00104 只點名 `schema-definition.md`，本檔為同類之外的第二份；本輪當批收掉、不另立 BL。
- **RL-0011 同源假述**：`tools/fork-delta-lint.py` 的模組 docstring 與被改的契約節寫同一句過期的「軌道名 ∈ §III.1 表首欄字面」。改對為與本體 `S1_NEW_FILE_FACE` 射程界定一致的敘述。★工具**本體**判準正確（名冊外之名刻意不做名冊斷言，條文就在該常數註內），失準的只有 docstring。

## 3. 驗證（主線實跑）

| 項 | 值 |
|---|---|
| 新增 Rust 案 | 容器內 `cargo fmt -p server` 後 `tools/rust-fmt-gate.py check` 全綠（2.1s）；★三個憲法例外面（`entity/`／`migration/`／`sea-orm-adapter/`）`git diff --stat` 為空＝零改動自證 |
| **變異取證①**（L9-1） | 加第九態 `MutantNinth` ＋補 `Confidence::as_str` 的 arm → `cargo test --workspace --no-run` **僅一個錯誤**＝`error[E0004]: non-exhaustive patterns: trust::Confidence::MutantNinth not covered`（命中新增之 `confidence_ordinal`）。★「僅一個」同時反證了缺口：若無此守，補了 arm 即編譯通過、兩支既有案全綠。還原後該案復綠 |
| **變異取證②**（L3-1） | ①先打廣義變異（四寫端共用守之 `rows_after(active, gone, added)` → `None`）：新案與**既有案皆紅**——證明軟刪腿另有既有案覆蓋，finding 的變異描述過寬；②改打 finding 所指的那一格（`RuleWrite::Update` 臂之 `gone` → `None`）：**只有新案紅、既有案綠**＝缺口專屬更新腿、新案為其判別腿。兩次皆自備份還原並復驗 |
| 全量 | 容器內 `cargo test --workspace --no-fail-fast -- --test-threads=1` **全綠 0 紅 2 ignored**（lib 577＝原 575＋本輪 2；各 target 合計 772 案） |
| 走查基準 | 全量測試前後 `walkthrough-baseline diff` **全等**（表 16／序列 11／redis 0 鍵、0 前綴）＝零殘列 |
| 十筆機器複驗 | 死指針（拼接路徑 `ls` 不存在＋lint 對該檔命中 0）｜`gone` 六處全在 src、測試側零引用｜八態 `table` 與 `all` 皆手寫八元｜`FORBIDDEN` 5 條 vs 契約 3 條｜`doorbell_subscribe` 發射 5 處 vs 碼註 4 種｜`obs.rs` 4 處指凍結 spec vs 活書指 `obs.rs`｜dev 三態（三處宣稱二態＋`login.rs` 之 `ChainRejected` 早退腿）｜活書 10 判準 vs clarify（`結構清單` 於現在式面零命中）｜憲法「增補恰四處」在案｜ADR-00039／00040 之 `rev5` 命中各 0（其餘五支 1／1／1／6／9） |
| 工具自測 | `fork-delta-lint.py test` 綠；`docsync lint` ＝2 錯／12 警——2 錯皆 GT-01 生成檔漂移（`STATE.md`／`reference/perf.md`，未 commit 之 `close_bookkeeping` perf 事件所致之既有在途態、簿記時 generate 消除），12 警皆 GT-03 新配號在途落帳窗口（BL-00114～00125，由本輪 review 事件之 `backlog_add` 消除） |

## 4. 冷啟動探針（只入報告與事件 notes、不填事件 `probe` 欄）

| 題 | 判分 | 最短跳數 | 註 |
|---|---|---|---|
| Q1 兩層反向代理下如何決定真實來源位址與其可信度；判不出來時如何 | 繞路 | 2 | 純函式 `trust::resolve_client_ip`（零 I/O 零狀態）；鏈＝`normalize_xff(XFF) ++ [peer]`、**取窗先於解析**（由右往左留最右 `MAX_XFF_TOKENS`＝32 欄）；三層固定序＝對端閘／Tier-1 CDN 錨（F6 硬化以全稱量詞掃錨右整段）／窗內推導；判不出＝`fallback` |
| Q2 新增涵蓋自身來源的阻擋規則會如何；寫入後要不要重啟 | 繞路 | 2 | 寫不進去——四寫端於業務列落庫前、同一交易內跑 `guard_self_lock`（交易內現讀→套變更→`build_ruleset`→`would_self_lock`）；不需重啟，寫端成功後重載並發門鈴 |
| Q3 同來源輪換帳號名連續失敗如何處理、如何解開、留下什麼紀錄 | 繞路 | 2 | 來源維節流接手（兩維並列合成）；解鎖端點兩維擇一、稽核先於生效、未鎖標的亦回 `0000` |

找不到 0、答錯 0。三題皆「繞路」＝答案正確但導航跳數高於最短路徑；grader 指出共同成因＝活書 §6.1 島 E／島 F 兩情境的表格列極長，逐題答案散在單列內。不填 `probe` 欄之理由同 002／003 兩輪報告（檢索性列取最近一筆帶 `probe` 之 review 事件、不分 scope、比輪間不降，題組不同質）。

grader 對探針 suggestion 之處置：採納者成為 P1-P1～P1-P4（P1-P1 併入 L1-1、P1-P2 併入 L8-1 而駁回、P1-P4 經 refuter 鏡駁回）。

## 5. 建議（未列為 finding）

1. **活書 §6.1 兩情境表格列過長**（探針三題皆「繞路」之共同成因）：島 E 與島 F 的單列內含完整判定序與降級矩陣，冷啟動讀者須逐列掃讀才能定位。可在 000-r3 的檢索性面一併評估拆列或加小標。
2. **`wire-ip-rule` 契約未隨 ADR-00041 抽出活體家**：本輪寫 BL-00116 時被 GT-06 擋下（現在式面不得引 spec 契約），而該篇並不在抽出的六檔內＝現況只有凍結存證一份。與 BL-00105／BL-00112 同屬 wire 裁判面缺口，005 動 `tests/wire_schema.rs` 時可一併評估。
3. **L9 推演存活但後果窄的變異**（lens 自陳未報）：存取閘六步序中「健康端點放行」與「請求上下文」兩步對調（現況兩步皆不寫狀態、可觀察差異只在 metrics 標籤）；`build_ruleset` 對同段 allow／deny 並存時的插入序（集合語意下結果不變）。

## 6. 判定

**需要後續處置：是（本輪即處理完）。** 十二筆修落於本輪修單、十二條轉 BACKLOG（BL-00114～BL-00125，含 user 2026-09-22 逐題裁定之兩條憲法面併案項）、兩筆駁回、七筆報告記載；另主線復核自查追加兩筆當批收掉。specs 本文與憲法零改動；rust-api 三檔改動（兩支新案＋碼註）、外層八檔改動。
