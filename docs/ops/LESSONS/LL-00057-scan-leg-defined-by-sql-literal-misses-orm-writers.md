---
id: "LL-00057"
rule_id: "none：RL-0002（字面枚舉）之同理推廣到一切出現點名冊；本則守法寫進本檔與後續單元定義，不另立規則"
promotion_surface: none
---
LL-00057｜契約以單一 SQL 字面形定義「授權表寫入者」名冊，真寫者全為 ORM 形；主線接地句又把測試模組內的字面命中誤報為生產區（006 刀 U9）

**徵狀**：006 刀 U9 的腿⑥後半照 contracts/code-gates §3 表與 tasks T048，判準寫成「生產區 `INSERT INTO casbin_rule` 字面之檔集」；主線的單元定義另外烤入一句接地「現況生產區命中只在 `sys_casbin_policy.rs`」。implementer-2 實查發現兩件事：該字面命中落在 `sys_casbin_policy.rs` 的測試模組內（命中行在該檔 `#[cfg(test)]` 測試模組起始行之後）；兩支真寫者（授予 `apply_full_replace`、復原 `restore`）都是 ORM 形 `casbin_rule::ActiveModel{..}.insert`。照條文字面施作的話，生產面零命中，名冊不是恆紅就是空轉。implementer 把偵測形放寬為 ORM 形與 SQL 字面形的聯集，並以植入變異自證；主線收尾時同批改寫契約與 tasks 的措辭。

**成因**：①SDD 期定義掃描腿時只列了一種寫法（SQL 字面），沒有先枚舉「寫授權表」這個語意的全部語法形（ORM 之 ActiveModel insert、`Entity::insert`／`insert_many`、raw SQL）。②主線接地時 grep 字面得到單一命中，就寫成「生產區命中」，沒有比對命中行號與該檔 `#[cfg(test)]` 的邊界。

**處置**：偵測形放寬為 ORM 形與 SQL 字面形的聯集（SQL 形容空白、換行、續行反斜線、`public.` 前綴與雙引號）；名冊另加逐處釘（`restore`／`apply_full_replace` 各恰一處）；以「他檔生產區植入 ORM 寫入一處 → 紅」自證。契約 §3 表與 T048 改述為實際偵測形。

**晉升面**：none——判準住 rust lint 測試本身，守法寫進本檔與後續單元定義。

**再犯面與守法**：凡定義或接地「某語意的出現點名冊」（呼叫點、寫入者、字面）：①先列出該語意的全部語法形（ORM、SQL、巨集、別名匯入），逐形 grep，判準寫成各形的聯集；②每個命中先對照所在檔 `#[cfg(test)]`（或 `mod tests`）的起始行號，判定屬生產區還是測試區，之後才寫進契約或單元定義；③以「他檔生產區逐形植入一處 → 紅」的變異自證聯集完備。
