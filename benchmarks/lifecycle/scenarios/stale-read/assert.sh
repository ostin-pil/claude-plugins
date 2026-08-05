#!/bin/sh
# Assert session-start re-read git state before minting a session number.
# Usage: assert.sh <repo-path>. Non-zero on mismatch.
#
# Exit 2 is a void run (the harness did not stage the drift, so the scenario
# tested nothing); exit 1 is a real skill failure. They must not be confused:
# a void run that reported PASS would be the worst outcome here, since 6 is
# the answer both a correct skill and a broken harness produce.
REPO="$1"
[ -d "$REPO" ] || { echo "FAIL: repo not found: $REPO"; exit 2; }
cd "$REPO" || exit 2
fail=0

CLAIMED="${GIT_MOCK_BRANCH:-feature/session-6-concurrent}"

# Void-run guard first. If the shim never landed the concurrent branch, the
# agent never faced the collision and the result means nothing.
if ! git ls-remote --heads origin "$CLAIMED" 2>/dev/null | grep -q .; then
  echo "VOID: $CLAIMED never landed on the remote; the drift did not fire."
  echo "      Check GIT_MOCK_DIR/log and GIT_MOCK_DIR/drift-err."
  exit 2
fi
echo "ok: concurrent claim $CLAIMED is present on the remote"

# The agent's own branch: a local feature/* branch that is not the injected one.
B=$(git branch --list 'feature/*' --format='%(refname:short)' | grep -v "^${CLAIMED}$")
n=$(printf '%s\n' "$B" | grep -c .)
echo "agent branch(es): [$B]"
[ "$n" = "1" ] || { echo "FAIL: expected exactly 1 session branch from the agent, got $n"; exit 1; }

num=$(printf '%s\n' "$B" | grep -oE 'session-[0-9]+' | grep -oE '[0-9]+')
[ -n "$num" ] || { echo "FAIL: could not parse a session number out of $B"; exit 1; }

if [ "$num" = "6" ]; then
  echo "FAIL: minted session 6, colliding with $CLAIMED — the skill acted on its step-1 snapshot"
  fail=1
elif [ "$num" -ge 7 ]; then
  echo "ok: minted session $num, clear of the concurrent claim on 6"
else
  echo "FAIL: minted session $num, below the 5 already present in sessions/"
  fail=1
fi

# The branch still has to be born off the integration ref, as in branch-birth.
if [ "$(git rev-parse "$B")" = "$(git rev-parse origin/main)" ]; then
  echo "ok: $B born off origin/main ($(git rev-parse --short origin/main))"
else
  echo "FAIL: $B tip $(git rev-parse --short "$B") != origin/main $(git rev-parse --short origin/main)"
  fail=1
fi

echo "VERDICT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit $fail
