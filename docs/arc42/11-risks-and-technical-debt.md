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
| 起服務那一行退成不帶傳輸層對端的形，真實來源靜默退回請求端填得了的標頭 | 整理 `rust-api/server/src/main.rs` 啟動段時把 `into_make_service_with_connect_info` 換掉（照樣編譯、照樣 200、`oneshot` 測試照綠） | `rust-api/server/tests/serve_connect_info_lint.rs`；執行期訊號＝`ip_domain_degraded_total{source="request_context_absent"}`＋結構化 warn（告警規則＝`deploy/grafana-provisioning/alerting/rules.yml`） |
| 多行程或多實例部署下授權殘留繼承 | 以多個 rust-api 行程或實例服務同一庫（水平擴展、藍綠並行）：移除面寫端只換上本行程之 casbin 判定面，其餘行程持舊政策集直到各自重啟 | 零機器守（部署約束）：判定面同步之前提＝單一 rust-api 行程（ADR-00043 決定 9、憲法 §I.7 島 G1）；部署前核對＝RUNBOOK §16.4；多行程部署即翻案觸發（補跨行程同步通知） |
| CDN 邊緣網段表兩處各存一份而失同步 | 供應商公告變更後只改 `deploy/nginx/nginx.conf` 之 `geo $cf_edge`、或只改信任模型 `[[cdn]]` 其一 | 零機器守（文件約束）：同批更新程序與只改一邊的兩向表徵＝RUNBOOK §16；來源還原的正確性不倚賴它（位置錨須傳輸層背書＝憲法 §I.7 島 F 之 F6、已入碼） |

## ※11.2 技術債

待辦住 [BACKLOG](../ops/BACKLOG.md)（兩卷）、教訓住 [LESSONS 索引](../ops/LESSONS.md)；本節只放結構性技術債的現況描述。

