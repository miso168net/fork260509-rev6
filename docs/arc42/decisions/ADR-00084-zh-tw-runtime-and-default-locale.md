---
id: "ADR-00084"
title: 繁中介面接上 runtime 並預設繁中——`LangType` 擴 `zh-TW`、locale／元件庫／日期庫三處註冊、未選過語言預設 zh-TW、語言下拉三語、`zh-tw.ts` 由治理錨點孤立檔改為 `App.I18n.Schema` 標型之完整 locale（續行並 supersede ADR-00039：譯文之家三檔不變）；ADR-00050 決定 1「zh-tw 不在對照面」之前提改述；繁中機器檢查之載體＝新碼面閘 `tools/zh-tw-lint.py`（四腿、讀面 (a)）；開發期根元件驗證器不改＝已知態；候選兩款未定案
date: 2026-10-05
status: proposed
supersedes: []
superseded_by: []
provenance: "007-user-password-admin 之 spec FR-052（繁中 runtime）、FR-054（fork-delta 檔集）、FR-056⑪、FR-059（「zh-tw 不接 runtime／孤立檔」與憲法「兩語」之假述掃除）、FR-060（BL-00138①由本刀兌現）、FR-065（CDP 對照顯式設簡中、繁中畫面驗收依 GR5）、US5 AS1～AS5、SC-009、Edge Cases「繁中介面」、★ 軌道逐處登記表之 `BASE-WEB-I18N-WIRING(iii)` 各列與 `zh-tw.ts` 列、刻意分岔登記表「預設語言與語言下拉」「繁中畫面」兩列；brainstorm §0 Q4（007 接上繁中；非建議項）／Q4a（預設改為繁中）／GR2（「頂替」與「踢除」用語）／GR5（機器檢查＋AI 逐頁審讀＋user 抽查）、主線工程判斷⑩⑯、§3 §3 前端節繁中 runtime 條；plan 期主線定案（開發期根元件驗證器不改＝已知態、★ 軌道登記表刪該候選列；繁中機器檢查之載體＝新碼面閘）；被續行面＝ADR-00039（其決定 1 續行之 ADR-00029 決定 5「`zh-tw.ts` 為治理錨點孤立檔」即本 ADR 改寫之款；rev6 無部分翻案機制＝ADR-00011 決定 5，整顆續行）；改述面＝ADR-00050 決定 1（所續行之 ADR-00049 決定 1 末句）；BL-00138①；ADR-00055 決定 3（新讀子庫工作樹之碼面閘同刀標讀面型）、ADR-00019 決定 3／決定 4（hook 段零條件判斷、tracked 面缺席方向不類推）、ADR-00041 決定 2（跨刀活體契約收錄判準）、ADR-00071 決定 6②（碼面閘 `check` 不連帶跑自測之一派）；前代無藍本——`rev5:` 終態 `LangType` 為兩語、`zh-tw.ts` 只有 backend 樹（`rev5:R3-15` 之延後未兌現）；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research R21（ADR 配號與親決時點表）；accepted 同顆於 supersedes 補 ADR-00039 並改 ADR-00039 狀態"
tags: [i18n, base-web, code-gate, decision-reversal, user-password-admin]
---

## 背景

