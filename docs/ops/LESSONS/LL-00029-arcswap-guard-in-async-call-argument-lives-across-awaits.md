---
id: "LL-00029"
rule_id: "none：`ArcSwap` 讀端 Guard 之生命週期屬碼面慣例、由呼叫點碼註與 code review 承載，無對應 RL 條目"
promotion_surface: none
---
LL-00029｜`ArcSwap::load()` 的 Guard 寫在 async 呼叫的實參位→暫時值活到整句敘述結尾，被存進 future、跨過整段 await

**徵狀**：004 刀 U9 login 步驟②初版把 `&state.ip_rules.load().allow` 直接寫進 `throttle::precheck(...)` 的實參；編譯與測試全綠，碼品質審查才指出該 Guard 橫跨 precheck 內兩次 redis GET 與數支 PG 查詢的 await。

**成因**：Rust 的暫時值活到所在敘述結尾；敘述是 `f(...).await` 時，實參位的暫時值會被捕進 future、活過整段 await。`arc-swap` 每執行緒只有少數 fast slot，Guard 長時間不放會把後續 `load()` 擠到慢路徑，並延後舊規則集的回收——功能面量不到、只在負載下顯形。

**處置**：把「自規則集取值」拆成獨立一句同步敘述（`let source = throttle_source(.., &state.ip_rules.load().allow);`），回傳值不借用規則集、Guard 於該句結尾即放；呼叫點留一句碼註講理由。防法：凡 `ArcSwap`／`RwLock` 讀端 Guard，一律先在同步敘述裡取出「不借用 Guard 的值」再進 async 呼叫；審查 async handler 時專看實參位的 `.load()`／`.read()`。
