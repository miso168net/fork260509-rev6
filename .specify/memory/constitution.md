# rev6-admin (fork260509-rev6) Constitution

> **本檔為 rev6 設計凍結權威**：與活書家族（`docs/arc42/` 12 節＋§13、`docs/c4/`、`docs/compliance/`、`docs/process/`）、ADR、`docs/ops/RULES.md`、生成物衝突時以本檔為準（權威鏈＝§V.1）。
> v1.0.0 由 rev5 constitution v1.10.0（rev5 凍結 SHA `7eab28a`、唯讀）依啟動書 `docs/brainstorms/000-doc-architecture.md` §3.8 逐條表搬入、user 親審 diff 後定版（創世拍板紀錄＝ADR-00003）。
> 改動本檔一律走 Amendment 流程（§V.2）；spec-kit `/speckit-plan` 必須對照本檔跑 Constitution Check（§IV）。
> 文件治理**程序**條款（三材質細則、時態、完成即刪、ID 配號、lint 運作模式）住 `docs/ops/RULES.md`——改動走輕量軌、不走 Amendment。

---

## I. Core Principles

### I.1 base-web 為權威（NON-NEGOTIABLE）

**規則**：base-web（`rev6-admin-base-web` 分支實碼、自 upstream soybeanjs example `8be6f9ba` 衍生——基線 SHA 與 rev5 同、啟動書 D14）有的功能，rust-api 都要提供對應 endpoint。設計範圍嚴格、不縮減。

**含義**：
- base-web 的 wire／type／endpoint／route shape，rust-api 必須對齊
- 「v1 從簡」只能是交付排程、不能簡化設計範圍
- 不動 base-web inline（例外見 §III 軌道授權；授權後的變動執行紀律見 §III fork-delta 紀律）
- upstream rebase 友善——不留 upstream 衝突風險高的改動；fork 差異全程 `rev6-inline` 標記可定位

### I.2 menu 權限 Casbin enforce

**規則**：menu 由 Casbin RBAC enforce、有權才顯示。

**含義**：
- 業務 menu 走 `/route/getUserRoutes` → 後端 Casbin enforce 過濾 → 前端顯示
- demo menu 處理：demo view **全部進 `sys_menu` seed、初始僅勾給 `R_SUPER`**——全集完整、可見性由角色勾選層（casbin menu 維度）治理下放；`hideInMenu`／頁面排除等前端隱藏機制**皆不啟用**。例外與釋義（承 rev5:ADR 0005）：①toggle-auth 示範鏈（`function`／`function_toggle-auth`）保留 `R_ADMIN`／`R_USER_COMMON` 初始勾選（恰 4 列、示範「三角色各見不同按鈕」語意所需、承 rev4 終態）；②「不啟用」＝禁止以 hideInMenu 作 demo 可見性治理手段，upstream route meta 自帶之 `hide_in_menu` 值照原樣入 seed、不視為啟用（6 列白名單載 rev5:ADR 0005）
- constantRoutes（builtin 常量集，現為 403／404／500／iframe-page／login 五條、實數以 base-web `createStaticRoutes` 為準）前端寫死、與 menu 無關、不動；constant route 集合可經 §III.2 授權新增——builtin 常量集不動與 Casbin 豁免語意不變

### I.3 wire 契約權威序與不變式（NON-NEGOTIABLE）

**權威序**（對賬裁決）：
1. **base-web 實碼**（`rev6-admin-base-web` 分支：`typings/api/*.d.ts`＋`service/api/*.ts`＋`.env`＋`views/**`）＝ wire **唯一權威**
2. 官方 docs 站＝解釋性文件，僅紀律性約束引為規範
3. mock 實測＝補充回歸 fixture，**不當 shape oracle**

**鎖定不變式**：
- envelope `{data, code, msg}`（無 `success` bool）；`code`＝string `"0000"` 非 number；business error 走 **HTTP 200** 信封
- **id 序列化＝逐欄位忠實 typings**：typings 宣告 number 的欄位回 JSON number、宣告 string 的欄位（如 `MenuRoute.id`／`UserInfo.userId`）於序列化邊界轉字串；DB 一律 i64 自增；serializer 帶 2^53 fail-loud 守衛；**型別謊言帳本歸零起算**（每筆顯式偏離＝拍板、立 ADR）
- **13 碼矩陣整組凍結**：`0000`/`1000`/`2222`/`3333`/`7777`/`7778`/`8888`/`8889`/`9998`/`9999`/`4040`/`5003`/`5000`；HTTP status 例外僅 `4040`→404、`5003`→403，**內部錯誤 `5000` 一律 HTTP 200 信封**；4 保留碼（`7778`/`8889`/`9998`/`9999` 組內後端從不發出者）僅前端 `.env` 分組認得、**型別層全變體窮舉＋`error.rs` 矩陣斷言雙錨**守其從不發出（ADR-00023）；新需求優先 reuse 既有碼
- `msg` 載穩定 i18n key（後端語言無關、不在地化；前端 `$t` 翻譯、未命中 graceful fallback）——「wire 凍結事實」指錯誤碼本身、`msg` 非人話字串；觀測側可讀性補強候選掛 BACKLOG
- 業務驗證 error code＝`2222`；`5xxx` 段為授權／基建、非業務；refresh 類 critical code 絕不用在業務驗證
- 分頁形 `PageRes<T>`＝`{current, size, total, records}`（camelCase、無 `pages`/`success`、空頁 `records:[]`）
- envelope universal 例外僅 2：`/health`（plain text）與 `/metrics`（Prometheus exposition）
- 預設帳號：`Super / Admin / User`（login req）＋ User → User01 alias（getUserInfo response）
- **契約機器化**：typings 抽 JSON Schema 當 contract test 裁判（唯讀、不動官方檔）＋coverage gate（每條 route 必有 contract case）＋碼表 table-driven case；機制隨 wire 地基刀落地

**錨定註**：本節錨定 `rev6-admin-base-web` 分支實碼；若上游演進使碼表／typings 與本節分叉，於 wire 地基刀對賬現形、走 Amendment 校正。

### I.4 SDD＋TDD 混合工作流（NON-NEGOTIABLE）

- 每把刀（spec-kit feature、`NNN-<name>` 分支）的路徑固定為 **brainstorm → SDD 設計鏈 → TDD 實作 → finishing**；階段不可跳、不可反序；期間拍板一律歸 ADR。
- 收尾一律 `git merge --no-ff` 回 `rev6-admin-root`（保留 feature branch 供 audit）；`git push`／`git merge` 不得出現於 finishing 之前。
- 收刀簿記三步：events append＋NOTES＋`python3 tools/docsync generate`（一筆簿記 commit；perf 第四步等細目＝RULES.md）。
- 詳細操作（各階段指令、Workflow 編排、防呆六件套、看門狗、單元收尾序、輕量軌判準）＝`docs/ops/RULES.md`＋CLAUDE.md §2（本檔不重複）。

### I.5 rust-api 全新寫、對前代 source 受控參照（RUSTAPI-SOURCE-ISOLATION）

**規則**：rev6 rust-api 整棵樹自源倉 main `32c5254`（Initial commit）起全新寫；設計以 rev5 已驗證結論為輸入（承接經 ADR provenance、引 `rev5:ADR 00NN`），**code 不拷貝**。實作以 rev5 對應碼為**預設藍本**——先讀後寫、高度參照（承 rev5:ADR 0019）。

**前代 source 立場（rev5 為主、rev4 溯源，皆唯讀參考庫；rev5 樹凍結於 SHA `7eab28a`、由 `tools/bootstrap.sh` 斷言、絕不寫入）**：
- **讀允許**：可 grep／閱讀前代 source 對照驗證（施工參考）
- **拷貝禁止**：實作必須重新打字消化、不可整段複製
- **註解一律重寫**：不拷前代註解；rev6 語境重寫（引 rev6 契約／ADR）、前代出處帶 `rev5:` 前綴（rev4 溯源帶 `rev4:`）
- **防回歸條款**：參照前代 code 時，凡 rev6 拍板已推翻的行為**不得帶回**

**例外**：①`sea-orm-adapter`／`xdb` 工具性 crate 整檔拷貝**（含註解——豁免本節第 3 款「註解一律重寫」；承 rev5、已驗證、工具性質；自證＝`python3 tools/docsync vendored-check` 去整行註解後逐位元、ADR-00022）**；②資料形狀契約三件整檔拷貝——基線結構 migration（`m0001_baseline_schema.rs`、承 `rev5:m001`）、基線 seed migration（`m0002_baseline_seeds.rs`、承 `rev5:m002`）、基線 entity 15 檔——射程鎖 rev5 rust-api 凍結 SHA `92919b9` 之版本；程式內容逐位元承襲（去註解後 diff 全等自證）、檔名依 ADR-00008 四碼；註解依語意判準重寫（四型失效引用必改、前代出處帶 `rev5:`；通用註解可同文）；防回歸條款照常；`m0003` 起 delta migration 與一切業務碼不在此例外（ADR-00009）。

### I.6 業務表審計欄標準（SCHEMA-AUDIT-COLUMNS）

**規則**：業務主表建表（create migration）時 MUST 含 6 審計欄——
`created_at` / `created_by` / `updated_at` / `updated_by` / `deleted_at` / `deleted_by`。

**型與約束**：
- `*_at`：`timestamptz`。`created_at` NOT NULL default `now()`；`updated_at`／`deleted_at` nullable
- `*_by`：operator 的 `user_id`（`bigint` nullable／`Option<i64>`，**非 user_name 字串**）；system seed／migration／未認證情境無 operator → `null`
- **成對**：`deleted_at` 必與 `deleted_by` 同寫；`updated_at`＋`updated_by` 同理
- **時間點欄通則**（v1.6.0、ADR-00060）：表示瞬間之欄一律 `timestamptz`、不限審計欄；MUST NOT 用 `timestamp without time zone`；純日曆日期（不表示瞬間，例：生日）得用 `date`、須於該刀 spec 具名理由；機器守衛＝`tools/schema-gate.py check` 全庫時間欄型別斷言

**archetype 四變體**（整組凍結；各表歸屬隨 schema 刀入活書與 generated/reference/schema）：
- **A 業務全 6 欄**（例：使用者／角色／選單／系統設定表）：如上；soft-delete 表配 partial-uniq `WHERE deleted_at IS NULL`（PK 本身總體唯一者除外）
- **B append-only 日誌**（例：三 log 表）：只 `created_at` NN（＋operator 類 domain 欄）；**無 soft-delete、無 update、不可竄改**；MUST NOT 加 `updated_*`/`deleted_*`（retention 水平線刪除不屬「竄改」——權威釋義＝§I.7 島 J3）
- **C join／狀態機**（例：user-role join＝零審計硬刪；token 表＝僅 `created_at`＋status 狀態機）；★變體 C upsert 釋義（承 rev4:ADR 0085 釋義）：1:1 已驗證值衛星表之 upsert 刷新＝重驗事件覆寫、`verified_at` 即其時戳、不設 `updated_*`——「成對」條款不因此觸發
- **D 治理變體**（例：casbin 規則表＝`protected`/`created_at`/`created_by` 對 stock adapter 隱形；archive 表＝原 grant 欄＋`archived_at/by`＋`archive_reason`、無 update/delete 欄）

**無 retrofit 條款（含範圍釋義）**：本標準自第一條 migration 即生效——建表即帶 archetype 全欄，**不允許「建表漏審計欄、事後補」**。釋義：本條款標的**僅限 archetype 審計欄**；既有表因功能需要加業務／鑑識欄的**刻意、規劃、可逆**演進不在此限——前提是 archetype 欄規則不變（如變體 B 永不加 `updated_*`/`deleted_*`、不可竄改性維持），且非「忘帶事後補」的意外債。

### I.7 行為島 invariants（隨刀進場）

**本節為行為島狀態機不變式的凍結位，隨刀填充。**

**進場規則**：每台狀態機（如 token rotation／policy governance／single-session）隨其刀的 brainstorm 拍板後，以 **MINOR Amendment** 將不變式條文入本節；前代已驗證狀態機之不變式（rev5 憲法 §I.7 已入憲者）為對應刀 brainstorm 的直接輸入（出處經 ADR provenance 溯源、引 `rev5:ADR 00NN`）。入本節後，動任一條不變式走 Amendment；方向性反轉（fail-OPEN/closed 方向、DB-first、踢人雙通道分離等）＝MAJOR。常數值與欄級細節留活書（非凍結面）。

**已入憲行為島**（首批五座由 ADR-00026 於 v1.3.0 隨 003-auth-session 進場；出處 `rev5:ADR 0028`、rev5 v1.3.0 字面為底；各島進場時之 rev6 增補與其後細項調整，逐次見文末 Amendment log）：

