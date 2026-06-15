<!-- prose-check: skip bold-colon-opener -->
# Issue & Solution Tracker

Problems encountered during Untype development and how they were resolved.
Each entry includes: symptom, root cause, fix, and session reference.

---

## ISS-001: Duplicate Dock icon when running via `swift run`
**Session**: 14 | **Date**: 2026-04-10 | **Status**: Resolved

**Symptom**: App shows in Dock even though `LSUIElement = YES` is in Info.plist.

**Root Cause**: `swift run` launches a bare binary, macOS doesn't load Info.plist from the .app bundle, so `LSUIElement` is ignored.

**Fix**: Added `NSApplication.shared.setActivationPolicy(.accessory)` in `applicationDidFinishLaunching` as code-level fallback.

**Commit**: `18727ac`

---

## ISS-002: Permissions incorrectly flagged as missing on first launch
**Session**: 14 | **Date**: 2026-04-10 | **Status**: Resolved

**Symptom**: App reports permissions as missing before user has ever been prompted.

**Root Cause**: `missingPermissions()` checked `!= .authorized`, which treats `.notDetermined` (never prompted) the same as `.denied`.

**Fix**: Changed to only flag `.denied` or `.restricted`. `.notDetermined` means the system will prompt on first use.

**Commit**: `edcce1a`

---

## ISS-003: MainActor violation in RecordingCoordinator
**Session**: 15 | **Date**: 2026-04-11 | **Status**: Resolved

**Symptom**: Potential data race, `appState.audioLevel` mutated from non-main thread.

**Root Cause**: `stopRecording()` and `startLevelMonitoring()` timer callback accessed `appState` without MainActor isolation.

**Fix**: Wrapped mutations in `Task { @MainActor in }` and scheduled timer on main run loop.

**Files**: `Untype/App/RecordingCoordinator.swift`

---

## ISS-004: Overlay visibility race condition
**Session**: 15 | **Date**: 2026-04-11 | **Status**: Resolved

**Symptom**: Overlay sometimes not updating immediately on phase change.

**Root Cause**: `startPhaseObservation()` used `onChange: { Task { @MainActor in } }` introducing an async hop between observation and handler.

**Fix**: Replaced with `withCheckedContinuation` pattern so `updateOverlayVisibility()` runs as the immediate next MainActor work item.

**Files**: `Untype/App/AppDelegate.swift`

---

## ISS-005: MainActor violation in ProcessingCoordinator
**Session**: 15 | **Date**: 2026-04-11 | **Status**: Resolved

**Symptom**: `appState` accessed off main actor in processing Task.

**Root Cause**: `Task` in `startProcessing()` lacked `@MainActor` annotation.

**Fix**: Added `@MainActor` to Task closure.

**Files**: `Untype/Processing/ProcessingCoordinator.swift`

---

## ISS-006: MainActor violation in AppDelegate insertAndDismiss
**Session**: 15 | **Date**: 2026-04-11 | **Status**: Resolved

**Symptom**: `dismiss()` called off MainActor, mutating appState unsafely.

**Root Cause**: Task in `insertAndDismiss` missing `@MainActor in`.

**Fix**: Added `@MainActor in` to Task closure.

**Files**: `Untype/App/AppDelegate.swift`

---

## ISS-007: Audio level updates too frequent
**Session**: 14 | **Date**: 2026-04-10 | **Status**: Resolved

**Symptom**: High CPU usage, excessive SwiftUI re-renders.

**Root Cause**: `processBuffer` in `AudioRecorder` dispatched audioLevel updates ~43x/sec (every audio buffer), each triggering @Observable change notifications via DispatchQueue.main.async.

**Fix**: Original throttle was reverted by parallel merge. Re-fixed in session 30: marked `audioLevel` with `@ObservationIgnored` and removed the main-thread dispatch. `AudioLevelMonitor` (20Hz timer) is the sole consumer, it polls the raw value and pushes to `appState`.

**Files**: `Untype/Audio/AudioRecorder.swift`

---

## ISS-008: Speech recognition cleanup on failure
**Session**: 14 | **Date**: 2026-04-10 | **Status**: Resolved

