# 003-auth-session 規格對照審查（spec-compliance-003、2026-09-15）

範圍＝已收刀之 003 auth-session 刀對 `specs/003-auth-session/` 的兌現度：spec.md FR-001～FR-040、SC-001～SC-012、User Story 1～6、Clarifications Session 2026-09-08 Q1～Q4、Edge Cases，連同 data-model §1～§14、`contracts/wire-auth.md`、`contracts/wire-route.md`、`contracts/msg-keys.md`、`contracts/code-gates.md` §1～§7。對照基準＝HEAD 現況（外層 `4f8d607`／rust-api `e907b53`／base-web `ff528496`）；003 收刀範圍（外層 `84caa8b..51ab7c7`、rust-api `4ebd6ce..d6c9661`、base-web `50812f89..1584407e`，merge `0e74551`、簿記 `f88db3d`）只作歸因。偏離有憲法／ADR／BACKLOG／clarify／commit 所引拍板承載者不報。specs 本文不改（ADR-00012 定點快照；user 2026-09-15 裁定）。

## 0. 方法與取證

| 項 | 值 |
|---|---|
| 形式 | RL-0073 承載處②：user 2026-09-15 臨時發起、附屬 003 刀；分支 `maint-spec-compliance-003`（自 `rev6-admin-root @ 4f8d607`，即 spec-compliance-002 收單後） |
| 編排 | 一支唯讀 Workflow（run `wf_986564f0-f2d`；review 骨架 explore＋inline 兩鏡三態；最壞 21 支／保險絲 22）：六支 lens＋一支冷啟動探針，派 21 支、零錯零 null、牆鐘 47.8 分鐘；全角色 `opus[1m]` xhigh |
| lens | L1 會話產品面（US1～US3：FR-001／002／004～011／018～021／032／033、SC-001～003／006、Q1／Q4、data-model §1／§2／§4～§7／§10／§12）｜L2 節流、captcha、替代登入、碼表與治理（US4～US6：FR-003／012～017／022～025／029／031／034／035／038～040、SC-004／005／007 後端／008／009 憲法面／010～012、Q3、data-model §3／§6／§8／§9／§11）｜L3 四契約與 wire 面（wire-auth／wire-route／msg-keys／code-gates §1～§7、data-model §11～§14、FR-027／036／037、Q2）｜L4 base-web fork-delta×憲法 §III（FR-026／028／030、SC-007 前端／SC-009，逐檔核標記形與軌道授權）｜L5 收刀後變動承載歸因（`0e74551`／`d6c9661`／`1584407e`→HEAD、`51ab7c7` 處置、BL-00043～00069 現況、現在式面）｜L6 測試與閘保護力（八組不變式之變異推演） |
| 探針 | P1 三題（access 過期與並發換發／節流矛盾設定之降級／在登入頁加欄之標記與授權），grader 判分＋refuter 覆核衍生 finding |
| 002 輪經驗 | CONTEXT 烤入五條：修法落點會使既有 BL 到期者須明寫／逐字出自 accepted ADR 或 specs 之句不得單改現在式面／evidence 須可原樣重跑／不逐檔列易漂移名冊／spec-compliance-002 已處置者不重報 |
| 規則塊 | `rules emit --scope review` 全塊烤入，RULES-VERSION `a2721b391067` |
| 唯讀邊界 | agent 禁寫入形命令、禁 docker／cargo／pnpm／generate；rev5 樹只讀（各 lens 自陳僅唯讀 grep、零 git 操作）；python 工具之保護力以記憶體內 exec 變異取證 |
| 主線復核 | 26 筆逐筆重讀證據與兩鏡理由；另親核 rev5:ADR 0059 全文與 logout.rs 碼註（L1-5）、憲法 §I.7 島 E 與跨島總則、ADR-00026 後果段「跨島總則受 MAJOR 閘保護」、throttle `precheck` ①早退碼（L2-2）、`jwt::ttl_from_settings`／enforce `update_last_activity_best_effort`（L1-1／L6-1）、base-web 修改型標記實形（L4-3／P1-P2）、msg-key-gate 真 repo Biz 形（L3-1）；兩輪變異抽驗見 §3 |
| 未覆蓋 | SC-001／SC-002 之 CDP 端到端與前端重放、前端 typecheck（歷史紀錄承載＝`6c8eb60` T076）；L4 列出之行為面 CDP 抽驗項未做（全為已有承載或已轉 BL 之面） |

