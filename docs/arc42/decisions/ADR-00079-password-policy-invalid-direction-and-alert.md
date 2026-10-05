---
id: "ADR-00079"
title: 密碼政策壞值方向——長度上下界矛盾（`password_min_length` ＞ `password_max_length`）時三個設密入口一律拒（安全側、不整組退預設），並以專屬計數族 `password_policy_invalid_total`＋告警規則 `obs016-password-policy-invalid`＋結構化 warn 為出口；設定寫端不加跨鍵守門；登入不受影響；與島 E「整組退」方向刻意相反之跨島理由（BL-00031）
date: 2026-10-05
status: proposed
supersedes: []
superseded_by: []
provenance: "007-user-password-admin 之 spec FR-034（設密全拒、告警出口三件、不併入節流降級計數、寫端不守、登入不受影響、跨島註）、FR-032（單一驗證點、消費當下讀現值、登入不驗）、FR-038（政策讀端投影）、FR-060（BL-00031 backlog_done）、FR-063（政策矛盾全拒＋告警之自證）、US3 AS3、SC-006、Edge Cases「密碼面」段；brainstorm §0 Q19、§1「min>max 安全側恆拒」與「密碼政策整套」兩列；spec Assumptions 所記 clarify 步主線工程判斷（FR-034 專屬計數族＋新告警規則）；plan 期主線定案（計數族名、預註冊、發射出口與恰一處、告警規則 uid／title／expr／門檻、warn 一則）；藍本＝rev5:server/src/model/password.rs（`validate_against_policy` 之「min > max 安全側恆拒」、`policy_from_pairs` 逐欄 fail-default、`PasswordPolicy` 之 Default＝seed 值；前代無告警）；rev6 前例＝ADR-00038 決定 4（節流設定矛盾整組退常數＋告警、寫端不守）、憲法島 E 設定壞值句與既有跨島註（`session_idle_timeout` fail-loud 對島 E fail-open）、`obs::ipgate_blocked`（無 label 計數族、預註冊、發射點恰一處之形）、deploy/grafana-provisioning/alerting/rules.yml 之 `obs016-*` 命名；設定界值權威＝`validation::REGISTRY`（ADR-00054；`password_min_length` [1,128]、`password_max_length` [1,256]、seed 8／64）；對沖條目＝BL-00031；跨島註條文字面由 ADR-00074 於本刀 U0 親決；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [password, settings, observability, behavior-island, user-password-admin]
---

## 背景

- 002 刀之設定 registry 逐鍵驗型與界、跨鍵零守：`password_min_length`（[1,128]）與 `password_max_length`（[1,256]）各自合法即可寫成 min＞max（BL-00031；觸發＝消費側進場＝本刀）。設定寫端至 008 刀前無畫面、只能經受保護之 updateSystemSetting（R_SUPER）寫入。
- 兩對節流鍵之同型矛盾已拍「寫端不守、消費側整組退常數＋告警」（003 刀 clarify Q3、004 刀 brainstorm Q4＝ADR-00038 決定 4；憲法島 E 設定壞值句）。
- 前代 as-built：密碼政策逐欄 fail-default、min＞max 時任意長度必違反其一＝安全側恆拒、無告警——設密者只見長度違規、管理員無從察覺設定錯了。
- 憲法承襲指針表尾句：跨島刻意不一致隨各島進場一併重審；島 I 進場即本刀。

## 決策驅動因子

- 政策是設密面的守門：管理員以為更嚴時不得靜默放寬。
- 登入不受影響（島 I5：登入路徑不驗政策；seed 三帳號之密碼本即短於政策下限）。
- 設錯要被看見（明細＋告警），且告警標題不誤導。
- 三對設定之寫端取態一致；零新拒因鍵、零新違規碼。

## 考慮過的替代案

