# Code Health Audit, 2026-04-14 (run 2, via /code-health-audit skill)

**Branch**: main
**Commit**: 4732251
**Focus**: broad sweep (first skill-driven run)

## Critical

- `Untype/App/RecordingCoordinator.swift:65`, Task created in `startRecording()` is not stored and cannot be cancelled on deinit. *Fix:* store in a `private var` and cancel in `deinit`.
- `Untype/Window/FocusedElementLocator.swift:55`, force-unwrap of `rangeValue!` after a guard that doesn't prove non-nil; will crash if AX returns success with nil value. *Fix:* use optional binding.
- `Untype/App/PermissionsCoordinator.swift:11`, no `deinit` to invalidate `pollTimer`; timer callback can fire after deallocation. *Fix:* `deinit { pollTimer?.invalidate() }`.
- `Untype/App/RecordingCoordinator.swift:1`, no `deinit` cancelling `graceTask`, `transcriptionTask`, `levelTimer`; leaks if coordinator is torn down mid-recording. *Fix:* add `deinit` that cancels all three.
- `Untype/Processing/ProcessingCoordinator.swift:1`, no `deinit` to cancel `activeTask`. *Fix:* `deinit { activeTask?.cancel() }`.

## Medium

- `Untype/App/RecordingCoordinator.swift:182`, 50ms level timer wraps each tick in `Task { @MainActor }` despite the timer already running on main. *Fix:* drop the Task wrapper, mutate `appState` directly.
- `Untype/App/AppDelegate.swift:179`, `insertAndDismiss()` spawns a fire-and-forget Task capturing `self` with no weak guard. *Fix:* store the task or use `[weak self]`.
- `Untype/Window/OverlayController.swift:14`, silent return if `panel.contentView` is nil; hosting view left unattached. *Fix:* log/assert.

## Minor

- `Untype/App/RecordingCoordinator.swift:203`, fire-and-forget cleanup Task in `stopLevelMonitoring()`. *Fix:* await or justify with a comment.
- `Untype/Transcription/AppleSpeechService.swift:26`, force-unwrap of the en-US fallback locale. *Fix:* provide a safer fallback or document the assumption.

## Clean

- No Combine usage
- No storyboards/XIBs
- No AppKit leaking into SwiftUI views
- No dependencies beyond HotKey (via `UntypeCore`)
- No debug artifacts (`NSLog`, `print`, `/tmp/untype_debug.log`)
- Good `[weak self]` discipline across 20+ closures
- Timer cleanup in `FnPushToTalkMonitor` and `KeyboardHandler` deinit
- Two files over the 200-line rule: `AppDelegate.swift` (225), `RecordingCoordinator.swift` (208), both borderline
