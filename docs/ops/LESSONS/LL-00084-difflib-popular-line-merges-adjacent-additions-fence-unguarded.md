---
id: "LL-00084"
rule_id: "none：判準已晉升為碼面閘本體（tools/fork-delta-lint.py 之 find_unmarked_additions 分塊改 autojunk 關閉、self-test HJ0～HJ2；maint-backlog-142-146 U1），與各單元出口之 §1.5 逐塊暫拔斷言並守；與 LL-00058 同族，不另立規則"
promotion_surface: gate
recurrence_of: "LL-00058"
---
LL-00084｜熱門行不能當 difflib 的錨：在檔內高頻閉合行（如 `</NFormItem>`）與另一段新增之間插入新行，該行即被判為刪除再新增、兩段新增併成一個替換塊，拔掉圈界 lint 照綠——前代「下拉下方另起告知行」之形因而放不進（007 刀 U17）

**徵狀**：使用者編輯抽屜之角色欄，碼品質審查要求「候選讀取失敗」告知照前代形（下拉之下另起一行 12px 警示色字、下拉框不變色）。fix 實作兩形：下拉之後、本項閉合標籤之前插告知行；以直排容器包覆下拉（下拉隨之重縮排）。兩形 lint 皆綠，但 §1.5 逐塊暫拔時，告知段與其後既有之會話政策段拔 START／END 皆 rc 0——原本已證紅之會話政策段也一併失守。

**成因**：`tools/fork-delta-lint.py` 當時以 `difflib.unified_diff` 分塊，底層 SequenceMatcher 預設 autojunk：序列長 200 行以上時，出現次數超過 1%＋1 之行判為熱門行，不入比對索引，只能靠相鄰匹配延伸對上。`        </NFormItem>` 在該檔出現 11 次，屬熱門行；前後皆為新增行時無從延伸，即被判為「刪除＋新增」。兩段新增連同此行併成一個含被移除碼行的替換塊，`find_unmarked_additions` 依「含移除碼＝修改型」跳過不驗。重縮排形同理：被重縮排的行本身就是移除碼。

**處置**：U17 維持表單項回饋屬性形（告知落表單回饋列、下拉框轉警示色）。與前代之差屬字級、顏色、間距，依 spec SC-010 只記入走查紀錄、不擋收刀。角色欄修改型標記之理由句據實寫明偏離與成因；§1.5 全單元 27 發全紅。

**晉升面**：gate——分塊改用 `difflib.SequenceMatcher(None, a, b, autojunk=False)` 之 grouped opcodes，change-block 定義與其餘判準不動，全樹 check 改前改後摘要逐項相同；self-test 以 208 行合成基線（熱門閉合行出現 12 次、超過熱門門檻 3）之 HJ0～HJ2 守住：HJ0 自證樣本越過門檻，HJ1 兩段新增各帶成對圈界為綠，HJ2 拔其中一段之圈界須攔。判準住碼面閘本體、由 pre-commit fork-delta 段實跑（maint-backlog-142-146 U1）。

**再犯面與守法**：
- 新增段落點緊鄰高頻閉合行（`</NFormItem>`、`</template>`、`/>` 一類）時，熱門行併塊已由分塊關閉 autojunk 排除；與修改型落在同一變更塊之隔開要求仍依 LL-00058。定形前照跑 §1.5 逐塊暫拔。
- lint 綠只證「有標記」，不證「標記受守」；圈界是否受守，以 §1.5 逐塊暫拔之實得為準。
