# 004-ip-trust-anchor — IP 域整批 brainstorm（階段 0）

- 日期：2026-09-15｜狀態：起手前收斂兩題（BL-00066／BL-00078）＋範圍與治理七題（Q1～Q7）＋設計十節已過 user 核可；同日 grill-with-docs 輪（G1～G6：以 BACKLOG 分類體檢為主核本刀是否納全）已收斂、共識經 user 確認，本檔修訂與帳本勘誤同顆落地；同日第二輪 grill（覆蓋逐號重核＋原 clarify 候選十項定案＝§5、G7）亦收斂、共識經 user 確認；下一步＝**手動** `/speckit-specify`（本檔為其 input；不自動觸發——否則 before_specify hook 不跑、分支不建、spec 落 default）。
- 一句話：把「三端備好、中間沒接」的 IP 域接通——信任錨還原真實來源（八態、含 Tier-1 錨傳輸層背書硬化與轉發鏈超長拒絕）、IP 存取閘（白＞黑＞預設放行、熱重載）、來源維登入節流、IP 規則管理五端點與管理頁、管理員解鎖端點；並以同一筆 MINOR Amendment 讓憲法 §I.7 島 F 入憲、開 §III.2 管理頁 ★ 軌道。
- 交付價值：稽核列記下的是真實使用者位址與其來源信心（不再是最近一跳代理）；超管首次能以規則擋放來源、能手動解鎖；「輪換帳號名」這個帳號維擋不住的攻擊面由來源維補上；節流判定面同時收斂為「每次嘗試由 PG 定案」，兌現憲法跨島總則；測試基建去掉「殘列連坐全量紅」之源。

> 輸入：`docs/ops/NOTES.md` 下一步（004 條）、憲法 §I.7（島 E 條文、跨島總則、島 F 承襲指針）／§III.2（承襲指針、表外宣告）／§IV／§V.3、活書 06 frontmatter「信任錨與 IP 存取閘：隨刀」列與 11「nginx 邊緣 `auth_limit`」已知態列、`docs/generated/reference/rev5-blueprint-map.md`、`docs/ops/BACKLOG.md` 觸發於本刀之條目、主線 BACKLOG 分類體檢工作檔（2026-09-15 重整、gitignored、不入帳；grill 輪以之為主核）、`docs/reviews/20260915-spec-compliance-003.md`（L2-1／L2-2、§5 建議 1）、ADR-00007／ADR-00012／ADR-00026／ADR-00027／ADR-00029／ADR-00033、rev5 `rev5:004-ip-trust-anchor` 全套（brainstorm／spec／plan／research／data-model／contracts／tasks；`rev5:ADR 0039`～`rev5:ADR 0043`）與其收刀後動 004 域檔之 commit（`rev5:1193bb9`／`rev5:31c1293`／`rev5:f841b04`／`rev5:47e8a67`／`rev5:fd23de9`／`rev5:55bb3e3`／`rev5:6ee82e2`；唯讀、凍結 SHA 外層 7eab28a／base-web 9833308／rust-api 92919b9）。

## 0. 拍板紀錄（全數 user 拍板 2026-09-15、一題一問；首選項皆為建議）

| 題 | 拍定 | 要點 |
|---|---|---|
| BL-00066 收斂方向 | **改碼：每次嘗試由 PG 定案** | 現況 `throttle::precheck` ① L1 鎖命中即回 `biz.auth.locked`、不讀三門檻鍵現值亦不查 PG，抵觸憲法 §I.7 跨島總則「節流三鍵於每次登入嘗試讀現值」（003 clarify Q4 答覆寫「承 rev5 實作、零新碼、立即」，而 rev5／rev6 之 L1 命中路徑實皆不讀）；兩個可見後果＝超管放寬門檻後已鎖帳號最長 15 分鐘才吃到新值、設定不變時 L1 亦可比 PG 多擋近一個窗長。成本實證：鎖中每發由 1 次 redis GET 變為 4 支 PG 查詢（設定 3＋計數 1、計數走 `idx_login_attempt_user_time`），仍零 argon2 零落列；攻擊者換帳號名本即可逼出「4 查詢＋argon2＋落列」、nginx `auth_limit` 每 IP 5r/s burst 40 ⇒ 不新增更貴的攻擊路徑。棄案：走 §V.2 Amendment 把 L1 例外寫入跨島總則（ADR-00026 後果段：跨島總則受 MAJOR 閘保護＝rev6 首次 MAJOR，且把沒人刻意選過的過擋行為入憲） |
| BL-00066 落地時點 | **隨 004 同單元** | 本刀依藍本本就整支重寫 `precheck`（加來源維）；併入＝precheck 與節流測試只改一輪、差異點於 research＋ADR 一處記齊、BL-00066 隨收刀關、維護批 +0（治理批對 feature 比現值 7.33、目標 ≤1）。棄案：004 前先開輕量軌維護批（同函式同測試改兩輪、治理批比續升） |
| BL-00078 rules.yml ② | **刪除規則 `obs016-throttle-suppressed`** | 發射源 `suppressed_breadcrumb` 為 rev4 遺留：`rev5:R3-3` 判不做、rev5 004 仍不搬（rev5 碼面只兩行註解說明不搬、規則卻拷到收官）、rev6 src 零命中、specs/003 防回歸清單 B 明列不得帶回 ⇒ 結構上永不觸發、註解指向不存在事件。刪規則塊＋②註解＋檔頭「告警六組 13 條」數量詞與「LogQL 形（②③b③d）」「fields_suppressed」兩處；tools／hooks／rust-api 對 rules.yml 零引用、無計數斷言；史料面不動。棄案：帶入 suppressed 事件（翻案 `rev5:R3-3`、多一塊觀測能力面與 redis 鍵族） |
| Q1 IP 規則管理頁 | **納入本刀** | seed 已有 `manage_ip-rule` 選單列（78）與四顆 `ipRule:*` 按鈕碼、超管點選現得 404 且展開態顯裸鍵（BL-00045）；無頁則五端點零消費者、防自鎖無法在真實操作流程驗。代價＝§III.2 新開 ★ 軌道（兩語 locale route／page 樹、`app.d.ts` page 型節、路由外掛產物四支）、兩支新機器守、CDP 對照走查、走查寫 `sys_ip_rule`；島 F 入憲本即 MINOR、軌道併同一次 Amendment 版號不多跳。棄案：只做後端、頁延管理頁刀（規則只能以 API 管、選單 404 續存、BL-00058 待下一次 §III.2 Amendment） |
| Q2 解鎖端點 | **納入本刀、API-only** | 現況有鎖無解（003 碼明寫 unlock marker 無寫入者；來源維 seed 門檻 15 分窗 50 次即鎖整個來源）；BL-00066 定案後只刪 redis 鍵解不了鎖；dev 瀏覽器不帶構造標頭之流量收斂為單一來源桶、易誤觸來源鎖，`rev5:004` spec 之解法即解鎖自癒。形制承 rev5：兩維擇一、先落操作稽核列後動快取、未鎖標的冪等 `0000`、按鈕待使用者管理頁刀（按鈕碼 `user:unlock` 已在 seed）；多一鍵 `biz.throttle.invalidUnlockTarget`。★`rev5:007` 為解鎖加的 no-escalation 守門不帶（BL-00048 射程）。棄案：不納入（被鎖者只能等窗滑過、dev 誤觸來源鎖須 user 以 `!` 跑 restore） |
| Q3 msg key 譯文之家（BL-00042 ②） | **三檔 locale backend 子樹各為該語之家** | 現況憲法 §III.2 ★I18N-WIRING (ii) 列與 ADR-00029 把譯文權威定於凍結的 `specs/003-auth-session/contracts/msg-keys.md`；本刀新增六鍵、spec 目錄是定點快照（ADR-00012 原則：跨刀活體不住 spec 目錄）。定案：`en-us`／`zh-cn`／`zh-tw` 三檔 backend 子樹即各語譯文權威、鍵集由既有 msg-key-gate 對賬、不另立譯文表（另立即人寫鏡像＝RL-0049）；憲法 (ii) 列權威句併本刀 Amendment 改寫、新 ADR 翻 ADR-00029 之譯文權威句；base-web 五處標記註解與 rust-api 四處 doc 改為史料出處指針、手抄「13 鍵」刪（鍵數以 msg-key-gate 為準）；BL-00042 原項（Day-1 契約）不動。棄案：各刀 `contracts/msg-keys.md`（rev5 形、活體權威住 spec 目錄且兩家）；另立 `docs/ops/reference-src/msg-keys.md` 譯文表（成鏡像、須擴閘逐鍵對譯文、每加一鍵改五處） |
| Q4 settings 寫端跨鍵守衛（BL-00031） | **寫端不守、消費側承載** | 兩對節流鍵皆維持 002 寫端零改動＝與 003 clarify Q3 一致；來源維三鍵依憲法島 E「節流設定鍵缺失或矛盾組合＝視同不可用、退常數並告警；門檻相等合法」整組退（10／50／15）、來源維獨立告警 label（＝rev6 對 rev5 逐鍵退、不判矛盾之差異點）。寫端若守：`update_by_key` 無交易、doc 明載「16 鍵低頻治理面、不驗併發」＝須加交易＋兩列鎖才守得住，且同時調高兩鍵須依序寫。BL-00031 之 `ip_*` 臂隨本刀關、`password_*` 臂留 007 user-password-admin。棄案：寫端只守 `ip_*`（與帳號維不對稱）；寫端守兩對節流鍵（翻案 003 clarify Q3、帳號維寫端行為 user 可見改變） |
| Q5 logout 5000 出口（BL-00062） | **維持 5000＋契約補列＋故障窗 oracle 記已知態** | logout 依島 F 之 F4 改取信任錨上下文（承 `rev5:004` final review M18、user 2026-08-17 親決）＝handler 可執行碼必動 ⇒ BL-00062 到期。wire 不變：契約補 5000 出口（DbErr／commit 失敗；射程與落點見 G2、工程判斷 8）；DB 故障窗內「簽章有效→5000／垃圾→0000」之弱 oracle 立 won't-fix ADR（只在故障窗可見、只洩持票者手上那張票、refresh 端點對持票者本即回應可用性〔代價為觸發輪替〕、保留 5000 使 API 呼叫端知撤銷未成）。前端登出 best-effort 不看結果、UI 零差異。棄案：DbErr 折 `0000` no-op（撤銷未成卻回報成功、偏離 rev5 與 login／refresh 體例） |
| Q6 HTTP 403／404 信封轉譯（BL-00077） | **納入本刀（`rev5:B-117` 形）** | IP 閘擋人回 5003／HTTP 403、落任何頁面（含登入頁）＝本刀為 rev6 首個 UI 可達 403 信封之刀；現況 onError 只在 `BACKEND_ERROR_CODE` 分支轉譯、被擋來源見「Request failed with status code 403」原文，而 rev5 22080 HEAD 已含該轉譯塊（rev5 由 006 CDP 走查發現、維護批 `rev5:ae1ac0c9` 補）＝CDP 對照會差。形＝`src/service/request/index.ts` onError 對「回應帶信封 msg」之 HTTP 錯誤走 `translateBackendMsg`、無信封維持 axios 原文；同檔同用途＝I18N-WIRING (i) 補完（rev5 同樣未修憲），範圍欄處數若需對齊併本刀 Amendment；demo 頁 `/auth/error` 之 4040 toast 同步變譯文（BL-00064／00067 不動）。棄案：不納入（被擋者見英文原文、CDP 對照記差異、006／008 再補） |
| Q7 節流 L1 負快取去留 | **拔除（帳號維與來源維皆不設）** | BL-00066 定案後 L1 命中亦重查 PG＝負快取不再省任何查詢。拔除：判定全由 PG 滑動窗；redis 在節流面只剩 captcha 消耗標記與解鎖標記；島 E「redis L1 為負快取」一句併本刀 MINOR 刪改（§V.3「已入憲 invariant 細項調整」、fail 方向零改）；「redis 整體不可用」判定改由解鎖標記讀取承載（本刀本即新增、排在計數之前）；刪 `throttle:lock:*` 鍵族／`lock_ttl_secs`／`THROTTLE_LOCK_TTL_SECS`／降級源 `redis_lock`・`redis_lock_set`／兩支 L1 測試（命中不續期、TTL 隨窗縮短）／活書 L1 敘述；解鎖端點只寫標記。可見差異只在「計數查詢單獨失敗」之部分故障：已鎖帳號由 `biz.auth.locked` 改走島 E 既定 fail-open＋補償（要求驗證碼、密碼錯仍計數）；PG 整體故障時 authenticate 查 `sys_user` 即 5000、兩案皆無法登入。棄案：保留 L1 作 PG 故障後備（島 E 須補「L1 命中且 L2 查詢失敗＝維持鎖定」例外句、分級有 MAJOR 爭議、元件平時不起作用仍須維護） |

