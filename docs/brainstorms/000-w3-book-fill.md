# 波 3 活書填實實作計畫（000-w3-book-fill）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans 逐 Task 執行（本 session 主線自做、不派 subagent；只在 merge 時點停）。Steps 用 `- [ ]` 勾選。

**Goal:** 把波 2 骨架的 95 處 `TODO(波 3)` 全數填為真內容（arc42 28／c4 16／process 51），產出 rev5 藍本對照表（20 列、缺／重複／未知鍵／形制四項皆零），波標記 bump 4。

**Architecture:** 內容三軌——arc42 官方子節自 rev5 單檔活書重打字消化（憲法 §I.5：讀允許、拷貝禁止、註解重寫、拍板已推翻者不帶回）；流程層 51 子節每節首句「類比張力：」真句（對得上／部分／硬套三判定、後兩者附理由）；C4-E 三檔規則與表。工具一支——arc42 節檔 frontmatter `rev5_blueprint:`（人寫的家）→ `references.gen_rev5_blueprint_map` 生成 `docs/generated/reference/rev5-blueprint-map.md`（缺列可見、永不 rc 1；ADR-00006）。

**Tech Stack:** python 標準庫（`tools/docsync`）、Markdown＋mermaid、git（`-F` 檔訊息）。

**Spec:** 啟動書 `docs/brainstorms/000-doc-architecture.md`（§1 DoD 第 5 點、§3.2 樹 process 八列內容提示、§3.4 形制規則、§3.7 藍本表首列、§5 波 3 列）；波 2 計畫 `docs/brainstorms/000-w2-book-skeleton.md` §0.3 剩餘欄；本檔 §0.1 兩題拍板。

---

## 0. 本 brainstorm 的拍板與判斷

### 0.1 user 拍板（2026-09-03；一題一問、首選項為建議、兩題皆取 A）

| 題 | 結論 | 理由（一句） |
|---|---|---|
| Q1 藍本「去處」這 20 筆人判斷住哪 | **A：frontmatter `rev5_blueprint:` 住同號 rev6 節檔**（鍵＝rev5 標題字面、值＝`承襲（…）`／`隨刀：…`／`不承襲：…`） | 與波 2 `rad_ai_map`→RAD-AI-MAP、`summary`→ARCHITECTURE.md 同形；`parse_front_matter` 已認一層巢狀對映；讀 06 節即見它承了 rev5 哪四個 `###`；不承襲的理由住「本該承接它的那一節」 |
| Q2 齊全性怎麼驗 | **A：生成器只排「缺／重複／未知鍵／形制」列與檔尾計數、永不 rc 1；波 3 出口人驗四項皆零** | 對齊啟動書 R2-F19「一次性 migrate-audit、非常駐閘」與閘數固定 12；不藏第 13 閘在 generate 內；日後刪鍵＝GT-01 逼重算、generated diff 多一列「缺」——看得見但不擋 |

### 0.2 工程判斷（回報備查；grill 可翻）

1. **射程 20 列**＝rev5 活書 12 個 `##`＋8 個 `###`（`###` 全在 §6 四個、§8 四個）。啟動書 §1 第 5 點與 §3.7 寫「每個 `###`」、§5 波 3 列寫「`###` 與 ADR」——取 §1／§3.7：`##` 一併入表是超集；rev5 ADR 依 D5 不入表。
2. **名冊住常數** `references.REV5_BLUEPRINT`（標題字面｜層｜所屬 §N）；一支 skip-if-absent 測試對凍結的 rev5 檔逐字核（`../fork260509-rev5/docs/arc42/ARCHITECTURE.md`；樹缺席即 skip、在場即必全等；bootstrap 已 die 級斷言其 SHA 7eab28a）。生成器不讀 repo 外檔、pre-commit 保持 hermetic。
3. **不承襲列住同號 rev6 節檔**（§3→03、§7→07、§10→10）；每個 rev5 `§N` 都有同號 rev6 節、無孤兒。
4. **值詞彙三種**：`承襲（一句說明）`／`隨刀：<刀類或憲法 §I.7 島>`／`不承襲：<理由>`；隨刀不寫刀號（刀序由首刀 brainstorm 定、D13）；值內不用 `[`（parse 會當清單）、鍵內不用 ASCII 冒號。
5. **`reference/agents.md` 生成不入本波**：`tools/orchestration/EXAMPLE-*.mjs` 的 `IMPL_OPTS`／`REVIEW_OPTS`／`FIX_OPTS` 是範本、rev6 尚無真刀 script；P-E2 名冊表＝角色×刻板型×產物進哪道閘（純人判斷欄）、模型／effort 只指針到 `*_OPTS` 常數不重抄（RL-0049）；生成表隨首個編排刀→BACKLOG 首條 BL-00001（T6 落帳、觸發＝首個含 Workflow script 的刀開分支）。
6. **C4-L1／L2「修訂」＝一致性校**：寫完 §3／§7 後對照兩圖（節點與邊零增減為預期）；§3.1 若引入 L1 沒有的外部系統則同批補圖與表。
7. **§12 系統術語**只收 rev5 治理詞與 rev6 工作區詞（傘狀 repo／雙身分子體／pin／短名長名／軌道／島／事件源／對照 stack／fork 源倉／基線／`rev6-inline` 標記）；流程詞不重複 RULES 名詞段；rev5 域詞四組（停用／軟刪、踢除／撤銷、鎖定、重設／修改）隨島 A～I 進場刀。
8. **§12 AI 術語（保留）**取 RAD-AI glossary 中 rev6 E 節與流程層實際用到的約 18 詞、中文改寫、標記欄＝`保留`（系統層尚無實例）／`流程層`（docs/process 已用）；不全譯 53 條（D15）。
9. **流程層判定三值**：對得上／部分／硬套；部分與硬套一律附一句理由；三處既定硬套照認定（糾纏 CACE↔rev5:L-032 症狀相似機制無關；監測之 wf-watchdog 守存活非漂移；E4 公平／可解釋／安全對 agent 不適用）。判定表＝本檔 §4。
10. **mermaid 範本一律放 text 圍欄（三反引號＋text）**：GT-10 圖表對賬掃全檔的 mermaid 圍欄（節點 ⊆ 同檔表首欄），範本節點不在表內；散文裡也不寫三反引號字面（GT-06 圍欄配對會被打歪）。
11. **零新增 `TODO(波 k)`**：延後內容一律現在式「隨 <刀類> 進場」句（避開 屆時／日後／將由）。
12. **Day-1 兩筆本波不動**（GT-03 需 feature_close、GT-08 需首條 LL）；若本波踩到值得立教訓的坑→`LL-00001` 與 `GT-08.lessons-absent` 解除同一 commit。
13. **不動 RULES 規則列**（RULES-VERSION `c7a137209e0e` 不變、EXAMPLE 版本字面不過期）；名詞段亦不動。
14. **一 Task 一 commit**；波標記 bump 在 T8、merge 之前；簿記在 merge 之後（CLAUDE.md §2 收刀序）。
15. **生成檔內連結**以 `_link(rel, "docs/generated/reference")` 產相對路徑（GT-06 連結腿掃 generated）。
16. **§4 頂層分解與 §5.1 白盒同物不同欄**（§4 寫職責與選型理由、§5.1 寫內含與介面）；rust-api 現＝源倉 Initial commit（僅 LICENSE）、§5.2／5.3 rust-api 側為「隨刀」句；base-web 第二層＝upstream 原樣目錄（`8be6f9ba`、fork-delta 零）。
17. **§1.1 缺口段**＝RAD-AI reference「Documentation Gaps Addressed」G1～G5 中文改寫成表（缺口｜一句｜rev6 承載）。

### 0.3 波次表縮編紀錄（不改啟動書；波 4 brainstorm 以此為準）

| 波 | 波 2 計畫剩餘欄 | 本波吸收 | 剩餘 |
|---|---|---|---|
| 3 | 流程層填實（51）；官方子節內容（28）；`reference/rev5-blueprint-map.md`；C4-L1／L2 修訂；C4-E 三檔（16）；12 名詞表 | 全部（C4-L1／L2 修訂＝一致性校） | `reference/agents.md` 生成→BL-00001（隨首個編排刀） |
| 4 | RAD-AI 23 筆取捨 ADR（附錄 A 進 ADR） | — | 同左 |

---

## Global Constraints

