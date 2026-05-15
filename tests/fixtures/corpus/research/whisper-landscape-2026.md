# Whisper & Alternatives — Landscape (April 2026)

Companion to `whisper-vs-apple-speech.md` (deep comparison of 5 options) and `stt-quality-apple-speech.md` (audit of the current Apple path). This doc is a wider market scan: what exists beyond Whisper, which providers host Whisper well, which local runtimes win on macOS, and what competing dictation apps have chosen.

> **Development machine constraint.** Untype is developed on an Intel MacBook Pro (i7-9750H, 32 GB RAM, macOS 26.4.1). That rules out WhisperKit (Apple Silicon / ANE only), parakeet-mlx (MLX is Apple Silicon only), and the FluidInference Parakeet CoreML path (CoreML on Intel has no ANE and limited compute targets). The practical local runtime set on this machine is **Apple `SFSpeechRecognizer`**, **whisper.cpp** (CPU via AVX/AVX2 or OpenVINO), **faster-whisper** (Python + CTranslate2 CPU int8), and **Moonshine** (ONNX, works anywhere). See *Local options on Intel Mac* below for the Intel-specific short-list.

## Executive Summary

1. **Whisper is no longer the accuracy leader.** On the Artificial Analysis leaderboard, ElevenLabs Scribe v2 (2.3% WER) and Google Gemini 3 Pro (2.9%) beat every Whisper variant. The best open-weights model is now **Mistral Voxtral Small at 2.9% WER** — better than any Whisper and Apache-licensed.
2. **Whisper's best value play is Groq.** `whisper-large-v3-turbo` on Groq hits 4.8% WER at 242× realtime for ~$0.04/hr — the best cost/latency/accuracy mix for a cloud dictation backend.
3. **NVIDIA Parakeet TDT 0.6B** is the speed-optimized open-weights option (>2000× RTFx on GPU, ~2.2% WER on some benches) with a production-ready MLX port for Apple Silicon (`parakeet-mlx`) and a CoreML conversion. Turbo Whisper (macdaddy.io) already ships it.
4. **Moonshine v2 (Useful Sensors)** is the on-device latency king: 50 ms first-token for Tiny, 27 MB model size, Apache-licensed. Under-rated for live overlay streaming.
5. **On macOS, the runtime choice matters.** whisper.cpp is ~12–18% faster than WhisperKit on wall-clock; WhisperKit is the first-party Swift path with CoreML + ANE; parakeet-mlx is the MLX path; faster-whisper is Python-only. For a Swift app, WhisperKit vs whisper.cpp (via Swift wrapper) are the realistic choices.
6. **The competitive app market is crowded but commoditized.** Superwhisper and its alternatives (Whispering, VoiceInk, Wispr Flow, Willow, Turbo Whisper, Vibe, OpenWhispr) almost all pass audio through whisper.cpp, WhisperKit, or a cloud Whisper API. Differentiation is UI, post-processing, and hotkey UX — not the model.

## The Benchmark Landscape

### Artificial Analysis (multilingual, real-world audio) — April 2026

| Rank | Model | Provider | WER | Notes |
|------|-------|----------|-----|-------|
| 1 | Scribe v2 | ElevenLabs | 2.3% | Proprietary |
| 2 | Gemini 3 Pro (High) | Google | 2.9% | Proprietary |
| 3 | **Voxtral Small** | **Mistral** | **2.9%** | **Open weights** |
| 4 | Gemini 3.1 Pro Preview | Google | 2.9% | Proprietary |
| 5 | Gemini 2.5 Pro | Google | 3.0% | Proprietary |
| 7 | Voxtral Mini Transcribe | Mistral | 3.7% | Open weights |
| 9 | AssemblyAI Universal | AssemblyAI | 4.0% | Proprietary |
| — | Whisper Large v3 (fal.ai) | — | 4.2% | — |
| — | Whisper Large v3 Turbo (Groq) | — | 4.8% | Best Whisper $/latency |
| — | Whisper Large v3 (Together.ai) | — | 7.4% | Provider-tuning matters |

