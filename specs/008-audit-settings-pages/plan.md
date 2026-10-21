# Implementation Plan: 008 稽核與系統設定頁進場——系統設定頁、稽核頁四源與清理、存取日誌寫入、reaper 三 job、島 J 入憲

**Branch**: `008-audit-settings-pages` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/008-audit-settings-pages/spec.md`（specify 一輪；clarify 兩題〔數字框 10 鍵鉗界、存取日誌照 rev4 欄形＋告示〕；plan 期 spec 字面修補 E1～E8 見 research R24——其中 E1〔存取分頁告示只提 403〕出自 user 2026-10-21 轉來之 side agent 提醒、與主線取證同結論）＋`docs/brainstorms/008-audit-settings-pages.md`（拍板 B1～B5、D1～D12、grilling g1～g5、主線工程判斷①～㉖、設計四節、§IV 九題預答）＋`rev5:008-audit-settings-pages` 全套與 rev5 凍結 worktree（唯讀）＋rev4 reaper 與存取軌跡中介層（唯讀）＋plan 期唯讀取證（主線親做、未派 agent）

## Summary

把側欄兩項死項接成真頁：稽核 5 支端點（ROUTES 61→66、政策保護 45→50、可授出集 30→35；新檔 `handler/audit.rs`）、系統設定頁與稽核頁（§III.2 新用途 (ix)(x)），前後端同刀、CDP 對照 rev5 HEAD 驗收。語意核心五件：①**四源讀端**唯讀交易、固定序、寬鬆過濾、讀端打碼單點（島 J1、J4）②**水平線清理**固定序守門＋單交易自記，手動與 reaper 排程共用一支 retention 核（`model/retention.rs`；島 J3 一條規則之結構保證；排程自記列＝哨兵 `0.0.0.0`、操作者空、刪 0 列照落）③**存取日誌寫入**中介層掛於兩受保護子 router 之 enforce_mw 內側、包住授權判定、回應先回後非同步寫、號誌上界 2、fail-open（島 J2；解除 `rev5:R2-9`）④**設定寫端交易化並落操作稽核**、讀 wire 擴宣告旗標與界值（D1、clarify Q1）⑤**reaper 三 job**（token-reap、audit-retention、policy-reconcile 只報不刪）以 rev4 藍本重打、job 本體住 lib、心跳推 pushgateway。
一支 delta migration `m0004`（reaper 最小權限 role＋GRANT；選單 77 增 `audit:purge` 碼＋R_SUPER 按鈕授權列 165）；其前補 BL-00148 零 docker 離線對賬腿（`schema-gate.py offline`＋pre-commit 段）。憲法一次 MINOR 1.8.1→1.9.0（島 J 全入、§III.2 (ix)(x)、I18N (i) 明細轉譯兩鍵→三鍵）；`MSG_KEYS` 68→70；`AppError` 變體維持 11；**新依賴恰一項**（ureq 3.4.2，心跳推送；全域 §6 兩源分歧經 user 2026-10-21 plan 期擇定，research R11.6）。
技術路徑＝高度參照 rev5 HEAD（讀端、清理、兩頁）與 rev4（reaper、存取軌跡中介層、reaper role）；對應碼清單與差異點＝research R2～R5。BACKLOG 收 5、記 0（008 窗淨約 −6）、反向確認 2。ADR 十支（ADR-00099～ADR-00108）已於本 plan 落 draft（`proposed`、各附親決分類）；收刀前另立 PATCH Amendment 一支。

## Technical Context

**Language/Version**: Rust 1.96.1（edition 2024；容器內 build／test 全程 serial）＋TypeScript 6.0.3／Vue 3.5.34（base-web：兩頁 view 與模組新檔、MANAGE (ix)(x) 與 I18N (i)(ii)(iii) 既有檔）＋Python 3 標準庫（`tools/schema-gate.py offline` 新子命令、`tools/msg-key-gate.py` 逐鍵之家、runtime-append 兩工具、`tools/seed-view-gate.py` 摘列）

**Primary Dependencies**: 既有不變——axum 0.8.9、sea-orm 1.1.20、tokio 1.53.1、metrics 0.24.6、metrics-exporter-prometheus 0.18.3（`default-features = false`；reaper 以區域 recorder〔`build_recorder`＋`metrics::with_local_recorder`＋`handle().render()`〕組心跳 body）、naive-ui 2.44.1、vue-i18n 11.4.2；**新增**＝`ureq` 3.4.2（`default-features = false`；兩源分歧〔rev4 lockfile 3.3.0 對 crates.io 最新穩定 3.4.2〕經 user 2026-10-21 plan 期擇 3.4.2；lockfile 連帶新增 `ureq-proto` 0.6.5、`utf8-zero`、`base64` 0.23.1〔與既有 0.13.1、0.22.1 並存＝三版本〕）

**Storage**: PostgreSQL 18.4（四稽核表與 `sys_token` 首個刪除者、`sys_access_log` 首個寫入者、`system_settings` 寫端交易化；唯一 DDL＝m0004 之 `reaper` 角色與 GRANT）；pushgateway（compose metrics profile、心跳接收端）

**Testing**: cargo test（`--test-threads=1` 容器內）——讀端過濾逐維／打碼兩鍵與邊界／唯讀交易負向／清理固定序逐步負向與同時違反位次／原子性 fault-injection（retention 核注入「自記必敗」）／排程清理自記哨兵形與 HTTP 寫端仍拒佔位之對照／存取日誌（未認證與 fallback 零列、`5003`→403、`2222`→200、寫入失敗回應不變＋告警＋計數、慢寫不延遲、在途 drain）／設定寫端稽核（舊→新、同值照落、拒因零稽核、上下文缺席 `5000`）與讀 wire 三欄／reaper（CLI 嚴拒、環境變數三分語意、三 job dry-run 零變動、execute 刪除與自記、對賬植列正負向、心跳失敗不改退出碼）／reaper role 權限正負向（`SET LOCAL ROLE reaper`）／m0004 全新庫重放＋schema 三閘＋序號合成變異／contract 66 case＋授權態矩陣＋兩新鍵實發；python 工具 `test` 子命令（offline 腿一正一反＋逐判準停用、msg-key-gate 新家變異、runtime-append 對賬、seed-view-gate 空表）；前端零測試框架＝型別檢查＋機器斷言＋兩段 review＋CDP 三方對照

**Target Platform**: Linux 容器（compose project `rev6-admin`；一次性 `migrate` 先於 rust-api＝m0004 隨 stack 啟動套用；reaper＝jobs profile sidecar、dev loop 每日一輪三 job）；host＝WSL2；CDP 由 host 瀏覽器 `127.0.0.1:9229`、一律 opus[1m]／xhigh agent 操作

**Project Type**: web-service（rust-api server crate：1 新 handler＋2 新 model 模組〔`audit_query`、`retention`〕＋1 新 facade〔`sys_access_log`〕＋1 新 lib 模組〔`reaper`〕＋1 新 bin〔`reaper`〕＋既有模組擴寫〔清單＝data-model §12〕＋migration 第四支）＋前端接線（兩頁、五模組、wrapper／typings 新檔、三語）＋憲法 Amendment＋治理（十 ADR、活書、RUNBOOK、工具與閘、觀測層）

**Performance Goals**: 無業務量化目標（dev workspace）。紀律面：①存取日誌寫入不佔請求延遲（回應先回）、同時佔用之庫連線上界 2 ②讀端清單分頁上限 100、伺服端固定序 ③清理單交易、刪除謂詞走 `created_at` ④pre-commit 新段（offline 腿）純讀檔、秒級 ⑤心跳推送全程時限 10 秒

**Constraints**: Amendment 硬序（accepted 前 base-web 既有檔零 diff；新增檔不受此閘）／BL-00148 離線腿早於撰寫 m0004 之單元（且先對 m0003 綠）／測試基建（存取日誌守衛與 drain、清理類前置斷言）早於任一寫稽核表之單元／retention 核單一實作（handler 與 reaper 共用、不鏡像）／哨兵只經系統程序具名型構造／連線池設定零改動（BL-00147）、不入登入路徑（BL-00145）／§I.5 rev5／rev4 參照紀律（重打字、註解重寫、差異點烤入 prompt）／§III fork-delta 三元組與新增型圈界／三語同批（型別即機器守）／dev 庫寫入逐步取 user 放行（LL-00053）／清理與排程清理真庫案前置斷言（防刪 dev 庫真實舊列）／jobs profile 不於走查與真庫測試期間起（例外＝U18 jobs 活體一輪之 RUNBOOK §9c 指定步驟、一律 `run --rm`）／review 只讀／rev5 與 rev4 樹與 rev5 stack 唯讀／編排全角色 opus[1m]／xhigh

**Scale/Scope**: 66 routes（5 新：GET 4／POST 1；Policy 45→50）／70 msg keys（2 新；攜參明細三鍵）／`AppError` 11 不變／AuditOperation 8→9（`purge`）／新計數 1（`access_log_write_failed_total`）＋心跳 gauge 族 3（`reaper_*`）＋告警規則 2 新、5 重錨＋儀表板刪 3 面板／m0004 一支（演進帳 2 筆 E-010／E-011；授權列 163→164、序號 165、受保護 25 不變、R_SUPER 按鈕碼 21→22）／base-web：★軌道登記 10 列（含本 plan 補 `request/index.ts`）＋新檔 10 支（兩頁 view、五模組與 composable、wrapper、typings）／新 pre-commit 段 1（schema-offline）／憲法 +1 島（J）＋用途 (ix)(x)＋I18N (i) 紀律欄改寫／ADR 10＋收刀前 PATCH 1／BACKLOG done 5＋add 0＋反向確認 2／執行單元 20（U0～U19；派發真源＝tasks.md、骨架＝research R22）

## Constitution Check

*GATE: 對照 constitution v1.8.1 §IV 九題（初檢＝Phase 0 前；複檢＝Phase 1 設計後）。第 2／7／9 題「涉及——授權以 Amendment 先行取得」承 003～007 形制；Complexity Tracking 不填（★軌道、島與 I18N 紀律欄改寫皆循憲法明文機制取得授權、非違規）。*

| # | 題 | 判定 | 依據 |
|---|---|---|---|
| 1 | 違反 §I.1 base-web 權威？ | **PASS** | 兩頁之選單、route 鍵與五支端點之 seed 政策列早已預埋（001 凍結 seed 列 9／77、139／140／141／158／159），本刀補齊 view 與後端端點（§I.1：base-web 有的功能 rust-api 都要提供對應 endpoint）；wire 型開獨立命名空間 `Api.Audit`（`rev6-` 前綴新檔）、逐欄忠實 rev5 契約形；設定讀 wire 擴欄住 rev6 自有 typings 檔；存取日誌與 reaper 屬後端稽核面、不縮減任何 upstream 功能 |
| 2 | 動 base-web inline？ | **涉及——授權以 Amendment 先行取得** | ★`BASE-WEB-MANAGE-PAGE-WIRING` 新用途 (ix) 系統設定頁進場、(x) 稽核頁進場（形照 (i)／(iv)：`{en-us,zh-cn}.ts` 之 `route:`／`page:` 新增型塊、`app.d.ts` 型節、產物四檔沿 (i) 列）；★`BASE-WEB-I18N-WIRING` (i) 紀律欄「錯誤明細轉譯只限兩鍵」改三鍵（`request/index.ts` 改動落既有新增型圈界塊內、範圍欄處數不變）；backend 子樹新鍵＝I18N (ii)(iii) 既有射程；新增型圈界、零修改型行（預期）；新檔 10 支不入表、檔頭一行標記。授權鏈＝ADR-00099 draft（已落、proposed；條文字面 plan 期已逐款親決）→U0 收尾（作答後改字之款重問、對照表一題、銜接字面一份 diff）→accepted＋§III.2＋bump 1.9.0＋generate（§V.2 四步、獨立 commit）。★硬序：accepted 前不得動 base-web 既有檔。驗收錨＝`fork-delta-lint`（名冊、範圍欄對賬腿）＋`route-artifact-gate` 冪等＋`seed-view-gate`（豁免摘空）＋`view-render-guard`＋`zh-tw-lint` |
| 3 | menu 走 Casbin enforce？ | **PASS** | 兩頁可見性由 seed 選單維政策列 69／142（只授 R_SUPER）經判定面導出；`audit:purge` 按鈕碼與 R_SUPER 授權列經 m0004（seed 基線層級決策、與島 G 之 G2 末句「受保護集之變更屬 seed 基線層級決策」同層〔列 165 不受保護、非該句射程〕；直接改列、不走執行期撤銷歸檔與操作稽核）；讀端與清理零 `casbin_rule` 寫入；policy-reconcile 只讀；不啟用前端隱藏機制 |
| 4 | wire 對齊 §I.3？ | **PASS** | 信封三欄／`code` string／業務錯誤 HTTP 200／`PageRes`／逐欄 id 型（i64 欄掛 2^53 守衛）／`msg` 載穩定 key（`MSG_KEYS` 68→70）；13 碼矩陣零觸碰（兩新鍵共用 `2222`）；錯誤信封 `data` 攜明細之射程三鍵——該約束住 §III.2 I18N (i) 列與 002 wire 契約、非 §I.3 本文，由 ADR-00099（I18N (i) 改寫）與 ADR-00102（明細通道三鍵、supersede ADR-00076）承載；驗收錨＝contracts 兩支 wire＋`msg-keys.md`＋data-model §6 |
| 5 | 拷貝前代 code？ | **否（重打字）** | rust／vue／python 全程重打字、註解 rev6 語境（rev5／rev4 出處帶前綴）；翻案不帶回四項＋本刀差異點 34 條（research R5）烤入 implementer prompt；m0004 非 §I.5 例外②（`m0003` 起 delta 不在例外） |
| 6 | 抵觸 §II 拍板？ | **否** | 未知標頭忽略、動態選單、`/api` 前綴皆不動；accepted ADR 之變更一律以新 ADR 承接（ADR-00076→ADR-00102、ADR-00081→ADR-00103、ADR-00082→ADR-00104、ADR-00091→ADR-00107；accepted 同顆補 supersedes）；ADR-00090 決定 1 以釐清款處理（不 supersede；ADR-00090 決定 5 前例） |
| 7 | 觸及 §III ★ 軌道？ | **涉及——授權以 Amendment 先行取得** | 新頁進場＝新能力（新路由、新命名空間、跨多檔）非補完；i18n 兩檔與 `app.d.ts` 仍最熱（12m 11～12、spec 登記表＋本 plan 補 `request/index.ts` 一列〔低〕）；範圍欄以預估填列、各前端單元出口逐檔斷言、收刀前 PATCH 實數化（前例 ADR-00051／ADR-00072／ADR-00092） |
| 8 | 新建業務表含 §I.6 六審計欄？ | **不適用（零新表）** | m0004 不建表（角色＋GRANT＋seed 兩筆）；消費之表皆 001 基線（四稽核表＝變體 B append-only；水平線刪除不屬變體 B 所禁之竄改＝島 J3 入憲時以交叉指針回填 §I.6 括號句；`system_settings`＝變體 A；`sys_token`＝變體 C）；schema-definition 留 001 基線、差額只登演進帳（ADR-00087）；收刀前 Day-1 登記三步（RUNBOOK §10；第 3 步 pristine 庫） |
| 9 | 觸及 §I.7 行為島？ | **涉及——授權以 Amendment 先行取得** | 島 J（稽核域）隨本刀 MINOR 入憲（J1～J5；J2 回填；`rev5:ADR 0077` 字面為底、rev4 島 J1 分句與 J2 字面補回、J3 含排程清理與自記列形、J5 指島 E 末兩點）；MAJOR 射程九島→十島；島 E 末兩點（解鎖稽核先於標記、上下文缺席拒寫）與島 F 之 F3①（不以佔位位址補稽核列）與哨兵之區分寫入 ADR-00101 與 J3；state-machine 鏡頭＝data-model §2（稽核列生命週期、存取日誌寫入、reaper 執行流、設定寫入） |

**初檢結論**：第 1／3／4／5／6／8 題 PASS（第 8 題不適用）；第 2／7／9 題「涉及、授權以 Amendment 先行取得」＝條件通過。

**Phase 1 複檢（設計後）**：九題判定不變（PASS 五、不適用一、涉及三＝條件通過）。設計期定案而影響判定依據者逐題記：

| # | 複檢要點（承載） |
|---|---|
| 1 | `Api.Audit` 受審型十二支入 wire 裁判名冊（讀端冊七＝四列型、`PurgeAuditLogRes`、`PurgeBelowFloorDetail` 與封閉字面聯集型 `PurgeAuditTable`；請求端冊五＝四 query 型與 `PurgeAuditLogReq`）（`contracts/wire-audit.md`）；設定讀 wire 三欄住 rev6 自有 typings 檔（`contracts/wire-settings.md`） |
| 2／7 | ★軌道表補 `src/service/request/index.ts`（I18N (i)；12m 0／24m 3＝低；改動落既有新增型圈界塊內＝範圍欄不變）——spec 修補 E2；Amendment 條文面增 I18N (i) 紀律欄改寫（research R19 ⑤）；稽核頁不用共用表頭元件＝view-render-guard 腿②錨表不擴 |
| 3 | m0004 屬 seed 基線層直接改列（ADR-00108）；`audit:purge` 不受保護、可撤可授 |
| 4 | 第三攜參鍵之明細型具名 `PurgeBelowFloorDetail`、佔位符對賬取其序列化欄名；msg-key-gate 明細型之家改逐鍵對映（`contracts/code-gates.md` §2.1）；13 碼矩陣不動 |
| 5 | rev5／rev4 對應碼清單與差異點＝research R2～R5（含 rev4 鏡像常數、per-request 無上限 spawn、`operator: None` 自記形、HLL／TTL 觀測不帶回） |
| 6 | 續行型 ADR 四支 accepted 同顆補 supersedes；設定域觸發器之現行承載為 ADR-00091（spec 原指 ADR-00080＝修補 E3） |
| 8 | 零 DDL 於業務表；權限面 DDL 不入演進帳、由 offline 腿結構化列出＋`SET LOCAL ROLE` 權限測承擔（research R12.5、R11.9） |
| 9 | 島 J 候選字面依 brainstorm ㉓；存取日誌 fail-open 與 HTTP 寫端「上下文缺席拒寫」方向相反屬刻意（存取日誌為請求後觀測紀錄）；哨兵只經系統程序具名型構造（型別層防外溢）；存取日誌號誌上界不改 fail-open 方向（等待許可、不丟列）；他島觸及面逐島判讀（不變式皆保持）：島 A／C——token-reap 為 `sys_token`（島 C 之權威）首個刪除者，判準 `expires_at < now() − REAPER_GRACE_DAYS 天`；換發與登出皆先驗章（`jwt::verify_refresh`、`leeway = 0`）後查列＝被刪列之票已不可呈遞，rotate 次序、reuse 唯一觸發形與 status 定案不受影響；島 B／D——`session_event` 清理只刪水平線（≥ `PURGE_MIN_DAYS` 30 天）以前之列，該表除稽核讀端外無判定讀者，頂替落列與 idle 首次落之守門（redis SET NX）不讀既有列；島 E——`sys_login_attempt` 為兩維滑動窗計數源，水平線下限 30 天大於節流窗宣告上界 1440 分鐘＝清理不觸窗內列；島 G——RUNBOOK §8.1 維運 SQL 直刪孤兒授權列（先匯出留存、不寫歸檔列、受保護列命中即停手、重啟重載判定面）屬資料庫層人工處置、不經應用之授權寫端，G1（授權變更與操作稽核同交易、commit 後同步）與 G3（撤銷必歸檔）約束應用寫端、不及於此（同形前例＝RUNBOOK §9c 走查還原與 §10 手動重放直改 `casbin_rule` 後重啟）；處置形承 grilling g3 |

- 設計期揭出與 plan 期作答連帶之 spec 字面修補八項＝research R24 E1～E8（spec 已修補）。
- **複檢結論**：第 1／3／4／5／6／8 題 PASS（第 8 題不適用）；第 2／7／9 題仍為「涉及、授權以 Amendment 先行取得」＝條件通過；Complexity Tracking 續免填。

## Project Structure

### Documentation (this feature)

```text
specs/008-audit-settings-pages/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── checklists/requirements.md
├── contracts/
│   ├── wire-audit.md      # 稽核五端點（四源讀端＋清理）、授權態矩陣、與 rev5 逐欄比對
│   ├── wire-settings.md   # 設定讀 wire 擴三欄、寫端落稽核之語意差額
│   ├── msg-keys.md        # 後端兩鍵、攜參明細三鍵、兩頁 page 節與告示語意
│   ├── reaper-cli.md      # 三 job CLI、環境變數、退出碼、事件欄、心跳、compose、告警
│   └── code-gates.md      # fork-delta 新用途／python 閘與工具／rust 名冊閘／測試基建／觀測／ADR 與帳本
└── tasks.md               # /speckit-tasks 產（非本命令）
docs/arc42/decisions/ADR-00099～ADR-00108-*.md   # plan 期 draft（proposed）；ADR-00099 條文字面已於 plan 期由 user 逐款親決、U0 Amendment 顆 accepted；其餘依 research R20 之時點 accepted
```

### Source Code (repository root)

```text
rust-api/                                            # worktree（rev6-admin-rust-api）
├── Cargo.toml(擴：workspace ureq)                    # ureq 3.4.2（user 2026-10-21 擇定）
├── migration/src/
│   ├── m0004_reaper_role_and_audit_purge.rs(新)      # role＋GRANT＋選單 77＋列 165＋setval；影響列數斷言；down 反向
│   └── lib.rs(擴)
└── server/
    ├── Cargo.toml(擴：ureq)
    ├── src/
    │   ├── bin/reaper.rs(新)                         # 進場點：tracing、退出碼、心跳推送
    │   ├── reaper.rs(新)                             # job 本體：CLI 解析、環境變數三分語意、三 job、連線字串
    │   ├── handler/
    │   │   ├── audit.rs(新)                          # 四讀端＋purge＋DTO＋query 型＋PurgeBelowFloorDetail
    │   │   ├── system_settings.rs(改)                # 寫端交易化＋稽核；讀 wire 三欄；碼註順改
    │   │   └── mod.rs(擴)
    │   ├── model/
    │   │   ├── audit.rs(擴)                          # Purge、SystemJob、SystemAuditEvent；檔頭兩路句
    │   │   ├── audit_query.rs(新)                    # 時間、人員、打碼
    │   │   ├── retention.rs(新)                      # PURGE_MIN_DAYS、RetentionTable、purge_with_self_record、count_before
    │   │   ├── mod.rs(擴)
    │   │   └── facade/
    │   │       ├── sys_access_log.rs(新)             # insert／list／purge_before／count_before
    │   │       ├── sys_operation_log.rs(擴)          # list／purge_before／count_before／write_system_in_txn
    │   │       ├── sys_login_attempt.rs(擴)／session_event.rs(擴)
    │   │       ├── sys_token.rs(擴)                  # count_reap_candidates／reap_expired
    │   │       ├── sys_casbin_policy.rs(擴)          # orphan_counts
    │   │       ├── sys_role.rs(擴)                   # active_codes（活性角色代碼集；對賬「角色無主」判準）
    │   │       ├── sys_user.rs(擴)                   # find_ids_by_name_incl_deleted
    │   │       ├── system_settings.rs(擴)            # find_by_key_for_update／update_by_key_in_txn
    │   │       ├── test_kit.rs(擴)                   # AccessLogRowsGuard、PurgeSelfAuditGuard、app 包裝
    │   │       └── mod.rs(擴)
    │   ├── middleware/mod.rs(擴)                     # access_log_mw、AccessLogLayer、號誌、在途計數
    │   ├── router.rs(擴)                             # ROUTES 66、兩子 router 掛 access_log、層序釘
    │   ├── error.rs(擴)                              # MSG_KEYS 70、兩常數
    │   ├── obs.rs(擴)                                # access_log_write_failed_total
    │   └── lib.rs(擴)                                # pub mod reaper
    └── tests/
        ├── contract.rs(擴)／common/mod.rs(擴)／wire_schema.rs(擴)／authz_entrypoint_lint.rs(擴)／entity_access_lint.rs(擴)
        ├── system_audit_entry_lint.rs(新)／reaper_cli.rs(新；U10 已立 bin 黑箱測檔時併入該檔)   # 系統程序入口名冊閘；reaper 子行程黑箱測
        └── fixtures/wire-schema.json(重抽)

