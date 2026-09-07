---
id: "LL-00014"
rule_id: "none：屬本機驗證程序的環境面陷阱、非流程規則；守法（等長改動的反例驗證前後清 __pycache__）寫進本檔"
promotion_surface: none
---
LL-00014｜等長字元替換＋同一秒內還原＝CPython 判 pyc 仍有效而沿用舊碼——反例驗證讀到假結果

**徵狀**：為 LL-00013 取紅→綠證據，把 `[ \t]*` 暫改回 `[ \t]+` 跑新測案（紅、如預期），`cp` 還原修正版後再跑，測案**仍紅**；`grep` 明明顯示檔案裡是 `*`，而 `python3 -c "print(gates.RE_GATE_BLOCK.pattern)"` 印出的是 `+`。

**成因**：CPython 預設以 (原始碼 mtime 秒數, 位元組數) 判 `__pycache__/*.pyc` 是否過期。`[ \t]*`↔`[ \t]+` 是**等長**替換＝size 不變；還原動作又落在與前次寫入**同一秒**內＝mtime 秒數不變。兩個判準同時不動，Python 遂沿用暫改版留下的 bytecode。

**處置**：`find tools deploy -name __pycache__ -type d -exec rm -rf {} +` 清乾淨後重跑，regex 與 `gate_id(gt_01)` 立即回正確值。

**晉升面**：none（守法住本檔）。

**再犯面與守法**：凡做「暫改→跑→還原」式反例驗證且改動可能等長（旗標字元、比較運算子、`+`／`*`、`>=`／`<=`、單字元常數），還原後**先清 `__pycache__` 再跑**；或用 `python3 -B` 跑該次驗證。徵狀識別：檔案內容與程式讀到的值矛盾（grep 與 runtime 不一致）＝先查 bytecode 快取，不要再去改邏輯。同理適用於任何靠 mtime＋size 判快取的層（LL-00005 的 bind-mount 目錄佔位快取是同一家族的不同層）。
