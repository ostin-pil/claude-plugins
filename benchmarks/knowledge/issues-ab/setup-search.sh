#!/bin/sh
# Fixture for the `issues search` A/B. The query term "thermal throttling" appears
# only in a session log, not in any tracker entry. ISS-207's tracker entry uses
# generic words ("audio dropout under sustained load"); the session log is what
# ties that symptom to "thermal throttling". The skill's search greps the tracker
# AND the session logs, so it surfaces ISS-207; a control that searches only the
# tracker finds nothing. Ground truth: does the agent's report cite ISS-207.
#
# Prints the repo path on stdout (last line).
set -e

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/issues-search.XXXXXX")
REPO="$ROOT/repo"
mkdir -p "$REPO/knowledge/decisions" "$REPO/.claude" "$REPO/sessions"
cd "$REPO"
git init -q
git config user.email bench@example.com
git config user.name Bench

cat > .claude/lifecycle-manifest.md <<'EOF'
```yaml
product_name: benchwidget
issues_file: knowledge/decisions/issues.md
log_dir: sessions
```
EOF

cat > knowledge/decisions/issues.md <<'EOF'
<!-- prose-check: skip bold-colon-opener -->
# Issues

## ISS-205: Hotkey conflicts with system shortcut
**Session**: 40 | **Date**: 2026-05-20 | **Status**: Open

**Symptom**: The capture hotkey collides with a macOS default.

**Files**: src/hotkey.swift

## ISS-206: Settings checkbox state not persisted
**Session**: 41 | **Date**: 2026-05-24 | **Status**: Resolved

**Symptom**: Toggling a setting did not survive relaunch.

**Files**: src/settings.swift

## ISS-207: Audio dropout under sustained load
**Session**: 42 | **Date**: 2026-05-29 | **Status**: Open

**Symptom**: After several minutes of continuous dictation, audio frames start
dropping and the transcript stalls.

**Root Cause**: Under investigation.

**Files**: src/audio.swift
EOF

# The session log is the only place the symptom is tied to the query term.
cat > sessions/2026-05-29_session_42_audio.md <<'EOF'
# Session 42

## What happened
- Reproduced the long-session audio dropout (ISS-207). Instrumented the capture
  thread and found the dropouts coincide with CPU thermal throttling on sustained
  load: once the package hits the thermal limit the audio callback misses its
  deadline. So ISS-207 is a thermal throttling problem, not a buffer-size bug.
EOF

git add -A
git commit -qm "tracker + a log that ties ISS-207 to thermal throttling"

{
  echo "scenario repo: $REPO"
  echo "query 'thermal throttling' -> ISS-207, findable only via the session log"
} >&2
echo "$REPO"
