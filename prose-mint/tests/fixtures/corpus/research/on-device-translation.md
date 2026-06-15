# On-Device Translation Research

**Date**: 2026-04-10
**Target**: Untype Tier 2 feature -- optional translation after voice cleanup
**Use case**: Speak in language A, insert cleaned text in language B
**Priority pairs**: EN<->RU, EN<->ZH
**Constraints**: macOS 14+, Apple Silicon, native Swift, minimal RAM overhead

---

## Option Comparison Table

| Option | On-Device | Quality (EN-RU/ZH) | RAM Cost | Latency (est.) | macOS Req | Integration Effort | Cost |
|---|---|---|---|---|---|---|---|
| Apple Translation | Yes | Good (Apple NMT) | ~0 (system) | ~200ms | macOS 15+ (programmatic: macOS 26+) | Low (SwiftUI only) | Free |
| NLLB-200 600M | Yes | Good (high-resource) | ~1.2 GB (FP16) / ~600 MB (INT8) | ~300-500ms | macOS 14+ | High (MLX/CTranslate2) | Free |
| NLLB-200 1.3B | Yes | Better | ~2.6 GB (FP16) / ~1.3 GB (INT8) | ~500-800ms | macOS 14+ | High | Free |
| NLLB-200 3.3B | Yes | Best (NLLB family) | ~6.6 GB (FP16) / ~3.3 GB (INT8) | ~1-2s | macOS 14+ | High | Free |
| Madlad-400 3B | Yes | Good (breadth > depth) | ~6 GB (FP16) / ~1 GB (Q2) | ~500ms-1s | macOS 14+ | Medium (GGUF available) | Free |
| MarianMT (per-pair) | Yes | Good (pair-specific) | ~300 MB per pair | ~100-200ms | macOS 14+ | Medium | Free |
| LLM one-pass (cloud) | No* | Excellent (GPT-4, Claude) | 0 (cloud) | +100-300ms over cleanup | macOS 14+ | Very Low | API cost |
| LLM one-pass (local) | Yes | Good-Very Good | 0 (shared w/ cleanup model) | +200-500ms | macOS 14+ | Very Low | Free |
| DeepL API | No | Excellent (EN-RU), Very Good (EN-ZH) | 0 | ~200-400ms | macOS 14+ | Low | $25/M chars |
| Google Cloud Translation | No | Very Good | 0 | ~200-400ms | macOS 14+ | Low | $20/M chars |
| Microsoft Translator | No | Very Good | 0 | ~200-400ms | macOS 14+ | Low | $10/M chars |

*LLM one-pass: local if using Qwen3 1.7B already loaded for cleanup; cloud if using GPT-4o/Claude.

---

## Detailed Analysis

### 1. Apple Translation Framework (macOS 15+)

**API Surface:**
- `TranslationSession` class -- translates text between language pairs
- Obtained via SwiftUI `.translationTask(source:target:action:)` modifier
- Methods: `translate(_:)` for single string, `translations(from:)` for batch
- On-device ML models, shared system-wide (user downloads language packs)
- **Cannot be directly instantiated** without SwiftUI on macOS 15 (Sequoia)

**macOS 26 (Tahoe) Update:**
- `TranslationSession.init(installedSource:target:)` enables direct instantiation without SwiftUI
- This removes the need for the NSHostingView workaround
- Expected release: Fall 2026

**Supported Languages (confirmed):**
Arabic, Chinese (Mandarin - Mainland), Chinese (Mandarin - Taiwan), Dutch, English (US/UK), French, German, Hindi, Indonesian, Italian, Japanese, Korean, Polish, Portuguese (Brazil), Russian, Spanish, Thai, Turkish, Ukrainian, Vietnamese. More coming in 2026.

**EN<->RU, EN<->ZH: Both supported.**

**Quality:** Apple's NMT models are competitive with Google Translate for common pairs. Not as good as DeepL for nuanced European language translation, but solid for the target pairs.

**Integration with Untype (AppKit):**
- macOS 15: Requires embedding a hidden SwiftUI view via `NSHostingView` to obtain `TranslationSession`. Workable but awkward -- the session is tied to the view lifecycle.
- macOS 26: Direct init, clean integration. But raises minimum deployment target.

**Verdict:** Best option if we can accept macOS 15+ minimum. Free, zero RAM overhead, system-maintained models. The SwiftUI workaround is ugly but functional. Becomes clean on macOS 26.

---

### 2. NLLB-200 (Meta)

**Model Variants:**
| Variant | Parameters | Disk (FP16) | Disk (INT8/Q4) | Languages |
|---|---|---|---|---|
| Distilled-600M | 600M | ~1.2 GB | ~600 MB | 200 |
| Distilled-1.3B | 1.3B | ~2.6 GB | ~1.3 GB | 200 |
| Dense-3.3B | 3.3B | ~6.6 GB | ~3.3 GB | 200 |

