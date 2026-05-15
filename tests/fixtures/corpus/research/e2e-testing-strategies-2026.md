# E2E testing strategies for Untype — survey of macOS-native OSS dictation apps

**Date:** 2026-04-24
**Scope:** How 6 macOS-native open-source voice-to-text apps handle automated testing, and what Untype should adopt.
**Companion:** `oss-competitor-landscape-2026.md` covers the same app set along feature/product axes.

---

## The gap in Untype today

Untype has **170 XCTest cases** covering the `UntypeCore` library (adapters, registries, STT/polishing protocols, scoring, streaming). But `Package.swift` declares **no test target for the `Untype` executable target**, so the entire app-level glue layer is manually verified at release time:

- `Untype/State/AppState.swift` — the `@Observable` state machine that drives all UI (165 LOC).
- `Untype/App/RecordingCoordinator.swift` — mic capture → STT dispatch (309 LOC; the largest untested hotspot).
- `Untype/Processing/ProcessingCoordinator.swift` — STT output → polishing → insertion (via `UntypeCore`).
- `Untype/App/AppRouterBuilder.swift` — wires the registries into a live router (58 LOC).
- `Untype/Window/OverlayPanel.swift` + `OverlayController.swift` — NSPanel + SwiftUI host.

Session 53 just landed four parallel adapters; the registry surface keeps growing while the glue stays untested. That's the concrete problem this research is meant to inform.

---

## Surveyed apps at a glance

