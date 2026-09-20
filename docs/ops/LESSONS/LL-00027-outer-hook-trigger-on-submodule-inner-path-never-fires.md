---
id: "LL-00027"
rule_id: "RL-0008"
promotion_surface: none
---
LL-00027｜外層 pre-commit 條件段的觸發字面寫成子庫內路徑→永不命中，閘接了線卻從不實跑

**徵狀**：004 刀 tasks 為兩支新碼面閘寫的 pre-commit 觸發條件是 `-e 'base-web/src/views/manage/'`、`-e 'base-web/src/router/elegant/'` 這類子庫內路徑。照字面施工的話，段在、`sh -n` 過、接線守衛綠，但該段一輩子不會被觸發——守門實質下線而全鏈無聲。

**成因**：外層 repo 對子庫只記 gitlink；`git diff --cached --name-only` 在外層只會印 `base-web`／`rust-api` 兩個名字，子庫裡改了哪些檔永不現身於外層 staged 面。SDD 期寫條文時想的是「哪些檔變了該跑」，沒有落到「hook 在哪一層、那一層看得到什麼」。

**處置**：U8 派發前逐條存在性核對（RL-0008）時對照既有四支碼面閘段形抓到，tasks 與 contracts 同顆勘誤為既有形——`-e '<gitlink 名>' -e 'tools/<閘>.py'`（讀憲法當名冊者另加憲法路徑）；細判（子庫 pin 區間內到底動了哪些檔）若需要，住工具內、不住 sh。防法：寫外層 hook 觸發條件時，字面只能取自「外層 tracked 路徑」與「gitlink 名」兩類；凡出現 `<子庫>/…` 形即錯。
