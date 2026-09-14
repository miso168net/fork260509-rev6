# 002-system-settings 規格對照審查（spec-compliance-002、2026-09-15）

範圍＝已收刀之 002 system-settings 刀對 `specs/002-system-settings/` 的兌現度：spec.md FR-001～FR-030、SC-001～SC-009、User Story 1～6、clarify Q1～Q5，連同 data-model §1～§8、`contracts/wire-settings.md` §1～§5、`contracts/code-gates.md` §1～§6。對照基準＝HEAD 現況（外層 `f2f57a4`／rust-api `e978900`／base-web `ff528496`）；002 收刀範圍（外層 `68512c0..934c64a`、rust-api `d443278..4ebd6ce`、base-web `8fea31ea..50812f89`，merge `ecea8ee`）只作歸因。偏離有 ADR／BACKLOG／clarify／commit 所引拍板承載者不報。specs 本文不改（ADR-00012 定點快照；user 2026-09-15 裁定）。

## 0. 方法與取證

| 項 | 值 |
|---|---|
| 形式 | RL-0073 承載處②：user 2026-09-15 臨時發起、附屬 002 刀；分支 `maint-spec-compliance-002`（自 `rev6-admin-root @ f2f57a4`） |
| 編排 | 一支唯讀 Workflow（run `wf_7281df94-3c9`；review 骨架 explore＋inline 兩鏡三態；最壞 12 支／保險絲 13）：三支 lens＋一支冷啟動探針，派 12 支、零錯零 null、牆鐘 20.5 分鐘；全角色 `opus[1m]` xhigh |
| lens | L1 產品面兌現（FR-001～016／019／020／022、SC-001～005／007、US1～5、clarify Q1～Q4、data-model §1～§8）｜L2 契約與治理面（FR-017／018／021／023～030、SC-006／008／009、US6、clarify Q5、wire-settings §1～§5、code-gates §1～§6）｜L3 收刀後變動之承載歸因（15 組變動 commit→受影響之 002 條文→承載處、`ecea8ee` 收單未收項①～④、現在式面） |
| 探針 | P1 三題（新增設定鍵之改動面與守衛／R_ADMIN 呼叫寫端之回應與規則真源／容器缺席時 wire 契約閘的處理），grader 判分＋refuter 覆核衍生 finding |
| 規則塊 | `rules emit --scope review` 全塊烤入，RULES-VERSION `a2721b391067` |
| 唯讀邊界 | agent 禁寫入形命令、禁 docker／cargo／generate；rev5 樹只讀（各 lens 自陳僅唯讀 grep、零 git 操作） |
| 主線復核 | 依 CLAUDE.md §5 不採信回報：11 筆逐筆以 grep／`git show` 重現證據；另核 BACKLOG 檔頭「動 X」定義與 `e0dd22b` L5-4 裁定（L1-2 落點）、ADR-00010／00016／00018／00019 與 `tools/schema-gate.py` 環境異常路徑（L2-3）、`rules emit` 三 scope 對「碼面閘」零命中（L2-3 影響面）、`tests/*` 與 `tools/docsync` 對「現＝」零解析（L2-4）、`real_app` 消費者現況（L3-1）；三發變異抽驗見 §3 |
| 未覆蓋 | FR-001／SC-007 需起 stack 走 quickstart，靜態不可驗（`ecea8ee` 收單訊息有復跑紀錄）；FR-024 前端 typecheck 未實跑 |

## 1. 結論

**零 blocker、零 wire 行為缺陷。** 002 的產品面、契約面、治理面在 HEAD 全數兌現；收刀後改動 002 所建面的 15 組變動都找得到承載（003 spec 各 FR、ADR-00023／00026／00027／00028／00029／00031、BL-00037③、BL-00046），無無承載偏離。002 生產碼（`handler/system_settings.rs`、`validation.rs`、`model/facade/system_settings.rs`、`envelope.rs`）收刀後的非註解變動全落在 `#[cfg(test)]` 區，registry 值域、三態、2222／5000、審計欄成對、讀端 16 鍵與排序都照 002 spec。

要處置的是三處測試保護缺口、三處現在式文件失準、一處可漂移鏡像、一處規則定義射程過寬，以及兩處 spec 自身字面缺陷（只記載）。

## 2. findings 與三分流（11 筆：修 8／轉 BL 0／won't-fix 0；none 2、併入 1）

