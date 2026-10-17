# 007-user-password-admin 規格對照審查（spec-compliance-007、2026-10-16）

範圍＝已收刀之 007 user-password-admin 刀對 `specs/007-user-password-admin/` 的兌現度：spec.md FR-001～FR-066（A～J 十組）、SC-001～SC-014、User Story 1～6、Edge Cases 八節、Assumptions、Out of Scope、Key Entities、★軌道逐處登記表（19 列）、刻意分岔登記表與一次性遷移三欄表（m0003），連同 data-model、`contracts/` 四份（wire-user-admin／wire-user-center／msg-keys／code-gates）、quickstart.md、research.md、tasks.md、checklists/requirements.md；另核收刀後三支維護批（maint-backlog-142-146、maint-backlog-139-140-145-147、maint-adr-00094-wording）對 007 刀所建所定之面的改動有無承載。基準＝HEAD（外層 `7a0b47b`、rust-api `34aa3d6`、base-web `9fe562d`）；收刀點（merge `8d8dc57`）只用於歸因；specs 本文不改（凍結史料面）。

## 0. 方法與取證

| 項 | 值 |
|---|---|
| 形式 | RL-0073 承載處②：user 2026-10-16 臨時發起、附屬 007 刀；user 指定以 superpowers:requesting-code-review 對照 spec 做 review；分支 `maint-spec-compliance-007`（自 `rev6-admin-root @ 7a0b47b`，即 maint-adr-00094-wording 收單後） |
| 編排 | **三支唯讀 Workflow、依序發射**（沿 005／006 輪形；射程互斥；review 骨架 explore＋inline 兩鏡三態；全角色 `opus[1m]` xhigh、零 CDP；零 finding 之 lens 不派兩鏡）。run A＝`wf_70c37789-513`（六 lens；最壞 18／保險絲 19），派 18 支、牆鐘 36.2 分；run B＝`wf_602f02ca-40a`（三 lens＋一冷啟動探針；最壞 12／保險絲 13），派 12 支、牆鐘 40.8 分；run C＝`wf_3c932612-7a5`（五 lens；最壞 15／保險絲 16），派 15 支、牆鐘 44.9 分；三支皆零錯零 null |
| 切成三支、依序發射的理由 | FR 66 條、specs 共 5,638 行（刀內 rust-api +31,733 行、base-web +3,486 行、外層 +13,261 行）、契約四份，另需一鏡核收刀後三支維護批。開工時週用量已達 92%：依序發射讓每支完成即落盤成檢查點，額度中斷只損在飛那一支；續跑配方先寫入主線工作區，並排一次性續跑檢查 |
| run A lens（使用者域後端行為） | L1 端點總則、授權態與契約碼表（A 段 FR-001～009、SC-001／002）｜L2 寫端固定序、鎖序與結構保護（FR-010／011／016／017／020、SC-003）｜L3 寫端各端點語意（FR-012～015／018／019）｜L4 包含規則與解鎖入口（C 段 FR-021～025＋FR-040、SC-004）｜L5 斷權與會話（D 段 FR-026～031、SC-005）｜L6 密碼政策、冷卻、節流、自助改密與自助路由（E 段 FR-032～038＋FR-039、SC-006） |
| run B lens（seed 遷移、前端、繁中） | L7 自鎖防護與 seed 基線遷移 m0003（G 段 FR-041～046、SC-007）｜L8 前端使用者頁、個人中心、登入表單、請求層與四頁按鈕碼（FR-047～051、053）｜L9 繁中介面與 fork-delta×憲法 §III（FR-052、054、SC-009／011）｜P1 冷啟動探針三題 |
| run C lens（治理、工具、測試、變動、跨域） | L10 憲法 Amendment、ADR 與治理帳本（FR-055／056／059／060、SC-012／014）｜L11 工具擴面與測試基建（FR-057／058／061／062、SC-008）｜L12 測試保護力與 wire 裁判面（FR-063／064／066、SC-013；不變式驅動）｜L13 收刀後變動承載歸因與既有處置之落地（變動驅動）｜L14 Edge Cases 交叉、Assumptions、Out of Scope、Key Entities、checklists、quickstart、CDP 紀錄與跨域連帶 |
| review 模板 | requesting-code-review 要點烤入三支 run 之 CONTEXT：spec 是願景文件（spec 沉默處以合理使用者期待判斷）；Critical／Important／Minor 對映 blocker／major／minor；每支 lens 的 notes 末附「做得好的地方」「擱置未判」「本 lens 判定」三段（摘要見 §5） |
| 前六輪經驗 | CONTEXT 烤入十一條：006 輪之十條（BL 到期落點須明寫／逐字出自 accepted ADR 或 specs 之句不得單改現在式面／evidence 可原樣重跑／不逐檔列易漂移名冊／機器枚舉先證樣式集完備／錨字面被自身散文滿足＝恆綠無聲／已處置者不重報／Amendment log 與 ADR provenance 所帶 BL 號屬出處標籤／既有事件只經 RUNBOOK §12c erratum 更正列名欄位／否定掃描須涵蓋同義與英文寫法）＋規則晚於碼（以收刀後新立或擴寫之 RL 評 007 既有測試前，先核其確落新規射程）；另烤 RL-0078 防污染條款 |
| 規則塊 | `rules emit --scope review` 全塊烤入，RULES-VERSION `fa99668b6699`；本輪三度調規後依序為 `2b8572cfe0ea`（`a513098`：RL-0084 擴寫）、`9df0bd62580d`（`8f851fb`：RL-0084 第二點再補＋RL-0080 末句擴寫）、`13794b33f782`（`30d12e9`：RL-0080 判準逐成分與共用輸出面兩處） |
| 唯讀邊界 | agent 禁寫入形命令、禁 docker／cargo／pnpm／generate；rev5 樹只讀；python 工具之保護力以記憶體內 exec 變異取證、rust 以讀碼推演 |
| 額度暫停與銜接 | run C 在飛時週用量達 98%。user 問能否不讓「探索驗證」發射：兩鏡隨各 lens 回報自動接派、屬 script 常數，主線只能整支停（在飛 lens 一併作廢），故依 user 指示讓 run C 跑完、主線只落盤後暫停。額度恢復後由一次性續跑檢查（本機 23:07）接續：三支皆完成、零在飛，免續跑 |
| 主線復核 | 38 筆 lens findings 之 evidence 命令原樣重跑，事實全數重現（三筆寫入形掃描屬誤報：grep 字面含 `run --rm migrate`、樣式內含 `=>`）；主線親核 L3-1、L6-1、L14-4 與三筆駁回之承載；兩鏡相左、缺判與重複者由主線裁斷（§2） |
| 修單 | user 2026-10-16／17 裁定（§1）。rust-api：`27d49c9`（U1 補測七案＋碼註一處）、`d69a0a2`（補證殘留碼註四處）。外層：`a513098`（治理文字顆：RL-0084 擴寫、ADR-00098、LL-00094、BL-00148、活書與 RUNBOOK 九處）、`02c0132`（U1 pin＋LL-00039）、`011c91d`（提示 hook＋LL-00095）、`8f851fb`（治理文字二顆：RL-0084 第二點、RL-0080、CLAUDE.md §2 兩處、LL-00094、LL-00039）、`d51bd3d`（補證殘留外層六處＋pin）、`4f75750`（U2 工具三筆）、`30d12e9`（RL-0080 兩處擴寫＋LL-00096） |
| 補證 run（L10-4） | side agent 指出「007 刀」只以樣式篩過後，user 指示逐條判讀後才下結論；主線依 RULES 名詞段分面後開兩支唯讀判讀 run：J＝`wf_ff41fbd6-652`（「007 刀」外層＋子庫現在式 475 處；17 支、牆鐘 49.8 分）、J2＝`wf_4ec186c9-e30`（「007 刀」LESSONS 63 處、「十九款／19 列」LESSONS 3 處、「被踢」子庫 50 處；7 支、牆鐘 37.1 分）。兩支皆零錯零 null，判讀表鍵集與命中逐鍵全等；結果見 §2 L10-1／L10-4 補記 |
| 未覆蓋 | SC-010 之 CDP 三方對照（承載＝007 刀 U22 走查）；前端行為面只讀碼推演、本輪未跑 `pnpm typecheck` |

