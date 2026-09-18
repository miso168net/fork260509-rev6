---
id: "LL-00024"
rule_id: "RL-0016"
promotion_surface: code
---
LL-00024｜看門狗冒煙只讀 transcript 首行；harness 在 prompt 行之前多放一行框架行後，ARMED 恆報「token 命中=0」

**徵狀**：004 刀 U1 續跑形 run 一發射，看門狗 ARMED 行回報「impl首行829bytes／token 命中=0」；依 RL-0016 這個訊號的意思是「鎖錯標的或 prompt 沒送到」。人工讀 transcript 才確認是誤報：第 1 行是 harness 的「user request 轉述」框架行（829 bytes、不含 token），真正的 prompt 在第 2 行（含 token、`zh-TW`、規則塊版本串）。同一 session 三天前的另一支 run 首行即 prompt、命中=1——差別在該次 launch 當回合有無可轉述的 user 訊息，框架行時有時無。

**成因**：`tools/wf-watchdog.py` 的冒煙判準寫死「最早 agent transcript 的**第一行**」，把 harness 的 transcript 佈局當成穩定介面；佈局一變，判準不是報錯而是安靜地回報一個看起來像真故障的值。此外 Monitor 工具單次上限 30 分鐘，長 run 每次重掛都重印一次 ARMED 行＝同一則誤報每 30 分鐘重播一次，稀釋了真告警。

**處置**：冒煙改掃前 `SMOKE_SCAN_LINES`（5）行、取第一個含 token 的行並回報其行號與 byte 數；掃描窗設上限＝token 只出現在第 6 行之後者仍報命中=0（那是 agent 自己輸出的複述、不算 prompt 送達；有反例測試釘住）。同批：重掛專用旗標 `--rearm`（不印 ARMED、必帶目標）；run 結束（持久 json 於迴圈起點之後落地或 mtime 前進）自動印 DONE 退出——次序排在 RUNAWAY 補判之後、STALL 之前，鎖到早已完成的 run 不觸發。

**再犯面與守法**：凡判準建立在「別人的輸出檔第 N 行／第 N 欄」之上，先問該佈局是不是對方承諾的介面；不是就掃一個有上限的窗、以內容（token）定位而非以位置定位，且窗外必有反例測試。ARMED 命中=0 時的處置序不變（RL-0016）：先讀 transcript 前幾行人工確認、再判鎖錯標的，不得因「上次是誤報」就略過。
