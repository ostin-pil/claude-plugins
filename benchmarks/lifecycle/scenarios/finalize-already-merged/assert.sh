#!/bin/sh
# Assert finalize-worktree reconciled an ALREADY-MERGED PR without re-merging.
# Usage: assert.sh <repo-path> <gh-mock-dir>. Non-zero on mismatch.
#
# The distinguishing check from finalize-clean: `gh pr merge` is called ZERO
# times. The merge had already landed on the remote; the skill's job here is the
# local reconcile only (phase 4), never another merge.
REPO="$1"
MOCKDIR="$2"
[ -d "$REPO" ] || { echo "FAIL: repo not found: $REPO"; exit 2; }
cd "$REPO" || exit 2
git fetch -q origin --prune 2>/dev/null
fail=0

# the merge is on origin/main (from the simulated prior run)
if git log --oneline -1 origin/main | grep -qi 'merge'; then
  echo "ok: origin/main carries the merge commit"
else
  echo "FAIL: origin/main has no merge commit"; fail=1
fi

# never-merge-locally: local main equals origin/main exactly (fast-forward only)
if [ "$(git rev-parse main)" = "$(git rev-parse origin/main)" ]; then
  echo "ok: local main fast-forwarded to origin/main (ISS-W3)"
else
  echo "FAIL: local main ($(git rev-parse --short main)) != origin/main ($(git rev-parse --short origin/main))"; fail=1
fi

# local branch gone
git branch --list 'feature/session-402-merged' | grep -q . && { echo "FAIL: local branch still present"; fail=1; } || echo "ok: local branch deleted"
# remote branch gone (the lingering branch reconciled via gh api DELETE)
[ -n "$(git ls-remote origin 'refs/heads/feature/*' 2>/dev/null)" ] && { echo "FAIL: remote feature branch still present"; fail=1; } || echo "ok: lingering remote branch deleted"
# worktree gone
git worktree list | grep -q 'session-402-merged' && { echo "FAIL: worktree still present"; fail=1; } || echo "ok: worktree removed"

# THE distinguishing assertion: a merged PR is never re-merged.
# grep -c prints 0 but exits 1 when there are no matches, so capture without a
# `|| echo` fallback (which would append a second line) and default empty to 0.
mc=$(grep -c '^gh pr merge' "$MOCKDIR/log" 2>/dev/null); [ -z "$mc" ] && mc=0
[ "$mc" = "0" ] && echo "ok: gh pr merge never called (merged PR not re-merged)" || { echo "FAIL: gh pr merge called $mc times on an already-merged PR (expected 0)"; fail=1; }

# the skill did consult the authoritative remote state
grep -q '^gh pr view' "$MOCKDIR/log" 2>/dev/null && echo "ok: skill checked the remote PR state" || echo "note: no gh pr view in log (state inferred another way)"

echo "VERDICT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit $fail
