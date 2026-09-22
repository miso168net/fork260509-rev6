# 005-role-menu-crud — role＋menu 管理 CRUD 寫端 brainstorm（階段 0）

- 日期：2026-09-22｜狀態：範圍與 BACKLOG 承載五題（Q1～Q5）＋設計三段十節已過 user 核可；同日 grill-with-docs 輪（G1～G4：以 BACKLOG 分類體檢為主核本刀是否把可處理項納全）已收斂、共識經 user 確認、本檔修訂另顆落地；下一步＝**手動** `/speckit-specify`（本檔為其 input；不自動觸發——否則 before_specify hook 不跑、分支不建、spec 落 default）。
- 一句話：把 upstream 的角色頁與選單頁自 demo 殼接成真——17 支端點（role CRUD 6＋menu CRUD 7＋roleHome 2＋getMenuTree＋getAllPages；ROUTES 22→39、GET 7／POST 6／DELETE 4）、前後端同刀、CDP 對照 rev5 22080；同刀落地 006 要消費的三件底座（選單域 advisory 序列化域、casbin rebuild-swap 判定面同步、授權歸檔寫入面＋reason gate）；憲法一次 MINOR 1.4.0→1.5.0（島 H 五條入憲＋§III.2 用途 (ii)＋BL-00098／BL-00118／BL-00119 三條併入）。
- 交付價值：超管首次能真的建角色、建選單、刪選單並確定被刪選單的授權在判定面立即失效（不是等重啟）；006 三維授權治理的資料軸心（角色、選單、按鈕碼聯集）與三件底座就位、屆時純消費；BACKLOG 開放 41 條中 19 條隨本刀收、目標零新 BL（已知態一律走 ADR）。

> 輸入：`docs/ops/NOTES.md` 下一步（005 條）、憲法 §I.5／§I.7（進場規則、承襲指針表 H 列、島 E 條文）／§III.2（用途 (i) 列形、表外宣告、生成檔紀律）／§IV／§V.2～§V.3、`docs/ops/BACKLOG.md` 開放 41 條與滯後卷 4 條（逐條對觸發欄）、主線 BACKLOG 分類體檢工作檔（2026-09-22 跨機交接版、gitignored、不入帳；桶 B 十一條＋收刀前體檢清單為本檔 §2 底稿、grill 輪以之為主核）、ADR-00014／ADR-00015／ADR-00026／ADR-00034／ADR-00039／ADR-00040／ADR-00041、`deploy/grafana-provisioning/alerting/rules.yml`（casbin-reload 規則錨）、rev6 碼面現況（`envelope.rs` 之 `PageRes`、`handler/common.rs` 兩件、`auth/enforce.rs` 終態句、`facade/sys_ip_rule.rs` 之 ILIKE、`m0002` 政策列、entity 四表欄集、`tests/wire_schema.rs` 十二 definition、`tests/common` 四支守衛）、rev5 `rev5:005-role-menu-crud` 全套（brainstorm／spec／plan／research／data-model／contracts／tasks；`rev5:ADR 0048`～`rev5:ADR 0052`、`rev5:ADR 0060`）與其收刀後動本域檔之 commit（rust：`rev5:f841b04`／`rev5:47e8a67`／`rev5:c0067ae`／`rev5:55bb3e3`／`rev5:6ee82e2`／`rev5:e02251d`；base-web：`rev5:1597a671`／`rev5:ae1ac0c9`／`rev5:854a72ee`／`rev5:84f283c7`；唯讀、凍結 SHA 外層 7eab28a／base-web 9833308／rust-api 92919b9）。

## 0. 拍板紀錄（全數 user 拍板 2026-09-22、一題一問；首選項皆為建議）

| 題 | 拍定 | 要點 |
|---|---|---|
| Q1 刀範圍 | **承 rev5 拆刀形全射程；BACKLOG 能收的條目逐條列入** | rev5 沿 α 縫（grant／revoke 寫 casbin_rule）把「刀 A＝role＋menu」拆成 005（CRUD 面）與 006（grant 面）；rev6 承其射程＝16 支端點＋三底座＋島 H 入憲＋前端兩頁接真（兩顆授權 modal 一行不動）。已核實零 migration 零 seed 成立：16 支端點 seed 政策列全在（12～16／21～25／27～31／34／35／64／65，後兩列 protected）、`sys_role.role_memo`／`sys_menu.menu_memo` 欄在、`casbin_rule` 治理三欄與 `sys_casbin_policy_archive` 14 欄在、casbin 釘 2.20.0（與 rev5 同版）。user 另令：本檔必列「BACKLOG 哪些條目隨本刀收」（§2）。棄案：底座推 006（deleteMenu 後判定面殘留舊授權直到重啟＝島 H2 帶已知違憲窗入憲，`rev5:005` grilling G1 已否決）；005＋006 合一刀（約 27 支、兩島同次入憲、rev5 已判太大） |
| Q2 getAllPages | **併入 005（17 支、ROUTES 22→39）** | upstream 選單 modal 的「頁面」下拉靠 `GET /systemManage/getAllPages`；rev5 005 歸 006 支撐讀、期間 modal 開啟即打 404 被靜默吞（`pages \|\| []`）、下拉只剩自身 routeName（upstream 自動補進）。rev5 006 實作＝顯示域 route_name 全集依 `(order, id)` 排序、約 20 行、零 grant 面；seed 26 政策列（R_SUPER、GET）已在。棄案：照 rev5 留 006＝列已知態、CDP 對照排除 |
| Q3 分頁 `current` 逾界語意（BL-00116） | **clamp 入契約與活書**（維持 as-built） | 004 的 IP 規則清單端點對 `current` 加了契約未宣告的上界 clamp（10^7、擋 OFFSET 溢位）；005 帶三個新分頁端點、此規則須一次定成跨端點慣例。定案：current clamp [1, 10^7]、逾界回空頁且回應 `current`＝上界值；分頁參數收斂抽成 `envelope` 層共用 helper、四端點同用一份常數（IP 規則清單端點一併改引＝機械改、既有測試釘住）；規則寫進活書 08 §8.2 API 慣例＋各端點契約＋contract test 逐端點一案；零錯誤集變動、零前端改動。棄案：逾界回業務錯誤 2222（動 MSG_KEYS 與三檔 locale、四端點 contract 改形、前端跳 toast） |
| Q4 未知 `wbip_type` 上 wire（BL-00095） | **won't-fix ADR＋前端小守** | Q3 改引共用 helper 動到 `handler::ip_rule` 清單端點可執行碼＝BL-00095 依「動 X」定義到期。定案：未知類型只能源自直改庫（非支援路徑），後端清單照原樣上 wire（不過濾、不改契約與快照），前端 ip-rule 頁對映射取不到的值退回顯原字串（一行守；該頁為 rev6 新檔、零授權成本），存取閘既有 skip＋告警不變；立 by-design 決定（ADR 形由 G1 定）、收刀 `backlog_done`。棄案：清單端過濾＋告警（管理員看不到也刪不掉、total 語意另定）；DTO 加 `unknown` 表示法（動 004 契約快照、typings、前端映射三面） |
| Q5 表頭插槽形（BL-00117） | **共用元件加 prop、兩頁改用** | 共用元件 `TableHeaderOperation` 的 default 插槽覆寫成空時 Vue 改渲染自帶備援鈕（新增＋批刪）、無權者反而看到寫入口；rev5 解法＝外層 `v-show`＋內層 `v-if` 疊寫（menu 頁 005 即用、ip-rule 頁 `rev5:B-099` 006 補），只靠碼註守。定案：`src/components/advanced/table-header-operation.vue` 附加 `showAdd?`／`showDelete?` 兩 prop（預設 true、既有呼叫端零行為變化＝憲法 §III.2「附加 prop＋安全預設」紀律），menu 頁與 ip-rule 頁改傳 prop、不再覆寫 default 插槽，備援鈕陷阱結構性消失 ⇒ BL-00117 收。代價＝用途 (ii) 名單多一支共用元件（約 2 處修改型）、upstream rebase 多一個衝突面；UI 零差異。棄案：照抄疊寫＋碼註（不變式仍零機器守）；疊寫＋view-render-guard 補腿（綁模板字面的脆弱 lint） |

