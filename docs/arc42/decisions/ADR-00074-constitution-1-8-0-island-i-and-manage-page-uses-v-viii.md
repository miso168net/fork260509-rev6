---
id: "ADR-00074"
title: 憲法 Amendment 1.7.1→1.8.0——§I.7 島 I（使用者域治理；I1～I5、I7 入憲、I6 刻意空缺）＋跨島註與跨島總則＋島 B／C 用語與島 H2 連動＋§III.2 ★BASE-WEB-MANAGE-PAGE-WIRING 用途 (v)～(viii)＋★BASE-WEB-LOGIN-CAPTCHA-WIRING (ii) 開立＋★BASE-WEB-I18N-WIRING (i)(iii) 改寫與三語鍵集
date: 2026-10-05
status: accepted
supersedes: []
superseded_by: []
provenance: "007-user-password-admin 之 spec FR-055（①～⑤）、FR-056①、FR-010～FR-011、FR-014～FR-018、FR-021～FR-030、FR-032～FR-037、FR-040、FR-043、FR-047～FR-054、SC-012；brainstorm §0 Q1／Q3／Q4／Q4a／Q6／Q7／Q8／Q9／Q12／Q13／Q17／Q18／Q19、GR1b／GR2／GR3／GR4、主線工程判斷②⑤⑪；§3 §1 憲法 Amendment 段、§4 第 2／7／9 題；島 I 條文以 rev5 憲法 v1.10.0 §I.7 島 I 段為底（`rev5:ADR 0063` 款一；I5 末句＝`rev5:ADR 0068`；rev5 凍結 SHA 7eab28a）；§III.2 (v)(vi) 與 LOGIN-CAPTCHA (ii) 列形承 `rev5:ADR 0063` 款二，範圍欄預估取 rev5 base-web 9833308 同用途標記實數；承接 ADR-00063 翻案觸發器兩條（G5 ★句轉非 vacuous、島 I 入憲時複核 G2／G6 與包含規則邊界）與 ADR-00003 後果段（I6 空缺位之處置）；範圍欄 PATCH 實數化前例＝ADR-00051／ADR-00072；§V.2 流程、§V.3 MINOR 判準；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [constitution, amendment, behavior-island, user-domain, password, fork-delta, i18n]
---

## 背景

007-user-password-admin（本刀）同時撞到憲法五處凍結位：

- **§I.7 島 I**：本刀落地使用者域治理狀態機（帳號啟停刪復、會話撤銷三型、設密冷卻與改密節流、寫端下放之包含規則），承襲指針表 I 列（`rev5:ADR 0063`；I5 釐清＝`rev5:ADR 0068`）為直接輸入、§IV 第 9 題要求隨本刀入憲；ADR-00003 後果段與承襲指針表尾句要求島 I 進場時一併處置空缺位 I6 與跨島不一致；ADR-00063 翻案觸發器兩條指向本刀（G5 ★句轉非 vacuous；複核 G2／G6 與包含規則之邊界）。
- **島 B／C／H**：管理員踢除另立第三 reason `admin_kick`（spec FR-027），島 C「`kicked` 與 `revoked` 兩 reason 皆同」漏列；GR2 定用語（單一會話被別處登入擠掉＝頂替、管理員結束他人全部會話＝踢除），島 B 第三點現以「踢除」指頂替；選單刪碼守門（GR1b）是否入 H2 待親決（FR-055③）。
- **跨島**：密碼政策鍵矛盾組合取「設密全拒」（Q19），與島 E「整組退常數」方向相反（FR-034 要求跨島註寫明理由）。
- **§III.2**：使用者頁三檔、個人中心父層、IP 規則頁解鎖之 i18n、角色與選單頁按鈕碼顯隱皆動 base-web 既有檔，用途 (i)～(iv) 不涵蓋 ⇒ 新開 (v)～(viii)；LOGIN-CAPTCHA (i) 列保留凍結位「用途 (ii)（`formRules` 放寬）不在本次授權，延改密端點刀」——本刀即改密端點刀；I18N (i) 列「錯誤信封 `data` 恆 null、無明細通道 ⇒ 不建 `translateDetailValue`」與 Q18（明細只限兩鍵）相牴；I18N (iii) 列「`LangType` 擴充／locale 註冊／`zh-tw.ts` 標型重構不在本次授權，延前端 UI 刀」——Q4／Q4a 本刀接上並預設繁中；MANAGE (i) 列解鎖延後句、(iii) 列「門在頁級」句隨 Q9／Q8 失準；(i)～(iv) 列「兩語鍵集 MUST 相等」隨三語 runtime 失準。
- **承襲指針與射程句**：I 列補 rev6 入憲尾註；MAJOR 射程句「八島」改「九島」。

合計一次 bump **1.7.1 → 1.8.0**（MINOR）。**改本檔哪一節**（§V.2 步 1）：§I.7（新增島 I 段、島 B／C 第三點、島 H2〔依 H-a〕、跨島註、跨島總則、MAJOR 射程句、承襲指針表 I 列）、§III.2（新增五列；改寫 LOGIN-CAPTCHA (i)、I18N (i)(iii)、MANAGE (i)～(iv) 列內句）、版本行與 Amendment log。

★附記：`rev5:ADR 0063` 款三不入條文——no-escalation 兩實作位分工由 ADR-00075 承載；按鈕碼 gating 判準（「該頁選單維政策是否僅 R_SUPER」）因 Q8（三頁一律逐鈕顯隱）不帶回，角色抽屜三顆授權鈕與選單回收桶復原鈕不設碼之理由改為「其讀寫端點屬封死集」（spec FR-048；seed 政策列 32／33／52～57／64／65 皆受保護）。`rev5:ADR 0068` 之 I5 末句直接併入（FR-055①）、不另立 PATCH。

## 決策驅動因子

- 一刀一次 MINOR；範圍欄實數化另以收刀前 PATCH（前例 ADR-00051／ADR-00072）。
- 島條文只收已有或本刀同時交付機器證之行為（spec FR-063 自證索引）；條文只凍結方向面，常數住 ADR／活書。
- 憲法不寫 BL 號、刀名代稱與未來式（BL 收刀即刪列、憲法不留死引用；GT-05／時態分離）。
- 對前代字面與 rev6 現行字面之差異全數申報（差異附表）。
- 同一事實一個家：明細通道＝ADR-00076、自助路由白名單與 §I.2 之關係＝ADR-00077、冷卻與節流＝ADR-00078、政策壞值告警出口＝ADR-00079、包含規則實作位與 G2／G6 邊界＝ADR-00075；條文只承接方向面。
- 檔級名單是硬邊界、範圍欄注記須落 `tools/fork-delta-lint.py` 數量段閉集形；新列一律「預估」使對賬腿可辨認跳過。
- 硬序：本 Amendment accepted 前 base-web 既有檔零 diff（FR-055⑤、SC-012）。

## 考慮過的替代案

1. **取 rev5 島 I 字面逐字**：I1「與登入／換發同源的 per-user advisory 鎖」不實（換發鎖呈遞票列 `sys_token::find_by_hash_for_update`、不取 advisory；前代同形）；I1「角色列（僅比對需要時讀）」牴觸 rev6 G5 ★句（前代 as-built 只讀不鎖＝RL-0065 不帶回）；I2 漏自助改密撤他會話；標頭寫 BL 號；棄。
2. **I6 往前遞補**：前代刻意留號以便兌現時回填、不動已凍結編號；遞補即跨代條號錯位；棄。
3. **首登強制改密併入本刀填 I6**：Q1 拍板不做（BL-00140）；棄。
4. **島 C 不動、`admin_kick` 只記活書**：第三 reason 之 TTL 可被靜默改短而不觸修憲（前代同漏）；棄。
5. **政策壞值方向只寫跨島註**：方向無家則其反轉不在 §I.7 MAJOR 條款射程；棄（I5 載方向、跨島註載理由）。
6. **改密節流入 I5 條文**：載體、門檻、降級來源皆 ADR 級（前代同判）；島 E「redis 於本島只承載 captcha 一次性標記與解鎖標記」射程限島 E、不衝突；棄。
7. **§I.2 增自助路由例外句**：ADR-00077 以兩支柱承載、前代同判不修 §I.2；棄。
8. **(viii) 併入 (ii) 列**：(ii) 範圍欄為實數，併入即改預估而失去兩支 view 之修改型對賬；005 刀與本刀改點混標；棄。
9. **繁中 runtime 另開 I18N (iv)**：(iii) 列之延後句即該凍結位（形同 LOGIN-CAPTCHA (ii)），spec FR-054 與 ★ 軌道逐處登記表已以 (iii) 為授權名；棄。
10. **I18N (i) 只刪「data 恆 null」句、不限鍵數**：明細通道射程無條文上限、Q18 限兩鍵落空；棄。
11. **「兩語」八處全改三語**：四處指稱 upstream 兩檔 locale 之授權（`zh-tw.ts` 為 rev6 自有檔、不入本表），改寫即誤讀為三檔受本表授權；棄（見決定四 T-a）。

