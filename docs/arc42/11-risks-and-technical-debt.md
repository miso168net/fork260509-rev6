---
section: 11
summary: 風險與技術債（指針 BACKLOG／LESSONS）；E7 AI 債務登記
rad_ai: [E7]
rad_ai_stage: 3
rev5_blueprint:
  §11 風險與技術債: 承襲（BACKLOG／LESSONS 指針；rev6 加 ※11.1 風險）
---
# §11 風險與技術債

## ※11.1 風險

（rev6 自訂子節、官方無）

| 風險 | 觸發 | 守門 |
|---|---|---|
| upstream rebase 衝突把 fork 改動抹掉 | soybean-admin `example` 分支大重構 | 憲法 §III 軌道制、`rev6-inline` 標記＝全 repo grep 即得 patch set；修改型帶 `原行:` |
| rev5 對照樹被誤寫 | 在 `../fork260509-rev5/` 下 commit 或改 stack 設定 | bootstrap 凍結 SHA 斷言（ADR-00002）；CLAUDE.md §6 硬禁令 |
| 子庫分支只在本機源倉、換機不可得 | 新機器 clone 外層 | `tools/bootstrap.sh` 重建源倉 clone 與 worktree（RUNBOOK §1） |
| 治理工具鏈超出預算 | docsync 邏輯行逼近上限、閘數增加 | STATE 預算對賬（D8）；GT-12 閘數 12 固定 |
| Day-1 豁免到期未解 | 首條 LL 落地時忘記解除鍵 | GT-08 解除謂詞（檔存在即到期紅）；名冊＝`docs/generated/GATES.md` |

## ※11.2 技術債

待辦住 [BACKLOG](../ops/BACKLOG.md)（兩卷）、教訓住 [LESSONS 索引](../ops/LESSONS.md)；本節只放結構性技術債的現況描述。

| 債 | 現況 | 去處 |
|---|---|---|
| Day-1 豁免（GT-12 到期即紅） | 目前零筆（GT-08.lessons-absent 隨 LL-00001 落地移除） | 新豁免逐筆具名帶解除謂詞、到期同 commit 自 `DAY1_EXEMPTIONS` 移除 |
| 編排範本的版本字面耦合 | 組裝成品 script（`EXAMPLE-<unit>.mjs`／單元 script）烤入 RULES-VERSION 字面，規則列一改即過期、hook 擋發射 | 改規則列時同批重烤（`python3 tools/docsync rules emit`） |

## ※11.3 E7 AI 債務登記

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E7 代理債務登記](../process/P-E7-agent-debt.md)。