**A. token rotation**
- 同一鏈（family）至多一條 `active`；DB partial UNIQUE 為護欄而非唯一防線。
- rotate 次序 MUST 為「舊列轉 `rotated` 並寫 `used_at` → 插新 `active`」，**次序不可反**。
- grace 窗內同票二度換發 MUST 冪等回**既發的同一對**；grace 窗 MUST 大於前端最壞重試間隔。
- reuse 偵測的**唯一觸發形**＝列為 `rotated` 且 grace miss；命中即撤整條家族。
- fail-* 方向：grace 不可用＝**fail-secure**（並發換發觸發 reuse、撤家族；重登復原）。

**B. single-session**
- 政策解析為**兩層**：`effective_single = session_policy=='single' || (session_policy=='inherit' && single_session_default=='on')`。
- 單一會話**只於登入事件判定**；`single_session_default` 翻轉不影響既有會話（不追溯；窗口上限＝refresh 全壽命、值留活書）。
- 頂替（同帳號之新登入使既有會話失效；「踢除」專指管理員結束他人全部會話＝島 I2）MUST 落 `session_event(kicked)` 並寫 denylist；被頂替者在 `(access, refresh)` 窗內換發仍得 `7777`。
- fail-* 方向：`single_session_default` 讀不到＝**off 語意**（刻意與 D、E 方向不同）。

**C. denylist 撤銷**
- `sys_token.status` 為**權威**、denylist 為加速層；兩者不一致時以 status 定案。
- 鍵缺席（nil）＝「未撤」語意 ⇒ 放行；`revoked` 列缺 denylist MUST 靜默 `8888`、**不得落假 reuse**。
- denylist TTL MUST ＝ refresh 全壽命，`kicked`、`admin_kick` 與 `revoked` 三 reason 皆同。
- fail-* 方向：讀不到（連線 Err）＝**fail-closed**——退 PG 查該鏈是否仍有 active，無 active→`8888`；**PG 亦故障 MUST 視為無 active、絕不盲放**。

**D. idle 逾時**
- 門檻＝`refresh_secs − access_secs`；`session_event(idle)` MUST 僅首次落（SET NX 守門）。
- 不等式 `access_TTL ≤ N×30 < N×60` ⇒ idle 命中 **MUST NOT** 寫 denylist。
- fail-* 方向：`last_activity` 不可讀＝**fail-open**（不 idle-reject，以 token exp 為界）。

**E. 登入失敗節流（帳號維）**
- 三區（自由／需驗證碼／鎖定）；判定於**每次登入嘗試**以滑動窗（PG）計數定案、**無快取層負快取**（redis 於本島只承載 captcha 一次性標記與解鎖標記）。
- 軟區與鎖定 MUST 在密碼雜湊驗證**之前**擋下，且**零稽核列、零計數桶**（拒絕不得消耗受害者的額度）。
- fail-* 方向：redis 整體不可用＝**fail-open**（軟區 captcha 要求整層停用、續驗密碼，密碼錯仍計數）；L2（PG）查詢失敗＝**fail-open ＋ 補償**（計數歸零放行並置 `captcha_forced`）；captcha 標記 SET NX 瞬斷（redis 健康）＝**fail-closed 不罰**（拒該次、零計數桶）。
- 上列 captcha 兩層方向刻意相反之理由（記於此以免被「統一」）：整體不可用時若仍要求驗證碼＝驗不了題卻要求、把合法使用者鎖在門外，故停用軟區、密碼錯仍計數保阻力；單次標記瞬斷時若放行＝攻擊者附偽造題即可在瞬斷窗通關（降級恰好只放行對抗性流量），故拒該次；一次性標記寫不進去即無法認定該題已耗，受害者不該被罰計數。
- 節流設定鍵缺失、不可解析、**越界**（超出設定 registry 宣告界值）、或**矛盾組合**（驗證碼門檻大於鎖定門檻）＝該組視同不可用、**整組**退活書常數並發結構化告警（每次載入至多一筆；帳號維與來源維各自獨立判定與告警）；門檻相等＝合法（軟區寬度零）。
- 來源維計數之時間窗下界**恆兩源**（窗起點、解鎖標記）、**禁**「成功即重置」——帳號維取三源（含窗內最近成功）、兩維刻意不對稱（來源維鍵為攻擊者可控之位址、成功即重置＝以一組有效帳密穿插即可清零），記於此以免日後被「統一」。
- 解鎖標記讀取故障＝**fail-closed**（視為無標記、該標的可能仍在鎖定中；至多少解鎖一次、可再解鎖自癒）。該標記為帳號維與來源維**共用**機制，故方向記於本島而非島 F。
- 管理員解鎖端點之操作稽核 MUST **先於**解鎖標記寫入：稽核列寫不進去＝該次解鎖不生效、零標記；稽核已落而標記寫入失敗＝回 `5000`、可重試，重試多記之稽核列明文接受。
- 解鎖端點之操作者上下文缺席或其來源位址取不到 MUST 拒寫 `5000`、不得以佔位位址補足稽核列（與島 F 之 F3① 同向）。

**F. IP 存取閘＋信任錨＋來源維節流**（004-ip-trust-anchor 進場；出處 `rev5:ADR 0040`／`rev5:ADR 0043`、rev5 v1.6.2 釐清後字面為底）
- ★**本島射程**＝位址的真相面（信任錨）與存取判定面（規則集）。來源維節流的狀態機本體（三區、滑動窗、計數下界、解鎖標記）屬**島 E**；本島只約束其**位址輸入**（F4）與**跳過條件**（F5）。
- **F1 判定序與集合語意**：存取判定序**六步固定**——①健康／觀測端點放行 ②請求上下文缺席放行 ③結構豁免段放行 ④allow any-match 放行 ⑤deny any-match 拒絕 ⑥預設放行。規則集為 **any-match 集合語意**：白＞黑＞預設放行、無優先序欄、判定結果與載入順序無關。阻擋只作用於**請求層**：不撤銷既有會話與 token、不寫 denylist（規則解除即恢復）。
- **F2 真相分層**：資料庫為真相、記憶體判定面**每請求零外部查詢**；執行中真相暫不可讀 MUST **沿用上一份已知良好規則集、不清空**（啟動初載無「上一份」⇒ 空集＝全放行，方向同為 fail-open）。
- **F3 fail-* 方向**：全鏈 **fail-open**；fail-closed **恰兩處**——①**寫端自鎖拒寫**（會把操作者自己鎖在門外的規則 MUST 拒寫、零落庫、零重載）★其輸入不可得時同向：判定所需的操作者來源位址取不到時 MUST 一併拒寫、不得跳過檢查放行、亦不得以佔位位址補足稽核列（往 append-only 稽核表寫編造來源＝證據代筆）——此為本項自身的降級方向、非第三條腿（同島 C denylist 讀失敗、島 E 解鎖標記讀失敗，每項不變式自帶「輸入不可得時往哪走」）②**轉發鏈跳數逾上界即拒絕**（F7）。每次降級 MUST 發結構化告警。★日後任一**降級腿**由 fail-open 翻 fail-closed 才是 §V.3 方向性反轉＝MAJOR；本島例外集由一項擴為兩項時已辨明不算反轉（新增的是原不在降級矩陣裡的判定腿）。
- **F4 信任錨為唯一位址輸入**：來源維度一切機制（存取閘、來源維節流、稽核落列、防自鎖）的位址輸入 MUST 為信任錨結果；**受信集與跳過集 MUST 由同一 helper 導出、內容對稱**（分叉即真實來源塌縮為常數）。
- **F5 放行與節流的分界**：命中**顯式** allow 規則者跳過來源維節流；**結構豁免段 MUST NOT 跳**——結構豁免只豁免「阻擋」、不豁免「節流」。
- **F6 Tier-1 錨須傳輸層背書**：Tier-1 位置錨成立 MUST 附傳輸層背書——錨右鄰起、直到傳輸層對端，全屬受信基建；不成立即棄錨、退 Tier-2。受信判定 MUST 用 F4 同一 helper、不得另立第三集合。（無此背書時，攻擊者繞過 CDN 直打來源站並自帶「偽造位址, CDN 邊緣」鏈即可把任意位址寫成真實來源；「鎖定來源站僅接受 CDN 邊緣連線」自此為縱深防禦建議、非承重前提。）
- **F7 轉發鏈跳數上界**：鏈跳數逾上界者，**於登入端點** MUST 拒絕該請求（不服務、不進密碼雜湊驗證）；**其餘端點 MUST 標記**（`ip_confidence=chain_rejected`）**但照常服務**——標記全域、拒絕限登入（逾限只有中介層算得出來，下游拿到的轉發鏈欄已是判定窗、不可重算）。逾限請求 MUST **仍落一列稽核**；該列 MUST 被**帳號維計數排除**（保護受害者：否則以受害者帳號名發敵意鏈即可無限期鎖死該帳號）、被**來源維計數納入**（來源維鍵為攻擊者自身位址）。
- **F8 稽核轉錄的複驗性**：稽核列的轉發鏈欄 MUST **保留判定窗**且與判定軌**共用同一份取窗實作**（結構性保證的是「同一份切分、同一組欄」）；複驗性帶**兩個成立條件**、不得寫成無條件保證：(a) 真實來源由鏈推導（直連腿／回退腿／通道覆蓋的位址取自對端或訪客標頭、本就不在鏈中）(b) 窗未逾字元上限（逾限時稽核欄退為字元對齊尾段、可能切掉最左欄）。

**G. casbin 授權治理**（006-authz-governance 進場；出處 `rev5:ADR 0053`、rev5 v1.10.0 字面為底——G1～G5 沿前代已驗證形〔其中 G1 前半／G3／G4／G5 之行為先由 ADR-00044 決定 3 承載、本次轉正〕、G6 結構性封死為前代新立條〔`rev5:ADR 0054`〕；rev6 增補＝G1 已知降級窗兩類與單一行程前提；rev6 明文化＝G1 授權變更之列舉與觸發射程（含授予面之空 diff）；rev6 改寫＝G1 失敗方向列舉與耗盡後之告警與恢復形、G6 已知態之射程（該頁之封死集端點）；逐項出處見 ADR-00063。字母沿前代記 G、與島 H 對偶（H2↔G3、H1／H5↔G5、H3↔G4））
- **G1 真相唯一與同步失敗契約**：授權真相＝資料庫授權表；授權變更（授予、授權撤銷、連動歸檔、復原回灌）與其操作稽核 MUST 同一交易落地、絕不走判定引擎管理 API 寫面（DB-first）；記憶體授權判定面由真相全量重建導出——授權變更寫端成功 commit 後 MUST 同步、被拒／無作用／標的不存在 MUST NOT 觸發（早退之結構性保證）；★**授予面刻意例外**：三維授權寫端「Applied 即觸發、不問 diff（含空 diff）」，與移除面「成功且實際歸檔 ≥1 列」並陳、勿互相「統一」；觸發矩陣本體留 ADR（ADR-00043 決定 7 與 ADR-00067）。★同步失敗契約：同步 MUST 以「全新重建成功才一步換上」實現、絕不對現役判定面就地清空再載入；失敗 MUST 保留上一份已知良好判定面（絕不空窗、半載或全域拒絕）＋結構化告警＋有界重試，耗盡仍失敗＝維持舊面、恢復＝下次成功同步或重啟。★已知降級窗恰兩類（前提＝單一 rust-api 行程部署；前提與翻案觸發見 ADR-00043）：①commit→換上之有界過渡窗 ②重試耗盡窗——窗內記憶體授權判定面仍為上一份：已撤銷或已歸檔之授權續生效（含 API 授權）、新授予或新復原之授權仍不生效（端點維＝仍回 `5003`）（兩窗語意本體＝ADR-00067、機制細節＝ADR-00043）。★方向反轉（同步失敗改為清空或全域拒絕）＝MAJOR。
- **G2 受保護拒絕**：撤銷集觸及受保護授權列 MUST 整批拒、零變更（於任何寫入之前判定）；拒絕 MUST 使原因可辨識——一因一鍵（明細載體屬活書級、不入條文）；設定或解除受保護旗標之能力經一般管理介面永不提供（防鎖死 by-design；受保護集之變更屬 seed 基線層級決策）。反轉（整批拒改部分成功、開放受保護旗標之管理介面）＝MAJOR。
- **G3 撤銷必歸檔**：授權撤銷＝移入授權歸檔（完整快照＋來源角色識別＋原因值）、授予＝補齊治理欄之寫入（受保護旗標 FALSE＋建立時間與建立者）；刪角色 MUST 同交易全維連動歸檔（含受保護授權列、原因值 `role_soft_delete`）；`role_soft_delete` 歸檔列 MUST NOT 可手動復原；角色刪除單向、無角色復原。反轉＝MAJOR。
- **G4 刪除守門與批次原子**：角色刪除依固定序三層守門（①seeded ②in-use ③self-role）；批次逐項驗證、任一違規**整批拒**（no-partial）、單一交易。反轉＝MAJOR。
- **G5 復原同實例與全端點鎖序**：一切向現役授權寫入、或改動角色活性／啟用狀態之寫端（三維授權寫端、授權復原、角色刪除家族、角色停用）MUST 同交易 `FOR UPDATE` 鎖標的角色列、**鎖內重判前提**後才落寫（lock-then-redecide、永不信 pre-read）；固定鎖序 advisory → 歸檔表列 → sys_role 列 → sys_menu 列 → casbin_rule（選單維／按鈕維授權寫端另入島 H1 序列化域；端點維授權寫端與授權復原不入域）；授權復原 MUST 鎖內重驗（原因值閘＋同實例：歸檔列之來源角色 id＝現役同代碼活角色 id、NULL＝不可復原、誠實退化）後才回灌，重驗腿之固定序與全文＝ADR-00065。★使用者角色指派寫端 MUST 同納本鎖序（該寫端不存在期間本句 vacuous 成立）。反轉（拔鎖序、信 pre-read）＝MAJOR。
- **G6 結構性封死**：屬「`ptype='p' ∧ protected=TRUE ∧ v2 ∈ HTTP 方法白名單`」之（路徑,方法）集合（謂詞式、鎖內以資料庫現況判定、不寫列數）MUST NOT 授予非 R_SUPER 角色；掛點恰兩處＝端點維授權寫端與授權回收桶之端點維復原（雙路徑、同一判準）；違者整批拒、零變更；v2＝`menu` 之受保護授權列不在射程（已知態：可見性可授、該頁之封死集端點仍拒）；守門 MUST 非 vacuous 並配變異自證；決定本體與量測值＝ADR-00064。反轉（部分成功、開放受保護旗標之管理介面、掛點少一處）＝MAJOR。
- 常數（原因值字面集、封死集量測值、觸發矩陣列數、候選集來源、同步重試次數與退避）＝活書／ADR 級、不入條文。

