#!/usr/bin/env bash
# tools/bootstrap.sh — rev6 workspace 新機器重建／舊機體檢（幂等、fail-loud；承 rev5 形、啟動書 D17）
#
# 用途：clone 外層 repo 後一鍵補齊 gitignored 源倉（fork260509-*）＋雙 worktree，並斷言
#       ①base-web 基線＝源倉 example @ 8be6f9ba（D14：沿用 rev5 基線 SHA、不前進 upstream）
#       ②rust-api 源倉 main @ 32c5254（D17 分支點；分歧只警告）
#       ③rev5 對照樹三處 HEAD＝凍結 SHA（D17 凍結三件套之 bootstrap 腿；rev5＝唯讀對照基準）
#       ④pin 一致性；舊機重跑＝純體檢。斷言失敗→exit 2＋指名處置；分歧類只警告（⚠）不自動 reset、絕不半套。
# 掃描防線（.githooks／betterleaks 釘版／兩 worktree hooksPath＋指紋斷言）與治理 lint（tools/docsync test／check／lint＋閘數斷言）已回填（波 1）。
# 不含：機密實值（僅體檢 SECRETS_DIR 下缺檔；重建走 deploy/secrets/README.md 的產鑰→生成→加密流程）。
# 測試掛點：RV6_BASEWEB_SRC_URL／RV6_RUSTAPI_SRC_URL 覆寫 clone 來源（file:// 亦可）；
#       RV6_REV5_ROOT 覆寫 rev5 對照樹路徑（負向自測：指向 HEAD≠凍結 SHA 的 repo 必須 exit 2）。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
BASEWEB_SRC="$ROOT/fork260509-soybean-admin-base"
RUSTAPI_SRC="$ROOT/fork260509-rev2-anew-rust-api"
BASEWEB_URL="${RV6_BASEWEB_SRC_URL:-https://github.com/miso168net/fork260509-soybean-admin-base.git}"
RUSTAPI_URL="${RV6_RUSTAPI_SRC_URL:-https://github.com/miso168net/fork260509-rev2-anew-rust-api.git}"
UPSTREAM_URL="https://github.com/soybeanjs/soybean-admin.git"
DEFAULT_BRANCH="rev6-admin-root"
BASELINE_BRANCH="example";  BASEWEB_BASE_SHA="8be6f9ba"   # D14
RUSTAPI_BASE_BRANCH="main"; RUSTAPI_BASE_SHA="32c5254"    # D17
BASEWEB_BR="rev6-admin-base-web"; RUSTAPI_BR="rev6-admin-rust-api"
REV5_ROOT="${RV6_REV5_ROOT:-$ROOT/../fork260509-rev5}"
# rev5 凍結 SHA（README-rev6-handoff／啟動書 D17；改值＝先立 ADR）
REV5_FROZEN=".:7eab28a base-web:9833308 rust-api:92919b9"
WARNS=0

ok()   { echo "[bootstrap] ✓ $*"; }
warn() { echo "[bootstrap] ⚠ $*"; WARNS=$((WARNS + 1)); }
die()  { echo "[bootstrap] ✗ $*" >&2; exit 2; }
is_ancestor_or_same() { # $1=repo $2=short-sha 期望 $3=HEAD；期望 SHA 必須解析且＝HEAD
  local want; want="$(git -C "$1" rev-parse --verify -q "$2^{commit}" 2>/dev/null || echo '')"
  [ -n "$want" ] && [ "$want" = "$3" ]
}

# ── 0. 外層 repo 身分斷言 ─────────────────────────────────────────────
git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "$ROOT 不是 git repo"
git -C "$ROOT" show-ref --verify -q "refs/heads/$DEFAULT_BRANCH" \
  || die "外層無 $DEFAULT_BRANCH 分支——請在 rev6 傘狀 repo 根下跑（README-rev6-handoff 波 1 第 1 點）"