## 1. 結論

**零 blocker、零 wire 行為缺陷。** 003 的四份契約逐列與 HEAD 一致（碼／msg／HTTP 零偏離）；五座行為島的降級方向、rotation／reuse／grace、三區節流、captcha、碼表 9＋4、MSG_KEYS 13 與前端三檔雙向全等、ROUTES 16、base-web 修改型 19 處授權判定皆兌現；收刀後改動 003 所建面的變動全部找得到承載（003 行為面在 HEAD 零行為改動）。

要處置的集中在三類：①**測試保護缺口**——login 第⑥步 TTL 兩腿、last_activity 兩寫端 TTL、「驗章前擋」次序、第⑩步成功列 fail-loud 臂、idle 門檻隨設定現值、getUserRoutes home 兜底接線、msg-key-gate 斷言 2 之同義構造形、子庫 pre-commit 接線、fork-delta-lint template 形與修改型樓地板守；②**現在式文件失準**——sys_role 模組 doc 消費者宣稱、throttle `lock_ttl_secs` doc、活書 08 §8.4 標記定形、README／RUNBOOK 手抄案數、rules.yml 過期 label 名單；③**兩筆須 user 拍板的偏離**——logout 呈遞 rotated 票不撤會話（立 ADR-00033）、L1 鎖命中不讀設定現值抵觸憲法跨島總則（BL-00066 留帳至 004 收斂）。

## 2. findings 與三分流（26 筆：修 16／轉 BL 4／won't-fix ADR 1；駁回 4、併入 1）

