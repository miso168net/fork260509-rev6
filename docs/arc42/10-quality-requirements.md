---
section: 10
summary: 品質需求概覽與情境；E6 AI 品質情境的系統層落點
rad_ai: [E6]
rad_ai_stage: 2
rev5_blueprint:
  §10 品質要求: 不承襲：rev5 空節；rev6 §10 自 §1.2 品質目標展開、情境隨島進場
---
# §10 品質需求

## 10.1 品質需求概覽

| 屬性 | §1.2 目標 | 量測 | 守門 |
|---|---|---|---|
| 安全性 | 安全 | 授權判定零快取（角色一撤、下一請求即生效）；fail-* 方向逐島明文；tracked 檔零機密實值 | 憲法 §I.2／§I.7；GT-07 |
| 契約一致性 | 契約守恆 | 每條 route 有 contract case、13 碼矩陣零偏離 | 憲法 §I.3；`rust-api/server/tests/contract.rs`（ROUTES×case 雙向覆蓋閘）／`src/error.rs` 13 碼矩陣斷言；wire 快照面另由 `tools/wire-schema.py`（碼面閘）守 |
| 可重現性 | 可重現 | 任一外層 commit 的 pin＝子庫 worktree HEAD；新機 bootstrap rc 0 | GT-02；`tools/bootstrap.sh` |
| 文件正確性 | 文件與碼零漂移 | generate 兩次同 bytes；名冊同源；預算表「內」 | GT-01／GT-12；STATE 預算對賬 |
| UI 一致性 | UI 與 rev5 一致 | CDP 三方比對零差異（rev5／rev6／example；已知例外＝四支未進場管理頁選單標題於側邊欄展開態顯裸鍵、帳住 BACKLOG，收合態零差異） | 走查流程（CLAUDE.md §7） |

## 10.2 品質情境

情境格式（每情境一個 `###`）：

| 欄 | 內容 |
|---|---|
| 刺激 | 誰在什麼環境下做了什麼（含異常：redis 失聯、PG 查詢失敗、鏈長逾上界） |
| 回應 | 系統的可觀察行為與方向（fail-open／fail-closed、降級腿） |
| 量測 | 可斷言的值：碼、HTTP status、序列計數、時限 |
| 守門 | 釘住該情境的測試或 lint |

情境五則＝憲法 §I.7 已入憲行為島 A～E 各一（島 F～J 的情境隨其進場刀入本節；承襲指針表＝憲法 §I.7）。每則只釘該島最容易被「順手統一」抹掉的 fail-* 方向（方向之凍結面＝該島入憲條文）；流的完整敘述住 §6.1、碼表與每級語意的權威定義住 §8.2／§8.3，本節依上表格式只在回應欄寫方向、在量測欄引用該欄所定義的可斷言值，不重新定義語意。守門欄的案名皆可 `grep -rn "fn <名>" rust-api/server` 自證。

### 島 A token rotation——並發換發與 grace 不可用

| 欄 | 內容 |
|---|---|
| 刺激 | 同一 refresh 票兩個並發換發請求；或 `rotated` 腿讀 grace 鍵時 redis 連線 `Err` |
| 回應 | 先到者鎖列 rotate 並於 commit 前寫 grace；後到者釋鎖後見 `rotated`→grace 命中→回既發同一對（冪等、不觸 reuse）；grace 讀 `Err`→fail-secure 走 reuse 撤家族＋8888（重登復原＝已知代價） |
| 量測 | 兩回應 `data` 逐字相等、該鏈恰一列 `active`；降級腿：鏈上全列 `revoked`＋`session_event(reuse)` 恰一列＋denylist `revoked`、回 `8888` |
| 守門 | `handler/auth/refresh.rs`：`refresh_second_presentation_within_grace_returns_identical_pair`／`refresh_grace_miss_triggers_reuse_revokes_family_audits_and_denylists`／`refresh_grace_read_error_fails_secure_into_reuse` |

### 島 B single-session——設定翻轉不追溯

| 欄 | 內容 |
|---|---|
| 刺激 | `single_session_default` 翻 on 後同帳號再登入；或翻 on 之前已有兩條會話、翻後不再登入 |
| 回應 | 只於登入事件判定：其他 chain 的 active 轉 `revoked`＋逐 sid `session_event(kicked, single_session)`＋denylist `kicked`；被踢者下個請求 7777 modal；翻轉本身不觸任何既有會話、鍵缺席＝off 語意 |
| 量測 | 前一條 access 打 Authed 端點回 `code=7777`＋`auth.session.kicked`；翻 on 前的兩條會話翻後皆仍 `0000`；`sys_user.session_id`＝新 sid |
| 守門 | `handler/auth/login.rs`：`login_global_single_session_on_second_login_kicks_previous_to_7777`／`login_flipping_single_session_on_does_not_revoke_existing_sessions_until_next_login`；`handler/auth/refresh.rs`：`refresh_revoked_row_with_kicked_denylist_returns_7777_modal` |