origin_url="$(git -C "$ROOT" remote get-url origin 2>/dev/null || echo '')"
case "$origin_url" in
  "") warn "外層 origin 未設（rev6 remote 待定、啟動書附錄 D）——身分以 $DEFAULT_BRANCH 分支存在為準" ;;
  *fork260509-rev6*) ok "外層 repo 身分（origin＝${origin_url}）" ;;
  *) die "外層 origin（${origin_url}）不含 fork260509-rev6——請在 rev6 傘狀 repo 根下跑" ;;
esac

# ── 1. 掃描防線（承 rev5 形：hooksPath＋betterleaks 釘版＋hooks 指紋斷言；★die 級）──────────
[ -d "$ROOT/.githooks" ] || die ".githooks 缺席——掃描防線標的不存在；git checkout -- .githooks 還原並追查來源"
git -C "$ROOT" config core.hooksPath .githooks
[ "$(git -C "$ROOT" config core.hooksPath)" = ".githooks" ] || die "外層 core.hooksPath 讀值異常——自癒：git config core.hooksPath .githooks"
ok "core.hooksPath=.githooks"
# 掃描器斷言（★die 級——缺席時 hook 會以 exit 127 擋掉每次 commit 且訊息難解，體檢須先 fail-loud；
# 釘版值＝rev5 釘定沿用、升版先立 ADR 再改此值）
BETTERLEAKS_VER="1.7.3"
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)  BL_ASSET="linux_x64";  BL_SUMCMD="sha256sum -c checksums.txt --ignore-missing" ;;
  Darwin-arm64)  BL_ASSET="darwin_arm64"; BL_SUMCMD="shasum -a 256 -c checksums.txt --ignore-missing" ;;
  *) die "未支援平台 $(uname -s)-$(uname -m)——請對照官方 release 資產名補 case 分支" ;;
esac
BETTERLEAKS_GET="處置：下載 https://github.com/betterleaks/betterleaks/releases/download/v${BETTERLEAKS_VER}/betterleaks_${BETTERLEAKS_VER}_${BL_ASSET}.tar.gz 與同頁 checksums.txt → ${BL_SUMCMD} 驗證 → 解壓 betterleaks 至 ~/.local/bin"
command -v betterleaks >/dev/null 2>&1 || die "betterleaks 缺席（掃描防線之樣式層）——${BETTERLEAKS_GET}"
bl_ver="$(betterleaks version 2>/dev/null || true)"
[ "$bl_ver" = "$BETTERLEAKS_VER" ] || die "betterleaks 版本（${bl_ver:-讀不到}）≠ 釘定 ${BETTERLEAKS_VER}——${BETTERLEAKS_GET}"
ok "betterleaks ${BETTERLEAKS_VER} 就緒（釘版斷言過）"
# hooks 標的檔內容指紋斷言（承 rev5、rev4:B-124：simple-git-hooks 類若覆寫標的檔、hooksPath 指標值不變仍印 ok＝防線靜默失效）。
# 法＝逐檔 git hash-object 對 git rev-parse HEAD:路徑 比對——逐 byte 級 blob 指紋、失敗逐檔指名；缺檔獨立分支指名。
for hf in .githooks/pre-commit .githooks/pre-push .githooks/lib/scan-range.sh .githooks-submodule/pre-commit .githooks-submodule/pre-push; do
  [ -f "$ROOT/$hf" ] || die "$hf 缺檔——hooks 防線標的不存在；疑遭覆寫／誤刪：git checkout -- $hf 還原並追查來源"
  head_blob="$(git -C "$ROOT" rev-parse "HEAD:$hf" 2>/dev/null || echo '')"
  [ -n "$head_blob" ] || die "$hf 不在外層 HEAD——hooks 標的無版控基準；確認內容後 commit 該檔再重跑"
  wt_blob="$(git -C "$ROOT" hash-object "$hf")"
  [ "$wt_blob" = "$head_blob" ] || die "$hf 工作樹內容 ≠ HEAD 版本——a) 非本人改動＝疑遭覆寫：git diff HEAD -- $hf 查看、確認後 git checkout -- $hf 還原並追查覆寫源；b) 本人正在改 hooks（未 commit）：commit 後重跑即綠"
done
ok "hooks 標的檔內容＝HEAD 版本（五檔指紋一致）"