**grill 輪拍板紀錄（user 2026-09-15 發起 grill-with-docs：以 BACKLOG 分類體檢為主核本刀是否把可處理項納全；兩輪 frontier；首選項皆為建議）**

| 題 | 拍定 | 要點 |
|---|---|---|
| G1 §III.2 標籤射程（BL-00058） | **五欄一併精確化** | BL-00058 之 user 拍板（2026-09-14）原留「只改 (iii) 一欄或一併精確化五欄、屆時再定」，定稿版誤寫為只改 (iii)、本輪補問。定案：(b) 三表單 stub／(c) captcha hook／LOGIN-CAPTCHA (i) auth store／LOGOUT-UX (i)／I18N (iii) 五欄範圍欄改「修改型 N 處＋新增型圈界 M 塊」實數形（plan 期以 fork-delta-lint 實跑取數），與新軌道列同一標法；併本刀 MINOR、零碼改動；BL-00058 隨本刀關。棄案：只改 (iii)（同表兩種標法並存、舊四欄粗標籤續為已知態） |
| G2 本刀改動 003 端點之契約列落點 | **本刀 spec contracts 記增量** | 本刀為首把回頭改前一刀端點契約的刀（login 加 F7 鏈超長 5003 列、logout 補 5000 列、三端點上下文來源改變）；RULES 對 wire 契約活體權威零明文、`specs/**` 屬史料面、wire 行為機器承載＝`tests/contract.rs` 覆蓋閘＋`router.rs` ROUTES（`docs/generated/reference/routes.md` 由之生成）。定案：受影響端點之增量列寫 `specs/004-ip-trust-anchor/contracts/`、明載基底見 specs/003 快照；wire 活體權威＝碼＋contract test、不另立文件家；BL-00062「活體契約放哪」一句收刀時以本決定回應；BL-00042 原項不擴。棄案：立活體 wire 契約家（`docs/ops/reference-src/wire-*.md`、擴用 ADR-00012 原則並與 BL-00042 原項同 ADR 抽；本刀多一塊治理工作、不加對賬閘即成人寫鏡像） |
| G3 BACKLOG 分類體檢 §5 無關勘誤落點 | **brainstorm 定案同顆於 default 落帳** | 三項與本刀無關之失準（BL-00047 射程漏三處、滯後卷 BL-00049 預填帳號敘述、活書 09 §9.1 流程層句與 ADR-00007 決定 2 漂移）＋交接既定之 BL-00043／00045／00075 觸發欄改寫＋LESSONS 一筆（LL-00022）；user 確認共識時選與本檔修訂合成一顆（`69c422c` 開刀前承載體檢前例、不開輕量軌、維護批 +0）。棄案：併入本刀治理單元（無關字面混入刀 diff）；留待下一支維護批（治理批比續升、失準字面續存） |
| G4 節流設定消費側驗界（BL-00028 附帶觀察） | **納入：越界＝壞值、整組退** | 寫端驗單鍵界值（門檻 1～100、窗 1～1440），但 003 `throttle::load_settings` 與 rev5 `load_ip_settings` 皆只 parse；越界值只能經 migration 或直改庫寫入、後果卻重：`max_fails=0` ⇒ 計數 0 ≥ 0 ⇒ 全站每次登入被鎖（fail-closed、與島 E 設定壞值退常數之 fail-open 方向相反）、`window_minutes=0` ⇒ 計數恆 0 ⇒ 節流失效。定案：本刀重寫之兩維 loader 以 registry 宣告界驗每鍵（沿用 `validation` 宣告、不另抄）、越界與不可解析同屬壞值 ⇒ 整組退常數＋告警；島 E 字面補「越界」屬 plan 措辭、併同次 Amendment；BL-00028 收刀刪 `throttle::load_settings` 半句（jwt TTL 等其餘消費者續留）。棄案：留 BL-00028 到期（越界 seed 仍可全站鎖死或節流失效、無閘攔） |
| G5 後端藍本取形（rev5 004 收刀後之維護批修補） | **帶 `rev5:B-074`＋`rev5:B-075`；`rev5:B-111` 收刀立 BL** | 同顆 `rev5:1193bb9` 三件：B-074＝信任模型設定檔之 IPv4-mapped 網段字面（`::ffff:a.b.c.d/N`）因判定側先折 v4 而永遠比不中 ⇒ 載入時結構化告警（附改寫建議）＋清空該集合（與「單一集合含無效網段＝只清該集合」同形、只縮小信任）＝004 域缺陷；B-075＝`main.rs` `axum::serve` 須 `into_make_service_with_connect_info::<SocketAddr>` 之測試 lint（rev5 345 行）＝本刀前提守門；B-111＝全樹 `Serialize` i64 欄須掛 2^53 守衛或字串序列化或明示豁免之 lint（rev5 1480 行）＝全域 wire 守衛、非 IP 域。本刀自身 `IpRuleRecord.id` 照憲法 §I.3 掛守衛、由 contract test 驗。棄案：三件都帶（多一支與 IP 域無關之全域 lint、掃描面及 002／003 全部 DTO）；都不帶（B-074 為 rev5 已知且已修之缺陷＝帶回） |
| G6 測試守衛 `SequenceResetGuard` | **本刀整支廢除＋`walkthrough-baseline` 序列口徑對齊 gate2** | ★首問題幹前提有誤（主線自承、已更正重問）：誤稱守衛立論＝「序列前進使 schema-gate 紅」，實際 `test_kit.rs` doc 明載 rev6 003 知 `rev5:B-121`／`rev5:L-055` 而刻意保留硬化形、立論＝「測後庫態＝seed 態之可重跑性＋與走查還原紀律（RL-0031）對齊」。事實：69 處掛載；Drop 數 `sys_token`／`session_event`／`sys_login_attempt` 三表**全部**列、非零即拒重設並 panic ⇒ dev 庫一次真登入殘列即連坐會話面全量紅（LL-00022）；`SessionRowsGuard`（id 水位形）不拒跑、不在本題；gate2 已正規化 runtime-append 四表序列值，`walkthrough-baseline diff` 則逐支比全部序列值。定案：承 rev5 HEAD 廢除（69 處＋自證測＋doc），runtime-append 表序列一律不重設、各案只清自己寫的列；`walkthrough-baseline diff` 對 runtime-append 四表之序列改比存在性不比值（與 gate2 同口徑；restore 仍依基準檔 setval）＝「runtime-append 表的序列值不入任何比對」一條規則通兩處；落本刀測試基建單元；RUNBOOK §9c 一句＋LL-00017 補述。棄案：保留重設、殘列時 warn 不 panic（漏列偵測變弱、兩種序列規則並存）；不動（殘列摩擦隨本刀走查與新 DB 案加劇） |
| G7 toml 釘版（第二輪；三源分歧） | **1.1.6** | 全域 §6 雙源紀律：rev5 藍本釘 1.1.4（lock `1.1.4+spec-1.1.0`）、crates.io 最新穩定 `1.1.6+spec-1.1.0`（2026-09-10）、rev6 lock 無此 crate＝三源分歧、須 user 挑；同 minor 差 patch、無傳遞約束。另兩支 arc-swap 1.9.2／futures-util 0.3.34 三源一致（rev6 lock 傳遞既有＝rev5＝crates.io）、直接採不問。棄案：1.1.4（與藍本逐字同版、一進場即釘舊 patch） |

