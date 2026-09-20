# Contract — 信任模型設定檔（TOML）

> 格式 TOML（承 rev5：內容是 CIDR 清單、旁註「哪段是哪家 CDN／何時更新／依據哪份官方表」需註解語法）。環境變數 `APP_TRUST_MODEL_PATH` 指向路徑、啟動一次載入、唯讀共享。★dev **必掛**：`deploy/trust-model.dev.toml`（創世已在、compose 已掛 `/etc/rev6/trust-model.toml`）＝部署樣例活體（spec FR-010）。解析＝`toml` 1.1.6（R1）。

## 集合語意（六項，皆可省略＝空集）

| 鍵 | 型 | 語意 |
|---|---|---|
| `internal_default` | CIDR 陣列 | 內網預設受信集 |
| `cf_gate_egress` | CIDR 陣列 | 掛邊緣驗證閘的我方出口集（覆蓋 B 前置） |
| `[tunnel] networks`／`connecting_ip_header` | CIDR 陣列／string | 通道來源集與訪客位址標頭名（省略＝`CF-Connecting-IP`） |
| `[[cdn]] networks`／`connecting_ip_header` | CIDR 陣列／string | CDN 段（Tier-1 位置錨判定面）與其訪客標頭名 |
| `[[my_public]] networks`／`dual_role` | CIDR 陣列／bool | 我方公開出口；`dual_role=true`＝該位址也可能是直連使用者 ⇒ walk 經過即 `proxy_soft` |
| `[[bindings]] public`／`internal` | CIDR 陣列 | 公開出口×專屬後置內網（右鄰不符即 `proxy_soft`） |

六集合聯集同時導出受信集與跳過集（同源對稱、F4／F6）。未知鍵＝載入告警（不當機）。

## 載入失敗語意（三層＋一、方向皆「只縮小信任」、皆不當機、皆發結構化告警＋`ip_domain_degraded_total`）

| 情境 | 行為 | source |
|---|---|---|
| 路徑未設／檔案讀不到 | 沿用扁平退路 `APP_TRUSTED_PROXY_CIDRS`（逗號分隔 CIDR、充 `internal_default`） | `trust_model_missing` |
| 檔案存在但整體解析失敗 | 全空＝全直連；★不套扁平退路 | `trust_model_invalid` |
| 單一集合含無效 CIDR | 只清空該集合 | `trust_model_set_cleared` |
| 單一集合含 IPv4-mapped 網段字面（如 `::ffff:10.0.0.0/104`；`rev5:B-074`） | 指名集合與壞字面、附改寫建議（`10.0.0.0/8`）、清空該集合；判別取位址本身而非遮罩後網段 | `trust_model_set_cleared` |

## dev 交付形（現檔、零改）

```toml
internal_default = [
  "172.16.0.0/12",   # docker 預設橋接網段
]
```

只填此項、其餘留空 ⇒ 經反向代理可達 `fallback`／`proxy_clean` 二態（research R7）。

## prod 樣例（RUNBOOK §16 實文由此擴充；FR-066）

```toml
internal_default = ["10.0.0.0/8"]
cf_gate_egress   = ["10.0.0.0/8"]      # 掛 CF 驗證閘的我方 ingress 出口——缺此項邊緣驗證標記不被採信
[[cdn]]
networks = ["173.245.48.0/20", "2400:cb00::/32"]   # 來源 https://www.cloudflare.com/ips/ ；★需定期更新且與 nginx geo 區塊同步
connecting_ip_header = "CF-Connecting-IP"
```

★checklist 必列：CDN 網段在 nginx `geo $cf_edge` 與本檔各存一份、用途不同（傳輸層對端 vs 轉發鏈位置錨）、MUST 同步更新；只改一邊的表徵＝信心大量落 `cdn_mismatch`。「鎖定來源站僅接受 CDN 邊緣連線」已由 F6 入碼、降為縱深防禦建議。

## 標頭契約（反向代理側、創世已在、本刀零改動）

| 標頭 | 注入規則 |
|---|---|
| `X-Real-IP` | 恆為反向代理觀察到的傳輸層對端 |
| `X-Forwarded-For` | 既有鏈＋反向代理觀察到的對端（附加於最右） |
| `X-CF-Verified` | 對端 ∈ CDN 邊緣網段→`"1"`；否則移除（client 自帶不倖存） |
| `CF-Connecting-IP` | 同條件透傳；否則移除 |

dev 的 `geo` 清單為空 ⇒ 後兩標頭恆被移除 ⇒ 邊緣驗證兩態 dev 不可達。後端常數：`MAX_XFF_TOKENS`＝32、`XFF_MAX_CHARS`＝1024（值以碼為單一權威）。
