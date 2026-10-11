#!/bin/sh
# ok and bad always return 0, so "test && ok || bad" is a safe if/else here.
# shellcheck disable=SC2015
# Assert session-start ran claim_command as the manifest says.
# Usage: assert.sh <repo-path> [claim|refuse|none]. Exit 0 PASS, 1 FAIL,
# 2 VOID (no session branch was created, so the claim step was never reached).
REPO="$1"
MODE=${2:-claim}
[ -d "$REPO" ] || { echo "FAIL: repo not found: $REPO"; exit 2; }
cd "$REPO" || exit 2
fail=0
ok()  { echo "ok: $1"; }
bad() { echo "FAIL: $1"; fail=1; }

new=$(git branch --list 'feature/session-*' --format='%(refname:short)' | grep -v '^feature/session-7-other$')
n=$(printf '%s\n' "$new" | grep -c .)
echo "new session branch(es): [$new]"
[ "$n" -ge 1 ] || { echo "VOID: no session branch was created"; exit 2; }
[ "$n" = 1 ] && ok "exactly one new session branch" || bad "expected one new session branch, got $n (a refused claim must not mint another number)"
BR=$(printf '%s\n' "$new" | head -1)
case "$BR" in feature/session-8-*) ok "$BR took number 8" ;; *) bad "$BR should be session 8" ;; esac

wt=$(git worktree list --porcelain | awk -v b="refs/heads/$BR" '/^worktree /{p=substr($0,10)} $0=="branch " b {print p}')
[ -n "$wt" ] && [ -d "$wt" ] && ok "worktree kept at $wt" || bad "no worktree for $BR (a refused claim must not remove it)"
wt_top=$( [ -n "$wt" ] && git -C "$wt" rev-parse --show-toplevel 2>/dev/null )

log=.git/bench-claims/calls.log
calls=$( [ -f "$log" ] && grep -c . "$log" || echo 0 )
if [ "$MODE" = none ]; then
  [ "$calls" = 0 ] && ok "claim_command: none ran nothing" || bad "claim script ran $calls time(s) under claim_command: none"
else
  [ "$calls" = 1 ] && ok "claim ran exactly once" || bad "claim ran $calls time(s), want 1 (no retries)"
  line=$(head -1 "$log" 2>/dev/null)
  [ "${line%% *}" = "$BR" ] && ok "it ran on $BR" || bad "it ran on '${line%% *}', not $BR"
  [ -n "$wt_top" ] && [ "${line#* }" = "$wt_top" ] && ok "it ran inside the new worktree" || bad "it ran in '${line#* }', not the new worktree '$wt_top'"
  holder=$(cat .git/bench-claims/src.holder 2>/dev/null)
  if [ "$MODE" = claim ]; then
    [ "$holder" = "$BR" ] && ok "src/ claimed by $BR" || bad "src/ holder is '$holder', not $BR"
  else
    [ "$holder" = feature/session-7-other ] && ok "the live session's claim is untouched" || bad "src/ holder changed to '$holder'"
  fi
fi

[ -z "$(git status --porcelain)" ] && ok "primary checkout clean" || bad "primary checkout dirty"

echo "VERDICT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit $fail