| 編號 | 嚴重度 | 類別 | 面 | 一句話 | 處置 |
|---|---|---|---|---|---|
| L1-1 | minor | 測試保護缺口 | login 第⑥步 | TTL 讀設定現值與缺失 fail-loud 5000 兩腿在 login 端點零測試，改成固定預設值全測照綠 | 修 |
| L1-2 | major | 現在式文件失準 | `sys_role.rs` 模組 doc | 稱 `enabled_roles_of_user` 供 login／getUserInfo 取角色，實際零生產消費者 | 修 |
| L1-3 | minor | 測試保護缺口 | `route.rs` `get_user_routes` | `resolve_home` 兜底接線零端點測試：seed `role_home` 恆為可導航葉，架空兜底全測照綠 | 修 |
| L1-4 | minor | spec 自身缺陷 | FR-004／data-model §3 | 稽核成功列「txn 內原子」與「best-effort」字面不可兼得 | 駁回（real 鏡） |
| L1-5 | minor | spec 自身缺陷→by-design 偏離 | `logout.rs` no-op 第四款 | 驗章成功之 rotated 票回 0000 不撤會話，偏離 FR-010 字面，rev6 無 ADR 承載 | ADR-00033（user 拍板） |
| L2-1 | major→minor（decided 鏡） | 現在式文件失準 | throttle `lock_ttl_secs` doc | doc 宣稱「負快取不得比權威源更嚴」，但 L1 可比 L2 多擋至多近一個窗長 | 修（decided 鏡改判：非違島 E、是碼註假述） |
| L2-2 | major | 無承載偏離 | BL-00066 × 憲法 §I.7 | L1 鎖命中早退不讀三門檻鍵現值，抵觸跨島總則「節流三鍵於每次登入嘗試讀現值」，BL-00066 只歸因於 data-model 措辭 | 轉 BL-00066（user 拍板留帳、004 收斂） |
| L3-1 | minor | 測試保護缺口 | `tools/msg-key-gate.py` 斷言 2 | 只認字面 `AppError::Biz(`：`Self::Biz(`、裸 `Biz(`、夾空白、函式值形之動態構造皆漏 | 修 |
| L3-2 | minor | 測試保護缺口 | `test_hook_wiring.py` | 子庫 `.githooks-submodule/pre-commit`（兩源倉 commit 期唯一機密掃描）不在 hook 接線守衛名冊 | 修 |
| L3-3 | minor | spec 自身缺陷 | msg key 譯文權威 | 憲法 §III.2 與 ADR-00029 把譯文權威定於凍結的 contracts/msg-keys.md，後刀新鍵譯文無活體之家 | 轉 BL-00042 ②（兩鏡不確定、主線裁定併入同題） |
| L3-4 | minor | spec 自身缺陷 | wire-route §isRouteExist | 契約漏記顯示域謂詞 | 駁回（decided 鏡：research rev5 對應碼清單已承載） |
| L4-1 | minor | 無承載偏離 | base-web `service/request/index.ts` | 4040／5003（HTTP 404／403）信封 msg 未經 `translateBackendMsg`，rev5:B-117 塊未帶入 | 轉 BL-00077 |
| L4-2 | minor | 契約漂移 | `tools/fork-delta-lint.py` `MARKER` | `.vue` template 修改型標記形 `<!-- … 原行: … -->` 之行尾 `-->` 被捕進原行值、必誤判缺原行（潛伏） | 修（驗證員提 BL、主線改判） |
| L4-3 | minor→major（real 鏡） | 現在式文件失準 | 活書 08 §8.4 | 新增型區塊定形寫成必帶 `(<用途>)` 且稱 as-built 七塊同形，pwd-login.vue 兩塊無用途後綴 | 修（P1-P1 併入） |
| L4-4 | minor→major（real 鏡） | 測試保護缺口 | `tools/fork-delta-lint.py` main | 「修改型 0 處＝合法 vacuous」之前提「rev6 base-web 零 inline」已失效（HEAD 19 處），樓地板守未恢復、docstring 與輸出訊息假述 | 修（驗證員提 BL、主線改判） |
| L4-5 | minor | 測試保護缺口 | 憲法 §III.2 表外宣告 3 | 新增型標記不過三元組判定 | 駁回（decided 鏡：宣告 3 明文取捨） |
| L5-1 | major→minor（decided 鏡） | 現在式文件失準 | README／RUNBOOK §12 | msg-key-gate 自測案數分項手抄兩列、零機器對賬 | 修 |
| L6-1 | major | 測試保護缺口 | login ⑪／enforce 放行後 | `last_activity` 兩寫端 TTL＝refresh 全壽命無判別測試，誤寫 access_secs 時島 D idle 靜默失效 | 修 |
| L6-2 | major | 測試保護缺口 | login ②③ 次序 | 島 E「軟區與鎖定 MUST 在密碼雜湊驗證之前擋下」無判別測試，把 precheck 挪到 authenticate 之後全測照綠 | 修 |
| L6-3 | minor | 測試保護缺口 | refresh idle 門檻 | 「idle 門檻於每次換發讀現值」無判別測試，門檻寫死 3600 全測照綠 | 修 |
| L6-4 | minor | 測試保護缺口 | login 第⑩步成功列臂 | 「寫失敗不得吞→rollback→5000」臂無測試或源序守，改成 `let _ =` 全測照綠 | 修 |
| P1-P1 | minor | 現在式文件失準 | 同 L4-3 | 探針 grader 衍生、decided 鏡確認 | 併入 L4-3 |
| P1-P2 | minor | fork-delta 標記或授權失準 | 活書 08 §8.4 | 「★ 軌道修改型標記必帶用途後綴」在現在式面無家、未寫明 lint 三元組射程只到修改型 | 修（decided 鏡刪去併入 BL-00058 之附帶提議） |
| P1-P3 | minor | 現在式文件失準 | `rules.yml` ② | `obs016-throttle-suppressed` 錨在 rev6 不存在的 `suppressed=N` 事件、結構上永不觸發 | 轉 BL-00078 |
| P1-P4 | minor | 現在式文件失準 | `rules.yml` ③a 註解 | 列 14 個 rev5／rev4 label 並稱 obs.rs 全數預註冊，實為七值且含 `settings_invalid` | 修 |
| P1-P5 | minor | 檢索性 | 活書 06 §6.1 ③ | partial UNIQUE 重入易被讀成同票並發主路徑 | 駁回（decided 鏡：10 §島 A 已寫真實收場） |

### 三分流細節

**修（16 筆）**——落於本輪修單：

