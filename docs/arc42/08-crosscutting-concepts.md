---
section: 8
summary: 資料／API／授權慣例、fork-delta 軌道；E4 負責任 AI 概念
rad_ai: [E4]
rad_ai_stage: 3
rev5_blueprint:
  §8 橫切概念: 承襲（四子節形制）
  fork-delta 接線現況（base-web）: 承襲（指針形：規則面承 rev5 FORK-DELTA-WIRING、接線 as-built 隨 base-web 各刀重生）
  資料慣例: 承襲（archetype 四變體與成對條款在憲法 §I.6；三閘／演進帳／歸屬帳＝ADR-00010；memo 欄與 ORM 紀律見 §8.1）
  API 慣例: 承襲（信封／碼表／i64 守衛＝憲法 §I.3；契約機器化與部分更新三態＝§8.2、ADR-00015；msg 名冊後端側閉環＝ADR-00017）
  授權慣例: 承襲（判定單點／DB-fresh＝憲法 §I.2；拒絕語意與 no-escalation 掛點＝§8.3、ADR-00014；no-escalation 本體與三維授權治理＝憲法 §I.7 島 G／I 承襲指針）
---
# §8 橫切概念

## 8.1 資料慣例

紀律上位＝憲法 §I.6（業務表審計欄四變體：A 業務全六欄／B append-only／C join·狀態機·衛星／D 治理；成對條款）。schema 基線＝`rust-api/migration/src/m0001_baseline_schema.rs`（結構）＋`m0002_baseline_seeds.rs`（seed、完全決定性；程式內容逐位元承襲 rev5 終態、ADR-00009），對 pristine 重放兩支即得全庫；漂移三閘＝`tools/schema-gate.py`（gate1 結構／gate2 欄序＋seed／audit archetype）、entity 漂移閘＝`tools/entity-drift-gate.py`（pre-commit 條件實跑：rust-api pin bump 或 schema 快照 staged 時）、受管演進帳＝`docs/ops/reference-src/schema-evolution.json`、歸屬帳＝`docs/ops/reference-src/archetype-map.json`——四者的左源、判準與登記紀律＝ADR-00010（承 rev5:ADR 0006、rev5:ADR 0007 的形）；表清單與欄型正典的家＝`docs/generated/reference/schema.md`（`python3 tools/docsync refresh` 照相、generate 產）。

memo 欄家族（`user_memo`／`role_memo`／`menu_memo`／`wbip_memo` 與 `role_desc` 的分工）語意權威＝`docs/ops/reference-src/schema-definition.md` §5、UI 兌現隨對應 UI 刀。

ORM 關聯與行為層紀律：關聯宣告只映真 DB FK（無 DB FK 之邏輯關聯不建 Relation、需要即手寫 join）、`ActiveModelBehavior` 恆空（審計欄由 model/facade 顯式成對寫、憲法 §I.6 成對條款）——`rust-api/entity/` 已依此宣告，機器錨＝`rust-api/server/tests/entity_behavior_lint.rs`（承 rev5 同名形；等式形站點數＝帶 DeriveEntityModel 檔數、空體判定、合成正例必紅）。

## 8.2 API 慣例

紀律上位＝憲法 §I.3（`Res` 三欄信封、13 碼矩陣整組凍結、id 序列化逐欄位忠實 typings、2^53 fail-loud 守衛）。契約機器化四件：①base-web typings（抽取面＝`tools/wire-schema.py` 之 `TYPINGS_GLOB`，涵蓋 `src/typings/api/` 與 `src/typings/common.d.ts`）＝wire 權威，`tools/wire-schema.py extract` 抽 draft-07 JSON Schema 快照至 `rust-api/server/tests/fixtures/wire-schema.json`（`check` 重抽 byte 比對＝碼面閘、名冊＝RUNBOOK §12 碼面閘表）；②`rust-api/server/tests/wire_schema.rs` 以快照裁判後端 DTO 序列化輸出與三態反序列化落點；③`rust-api/server/tests/contract.rs`＝case registry×`ROUTES` 雙向覆蓋閘（缺 case 指名 route、殭屍 case 指名 case_key）＋fallback 兩案（未註冊路徑／方法不符皆 HTTP 404＋4040、標頭鍵集全等零存在性洩漏）；④route 真表 `docs/generated/reference/routes.md` 由 generate 自 `ROUTES` 重算。

13 碼矩陣整組凍結的機器承載住 `rust-api/server/src/error.rs`——`code` 常量 mod 與同檔 `#[cfg(test)]` 之 table-driven 矩陣逐列同序同值斷言（碼×msg key×HTTP 對映、表長恰 13）；保留碼零發出另有雙錨＝`AppError` 無對應變體之全變體窮舉見證（cargo 型別層）＋同一矩陣斷言，`tests/contract.rs` 不重寫第三份。

