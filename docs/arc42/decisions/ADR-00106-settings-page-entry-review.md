---
id: "ADR-00106"
title: 系統設定頁進場複核——ADR-00079 觸發器（前端即時提示三對矛盾、不擋送出，決定 2 維持）、ADR-00054 觸發器不成立（界值由讀端下發 REGISTRY 宣告界、不另立真源）、ADR-00057 之宣告集外列呈現（唯讀、排組尾、標 description）、ADR-00064 封死集不下放、刻意分岔四項（跨鍵矛盾即時提示、密碼政策快取同分頁清除、數字框 10 鍵一律鉗界、宣告集外列唯讀）
date: 2026-10-21
status: proposed
supersedes: []
superseded_by: []
provenance: "008-audit-settings-pages 之 spec FR-026、FR-045～FR-050、FR-061⑧、US1、SC-009、Edge Cases「系統設定」、刻意分岔登記表（設定頁跨鍵矛盾、密碼政策快取、宣告集外設定列、數字框界值五鍵）、clarify Q1（10 鍵一律鉗界；user 2026-10-21）；brainstorm §0 D2、D3、主線工程判斷③④⑰㉔；ADR-00079 決定 2 與翻案觸發器、ADR-00054 翻案觸發器、ADR-00057、ADR-00064；draft 於 plan 期落、刻意分岔之畫面效果於本刀 CDP 三方對照單元實測後定稿；前代：rev5:B-160（前端手抄 `numberRanges` 五鍵）、rev5:008-audit-settings-pages 之設定頁形（四組、逐項即改即存）"
tags: [system-settings, frontend, known-state, by-design]
---

## 背景

- 設定頁進場觸及四支既有 ADR 之觸發器或射程：ADR-00079（密碼政策矛盾之前端提示或擋送出）、ADR-00054（界值唯一權威）、ADR-00057（宣告集外列讀得到、寫回 2222）、ADR-00064（封死集）。
- rev5 前端手抄五鍵界值（`rev5:B-160`）；另五鍵越界送後端拒（clarify Q1 查證）。
- 密碼政策 hook 只增不清（007 刀已知態）。

## 考慮過的替代案

1. **擋送出矛盾組合**——ADR-00079 決定 2 定後端逐鍵驗、不新增組合守門；擋送出須另立 ADR 翻案；否決（D2）。
2. **前端照 rev5 逐鍵鉗界**——回到手抄鍵集之老問題；否決（clarify Q1）。
3. **宣告集外列可編**——寫回必 `2222`；否決（工程判斷③）。

對所選方案跑同一反例（RL-0013）：「誤打越界值被靜默存成界值」→成功提示、框內數值與操作日誌舊→新三處可見；成立而接受（clarify Q1 代價、分岔表登記）。

## 決定

1. **ADR-00079 觸發器重評**：前端即時提示三對嚴格不等式矛盾（`password_min_length` ＞ `password_max_length`、`login_throttle_captcha_after` ＞ `login_throttle_max_fails`、`ip_captcha_after` ＞ `ip_max_fails`），警示落該組卡片並寫後果、不阻存；相等合法；ADR-00079 決定 2（後端逐鍵驗、不新增組合守門）維持、不 supersede。
2. **ADR-00054 觸發器不成立**：界值由讀端 wire 下發（`rangeMin`／`rangeMax`、取 REGISTRY）；前端不抄鍵集；10 個 number 鍵一律鉗界（越界失焦即改界值後送出）。
3. **ADR-00057 之呈現**：讀 wire 下發 `declared`；宣告集外列唯讀、排組尾、標示後端 description；寫回仍 `2222`（ADR-00057 不變）。
4. **ADR-00064 不下放**：設定兩端點續為封死集；選單維可見性可授（ADR-00103 款 10）。
5. **密碼政策快取**：寫入政策七鍵任一成功即清同分頁快取（hook 增清除函式）；其他分頁仍須重新整理（RUNBOOK §11.3 改設定頁首選）。
6. **刻意分岔**（對 rev5 HEAD；spec 刻意分岔表為單一出處）：跨鍵矛盾提示、政策快取清除、宣告集外列唯讀、數字框五鍵（`ip_captcha_after`、`ip_max_fails`、`ip_window_minutes`、`password_change_min_interval`、`session_idle_timeout`）由「送出被拒」改「鉗界存檔」。
7. **說明文案**：16 鍵 label＋help 三語全映射；帳號登入與 IP 源登入兩組不承諾嚴格上限（BL-00145 約束）。

## 後果

- 誤打越界值會存成界值（clarify Q1 代價）；可由操作日誌追溯。
- 四支既有 ADR 皆不 supersede（觸發器重評結論與呈現面住本 ADR）。

## 翻案觸發器

- 出現擋送出矛盾組合之需求 ⇒ 新 ADR 翻 ADR-00079 決定 2。
- REGISTRY 新增非 number 有界型 ⇒ 重評讀 wire 界值欄。
- 出現設定頁下放之需求 ⇒ 重評 ADR-00064 封死集。

## 親決分類

依 ADR-00089（RL-0086）；類別定義同 ADR-00099 本節。

| 款 | 類別 | 出處或理由 | 白話一句 |
|---|---|---|---|
| 決定 1 | 承決 | brainstorm D2、㉔；spec FR-047 | 三對設定互相矛盾時當場警示，但不擋存檔。 |
| 決定 2 | 承決 | brainstorm ③；clarify Q1；spec FR-026、FR-046 | 數字框的上下限由後端下發，十個數字鍵都會被拉回界內。 |
| 決定 3 | 承決 | brainstorm ③；spec FR-046 | 後端宣告以外的設定列只能看不能改。 |
| 決定 4 | 承決 | brainstorm ④；spec FR-002、FR-050 | 設定頁的讀寫不下放給其他角色。 |
| 決定 5 | 承決 | brainstorm D3；spec FR-048 | 改了密碼政策，同一分頁的密碼提示立即用新值。 |
| 決定 6 | 承決 | spec 刻意分岔登記表四列、clarify Q1 | 和舊版不同的地方逐項登記。 |
| 決定 7 | 承決 | brainstorm ⑰；spec FR-049 | 每個設定都有三語說明，節流說明不保證嚴格上限。 |

- **親決紀錄**：（plan 期）獨立核對（ADR-00089 決定 5；2026-10-21）：7 列中相符 6（決定 1～5、7）、改正 1（決定 6 與標題：標題稱三項、決定 6 列四項）；處置＝標題改四項；決定 6 之畫面效果於 CDP 單元實測後定稿；改過之款於轉 accepted 前依 ADR-00089 決定 6② 復核。
