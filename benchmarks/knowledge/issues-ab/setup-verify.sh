#!/bin/sh
# Fixture for the `issues verify` A/B. Plants four "Resolved (verify)" issues, each
# naming a Fix marker and a referenced file. Two markers are still present in their
# file (the fix held -> should become Resolved), two are gone (the fix was reverted
# -> should become Regressed). Two non-target issues (Open, Resolved) must not
# change. The skill's verify procedure is: find the Resolved (verify) issues, check
# the referenced files, transition to Resolved or Regressed. A naive control must
# infer to read the files and to use the project's "Regressed" status word.
#
# Prints the repo path on stdout (last line). Expected transitions are hard-coded
# in assert-verify.py.
set -e

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/issues-verify.XXXXXX")
REPO="$ROOT/repo"
mkdir -p "$REPO/knowledge/decisions" "$REPO/.claude" "$REPO/src"
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

# Referenced files. Markers present => fix held; absent => regressed.
echo 'func handleHotkey() { scheduleDebounce(150); capture() }' > src/hotkey.swift   # ISS-101 marker PRESENT
echo 'func showOverlay() { panel.orderFront(nil); addBlurView() }' > src/overlay.swift # ISS-102 marker buildViewTree() ABSENT
echo 'func startCapture() { requestAuthorization(); beginTap() }' > src/audio.swift    # ISS-103 marker PRESENT
echo 'func restoreFrame() { window.setFrame(saved) }' > src/insert.swift               # ISS-104 marker clampToVisibleScreens() ABSENT

cat > knowledge/decisions/issues.md <<'EOF'
<!-- prose-check: skip bold-colon-opener -->
# Issues

## ISS-101: Hotkey double-fires on rapid press
**Session**: 12 | **Date**: 2026-03-02 | **Status**: Resolved (verify)

**Symptom**: Pressing the global hotkey twice quickly triggered two captures.

**Root Cause**: No debounce on the key handler.

**Fix**: Added a debounce guard `scheduleDebounce(150)` in the handler.

**Files**: src/hotkey.swift

## ISS-102: Overlay flickers on first show
**Session**: 18 | **Date**: 2026-03-20 | **Status**: Resolved (verify)

**Symptom**: The overlay panel flashed before the blur applied.

**Root Cause**: The blur view was added after the panel was ordered front.

**Fix**: Build the view tree before ordering front via `buildViewTree()`.

**Files**: src/overlay.swift

## ISS-103: Mic permission prompt never appears
**Session**: 21 | **Date**: 2026-04-01 | **Status**: Resolved (verify)

**Symptom**: First-run users never saw the microphone prompt.

**Root Cause**: Capture started before authorization was requested.

**Fix**: Request mic access on first capture with `requestAuthorization()`.

**Files**: src/audio.swift

## ISS-104: Settings window opens off-screen
**Session**: 33 | **Date**: 2026-05-08 | **Status**: Resolved (verify)

**Symptom**: With a monitor unplugged, Settings opened off-screen.

**Root Cause**: The saved frame was not clamped to visible screens.

**Fix**: Clamp the saved frame via `clampToVisibleScreens()`.

**Files**: src/insert.swift

## ISS-105: Transcript drops the last word
**Session**: 27 | **Date**: 2026-04-19 | **Status**: Open

**Symptom**: The final word is occasionally missing.

**Root Cause**: The audio buffer is flushed before the recognizer finishes.

**Fix**: (unresolved)

**Files**: src/audio.swift

## ISS-106: Menu bar icon wrong in dark mode
**Session**: 30 | **Date**: 2026-04-28 | **Status**: Resolved

**Symptom**: The template icon rendered solid black in dark mode.

**Root Cause**: The image was not marked as a template.

**Fix**: Set `isTemplate = true` on the status item image.

**Files**: src/menu.swift
EOF

printf '# Session 33\n\n## What happened\n- routine triage\n' > /dev/null
mkdir -p sessions
printf '# Session 30\n\n## Decisions worth remembering\n- marked the menu icon template (ISS-106)\n' \
  > sessions/2026-04-28_session_30_menu.md

git add -A
git commit -qm "repo with resolved-verify issues + referenced files"

{
  echo "scenario repo: $REPO"
  echo "verify targets: ISS-101 (hold), ISS-102 (regressed), ISS-103 (hold), ISS-104 (regressed)"
} >&2
echo "$REPO"