- 語言：一切書面產物 zh-TW；RAD-AI 子節名、欄位、檢核表列文字全部中文改寫、英文原名只出現在 frontmatter `rad_ai_map` 鍵（D15）；rev5 內容一律重打字消化、不整段複製（憲法 §I.5）。
- 面：**活書家族**＝docs/arc42（不含 decisions/）、docs/c4、docs/compliance、docs/process＝GT-10 形制面＋GT-06 時態面；本檔（史料面）不受形制與時態掃描，但 GT-06 連結腿掃全部 tracked *.md——本檔路徑一律反引號、不放 Markdown 連結。
- 時態（活書家族＋ops＋generated）：禁詞 待決／TBD／⏳／已完成／下一步（ERROR）；預告詞 屆時／日後／將由（WARN）；未來式一律改寫成現在式事實或「隨 <刀類> 進場」句。
- 佔位：`*[`、五個以上底線、`- [ ]`、裸 `[Xxx]` 四腿零殘留；**本波出口 `TODO(波 3)` 歸零、不新增 `TODO(波 4)`**（現在波 3；bump 4 前殘留即 95 處全紅）。
- 流程層：每個 `###` 後第一個非空行必含「類比張力：」（GT-10）；子節正文零 `TODO(波 k)` 才計入 RAD-AI-MAP 填實。
- 圖表：mermaid id 只用 `[A-Za-z0-9_]`、label 雙引號＝同檔表格首欄字面、label 與邊文字皆不含 `()[]{}`、不用 subgraph；`C4-L2` 節點 ⊇ compose 17 services；範本用 text 圍欄（三反引號＋text）。
- 前代引用：一律 `rev5:`／`rev4:` 前綴（B-NNN／L-NNN／ADR 0NNN／LintNN／刀名）；`000-` 家族除外。
- 每個事實只有一個家：埠只在 `reference/ports.md`；十三機密表只在 `deploy/secrets/README.md`；標題只在 H1；摘要只在 frontmatter；閘名冊只在 `GATES.md`（活書引閘用指針不重抄）；模型／effort 只在 `*_OPTS`。
- frontmatter 只用 `parse_front_matter` 認得的形：頂層 `key: value`、單行清單 `[E1]`、一層巢狀對映（`key:` 空值＋兩空格縮排子鍵）；巢狀鍵不含 ASCII 冒號、不加引號；值不含 `[`。新鍵 `rev5_blueprint` 只住 `docs/arc42/NN-*.md`。
- 機器生成檔首行 `common.GENERATED_HEADER`；名冊 GENERATED_FILES 擴為 **11** 件；`docs/generated/**` 只可含名冊檔；新檔先 `git add` 再 generate、再 lint（lint 面＝tracked，未 add 的新檔＝假綠）。
- 工具：只用 python 標準庫；`tools/docsync/` 邏輯行 ≤4,000（現 1,981）；閘數恆 12、不加閘、不在 generate 內藏斷言；新生成器一正一反自證＋名冊測試更新。
- git：分支 `000-w3-book-fill`；commit 訊息 zh-TW、含反引號一律 `git commit -F <暫存檔>`；每步後以 `git rev-parse HEAD`／`git status --porcelain` 自證；merge 需 user 當次同意；不 push；rev5 樹絕不寫入。
- 環境：/mnt/d drvfs——每次 Bash 自 repo 根起手（`cd tools` 會持久）；跑過 docker bind mount 後同 shell 先重新 `cd`；`set -e` 靠不住、以工件自證。
- 單元收尾序（CLAUDE.md §2）：③落帳（BACKLOG／LESSONS／ADR）早於⑤generate；每 Task 末＝`python3 tools/docsync generate` → `git add docs/generated docs/arc42/ARCHITECTURE.md docs/ops/LESSONS.md` → lint 全綠 → 一顆 commit。

---

## 檔案結構

```
tools/docsync/references.py               REV5_BLUEPRINT（20 列名冊）、BLUEPRINT_DISPOSITIONS、gen_rev5_blueprint_map；GENERATED_FILES 11；compute_generated 加一鍵（T1）
tools/docsync/tests/test_references.py    TestBlueprintMap：一正一反＋名冊 11＋skip-if-absent 對 rev5 檔核名冊（T1）
docs/arc42/decisions/ADR-00006-rev5-blueprint-map-frontmatter.md   accepted（T1）
docs/generated/reference/rev5-blueprint-map.md   生成（T1 首生＝20 缺；T4 後四項皆零）
README.md                                 generated 行加 rev5-blueprint-map；「想知道 X 看 Y」加一列（T1）
docs/arc42/01…04-*.md                     12 處 TODO 填實＋frontmatter rev5_blueprint 4 鍵（T2）
docs/arc42/05…08-*.md                     10 處 TODO 填實＋rev5_blueprint 11 鍵（§5 一、§6 五、§8 五）（T3）
docs/arc42/10…12-*.md、07、09             6 處 TODO 填實＋rev5_blueprint 5 鍵（§7、§9、§10、§11、§12）（T4）
docs/c4/C4-E1／E2／E3-*.md                16 處 TODO 填實；C4-L1／L2 一致性校（T5）
docs/process/P-E1～P-E4-*.md              22 子節類比張力真句（T6）＋docs/ops/BACKLOG.md 首條 BL-00001（T6）
docs/process/P-E6～P-E8、P-C4-E3-*.md     29 子節類比張力真句（T7）→ TODO(波 3) 歸零
docs/ops/NOTES.md                         波標記 4＋現況／下一步（T8）
docs/ops/events.jsonl                     misc 收單事件（merge 後簿記）＋perf 事件（隨下一顆）
```

---

## 1. 藍本對照（rev5 活書 20 標題 → rev6 去處）

### 1.1 名冊（`references.REV5_BLUEPRINT`；字面取自凍結 rev5 檔、T1 測試逐字核）

| # | rev5 標題字面 | 層 | 所屬 |
|---|---|---|---|
| 1 | §1 簡介與目標 | `##` | 1 |
| 2 | §2 約束 | `##` | 2 |
| 3 | §3 系統脈絡 | `##` | 3 |
| 4 | §4 解法策略 | `##` | 4 |
| 5 | §5 Building blocks | `##` | 5 |
| 6 | §6 Runtime | `##` | 6 |
| 7 | 信任錨與 IP 存取閘 | `###` | 6 |
| 8 | 會話狀態機（sys_token） | `###` | 6 |
| 9 | 登入失敗節流三區（帳號維＋來源維） | `###` | 6 |
| 10 | 使用者域斷權與密碼三入口（007 落地） | `###` | 6 |
| 11 | §7 部署 | `##` | 7 |
| 12 | §8 橫切概念 | `##` | 8 |
| 13 | fork-delta 接線現況（base-web） | `###` | 8 |
| 14 | 資料慣例 | `###` | 8 |
| 15 | API 慣例 | `###` | 8 |
| 16 | 授權慣例 | `###` | 8 |
| 17 | §9 架構決策 | `##` | 9 |
| 18 | §10 品質要求 | `##` | 10 |
| 19 | §11 風險與技術債 | `##` | 11 |
| 20 | §12 名詞表 | `##` | 12 |

### 1.2 處置表（＝各節檔 frontmatter `rev5_blueprint` 的值字面；T2～T4 逐檔落）