## 1. 結論

**零 blocker、零 wire 行為缺陷。** 十四支 lens 之判定：L1／L2／L4／L5／L8／L9／L10／L11＝兌現，L3／L6／L7／L12／L13／L14＝修後可兌現。主線實跑核得：ROUTES 61 條（政策保護 45）與路由條數常數同值；`MSG_KEYS` 68；migration 目錄恰 m0001～m0003、演進帳 entries 9／`next_id` 10；`Cargo.lock`、`pnpm-lock.yaml` 自刀起點 pin 零 diff。八支寫端固定序與鎖序、包含規則九消費點、斷權兩層兜底、政策單一驗證點與改密節流、m0003 五句逐句影響列數斷言，在憲法島 I、ADR、活書、RUNBOOK、碼註之間一致，且各有可指名的測試。收刀後三支維護批的變動逐項有承載，007 碼與 007 final holistic review 修項皆未被撤。

要處置的集中在五類：

- ①**測試保護缺口**九筆，皆經變異推演存活：
  - rust 六筆。major 三筆：L3-1（userGender 不動之 no-op 案打在性別 NULL 的帳號上、無判別力）、L6-1（addUser 之 forbidUsername 比對對象零測試）、L12-2（PHC 日誌面零結構守、成功路徑零擷取案）。minor 三筆：L3-2、L5-1、L6-2。
  - 工具三筆：L9-1（繁中用語表缺避用詞）、L12-1（page 鍵過渡豁免無到期）、L11-2（redis 清理前綴與 rust 鍵前綴零跨語言對賬）。
- ②**現在式碼註、文件與指路**十筆：碼註 L1-1；RUNBOOK §9c／§10／§11.3／§12 四處（L11-1、L7-1、L14-2、L11-3）；活書 11 一處（L7-3）；BACKLOG-DEFERRED 一處（L13-1）；NOTES 一處（L14-3）；探針衍生兩筆（P1-P1 活書未定義 8888 前端呈現、P1-P2 島 I ⑥ 無政策鍵名）。
- ③**收刀帳本後驗缺口**兩筆：L10-1（contracts §8.3 指定入收單事件之六項反向確認只入三條）、L10-4（SC-014「假述零殘留」以 lint／check 綠代證）。這是 LL-00067 的再犯：RL-0084 擴面後第一刀仍只核到第一處、且無證據形制（LL-00094）。補證時依名詞段分面逐條判讀現在式面 633 處，確認殘留 10 處（§2 J／J2 十列），本輪修。
- ④**行為已知態**一筆：L4-1（L2-1 併入）——非超管本人持停用角色時，對本人的 updateUser 與帳號維 unlockLogin 得 5003。
- ⑤**轉帳**一筆：L7-2（m0003×演進帳×凍結 seed 一致性只由需 docker 之閘承載）。

另有 spec 等史料面之字面缺陷 13 筆只記報告（§2），駁回 3 筆。

**user 2026-10-16 裁定（七題）**：
- ①L4-1＝記為 by-design：立 ADR-00098（比照 ADR-00093），活書 06 島 I 與 11 技術債表加指針，真庫測釘現行行為。
- ②rust 測試五案本輪補（L3-1、L3-2、L5-1、L6-1、L6-2），變異自證、容器 serial 全量。
- ③L12-2＝只補成功路徑日誌斷言（純測試、不動 entity）。
- ④工具三筆本輪修。L11-2 之建議選項前提經主線更正後重問，user 改選「加 GT-12 腿」（§2 主線更正段）。
- ⑤L7-2＝轉 BL-00148（觸發＝下一支 delta migration 進場之單元起手前）。
- ⑥文件與碼註十筆本輪全修；探針另提之總表不另立、只補指路。
- ⑦RL-0084 擴寫兩點＋LESSONS 一則（LL-00094）＋三項反向確認結果補記於本輪 review 事件 notes。

**user 2026-10-17 再裁四題**：
- Q-RL0084b：RL-0084 第二點再補「命中依名詞段分面、現在式面命中逐條判讀、不得以樣式篩代判」，CLAUDE.md §2 兩處同步（補證時兩度重犯之結論；§2 補記）。
- Q-TM：信任模型單檔 bind mount 懸空第三次同形（LL-00095），本輪加外層 post-merge／post-checkout 提示 hook。
- Q-RL0080：審查員以短 timeout 中途終止跑測、留 dev 庫殘列（LL-00039 同根第三種觸發形），RL-0080 末句擴及跑測逾時。
- Q-RL0080b：修單 U2 之審查迴圈 blocker 皆屬 RL-0080 族（LESSONS 鏈第 5 次、10-15 擴寫後首次；LL-00096），RL-0080 擴寫兩處：正則內之錨、必含字面與字元類排除各算一條判準；每增判準即重跑，含與新判準共用輸出面之既有判準（§3 U2）。

