---
id: "ADR-00100"
title: 存取日誌寫入中介層——掛兩受保護子 router 之 enforce_mw 內側（包住授權判定、`5003` 照記為 403）、回應先回後非同步寫、寫入併發號誌上界 2（等待不丟列）、fail-open（warn＋降級計數）；狀態欄只見 200 與 403；解除 004 刀防回歸清單 B 之 `rev5:R2-9`
date: 2026-10-21
status: accepted
supersedes: []
superseded_by: []
provenance: "008-audit-settings-pages 之 spec FR-021～FR-025、US4、SC-006、Edge Cases「存取日誌」、clarify Q2（照 rev4 欄形只記 HTTP 狀態碼＋存取分頁告示）；brainstorm §0 B2、主線工程判斷⑧㉒；plan 期 research R9（掛點、R3 對策、狀態欄 as-built）與 spec 修補 E1（告示只提 403；緣起＝user 2026-10-21 轉來 side agent 提醒、與主線取證同結論；user 2026-10-21 plan 期 AskUserQuestion 親決「只提 403」後套入 spec）；藍本＝rev4:server/src/middleware/mod.rs 之 `access_log_mw` 與 rev4:server/src/router.rs 之層序；被解除面＝004 刀 research 防回歸清單 B 之 `rev5:R2-9`（存取軌跡中介層不搬；其 rev5 原因＝歸 `rev5:B-016` 稽核域射程、非否決判斷）"
tags: [audit, access-log, middleware, island-j, observability]
---

## 背景

- `sys_access_log` 自 001 基線在庫、零寫入者（BL-00043）；rev5 存取分頁讀空表（`rev5:R2-9` 不搬）。本刀 B2 拍板「做、加寫入中介層」，照 rev4 形重打。
- rev6 中介層序＝`request_context_mw`→`ip_gate_mw`→（兩受保護子 router）`enforce_mw`→（Policy 條目）`require_policy`→handler；兩道 fallback（未註冊路徑、動詞不符＝`4040`）掛在合併後外層。
- 業務 handler 零 `AppError::NotFound` 構造（生產構造點恰為 `router.rs` 兩道 fallback）。
- 真庫測試連 dev 庫；每請求一寫會使全套件留下大量列（R3）。

## 考慮過的替代案

1. **掛在授權判定之後**——被拒請求無列；違 clarify Q2 前提（403 可辨）；否決（㉒ 更正）。
2. **同步寫入**——寫入延遲直接加到回應；違 J2；否決。
3. **每請求無上限 spawn（rev4 形）**——洪峰時寫入任務與業務請求搶連線池；否決。
4. **單一寫入者佇列（有界 mpsc）**——上界 1 連線，但佇列滿即丟列、且需開機接線與測試 drain 兩套；否決。
5. **號誌 `try_acquire` 失敗即丟**——違「每筆已登入請求一列」；否決。
6. **加業務碼欄**——破 §I.5 例外② 基線 entity 逐位元承襲；clarify Q2 已否決。

對所選方案跑同一反例（RL-0013）：「洪峰佔滿連線池」→上界 2、不成立；「丟列」→等待許可、不成立；「被拒請求無列」→包住授權判定、不成立；「認證失敗也記」→enforce_mw 早退於外、不成立。

## 決定