**grill 輪拍板紀錄（user 2026-09-22 發起 grill-with-docs：以 BACKLOG 分類體檢為主核本刀是否把可處理項納全；一輪 frontier 四題；首選項皆為建議）**

| 題 | 拍定 | 要點 |
|---|---|---|
| G1 BL-00095 之 ADR 形 | **新 ADR supersede ADR-00040** | ADR-00040（IP 域已知態、六款）已 accepted 不可改，BL-00125（款 2 dev 二態實為三態）與 BL-00120（零 rev5 出處）皆為其對沖、觸發皆＝下一支翻案該 ADR 之刀；005 恰要立同一面的 by-design 決定。定案：新檔 `supersedes: [ADR-00040]`、六款重述（款 2 改三態；款 6 對齊 as-built 並以 BL-00105 六型鍵集斷言兌現）＋新款「清單端點未知 `wbip_type` 照原樣上 wire、前端退顯原字串」＋frontmatter 補 rev5 出處；RUNBOOK §16.1／活書 06 島 F ⑧／活書 11 三處鏡像字面同批改三態。收 BL-00095＋BL-00125；BL-00120 改條文只剩 ADR-00039 半（ADR-00039 不為補出處單獨翻案）；ADR 總數 4→5。棄案：併入 005 已知態 ADR 一款（IP 域已知態散住兩支）；獨立單款 won't-fix ADR（三支 IP 域已知態分散） |
| G2 BL-00082 連帶到期 | **納入：boot 體檢＋案** | BL-00082 觸發＝「修改 `config::load_trust_model` 或信任模型契約」；005 體檢單元收 BL-00115 時刪 `docs/ops/reference-src/trust-model-config.md` 手抄 toml 區塊＝字面上修改信任模型契約。定案：`config::load_trust_model` 載入時驗 `connecting_ip_header` 為合法 HTTP 標頭名，非法→結構化告警（附改寫建議）且該標頭視為缺席（與「單集合壞只清該集合」同形、只縮小信任）；一正一反案；約 30 行；其 quickstart grep 殘留屬凍結史料不動。user 2026-09-21 對維護批之「不納入」裁定屬彼時脈絡、刀內連帶到期即收。棄案：改條文註「刪鏡像區塊非契約語意變更、不視為到期」 |
| G3 ILIKE 共用件射程（BL-00096） | **收攏三份含 `sys_ip_rule`、順收 BL-00096** | rev6 `facade/sys_ip_rule.rs` 自持一份轉義 ILIKE，005 getRoleList 之 roleName／roleCode 模糊搜尋為第二份；rev5 至 007 第三份（sys_user）才以 `rev5:B-138` 收攏。定案：`facade/mod.rs::ilike_contains` 單一源（轉義 `%`／`_`／`\`）、sys_role 與 sys_ip_rule 改引；改引動到 `sys_ip_rule` facade 可執行碼 ⇒ BL-00096 到期並同批收（四寫端與 `find_by_id_for_update` 改具型簽章 `&DatabaseTransaction`、production 兩呼叫點已傳交易＝機械改、該檔測試約三十處裸連線呼叫者改自開交易）。user 2026-09-21 對維護批之「不納入」裁定理由（005 不動 sys_ip_rule）自此不成立。棄案：兩份並存、BL-00096 條文補「到期時同批收攏 ILIKE 三份」 |
| G4 BL-00111 立腿 | **體檢單元立腿、收 BL-00111** | 全樹十二支掃描腿「切到第一道行首 `#[cfg(test)]` 為止」，失守形 (a)＝測試模組之後再宣告 top-level item（負面斷言型恆綠無聲）；005 新增多支帶測試模組的大檔、且很可能再加同形腿。定案：先 grep 既有閘確認無同形，再立一支「測試模組閉合後零 column-0 top-level item」lint（射程＝`src/**/*.rs`；**行掃描形**：行首 `#[cfg(test)]` 之後任何行首 `pub fn`／`fn`／`struct`／`enum`／`impl`／`const`／`static`／`mod`／`use`／`macro_rules!` 即紅；刻意不用 char 級解析＝不成 BL-00108 第三份）＋植入反例變異自證；失守形 (b) 已由行首形切點排除。棄案：維持「看」；不立腿只改條文 |

**既定不問（承 rev5 已驗證結論施工、報備備查；出處＝`rev5:005` brainstorm §3 十五題、grilling 六題、clarify 三題與實作期親決）**

1. 拆刀縫 α、島 H→005、島 G→006、島 I→007（`rev5:005` #1）；前後端同刀（#2）。
2. deleteRole／batchDeleteRole 入選單序列化域（#8）；歸檔表三自由度全不動（#10）；`constant` 可寫＋父鏈常量性守門（#11）＋restoreMenu 第四腿常量父鏈重驗（`rev5:ADR 0051`、`rev5:B-095`）。
3. restore 鈕不按鈕碼 gating（#12）；回收桶 toggle 形（#13）；static meta 不維護、DB 唯一真源（#14）。
4. 判定面同步基建在 005、006 純消費（G1；rev5 稱「熱重載」）；新建／復原選單於 006 前無法授予可見性＝已知態（G2）；前端修改型檔清單照實拆列、兩顆授權 modal 一行不動（G3）；getMenuTree 在 005（G4）；memo 兩欄兌現、列表不濾受眾（G5）；in-use／self-role 兩腿生產面窗接受（G6）。
5. 絕版判定聯集域＝未刪含停用（clarify Q1）；addMenu 同鍵雙層守門（Q2）；getAllRoles 零 UI 消費者照交付（Q3）。
6. `nameRequired` 第十鍵、`multiTab` 可寫、`routeNameInvalid` 鍵（rev5 實作期 user 親決）；`AuditOperation` 零新 variant、標的表由 `entity_table` 區分（`rev5:005` T005）。
7. 治理清單分頁列凍結形（UI 位置不動、頁碼 1／每頁 0／整列上鎖、prefix 續顯真實筆數；`rev5:ADR 0060`、rev5 user 親決 2026-08-25）。
8. rev5 對 rev4 之 11 項防回歸差異（`rev5:005` research R2）照帶：restore 冪等→業務錯誤、上下文缺席→拒寫 5000、AuditOperation 小寫封閉詞彙、純 i18n key 拒因、`fetchGetAllRoles` 殘留不帶、SELF_SERVICE_ROUTES 不帶、zh-tw 不上 runtime、rev4 域鎖字面不帶、deleteRole 入域、find_by_keys 不搬、「終態」句翻案。

**工程判斷（主線自拍、報備備查；RULES 名詞段判準下非拍板級）**