- 現況量測（2026-10-05、base-web pin `fb4dac2`；只供背景、施工以當下現算為準）：
  - `App.I18n.LangType`＝`'en-US' | 'zh-CN'`（`src/typings/app.d.ts`）。語系註冊三處——`src/locales/locale.ts`（訊息字典）、`src/locales/naive.ts`（元件庫語系與日期語系）、`src/locales/dayjs.ts`（日期庫語系對映）——皆以 `Record<App.I18n.LangType, T>` 形標型（鍵＝語系型別全集）、各只列兩語。
  - 未選過語言之預設 `zh-CN` 散住三處：`src/locales/index.ts` 之 `createI18n` 起始語言、`src/store/modules/app/index.ts` 之 `locale` 初值、`src/locales/dayjs.ts` 之參數預設與退路。語言下拉 `localeOptions` 兩項（`中文`／`English`）。退路語言 `fallbackLocale: 'en'`。
  - `src/locales/langs/zh-tw.ts` 共 66 行、裸 object、只含 backend 子樹（鍵集＝`MSG_KEYS`），檔頭自述「治理錨點孤立檔、不接 runtime、不註冊 LangType」；`zh-cn.ts` 855 行、`en-us.ts` 867 行皆以 `const local: App.I18n.Schema` 標型。字串值所用之相異漢字（剝行註解、以單引號字串粗算）：`zh-cn.ts` 約 535 個、`zh-tw.ts` 約 200 個。
  - `src` 下帶 `'zh-CN'` 字面之檔恰 8 支：上列註冊三支、預設三處之兩支（`locales/index.ts`、`store/modules/app/index.ts`；`dayjs.ts` 已計）、`typings/app.d.ts`，另兩支不在 spec ★ 軌道登記表——`src/main.ts`（開發期根元件驗證器以 `getLocale() === 'zh-CN' ? 'zh' : 'en'` 判提示語言）與 `src/views/pro-naive/ConfigProvider.vue`（pro-naive 示範頁以 `appStore.locale === 'zh-CN' ? zhCN : undefined` 選元件庫語系）。
  - 依賴：naive-ui 2.44.1 內含 `zhTW`／`dateZhTW`；dayjs 1.11.20 內含 `locale/zh-tw`；pro-naive-ui 3.2.2 只帶 `zh-cn`／`en-us` 兩語系、`locale` 未給時退回 `enUS`。`index.html` 之 `<html lang>` 靜態為 `zh-CN`，執行期只在 `setLocale`（切換語言）時改寫。
- 憲法 §III.2 ★`BASE-WEB-I18N-WIRING` (iii) 列明文「`LangType` 擴充／locale 註冊／`zh-tw.ts` 標型重構不在本次授權，延前端 UI 刀」；刀序表無此刀，BL-00138① 以本刀 brainstorm 起手為觸發。brainstorm Q4 user 拍板本刀接上（非建議項）、Q4a 拍板預設改為繁中；Amendment（ADR-00074）開立 (iii) 新用途並把各列「兩語鍵集 MUST 相等」改三語。
- ADR-00039 決定 1 續行 ADR-00029 決定 1～5，其中決定 5 定「`zh-tw.ts`＝治理錨點孤立檔（裸 object、不接 runtime、不註冊 `LangType`）」；接上 runtime 後此款失真，rev6 無部分翻案機制 ⇒ 本 ADR 整顆續行 ADR-00039。
- ADR-00050 決定 1（所續行之 ADR-00049 決定 1 末句）「`zh-tw.ts` 不接 runtime、不在對照面，不隨改」：結論（繁中不在 rev5 對照面）續真、前提（不接 runtime）失真。
- 繁中畫面無 rev5 基準（rev5 終態只兩語）。GR5 定驗收形＝機器檢查（型別、簡體殘字掃描、用語表）＋AI 逐頁審讀＋user 抽查；其中型別由前端型別檢查承擔，簡體殘字與用語兩項 rev6 無現成載體。GR2 定會話用語：單一會話被別處登入擠掉＝「頂替」、管理員結束他人全部會話＝「踢除」，程式內原因值（`kicked`／`admin_kick`）不改。

## 決策驅動因子

- 註冊完整性要有機器守、不靠人記（漏一處＝執行期缺語系、畫面混語）。
- 三語鍵集相等要有機器守（本刀起每刀三語同批）。
- 譯文之家單一（RL-0049）：三檔各為該語之家不變、不另立譯文表。
- 繁中用字與用語要有持續訊號（每刀新增譯文），且字表完備由機器保證、不靠記憶增補。
- 零新依賴；base-web 改動面只落 Amendment 授權之 I18N (iii) 檔集與本刀各用途檔集。
- 開發期提示與 upstream 示範頁之語系行為不擴授權面，除非 user 判定其為產品面缺陷（見決定 10 候選兩款）。

## 考慮過的替代案

