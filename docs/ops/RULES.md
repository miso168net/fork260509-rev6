<!-- next: RL-0074 -->
# RULES — 規則層

權威鏈：constitution ＞ ADR accepted ＞ RULES ＞ arc42／c4／compliance／process ＞ generated（與 accepted ADR 衝突＝RULES 有誤、就地改 RULES，輕量軌）。
上限（D8；ADR-00004）：總 92｜implementer 48｜review 18｜fix 19｜主線 52｜人 12。scope 可多值、逗號分隔。
carrier ∈ prompt（烤進 agent prompt、`python3 tools/docsync rules emit --scope <s>` 產出）／lint（GT 閘機器守）／checklist（主線或人的單元邊界檢核）；source ∈ LL-NNNNN／ADR-NNNNN／rev5:L-NNN／rev5:ADR 00NN。
改動本表走輕量軌（不走 Amendment）；配號取檔頭 next 後 bump、號碼不回收；每列規則句為命令句、不帶刀名。

| id | 規則 | scope | carrier | source |
|---|---|---|---|---|
| RL-0001 | 拍板級條目施工前先查拍板紀錄（ADR／events／NOTES）；查無即先問、不以概括指示豁免。勘誤一律以 `python3 tools/docsync errata <詞>` 機器枚舉全 repo 逐處處置、禁止只修被點名處；自擬樣式只取最短公共子串。 | 主線,implementer | prompt | rev5:L-003 |
| RL-0002 | 世代字串殘留掃描同列三形（連字號後綴／黏斜線路徑段／裸詞邊界）；先證樣式集完備、再證零命中——只證所列樣式零命中不算零殘留。 | implementer,主線 | prompt | rev5:L-006 |
| RL-0003 | 凡寫「一律 X」先問反向情境存在嗎；存在即雙向寫並給機器判準（如 pin 分歧先判方向、`merge-base --is-ancestor` 三態）。 | 人,主線 | checklist | rev5:L-008 |
| RL-0004 | 編排 script 的狀態欄不跨角色複用（agent 受阻與審查有 blocker 是兩件事）；fix 迴圈跑滿上限必有確認輪（再 review 一次、空 blocker 即收斂），回報必反映最後一次動作之後。 | 主線 | prompt | rev5:L-011 |
| RL-0005 | 子庫 git 操作一律 `git -C <子庫>` 形、不 cd 進子庫；破壞性驗證每項還原後立即 `git -C <子庫> status --porcelain` 確認回基準態、單獨跑不疊加。 | implementer,fix | prompt | rev5:L-012 |
| RL-0006 | 單元收尾第③步固定落帳（衍生工作→BACKLOG append、踩坑→LESSONS append、tasks 全勾、新拍板→ADR draft→accepted、pin 即時 bump）且必早於 generate；判準＝「下一個人查得到嗎」。 | 主線 | checklist | rev5:L-018 |
| RL-0007 | 非零退出先看首行輸出：`error:` 起首＝工具層拒跑、`FAILED`／`panicked`＝受測物真失敗；迴圈跑測試連首行錯誤一併印。 | implementer,fix | prompt | rev5:L-021 |
| RL-0008 | 派發前對每個 task 問「它 import／呼叫／宣告的東西現在存在嗎」，不存在就往前追是誰該建（沒有任何 task 建＝派工單缺口）；agent 回 blocked 先判允許清單有無缺口、撞到就回頭修 tasks。 | 主線 | checklist | rev5:L-022 |
| RL-0009 | resume 續跑時看門狗 ARMED 行的冒煙位元組是前一輪殘留；續跑冒煙改看最新 agent 檔（mtime＋本輪新字串）。 | 主線 | checklist | rev5:L-023 |
| RL-0010 | resume 只用於故障續跑、不是讓某支 agent 重跑的手段；需某階段重跑＝新開一支只跑該階段的 workflow（新 runId），CONTEXT 寫清已完成結論與勿重報清單。 | 主線 | checklist | rev5:L-027 |
| RL-0011 | 凡改變某數字／集合／方向／名稱／單一權威＝`grep -rn` 枚舉全 repo 同語意命中逐處回報；允許清單內自改、清單外依 status 分值升級；史述保留、現在式改對。 | implementer,fix,review | prompt | rev5:L-032 |
| RL-0012 | agent status 分 `blocked`（整件做不下去、主線立刻接手）與 `done_with_escalation`（交付已完成、只有清單外待辦、附 escalations）兩值；只有前者觸發 script 立即 return、後者照常進審查。 | implementer,fix | prompt | rev5:L-035 |
| RL-0013 | 棄案論證寫完必回頭對所選方案跑同一反例；寫「結構性保證」前先找一條讓它不成立的輸入；雙上限設計必寫「只滿足其一時會怎樣」。 | 人,主線 | checklist | rev5:L-037 |
| RL-0014 | 允許檔清單答「碰得到什麼」而非 task 寫了什麼：對實碼查值域／建構點／下游消費者，另納會因本單元改動而連動的釘值測所在檔、寧可多列。 | 主線 | checklist | rev5:L-042 |
| RL-0015 | 預告必標成預告並附回填義務（該刀 tasks 同批加回填條）；活書家族零未來式，覆核把「屆時／日後／將由」當同義集掃。 | implementer,review | lint | rev5:L-043 |
| RL-0016 | Workflow launch 被擋即 TaskStop 已 armed 的看門狗，重發後帶明確 runId 重掛；ARMED 行冒煙命中 0 或 run id 不對＝鎖錯標的。 | 主線 | checklist | rev5:L-049 |
| RL-0017 | 完成通知一到立即 TaskStop 該看門狗（run 後 journal 永不再動＝必誤報 stall）；stall 閾值語意＝agent 邊界間隔上限。 | 主線 | checklist | rev5:L-051 |
| RL-0018 | 冒煙 token 置於所有 agent prompt 共用段，與「zh-TW」字面同列渲染斷言一併檢查，不得只烤在 implementer prompt。 | 主線 | checklist | rev5:L-057 |
| RL-0019 | 暫改真檔驗紅後以存原文寫回還原、禁 `git checkout` 整檔還原（會丟該檔其它未 commit 改動）；還原後 `git diff --name-only` 證零殘留。 | implementer,fix | prompt | rev5:L-060 |
| RL-0020 | ops 帳本提及刀號／單元輪次一律寫「本刀 U2」形、不寫裸刀號；新建 ops 檔先 `git add` 再驗 lint 才進掃描面。 | implementer,主線 | prompt | rev5:L-067 |
| RL-0021 | 變異紅證必印 skipped=0；探針就地變異或改寫 ROOT、不自 repo 外載入 mutant。 | implementer | prompt | rev5:L-073 |
| RL-0022 | 只准動允許檔清單內的檔；清單外需要動＝絕不擅改、依 status 分值升級；限定式清單項附「本檔之限定外改動＝清單外、走 done_with_escalation」；主線復核看 `git diff` 實際改動面、不看 escalations 欄下結論。 | implementer,fix,主線 | prompt | rev5:L-075 |
| RL-0023 | 枚舉同語意命中逐行剝 token 再判、不 `grep -v` 過濾整行（同行雙 token 會漏）；枚舉筆數要有第二來源對賬。 | implementer,fix | prompt | rev5:L-076 |
| RL-0024 | 對賬 schema 真源腳本化：真源與文件各拉 {欄名:可空性} 比對；可空性以 migration／entity 為準；同檔同型欄寫法不一致即失真訊號。 | implementer | prompt | rev5:L-077 |
| RL-0025 | fix 對 `done_with_escalation`＋零改動當場 return 升級主線、置於零改動偵測之前；零改動偵測只服務 status ok 的真空轉。 | 主線 | prompt | rev5:L-078 |
| RL-0026 | 驗「呼叫處恰 N 處」取 `name(`／`(name)`／`::name` 三形聯集，或改名讓編譯器列出真實使用點；處數型驗收由測試釘、不由人 grep。 | implementer,review | prompt | rev5:L-079 |
| RL-0027 | 連動面盤點數字釘與手抄名冊釘並行（新增一個檔本身就是集合改變）；新增檔的單元把全量測試排在實作早期。 | implementer,主線 | prompt | rev5:L-080 |
| RL-0028 | agent prompt 的事實接地每條附出處（檔:行／指令）、不憑印象寫；同段明令「與碼衝突以碼為準並回報」。 | 主線 | checklist | rev5:L-081 |
| RL-0029 | 變異注入前先讀 detector 排除條件、變異要打在該閘判準上；未紅先印 scanned/hits 自證進入受檢面；閘的 doc 自陳該注入什麼形。 | implementer | prompt | rev5:L-082 |
| RL-0030 | 動工或再 triage 前對碼復核 BACKLOG 條目「因為碼是 X」那一句；條目把技術前提與價值判斷分寫、前提帶出處；關帳時把「哪一句與實碼不符」寫進收單訊息。 | 人,主線 | checklist | rev5:L-083 |
| RL-0031 | 走查還原的清理面含被改列的審計欄（改回值≠改回痕）；`setval` 等還原值自本次 baseline 現讀、不沿用上次指令；baseline 對賬與閘綠是兩道網、都綠才算還原。 | implementer | prompt | rev5:L-084 |
| RL-0032 | 寫驅動件／量測件／編排骨架前先 `ls -R tmp/` 與既有工件（tmp 是跨刀資產庫）；枚舉先跑 errata、手拼 grep 只作補充角度。 | 主線 | checklist | rev5:L-087 |
| RL-0033 | 走查回報「無可觀察實例」或「契約豁免」須附機器反證（psql／grep／原文行號），否則 redo、不得記已知態。 | review | prompt | rev5:L-054 |
| RL-0034 | 文件擴充分階段導入：先可見性層、再決策治理、再營運深度；不一次填滿全部項目。 | 人 | checklist | ADR-00004 |
| RL-0035 | 模板是起手結構不是表單：每節依實況寫，無實體即一句「目前無」附理由；不填樣板文、不留佔位符。 | implementer,review | lint | ADR-00004 |
| RL-0036 | 系統層 AI 元件文件由其建置者填寫；無建置者即標「不適用」附理由、不代填。 | 人 | checklist | ADR-00004 |
| RL-0037 | 每個 AI 元件至少一條可量測品質情境（來源／刺激／環境／回應，含門檻與期限）。 | implementer | checklist | ADR-00004 |
| RL-0038 | 文件更新綁定收刀與部署流程：換模型、換規則版本、換資料源即同批更新名冊與情境。 | 主線 | checklist | ADR-00004 |
| RL-0039 | 記錄跨元件相依與連鎖漂移路徑；不孤立描述單一元件。 | implementer | checklist | ADR-00004 |
| RL-0040 | 文件深度依風險分級；低風險元件只做可見性層、不過度文件化。 | 人 | checklist | ADR-00004 |
| RL-0041 | 活書 frontmatter 帶 `rad_ai_map` 對照鍵；正文子節名一律中文改寫、RAD-AI 文字不逐字複製（只在 README 一句參考來源）；對照總表由 generate 產、不手維護。 | implementer | lint | ADR-00004 |
| RL-0042 | 一切書面產物（report／blocker／程式碼註解／文件／commit 訊息）一律 zh-TW；識別字、程式碼、路徑保留原形；每支 agent prompt 必含「zh-TW」字面。 | 主線,implementer,review,fix | prompt | ADR-00004 |
| RL-0043 | review agent 只讀不寫 repo 檔；findings 只放回傳訊息。 | review | prompt | ADR-00003 |
| RL-0044 | push／merge 回 default branch 需 user 當次明確同意；絕不在 finishing 之前 push／merge；tasks 清單不得排入 push／merge。 | 主線,人 | prompt | ADR-00003 |
| RL-0045 | rust build／test 一律容器內、全程 serial（`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1`）；rust 碼完工前容器內 `cargo fmt --all`。 | implementer,fix | prompt | rev5:ADR 0057 |
| RL-0046 | 引前代編號一律帶 `rev5:`／`rev4:` 前綴（ADR、L、B、Lint、刀名皆同）；rev6 新形原生（BL／LL／ADR 五碼、RL 四碼、GT 二碼）；裸刀號禁、`000-` 創世家族除外。 | implementer,review,主線 | lint | rev5:ADR 0012 |
| RL-0047 | 文件權威鏈 constitution ＞ ADR accepted ＞ RULES ＞ 活書家族 ＞ generated；RULES 與 accepted ADR 衝突＝RULES 有誤、就地改 RULES（輕量軌）。 | 人,主線 | checklist | ADR-00003 |
| RL-0048 | 時態分離：活書家族永遠現在式、未來式住 ops、過去式住 git＋events；完成即刪、git 即史；跨檔引用不用行號、不 deep-link 帳本內部錨、不引 per-machine 路徑。 | implementer,review | lint | ADR-00004 |
| RL-0049 | 人寫／事件源／機器生成三材質各有唯一的家；鏡像不是機器生成就是不存在；`docs/generated/**` 與 GENERATED_FILES 名冊檔禁手改、只由 generate 重算。 | implementer,主線 | lint | ADR-00004 |
| RL-0050 | BL／LL／RL 配號取檔頭 `<!-- next: -->` 後 bump、單調遞增、號碼永不回收；刪條目前先掃現在式引用。 | implementer,主線 | lint | rev5:ADR 0012 |
| RL-0051 | 每條閘一正一反自證、掃描面空集合即紅、變異要打在判準上；Day-1 豁免逐筆具名帶解除謂詞、到期即紅。 | implementer,review | lint | rev5:ADR 0024 |
| RL-0052 | 數量預算（閘 ≤12、RULES 總／per-scope 上限、BACKLOG 開放 ≤25）超限只擋新增、不可調數字；一進一出或走 ADR；波 6 前 WARN、之後 ERROR。 | 主線,人 | lint | ADR-00004 |
| RL-0053 | 收刀簿記＝events append（feature_close 或 misc）→NOTES 改下一步→generate，一顆簿記 commit、排在 merge 之後；簿記落地後量該顆牆鐘、append 一筆 close_bookkeeping perf 事件隨下一顆 commit 入帳。 | 主線 | checklist | ADR-00004 |
| RL-0054 | 機密實值與憑證樣式永不入版控面（含史料面與 tests）；合成樣本執行期串接、不落完整字面；`CHANGE-ME` 起首佔位值不算機密。 | implementer,fix,主線 | lint | rev5:ADR 0003 |
| RL-0055 | 事件帳一行一 JSON 事件、逐型 schema、SHA 逐列向 git 實證；feature_close 帶序號 window；不記「已 push／未 push」揮發狀態、只記 SHA。 | 主線 | lint | rev5:ADR 0012 |
| RL-0056 | bash 內 `$VAR` 後不得緊接非 ASCII（bash 3.2 會黏進變數名）；shebang 只用白名單形。 | implementer,fix | lint | rev5:L-001 |
| RL-0057 | README 目錄樹、hook 註冊、exec bit 名冊與實檔集機器對賬；名冊改動同刀改齊；子庫任一 pnpm install 後重跑 bootstrap 驗 hooks 指紋。 | implementer,主線 | lint | rev5:L-061 |
| RL-0058 | Workflow script 的 agent prompt 全數烤進 script 本體；args 只傳短純量、首段逐欄斷言型別與非空、不符零派發即 throw。 | 主線 | prompt | ADR-00004 |
| RL-0059 | 派發前斷言渲染後 prompt 非空、長度合理、開頭無「undefined」／「null」字面、必含「zh-TW」字面與冒煙 token。 | 主線 | prompt | ADR-00004 |
| RL-0060 | 一切邊界寫死 script 常數不取自 args：fix 迴圈上限 ≤3、單元 agent 保險絲 ≤20；fix agent 允許檔清單寫死常數、次輪只縮不擴。 | 主線 | prompt | ADR-00004 |
| RL-0061 | Workflow launch 與 Monitor 看門狗同一回合原子成對發射、兩 call 間零其他動作；完成通知＋Monitor 雙訊號全覆蓋、毋需輪詢。 | 主線 | checklist | ADR-00004 |
| RL-0062 | 保險絲值由同檔 script 常數推導並自我斷言，MUST ≥ 結構最壞值、不得手挑；runaway 判準數不重複 agent key、非 journal 行數。 | 主線 | prompt | rev5:L-068 |
| RL-0063 | agent 絕不 push／merge／git commit／git checkout；只改工作樹，git 操作由主線負責。 | implementer,fix,review | prompt | ADR-00004 |
| RL-0064 | 絕不寫入 `../fork260509-rev5/`（含子庫與源倉；凍結 SHA 由 bootstrap 斷言）；讀取允許且必要；rev5 stack（埠 2xxxx）不做 schema／seed／設定變更或 `down -v`，rev6 走 3xxxx。 | implementer,fix,主線 | prompt | ADR-00002 |
| RL-0065 | 實作先讀 rev5 對應碼（唯讀）、高度參照但重打字消化不拷貝；註解一律重寫、rev5 出處帶 `rev5:` 前綴；rev6 拍板已推翻的行為不得帶回。 | implementer | prompt | ADR-00003 |
| RL-0066 | TDD 先紅後綠：每個可測面先寫會紅的測、跑到真的紅、再寫實作到綠；分階段推進，每階段容器內 serial 跑一次測試確認綠再進下一階段。 | implementer,fix | prompt | ADR-00004 |
| RL-0067 | 變異自證前提＝被守面已有實例；零實例＝測空集合、紅證結構性 vacuous——延後到實例出現後補做並在 tasks 記回填條。 | implementer | prompt | rev5:L-063 |
| RL-0068 | 對破壞性守門做變異測試先掛快照還原式守衛（arm 拍快照、drop 還原）；刪除式清理守衛救不了 seed 列。 | implementer | prompt | rev5:L-065 |
| RL-0069 | 「應該被拒」的負向樣本業務鍵也帶清理鍵前綴（帶前綴但仍違規的構造），否則守門被改壞那一發的殘列圈不到。 | implementer | prompt | rev5:L-066 |
| RL-0070 | 可見性放寬（私有→pub）前先 grep 函式體內有無被 token 掃描閘守著的呼叫；有則以 finding 要求同批補消費者名冊閘、由 fix 輪落地。 | review,fix | prompt | rev5:L-069 |
| RL-0071 | fix 後次輪 review prompt 必附前輪已駁回 findings 清單（file×summary＋駁回理由）、明令勿沿用被駁論據重報；同一 finding 再報須附新證據，否則計入收斂判定。 | 主線,review | prompt | ADR-00004 |
| RL-0072 | rust 單元收尾除容器內 rc 綠外另跑 `python3 tools/docsync lint`——cargo 綠與 lint 綠是兩件事（碼面閘只看靜態形）。 | 主線 | checklist | rev5:L-064 |
| RL-0073 | review findings 一律三分流（修／轉 BL-NNNNN／won't-fix 立 ADR）；承載處二分：不定期獨立輪落 `docs/reviews/` 報告＋review 事件，feature 收刀之 final holistic review 不落報告、以收單 commit 訊息逐項列處置。 | 主線,review | checklist | rev5:ADR 0075 |