另依 user 指示，CLAUDE.md §2 兩處收刀步驟同補 RL-0084 擴寫兩點（`a513098` 訊息原記「CLAUDE.md 不動」，由 `8f851fb` 更正）。

## 2. findings 與三分流（50 筆＝run A 14＋run B 9〔含探針衍生 2〕＋run C 17＋補證 run J 7＋J2 3；修 31／轉 BL 1／won't-fix ADR 1／只記報告 13／駁回 3／併重 1）

| 編號 | 嚴重 | 類別 | 面 | 一句話 | 處置 |
|---|---|---|---|---|---|
| **L3-1** | **major** | 測試保護缺口 | updateUser `userGender`（`handler/user.rs` update_tests） | 空字串與值域外＝不動之兩發打在性別為 NULL 的帳號上，「清空」與「不動」同結果：測試標籤宣稱的保護不存在 | 修（標的先設非 NULL 性別之判別案；變異自證） |
| **L6-1** | **major** | 測試保護缺口 | addUser 政策腿 forbidUsername | 比對對象（本請求帳號名）零測試：第二引數改空字串或他名全套照綠，「禁止密碼與帳號相同」可靜默失效 | 修（開 `password_forbid_username` 之真庫案；變異自證） |
| **L12-2** | **major** | 測試保護缺口 | 密碼雜湊之日誌面（FR-005、島 I5 三重不洩） | 帶 PHC 之 `sys_user::Model` derive Debug、在八寫端與改密鎖內流通，成功路徑零日誌擷取案：任一寫端內層插入以 Debug 記錄 Model 之日誌全套照綠 | 修（user 裁：只補成功路徑日誌斷言、不動 entity） |
| L3-2 | minor | 測試保護缺口 | updateUser 停用撤票觸發 | 「已停用帳號再送 status 2 並改他欄＝零撤票」半邊無案：disabling 改取請求值全綠 | 修（補案；變異自證） |
| L5-1 | minor | 測試保護缺口 | FR-029 帳號資訊讀端不判帳號狀態 | 反向確認只行使停用一形，軟刪合取零案 | 修（補案；變異自證） |
| L6-2 | minor | 測試保護缺口 | `load_password_policy` | 島 I5「單一快照讀現值」零機器守：改逐鍵分查全綠 | 修（單語句機器守；變異自證） |
| L9-1 | minor | 測試保護缺口 | `tools/zh-tw-lint.py` 用語表 | msg-keys §1.3 避用詞（內置、字符等）不在表內、也未列不入表理由 | 修 |
| L12-1 | minor | 測試保護缺口 | zh-tw-lint 腿④ page 鍵 | 「缺席不判」過渡豁免在三鍵落地後仍在、無到期謂詞：鍵改名或刪除即靜默失效 | 修（缺席改判紅＝名冊幽靈即紅；RL-0051） |
| L11-2 | minor | 測試保護缺口 | 走查工具 redis 清理前綴名冊 | 與 rust-api 鍵渲染點前綴零跨語言對賬：rust 改前綴時 seed 模式 restore 留殘鍵仍回 rc 0 | 修（user 裁：GT-12 新腿＋一正一反自測＋停用變異） |
| L1-1 | minor | 現在式文件失準 | `tests/contract.rs` `observed_msgs` doc | 族別列舉漏 `biz.user` 二十鍵與 `auth.session.kickedByAdmin` | 修（改不逐族列舉形、改指 `observed_msgs_real_db`） |
| L7-1 | minor | 現在式文件失準 | RUNBOOK §10 | 手動重放 migrate 未寫「rust-api 在跑時動判定面之 migration 須重啟 rust-api」：ADR-00085 決定 4 之 MUST 在維運面無家 | 修 |
| L7-3 | minor | 現在式文件失準 | 活書 11 技術債表 | ADR-00086 決定 6 之已知態（受保護按鈕碼誤加到非受保護選單後只能刪該選單）無指針 | 修 |
| L11-1 | minor | 現在式文件失準 | RUNBOOK §9c | 走查工具自測觸發只寫「本體 staged 時」，漏 007 final holistic review 新增之依賴觸發 | 修 |
| L11-3 | minor | 現在式文件失準 | RUNBOOK §12 碼面閘表 schema-gate 列 | 根據 ADR 欄未列 ADR-00085 決定 7 | 修 |
| L13-1 | minor | 現在式文件失準 | BACKLOG-DEFERRED BL-00147 | 以已 superseded 之 ADR-00078 後果為拍板出處 | 修（改指 ADR-00090 後果） |
| L14-2 | minor | 現在式文件失準 | RUNBOOK §11.3 政策壞值計數 | 未載前端射程：重設浮層與改密卡以政策投影先擋、不發請求，UI 上改密不推進告警計數 | 修 |
| L14-3 | minor | 檢索性 | NOTES 008 題 | ADR-00079 翻案觸發器（設定頁進場⇒複核畫面前置提示或守門）在受版控面計數 0 | 修 |
| P1-P1 | minor | 現在式文件失準（探針衍生） | 活書 06／08／10／12 | 只寫 3333 與 7777 之前端呈現、8888 一處未寫，反以未定義的「（靜默）」標註被撤者所見 | 修（改述為清登入態、回登入頁並 toast、不彈 modal；伺服端「不落事件」義之「靜默」保留） |
| P1-P2 | minor | 檢索性（探針衍生） | 活書 06 島 I ⑥ | 政策七鍵無鍵名、registry 界與冷卻鍵 seed | 修（並於 RUNBOOK §13 補拒因指路） |
| L10-1 | minor | 其他（帳本後驗） | 007 feature_close notes × perf 第四步 | contracts §8.3「結果入收單事件」之六項反向確認只入三條；RL-0084 後驗只照 §8.2 判相符 | 修（三項結果補記於本輪 review 事件 notes；RL-0084 擴寫；LL-00094） |
| L10-4 | minor | 測試保護缺口（帳本後驗） | SC-014「機器枚舉之假述零殘留」 | 子句表承載與後驗⑤皆以 lint／check 綠代證，lint 不含 FR-059 任一種子 | 修（主線以種子實跑、依名詞段分面逐條判讀補證，結果見下；RL-0084 兩度擴寫） |
| J-H119 | minor | 現在式文件失準（補證） | `rust-api/server/src/error.rs` 模組 doc | 「變體集與 13 碼矩陣的機器基準＝003 data-model §11」：變體集已非該表九列（007 刀 U6、U10 各增一變體） | 修（`d69a0a2`） |
| J-H163 | minor | 現在式文件失準（補證） | `server/src/handler/mod.rs` 共用件句 | 「設計面恰五件…已落地者之名冊」為施工期限定語，五件早已全落地 | 修（`d69a0a2`） |
| J-H221 | minor | 現在式文件失準（補證） | `handler/user.rs` `update_tests` 模組 doc | 共用件消費者只列三模組，實有六模組以 `use super::update_tests::` 取用 | 修（改不逐一列舉、以該 grep 為準；`d69a0a2`） |
| J-H222 | minor | 現在式文件失準（補證） | 同檔 `revoked_events` doc | 「另供 `kick_tests` 沿用」漏 `reset_tests` | 修（同上） |
| J-H020 | minor | 現在式文件失準（補證） | `docs/ops/reference-src/code-gate-contracts.md` msg-key-gate 斷言 2 | 「射程守分階段四句…②③隨兩鍵分批入名冊逐鍵生效」：射程二鍵皆已入名冊，施工期過渡語成假述 | 修（`d51bd3d`） |
| J-H018 | minor | 現在式文件失準（補證） | RUNBOOK §12 碼面閘表 msg-key-gate 列 | 同 J-H020 | 修（`d51bd3d`） |
| J-H038 | minor | 現在式文件失準（補證） | `tools/msg-key-gate.py` 模組 doc、`bizdata_stage_findings` doc、self_test 碼註 | 同 J-H020（RL-0011 同語意）；碼註「攜參鍵恆非空＝`biz.user.passwordPolicy`」漏另一射程鍵 | 修（`d51bd3d`） |
| J2-K012 | minor | 現在式文件失準（補證） | LL-00074 守法段 | 「007 刀後續設密入口的冷卻整合案…主線組裝其單元定義時烤入此句」已兌現 | 修（改通則句；`d51bd3d`） |
| J2-K015 | minor | 現在式文件失準（補證） | LL-00075 守法段 | 「007 刀 U12a 的 rejection 日誌掃描跨十一檔…烤入此句」：U12a 實以遞迴取檔、不在射程 (b) | 修（改例示句＋通則句；`d51bd3d`） |
| J2-K035 | minor | 現在式文件失準（補證） | LL-00080 守法段 | 「主線自 007 刀 U14 起把 (e)～(g) 烤入單元定義」：(e)～(g) 已入 RL-0080、由規則塊帶入 | 修（`d51bd3d`） |
| L4-1 | minor | spec 自身缺陷 | 包含規則×本人標的 | 非超管本人持停用角色時，對本人 updateUser（只改暱稱亦然）與本人帳號維 unlockLogin 得 5003，與「本人可改非角色欄」明文衝突、無已知態登記 | won't-fix ADR（ADR-00098 by-design；真庫測釘現行；活書 06／11 指針） |
| L2-1 | minor | spec 自身缺陷 | 同 L4-1 | real 確認、decided 駁回 | 併入 L4-1 |
| L7-2 | minor | 測試保護缺口 | m0003×演進帳×凍結 seed | 三者一致性只由需 docker 之 `schema-gate.py check` 承載，m0003 套用後被改或演進帳少登一筆時 pre-commit 與 cargo 全量皆綠 | 轉 BL-00148（觸發＝下一支 delta migration 進場之單元起手前） |
| L1-2 | minor | spec 自身缺陷 | contracts wire-user-admin §1 | 「upstream `fetchGetUserList` 本刀起零畫面消費」與同檔偏離帳、ADR-00083 決定 3（excel 示範頁仍消費）矛盾 | 只記報告 |
| L5-2 | minor | spec 自身缺陷 | US2 AS2／AS3／AS6、Edge Cases「斷權與會話」 | 寫端撤銷後之換發拒絕歸因於鎖內活性重驗，HEAD 實為 revoked 腿先擋 | 只記報告 |
| L6-3 | minor | spec 自身缺陷 | US3 Independent Test | 「或改密成功後解除」於受節流態不可達（C3 先於舊密比對即拒） | 只記報告 |
| L6-4 | minor | spec 自身缺陷 | Edge Cases「密碼面」、FR-035 括注 | 剩餘秒數之上限夾值稱「rev5 HEAD 同形」，實則 rev5 無上限夾 | 只記報告 |
| L7-4 | minor | 其他 | ADR-00085 決定 3 括注 | 「序列已前進之庫不倒退」不實（down⑤′ 取 max(id)、不讀 last_value），無行為後果 | 只記報告（accepted body 不可變） |
| L8-1 | minor | spec 自身缺陷 | 刻意分岔登記表 | 漏「單刪成功即移除勾選鍵」一列（rev5 不移除、批刪送出必整批 notFound） | 只記報告 |
| L10-2 | minor | 其他 | 憲法 1.8.1 log 列、ADR-00092 | I18N (i) 之改字稱「理由欄」（§III.2 表無此欄、實為紀律欄），同列又稱紀律欄不變 | 只記報告（修訂史與 accepted body） |
| L10-3 | minor | spec 自身缺陷 | FR-060 `adrs` 括注 | 漏 ADR-00091（實作期翻案）與 ADR-00093（final review won't-fix） | 只記報告 |
| L11-4 | minor | spec 自身缺陷 | data-model §10 SeedUserRestoreGuard | 「Drop＝不等者逐列寫回」與契約「無條件逐列寫回」及 HEAD 矛盾 | 只記報告 |
| L14-1 | minor | spec 自身缺陷 | quickstart §12 | ADR 狀態核對預期值未隨 ADR-00091 更新（HEAD 實得 12 accepted／2 superseded） | 只記報告 |
| L14-4 | minor | spec 自身缺陷 | Assumptions 第三條 | 密碼政策鍵歸於 m0001，實住 m0002（零 DDL 之結論不受影響） | 只記報告（decided 鏡判駁回、理由只寫「不確定」→主線改判確認） |
| L14-5 | minor | spec 自身缺陷 | Assumptions 第二條 | 003～006 底座「本刀純消費」與 FR-021／027／028／040 及 HEAD 矛盾 | 只記報告（decided 鏡缺判→主線判確認） |
| L14-6 | minor | spec 自身缺陷 | Edge Cases「包含規則與委派」第二條 | 「只有軟刪使用者才硬刪指派」全稱句與 updateUser 差集硬刪矛盾 | 只記報告（同上） |
| L5-3 | minor | 現在式文件失準 | login.rs 碼註與 warn 字面 | 以「被踢者」稱單一會話頂替 | **駁回**（見下） |
| L6-5 | minor | 其他 | entity `sys_user::Model` derive Debug | 島 I5 DTO 遮蔽之結構保護不及此型 | **駁回**（見下） |
| L9-2 | minor | spec 自身缺陷 | ★軌道逐處登記表三列 | 型別、改動內容與軌道欄三處與 HEAD 不符 | **駁回**（見下） |