**H. 選單域生命週期**（005-role-menu-crud 進場；出處 `rev5:ADR 0048`、rev5 v1.7.0 字面為底；五條主體沿前代已驗證形——rev6 增補＝H3 受保護選單不可停用、不可改父，H2 已知降級窗兩類之本條後果（同步失敗契約本體住島 G1、H2 互引）；rev6 明文化＝H3 常量父鏈之寫端列舉、H4 兩域消費面補列、H5 常量標的之父鏈重驗；逐項出處見 ADR-00042、ADR-00063。字母沿前代記 H；與島 G 對偶（H2↔G3、H1／H5↔G5、H3↔G4））
- **H1 序列化域**：選單樹五寫端（新增／編輯／刪除／批次刪除／復原）＋角色刪除家族（刪除／批次刪除）＋授權治理之選單維與按鈕維寫端及授權回收桶復原之該兩維分支（條文寫狀態機**終態成員**：授權治理之選單維與按鈕維寫端已入域；授權回收桶復原之該兩維分支因不可復原集擴列而結構性不可達）MUST 於單一 DB 交易級 advisory 序列化域內互斥執行（域鎖為載體、key 值留活書）；每一寫端 MUST 於域內鎖定標的並**重驗全部守門前提後才落寫**（lock-then-redecide、永不信 pre-read）。端點維授權寫入不涉選單域、不屬本域。★**advisory key space 全域唯一**：per-user 鎖以 uid 為 key、域鎖以高位自描述 ASCII 常數為 key——兩空間 MUST NOT 碰撞、新增 advisory 用途 MUST 先核既有 key space。★方向反轉（拆散序列化域、改回無域逐列鎖或無鎖 pre-read）＝MAJOR。
- **H2 同鍵重建零繼承**：選單軟刪 MUST 同交易將其選單維授權（跨全角色）連動歸檔（reason=`menu_soft_delete`）；該選單「獨有」按鈕代碼（刪除後不再屬任何未刪選單〔含停用〕之按鈕碼聯集）之按鈕維授權亦同交易歸檔（reason 同 `menu_soft_delete`）；編輯移除按鈕代碼致其**全域絕版**（聯集域同上）時同理（reason=`menu_button_removed`）。★選單編輯之按鈕代碼移除集（改碼＝移除舊碼）含尚有受保護授權列之代碼者 MUST 整筆拒、零變更（於任何寫入與歸檔之前判定；承島 G2——受保護授權列不經一般管理介面移除）。上列三類歸檔（reason 值 `menu_soft_delete`／`menu_button_removed`）之歸檔列 MUST NOT 可手動復原（gate enforce 於復原權威判定）。同路由鍵重建之新選單 MUST NOT 經任何路徑（現役殘留、判定面殘留、授權回收桶復原）繼承舊實例授權——雙封＝現役無殘留（序列化域＋刪除連動歸檔掃盡）＋歸檔不可回灌（reason gate）；判定面同步使記憶體授權判定面同受本條約束——其同步失敗契約與已知降級窗之本體＝島 G1：兩窗（commit→換上之有界過渡窗、重試耗盡窗）期間，記憶體授權判定面之殘留可使同鍵重建之新實例繼承舊授權，為本條已知降級（恢復＝換上完成或下次成功同步或重啟）。反轉＝MAJOR。
- **H3 樹結構不變式**：選單樹恆無環（改父 MUST 過防環檢查、上溯上限為常數）；活性子項 MUST NOT 掛於已軟刪父層之下——parent 驗證三處一致（新增／改父／復原＝父存在且未刪、**停用不擋**、頂層豁免）；受保護選單 MUST NOT 可刪、**MUST NOT 可停用、MUST NOT 變更其父選單**；存在未刪子項（不論啟停）之選單 MUST NOT 可刪；批次刪除逐項驗證、任一違規**整批拒**（no-partial、單一交易、child-first 拓撲序）。★**常量父鏈常量性**：常量選單 MUST NOT 掛於常量性非真之父下——寫端 MUST 於寫入前驗證父鏈常量性（含改父、設為常量、復原常量標的，及清除自身常量性而其未刪後代存常量者）、違反顯式拒。
- **H4 不可變錨欄與治理域／顯示域分層**：`route_name`（授權列錨／i18n 錨）與 `menu_type` 建後不可變（寫端 MUST 顯式拒變更、MUST NOT 靜默忽略）；選單讀端分兩域——**治理域**（授權候選與映射、管理列表、父選擇器、按鈕碼絕版判定）以「未軟刪」全集為準（含停用）、**顯示域**（使用者可見性、頁面下拉）以「啟用且未軟刪」為準；停用 MUST NOT 被任何全量替換語意升級為撤銷（停用＝暫時下架、非撤銷）。反轉＝MAJOR。
- **H5 復原不回灌**：選單復原 MUST 於序列化域內鎖定並重驗守門（同路由鍵活性衝突／父層未刪／常量標的之父鏈常量性）；復原＝成對清空軟刪欄＋原 status 保留；MUST NOT 回灌任何授權——復原後零授權、可見性一律經授權面板重新勾選下放（與新增選單之兩步流一致）。反轉＝MAJOR。
- 常數（advisory key 值、防環上溯上限、`route_name` 形制上限）＝活書級可調、不入條文。

**I. 使用者域治理**（007-user-password-admin 進場；出處 `rev5:ADR 0063`＋`rev5:ADR 0068`、rev5 v1.10.0 字面為底——I1～I5 沿前代已驗證形〔I5 末句之雜湊生成與驗證區分＝`rev5:ADR 0068`〕、I7 包含規則為前代新立條；★I6 位刻意空缺＝前代 I6 之密碼經手判定與首登強制改密不做、兌現時回填該位；rev6 增補＝I1 角色列鎖讀與鎖內重驗未軟刪、I2 自助改密撤他會話、I5 政策矛盾組合之方向；rev6 明文化＝I1 使用者域寫端不入島 H1 序列化域、I2 換發重驗之讀形與不加每請求判定之射程、I5 政策鍵於每次設密讀現值、I5 不洩面列舉、I7 與島 G6 正交、I7 射程排除自助改密；rev6 改寫＝I1 advisory 同源句（換發不取 advisory）、取鎖時點與批次取鎖序；逐項出處見 ADR-00074。字母沿前代記 I）
- **I1 寫端鎖序與 lock-then-redecide**：一切以**既有**使用者為標的之使用者域寫端 MUST 於任何列鎖之前取得與登入同源的 per-user advisory 鎖；域內固定鎖序 MUST 為 advisory(uid) → 標的使用者列 `FOR UPDATE`（復原用已刪列版）→ 角色列 → 角色指派列寫入，禁反向；改動角色指派之寫端（含軟刪連帶硬刪指派）MUST 對標的現持與寫後角色集之聯集依識別去重升序 `FOR UPDATE` 角色列、鎖內重驗未軟刪（島 G5 ★句之兌現；不改指派之寫端不鎖角色列）；一切守門判定 MUST 鎖內重驗（lock-then-redecide、永不信 pre-read）。新增使用者豁免 per-user 鎖（新識別對並發不可見；並發同名保護＝帳號名活性唯一約束），角色列鎖讀照前句；批次寫端依識別去重升序、全批 advisory 先於任何列鎖、角色列整批聯集一次升序。帳號名與信箱之活性唯一索引為復原衝突守門之顯式前提。使用者域寫端不入島 H1 序列化域。★advisory key space 沿用登入之 uid 鍵（同用途擴消費者、與島 H1 域鎖之高位自描述常數不碰撞、核過）。★方向反轉（拆散序列化、改回無鎖 pre-read）＝MAJOR。
- **I2 斷權即時性與分碼不互換**：停用、刪除、管理端重設密碼 MUST 同交易撤銷標的全部 active 票，自助改密 MUST 同交易撤銷本人其餘 active 票（保留當前會話）——rotated 列不動、重放仍走既有重用偵測（島 A）——並落會話事件；管理員踢除同形（撤全部 active 票）、但為**獨立 reason**。動作序 MUST 權威優先（業務寫＋票作廢＋稽核同一交易落定 → commit → denylist 寫入盡力型、存活＝refresh 全壽命）；寫入失敗只結構化告警、**權威儲存為準**。換發之簽發腿 MUST 於呈遞票列鎖之後、簽發之前以一般讀取重驗使用者活性（啟用且未軟刪；查無列＝不活），不活即拒；重驗不取 advisory、不改換發鎖序；grace 冪等窗回既發之同一對、不屬簽發——此為既有 token 狀態機**新增判定腿**、非 fail 方向反轉。MUST NOT 新增每請求活性判定（登入後之一般端點與帳號資訊讀端不判帳號狀態；斷權兩層＝同交易撤票含 denylist＋換發重驗）。撤銷類、單一會話頂替類與管理員踢除類之體驗碼與文案鍵 MUST NOT 互換（三者各自對應、勿「統一」；reason 見島 C）。★方向反轉（拔換發重驗、改 denylist 優先、改為每請求活性判定）＝MAJOR。
- **I3 seed 帳號與自身結構保護**：前三個種子帳號 MUST 不可刪；第一個（Super）MUST 恆禁停用、恆禁解除其超管角色指派（不因操作者身分而異）——系統恆有至少一個活躍且啟用的超級管理員（結構保證、不需動態計數）；Super MAY 被踢除、被重設密碼。操作者 MUST NOT 刪除、停用、踢除自己，MUST NOT 變更自己的角色指派，MUST NOT 以管理端重設自己的密碼（自助改密走自助端點）；操作者 MAY 改自己的非角色欄與會話政策。守門為碼內常數形。
- **I4 軟刪硬刪指派＋復原零回灌**：使用者軟刪 MUST 同交易硬刪其全部角色指派列（零幽靈掛載、角色域掛載計數守門保持誠實）；復原 MUST NOT 回灌任何指派（復原後零角色、須重新指派）、狀態保留刪除前原值；同帳號名重建之新使用者 MUST NOT 經任何路徑繼承舊實例角色。批次刪除逐項驗證、任一違規（含已刪識別）**整批拒**（no-partial、單一交易）。
- **I5 密碼政策單一驗證點＋登入不驗＋三重不洩**：密碼政策驗證 MUST 為單一驗證點（新增帳號、管理端重設、自助改密三入口共用、零分叉）、政策鍵於每次設密單一快照讀現值、違規 MUST 一次收集全部；長度單位＝字元、另加固定位元組上界 ≤ 登入端形制上限；「禁止密碼與帳號名相同」＝大小寫不敏感相等。★**登入路徑 MUST NOT 驗政策**——政策是設密面的守門、不是登入面的守門；把它掛上登入即令既存帳號的合法憑證因政策事後調整而失效。fail-* 方向：政策鍵矛盾組合（最小長度大於最大長度）＝**設密全拒**並發結構化告警（登入不受影響；與島 E 方向相反之理由見跨島註）。密碼明文與雜湊 MUST NOT 洩漏於任何面：承載密碼之 DTO 除錯輸出 MUST 遮蔽（不得預設印出）；API 回應、操作稽核 payload 與日誌 MUST NOT 含密碼明文或雜湊；密碼雜湊之**生成**（hash）MUST NOT 於持有列鎖期間計算（三入口一律於取鎖前算好再進鎖）；雜湊**驗證**（verify）作為守門判定，依 I1 於鎖內重驗執行。★方向反轉（拆單一驗證點、拔遮蔽、把政策掛上登入路徑、矛盾組合改放行）＝MAJOR。
- **I7 no-escalation 包含規則**：使用者域寫端授權 MAY 由超管於運行期下放給其他角色（seed 預設仍僅 `R_SUPER`、下放為可開關能力、非預設態）；下放後**一切受規則約束之寫端**（使用者管理面寫端全集〔自助改密除外——其標的恆為操作者本人〕＋帳號維解鎖）MUST 於鎖內、任何寫入前判 `T ⊆ A ∧ N ⊆ A`——A＝操作者現役角色集（濾軟刪與停用角色、資料庫現讀；★持 `R_SUPER` 者之 A 視為全集）、T＝標的全部指派列（**不**濾角色狀態）、N＝寫後標的角色集；違者 MUST fail-closed 拒絕（純 key、不洩漏角色差集、零變更零稽核）。seed 保護（I3）與本人諸不 MUST **先於**本規則判定；同級互管允許（零特例）；來源維解鎖不套。判定 MUST 以具名純函式單點實作、諸寫端共用；前端 MUST NOT 預判本規則（後端為唯一裁判）。本規則約束操作者維、島 G6 結構性封死約束角色維——兩者正交、封死不因本規則撤。★方向反轉（拔守門、改 fail-open、改由前端預判、把某支受約束寫端移出射程）＝MAJOR。
- 常數（seed 帳號識別集、政策鍵名與門檻、違規碼集、設密冷卻與改密節流之窗、次數與計數載體、會話事件 reason 字面集、攜參明細通道之鍵集、自助路由白名單成員、advisory key 值）＝活書／ADR 級、不入條文。