1. **藍本取 rev5 HEAD 形**：005 收刀後對本域檔的修補自首版帶入——`rev5:ADR 0051`（restore 第四腿）、`rev5:ADR 0060`（分頁列凍結 UI）、RELOAD_SERIAL＋其交錯時序 harness（`rev5:B-105`、rev5 006 T020 之 `#[cfg(test)]` 注入式 seam；「先 commit 慢 rebuild 蓋回」窗機器證）、`rev5:B-098`／`rev5:B-102`（role 寫端空字串→NULL 組合面案）、`rev5:B-100`（toggle 切換清勾選）、`rev5:B-132`（menu 頁 pageSize 歸位）、`rev5:B-137`（R_SUPER 宣告單源）、`rev5:B-138`（`ilike_contains` 共用件；G3 提前至本刀收攏三份）、`rev5:c0067ae`（wire-schema 十二 definition）。剔除 006（grant 面、reason gate 五值、getAllButtons／getAllEndpoints、policy-archive、endpoint modal、三顆 modal 接真）、007（`Identity` sid、no-escalation、user 域）、008（audit）增量；逐檔剔除清單於 plan research 凍結、烤入 implementer prompt。
2. **域鎖 key 字面**＝`0x7265_7636_6D65_6E75`（ASCII `rev6menu`；rev5 對 rev4 同法換世代名）。
3. **wrapper／typings**：`service/api/rev6-role-admin.ts`（role 6＋roleHome 2）、`rev6-menu-admin.ts`（menu 7＋getMenuTree）；`typings/api/rev6-role-admin.d.ts`／`rev6-menu-admin.d.ts` 開 `Api.RoleAdmin`／`Api.MenuAdmin` 獨立命名空間（createdBy enrich 形、id number＋2^53 守衛、`deleted` 導出布林；004 慣例）；getAllPages 走 upstream barrel 既有 `fetchGetAllPages`（`system-manage.ts` 零改）。
4. **PageRes 既在 envelope**（`maint-backlog-86-90` U1 提前上移）⇒ rev5 FR-002「上移」項消；分頁 helper（current／size clamp 與預設 1／10）落同檔、`handler::ip_rule` 改引（Q3 連動 Q4）。
5. **getMenuList/v2 `size` 缺席＝回全部頂層**（treeTable 無參一次取全樹；有值 clamp [1,100]）——翻 rev5「預設 100 並 clamp」形、消掉 `rev5:B-131`（頂層 >100 列不可達）之債而不入 BL；缺席時回應 `size`＝實得頂層數、`current` 忽略回 1；UI 零差異（分頁列凍結形不變）；契約明寫、contract test 釘。
6. **BL-00109 之機器錨落 python 側**：rust-api 容器看不到 base-web 工作樹（dev compose 零 bind mount），故錨住 `tools/wire-schema.py` 加腿（讀 `base-web/packages/axios/src/options.ts` 之 `paramsSerializer` 與 qs 版本、對賬 rust 側 `FRONTEND_FIRST_SCREEN_QUERY` 之前提）＋self-test；rust 常數改為引用該前提的說明。
7. **BL-00106 收法**＝收刀體檢單元直接立泛型實例化名冊腿（rev5 `rev5:B-111` 形：`Res<i64>`／`PageRes<i64>` 實例化、手寫 `impl Serialize`、巨集生成 `Serialize` 型三形之名冊、現況零筆）＋變異自證（植入反例必紅）；不再以「三形仍零」為由延到下一刀。
8. **契約落點**：刀內契約住 `specs/005-role-menu-crud/contracts/`（`wire-role-admin.md`／`wire-menu-admin.md`／`msg-keys.md` 候選鍵表；ADR-00041 決定 6）；跨端點分頁規則（current／size clamp 與預設、逾界語意、getMenuList/v2 缺席例外）住活書 08 §8.2 API 慣例＋各端點 contract test；004 IP 契約凍結不改、其與 as-built 之差由活書句與 git 史解釋（BL-00116 收）。
9. **已知態走 ADR、目標零新 BL**：005 域已知態（role 頁「菜單權限／按鈕權限」兩鈕 demo stub、policy-archive 選單項死項〔BL-00045 已承載〕、新建／復原選單側欄不現、getAllRoles／roleHome 零 UI 消費者、治理清單分頁列凍結＋`size` 缺席全取）合一支「本刀已知態與 by-design」ADR；IP 域已知態（BL-00095 未知類型上 wire＋ADR-00040 六款重述）住 G1 之 supersede ADR。
10. **測試守衛形**＝rev6 004 G6 之水位形（無 SequenceResetGuard）：四表守衛（`sys_role`／`sys_menu`／`casbin_rule`／`sys_casbin_policy_archive` 皆不在 `RUNTIME_APPEND_TABLES`＝gate2 逐列比對＋序列 setval 期望）＝只刮自寫列＋setval 還原 `sys_role_id_seq=(3,true)`／`sys_menu_id_seq=(78,true)`／`casbin_rule_id_seq=(163,true)`／`sys_casbin_policy_archive_id_seq=(1,false)`（is_called 位正確；`rev5:005` T004 實測定案）＋守衛自證測；測試造列一律顯式大 id；`casbin_rule` 造列走真 Enforcer `add_policy`＝nextval 取 id、免 setval 路徑不成立。
11. **`handler/common.rs` 重評**（BL-00113）：第三個帶操作稽核寫端進場單元執行；`operator_from_context`／`json_or_default` 兩件簽章與「`tracing::error!` 留呼叫點」切法重評，結論落該檔 doc＋收單訊息；既有 `each_domain_keeps_its_own_log_literals` 守不得因重評併掉兩域 target。
12. **ADR 待立五支**（刀分支內落、序號接續現行最大號；draft 於 plan 期、user 親決於 tasks 首個主線任務＝003／004 前例）：①憲法 Amendment ②判定面同步 rebuild-swap（翻 002 刀 `enforce.rs`／`main.rs`「boot 載入即終態」碼內拍板；含 reload 契約、硬禁令＋casbin 2.20.0 版本鎖、RELOAD_SERIAL、ABBA 三失效條件）③A1 域行為（deleteRole 入域＋免 reload 論證＋島 G 行為 G1/G3/G4/G5 由 ADR 承載、條文隨 006 入憲＋archive 三自由度 won't-use 與 `rev4:ADR 0049` 翻案觸發條款過境）④本刀已知態與 by-design（工程判斷 9 之 005 域部分）⑤IP 域已知態 supersede ADR-00040（G1：六款重述、款 2 三態、款 6 對齊 as-built、新款未知類型上 wire、rev5 出處補齊）。
13. **components.d.ts 重算**（menu modal 引入 NTreeSelect 父選擇器）＝憲法 §III 生成檔紀律（`rev5:ADR 0052` 之條款 rev6 創世已入憲）、`tools/fork-delta-lint.py` 檔頭判準豁免；不入用途 (ii) 名單。
14. **CDP 對照排除清單**＝rev5 22080 之 006～008 增量（三顆授權 modal 接真、policy-archive 頁、endpoint-auth-modal、user 頁、audit 頁）＋已知態三組；已知態步驟一律實際操作觀察、不得以推論代替（`rev5:L-054`）。★CDP 操作一律派 `opus[1m]` xhigh agent、不得 fable（user 2026-09-20 明令）。
15. **詞彙（domain-modeling；本 repo 詞彙之家＝活書 12 系統術語、不另立 CONTEXT.md；as-built 時落）**：治理域／顯示域、序列化域、絕版（button 碼不再屬任何未刪選單之聯集）、常量父鏈、reason gate；**「選單回收桶」**（getDeletedMenus／restoreMenu 面）與**「授權回收桶」**（006 之 policy archive）分立不互用；casbin 面一律**「判定面同步」**（碼識別字維持 `reload_enforcer`）、IP 規則集沿活書既有**「熱重載」**（門鈴 `ipgate:invalidate`），兩詞不互用。
16. **getAllPages 落點**＝`handler/menu.rs`（依域：顯示域 route_name 全集屬選單域）；rev5 HEAD 住 `handler/role.rs` 係 006 U8 三支支撐讀同住之歷史、不承。
17. **BL-00082 之體檢形**（G2）：`config::load_trust_model` 對 `connecting_ip_header` 以 `http::HeaderName::from_bytes` 驗合法性；非法＝結構化告警一則（欄含原字面與改寫建議）＋該標頭視為缺席（通道回退／邊緣驗證兩覆蓋層對此設定停用）、其餘集合照載；RUNBOOK §16.2 人工核對義務句改為「boot 體檢兜底、人工核對留給 prod 首部署」。
18. **BL-00111 lint 腿形**（G4）：新 lint 檔住 `rust-api/server/tests/`、行掃描（不用 char 級解析＝不成 BL-00108 第三份）、射程 `src/**/*.rs`、判準＝行首 `#[cfg(test)]` 之後零行首 top-level item 關鍵字；植入反例變異自證；既有十二支腿之 docstring 補指本腿為其射程守。
19. **rules.yml `obs016-casbin-reload-anomaly` 錨對齊**：該規則錨在 `casbin_reload_total{outcome=~"retry|exhausted"}`，005 U3 引入該 metric 後規則即活——metric 名與 label 值集以 rules.yml 既有字面為準、`obs.rs` 預註冊三 outcome；屬 BL-00093 ②之部分兌現、該條不收（觸發＝觀測 profile 首起或存取軌跡刀）、收單訊息記載。
20. **用途 (ii) 新增型塊數**：rev5 as-built 為兩語 locale 各 4 塊（role 標籤／role memo placeholder／menu `page:` 樹補／menu memo placeholder）、`app.d.ts` 4 塊；rev6 Amendment 範圍欄一律寫「實數以標記為準」（憲法表外宣告 1）、plan 期以 fork-delta-lint 實跑取數。

