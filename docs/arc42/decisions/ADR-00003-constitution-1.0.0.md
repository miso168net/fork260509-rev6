---
id: "ADR-00003"
title: 憲法 1.0.0 定版——自 rev5 v1.10.0 依啟動書 §3.8 逐條表搬入；§I.7／§III.2 只留骨架＋承襲指針、§I.8 新增；spec-kit 產物同批入版控
date: 2026-09-03
status: accepted
supersedes: []
superseded_by: []
provenance: "啟動書 §3.8 逐條表（user 拍板 2026-09-03）＋user 親審 diff `tmp/constitution-1.0.0.diff`（2026-09-03）；形制承 rev5:ADR 0001（創世採用）"
tags: [governance, constitution]
rev5_id: "rev5:ADR 0001"
---

## 背景

- 啟動書 §3.8 拍板憲法射程：系統事實條款承襲、工作流收為方向性條款、§I.5 世代 bump、§I.7 十島隨刀進場、
  §V.1 權威鏈納 RULES、新增 AI 代理方向性條款；文件治理**程序**條款移 RULES.md。
- 藍本＝rev5 constitution v1.10.0（rev5 凍結 SHA `7eab28a`、唯讀直讀；314 行、十座行為島與五條 ★ 軌道十七用途全展開）。
  rev6 工作樹的 `.specify/memory/constitution.md` 在本 ADR 前仍是 spec-kit 1.0.3 空模板（50 行）。
- 波 1 治理計畫（`docs/brainstorms/000-w1-governance-tooling.md`）grill 時 user 拍板兩點：
  ①§I.7「已入憲行為島」與 §III.2 ★ 軌道表**只搬骨架＋承襲指針**，島體與軌道隨刀以 MINOR Amendment 重新進場；
  ②spec-kit 產物（`.claude/skills/`、`.specify/`）與憲法 1.0.0 同批入版控（此前保持未追蹤）。
- 憲法屬**現在式面**：GT-05 裸編號、GT-06 時態、GT-10 形制皆掃本檔；引 rev5 一律 `rev5:` 前綴，提及形用反引號或「」。

## 決定

**rev6 憲法 1.0.0 依下表定版**（逐條可核；diff 對照＝`tmp/constitution-1.0.0.diff`、user 親審 2026-09-03）：

| 節 | 處置 |
|---|---|
| 標頭 | 世代改字；活書改指活書家族四目錄；創世紀錄改指本 ADR；末行加「程序條款住 RULES.md」 |
| §I.1／§I.2／§I.3／§I.6 | 承襲；分支名 `rev6-admin-base-web`、基線 SHA `8be6f9ba`（D14）、token `rev6-inline`；rev5 ADR 引用加 `rev5:` 前綴（§I.2 之 0005）；rev4 出處保留 `rev4:`（§I.6 之 0085） |
| §I.4 | 收為方向性四句（路徑固定／merge 回 `rev6-admin-root`／簿記三步／細節＝RULES＋CLAUDE.md §2） |
| §I.5 | 世代 bump：源倉 main `32c5254` 起全新寫；前代＝rev5（凍結 SHA 由 bootstrap 斷言）、rev4 溯源；註解出處 `rev5:` 前綴；例外兩 crate 承襲 |
| §I.7 | 進場規則承襲；已入憲＝空；承襲指針以**表**列十島 A～J 與 rev5 入憲載體 |
| §I.8 | 新增：人審＋機器閘雙放行、review 只讀、push／merge 需當次明確同意；反轉＝MAJOR |
| §II | 三筆承襲；`tmp/rev5-handoff/rev5-adr-digest.md` 逐筆核無翻案 |
| §III | fork-delta 紀律承襲（token、基線 SHA 句）；生成檔紀律引 `rev5:ADR 0052`、機器承載改指隨刀進場的碼面閘 |
| §III.1 | 三軌道承襲；wrapper 前綴 `rev6-` |
| §III.2 | 機制骨架＋補完判準＋表外三項宣告＋空表頭；承襲指針列 rev5 五條 ★ 軌道十七用途＋§III.1 三軌道＝八條 |
| §IV | 九題承襲；第 2 題 token、第 5 題前代改引、第 9 題候選來源改指 §I.7 承襲指針；註記補 §I.8 為方向性承載 |
| §V | 權威鏈納 RULES.md（constitution ＞ ADR ＞ RULES ＞ 活書家族 ＞ generated）；§V.2 第 4 步 `python3 tools/docsync generate`；§V.3 MAJOR 款納 §I.8；Version 1.0.0｜Ratified 2026-09-03 |

