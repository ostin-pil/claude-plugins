# Code Health Audit, 2026-04-14 (run 3, tuned skill)

**Branch**: main
**Commit**: 27341e0
**Focus**: broad sweep (second skill-driven run, post-tune)
**Coverage**: 19 of 19 in-scope Swift files opened

## Critical

- `Untype/App/RecordingCoordinator.swift:13`, no `deinit` cancelling `transcriptionTask` / `graceTask`. *Fix:* add `deinit { transcriptionTask?.cancel(); graceTask?.cancel() }`.
- `Untype/App/AppDelegate.swift:17`, no `deinit` cancelling `phaseObservationTask` or invalidating `onboardingTimer`. *Fix:* add `deinit` that cancels both.
- `Untype/App/AppDelegate.swift:9`, IUO `menuBar` assigned in `applicationDidFinishLaunching` with no guard. *Fix:* optional + guard.
- `Untype/App/AppDelegate.swift:10`, IUO `overlayController` lacks nil-safety. *Fix:* optional.
- `Untype/App/AppDelegate.swift:11`, IUO `fnMonitor` lacks nil-safety. *Fix:* optional.
- `Untype/App/AppDelegate.swift:12`, IUO `keyboardHandler` lacks nil-safety. *Fix:* optional.
- `Untype/App/AppDelegate.swift:13`, IUO `recordingCoordinator` lacks nil-safety. *Fix:* optional.
- `Untype/App/AppDelegate.swift:14`, IUO `processingCoordinator` lacks nil-safety. *Fix:* optional.
- `Untype/App/AppDelegate.swift:15`, IUO `permissionsCoordinator` lacks nil-safety. *Fix:* optional.
- `Untype/Window/FocusedElementLocator.swift:31`, force-cast `as! AXUIElement`. *Fix:* `guard let … as? AXUIElement`.
- `Untype/Window/FocusedElementLocator.swift:60`, force-cast `as! AXValue`. *Fix:* optional cast.
- `Untype/App/MenuBarController.swift:9`, IUO `statusItem` assigned in `start()`; re-entrant call unsafe. *Fix:* optional + guard.
- `Untype/App/RecordingCoordinator.swift:65`, `Task` without `[weak self]`; retain cycle risk. *Fix:* add capture list.
- `Untype/App/RecordingCoordinator.swift:130`, same. *Fix:* `[weak self]`.
- `Untype/App/RecordingCoordinator.swift:185`, same, inside level-monitoring callback. *Fix:* `[weak self]`.
- `Untype/App/RecordingCoordinator.swift:203`, same, in `stopLevelMonitoring`. *Fix:* `[weak self]`.

## Medium

- `Untype/App/PermissionsCoordinator.swift:74`, 1Hz permission poll never escalates to event-driven once granted. *Fix:* stop or back off after first `allGranted`.
- `Untype/Processing/ProcessingCoordinator.swift:45`, `activeTask` reassigned without confirming prior is fully released. *Fix:* await cancellation before overwrite.
- `Untype/Window/OverlayController.swift:11`, `NSHostingView` embedded directly in coordinator creates tight SwiftUI/AppKit coupling. *Fix:* extract a measurement helper.

## Minor

- `Untype/Transcription/AppleSpeechService.swift:26`, force-unwrap of en-US fallback recognizer. *Fix:* throw or surface init error.
- `Untype/Window/OverlayPanel.swift:42`, nil-screen fallback positions the panel at an arbitrary spot. *Fix:* log/assert.

## Clean

- No Combine usage
- No XIBs/storyboards
- No debug artifacts (`print`, `NSLog`, `/tmp/untype`)
- No dependencies beyond HotKey
- No AppKit leaking into SwiftUI views
- Proper `[weak self]` and deinit in `AudioRecorder`, `FnPushToTalkMonitor`, `KeyboardHandler`, `PermissionsCoordinator`
- No swallowed errors
- No unbounded polling past success (except the one Medium item above)
