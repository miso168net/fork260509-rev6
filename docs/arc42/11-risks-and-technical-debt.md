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
| Day-1 豁免（GT-12 到期即紅） | 目前零筆（GT-08.lessons-absent 隨 LL-00001 落地移除；面缺席型 SKIP 已於 000-r2 全數改 ERROR） | 新豁免逐筆具名帶解除謂詞、到期同 commit 自 `DAY1_EXEMPTIONS` 移除 |
| 環境型具名跳過（不到期、rc 0） | 3 筆：`GT-02`／`GT-05` submodule-absent、`GT-07` secrets-absent（ADR-00019 語意；觸發＝唯讀看碼模式或新機未佈機密） | 登記＝`tools/docsync/gates.py` 之 `ENV_SKIPS`；渲染面＝`docs/generated/GATES.md`「環境型跳過登記」表；GT-12 腿斷言原始碼 SKIP 鍵集 ⊆ 兩登記聯集 |
| 編排範本的版本字面耦合 | 組裝成品 script（`EXAMPLE-<unit>.mjs`／單元 script）烤入 RULES-VERSION 字面，規則列一改即過期、hook 擋發射 | 改規則列時同批重烤（`python3 tools/docsync rules emit`） |
| redis 不開 AOF（auth 域 by-design 已知態） | `docker-compose.yml` 之 redis 持久化旗標只有 `--dir /data`、無 `--appendonly`＝RDB 預設快照；redis 重啟時距上次快照的 `session:*`／`throttle:*` 鍵可能遺失。暴險受憲法 §I.7 島 C 封頂：`sys_token.status` 為權威、denylist 只是加速層（丟 denylist 的被撤會話至多在 ≤access_secs 內未被即時攔截、換發時仍由 status 靜默 8888）；丟 L1 lock 由 L2 PG 滑動窗逐請求重判；丟 grace 的並發換發落 reuse 撤家族（fail-secure、重登復原）；丟 idle-emitted 至多多落一列 idle 事件 | 拍板＝憲法 §I.7 島 C（fail-* 方向）；持久化開關的家＝compose redis service、屬部署域、003 刀不動 |
| 快速登入鈕暴露 dev seed 帳密（auth 域 by-design 已知態） | 登入頁三顆快速登入鈕與表單預填密碼＝upstream `example` 基線既有、003 刀零 inline、與 rev5 UI 對照零差異、US1 驗收即靠它一鍵切三帳號 | 拍板＝ADR-00030（保留＋記帳）；帳＝滯後卷 BL-00049（觸發＝RUNBOOK §16 prod 硬化拍板成立時） |
| nginx 邊緣 `auth_limit` 先於後端節流（auth 域 by-design 已知態） | `deploy/nginx/nginx.conf` `limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;`＋`conf.d/_locations.inc` 四支 exact-match location（`/api/auth/login`／`loginCaptcha`／`refreshToken`／`logout`）`burst=40 nodelay`＝per-IP 粗閘、429 落在應用層之前（走查勿秒內狂打、RUNBOOK §9c）；後端節流只有帳號維，來源維與信任錨還原不在本 crate | 去處＝004 ip-trust-anchor 域（憲法 §I.7 島 F 承襲指針）；邊緣桶參數的家＝該 conf 註解 |

## ※11.3 E7 AI 債務登記

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E7 代理債務登記](../process/P-E7-agent-debt.md)。
