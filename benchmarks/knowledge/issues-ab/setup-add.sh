#!/bin/sh
# Build a throwaway repo with a populated issue tracker, so the `issues` add A/B
# has a known ground truth. Plants ISS-001..005 in the skill's canonical format,
# a manifest pointing at the tracker, and two session logs. The agent is asked to
# add one new issue; a correct add preserves all five originals, uses the next
# sequential id (ISS-006), and matches the entry schema.
#
# Prints the repo path on stdout (last line). Diagnostics to stderr.
set -e

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/issues-ab.XXXXXX")
REPO="$ROOT/repo"
mkdir -p "$REPO/knowledge/decisions" "$REPO/sessions" "$REPO/.claude"
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

## ISS-001: Hotkey double-fires on rapid press
**Session**: 12 | **Date**: 2026-03-02 | **Status**: Resolved

**Symptom**: Pressing the global hotkey twice quickly triggered two captures.

**Root Cause**: No debounce on the key handler.

**Fix**: Added a 150ms debounce window.

**Commit**: `a1b2c3d`

**Files**: Hotkey/HotkeyManager.swift

## ISS-002: Overlay flickers on first show
**Session**: 18 | **Date**: 2026-03-20 | **Status**: Resolved

**Symptom**: The overlay panel flashed black before the blur applied.

**Root Cause**: The visual-effect view was added after the panel was ordered front.

**Fix**: Build the view tree before ordering front.

**Files**: Window/OverlayPanel.swift

## ISS-003: Mic permission prompt never appears
**Session**: 21 | **Date**: 2026-04-01 | **Status**: Resolved (verify)

**Symptom**: First-run users never saw the microphone prompt.

**Root Cause**: Capture started before the usage description was registered.

**Fix**: Request authorization explicitly on first capture.

**Files**: Audio/MicCapture.swift

## ISS-004: Transcript drops the last word
**Session**: 27 | **Date**: 2026-04-19 | **Status**: Open

**Symptom**: The final word is occasionally missing from the inserted text.

**Root Cause**: The audio buffer is flushed before the recognizer finishes.

**Fix**: (unresolved)

**Files**: Transcription/Recognizer.swift

## ISS-005: Settings window opens off-screen on external display
**Session**: 33 | **Date**: 2026-05-08 | **Status**: Open

**Symptom**: With a second monitor unplugged, Settings opens at saved coords off-screen.

**Root Cause**: Saved frame is not clamped to visible screens.

**Fix**: (unresolved)

**Files**: Settings/SettingsWindow.swift
EOF

printf '# Session 33\n\n## Decisions worth remembering\n- deferred the off-screen clamp (ISS-005)\n' \
  > sessions/2026-05-08_session_33_settings.md
printf '# Session 27\n\n## What happened\n- triaged the dropped-word bug (ISS-004)\n' \
  > sessions/2026-04-19_session_27_transcription.md

git add -A
git commit -qm "repo with populated issue tracker"

{
  echo "scenario repo: $REPO"
  echo "tracker: knowledge/decisions/issues.md (ISS-001..005)"
} >&2
echo "$REPO"