| 編號 | 嚴重度 | 類別 | 面 | 一句話 | 處置 |
|---|---|---|---|---|---|
| L1-1 | minor | 測試保護缺口 | facade `build_update_active_model` | 同值更新時 `updated_by` 仍須重寫為本次操作者，卻無能分辨的測試：改成「值不變就不 Set `updated_by`」全測照綠 | 修 |
| L1-2 | minor | 測試保護缺口 | `UpdateSystemSettingReq.description` | description 既非字串也非 null（如 `123`）的拒收形在 rust 側零測試，只有 TS 快照裁判的負面案 | 修 |
| L1-3 | minor | spec 自身缺陷 | data-model §7 | `update_by_key` 簽章字面含 `now`，與 research R7／tasks T032 及 HEAD（`now` 注入於 `build_update_active_model`）不符 | none（記載） |
| L1-4 | minor | spec 自身缺陷 | data-model §2 | settingKey「型別非 string→handler 層判」與 ADR-00015 決定 3 相悖（型別不符只可能落 serde／`FromRequest` rejection）；wire 上碼、msg、HTTP 全同 | none（記載） |
| L2-1 | minor→major（real 鏡） | 現在式文件失準 | `tools/wire-schema.py` 模組 docstring | `--staged-gate` 仍寫只看 base-web 單側 typings 區間，as-built 自 BL-00037③ 起為兩側 pin 區間皆零才跳過 | 修（P1-P1 併入） |
| L2-2 | minor | 現在式文件失準 | `tools/wire-schema.py` `OUTPUT_PATH` 註解 | 「快照缺席時 check 走 rc 2」未帶「base-web 容器可用」前提（容器未起先具名跳過 rc 0） | 修 |
| L2-3 | minor→major（real 鏡） | 定義失準 | RULES 名詞段「碼面閘」 | 「環境缺席＝具名跳過、工具缺席＝fail-loud」寫成全體碼面閘共同屬性；`tools/schema-gate.py` 環境異常＝rc 2 | 修（立 ADR-00032，user 拍板） |
| L2-4 | minor→major（real 鏡） | 可漂移鏡像 | RUNBOOK §12 碼面閘表前言 | 手抄 `NON_GATE_TOOLS` 現值三支、零機器對賬（GT-12 只讀表首欄、`test_hook_wiring` 讀常數本身） | 修 |
| L2-5 | minor | 測試保護缺口 | `tests/contract.rs` 雙向覆蓋閘 | 兩支覆蓋閘直接迭代真 ROUTES 與 registry、無常駐合成反例；SC-006 負向自證只有 T045 一次性演練 | 修（驗證員提 BL、主線改判） |
| L3-1 | minor | 現在式文件失準 | arc42 05 §5.2 | 「真 DB 端點案住 `handler/system_settings.rs` 之 `endpoint_tests`」未反映 003 刀後 auth 四檔、`route.rs` 等亦自持真 DB 端點案 | 修 |
| P1-P1 | minor | 現在式文件失準 | 同 L2-1 | 探針 grader 衍生、decided 鏡確認 | 併入 L2-1 |

### 三分流細節

**修（8 筆）**——落於本輪修單：

