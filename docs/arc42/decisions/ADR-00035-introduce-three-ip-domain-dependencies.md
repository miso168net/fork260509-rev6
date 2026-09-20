---
id: "ADR-00035"
title: 引入 IP 域依賴三支——arc-swap 1.9.2／futures-util 0.3.34（default features 關）／toml 1.1.6；ADR-00028 決定 2「明確不進」七支中三支之前提於 004 成立
date: 2026-09-15
status: accepted
supersedes: []
superseded_by: []
provenance: "004-ip-trust-anchor plan 2026-09-15 research R1（三源＝rev5 lock／rev6 lock 現值 vs crates.io 最新穩定 2026-09-15）；brainstorm G7（toml 三源分歧、user 拍板 1.1.6；arc-swap／futures-util 三源一致、直採報備不問）；rev5 同位＝rev5:004 research R3（rev5 釘 arc-swap 1.9.2／futures-util 0.3.34／toml 1.1.4、features 同形、零新 redis feature flag 同判）；「域外者不進」紀律承 rev5:ADR 0032；進場依 ADR-00028 翻案觸發器第二款（清單中任一支前提成立＝該刀 ADR 承載、非修訂 ADR-00028）；主線擬稿即 accepted（tasks T003）"
tags: [rust-api, dependency, version-pinning, ip-trust-anchor]
---

## 背景

ADR-00028 決定 2 把 rev5 server 終態有、003 前提未成立的七支列為「明確不進」——`lettre`／`toml`／`arc-swap`／`once_cell`／`futures-util`／`xdb`／`subtle`——並於翻案觸發器寫明「清單中任一支前提成立＝該刀 ADR 承載、非本 ADR 修訂」。004-ip-trust-anchor 讓其中三支的前提成立：

- **`toml`**：信任模型設定檔以 TOML 交付（`APP_TRUST_MODEL_PATH`、dev 交付形 `deploy/trust-model.dev.toml`、六集合），boot 須解析為 `RawTrustModel`（`serde` derive＋未知鍵逐鍵檢、不用 `deny_unknown_fields`）——外部設定檔的前提自此成立。
- **`arc-swap`**：IP 規則判定面 MUST **每請求零外部查詢**（憲法 §I.7 島 F F2），規則集以 `Arc<ArcSwap<RuleSet>>` 承載、門鈴重載後整份 `store`——熱替換的前提自此成立。
- **`futures-util`**：門鈴訂閱走 redis pub/sub 串流，watcher 唯一使用點＝`StreamExt::next()`——串流消費的前提自此成立。

其餘四支（`lettre`／`once_cell`／`xdb`／`subtle`）前提仍未成立、仍不進（IP 庫 `xdb` 尤其：本刀無 region／GeoIP，research R3 清單 B 明列不得帶回）。

## 決策驅動因子

- **全域版本紀律**（CLAUDE.md §6；`rust-api/Cargo.toml` 檔頭）：每支三源核對（rev5 lock／rev6 lock 現值／crates.io 最新穩定）、同值直採、分歧由 user 拍板。
- **版本單一來源**＝`[workspace.dependencies]` 完整三段釘死、成員側只寫 `{ workspace = true }`＋features（ADR-00028 決定 1 同形）。
- **供應鏈面最小化**：`futures-util` 只用 `StreamExt::next` ⇒ `default-features = false`，不拖 default 之 `async-await` 巨集鏈（`futures-macro` proc-macro）；零新 redis feature flag——pub/sub 訂閱在既有 `connection-manager`＋`tokio-comp` 下即可用（rev5 同組合實證）。
- **lock 圖零擾動**：`arc-swap`／`futures-util` 於 rev6 `Cargo.lock` 已為傳遞依賴且與最新穩定同值，直接依賴化不動現值；`toml` 為全新條目。

## 考慮過的替代案

