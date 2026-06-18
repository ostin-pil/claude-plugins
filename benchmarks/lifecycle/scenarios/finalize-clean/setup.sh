#!/bin/sh
# Scenario: finalize-worktree happy path (clean merge via the gh mock).
#
# A normal pre-finalize state: one feature/* worktree with a code commit and a
# committed session log, ahead of origin/main, not yet pushed (the skill pushes).
# The gh mock lands the merge on the file remote and deletes the remote branch.
#
# Prints the repo path on stdout. The GH_MOCK_DIR to export is echoed to stderr.
set -e

MOCKBIN=$(cd "$(dirname "$0")/../../gh-mock" && pwd)
ROOT=$(mktemp -d "${TMPDIR:-/tmp}/lck-finclean.XXXXXX")
REMOTE="$ROOT/remote.git"
REPO="$ROOT/repo"
MOCKDIR="$ROOT/gh-mock-state"
mkdir -p "$MOCKDIR"

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
log_presence_regex: '^sessions/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_session.*\.md$'
build_commands: [true]
test_commands: [true]
subpkg_guard: none
merge_strategy: merge
prose_gate: none
code_reviewer: none
review_command: none
requires_remote: true
```
EOF
echo "# bench" > README.md
git add -A
git commit -qm "chore: init"
git branch -M main
git push -q -u origin main

git switch -qc feature/session-401-clean
mkdir -p sessions
echo work > feature.txt
printf '# Session 401 clean\n' > sessions/2026-06-18_session_401_clean.md
git add -A
git commit -qm "feat: 401 work + session log"
git switch -q main
git worktree add -q .claude/worktrees/session-401-clean feature/session-401-clean

{
  echo "scenario repo:  $REPO"
  echo "GH_MOCK_DIR:    $MOCKDIR"
  echo "GH_MOCK_REMOTE: $REMOTE"
  echo "mock gh bin:    $MOCKBIN"
} >&2
echo "$REPO"
