#!/bin/sh
# Scenario: session-start branch birth off the integration ref.
#
# Local main is one stray commit AHEAD of origin/main. A correct session-start
# fetches and births the session branch off origin/main, excluding the stray;
# a buggy one branches from the stale working tree and inherits it.
#
# Prints the repo path on stdout (last line). Diagnostics go to stderr.
set -e

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/lck-birth.XXXXXX")
REMOTE="$ROOT/remote.git"
REPO="$ROOT/repo"

git init --bare -q "$REMOTE"
git init -q "$REPO"
cd "$REPO"
git config user.email bench@example.com
git config user.name Bench
git remote add origin "$REMOTE"

mkdir -p .claude sessions
cat > .claude/lifecycle-manifest.md <<'EOF'
```yaml
product_name: benchwidget
remote: origin
integration_ref: origin/main
local_main: main
pr_base: main
branch_pattern: "feature/session-{n}-{topic}"
branch_glob: "feature/*"
worktree_dir: .claude/worktrees
log_dir: sessions
merge_strategy: merge
requires_remote: true
```
EOF
echo "# bench" > README.md
git add -A
git commit -qm "chore: init"
git branch -M main
git push -q -u origin main            # origin/main = C1

echo stray > stray.txt
git add stray.txt
git commit -qm "stray: direct commit on local main (not pushed)"   # C2, local-only; main now ahead

{
  echo "scenario repo: $REPO"
  echo "origin/main (base): $(git rev-parse --short origin/main)"
  echo "local main (stray-ahead): $(git rev-parse --short main)"
} >&2
echo "$REPO"
