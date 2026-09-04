# Data Model — 002-system-settings（Phase 1）

轉錄自 spec（clarify 2026-09-05 Q1～Q5 已定案）＋brainstorm §3 §5 §6＋research R4／R8；本檔凍結後＝本刀資料面與 wire 型唯一權威（spec 敘事讓位）。
零 migration：`system_settings` 表＋16 鍵 seed 已隨 001 基線在庫（現況真表＝`docs/generated/reference/schema.md` 之 system_settings 節；定稿權威＝`docs/ops/reference-src/schema-definition.md` §2）。
rev5 對應＝`rev5:002-system-settings` data-model（沿用形、rev6 座標與 clarify 差異逐處標 ★）。

## §1 wire DTO — SettingItem（讀端列型）

camelCase 序列化；審計欄不上 wire（Model→DTO 映射僅取四欄）。

| wire 欄 | 型 | 語意 |
|---|---|---|
| settingKey | string | PK、不可改 |
| settingValue | string | 值（字串載體；number 型亦字串承載、已是 canonical 形） |
| settingType | string | 庫中 `setting_type` 字面（`"number"`／`"enum:on,off"`；驅動前端 render） |
| description | string?（缺席＝無） | 用途說明；庫中 NULL 不上 wire（★clarify Q2：缺席、不回 null） |

讀端回傳形＝`Res<Vec<SettingItem>>`（非分頁、`ORDER BY setting_key` 升冪穩定序、`deleted_at IS NULL` filter）。
★讀端 Model→DTO 映射帶兩道守衛、任一觸發＝Internal `5000` 整支 fail-loud、不跳列：①型別認識集守衛（`setting_type` 非 `number`／`enum:` 前綴）
②registry 一致性守衛（★clarify Q1：已知鍵之庫中 `setting_type` ≠ registry 宣告型別字面）。

## §2 wire DTO — UpdateSystemSettingReq（寫端請求）

camelCase；三態欄依 RFC 7386 語意（§8 條文）。

| wire 欄 | 型 | 三態語意 |
|---|---|---|
| settingKey | string（必） | 定位鍵；未知鍵→`2222` notFound；欄缺席／型別非 string→`2222` invalidValue（handler 層判） |
| settingValue | string（必） | 新值；經 registry 驗證＋正規化；JSON null＝顯式清空 NOT NULL 欄→`2222` invalidValue；欄缺席→`2222` invalidValue |
| description | 三態（缺席／null／值） | 缺席＝不動；null＝清空落 NULL；值＝設值（含空字串 ""＝設值；不經 registry；欄無長度上限） |

- 三態承載型（實作慣例）：`Option<Option<String>>`＋`#[serde(default)]`＋自訂 `deserialize_with`（rev5:L-009：預設 Deserialize 把 null 也落外層 None、三態塌兩態）
  ——外層 None＝缺席、Some(None)＝顯式清空、Some(Some(v))＝設值；settingValue 亦以三態型承載以偵測顯式 null（Some(None)→`2222`）。
- 必填欄以寬鬆形承載、缺席由 handler 層判 `2222`——不由 serde 必填拒收；JSON 反序列化失敗以自訂 rejection 落 `2222` 信封 HTTP 200
  （框架預設 400／422 裸 body＝違憲法 §I.3、絕不放行）。
- 成功回傳＝`Res<()>`（`{data:null, code:"0000", msg:"common.success"}`；★clarify Q3：不回更新後物件、驗收以回讀端比對）。

## §3 設定值 registry（16 鍵逐鍵凍結；值域承 rev5 定稿原值——research R4）

**number 型（10 鍵；含界 [min,max]；canonical＝`trim`→`parse::<i64>`→界內→`to_string()`）**