第二輪（同日、user 換模後再叫 grill-with-docs）：BACKLOG 開放 25＋滯後 2 逐號重核＝§2 皆有處置；004 外桶 C 兩題（BL-00042 原項＝等首支帶 migration 的刀；BL-00064＋00067 demo 頁＝需 §I.3 Amendment 或 m0003）維持不納；原留給 clarify 的十候選改為定案（§5：九項工程判斷、一項拍板＝G7）。

**既定不問（承 rev5 已驗證結論施工、報備備查）**

1. IP 規則五端點（無寫端＝閘恆空）與其契約形（`rev5:004` `contracts/wire-ip-rule.md`）。
2. 信任錨全形：三層（對端閘→Tier-1 CDN 位置錨→Tier-2 最右非受信）＋兩覆蓋（通道回退、邊緣驗證升等）＋F6 硬化；第八態 `chain_rejected`＋F7（登入端點鏈跳數逾上界拒絕、其餘端點標記照服務、拒絕列帳號維計數排除／來源維計數納入）＋F8（稽核轉錄保留判定窗、兩成立條件）——取 `rev5:ADR 0043` 與 rev5 憲法 v1.5.1～v1.6.2 收窄後之終態。
3. logout／refresh 之 `source_ip` 改取信任錨（F4；見 Q5）。
4. `AppState` 5→7（`trust_model`／`ip_rules`；ADR-00027 翻案觸發器已預告）。
5. 操作稽核首寫不對稱：規則四寫端＋解鎖落 `sys_operation_log`、既有設定寫端維持不落列（002 刀 spec FR-016 刻意決定）。

**工程判斷（主線自拍、報備備查；RULES 名詞段判準下非拍板級）**

