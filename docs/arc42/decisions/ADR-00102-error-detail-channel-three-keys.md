---
id: "ADR-00102"
title: 錯誤明細通道射程恰三鍵（續行 ADR-00076）——新增 `biz.audit.purgeBelowFloor` 攜 `{minDays}`（具名明細型 `PurgeBelowFloorDetail`、單一組裝件、家＝稽核 handler）；msg-key-gate 明細型之家改逐鍵對映；並釐清「照提示秒數重試必過」只在牆鐘單調且冷卻設定未改時成立（ADR-00076 決定 1 冷卻列改寫、ADR-00090 決定 1 立釐清款不 supersede）
date: 2026-10-21
status: accepted
supersedes: ["ADR-00076"]
superseded_by: []
provenance: "008-audit-settings-pages 之 spec FR-004、FR-016②、US3 第 1 條、SC-002；brainstorm §0 D7（照 rev5：拒因攜 `{minDays}`；新 ADR 整顆 supersede ADR-00076、另一款釐清 ADR-00076／ADR-00090 決定 1 之「必過」）、主線工程判斷⑲（RL-0080 判讀於 plan 期定）；plan 期 research R13；被續行面＝ADR-00076 決定 1～7（body 已 accepted 不可變、rev6 無部分翻案機制＝ADR-00011 決定 5）；被釐清面＝ADR-00090 決定 1（射程釐清不 supersede；前例 ADR-00090 決定 5）；LL-00054（牆鐘回撥）；藍本＝rev5:server/src/handler/audit.rs 之 purge 固定序②（`rev5:B-139` 之第三攜參鍵）"
tags: [error-envelope, i18n, audit, msg-key-gate]
---

## 背景

- ADR-00076 標題與決定 1 定射程「恰兩鍵」；D7 拍板清理下限拒因攜 `{minDays}`＝射程擴為三鍵，ADR-00076 之標題句被推翻。
- ADR-00076 決定 1 冷卻列寫「時鐘回撥時上限 I——照提示秒數重試必過」、ADR-00090 決定 1 寫「時鐘回撥上限 I——照提示秒數重試必過」；牆鐘回撥使經過秒數可為負，等待提示秒數後伺服端計得之經過仍可能不足、或冷卻設定於等待期間被調大——「必過」不成立。
- msg-key-gate 之佔位符對賬讀明細型序列化欄名，明細型之家寫死單檔（`handler/user.rs`）。

## 考慮過的替代案

1. **第三鍵以 `serde_json::json!` 字面構造（rev5 形）**——明細鍵名脫離型別層單一出處、佔位符對賬無型可讀；否決。
2. **三型集中一檔**——搬動 007 兩型、與「明細型與組裝件同住」相悖；否決。
3. **ADR-00090 一併 supersede**——該 ADR 其餘決定不變、只釐清一句；否決（釐清款）。

對所選方案跑同一反例（RL-0013）：「第三鍵譯文佔位符與後端鍵名分岔、明細靜默消失」於所選形？佔位符對賬讀 `PurgeBelowFloorDetail` 序列化鍵、改名即紅；不成立。

## 決定

本 ADR 續行並將 supersede ADR-00076（accepted 同顆補 `supersedes: ["ADR-00076"]`、ADR-00076 status 改 superseded）。ADR-00076 決定 1～7 對應本 ADR 同號：

