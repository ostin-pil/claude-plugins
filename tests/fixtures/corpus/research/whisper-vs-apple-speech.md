# On-Device Speech-to-Text: Whisper vs Apple Speech

Research for Untype (macOS voice-to-message app). Target: macOS 14+, Swift 5.9+, Apple Silicon.

**Date:** 2026-04-10

---

## Executive Summary

For Untype's MVP, **keep Apple Speech (SFSpeechRecognizer) as the primary engine** -- it is free, zero-download, streams partial results natively, and covers English/Russian/Chinese. When accuracy matters more than latency (the "final pass" after recording stops), add **WhisperKit** as an optional second pass. WhisperKit is the only Whisper variant that is Swift-native, ships via SPM, uses CoreML/Neural Engine, and now supports streaming. Looking ahead, Apple's **SpeechAnalyzer** (macOS Tahoe / macOS 26, WWDC 2025) will likely replace SFSpeechRecognizer entirely and close much of the accuracy gap with Whisper.

---

## Option Comparison Table

| Criterion | Apple Speech (SFSpeech) | WhisperKit (Argmax) | whisper.cpp | MLX Whisper | Distil-Whisper |
|---|---|---|---|---|---|
| **Engine** | Apple proprietary | Whisper via CoreML/ANE | Whisper via GGML/C++ | Whisper via MLX (GPU) | Distilled Whisper (any runtime) |
| **WER (English)** | ~8-12% (estimated, on-device) | 2.2% (large-v3-turbo) | Same as base Whisper model | Same as base Whisper model | Within 1% of large-v3 |
| **WER (Russian)** | Supported, accuracy unknown | ~5-8% (large-v3) | Same | Same | English-focused, limited multilingual |
| **WER (Chinese)** | Supported (CER metric) | ~5-10% CER (large-v3) | Same | Same | English-focused |
| **Streaming partials** | Native, real-time | Yes (LocalAgreement policy, dual streams) | Pseudo-streaming (chunked re-transcription) | No native streaming | Depends on runtime |
| **Model sizes** | Built-in (no choice) | tiny to large-v3-turbo (CoreML) | tiny to large-v3 (GGML) | tiny to large-v3 | distil-large-v2, distil-large-v3 |
| **Disk (recommended model)** | 0 MB (built-in) | ~950 MB (large-v3-turbo) | ~500 MB (medium, GGML) | ~500 MB (medium) | ~756 MB |
| **RAM usage** | Managed by OS | ~1-3 GB (model dependent) | ~1-5 GB (model dependent) | ~1-5 GB | ~2-3 GB |
| **RTF on M1** | Real-time (streaming) | ~0.45s latency (streaming) | ~0.3x for medium (3 min for 10 min audio) | ~30-40% faster than whisper.cpp | ~6x faster than large-v3 |
| **Swift integration** | Native framework (Speech.framework) | SPM package, pure Swift | C API via whisper.spm or SwiftWhisper (bridging) | Python only (pip) | Python only (pip) |
| **Offline** | Yes (requiresOnDeviceRecognition) | Yes | Yes | Yes | Yes |
| **Languages** | ~50 locales (10+ on-device) | 99 languages | 99 languages | 99 languages | Primarily English |
| **License** | Proprietary (free) | MIT | MIT | MIT | MIT |
| **First-run download** | None | 950 MB - 3.1 GB | 75 MB - 3 GB | 75 MB - 3 GB | ~756 MB |
| **Cost** | Free | Free | Free | Free | Free |

---

## Detailed Analysis

### 1. Apple Speech (SFSpeechRecognizer) -- Current Implementation

**Strengths:**
- Zero setup, zero download, zero cost
- Native streaming with partial results via `shouldReportPartialResults`
- Tight OS integration (permissions, energy management)
- Supports English, Russian (`ru_RU`), Chinese (`zh_CN`, `zh_TW`, `zh_HK`, `yue_CN`)
- No model management, no disk overhead
- Privacy: fully on-device with `requiresOnDeviceRecognition = true`

