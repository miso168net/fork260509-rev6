---
id: "LL-00021"
rule_id: "none：變異演練的執行環境配方——守法句寫進本檔與演練腳本，非流程規則"
promotion_surface: none
---
LL-00021｜drvfs 上以 subprocess 對同一 python 模組連續注入變異並重跑自測，同一秒寫入且檔長相同的兩支變異會沿用前一支的 `.pyc`——變異「假存活」（或假紅），誤判守門強度

**徵狀**：maint-backlog-pre-004 A2b implementer-1 對 `tools/docsync/snapshot.py` 逐支變異（`tmp/maint-a2b-impl1-mutate-snapshot.py`），M4「findings 不擋」首跑全綠＝看似守門未抓到；同批 A2a 規格審查對 `tools/wire-schema.py` 常數做 M6b 變異，首跑亦出現與改動不符的結果。兩者改用獨立 bytecode 快取重跑後即如預期轉紅。

**成因**：CPython 預設以「時間戳形」`.pyc`（PEP 552）驗證快取——檔頭只記來源檔 mtime（秒）與檔長，兩者相符即直接載入舊 bytecode。變異腳本在同一秒內寫出第二支、且字元替換前後檔長不變時，import 到的是上一支的編譯結果；drvfs（9p）上 mtime 解析度與寫入時序更容易湊齊這個條件。

**處置**：每支變異以獨立快取根重跑（`PYTHONPYCACHEPREFIX=<每支專屬暫存目錄>`），或變異後先刪對應 `__pycache__`；還原後以 `cmp` 驗原檔 byte 全等。A2b 以前者重跑 M4 即紅；A2a 審查改路徑並關 bytecode 後 M6b 即正確。

**晉升面**：none（演練環境配方；守法寫進本檔與各單元 tmp 變異腳本）。

**再犯面與守法**：凡在 /mnt/* 以 subprocess 反覆改寫同一 `.py` 再 import 或跑其自測（變異演練、打壞判準→紅→還原），每次重跑一律帶獨立 `PYTHONPYCACHEPREFIX`（或 `python3 -B` 搭配清除既有 `__pycache__`）；判讀「變異存活」前先排除快取——存活結論須在獨立快取下重現一次才成立。
