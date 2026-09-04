---
id: "LL-00001"
rule_id: "none：Cargo.lock 已入版控後，後續單元的 cargo 自然以現有 lock 為種子、零種子情境只出現在 workspace 首建；再犯面極窄（新 workspace 或刻意刪 lock）、不值一條規則，留本檔供 002 刀 server crate 進場時對照"
promotion_surface: none
---
LL-00001｜零種子 fresh resolve 讓 Cargo.lock 拉到 toolchain 不支援的新版 crate（tinyvec 1.13.0 vs rustc 1.96.1）

**徵狀**：001 刀 U1 首建 rust-api workspace 時，無 Cargo.lock 直接容器內 `cargo build --workspace`，cargo 對全部傳遞依賴解析到「最新相容版」（`Locking 369 packages to latest compatible versions`）；`tinyvec 1.13.0` 用到 rustc 1.96.1 沒有的巨集（`error: cannot find macro vec in this scope`）、build rc 101；且 lock 圖與 rev5 大面積分歧，違背 research R0「Cargo.lock 其餘同 rev5」與 spec FR-004「依賴首源＝rev5 lockfile」。

**成因**：manifest 只釘直接依賴五支的完整版號；傳遞依賴的版本由 lock 決定，零種子＝把「傳遞依賴用 rev5 已驗證組合」這個前提丟掉，crates.io 上比 rev5 收官晚發的新版自然被選進來，而 toolchain 釘在 1.96.1（`rust-toolchain.toml`＝deploy 映像同值）不動。

**處置**：先 `cp` `rev5:Cargo.lock` 到 rust-api/ 作種子，再容器內 `cargo build --workspace`——cargo 自動剪掉 rev5 server 專屬的 118 條 package、唯一版本異動＝`async-trait 0.1.89 → 0.1.92`（user 拍板取最新 patch）、零新增條目；`cargo build --workspace --locked` 綠、372 套件。lock 非程式碼、不在憲法 §I.5 拷貝禁令射程，最終檔案由 cargo 產出。

**再犯面與守法**：lock 落版控後，凡在同 workspace 加 crate（如 002 刀 server），cargo 以現 lock 為基底只解析新增節點、不會重演零種子；唯二再犯形＝新開 workspace、或刻意刪 lock 重解析——兩者都該先問「傳遞依賴的已驗證組合從哪裡來」，答案永遠是前代或現有 lock，不是 crates.io 最新。
