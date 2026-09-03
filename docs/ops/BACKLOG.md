<!-- next: BL-00003 -->
# BACKLOG — 待辦

條目形 `- BL-NNNNN｜<product／governance>｜<一句話>｜<觸發條件（必填、須可到期）>`；配號取檔頭 next 後 bump、號碼永不回收；完成即刪列、git 即史（RL-0050）。
滯後項另居 `BACKLOG-DEFERRED.md`（user 拍板暫不排程；lint 視為仍開放、STATE 分開計數）——查待辦全帳須兩卷併看。開放上限 25（RL-0052）；觸發條件寫「何時該做」、ADR 翻案觸發器寫「決定何時失效」，兩者不混。

- BL-00001｜governance｜編排骨架 `_sk_head*.js` 三變體各持一組 `*_OPTS`（模型／effort 無單一家、只在 `docs/generated/reference/agents.md` 可見；P-E7 設定債與管線債兩列的去處）→ 收斂為單一常數家與單一骨架｜觸發：首個含 Workflow script 的刀開分支時
- BL-00002｜governance｜GT-10 對 `docs/arc42/09-architecture-decisions.md` 的兩腿在首個 AI-ADR 落地（「目前無」句移除）後互斥：子項名冊腿要 `rad_ai_map` 鍵 ⊇ E5 七欄、第八腿要值＝同檔 `###`，而 E5 子項住 ADR body 的 `####`→ E5 改由 ADR 檔面守或豁免 §9 兩腿（工具改動、一正一反自證）｜觸發：首個 AI-ADR 開寫前
