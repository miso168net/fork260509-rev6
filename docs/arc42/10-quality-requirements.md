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
| UI 一致性 | UI 與 rev5 一致 | **結構清單逐項全等才綠**——表格欄位集合與列序／搜尋器項目／按鈕集合與權限顯隱／抽屜欄位與校驗訊息／分頁／回收桶流程／toast 文案；截圖之間距、字體、顏色差異**只記入走查紀錄、不擋收刀**（判準自 004 刀 clarify 起適用）。已知例外＝view 未進場之管理頁選單標題於側邊欄展開態顯裸鍵、逐頁帳住 BACKLOG，收合態零差異 | 走查流程（CLAUDE.md §7） |

## 10.2 品質情境

情境格式（每情境一個 `###`）：

| 欄 | 內容 |
|---|---|
| 刺激 | 誰在什麼環境下做了什麼（含異常：redis 失聯、PG 查詢失敗、鏈長逾上界） |
| 回應 | 系統的可觀察行為與方向（fail-open／fail-closed、降級腿） |
| 量測 | 可斷言的值：碼、HTTP status、序列計數、時限 |
| 守門 | 釘住該情境的測試或 lint |

情境逐島一則＝憲法 §I.7 已入憲行為島 A～F（島 G～J 的情境隨其進場刀入本節；承襲指針表＝憲法 §I.7）。每則只釘該島最容易被「順手統一」抹掉的 fail-* 方向（方向之凍結面＝該島入憲條文）；流的完整敘述住 §6.1、碼表與每級語意的權威定義住 §8.2／§8.3，本節依上表格式只在回應欄寫方向、在量測欄引用該欄所定義的可斷言值，不重新定義語意。守門欄的案名皆可 `grep -rn "fn <名>" rust-api/server` 自證。

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

### 島 E 登入失敗節流——兩維三區、每次嘗試由 PG 定案與兩層刻意相反的 captcha 降級

| 欄 | 內容 |
|---|---|
| 刺激 | 同帳號窗內連續失敗達 `captcha_after`（seed 2）與 `max_fails`（seed 5）；同一來源輪換帳號名、失敗累計達來源維門檻（seed 10／50），其間穿插一次成功登入；管理員放寬門檻、或對該維寫入解鎖標記；快取整體不可用（解鎖標記讀取 `Err`）；任一維計數查詢 `DbErr`；captcha 消耗標記 SET NX 瞬斷（快取健康）；設定三鍵缺列、越界或矛盾組合 |
| 回應 | 每一維各自：自由區 1000→軟區 2222 `biz.auth.captchaRequired`→鎖定 2222 `biz.auth.locked`（兩維共用同一組 msg、不揭露觸發維度；拒絕皆驗密前擋、零稽核列零計數桶）；合成＝任一維鎖定即鎖定、否則任一維軟區即要求驗證碼；成功登入只重置帳號維、來源維不重置；判定於每次嘗試讀設定現值＋PG 滑動窗重算——放寬門檻與解鎖標記於下一次嘗試即生效、最早一筆失敗出窗即解；解鎖標記讀不到→視為無標記（fail-closed）＋captcha 整層停用續驗密碼、密碼錯仍計數；計數 `Err`→該維 `count := 0` 放行＋`captcha_forced`；SET NX `Err`→拒該次不罰；設定壞值→該維整組退常數＋該維告警至多一筆 |
| 量測 | 窗內 `success=false` 列數＝通過節流閘後的失敗次數（被 `biz.auth.captchaRequired` 或 `biz.auth.locked` 擋下者零列；軟區過題後的密碼失敗照落列＝計數得以由軟門檻推進到硬門檻）；`throttle_soft_zone_total` 每發至多增 1；`throttle_degraded_total{source}` 對應源各增 1（值集＝`obs.rs` `THROTTLE_DEGRADED_SOURCES`、預註冊顯式 0）；鎖定與軟區拒絕皆不建任何節流鎖定鍵（快取層無鎖定鍵）、需驗證碼時送出有效題者另寫一把一次性消耗標記；顯式放行來源與缺席輸入＝來源維零查詢；解鎖後同一帳號（或同一來源）的下一次登入即進密碼驗證、不再回 `biz.auth.locked`，且落一列 `sys_login_attempt` |
| 守門 | `throttle/mod.rs`：`three_zone_transition_rejects_without_audit_rows_or_redis_keys`／`soft_zone_rejections_do_not_consume_bucket_success_still_possible`／`source_dimension_three_zones_count_across_rotating_user_names`／`two_dimension_composition_hard_lock_wins_then_soft_zone_then_pass`／`interleaved_success_does_not_reset_the_source_dimension`／`relaxed_hard_threshold_applies_on_the_very_next_attempt_in_both_dimensions`／`lock_lifts_as_soon_as_the_earliest_failure_leaves_the_window`／`unlock_marker_read_error_means_no_marker_and_redis_down_per_dimension`／`explicit_allow_skips_the_source_dimension_including_its_marker_read`／`redis_down_disables_captcha_layer_but_keeps_counting`／`count_dberr_fails_open_with_captcha_forced_compensation_in_both_dimensions`／`captcha_gate_set_nx_failure_rejects_without_penalty`／`out_of_range_or_contradictory_settings_fall_back_whole_group_per_dimension`／`warn_degraded_increments_each_of_the_ten_sources`／`src_tree_carries_no_lock_cache_literals`；`handler/throttle.rs`：`unlocking_an_account_lets_the_same_login_through_at_once`／`unlocking_a_source_lets_the_same_login_through_at_once`；`obs.rs`：`pre_register_renders_throttle_degraded_ten_sources_explicit_zero`／`pre_register_renders_throttle_soft_zone_explicit_zero` |

