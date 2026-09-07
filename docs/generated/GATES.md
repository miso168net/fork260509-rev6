<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# GATES — 閘名冊（§4.1）

閘數 12／上限 12（一進一出；超限只警告不擋＝ADR-00011）。真源兩層：存在＝原始碼 finding 錨形、語意＝docstring GATE 區塊（GT-12 斷言錨形 ⊆ 區塊、三處名冊同源）。Day-1 豁免 0 筆（§4.6；到期即紅）、環境型具名跳過 3 筆（ADR-00019；rc 0、不到期）。

| 閘 | 守哪條 RULES／ADR | 監測哪一面的漂移 | 真源 | 掃描面 | 觸發時機 | 紅時 rc | Day-1 豁免狀態 | 拿掉會壞什麼 |
|---|---|---|---|---|---|---|---|---|
| GT-01 | RL-0049 | generated↔真源；真源掃描面存在性 | rev5:ADR 0052 | GENERATED_FILES（docs/generated/**＋tools/orchestration/_sk_rules.js＋例外註冊 docs/arc42/ARCHITECTURE.md、docs/ops/LESSONS.md）＋agents.md 之真源掃描面（tracked tools/orchestration 之 *.js／*.mjs 的 *_OPTS 字面；空集合＝WARN） | pre-commit | 1 | — | 鏡像可手改、生成檔與真源靜默分叉、*_OPTS 字面形改動可靜默縮小掃描面而不察 |
| GT-02 | RL-0055 | 事件帳形制、SHA 實證、pin↔worktree | rev5:ADR 0012 | docs/ops/events.jsonl；外層 index gitlink；兩 worktree HEAD | pre-commit | 1 | — | 事件帳可寫入任意形、假 SHA 入帳不察、pin 漂移靜默 |
| GT-03 | RL-0055 | 收刀與 review 事件完整性、BL 引用存在性 | rev5:ADR 0075 | docs/ops/events.jsonl；specs/*/spec.md；docs/arc42/decisions；docs/reviews；docs/ops/BACKLOG.md；docs/ops/BACKLOG-DEFERRED.md | pre-commit | 1 | — | 收刀可指向不存在的 spec／ADR／報告、分流引用斷鏈、BL 號可憑空出現 |
| GT-04 | RL-0074 | ADR 不可變與 supersede 對稱 | rev5:ADR 0012 | docs/arc42/decisions/*.md | pre-commit | 1 | — | 拍板全文可被改寫、翻案可單向 |
| GT-05 | RL-0050 | 配號唯一單調、跨代裸編號、ID 引用存在性與書寫形 | rev5:ADR 0012 | docs/ops 三帳＋現在式面＋兩子庫 pin 樹＋ID 引用面（現在式面之 *.md〔含憲法〕 ∪ tools/**、去生成鏡像與 vendored、ADR body 存量豁免） | pre-commit | 1 | — | 號碼可回收、rev5 編號走私入 rev6 現在式文件、引用可指向不存在的 ID、縮寫形讓全字枚舉漏抓 |
| GT-06 | RL-0048 | 引用斷鏈、時態混入 | rev5:ADR 0012 | tracked *.md；活書家族 | pre-commit | 1 | — | 死連結與未來式靜默入書 |
| GT-07 | RL-0054 | 機密入版控 | rev5:ADR 0003 | tracked 文字檔＋SECRETS_DIR 實值 | pre-commit | 1 | — | 機密實值或樣式進 git 歷史、不可逆 |
| GT-08 | RL-0049 | RULES↔LESSONS 對賬 | rev5:ADR 0024 | docs/ops/RULES.md；docs/ops/LESSONS/*.md | pre-commit | 1 | — | 規則層可無來源、教訓可不指向規則 |
| GT-09 | RL-0057 | 接線與實檔集（含編排骨架子名冊） | rev5:L-061 | README 樹（含 docs/generated 成員行）、tools/deploy/.githooks/.claude、settings.json、EXEC_REQUIRED、tools/orchestration/README.md 檔表（⇔ tools/orchestration/ tracked 檔集；ADR-00020） | pre-commit | 1 | — | hook 被 pnpm install 覆寫或失去 exec bit 而靜默失效、README 地圖與實檔分叉 |
| GT-10 | RL-0035 | 佔位與樣板文、子項名冊（鍵集＋值↔標題）、圖表對賬 | ADR-00004 | BOOK_FACE（docs/arc42 非 decisions、docs/c4、docs/compliance、docs/process） | pre-commit | 1 | — | RAD-AI 表可空殼交卷（22/22 假滿分重演） |
| GT-11 | RL-0056 | bash 黏字與 shebang | rev5:L-001 | 外層 tracked bash 面（*.sh ∪ sh shebang；含 deploy/、.githooks/） | pre-commit | 1 | — | macOS bash 3.2 unbound variable 炸在 preflight |
| GT-12 | RL-0052 | 名冊同源與數量預算、SKIP 鍵登記、人寫面數值／SHA 主張 | rev5:ADR 0024 | tools/docsync/*.py（含 SKIP 錨形鍵 ⊆ DAY1_EXEMPTIONS ∪ ENV_SKIPS）、GATES.md、pre-commit 檔頭、RUNBOOK、RUNBOOK 碼面閘表（⇔ tools/ 頂層 *.py − NON_GATE_TOOLS）、NOTES 波標記、CLAUDE.md 與憲法之 SHA／上限主張（⇔ tools/bootstrap.sh、tools/orchestration/_sk_head.js） | pre-commit | 1 | — | 閘可無語意區塊、名冊三處分叉、預算超限連警告都沒有、跳過分支可無名無登記、人寫面數值與工具常數可單邊漂移 |

## Day-1 豁免登記（鍵｜理由｜解除謂詞｜登記日）

| 鍵 | 理由 | 解除謂詞 | 登記日 |
|---|---|---|---|

## 環境型跳過登記（鍵｜命中謂詞｜理由）

ADR-00019 形：環境缺席＝具名跳過 rc 0（不到期、與 Day-1 豁免兩制）；GT-12 斷言原始碼 SKIP 錨形鍵 ⊆ 本表 ∪ Day-1 豁免。

| 鍵 | 命中謂詞 | 理由 |
|---|---|---|
| GT-02.submodule-absent | base-web／rust-api 之 .git 任一不存在 | 唯讀看碼捷徑（git submodule update --init、無源倉）或新機尚未 bootstrap：pins 的子庫側 SHA 無處實證 |
| GT-05.submodule-absent | base-web／rust-api 之 .git 任一不存在 | 同上：子庫 pin 樹不在，碼面裸編號的 git grep 無標的 |
| GT-07.secrets-absent | SECRETS_DIR 三級解析所得路徑非目錄 | 新機尚未佈機密（deploy/decrypt-secrets.py 未跑）：實值比對無標的；樣式面照掃 |
