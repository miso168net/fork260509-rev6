<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
<!-- next: LL-00002 -->
# LESSONS — 教訓索引（機器生成；一坑一檔住 LESSONS/LL-NNNNN-<slug>.md）

配號＝本檔頭 next（自檔集最大號＋1 推導；ADR-00005）→ 建檔 → `python3 tools/docsync generate`。條目檔 frontmatter：`id`、`rule_id`（RL-NNNN 或 none：理由）、`promotion_surface`（rules／gate／code／none）、選填 `recurrence_of`；正文首行 `LL-NNNNN｜坑名`（GT-08 對賬）。

| LL | 坑名 | rule_id | promotion_surface | 檔 |
|---|---|---|---|---|
| LL-00001 | 零種子 fresh resolve 讓 Cargo.lock 拉到 toolchain 不支援的新版 crate（tinyvec 1.13.0 vs rustc 1.96.1） | none：Cargo.lock 已入版控後，後續單元的 cargo 自然以現有 lock 為種子、零種子情境只出現在 workspace 首建；再犯面極窄（新 workspace 或刻意刪 lock）、不值一條規則，留本檔供 002 刀 server crate 進場時對照 | none | [LL-00001-cargo-lock-zero-seed-resolve.md](LESSONS/LL-00001-cargo-lock-zero-seed-resolve.md) |
