<!-- next: BL-00009 -->
# BACKLOG — 待辦

條目形 `- BL-NNNNN｜<product／governance>｜<一句話>｜<觸發條件（必填、須可到期）>`；配號取檔頭 next 後 bump、號碼永不回收；完成即刪列、git 即史（RL-0050）。
滯後項另居 `BACKLOG-DEFERRED.md`（user 拍板暫不排程；配號計入 GT-05 家族、不計入開放上限 25、STATE 分開計數）——查待辦全帳須兩卷併看。開放上限 25（RL-0052）；觸發條件寫「何時該做」、ADR 翻案觸發器寫「決定何時失效」，兩者不混。

- BL-00001｜governance｜編排骨架 `_sk_head*.js` 三變體各持一組 `*_OPTS`（模型／effort 無單一家、只在 `docs/generated/reference/agents.md` 可見；P-E7 設定債與管線債兩列的去處）→ 收斂為單一常數家與單一骨架（000-r1 併入：R1-080 骨架 review prompt 未烤 RULES_REVIEW／RL-0070、R1-082 harness 無斷言退出碼、EXAMPLE 兩支重組 R1-059／060／062／087／088）｜觸發：首個含 Workflow script 的刀開分支時
- BL-00002｜governance｜GT-10 對 `docs/arc42/09-architecture-decisions.md` 的兩腿在首個 AI-ADR 落地（「目前無」句移除）後互斥：子項名冊腿要 `rad_ai_map` 鍵 ⊇ E5 七欄、第八腿要值＝同檔 `###`，而 E5 子項住 ADR body 的 `####`→ E5 改由 ADR 檔面守或豁免 §9 兩腿（工具改動、一正一反自證）｜觸發：首個 AI-ADR 開寫前
- BL-00003｜governance｜閘補腿群（000-r1 R1-001／R1-027／R1-C301）：GT-03 補 BL 引用存在性腿（review.to_backlog、feature_close／misc 的 backlog_add／done）、七個自稱 Day-1 的 SKIP 分支登記或改 ERROR、CLAUDE.md／憲法內容型主張零閘（主張×閘矩陣見 `docs/reviews/20260904-doc-governance.md`）→ 逐項一正一反自證；新增閘走 ADR-00004 一進一出｜觸發：下次獨立 review 輪前、或任一 lint 誤綠實例出現時
- BL-00004｜governance｜生成器補全群（000-r1 R1-003／R1-008）：erratum 更正視圖套用到 MILESTONES／perf／STATE／DECISIONS-INDEX 四面；DECISIONS-INDEX feature 欄對 misc 型收單 ADR 的反查（需 misc 帶 adrs 欄＝schema 拍板）｜觸發：首筆 erratum 事件、或首個 misc 型收單立 ADR 前
- BL-00005｜governance｜事件欄無家群（000-r1 R1-009／R1-010）：misc.workflow、feature_close.kind／spec_supersessions、非 perf 型 notes 零渲染零指標→補渲染或刪欄（schema 變更、拍板級）｜觸發：首刀收刀（首筆 feature_close）前
- BL-00006｜governance｜review 骨架入庫：000-r1 三支 script（探索／驗證／補漏）與組裝器住 tmp、報告 §0 記 sha256；可重用骨架（lens／兩鏡三態／grader／critic）入 `tools/orchestration/`、agents.md 自動入冊；單元 script 組裝器（`001-schema-baseline` 之 session 工作檔 `tmp/001-assemble.py`：八段拼接＋三道自檢）同批入庫｜觸發：第二次獨立 review 輪開分支時
- BL-00007｜governance｜檢索性第四指標候選：冷啟動探針（命中率／平均 hops／≤3 跳比例）與否定對照題（答錯數）入 STATE 需新 generated 欄＋資料源（ADR）｜觸發：第二次獨立 review 輪
- BL-00008｜product｜`ActiveModelBehavior` 恆空（ORM 行為層不承載六審計欄自動化、審計欄由 facade 顯式成對寫）之機器錨：承 `rev5:server/tests/entity_behavior_lint.rs` 形隨 server crate 建立——`rust-api/entity/src/sys_user_role.rs` 註解揭露現無此錨（本刀 U1 碼品質審查留帳）｜觸發：002 刀（server crate）開分支時
