---
id: "LL-00050"
rule_id: "RL-0061"
promotion_surface: code
---
LL-00050｜宿主背景任務開始套用預設時限後，看門狗長尾腿沒給 `timeout`、約 28.5 分鐘被停；CLAUDE.md 寫的 `--bg --rearm` 補回形又被工具以互斥拒收——run 逾 30 分鐘即失去長尾覆蓋（maint-backlog-128-129-130；2026-09-30）

**徵狀**：2026-09-30 session 重啟後（宿主 Claude Code 2.1.285），spec-compliance-005 的兩支 review run 與 maint-backlog-128-129-130 U1 的 TDD run，`--bg` 長尾腿都在發射後約 28.5 分鐘被停止（transcript 時戳），前後三次；停止通知明載 `killed` 與「stopped after reaching its background time limit」。此前未給 timeout 的長尾腿都能全程覆蓋，前一輪的長尾腿跑了 98 分鐘才正常印 DONE。主線當時已認出是宿主的背景時限、也記下「重啟後行為不同」，補救卻停在改掛帶 runId 的 Monitor `--rearm`、每 30 分鐘續一次，沒有追到「發射時可明給 `timeout`」這一層，直到 user 指出。CLAUDE.md §2 對長尾腿重發寫的是「帶 `--bg --rearm`」，工具卻把兩旗標定為互斥、回 rc 2；改發不帶 `--rearm` 的 `--bg`，在已逾上限的扇出 run 上首輪就會告 RUNAWAY 並退出，覆蓋同樣歸零。

**成因**：①宿主行為在 session 重啟後改變：背景任務不給 `timeout` 即套預設 1800000（30 分鐘），到點停止並通知主線；Bash 工具說明所載背景上限為 7200000（2 小時）。雙掛形（maint-backlog-79）設計時背景任務沒有時限，程序只寫明 Monitor 的 `timeout_ms`（Monitor 預設只有 5 分鐘），沒寫 Bash 腿的 `timeout`。宿主一變，「長尾腿覆蓋全程」的前提就失效，而程序裡沒有任何一處會因此轉紅。②程序句「帶 `--bg --rearm` 重發長尾腿」與工具的 `--bg`／`--rearm` 互斥，是同一顆收單 commit（c74179b）寫進來的：互斥為保護背景腿唯一的冒煙紀錄（ARMED 行）而加，寫程序句時沒有回頭對工具實跑這個組合。兩者從此矛盾，直到真的需要重發才暴露。

**處置**：CLAUDE.md §2 與 PostToolUse 提醒寫明：長尾腿必給 `timeout: 7200000`，明給也只撐 2 小時；補回一律 `<冒煙token> <runId> --bg --rearm`，限同一 run、且 run 仍在飛；新 launch（被擋重發、resume）一律首掛形。停止通知附的「已用最長 timeout 勿重啟」不適用監看腿，照補並向 user 報停止。`tools/wf-watchdog.py` 解除互斥，`--rearm` 仍必帶 runId、不重做冒煙；`--bg --rearm` 印一行 REARMED 紀錄。重掛當下已逾有效上限＝預先承認：此後不告 RUNAWAY，背景腿也不因此退出；未逾照常武裝，首掛永不預先承認。重掛當下 run 已結束＝印 DONE 即退。背景形 RUNAWAY 告警當下即印出補回形。自測 38→44 案，判準變異 29 支皆在 0.3 秒內轉紅，含對抗式審查找出的逃逸形。

**晉升面**：code——工具行為、PostToolUse 提醒字與 CLAUDE.md §2 程序句；RL-0061 條文不變（未寫任何與新行為衝突的字面）。

**再犯面與守法**：監看器的「覆蓋全程」前提依賴宿主對背景任務的行為，而宿主可能在 session 重啟或升版時無預警改變。停止通知一出現新形態（例：`killed`、time limit），當場回頭驗前提、把參數明給，不要只繞過症狀。程序句寫進某個工具旗標組合的那一顆 commit，同批對工具實跑該組合；對工具旗標加限制（互斥、拒收）時，同批以 `python3 tools/docsync errata` 掃程序文件裡被禁掉的寫法。