| rev5 標題 | 住 rev6 檔 | 值（字面） |
|---|---|---|
| §1 簡介與目標 | 01 | `承襲（能力級／明確不做／建置狀態改寫為 rev6 現況）` |
| §2 約束 | 02 | `承襲（技術棧／拓樸／環境／上游關係四條＋rev6 新約束）` |
| §3 系統脈絡 | 03 | `不承襲：rev5 空節（該節自述尚無內容）；rev6 §3 自 C4-L1 起手` |
| §4 解法策略 | 04 | `承襲（五條策略對 rev6 仍真、上位＝憲法 §I.1～I.5）` |
| §5 Building blocks | 05 | `隨刀：rust-api 骨架刀（workspace members 與管線形；rust-api 現為源倉 Initial commit）；本波只寫傘狀層白盒` |
| §6 Runtime | 06 | `承襲（方針段：不變式凍結面住憲法 §I.7、本節只寫 as-built）；情境隨島進場` |
| 信任錨與 IP 存取閘 | 06 | `隨刀：憲法 §I.7 島 F 進場刀` |
| 會話狀態機（sys_token） | 06 | `隨刀：憲法 §I.7 島 A～D 進場刀（auth 會話）` |
| 登入失敗節流三區（帳號維＋來源維） | 06 | `隨刀：憲法 §I.7 島 E 進場刀（帳號維）；來源維隨島 F` |
| 使用者域斷權與密碼三入口（007 落地） | 06 | `隨刀：憲法 §I.7 島 I 進場刀（使用者域）` |
| §7 部署 | 07 | `不承襲：rev5 空節；rev6 §7 自 C4-L2 與 reference/ports 起手` |
| §8 橫切概念 | 08 | `承襲（四子節形制）` |
| fork-delta 接線現況（base-web） | 08 | `承襲（指針形：規則面承 rev5 FORK-DELTA-WIRING、接線 as-built 隨 base-web 各刀重生）` |
| 資料慣例 | 08 | `隨刀：schema 基線刀（archetype 四變體與成對條款已入憲法 §I.6、本波留指針）` |
| API 慣例 | 08 | `隨刀：wire 地基刀（信封、碼表、i64 守衛已入憲法 §I.3；部分更新三態承 rev5:ADR 0023 隨刀重審）` |
| 授權慣例 | 08 | `隨刀：授權治理刀（憲法 §I.7 島 G／I；判定單點與 DB-fresh 已入憲法 §I.2、本波留指針）` |
| §9 架構決策 | 09 | `承襲（decisions/ 一決策一檔＋DECISIONS-INDEX 指針；波 2 落地）` |
| §10 品質要求 | 10 | `不承襲：rev5 空節；rev6 §10 自 §1.2 品質目標展開、情境隨島進場` |
| §11 風險與技術債 | 11 | `承襲（BACKLOG／LESSONS 指針；rev6 加 ※11.1 風險）` |
| §12 名詞表 | 12 | `承襲（治理詞入 §12 系統術語；域詞四組隨島 A～I 進場刀）` |

### 1.3 生成檔形（`docs/generated/reference/rev5-blueprint-map.md`）

```
<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# reference/rev5-blueprint-map — rev5 活書藍本對照表（一次性 migrate-audit 面；ADR-00006）

名冊＝rev5 活書 `../fork260509-rev5/docs/arc42/ARCHITECTURE.md`（凍結 SHA 7eab28a）的 12 個 `##`＋8 個 `###`（`references.REV5_BLUEPRINT`）；去處＝`docs/arc42/NN-*.md` frontmatter `rev5_blueprint`（鍵＝rev5 標題字面、值＝承襲（…）／隨刀：…／不承襲：…）。未宣告列「缺」、多檔宣告標「重複」、鍵不在名冊列「未知鍵」、值不以三詞起頭標「形制」；四項皆零＝藍本對照表零缺（波 3 出口判準）。

| rev5 標題 | 層 | rev6 去處 | 處置 |
|---|---|---|---|
| §1 簡介與目標 | ## | <連結：文字＝01-introduction-and-goals.md、目標＝../../arc42/01-introduction-and-goals.md> | 承襲（…） |
| 信任錨與 IP 存取閘 | ### §6 | <連結：06-runtime-view.md> | 隨刀：… |
| 資料慣例 | ### §8 | 缺 | 缺 |
| （未知鍵列排在名冊列之後） | 未知鍵 | <連結：宣告它的檔> | 未知鍵 |