> 修 31 筆中，L10-1 與 L10-4 的修法是本輪 review 事件 notes 補記與 RL-0084 擴寫（feature_close notes 不可更正），其餘 29 筆為碼面與文件改動（含補證十筆）。只記報告的 13 筆，缺陷皆在 spec、data-model、quickstart、contracts 或 accepted ADR 等不可改之面，現在式面已正確。

### 主線裁斷（兩鏡相左、缺判與重複）

- **L2-1 併入 L4-1**：兩筆指同一碼路（本人只送非角色欄時③放行、④的 T 含停用角色而 T⊄A）。L2-1 的 decided 鏡以 ADR-00075 決定 1／3 與島 I7 為據判駁回；機制確有拍板承載，但「本人標的因此被拒」這個後果未被登記，比照 ADR-00093 屬拍板級，交 user 裁定（Q1）。
- **L14-4 改判確認**：decided 鏡判駁回、理由欄只寫「不確定」。主線親核 m0001 零政策鍵、m0002 有八支 `password_*` 鍵，事實成立。
- **L14-5、L14-6 主線判確認**：decided 鏡缺判；兩筆皆為 spec 字面與同 spec 他條及 HEAD 矛盾，只記報告。
- **主線更正（L11-2）**：主線起初給的建議是「比照門鈴頻道，在走查工具自測加一案」，前提有誤——門鈴頻道的對賬實為 docsync GT-12 腿，`tools/docsync/gates.py` 明載工具自測只在工具本身 staged 時才跑、承載不了跨語言對賬。重問後 user 選加 GT-12 腿：rust-api HEAD 樹 `server/src/cache/mod.rs` 之鍵前綴集 ⇔ 走查工具 `RESTORE_REDIS_PREFIXES` 恰等，錨形零命中或多命中即紅；閘數不變。

