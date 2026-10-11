#!/bin/sh
# Scenario: session-start runs the project's path claim in the new checkout.
#
# Usage: setup.sh [claim|refuse|none]   (default claim)
#
#   claim   claim_command names tools/claim.sh, which records a claim for the
#           branch it finds itself on. It must run once, inside the new
#           worktree, after the create.
#   refuse  The same script refuses, because a live session holds the path.
#           The skill must report it and stop: no retry, no second session
#           number, and the new branch and worktree kept.
#   none    claim_command: none. The skill must run nothing.
#
# A file remote (offline), one earlier session log (session 6), and one live
# session branch, feature/session-7-other, pushed and holding a claim on src/.
# So a correct run mints 8. Prints the repo path on stdout (last line).
set -e

MODE=${1:-claim}
case "$MODE" in claim|refuse|none) ;; *) echo "unknown mode: $MODE" >&2; exit 2 ;; esac

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/lck-claim.XXXXXX")
REMOTE="$ROOT/remote.git"
REPO="$ROOT/repo"

git init --bare -q "$REMOTE"
git init -q "$REPO"
cd "$REPO"
git config user.email bench@example.com
git config user.name Bench
git remote add origin "$REMOTE"
echo ".claude/worktrees/" >> .git/info/exclude   # worktree_ignore

if [ "$MODE" = none ]; then CLAIM='none'; else CLAIM='"sh tools/claim.sh"'; fi

mkdir -p .claude sessions tools src
cat > .claude/lifecycle-manifest.md <<EOF
\`\`\`yaml
product_name: benchwidget
remote: origin
integration_ref: origin/main
local_main: main
pr_base: main
requires_remote: true
branch_pattern: "feature/session-{n}-{topic}"
branch_glob: "feature/*"
docs_log_branch: "docs/session-{n}-log"
worktree_dir: .claude/worktrees
worktree_pattern: "session-{n}-{topic}"
worktree_ignore: .git/info/exclude
claim_command: $CLAIM
log_dir: sessions
log_index: none
log_pattern: "{date}_session_{n}[_{suffix}].md"
log_glob: "sessions/[0-9]*_session*.md"
log_presence_regex: '^sessions/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_session.*\.md$'
code_globs: ["src/*"]
build_commands: [true]
test_commands: [true]
merge_strategy: merge
issues_file: none
plan_doc: none
\`\`\`
EOF

# The claim script. Every call is logged (branch and toplevel) in the common git
# dir, which every worktree shares and the agent's checkout never commits, so
# the assertion counts calls from outside the agent.
cat > tools/claim.sh <<'EOF'
#!/bin/sh
# Claim src/ for the current session branch.
common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
dir="$common/bench-claims"
mkdir -p "$dir"
br=$(git branch --show-current)
printf '%s %s\n' "$br" "$(git rev-parse --show-toplevel)" >> "$dir/calls.log"
holder=$(cat "$dir/src.holder" 2>/dev/null)
if [ -n "$holder" ] && [ "$holder" != "$br" ]; then
  echo "claim: src/ is held by $holder, which is live." >&2
  echo "claim: claim other paths, wait for $holder to merge, or ask its holder to release src/." >&2
  exit 1
fi
echo "$br" > "$dir/src.holder"
echo "$br claims: src/"
EOF

echo "# bench" > README.md
echo "x = 1" > src/app.py
printf '# Session 6\n\n## What'"'"'s next\n\n- More of src/.\n' > sessions/2026-10-01_session_6.md
git add -A
git commit -qm "chore: init"
git branch -M main
git push -q -u origin main

# A live concurrent session: its branch on the remote, and in refuse mode its
# claim on src/.
git branch feature/session-7-other main
git push -q origin feature/session-7-other
if [ "$MODE" = refuse ]; then
  mkdir -p .git/bench-claims
  echo feature/session-7-other > .git/bench-claims/src.holder
fi

{
  echo "scenario repo: $REPO (mode $MODE)"
  echo "expected session number: 8"
} >&2
echo "$REPO"
