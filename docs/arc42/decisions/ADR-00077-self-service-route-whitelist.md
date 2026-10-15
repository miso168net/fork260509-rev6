---
id: "ADR-00077"
title: 自助路由白名單為碼內常數 `SELF_SERVICE_ROUTES`、於 casbin 過濾之後恆併入 getUserRoutes——以「業務 menu 射程＋`hide_in_menu` seed 實值」二支柱對憲法 §I.2 立論、只收受眾＝本人之自助頁；身分注入形增 `sid`（ADR-00014 後果段「注入形不變」句自本刀起不再成立）；003 刀與 005 刀照帶之「不帶回」前提翻轉
date: 2026-10-05
status: accepted
supersedes: []
superseded_by: []
provenance: "007-user-password-admin 之 spec FR-039（恆併入、只收自助頁、seed 政策列保留、兩向案、§I.2 關係、路由讀端歸因勘誤、005 照帶前提翻轉）、FR-036（身分帶會話 id、保留當前會話）、FR-049（個人中心入口與零角色可達）、US3 AS8、Edge Cases「零角色帳號」；brainstorm §0 Q11（程式內自助白名單）、§1「自助路由白名單」「changePassword 流程」兩列；plan 期主線定案（`Identity { uid, user_name, sid }`、注入點與消費者）；藍本＝rev5:ADR 0065（二支柱、併入次序、擴充紀律、seed 列保留）與其 as-built rev5:server/src/handler/route.rs（`SELF_SERVICE_ROUTES`）、起源＝rev4:ADR 0065（rev4:014-user-center）、`rev5:B-140`（前代收刀後以 `Identity.sid` 取代 handler 內重驗章取會話 id）；rev6 既有件＝`handler::route::get_user_routes`／`resolve_home`、`sys_menu::visible_menu_routes`／`list_active`／`build_user_route_tree`、`sys_role::home_of_roles`、`auth::Identity`、`auth::enforce::enforce_mw`、`auth::jwt::Claims` 之 `sid`、`sys_token::revoke_others_of_user`；seed 事實＝rust-api/migration/src/m0002_baseline_seeds.rs 之 `sys_menu` 列 16（`user-center`、`hide_in_menu=TRUE`、頂層、非受保護）與 `casbin_rule` 列 123（`p|R_SUPER|user-center|menu`；2026-10-05 核）；照帶前提出處＝rust-api/server/src/handler/route.rs 檔頭（003 刀 U5）、specs/005-role-menu-crud/research.md R3 防回歸清單；上游＝憲法 §I.2（規則句、含義第一條、釋義②）、ADR-00014 後果段；draft 於 plan 期落 feature branch、親決與 accepted 時點見本刀 research 之「ADR 配號與親決時點表」"
tags: [routing, authz, self-service, constitution-check, user-password-admin]
---

## 背景

- getUserRoutes 之路由樹＝casbin `menu` 維度對操作者現役角色之枚舉。`user-center` 之選單維政策只授 R_SUPER（seed 列 123）⇒ 非超管之路由樹沒有個人中心、點頭像下拉「個人中心」即 404。本刀把個人中心改為真頁（改密卡；兩支 Authed 端點），spec 要求任何登入者（含零角色帳號）皆可達（FR-039、FR-049）。
- `handler/route.rs` 檔頭（003 刀 U5）寫「前代的自助路由白名單屬 `rev5:004` 增量（前提是個人中心端點，rev6 本刀沒有），不帶」；005 刀 research R3 照帶「`SELF_SERVICE_ROUTES` 不帶回」為防回歸項。歸因有誤：白名單起源＝`rev4:014`（rev4:ADR 0065）；前代起初明文不帶回（`rev5:67e59c7` 之碼註）、至 `rev5:007` U4 帶回（`rev5:d5d5306`；rev5:ADR 0065）。其前提（無個人中心端點）於本刀消失。
- rev6 憲法 §I.2 規則句「menu 由 Casbin RBAC enforce、有權才顯示」為無限定句、與前代同；rev4 之頁級豁免條文在 rev6 不存在、不能援引 ⇒ 須自立論並過 Constitution Check（§IV 第 3 題）。
- changePassword 須撤本人其他會話、保留當前會話（FR-036）⇒ 需要當前會話 id；現行 `Identity` 恰兩欄（`uid`、`user_name`），ADR-00014 後果段記「003 接真 session 時只換驗證器內部（`Identity{uid, user_name}` 注入形不變）」。

## 決策驅動因子

