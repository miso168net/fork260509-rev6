---
id: "LL-00112"
rule_id: "RL-0028"
promotion_surface: none
---
LL-00112｜CDP 生成器之設定 seed 值表取自全量測試進行中之 dev 庫：`single_session_default` 讀到測試暫態 `on`（真源 m0002 為 `off`），連帶放行點四擬稿寫出不存在之「seed 帳號單一會話互相頂替」句（008 刀 U18）

**徵狀**：U18 主線在 T164 quickstart §9 全量測試背景執行期間，以 psql 讀 `system_settings` 當作 seed 值表寫入 CDP 生成器；`single_session_default` 讀得 `on`，而 m0002 seed 與測試結束後之現庫皆為 `off`。生成器之 settingsAtSeed 閘與放行點四擬稿皆據此錯值；第三層清冊 run 於派發前抓到。

**成因**：把「現庫值」當「seed 值」。seed 之真源是 migration（m0002），dev 庫只是其投影；全量測試期間有測試暫改設定再還原，讀到的是暫態。讀庫前也沒確認當下有無在跑之測試或走查。

**處置**：生成器之 seed 值表改以 m0002 為源，並於派發前斷言現庫與之逐鍵相等；放行點四擬稿刪去錯句。

**晉升面**：none。判準同 RL-0028（prompt 之事實接地每條附出處）；守法落在主線撰寫生成器時。

**再犯面與守法**：
- seed 值一律取 migration 原檔（m0002 等）；dev 庫值只作「現況＝seed」之對賬斷言、不作來源。
- 讀 dev 庫取任何基準前，先確認無在跑之全量測試、走查或 jobs（背景 task 清單、`docker ps`）；有則等其結束，或改讀真源。
