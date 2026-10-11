# Implementation Plan: 007 使用者管理與密碼治理——使用者頁全套、斷權、密碼政策與自助改密、委派治理、繁中介面、島 I 入憲

**Branch**: `007-user-password-admin` | **Date**: 2026-10-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/007-user-password-admin/spec.md`（specify 一輪；clarify 零提問；plan 前 user 兩度裁定走查還原工具擴面——遷移帳前置、seed 模式與兩模式系統設定比對改以凍結 seed 合成演進登記〔FR-057〕；plan 期主線定案之 spec 字面修補 E1～E25〔45 組〕見 research R25 末段）＋`docs/brainstorms/007-user-password-admin.md`（拍板 Q1～Q22、grilling GR1～GR9、主線工程判斷①～⑰、設計四節、§IV 九題預答）＋`rev5:007-user-password-admin` 全套與 rev5 凍結 worktree（唯讀）＋brainstorm 期唯讀取證一輪（十一軌各接反駁＋完備性評審）＋plan 期起草審查（十五支起草分八組、各組接核對八支、跨檔評審一支＝24 支 agent；核對 findings 139 筆〔blocker 15／major 42／minor 82〕與評審 52 項〔名稱衝突 12／矛盾 24／覆蓋缺口 7／其他 9〕由主線逐筆處置；user 親決 2 題〔excel 示範頁不改、pro-naive 示範頁記已知態〕）

## Summary

把使用者管理頁與個人中心改密卡自 demo 殼接成真：12 支端點（管理面 10 支住新建 `handler/user.rs`、個人中心 2 支住新建 `handler/user_center.rs`；ROUTES 49→61、政策保護端點 35→45），前後端同刀、CDP 對照 rev5 HEAD 驗收。語意核心六件：①**使用者寫端八支**依固定序判定（活性標的鎖讀→seed 保護→本人規則→包含規則→業務守門）、使用者域同值不寫不記、空字串＝清空 ②**包含規則**（T⊆A∧N⊆A、持 R_SUPER 者 A＝全集）以具名純函式單點實作、9 個消費點於鎖內呼叫、中介層掛點續恆放行 ③**斷權兩層**（停用／刪除／重設／自助改密同交易撤全部有效票＋換發鎖內活性重驗；管理員踢除另立 `admin_kick` 與專屬文案；不做每請求活性判定）④**密碼政策單一驗證點**（七鍵、違規碼八枚、只限兩鍵之攜參明細通道）＋設密冷卻＋改密舊密節流（`cpwd:{uid}`）＋政策壞值設密全拒並告警 ⑤**委派治理與自鎖防護**（三頁按鈕碼顯隱、兩處解鎖入口；R_SUPER 名下角色與選單六碼受保護、選單編輯不得移除尚有受保護授權之碼）⑥**繁中介面接上 runtime、預設繁中**。
一支 seed-only migration `m0003`（零 DDL：六列改受保護、刪 R_ADMIN `user:edit`、增 R_SUPER `ipRule:unlock` 與選單 78 之按鈕碼）＋schema 閘 seed_add 序號合成；走查還原工具升檔形 v4（遷移帳前置、演進登記合成、使用者域面）。憲法一次 MINOR 1.7.1→1.8.0（島 I 入憲、§III.2 管理頁軌道新用途 (v)～(viii)、LOGIN-CAPTCHA (ii)、I18N (i) 改寫與 (iii) 開立、島 B／C 用語、九島）；`MSG_KEYS` 46→68；`AppError` 9→11；**零新依賴**。
技術路徑＝高度參照 rev5 HEAD 形（research R2～R5 之 rev5 對應碼清單與差異點）；BACKLOG 收 9、記 4（BL-00140／BL-00141／BL-00142／BL-00143；本窗淨 −5）、反向確認 3；ADR 十四支（ADR-00074～ADR-00087；spec FR-056 之 ⑫ 併入 spec 刻意分岔表、不另立）已於本 plan 落 draft（`proposed`）；收刀前另立 PATCH Amendment ADR 一支（配號屆時）。

## Technical Context

**Language/Version**: Rust 1.96.1（`rust-api/rust-toolchain.toml`；edition 2024；容器內 build／test 全程 serial）＋TypeScript 6.0.3／Vue 3.5.34（base-web：管理頁軌道新用途 (v)～(viii)、LOGIN-CAPTCHA (ii)、I18N (i)(iii) 之既有檔＋新檔 9 支）＋Python 3 標準庫（`tools/schema-gate.py` 序號合成、`tools/walkthrough-baseline.py` v4、`tools/msg-key-gate.py` 擴腿、新碼面閘 `tools/zh-tw-lint.py`、docsync tests 釘值）

**Primary Dependencies**: 零新依賴、零版本變更——axum 0.8.9、sea-orm／sea-orm-migration 1.1.20、casbin 2.20.0、tokio 1.53.1、argon2 0.6.0、getrandom 0.4.3、redis 1.7.0、metrics 0.24.6、serde_json 1.0.151（`rust-api/Cargo.toml` 現讀）；naive-ui 2.44.1（內含 `zhTW`／`dateZhTW`）、dayjs 1.11.20（內含 `zh-tw` locale）、vue-i18n 11.4.2（`base-web/package.json` 現讀）

**Storage**: PostgreSQL 18.4（001 基線；`sys_user`／`sys_user_role`／`sys_pwd_custody`／`session_event`／`sys_token` 首個使用者域寫入者、`sys_operation_log` 擴寫入者、`casbin_rule`／`sys_menu` 經 m0003 改 seed 列；零 DDL、一支 seed-only migration）；Redis 新前綴 `cpwd:`（改密舊密節流桶；與登入節流 `throttle:` 分離）；rev6 stack 埠 35432／36379

**Testing**: cargo test（`--test-threads=1` 容器內）——facade 真 DB 案（鎖讀、指派全量替換＋角色列鎖、撤票迴圈原語、經手表 upsert）／handler oneshot＋真 seed app 案（寫端固定序逐格、空格理由、同值 no-op、空字串、批刪整批 rollback、復原兩腿、已刪標的 notFound、包含規則 9 消費點正負向與 A＝全集正向、斷權兩層、三向分派、換發活性重驗、冷卻、改密節流、政策壞值、明細通道、選單刪碼守門）／contract 61 case＋新 22 鍵實發點＋授權態矩陣／`authz_entrypoint_lint` 名冊擴列與植入自證／wire-schema 新命名空間正反例／m0003 全新庫重放＋schema 三閘；python 工具 `test` 子命令（schema-gate 序號合成、walkthrough-baseline v4、msg-key-gate 新腿、zh-tw-lint）；前端零測試框架＝`pnpm typecheck`（三語 Schema）＋機器斷言（fork-delta-lint、route-artifact-gate、view-render-guard、msg-key-gate、zh-tw-lint、seed-view-gate）＋兩段 review＋CDP 三方對照

**Target Platform**: Linux 容器（compose project `rev6-admin`；一次性 `migrate` 服務先於 rust-api＝m0003 隨 stack 啟動套用）；host＝WSL2／macOS；CDP 由 host 瀏覽器 `127.0.0.1:9229`、一律 opus[1m]／xhigh agent 操作

**Project Type**: web-service（rust-api server crate：2 新 handler＋1 新 auth 模組＋2 新 facade／throttle 模組＋既有模組擴寫〔清單＝research R2／R6〕＋migration 第三支）＋前端接線（base-web 用途 (v)～(viii)、LOGIN-CAPTCHA (ii)、I18N (i)(iii)＋新檔 9 支）＋憲法 Amendment＋治理（14 ADR、活書、RUNBOOK、工具與閘）

**Performance Goals**: 無業務量化目標（dev workspace）。紀律面：①判定面每請求零外部查詢不變、使用者域寫端零判定面重載 ②不做每請求帳號活性判定（斷權兩層＝同交易撤票＋換發鎖內重驗）③密碼雜湊（argon2 預設參數）於鎖外計算、鎖內只驗證 ④清單分頁上限 100、伺服端固定穩定序 ⑤pre-commit 全鏈秒級（新 python 閘為純讀檔）

**Constraints**: Amendment 硬序（accepted 前 base-web 既有檔零 diff、含 locale backend 鍵）／走查還原工具 v4 早於撰寫 m0003 之單元（spec FR-057 (c)）／測試守衛早於任一寫 seed 帳號或指派之寫端單元／handler 持交易＋`<op>_in_txn`、合併鎖序（advisory(uid)→使用者列→角色列升序→指派；批次先取完全部 advisory）／零每請求活性判定、零使用者域重載／§I.5 rev5 參照紀律（重打字、註解重寫、差異點烤入 prompt）／§III fork-delta 三元組＋Vue 模板屬性行變體／三語同批（型別即機器守）／dev 庫寫入逐步取 user 放行（LL-00053）／review 只讀／rev5 樹與 stack 唯讀／編排全角色 opus[1m]／xhigh

**Scale/Scope**: 61 routes（12 新：GET 3／POST 7／DELETE 2；Policy 35→45、Authed 3→5）／68 msg keys（22 新）／`AppError` 9→11（BizData、ModalLogoutByAdmin）／AuditOperation 5→8／session_event 增 1 事件型＋5 原因／節流降級來源 10→11／新計數族 1＋告警規則 1／m0003 一支（演進帳 9 筆；授權列 163 不變、受保護 19→25、新列 id 164）／base-web：★ 軌道登記 19 列＋新檔 9 支（包裝 2、型別 2、浮層與彈窗 3、改密卡 1、政策 hook 1）／新碼面閘 1（zh-tw-lint）／憲法 +1 島（I）＋用途 (v)～(viii)＋LOGIN-CAPTCHA (ii)＋I18N (i)(iii)／ADR 14＋收刀前 PATCH 1／BACKLOG done 8＋add 3＋反向確認 3／執行單元 24（U0～U23；派發真源＝tasks.md、骨架＝research R23）

## Constitution Check

*GATE: 對照 constitution v1.7.1 §IV 九題（初檢＝Phase 0 前；複檢＝Phase 1 設計後）。第 2／7／9 題判定值「涉及——授權以 Amendment 先行取得」承 003～006 形制；Complexity Tracking 不填（★ 軌道與島皆循憲法明文機制取得授權、非違規）。*

| # | 題 | 判定 | 依據 |
|---|---|---|---|
| 1 | 違反 §I.1 base-web 權威？ | **PASS** | 使用者頁、個人中心、角色與選單頁、IP 規則頁皆為既有面、其呼叫之 12 支端點正是本刀補齊對象；搜尋卡手機與信箱兩欄由後端六欄過濾補齊（§I.1「後端補齊前端已有之功能」）；回傳型逐欄忠實兩支 wire 契約＋wire-schema 快照；wire 型開獨立命名空間 `Api.UserAdmin`／`Api.UserCenter`；與 upstream `Api.SystemManage.User` 之偏離記偏離帳（ADR-00083）；郵件與個資自助不做＝滯後卷 BL-00141（upstream 個人中心為佔位、無個資 wrapper） |
| 2 | 動 base-web inline？ | **涉及——授權以 Amendment 先行取得** | ★`BASE-WEB-MANAGE-PAGE-WIRING` 新用途 (v) 使用者管理頁、(vi) 個人中心改密卡、(vii) IP 規則頁來源 IP 解鎖入口、(viii) 角色與選單頁按鈕碼顯隱（改寫 (ii)／(iii) 列「門在頁級」字面）；★`BASE-WEB-LOGIN-CAPTCHA-WIRING` (ii) 登入表單兩欄只驗必填；★`BASE-WEB-I18N-WIRING` (i) 改寫（兩鍵明細轉譯）與 (iii) 開立（語系型別擴 zh-TW、三處註冊、繁中檔標型、預設 zh-TW）；修改型逐行 `原行:`＋Vue 模板屬性行變體、新增型圈界；新檔 9 支不入表、檔頭一行標記；`src/main.ts` 不改（research R19）。授權鏈＝ADR-00074 draft（已落、proposed）→ user U0 逐款親決 → accepted＋§III.2 各列＋bump 1.8.0＋generate（§V.2 四步、獨立 commit）。★硬序：accepted 前不得動任何 base-web 既有檔（含 locale backend 鍵）；純新增檔不受此閘。驗收錨＝`tools/fork-delta-lint.py`（含範圍欄對賬腿）＋`route-artifact-gate.py` 冪等（不新增 view 目錄＝零重算）＋`view-render-guard.py`＋`zh-tw-lint.py` |
| 3 | menu 走 Casbin enforce？ | **PASS** | 選單可見性與按鈕碼一律由判定面導出（`getUserInfo` 之按鈕集＝casbin 按鈕維）；使用者寫端零 `casbin_rule` 寫入；`casbin_rule`／`sys_menu` 之 seed 改動經 m0003（受保護集之變更屬 seed 基線層級決策＝島 G 之 G2 末句；直接改列、不走執行期撤銷歸檔與操作稽核）；自助路由白名單與 §I.2 之關係另立 ADR-00077（受眾＝本人之自助頁、授權資源頁禁入）；不啟用前端隱藏機制 |
| 4 | wire 對齊 §I.3？ | **PASS** | 信封三欄／`code` string／業務錯誤 HTTP 200／分頁 `PageRes` 不變／逐欄 id 型（i64 欄掛 2^53 守衛）／`msg` 載穩定 key（`MSG_KEYS` 46→68）；13 碼矩陣零觸碰（`admin_kick` 共用 `7777`、明細兩鍵共用 `2222`）；錯誤信封 `data` 於兩鍵攜明細物件——該約束住 §III.2 I18N (i) 列與 002 wire 契約、非 §I.3 本文，由 ADR-00074（I18N (i) 改寫）與 ADR-00076（明細通道）承載；清單型偏離 upstream 宣告型＝偏離帳（ADR-00083、漂移即紅）；驗收錨＝contracts 兩支 wire＋`msg-keys.md`＋data-model wire 映射節 |
| 5 | 拷貝前代 code？ | **否（重打字）** | rust／vue／python 全程重打字、註解 rev6 語境（rev5 出處 `rev5:`）；翻案不帶回四項（使用者域寫端之授權重載、`[rev5-inline]` 標記字面、rev5 測試守衛名、`rev5-` 前綴之包裝與型別檔）與本刀差異點烤入 prompt（research R5）；rev5 碼註之已知錯誤不照抄 |
| 6 | 抵觸 §II 拍板？ | **否** | 未知標頭忽略、動態選單、`/api` 前綴皆不動；accepted ADR 之續行（ADR-00012／ADR-00039／ADR-00047／ADR-00068／ADR-00069）一律以新 ADR 承接（accepted 同顆補 supersedes） |
| 7 | 觸及 §III ★ 軌道？ | **涉及——授權以 Amendment 先行取得** | 既有軌道加用途＝新能力（新接線、跨多檔）非補完；i18n 三檔與 `app.d.ts` 仍最熱（spec ★ 軌道登記表 19 列、風險判準可覆算）；範圍欄以預估填列、各前端單元出口逐檔斷言、收刀前 PATCH 實數化 |
| 8 | 新建業務表含 §I.6 六審計欄？ | **不適用（零新表）** | 一支 seed-only migration `m0003`（零 DDL、不建表；改 `casbin_rule` 列 58～63 受保護旗標、刪列 44、增列 164、改 `sys_menu` 列 78 按鈕清單）；消費之表皆 001 基線既有（`sys_user` 變體 A 含審計欄與成對軟刪欄；`sys_user_role` join 表；`sys_pwd_custody` 經手表；`session_event`／`sys_token`／`sys_operation_log` append 形）；schema-definition 留 001 基線、差額只登演進帳（ADR-00087）；收刀前跑 Day-1 登記三步（RUNBOOK §10；第 3 步以全新庫驗） |
| 9 | 觸及 §I.7 行為島？ | **涉及——授權以 Amendment 先行取得** | 島 I 隨本刀 MINOR 入憲（I1～I5、I7；I6 留空並寫明原因；`rev5:007` 島 I 字面為底、rev6 座標改寫；I1 角色列鎖句、I2 換發重驗與不加每請求判定、I5 釐清句、I7 具名 R_SUPER 與否於 U0 親決）；島 B「踢除」改述為「頂替」、島 C reason 含 `admin_kick`；密碼政策壞值「設密全拒」與島 E「整組退回預設」方向相反之跨島註；島 G 之 G5 末句轉非 vacuous（指派寫端納角色列鎖序）；島 H 之 H2 補句與否於 U0 親決；state-machine 鏡頭＝data-model §2（帳號生命週期、會話撤銷三型、設密冷卻、改密節流桶、政策載入與壞值）＋§3 寫端固定序；方向性反轉自此 MAJOR（射程九島） |

**初檢結論**：第 1／3／4／5／6／8 題 PASS（第 8 題不適用）；第 2／7／9 題「涉及、授權以 Amendment 先行取得」＝條件通過。

**Phase 1 複檢（設計後）**：九題判定不變（PASS 五、不適用一、涉及三＝條件通過）。設計期定案而影響判定依據者逐題記：

| # | 複檢要點（承載） |
|---|---|
| 1 | wire 型十八支（讀 8＋請求 10）入受審名冊、常數定名不撞既有（`contracts/code-gates.md` §4）；清單偏離帳第三列（ADR-00083）；excel 示範頁＝殘存消費面、spec FR-008 射程收窄至使用者管理頁（user 2026-10-05 plan 期親決） |
| 2／7 | Amendment 候選字面（ADR-00074 決定四）以合成憲法實跑 `tools/fork-delta-lint.py --constitution` rc 0（修改型三元組對賬 32、跳過 25；新增型逐檔對賬 14、跳過 15；產物檔跳過 4）；範圍欄訂正——`request/index.ts` 2＋2 實數不變、`locale.ts`／`naive.ts` 單行形預估 0 塊、`dayjs.ts` 預估 2 處修改型、store 繁中選項單行形；(vii) 補鍵以巢狀圈界承接（其機器守＝PATCH 實數化後之對賬腿塊數）、(viii) 選單頁表頭兩 prop 改點落 (ii) 既有標記內補述（預估 3 處）；`src/views/pro-naive/ConfigProvider.vue` 零 diff＋已知態（user 2026-10-05 plan 期親決）；`src/locales/index.ts` 首開同步 `<html lang>`（單行形、ADR-00084 決定 10 甲）；page 新鍵名冊與 zh-tw-lint 四腿＋空值檢查（code-gates §1.2／§2.1） |
| 3 | m0003 屬 seed 基線層直接改列（ADR-00085）；自助白名單之首頁兜底落點（order 999）入 ADR-00077 後果、ADR-00081 款 17 改述 |
| 4 | 明細通道射程守分階段四句＋佔位符對賬取明細型序列化欄名（ADR-00076 決定 7、code-gates §2.3）；002 wire 契約原檔不改、碼註六處補指 ADR-00076（spec FR-051 修補後；ADR-00041 決定 3）；13 碼矩陣不動、另立變體樣本表（code-gates §3） |
| 5 | rev5 對應碼清單與差異點＝research R2～R5（含防回歸清單與翻案不帶回項）；走查密碼字面改執行期串接（quickstart；RL-0054） |
| 6 | 續行型 ADR 五支（ADR-00080／00081／00082／00084／00087）accepted 同顆補 supersedes（code-gates §8.1） |
| 8 | 零 DDL；schema 閘 seed_add 序號合成以研究形辨識序列（ADR-00085 決定 7）；走查還原工具 v4 執行期共用 schema 閘合成鏈（importlib）、仍拒跑之演進形兩種（清理面各表之 seed 列；合成面表之結構演進屬 schema 閘合成未內建之形）據實記入 ADR-00085 與 spec Edge Cases |
| 9 | 島 I 候選字面：I7 射程＝使用者管理面寫端全集（自助改密除外）＋帳號維解鎖；ADR-00043 決定 8 無 ABBA 論證重核＝續真（三失效條件已核未觸發；ADR-00074 決定二）；鎖內構 N（指派寫端①後②前對 T∪N 去重升序鎖讀；ADR-00075 決定 1） |

- 設計期揭出之治理缺口一項：ADR-00032 翻案觸發器①（碼面閘 ≥8 支）於本刀前即已成立而未處置、本刀後碼面閘 10 支——轉 BL-00142（plan 顆新記、`backlog_add` 隨本刀第一筆 events；ADR-00084 後果載複核狀態）。
- **複檢結論**：第 1／3／4／5／6／8 題 PASS（第 8 題不適用）；第 2／7／9 題仍為「涉及、授權以 Amendment 先行取得」＝條件通過；Complexity Tracking 續免填。

## Project Structure

### Documentation (this feature)

```text
specs/007-user-password-admin/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── checklists/requirements.md
├── contracts/
│   ├── wire-user-admin.md     # 管理面十支（清單兩支、寫端八支）＋unlockLogin 帳號維之變更
│   ├── wire-user-center.md    # 個人中心兩支（getPasswordPolicy／changePassword）＋明細通道信封
│   ├── msg-keys.md            # 新 22 鍵（發出點、碼、三語譯文、攜參兩鍵 data 形、page.passwordPolicy 子鍵、跨端閘、落地時序）
│   └── code-gates.md          # fork-delta 新用途／新閘與新腿／名冊擴列／wire 裁判／測試基建／走查工具 v4／觀測與告警／ADR 與帳本
└── tasks.md                   # /speckit-tasks 產（非本命令）
docs/arc42/decisions/ADR-00074～ADR-00087-*.md   # plan 期 draft（proposed）；ADR-00074 於 U0 由 user 逐款親決（Amendment 顆）；其餘依 research R21「ADR 配號與親決時點表」所定時點 accepted
```

### Source Code (repository root)

```text
rust-api/                                        # worktree（rev6-admin-rust-api）
├── migration/src/
│   ├── m0003_seed_button_governance.rs(新)      # seed-only：列 58～63 受保護、刪列 44、增列 164、選單 78 按鈕清單；逐句影響列數斷言、down 反向
│   └── lib.rs(擴)                               # 遷移向量第三支
└── server/
    ├── src/
    │   ├── handler/
    │   │   ├── user.rs(新)                      # 管理面十支；跨檔共用件五支（guard_no_escalation／revoke_sessions_in_txn／finish_user_write／password_policy_err／pwd_set_too_frequent_err，pub(super)）＋明細型 PasswordPolicyDetail／PwdSetTooFrequentDetail；SEED_USER_IDS／SUPER_USER_ID
    │   │   ├── user_center.rs(新)               # getPasswordPolicy／changePassword
    │   │   ├── throttle.rs(改)                  # unlockLogin 帳號維交易化＋包含規則；源碼次序釘
    │   │   ├── menu.rs(改)                      # updateMenu 選單刪碼守門（判定於歸檔之前）
    │   │   ├── route.rs(改)                     # SELF_SERVICE_ROUTES 恆併入；檔頭前代歸因勘誤
    │   │   ├── auth/refresh.rs(改)              # 鎖內活性重驗＋三向分派；模組 doc「兩件不搬」改寫
    │   │   ├── common.rs(消費)／mod.rs(改)      # pub mod user／user_center
    │   │   └── auth/{login,user_info}.rs(改：DTO 遮蔽／碼註)
    │   ├── auth/
    │   │   ├── no_escalation.rs(新)             # ActorScope／actor_scope_of／assert_no_escalation（純函式）
    │   │   ├── mod.rs(改)                       # Identity 增 sid
    │   │   └── enforce.rs(改)                   # 三向分派；no_escalation_check 掛點續恆放行、模組註與 doc 勘誤
    │   ├── model/
    │   │   ├── password.rs(擴)                  # hash／NewPassword::prepare／PasswordPolicy／load_password_policy／validate_against_policy（政策壞值告警發射點）／VIOLATION_* 八枚／cooldown_remaining_secs
    │   │   ├── audit.rs(擴)                     # AuditOperation 5→8
    │   │   └── facade/
    │   │       ├── sys_user.rs(擴)              # 鎖讀兩支、清單兩支、寫端諸件；advisory_lock_user 收窄為交易型
    │   │       ├── sys_user_role.rs(擴)         # T／A 料源、全量替換＋角色列鎖、刪全部、清單角色回填
    │   │       ├── sys_token.rs(擴)             # revoke_sids_of_user 底座＋revoke_all_of_user
    │   │       ├── session_event.rs(擴)         # EVENT_REVOKED＋五原因
    │   │       ├── sys_pwd_custody.rs(新)       # touch／last_set_at
    │   │       └── test_kit.rs(擴)              # UserRowsGuard／SeedUserRestoreGuard／PwdCustodyRowsGuard；UserRoleRowsGuard 回補腿；RedisKeysGuard 增 cpwd:
    │   ├── throttle/change_pwd.rs(新)           # precheck／record_failure／clear（5 次／900 秒）
    │   ├── cache/mod.rs(擴)                     # cpwd: 前綴與鍵 builder、incr_with_window、REASON_ADMIN_KICK
    │   ├── error.rs(擴)                         # BizData／ModalLogoutByAdmin；msg_key 22 常數；MSG_KEYS 46→68
    │   ├── envelope.rs(改)                      # Res::from_err_with_data＝BizData 之 data 上 wire（錯誤 data 恆 null 之唯一例外）；碼註補指 ADR-00076
    │   ├── obs.rs(擴)                           # password_policy_invalid_total 預註冊與出口；THROTTLE_DEGRADED_SOURCES 10→11
    │   └── router.rs(擴)                        # ROUTES 61、路由條數常數
    └── tests/
        ├── contract.rs(改：61 case＋22 新鍵實發點＋授權態矩陣＋清單分頁五案×2＋列 68 探針改植)
        ├── common/mod.rs(擴：UserWriteGuard／SeedUserWriteGuard／PwdCustodyWriteGuard 鏡像＋UserRoleWriteGuard 兩腿＋逐字對賬)
        ├── wire_schema.rs(擴：Api.UserAdmin／Api.UserCenter 受審型、正反例、偏離帳第三列)
        ├── authz_entrypoint_lint.rs(改：NO_ESCALATION_CALL_FILES 新腿＋植入自證；腿⑤零交集維持)
        └── fixtures/wire-schema.json(重抽)