1. **不接 runtime、立 won't-fix ADR**（取證期建議案；`rev5:` 終態同形）：brainstorm Q4 user 否決（非建議項）。否決。
2. **接 runtime、預設仍簡中**：brainstorm Q4a 否決。否決。
3. **`zh-tw.ts` 維持裸 object、以 msg-key-gate 擴全樹比對取代型別**：等於另寫第二份全樹解析器、與 TS 型別重複；`App.I18n.Schema` 標型即三語鍵集之機器守。否決。
4. **繁中檢查只靠 AI 審讀與 user 抽查、不立閘**：一次性、後刀新增譯文無持續訊號；GR5 明定機器檢查為三件之一。否決。
5. **簡體檢查採單一「簡化字黑名單」**：完備性靠記憶增補、漏列之字靜默放行。否決（改採分類兩表＋完備腿，決定 7）。
6. **簡體檢查改用外部轉換套件或字典**：新依賴、pre-commit 須零網路零安裝；違零新依賴。否決。
7. **閘以 rust 或 node 實作**：rust 側須容器（rust-api 容器之掛載不含 base-web 樹）、node 側須 base-web 容器；pre-commit 常跑鏈要求零 docker。否決。
8. **`src/main.ts` 驗證器改判「是否中文」**：該提示屬開發期、非產品面；外掛只有 zh／en 兩語；免動近 12 月 upstream 有改動之檔（12m 2／24m 3、修改型再升一級＝高）。否決（決定 9）。

對所選方案跑同一反例（RL-0013）：
- 「漏註冊一處」可否發生？三處註冊皆以 `Record<App.I18n.LangType, T>` 形標型，`LangType` 擴 `zh-TW` 後缺鍵即前端型別檢查紅。成立。
- 「`zh-tw.ts` 缺鍵或多鍵」？`App.I18n.Schema` 標型使缺鍵為型別錯、物件字面多餘屬性檢查使多鍵亦錯；backend 子樹另由 msg-key-gate 對 `MSG_KEYS` 逐檔雙向全等。成立。
- 「簡化字混入而該字不在任何表」？字表完備腿要求 `zh-tw.ts` 每字皆已分類、未分類即紅。成立。殘餘：腿②只保證每字皆已歸類、不驗歸類正確——任一字（不論首見 `zh-cn.ts` 或 `zh-tw.ts`）被誤歸 `APPROVED_CHARS` 機器皆抓不到，由表值 diff 審查、AI 逐頁審讀與 user 抽查承接；一對多簡化字（只／隻、里／裡、后／後、台／臺等）在互斥兩表下只能擇一歸類，表值建立時逐字記取捨（歸 `SIMPLIFIED_CHARS` 者合法用例入 `EXEMPT`）；擴讀 `zh-cn.ts` 之效益＝新字必被逼出分類、不防誤歸（記入後果）。
- 「頂替與踢除混用」？會話用語腿以鍵路徑判定（決定 7④）。成立。

## 決定

（草稿；user 親決於 U0 施工前提顆；親決輪後依結果改寫本節並補親決紀錄。決定 10 兩面已於 plan 期定案：甲＝主線定案、乙＝user 2026-10-05 親決。）