**改寫期的四處事實校正**（計畫逐節清單與藍本落差、施工時實查後定）：
1. 島 G 的 rev5 入憲載體＝`rev5:ADR 0053`（rev5 v1.8.0 條目）；`rev5:ADR 0054` 是 G6 結構性封死、`rev5:ADR 0055` 是復原五腿——計畫表原寫 0054，承襲指針表三號並列。
2. §I.6 變體 B 的「retention 非竄改」權威釋義在 rev5 是 §I.7 島 J3 交叉指針；rev6 島 J 未進場、指針會懸空——改寫為「隨稽核域行為島進場時回填、rev5 位置＝島 J3」。
3. rev5 承襲指針句引的「啟動書 §5 K1 承襲清單」在 rev6 啟動書不存在——改指 rev5 憲法凍結版本身（`7eab28a`）。
4. §II #2「auth route mode＝dynamic」拍板不變，但 rev6 base-web 基線 `.env` 現值仍為 upstream 的 `static`——as-built 落後屬 ADAPT 軌道首刀工作、不入憲法字面。

**grill 三題 user 親決（2026-09-03、`/grill-with-docs` 對本檔）**：
1. §I.4 保留「階段不可跳、不可反序」並錨定「刀」＝spec-kit feature（`NNN-<name>` 分支）；輕量軌不進 spec-kit、憲法不寫它（維護批不是刀，§I.4 自然不涉）。
2. §I.8「人審」釋義＝merge 回 default branch 前 user 當次明確同意＋拍板級項親決，逐 diff 親讀非必要條件；機器閘限「適用於該改動者」（純文件改動無容器測試）。
3. §III.2 表外宣告 2 改原則句、去 rev4／rev5 軌道名（devproxy 由 ADAPT 涵蓋、modal 不另開專屬軌道），ADAPT 列的引用仍成立。
另四處精度自改：§I.2「承 rev4 終態」、§I.4 簿記句補 perf 第四步指針、§I.8 第三點去程序句（烤入 prompt 屬 RULES）、§V.1 活書家族標「不含 decisions/」。

**spec-kit 產物入版控**：`.claude/skills/`（15 支 speckit-* SKILL.md）與 `.specify/`（43 檔：templates／scripts／extensions／
integrations／memory）共 58 檔隨本 ADR 同 commit 進 index；`.specify/.gitignore` 自帶 `feature.json` 與
`extensions/*/local-config.yml` 排除、根 `.gitignore` 另排 `.specify/extensions/.cache/`。入版控前 betterleaks 零命中、
無機器路徑字面。

**spec-kit git extension 設定（user 三題親決 2026-09-03、對照 rev5 f889912 拍板）**：
1. `git-config.yml`：`auto_commit.default: true`＋16 個 hook `enabled: true`、訊息留 1.0.3 出廠英文 fixed 形——與 rev5 檔逐位相同
   （rev5 八把刀實發 34 顆 `[Spec Kit]` commit；CLAUDE.md §2「SDD 每步後 commit」由此承載）。
2. `extensions.yml`：16 個 git.commit hook `optional: false`（自動執行、不插問）——比 rev5 多關 `before_clarify` 一處
   （rev5 照 rev4 留 optional；rev6 判 clarify 前若有未收改動直接收進「Save progress before clarification」即可）。
3. `feature.json` 維持 1.0.3 自帶 `.specify/.gitignore` 排除（rev5 0.15.1 追蹤它、每次 specify 都跟著改）。
機制＝`git add .`＋`git commit`（掃進一切未 ignore 改動、含子庫 gitlink pin），過 rev6 pre-commit；沙盒實跑：
`after_specify`→「[Spec Kit] Add specification」、`before_plan`→「Save progress before planning」、無改動→skip rc 0。

## 後果

- 憲法自此為 rev6 凍結權威；改動走 §V.2（ADR draft→user 親決→accepted＋bump），Claude 不主動 amend。
- 十座行為島與五條 ★ 軌道的**條文全文只在 rev5 凍結樹**可讀；每把刀的 brainstorm 以 §I.7／§III.2 承襲指針為輸入、
  逐島／逐用途重新入憲——不得整段回貼。
- §I.6 變體 B 的 J3 指針句、§I.7 空缺位（rev5 之 I6／J2）之處置，隨島 J／島 I 進場 Amendment 一併回填。
- spec-kit 產物屬**第三方面**：豁免 GT-05／GT-06 時態／GT-10；GT-06 連結與 GT-07 機密仍掃（波 1 計畫 Global Constraints）。
  升級 spec-kit＝一顆獨立 commit、diff 只允許工具重算形。
- 本 ADR 為 RULES.md 首版（ADR-00004）之 source 相依：RULES 條目引 `ADR-00003` 者以本檔為權威。