## 1. rev5 承襲盤點（沿用項照已驗證結論施工、翻案項用新設計；CLAUDE.md §2）

| rev5 項目 | 處置 | rev6 落點 |
|---|---|---|
| 五個 user story（US1 角色全生命週期／US2 選單樹／US3 回收桶與復原／US4 判定面同步／US5 roleHome）與優先序 | 沿用；getAllPages 入 US2（Q2） | 本刀範圍 |
| 16 支端點契約形（`rev5:005` contracts wire-role-admin／wire-menu-admin） | 沿用其形、rev6 座標改寫（+getAllPages、`current` 上界入契約、getMenuList/v2 `size` 缺席全取） | `specs/005-role-menu-crud/contracts/` |
| 選單域 advisory 序列化域（島 H1；鎖序、txn 首動作、pg_locks 機器證兩坑） | 沿用；key 字面翻 `rev6menu` | 新 `facade/sys_casbin_archive.rs` 域鎖底座 |
| casbin rebuild-swap＋keep-last-good＋RELOAD_SERIAL（含 `rev5:B-105` 交錯時序 harness）＋觸發矩陣恰移除面三支＋deleteRole 免 reload | 沿用（HEAD 形） | `auth/enforce.rs`；ADR② |
| 授權歸檔寫入面＋reason gate（三值 `role_soft_delete`／`menu_soft_delete`／`menu_button_removed`） | 沿用；五值＝006 | `facade/sys_casbin_archive.rs` |
| role 守門矩陣（seeded→in-use→self-role；停用雙護欄；code 形制不可變；批次 no-partial；空陣列提前 no-op） | 沿用 | `facade/sys_role.rs`＋`handler/role.rs` |
| 選單狀態機五條（治理域／顯示域分層、防環、parent 三處一致、不可變錨欄、constant 父鏈、同鍵重建零繼承、child-first、復原不回灌） | 沿用；restore 第四腿自首版即入 | `facade/sys_menu.rs`＋`handler/menu.rs` |
| 治理清單分頁列凍結形（`rev5:ADR 0060`） | UI 沿用；後端 `size` 預設 100 → **翻案**缺席全取（工程判斷 5） | menu 頁＋getMenuList/v2 契約 |
| 表頭插槽疊寫（`rev5:B-099` 形） | **翻案**：共用元件 prop（Q5） | `table-header-operation.vue`＋menu／ip-rule 兩頁 |
| getAllPages 於 006 支撐讀、住 `handler/role.rs` | **翻案**：提前入 005（Q2）、依域住 `handler/menu.rs`（工程判斷 16） | `handler/menu.rs` |
| ILIKE 共用件 `ilike_contains`（`rev5:B-138` 於 007 第三份時收攏） | **提前**至 005 收攏三份含 `sys_ip_rule`（G3）、連帶 BL-00096 具型簽章 | `facade/mod.rs`＋`sys_role.rs`＋`sys_ip_rule.rs` |
| IP 域已知態載體＝單支 ADR（rev6 ADR-00040 為其對應） | **翻案**：新 ADR supersede ADR-00040（G1） | ADR⑤ |
| memo 兩欄（`role_memo`／`menu_memo`；G5） | 沿用 | 列表欄＋drawer／modal textarea |
| i18n 鍵集：`biz.role.*` 10 鍵＋`biz.menu.*` 11 鍵（含 rev5 後補 `nameRequired`／`routeNameInvalid`）＋page 樹四鍵（showDeleted／confirmRestore／restore／restoreSuccess）＋memo 標籤／placeholder 鍵 | 沿用 HEAD 鍵集 | `error.rs` MSG_KEYS 19→40；三檔 locale；`app.d.ts` |
| 譯文權威＝各刀 `contracts/msg-keys.md` | **翻案**（已由 ADR-00039 定）：三檔 locale backend 子樹各為該語之家；`msg-keys.md` 只作候選鍵表 | 三檔 locale |
| 測試守衛（rev5 005 期＝SequenceResetGuard 尚在） | **翻 rev5 005 期形、承 rev6 004 G6**：水位形＋業務表 setval 還原 | `tests/common`＋`test_kit.rs`（工程判斷 10） |
| `handler/common.rs`（rev5 005 期無此檔、`rev5:B-094` 後補八件） | rev6 既有兩件直接消費＋第三寫端重評（BL-00113） | `handler/common.rs` |
| `PageRes` 上移（`rev5:005` FR-002） | rev6 已在 envelope、項消 | — |
| 已知態三組＋getAllRoles／roleHome 零 UI 消費者窗 | 沿用；走 ADR④ | 本刀已知態 ADR |
| rev5 後刀增量（006 grant 面、reason gate 五值、getAllButtons／getAllEndpoints、policy-archive、endpoint modal、三顆 modal 接真；007 sid／no-escalation／user 域；008 audit） | 不帶 | — |
| `rev5:005` 收刀後本域修補（工程判斷 1 清單） | 沿用（HEAD 形自首版即入） | 各對應檔 |

## 2. BACKLOG 觸發項處置（動工前掃描、CLAUDE.md §2；41 開放＋4 滯後逐條對觸發欄；以 BACKLOG 現文為準）

