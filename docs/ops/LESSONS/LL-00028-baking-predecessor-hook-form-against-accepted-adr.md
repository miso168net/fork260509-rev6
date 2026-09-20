---
id: "LL-00028"
rule_id: "RL-0065"
promotion_surface: none
---
LL-00028｜主線把前代的 hook 段形烤進單元 prompt，卻與 rev6 已 accepted 的 ADR 相違；implementer 照做、靠其升級項才現形

**徵狀**：004 刀 U8 單元定義寫「`view-render-guard` 之 hook 段以 `base-web/src` 在位與否具名跳過、沿 rev5 段形」。implementer 照裁定落地，同時於升級項指出：ADR-00019 決定 3「跳過邏輯住工具內、pre-commit 段零條件判斷」與決定 4「tracked 面缺席不類推環境缺席＝rc 2 fail-loud」、以及本刀 contracts「工作樹缺席即 fail-loud」皆與該段形相反。

**成因**：主線備單元時讀了前代 hook 該段、覺得理由充分就整段帶入裁定，沒有先查 rev6 對同一主題（碼面閘之環境缺席語意）是否已有拍板。前代該形在前代成立（創世期 worktree 可能未就位），rev6 則以 bootstrap 先行＋ADR-00019 明文收掉了這條分支。

**處置**：主線收尾時依 ADR-00019 改為零條件段，並同步工具檔頭、pre-commit 檔頭段序句、README 守門條目與 RUNBOOK 碼面閘表四處鏡像句。防法：單元定義之「主線裁定」段凡寫「沿 rev5 形」者，落筆前先以主題詞 grep `docs/arc42/decisions/`——rev6 已有 accepted ADR 涵蓋者以 ADR 為準、前代形只當參考；implementer 指出裁定與 ADR 相違的升級項，優先於其餘升級項處理。