對所選方案跑同一反例（RL-0013）：
- 新增使用者豁免 per-user 鎖是否使 addUser 掛上已軟刪角色？其寫後角色集仍 `FOR UPDATE` 並鎖內重驗未軟刪；成立。
- 換發重驗是否被 grace 冪等窗違反？條文射程限簽發腿；grace 回既發之同一對、零新簽發，該對 refresh 列已隨撤票轉 `revoked`、access 由 denylist 與到期兜底；成立。
- 不加每請求判定與「被撤者下一次請求 `8888`」矛盾否？後者靠 sid 級 denylist、非帳號活性查詢；成立。
- I7 全集是否繞過 I3 與本人規則？I7 明定兩者先判；成立。
- H2 補句（甲）與 H2 絕版歸檔句矛盾否？補句於任何寫入與歸檔之前判拒、被拒者不發生歸檔；成立。
- 新列全數預估是否留無守窗？窗＝本 Amendment 至收刀前 PATCH，計數由單元出口逐檔實測承擔（P-c），授權判定（三元組名冊、檔級名單）不受預估影響；以候選字面合成之憲法經 `tools/fork-delta-lint.py --constitution` 實跑 rc 0（修改型三元組對賬 33→32、跳過 0→25；新增型逐檔對賬 20→14、跳過 0→15；產物檔跳過 4 不變；2026-10-05 plan 期收攏後以本決定四候選字面重跑）；成立。
- I1 取鎖時點改「於任何列鎖之前」（I-d1）是否放出 pre-read 判定窗？鎖前只容普通讀（unlockLogin 帳號維之帳號名解析）、advisory 仍先於任何列鎖、一切守門判定仍鎖內重驗（lock-then-redecide）；域內鎖序與批次取鎖序不變；成立。
- 「兩語」指稱句改兩檔明寫（T-a②）是否落入替代案 11 之誤讀（三檔受本表授權）？指稱句明寫 `en-us`／`zh-cn` 兩檔、`zh-tw.ts` 仍為 rev6 自有檔不入本表；I18N (iii) 列不設定義句（N-b）、表內零「兩語 locale」一詞；成立。

## 決定

以**一筆 MINOR Amendment**（1.7.1 → 1.8.0）處理下列五款。★「候選字面」皆為本刀 U0 親決輪之底稿：user 逐款親決後，本 ADR 於 accepted 前同步改寫為定稿字面（翻案觸發器第一條）；各選項題之建議列首位。

### 一、§I.7 新增島 I 段（置於島 H 之後、跨島註之前）

**標頭（I-a）**：①（建議）完整形——列區間＋出處＋I6 空缺說明＋增補／明文化／改寫申報（不寫條數）；前代 U0 題②親決同取、I6 跳號須在本文留痕、島 G／H 同形。② 最短形（進場刀名＋出處＋I6 一句）——rev6 增補在本文不可見。

**I6 寫法（I-b）**：①（建議）標頭括號一句、不寫 BL 號（承載 BL-00140 由本 ADR 後果段指向）。② 照前代加寫 BL 號——兌現即刪列、條文留死引用。③ 另起「I6（空缺）」條目——空條目與「只收有機器證之行為」不合。

**I7 具名（I-c）**：①（建議）具名 `R_SUPER`——前代 U0 題①同取；G6 已逐字寫「非 R_SUPER 角色」；常數慣例射程是量測值與門檻、非結構性身分。② 不具名（「持超級管理員角色者」）——取②時 I7 兩處同改。

**候選字面**（取 I-a①、I-b①、I-c①；逐條親決＝I-d1～I-d7）：

