---
id: "ADR-00067"
title: 判定面同步觸發列增列——授予面三支 Applied 即觸發（含空 diff、刻意例外）與 restorePolicy Applied 觸發，與移除面「成功且實際歸檔 ≥1 列」三類並陳；已知降級窗改記兩窗（commit→換上之有界過渡窗＋重試耗盡窗）、補述 ADR-00043 決定 9、不 supersede ADR-00043
date: 2026-10-01
status: proposed
supersedes: []
superseded_by: []
provenance: "006-authz-governance 之 spec FR-041⑤、FR-017～FR-020、SC-006、Edge Cases 之「判定面同步與生效時點」段、刻意分岔登記表「已知降級窗之條文」列；brainstorm §0 Q6（BL-00134 記窗）／Q13（生效兩層時點）與主線工程判斷⑤（授予面 Applied 即觸發含空 diff 照 rev5 HEAD）／⑥（觸發列以新 ADR 增列、不 supersede ADR-00043）；BL-00134（spec-compliance-005 L4-1、user 2026-09-30 裁交本刀 brainstorm）；被補述面＝ADR-00043 決定 6／決定 7（末句預授「其觸發列由該刀 ADR 增列」）／決定 9，與 ADR-00042 決定三之 H2 引文與差異附表 H2 列之「唯一已知降級窗」字面；藍本＝rev5:ADR 0053 款四（grant 面 Applied 即觸發不問 diff＝刻意例外、回收桶 Applied 觸發之矩陣列與並陳理由）、rev5 v1.10.0 島 G1 條文、rev5:server/src/auth/enforce.rs 之 reload_enforcer doc 觸發矩陣；過渡窗之記載為 rev6 新增（前代只記耗盡窗）；rev6 既有件＝rust-api/server/src/auth/enforce.rs 之 reload_enforcer／RELOAD_SERIAL／RELOAD_MAX_ATTEMPTS／RELOAD_RETRY_BACKOFF_MS、rust-api/server/src/handler/role.rs 之 settle_domain_write（取消安全收場形）、rust-api/server/tests/authz_entrypoint_lint.rs 之 RELOAD_CALL_FILES／ENFORCER_WRITE_FILES、casbin_reload_total 與 deploy/grafana-provisioning/alerting/rules.yml 之告警規則 obs016-casbin-reload-anomaly；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [authz, casbin, enforcer, reload, known-state, authz-governance]
---

## 背景

- ADR-00043 立判定面同步機制（全新重建後一步換上、保留上一份、`RELOAD_SERIAL` 全程互斥、有界重試），觸發矩陣恰五支移除面寫端、門＝「成功且實際歸檔 ≥1 列」（決定 7）；該款末句預授：「授權治理刀之授權寫端屆時純消費同一支 `reload_enforcer`、零新機制，其觸發列由該刀 ADR 增列」。本 ADR 即該增列之承載。
- 本刀新增四支會改動授權真相 `casbin_rule` 的寫端：三維授權寫端 updateRoleMenu／updateRoleButton／updateRoleEndpoints（授予面；全量替換、射程＝候選集＝ADR-00066）與授權回收桶 restorePolicy（回灌端點維授權）。前代 as-built 之觸發形＝grant 面 `Applied` 即觸發、不問 diff（刻意例外）、回收桶 `Applied` 觸發（`rev5:ADR 0053` 款四；rev5 v1.10.0 島 G1 條文同句）。rev6 移除面比前代多 deleteRole／batchDeleteRole 兩支（ADR-00043 決定 7、ADR-00044 決定 2），故增列後觸發者＝移除面五支＋授予面三支＋復原一支。
- 降級窗之字面失準（BL-00134）：憲法島 H2、ADR-00042 決定三之 H2 引文與其差異附表 H2 列、ADR-00043 決定 9 皆稱重試耗盡窗為「唯一已知降級窗」。實際上 commit 與換上之間另有一段窗：選單序列化域鎖為交易級（`pg_advisory_xact_lock`）、標的列鎖亦隨交易，commit 即一併釋放；判定面重建換上在 commit 之後（一次重建，失敗重試另加線性退避，`RELOAD_SERIAL` 排隊另加等候）。005 刀時期此窗只及 UI 可見性（刪除後同路由名或同代碼重建者，其選單與按鈕讀端短暫讀到舊面）；本刀起端點維撤銷與授予使之**及於 API 授權**。
- 前代 rev5 只記耗盡窗；user 於 brainstorm Q6 裁「記窗」（如實記兩窗、零碼改），不關窗。