base-web/src/                                        # worktree（rev6-admin-base-web）
├── views/manage/system-settings/index.vue(新)
├── views/manage/audit/{index.vue,modules/*}(新；五模組＋composable)
├── service/api/rev6-audit.ts(新) / typings/api/rev6-audit.d.ts(新) / typings/api/rev6-settings.d.ts(擴三欄)
├── service/request/index.ts(★I18N (i)：既有圈界塊內第三分支)
├── hooks/business/pwd-policy.ts(擴：clearPwdPolicyCache；檔頭句改述)
├── views/manage/user/modules/user-reset-pwd-modal.vue(檔頭快取句改述)
├── locales/langs/{zh-cn,en-us}.ts(★(ix)(x) route／page 塊＋backend 新鍵) / zh-tw.ts(同)
├── typings/app.d.ts(★(ix)(x) page 型節＋backend 型節) / typings/components.d.ts(工具重算：NDatePicker)
└── router/elegant/*＋typings/elegant-router.d.ts(產物重算)

tools/schema-gate.py(offline 子命令＋runtime-append) / walkthrough-baseline.py(runtime-append＋還原集) / msg-key-gate.py(第三鍵＋逐鍵之家) / seed-view-gate.py(豁免摘空) / zh-tw-lint.py(字表表值增列) / docsync/tests/{test_references.py,test_hook_wiring.py}
.githooks/pre-commit(schema-offline 段＋submodule-sync 閘面)
deploy/grafana-provisioning/alerting/rules.yml(③d④⑤⑤b⑥⑥b 現況、⑦⑦b 新) / dashboards/json/{rust-api,reaper,master-overview,audit-log}.json
docker-compose.yml / docker-compose.dev.yml(reaper 段現況、dev loop 三 job)
docs/ops/reference-src/schema-evolution.json(E-010／E-011)
.specify/memory/constitution.md(島 J、§I.6 括號句、§III.2 (ix)(x)、I18N (i)、1.9.0；U0／(ix)(x) 範圍欄實數化、1.9.1；U19 PATCH)
docs/arc42/{05,06,07,08,10,11,12}-*.md、docs/c4/*(as-built、feature branch 內) / decisions/ADR-00099～00108＋收刀前 PATCH ADR 一支（配號＝當下下一號）
docs/ops/RUNBOOK.md(§3／§8〔含孤兒授權處置〕／§9c／§10／§11〔§11.3 改設定頁首選、§11.4 稽核容量與存取日誌〕／§12) / BACKLOG.md(收刀刪 5) / NOTES.md / events.jsonl
```

**Structure Decision**：承 rev6 005～007 形——handler 依端點群拆檔（`handler/audit.rs`）、交易殼住 handler、facade 只收具型交易；retention 共用核上移 model 層使 handler 與 reaper 共用（島 J3 結構保證）；reaper 之可測本體住 lib、bin 只留 CLI 外殼；存取日誌中介層與既有兩支中介層同檔。高風險共享檔序列鏈與單元骨架＝research R22（U0 主線兩顆〔Amendment 顆＋施工前提顆〕→U1 工具前置〔BL-00148 離線腿＋runtime-append〕→U2 測試基建→U3 骨架→U4 m0004→U5～U13 後端與觀測→U14～U15 前端兩頁→U16 走查工具收尾→U17 文件→U18 CDP 三方對照〔ADR-00103／ADR-00106 實測定稿〕→U19 收刀前承載體檢）；每單元 pin bump、Workflow 六件套、review／fix 烤入 RULES scope 塊、TDD 單元保險絲 ≤20 支；編排全角色 opus[1m] xhigh。

## Complexity Tracking

Constitution Check 九題：五題 PASS、一題不適用、三題「涉及——授權以 Amendment 先行取得」（循憲法 §V.2 明文機制、非違規）——本節免填；授權鏈與硬序記於 Constitution Check 第 2／7／9 題與 research R19～R20。
