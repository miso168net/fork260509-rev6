---
id: "LL-00101"
rule_id: "RL-0067"
promotion_surface: none
recurrence_of: "LL-00081"
---
LL-00101｜子庫新檔於 commit 前以 `git -C <子庫> grep` 取 DoD 計數與零命中恆空掃：未追蹤檔不在掃描面，計數恆 0、零命中類否定證據結構性成立（008 刀 U10）

**徵狀**：008 刀 U10 之 T091／T093 DoD 以 `git -C rust-api grep` 對兩支新檔（`server/src/reaper.rs`、`server/src/bin/reaper.rs`）取計數（如 `Duration::from_secs(HEARTBEAT_TIMEOUT_SECS)`＝1、`grace_days_from_lookup(`＝1）與零命中（`config::|entity::`、`install_recorder|config::|entity::`、逐段時限）。兩檔在子庫 commit 前皆未追蹤，`git grep` 不帶 `--untracked` 只掃已追蹤檔：計數項恆 0，零命中項恆成立——植入違規也照樣零命中。implementer 與規格對照、碼品質審查各自發現，改以 `git grep --untracked` 或一般 grep 實核；本單元之 DoD 實得皆以改形取得。

**成因**：
1. `git grep` 之掃描面預設為已追蹤檔；子庫新檔要到子庫 commit 後才進掃描面，而 agent 不得 `git add`。
2. tasks 起草時，DoD 命令沒有區分「單元內 agent 跑」與「子庫 commit 後主線跑」兩個時點，寫成同一字面。LL-00081 之守法只落在 fork-delta-lint 一支工具，沒有擴及以 git 為掃描面之一般 DoD 命令——同根（git 掃描面看不到未追蹤新檔）之第二形。

**處置**：U10 收尾於 rust-api commit 後、外層 commit 前，照 tasks 字面（不帶 `--untracked`）重跑 T091／T093 之 DoD grep，實得入外層收單 commit 訊息。

**晉升面**：none。判準同 RL-0067（證據須打在掃描面確實看得到的實例上）；守法落在單元定義、tasks 起草與主線收尾程序。同根再出第三形時，改評估機制面（RULES 擴寫或閘），不再只補 LESSONS。

**再犯面與守法**：
- 含子庫新檔之單元，單元定義烤句：新檔於子庫 commit 前，凡以 `git -C <子庫> grep` 取之計數與零命中一律加 `--untracked`（或以一般 grep 指定檔路徑）；不帶者之結果不作新檔之證據。
- tasks 起草：涉新檔之 DoD grep 直接寫 `--untracked` 形，或明註「子庫 commit 後由主線跑」。
- 主線收尾：子庫 commit 之後、外層 commit 之前，照 tasks 字面重跑涉新檔之 DoD grep。