| setting_key | min | max | 界語意備註 |
|---|---|---|---|
| ip_captcha_after | 1 | 100 | 來源桶軟區門檻 |
| ip_max_fails | 1 | 100 | 來源桶硬鎖門檻 |
| ip_window_minutes | 1 | 1440 | 分鐘；上界一日 |
| login_throttle_captcha_after | 1 | 100 | 登入軟區門檻 |
| login_throttle_max_fails | 1 | 100 | 登入鎖定門檻 |
| login_throttle_window_minutes | 1 | 1440 | 分鐘；上界一日 |
| password_change_min_interval | 0 | 86400 | 秒；下界 0＝停用語意明確放行 |
| password_max_length | 1 | 256 | — |
| password_min_length | 1 | 128 | — |
| session_idle_timeout | 5 | 1440 | 分鐘 |

**enum:on,off 型（6 鍵；值域自含於 setting_type 字面；canonical＝原值、大小寫敏感）**：
password_forbid_username／password_require_digit／password_require_lowercase／password_require_special／password_require_uppercase／single_session_default。

**registry 行為不變式**：
- 每鍵必有顯式宣告（型別＋值域）；宣告集外＝未知鍵→`2222` notFound（含 number 鍵不在範圍表＝fail-loud 拒）。
- registry 為 rust 端 const 純宣告、不讀庫；★不驗跨鍵關係（clarify 前 brainstorm Q6：password_min／max、captcha_after／max_fails 兩組矛盾可各自合法落庫、留消費側刀）。
- ★型別一致性（clarify Q1）：讀寫路徑觸及已知鍵時，庫中 `setting_type` 字面 MUST 等於 registry 宣告字面、否則 `5000`；庫中字面不在認識集亦 `5000`。
- 「含軟刪防禦態」之判定落點＝facade 查詢層（find_by_key／find_all 皆帶 `deleted_at IS NULL`、軟刪列視同 miss→寫端 notFound）。
- 驗證失敗一律零寫入（原值保留）；同值更新照寫審計欄（不做 no-op 短路）。
- 16 鍵集合本刀凍結（無新增／刪除鍵端點）。

## §4 route 註冊表（ROUTES const；RouteDef 六欄承 rev5 形——第六欄 handler＝`fn() -> MethodRouter<AppState>` builder、表略）

| path | method | case_key | envelope_exception | protection |
|---|---|---|---|---|
| /health | GET | health | true（plain text "ok"） | Public |
| /metrics | GET | metrics | true（Prometheus exposition） | Public |
| /systemManage/getSystemSettings | GET | get-system-settings | false | Policy |
| /systemManage/updateSystemSetting | POST | update-system-setting | false | Policy |

- Protection 三態承 rev5（Public／Authed／Policy）；本刀無 Authed 成員（型別保留、003 啟用）。
- Policy＝enforce_mw（dev 驗證器→Identity）＋require_policy(path, method)——casbin act＝method 字面、與 seed 政策列 66／67 對齊；路徑不帶 `/api` 前綴（front-nginx strip）。
- ★fallback 同形（clarify Q4）：未註冊路徑**與**已註冊路徑但方法不符，皆由 router 統一 fallback 渲成 HTTP 404＋`{data:null, code:"4040", msg:"system.notFound"}`；
  框架預設 405 MUST NOT 露出（axum 之 `method_not_allowed_fallback` 掛同一函式）。
- 覆蓋閘：contract case registry 與本表 case_key 雙向比對（缺 case 紅指名、殭屍 case 紅指名）；fallback 兩案為獨立測試、不進 registry。
- ★機器契約（rev6 新、docsync routes 生成器解析源——契約全文＝contracts/code-gates.md §4）：`pub const ROUTES: &[RouteDef] = &[` 精確開頭、block 頂層只認 `RouteDef {` 與 `];`、
  每欄一行 `key: value,`、handler＝`handler: || get|post|delete(...),` 形、method 限 `Method::Get|Post|Delete`、protection 限 `Protection::Public|Authed|Policy`、
  envelope_exception 限 `true|false`——任一偏離＝generate 重算失敗（fail-loud、GT-01 連帶紅）。

## §5 AppState 與 dev-only 測試態身分

