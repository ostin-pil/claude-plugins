# Research: Cloud LLM Provider for Untype

## Context

Untype is a macOS voice-to-message app. The user speaks via a hotkey, 
the app transcribes (on-device via Apple Speech), then an LLM cleans/structures 
the text, and the result is pasted into the active app (Slack, email, etc.).

The processing architecture is protocol-based:

    protocol LLMProvider: Sendable {
        var name: String { get }
        func process(_ request: LLMRequest) async throws -> LLMResponse
    }

Currently only a `LocalProvider` exists (rule-based cleanup). The router 
already supports an optional `cloudProvider` with fallback strategies 
(cloud-primary-local-fallback, local-primary-cloud-fallback).

LLMRequest carries: requestId (UUID), inputText, locale, maxOutputTokens.
LLMResponse carries: requestId, outputText, providerName, modelName, latencyMs.
LLMError covers: cancelled, timeout, networkUnavailable, rateLimited, 
authFailed, quotaExceeded, server, invalidResponse, providerUnavailable.

No external dependencies beyond HotKey. No SDKs. Pure Swift, async/await only 
(no Combine). The app is non-sandboxed (Developer ID distribution).

## What the LLM does

The LLM receives raw speech transcription and must:
1. Clean filler words (um, uh, like, you know)
2. Fix grammar and punctuation
3. Preserve meaning and tone — this is NOT rewriting, it's cleanup
4. Keep it fast — this runs on every message, latency is critical

Future (Tier 2): tone adjustment, translation, bilingual output.
The bilingual/translation use case makes multilingual model strength 
especially relevant.

## Research questions

### 1. Provider selection
Compare ALL of the following for this specific use case:

**US/Western providers:**
- Claude (Anthropic) — Haiku 4.5, Sonnet 4.6
- GPT (OpenAI) — GPT-4o-mini, GPT-4o
- Gemini (Google) — Flash 2.0, Pro 2.5

**Chinese providers:**
- DeepSeek — V3, R1
- Qwen (Alibaba) — Qwen3 series
- Kimi K2 (Moonshot AI)
- MiniMax — MiniMax-M1

**Open-source / self-hostable (via API providers like Together, Fireworks, Groq):**
- Gemma 3 (Google)
- Llama 4 (Meta)
- Mistral / Mixtral

For each, evaluate:
- Which model tier fits best for short text cleanup (~50-200 words)?
- Latency: time-to-first-token and total response time for short prompts
- Cost per request at expected volumes (50-200 requests/day per user)
- API reliability, rate limits, uptime track record
- Quality of "cleanup without rewriting" — which model best preserves 
  the speaker's voice and tone?
- Multilingual strength (especially EN, RU, ZH for future translation)
- API availability and access from outside China (for Chinese providers)
- Data privacy / residency considerations

Produce a comparison table with: provider, model, cost/1M tokens (in+out), 
avg latency, multilingual rating, API accessibility, and notes.

### 2. API integration approach
- Direct HTTP (URLSession) vs official Swift SDK vs community SDK
- Most Chinese and open-source providers use OpenAI-compatible APIs — 
  can we build one generic OpenAI-compatible client that covers 
  DeepSeek, Qwen, Kimi, Together, Fireworks, Groq, etc.?
- Evaluate native SDKs: Anthropic Swift SDK, OpenAI Swift SDK — 
  maturity, maintenance, async/await support, Sendable conformance
- Streaming vs non-streaming for this payload size
- Is streaming worth the complexity for 50-200 word responses?
- Provider-agnostic design: one CloudProvider with configurable 
  endpoint+model, or separate provider classes?

### 3. Prompt design
- System prompt for speech cleanup (clean, don't rewrite)
- How to handle locale/language detection
- Token budget: what's the right maxOutputTokens for this use case?
- Do different providers/models need different prompts, or can one 
  prompt work across all?

### 4. Authentication & key storage
- macOS Keychain integration for API keys (Security framework)
- Key rotation / validation patterns
- How to handle first-time setup UX (no key yet)
- Supporting multiple provider keys simultaneously

### 5. Error handling & resilience
- Retry strategy for transient failures (map to existing LLMError cases)
- Timeout values for speech cleanup (user is waiting)
- Offline detection (NWPathMonitor) and graceful degradation to LocalProvider
- Rate limit handling with backoff
- Provider-specific error code mapping

### 6. Cost control
- Token counting / budget tracking
- Monthly usage caps
- Warn user when approaching limits
- Cost comparison: which provider gives best quality-per-dollar for 
  this narrow use case?

## Constraints
- Swift 5.9+, macOS 14+
- async/await only, no Combine
- All types must be Sendable
- No new SPM dependencies unless strongly justified
- Keychain storage in a separate SettingsManager (not in the provider)
- Prioritize providers with OpenAI-compatible API to minimize 
  integration surface area

## Deliverable
A recommendation with:
- Tiered ranking: best overall, best budget, best multilingual, 
  best latency, best open-source
- API integration architecture (single generic client vs per-provider)
- Provider comparison table
- Draft system prompt
- Rough cost estimate per user per month (by provider tier)
- Implementation sketch (types, method signatures, error mapping)