部分更新三態（欄缺席＝不動／JSON null＝清空／有值＝設值）＝ADR-00015，後端承載＝`Option<Option<String>>`＋`tristate` 反序列化、body 取用失敗一律 2222 信封。

msg 名冊後端側閉環＝`rust-api/server/src/error.rs` 之 `MSG_KEYS` 單一常數陣列＋contract 雙向斷言（實發 ⊆ 名冊、名冊每鍵 ≥1 發出點）；跨端閘（名冊 ⊆ 前端 i18n 字典）不在本面、去處＝ADR-00017（延首個接 i18n 的前端刀、觸發由 BACKLOG 承載）。

## 8.3 授權慣例

紀律上位＝憲法 §I.2（menu 權限 casbin enforce、DB-first 寫入、寫後全量重載）。判定單點＝`rust-api/server/src/auth/enforce.rs` 之 `enforce_role_path_method`（全服務唯一判定進入點；每次判定記 `casbin_enforce_total{decision}`、取值恰三 allow／deny／error）；每請求 DB-fresh＝`require_policy` 經 facade `roles_of_user` 現查角色（兩道濾網＝未軟刪且 `status = 1`；不快取、不採信 token 帶的角色）；驗證器 `enforce_mw`＝真驗章單一段碼（debug／release 同形、`from_fn_with_state` 掛法）：`verify_access` 三分碼（僅 access `exp` 過期→3333；標頭缺席・非 Bearer・簽章不符→8888；被踢→7777）→denylist 四級降級（redis 命中依 reason 二向〔kicked→7777、其餘→8888〕／nil 放行／redis `Err` 退 PG `sys_token::has_active_in_chain` fail-closed／PG 亦 `Err` 視為無 active、絕不盲放）→放行後 best-effort 推進 `last_activity`、注入 `Identity{uid, user_name: ""}`（帳號名以 uid 現查＝已知態）；降級鏈觀測＝`denylist_hit_total{source}` 二值（redis／pg）。拒絕語意四條＝ADR-00014：無權＝5003＋HTTP 403＋msg 純 key `system.forbidden`；未認證＝8888（HTTP 200 信封、`auth.session.reLogin`）；政策求值失敗＝5000（先落 log、不偽裝成無權）；不揭露政策明細與角色集。no-escalation 掛點＝`no_escalation_check`（空掛點；簽章預留 async 與 DB 句柄、`enforce_role_path_method` 為唯一呼叫點；ADR-00014）；no-escalation 本體、三維授權治理與回收桶＝憲法 §I.7 島 G／I 承襲指針。

## 8.4 fork-delta 軌道

紀律上位＝憲法 §III（token `rev6-inline`；修改型帶 `原行:`、新增型圈界）；規則面承 rev5 `docs/arc42/FORK-DELTA-WIRING.md`、接線 as-built 隨 base-web 各刀重生；機器守＝`tools/fork-delta-lint.py`（修改型原行／新增型圈界含新檔檔頭標記、軌道授權判定、生成檔紀律；碼面閘、名冊＝RUNBOOK §12 碼面閘表、pre-commit fork-delta 段實跑）。程式碼 fork-delta as-built＝base-web 四支新增型新檔：`src/typings/api/rev6-settings.d.ts` 與 `src/typings/api/rev6-auth.d.ts`（§III.1 BASE-WEB-ADAPT 軌道）、`src/service/api/rev6-settings.ts` 與 `src/service/api/rev6-auth.ts`（§III.1 BASE-WEB-WRAPPER 軌道、不入 barrel）＋inline 修改型 11 處（`.env` 2／`.env.test` 1／`.env.prod` 1＝BASE-WEB-ADAPT 軌道、`src/store/modules/route/index.ts` 1＝BASE-WEB-AUTH-WIRING(a) 軌道、`src/layouts/modules/global-header/components/user-avatar.vue` 1＝§III.2 BASE-WEB-LOGOUT-UX-WIRING(i) 軌道、`src/store/modules/auth/index.ts` 3 與 `src/views/_builtin/login/modules/pwd-login.vue` 2＝§III.2 BASE-WEB-LOGIN-CAPTCHA-WIRING(i) 軌道；後三檔另新增型圈界 2／5／4 處）；fork patch set 另含檔頭標記的分支來源紀錄檔 `x_fork.branch-origin.md`（非程式邏輯）。新檔檔頭標記定形＝`[rev6-inline <軌道名>+ <刀名>]`（軌道名後緊接 `+` 尾綴＝新增型），由 `tools/fork-delta-lint.py` 兩道判定強制（`+` 尾綴定形×所稱軌道與檔路徑相符）。

## 8.5 E4 負責任 AI 概念

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E4 負責任代理](../process/P-E4-responsible-agent.md)。