> **I. 使用者域治理**（007-user-password-admin 進場；出處 `rev5:ADR 0063`＋`rev5:ADR 0068`、rev5 v1.10.0 字面為底——I1～I5 沿前代已驗證形〔I5 末句之雜湊生成與驗證區分＝`rev5:ADR 0068`〕、I7 包含規則為前代新立條；★I6 位刻意空缺＝前代 I6 之密碼經手判定與首登強制改密不做、兌現時回填該位；rev6 增補＝I1 角色列鎖讀與鎖內重驗未軟刪、I2 自助改密撤他會話、I5 政策矛盾組合之方向；rev6 明文化＝I1 使用者域寫端不入島 H1 序列化域、I2 換發重驗之讀形與不加每請求判定之射程、I5 政策鍵於每次設密讀現值、I5 不洩面列舉、I7 與島 G6 正交、I7 射程排除自助改密；rev6 改寫＝I1 advisory 同源句（換發不取 advisory）、取鎖時點與批次取鎖序；逐項出處見 ADR-00074。字母沿前代記 I）
> - **I1 寫端鎖序與 lock-then-redecide**：一切以**既有**使用者為標的之使用者域寫端 MUST 於任何列鎖之前取得與登入同源的 per-user advisory 鎖；域內固定鎖序 MUST 為 advisory(uid) → 標的使用者列 `FOR UPDATE`（復原用已刪列版）→ 角色列 → 角色指派列寫入，禁反向；改動角色指派之寫端（含軟刪連帶硬刪指派）MUST 對標的現持與寫後角色集之聯集依識別去重升序 `FOR UPDATE` 角色列、鎖內重驗未軟刪（島 G5 ★句之兌現；不改指派之寫端不鎖角色列）；一切守門判定 MUST 鎖內重驗（lock-then-redecide、永不信 pre-read）。新增使用者豁免 per-user 鎖（新識別對並發不可見；並發同名保護＝帳號名活性唯一約束），角色列鎖讀照前句；批次寫端依識別去重升序、全批 advisory 先於任何列鎖、角色列整批聯集一次升序。帳號名與信箱之活性唯一索引為復原衝突守門之顯式前提。使用者域寫端不入島 H1 序列化域。★advisory key space 沿用登入之 uid 鍵（同用途擴消費者、與島 H1 域鎖之高位自描述常數不碰撞、核過）。★方向反轉（拆散序列化、改回無鎖 pre-read）＝MAJOR。
> - **I2 斷權即時性與分碼不互換**：停用、刪除、管理端重設密碼 MUST 同交易撤銷標的全部 active 票，自助改密 MUST 同交易撤銷本人其餘 active 票（保留當前會話）——rotated 列不動、重放仍走既有重用偵測（島 A）——並落會話事件；管理員踢除同形（撤全部 active 票）、但為**獨立 reason**。動作序 MUST 權威優先（業務寫＋票作廢＋稽核同一交易落定 → commit → denylist 寫入盡力型、存活＝refresh 全壽命）；寫入失敗只結構化告警、**權威儲存為準**。換發之簽發腿 MUST 於呈遞票列鎖之後、簽發之前以一般讀取重驗使用者活性（啟用且未軟刪；查無列＝不活），不活即拒；重驗不取 advisory、不改換發鎖序；grace 冪等窗回既發之同一對、不屬簽發——此為既有 token 狀態機**新增判定腿**、非 fail 方向反轉。MUST NOT 新增每請求活性判定（登入後之一般端點與帳號資訊讀端不判帳號狀態；斷權兩層＝同交易撤票含 denylist＋換發重驗）。撤銷類、單一會話頂替類與管理員踢除類之體驗碼與文案鍵 MUST NOT 互換（三者各自對應、勿「統一」；reason 見島 C）。★方向反轉（拔換發重驗、改 denylist 優先、改為每請求活性判定）＝MAJOR。
> - **I3 seed 帳號與自身結構保護**：前三個種子帳號 MUST 不可刪；第一個（Super）MUST 恆禁停用、恆禁解除其超管角色指派（不因操作者身分而異）——系統恆有至少一個活躍且啟用的超級管理員（結構保證、不需動態計數）；Super MAY 被踢除、被重設密碼。操作者 MUST NOT 刪除、停用、踢除自己，MUST NOT 變更自己的角色指派，MUST NOT 以管理端重設自己的密碼（自助改密走自助端點）；操作者 MAY 改自己的非角色欄與會話政策。守門為碼內常數形。
> - **I4 軟刪硬刪指派＋復原零回灌**：使用者軟刪 MUST 同交易硬刪其全部角色指派列（零幽靈掛載、角色域掛載計數守門保持誠實）；復原 MUST NOT 回灌任何指派（復原後零角色、須重新指派）、狀態保留刪除前原值；同帳號名重建之新使用者 MUST NOT 經任何路徑繼承舊實例角色。批次刪除逐項驗證、任一違規（含已刪識別）**整批拒**（no-partial、單一交易）。
> - **I5 密碼政策單一驗證點＋登入不驗＋三重不洩**：密碼政策驗證 MUST 為單一驗證點（新增帳號、管理端重設、自助改密三入口共用、零分叉）、政策鍵於每次設密單一快照讀現值、違規 MUST 一次收集全部；長度單位＝字元、另加固定位元組上界 ≤ 登入端形制上限；「禁止密碼與帳號名相同」＝大小寫不敏感相等。★**登入路徑 MUST NOT 驗政策**——政策是設密面的守門、不是登入面的守門；把它掛上登入即令既存帳號的合法憑證因政策事後調整而失效。fail-* 方向：政策鍵矛盾組合（最小長度大於最大長度）＝**設密全拒**並發結構化告警（登入不受影響；與島 E 方向相反之理由見跨島註）。密碼明文與雜湊 MUST NOT 洩漏於任何面：承載密碼之 DTO 除錯輸出 MUST 遮蔽（不得預設印出）；API 回應、操作稽核 payload 與日誌 MUST NOT 含密碼明文或雜湊；密碼雜湊之**生成**（hash）MUST NOT 於持有列鎖期間計算（三入口一律於取鎖前算好再進鎖）；雜湊**驗證**（verify）作為守門判定，依 I1 於鎖內重驗執行。★方向反轉（拆單一驗證點、拔遮蔽、把政策掛上登入路徑、矛盾組合改放行）＝MAJOR。
> - **I7 no-escalation 包含規則**：使用者域寫端授權 MAY 由超管於運行期下放給其他角色（seed 預設仍僅 `R_SUPER`、下放為可開關能力、非預設態）；下放後**一切受規則約束之寫端**（使用者管理面寫端全集〔自助改密除外——其標的恆為操作者本人〕＋帳號維解鎖）MUST 於鎖內、任何寫入前判 `T ⊆ A ∧ N ⊆ A`——A＝操作者現役角色集（濾軟刪與停用角色、資料庫現讀；★持 `R_SUPER` 者之 A 視為全集）、T＝標的全部指派列（**不**濾角色狀態）、N＝寫後標的角色集；違者 MUST fail-closed 拒絕（純 key、不洩漏角色差集、零變更零稽核）。seed 保護（I3）與本人諸不 MUST **先於**本規則判定；同級互管允許（零特例）；來源維解鎖不套。判定 MUST 以具名純函式單點實作、諸寫端共用；前端 MUST NOT 預判本規則（後端為唯一裁判）。本規則約束操作者維、島 G6 結構性封死約束角色維——兩者正交、封死不因本規則撤。★方向反轉（拔守門、改 fail-open、改由前端預判、把某支受約束寫端移出射程）＝MAJOR。
> - 常數（seed 帳號識別集、政策鍵名與門檻、違規碼集、設密冷卻與改密節流之窗、次數與計數載體、會話事件 reason 字面集、攜參明細通道之鍵集、自助路由白名單成員、advisory key 值）＝活書／ADR 級、不入條文。

**條文↔承載對照**（非條文、供 tasks 對表）：I1＝spec FR-010／FR-011（ADR-00043 決定 8 重核結論＝本 ADR 決定二）；I2＝spec FR-026～FR-029；I3＝FR-017；I4＝FR-014～FR-016（即 ADR-00044 翻案觸發器第一款之答案）；I5＝FR-032～FR-036，告警出口＝ADR-00079、冷卻與節流＝ADR-00078、明細通道＝ADR-00076；I7＝FR-021～FR-025，實作位分工（中介層掛點續恆放行、判定於 handler 鎖內）與 G2／G6 邊界複核＝ADR-00075；白名單＝ADR-00077。

**對 rev5 v1.10.0 島 I 字面之差異附表**：

| 類 | 位置 | 差異 | 出處 |
|---|---|---|---|
| 座標 | 標頭 | 「I1～I5 沿 rev4 已驗證形〔`rev4:ADR 0053`／`rev4:ADR 0054`〕、I7 為本刀新拍板」→「出處 `rev5:ADR 0063`＋`rev5:ADR 0068`、rev5 v1.10.0 字面為底——I1～I5 沿前代已驗證形、I7 為前代新立條」；「字母沿 rev4」→「字母沿前代」；補三類申報句 | I-a；ADR-00063 決定一 |
| 改寫 | 標頭 I6 句 | 「rev4 之密碼經手與首登強制換密〔`rev4:ADR 0067`〕本刀不做、留 `rev5:B-134`，日後兌現時回填該位」→「前代 I6 之密碼經手判定與首登強制改密不做、兌現時回填該位」 | Q1；I-b |
| 改寫 | I1 | 「與登入／換發同源」→「與登入同源」 | `handler/auth/refresh.rs` 鎖讀形；spec FR-028 |
| 改寫 | I1 | 「於交易起手取得」→「於任何列鎖之前取得」 | I-d1；ADR-00075 決定 4、research R9 第 5 款（unlockLogin 帳號維之帳號名解析為鎖前普通讀） |
| 增補 | I1 | 角色列「（僅比對需要時讀、識別升序）」→ 改動指派之寫端聯集升序 `FOR UPDATE`、鎖內重驗未軟刪（新增使用者亦然）；不改指派者不鎖 | 島 G5 ★句；spec FR-011；工程判斷② |
| 改寫 | I1 | 「批次刪除依識別去重升序逐一取鎖」→「批次寫端依識別去重升序、全批 advisory 先於任何列鎖、角色列整批聯集一次升序」 | `sys_user::advisory_lock_user` fn doc；FR-011 |
| 明文化 | I1 | 補「使用者域寫端不入島 H1 序列化域」 | ADR-00043 決定 8 失效條件② |
| 增補 | I2 | 補自助改密撤本人其餘 active 票、保留當前會話 | FR-026／FR-036 |
| 明文化 | I2 | 換發重驗讀形（票列鎖後、簽發前、一般讀取、查無列＝不活、不取 advisory、不改鎖序）、射程限簽發腿；每請求判定之射程與兩層 | Q12；FR-028／FR-029；BL-00065 題 b |
| 座標 | I2 | 「失效廣播 best-effort、存活時間覆蓋換發憑證壽命」→「denylist 寫入盡力型、存活＝refresh 全壽命」；反轉括號「改廣播優先」→「改 denylist 優先」；補「reason 見島 C」 | rev6 島 C 用語 |
| 增補 | I5 | fail-* 方向句（矛盾組合＝設密全拒＋告警）；反轉括號補「矛盾組合改放行」 | Q19；FR-034 |
| 明文化 | I5 | 「政策鍵單一快照讀取」→「於每次設密單一快照讀現值」；不洩面列「API 回應、操作稽核 payload 與日誌」 | FR-032／FR-005 |
| 座標 | I7 | 刪「（rev5 專屬新條）」；「DB-fresh」→「資料庫現讀」；「super-only」→「僅 `R_SUPER`」 | I-c |
| 明文化 | I7 | 補與島 G6 正交句 | ADR-00064 決定 7 |
| 明文化 | I7 | 射程排除自助改密（使用者管理面寫端全集） | spec FR-021／FR-036 |
| 座標 | 常數行 | 補「違規碼集」「計數載體」「攜參明細通道之鍵集」；「事件 reason」→「會話事件 reason」 | FR-033／FR-037／FR-004 |
| 正名與措辭（併列） | I1～I7 | 箭頭補空白；「建帳／管理端重設／自助改密」→「新增帳號、管理端重設、自助改密」；斜線分隔改頓號；「self 諸不」→「本人諸不」；I5 末之前代 ADR 括註刪（出處入標頭）、「依島 I1」→「依 I1」；I2「重設密碼」→「管理端重設密碼」、「session 事件」→「會話事件」、補「（島 A）」、反轉括號「拔鎖內重驗」→「拔換發重驗」；I5「API 回應 MUST NOT 含密碼」併入「API 回應、操作稽核 payload 與日誌 MUST NOT 含密碼明文或雜湊」 | 名詞正名 |

