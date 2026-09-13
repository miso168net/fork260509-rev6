---
id: "ADR-00028"
title: root Cargo.toml「不引 argon2」翻案——引入 auth 依賴八支（六支 auth＋log＋getrandom）、全域版本紀律雙源核對 D1～D6
date: 2026-09-08
status: accepted
supersedes: []
superseded_by: []
provenance: "003-auth-session plan 2026-09-08 research R1（雙源＝rev5 lock／rev6 lock 現值 vs crates.io 最新穩定 2026-09-08；user 逐支拍板 D1～D5 全取最新穩定、D6 getrandom 主線同值直採）；spec FR-032／FR-034；被翻案的拍板住 rust-api/Cargo.toml 檔頭碼註（001 刀 research R1、user 2026-09-04：001 無 runtime 雜湊故不引 argon2）與 rust-api/server/Cargo.toml 檔頭不進清單（002 刀 research R1）、無 ADR 承載故 supersedes 留空；rev5 同位＝rev5:ADR 0032（六支、沿 rev4 組合值）；「域外者不進」紀律承 rev5:ADR 0032 不變；主線擬稿即 accepted（tasks T003）"
tags: [rust-api, dependency, version-pinning, decision-reversal, auth]
---

## 背景

兩處碼註承載了同一個拍板：

- `rust-api/Cargo.toml` 檔頭：「★『域外者不進』紀律（承 rev5:ADR 0032）：001-schema-baseline 無 runtime 雜湊（seed password＝PHC 定稿常數）故不引 argon2；auth／web／obs 依賴群一律不在此、各隨其功能刀進場」。
- `rust-api/server/Cargo.toml` 檔頭：「rev5 server 於後刀擴入而 002 刀域外者一律不進（argon2／captcha／hex／jsonwebtoken／redis／sha2／arc-swap／futures-util／toml／log——各隨其功能刀）」。

拍板的**前提**寫得很清楚：001／002 沒有 runtime 密碼驗證，seed 的 password 只是 PHC 定稿常數字串。前提成立時結論正確。003-auth-session 讓前提消滅：真登入必須在 runtime 以 argon2id 拿使用者送來的密碼去驗 seed 的 PHC；連帶簽發與驗章要 `jsonwebtoken`、denylist／grace／節流 L1 要 `redis`、圖形驗證碼要 `captcha`、token hash 與答案 MAC 要 `sha2`＋`hex`；BL-00026 的 `sqlx_logging_level` 要 `log::LevelFilter` 型別；argon2 0.6 拔掉 `rand_core::OsRng` 後，CSPRNG 要具名依賴 `getrandom`。

## 決策驅動因子

- **全域版本紀律**（CLAUDE.md §6）：每支雙源核對（rev5 lock／rev6 lock 現值 vs crates.io 最新穩定）、同值直採、分歧由 user 逐支拍板；001／002 同型先例＝分歧取最新穩定。
- **feature 陷阱必須在 manifest 釘死**：`jsonwebtoken` 漏開 `rust_crypto` 不是編譯紅、是 decode 執行期 panic。
- **API 破壞面實查**（research R1 守則）：jsonwebtoken 11 主路徑 API 不變（enum `non_exhaustive` ⇒ match 補 `_` 臂）；argon2 0.6 `simple`→`password-hash` feature 改名、移除 `std`、`rand_core` 0.10 已無 `OsRng`＝rev5 取亂數路徑不可沿用；redis 1.7 `FromRedisValue` 收 owned 值；sha2 0.11 `digest` 0.11 同形；captcha 1.0.0 無變。
- MSRV 最高 1.88（jsonwebtoken／redis）≤ rev6 toolchain 1.96.1。

## 考慮過的替代案