### Voice Writer leaderboard (English dictation) — Oct 2025

- GPT-4o Transcribe: 5.4% (formatted WER) @ $0.36/hr
- Gemini 2.5 Pro: 5.6% @ $0.22/hr
- ElevenLabs: 6.8% @ $0.35/hr
- AssemblyAI: 6.8% @ $0.15/hr
- Whisper Large: 7.2% (local)
- Deepgram: 7.6% @ $0.26/hr
- **Apple Dictation: 16.5%** — confirms the current Untype engine is a floor, not a ceiling.

### Speed (AA benchmark)

- Deepgram Base: 531× realtime
- Groq Whisper Turbo: 242× realtime
- Fal.ai Wizper Large v3: 219× realtime
- Moonshine Tiny v2: 50 ms first-token, 5.8× faster than Whisper Tiny
- Parakeet TDT 1.1B: ~2000× RTFx on GPU

## Open-Weights Models Worth Knowing

| Model | Size | License | WER | Best use |
|-------|------|---------|-----|----------|
| **Voxtral Small** (Mistral) | ~12B | Apache 2.0 | 2.9% | Highest-accuracy open model; cloud GPU |
| **Voxtral Mini Transcribe** | ~3B | Apache 2.0 | 3.7% | Laptop/server on-device |
| **Parakeet TDT 0.6B v2** (NVIDIA) | 0.6B | CC-BY-4.0 | ~2.2% | Real-time, low-latency; ANE/MLX friendly |
| **Canary Qwen 2.5B** (NVIDIA) | 2.5B | CC-BY-4.0 | 5.6% | HF Open ASR Leaderboard #1 for accuracy |
| **Whisper Large v3 / Turbo** (OpenAI) | 1.5B / 809M | MIT | 4.2–4.8% | Still the ecosystem default |
| **Moonshine v2** (Useful Sensors) | 27–150 MB | Apache 2.0 | ≥ Whisper Tiny | Smallest on-device, 50 ms first-token |

## Cloud API Providers for Whisper

| Provider | Model | Price | Latency | Notable |
|----------|-------|-------|---------|---------|
| **Groq** | whisper-large-v3-turbo | $0.04/hr | 242× realtime | Best overall value |
| Groq | whisper-large-v3 | $0.111/hr | ~100× | Accuracy-optimized |
| Fal.ai | whisper-large-v3 | $0.50/1000 min | 219× | Competitive |
| Fireworks | whisper-large-v3 Turbo | — | Fast | OpenAI-compatible API |
| Together.ai | whisper-large-v3 | ~$0.015/min ($0.90/hr) | — | Priced high, worst WER of hosted (7.4%) |
| OpenAI | whisper-1 / gpt-4o-transcribe | $0.006/min audio | — | First-party; `gpt-4o-transcribe` now beats `whisper-1` |
| Naga.ac | whisper-large-v3 (free tier) | Free | Unknown | Community reseller, OpenAI-compatible; reliability unproven |
| Hugging Face Inference | many | Varies | — | Flexible; configure yourself |
| SiliconFlow | multiple | — | Claims 2.3× faster, 32% lower latency | OpenAI-compatible |

Takeaway: **Groq is the clear cloud choice** for a Untype cloud tier — OpenAI-compatible, fast, cheap, and the turbo model's accuracy is acceptable. Naga.ac is interesting as a free tier but not reliable enough for paid use.

## Local / On-Device Runtimes