### 二、跨島註、跨島總則與跨島重審

**跨島註補句（X-a）**：現行跨島註（`session_idle_timeout` fail-loud 對島 E fail-open）句末續接：

> 島 I5 之密碼政策鍵矛盾組合（最小長度大於最大長度）＝**設密全拒**並告警，與 E 的節流設定鍵矛盾組合整組退常數方向相反——設密面若退回預設值，可能以寬於管理員意圖之政策放行密碼，且放行之密碼落庫後不隨設定改正而失效（後果殘留）；節流退常數之後果隨設定改正即消失，若改拒則把全體使用者擋在登入門外。設密全拒之衝擊面限設密三入口（登入不驗政策＝I5），恢復＝改正設定鍵。

**跨島總則補例（X-b）**：①（建議）列舉末「節流三鍵於每次登入嘗試」後補「、密碼政策鍵與設密冷卻秒數於每次設密（既有密碼不追溯＝I5 登入不驗）」——FR-032／FR-035「只在消費當下讀現值」之家即本總則、「不追溯」與總則前句同形。② 不動（總則首句已涵蓋、列舉屬例示）。

**跨島重審結論**（依承襲指針表尾句、本島進場時完成；入 Amendment log）：
- 空缺位：I6 隨本島標頭處置；J2 隨島 J 進場重審（表尾句不動）。
- 島 I 之 fail-* 方向：政策矛盾組合＝設密全拒（與島 E 相反＝上列跨島註）；改密節流載體不可用＝放行並計入既有節流降級計數（與島 E redis 整體不可用同向；改密節流鍵屬島 I 常數，島 E「redis 於本島只承載 captcha 一次性標記與解鎖標記」射程限島 E、不動；ADR-00078 釐清 ADR-00038 射程限登入節流）；denylist 寫入失敗＝盡力型、資料庫為權威（與島 C 同向）；換發重驗＝新增判定腿、島 A／C 方向不變。
- 島 B：會話政策改為 single 不即時踢除（FR-018）＝與「不追溯」同向、ADR-00033 觸發不成立。島 E：帳號維解鎖之包含規則插於上下文檢查之後、稽核之前（FR-040），「稽核先於標記」與「上下文缺席拒寫 `5000`」不動。島 F：來源維解鎖之位址輸入仍為信任錨、不套 I7。
- 島 G：指派寫端落地使 G5 ★句轉非 vacuous（零修憲；括號條件句恆真、不動）；I1 鎖序與 G5 相容（兩序皆 advisory 居首、角色列先於其後各列；使用者列居 advisory 與角色列之間、G5 寫端不鎖使用者列）；G4 in-use／self-role 兩腿轉生產可達（FR-063）；G2／G6 與 I7 正交、判定位次與拒因不互吞（本體＝ADR-00075）。
- ★ADR-00043 決定 8 無 ABBA 論證重核（spec FR-011；結論＝續真）：①key space 不碰撞——I1 沿登入 uid 鍵、選單域鎖為高位自描述常數；②鎖集合——角色域寫端（含角色刪除家族、角色停用）不取 per-user 鎖、使用者域寫端不入選單序列化域（I1 明文），兩序唯一共用之角色列皆於各自 advisory 之後依識別升序取得＝不成環；三失效條件已核未觸發（①角色寫端不撤會話 ②I1 明文不入域 ③無同 key 跨交易重入）；推演細節住本刀 research 鎖序節。
- 島 H：H1 不動（I1 明文化不入域）；H2 依 H-a。

### 三、島 B／C 用語與島 H2

**島 B 第三點（B-a）**：現行「- 踢除 MUST 落 `session_event(kicked)` 並寫 denylist；被踢者在 `(access, refresh)` 窗內換發仍得 `7777`。」改：

> - 頂替（同帳號之新登入使既有會話失效；「踢除」專指管理員結束他人全部會話＝島 I2）MUST 落 `session_event(kicked)` 並寫 denylist；被頂替者在 `(access, refresh)` 窗內換發仍得 `7777`。

**島 C 第三點（C-a）**：「`kicked` 與 `revoked` 兩 reason 皆同」改「`kicked`、`admin_kick` 與 `revoked` 三 reason 皆同」。

**島 H2 補句（H-a；兩候選並列）**：
- **候選甲（建議）**：於 H2「編輯移除按鈕代碼致其**全域絕版**（聯集域同上）時同理（reason=`menu_button_removed`）。」之後插入（其餘逐字不動）：

  > ★選單編輯之按鈕代碼移除集（改碼＝移除舊碼）含尚有受保護授權列之代碼者 MUST 整筆拒、零變更（於任何寫入與歸檔之前判定；承島 G2——受保護授權列不經一般管理介面移除）。

  理由：m0003 起按鈕維受保護 6 列，絕版連動歸檔即經一般管理介面移除受保護授權列之旁路、與 G2「受保護集之變更屬 seed 基線層級決策」相牴；與 H3 受保護選單守門同屬方向面、本刀同時交付機器證（FR-043 正負向＋變異自證）；入 H2 使拔守門＝MAJOR。
- **候選乙**：不補，守門只住 ADR-00086——拔守門僅翻 ADR、旁路之封閉無憲法凍結。

差異：島 B 為用語正名（PATCH 級）；島 C 擴列第三 reason、H2 補句為細項調整（MINOR 計）；出處 GR2／FR-030、FR-027（前代同漏）、GR1b／FR-043。

### 四、§III.2 新增五列與既有列改寫

**新增 MANAGE 四列（列於 (iv) 之後；P-a）**：