## 決策驅動因子

- 判定面與授權真相之分歧窗必須全數如實入帳：條文寫「唯一」而實有兩窗＝權威文件失準。
- 授予面之同步觸發必須不依賴 diff 計算之正確性：diff 算錯時仍須同步，否則判定面與真相分歧而無任何告警。
- 零新機制（FR-018）：純消費 ADR-00043 之同步件、既有計數與告警。
- ADR-00043 已 accepted、body 不可變（GT-04），其決定 7 末句已預授增列之路徑。
- 過渡窗之「有界」必須有結構性前提，不能只靠重建通常很快。

## 考慮過的替代案

1. **入域寫端等待在途同步以關窗（BL-00134 選項一）**：只關得到入域寫端與同路由名重建那一半；過渡窗內讀舊面的是**所有並行請求**（判定進入點與選單、按鈕讀端皆不受域鎖約束），端點維寫端與 restorePolicy 亦不入域——窗對 API 授權照樣存在。另需一個跨交易可見的「同步在途」狀態供入域者等待＝新機制（違 FR-018）。user 於 Q6 否決。
2. **授予面空 diff 不觸發（與移除面統一以 diff 為門）**：diff 判定一旦漏算（撤銷集或新授集算錯、實際有寫卻判為空），判定面即與真相分歧且零告警；判定面重建冪等（自 DB 全量導出、同一資料態重建結果不變），空 diff 多重建一次無害、治理 QPS≈0 成本可忽略（前代 `rev5:ADR 0053` 款四同判準）。否決。
3. **修改 ADR-00043 本體（改寫決定 7 之表與決定 9 之字面）**：accepted body 不可變；其決定 7 末句已預授由本刀 ADR 增列。整顆 supersede 則需把決定 1～10 未變之九款重述一遍、只為增列三類中的兩類，不成比例。否決。
4. **同步耗盡時寫端改回錯誤（讓發起者看見耗盡）**：交易已 commit、授權真相已落地；回錯＝把「已落地的寫入」報成失敗，誘發重送（ADR-00043 決定 4 同判準：同步結果不影響寫端回應）。否決；耗盡由計數與告警承擔可見性。
5. **授予面收場沿用移除面之 `archived > 0` 門（直接套 `handler/role.rs` 之 `settle_domain_write`）**：授予面只有新授而無撤銷時實際歸檔為 0 ⇒ 新授權永不同步（新授端點恆回 `5003` 直到他事觸發或重啟）。否決。

對所選方案跑同一反例（RL-0013）：
- 「空 diff 仍觸發」會不會讓較早開始、較慢完成之重建以舊快照蓋掉較晚之 commit？`RELOAD_SERIAL` 包住重建＋換上＋重試全程（ADR-00043 決定 3），重建讀庫之時點在臨界區內 ⇒ 後進入臨界區者讀到的必是較新之 DB 態。成立。
- 「過渡窗有界」遇請求於 commit 之後、換上之前被丟棄（用戶端中斷或逾時）是否仍成立？若 commit 與同步在請求 future 內 await，一丟即同步中止、零告警零計數 ⇒ 窗延長至下次任一同步或重啟＝無界。故決定 4 要求收場取消安全；有此前提則成立。
- 「restorePolicy NoOp 不觸發」是否漏同步？NoOp 之交易只刪歸檔列、`casbin_rule` 零變化 ⇒ 判定面與真相無差可同步。成立。

## 決定