缺：1｜重複：0｜未知鍵：0｜形制：0
```

---

## 2. arc42 28 處內容規格（來源＝rev5 活書同節；抄形不抄字；「不帶回」欄＝rev6 拍板已推翻或尚未為真者）

| 檔 | TODO 位 | 寫什麼 | 來源與指針 | 不帶回 |
|---|---|---|---|---|
| 01 | §1.1 需求概覽（2 處） | ①定位一段：rev6-admin＝管理後台；前端 fork 自 soybean-admin（Vue3／TS／naive-ui、基線 upstream `example` tip `8be6f9ba`、D14）、後端 Rust 全新寫（憲法 §I.5）；rev1～rev5 五代、本代自 rev5 交接包重起（ADR-00002）。②能力級（base-web 為權威、範圍不縮減；憲法 §I.1）：使用者／角色／選單管理、casbin RBAC（menu／button）、認證與 session 治理、系統設定、審計（操作／存取／登入嘗試）、IP 存取控制、觀測層。③明確不做：多租戶、對外開放 API、行動端。④目前建置狀態：文件地基三波（治理工具、活書骨架、填實）；應用碼零刀（rust-api＝源倉 Initial commit、base-web＝upstream 原樣）；各域隨刀建置、刀序由首刀 brainstorm 定（D13）。⑤缺口段表：G1～G5（缺口｜一句中文改寫｜rev6 承載＝E1～E8 節／C4-E 三檔／compliance 兩檔／§9.1 E5 形／P-E2、P-E3 銜接子節） | rev5 §1；RAD-AI reference「Documentation Gaps Addressed」 | rev5 建置狀態（001～008 各刀）、「rev4 治理終態」措辭 |
| 01 | §1.2 品質目標 | 表（目標｜動機｜守門）五列：安全（授權 DB-fresh、fail-closed 方向、機密不入版控；憲法 §I.2／§I.7、GT-07）；契約守恆（typings 為裁判、wire 契約機器化；憲法 §I.3）；可重現（傘狀 pin、兩段式 commit、bootstrap 幂等；GT-02）；文件與碼零漂移（機器優先文件觀；GT-01／GT-12）；UI 與 rev5 一致（CDP 對照驗收；CLAUDE.md §7） | 憲法 §I、CLAUDE.md §7、啟動書 §4.3 | — |
| 01 | §1.3 利害關係人 | 表（角色｜期望｜接觸面）：管理員（Super／Admin／User；UI）、營運者（dev stack／RUNBOOK）、開發者＝user（拍板、人審；憲法 §I.8）、AI 代理（流程層；`docs/process/`）、upstream soybean-admin（rebase 來源、單向） | CLAUDE.md §7、憲法 §I.8、§III | — |
| 02 | 技術約束 | 清單：技術棧（前端 Vue3／TS／naive-ui／vite／pnpm；後端 Rust axum／sea-orm／PostgreSQL／Redis／casbin；docker compose；工作區工具 python3 標準庫）；host 無 rust toolchain、build／test 容器內且 serial；host 埠世代 3xxxx（ADR-00001、真表 `reference/ports.md`）；rev5 對照 stack 2xxxx 併行；.gitattributes 強制 LF；zh-TW 書面 | rev5 §2 技術棧／環境；CLAUDE.md §1／§6／§7 | macOS 工作環境（rev6 只在 WSL2） |
| 02 | 組織約束 | 清單：傘狀 repo＋兩個雙身分子體（worktree／gitlink）；fork 源倉住 repo 根、必須保留；rev5 唯讀凍結 SHA（外層 7eab28a／base-web 9833308／rust-api 92919b9；ADR-00002）；push／merge 需人審（憲法 §I.8）；單一開發者＋AI 代理（流程層） | rev5 §2 repo 拓樸；ADR-00002；憲法 §I.8 | rev5 分支長名 |
| 02 | 慣例約束 | 清單：憲法 §III 軌道（`rev6-inline` token、修改型帶 `原行:`）；前代引用 `rev5:` 前綴（RL-0046）；每個事實一個家（RL-0049）；時態分離（RL-0048）；RAD-AI 中文改寫（D15）；波標記＝NOTES 首行 | 憲法 §III、RULES | rev5-inline token |
| 03 | §3.1 業務脈絡 | 一段＋表（對象｜互動）：管理員經瀏覽器操作後台（能力級指 §1.1）；SMTP 寄信（dev＝mailpit）；無對外 API、無第三方登入、無行動端 | C4-L1 表；§1.1 | — |
| 03 | §3.2 技術脈絡 | 保留既有指針句、去 TODO；加技術介面表（介面｜協定｜端）：管理員↔front-nginx（HTTPS）、front-nginx→base-web／rust-api、rust-api→SMTP（dev 1025）；對照 stack 2xxxx＝驗收基準、不屬系統脈絡 | C4-L1／L2 表；CLAUDE.md §7 | — |
| 04 | 技術選擇 | 五條 rev6 版：fork 自 upstream `example` tip 衍生＋rust-api 全新寫受控參照（憲法 §I.1／§I.5）；casbin RBAC DB-first（憲法 §I.2）；wire 契約機器化（憲法 §I.3）；縱切刀工作流 SDD＋TDD（憲法 §I.4）；機器優先文件觀＋人審機器閘（RL-0049、憲法 §I.8） | rev5 §4 五條 | rev5 `tools/docs-sync.py`、`rev5-inline` |
| 04 | 頂層分解 | 表（區塊｜職責｜真源）：base-web／rust-api／deploy（compose 三檔、secrets）／tools（docsync、orchestration、bootstrap）／docs（活書家族、ops、generated） | README 樹；CLAUDE.md §1 | — |
| 04 | 品質目標達成法 | 表（§1.2 目標｜手段｜守門）五列，一一對應 §1.2 | §1.2 | — |
| 05 | §5.1 整體系統白盒 | 表（區塊｜內含｜介面）：base-web（upstream 分層、fork-delta）｜rust-api（隨刀）｜deploy（17 services、secrets 13 支）｜tools｜docs；介面＝gitlink pin、compose service、docsync 名冊 | §4 頂層分解、C4-L2 | rev5 crate 名冊 |
| 05 | §5.2 第二層 | base-web＝upstream 原樣目錄一覽（views／router／store／service／typings 等頂層目錄、fork-delta 零）；rust-api＝隨 rust-api 骨架刀進場（workspace members 隨刀） | `base-web/src`、`rust-api/` | rev5 §5 模組拓樸 |
| 05 | §5.3 第三層 | 一句：隨各域刀進場、本節以指針列各刀 spec | — | — |
| 06 | §6.1 執行情境 | 方針段（不變式凍結面住憲法 §I.7、本節只寫 as-built 執行形：模組落點、常數實值、欄與鍵名；凍結條文只給指針不複述）＋情境格式（標題｜參與者｜步驟｜守門）＋「目前零情境」句 | rev5 §6 導言 | rev5 四個 ### 內容 |
| 07 | §7.1 基礎設施第一層 | 保留指針句、去 TODO；加：dev stack 起法指針 RUNBOOK §1／§2；兩 stack 併行（2xxxx 對照、3xxxx rev6）；profiles 指針 RUNBOOK §3 | RUNBOOK、CLAUDE.md §7 | — |
| 07 | §7.2 基礎設施第二層 | compose 三檔組合形（基底 yml＋dev 疊加＋example 對照）、profiles obs／metrics／jobs、named volume 前綴（RUNBOOK §5）、TLS 終端與 `/api` 前綴（憲法 §II #3）、部署 checklist 指針 §16 | compose 三檔、RUNBOOK | — |
| 08 | §8.1 資料慣例 | 指針段：archetype 四變體與成對條款＝憲法 §I.6；schema 基線、三閘、演進帳隨 schema 基線刀進場（承 rev5:ADR 0006／0007 形、隨刀重審） | rev5 §8 資料慣例 | memo 欄家族、ORM 關聯紀律細節 |
| 08 | §8.2 API 慣例 | 指針段：信封三欄、13 碼矩陣、i64 守衛＝憲法 §I.3；部分更新三態（承 rev5:ADR 0023）隨 wire 地基刀重審 | rev5 §8 API 慣例 | 序列化 lint 檔名 |
| 08 | §8.3 授權慣例 | 指針段：判定單點與 DB-fresh＝憲法 §I.2；拒絕語意、no-escalation 兩射程、三維授權治理隨島 G／I 進場刀 | rev5 §8 授權慣例 | rev5 ADR 0022／0054～0056 細節 |
| 08 | §8.4 fork-delta 軌道 | 保留既有句、去 TODO；加一句：機器守 fork-delta-lint 隨子庫刀進場 | 憲法 §III | — |
| 10 | §10.1 品質需求概覽 | 表（屬性｜§1.2 目標｜量測｜守門）五列 | §1.2 | — |
| 10 | §10.2 品質情境 | 情境格式（刺激｜環境｜回應｜量測）＋「目前零情境」句＋島清單指針（憲法 §I.7 承襲指針表 A～J） | 憲法 §I.7 | — |
| 11 | ※11.1 風險 | 表（風險｜觸發｜守門）：upstream rebase 衝突（軌道制、`rev6-inline`）；rev5 對照樹被誤寫（bootstrap 斷言）；源倉只在本機（bootstrap 重建）；docsync 邏輯行預算（STATE 報表）；Day-1 豁免到期 | CLAUDE.md、GATES | — |
| 11 | ※11.2 技術債 | 保留指針句、去 TODO；結構性債現況：Day-1 兩筆（GT-03／GT-08）；EXAMPLE-*.mjs 版本字面耦合 RULES-VERSION；`_sk_head*.js`／`_sk_main*.js` 多份變體 | GATES、tools/orchestration | — |
| 12 | 系統術語 | 表（術語｜定義｜出處）§0.2-7 十一詞 | rev5 §12、CLAUDE.md、憲法 | rev5 域詞四組 |
| 12 | AI 術語（保留） | 表（術語｜定義｜標記）約 18 詞：非確定性邊界／確定性區域／資料漂移／概念漂移／串聯漂移／漂移偵測／模型新鮮度／模型陳舊／糾纏（CACE）／邊界侵蝕／隱藏回饋迴圈／資料血緣／特徵庫／模型卡／資料卡／人在迴圈／信心規格／降級輪廓／fallback／再訓練觸發／回退政策／品質閘／雙生命週期／Annex IV | RAD-AI glossary（中文改寫） | 全譯 |

---

## 3. C4 16 處內容規格

| 檔 | 子節 | 寫什麼 |
|---|---|---|
| C4-E1 | 刻板型定義 | 表（中文名｜簡寫｜意涵｜rev6 目前實例）五列：ML 模型／資料管線／特徵庫／監測／人在迴圈；實例欄＝目前無（流程層對應見 P-E2） |
| C4-E1 | Mermaid 慣例 | 規則：節點 label 不變（守 GT-10 圖表對賬）、刻板型以 `classDef` 五類＋`:::` 標注、同檔表加「刻板型」欄；不用 `()[]{}`、不用 subgraph |
| C4-E1 | 標註準則 | 何時標（元件含 AI 推論／管線／特徵庫／監測／人審）、標在 L2、L1 只標邊界、與 C4-E3 邊界的關係 |
| C4-E1 | 範本 | text 圍欄一段 mermaid 範本（classDef 五類＋一節點示例）＋表列範本 |
| C4-E2 | 資料源清冊 | 「目前無 AI 資料源」句＋表欄定義（來源｜型｜擁有者｜新鮮度｜隱私級）；系統資料源＝postgres／redis／compose 設定（指 C4-L2 表） |
| C4-E2 | 血緣圖 | 規則：不另畫、疊加於 C4-L2、邊文字「血緣：」前綴 |
| C4-E2 | 血緣明細 | 表欄定義（階段｜輸入｜輸出｜schema 期望｜轉換） |
| C4-E2 | 新鮮度需求 | 規則：快變事實住 `docs/generated/reference/`、重算時點＝每 commit（GT-01） |
| C4-E2 | 隱私流 | 一句：稽核表欄位與保留期隨 schema 基線刀進場（啟動書 §3.3 列為真內容） |
| C4-E2 | schema 登錄 | 一句：`reference/schema.md` 隨 schema 基線刀進場、版本＝migration 序 |
| C4-E3 | 邊界總覽 | 系統本體全確定性；非確定性只在流程層（指 P-C4-E3）；mermaid 一圖（節點 ⊆ 表） |
| C4-E3 | 邊界介面 | 目前無（系統）；規則：介面表欄（介面｜輸入型｜輸出型｜三性質契約） |
| C4-E3 | 信心門檻 | 目前無；規則：每模型一列（模型｜指標｜門檻｜低於門檻的行為） |
| C4-E3 | 降級行為 | 目前無；規則：降級輪廓五型（規則預設／快取末值／人工升級／優雅降級／斷路器） |
| C4-E3 | 傳播規則 | 目前無；規則：非確定輸出進確定區前必經驗證點 |
| C4-E3 | 測試含意 | 系統測試全確定性（contract test、fault-injection 隨刀）；AI 進場時的統計測試規則 |

C4-L1／L2 一致性校（T5）：§3.1／§3.2／§7.1／§7.2 寫完後對照兩圖與表，節點與邊零增減；有增減即同批改圖並重跑 lint（GT-10 對賬）。

---

## 4. 流程層 51 子節判定表（判定｜rev6 對應機制與真源；「類比張力：」首句以此為準）

**P-E1 邊界劃定**

| 子節 | 判定 | rev6 對應（真源） |
|---|---|---|
| AI 元件清冊 | 對得上 | 名冊＝主線（Claude Code session）／implementer／review／fix（Workflow agent）／CDP 代理（`tools/orchestration/cdp.mjs`）；三支 hook（`.claude/hooks/`）與 `tools/wf-watchdog.py` 是確定性守門、列入為畫邊界；欄＝角色｜承載｜產物｜進哪道閘 |
| 系統邊界圖 | 對得上 | mermaid：user⇄主線→三角色 agent；閘節點＝pre-commit／PreToolUse hook／人審；節點 ⊆ 同檔表首欄 |
| 四段邊界契約 | 對得上 | 輸出型＝生成型（報告＋diff）；信心規格＝lint 全綠＋review 零 blocker（非數值）；換版頻率＝事件觸發（RULES-VERSION 變、換模 commit）、非排程；fallback＝人工升級（blocked／done_with_escalation；六件套④） |
| 失效模式 | 對得上 | hook 註冊斷裂→靜默放行（GT-09）；stall／runaway（看門狗、保險絲）；agent 自報成功（不採信回報、逐項 grep）；規則塊過期（PreToolUse 對賬） |
| 外部 AI 依賴 | 對得上 | Anthropic 託管模型（id 住 `*_OPTS`、無 SLA、換版由供應商）；第三方 skills（`.claude/skills/`）；影響面＝換模＝一次改常數的 commit |

**P-E2 代理名冊**

| 子節 | 判定 | rev6 對應（真源） |
|---|---|---|
| 模型清冊表 | 部分 | 表＝角色×刻板型（主線／implementer／review／fix／CDP＝ML 模型；看門狗＝監測；user 拍板＝人在迴圈；hook＝無）×產物進哪道閘；模型／effort 指針 `EXAMPLE-*.mjs` 三組 `*_OPTS`、不重抄；生成表隨首個編排刀（BL-00001） |
| 逐模型明細 | 硬套 | 託管 LLM 無訓練資料／指標／owner 可記；明細只剩 model id、effort、換模紀錄（`*_OPTS` 的 git log）；附理由 |
| 與模型卡的銜接 | 硬套 | 模型卡＝供應商公開文件、rev6 不自寫；一句指針 |
| 與模型登錄工具的銜接 | 硬套 | 無 MLflow 類工具；「登錄」＝`*_OPTS` 常數＋git 歷史；附理由 |

**P-E3 文件管線**

| 子節 | 判定 | rev6 對應（真源） |
|---|---|---|
| 管線總覽圖 | 對得上 | brainstorm→specify→clarify→plan→tasks→analyze→Workflow（implementer→review→fix）→final review→merge→簿記→generate；節點 ⊆ 表 |
| 管線清冊表 | 對得上 | 每階段：輸入｜輸出｜承載（skill／命令／工具）｜閘 |
| 品質閘 | 對得上 | 三層：pre-commit 十二閘（指針 `docs/generated/GATES.md`）／PreToolUse hook（RULES-VERSION 對賬）／review 輪（findings 三分流 RL-0073） |
| 特徵庫記載 | 硬套 | 無特徵庫；最近類比＝`rules emit` 規則塊烤入 prompt（版本化輸入）；附理由 |
| 回饋迴圈 | 對得上 | LESSONS→RULES 晉升→`rules emit`→prompt（啟動書 §3.6）；findings→修／BL／ADR；events→STATE 三指標 |
| 與資料卡的銜接 | 硬套 | 無資料卡；類比＝`docs/ops/reference-src/` 半自動快照（隨 schema 刀）；附理由 |

**P-E4 負責任代理**

| 子節 | 判定 | rev6 對應（真源） |
|---|---|---|
| 負責任 AI 關注矩陣 | 對得上 | 六關注×（適用｜承載｜守門）；三適用、三不適用附理由 |
| 公平 | 硬套 | agent 產物不對人分類、無人群決策；附理由 |
| 可解釋 | 硬套 | 託管模型內部不可解釋；替代＝產物可追溯（findings file×summary、收單訊息列處置）歸「透明」 |
| 人類監督 | 對得上 | 憲法 §I.8：merge／push 當次同意、拍板級親決、review 只讀；一題一問 |
| 透明 | 對得上 | events.jsonl 留痕、commit 尾 Co-Authored-By 與 Claude-Session、收單訊息逐項處置 |
| 隱私 | 對得上 | 機密不入 prompt／chat／tracked 檔（GT-07、RL-0054）；SECRETS_DIR＋age；rev5 樹唯讀 |
| 安全 | 硬套 | RAD-AI 安全＝人身／物理；agent 面對應＝破壞性操作硬禁令（CLAUDE.md §6）已歸人類監督；附理由 |

**P-E6 品質情境**

| 子節 | 判定 | rev6 對應（真源） |
|---|---|---|
| 品質屬性定義 | 對得上 | 四屬性：review 精準度（誤報率）、閘可見性（恆綠風險）、stall 恢復、規則烤入一致性；各附量測 |
| 模型新鮮度 | 部分 | 無自動陳舊偵測；新鮮度＝供應商版本＋換模 commit；附理由 |
| 漂移容忍 | 部分 | rev6 漂移＝確定性零容忍（GT-01／GT-12／RULES-VERSION 對賬）、非統計容忍帶；附理由 |
| 可解釋 | 部分 | findings 帶 file×summary、三分流去處可查；模型內部不可解釋 |
| 公平 | 硬套 | 同 P-E4；附理由 |
| 強健 | 對得上 | stall／runaway／blocked 升級／不收斂偵測（六件套③⑤）；harness 六案 |
| 情境格式 | 對得上 | 刺激｜環境｜回應｜量測＋兩條實例（review 連兩輪同 blocker→判不收斂；hook 擋缺 RULES-VERSION 的 script） |
| 跨元件情境 | 對得上 | 規則列改一行→RULES-VERSION 變→`_sk_rules.js` 重算→EXAMPLE 版本字面過期→hook 擋發射 |

**P-E7 代理債務登記**

| 子節 | 判定 | rev6 對應（真源） |
|---|---|---|
| 邊界侵蝕 | 對得上 | agent 動允許清單外檔（六件套⑥）、review 寫檔（憲法 §I.8 禁）；種子＝RULES 中 source 為 rev5:L 之相關列（指針、不重抄） |
| 糾纏 | 硬套 | CACE（改一處全變）↔ rev5:L-032 症狀相似機制無關（確定性連動、非模型糾纏）；附理由 |
| 隱藏回饋迴圈 | 部分 | 顯式迴圈＝LESSONS→RULES→prompt；隱藏者＝agent 讀自己前輪產物；防法＝review 附前輪駁回清單（RL-0071） |
| 資料依賴債 | 硬套 | 無訓練資料；類比＝prompt 依賴 tracked 檔（規則塊、tasks）且顯式版本化；附理由 |
| 管線債 | 對得上 | 編排膠水：`_sk_head*.js`／`_sk_main*.js` 多份變體、EXAMPLE 版本字面耦合 |
| 設定債 | 對得上 | `*_OPTS` 散在各 script、保險絲值須自斷言不得手挑（rev5:L-068）、effort 值無單一家 |
| 模型陳舊 | 部分 | model id 釘死；供應商下架＝陳舊；無偵測、換模＝人決 |
| 登記條目格式 | 部分 | 九欄定義（id｜類別｜徵狀｜來源｜影響面｜觸發｜處置｜去處｜狀態）；條目住 BACKLOG（governance）／LESSONS、本檔不另設登記簿（RL-0049） |
| 債務總覽板 | 部分 | 總覽＝`docs/generated/STATE.md` 三指標；不另設板 |
| 覆審節奏 | 對得上 | 條件觸發：收刀 final holistic review、不定期獨立輪（`docs/reviews/`）、Day-1 到期紅；非定期 |

**P-E8 代理營運**

| 子節 | 判定 | rev6 對應（真源） |
|---|---|---|
| 監測 | 部分 | wf-watchdog 守存活（stall／runaway）非漂移偵測；perf 引信（`close_bookkeeping` 牆鐘、`reference/perf.md`）；lint 漂移閘 |
| 再訓練政策 | 硬套 | 無訓練；類比＝換模（`*_OPTS`）與規則層更新（LESSONS 晉升）的觸發；附理由 |
| 部署策略 | 部分 | 規則層版本進 prompt 的發布形（`rules emit`＋PreToolUse 對賬）；無金絲雀／影子 |
| 回退政策 | 對得上 | 治理閘改壞→git revert 該顆＋generate 重算；規則列回退→RULES-VERSION 重算＋EXAMPLE 版本字面同批 |
| 事故應變 | 對得上 | blocked／done_with_escalation 升級路徑；stall→TaskStop→修 script→resume（RL-0010）；落帳 LESSONS |

**P-C4-E3 材質邊界**

| 子節 | 判定 | rev6 對應（真源） |
|---|---|---|
| 邊界總覽 | 對得上 | 三材質（Claude 執筆／機器生成／user 拍板）＝非確定性邊界；mermaid 一圖＋表 |
| 邊界介面 | 對得上 | 三種：檔案（人寫 vs generated）、commit（pre-commit）、AskUserQuestion（拍板） |
| 信心門檻 | 部分 | 無數值信心；門檻＝lint 綠＋review 零 blocker＋人審三合一 |
| 降級行為 | 對得上 | blocked／escalation、hook 擋發射、Day-1 到期紅 |
| 傳播規則 | 對得上 | 非確定產物只經閘入 default；generated 永不手改（GT-01）；agent 不 push／merge（憲法 §I.8） |
| 測試含意 | 對得上 | harness 六案（`tools/orchestration/harness-test.mjs`）、docsync 自測、破壞性自證（RL-0005） |

首句形：`類比張力：<對得上｜部分｜硬套>——<一句>`；正文接表或清單；子節內零 `TODO(波 k)`。

---

## 5. 寫作紀律（閘對照；執行時每檔寫完先跑 `python3 tools/docsync lint`）

| 閘 | 本波會撞到的腿 | 防法 |
|---|---|---|
| GT-06 | 時態禁詞（待決／TBD／⏳／已完成／下一步）與預告詞（屆時／日後／將由）；活書相對連結目標必存在；deep-link 禁 | 延後內容寫「隨 <刀類> 進場」；連結只指已存在檔；路徑反引號 |
| GT-05 | 新散文裡 rev5 編號（B-NNN／L-NNN／ADR 0NNN／LintNN／刀名） | 一律 `rev5:` 前綴；`000-` 家族除外 |
| GT-10 | 類比張力首句；`###` 標題改動→frontmatter `rad_ai_map` 值同步；mermaid 節點 ⊆ 表首欄；佔位四腿；`TODO(波 3)` 現合法、bump 4 即紅 | 不改任何 `###` 字面；範本用 text 圍欄；寫完 grep `TODO(波 3)` |
| GT-01 | 名冊 11、每檔改動皆重算 | 每 Task 末 generate＋`git add docs/generated docs/arc42/ARCHITECTURE.md docs/ops/LESSONS.md` |
| GT-09 | README 樹與實檔集 | T1 同批改 README generated 行 |
| GT-12 | 閘數 12、名冊同源 | 不加閘、不動 gates.py |
| GT-07 | 機密樣式 | 內容不含任何機密字面；`alert_webhook_url` 只提名不提值 |

