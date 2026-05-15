# STT Work — Next Steps Guide

Companion to `whisper-landscape-2026.md` and `whisper-bench-2026-04-18.md`. Splits the follow-up work by *who has to do it*: steps I can pick up autonomously in a future session, steps that need you (account signup, spending, a key), and steps that need Apple Silicon hardware.

Working assumption: Untype's STT story is **pluggable engines with good defaults**, not a single pick (see `whisper-landscape-2026.md` § Product Principle).

---

## A. Auto-manageable — next session can do these without new input

These only need the keys + tools already in place (Groq in Keychain, OpenRouter env var, whisper.cpp + Moonshine installed). No spending, no signup, no hardware.

| # | Task | Effort | Why it matters |
|---|------|--------|----------------|
| A1 | Hand-verify `carmack_unscripted_en` and `joker_kotlin_ru` reference transcripts in `bench/audio-corpus.json` | 20 min | Biggest data-quality win. Every provider's WER is inflated ~2–3 pp by bad references. Rankings may flip at the margins. |
| A2 | Re-run the full bench with the fixed corpus → update `whisper-bench-2026-04-18.md` with trustworthy numbers | 15 min | Closes the loop on A1. |
| A3 | ~~Add `elevenlabs:<model>` provider to `tools/stt-bench/stt_compare.py` (proprietary endpoint shape, not OpenAI-compatible)~~ — landed in `be21efe`. Awaiting key top-up to bench Scribe v2. | 1 h | Path ready for when a key lands. Endpoint: `POST https://api.elevenlabs.io/v1/speech-to-text` with `multipart/form-data`, field `model_id=scribe_v2`. |
| A4 | Add `nvidia_nim:<model>` provider to the harness (OpenAI-compatible /v1/audio/transcriptions; free tier available) | 1 h | Path ready for when a NIM key lands. Endpoint at `https://integrate.api.nvidia.com/v1/audio/transcriptions`. |
| A5 | Add `deepgram:<model>` provider (`Token <key>` auth, proprietary /listen endpoint) | 1 h | Coverage for the main non-Whisper proprietary option. |
| A6 | Write a Swift `CloudSTTProvider` in `Sources/UntypeCore/Transcription/` modelled on the existing `CloudProvider` LLM pattern; wire into `TranscriptionHarness` as `PlaybackMode.cloud(provider:model:)` | ~day | Moves cloud STT out of the Python harness into the Swift bench, which is the only way to run CI gates on provider changes. |
| A7 | ~~Wire Groq `whisper-large-v3-turbo` into the app as the first cloud final-pass engine, behind a Settings toggle~~ — landed in `86ab7ea` (Settings stub) + `78c0ab5` (GroqSTTProvider). ~~On-device end-to-end test~~ — verified 2026-04-22. Full path (key → Keychain → record → cloud transcribe → polish → insert) confirmed working. | ~day | First real product use of the flexibility layer. Doesn't commit us to Groq as the only option — just lands the plumbing. |
| A8 | Swift bindings for whisper.cpp (`WhisperCppKit` SPM package or hand-rolled C bridge) → add a `WhisperCppService` implementing `TranscriptionProvider` | 1–2 days | Unlocks the local cross-silicon path, needed for the Intel local default and as a fallback-when-offline story on Apple Silicon too. |
| A9 | Bench Moonshine vs Apple `SFSpeechRecognizer` side-by-side for time-to-first-partial-token, not just end-to-end WER | Half day | Decides whether Moonshine replaces Apple for the streaming slot. |
| A10 | Prototype the provider-menu UI in Settings (read-only for now, shows available engines with install/signup prompts) | 1 day | First UI surface of the flexibility principle. Doesn't need the engines to work yet — shows them and what's required. |

---

## B. Manual — needs you (account, spend, or decision)

