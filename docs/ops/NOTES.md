<!-- wave: 6 -->
# NOTES — 當前意圖／下一步

## 現況（文件創世收官、波 6 起＝刀）

現況帳＝`docs/generated/STATE.md`；史＝`docs/generated/MILESTONES.md`（真源 `docs/ops/events.jsonl`）；進度面＝`docs/generated/RAD-AI-MAP.md`；閘與 Day-1 豁免＝`docs/generated/GATES.md`；最近一次獨立 review 輪＝`000-r2-doc-governance`（報告 `docs/reviews/20260907-doc-governance.md`；前輪 `000-r1` 報告 `docs/reviews/20260904-doc-governance.md`）；by-design 已知態指針總表＝`docs/arc42/11-risks-and-technical-debt.md` 技術債表。

## 下一步

- **進行中＝008 audit-settings-pages**（分支 `008-audit-settings-pages`）：SDD 五步已完、U0 兩顆已落（Amendment 顆 `8ceadb5`＝憲法 1.9.0；ADR-00099～ADR-00102、ADR-00104、ADR-00105、ADR-00107、ADR-00108 accepted；ADR-00103／ADR-00106 留 proposed 至 U18）；U1 工具前置已落（`tools/schema-gate.py offline` 離線對賬腿＋pre-commit `schema-offline` 段、runtime-append 兩工具擴 `sys_access_log`）；U2 測試基建已落（存取日誌在途計數件、`AccessLogRowsGuard`／`PurgeSelfAuditGuard`、逐回應 drain 與帶守衛之 app 建構件、清理類前置斷言件，兩層鏡像）；U3 骨架已落（ROUTES 61→66、`handler/audit.rs` 空殼五支、contract 登記與稽核域授權態矩陣、可授出集 35）；U4 m0004 與演進帳已落（m0004＝reaper role＋GRANT 六條、選單 77 按鈕清單一碼 `audit:purge`、R_SUPER 授權列 165，dev 庫已套用；演進帳 E-010／E-011；seed 錨定測試改對、reaper 角色身分權限正負向三案）；U5 四源讀端 facade 與讀端件已落（`model/audit_query.rs` 時間區間／人員過濾／個資打碼三件、`sys_user` 名對應件含已軟刪同名全集、四源 `list` 與新建 `facade/sys_access_log.rs`）；U6 讀端 handler 四支已接真（唯讀交易、伺服端固定序、寬鬆 query、逐欄白名單 DTO 與打碼單點、第二發批查名；base-web `rev6-audit.d.ts` 讀端八型入 wire 受審名冊、快照重抽；contract 四 case 收緊）；U7 retention 共用核與手動清理寫端已落（`model/retention.rs` 共用核〔下限 30、標的四表、同交易刪除與自記〕、四源水平線刪除與計數件、`purgeAuditLog` 接真〔固定序①白名單②下限③操作者上下文〕、錯誤明細第三鍵 `biz.audit.purgeBelowFloor`〔`{minDays}`；msg-key-gate 明細型之家逐鍵對映〕、base-web 清理 wire 四型與 `translateBackendMsg` 第三分支）；**下一步＝U8 存取日誌寫入中介層**。
- 接手機器（含 WSL）：外層取 `rev6-admin-root` → `bash tools/bootstrap.sh` 綠才可 commit（CLAUDE.md §3／§6）→ pins 以 `docs/generated/STATE.md` 為準（SessionStart 健檢應零分歧）→ 新刀起手依 CLAUDE.md §2 以 `/speckit-specify` 建分支。
- migration 檔名四碼（ADR-00008）、delta 自 `m0003` 起編（ADR-00010 決定 1）；每支帶 migration 的刀收刀前必跑 Day-1 登記紀律三步（RUNBOOK §10）；帶結構演進（DDL）之 delta migration 須同刀先擴 `tools/schema-gate.py offline`，未擴即被 pre-commit `schema-offline` 段擋（RUNBOOK §10）。rev5 藍本去處見 `docs/generated/reference/rev5-blueprint-map.md`、島進場規則見憲法 §I.7；檢索性第四指標（ADR-00021）自 000-r1 回填值起由 STATE 現讀、每次獨立輪收單隨 review 事件 `probe` 欄更新。

## 未決

- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
- base-web 型別檔無常設檢查：`pnpm typecheck` 帶 `--skipLibCheck`、不檢任何 `.d.ts`（含 `src/typings/**`），pre-commit 亦不跑前端型別檢查；008 刀內由主線於動到型別檔之單元收尾加跑完整 vue-tsc（node_modules 以外 0 錯）並記入收單訊息，收刀後由 user 決定是否開維護批做成常設檢查。
