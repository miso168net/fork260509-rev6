---
id: "LL-00056"
rule_id: "none：同 LL-00032（cargo 以 mtime 判新舊之假綠）；本則把守法自 drvfs 擴及容器內副本，寫進本檔與後續單元定義，不另立規則"
promotion_surface: none
recurrence_of: "LL-00032"
---
LL-00056｜容器內副本做判準變異、各發共用同一個 target 目錄——被換檔的 mtime 早於上一發建置時，cargo 靜默沿用上一發的執行檔，結果與變異無關（006 刀 U7）

**徵狀**：006 刀 U7 implementer-1 的判準變異第一輪（容器內副本、各發共用一個獨立 target 目錄、一次一支 cargo），第 2～4 發跑的是第 1 發建好的執行檔：cargo 未重編，結果與所換入的變異無關。察覺後三發作廢，改為每發先 touch 被換檔、並以該發 log 的 `Compiling server` 計數＝1 自證重編後重跑，各得應有之紅。

**成因**：cargo 的 fingerprint 以 mtime 判新舊。副本以 tar 複製（保留原 mtime），被換檔的 mtime 早於上一發的建置產物時，cargo 判定「無事可做」。LL-00032 記的是 drvfs 跨 host↔容器 mtime 不傳之形，處置框在「host 改檔後容器內 touch」；本形不經 drvfs、純在容器內，同一機制換了入口，守法因框在 drvfs 而未被套用。

**處置**：每發 touch 被換檔＋計數自證、三發重跑；後續單元定義的判準變異段同批烤入此句。

**晉升面**：none——守法寫進本檔與後續單元定義。

**再犯面與守法**：凡以 cargo 驗「改了碼、期待結果跟著變」——不論改檔在 host、drvfs 或容器內副本——每發先 touch 被換檔，並以該發 log 的 `Compiling` 計數（或產物 mtime 晚於 touch）自證重編；只見 `Finished` 而無 `Compiling`＝該發作廢重跑。徵狀是假綠或「紅得不對」，閘攔不下，防線只有起手動作。
