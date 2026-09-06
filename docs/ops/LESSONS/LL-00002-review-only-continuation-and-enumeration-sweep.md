---
id: "LL-00002"
rule_id: "none：RL-0010（續跑＝新開只跑該階段的 run）與 RL-0011（同語意命中逐處改對）條文已在；本坑＝主線落地升級項後未先自掃就發射續跑、兩條未被串起——守法寫進本檔與組裝流程，不加規則"
promotion_surface: none
---
LL-00002｜fix 升級後的續跑：骨架不支援只跑審查段、主線落地又未先自掃同語意列舉——兩支續跑 run 各被 README 一行打回

**徵狀**：001 刀 U3 主 run 在規格審查段以 rev5:L-078 分支收場（唯一 blocker＝README 樹行殘留已兌現預告、fix 判成立但落授權面外、正確零改動升級主線）。主線落地後依 RL-0010 需「新開一支只跑審查段的 workflow」，但單一骨架斷言 IMPLEMENTERS ≥ 1、無此形；補上續跑形發射後，第一支續跑 run 又被 README `docs/generated/` 樹行的成員窮舉未隨名冊 12→14 補列打回（同樣 rev5:L-078 分支）；第二支才收斂。多花兩支 run（約 55 萬 token、40 分鐘）。

**成因**：①骨架把「有 implementer」寫死為前提，RL-0010 的續跑形沒有原生載體；②主線落地升級項時只改了被指名的那一行，未先以 RL-0011 對「本單元改變的集合」（生成物名冊 12→14、pre-commit 段集）全 repo 掃同語意命中——README 三處（樹行成員窮舉、查詢表、守門鏈列舉）與 `docs/process/P-E1-boundary.md` 一處同時過時，而 GT-09 掃描面不含 docs/、對此類列舉恆假綠（BL-00009）。

**處置**：骨架加 IMPLEMENTERS=0 續跑形（`_sk_head.js` 斷言改 ≥0、`_sk_main.js` 零 impl 直入審查、`harness-test.mjs` 案 7 於 N=0 改驗零 implementer、`tools/orchestration/README.md` 兩列）；續跑單元定義承原單元、CONTEXT 加「已完成結論與勿重報清單」段、允許清單只縮不擴；第二次落地前先全掃（generated 名冊數／reference-src 提及／pre-commit 鏈列舉）再發射，續跑 run 2 一輪收斂。

**再犯面與守法**：凡 fix 以 `done_with_escalation` 零改動升級（rev5:L-078 分支）→ 主線落地時先問「本單元改變了哪個集合」、以 `grep -rn` 對該集合每個成員名掃全 repo 現在式面、逐處改對，再組續跑 script（IMPLEMENTERS=0、勿重報清單）發射（★ADR-00013 起：零改動升級不再終止 run、碼品質段照跑，續跑形只用於故障續跑或主線判需重審）；機器面待 BL-00009 補 GT-09 腿後收口。
