---
id: "LL-00051"
rule_id: "RL-0017"
promotion_surface: code
---
LL-00051｜BASH_MAX_TIMEOUT_MS 放寬後子 agent 前景命令可逾 600 秒，看門狗 STALL 780 秒的推導前提失效——implementer 以一小時等待迴圈等背景 cargo 變異串，兩腿同時誤報 STALL 退出（maint-backlog-128-129-130 U2；2026-09-30）

**徵狀**：U2 當機後重發，implementer 把七支「改前缺口」變異測試串丟到背景跑（每支全量 cargo 約 4.5 分鐘），自己以 `until grep -q "chain done" …; do sleep 10; done` 前景等待，Bash timeout 給 3600000。14 分鐘沒有 transcript 寫入，Monitor 腿與長尾腿同時以 STALL（794s）告警退出。實查容器內 cargo test 以 72% CPU 在跑，run 完全健在。

**成因**：STALL＝780 秒的推導前提是「子 agent 的 Bash 單條命令上限 600 秒，再加餘裕」，而子 agent 的 transcript 在工具回傳之前不會寫入，所以長命令期間必然靜默。同日 user 為了讓看門狗長尾腿能在背景撐 2 小時而設的 `BASH_MAX_TIMEOUT_MS`，連帶放寬了子 agent 前景命令的上限；前提就此失效，判準卻沒跟上。常數註解寫明了推導前提，但前提所依賴的設定變動時，沒有任何一處提醒要回頭重驗門檻。

**處置**：當次不 TaskStop。改掛一支背景命令，等該 run 下一筆寫入後以 `--bg --rearm` 補回長尾腿。user 裁定本批內修 `tools/wf-watchdog.py`：STALL 前加合法靜默判定（legit_silence）——自 journal 取未完成 agent（有 started、無 result），自各自 transcript 取未回的工具呼叫；截止＝開始時戳＋自報 timeout（Bash 未帶時取預設 120000）。所有未完成 agent 都在「截止＋60 秒」之內時不告 STALL。以下一律照 STALL 判，寧誤報不漏報：非 Bash 且無 timeout、背景呼叫、時戳壞形、journal 或 transcript 讀不懂、未完成集為空（agent 皆已回、run 卻未收）。自測 44→53 案，判準變異 14 支皆 0.2 秒內轉紅；對在飛 run 實測判為合法等待，對當機 run 判為不合法。

**晉升面**：code——工具判準；RL-0017 條文不變（stall 閾值語意仍指 agent 寫入間隔之上限，合法等待之例外住工具 docstring）。

**再犯面與守法**：凡門檻常數的註解寫著「由某上限推出」，那個上限所依賴的設定（env、宿主版本、工具預設）一變，當場回頭重驗門檻。「靜默＝卡死」類判準要認得被監看者自報的合法等待，不能只數沉默秒數。代價要明講：合法等待期間若 agent 行程本身已死，STALL 最多遲到該呼叫的 timeout 加 60 秒。