1. **觸發矩陣增列**（以 ADR-00043 決定 7 末句之預授為據；本 ADR MUST NOT supersede ADR-00043，現行觸發矩陣＝ADR-00043 決定 7 之表＋本款增列兩類）。三類觸發條件字面固定如下，判定面家檔 `auth/enforce.rs` 之 `reload_enforcer` doc、活書與 RUNBOOK 三類逐字沿用、不另造同義句；ADR-00063 決定一之島 G1 條文只載授予面與移除面兩類之觸發門字面（逐字沿本表），復原列由其通則句「授權變更寫端成功 commit 後 MUST 同步、被拒／無作用／標的不存在 MUST NOT 觸發」涵蓋、不另列：

   | 類 | 寫端 | 觸發條件 |
   |---|---|---|
   | 移除面（ADR-00043 決定 7，不變） | deleteMenu／batchDeleteMenu／updateMenu／deleteRole／batchDeleteRole | 成功且實際歸檔 ≥1 列 |
   | 授予面（本款增列） | updateRoleMenu／updateRoleButton／updateRoleEndpoints | Applied 即觸發、不問 diff（含空 diff） |
   | 復原（本款增列） | restorePolicy | Applied |

2. **授予面刻意例外與並陳**：授予面不以 diff 為門、移除面以實際歸檔為門——兩門方向相反為**刻意並陳**、MUST NOT 互相「統一」。判準：授予面之提交本身即宣告「此角色此維之全集如此」，重建冪等而成本可忽略，不問 diff 省去 diff 漏算一整類缺陷；移除面零歸檔＝判定面零變化，且新建零授權選單等零歸檔路徑屬常態，觸發純屬浪費（ADR-00043 決策驅動因子）。「授予面刻意例外」一語 MUST 明文於 ADR-00063 決定一之島 G1 條文與 `reload_enforcer` doc（FR-017）。
3. **不觸發集**（早退結構性保證）：四支寫端共通——操作者缺席（拒寫 `5000`；spec Edge Cases「授權寫端」段、ADR-00065 決定 3 前置）與任何未 commit 之失敗（含資料庫故障收斂之 `5000`；ADR-00065 決定 7）；授予面另有 Rejected（受保護撤銷拒 `biz.role.protectedRevoke`、封死拒 `biz.role.protectedGrant`）與查無角色（`biz.role.notFound`，含 body 缺席或壞形之收斂）；restorePolicy 另有 NoOp（身分鍵已在現役：只刪歸檔列、授權表零變化）與 NotRestorable（識別不存在或任一腿拒，`biz.policy.notRestorable`）；本刀新增之讀端六支（三維現況讀、候選讀兩支、回收桶讀）零觸發。ADR-00043 決定 7 之零觸發集不變。
4. **呼叫端紀律與收場形**：沿 ADR-00043 決定 6——同步 MUST 於交易 commit 之後、呼叫時 MUST NOT 持有判定面讀鎖；每請求至多一次；同一支 `reload_enforcer`、零新機制；同步結果不影響寫端回應（commit 成功即回成功）。授予面三支與 restorePolicy 之收場 MUST 沿 005 刀之取消安全形（`handler/role.rs` 之 `settle_domain_write` 形：commit 與其後同步整段交給脫離請求生命週期之 task、回應前 await 之；失敗腿顯式 rollback）；觸發門以 outcome 判（Applied），MUST NOT 套用移除面之 `archived > 0` 門。判定引擎版本錨（`rust-api/Cargo.toml` 之 casbin 釘版）本刀不升版（FR-018）；日後升版 MUST 依 ADR-00043 決定 5 重核其重載語意。
5. **同步呼叫點名冊**：`tests/authz_entrypoint_lint.rs` 之 `RELOAD_CALL_FILES` 加新建之 `handler/policy_archive.rs`（ADR-00065 決定 3；與 restorePolicy 之同步接線同一 commit；路徑字典序），三維授權寫端住已在冊之 `handler/role.rs`；`ENFORCER_WRITE_FILES` 維持空冊（家檔外生產面零判定面寫鎖取得；換上之唯一正道仍是 `reload_enforcer`）。
6. **已知降級窗恰兩類（兩窗）**（補述 ADR-00043 決定 9；記窗、不關窗——不為關窗改動既有同步機制）：
   - **①commit→換上之有界過渡窗**：自寫端交易 commit（選單序列化域鎖與標的列鎖於此刻一併釋放）至 `reload_enforcer` 以全新重建之判定面換上完成為止。長度＝一次重建（模型→轉接器→建構→載入）＋失敗重試之線性退避（上限 `RELOAD_MAX_ATTEMPTS`、基數 `RELOAD_RETRY_BACKOFF_MS`；ADR-00043 決定 4）＋`RELOAD_SERIAL` 排隊等候在途同步。窗內**其他並行請求**之判定與選單、按鈕讀端讀舊判定面；發起寫端之請求於同步結束後才收到回應（決定 4 之收場 await）。影響面：UI 可見性（選單維與按鈕維；005 刀既有之同路由名或同代碼重建短暫繼承舊授權）＋★**API 授權**（本刀起）：端點維撤銷於窗內被撤端點仍放行（**撤銷殘留**）；端點維授予與 restorePolicy 回灌於窗內新授端點仍回 `5003`（**授予面反向症狀**）。換上即止、自癒。有界之前提＝重建本身有界且收場取消安全（決定 4）。
   - **②重試耗盡窗**：ADR-00043 決定 9 之耗盡窗原款，觸發面擴及授予面與復原：耗盡仍失敗＝舊面續用——移除面之殘留繼承（同路由名重建之選單、同代碼重建之角色經殘留面繼承）＋授予面反向症狀持續（新授端點持續回 `5003`）＋撤銷殘留持續（新撤端點持續放行）；選單與按鈕顯隱於重新載入後仍為舊面；恢復＝下次任一成功同步或重啟 rust-api（RUNBOOK §13）。
   - 兩窗之前提同為單一 rust-api 行程（ADR-00043 決定 9）。與生效兩層時點（API 判定於換上後即時生效、選單與按鈕顯隱於下次載入頁面時更新；FR-019、ADR-00063 後果「生效語意兩層時點」）正交：後者是設計語意，兩窗是其降級偏離。