1. **射程恰三鍵、其餘恆純 key（改寫）**：①`biz.user.passwordPolicy`（`violations`；續行）②`biz.user.pwdSetTooFrequent`（`remainingSeconds`＝`min(max(I−⌊Δ⌋, 1), I)`；續行，惟將「時鐘回撥時上限 I——照提示秒數重試必過」改寫為「上限 I；提示秒數為等待之估計——牆鐘單調且冷卻設定未改時照提示秒數重試即過，牆鐘回撥或設定調大時可再被擋、回新的剩餘秒數」）③**`biz.audit.purgeBelowFloor`**（`minDays`＝`PURGE_MIN_DAYS`；新增；構造點＝purge 固定序②、組裝件 `purge_below_floor_err`、明細型 `PurgeBelowFloorDetail { min_days: u64 }`（值＝`PURGE_MIN_DAYS.unsigned_abs()`；先例 `PwdSetTooFrequentDetail` 之 u64）＋struct 級 `rename_all = "camelCase"`、住 `handler/audit.rs`）。
2. **受眾判準（續行）**：明細描述操作者自己剛送出之輸入的評估；第三鍵之下限天數為系統常數、不含他人資訊。
3. **錯誤變體（續行）**：`AppError::BizData`，變體數不變。
4. **信封出口分離（續行）**：`Res::from_err_with_data` 為攜明細之唯一出口。
5. **002 wire 契約之現行讀法（續行）**：錯誤 data 恆 null，惟本 ADR 決定 1 三鍵例外。
6. **前端（改寫）**：ADR-00076 決定 6 三子項續行，惟其中兩處「兩鍵」改「三鍵」——請求層明細轉譯「只認兩鍵」改「只認三鍵」（`translateBackendMsg` 第三分支以 `Api.Audit.PurgeBelowFloorDetail` 收窄、具名插值 `{minDays}`）；「兩鍵之 backend 子樹譯文帶具名插值佔位」改「三鍵之 backend 子樹譯文帶具名插值佔位」（第三鍵各語字面見 008 刀 contracts msg-keys §1）；其餘原文續行（其餘錯誤續呈純 key 提示、轉譯未命中一律 graceful fallback；違規子鍵單一共用命名空間 `page.passwordPolicy.*`；backend 子樹譯文之具名佔位名＝明細鍵名、`data` 形不合即退回純 key、backend 子樹只放 `MSG_KEYS` 成員）；條文字面由 ADR-00099 決定 11 承載（ADR-00076 決定 6 之「由 ADR-00074 親決」改讀此）。
7. **機器守（改寫）**：msg-key-gate `BIZ_DATA_KEYS` 三鍵、明細型之家逐鍵對映（兩鍵→`handler/user.rs`、一鍵→`handler/audit.rs`）；斷言 2 之 BizData 構造形判準（首引數須為 `Cow::Borrowed(字面｜msg_key::NAME)`、解出鍵 ∈ 名冊、動態構造＝紅）、射程守四句與佔位符對賬照舊；斷言 3 之 `FRONTEND_MSG_CONSUMERS` 照舊、擴第三鍵之請求層消費點；contract 腿（每鍵至少一案實發並斷言 `data` 形；其餘拒因續以 `assert_error_envelope` 斷 data null、名冊雙向閘照舊）與 wire 裁判腿（明細信封之 wire 型入受審名冊、配正向＋反例）照舊、擴第三鍵；pre-commit submodule-sync 閘面增新家；各腿一正一反（RL-0080；新家之欄改名與移家各一支變異）。
8. **ADR-00090 決定 1 之釐清款（新增；不 supersede）**：其「時鐘回撥上限 I——照提示秒數重試必過」讀作本 ADR 決定 1②之改寫字面；ADR-00090 其餘決定與後果不變。

## 後果

- ADR-00076 轉 superseded；現在式引用面改指本 ADR（機器枚舉、改完復掃）。
- 第三鍵之前端插值須 Amendment（ADR-00099 決定 11）。

## 翻案觸發器

- 出現第四個攜參需求 ⇒ 新 ADR 續行（射程不默擴）。
- 冷卻判定改用單調時鐘 ⇒ 決定 1② 之條件句可收回。

## 親決分類

依 ADR-00089（RL-0086）；類別定義同 ADR-00099 本節。

| 款 | 類別 | 出處或理由 | 白話一句 |
|---|---|---|---|
| 決定節導言 | 工程 | supersede 簿記＝GT-04；ADR-00076 決定 1～7 對應同號 | 舊 ADR 的七款逐款對應到這份。 |
| 決定 1 | 承決 | brainstorm D7；spec FR-004、FR-016②；「必過」改寫＝D7 題面所列釐清款、憲法 §I.7 跨島總則（設密冷卻秒數於每次設密讀現值＝設定調大時可再被擋） | 可帶參數的錯誤從兩支變三支，清理下限帶天數；冷卻秒數不保證照等必過。 |
| 決定 2 | 承決 | ADR-00076 決定 2 | 參數只描述你自己送出的內容。 |
| 決定 3 | 承決 | ADR-00076 決定 3；spec FR-004（變體數維持 11） | 不新增錯誤種類。 |
| 決定 4 | 承決 | ADR-00076 決定 4 | 帶參數的錯誤只有一個出口。 |
| 決定 5 | 承決 | ADR-00076 決定 5 | 錯誤的資料欄平常是空，只有三支例外。 |
| 決定 6 | 承決 | ADR-00076 決定 6（三子項續行）；brainstorm D7；spec FR-004（三語只放佔位符） | 前端多一支把天數填進提示，其餘轉譯規則照舊。 |
| 決定 7 | 工程 | research R13.3～R13.4（機器守之資料面擴列與變異） | 檢查工具認得第三支、它的定義位置與前端用到它的地方。 |
| 決定 8 | 承決 | brainstorm D7（另一款釐清 ADR-00090 決定 1） | 另一份 ADR 的「必過」同樣這樣讀，不另改它。 |