1. **ip-rule 頁藍本取 rev5 HEAD 形**：含 `rev5:1597a671`（006 U9 之 `rev5:B-099` 修：header-extra slot 無權時退回渲染共用元件新增／批刪 fallback 鈕 ⇒ 外層 div `v-show`＋內層 `v-if`）與 `rev5:b8270630`（eslint multiline 註解形、零語意）；rev5 004 收刀形有該缺陷、不取。
2. **走查還原工具擴面**：`tools/walkthrough-baseline.py` 之還原面擴及 `sys_ip_rule`／`sys_operation_log`（含其序列），並加「以凍結 seed 為基準」模式 ⇒ 動 restore 可執行碼＝BL-00075 到期、同批以其候選①收（seed 態下五表皆 0 列、無須空基準 snapshot 檔）；同單元兌現 G6 之序列比對口徑。`tools/schema-gate.py` 之 `RUNTIME_APPEND_TABLES` 已含 `sys_operation_log`（創世已帶）、`sys_ip_rule` 刻意不收窄（變體 A 業務表）＝零改。
3. **跨島總則字面不動**：其首句「每個設定鍵只在其消費事件當下讀現值」已涵蓋 `ip_*` 三鍵（消費事件＝每次登入嘗試）；列舉句不擴寫，避開 ADR-00026 後果段所稱之 MAJOR 閘。
4. **兩支新機器守走碼面閘**（管理頁零 `v-html`／`innerHTML`、路由產物重算冪等）：STATE「閘數 12／上限 12」只計 docsync GT-01～GT-12，碼面閘另冊（RUNBOOK §12 碼面閘表）⇒ 不佔閘數預算；四處名冊（RUNBOOK §12、README 樹、`tools/bootstrap.sh` `run_tool_test`、pre-commit 段與 `test_hook_wiring` SEGMENTS）照 msg-key-gate 前例同批接。
5. **rules.yml 其餘事件錨**：③b `obs016-ipgate-degraded`（錨 `ipgate/mod.rs`、本刀建）隨設計段對齊 as-built；casbin-reload／accesslog-write-fail／reaper×2／obs017×2 錨向 rev6 零命中之模組或指標、屬後刀（授權治理／稽核域／reaper 域）、非本刀射程，不動。
6. **延後項須有家**：收刀新記兩條 BL——「解鎖按鈕＋前端 wrapper 待使用者管理頁刀」與「全域 wire i64 守衛 lint（`rev5:B-111` 同形；G5）」（002 承載體檢同型教訓：延後項不得只住 ADR）。
7. **BL-00070 一次收七處**：六支自持殼＋`obs.rs` 第七處（本刀於其測試模組增案＝BACKLOG 檔頭「動 X」定義下到期）；條文原稱 `envelope_json`「非 JSON 信封形」失準——實為 JSON 信封解析、可委派 `oneshot_json`，具名留存候選只剩 `obs.rs` 案（不讀 body、只驗 recorder render）與 `router.rs` `send`（通用送出殼）；rev5 以 `rev5:fd23de9`／`rev5:47e8a67` 做過同構收攏（`test_state` 單一字面、AppState 自訂形收窄），本刀與 AppState 擴欄、G6 同單元。
8. **BL-00062 契約補列擴三表**：login／refresh／logout 三張契約表同批補齊 5000 出口（DbErr／commit 失敗）與上下文缺席列（依 clarify 候選①定形），落點＝G2 之本刀 spec contracts 增量；不改 wire 行為。
9. **後端藍本之 HEAD 形細則**：audit 詞彙取 `rev5:31c1293` 定案形（`AuditOperation` 零新 variant、`add`／`update`／`delete`／`restore`／`unlock` 字面不變＝append-only 表無混詞風險）；規則列表之操作者名首版即批次讀（`rev5:B-106`、不帶 N+1 已知債）；`handler/common.rs` 共用件（`rev5:B-094`，rev5 於第三消費者才收）依 rev6 當下消費者數判、不預建；稽核斷言一律水位／窗形（`rev5:L-056` 類：`sys_ip_rule` 序列經清理復位後 id 重用、走查孤兒稽核列以 `entity_id` 對上即誤紅）。
10. **補記四項**：rev5 來源維預設常數註「恆須嚴格小於」與 rev6「≤、相等合法」（島 E）之差異入 research 差異點；BL-00072 之「七支／七鍵」數量字面另住 `main.rs` 模組 doc 與 `config.rs` 檔頭、依 RL-0011 同批改；`request_context.rs` 模組頭「三欄與消費面不動」預告於落地時依 RL-0015 回填；島 E 字面補「越界」（G4）。
11. **詞彙定案（domain-modeling；活書 12 於 as-built 時落、現在式紀律）**：`ip_confidence` 之值稱「來源信心」（八態；與活書 12 既有 AI 流程層術語「信心規格」區分，比照「降級（基礎設施）」／「降級輪廓」前例另立系統術語條）；文件一律「來源維」、碼識別字維持 `ip`（`DIM_IP`、`ip_bucket`）；「結構豁免」（不寫「結構性豁免」）；另入詞：信任錨、判定窗、計數桶、顯式放行、解鎖標記、防自鎖；活書 12「節流三區」列之「redis L1 負快取」字面隨 Q7 刪、「鎖定」列之 L1 句與「本代現無解鎖端點、只等窗過」隨 Q2／Q7 改；★`fallback` 撞詞（活書 12 流程層術語「fallback＝降級輪廓實採行為」vs 來源信心第七態 `fallback`）：文件寫態名一律反引號碼識別字並冠「來源信心態」、活書 12 as-built 補一句區分、兩詞不互用（比照「降級（基礎設施）」／「降級輪廓」前例）。
12. **帳本勘誤同顆落地（G3）**：BACKLOG 條文——BL-00031（補引 003 刀 clarify Q3 與本檔 Q4 之寫端不守拍板）／BL-00047（射程補三處）／BL-00070（`envelope_json` 句更正、obs.rs 屬觸發面明示）；觸發欄——BL-00043（按面拆）／BL-00045（按頁拆）／BL-00075（具名本刀擴 restore 清理面）；滯後卷 BL-00049（預填帳號敘述）；活書 09 §9.1 流程層句；LESSONS LL-00022。
13. **原 clarify 候選九項工程判斷**（第二輪 grill）：全文住 §5、specify 直接抄、clarify 不再以此出題。

## 1. rev5 承襲盤點（沿用項照已驗證結論施工、翻案項用新設計；CLAUDE.md §2）