1. **設定寫端加跨鍵守門**（存 min＞max 即拒）：改動 002 刀已收刀之寫端、交易內須兩列鎖、與兩對節流鍵「寫端不守」不對稱；直改庫仍須消費側兜底。否決。
2. **消費側整組退出廠值**（比照島 E；長度一對退 8／64 並告警）：管理員本意更嚴（例：把下限調到 20 而誤設上限 10）時退回 8＝靜默放寬；島 E 退常數之理由（猜錯只影響阻力強度，而 fail-closed 會把所有人擋在登入之外）不適用於設密面；不可滿足組合不只長度一對、整組退須逐一列舉。Q19 否。
3. **沿前代安全側恆拒、不告警**：無觀測面，設密者看到的長度違規無從分辨是自己輸入錯還是設定錯。否決。
4. **告警併入 `throttle_degraded_total` 新源**：非節流降級；throttle-degraded 告警標題誤導；稀釋「降級序列有值＝基建出事」之語意。否決（spec FR-034）。
5. **只發 log、以日誌型告警承接**（比照 ipgate-degraded）：無預註冊基線、依賴日誌管線；無 label 計數族＋預註冊 0 已有 `ipgate_blocked_total` 同形先例。否決。
6. **矛盾時以專屬拒因鍵早拒**（「密碼政策設定矛盾」）：新增 msg 鍵、名冊與三語譯文；而自然收集之違規明細與政策讀端投影一致、對設密者誠實，設定錯誤之受眾是維運、由告警承接。否決。

對所選方案跑同一反例（RL-0013）：

- 「全拒擋住正當設密」：擋的只是三個設密入口，登入與一切既有會話不受影響；矛盾只能由持受保護設定寫端者造成、亦由其改正；告警即時。接受。
- 「靜默放寬」於所選方案下是否仍可能：min＞max 不退預設、不夾界、不改寫設定值；剩餘形＝單鍵異常之逐欄退出廠值（決定 4），只能由直改庫或缺陷形成（寫端經 registry 逐鍵驗型與界），列為已知邊界。
- 「全拒是否真全拒」：任意長度 L，若 L ≥ min 則 L ≥ min ＞ max ⇒ L ＞ max；否則 L ＜ min ⇒ 至少一條長度違規恆成立，無須特別分支。成立。

## 決定

1. **方向＝設密全拒**：`password_min_length` ＞ `password_max_length` 時，addUser 初始密碼、resetUserPassword、changePassword 三入口一律拒——由單一驗證點自然收集之長度違規（`minLength`、`maxLength` 之一或兩者）達成、不另立分支與拒因鍵；回 `2222`＋`biz.user.passwordPolicy` 攜違規清單（ADR-00076）。不退預設、不夾界、不改寫設定值。
2. **寫端不守**：updateSystemSetting 不新增跨鍵組合守門；三對設定之寫端取態一致（寫端逐鍵驗型與界、跨鍵不變式由消費側承載）——registry 不守跨鍵＝by-design。
3. **登入不受影響**：登入路徑不驗政策（島 I5）；矛盾期間既有帳號照常登入、既有會話不受影響。
4. **單鍵異常**（缺列、軟刪、不可解析〔含開關鍵值域外〕、越 registry 宣告界——只能由直改庫或缺陷形成）＝該欄逐欄退出廠值（seed 值：min 8／max 64／五開關 off＝`PasswordPolicy` 之 Default）、其餘鍵照用現值，並落 warn 一則（指名該鍵；target 與欄名見本刀 research R11）；界值取 `validation::range_of`、不另抄一份；不推本計數族。逐欄而非整組：七鍵彼此獨立，整組退會因一鍵壞值拋棄其餘已設之較嚴政策＝靜默放寬。逐欄退值後若形成 min＞max，依決定 1、決定 5 處置。前代逐欄 fail-default 形沿用（brainstorm §1「密碼政策整套」沿用列），越界判準為 rev6 增補（前代不驗界、越界值照用）。
5. **告警出口**（三件同腿、恰一處）：
   - 計數族 `password_policy_invalid_total`（無 label）：`obs::pre_register_metrics` 預註冊 0；出口 `obs::password_policy_invalid()`；發射點恰一處＝單一驗證件 `model::password::validate_against_policy` 判出 min＞max 之腿（三設密入口共經；getPasswordPolicy 只經載入件 `load_policy`、不經驗證件＝不計）——每次設密驗證至多一格；計數語意＝矛盾期間之設密驗證次數（設密被拒時才告警＝spec FR-034）。
   - 結構化 warn 一則（同腿；帶 min、max 現值、不含任何密碼材料；target 與欄名見本刀 research R11）。
   - 告警規則：`deploy/grafana-provisioning/alerting/rules.yml` 增 uid `obs016-password-policy-invalid`、title `password-policy-invalid`、expr `sum(increase(password_policy_invalid_total[5m]))`、門檻 > 0；依既有告警規則之活體驗證慣例實測。
   - 不入 `throttle_degraded_total`、不推任何降級序列。
   - 機器守比照 `obs::ipgate_blocked`：預註冊 0 一案、發射點恰一處之靜態掃描、序列名字面只住 obs 兩處（預註冊與出口）；矛盾時三入口各拒一案、計數＋warn 一案、登入照常一案（spec FR-063）。