**Weaknesses:**
- Accuracy is mid-tier (~8-12% WER for English, worse for noisy/conversational speech)
- No model choice -- you get whatever Apple ships
- Limited customization (vocabulary hints via `contextualStrings` only)
- 1-minute recording limit per recognition task (can be worked around)
- Deprecated path: Apple introduced SpeechAnalyzer at WWDC 2025 as the replacement

**Conversational speech handling:**
Apple Speech handles casual dictation reasonably well but struggles with:
- Code-switching (mixing languages mid-sentence)
- Heavy accents or dialectal speech
- Noisy environments
- Technical vocabulary

**Future: SpeechAnalyzer (macOS Tahoe / macOS 26)**
Apple announced SpeechAnalyzer at WWDC 2025 as a direct replacement for SFSpeechRecognizer. Key improvements:
- 55% faster than Whisper in Apple's benchmarks
- Better long-form and distant audio handling
- New SpeechTranscriber class with modern async API
- Matches mid-tier Whisper accuracy
- Supported locales include `ru_RU`, `zh_CN`, `zh_TW`, `ja_JP`, `ko_KR`, and 30+ more
- Requires macOS 26 (Tahoe) minimum -- not usable on macOS 14/15

### 2. WhisperKit (Argmax) -- Recommended Whisper Option

**Strengths:**
- Pure Swift, SPM-native: `.package(url: "https://github.com/argmaxinc/WhisperKit.git", from: "0.9.0")`
- CoreML compilation targets Neural Engine (ANE) for peak efficiency
- Streaming support via LocalAgreement policy (dual output streams)
- 2.2% WER with large-v3-turbo -- best accuracy among on-device options
- 0.45s mean streaming latency
- 99 languages, strong multilingual performance
- Active development, backed by Argmax (Apple acquired/partnered for SpeechAnalyzer)
- CLI tool for testing: `swift run whisperkit-cli transcribe --stream`

**Weaknesses:**
- First-run model download: 950 MB (large-v3-turbo) to 3.1 GB (large-v3)
- Needs ~2x disk space temporarily during download/extraction
- First inference is slow (CoreML compilation to device-specific format)
- Adds ~950 MB to app footprint (or requires runtime download)
- RAM: 1-3 GB depending on model

**Model recommendations for Untype:**
| Model | Disk | RAM | RTF (M1) | WER (en) | Use case |
|---|---|---|---|---|---|
| tiny | ~75 MB | ~400 MB | 27x faster than RT | ~15% | Not recommended |
| base | ~150 MB | ~500 MB | 16x faster than RT | ~12% | Fallback/testing |
| small | ~500 MB | ~1 GB | 6x faster than RT | ~8% | Good balance |
| large-v3-turbo | ~950 MB | ~1.5 GB | ~real-time streaming | ~2.2% | Best accuracy |

**Integration approach:**
```swift
// Package.swift
.package(url: "https://github.com/argmaxinc/WhisperKit.git", from: "0.9.0")

// Usage
import WhisperKit
let pipe = try await WhisperKit(model: "large-v3-turbo")
let result = try await pipe.transcribe(audioPath: url.path)
```

### 3. whisper.cpp

**Strengths:**
- Lightweight C/C++ implementation, very portable
- CoreML acceleration available (3x speedup on ANE)
- Smallest memory footprint of Whisper options
- Mature, battle-tested codebase
- GGML quantized models are smaller than CoreML equivalents

**Weaknesses:**
- No true streaming -- "stream" mode is chunked re-transcription with overlap
- Swift integration is awkward: C bridging headers, manual memory management, callback APIs
- SPM package (whisper.spm) exists but is not actively maintained
- SwiftWhisper wrapper exists but adds another dependency layer
- No native async/await support -- requires manual bridging

**Streaming limitation (critical for Untype):**
whisper.cpp's "stream" mode captures audio in chunks (configurable via `--step` and `--length` flags), runs full inference on each chunk, and concatenates results. This is fundamentally different from Apple Speech's true streaming where partial results update continuously. For Untype's live overlay UX, this creates a choppy, delayed experience.

### 4. MLX Whisper

