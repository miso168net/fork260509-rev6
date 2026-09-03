<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# reference/rev5-blueprint-map — rev5 活書藍本對照表（一次性 migrate-audit 面；ADR-00006）

名冊＝rev5 活書 `../fork260509-rev5/docs/arc42/ARCHITECTURE.md`（凍結 SHA 7eab28a）的 12 個 `##`＋8 個 `###`（`references.REV5_BLUEPRINT`）；去處＝`docs/arc42/NN-*.md` frontmatter `rev5_blueprint`（鍵＝rev5 標題字面、值＝承襲（…）／隨刀：…／不承襲：…）。未宣告列「缺」、多檔宣告標「重複」、鍵不在名冊列「未知鍵」、值不以三詞起頭標「形制」；四項皆零＝藍本對照表零缺（波 3 出口判準、非常駐閘）。

| rev5 標題 | 層 | rev6 去處 | 處置 |
|---|---|---|---|
| §1 簡介與目標 | ## | [01-introduction-and-goals.md](../../arc42/01-introduction-and-goals.md) | 承襲（能力級／明確不做／建置狀態改寫為 rev6 現況） |
| §2 約束 | ## | [02-architecture-constraints.md](../../arc42/02-architecture-constraints.md) | 承襲（技術棧／拓樸／環境／上游關係四條＋rev6 新約束） |
| §3 系統脈絡 | ## | [03-context-and-scope.md](../../arc42/03-context-and-scope.md) | 不承襲：rev5 空節（該節自述尚無內容）；rev6 §3 自 C4-L1 起手 |
| §4 解法策略 | ## | [04-solution-strategy.md](../../arc42/04-solution-strategy.md) | 承襲（五條策略對 rev6 仍真、上位＝憲法 §I.1～I.5） |
| §5 Building blocks | ## | [05-building-block-view.md](../../arc42/05-building-block-view.md) | 隨刀：rust-api 骨架刀（workspace members 與管線形；rust-api 現為源倉 Initial commit）；本波只寫傘狀層白盒 |
| §6 Runtime | ## | [06-runtime-view.md](../../arc42/06-runtime-view.md) | 承襲（方針段：不變式凍結面住憲法 §I.7、本節只寫 as-built）；情境隨島進場 |
| 信任錨與 IP 存取閘 | ### §6 | [06-runtime-view.md](../../arc42/06-runtime-view.md) | 隨刀：憲法 §I.7 島 F 進場刀 |
| 會話狀態機（sys_token） | ### §6 | [06-runtime-view.md](../../arc42/06-runtime-view.md) | 隨刀：憲法 §I.7 島 A～D 進場刀（auth 會話） |
| 登入失敗節流三區（帳號維＋來源維） | ### §6 | [06-runtime-view.md](../../arc42/06-runtime-view.md) | 隨刀：憲法 §I.7 島 E 進場刀（帳號維）；來源維隨島 F |
| 使用者域斷權與密碼三入口（007 落地） | ### §6 | [06-runtime-view.md](../../arc42/06-runtime-view.md) | 隨刀：憲法 §I.7 島 I 進場刀（使用者域） |
| §7 部署 | ## | [07-deployment-view.md](../../arc42/07-deployment-view.md) | 不承襲：rev5 空節；rev6 §7 自 C4-L2 與 reference/ports 起手 |
| §8 橫切概念 | ## | [08-crosscutting-concepts.md](../../arc42/08-crosscutting-concepts.md) | 承襲（四子節形制） |
| fork-delta 接線現況（base-web） | ### §8 | [08-crosscutting-concepts.md](../../arc42/08-crosscutting-concepts.md) | 承襲（指針形：規則面承 rev5 FORK-DELTA-WIRING、接線 as-built 隨 base-web 各刀重生） |
| 資料慣例 | ### §8 | [08-crosscutting-concepts.md](../../arc42/08-crosscutting-concepts.md) | 隨刀：schema 基線刀（archetype 四變體與成對條款已入憲法 §I.6、本波留指針） |
| API 慣例 | ### §8 | [08-crosscutting-concepts.md](../../arc42/08-crosscutting-concepts.md) | 隨刀：wire 地基刀（信封、碼表、i64 守衛已入憲法 §I.3；部分更新三態承 rev5:ADR 0023 隨刀重審） |
| 授權慣例 | ### §8 | [08-crosscutting-concepts.md](../../arc42/08-crosscutting-concepts.md) | 隨刀：授權治理刀（憲法 §I.7 島 G／I；判定單點與 DB-fresh 已入憲法 §I.2、本波留指針） |
| §9 架構決策 | ## | [09-architecture-decisions.md](../../arc42/09-architecture-decisions.md) | 承襲（decisions/ 一決策一檔＋DECISIONS-INDEX 指針；波 2 落地） |
| §10 品質要求 | ## | [10-quality-requirements.md](../../arc42/10-quality-requirements.md) | 不承襲：rev5 空節；rev6 §10 自 §1.2 品質目標展開、情境隨島進場 |
| §11 風險與技術債 | ## | [11-risks-and-technical-debt.md](../../arc42/11-risks-and-technical-debt.md) | 承襲（BACKLOG／LESSONS 指針；rev6 加 ※11.1 風險） |
| §12 名詞表 | ## | [12-glossary.md](../../arc42/12-glossary.md) | 承襲（治理詞入 §12 系統術語；域詞四組隨島 A～I 進場刀） |

缺：0｜重複：0｜未知鍵：0｜形制：0
