#!/bin/sh
# Scenario: session-start must re-read git state before it mints a session
# number, not act on the snapshot its step-1 fetch took.
#
# The repo starts with session logs through 5 and no session branches, so the
# pre-flight at step 1 sees a maximum of 5 and would pick 6. The git shim lands
# feature/session-6-concurrent on the remote after the agent's first fetch, so
# 6 is claimed by the time branch birth happens. A skill that re-reads picks 7;
# one that trusts its step-1 snapshot collides on 6.
#
# Prints the repo path on stdout (last line). Diagnostics go to stderr.
set -e

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/lck-stale.XXXXXX")
REMOTE="$ROOT/remote.git"
REPO="$ROOT/repo"
MOCK="$ROOT/git-mock-state"

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
log_pattern: "{date}_session_{n}[_{suffix}].md"
merge_strategy: merge
requires_remote: true
issues_file: none
plan_doc: none
```
EOF

# Session logs through 5, so the log-filename source tops out at 5.
n=1
while [ "$n" -le 5 ]; do
  cat > "sessions/2026-07-0${n}_session_${n}.md" <<EOF
# Session ${n} — 2026-07-0${n}

Branch: \`feature/session-${n}-widget\`, born off \`origin/main\`.

## Context

Bench filler for session ${n}.

## Build status

Not run.

## What's next

1. Keep going.

## Commits (this session)

None.
EOF
  n=$((n + 1))
done

echo "# bench" > README.md
git add -A
git commit -qm "chore: init with session logs through 5"
git branch -M main
git push -q -u origin main

mkdir -p "$MOCK"

{
  echo "scenario repo:  $REPO"
  echo "bare remote:    $REMOTE"
  echo "mock state dir: $MOCK"
  echo "real git:       $(command -v git)"
  echo
  echo "Run the agent with the git shim first on PATH, e.g.:"
  echo "  export GIT_MOCK_DIR=$MOCK"
  echo "  export GIT_MOCK_REAL=$(command -v git)"
  echo "  export GIT_MOCK_REMOTE=$REMOTE"
  echo "  export PATH=<benchmarks>/lifecycle/git-mock:\$PATH"
} >&2
echo "$REPO"
