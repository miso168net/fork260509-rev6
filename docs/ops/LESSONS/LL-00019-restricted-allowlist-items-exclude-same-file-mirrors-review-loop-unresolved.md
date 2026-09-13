---
id: "LL-00019"
rule_id: "RL-0022"
promotion_surface: rules
---
LL-00019｜允許清單「只准」限定式項把同檔的枚舉鏡像句（數量詞／段序枚舉／檔頭名冊句）排除在外——fix 輪三處各漏一次、規格審查跑滿三輪後確認輪仍有 blocker＝unresolved 回主線，品質審查整段沒跑、得再開一支續跑形（10 支 agent）補完

**徵狀**：003 刀 U9（run `wf_3072b444-1c7`）規格審查 r1～r4 每輪抓到的 blocker 幾乎全是同一型——本單元自己落地的改動（msg-key-gate 段、ROUTES 12→16、common helper 改形）在**同檔**留下的舊數量詞或枚舉句沒跟著改（contract.rs「現十二 case」、pre-commit 檔頭段序與「三支碼面閘」標題、README 守門鏈與樹列、bootstrap「三支碼面閘」、test_hook_wiring「七條件段」、common 檔頭「兩形」）。fix-1／fix-2 依 RL-0022「限定式項之限定外改動＝清單外」把這些句子升級主線、零改動；fix-3 依 RL-0011 種子③④「允許清單內自改」自行改了三處並自陳「若主線判超權可 revert」——同一份 prompt、三支 fix agent 兩種讀法。確認輪（r4）仍剩 3 條同型 blocker，骨架判 unresolved、直接 return，碼品質審查未跑；主線修完後以 IMPLEMENTERS=0 續跑形另開 `wf_b7d80ece-0d5`（10 支）才把品質審查跑完。代價＝一支 run、約 2M tokens、3.6 小時。

**成因**：允許清單的「只准」項是按 task 條文寫的改動面（「只准新段＋for 名冊」「只准樹加一行」「只准 `run_tool_test` 一列」），寫清單時無法預先枚舉 RL-0011 sweep 會命中的同檔鏡像句；RL-0022 的「限定外＝清單外」與 RL-0011 的「允許清單內自改」對這類句子沒有明說誰上位，保守的 fix agent 選擇升級。審查員每輪只掃到被上一輪改動新曝露的鏡像（改了 A 句才看見 B 句矛盾），三輪剛好用完。

**處置**：主線修三處 blocker＋全部升級項後，以續跑形（`IMPLEMENTERS=0`、`IMPL_STAGES=[]`、前 run 五份 report 原文轉存 tmp、CONTEXT 烤「續跑態」段）跑完規格確認→品質審查→fix；BL-00055 記三處人寫鏡像無機器守。

**再犯面與守法**：①RL-0022 增句——限定式項之射程恆含同檔 RL-0011 種子③④鏡像句（數量詞／段序或成員枚舉／檔頭名冊句），fix 得改、report 指名檔:行與新句、不算限定外；②主線寫允許清單時，每個「只准」項後附「＋同檔鏡像句」四字，並在發射前對每個限定式檔 `grep -n` 一次數量詞與枚舉句、把已知鏡像直接寫進清單；③unresolved 回主線＝標準接法為 IMPLEMENTERS=0 續跑形（新 runId、前 run report 轉存 tmp），不是 resumeFromRunId（cache 會把確認輪 blocker 原樣回放）。
