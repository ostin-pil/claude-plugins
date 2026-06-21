#!/bin/sh
# Build a throwaway repo with a controlled knowledge base, so knowledge-audit's
# three checks have a known ground truth. Plants:
#   - two orphaned knowledge docs (nothing references them),
#   - one stale doc (added in a backdated commit, never touched since),
#   - one unpromoted session log (its session number appears nowhere under
#     knowledge/), alongside a promoted one and one with no decisions section.
# Everything else is referenced / fresh / promoted, so it must NOT be flagged.
# Prints the repo path on stdout. Expected flags are in expected.json.
set -e

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/kaudit.XXXXXX")
REPO="$ROOT/repo"
mkdir -p "$REPO"
cd "$REPO"
git init -q
git config user.email bench@example.com
git config user.name Bench

mkdir -p knowledge/decisions knowledge/design sessions

# Entry point that links two docs by markdown link (those are referenced).
cat > knowledge/README.md <<'EOF'
# Knowledge

- [design note](design/cited.md)
- [open decisions](decisions/open-decisions.md)
EOF

echo "# a design note" > knowledge/design/cited.md
cat > knowledge/decisions/open-decisions.md <<'EOF'
# Open decisions

OD-001: keep the widget cache warm. Promoted from session 50.
EOF

echo "# orphan one"   > knowledge/decisions/orphan-a.md
echo "# orphan two"   > knowledge/orphan-b.md
echo "# old but cited" > knowledge/old-stale.md

# Session logs.
cat > sessions/2026-06-10_session_50_alpha.md <<'EOF'
# Session 50

## Decisions worth remembering
- chose X over Y because Z
EOF

cat > sessions/2026-06-11_session_51_beta.md <<'EOF'
# Session 51

## Decisions worth remembering
- adopted approach Q for reason R

See `knowledge/old-stale.md` for context.
EOF

cat > sessions/2026-06-12_session_52_gamma.md <<'EOF'
# Session 52

## What happened
- routine work, nothing worth promoting
EOF

# Old, backdated commit for old-stale.md only, so its last commit is far in the
# past and it reads as stale; it is still cited by session 51, so not an orphan.
git add knowledge/old-stale.md
GIT_AUTHOR_DATE="2026-01-01T12:00:00" GIT_COMMITTER_DATE="2026-01-01T12:00:00" \
  git commit -qm "add old-stale doc"

# Recent commit (now) for everything else.
git add -A
git commit -qm "knowledge base + sessions"

echo "$REPO"
