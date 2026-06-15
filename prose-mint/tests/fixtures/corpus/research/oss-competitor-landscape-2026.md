# macOS-native open-source voice-to-text landscape — April 2026

**Date:** 2026-04-24
**Scope:** macOS-native Swift open-source dictation apps and the two leading Swift audio libraries they build on. Commercial apps are surveyed separately in [`competitive-landscape.md`](./competitive-landscape.md) — that doc covers Superwhisper, Wispr Flow, MacWhisper, Aqua, Notta, etc. This doc is for the OSS slice only, where we can read the source.
**Companion:** [`e2e-testing-strategies-2026.md`](./e2e-testing-strategies-2026.md) covers the same app set with a testing-only lens; read that for detailed test patterns and CI approaches.

## Scope notes

**Included (6 apps):**
- [Beingpax/VoiceInk](https://github.com/Beingpax/VoiceInk) — 4,681 ⭐
- [altic-dev/FluidVoice](https://github.com/altic-dev/FluidVoice) — 1,984 ⭐
- [watzon/pindrop](https://github.com/watzon/pindrop) — 469 ⭐
- [FluidInference/swift-scribe](https://github.com/FluidInference/swift-scribe) — 285 ⭐
- [moona3k/macparakeet](https://github.com/moona3k/macparakeet) — 119 ⭐
- [zachswift615/speak2](https://github.com/zachswift615/speak2) — 75 ⭐

**Also referenced (2 libraries, not apps):**
- [argmaxinc/WhisperKit](https://github.com/argmaxinc/WhisperKit) — 6,030 ⭐, MIT — the dominant on-device Whisper runtime for Apple Silicon. Untype already depends on `argmax-oss-swift` (same org).
- [FluidInference/FluidAudio](https://github.com/FluidInference/FluidAudio) — 1,913 ⭐, Apache-2.0 — CoreML audio models, including Parakeet variants and speaker diarization. FluidVoice and macparakeet both build on it.

**Excluded (and why):**
- [Explosion-Scratch/whisper-mac](https://github.com/Explosion-Scratch/whisper-mac) — TypeScript/Electron, not macOS-native Swift.
- [OpenWhispr/openwhispr](https://github.com/OpenWhispr/openwhispr) — cross-platform (Win/Linux/Mac), not Swift-native.
- Buzz (PyQt), Vibe (Tauri), Whispo (Electron), WhisperWriter (Python) — cross-platform, out of scope.
- Aiko — freemium, not OSS on GitHub.

---

## App-by-app profiles

### VoiceInk — 4,681 ⭐ · three local engines + nine cloud providers

**Description:** "Voice-to-text app for macOS to transcribe what you say to text almost instantly" — the most starred OSS macOS dictation app by a wide margin.

**Stack:** Pure AppKit + SwiftUI, `VoiceInk.xcodeproj`, no Swift Package Manager. License NOASSERTION.

**STT engines:** three local backends plus nine cloud providers, routed through a `TranscriptionServiceRegistry` — the broadest engine coverage in the surveyed set. Local: Whisper (via `WhisperModelManager`, with `ggml-silero-v5.1.2.bin` bundled for VAD), FluidAudio/Parakeet (`VoiceInk/Transcription/FluidAudio/`), and Apple Speech (`VoiceInk/Transcription/Native/NativeAppleTranscriptionService.swift`). Cloud providers under `VoiceInk/Transcription/Cloud/`: Deepgram, ElevenLabs, Gemini, Groq, Mistral, OpenAI-compatible, Soniox, Speechmatics, XAI. Directly analogous to Untype's adapter registry — same problem, same solution.

**Feature highlights:** transcription model registry, per-transcription audio file management, auto-cleanup service, clipboard output, global hotkey, custom cloud model manager. Releases tracked via `appcast.xml` + Sparkle-style updates.

**Testing:** essentially none. `VoiceInkTests/VoiceInkTests.swift` is the Xcode default template with an empty `@Test func example()`. `VoiceInkUITests/` has an unmodified launch-performance test. No `.github/workflows` at all. Ships releases manually.

**Top open issues (by reactions):**
- [#199](https://github.com/Beingpax/VoiceInk/issues/199) (14) — system audio capture (dictating into meeting recordings)
- [#333](https://github.com/Beingpax/VoiceInk/issues/333) (12) — integrate Apple Foundation Models for cleanup
- [#84](https://github.com/Beingpax/VoiceInk/issues/84) (7) — URL scheme support for programmatic invocation
- [#534](https://github.com/Beingpax/VoiceInk/issues/534) (6) — run Voxtral Realtime model on-device
- [#450](https://github.com/Beingpax/VoiceInk/issues/450) (6) — double-tap hotkey to start recording

### FluidVoice — 1,984 ⭐ · multi-engine, real E2E tests

**Description:** "Fastest macOS Offline Dictation app — Voice to Text fully Local." Ships a feature-heavy app targeting the on-device multi-model niche.

**Stack:** AppKit + SwiftUI via `Fluid.xcodeproj`, GPL-3.0, 79 MB (bundles model metadata). Services in `Sources/Fluid/Services/`. Integrates with SwiftLint, xcpretty.

**STT engines:** Parakeet Flash, Parakeet TDT v3, Parakeet TDT v2, Cohere Transcribe (added recently for higher multilingual accuracy), Apple Speech framework, Whisper (multiple sizes). Multi-engine switching is a core UX.

**Feature highlights:** per-app dictation prompt profiles, global/default/app-binding prompt resolution, AI post-processing toggle, transcription start/end sound options (with a legacy-settings migration path visible in the test file), settings store backed by UserDefaults + Keychain.

**Testing:** `Tests/FluidDictationIntegrationTests/` has a real `DictationE2ETests.swift` that transcribes a fixture WAV with a real Whisper Tiny model and fuzzy-matches the output. CI (`macos-latest`) caches Whisper models across runs. This is the single strongest OSS example of "E2E that actually runs." See [`e2e-testing-strategies-2026.md`](./e2e-testing-strategies-2026.md) for the detailed pattern.

**Top open issues:**
- [#92](https://github.com/altic-dev/FluidVoice/issues/92) (10) — distribute via Homebrew cask
- [#18](https://github.com/altic-dev/FluidVoice/issues/18) (8) — speaker diarization for multi-speaker conversations
- [#62](https://github.com/altic-dev/FluidVoice/issues/62) (5) — Sonoma crash tracker
- [#182](https://github.com/altic-dev/FluidVoice/issues/182) (3) — separate button for toggling AI post-processing

### pindrop — 469 ⭐ · WhisperKit + Parakeet, test-first architecture

**Description:** "A native macOS menu bar dictation app using local speech-to-text with WhisperKit." Tagline matches Untype almost exactly; the most ideologically aligned comparable.

**Stack:** `Pindrop.xcodeproj`, SwiftUI + AppKit, MIT license. Uses Swift Testing (the new `import Testing` framework), not XCTest.

**STT engines:** WhisperKit (via argmax-oss-swift, same dep as Untype) + Parakeet (`ParakeetEngineTests.swift` suggests dedicated wrapping). AI enhancement service layered on top (`AIEnhancementServiceTests.swift`, `AIEnhancementResponseSanitizerTests.swift`).

**Feature highlights:** automatic dictionary learning, history store, media ingestion service, path-mention resolver (dictate `"@docs/readme"` and it resolves to a path), mention formatter, prompt preset store, app-context adapter registry. Three xctestplans (Unit/Integration/UI) gated by env vars. `AGENTS.md` in the test dir explains the test authoring pattern.

**Testing:** the second-strongest OSS example after FluidVoice, and the structurally cleanest — every external dependency (AX, mic, permissions, URLSession) sits behind a protocol with a matching mock. CI on `macos-26` with `xcodebuild`, unsigned, uploads `.app` artifact.

**Top open issues:**
- [#61](https://github.com/watzon/pindrop/pull/61) / [#60](https://github.com/watzon/pindrop/issues/60) / [#57](https://github.com/watzon/pindrop/issues/57) — Russian, Ukrainian, Polish language support
- [#59](https://github.com/watzon/pindrop/issues/59) — text insertion fails in VMs (types "AAA..." or "v")
- [#56](https://github.com/watzon/pindrop/issues/56) — OpenAI models not working

### swift-scribe — 285 ⭐ · Apple-first, macOS 26 only

**Description:** "Fully local, no dependency scribe. Speak into your microphone and summarize. Requires iOS 26 and MacOS 26." A bet on Apple's on-device stack entirely.

**Stack:** `SwiftScribe.xcodeproj`, MIT. Requires macOS 26.

**STT engines:** Apple's new `SpeechAnalyzer` (the post-`SFSpeechRecognizer` API) + Apple Foundation Models for summarization. No third-party STT at all. Diarization via `DiarizationManager.swift`. Extremely thin surface area: ~15 Swift files total.

**Feature highlights:** live transcription + summary, speaker diarization, persistent memo model (SwiftData). Pitched as a minimal reference implementation for developers exploring the macOS 26 speech stack.

**Testing:** none. No test directory. Trusts Apple's frameworks entirely.

**Top open issues:** no open issues as of the survey — low engagement, likely because the macOS 26 requirement gates the audience.

### macparakeet — 119 ⭐ · Parakeet-only, deepest test coverage

**Description:** "Fast, local-first voice app for Mac. Dictation and transcription powered by Parakeet TDT on the Neural Engine."

**Stack:** SPM-native (`swift build` / `swift test --parallel`), license NOASSERTION (GitHub couldn't auto-detect an SPDX match). Splits CLI (`Sources/CLI/`) from GUI (`Sources/App/`). Uses SwiftData for persistence.

**STT engines:** Parakeet TDT on the Neural Engine, via FluidAudio. Single-engine focus.

**Feature highlights:** dictation + file/URL transcription, full-text history, stats and lifetime metrics, custom words dictionary, chat conversations over dictations, transcription repository with private/shared separation. GUI for meeting audio capture (`MeetingAudioCaptureService`). LLM integration for summarization.

**Testing:** deepest OSS coverage by far. ~40 test files split across CLI tests and app tests. Audio tests use a `MockAudioProcessor` actor. Database tests use in-memory SwiftData. The standout pattern: `DictationFlowStateMachineTests` treats the state machine as a pure `(state, event) → [effect]` function — a pattern Untype should consider adopting for `AppState`. CI on `macos-14` runs `swift build -c release`, a concurrency-safety pass, and `swift test --parallel`.

**Top open issues:**
- [#101](https://github.com/moona3k/macparakeet/pull/101) — NSHostingView overlay container fixes
- [#128](https://github.com/moona3k/macparakeet/issues/128) — edit transcriptions inline
- [#127](https://github.com/moona3k/macparakeet/issues/127) — timestamp-stripped YouTube transcripts
- [#117](https://github.com/moona3k/macparakeet/issues/117) — app-detection-based AI profiles (per-app prompts)

### speak2 — 75 ⭐ · fn-key hold, WhisperKit + Parakeet + Ollama

**Description:** "Local Voice Dictation for MacOS — hold fn key to speak, release to transcribe." The minimal-footprint option in the set.

**Stack:** `Speak2.xcodeproj`. No license declared.

**STT engines:** WhisperKit and Parakeet for transcription, Ollama for optional local LLM refinement. Streaming support via `AudioSampleBuffer` and a `diffWords(previous:current:)` diff algorithm for incremental display.

**Feature highlights:** fn-key push-to-talk, phonetic matcher for custom word hints, refinement mode (Ollama-backed), custom hotkey configuration. Distinctively narrow focus — no history, no menu bar, just dictate-and-insert.

**Testing:** 9 XCTest files covering streaming primitives (`AudioSampleBuffer`, `StreamingTextSnapshot`, `diffWords`), state enums, refiner config. CI workflow only runs on release tags (build + sign), **not on push or PR** — tests exist but aren't automatically validated.

**Top open issues:**
- [#16](https://github.com/zachswift615/speak2/issues/16) — transcriptions lost on audio longer than 30 seconds (classic Whisper context-window issue)

---

## Cross-cutting observations

### STT engine trend: Parakeet is catching up to Whisper for dictation

Four of the six apps ship Parakeet alongside or instead of Whisper:

- **macparakeet** and **FluidVoice** default to Parakeet TDT for dictation (faster, lower latency on Apple Silicon, better for short utterances).
- **pindrop** and **speak2** support both.
- **VoiceInk** ships all three local engines (Whisper + Parakeet via FluidAudio + Apple Speech) plus nine cloud providers — breadth over depth.
- **swift-scribe** uses neither Whisper nor Parakeet — it bet on Apple's `SpeechAnalyzer`.

The tailwind for Parakeet is that `FluidInference/FluidAudio` made it easy to embed (1,913 ⭐, Apache-2.0, ~286 MB of CoreML weights). Untype currently uses WhisperKit via `argmax-oss-swift`; a Parakeet adapter is a natural future addition, and the adapter registry built in session 51 already supports it at the `STTStage` protocol level.

### LLM polishing: the Foundation-Models shoe is dropping

VoiceInk issue [#333](https://github.com/Beingpax/VoiceInk/issues/333) (12 reactions) and pindrop's `AIEnhancementService` show the same direction: apps are moving the "polish" stage from cloud LLMs (OpenAI/Anthropic/Gemini) toward on-device Apple Foundation Models (macOS 26) or local Ollama. swift-scribe goes all-in on Apple FM; pindrop hedges with a pluggable service.

Untype's polishing registry already supports this trajectory — `CloudPolishingAdapter` + `OllamaPolishingAdapter` are in place, and an Apple Foundation Models adapter would slot in cleanly on macOS 26.

### Architecture: everyone hits the same seams

Every app in the set independently arrived at roughly the same module layout:
1. Hotkey / push-to-talk input.
2. Permissions (mic + accessibility).
3. Audio capture with a level monitor.
4. STT engine(s) behind a registry or protocol.
5. Optional LLM polishing/refinement stage.
6. Output (clipboard paste, direct text insertion via CGEventPost or AX).
7. Menu bar + overlay panel for state UI.
8. Settings store (UserDefaults + Keychain).
9. History store (SwiftData for the ones that have it).

Untype's existing layout matches this exactly. The adapter-registry abstraction Untype introduced in sessions 51–53 is the cleanest version of the pattern in the surveyed set — VoiceInk has a cloud-provider registry, FluidVoice has engine switching, but neither has Untype's separation of `STTStage` + `PolishingStage` + provider descriptors at the library level.

### Pain points that recur across apps

Cross-referencing with `user-pain-points-and-desires-2026.md` (which synthesizes commercial-side feedback), the OSS issue trackers surface the same themes plus a few OSS-specific ones:

| Pain point | Observed in | Relevance to Untype |
|---|---|---|
| System audio capture (not just mic) | VoiceInk #199 | Out of scope for MVP |
| On-device LLM polishing (Apple FM or Ollama) | VoiceInk #333, pindrop | **Already in scope** — Ollama adapter shipped session 52 |
| Per-app dictation profiles / prompts | FluidVoice, macparakeet #117 | **Worth considering** — fits `AppContext` (`Sources/UntypeCore/Processing/AppContext.swift`) |
| Speaker diarization | FluidVoice #18 | Out of scope |
| Homebrew cask distribution | FluidVoice #92 | Distribution decision for later |
| 30-second Whisper context cutoff | speak2 #16 | Untype uses WhisperKit which handles this via chunking — verify |
| Text insertion failure in VMs / Electron apps | pindrop #59 | Known class of AX-injection bugs; worth a test fixture |
| Language support beyond English (RU/UA/PL) | pindrop #57/#60/#61 | Out of scope for MVP; note for later |
| Double-tap hotkey | VoiceInk #450 | UX tweak; aligns with existing push-to-talk work |

---

## Implications for Untype

Five bullet points of "consider / be aware of / avoid," keyed to existing modules:

1. **Steal the xctestplan-gated-integration-tests pattern from pindrop.** One test target, multiple plans, env vars flipping which classes run. Matches the Tier 3 recommendation in the E2E doc. Relevant files: new `UntypeTests` target + optional xctestplans at the project level if/when we add an xcodeproj back.

2. **Refactor `AppState` toward macparakeet's `(state, event) → [effect]` style before adding more UI state.** `Untype/State/AppState.swift` is 165 LOC and will grow; pure-function transitions make every new state testable for ~1 extra test file. See [`DictationFlowStateMachineTests.swift`](https://github.com/moona3k/macparakeet/blob/main/Tests/MacParakeetTests/DictationFlow/DictationFlowStateMachineTests.swift).

3. **Plan a Parakeet STT adapter.** Four of six comparables ship it; the `STTStage` protocol and registry already make this additive (see the existing `GroqSTTDescriptor` / `RemoteWhisperSTTDescriptor` pattern). `FluidAudio` is Apache-2.0 and 1.9k-star-maintained.

4. **Apple Foundation Models polishing adapter is the natural next polishing target** after Ollama. swift-scribe's entire approach rests on it; VoiceInk #333 (12 reactions) shows demand. Additive to `PolishingRegistry`.

5. **Don't chase popularity as a signal — VoiceInk has 4.7k stars and zero tests.** Untype's unit-test foundation is already stronger than every app in this set except macparakeet. The investment to make is in the app-target glue (Tier 1/2/4 in the E2E doc), not in copying VoiceInk's feature list wholesale.

---

## Sources

- [watzon/pindrop](https://github.com/watzon/pindrop)
- [altic-dev/FluidVoice](https://github.com/altic-dev/FluidVoice)
- [moona3k/macparakeet](https://github.com/moona3k/macparakeet)
- [zachswift615/speak2](https://github.com/zachswift615/speak2)
- [Beingpax/VoiceInk](https://github.com/Beingpax/VoiceInk)
- [FluidInference/swift-scribe](https://github.com/FluidInference/swift-scribe)
- [argmaxinc/WhisperKit](https://github.com/argmaxinc/WhisperKit)
- [FluidInference/FluidAudio](https://github.com/FluidInference/FluidAudio)