# ── 2. 源倉（缺才 clone、幂等）────────────────────────────────────────
ensure_src() { # $1=目錄 $2=URL $3=名
  if [ -d "$1/.git" ]; then
    ok "$3 源倉已存在"
  else
    echo "[bootstrap] … clone $3 源倉（$2）"
    git clone "$2" "$1" || die "$3 源倉 clone 失敗（$2）"
    ok "$3 源倉 clone 完成"
  fi
}
ensure_src "$BASEWEB_SRC" "$BASEWEB_URL" "base-web"
ensure_src "$RUSTAPI_SRC" "$RUSTAPI_URL" "rust-api"

# base-web 源倉＝最原始源基線：切 example 且 HEAD＝D14 基線 SHA（不前進 upstream）；upstream remote＋no_push
cur="$(git -C "$BASEWEB_SRC" branch --show-current || echo '')"
if [ "$cur" != "$BASELINE_BRANCH" ]; then
  [ -z "$(git -C "$BASEWEB_SRC" status --porcelain)" ] \
    || die "最原始源不在 $BASELINE_BRANCH 且工作區不淨（現：${cur:-detached}）——手動處理後重跑"
  git -C "$BASEWEB_SRC" checkout "$BASELINE_BRANCH" \
    || die "最原始源 checkout $BASELINE_BRANCH 失敗（origin/$BASELINE_BRANCH 不存在？）"
fi
bw_head="$(git -C "$BASEWEB_SRC" rev-parse HEAD)"
is_ancestor_or_same "$BASEWEB_SRC" "$BASEWEB_BASE_SHA" "$bw_head" \
  || die "base-web 源倉 $BASELINE_BRANCH HEAD（${bw_head:0:7}）≠ D14 基線 ${BASEWEB_BASE_SHA}——rev6 沿用 rev5 基線、不前進 upstream；要前進須先立 ADR 再改本值；回退：git -C $BASEWEB_SRC checkout -B $BASELINE_BRANCH $BASEWEB_BASE_SHA"
ok "最原始源基線＝${BASELINE_BRANCH}@${BASEWEB_BASE_SHA}（D14）"
if ! git -C "$BASEWEB_SRC" remote get-url upstream >/dev/null 2>&1; then
  git -C "$BASEWEB_SRC" remote add upstream "$UPSTREAM_URL"
fi
git -C "$BASEWEB_SRC" remote set-url --push upstream no_push
ok "upstream remote 就緒（push=no_push）"
ra_head="$(git -C "$RUSTAPI_SRC" rev-parse "$RUSTAPI_BASE_BRANCH" 2>/dev/null || echo '')"
if [ -n "$ra_head" ] && is_ancestor_or_same "$RUSTAPI_SRC" "$RUSTAPI_BASE_SHA" "$ra_head"; then
  ok "rust-api 源倉 ${RUSTAPI_BASE_BRANCH}＝分支點 ${RUSTAPI_BASE_SHA}（D17）"
else
  warn "rust-api 源倉 ${RUSTAPI_BASE_BRANCH}（${ra_head:0:7}）≠ D17 分支點 ${RUSTAPI_BASE_SHA}——worktree 分支不受影響；main 若有意前進請立 ADR"
fi

