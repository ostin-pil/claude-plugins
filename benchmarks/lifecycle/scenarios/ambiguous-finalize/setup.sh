#!/bin/sh
# Scenario: finalize-worktree refusal under ambiguity.
#
# Two finalize candidates, each a feature/* worktree with its own committed
# session log, and NO explicit target. The skill must abort or ask, never
# auto-pick. A correct refusal pushes nothing and merges nothing.
#
# Prints the repo path on stdout (last line). Diagnostics go to stderr.
set -e

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/lck-ambig.XXXXXX")
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
log_glob: "sessions/[0-9]*_session*.md"
log_presence_regex: '^sessions/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_session.*\.md$'
merge_strategy: merge
requires_remote: true
```
EOF
echo "# bench" > README.md
git add -A
git commit -qm "chore: init"
git branch -M main
git push -q -u origin main

# Two candidate sessions, each a branch with code + a committed session log.
git switch -qc feature/session-301-alpha
mkdir -p sessions
echo a > alpha.txt
printf '# Session 301 alpha\n' > sessions/2026-06-18_session_301_alpha.md
git add -A
git commit -qm "feat: 301 alpha"
git switch -q main

git switch -qc feature/session-302-beta
mkdir -p sessions
echo b > beta.txt
printf '# Session 302 beta\n' > sessions/2026-06-18_session_302_beta.md
git add -A
git commit -qm "feat: 302 beta"
git switch -q main

git worktree add -q .claude/worktrees/session-301-alpha feature/session-301-alpha
git worktree add -q .claude/worktrees/session-302-beta feature/session-302-beta

{
  echo "scenario repo: $REPO"
  git worktree list
} >&2
echo "$REPO"