### 島 F 信任錨與 IP 存取閘——全鏈 fail-open 與恰兩處 fail-closed

| 欄 | 內容 |
|---|---|
| 刺激 | 攻擊者繞過 CDN 直連來源站、自帶「偽造位址, CDN 邊緣位址」轉發鏈；轉發鏈原始欄數逾 `MAX_XFF_TOKENS`；執行中規則集重讀 `DbErr`（寫端重載或 watcher 收門鈴）；boot 初載失敗；請求上下文缺席；超管送出會把自己擋在門外的規則變更、或其來源位址取不到；來源命中 deny 規則 |
| 回應 | 錨右含不受信跳→棄錨、取最右不受信跳（攻擊者自身位址、`proxy_clean`），合法 CDN 路徑結論逐位元不變；逾限→全域只標記 `chain_rejected`（位址不覆寫、照常服務），登入端點拒絕並仍落一列稽核（帳號維計數排除、來源維計入）；重讀失敗→沿用上一份規則集、不清空；初載失敗→空規則集＝除結構豁免外全放行；上下文缺席→存取閘放行、來源維節流跳過；fail-closed 恰兩處＝寫端自鎖拒寫（操作者來源取不到時同向拒寫、零落庫零重載）與登入端點逾限拒絕；阻擋只擋該次請求、會話與 token 不動、規則解除即恢復；每次降級一則結構化 warn＋計數，阻擋與逾限拒絕不入降級序列 |
| 量測 | 攻擊形鏈之 `real_ip`＝攻擊者位址而非偽造位址；逾限登入回 HTTP 403＋`code=5003`、`sys_login_attempt` 恰增一列 `ip_confidence=chain_rejected`；重讀失敗前後規則集兩袋原樣（不清空）、`ip_domain_degraded_total{source="ruleset_reload"}` 增 1；阻擋回 `5003`＋`ipgate_blocked_total` 增 1＋warn 帶命中網段；自鎖拒寫回 2222 `biz.ipRule.selfLock`、來源取不到回 `5000`，兩者 `sys_ip_rule`／`sys_operation_log` 皆零新列；`ip_domain_degraded_total` 值集（`obs.rs` `IP_DOMAIN_DEGRADED_SOURCES`）預註冊顯式 0 |
| 守門 | `trust/mod.rs`：`hardening_defeats_forged_anchor_on_bypass_path`／`hardening_is_bit_identical_on_legitimate_cdn_path`／`window_direction_guards_real_ip_under_left_side_flood`／`every_confidence_state_is_reachable_through_the_pipeline`；`middleware/mod.rs`：`chain_over_the_token_bound_is_marked_rejected_and_keeps_the_resolved_address`／`ip_gate_walks_the_six_decision_steps_in_order`／`gate_outcome_agrees_with_decide_on_every_cell`／`blocked_request_gets_the_5003_envelope_one_count_and_a_warn_naming_the_cidr`／`absent_context_passes_with_one_degraded_count_and_a_warn`／`chain_rejected_source_is_gated_on_its_resolved_address_not_bypassed_nor_pre_rejected`；`handler/auth/login.rs`：`login_with_overflowing_chain_is_403_and_lands_one_chain_rejected_row`；`model/facade/sys_login_attempt.rs`：`count_recent_failures_excludes_chain_rejected_but_counts_null_and_legacy_rows`／`count_by_ip_counts_chain_rejected_rows_unlike_the_account_dimension`；`ipgate/mod.rs`：`initial_load_failure_falls_back_to_the_empty_ruleset`／`reload_failure_keeps_the_last_good_ruleset_and_returns_err`／`watcher_keeps_the_last_good_ruleset_when_its_rereads_fail`／`a_blocked_source_keeps_its_session_and_recovers_once_the_rule_is_gone`／`ruleset_mutator_calls_across_src_stay_at_the_single_keep_last_good_site`／`watcher_pushed_degraded_counts_are_never_pinned_on_the_process_recorder`；`handler/ip_rule.rs`：`self_lock_guard_refuses_on_all_four_write_ends_and_writes_nothing`／`write_ends_refuse_with_5000_when_the_request_context_is_absent`；`obs.rs`：`pre_register_renders_ip_domain_degraded_eight_sources_explicit_zero`／`pre_register_renders_ipgate_blocked_explicit_zero`／`ipgate_blocked_outlet_is_called_from_exactly_one_production_site`／`blocked_series_literal_is_named_only_at_the_obs_outlets`；`tests/serve_connect_info_lint.rs` |

## 10.3 E6 AI 品質情境

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E6 品質情境](../process/P-E6-quality-scenarios.md)。
