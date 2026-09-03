---
id: "ADR-00005"
title: 三件生成索引（ARCHITECTURE.md、LESSONS.md 例外註冊、RAD-AI-MAP）與 LL next-id 自檔集推導——索引不再是人寫的家、永不回收靠 GT-05 單調腿
date: 2026-09-03
status: accepted
supersedes: []
superseded_by: []
provenance: "啟動書 §3.1 例外註冊、§3.6 索引為派生物、§3.3 對照總表由 generate 產；user 拍板 2026-09-03（波 2 brainstorm Q1；grill Q3／Q4）"
tags: [governance, generated, lessons]
---

## 背景

- 啟動書 §3.1 把兩個路徑沿革需保留的索引檔（`docs/arc42/ARCHITECTURE.md`、`docs/ops/LESSONS.md`）定為**例外註冊**的機器生成物：登記於 GENERATED_FILES、檔頭 Generated 標記、GT-01 掃描面納入、重算冪等；§3.6 進一步說 LESSONS 索引是派生物、rev5:Lint26「索引↔檔雙向對賬」退場。
- 波 1 落地的 GT-05 卻讀 `docs/ops/LESSONS.md` 檔頭 `<!-- next: LL-NNNNN -->` 來守「配號取 next 後 bump、永不回收」（RL-0050）。索引若是機器產，這行 next-id 就沒有人寫的家——兩者互撞，波 2 建帳本前必須定案。
- 啟動書 §3.3 的 RAD-AI 項目對照總表是 DoD A1 的驗收清單（「每一驗收列的檔或子節存在且非佔位」），但 §3.2 只說「由 generate 自 frontmatter 產出」、未定落點與欄。

## 決策驅動因子

- 每個事實只有一個家（RL-0049）：索引與 next-id 若各有人寫的家，就多一條雙向對賬腿。
- 既有閘已守到哪就不再加腿：GT-05 已有「現 next ＜ HEAD next 即紅」的單調腿；GT-01 已守生成物零漂移。
- DoD A1 需要機器面：「非佔位」不能只靠 GT-10 到期紅，要有進度表。

## 考慮過的替代案

1. **索引改回人寫、next-id 人管**（承 rev5 形）：推翻 §3.6，每加一條教訓手改索引一列＋手改 next，索引↔檔雙向對賬回到 GT-08——棄。
2. **索引生成、next-id 另立人寫小檔**（例如 `docs/ops/LESSONS/NEXT-ID.md` 一行）：多一個一行檔、配號要記得改它——棄。
3. **索引生成＋GT-08 加「LL 檔禁刪除」腿保永不回收**：user 反問「next-id 是最大號＋1，那跟禁刪有什麼關係」——實查 GT-05 單調腿已擋「刪最大號檔→next 倒退」，禁刪腿多餘——撤回。

## 決定

1. **`docs/ops/LESSONS.md` 全生成**（`references.gen_lessons_index`）：檔頭第二行 `<!-- next: LL-NNNNN -->`，值＝`docs/ops/LESSONS/LL-*.md` 檔集最大號＋1（零檔＝`LL-00001`）；索引列為**表格形**（`| LL-NNNNN | 坑名 | rule_id | promotion_surface | 檔 |`）、刻意不合 `book.RE_ENTRY["LL"]`，使 GT-05 的 LL ids 只來自檔名、零雙計數。人配號流程＝讀索引檔頭 next → 建檔 → `python3 tools/docsync generate`。
2. **永不回收靠既有機制**：刪掉最大號檔再 generate → next 倒退 → GT-05 單調腿 ERROR；不跑 generate → GT-01 漂移 ERROR。不加新腿。
3. **`docs/arc42/ARCHITECTURE.md` 全生成**（`gen_architecture_index`）：輸入＝`docs/arc42/NN-*.md` frontmatter（`section`、`summary`、`rad_ai`）與 H1；欄＝節｜檔｜摘要｜掛載 E｜流程層檔（`docs/process/` 中 `rad_ai` 同值者、join 推導，不設 `process:` 鍵）。標題唯一家＝H1、摘要唯一家＝frontmatter。
4. **RAD-AI 對照總表落 `docs/generated/RAD-AI-MAP.md`**（`gen_rad_ai_map`）：欄＝RAD-AI 項目｜系統層檔｜系統層子節｜流程層檔｜流程層子節｜採用階段；子節欄＝`已填實/N`（`###` 標題 ∈ `rad_ai_map` 值且子節正文零 `TODO(波 k)`）、系統層含「目前無 AI 元件」句即「目前無」。
5. **GT-10 加第八腿**：有 `rad_ai_map` 的檔，每個 map 值必須是同檔某 `###` 標題字面（反向不要求、多鍵同值合法）；缺＝ERROR。此腿是決定 4 計數的前提，不加閘、不加規則（仍屬 RL-0035 形制閘）。
6. GENERATED_FILES 名冊 7→10；三件皆 `GENERATED_HEADER` 起頭、只依賴 tracked 檔（ARCHITECTURE.md／RAD-AI-MAP）或 tracked ∪ 工作樹檔名（LESSONS.md，與 GT-05 同口徑）。

## 後果

- 新建活書檔一律**先 `git add` 再 `generate`**，否則索引缺列、pre-commit 才發現漂移。
- `docs/arc42/ARCHITECTURE.md` 屬活書家族：其內容（含 frontmatter `summary` 的人寫字面）受 GT-06 時態腿與 GT-10 佔位腿掃描。
- Day-1 豁免 `GT-05.ledgers-absent`、`GT-06.book-absent` 隨本 ADR 落地解除；`GT-08.lessons-absent` 留到首條 LL 檔。
- RULES 不改（RL-0050「取檔頭 next 後 bump」仍為真：取自生成索引、bump 由 generate 完成）。

## 翻案觸發器

- LL 檔出現合法的刪除需求（教訓不再 append-only）→ 重評「最大號＋1」與單調腿的組合是否仍足以保證永不回收。
- 索引需要人寫欄位（例如人工排序、分組）→ 重評索引是否仍為純派生物。