> | **★BASE-WEB-MANAGE-PAGE-WIRING** | (v) 使用者管理頁接真（含回收桶、列操作下拉、列解鎖、重設與產密浮層、七碼顯隱） | `src/views/manage/user/index.vue`（預估 16 處修改型＋9 塊新增型）／`src/views/manage/user/modules/user-operate-drawer.vue`（預估 22 處修改型＋16 塊新增型）／`src/views/manage/user/modules/user-search.vue`（預估 2 處，修改型）／`src/locales/langs/{en-us,zh-cn}.ts`（各預估 3 塊，新增型：`page:` 樹既有 `manage.user` 子命名空間之資料級補鍵）／`src/typings/app.d.ts`（預估 3 塊，新增型：`Schema.page` 之 `manage.user` 對應型節） | 嚴格限 demo 殼接真後端（清單六欄搜尋與分頁／回收桶切換兩資料源、已刪模式隱搜尋卡並換復原鈕／新增編輯抽屜〔帳號名編輯態停用、持停用角色之灰色保留選項、會話政策欄僅編輯態且非超管停用並提示、本人列狀態與角色停用、狀態與角色只在改動時送〕／單刪批刪／列操作下拉之踢除下線、重設密碼、解鎖登入／七枚按鈕碼逐鈕顯隱、表頭新增與批刪走既有「顯示新增」「顯示批刪」兩 prop／記事欄純文字插值）；搜尋卡只准拔除手機與信箱兩欄之格式驗證；表格橫向捲動寬＝各欄寬之和同批改；重設密碼浮層、產密浮層、API 包裝與型別為新增型新檔（檔頭一行標記、不入本表）；前端 MUST NOT 預判包含規則（島 I7）；三語鍵集 MUST 相等；`route:` 樹零新增（`manage_user` route 鍵 upstream 既在）；路由外掛產物四檔本用途零變動（不新增 view 頁）；`src/typings/components.d.ts` 之重算走 §III 生成檔紀律、不入本列；後端拒因鍵落 `en-us`／`zh-cn` 兩檔 locale `backend:` 樹與 `app.d.ts` backend 型節＝既有 I18N-WIRING (ii)(iii) 射程、不隨本列擴列 |
> | **★BASE-WEB-MANAGE-PAGE-WIRING** | (vi) 個人中心改密卡進場 | `src/views/user-center/index.vue`（預估 2 處修改型＋1 塊新增型）／`src/locales/langs/{en-us,zh-cn}.ts`（各預估 1 塊，新增型：`page:` 樹新 top-level `userCenter` 命名空間）／`src/typings/app.d.ts`（預估 1 塊，新增型：`Schema.page` 之 `userCenter` 型節） | 嚴格限父層骨架改寫＋只掛「修改密碼」卡（舊密碼一路、無信箱與手機選項；其餘卡位留白）；改密卡與密碼政策 hook 為新增型新檔（檔頭一行標記、不入本表）；入口沿既有頭像下拉（`user-avatar.vue` 本用途零 diff）；三語鍵集 MUST 相等；`route:` 樹零新增（`user-center` route 鍵 upstream 既在）；路由外掛產物四檔本用途零變動 |
> | **★BASE-WEB-MANAGE-PAGE-WIRING** | (vii) IP 規則頁來源 IP 解鎖入口 | `src/locales/langs/{en-us,zh-cn}.ts`（各預估 1 塊，新增型：`page:` 樹 `manage.ipRule` 子命名空間之資料級補鍵）／`src/typings/app.d.ts`（預估 1 塊，新增型：`Schema.page` 之 `manage.ipRule` 對應型節） | 嚴格限 IP 規則頁表頭前綴插槽之「解鎖來源 IP」鈕（按鈕碼 `ipRule:unlock` 顯隱）與輸入 IP 之彈窗，經與帳號維解鎖共用之同一 API 包裝呼叫解鎖端點之來源維（不套包含規則）；IP 規則頁三檔為 rev6 新增檔、解鎖彈窗為新增型新檔（檔頭一行標記、皆不入本表）；★`manage.ipRule` 補鍵與型節之插入點位於本軌道用途 (i) 既有圈界塊內——本用途以巢狀圈界（塊首塊尾帶 (vii)）承接、(i) 塊首尾不動；三語鍵集 MUST 相等；`route:` 樹零新增；路由外掛產物四檔本用途零變動 |
> | **★BASE-WEB-MANAGE-PAGE-WIRING** | (viii) 角色頁與選單頁按鈕碼顯隱 | `src/views/manage/role/index.vue`（預估 3 處，修改型）／`src/views/manage/menu/index.vue`（預估 3 處，修改型） | 嚴格限表格操作鈕依按鈕碼逐鈕顯隱（角色頁 `role:add`／`role:edit`／`role:delete`；選單頁 `menu:add`〔含新增子選單〕／`menu:edit`／`menu:delete`）、表頭新增與批刪走既有「顯示新增」「顯示批刪」兩 prop；選單回收桶之復原鈕與角色抽屜三顆授權鈕不設碼（其讀寫端點屬封死集）；★同檔雙用途——與 (ii) 並存、標記各帶其用途號；改點落於用途 (ii) 既有修改型標記所涵蓋之行（選單頁表頭開標籤之兩 prop 值）者，於該 (ii) 標記內文同批補述本用途改點、不另立本用途標記（無可載之基線 `原行:`）；角色抽屜、選單彈窗與共用表頭元件本用途零 diff；i18n 零新鍵（locale 與 `app.d.ts` 本用途零 diff）；路由外掛產物四檔本用途零變動 |

**LOGIN-CAPTCHA（L-a）**：(i) 列紀律欄末句「。★用途 (ii)（`formRules` 放寬）**不在本次授權**，延改密端點刀」刪去（凍結位開立之必然後果；前代同批刪句同形），(i) 列之後新增：

> | **★BASE-WEB-LOGIN-CAPTCHA-WIRING** | (ii) 登入表單規則放寬 | `src/views/_builtin/login/modules/pwd-login.vue`（預估 3 處，修改型） | 嚴格限 `formRules` 之帳號名與密碼兩欄由格式正則改必填規則（前端只驗必填、格式判定交後端——設得進的密碼必須登得進）；★MUST NOT 動 `src/constants/reg.ts`（全域正則為其他表單共用）；`register`／`reset-pwd` 兩支 stub 不動；用途 (i) 之 captcha 軟區條件渲染行為與三顆快速登入鈕零變更 |

**I18N (i) 整列改寫（N-a）**：

> | **★BASE-WEB-I18N-WIRING** | (i) 後端 msg 轉譯與錯誤明細轉譯 | `src/service/request/index.ts`（2 處修改型＋2 塊新增型：明細轉譯改寫落既有塊內、不增塊）／`src/locales/langs/{en-us,zh-cn}.ts`（各預估 1 塊，新增型：`page:` 樹新 top-level `passwordPolicy` 命名空間）／`src/typings/app.d.ts`（預估 1 塊，新增型：`Schema.page` 之 `passwordPolicy` 型節） | 單一 helper `translateBackendMsg(msg)`＝`$t` 帶原文 fallback；modal `content` 與 `showErrorMsg` 鏈改走之；未命中 MUST graceful fallback，不得吞錯亦不得顯裸 key；同 helper 亦用於**帶信封 msg 的 HTTP 層錯誤**（如 `5003`／403、`4040`／404）之提示；無信封維持原文（`rev5:B-117` 形）。★錯誤明細轉譯**只限兩鍵**——密碼政策違規（攜違規碼清單、逐碼譯為 `page.passwordPolicy` 子鍵）與設密冷卻（攜剩餘秒數、具名插值）；其餘錯誤信封 `data` 恆 null、仍以純 key 提示；違規子鍵為單一共用命名空間（請求層、即時規則提示與產密元件共用）、三語鍵集 MUST 相等；明細通道射程與受眾＝ADR-00076 |

**I18N (iii) 整列改寫（N-b；spec 所稱「(iii) 開立」＝開立本列原延後之凍結內容）**：

> | **★BASE-WEB-I18N-WIRING** | (iii) Schema 型節與繁中 runtime | `src/typings/app.d.ts`（預估 1 處修改型＋1 塊新增型）／`src/locales/locale.ts`（預估 0 塊，新增型：匯入與對映皆單行形）／`src/locales/naive.ts`（預估 0 塊，新增型：獨立匯入行與兩表各一項皆單行形）／`src/locales/dayjs.ts`（預估 2 處，修改型：預設參數與退路；匯入與對映皆單行形）／`src/locales/index.ts`（預估 1 處，修改型）／`src/store/modules/app/index.ts`（預估 2 處，修改型：預設值與既有標籤；繁中選項為單行形） | 補 `App.I18n.Schema` 之 `backend` **必填**型節；`LangType` 擴 `'zh-TW'`；locale、元件庫（繁中語系與日期語系）、日期庫（`zh-tw`）三處註冊 zh-TW；未選過語言之預設改 zh-TW（`locales/index.ts`、`store/modules/app/index.ts`、`locales/dayjs.ts` 三處；選過者照記）、首次載入即以現行語言同步 `<html lang>`；語言下拉恰三項「简体中文／繁體中文／English」；退路語言不變；零新依賴；`src/main.ts` 本用途零 diff（開發期根元件驗證器之語言判斷不改）；`src/views/pro-naive/ConfigProvider.vue` 本用途零 diff（擴充元件庫只內建簡中與英文兩語，zh-TW 下 pro-naive 示範頁之擴充元件文案退其英文預設＝已知態）。`src/locales/langs/zh-tw.ts` 為 rev6 自有檔（檔頭一行標記、不入本表），以完整 `App.I18n.Schema` 標型＝三語鍵集之型別機器守、各樹隨各用途同批補齊（臺灣用語） |

