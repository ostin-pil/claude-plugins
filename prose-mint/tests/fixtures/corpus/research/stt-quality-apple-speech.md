# STT Quality — Tuning SFSpeechRecognizer for Untype

**Date:** 2026-04-14
**Context:** Session 24 flagged Apple Speech output quality as the real
quality bottleneck in Untype, upstream of any LLM cleanup. This note
enumerates every quality-affecting knob on `SFSpeechRecognizer` /
`SFSpeechAudioBufferRecognitionRequest` on macOS, notes which ones
Untype currently uses, and prioritizes the wins.

Sources: Apple developer docs, WWDC23 session 10101 "Customize on-device
speech recognition", and the `dotnet/macios` Speech bindings (authoritative
for exact macOS `API_AVAILABLE` annotations).

---

## Executive summary

1. **`addsPunctuation = true`** (macOS 13+, off by default) is the single
   biggest free UX win. Without it users have to speak punctuation
   manually. Flip it unconditionally — Untype's deployment target is
   macOS 14. **Shipping this slice.**
2. **`contextualStrings`** is a cheap phonetic bias hint for domain vocab.
   Useful for product-specific terms like "Untype" itself. Wire the
   infrastructure in; seed a minimal baseline. Growing the list from user
   history is a later UX decision. **Shipping this slice (infrastructure).**
3. **Custom `SFSpeechLanguageModel`** (macOS 14+) is the biggest quality
   lever below swapping engines, but requires an offline build step, a
   binary artifact, and a slow first-launch `prepareCustomLanguageModel`
   call. Separate spike — scoped below.
4. **Per-segment confidence** and **alternative transcriptions** are
   already in the result object and we throw them away. Potential to dim
   low-confidence words in the overlay and/or feed confidence metadata
   into the LLM cleanup pass. Follow-up.
5. **Server-side recognition** (flipping `requiresOnDeviceRecognition`
   off) would cost Untype its privacy story, its offline capability, and
   its custom-LM compatibility. Not worth it — WhisperKit is a better
   accuracy upgrade path per `research/whisper-vs-apple-speech.md`.

---

## SFSpeechRecognitionRequest — quality knobs

| Property | Type | macOS floor | On-device OK? | Untype today | Notes |
|---|---|---|---|---|---|
| `shouldReportPartialResults` | `Bool` | 10.15 | yes | `true` | Correct — drives the live overlay. |
| `taskHint` | `SFSpeechRecognitionTaskHint` | 10.15 | yes | `.dictation` | Correct for voice-to-text. |
| `requiresOnDeviceRecognition` | `Bool` | 10.15 | — | `true` | Privacy + offline. Keep. |
| `contextualStrings` | `[String]` | 10.15 | yes | **unset** | Soft phonetic bias. Not a dictionary — novel words still fail. |
| `addsPunctuation` | `Bool` | **13.0** | yes | **unset (false)** | Auto period/comma/question-mark. Off by default. |
| `interactionIdentifier` | `String?` | 10.15, deprecated 13.0 | — | unset | Legacy analytics. Skip. |
| `customizedLanguageModel` | `SFSpeechLanguageModel.Configuration?` | **14.0** | **requires on-device** | unset | See custom-LM section. |

## Result-level signals we ignore today

| API | macOS floor | Potential use |
|---|---|---|
| `SFSpeechRecognitionResult.transcriptions` | 10.15 | Alternative transcriptions beyond `bestTranscription` — feed into LLM reranking. |
| `SFTranscriptionSegment.confidence` | 10.15 | Float 0.0–1.0 per word. Dim low-confidence words in overlay, or hint LLM cleanup. |
| `SFTranscriptionSegment.alternativeSubstrings` | 10.15 | N-best alternatives per word span. |
| `SFSpeechRecognitionResult.speechRecognitionMetadata` | 11.0 | Speaking rate, pause duration, voice analytics. Useful for VAD/endpointing. |

## SFSpeechRecognizer — class-level knobs

- `SFSpeechRecognizer.supportsOnDeviceRecognition` — varies by locale. Untype currently assumes on-device works for any `Locale.current`; this is a latent bug for users in unsupported locales. Follow-up.
- `SFSpeechRecognizer.defaultTaskHint` — equivalent to setting per-request; skip.

---

## Custom SFSpeechLanguageModel — scope

**Availability:** macOS 14 / iOS 17. **Only with `requiresOnDeviceRecognition = true`** — Apple's privacy guarantee.

