---
id: "LL-00007"
rule_id: "RL-0011"
promotion_surface: none
recurrence_of: "LL-00002"
---
LL-00007｜生成物名冊 14→15 時 README 只補了 tasks 條指名的樹行、「想知道 X 看 Y」查詢表漏列——LL-00002 點名的三處列舉面再犯一處

**徵狀**：002 刀 U1 T019 把 `docs/generated/reference/routes.md` 加進 GENERATED_FILES（14→15），tasks 條寫「`README.md` `docs/generated/` 成員行加 `routes`」——implementer 與主線都只改了那一行；README 查詢表既有六件 reference 生成物六件全有列、唯 routes 缺列。U1 第三輪確認 run（wf_8bb6b498-929）規格審查以 `grep -rn "reference/accounts\|reference/schema"` 對賬抓到；`docsync lint`／`check` 對此恆綠（GT-09 掃描面不含 docs/ 敘述性列舉、BL-00009）。

**成因**：LL-00002 守法已寫明「以 `grep -rn` 對該集合每個成員名掃全 repo 現在式面（README 三處：樹行成員窮舉、查詢表、守門鏈列舉）」，但 tasks 條把 README 改動寫成**單處**，主線復核時照條文字面核對「樹行有 routes」即放行、沒把名冊增員當成 RL-0011 集合改變再掃一次。屬 LL-00002 再犯（`recurrence_of`）。

**處置**：README 查詢表補 routes 列（真源＝`rust-api/server/src/router.rs` ROUTES const）；同批以 `reference/<成員名>` 六詞 grep 對賬其餘命中皆單件指針或史料面、無需改。

**晉升面**：none——RL-0011 條文與 LL-00002 守法已足；本坑＝tasks 條「單處」措辭誘導主線只核一處。

**再犯面與守法**：凡 tasks 條寫「README 加一列／一處」而該改動實為名冊增員，主線派發前把 LL-00002 三處（樹行、查詢表、守門鏈）明寫進該 task 條或 CONTEXT；收尾①復核時以成員名 grep 全 repo、把零命中證據寫進 commit 訊息，不以「task 說的那一行改了」放行。