**Strengths:**
- 30-40% faster than whisper.cpp on Apple Silicon
- Uses MLX framework (Apple's ML array library) for GPU acceleration
- Good for batch transcription workloads

**Weaknesses:**
- Python-only (`pip install mlx-whisper`) -- no Swift API
- No streaming support
- Would require running a Python subprocess or local HTTP server
- Adds Python runtime dependency to a native Swift app
- Not suitable for a native macOS app architecture

**Verdict:** Not viable for Untype. The Python dependency and lack of Swift integration make it incompatible with the project's native Swift architecture.

### 5. Distil-Whisper

**Strengths:**
- 6x faster than Whisper large-v3 with <1% WER degradation
- 49% smaller model (756M vs 1.55B parameters)
- Fewer hallucinations and repeated words than standard Whisper
- Good accuracy-to-speed ratio

**Weaknesses:**
- Primarily optimized for English -- limited multilingual support
- Not a runtime -- needs whisper.cpp, WhisperKit, or MLX as the execution backend
- distil-large-v3 CoreML models available via WhisperKit
- Russian and Chinese support is significantly worse than full Whisper models

**Verdict:** Viable as a WhisperKit model variant for English-only use cases. Not suitable as a standalone option for multilingual support.

---

## Key Questions Answered

### Can Whisper stream partial results like Apple Speech?

**WhisperKit: Yes**, with caveats. WhisperKit implements a LocalAgreement streaming policy that produces dual output streams -- a "confirmed" stream of stable text and a "speculative" stream of tentative text. This is architecturally different from Apple Speech's native streaming but achieves a similar UX. Latency is ~0.45 seconds.

**whisper.cpp: No**, not truly. Its "stream" mode re-transcribes overlapping audio chunks, which creates visible text flickering and higher latency. Not suitable for a live overlay.

**MLX Whisper: No.** Batch-only.

### What's the accuracy difference for messy conversational speech?

Whisper models (especially large-v3 and large-v3-turbo) significantly outperform Apple Speech on conversational, noisy, and accented speech. Whisper was trained on 680,000 hours of diverse, messy real-world audio. Apple Speech was trained on cleaner dictation-style data.

For Untype's use case (voice messages, casual speech, potentially noisy environments):
- Apple Speech: adequate for clear dictation, degrades with noise/accents
- Whisper large-v3-turbo: robust across conditions, 2.2% WER even on challenging audio

### Can we run both: Apple Speech for streaming, Whisper for final pass?

**Yes, this is the recommended architecture for Untype.** The dual-engine approach:

1. **Live phase:** Apple Speech streams partial results to the overlay in real-time (zero latency, no download required)
2. **Final phase:** When the user stops recording, run WhisperKit on the complete audio buffer for a high-accuracy final transcription
3. **Replace:** Swap the Apple Speech partial text with WhisperKit's final text before insertion

This gives the best of both worlds: instant visual feedback during recording, and high accuracy for the final inserted text. The WhisperKit final pass on a typical voice message (5-30 seconds) completes in under 1 second on Apple Silicon.

### What model size gives the best accuracy/speed trade-off?

For Untype's use case (short voice messages, 5-60 seconds):

**Recommended: `large-v3-turbo`** (~950 MB disk, ~1.5 GB RAM)
- Best accuracy (2.2% WER)
- Real-time streaming capable
- Optimized for Neural Engine
- For short audio clips, inference completes in <1 second

**Fallback: `small`** (~500 MB disk, ~1 GB RAM)
- Good accuracy (~8% WER)
- 6x faster than real-time
- Reasonable for devices with limited RAM

### WhisperKit CoreML vs whisper.cpp vs MLX performance?

On Apple Silicon (M1-M4):
- **WhisperKit (CoreML/ANE):** Fastest for streaming, best Neural Engine utilization, lowest power consumption
- **MLX Whisper (GPU):** 30-40% faster than whisper.cpp for batch, but Python-only
- **whisper.cpp (CPU+CoreML):** Good batch performance, 3x speedup with CoreML, but no true streaming

WhisperKit wins for Untype because it combines Neural Engine optimization with native Swift APIs and true streaming support.

### Disk space and first-run download?

| Option | First-run download | Final disk usage | Temp space needed |
|---|---|---|---|
| Apple Speech | None | 0 (built-in) | None |
| WhisperKit (large-v3-turbo) | ~950 MB | ~950 MB | ~1.9 GB |
| WhisperKit (small) | ~500 MB | ~500 MB | ~1 GB |
| whisper.cpp (medium GGML) | ~500 MB | ~500 MB | ~500 MB |

First-run UX consideration: WhisperKit needs to download and compile the CoreML model on first use. The download can be done in the background, and the first inference is slower due to ANE compilation. Subsequent runs are fast.

---

## Recommended Architecture for Untype

### Phase 1: MVP (Current)
Keep Apple Speech only. It works, streams, and requires no downloads.

### Phase 2: Accuracy Upgrade
Add WhisperKit as an optional "enhanced accuracy" mode:

```
Recording starts
  |
  v
Apple Speech streams partials --> overlay shows live text
  |
  v
User releases hotkey (recording stops)
  |
  v
WhisperKit runs final pass on full audio buffer (~0.5-1s)
  |
  v
Final text replaces partial text --> inserted into target app
```

**Integration steps:**
1. Add WhisperKit SPM dependency
2. Create `WhisperKitService` conforming to a `TranscriptionProvider` protocol
3. Download model on first launch (background, with progress indicator)
4. Run WhisperKit final pass after recording stops
5. Settings toggle: "Enhanced accuracy (requires ~1 GB download)"

### Phase 3: Future (macOS 26+)
When Untype drops macOS 14/15 support, migrate from SFSpeechRecognizer to SpeechAnalyzer/SpeechTranscriber. This may eliminate the need for WhisperKit entirely, as Apple's new engine matches mid-tier Whisper accuracy with zero download.

---

## Risk Assessment

| Risk | Mitigation |
|---|---|
| WhisperKit model download fails or is slow | Cache model, retry logic, fallback to Apple Speech |
| WhisperKit increases app RAM to 1.5+ GB | Use `small` model variant, or make it opt-in |
| Apple deprecates SFSpeechRecognizer before macOS 26 adoption | WhisperKit becomes primary engine |
| First-run CoreML compilation is slow (30-60s) | Show progress, do it in background on first launch |
| User has limited disk space | Check available space before download, show size warning |
| Distil-Whisper multilingual quality is poor | Use full large-v3-turbo for multilingual users |

---

## Sources

- [WhisperKit GitHub (Argmax)](https://github.com/argmaxinc/WhisperKit)
- [WhisperKit ICML 2025 Paper](https://arxiv.org/abs/2507.10860)
- [WhisperKit Benchmarks](https://github.com/argmaxinc/WhisperKit/blob/main/BENCHMARKS.md)
- [whisper.cpp GitHub](https://github.com/ggml-org/whisper.cpp)
- [whisper.cpp Stream Example](https://github.com/ggml-org/whisper.cpp/blob/master/examples/stream/README.md)
- [whisper.spm (Swift Package)](https://github.com/ggerganov/whisper.spm)
- [MLX Whisper (PyPI)](https://pypi.org/project/mlx-whisper/)
- [Distil-Whisper (HuggingFace)](https://huggingface.co/distil-whisper/distil-large-v3)
- [Whisper Model Sizes Explained](https://openwhispr.com/blog/whisper-model-sizes-explained)
- [Apple SpeechAnalyzer Documentation](https://developer.apple.com/documentation/speech/speechanalyzer)
- [Apple SpeechAnalyzer and WhisperKit (Argmax Blog)](https://www.argmaxinc.com/blog/apple-and-argmax)
- [WWDC 2025: SpeechAnalyzer Session](https://developer.apple.com/videos/play/wwdc2025/277/)
- [Apple Speech vs Whisper Speed Tests (MacStories)](https://www.macstories.net/stories/hands-on-how-apples-new-speech-apis-outpace-whisper-for-lightning-fast-transcription/)
- [Whisper Performance on Apple Silicon](https://www.voicci.com/blog/apple-silicon-whisper-performance.html)
- [Mac Whisper Speed Test (Benchmark Tool)](https://github.com/anvanvan/mac-whisper-speedtest)
- [OpenAI Whisper Large-V3 (HuggingFace)](https://huggingface.co/openai/whisper-large-v3)
- [WhisperKit CoreML Models (HuggingFace)](https://huggingface.co/argmaxinc/whisperkit-coreml)
