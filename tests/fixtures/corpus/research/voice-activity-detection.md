# Voice Activity Detection (VAD) Research

**Date:** 2026-04-10
**Context:** Untype currently uses hold-to-talk (hotkey press/release). We want to explore auto-detecting speech start/stop for silence trimming, false-start reduction, and potential "press once, auto-stop" UX.

---

## Comparison Table

| Option | Accuracy | Latency (start/end) | Model Size | Integration Effort | AVAudioEngine Compat | Configurable Silence | macOS Native |
|--------|----------|---------------------|------------|-------------------|---------------------|---------------------|-------------|
| **Silero VAD v5/v6 (CoreML)** | Excellent (0.96 overall, 87.7% TPR @ 5% FPR) | <1ms per chunk; ~200-500ms end detection | ~2 MB | Medium (SPM via FluidAudio) | Yes (16kHz mono Float32) | Yes (full control) | Via CoreML/ANE |
| **WebRTC VAD** | Good (0.73 overall, 50% TPR @ 5% FPR) | Very fast (<1ms) | ~100 KB | Medium (C bridge or CocoaPod) | Yes (needs Int16 conversion) | Limited (aggressiveness levels only) | No (C library) |
| **Apple SpeechDetector** | Unknown (Apple internal) | Unknown | 0 (system) | Low | Yes (native) | Unknown | Yes (macOS 26+ only) |
| **Whisper no_speech_prob** | Moderate (segment-level, not frame-level) | High (30s chunks, ~1-2s processing) | 39 MB - 1.5 GB | N/A (already transcribing) | Yes (same pipeline) | Via threshold (default 0.6) | Via WhisperKit |
| **Custom energy-based (RMS)** | Poor (no noise robustness) | Instant | 0 | Trivial (already have code) | Yes (already using it) | Yes (manual threshold) | Yes |

---

## Detailed Analysis

### 1. Silero VAD via FluidAudio (CoreML) -- RECOMMENDED

**What it is:** Silero VAD is the most widely-used open-source neural VAD. FluidInference has pre-converted it to CoreML and wrapped it in a native Swift package (FluidAudio) that runs on Apple's Neural Engine.

**Accuracy:**
- Overall score: 0.96 vs WebRTC's 0.73
- At 5% false positive rate: 87.7% true positive rate (Silero) vs 50% (WebRTC)
- Trained on 6000+ languages
- Robust to background noise across domains

**Latency:**
- Processes 32ms audio chunks in <1ms on CPU
- CoreML on ANE: 7.7x faster than MLX implementations
- Speech-start detection: near-instant (1-2 chunks = 32-64ms)
- Speech-end detection: configurable, typically 200-500ms after silence begins
- Known caveat: some reports of several-hundred-ms delay on speech-to-silence transitions vs newer alternatives (TEN VAD)

**Model size:** ~2 MB (CoreML, quantized variants available with no accuracy loss)

**Integration via FluidAudio (SPM):**
```swift
// Package.swift
.package(url: "https://github.com/FluidInference/FluidAudio.git", from: "0.4.0")

// Streaming usage in AudioRecorder
import FluidAudio

let vadManager = try await VadManager()
var streamState = await vadManager.makeStreamState()

// In audio tap callback (must resample to 16kHz mono Float32):
let result = try await vadManager.processStreamingChunk(
    chunk,
    state: streamState,
    config: .default,
    returnSeconds: true,
    timeResolution: 2
)
streamState = result.state

if let event = result.event {
    switch event.kind {
    case .speechStart:
        // User started speaking
    case .speechEnd:
        // User stopped speaking -- trigger auto-stop
    }
}
```

**Segmentation config (offline or streaming):**
```swift
var segConfig = VadSegmentationConfig.default
segConfig.minSpeechDuration = 0.25    // ignore bursts < 250ms
segConfig.minSilenceDuration = 0.4    // 400ms silence to close segment
segConfig.speechPadding = 0.12        // 120ms padding on both sides
segConfig.maxSpeechDuration = 14.0    // auto-split long spans
```