1. **語系型別與三處註冊**：`App.I18n.LangType`＝`'en-US' | 'zh-CN' | 'zh-TW'`（修改型）；`locale.ts` 註冊 `'zh-TW': zhTW`（`./langs/zh-tw`）、`naive.ts` 註冊 naive-ui `zhTW` 與 `dateZhTW`、`dayjs.ts` 匯入 `dayjs/locale/zh-tw` 並對映 `'zh-TW': 'zh-tw'`（皆新增型）。三處之 `Record<App.I18n.LangType, T>` 形標型即註冊完整性之機器守，不另立閘。零新依賴（版本見背景）。
2. **未選過語言預設 zh-TW**：前述三處之 `zh-CN` 預設與退路一律改 `zh-TW`（修改型、各逐行 `原行:`）；已選過者照 `lang` 儲存值（`localStg`）；`fallbackLocale` 不變（spec Edge Cases「退路語言設定不變」）。
3. **語言下拉三語**：`localeOptions`＝`[{label:'简体中文',key:'zh-CN'},{label:'繁體中文',key:'zh-TW'},{label:'English',key:'en-US'}]`（項序即此；`中文` 標籤改寫屬修改型）。
4. **`zh-tw.ts` 改為完整 locale**：形同 `zh-cn.ts`／`en-us.ts`——以 `const local: App.I18n.Schema` 宣告全樹物件並 `export default local`——全樹譯文採臺灣用語；既有 backend 子樹保留、其錨 `  backend: {` 續獨佔一行（msg-key-gate 右源錨）；檔頭一行改述本檔定性（rev6 自有檔、`BASE-WEB-I18N-WIRING(iii)` 新增型、不入名冊；「治理錨點孤立檔」與「延前端 UI 刀」兩句刪除）。三語鍵集相等＝型別（全樹）＋msg-key-gate（backend 子樹）雙守。
5. **ADR-00039 之續行**（逐決定照錄處置）：
   - ADR-00039 決定 1（續行 ADR-00029 決定 1～5）：ADR-00029 決定 1～4 原意續行（形制＝逐檔雙向全等、無白名單；Biz 構造點守衛兩形；承載＝`tools/msg-key-gate.py` 與其接線名冊；與 ADR-00017 之射程關係）；ADR-00029 決定 5 改寫為「`zh-tw.ts`＝runtime 註冊之完整 locale（`App.I18n.Schema` 標型）、仍是右源之一與繁中譯文之家，鍵集紀律與另兩檔同」。
   - ADR-00039 決定 2（譯文之家＝三檔各自 backend 子樹、不另立譯文表）原文續行。
   - ADR-00039 決定 3（鍵數不手抄）原文續行。
   - ADR-00039 決定 4（現在式面引用改指）原文續行；本 ADR accepted 後，現在式面引 ADR-00039 之處（RUNBOOK §12 碼面閘表 msg-key-gate 列之「根據 ADR」欄、活書、碼註、標記註解）改指本 ADR。
