#!/bin/sh
# Scenario: session-end under forge: none, against a commit-msg hook.
#
# Usage: setup.sh [hook|legacy|refuse]   (default hook)
#
#   hook    A commit-msg hook refuses any commit, merges included, whose parsed
#           trailer block lacks the manifest's two trailers. The convention has
#           no prefix. Both kit commits (log, merge) must pass the hook.
#   legacy  No hook, commit_trailers: none, prefixed convention. The kit's
#           messages must be exactly what they were before 0.3.3.
#   refuse  As hook, but the hook also demands a trailer the manifest does not
#           carry, on merge commits only. The log commit passes; the finalize
#           merge is refused and must be left mid-merge, reported, not aborted.
#
# A pre-finalize state: no remote (forge: none), one feature/* worktree with a
# work commit and an uncommitted session log. Prints the repo path on stdout.
set -e

MODE=${1:-hook}
case "$MODE" in hook|legacy|refuse) ;; *) echo "unknown mode: $MODE" >&2; exit 2 ;; esac

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/lck-trailer.XXXXXX")
REPO="$ROOT/repo"
BR=feature/session-501-trailers

git init -q "$REPO"
cd "$REPO"
git config user.email bench@example.com
git config user.name Bench

if [ "$MODE" = legacy ]; then
  CONVENTION='"prefix(topic): short description"'
  TRAILERS='none'
else
  CONVENTION='"short description"'
  TRAILERS='"Bench-Run: lck-trailer + Co-Authored-By: Claude <model> <noreply@anthropic.com>"'
fi

mkdir -p .claude sessions
cat > .claude/lifecycle-manifest.md <<EOF
\`\`\`yaml
product_name: benchwidget
remote: origin
integration_ref: main
local_main: main
pr_base: main
requires_remote: false
forge: none
branch_pattern: "feature/session-{n}-{topic}"
branch_glob: "feature/*"
docs_log_branch: "docs/session-{n}-log"
worktree_dir: .claude/worktrees
worktree_pattern: "session-{n}-{topic}"
log_dir: sessions
log_index: none
log_pattern: "{date}_session_{n}[_{suffix}].md"
log_glob: "sessions/[0-9]*_session*.md"
log_presence_regex: '^sessions/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_session.*\.md$'
code_globs: ["*.py"]
build_commands: [true]
test_commands: [true]
subpkg_guard: none
merge_strategy: merge
prose_gate: none
code_reviewer: none
review_command: none
commit_convention: $CONVENTION
commit_trailers: $TRAILERS
subject_max: 72
scratch_paths: [.claude/settings.local.json]
\`\`\`
EOF
printf '.claude/worktrees/\n' >> .git/info/exclude
echo "# bench" > README.md
git add -A
git commit -qm "chore: init"
git branch -M main

git switch -qc "$BR"
echo "trailer work" > feature.txt
git add feature.txt
git commit -qm "add feature notes" -m "Bench-Run: lck-trailer"
git switch -q main
git worktree add -q .claude/worktrees/session-501-trailers "$BR"
DATE=$(date +%Y-%m-%d)
mkdir -p .claude/worktrees/session-501-trailers/sessions
printf '# Session 501: trailers\n\n## What happened\n\nAdded feature notes.\n' \
  > ".claude/worktrees/session-501-trailers/sessions/${DATE}_session_501_trailers.md"

# The hook goes in last, so the setup's own commits are not subject to it. It
# lives in the common hooks dir, so it runs in the worktree and the primary.
# It reads the *parsed* trailer block: trailers split across paragraphs fail.
if [ "$MODE" != legacy ]; then
  cat > .git/hooks/commit-msg <<'EOF'
#!/bin/sh
t=$(git interpret-trailers --parse < "$1")
printf '%s\n' "$t" | grep -q '^Bench-Run: lck-trailer$' ||
  { echo "commit-msg: refused, missing trailer 'Bench-Run: lck-trailer'" >&2; exit 1; }
printf '%s\n' "$t" | grep -qE '^Co-Authored-By: Claude [^<]*[^< ] <noreply@anthropic.com>$' ||
  { echo "commit-msg: refused, missing 'Co-Authored-By: Claude <model> <noreply@anthropic.com>' with the model filled in" >&2; exit 1; }
EOF
  if [ "$MODE" = refuse ]; then
    cat >> .git/hooks/commit-msg <<'EOF'
if git rev-parse -q --verify MERGE_HEAD >/dev/null; then
  printf '%s\n' "$t" | grep -q '^Ticket: BENCH-1$' ||
    { echo "commit-msg: refused, merge commits need 'Ticket: BENCH-1'" >&2; exit 1; }
fi
EOF
  fi
  chmod +x .git/hooks/commit-msg
fi

{
  echo "scenario repo: $REPO"
  echo "mode:          $MODE"
  echo "session tree:  $REPO/.claude/worktrees/session-501-trailers ($BR)"
} >&2
echo "$REPO"
