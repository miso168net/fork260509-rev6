---
id: "ADR-00002"
title: rev5 凍結面＝rev6 bootstrap 單腿斷言——不開 rev5 遠端分支保護、不補 rev5 NOTES 凍結宣告
date: 2026-09-03
status: accepted
supersedes: []
superseded_by: []
provenance: "user 拍板 2026-09-03（rev6 波 1 session 問答）；翻案對象＝啟動書 §6 Guard 欄與 D17 同句「rev5 remote 分支保護＋rev5 NOTES 凍結宣告＋rev6 bootstrap 斷言」三件套"
tags: [governance, freeze]
---

## 背景

啟動書 §6／D17 把 rev5 凍結設計為三件套。2026-09-03 波 1 首 session 實查：

1. **遠端分支保護**：rev5 三條長名分支皆未開。`fork260509-rev5`（rev5-admin-root）與
   `fork260509-soybean-admin-base`（rev5-admin-base-web）為 public repo、可開；
   `fork260509-rev2-anew-rust-api`（rev5-admin-rust-api）為 private repo，GitHub 免費方案回 403
   （需 Pro 或轉 public）、開不了。
2. **rev5 NOTES 凍結宣告**：`docs/ops/NOTES.md` 無此宣告，最後 commit 7eab28a（rev5:L-087）。
   補寫＝rev5 多一顆 commit、凍結 SHA 三處連動改、且須 push rev5 origin，與啟動書 §5
   「rev5 session 之後不再寫入」相牴。
3. **rev6 bootstrap 斷言**：已落地（`tools/bootstrap.sh` 3b 節）——rev5 三處 HEAD＝
   7eab28a／9833308／92919b9 為 die 級、已追蹤檔改動為 ⚠；負向自測（`RV6_REV5_ROOT` 指向
   HEAD≠凍結之 repo）rc=2。

## 決定

1. **不開任何 rev5 遠端分支保護**（三條皆不開；不因 rust-api 私有而轉 public）。
2. **不補 rev5 NOTES 凍結宣告**：rev5 樹零寫入，**7eab28a 即凍結點**。凍結宣告改由 rev6 側承載：
   本 ADR、`tools/bootstrap.sh` 的 `REV5_FROZEN`、CLAUDE.md §6 硬禁令、rev6 正式 README（波 1 末）一句。
3. 凍結面＝**rev6 bootstrap 斷言單腿＋人紀律**（CLAUDE.md §6「絕不寫入 `../fork260509-rev5/`」）。

## 後果

- 遠端側無機器阻擋誤 push 至 rev5 三條分支；偵測為**事後**（下次 bootstrap 體檢紅喊）、非事前。接受此殘餘。
- rev5 自身文件讀不到凍結字樣；查凍結一律看 rev6 側。
- 凍結 SHA 改值＝先 supersede 本 ADR、再改 `REV5_FROZEN`（bootstrap die 訊息已指向此流程）。
- 啟動書 §6／D17 三件套字面屬創世史料不回改；本 ADR 為翻案正式載體（承 rev5:ADR 0004 之史料紀律）。
- rev6 remote 仍待定（啟動書附錄 D）：user 同日決定延後到掃描防線（GT 閘／.githooks／betterleaks 釘版）就位；非本 ADR 射程。
