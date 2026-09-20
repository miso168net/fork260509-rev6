---
id: "ADR-00027"
title: AppState 恰兩欄封條翻案→五欄——加 jwt／cache／captcha_secret；ip_rules／trust_model／mailer 續留域外
date: 2026-09-08
status: superseded
supersedes: []
superseded_by: [ADR-00036]
provenance: "003-auth-session clarify 2026-09-08 Q1（user 親決：A 五欄承 rev5；棄案＝三欄 auth 子結構打包／四欄 captcha 密鑰併 jwt 設定）；spec FR-032、data-model §10；被翻案的拍板住 rust-api/server/src/state.rs 檔頭 doc（002 刀 U1 落地、其 data-model §5 為由）、無 ADR 承載故 supersedes 留空；rev5 同位＝rev5:ADR 0029（兩欄→五欄、後由 rev5:ADR 0041 五→七欄）；主線擬稿即 accepted（tasks T003、user 於 clarify 已拍板）"
tags: [rust-api, state, decision-reversal, auth]
---

## 背景

`rust-api/server/src/state.rs` 檔頭 doc 有一段自稱拍板級的封條：

> ★★恰兩欄是拍板釘死的邊界（data-model §5）：rev5 終態 AppState 之 jwt／cache／captcha_secret／trust_model／ip_rules 諸欄各屬後刀域、一欄都不帶；要開第三欄＝拍板級、不得逕加。機器錨＝本檔測試之窮舉解構（加欄即編譯失敗）。

該封條在 002-system-settings 當時完全正確：那把刀沒有認證、沒有快取、沒有驗證碼，五欄一欄都用不到。但它**只住在碼註裡、沒有 ADR 承載**——這正是它自己要求的「拍板級翻案」找不到可 supersede 對象的原因（rev5 同型、rev5:ADR 0029 亦 supersedes 留空）。

003-auth-session 需要其中三欄：真驗章要 `JwtConfig`（access／refresh 各自秘鑰＋iss／aud）、denylist／grace／idle／節流 L1 要 redis 連線、簽發圖形驗證碼題目要 `captcha_secret`。三者都是 request 路徑上每次都要用、且 boot 期一次建好即不可變的資源。

## 決策驅動因子

- 繞過 `AppState` 另建全域單例只會多一套生命週期管理；axum `State` 每 request clone 一份、五欄複製的仍全是句柄（`JwtConfig` 與 `captcha_secret` 為小型不可變值、`SessionCache`＝`redis::aio::ConnectionManager` 內部 `Arc`），clone 得起的理由與兩欄時代相同。
- `cache` 的缺席語意必須在型別上可見：測試要能構造「快取自始缺席」的降級面（憲法 §I.7 島 C 四級降級鏈的天然測試面），production 卻絕不容許靜默缺席——否則島 C 的 fail-closed 方向會被開機期一個軟失敗整條旁路。
- 封條要求的正是「開欄須拍板」；本 ADR 即是該拍板，封條不因此失效、只收窄射程。
- rev5 已驗證同一欄集（rev5:ADR 0029），承襲指針以 rev5 為藍本、rev6 座標重定。

## 考慮過的替代案

1. **三欄：`auth: AuthConfig{jwt, cache, captcha_secret}` 子結構打包**——取用多一層、`Option` 語意藏進子結構、錨測窮舉失去欄級精度；棄（clarify Q1 棄案）。
2. **四欄：captcha 密鑰併入 `JwtConfig`**——captcha 密鑰是第三把獨立秘鑰（`APP_CAPTCHA_SECRET`）、與 jwt 兩把語意混型，且與 RUNBOOK §7 機密輪替表分列不對齊；棄（clarify Q1 棄案）。
3. **全域單例（`OnceLock`）繞過 `AppState`**——多一套生命週期、測試無法逐案注入；棄。

## 決定

1. **`AppState` 兩欄 → 五欄**（data-model §10 字面）：

   ```text
   AppState { db: DatabaseConnection, enforcer: Arc<RwLock<Enforcer>>, jwt: JwtConfig, cache: Option<SessionCache>, captcha_secret: String }
   JwtConfig { access_secret: String, refresh_secret: String, iss: String, aud: String }
   SessionCache = redis::aio::ConnectionManager
   ```

2. **`cache: Option<SessionCache>` 的語意不是「可有可無」**：`None` **只給測試**（快取自始缺席之降級測試面）；production 恆 `Some`；boot 期 `cache::connect(redis_url)` 建連失敗 MUST **fail-loud panic**，不得靜默退 `None`。
3. **邊界維持、只開三欄**：`ip_rules`／`trust_model`（004 ip-trust-anchor 域）與 `mailer`（郵件域）續留域外；封條「不得逕加」句原樣保留、日後第六欄仍須新 ADR。
4. **同批改寫面**（U1）：`state.rs` 檔頭封條改「恰五欄（ADR-00027）」並**保留剩餘欄的邊界說明**、不得整段刪除；編譯期錨測改五欄窮舉解構（加第六欄即編譯紅）；`AppState { … }` 字面建構點以 `grep -rn 'AppState {'` 現算、同批全改（`main.rs`／`router.rs` 兩 stub／`handler/system_settings.rs` 兩處／`tests/common/mod.rs` `state_from_parts`；測試側 `cache: None`、`captcha_secret` 取非機密字面 `stub-captcha`、`JwtConfig` 取測試字面）。

## 後果

- 封條**強度不變、射程收窄**：「恰兩欄」→「恰五欄」，「開欄須拍板」門檻原樣保留。
- `Option<SessionCache>` 的 `None` 路徑成為 enforce 四級降級測試（真 redis／壞 redis 退 PG／PG 亦壞／nil 放行）的構造面之一；壞 redis 以指向不存在位址的連線構造。
- config 六 getter（`jwt_secret`／`refresh_token_secret`／`jwt_iss`／`jwt_aud`／`redis_url`／`captcha_secret`）隨本欄集進場，compose 環境鍵自 001 起即已接、本刀首次實讀。
- 依賴面（redis crate 進場）由 ADR-00028 承載；本 ADR 不動 wire 契約、不動 schema。

## 翻案觸發器

- 004 ip-trust-anchor 需 `trust_model`／`ip_rules` 欄（rev5:ADR 0041 同位）＝新 ADR 開第六、七欄。
- 郵件域刀需 `mailer` 欄＝新 ADR。
- 任何刀要讓 production 容許 `cache: None`（fail-open 化）＝觸憲法 §I.7 島 C 方向反轉、MAJOR。
