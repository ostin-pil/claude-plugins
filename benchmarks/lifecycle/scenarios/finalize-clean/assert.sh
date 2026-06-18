#!/bin/sh
# Assert finalize-worktree (clean mode) landed the merge and fully reconciled.
# Usage: assert.sh <repo-path> <gh-mock-dir>. Non-zero on mismatch.
REPO="$1"
MOCKDIR="$2"
[ -d "$REPO" ] || { echo "FAIL: repo not found: $REPO"; exit 2; }
cd "$REPO" || exit 2
git fetch -q origin --prune 2>/dev/null
fail=0

# branch landed: feature tip is an ancestor of origin/main (merge happened)
if git merge-base --is-ancestor feature/session-401-clean origin/main 2>/dev/null; then
  echo "ok: feature branch merged into origin/main"
else
  # branch may be deleted locally already; check the remote merge commit instead
  git log --oneline -1 origin/main | grep -qi 'merge' && echo "ok: origin/main has the merge commit" || { echo "FAIL: merge did not land on origin/main"; fail=1; }
fi

# never-merge-locally: local main equals origin/main exactly (fast-forward only)
if [ "$(git rev-parse main)" = "$(git rev-parse origin/main)" ]; then
  echo "ok: local main fast-forwarded to origin/main (no divergent local merge)"
else
  echo "FAIL: local main ($(git rev-parse --short main)) != origin/main ($(git rev-parse --short origin/main))"; fail=1
fi

# local branch gone
git branch --list 'feature/session-401-clean' | grep -q . && { echo "FAIL: local branch still present"; fail=1; } || echo "ok: local branch deleted"
# remote branch gone
[ -n "$(git ls-remote origin 'refs/heads/feature/*' 2>/dev/null)" ] && { echo "FAIL: remote feature branch still present"; fail=1; } || echo "ok: remote branch deleted"
# worktree gone
git worktree list | grep -q 'session-401-clean' && { echo "FAIL: worktree still present"; fail=1; } || echo "ok: worktree removed"

# gh mock: exactly one pr-merge call (no retry on a merged PR)
mc=$(grep -c '^gh pr merge' "$MOCKDIR/log" 2>/dev/null || echo 0)
[ "$mc" = "1" ] && echo "ok: gh pr merge called exactly once" || { echo "FAIL: gh pr merge called $mc times (expected 1)"; fail=1; }

echo "VERDICT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit $fail
