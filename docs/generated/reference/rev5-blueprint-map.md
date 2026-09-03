<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# reference/rev5-blueprint-map — rev5 活書藍本對照表（一次性 migrate-audit 面；ADR-00006）

名冊＝rev5 活書 `../fork260509-rev5/docs/arc42/ARCHITECTURE.md`（凍結 SHA 7eab28a）的 12 個 `##`＋8 個 `###`（`references.REV5_BLUEPRINT`）；去處＝`docs/arc42/NN-*.md` frontmatter `rev5_blueprint`（鍵＝rev5 標題字面、值＝承襲（…）／隨刀：…／不承襲：…）。未宣告列「缺」、多檔宣告標「重複」、鍵不在名冊列「未知鍵」、值不以三詞起頭標「形制」；四項皆零＝藍本對照表零缺（波 3 出口判準、非常駐閘）。

| rev5 標題 | 層 | rev6 去處 | 處置 |
|---|---|---|---|
| §1 簡介與目標 | ## | [01-introduction-and-goals.md](../../arc42/01-introduction-and-goals.md) | 承襲（能力級／明確不做／建置狀態改寫為 rev6 現況） |
| §2 約束 | ## | [02-architecture-constraints.md](../../arc42/02-architecture-constraints.md) | 承襲（技術棧／拓樸／環境／上游關係四條＋rev6 新約束） |
| §3 系統脈絡 | ## | [03-context-and-scope.md](../../arc42/03-context-and-scope.md) | 不承襲：rev5 空節（該節自述尚無內容）；rev6 §3 自 C4-L1 起手 |
| §4 解法策略 | ## | [04-solution-strategy.md](../../arc42/04-solution-strategy.md) | 承襲（五條策略對 rev6 仍真、上位＝憲法 §I.1～I.5） |
| §5 Building blocks | ## | 缺 | 缺 |
| §6 Runtime | ## | 缺 | 缺 |
| 信任錨與 IP 存取閘 | ### §6 | 缺 | 缺 |
| 會話狀態機（sys_token） | ### §6 | 缺 | 缺 |
| 登入失敗節流三區（帳號維＋來源維） | ### §6 | 缺 | 缺 |
| 使用者域斷權與密碼三入口（007 落地） | ### §6 | 缺 | 缺 |
| §7 部署 | ## | 缺 | 缺 |
| §8 橫切概念 | ## | 缺 | 缺 |
| fork-delta 接線現況（base-web） | ### §8 | 缺 | 缺 |
| 資料慣例 | ### §8 | 缺 | 缺 |
| API 慣例 | ### §8 | 缺 | 缺 |
| 授權慣例 | ### §8 | 缺 | 缺 |
| §9 架構決策 | ## | 缺 | 缺 |
| §10 品質要求 | ## | 缺 | 缺 |
| §11 風險與技術債 | ## | 缺 | 缺 |
| §12 名詞表 | ## | 缺 | 缺 |

缺：16｜重複：0｜未知鍵：0｜形制：0
