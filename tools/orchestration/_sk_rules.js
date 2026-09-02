const RULES = [
  '★不可違反項（全數烤入、違反即單元失敗）：',
  '1. 一切書面產物（report／blocker／**程式碼註解**／文件）**一律 zh-TW**（繁體中文；識別字、程式碼、路徑保留原形）。',
  '2. **絕不 push／merge／git commit**——只改工作樹，git 操作由主線負責。',
  '3. **絕不寫入 `../fork260509-rev5/`**（含子庫與源倉）——rev5 是唯讀對照基準、硬禁令唯讀；讀取允許且**必要**。',
  '4. rust build／test **一律容器內、全程 serial**。正確命令形（quickstart 的簡寫形缺 `-f` 會報 invalid compose project）：',
  '   `docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo test --workspace -- --test-threads=1`',
  '5. rust 碼完工前 MUST 於容器內跑 `docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T rust-api cargo fmt --all`（rev5:ADR 0057）。',
  '6. 空間邊界：只准動允許清單內的檔；清單外需要動＝**絕不擅改**，依 status 分值升級。',
  '7. status 分值語意（★兩值反應相反）：`blocked`＝整件做不下去、主線須立刻接手；`done_with_escalation`＝交付已完成、只是有清單外待辦（附 escalations）。',
  '8. 凡改變某數字／集合／方向／名稱／單一權威，MUST `grep -rn` 枚舉全 repo 同語意命中、逐處回報。★**枚舉後逐處判別、不得用 `grep -v` 過濾整行**——同一行可能同時含該改與不該改的 token（rev5:L-076 實暴）。史述保留、現在式改對（rev5:L-032）。',
  '9. 提及前代（rev5／rev4／rev3）編號一律帶 `rev5:` 之類前綴（GT-05；承 rev5:Lint25、rev5:ADR 0012）。',
  '10. ★**實作先讀 rev5 對應碼**（唯讀）、高度參照但**重打字消化不拷貝**；註解**一律重寫**（rev5 出處帶 `rev5:` 前綴）；rev6 拍板差異點**不得帶回**（承 rev5:ADR 0019）。',
  '11. ★**TDD：先紅後綠**。每個可測面先寫會紅的測、跑到真的紅、再寫實作到綠。★分階段推進：每完成一階段就在容器內 serial 跑一次測試確認綠，再進下一階段——不要全部寫完才第一次編譯。',
].join('\n')

