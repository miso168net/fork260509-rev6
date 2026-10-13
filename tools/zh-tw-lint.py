#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/zh-tw-lint.py — 碼面閘：繁中 locale 之簡體殘字、字表完備、大陸用語、會話用語與空值（007 刀 U16；ADR-00084 決定 7；
spec FR-052、SC-009、GR2／GR5 之機器面；rev6 新寫、rev5 無藍本；行為契約＝docs/ops/reference-src/code-gate-contracts.md 之 zh-tw-lint 節；
名冊＝RUNBOOK §12 碼面閘表）

子命令：
  check   （預設）讀 base-web/src/locales/langs/zh-tw.ts（四腿與空值）與同目錄 zh-cn.ts（只供腿②）兩固定路徑後判定；
          不收路徑引數、不連帶跑 self-test；綠時逐列印出仍生效之具名豁免
  test    離線 self-test（暫存目錄與記憶體內合成 fixtures＋對本檔自身常數與原文之釘；零 docker、零網路、不讀真 repo）

守什麼：
  zh-tw.ts 是 runtime 註冊之完整繁中全樹（ADR-00084）。三語鍵集相等由 `App.I18n.Schema` 標型與前端型別檢查守，內容面卻無人守——
  譯文混進簡化字、大陸用語、把單一會話被擠下線寫成「踢除」、留下空字串，型別檢查與其餘碼面閘一律照綠。本閘把這幾類內容錯誤改成 commit 級訊號。

掃描面與解析（本閘自有一份；與 tools/msg-key-gate.py 之 backend 錨解析各持解析、互不共用，各以自測守自身解析）：
  詞法：丟棄 `//` 行註解與 `/* */` 區塊註解（字串內之 `//`、`/*` 不算註解）；字串字面＝單引號、雙引號、反引號三形，值先解跳脫
    （`\\uXXXX`、`\\u{…}`、`\\xXX`、行接續；其餘 `\\c` 取 c）再判；含 `${…}` 之反引號不算字串字面值。
  物件根＝首個 `const <名>(: <型>)? = {` 或 `export default {` 之開括號（以詞法單元比對：註解與字串內之同形字不算；其後之物件不收）。
  自物件根 brace 配對攤平：鍵＝識別字、數字或引號字串，巢狀鍵以 `.` 串接成鍵路徑（例 `backend.auth.session.kicked`、`route.403`）；值為物件即遞迴，
    其餘值收至同層 `,`／`}` 為止、其間字串字面值皆歸該鍵（`'甲' + '乙'` 兩段同歸一鍵；鍵層判準以串接後之全文判——
    詞跨字面切開照命中（③、④b／④c 之 MUST 不含、④e）、MUST 含類照算含（④b／④c／④d）、幽靈以全文判；單字判準「踢」〔④a、④b〕
    逐字面與串接等價）。
  鍵名與註解不判。行號＝字串字面起始行；鍵層判準（③④）取該鍵首個字面之行、該鍵無字面時取鍵所在行。

判準（四腿＋空值；逐項獨立出列、互不遮蔽——同一字串同時命中多條即多行）：
  ①簡體殘字（zh-tw）：逐字面逐字，屬 SIMPLIFIED_CHARS 之鍵＝紅、附正體建議。
  ②字表完備（zh-tw＋zh-cn）：兩檔字面所用 CJK 表意文字（CJK_RANGES＝統一區、擴充 A～J 與兩個相容區）每字 MUST 屬 SIMPLIFIED_CHARS 之鍵或
    APPROVED_CHARS；未分類＝紅、逐字一行、指名首見之檔:行與鍵路徑（先掃 zh-tw）。新譯文之新字由本腿逼出分類。
  ③大陸用語（zh-tw）：鍵全文含 MAINLAND_TERMS 之詞（含 _HOMOGRAPH_TERMS 併入之同形異用字詞條）＝紅、附臺灣用語。
  ④會話用語（zh-tw；GR2——「頂替」＝單一會話政策下新登入撤下同帳號既有會話、「踢除」＝管理員結束他人全部會話）：
    a.「踢」出現於 ADMIN_KICK_KEYS 以外之鍵＝紅（名冊＝精確鍵集、鍵路徑逐字全等比對；名冊外逐形有案：無關鍵、延長名冊鍵、截短名冊鍵、
      同葉名異父、名冊鍵掛於他父之下、大小寫異形）；
    b.`backend.auth.session.kicked` 缺席、缺「頂替」、含「踢」、含「管理員」各＝紅（含「踢」即使該鍵誤入 ADMIN_KICK_KEYS 仍紅）；
    c.`backend.auth.session.kickedByAdmin` 缺席、缺「管理員」、含「頂替」各＝紅；
    d.ADMIN_KICK_KEYS 中 `page.` 起首之鍵在場而缺「踢除」＝紅；缺席之 page 鍵不判（名冊鍵先於頁面落地之過渡語意，鍵一落地即受判）；
    e.任一鍵含 BANNED_SESSION_TERMS（踢出／踢掉／踢下線／擠下線／擠掉／頂掉）＝紅（ADMIN_KICK_KEYS 內亦同）。
  空值（zh-tw）：任一字串字面為空字串＝紅（逐字面判：同鍵多段字面中任一段為空亦紅；三語型別不擋空字串）。
  zh-cn.ts 只供腿②（簡化字為其本分）；en-us.ts 不讀。

具名白名單（EXEMPT）：
  逐筆＝（鍵路徑, 字或詞, 理由）三個非空字串；字或詞須屬 SIMPLIFIED_CHARS 或 MAINLAND_TERMS 之鍵——只對腿①③生效、只及所列鍵之所列字或詞（同鍵他字他詞與②④照報）。
  模組常數之唯讀 tuple、定義為純字面，不接受 args、env 或讀檔來源；項數由 self-test 釘住（現為零筆；增列須同批改該斷言、於 diff 現形）。
  幽靈即紅＝該鍵已不在 zh-tw.ts、或該鍵全文已無該字或詞（RL-0051 形；同 tools/seed-view-gate.py 之 EXEMPT 語意）——逼人同批摘列、表只會縮。
  壞形（非三元組、任一欄空、字或詞不屬腿①③之表）＝rc 2。
  self-test 對本檔自身打五根釘（形照 tools/seed-view-gate.py）、各封一條繞道：項數恆定；呼叫點原封傳入（run_check
    唯一的 judge 呼叫以四表與 EXEMPT 本名為末五實參）；判定路徑零外部取值形（詞法、解析與 judge 原文不得出現讀檔、環境變數、命令列、stdin、
    json 之取值字面）；呼叫端零就地改表（不可變型、全檔各恰一處綁定且無 global 宣告、EXEMPT 測試類以外恰一處引用）；白名單定義為純字面
    （頂層恰一處以 EXEMPT 為唯一目標之指派、其值經 ast.literal_eval 成立——取自環境變數、讀檔、命令列或任何呼叫、名稱引用、運算式皆非字面＝紅，
    定義改置條件區塊內或解構指派＝頂層零處＝紅）。
  ★射程自陳：五釘守的是字面形與佈線；刻意繞開字面者（反射、動態拼名）仍靠人審，不是形式證明。

射程外（判不出之形與其承載）：
  ·腿②只驗「每字有歸類」、不驗歸類正確：簡化字被誤歸 APPROVED_CHARS 機器抓不到——承載＝表值 diff 審查、GR5 AI 逐頁審讀與 user 抽查（ADR-00084 後果）。
  ·Big5 內簡繁同形異用字（_APPROVED_HOMOGRAPHS；取捨見該表旁）歸 APPROVED_CHARS、腿①不報；其大陸用法由腿③以詞境承擔＝
    _HOMOGRAPH_TERMS 逐字分組之詞條（併入 MAINLAND_TERMS；self-test 釘每個同形異用字恰屬「有詞條組」或「_HOMOGRAPHS_NO_TERM 附理由」之一）。
    判不出者兩形、皆由 GR5 AI 逐頁審讀承擔：甲、詞條未收之詞境（詞條只收兩檔現用之大陸用法詞與介面常用詞；連詞「并」、後置「后」
    接任意詞之一般形不可窮舉——例「刪除后」「確認并送出」判不出，詞條已收之建立后、選擇并等形除外）；乙、_HOMOGRAPHS_NO_TERM 之字（臺灣亦通行該寫法＝無大陸專屬用法，
    或短詞境必誤殺正當用例——逐字理由見該表）。
    「里」「干」（契約點名之同形異用字）不在任一字表（兩檔現未用）：出現即由腿②逼出逐字人審；歸 _APPROVED_HOMOGRAPHS 時須同批補詞條組
    或列入 _HOMOGRAPHS_NO_TERM（「里面」詞條已在 MAINLAND_TERMS）。
    Big5 收錄而只是正字異體寫法之九字（确网与挂触异昵优构）不屬此類、歸 SIMPLIFIED_CHARS＝腿①照報。
  ·值內非字串字面之成分（識別字、運算式、函式呼叫、含 `${…}` 之反引號）不貢獻字、其內容不判，審查兜底。鍵層「MUST 含」判準
    （④b「頂替」、④c「管理員」、④d「踢除」）以該鍵字串字面串接之全文判：值內無任何字串字面者（上列四形）逐腿視同無字＝紅；
    值內另有字串字面者只以該字面判（例 `x + '…頂替'` 過 ④b 之必含）。
  ·CJK 部首、注音與標點不入腿②；審查兜底。正規表示式字面值不在詞法射程（locale 檔不用）。
  ·葉值之間缺 `,`（`a: '甲'` 換行接 `b: '乙'`）不在上列結構異常：其後之鍵名與字面併入前一鍵之值（字面照判、鍵路徑與鍵層判準歸前一鍵；
    self-test 釘此併入形）——該語法錯由前端型別檢查承擔。
  ·物件根提早收住而全檔括號仍配對（多一個 `}` 同時他處少一個 `}`）：根外之鍵值不收、不報結構異常（self-test 釘此形）——承載＝前端型別
    檢查（`App.I18n.Schema` 標型缺鍵、`const` 宣告語法錯）。只多一個 `}` 者全檔括號不配對＝rc 2（見退出碼）。
  ·程式內之原因值與後端碼註不在射程（GR2）。

退出碼：0 綠／1 任一腿命中、空值或白名單幽靈（合併列出、逐項指名鍵路徑與字或詞；鍵在場者並附檔:行〔腿②為首見之檔:行〕，鍵缺席之三形——
  頂替鍵缺席、管理員踢除鍵缺席、白名單幽靈之鍵已不在——只指鍵路徑）／2 結構異常（逐形列舉、各形 self-test 以訊息指名成因：
  兩檔任一缺席或非 UTF-8（不以替代字元續判）、物件根兩形皆缺、物件至檔尾未收、括號錯配或多出閉括號〔物件根內由解析各層判；物件根以外
  ——根前與根收尾後合併為一列——另以括號堆疊判：多一個 `}` 提早收住物件根、其後鍵值落在根外即落此形〕、物件根以外之開括號至檔尾未收、
  字串或註解未收尾〔單、雙引號字面內遇換行亦屬之〕、鍵位不是識別字／數字／引號字串〔展開 `...`、計算鍵 `[…]`、含 `${…}` 之反引號鍵〕、鍵後缺 `:`〔簡寫屬性〕、鍵缺值、
  物件值或值之後不是 `,`／`}`〔其後即檔尾亦屬之〕、任一檔零字串字面值＝比對面為空〔RL-0051〕、兩字表相交、白名單項壞形；self-test 敗亦 2）
  ／64 用法錯。tracked 面缺席一律 rc 2，工具與 pre-commit 段皆不設具名跳過（ADR-00019 決定 4）。
讀面型（ADR-00055 決定 3）：(a) 兩檔皆在 base-web `src/locales/langs`＝pre-commit submodule-sync 段之 base-web 閘面內——外層單獨 commit 時
  可能判到工作樹，下一次 pin bump 時該段要求閘面乾淨、屆時補抓。
check 不連帶跑 self-test（ADR-00084 決定 7）：自測只吃合成 fixtures、結果只隨本檔而變，本檔 staged 時 pre-commit `for` 自測迴圈必跑其 test、
  bootstrap 體檢亦跑。
表值之家＝本檔常數（SIMPLIFIED_CHARS／APPROVED_CHARS／MAINLAND_TERMS／ADMIN_KICK_KEYS／BANNED_SESSION_TERMS／EXEMPT）；活書與契約只指、不鏡像。
依賴：Python 3 標準庫、零 docker、零網路。接線：pre-commit zh-tw-lint 段（base-web pin bump 或本檔 staged 時跑 check）、
  `for` 自測迴圈與 bootstrap 名冊（test）、README 樹、RUNBOOK §12 兩表。