**J. 稽核域 retention 與 reporting**（008-audit-settings-pages 進場；出處 `rev5:ADR 0077`、rev5 v1.10.0 字面為底——J1／J3／J4 沿前代已驗證形，J2 以 rev4 島 J2 字面為底回填〔`rev4:ADR 0060`；rev5 之 J2 位刻意空缺〕，J5 改為指針〔前代 J5 之行為於 rev6 住島 E 末兩點＝ADR-00042；前代 J5 末之方向反轉 MAJOR 句不隨之承載（島 E 末兩點本身無具名 MAJOR 句）〕；差異申報＝J1 補回 rev4 統一記錄層分句（其「存取軌跡」依 rev5 J1 四源名改稱「存取日誌」，並補「讀端請求亦落存取日誌列不違本條」）、純唯讀括號之「handler 零業務寫入」（rev4／rev5 同形）改「讀端 handler 與其交易零寫入」、標題「read-only」改「唯讀」；J2 對 rev4 島 J2 之改寫——標題「access-log」改「存取日誌」、「存取軌跡記錄 MUST best-effort」改為已認證請求（認證之後、包住授權判定）完成時 MUST 落一列並列欄、fail-open 句「寫入故障僅結構化告警、MUST NOT 影響業務請求成敗與延遲語意」改寫為「寫入 MUST 不阻塞回應、寫入失敗 MUST 只發結構化告警、MUST NOT 改變業務回應（fail-open）」並移至信任錨句之後、「位址輸入取信任錨」改「來源欄 MUST 取信任錨結論」、「MUST NOT 記錄」「MUST NOT 落列」各改「MUST NOT 記」「MUST 零列」、未認證零列之構造保證由「記錄層位於認證下游＋created_by NOT NULL」改「記錄層構造上不掛公開路由」、rev4「與島 E1／F3 同向」改為與島 E 末點及 F3①「取不到來源位址即拒寫」方向相反之刻意句、方向反轉括號由「改 fail-closed／記 body・query」改「寫入失敗改擋請求、同步阻塞回應、記錄內文」；J3 加入手動與排程清理同一條規則及排程清理自記列之哨兵句；逐項出處見 ADR-00099。字母沿前代記 J）
- **J1 讀端唯讀＋授權面 seed 預設僅超管**：稽核查詢面（操作日誌／存取日誌／登入嘗試／會話事件四源）MUST 純唯讀（讀端 handler 與其交易零寫入、零狀態變更；存取日誌由統一記錄層承載、非查詢職責——讀端請求亦落存取日誌列不違本條）；授權面 **seed 預設僅 `R_SUPER`**，MAY 由超管於運行期下放給其他角色（下放為可開關能力、非預設態——形照島 I7）；回應 MUST 逐欄構造、不序列化原始列；資料源集合增減＝新 ADR。★方向反轉（讀端開寫入面、把 seed 預設改成非 super-only）＝MAJOR。
- **J2 存取日誌寫入 fail-open**：已認證請求（認證之後、包住授權判定）完成時 MUST 落一列存取日誌（操作者、方法、路徑、HTTP 狀態碼、來源欄）；MUST NOT 記請求內文與查詢字串；未認證請求 MUST 零列（記錄層構造上不掛公開路由）；來源欄 MUST 取信任錨結論（島 F 之 F4）；寫入 MUST 不阻塞回應、寫入失敗 MUST 只發結構化告警、MUST NOT 改變業務回應（fail-open）；與島 E 末點及島 F 之 F3①「取不到來源位址即拒寫」方向相反屬刻意——存取日誌為請求完成後之觀測紀錄（身分或來源欄取不到＝跳過該列）、操作稽核為與業務同交易之紀錄（取不到即拒寫）。★方向反轉（寫入失敗改擋請求、同步阻塞回應、記錄內文）＝MAJOR。
- **J3 purge 唯一形狀＝時間水平線＋原子自記**：稽核資料唯一刪除路徑＝來源表白名單×保留天數下限守門之水平線整段刪除——手動清理與排程清理同一條規則、同謂詞同自記形；構造上禁挑列／任意條件刪；每次 purge MUST 同一交易自落操作日誌自記（含來源表、天數、刪除筆數；刪 0 列照落）；排程清理之自記列操作者為空、來源位址為無網路來源之哨兵（非島 F 之 F3① 與島 E 末點所禁之「有操作者而取不到其位址時以佔位位址補足」）；操作日誌源之水平線 DELETE MUST 固定豁免歷史清理自記列（後設證據永久保留）；自記寫入失敗 MUST 整筆回滾（零刪除、零自記、回錯誤）——「回報刪 N 筆、實際零刪除」MUST 構造不可達並以 fault-injection 級測試釘住。fail-* 方向：purge 全鏈 **fail-closed**（任一步失敗＝整筆回滾）。水平線 retention 刪除不屬 §I.6 變體 B 所禁之「竄改」——**本條為其權威釋義**。★方向反轉（開挑列刪、拆自記／豁免、容忍部分成功）＝MAJOR。
- **J4 PII 顯示打碼單點**：稽核讀端 payload 之個資遮蔽 MUST 於後端序列化單點完成（前端 MUST NOT 經手原值）；遮蔽鍵清單＝常數（擴充＝改常數＋補測試）；落庫面白名單（密碼明文／雜湊永不入列、島 I5）為政策本體、不回溯清洗。★方向反轉（拆單點、改前端打碼）＝MAJOR。
- **J5 解鎖稽核先於生效**：見島 E 末兩點（ADR-00042）；本島不重述。
- 常數（`PURGE_MIN_DAYS` 值、來源表白名單成員字面、遮蔽鍵清單、分頁夾界與固定序、拒因鍵字面、保留天數環境變數名與預設值、哨兵字面、存取日誌寫入併發上界）＝活書／ADR 級、不入條文。

**跨島註（方向刻意不一致，記於此以免日後被「統一」）**：登入流程讀 `session_idle_timeout` 設定鍵缺失＝**fail-loud**（`5000`、不猜 TTL 值），與 E 的節流設定鍵缺失走 fail-open 退常數方向相反——前者猜錯會靜默改變所有人的會話壽命，後者猜錯只影響阻力強度。島 I5 之密碼政策鍵矛盾組合（最小長度大於最大長度）＝**設密全拒**並告警，與 E 的節流設定鍵矛盾組合整組退常數方向相反——設密面若退回預設值，可能以寬於管理員意圖之政策放行密碼，且放行之密碼落庫後不隨設定改正而失效（後果殘留）；節流退常數之後果隨設定改正即消失，若改拒則把全體使用者擋在登入門外。設密全拒之衝擊面限設密三入口（登入不驗政策＝I5），恢復＝改正設定鍵。

**跨島總則（設定改值的生效時點）**：每個設定鍵只在其消費事件當下讀現值；已簽發 token 的壽命與已建立的會話不追溯——single-session 於登入事件、idle 門檻與 TTL 於每次簽發（登入／換發）、節流三鍵於每次登入嘗試、密碼政策鍵與設密冷卻秒數於每次設密（既有密碼不追溯＝I5 登入不驗）。

**方向性反轉自此為 MAJOR**（§I.7 進場規則既有條款，此處確認其射程已涵蓋上列十島）。

**承襲指針**（user 拍板 2026-09-03：島體不預載、隨刀重新進場確認＝世代 DoD 的每刀驗收）：rev5 憲法 v1.10.0（唯讀、凍結 SHA `7eab28a`）§I.7 曾入憲十座行為島，對應域動刀時為 brainstorm 的直接輸入、依本節進場規則重新入憲——

| 島 | 名稱 | rev5 入憲載體 |
|---|---|---|
| A | token rotation | rev5:ADR 0028（rev5 v1.3.0）；rev6 已入憲 v1.3.0（ADR-00026） |
| B | single-session | rev5:ADR 0028（rev5 v1.3.0）；rev6 已入憲 v1.3.0（ADR-00026） |
| C | denylist 撤銷 | rev5:ADR 0028（rev5 v1.3.0）；rev6 已入憲 v1.3.0（ADR-00026） |
| D | idle 逾時 | rev5:ADR 0028（rev5 v1.3.0）；rev6 已入憲 v1.3.0（ADR-00026） |
| E | 登入失敗節流 | rev5:ADR 0028（rev5 v1.3.0；來源維兩句隨 rev5 v1.4.0 補）；rev6 已入憲 v1.3.0（ADR-00026） |
| F | IP 存取閘＋信任錨＋來源維節流 | rev5:ADR 0040（rev5 v1.4.0）＋rev5:ADR 0043（rev5 v1.5.0、F7／F8）；釐清至 rev5 v1.6.2；rev6 已入憲 v1.4.0（ADR-00034） |
| G | casbin 授權治理（含 G6 結構性封死） | rev5:ADR 0053（rev5 v1.8.0；G6＝rev5:ADR 0054、復原五腿＝rev5:ADR 0055）；rev6 已入憲 v1.7.0（ADR-00063） |
| H | 選單域生命週期 | rev5:ADR 0048（rev5 v1.7.0）；rev6 已入憲 v1.5.0（ADR-00042） |
| I | 使用者域治理（含 I7 no-escalation 包含規則） | rev5:ADR 0063（rev5 v1.9.0）；I5 釐清＝rev5:ADR 0068（rev5 v1.9.1）；rev6 已入憲 v1.8.0（ADR-00074） |
| J | 稽核域 retention 與 reporting | rev5:ADR 0077（rev5 v1.10.0）；rev6 已入憲 v1.9.0（ADR-00099） |

跨島刻意不一致（各島 fail-* 方向、島 E 與登入設定鍵缺失的相反方向）之處置，於日後新行為島進場時一併重審、不預裁；刻意空缺位（rev5 之 I6）之處置見島 I 標頭（兌現時回填該位）。

### I.8 AI 代理產物必經人審與機器閘（NON-NEGOTIABLE）

- AI 代理（implementer／review／fix 等一切 agent）的產物——程式碼、文件、帳本條目、拍板文——MUST 同時經**人審**與**機器閘**放行，任一缺席即不得入 default branch。人審＝merge 回 default branch 前 user 的明確同意（當次對話），拍板級項（schema／scope／破紀律／user 可見行為）另需 user 親決，逐 diff 親讀非必要條件；機器閘＝適用於該改動之 `python3 tools/docsync lint`、pre-commit／pre-push、容器內測試。
- review agent **只讀不寫** repo 檔；findings 只以回傳訊息承載。
- `git push`／`git merge` 回 default branch MUST 有 user **明確同意**（當次對話內給出、不得沿用前次）。
- 方向性反轉（免人審入主線、review agent 可寫、agent 自主 push／merge）＝MAJOR。
- 出處＝RAD4AI-report Q11（啟動書 §3.8 新增列）；程序細節（審查輪、findings 三分流、hook 接線）＝`docs/ops/RULES.md`。

---

## II. 設計拍板凍結

隨 §I 未承載的獨立小拍板（拍板現況機器索引＝docs/generated/DECISIONS-INDEX.md）；三筆承襲 rev5 §II、2026-09-03 逐筆核 rev5 ADR 摘要無翻案：

| # | 主題 | 拍板凍結 |
|---|---|---|
| #1 | unknown header | rust-api 忽略不認識的 header（如 apifoxToken）；base-web 不動 |
| #2 | auth route mode | dynamic（後端控 menu；`.env` `VITE_AUTH_ROUTE_MODE=dynamic`、ADAPT 軌道） |
| #3 | prod 路徑前綴 | `/api/*` 主流（front-nginx strip 轉發、`/api/metrics` 擋塊） |