### 駁回之主線裁定

- **L5-3（real 確認、decided 駁回）**：007 刀 U21 收單 `79e5fca` 之主線裁定 4 已定 rust 碼註「被踢／踢人」不改（FR-030 射程只及憲法島 B 與活書 12、碼識別字 `kicked`／`admin_kick` 已分義）；U5 收單 `39cf8a2` 亦定測試訊息與 003 舊句之「被踢」屬口語、非假述。warn 字面出自 003 刀，同屬舊句。
- **L6-5（real 確認、decided 駁回）**：「承載密碼之 DTO」的射程已有定形——ADR-00074 後果「兌現窗」列 DTO 遮蔽句的既有反例只有 `LoginReq`，當時 sys_user Model 已是 derive Debug 而未被列入；research R11 決定 6 與 data-model §6 也只列請求 DTO。sys_user 列的承載改由「絕不序列化原始列」守。日誌面的保護力缺口另由 L12-2 以成功路徑擷取案補上。
- **L9-2（real 確認、decided 駁回）**：三處差異在現在式面（憲法 1.8.1 範圍欄、活書 08 §8.4）皆與拍板一致；spec 登記表是 plan 期預估快照，屬史料面。

### L4-1：本人標的照判包含規則（ADR-00098）

- 行為：非超管操作者本人持停用角色時，T（全部指派、停用照計）⊄ A（現役角色集、濾停用）。對本人的 updateUser（只改暱稱亦然）與本人帳號維 unlockLogin 因此得 5003，零變更、零稽核。
- 定性：包含規則一體適用之後果。島 I3「本人 MAY 改自己的非角色欄」是本人規則的許可，不是包含規則的豁免；唯一的本人例外是自助改密（標的恆為本人）。
- 補救：由持該角色或 R_SUPER 者代為。前代同形未登記（`rev5:server/src/handler/user.rs` 之 `guard_no_escalation`）。
- 承載：ADR-00098（by-design）；活書 06 島 I ⑦、11 技術債表使用者域列同批加指針；真庫測釘現行（rust-api `27d49c9` 之 `an_operator_holding_a_disabled_role_is_refused_on_their_own_profile`）。

### L10-1／L10-4 補記：007 刀收刀之反向確認與假述零殘留

feature_close notes 屬不可更正欄，依 RUNBOOK §12c 改在本輪 review 事件的 notes 同記（基準樹現算：外層 `a513098`、rust-api `34aa3d6`、base-web `9fe562d`；本輪修單未動 lockfile、migration 目錄、演進帳與 base-web，§8.3 三項於修後 HEAD 同值）：

- **contracts code-gates §8.3 另三項反向確認**：
  - 零新依賴：`rust-api/Cargo.lock` 自 `6f74d202` 起、`base-web/pnpm-lock.yaml` 自 `fb4dac2` 起皆零 diff。
  - migration 目錄恰 `m0001_baseline_schema.rs`／`m0002_baseline_seeds.rs`／`m0003_seed_button_governance.rs`（另 `lib.rs`、`main.rs`）。
  - `docs/ops/reference-src/schema-evolution.json` 之 entries 9、`next_id` 10。
  - 三項皆相符；結果原只住 U23 `c9be3eb` 訊息之 T105 ④⑤。