base-web/src/                                    # worktree（rev6-admin-base-web）
├── views/manage/user/{index.vue,modules/user-operate-drawer.vue,modules/user-search.vue}(★(v) 修改型＋新增型)
├── views/manage/user/modules/user-reset-pwd-modal.vue(新)
├── views/manage/{role,menu}/index.vue(★(viii) 修改型；選單頁表頭改點落 (ii) 既有標記內補述)
├── views/manage/role/modules/role-operate-drawer.vue(★(iii) 圈界碼註改述「門在頁級」)
├── views/manage/ip-rule/modules/ip-unlock-modal.vue(新；ip-rule 頁為 rev6 自有檔、表頭 prefix 插槽掛鈕)
├── views/user-center/index.vue(★(vi))／modules/password-card.vue(新)
├── views/_builtin/login/modules/pwd-login.vue(★LOGIN-CAPTCHA (ii))
├── components/custom/pwd-gen-modal.vue(新)  hooks/business/pwd-policy.ts(新)
├── service/request/index.ts(★I18N (i) 兩鍵明細轉譯)
├── service/api/{rev6-user-admin,rev6-user-center}.ts(新 WRAPPER) / typings/api/{rev6-user-admin,rev6-user-center}.d.ts(新 ADAPT)
├── locales/{locale,naive,dayjs,index}.ts(★I18N (iii)；index.ts 首開同步 <html lang>) / store/modules/app/index.ts(★I18N (iii)：預設 zh-TW、語言下拉三項)
├── locales/langs/{zh-cn,en-us}.ts(★各用途 page:／backend 塊) / zh-tw.ts(★I18N (iii)：Schema 標型全樹)
├── typings/app.d.ts(★I18N (iii) LangType＋各用途型節)
└── typings/components.d.ts(若引入新元件＝工具重算形)

