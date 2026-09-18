---
id: "LL-00023"
rule_id: "RL-0010"
promotion_surface: none
---
LL-00023｜implementer 跑到一半被外力中止（模型限額）時，resume 原 run 會讓未完成的那支整支重跑並撞上自己留在工作樹的半成品

**徵狀**：004 刀 U1（兩支 implementer serial）跑到第二支收尾自驗時，implementer 所用模型觸限額、user 叫停；主線 TaskStop 後 journal 只有第一支的 `result`，第二支的改動（`config.rs` 逾千行）已完整落在工作樹，卻沒有結構化 report——先紅後綠原文與打壞判準演練紀錄一併遺失。

**成因**：Workflow 的續跑快取以「已完成的 agent 呼叫」為單位：未回傳者無快取、resume 即整支重跑；而重跑的那支會讀到自己上一輪寫到一半（或已寫完）的碼，既可能重工、也可能把半成品誤判為既有基線。換模後 resume（opts 變更使快取失效）同病。

**處置**：不 resume。①主線先對工作樹取機器證據（容器內 fmt／build／test 兩次、comment-overlap、限定面 numstat、lock 斷言）；②另組**零 implementer 續跑形**（`IMPLEMENTERS=0`、`IMPL_STAGES=[]`、新冒煙 token、新 runId），`CONTEXT` 寫明「兩支已跑過、改動在樹上未 commit、缺哪一支的 report」與主線已取之證據；③缺 report 造成的歷史證據缺口明文裁定為非 blocker，改由規格審查的「判準級變異（非 vacuous）」面補足，並指名至少幾處變異；④unitdef 自原單元定義派生（同源的允許清單與審查 prompt），只加續跑段。實績：審查段照常收斂（規格 4 輪、碼品質 4 輪），並抓出三筆 implementer 自驗抓不到的真缺陷。

**再犯面與守法**：凡 run 因外力中止（限額、TaskStop、斷線），先讀 journal 分辨「誰有 `result`」，再看工作樹分辨「誰的改動已落地」；兩者不一致的那一支一律視為「碼在、證據不在」，走零 implementer 續跑形而非 resume。審查／fix 與 implementer 分用不同模型時，續跑形天然不受 implementer 側限額影響。
