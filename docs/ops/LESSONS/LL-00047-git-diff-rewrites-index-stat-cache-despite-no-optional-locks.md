---
id: "LL-00047"
rule_id: "none：閘取值命令的唯讀寫法，判準住兩個取值點的碼註與 pre-commit 檔頭「各閘唯讀」即可承"
promotion_surface: code
---
LL-00047｜GT-04 在 lint 路徑用 `git diff --name-only HEAD` 取捷徑，會回寫 index 的 stat 快取，`--no-optional-locks` 也擋不住（maint-backlog-28-35-36-39-74-101-102-120 U1 實測、U2 修；2026-09-29）

**徵狀**：`tools/docsync/adr.py` 的 `_files(head=True)` 以 `git diff --name-only HEAD -- <ADR 目錄>` 略過未改檔的 HEAD 讀取。每趟 lint 跑完，`.git/index` 的位元都可能變（stat 髒而內容不變之檔被刷新寫回）；在 hook 期，寫的是本次 commit 的暫存區檔（`GIT_INDEX_FILE`；`commit -a`／部分 commit 時為外層 lock index），違反 pre-commit 並行 harness 的「各閘唯讀」。

**成因**：`git diff`（有工作樹一側）遇 stat 資訊不符而內容相同的檔，會在結尾「順手」刷新 index 並回寫——這一步不看 optional locks 設定，所以加 `--no-optional-locks` 仍照寫（git 2.43 實測）。drvfs 上 stat 常不準，這種檔很常見。

**處置**：兩個取值點都改用 `git --no-optional-locks status --porcelain -z …`：status 只在記憶體刷新、不回寫，列出的「HEAD≠暫存區」與「暫存區≠工作樹」聯集是「工作樹≠HEAD」的超集，比對面不減。GT-12 的「工作樹＝暫存區」一致性腿同理選 status。GT-04 另有一案把 ADR 弄成 stat 髒而內容不變，斷言 `_files(head=True)` 前後 `.git/index` 位元相同。plumbing `diff-index` 不回寫，但把 stat 髒檔全部當已改：在 drvfs 複本上把 55 支 ADR 全弄成 stat 髒時全數列出、退回逐檔讀 HEAD 版約 4.8 秒（status 同條件 0.3 秒），所以不用。

**晉升面**：code——唯讀寫法住兩個取值點的碼註，由該案機器守；不另立規則。

**再犯面與守法**：閘或 lint 路徑新增 git 取值時，先在臨時 repo 把目標檔弄成 stat 髒而內容不變，比對命令前後 `.git/index` 的位元。會變的命令（`git diff` 工作樹側、不帶 `--no-optional-locks` 的 `git status`）不得進閘；要判「工作樹與 HEAD／暫存區是否不同」，一律用 `git --no-optional-locks status`。
