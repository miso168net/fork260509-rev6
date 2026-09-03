---
rad_ai: [E4]
rad_ai_map:
  Responsible AI Concern Matrix: 負責任 AI 關注矩陣
  Fairness: 公平
  Explainability: 可解釋
  Human Oversight: 人類監督
  Transparency: 透明
  Privacy: 隱私
  Safety: 安全
---
# P-E4 負責任代理（流程層）

本檔以 RAD-AI E4 的形制記載代理面的人類監督（拍板級判準、push／merge 同意閘、review 只讀）、透明（events 留痕）、隱私（機密掃描）；公平／可解釋／安全對 agent 面不適用者附理由；系統層對應＝`docs/arc42/08-crosscutting-concepts.md` §8.5。每個子節首句標明類比張力（哪裡對得上、哪裡是硬套）。

### 負責任 AI 關注矩陣

類比張力：對得上——六關注逐條判適用；三適用、三不適用附理由。

| 關注 | 適用 | 承載 | 守門 |
|---|---|---|---|
| 公平 | 不適用 | agent 產物不對人分類、無人群決策 | — |
| 可解釋 | 不適用（替代＝可追溯） | findings 帶 file×summary；收單訊息逐項處置 | 歸「透明」 |
| 人類監督 | 適用 | 憲法 §I.8：merge／push 當次同意、拍板級親決、review 只讀 | RL-0044／RL-0043 |
| 透明 | 適用 | events.jsonl 留痕、commit 尾 Co-Authored-By 與 Claude-Session、收單訊息列處置 | GT-02／GT-03 |
| 隱私 | 適用 | 機密不入 prompt／chat／tracked 檔；SECRETS_DIR＋age | GT-07；RL-0054 |
| 安全 | 不適用（歸人類監督） | 破壞性操作硬禁令（CLAUDE.md §6） | RL-0063／RL-0064 |

### 公平

類比張力：硬套——公平關注的是對人群的差別待遇；流程層 agent 的產物是碼與文件、不對人分類、不做影響個人的決策，不適用。

### 可解釋

類比張力：硬套——託管模型內部不可解釋；rev6 以「可追溯」替代：每筆 finding 帶 file×summary 與駁回理由（RL-0071）、每顆收單 commit 逐項列處置、每個拍板有 ADR——歸「透明」承載。

### 人類監督

類比張力：對得上——憲法 §I.8 原文即此：agent 產物必經人審與機器閘；人審＝merge 前 user 當次同意＋拍板級親決；review agent 只讀不寫；agent 不 push／merge／commit（RL-0063）。

### 透明

類比張力：對得上——事件源留痕（feature_close／misc／review／perf）、commit 訊息尾行標明 AI 共同作者與 session、收單訊息逐項列 final review 處置（RL-0073）。

### 隱私

類比張力：對得上——機密實值永不進 prompt、chat、tracked 檔（RL-0054、GT-07）；密文入版控、私鑰只在本機；rev5 對照樹唯讀（RL-0064）。

### 安全

類比張力：硬套——RAD-AI 的安全指人身與物理危害；流程層對應的是破壞性操作（刪卷、reset worktree、寫入 rev5 樹）的硬禁令，已由人類監督與 RL-0063／RL-0064 承載，不另列。
