# Code Health Audit, 2026-04-30

> **2026-05-04 update:** Substantially resolved. AppDelegate IUOs converted to optionals; the three Critical AX force-casts fixed via `axBridge*` helpers (commits `39f5c2d`, `35dda7c`, `fcad6dc`); all four Medium file-size violations refactored (RecordingCoordinator 332-to-109, AppDelegate 234-to-136, ProcessingCoordinator 224-to-97, BarView 211-to-205). See `code-health-audit-2026-05-04.md` for the post-cutover refresh.

- Branch: main
- Commit: aa6d528
- Focus: post-AppStateReducer cutover
- In-scope files: 37 opened of 37 total

## Critical

- `Untype/App/AppDelegate.swift:9-16`, Eight IUO stored properties on AppDelegate that must be assigned in `applicationDidFinishLaunching`. If any assignment fails or is skipped, access will trap. *Fix:* validate each assignment or use optional with explicit nil-checks; confirm all eight are always assigned before any other method is called.
- `Untype/Processing/ContextDetector.swift:94`, Force-cast `windowObj as! AXUIElement` after only checking `CFGetTypeID == AXUIElementGetTypeID()`. If the type check passes but the cast fails (impossible in theory, but CF bridging can be fragile), crash. *Fix:* use `as? AXUIElement` and handle nil.
- `Untype/Window/FocusedElementLocator.swift:32,84,85`, Three force-casts of AX values checked only by `CFGetTypeID` comparison. If bridging fails mid-call, crash. *Fix:* use optional casts and handle nil gracefully.

## Medium

- `Untype/App/RecordingCoordinator.swift:1`, File is 332 lines, exceeds 200-line rule. *Fix:* split by responsibility: move transcriberFactory/speech-permission logic to TranscriberLifecycle; move stream handlers to TranscriptionStreamHandler.
- `Untype/App/AppDelegate.swift:1`, File is 234 lines, exceeds 200-line rule. *Fix:* extract effect handler (lines 56–69) and profile override logic (lines 174–179) to a new EffectCoordinator; extract phase observation (lines 209–224) to PhaseObserver.
- `Untype/Processing/ProcessingCoordinator.swift:1`, File is 224 lines, exceeds 200-line rule. *Fix:* split stream consumption (lines 103–182) into a new StreamConsumer helper; move error mapping to ErrorMapper.
- `Untype/Window/BarView.swift:1`, File is 211 lines, exceeds 200-line rule. *Fix:* extract reviewingBody builder and its helpers into ReviewingBodyBuilder; extract AppError extension into AppErrorView.
- `Untype/App/ContextCaptureCoordinator.swift:52`, Force-cast after type check: `(value as! AXUIElement)`. *Fix:* use optional cast; return nil on failure instead of crashing.
- `Untype/App/AppDelegate.swift:183,190,209`, Three fire-and-forget `Task { @MainActor ... }` with no stored reference. Lines 183/190 are brief; line 209 is `phaseObservationTask` (stored). First two could be awaited in a parent async context instead of fire-and-forget. *Fix:* hoist into stored tasks if cancellation is needed; document why fire-and-forget is safe if kept.
- `Untype/Audio/AudioLevelMonitor.swift:38–54`, Timer closure uses `Timer(timeInterval:repeats:block:)` initialized in `start()` but the timer must be invalidated in `deinit`. Proper, but docstring at line 8 claims "no allocation per tick", verify `MainActor.assumeIsolated` truly avoids task allocation. *Fix:* confirm via profiling; if a Task is being allocated despite `assumeIsolated`, switch to a dedicated callback pattern.
- `Untype/Processing/ProcessingCoordinator.swift:33`, `flushInterval = .milliseconds(33)` (~30Hz polling via explicit dispatch). During polishing, `.polishingPartial` dispatches on a 33ms cadence (line 138–141). If this is allocated as a Task per tick, it's a problem. Current code dispatches via `appState.dispatch()` which doesn't allocate Tasks; safe. But verify no intermediate Task wrapping occurs. *Fix:* audit the call chain from dispatch to reducer to ensure no Task allocation per tick.
- `Untype/App/RecordingCoordinator.swift:206`, `graceTask` created as `Task { @MainActor [weak self] ...}` with a `while` loop polling `finalTranscriber?.finalText` every 20ms for up to 300ms. Polling is bounded, so the issue is containment: if the task is cancelled mid-poll, cleanup is skipped. *Fix:* ensure `stopRecordingWithGrace()` explicitly cancels and clears `graceTask` before exiting.
- `Untype/App/PermissionsCoordinator.swift:74`, 1-second polling timer started in `startPolling()`. Runs until `allGranted`, then stopped. Timer is properly invalidated in deinit. However, line 75 calls `evaluate()` which may set `appState.phase = .setup(...)`, direct mutation. *Fix:* dispatch `.setupShown` event instead of direct mutation at line 61.

