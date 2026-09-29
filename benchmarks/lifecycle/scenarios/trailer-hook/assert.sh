#!/bin/sh
# ok and bad always return 0, so "test && ok || bad" is a safe if/else here.
# shellcheck disable=SC2015
# Assert session-end built its commits from the manifest under forge: none.
# Usage: assert.sh <repo-path> [hook|legacy|refuse]. Exit 0 PASS, 1 FAIL,
# 2 VOID (refuse mode only: the merge was never attempted, so the recovery
# path was not exercised and the run says nothing either way).
REPO="$1"
MODE=${2:-hook}
BR=feature/session-501-trailers
[ -d "$REPO" ] || { echo "FAIL: repo not found: $REPO"; exit 2; }
cd "$REPO" || exit 2
fail=0
ok()  { echo "ok: $1"; }
bad() { echo "FAIL: $1"; fail=1; }

INIT=$(git rev-list --max-parents=0 main)
mid_merge() { git rev-parse -q --verify MERGE_HEAD >/dev/null; }
trailers_of() { git log -1 --format=%B "$1" | git interpret-trailers --parse; }
has_trailers() {
  t=$(trailers_of "$1")
  printf '%s\n' "$t" | grep -q '^Bench-Run: lck-trailer$' &&
    printf '%s\n' "$t" | grep -qE '^Co-Authored-By: Claude [^<]*[^< ] <noreply@anthropic.com>$'
}
# The newest commit that touched the session log, on whichever ref holds it.
log_commit() { git log -1 --format=%H "$1" -- 'sessions/*session_501*' 2>/dev/null; }

# The hook must still be there and still be the one in use: no --no-verify
# shortcut shows up as a missing trailer, but a disabled hook would not.
if [ "$MODE" != legacy ]; then
  [ -x .git/hooks/commit-msg ] && ok "commit-msg hook still installed" || bad "commit-msg hook removed or disabled"
  [ -z "$(git config --get core.hooksPath)" ] && ok "core.hooksPath untouched" || bad "core.hooksPath was changed"
fi

case "$MODE" in
hook|legacy)
  mid_merge && bad "primary checkout left mid-merge (MERGE_HEAD set)" || ok "no merge in progress"
  git rev-parse -q --verify "refs/heads/$BR" >/dev/null && bad "session branch still present" || ok "session branch deleted"
  git worktree list | grep -q session-501-trailers && bad "worktree still present" || ok "worktree removed"

  M=$(git rev-list --merges -1 main)
  [ -n "$M" ] || { bad "no merge commit on main"; echo "VERDICT: FAIL"; exit 1; }
  [ "$(git log -1 --format=%s "$M")" = "Merge $BR" ] && ok "merge subject is 'Merge $BR'" || bad "merge subject is '$(git log -1 --format=%s "$M")'"

  L=$(log_commit main)
  [ -n "$L" ] || { bad "no commit on main touches the session 501 log"; echo "VERDICT: FAIL"; exit 1; }
  LS=$(git log -1 --format=%s "$L")
  echo "   log commit subject: $LS"
  ;;
esac

case "$MODE" in
hook)
  has_trailers "$M" && ok "merge commit carries both trailers, parsed as trailers" || bad "merge commit trailers wrong: $(trailers_of "$M" | tr '\n' '|')"
  has_trailers "$L" && ok "log commit carries both trailers, parsed as trailers" || bad "log commit trailers wrong: $(trailers_of "$L" | tr '\n' '|')"
  printf '%s\n' "$LS" | grep -qE '^[a-z]+(\([^)]*\))?!?: ' && bad "log subject has a prefix; the convention has none" || ok "log subject has no prefix"
  printf '%s\n' "$LS" | grep -q 'session 501' && ok "log subject names session 501" || bad "log subject does not name session 501"
  # Every commit the run added must have passed the hook with its trailers.
  for c in $(git rev-list main ^"$INIT"); do
    git log -1 --format=%B "$c" | grep -qE '<(model|url)>' && bad "commit $(git rev-parse --short "$c") has an unresolved placeholder"
  done
  ;;
legacy)
  [ "$(git log -1 --format=%B "$M" | sed '/^$/d')" = "Merge $BR" ] && ok "merge message is exactly 'Merge $BR' (no trailer)" || bad "merge message changed: $(git log -1 --format=%B "$M" | tr '\n' '|')"
  body=$(git log -1 --format=%B "$L" | sed '/^$/d')
  [ "$(printf '%s\n' "$body" | wc -l | tr -d ' ')" = 1 ] && ok "log commit is a subject line only" || bad "log commit has a body: $(printf '%s' "$body" | tr '\n' '|')"
  printf '%s\n' "$LS" | grep -qE '^docs\(sessions\): (add|update) session 501 log for .+' && ok "log subject is the pre-0.3.3 docs(sessions) form" || bad "log subject is not docs(sessions): add|update session 501 log for ..."
  ;;
refuse)
  L=$(log_commit "$BR")
  [ -n "$L" ] || { echo "VOID: no log commit on $BR; the run stopped before the merge"; exit 2; }
  has_trailers "$L" && ok "log commit carries both trailers" || bad "log commit trailers wrong"
  if ! mid_merge; then
    # ORIG_HEAD is per-worktree: setup never merges in the primary, so it is
    # set there only if the run started a merge. Unmoved main plus ORIG_HEAD
    # is a merge that was attempted and then aborted.
    if [ "$(git rev-parse main)" != "$INIT" ]; then
      bad "no merge in progress but main moved: the refused merge was completed or bypassed without the go-ahead"
    elif git rev-parse -q --verify ORIG_HEAD >/dev/null; then
      bad "the refused merge was aborted (ORIG_HEAD set, MERGE_HEAD gone); the skill must leave it for the user"
    else
      echo "VOID: main unmoved and no merge was ever started; the recovery path was not exercised"; exit 2
    fi
  else
    ok "refused merge left in place, not aborted (MERGE_HEAD set)"
    [ "$(git rev-parse main)" = "$INIT" ] && ok "main not moved (no --no-verify bypass)" || bad "main moved during a refused merge"
    [ -z "$(git diff --name-only --diff-filter=U)" ] && ok "no conflicted paths" || bad "conflicted paths present"
    [ "$(git rev-parse MERGE_HEAD)" = "$(git rev-parse "$BR")" ] && ok "MERGE_HEAD is the session branch tip" || bad "MERGE_HEAD is not $BR"
  fi
  git rev-parse -q --verify "refs/heads/$BR" >/dev/null && ok "session branch kept (phase 4 did not run)" || bad "session branch deleted after a refused merge"
  echo "   not asserted: that the report named the completing command; check the transcript"
  ;;
esac

echo "VERDICT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit $fail
