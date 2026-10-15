---
id: "LL-00073"
rule_id: "none：命名屬工程判斷（CLAUDE.md §5）已明文；缺的是 plan 期定名查撞與單元定義之裁量句，守法寫於本檔、並由主線烤入後續單元定義"
promotion_surface: none
---
LL-00073｜照 rev5 藍本取名的新公開件 `password::load_policy` 撞上 rev6 自有 lint 腿③之 casbin 載入族 token——名字釘在 spec 家族十餘處，三支 implementer 皆升級、審查兩階段各再升級一次，碼品質 fix 才改名（007 刀 U6）

**徵狀**：007 刀 U6 implementer-1 依 T031 與 data-model 之跨檔定名落 `pub async fn load_policy`，全量測試 `tests/authz_entrypoint_lint.rs` 兩案轉紅（腿③實得檔集多出 `model/password.rs`）。該名同時寫在 tasks、data-model、research、plan、兩份 contracts 與 accepted ADR-00079 的 body；lint 檔又不在允許清單內。implementer-1～3 因此都以 done_with_escalation 收工，規格對照與碼品質第 1 輪也各升級一次。直到碼品質 fix-1 依工程命名權改名為 `load_password_policy`，全量才轉綠。

**成因**：plan 期沿用 rev5 的公開件名（`rev5:server/src/model/password.rs` 之 `load_policy`）。rev6 自 005 刀起另有 rev5 沒有的 authz_entrypoint_lint 腿③：載入族以完整 token「任何出現」即中，是刻意取寬的守門（ADR-00043 決定 5）。plan／tasks 定新件名時，沒有對既有碼面 lint 的 token 名冊查撞。agent 之間對「spec 指名之內部函式能否改名」的判讀也不一致：implementer 判為拍板級而停手，fix 判為工程命名而照改。

**處置**：採改名，不收窄腿③（收窄等於放寬硬禁令閘）。spec 家族勘誤 15 處；research 的 rev5 欄保留前代名。函式 doc 補一句「不取 rev5 名」的理由，防日後改回。ADR-00079 body 依 accepted 不可變留舊名，改名記在收單 commit 訊息。

**晉升面**：none——命名屬工程判斷已有明文（CLAUDE.md §5）；缺的是查撞的時點與單元定義裡的裁量句。

**再犯面與守法**：①SDD plan 期為新公開件定名（尤其沿用 rev5 名者），逐名以 `git grep -nw <名>` 掃全樹，含 `tests/*_lint.rs` 的 token 常數；撞上既有守門即當場換名。②單元定義烤一句：spec 指名之內部 Rust 件名若撞既有碼面 lint，改名屬工程判斷，implementer 在允許清單內照改，只把 spec 家族勘誤升級主線；wire 面字面（路徑、JSON 欄、msg 鍵）不在此列。