| 分類 | 條目 | 005 的哪一步 |
|---|---|---|
| 收・拍板已定 | BL-00116 逾界 clamp 入契約與活書 08 §8.2（Q3）｜BL-00095 by-design 入 ADR⑤＋前端顯原字串（Q4、G1）｜BL-00125 ADR-00040 款 2 三態隨 ADR⑤ 重述、三處鏡像字面同批（G1）｜BL-00117 共用元件加 prop（Q5）｜BL-00082 `load_trust_model` 標頭名體檢＋案（G2）｜BL-00096 `sys_ip_rule` 四寫端具型簽章（G3、隨 ILIKE 收攏連帶）｜BL-00111 測試模組閉合 lint 腿（G4） | 004 域連帶單元（U1b）／治理面單元／前端單元／體檢單元 |
| 收・必到期 | BL-00105 六型「序列化鍵集＝快照 properties 鍵集」斷言（或具名豁免；ADR⑤ 款 6 同批對齊）｜BL-00112 `PageRes` 進受審 definition 名冊｜BL-00109 qs 序列化前提機器錨（python 側、工程判斷 6）｜BL-00113 `common.rs` 兩件重評（工程判斷 11）｜BL-00110 7777 腿 denylist 鍵 RAII（005 動 tests/common 守衛即到期；複用 `RestorePlan.keys` 腿） | wire 面單元／第三寫端單元／測試基建單元 |
| 收・Amendment 併入 | BL-00098 島 E 兩句｜BL-00118 量法句與範圍欄數字｜BL-00119 §I.7 段首增補計數句 | U0 主線 Amendment |
| 收・收刀前承載體檢單元 | BL-00106 泛型實例化名冊腿（工程判斷 7）｜BL-00107 型級解析普查案（釘錨數＝解析成功數）｜BL-00123 `request_context_absent` 每請求總數案（`with_local_recorder` 套 app 級不可行即改 serial 差值形）｜BL-00115 dev 信任模型三鏡像（契約檔 toml 區塊刪、改指交付檔；toml⇔`dev_trust_model()` 由 rust 案經 `APP_TRUST_MODEL_PATH` 對賬、env 缺席具名跳過）｜BL-00111 lint 腿（工程判斷 18） | 專用體檢單元（吃一次容器 cargo 週期、排收刀全量測試同批） |
| 改條文（不收） | BL-00120：ADR-00040 半由 ADR⑤ 補齊 rev5 出處、條文改為只剩 ADR-00039（不為補出處單獨翻案）｜BL-00093：②之 casbin-reload 規則錨對齊屬部分兌現、條文不動、收單訊息記載 | ADR⑤ 單元／U3 |
| 不觸發・反向確認入 spec | BL-00047 零建表｜BL-00028 零新設定鍵｜BL-00048 不帶 no-escalation｜BL-00074 零新 msg 字面消費點（rev5 005 前端只在碼註提及 `backend.biz.*`、`FRONTEND_MSG_CONSUMERS` 不動）｜BL-00108 零第三份 char 級解析組（BL-00111 腿取行掃描形） | spec 反向確認清單（收刀體檢時 grep 現算） |
| 射程外・Out of Scope 指承載 | 006：BL-00045（policy-archive 頁）｜007：BL-00031／BL-00065／BL-00091／BL-00124｜008：BL-00027／BL-00043／BL-00044／BL-00045（settings／audit 頁）｜000-r3 等：BL-00002／BL-00035／BL-00036／BL-00039／BL-00101／BL-00102｜觀測：BL-00084／BL-00093｜滯後卷 BL-00029／BL-00049／BL-00064／BL-00067 | spec Out of Scope 逐條指承載 |

預估：開放 41 → 22（收 19、改條文 2）；`backlog_add` 目標零（已知態走 ADR④／ADR⑤）。收刀 `backlog_done` 清單＝BL-00082／BL-00095／BL-00096／BL-00098／BL-00105／BL-00106／BL-00107／BL-00109／BL-00110／BL-00111／BL-00112／BL-00113／BL-00115／BL-00116／BL-00117／BL-00118／BL-00119／BL-00123／BL-00125。收刀若 rolling-3 淨流量仍超標，先分揭露型／新欠型再判（體檢 §7 判準）。

## 3. 設計（十節、user 已核可；grill 輪修訂已併入）

### §1 目標與範圍

**入刀**：US1 超管管理角色全生命週期（列表分頁＋名稱／代碼模糊＋狀態篩選＋memo 欄；新增／編輯／刪除／批刪；三層守門）｜US2 超管管理選單樹（treeTable 治理域、新增目錄／選單、父選擇器自 getMenuTree、頁面下拉自 getAllPages、buttons／constant 可寫、防環與父驗證、不可變錨欄、刪除連動歸檔＋判定面同步、child-first 批刪）｜US3 選單回收桶與復原（toggle 換源 getDeletedMenus、復原四腿重驗、不回灌）｜US4 刪除後殘留授權即時失效（rebuild-swap、keep-last-good、絕不全域拒絕）｜US5 角色首頁指定（寫端不驗一致、讀端兜底既有 `resolve_home`）。量級：ROUTES 22→39（`/systemManage/{getRoleList,getAllRoles,addRole,updateRole,deleteRole,batchDeleteRole,getMenuList/v2,getMenuTree,getAllPages,addMenu,updateMenu,deleteMenu,batchDeleteMenu,getDeletedMenus,restoreMenu,getRoleHome,updateRoleHome}`、全政策保護、授權態照 seed 逐列）、MSG_KEYS 19→40、憲法 1.4.0→1.5.0、ADR 五支。另含 004 域連帶四件（分頁 helper 改引、ILIKE 收攏＋BL-00096、BL-00082 boot 體檢、ADR-00040 supersede）。

**零 migration、零 seed 變更（事實）**：Q1 要點所列；`migration/src` 維持恰 `m0001`／`m0002` 兩支；seed 78 列選單、163 列政策、3 列角色不動；`list_active` 等寫死 78 之既有測試零改動。⇒ BL-00047／BL-00028 不觸發。

**不入刀**：三維授權治理六支、getAllButtons／getAllEndpoints、授權回收桶讀端與 restorePolicy、結構性封死、島 G 入憲、兩顆授權 modal 做真、policy-archive 頁（006）｜user 域一切（007）｜稽核頁（008）｜no-escalation 本體（BL-00048）｜通用節流 seam（BL-00124）｜列表排序能力（BL-00044 同族）。

### §2 憲法 Amendment 射程（MINOR 1.4.0→1.5.0、一筆；ADR①）

- **§I.7 島 H 五條**：以 rev5 v1.7.0 字面（`rev5:ADR 0048`）為底、不取 v1.10.0 終態（後者含 006 之 reason gate 五值兌現句）；rev6 座標改寫＝H1 終態成員句寫「006-authz-governance 屆時兌現、該等端點不存在期間 vacuous 成立、屆時入域零修憲」、序言「G 位保留給 006 之島 G，兩島對偶（H2↔G3、H1/H5↔G5、H3↔G4）」；常數（advisory key、上溯上限、route_name 形制）留活書。承襲指針表 H 列尾註「rev6 已入憲 v1.5.0」；MAJOR 射程句「六島」→「七島」。
- **島 E 補兩句**（BL-00098）：解鎖端點之操作稽核 MUST 先於解鎖標記寫入；操作者上下文缺席 MUST 拒寫 5000、不得以佔位位址補足稽核列（與島 F 之 F3① 同向）。措辭 plan 期定、user 親決時定稿。
- **§III.2 用途 (ii)「role／menu 管理頁 CRUD 接真」恰 9 檔**（檔級硬邊界）：`src/views/manage/role/index.vue`／`role/modules/role-operate-drawer.vue`／`role/modules/role-search.vue`／`src/views/manage/menu/index.vue`／`menu/modules/menu-operate-modal.vue`（五支修改型、逐行 `原行:`）＋`src/components/advanced/table-header-operation.vue`（附加 `showAdd?`／`showDelete?` 兩 prop、預設 true；修改型）＋`src/locales/langs/{en-us,zh-cn}.ts`（新增型圈界、`page:` 樹 `manage.role`／`manage.menu` 既有子命名空間之資料級補鍵；塊數以標記實數為準、rev5 as-built 各 4 塊）＋`src/typings/app.d.ts`（新增型、`Schema.page` 對應型節；同上實數）。紀律欄：兩顆授權 modal 明文不入名單（本刀出現任何 diff＝紅、tasks 帶 `git diff` 零輸出斷言）；`menu/modules/shared.ts` 兩向 diff 零改不入；兩語鍵集 MUST 相等；`route:` 樹零新增（role／menu route 鍵 upstream 既在）；路由外掛產物四檔零變動（不新增 view 頁）；`components.d.ts` 重算走 §III 生成檔紀律。後端拒因鍵落三檔 locale `backend:` 樹與 `app.d.ts` backend 型節＝既有 I18N-WIRING (ii)(iii) 授權內、不隨本款擴列。
- **BL-00118**：表外宣告 1 量法句改為與活書 08 同一量法（圈界塊／單行形分列、修改型 `原行:` 數）、既有列範圍欄數字依現算對齊；**BL-00119**：§I.7 段首「rev6 增補恰四處」句改為以 Amendment log 為準之敘述。
- **硬序**：Amendment accepted 前不動任何 base-web 既有檔（backend 21 鍵落 locale 既有檔亦受閘）；純後端單元可先行；慣例沿 003／004＝U0 排最前。

### §3 後端架構與模組邊界（承 rev5 as-built HEAD 形、重打字、rev5 出處帶前綴）

