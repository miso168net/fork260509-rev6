// 機器生成：python3 tools/docsync generate（自 docs/ops/RULES.md 之 rules emit）——嚴禁手改；差異由 pre-commit check 攔下
const RULES = `=== RULES scope=implementer（39 條）===
RL-0001｜拍板級條目施工前先查拍板紀錄（ADR／events／NOTES）；查無即先問、不以概括指示豁免。勘誤一律以 \`python3 tools/docsync errata <詞>\` 機器枚舉全 repo 逐處處置、禁止只修被點名處；自擬樣式只取最短公共子串。
RL-0002｜世代字串殘留掃描同列三形（連字號後綴／黏斜線路徑段／裸詞邊界）；先證樣式集完備、再證零命中——只證所列樣式零命中不算零殘留。
RL-0005｜子庫 git 操作一律 \`git -C <子庫>\` 形、不 cd 進子庫；破壞性驗證每項還原後立即 \`git -C <子庫> status --porcelain\` 確認回基準態、單獨跑不疊加。
RL-0007｜非零退出先看首行輸出：\`error:\` 起首＝工具層拒跑、\`FAILED\`／\`panicked\`＝受測物真失敗；迴圈跑測試連首行錯誤一併印。
RL-0011｜凡改變某數字／集合／方向／名稱／單一權威＝\`grep -rn\` 枚舉全 repo 同語意命中逐處回報；★掃描種子四形皆須跑：①該物之名 ②其未來式短語（「隨…刀進場」「尚無…」）③承載它的活書枚舉表 ④舊數量詞字面；允許清單內自改、清單外依 status 分值升級；史述保留、現在式改對。
RL-0012｜agent status 分 \`blocked\`（整件做不下去、主線立刻接手）與 \`done_with_escalation\`（交付已完成、只有清單外待辦、附 escalations）兩值；只有前者觸發 script 立即 return、後者照常進審查。
RL-0015｜預告必標成預告並附回填義務（該刀 tasks 同批加回填條）；活書家族零未來式，覆核把「屆時／日後／將由／隨…刀進場／尚無…」當同義集掃；落地某能力的單元必以其名掃「隨…進場」形改現在式。
RL-0019｜暫改真檔驗紅後以存原文寫回還原、禁 \`git checkout\` 整檔還原（會丟該檔其它未 commit 改動）；還原後 \`git diff --name-only\` 證零殘留。
RL-0020｜提及刀號／單元輪次寫「本刀 U2」形、不寫裸刀號；★跨刀存活面（BACKLOG／LESSONS／工具與 hook 註解）改寫刀名形「001 刀 U2」——「本刀」只用於該刀分支內的 tasks／NOTES／commit 訊息；新建 ops 檔先 \`git add\` 再驗 lint 才進掃描面。
RL-0021｜變異紅證必印 skipped=0；探針就地變異或改寫 ROOT、不自 repo 外載入 mutant。
RL-0022｜只准動允許檔清單內的檔；清單外需要動＝絕不擅改、依 status 分值升級；限定式清單項附「本檔之限定外改動＝清單外、走 done_with_escalation」；主線復核看 \`git diff\` 實際改動面、不看 escalations 欄下結論。
RL-0023｜枚舉同語意命中逐行剝 token 再判、不 \`grep -v\` 過濾整行（同行雙 token 會漏）；枚舉筆數要有第二來源對賬。
RL-0024｜對賬 schema 真源腳本化：真源與文件各拉 {欄名:可空性} 比對；可空性以 migration／entity 為準；同檔同型欄寫法不一致即失真訊號。
RL-0026｜驗「呼叫處恰 N 處」取 \`name(\`／\`(name)\`／\`::name\` 三形聯集，或改名讓編譯器列出真實使用點；處數型驗收由測試釘、不由人 grep。
RL-0027｜連動面盤點數字釘與手抄名冊釘並行（新增一個檔本身就是集合改變）；新增檔的單元把全量測試排在實作早期。
RL-0029｜變異注入前先讀 detector 排除條件、變異要打在該閘判準上；未紅先印 scanned/hits 自證進入受檢面；閘的 doc 自陳該注入什麼形。
RL-0031｜走查還原的清理面含被改列的審計欄（改回值≠改回痕）；\`setval\` 等還原值自本次 baseline 現讀、不沿用上次指令；baseline 對賬與閘綠是兩道網、都綠才算還原。
RL-0035｜模板是起手結構不是表單：每節依實況寫，無實體即一句「目前無」附理由；不填樣板文、不留佔位符。
RL-0037｜每個 AI 元件至少一條可量測品質情境（來源／刺激／環境／回應，含門檻與期限）。
RL-0039｜記錄跨元件相依與連鎖漂移路徑；不孤立描述單一元件。
RL-0041｜活書 frontmatter 帶 \`rad_ai_map\` 對照鍵；正文子節名一律中文改寫、RAD-AI 文字不逐字複製（只在 README 一句參考來源）；對照總表由 generate 產、不手維護。
RL-0042｜一切書面產物（report／blocker／程式碼註解／文件／commit 訊息）一律 zh-TW；識別字、程式碼、路徑保留原形；每支 agent prompt 必含「zh-TW」字面。具名例外二項（皆屬 ADR-00003 之 spec-kit「第三方面」）：①spec-kit git extension 自動 commit 之 \`[Spec Kit]\` 英文固定訊息 ②\`/speckit-specify\` 自產 \`specs/*/checklists/requirements.md\` 之內建檢核項文字。
RL-0045｜rust build／test 一律容器內、全程 serial（\`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1\`）；rust 碼完工前容器內 \`cargo fmt --all\`。
RL-0046｜引前代編號一律帶 \`rev5:\`／\`rev4:\` 前綴（ADR、L、B、Lint、刀名皆同）；rev6 新形原生（BL／LL／ADR 五碼、RL 四碼、GT 二碼、migration 短號 \`m\` 四碼＝ADR-00008）；裸刀號禁、\`000-\` 創世家族除外。
RL-0048｜時態分離：活書家族永遠現在式、未來式住 ops、過去式住 git＋events；完成即刪、git 即史；跨檔引用不用行號、不 deep-link 帳本內部錨、不引 per-machine 路徑。
RL-0049｜人寫／事件源／機器生成三材質各有唯一的家；鏡像不是機器生成就是不存在；\`docs/generated/**\` 與 GENERATED_FILES 名冊檔禁手改、只由 generate 重算。
RL-0050｜BL／LL／RL 配號取檔頭 \`<!-- next: -->\` 後 bump、單調遞增、號碼永不回收；刪條目前先掃現在式引用。
RL-0051｜每條閘一正一反自證、掃描面空集合即紅、變異要打在判準上；Day-1 豁免逐筆具名帶解除謂詞、到期即紅。
RL-0054｜機密實值與憑證樣式永不入版控面（含史料面與 tests）；合成樣本執行期串接、不落完整字面；\`CHANGE-ME\` 起首佔位值不算機密。
RL-0056｜bash 內 \`$VAR\` 後不得緊接非 ASCII（bash 3.2 會黏進變數名）；shebang 只用白名單形。
RL-0057｜README 目錄樹、hook 註冊、exec bit 名冊與實檔集機器對賬；名冊改動同刀改齊；子庫任一 pnpm install 後重跑 bootstrap 驗 hooks 指紋。
RL-0063｜agent 絕不 push／merge／git commit／git checkout；只改工作樹，git 操作由主線負責。
RL-0064｜絕不寫入 \`../fork260509-rev5/\`（含子庫與源倉；凍結 SHA 由 bootstrap 斷言）；讀取允許且必要；rev5 stack（埠 2xxxx）不做 schema／seed／設定變更或 \`down -v\`，rev6 走 3xxxx。
RL-0065｜實作先讀 rev5 對應碼（唯讀）、高度參照但重打字消化不拷貝；註解一律重寫、rev5 出處帶 \`rev5:\` 前綴；rev6 拍板已推翻的行為不得帶回。
RL-0066｜TDD 先紅後綠：每個可測面先寫會紅的測、跑到真的紅、再寫實作到綠；分階段推進，每階段容器內 serial 跑一次測試確認綠再進下一階段。
RL-0067｜變異自證前提＝被守面已有實例；零實例＝測空集合、紅證結構性 vacuous——延後到實例出現後補做並在 tasks 記回填條。
RL-0068｜對破壞性守門做變異測試先掛快照還原式守衛（arm 拍快照、drop 還原）；刪除式清理守衛救不了 seed 列。
RL-0069｜「應該被拒」的負向樣本業務鍵也帶清理鍵前綴（帶前綴但仍違規的構造），否則守門被改壞那一發的殘列圈不到。
RL-0075｜改動屬拍板級判準（user／operator 可見行為變更、schema／migration、feature scope 邊界、破紀律例外）者，縱使檔在允許清單內亦一律 \`done_with_escalation\`＋\`escalatedFindings\` 指名、不得落地；審查員標「拍板級／超出權限」之 finding 只落據實碼註那一半。
RULES-VERSION: d7ed17b0b324
`;
const RULES_REVIEW = `=== RULES scope=review（14 條）===
RL-0011｜凡改變某數字／集合／方向／名稱／單一權威＝\`grep -rn\` 枚舉全 repo 同語意命中逐處回報；★掃描種子四形皆須跑：①該物之名 ②其未來式短語（「隨…刀進場」「尚無…」）③承載它的活書枚舉表 ④舊數量詞字面；允許清單內自改、清單外依 status 分值升級；史述保留、現在式改對。
RL-0015｜預告必標成預告並附回填義務（該刀 tasks 同批加回填條）；活書家族零未來式，覆核把「屆時／日後／將由／隨…刀進場／尚無…」當同義集掃；落地某能力的單元必以其名掃「隨…進場」形改現在式。
RL-0026｜驗「呼叫處恰 N 處」取 \`name(\`／\`(name)\`／\`::name\` 三形聯集，或改名讓編譯器列出真實使用點；處數型驗收由測試釘、不由人 grep。
RL-0033｜走查回報「無可觀察實例」或「契約豁免」須附機器反證（psql／grep／原文行號），否則 redo、不得記已知態。
RL-0035｜模板是起手結構不是表單：每節依實況寫，無實體即一句「目前無」附理由；不填樣板文、不留佔位符。
RL-0042｜一切書面產物（report／blocker／程式碼註解／文件／commit 訊息）一律 zh-TW；識別字、程式碼、路徑保留原形；每支 agent prompt 必含「zh-TW」字面。具名例外二項（皆屬 ADR-00003 之 spec-kit「第三方面」）：①spec-kit git extension 自動 commit 之 \`[Spec Kit]\` 英文固定訊息 ②\`/speckit-specify\` 自產 \`specs/*/checklists/requirements.md\` 之內建檢核項文字。
RL-0043｜review agent 只讀不寫 repo 檔；findings 只放回傳訊息。
RL-0046｜引前代編號一律帶 \`rev5:\`／\`rev4:\` 前綴（ADR、L、B、Lint、刀名皆同）；rev6 新形原生（BL／LL／ADR 五碼、RL 四碼、GT 二碼、migration 短號 \`m\` 四碼＝ADR-00008）；裸刀號禁、\`000-\` 創世家族除外。
RL-0048｜時態分離：活書家族永遠現在式、未來式住 ops、過去式住 git＋events；完成即刪、git 即史；跨檔引用不用行號、不 deep-link 帳本內部錨、不引 per-machine 路徑。
RL-0051｜每條閘一正一反自證、掃描面空集合即紅、變異要打在判準上；Day-1 豁免逐筆具名帶解除謂詞、到期即紅。
RL-0063｜agent 絕不 push／merge／git commit／git checkout；只改工作樹，git 操作由主線負責。
RL-0070｜可見性放寬（私有→pub）前先 grep 函式體內有無被 token 掃描閘守著的呼叫；有則以 finding 要求同批補消費者名冊閘、由 fix 輪落地。
RL-0071｜fix 後次輪 review prompt 必附前輪已駁回 findings 清單（file×summary＋駁回理由）、明令勿沿用被駁論據重報；同一 finding 再報須附新證據，否則計入收斂判定。
RL-0073｜review findings 一律三分流（修／轉 BL-NNNNN／won't-fix 立 ADR）；承載處三類：①不定期獨立輪落 \`docs/reviews/\` 報告＋review 事件 ②附屬某刀而由 user 臨時發起的對照輪同樣落報告＋review 事件、以其 \`feature\` 欄標所屬刀 ③feature 收刀之 final holistic review 不落報告、以收單 commit 訊息逐項列處置。
RULES-VERSION: d7ed17b0b324
`;
const RULES_FIX = `=== RULES scope=fix（16 條）===
RL-0005｜子庫 git 操作一律 \`git -C <子庫>\` 形、不 cd 進子庫；破壞性驗證每項還原後立即 \`git -C <子庫> status --porcelain\` 確認回基準態、單獨跑不疊加。
RL-0007｜非零退出先看首行輸出：\`error:\` 起首＝工具層拒跑、\`FAILED\`／\`panicked\`＝受測物真失敗；迴圈跑測試連首行錯誤一併印。
RL-0011｜凡改變某數字／集合／方向／名稱／單一權威＝\`grep -rn\` 枚舉全 repo 同語意命中逐處回報；★掃描種子四形皆須跑：①該物之名 ②其未來式短語（「隨…刀進場」「尚無…」）③承載它的活書枚舉表 ④舊數量詞字面；允許清單內自改、清單外依 status 分值升級；史述保留、現在式改對。
RL-0012｜agent status 分 \`blocked\`（整件做不下去、主線立刻接手）與 \`done_with_escalation\`（交付已完成、只有清單外待辦、附 escalations）兩值；只有前者觸發 script 立即 return、後者照常進審查。
RL-0019｜暫改真檔驗紅後以存原文寫回還原、禁 \`git checkout\` 整檔還原（會丟該檔其它未 commit 改動）；還原後 \`git diff --name-only\` 證零殘留。
RL-0022｜只准動允許檔清單內的檔；清單外需要動＝絕不擅改、依 status 分值升級；限定式清單項附「本檔之限定外改動＝清單外、走 done_with_escalation」；主線復核看 \`git diff\` 實際改動面、不看 escalations 欄下結論。
RL-0023｜枚舉同語意命中逐行剝 token 再判、不 \`grep -v\` 過濾整行（同行雙 token 會漏）；枚舉筆數要有第二來源對賬。
RL-0042｜一切書面產物（report／blocker／程式碼註解／文件／commit 訊息）一律 zh-TW；識別字、程式碼、路徑保留原形；每支 agent prompt 必含「zh-TW」字面。具名例外二項（皆屬 ADR-00003 之 spec-kit「第三方面」）：①spec-kit git extension 自動 commit 之 \`[Spec Kit]\` 英文固定訊息 ②\`/speckit-specify\` 自產 \`specs/*/checklists/requirements.md\` 之內建檢核項文字。
RL-0045｜rust build／test 一律容器內、全程 serial（\`docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1\`）；rust 碼完工前容器內 \`cargo fmt --all\`。
RL-0054｜機密實值與憑證樣式永不入版控面（含史料面與 tests）；合成樣本執行期串接、不落完整字面；\`CHANGE-ME\` 起首佔位值不算機密。
RL-0056｜bash 內 \`$VAR\` 後不得緊接非 ASCII（bash 3.2 會黏進變數名）；shebang 只用白名單形。
RL-0063｜agent 絕不 push／merge／git commit／git checkout；只改工作樹，git 操作由主線負責。
RL-0064｜絕不寫入 \`../fork260509-rev5/\`（含子庫與源倉；凍結 SHA 由 bootstrap 斷言）；讀取允許且必要；rev5 stack（埠 2xxxx）不做 schema／seed／設定變更或 \`down -v\`，rev6 走 3xxxx。
RL-0066｜TDD 先紅後綠：每個可測面先寫會紅的測、跑到真的紅、再寫實作到綠；分階段推進，每階段容器內 serial 跑一次測試確認綠再進下一階段。
RL-0070｜可見性放寬（私有→pub）前先 grep 函式體內有無被 token 掃描閘守著的呼叫；有則以 finding 要求同批補消費者名冊閘、由 fix 輪落地。
RL-0075｜改動屬拍板級判準（user／operator 可見行為變更、schema／migration、feature scope 邊界、破紀律例外）者，縱使檔在允許清單內亦一律 \`done_with_escalation\`＋\`escalatedFindings\` 指名、不得落地；審查員標「拍板級／超出權限」之 finding 只落據實碼註那一半。
RULES-VERSION: d7ed17b0b324
`;