6. **跨島理由**（條文字面由 ADR-00074 之跨島註承載）：島 E 設定壞值整組退常數、密碼政策長度矛盾設密全拒——方向刻意相反：①失效面不同：島 E 若改拒即把全體使用者擋在登入之外，密碼政策全拒只擋設密三入口（登入不驗政策）、恢復＝改正設定鍵；②猜錯之後果不同：島 E 退常數猜錯只影響阻力強度、且隨設定改正即消失，密碼政策退預設猜錯即以寬於管理員意圖之政策放行密碼、而放行之密碼落庫後不隨設定改正而失效（後果殘留）；③可見性：全拒即時以違規明細與告警現形。記之以免日後被「統一」。
7. **政策讀端**：getPasswordPolicy 照回載入件之七鍵投影（矛盾值照回；單鍵異常者為決定 4 之退值）、不另加旗標、不推計數；前端即時規則依投影呈現（矛盾期間提示不可同時滿足）、後端仍為唯一裁判。

## 後果

- BL-00031 收刀 backlog_done（承載＝本 ADR：registry 不守跨鍵＝by-design、消費側全拒＋告警）。
- 修復路徑：008 刀前無設定頁畫面，改正兩鍵須經 updateSystemSetting（R_SUPER）——造成矛盾者與改正者同一權限面；RUNBOOK §11 觀測層維運補本計數之判讀與處置（比照判定面同步計數之段）。
- 已知邊界：長度一對以外之不可滿足組合（例：上限小於須含之字元類別數）同樣由逐條違規自然全拒、但不被偵測、不告警；單鍵異常之逐欄退出廠值在該鍵原值較嚴時屬放寬。
- 碼面：`model/password.rs` 檔頭「本刀不落 `hash()`…密碼政策三支一併不帶」改現在式（RL-0011）；`obs.rs` 檔頭宣告面與 `pre_register_metrics` 補列新序列。
- 代價：矛盾期間三入口全面不可用、直到改正；告警為唯一主動訊號。

## 翻案觸發器

- 矛盾告警於生產面實際觸發、且全拒造成之中斷被判不可接受 ⇒ 重評替代案 1（寫端守門），並複核跨島註。
- 長度一對以外之不可滿足組合於生產面實際出現 ⇒ 擴偵測範圍（同一計數族或另立）。
- 008 刀設定頁進場 ⇒ 複核寫端是否加畫面前置提示或守門。
- 單鍵異常於生產面實際出現 ⇒ 複核決定 4（改為全拒或計數告警）。
- 新增政策鍵（例：密碼歷史、到期）⇒ 依本 ADR 方向判其壞值處置，更新決定 4、決定 5。
- 島 E 設定壞值方向或島 I5「登入不驗政策」反轉 ⇒ MAJOR、重審決定 6。
