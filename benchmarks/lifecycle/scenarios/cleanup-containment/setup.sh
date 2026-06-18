#!/bin/sh
# Scenario: cleanup-worktrees containment.
#
# Builds a repo with a file-based remote and two non-primary worktrees:
#   feature/session-901-done   - its commit IS merged into origin/main -> should be swept
#   feature/session-902-active - its commit is NOT in origin/main       -> should survive
#
# Prints the repo path on stdout (last line). Diagnostics go to stderr.
set -e

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/lck-cleanup.XXXXXX")
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
git push -q -u origin main

# 901: merged into main (contained in origin/main)
git switch -qc feature/session-901-done
echo done > done.txt
git add done.txt
git commit -qm "feat: 901"
git switch -q main
git merge -q --no-ff feature/session-901-done -m "Merge 901"
git push -q origin main

# 902: unique work, not merged
git switch -qc feature/session-902-active
echo wip > wip.txt
git add wip.txt
git commit -qm "feat: 902"
git switch -q main

git worktree add -q .claude/worktrees/session-901-done feature/session-901-done
git worktree add -q .claude/worktrees/session-902-active feature/session-902-active
git fetch -q origin

{
  echo "scenario repo: $REPO"
  git worktree list
} >&2
echo "$REPO"