- 「登入即可達」應為碼面事實、不靠資料維護約定（新建角色不漏配）。
- 不把與授權無關之事寫進授權表。
- 對 §I.2 自證、不為單一頁面另開憲法條文。
- 後端為路由唯一來源（§I.2：constantRoutes 只 builtin 常量集）。
- 頁面可達性與其端點保護同軸（個人中心兩端點皆 Authed、零政策列）。
- 會話 id 只有一個誠實來源：驗章當下之票面。

## 考慮過的替代案

1. **改 seed 把 `user-center` 選單政策授全部角色**：新建角色仍漏配；授權表多純冗餘列、讀者會誤以為個人中心是受治理資源；另一處 seed 變更。否決。
2. **憲法補 `user-center` 頁級豁免**（rev4 形）：為單一頁開條文，而二支柱已足；白名單成長時重評（翻案觸發器）。否決。
3. **前端寫進 constantRoutes**：§I.2 之 constantRoutes 為 builtin 常量集、不動；前端寫死破「後端為路由唯一來源」。否決。
4. **把 `user-center` 選單列設 `constant=TRUE`**（資料庫常量路由）：常量路由經 Public 之 getConstantRoutes 於登入前下發、受眾錯（自助頁受眾＝已登入本人）；且屬 seed 變更。否決。
5. **個人中心只開給超管**：非超管不能自助改密，與 FR-039／FR-049 相悖。否決。
6. **白名單併在 casbin 過濾之前**（或塞進角色集）：對零選單政策角色仍被濾掉，白名單失效且不會紅（超管案照過）。否決。
7. **handler 內重驗 Authorization 標頭取會話 id**（`rev5:007` as-built 之 `current_sid` 形）：第二條驗章路徑、可與 `enforce_mw` 之三分碼與 denylist 判定分岔；前代收刀後已改 `Identity.sid`（`rev5:B-140`）。否決、取 HEAD 形。

對所選方案跑同一反例（RL-0013）：

- 「白名單被用來抹平授權差異」：擴充紀律（決定 3）＋常數型長度＋兩向測；新增成員須回二支柱重驗。成立——「是否自助頁」之判斷無機器守、由本 ADR 紀律與審查承擔。
- 「頁可達而 API `5003`」：白名單頁之端點皆 Authed ⇒ 頁之可達性與端點保護同軸。成立。
- 「白名單越過顯示域」：併入的是可見名集，組樹仍經顯示域（啟用且未刪）⇒ 不越顯示域。成立（已知態見後果）。

## 決定

1. **常數與併入點**：`handler/route.rs` 之 `SELF_SERVICE_ROUTES: [&str; 1] = ["user-center"]`；getUserRoutes 於 casbin `menu` 維度過濾所得可見集之後恆併入（集合語意天然去重：與 seed 列 123 雙來源命中不生重複節點），再經既有顯示域組樹與首頁兜底。次序不可反（替代案 6）。
2. **二支柱**（缺一不可）：
   - ①§I.2 含義第一條之射程是「業務 menu」——個人中心無受治理之資料面、受眾恆＝登入者本人、可達性不隨角色而變；交給 RBAC 治理的是一個沒有變數的量。
   - ②`user-center` 之 seed 選單列（`sys_menu` 列 16）`hide_in_menu=TRUE` ⇒ §I.2「有權才顯示」在側欄面對此頁結構性不觸發（恆不出現在側欄、入口恆為頭像下拉）；白名單改變的是「路由在不在回傳樹裡」（點下去會不會 404），不是側欄多一項。該值為 upstream route meta 自帶、照原樣入 seed，依 §I.2 釋義②不視為啟用前端隱藏機制。
   - 只有①＝「何謂業務頁」淪為可爭辯之形容詞；只有②＝任何 `hide_in_menu` 頁皆可入白名單。