| App | Stars | License | Test files | Audio fixtures | CI runs tests | STT engine |
|---|---|---|---|---|---|---|
| [watzon/pindrop](https://github.com/watzon/pindrop) | 469 | MIT | ~30 (Swift Testing) | Synthesized mock buffers, not fixtures | ✅ `macos-26` | WhisperKit + Parakeet |
| [altic-dev/FluidVoice](https://github.com/altic-dev/FluidVoice) | 1,984 | GPL-3.0 | ~10 (XCTest, real E2E) | ✅ `dictation_fixture.wav` | ✅ `macos-latest` | Parakeet/Whisper/Apple/Cohere |
| [moona3k/macparakeet](https://github.com/moona3k/macparakeet) | 119 | NOASSERTION | ~40 (XCTest + CLI tests) | Mock audio processor actor | ✅ `macos-14`, `swift test --parallel` | Parakeet TDT on ANE |
| [zachswift615/speak2](https://github.com/zachswift615/speak2) | 75 | — | 9 (XCTest) | No | ❌ release-only workflow | WhisperKit + Parakeet + Ollama |
| [Beingpax/VoiceInk](https://github.com/Beingpax/VoiceInk) | 4,681 | NOASSERTION | **2 empty templates** | No | ❌ no CI | Whisper + Parakeet + Apple + 9 cloud providers |
| [FluidInference/swift-scribe](https://github.com/FluidInference/swift-scribe) | 285 | MIT | **0** | No | ❌ no CI | Apple SpeechAnalyzer (macOS 26) |

**The single most important finding:** stars don't correlate with test coverage. VoiceInk (4.7k stars) has two Xcode-default empty template files and no CI. The 2k-star FluidVoice and the 119-star macparakeet are the only two projects with anything like a real test strategy. Most shipping macOS OSS dictation apps are held together entirely by hand-testing.

---

## Per-project breakdown

### FluidVoice — real E2E at the STT seam

The one worth studying first. `Tests/FluidDictationIntegrationTests/` contains:

- **`DictationE2ETests.swift`** — `testDictationEndToEnd_whisperTiny_transcribesFixture` instantiates a real `WhisperProvider`, calls `prepare()` to download the tiny model, loads a fixture WAV, calls `transcribe(samples)`, and asserts the result with **fuzzy `contains`** on normalized text: `"hello"`, `"fluid"`, `"voice" || "fluidvoice" || "boys"` (allowing a near-variant).
- **`Helpers/AudioFixtureLoader.swift`** — ~100 lines. Reads `dictation_fixture.wav` from the test bundle, runs it through `AVAudioConverter` to 16kHz/mono/Float32, returns `[Float]`. Clean, reusable, no hardware dependency.
- **`Resources/dictation_fixture.wav`** — 2–4 sec, WAV mono 16kHz 16-bit PCM, phrase "hello fluid voice". Documented format spec in `Resources/README.md`.
- **CI** (`.github/workflows/build.yml`): `macos-latest`, **caches `~/Library/Caches/WhisperModels`** across runs so the model download only hits once, unsigned build, `xcodebuild test` with xcpretty.

What makes this good: the test is *against the real STT pipeline*, not a mock. It validates that the WAV-decoding code, the model loader, the provider, and the text path all work together. Fuzzy matching makes it robust to ±1 token variations from Whisper's nondeterminism.

### pindrop — layered test plans, Swift Testing, protocol mocks

`PindropTests/` has ~30 files in Swift Testing (`import Testing`, `@Test`, `#expect`, `#require`) — not XCTest. The pattern worth stealing:

- **Three xctestplans** sharing the same test target: `Unit.xctestplan`, `Integration.xctestplan`, `UI.xctestplan`. Each sets env vars `PINDROP_TEST_MODE=1` and `PINDROP_RUN_INTEGRATION_TESTS=0|1` and uses `skippedTests`/`selectedTests` to include or exclude specific test classes. Same code, three boundaries — CI runs the unit plan, devs can opt into integration locally.
- **`PindropTests/AGENTS.md`** — a written test-authoring guide explaining mock patterns (`MockURLSession`, `MockPermissionProvider`, `MockAudioCaptureBackend`), async patterns, in-memory SwiftData. Worth having as our own playbook.
- **Protocol-based hardware mocks**: `AudioCaptureBackend`, `PermissionProviding`, `URLSessionProtocol` — every external dependency sits behind a protocol, so tests never hit mic/keychain/network.
- **`AppCoordinatorContextFlowTests.swift`** uses a `MockAXProvider` to simulate `AXUIElementCreateApplication(88880)` and attribute lookups — tests accessibility-tree integration without requiring TCC grants.
- **`AppTestMode.swift`** in the app target exposes a test-mode hook the test plans can toggle.
- **CI** (`.github/workflows/ci.yml`): `macos-26` runner, latest-stable Xcode, unsigned build and test, uploads the `.app` as an artifact. Pure `xcodebuild`.

### macparakeet — actor-based mocks + event-driven state machine

The most interesting architectural pattern. `Tests/MacParakeetTests/`:

- **`DictationFlow/DictationFlowStateMachineTests.swift`** — `DictationFlowStateMachine` is tested as a pure event → `[effect]` function. Events like `.startRequested(mode:)`, `.entitlementsGranted(generation:)`, `.recordingStarted(generation:)`, `.stopRequested`, `.cancelRequested(reason:)` drive state transitions; the test asserts on the emitted effects array (`.hideIdlePill`, `.showReadyPill`, `.checkEntitlements`). No UI, no timers, no I/O — just `(state, event) → (state, effects)`.
- **`DictationFlowCoordinatorTests.swift`** — the layer above the state machine, wired to mock services.
- **`Audio/MockAudioProcessor.swift`** — a Swift `actor` conforming to `AudioProcessorProtocol`. Configurable results, errors, start-capture delays, call-count tracking. Clean dependency injection seam.
- **`Database/` tests** use SwiftData in-memory containers (SQLite file alternatives), similar to pindrop.
- **CI** (`.github/workflows/ci.yml`): `macos-14`, Xcode 16.1, runs `swift build -c release`, a concurrency-safety pass with `-warn-concurrency`, then `swift test --parallel`. **No xcodebuild required** — the whole project is SPM-addressable.

### speak2 — cheap state tests, no CI tests

9 test files, all XCTest. Patterns:

- **`RecordingStateTests.swift`** — enum-case-existence checks ("RecordingState has 5 cases including .refining"). Near-zero value, but serves as compile guard.
- **`WhisperStreamingTests.swift`** — `AudioSampleBuffer` unit tests (append, snapshot, count, thread-safe snapshot copy) and `diffWords(previous:current:)` tests for streaming display. These are the kind of tests that *prevent* streaming regressions.
- **`OllamaRefinerTests.swift`**, **`ParakeetStreamingTests.swift`** — similar unit-level coverage.
- **CI**: `release.yml` builds and signs for releases; **no CI job runs the tests**. Tests exist for the developer's local use only.

### VoiceInk — 4.7k stars, zero real tests

`VoiceInkTests/VoiceInkTests.swift` is the stock Xcode template with one `@Test func example()` whose body is a comment. `VoiceInkUITests.swift` has an unmodified launch-performance measurement. No workflows directory at all. The app has 8 cloud STT providers wired through `VoiceInk/Transcription/Cloud/` and no automated confirmation that any of them work. This is the prevailing norm in the space.

### swift-scribe — no tests directory

Pure manual verification. Relies on macOS 26's `SpeechAnalyzer` and Foundation Models, which are Apple-framework-level and presumably trusted as "Apple tests them for us." No CI.

---

## Patterns that recur

1. **Fixture audio + fuzzy-contains assertions at the STT seam** (FluidVoice): the canonical "E2E" test. Load a short WAV, run it through the real provider, assert the decoded text `contains` a few expected tokens. Cheaply replayable on CI.
2. **Actor or protocol mocks for hardware** (pindrop, macparakeet): every external side (mic, AX, clipboard, URLSession, permissions) sits behind a protocol or actor, and tests wire in a scripted version. Never touches real hardware.
3. **State machine as pure `(state, event) → effects`** (macparakeet): a `DictationFlowStateMachine` that returns an effect list is vastly more testable than a classic coordinator that calls `showPill()` and `startTimer()` directly. Every transition becomes a unit test.
4. **Xctestplans as test filters** (pindrop): one test target, multiple plans, env-var-gated `skippedTests`/`selectedTests`. Lets CI run a fast subset while devs opt into slow integration work locally.
5. **Model caching on CI** (FluidVoice): `actions/cache@v4` keyed on `whisper-models-v1`. First run is slow, subsequent runs reuse.
6. **Unsigned `xcodebuild` on `macos-latest` or `macos-26`** (pindrop, FluidVoice, macparakeet): set `CODE_SIGN_IDENTITY=""`, `CODE_SIGNING_REQUIRED=NO`, `CODE_SIGNING_ALLOWED=NO`. Nobody tries to CI-sign a real app bundle — that's release-only.
7. **SPM-native when possible** (macparakeet): if the code compiles with `swift test`, use `swift test --parallel` instead of `xcodebuild`. Faster, simpler, no Xcode project drift.

## Anti-patterns / absences

- **No one runs XCUITest flows in CI** across the whole recording → transcribe → insert pipeline. The one XCUITest file in pindrop and VoiceInk both launch the app and assert nothing meaningful. `.accessory` NSPanels are TCC-restricted and flaky in automation; the consensus is to skip them.
- **No one uses the real microphone in CI.** All "audio input" in CI flows is pre-recorded fixtures or synthesized buffers. Permission prompts make live mic capture a non-starter on headless runners.
- **No one snapshot-tests SwiftUI views.** ViewInspector and similar libraries are absent from every one of these repos.
- **Most apps have no CI test job at all** (VoiceInk, swift-scribe, speak2). The ones that do test (FluidVoice, pindrop, macparakeet) do it well; everyone else doesn't bother.
- **Signing for tests is universally skipped.** TCC-gated permissions (mic, speech recognition, accessibility) are tested via protocol mocks, not by signing and granting on a CI runner.

---

## Recommendation for Untype

The hypotheses from the plan held up against the survey. Revised tiering, **ranked by ROI**:

### Tier 1 — Add a `UntypeTests` test target for the app executable (week 1)

The structural blocker. `Package.swift` currently has no test target for the `Untype` executable target, so `AppState`, `RecordingCoordinator`, `ProcessingCoordinator`, `AppRouterBuilder` cannot even be imported by tests. Add:

```swift
.testTarget(
    name: "UntypeTests",
    dependencies: ["Untype", "UntypeCore"],
    path: "Tests/UntypeTests"
)
```

This alone unblocks every subsequent tier. Cost: one line in `Package.swift`, one empty test file, one CI run to confirm nothing broke.

### Tier 2 — State-machine tests on `AppState` (week 1)

`Untype/State/AppState.swift` is an `@Observable final class`, 165 LOC. Before adding new tests, consider refactoring its state transitions into a macparakeet-style `(state, event) → effects` function so transitions are pure and testable without timers, UI, or I/O. If that refactor is too big, start with direct mutation tests (set state, assert observable fields) — still better than nothing.

Concrete first tests: "idle → recording → processing → inserting → idle" happy path, cancel from each state, error from each state.

### Tier 3 — Fixture-audio integration tests at the STT seam (week 2)

Copy the FluidVoice pattern wholesale into `Tests/UntypeCoreTests/` (not the new `UntypeTests`, since STT lives in `UntypeCore`):

- Add `Tests/UntypeCoreTests/Fixtures/Audio/` with 2–3 WAVs: mono 16kHz 16-bit PCM, ~3 seconds each, distinct phrases ("the quick brown fox", "hello untype", a sentence with numbers).
- Port `AudioFixtureLoader` directly — it's generic, no FluidVoice-specific logic.
- Gate the tests behind an env var `UNTYPE_RUN_INTEGRATION_TESTS=1`, matching pindrop's pattern; local-default off, CI-opt-in on a separate job.
- Run each registered STT adapter (`AppleSpeechDescriptor`, `WhisperKitService`-backed descriptor, `GroqSTTProvider`, `RemoteWhisperSTTProvider` with a recorded HTTP response) against each fixture and assert fuzzy-contains on normalized text. The adapter registry already exists — these tests exercise the exact seam session 53 just finished stabilizing.
- On CI, cache `~/Library/Caches/WhisperKit` (or wherever `argmax-oss-swift` stashes models) the same way FluidVoice caches Whisper.

**Build-config note:** FluidVoice's integration tests import `@testable import FluidVoice_Debug` — a Debug-only build product, not the standard target. If we follow the same `xcodebuild` path later (for a UI-test target), we'll need to mirror that split. For SPM-only tests via `swift test`, the distinction doesn't apply.

### Tier 4 — Coordinator tests with mocked `STTStage` / `PolishingStage` (week 2–3)

`RecordingCoordinator` (309 LOC) and `ProcessingCoordinator` are the untested hotspots. Inject `STTStage` and `PolishingStage` as protocols (they already are protocols — defined at `Sources/UntypeCore/Transcription/STTStage.swift` and `Sources/UntypeCore/Processing/PolishingStage.swift`). Write a `ScriptedSTTStage` that emits a scripted sequence of `TranscriptionChunk`s at controlled intervals, and assert on the observable state transitions and final insertion payload.

This is cheaper than Tier 3 (no real audio, no real models) but tests the *glue* in a way Tier 3 cannot.

### Tier 5 — skip (for now)

- **XCUITest**: no OSS comparable runs meaningful XCUITest flows. Skip until we have a specific bug class that can only be caught here.
- **SwiftUI snapshot tests**: no OSS comparable does this. Skip until there's a visual-regression problem worth chasing.
- **Real-microphone CI**: universally avoided. Skip.

---

## CI implications

- **Two jobs**: `unit` (the default, runs on every push, fast, `swift test`) and `integration` (env-gated, runs on PR + main-push, downloads models, caches them). Mirrors pindrop.
- **`macos-14` or `macos-latest`** with `maxim-lobanov/setup-xcode@v1`. Pindrop's `macos-26` is only needed when you require new-OS APIs; Untype's `platforms: [.macOS(.v14)]` means `macos-14` is sufficient.
- **Unsigned build**: `CODE_SIGN_IDENTITY=""`, `CODE_SIGNING_REQUIRED=NO`, `CODE_SIGNING_ALLOWED=NO`. The `bin/build.sh` signing identity is local-only and does not belong on CI. Matches every OSS comparable.
- **SPM-native where possible**: `swift build && swift test --parallel`. Only reach for `xcodebuild` if a future target (e.g. UI tests) requires it.
- **Model cache**: `actions/cache@v4` on the WhisperKit model directory, keyed by `whisperkit-models-v1`. FluidVoice shows this pattern.

## What to do first (single-PR scope)

One PR, one day of work:

1. Add `UntypeTests` test target in `Package.swift` (library target `dependencies: ["Untype", "UntypeCore"]`).
2. Create `Tests/UntypeTests/AppStateTests.swift` with three or four state-transition tests — no refactor yet, just prove the target wires up.
3. Add `.github/workflows/ci.yml` with a single `swift test` job on `macos-14`. Nothing else yet.
4. Document the approach inline in a new `Tests/UntypeTests/AGENTS.md` mirroring pindrop's test-authoring brief.

Ship that. Tier 3 and Tier 4 become separate PRs, each a few days.

---

## Sources

- [watzon/pindrop](https://github.com/watzon/pindrop) — [AGENTS.md](https://github.com/watzon/pindrop/blob/main/PindropTests/AGENTS.md), [Integration.xctestplan](https://github.com/watzon/pindrop/blob/main/Pindrop.xcodeproj/xcshareddata/xctestplans/Integration.xctestplan), [ci.yml](https://github.com/watzon/pindrop/blob/main/.github/workflows/ci.yml), [AppCoordinatorContextFlowTests.swift](https://github.com/watzon/pindrop/blob/main/PindropTests/AppCoordinatorContextFlowTests.swift)
- [altic-dev/FluidVoice](https://github.com/altic-dev/FluidVoice) — [DictationE2ETests.swift](https://github.com/altic-dev/FluidVoice/blob/main/Tests/FluidDictationIntegrationTests/DictationE2ETests.swift), [AudioFixtureLoader.swift](https://github.com/altic-dev/FluidVoice/blob/main/Tests/FluidDictationIntegrationTests/Helpers/AudioFixtureLoader.swift), [build.yml](https://github.com/altic-dev/FluidVoice/blob/main/.github/workflows/build.yml)
- [moona3k/macparakeet](https://github.com/moona3k/macparakeet) — [DictationFlowStateMachineTests.swift](https://github.com/moona3k/macparakeet/blob/main/Tests/MacParakeetTests/DictationFlow/DictationFlowStateMachineTests.swift), [MockAudioProcessor.swift](https://github.com/moona3k/macparakeet/blob/main/Tests/MacParakeetTests/Audio/MockAudioProcessor.swift), [ci.yml](https://github.com/moona3k/macparakeet/blob/main/.github/workflows/ci.yml)
- [zachswift615/speak2](https://github.com/zachswift615/speak2) — [RecordingStateTests.swift](https://github.com/zachswift615/speak2/blob/main/Tests/Speak2Tests/RecordingStateTests.swift), [WhisperStreamingTests.swift](https://github.com/zachswift615/speak2/blob/main/Tests/Speak2Tests/WhisperStreamingTests.swift)
- [Beingpax/VoiceInk](https://github.com/Beingpax/VoiceInk) — [VoiceInkTests.swift](https://github.com/Beingpax/VoiceInk/blob/main/VoiceInkTests/VoiceInkTests.swift) (empty template confirmed 2026-04-24)
- [FluidInference/swift-scribe](https://github.com/FluidInference/swift-scribe) — no tests directory as of 2026-04-24
