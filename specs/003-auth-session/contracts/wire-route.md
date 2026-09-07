# Wire 契約 — route 面（3 條）＋動詞不符處置

權威＝base-web typings（憲法 §I.3 權威序 1）。欄位映射見 `../data-model.md` §5、不重複。

## GET /route/getConstantRoutes（**Public**）

Public 理由：登入前就要拿得到（前端 `initConstantRoute` 於 dynamic 模式呼叫）。

| 面 | 內容 |
|---|---|
| 成功 | `data`＝`Api.Route.MenuRoute[]`；濾 `sys_menu.constant = TRUE`（★勿寫 `IS NOT FALSE`——NULL 占 64 列） |
| 現值 | seed `constant=TRUE` 為 **0 列** ⇒ 現回 `[]` |
| 前端接線（AUTH-WIRING(a)） | ★**合併**而非取代：route store `initConstantRoute` 之 dynamic 分支改 `addConstantRoutes([...staticRoute.constantRoutes, ...data])`（Map 按 name 收斂、後端同名可覆寫）；取代會清空 5 條 builtin 常量路由（403／404／500／iframe-page／login） |

## GET /route/getUserRoutes（Authed）

| 面 | 內容 |
|---|---|
| 成功 | `data`＝`Api.Route.UserRoute`＝`{routes: MenuRoute[], home}` |
| `routes` | DB-fresh roles → Casbin `menu` 維度過濾 → 祖先包含 → 同層 `order`→`id` 升冪 |
| `home` | 啟用角色依 role id 升冪取首個非空 `role_home`，全空→`home`；再經兜底（驗屬可見樹可導航葉、不屬→先序第一可導航頁） |

★`home` 型別為 elegant-router 生成的字面聯集——回非法值時前端靜默不改 root redirect（無錯誤訊息），故 tasks 須有合成多角色測試釘住收斂律。

## GET /route/isRouteExist（Authed）

請求 `?routeName=`；成功 `data`＝boolean（依 route_name 於 sys_menu 存在性判定）。dynamic 模式下前端 `getIsAuthRouteExist` 走此端點（static 模式走本地表 ⇒ 未翻 `.env` 則此端點零呼叫）。

## 動詞不符（002 既有、本刀零改動）

已註冊路徑遇未註冊動詞 → `4040`＋HTTP 404（框架預設 405 不露出；`allow` 標頭由外殼剝除）。組裝次序（002 `router.rs` 既定）：route 註冊 → 各子 router `enforce_mw` layer → merge → `.fallback()` → `.method_not_allowed_fallback()` → metric layer → 外殼 `strip_allow_header`。

| 情境 | 結果 |
|---|---|
| Public 路由＋動詞不符 | `4040`＋404 |
| Authed 路由＋未認證＋動詞不符 | `4040`＋404（mnaf 在 layer 之後 ⇒ 不經 `enforce_mw`、零路徑存在性洩漏） |
| Authed 路由＋已認證＋動詞不符 | `4040`＋404 |
| 完全未註冊路徑 | `4040`＋404 |

本刀 12 條新 route 自然納入上表；`router.rs` 既有守恆測試（合成受保護條目直打）覆蓋 Authed 新成員。