- **L1-1**：login 測試模組加兩案——`login_idle_timeout_setting_missing_is_5000_with_zero_rows`（`session_idle_timeout` 列暫軟刪→5000＋`system.internal`、零憑證列、高水位後零稽核列）與 `login_issues_pair_with_ttl_from_current_idle_timeout_setting`（暫改 N=10→所簽 refresh `exp−iat`＝900）。落點不在 BL-00062（logout.rs）與 BL-00070（未列 login.rs）射程；案冊碼註 19→22 同批改（decided 鏡補正 proposed 漏項）。
- **L1-2**：`sys_role.rs` 模組 doc「兩支的分工」首項改為「現無生產消費者（三端點取角色一律經 `sys_user_role::roles_of_user`、以 grep 為準）、只供本檔雙源恰等案對賬」；第 5～9 行謂詞分岔段保留（decided 鏡：該段於 HEAD 仍成立）。
- **L1-3**：route.rs **另立** `home_fallback_tests` 模組加 `user_routes_home_outside_visible_tree_falls_back_to_first_navigable_leaf`（暫把 User 角色 `role_home` 改成樹外名→回包 `home` 須＝先序第一可導航葉）。不落 `integration_tests`：該模組自持 `get_json` 殼屬 BL-00070 射程，增案即到期（`e0dd22b` L5-4）；不落純函式 `tests`：decided 鏡指出混入真 DB 案破壞分層。新模組改走 test_kit `get_with_bearer`；`integration_tests` 案冊碼註同批補指針。
- **L2-1**：`lock_ttl_secs` doc 改為實述「保證鎖期不長於武裝當下的計數窗；★不保證不比 L2 嚴（TTL 自武裝起算、命中不重讀 L2，最早失敗列出窗時 L2 已解鎖、L1 仍可再擋至多近一個窗長＝BL-00066）」，刪去誤引之 data-model §8。純註解、不觸 BL-00066 到期。
- **L3-1**：斷言 2 比對面擴為 `AppError::Biz(`／`Self::Biz(`／經 use 匯入之裸 `Biz(`（`::` 與 `(` 間容空白），另把函式值形 `AppError::Biz`／`Self::Biz`（不帶括號、`use` 行除外）判為動態構造（real 鏡實測 `map_err(AppError::Biz)` 同樣漏網），`enum AppError { … }` 本體內之變體宣告以 brace 配對排除。self-test 加⑩b 一案（四形各紅、use 行／合法常數形／enum 變體宣告不誤報），真 repo `check` 仍綠（Biz 構造點 9 處）。屬既有斷言比對面擴到同義語法形、非新能力面（decided 鏡比照 `eb4c520` L3-3），不需新 ADR；BL-00074 觸發未觸及。
- **L3-2**：`test_hook_wiring.py` HOOKS 名冊加 `sub-pre-commit`，新增 `check_sub_precommit`（betterleaks 呼叫緊接 `rc=$?`、rc 0 放行、rc 2 命中分支、非零收尾 `exit 1` 四字面）與 `TestSubPrecommitWiring`（真檔零 finding、刪任一字面紅指名）；模組 docstring 與 `.githooks/pre-commit` 段註之「四檔名冊」同批改「五檔」（errata 枚舉；specs/003 兩處史料面不動）。
- **L4-2**（驗證員提 BL、主線改判修）：`find_missing` 對以 `<!--`／`/*` 起首之標記行，剝除原行值行尾一次 `-->`／`*/` 後再比；`//` 標記原行尾端照原樣。self-test 加 D2（template 單行 HTML 註解形須過）／D3（原行值不符仍攔）。改判理由：與 L4-4 同檔同批、改動在工具內且有自測載體，BACKLOG 淨流量已超標。
- **L4-3＋P1-P1**：§8.4 新增型定形改為「用途後綴選配」，補單行新增型形，as-built 處數改「以 `grep -rn 'rev6-inline' base-web/src` 為準」。
- **P1-P2**：§8.4 同段補修改型定形（★ 軌道必帶用途後綴、§III.1 ADAPT 根層 `.env*` 裸形）與 lint 機器守射程（修改型驗原行與三元組；新增型只驗 token 在場、不過三元組＝表外宣告 3）。decided 鏡駁回 grader 附帶之「併入 BL-00058 追加子項」：憲法 177 行為「如」字示例、BL-00058 為 user 已拍板之射程，不擅改。
- **L4-4**（驗證員提 BL、主線改判修）：抽 `floor_violation(checked_total)`，`checked_total < 1` 由印 ⓘ 改為 `die`（rc 2、訊息指「掃描面塌縮或標記整批遺失」）；self-test 加 FL；模組 docstring 兩處「零 inline」改為 002 刀當時的歷史敘述。實跑 lint 對真 repo 仍 rc 0（修改型 19 處）。
- **L5-1**：README 樹列、RUNBOOK §12 工具鏈速查列與碼面閘表列之 msg-key-gate `test` 描述改為只列案類、「案數以 `test` 輸出為準」（承 ADR-00029 決定 3）；工具 docstring 同改。decided 鏡指出 proposed 所引 LL-00009 出處錯誤（該 LL 為 tracing 捕捉之坑），本輪修法未引。
- **L6-1**：`login_success_starts_last_activity_clock_with_real_redis` 之 TTL 下界由 0 改為 idle 門檻＋餘裕（(3600, 3900]），並以登入所得 access 打一次 getUserInfo（enforce 放行後推進）重讀 TTL 套同一區間＝enforce 寫端一併守到，不動 `auth/enforce.rs` 測試模組（BL-00070 射程）。
- **L6-2＋L6-4**：login 測試模組加純函式判準 `precheck_precedes_authenticate`／`success_audit_arm_is_fail_loud` 與源序守案 `login_source_order_precheck_before_authenticate_and_success_audit_fail_loud`（形同 refresh.rs 唯一鍵衝突臂守；真正文過兩判準、合成反序／吞錯／臂落 commit 後三樣本皆判否＝RL-0051）。
- **L6-3**：refresh 測試模組加 `refresh_idle_threshold_follows_current_idle_timeout_setting`（N 暫改 30、陳舊度 1800＋120 之 last_activity 換發得 8888；還原 seed 後同陳舊度另一條鏈換發 0000＝對照腿）；案冊碼註 18→19。
- **P1-P4**：rules.yml ③a 註解之 14 label 枚舉改為指針「label 值集＝obs.rs `THROTTLE_DEGRADED_SOURCES`（以該常數為準）」，刪去 rev5 Gmail 判讀半句；零 expr 改動。