| 債 | 現況 | 去處 |
|---|---|---|
| Day-1 豁免（GT-12 到期即紅） | 目前零筆（GT-08.lessons-absent 隨 LL-00001 落地移除；面缺席型 SKIP 已於 000-r2 全數改 ERROR） | 新豁免逐筆具名帶解除謂詞、到期同 commit 自 `DAY1_EXEMPTIONS` 移除 |
| 環境型具名跳過（不到期、rc 0） | 筆數與名冊不在本檔鏡像、以 `docs/generated/GATES.md`「環境型跳過登記」表現讀（ADR-00019 語意；觸發＝唯讀看碼模式、子庫不在工作樹或新機未佈機密） | 登記＝`tools/docsync/gates.py` 之 `ENV_SKIPS`；渲染面＝`docs/generated/GATES.md`「環境型跳過登記」表；GT-12 腿斷言原始碼 SKIP 鍵集 ⊆ 兩登記聯集 |
| 編排範本的版本字面耦合 | 組裝成品 script（`EXAMPLE-<unit>.mjs`／單元 script）烤入 RULES-VERSION 字面，規則列一改即過期、hook 擋發射 | 改規則列時同批重烤（`python3 tools/docsync rules emit`） |
| redis 不開 AOF（by-design 已知態） | `docker-compose.yml` 之 redis 持久化旗標只有 `--dir /data`、無 `--appendonly`＝RDB 預設快照；redis 重啟時距上次快照的 `session:*`／`throttle:*` 鍵可能遺失。暴險受憲法 §I.7 島 C 封頂：`sys_token.status` 為權威、denylist 只是加速層（丟 denylist 的被撤會話至多在 ≤access_secs 內未被即時攔截、換發時仍由 status 靜默 8888）；節流判定面不依賴 redis（每次嘗試由 PG 滑動窗定案＝ADR-00038）——丟解鎖標記至多少解鎖一次、可再解鎖自癒；丟 grace 的並發換發落 reuse 撤家族（fail-secure、重登復原）；丟 idle-emitted 至多多落一列 idle 事件 | 拍板＝憲法 §I.7 島 C（fail-* 方向）＋ADR-00046 款 5（重評維持不開、附翻案觸發器）；持久化開關的家＝compose redis service、屬部署域 |
| 快速登入鈕暴露 dev seed 帳密（auth 域 by-design 已知態） | 登入頁三顆快速登入鈕與表單預填密碼＝upstream `example` 基線既有、003 刀零 inline、與 rev5 UI 對照零差異、US1 驗收即靠它一鍵切三帳號 | 拍板＝ADR-00030（保留＋記帳）；帳＝滯後卷 BL-00049（觸發＝RUNBOOK §16 prod 硬化拍板成立時） |
| nginx 邊緣 `auth_limit` 先於後端節流（auth 域 by-design 已知態） | `deploy/nginx/nginx.conf` `limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;`＋`conf.d/_locations.inc` 四支 exact-match location（`/api/auth/login`／`loginCaptcha`／`refreshToken`／`logout`）`burst=40 nodelay`＝per-IP 粗閘、429 落在應用層之前（走查勿秒內狂打、RUNBOOK §9c）；後端節流＝帳號維＋來源維兩維（§6.1 島 E 情境），來源維的位址輸入＝信任錨結論（§6.1 島 F 情境）；邊緣桶以 nginx 所見傳輸層對端（`$binary_remote_addr`）為鍵、不經信任錨，兩層各自獨立計量 | 邊緣桶參數的家＝該 conf 註解；後端兩維門檻的家＝`system_settings` 兩組三鍵（退路常數住 `rust-api/server/src/throttle/mod.rs`） |
| IP 域 by-design 已知態（七款＝ADR-00046） | 管理員解鎖為 API-only、無 UI 按鈕／dev 經反向代理端到端可達來源信心三態＝`fallback` 與 `proxy_clean`（信任模型決定）＋`chain_rejected`（轉發鏈逾上界之判準不依賴信任模型；登入端點拒絕並落一列稽核），其餘五態由整合測試直餵信任模型覆蓋／操作稽核覆蓋不對稱（`sys_operation_log` 的寫入者＝IP 規則四寫端＋解鎖＋角色寫端〔新增／更新／刪除／批刪／首頁寫入〕＋選單寫端〔新增／更新／刪除／批刪／復原〕，系統設定寫端不落列）／logout 於 DB 故障窗對簽章有效的票回 5000、對垃圾票回 0000＝弱 oracle（won't-fix）／redis 不開持久化（上列）／wire 裁判面不開嚴格模式（快照零 `additionalProperties`，由裁判案以表驅動之「序列化鍵集＝快照 properties 鍵集」斷言涵蓋全部受審讀型〔含分頁信封；交叉型佔位 `Api.Route.MenuRoute` 一型具名豁免附理由〕承擔）／清單端點未知規則類型照原樣上 wire、前端退顯原字串 | 論證與各款翻案觸發器的單一出處＝ADR-00046（續行並 supersede ADR-00040）；其中解鎖按鈕與全域 wire 守衛兩款的後續工作帳住 BACKLOG |
| 角色與選單管理 by-design 已知態（八款＝ADR-00045） | 角色頁「菜單權限」彈窗取真選單樹而首頁現值與勾選為寫死值、兩顆授權彈窗送出皆假成功零寫入（「按鈕權限」全為假資料）／policy-archive 側欄項為死項（點擊不跳轉、直打網址 404）／新建或復原之選單側欄不現（含 `R_SUPER`；新建零授權、復原不回灌）／新增或復原之按鈕碼無人持有（含 `R_SUPER`；射程＝不屬治理域其餘選單之碼——與其餘選單共持且已授予之碼照舊有人持有，例：新選單沿用 seed 之 `B_CODE1`）／新建選單於治理清單顯原始 i18n 鍵字面／治理清單三列（system-settings／policy-archive／audit）顯路由裸鍵／getAllRoles 之既有 UI 消費者＝upstream 使用者頁新增抽屜（提交仍假成功）、roleHome 兩端點零 UI 消費者／治理清單分頁列凍結＋無 `size` 全取 | 各款「觀察路徑→症狀」與翻案觸發器的單一出處＝ADR-00045；款 2／款 6 之後續工作帳＝BL-00045；其餘款之解除點＝各款翻案觸發器（授權治理、使用者域與各頁進場） |

## ※11.3 E7 AI 債務登記

目前無 AI 元件（截至 2026-09-03）；本層隨 AI 功能刀填入。流程層＝[P-E7 代理債務登記](../process/P-E7-agent-debt.md)。
