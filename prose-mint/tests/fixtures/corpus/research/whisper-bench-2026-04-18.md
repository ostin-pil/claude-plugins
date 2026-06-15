# STT Benchmark Analysis — 2026-04-18 / -04-19 / -04-20

**Corpus**: `bench/audio-corpus.json`, 7 samples, 149 s total audio (6 EN, 1 RU). Hand-verified 2026-04-20 — prior two un-verified references (carmack, joker) extended to include the trailing phrase each auto-caption had dropped.
**Dev hardware**: MacBook Pro (Intel i7-9750H @ 2.6 GHz, 32 GB, macOS 26.4.1).
**Providers benched**: 3 local whisper.cpp sizes (base, small, large-v3-turbo), Moonshine base, Groq whisper-large-v3-turbo, OpenRouter-routed Gemini 2.5 Pro (2 rounds each). Plus the 2026-04-18 pre-hand-verify pass for whisper.cpp tiny, Moonshine tiny, and groq whisper-large-v3 baseline.
**Not yet benched (need keys or Apple Silicon)**: WhisperKit, parakeet-mlx / Parakeet CoreML / Parakeet NIM, ElevenLabs Scribe v2, Deepgram Nova, Mistral Voxtral **via the correct endpoint** (see "Voxtral routing failure" below).
**Confirmed unavailable / deferred**:
- `anthropic/claude-opus-4` via OpenRouter — HTTP 404 `"No endpoints found that support input audio"` across all samples. OpenRouter does not expose an audio-input surface for Claude today; direct Anthropic API also has no public documentation for audio input on the Opus 4 family. Even if it lands, Opus 4's chat pricing (~$15/$75 per 1M in/out tokens) is untenable as a default transcription engine for a voice-to-text app — would only fit behind a dedicated premium tier where the user brings their own key.
- OpenAI `gpt-4o-audio-preview` deliberately dropped (~$14/$55 per 1M in/out tokens — same "premium-plan-only" argument as Opus).

> **Rerun 2026-04-20.** Tables below regenerated from `benchmarks/2026-04-20_openrouter-rerun/` after the corpus hand-verification. Numbers supersede the prior 2026-04-18 tables. Effect of hand-verify: every provider's mean WER dropped ~1.5–2 pp, consistent with the prior caveat; rankings did not flip.
>
> **Follow-up 2026-04-20.** Added Gemini 2.5 Pro row from `benchmarks/2026-04-20_gemini-claude-opus-audio/`. Voxtral Small re-investigated after the initial "content-hallucination" finding looked off — root cause turned out to be an API-routing mismatch, not a Voxtral model defect. See Voxtral section.

> This document captures a point-in-time measurement, not a final provider decision. Untype's design stance is that users should be able to pick the engine that fits their hardware and privacy preference — see "Product Principle: Model Flexibility as a Differentiator" in `whisper-landscape-2026.md`. The numbers below inform good *defaults* for the engine menu, not the menu itself.

## Headline Results (2026-04-20 rerun)