**Quality:**
- 44% average improvement over prior MT research (Meta's claim)
- Strong on high-resource pairs (EN-RU, EN-ZH are high-resource)
- 1.3B is the sweet spot: significantly fewer mistranslation errors than 600M, close to 3.3B quality for high-resource pairs
- For EN-RU and EN-ZH specifically, quality is competitive with Google Translate NMT but below DeepL and modern LLMs

**Running on macOS / Apple Silicon:**
- **MLX Transformers**: Supports NLLB. `mlx-transformers` library can load and run `facebook/nllb-200-distilled-600M` directly. Python-based.
- **CTranslate2**: Efficient C++ inference engine with NLLB support. INT8 quantization available. Can be called from Swift via C bridge or subprocess. Pre-converted models on HuggingFace (`OpenNMT/nllb-200-3.3B-ct2-int8`).
- **CoreML**: No official conversion. Would need custom conversion pipeline (PyTorch -> ONNX -> CoreML or direct coremltools). Encoder-decoder architecture adds complexity.
- **No native Swift library** -- would need Python subprocess, C++ bridge, or CoreML conversion.

**RAM Budget Concern:**
If already running Qwen3 1.7B for cleanup (~2-3 GB), adding NLLB 1.3B adds another 1.3-2.6 GB. On 8 GB machines this is tight. On 16 GB+ it's fine.

**Verdict:** High quality for the target pairs, but integration into a native Swift app is complex. No clean Swift-native path. Best suited if we want a dedicated on-device translation model and are willing to invest in the integration layer.

---

### 3. Madlad-400 (Google)

**Model Variants:**
| Variant | Parameters | Architecture | Languages |
|---|---|---|---|
| 3B-MT | 3B | T5 | 450+ |
| 7.5B-MT | 7.5B | T5 | 450+ |
| 10B-MT | 10B | T5 | 450+ |

**Quality:**
- Competitive with larger models for high-resource pairs
- Breadth (450+ languages) is the main value proposition, not best-in-class quality per pair
- For EN-RU and EN-ZH: acceptable but generally below NLLB-1.3B and significantly below cloud APIs

**GGUF/MLX:**
- GGUF versions available on HuggingFace (T5 architecture support in llama.cpp)
- Q2 quantization brings 3B model under 1 GB -- aggressive but quality degrades
- MLX: limited community support, no official MLX conversion
- A Gradio WebUI exists (`mamei16/MADLAD-400-WebUI`) for local use

**Verdict:** Not recommended over NLLB for our specific pairs. The 450+ language breadth is irrelevant when we only need EN/RU/ZH. Larger models needed for comparable quality.

---

### 4. MarianMT (Helsinki-NLP)

**Overview:**
- Per-language-pair models (~298 MB each)
- 1000+ models available on HuggingFace
- Format: `Helsinki-NLP/opus-mt-{src}-{tgt}` (e.g., `opus-mt-en-ru`, `opus-mt-en-zh`)

**Quality:**
- Good for specific pairs they were trained on
- EN-RU: solid, well-established pair
- EN-ZH: available but quality can be inconsistent
- Below NLLB-1.3B on most benchmarks for the target pairs

**On-Device Deployment:**
- Small models (~300 MB per pair) -- very RAM-friendly
- CTranslate2 supports MarianMT
- OPUS-MT-app exists for local translation (Bergamot engine)
- CoreML conversion: theoretically possible but no established pipeline
- Same integration challenges as NLLB (no native Swift path)

**Verdict:** Lightweight option if RAM is critical. But managing separate models per pair adds complexity, and quality trails NLLB. Not recommended unless RAM is extremely constrained.

---

### 5. LLM-Based Translation (One-Pass Cleanup + Translate)

This is the most interesting option for Untype because **the LLM is already in the pipeline**.

#### Cloud LLM (GPT-4o / Claude / Qwen-MT)

**One-pass "cleanup AND translate" prompt:**
```
Clean up this voice transcription and translate it to {target_language}.
Fix filler words, grammar, and disfluencies. Output only the translated text.

Transcription: {raw_text}
```

**Quality Assessment:**
- **GPT-4o / GPT-4.1**: Excellent translation quality. WMT24/25 top tier. Handles cleanup + translation in one pass naturally.
- **Claude 4 / 3.5 Sonnet**: Won 9/11 language pairs in WMT24 human evaluation. Excellent for EN-RU.
- **Qwen-MT (cloud API)**: Alibaba's dedicated translation model built on Qwen3. Beats GPT-4.1-mini on multi-domain benchmarks. Best for EN<->ZH.
- **Qwen3 32B**: Strongest on Asian languages (ZH, JA, KO). Outperforms DeepSeek-V3 on multilingual benchmarks.

**Token Cost (one-pass vs two-step):**
- One-pass cleanup+translate: ~same input tokens, ~same output tokens as cleanup alone (output is in target language instead of source)
- Two-step (cleanup then translate): 2x API calls, ~2x cost, ~2x latency
- **One-pass is strictly better** for cost and latency

**Verdict:** If using a cloud LLM for cleanup already, adding translation is essentially free (just modify the prompt). Quality is excellent.

#### Local LLM (Qwen3 1.7B already loaded)

**One-pass with local model:**
- Qwen3 1.7B can handle cleanup + translation in one pass
- EN->ZH quality: reasonable (Qwen family is strong on Chinese)
- EN->RU quality: acceptable but noticeably below cloud LLMs
- ZH/RU->EN quality: generally better than the reverse direction
- **No additional RAM cost** -- reuses the already-loaded model
- **No additional latency** -- same single inference pass
- Quality gap vs cloud: moderate for simple/conversational text, larger for complex/technical text

**Quality Reality Check:**
A 1.7B model doing cleanup+translation simultaneously is asking a lot. For conversational voice messages (Untype's primary use case), it's adequate. For formal/technical text, quality drops.

**Verdict:** Best "free lunch" option. Zero additional cost in RAM, latency, or money. Quality is acceptable for conversational use. Can fall back to cloud for higher quality.

---

### 6. Cloud Translation APIs (Baseline Comparison)

| API | Price / 1M chars | Free Tier | Quality (EN-RU) | Quality (EN-ZH) | Latency |
|---|---|---|---|---|---|
| DeepL | $25 + $5.49/mo base | 500K chars/mo | Excellent | Very Good | ~200ms |
| Google Cloud Translation | $20 | 500K chars/mo | Very Good | Very Good | ~200ms |
| Google LLM Translation | $10 in + $10 out / 1M | None | Excellent | Excellent | ~300ms |
| Microsoft Translator | $10 | 2M chars/mo (12 mo) | Very Good | Very Good | ~200ms |

**For Untype's volume** (voice messages, ~100-500 chars each, maybe 50-200/day):
- ~10K-100K chars/month -- well within free tiers
- Even at paid rates: < $3/month

**Verdict:** Cloud APIs are cheap enough to be viable. But they add a network dependency and another API key to manage. Not worth it if we can get comparable quality from the LLM already in the pipeline.

---

## Key Questions Answered

### Is one-pass "cleanup + translate" via LLM good enough?

**Yes, for Untype's use case.** Voice messages are conversational, short, and tolerant of minor translation imperfections. A cloud LLM (GPT-4o, Claude, Qwen-MT) does this excellently. A local 1.7B model does it acceptably.

The one-pass approach is strictly superior to separate cleanup + translate steps: same quality, half the latency, half the cost.

### Quality gap: on-device (NLLB 1.3B) vs cloud (DeepL)?

For EN<->RU and EN<->ZH on conversational text:
- **NLLB 1.3B**: ~85-90% of DeepL quality. Occasional awkward phrasing, handles idioms poorly.
- **DeepL**: Benchmark leader for European pairs. Slightly less dominant for ZH.
- **GPT-4o / Claude**: Matches or exceeds DeepL on most pairs in human evaluation (WMT24).
- **Qwen3 1.7B (local)**: ~70-80% of DeepL quality. Adequate for chat, insufficient for formal text.

### Can Apple Translation be called programmatically?

- **macOS 15 (Sequoia)**: Only via SwiftUI `.translationTask()` modifier. AppKit apps need an `NSHostingView` workaround.
- **macOS 26 (Tahoe, Fall 2026)**: `TranslationSession.init(installedSource:target:)` enables direct instantiation. Clean programmatic API.
- Both target pairs (EN<->RU, EN<->ZH) are supported.

### RAM/disk budget with Qwen3 1.7B already loaded?

| Configuration | Additional RAM | Additional Disk |
|---|---|---|
| LLM one-pass (no extra model) | 0 | 0 |
| Apple Translation | 0 (system models) | 0 (system manages) |
| NLLB 600M (INT8) | ~600 MB | ~600 MB |
| NLLB 1.3B (INT8) | ~1.3 GB | ~1.3 GB |
| MarianMT (2 pairs) | ~600 MB | ~600 MB |

On an 8 GB machine running Qwen3 1.7B (~2-3 GB), adding NLLB 1.3B would push total ML memory to ~4-5 GB, leaving little headroom. **LLM one-pass or Apple Translation are the only zero-cost options.**

### Latency impact on the pipeline?

Current pipeline: Transcription (~1-3s) -> Cleanup (~0.5-1s local, ~0.3-0.5s cloud) -> Insert

With translation:
| Approach | Additional Latency |
|---|---|
| LLM one-pass (cleanup+translate) | ~0ms (same inference) |
| Apple Translation (after cleanup) | ~200-300ms |
| NLLB 1.3B (after cleanup) | ~500-800ms |
| Cloud API (after cleanup) | ~200-400ms (network) |

**One-pass LLM adds zero latency. Dedicated translation adds 200-800ms as a second step.**

---

## Recommendation

### Primary approach: LLM one-pass cleanup + translate

Modify the existing cleanup prompt to include translation when the user has a target language configured. This is the clear winner on every axis:

- **Zero additional RAM/disk** (reuses cleanup model)
- **Zero additional latency** (same inference pass)
- **Zero additional cost** (cloud) or already paid for (local)
- **Minimal integration work** (prompt change + language setting)
- **Quality**: excellent with cloud LLMs, acceptable with local 1.7B

**Implementation:**
1. Add `targetLanguage: String?` to `LLMRequest`
2. Update `PromptTemplates` to conditionally append translation instruction
3. Add language picker to Settings (EN, RU, ZH + auto-detect source)
4. No new dependencies

### Fallback / Enhancement: Apple Translation Framework

For users who want higher-quality on-device translation without cloud dependency:

- Add as optional second step after cleanup (when local LLM quality is insufficient)
- macOS 15+: use `NSHostingView` workaround to obtain `TranslationSession`
- macOS 26+: direct `TranslationSession.init()` -- clean integration
- Free, zero RAM, system-maintained models

**Implementation:**
1. Add `Translation` framework import (conditional on macOS 15+)
2. Create `AppleTranslationService` in `Processing/` or new `Translation/` directory
3. Embed hidden SwiftUI view for session access (macOS 15 workaround)
4. Wire into `ProcessingCoordinator` as optional post-cleanup step

### Not recommended for Untype

- **NLLB / Madlad-400 / MarianMT**: Too much integration complexity for a native Swift app. No clean Swift-native inference path. Significant RAM overhead. Only justified if Apple Translation is unavailable and we need offline translation without an LLM -- but we already have an LLM.
- **Dedicated cloud translation APIs** (DeepL, Google, Microsoft): Adds API key management and network dependency for marginal quality gain over LLM one-pass. Not worth the complexity when GPT-4o/Claude already translate excellently.

### Implementation Priority

1. **Phase 1 (MVP)**: LLM one-pass -- modify prompt, add language setting. ~1-2 hours of work.
2. **Phase 2 (Polish)**: Apple Translation as quality upgrade for on-device path. ~4-8 hours. Requires macOS 15+.
3. **Phase 3 (Never)**: Dedicated translation models. Only if requirements change drastically.

---

## Sources

- [Apple TranslationSession Documentation](https://developer.apple.com/documentation/translation/translationsession)
- [Meet the Translation API - WWDC24](https://developer.apple.com/videos/play/wwdc2024/10117/)
- [Translation API in iOS 18 and macOS Sequoia](https://mjtsai.com/blog/2024/07/04/translation-api-in-ios-17-and-macos-sequoia/)
- [Apple Developer Forums - TranslationSession init](https://developer.apple.com/forums/thread/758156)
- [Translation's Concurrency Pattern Spells Out the Plank for UIKit](https://captainswiftui.substack.com/p/translations-concurrency-pattern)
- [Popular Open-Source Translation Models for Mobile & Embedded (2025)](https://picovoice.ai/blog/open-source-translation/)
- [Meta NLLB-200 Paper](https://arxiv.org/abs/2207.04672)
- [NLLB-200 on HuggingFace](https://huggingface.co/docs/transformers/model_doc/nllb)
- [Madlad-400-3B-MT on HuggingFace](https://huggingface.co/google/madlad400-3b-mt)
- [MLX Transformers](https://github.com/ToluClassics/mlx-transformers)
- [CTranslate2](https://github.com/OpenNMT/CTranslate2)
- [MarianMT Documentation](https://huggingface.co/docs/transformers/en/model_doc/marian)
- [Best LLMs for Translation (2025)](https://www.getblend.com/blog/which-llm-is-best-for-translation/)
- [Translation API Pricing Comparison (2026)](https://www.buildmvpfast.com/api-costs/translation)
- [Qwen-MT Blog](https://qwenlm.github.io/blog/qwen-mt/)
- [Benchmarking On-Device ML on Apple Silicon with MLX](https://arxiv.org/html/2510.18921v1)
- [DeepL API Pricing](https://support.deepl.com/hc/en-us/articles/360021200939-DeepL-API-plans)
- [Google Cloud Translation Pricing](https://cloud.google.com/translate/pricing)