- **親決紀錄**：（plan 期）獨立核對（ADR-00089 決定 5；2026-10-21）：8 列中相符 5（決定 2～5、8）、改正 2（決定 1 出處補憲法跨島總則；決定 7 補 contract、wire 裁判兩腿與斷言 3 名冊之續行）、升待決 1（決定 6：改寫只剩一句、ADR-00076 決定 6 其餘子項無續行字面＝對出處少寫）、漏列 1（決定節導言）。處置：決定 6 改為「兩鍵→三鍵、其餘子項原文續行」後回承決（出處＝ADR-00076 決定 6、免問）、補導言列；改過之款於轉 accepted 前依 ADR-00089 決定 6② 復核。tasks 期改字（2026-10-21；tasks 起草稿實證）：決定 1③ 明細欄型 i64→u64（`tests/wire_i64_guard_lint.rs` 要 i64 wire 欄掛 2^53 守衛 serde 屬性或入 `EXEMPT_FIELDS`〔名冊語意＝非 wire〕，msg-key-gate 要明細型欄位零 serde 屬性＝兩者互斥）＝承決款改字（型別屬工程）、依決定 6② 復核。analyze 期改字（2026-10-21；`62f8a4c`、user 核可 analyze 修補全套）：背景與決定 8 所引 ADR-00090 決定 1 改為其原字面「時鐘回撥上限 I——照提示秒數重試必過」（原稿誤作 ADR-00076 決定 1 冷卻列之「時鐘回撥時上限 I」），背景同句另列 ADR-00076 決定 1 冷卻列原字面＝背景為非款文、決定 8 為承決款改字、依決定 6② 復核。U0 T002 停手升級改正（2026-10-23；`c091448`；user 2026-10-22 裁定「T003 前另落一顆只改 ADR-00102（建議）」，作答時 HEAD＝`6036cb9`）：決定 6 兩處「兩鍵」皆改「三鍵」（第三鍵各語字面指 008 刀 contracts msg-keys §1）、決定 1② 替換文去起首「下限 1、」、決定 7 補回斷言 2 之 BizData 構造形判準與 contract 腿之 `assert_error_envelope`／名冊雙向閘；改後復核輪（三 lens＋逐 lens 反駁＋完整性 critic）判決定 1、2、6、7、8 與全檔一致、無停手升級事項。U0 收尾（2026-10-23；008 刀 tasks T003／T004；ADR-00089 決定 6）：分類（以對照表現算）＝9 列：工程 2、承決 7、待決 0。①作答後改字之重問：無。②復核：T002 首輪之停手升級事項（決定 6、決定 1 冗字、決定 7 漏兩腿）＝`c091448` 改正（見上），改正後復核輪相符；T004 復核輪（本 ADR 親決紀錄改字史）相符、決定 1、2、6 對 `8ceadb5` 零改動。③對照表收尾一題（T003 第 4 題；作答時 HEAD `be11a3d`）答「照表定稿（建議）」、拉出 0 款（決定 1、2、6 為憲法 I18N (i) 末句所指，於 Amendment 顆 `8ceadb5` 之前定稿）。實問題數＝U0 2 題（停手升級處置 1、收尾 1）；plan 期 0 題。出題錯字（user 所見）0。T004 ④ 時序：Amendment 顆 `8ceadb5` 起，憲法 I18N (i) 末句已指本 ADR（其時 proposed）；本 ADR 於施工前提顆 accepted 後才指向現行 ADR；兩顆之間零施工單元，為唯一之 proposed 指向窗。決定 1、2、6 對 Amendment 顆零改動（status、supersedes 與親決紀錄除外）。