- **Best cloud on our corpus:** Groq `whisper-large-v3-turbo` — **4.3 % mean WER**, 0.46 s wall-clock, ~$0.04/hr. Pulled further ahead after hand-verify (was 6.2 %). Median WER is 0 %, so the mean is driven by two hard samples (carmack unscripted, joker RU). Still the strongest default for the "cloud" tier, pending Scribe v2.
- **Gemini 2.5 Pro (OpenRouter-routed)** — **6.8 % mean / 6.7 % median** WER, 4.19 s wall-clock. Clean run, no outliers. Strongest on the Russian sample of anything benched so far (4.6 % WER vs. Groq's 12.6 %), which matters for a multilingual product. ~10× slower than Groq on wall-clock, so not a streaming-tier candidate; positions as "frontier-LLM cloud option with best-in-corpus RU accuracy".
- **Best local on our corpus:** whisper.cpp `small` — 8.1 % WER, 23.9 s wall-clock on Intel. Moonshine `base` is 36.4 % mean / 10.4 % median — the mean is pushed up by a 213.8 % score on the Russian sample (hallucination; model is English-only by design). English-only mean is closer to ~7 %, putting it ahead of whisper.cpp small on pure accuracy at ~7× lower latency.
- **whisper.cpp `large-v3-turbo` on Intel CPU is not viable as a product engine** for Intel users (49 s for a 30 s clip = 2.3× realtime, unchanged). On Apple Silicon it runs above realtime per published benchmarks — the engine isn't disqualified, only its Intel deployment story is.

## Ranked Summary (2026-04-20 rerun)

| Provider | Mean WER | Median WER | Mean wall-clock | RTF* | Notes |
|----------|---------:|-----------:|----------------:|-----:|-------|
| `groq:whisper-large-v3-turbo` | **4.3 %** | **0.0 %** | **0.46 s** | 0.022 | Cloud; no open-weights access |
| `openrouter:google/gemini-2.5-pro` | 6.8 % | 6.7 % | 4.19 s | 0.20 | Cloud via OpenRouter; best RU WER in the bench (4.6 %) |
| `whispercpp:small` | 8.1 % | 6.7 % | 23.93 s | 1.12 | Local; realtime-ish on Intel |
| `whispercpp:large-v3-turbo` | 8.7 % | 10.9 % | 49.17 s | 2.31 | Local; **slower than realtime on Intel**; fine on Apple Silicon |
| `whispercpp:base` | 9.6 % | 6.7 % | 9.28 s | 0.44 | Local; acceptable EN; weak RU (34.5 %) |
| `moonshine:base` | 36.4 % (mean) / ~7 % EN-only | 10.4 % | 3.25 s | 0.15 | Local; Apache 2.0; EN-only (RU = 213.8 % WER) |
| `openrouter:mistralai/voxtral-small-24b-2507` | — | — | — | — | **Wrong API surface — see Voxtral section. Numbers from this lane do not measure Voxtral's transcription quality.** |
| `openrouter:anthropic/claude-opus-4` | — | — | — | — | No audio-input endpoint exposed via OpenRouter (HTTP 404); also price-parked |

\* RTF = wall-clock ÷ audio duration. >1 means slower than realtime.

For reference, the 2026-04-18 pre-hand-verify run also covered `whispercpp:tiny` (17.0 % WER, 0.18 RTF), `moonshine:tiny` (11.8 % EN-only), and the slower `groq:whisper-large-v3` baseline (7.7 %) — not repeated in this rerun. Those numbers still hold directionally but inherit the old corpus's ~1.5–2 pp inflation.

## Voxtral routing failure — why the OpenRouter numbers don't count

Initial bench showed Voxtral Small producing a 97 % WER on `wwdc_swiftui_perf_en`: two rounds at temperature=0 returned two *different* plausible-sounding SwiftUI-performance prose outputs, neither matching the audio. Follow-up with a firmer "verbatim only, do not invent content" prompt flipped the fabrication into an honest `[inaudible]` and cleaned up `wwdc_swiftui_intro_en` from 8.4 % → 0 %, but the perf sample remained 100 % WER. Taken on its own that looked like a model flaw.

It isn't a model flaw — it's an API-surface mismatch.

- Voxtral has two built-in modes: `<repeat>` (verbatim transcription) and `<next>` (audio understanding / continuation), controlled by **special tokens, not by the user's text prompt** (Voxtral paper, [arXiv 2507.13264](https://arxiv.org/html/2507.13264v1)). The HuggingFace model card also notes **"System prompts are not yet supported"** ([HF card](https://huggingface.co/mistralai/Voxtral-Small-24B-2507)).
- OpenRouter exposes audio *only* through `/api/v1/chat/completions` with `input_audio` content parts — it has **no passthrough** to Mistral's dedicated `audio/transcriptions` endpoint ([OpenRouter Audio docs](https://openrouter.ai/docs/guides/overview/multimodal/audio)). That surface never activates the `<repeat>` token, so Voxtral is free to run in understanding mode and generate topic-adjacent prose on top of the audio.
- Mistral's own docs explicitly recommend the `audio/transcriptions` endpoint for transcription, and warn that chat-completions "may provide different results" ([Mistral API](https://docs.mistral.ai/api/endpoint/audio/transcriptions)). The newer dedicated model for this slot is `voxtral-mini-transcribe-realtime-2602` (Feb 2026 release) ([Voxtral Transcribe 2 announcement](https://mistral.ai/news/voxtral-transcribe-2)).

**Conclusion**: the OpenRouter-routed Voxtral bench does not measure what we thought it measured. The model's actual transcription quality is uncharacterised in our data until we run it through Mistral's direct API. A firmer system prompt is a band-aid, not a fix, and cannot work reliably because the transcribe/understand mode is token-gated rather than prompt-gated.

**Action**: drop the OpenRouter-routed Voxtral lane from future runs. Add a direct Mistral lane (new B-track item: Mistral API key + `mistral:<model>` provider in the harness calling `/v1/audio/transcriptions` with `voxtral-mini-transcribe-realtime-2602`). Raw data from the invalidated lane kept under `benchmarks/2026-04-20_*/` for reference but excluded from the ranked summary.

## Per-sample Observations

- **Clean synthetic (`clean_en`, `technical_en`)**: every valid provider scores 0 %. Not a discriminator.
- **False-start (`false_start_en`)**: only whisper.cpp `large-v3-turbo` and Groq turbo got 0 %. Smaller/older models stumble on "uh". This is the "raw text good enough for LLM cleanup" bar.
- **WWDC SwiftUI (intro/perf)**: mid-tier models handle intro well (0 %), but `wwdc_swiftui_perf_en` still has a ~9 % floor across most providers (14.9 % for the whisper.cpp family). Some of that floor survives the hand-verify, suggesting punctuation/capitalisation normalisation noise in the reference rather than model error.
- **`carmack_unscripted_en`**: previously 19–28 % across every provider (with un-verified reference); post hand-verify it's 8.7 % Groq, 10.9 % whisper.cpp, 12 % Moonshine. The ~2 pp compression vs. prior matches the inflation caveat.
- **`joker_kotlin_ru`**: Gemini 2.5 Pro **4.6 % (best)**, Groq turbo 12.6 %, whisper.cpp `large-v3-turbo` 21.8 %, whisper.cpp `small` 24.1 %, whisper.cpp `base` 34.5 % — multilingual-capable tiers ranked top-to-bottom by model strength. Moonshine catastrophic (213.8 %, EN-only by design). Gemini's RU lead matters: Groq stumbled on this sample even though it's "cloud-tier" too.

## The Intel Dev-Machine Reality (NOT the product reality)

This is a *dev-testing* constraint, not a product design constraint. Keep them separate.

| Runtime | RTF on Intel | Apple Silicon expectation (literature) |
|---------|-------------:|---------------------------------------|
| Groq cloud (any model) | 0.02 | 0.02 (network-bound, hardware-independent) |
| Moonshine tiny | 0.10 | <0.05 (CoreML ExecutionProvider available) |
| whisper.cpp tiny | 0.18 | 0.04 |
| whisper.cpp base | 0.35 | 0.08 |
| whisper.cpp small | 1.08 | 0.25 |
| whisper.cpp large-v3-turbo | 2.35 | ~0.4 |
| WhisperKit large-v3-turbo | not runnable | ~0.3 (ANE) |
| parakeet-mlx 0.6B | not runnable | ~0.0005 (per NVIDIA's >2000x RTFx claim, which is GPU-measured but Apple Silicon MLX still beats realtime by ~10x) |

Product conclusions:
- For Apple Silicon users, *every* on-device option is realtime or better. Local-only UX is entirely feasible.
- For Intel users (rare in the target segment but not zero), only Moonshine + whisper.cpp base/small are realtime on-device; anything beefier needs cloud.
- Cloud is valuable for both groups — for Apple Silicon it buys accuracy (Scribe v2 at 2.3 %, Groq turbo at 4.3 %) that local can't match today without a large download, and for Intel it bypasses the CPU bottleneck entirely.

## Cost Back-of-Napkin

| Provider | Price | 60 min/day heavy user | 15 min/day typical |
|----------|-------|----------------------:|-------------------:|
| Groq `whisper-large-v3-turbo` | $0.04/hr | $1.20/mo | $0.30/mo |
| OpenAI `gpt-4o-mini-transcribe` | ~$0.18/hr | $5.40/mo | $1.35/mo |
| ElevenLabs Scribe v2 | $0.22/hr | $6.60/mo | $1.65/mo |
| Mistral `voxtral-mini-transcribe` (direct) | ~$0.18/hr | $5.40/mo | $1.35/mo |
| OpenAI `gpt-4o-transcribe` / Gemini 2.5 Pro | ~$0.36/hr | $10.80/mo | $2.70/mo |
| Claude Opus 4 chat (if audio ever lands) | ~$15/$75 per 1M tokens → ≫$30/mo for heavy | **premium-tier BYOK only** | same |
| Local (Apple Silicon + WhisperKit / Moonshine) | $0 | — | — |

Even a free cloud tier subsidised at 30 min/day would cost Untype ~$0.60/user/month on Groq. Scribe v2 would be ~$3.30/user/month — still cheap, but the price difference is real if free-tier scale matters. Opus 4 is an order of magnitude beyond that and doesn't fit any default path.

## What This Means for the Engine Menu Defaults

*These are defaults, not lock-ins. Every row here is revisitable.*

1. **Live streaming partial (overlay):** Apple `SFSpeechRecognizer` today. Evaluate Moonshine base as an alternative once we have measured latency on Apple Silicon — Moonshine's 50 ms first-token claim is compelling if it holds on our corpus.
2. **Final pass — cloud default:** Groq `whisper-large-v3-turbo`. Measured best on our corpus, cheapest, fast. Re-evaluate after benching Scribe v2 and Voxtral-via-Mistral-direct.
3. **Final pass — Apple Silicon local default:** WhisperKit `large-v3-turbo`. Cannot validate on this dev machine — goes in behind feature-detect, tested in CI or on loaner hardware.
4. **Final pass — Intel local default:** whisper.cpp `small` or Moonshine `base`. Moonshine wins on latency and size; whisper.cpp wins on multilingual support. If user is English-only, Moonshine. Otherwise whisper.cpp `small`.
5. **Fully offline opt-in:** any local model above with "don't call cloud" toggled. Zero cloud calls, even for LLM cleanup (would need a local LLM).
6. **Cloud menu (BYOK):** Groq, OpenAI (direct), ElevenLabs, Mistral (direct), OpenRouter (non-Voxtral), plus a "premium BYOK" slot for Opus/GPT-Audio-class where the user accepts the price.

## Next Bench Rounds (priority order)

1. **Bench Voxtral via Mistral's direct `/v1/audio/transcriptions` endpoint**, not via OpenRouter's chat-completions. Needs a Mistral API key + a new `mistral:<model>` provider in the harness targeting `voxtral-mini-transcribe-realtime-2602`. Until this lands, Voxtral is untested on our corpus.
2. **Get more cloud keys and rebench.**
   - ElevenLabs — Scribe v2 ($0.22/hr base); unique endpoint shape; 2.3 % published WER. Harness path already landed in `be21efe`; awaiting key top-up.
   - NVIDIA NIM free tier — Parakeet TDT 0.6B v2 (unique accuracy/speed combo). **Blocked** on phone verification.
   - Deepgram Nova — the main non-Whisper proprietary option not yet covered.
   - OpenAI `gpt-4o-transcribe` / `gpt-4o-mini-transcribe` — deferred in favour of OpenRouter coverage (single key, same models reachable).
3. **Bench WhisperKit and parakeet-mlx on Apple Silicon.** Needs loaner M-series hardware or a CI runner. Fills the biggest gap in the data.
4. **Latency measurement for the streaming slot.** Time-to-first-token on Apple Silicon for Moonshine vs Apple `SFSpeechRecognizer` — this is a different measurement than end-to-end latency and matters more for live overlay UX.
5. **Extend the corpus.** 2–3 more real-speech samples (meeting audio, accented EN, mobile-mic RU) would make the provider means more stable against single-sample outliers.

## Files

- Raw results — 2026-04-20 hand-verified rerun: `benchmarks/2026-04-20_openrouter-rerun/`
- Raw results — 2026-04-20 Gemini + Claude Opus Audio follow-up: `benchmarks/2026-04-20_gemini-claude-opus-audio/`
- Raw results — 2026-04-20 Voxtral prompt-retry + reproducibility (invalidated — wrong API surface): `benchmarks/2026-04-20_voxtral-*/`
- Raw results — 2026-04-18 whisper.cpp + Groq run (pre-hand-verify): `benchmarks/whisper-landscape-20260418_230151/`
- Raw results — 2026-04-19 Moonshine run: `benchmarks/moonshine-20260419_*/`
- Harness: `tools/stt-bench/stt_compare.py` (providers: `whispercpp:<model>`, `moonshine:<size>`, `groq:<model>`, `openai:<model>`, `openrouter:<model>`, `elevenlabs:<model_id>`)