## 名詞

- **刀**＝spec-kit feature（`NNN-<name>` 分支、走 SDD 五步）；**單元**＝一支 Workflow 執行單元；**收刀**＝`merge --no-ff` 回 default 後的簿記。
- **輕量軌**＝不開 SDD 的維護批（單點缺陷、文件與設定調整、既有機制小幅完備化；不動 schema、不新增能力面）；**拍板級**＝schema／scope／破紀律／user 可見行為，拿不準即開 SDD。
- **波**＝啟動書 §5 的階段；**現在波**＝`docs/ops/NOTES.md` 首行 `<!-- wave: N -->`。
- **活書家族**＝docs/arc42（不含 decisions/）、docs/c4、docs/compliance、docs/process；**現在式面**＝活書家族＋docs/ops、docs/generated、README.md、CLAUDE.md、constitution、tools/、deploy/、.githooks/、.claude/hooks 與 settings.json；**史料面**＝docs/brainstorms、specs、docs/reviews；**第三方面**＝.claude/skills、.specify（constitution 除外）；**語料面**＝tools/docsync/tests。後三面不受裸編號、時態、形制掃描。
- **提及**＝反引號或「」內的引用、不算使用（裸編號閘不判）；**人審**＝merge 回 default 前 user 的當次明確同意＋拍板級親決（憲法 §I.8）。