**轉 BL（4 筆）**：

- **L2-2 → BL-00066**（user 2026-09-15 拍板＝留帳）：條文補「抵觸憲法 §I.7 跨島總則」與 user 拍板、收斂二擇一（改碼使 L1 命中仍以 L2＋設定現值複核，或走 §V.2 Amendment 把 L1 例外寫入跨島總則——ADR-00026 後果段明言跨島總則受 MAJOR 閘保護），觸發改為「004 ip-trust-anchor brainstorm 起手前，或下次動節流三區或設定鍵熱更新面時」；L2-1 所述「設定不變時 L1 亦可多擋近一個窗長」同批記入。decided 鏡指出：`51ab7c7` L3-2 之「有界已知態」屬主線處置、非 user 拍板，延續憲法偏離須 user 過目（比照 BL-00058）。
- **L3-3 → BL-00042 ②**（uncertain、主線裁定）：real 鏡補出決定性證據——憲法 1.3.0 §III.2 I18N-WIRING (ii) 列本身即把譯文權威定於凍結 spec 檔，故改權威須走 Amendment；decided 鏡建議併入 BL-00042（跨刀活體契約仍住 spec 目錄）以免同題兩家。條文加②與獨立觸發「首個新增或改名 msg key 的刀開寫前」。
- **L4-1 → BL-00077**：屬 user 可見行為變更且需 CDP 對照驗收，現況可達面僅 R_SUPER 之 demo 頁；觸發＝首個會碰到 HTTP 403／404 信封的 UI 刀，或 BL-00067 決定 demo 頁去留時。
- **P1-P3 → BL-00078**：刪或留規則屬 compose 掛載之 runtime 設定、非純文字小修；`rev5:R3-3` 已判不做，刪除為預設候選；觸發＝004 brainstorm 起手前。

**won't-fix／by-design ADR（1 筆）**：

- **L1-5 → ADR-00033**（user 2026-09-15 拍板）：logout 呈遞 rotated（及 revoked）票＝0000 靜默 no-op、撤銷射程恆為單列，承 rev5:ADR 0059 之理由（異碼＝有效性 oracle、撤全鏈路徑綁 reuse 攻擊事件）；已知代價（多分頁競態下另一分頁會話續活）與翻案觸發器入 ADR；logout.rs 碼註補指針（純註解、不觸 BL-00062）。decided 鏡指出 proposed 原提「碼註補 rev5 指針」不足：憲法 §I.5／ADR-00014 背景要求前代拍板以 rev6 自立 ADR 承襲，且多分頁代價屬 user 可見行為。

**駁回（4 筆）**：