1. **全沿 rev5 lock 值**（argon2 0.5.3／jsonwebtoken 10.4.0／redis 1.3.0／sha2 0.10.9／log 0.4.33）：重打字摩擦最小，但落後一至四個版本、日後另開維護批升版；002 對 jsonschema 同型棄案——棄（D1～D5）。
2. **只升 minor／patch、major 沿 rev5**：jsonwebtoken 10→11 破壞面不觸主路徑、無理由獨留——棄。
3. **CSPRNG 改引 `rand`**：多一支 crate、且 argon2 內部本就經 `getrandom` 取亂數；rev6 lock 現值 0.4.3＝最新穩定、同值直採零新 crate——棄（D6）。

## 決定

1. **引入八支**（版本三段全釘、單一來源＝`rust-api/Cargo.toml` `[workspace.dependencies]`；`server/Cargo.toml` 只寫 `{ workspace = true }`＋features）：

   | crate | 版本（拍板） | features（server 側） | 用途 |
   |---|---|---|---|
   | jsonwebtoken | **11.0.0**（D1） | `default-features = false`＋`rust_crypto`（★硬要求） | access／refresh／captcha 三處 HS256 簽驗 |
   | argon2 | **0.6.0**（D2） | 預設（`alloc`／`getrandom`／`password-hash`） | seed argon2id PHC 驗章＋`dummy_verify` 時序等化；本刀不產 hash |
   | redis | **1.7.0**（D3） | `default-features = false`＋`connection-manager`＋`tokio-comp` | denylist／grace／last_activity／idle-emitted／captcha nonce／節流 L1 |
   | captcha | 1.0.0（同值） | `default-features = false`（關 `audio`） | 圖形題產圖 |
   | sha2 | **0.11.0**（D4） | 預設 | `token_hash`＋captcha `ans_mac`；★lock 同時存 sqlx 間接帶的 0.10.9＝兩份副本、已知代價 |
   | hex | 0.4.3（同值、rev6 lock 已在） | 預設 | hash hex 編碼 |
   | log | **0.4.34**（D5） | 預設 | 僅 `log::LevelFilter::Debug`（BL-00026）；容器內 `cargo update -p log` 令間接依賴同版、單一副本 |
   | getrandom | 0.4.3（D6 同值直採） | 預設 | CSPRNG：captcha nonce 與答案拒絕採樣、sid／jti uuid v4 素材（`getrandom::fill`） |

2. **明確不進**（rev5 有、本刀域外或紀律禁）：`lettre`／`toml`／`arc-swap`／`once_cell`／`futures-util`／`xdb`／`subtle`——各自前提（郵件、外部設定檔、熱替換、IP 庫、常數時間比較另有承載）本刀一個都沒成立。
3. **三處舊拍板註解同批改寫**（U1 T004）：root `Cargo.toml` 檔頭「不引 argon2」句改現在式並指本 ADR；`server/Cargo.toml` 檔頭不進清單改寫為只列上述不進者；`state.rs` 恰兩欄封條屬 ADR-00027 射程（此處僅記其同批性）。
4. `Cargo.lock` 入版控；新增套件數記 U1 commit 訊息（事後可查）。

## 後果

- 拍板的**判準不變、結論隨前提翻轉**：「域外者不進」紀律完好，翻的是「argon2 屬域外」這個隨刀變動的事實；日後任一支要進，同樣看前提是否成立、不看清單本身。
- rev5 對應檔只當藍本、照新版 API 寫（research R1 守則烤入 implementer）：亂數四處一律 `getrandom::fill`、`SaltString::generate` 本刀不用。
- **供應鏈面誠實揭露**：`captcha 1.0.0` 是唯一非廣泛使用的依賴、且 crate 名與 `crate::captcha` 模組同名（消歧三規則隨 U8 落 `captcha/mod.rs` 檔頭碼註）；字元集受其內嵌字型 glyph 涵蓋限制（收 34 字＋字型涵蓋測試）。
- sha2 兩副本為已知代價（sqlx 釘 0.10 系），不以降版消除。

## 翻案觸發器

- 任一支需 major 升版＝維護批依同一雙源紀律、新 ADR 記拍板。
- 「明確不進」清單中任一支前提成立（如郵件刀引 `lettre`）＝該刀 ADR 承載、非本 ADR 修訂。