1. **掛點**：`router::build_from` 之 Authed 與 Policy 兩子 router 各掛 `access_log_mw`，位於該子 router `enforce_mw` 之內側（先掛）；Public 子 router 與兩道 fallback 不掛。`router.rs` 層序源碼釘值測擴列。
2. **欄位**：`created_by`＝`Identity.uid`；方法；`uri().path()`（不含 query、不讀 body）；`response.status()`；來源四欄轉錄請求上下文（`real_ip` 解析不成＝跳過）；region／trace_id NULL。
3. **非同步**：回應先回；寫入於 `tokio::spawn` 任務內進行；身分或上下文缺席＝跳過（不 panic、不 500）。
4. **併發上界**：層狀態持號誌（許可 2；碼內常數）；任務內等待許可後才取連線寫入；連線池設定零改動（BL-00147 之臂不觸）。
5. **fail-open**：寫入失敗＝`tracing::warn!(target: "audit.access_log", degraded = "access_log_write", …)`＋`access_log_write_failed_total` +1；業務回應零影響。告警 ③d（loki、target 與 degraded 欄）依此 as-built 欄形重錨（規則體不動、現況註改）。
6. **測試面**：在途計數（spawn 前 +1、任務結束 −1）供測試 drain；`AccessLogRowsGuard`（tests 側 `AccessLogWriteGuard`；`max(id)` 水位、不動序列）兩層各一；drain 於帶守衛 app 之逐回應層（await 在途歸零）、Drop 先確認在途歸零再清（`#[tokio::test]` 預設 current-thread runtime、同步 Drop 內等待恆逾時；current-thread 在途非零＝先清後 fail-loud）；app 建構 helper 內部帶守衛＝全套件零殘列（驗收＝全量測試前後列數相等）。
7. **狀態欄語意**：只見 200 與 403（業務拒因與系統錯誤皆 200；`4040` 不經記錄層＝零列）＝已知態；存取分頁告示只提 403；spec、活書 08 與 RUNBOOK §11 寫明。
8. **runtime-append**：`tools/schema-gate.py` 與 `tools/walkthrough-baseline.py` 之 `RUNTIME_APPEND_TABLES` 同值擴入 `sys_access_log`、還原集同批。
9. **解除**：004 刀 research 防回歸清單 B 之 `rev5:R2-9` 自本 ADR accepted 起不再適用（射程＝本 ADR 決定 1～8 之形；rev4 之 region 解析與 xdb 不帶）。

## 後果

- 存取日誌每已認證請求一列：量隨流量線性成長，audit-capacity 告警（四表 > 1,000,000）之觸發可能較早——處置＝稽核頁清理或 reaper 排程清理（RUNBOOK §11）。
- 資料庫故障期間待寫任務於記憶體排隊（同期業務請求亦失敗）；恢復後消化。
- 測試基建一次落：守衛隨 Router clone 走、app 建構 helper 內部帶守衛（呼叫點零改寫；直呼與 stub 案由測試基建單元現算處置）。
- 稽核頁可見自身請求（無豁免名單）。
- 零列已知態兩則（by-design）：被 IP 存取閘擋下之請求（閘在驗章之前＝未認證；帶有效權杖亦然）與回應產生前即被丟棄之已認證請求（用戶端中斷、逾時；寫入於回應產生後才排程）皆不落存取日誌列——阻擋紀錄住閘門結構化告警（target `security.ipgate`）與 `ipgate_blocked_total`（spec Edge Cases「存取日誌」末條）。
- 停機丟棄在途寫入（by-design）：行程停機（graceful shutdown）時尚在等候號誌許可或寫入中之任務隨 runtime 結束被丟棄＝等候許可者該列不落、寫入中者視 INSERT 是否已送達庫端而定（已送達者仍可能落列、照計失敗）；在途 RAII 件未結案即 Drop 時補發與寫入失敗同形之 warn 並計入 `access_log_write_failed_total`（J2「寫入失敗 MUST 只發結構化告警」；`server/src/main.rs` 零改、不延長停機）。

## 翻案觸發器

- 出現連線池等待或 p95 延遲因存取日誌上升之觀測 ⇒ 重評號誌上界或改單一寫入者形。
- 需要業務成敗入存取日誌 ⇒ 另立 ADR（涉 §I.5 例外②）。
- 出現 trace_id 或 region 料源 ⇒ 同批填欄。

## 親決分類

依 ADR-00089（RL-0086）；類別定義同 ADR-00099 本節。

