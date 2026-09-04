# Contract — wire：系統設定兩端點＋信封例外二＋前端接線層（002-system-settings）

> 承 `rev5:002-system-settings` contracts/wire-settings 形、rev6 座標與 clarify 2026-09-05 差異逐處標 ★；權威序＝憲法 §I.3（base-web typings 實碼＝wire 唯一權威）＞本檔＞data-model。
> 埠：rev6 API dev 直連 32079、front-nginx 32080（`/api/*` strip 轉發；`/health` 自答塊、`/api/metrics` 擋塊）。

## §1 讀端 `GET /systemManage/getSystemSettings`

- 授權：Policy（R_SUPER only；casbin seed 政策列 66）。
- 請求：無 body、無 query（不認識的 header 一律忽略——憲法 §II #1）。
- 成功：HTTP 200、`{data: SettingItem[16], code:"0000", msg:"common.success"}`；`settingKey` 升冪穩定序；僅未刪列；★description 為 NULL 者該欄缺席（不回 null）。
- 錯誤矩陣：

| 情境 | 碼 | msg key | HTTP |
|---|---|---|---|
| 越權（政策無授，R_ADMIN 組合；含角色軟刪或停用） | 5003 | system.forbidden | 403 |
| 未認證（無 `Authorization` 標頭／非 Bearer 形／token 不在 dev 表） | 8888 | auth.session.reLogin | 200 |
| 庫中 setting_type 未知型、或 ★已知鍵型別與 registry 不一致 | 5000 | system.internal | 200 |

  末列非寫端專屬：讀寫路徑觸及皆同、不跳過該列（機器面＝具名 integration 案）。

## §2 寫端 `POST /systemManage/updateSystemSetting`

- 授權：Policy（R_SUPER only；casbin seed 政策列 67；act＝POST）。
- 請求：`UpdateSystemSettingReq`（camelCase JSON body；三態語意＝data-model §8）。
- 成功：HTTP 200、★`{data:null, code:"0000", msg:"common.success"}`（不回更新後物件）；落庫效果＝settingValue canonical 形＋updated_at／updated_by 成對＋description 依三態；同值更新照寫審計欄。
- 錯誤矩陣（全部零寫入）：

| 情境 | 碼 | msg key | HTTP |
|---|---|---|---|
| settingValue 型別不符／超範圍／enum 外值（含大小寫不同）／小數／溢位 | 2222 | biz.systemSettings.invalidValue | 200 |
| settingValue 顯式 null（NOT NULL 欄清空） | 2222 | biz.systemSettings.invalidValue | 200 |
| settingKey 不在 registry 宣告集（含軟刪防禦態——判定落點＝facade filter） | 2222 | biz.systemSettings.notFound | 200 |
| settingKey 或 settingValue 欄缺席／型別非 string／JSON 反序列化失敗 | 2222 | biz.systemSettings.invalidValue | 200 |
| 越權（政策無授，R_ADMIN 組合；含角色軟刪或停用） | 5003 | system.forbidden | 403 |
| 未認證（無標頭／非 Bearer 形／token 不在表） | 8888 | auth.session.reLogin | 200 |
| 庫中 setting_type 未知型、或 ★已知鍵型別與 registry 不一致 | 5000 | system.internal | 200 |

## §3 碼面斷言（contract test 消費）

1. 本刀可發碼恰六：0000／2222／4040（router fallback）／5003／5000／8888。
2. 1000／3333／7777＋4 保留碼（7778／8889／9998／9999）＝AppError 無變體、構造層不可發出（cargo 型別層保證＋contract 斷言雙錨）。
3. 信封三欄宣告序 `data→code→msg`；code 恆 string；錯誤 `data:null` 不省略；business error 一律 HTTP 200（例外僅 4040→404、5003→403）。
4. msg 恆穩定 i18n key（後端不在地化）；★名冊恰七鍵（data-model §6）、contract 雙向斷言（實發 ⊆ 名冊、名冊每鍵 ≥1 發出點）。
5. 信封例外恰二：`/health`（plain text "ok"）、`/metrics`（Prometheus exposition）。
6. ★fallback 同形（clarify Q4）：未註冊路徑（如 `GET /nope`）與方法不符（如 `POST /health`、`GET /systemManage/updateSystemSetting`）皆回 HTTP 404＋`4040` 信封；
   零無信封 405；兩案為獨立測試函式、不進 case registry。
7. 不認識的 header（如 `apifoxToken`）一律忽略、不改變任何回應（憲法 §II #1；case 附斷言）。

## §4 快照與覆蓋閘契約

- 快照產製：`python3 tools/wire-schema.py extract`（base-web 容器內 `npx typescript-json-schema@0.67.4` 唯讀抽取、`--strictNullChecks`、原子替換寫入
  `rust-api/server/tests/fixtures/wire-schema.json`；需 stack 在跑）；drift 閘＝`check`（重抽 byte 比對；pre-commit `--staged-gate` 收窄：staged base-web gitlink 區間零 typings 變動即跳過；
  ★docker 缺或 `base-web` 容器未起＝具名跳過 rc 0、容器在而重抽失敗或不一致＝rc 2——clarify Q5）。
- 受審 definitions（本刀新增）：`Api.SystemManage.SystemSetting`（讀端序列化輸出必過；★description 不含 null）＋`Api.SystemManage.UpdateSystemSettingReq`
  （service 送出形錨定；description 呈 `["null","string"]`）。
- 覆蓋閘：`server/tests/contract.rs` case registry 與 `router::ROUTES` 之 case_key **雙向**比對——每條 route 必有 case（缺即紅指名）、每個 case 必對 route（殭屍即紅指名）。本刀 case 集恰四：health／metrics／get-system-settings／update-system-setting。
- 負向自證（DoD）：抽掉 update-system-setting 案→紅指名→還原全綠；加一殭屍案→紅指名→還原。

## §5 前端接線層契約

- `base-web/src/typings/api/rev6-settings.d.ts`（§III.1 ADAPT 軌道新檔）：declaration merging 併入 `Api.SystemManage`（不改既有 `system-manage.d.ts`）；
  `SystemSetting { settingKey: string; settingValue: string; settingType: string; description?: string }`、`UpdateSystemSettingReq { settingKey: string; settingValue: string; description?: string | null }`。
- `base-web/src/service/api/rev6-settings.ts`（§III.1 WRAPPER 軌道新檔）：直接路徑 import `../request`（不經 barrel `index.ts`）；
  `fetchGetSystemSettings(): request<Api.SystemManage.SystemSetting[]>`＋`fetchUpdateSystemSetting(req): request<null>` 兩函式、型別完備（未來 view 刀接上即用）。
- ★兩檔檔頭一行 fork-delta 新增型圈界標記（契約字面＝contracts/code-gates.md §1.3）：`// [rev6-inline BASE-WEB-ADAPT+ 002-system-settings] …`／`// [rev6-inline BASE-WEB-WRAPPER+ 002-system-settings] …`。
- 零 inline、零 `.env` 改動、零 locales 改動；容器內 `pnpm typecheck` 綠為驗收面。