6. **ADR-00050 決定 1 之改述**：ADR-00050 決定 1 所續行之 ADR-00049 決定 1 末句（ADR-00049 已由 ADR-00050 supersede、屬史料；現行承載＝ADR-00050 決定 1）之結論「繁中不在 rev5 對照面、不隨 rev5 措辭改」續真；其前提自本 ADR 起改讀為「rev5 無繁中 runtime 基準」（非「不接 runtime」）。繁中拒因譯文以臺灣用語轉寫 zh-cn 之已定語意、驗收依決定 8。ADR-00050 不 supersede（其決定內容不變、只前提之理由換句）；讀 ADR-00050 決定 1 時併讀本款。
7. **繁中機器檢查載體＝新碼面閘 `tools/zh-tw-lint.py`**（python 標準庫、零 docker、零網路、毫秒級）：
   - **掃描面**：`base-web/src/locales/langs/zh-tw.ts` 匯出物件之全部字串值（鍵名與註解不掃）；完備腿另讀 `base-web/src/locales/langs/zh-cn.ts` 之字串值。解析＝剝註解、brace 配對後自物件根攤平為「鍵路徑→字串值」；物件根＝檔內首個 `const <名>(: <型>)? = {` 或 `export default {` 之開括號（兩形皆認、皆缺＝rc 2；現行 `zh-cn.ts`＝`const local: App.I18n.Schema = {…}`＋末行 `export default local;`）；與 msg-key-gate（以 `backend: {` 錨前最近之未配對 `{` 為外層物件）各持解析、互不共用。
   - **四腿**（任一腿命中＝rc 1，逐項指名鍵路徑與字或詞並附建議）：
     - ①**簡體殘字腿**：字串值中屬 `SIMPLIFIED_CHARS`（工具常數：簡化字→正體字對照）之字＝紅。
     - ②**字表完備腿**：`zh-tw.ts` 與 `zh-cn.ts` 字串值所用之 CJK 統一表意文字（含擴充區），每字 MUST 屬 `SIMPLIFIED_CHARS` 之鍵或 `APPROVED_CHARS`（工具常數：已審為正體或繁簡同形之字）；未分類＝紅（指名字與首見檔、鍵路徑）。每刀新增譯文之新字由本腿逼出分類；兩表相交＝rc 2（表本身受損）。
     - ③**大陸用語腿**：`zh-tw.ts` 字串值含 `MAINLAND_TERMS`（工具常數：大陸用語→臺灣用語）任一詞＝紅。
     - ④**會話用語腿**（GR2）：「踢」字只准出現於 `ADMIN_KICK_KEYS`（工具常數：管理員踢除語境之鍵路徑集，至少含 `backend.auth.session.kickedByAdmin` 與使用者頁之踢除相關鍵；頁面鍵路徑依本刀 contracts code-gates §1.2「page 新鍵名冊」照列）；`backend.auth.session.kicked`（單一會話被頂替）之值 MUST NOT 含「踢」與「管理員」；`backend.auth.session.kickedByAdmin` 之值 MUST 含「管理員」、MUST NOT 含「頂替」；`ADMIN_KICK_KEYS` 之 page 鍵 MUST 含「踢除」；全樹不得出現「踢出」「踢掉」「踢下線」「擠下線」「擠掉」「頂掉」（統一為「踢除」「頂替」）。程式內原因值不在射程（GR2）。
   - **空值檢查**：`zh-tw.ts` 字串值為空字串＝rc 1（指名鍵路徑；三語 Schema 型別不擋空值）。
   - **具名白名單 `EXEMPT`**（工具常數；逐項＝鍵路徑×字或詞×理由；只對①③生效）：不得取自 args／env／讀檔；幽靈項（該鍵已不存在、或其值已無該字詞）＝紅；項數由自測釘住——增列須同批改自測斷言、於 diff 現形。
   - **表值**：`SIMPLIFIED_CHARS`／`APPROVED_CHARS`／`MAINLAND_TERMS`／`ADMIN_KICK_KEYS` 之初值於繁中閘單元建立（兩字表以兩檔現有用字逐字分類；用語表以臺灣用語為準，例：信息→訊息、默認→預設、設置→設定、菜單→選單、登錄→登入、網絡→網路、視頻→影片、數據→資料、軟件→軟體、屏幕→螢幕、用戶→使用者）；表值屬資料、實作期定（理由：隨全樹譯文量而定，腿②保證字表完備）。
   - **退出碼與缺席語意**：rc 0 綠｜rc 1 任一腿命中、空值或白名單幽靈（各項合併列出）｜rc 2 結構異常（兩檔任一缺席、物件根兩形皆缺或 brace 不配對、掃描面空集合＝RL-0051、兩字表相交、白名單項壞形）｜rc 64 用法錯。tracked 面缺席一律 rc 2、不設具名跳過（ADR-00019 決定 4 方向不類推）。子命令 `check`（預設）／`test`（離線合成 fixtures）；`check` 不連帶跑自測（ADR-00071 決定 6② 所述前一派：自測只用合成 fixtures、本體 staged 時 `for` 自測迴圈必跑）。
   - **讀面型（ADR-00055 決定 3）**：兩檔皆 `base-web/src/locales/langs`＝(a) 閘面內（pre-commit submodule-sync 段之 base-web 閘面含 `src/locales/langs`）、延後至下次 base-web pin bump 補抓。
   - **接線四處（同一單元落地）**：
     - ①外層 `.githooks/pre-commit` 新增條件段 `zh-tw-lint`：`base-web` gitlink 變動（pin bump）或工具本體 staged 時跑 `check`；段內零條件判斷、不設跳過分支（ADR-00019 決定 3）。★`zh-tw.ts` 住子庫、外層 staged 面只看得到 gitlink；子庫 hook（`.githooks-submodule/pre-commit`）只做機密掃描、不掛本閘。
     - ②自測入 pre-commit 之 `for t in` 自測迴圈（`check_hook_wiring` 強制碼面閘表全員入迴圈）。
     - ③bootstrap 名冊由 tracked 檔推導自動納入（不手增名冊行）。
     - ④RUNBOOK §12 碼面閘表一列（工具檔／守什麼／觸發時機含缺席語意與 (a)／根據 ADR＝本 ADR，並列 ADR-00055 決定 3、ADR-00019 決定 3／決定 4）——GT-12 腿雙向對賬；「根據 ADR」欄只收 accepted 號 ⇒ 本 ADR 須不晚於接線單元同顆 accepted（預定 U0）。
     - 連動名冊同顆改齊：`tools/docsync/tests/test_hook_wiring.py` 之 `SEGMENTS`／`MIRROR_WORDS` 與三處人寫鏡像行（pre-commit 檔頭段序、README 樹 `.githooks/` 列、README 守門條目）、README 工具樹、RUNBOOK §12 工具鏈速查表一列、活書 05 建構塊視圖 `tools/` 列；數量詞「七支碼面閘」（pre-commit 碼面閘段首句、`tools/bootstrap.sh` 名冊註解）與「十三條件段」（`test_hook_wiring.py` 模組 docstring）同批改，處數以 `python3 tools/docsync errata <詞>` 現算；逐項落點由本刀 contracts（code-gates）定。
   - **跨刀活體契約**：判準、四表與白名單之語意、退出碼、讀面型入 `docs/ops/reference-src/code-gate-contracts.md` 新節（ADR-00041 決定 2 收錄判準成立：每刀三語同批、字表與用語表隨刀前進）；RUNBOOK §12 該列之契約指針指該節。
   - **碼面閘不佔 GT 名額**：不入 GATES.md、治理閘數維持 12。
   - **一正一反自證（RL-0080）**：正＝真 repo `check` rc 0；反（合成）＝四腿各一紅案、空值紅案、白名單生效綠與幽靈紅、兩表相交 rc 2、掃描面空 rc 2、物件根兩形各一綠案、白名單項數恆定斷言；反（真檔暫改）＝於 `zh-tw.ts` 一個字串值植入一個簡化字 → `check` rc 1 且指名該鍵與字 → 以原檔寫回還原 → `git -C base-web status --porcelain` 回基準態（RL-0005）。變異打在判準上（拆掉腿①之比對 ⇒ 合成紅案轉綠＝自測紅），紅證以 rc 與指名字面為準。
