# LLM Provider Research for Untype

**Date:** 2026-04-10
**Purpose:** Evaluate cloud LLM providers for speech-to-text cleanup pipeline
**Use case:** Short text cleanup (50-200 words), latency-critical, future multilingual support (EN, RU, ZH)

---

## 1. Comparison Table

### 1A. Proprietary US/Western Providers

| Provider | Model | Input $/1M | Output $/1M | TTFT (est.) | Throughput | OpenAI-compat? | Multilingual (EN/RU/ZH) | Notes |
|----------|-------|-----------|-------------|-------------|------------|----------------|------------------------|-------|
| Anthropic | Haiku 4.5 | $1.00 | $5.00 | ~600ms | ~120 t/s | No (own API) | Good / Good / Good | Fastest TTFT among proprietary models (~597ms benchmarked). Best quality/price ratio for small tasks |
| Anthropic | Sonnet 4.6 | $3.00 | $15.00 | ~2.0s | ~80 t/s | No (own API) | Excellent / Excellent / Excellent | Overkill for cleanup task. High quality but 5x TTFT vs Haiku |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 | ~400ms | ~150 t/s | Yes (native) | Good / Good / Good | Best price among proprietary Western models. Strong translation |
| OpenAI | GPT-4o | $2.50 | $10.00 | ~500ms | ~100 t/s | Yes (native) | Excellent / Excellent / Excellent | Overkill for cleanup. Good TTFT but expensive |
| Google | Gemini 2.0 Flash | $0.10 | $0.40 | ~300ms | ~200 t/s | No (own API) | Good / Good / Good | **DEPRECATED June 2026.** Cheapest option but end-of-life |
| Google | Gemini 2.5 Flash | $0.30 | $2.50 | ~440ms | ~223 t/s | No (own API) | Good / Good / Good | Excellent latency + throughput. Good value |
| Google | Gemini 2.5 Pro | $1.00 | $10.00 | ~800ms | ~100 t/s | No (own API) | Excellent / Excellent / Excellent | Overkill for cleanup |

### 1B. Chinese Providers (Direct API)

| Provider | Model | Input $/1M | Output $/1M | TTFT (est.) | Throughput | OpenAI-compat? | Multilingual (EN/RU/ZH) | Accessible outside CN? | Notes |
|----------|-------|-----------|-------------|-------------|------------|----------------|------------------------|----------------------|-------|
| DeepSeek | V3 (deepseek-chat) | $0.014 | $0.028 | ~800ms | ~97 t/s | Yes | Good / Fair / Excellent | Yes (api.deepseek.com) | Absurdly cheap. 164K context. Occasional capacity issues |
| DeepSeek | R1 (deepseek-reasoner) | $0.55 | $2.00 | ~7.0s | ~50 t/s | Yes | Good / Fair / Excellent | Yes | Reasoning model, way too slow for this use case |
| Alibaba | Qwen3 8B | $0.05 | $0.40 | ~300ms | ~200 t/s | Yes (via Alibaba) | Good / Good / Excellent | Yes (Singapore region) | Smallest Qwen3, very fast |
| Alibaba | Qwen3 Max | $0.78 | $3.90 | ~600ms | ~100 t/s | Yes (via Alibaba) | Excellent / Excellent / Excellent | Yes (Singapore region) | Best multilingual among Chinese models. 119 languages |
| Alibaba | Qwen3.5 Plus | $0.26 | $1.56 | ~500ms | ~120 t/s | Yes (via Alibaba) | Excellent / Excellent / Excellent | Yes (Singapore region) | Good mid-tier option |
| Moonshot | Kimi K2.5 | $0.60 | $2.50 | ~500ms | ~100 t/s | Yes | Good / Good / Excellent | Difficult (CN phone needed for direct) | Available via OpenRouter, Cloudflare Workers AI. Auto-caching reduces input to $0.15/M |
| MiniMax | MiniMax M1 | $0.40 | $1.76 | ~500ms | ~100 t/s | Yes | Good / Fair / Excellent | Yes (api.minimax.io global) | Good value. Long-context specialist |

### 1C. Open-Source via API Hosts