- `AppState`（`#[derive(Clone)]`）＝`db: DatabaseConnection`＋`enforcer: Arc<tokio::sync::RwLock<Enforcer>>`——恰兩欄。
- **測試態身分（dev-only）查表**（`#[cfg(debug_assertions)]`、research R8；沿 rev5 三 token）：

  | token 字面 | uid | 對應 seed 帳號 |
  |---|---|---|
  | dev-super | 1 | Super（R_SUPER） |
  | dev-admin | 2 | Admin（R_ADMIN） |
  | dev-user | 3 | User（R_USER_COMMON） |

  roles 不入表——授權判定恆走 require_policy 之 DB-fresh `roles_of_user`（真政策；只認 `deleted_at IS NULL` 且 `status=1` 的角色）。
  標頭承載形（權威定義）：`Authorization: Bearer <token>`——剝除 `Bearer ` 前綴、trim 後查表；標頭缺席／非 Bearer 形（含裸 token）／token 不在表→`8888`。
  release 建置＝驗證器缺席、一切 Policy 請求 `8888`（fail-closed）；獨立檔 `auth/dev_identity.rs`、003 整檔汰換。
- 注入形：驗證器產 `Identity { uid: i64, user_name: String }`；audit `updated_by` 消費 uid；003 換 JWT 驗章時本型介面不變。

## §6 錯誤映射（AppError 變體集＝本刀六碼；單一來源住 error.rs）

| 變體 | 碼 | msg key | HTTP |
|---|---|---|---|
| Success | 0000 | common.success | 200 |
| Biz(key) | 2222 | 構造點顯式給定（biz.systemSettings.*） | 200 |
| NotFound | 4040 | system.notFound | 404（router fallback 專用：未註冊路徑＋方法不符） |
| PermissionDenied | 5003 | system.forbidden | 403 |
| Internal | 5000 | system.internal | 200 |
| Logout | 8888 | auth.session.reLogin | 200 |

- 13 碼常量 mod 全列（憲法 §I.3 矩陣完整）；1000／3333／7777＋4 保留碼皆無變體＝構造層不可發出（contract 斷言消費此保證）。
- ★**msg key 名冊**（clarify 前 brainstorm Q4、spec FR-020；後端側閉環權威）＝恰七鍵：`common.success`／`biz.systemSettings.invalidValue`／`biz.systemSettings.notFound`／
  `system.notFound`／`system.forbidden`／`system.internal`／`auth.session.reLogin`；名冊住 error.rs 單一常數陣列，contract test 雙向斷言（每條 route 每個錯誤路徑實發 msg ∈ 名冊；名冊每鍵 ≥1 發出點）。
  跨端閘（名冊 ⊆ 前端字典）不入本刀、BACKLOG 承載。

## §7 資料面拍板轉錄（零 DDL）

- ①無 DB FK 之邏輯關聯**不建** sea-orm Relation（需要即手寫 join——單一關聯真相＝DB FK）；`sys_user_role` 兩條真 FK 之 Relation＋Related 已隨 001 在、本刀零改。
- ②ActiveModelBehavior **不承載**六審計欄自動化（審計欄由 facade 顯式成對寫）；★機器錨＝`server/tests/entity_behavior_lint.rs`（BL-00008；契約＝contracts/code-gates.md §5）。
- 寫端落庫形：`update_by_key(key, canonical_value, description_tristate, operator_uid, now)`——`setting_value` Set canonical、`updated_at`／`updated_by` ★成對 Set、description 依三態 Set 或不動；查無或軟刪→`Ok(None)`（零寫入、handler 映 2222 notFound）。

## §8 三態約定（envelope 級定形條文；全 repo 後續寫端消費）

部分更新請求之每一可選欄：**欄位缺席＝不動；欄位值 JSON null＝顯式清空（NOT NULL 欄→`2222` 拒收、nullable 欄→落 NULL）；欄位有值＝設值（空字串亦為設值）**。
解析層以三態型別區分「未出現」與「null」（serde `Option<Option<T>>`＋default＋自訂 deserialize_with）。逐域欄級三態表由各域刀自定；本約定僅鎖 envelope 級語意；
射程＝部分更新請求 body（create 請求與 query 參數不在射程）。★本條文隨 U7 轉錄為 ADR（承 rev5:ADR 0023；憲法 §V.1 權威鏈落點）——accepted 後以該 ADR 為權威、本節轉指引。
