<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# DECISIONS-INDEX — ADR 索引

| id | status | date | title | feature | supersedes | superseded_by |
|---|---|---|---|---|---|---|
| ADR-00001 | accepted | 2026-09-03 | host 埠配號 3xxxx 世代制——首碼 2→3、尾碼不動，D12 六值補全為十二值 | 輕量軌 | — | — |
| ADR-00002 | accepted | 2026-09-03 | rev5 凍結面＝rev6 bootstrap 單腿斷言——不開 rev5 遠端分支保護、不補 rev5 NOTES 凍結宣告 | 輕量軌 | — | — |
| ADR-00003 | accepted | 2026-09-03 | 憲法 1.0.0 定版——自 rev5 v1.10.0 依啟動書 §3.8 逐條表搬入；§I.7／§III.2 只留骨架＋承襲指針、§I.8 新增；spec-kit 產物同批入版控 | 輕量軌 | — | — |
| ADR-00004 | accepted | 2026-09-03 | RULES.md 首版 73 條與數量上限——總 92、per-scope 實算 ＋25%；六件套與看門狗紀律入 RULES；agent 面不可違反項自 CLAUDE.md 範本補列 | 輕量軌 | — | — |
| ADR-00005 | accepted | 2026-09-03 | 三件生成索引（ARCHITECTURE.md、LESSONS.md 例外註冊、RAD-AI-MAP）與 LL next-id 自檔集推導——索引不再是人寫的家、永不回收靠 GT-05 單調腿 | 輕量軌 | — | — |
| ADR-00006 | accepted | 2026-09-03 | rev5 藍本對照表——去處住 arc42 節檔 frontmatter `rev5_blueprint`、生成器只排缺列不斷言（一次性 migrate-audit、非常駐閘）、`##` 一併入表、rev5 ADR 不入 | 輕量軌 | — | — |
| ADR-00007 | accepted | 2026-09-03 | RAD-AI 23 筆內部不一致的 rev6 取捨與量表第四值「不適用」——reference 為預設仲裁者、逐筆例外採模板或 adoption-guide；射程＝系統層形制、流程層偏離以「類比張力：」宣告 | 輕量軌 | — | — |
| ADR-00008 | accepted | 2026-09-04 | migration 短號形制＝`m0001` 四碼（承啟動書 D4；rev6 現在式面唯一家；承襲 rev5 migration 時改名） | 輕量軌 | — | — |
| ADR-00009 | accepted | 2026-09-04 | 憲法 §I.5 例外清單擴展——資料形狀契約三件整檔拷貝（基線結構 migration＋基線 seed migration＋基線 entity 15 檔；射程鎖 rev5 rust-api `92919b9`；MINOR 1.1.0） | 輕量軌 | — | — |
| ADR-00010 | proposed | 2026-09-04 | schema 基線＝rev5 終態逐位元承襲＋受管演進帳閘契約（凍結面／演進面／全等語意／archetype 歸屬／雙源互證） | 輕量軌 | — | — |