**排程性拍板註記**：排程性結論（何時做／先做哪個）**不預載於本檔**——入波排程時逐筆重審立 ADR；重議既有排程性拍板仍走 §V.2 Amendment、**不得默改**。

---

## III. 軌道授權邊界

**跨軌道 fork-delta 執行紀律**（upstream 常態更新，本紀律使 fork 差異在 rebase 時可快速定位；基線 SHA＝rev5 同 SHA `8be6f9ba`、啟動書 D14）：
- **修改型**（既有行語意被改變）：**原行註解保留**、緊鄰新行之上，含標記（如 `// [rev6-inline <軌道代號>] 原行: ...`）——rebase 衝突塊自含對照基準；★**Vue 模板屬性行變體**：改動落在元素開標籤之內（屬性之間放不了註解）時，標記置於該元素開標籤**正上方**、由標記內文點名被改之屬性，`原行:` 載一條真實被替換之基線行原文；同一開標籤內之新增屬性，須與 `原行:` 所載之被替換基線行同處一個變更塊（其間無未改行），始由該標記涵蓋、不另立新增型圈界
- **新增型**（純插入新行／區塊／檔）：插入區塊以 `[rev6-inline ...+]` 標記圈界；新檔僅檔頭一行標記
- **標記統一含 `rev6-inline` token**：全 repo grep 即得完整 fork patch set（upstream 大重構時的災難重建索引）
- **rebase 同步紀律**：解衝突時，註解內「原行」同步更新為 upstream 現行版（防對照基準過時）
- **生成檔紀律**（承 rev5:ADR 0052 條款）：判準＝檔頭帶工具 Generated 標記之機器生成檔（unplugin 元件宣告 `src/typings/components.d.ts` 同族）與路由外掛（elegant-router）重算產出之檔同族（具體檔集隨相關 ★ 軌道 Amendment 落表；ADR-00024）——由工具重算產出、**禁手改**、不逐行標記、不入任何用途之檔級名單；其變更隨引入新元件／新頁之單元同 commit 帶入，審查判準＝diff 只允許工具重算形（宣告行增刪）、出現手寫內容即紅；機器承載＝fork-delta-lint 之檔頭判準（碼面閘、隨子庫刀進場）

### III.1 預設可動軌道（無需額外授權）

| 軌道 | 範圍 | 紀律 |
|---|---|---|
| **BASE-WEB-ADAPT** | `.env*`＋`src/typings/api/` 新檔 | 新增為主；**inline 修改限根層 `.env*` 接管面**（§III.2 表外宣告 2 指定之 devproxy 涵蓋路徑）；禁止刪除既有 type／field |
| **BASE-WEB-WRAPPER** | `src/service/api/rev6-*.ts` 新檔 | 一律新檔（`rev6-` 前綴）；不改既有 service 檔 |
| **RUSTAPI-SOURCE-ISOLATION** | rust-api 整棵樹 | 全新寫；前代受控參照不拷貝（§I.5） |

### III.2 ★ 需 constitution 顯式授權軌道

**本節為 ★ 軌道的凍結位**——每條軌道與其**每一個用途**皆須經 §V.2 Amendment 明文開立；未列於下表者一律無授權（同軌道內的未列用途，不因該軌道已開而自動授權）。**首批軌道隨首刀 Amendment 開立**（user 拍板 2026-09-03：rev5 名冊不預載）。

**機制骨架**（一切 ★ 軌道的共同紀律）：
- ★ 軌道＝base-web inline 的顯式授權邊界：嚴格限本檔已授權之用途／範圍，新用途一律走 §V.2 Amendment
- **補完 vs 新能力判準**：既有授權頁內「單頁、純加、復用既有 wrapper、零新 key/元件/路由」四條件全中的 dispatcher 補完＝**用途補完、不 bump 本檔**；跨多頁新能力＝**須 Amendment**
  - **「零新 key」釋義**（承 rev4:ADR 0041）：指**新 i18n 命名空間／新元件／新路由等「面」級新增**；**不含**既有授權頁、既有子命名空間之下的**資料級 label key**。新增 top-level i18n 命名空間、新元件／路由、跨頁能力仍須 Amendment；判準其餘三條件仍須全中
- 每改一處在 spec 內紀錄（位置＋改動內容＋upstream 衝突風險評估）
- 共用元件改動 MUST 用附加 prop＋安全預設（不變既有呼叫端行為）

**已授權軌道與用途**（機器可解表格；掃描錨＝本表標題列之後、以 `|` 起的資料列，跳分隔列；軌道名以 `**★NAME**` 包覆、掃描端剝 `**` 與 `★`。**授權名冊＝本表 ★ 軌道 ∪ §III.1 三軌道**）：