- **SC-014 假述零殘留（FR-059 種子實跑；RL-0084 第二點之形）**：
  - 方法：FR-059 所列種子於上列基準樹以 `docsync errata` 同一比對實跑（外層 tracked 文字檔不分大小寫子串＋兩子庫 pin 樹 `git grep -F -i`）。路由讀端前代歸因非字面種子、不跑；受保護列數「19」以「十九款」「19 列」「受保護列 19」「受保護授權列 19」四形代跑，schema-definition 檔頭前進句以「隨每支帶 migration」、「踢除」指單會話之句以「被踢」代跑。
  - 分面依 RULES 名詞段。不逐條判讀之面與理由：史料面（docs/brainstorms、specs、docs/reviews；凍結）；ADR 面（accepted body 不可變、不受活書時態腿）；生成鏡像（docs/generated、LESSONS.md 等；以真源判，本表各命中之真源皆落 ADR 面、事件源或 LESSONS）；事件源（events.jsonl；RL-0048 之過去式家、不可更正）。其餘現在式面（含 docs/ops/LESSONS 與憲法本文）、子庫碼面與語料面一律逐條判讀。

| 種子 | 全 repo | 逐條判讀（現在式面） | 排除面（史料＋ADR＋生成＋事件源） | 判讀結果 |
|---|---|---|---|---|
| 007 刀 | 659 | 538（外層 78、LESSONS 63、子庫 394、語料面 3） | 121（27＋67＋25＋2） | 出處 499、現況 28、他義 1、疑 10；確認殘留 10、駁回 3（見下） |
| 被踢 | 124 | 54（外層 4、子庫 50） | 70（64＋6＋0＋0） | 外層 4 處皆「被踢除」之管理員義；子庫 50 處＝管理員義 11、單一會話義 30、他義 9，單一會話義者為 7777 與頂替之碼註，依 `79e5fca` 主線裁定 4 不改；殘留 0 |
| 兩語 | 128 | 11（憲法 7、子庫 4） | 117（85＋32＋0＋0） | 憲法修訂史 6；§III.2 I18N 列「擴充元件只內建兩語」他義 1；locale 檔「另兩語同插」4 處他義；殘留 0 |
| 零 migration | 122 | 3（外層 1、子庫 2） | 119（95＋13＋6＋5） | BL-00140 兌現選項句 1；`sys_user.rs` 之 003 刀設計理由 2（§5 ⑥）；殘留 0 |
| 恰十 | 43 | 19（子庫 19） | 24（23＋1＋0＋0） | 皆「恰十一／十二／十四／十七」之子串，或 IP 規則之「恰十鍵」他義；殘留 0 |
| 門在頁級 | 38 | 4（外層 2、憲法 1、子庫 1） | 34（28＋6＋0＋0） | 憲法修訂史 1；活書 05、08 與 policy-archive 碼註之授權回收桶頁句 3，續真；殘留 0 |
| 使用者角色指派寫端 | 24 | 1（憲法 1） | 23（10＋13＋0＋0） | 憲法 G5 括號句恆真（ADR-00074 決定二定不動）；殘留 0 |
| 十九款 | 8 | 2（LESSONS 2） | 6（0＋4＋1＋1） | LL-00064 兩處他義；殘留 0 |
| 19 列 | 25 | 1（LESSONS 1） | 24（18＋4＋1＋1） | LL-00071 一處他義；殘留 0 |
| 使用者域刀／屬後刀域／不產 hash／不接 runtime／孤立檔／無 UI 按鈕／受保護列 19／受保護授權列 19／隨每支帶 migration | 21／24／12／29／27／27／5／3／10 | 0 | 全數 | 現在式面零命中 |

  - 「007 刀」與「被踢」子庫、「十九款／19 列」LESSONS 共 591 處由兩支唯讀 run（J、J2）以四類逐鍵判讀，另由複核 lens 二次判讀可疑鍵與夾帶施工期語之「出處」，並走兩鏡三態；其餘 42 處由主線逐條判讀。合計現在式面逐條判讀 633 處。
  - 「007 刀」之裁定：確認殘留 10 處（J-H018／H020／H038／H119／H163／H221／H222、J2-K012／K015／K035，見 §2 表）。其中 H163 兩鏡相左、K035 兩鏡未定，主線皆裁確認。駁回 3 處：H016（NOTES「下一步＝007 規格對照審查輪」＝本輪合法待辦）、K027（LL-00078 之 (b)～(d) 仍靠主線手動烤入、句真）、K031（LL-00079 該句屬處置紀錄）。
  - 結論：「全屬出處」不成立。現在式面確認殘留 10 處、皆屬「007 刀」，本輪已修（rust-api `d69a0a2`、外層 `d51bd3d`）；其餘種子現在式面零殘留。修後 HEAD（外層 `30d12e9`／rust-api `d69a0a2`／base-web `9fe562d`）之「007 刀」662 處：較基準增 15、減 12，增者主線逐條判讀，皆為出處、現況或他義。

### RL-0084 兩度擴寫（user 裁）

- 第一次（Q7、`a513098`）新增兩點、條數不變：
  - contracts 以全檔中「寫入／入收單事件」各處之聯集為核對全集；
  - 「假述零殘留」類子句須以 spec 所列種子實跑 `python3 tools/docsync errata <詞>`，並於 commit 訊息記命中分流，不得以 lint／check 綠代證。
- 第二次（Q-RL0084b、`8f851fb`）：照第一次的字面補證時又兩度重犯——run C 之 lens 以種子實跑即稱零殘留；主線初稿以約二十種未來式樣式篩「007 刀」，又以自訂分流把 docs/ops/LESSONS 列為史料面，即擬寫「全屬出處」。「記命中分流」擋不住「沒逐條看就判零殘留」，故第二點改為：命中依 RULES 名詞段分面、現在式面命中逐條判讀（不得以樣式篩代判），訊息記各種子之命中數、分面與判讀結果。
- RULES-VERSION `fa99668b6699`→`2b8572cfe0ea`→`9df0bd62580d`（第二次與 RL-0080 擴寫同顆）。CLAUDE.md §2 兩處收刀步驟於 `8f851fb` 補上兩點（含第二次字面），理由＝LL-00067 成因（收刀者照 §2 範本做）；006 輪擴面時亦同批改兩處。
- LESSONS：LL-00094（recurrence_of LL-00067）記第一次；`8f851fb` 依逐條判讀結果改其徵狀、成因、處置、晉升面與守法②。

### 環境態一：信任模型懸空再犯與提示 hook（user 裁 Q-TM）

