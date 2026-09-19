---
id: "ADR-00036"
title: AppState 五欄→七欄（續行 ADR-00027）——加 trust_model／ip_rules；mailer 續留域外、開第八欄須新 ADR
date: 2026-09-19
status: accepted
supersedes: ["ADR-00027"]
superseded_by: []
provenance: "004-ip-trust-anchor brainstorm 既定不問 4（AppState 5→7 承 rev5、user 於 brainstorm 核可）；spec FR-060（grep 現核）、data-model §2.1／§2.2；ADR-00027 翻案觸發器首款已預告本翻案；rev5 同位＝rev5:ADR 0041（五→七欄）；判定面換版選型＝ADR-00035（arc-swap）；主線擬稿即 accepted（tasks T016）"
tags: [rust-api, state, decision-reversal, ip-trust-anchor]
---

## 背景

ADR-00027 把 `AppState` 封為「恰五欄」，並在翻案觸發器首款寫明「004 ip-trust-anchor 需 `trust_model`／`ip_rules` 欄＝新 ADR 開第六、七欄」。004 讓這個前提成立：

- **信任模型**於啟動時一次載入、之後唯讀共享（憲法 §I.7 島 F 之 F4：來源維度一切機制的位址輸入 MUST 為信任錨結果）——請求層中介層、稽核落列、防自鎖都要讀同一份。
- **IP 規則判定面** MUST 每請求零外部查詢（F2），且寫端成功後與門鈴 watcher 都要整份換版——需要一個全 crate 共享、可 lock-free 換版的句柄。

兩者都是「行程級、boot 期建好、各 handler／middleware 共用」的狀態，正是 `AppState` 的職責；放進模組級 static 會繞過建構點、測試無從注入。

## 決策驅動因子

- 測試可注入：integration 與 `#[cfg(test)]` 案須能給定「指定的信任模型」與「指定的規則集」，而不是改行程全域狀態。
- 建構點收斂（004 刀 U3 T014）後，字面建構點只剩 `main.rs`、`test_kit` 單一構造點與 `tests/common/mod.rs` 入口——加欄的編譯期連動面已縮到最小。
- 封條機制（檔頭邊界句＋不帶 `..` 的窮舉解構錨測）在 002／003 兩次翻案中證實有效，續用。

## 考慮過的替代案

1. **兩欄打包成一個 `IpDomain` 子結構、`AppState` 只加一欄**：兩者生命週期與可變性不同（`trust_model` 啟動後不可變、`ip_rules` 執行中換版），打包只是把欄數藏起來、封條失去「加狀態必過 ADR」的攔截力——棄（同 ADR-00027 棄「auth 子結構打包」之理）。
2. **`ip_rules` 用模組級 `static ArcSwap`**：handler 省一個參數，但測試彼此共用行程全域狀態、須序列化且互相汙染——棄。
3. **`trust_model` 每請求自 config 重讀**：違「啟動一次載入」（FR-010）、且把檔案 I/O 帶進請求路徑——棄。

## 決定

1. **ADR-00027 原意續行兩款**，現行依據＝本決定：①其決定 1 之 `JwtConfig { access_secret, refresh_secret, iss, aud }` 四欄形（access 與 refresh 各持一把密鑰）與 `SessionCache = redis::aio::ConnectionManager` 型別別名；②其決定 2（`cache: Option<SessionCache>` 語意：`None` 只給測試、production 恆 `Some`、建連失敗 fail-loud）。其決定 1 之 `AppState` 五欄字面由下款取代、決定 3／4 之邊界與改寫面由下兩款取代。
2. **`AppState` 五欄 → 七欄**：

   ```text
   AppState {
     db: DatabaseConnection, enforcer: Arc<RwLock<Enforcer>>, jwt: JwtConfig,
     cache: Option<SessionCache>, captcha_secret: String,
     trust_model: Arc<TrustModel>,          // 啟動一次載入、之後唯讀；預設全空＝全直連
     ip_rules: Arc<ArcSwap<RuleSet>>,       // 判定面；每請求 load()、寫端與門鈴 watcher 整份 store()
   }
   ```

   測試側預設：`trust_model`＝`TrustModel::default()`（全空）、`ip_rules`＝空 `RuleSet`（全放行）；production 由 boot 鏈載入（信任模型載入告警逐筆發、規則集初載失敗＝空集放行＋告警，方向皆 fail-open＝島 F F2／F3）。
3. **邊界維持、只開兩欄**：`mailer`（郵件域）續留域外；封條改「恰七欄、開第八欄須新 ADR」、**保留剩餘欄的邊界說明**不得整段刪除。
4. **同批改寫面**：`state.rs` 檔頭封條與各欄 doc；編譯期錨測改七欄窮舉解構（加第八欄即編譯紅）；字面建構點以 `grep -rn 'AppState {'` 現算、同批全改。

## 後果

- `Clone` 成本不變量級：兩新欄皆 `Arc`。
- 換版語意集中在 `ArcSwap`：讀端永遠拿到某一份完整規則集（無半更新態）；keep-last-good（重載失敗不 `store`）由 `ipgate` 承載、不在 `AppState`。
- 既有 contract case 不受影響（測試預設＝空規則集＋全空信任模型＝閘門全放行、來源信心走缺席退路）。

## 翻案觸發器

- 郵件域刀需 `mailer` 欄＝新 ADR 開第八欄。
- 任何刀要讓 production 容許 `cache: None`（fail-open 化）＝觸憲法 §I.7 島 C 方向反轉、MAJOR（承 ADR-00027 同款）。
- `ip_rules` 要改成「執行中真相不可讀即清空」＝觸島 F F2 方向反轉、MAJOR。
