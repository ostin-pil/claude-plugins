# Code Health Audit, 2026-04-14 (run 4, tuned skill v2)

**Branch**: main
**Commit**: 7fdf69e
**Focus**: broad sweep
**Coverage**: 27 of 27 in-scope Swift files opened (now including UntypeCore)

## Critical

- `Untype/Window/FocusedElementLocator.swift:31,60,81,82`, four `as!` force-casts on AX values with no validation. *Fix:* `guard let … as?` or document the API invariant.
- `Untype/App/RecordingCoordinator.swift:115`, `graceTask` not cancelled in a `deinit`. *Fix:* `deinit { graceTask?.cancel() }`.
- `Untype/App/RecordingCoordinator.swift:130`, `transcriptionTask` not cancelled in a `deinit`. *Fix:* `deinit { transcriptionTask?.cancel() }`.
- `Untype/App/AppDelegate.swift:200`, `phaseObservationTask` not cancelled in a `deinit`. *Fix:* cancel in deinit alongside `onboardingTimer`.

## Medium

- `Untype/App/RecordingCoordinator.swift:1`, file is 208 lines, over the 200-line rule. *Fix:* split into smaller files by responsibility (extract level monitoring).
- `Untype/App/AppDelegate.swift:1`, file is 225 lines, over the 200-line rule. *Fix:* split (move phase observation and onboarding into dedicated coordinators).
- `Untype/App/RecordingCoordinator.swift:182`, 50ms (20Hz) level timer allocates a `Task { @MainActor }` every tick. *Fix:* drop the Task wrapper, the main-run-loop timer already runs on main.
- `Untype/App/RecordingCoordinator.swift:120`, 20ms poll timer body allocates a Task every tick. *Fix:* collapse the allocation or raise the interval.
- `Untype/App/PermissionsCoordinator.swift:74`, 1Hz permissions poll allocates a Task per tick and never backs off after `allGranted`. *Fix:* stop the timer on success.

## Minor

- `Untype/Transcription/AppleSpeechService.swift:26`, force-unwrap of en-US fallback `SFSpeechRecognizer`. *Fix:* throw/surface init error.
- `Untype/App/MenuBarController.swift:9`, IUO `statusItem` assigned in `start()`; re-entrant call unsafe. *Fix:* optional + guard, or lazy init.

## Clean

- No Combine usage
- No storyboards/XIBs
- No AppKit types leaking into SwiftUI views
- No dependencies beyond HotKey (verified across Untype/ and UntypeCore/)
- No debug artifacts (`print`, `NSLog`, `/tmp/untype`)
- Proper `deinit` cleanup in `AudioRecorder`, `FnPushToTalkMonitor`, `KeyboardHandler`, `PermissionsCoordinator`, `ProcessingCoordinator`
- No swallowed errors
- No `@Observable` off-main mutation found
- `UntypeCore` library code (Processing/, Settings/) passes all checks

## Phase 3 hot-path sweep (from working notes)

```
TIMER AppDelegate.swift:144           interval=3000ms  body-allocates-task=NO
TIMER PermissionsCoordinator.swift:74 interval=1000ms  body-allocates-task=YES
TIMER RecordingCoordinator.swift:182  interval=50ms    body-allocates-task=YES
TIMER RecordingCoordinator.swift:120  interval=20ms    body-allocates-task=YES
TIMER FnPushToTalkMonitor.swift:110   interval=200ms   body-allocates-task=NO
```
