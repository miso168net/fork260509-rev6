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
| ADR-00012 | superseded | 2026-09-05 | schema 定稿權威自 001 spec 目錄抽出至 reference-src——凍結存證與跨刀活體二分 | 輕量軌｜2026-09-05 | — | ADR-00087 |
| ADR-00013 | accepted | 2026-09-05 | fix 清單外零改動升級不終止 run——該段收斂帶升級項、碼品質段照跑、已升級項重報過濾 | 002-system-settings | — | — |
| ADR-00014 | accepted | 2026-09-05 | 授權拒絕語意定死為 5003＋HTTP 403＋純 i18n key，並預留空 no-escalation 掛點簽章 | 002-system-settings | — | — |
| ADR-00015 | superseded | 2026-09-05 | 部分更新請求之 envelope 級三態約定——欄位缺席＝不動、JSON null＝顯式清空、有值＝設值 | 002-system-settings | — | ADR-00047 |
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
| ADR-00039 | superseded | 2026-09-20 | msg key 譯文之家＝三檔 locale backend 子樹各為該語權威（續行 ADR-00029）——不另立譯文表、鍵數以跨端閘為準 | 004-ip-trust-anchor | ADR-00029 | ADR-00084 |
| ADR-00040 | superseded | 2026-09-20 | 004 ip-trust-anchor 已知態集——解鎖無 UI 按鈕／dev 經反向代理可達二態／操作稽核覆蓋不對稱／logout 故障窗弱 oracle／redis 不開持久化／wire 裁判面不開嚴格模式（六款皆 by-design、各附翻案觸發器） | 004-ip-trust-anchor | — | ADR-00046 |
| ADR-00041 | accepted | 2026-09-21 | 跨刀活體契約自 spec 目錄抽出至 reference-src——五份新家、spec 原檔留凍結存證、現在式面改指新家（兩種書寫形皆機器守） | 輕量軌｜maint-backlog-42 | — | — |
| ADR-00042 | accepted | 2026-09-23 | 憲法 Amendment 1.4.0→1.5.0——§I.7 島 H 入憲（H3 增補受保護選單不可停用／不可改父、H2 載同步失敗保留上一份）＋島 E 補兩句＋§III.2 ★BASE-WEB-MANAGE-PAGE-WIRING 用途 (ii) 恰九檔＋表外宣告 1 量法句與 §I.7 段首計數句改對 | 005-role-menu-crud | — | — |
| ADR-00043 | accepted | 2026-09-23 | casbin 判定面同步——全新重建後一步換上、保留上一份、全程互斥、觸發恰五支移除面寫端之「實際歸檔 ≥1 列」；翻 002 刀「boot 載入即終態」宣告、兌現 ADR-00014 決定 4 之運行期重載預告 | 005-role-menu-crud | — | — |
| ADR-00044 | accepted | 2026-09-23 | 選單域與角色刪除之域行為——角色刪除家族入域且實際歸檔才同步、島 G 行為（G1 前半／G3／G4／G5）由本 ADR 承載、授權歸檔表三自由度 won't-use、受保護選單守門、隱藏於選單釋義、保留路由名守門、upstream 同 URL 型偏離帳 | 005-role-menu-crud | — | — |
| ADR-00045 | superseded | 2026-09-23 | 角色與選單管理之已知態與 by-design——授權彈窗真樹假勾選／policy-archive 死項／新建與復原選單側欄不現／新按鈕碼無人持有／新建選單顯原始 i18n 鍵／治理清單三列路由裸鍵／getAllRoles 之既有 UI 消費者與 roleHome 零消費者／治理清單分頁列凍結與無 size 全取（各款「觀察路徑→症狀」、CDP 實際觀察後定稿） | 005-role-menu-crud | — | ADR-00068 |
| ADR-00046 | superseded | 2026-09-23 | IP 域已知態集（續行 ADR-00040）——六款重述（款 2 改三態、款 3 寫入者集對齊 as-built、款 6 以讀型鍵集表驅動斷言兌現）＋新款：清單端點未知規則類型照原樣上 wire、前端退顯原字串 | 005-role-menu-crud | ADR-00040 | ADR-00069 |
| ADR-00047 | superseded | 2026-09-23 | 部分更新語意（續行 ADR-00015）——envelope 級三態續行；角色與選單之可空文字欄空字串＝清空落 NULL（新增同形）、名稱欄空字串與 null 同拒；系統設定寫端「空字串＝設值」續行；提前 no-op 與不可變欄出現形 | 005-role-menu-crud | ADR-00015 | ADR-00080 |
| ADR-00048 | accepted | 2026-09-27 | 憲法 Amendment 1.5.0→1.5.1——§III.2 ★BASE-WEB-AUTH-WIRING (c) 列範圍欄 captcha.ts 修改型處數 3→5（fork-delta-lint 改逐值比次數後揭出之既有缺漏補錄） | 005-role-menu-crud | — | — |
| ADR-00049 | superseded | 2026-09-28 | 角色與選單拒因譯文對 rev5 之對照口徑——純換句話說者逐字對齊 rev5、帶 rev6 語意延伸之四鍵保留 rev6 措辭並入 CDP 排除清單 | 005-role-menu-crud | — | ADR-00050 |
| ADR-00050 | accepted | 2026-09-28 | 角色與選單拒因譯文對 rev5 之對照口徑（續行 ADR-00049）——`nameRequired` 兩鍵改歸「帶 rev6 語意延伸」、保留 rev6 措辭並入 CDP 排除清單 | 005-role-menu-crud | ADR-00049 | — |
| ADR-00051 | accepted | 2026-09-28 | 憲法 Amendment 1.5.1→1.5.2——§III.2 ★BASE-WEB-MANAGE-PAGE-WIRING 用途 (ii) 六支 view／元件檔範圍欄「不預估」實數化（兌現 ADR-00042 回填義務） | 005-role-menu-crud | — | — |
| ADR-00052 | accepted | 2026-09-29 | 治理閘取值口徑——文字類腿續讀工作樹＋「工作樹＝暫存區」一致性腿；HEAD 版本缺席＝新檔通過、其他 git 失敗＝ERROR | 輕量軌｜maint-backlog-28-35-36-39-74-101-102-120 | — | — |
| ADR-00053 | accepted | 2026-09-29 | 事件帳自由文字欄（summary／reason／spec_supersessions[].note）不入更正欄位、寫錯以後續事件 notes 說明——三欄於寫入端套 notes 同一道守衛 | 輕量軌｜maint-backlog-28-35-36-39-74-101-102-120 | — | — |
| ADR-00054 | accepted | 2026-09-29 | 設定界值唯一權威＝validation.rs 的 REGISTRY、不與設計文件做機器對賬——seed 界內以純測守衛 | 輕量軌｜maint-backlog-28-35-36-39-74-101-102-120 | — | — |
| ADR-00055 | accepted | 2026-09-29 | 碼面閘讀子庫工作樹、不讀本顆 commit 所 pin 的子庫內容——照實登記兩型（閘面內延後偵測／閘面外無兜底）為已知態、不擴觸發（won't-fix） | 輕量軌｜maint-backlog-28-35-36-39-74-101-102-120 | — | — |
| ADR-00056 | accepted | 2026-09-29 | 組裝形 workflow 每支 agent 的模型家恆為 opus[1m]／xhigh、不隨主線 session effort——拍板入 ADR，TDD 形與 review 形 harness 皆以寫死字面機器守 | 輕量軌｜maint-backlog-127 | — | — |
| ADR-00057 | accepted | 2026-09-29 | 系統設定讀端回全部未刪列、不以 registry 鍵集過濾（任一列型別守衛不過即整支 5000）——宣告集外而型別合法之列讀得到、寫端回 2222 為已知態（by-design） | 輕量軌｜maint-backlog-27-44 | — | — |
| ADR-00058 | accepted | 2026-09-29 | 管理清單一律伺服器端固定穩定序、零 client 排序參數——列表排序能力不提供（by-design） | 輕量軌｜maint-backlog-27-44 | — | — |
| ADR-00059 | accepted | 2026-09-30 | DB 伺服器時區以 compose 明文固定 UTC、全服務容器明設 TZ=UTC、schema-gate check 常設斷言——取代「postgres 容器預設、不另設定」 | 輕量軌｜maint-tz-utc | — | — |
| ADR-00060 | accepted | 2026-09-30 | 憲法 §I.6 修訂——表示瞬間之時間欄一律 timestamptz（不限審計欄）、禁無時區 timestamp；純日曆日期得用 date、須 spec 具名理由（v1.6.0） | 輕量軌｜maint-tz-utc | — | — |
| ADR-00061 | accepted | 2026-09-30 | 時間傳輸與顯示——wire 時間欄一律 RFC3339、偏移恆 +00:00（小數位數隨值）；管理頁原樣顯示 UTC、不依瀏覽器時區換算（by-design） | 輕量軌｜maint-tz-utc | — | — |
| ADR-00062 | accepted | 2026-09-30 | 記時與帳本日期時區——主線在 tmp/ 記時刻一律同指令取 OS 系統時間、不得估計；受版控帳本日期欄記 OS 系統時間之當地日期（UTC+8）；工具產出之機器時間欄不在此列 | 輕量軌｜maint-tz-utc | — | — |
| ADR-00063 | accepted | 2026-10-01 | 憲法 Amendment 1.6.0→1.7.0——§I.7 島 G（casbin 授權治理、G1～G6、G6 結構性封死）入憲＋島 H 連動（序言、H1 終態成員括號、判定面同步失敗方向與兩窗之落位）＋§III.2 ★BASE-WEB-MANAGE-PAGE-WIRING 用途 (iii)(iv)＋§III 修改型之 Vue 模板屬性行變體＋表外宣告 3 範圍欄入機器對賬 | 006-authz-governance | — | — |
| ADR-00064 | accepted | 2026-10-01 | 結構性封死（島 G6）——封死集＝「ptype='p' ∧ protected=TRUE ∧ v2 ∈ HTTP 方法白名單」之（路徑,方法）謂詞、不寫列數；授予側整批拒 `biz.role.protectedGrant`、R_SUPER 豁免；掛點恰兩處（端點維授權寫端、授權回收桶復原第③腿）；承重前提＝受保護旗標寫不進來；選單維受保護四列與非封死之政策端點不封、no-escalation 本體留 007 刀 | 006-authz-governance | — | — |
| ADR-00065 | accepted | 2026-10-01 | 授權回收桶復原——不可復原集 3→5（可復原恰 `endpoint_revoke`、零 migration）、鎖內固定序五腿（原因→同實例→封死→端點在路由表→停用不擋）、以歸檔來源角色 id 鎖角色列之等價改形、NoOp 消費歸檔列且零稽核、可復原旗標＝①～④ 同判準、回收桶只篩角色代碼與維度、不設 23505 收窄；ADR-00044 決定 4 復核結論＝選單維仍無可復原原因 | 006-authz-governance | — | — |
| ADR-00066 | accepted | 2026-10-01 | 三維授權全量替換之射程＝候選集——撤銷集＝（現況 ∩ 候選集）−期望、新授集＝（期望 ∩ 候選集）−現況、候選外現役列不撤不授不入生效集合；現況讀端只回候選內（讀端取態與 rev5:ADR 0056 分岔） | 006-authz-governance | — | — |
| ADR-00067 | accepted | 2026-10-01 | 判定面同步觸發列增列——授予面三支 Applied 即觸發（含空 diff、刻意例外）與 restorePolicy Applied 觸發，與移除面「成功且實際歸檔 ≥1 列」三類並陳；已知降級窗改記兩窗（commit→換上之有界過渡窗＋重試耗盡窗）、補述 ADR-00043 決定 9、不 supersede ADR-00043 | 006-authz-governance | — | — |
| ADR-00068 | accepted | 2026-10-01 | 角色與選單管理之已知態（續行 ADR-00045）——八款逐款處置（款 1 解除／款 2、6 收窄為 system-settings 與 audit 兩列／款 3、4、7 改述／款 5、8 續行）＋新款：21 支可授出端點之下放效果（含 unlockLogin 無帳號維守門）／選單維受保護四列看得到、封死功能點不動／並行編輯後送出者整份覆蓋／授權回收桶復原 NoOp 移除歸檔列而零稽核／首頁下拉選值即寫／可授予指向不存在 view 之自建選單／選單維與按鈕維之授權撤銷只剩閱覽／授權回收桶復原不擋停用角色／只勾目錄之無子項死項與首頁兜底落 /403／三組按鈕碼授撤零可見效果／兩分頁下角色抽屜三欄舊值覆寫／UI 外對已停用之自身所屬角色送停用值照擋（款 17～20＝候選四款定案） | 006-authz-governance | ADR-00045 | — |
| ADR-00069 | accepted | 2026-10-01 | IP 域已知態集（續行 ADR-00046）——款 1、2、4～7 續行（款 1 刀射程句座標改寫）、款 3 操作稽核寫入者集擴列三維授權寫端（update）與授權回收桶復原（restore）並以現行全集重述＋新款：IP 存取閘每次阻擋恰一則結構化 warn、不設節流（BL-00084 by-design） | 006-authz-governance | ADR-00046 | — |
| ADR-00070 | accepted | 2026-10-01 | 角色抽屜編輯只在狀態異於開啟時回填值才帶狀態欄（BL-00131 前端修）——與 rev5 恆送之刻意分岔、改點在用途 (ii) 既有新增型圈界內免修憲、後端停用雙護欄口徑不動 | 006-authz-governance | — | — |
| ADR-00071 | accepted | 2026-10-01 | seed-view-gate 碼面閘——seed 選單 component 之 view 集 ⊆ base-web view 集、具名豁免恰兩列（system-settings／audit、附 BL-00045、到期即紅）、python 實作避開 BL-00108 第三份、讀面分型 (a)／(b)（ADR-00055 決定 3 之首例） | 006-authz-governance | — | — |
| ADR-00072 | accepted | 2026-10-04 | 憲法 Amendment 1.7.0→1.7.1——§III.2 ★BASE-WEB-MANAGE-PAGE-WIRING 用途 (iii)(iv) 範圍欄預估值實數化（兌現 ADR-00063 回填義務） | 006-authz-governance | — | — |
| ADR-00073 | accepted | 2026-10-04 | GT-03 加 BL 唯一性腳——同一 BL 號全帳至多誕生一次、至多收一次（ERROR） | 輕量軌｜maint-backlog-137-133 | — | — |
| ADR-00074 | accepted | 2026-10-05 | 憲法 Amendment 1.7.1→1.8.0——§I.7 島 I（使用者域治理；I1～I5、I7 入憲、I6 刻意空缺）＋跨島註與跨島總則＋島 B／C 用語與島 H2 連動＋§III.2 ★BASE-WEB-MANAGE-PAGE-WIRING 用途 (v)～(viii)＋★BASE-WEB-LOGIN-CAPTCHA-WIRING (ii) 開立＋★BASE-WEB-I18N-WIRING (i)(iii) 改寫與三語鍵集 | — | — | — |
| ADR-00075 | accepted | 2026-10-05 | 包含規則（島 I7）與射程分工——判定＝handler 鎖內具名純函式、9 個消費點（使用者寫端八支＋unlockLogin 帳號維）共用單一包裝；中介層 no-escalation 掛點續恆放行為路徑級上限位、簽章與呼叫點不動；角色域、IP 域與授權回收桶復原不掛；ADR-00064 翻案觸發器首條與次條之複核結論；BL-00048 兌現 | — | — | — |
| ADR-00076 | accepted | 2026-10-05 | 錯誤明細通道射程恰兩鍵——`biz.user.passwordPolicy` 攜違規碼清單、`biz.user.pwdSetTooFrequent` 攜剩餘秒數，經新變體 `AppError::BizData` 與信封之獨立攜明細出口上 wire；受眾判準＝明細是否只是操作者自陳輸入之評估結果；`5003` 與改密節流等其餘拒因恆純 key；違規子鍵譯文落 page 樹單一命名空間 | — | — | — |
| ADR-00077 | accepted | 2026-10-05 | 自助路由白名單為碼內常數 `SELF_SERVICE_ROUTES`、於 casbin 過濾之後恆併入 getUserRoutes——以「業務 menu 射程＋`hide_in_menu` seed 實值」二支柱對憲法 §I.2 立論、只收受眾＝本人之自助頁；身分注入形增 `sid`（ADR-00014 後果段「注入形不變」句自本刀起不再成立）；003 刀與 005 刀照帶之「不帶回」前提翻轉 | — | — | — |
| ADR-00078 | superseded | 2026-10-05 | 設密冷卻與改密舊密節流刻意分家——冷卻走設定鍵、維度（標的, 操作者）、借經手表時戳、零豁免；節流走碼內常數 5 次／900 秒、redis 計數桶 `cpwd:{uid}`、舊密比對之前拒、fail-open 並計入節流降級第十一源 `redis_change_pwd`；ADR-00038 射程限登入節流；通用節流 seam 以 rev6 形重做四面比較後不建（BL-00124） | — | — | ADR-00090 |
| ADR-00079 | accepted | 2026-10-05 | 密碼政策壞值方向——長度上下界矛盾（`password_min_length` ＞ `password_max_length`）時三個設密入口一律拒（安全側、不整組退預設），並以專屬計數族 `password_policy_invalid_total`＋告警規則 `obs016-password-policy-invalid`＋結構化 warn 為出口；設定寫端不加跨鍵守門；登入不受影響；與島 E「整組退」方向刻意相反之跨島理由（BL-00031） | — | — | — |
| ADR-00080 | accepted | 2026-10-05 | 部分更新語意（續行 ADR-00047）——系統設定與角色選單兩域續行；使用者域：可空文字欄空字串＝清空落 NULL（新增與更新同形）、缺席早退＋值 diff（同值零寫入零稽核、不 bump 時戳；早退位次在固定序⑤之首）、指派欄期望全集全量替換（界外整筆拒）；會話政策寫端值 diff 同形；並行編輯恆送欄後送出者為準（已知態）；逐域差異表 | — | ADR-00047 | — |
| ADR-00081 | proposed | 2026-10-05 | 角色與選單管理之已知態（續行 ADR-00068）——決定 4① 收回（觀察一律自建帳號持自建角色）；款 7 解除（`rev5:B-145` 結案）、款 18 解除（三頁按鈕依碼顯隱）；款 9 部分解除（使用者域寫端與 unlockLogin 帳號維受包含規則；可授出集重算為 30 支）；款 10、11、20 改述（按鈕碼顯隱後之可見效果／相異 R_SUPER 帳號可達／UI 外送停用值生產可達並實測）；其餘款續行（現行十七款） | — | — | — |
| ADR-00082 | proposed | 2026-10-05 | IP 域已知態集（續行 ADR-00069）——款 1 解除（帳號維＝使用者列「解鎖登入」、來源維＝IP 規則頁「解鎖來源 IP」兩處入口共用同一包裝）、款 3 操作稽核寫入者集擴列使用者域寫端八支與個人中心改密並以現行全集重述（封閉詞彙五詞→八詞）、款 5 複核本刀新增之 redis 狀態皆可自癒、款 6 受審讀型擴列、款 2／4／7／8 續行（現行七款） | — | — | — |
| ADR-00083 | accepted | 2026-10-05 | 使用者清單之 upstream 同 URL 型偏離帳——upstream `Api.SystemManage.User` 對 `Api.UserAdmin.UserRecord` 之欄差集由 wire 裁判自快照機器導出、釘值、漂移即紅（ADR-00044 決定 9 形、偏離帳第三列）；使用者管理頁改線 rev6 包裝、excel 示範頁為殘存消費面（所讀六欄皆共有欄） | — | — | — |
| ADR-00084 | accepted | 2026-10-05 | 繁中介面接上 runtime 並預設繁中——`LangType` 擴 `zh-TW`、locale／元件庫／日期庫三處註冊、未選過語言預設 zh-TW、語言下拉三語、`zh-tw.ts` 由治理錨點孤立檔改為 `App.I18n.Schema` 標型之完整 locale（續行並 supersede ADR-00039：譯文之家三檔不變）；ADR-00050 決定 1「zh-tw 不在對照面」之前提改述；繁中機器檢查之載體＝新碼面閘 `tools/zh-tw-lint.py`（四腿、讀面 (a)）；開發期根元件驗證器不改＝已知態；候選兩款未定案 | — | ADR-00039 | — |
| ADR-00085 | accepted | 2026-10-05 | seed-only migration m0003（rev6 首支 delta）——R_SUPER 名下角色與選單六碼改受保護（按鈕維受保護列首例）、刪 R_ADMIN `user:edit`（列 44）、增 R_SUPER `ipRule:unlock`（列 164）與 `manage_ip-rule` 按鈕清單一碼；seed 基線層直接改列、單一交易五句逐句斷言、前置不符整支回滾（fail-loud）；演進帳九筆＋schema 閘 seed_add 序號合成；走查還原工具之遷移帳前置與 seed 合成（兩模式之系統設定比對、清理面 seed 列照舊拒跑）；ADR-00064 背景「按鈕維受保護 0 列」之讀法 | — | — | — |
| ADR-00086 | accepted | 2026-10-05 | 選單編輯不得移除尚有受保護授權之按鈕碼——判定集＝本次移除集（含改碼之舊碼）∩ 持有受保護按鈕維授權列之碼、不問持有者；位次＝按鈕碼清單形制之後、絕版碼歸檔之前（⑨′）；違者整筆拒 `biz.menu.protectedButtonRemove`（純 key）、零變更零歸檔零稽核零同步；與受保護選單守門並列、拒因分鍵（承島 G 之 G2：受保護集只在 seed 基線層變更） | — | — | — |
| ADR-00087 | accepted | 2026-10-05 | schema 定稿權威留 001 基線（續行並 supersede ADR-00012）——`schema-definition.md` 各節不隨刀前進、其後刀之結構與 seed 變更只登演進帳、現況看實庫照相；表數斷言改屬基線恆真（BL-00047 收）；新表歸屬直接登記 `archetype-map.json`（§1 留基線 15 表）；其餘決定原文續行 | — | ADR-00012 | — |
| ADR-00088 | accepted | 2026-10-06 | 組裝形 workflow 的 agent prompt 不帶深思關鍵詞——思考深度只由 effort 承載，兩支 harness 以寫死字面守 | — | — | — |
| ADR-00089 | accepted | 2026-10-06 | SDD 刀 plan 期 ADR 之親決分類——待決一題一問、承決與工程不逐款問，轉 accepted 前以對照表一題收尾 | — | — | — |
| ADR-00090 | accepted | 2026-10-12 | 設密冷卻與改密舊密節流（續行 ADR-00078）——決定 2 改寫：改密節流桶之判讀與推進皆在帳號鎖持有期內（撤除開交易前之預檢、舊密不符於交易回滾之前推進）＝同一帳號並發請求合計之單窗上界嚴格；桶值不可遞增時於下一次推進原子自癒為 1（warn、不計降級）；鎖內兩次快取往返各以 1 秒為上界（逾時照降級放行）；決定 1、3～6 照錄續行；新增決定 7 現在式面改指 | — | ADR-00078 | — |
| ADR-00091 | proposed | 2026-10-14 | 部分更新語意（續行 ADR-00080）——決定 1～6、8 原文續行；決定 7 改寫：使用者編輯抽屜之會話政策呼叫被拒（更新呼叫已生效）後留原地重試時，`status`／`roleIds` 之改動判定改以已生效值為比對基準；決定 9 改寫：現在式面 ADR-00080 改指本 ADR、與本 ADR 轉 accepted 同顆 | — | — | — |