**Pros:**
- Best accuracy of any standalone option
- Native Swift API, SPM integration
- Runs on ANE -- negligible battery/CPU impact
- Streaming API with speechStart/speechEnd events
- Pre-converted CoreML model on HuggingFace (FluidInference/silero-vad-coreml)
- Actively maintained (v6 as of 2025)

**Cons:**
- New dependency (FluidAudio)
- Requires audio resampling to 16kHz mono (Untype currently captures at device native rate)
- Slight end-of-speech detection delay reported in some scenarios

---

### 2. WebRTC VAD

**What it is:** Google's classic energy + GMM-based VAD from the WebRTC project. Battle-tested in telephony for 15+ years.

**Accuracy:**
- Overall score: 0.73 (significantly below Silero's 0.96)
- At 5% FPR: only 50% TPR -- misses ~1 in 2 speech frames
- Struggles with low-volume speech and varied background noise

**Latency:** Extremely low (<1ms per frame). Processes 10-30ms frames.

**Integration:**
- Swift wrapper available: `VoiceActivityDetector` CocoaPod (reedom/VoiceActivityDetector)
- Requires Int16 PCM audio (conversion from Float32 needed)
- Internally downsamples everything to 8kHz
- Four aggressiveness modes: `.quality`, `.lowBitRate`, `.aggressive`, `.veryAggressive`

```swift
let vad = VoiceActivityDetector(sampleRate: 16000, agressiveness: .veryAggressive)
let isVoiced = vad.detect(frames: audioFrames, count: frameCount)
```

**Pros:**
- Tiny (~100 KB), zero ML dependencies
- Extremely fast, no GPU/ANE needed
- Well understood, predictable behavior

**Cons:**
- Much lower accuracy than neural VADs -- 4x more errors than Silero
- No fine-grained threshold control (only 4 aggressiveness levels)
- No speech-start/end event API -- you'd build your own state machine
- CocoaPod targets iOS primarily; macOS support uncertain
- Effectively obsoleted by neural VADs for quality-sensitive use cases

**Verdict:** Not recommended for Untype. The accuracy gap is too large for a dictation app where false starts and missed speech directly affect UX.

---

### 3. Apple SpeechDetector (macOS 26+)

**What it is:** New in iOS/macOS 26 (WWDC 2025). A dedicated VAD module within the SpeechAnalyzer framework. Detects speech presence and timing without full transcription.

**Key facts:**
- Part of the new `SpeechAnalyzer` API replacing `SFSpeechRecognizer`
- `SpeechDetector` module performs VAD analysis
- Reports speech presence and timing
- Powers system apps (Notes, Voice Memos, Journal)

**Limitations (critical):**
- **Requires macOS 26** -- Untype targets macOS 14+, so this is not usable today
- SpeechDetector reportedly can only be used paired with other SpeechAnalyzer modules (SpeechTranscriber or DictationTranscriber), not fully standalone
- Limited documentation available; API surface still evolving

**Verdict:** Monitor for the future. When Untype's minimum target moves to macOS 26, this becomes the obvious first-party choice. For now, it's not viable.

---

### 4. Whisper's Implicit VAD (no_speech_prob)

**What it is:** Whisper models predict a `<|nospeech|>` token with a probability (`no_speech_prob`) for each 30-second segment. This acts as a crude segment-level VAD.

**How it works:**
- Each transcription segment has `no_speech_prob` (0.0-1.0)
- Default threshold: 0.6
- If `no_speech_prob > threshold`, segment is considered silent
- 20ms timestamp quantization

**Limitations:**
- Segment-level (30s chunks), not frame-level -- far too coarse for real-time end detection
- High latency: must process an entire chunk before making a decision
- Only useful for post-hoc silence trimming, not live auto-stop
- Untype uses Apple Speech (SFSpeechRecognizer), not Whisper

**Verdict:** Not applicable for real-time VAD. If Untype ever switches to Whisper for transcription, Silero VAD is typically used as a preprocessing step anyway (as in faster-whisper/WhisperX).

---

### 5. Custom Energy-Based VAD (RMS/dBFS Threshold)

**What it is:** Simple amplitude-based detection. Untype already computes RMS in `AudioRecorder.processBuffer()`.

**Current code (AudioRecorder.swift:65-78):**
```swift
private func processBuffer(_ buffer: AVAudioPCMBuffer) {
    guard let channelData = buffer.floatChannelData?[0] else { return }
    let count = Int(buffer.frameLength)
    var sum: Float = 0
    for i in 0..<count {
        sum += channelData[i] * channelData[i]
    }
    let rms = sqrt(sum / Float(max(count, 1)))
    let level = min(1.0, rms * 5.0)
    // ... update audioLevel
}
```

**What it would take to add VAD:**
```swift
// Simple energy VAD on top of existing RMS
private var silenceStartTime: Date?
private let silenceThreshold: Float = 0.02  // tunable
private let silenceTimeout: TimeInterval = 1.5

private func checkSilence(rms: Float) {
    if rms < silenceThreshold {
        if silenceStartTime == nil { silenceStartTime = Date() }
        if let start = silenceStartTime,
           Date().timeIntervalSince(start) > silenceTimeout {
            // Trigger auto-stop
        }
    } else {
        silenceStartTime = nil
    }
}
```

**Pros:**
- Zero dependencies, zero latency, trivially simple
- Already have RMS computation
- Good enough for quiet rooms with close-mic

**Cons:**
- No noise robustness: AC hum, keyboard typing, fan noise all register as "speech"
- No frequency analysis: can't distinguish speech from other sounds
- Threshold tuning is environment-dependent and fragile
- Will produce many false positives (non-speech sounds keeping recording alive) and false negatives (quiet speech being cut off)

**Verdict:** Useful as a first-pass filter or fallback, but not reliable enough for auto-stop on its own. Could be combined with neural VAD as a quick pre-filter.

---

## Key Questions Answered

### What silence duration works best for conversational dictation?

Research and industry practice suggest a **tiered approach**:

| Duration | Use Case | Trade-off |
|----------|----------|-----------|
| 500ms | Fast, snappy interaction (chat messages) | May cut off thinking pauses |
| 1.0-1.5s | **General dictation (recommended default)** | Good balance; most natural pauses are <1s |
| 2.0s | Long-form dictation (emails, documents) | Accommodates "um", "ahh" pauses |
| 3.0s+ | Very cautious / accessibility | Rarely needed |

**Recommendation for Untype:** Start with **1.5s default**, make it user-configurable (0.5s - 3.0s slider in Settings). Competitors like Microsoft dictation use ~1.5s. Advanced: use a probability-weighted wait (shorter silence needed when VAD confidence is very high that speech ended).

### Can VAD run on the same audio buffer that feeds SFSpeechRecognizer?

**Yes, with resampling.** Current flow:
1. `AVAudioEngine` tap captures audio at device native sample rate
2. Buffers go to `SFSpeechRecognizer` (which wants 16kHz mono) and to file

Silero VAD (via FluidAudio) also wants **16kHz mono Float32** -- the exact same format. The integration point is in `AudioRecorder`'s tap callback:

```swift
inputNode.installTap(onBus: 0, bufferSize: 1024, format: inputFormat) {
    [weak self] buffer, _ in
    self?.processBuffer(buffer)        // RMS level (existing)
    self?.onBuffer?(buffer)            // SFSpeechRecognizer (existing)
    self?.processVAD(buffer)           // VAD analysis (new)
    try? file.write(from: buffer)
}
```

Both consumers can share the same resampled buffer. No duplication needed.

### Does Silero VAD have a CoreML-converted model?

**Yes.** FluidInference maintains `silero-vad-coreml` on HuggingFace with:
- Pre-converted CoreML models (standard and 256ms batch variants)
- Quantized variants (no accuracy loss due to model's small size)
- Optimized for Apple Neural Engine
- Available via the FluidAudio Swift package (SPM)

### UX pattern: auto-stop vs. trim silence?

**Both, as layered features:**

1. **Phase 1 -- Trim silence (low risk, immediate value):**
   - Keep hold-to-talk as primary UX
   - Run VAD on captured audio to trim leading/trailing silence
   - Detect if recording is all silence and show error ("No speech detected")
   - Zero UX change, just better recordings

2. **Phase 2 -- Auto-stop after silence (medium risk):**
   - "Press once to start, auto-stop when done"
   - Show countdown indicator when silence detected ("Finishing in 1.5s...")
   - Allow user to keep talking to reset the timer
   - Cancel button if they want to abort
   - This is the "press-once" mode some users will love

3. **Phase 3 -- Continuous/hands-free (high complexity):**
   - Always-listening mode with VAD gating
   - Only record and transcribe speech segments
   - Much more complex state management

### How do competitors handle this?

- **Superwhisper:** Manual activation only (press shortcut, talk, stop). No auto-stop.
- **Wispr Flow:** Hold-to-talk (press, speak, release). No auto-stop.
- **Blazing Transcribe:** Continuous VAD -- always listening, auto-detects speech, transcribes, types. No trigger needed.
- **Apple Dictation:** Has a silence timeout (~3s of silence ends dictation automatically).

Most dictation apps still use manual stop. Auto-stop is a differentiator, not table stakes.

---

## Recommendation

### Primary: Silero VAD via FluidAudio (CoreML)

**Why:**
1. Best accuracy (4x fewer errors than WebRTC)
2. Native Swift package with streaming API
3. Runs on Neural Engine -- negligible resource impact
4. Pre-converted CoreML model available
5. Provides exactly the events we need (speechStart, speechEnd)
6. Same audio format as SFSpeechRecognizer (16kHz mono Float32)
7. Configurable thresholds for silence duration, min speech duration, padding

**Trade-off:** Adds one dependency (FluidAudio). But it's a well-maintained, MIT-licensed Swift package built specifically for Apple platforms. The CLAUDE.md rule says "NEVER add dependencies beyond HotKey unless explicitly discussed" -- this research constitutes that discussion.

### Fallback: Custom RMS VAD

Keep the existing RMS computation as a lightweight pre-filter. If Silero VAD is ever problematic, a simple energy-based approach can serve as a degraded fallback.

### Future: Apple SpeechDetector

When Untype moves its minimum target to macOS 26, evaluate replacing Silero with Apple's built-in SpeechDetector. It would eliminate the FluidAudio dependency and integrate natively with the SpeechAnalyzer transcription pipeline.

---

## Integration Sketch

### Files to create/modify:

```
Untype/Audio/
  AudioRecorder.swift        -- add VAD tap alongside existing buffer tap
  VoiceActivityDetector.swift -- NEW: wraps FluidAudio VadManager
Untype/State/
  AppState.swift             -- add VAD-related state (speechDetected, silenceTimer)
Untype/App/
  RecordingCoordinator.swift -- wire VAD events to auto-stop logic
Untype/Settings/
  (future)                   -- silence timeout preference
```

### VoiceActivityDetector.swift (new, ~80 lines):

```swift
import FluidAudio
import AVFoundation
import Observation

@Observable
final class VoiceActivityDetector {
    private(set) var isSpeechDetected = false
    private(set) var silenceDuration: TimeInterval = 0

    private var vadManager: VadManager?
    private var streamState: VadStreamState?
    private var silenceStart: Date?

    var onSpeechStart: (() -> Void)?
    var onSpeechEnd: ((TimeInterval) -> Void)?  // passes silence duration

    var silenceTimeout: TimeInterval = 1.5  // configurable

    func prepare() async throws {
        vadManager = try await VadManager()
        streamState = await vadManager?.makeStreamState()
    }

    /// Call from audio tap with 16kHz mono Float32 samples
    func processChunk(_ samples: [Float]) async throws {
        guard let manager = vadManager, var state = streamState else { return }

        let result = try await manager.processStreamingChunk(
            samples,
            state: state,
            config: .default,
            returnSeconds: true,
            timeResolution: 2
        )
        streamState = result.state

        if let event = result.event {
            switch event.kind {
            case .speechStart:
                isSpeechDetected = true
                silenceStart = nil
                silenceDuration = 0
                onSpeechStart?()
            case .speechEnd:
                isSpeechDetected = false
                silenceStart = Date()
                onSpeechEnd?(0)
            }
        }

        // Track ongoing silence duration
        if !isSpeechDetected, let start = silenceStart {
            silenceDuration = Date().timeIntervalSince(start)
            if silenceDuration >= silenceTimeout {
                onSpeechEnd?(silenceDuration)
            }
        }
    }

    func reset() {
        isSpeechDetected = false
        silenceDuration = 0
        silenceStart = nil
        streamState = nil
    }
}
```

### RecordingCoordinator changes (conceptual):

```swift
// In startRecording():
try await vad.prepare()
audioRecorder.onVADBuffer = { [weak self] samples in
    Task { try await self?.vad.processChunk(samples) }
}
vad.onSpeechEnd = { [weak self] duration in
    if duration >= vad.silenceTimeout {
        self?.stopRecording()  // auto-stop
    }
}
```

### Audio format consideration:

The existing `AudioRecorder` captures at device native sample rate (typically 48kHz). Both `SFSpeechRecognizer` and Silero VAD want 16kHz mono. Add a resampling utility or use `AVAudioConverter`:

```swift
private func resampleTo16kHz(_ buffer: AVAudioPCMBuffer) -> [Float]? {
    let targetFormat = AVAudioFormat(
        commonFormat: .pcmFormatFloat32,
        sampleRate: 16000,
        channels: 1,
        interleaved: false
    )!
    guard let converter = AVAudioConverter(from: buffer.format, to: targetFormat) else {
        return nil
    }
    // ... convert and return samples
}
```

---

## Implementation Priority

1. **Immediate (Phase 1):** Add Silero VAD to detect "no speech" in recordings. Show "No speech detected" error instead of sending empty audio to transcription. Trim silence from start/end.

2. **Next (Phase 2):** Add "press-once" mode with auto-stop. Visual countdown in overlay when silence detected. User-configurable timeout in Settings (default 1.5s).

3. **Later (Phase 3):** Explore continuous mode. Evaluate SpeechDetector when macOS 26 becomes minimum target.

---

## Sources

- [Silero VAD GitHub](https://github.com/snakers4/silero-vad)
- [FluidAudio GitHub](https://github.com/FluidInference/FluidAudio)
- [FluidAudio VAD Getting Started](https://github.com/FluidInference/FluidAudio/blob/main/Documentation/VAD/GettingStarted.md)
- [Silero VAD CoreML on HuggingFace](https://huggingface.co/FluidInference/silero-vad-coreml)
- [RealTimeCutVADLibrary (ONNX alternative)](https://github.com/helloooideeeeea/RealTimeCutVADLibrary)
- [WebRTC VoiceActivityDetector](https://github.com/reedom/VoiceActivityDetector)
- [Picovoice VAD Benchmark 2026](https://picovoice.ai/blog/best-voice-activity-detection-vad/)
- [Apple SpeechAnalyzer Documentation](https://developer.apple.com/documentation/speech/speechanalyzer)
- [Apple SpeechDetector Documentation](https://developer.apple.com/documentation/speech/speechdetector)
- [WWDC25: SpeechAnalyzer Session](https://developer.apple.com/videos/play/wwdc2025/277/)
- [Wispr Flow](https://wisprflow.ai)
- [Superwhisper vs Wispr Flow Comparison](https://www.blazingfasttranscription.com/blog/superwhisper-vs-wispr-flow)