| Runtime | Language | Acceleration | Pros | Cons |
|---------|----------|--------------|------|------|
| **WhisperKit** (Argmax) | Swift | CoreML + ANE | First-party Swift, ANE-optimized, already in Untype bench | 12–18% slower than whisper.cpp wall-clock; 30–60s first-run CoreML compile; model download UX required |
| **whisper.cpp** | C/C++ | Metal + CoreML | Fastest on Apple Silicon per benchmark; tiny binary; mature | Needs Swift wrapper |
| **faster-whisper** | Python | CTranslate2 | Fast; great for servers | Python runtime unsuitable for a Swift app |
| **parakeet-mlx** | Python | MLX (Metal) | Runs NVIDIA Parakeet on Apple Silicon | Python; no Swift bindings yet |
| **FluidAudio CoreML** | Swift | CoreML | Newer Parakeet CoreML bindings for Swift | Ecosystem young |
| **MLX Whisper** | Python | MLX | Apple's ML framework | Python; weaker streaming than faster-whisper |
| **Moonshine** (ONNX + Core ML) | Swift/Python | Any | Smallest, lowest-latency; Apache 2.0 | Whisper-tiny-equivalent accuracy only |

## Competing Dictation Apps (April 2026)

| App | Model backend | License | Price | Lesson |
|-----|---------------|---------|-------|--------|
| **Whispering** (Epicenter) | whisper.cpp local + Groq/OpenAI/ElevenLabs cloud | AGPLv3 | Free | BYO-key model avoids sub-fees; cross-platform Tauri stack |
| **VoiceInk** | Local ASR + cloud | Open source | $25 one-time | "The magic is in post-processing" — matches our LLM-cleanup pipeline bet |
| **Turbo Whisper** (MacDaddy) | WhisperKit + Parakeet v3 (Metal) | Free | Free | Two-engine UX: accuracy vs speed, user-chosen |
| **Vibe** | whisper.cpp | MIT | Free | Speaker diarization, system-audio capture; feature-rich cross-platform |
| **OpenWhispr** | 5 Whisper sizes local + cloud | Open | Freemium | UI for model-size selection |
| **Wispr Flow** | Cloud | Proprietary | $15/mo | Best polish; users pay for zero-setup |
| **Willow Voice** | Cloud | Proprietary | $15/mo | macOS-focused Wispr clone |
| **SpeechPulse** | Local | Proprietary | $159 bundle | Dragon-style real-time auto-insert |
| **Aqua Voice** | Cloud | Proprietary | $8/mo | Real-time on-screen text |
| **Superwhisper** | Multiple | Proprietary | $8.49–15/mo | The incumbent; built-in model manager + prompt library |

## Measured Results on Untype's Corpus (2026-04-18 / 04-19)

Ran `bench/audio-corpus.json` (7 samples, 149 s total) through multiple providers on the Intel dev MacBook. Full analysis in `research/whisper-bench-2026-04-18.md`; harness at `tools/stt-bench/stt_compare.py`.

| Provider | Mean WER | Mean wall-clock | RTF | Notes |
|----------|---------:|----------------:|----:|-------|
| `groq:whisper-large-v3-turbo` | **6.2 %** | **0.45 s** | 0.02 | Best cloud result today |
| `groq:whisper-large-v3` | 7.7 % | 0.53 s | 0.03 | No reason to pay 3× turbo's cost |
| `moonshine:base` (local, EN-only) | 8.6 % EN-only | 3.2 s | 0.14 | Apache 2.0, 148 MB; RU fails catastrophically |
| `whispercpp:small` (local) | 8.7 % | 23.0 s | 1.08 | Realtime-ish on Intel |
| `whispercpp:large-v3-turbo` (local) | 9.0 % | 50.1 s | 2.35 | Slower than realtime on Intel CPU |
| `whispercpp:base` (local) | 11.3 % | 7.4 s | 0.35 | Acceptable EN; weak RU |
| `moonshine:tiny` (local, EN-only) | 11.8 % EN-only | 2.2 s | 0.10 | 27 MB, fastest on-device option tested |
| `whispercpp:tiny` (local) | 17.0 % | 3.9 s | 0.18 | Accuracy floor |

