---
id: "LL-00016"
rule_id: "RL-0076"
promotion_surface: rules
---
LL-00016｜implementer 把 rev5 對應檔的註解逐字搬進 rev6、靠審查輪才抓到——「註解一律重寫」是散文規則、交付前沒有機器自核

**徵狀**：003 刀 U2（run `wf_2e4bf854-5d3`）與 U3（run `wf_9bfcfb16-f82`）的規格對照審查第 1 輪都開出同一形 blocker：新建檔的註解與 `../fork260509-rev5/` 同路徑檔逐字相同。U3 六支 facade 改寫前的逐字重疊（門檻 25 字元）＝sys_token 50.0%、sys_login_attempt 43.4%、session_event 40.4%、sys_menu 32.9%、sys_user 24.4%、sys_role 16.7%，最長單段 260 字元；審查員得先自己寫比對腳本才開得出這條 finding，fix 輪再把六檔散文全部重寫（碼面零改動）——兩個單元各燒掉一輪 review＋一輪 fix。主線收尾把同一把尺掃回 002 刀落地的檔：`rust-api/server/` src 16 檔與 tests 6 檔在門檻 40 字元下重疊 7.4%～81.2%（obs.rs 72.6%、tests/entity_behavior_lint.rs 81.2%），即 002 刀整刀都是這樣過的、當時沒有任何一輪審查抓到。

**成因**：RL-0065「註解一律重寫」烤在 implementer prompt 裡，但它是一句散文——implementer 讀 rev5 對應碼「重打字消化」時，doc 註解是最容易原樣抄過來的部分（碼要改型別與 API、註解不用），而交付前的自檢清單裡沒有任何一項會量這件事；審查員看到的是兩份各自通順的中文、要抓逐字相同得先寫工具。規則有、量尺沒有，於是違規的偵測完全靠某個審查員當輪的自主性，002 刀就是零偵測穿過。

**處置**：U2／U3 兩輪 fix 已把當單元檔改寫到門檻 40 字元下 ≤4.1%；主線把審查員／fix agent 各自即興寫的比對腳本收成 `tools/comment-overlap.py`（rev5 對應檔自動映射、預設門檻 40 字元／上限 5%、任一檔超標 rc 1、`test` 子命令一正一反自證且入 pre-commit 條件觸發名冊；門檻取 40 是因為識別字、SQL 片段、路徑與 doctest 碼行本就兩代共用、門檻 25 下識別字密集檔仍佔 10%～12%，而逐字搬運檔在門檻 40 下落 18%～45%，兩態不相接）；002 刀遺留的 22 檔開 BL-00050 待維護批改寫、003 刀各單元改寫到的檔隨新規則就地歸零。

**再犯面與守法**：凡承 rev5 對應碼新建或改寫的 rust 檔，implementer 交付前 MUST 跑 `python3 tools/comment-overlap.py <檔…>` 得 rc 0 並把逐檔百分比寫進 report——量尺跟規則同住 prompt，違規在交付前就紅、不再等審查輪；限定式（只准）項的既有超標不在該單元射程、report 指名即可。守法落 RL-0076（implementer scope、prompt carrier）。主線收尾第①步復核對本單元承 rev5 的檔同跑一次。