3. **擴充紀律**：只收「受眾＝任何登入者本人」之自助頁（頁上每支端點皆 Authed、標的恆＝登入者本人）；授權資源頁禁入（授權仍走 casbin 唯一路徑）；擴列＝回本 ADR 二支柱重驗＋同批改常數型長度與兩向測，不是在陣列多加一個字串。判準：該頁對不同角色之可達性有無差別——有差別而想用白名單抹平者，要的是一列 casbin 政策。
4. **seed 政策列 123 保留不動**（硬刪屬 seed 移除軌道、非本刀射程）。
5. **身分注入形**：`Identity { uid, user_name, sid }`——`enforce_mw` 於驗章、denylist 判定皆放行之後自 `Claims.sid` 注入；消費者＝changePassword（撤本人其他有效票、以 `sid` 為保留鍵保留當前會話）。ADR-00014 後果段「`Identity{uid, user_name}` 注入形不變」句為 003 刀接真 session 之預告、已兌現；本刀之變更由本款承載，該句自本刀起不再成立。ADR-00014 不翻案（決定 1～6 不受影響）。
6. **照帶前提翻轉**：`handler/route.rs` 檔頭「不帶」句改為帶回之現在式並勘誤歸因（起源＝`rev4:014`〔rev4:ADR 0065〕、前代帶回＝`rev5:007` U4〔rev5:ADR 0065〕）；005 刀 research R3 照帶之「`SELF_SERVICE_ROUTES` 不帶回」防回歸項之前提隨本刀消失——該 research 屬凍結存證不改，本刀 research R5 之防回歸清單不再列此項。
7. **測試**：「零選單政策角色仍得自助路由」與「白名單外路由不受影響」兩向案（spec FR-039）；併入次序以零選單政策角色案釘住（超管案照過、不足以證）；`sid` 注入以「改密後當前會話續用、其他會話 `8888`」端到端案釘住（FR-036、SC-005）；首頁兜底落點另一案：首頁不在可見樹且可見葉皆排序在 `user-center`（seed order 999）之後之角色，登入落點＝個人中心。

- **親決紀錄**：user 親決 2026-10-06（007 刀 tasks T003 施工前提顆）——本輪逐款一題一問呈決定 1～7、皆照文定稿；零非建議項 ⇒ 決定節免改寫。

## 後果

- 任何登入帳號（含新建角色、零角色）恆得 `user-center` 路由。零角色帳號之可導航葉恰此一頁 ⇒ 登入落地頁經既有首頁兜底（`sys_role::home_of_roles` 對空角色集回 `home`、`resolve_home` 見其不在可導航葉集即取先序第一葉）落於個人中心——與 Edge Cases「零角色帳號只得常量路由＋個人中心」一致。
- 白名單之 `user-center`（seed order 999）為可導航頂層葉、參與首頁兜底：首頁不在可見樹且可見葉皆排序在 999 之後之角色（例：只授插件示例或 function 下之頁），登入落點自本刀起為個人中心（與 rev5 HEAD 同 seed 序、同形＝CDP 零差）；連動 ADR-00081 款 17（只授目錄之 `/403` 症狀限 order＜999 之目錄）。
- 已知態：白名單不越顯示域——`user-center` 選單列非受保護，經選單管理停用或軟刪即對所有人（含超管）消失；屬選單治理之誠實結果、不另加守門。
- `Identity` 構造點：生產 1（`enforce_mw`）＋測試 10（plan 期 grep 量測；加欄後以編譯器列舉為準）同批補欄。現在式假述（RL-0011）：`auth/mod.rs` 模組 doc「恰兩欄」與「其第三欄 `sid` 屬後刀域、本刀不帶」、`auth/enforce.rs` 模組 doc「`Identity.sid` 第三欄屬後刀域、不帶」、活書 06（「注入 `Identity{uid}`」）與 08 §8.3（「注入 `Identity{uid, user_name: ""}`」）同批改現在式；種子＝「Identity{」「恰兩欄」「第三欄」「SELF_SERVICE」「自助路由白名單」，施工時以 `python3 tools/docsync errata <詞>` 現算、改完復掃。
- 憲法 §IV 第 3 題（casbin）之自助白名單與 §I.2 關係以本 ADR 過檢查。
- 代價：白名單成員「是否自助頁」之判斷無機器守、靠本 ADR 紀律。

## 翻案觸發器

- 白名單成長到三頁以上、或收入一頁不帶 `hide_in_menu` ⇒ 支柱②失效、重評替代案 2。
- 某自助頁之可達性開始隨角色而異（例：個人中心某卡只給特定角色）⇒ 該面改走 casbin 政策、複核決定 3。
- 憲法 §I.2 規則句或釋義②改寫 ⇒ 重驗二支柱。
- `user-center` 選單列改為受保護、或出現「個人中心恆可見」之需求 ⇒ 複核已知態。
- 會話識別改形（例：`sid` 不再等於輪替鏈識別、一票多會話）⇒ 複核決定 5 之保留鍵語意。
- `Identity` 再增欄 ⇒ 以新 ADR 或本 ADR 續行記注入形變更。