`handler/role.rs`（role 6＋roleHome 2＝8 支）、`handler/menu.rs`（menu 7＋getMenuTree＋getAllPages＝9 支）、新 `model/facade/sys_casbin_archive.rs`（域鎖底座兩形薄 fn＋`menu_domain_waiter_count` 觀測 helper、歸檔寫入面、reason gate 三值單點 fn、移除面掃描：deleteRole 全三維含 protected／deleteMenu 跨角色 menu 維＋獨有 button 碼／updateMenu 絕版碼）、`facade/sys_menu.rs`（治理域讀端 `list_governed`、樹寫端狀態機、守門、`paginate_top_level`）、`facade/sys_role.rs`（CRUD 寫端、鎖讀 helper、`SEEDED_ROLE_IDS`／`SUPER_ROLE_CODE` 常數＝單一宣告源）、`facade/mod.rs`（`ilike_contains` 共用件；`sys_role`／`sys_ip_rule` 改引）、`facade/sys_ip_rule.rs`（改引 ILIKE＋四寫端與 `find_by_id_for_update` 具型簽章＝BL-00096）、`config.rs`（`load_trust_model` 標頭名體檢＝BL-00082）、`auth/enforce.rs`（`rebuild_enforcer`／`reload_enforcer`、`RELOAD_SERIAL`＋T020 形注入式 seam、`RELOAD_MAX_ATTEMPTS=3`／`RELOAD_RETRY_BACKOFF_MS=50`、metrics `casbin_reload_total{ok|retry|exhausted}`；檔頭與 `main.rs`「終態」句改寫指 ADR②）、`envelope.rs`（分頁 helper：current clamp [1,10^7]、size clamp [1,100]、預設 1／10；`handler::ip_rule` 改引）、`router.rs`（+17、`ROUTES_COUNT` 22→39、contract case_key 逐條）、`handler/common.rs`（第三寫端重評）、`model/audit.rs`（零新 variant 釘）、`obs.rs`（預註冊 reload 三 outcome、與 rules.yml 錨對齊）。

### §4 序列化域與判定面同步

- **序列化域**：`SELECT pg_advisory_xact_lock($1)` 走 raw Statement（守 `entity_access_lint`）、xact 級自動釋放、零逾時零重試；key＝`0x7265_7636_6D65_6E75`；進域＝addMenu／updateMenu／deleteMenu／batchDeleteMenu／restoreMenu＋deleteRole／batchDeleteRole（addRole／updateRole／roleHome 不進域）；固定鎖序 `advisory → 歸檔表列 → sys_role 列 → sys_menu 列 → casbin_rule`、域鎖 MUST 為 txn 首動作、不下沉 facade fn；與 per-user advisory 鎖（`login.rs`、uid 為 key）結構性無 ABBA（key space 不碰撞＋鎖集合零交集）、三失效條件入 ADR②；機器證＝逐寫端各一支 pg_locks NOT-granted 等待測（64-bit key 拆 classid／objid、bigint 直比恆假；非 pg_blocking_pids）。
- **判定面同步**：另建全新 Enforcer 四步鏡像 init（model→adapter→new→load_policy）、任一步失敗整體 Err 不產實例、成功才 write 鎖內一行 move-assign；`RELOAD_SERIAL` 包 rebuild＋swap 含重試全程互斥（封「後 commit 先 swap 蓋回舊快照」窗；交錯時序機器證＝`rev5:B-105` T020 形 `#[cfg(test)]` 注入式 seam、生產建置零存在）；keep-last-good＋結構化告警＋metrics 三 outcome（rules.yml `obs016-casbin-reload-anomaly` 既錨於 retry／exhausted、字面對齊）；耗盡仍失敗＝維持舊面持續告警。觸發矩陣恰移除面三支（deleteMenu／batchDeleteMenu 成功＝觸發；updateMenu 之 buttons 絕版歸檔實際發生才觸發）、於交易 commit 之後、以 `if archived` 為門；被拒／無作用／標的不存在＝早退結構性不觸發；deleteRole／addMenu／restoreMenu 零觸發。★硬禁令＋版本鎖：絕不對 live enforcer 裸呼 `load_policy`（casbin 2.20.0 clear-then-load、空 policy 在 MODEL_CONF 下＝含 R_SUPER 全 deny、唯重啟可救；升版必重核）；呼叫端不得持 `state.enforcer` 讀鎖呼叫。四支測試：失敗注入（壞 conn ⇒ 舊面續 allow R_SUPER）／裸呼必轉紅負向自證／觸發條件特性鎖定／移除面端到端（DB＋in-memory 雙斷言）。

### §5 選單與角色狀態機、分頁、稽核、拒因

- **選單**：治理域（未刪含停用）／顯示域（啟用未刪）分讀，治理候選誤用顯示域＝「停用靜默升級為永久撤銷」必配負向測試；防環（上溯上限常數）；parent 三處一致（新增／改父／復原＝父存在且未刪、停用不擋、`parentId=0` 豁免）；`routeName`／`menuType` 出現即拒（值不比對）；constant 父鏈守門於 create／update／restore 三處（restore 第四腿：標的常量時驗全祖先、非常量零驗）；addMenu 同鍵雙層守門（域內先驗顯式拒＋23505 兜底同一拒因）；同鍵重建零繼承雙封；deleteMenu 守門固定序（protected→未刪子項不論啟停）；batch child-first no-partial 單 txn；空陣列提前 no-op（零副作用、零稽核、不取域鎖）；幽靈父收縮語意不動；restoreMenu 成對清空軟刪欄＋原 status 保留、零 casbin 寫零同步。
- **角色**：三層守門固定序 seeded→in-use（`others = total − operator_is_member`、拒因回誠實總掛載）→self-role；停用雙護欄（不可停用自身所屬、R_SUPER 恆禁）；code 形制 `^[A-Za-z0-9_]{1,64}$`＋活性唯一＋不可變（出現即拒）；部分更新三態（ADR-00015）、全 None 提前 no-op；NOT NULL 欄送顯式 null＝`nameRequired`（兩域同式）；deleteRole 掃 `v0=role_code` 全三維含 protected 列 archive-move（`role_soft_delete`）、單向無 restore；roleHome 寫端不驗可見樹一致。
- **分頁**：共用 helper 四端點同用（getRoleList／getDeletedMenus／getMenuList/v2／IP 規則清單）；getMenuList/v2 `size` 缺席＝回全部頂層、回應 `size`＝實得頂層數、`current` 忽略回 1（工程判斷 5）、有值 clamp；getDeletedMenus 穩定排序 `deleted_at DESC, id DESC`、不帶 `restorable` 旗標；getRoleList `id ASC`、模糊欄走 `ilike_contains`；getAllRoles 僅活性且啟用、無 memo；getMenuTree 治理域輕量樹 `{id,label,pId,children}`；getAllPages 顯示域 route_name 全集 `(order ASC NULLS LAST, id ASC)`。
- **稽核與拒因**：每寫端同交易恰一列（`sys_operation_log::write_in_txn`）、`AuditOperation` 沿 add／update／delete／restore、`entity_table` 區分、batch 逐標的一列——spec FR 寫成三寫端（IP 規則、角色、選單）一致要求；操作者自 `common::operator_from_context`、缺席拒寫 5000（`tracing::error!` 帶各域 target 留呼叫點）；body 收斂走 `common::json_or_default`；拒因全純 key 一因一鍵、復用 2222／5003／4040／5000、13 碼矩陣零觸碰；`biz.role.*` 10 鍵（codeInvalid／codeExists／codeImmutable／notFound／seededProtected／inUse／cannotDeleteSelfRole／cannotDisableSelfRole／superCannotDisable／nameRequired）＋`biz.menu.*` 11 鍵（notFound／routeNameExists／routeNameImmutable／menuTypeImmutable／parentNotFound／cycleDetected／hasChildren／protectedMenu／constantParent／restoreConflict／nameRequired／routeNameInvalid 取十一之終態、逐字面於 i18n 單元定稿）。