7. **「唯一已知降級窗」字面之取代**（逐處指名；取代為 ADR-00063 決定一／決定五之 G1／H2 落字——已知降級窗恰兩類、定義＝本 ADR 決定 6）：
   - 憲法 §I.7 島 H2 之「…重試耗盡期間記憶體授權判定面之殘留繼承為本條唯一已知降級窗…」句——由 ADR-00063 決定五之 H2 改寫（與島 G1 對應；「同步失敗保留上一份」方向句之落位＝其親決題 H-a、於本刀 U0 親決）承接。
   - ADR-00042「## 決定」之「### 三、新增島 H 段（置於島 F 之後、跨島註之前；逐字）」所引 H2 條文之同句。
   - ADR-00042 同節「對 rev5 v1.7.0 島 H 字面之差異附表」之「增補｜H2」列「同步失敗保留上一份、單一行程部署下耗盡窗為本條唯一已知降級窗」。
   - ADR-00043 決定 9 之括號「（＝島 H2 條文所載之唯一已知降級窗）」。
   兩支 accepted ADR 之 body 不動（GT-04），讀時併讀本 ADR 與 ADR-00063；現在式帳本面之同字面（BL-00134 條文）隨收刀刪列；史料面（`docs/reviews/`、`specs/`）之同字面不動。逐處枚舉以 `python3 tools/docsync errata 唯一已知降級窗` 現算、改完復掃（RL-0001）。
