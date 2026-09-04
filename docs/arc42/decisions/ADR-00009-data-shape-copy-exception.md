---
id: "ADR-00009"
title: 憲法 §I.5 例外清單擴展——資料形狀契約三件整檔拷貝（基線結構 migration＋基線 seed migration＋基線 entity 15 檔；射程鎖 rev5 rust-api `92919b9`；MINOR 1.1.0）
date: 2026-09-04
status: accepted
supersedes: []
superseded_by: []
provenance: "001 schema 基線刀 brainstorm §0 user 指示與 Q2（2026-09-03）、§2 草案要點；grill 拍板 Q1 版級 MINOR（2026-09-04）；specify clarify Q1 註解語意判準（2026-09-04）；user 核准 Amendment 全文（2026-09-04）。前代立場：rev5:ADR 0001 決定 3「資料形狀是契約不是碼」、rev5:ADR 0003「佔位字面非機密」。"
tags: [governance, constitution, schema, rust-api]
---

## 背景

- 憲法 §I.5 鐵紀律：rust-api 全新寫、前代 source 唯讀參考、**拷貝禁止**（實作重打字消化）；既有例外僅 `sea-orm-adapter`／`xdb` 工具性 crate。
- rev5 的資料庫基線是**定稿制**成果：15 表 169 欄由 user 親排欄序、266 列 seed 全量過目簽核、與凍結 fixtures 逐位元全等驗證；rev6 拍板（啟動書 D13、001 brainstorm Q1）rev6 資料庫基線＝rev5 終態 15 表、不重開親排與過目工作坊。
- user 指示（2026-09-03）：`rev5:m001`／`rev5:m002` 程式碼完整照抄、註解重寫；Q2 裁定例外射程＝資料形狀契約三件（結構 migration、seed migration、entity 15 檔）＝rev5 rust-api 凍結 SHA `92919b9` 之 17 檔。
- rev6 UI 對照驗收（CDP 對 rev5 stack 全等）要求兩代資料形狀同一；entity 漂移閘兩側（快照 vs entity）亦須同源。
- ADR-00008 已定 migration 短號四碼：承襲 rev5 migration 時檔名改 `m0001_`／`m0002_`，口徑＝「內容逐位元、檔名依 ADR-00008」。

## 決策驅動因子

- 零資訊增益 vs 抄錯風險：定稿制成果已簽核，重打字 17 檔只可能引入偏差、不可能增加正確性。
- 機器可證：資料形狀三件有現成的全等驗證鏈（去註解 diff、pristine 重放、fixtures 雙源互證），例外的邊界可被機器守住。
- 權威鏈：例外必須住憲法 §I.5（RL-0047 constitution 最高），不能只住 ADR 或 brainstorm。
- 版級訊號：§V.3 的 MAJOR 保留給「方向性反轉」；本案規則方向（code 不拷貝）不變、只擴例外清單。

## 考慮過的替代案

- **重打字消化 17 檔（照 §I.5 原則）**——否決：零資訊增益、抄錯即破雙源互證與 UI 對照前提；定稿制簽核成果失效。
- **只拷兩支 migration、entity 重寫**——否決：entity 是資料形狀契約第三件，drift 閘兩側須同源；重寫 15 檔與 migration 逐欄對賬＝重做 rev5 已驗證工作。
- **版級 MAJOR 2.0.0**——否決（user 2026-09-04）：規則方向不變；每加一檔例外即 MAJOR 會使版號失去「方向性反轉」訊號。
- **註解「逐行零同文」機器判準**——否決（user 2026-09-04 clarify）：175 行全數改寫零收益；改採 RULES 名詞段「隨遷工具」的四型失效引用語意判準，GT-05 機器兜底。

## 決定

1. **憲法 §I.5 例外清單加第②項**（原文＝憲法 §I.5「例外」句）：資料形狀契約三件整檔拷貝——基線結構 migration（`m0001_baseline_schema.rs`、承 `rev5:m001`）、基線 seed migration（`m0002_baseline_seeds.rs`、承 `rev5:m002`）、基線 entity 15 檔——射程鎖 rev5 rust-api 凍結 SHA `92919b9` 之版本；`m0003` 起 delta migration 與一切業務碼不在此例外。
2. **四條件**（例外的成立要件，缺一即回到 §I.5 原則）：
   - ①**逐位元自證**：程式內容去註解後 diff 全等。命令形（兩邊各自）：刪除「首個非空白字元為 `//` 的整行」（含 `///`／`//!`；rev5 三件零行內尾註解）→ 去行尾空白 → 去空行 → 逐檔 `diff`，期望零輸出。實跑結果**不回灌本 ADR**（accepted 後不可變）：落在對應 commit 訊息與本刀 `feature_close` 事件。
   - ②**註解依語意判準重寫**：四型失效引用（無前綴前代編號、rev5 語境事實、章節號指到 rev6 不存在的節、repo 外權威）必改——帶 `rev5:`／`rev4:` 前綴或改指 rev6 去處；通用註解可與 rev5 同文；判定＝review 逐檔改寫清單＋GT-05 掃 tools/ 與子庫 pin 樹兜底。
   - ③**防回歸審查**：逐檔核無 rev6 已推翻行為；entity 終態版之後刀差異逐項列出、屬形狀外者去除並記錄（實核唯一差異＝`sys_user_role` 兩條真 DB FK 關聯宣告、形狀派生、保留；清單記 ADR-00010）。
   - ④**seed 固定值＝定稿字面、非機密**（三帳共用 PHC 常數、`created_at` 定稿時戳；承 `rev5:ADR 0003` 立場）：機密掃描命中才依 `.gitleaks.toml` 紀律逐條 allowlist＋雙向突變實證、絕不 `--no-verify`。
3. **檔名依 ADR-00008 四碼**；「逐位元承襲」口徑＝內容逐位元、檔名依 ADR-00008；`seaql_migrations` 記錄之遷移名隨檔名改、該表 COPY 段依閘契約本就剝除、不影響 fixtures 雙源互證。
4. **版級 MINOR 1.0.0→1.1.0**，依據＝類比 §V.3「軌道授權邊界擴展」（規則方向不變、只擴例外）；同一 Amendment 於 §V.3 MINOR 款補「§I 例外清單擴展」釋義，使日後同型案不再解讀。
5. **時點**：本 ADR 與憲法段更新同一獨立 commit（§V.2 步 4），早於 `/speckit-plan` 之 §IV 第 5 題；任何拷貝碼落地前生效。

## 後果

- `/speckit-plan` §IV 第 5 題答「是、屬 §I.5 例外清單②（資料形狀契約三件）」；防回歸條款照常適用。
- 例外不影響 §I.5 其餘四款（讀允許、拷貝禁止、註解重寫、防回歸）對射程外一切碼的約束；日後任何第 18 檔要拷＝新 Amendment。
- 自證與審查的 as-built 結果歸 commit 訊息與收刀事件（CLAUDE.md §4「as-built 不回灌 ADR」）；schema 基線與閘契約另立 ADR-00010。
- RULES 名詞段「隨遷工具」的語意判準自此同時涵蓋資料形狀三件（判準單一家、不另立）。

## 翻案觸發器

- rev6 拍板推翻任一資料形狀（表集、變體歸屬、欄）→ 新 ADR `supersedes: [ADR-00009]`，該件回到 §I.5 原則（重寫）並走基線翻案。
- 逐位元自證在實作期無法成立（rev5 原檔含無法保留之程式面前代耦合）→ 停手、新 ADR 重議射程，不得以「部分逐位元」施工。