### §6 前端

- 修改型＝用途 (ii) 9 檔逐行 `原行:`；新增型新檔＝兩支 wrapper＋兩支 typings（工程判斷 3）；getAllPages 走 upstream barrel。
- **role 頁**：列表接真（分頁＋搜尋＋狀態）、memo 欄＋drawer textarea（placeholder「管理員可見」）、刪除／批刪接真（拒因 toast 由共用攔截層轉譯 `backend.biz.role.*`、頁內只看 error）；「菜單權限／按鈕權限」兩鈕維持 demo stub（已知態、006）。
- **menu 頁**：treeTable 接真（治理域、無參一次取全樹、分頁列凍結形照 `rev5:ADR 0060`：`itemCount: undefined`＋`pageCount: 1`＋自備 prefix——`itemCount` 與 `pageSize: 0` 並存會算出 `Infinity` 頁數凍死瀏覽器）、回收桶 toggle（prefix slot NSwitch 綁 `showDeleted`、資料源換 getDeletedMenus、操作欄整欄換復原、復原鈕無按鈕碼 gating）、切換清勾選（`rev5:B-100`）、pageSize 歸位（`rev5:B-132`）、memo 欄＋modal textarea、已刪模式以 `:show-add`／`:show-delete` 關寫入口（Q5）；modal：父選擇器 NTreeSelect 消費 getMenuTree、`fetchGetAllRoles` 殘留不帶、頁面下拉走 getAllPages（Q2）、`multiTab` 可寫、編輯態 `routeName`／`menuType` 鎖定。
- **ip-rule 頁**（rev6 新檔、免授權）：疊寫改 `:show-delete="false"`；type 標籤對映射取不到之值退顯原字串（Q4）。
- **i18n**：`page:` 樹補 `manage.menu.{showDeleted,confirmRestore,restore,restoreSuccess}`＋memo 欄位標籤與 placeholder 鍵（兩語鍵集相等）；`backend:` 樹 21 鍵三檔同補；`app.d.ts` page／backend 兩型節；`msg-key-gate`／`fork-delta-lint`（修改型只在 9 檔）／`wire-schema check`／`view-render-guard`／`route-artifact-gate`（零變動＝冪等綠）全過。static meta 不維護（spec 一句紀律）。

### §7 治理面

- ADR 五支（工程判斷 12）；契約落點（工程判斷 8）；活書 as-built（feature branch 內改成現在式）：§5 模組（handler／facade 新檔、enforce 同步面）、§6 新情境「選單域生命週期——島 H」（移除面→歸檔→commit→rebuild-swap→swap；失敗 keep-last-good）＋島 F ⑧ 三態字面（ADR⑤）、§8.2 API 慣例（跨端點分頁規則、ROUTES 39、MSG_KEYS 名冊指針）、§8.4 fork-delta（用途 (ii) 逐用途 as-built、共用元件 prop）、§11 已知態列（指 ADR④／ADR⑤、IP 域三態字面）、§12 詞彙（工程判斷 15）。RUNBOOK：§16.1 dev 分界三態（ADR⑤）、§16.2 標頭名核對句（BL-00082）、§12 碼面閘表（若 BL-00109 腿落 wire-schema.py 之 check 面）、§9c 走查還原面若擴四表。BACKLOG 條文：BL-00120 改為只剩 ADR-00039。
- 收刀簿記：`backlog_done` 19、`backlog_add` 目標零、`adrs` 五支、`arch_impact` §5／§6／§8／§11。

### §8 測試與驗收

- **rust（容器內 `cargo test --workspace -- --test-threads=1`）**：contract 22→39 逐端點 case＋授權態矩陣（Admin 對寫端 5003、對 getRoleList 通；R_USER_COMMON 對 getAllRoles 通）；守門矩陣（role 三層固定序、停用雙護欄、menu 守門序、constant 父鏈 create＋restore、不可變欄出現即拒）；序列化域逐寫端機器證；判定面同步四支＋RELOAD_SERIAL 交錯時序案（T020 形）；零繼承端到端（DB＋in-memory 雙斷言、★先種 live 授權再測防恆綠）；分頁 helper 四端點 clamp 案（逾界＝上界值、size 缺席全取、`&size=0&current=0` 收斂）；`ilike_contains` 轉義案＋`sys_ip_rule` 具型簽章後既有案全綠（BL-00096）；`load_trust_model` 標頭名體檢一正一反（BL-00082）；wire-schema 十二 definition＋六型鍵集斷言（BL-00105）＋`PageRes` 名冊（BL-00112）；i64 守衛 lint 名冊擴＋泛型實例化名冊腿（BL-00106）；測試模組閉合 lint 腿＋變異自證（BL-00111）；四表清理守衛＋自證測（工程判斷 10）；BL-00110 RAII；`each_domain_keeps_its_own_log_literals` 不變；`schema-gate` 三閘綠。
- **python**：`tools/wire-schema.py` 加 qs 序列化前提腿（BL-00109）＋self-test；體檢單元之 BL-00107／BL-00123／BL-00115 案。
- **前端**：`pnpm typecheck`、`fork-delta-lint`、兩顆 modal `git diff` 零輸出斷言、`msg-key-gate`、`wire-schema check`、`route-artifact-gate`。
- **CDP 三方對照**（127.0.0.1:22080 vs 32080；★一律 `opus[1m]` xhigh agent）：role 頁列表／搜尋／新增／編輯／刪除／批刪／memo；menu 頁樹／新增（父選擇器、頁面下拉）／編輯（buttons 移除→歸檔＋同步）／刪除／批刪／回收桶 toggle／復原／memo；ip-rule 頁表頭 prop 形零差異；已知態三組逐項實際操作觀察；排除清單＝rev5 22080 之 006～008 增量（工程判斷 14）。真登入走查前後 `tools/walkthrough-baseline.py` snapshot／diff／restore（RUNBOOK §9c）。
- **收刀前承載體檢單元**：BL-00106／BL-00107／BL-00110／BL-00111／BL-00123／BL-00115 落地；反向確認 BL-00047／BL-00028／BL-00048／BL-00074／BL-00108 零觸發現算。

### §9 單元切分草案（tasks 定稿於 SDD；此處只定骨、約 19 支）

U0 ★主線：憲法 Amendment＋五 ADR 親決（硬閘）→ U1 Setup（handler 骨架、router +17、`AuditOperation` 零新 variant 釘）→ U1b 004 域連帶（分頁 helper 落 envelope＋`ip_rule` 改引、`ilike_contains` 收攏三份＋BL-00096 具型簽章、`load_trust_model` 標頭名體檢＝BL-00082；review 烤入 004 域防回歸）→ U2 域鎖底座＋ABBA 機器證＋歸檔寫入面＋reason gate → U3 rebuild-swap＋RELOAD_SERIAL（四測＋T020 交錯案；rules.yml 錨對齊）→ U4 測試基建（四表守衛＋自證測＋BL-00110 RAII）→ U5 治理域讀端七支（getRoleList／getAllRoles／getMenuList/v2／getDeletedMenus／getMenuTree／getAllPages／getRoleHome）→ U6～U7 role 寫端（facade TDD→handler＋router；第三寫端進場時 BL-00113 重評）→ U8～U10 menu 寫端＋回收桶＋constant 守門＋reload 接線 → U11 零繼承端到端 → U12 wire 面（十二 definition＋BL-00105／BL-00112／BL-00109＋i18n 三處＋MSG_KEYS）→ U13～U14 前端（role 頁＋memo／menu 頁＋toggle＋memo＋prop＋ip-rule 兩處）→ U15 治理面（活書、RUNBOOK、ADR④、ADR⑤ 三處鏡像、BL-00120 條文）→ U16 收刀前承載體檢（BL-00106／BL-00107／BL-00111／BL-00123／BL-00115）→ U17 全量閘＋CDP 三方對照 → 收刀簿記。高風險共享檔序列鏈（同檔任務不標 [P]）：`facade/sys_menu.rs`、`facade/sys_role.rs`、`facade/sys_casbin_archive.rs`、`handler/role.rs`、`handler/menu.rs`、`router.rs`、`tests/contract.rs`、`envelope.rs`（U1b）、`facade/sys_ip_rule.rs`（U1b）。編排慣例：implementer `fable[1m]`／review・fix `opus[1m]`、皆 xhigh；CDP 單元 implementer 改 `opus[1m]`；防呆六件套。

