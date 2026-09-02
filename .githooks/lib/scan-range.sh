# .githooks/lib/scan-range.sh — pre-push stdin 解析＋掃描範圍推導（承 rev5；三 repo 共用）
# ★本 lib 只承載 pre-push 面（source 後呼叫 scan_push_ranges）；pre-commit 不 source 本檔。
# 呼叫端先設 SCAN_CONFIG＝.gitleaks.toml 路徑（源倉自身樹無此檔、必須顯式指定；外層同形統一）。
#
# 範圍推導（契約表）：
#   一般更新（兩 oid 非全零）      → --log-opts=<remote-oid>..<local-oid>
#   新分支首推（remote-oid 全零）  → --log-opts=<local-oid> --not --remotes=origin
#   上述退階（origin 零 ref）      → 掃整條分支（--log-opts=<local-oid>）
#   刪除分支（local-oid 全零）     → 跳過該行（無內容可掃）
# 退出碼分流同 pre-commit：scanner exit 2＝機密命中→回 1 擋 push；其餘非零＝掃描器本身異常（亦回 1、指向 bootstrap）。
# `git push --no-verify` 仍可繞過＝已知邊界。

scan_range_run() {
  if [ -n "${SCAN_CONFIG:-}" ]; then
    betterleaks git --config "$SCAN_CONFIG" --redact --verbose --exit-code 2 --log-opts="$1"
  else
    betterleaks git --redact --verbose --exit-code 2 --log-opts="$1"
  fi
}

scan_push_ranges() {
  sr_status=0
  while read -r sr_local_ref sr_local_oid sr_remote_ref sr_remote_oid; do
    [ -z "$sr_local_ref" ] && continue
    case "$sr_local_oid" in
      *[!0]*) ;;
      *) continue ;;
    esac
    case "$sr_remote_oid" in
      *[!0]*) sr_opts="$sr_remote_oid..$sr_local_oid" ;;
      *)
        if [ -n "$(git for-each-ref --count=1 'refs/remotes/origin')" ]; then
          sr_opts="$sr_local_oid --not --remotes=origin"
        else
          sr_opts="$sr_local_oid"
        fi ;;
    esac
    scan_range_run "$sr_opts"
    sr_rc=$?
    if [ "$sr_rc" -eq 2 ]; then
      echo "[pre-push] ✗ 機密命中（${sr_local_ref}、範圍 ${sr_opts}；輸出值已遮蔽）——移除後重推；誤報→修 .gitleaks.toml allowlist、絕不 --no-verify" >&2
      sr_status=1
    elif [ "$sr_rc" -ne 0 ]; then
      echo "[pre-push] ✗ 掃描器本身異常（exit ${sr_rc}）、非機密命中——跑 bash tools/bootstrap.sh 檢修（安裝／釘版斷言）" >&2
      sr_status=1
    fi
  done
  return "$sr_status"
}