- 修單 U1 改動前之基線全量起，server lib `dev_trust_model_matches_the_delivered_file` 每趟皆紅：rust-api 容器內 `/etc/rev6/trust-model.toml` 單檔 bind mount 懸空。起點＝007 收刀 checkout default 與 merge `8d8dc57`（2026-10-15 18:28:59／18:29:00；該檔於 007 刀 `df7335b` 改過）後未重建容器，懸空約 29 小時、橫跨三支維護批。
- 同形第三次（LL-00033 pull、LL-00068 006 收刀 merge、本次）。LL-00068 預立之晉升條件「同形第三次即評估 post-merge／post-checkout 提示 hook」成立，交 user 裁定＝本輪加提示 hook（`011c91d`）：外層 `.githooks/post-merge` 與 `.githooks/post-checkout` 於前後兩顆 commit 間該檔有變動時於 stderr 印 RUNBOOK §2 重建命令、只提示恆 rc 0；bootstrap hooks 指紋名冊、GT-09 `EXEC_REQUIRED` 與 README 檔樹同步；RUNBOOK §2 起手句補 merge；docsync tests 以臨時 repo 實跑兩支真 hook 機器守。LESSONS 記 LL-00095（recurrence_of LL-00068）。
- 處置：主線依 RUNBOOK §2 重建 rust-api 容器，該案轉綠（§3）。

### 環境態二：dev 庫殘列與 RL-0080 擴寫（user 裁 Q-RL0080）

- U1 規格審查 r1 以容器內 `timeout 580` 前景包 `cargo test -p server --bins --tests`（server lib 單支約 10 分），逾時中途終止測試、守衛 Drop 未跑，留下 `casbin_rule` 一列（id 166）與序列 164→166；其後三支 agent 之走查 diff 皆 rc 1、只能升級。誘因＝單元定義「Bash 前景單命令控制在 600 秒內」一句：審查員為湊前景時限縮短 timeout，沒有改丟背景。
- LL-00039「測試被中斷→守衛 Drop 不跑→留殘列」同根第三種觸發形（005 為 host 端 timeout、006 為 TaskStop）。主線先只補文字（LL-00039 一段、單元定義範本改句），side agent 提醒後交 user 裁定＝擴寫 RL-0080 末句：「變異不得拆除、繞過真庫清理守衛；變異與跑測皆不得令其 Drop 不跑（證守衛承重改用守衛照掛、反轉期望；跑測逾時不得短於實耗——長跑一律丟背景、容器內 timeout 須大於實耗上界）」（`8f851fb`；RL-0080 已適用 implementer／review／fix、條數不變）。LL-00039 晉升 rules。
- 處置：主線核容器內無殘存測試行程、pg 無交易中閒置連線後，以 `walkthrough-baseline.py restore` 還原（rc 0），重建容器兼重啟 rust-api，走查 diff 回 rc 0。

## 3. 驗證（主線實跑）

- **U1（rust-api 補測，`27d49c9`）**：
  - 編排：`wf_f8bc71bd-320` 七支零錯。implementer 回 done_with_escalation（升級＝§2 兩項環境態）；規格審查 r1 一 blocker（password.rs 案冊數量詞）→fix→r2 零；碼品質 r1 一 blocker（contract.rs `observed_msgs` doc 之「理由之通則」全稱句）→fix→r2 零。
  - 判準變異：implementer m1～m7b 八發、規格審查 r2 九支、碼品質 r1 九支與 r2 六支（各輪另取形）；新案皆紅、配對既有案照綠，零存活。
  - 主線自驗（容器重建後）：容器內 serial 全量兩趟 rc 0，皆 1558 passed／0 failed／2 ignored（server lib 1095；逐 binary 兩趟全等；007 收刀 1550＋本單元 8）；`cargo build --workspace --locked` 零 warning；rust-fmt-gate check rc 0；docsync test 420 OK、lint 0 錯；走查基準 diff 全量前後皆 rc 0；RUNBOOK §16.1 驗收①（容器內檔＝交付檔）rc 0、③載入告警 0。
  - 生產碼零改：user.rs、user_center.rs 之生產區與 `34aa3d6` 逐字相同；refresh.rs、password.rs 之生產區只改案冊數量詞之註解。
- **提示 hook（`011c91d`）**：docsync test 421 OK；新案變異兩發（路徑字面改錯→應提示兩發落空即紅；post-merge 改 `exit 1`→rc 斷言紅），還原後綠；bootstrap 體檢 rc 0（七檔指紋一致、警告 0）。
- **治理文字二顆（`8f851fb`）**：lint 0 錯；RULES-VERSION `9df0bd62580d`；改動字面之 errata 復掃見該顆訊息。
- **補證殘留修（`d69a0a2`＋`d51bd3d`）**：rust-api 容器內 touch 後 `cargo build --workspace --locked --all-targets` 零 warning、doc test 9＋31 passed、rust-fmt-gate rc 0；msg-key-gate self-test 34 案全綠、check 綠；改動字面十種之 errata 復掃，剩餘命中皆在 ADR-00076（不可變）、specs/007（史料面）與 msg-key-gate 夾具說明一處（仍真）。
- **U2（工具三筆，`4f75750`）**：
  - 編排：`wf_31205df4-182` 十一支零錯、約 152 分。implementer 回 done_with_escalation（升級＝rust-api 缺席時新腿共用門鈴腿之具名跳過，SKIP 行與 ENV_SKIPS 理由只名門鈴）。規格審查 r1 兩 blocker（上述具名跳過；zh 射程外漏列裸詞形）→fix→r2 零。碼品質 r1 三 blocker（外層錨行首判準無變異實證；綠行過渡計數殘留；docstring 註解面與常數 `=` 後折行兩途徑失述）→fix→r2 一（射程外漏列 `format!(` 無 `:` 之鍵形）→fix→r3 一（新腿訊息與門鈴腿共用子字串，門鈴腿「外層缺席即紅」之停用變異全綠存活）→fix（回 done_with_escalation：門鈴案斷言一行屬限定外）→確認輪 r4 零。fix 跑滿上限，各輪 blocker 皆屬 RL-0080 族（LL-00096；user 裁 Q-RL0080b＝RL-0080 擴寫兩處，`30d12e9`）。
  - 判準變異：implementer zh 三支、gates 六支；兩輪規格審查與四輪碼品質審查各自重跑，確認輪有效變異全數打紅。主線改門鈴案斷言帶腿標籤後，D1（門鈴腿外層缺席改回空）與 D4（改出 redis 腿訊息）於門鈴類轉紅。
  - 主線自驗：zh-tw-lint self-test 87→90 案、全樹 check rc 0（MAINLAND_TERMS 128 詞）；docsync test 421→431 OK；lint 0 錯（2 警告皆已知）；generate 只動 GATES.md 之 GT-12 列與環境跳過表一列、STATE.md docsync 行數 4217→4283；新腿於現樹零 finding（兩側皆 {session, throttle, cpwd}）。
  - 文件同步：code-gate-contracts §8 五處（腿③、腿④、rc 四形、射程外、self-test）與 RUNBOOK §12 zh-tw-lint 列；errata 復掃「過渡語意」「鍵缺席之三形」「page 鍵在場」「門鈴字面未對賬」皆零命中。

