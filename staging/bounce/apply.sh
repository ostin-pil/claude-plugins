#!/bin/sh
# Apply the prose-lint fallback-chain shim to the Bounce repo.
#
# Run this YOURSELF, from inside the Bounce repo, on a fresh feature branch
# (Bounce's one-PR-per-session rule; .githooks/pre-commit refuses commits
# on main). It only renames and copies files; it does not commit, push, or
# touch .claude/. You commit, write the session log, and open the one PR.
#
# Usage (from the Bounce repo root):
#   git fetch origin
#   git switch -c feature/session-<N>-prose-lint-shim origin/main
#   sh /Users/costa/Projects/prose-lint/staging/bounce/apply.sh
#   # review `git status`, then commit + session log + PR per workflow.md
#
# Reverse it: `git checkout -- bin/ && git clean -f bin/` before committing,
# or just delete the branch.

set -eu

STAGE="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d .git ] || [ ! -f bin/check-prose.sh ]; then
  echo "error: run this from the Bounce repo root (bin/check-prose.sh not found)" >&2
  exit 1
fi

branch=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
if [ "$branch" = "main" ] || [ -z "$branch" ]; then
  echo "error: on '$branch'. Switch to a feature branch off origin/main first." >&2
  exit 1
fi

# Preserve today's implementations as the CI/offline fallback.
git mv bin/check-prose.sh       bin/check-prose-impl.py
git mv bin/check-prose-bulk.sh  bin/check-prose-bulk-impl.py
git mv bin/unwrap-prose.py      bin/unwrap-prose-impl.py

# Install the shims under the original names (interface unchanged).
cp "$STAGE/bin/check-prose.sh"       bin/check-prose.sh
cp "$STAGE/bin/check-prose-bulk.sh"  bin/check-prose-bulk.sh
cp "$STAGE/bin/unwrap-prose.py"      bin/unwrap-prose.py
chmod +x bin/check-prose.sh bin/check-prose-bulk.sh bin/unwrap-prose.py \
         bin/check-prose-impl.py bin/check-prose-bulk-impl.py bin/unwrap-prose-impl.py

git add bin/

echo
echo "done. staged:"
echo "  bin/check-prose.sh        -> shim (was: renamed to check-prose-impl.py)"
echo "  bin/check-prose-bulk.sh   -> shim (was: renamed to check-prose-bulk-impl.py)"
echo "  bin/unwrap-prose.py       -> shim (was: renamed to unwrap-prose-impl.py)"
echo
echo "optional: cp $STAGE/prose-lint.toml .prose-lint.toml   (bulk-only scope; see file header)"
echo
echo "next (yours): commit, write sessions/<date>_session_<N>_prose-lint-shim.md,"
echo "open one PR, let Bounce's prose CI gate run. Do not edit .claude/."
