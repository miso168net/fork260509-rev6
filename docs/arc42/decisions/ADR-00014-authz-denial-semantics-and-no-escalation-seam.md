---
id: "ADR-00014"
title: 授權拒絕語意定死為 5003＋HTTP 403＋純 i18n key，並預留空 no-escalation 掛點簽章
date: 2026-09-05
status: accepted
supersedes: []
superseded_by: []
provenance: "rev5:ADR 0022（rev5 002 刀 M4 授權拒絕語意）；docs/brainstorms/002-system-settings.md §0 Q1～Q8 與 §4 憲法 §IV 預答；specs/002-system-settings/spec.md FR-013／FR-014／US4；data-model §5／§6；user 於 brainstorm 與 clarify 過目、主線擬稿即 accepted（2026-09-05）"
tags: [authz, wire, seam]
---

## 背景

- 002 刀是 rev6 第一支寫端；「R_ADMIN 有 user:edit 鈕、無設定域政策」是 seed 現況就存在的組合（casbin 政策列 66／67 僅 R_SUPER）。第一支寫端落地即隱含定死「政策無授時回什麼」——不顯式定形＝默拍。
- 憲法 §I.3 鎖 13 碼矩陣與 msg＝穩定 i18n key；憲法 §I.7 把 no-escalation（不得授予超出自身權限之角色）列為授權治理島、隨後刀進場，但其判定掛點若不在首刀立位，接手刀就得改判定進入點的簽章與每個呼叫端。
- rev5 於同一刀以 rev5:ADR 0022 拍定同題；rev6 憲法 §I.5 要求拍板結論以 rev6 自立 ADR 承襲、不引前代編號為現行依據。

## 決策驅動因子

- 拒絕回包不得成為權限探測面：揭露「缺哪條政策」或「操作者持哪些角色」＝把授權表逐請求洩漏給被拒者。
- 前端統一錯誤處理只認信封 `code`＋`msg` key；HTTP 狀態列只在信封例外恰二之外的兩個碼（4040→404、5003→403）帶語意。
- 判定進入點必須單一（spec FR-013）、每請求向資料庫取現行角色（角色一撤、下一請求即生效）；掛點必須可觀察（不是裝飾性函式）。

## 考慮過的替代案

1. **拒絕時附結構化明細（缺的政策、持有角色）**：診斷方便，但把授權表變成可枚舉資源，且 13 碼矩陣沒有攜帶明細的碼面；棄。
2. **未認證與越權同碼**（皆 8888 或皆 5003）：前端無法區分「去登入」與「權限不足」兩個下一步；棄。
3. **no-escalation 掛點留到本體刀再開**：本體刀必須改判定進入點簽章與呼叫端；本刀多四個未用參數的成本遠小於日後改介面；棄。
4. **政策求值失敗也回 5003**：把我方故障偽裝成使用者無權限、診斷方向錯誤；棄——求值失敗回 5000 並落 log。

## 決定

1. **越權（政策無授、含角色已軟刪或停用）**＝`AppError::PermissionDenied`→碼 `5003`＋HTTP **403**＋`msg` 純 key `system.forbidden`＋`data: null`；回包**不揭露**缺哪條政策、亦不揭露操作者角色集。
2. **未認證**（標頭缺席／非 Bearer 形／token 不在表／release 建置驗證器缺席）＝`AppError::Logout`→`8888`＋HTTP 200＋`auth.session.reLogin`；與越權嚴格分碼。
3. **政策求值本身失敗**（casbin 求值 Err）＝`AppError::Internal`→`5000`、先 `tracing::error!` 落 root cause；不走 5003。
4. **判定單點**＝`auth::enforce::enforce_role_path_method(db, enforcer, actor_uid, roles, path, method)`；角色一律由 `model::facade::sys_user_role::roles_of_user` 每請求現查（`deleted_at IS NULL`＋`status=1` 兩濾網）、不快取、不採信 token 帶的角色。★spec FR-013「每請求向資料庫取現行政策」於本刀之語意＝每請求 DB-fresh 取**角色**；casbin 政策集本身 boot 一次 `load_policy` 即終態（運行期重載屬後刀、research R2）。
5. **no-escalation 掛點**＝`pub(crate) async fn no_escalation_check(db: &DatabaseConnection, actor_uid: i64, path: &str, method: &str) -> Result<(), AppError>`：本刀恆 `Ok(())`；簽章預留 async 與資料庫句柄；**唯一呼叫點**＝判定單點內、先於政策求值；掛點 deny 與政策 deny 同出口（5003）。可觀察形＝`#[cfg(test)]` 旗標掰開即回 `Err(PermissionDenied)`，整鏈測試據此證掛點在判定鏈上而非裝飾。
6. metrics `casbin_enforce_total` 只帶 `decision` 一維（allow／deny／error）；掛點 deny 併入 deny。

## 後果

- 003 接真 session 時只換驗證器內部（`Identity{uid, user_name}` 注入形不變）；no-escalation 本體刀只填掛點函式體、零簽章變更、零呼叫端改動。
- 拒絕語意的機器守＝contract 通則 case（未認證 8888）、handler 真 DB 授權矩陣（R_ADMIN 讀寫 5003、角色軟刪／停用 5003）、掛點旗標整鏈案；求值失敗 5000 由純函式測釘住。
- 代價：每個 Policy 請求多一次角色查庫（16 鍵低頻治理面、可接受；R11 併發語意同刀拍板）。

## 翻案觸發器

- 業務錯誤明細的受眾邊界重評（例如管理台需要「為何被拒」的診斷面）——屆時由 no-escalation 本體刀或專屬治理刀以新 ADR 翻案、不得就地放寬本決定。
- 003 接真 session 時對 3333／8888 分工重定（本 ADR 只鎖「未認證≠越權」，不鎖 3333 的射程）。
