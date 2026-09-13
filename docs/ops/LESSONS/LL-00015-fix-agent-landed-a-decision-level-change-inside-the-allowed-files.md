---
id: "LL-00015"
rule_id: "RL-0075"
promotion_surface: rules
---
LL-00015｜審查員標明「拍板級、超出 fix agent 權限」的修法，下一輪 fix 仍逕自落地——空間邊界只圈檔、不圈行為級別

**徵狀**：003 刀 U1（run `wf_bbe94fcc-bf4`）規格對照審查第 2 輪把「是否連 PG NOTICE 一併壓下」逐字列為【拍板級·觀測面行為變更】，並寫明兩個落點「都超出 fix agent 權限，故本輪只在 main.rs 補上據實碼註」；第 3 輪 fix 收到同一 finding 附帶的「建議修法①（落地達 DoD）」後，就在 `main.rs` 的 subscriber 加了 `.add_directive("sqlx::postgres::notice=warn")`——`main.rs` 在允許清單第 6 項內、fix 自檢因此全過，第 4 輪確認輪零 blocker 判收斂。一個 operator 可見的行為變更（`EnvFilter` 對同 target 是「後加即取代」⇒ 營運者顯式設 `RUST_LOG=sqlx::postgres::notice=info` 也會被碼裡那條蓋掉、永遠調不回來）就這樣穿過整條 fix→review 迴圈，直到主線收尾第①步逐項復核才攔下、改由 user 拍板（移到 compose 的 `RUST_LOG`、控制權留給營運者）。

**成因**：防呆六件套⑥的空間邊界是**檔級**的——`ALLOWED_BLOCK` 回答「碰得到哪些檔」，fix 的升級判準（六件套④）也只問「改動落不落在清單內」。「這個改動的**行為級別**是不是拍板級」不在任何一道機器或 prompt 判準上，於是「檔在清單內」＝「可以改」被當成充分條件。審查員雖已在 finding 內文標了級別，但那是自由文字、對 fix 的處置流程零約束力；`escalatedFindings` 的結構化欄位也只承載「落在清單外」這一種升級理由。

**處置**：主線於 U1 收尾撤掉該 `add_directive`（碼註改述為「刻意不追加、理由＝控制權歸屬」），壓制點移到 `docker-compose.yml` 的 `RUST_LOG: "info,sqlx::postgres::notice=warn"`（user 拍板 2026-09-08）；實測 boot log 首行即「boot 就緒」、`sqlx::postgres::notice` 與 `sqlx::query` 行數皆 0，而營運者改 compose 或以環境變數覆寫即可把 NOTICE 開回。

**再犯面與守法**：凡 fix／implementer 收到的 finding 涉及 user 或 operator 可見的行為變更（log 面預設值、回應碼與訊息、端點行為、部署設定預設），檔級清單就不再是充分條件——級別邊界與空間邊界正交，兩道都要過。守法落 RL-0075（fix／implementer scope、prompt carrier）：凡改動屬拍板級判準（user／operator 可見行為變更、schema／migration、feature scope 邊界、破紀律例外），**縱使檔在允許清單內**亦一律 `done_with_escalation`＋`escalatedFindings` 結構化指名，不得落地；審查員在 finding 內文標了「拍板級／超出權限」時，該 finding 的行為變更修法 MUST NOT 由 fix 落地——只落「據實碼註」這一半。主線收尾第①步的逐項復核是這條的最後一道網，不可省。