**Moonshine was tested (2026-04-19).** Installed via `useful-moonshine-onnx` (binary-wheel path: `pip install --only-binary=:all:` to avoid llvmlite's source build on Intel). English-only by design — on the Russian sample both tiny and base emit catastrophic hallucinations (167–238 % WER). On English, **Moonshine base is competitive with whisper.cpp small** (8.6 % vs 8.7 %) at ~7× faster wall-clock on Intel. This makes it a credible candidate for the live streaming slot, not just the final pass.

**Voxtral Small via OpenRouter** was implemented in the harness but could not run: the existing `UNTYPE_OPENROUTER_KEY` has hit its total credit limit. Endpoint verified as `POST /api/v1/chat/completions` with `input_audio` content parts; OpenAI-compatible shape.

Caveats: two of seven references (`carmack_unscripted_en`, `joker_kotlin_ru`) are auto-captions per the corpus metadata — they inflate every provider's mean WER by ~2–3 pp.

**Key Intel finding (dev-only):** on this Intel CPU, whisper.cpp `large-v3-turbo` runs at 2.35× realtime and WhisperKit can't run at all. That affects *how we develop and dogfood* — it does **not** describe the product. Apple-Silicon users (the product's actual audience) have entirely different options available.

## Hosting Options for the Models Worth Considering

| Model | Open weights? | Self-host | Cloud host(s) | Cost per hour of audio |
|-------|:-------------:|-----------|---------------|------------------------|
| **Whisper large-v3-turbo** | MIT | whisper.cpp, WhisperKit | Groq, Fireworks, Fal.ai, OpenAI (`whisper-1`), Naga.ac free tier | Groq $0.04 · OpenAI $0.36 |
| **Whisper large-v3** | MIT | whisper.cpp, WhisperKit | Groq, Fireworks, Fal.ai, Together.ai | Groq $0.11 · Together $0.90 |
| **Mistral Voxtral Small (24B)** | Apache 2.0 | SageMaker BYOC, vLLM, Hugging Face | Mistral AI direct (transcribe variant $0.003/min), OpenRouter (chat-completions + input_audio), Hugging Face Inference | Mistral $0.18 · OR ~$0.36 |
| **Mistral Voxtral Mini Transcribe** | Apache 2.0 | Self-host (smaller) | Mistral AI (transcribe-optimized routing) | Mistral $0.18 |
| **NVIDIA Parakeet TDT 0.6B v2** | CC-BY-4.0 | MLX (Apple Silicon), CoreML, NeMo | NVIDIA NIM (free tier at build.nvidia.com), Replicate (~$0.007/run), Together.ai (v3) | Replicate ~$0.01/min · NIM free |
| **NVIDIA Canary Qwen 2.5B** | CC-BY-4.0 | NeMo | NVIDIA NIM, HF Inference | NIM free tier |
| **ElevenLabs Scribe v2** | Proprietary | Not available | ElevenLabs API ($0.22/hr base, +$0.07 for entity detection, +$0.05 for keyterm prompting); Scribe v2 Realtime variant at 150 ms latency | $0.22/hr |
| **Moonshine v2** (tiny/base/medium) | Apache 2.0 | ONNX, PyTorch, HF Transformers | Hugging Face Inference, self-hosted only in practice | Free (on-device) |
| **GPT-4o Transcribe / GPT-4o Mini Transcribe** | Proprietary | Not available | OpenAI direct, OpenRouter | OpenAI ~$0.36/hr (4o), ~$0.18/hr (4o-mini) |
| **Gemini 2.5 / 3 family** | Proprietary | Not available | Google AI / Vertex, OpenRouter | ~$0.14–0.22/hr |
| **Apple SpeechAnalyzer (macOS 26)** | First-party OS | N/A (built-in) | — | Free |

Takeaways for Untype:
- **Most of these are BYOK-compatible over one of two endpoint shapes**: OpenAI-style `/v1/audio/transcriptions` (Groq, Fireworks, OpenAI direct) or chat-completions-with-audio (OpenRouter, Gemini). A single gateway component + a provider dropdown covers most of the market.
- **NVIDIA NIM has a free tier for Parakeet** — good for an opt-in "try this model" path that doesn't require the user to put in a credit card.
- **ElevenLabs Scribe v2** is the accuracy leader but is *not* OpenAI-compatible — needs its own endpoint integration. Worth a dedicated path if accuracy benchmarks on Untype's own corpus justify it.