- **L1-1**：facade `mod tests` 加 `build_update_active_model_same_value_still_pairs_audit_columns`——新值＝列上現值、列上 `updated_by`＝3，斷言 `updated_at`／`updated_by` 皆 Set（成本次 uid 7）。落在 facade 純測，不在 BL-00070 射程（該條所列六支自持 oneshot 殼住 handler／enforce／router 測試模組）。
- **L1-2**：`tests/wire_schema.rs` 加 `update_req_wrong_description_type_fails_deserialization`——description 為 number／bool／object／array 四形，`serde_json::from_value::<UpdateSystemSettingReq>` 皆須 Err；與 handler 模組 `update_req_extractor_type_mismatch_rejects_biz_2222`（serde 失敗→自訂 rejection→2222）接成完整拒收鏈。★lens 原提的兩個落點（`endpoint_tests` 七格壞形表、handler `mod tests` 合成 router 案）依 `e0dd22b` L5-4「在該模組增案即改到 X 本體＝到期」會使 BL-00070 到期，decided 鏡據此改議、主線採之。
- **L2-1**：docstring 改為「兩側 pin 區間皆零變動才跳過（base-web 區間零 typings 變動＋rust-api 區間零快照變動）」，與 RUNBOOK §12 同字。ADR-00019 決定 2（accepted body）與 specs/002 contracts 兩處（史料面）依 `4556778` 已明載的「as-built 不回灌」不動。
- **L2-2**：註解補「base-web 容器可用而快照缺席時 rc 2；容器不可用先具名跳過 rc 0、不讀快照＝ADR-00019 決定 2」。`5d51348` T044 裁定不動的前半句（首抽已隨 002 刀 U3 落地）保留。
- **L2-3**：user 拍板立 **ADR-00032 supersedes ADR-00016**（rev6 無部分翻案機制，承 ADR-00011 決定 5 先例）：決定 1／2／4 原意續行；名詞括注改為「環境缺席語意逐支見碼面閘表『觸發時機』欄——容器依賴且入 pre-commit 者＝具名跳過、工具缺席＝fail-loud（ADR-00019），其餘不類推」。同批改 RULES 名詞段、README 查詢表與 RUNBOOK 碼面閘表 schema-gate 列「根據 ADR」欄改指 ADR-00032；ADR-00016 status 轉 superseded（`superseded_by` 由 generate 回填）。名詞段不入 `rules emit`（implementer／review／fix 三 scope 命中 0），編排成品不需重組。
- **L2-4**：改為指針「`tools/docsync/gates.py` 常數；成員以該常數為準、此處不鏡像」（RL-0049）。`specs/003-auth-session` 三處轉錄該句屬史料面、不動；RUNBOOK 各非閘工具列之「`NON_GATE_TOOLS` 成員」宣稱由 GT-12 幽靈列／漏列兩向間接守住、保留。
- **L2-5**：抽 `coverage_diff` 純函式，兩支真 repo 覆蓋閘改呼叫它，另加 `coverage_diff_names_missing_route_and_orphan_case` 合成反例（少一案指名 route、多一殭屍指名 case_key、全對應雙空）。改判理由：同檔已有 `contract_case_key_binding_detects_mismatched_verify` 同構常駐自證，改動只在測試檔；BACKLOG 淨流量已超標（37，目標 ≤0），小修不另開一條。
- **L3-1**：改為「真 DB 端點案分住各模組之 `#[cfg(test)]` 測試模組（消費者不寫死、以 grep `real_app` 為準；…）」。decided 鏡指出 lens 所擬逐檔列名會漏 `captcha.rs`／`throttle/mod.rs`，且 `test_kit.rs` 檔頭與 LL-00009 已採 grep 現算，故不列名。

**none（2 筆，只記載、無後續義務）**：

- **L1-3**：首次記載於 `4986f4a`（002 刀 U4 收官訊息之「規格備查」：data-model §7 簽章措辭差、排 U8 T043 判是否加註），U8（`5d51348`）未留處置。HEAD 行為與 FR-010 一致、時鐘注入的純測面在；字面落後的只有史料面。
- **L1-4**：HEAD 與 ADR-00015 決定 3、`contracts/wire-settings.md` §2（「型別非 string／JSON 反序列化失敗」併為同列）一致；現在式面未抄錄該句。decided 鏡補正：data-model §2 本身只把三態型明寫給 description 與 settingValue，此矛盾須經 ADR-00015 決定 3 才成立、非純粹同節自相矛盾。

**併入（1 筆）**：P1-P1 → L2-1。

### 驗證鏡對 lens 陳述的更正（記載）

- L1-2：lens 所舉變異「把 tristate 放寬成先吃 Value 再轉字串」寫法不精確——tristate 三欄共用，照寫會先被 settingKey 型別不符案抓紅；只放寬 description 一欄才存活（主線抽驗即採此形）。
- L1-3：「與 T032 不符」屬推論，T032 並未字面排除 `update_by_key` 收 `now`；字面不符的一方是 HEAD 對 data-model §7。
- L2-3：lens 稱 generate 會連帶更新 RULES-VERSION 與 `_sk_rules.js`，不實（兩者只取規則表列）；缺陷落定點應記 ADR-00016 決定 3，不只 `contracts/code-gates.md` §3。
- L3-1：lens 稱「此句最後一次變動＝002 U8」不精確，句內括號於 003 刀 U1 改過。

## 3. 驗證（主線實跑）

