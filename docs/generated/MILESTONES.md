<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# MILESTONES — 事件表（新在前）——perf 型另居 reference/perf.md

| date | type | 標的 | summary | merge | adrs | arch |
|---|---|---|---|---|---|---|
| 2026-09-04 | misc | governance | rev6 獨立 review 輪 000-r1 文件治理架構體檢收單：四支唯讀 Workflow（探索 14／驗證 41／補漏 12）＋修單 run 8 支；confirmed 86＝修 75／BL 4 條／ADR-00008／none 2；報告 docs/reviews/20260904-doc-governance.md＋review 事件（total 80）；RULES 74（名詞段獨立輪／隨遷工具／其他面、RL-0074）、RULES-VERSION 064380371fc0；BACKLOG 開放 7；merge --no-ff 回 rev6-admin-root | 5459c9d | — | — |
| 2026-09-04 | review | doc-governance | findings 80（修 75／BL 4／ADR 1）；BL-00001、BL-00003、BL-00004、BL-00005、ADR-00008 | — | — | — |
| 2026-09-03 | misc | governance | rev6 波 5 文件創世驗收收單：DoD A 六條全勾（報告 docs/reviews/20260903-doc-genesis.md＋首筆 review 事件、§7 自評十三列：系統層全不適用、流程層 2×7／1×4）；GT-03 Day-1 豁免解除（gates.py 移鍵、零 close 事件改 ERROR、Day-1 餘 GT-08 一筆）；tmp 交接包與憲法 diff 已清；外層 origin 已設；波標記 6＝文件創世收官、波 6 起為刀；merge --no-ff 回 rev6-admin-root | 5bae24c | — | — |
| 2026-09-03 | review | doc-genesis | findings 0（修 0／BL 0／ADR 0） | — | — | — |
| 2026-09-03 | misc | governance | rev6 波 4 RAD-AI 取捨 ADR 收單：ADR-00007 accepted（附錄 A 19 列涵蓋 F01～F24；射程＝系統層形制、流程層以類比張力宣告偏離、D15 在活書正文零例外＋機器自證）；附錄 A 對 as-built 對賬零未決（證據段住 ADR）；活書四處（P-E1 指向 C4-E3、C4-E1 必填性質指針與導言中文化、§9.1 對映表改欄序）；波標記 5；merge --no-ff 回 rev6-admin-root | 1089a23 | — | — |
| 2026-09-03 | misc | governance | rev6 波 3 活書填實收單：arc42 官方子節 28 處自 rev5 藍本消化、C4-E 三檔 16 處、流程層 51 子節類比張力真句（P-E7 九欄登記表）、rev5 藍本對照表 20 列四項皆零（frontmatter rev5_blueprint 真源、ADR-00006）、reference/agents.md 15 列、GENERATED_FILES 12；TODO(波 3) 歸零、波標記 4；merge --no-ff 回 rev6-admin-root | 678705e | — | — |
| 2026-09-03 | misc | governance | rev6 波 2 活書骨架收單：arc42 十三檔＋ARCHITECTURE 索引、C4 五檔、compliance 23 鍵不適用、process 八檔 51 子節、ops 帳本三檔、生成器三支（ADR-00005）、GT-10 第八腿；Day-1 6→2、波標記 3；merge --no-ff 回 rev6-admin-root | 6e5f48c | — | — |
| 2026-09-03 | misc | governance | rev6 波 1 後段收單：憲法 1.0.0（ADR-00003）＋RULES 首版 73 條（ADR-00004）＋tools/docsync（GT-01～GT-12、generate／check／lint／rules emit／errata）＋掃描防線（.gitleaks.toml、.githooks、bootstrap 回填）＋hook RULES-VERSION 對賬＋README／CLAUDE.md 正式版；merge --no-ff 回 rev6-admin-root | 4f892fc | — | — |
| 2026-09-03 | misc | governance | rev6 波 1 創世：守門五件（49f37d2）＋源倉 gitlink（881c621）＋啟動書搬入（7f34015）＋compose 3xxxx 與 deploy 遷入（8a20aaa）＋bootstrap 凍結斷言（4c24966）＋ADR-00001/00002（a31cb54）＋機密管線首建（ce6cfff／5e8e69f） | — | — | — |
