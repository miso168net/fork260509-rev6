---
id: "LL-00085"
rule_id: "none：同 LL-00082，DoD 字面之寫法守在 tasks 撰寫與單元定義審讀，不另立規則"
promotion_surface: none
recurrence_of: "LL-00082"
---
LL-00085｜DoD 以字面 grep 計數斷言「恰 N 處」或「零命中」，同一字面在檔內另有說明性的出現（修改型的 `原行:` 紀錄、包裝函式 JSDoc 引端點路徑），照字面跑就多計——007 刀 U17、U18 連兩單元各踩一次

**徵狀**：
- 007 刀 U17（T081）：DoD 四條字面 grep（`patternRules`、`patternRules.phone`／`REG_PHONE`、`fetchGetUserList` 之匯入來源、`fetchGetAllRoles` 之 barrel 匯入）照字面跑，都命中 `原行:` 標記行。憲法 §III 規定修改型 MUST 以 `原行:` 逐字記下被替換的基線行，基線字面因此必然留在檔內。三支 implementer 一起升級，主線裁定先剔除 `原行:` 行再判。
- 007 刀 U18（T086）：DoD「`git -C base-web grep -n '/systemManage/unlockLogin' -- src` 恰 1 處」實得 2 行。`src/service/api/rev6-user-admin.ts` 十一支包裝的 JSDoc 都依檔內慣例引自己的端點路徑，所以該路徑一行在 JSDoc、一行在 `url:`。implementer-2、-3 各自升級，主線裁定改以 `url: '/systemManage/unlockLogin'` 形計數。

**成因**：
1. DoD 拿來計數的是名稱，不是該名稱的宣告形或消費形。repo 慣例本來就會在別處以說明身分寫出同一字面（fork-delta 逐字紀錄基線行、包裝檔逐支註明路徑），寫 DoD 時沒對現檔實跑，看不到這些出現。
2. 與 LL-00082 成因 3 相同：tasks 產出期與 analyze 期都不實跑 DoD 命令，字面誤差要到單元出口才第一次暴露，每次都多耗一輪升級與主線裁定。

**處置**：U17 收尾在 T081 DoD 補上「先剔除 `原行:` 行再判」；U18 收尾在 T086 DoD 補上「以 `url:` 形計恰 1」。兩處都只插入說明，DoD 原有字面不改。

**晉升面**：none。與 LL-00082 同族：守法落在 tasks 撰寫與單元定義審讀，不另立規則。

**再犯面與守法**：
- 寫「恰 N 處」或「零命中」的字面 grep DoD 時，先對現檔（或藍本檔）實跑一次，看命中裡有沒有說明性的出現。計數對象改取宣告形或消費形（`url: '<路徑>'`、`import … from '<模組>'`、呼叫括號），否則就在條文寫明剔除條件（例：`grep -v '原行:'`）。
- 主線派發單元前，對 DoD 裡的字面計數條逐條實跑現況值（尚未實作的就寫出預期值），一併寫進 ground。