---

## 6. Tasks

### Task 1: 藍本工具——名冊常數＋生成器＋名冊 11＋測試＋ADR-00006＋README

**Files:**
- Modify: `tools/docsync/references.py`（`REV5_BLUEPRINT`、`BLUEPRINT_DISPOSITIONS`、`gen_rev5_blueprint_map(ctx)`；`GENERATED_FILES` 加 `docs/generated/reference/rev5-blueprint-map.md`；`compute_generated` 加一鍵）、`README.md`（generated 行加 `rev5-blueprint-map`；「想知道 X 看 Y」加「rev5 活書哪節去了哪→`docs/generated/reference/rev5-blueprint-map.md`」）
- Create: `docs/arc42/decisions/ADR-00006-rev5-blueprint-map-frontmatter.md`（accepted；背景／驅動因子／替代案（B 人寫表、C tmp 腳本、Q2-B 自斷言）／決定六條／後果／翻案觸發器）
- Test: `tools/docsync/tests/test_references.py`（`TestBlueprintMap`）

**Interfaces:**
- Produces: `references.REV5_BLUEPRINT: tuple[tuple[str, str, int], ...]`（20 列）、`references.gen_rev5_blueprint_map(ctx) -> str`、`GENERATED_FILES` 長度 11。
- Consumes: `_book_meta(ctx, "docs/arc42/")`、`RE_CHAPTER`、`_link`、`common.GENERATED_HEADER`、`tests.test_book_ids.stub`。