- **L1-4**：real 鏡駁回——「兩者不可兼得」證據不足（SAVEPOINT 可同時滿足兩條字面）；decided 鏡另指出 spec 套件在 research R5 與 wire-auth 已把 best-effort 收窄到失敗列，HEAD 取原子性並承 rev5 藍本。
- **L3-4**：research.md rev5 對應碼清單把 `handler/route.rs`（含 isRouteExist）列「A／同」、rev5 藍本即顯示域形，契約簡寫不構成缺陷。
- **L4-5**：新增型不過三元組是憲法 §III.2 表外宣告 3 的明文取捨，現在式面無一處宣稱新增型受三元組機器守。
- **P1-P5**：活書 10 §島 A 回應欄已寫同票並發之真實收場，06 §6.1 ③ 亦有 `rotated`→grace 分支，不可達推導住該常數 doc。

### 驗證鏡對 lens 陳述的更正（記載）

- L1-1：proposed 漏改「案冊恰 19 支」碼註（RL-0011）。L1-3：落 `mod tests` 會使 `integration_tests` 檔頭案冊句失準，且真 DB 案混入純函式模組破壞分層。
- L1-2：改寫時不宜替零消費者函式補「存在理由」，只直述現況。
- L2-1：「違島 E／無承載偏離」定性不成立（L1 鎖期上界＝窗是拍板的必然結果）。L2-2：proposed 出路 (b) 不可預寫 MINOR（ADR-00026 後果段：跨島總則受 MAJOR 閘保護）。
- L3-1：漏洞比 summary 所列更寬（函式值形 `map_err(AppError::Biz)` 同樣漏網）。
- L5-1：「與 ADR-00029 決定 3 相悖」言過其實（現值 19 與 test 輸出一致）；proposed 所引 LL-00009 出處錯誤。

## 3. 驗證（主線實跑）

| 項 | 值 |
|---|---|
| 新增與加強之 Rust 案（真碼） | 容器內 `rustfmt`（僅三個改動檔）後 `cargo fmt --all --check` 綠；`login_idle_timeout_setting_missing_is_5000_with_zero_rows`／`login_issues_pair_with_ttl_from_current_idle_timeout_setting`／`login_source_order_precheck_before_authenticate_and_success_audit_fail_loud`／`login_success_starts_last_activity_clock_with_real_redis`／`refresh_idle_threshold_follows_current_idle_timeout_setting`／`user_routes_home_outside_visible_tree_falls_back_to_first_navigable_leaf` 六案綠；前後 `walkthrough-baseline diff` 皆全等 |
| 變異抽驗輪 A | 五發同時打上（M1 login 第⑥步 TTL 讀取失敗改回固定值／M2 login ⑪ last_activity TTL→access_secs／M4 第⑩步成功列臂改 `let _ =` 吞錯／M6 refresh idle 門檻寫死 3600／M7 route 兜底改 `resolve_home(&[], home)`），跑 login／refresh／route／enforce 四模組 69 案→**只有** `login_idle_timeout_setting_missing_is_5000_with_zero_rows`（M1）、`login_success_starts_last_activity_clock_with_real_redis`（M2）、源序守案（M4）、`refresh_idle_threshold_follows_current_idle_timeout_setting`（M6）、`user_routes_home_outside_visible_tree_falls_back_to_first_navigable_leaf`（M7）五案紅、64 綠 |
| 變異抽驗輪 B | 兩發（M3 enforce 放行後 last_activity TTL→access_secs／M5 login precheck 整段挪到 authenticate 之後），跑 login／enforce 兩模組 45 案→**只有** `login_success_starts_last_activity_clock_with_real_redis`（M3）與源序守案（M5）紅、43 綠（enforce 既有案全綠＝缺口屬實） |
| 變異抽驗輪 C | 一發（login 第⑥步改為不讀設定、寫死 `TokenTtl { 300, 3900 }`；輪 A 之 M1 只變異失敗腿、打不到「讀現值」判準，故補此輪），跑 login 模組 22 案→**只有** `login_idle_timeout_setting_missing_is_5000_with_zero_rows` 與 `login_issues_pair_with_ttl_from_current_idle_timeout_setting` 紅、20 綠。三輪變異檔皆以 sha256 還原自證、rust-api porcelain 只剩本輪六檔、前後 `walkthrough-baseline diff` 全等 |
| 全量 | 容器內 `cargo test --workspace --no-fail-fast` 440 綠／0 紅／2 ignored（含本輪新增 6 案），測後 `walkthrough-baseline diff` 全等 |
| 工具自測與真 repo 實跑 | `msg-key-gate.py test` 20 案全綠、`check` 真 repo 綠（Biz 構造點 9 處、前端消費點 1 處）；`fork-delta-lint.py test` 過、全掃 rc 0（修改型 19 處授權皆合、新檔 5 支）；`docsync test` 279 案唯一紅＝generate 前之 GT-01 生成檔漂移（真 repo lint 案），generate 後由 pre-commit check／lint 復驗 |

