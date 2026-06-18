#!/bin/sh
# Scenario: finalize-worktree re-entry when the PR is ALREADY MERGED.
#
# Models the assert-then-reconcile case (sessions 82/83/85, finding 3): a prior
# run merged the PR on GitHub but aborted before phase 4 reconciled locally (gh's
# cross-worktree `--delete-branch` abort). Re-running `/session-end` re-enters
# finalize with the remote already `MERGED` and the remote feature branch still
# lingering. The skill must NOT call `gh pr merge` again (re-merging a merged PR
# errors); it reconciles local state to the merged remote: fast-forward local
# `main` (ISS-W3), delete the local and remote branch, remove the worktree.
#
# Prints the repo path on stdout. The env to export is echoed to stderr.
set -e

MOCKBIN=$(cd "$(dirname "$0")/../../gh-mock" && pwd)
ROOT=$(mktemp -d "${TMPDIR:-/tmp}/lck-finmerged.XXXXXX")
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

BR=feature/session-402-merged
git switch -qc "$BR"
mkdir -p sessions
echo work > feature.txt
printf '# Session 402 already-merged\n' > sessions/2026-06-18_session_402_merged.md
git add -A
git commit -qm "feat: 402 work + session log"
git push -q -u origin "$BR"             # the branch is on the remote (PR opened)
git switch -q main
git worktree add -q .claude/worktrees/session-402-merged "$BR"

# Simulate the prior, half-finished run: the PR was MERGED on GitHub, but the
# local reconcile never happened. Land the merge on the bare remote so
# origin/main carries it, leave the remote feature branch in place (the
# --delete-branch abort), and pre-seed the gh mock state to MERGED. Local main
# is deliberately left behind origin/main.
TMP=$(mktemp -d)
git clone -q "$REMOTE" "$TMP/clone"
git -C "$TMP/clone" config user.email mock@example.com
git -C "$TMP/clone" config user.name ghmock
git -C "$TMP/clone" merge --no-ff -q -m "Merge pull request #1 ($BR)" "origin/$BR"
git -C "$TMP/clone" push -q origin HEAD:main
rm -rf "$TMP"
echo "$BR" > "$MOCKDIR/pr_branch"
echo MERGED > "$MOCKDIR/pr_state"

{
  echo "scenario repo:  $REPO"
  echo "GH_MOCK_DIR:    $MOCKDIR"
  echo "GH_MOCK_REMOTE: $REMOTE"
  echo "mock gh bin:    $MOCKBIN"
} >&2
echo "$REPO"
