---
id: "LL-00050"
rule_id: "RL-0061"
promotion_surface: code
---
LL-00050｜看門狗長尾腿的 Bash 背景呼叫沒給 `timeout`，吃背景預設 30 分鐘時限被停；CLAUDE.md 寫的 `--bg --rearm` 重發形又被工具以互斥拒收——長尾覆蓋從未撐過 30 分鐘（maint-backlog-128-129-130；2026-09-30）

**徵狀**：spec-compliance-005 的兩支 review run 與 maint-backlog-128-129-130 U1 的 TDD run，`--bg` 長尾腿都在 29～35 分鐘時被停止（不是 RUNAWAY、也不是 STALL 出口），前後三次。主線的補救是改掛帶 runId 的 Monitor `--rearm`、每 30 分鐘續一次；005 輪報告把停止歸因於「執行環境的背景時限」，沒有再往下追，直到 user 指出背景時限可明給到 2 小時。CLAUDE.md §2 對長尾腿重發寫的是「帶 `--bg --rearm`」，但工具自 maint-backlog-79 起把兩旗標定為互斥、回 rc 2；改發不帶 `--rearm` 的 `--bg`，在已逾上限的扇出 run 上首輪就會告 RUNAWAY 並退出，覆蓋同樣歸零。

**成因**：①Bash 工具的背景任務另有自己的時限：不給 `timeout`＝預設 1800000（30 分鐘），到點即停止並通知主線；本 workspace 環境可明給至 7200000（2 小時）。雙掛形（maint-backlog-79）只把 Monitor 的 `timeout_ms` 寫明（Monitor 預設只有 5 分鐘），沒寫 Bash 腿的 `timeout`，「長尾腿覆蓋全程」這個前提在超過 30 分鐘的 run 上從未成立。停止通知的外觀與正常退出相近，前幾次都沒被當成缺陷。②同批 review 為保護背景腿唯一的冒煙紀錄（ARMED 行）加了 `--bg`／`--rearm` 互斥，卻沒有回頭掃程序文件裡這個組合的寫法；文件與工具從此矛盾，直到真的需要重發才暴露。

**處置**：CLAUDE.md §2 與 PostToolUse 提醒明寫長尾腿必給 `timeout: 7200000`，重發形一律 `<冒煙token> <runId> --bg --rearm`（同給 timeout）。`tools/wf-watchdog.py` 解除互斥：`--rearm` 仍必帶 runId、不重做冒煙；`--bg --rearm` 印一行 REARMED 進輸出檔，記錄重掛當下的 key 數、有效上限與判定。重掛當下不重複 agent key 已逾有效上限，視為主線已判扇出型而預先承認：此後不再告 RUNAWAY，背景腿也不因此退出；未逾則照常武裝。首掛永不預先承認。背景形 RUNAWAY 告警當下即印出帶本 run runId 的重發形。自測新增三案、改寫三案（38→41 案），判準變異 12 支皆在秒內轉紅（其中「重掛不必帶目標」一支原本會讓整支自測掛到逾時，改把參數錯誤類呼叫放進樁內）。

**晉升面**：code——工具行為、PostToolUse 提醒字與 CLAUDE.md §2 程序句；RL-0061 條文不變（未寫任何與新行為衝突的字面）。

**再犯面與守法**：交給背景任務「覆蓋全程」的監看器，先查宿主對背景任務的時限並在呼叫時明給；被宿主停止不會以錯誤出現，只會像一次普通的退出通知。對工具旗標加限制（互斥、拒收）的那一顆 commit，同批以 `python3 tools/docsync errata` 掃程序文件裡被禁掉的寫法，逐處改掉。