## 4. 冷啟動探針（只入報告與事件 notes、不填事件 `probe` 欄）

| 題 | 判分 | 探針跳數／最短跳數 | 註 |
|---|---|---|---|
| Q1 access 過期時後端回碼與前端流程；同票並發換發結果；真源 | 繞路 | 9／5 | 3333 只在簽章有效而 exp 已過；前端 `refreshTokenPromise` 同分頁單飛；後到者阻塞列鎖、見 rotated＋grace 命中回同一對；真源鏈＝憲法 §I.3／§I.7 島 A／C→活書 08／06→碼註 |
| Q2 `login_throttle_captcha_after`＝6、`max_fails`＝5 之實際運作與可見面 | 繞路 | 6／4 | 002 寫端逐鍵驗、寫得進；消費側整組退常數（5／15／2）並發 `settings_invalid` 告警；log target `security.throttle`、metrics `throttle_degraded_total{source}`、Grafana `obs016-throttle-degraded` |
| Q3 在 `pwd-login.vue` 加一個輸入欄位之標記、授權與機器閘 | 繞路 | 5／4 | 屬 ★LOGIN-CAPTCHA-WIRING (i) 軟區補完者不 bump、其他用途須 §V.2 Amendment；修改型帶用途後綴與 `原行:`、新增型圈界；`fork-delta-lint.py` 三元組只驗修改型 |

找不到 0、答錯 0。不填 `probe` 欄之理由同 spec-compliance-002 報告（檢索性列取最近一筆帶 `probe` 之 review 事件、不分 scope、比輪間不降，題組不同質）。

grader 對探針 suggestion 之處置：採納者成為 P1-P1～P1-P4（其中 P1-P5 經 decided 鏡駁回）；未採納——Q1「無文件量化前端最壞重試間隔」不實（`cache/mod.rs` `GRACE_TTL_SECS` doc 已寫約 11 秒）；Q2「RUNBOOK §3 補節流降級查法」由觀測刀承載（000-r1 R1-C214 先例）、「BL-00031 條文未刪 003 對鍵」不實（`6c8eb60` T078 已改觸發欄）、「寫端回饋矛盾組合」屬 user 可見行為變更且 clarify Q3 已拍板。

## 5. 建議（未列為 finding）

1. **rules.yml 其餘事件錨**（grader 範圍外觀察）：③b `ipgate/mod.rs`、③d `middleware/mod.rs` 之 `access_log_mw`、`auth/enforce.rs` 之 `casbin_reload_total` 皆錨向 rev6 尚不存在的發射點，分屬 004／008／觀測域、非 003 引入；BL-00078 兌現時可擴成「rules.yml 事件錨對 rev6 as-built 全面對賬」。
2. **L6 推演存活但後果窄的變異**（lens 自陳未報）：login 第⑤步刪密碼雜湊比對（需改密寫端競態、007 前無寫端）、第⑩步落點改外層 conn（原子性只在 commit 失敗時可觀察）、`detect_reuse`／logout 之 TTL 讀取搬回 txn 內（只有查庫失敗腿可觀察）。
3. **L1 已查不報之觀察**：被踢者 denylist TTL 取踢人者登入當下之 N（設定改小後被踢者晚段換發降為靜默 8888＝跨島總則下的有界已知態）；`resolve_home` 以 children 缺席判葉，自身可見而子項全不可見的目錄會被當可導航葉（seed 無此形）。
4. **L4 列出之 CDP 抽驗項**（軟區驗證碼出圖與換題、7777 modal 人話、三表單「尚未開放」toast、captcha 送碼不倒數、demo 頁 4040 toast）本輪未做：前四項為 003 U11 走查已驗之 as-built，末項已轉 BL-00077 由該刀 CDP 驗收。

## 6. 判定

**需要後續處置：是（本輪即處理完）。** 十六筆修落於本輪修單、四筆轉 BL（其中 BL-00066 經 user 拍板留帳至 004 收斂）、一筆立 by-design ADR-00033（user 拍板）、四筆駁回、一筆併入；specs 本文與憲法零改動。
