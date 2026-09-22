---
id: "LL-00005"
rule_id: "none：環境層一次性坑（drvfs＋Docker Desktop bind-mount 的目錄佔位快取）、非流程規則可承；解法記於本檔與 RUNBOOK §1 步驟 4 徵狀句即可"
promotion_surface: none
---
LL-00005｜bind-mount 來源檔缺席時 compose 代建目錄佔位，補上真檔後舊容器仍掛目錄形——`up -d --wait` 報 mount source path 已存在

**徵狀**：002 刀 U1 T020 首次 `docker compose … up -d --wait` 七件，front-nginx `Exited (1)`：`nginx: [emerg] cannot load certificate "/etc/nginx/certs/fullchain.pem": PEM_read_bio_X509_AUX() failed … no start line`。查 `deploy/dev-certs/` 只有 `.gitkeep`，而 `fullchain.pem`／`privkey.pem` 兩個「檔」是 Docker 為缺席的 bind-mount 來源代建的**空目錄**。依 RUNBOOK §1 步驟 4 跑 `bash deploy/generate-dev-cert.sh` 產出憑證後再 `up`，front-nginx 仍起不來：`error while creating mount source path … file exists`——舊容器持有目錄形 mount 的快取，來源由目錄變成檔案後 Docker 拒絕重掛。

**成因**：compose 對缺席的 bind-mount 來源（`./deploy/dev-certs/fullchain.pem:/etc/nginx/certs/fullchain.pem:ro`）預設代建目錄佔位；容器物件建立時記住了「來源是目錄」，之後來源被真檔取代，同一容器再起會撞型別衝突。drvfs（/mnt/d）下該佔位目錄還需要 host 側刪除。新機 bootstrap 未跑 RUNBOOK §1 步驟 4 即 `up` 全七件，就會走進這條路。

**處置**：①刪掉代建的空目錄佔位（`rmdir deploy/dev-certs/fullchain.pem deploy/dev-certs/privkey.pem`）②`bash deploy/generate-dev-cert.sh`（self-signed、gitignored）③`docker compose … rm -sf front-nginx` 丟棄持舊 mount 的容器物件 ④再 `up -d --wait`＝七件 healthy。U1 fix 輪照此做完、front-nginx 轉 healthy。

**晉升面**：none——環境層一次性坑；RUNBOOK §1 步驟 4 已明寫「dev TLS 憑證」是前置、本檔補「跑漏了會長什麼樣、怎麼解」的徵狀鏈。

**再犯面與守法**：新機或清過 `deploy/dev-certs/` 之後首次 `up` 全七件都會踩到。守法＝先 `ls deploy/dev-certs/` 看有無真檔再 `up`；看到 `file exists` 的 mount 錯誤，直接 `rm -sf` 該服務容器再 `up`，不要去改 compose。只起 postgres／redis／base-web 三件（如 002 刀 T002）不會觸發，因為 front-nginx 不在其中。