| 項 | 值 |
|---|---|
| 新增三案（真碼） | 容器內 `cargo fmt --all --check` 綠；`cargo test -p server --lib build_update_active_model` 3 綠、`--test wire_schema update_req` 6 綠、`--test contract coverage` 3 綠 |
| 變異抽驗 | 三發同時打上（①facade 同值時不 Set `updated_by` ②description 改吃 `serde_json::Value` 後轉字串 ③`coverage_diff` 缺案判準恆空），容器內 serial 重跑相關面：lib 33 案（facade 純測 8、handler `mod tests` 12、`endpoint_tests` 之 `us2_*` 7／`us3_write_malformed_body_*` 1／`us5_*` 5 真 DB 案）→ **只有** `build_update_active_model_same_value_still_pairs_audit_columns` 紅、32 綠；`wire_schema update_req*` 6 案→**只有** `update_req_wrong_description_type_fails_deserialization` 紅；`contract coverage*` 3 案→**只有** `coverage_diff_names_missing_route_and_orphan_case` 紅。既有案在三發變異下全綠＝三個缺口屬實，新增案各自抓得到。變異檔以 sha256 還原自證、rust-api porcelain 只剩本輪三檔 |
| 全量 | 容器內 `cargo test --workspace --no-fail-fast` 435 綠／0 紅／2 ignored。首跑 lib 64 紅＋contract 1 紅，皆為 SequenceResetGuard／LoginAttemptGuard 因 dev 庫會話殘列拒跑（2026-09-14 18:27Z Super 真登入留下之 `sys_token` 1 列／`sys_login_attempt` 1 列，已過期、非本輪所留；BL-00075 所述情形）；依 RUNBOOK §9c 以空基準 tmp 快照 `restore`（user 執行）全等後重跑全綠，測後 `diff` 仍全等 |
| 工具自測 | `python3 tools/wire-schema.py test` 31 綠 |

## 4. 冷啟動探針（只入報告與事件 notes、不填事件 `probe` 欄）

| 題 | 判分 | 探針跳數／最短跳數 | 註 |
|---|---|---|---|
| Q1 新增 number 型設定鍵要改哪些檔、哪些守衛會擋 | 繞路 | 20／5 | repo 無「新增設定鍵」專屬程序文件；資訊分住 RUNBOOK §10（migration 三步）、§9c（walkthrough-baseline 拒跑）、BACKLOG 觸發欄與 cargo 測試釘值 |
| Q2 R_ADMIN 呼叫寫端的回應與規則真源 | 繞路 | 7／2 | 403＋`{data:null, code:"5003", msg:"system.forbidden"}`；真源 ADR-00014 決定 1、上位憲法 §I.3 |
| Q3 rust-api 容器未起時 commit 動到 typings，wire 閘怎麼處理 | 繞路 | 9／2 | 探針識破題設（閘依賴 base-web 容器、與 rust-api 容器無關）並兩態並列 |

找不到 0、答錯 0。不填 `probe` 欄之理由：`tools/docsync/references.py` 檢索性列取最近一筆帶 `probe` 之 review 事件、不分 scope，且比「輪間不降」；本輪題組與 doc-governance 輪不同質，互比無意義。

grader 未採納之 suggestion：Q1「新增或改動設定鍵」檢核清單（三表與釘值已由 cargo 測試擋、migration 三步已住 RUNBOOK §10，另立清單＝多一份無機器守的鏡像）；Q2 於 wire-settings §2 補判定次序欄（史料面不改）；Q3 於 RUNBOOK §12 加「與 rust-api 容器無關」否定句（該列已具名 base-web 容器、屬冗述）。

## 5. 建議（未列為 finding）

1. **seed 值↔REGISTRY `range` 零機器守**（探針 grader 附帶觀察）：`validation::validate` 只在寫端 handler 呼叫，讀端與 `auth/jwt.rs`／`throttle::load_settings` 等消費側只解析不驗界，新 migration 寫入越界 seed 值無任何測試或閘會紅；現行 10 個 number 鍵 seed 值經主線解析皆在界內、無實害。→ 併入 BL-00028 條文（觸發同為首次新增或改動設定鍵）。
2. **越權者送壞形 body 的判定次序**（5003 先於 2222）只由 `router.rs` `build_from` doc 與 axum 中介層語意保證、無具名測試；wire 上屬已拍板次序（authn→authz→handler），留作觀察。

## 6. 判定

**需要後續處置：是（本輪即處理完）。** 八筆修落於本輪修單、兩筆 spec 自身缺陷記載、一筆併入；翻案一顆 ADR（ADR-00016→ADR-00032，user 拍板），specs 本文零改動。
