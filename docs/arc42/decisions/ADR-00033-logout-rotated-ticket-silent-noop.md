---
id: "ADR-00033"
title: logout 呈遞 rotated 票維持 0000 靜默 no-op——撤銷射程恆為單列、不擴撤全鏈（by-design；承 rev5:ADR 0059）
date: 2026-09-15
status: accepted
supersedes: []
superseded_by: []
provenance: "user 拍板 2026-09-15（spec-compliance-003 對照審查 finding L1-5 三選一：①立 by-design ADR 維持現行／②改行為撤同鏈後繼／③轉 BL 暫不裁）；前代同題裁決＝rev5:ADR 0059（user 親決 2026-08-25）；憲法 §I.5 與 ADR-00014 背景要求前代拍板以 rev6 自立 ADR 承襲；as-built＝rust-api/server/src/handler/auth/logout.rs 冪等 no-op 家第四款、測試 logout_rotated_ticket_is_noop_and_active_successor_logout_revokes_only_that_row"
tags: [auth, session, state-machine, by-design]
---

## 背景

- `specs/003-auth-session/spec.md` FR-010 寫「驗 refresh 成功→撤該會話（列轉 revoked＋denylist）」；data-model §1 的 logout 只有兩列：`active`＋驗章成功→該列 `revoked`；（任意／無）＋驗章失敗→不變、`0000`。呈遞 **rotated** 票（驗章成功、查得到列、現態非 `active`）兩列皆落不進＝矩陣缺格。
- rev6 as-built 把它歸冪等 no-op 家：`0000`、`data: null`、零 DB 寫、不落事件；撤銷射程恆為呈遞之 `active` 單列（`sys_token::revoke_row`），由上述測試釘住。
- 同一缺格 rev5 已由 user 親決（rev5:ADR 0059）；rev6 未自立 ADR＝偏離 FR-010 字面而無 rev6 承載（spec-compliance-003 L1-5，兩鏡確認）。

## 決策驅動因子

- logout 一律回 `0000`：回異碼＝token 有效性 oracle（wire-auth §logout 紀律、logout.rs 檔頭）。
- 撤全鏈的既有路徑＝refresh grace miss 之 `revoke_family`，綁 `session_event(reuse)` 系統事件（攻擊訊號）；把使用者主動登出併入會污染 reuse 語意，另建「撤全鏈但落 logout 事件」的路徑屬新增能力面。
- 鏈上 rotated 舊票之後的重放由 reuse 偵測接手；登出時預收，等於讓「登出後有人拿舊票重放」的竊取訊號消失（logout.rs 成功形碼註）。

## 考慮過的替代案

1. **改行為：rotated 票驗章成功時撤同鏈 active 後繼**（另建落 logout 事件之撤全鏈路徑）：user 可見行為變更；動 logout.rs 可執行碼連帶 BL-00062 到期；須反轉現有測試並做 CDP 驗收；棄。
2. **轉 BL 暫不裁**：偏離 FR-010 字面仍無 rev6 承載，下一輪 review 會重報；棄。

## 決定

1. logout 呈遞 rotated（及 revoked）票＝`0000` 靜默 no-op：零 DB 寫、不落事件、不寫 denylist；撤銷射程恆為呈遞之 `active` 單列，不擴為撤全鏈。
2. 本 ADR 即 data-model §1 logout 缺格之 rev6 裁決記錄；`specs/003-auth-session` 屬史料面、不改。
3. logout.rs 冪等 no-op 家第四款碼註指向本 ADR。

## 後果

- 行為零改動；現行測試續釘住，改動任一方向即紅。
- ★已知代價（user 可見、不粉飾）：多分頁 rotate 競態下，分頁 A 完成換發後，分頁 B 手上的票已是 rotated；在 B 按登出得 `0000`，B 清本地票回登入頁，但同鏈的 active 後繼未被撤＝分頁 A 的會話續活。若使用者對「登出」的心智模型是「結束整個會話」而非「結束本分頁」，此形與預期不符——本決定接受此代價。

## 翻案觸發器

- 收到真實回報「在一個分頁登出後其他分頁仍活著」，或 single-session 語意調整時＝立新 ADR supersedes 本決定，並反轉上述測試。
