<!-- wave: 1 -->
# NOTES — 當前意圖／下一步

## 現況（波 1 後段）

治理工具落地中：`tools/docsync` 骨架、RULES.md 首版（73 條、ADR-00004）、憲法 1.0.0（ADR-00003）已入 `000-w1-governance-tooling` 分支；
events／adr／book／references／gates 六模組與 GT-01～GT-12、掃描防線（.githooks、.gitleaks.toml）、README 與正式版 CLAUDE.md 依計畫
`docs/brainstorms/000-w1-governance-tooling.md` 逐 Task 落地。

## 下一步

- 波 1 出口：`python3 tools/docsync lint` 零 ERROR、Day-1 豁免逐筆有解除謂詞、GT-12 首值在預算內、pre-commit 實跑守門；
  `merge --no-ff` 回 `rev6-admin-root`＋misc 事件收單。
- 波 2：arc42 12 節檔＋§13＋ARCHITECTURE.md 索引、C4 五檔、compliance 兩檔、process 九檔骨架、ops 帳本空檔（啟動書 §5）。

## 未決

- rev6 GitHub remote：掃描防線就位後再建（啟動書附錄 D；ADR-00002 後果段）。
- `alert_webhook_url` 佔位值→真值（RUNBOOK §15.4 形重加密）。
