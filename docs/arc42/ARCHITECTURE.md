<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# ARCHITECTURE — 活書索引（機器生成、例外註冊）

節檔＝`NN-<arc42 英文節名>.md`；標題取各檔 H1、摘要取 frontmatter `summary`、掛載 E 取 `rad_ai`、流程層檔＝`docs/process/` 中 `rad_ai` 同值之檔。決策住 `decisions/`（索引＝`docs/generated/DECISIONS-INDEX.md`）。

| 節 | 檔 | 摘要 | 掛載 E | 流程層檔 |
|---|---|---|---|---|
| §1 | [簡介與目標](01-introduction-and-goals.md) | 系統定位、品質目標、利害關係人；RAD-AI 論文缺口段 | — | — |
| §2 | [架構約束](02-architecture-constraints.md) | 技術／組織／慣例三類約束 | — | — |
| §3 | [脈絡與範圍](03-context-and-scope.md) | 業務脈絡與技術脈絡；E1 AI 邊界劃定的系統層落點 | E1 | [P-E1-boundary.md](../process/P-E1-boundary.md) |
| §4 | [解法策略](04-solution-strategy.md) | 技術選擇、頂層分解、品質目標達成法 | — | — |
| §5 | [建構區塊視圖](05-building-block-view.md) | 建構區塊三層白盒；E2 模型登錄視圖的系統層落點 | E2 | [P-E2-agent-registry.md](../process/P-E2-agent-registry.md) |
| §6 | [執行期視圖](06-runtime-view.md) | 執行期情境；E3 資料管線視圖的系統層落點 | E3 | [P-E3-doc-pipeline.md](../process/P-E3-doc-pipeline.md) |
| §7 | [部署視圖](07-deployment-view.md) | 基礎設施兩層；容器拓樸＝C4-L2、埠＝reference/ports | — | — |
| §8 | [橫切概念](08-crosscutting-concepts.md) | 資料／API／授權慣例、fork-delta 軌道；E4 負責任 AI 概念 | E4 | [P-E4-responsible-agent.md](../process/P-E4-responsible-agent.md) |
| §9 | [架構決策](09-architecture-decisions.md) | 決策外置 decisions/ 與索引；E5 AI-ADR 形制與對映表 | E5 | — |
| §10 | [品質需求](10-quality-requirements.md) | 品質需求概覽與情境；E6 AI 品質情境的系統層落點 | E6 | [P-E6-quality-scenarios.md](../process/P-E6-quality-scenarios.md) |
| §11 | [風險與技術債](11-risks-and-technical-debt.md) | 風險與技術債（指針 BACKLOG／LESSONS）；E7 AI 債務登記 | E7 | [P-E7-agent-debt.md](../process/P-E7-agent-debt.md) |
| §12 | [名詞表](12-glossary.md) | 系統術語與 AI 術語（保留）；流程術語住 RULES 名詞段 | — | — |
| §13 | [營運 AI 視圖](13-operational-ai-view.md) | E8 營運 AI 視圖：系統層目前無、指針 P-E8 | E8 | [P-E8-operations.md](../process/P-E8-operations.md) |