1. **`toml` 沿 rev5 1.1.4**（藍本逐字同版）：同 minor 差 patch、無傳遞約束，一進場即釘舊 patch——棄（G7）。
2. **省 `futures-util`、watcher 手寫 `poll_fn`**：規則熱重載路徑上十行難審樣板、換不掉一支已在 lock 圖內的 crate——棄（承 rev5:004 research R3 同判）。
3. **`futures-util` 取 default features**：多拖 `async-await`／`futures-macro` proc-macro 鏈、唯一使用點用不到——棄。
4. **判定面改 `RwLock<Arc<RuleSet>>`**：讀端每請求取讀鎖、寫端有飢餓面；`ArcSwap::load` 為 lock-free 讀且 rev5 已驗——棄。

## 決定

1. **引入三支**（版本三段全釘、單一來源＝`rust-api/Cargo.toml` `[workspace.dependencies]`；`rust-api/server/Cargo.toml` 只寫 `{ workspace = true }`）：

   | crate | 版本（拍板） | rev5 釘版 | rev6 lock 現值 | crates.io 最新穩定（2026-09-15） | features（workspace 側） | 用途 |
   |---|---|---|---|---|---|---|
   | `arc-swap` | **1.9.2** | 1.9.2 | 1.9.2（傳遞） | 1.9.2 | default | `Arc<ArcSwap<RuleSet>>` 判定面 lock-free 換版 |
   | `futures-util` | **0.3.34** | 0.3.34 | 0.3.34（傳遞） | 0.3.34 | `default-features = false`（唯一使用點＝watcher `StreamExt::next()`） | 門鈴訂閱串流 |
   | `toml` | **1.1.6**（G7） | 1.1.4 | 不在 lock | 1.1.6（完整字串 `1.1.6+spec-1.1.0`、`+` 後為建置註記、Cargo 不參與比對） | default | 信任模型設定檔解析 |

2. **落點與碼註**：兩份 `Cargo.toml` 各加三行；兩檔檔頭碼註改現在式——「明確不進七支」句改為餘四支＋引本 ADR，`web／obs 依賴群隨功能刀進場` 之本刀兌現處改現在式（RL-0015）；`Cargo.lock` 由容器內 `cargo build --workspace` 機器重算：`toml` 及其子依賴為新條目（按 lock 實得、不手列）、`arc-swap`／`futures-util` 版本不變、★**不得出現 `futures-macro` 新條目**（default 關之機器證據；tasks T004 DoD、記 commit 訊息）。
3. **API 守則**（烤入 implementer prompt）：`ArcSwap::load`／`store` 兩式；`StreamExt::next` 為 `futures-util` 唯一使用點；`toml::from_str::<RawTrustModel>`＋載入面逐鍵檢（未知鍵＝只發 `unknown_key` 告警、六集合照常生效；★不用 `serde(deny_unknown_fields)`——會把一個手誤升級成層②全空、與契約「未知鍵＝載入告警（不當機）」相違；rev5 config.rs 碼註同判）；redis 1.7 pub/sub 以 `Client::get_async_pubsub()` 另開專用 `redis::Client`（多工 `ConnectionManager` 不可 SUBSCRIBE）；`IpNetwork` 經 `sea_orm::prelude::IpNetwork` 取用、`ipnetwork` 不列直接依賴（rev5 同形）。
4. 「域外者不進」紀律不變；ADR-00028 決定 2 之「明確不進」清單自此餘 `lettre`／`once_cell`／`xdb`／`subtle` 四支。

## 後果

- 判準不變、結論隨前提翻轉（同 ADR-00028 後果首款）：翻的是「toml／arc-swap／futures-util 屬域外」這個隨刀變動的事實。
- lock 圖：兩支零變動、一支新條目群；容器內 `cargo build --workspace --locked` 綠＝機器證據（T004）。
- `futures-util` default 關：日後任何 `join!`／`select!` 巨集需求須另開 feature、屬本 ADR 翻案面。
- 供應鏈面：三支皆廣泛使用之 crate；crate 名與本刀新模組（`crate::trust`／`crate::ipgate`）不撞名、無 ADR-00028 之 `captcha` 消歧問題。

## 翻案觸發器

- 任一支需 major 升版＝維護批依同一三源紀律、新 ADR 記拍板。
- `futures-util` 需開 default／`async-await` feature＝新 ADR（非本 ADR 修訂）。
- 「明確不進」餘四支任一前提成立＝該刀 ADR 承載（同 ADR-00028 第二款）。
