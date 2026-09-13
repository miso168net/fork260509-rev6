---
id: "ADR-00031"
title: rust-api boot 期 JWT access／refresh 兩把秘鑰同值即 fail-loud（兩鍵指名、訊息不含值；射程只 JWT 兩鑰）
date: 2026-09-14
status: accepted
supersedes: []
superseded_by: []
provenance: "user 拍板 2026-09-14（maint-backlog-pre-004 grill Q3「納入 A1」；同題附帶「只比 JWT 兩鑰、captcha 不擴」）；docs/ops/BACKLOG.md BL-00061；rust-api/server/src/auth/jwt.rs `verify_access`／`verify_refresh` doc「金鑰隔離即由只換秘鑰落實」；rev5 同位（rev5:server/src/main.rs）無此斷言＝rev6 新增行為；主線擬稿即 accepted（maint-backlog-pre-004 A1 收尾落檔）"
tags: [rust-api, security, boot, secrets, fail-loud]
---

## 背景

- rust-api 以兩把 HS256 秘鑰分簽兩種票：`APP_JWT_JWT_SECRET[_FILE]` 簽 access、`APP_JWT_REFRESH_TOKEN_SECRET[_FILE]` 簽 refresh；兩者經 `config::env_or_file` 各自讀入，`main.rs` 組進 `AppState.jwt`。
- 兩種票的 Claims 形狀逐欄相同（八欄），驗章底座 `verify_with` 兩路之間唯一的差別就是秘鑰——票面沒有「種類」欄。`jwt.rs` 文件明寫金鑰隔離「即由只換秘鑰落實」。
- 因此兩個 secret 檔一旦被填成同一值：refresh 票（壽命＝refresh TTL、seed 3900 秒）直接通過 `verify_access`，Authed 端點把它當 access 放行；金鑰隔離整層靜默消失、服務卻照常起來、log 無任何訊號。
- 「兩鑰須相異」原先只存在於碼註與 `deploy/secrets/README.md` 的生成慣例（各自亂數生成），boot 期零機器斷言（BL-00061）；rev5 同位亦無。

## 決策驅動因子

- 設定錯誤要在 boot 最前面、以一行指名的 log 倒地——與 `env_or_file` 四段 panic（缺鍵／讀檔失敗／空值／`CHANGE-ME` 範本值）同一立場，且 `main.rs` 已定「七支 getter 先讀完、再建連」次序。
- 失敗訊息不得洩漏任何秘鑰值（連「相同」的那個值都不印）。
- 不改票面格式、不動既有已簽發票與 wire 契約。
- 射程收斂：只補「同一種防線被靜默拆掉」的那一對鑰。

## 考慮過的替代案

1. **留帳、等下一支動 boot 鏈的刀**（BL-00061 原觸發）：誤設期間金鑰隔離持續失效且無訊號；斷言本身一行、測試側兩處 `JwtConfig` 構造字面本就相異＝落地即綠——user 選提前收。棄。
2. **票面加「種類」欄（typ）、驗章時比對**：金鑰隔離之外多一層型別分界，但改動票面格式、牽動簽發／驗章兩端與既有票的相容期，屬能力面擴張、非輕量軌射程。棄（不妨礙日後另立 ADR）。
3. **同值只記 warn、不倒地**：服務帶著已失效的隔離跑起來、訊號淹在 log 裡——與 `env_or_file` 的 fail-loud 立場相反。棄。
4. **一併斷言 captcha 秘鑰（三鑰兩兩相異）**：captcha 題票 Claims 形狀與會話票不同，跨用在解碼即被擋；無「同一種防線被靜默拆掉」的等價風險——user 裁定不擴。棄。

## 決定

1. **boot 期斷言**：`config.rs` 提供純函式比對兩鑰；兩值相同即 panic，訊息指名 `APP_JWT_JWT_SECRET[_FILE]` 與 `APP_JWT_REFRESH_TOKEN_SECRET[_FILE]` 兩鍵、★絕不含值。
2. **位置**：`main.rs` 於七支設定 getter 全部讀完之後、任何連線（DB／casbin／redis）建立之前呼叫——一個設定錯誤只佔一行 log。
3. **射程**：只 JWT access／refresh 兩鑰；captcha 秘鑰與其他機密不在此列。
4. **性質**：rev6 新增的 operator 可見 boot 行為（rev5 無），非翻案。
5. **本 ADR 只記拍板**：函式名、測試案名與落地 commit 歸收單事件與碼，不回灌本檔。

## 後果

- 兩個 secret 檔被填成同一值時，rust-api 容器開機即倒（`docker compose up --wait` 失敗），DB／redis 尚未建連；排障者由該行 panic 直接定位到兩鍵。
- `deploy/secrets/README.md` 不變式段載明「兩鑰相異、同值 boot 中止」。
- 測試側兩處 `JwtConfig` 構造（`state.rs` `for_tests`、`tests/common`）字面相異，零改動。
- 代價：日後若秘鑰輪替流程需要短暫讓兩鑰同值，會被本斷言擋下——屆時須先改輪替程序或另立 ADR。

## 翻案觸發器

- 票面增設種類欄且驗章兩路逐票比對、使「秘鑰相異」不再是唯一隔離手段時，可重議本斷言之必要性（新 ADR）。
- 秘鑰輪替程序確有「兩鑰暫時同值」之合法需求時（新 ADR 改寫決定 1 之條件）。
