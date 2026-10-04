---
id: "LL-00060"
rule_id: "none：連動關係已明文於 rust-api `server/src/router.rs` ROUTES doc 與 `tools/docsync/tests/test_references.py` 該測註解；缺的是收尾②沒跑 docsync test，守法寫進本檔與主線收尾鏈腳本（不入版控之工作檔與跨刀資產）；受版控之程序面＝CLAUDE.md §2 六步序②已補此步（user 2026-10-04 收刀親決）"
promotion_surface: none
---
LL-00060｜ROUTES 只改次序也要同批改 docsync 釘值測：收尾②只跑 docsync check／lint、pre-commit 又只在 staged 含 tools/docsync/ 時才跑 docsync 自測，釘值測紅了一整個單元沒人察覺（006 刀 U16→U17）

**徵狀**：006 刀 U17 的三支 implementer 與兩輪審查都回報 `python3 -B tools/docsync test` 有一支既有紅：`test_references.TestRoutes.test_real_repo_pinned_rows`，第 28 個元素期望 getRoleHome、實得 getMenuList/v2。列集相等（49＝49），只有索引 28～46 的次序不同。

**成因**：
- 006 刀 U16（rust-api `10ac6dc`）為了讓端點候選序對齊 rev5，把 ROUTES 三條改置：getRoleHome／updateRoleHome 移到 restoreMenu 之後，getAllPages 移到 restorePolicy 之後。同顆改了 router.rs 內的序釘測試與 contract.rs 兩張授權態矩陣，generate 也重算了 routes.md。
- 外層 `test_real_repo_pinned_rows` 釘的是 ROUTES 逐列全等（含次序），這顆沒改到。router.rs ROUTES doc 與該測註解都寫明「追加時須同批改」，但「追加」字面讓人只想到增列，沒想到改置也會動到。
- 三道該擋的關都沒擋：
  - pre-commit 的 selftest-docsync 只在 staged 含 `tools/docsync/` 時才跑。
  - GT-01 漂移在 generate 之後就消失，lint 與 check 照綠。
  - 主線收尾②的鏈只跑 docsync check／lint，沒跑 docsync test。

**處置**：U17 由主線把該測兩張期望表（解析列元組表、routes.md 渲染行表）改成現行宣告序，`TestRoutes` 8 支全綠。主線收尾鏈腳本（不入版控）自 U17 起加跑 `python3 -B tools/docsync test`，跨刀資產之收尾鏈範本同批補（006 刀 final holistic review 揭出範本漏此步）。

**晉升面**：none。連動關係已明文於上述兩處，本坑缺的只是收尾鏈沒跑測試這一步；本守法已寫入受版控之程序面 CLAUDE.md §2 六步序②（user 2026-10-04 收刀親決）。

**再犯面與守法**：
- ①rust-api 動到 ROUTES 的單元，不論增列、刪列或只改次序，收尾②一律跑 `python3 -B tools/docsync test`，不能只看 check／lint 綠就放行。
- ②docsync test 的紅要先分清是 GT-01 漂移的連帶（generate 即消），還是釘值測本身。後者不會因 generate 而消失。
