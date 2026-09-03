<!-- wave: 5 -->
# NOTES — 當前意圖／下一步

## 現況（波 4 出口已過、波 5 起手）

波 4 在分支 `000-w4-rad-ai-tradeoffs` 落地（計畫 `docs/brainstorms/000-w4-rad-ai-tradeoffs.md`；merge 與收單事件見 `docs/ops/events.jsonl`）：ADR-00007 accepted（RAD-AI 23 筆取捨＋F24 量表第四值「不適用」；射程＝系統層形制、流程層以「類比張力：」宣告偏離、D15 在活書正文零例外）；附錄 A 對 as-built 對賬零未決（證據段住該 ADR）；活書四處（P-E1 指向 C4-E3、C4-E1 必填性質指針與導言中文化、§9.1 對映表改欄序）；BACKLOG BL-00002（GT-10 對 §9 兩腿在首個 AI-ADR 後互斥、觸發＝首個 AI-ADR 開寫前）。
Day-1 豁免餘兩筆（GT-03.no-close-events、GT-08.lessons-absent），首刀收刀與首條 LL 時解除。活書家族 `TODO(波 k)` 殘留 0；進度面＝`docs/generated/RAD-AI-MAP.md`（流程層八列全 N/N、系統層十二列「目前無」）。

## 下一步

- 波 5（本波）：文件創世驗收——addressability 自評（啟動書 §7 形、量表 0／1／2＋「不適用」附理由）、三指標首值或 n/a（`docs/generated/STATE.md`）、DoD A 六條逐條（啟動書 §0.3 A）、tmp-clean（含 `tmp/rev5-handoff/`）。出口＝DoD A 打勾、波標記 bump 6。
- 首刀（應用碼）：刀序由首刀 brainstorm 決定（D13）；rev5 藍本去處見 blueprint-map、島進場規則見憲法 §I.7；首個 AI-ADR 前先消化 BL-00002。

## 未決

- rev6 GitHub remote：掃描防線就位後再建（啟動書附錄 D；ADR-00002 後果段）。
- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