## Dev Machine vs Product: Two Different Constraint Sets

Untype is developed on an Intel MBP (i7-9750H, 32 GB, macOS 26.4.1). The product's users are predominantly Apple Silicon (M-series). These are two different constraint sets and should not be conflated:

| Constraint | Applies to |
|------------|-----------|
| WhisperKit is Apple-Silicon-only | Product users: fine. Dev machine: blocked — gets tested in CI or on a borrowed M-series. |
| parakeet-mlx is Apple-Silicon-only | Product users: fine. Dev: bench via Replicate / NIM API instead of local. |
| whisper.cpp `large-v3-turbo` is 2.35× RT on this Intel CPU | Dev-machine only — 30× realtime on M2, per published benchmarks. |
| Moonshine ONNX | Works everywhere; fastest on Apple Silicon via CoreMLExecutionProvider. |

Dev decisions (e.g. "what runs locally during `swift test`?") should optimise for the dev machine. Product decisions (e.g. "which engines ship in the build?") must not treat the dev machine as representative.

## Product Principle: Model Flexibility as a Differentiator

Most competitors (see `user-pain-points-and-desires-2026.md`) pick a single backend and hide it. Untype should instead make the engine choice first-class:

- **Local engine menu**, auto-gated by hardware capability and with an explicit "this model needs Apple Silicon / an internet connection" callout:
  - Apple `SFSpeechRecognizer` / `SpeechAnalyzer` (first-party, no download)
  - whisper.cpp models (tiny / base / small / medium / large-v3 / large-v3-turbo) — cross-silicon
  - WhisperKit models (Apple Silicon fast path)
  - Parakeet via MLX or CoreML (Apple Silicon only)
  - Moonshine tiny / base / medium (27 MB–150 MB, fast, EN-only today)
- **Cloud engine menu** with BYOK, grouped by endpoint shape so the plumbing is shared:
  - *OpenAI-compatible `/v1/audio/transcriptions`:* Groq, Fireworks, Fal.ai, OpenAI, Naga.ac (free tier for experimentation)
  - *OpenAI-compatible chat completions with `input_audio`:* OpenRouter (Voxtral, GPT-Audio, Gemini 2.5), Gemini direct
  - *Proprietary-shape endpoints:* ElevenLabs Scribe v2 (worth the custom integration cost for the 2.3 % WER)
  - *NVIDIA NIM* (free tier for Parakeet experimentation)

Treat this as analogous to Claude Code's provider configurability: pick the engine that matches your privacy / latency / cost preference, plug in a key. Untype's internal `CloudProvider` pattern (see `Sources/UntypeCore/Processing/CloudProvider.swift`) already does this for LLM cleanup — the STT layer can follow the same shape.

This framing also protects against model churn: when the next better model ships, adding it is a new row in a menu, not a rewrite.

## Candidates for a First Cut (non-final)

These are *defaults* the build would ship with, chosen to be good out-of-the-box while the menu gives power users full control. Every entry here should be revisited after a fresh bench round with verified corpus references and cloud providers we don't currently have keys for.

**Live streaming partial (overlay):**
- Apple `SFSpeechRecognizer` (current): zero-install, works on Intel + Apple Silicon. Baseline until macOS 26's `SpeechAnalyzer` is evaluated.
- **Moonshine tiny or base (candidate):** measured 8.6 % WER (EN, Moonshine base) at ~3.2 s for a ~15 s clip on Intel — suggests ≤100 ms first-token latency on Apple Silicon. 27 MB / 148 MB on-disk. Worth a side-by-side against `SFSpeechRecognizer` before committing.