8. **繁中驗收（GR5）與 CDP 對照**：繁中畫面之驗收＝本閘綠＋前端型別檢查綠（三語 Schema）＋AI 逐頁審讀紀錄涵蓋全部接真頁面＋user 抽查並記錄（SC-009）；繁中畫面無 rev5 基準、屬刻意分岔（spec 刻意分岔登記表兩列）。CDP 三方對照之步驟兩側一律顯式設簡中（22080 側為 spec 明文；32080 側同設＝提示文案逐項對照之前提；`tools/orchestration/cdp.mjs` 現無語言設定、由走查腳本寫入 `lang` 儲存值）。
9. **已知態：開發期根元件驗證器**：`src/main.ts` 不改——zh-TW 下開發期根元件驗證器之提示語言落英文；該檔不入 ★ 軌道登記表（spec 該候選列刪除、登記表 19 列→18 列）。理由見替代案 8。
10. **首開語言之兩面（plan 期定案）**：
    - **甲 首次載入之 `<html lang>`（plan 期主線定案＝同步）**：未選過語言之瀏覽器首開為繁中，但 `<html lang>` 仍為 `index.html` 之靜態 `zh-CN`（執行期只在 `setLocale` 切換語言時改寫）；瀏覽器依此屬性為 CJK 字形選字型（例：Windows 上簡中字型與繁中字型字面不同）。定案＝`src/locales/index.ts`（已屬 I18N (iii) 檔集）之 `setupI18n` 內以現行語言同步 `<html lang>` 一行（單行形新增型、不入範圍欄計數；spec Edge Cases「首開即同步」）。
    - **乙 pro-naive 示範頁（user 2026-10-05 plan 期親決＝記已知態、不改）**：`src/views/pro-naive/ConfigProvider.vue` 於 zh-TW 下取 `undefined`、pro-naive-ui 退 `enUS`＝該類示範頁之元件內建字串為英文、頁面其餘文字為繁中；pro-naive-ui 3.2.2 無繁中語系。定案＝記已知態、該檔零 diff、入 spec 刻意分岔登記；GR5 逐頁審讀與 CDP 排除其元件內建字（改為對映簡中＝繁中畫面出現簡體字、違 GR5；自建繁中語系物件＝新譯文面、不在 spec 範圍）。
11. **憲法連動與時序**：本 ADR 之 base-web 施工以 ADR-00074（Amendment：I18N (iii) 新用途、各列「兩語」改三語）accepted 為前提；本 ADR 不承載條文字面。本刀起每刀三語同批（`page:`／`route:`／backend 三樹三檔同 commit）；BL-00138① 由本 ADR 兌現、② 移交 BL-00141。

