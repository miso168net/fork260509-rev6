# 契約 — msg key 名冊與 i18n backend 樹（跨端閘面）

後端 `msg` 載**穩定 i18n key**（語言無關、不在地化；憲法 §I.3）；前端經 ``$t(`backend.${msg}`, msg)`` 轉譯、未命中回原文 fallback（★I18N-WIRING(i)）。
名冊單一來源＝`rust-api/server/src/error.rs` 之 `MSG_KEYS`（13 鍵；元素為 `msg_key::NAME` 常數引用、字面只住 `pub mod msg_key`；**宣告序**＝002 既有七鍵現行序＋本刀六鍵、見表下）；三檔 backend 子樹逐檔雙向全等（clarify Q2；閘契約＝code-gates.md §2）。表中 # 欄為閱讀序、非宣告序。

## 13 鍵全集（三語譯文；繁中權威＝本表→`zh-tw.ts` 逐字；簡中／英文以 rev5 為藍本重打字消化）

| # | key | 構造形 | code | zh-TW | zh-CN | en-US | 來源 |
|---|---|---|---|---|---|---|---|
| 1 | `common.success` | `Success` 固定鍵 | 0000 | 操作成功 | 操作成功 | Operation successful | 002 |
| 2 | `system.internal` | `Internal` 固定鍵 | 5000 | 系統發生內部錯誤，請稍後再試 | 系统发生内部错误，请稍后再试 | An internal error occurred. Please try again later | 002 |
| 3 | `system.notFound` | `NotFound` 固定鍵 | 4040 | 找不到請求的資源 | 找不到请求的资源 | The requested resource was not found | 002 |
| 4 | `system.forbidden` | `PermissionDenied` 固定鍵 | 5003 | 沒有權限執行此操作 | 没有权限执行此操作 | You do not have permission to perform this action | 002 |
| 5 | `auth.session.reLogin` | `Logout` 固定鍵 | 8888 | 請重新登入 | 请重新登录 | Please log in again | 002（★本刀不動、勿漏列） |
| 6 | `biz.systemSettings.invalidValue` | Biz 構造點 | 2222 | 設定值不合法（型別不符、超出範圍或非允許選項） | 设置值无效 | Invalid setting value (wrong type, out of range or not an allowed option) | 002 |
| 7 | `biz.systemSettings.notFound` | Biz 構造點 | 2222 | 找不到指定的設定鍵 | 设置项不存在 | The specified setting key was not found | 002 |
| 8 | `auth.login.failed` | `LoginFailed` 固定鍵 | 1000 | 帳號或密碼錯誤 | 用户名或密码错误 | Incorrect username or password | **本刀** |
| 9 | `auth.token.expired` | `TokenExpired` 固定鍵 | 3333 | 登入已逾時，正在重新取得授權 | 登录已过期，正在重新获取授权 | Session expired, refreshing | **本刀** |
| 10 | `auth.session.kicked` | `ModalLogout` 固定鍵 | 7777 | 您的帳號已在其他裝置登入，此工作階段已結束 | 您的账号已在其他设备登录，当前会话已结束 | Your account signed in elsewhere; this session ended | **本刀** |
| 11 | `biz.auth.notSupported` | Biz 構造點（`alt_stub.rs`） | 2222 | 該功能尚未開放 | 该功能暂未开放 | This feature is not available yet | **本刀** |
| 12 | `biz.auth.captchaRequired` | Biz 構造點（`throttle` captcha 閘） | 2222 | 請完成圖形驗證碼後再試 | 请完成验证码后再试 | Please complete the captcha and try again | **本刀** |
| 13 | `biz.auth.locked` | Biz 構造點（`throttle` 鎖定） | 2222 | 嘗試次數過多，請稍後再試 | 尝试次数过多，请稍后再试 | Too many attempts; please try again later | **本刀** |

**`MSG_KEYS` 宣告序（13）**：`common.success`／`biz.systemSettings.invalidValue`／`biz.systemSettings.notFound`／`system.notFound`／`system.forbidden`／`system.internal`／`auth.session.reLogin`（002 既有七鍵、`error.rs` 現行序不動）→ `auth.login.failed`／`auth.token.expired`／`auth.session.kicked`／`biz.auth.notSupported`／`biz.auth.captchaRequired`／`biz.auth.locked`（本刀六鍵追加）。

★Biz 構造點鍵一律 `biz.<domain>.<case>`（`rev5:R3-4` 正規化；前端 captcha 軟區判斷式拿 `msg` 字面比對 `biz.auth.captchaRequired` 區分兩態、須用此名）；三個本刀新增 Biz 鍵與 002 既有兩鍵一律 `Cow::Borrowed(msg_key::NAME)` 常數形構造（字面只住 `pub mod msg_key`＝002「零第二份 wire 字面」不變式；跨端閘 Biz 守衛接受字面形與常數形、拒動態構造）。
★rev5 另有九鍵前端內部白名單（`biz.user.passwordViolation.*` 八鍵＋`common.listSeparator`）——rev6 **不建**；`translateDetailValue` 亦不建（rev6 錯誤信封 `data` 恆 null、無明細通道；I18N(i) 只有單一 helper `translateBackendMsg(msg)`）。

## 樹形（三檔同構；`zh-tw.ts` 裸 object、不接 runtime）

```ts
backend: {
  common: { success: '…' },
  system: { internal: '…', notFound: '…', forbidden: '…' },
  auth: {
    login: { failed: '…' },
    session: { reLogin: '…', kicked: '…' },
    token: { expired: '…' }
  },
  biz: {
    systemSettings: { invalidValue: '…', notFound: '…' },
    auth: { notSupported: '…', captchaRequired: '…', locked: '…' }
  }
}
```

- `en-us.ts`／`zh-cn.ts`：頂層 object 內插入獨佔一行 `  backend: {` 起的區塊（新增型圈界標記；★I18N-WIRING(ii)）；`app.d.ts` `App.I18n.Schema` 補同構 `backend` 必填型節（★I18N-WIRING(iii)）⇒ `pnpm typecheck` 免費守兩語結構。
- `zh-tw.ts`：新檔、檔頭 `// [rev6-inline BASE-WEB-I18N-WIRING+ 003-auth-session] …`、裸 object（`export default {` 換行後 `  backend: {` **獨佔一行**＝跨端閘右源錨、與兩語插入錨同形）、無 `App.I18n.Schema` 標註、不註冊 `LangType`（Q3）。
- 跨端閘攤平比對：`backend.common.success` 等 13 條鍵路徑 ⇔ `MSG_KEYS` 字面（`common.success` 等）逐檔全等。

## 機器閘落點

| 閘 | 規則 | 本刀動作 |
|---|---|---|
| `error.rs` 名冊測試 | `MSG_KEYS` 恰十三、序固定、無重複；固定鍵 `key()` ∈ 名冊；Biz 五鍵 ∈ 名冊 | 三支測試改對（research R7-3 ⑥⑦⑧） |
| `tests/contract.rs` 雙向 | 每條 route 每個錯誤路徑實發 msg ∈ 名冊；名冊每鍵 ≥1 發出點 | 16 case 補 6 鍵發出點 |
| `tools/msg-key-gate.py` | 三檔 backend 子樹 ⇔ `MSG_KEYS` 逐檔雙向；Biz 字面守衛 | 新工具（code-gates.md §2） |
| `pnpm typecheck` | `app.d.ts` `backend` 必填型節守兩語結構 | I18N(iii) |
