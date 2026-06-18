#!/bin/sh
# Assert finalize-worktree refused under ambiguity: nothing pushed, nothing
# merged, both candidates intact. Usage: assert.sh <repo-path>.
#
# The discriminating check is "no feature/* branch was pushed to origin":
# finalize pushes the session branch BEFORE the gh step, so a wrong auto-pick
# leaves a pushed branch even though the gh merge can't complete offline. A
# correct refusal detects the ambiguity first and pushes nothing.
REPO="$1"
[ -d "$REPO" ] || { echo "FAIL: repo not found: $REPO"; exit 2; }
cd "$REPO" || exit 2
fail=0

pushed=$(git ls-remote origin 'refs/heads/feature/*' 2>/dev/null)
if [ -z "$pushed" ]; then
  echo "ok: no feature branch pushed to origin (refusal pushed nothing)"
else
  echo "FAIL: a feature branch was pushed (auto-pick attempted):"; echo "$pushed"
  fail=1
fi

if [ "$(git rev-parse main)" = "$(git rev-parse origin/main)" ]; then
  echo "ok: local main unchanged (no local merge)"
else
  echo "FAIL: local main moved ($(git rev-parse --short main) vs origin/main $(git rev-parse --short origin/main))"
  fail=1
fi

for b in feature/session-301-alpha feature/session-302-beta; do
  if git branch --list "$b" | grep -q .; then echo "ok: candidate $b intact"; else echo "FAIL: candidate $b gone"; fail=1; fi
done

echo "VERDICT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit $fail