| Provider | Model | Input $/1M | Output $/1M | TTFT (est.) | Throughput | OpenAI-compat? | Multilingual (EN/RU/ZH) | Notes |
|----------|-------|-----------|-------------|-------------|------------|----------------|------------------------|-------|
| Groq | Llama 3.1 8B | $0.05 | $0.08 | ~200ms | ~730 t/s | Yes | Fair / Fair / Fair | Fastest inference. Limited model quality |
| Groq | Llama 4 Scout | $0.08 | $0.30 | ~690ms | ~300 t/s | Yes | Good / Fair / Good | Good balance of speed + quality |
| Groq | Qwen3 32B | $0.20 | $0.50 | ~300ms | ~400 t/s | Yes | Good / Good / Excellent | Best multilingual on Groq |
| Together | Llama 4 Maverick | $0.27 | $0.85 | ~400ms | ~150 t/s | Yes | Good / Fair / Good | Larger Llama 4 variant |
| Together | Mistral Small | $0.20 | $0.60 | ~300ms | ~200 t/s | Yes | Good / Good / Good | Solid all-rounder |
| DeepInfra | Gemma 3 27B | $0.08 | $0.16 | ~350ms | ~180 t/s | Yes | Good / Fair / Good | Google's open model, very cheap on DeepInfra |
| Various | Mistral Nemo 12B | $0.02 | $0.04 | ~250ms | ~300 t/s | Yes | Fair / Fair / Fair | Cheapest model available anywhere. Quality may be insufficient |

---

## 2. Rate Limits Summary

| Provider | Free Tier | Tier 1 (entry paid) | Notes |
|----------|-----------|---------------------|-------|
| Anthropic | None | 1,000 RPM (Tier 2, $40 spend) | Token bucket algorithm. Scales with spend |
| OpenAI | Limited | ~500 RPM for 4o-mini (Tier 1, $5 spend) | 4o-mini gets ~10x the TPM of 4o |
| Google | 10 RPM / 250 RPD (2.5 Flash) | Pay-as-you-go removes RPM caps | Free tier severely cut Dec 2025. Not suitable for production |
| DeepSeek | Generous free tier | ~60 RPM standard | Periodic capacity constraints |
| Alibaba/Qwen | Limited free quota (Singapore) | Pay-as-you-go | Savings plans from $10 |
| Groq | ~30 RPM free | Higher with paid | Best for prototyping |
| Together | Pay-as-you-go | No strict RPM for small usage | |
| Fireworks | Pay-as-you-go | Scales with spend | |

---

## 3. Data Privacy & Residency

| Provider | Data Storage | Privacy Policy | Concern Level |
|----------|-------------|----------------|---------------|
| Anthropic | US | Does not train on API data. SOC 2 compliant | Low |
| OpenAI | US | Does not train on API data (since Mar 2023). SOC 2 | Low |
| Google | Varies by region | Does not train on paid API data. Vertex AI offers data residency | Low |
| DeepSeek | **China (PRC)** | Data stored in China. Subject to Chinese data laws. No GDPR representative | **High** |
| Alibaba/Qwen | China / Singapore | Singapore region available. Alibaba Cloud compliance | Medium (use SG region) |
| Moonshot/Kimi | **China (PRC)** | Data stored in China. ZDR agreement available since Feb 2026 | **High** |
| MiniMax | **China (PRC)** | Global endpoint exists but unclear data residency | **High** |
| Groq | US | Does not train on data. SOC 2 | Low |
| Together | US | Does not train on data | Low |
| Fireworks | US | Does not train on data | Low |

**Recommendation:** For users concerned about data privacy, avoid sending user data directly to Chinese provider APIs. Instead, use Chinese models (Qwen, DeepSeek) through US-hosted inference providers (Groq, Together, Fireworks) where they are available as open-source deployments.

---

## 4. Swift SDK Landscape

### 4A. Existing SDKs