**Symptom**: Audio engine left running if speech recognition fails to start.

**Root Cause**: If `speechService.startRecognition()` throws after `audioRecorder.startRecording()` succeeds, no cleanup in catch block.

**Fix**: Added cleanup (stop recorder, clear onBuffer) in catch block. Note: may have been reverted by parallel agent merge, needs verification.

**Files**: `Untype/App/RecordingCoordinator.swift`

---

## ISS-009: Xcode project out of date
**Session**: 14 | **Date**: 2026-04-10 | **Status**: Resolved (session 22, 2026-04-13)

**Symptom**: `xcodebuild` fails to compile.

**Root Cause**: SPM-first development, new Swift files added via SPM but never added to Xcode `.pbxproj`. By session 22 the actual state was 14 of 19 files correct, 6 stale refs to deleted files (`HotkeyManager`, `LLMModels`, `LLMProvider`, `LocalProvider`, `ProcessingRouter`, `AudioLevelIndicator`), 5 new files missing (`MenuBarController`, `PermissionsCoordinator`, `FnPushToTalkMonitor`, `BlobWaveform`, `FocusedElementLocator`).

**Fix**: Deleted `Untype.xcodeproj` entirely. Xcode 14+ opens `Package.swift` directly with full editor/debugger support, so the xcodeproj was dead weight, its build settings were all stock boilerplate already replicated by `bin/build.sh` + `Info.plist`. Releasable bundles still go through `./bin/build.sh` so TCC grants survive rebuilds (`knowledge/signing-setup.md`).

---

## ISS-010: Parallel worktree agents overwrite uncommitted changes
**Session**: 14 | **Date**: 2026-04-10 | **Status**: Resolved (process)

**Symptom**: Manual changes lost after worktree agent merges.

**Root Cause**: Agents merge feature branches into main working tree, overwriting uncommitted changes.

**Fix**: Process change, commit in-progress work before launching parallel agents. Agents should use `--no-ff` merges for clean history.

---

## ISS-011: LocalProvider String/Substring type mismatch
**Session**: 15 | **Date**: 2026-04-11 | **Status**: Resolved

**Symptom**: Unnecessary `String()` wrapper in `capitalizeFirst`.

**Root Cause**: `Character.uppercased() + String(text.dropFirst())`, extra allocation.

**Fix**: Simplified to `text.prefix(1).uppercased() + text.dropFirst()`.

**Files**: `Untype/Processing/LocalProvider.swift`

---

## ISS-012: fn-press during inserting/justInserted swallowed
**Session**: 61 | **Date**: 2026-05-01 | **Status**: Resolved

**Symptom**: After Untype inserted text, pressing fn again immediately to start a new recording was a no-op until the overlay had fully dismissed.

**Root Cause**: `AppStateReducer`'s permissive set for the `fnPressed` event did not include `.inserting` and `.justInserted` phases. The state machine treated those windows as a dead zone for new recordings.

**Fix**: Extended the reducer's permissive sets to include both phases. `fnPressed` during `.inserting` cancels the in-flight insert and starts a new recording; during `.justInserted` it starts a new recording cleanly.

**Files**: `Untype/State/AppStateReducer.swift`

**Commit**: `5601328`

---

## ISS-013: STT "Thank you." hallucination on near-empty audio
**Session**: 61–62 | **Date**: 2026-05-01 | **Status**: Resolved

**Symptom**: When a recording was mostly silence with brief room noise, STT models emitted "Thank you.", "Thanks for watching.", "Subtitles by …", or single short words like "Paul", "What", "and", "So", "H.", high-frequency phrases / random short outputs the models produce on near-silent audio. Originally observed with Apple Speech (commit `1854419`); subsequently confirmed across the Whisper-family providers (Groq, RemoteWhisper, WhisperKit) which carry the same artefact from their YouTube-captions training corpus. The existing fully-silent gate did not catch the mostly-silent case.

**Root Cause**: Silence detector only fired `.transcriptDroppedAsSilent` when the entire recording's `peakLevel` was below `0.01`; transient noise (a chair, breath, mic bump) lifted the peak enough to bypass it, and the model then emitted training-corpus boilerplate or random short outputs.

