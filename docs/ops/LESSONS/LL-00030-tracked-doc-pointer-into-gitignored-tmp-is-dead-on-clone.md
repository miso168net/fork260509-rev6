---
id: "LL-00030"
rule_id: "RL-0077"
promotion_surface: rules
---
LL-00030｜受版控文件把範本／工件指成 `tmp/` 具名路徑——tmp 是 gitignored 工作區，他人 clone 與清理後皆無此檔，指針當場死掉且沒有任何閘會紅

**徵狀**：`docs/ops/LESSONS/` 三筆（LL-00008／LL-00020／LL-00021）與 `tools/orchestration/` 三處（`README.md`、`assemble.py`、`EXAMPLE-dual-implementer.mjs`）把「範本住哪」寫成 `tmp/` 底下的具名檔；其中入庫工具所指的組裝器檔早在後續清理中不存在。清工作區時主線一度提議「把字面更新成新的 tmp 路徑」，那只是把死指針換個位置。

**成因**：`tmp/` 既是跨刀資產庫（RL-0032）又是 gitignored 工作區——同一目錄兼「我這台機器上現在有的東西」與「值得長期參照的範本」兩種身分，寫文件時很容易把後者當成可被受版控文件引用的穩定落點。而路徑指向不存在的**未受版控**檔時，連結腿看不到（不是 markdown 連結）、檔案存在性腿也不管（tmp 不在 tracked 面），於是全綠。

**處置**：現在式面十處改寫：LESSONS 三筆改成不綁路徑的描述（「走查腳本範本（輪詢 exp 形）」「U3／U4 單元定義」），`tools/orchestration/` 三處改指入庫落點與刀名形，`deploy/sops.sh` 用法例改佔位形。規則立為 RL-0077，機器面掛在 GT-06 新腿（面＝現在式面全副檔名；佔位／glob 形與 OS `/tmp/` 不入射程；史料面與凍結面〔accepted ADR body、events、generated〕豁免）。

**再犯面與守法**：凡在受版控檔寫「範本／工件在哪」一律先問「同事 clone 完這個 repo 有沒有這個檔」——沒有就不是可引用的落點：要嘛把它入庫（如 `tools/orchestration/EXAMPLE-*.py`）、要嘛寫成不綁路徑的描述、要嘛用佔位形（`tmp/<名>.json`）。既有違規的修法是**拿掉路徑**、不是更新路徑。
