---
id: "LL-00082"
rule_id: "RL-0067"
promotion_surface: none
---
LL-00082｜DoD 以「`git diff A..HEAD -- <檔> | grep -c <樣式>`＝0」斷言某行未改：被改行在其 3 行內時，預設上下文必帶出該未改行＝子庫 commit 後結構上必紅；commit 前跑則 `A..HEAD` 尚不含改動＝空轉 0（007 刀 U15）

**徵狀**：007 刀 U15（T074～T075）把 `src/locales/index.ts` 之 `locale:` 行之預設語言改為 zh-TW（修改型），T075 DoD 另要求退路語言不變，寫成 `git -C base-web diff fb4dac2..HEAD -- src/locales/index.ts | grep -c fallbackLocale`＝0。implementer 實跑工作樹形得 1，命中的是 diff 之上下文行 ` fallbackLocale: 'en',`（行首為空格、未改）——被改的 `locale:` 行就在它正上方。規格對照第 2 輪據此列 blocker；fix 輪因 tasks.md 不在允許清單內，只能零改動升級，整輪只花在一條計畫字面上。

**成因**：
1. unified diff 預設帶 3 行上下文。「某行未改」若以 diff 輸出之樣式計數表達，凡被改行落在該行 3 行內，該行即以上下文行身分出現，計數恆 ≥1。
2. 同一斷言若在子庫 commit 前照字面跑，`A..HEAD` 只見已 commit 之改動，得 0 屬空轉——兩個時點都量不到「退路語言是否被改」。
3. tasks 產出期與 analyze 期都沒有逐條實跑 DoD 命令；這類命令只有到單元出口才第一次執行。

**處置**：U15 收尾把 T075 DoD 改為 `git -C base-web diff -U0 fb4dac2..HEAD -- src/locales/index.ts | grep -c fallbackLocale`＝0（只數增刪行），保留 `git -C base-web grep -c "fallbackLocale: 'en'" -- src/locales/index.ts`＝1。fix 輪另做變異實證：暫把退路改成 zh-TW 時 `-U0` 形得 2（紅），還原後得 0。

**晉升面**：none。判準同 RL-0067（紅證須打在掃描面確實看得到的實例上）；本坑是斷言字面之寫法，守法落在 tasks 撰寫與單元定義審讀。

**再犯面與守法**：
- 寫 DoD 時，凡以 diff 輸出斷言「某行未改」或「某檔只動指定行」，一律用 `-U0`，或只數 `^[-+]` 行（排除 `+++`／`---` 檔頭）；並在同條附一個正向斷言（例：`git grep -c <原值>`＝1）。
- `A..HEAD` 形之斷言排在子庫 commit 之後跑；commit 前之工作樹改用 `git diff <基線>`（不帶 `..HEAD`）取證。