| 軌道 | 用途 | 範圍（檔案） | 紀律 |
|---|---|---|---|
| **★BASE-WEB-AUTH-WIRING** | (a) constant routes 合併 | `src/store/modules/route/index.ts`（1 處，修改型） | 僅限 `initConstantRoute` 之 dynamic 分支；MUST 為**併入** static 常量集而非取代（seed `constant=TRUE` 為 0 列，取代會清空 login／403／404／500／iframe-page 五條 builtin）；不得擴及 route store 其他分支 |
| **★BASE-WEB-AUTH-WIRING** | (b) 三表單 stub 化 | `src/views/_builtin/login/modules/{code-login,register,reset-pwd}.vue`（各 1 處，修改型） | 僅改 import 指向 stub wrapper＋消滅假成功 toast；不動表單欄位、驗證規則與版面 |
| **★BASE-WEB-AUTH-WIRING** | (c) captcha hook 改打 stub | `src/hooks/business/captcha.ts`（5 處修改型＋1 塊新增型） | 僅改請求目標為 `/auth/sendCaptcha`＋移除假延遲與假成功 toast；hook 對外簽名不變 |
| **★BASE-WEB-LOGIN-CAPTCHA-WIRING** | (i) 登入頁 captcha 軟區 | `src/store/modules/auth/index.ts`（3 處，修改型）／`src/views/_builtin/login/modules/pwd-login.vue`（2 處修改型＋2 塊新增型） | auth store `login()` 改打 wrapper `fetchLoginWithCaptcha`（不改 upstream `auth.ts`）並串通失敗 msg 回傳鏈；軟區為條件渲染，登入失敗後 MUST 重取新題並清空輸入（後端提交即消耗）；**非軟區時零行為變更**；三顆快速登入鈕零 inline |
| **★BASE-WEB-LOGIN-CAPTCHA-WIRING** | (ii) 登入表單規則放寬 | `src/views/_builtin/login/modules/pwd-login.vue`（3 處，修改型） | 嚴格限 `formRules` 之帳號名與密碼兩欄由格式正則改必填規則（前端只驗必填、格式判定交後端——設得進的密碼必須登得進）；★MUST NOT 動 `src/constants/reg.ts`（全域正則為其他表單共用）；`register`／`reset-pwd` 兩支 stub 不動；用途 (i) 之 captcha 軟區條件渲染行為與三顆快速登入鈕零變更 |
| **★BASE-WEB-I18N-WIRING** | (i) 後端 msg 轉譯與錯誤明細轉譯 | `src/service/request/index.ts`（2 處修改型＋2 塊新增型：明細轉譯改寫落既有塊內、不增塊）／`src/locales/langs/{en-us,zh-cn}.ts`（各 1 塊，新增型：`page:` 樹新 top-level `passwordPolicy` 命名空間）／`src/typings/app.d.ts`（1 塊，新增型：`Schema.page` 之 `passwordPolicy` 型節） | 單一 helper `translateBackendMsg(msg, detail?)`＝`$t` 帶原文 fallback；modal `content` 與 `showErrorMsg` 鏈改走之；未命中 MUST graceful fallback，不得吞錯亦不得顯裸 key；同 helper 亦用於**帶信封 msg 的 HTTP 層錯誤**（如 `5003`／403、`4040`／404）之提示；無信封維持原文（`rev5:B-117` 形）。★錯誤明細轉譯**恰三鍵**——密碼政策違規（攜違規碼清單、逐碼譯為 `page.passwordPolicy` 子鍵）、設密冷卻（攜剩餘秒數、具名插值）與稽核清理下限（攜下限天數、具名插值）；其餘錯誤信封 `data` 恆 null、仍以純 key 提示；違規子鍵為單一共用命名空間（請求層、即時規則提示與產密元件共用）、三語鍵集 MUST 相等；明細通道射程與受眾＝ADR-00102 |
| **★BASE-WEB-I18N-WIRING** | (ii) locale backend 樹 | `src/locales/langs/{en-us,zh-cn}.ts`（各 1 塊，新增型） | 插入錨為**獨佔一行**的 `  backend: {`；三檔（含新檔 `zh-tw.ts`、新增型不入名冊）backend 子樹鍵集 MUST 各自與後端 `MSG_KEYS` 全等（跨端閘）；譯文之家＝三檔各自的 backend 子樹（`en-us`／`zh-cn`／`zh-tw` 各為該語譯文權威；鍵集由跨端閘對賬、不另立譯文表） |
| **★BASE-WEB-I18N-WIRING** | (iii) Schema 型節與繁中 runtime | `src/typings/app.d.ts`（1 處修改型＋1 塊新增型）／`src/locales/locale.ts`（0 塊，新增型：匯入與對映皆單行形）／`src/locales/naive.ts`（0 塊，新增型：獨立匯入行與兩表各一項皆單行形）／`src/locales/dayjs.ts`（2 處，修改型：預設參數與退路；匯入與對映皆單行形）／`src/locales/index.ts`（1 處，修改型）／`src/store/modules/app/index.ts`（2 處，修改型：預設值與既有標籤；繁中選項為單行形） | 補 `App.I18n.Schema` 之 `backend` **必填**型節；`LangType` 擴 `'zh-TW'`；locale、元件庫（繁中語系與日期語系）、日期庫（`zh-tw`）三處註冊 zh-TW；未選過語言之預設改 zh-TW（`locales/index.ts`、`store/modules/app/index.ts`、`locales/dayjs.ts` 三處；選過者照記）、首次載入即以現行語言同步 `<html lang>`；語言下拉恰三項「简体中文／繁體中文／English」；退路語言不變；零新依賴；`src/main.ts` 本用途零 diff（開發期根元件驗證器之語言判斷不改）；`src/views/pro-naive/ConfigProvider.vue` 本用途零 diff（擴充元件庫只內建簡中與英文兩語，zh-TW 下 pro-naive 示範頁之擴充元件文案退其英文預設＝已知態）。`src/locales/langs/zh-tw.ts` 為 rev6 自有檔（檔頭一行標記、不入本表），以完整 `App.I18n.Schema` 標型＝三語鍵集之型別機器守、各樹隨各用途同批補齊（臺灣用語） |
| **★BASE-WEB-LOGOUT-UX-WIRING** | (i) 登出前撤銷接線 | `src/layouts/modules/global-header/components/user-avatar.vue`（1 處，修改型） | `onPositiveClick` 改 async、登出前 best-effort `await` logout wrapper，**失敗不得阻斷** `resetStore()`。★用途 (ii)（reLogin toast）**不在本次授權** |
| **★BASE-WEB-MANAGE-PAGE-WIRING** | (i) IP 規則管理頁進場 | `src/locales/langs/{en-us,zh-cn}.ts`（各 2 塊，新增型：`route:` 樹與 `page:` 樹）／`src/typings/app.d.ts`（1 塊，新增型：`Schema.page` 之 `manage.ipRule` 型節）／`src/router/elegant/{imports,routes,transform}.ts`＋`src/typings/elegant-router.d.ts`（產物檔 4 支） | `en-us`／`zh-cn` 兩檔 locale 只在 `route:`（鍵 `manage_ip-rule`）與 `page:`（`manage.ipRule` 子樹）各插一塊新增型圈界、三語鍵集 MUST 相等；`app.d.ts` 只補 `page.manage.ipRule` 型節（★必需：`page:` 為顯式型樹、既有 (iii) 只涵蓋 `backend`）；產物四檔採**產物檔紀律**——僅由路由外掛重算產出、禁手改、驗收＝重算冪等（`tools/route-artifact-gate.py`）＋「本列產物檔集＝外掛實際產出檔集」斷言；★明文**不要求逐行原文標記**：標記於下次重算即被抹除、物理上不可維持，故以冪等檢查（連單行手改都抓得到）替代註解紀律。頁面三檔、`rev6-ip-rule.{ts,d.ts}` 為新增檔、不入本表。帳號維解鎖入口屬本軌道用途 (v)、來源 IP 解鎖入口屬用途 (vii)，皆不入本用途 |
| **★BASE-WEB-MANAGE-PAGE-WIRING** | (ii) role／menu 管理頁 CRUD 接真 | `src/views/manage/role/index.vue`（6 處修改型＋2 塊新增型）／`src/views/manage/role/modules/role-operate-drawer.vue`（6 處修改型＋4 塊新增型）／`src/views/manage/role/modules/role-search.vue`（1 處修改型＋1 塊新增型）／`src/views/manage/menu/index.vue`（16 處修改型＋7 塊新增型）／`src/views/manage/menu/modules/menu-operate-modal.vue`（16 處修改型＋6 塊新增型）／`src/components/advanced/table-header-operation.vue`（3 處修改型＋1 塊新增型）／`src/locales/langs/{en-us,zh-cn}.ts`（各 4 塊，新增型：`page:` 樹 `manage.role`／`manage.menu` 既有子命名空間之資料級補鍵）／`src/typings/app.d.ts`（4 塊，新增型：`Schema.page` 之 `manage.role`／`manage.menu` 對應型節） | 嚴格限 demo 殼接真後端（列表／搜尋／新增編輯 drawer·modal／刪除批刪／回收桶開關／備註欄／父選擇器／頁面下拉）；共用表頭元件只准附加「顯示新增」「顯示批刪」兩布林 prop（預設 true、以帶預設值之宣告承載；既有呼叫端零行為變化）；★同目錄 `role/modules/` 之 `menu-auth-modal.vue`／`button-auth-modal.vue` **不入本用途名單**（屬本軌道用途 (iii)；本用途之修改型標記出現於該兩檔＝紅〔名冊三元組判定〕）；`menu/modules/shared.ts` 經基線兩向 diff 判定零改動、不入名單；三語鍵集 MUST 相等；`route:` 樹零新增（role／menu 頁 route 鍵 upstream 既在）；路由外掛產物四檔本用途零變動（不新增 view 頁）；`src/typings/components.d.ts` 之重算走 §III 生成檔紀律、不入本列；後端拒因鍵落 `en-us`／`zh-cn` 兩檔 locale `backend:` 樹與 `app.d.ts` backend 型節＝既有 I18N-WIRING (ii)(iii) 射程、不隨本列擴列 |
| **★BASE-WEB-MANAGE-PAGE-WIRING** | (iii) 三顆授權彈窗接真（含首頁下拉） | `src/views/manage/role/modules/menu-auth-modal.vue`（14 處修改型＋6 塊新增型）／`src/views/manage/role/modules/button-auth-modal.vue`（23 處修改型＋3 塊新增型）／`src/views/manage/role/modules/role-operate-drawer.vue`（3 塊，新增型；本用途不帶修改型）／`src/locales/langs/{en-us,zh-cn}.ts`（各 1 塊，新增型：`page:` 樹 `manage.role` 既有子命名空間之資料級補鍵）／`src/typings/app.d.ts`（1 塊，新增型：`Schema.page` 之 `manage.role` 對應型節） | 嚴格限兩顆既有授權彈窗自 demo 殼接真後端、並經角色抽屜掛載新增之端點權限彈窗（選單維／按鈕維／端點維之現況讀、候選讀與全量寫入＋首頁下拉之首頁讀寫＋受保護項鎖定＋端點權限彈窗之路徑群組勾選）；模板之勾選雙向綁定一行不動（受控勾選集以可寫 computed 承接）；角色抽屜本用途只准新增第三鈕「端點權限」與端點權限彈窗之引入、顯隱狀態與掛載（新增型；★同檔雙用途——與 (ii) 並存、標記各帶其用途號；角色抽屜編輯時狀態欄之送出修法（ADR-00070）屬 (ii) 既有圈界、不入本用途）；端點權限彈窗為新增型新檔（檔頭一行標記、不入本表）；`src/views/manage/role/index.vue` 本用途零 diff；角色抽屜三顆授權鈕不設按鈕碼（其讀寫端點屬封死集、非 R_SUPER 連授權現況都載不出；角色頁其餘操作鈕之按鈕碼顯隱屬本軌道用途 (viii)）；三語鍵集 MUST 相等；`route:` 樹零新增；路由外掛產物四檔本用途零變動；`src/typings/components.d.ts` 之重算走 §III 生成檔紀律、不入本列；後端拒因鍵落 `en-us`／`zh-cn` 兩檔 locale `backend:` 樹與 `app.d.ts` backend 型節＝既有 I18N-WIRING (ii)(iii) 射程、不隨本列擴列 |
| **★BASE-WEB-MANAGE-PAGE-WIRING** | (iv) 授權回收桶頁進場 | `src/locales/langs/{en-us,zh-cn}.ts`（各 2 塊，新增型：`route:` 樹與 `page:` 樹各一）／`src/typings/app.d.ts`（1 塊，新增型：`Schema.page` 之 `manage.policyArchive` 型節） | 形照 (i)：`en-us`／`zh-cn` 兩檔 locale 只在 `route:`（鍵 `manage_policy-archive`）與 `page:`（`manage.policyArchive` 子樹）各插一塊新增型圈界、三語鍵集 MUST 相等；`app.d.ts` 只補 `page.manage.policyArchive` 型節（★必需）；路由外掛產物四檔之授權沿 (i) 列（產物檔紀律＋重算冪等＋產物檔集斷言）、本列不重複列名；頁面與搜尋模組兩檔為新增型新檔、不入本表；頁面目錄由 seed 選單列之 component 字面決定、圖示以 DB 為唯一真源（不寫 static meta）；表格橫向捲動寬＝各欄寬之和；復原鈕無按鈕碼 gating（門＝頁級選單維受保護授權列＋列級可復原旗標）；`src/typings/components.d.ts` 之重算走 §III 生成檔紀律、不入本列；後端拒因鍵＝既有 I18N-WIRING (ii)(iii) 射程、不隨本列擴列 |
| **★BASE-WEB-MANAGE-PAGE-WIRING** | (v) 使用者管理頁接真（含回收桶、列操作下拉、列解鎖、重設與產密浮層、七碼顯隱） | `src/views/manage/user/index.vue`（13 處修改型＋8 塊新增型）／`src/views/manage/user/modules/user-operate-drawer.vue`（23 處修改型＋12 塊新增型）／`src/views/manage/user/modules/user-search.vue`（4 處，修改型）／`src/locales/langs/{en-us,zh-cn}.ts`（各 2 塊，新增型：`page:` 樹既有 `manage.user` 子命名空間之資料級補鍵）／`src/typings/app.d.ts`（2 塊，新增型：`Schema.page` 之 `manage.user` 對應型節） | 嚴格限 demo 殼接真後端（清單六欄搜尋與分頁／回收桶切換兩資料源、已刪模式隱搜尋卡並換復原鈕／新增編輯抽屜〔帳號名編輯態停用、持停用角色之灰色保留選項、會話政策欄僅編輯態且非超管停用並提示、本人列狀態與角色停用、狀態與角色只在改動時送〕／單刪批刪／列操作下拉之踢除下線、重設密碼、解鎖登入／七枚按鈕碼逐鈕顯隱、表頭新增與批刪走既有「顯示新增」「顯示批刪」兩 prop／記事欄純文字插值）；搜尋卡只准拔除手機與信箱兩欄之格式驗證；表格橫向捲動寬＝各欄寬之和同批改；重設密碼浮層、產密浮層、API 包裝與型別為新增型新檔（檔頭一行標記、不入本表）；前端 MUST NOT 預判包含規則（島 I7）；三語鍵集 MUST 相等；`route:` 樹零新增（`manage_user` route 鍵 upstream 既在）；路由外掛產物四檔本用途零變動（不新增 view 頁）；`src/typings/components.d.ts` 之重算走 §III 生成檔紀律、不入本列；後端拒因鍵落 `en-us`／`zh-cn` 兩檔 locale `backend:` 樹與 `app.d.ts` backend 型節＝既有 I18N-WIRING (ii)(iii) 射程、不隨本列擴列 |
| **★BASE-WEB-MANAGE-PAGE-WIRING** | (vi) 個人中心改密卡進場 | `src/views/user-center/index.vue`（2 處修改型＋1 塊新增型）／`src/locales/langs/{en-us,zh-cn}.ts`（各 1 塊，新增型：`page:` 樹新 top-level `userCenter` 命名空間）／`src/typings/app.d.ts`（1 塊，新增型：`Schema.page` 之 `userCenter` 型節） | 嚴格限父層骨架改寫＋只掛「修改密碼」卡（舊密碼一路、無信箱與手機選項；其餘卡位留白）；改密卡與密碼政策 hook 為新增型新檔（檔頭一行標記、不入本表）；入口沿既有頭像下拉（`user-avatar.vue` 本用途零 diff）；三語鍵集 MUST 相等；`route:` 樹零新增（`user-center` route 鍵 upstream 既在）；路由外掛產物四檔本用途零變動 |
| **★BASE-WEB-MANAGE-PAGE-WIRING** | (vii) IP 規則頁來源 IP 解鎖入口 | `src/locales/langs/{en-us,zh-cn}.ts`（各 1 塊，新增型：`page:` 樹 `manage.ipRule` 子命名空間之資料級補鍵）／`src/typings/app.d.ts`（1 塊，新增型：`Schema.page` 之 `manage.ipRule` 對應型節） | 嚴格限 IP 規則頁表頭前綴插槽之「解鎖來源 IP」鈕（按鈕碼 `ipRule:unlock` 顯隱）與輸入 IP 之彈窗，經與帳號維解鎖共用之同一 API 包裝呼叫解鎖端點之來源維（不套包含規則）；IP 規則頁三檔為 rev6 新增檔、解鎖彈窗為新增型新檔（檔頭一行標記、皆不入本表）；★`manage.ipRule` 補鍵與型節之插入點位於本軌道用途 (i) 既有圈界塊內——本用途以巢狀圈界（塊首塊尾帶 (vii)）承接、(i) 塊首尾不動；三語鍵集 MUST 相等；`route:` 樹零新增；路由外掛產物四檔本用途零變動 |
| **★BASE-WEB-MANAGE-PAGE-WIRING** | (viii) 角色頁與選單頁按鈕碼顯隱 | `src/views/manage/role/index.vue`（2 處修改型＋2 塊新增型）／`src/views/manage/menu/index.vue`（1 處修改型＋2 塊新增型） | 嚴格限表格操作鈕依按鈕碼逐鈕顯隱（角色頁 `role:add`／`role:edit`／`role:delete`；選單頁 `menu:add`〔含新增子選單〕／`menu:edit`／`menu:delete`）、表頭新增與批刪走既有「顯示新增」「顯示批刪」兩 prop；選單回收桶之復原鈕與角色抽屜三顆授權鈕不設碼（其讀寫端點屬封死集）；★同檔雙用途——與 (ii) 並存、標記各帶其用途號；改點落於用途 (ii) 既有修改型標記所涵蓋之行（選單頁表頭開標籤之兩 prop 值）者，於該 (ii) 標記內文同批補述本用途改點、不另立本用途標記（無可載之基線 `原行:`）；角色抽屜、選單彈窗與共用表頭元件本用途零 diff；i18n 零新鍵（locale 與 `app.d.ts` 本用途零 diff）；路由外掛產物四檔本用途零變動 |
| **★BASE-WEB-MANAGE-PAGE-WIRING** | (ix) 系統設定頁進場 | `src/locales/langs/{en-us,zh-cn}.ts`（各預估 2 塊，新增型：`route:` 樹與 `page:` 樹各一）／`src/typings/app.d.ts`（預估 1 塊，新增型：`Schema.page` 之 `manage.systemSettings` 型節） | 形照 (i)：`en-us`／`zh-cn` 兩檔 locale 只在 `route:`（鍵 `manage_system-settings`）與 `page:`（`manage.systemSettings` 子樹）各插一塊新增型圈界、三語鍵集 MUST 相等；`app.d.ts` 只補 `page.manage.systemSettings` 型節（★必需）；路由外掛產物四檔之授權沿 (i) 列（產物檔紀律＋重算冪等＋產物檔集斷言）、本列不重複列名；頁面為新增型新檔、不入本表；頁內零按鈕級 gating（設定兩端點屬封死集、門＝頁級選單維授權）；後端宣告集外之設定列唯讀；`zh-tw.ts` 為 rev6 自有之整檔新增型檔、不入本表（三語由「三語鍵集 MUST 相等」與型別守承擔） |
| **★BASE-WEB-MANAGE-PAGE-WIRING** | (x) 稽核頁進場 | `src/locales/langs/{en-us,zh-cn}.ts`（各預估 2 塊，新增型：`route:` 樹與 `page:` 樹各一）／`src/typings/app.d.ts`（預估 1 塊，新增型：`Schema.page` 之 `manage.audit` 型節） | 形照 (i)：`en-us`／`zh-cn` 兩檔 locale 只在 `route:`（鍵 `manage_audit`）與 `page:`（`manage.audit` 子樹）各插一塊新增型圈界、三語鍵集 MUST 相等；`app.d.ts` 只補 `page.manage.audit` 型節（★必需）；路由外掛產物四檔之授權沿 (i) 列、本列不重複列名；清理入口 MUST 依按鈕碼 `audit:purge` 顯隱（碼與清理端點授權各自獨立）；自由文字欄（XFF、快照內容）一律純文字插值、MUST NOT 以 HTML 渲染；頁面（含頁內快照對話框、無獨立檔）、其模組（四張搜尋卡、清理浮層、時間區間 composable）、`rev6-audit.{ts,d.ts}` 為新增型新檔、不入本表；`zh-tw.ts` 同 (ix) |