## 4. 冷啟動探針（只入報告與事件 notes、不填事件 `probe` 欄）

三題：

- 帳號被鎖時從哪解鎖、帳號維與來源維的入口與權限，受委派的非超管能否解鎖持超管角色的帳號。
- 停用或重設密碼後對方會話何時失效、與踢除的差別、之後以舊換發憑證續期會怎樣。
- 一般使用者自助改密一直被拒的可能原因與畫面訊息、政策在哪設定與何時生效、連續輸錯舊密碼的後果。

結果：

- 三題皆 found、答錯 0、找不到 0，三題皆判繞路：最短 3／2／5 跳，有效 5／4／8 跳。
- Q2 繞路的起因是活書全無 8888 之前端呈現，卻以未定義的「靜默」標註被撤者所見，探針被迫下探五支前端檔（→P1-P1）。
- Q3 的最短路徑本身已大於 3 跳；其中「七鍵鍵名」一跳被迫下探碼面或凍結 contract，原因是 06 島 I ⑥ 未列鍵名（→P1-P2）。

探針建議的處置：

- RUNBOOK §13 改密拒因與斷權所見之總表：不另立表，只在 §13 補指路（ADR-00084 決定 5 續行 ADR-00039 決定 2：譯文之家＝三檔 locale backend 子樹；06 島 A～D ⑤、島 I ⑤ 已逐向列出名單 reason 對回碼，另立表會使同一事實有兩個家，RL-0049）。
- README 補「管理功能怎麼運作」入口列：spec-compliance-005 P1-P3 已駁回同形建議，不重提。
- 兩維鎖同文（登入頁不揭露觸發維度）：屬拍板（06 島 E ④、004 刀 FR-041），不報。

## 5. 各 lens 判定摘要與建議（requesting-code-review 模板要點）

**做得好的地方（摘）**：

- 授權態矩陣與 ROUTES 自首鍵起逐位綁定、十二列全釘碼值，案末再以全矩陣零變更與改密節流桶缺席復核：授權態、路徑×動詞對齊與 body 收斂三者一案同證。
- 八支寫端以 WRITE_ENDS／WRITES 表驅動源碼釘守固定序與包含規則消費點，配 29 發判準自證；連 kickUser 失敗腿改 commit 這類行為面分不出的形也攔得下。
- 包含規則純函式表驅動，「只 T 越界」「只 N 越界」各自成列並以正負例數釘住；拒後以列逐欄含 xmin、指派、經手、票數、事件數、稽核、失效名單做指紋全等。
- 改密節流的判讀與推進皆在帳號鎖持有期內，配確定性並發案（先持鎖、輪詢至排隊數到齊、放鎖後才斷言）。
- m0003 五句逐句以影響列數斷言、失敗訊息帶方向與遷移帳結局；dev 庫偏離 seed 即整支回滾。
- 前端抽屜以送出當輪序號標記取用基準，精確落實 ADR-00091 決定 7「只在同一輪取用」；產密以 CSPRNG 拒絕取樣消模偏差再洗牌。
- base-web 160 處「原行:」皆可在 upstream example 逐行找到，零 stale。
- 走查還原工具之期望 seed 以 importlib 取 schema-gate 同一合成鏈，不自持第二份合成；交易失敗訊息三層遮蔽各有專屬樁形。

**擱置未判中值得主線留意者**：

- ①**日後在使用者域新增寫端卻漏掛包含規則包裝**：現無機器釘，屬 ADR-00075 翻案觸發器「新增以使用者為標的之寫端」的流程承載。
- ②**管理員重設密碼不清被重設者的改密節流桶**（15 分鐘窗內仍不得自助改密）：rev5 同形、spec 沉默、影響輕。
- ③**失效名單寫入失敗之殘窗內，已停用帳號仍可呼叫 changePassword**（C1 只濾軟刪）：島 I2「不加每請求活性判定」之 by-design 射程，需 redis 故障方可達。
- ④**產密浮層複製不帶 rev5 之 execCommand 退路**：非安全來源下 rev6 報失敗、rev5 能複製；現行埠皆綁 127.0.0.1，此形不可達，屬部署硬化面。
- ⑤**README 未設業務行為入口列**：spec-compliance-005 P1-P3 已駁回同形建議。
- ⑥**`sys_user.rs` 兩處「保住『零 migration』（spec FR-005）」**：出自 003 刀，指 003 當時之設計理由；所引 FR-005 未標刀號、讀者難定位。屬 003 域碼註，本輪不處置。

## 6. 判定

007 user-password-admin 刀之 spec 在 HEAD 上**實質兌現**：零 blocker、零 wire 行為缺陷、零無承載之行為偏離。剩餘缺口除一筆轉帳外，全數於本輪收掉：

- 測試保護力：rust 六筆＋L4-1 釘現行＝rust-api `27d49c9`；工具三筆＝外層 `4f75750`。
- 現在式碼註、文件與指路十筆：rust-api `27d49c9`（L1-1）與外層 `a513098`。
- 收刀帳本兩筆：本輪 review 事件 notes 補記；RL-0084 兩度擴寫（LL-00094），CLAUDE.md §2 兩處同補（`8f851fb`）。補證確認之現在式殘留十筆：rust-api `d69a0a2`、外層 `d51bd3d`。
- 行為已知態一筆：ADR-00098（by-design）。
- 轉帳一筆：BL-00148。
- 本輪另起兩項環境態之機制補強（user 裁）：提示 hook（`011c91d`、LL-00095）；RL-0080 擴及跑測逾時（`8f851fb`、LL-00039）。
- 修單 U2 審查迴圈之 RL-0080 族再犯（user 裁）：RL-0080 再擴兩處（`30d12e9`、LL-00096）。