# ── 3. worktree（缺才掛、斷裂指名；本機分支＞origin 長名分支＞自分支點 SHA 新建）──
ensure_worktree() { # $1=源倉 $2=目錄名 $3=分支 $4=分支點 SHA
  local src="$1" tgt="$ROOT/$2" br="$3" base="$4"
  if [ -f "$tgt/.git" ]; then
    local gitdir; gitdir="$(sed -n 's/^gitdir: //p' "$tgt/.git")"
    [ -d "$gitdir" ] || die "$2 worktree 斷裂（gitdir 不存在）——處置：git -C $src worktree prune、備份移除 $2/ 後重跑"
    ok "$2 worktree 就緒（$(git -C "$tgt" rev-parse --short HEAD) [$(git -C "$tgt" branch --show-current)]）"
    return
  fi
  [ -d "$tgt/.git" ] && die "$2/.git 是目錄＝submodule 模式（唯讀捷徑、不可開發）——要開發：確認無未收改動後移除 $2/、重跑本腳本"
  if [ -d "$tgt" ]; then
    rmdir "$tgt" 2>/dev/null || die "$2/ 非空且非 worktree——手動檢視後重跑"
  fi
  [ "$(git -C "$src" branch --show-current || true)" = "$br" ] && git -C "$src" checkout --detach
  if git -C "$src" show-ref --verify -q "refs/heads/$br"; then
    git -C "$src" worktree add "$tgt" "$br"
  elif git -C "$src" show-ref --verify -q "refs/remotes/origin/$br"; then
    git -C "$src" worktree add --track -b "$br" "$tgt" "origin/$br" || die "$2 worktree 掛載失敗（origin/${br}）"
  else
    git -C "$src" worktree add -b "$br" "$tgt" "$base" || die "$2 worktree 自分支點 $base 新建失敗"
  fi
  ok "$2 worktree 掛載（${br}）"
}
ensure_worktree "$BASEWEB_SRC" "base-web" "$BASEWEB_BR" "$BASEWEB_BASE_SHA"
ensure_worktree "$RUSTAPI_SRC" "rust-api" "$RUSTAPI_BR" "$RUSTAPI_BASE_SHA"
# 兩 worktree hooksPath 佈署＋讀值斷言（承 rev5；per-machine git config、源倉工作樹零改動）：★絕對路徑指向外層
# .githooks-submodule（相對路徑會相對於源倉根、必錯）；冪等；他機 clone 未跑 bootstrap＝源倉無防線，由本斷言暴露。
for wt in base-web rust-api; do
  git -C "$ROOT/$wt" config core.hooksPath "$ROOT/.githooks-submodule"
  hp="$(git -C "$ROOT/$wt" config core.hooksPath || echo '')"
  [ "$hp" = "$ROOT/.githooks-submodule" ] || die "$wt core.hooksPath 讀值（${hp:-未設}）≠ 預期——自癒：git -C $ROOT/$wt config core.hooksPath $ROOT/.githooks-submodule"
done
ok "兩 worktree core.hooksPath＝外層 .githooks-submodule（樣式掃描防線就位）"

# ── 3b. rev5 凍結斷言（D17 凍結三件套之 bootstrap 腿；rev5 三處 HEAD＝凍結 SHA、工作樹不得有已追蹤改動）──
if [ -d "$REV5_ROOT/.git" ]; then
  for pair in $REV5_FROZEN; do
    sub="${pair%%:*}"; sha="${pair##*:}"; dir="$REV5_ROOT/$sub"
    [ -e "$dir/.git" ] || die "rev5 對照樹缺 ${sub}（${dir}）——凍結面不完整；rev5 為唯讀對照基準（D17）"
    head="$(git -C "$dir" rev-parse HEAD)"
    [ "${head:0:7}" = "$sha" ] \
      || die "rev5 凍結破壞：$sub HEAD（${head:0:7}）≠ 凍結 ${sha}——rev5 自 2026-09-03 起唯讀（D17）；若確為有意變更，先於啟動書／README-rev6-handoff 改凍結值並立 ADR，再改本檔 REV5_FROZEN"
  done
  ok "rev5 凍結 SHA 斷言過（外層 7eab28a／base-web 9833308／rust-api 92919b9）"
  dirty="$(git -C "$REV5_ROOT" status --porcelain --untracked-files=no 2>/dev/null || true)"
  [ -z "$dirty" ] && ok "rev5 對照樹已追蹤檔零改動" \
    || warn "rev5 對照樹有已追蹤檔改動（$(echo "$dirty" | wc -l | tr -d ' ') 筆）——rev5 應唯讀；請 git -C $REV5_ROOT status 查明並還原"
else
  warn "rev5 對照樹不在本機（${REV5_ROOT}）——凍結斷言跳過；對照 stack（埠 2xxxx）需 rev5 樹"
fi