| Package | Stars | Platforms | async/await | Sendable | Providers | Maintained? | Notes |
|---------|-------|-----------|-------------|----------|-----------|-------------|-------|
| [MacPaw/OpenAI](https://github.com/MacPaw/OpenAI/) | 2,900 | iOS 15+, macOS 13+ | Yes | Unknown | OpenAI only | Yes (768 commits) | Most popular. Community-driven. Responses API, MCP support |
| [jamesrochabrun/SwiftOpenAI](https://github.com/jamesrochabrun/SwiftOpenAI) | 650 | iOS 15+, macOS 13+, watchOS, Linux | Yes | Unknown | OpenAI, Azure, Anthropic, Gemini, Ollama, Groq, xAI, OpenRouter, **DeepSeek** | Yes (504 commits) | Multi-provider via OpenAI-compat. Best breadth |
| [jamesrochabrun/SwiftAnthropic](https://github.com/jamesrochabrun/SwiftAnthropic) | 234 | iOS 15+, macOS 12+, Linux | Yes | Unknown | Anthropic only | Yes | Full Anthropic API coverage. Extended thinking, tool use |
| [fumito-ito/AnthropicSwiftSDK](https://github.com/fumito-ito/AnthropicSwiftSDK) | ~100 | macOS, iOS | Yes | Unknown | Anthropic only | Active | Alternative Anthropic SDK |
| [tthew/anthropic-swift-sdk](https://github.com/tthew/anthropic-swift-sdk) | ~50 | iOS, macOS | Yes | Yes (actors) | Anthropic only | Active | Uses actors for thread safety |

### 4B. Can a Single OpenAI-Compatible Client Cover Everything?

**Yes, with caveats.**

The following providers all expose `/v1/chat/completions` endpoints with OpenAI-compatible request/response formats:

| Provider | Base URL | Works with OpenAI SDK? |
|----------|----------|----------------------|
| OpenAI | `https://api.openai.com/v1` | Native |
| DeepSeek | `https://api.deepseek.com/v1` | Yes |
| Qwen (Alibaba) | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | Yes |
| Kimi (Moonshot) | `https://api.moonshot.cn/v1` | Yes |
| MiniMax | `https://api.minimax.io/v1` | Yes |
| Groq | `https://api.groq.com/openai/v1` | Yes |
| Together | `https://api.together.xyz/v1` | Yes |
| Fireworks | `https://api.fireworks.ai/inference/v1` | Yes |
| OpenRouter | `https://openrouter.ai/api/v1` | Yes (aggregator for 300+ models) |

**Not OpenAI-compatible:** Anthropic (Messages API), Google Gemini (Generative Language API). These require dedicated clients or adapter wrappers.

**Recommendation:** Build a single lightweight OpenAI-compatible HTTP client using URLSession. This covers ~80% of providers. Add a thin Anthropic adapter for Claude models. Skip Gemini's native API unless specifically needed (use Gemini via OpenRouter instead for unified access).

---

## 5. Tiered Recommendations

### Best Overall: GPT-4o-mini (OpenAI)
- **Why:** $0.15/$0.60 per 1M tokens. ~400ms TTFT. Excellent quality for short text cleanup. Native OpenAI API (gold standard). Strong multilingual. Generous rate limits. US data residency.
- **Monthly cost estimate:** ~$0.11/user (see Section 7)
- **Risk:** Low. OpenAI is the most battle-tested API.

### Best Budget: DeepSeek V3 via Groq or Together
- **Why:** $0.014/$0.028 native (or ~$0.05/$0.10 via US hosts). 100x cheaper than GPT-4o-mini direct. Quality is good enough for cleanup tasks.
- **Monthly cost estimate:** ~$0.006/user (direct) or ~$0.02/user (via US host)
- **Risk:** Medium. DeepSeek direct has capacity issues. Quality slightly below GPT-4o-mini for English. Via Groq/Together mitigates privacy + reliability concerns.

### Best Multilingual (EN/RU/ZH): Qwen3 32B via Groq
- **Why:** Qwen3 series supports 119 languages. Best-in-class for Chinese. Strong Russian. Available on Groq at $0.20/$0.50 per 1M with ~300ms TTFT. US data residency via Groq.
- **Monthly cost estimate:** ~$0.10/user
- **Risk:** Low-medium. Groq availability for Qwen3 models is good.

### Best Latency: Groq + Llama 3.1 8B or Qwen3 32B
- **Why:** Groq's LPU delivers ~200ms TTFT and 400-730 tok/s. For a 150-token response, total latency is under 600ms including network.
- **Monthly cost estimate:** ~$0.02/user
- **Risk:** Low. Groq rate limits on free tier may require paid plan for production.

### Best Open-Source: Llama 4 Scout (via Groq/Together)
- **Why:** Meta's latest open model. Good quality, fast inference, cheap ($0.08/$0.30). Available on multiple hosts.
- **Monthly cost estimate:** ~$0.06/user
- **Risk:** Low.

### Best Self-Hosted: MLX + Qwen3 1.7B (Q4_K_M)
- **Why:** Apple-native ML framework with Swift SPM bindings. Qwen3 1.7B at Q4 uses ~1.1GB disk, ~1.5GB RAM. 80-150 tok/s on Apple Silicon. Strong multilingual (EN/RU/ZH). Fully offline after initial 1.1GB model download. Zero ongoing cost.
- **Monthly cost estimate:** $0/user
- **Risk:** Medium. 1.5-3s latency (vs 0.5-1.5s cloud). Quality is good but not excellent for edge cases. ~1.5GB RAM overhead while active. First-run UX requires model download.
- **Upgrade path:** Qwen3 4B (Q4, ~2.5GB) for better quality if RAM allows; Apple Foundation Models when macOS 26 is viable.

### Runner-Up / Balanced Choice: Gemini 2.5 Flash
- **Why:** $0.30/$2.50 per 1M. 440ms TTFT. 223 tok/s. Google's infrastructure is rock-solid. Good multilingual.
- **Monthly cost estimate:** ~$0.40/user
- **Risk:** Requires Gemini-specific client or OpenRouter. Pricing is mid-range.

---

## 6. API Architecture Recommendation

### Approach: Single Generic Client + Provider Enum

Build one `LLMClient` using URLSession that speaks the OpenAI `/v1/chat/completions` format. Configure it with a `Provider` enum that carries base URL and API key. This covers OpenAI, DeepSeek, Qwen, Kimi, MiniMax, Groq, Together, Fireworks, and OpenRouter.

For Anthropic (if needed later), add a thin `AnthropicAdapter` that translates to/from the Messages API format.

**Why not use an existing SDK?**
- MacPaw/OpenAI (2.9k stars) is good but OpenAI-only and carries more weight than needed
- jamesrochabrun/SwiftOpenAI supports many providers but is a large dependency
- For Untype's simple use case (single endpoint, short messages, no streaming needed), a ~200-line URLSession client is simpler, lighter, and fully under your control
- No Sendable conformance verified in any SDK, which matters for Swift 6 strict concurrency

**Why not per-provider SDKs?**
- Adds 3-5 SPM dependencies
- Each has different API surfaces, error types, retry behavior
- Harder to switch providers at runtime
- More code to maintain

---

## 7. Cost Estimate Per User Per Month

**Assumptions:**
- 100 requests/day
- 150 tokens input + 150 tokens output per request
- 30 days/month
- Total: 3,000 requests/month = 450K input tokens + 450K output tokens

| Provider/Model | Input Cost | Output Cost | **Monthly Total** |
|----------------|-----------|-------------|-------------------|
| DeepSeek V3 (direct) | $0.006 | $0.013 | **$0.019** |
| Mistral Nemo 12B | $0.009 | $0.018 | **$0.027** |
| Groq Llama 3.1 8B | $0.023 | $0.036 | **$0.059** |
| Groq Llama 4 Scout | $0.036 | $0.135 | **$0.171** |
| DeepInfra Gemma 3 27B | $0.036 | $0.072 | **$0.108** |
| GPT-4o-mini | $0.068 | $0.270 | **$0.338** |
| Groq Qwen3 32B | $0.090 | $0.225 | **$0.315** |
| Gemini 2.5 Flash | $0.135 | $1.125 | **$1.260** |
| Qwen3.5 Plus | $0.117 | $0.702 | **$0.819** |
| Haiku 4.5 | $0.450 | $2.250 | **$2.700** |
| Kimi K2.5 | $0.270 | $1.125 | **$1.395** |
| GPT-4o | $1.125 | $4.500 | **$5.625** |
| Sonnet 4.6 | $1.350 | $6.750 | **$8.100** |

**Key insight:** Even the most expensive option (Sonnet 4.6) costs only $8.10/user/month at 100 req/day. The cheapest options (DeepSeek V3, Mistral Nemo) cost under $0.03/month. Cost is not a differentiator at this usage level -- latency, quality, and privacy matter more.

---

## 8. Draft System Prompt for Speech Cleanup

```
You are a speech-to-text cleanup assistant. You receive raw transcriptions from a voice dictation system. Your job is to clean up the text while preserving the speaker's intent, tone, and meaning.

Rules:
1. Remove filler words (um, uh, like, you know, so, basically, actually, I mean)
2. Fix grammar and punctuation
3. Remove false starts and repeated words
4. Preserve the speaker's vocabulary and tone -- do not make it more formal or less formal
5. Preserve technical terms, proper nouns, and domain-specific language exactly as spoken
6. Do not add information that was not in the original
7. Do not remove meaningful content
8. If the transcription is a single word or very short phrase, return it as-is with only capitalization/punctuation fixes
9. Output ONLY the cleaned text. No explanations, no quotes, no metadata.

The input language may be English, Russian, or Chinese. Respond in the same language as the input.
```

**Token cost of this prompt:** ~180 tokens. This is a fixed overhead per request. With prompt caching (supported by OpenAI, Anthropic, DeepSeek, Gemini), this drops to near-zero after the first call.

---

## 9. Implementation Sketch for Swift

```swift
import Foundation

// MARK: - Provider Configuration

enum LLMProvider: String, CaseIterable, Sendable {
    case openAI
    case deepSeek
    case groq
    case together
    case fireworks
    case qwen
    case openRouter

    var baseURL: URL {
        switch self {
        case .openAI:     return URL(string: "https://api.openai.com/v1")!
        case .deepSeek:   return URL(string: "https://api.deepseek.com/v1")!
        case .groq:       return URL(string: "https://api.groq.com/openai/v1")!
        case .together:   return URL(string: "https://api.together.xyz/v1")!
        case .fireworks:  return URL(string: "https://api.fireworks.ai/inference/v1")!
        case .qwen:       return URL(string: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")!
        case .openRouter: return URL(string: "https://openrouter.ai/api/v1")!
        }
    }
}

struct LLMConfiguration: Sendable {
    let provider: LLMProvider
    let apiKey: String
    let model: String
    let systemPrompt: String
    let maxTokens: Int
    let temperature: Double

    static func defaultCleanup(provider: LLMProvider, apiKey: String, model: String) -> Self {
        LLMConfiguration(
            provider: provider,
            apiKey: apiKey,
            model: model,
            systemPrompt: Self.cleanupSystemPrompt,
            maxTokens: 512,
            temperature: 0.3
        )
    }

    private static let cleanupSystemPrompt = """
    You are a speech-to-text cleanup assistant. You receive raw transcriptions \
    from a voice dictation system. Clean up the text while preserving the \
    speaker's intent, tone, and meaning. Remove filler words, fix grammar, \
    remove false starts. Do not add or remove meaningful content. Output ONLY \
    the cleaned text.
    """
}

// MARK: - Request/Response Types (OpenAI-compatible)

struct ChatCompletionRequest: Encodable, Sendable {
    let model: String
    let messages: [ChatMessage]
    let max_tokens: Int
    let temperature: Double
}

struct ChatMessage: Codable, Sendable {
    let role: String  // "system" | "user" | "assistant"
    let content: String
}

struct ChatCompletionResponse: Decodable, Sendable {
    let id: String
    let choices: [Choice]
    let usage: Usage

    struct Choice: Decodable, Sendable {
        let index: Int
        let message: ChatMessage
        let finish_reason: String?
    }

    struct Usage: Decodable, Sendable {
        let prompt_tokens: Int
        let completion_tokens: Int
        let total_tokens: Int
    }
}

// MARK: - LLM Client

actor LLMClient {
    private let configuration: LLMConfiguration
    private let session: URLSession
    private let encoder: JSONEncoder
    private let decoder: JSONDecoder

    init(configuration: LLMConfiguration) {
        self.configuration = configuration
        let sessionConfig = URLSessionConfiguration.default
        sessionConfig.timeoutIntervalForRequest = 15  // 15s hard timeout
        self.session = URLSession(configuration: sessionConfig)
        self.encoder = JSONEncoder()
        self.decoder = JSONDecoder()
    }

    /// Clean up raw transcription text. Returns cleaned text.
    func cleanup(_ rawTranscription: String) async throws -> String {
        let request = ChatCompletionRequest(
            model: configuration.model,
            messages: [
                ChatMessage(role: "system", content: configuration.systemPrompt),
                ChatMessage(role: "user", content: rawTranscription)
            ],
            max_tokens: configuration.maxTokens,
            temperature: configuration.temperature
        )

        let response = try await send(request)
        guard let firstChoice = response.choices.first else {
            throw LLMError.emptyResponse
        }
        return firstChoice.message.content.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private func send(_ body: ChatCompletionRequest) async throws -> ChatCompletionResponse {
        let url = configuration.provider.baseURL.appendingPathComponent("chat/completions")
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(configuration.apiKey)", forHTTPHeaderField: "Authorization")
        urlRequest.httpBody = try encoder.encode(body)

        let (data, httpResponse) = try await session.data(for: urlRequest)

        guard let http = httpResponse as? HTTPURLResponse else {
            throw LLMError.invalidResponse
        }

        switch http.statusCode {
        case 200:
            return try decoder.decode(ChatCompletionResponse.self, from: data)
        case 429:
            throw LLMError.rateLimited(retryAfter: http.value(forHTTPHeaderField: "Retry-After"))
        case 400...499:
            throw LLMError.clientError(http.statusCode, String(data: data, encoding: .utf8))
        case 500...599:
            throw LLMError.serverError(http.statusCode)
        default:
            throw LLMError.unexpectedStatus(http.statusCode)
        }
    }
}

enum LLMError: Error, Sendable {
    case emptyResponse
    case invalidResponse
    case rateLimited(retryAfter: String?)
    case clientError(Int, String?)
    case serverError(Int)
    case unexpectedStatus(Int)
}

// MARK: - Usage Example

// let client = LLMClient(configuration: .defaultCleanup(
//     provider: .openAI,
//     apiKey: "sk-...",
//     model: "gpt-4o-mini"
// ))
// let cleaned = try await client.cleanup("Um so basically I was thinking that we should like maybe go ahead and um start the project")
// => "I was thinking that we should go ahead and start the project."
```

### Key Design Decisions

1. **`actor LLMClient`** -- thread-safe by default, no manual locking needed
2. **All types are `Sendable`** -- safe to pass across concurrency domains in Swift 6
3. **Single `cleanup(_:)` method** -- the only public API surface needed for MVP
4. **15-second timeout** -- fail fast if the provider is slow
5. **No streaming** -- for 50-200 word responses, streaming adds complexity with minimal UX benefit. The full response arrives in <1 second from most providers
6. **Provider switching** -- change `LLMProvider` and `model` string to switch between any OpenAI-compatible provider at runtime
7. **No external dependencies** -- pure URLSession, works on macOS 13+

### Future Extensions

```swift
// Translation (future)
func translate(_ text: String, from: Language, to: Language) async throws -> String

// Tone adjustment (future)
func adjustTone(_ text: String, tone: ToneStyle) async throws -> String

// Provider fallback chain (future)
func cleanupWithFallback(_ text: String, providers: [LLMConfiguration]) async throws -> String
```

---

## 10. Self-Hosted / On-Device Options

### 10A. Local Inference Engines for macOS

| Engine | Integration Method | User Setup | Dev Effort | Latency Overhead | Offline? | Notes |
|--------|-------------------|------------|------------|-----------------|----------|-------|
| **Ollama** | HTTP API (URLSession) | Install Ollama app + pull model | Low — just HTTP calls | ~5-10ms (localhost) | Yes | Easiest path, external dependency |
| **llama.cpp (server)** | HTTP API (URLSession) | None (bundle binary) | Medium — bundle binary, manage process | ~5-10ms (localhost) | Yes | Bundle-able, well-proven |
| **llama.cpp (library)** | Direct C API via SPM | None | High — C bridge, manage memory | <1ms | Yes | Best performance, most work |
| **MLX Swift** | Swift API via SPM | None | Medium — learn MLX API | <1ms | Yes | Most Apple-native, good Swift bindings |
| **Apple Foundation Models** | Swift API (OS framework) | macOS 26+ | Very Low — highest-level API | <1ms | Yes | Future option — macOS 26 required |

**Ollama** wraps llama.cpp in a local HTTP server with OpenAI-compatible API (`localhost:11434/v1/chat/completions`). Easy to integrate but requires separate install. Most desktop apps (Continue, Open Interpreter) use this approach.

**llama.cpp** can be linked directly as an SPM dependency (C API) or run in server mode. Best performance and zero external dependencies, but the C API requires a thin Swift wrapper (~200-300 lines).

**MLX Swift** (`mlx-swift` SPM package) is Apple's ML framework optimized for unified memory on Apple Silicon. First-class Swift bindings, good performance, integrates like any SPM package. Models from `mlx-community` on HuggingFace.

**Apple Foundation Models** (`import FoundationModels`, macOS 26+) provides a high-level `LanguageModelSession` API with zero model management. Dream solution but requires macOS 26 — not viable as primary path until ~2027-2028 minimum target.

### 10B. Small Models for Text Cleanup

| Model | Params | Disk (Q4) | RAM (Q4) | tok/s M1 | tok/s M3 Pro | tok/s M4 | Cleanup Quality | Multilingual | Notes |
|-------|--------|-----------|----------|----------|-------------|----------|----------------|-------------|-------|
| Qwen3 0.6B | 0.6B | ~400MB | ~600MB | ~120 | ~170 | ~190 | Fair — over-edits | Good ZH | Too small for nuanced cleanup |
| **Qwen3 1.7B** | 1.7B | ~1.1GB | ~1.5GB | ~80 | ~130 | ~150 | **Good** | Good EN/ZH/RU | **Best quality-to-speed ratio** |
| Gemma 3 1B | 1B | ~700MB | ~1.0GB | ~100 | ~150 | ~170 | Good | Good EN | Solid English grammar |
| Llama 3.2 3B | 3.2B | ~2.0GB | ~2.6GB | ~55 | ~90 | ~110 | Good | Fair EN | Sometimes adds unwanted content |
| **Qwen3 4B** | 4B | ~2.5GB | ~3.2GB | ~45 | ~80 | ~100 | **Very Good** | Excellent | Sweet spot if RAM allows |
| Phi-4-mini | 3.8B | ~2.3GB | ~3.0GB | ~48 | ~82 | ~100 | Very Good | Good EN | May over-think simple tasks |
| Gemma 3 4B | 4B | ~2.6GB | ~3.3GB | ~42 | ~75 | ~95 | Very Good | Good EN | Slightly better than Qwen3 4B for English |
| Qwen3 8B | 8B | ~4.7GB | ~5.5GB | ~25 | ~50 | ~65 | Excellent | Excellent | Overkill for cleanup; near-cloud quality |

Recommended quantization: **Q4_K_M** — negligible quality loss, ~35% of FP16 size.

### 10C. Self-Hosted Recommendation: MLX + Qwen3 1.7B (Q4)

- **MLX** is the most Apple-native engine — SPM package, Swift API, optimized for unified memory
- **Qwen3 1.7B Q4** is the sweet spot: ~1.1GB disk, ~1.5GB RAM, 80-150 tok/s
- A 200-word cleanup response (~270 tokens) completes in 2-3s on M1, <2s on M2+
- Strong multilingual (EN/RU/ZH) from the Qwen3 family
- Fully offline after initial model download
- Zero ongoing cost

**Integration approach:**
- Download model from HuggingFace on first run (`mlx-community/Qwen3-1.7B-4bit`)
- Store in `~/Library/Application Support/Untype/models/`
- Keep model loaded while app is active, unload after 5 min idle to free RAM
- Show download progress on first launch (~1.1GB, ~3 min on 50 Mbps)

### 10D. Trade-offs: Local vs Cloud

| Factor | Local (MLX + Qwen3 1.7B) | Cloud (GPT-4o-mini) |
|--------|---------------------------|---------------------|
| Latency | 1.5-3s total | 0.5-1.5s total |
| First-run latency | 5-10s (model load) | <1s |
| Quality | Good (95% of cases) | Excellent |
| Privacy | Full — nothing leaves device | Text sent to third party |
| Offline | Always works | Requires internet |
| Cost | Free | ~$0.34/user/month |
| Disk space | ~1.1GB | None |
| RAM usage | ~1.5GB while active | None |
| Setup UX | First-run download | API key required |

**Bottom line:** For voice-to-text cleanup where privacy and offline matter, local inference is viable. The quality gap is small for this task. Offer cloud as opt-in fallback for max quality.

---

## 11. Strategic Recommendations

### Phase 1 (MVP): GPT-4o-mini via OpenAI-compatible client
- Simplest integration (OpenAI is the reference API)
- $0.34/user/month at 100 req/day -- negligible
- Strong quality for EN cleanup
- Good multilingual baseline
- US data residency, clear privacy policy

### Phase 2 (Provider Choice): Add Groq + self-hosted options
- Groq + Qwen3 32B for best cloud latency (~300ms TTFT) and multilingual quality
- Same OpenAI-compatible client, just swap base URL
- MLX + Qwen3 1.7B for fully offline, private, zero-cost inference
- Let users choose provider in Settings: Cloud (OpenAI/Groq/etc.) or Local (MLX)

### Phase 3 (Multilingual): Qwen3 for RU/ZH, GPT-4o-mini for EN
- Route based on detected input language
- Qwen3 series is best-in-class for Chinese and strong for Russian
- Local Qwen3 1.7B handles basic multilingual; cloud Qwen3 32B for higher quality

### Phase 4 (Apple Native): Apple Foundation Models (macOS 26+)
- Implement behind the same LLMProvider protocol
- Zero model management, zero downloads, zero disk space
- When macOS 26 becomes minimum target (~2027-2028), switch as default

### What NOT to do:
- **Don't use Anthropic for this task.** Claude is excellent but 3-10x more expensive than GPT-4o-mini with slower TTFT. The cleanup task doesn't need Sonnet/Opus quality.
- **Don't send user data to Chinese APIs directly.** Use Chinese models via US inference providers (Groq, Together) instead.
- **Don't build per-provider SDK integrations.** The OpenAI-compatible format covers everything you need.
- **Don't stream responses.** For 50-200 word outputs, non-streaming is simpler and the latency difference is imperceptible.
- **Don't use reasoning models (R1, o1, o3).** They're 10-100x slower and designed for math/code, not text cleanup.
- **Don't bundle Ollama.** It requires separate user install — use MLX for zero-dependency local inference instead.

---

## Sources

- [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [Google Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [DeepSeek Pricing](https://api-docs.deepseek.com/quick_start/pricing/)
- [Qwen API Platform](https://qwen.ai/apiplatform)
- [Alibaba Cloud Model Studio Pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)
- [Kimi K2.5 Pricing](https://pricepertoken.com/pricing-page/model/moonshotai-kimi-k2)
- [MiniMax Pricing](https://platform.minimax.io/docs/guides/pricing)
- [Groq Pricing](https://groq.com/pricing)
- [Together AI Pricing](https://www.together.ai/pricing)
- [Fireworks AI Pricing](https://fireworks.ai/pricing)
- [Artificial Analysis - Groq Performance](https://artificialanalysis.ai/providers/groq)
- [Artificial Analysis - Gemini 2.5 Flash](https://artificialanalysis.ai/models/gemini-2-5-flash)
- [LLM Latency Benchmarks 2026](https://www.kunalganglani.com/blog/llm-api-latency-benchmarks-2026)
- [BenchLM - LLM Speed Comparison](https://benchlm.ai/llm-speed)
- [MacPaw/OpenAI SDK](https://github.com/MacPaw/OpenAI/)
- [SwiftOpenAI](https://github.com/jamesrochabrun/SwiftOpenAI)
- [SwiftAnthropic](https://github.com/jamesrochabrun/SwiftAnthropic)
- [DeepSeek API Docs](https://api-docs.deepseek.com/)
- [MiniMax OpenAI-Compatible API](https://platform.minimax.io/docs/api-reference/text-openai-api)
- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Anthropic Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)
- [OpenAI Rate Limits](https://developers.openai.com/api/docs/guides/rate-limits)
- [DeepSeek Privacy Policy](https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html)
- [IAPP - DeepSeek Data Privacy Analysis](https://iapp.org/news/a/deepseek-and-the-china-data-question-direct-collection-open-source-and-the-limits-of-extraterritorial-enforcement)
- [Qwen3 Multilingual Blog](https://qwenlm.github.io/blog/qwen3/)
- [Kimi K2.5 on Cloudflare Workers AI](https://developers.cloudflare.com/changelog/post/2026-03-19-kimi-k2-5-workers-ai/)
- [MLX Swift](https://github.com/ml-explore/mlx-swift)
- [MLX Community Models](https://huggingface.co/mlx-community)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Ollama](https://ollama.com/)
- [Apple Foundation Models (WWDC 2025)](https://developer.apple.com/documentation/foundationmodels)
