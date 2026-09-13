<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# reference/rev5-blueprint-map — rev5 活書藍本對照表（一次性 migrate-audit 面；ADR-00006）

名冊＝rev5 活書 `../fork260509-rev5/docs/arc42/ARCHITECTURE.md`（凍結 SHA 7eab28a）的 12 個 `##`＋8 個 `###`（`references.REV5_BLUEPRINT`）；去處＝`docs/arc42/NN-*.md` frontmatter `rev5_blueprint`（鍵＝rev5 標題字面、值＝承襲（…）／隨刀：…／不承襲：…）。未宣告列「缺」、多檔宣告標「重複」、鍵不在名冊列「未知鍵」、值不以三詞起頭標「形制」；四項皆零＝藍本對照表零缺（波 3 出口判準、非常駐閘）。

| rev5 標題 | 層 | rev6 去處 | 處置 |
|---|---|---|---|
| §1 簡介與目標 | ## | [01-introduction-and-goals.md](../../arc42/01-introduction-and-goals.md) | 承襲（能力級／明確不做／建置狀態改寫為 rev6 現況） |
| §2 約束 | ## | [02-architecture-constraints.md](../../arc42/02-architecture-constraints.md) | 承襲（技術棧／拓樸／環境／上游關係四條＋rev6 新約束） |
| §3 系統脈絡 | ## | [03-context-and-scope.md](../../arc42/03-context-and-scope.md) | 不承襲：rev5 空節（該節自述尚無內容）；rev6 §3 自 C4-L1 起手 |
| §4 解法策略 | ## | [04-solution-strategy.md](../../arc42/04-solution-strategy.md) | 承襲（五條策略對 rev6 仍真、上位＝憲法 §I.1～I.5） |
| §5 Building blocks | ## | [05-building-block-view.md](../../arc42/05-building-block-view.md) | 承襲（rust-api workspace 四 crate＝migration／entity／sea-orm-adapter／server；server 管線 as-built 見 §5.2、以 rev5 活書 §5 為藍本重打字＝憲法 §I.5） |
| §6 Runtime | ## | [06-runtime-view.md](../../arc42/06-runtime-view.md) | 承襲（方針段：不變式凍結面住憲法 §I.7、本節只寫 as-built）；情境隨島進場 |
| 信任錨與 IP 存取閘 | ### §6 | [06-runtime-view.md](../../arc42/06-runtime-view.md) | 隨刀：憲法 §I.7 島 F 進場刀 |
| 會話狀態機（sys_token） | ### §6 | [06-runtime-view.md](../../arc42/06-runtime-view.md) | 承襲（§6.1「會話狀態機——島 A～D」情境：登入簽發對→每請求驗章＋denylist→續期 rotate／grace／reuse→撤銷三型 logout／kick／idle；凍結面住憲法 §I.7 島 A～D、rev5 該子節為藍本重打字） |
| 登入失敗節流三區（帳號維＋來源維） | ### §6 | [06-runtime-view.md](../../arc42/06-runtime-view.md) | 承襲（§6.1「登入失敗節流——島 E」情境：帳號維三區 precheck→captcha gate→L1 lock／L2 count→降級七源可觀測；凍結面住憲法 §I.7 島 E、rev5 該子節帳號維部分為藍本重打字）；來源維隨島 F |
| 使用者域斷權與密碼三入口（007 落地） | ### §6 | [06-runtime-view.md](../../arc42/06-runtime-view.md) | 隨刀：憲法 §I.7 島 I 進場刀（使用者域） |
| §7 部署 | ## | [07-deployment-view.md](../../arc42/07-deployment-view.md) | 不承襲：rev5 空節；rev6 §7 自 C4-L2 與 reference/ports 起手 |
| §8 橫切概念 | ## | [08-crosscutting-concepts.md](../../arc42/08-crosscutting-concepts.md) | 承襲（四子節形制） |
| fork-delta 接線現況（base-web） | ### §8 | [08-crosscutting-concepts.md](../../arc42/08-crosscutting-concepts.md) | 承襲（指針形：規則面承 rev5 FORK-DELTA-WIRING、接線 as-built 隨 base-web 各刀重生） |
| 資料慣例 | ### §8 | [08-crosscutting-concepts.md](../../arc42/08-crosscutting-concepts.md) | 承襲（archetype 四變體與成對條款在憲法 §I.6；三閘／演進帳／歸屬帳＝ADR-00010；memo 欄與 ORM 紀律見 §8.1） |
| API 慣例 | ### §8 | [08-crosscutting-concepts.md](../../arc42/08-crosscutting-concepts.md) | 承襲（信封／碼表／i64 守衛＝憲法 §I.3；契約機器化與部分更新三態＝§8.2、ADR-00015；msg 名冊後端側閉環＝ADR-00017） |
| 授權慣例 | ### §8 | [08-crosscutting-concepts.md](../../arc42/08-crosscutting-concepts.md) | 承襲（判定單點／DB-fresh＝憲法 §I.2；拒絕語意與 no-escalation 掛點＝§8.3、ADR-00014；no-escalation 本體與三維授權治理＝憲法 §I.7 島 G／I 承襲指針） |
| §9 架構決策 | ## | [09-architecture-decisions.md](../../arc42/09-architecture-decisions.md) | 承襲（decisions/ 一決策一檔＋DECISIONS-INDEX 指針；波 2 落地） |
| §10 品質要求 | ## | [10-quality-requirements.md](../../arc42/10-quality-requirements.md) | 不承襲：rev5 空節；rev6 §10 自 §1.2 品質目標展開、情境隨島進場 |
| §11 風險與技術債 | ## | [11-risks-and-technical-debt.md](../../arc42/11-risks-and-technical-debt.md) | 承襲（BACKLOG／LESSONS 指針；rev6 加 ※11.1 風險） |
| §12 名詞表 | ## | [12-glossary.md](../../arc42/12-glossary.md) | 承襲（治理詞入 §12 系統術語；踢除／撤銷與鎖定兩組域詞已入表，停用／軟刪、重設／修改密碼兩組隨島 I 進場刀） |

缺：0｜重複：0｜未知鍵：0｜形制：0