（N-b 紀律欄之 `ConfigProvider.vue` 零 diff＋已知態＝user 2026-10-05 plan 期親決〔AskUserQuestion〕；入 spec 刻意分岔登記、ADR-00084 決定 10 乙同結論。）

**MANAGE 既有列各一句**：
- (i) 列（M-a）：「解鎖按鈕與其包裝**不在本次授權**（使用者管理頁刀）」→「帳號維解鎖入口屬本軌道用途 (v)、來源 IP 解鎖入口屬用途 (vii)，皆不入本用途」。①（建議）同顆改寫；② 刪句（失去「解鎖不入 (i)」之邊界）；③ 不動（留已兌現之預告）。
- (iii) 列（M-b）：「`src/views/manage/role/index.vue` 本用途零 diff、三鈕不做按鈕碼 gating（門在頁級）」→「`src/views/manage/role/index.vue` 本用途零 diff；角色抽屜三顆授權鈕不設按鈕碼（其讀寫端點屬封死集、非 R_SUPER 連授權現況都載不出；角色頁其餘操作鈕之按鈕碼顯隱屬本軌道用途 (viii)）」。①（建議）同顆改寫——「門在頁級」於 (viii) 落地即不實；② 不動。(ii) 列現算零處「門在頁級」、不涉。

**「兩語」逐處判讀（T-a；憲法現算 14 處＝§III.2 表 8＋Amendment log 6）**：§III.2 表內八處全改（U0 親決取②）——MANAGE (i)～(iv) 紀律欄之「兩語鍵集 MUST 相等」四處改「三語鍵集 MUST 相等」；指稱 upstream 兩檔之授權句四處（(i)(iv) 之「兩語 locale 只在 `route:`」句、(ii)(iii) 之「後端拒因鍵落兩語 locale `backend:` 樹」句）改「`en-us`／`zh-cn` 兩檔 locale」明寫（新列 (v) 之同句同形；I18N (iii) 列不設「兩語 locale」定義句＝N-b）；Amendment log 六處屬史述不改。未取：①指稱句不改、由 I18N (iii) 列定義句釋義（原建議）；③只改四處鍵集句、不補定義句——兩詞並陳無釋義。

**用途號與結構（P-a）**：①（建議）(v) 使用者頁、(vi) 個人中心、(vii) IP 規則頁解鎖、(viii) 角色與選單頁按鈕碼（spec FR-054 與 ★ 軌道逐處登記表已用此號）；② (viii) 併入 (ii)（替代案 8 之棄因）。

**(v) 名單與 upstream 示範頁（P-b）**：`src/views/plugin/excel/index.vue`（seed 選單 `plugin_excel`、R_SUPER 可見）經 upstream `fetchGetUserList` 消費同一端點，getUserList 進場即改吃真資料。①（建議；user 2026-10-05 plan 期親決＝取①）不入名單——本 Amendment 不授權改動該檔（前代同形零 diff），其消費 upstream 宣告型之偏離由 ADR-00083 承載，spec FR-008「upstream 舊函式 MUST NOT 再有畫面消費」之射程讀為使用者管理頁（plan 期 spec 修補）；② 入 (v) 名單改打 rev6 包裝——示範頁非本刀射程、擴大既有檔面。

**範圍欄初值與單元出口程序（P-c）**：
- ①（建議）新列與改寫列計數一律「預估」（依據見下）；觸及 base-web 既有檔之單元出口逐檔實測、與範圍欄應有值比對（實數項取實數；預估項於其承載單元落地後取預估、之前計 0；新增型以全檔各項之和比對）；**不等＝主線判讀**：差額之標記皆在該用途紀律欄射程內＝記入單元收尾紀錄、延至收刀前 PATCH 實數化（不停手）；出現紀律欄射程外之改點＝停手升級。理由：006 刀 `menu-auth-modal.vue` 實得與預估差一塊即須 user 親決（ADR-00072 provenance），計數差本身非授權問題；授權邊界仍由名冊三元組與檔級名單機器守。
- ② 預估＋ADR-00063 程序原樣（不等即停手升級、由 user 定當刀或收刀前 PATCH）。
- ③ 無藍本之項（下標「推估」者）改「不預估」——該等檔失去出口比對基準。

**預估依據**（程序說明、不入憲法；藍本＝rev5 base-web 9833308 同用途之 `原行:` 數與 ` START]` 圈界數；推估＝依改點逐處推算；單行形新增型不入範圍欄＝表外宣告 1）：(v) `user/index.vue` 16＋9、`user-operate-drawer.vue` 22＋16、兩語 locale 各 3、`app.d.ts` 3（藍本；rev6 改列解鎖、刪頁首解鎖彈窗、增灰色保留選項，淨差未定、取藍本）、`user-search.vue` 2（推估：兩欄規則行）；(vi) `user-center/index.vue` 2＋1、兩語 locale 各 1、`app.d.ts` 1（藍本）；(vii) 兩語 locale 各 1、`app.d.ts` 1（推估：解鎖彈窗子樹一塊）；(viii) `role/index.vue` 3（推估：編輯、刪除＋表頭元件開標籤〔Vue 模板屬性行變體〕）、`menu/index.vue` 3（推估：新增子選單、編輯、刪除；表頭兩 prop 值屬 (ii) 標記涵蓋）；LOGIN-CAPTCHA (ii) 3（藍本：必填規則取用行＋兩欄規則行）；I18N (i) `request/index.ts` 2＋2（實數不變：明細轉譯改寫落既有塊內、不增塊）、兩語 locale 各 1、`app.d.ts` 1（推估）；I18N (iii) `app.d.ts` 1＋1（既有 backend 型節 1 塊＋`LangType` 一處）、`locale.ts` 0（匯入與對映皆單行形新增型、不入計數）、`naive.ts` 0（獨立匯入行與兩表各一項皆單行形；lint 擋重複匯入即改「預估 1 處，修改型」並同批改 spec 登記表型別欄）、`dayjs.ts` 2（預設參數與退路；匯入與對映單行形不入計數）、`locales/index.ts` 1（預設值）、`store/modules/app/index.ts` 2（預設值與既有標籤「中文」→「简体中文」；繁中選項單行形）（推估）。

**差異申報**——對 rev6 1.7.1：LOGIN-CAPTCHA (i) 刪延後句（ADR-00026 預告兌現）；I18N (i) 用途名補「與錯誤明細轉譯」、範圍欄 `request/index.ts` 2＋2 實數不變並增 `passwordPolicy` 三面（預估）、刪「（錯誤信封 `data` 恆 null、無明細通道 ⇒ 不建 `translateDetailValue`）」、補兩鍵句（Q18；FR-033／FR-051）；I18N (iii) 用途名「Schema backend 型節」→「Schema 型節與繁中 runtime」、範圍欄 1 塊實數改預估 1＋1 並增五檔、延後句改開立句群（Q4／Q4a；FR-052；ADR-00026 預告兌現）；MANAGE (i) 解鎖句（ADR-00034 預告與 ADR-00042 用途號註記兌現）、(iii) 門在頁級句（Q8；FR-048）、(i)～(iv) 鍵集句四處改三語與指稱句四處改 `en-us`／`zh-cn` 兩檔明寫（T-a）。對 `rev5:ADR 0063` 款二：(v) 用途名「user 管理頁接真（含回收桶、操作下拉、解鎖入口、七碼 gating）」→「使用者管理頁接真（含回收桶、列操作下拉、列解鎖、重設與產密浮層、七碼顯隱）」；範圍欄「兩支＝修改型，逐行 `原行:`」→ 逐檔預估並增 `user-search.vue`（前代經兩向 diff 明文不入；Q17）；紀律欄頁首解鎖彈窗改列操作「解鎖登入」（Q9）、增灰色保留選項等抽屜行為與前端不預判（Q13；FR-024／FR-047）、前代 `user-unlock-modal.vue` 不帶回、新檔改述不寫前代檔名、補 `components.d.ts` 與後端拒因鍵兩句（rev6 (ii) 列同句）；(vi)「改密頁進場」→「改密卡進場」、補「舊密碼一路、無信箱與手機選項」（Q3）；LOGIN (ii) 範圍欄改預估、紀律欄補三顆快速登入鈕（BL-00049）；全列「兩語」→「三語」、「`App.I18n.Schema.page`」→「`Schema.page`」。(vii)(viii) 前代無對應（前代同號屬 `rev5:008` 刀之系統設定頁與稽核頁；rev6 用途號依本刀序重定）。

