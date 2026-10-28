<!-- next: BL-00149 -->
# BACKLOG — 待辦

條目形 `- BL-NNNNN｜<product／governance>｜<一句話>｜<觸發條件（必填、須可到期）>`；配號取檔頭 next 後 bump、號碼永不回收；完成即刪列、git 即史（RL-0050）。
滯後項另居 `BACKLOG-DEFERRED.md`（user 拍板暫不排程；配號計入 GT-05 家族、STATE 分開計數）——查待辦全帳須兩卷併看。開放條數不設上限（觀測值、只報表；RL-0052／ADR-00011）；觸發條件寫「何時該做」、ADR 翻案觸發器寫「決定何時失效」，兩者不混。
觸發條件以「動 X」為條件者（「下次動 X 時」「下一支／首個動 X 的單元或刀」等各形），「動」＝改到 X 的可執行碼（X 本身是測試設施時含其測試碼）；純註解／doc 改寫、或只在 X 所在檔的測試模組增案而 X 本體未改，皆不構成到期。

- BL-00002｜governance｜GT-10 對 `docs/arc42/09-architecture-decisions.md` 的兩腿在首個 AI-ADR 落地（「目前無」句移除）後互斥：子項名冊腿要 `rad_ai_map` 鍵 ⊇ E5 七欄、第八腿要值＝同檔 `###`，而 E5 子項住 ADR body 的 `####`→ E5 改由 ADR 檔面守或豁免 §9 兩腿（工具改動、一正一反自證）｜觸發：首個 AI-ADR 開寫前
- BL-00108｜governance｜char 級源碼解析工具組已有**第二份**且已分岔：`rust-api/server/tests/entity_behavior_lint.rs` 持 `skip_ws`／`ident_at`／`close_of`／`split_top`／`peel_attrs`／`attr_spans`／`token_positions` 七支，`wire_i64_guard_lint.rs` 另持同形一組（後者多了 `r#` 前綴、可見性剝除、箭號守衛與角括號深度；前者以 `step()` 逐步跳常值而非預先換白）——同型警語曾住 `tests/common/mod.rs` 的 Drop 守衛面，已隨 BL-00089① 收攏為一支 `run_restore` 而移除；該收攏另使還原殼形成三份（src 側 `run_restore_stmts` 的 DB 腿殼／`RedisKeysGuard` 的鍵腿殼／tests 側合兩腿的 `run_restore`）、三份同改之維護指令已落 doc｜觸發＝第三份出現時，或下一支同時動這兩支 lint 之刀或維護批（先到者）