# ── 4. pin 一致性（分歧只警告；判讀＝先判方向、兩向處置相反，承 rev5:CLAUDE.md §3）──
check_pin() { # $1=目錄名
  local pin head
  pin="$(git -C "$ROOT" rev-parse "HEAD:$1" 2>/dev/null || echo 'none')"
  head="$(git -C "$ROOT/$1" rev-parse HEAD)"
  [ "$pin" = "$head" ] && ok "$1 pin＝worktree HEAD（${head:0:7}）" \
    || warn "$1 pin（${pin:0:7}）≠ worktree HEAD（${head:0:7}）——先判方向：worktree 在前＝回外層 bump pin；pin 在前＝worktree 內 merge --ff-only 該 pin"
}
check_pin "base-web"
check_pin "rust-api"

# ── 5. 隨遷工具自測（§4.5；治理 lint 隨 tools/docsync 落地後回填）＋ compose 三檔 render ──
run_tool_test() { # $1=工具相對路徑；失敗才吐明細
  local out
  if ! out="$(python3 "$ROOT/$1" test 2>&1)"; then
    echo "$out" >&2
    die "$1 自測未過——見上方明細"
  fi
  ok "$1 自測綠"
}
# 治理 lint（tools/docsync）：自測→check（GT-01 零漂移）→lint（GT-01～GT-12 零 ERROR）；閘數斷言取自 derive_anchor_codes 掃源現算、不落字面。
docsync_out="$(python3 "$ROOT/tools/docsync" test 2>&1)" || { echo "$docsync_out" >&2; die "tools/docsync 自測未過——見上方明細"; }
ok "tools/docsync 自測綠"
docsync_out="$(python3 "$ROOT/tools/docsync" check 2>&1)" || { echo "$docsync_out" >&2; die "docsync check 有漂移——跑 python3 tools/docsync generate 後 commit"; }
ok "docsync check 零漂移"
docsync_out="$(python3 "$ROOT/tools/docsync" lint 2>&1)" || { echo "$docsync_out" >&2; die "docsync lint 有 ERROR——見上方明細"; }
ok "docsync lint 零 ERROR（$(echo "$docsync_out" | tail -1)）"
GATE_COUNT="$(cd "$ROOT/tools" && python3 -c 'from docsync import gates; print(len(gates.derive_anchor_codes("\n".join(gates.package_sources().values()))))' 2>/dev/null || echo 0)"
[ "$GATE_COUNT" = "12" ] || die "閘數推導得 ${GATE_COUNT} ≠ 12——掃源錨形與 ROSTER 不同步（GT-12 應已紅；恰 12、一進一出）"
ok "閘數斷言過（掃源推導 12＝GT-01～GT-12）"
run_tool_test tools/wf-watchdog.py
run_tool_test deploy/preflight-secrets.py
run_tool_test deploy/generate-secrets.py
run_tool_test deploy/setup-reaper-role.py
run_tool_test deploy/backup-db.py
# ★Day-1 具名豁免（§4.6）：decrypt-secrets 的「五面 parity」案要求 deploy/secrets.dev.enc.yaml 在檔；
#   rev6 世代錯開不搬 rev5 密文（.sops.yaml）、產鑰前該檔必缺。解除謂詞＝檔案存在（存在即無條件全跑）。
if [ -f "$ROOT/deploy/secrets.dev.enc.yaml" ]; then
  run_tool_test deploy/decrypt-secrets.py
else
  warn "Day-1 豁免：deploy/secrets.dev.enc.yaml 未產（rev6 產鑰前）——decrypt-secrets.py 自測跳過；解除謂詞＝該檔存在（產鑰→生成→加密後本節自動回填）"