### 五、§I.7 其餘處、版本與程序

- **MAJOR 射程句（Y-a）**：「八島」→「九島」。**承襲指針表 I 列（Y-b）**：尾補「；rev6 已入憲 v1.8.0（ADR-00074）」；表尾句不動。
- **版本**：版本行改 **1.8.0**、`Last Amended` 改親決日。版本級＝**MINOR**——§V.3「行為島隨刀進場」（島 I＋跨島註新項）、「軌道授權邊界擴展」（MANAGE (v)～(viii)、LOGIN-CAPTCHA (ii)、I18N (i) 新範圍與明細轉譯、I18N (iii) 五檔）、「已入憲 invariant 細項調整」（島 C 第三 reason；H2 補句；鍵集句改三語＝紀律加嚴）三款；島 B 用語、MANAGE (i)(iii) 一句、指稱句改兩檔明寫、跨島總則補例、承襲指針尾註、MAJOR 射程計數＝PATCH 級隨批；非 MAJOR——零入憲不變式方向反轉、零 ★ 軌道授權撤銷（I18N (i)「data 恆 null」改兩鍵例外＝授權擴展）。
- **Amendment log 加 1.8.0 列**（形沿 1.7.0 列）：①島 I 入憲（I1～I5、I7；I6 刻意空缺；rev5 v1.10.0 字面為底、座標改寫依本 ADR 決定一附表）、跨島註補句、跨島總則補例、承襲指針 I 列尾註、MAJOR 射程九島、跨島重審結論要點（I6 隨島 I、J2 待島 J、改密節流與島 E 同向、G5 ★句轉非 vacuous、G2／G6 與 I7 正交）②島 B 用語、島 C 三 reason、H2 補句③§III.2 新增 MANAGE (v)～(viii)、LOGIN-CAPTCHA (ii)（(i) 延後句同批刪）、I18N (i)(iii) 改寫、MANAGE (i)(iii) 各一句、表內「兩語」八處改寫（鍵集句四處改三語、指稱句四處改 `en-us`／`zh-cn` 兩檔明寫）、範圍欄預估、收刀前 PATCH 實數化；版本級句同上；末句記 ADR-00074 同 commit accepted（§V.2 步 4）＋user 親決日期與所在任務。
- **README**：不改——README 已不設憲法版本鏡像（只指 `docs/generated/STATE.md`；現算版本字面 0 處）。
- **本刀 U0 順序**：①前置體檢——本 ADR 所引「現行」原文逐段對憲法現況、不符先改本 ADR；所引單元（首個觸及 base-web 既有檔之單元、繁中 runtime 單元、文件單元、收刀前承載體檢單元）對 tasks 定稿核對；`git -C base-web status --porcelain` 空且 HEAD＝pin；`python3 tools/docsync errata <詞>` 現算後果段種子 ②同一親決輪先定被 I18N (i) 列指向之 ADR-00076 決定款（兩鍵射程與受眾），再呈本 ADR 各題 ③user 逐款親決（一題一問；依賴題先問：I-c→I-d6、T-a→N-b、P-a→P-d1～P-d4／M-a／M-b；P-b 已於 plan 期親決） ④本 ADR 轉 accepted（同顆補親決紀錄）＋Amendment commit ⑤施工前提 ADR 另顆 accepted ⑥其餘施工。ADR-00076 被指向之決定款於其 accepted 前 MUST NOT 改動（確需改動＝停手升級、該指針另走 §V.2）。
- **Amendment commit**：獨立一顆、訊息 `docs(constitution): amend §I.7 島 I＋島 B／C／H 連動＋§III.2 MANAGE-PAGE (v)～(viii)＋LOGIN-CAPTCHA (ii)＋I18N (i)(iii)（1.7.1→1.8.0）`；內容恰為憲法、本 ADR、活書狀態句（S-a）與 generate 產物（DECISIONS-INDEX、STATE；S-a 取①時連同 rev5-blueprint-map）。落地前主線親跑 `python3 tools/fork-delta-lint.py` rc 0 與 `python3 tools/route-artifact-gate.py check` rc 0，關鍵行寫進 commit 訊息；名冊載入新列之變異自證（暫改 (v) 列任一反引號路徑為不含 `/` 之 token → rc 2〔`load_roster` 非路徑 token 斷言；plan 期以合成憲法實跑已見此紅〕→ 存原文寫回）於首個觸及 base-web 既有檔之單元派發前由主線親跑、記入該單元收尾紀錄（SC-012；ADR-00042 決定七前例）。
- **活書狀態句（S-a）**：收錄判準＝活書家族中本 Amendment 一落地即成假述之現在式句；碼註（`auth/enforce.rs` 掛點 doc、`app.d.ts` backend 型節註、`pwd-login.vue` 軟區圈界註、`zh-tw.ts` 檔頭）歸各承載單元、as-built 補寫歸文件單元。①（建議）同顆改：08 frontmatter `rev5_blueprint` 授權慣例值與 §8.3 之「no-escalation 本體＝島 I 承襲指針」兩處改「no-escalation 本體＝憲法 §I.7 島 I7」；10 §10.2 導言「已入憲行為島 A～H（未入憲之島 I／J 目前無情境」改「已入憲行為島 A～I（島 I 情境目前無；未入憲之島 J 目前無情境」、10 frontmatter `§10 品質要求` 值「情境逐已入憲行為島一則」改「情境逐已入憲行為島一則（島 I 情境目前無）」；12 frontmatter `§12 名詞表` 值與收尾句之「屬未入憲之島 I」兩處改「屬島 I」。② 延至文件單元——期間持假述。
- **硬閘**：本顆落地前 base-web 既有檔 MUST 零 diff（git 史可證）；純新增檔本不受閘。
- **親決題索引**（一題一問、首選為建議）：

| 題 | 款 | 建議 | 其他 |
|---|---|---|---|
| I-a 標頭 | 一 | ①完整形 | ②最短形 |
| I-b I6 寫法 | 一 | ①標頭一句、不寫 BL 號 | ②寫 BL 號／③空條目 |
| I-c I7 具名 | 一 | ①`R_SUPER` | ②不具名 |
| I-d1～I-d7 I1～I5、I7、常數行 | 一 | 照候選字面 | 逐條改字 |
| X-a 跨島註補句 | 二 | 照候選字面 | 改字 |
| X-b 跨島總則補例 | 二 | ①補 | ②不動 |
| B-a 島 B 用語 | 三 | 照候選字面 | 改字 |
| C-a 島 C 三 reason | 三 | 照候選字面 | 改字 |
| H-a 島 H2 | 三 | 候選甲（補） | 候選乙（不補） |
| P-a 用途號 | 四 | ①(v)～(viii) | ②(viii) 併 (ii) |
| P-b excel 示範頁 | 四 | ①不入（user 2026-10-05 plan 期親決＝不入） | ②入 |
| P-c 範圍欄與出口程序 | 四 | ①預估＋射程內差額延 PATCH | ②ADR-00063 程序原樣／③無藍本者不預估 |
| P-d1～P-d4 (v)～(viii) 列 | 四 | 照候選字面 | 逐欄改字 |
| L-a LOGIN-CAPTCHA (i) 刪句＋(ii) 列 | 四 | 照候選字面 | 改字 |
| N-a I18N (i) 列 | 四 | 照候選字面 | 改字 |
| N-b I18N (iii) 列 | 四 | 照候選字面 | 改字 |
| M-a MANAGE (i) 解鎖句 | 四 | ①同顆改寫 | ②刪句／③不動 |
| M-b MANAGE (iii) 門在頁級句 | 四 | ①同顆改寫 | ②不動 |
| T-a 「兩語」逐處判讀 | 四 | ①鍵集句四處改三語＋定義句 | ②八處全改／③不補定義句 |
| Y-a MAJOR 射程句 | 五 | 「九島」 | 改字 |
| Y-b 承襲指針 I 列尾註 | 五 | 照候選字面 | 改字 |
| S-a 活書狀態句 | 五 | ①同顆改 | ②延文件單元 |

