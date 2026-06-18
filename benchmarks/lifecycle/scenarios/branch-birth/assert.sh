#!/bin/sh
# Assert session-start birthed the session branch off origin/main, not the
# stray-ahead local main. Usage: assert.sh <repo-path>. Non-zero on mismatch.
REPO="$1"
[ -d "$REPO" ] || { echo "FAIL: repo not found: $REPO"; exit 2; }
cd "$REPO" || exit 2
fail=0

B=$(git branch --list 'feature/*' --format='%(refname:short)')
n=$(printf '%s\n' "$B" | grep -c .)
echo "feature branch(es): [$B]"
[ "$n" = "1" ] || { echo "FAIL: expected exactly 1 session branch, got $n"; exit 1; }

if [ "$(git rev-parse "$B")" = "$(git rev-parse origin/main)" ]; then
  echo "ok: $B born exactly off origin/main ($(git rev-parse --short origin/main))"
else
  echo "FAIL: $B tip $(git rev-parse --short "$B") != origin/main $(git rev-parse --short origin/main)"
  fail=1
fi

for sha in $(git rev-list origin/main..main); do
  if git merge-base --is-ancestor "$sha" "$B" 2>/dev/null; then
    echo "FAIL: stray $(git rev-parse --short "$sha") leaked into $B"
    fail=1
  else
    echo "ok: stray $(git rev-parse --short "$sha") excluded from $B"
  fi
done

echo "VERDICT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit $fail