**Training data model** (`SFCustomLanguageModelData`, iOS 17+):
- `PhraseCount(phrase:count:)` — literal phrase with frequency weight.
- `PhraseCountsFromTemplates` — class/template macro expansion (e.g. class `opening: ["Ruy Lopez", "Sicilian"]` + template `"Let's play <opening>"` with count 500 expands the full combinatorial space).
- `CustomPronunciation(phrase:pronunciations:)` — X-SAMPA pronunciations for novel words.

**Build → ship → runtime:**
1. Offline build step constructs `SFCustomLanguageModelData` and exports a binary file (conventionally `.bin`).
2. Ship the `.bin` inside the app bundle (or download on first launch).
3. At app start, off the main thread:
   ```swift
   try await SFSpeechLanguageModel.prepareCustomLanguageModel(
       for: trainingBinURL,
       clientIdentifier: "com.untype.app.lm.v1",
       configuration: config
   )
   ```
   Compiles the blob into two derived files (`languageModel` and `vocabulary` URLs). Apple warns this has "significant latency" — seconds, proportional to phrase count.
4. Per-request:
   ```swift
   request.requiresOnDeviceRecognition = true  // mandatory
   request.customizedLanguageModel = lmConfig
   ```

**Gotchas:**
- `clientIdentifier` is the cache key. Bump it (`...v1` → `...v2`) whenever training data changes, otherwise prepared files aren't rebuilt.
- `customizedLanguageModel` is silently ignored without `requiresOnDeviceRecognition = true`.
- `SFSpeechLanguageModel.Configuration` takes file URLs that must exist at request start.

**Recommended Untype spike (separate session):**
- Add a tiny macOS CLI in `tools/` that takes a JSON vocab file and writes a `CustomLMData.bin`.
- Initial seed: product vocab ("Untype"), common message openers, user's contacts (if accessible), slash commands.
- Bundle `.bin` at build time. Iterate: later, regenerate per-user from local usage history.
- First-launch `prepareCustomLanguageModel` hidden behind a splash/loading state.

---

## Server-side vs on-device — don't

Flipping `requiresOnDeviceRecognition = false` would:
- Lose the privacy story (audio hits Apple servers).
- Lose offline capability entirely.
- Silently disable `customizedLanguageModel`, closing off the biggest quality lever.
- Give modest quality gains that WhisperKit large-v3-turbo would match or beat — per `research/whisper-vs-apple-speech.md`, WhisperKit is the recommended accuracy upgrade path.

No exploration needed. Keep `requiresOnDeviceRecognition = true`.

---

## This session — what shipped

- `addsPunctuation = true` (unconditional — deployment target is macOS 14, floor is 13).
- `contextualStrings` wired from a private baseline constant containing product-specific vocab ("Untype" itself). No settings UI; growing the list from user data is a follow-up.
- This research note saved to `research/stt-quality-apple-speech.md`.

## Follow-ups

- Custom LM spike (see scope above) — biggest pending quality lever.
- Surface `supportsOnDeviceRecognition` in `PermissionsChecker` / locale fallback.
- Consume `SFTranscriptionSegment.confidence` — dim low-confidence words in overlay, pass metadata to LLM cleanup.
- Extract `TranscriptionProvider` protocol before adding any alternative STT backend (local alt or cloud). Untype/Transcription/ currently has only `AppleSpeechService.swift`; there's no seam.
- User-settings pathway for `contextualStrings` (custom terms, contacts import).

## References

- Apple: [SFSpeechAudioBufferRecognitionRequest](https://developer.apple.com/documentation/speech/sfspeechaudiobufferrecognitionrequest)
- Apple: [SFSpeechLanguageModel](https://developer.apple.com/documentation/speech/sfspeechlanguagemodel)
- Apple: [SFCustomLanguageModelData](https://developer.apple.com/documentation/speech/sfcustomlanguagemodeldata)
- [WWDC23 10101 — Customize on-device speech recognition](https://developer.apple.com/videos/play/wwdc2023/10101/)
- [dotnet/macios Speech bindings — xcode26.0 b1](https://github.com/dotnet/macios/wiki/Speech-macOS-xcode26.0-b1) — authoritative macOS availability floors
- [Compiler-Inc/SpeechModelBuilder](https://github.com/Compiler-Inc/SpeechModelBuilder) — reference `SFCustomLanguageModelData` builder
- [Compiler-Inc/Transcriber](https://github.com/Compiler-Inc/Transcriber) — reference custom-LM wrapper (iOS 17+/macOS 14+)
- Existing Untype research: `research/whisper-vs-apple-speech.md`