- **親決紀錄**：user 親決 2026-10-06（007 刀 tasks T002 Amendment 顆）——同一親決輪先定被條文重述或倚賴之他 ADR 決定款十八款：ADR-00076 決定 1／2、ADR-00075 決定 1／3／4／6、ADR-00079 決定 1／3／5、ADR-00084 決定 1／2／3／4／9（決定 10 兩面 plan 期已定、不再呈）、ADR-00086 決定 1～4（逐款一題一問、皆照文）；再依本索引一題一問呈本 ADR 三十題（P-b 已於 plan 期親決、不再呈）＋T-a 連動一題。非建議項二題——I-d1 改字（I1「於交易起手取得」→「於任何列鎖之前取得」：原字面與 ADR-00075 決定 4 之鎖前普通讀未對齊；同批於標頭 rev6 改寫申報補「取鎖時點」、差異附表增列）、T-a 取②（八處全改：鍵集句四處改三語、指稱句四處改 `en-us`／`zh-cn` 兩檔明寫）；T-a 連動＝新列 (v) 紀律欄之同類指稱句同改；N-b 照候選字面但刪「兩語 locale」定義句（隨 T-a② 表內已無該詞）；其餘皆採建議——I-a①、I-b①、I-c①、I-d2～I-d7 照候選字面、X-a 照候選字面、X-b①、B-a 照候選字面（首問因題面錯字作廢、重問後定）、C-a 照候選字面、H-a 候選甲、P-a①、P-c①、P-d1～P-d4 照候選字面、L-a／N-a 照候選字面、M-a①、M-b①、Y-a「九島」、Y-b 照候選字面、S-a①。決定節、差異附表與差異申報、Amendment log 草稿已同步改寫為定稿字面（翻案觸發器第一條），憲法落字逐字取自本 ADR 之定稿字面。

## 後果

- **島 I 方向性面凍結**：拆散 per-user 序列化或改回無鎖 pre-read、拔換發重驗或改 denylist 優先或改每請求判定、拆單一驗證點或把政策掛上登入、矛盾組合改放行、拔遮蔽、拔包含規則或改 fail-open 或改由前端預判、把受約束寫端移出射程——皆 MAJOR；常數留 ADR／活書可調。
- **兌現窗**：條文為規範面，as-built 於本刀各單元落地前未兌現——島 C 第三 reason 與 I2 三向分派（踢除與換發單元）、I1／I4／I7（使用者寫端單元）、I5（密碼面單元；其中 DTO 遮蔽句之既有反例＝`handler/auth/login.rs` 之 `LoginReq` 以 derive 形 Debug 含密碼欄，同單元改遮蔽形並配機器釘，前代 as-built 同形自承）、H2 補句（取甲時；選單刪碼守門單元）、「三語鍵集 MUST 相等」（繁中 runtime 單元起以 Schema 標型守；之前 `zh-tw.ts` 只有 backend 子樹）；收刀前承載體檢單元複核全數已落地。grace 冪等窗不重驗屬已知殘窗（既發對已隨撤票失效、無新簽發）。
- **ADR 關係**：ADR-00063 翻案觸發器兩條由決定二答覆（邊界本體＝ADR-00075）；ADR-00003 之 I6 處置兌現（J2 待島 J）；ADR-00026（LOGIN-CAPTCHA (ii)、I18N (iii) 延後）、ADR-00034（解鎖延後）、ADR-00042 背景附記（解鎖取下一可用用途號）之預告於本顆兌現（accepted body 不改、讀時併讀）；本 ADR 不 supersede 任何 ADR。
- **§III.2 授權名冊**：MANAGE 用途 4→8、LOGIN-CAPTCHA 1→2、I18N 3（(i)(iii) 改寫）；表列 12→17；軌道數不變（`tools/fork-delta-lint.py` 名冊仍八名）；`tools/route-artifact-gate.py` 讀面不變；對賬腿受檢面＝修改型三元組 32、新增型逐檔 14（U0 以定稿字面重跑覆核）。
- **硬閘解除點**：本顆落地即解除；新列計數由 P-c 程序承擔至收刀前 PATCH。
- **回填義務**：新增與改寫各列之預估值於收刀前承載體檢單元以 PATCH Amendment 實數化（配號＝當下下一號；前例 ADR-00072；RL-0015）。
- **帳本**：I6 空缺之承載＝BL-00140；BL-00065 題 b 由 I2 兌現、BL-00091 由 (v)(vii) 授權、BL-00138① 由 I18N (iii) 授權，依 spec FR-060 於收刀 `backlog_done`。
- **errata 面**（U0 以 `python3 tools/docsync errata <詞>` 現算、逐處分流本顆改／他單元改／史料與 accepted 不動／BACKLOG 收刀刪列；種子＝「八島」「未入憲」「承襲指針」「島 I」「兩語」「門在頁級」「頁級」「不在本次授權」「不在授權內」「延改密端點刀」「延前端 UI 刀」「使用者管理頁刀」「恆 null」「兩 reason」「踢除」「1.7.1」）：憲法自身本顆改（MAJOR 句「八島」、島 B「踢除」、島 C「兩 reason」、§III.2 延後句與「恆 null」「門在頁級」、表內「兩語」八處〔T-a〕；1.7.0 log「八島」、§IV 第 9 題「未入憲」通則、§I.7 進場規則「踢人雙通道分離」泛指例示皆不動）；活書狀態句本顆改（S-a）；活書 as-built 歸文件單元（06／10 新增島 I 情境並補 frontmatter、島列舉改「A～I」〔收回 10 導言之 S-a 暫改句〕、06 島 C 情境「兩 reason」、06 與 08 之「三鈕不接按鈕權限碼（門在頁級）」、12 使用者域詞組與「頂替」「踢除」消歧）；碼註歸各承載單元——`menu/index.vue` 用途 (ii) 標記之「門是頁級」與 `role-operate-drawer.vue` 用途 (iii) 圈界註之「門在頁級」（角色與選單頁按鈕碼單元）、`pwd-login.vue` 圈界註之「(ii) formRules 放寬不在授權內」（登入表單單元）；BACKLOG「延前端 UI 刀」「使用者管理頁刀」各一處屬 BL-00138／BL-00091 本文、收刀刪列。
- **跨島**：島 J 仍未入憲；承襲指針表 J 列與表尾句、§I.7 段首括號句不動。

## 翻案觸發器

- U0 親決改動任一候選字面（含選項題取非建議項）＝本 ADR 於 accepted 前同步改寫決定節、差異申報與 Amendment log 草稿，使 accepted body 與憲法落字逐字一致。
- 被 I18N (i) 列指向之 ADR-00076 決定款於其 accepted 前須改動＝停手升級；指針另走 §V.2（PATCH 級 ADR＋獨立 `docs(constitution): amend` commit）。
- ★收刀前 §V.2 PATCH Amendment MUST 將本 ADR 新增與改寫各列之預估值實數化（表外宣告 1 例外路徑之回填義務）；單元出口出現紀律欄射程外之改點＝停手升級。
- 首登強制改密或密碼經手判定兌現（BL-00140 觸發）＝Amendment 回填 I6、標頭空缺句同批改。
- 包含規則射程擴至角色域、IP 域或授權回收桶復原＝I7 射程 Amendment＋ADR-00075 複核。
- 錯誤明細通道擴第三鍵＝ADR-00076 判準重驗＋I18N (i) 列 Amendment。
- 出現第四種 denylist reason＝島 C 第三點 Amendment、I2 三類對應複核。
- 政策鍵缺鍵、不可解析或越界之處置方向須凍結（現屬 ADR 級、不入條文）＝I5 fail-* 句擴列。
- 換發改多行程部署或出現每請求活性判定需求＝I2 方向重議（MAJOR）。
- 第四語進 runtime＝鍵集句與 I18N (iii) 列 Amendment。
- `src/views/plugin/excel/index.vue` 或名單外 base-web 既有檔非動不可＝回 §III.2 走 §V.2。
- upstream rebase 改動新列各檔之標記處數＝範圍欄同批更新（表外宣告 1）。