fi
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  docker compose -f "$ROOT/docker-compose.yml" -f "$ROOT/docker-compose.dev.yml" --profile obs --profile metrics --profile jobs config -q \
    || die "compose dev（含三 profile）render 失敗——見上方"
  docker compose -f "$ROOT/docker-compose.example.yml" config -q || die "compose example render 失敗——見上方"
  rendered="$(docker compose -f "$ROOT/docker-compose.yml" -f "$ROOT/docker-compose.dev.yml" --profile obs --profile metrics --profile jobs config 2>/dev/null)"
  bad_ports="$(echo "$rendered" | grep -E 'published:' | grep -oE '"[0-9]+"' | tr -d '"' | grep -vE '^3[0-9]{4}$' || true)"
  [ -z "$bad_ports" ] || die "compose host 埠非 3xxxx 世代（ADR-00001）：$(echo $bad_ports)"
  echo "$rendered" | grep -q 'rev5' && die "compose render 含 rev5 字面——與常駐 rev5 stack 撞名（ADR-00001 撞名連動）" || true
  ok "compose 三檔 render 綠（host 埠全 3xxxx、零 rev5 字面）"
else
  warn "docker compose 不在機——compose render 檢查跳過"
fi

# ── 6. .env 單一事實來源（承 rev5 形：缺→代勞產生；在→只讀值斷言、不覆寫）────────
ENV_FILE="$ROOT/.env"
SECRETS_DIR_DEFAULT="$HOME/.cache/fork260509-rev6/secrets"
if [ ! -f "$ENV_FILE" ]; then
  printf 'SECRETS_DIR=%s\n' "$SECRETS_DIR_DEFAULT" > "$ENV_FILE"
  ok ".env 缺失→已代勞產生（SECRETS_DIR=${SECRETS_DIR_DEFAULT}）"
fi
SECRETS_DIR="$ROOT/deploy/secrets"   # 讀值失敗時的體檢回退（＝compose 未設變數之回退口徑）
env_line="$(sed -e "1s/^$(printf '\357\273\277')//" -e 's/\r$//' "$ENV_FILE" \
            | grep -E '^[[:space:]]*(export[[:space:]]+)?SECRETS_DIR[[:space:]]*=' | tail -n 1 || true)"
if [ -z "$env_line" ]; then
  warn ".env 已存在但無 SECRETS_DIR 行——compose 將回退 ./deploy/secrets（保護失效）；自癒：echo SECRETS_DIR=$SECRETS_DIR_DEFAULT 附加進 .env"
else
  env_val="$(printf '%s\n' "$env_line" \
             | sed -E 's/^[[:space:]]*(export[[:space:]]+)?SECRETS_DIR[[:space:]]*=[[:space:]]*//; s/[[:space:]]+$//')"
  case "$env_val" in
    *[!A-Za-z0-9_/.-]*|"")
      warn ".env 之 SECRETS_DIR 為空或含空白／shell 元字元（產檔約束見 .env.example）——體檢以 deploy/secrets 回退進行" ;;
    /*)
      SECRETS_DIR="$env_val"
      ok ".env SECRETS_DIR=${env_val}（絕對路徑字面、形制合格）" ;;
    *)
      warn ".env 之 SECRETS_DIR 非絕對路徑字面（compose 不做 shell 展開）——體檢以 deploy/secrets 回退進行" ;;
  esac
fi

# ── 7. secrets 體檢（僅檢缺檔、不碰實值；名冊＝repo 內 .example、落點隨 SECRETS_DIR）──
missing=""
for ex in "$ROOT"/deploy/secrets/*.example; do
  [ -e "$ex" ] || continue
  real_base="$(basename "${ex%.example}")"
  [ -f "$SECRETS_DIR/$real_base" ] || missing="$missing $real_base"
done
if [ -n "$missing" ]; then
  warn "SECRETS_DIR（${SECRETS_DIR}）缺實值檔：$missing —— 重建：deploy/secrets/README.md 產鑰→生成→加密→解密流程；上機前把關＝preflight"
else
  ok "SECRETS_DIR（${SECRETS_DIR}）實值檔齊"
fi

# ── 摘要 ─────────────────────────────────────────────────────────────
echo "[bootstrap] ── 完成：掃描防線／源倉×2／worktree×2／基線 ${BASELINE_BRANCH}@${BASEWEB_BASE_SHA}／rev5 凍結斷言／docsync 三段＋閘數／隨遷工具自測；警告 $WARNS 項$([ "$WARNS" -gt 0 ] && echo '（見上方 ⚠）' || echo '')"