| rev5 項目 | 處置 | rev6 落點 |
|---|---|---|
| 五個 user story（`rev5:004` spec US1 還原真實來源／US2 IP 閘／US3 規則管理頁／US4 來源維節流／US5 解鎖）與優先序 | 沿用 | 本刀範圍（Q1／Q2） |
| 信任錨三層＋兩覆蓋＋F6 硬化＋單一 helper 導出受信集與跳過集（F4 同源對稱）＋IPv4-mapped 正規化單點 | 沿用 | `trust/` 新模組 |
| 轉發鏈正規化兩步（右端取窗 `MAX_XFF_TOKENS`、逐欄正規化、不可解析即丟欄）與三語意區辨測試 | 沿用 | `trust/` |
| 第八態 `chain_rejected`＋F7 登入拒絕（先於 precheck、仍落稽核列）＋F8 判定窗轉錄（`rev5:ADR 0043`、rev5 憲法 v1.5.1／v1.6.x 收窄） | 沿用（終態） | `trust/`＋`middleware/`＋login；`sys_login_attempt` 帳號維計數 `IS DISTINCT FROM 'chain_rejected'` |
| TOML 信任模型（六集合）＋三層失敗語意（缺檔退扁平環境變數／整體壞＝全空不套退路／單集合壞只清該集合）＋dev 最小設定（僅容器網段入 `internal_default`） | 沿用 | `config.rs`；★`deploy/trust-model.dev.toml` 與 `docker-compose.dev.yml` 之 `APP_TRUST_MODEL_PATH` 掛載創世已在 |
| `rev5:B-074` 信任模型 IPv4-mapped 網段字面告警＋清該集合（rev5 004 收刀後維護批） | 沿用（G5） | `config.rs` |
| `rev5:B-075` serve ConnectInfo 備線 lint | 沿用（G5） | `rust-api/server/tests/` 新 lint |
| `rev5:B-111` 全域 wire i64 守衛 lint | 不帶（G5；收刀新記 BL） | — |
| ipgate：判定序六步、any-match 白＞黑＞預設放行、結構豁免六段只豁免阻擋、keep-last-good、門鈴 `ipgate:invalidate`＋專用 pub/sub 連線 watcher（5 秒 timeout、1s→30s backoff、重連後補一次重讀）、未知 `wbip_type` 列略過告警 | 沿用 | `ipgate/` 新模組 |
| `would_self_lock`＝同一 `decide`；F3① 操作者來源位址不可得時同向拒寫 | 沿用 | `handler/ip_rule.rs` |
| 規則五端點契約（分頁三篩選、審計欄上 wire、`deleted` 導出布林、CIDR 主機位元正規化、唯一衝突映 2222、軟刪復原成對寫） | 沿用 | `handler/ip_rule.rs`＋facade `sys_ip_rule` |
| 操作者名回填（rev5 004 形為逐筆查＝N+1；`rev5:B-106` 改批次讀） | 沿用終態（首版即批次；工程判斷 9） | `handler/ip_rule.rs`＋facade `sys_user` |
| `AuditOperation` 詞彙（`rev5:31c1293` 定案：零新 variant、單一宣告源） | 沿用定案形 | `model/audit` |
| `handler/common.rs` 共用件收攏（`rev5:B-094`） | 不預建（依 rev6 消費者數；工程判斷 9） | — |
| 解鎖端點（兩維擇一、畸形零稽核零狀態、稽核先於生效、未鎖冪等 `0000`、API-only） | 沿用（Q2） | `handler/throttle.rs`；只寫標記（Q7） |
| 來源維：兩維並列合成、計數下界恆兩源禁成功即重置（負向自證）、v4 `/32`／v6 `/64` 桶、`unspecified`→無桶、L0 顯式 allow 直讀 allow 袋（絕不經 `decide`） | 沿用 | `throttle/mod.rs`＋facade `sys_login_attempt` |
| 負快取 L1（`rev5:004` spec FR-028：兩維只短路已鎖、命中不續期） | **翻案**（BL-00066＋Q7） | 拔除；每次嘗試由 PG 定案 |
| 來源維設定逐鍵退常數、不判矛盾組合（`rev5:throttle/mod.rs` `load_ip_settings`）；消費側只 parse 不驗界（rev5 兩 loader、rev6 003 `load_settings`） | **翻案**（Q4＋G4、島 E 條文） | 整組退＋矛盾組合退常數＋越界＝壞值＋獨立告警 label |
| 帳號維三件（標記鍵＋讀取端＋計數標籤）、計數查詢本體零改動 | 沿用 | `cache/mod.rs`＋`throttle/mod.rs` |
| 解鎖標記讀取故障＝fail-closed（視為無標記） | 沿用 | 島 E 補句；★本刀另以同一讀取 Err 立 `redis_down`（Q7） |
| msg 譯文權威＝各刀 `contracts/msg-keys.md` | **翻案**（Q3） | 三檔 locale backend 子樹 |
| 新增六鍵 `biz.ipRule.{invalidRuleType,invalidCidr,conflict,notFound,selfLock}`／`biz.throttle.invalidUnlockTarget`、13 碼矩陣零觸碰、零新 `AppError` 變體（阻擋復用 `PermissionDenied`） | 沿用 | `error.rs`＋三檔 locale＋`app.d.ts` backend 型節 |
| `★BASE-WEB-MANAGE-PAGE-WIRING` (i)：七支既有檔、第三塊產物檔紀律（禁手改＋重算冪等驗收、明文不要求逐行標記及其理由）、兩語鍵集相等、page 型節必需 | 沿用（Q1） | 憲法 §III.2 新軌道（同表五欄同批精確化＝G1） |
| 管理頁三檔＋wrapper＋typings（`rev5-` 前綴） | 沿用其形、**前綴改 `rev6-`**、取 HEAD 形（工程判斷 1） | `views/manage/ip-rule/`、`service/api/rev6-ip-rule.ts`、`typings/api/rev6-ip-rule.d.ts` |
| `rev5:B-117` HTTP 層信封 msg 轉譯 | **提前帶入**（Q6；rev5 屬 006 後維護批） | `service/request/index.ts` |
| logout／refresh `source_ip` 取信任錨、上下文缺席退路（rev5＝退標頭轉錄 fail-open） | 沿用（缺席退路形已定＝§5 ①：承 `rev5:004` T048 形＋rev6 `from_headers` `Err` 兩態＝003 刀 spec FR-018、與 `rev5:003` 空字串形不同） | `handler/auth/{login,refresh,logout}.rs` |
| 操作稽核首寫不對稱、`sys_operation_log` 入 gate2 收窄集 | 沿用；收窄集創世已在＝零改 | facade `sys_operation_log`＋`model/audit` |
| `AppState` 5→7、封條改寫保留域外欄說明、兩新欄皆 `Arc` | 沿用 | `state.rs`；新 ADR supersede ADR-00027 |
| 測試基建：`SequenceResetGuard` 廢除＋水位清理守衛（`rev5:B-121`／`rev5:B-122`）；測試建構點收攏（`rev5:fd23de9`／`rev5:47e8a67`） | **翻 rev6 003 之保留設計、承 rev5 HEAD**（G6）；收攏＝BL-00070 同構（工程判斷 7） | `model/facade/test_kit.rs` 與各測試模組；`tools/walkthrough-baseline.py` 序列口徑 |
| 已知態：redis 不開持久化重評維持、dev 經反向代理可達兩態（`fallback`／`proxy_clean`）、解鎖無 UI 按鈕、稽核覆蓋不對稱、wire 裁判面嚴格模式不動 | 沿用；redis 持久化已知態 rev6 活書 11 已載、wire 嚴格模式現況 plan 核 | 本刀已知態 ADR |
| 部署 checklist（CDN 網段 geo 與 TOML 雙份同步義務、鎖 origin 降為縱深防禦建議、樣例＝dev 實掛那份） | 沿用 | RUNBOOK §16 實文 |
| nginx `geo $cf_edge`／兩 map／`X-Real-IP`・`X-Forwarded-For` 注入／`auth_limit` | 沿用（創世已在、零改動） | `deploy/nginx/` |
| 依賴 arc-swap／futures-util（`default-features = false`）／toml | 沿用其選型；版本已三源核對（§6 釘版行；toml＝G7） | 兩份 `Cargo.toml` |
| rules.yml ② `obs016-throttle-suppressed` | **翻案**（BL-00078：刪） | `deploy/grafana-provisioning/alerting/rules.yml` |
| rev5 後刀增量：解鎖 no-escalation（`rev5:007`）、改密節流（`rev5:007` change_pwd）、`Identity` 補 sid（`rev5:B-140`）、`access_log_mw`、region GeoIP、HLL 廣度 | 不帶 | — |

## 2. BACKLOG 觸發項處置（動工前掃描、CLAUDE.md §2；以 BACKLOG 現文為準）

- **BL-00066**（觸發：004 brainstorm 起手前）→ 已收斂（§0 兩題＋Q7），隨本刀節流重寫單元兌現、收刀 `backlog_done`。
- **BL-00078**（觸發：004 brainstorm 起手前）→ 已收斂（刪規則 ②），治理單元兌現、收刀 `backlog_done`。
- **BL-00031**（觸發：各對消費側進場）→ 本刀為 `ip_*` 臂消費側：方向＝`captcha_after ≤ max_fails`（相等合法）、整組退、寫端不守（Q4）⇒ 收刀改條文刪 `ip_*` 臂、只留 `password_*`（007 user-password-admin）；條文已於本檔修訂同顆補引寫端不守之兩處拍板（工程判斷 12）。
- **BL-00042**（②觸發：首個新增或改名 msg key 的刀開寫前）→ 本刀新增六鍵＝②到期、Q3 收斂（新 ADR＋Amendment 改權威句）；原項（下一支帶 migration 的刀）＝本刀零 migration 不觸發 ⇒ 收刀改條文刪②、原項續留（G2 不擴）。
- **BL-00043**（觸發：任一刀首次需要寫稽核 log）→ 本刀為 `sys_operation_log` 首寫者（規則四寫端＋解鎖）＝operation 面到期；`sys_access_log` 面不寫 ⇒ 收刀改條文為只剩 access 面（008 audit-settings-pages）；觸發欄已於本檔修訂同顆按面拆寫。
- **BL-00045**（觸發：各管理頁進場刀）→ Q1 納入 ip-rule 頁（含其 route 樹譯文）⇒ 收刀改條文刪 `manage_ip-rule` 一頁、餘三頁續留；觸發欄已於本檔修訂同顆按頁拆寫。
- **BL-00058**（觸發：下一次 §III.2 Amendment 同批修正）→ 本刀 Amendment 同批處置、射程＝五欄一併精確化（G1）、收刀 `backlog_done`。
- **BL-00062**（觸發：下次動 logout handler 可執行碼）→ 本刀必動（F4）＝到期、Q5 收斂（契約補列擴三表＝工程判斷 8、落點＝G2）、收刀 `backlog_done`。
- **BL-00070**（觸發：下次動上列任一測試模組的可執行碼）→ `AppState` 擴欄使 `router.rs` `stub_state`、`auth/enforce.rs` `state_with`、`handler/system_settings.rs` 端點案之字面建構點受編譯強制改、`obs.rs` 測試模組增案＝到期；一次收七處（工程判斷 7；條文失準句已於本檔修訂同顆更正）、收刀 `backlog_done`。
- **BL-00072**（觸發：下次動 `main.rs` 可執行碼）→ boot 加載信任模型／初載規則集／起 watcher＝到期；同單元補 `include_str!` 靜態掃描案（`assert_jwt_secrets_distinct` 恰一處、以具名 getter 界定位置；`cache::connect` 同形）附合成反例、「七支／七鍵」數量字面同批改（工程判斷 10）、收刀 `backlog_done`。
- **BL-00075**（觸發：本刀擴 restore 清理面時、走查外殘列出現、或動 restore 可執行碼）→ 工程判斷 2 擴還原面＝到期、同批以候選①收（觸發欄已於本檔修訂同顆具名本刀）、收刀 `backlog_done`。
- **BL-00077**（觸發：首個 UI 會碰到 HTTP 403／404 信封的刀）→ 本刀 IP 閘使 403 可達＝到期、Q6 收斂、收刀 `backlog_done`。
- **BL-00028**（觸發：首次新增或改動設定鍵）→ 觸發未到；但本刀重寫兩維 loader、G4 納入消費側驗界 ⇒ 收刀改條文刪 `throttle::load_settings` 半句（其餘消費者續留）。
- **BL-00047**（觸發：首支 create table 之刀開寫前）→ 本刀零 create table、不觸發；條文射程已於本檔修訂同顆補齊三處（G3）。
- 其餘條目觸發未到、本刀不碰：BL-00002（無 AI 元件）／00027（設定頁 view）／00035／00036／00039／00044／00048（解鎖不帶 no-escalation）／00064・00067（demo 頁本身不動；去留仍未排程）／00065（007）／00074（`FRONTEND_MSG_CONSUMERS` 不動：轉譯塊取回應 msg、零字面）；滯後卷 BL-00029 不動、BL-00049 條文敘述已於本檔修訂同顆更正（G3）。