"""
import ast
import contextlib
import inspect
import io
import os
import re
import sys
import tempfile
import types
import unittest
import unittest.mock

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS_REL = os.path.join("base-web", "src", "locales", "langs")
TW_REL = os.path.join(LANGS_REL, "zh-tw.ts")
CN_REL = os.path.join(LANGS_REL, "zh-cn.ts")
TW_NAME = "zh-tw.ts"
CN_NAME = "zh-cn.ts"
TAG = "[zh-tw-lint]"
USAGE = "用法：tools/zh-tw-lint.py [check|test]"
RC_OK, RC_VIOLATION, RC_STRUCT, RC_USAGE = 0, 1, 2, 64

# 腿② 之 CJK 表意文字碼位：擴充 A／統一區／相容區／擴充 B～I 與相容補充區（含其間未配置碼位）／擴充 G～J。
CJK_RANGES = ((0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF), (0x20000, 0x2FA1F), (0x30000, 0x3347F))

# ── 表值（ADR-00084 決定 7；007 刀 U16 初建）───────────────────────────────────────
# 初建程序：自 zh-tw.ts 與 zh-cn.ts 之字面用字，以 codec 判準（可編碼於 gb2312 而不可編碼於 cp950）篩候選、逐字人審後入表；其餘用字亦逐字
#   人審入 APPROVED_CHARS 兩組。codec 只作初建輔助、不在本檔判定路徑。後續新字由腿②逼出、同樣逐字人審：
#   簡化字（臺灣正體不用此形）→ SIMPLIFIED_CHARS 附建議；正體字與繁簡同形字 → _APPROVED_PLAIN；
#   簡化字形而本身亦為 Big5 正體字（同形異用）→ _APPROVED_HOMOGRAPHS（腿①不報；其大陸用法由腿③以詞境承擔＝同批於 _HOMOGRAPH_TERMS
#   補該字詞條組、或列入 _HOMOGRAPHS_NO_TERM 附理由，self-test 釘二擇一）。
# 一對多簡化字與 Big5 收錄字形之取捨（逐字）：
#   ①歸 SIMPLIFIED_CHARS 者——該簡化字本身不屬臺灣正體用字（不在 Big5），任何出現皆誤；建議欄列全部正體候選、首列為本介面語境常用者；
#     合法用例不存在 ⇒ 不設 EXEMPT：发→發（髮：毛髮義）、当→當（噹：狀聲詞）、获→獲（穫：收穫義）、尝→嘗（嚐：品嚐義）、
#     须→須（鬚：鬍鬚義）、签→簽（籤：標籤義）、术→術（朮：藥名白朮）、别→別（彆：彆扭義）、个→個（箇：異體）；
#     另账→帳／賬（標準對應為賬；臺灣「帳號」「帳戶」慣用帳，故帳列首）。
#   ②歸 _APPROVED_HOMOGRAPHS 者——該字本身亦為 Big5 正體字，單字判定必誤殺正當用例 ⇒ 腿①不收（ADR-00084 決定 7）：
#     于（於；姓）、后（後；皇后）、台（臺／檯／颱；台）、只（隻）、系（係／繫）、了（瞭）、面（麵）、布（佈）、表（錶）、致（緻）、才（纔）、
#     回（迴）、向（嚮）、出（齣）、合（閤）、注（註）、范（範；姓）、采（採；風采）、余（餘；我、姓）、云（雲；云云）、准（準；批准）、
#     板（闆）、谷（穀）、折（摺）、制（製）、丰（豐；丰采）、并（並／併）、复（復／複）、划（劃；划船）、据（據；拮据）、适（適）；
#     Big5 收錄之簡化字形而另有獨立正體音義者同 适 之例歸此組（本介面難見其用例，然單字判定即誤殺該獨立義、守 ADR-00084 決定 7 之分界）：
#     体（體；另讀 bèn、粗劣義）、机（機；另為木名與几案義）、离（離；另讀 chī、山神義）、荐（薦；另為草蓆、屢次義）——
#     本組各字之大陸用法由腿③詞條承擔（_HOMOGRAPH_TERMS；如体驗、手机、离線、推荐），無詞條者見 _HOMOGRAPHS_NO_TERM。
#   ③Big5 收錄而只是正字之異體寫法者（同音同義、無現行獨立正體義；臺灣正體書面一律用正字）不屬同形異用 ⇒ 歸 SIMPLIFIED_CHARS、
#     附正字建議（合法用例若現＝入 EXEMPT；現無）：确（確）、网（網）、与（與）、挂（掛）、触（觸）、异（異）、昵（暱）、优（優）、构（構）——
#     皆 zh-cn 對譯最易漏改之高頻字（确认、网络、与、挂载、触发、异常、昵称、优化、构建）。
SIMPLIFIED_CHARS = types.MappingProxyType({
    "两": "兩", "严": "嚴", "个": "個／箇", "为": "為", "义": "義", "乐": "樂", "习": "習", "产": "產", "仅": "僅", "们": "們", "会": "會", "侧": "側",
    "兰": "蘭", "关": "關", "内": "內", "册": "冊", "写": "寫", "决": "決", "凑": "湊", "击": "擊", "则": "則", "刚": "剛", "创": "創", "删": "刪",
    "别": "別／彆", "办": "辦", "务": "務", "动": "動", "区": "區", "协": "協", "单": "單", "参": "參", "双": "雙", "发": "發／髮", "变": "變", "叠": "疊",
    "号": "號", "吗": "嗎", "启": "啟", "员": "員", "响": "響", "国": "國", "图": "圖", "圆": "圓", "场": "場", "块": "塊", "处": "處", "备": "備",
    "头": "頭", "娱": "娛", "孙": "孫", "学": "學", "实": "實", "宽": "寬", "对": "對", "导": "導", "将": "將", "尝": "嘗／嚐", "层": "層", "屉": "屜", "属": "屬",
    "带": "帶", "应": "應", "开": "開", "弹": "彈", "强": "強", "归": "歸", "当": "當／噹", "录": "錄", "径": "徑", "态": "態", "户": "戶", "执": "執",
    "护": "護", "择": "擇", "挡": "擋", "换": "換", "携": "攜", "数": "數", "断": "斷", "无": "無", "旧": "舊", "时": "時", "显": "顯", "暂": "暫",
    "术": "術／朮", "权": "權", "条": "條", "来": "來", "标": "標", "栈": "棧", "栏": "欄", "样": "樣", "档": "檔", "检": "檢", "欢": "歡", "没": "沒",
    "浅": "淺", "测": "測", "浏": "瀏", "渐": "漸", "滚": "滾", "满": "滿", "点": "點", "状": "狀", "现": "現", "画": "畫", "码": "碼", "础": "礎",
    "称": "稱", "筛": "篩", "签": "簽／籤", "简": "簡", "类": "類", "紧": "緊", "红": "紅", "级": "級", "线": "線", "组": "組", "细": "細", "经": "經",
    "绑": "綁", "结": "結", "络": "絡", "绝": "絕", "统": "統", "维": "維", "缓": "緩", "编": "編", "缩": "縮", "获": "獲／穫", "见": "見", "观": "觀",
    "规": "規", "视": "視", "览": "覽", "认": "認", "议": "議", "记": "記", "许": "許", "设": "設", "访": "訪", "证": "證", "评": "評", "词": "詞",
    "试": "試", "话": "話", "询": "詢", "该": "該", "详": "詳", "语": "語", "误": "誤", "说": "說", "请": "請", "读": "讀", "调": "調", "谨": "謹", "败": "敗",
    "账": "帳／賬", "贴": "貼", "资": "資", "赖": "賴", "践": "踐", "转": "轉", "载": "載", "较": "較", "辑": "輯", "输": "輸", "边": "邊", "过": "過",
    "还": "還", "进": "進", "远": "遠", "连": "連", "选": "選", "邮": "郵", "钩": "鉤", "钮": "鈕", "链": "鏈", "销": "銷", "锁": "鎖", "错": "錯",
    "键": "鍵", "长": "長", "闪": "閃", "闭": "閉", "问": "問", "间": "間", "阅": "閱", "际": "際", "随": "隨", "隐": "隱", "页": "頁", "顶": "頂",
    "项": "項", "须": "須／鬚", "预": "預", "频": "頻", "题": "題", "颜": "顏", "额": "額", "风": "風", "验": "驗",
    # Big5 收錄之異體字形（取捨見上方③）：
    "确": "確", "网": "網", "与": "與", "挂": "掛", "触": "觸", "异": "異", "昵": "暱", "优": "優", "构": "構",
})

_APPROVED_PLAIN = (
    "一三上下不且並中主之也二些交亦亮人今仍仔他代以件任休伺位住何作你佳併使來例供依便保信修個們候值偏做停側偵備傳僅優儲允元充先入"
    "內全兩共其冊再冷函分切列別刪到刷則前剛剪創力功加勉動務勾包化匹區印即原參又取受口可右同名否含告和員啟喜單嗎嘗器嚴因固國圍"
    "圓圖在地址型域執基堆報塊填境增外多夜大天失套女如始娛子字存孫學它安完定家容密富實寫寬將專尋對導小尚尾局居屏屑展屜層屬工左己"
    "已帳帶常幕年序底度建式弱強彈形彩影役往待後徑得復微心必忘忙快性恢息您情意愛態應成我或所手打批找技把抽拒括拼持指按捲授排掛採"
    "接推描提插換援搜撤撰擇擊擋操支收改放政效敗教敬整數文料新方於日早明是時普景晴暗暫暱更替最會月有服期未本束查校格框案桶條樂標模"
    "樣橙機檔檢欄權次款歌歡止正此步歸段母每比水求決沒沿法活派浮消淡深混淺添清測湊源準滑滿演漸瀏灰為無然照父片版特狀現理環甘生產"
    "用由男留略畫異疊登發的目相看知確碼礎示禁私秒移程稍稱空窗立站端符第筆策算管箱範篩簡簿精糊紅級索細結絕統綁維網緊線編縮繁置"
    "習考者能自至臺與舊航般色莫菜著薦藏蘭處號螢行術被裝製複見規視覽觀角解觸言訂訊記訪設許註評詢試話該詳認語誤說調請謹證警護讀"
    "變豐象貼資起超跟跨路跳踐踢身載輯輸轉辦迎返迪述退送通速造連逾過遠適選還邊部配醒重量鈕鉤銷錄錯鍵鎖長閃閉開間閱關阻限除階際"
    "隨隱雅集雙離雲需非靠音頁頂項須預頭頻題額顏類顯風餘首驗驟體高麵黑默點鼠"
)
_APPROVED_HOMOGRAPHS = "丰了于云体余准出划制只台合后向回复布并才折据机板注离系致范荐表谷适采面"
APPROVED_CHARS = frozenset(_APPROVED_PLAIN + _APPROVED_HOMOGRAPHS)

# 同形異用字之詞境詞條（腿③承擔 _APPROVED_HOMOGRAPHS 之大陸用法；007 刀 contracts code-gates §2.1 腿①）：逐字分組、組內詞皆含該字，
#   全組併入 MAINLAND_TERMS。詞形＝臺灣正體詞中、只有該字取大陸寫法之形（其餘字已為正體＝腿①不報之漏網形；含簡化字之形由腿①先報、
#   改正後即落入此形）。收詞＝兩檔現用之大陸用法詞與介面常用詞；短詞境會與正當用例相鄰誤殺者不收。ADR-00084 決定 7 之初版必收詞中
#   屬同形異用字者（于、后台、以后、之后、然后、最后）住本表 于／台／后 三組。
_HOMOGRAPH_TERMS = types.MappingProxyType({
    "丰": {"丰富": "豐富"},
    "于": {"于": "於"},
    "云": {"多云": "多雲", "云端": "雲端"},
    "体": {"主体": "主體", "字体": "字型", "具体": "具體", "整体": "整體", "實体": "實體", "体驗": "體驗", "体系": "體系"},
    "余": {"其余": "其餘", "剩余": "剩餘", "多余": "多餘"},
    "准": {"准備": "準備", "標准": "標準", "准確": "準確", "精准": "精準"},
    "划": {"下划線": "底線／下劃線", "計划": "計畫／計劃", "規划": "規劃", "划分": "劃分"},
    "制": {"複制": "複製", "繪制": "繪製"},
    "台": {"后台": "後臺"},
    "后": {"以后": "以後", "之后": "之後", "然后": "然後", "最后": "最後", "稍后": "稍後", "后再": "後再", "成功后": "成功後",
           "失敗后": "失敗後", "啟用后": "啟用後", "建立后": "建立後", "變更后": "變更後", "重連后": "重連後", "頁面后": "頁面後"},
    "复": {"复制": "複製", "复製": "複製", "复原": "復原", "恢复": "恢復", "重复": "重複", "回复": "回覆／回復", "复選": "複選", "复雜": "複雜"},
    "并": {"并且": "並且", "合并": "合併", "并發": "並發／併發", "并行": "並行", "并列": "並列", "選擇并": "選擇並", "閱讀并": "閱讀並"},
    "据": {"數据": "資料", "根据": "根據", "依据": "依據", "證据": "證據"},
    "机": {"手机": "手機", "打字机": "打字機", "隨机": "隨機", "机器": "機器", "主机": "主機", "机制": "機制", "机會": "機會"},
    "板": {"老板": "老闆"},
    "注": {"注冊": "註冊", "備注": "備註"},
    "离": {"离開": "離開", "离線": "離線", "距离": "距離"},
    "致": {"精致": "精緻", "細致": "細緻"},
    "范": {"規范": "規範", "范圍": "範圍", "示范": "示範"},
    "荐": {"推荐": "推薦"},
    "谷": {"谷歌": "Google"},
    "适": {"适用": "適用", "适合": "適合", "合适": "合適", "自适應": "自適應", "适配": "適配", "适當": "適當"},
    "采": {"采用": "採用", "采集": "採集"},
})
# 無詞條之同形異用字（大陸用法由 GR5 AI 逐頁審讀承擔）：臺灣亦通行該寫法＝無大陸專屬用法，或短詞境必誤殺正當用例。
_HOMOGRAPHS_NO_TERM = types.MappingProxyType({
    "了": "瞭義：臺灣「了解」「瞭解」並行＝無大陸專屬用法",
    "才": "纔義：臺灣通行「才」＝無大陸專屬用法",
    "合": "閤義：臺灣「合家」「閤家」並行＝無大陸專屬用法",
    "布": "佈義：臺灣「布局」「布置」「分布」「發布」皆通行＝無大陸專屬用法",
    "折": "摺義：臺灣「折疊」「摺疊」並行＝具歧義、不入表",
    "回": "迴義：臺灣「回響／迴響」「回避／迴避」並行；回覆義之大陸寫法「回复」由 复 組承擔",
    "出": "齣義（一齣戲）介面無用例；量詞短詞境「一出」誤殺「唯一出現」",
    "只": "隻義（量詞）介面罕見；短詞境「一只」誤殺「唯一只能」",
    "向": "嚮義（嚮導、嚮往）介面罕見；短詞境「向導」誤殺「方向導覽」",
    "系": "係／繫義：短詞境「關系」「聯系」誤殺「相關系統」「關聯系統」",
    "表": "錶義（手錶）介面罕見；短詞境「手表」誤殺「選手表現」",
    "面": "麵義（麵條）介面無用例；短詞境「方便面」誤殺「方便面對」",
})

# 大陸用語 → 臺灣用語：ADR-00084 決定 7 之初版必收詞全收（同形異用字詞條住 _HOMOGRAPH_TERMS、於此併入），另收「常量」（007 刀 U15
#   全樹審讀；臺灣程式用語作「常數」）。不入表：具歧義之詞（文件、項目、地址、對象——臺灣亦有正當用法）與非大陸專用語（工作臺、一站式、
#   開箱即用、前沿技術、最佳實踐），皆由 GR5 AI 逐頁審讀承擔。
MAINLAND_TERMS = types.MappingProxyType({
    "用戶": "使用者", "默認": "預設", "登錄": "登入", "註銷": "登出", "退出登錄": "登出", "菜單": "選單", "設置": "設定", "數據": "資料",
    "信息": "訊息／資訊", "網絡": "網路", "軟件": "軟體", "程序": "程式", "支持": "支援", "激活": "啟用", "賬號": "帳號", "服務器": "伺服器",
    "緩存": "快取", "內存": "記憶體", "打印": "列印", "導入": "匯入", "導出": "匯出", "搜索": "搜尋", "刷新": "重新整理", "創建": "建立",
    "保存": "儲存", "郵箱": "信箱", "鏈接": "連結", "圖標": "圖示", "字體": "字型", "模塊": "模組", "加載": "載入", "視頻": "影片",
    "屏幕": "螢幕", "全屏": "全螢幕", "質量": "品質", "里面": "裡面", "常量": "常數",
    **{term: advice for group in _HOMOGRAPH_TERMS.values() for term, advice in group.items()},
})

# 會話用語腿（GR2）：管理員踢除語境之鍵路徑集＝kickedByAdmin、管理員對自身執行踢除之拒因鍵、使用者頁踢除三鍵（鍵名＝007 刀 contracts
# code-gates §1.2 page 新鍵名冊）；增減須同批改 self-test 之名冊釘。
SESSION_KICKED_KEY = "backend.auth.session.kicked"
ADMIN_KICKED_KEY = "backend.auth.session.kickedByAdmin"
ADMIN_KICK_KEYS = frozenset({
    ADMIN_KICKED_KEY, "backend.biz.user.cannotKickSelf",
    "page.manage.user.kick", "page.manage.user.confirmKick", "page.manage.user.kickSuccess",
})
PAGE_PREFIX = "page."
KICK_CHAR = "踢"
KICK_WORD = "踢除"
SUPERSEDE_WORD = "頂替"
ADMIN_WORD = "管理員"
BANNED_SESSION_TERMS = ("踢出", "踢掉", "踢下線", "擠下線", "擠掉", "頂掉")

# 具名白名單（語意與五釘見檔頭）：逐筆（鍵路徑, 字或詞, 理由）；現為零筆。
EXEMPT = ()


class StructuralError(Exception):
    """解析或表值受損（rc 2）：訊息即輸出行之主體。"""


def is_cjk(ch):
    """單字是否屬 CJK 表意文字碼位（CJK_RANGES）。"""
    code = ord(ch)
    return any(lo <= code <= hi for lo, hi in CJK_RANGES)


# ── 詞法與解析（本閘自有；與 tools/msg-key-gate.py 之 backend 錨解析各持一份、互不共用）────────────

RE_WORD = re.compile(r"[A-Za-z0-9_$]+")
RE_IDENT = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
RE_ESCAPE = re.compile(r"\\(u\{[0-9A-Fa-f]{1,6}\}|u[0-9A-Fa-f]{4}|x[0-9A-Fa-f]{2}|\r\n|[\s\S])")
ESCAPE_CHARS = {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}
LINE_CONTINUATIONS = ("\n", "\r", "\r\n", "\u2028", "\u2029")
OPENERS, CLOSERS = "([{", ")]}"


def _unescape(raw):
    """字面原文 → 值：`\\uXXXX`／`\\u{…}`／`\\xXX`／單字元跳脫／行接續逐一解碼；其餘 `\\c` 取 c。"""
    def one(m):
        seq = m.group(1)
        if seq[0] in "ux" and len(seq) > 1:
            code = int(seq.strip("ux{}"), 16)
            return chr(code) if code <= 0x10FFFF else m.group(0)
        if seq in LINE_CONTINUATIONS:
            return ""
        return ESCAPE_CHARS.get(seq, seq)
    return RE_ESCAPE.sub(one, raw)


def _skip_interpolation(text, j):
    """反引號內 `${` 之 `{` 起、brace 計數至配對 `}` 之後一位；未收即回傳檔尾（由呼叫端報字串字面未收尾）。"""
    depth = 0
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return j


def tokenize(text):
    """全文 → 詞法單元 [(類別, 值, 行號)]：類別＝str（值＝解碼後字面；含 ${…} 之反引號值為 None）／word／punct；註解丟棄。"""
    toks, i, n, line = [], 0, len(text), 1
    while i < n:
        c = text[i]
        if c == "\n":
            line += 1
            i += 1
        elif c.isspace() or c == "\ufeff":
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            if j < 0:
                raise StructuralError(f"第 {line} 行起之 /* 區塊註解未收尾")
            line += text.count("\n", i, j)
            i = j + 2
        elif c in "'\"`":
            j, interpolated = i + 1, False
            while True:
                if j >= n or (c != "`" and text[j] == "\n"):
                    raise StructuralError(f"第 {line} 行起之字串字面未收尾")
                if text[j] == "\\":
                    j += 2
                elif text[j] == c:
                    break
                elif c == "`" and text.startswith("${", j):
                    interpolated, j = True, _skip_interpolation(text, j + 1)
                else:
                    j += 1
            raw = text[i + 1:j]
            toks.append(("str", None if interpolated else _unescape(raw), line))
            line += raw.count("\n")
            i = j + 1
        else:
            m = RE_WORD.match(text, i)
            word = m.group() if m else c
            toks.append(("word" if m else "punct", word, line))
            i += len(word)
    return toks


def _at(toks, k):
    return toks[k][:2] if k < len(toks) else None


def _find_root(toks):
    """首個 `export default {` 或 `const <名>(: <型>)? = {` 之開括號位置（詞法單元比對：註解與字串內之同形字不算）。"""
    for k, (kind, val, _) in enumerate(toks):
        if kind != "word":
            continue
        if val == "export" and _at(toks, k + 1) == ("word", "default") and _at(toks, k + 2) == ("punct", "{"):
            return k + 2
        if val == "const" and k + 1 < len(toks) and toks[k + 1][0] == "word" and RE_IDENT.fullmatch(toks[k + 1][1]):
            j = k + 2
            if _at(toks, j) == ("punct", ":"):
                j += 1
                while j < len(toks) and not (toks[j][0] == "punct" and toks[j][1] in "={};"):
                    j += 1
            if _at(toks, j) == ("punct", "=") and _at(toks, j + 1) == ("punct", "{"):
                return j + 1
    raise StructuralError("物件根兩形皆缺：找不到 `const <名>(: <型>)? = {` 或 `export default {`")


def _parse_value(toks, k, path, key_line, leaves):
    """非物件值：收至同層 `,`／`}` 或檔尾為止，其間字串字面值皆歸本鍵；括號須配對（檔尾由呼叫端報）。回傳停止位置。"""
    stack, lits, start = [], [], k
    while k < len(toks):
        kind, val, line = toks[k]
        if kind == "punct" and not stack and val in ",}":
            break
        if kind == "punct" and val in OPENERS:
            stack.append(CLOSERS[OPENERS.index(val)])
        elif kind == "punct" and val in CLOSERS:
            if not stack or stack.pop() != val:
                raise StructuralError(f"第 {line} 行：括號不配對（遇「{val}」）")
        elif kind == "str" and val is not None:
            lits.append((val, line))
        k += 1
    if k == start:
        raise StructuralError(f"第 {key_line} 行：鍵 {'.'.join(path)} 缺值")
    leaves.append((".".join(path), key_line, lits))
    return k


def _parse_object(toks, k, prefix, leaves):
    """自 toks[k]＝`{` 起解析物件：鍵＝識別字、數字或引號字串；值為物件即遞迴。回傳配對 `}` 之後一位。"""
    k += 1
    while True:
        if k >= len(toks):
            raise StructuralError("brace 不配對：物件至檔尾未收")
        kind, val, line = toks[k]
        if (kind, val) == ("punct", "}"):
            return k + 1
        if kind not in ("word", "str") or val is None:
            raise StructuralError(f"第 {line} 行：預期鍵名、遇「{val}」（展開、計算鍵等寫法不在解析射程）")
        if _at(toks, k + 1) != ("punct", ":"):
            raise StructuralError(f"第 {line} 行：鍵 {val} 之後缺 `:`（簡寫屬性等寫法不在解析射程）")
        path, k = prefix + (val,), k + 2
        if _at(toks, k) == ("punct", "{"):
            k = _parse_object(toks, k, path, leaves)
        else:
            k = _parse_value(toks, k, path, line, leaves)
        if _at(toks, k) == ("punct", ","):
            k += 1
        elif _at(toks, k) != ("punct", "}"):
            raise StructuralError(f"第 {toks[k][2] if k < len(toks) else line} 行：鍵 {'.'.join(path)} 之後預期 `,` 或 `}}`")


def _scan_outside_root(toks):
    """物件根以外之詞法單元（根前與根收尾後合併為一列）括號須配對：多出閉括號、錯配、開括號至檔尾未收＝StructuralError。
    多一個 `}` 會提早收住物件根、其後鍵值落在根外而不入掃描面（RL-0051 形之縮水），由本檢查轉成結構異常。"""
    pending = []
    for kind, val, line in toks:
        if kind != "punct":
            continue
        if val in OPENERS:
            pending.append((val, line))
        elif val in CLOSERS:
            if not pending:
                raise StructuralError(f"第 {line} 行：物件根之外多出閉括號「{val}」——多一個 `}}` 會提早收住物件根、其後鍵值不入掃描面")
            opener, _ = pending.pop()
            if CLOSERS[OPENERS.index(opener)] != val:
                raise StructuralError(f"第 {line} 行：物件根之外括號錯配（遇「{val}」）")
    if pending:
        raise StructuralError(f"第 {pending[-1][1]} 行起：物件根之外開括號「{pending[-1][0]}」至檔尾未收")


def parse_locale(text):
    """檔全文 → 葉鍵串列 [(鍵路徑, 鍵所在行, [(字面值, 行號), …])]（檔內序）。物件根缺、brace 不配對（根內與根外）、射程外寫法、
    零字面＝StructuralError。"""
    toks = tokenize(text)
    leaves = []
    start = _find_root(toks)
    end = _parse_object(toks, start, (), leaves)
    _scan_outside_root(toks[:start] + toks[end:])
    if not any(lits for _, _, lits in leaves):
        raise StructuralError("物件根內零個字串字面值（比對面為空）")
    return leaves


# ── 判定 ───────────────────────────────────────────────────────────────

def table_faults(simplified, approved, terms, exempt):
    """表本身受損之逐項說明（空串列＝健全）：兩字表相交、白名單項壞形。"""
    faults = []
    both = sorted(set(simplified) & set(approved))
    if both:
        faults.append(f"SIMPLIFIED_CHARS 與 APPROVED_CHARS 相交：{'、'.join(both)}——同一字不得兼屬兩表（表本身受損）")
    for item in exempt:
        if not (isinstance(item, tuple) and len(item) == 3 and all(isinstance(x, str) and x for x in item)):
            faults.append(f"白名單項壞形：{item!r}——須為（鍵路徑, 字或詞, 理由）三個非空字串")
        elif item[1] not in simplified and item[1] not in terms:
            faults.append(f"白名單項壞形：{item!r}——字或詞須屬 SIMPLIFIED_CHARS 或 MAINLAND_TERMS 之鍵（白名單只對腿①③生效）")
    return faults


def judge(tw, cn, simplified, approved, terms, kick_keys, exempt):
    """純判定 → (rc, 輸出行)：rc 0 綠／1 命中／2 表或白名單受損。兩棵解析樹、四表與白名單由呼叫端以七個實參備妥；會話腿之鍵名、判準字與
    禁用詞表直讀模組常數（SESSION_KICKED_KEY／ADMIN_KICKED_KEY／PAGE_PREFIX／KICK_CHAR／KICK_WORD／SUPERSEDE_WORD／ADMIN_WORD／
    BANNED_SESSION_TERMS）；不碰檔案與環境。"""
    faults = table_faults(simplified, approved, terms, exempt)
    if faults:
        return RC_STRUCT, [f"{TAG} ✗ 結構異常：{f}" for f in faults]
    waived = {(path, token) for path, token, _ in exempt}
    present = {}
    leg1, leg2, leg3, leg4, empty, ghost = [], [], [], [], [], []
    for path, key_line, lits in tw:
        text = "".join(lit for lit, _ in lits)
        loc = f"{TW_NAME}:{lits[0][1] if lits else key_line}"
        where = f"{loc} {path}"
        present[path] = (loc, text)
        for lit, line in lits:
            if lit == "":
                empty.append(f"空值｜{TW_NAME}:{line} {path}——字串值不得為空字串（三語型別不擋空字串）")
            for ch in dict.fromkeys(lit):
                if ch in simplified and (path, ch) not in waived:
                    leg1.append(f"腿①簡體殘字｜{TW_NAME}:{line} {path}「{ch}」→ 正體建議「{simplified[ch]}」")
        for term, advice in terms.items():
            if term in text and (path, term) not in waived:
                leg3.append(f"腿③大陸用語｜{where}「{term}」→ 臺灣用語「{advice}」")
        if KICK_CHAR in text and path not in kick_keys:
            leg4.append(f"腿④「{KICK_CHAR}」出現於 ADMIN_KICK_KEYS 之外｜{where}——「踢除」專指管理員結束他人全部會話；單一會話政策下被新登入撤下用「頂替」")
        for term in BANNED_SESSION_TERMS:
            if term in text:
                leg4.append(f"腿④禁用會話詞｜{where}「{term}」——統一為「踢除」（管理員）或「頂替」（單一會話）")
    kicked = present.get(SESSION_KICKED_KEY)
    if kicked is None:
        leg4.append(f"腿④頂替鍵缺席｜{SESSION_KICKED_KEY}——單一會話頂替文案 MUST 在場且含「{SUPERSEDE_WORD}」")
    else:
        if SUPERSEDE_WORD not in kicked[1]:
            leg4.append(f"腿④頂替鍵缺「{SUPERSEDE_WORD}」｜{SESSION_KICKED_KEY}（{kicked[0]}）")
        if KICK_CHAR in kicked[1]:
            leg4.append(f"腿④頂替鍵含「{KICK_CHAR}」｜{SESSION_KICKED_KEY}（{kicked[0]}）")
        if ADMIN_WORD in kicked[1]:
            leg4.append(f"腿④頂替鍵含「{ADMIN_WORD}」｜{SESSION_KICKED_KEY}（{kicked[0]}）")
    by_admin = present.get(ADMIN_KICKED_KEY)
    if by_admin is None:
        leg4.append(f"腿④管理員踢除鍵缺席｜{ADMIN_KICKED_KEY}——管理員踢除文案 MUST 在場且含「{ADMIN_WORD}」")
    else:
        if ADMIN_WORD not in by_admin[1]:
            leg4.append(f"腿④管理員踢除鍵缺「{ADMIN_WORD}」｜{ADMIN_KICKED_KEY}（{by_admin[0]}）")
        if SUPERSEDE_WORD in by_admin[1]:
            leg4.append(f"腿④管理員踢除鍵含「{SUPERSEDE_WORD}」｜{ADMIN_KICKED_KEY}（{by_admin[0]}）")
    for key in sorted(kick_keys):
        if key.startswith(PAGE_PREFIX) and key in present and KICK_WORD not in present[key][1]:
            leg4.append(f"腿④踢除頁面鍵缺「{KICK_WORD}」｜{key}（{present[key][0]}）")
    first_seen = {}
    for name, leaves in ((TW_NAME, tw), (CN_NAME, cn)):
        for path, _, lits in leaves:
            for lit, line in lits:
                for ch in lit:
                    if is_cjk(ch):
                        first_seen.setdefault(ch, f"{name}:{line} {path}")
    for ch, where in first_seen.items():
        if ch not in simplified and ch not in approved:
            leg2.append(f"腿②字表未分類｜「{ch}」首見 {where}——逐字人審後歸 SIMPLIFIED_CHARS（附正體建議）或 APPROVED_CHARS")
    for path, token, why in exempt:
        if path not in present or token not in present[path][1]:
            state = "該鍵已不在 zh-tw.ts" if path not in present else "該鍵字面已無此字或詞"
            at = path if path not in present else f"{present[path][0]} {path}"
            ghost.append(f"白名單幽靈｜{at}「{token}」——{state}；自 EXEMPT 摘列（{why}）")
    hits = leg1 + leg2 + leg3 + leg4 + empty + ghost
    if hits:
        return RC_VIOLATION, [f"{TAG} ✗ 繁中 locale 命中 {len(hits)} 項（四腿、空值與白名單幽靈逐項獨立出列）："] + [f"  {h}" for h in hits]
    page_kick = [k for k in kick_keys if k.startswith(PAGE_PREFIX)]
    lines = [f"{TAG} ✓ {TW_NAME} 葉鍵 {len(tw)}（字串字面 {sum(len(l) for _, _, l in tw)}）、{CN_NAME} 葉鍵 {len(cn)}"
             f"（字串字面 {sum(len(l) for _, _, l in cn)}）；兩檔 CJK 用字 {len(first_seen)} 字全分類"
             f"（屬 SIMPLIFIED_CHARS {sum(1 for c in first_seen if c in simplified)}、APPROVED_CHARS {sum(1 for c in first_seen if c in approved)}）；"
             f"MAINLAND_TERMS {len(terms)} 詞、會話用語腿（ADMIN_KICK_KEYS {len(kick_keys)} 鍵、其 page 鍵在場 "
             f"{sum(1 for k in page_kick if k in present)}／{len(page_kick)}）、空值皆零命中；EXEMPT {len(exempt)} 筆"]
    lines += [f"{TAG}   豁免仍生效：{path}「{token}」——{why}" for path, token, why in exempt]
    return RC_OK, lines


def run_check(repo_root):
    """讀真檔兩面 → (rc, 輸出行)。缺席、非 UTF-8 與解析異常＝rc 2（逐檔指名）；其餘交 judge，四表與白名單原封傳入。"""
    absent = [rel.replace(os.sep, "/") for rel in (TW_REL, CN_REL) if not os.path.isfile(os.path.join(repo_root, rel))]
    if absent:
        return RC_STRUCT, [f"{TAG} ✗ 讀面缺席：{'、'.join(absent)}——tracked 面缺席不設跳過（ADR-00019 決定 4）；子庫工作樹未就位跑 bash tools/bootstrap.sh"]
    trees = []
    for rel in (TW_REL, CN_REL):
        try:
            with open(os.path.join(repo_root, rel), encoding="utf-8") as fh:
                trees.append(parse_locale(fh.read()))
        except (StructuralError, UnicodeDecodeError) as ex:
            return RC_STRUCT, [f"{TAG} ✗ 結構異常：{rel.replace(os.sep, '/')}：{ex}——掃描面為空或形制已變不算綠（RL-0051）"]
    return judge(trees[0], trees[1], SIMPLIFIED_CHARS, APPROVED_CHARS, MAINLAND_TERMS, ADMIN_KICK_KEYS, EXEMPT)


def _say(msg, err=False):
    print(msg, file=sys.stderr if err else sys.stdout, flush=True)


# ── self-test（離線；暫存目錄與記憶體內合成 fixtures，一律實跑上方生產函式）────────────────────

OK_KICKED = "您的帳號已在其他裝置登入，此工作階段已被頂替"
OK_BY_ADMIN = "此工作階段已被管理員結束，請重新登入"
CN_TREE = {"backend": {"common": {"success": "操作成功"}}}
TW_POSIX = TW_REL.replace(os.sep, "/")
CN_POSIX = CN_REL.replace(os.sep, "/")


def _q(value):
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _obj(tree, depth=1):
    pad = "  " * depth
    rows = []
    for key, value in tree.items():
        lit = key if re.fullmatch(r"[A-Za-z_$][\w$]*", key) else _q(key)
        rows.append(f"{pad}{lit}: " + (_obj(value, depth + 1) if isinstance(value, dict) else _q(value)))
    return "{\n" + ",\n".join(rows) + "\n" + "  " * (depth - 1) + "}"


def _ts(tree, root="const"):
    """合成 locale 檔：root＝const（`const local: App.I18n.Schema = {`＋末行 export default local）／bare（`const local = {`）／export（`export default {`）。"""
    body = _obj(tree)
    if root == "export":
        return f"export default {body};\n"
    head = "const local: App.I18n.Schema = " if root == "const" else "const local = "
    return f"{head}{body};\n\nexport default local;\n"


def _tw(page=None, kicked=OK_KICKED, by_admin=OK_BY_ADMIN, extra_backend=None):
    """合成 zh-tw 樹：backend 會話兩鍵預設合法；page 子樹與 backend 其餘子樹由案自帶。kicked／by_admin 給 None＝該鍵缺席。"""
    session = {}
    if kicked is not None:
        session["kicked"] = kicked
    if by_admin is not None:
        session["kickedByAdmin"] = by_admin
    backend = {"auth": {"session": session}}
    backend.update(extra_backend or {})
    return {"backend": backend, "page": page or {"home": {"greeting": "早安"}}}


def _line_of(text, needle):
    return text[:text.index(needle)].count("\n") + 1


def _judge(tw_text, cn_text=None, *, simplified=None, approved=None, terms=None, kick_keys=None, exempt=()):
    tw = parse_locale(tw_text)
    cn = parse_locale(cn_text if cn_text is not None else _ts(CN_TREE))
    rc, lines = judge(tw, cn, SIMPLIFIED_CHARS if simplified is None else simplified,
                      APPROVED_CHARS if approved is None else approved, MAINLAND_TERMS if terms is None else terms,
                      ADMIN_KICK_KEYS if kick_keys is None else kick_keys, exempt)
    return rc, "\n".join(lines)


def _write(path, text, binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w", **({} if binary else {"encoding": "utf-8"})) as fh:
        fh.write(text)


def _fake_repo(tmp, tw_text, cn_text, skip=()):
    if "tw" not in skip:
        _write(os.path.join(tmp, TW_REL), tw_text)
    if "cn" not in skip:
        _write(os.path.join(tmp, CN_REL), cn_text)
    return tmp


class TestC01Green(unittest.TestCase):
    """自測①：合成全繁中樹＝綠。"""

    def test_c01_all_traditional_tree_is_green(self):
        """全繁中樹（含會話兩鍵合法值、踢除語境鍵合法用「踢」、多層巢狀與引號鍵）＝rc 0、零 ✗"""
        tw = _ts(_tw(page={"home": {"greeting": "早安", "desc": "專案動態"}, "manage": {"user": {"kick": "踢除下線"}}},
                     extra_backend={"biz": {"user": {"cannotKickSelf": "不可踢除您自己的帳號"}}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 0, text)
        self.assertNotIn("✗", text)
        self.assertIn("✓", text)


class TestC02Simplified(unittest.TestCase):
    """自測②：腿①簡體殘字——值含 SIMPLIFIED_CHARS 之字＝rc 1、指名檔:行、鍵路徑、字與正體建議。"""

    def test_c02_simplified_char_is_red_naming_key_line_and_advice(self):
        tw = _ts(_tw(page={"home": {"greeting": "早安设定"}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn(f"腿①簡體殘字｜{TW_NAME}:{_line_of(tw, '早安设定')} page.home.greeting「设」→ 正體建議「設」", text)

    def test_c02_escape_sequences_are_decoded_before_judging(self):
        """`\\u8bbe`、`\\u{8bbe}`、`\\x` 形跳脫解碼後再判（设＝U+8BBE）"""
        tw = _ts(_tw()).replace("greeting: '早安'", "greeting: '早安\\u8bbe', b: '\\u{8bbe}定', c: 'x\\x41'")
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn("page.home.greeting「设」", text)
        self.assertIn("page.home.b「设」", text)
        self.assertNotIn("page.home.c", text)

    def test_c02_double_quoted_value_and_line_continuation(self):
        """雙引號字面照判；行接續與 `\\'` 跳脫解碼後再判（跨行接續之詞照命中腿③）、行號取字面起始行"""
        tw = _ts(_tw()).replace("greeting: '早安'", "greeting: \"早安设\", b: '設\\\n置\\'设'")
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn("page.home.greeting「设」", text)
        self.assertIn(f"{TW_NAME}:{_line_of(tw, 'b: ')} page.home.b「设」", text)
        self.assertIn(f"{TW_NAME}:{_line_of(tw, 'b: ')} page.home.b「設置」", text)

    def test_c02_backtick_without_interpolation_is_scanned(self):
        tw = _ts(_tw()).replace("greeting: '早安'", "greeting: `早安设`")
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn("page.home.greeting「设」", text)


class TestC03Comments(unittest.TestCase):
    """自測③：簡化字只在註解（`//`、`/* */`）與鍵名內＝綠；字串內之 `//` 不算註解。"""

    def test_c03_simplified_only_in_comments_and_key_names_is_green(self):
        tw = _ts(_tw()).replace("greeting: '早安'", "// 设\n      greeting: /* 设 */ '早安', /**\n * 设\n */\n      '设': '設定'")
        rc, text = _judge(tw)
        self.assertEqual(rc, 0, text)

    def test_c03_double_slash_inside_string_is_not_a_comment(self):
        """zh-cn 外部連結拒因之形：字串內 `http://` 之後仍屬字面、照判"""
        tw = _ts(_tw()).replace("greeting: '早安'", "greeting: '以 http:// 或 https:// 开頭'")
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn("page.home.greeting「开」", text)

    def test_c03_block_comment_opener_inside_string_is_not_a_comment(self):
        """路徑樣式之形：字串內 `/*` 不開區塊註解——其後各鍵之字面直到另一字串內之 `*/` 為止照判"""
        tw = _ts(_tw()).replace("greeting: '早安'", "greeting: '路徑 /api/*', b: '早安设', c: '*/ 結尾'")
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn(f"腿①簡體殘字｜{TW_NAME}:{_line_of(tw, 'b: ')} page.home.b「设」", text)


class TestC04Completeness(unittest.TestCase):
    """自測④：腿②字表完備——未分類字 rc 1（指名字、首見檔與鍵路徑）；兩表相交 rc 2。"""

    def test_c04_unclassified_char_in_zh_tw_is_red_naming_char_file_and_key(self):
        tw = _ts(_tw(page={"home": {"greeting": "早安鬱"}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn(f"腿②字表未分類｜「鬱」首見 {TW_NAME}:{_line_of(tw, '早安鬱')} page.home.greeting", text)

    def test_c04_unclassified_char_first_seen_in_zh_cn_names_zh_cn(self):
        cn = _ts({"backend": {"common": {"success": "操作成功鬱"}}})
        rc, text = _judge(_ts(_tw()), cn)
        self.assertEqual(rc, 1, text)
        self.assertIn(f"腿②字表未分類｜「鬱」首見 {CN_NAME}:{_line_of(cn, '操作成功鬱')} backend.common.success", text)

    def test_c04_zh_tw_is_scanned_first(self):
        """兩檔皆用之未分類字只報一行、首見指 zh-tw"""
        rc, text = _judge(_ts(_tw(page={"home": {"greeting": "鬱"}})), _ts({"backend": {"common": {"success": "鬱"}}}))
        self.assertEqual(rc, 1, text)
        self.assertEqual(text.count("「鬱」首見"), 1, text)
        self.assertIn(f"「鬱」首見 {TW_NAME}:", text)

    def test_c04_zh_cn_feeds_leg2_only(self):
        """zh-cn 之簡化字屬 SIMPLIFIED_CHARS 之鍵＝已分類；①③④與空值不掃 zh-cn"""
        cn = _ts({"backend": {"common": {"success": "设置成功", "a": "常量", "b": "踢出", "c": ""}}})
        rc, text = _judge(_ts(_tw()), cn)
        self.assertEqual(rc, 0, text)

    def test_c04_every_cjk_range_reaches_leg2_in_both_files(self):
        """腿②判定經 is_cjk 全段（CJK_RANGES 五段：擴充 A、統一區、相容區、擴充 B～I 與相容補充區、擴充 G～J）：兩檔各植五段之未分類字
        （統一區以外各段一字、統一區由上列各案承擔），逐字一行指名首見之檔:行與鍵路徑"""
        tw_chars = ("㐀", "豈", "\U00020000", "\U0002f800", "\U00030000")
        cn_chars = ("㐁", "更", "\U00020001", "\U0002f801", "\U00030001")
        tw = _ts(_tw(page={"home": {f"k{i}": f"早{ch}" for i, ch in enumerate(tw_chars)}}))
        cn = _ts({"backend": {"common": {f"k{i}": f"成{ch}" for i, ch in enumerate(cn_chars)}}})
        rc, text = _judge(tw, cn)
        self.assertEqual(rc, 1, text)
        for name, src, chars, prefix, lead in ((TW_NAME, tw, tw_chars, "page.home", "早"), (CN_NAME, cn, cn_chars, "backend.common", "成")):
            for i, ch in enumerate(chars):
                self.assertIn(f"腿②字表未分類｜「{ch}」首見 {name}:{_line_of(src, lead + ch)} {prefix}.k{i}", text)
        self.assertEqual(text.count("腿②字表未分類｜"), len(tw_chars) + len(cn_chars), text)

    def test_c04_tables_intersecting_is_rc2(self):
        rc, text = _judge(_ts(_tw()), approved=APPROVED_CHARS | {"设"})
        self.assertEqual(rc, 2, text)
        self.assertIn("相交", text)
        self.assertIn("设", text)


class TestC05Mainland(unittest.TestCase):
    """自測⑤：腿③大陸用語——命中附臺灣用語建議；鍵內多段字面串接後判；同形異用字之大陸用法由本腿承擔。"""

    def test_c05_mainland_term_is_red_with_advice(self):
        tw = _ts(_tw(page={"home": {"greeting": "請完成設置"}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn(f"腿③大陸用語｜{TW_NAME}:{_line_of(tw, '請完成設置')} page.home.greeting「設置」→ 臺灣用語「設定」", text)

    def test_c05_term_split_across_concatenated_literals_is_caught(self):
        tw = _ts(_tw()).replace("greeting: '早安'", "greeting: '早安設' +\n        '置'")
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn("page.home.greeting「設置」", text)

    def test_c05_homograph_chars_are_carried_by_leg3_not_leg1(self):
        """「于」「后」屬 Big5 同形異用字＝腿①不報；其大陸用法由腿③詞條承擔"""
        rc, text = _judge(_ts(_tw(page={"home": {"a": "關于本頁", "b": "之后再說", "c": "表格里面"}})),
                          approved=APPROVED_CHARS | {"里"})
        self.assertEqual(rc, 1, text)
        self.assertIn("page.home.a「于」→ 臺灣用語「於」", text)
        self.assertIn("page.home.b「之后」→ 臺灣用語「之後」", text)
        self.assertIn("page.home.c「里面」→ 臺灣用語「裡面」", text)
        self.assertNotIn("腿①", text)

    def test_c05_constant_term_from_review(self):
        rc, text = _judge(_ts(_tw(page={"home": {"greeting": "常量路由"}})))
        self.assertEqual(rc, 1, text)
        self.assertIn("「常量」→ 臺灣用語「常數」", text)

    def test_c05_homograph_words_in_mainland_sense_are_red_with_advice(self):
        """同形異用字取大陸用法之詞（其餘字已為正體＝腿①不報之漏網形）由腿③逐詞報、附臺灣用語（審查實證七形）"""
        probes = (("a", "复制設定", "复制", "複製"), ("b", "主体捲動", "主体", "主體"), ("c", "主體复原", "复原", "復原"),
                  ("d", "手机號碼", "手机", "手機"), ("e", "推荐顏色", "推荐", "推薦"), ("f", "适合夜間", "适合", "適合"),
                  ("g", "多云轉晴", "多云", "多雲"))
        tw = _ts(_tw(page={"home": {key: value for key, value, _, _ in probes}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        for key, value, term, advice in probes:
            self.assertIn(f"腿③大陸用語｜{TW_NAME}:{_line_of(tw, value)} page.home.{key}「{term}」→ 臺灣用語「{advice}」", text)
        self.assertEqual(text.count("腿③大陸用語｜"), len(probes), text)
        self.assertNotIn("腿①", text)

    def test_c05_every_homograph_term_is_red_via_leg3_not_leg1(self):
        """_HOMOGRAPH_TERMS 逐詞：植入即腿③紅、附該詞之臺灣用語；腿①不報（詞內含未分類字者腿②另報、不在本案斷言）"""
        pairs = [(term, advice) for group in _HOMOGRAPH_TERMS.values() for term, advice in group.items()]
        tw = _ts(_tw(page={"home": {f"k{i}": term for i, (term, _) in enumerate(pairs)}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        for i, (term, advice) in enumerate(pairs):
            self.assertIn(f"page.home.k{i}「{term}」→ 臺灣用語「{advice}」", text)
        self.assertNotIn("腿①", text)

    def test_c05_homograph_legit_uses_are_green(self):
        """同形異用字之臺灣正當用法（單字與易誤殺之相鄰形）不受腿③詞條波及：例「相關系統」不因「關系」、「唯一只能」不因「一只」而紅"""
        legit = ("返回首頁", "表格", "只能", "系統", "合法", "頁面", "不一致", "送出", "收合", "實現了", "剛才", "發布", "注意", "模板",
                 "向下", "風采", "划算", "折線圖", "批准", "控制", "山谷", "平台", "相關系統", "方向導覽", "唯一只能", "唯一出現",
                 "選手表現", "方便面對")
        tw = _ts(_tw(page={"home": {f"k{i}": value for i, value in enumerate(legit)}}))
        rc, text = _judge(tw, approved=APPROVED_CHARS | frozenset("唯山平控"))
        self.assertEqual(rc, 0, text)

    def test_c05_li_and_gan_are_forced_by_leg2(self):
        """契約點名之「里」「干」不在任一字表：出現即腿②逼出人審（歸類前不靠腿③）"""
        for ch in "里干":
            self.assertNotIn(ch, SIMPLIFIED_CHARS)
            self.assertNotIn(ch, APPROVED_CHARS)
        tw = _ts(_tw(page={"home": {"a": "表格里", "b": "干"}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn(f"腿②字表未分類｜「里」首見 {TW_NAME}:{_line_of(tw, '表格里')} page.home.a", text)
        self.assertIn(f"腿②字表未分類｜「干」首見 {TW_NAME}:{_line_of(tw, 'b: ')} page.home.b", text)


class TestC06Exempt(unittest.TestCase):
    """自測⑥：白名單只抑制腿①③之所列鍵×所列字或詞、幽靈即紅、壞形 rc 2；項數恆定與定義純字面斷言見 TestInvariants。"""

    TREE = {"home": {"a": "早安设定", "b": "請完成設置"}}

    def test_c06_exempt_masks_leg1_and_leg3_and_is_listed(self):
        exempt = (("page.home.a", "设", "合成理由甲"), ("page.home.b", "設置", "合成理由乙"))
        rc, text = _judge(_ts(_tw(page=self.TREE)), exempt=exempt)
        self.assertEqual(rc, 0, text)
        self.assertIn("豁免仍生效：page.home.a「设」——合成理由甲", text)
        self.assertIn("豁免仍生效：page.home.b「設置」——合成理由乙", text)

    def test_c06_exempt_is_per_key(self):
        """豁免只及所列鍵：同字（腿①）、同詞（腿③）出現在他鍵照報、所列鍵不報"""
        for leg, token, value in (("腿①簡體殘字", "设", "设"), ("腿③大陸用語", "設置", "請完成設置")):
            with self.subTest(leg):
                tw = _ts(_tw(page={"home": {"a": value, "c": value}}))
                rc, text = _judge(tw, exempt=(("page.home.a", token, "合成理由"),))
                self.assertEqual(rc, 1, text)
                self.assertIn(f"{leg}｜{TW_NAME}:{_line_of(tw, 'c: ')} page.home.c「{token}」→", text)
                self.assertNotIn(f"page.home.a「{token}」→", text)

    def test_c06_exempt_is_per_token(self):
        """豁免只及所列鍵之所列字或詞：同鍵另含之簡化字（腿①「发」）與大陸用語（腿③「保存」）照報，所列之「设」「設置」不報"""
        tw = _ts(_tw(page={"home": {"a": "设定发布，請完成設置並保存"}}))
        rc, text = _judge(tw, exempt=(("page.home.a", "设", "合成理由"), ("page.home.a", "設置", "合成理由")))
        self.assertEqual(rc, 1, text)
        at = f"{TW_NAME}:{_line_of(tw, '设定发布')} page.home.a"
        self.assertIn(f"腿①簡體殘字｜{at}「发」→", text)
        self.assertIn(f"腿③大陸用語｜{at}「保存」→", text)
        self.assertEqual((text.count("腿①簡體殘字｜"), text.count("腿③大陸用語｜"), text.count("白名單幽靈｜")), (1, 1, 0), text)

    def test_c06_exempt_does_not_mask_leg2_or_leg4(self):
        """豁免只抑制腿③：同鍵之腿②（未分類字）與腿④各形照報——a「踢」在名冊外、e 禁用會話詞（字詞同時落在腿③與腿②／腿④），
        b／c／d 鍵層 MUST 含（豁免該鍵之腿③詞不放行其腿④）"""
        terms = dict(MAINLAND_TERMS, **{"踢出": "踢除", "鬱": "郁"})
        tw = _ts(_tw(page={"home": {"greeting": "已踢出", "b": "鬱"}, "manage": {"user": {"kick": "強制下線設置"}}},
                     kicked="此工作階段已結束設置", by_admin="此工作階段已被結束設置"))
        exempt = (("page.home.greeting", "踢出", "合成理由"), ("page.home.b", "鬱", "合成理由"),
                  (SESSION_KICKED_KEY, "設置", "合成理由"), (ADMIN_KICKED_KEY, "設置", "合成理由"), ("page.manage.user.kick", "設置", "合成理由"))
        rc, text = _judge(tw, terms=terms, exempt=exempt)
        self.assertEqual(rc, 1, text)
        g, k, a, p = (f"{TW_NAME}:{_line_of(tw, anchor)}" for anchor in ("greeting:", "kicked:", "kickedByAdmin:", "kick:"))
        expected = (f"腿④「踢」出現於 ADMIN_KICK_KEYS 之外｜{g} page.home.greeting",
                    f"腿④禁用會話詞｜{g} page.home.greeting「踢出」",
                    f"腿④頂替鍵缺「頂替」｜{SESSION_KICKED_KEY}（{k}）",
                    f"腿④管理員踢除鍵缺「管理員」｜{ADMIN_KICKED_KEY}（{a}）",
                    f"腿④踢除頁面鍵缺「踢除」｜page.manage.user.kick（{p}）")
        for phrase in expected:
            self.assertIn(phrase, text)
        self.assertEqual(text.count("腿④"), len(expected), text)
        self.assertIn("腿②字表未分類｜「鬱」", text)
        self.assertNotIn("腿③", text)

    def test_c06_ghost_when_key_absent_is_red(self):
        rc, text = _judge(_ts(_tw()), exempt=(("page.home.gone", "设", "合成理由"),))
        self.assertEqual(rc, 1, text)
        self.assertIn("白名單幽靈｜page.home.gone「设」", text)
        self.assertIn("該鍵已不在", text)

    def test_c06_ghost_when_token_gone_is_red(self):
        """鍵仍在場而字詞已無：幽靈項附該鍵之檔:行（鍵缺席之幽靈只指鍵路徑，見上一案）"""
        tw = _ts(_tw())
        rc, text = _judge(tw, exempt=(("page.home.greeting", "設置", "合成理由"),))
        self.assertEqual(rc, 1, text)
        self.assertIn(f"白名單幽靈｜{TW_NAME}:{_line_of(tw, 'greeting:')} page.home.greeting「設置」", text)
        self.assertIn("已無此字或詞", text)

    def test_c06_exempt_term_split_across_literals_is_live_not_ghost(self):
        """幽靈判準以該鍵全文判：豁免之詞跨字面切開（`'…設' + '置'`）仍屬生效豁免、不報幽靈"""
        tw = _ts(_tw()).replace("greeting: '早安'", "greeting: '請完成設' + '置'")
        rc, text = _judge(tw, exempt=(("page.home.greeting", "設置", "合成理由"),))
        self.assertEqual(rc, 0, text)
        self.assertIn("豁免仍生效：page.home.greeting「設置」——合成理由", text)

    def test_c06_malformed_exempt_item_is_rc2(self):
        """壞形逐形 rc 2、以訊息指名成因：非三元組（含非 tuple 之三元序列）、任一欄空或非字串、字詞不屬腿①③之表"""
        shape, table = "三個非空字串", "字或詞須屬 SIMPLIFIED_CHARS 或 MAINLAND_TERMS 之鍵"
        for label, item, cause in (("非三元組", ("page.home.greeting", "设"), shape),
                                   ("非 tuple 之三元序列", ["page.home.greeting", "设", "合成理由"], shape),
                                   ("鍵欄空", ("", "设", "合成理由"), shape), ("字詞欄空", ("page.home.greeting", "", "合成理由"), shape),
                                   ("理由空", ("page.home.greeting", "设", ""), shape), ("欄非字串", ("page.home.greeting", "设", 1), shape),
                                   ("字詞不屬腿①③之表", ("page.home.greeting", "早", "合成理由"), table)):
            with self.subTest(label):
                rc, text = _judge(_ts(_tw(page={"home": {"greeting": "早安设"}})), exempt=(item,))
                self.assertEqual(rc, 2, text)
                self.assertIn(f"白名單項壞形：{item!r}——", text)
                self.assertIn(cause, text)


class TestC07Session(unittest.TestCase):
    """自測⑦：腿④會話用語各形。"""

    def _red(self, tw_text, phrase, **kw):
        rc, text = _judge(tw_text, **kw)
        self.assertEqual(rc, 1, text)
        self.assertIn(phrase, text)
        return text

    def test_c07_kicked_containing_kick_char_is_red_even_if_listed(self):
        """頂替鍵含「踢」：即使誤入 ADMIN_KICK_KEYS 仍紅（本判準獨立於歸屬檢查）"""
        tw = _ts(_tw(kicked=OK_KICKED + "（踢）"))
        text = self._red(tw, f"腿④頂替鍵含「踢」｜{SESSION_KICKED_KEY}（{TW_NAME}:{_line_of(tw, 'kicked:')}）",
                         kick_keys=ADMIN_KICK_KEYS | {SESSION_KICKED_KEY})
        self.assertNotIn("出現於 ADMIN_KICK_KEYS 之外", text)

    def test_c07_kicked_containing_admin_is_red(self):
        tw = _ts(_tw(kicked=OK_KICKED + "，由管理員"))
        self._red(tw, f"腿④頂替鍵含「管理員」｜{SESSION_KICKED_KEY}（{TW_NAME}:{_line_of(tw, 'kicked:')}）")

    def test_c07_kicked_lacking_supersede_word_is_red(self):
        tw = _ts(_tw(kicked="您的帳號已在其他裝置登入，此工作階段已結束"))
        self._red(tw, f"腿④頂替鍵缺「頂替」｜{SESSION_KICKED_KEY}（{TW_NAME}:{_line_of(tw, 'kicked:')}）")

    def test_c07_kicked_absent_is_red(self):
        self._red(_ts(_tw(kicked=None)), f"腿④頂替鍵缺席｜{SESSION_KICKED_KEY}")

    def test_c07_kicked_non_literal_value_counts_as_lacking(self):
        """含 `${…}` 之反引號不是字串字面值：MUST 含類判準視同無字"""
        tw = _ts(_tw()).replace(_q(OK_KICKED), "`${x}頂替`")
        self._red(tw, f"腿④頂替鍵缺「頂替」｜{SESSION_KICKED_KEY}（{TW_NAME}:{_line_of(tw, 'kicked:')}）")

    def test_c07_must_contain_without_any_literal_counts_as_lacking(self):
        """「MUST 含」類判準（④b 頂替、④c 管理員、④d 踢除）以該鍵字串字面串接之全文判：值內無字串字面之四形
        （識別字、含 `${…}` 之反引號、運算式、函式呼叫）逐腿視同無字＝紅、指名鍵所在行；值內另有字串字面者以該字面判"""
        page = {"manage": {"user": {"kick": "踢除下線"}}}
        legs = ((SESSION_KICKED_KEY, "kicked:", OK_KICKED, SUPERSEDE_WORD, "腿④頂替鍵缺「頂替」"),
                (ADMIN_KICKED_KEY, "kickedByAdmin:", OK_BY_ADMIN, ADMIN_WORD, "腿④管理員踢除鍵缺「管理員」"),
                ("page.manage.user.kick", "kick:", "踢除下線", KICK_WORD, "腿④踢除頁面鍵缺「踢除」"))
        for key, anchor, value, word, label in legs:
            for form, expr in (("識別字", "x"), ("含 ${…} 之反引號", f"`${{x}}{word}`"), ("運算式", "a + b"), ("函式呼叫", "f(x)")):
                with self.subTest(key=key, form=form):
                    tw = _ts(_tw(page=page)).replace(_q(value), expr)
                    self._red(tw, f"{label}｜{key}（{TW_NAME}:{_line_of(tw, anchor)}）")
            with self.subTest(key=key, form="另有字串字面"):
                rc, text = _judge(_ts(_tw(page=page)).replace(_q(value), f"x + {_q(value)}"))
                self.assertEqual(rc, 0, text)

    def test_c07_by_admin_lacking_admin_is_red(self):
        tw = _ts(_tw(by_admin="此工作階段已被結束，請重新登入"))
        self._red(tw, f"腿④管理員踢除鍵缺「管理員」｜{ADMIN_KICKED_KEY}（{TW_NAME}:{_line_of(tw, 'kickedByAdmin:')}）")

    def test_c07_by_admin_containing_supersede_word_is_red(self):
        tw = _ts(_tw(by_admin=OK_BY_ADMIN + "（頂替）"))
        self._red(tw, f"腿④管理員踢除鍵含「頂替」｜{ADMIN_KICKED_KEY}（{TW_NAME}:{_line_of(tw, 'kickedByAdmin:')}）")

    def test_c07_by_admin_absent_is_red(self):
        self._red(_ts(_tw(by_admin=None)), f"腿④管理員踢除鍵缺席｜{ADMIN_KICKED_KEY}")

    def test_c07_kick_char_outside_admin_kick_keys_is_red(self):
        tw = _ts(_tw(page={"home": {"greeting": "踢球"}}))
        self._red(tw, f"腿④「踢」出現於 ADMIN_KICK_KEYS 之外｜{TW_NAME}:{_line_of(tw, '踢球')} page.home.greeting")

    def test_c07_kick_char_in_unlisted_key_resembling_listed_key_is_red(self):
        """名冊為精確鍵集（鍵路徑逐字全等比對）：形似名冊鍵之非名冊鍵含「踢」逐形紅、各指名該鍵——延長名冊鍵（page.manage.user.kickAll、
        backend.auth.session.kickedByAdminHint）、截短名冊鍵（backend.biz.user.cannotKick）、同葉名異父（page.manage.role.kick、
        backend.biz.role.cannotKickSelf）、名冊鍵掛於他父之下（backend.page.manage.user.kick）、大小寫異形（page.manage.user.Kick）"""
        forms = (("page.manage.user.kickAll", "踢除全部"), ("backend.auth.session.kickedByAdminHint", "由管理員踢除"),
                 ("backend.biz.user.cannotKick", "不可踢除"), ("page.manage.role.kick", "踢除角色"),
                 ("backend.biz.role.cannotKickSelf", "不可踢除您自己的角色"), ("backend.page.manage.user.kick", "踢除（他父）"),
                 ("page.manage.user.Kick", "踢除（大寫）"))
        tree = _tw(page={"manage": {"user": {"kick": "踢除下線"}}},
                   extra_backend={"biz": {"user": {"cannotKickSelf": "不可踢除您自己的帳號"}}})
        for key, value in forms:
            node = tree
            *parents, leaf = key.split(".")
            for part in parents:
                node = node.setdefault(part, {})
            node[leaf] = value
        tw = _ts(tree)
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        for key, value in forms:
            self.assertIn(f"腿④「踢」出現於 ADMIN_KICK_KEYS 之外｜{TW_NAME}:{_line_of(tw, _q(value))} {key}", text)
        self.assertEqual(text.count("腿④"), len(forms), text)

    def test_c07_kick_char_inside_admin_kick_keys_is_green(self):
        tw = _ts(_tw(page={"manage": {"user": {"kick": "踢除下線", "confirmKick": "確認踢除？", "kickSuccess": "踢除成功"}}},
                     extra_backend={"biz": {"user": {"cannotKickSelf": "不可踢除您自己的帳號"}}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 0, text)

    def test_c07_page_kick_key_lacking_kick_word_is_red(self):
        tw = _ts(_tw(page={"manage": {"user": {"kick": "強制下線", "confirmKick": "確認踢除？"}}}))
        self._red(tw, f"腿④踢除頁面鍵缺「踢除」｜page.manage.user.kick（{TW_NAME}:{_line_of(tw, 'kick:')}）")

    def test_c07_absent_page_kick_keys_are_not_judged(self):
        """名冊之 page 鍵在真檔缺席＝「MUST 含踢除」不判（過渡語意）"""
        rc, text = _judge(_ts(_tw(page={"manage": {"user": {"title": "使用者清單"}}})))
        self.assertEqual(rc, 0, text)

    def test_c07_banned_session_terms_each_red(self):
        """六個禁用詞逐一：落在 ADMIN_KICK_KEYS 之 page 鍵內亦紅"""
        for term in BANNED_SESSION_TERMS:
            with self.subTest(term):
                text = self._red(_ts(_tw(page={"manage": {"user": {"kick": f"踢除（{term}）"}}})),
                                 f"腿④禁用會話詞｜{TW_NAME}:", approved=APPROVED_CHARS | frozenset("擠掉"))
                self.assertIn(f"page.manage.user.kick「{term}」——統一為", text)

    def test_c07_squeeze_offline_named_by_contract(self):
        """契約點名形：全樹出現「擠下線」＝rc 1（落在非踢除語境鍵亦同）"""
        self._red(_ts(_tw(page={"home": {"greeting": "已擠下線"}})), "腿④禁用會話詞｜", approved=APPROVED_CHARS | frozenset("擠"))

    def test_c07_words_split_across_literals_are_judged_on_joined_text(self):
        """鍵層判準以該鍵字串字面串接之全文判：詞跨字面切開——④b／④c／④d 之 MUST 含照算含（不報缺），
        ④b／④c 之 MUST 不含與 ④e 禁用詞照紅（單字判準「踢」不跨字面、逐字面與串接等價，不另設案）"""
        page = {"home": {"greeting": "早安"}, "manage": {"user": {"kick": "踢除下線"}}}
        base = _ts(_tw(page=page))
        cases = (
            ("④b 頂替跨字面＝含", _q(OK_KICKED), "'您的帳號已在其他裝置登入，此工作階段已被頂' + '替'", None),
            ("④c 管理員跨字面＝含", _q(OK_BY_ADMIN), "'此工作階段已被管理' + '員結束，請重新登入'", None),
            ("④d 踢除跨字面＝含", "'踢除下線'", "'踢' + '除下線'", None),
            ("④b 含管理員跨字面", _q(OK_KICKED), _q(OK_KICKED)[:-1] + "，由管理' + '員結束'",
             f"腿④頂替鍵含「管理員」｜{SESSION_KICKED_KEY}（{TW_NAME}:{_line_of(base, 'kicked:')}）"),
            ("④c 含頂替跨字面", _q(OK_BY_ADMIN), _q(OK_BY_ADMIN)[:-1] + "（頂' + '替）'",
             f"腿④管理員踢除鍵含「頂替」｜{ADMIN_KICKED_KEY}（{TW_NAME}:{_line_of(base, 'kickedByAdmin:')}）"),
            ("④e 禁用詞跨字面", "greeting: '早安'", "greeting: '已擠下' + '線'",
             f"腿④禁用會話詞｜{TW_NAME}:{_line_of(base, 'greeting:')} page.home.greeting「擠下線」"),
        )
        for label, old, new, phrase in cases:
            with self.subTest(label):
                self.assertEqual(base.count(old), 1, old)
                rc, text = _judge(base.replace(old, new), approved=APPROVED_CHARS | frozenset("擠"))
                self.assertEqual(rc, 0 if phrase is None else 1, text)
                if phrase is not None:
                    self.assertIn(phrase, text)
                    self.assertEqual(text.count("腿④"), 1, text)

    def test_c07_each_criterion_on_one_key_is_listed(self):
        """同鍵多條並列、互不遮蔽：頂替鍵同時缺「頂替」、含「踢」、含「管理員」、「踢」在名冊外、含禁用詞＝五行；
        管理員踢除鍵同時缺「管理員」、含「頂替」＝兩行；同鍵兩個禁用詞各一行"""
        tw = _ts(_tw(kicked="已被管理員踢下線", by_admin="已被頂替", page={"manage": {"user": {"kick": "踢除（踢出、踢掉）"}}}))
        k, a, p = (f"{TW_NAME}:{_line_of(tw, anchor)}" for anchor in ("kicked:", "kickedByAdmin:", "kick:"))
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        expected = (f"腿④「踢」出現於 ADMIN_KICK_KEYS 之外｜{k} {SESSION_KICKED_KEY}",
                    f"腿④禁用會話詞｜{k} {SESSION_KICKED_KEY}「踢下線」",
                    f"腿④頂替鍵缺「頂替」｜{SESSION_KICKED_KEY}（{k}）",
                    f"腿④頂替鍵含「踢」｜{SESSION_KICKED_KEY}（{k}）",
                    f"腿④頂替鍵含「管理員」｜{SESSION_KICKED_KEY}（{k}）",
                    f"腿④管理員踢除鍵缺「管理員」｜{ADMIN_KICKED_KEY}（{a}）",
                    f"腿④管理員踢除鍵含「頂替」｜{ADMIN_KICKED_KEY}（{a}）",
                    f"腿④禁用會話詞｜{p} page.manage.user.kick「踢出」",
                    f"腿④禁用會話詞｜{p} page.manage.user.kick「踢掉」")
        for phrase in expected:
            self.assertIn(phrase, text)
        self.assertEqual(text.count("腿④"), len(expected), text)


class TestC08Empty(unittest.TestCase):
    """自測⑧：空值＝rc 1、指名鍵路徑與行（逐字面判：同鍵多段字面任一段為空亦紅）。"""

    def test_c08_empty_string_value_is_red(self):
        tw = _ts(_tw(page={"home": {"greeting": "早安", "empty": ""}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn(f"空值｜{TW_NAME}:{_line_of(tw, 'empty:')} page.home.empty", text)

    def test_c08_empty_segment_among_non_empty_literals_is_red(self):
        """逐字面判：同鍵另有非空字面而其中一段為空字串（首段或末段）＝紅、指名該空字面之行"""
        for label, value, offset in (("首段空", "'' +\n        '早安'", 0), ("末段空", "'早安' +\n        ''", 1)):
            with self.subTest(label):
                tw = _ts(_tw()).replace("greeting: '早安'", f"greeting: {value}")
                rc, text = _judge(tw)
                self.assertEqual(rc, 1, text)
                self.assertIn(f"空值｜{TW_NAME}:{_line_of(tw, 'greeting:') + offset} page.home.greeting", text)


class TestC09Struct(unittest.TestCase):
    """自測⑨：空檔或零字面 rc 2、兩檔任一缺席 rc 2（經 run_check 全鏈）。"""

    def _check(self, tw_text, cn_text, skip=(), binary_tw=False):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _fake_repo(tmp, tw_text if not binary_tw else "", cn_text, skip)
            if binary_tw:
                _write(os.path.join(tmp, TW_REL), tw_text, binary=True)
            rc, lines = run_check(repo)
        return rc, "\n".join(lines)

    def test_c09_absent_file_is_rc2_and_named(self):
        for face, rel in (("tw", TW_POSIX), ("cn", CN_POSIX)):
            with self.subTest(face):
                rc, text = self._check(_ts(_tw()), _ts(CN_TREE), skip=(face,))
                self.assertEqual(rc, 2, text)
                self.assertIn(f"讀面缺席：{rel}——", text)

    def test_c09_empty_file_is_rc2(self):
        for label, tw, cn in (("zh-tw 空檔", "", _ts(CN_TREE)), ("zh-cn 空檔", _ts(_tw()), "")):
            with self.subTest(label):
                rc, text = self._check(tw, cn)
                self.assertEqual(rc, 2, text)

    def test_c09_zero_literals_is_rc2(self):
        empty_tree = "const local: App.I18n.Schema = {\n  backend: {},\n  page: { home: {} }\n};\n"
        for label, tw, cn in (("zh-tw 零字面", empty_tree, _ts(CN_TREE)), ("zh-cn 零字面", _ts(_tw()), empty_tree)):
            with self.subTest(label):
                rc, text = self._check(tw, cn)
                self.assertEqual(rc, 2, text)
                self.assertIn("比對面為空", text)

    def test_c09_non_utf8_is_rc2(self):
        rc, text = self._check(b"\xff\xfe\xfd", _ts(CN_TREE), binary_tw=True)
        self.assertEqual(rc, 2, text)

    def test_c09_non_utf8_byte_inside_valid_tree_is_rc2(self):
        """合法樹之字面內植入非 UTF-8 位元組（兩檔各一案）：rc 2、指名該檔與解碼錯——不以替代字元續判"""
        for face, rel in (("tw", TW_POSIX), ("cn", CN_POSIX)):
            with self.subTest(face), tempfile.TemporaryDirectory() as tmp:
                tw_bytes, cn_bytes = _ts(_tw()).encode("utf-8"), _ts(CN_TREE).encode("utf-8")
                if face == "tw":
                    tw_bytes = tw_bytes.replace("早安".encode("utf-8"), "早安".encode("utf-8") + b"\xff")
                else:
                    cn_bytes = cn_bytes.replace("操作成功".encode("utf-8"), "操作成功".encode("utf-8") + b"\xff")
                _write(os.path.join(tmp, TW_REL), tw_bytes, binary=True)
                _write(os.path.join(tmp, CN_REL), cn_bytes, binary=True)
                rc, lines = run_check(tmp)
                text = "\n".join(lines)
                self.assertEqual(rc, 2, text)
                self.assertIn(f"結構異常：{rel}：", text)
                self.assertIn("codec can't decode byte 0xff", text)

    def test_c09_check_chain_with_real_tables(self):
        """全鏈經真表：綠案 rc 0；植一簡化字 rc 1 指名鍵與字"""
        rc, text = self._check(_ts(_tw()), _ts(CN_TREE))
        self.assertEqual(rc, 0, text)
        rc, text = self._check(_ts(_tw(page={"home": {"greeting": "早安设"}})), _ts(CN_TREE))
        self.assertEqual(rc, 1, text)
        self.assertIn("page.home.greeting「设」", text)


class TestC10Root(unittest.TestCase):
    """自測⑩：物件根兩形（含無型別註記之 const）各一綠案、兩形皆缺 rc 2；brace 不配對與解析射程外寫法 rc 2。"""

    def test_c10_each_root_form_is_green(self):
        for root in ("const", "bare", "export"):
            with self.subTest(root):
                rc, text = _judge(_ts(_tw(), root=root))
                self.assertEqual(rc, 0, text)

    def test_c10_both_root_forms_absent_is_rc2(self):
        body = _obj(_tw())
        for label, text in (("let 宣告", f"let local = {body};\n"), ("module.exports", f"module.exports = {body};\n"),
                            ("裸物件字面", f"{body}\n"),
                            ("根形只在註解與字串內", f"// export default {{\nconst s = 'const x = {{';\nlet local = {body};\n")):
            with self.subTest(label):
                with self.assertRaises(StructuralError) as ctx:
                    parse_locale(text)
                self.assertIn("物件根兩形皆缺", str(ctx.exception))

    def test_c10_first_root_wins(self):
        """檔內首個根形為準：其後之物件不收"""
        text = "const a = { x: '设' };\nexport default { y: '早' };\n"
        self.assertEqual([path for path, _, _ in parse_locale(text)], ["x"])

    def test_c10_brace_mismatch_or_unparsable_is_rc2(self):
        """結構異常逐形（檔頭 rc 2 清單之解析各形）各一案以上、以訊息指名成因：任一判準停用即有案轉紅（不靠下游他判準兜住）"""
        good = _ts(_tw())
        tail, after, unclosed = "物件至檔尾未收", "之後預期 `,` 或 `}`", "字串字面未收尾"
        for label, text, cause in (("物件根未收", good.replace("};\n\nexport default local;", "\n"), f"鍵 page {after}"),
                                   ("物件根逗號後至檔尾", "const local = {\n  a: '早安',\n", tail),
                                   ("物件根開括號後即檔尾", "const local = {", tail),
                                   ("括號錯配", good.replace("greeting: '早安'", "greeting: ('早安']"), "括號不配對（遇「]」）"),
                                   ("多出閉括號", good.replace("greeting: '早安'", "greeting: '早安')"), "括號不配對（遇「)」）"),
                                   ("簡寫屬性", good.replace("greeting: '早安'", "greeting"), "鍵 greeting 之後缺 `:`"),
                                   ("根層簡寫屬性", "const local = {\n  a: '早安',\n  greeting\n};\n", "鍵 greeting 之後缺 `:`"),
                                   ("展開", good.replace("greeting: '早安'", "...rest"), "預期鍵名、遇「.」"),
                                   ("根層展開", "const local = {\n  a: '早安',\n  ...rest\n};\n", "預期鍵名、遇「.」"),
                                   ("計算鍵", good.replace("greeting: '早安'", "[k]: '早安'"), "預期鍵名、遇「[」"),
                                   ("含內插之反引號鍵", good.replace("greeting: '早安'", "`${k}`: '早安'"), "預期鍵名、遇「None」"),
                                   ("缺值", good.replace("greeting: '早安'", "greeting: "), "鍵 page.home.greeting 缺值"),
                                   ("值至檔尾", "const local = {\n  a: '早安'", f"鍵 a {after}"),
                                   ("物件值後缺逗號", "const local = {\n  a: { b: '早安' }\n  c: '早安'\n};\n", f"第 3 行：鍵 a {after}"),
                                   ("字串未收", good.replace("greeting: '早安'", "greeting: '早安"), unclosed),
                                   ("單引號字面內換行", good.replace("greeting: '早安'", "greeting: '早安\n'"), unclosed),
                                   ("雙引號字面內換行", good.replace("greeting: '早安'", "greeting: \"早安\n\""), unclosed),
                                   ("檔尾字串未收", good + "'未收", unclosed),
                                   ("反引號內插未收", good + "`${未收", unclosed),
                                   ("區塊註解未收", good.replace("greeting: '早安'", "greeting: '早安' /* 未收"), "區塊註解未收尾"),
                                   ("檔尾區塊註解未收", good + "/* 未收", "區塊註解未收尾")):
            with self.subTest(label):
                with self.assertRaises(StructuralError) as ctx:
                    parse_locale(text)
                self.assertIn(cause, str(ctx.exception))

    def test_c10_brace_mismatch_outside_root_is_rc2(self):
        """物件根以外（根前與根收尾後合併為一列）之詞法單元以括號堆疊另掃，逐形經 run_check 全鏈 rc 2、以訊息指名成因與行號：
        多一個 `}` 提早收住物件根（其後 page 子樹落在根外；該子樹植簡化字＝不以縮水之掃描面判綠或 rc 1）、根層葉值後多一個 `}`、
        `};` 之後多一個 `}`、根前多一個 `}`＝多出閉括號；根外括號錯配；根外開括號至檔尾未收。根外括號配對者不報（真檔形
        `};` 接 `export default local;` 見 test_c09_check_chain_with_real_tables、根後另一物件見 test_c10_first_root_wins）"""
        good = _ts(_tw(page={"home": {"greeting": "早安设"}}))
        anchor = "\n  },\n  page: {"
        self.assertEqual(good.count(anchor), 1)
        end, extra = _line_of(good, "};"), "物件根之外多出閉括號「}」"
        for label, text, cause in (("子樹收尾多一個 } 提早收住物件根", good.replace(anchor, "\n  }},\n  page: {"), f"第 {end} 行：{extra}"),
                                   ("根層葉值後多一個 }", "const local = {\n  a: '早安' }\n};\n", f"第 3 行：{extra}"),
                                   ("}; 之後多一個 }", good + "}\n", f"第 {end + 3} 行：{extra}"),
                                   ("根前多一個 }", "}\n" + good, f"第 1 行：{extra}"),
                                   ("根外括號錯配", good + "f(]\n", f"第 {end + 3} 行：物件根之外括號錯配（遇「]」）"),
                                   ("根外開括號至檔尾未收", good + "f(\n", f"第 {end + 3} 行起：物件根之外開括號「(」至檔尾未收")):
            with self.subTest(label), tempfile.TemporaryDirectory() as tmp:
                rc, lines = run_check(_fake_repo(tmp, text, _ts(CN_TREE)))
                out = "\n".join(lines)
                self.assertEqual(rc, 2, out)
                self.assertIn(f"結構異常：{TW_POSIX}：{cause}", out)


class TestParse(unittest.TestCase):
    """解析面補強：鍵路徑攤平、引號鍵與數字鍵、跨行值之行號與跨行構件之後的行號、反引號內插不算字面、單引號內之反引號、葉值缺 `,` 之併入形。"""

    def test_paths_and_lines(self):
        text = ("const local: App.I18n.Schema = {\n  route: {\n    403: '無權限',\n    'iframe-page': '外部連結頁面'\n  },\n"
                "  theme: {\n    'vertical-hybrid_detail':\n      '左側混合版面',\n    hook: '權限鉤子函式 `hasAuth`',\n"
                "    dyn: `${a}设`\n  }\n};\nexport default local;\n")
        got = [(path, [(t, ln) for t, ln in lits]) for path, _, lits in parse_locale(text)]
        self.assertEqual(got, [("route.403", [("無權限", 3)]), ("route.iframe-page", [("外部連結頁面", 4)]),
                               ("theme.vertical-hybrid_detail", [("左側混合版面", 8)]),
                               ("theme.hook", [("權限鉤子函式 `hasAuth`", 9)]), ("theme.dyn", [])])

    def test_lines_advance_past_multiline_constructs(self):
        """跨行構件之後的鍵與字面取其實際行：跨行反引號（不含與含內插）、單引號行接續、跨行區塊註解之後各接一鍵"""
        text = ("const local = {\n"
                "  a: `首行\n次行`,\n"
                "  b: '早安',\n"
                "  c: `${x}\n跨行`,\n"
                "  d: '早安',\n"
                "  e: '設\\\n定',\n"
                "  f: '早安',\n"
                "  /* 區塊\n  註解 */\n"
                "  g: '早安'\n"
                "};\n")
        got = {path: (key_line, lits) for path, key_line, lits in parse_locale(text)}
        self.assertEqual({key: got[key] for key in "bdfg"},
                         {"b": (4, [("早安", 4)]), "d": (7, [("早安", 7)]), "f": (10, [("早安", 10)]), "g": (13, [("早安", 13)])})

    def test_missing_comma_between_leaf_values_merges_into_previous_key(self):
        """射程外形之釘（檔頭「射程外」段）：葉值之間缺 `,` 不報結構異常——其後之鍵名與字面併入前一鍵之值（字面照判、鍵路徑歸前一鍵）"""
        text = "const local = {\n  a: '早安'\n  b: '设'\n};\n"
        self.assertEqual(parse_locale(text), [("a", 2, [("早安", 2), ("设", 3)])])
        rc, out = _judge(_ts(_tw()).replace("greeting: '早安'", "greeting: '早安'\n      b: '设'"))
        self.assertEqual(rc, 1, out)
        self.assertIn("腿①簡體殘字｜", out)
        self.assertIn("page.home.greeting「设」", out)

    def test_balanced_early_root_close_drops_trailing_keys(self):
        """射程外形之釘（檔頭「射程外」段）：多一個 `}` 同時他處少一個 `}`（全檔括號仍配對）＝物件根提早收住、根外之鍵值不收、
        不報結構異常（其後之 `'设'` 不入掃描面）"""
        self.assertEqual(parse_locale("const local = {\n  a: { b: '早安' }},\n  c: '设'\n;\n"), [("a.b", 2, [("早安", 2)])])


class TestAllLegsTogether(unittest.TestCase):
    """四腿、空值與幽靈互不遮蔽：同一樹同時命中即逐項並列。"""

    def test_all_legs_report_together(self):
        tw = _ts(_tw(page={"home": {"a": "设", "b": "鬱", "c": "用戶", "d": "踢球", "e": ""}}, kicked="此工作階段已結束"))
        rc, text = _judge(tw, exempt=(("page.home.gone", "设", "合成理由"),))
        self.assertEqual(rc, 1, text)
        for label in ("腿①簡體殘字｜", "腿②字表未分類｜", "腿③大陸用語｜", "腿④「踢」出現於", "腿④頂替鍵缺「頂替」", "空值｜", "白名單幽靈｜"):
            self.assertIn(label, text)


class TestLocations(unittest.TestCase):
    """輸出指名：跨行值之行號（逐字面判準取所在字面之起始行、鍵層判準取首個字面之行）與同腿多項逐行出列。"""

    def test_per_literal_legs_use_their_own_literal_line(self):
        """鍵行、首字面行、次字面行、末字面行四者相異：腿①②取所在字面之行、空值取該空字面之行（皆非鍵行、非首字面行）"""
        tw = _ts(_tw()).replace("greeting: '早安'", "greeting:\n        '早安' +\n        '设鬱' +\n        ''")
        key = _line_of(tw, "greeting:")
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        self.assertIn(f"腿①簡體殘字｜{TW_NAME}:{key + 2} page.home.greeting「设」", text)
        self.assertIn(f"腿②字表未分類｜「鬱」首見 {TW_NAME}:{key + 2} page.home.greeting", text)
        self.assertIn(f"空值｜{TW_NAME}:{key + 3} page.home.greeting", text)

    def test_key_level_legs_use_first_literal_line(self):
        """鍵層判準（③、④a、④e、④b）取該鍵首個字面之行：非鍵所在行、亦非末個字面之行（真檔有值在鍵之次行之形）"""
        tw = _ts(_tw()).replace("greeting: '早安'", "greeting:\n        '請完成設' +\n        '置，已踢下線'")
        tw = tw.replace(f"kicked: {_q(OK_KICKED)}", "kicked:\n        '您的帳號已在其他裝置登入' +\n        '，由管理員結束'")
        g, k = _line_of(tw, "greeting:") + 1, _line_of(tw, "kicked:") + 1
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        for phrase in (f"腿③大陸用語｜{TW_NAME}:{g} page.home.greeting「設置」",
                       f"腿④「踢」出現於 ADMIN_KICK_KEYS 之外｜{TW_NAME}:{g} page.home.greeting",
                       f"腿④禁用會話詞｜{TW_NAME}:{g} page.home.greeting「踢下線」",
                       f"腿④頂替鍵缺「頂替」｜{SESSION_KICKED_KEY}（{TW_NAME}:{k}）",
                       f"腿④頂替鍵含「管理員」｜{SESSION_KICKED_KEY}（{TW_NAME}:{k}）"):
            self.assertIn(phrase, text)

    def test_leg2_lists_each_unclassified_char_once(self):
        """腿②逐字一行：兩個未分類字各一行；同字重現於他鍵不重報"""
        tw = _ts(_tw(page={"home": {"greeting": "鬱黴", "b": "鬱"}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        for ch in "鬱黴":
            self.assertIn(f"腿②字表未分類｜「{ch}」首見 {TW_NAME}:{_line_of(tw, '鬱黴')} page.home.greeting", text)
        self.assertEqual(text.count("腿②字表未分類｜"), 2, text)

    def test_leg3_lists_each_term_in_one_key(self):
        """腿③同鍵逐詞出列：一鍵含兩個大陸用語各一行"""
        tw = _ts(_tw(page={"home": {"greeting": "請完成設置並保存"}}))
        rc, text = _judge(tw)
        self.assertEqual(rc, 1, text)
        for term, advice in (("設置", "設定"), ("保存", "儲存")):
            self.assertIn(f"腿③大陸用語｜{TW_NAME}:{_line_of(tw, '請完成')} page.home.greeting「{term}」→ 臺灣用語「{advice}」", text)
        self.assertEqual(text.count("腿③大陸用語｜"), 2, text)


class TestCjkRanges(unittest.TestCase):
    """腿②碼位：統一區、擴充 A～J、兩相容區之邊界屬之；部首、符號、注音、標點與 ASCII 不屬之。"""

    def test_range_bounds(self):
        inside = ("\u3400", "\u4dbf", "\u4e00", "\u9fff", "\uf900", "\ufaff", "\U00020000", "\U0002a6df", "\U0002ee5d",
                  "\U0002f800", "\U0002fa1f", "\U00030000", "\U000323af", "\U0003347f")
        outside = ("\u33ff", "\u4dc0", "\u3007", "\u2e80", "\u2f00", "\u3105", "\uff0c", "\u3001", "\ufb00", "\U0001ffff",
                   "\U0002fa20", "\U00033480", "A")
        self.assertEqual([hex(ord(c)) for c in inside if not is_cjk(c)], [])
        self.assertEqual([hex(ord(c)) for c in outside if is_cjk(c)], [])


class TestTables(unittest.TestCase):
    """表值形制釘（真表）：字表單字、建議非簡化字、兩表不相交、同形異用組、用語表必收詞、同形異用字詞條分組、禁用會話詞表、踢除語境鍵名冊。"""

    REQUIRED_TERMS = ("用戶", "默認", "登錄", "註銷", "退出登錄", "菜單", "設置", "數據", "信息", "網絡", "軟件", "程序", "支持", "激活",
                      "賬號", "服務器", "緩存", "內存", "打印", "導入", "導出", "搜索", "刷新", "創建", "保存", "郵箱", "鏈接", "圖標",
                      "字體", "模塊", "加載", "視頻", "屏幕", "全屏", "質量", "于", "后台", "以后", "之后", "然后", "最后", "里面", "常量")

    def test_simplified_table_shape(self):
        self.assertIsInstance(SIMPLIFIED_CHARS, types.MappingProxyType)
        for ch, advice in SIMPLIFIED_CHARS.items():
            self.assertTrue(len(ch) == 1 and is_cjk(ch), ch)
            self.assertTrue(all(part and all(is_cjk(c) for c in part) for part in advice.split("／")), (ch, advice))
            self.assertFalse(set(advice) & set(SIMPLIFIED_CHARS), (ch, advice))

    def test_approved_table_shape(self):
        self.assertIsInstance(APPROVED_CHARS, frozenset)
        for group in (_APPROVED_PLAIN, _APPROVED_HOMOGRAPHS):
            self.assertEqual(len(set(group)), len(group))
            self.assertTrue(all(is_cjk(c) for c in group))
        self.assertFalse(set(_APPROVED_PLAIN) & set(_APPROVED_HOMOGRAPHS))
        self.assertEqual(APPROVED_CHARS, frozenset(_APPROVED_PLAIN) | frozenset(_APPROVED_HOMOGRAPHS))

    def test_real_tables_are_sound(self):
        self.assertEqual(table_faults(SIMPLIFIED_CHARS, APPROVED_CHARS, MAINLAND_TERMS, EXEMPT), [])

    def test_adr_named_homographs_stay_out_of_leg1(self):
        for ch in "于后台适":
            self.assertIn(ch, _APPROVED_HOMOGRAPHS)
            self.assertNotIn(ch, SIMPLIFIED_CHARS)

    def test_big5_variant_forms_are_leg1_not_homographs(self):
        """Big5 收錄之異體字形九字（取捨見表旁③）歸 SIMPLIFIED_CHARS、不在 APPROVED_CHARS：zh-tw 漏改即腿①紅、附正字建議"""
        variants = "确网与挂触异昵优构"
        self.assertEqual([c for c in variants if c not in SIMPLIFIED_CHARS or c in APPROVED_CHARS], [])
        self.assertEqual("".join(SIMPLIFIED_CHARS[c] for c in variants), "確網與掛觸異暱優構")
        rc, text = _judge(_ts(_tw(page={"home": {"greeting": variants}})))
        self.assertEqual(rc, 1, text)
        for ch in variants:
            self.assertIn(f"page.home.greeting「{ch}」→ 正體建議「{SIMPLIFIED_CHARS[ch]}」", text)

    # 同形異用字詞條之必收形：兩檔現用之大陸用法詞（zh-cn 漏改入 zh-tw 即腿①不報之漏網形）。
    REQUIRED_HOMOGRAPH_TERMS = ("丰富", "多云", "主体", "其余", "准備", "下划線", "复制", "複制", "后台", "稍后", "后再", "失敗后", "建立后",
                                "頁面后", "啟用后", "重連后", "成功后", "變更后", "复原", "恢复", "重复", "合并", "并且", "選擇并", "閱讀并",
                                "數据", "手机", "打字机", "隨机", "注冊", "備注", "离開", "規范", "推荐", "谷歌", "适用", "适合", "合适",
                                "自适應", "采用")

    def test_mainland_terms_shape_and_required_words(self):
        self.assertIsInstance(MAINLAND_TERMS, types.MappingProxyType)
        self.assertTrue(all(term and advice for term, advice in MAINLAND_TERMS.items()))
        self.assertEqual([t for t in self.REQUIRED_TERMS if t not in MAINLAND_TERMS], [])
        self.assertEqual([t for t in self.REQUIRED_HOMOGRAPH_TERMS if t not in MAINLAND_TERMS], [])

    def test_homograph_terms_partition_and_shape(self):
        """每個同形異用字恰屬「有詞條組」或「_HOMOGRAPHS_NO_TERM 附理由」之一；組非空、組內詞皆含該字且不含簡化字（腿①不報之漏網形）、
        建議不含該字亦不含簡化字；全組詞跨組不重複、皆以同一建議併入 MAINLAND_TERMS"""
        groups, no_term = set(_HOMOGRAPH_TERMS), set(_HOMOGRAPHS_NO_TERM)
        self.assertEqual(groups | no_term, set(_APPROVED_HOMOGRAPHS))
        self.assertEqual(groups & no_term, set())
        self.assertEqual([ch for ch, why in _HOMOGRAPHS_NO_TERM.items() if not why], [])
        self.assertEqual([ch for ch, group in _HOMOGRAPH_TERMS.items() if not group], [])
        pairs = [(ch, term, advice) for ch, group in _HOMOGRAPH_TERMS.items() for term, advice in group.items()]
        self.assertEqual(len({term for _, term, _ in pairs}), len(pairs))
        for ch, term, advice in pairs:
            self.assertIn(ch, term)
            self.assertEqual(set(term) & set(SIMPLIFIED_CHARS), set(), term)
            self.assertTrue(advice and ch not in advice and not set(advice) & set(SIMPLIFIED_CHARS), (term, advice))
            self.assertEqual(MAINLAND_TERMS.get(term), advice, term)

    def test_banned_session_terms_are_pinned(self):
        """禁用會話詞六詞之值釘（007 刀 contracts code-gates §2.1 腿④）：自測④e 逐詞迭代本常數，本釘封縮表"""
        self.assertEqual(BANNED_SESSION_TERMS, ("踢出", "踢掉", "踢下線", "擠下線", "擠掉", "頂掉"),
                         "禁用會話詞增減須同批改本斷言")

    def test_admin_kick_keys_are_pinned(self):
        self.assertEqual(ADMIN_KICK_KEYS, frozenset({
            "backend.auth.session.kickedByAdmin", "backend.biz.user.cannotKickSelf",
            "page.manage.user.kick", "page.manage.user.confirmKick", "page.manage.user.kickSuccess"}),
            "踢除語境鍵增減須同批改本斷言（ADR-00084 決定 7④）")


class TestInvariants(unittest.TestCase):
    """白名單與表之五釘：對本檔自身之常數與原文判，各封一條繞道、互不覆蓋（射程自陳見檔頭）。"""

    TABLES = ("SIMPLIFIED_CHARS", "APPROVED_CHARS", "MAINLAND_TERMS", "ADMIN_KICK_KEYS", "EXEMPT")
    BANNED_JUDGE = ("open(", "read_text", "read_bytes", "environ", "getenv", "argv", "stdin", "input(", "json")
    BANNED_CALLER = ("environ", "getenv", "argv", "stdin", "input(", "json")

    @staticmethod
    def _module_tree():
        return ast.parse(inspect.getsource(sys.modules[__name__]))

    def test_exempt_count_is_pinned(self):
        """項數恆定：現為零筆（增列須同批改本斷言、於 diff 現形）"""
        self.assertIsInstance(EXEMPT, tuple)
        self.assertEqual(len(EXEMPT), 0, "EXEMPT 增減列須同批改本斷言（ADR-00084 決定 7）")

    def test_check_passes_tables_verbatim(self):
        """呼叫點原封傳入：run_check 內恰一處 judge 呼叫、七個位置實參、末五實參依序為四表與 EXEMPT 本名"""
        fn = next(n for n in ast.walk(self._module_tree()) if isinstance(n, ast.FunctionDef) and n.name == "run_check")
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "judge"]
        self.assertEqual(len(calls), 1, "run_check 內 judge 呼叫須恰一處")
        self.assertEqual((len(calls[0].args), calls[0].keywords), (7, []), ast.dump(calls[0]))
        self.assertEqual([a.id if isinstance(a, ast.Name) else None for a in calls[0].args[2:]], list(self.TABLES))

    def test_judgement_path_has_no_external_input_forms(self):
        """判定路徑零外部取值形：詞法、解析與判定函式不得出現讀檔／環境／命令列／stdin／json 字面；run_check 只准讀檔"""
        for fn in (is_cjk, _unescape, _skip_interpolation, tokenize, _at, _find_root, _parse_value, _parse_object, _scan_outside_root,
                   parse_locale, table_faults, judge):
            src = inspect.getsource(fn)
            for tok in self.BANNED_JUDGE:
                self.assertNotIn(tok, src, f"{fn.__name__}() 出現 {tok!r}")
        src = inspect.getsource(run_check)
        for tok in self.BANNED_CALLER:
            self.assertNotIn(tok, src, f"run_check() 出現 {tok!r}")

    def test_callers_never_mutate_or_rebind_tables(self):
        """呼叫端零就地改表：四表與 EXEMPT 皆不可變型、全檔各恰一處綁定且無 global 宣告；EXEMPT 測試類以外恰一處引用"""
        for value in (SIMPLIFIED_CHARS, MAINLAND_TERMS):
            self.assertIsInstance(value, types.MappingProxyType)
        for value in (APPROVED_CHARS, ADMIN_KICK_KEYS):
            self.assertIsInstance(value, frozenset)
        tree = self._module_tree()
        for name in self.TABLES:
            stores = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == name and not isinstance(n.ctx, ast.Load)]
            self.assertEqual(len(stores), 1, f"{name} 綁定處須恰一（模組層定義）")
            self.assertFalse([n for n in ast.walk(tree) if isinstance(n, (ast.Global, ast.Nonlocal)) and name in n.names])
        loads = [n for top in tree.body if not isinstance(top, ast.ClassDef)
                 for n in ast.walk(top) if isinstance(n, ast.Name) and n.id == "EXEMPT" and isinstance(n.ctx, ast.Load)]
        self.assertEqual(len(loads), 1, f"測試類以外 EXEMPT 引用 {len(loads)} 處（應恰 1＝傳進 judge 之末實參）")

    def test_exempt_definition_is_pure_literal(self):
        """白名單定義為純字面：模組層（頂層敘述）恰一處以 EXEMPT 為唯一目標之指派、其值經 ast.literal_eval 成立——
        取自環境變數、讀檔、命令列或任何呼叫、名稱引用、運算式皆非字面＝紅；定義改置於條件區塊或解構指派內＝頂層零處＝紅"""
        defs = [n for n in self._module_tree().body
                if isinstance(n, ast.Assign) and [getattr(t, "id", None) for t in n.targets] == ["EXEMPT"]
                or isinstance(n, ast.AnnAssign) and getattr(n.target, "id", None) == "EXEMPT"]
        self.assertEqual(len(defs), 1, "EXEMPT 須恰一處頂層定義")
        try:
            ast.literal_eval(defs[0].value)
        except ValueError:
            self.fail("EXEMPT 之定義須為純字面 tuple（不得取自 args／env／讀檔，ADR-00084 決定 7）")


class TestUsage(unittest.TestCase):
    def test_unknown_subcommand_or_extra_args_is_rc64(self):
        for argv in (["zh-tw-lint.py", "nope"], ["zh-tw-lint.py", "check", "x"], ["zh-tw-lint.py", "test", "x"]):
            err = io.StringIO()
            with self.subTest(argv=argv[1:]), contextlib.redirect_stderr(err):
                self.assertEqual(main(argv), RC_USAGE)
            self.assertIn("用法：", err.getvalue())

    def test_self_test_failed_or_skipped_is_rc2(self):
        """test 子命令：自測有敗、或全過而有略過＝rc 2（self-test 敗亦 2）；全過零略過＝rc 0——以假結果替換 unittest.main、不遞迴實跑"""
        for ok, skipped, rc in ((False, [], RC_STRUCT), (True, [("案", "略")], RC_STRUCT), (True, [], RC_OK)):
            result = types.SimpleNamespace(testsRun=1, failures=[] if ok else [("案", "敗")], errors=[], skipped=skipped,
                                           wasSuccessful=lambda ok=ok: ok)
            out = io.StringIO()
            with self.subTest(ok=ok, skipped=len(skipped)), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out), \
                    unittest.mock.patch.object(unittest, "main", return_value=types.SimpleNamespace(result=result)):
                self.assertEqual(main(["zh-tw-lint.py", "test"]), rc)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    if len(argv) > 2 or cmd not in ("check", "test"):
        _say(USAGE, err=True)
        return RC_USAGE
    if cmd == "test":
        result = unittest.main(argv=[argv[0]], exit=False, verbosity=1).result
        _say(f"{TAG} self-test：執行 {result.testsRun} 案、失敗 {len(result.failures)}、錯誤 {len(result.errors)}、略過 {len(result.skipped)}（skipped={len(result.skipped)}）")
        if result.wasSuccessful() and not result.skipped:
            _say(f"{TAG} ✓ self-test 過")
            return RC_OK
        return RC_STRUCT
    rc, lines = run_check(REPO_ROOT)
    for ln in lines:
        _say(ln, err=bool(rc))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