8. **觀測與告警照舊**：`casbin_reload_total{outcome=ok|retry|exhausted}` 值集封閉恰三、開機預註冊不變；告警規則 `obs016-casbin-reload-anomaly`（title `casbin-reload-anomaly`；`retry`／`exhausted` 之 5 分鐘增量 > 0）之 uid、title 與判準不變（其錨註解之指針隨動見後果「碼面連動」）；計數不帶觸發來源維度。`ok` 之增量來源自本刀起為三類（授予面空 diff 亦 +1）。
9. **RUNBOOK 同批**：§11.2 `ok` 判讀句改為三類觸發（字面同決定 1、指本 ADR 與 ADR-00043 決定 7），同句後半零增列舉「其餘寫端（新增、復原、角色停用、選單啟停等）」之泛稱「復原」改為「選單復原」（restorePolicy 之 Applied 自本刀起屬觸發者）；同句流程指針補島 G 情境一項不隨觸發列承載單元先補，改於治理單元新增活書 06 §6.1「授權治理——島 G」之同顆補入（免懸空指針）；§13「回應 403」分診補一項排障錨「剛授予或剛復原之端點仍回 `5003`」，依觀察時點分流：①觀察早於發起寫端收到回應（其他並行請求）＝過渡窗（決定 6①），稍後重送即通；②發起寫端已回成功後仍 `5003`＝不是過渡窗（決定 4：回應於同步結束後才送出），依序查——標的角色是否停用（停用不擋授權寫入、停用即斷權由授權讀端每請求濾角色狀態＝ADR-00065 決定 3 第⑤腿；復原形＝ADR-00068 款 16，三維授予同理）→（限授予）寫端回應之生效集合是否含該（路徑,方法）（不含＝所送之鍵不屬 getAllEndpoints 候選、已被 orphan skip 靜默略過＝ADR-00066 決定 2）→ 該鍵是否其後被撤（授權回收桶出現該角色該（路徑,方法）晚於該次寫端之 `endpoint_revoke` 歸檔列＝後送出之全量替換整份覆蓋＝ADR-00068 款 11；角色刪除受 in-use 守門所擋、持該角色者在場時不可達）→ §11.2 `exhausted` 增量（耗盡窗＝決定 6②）、處置沿「判定面同步耗盡」段；該段補授予面反向症狀（新授端點持續 `5003`）與撤銷殘留（新撤端點持續放行）兩項並列。授予面與復原之收場若另立取消告警字面，§13 之 log 引文同批補列。
10. **BL-00134 處置**：以記窗收（其觸發欄選項二：於 Amendment 在 H2 改字記過渡窗＝ADR-00063 決定五承接字面、本 ADR 承接定義）；選項一（入域寫端等待在途同步以關窗）依替代案 1 否決。收刀 `backlog_done` 刪列。

## 後果

- 現行觸發者＝移除面五支＋授予面三支＋restorePolicy；ADR-00043 body 與 title 不動（DECISIONS-INDEX 沿用其 accepted title），讀時併讀本 ADR——觸發矩陣＝ADR-00043 決定 7＋本 ADR 決定 1、殘窗＝本 ADR 決定 6。
- 碼面連動（承載單元同批；RL-0011）：
  - `reload_enforcer` doc 之「觸發矩陣（ADR-00043 決定 7；恰五支…）」表改三類並明文授予面刻意例外，其 rev5 出處句「前代授權寫端與授權回收桶兩類觸發屬授權治理刀、不帶」改現在式。
  - 「移除面寫端 commit 後以全新重建後一步換上同步」形之同語意現在式句改寫為三類觸發、改指 ADR-00043＋本 ADR 決定 1：`auth/enforce.rs` 檔頭與 `init_enforcer` doc、`main.rs` 連線段註解、`state.rs` 判定面欄 doc——即 ADR-00043 決定 1 所定改寫字面之承載面，該字面隨本 ADR 決定 1 擴為三類（ADR-00043 body 不動）；另 `auth/enforce.rs` 交錯時序測試 doc 之「判定面同步只由移除面寫端觸發」括號句同改。
  - `tests/authz_entrypoint_lint.rs` 之 `RELOAD_CALL_FILES` doc：「擴列＝接線一支 ADR-00043 決定 7 觸發矩陣內的寫端」句改指 ADR-00043 決定 7＋本 ADR 決定 1；「觸發門（實際歸檔 ≥1 列）屬呼叫點行為」句之觸發門改為三類（字面同決定 1）。
  - `handler/role.rs` 生產區同步觸發點「恰一處＋匯入句」之源碼釘測隨授予面收場件同單元改寫；名冊植入自證案之期望紅集字面依新檔入掃描面後之實況改。
  - `deploy/grafana-provisioning/alerting/rules.yml` 之 casbin-reload-anomaly 段錨註解（現為「（島 H2；判定面同步＝ADR-00043）」形）：判定面同步之指針補引本 ADR（ADR-00043＋本 ADR）；島指針依 ADR-00063 親決題 H-a 之結果——取①（同步失敗契約與兩窗之本體移至島 G1）改指島 G1（H2 互引）、取②補列島 G1、取③維持島 H2。錨字面（uid、title、summary）與判準不改。此註解屬 ADR-00063 決定六親決題 P-a 所列「不入本顆者」（本顆＝Amendment 顆），歸本 ADR 觸發列增列之承載單元順改。
  - `handler/menu.rs` 與 `handler/role.rs` 移除面取消安全測試 doc 之「ADR-00043 決定 6／9、憲法島 H2」指針：施工時依同一判準判讀（講降級窗或同步失敗方向者依 H-a 結果改指、講同鍵重建零繼承者維持 H2）。
  - 上列為起草期已知命中、非封閉清單：下條活書段之種子另加「移除面寫端 commit 時」「實際歸檔 ≥1 列」「決定 7 觸發矩陣」「島 H2」（後者只改指稱同步失敗契約或已知降級窗之指針、指稱同鍵重建零繼承或歸檔不可回灌者維持；判準同 ADR-00063 決定六），一律以 `python3 tools/docsync errata <詞>` 掃全 repo（含兩子庫 pin 樹）現算處數，活書與碼面同批現在式化、改完復掃（RL-0001）。