## 3. 設計（十節、user 已核可；grill 輪修訂已併入）

### §1 目標與範圍

**入刀**：US1 稽核記下真實來源與來源信心（信任錨八態）｜US2 超管以 IP 規則阻擋或放行來源（存取閘、熱重載）｜US3 超管在管理頁維護 IP 規則（五端點＋頁＋防自鎖）｜US4 來源維登入節流生效（與帳號維並列；節流判定全面改由 PG 定案、拔除 L1）｜US5 超管手動解鎖帳號或來源（API-only）。量級：ROUTES 16→22（`/systemManage/{getIpRuleList,addIpRule,updateIpRule,deleteIpRule,restoreIpRule,unlockLogin}`、全政策保護）、`AppState` 5→7、`MSG_KEYS` 13→19、`ip_confidence` 單字面→八態。另含測試基建一塊（G6：`SequenceResetGuard` 廢除＋BL-00070 收攏）。

**零 migration、零 seed 變更（事實）**：m0001 已含 `sys_ip_rule`（11 欄、partial unique `(wbip_cidr, wbip_type) WHERE deleted_at IS NULL`）與三張稽核表（`ip_confidence` 皆 `text` 可空、無 CHECK＝值域擴張零 DDL）；m0002 已含六條政策列（143～148）、`manage_ip-rule` 選單列（78）與其 menu 維政策列（149）、`user:unlock`（157）、`ipRule:*` 四鈕（160～163）、`ip_*` 三鍵（10／50／15）；來源維計數走既有 `idx_login_attempt_ip_time (real_ip, created_at)`（rev5 形 `real_ip <<= $1::inet`：v4 等值與 v6 `/64` 包含同一運算子）、不需新索引 ⇒ BL-00042 原項不觸發、BL-00047 不觸發。

**不入刀**：稽核管理頁與 `access_log_mw`（008 audit-settings-pages）｜解鎖按鈕與其 wrapper（使用者管理頁刀；工程判斷 6）｜no-escalation 本體（BL-00048）｜通用節流 seam｜region GeoIP｜prod 資產（RUNBOOK §16「prod 不入 roadmap」）｜settings 寫端跨鍵守衛（Q4）｜suppressed 麵包屑（BL-00078）｜全域 wire i64 守衛 lint（G5）｜demo 頁去留（BL-00064＋BL-00067）。

### §2 憲法 Amendment 射程（MINOR 1.3.0→1.4.0、一筆）

- **§I.7 島 F 入憲**：F1～F8，以 rev5 v1.10.0 終態字面為底（含射程分界句：來源維節流狀態機本體屬島 E、島 F 只約束其位址輸入與跳過條件）。
- **島 E 四處**：補「來源維計數下界恆兩源、禁成功即重置（刻意不對稱、防統一）」與「解鎖標記讀取故障＝fail-closed（兩維共用機制、故記島 E）」兩句；刪「redis L1 為負快取」（Q7）；設定鍵壞值字面補「越界」（G4；措辭 plan 定）。跨島總則不動（工程判斷 3）。
- **§III.2**：新 ★ 軌道 `BASE-WEB-MANAGE-PAGE-WIRING` (i)（範圍逐支：`src/locales/langs/{en-us,zh-cn}.ts` route／page 兩樹新增型圈界、`src/typings/app.d.ts` page 型節、`src/router/elegant/{imports,routes,transform}.ts`＋`src/typings/elegant-router.d.ts` 產物檔紀律）；`BASE-WEB-I18N-WIRING` (ii) 譯文權威句改三檔 locale（Q3）、(i) 範圍欄處數視 Q6 落地形對齊；(b)／(c)／LOGIN-CAPTCHA (i)／LOGOUT-UX (i)／I18N (iii) 五欄範圍欄精確化為「修改型 N 處＋新增型圈界 M 塊」（G1、BL-00058）。
- 硬序：Amendment accepted 前不動任何 base-web 既有檔（規則端點與解鎖單元之 backend 鍵落 locale 既有檔亦受此閘）。

### §3 後端架構與模組邊界

按功能域分模組、承 rev5 分工：`trust/`（純函式政策判定、零 I/O）與 `ipgate/`（可變判定面＋門鈴）刻意分兩模組；`middleware/`（首次進場：`request_context_mw`＝ConnectInfo 對端＋標頭→`trust` 純函式→注入 extensions；`ip_gate_mw`＝健康／觀測放行→上下文缺席放行→`decide`→5003／403＋阻擋可觀測紀錄；F7 拒絕腿在 login 先於 precheck）。`request_context.rs` 換血：三欄與取值器不動、`real_ip` 改信任錨推導之正規化字串、`ip_confidence` 八態（`nginx_peer` 退役、append-only 舊列不遷移）、轉發鏈欄改判定窗；handler 改自 Extension 取上下文，缺席退路形＝§5 ①。新 handler `handler/ip_rule.rs`（五支；操作者名批次讀）、`handler/throttle.rs`（解鎖）；新 facade `sys_ip_rule`／`sys_operation_log`＋`model/audit`（詞彙取定案形）；`sys_login_attempt` 加來源維計數、帳號維計數排除 `chain_rejected`；`cache/mod.rs` 補來源維與兩維解鎖標記鍵 builder、刪 lock 鍵 builder。`state.rs` 5→7、`main.rs` boot 載信任模型／初載規則集／起 watcher（`into_make_service_with_connect_info::<SocketAddr>` 已在、`ConnectInfo` 首次消費；B-075 lint 守之）、`router.rs` ROUTES 22、`obs.rs` 預註冊新序列與重排降級源名冊、`config.rs` 信任模型載入（含 B-074 IPv4-mapped 網段字面告警＋清集合）。

### §4 節流：兩維、無 L1、由 PG 定案

每次登入嘗試：①讀兩維解鎖標記（讀取 Err＝視為無標記〔fail-closed〕＋立 `redis_down`〔軟區 captcha 整層停用〕；`cache: None` 同算 `redis_down`）→②帳號維三鍵現值（缺鍵／不可解析／越界〔registry 宣告界、G4〕／矛盾組合整組退常數＋告警）＋PG 計數（下界三源：窗起點／窗內最近成功／解鎖標記）→帳號維硬鎖即回（短路省來源維查詢、合成語意不變）→③來源維（L0：命中顯式 allow 或無桶即整層跳過；否則三鍵現值同一驗法整組退＋獨立 label、PG 計數下界恆兩源）→④合成：任一硬鎖→`biz.auth.locked`；否則任一軟區或 `captcha_forced`→captcha gate；否則放行。L2 計數 DbErr＝`count := 0`＋`captcha_forced = !redis_down`（島 E 既定）。三個拒絕分支皆於 `authenticate` 前早退＝零稽核列、零 argon2、零計數桶。降級源名冊：刪 `redis_lock`／`redis_lock_set`，增兩維解鎖標記讀取源與來源維設定／計數源（值集單一權威仍住 `obs.rs`、名稱 plan 定）。