**表外三項適用宣告**：
1. 範圍欄處數以 `rev6-inline` 標記實數為準——量法＝修改型 `原行:` 數、新增型**圈界形塊數**（單行形新增型不入範圍欄、由活書 08 §8.4 分列）；實作期改動同批更新（例外：範圍欄明文「不預估」或以預估值填列之列，實數得延至下一次 §V.2 Amendment 實數化，延後即登記回填義務）；**檔級名單則是硬邊界**——名單外的 base-web 既有檔一律無授權，需要動即回本節走 §V.2。
2. devproxy 接管面由 §III.1 `BASE-WEB-ADAPT` 以根層 `.env*` 涵蓋、**不另開軌道**；modal 治理需求隨其頁面接線軌道之用途承載、**不另開專屬軌道**（承 rev5 處置）。
3. 新增型 `NAME+` 標記**不入名冊**（承 rev5:ADR 0021 款 1）——名冊斷言（軌道×用途×檔三元組授權判定）的射程僅修改型（帶 `原行:`）；★範圍欄之處數與塊數則**全數入機器對賬**：修改型 `原行:` 數逐軌道×用途×檔、新增型圈界形塊數逐檔加總（量法同宣告 1），與範圍欄注記不等即紅；範圍欄明文「不預估」或標「預估」之項不入對賬、至其實數化時納入（新增型逐檔加總含此類項者，該檔之新增型塊數不入對賬；修改型仍逐軌道×用途×檔對賬，標「不預估」或「預估」之三元組除外）。

**承襲指針**：rev5 憲法 v1.10.0（唯讀、凍結 SHA `7eab28a`）§III.2 曾授權五條 ★ 軌道十七用途（`BASE-WEB-AUTH-WIRING` 三用途／`BASE-WEB-LOGIN-CAPTCHA-WIRING` 二用途／`BASE-WEB-I18N-WIRING` 三用途／`BASE-WEB-LOGOUT-UX-WIRING` 一用途／`BASE-WEB-MANAGE-PAGE-WIRING` 八用途），連同 §III.1 三軌道＝rev5 名冊八條；對應接線需求出現時為 Amendment 提案的直接輸入——base-web 基線與 rev5 同 SHA，範圍欄可逐檔對照，但用途集隨 rev6 刀序重定、不整表照搬。

---

## IV. Compliance Check（spec-kit `/speckit-plan` 用）

`/speckit-plan` 必須對照本 constitution 逐項 yes/no：

1. **此 plan 是否違反 §I.1 base-web 為權威紀律？** rust-api 是否未提供 base-web 用到的對應 endpoint？
2. **此 plan 是否動到 base-web inline？** 若是、屬 §III.2 哪個用途／範圍？授權邊界內？是否依 fork-delta 紀律（修改型原行註解／新增型圈界、`rev6-inline` token）？
3. **此 plan 涉及 menu 顯示是否走 Casbin enforce？**（§I.2；demo menu 是否進 seed 而非隱藏？）
4. **此 plan 的 wire 設計是否對齊 §I.3 權威序與不變式？**（envelope／逐欄位 id 型／13 碼矩陣／msg=key；mock 僅補充 fixture）
5. **此 plan 是否從前代 source 拷貝 code？** 若是、屬 §I.5 例外清單嗎？參照處（§I.5 前代＝rev5、rev4 溯源）是否觸發防回歸條款？
6. **此 plan 是否抵觸 §II 拍板？** 任一拍板需改變、必先走 Amendment
7. **此 plan 是否觸及 §III ★ 軌道？** 若是、在授權邊界內？屬「補完」還是「新能力」（§III.2 判準）？
8. **此 plan 是否新建業務表（create migration）？** 若是，是否含 §I.6 六審計欄（建表即帶、無 retrofit）？append-only／join 表是否依變體處理？
9. **此 plan 是否觸及 §I.7 已入憲的行為島？** 若是、各 invariants 是否保持？是否用 state-machine 鏡頭設計（非 CRUD 格子）？若屬「該入憲而未入憲」的新行為島、是否隨本刀排入 Amendment（候選來源＝§I.7 承襲指針）？

任一檢查不通過 → plan 須回 brainstorm 或申請 Amendment（§V.2）。

註：本題組承接 rev5 九題制；「不增列 push/merge 自查題」為已封案事項、日後不再議——該紀律之方向性條款＝§I.8、程序承載＝CLAUDE.md 硬禁令＋agent prompt 烤入。

---

## V. Governance

### V.1 凍結權威性

本 constitution 為 rev6 的**凍結權威**；與其他文件衝突時**以本檔為準**。文件權威鏈：

> constitution（凍結權威）＞ ADR accepted（拍板全文；索引＝docs/generated/DECISIONS-INDEX.md）＞ docs/ops/RULES.md（規則層）＞ 活書家族 docs/arc42（不含 decisions/）／docs/c4／docs/compliance／docs/process（as-built 敘事）＞ docs/generated/（機器鏡像）

本檔與 accepted ADR 不一致＝Amendment 未同步的程序錯誤，以本檔為準並立即補同步。RULES.md 與 accepted ADR 衝突＝RULES 有誤、就地改 RULES（輕量軌）。

### V.2 Amendment 流程

1. **提案**：立 ADR draft（背景／決定／後果；註明改本檔哪一節）
2. **討論**：user 親決（本檔內容皆為 user 拍板項，Claude 不主動 amend）
3. **凍結**：ADR 轉 accepted＋更新本檔對應段＋bump version（§V.3）
4. **commit**：獨立 commit `docs(constitution): amend <條目>`（憲法改動＋ADR 同 commit）＋`python3 tools/docsync generate`

### V.3 Version 規則

- **MAJOR**（2.0.0）：鐵紀律（§I 原則、含 §I.8 方向性反轉）改變、§I.7 方向性不變式反轉、§II 拍板撤回、★ 軌道授權撤銷
- **MINOR**（1.1.0）：新拍板固化（§II 加項）、軌道授權邊界擴展（新用途／新範圍）、新增 ★ 軌道、**行為島隨刀進場（§I.7 填充）**、已入憲 invariant 細項調整、§I 例外清單擴展（規則方向不變、只擴例外）
- **PATCH**（1.0.1）：文字校正、釐清、reference 更新、Compliance Check 增補

---

**Version**: 1.9.0 | **Ratified**: 2026-09-03 | **Last Amended**: 2026-10-23

