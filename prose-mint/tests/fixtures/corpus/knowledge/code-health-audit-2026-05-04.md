# Code Health Audit, 2026-05-04

- Branch: main
- Commit: abb6a943c71c7d0c6274a2410e86fffd572ac250
- Focus: post-cutover refresh; prior audit 2026-04-30 substantially resolved
- In-scope files: 89 opened of 89 total

## Critical

- `Untype/App/PermissionsChecker.swift:47,55,63`, Three force-unwraps of dynamically-constructed system preferences URLs. String parsing can fail; recover gracefully with optional construction and error handling. *Fix:* use `URL(string:)` returning optional; provide fallback or return error if nil.
- `Sources/UntypeCore/Processing/CloudProviderConfig.swift:90`, Force-unwrap of fallback Ollama URL after primary parse failure. If both parse fails (invalid hardcoded default), crash. *Fix:* use optional; throw or return a clear error when no valid URL can be constructed.
- `Sources/UntypeCore/Voxtral/VoxtralReasonerAdapter+Networking.swift:11`, Static force-unwrap of hardcoded endpoint URL. If the literal URL ever becomes malformed (rare, but in version control), the app crashes at module load. *Fix:* validate at runtime in a lazy static computed property; throw on invalid URL.

## Medium

- `Sources/UntypeCore/Transcription/AppleSpeechService.swift:1`, File is 256 lines, exceeds 200-line rule. *Fix:* extract recognition result handling (lines 165–234) into a separate delegate type; move `cleanup()` and related helpers into an extension.
- `Sources/UntypeCore/Processing/AppContext.swift:1`, File is 223 lines, exceeds 200-line rule. *Fix:* extract `ContextProfile` into its own file (Untype/Processing/ContextProfile.swift); split `AppContext` methods by concern.
- `Sources/UntypeCore/Processing/CloudProviderConfig.swift:1`, File is 257 lines, exceeds 200-line rule (bench-read). *Fix:* extract wire types (ChatCompletionRequest, OutboundMessage, etc.) to CloudProviderWireTypes.swift; move system-prompt assembly to a dedicated helper struct.
- `Untype/Window/BarView.swift:1`, File is 205 lines, exceeds 200-line rule. *Fix:* extract statusIndicator and recordingHintView helpers to a new StatusIndicatorView.swift file.
- `Untype/App/MenuBarController.swift:96`, `makeKeyAndOrderFront(nil)` violates AppKit rule (should use `orderFront(nil)` or `orderFrontRegardless()`). Non-key windows should not activate. *Fix:* change to `settingsWindow?.orderFront(nil)` to avoid stealing focus from the target app.
- `Untype/App/RecordingCoordinator+Lifecycle.swift:106`, `graceTask` polling loop (lines 106–117), 20ms sleep in a while loop. If cancellation arrives mid-poll, the audio engine tap is left active. *Fix:* wrap the loop in a defer that unconditionally cleans up resources; or use a cancellation-aware timer instead of polling.
- `Untype/Audio/AudioRecorder.swift:37`, Tap callback silently swallows `file.write()` errors (line 37). If disk is full mid-recording, the audio buffer doesn't persist. Non-fatal, but silent failure could lead to data loss. *Fix:* add `try?` error logging so operator knows write failed; or raise an exception to halt recording.
- `Untype/Processing/ProcessingCoordinator+Stream.swift:21`, `Task { @MainActor in ... }` at line 22 (transcriptionTask), fire-and-forget task without stored cancellation reference until assignment. If the coordinator is deallocated before assignment completes, the task may continue running on a dangling coordinator. *Fix:* store in `nonisolated(unsafe) var` immediately, or use a completion handler pattern to avoid task lifetime surprise.

## Minor

- `Untype/App/AppRouterBuilder.swift:46–56`, Catch block swallows cloud-provider construction errors and falls back to local-only. The fallback is intentional, but no logging of the failure. *Fix:* add a debug log explaining which provider failed so operator can diagnose configuration issues.
- `Untype/App/RecordingCoordinator+Stream.swift:40–43`, `levelMonitor.stop()` is called in the stream handler after the recognizer yields final text. If the task is cancelled mid-yield, stop may not run. *Fix:* move the stop call into a defer block so it runs regardless of cancellation.
- `Untype/Window/OverlayPanel.swift:53`, `setFrame(..., animate: animate)` can be called frequently during `.polishing` phase (per-token updates). The animation flag is false when phase didn't change, but setting bounds many times per second may still cost layout thrashing. *Fix:* add a throttle check (only update if frame changed by >1pt) to reduce Core Animation overhead.

## Clean

- No Combine usage, all async/await
- No storyboards or XIBs
- No dependencies beyond HotKey
- AppKit types properly isolated (Window/ and Coordinator classes, no AppKit imports in SwiftUI views)
- All in-scope .swift files audited (89 opened)
- No fire-and-forget `Task {}` without `[weak self]` capture (checked all 21 Task sites)
- No swallowed errors in critical paths (error handling is explicit or fallback is documented)
- No NSLog or debug print() statements left in production code
- @Observable used consistently; no ObservableObject/Published
- No @unknown default cases missed in switch statements
- No concurrent mutation of AppState outside dispatch() and resetAuxiliary()
- No `as!` force-casts on untrusted AX data (AXBridging.swift centralizes the pattern after type-id checks)
- AppDelegate Task lifetime properly managed (phaseObservationTask cancelled in deinit)
- All three force-unwraps from prior audit (ContextDetector, FocusedElementLocator) have been replaced or documented as safe
- Per-stage provider registry and dual-conformant STT stages (Voxtral, AppleFM) correctly route through short-circuit and explicit polishing paths
- Hallucination filter and thread-context readers properly integrated without state leaks
- Keychain access centralized in KeychainStore; no plaintext API keys stored in UserDefaults
