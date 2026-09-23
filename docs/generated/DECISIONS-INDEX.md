<!-- 機器生成：python3 tools/docsync generate——嚴禁手改；差異由 pre-commit check 攔下 -->
# DECISIONS-INDEX — ADR 索引

| id | status | date | title | feature | supersedes | superseded_by |
|---|---|---|---|---|---|---|
| ADR-00001 | accepted | 2026-09-03 | host 埠配號 3xxxx 世代制——首碼 2→3、尾碼不動，D12 六值補全為十二值 | — | — | — |
| ADR-00002 | accepted | 2026-09-03 | rev5 凍結面＝rev6 bootstrap 單腿斷言——不開 rev5 遠端分支保護、不補 rev5 NOTES 凍結宣告 | — | — | — |
| ADR-00003 | accepted | 2026-09-03 | 憲法 1.0.0 定版——自 rev5 v1.10.0 依啟動書 §3.8 逐條表搬入；§I.7／§III.2 只留骨架＋承襲指針、§I.8 新增；spec-kit 產物同批入版控 | — | — | — |
| ADR-00004 | superseded | 2026-09-03 | RULES.md 首版 73 條與數量上限——總 92、per-scope 實算 ＋25%；六件套與看門狗紀律入 RULES；agent 面不可違反項自 CLAUDE.md 範本補列 | — | — | ADR-00011 |
| ADR-00005 | accepted | 2026-09-03 | 三件生成索引（ARCHITECTURE.md、LESSONS.md 例外註冊、RAD-AI-MAP）與 LL next-id 自檔集推導——索引不再是人寫的家、永不回收靠 GT-05 單調腿 | — | — | — |
| ADR-00006 | accepted | 2026-09-03 | rev5 藍本對照表——去處住 arc42 節檔 frontmatter `rev5_blueprint`、生成器只排缺列不斷言（一次性 migrate-audit、非常駐閘）、`##` 一併入表、rev5 ADR 不入 | — | — | — |
| ADR-00007 | accepted | 2026-09-03 | RAD-AI 23 筆內部不一致的 rev6 取捨與量表第四值「不適用」——reference 為預設仲裁者、逐筆例外採模板或 adoption-guide；射程＝系統層形制、流程層偏離以「類比張力：」宣告 | — | — | — |
| ADR-00008 | accepted | 2026-09-04 | migration 短號形制＝`m0001` 四碼（承啟動書 D4；rev6 現在式面唯一家；承襲 rev5 migration 時改名） | 獨立輪｜doc-governance | — | — |
| ADR-00009 | accepted | 2026-09-04 | 憲法 §I.5 例外清單擴展——資料形狀契約三件整檔拷貝（基線結構 migration＋基線 seed migration＋基線 entity 15 檔；射程鎖 rev5 rust-api `92919b9`；MINOR 1.1.0） | 001-schema-baseline | — | — |
| ADR-00010 | accepted | 2026-09-04 | schema 基線＝rev5 終態逐位元承襲＋受管演進帳閘契約（凍結面／演進面／全等語意／archetype 歸屬／雙源互證） | 001-schema-baseline | — | — |
| ADR-00011 | accepted | 2026-09-04 | 數量預算改為只警告不擋——BACKLOG 開放取消上限（觀測值）、閘數與 RULES per-scope 保留上限但一律 WARN | 輕量軌｜2026-09-04 | ADR-00004 | — |
| ADR-00012 | accepted | 2026-09-05 | schema 定稿權威自 001 spec 目錄抽出至 reference-src——凍結存證與跨刀活體二分 | 輕量軌｜2026-09-05 | — | — |
| ADR-00013 | accepted | 2026-09-05 | fix 清單外零改動升級不終止 run——該段收斂帶升級項、碼品質段照跑、已升級項重報過濾 | 002-system-settings | — | — |
| ADR-00014 | accepted | 2026-09-05 | 授權拒絕語意定死為 5003＋HTTP 403＋純 i18n key，並預留空 no-escalation 掛點簽章 | 002-system-settings | — | — |
| ADR-00015 | accepted | 2026-09-05 | 部分更新請求之 envelope 級三態約定——欄位缺席＝不動、JSON null＝顯式清空、有值＝設值 | 002-system-settings | — | — |
| ADR-00016 | superseded | 2026-09-05 | 碼面閘名冊承載於 RUNBOOK §12 碼面閘表，由 GT-12 新腿對賬 tools/ 頂層工具檔集 | 002-system-settings | — | ADR-00032 |
| ADR-00017 | accepted | 2026-09-05 | msg key 跨端契約延至首個接 i18n 的前端刀，002 只閉後端側 msg key 名冊 | 002-system-settings | — | — |
| ADR-00018 | accepted | 2026-09-05 | pre-commit entity-drift 段之 schema 快照缺席由 Day-1 具名跳過改為 rc 2 擋下並提示照相 | 002-system-settings | — | — |
| ADR-00019 | accepted | 2026-09-05 | 容器依賴型碼面閘之環境缺席語意——docker 或對應容器不在＝具名跳過 rc 0、容器在而工具缺或重抽失敗＝fail-loud | 002-system-settings | — | — |
| ADR-00020 | accepted | 2026-09-07 | 編排骨架子名冊＝tools/orchestration/README.md 檔表，由 GT-09 新腿對賬 tools/orchestration/ 實檔集 | 輕量軌｜maint-backlog-6 | — | — |
| ADR-00021 | accepted | 2026-09-07 | 檢索性第四指標——review 事件 `probe` 欄（冷啟動探針＋否定對照題計數）為資料源，STATE 治理指標表加一列、比例由 generate 現算；000-r1 以 erratum 回填為基準 | 輕量軌｜maint-backlog-7 | — | — |
| ADR-00022 | accepted | 2026-09-07 | 憲法 §I.5 例外① 射程含註解——整檔拷貝之工具性 crate 豁免「註解一律重寫」第 3 款；vendored-check 之去註解口徑就此有凍結權威背書 | 輕量軌｜000-r2-doc-governance | — | — |
| ADR-00023 | accepted | 2026-09-07 | 憲法 §I.3 四保留碼「從不發出」之機器承載點改記為型別層全變體窮舉＋error.rs 矩陣斷言雙錨（as-built 對齊，非行為變更） | 輕量軌｜000-r2-doc-governance | — | — |
| ADR-00024 | accepted | 2026-09-07 | 憲法 §III 生成檔紀律去除對空表的死引用——判準改為「路由外掛重算產出之檔同族」、具體檔集隨相關 ★ 軌道 Amendment 落表 | 輕量軌｜000-r2-doc-governance | — | — |
| ADR-00025 | accepted | 2026-09-07 | won't-fix——ADR 方向不設「誕生必帶事件」反向不變式；ADR 的家是檔案本身，BL／ADR 兩個 ID 家族刻意兩制 | 輕量軌｜000-r2-doc-governance | — | — |
| ADR-00026 | accepted | 2026-09-08 | 憲法 Amendment 1.2.0→1.3.0——§III.2 首批四條 ★ 軌道八用途授權＋§I.7 首批五座行為島 A～E 入憲 | 003-auth-session | — | — |
| ADR-00027 | superseded | 2026-09-08 | AppState 恰兩欄封條翻案→五欄——加 jwt／cache／captcha_secret；ip_rules／trust_model／mailer 續留域外 | 003-auth-session | — | ADR-00036 |
| ADR-00028 | accepted | 2026-09-08 | root Cargo.toml「不引 argon2」翻案——引入 auth 依賴八支（六支 auth＋log＋getrandom）、全域版本紀律雙源核對 D1～D6 | 003-auth-session | — | — |
| ADR-00029 | superseded | 2026-09-13 | msg key 跨端閘形制＝後端名冊與三檔 locale backend 子樹逐檔雙向全等、無白名單、Biz 構造點守衛兩形（tools/msg-key-gate.py） | 003-auth-session | — | ADR-00039 |
| ADR-00030 | accepted | 2026-09-13 | 登入頁三顆快速登入鈕與表單預填密碼＝已知態「保留＋記帳」（零 inline、UI 對照零差異；帳＝滯後卷 BL-00049、觸發綁 RUNBOOK §16 prod 硬化拍板） | 003-auth-session | — | — |
| ADR-00031 | accepted | 2026-09-14 | rust-api boot 期 JWT access／refresh 兩把秘鑰同值即 fail-loud（兩鍵指名、訊息不含值；射程只 JWT 兩鑰） | 輕量軌｜maint-backlog-pre-004 | — | — |
| ADR-00032 | accepted | 2026-09-15 | 碼面閘名冊承載於 RUNBOOK §12 碼面閘表（續行 ADR-00016）——名詞定義之環境缺席語意改為逐支見表、容器依賴型具名跳過 | 輕量軌｜maint-spec-compliance-002 | ADR-00016 | — |
| ADR-00033 | accepted | 2026-09-15 | logout 呈遞 rotated 票維持 0000 靜默 no-op——撤銷射程恆為單列、不擴撤全鏈（by-design；承 rev5:ADR 0059） | 輕量軌｜maint-spec-compliance-003 | — | — |
| ADR-00034 | accepted | 2026-09-15 | 憲法 Amendment 1.3.0→1.4.0——§I.7 島 F 入憲＋島 E 四處細項調整＋§III.2 開 ★BASE-WEB-MANAGE-PAGE-WIRING (i)、I18N-WIRING (ii) 權威句與 (i) 對齊、五欄範圍實數化 | 004-ip-trust-anchor | — | — |
| ADR-00035 | accepted | 2026-09-15 | 引入 IP 域依賴三支——arc-swap 1.9.2／futures-util 0.3.34（default features 關）／toml 1.1.6；ADR-00028 決定 2「明確不進」七支中三支之前提於 004 成立 | 004-ip-trust-anchor | — | — |
| ADR-00036 | accepted | 2026-09-19 | AppState 五欄→七欄（續行 ADR-00027）——加 trust_model／ip_rules；mailer 續留域外、開第八欄須新 ADR | 004-ip-trust-anchor | ADR-00027 | — |
| ADR-00037 | accepted | 2026-09-19 | 轉發鏈跳數逾上界——標記全域、拒絕限登入、計數分流；稽核轉錄保留判定窗並與判定軌共用取窗實作（島 F 之 F7／F8 落地形） | 004-ip-trust-anchor | — | — |
| ADR-00038 | accepted | 2026-09-20 | 登入節流判定面——兩維皆於每次嘗試讀設定現值並由 PG 滑動窗定案、不設快取層負快取；快取可用性改由解鎖標記讀取判定 | 004-ip-trust-anchor | — | — |
| ADR-00039 | accepted | 2026-09-20 | msg key 譯文之家＝三檔 locale backend 子樹各為該語權威（續行 ADR-00029）——不另立譯文表、鍵數以跨端閘為準 | 004-ip-trust-anchor | ADR-00029 | — |
| ADR-00040 | accepted | 2026-09-20 | 004 ip-trust-anchor 已知態集——解鎖無 UI 按鈕／dev 經反向代理可達二態／操作稽核覆蓋不對稱／logout 故障窗弱 oracle／redis 不開持久化／wire 裁判面不開嚴格模式（六款皆 by-design、各附翻案觸發器） | 004-ip-trust-anchor | — | — |
| ADR-00041 | accepted | 2026-09-21 | 跨刀活體契約自 spec 目錄抽出至 reference-src——五份新家、spec 原檔留凍結存證、現在式面改指新家（兩種書寫形皆機器守） | 輕量軌｜maint-backlog-42 | — | — |
| ADR-00042 | proposed | 2026-09-23 | 憲法 Amendment 1.4.0→1.5.0——§I.7 島 H 入憲（H3 增補受保護選單不可停用／不可改父、H2 載同步失敗保留上一份）＋島 E 補兩句＋§III.2 ★BASE-WEB-MANAGE-PAGE-WIRING 用途 (ii) 恰九檔＋表外宣告 1 量法句與 §I.7 段首計數句改對 | — | — | — |
| ADR-00043 | proposed | 2026-09-23 | casbin 判定面同步——全新重建後一步換上、保留上一份、全程互斥、觸發恰五支移除面寫端之「實際歸檔 ≥1 列」；翻 002 刀「boot 載入即終態」宣告、兌現 ADR-00014 決定 4 之運行期重載預告 | — | — | — |
| ADR-00044 | proposed | 2026-09-23 | 選單域與角色刪除之域行為——角色刪除家族入域且實際歸檔才同步、島 G 行為（G1 前半／G3／G4／G5）由本 ADR 承載、授權歸檔表三自由度 won't-use、受保護選單守門、隱藏於選單釋義 | — | — | — |
| ADR-00045 | proposed | 2026-09-23 | 角色與選單管理之已知態與 by-design——授權彈窗真樹假勾選／policy-archive 死項／新建與復原選單側欄不現／新按鈕碼無人持有／新建選單顯原始 i18n 鍵／治理清單三列路由裸鍵／getAllRoles 之既有 UI 消費者與 roleHome 零消費者／治理清單分頁列凍結與無 size 全取（各款「觀察路徑→症狀」、CDP 實際觀察後定稿） | — | — | — |
| ADR-00046 | proposed | 2026-09-23 | IP 域已知態集（續行 ADR-00040）——六款重述（款 2 改三態、款 3 寫入者集對齊 as-built、款 6 以讀型鍵集表驅動斷言兌現）＋新款：清單端點未知規則類型照原樣上 wire、前端退顯原字串 | — | — | — |
| ADR-00047 | proposed | 2026-09-23 | 部分更新語意（續行 ADR-00015）——envelope 級三態續行；角色與選單之可空文字欄空字串＝清空落 NULL（新增同形）、名稱欄空字串與 null 同拒；系統設定寫端「空字串＝設值」續行；提前 no-op 與不可變欄出現形 | — | — | — |
