#!/bin/sh
# Assert the end state after cleanup-worktrees ran on the scenario repo.
# Usage: assert.sh <repo-path>. Exits non-zero on any mismatch.
REPO="$1"
[ -d "$REPO" ] || { echo "FAIL: repo not found: $REPO"; exit 2; }
cd "$REPO" || exit 2
fail=0

git worktree list | grep -q 'session-901-done'        && { echo "FAIL: 901 worktree still present (should be swept)"; fail=1; } || echo "ok: 901 worktree swept"
git branch --list 'feature/session-901-done' | grep -q . && { echo "FAIL: branch 901 still present"; fail=1; } || echo "ok: branch 901 deleted"
git worktree list | grep -q 'session-902-active'      && echo "ok: 902 worktree preserved" || { echo "FAIL: 902 worktree swept (should survive)"; fail=1; }
git branch --list 'feature/session-902-active' | grep -q . && echo "ok: branch 902 preserved" || { echo "FAIL: branch 902 deleted (should survive)"; fail=1; }

echo "VERDICT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit $fail