**Final pass (after recording stops):**
- **Default cloud:** Groq `whisper-large-v3-turbo`. Measured 6.2 % WER, 0.45 s wall-clock, $0.04/hr. The "it just works out of the box" default — user can opt out.
- **Alternative cloud picks (menu):** OpenAI `gpt-4o-transcribe`, ElevenLabs Scribe v2 (if accuracy bench justifies the custom endpoint), Voxtral Small via OpenRouter / Mistral.
- **Default local (Apple Silicon):** WhisperKit `large-v3-turbo` or `large-v3` — measured by Turbo Whisper and the published WhisperKit paper to run faster than realtime on M-series.
- **Default local (Intel):** whisper.cpp `small` — the only cross-silicon option that's realtime on Intel at usable accuracy.
- **Fully offline opt-in:** any local model above with "don't call cloud" toggled.

These are good defaults — not locked-in choices. The build's value is the *menu plus the defaults*, not either alone.

## Open Follow-ups

- Spot-check WER numbers against the Artificial Analysis live dashboard before citing in a design doc — it updates monthly.
- Hand-verify `carmack_unscripted_en` and `joker_kotlin_ru` corpus references before the next bench round.
- Obtain keys + rebench: ElevenLabs Scribe v2, OpenAI `gpt-4o-transcribe`, Mistral (or refresh OpenRouter credit for Voxtral), Deepgram Nova, NVIDIA NIM (free tier for Parakeet).
- Bench WhisperKit + parakeet-mlx on an Apple Silicon loaner to fill the on-device Apple Silicon column.
- Prototype the provider-menu UX in Settings. First-run flow probably defaults to "Use Groq cloud + Apple streaming" with a "Customise" option that reveals the full menu.
- Evaluate `SpeechAnalyzer` / `DictationTranscriber` (macOS 26) — if Apple's new APIs beat `SFSpeechRecognizer`, the streaming-partial default shifts.

## Sources

- [Artificial Analysis — Speech-to-Text Leaderboard](https://artificialanalysis.ai/speech-to-text)
- [Voice Writer Speech Recognition Leaderboard](https://voicewriter.io/speech-recognition-leaderboard)
- [SiliconFlow — Best API Providers of Open-Source Audio Models](https://www.siliconflow.com/articles/en/The-best-API-providers-of-Open-Source-Audio-Model)
- [Whispering (Epicenter) README](https://github.com/EpicenterHQ/epicenter/blob/main/apps/whispering/README.md)
- [AssemblyAI — Top Free STT APIs and Open-Source Engines](https://www.assemblyai.com/blog/the-top-free-speech-to-text-apis-and-open-source-engines)
- [Sally.io — Best Whisper Alternatives](https://www.sally.io/blog/the-best-whisper-alternatives)
- [OpenWhispr](https://openwhispr.com/)
- [MacDaddy — Turbo Whisper](https://macdaddy.io/turbo-whisper/)
- [Vibe (thewh1teagle/vibe)](https://github.com/thewh1teagle/vibe)
- [Superwhisper Alternatives for 2025 (Medium)](https://beingpax.medium.com/superwhisper-alternatives-you-should-be-using-in-2025-67342aa61588)
- [Together.ai — Whisper Large v3](https://www.together.ai/models/openai-whisper-large-v3)
- [Naga.ac — Whisper Large v3 (free)](https://naga.ac/models/whisper-large-v3:free)
- [parakeet-mlx (senstella)](https://github.com/senstella/parakeet-mlx)
- [Northflank — Best open-source STT in 2026](https://northflank.com/blog/best-open-source-speech-to-text-stt-model-in-2026-benchmarks)
- [NVIDIA Parakeet TDT 0.6B v2 on Hugging Face](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2)
- [FluidInference Parakeet CoreML](https://huggingface.co/FluidInference/parakeet-tdt-0.6b-v2-coreml)
- [Moonshine (moonshine-ai/moonshine)](https://github.com/moonshine-ai/moonshine)
- [WhisperKit paper (arXiv 2507.10860)](https://arxiv.org/html/2507.10860v1)
- [WhisperKit vs whisper.cpp vs faster-whisper (Modal blog)](https://modal.com/blog/choosing-whisper-variants)
- [mac-whisper-speedtest (anvanvan)](https://github.com/anvanvan/mac-whisper-speedtest)