**Fix**: Provider-agnostic post-STT hallucination filter. Drops the transcript when recording-wide `peakLevel < 0.05` AND ANY of: (a) the transcript matches an allow-list of known phrases (case-insensitive, exact match after normalisation); (b) it begins with a YouTube-caption prefix (`subtitles by`, `subtitled by`); (c) the transcript is ≤2 words. Two-gate design (energy + content shape) is load-bearing: energy alone drops legitimate quiet speech, content alone drops legitimate "Thank you" / "Yes" dictation. The peak threshold is tunable; the word-count cap was added after smoke surfaced single-word hallucinations the allow-list couldn't reasonably cover.

**Files**: `Sources/UntypeCore/Transcription/HallucinationFilter.swift` (new), call site at `Untype/App/RecordingCoordinator+Stream.swift` post-STT dispatch.

**Commits**: `c5aad40` (initial filter, peak + allow-list), `1a1b3f4` (added short-transcript word-count cap), `1854419` (original silent-audio drop).

---

## ISS-014: Chrome Omnibox paste silently fails
**Session**: 61 | **Date**: 2026-05-01 | **Status**: Open (deferred)

**Symptom**: Inserting cleaned text into Chrome's address bar (Omnibox) silently fails, clipboard sets, Cmd+V appears to fire, but nothing lands. Other Chrome text fields (page-body inputs, contenteditables) work correctly.

**Root Cause**: Not yet diagnosed. Three ranked hypotheses from the smoke (`knowledge/follow-up-brief-2026-05-01.md` Task 2):
1. Chrome Omnibox treats clipboard paste as "go to URL" rather than plain text input; non-URL transcripts may be discarded.
2. Focus race during overlay show, Untype's non-activating panel may momentarily perturb AX focus, snapping Omnibox back to the page body.
3. CGEvent Cmd+V is intercepted by Chrome's own command system before reaching the Omnibox input chain.

**Fix**: Pending diagnosis. Diagnostic phase requires user-driven AX probe (`UntypeAXProbe`) at three moments, fn-press, overlay-show, Cmd+V post, plus `pbpaste` verification after a failed insert. Mitigation tree: hypothesis 1 to "Address bar dictation is unsupported" hint or drop the cmd-z affordance specifically there; hypothesis 2 to small post-paste delay or focus-restore; hypothesis 3 to likely conclude as documented limitation.

**Files**: `Untype/Insertion/TextInserter.swift` (likely target if a fix lands).

---

## ISS-015: WhisperKit cold-fetch UX gap on first record
**Session**: 62 | **Date**: 2026-05-04 | **Status**: Resolved 2026-05-06

**Symptom**: On a fresh Mac with no `~/Documents/huggingface/` cache, the first hotkey-triggered recording with WhisperKit selected blocks while the model downloads from HuggingFace. There is no progress UI in the overlay, the user sees the recording state stall with no feedback. On a moderate connection the cold fetch can take several minutes.

**Root Cause**: `WhisperKitService` lazily fetches the model on first use without surfacing download progress to `AppState` / the overlay.

