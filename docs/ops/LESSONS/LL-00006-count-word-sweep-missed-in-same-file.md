---
id: "LL-00006"
rule_id: "RL-0011"
promotion_surface: none
recurrence_of: "LL-00004"
---
LL-00006｜能力落地後只掃了能力名與未來式短語、沒掃「數量詞」——同一檔 §5.1 改對、§5.2「三 crate」留假述，確認輪多跑一輪

**徵狀**：002 刀 U1 把 server crate 落進 rust-api workspace（members 三→四）後，主線依 LL-00004 守法掃了 `隨 server crate 進場`／`server 隨 002` 並改對 `docs/arc42/05-building-block-view.md` §5.1 白盒表的 server 列；U1 審查確認輪（wf_c3c14efa-cfb）規格審查員以 `python3 tools/docsync errata "三 crate"` 掃出同檔 §5.2 第 26 行仍寫「Cargo workspace 三 crate……server crate 與管線形隨 002 刀進場」——同一檔兩節對同一事實陳述相反，且碼品質輪因此未跑、確認輪多跑一輪（約 18 分鐘、2 支 agent）。

**成因**：LL-00004 守法三形（①能力名 ②未來式短語 ③活書枚舉表）在本次全做了，但「members 三→四」這種**數量改變**是第四種形——文件裡寫的是「三 crate」而非能力名、也不帶未來式，三形全掃不到它。RL-0011 條文明寫「凡改變某**數字**／集合／…＝grep 枚舉」，主線把「加一個 crate」當成集合改變（掃能力名）、沒當成數字改變（掃舊數量詞「三 crate」「三支」）。屬執行疏漏、非規則缺口。

**處置**：主線改 §5.2 第 26 行為四 crate 現在式（與 §5.1 一致）、`errata "三 crate"` 復掃現在式面只剩 frontmatter 第 7 行（T043／U8 具名回填）；發第二輪確認 run（wf_e7a8937d-539）。

**晉升面**：none——RL-0011 已含「數字」；本坑記入 LL-00004 之再犯（`recurrence_of`），並把守法補成四形。

**再犯面與守法**：凡單元讓某集合的**元素數**改變（crate 數、閘數、名冊項數、表數、路由數），主線 RL-0011 掃描種子 MUST 含第四形＝**舊數量詞字面**（「三 crate」「三支」「12 閘」「14 項」「兩條」等，含中文數字與阿拉伯數字兩寫法），對現在式面逐處判「改／史料不動／accepted 不動」，並把零命中證據寫進收尾 commit 訊息；審查員亦以同一四形掃。