| 款 | 類別 | 出處或理由 | 白話一句 |
|---|---|---|---|
| 決定 1 | 承決 | brainstorm ㉒；spec FR-021、US4 第 2～3 條 | 記錄層在登入檢查之後、權限判定之外，被權限擋下的也記。 |
| 決定 2 | 承決 | spec FR-022、clarify Q2 | 記誰、什麼方法、哪個路徑（不含查詢字串）、HTTP 狀態碼與來源位址。 |
| 決定 3 | 承決 | spec FR-023、US4 第 5～6 條 | 先回應再背景寫入，缺身分就跳過。 |
| 決定 4 | 承決 | spec FR-024（不改動連線池設定）、Edge Cases「存取日誌」（R3 對策於 plan 期定；號誌上界 2 與等待不丟為款內工程細節、research R9.4） | 同時最多兩個寫入佔用資料庫連線，排隊等、不丟；連線池設定不動。 |
| 決定 5 | 承決 | spec FR-023、FR-043（③d 依 as-built 重錨） | 寫不進去只告警與計數，不影響回應。 |
| 決定 6 | 工程 | research R9.4、spec FR-070 | 測試等背景寫完再清掉自己寫的列。 |
| 決定 7 | 承決 | user 2026-10-21 plan 期 AskUserQuestion 答「只提 403（建議）」（原標待決：clarify Q2 題面範例含「找不到 404」、改只提 403 之緣起為 user 轉來之 side agent 提醒）；spec FR-009、FR-055、Edge Cases「存取日誌」（E1 已套） | 狀態欄只會看到 200 和 403，告示只講 403。 |
| 決定 8 | 承決 | spec FR-025 | 走查與結構閘工具把存取日誌當成會自然長資料的表。 |
| 決定 9 | 承決 | brainstorm B2；spec FR-024 | 前代「不搬存取軌跡中介層」的限制解除。 |

- **親決紀錄**：（plan 期）待決 1 款（決定 7）於 plan 期 AskUserQuestion 一題：user 2026-10-21 答「只提 403（建議）」（作答時 HEAD＝`926b359`、本 ADR 草稿未入版控），同日套入 spec（E1）並改標承決。獨立核對（ADR-00089 決定 5；2026-10-21）：9 列中相符 7（決定 1～3、5、6、8、9）、改正 2（決定 4 依混類取最高改標承決並補 spec 出處；provenance 之 E1 註記早於作答即寫成已套、今作答後套入）、升待決 0。改過之款於轉 accepted 前依 ADR-00089 決定 6② 復核。tasks 期改字（2026-10-21；tasks 起草稿實證）：決定 6 之 drain 位置（逐回應層）與 Drop 語意、後果之 helper 改寫句＝工程款改字、依決定 6② 復核。analyze 期增句（2026-10-21；`62f8a4c`、user 核可 analyze 修補全套）：後果增「零列已知態兩則」與「停機丟棄在途寫入」兩條（承 spec Edge Cases「存取日誌」末條；決定 1～9 未動）、依決定 6② 復核。U0 收尾（2026-10-23；008 刀 tasks T004；ADR-00089 決定 6）：分類（以對照表現算）＝9 列：承決 8、工程 1、待決 0。①作答後改字之重問：無（決定 7 作答後款文未改）。②復核：T002 首輪（十 lens＋逐 lens 反駁＋完整性 critic）本 ADR 三筆＝主線裁定改正（後果「停機丟棄在途寫入」句精確化為等候許可者不落、寫入中者視 INSERT 是否已送達；決定 6 補 current-thread 在途非零先清後 fail-loud；親決紀錄補 analyze 增句）；T004 復核輪（三 lens＋逐 lens 反駁＋完整性評審）三處改字相符、一筆僅記錄（停機丟棄之同義改字另含 tasks 需求追溯 E24#5，併入施工前提顆連帶）。③對照表收尾一題（T004 第 6 題；作答時 HEAD `8ceadb5`）答「照表定稿（建議）」、拉出 0 款。實問題數＝U0 1 題；連同 plan 期 1 題共 2 題。出題錯字（user 所見）0（送出前比對 hook 擋下 1 起碼位漂移、user 未見；LL-00099）。