tools/schema-gate.py(seed_add 序號合成) / walkthrough-baseline.py(v4；importlib 共用 schema 閘合成鏈) / msg-key-gate.py(BizData 射程守分階段＋佔位符對賬＋前端消費點名冊) / zh-tw-lint.py(新碼面閘) / view-render-guard.py(判準 (b) 具名插槽＋ANCHORS 四頁) / docsync/{snapshot.py(缺歸屬訊息),tests/test_references.py(+12 列)} / bootstrap.sh(閘名冊)   .githooks/pre-commit(zh-tw-lint 段)
deploy/grafana-provisioning/alerting/rules.yml(obs016-password-policy-invalid)   docs/ops/reference-src/{schema-evolution.json(九筆),schema-definition.md(檔頭句),code-gate-contracts.md}
.specify/memory/constitution.md(§I.7 島 I＋島 B／C 用語＋跨島註＋九島＋指針表；§III.2 (v)～(viii)、LOGIN-CAPTCHA (ii)、I18N (i)(iii)；1.8.0；U0)   README.md(tools 樹)
docs/arc42/{05,06,08,10,11,12}-*.md(as-built、feature branch 內) / decisions/ADR-00074～00087＋被續行者（accepted 時 status→superseded）
docs/ops/RUNBOOK.md(§9／§9c／§10／§12)   docs/ops/BACKLOG.md(plan 顆：BL-00142 新記；收刀：done 8)   docs/ops/NOTES.md   docs/ops/events.jsonl(第一筆事件帶 BL-00140／BL-00141／BL-00142 backlog_add；收刀 feature_close)
```

**Structure Decision**：承 rev6 005／006 形——handler 依端點群拆檔、交易殼住 handler（`<op>_in_txn` 首句取 per-user advisory、facade 寫端只收具型交易、可被組合）；使用者管理面十支自成新域檔 `handler/user.rs`、個人中心兩支自成 `handler/user_center.rs`；包含規則之純函式住 `auth/no_escalation.rs`、handler 包裝 `guard_no_escalation` 住 `handler/user.rs` 供 throttle.rs 共用（中介層掛點簽章不動）；使用者域寫端零 `enter_menu_domain`、advisory 使用點檔集與 `DOMAIN_WRITE_SIDE_FILES` 零交集；前端新檔不入 barrel、wire 型開 `Api.UserAdmin`／`Api.UserCenter`、兩份取全部角色之 fetcher 擇 `rev6-role-admin.ts`。高風險共享檔序列鏈（同檔單元不並發）：`router.rs`／`tests/contract.rs`、`error.rs`＋三檔 locale＋`app.d.ts`（隨各拒因鍵首發單元分批）、`handler/user.rs`、`model/facade/{sys_user,sys_user_role,sys_token,test_kit}.rs`、`tests/authz_entrypoint_lint.rs`、`tools/walkthrough-baseline.py`。執行單元＝research R23 骨架（U0 主線兩顆〔Amendment 顆＋施工前提顆〕→U1 工具〔閘序號合成＋走查工具 v4〕→U2 測試基建→U3 骨架→U4 m0003 與選單刪碼守門→U5～U14 後端與裁判面→U15～U20 前端→U21 文件→U22 CDP 三方對照〔已知態觀察、ADR-00081／ADR-00082 親決〕→U23 收刀前承載體檢〔Day-1 三步、PATCH Amendment〕）；每單元 pin bump、Workflow 六件套、review／fix 烤入 RULES scope 塊、TDD 單元保險絲 ≤20 支；編排全角色 opus[1m] xhigh。

## Complexity Tracking

Constitution Check 九題：五題 PASS、一題不適用、三題「涉及——授權以 Amendment 先行取得」（循憲法 §V.2 明文機制、非違規）——本節免填；授權鏈與硬序記於 Constitution Check 第 2／7／9 題與 research R20～R21。
