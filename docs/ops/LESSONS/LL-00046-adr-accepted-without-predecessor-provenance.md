---
id: "LL-00046"
rule_id: "RL-0081"
promotion_surface: rules
---
LL-00046｜ADR-00039 accepted 時全文沒有任何 rev5 出處，而 ADR body 不可變，缺口永遠補不回來（004 刀；2026-09-29 以紀律收）

**徵狀**：004 刀 FR-067 要求「本刀 ADR 皆帶 rev5 provenance」，ADR-00039（IP 域 i18n 決定）卻全文零 rev5 出處；accepted 後 GT-04 不許改 body，只能在 BACKLOG 立對沖條長掛。

**成因**：前代出處只有 002～004 三刀的 spec 各自要求，沒有 repo 級紀律、也沒有機器腿；001 刀與 005 刀的 ADR 就不受這條約束（005 刀的 ADR-00048／ADR-00051 全文零 rev5）。

**處置**：2026-09-29 user 裁定訂 RL-0081（新 ADR 的 provenance 必帶 `rev5:`／`rev4:` 出處，無前代對應者寫「前代無對應：<理由>」；已 accepted 者不回改），GT-04 加腿只查 ADR-00052 起的新檔；ADR-00039 的缺口記為已知態（經 supersedes 鏈可上溯 ADR-00029 的 `rev5:Lint24`）。

**晉升面**：rules——RL-0081（承載＝lint、GT-04）。

**再犯面與守法**：寫新 ADR 先填 provenance 的前代出處；確實沒有前代對應就寫明理由，不留空。