**Fix**: New `Phase.fetchingModel` (flag, progress lives in `AppState.modelFetchProgress` so per-tick Hub callbacks don't churn the reducer). `WhisperKitService.ensureModel(progressCallback:)` calls `WhisperKit.download(variant:progressCallback:)` and forwards `Foundation.Progress.fractionCompleted`; `loadPipeline` now points `WhisperKitConfig` at the local cache with `download: false` so initialization never re-fetches. `RecordingCoordinator+ModelFetch` gates `startPushToTalk` on a sub-millisecond `isModelCached()` filesystem check and runs the fetch instead of opening the mic when the cache is empty. `BarView` renders an `arrow.down.circle` glyph + linear progress bar + percent + Esc affordance; `.modelFetchFailed(reason:)` surfaces as a retryable error toast (⏎ re-kicks the fetch, Esc cancels). Esc mid-fetch dispatches `.dismiss` to `.cancelModelFetch` effect to coordinator cancels the Task; HubApi cooperates with `Task.isCancelled`. Closes Show-HN audit criterion 2 (`<5 min first-time setup`).

**Commits**: `8affeac` (state machine + view), `50bdb7f` (service refactor + tests), `6d7d1a8` (coordinator wiring + retry).

**Files**: `Sources/UntypeCore/Transcription/WhisperKitService.swift`, `Sources/UntypeCore/Transcription/WhisperKitSTTStage.swift`, `Untype/State/AppState.swift`, `Untype/State/AppStateReducer.swift`, `Untype/State/AppEvent.swift`, `Untype/State/AppEffect.swift`, `Untype/State/AppError.swift`, `Untype/Window/BarView.swift`, `Untype/Window/AppErrorView.swift`, `Untype/App/RecordingCoordinator.swift`, `Untype/App/RecordingCoordinator+ModelFetch.swift`, `Untype/App/AppDelegate.swift`, `Untype/App/AppDelegate+Handlers.swift`, `Tests/UntypeTests/AppStateReducerTests.swift`, `Tests/UntypeCoreTests/WhisperKitServiceFetchTests.swift`.

---

## ISS-016: Original toggle showed Apple Speech text in cloud-final hybrid mode
**Session**: 61 | **Date**: 2026-05-01 | **Status**: Resolved

**Symptom**: In hybrid mode (Apple Speech as live captions + cloud STT as final transcriber), the reviewing toast's `Cleaned ↔ Original` toggle displayed text that did not match what was polished. Per-segment alternates the user could tap also belonged to a different transcript than the polished one, making the alternates UI useless.

**Root Cause**: `RecordingCoordinator+Stream.swift` resolved its segments / prefix source as `(finalTranscriber as? AppleSpeechService) ?? liveTranscriber`. In hybrid mode `finalTranscriber` is cloud (no Apple), so the fallback pulled segments from the *live* Apple instance, but Apple's segmentation reflects Apple's STT output, not the cloud's. Two STT engines, two different transcripts; the toggle surfaced the wrong one.

**Fix**: Drop the `liveTranscriber` fallback. Segments now come exclusively from `finalTranscriber as? AppleSpeechService`. In hybrid / cloud-final mode this resolves to nil, segments stay empty, and `effectiveOriginalText` falls back to `lastOriginalText` (the cloud transcript actually polished). Apple-Speech-only mode is unaffected. Refactored further in `dd58ac7` to ride the data on the `.transcriptFinalized` event itself, funnelling all aux-state writes through the reducer's phase guard (closes the late-finalize-after-dismiss race for bug #7).

**Files**: `Untype/App/RecordingCoordinator+Stream.swift`.

**Commits**: `2f82c6f` (drop fallback), `dd58ac7` (refactor onto event data).

---

## ISS-017: Profile chip override produced identical polish output
**Session**: 61 | **Date**: 2026-05-01 | **Status**: Resolved (prompt shape), empirical retune may follow

**Symptom**: Picking a different profile from the chip menu (e.g. Chat to Email) triggered a re-polish (spinner ran, requestId rotated correctly per the wiring tests in session 65), but the resulting text was effectively identical to the previous profile's output. Per-profile tone/formatting hints had no visible effect.

**Root Cause**: Two-part. The wiring was correct, `appState.overriddenProfile` set, `effectiveContext` composed it, `LLMRequest.context.profile` carried it, `resolvedSystemPrompt` appended the per-profile tone block. But the base cleanup prompt instructed the model to "preserve the speaker's vocabulary, **tone**, and meaning exactly", which beat the appended per-profile tone hints. The model honoured the stronger absolute "preserve tone" rule and ignored the soft per-profile guidance.

**Fix**: Reframed the base prompt, drop "tone" from the verbatim list (vocabulary and meaning still preserved), add an explicit "tone and formatting may be adjusted to match any destination context provided below" clause. Tag the appended destination block as required, not suggested. Picking Email vs Chat now visibly shifts register without rewriting content. Empirical retune (stronger or more concrete per-profile `toneDescription` strings) may follow if smoke shows the shift is still too subtle on a given model.

**Files**: `Sources/UntypeCore/Processing/CloudProviderConfig.swift`.

**Commits**: `1895f3c`.

---

*To add a new issue, use `/issues add` with a description of the problem and solution.*