### 島 C denylist 撤銷——redis 失聯與 PG 亦故障

| 欄 | 內容 |
|---|---|
| 刺激 | 每請求驗章時 redis 連線 `Err`；再疊 PG `sys_token::has_active_in_chain` 回 `DbErr` |
| 回應 | fail-closed 退 PG 權威：鏈上有 active→放行、無→8888；PG 亦 `Err`→視為無 active→8888、絕不盲放；第 3／4 級各發一筆 `security.session` 結構化事件 |
| 量測 | `denylist_hit_total{source="pg"}` 增 1（命中腿則 `{source="redis"}` 增 1）；事件帶 `degraded=denylist_read`／`denylist_pg_fallback`＋sid、零 token 字面；雙源全斷回 `8888` |
| 守門 | `auth/enforce.rs`：`enforce_mw_bad_redis_pg_active_passes_counts_pg_source`／`enforce_mw_bad_redis_and_bad_pg_fails_closed_8888`／`enforce_mw_denylist_kicked_7777_counts_redis_source`／`enforce_mw_degradation_events_are_structured_under_session_target`；`obs.rs`：`pre_register_renders_denylist_hit_two_sources_explicit_zero` |

### 島 D idle 逾時——last_activity 不可讀

| 欄 | 內容 |
|---|---|
| 刺激 | 換發時 `session:{sid}:last_activity` 缺席（未寫或已過期）或讀取 `Err`；或距上次活動逾 `refresh_secs − access_secs`（＝N×60 秒） |
| 回應 | 缺席／`Err`→fail-open 續換發（以 token exp 為界、偏晚不誤踢活躍者）；逾時→8888、SET NX `session:idle-emitted:{sid}` 守門僅首次落 `session_event(idle)`、列不動、絕不寫 denylist |
| 量測 | 逾時腿回 `8888`、`session_event(idle)` 恰一列（再次換發不增列）、denylist 鍵缺席；fail-open 腿回 `0000`＋新對且零 idle 副作用 |
| 守門 | `handler/auth/refresh.rs`：`refresh_idle_timeout_rejects_8888_emits_idle_once_and_never_denylists`／`refresh_activity_within_idle_window_rotates_with_zero_idle_side_effects`／`reject_idle_guard_write_error_emits_no_event_and_keeps_8888` |

### 島 E 登入失敗節流——三區與兩層刻意相反的 captcha 降級

| 欄 | 內容 |
|---|---|
| 刺激 | 同帳號窗內連續失敗達 `captcha_after`（seed 2）與 `max_fails`（seed 5）；redis 整體不可用；L2 計數查詢 `DbErr`；captcha 消耗標記 SET NX 瞬斷（redis 健康）；三鍵矛盾組合 |
| 回應 | 自由區 1000→軟區 2222 `biz.auth.captchaRequired`→鎖定 2222 `biz.auth.locked`（軟區與鎖定皆驗章前擋、零稽核列零計數桶）；redis 不可用→captcha 整層停用續驗密碼、密碼錯仍計數；L2 `Err`→`count := 0` 放行＋`captcha_forced`；SET NX `Err`→拒該次不罰；矛盾組合→整組退常數＋告警一筆 |
| 量測 | 窗內 `success=false` 列數恰＝自由區失敗次數；`throttle_soft_zone_total` 增 1；`throttle_degraded_total{source}` 對應源各增 1（七源預註冊顯式 0）；鎖定後 L1 鍵 TTL 不因再次命中而延長 |
| 守門 | `throttle/mod.rs`：`three_zone_transition_lock_ttl_and_no_renew_on_hit`／`soft_zone_rejections_do_not_consume_bucket_success_still_possible`／`redis_down_disables_captcha_layer_but_keeps_counting`／`l2_dberr_fail_open_with_captcha_forced_compensation`／`captcha_gate_set_nx_failure_rejects_without_penalty`／`load_settings_contradiction_falls_back_with_settings_invalid_and_equal_is_legal`／`warn_degraded_increments_each_of_the_seven_sources`；`obs.rs`：`pre_register_renders_throttle_degraded_seven_sources_explicit_zero`／`pre_register_renders_throttle_soft_zone_explicit_zero` |

## 10.3 E6 AI 品質情境

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E6 品質情境](../process/P-E6-quality-scenarios.md)。
