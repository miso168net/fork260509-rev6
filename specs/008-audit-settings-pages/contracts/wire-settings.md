# Contract — 系統設定兩端點之本刀變更（讀 wire 擴三欄、寫端落稽核）

> 基底契約＝`specs/002-system-settings/contracts/wire-settings.md`（本檔只列差額；未列者照舊）。端點與授權不變：GET `/systemManage/getSystemSettings`（seed 66）、POST `/systemManage/updateSystemSetting`（seed 67），皆 R_SUPER、受保護＝封死集（不下放）。

## 1. 讀端 `SystemSetting` 擴三欄

| 欄 | 型 | 在場條件 | 值源 |
|---|---|---|---|
| `settingKey`／`settingValue`／`settingType`／`description?` | 既有 | 既有 | 既有 |
| `declared` | boolean | 恆在 | 鍵 ∈ REGISTRY 宣告集 |
| `rangeMin` | number | `declared ∧ settingType = "number"` | `validation::range_of(key).0` |
| `rangeMax` | number | 同上 | `validation::range_of(key).1` |

- rust：`SettingItem` 增 `declared: bool`、`range_min: Option<i64>`、`range_max: Option<i64>`（後兩者 `skip_serializing_if = "Option::is_none"`）；宣告集外列＝`declared: false`、兩界缺席。
- typings：`base-web/src/typings/api/rev6-settings.d.ts` 之 `Api.SystemManage.SystemSetting` 增 `declared: boolean; rangeMin?: number; rangeMax?: number;`（rev6 自有檔、檔頭標記既在）。
- wire 裁判：`tests/wire_schema.rs` 之 `SystemSetting` 受審案擴三欄正向＋反例（`declared` 缺席、界值非數值〔字串〕、界值為 `null`；整數性由 rust 側 `Option<i64>` 型別＋序列化後 `is_i64()` 釘值承擔——快照抽自 TS `number`、判不出小數）；快照重抽。
- 守衛照舊：庫中型別不在認識集或與宣告不一致＝整支 `5000`。
- 16 鍵之界值（REGISTRY 現值）：`password_min_length` 1～128、`password_max_length` 1～256、`login_throttle_max_fails` 1～100、`login_throttle_window_minutes` 1～1440、`login_throttle_captcha_after` 1～100、`ip_captcha_after` 1～100、`ip_max_fails` 1～100、`ip_window_minutes` 1～1440、`password_change_min_interval` 0～86400、`session_idle_timeout` 5～1440；六個二值 enum 鍵無界。

## 2. 寫端：wire 不變、語意三處變更

1. **固定序**（data-model §3.2）：請求上下文缺席＝`5000`、先於必填欄判定（原：寫端不讀上下文）。
2. **同交易稽核**：成功＝恰一列 `update`（data-model §7）；拒因（`2222`）＝零寫入、零稽核；`5000`＝整筆回滾。
3. **同值寫入**：照寫並照落一列（前後快照業務四欄相同）。

回應不變：成功 `0000`＋`data: null`；拒因 `2222 biz.systemSettings.invalidValue`／`notFound`；授權 `5003`／`8888`。

## 3. 前端消費（設定頁）

- 數字框 `:min`／`:max`＝`rangeMin`／`rangeMax`（10 個 number 鍵皆有）；`declared: false`＝唯讀。
- 寫入政策七鍵（`password_min_length`、`password_max_length`、`password_require_digit`、`password_require_lowercase`、`password_require_uppercase`、`password_require_special`、`password_forbid_username`）任一成功後呼叫 `clearPwdPolicyCache()`。
- `rev6-settings.ts` 兩支 fetcher 不改。

## 4. 與 rev5 比對

rev5 讀 wire 為四欄、前端手抄 `numberRanges` 五鍵；寫端零稽核。rev6 本刀三處差異皆入 spec 刻意分岔表（設定變更入操作日誌、數字框 10 鍵鉗界、宣告集外列唯讀）。
