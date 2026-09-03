---
section: 8
summary: 資料／API／授權慣例、fork-delta 軌道；E4 負責任 AI 概念
rad_ai: [E4]
rad_ai_stage: 3
rev5_blueprint:
  §8 橫切概念: 承襲（四子節形制）
  fork-delta 接線現況（base-web）: 承襲（指針形：規則面承 rev5 FORK-DELTA-WIRING、接線 as-built 隨 base-web 各刀重生）
  資料慣例: 隨刀：schema 基線刀（archetype 四變體與成對條款已入憲法 §I.6、本波留指針）
  API 慣例: 隨刀：wire 地基刀（信封、碼表、i64 守衛已入憲法 §I.3；部分更新三態承 rev5:ADR 0023 隨刀重審）
  授權慣例: 隨刀：授權治理刀（憲法 §I.7 島 G／I；判定單點與 DB-fresh 已入憲法 §I.2、本波留指針）
---
# §8 橫切概念

## 8.1 資料慣例

紀律上位＝憲法 §I.6（業務表審計欄四變體：A 業務全六欄／B append-only／C join·狀態機·衛星／D 治理；成對條款）。schema 基線、漂移三閘、受管演進帳與 archetype 歸屬帳隨 schema 基線刀進場（承 rev5:ADR 0006、rev5:ADR 0007 的形、隨刀重審）；表清單與欄型正典的家＝`docs/generated/reference/schema.md`（隨該刀生成）。

## 8.2 API 慣例

紀律上位＝憲法 §I.3（`Res` 三欄信封、13 碼矩陣整組凍結、id 序列化逐欄位忠實 typings、2^53 fail-loud 守衛）。契約機器化（typings 抽 JSON Schema、coverage gate、碼表 table-driven case）與部分更新三態（欄缺席＝不動／JSON null＝清空／有值＝設值；承 rev5:ADR 0023）隨 wire 地基刀進場、隨刀重審。

## 8.3 授權慣例

紀律上位＝憲法 §I.2（menu 權限 casbin enforce、DB-first 寫入、寫後全量重載）。判定單點與每請求 DB-fresh、拒絕語意（無權＝5003＋HTTP 403、msg 純 i18n key、不揭露政策明細）、no-escalation 包含規則、三維授權治理與回收桶，隨憲法 §I.7 島 G／I 的進場刀重生（承 rev5:ADR 0022、rev5:ADR 0053～0056、rev5:ADR 0063 的形）。

## 8.4 fork-delta 軌道

紀律上位＝憲法 §III（token `rev6-inline`；修改型帶 `原行:`、新增型圈界）；規則面承 rev5 `docs/arc42/FORK-DELTA-WIRING.md`、接線 as-built 隨 base-web 各刀重生；機器守 fork-delta-lint（檔頭判準、生成檔紀律）隨子庫刀進場。程式碼 fork-delta 目前為零；fork patch set 只有檔頭標記的分支來源紀錄檔 `x_fork.branch-origin.md`（非程式邏輯）。

## 8.5 E4 負責任 AI 概念

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E4 負責任代理](../process/P-E4-responsible-agent.md)。