| # | Task | What I need from you | Unlocks |
|---|------|----------------------|---------|
| B1 | ~~Top up OpenRouter credit~~ — done (2026-04-19). Benches landed: Gemini 2.5 Pro (6.8 % / best RU at 4.6 %). **Voxtral-via-OpenRouter dropped** — chat-completions routing can't activate Voxtral's transcribe-mode token (see `whisper-bench-2026-04-18.md` § Voxtral routing failure). **Claude Opus 4 parked twice** — no audio-input endpoint on OpenRouter + pricing (~$15/$75 per 1M tokens) is premium-BYOK-only, not a default path. **GPT-Audio dropped** (same pricing argument). | Account action | Gemini 2.5 Pro benched; Voxtral needs a different route (see B9); Opus/GPT-Audio parked. |
| B2 | Create an ElevenLabs API key and store in Keychain as service `com.untype.app`, account `elevenlabs.apiKey` — signup done (2026-04-19), key top-up still pending while API-vs-subscription is decided | Signup + $5–10 credit | Scribe v2 (2.3 % leaderboard WER — current accuracy champion) |
| B3 | ~~Create an OpenAI API key~~ — **deprioritised in favour of OpenRouter**; `openai:<model>` path remains in the harness but unused for now | Signup + credit | `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `whisper-1` (OpenAI path already in the harness) |
| B4 | ~~Create a NVIDIA build.nvidia.com account~~ — **blocked**: phone verification failing, unresolvable today. Park NIM/Parakeet path. | Signup only, free | Parakeet TDT 0.6B v2 — the accuracy leader among open-weights on ASR leaderboard |
| B5 | Optional: Deepgram key for Nova | Signup + credit | Non-Whisper proprietary coverage |
| B6 | Decide whether to add 2–3 more real-speech corpus samples (meeting audio, accented EN, mobile-mic RU) | Product decision | Better bench representativeness before provider picks get serious |
| B7 | Decide default-cloud-provider policy: Groq (cheap, fast) vs Scribe v2 (best accuracy, 3× price) vs "whatever bench says after B1–B5, B9" | Product decision | Drives A7's settings-default |
| B8 | Decide cloud-cost model: free tier subsidised by Untype vs BYOK-only vs hybrid | Product/business decision | Affects onboarding UX in A10 |
| B9 | Create a Mistral API key for `https://api.mistral.ai/v1/audio/transcriptions` (accesses Voxtral via the dedicated transcribe endpoint, not chat-completions). Harness needs a new `mistral:<model>` provider built on Groq's shape but pointed at Mistral's host. Unlocks a valid measurement of `voxtral-mini-transcribe-realtime-2602` — the only Voxtral surface that actually engages transcribe mode. | Signup + a few € credit | Voxtral measured honestly; answers whether Mistral's transcribe tier matches/beats Groq on our corpus |

---

## C. Hardware-blocked — needs Apple Silicon

Can't be done on the dev machine. Defer until there's an M-series machine in the loop (loaner, CI, or future dev-machine upgrade).

| # | Task | Unblocks |
|---|------|----------|
| C1 | Bench WhisperKit (`tiny`, `base`, `large-v3-turbo`, `large-v3`) against the corpus | Apple Silicon local defaults — the biggest gap in the data today |
| C2 | Bench parakeet-mlx 0.6B against the corpus | Best open-weights on-device option for Apple Silicon |
| C3 | Bench Parakeet via CoreML (FluidInference build) | Apple Silicon local option without the MLX dependency |
| C4 | Time-to-first-token measurements for on-device engines on Apple Silicon (not just wall-clock) | Streaming-slot decision on Apple Silicon |
| C5 | Evaluate macOS 26 `SpeechAnalyzer` / `DictationTranscriber` vs `SFSpeechRecognizer` | Streaming-slot default — may obsolete the current Apple streaming path |
| C6 | Validate Untype's existing `WhisperKitService.swift` scaffold actually runs | Turns a scaffolded-but-unvalidated code path into a real engine |

Setup shortcut when the hardware lands: the Python harness at `tools/stt-bench/stt_compare.py` is cross-silicon, so the first pass is "check out the branch, run the harness, file the results under `benchmarks/`". The Swift side (`WhisperKitService.swift`) then needs a single-command validation.

---

## Dependency graph — what unblocks what

```
A1 (fix corpus) ─► A2 (rebench)
                     │
                     ├─► credible "defaults" discussion in A7
                     │
B1 (OpenRouter $) ─► bench Gemini 2.5 Pro ─────────────┐   (Voxtral-via-OR = wrong surface; Opus/GPT-Audio price-parked)
B2 (ElevenLabs)   ─► A3 path useful ──► bench Scribe v2 ├─► B7 (pick defaults) ─► A7 (ship Groq-as-default, revisit)
B9 (Mistral $)    ─► new mistral:* path ──► bench Voxtral│
B4 (NIM free)     ─► A4 path useful ──► bench Parakeet ─┘

A6 (Swift cloud provider) ─► A7 (ship in app)
A8 (whisper.cpp Swift)     ─► offline local path in app

C1–C6 (Apple Silicon)      ─► Apple Silicon defaults for the menu
                                        │
A9 (Moonshine vs Apple)    ─► streaming-slot default
                                        │
                            ─► A10 (provider-menu UI with real data in each slot)
```

---

## Suggested first slice (when you next have 30 minutes)

1. **B1 (OpenRouter top-up).** Single cheapest unlock; gives us four new provider benches for one action.
2. **A1 + A2 in the same session** after B1. Verify the two corpus references, then re-run the full harness with Groq + whisper.cpp + Moonshine + the new OpenRouter-routed models. One evening's work yields the first *trustworthy* provider comparison.
3. After that the important fork is between:
   - **B2 (ElevenLabs signup)** if accuracy matters more than cost.
   - **A7 (wire Groq into the app)** if shipping the first working flexible backend matters more.

The two paths are independent; both are good moves.

---

## Things explicitly NOT on the list

- Rebuilding the CustomLM pipeline (tried in s37 and reverted — phonetic bias doesn't rescue rare vocab).
- Locking in *any* engine as the only option. Everything here feeds the menu.
- Together.ai Whisper hosting (worst-in-class per AA bench).
- whisperai.com (opaque reseller, page failed to load).

---

## How to keep this file useful

- Tick items off in-place by marking them `~~struck through~~` and appending the commit hash that closed them.
- When something blocked-on-key gets unblocked, move it from B to A with a note.
- Rebench after every material engine or corpus change — the harness is stable enough that a rerun is cheap.
