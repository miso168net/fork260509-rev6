---
id: "LL-00020"
rule_id: "none：走查探針配方——守法句寫進本檔與走查腳本範本（輪詢 exp 形），非規則句"
promotion_surface: none
---
LL-00020｜CDP 走查用「單次 setTimeout 算到 access 過期」等待，在 WSL2 下短睡約 14 秒——探針落在 `exp` 之前觸發、得 0000 而非 3333，假象＝「前端沒接自動續期」或「後端 leeway 非 0」

**徵狀**：003 刀 U11（run `wf_d74d20aa-54e`）T075 §2 續期面首版走查腳本以 `sleep(exp*1000 - Date.now() + 8000)` 等 access 過期，實際在 `exp−6` 秒就醒來打 `getUserInfo`，回 `0000`、`refreshToken` 呼叫數＝0、票未換發；同一支把安全帶加到 `+15000` 仍只落在 `exp+1` 秒——單次 `setTimeout` 相對牆鐘短少約 14 秒。若把「頁面仍在／未被登出」當判別器，會誤判為自動續期未接線或 leeway 非零（實況：leeway=0、續期鏈正常）。

**成因**：長時間單次 timer 在 WSL2（與 Docker Desktop 共用的虛擬時鐘）下與牆鐘不同步——與 LL-00017／BL-00051 記的「容器時鐘可倒退」同族：任何以「牆鐘算一次、睡到某刻」的等待，在此環境都不可靠。

**處置**：走查腳本改為以 `exp` 為輪詢條件（`while (Date.now()/1000 <= exp) await sleep(1000)` 再加安全帶）、每輪讀真時間；判別器改為「逐筆回應原文 code」（`3333`→`refreshToken`→重放 `0000`）與 claims 換新（`iat`／`exp`／jti），不看頁面態。走查後伺服器側另以 curl 於 `exp+11` 秒取 `3333` 佐證 leeway=0。

**再犯面與守法**：凡走查／探針要「等到某個時刻」（token 過期、TTL 到期、idle 逾時、lock 窗）一律以目標時刻為輪詢條件、不用單次長睡；判別器一律取回應原文 code／msg 或 DB／redis 現值，不取 UI 存在與否；首次失敗先懷疑計時而非功能——先印「觸發時刻 vs exp」再下結論。守法句已寫進 U11 走查腳本範本；後刀 CDP 走查 unitdef 引本檔。