- [ ] **Step 1: 寫失敗測試**

```python
class TestBlueprintMap(unittest.TestCase):
    """rev5 藍本對照表（ADR-00006）：frontmatter rev5_blueprint → 表；缺／重複／未知鍵／形制只排列、不拋錯；名冊對凍結 rev5 檔逐字核。"""
    REV5_BOOK = os.path.join(ROOT, "..", "fork260509-rev5", "docs", "arc42", "ARCHITECTURE.md")

    def test_map_lists_defects_and_never_raises(self):
        files = {"docs/arc42/01-introduction-and-goals.md": "---\nsection: 1\nrev5_blueprint:\n  §1 簡介與目標: 承襲（一句）\n---\n# §1\n",
                 "docs/arc42/06-runtime-view.md": "---\nsection: 6\nrev5_blueprint:\n  信任錨與 IP 存取閘: 隨刀：憲法 §I.7 島 F 進場刀\n  資料慣例: 亂寫\n  不存在的標題: 承襲（x）\n---\n# §6\n",
                 "docs/arc42/08-crosscutting-concepts.md": "---\nsection: 8\nrev5_blueprint:\n  §1 簡介與目標: 承襲（重複宣告）\n---\n# §8\n"}
        out = references.gen_rev5_blueprint_map(stub(files))
        self.assertTrue(out.startswith(common.GENERATED_HEADER))
        self.assertIn("| §2 約束 | ## | 缺 | 缺 |", out)
        l01 = references._link("docs/arc42/01-introduction-and-goals.md", references.BLUEPRINT_DIR)
        l06 = references._link("docs/arc42/06-runtime-view.md", references.BLUEPRINT_DIR)
        self.assertIn(f"| 信任錨與 IP 存取閘 | ### §6 | {l06} | 隨刀：憲法 §I.7 島 F 進場刀 |", out)
        self.assertIn(f"| 資料慣例 | ### §8 | {l06} | 形制：亂寫 |", out)
        self.assertIn(f"| §1 簡介與目標 | ## | {l01} | 重複：承襲（一句） |", out)
        self.assertIn(f"| 不存在的標題 | 未知鍵 | {l06} | 未知鍵 |", out)
        self.assertTrue(out.rstrip().endswith("缺：17｜重複：1｜未知鍵：1｜形制：1"), out[-120:])
        self.assertTrue(references.gen_rev5_blueprint_map(stub({})).rstrip().endswith("缺：20｜重複：0｜未知鍵：0｜形制：0"))

    def test_roster_eleven(self):
        self.assertEqual(len(references.GENERATED_FILES), 11)
        self.assertIn("docs/generated/reference/rev5-blueprint-map.md", references.GENERATED_FILES)

    @unittest.skipUnless(os.path.exists(REV5_BOOK), "rev5 對照樹缺席（bootstrap 斷言其在場；本機無則跳過）")
    def test_roster_equals_frozen_rev5_headings(self):
        with open(self.REV5_BOOK, encoding="utf-8") as f:
            heads = [(m.group(2).strip(), m.group(1)) for m in re.finditer(r"^(##|###) (.+?)\s*$", f.read(), re.M)]
        self.assertEqual(heads, [(h, lvl) for h, lvl, _ in references.REV5_BLUEPRINT])
```

（`test_roster_ten_and_compute_has_three_new_keys` 改名為 `test_compute_has_generated_index_keys`、拿掉 `len == 10` 斷言；`import re` 補上。）

- [ ] **Step 2: 跑測試確認紅**：`python3 tools/docsync test 2>&1 | tail -5` → 預期 `AttributeError: gen_rev5_blueprint_map`／名冊長度 10。
- [ ] **Step 3: 實作**