### §5 規則管理端點與操作稽核

五端點處理序：類型二值守門→CIDR 解析與主機位元正規化（寫前拒、零寫入）→防自鎖（變更後規則集對操作者真實來源跑同一 `decide`）→同交易落庫＋操作稽核列（唯一衝突映 `biz.ipRule.conflict`）→成功後 `reload_and_publish`。解鎖：標的導出（畸形＝`biz.throttle.invalidUnlockTarget`、零稽核零狀態）→先落操作稽核列（失敗＝5000 中止）→寫解鎖標記（unix 秒十進位字串）。`sys_operation_log` 首寫面＝規則四寫端＋解鎖；設定寫端維持不落列（已知態）。六新鍵譯文直寫三檔 locale、`app.d.ts` backend 型節同批（I18N-WIRING (ii)(iii) 既有授權內）。契約：新端點契約＋login／refresh／logout 增量列（5000 出口、F7 5003、上下文來源）住本刀 spec contracts（G2、工程判斷 8）。

### §6 前端

`views/manage/ip-rule/{index.vue,modules/ip-rule-operate-drawer.vue,modules/ip-rule-search.vue}`（新增型檔頭標記、免 ★ 授權；取 rev5 HEAD 形）＋`service/api/rev6-ip-rule.ts`（WRAPPER 軌、五支）＋`typings/api/rev6-ip-rule.d.ts`（ADAPT 軌、入 wire-schema 快照面）；locale route／page 樹＋`app.d.ts` page 型節＋路由產物重算（新軌道）；四顆按鈕接既有 `hasAuth`、選單鏈零 seed 改動；備註欄純文字插值。`service/request/index.ts` onError 轉譯塊（Q6）。兩支新碼面機器守（工程判斷 4）：`views/manage/**` 零 `v-html`／`innerHTML`；路由產物四檔重算冪等＋「軌道列檔集＝外掛實產出檔集」；皆附 self-test（植入反例必紅）。

### §7 治理面

rules.yml：刪 ②、檔頭數量詞與兩處引用、③b 錨對齊（BL-00078／工程判斷 5）。RUNBOOK §16 部署 checklist 實文、§9c 還原面擴表、seed 基準模式與「runtime-append 表序列只比存在性」契約（工程判斷 2、G6）、§12 兩支新碼面閘列。LESSONS：LL-00017 補述 G6 之結構解。活書 as-built（feature branch 內）：§5 模組、§6 新增「信任錨與 IP 存取閘——島 F」情境並改寫「登入失敗節流——島 E」情境（兩維、去 L1）、§8 API 慣例（ROUTES 22、msg 名冊權威）與 fork-delta 軌道、§11 `auth_limit` 已知態列之「來源維與信任錨還原不在本 crate」句、§12 詞彙（工程判斷 11）、01／03／10 之 L1 敘述。

### §8 測試與驗收

後端（容器內 `cargo test --workspace -- --test-threads=1`）：`trust` 純函式全態矩陣（七態×三層×兩覆蓋×硬化成立／不成立×正規化折疊×取窗方向×丟欄三語意區辨）＋B-074 載入面（IPv4-mapped 網段字面告警＋清集合）；ipgate 判定矩陣＋熱重載兩次請求反轉＋keep-last-good＋啟動初載失敗放行；防自鎖零寫入；節流兩維合成四組合、來源維穿插成功不重置之負向自證、F7 拒絕列兩維計數分流、★「讀設定現值」變異打在判準上（改值後下一次嘗試即採新值）、越界設定（如 `max_fails=0`）整組退、部分故障腿（計數 DbErr 走補償）；解鎖兩維各一、稽核先於生效；B-075 lint（裸呼形與折行形反例格）；contract 16→22；`schema-gate`（`sys_ip_rule` 仍逐列比對）。測試基建：`SequenceResetGuard` 廢除後全量回歸綠、殘列在場時會話面測試不連坐（造一列真帳號殘列後全量仍綠＝G6 之驗收判準）、稽核斷言水位／窗形、`walkthrough-baseline` 自測含序列口徑新案。前端：`pnpm typecheck`＋`fork-delta-lint`＋`msg-key-gate`＋`wire-schema check`＋兩支新守。CDP（dev 經反向代理、以 extra header 構造公網來源）：兩來源計數隔離／對其一建 deny 即 403 且 toast 顯譯文／防自鎖拒寫／稽核三欄為推導真值；管理頁全程（列表→搜尋→新增正規化→編輯→軟刪→回收桶復原）對照 22080。

### §9 單元切分草案（tasks 定稿於 SDD；此處只定骨）

U0 ★主線：憲法 Amendment＋ADR 群親決（硬閘）→ 依賴＋`config` 信任模型載入（含 B-074）＋`trust/` → `ipgate/`＋facade `sys_ip_rule`＋兩支 lint 實測 → 測試基建（`SequenceResetGuard` 廢除＋水位清理＋`walkthrough-baseline` 序列口徑＝G6；BL-00070 七處收攏）→ `AppState` 5→7＋門鈴 watcher＋boot（B-075 lint、BL-00072）→ `middleware/`＋上下文換血＋login／refresh／logout 取 Extension＋F7／F8（BL-00062）→ 規則五端點＋操作稽核＋防自鎖＋六鍵 → 節流重寫（兩維、去 L1、消費側驗界、BL-00066）→ 解鎖端點 → 前端頁＋新軌道＋兩支新守＋轉譯塊（BL-00077）→ 治理（RUNBOOK／rules.yml／走查工具還原面／活書／LL-00017 補述）→ 收攏（全量閘＋CDP 走查）。約十二單元、與 rev5 同量級；純後端單元不受 U0 base-web 硬閘阻擋、可先行；測試基建單元排在大量新增 DB 案之前。

### §10 風險

1. **locale 兩檔與路由產物四檔為 upstream 熱檔**（rebase 衝突面最大）；緩解＝新增型圈界、產物只重算不手改。
2. **dev 瀏覽器流量收斂單一來源桶**（`fallback` 態、real_ip＝反向代理位址）⇒ 走查易誤觸來源鎖（解鎖自癒）；該位址落結構豁免段＝瀏覽器本身擋不到，阻擋與 403 轉譯之 CDP 驗收必須構造轉發標頭。
3. **去 L1 後鎖中每發 4 支 PG 查詢**（兩維合成時來源維再加 4 支、帳號維硬鎖先短路）；上界＝nginx `auth_limit`、且不高於未鎖路徑。
4. **`AppState` 擴欄與上下文改由中介層注入**連動大量測試建構點（`oneshot` 形不經 make-service＝上下文恆缺席）；缺席退路形已定（§5 ①）＝既有 36 處 `X-Real-IP` 注入測試零改形。
5. **rev5 後刀增量混入風險**（no-escalation、改密節流、`Identity` sid、`access_log_mw`、後刀 obs 序列）：藍本取 rev5 HEAD 形時逐檔剔除，防回歸清單烤入 implementer prompt。
6. **redis 不開持久化**（已知態）：解鎖標記遺失＝可再解鎖自癒、判定面不依賴 redis。
7. **測試基建大範圍機械改動**（`SequenceResetGuard` 69 處＋七處自持殼＋AppState 字面建構點）＝回歸面大、易與功能改動混淆；緩解＝獨立單元、排在功能單元之前、全量回歸綠且以「造殘列後全量仍綠」驗收、`walkthrough-baseline` 口徑同單元改。

## 4. 憲法 §IV 九題預答（供 `/speckit-plan` Constitution Check 起手）

