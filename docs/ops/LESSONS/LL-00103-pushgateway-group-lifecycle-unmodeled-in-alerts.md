---
id: "LL-00103"
rule_id: "RL-0013"
promotion_surface: none
---
LL-00103｜告警與儀表板之狀態宣稱未對 pushgateway 組生命週期建模（留存至 DELETE、PUT 整組替換）：寫出「未起 jobs＝零序列」假述，並把對賬心跳逾時告警綁在對該 job 無語意之 `mode="execute"` 上（008 刀 U13）

**徵狀**：
1. 008 刀 tasks 期 T114／T118 寫「未起 jobs profile＝零序列＝noDataState=OK 恆綠」「未起 jobs profile＝No data 屬預期」。U13 碼品質審查實證反例：compose 之 pushgateway 帶 `--persistence.file` 與具名卷、prometheus 對 pushgateway 設 `honor_labels: true`，各組留存至對該組 DELETE 為止；jobs 曾跑而後停跑時序列仍在、時戳凍結，逾 172800 即紅。
2. T115 定⑦b 之式為 `time() - reaper_last_success_timestamp{mode="execute", reaper_job="policy-reconcile"} > 172800`（「形照⑤／⑥全結構」），同條並寫「對賬不設 mode-misconfig 規則：`--execute` 只決定心跳 `mode` 標籤、行為恆唯讀」。U13 派發後 side agent 指出：排程漏帶 `--execute` 時心跳標 dry-run，⑦b 恆 noData 綠、停跑不響。主線復核另得第二條遮蔽路：⑦b 已 firing 時手跑一次 dry-run 對賬，PUT 整組替換抹掉 execute 序列，⑦b 轉 noData 綠。⑤（token-reap）有⑤b 兜底，⑦b 沒有。

**成因**：
1. 寫告警狀態句與 matcher 時只想到「序列有或無」，沒有把 pushgateway 組之兩條規則——留存至 DELETE、PUT 整組替換——代入停跑、漏旗標、手跑三種情境推演。`rev4:017` brainstorm 已記「持久組 execute 時戳凍結→48 小時後⑤誤紅」，tasks 起草時沒有帶過來。
2. 抄⑤／⑥形時把 `mode="execute"` 當結構照抄；它在⑤／⑥有語意（dry-run 不刪列），在對賬 job 沒有。棄⑦c 之論證「`--execute` 對此 job 無行為語意」沒有回頭對所選的⑦b 跑同一反例（RL-0013）。

**處置**：
- 第 1 形：fix 輪於允許面改述 rules.yml ⑤⑥⑦⑦b 段註與兩支儀表板描述（「pushgateway 無該組＝零序列」、持久卷留組＝停跑偵測本意、清組＝DELETE）；主線收尾追認讀法，tasks T114／T118 字面同改。
- 第 2 形：主線裁定⑦b 去 `mode` matcher；rules.yml 段註與 summary、reaper.json id 1 與 master-overview.json id 5 之描述、research R14.2、contracts reaper-cli §8、tasks T115／T118 同顆改述。T120 活體加一腿：只推 dry-run 舊時戳，⑦b 轉 firing、⑦ 不動，同時點舊式之 PromQL 零序列。

**晉升面**：none。判準同 RL-0013；守法在 tasks 起草與觀測層設計審查。

**再犯面與守法**：
- 寫 pushgateway 來源之告警或描述，逐一推演「從未推過、正常輪替、停跑、漏旗標、手跑另一模式、DELETE 清組」六種狀態下序列之有無與值，再下狀態句。
- 抄同族告警形時，逐個 matcher 問「在這個 job 下有沒有語意」；只認某模式之存活告警必配「模式設錯」兜底，否則改為不分模式。