```python
REV5_BLUEPRINT = (  # rev5 活書標題名冊（凍結 SHA 7eab28a；欄＝字面｜層｜所屬 §N）；T1 測試對 rev5 檔逐字核
    ("§1 簡介與目標", "##", 1), ("§2 約束", "##", 2), ("§3 系統脈絡", "##", 3), ("§4 解法策略", "##", 4),
    ("§5 Building blocks", "##", 5), ("§6 Runtime", "##", 6),
    ("信任錨與 IP 存取閘", "###", 6), ("會話狀態機（sys_token）", "###", 6),
    ("登入失敗節流三區（帳號維＋來源維）", "###", 6), ("使用者域斷權與密碼三入口（007 落地）", "###", 6),
    ("§7 部署", "##", 7), ("§8 橫切概念", "##", 8),
    ("fork-delta 接線現況（base-web）", "###", 8), ("資料慣例", "###", 8), ("API 慣例", "###", 8), ("授權慣例", "###", 8),
    ("§9 架構決策", "##", 9), ("§10 品質要求", "##", 10), ("§11 風險與技術債", "##", 11), ("§12 名詞表", "##", 12),
)
BLUEPRINT_DISPOSITIONS = ("承襲", "隨刀：", "不承襲：")
BLUEPRINT_DIR = "docs/generated/reference"


def gen_rev5_blueprint_map(ctx):
    """rev5 藍本對照表（ADR-00006）：frontmatter rev5_blueprint 對 REV5_BLUEPRINT 名冊；缺／重複／未知鍵／形制只排列、永不拋錯（R2-F19 非常駐閘）。"""
    decl = {}
    for rel, meta, _ in _book_meta(ctx, "docs/arc42/"):
        bp = meta.get("rev5_blueprint") if RE_CHAPTER.match(rel) else None
        if isinstance(bp, dict):
            for k, v in bp.items():
                decl.setdefault(k, []).append((rel, str(v)))
    n = {"缺": 0, "重複": 0, "未知鍵": 0, "形制": 0}
    rows = []
    for h, lvl, sec in REV5_BLUEPRINT:
        layer = "##" if lvl == "##" else f"### §{sec}"
        ds = decl.get(h, [])
        if not ds:
            n["缺"] += 1
            rows.append(f"| {h} | {layer} | 缺 | 缺 |")
            continue
        if len(ds) > 1:
            n["重複"] += 1
        for rel, v in ds:
            bad = not v.startswith(BLUEPRINT_DISPOSITIONS)
            n["形制"] += bad
            tag = "重複：" if len(ds) > 1 else ("形制：" if bad else "")
            rows.append(f"| {h} | {layer} | {_link(rel, BLUEPRINT_DIR)} | {tag}{v} |")
    for h in sorted(set(decl) - {h for h, _, _ in REV5_BLUEPRINT}):
        n["未知鍵"] += 1
        rows.append(f"| {h} | 未知鍵 | {'、'.join(_link(r, BLUEPRINT_DIR) for r, _ in decl[h])} | 未知鍵 |")
    lines = [GENERATED_HEADER, "# reference/rev5-blueprint-map — rev5 活書藍本對照表（一次性 migrate-audit 面；ADR-00006）", "",
             "名冊＝rev5 活書 `../fork260509-rev5/docs/arc42/ARCHITECTURE.md`（凍結 SHA 7eab28a）的 12 個 `##`＋8 個 `###`（`references.REV5_BLUEPRINT`）；"
             "去處＝`docs/arc42/NN-*.md` frontmatter `rev5_blueprint`（鍵＝rev5 標題字面、值＝承襲（…）／隨刀：…／不承襲：…）。"
             "未宣告列「缺」、多檔宣告標「重複」、鍵不在名冊列「未知鍵」、值不以三詞起頭標「形制」；四項皆零＝藍本對照表零缺（波 3 出口判準、非常駐閘）。", "",
             "| rev5 標題 | 層 | rev6 去處 | 處置 |", "|---|---|---|---|"] + rows + \
            ["", f"缺：{n['缺']}｜重複：{n['重複']}｜未知鍵：{n['未知鍵']}｜形制：{n['形制']}"]
    return "\n".join(lines) + "\n"