- 活書同批改現在式（RL-0011 種子「移除面寫端 commit 後」「只由移除面寫端觸發」「恰五支」「零歸檔之寫端不觸發同步」與「唯一已知降級窗」）：04「技術選擇」之判定面同步句、05 `reload_enforcer` 呼叫端、06 島 H 情境⑤（改寫）、08 授權慣例、10 §10.2 島 H 情境表回應欄之「零歸檔之寫端不觸發同步」（泛稱「寫端」自本刀起含授予面零歸檔亦觸發者＝成假述；改限移除面或改寫為三類）、11 多行程殘留風險列、12「判定面同步（vs IP 規則熱重載）」條；講移除面類別本身之句保留。另 06 §6.1 與 10 §10.2 新增之島 G 情境（治理單元新增、ADR-00063 後果；現無此則）：觸發三類字面同決定 1、兩窗與其症狀詞（撤銷殘留、授予面反向症狀）同決定 6。
- 機器守（SC-006）：觸發矩陣特性鎖定測——授予面三支 Applied 觸發（含空 diff）、Rejected 不觸發、restorePolicy Applied 觸發、NoOp／NotRestorable 不觸發，計數增量以區域 recorder 斷言；授予面與復原之收場取消安全案；授予成功後以單一判定進入點雙斷言即時生效、撤銷成功後即時失效；失敗注入下舊面續放行 R_SUPER（沿 ADR-00043 決定 10）。
- 維運面：授予面空 diff 亦觸發 ⇒ DB 修復後，任一授權彈窗原樣提交即觸發一次同步（另一條不必重啟之恢復途徑）；耗盡窗之恢復判準仍以 §11.2 `ok` 增量或重啟為準、不以告警解除為準。
- 成本：每次授予面 Applied（含空 diff）與復原 Applied 各全量重建一次判定面（治理 QPS≈0、可忽略）。
- CDP：兩窗屬文件面、UI 零差（spec 刻意分岔登記表「已知降級窗之條文」列）；單一操作者之走查一般觀察不到過渡窗（發起者收到回應時同步已結束）。

## 翻案觸發器

- 判定面改為多進程或多副本部署（含水平擴展、藍綠並行；ADR-00043 決定 9 前提破）⇒ 兩窗之定義與「有界」皆失效，須補跨行程同步通知並重寫決定 6。
- 過渡窗內實際觀察到越權（已撤端點於窗內被放行並造成事件）或誤拒被回報（新授端點於窗內回 `5003` 被當缺陷）⇒ 評估關窗（重審替代案 1 或另案）。
- 告警 `casbin-reload-anomaly` 於非故障注入情境實際觸發（`retry`／`exhausted` 增量 > 0）⇒ 複核耗盡窗處置、重試常數與 RUNBOOK §13。
- 判定面全量重建耗時上升使過渡窗不再可忽略（例如政策列數量級上升）⇒ 與 ADR-00043 之增量同步評估同審。
- 後續刀新增任何改動 `casbin_rule` 之寫端 ⇒ 以該刀 ADR 依本 ADR 之形增列觸發列、同 commit 擴 `RELOAD_CALL_FILES`；若其觸發門不屬決定 1 三類字面之一，複核決定 2 之並陳判準。