## 後果

- 首次開啟為繁中、選過照記；語言下拉三項；元件庫與日期元件隨語言切換（US5 AS1～AS3）。
- 三語鍵集相等由前端型別檢查（全樹）與 msg-key-gate（backend 子樹）雙守；每刀新增 `page:`／`route:` 鍵須三檔同批，否則型別檢查紅。
- 繁中用字、用語與會話用語自本刀起有 commit 級機器訊號；字表與用語表隨刀增長，白名單增列於 diff 現形。
- 殘餘：腿②不驗歸類正確——任一被誤歸 `APPROVED_CHARS` 之簡化字（不論首見何檔）機器抓不到，由表值 diff 審查、AI 逐頁審讀與 user 抽查承接（GR5 三件之二）；一對多簡化字逐字記取捨（歸 `SIMPLIFIED_CHARS` 者合法用例入 `EXEMPT`）。
- 現在式假述之同單元改寫（RL-0011；種子四形皆跑、處數以 `python3 tools/docsync errata <詞>` 現算、改完復掃）：「治理錨點孤立檔」「孤立檔」「不接 runtime」「延前端 UI 刀」「不在本次授權」（I18N (iii) 語境；憲法條文由 Amendment 改）、「兩語」（憲法各處由 Amendment 改、活書與碼註同批）、「zh-tw 不在對照面」；已知命中面＝`zh-tw.ts` 檔頭三行、`src/typings/app.d.ts` 之 I18N (iii) 圈界碼註、活書 08 之 i18n 段。史料面（specs、brainstorms、reviews、LESSONS、ADR 檔）不動。
- 現在式面引 ADR-00039 為現行依據之處改指本 ADR（決定 5 末項）；2026-10-05 已知命中面＝RUNBOOK §12 碼面閘表 msg-key-gate 列、活書 08、grafana 面板 `deploy/grafana-provisioning/dashboards/json/backend-msg-dict.json`、base-web 五處標記註解（三檔 locale、`src/service/request/index.ts`、`src/typings/app.d.ts`）——各隨其所屬檔之授權用途改、處數以 `python3 tools/docsync errata ADR-00039` 現算。
- 新碼面閘一支（碼面閘表 9→10 列）；★ADR-00032 翻案觸發器①（碼面閘 ≥8 支＝另立生成檔並翻案）本刀前 9 支即已成立而未處置、本刀後 10 支——複核結論＝本 ADR 不處置（射程為繁中閘、非碼面閘名冊之載體），轉 BL-00142（另立生成檔並翻案 ADR-00032，或立新 ADR 續行人寫表並重設觸發條件；觸發＝下一支治理維護批起手前或碼面閘再增一支時）；其施工面另涉 pre-commit、`test_hook_wiring`、README、RUNBOOK §12 兩表、活書 05、`code-gate-contracts.md` 新節，逐項由本刀 contracts（code-gates）與 tasks 收。
- 本閘非「隨遷工具」（rev5 無藍本）：rev6 新寫、註解 rev6 語境。
- 代價：每刀須維護兩字表與用語表（新字逼出分類）；`zh-cn.ts` 新字未分類亦令本閘紅（完備腿之刻意取捨）。

## 翻案觸發器

- 第四語系進場、或 `LangType` 改由設定產生 ⇒ 複核決定 1～3 與本閘之掃描面。
- 譯文改由外部翻譯平台管理（locale 檔成為產物）⇒ 權威移轉、以新 ADR 定（沿 ADR-00039 翻案觸發器）。
- 繁中閘四腿之任一實際漏網一次（以 AI 審讀或 user 抽查抓到之簡體字、大陸用語或會話用語混用為證）⇒ 複核決定 7 之判準與表之分類紀律。
- pro-naive-ui 升版帶繁中語系 ⇒ 複核候選乙之定案。
- upstream 改寫根元件驗證器之語言判斷或外掛增繁中 ⇒ 複核決定 9。
- `zh-cn.ts` 新字未分類之紅成為常態阻擋（連續三刀以上各有一次以上）⇒ 複核腿②之讀面是否收窄至 `zh-tw.ts`。