```

名冊加 `"docs/generated/reference/rev5-blueprint-map.md"`；`compute_generated` 加 `"docs/generated/reference/rev5-blueprint-map.md": gen_rev5_blueprint_map(ctx)`。

- [ ] **Step 4: 跑測試確認綠**：`python3 tools/docsync test 2>&1 | tail -3` → 預期 OK、計數 85＋3（原名冊測試改名不增）。
- [ ] **Step 5: ADR-00006＋README** 寫入；`python3 tools/docsync generate` → 新檔 `docs/generated/reference/rev5-blueprint-map.md` 尾行 `缺：20｜重複：0｜未知鍵：0｜形制：0`（實跑自證：真 repo 零宣告＝20 缺）。
- [ ] **Step 6: 驗**：`python3 tools/docsync lint` 0 錯；`python3 tools/docsync check` 零漂移；`git add` 全部（含 generated 新檔）；邏輯行數看 STATE 報表 ≤4,000。
- [ ] **Step 7: Commit**（訊息含反引號→`-F` 檔）：`docs(tools): rev5 藍本對照表——frontmatter rev5_blueprint 真源＋gen_rev5_blueprint_map（缺列可見、不斷言）＋名冊 11＋ADR-00006`。核 `git rev-parse HEAD`。

### Task 2: arc42 §1～§4（12 處）＋frontmatter 4 鍵

**Files:** Modify `docs/arc42/01-introduction-and-goals.md`、`02-architecture-constraints.md`、`03-context-and-scope.md`、`04-solution-strategy.md`（內容＝§2 表 01～04 列；frontmatter 加 `rev5_blueprint:` 依 §1.2 四鍵）。

- [ ] **Step 1: 讀 rev5 §1／§2／§4 與 RAD-AI reference 缺口表**（唯讀；`sed -n 6,60p ../fork260509-rev5/docs/arc42/ARCHITECTURE.md`）。
- [ ] **Step 2: 逐檔重打字寫入**（§2 表為準；不帶回欄不寫；每段以 rev6 名詞與指針改寫）。
- [ ] **Step 3: 驗**：`grep -c 'TODO(波 3)' docs/arc42/0[1-4]-*.md` 全 0；`python3 tools/docsync lint` 0 錯（時態、連結、佔位）；`python3 tools/docsync generate`；`tail -1 docs/generated/reference/rev5-blueprint-map.md` → `缺：16｜…`；`git add`。
- [ ] **Step 4: Commit**：`docs(arc42): §1～§4 自 rev5 藍本消化（12 處填實）＋rev5_blueprint 四鍵`。

### Task 3: arc42 §5～§8（10 處）＋frontmatter 11 鍵

**Files:** Modify `docs/arc42/05-building-block-view.md`、`06-runtime-view.md`、`07-deployment-view.md`（§7 兩處本 Task 一併填、鍵留 T4）、`08-crosscutting-concepts.md`（內容＝§2 表 05～08 列；`rev5_blueprint` 依 §1.2：05 一鍵、06 五鍵、08 五鍵）。

- [ ] **Step 1: 讀 rev5 §5／§6 導言／§8 四子節**（唯讀；只取形與拍板已入憲法之處的指針，不帶回 as-built 細節）；`ls base-web/src`、`ls rust-api/` 取現況。
- [ ] **Step 2: 逐檔寫入**；§6.1 情境格式與「目前零情境」句；§8.1～8.3 指針段。
- [ ] **Step 3: 驗**：`grep -c 'TODO(波 3)' docs/arc42/0[5-8]-*.md` 全 0；lint 0 錯；generate；尾行 `缺：5｜…`；`git add`。
- [ ] **Step 4: Commit**：`docs(arc42): §5～§8 填實（10 處；as-built 隨刀、慣例指憲法）＋rev5_blueprint 十一鍵`。

### Task 4: arc42 §10～§12（6 處）＋frontmatter 5 鍵→對照表四項皆零

**Files:** Modify `docs/arc42/10-quality-requirements.md`、`11-risks-and-technical-debt.md`、`12-glossary.md`（內容＝§2 表 10～12 列）；`07-deployment-view.md`、`09-architecture-decisions.md`、`10`、`11`、`12` 各加 `rev5_blueprint` 一鍵（§1.2）。

- [ ] **Step 1: 讀 rev5 §12 與 RAD-AI glossary**（唯讀；`grep -n '^\*\*' ../fork260509-rev5/tmp/RAD-AI/documentation/glossary.md`）。
- [ ] **Step 2: 寫入**：§10.1 表、§10.2 格式＋零情境句、※11.1 表、※11.2 現況、§12 兩表（系統術語 11 詞、AI 術語約 18 詞中文改寫）。
- [ ] **Step 3: 驗**：`grep -rc 'TODO(波 3)' docs/arc42/ | grep -v ':0'` 空；lint 0 錯；generate；`tail -1 docs/generated/reference/rev5-blueprint-map.md` 必為 `缺：0｜重複：0｜未知鍵：0｜形制：0`；`grep -c '| 缺 |' docs/generated/reference/rev5-blueprint-map.md` 為 0；ARCHITECTURE.md 13 列摘要無變；`git add`。
- [ ] **Step 4: Commit**：`docs(arc42): §10～§12 填實（6 處）＋rev5_blueprint 五鍵——藍本對照表 20 列零缺`。

### Task 5: C4-E 三檔 16 處＋C4-L1／L2 一致性校

**Files:** Modify `docs/c4/C4-E1-ai-component-stereotypes.md`、`C4-E2-data-lineage-overlay.md`、`C4-E3-non-determinism-boundary.md`（§3 表）；`C4-L1-system-context.md`、`C4-L2-container.md` 只在校出增減時改。

- [ ] **Step 1: 讀 RAD-AI c4 reference 五類刻板型與 E2／E3 子節定義**（唯讀、抄形不抄字）。
- [ ] **Step 2: 寫入**；範本用 text 圍欄；C4-E3 邊界總覽 mermaid 節點 ⊆ 同檔表首欄。
- [ ] **Step 3: 一致性校**：對照 §3.1／§3.2／§7.1／§7.2 與 L1／L2 節點、邊、表列；有增減即改圖。
- [ ] **Step 4: 驗**：`grep -c 'TODO(波 3)' docs/c4/*.md` 全 0；lint 0 錯（GT-10 圖表對賬、C4-L2 ⊇ 17 services）；generate（RAD-AI-MAP 系統層仍「目前無」）；`git add`。
- [ ] **Step 5: Commit**：`docs(c4): C4-E1～E3 規則與表填實（16 處）；L1／L2 一致性校`。

### Task 6: 流程層 P-E1～P-E4（22 子節）＋BACKLOG 首條

**Files:** Modify `docs/process/P-E1-boundary.md`、`P-E2-agent-registry.md`、`P-E3-doc-pipeline.md`、`P-E4-responsible-agent.md`（§4 表）；`docs/ops/BACKLOG.md`（BL-00001：`reference/agents.md` 生成隨首個編排刀；分類 governance；觸發＝首個含 Workflow script 的刀開分支；檔頭 next bump 為 BL-00002）。

- [ ] **Step 1: 落帳先於 generate**：BACKLOG 條目寫入（RL-0050 取 next 後 bump）。
- [ ] **Step 2: 逐檔寫入**：每 `###` 首句 `類比張力：<判定>——<一句>`；P-E1 邊界圖 mermaid 節點 ⊆ 表；P-E2 表不重抄 `*_OPTS`。
- [ ] **Step 3: 驗**：`grep -c 'TODO(波 3)' docs/process/P-E[1-4]-*.md` 全 0；lint 0 錯（GT-10 類比張力腿、GT-05 rev5 前綴、GT-06 時態）；generate → RAD-AI-MAP 流程層 E1 5/5、E2 4/4、E3 6/6、E4 7/7；STATE BACKLOG 開放 1；`git add`。
- [ ] **Step 4: Commit**：`docs(process): P-E1～P-E4 類比張力填實（22 子節）＋BL-00001 agents.md 生成隨首個編排刀`。

### Task 7: 流程層 P-E6～P-E8＋P-C4-E3（29 子節）→ `TODO(波 3)` 歸零

**Files:** Modify `docs/process/P-E6-quality-scenarios.md`、`P-E7-agent-debt.md`、`P-E8-operations.md`、`P-C4-E3-materials-boundary.md`（§4 表）。

- [ ] **Step 1: 種子查證**：`grep -n 'rev5:L-' docs/ops/RULES.md` 枚舉可引之 L 號（P-E7 只指針、不重抄）。
- [ ] **Step 2: 逐檔寫入**（三處既定硬套照 §0.2-9）。
- [ ] **Step 3: 驗**：`grep -rn 'TODO(波 3)' docs/ | wc -l` 必為 0；lint 0 錯；generate → RAD-AI-MAP 流程層八列全 N/N；`git add`。
- [ ] **Step 4: Commit**：`docs(process): P-E6～P-E8、P-C4-E3 類比張力填實（29 子節）——TODO(波 3) 歸零`。

### Task 8: 波 3 出口驗收＋波標記 bump 4（merge 停點在此）

**Files:** Modify `docs/ops/NOTES.md`（首行 `<!-- wave: 4 -->`；現況＝波 3 落地物；下一步＝波 4 RAD-AI 23 筆取捨 ADR；未決兩條不動）。

- [ ] **Step 1: 出口 checklist（全部以工件自證）**：①`grep -rn 'TODO(波' docs/ | wc -l`＝0 ②`tail -1 docs/generated/reference/rev5-blueprint-map.md`＝四項皆零 ③`python3 tools/docsync test` 全綠 ④`python3 tools/docsync lint` 0 錯 0 警 ⑤`python3 tools/docsync check` 零漂移 ⑥`bash tools/bootstrap.sh` rc 0（純體檢）⑦RAD-AI-MAP 流程層八列 N/N、系統層十二列「目前無」⑧Day-1 仍 2 筆（或依 §0.2-12 變 1）。
- [ ] **Step 2: NOTES 改**（波標記 4；此時 `TODO(波 3)` 已零、GT-10 不紅）→ generate（STATE 現在波 4）→ lint → commit：`docs(ops): 波 3 出口——波標記 4、現況與下一步`。
- [ ] **Step 3: 停——merge 需 user 同意**（AskUserQuestion：merge --no-ff 回 rev6-admin-root／保留分支不 merge／其他）。
- [ ] **Step 4（同意後）: merge**：訊息寫檔 → `git merge --no-ff -F <檔> 000-w3-book-fill`（在 rev6-admin-root）→ `git log -1` 核 merge commit。
- [ ] **Step 5: 簿記 commit**：`docs/ops/events.jsonl` append misc（category governance、merge SHA、backlog_add `["BL-00001"]`、notes 含「blueprint-map 四項皆零、TODO(波 3) 歸零、分支保留供 audit」）→ generate → lint → commit：`docs(ops): 波 3 收單簿記`。
- [ ] **Step 6: perf 第四步**：量簿記 commit 牆鐘、append `close_bookkeeping` perf 事件（隨下一顆 commit 入帳；RL-0053）。

---

## Self-Review

- **Spec coverage**：啟動書 §5 波 3 列「流程層填實」（T6／T7）、「blueprint-map」（T1～T4）、「C4-L1／L2」（T5 一致性校）、「§12 名詞表」（T4）；§1 DoD 第 5 點零缺（T4 尾行斷言）；波 2 計畫 §0.3 剩餘六項全入（§0.3 表）；agents.md 明示延後（BL-00001）。
- **Placeholder scan**：本檔零 TBD／TODO 字面（`TODO(波 3)` 只作為被消滅對象出現）；每 Task 有實際檔名、步驟、驗證命令與預期值。
- **Type consistency**：`gen_rev5_blueprint_map(ctx) -> str`、`REV5_BLUEPRINT` 三元組、測試以 `references._link(rel, references.BLUEPRINT_DIR)` 組期望字面（與實作同源）；名冊長度 11 與 `test_roster_eleven` 一致；測試計數 85→88（三新、一改名）。
- **Risk／Guard／Rollback**（一次性遷移三欄）：Risk＝把 rev5 as-built 誤當 rev6 事實帶回→Guard＝§2「不帶回」欄＋值詞彙「隨刀」＋憲法 §I.5 防回歸條款→Rollback＝git revert 該 Task 顆＋generate 重算。