1. base-web 為權威：PASS——五支規則端點與解鎖端點無 upstream 既有呼叫端、屬 rev6 自建管理能力，前端消費端同批交付；回傳型逐欄忠實本刀契約。2. base-web inline：**涉及——授權以 Amendment 先行取得**（新 ★ 軌道七支既有檔；backend 六鍵與轉譯塊屬既有 I18N-WIRING 授權內、範圍欄對齊與五欄精確化併同一次 Amendment）。3. casbin：選單列與政策列已在 seed、動態選單模式本即回傳、四鈕接既有權限碼機制、零 seed 改動。4. §I.3：阻擋復用 `5003`、規則錯誤與解鎖畸形復用 `2222`、13 碼矩陣零觸碰、零新變體；規則 id 為 number＋2^53 守衛；login／refresh／logout 契約補列不改 wire。5. 前代拷貝：零拷貝、重打字消化、註解 rev6 語境重寫（rev5 出處帶 `rev5:` 前綴）；翻案四項（L1、來源維逐鍵退與消費側不驗界、譯文權威、`SequenceResetGuard` 保留設計）與提前帶入一項（B-117）入 research 差異點表。6. §II：零抵觸（未知標頭忽略、動態選單、`/api` 前綴拓樸）；翻碼內舊拍板一處（`state.rs` 恰五欄封條）立 ADR。7. ★軌道：**涉及——授權以 Amendment 先行取得**，管理頁屬「新能力」非用途補完。8. 新表：零、零 migration；消費四表皆 001 基線既有、只寫入不改結構。9. 行為島：**涉及——島 F 隨本刀以 MINOR Amendment 入憲、島 E 細項調整四處**（兩句補、L1 句刪、越界字面補；fail 方向零改）；state-machine 鏡頭＝規則軟刪二態、兩維節流合成、降級矩陣。

## 5. 給 `/speckit-specify` 的輸入摘要

- feature 名＝`004-ip-trust-anchor`；user 故事核心＝稽核記下真實來源與來源信心、超管以規則擋放來源且即時生效、在管理頁維護規則並防自鎖、同一來源輪換帳號名的撞庫被來源維節流擋下、被鎖的帳號或來源可由超管手動解鎖；節流判定面改為每次嘗試由 PG 定案、設定壞值（含越界）一律整組退。
- 直接輸入：本檔＋BL-00028（部分）／00031／00042②／00043／00045／00058／00062／00066／00070／00072／00075／00077／00078＋`rev5:004-ip-trust-anchor` 之 US1～US5、FR、SC、Edge Cases（沿用形、rev6 座標改寫：去 L1 相關條、來源維整組退與消費側驗界、譯文權威改三檔 locale、B-117 轉譯納入、三端點契約增量列、F7／F8 自首版即入、B-074／B-075 自首版即入、wrapper 前綴 `rev6-`、測試基建 G6）。
- ★原 clarify 候選十項——第二輪 grill 已定（九項工程判斷＋⑥拍板 G7；編號沿用；specify 直接抄、clarify 不再以此出題）：
  - ①**上下文缺席退路**＝承 `rev5:004` T048 形＋rev6 `Err` 兩態：login／refresh／logout 取 `Option<Extension<RequestContext>>`，缺席→退 `from_headers`（缺 `X-Real-IP`→5000 不落列；在場→轉錄、信心 `fallback`、對端 NULL、判定窗空）＋結構化 warn＋降級計數；閘放行、來源維整層跳過（＝島 F F1②／F5 入憲字面）；規則寫端與解鎖端點之操作者位址缺席→拒寫（F3①）。依據：production 結構性不可達（`main.rs` 恆掛 `into_make_service_with_connect_info`；rev5 憲法 1.6.0 註明此腿＝「備線被拆」偵測腿）；rev6 既有 `X-Real-IP` 注入之 oneshot 測試 36 處（login 15／refresh 11／logout 9／contract 1）零改形。棄案：mandatory `Extension`（36 處整批改形、缺席 5000＝fail-closed 違 F3）。
  - ②**`redis_down` 判定點**＝節流步驟①任一解鎖標記讀取 Err（或 `cache: None`）即立；L0 跳過來源維時只憑帳號維那次讀取。
  - ③降級源新值集與 label、rules.yml ③b 事件錨＝plan data-model 定（值集權威仍 `obs.rs`）。
  - ④**翻 ADR-00029 之 ADR 形**＝承 ADR-00032 翻 ADR-00016 前例（repo 唯二 supersede 前例同形）：新檔 `supersedes: [ADR-00029]`、明列「決定 N 原意續行、現行依據＝本決定」、只改譯文權威句、現在式引用改指新檔。
  - ⑤走查工具 seed 基準模式沿現有 rc（0 已還原／1 有差／2 環境或結構異常／64 用法）；契約住 RUNBOOK §9c 一句、字面住工具常數（§9c 既定紀律）。
  - ⑥三支依賴＝§6 釘版行（G7）。
  - ⑦**wire 裁判面嚴格模式**：rev6 `tools/wire-schema.py` 零 `additionalProperties`＝與 rev5 同一已知態（未開「禁止額外欄位」）→ 維持不動、本刀已知態 ADR 記一句。
  - ⑧**CDP 構造來源**：`tools/orchestration/cdp.mjs` `connect()` 回傳通用 `send(method, params)` → 走查腳本直呼 `Network.setExtraHTTPHeaders` 帶 `X-Forwarded-For` 構造公網來源、工具零改；對照 22080 時逐項剔除 rev5 後刀改動（§1 末列）。
  - ⑨**水位清理守衛之家**＝`model/src/facade/test_kit.rs`（與既有 `SessionRowsGuard`／`SeedRestoreGuard`／`RowFixupGuard` 同檔；rev5 住 `server/src/model/mod.rs` 只因 rev5 無獨立 model crate）；`sys_operation_log`（runtime-append）只刮自寫列、`sys_ip_rule`（業務表）清列＋setval。
  - ⑩契約增量＝`specs/004-ip-trust-anchor/contracts/wire-auth-delta.md` 一檔記 login／refresh／logout 增量列（基底句指 specs/003 快照）＋新端點各自檔（`wire-ip-rule.md`、`wire-throttle-unlock.md`）；島 E「越界」措辭於 Amendment draft、user 親決時定。

## 6. 隨做隨記

- ADR 待立（刀分支內落、序號接續現行最大號）：主 Amendment（島 F＋島 E 四處＋§III.2 新軌道、I18N-WIRING 三處與五欄精確化）／`AppState` 5→7（supersede ADR-00027）／節流判定面去負快取、由 PG 定案（BL-00066、Q7）／msg 譯文之家（翻 ADR-00029 權威句、Q3）／轉發鏈超長拒絕與判定窗轉錄（F7／F8）／三支依賴進場／本刀已知態（解鎖無 UI 按鈕、dev 經反向代理可達兩態、稽核覆蓋不對稱、logout 故障窗弱 oracle〔Q5〕、redis 持久化重評維持、wire 嚴格模式重評）。
- 依賴釘版（第二輪三源核對、plan research 依賴表照抄）：arc-swap `1.9.2`、futures-util `0.3.34`（`default-features = false`）、toml `1.1.6`（G7）；前兩支已在 rust-api `Cargo.lock` 為傳遞依賴、直接依賴化不動 lock 既有值。
- ADR draft 時點承 003 刀 Q5：plan 期產 draft、tasks 首個主線任務只跑「user 親決→accepted→bump→generate」。
- 收刀 `backlog_done`：BL-00058／00062／00066／00070／00072／00075／00077／00078；改條文：BL-00028（刪 `throttle::load_settings` 半句）／BL-00031（刪 `ip_*` 臂）／BL-00042（刪②）／BL-00043（只剩 access 面）／BL-00045（刪 ip-rule 頁）。
- 收刀 `backlog_add`：解鎖按鈕＋前端 wrapper 待使用者管理頁刀／全域 wire i64 守衛 lint（工程判斷 6）。
- 本檔修訂同顆已落（G3、工程判斷 12）：BACKLOG 條文與觸發欄七條、滯後卷 BL-00049、活書 09 §9.1、LESSONS LL-00022。
- NOTES「下一步」：specify 起手後同批改為 004 進行中；收刀時改 005。
- TDD 發射前置：模型依 memory 通則（implementer 與其餘角色分派、CDP 走查類 implementer 另調）於發射前向 user 確認；「全部 opus」為前一維護批裁定、不外推。
- 活書：§3 設計 §7 所列各節於 feature branch 內改成現在式；C4-L2 拓樸不變（`middleware` 屬 rust-api 內部層）零改。
