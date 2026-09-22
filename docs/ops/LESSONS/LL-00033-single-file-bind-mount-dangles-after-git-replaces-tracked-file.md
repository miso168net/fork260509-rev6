---
id: "LL-00033"
rule_id: "none：屬 Docker Desktop 單檔 bind mount 的環境層陷阱、非流程規則；守法＝RUNBOOK §2 固定起手句（pull 動到該檔即重建 rust-api 容器）＋本檔診斷捷徑，不另立規則"
promotion_surface: none
---
LL-00033｜tracked 單檔 bind mount（`deploy/trust-model.dev.toml`）在 pull 換 inode 後於容器內懸空——信任模型靜默退成零網段、一切來源視為直連；watchexec 重啟與 `restart` 皆不重掛

**徵狀**：005 前維護批期間連續三次 pull（各批各改 `deploy/trust-model.dev.toml` 一行註解）之後，rust-api 容器內讀 `/etc/rev6/trust-model.toml` 回 ENOENT；`ls -la /etc/rev6/` 仍列出該檔，但 **link count 為 0、size 為舊版**。boot 日誌：`WARN 信任模型載入告警 kind=Missing`（退扁平環境變數）→ `kind=NoTrustedNetwork`「六集合受信側合計零網段：一切來源視為直連」→ `信任模型載入完成 warnings:2 internal_default:0`。服務照常 healthy、登入 e2e 全過——**降級方向安全、零紅燈**，靠日常操作面看不出來；此態下 IP 存取閘與來源維節流拿到的「真實來源」恆為 front-nginx 的容器位址。

**成因**：compose 以單檔 bind mount 把 `deploy/trust-model.dev.toml` 掛到 `/etc/rev6/trust-model.toml`（004 刀 T006）。bind mount 綁的是掛載當下的 inode；git checkout／pull 寫檔＝unlink＋新建（新 inode），掛載點遂指向已 unlink 的舊 inode。本坑實證於 Docker Desktop（macOS）：其檔案共享層對該路徑直接回 ENOENT；Linux 原生 bind mount 的語意是舊 inode 仍可讀但內容為舊版——同樣分叉、只是徵狀換成「讀到舊值」。watchexec 只重啟行程、`docker compose restart` 亦不重掛（同 `deploy/secrets/README.md` 對 secrets 檔早已記載的口徑）。載入器對缺檔的處置完全照契約（`docs/ops/reference-src/trust-model-config.md`：路徑未設／檔案讀不到→沿用扁平退路、告警 `trust_model_missing`）——契約沒錯，錯的是 mount。`docker inspect` 的 Mounts 仍列著該 bind：**「有掛」≠「可讀」**。

**處置**：`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate --no-deps rust-api`（target 卷有產物、秒級）→ 容器內 link count 回 1、內容為現行版，boot 日誌 `warnings:0 internal_default:1`。守法句落 RUNBOOK §2。

**晉升面**：none（RUNBOOK §2 一句＋本檔）。

**再犯面與守法**：觸發條件＝任何讓 git 重寫 `deploy/trust-model.dev.toml` 的動作（pull／checkout／merge 帶該檔變動、**含純註解改動**），以及手動編輯該檔調信任網段——改完一律重建容器、不是 `restart`。徵狀不紅，唯一機器可見面＝boot 日誌那兩行 WARN 與 `internal_default:0`。診斷捷徑：**先看 mount、不看 toml**——`docker exec rev6-admin-rust-api-1 ls -la /etc/rev6/` 見 link count 0 即定案，不必去查 toml 內容或載入器邏輯。同家族：LL-00005（bind-mount 來源缺席→目錄佔位）、LL-00032（drvfs mtime→cargo 假綠）——三者共同點＝容器對 host 檔的視圖與 host 實況分叉、且全部以「綠」呈現。