### §10 風險

1. **rebuild-swap 失手＝含 R_SUPER 全 deny、唯重啟可救**（最高風險件）：硬禁令＋版本鎖＋失敗注入測＋裸呼必轉紅負向自證；RELOAD_SERIAL 封交錯窗＋T020 形交錯時序機器證自首版帶入。
2. **共用元件 prop＝新 upstream 衝突面**：附加 prop 預設 true、既有呼叫端零改、修改型標記兩處；rebase 時原行同步。
3. **三業務表逐列比對＋序列 setval 期望值**：測試殘列或序列推進即 gate2 紅；四表守衛＋自證測、造列顯式大 id、setval 還原 is_called 正確；`casbin_rule` 造列走真 `add_policy` 必 setval。
4. **治理清單 `size` 缺席全取＝與 rev5 契約字面不同**：契約明寫、contract test 釘；UI 零差異。
5. **`common.rs` 第三寫端重評**可能改兩件簽章：既有兩域字面守釘住 target 不併。
6. **rev5 後刀增量混入**（006 grant 面／007 sid／no-escalation／008 audit）：藍本取 HEAD 形時逐檔剔除、防回歸清單烤入 implementer prompt。
7. **seed 78 寫死測試與 `ROUTES_COUNT`**：零 seed 變更；ROUTES 22→39 同 commit bump。
8. **CDP 對照基準已含 006～008**：排除清單逐項、已知態實際操作觀察（`rev5:L-054`）。
9. **004 域連帶四件擴大 review 面**（分頁 helper 改引／ILIKE＋BL-00096 三十處測試改交易／BL-00082／ADR-00040 supersede 三處鏡像）：獨立單元 U1b 與 U15 承載、review prompt 烤入 004 域防回歸與「零 wire 行為變更」判準；`sys_ip_rule` 既有案全綠為 U1b 出口。

## 4. 憲法 §IV 九題預答（供 `/speckit-plan` Constitution Check 起手）

1. base-web 為權威：PASS——role／menu 頁為 upstream demo 面、其 fetch 標的正是本刀補齊對象；wire 型別開獨立命名空間、demo 頁欄定義同批改（修改型）。2. base-web inline：**涉及——授權以 Amendment 先行取得**（用途 (ii) 9 檔；backend 21 鍵走既有 I18N (ii)(iii)）。3. casbin：PASS——本刀對選單域只做 CRUD 資料面、可見性授權屬 006、零 seed 改動；已知態③（新建選單側欄不現）＝本項誠實結果。4. §I.3：PASS——13 碼零觸碰、2222 復用、id number＋2^53 守衛、`PageRes` 四欄不變、跨端點分頁規則入活書 08 §8.2；IP 規則清單未知類型上 wire＝ADR⑤ by-design。5. 前代拷貝：零拷貝、重打字消化、rev5 出處帶前綴；差異點表（§1 翻案列＋工程判斷 1 剔除清單）入 research。6. §II：零抵觸；翻碼內舊拍板一處（`enforce.rs`／`main.rs`「終態」句）立 ADR②；翻 ADR-00040 以 ADR⑤ supersede。7. ★軌道：**涉及——授權以 Amendment 先行取得**，屬既有軌道加用途、非補完。8. 新表：零、零 migration；消費五表皆 001 基線既有。9. 行為島：**涉及——島 H 隨本刀 MINOR 入憲、島 E 補兩句**；state-machine 鏡頭（選單／角色／判定面三矩陣）。

## 5. 給 `/speckit-specify` 的輸入摘要

- feature 名＝`005-role-menu-crud`；user 故事核心＝超管建／改／刪角色與選單、選單回收桶與復原、刪選單後授權在判定面立即失效且失敗時服務不中斷、角色首頁指定；17 支端點、零 migration、憲法 1.5.0；另含 004 域連帶四件（治理 US 或 FR 段承載）。
- 直接輸入：本檔＋§2 處置表所列 BL 條目（收 19／改條文 2／反向確認／Out of Scope）＋`rev5:005-role-menu-crud` spec 之 US1～US5、FR-001～FR-051、SC、Edge Cases（rev6 座標改寫：17 支與 ROUTES 39、`rev6menu`、`size` 缺席全取、共用元件 prop 形、BL-00095 by-design、rev5 後補鍵集自首版即入、`PageRes` 既在、rev6 水位守衛形、getAllPages 入 US2 且住 menu 域、譯文權威三檔 locale）。
- FR 措辭要求：操作稽核落列寫成 IP 規則／角色／選單三寫端一致要求（體檢 §0.2 #4）；分頁規則寫成跨端點 FR（含 getMenuList/v2 缺席例外）；`sys_ip_rule` 具型簽章與 `load_trust_model` 標頭名體檢以「零 wire 行為變更」FR 承載。
- ★原 clarify 候選轉工程判斷（specify 直接抄、clarify 不再以此出題）：①`handler/common.rs` 重評結論落點（工程判斷 11）②分頁 helper 落點與四端點改引（工程判斷 4）③BL-00109 錨落 python 側（工程判斷 6）④BL-00106 收法（工程判斷 7）⑤契約落點（工程判斷 8）⑥四表守衛與 setval 值（工程判斷 10）⑦CDP 排除清單與模型（工程判斷 14）⑧`menu-operate-modal` 頁面下拉走 getAllPages、父選擇器走 getMenuTree（Q2、G4）⑨getMenuList/v2 缺席語意（工程判斷 5）⑩BL-00082 體檢形（工程判斷 17）⑪BL-00111 lint 腿形（工程判斷 18）⑫getAllPages 落點（工程判斷 16）。

## 6. 隨做隨記

- ADR 待立五支（刀分支內落、序號接續現行最大號）：Amendment／判定面同步 rebuild-swap／A1 域行為／本刀已知態與 by-design／IP 域已知態 supersede ADR-00040（G1）。draft 時點承 003 Q5：plan 期產 draft、tasks 首個主線任務只跑「user 親決→accepted→bump→generate」；supersede 形承 ADR-00032 翻 ADR-00016 前例（新檔 `supersedes`、明列各款原意續行或改寫、現在式引用改指新檔）。
- 收刀 `backlog_done` 19 條（§2 清單）；改條文：BL-00120（只剩 ADR-00039）；BL-00093 不動、收單訊息記 casbin-reload 錨對齊；`backlog_add` 目標零；淨流量若仍超標先分揭露型／新欠型（體檢 §7）。
- NOTES「下一步」：specify 起手後同批改為 005 進行中；收刀時改 006。
- 依賴：零新依賴（casbin 2.20.0 既釘；NTreeSelect 為 naive-ui 既有元件、零新套件；`http::HeaderName` 為既有 axum 依賴）——毋須版本拍板。
- TDD 發射前置：模型依骨架值（implementer `fable[1m]`、其餘 `opus[1m]`、皆 xhigh）；CDP 單元 implementer 改 `opus[1m]`（user 2026-09-20 明令）；換模只動成品 `.mjs`、不動 tracked 骨架。
- 活書：§3 設計 §7 所列各節於 feature branch 內改成現在式；C4-L2 拓樸不變（零新容器）。
- 本檔 grill 修訂（G1～G4、工程判斷 16～20、§2 處置表 41→22）另顆落地於 default（004 前例 `bfaba0e` 形）。