## Minor

- `Untype/App/AppRouterBuilder.swift:53,54`, Empty catch blocks swallow errors. On failure, logs to debug level and falls back to `.localOnly`. Silent failures are intentional (fallback strategy), but add a `catch {}` comment explaining the fallback. *Fix:* add `// Fallback to local-only on any build failure` before the catch.
- `Untype/App/RecordingCoordinator.swift:155`, Catch block at line 155 logs errors and dispatches `.recordingStartFailed` but doesn't reset `audioRecorder.onBuffer`. Lines 157–158 do reset it; code is correct but fragile. *Fix:* extract onBuffer teardown into a helper called in both the success and error paths.
- `Untype/Processing/ProcessingCoordinator.swift:174`, Catch block for untyped `Error` (line 174–180) dispatches `.providerUnavailable(reason:)`. Non-fatal, but confirm error messages are user-facing-safe (no secrets in description). *Fix:* audit error descriptions; if any sensitive info leaks (API endpoint, internal ID), sanitize.
- `Untype/Window/OverlayPanel.swift:96`, call to `makeKeyAndOrderFront(nil)` at line 96 in MenuBarController. AppKit rule forbids this for non-key panels; OverlayPanel correctly forbids key status. But MenuBarController's settingsWindow is a regular NSWindow that DOES call `makeKeyAndOrderFront`. *Fix:* ensure settingsWindow uses `orderFrontRegardless()` or explicitly sets level+policy to avoid stealing focus from the app.
- `Untype/Processing/ProcessingCoordinator.swift:18`, Comment references `NSHostingView.fittingSize`, but this class doesn't use NSHostingView; that's in OverlayController. *Fix:* move or update comment to the right file.
- `Untype/App/AppRouterBuilder.swift:36–55`, Overload `build(settingsProviderId:envProviderId:)` is documented as a test seam but is public; non-test code could call it directly, bypassing intent. *Fix:* mark `private` or fileprivate if only tests use it; ensure tests import the function correctly.
- `Untype/Audio/AudioRecorder.swift:37`, `try? file.write(from:buffer)` swallows errors silently in the hot-path AVAudioEngine tap callback. If disk is full or file permission fails, recording continues with partial data. Non-fatal (fallback is to stop and use what was buffered), but document why. *Fix:* add comment explaining partial-write fallback strategy.

## Clean

- no Combine usage
- no storyboards or XIBs
- no dependencies beyond HotKey
- AppKit types properly isolated (Window/ and Coordinator classes, SwiftUI views reference only AppState)
- all 37 in-scope .swift files use async/await (no hand-rolled callbacks except NSEvent monitors, which are necessary)
- @Observable used consistently for state-holding classes (AppState, SettingsStore, RecordingCoordinator, AudioRecorder)
- AppDelegate properly manages Task lifetimes (phaseObservationTask cancelled in deinit)
- Reducer-state mutations confined to AppState.dispatch(), AppStateReducer.reduce(), and AppState.resetAuxiliary()
- AppEvent and AppEffect surfaces are comprehensive and all effects are wired (runPolishing via AppDelegate.onEffect)
- No NSLog or print() statements left behind
- No @unknown default cases missed (AudioPermissions.swift:15 correctly handles)