**Amendment log**:
- 1.0.0（2026-09-03）：創世初版——自 rev5 constitution v1.10.0（凍結 SHA `7eab28a`）依啟動書 §3.8 逐條表搬入：§I.1～§I.3、§I.6 承襲改字（分支名、基線 SHA、fork 標記 token、前代 ADR 引用一律 `rev5:` 前綴）；§I.4 收為方向性四句、程序細節移 RULES.md；§I.5 世代 bump（前代＝rev5、rev4 溯源、源倉 main `32c5254` 起全新寫）；§I.7 僅搬進場規則、十座行為島以承襲指針表列（rev5 入憲載體逐島註明）、島體隨刀重新進場；§I.8 新增（AI 代理產物必經人審與機器閘、review 只讀、push／merge 需 user 明確同意）；§II 三筆承襲（逐筆核 rev5 ADR 摘要無翻案）；§III fork-delta 紀律與 §III.1 三軌道承襲（token `rev6-inline`、wrapper 前綴 `rev6-`）、§III.2 僅機制骨架＋補完判準＋表外三項宣告＋空表頭、rev5 五條 ★ 軌道十七用途以承襲指針列名；§IV 九題承襲（第 2 題 token、第 5 題前代改引）；§V.1 權威鏈納 RULES.md、§V.2 第 4 步改 `python3 tools/docsync generate`、§V.3 MAJOR 款納 §I.8。user 親審 diff＋grill 三題親決（§I.4 錨定「刀」＝spec-kit feature、§I.8 人審＝merge 同意＋拍板親決、§III.2 宣告 2 改原則句）後定版（創世拍板）。ADR-00003 同 commit 轉 accepted。
- 1.1.0（2026-09-04）：§I.5 例外清單加②資料形狀契約三件整檔拷貝（基線結構 migration＋基線 seed migration＋基線 entity 15 檔；射程鎖 rev5 rust-api `92919b9`；程式逐位元自證、檔名四碼＝ADR-00008、註解語意判準、防回歸照常、`m0003` 起不適用）；§V.3 MINOR 款補「§I 例外清單擴展」釋義。ADR-00009 同 commit accepted（user 拍板：例外射程 2026-09-03、版級 MINOR 與註解語意判準 2026-09-04、Amendment 全文核准 2026-09-04）。
- 1.2.0（2026-09-07）：獨立輪 000-r2 三筆同批 Amendment——①§I.5 例外① 射程補「含註解」、豁免第 3 款（ADR-00022；自證腿 `vendored-check` 去註解口徑就此有權威來源；例外② 之「註解依語意判準重寫」不變）②§I.3 四保留碼「從不發出」之機器承載點自「contract test 斷言」改記為「型別層全變體窮舉＋`error.rs` 矩陣斷言雙錨」（ADR-00023；as-built 對齊、零行為變更）③§III 生成檔紀律判準句去除對空表 §III.2 的死引用、改為「與路由外掛（elegant-router）重算產出之檔同族；具體檔集隨相關 ★ 軌道 Amendment 落表」（ADR-00024）。版本取三者最高級別＝MINOR（①屬 §I 例外清單射程擴展；②③為 PATCH 級釐清）。三支 ADR 與本次憲法改動同 commit（§V.2 步 4）；user 停點① 逐題親決 2026-09-07。
- 1.3.0（2026-09-08）：003-auth-session 首刀 Amendment（ADR-00026）——①§III.2 空表落入首批四條 ★ 軌道八用途（`BASE-WEB-AUTH-WIRING` (a)(b)(c)／`BASE-WEB-LOGIN-CAPTCHA-WIRING` (i)／`BASE-WEB-I18N-WIRING` (i)(ii)(iii)／`BASE-WEB-LOGOUT-UX-WIRING` (i)；12 支 base-web 既有檔取得修改型授權、(ii) 類三項明文不授權；哨兵句同批移除、`tools/fork-delta-lint.py` 名冊自此七名）②§I.7 首批五座行為島 A～E 入憲（rev5 v1.3.0 字面為底、rev6 增補四處＝島 B 不追溯、島 E 矛盾組合方向、跨島總則、MAJOR 射程確認；承襲指針表 A～E 列尾註）③§I.2 第三點 PATCH 級釐清（「builtin 三頁」→「builtin 常量集、現五條」）。版本取最高級別＝MINOR（§V.3「新增 ★ 軌道」與「行為島隨刀進場」兩款）。ADR-00026 同 commit accepted（§V.2 步 4）；user 親決 2026-09-08（003 刀 tasks T001）。
- 1.4.0（2026-09-15）：004-ip-trust-anchor Amendment（ADR-00034）——①§I.7 島 F（IP 存取閘＋信任錨＋來源維節流）八條 F1～F8 入憲（rev5 v1.10.0 終態字面為底、rev6 座標改寫）＋島 E 四處細項調整（判定面每次由 PG 定案、拔除 redis L1 負快取＝BL-00066；設定壞值判準補不可解析／越界且整組退、兩維獨立告警；來源維計數下界恆兩源；解鎖標記讀取故障 fail-closed）；承襲指針表 F 列尾註、MAJOR 射程改六島 ②§III.2 新增 `BASE-WEB-MANAGE-PAGE-WIRING` (i)（7 支既有檔：兩語 locale route／page 兩樹新增型、`app.d.ts` page 型節、路由外掛產物四檔採產物檔紀律、不要求逐行標記；解鎖按鈕明文不授權；`tools/fork-delta-lint.py` 名冊自此八名）、`BASE-WEB-I18N-WIRING` (ii) 譯文權威句改三檔 backend 子樹各為該語之家、(i) 範圍 2＋2 並補帶信封 HTTP 層錯誤句、五列範圍欄處數實數化（BL-00058 之 (iii) 改 1 塊新增型）、表外宣告 1 改以標記實數為準。版本取最高級別＝MINOR（§V.3「行為島隨刀進場」「已入憲 invariant 細項調整」「新增 ★ 軌道」「軌道授權邊界擴展」四款）。ADR-00034 同 commit accepted（§V.2 步 4）；user 親決 2026-09-15（004 刀 tasks T001；I18N (ii) 之程序備忘子句不入憲法、只留 ADR）。
- 1.5.0（2026-09-24）：005-role-menu-crud Amendment（ADR-00042）——①§I.7 島 H（選單域生命週期）五條 H1～H5 入憲（rev5 v1.7.0 字面為底；rev6 增補兩處＝H3 受保護選單不可停用／不可改父、H2 同步失敗保留上一份之方向句；明文化三處＝H3 常量父鏈之寫端列舉、H4 兩域消費面補列、H5 常量標的之父鏈重驗；座標改寫依 ADR-00042 差異附表）；承襲指針表 H 列尾註、MAJOR 射程改七島；跨島重審結論＝跨島註與跨島總則不動 ②島 E 末尾補兩點（解鎖端點稽核先於標記；操作者上下文缺席或其來源位址取不到即拒寫 `5000`；BL-00098；前代位置 rev5 島 J5）③§III.2 新增 `BASE-WEB-MANAGE-PAGE-WIRING` (ii)（九檔：role 三、menu 兩、共用表頭元件、兩語 locale `page:` 樹、`app.d.ts` `Schema.page`；兩顆授權彈窗與 `shared.ts` 明文不入）④表外宣告 1 量法句（圈界形塊數；不預估／預估列得延至下次 Amendment 實數化並登記回填；BL-00118；既有各列範圍欄數字現算覆核相符）⑤§I.7 段首括號句改指 Amendment log（BL-00119）。版本取最高級別＝MINOR（§V.3「行為島隨刀進場」「軌道授權邊界擴展」「已入憲 invariant 細項調整」三款）。ADR-00042 同 commit accepted（§V.2 步 4）；user 親決 2026-09-24（005 刀 tasks T002）。
- 1.5.1（2026-09-27）：005-role-menu-crud PATCH Amendment（ADR-00048）——§III.2 ★`BASE-WEB-AUTH-WIRING` (c) 列範圍欄 `src/hooks/business/captcha.ts` 修改型處數 3→5：`tools/fork-delta-lint.py` 之 `find_missing` 自集合判定改逐值比次數（非唯一基線行被刪改其一亦須帶 `原行:`）後，揭出該檔自 003 刀起即缺錄之兩處刪改（Promise 閉合行 `});`、移入圈界塊內條件式之 `start();`），補修改型註解標記（碼行零改）；依表外宣告 1 範圍欄實數化。用途、行為描述、檔級名單不變。版本取 §V.3 PATCH（文字校正）。ADR-00048 同 commit accepted（§V.2 步 4）；user 親決 2026-09-27（005 刀 U13b）。
- 1.5.2（2026-09-28）：005-role-menu-crud PATCH Amendment（ADR-00051）——§III.2 ★`BASE-WEB-MANAGE-PAGE-WIRING` (ii) 列範圍欄六支 view／元件檔「不預估」實數化（兌現 ADR-00042 翻案觸發器之回填義務；final holistic review 揭出 1.5.1 未處理）：`role/index.vue` 6＋2、`role-operate-drawer.vue` 6＋4、`role-search.vue` 1＋1、`menu/index.vue` 16＋7、`menu-operate-modal.vue` 16＋6、`table-header-operation.vue` 3＋1（修改型處數＋圈界形塊數；以 final review 修正後現算為準）；用途、行為描述、檔級名單不變。
- 1.6.0（2026-09-30）：maint-tz-utc Amendment（ADR-00060）——§I.6「型與約束」加「時間點欄通則」款：表示瞬間之欄一律 `timestamptz`、不限審計欄，禁 `timestamp without time zone`；純日曆日期得用 `date`、須該刀 spec 具名理由；機器守衛＝`tools/schema-gate.py check` 全庫時間欄型別斷言（user 2026-09-30 裁定：寫成規則並擴大檢查、落點本節）。
- 1.7.0（2026-10-02）：006-authz-governance Amendment（ADR-00063）——①§I.7 島 G（casbin 授權治理）六條 G1～G6 入憲（rev5 v1.10.0 字面為底、rev6 座標改寫依 ADR-00063 決定一附表；G6＝ADR-00064；G1 前半／G3／G4／G5 之行為自 ADR-00044 決定 3 轉正、該 ADR 不被 supersede；停用雙護欄不轉正）；承襲指針表 G 列尾註、MAJOR 射程改八島；跨島重審結論＝跨島註與跨島總則不動 ②島 H 連動（序言凍結位句改對偶句、H1 終態成員括號改寫、判定面同步失敗方向與已知降級窗兩類移至島 G1、H2 以指針互引並保留本島後果句）③§III.2 新增 `BASE-WEB-MANAGE-PAGE-WIRING` (iii)(iv)（(iii)＝兩顆授權彈窗＋角色抽屜同檔雙用途＋兩語 locale `page:` 樹＋`app.d.ts`；(iv)＝兩語 locale `route:`／`page:` 兩樹＋`app.d.ts`、產物四檔授權沿 (i) 列；範圍欄以預估值填列、收刀前 PATCH 實數化）＋(ii) 列兩彈窗句同顆改寫④§III 修改型補 Vue 模板屬性行變體句（BL-00135）⑤表外宣告 3 範圍欄處數與塊數入機器對賬（BL-00132）。版本取最高級別＝MINOR（§V.3「行為島隨刀進場」「軌道授權邊界擴展」「已入憲 invariant 細項調整」三款——後者＝H2 記兩窗與表外宣告 3 入機器對賬；島 H 序言與 H1 括號、§III 變體句、(ii) 列一句＝PATCH 級隨批、不另 bump）。ADR-00063 同 commit accepted（§V.2 步 4）；user 親決 2026-10-02（006 刀 tasks T002）。
- 1.7.1（2026-10-04）：006-authz-governance PATCH Amendment（ADR-00072）——§III.2 ★`BASE-WEB-MANAGE-PAGE-WIRING` (iii)(iv) 兩列範圍欄預估值實數化（兌現 ADR-00063 翻案觸發器第三條之回填義務；表外宣告 1 例外路徑）：(iii)＝`menu-auth-modal.vue` 14＋6（預估 7 塊；差一塊＝首頁讀之世代丟棄與修改型同處一個變更塊、圈界不承重，改由該處修改型標記涵蓋）、`button-auth-modal.vue` 23＋3、`role-operate-drawer.vue` 3 塊（本用途不帶修改型）、兩語 locale 各 1 塊、`app.d.ts` 1 塊；(iv)＝兩語 locale 各 2 塊、`app.d.ts` 1 塊（修改型處數＋圈界形塊數；逐用途現算）；用途、行為描述、紀律欄與檔級名單不變。表外宣告 3 對賬腿自動納入兩列（修改型三元組對賬 24→33、新增型逐檔對賬 14→20）。user 2026-10-04 親決（006 刀 tasks T082）。
- 1.8.0（2026-10-06）：007-user-password-admin Amendment（ADR-00074）——①§I.7 島 I（使用者域治理）六條 I1～I5、I7 入憲（I6 刻意空缺；rev5 v1.10.0 字面為底、rev6 座標改寫依 ADR-00074 決定一附表）；跨島註補句（島 I5 政策鍵矛盾組合＝設密全拒、與島 E 整組退常數方向相反之理由）、跨島總則補例（密碼政策鍵與設密冷卻秒數於每次設密）；承襲指針表 I 列尾註、MAJOR 射程改九島；跨島重審結論＝I6 隨島 I 標頭處置、J2 待島 J 進場重審，改密節流載體不可用與島 E 同向，島 G5 ★句轉非 vacuous，G2／G6 與 I7 正交 ②島 B 第三點用語正名（頂替；「踢除」專指管理員結束他人全部會話）、島 C 第三點擴列第三 reason `admin_kick`、島 H2 補句（選單編輯移除尚有受保護授權列之按鈕代碼＝整筆拒） ③§III.2 新增 `BASE-WEB-MANAGE-PAGE-WIRING` (v)～(viii)（(v) 使用者管理頁接真、(vi) 個人中心改密卡、(vii) IP 規則頁來源 IP 解鎖入口、(viii) 角色頁與選單頁按鈕碼顯隱）與 `BASE-WEB-LOGIN-CAPTCHA-WIRING` (ii)（登入表單規則放寬；(i) 延後句同批刪）；`BASE-WEB-I18N-WIRING` (i) 改寫（錯誤明細轉譯只限兩鍵）、(iii) 改寫（Schema 型節與繁中 runtime）；MANAGE (i) 解鎖句與 (iii) 門在頁級句各改寫一句；表內「兩語」八處改寫（鍵集句四處改三語、指稱句四處改 `en-us`／`zh-cn` 兩檔明寫）；新列與改寫列範圍欄以預估值填列、收刀前 PATCH 實數化。版本取最高級別＝MINOR（§V.3「行為島隨刀進場」「軌道授權邊界擴展」「已入憲 invariant 細項調整」三款——後者＝島 C 第三 reason、H2 補句、鍵集句改三語；島 B 用語、MANAGE (i)(iii) 各一句、指稱句改兩檔明寫、跨島總則補例、承襲指針尾註、MAJOR 射程計數＝PATCH 級隨批、不另 bump）。ADR-00074 同 commit accepted（§V.2 步 4）；user 親決 2026-10-06（007 刀 tasks T002）。
- 1.8.1（2026-10-15）：007-user-password-admin PATCH Amendment（ADR-00092）——§III.2 本刀七列範圍欄預估值實數化（兌現 ADR-00074 翻案觸發器第三條之回填義務；表外宣告 1 例外路徑；逐用途現算 25 項：17 項＝預估、8 項不等）：`BASE-WEB-LOGIN-CAPTCHA-WIRING` (ii)＝`pwd-login.vue` 3 處；`BASE-WEB-I18N-WIRING` (i)＝兩語 locale 各 1 塊、`app.d.ts` 1 塊，理由欄 helper 記法改 `translateBackendMsg(msg, detail?)`（碼面簽章；實義不變）；(iii)＝`app.d.ts` 1＋1、`locale.ts` 0 塊、`naive.ts` 0 塊、`dayjs.ts` 2 處、`locales/index.ts` 1 處、`store/modules/app/index.ts` 2 處；`BASE-WEB-MANAGE-PAGE-WIRING` (v)＝`user/index.vue` 13＋8（預估 16＋9）、`user-operate-drawer.vue` 23＋12（預估 22＋16）、`user-search.vue` 4 處（預估 2；規則來源之匯入與取用行連帶改寫）、兩語 locale 各 2 塊與 `app.d.ts` 2 塊（預估各 3）；(vi)＝`user-center/index.vue` 2＋1、兩語 locale 各 1 塊、`app.d.ts` 1 塊；(vii)＝兩語 locale 各 1 塊、`app.d.ts` 1 塊；(viii)＝`role/index.vue` 2 處修改型＋2 塊新增型、`menu/index.vue` 1 處修改型＋2 塊新增型（預估各 3 處修改型；兩檔以新增型塊承載按鈕碼判準來源之匯入與逐鈕顯隱之計算旗標，選單頁表頭兩 prop 另落於 (ii) 既有標記行）。各列用途、行為描述、紀律欄與檔級名單不變。版本級＝PATCH（§V.3；實數化不擴授權邊界，前例 1.5.1／1.5.2／1.7.1）；對賬腿：修改型三元組對賬 32→57、跳過 25→0，新增型逐檔對賬 14→29、跳過 15→0。ADR-00092 同 commit accepted（§V.2 步 4）；user 親決 2026-10-15（007 刀 tasks T104；十二題皆取建議項）。
- 1.9.0（2026-10-23）：008-audit-settings-pages Amendment（ADR-00099）——①§I.7 島 J（稽核域 retention 與 reporting）五條 J1～J5 入憲（rev5 v1.10.0 字面為底；J2 以 rev4 島 J2 字面為底回填〔rev5 J2 位刻意空缺〕、J5 為指向島 E 末兩點之指針；差異申報見島 J 標頭）＋島末常數句；承襲指針表 J 列尾註、MAJOR 射程改十島；表尾句改述（刻意空缺位只餘 I6、其處置見島 I 標頭；跨島刻意不一致之重審改於日後新行為島進場時）；跨島重審結論＝跨島註與跨島總則不動、J2 與島 E 末點及島 F 之 F3①「取不到來源位址即拒寫」方向相反之理由住 J2 字面（兌現 1.8.0「J2 待島 J 進場重審」）②§I.6 變體 B 括號句由預告句改為島 J3 交叉指針 ③§III.2 新增 `BASE-WEB-MANAGE-PAGE-WIRING` (ix)（系統設定頁進場）與 (x)（稽核頁進場），範圍欄以預估值填列、收刀前 PATCH 實數化；`BASE-WEB-I18N-WIRING` (i) 紀律欄改寫（錯誤明細轉譯恰三鍵、末句改指 ADR-00102；範圍欄不動）。版本取最高級別＝MINOR（§V.3「行為島隨刀進場」「軌道授權邊界擴展」兩款；§I.6 括號句、MAJOR 射程計數、表尾句、承襲指針尾註＝PATCH 級隨批、不另 bump）。ADR-00099 同 commit accepted（§V.2 步 4）；user 親決＝2026-10-21（plan 期條文逐款）與 2026-10-23（008 刀 tasks T003：銜接字面與重問）。
