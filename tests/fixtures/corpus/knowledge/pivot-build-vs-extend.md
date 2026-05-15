# Pivot: Build vs Extend
**Date**: 2026-04-30
**Status**: Decision-grade brainstorm, recommends a default and names the conditions that flip it.
**Sources**: `research/oss-competitor-landscape-2026.md`, `research/competitive-landscape.md`, `research/distribution-monetization.md`, Untype's own architecture (`Sources/UntypeCore/Processing/`, `Sources/UntypeCore/Transcription/`, `Untype/App/AppRouterBuilder.swift`).

---

## 0. The question

Untype is currently **Shape 1: Standalone**, original code, native Swift, BYOK + cloud APIs, own STT (Apple Speech / Groq / RemoteWhisper) + own polish (cloud / Ollama). That's a real product, but it's also a 12-month + ongoing engineering investment for a solo developer.

Three plausible alternative shapes:
- **Shape 2: Apple-Speech-thin-wrapper**, bet entirely on Apple's macOS 26 stack (`SpeechAnalyzer` + Apple Foundation Models). Minimum surface area, maximum platform lock-in.
- **Shape 3: OSS-orchestrator**, fork or wrap an existing OSS macOS dictation app and layer Untype's polish / intent / UX on top. Inherit infrastructure, contribute the differentiation.
- **Shape 4: BYOK-only-relay**, ship a thin client that does *no* STT or LLM itself. Pure UX + routing layer. User configures their own providers (OpenAI / Anthropic / Groq / local Ollama). Untype earns on the experience, not the inference.

The question this doc answers: **which shape should Untype occupy in the next 6–12 months, and what would flip the decision?**

---

## 1. Scoring the four shapes

Score 1 (low) – 5 (high). Total is unweighted sum (40 max).

| Shape | Differentiation | Build cost | Vendor lock-in *(higher = better)* | Apple attack surface *(higher = better)* | Velocity (solo dev) | Distribution friction *(higher = lower friction)* | License clarity | Roadmap optionality | **Total** |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **1. Standalone (today)** | 4 | 3 | 5 | 3 | 3 | 3 | 5 | 5 | **31** |
| 2. Apple-Speech-thin-wrapper | 1 | 5 | 1 | 1 | 5 | 2 | 5 | 1 | 21 |
| 3. OSS-orchestrator (fork pindrop / wrap VoiceInk) | 2 | 4 | 2 | 3 | 4 | 3 | 2 | 3 | 23 |
| 4. BYOK-only-relay | 3 | 5 | 4 | 3 | 4 | 2 | 5 | 4 | 30 |

Standalone wins on the unweighted score, with BYOK-only-relay a close second. Apple-thin-wrapper and OSS-orchestrator both have structural ceilings.

---

## 2. Per-shape analysis

### Shape 1: Standalone (current)

**The bet:** Untype builds and owns its STT registry + polish registry + UX, with BYOK providers and on-device-friendly defaults. The architecture (per `oss-competitor-landscape-2026.md` §3) is *the cleanest* in the surveyed set, `STTStage` + `PolishingStage` + provider descriptors give you swap-out provider freedom that VoiceInk and FluidVoice don't have.

**What this protects:** total ownership of the user experience and the data path. No upstream maintainer can ship a regression that breaks Untype. No platform vendor can deprecate the only API you depend on. Pricing is yours to set. Brand is yours to build.

**What this costs:** a year of foundation work that's mostly already done (the `UntypeCore` Swift package is the moat). Ongoing maintenance of the provider adapters as APIs drift. Solo-dev velocity is rate-limited by everything you choose to own.

**What kills this shape:** Apple Foundation Models on macOS 26+ ships polish quality close enough to cloud LLMs that BYOK becomes a power-user-only differentiator, and Apple Speech ships per-app context awareness that obsoletes Untype's intent-driven polish. *That's a real risk*, see swift-scribe (285⭐, MIT) which is already betting that direction. But macOS 26 adoption will lag behind macOS 14/15 for 12+ months, so the standalone shape buys a runway.

### Shape 2: Apple-Speech-thin-wrapper

**The bet:** macOS 26 is good enough to do everything Untype currently does, `SpeechAnalyzer` for STT, Apple Foundation Models for polish, native AX for insertion. Untype becomes a 15-Swift-file UX-layer-on-top, like swift-scribe's positioning.

**What this protects:** velocity. The Apple stack does the hard work. Untype only owns the UX shell.

**What this costs:** existential platform dependency. Every Apple decision (model quality, latency, deprecation, pricing if Apple ever monetizes) is your decision. The product is *unbundleable*, Apple ships a "Dictation 2.0" that does Untype's job and you have no path to differentiate.

**What's already happening here:** swift-scribe occupies this niche; Apple Notes already includes dictation; the speech-stack on macOS 26 is genuinely strong. The competitive map says: this is *a real product shape*, but it's also a commodity shape. It only wins on price (free) or on a UX moat that any Apple-native competitor can replicate.

**Distribution friction:** macOS 26 only is a hard adoption cap. As of April 2026, macOS 26 base install is non-trivial but shrinks the addressable market significantly versus macOS 14+.

**Verdict:** wrong shape for Untype as a paid product. Right shape for an open-source reference / "macOS dictation done minimally" demo. swift-scribe is already doing this.

### Shape 3: OSS-orchestrator (fork pindrop or wrap VoiceInk)

**The bet:** the dictation-engine layer is commodity. Fork an OSS app for the engine + UI scaffolding, contribute Untype's polish-with-intent and UX innovations on top.

**Candidate forks, in order of legal cleanliness for commercial use:**
1. **pindrop (469⭐, MIT)**, closest tagline match to Untype ("native macOS menu bar dictation … local STT with WhisperKit"), uses the same `argmax-oss-swift` dependency Untype already has, has the cleanest test architecture in the OSS set. *Forkable for commercial use.*
2. **VoiceInk (4,681⭐, NOASSERTION)**, biggest audience but the license is NOASSERTION, which is legally murky for commercial relicensing. *Not safely forkable.*
3. **FluidVoice (1,984⭐, GPL-3.0)**, strong tests, multi-engine, but GPL-3.0 means a fork must remain GPL, kills any proprietary-product path. *Not commercializable as a fork.*
4. **macparakeet (119⭐, NOASSERTION)**, best test coverage, Parakeet-only. License unclear. *Not safely forkable.*

**Realistic version of this shape:** fork pindrop, port Untype's `UntypeCore` Swift package (STT registry, polish registry, intent profiles) on top, replace pindrop's UI with Untype's overlay / review toast / context chip. Ship as a re-branded product.

**What this protects:** velocity *if* the fork's architecture aligns with Untype's. pindrop's protocol-first design and its WhisperKit dep make this less crazy than it sounds.

**What this costs:** every upstream pindrop release is a rebase decision. The differentiation is *only* what Untype adds on top, the polish layer, the review affordances, the intent profiles. Audience inheritance is partial: pindrop's 469⭐ users don't automatically become Untype's customers, especially after a rebrand.

**The deeper problem:** Untype already has the cleaner architecture (per `oss-competitor-landscape-2026.md` §3.2). Forking pindrop and porting Untype's core *to* pindrop's structure is harder than adding pindrop's missing pieces *to* Untype. The fork path optimizes for "saved building," but Untype already built it.

**Verdict:** wrong shape now, but a small adjacent move is right: **read** pindrop's source, **steal** the patterns that work (xctestplan gating, Swift Testing migration, mention-formatter, history store), but don't fork. Untype gets the value of pindrop's choices without the ongoing rebase tax.

### Shape 4: BYOK-only-relay

**The bet:** Untype ships *no inference*, no bundled models, no cloud-account broker, no managed keys. The user configures their own STT provider (Apple Speech locally, or BYOK Groq / OpenAI / Deepgram / Whisper-local) and their own LLM (BYOK OpenAI / Anthropic / Ollama). Untype earns on the UX layer: the overlay, the review toast, the intent profiles, the alternates editor, the polished glue.

**What this protects:** zero LLM ops, zero STT model maintenance, zero per-user inference cost. The product is *a relay with great taste*. Pricing can be lower because there's no variable cost per dictation. Privacy story is bullet-proof: every byte that leaves the user's machine goes to a provider they configured.

**What this costs:** harder marketing to non-technical users (they have to set up keys). Smaller addressable market: power users + privacy-conscious + technical. The category is also occupied, Spokenly is BYOK-positioned, VoiceInk lets users supply keys.

**What's interesting:** BYOK-only-relay maps cleanly onto Untype's existing `ProviderRegistry` + `STTRegistry` architecture. The pivot from Shape 1 to Shape 4 is *not* an architectural rewrite; it's a *positioning + monetization* shift. Drop the "we'll provide the API" story, double down on "you bring the keys, we provide the experience." The codebase doesn't need to change much; the marketing site does.

**Distribution friction:** BYOK is a hard sell on the App Store (App Review 5.1.2(i) AI-disclosure rules per `distribution-monetization.md`); easier on Developer ID + direct download.

**Verdict:** worth holding as a *fallback monetization shape*. If subscription pricing for managed keys proves tough to sell (because Wispr/Superwhisper have already trained the market on it), Untype can flip to BYOK-relay positioning without rebuilding the product.

---

## 3. Recommendation

**Stay in Shape 1 (Standalone), with three explicit guardrails.**

1. **Ship the Apple Foundation Models polish adapter on macOS 26.** The single biggest existential risk is Apple's stack catching up on the polish quality axis. Defending requires being *the better Apple-FM client* on macOS 26, not pretending Apple FM doesn't exist. Slot into existing `PolishingRegistry`, it's additive, not architectural.

2. **Don't fork OSS, but read it.** pindrop's test architecture and macparakeet's pure-state-machine pattern are worth porting (per `oss-competitor-landscape-2026.md` §3.2). The fork path costs more than it saves given Untype's architecture is already cleaner.

3. **Hold BYOK-relay (Shape 4) as a price-positioning option, not a product pivot.** The `ProviderRegistry` already supports it. If managed-key subscription pricing fails (signal: <30% conversion from trial), flip the marketing message to "BYOK-only, $29 lifetime" without rebuilding the product.

This is wrong if any of the trigger conditions in §4 fire.

---

## 4. Trigger conditions that flip the decision

These are the "I would change my mind if…" lines for each shape.

### Flip to Shape 2 (Apple-thin-wrapper) if:
- **Apple Notes / Apple Intelligence ships per-app context-aware dictation in macOS 26.x or 27** with quality matching cloud LLM polish *AND* macOS 26 base install crosses ~50%. At that point the standalone shape's polish layer is undifferentiated and the macOS 26-only constraint stops being a market-cap. Untype becomes "Apple Speech 2.0 with better UX," sells on UX, not on inference.
- **Solo-dev burnout signal:** if maintaining the cloud-provider adapters consumes >40% of dev time for 3+ months running with no architectural payoff.

### Flip to Shape 3 (OSS-orchestrator, pindrop fork) if:
- **A new STT modality (Parakeet-realtime, Voxtral-stream, Apple-26-streaming) emerges that Untype can't reasonably integrate alone in <2 weeks.** pindrop ships it first, pindrop's MIT license lets us fork, the rebase tax is one-time. (As of April 2026, no signal this is imminent.)
- **A Untype v2 audience-pivot (per X5: A1 long-form writers or D2 second-brain) makes pindrop's history-store / mention-formatter / dictionary-learning the right scaffolding.** In that case, fork pindrop, port UntypeCore on top, and accept the rebase tax for the audience-fit gain.

### Flip to Shape 4 (BYOK-relay) if:
- **Subscription monetization proves intractable.** Signal: 6 months post-launch, paid conversion <2% with no clear path to improvement. BYOK-relay's lower per-user economics + smaller addressable market + technical-user audience is a smaller business but a defensible one.
- **A managed-key compliance event** (a customer's API key leaks via Untype, or Apple App Review rejects the managed-key model under 5.1.2(i)) makes managed-key untenable. Flip immediately.

### Stay in Shape 1 if:
- macOS 26 dictation + Apple FM remain materially behind cloud-LLM polish on quality (current state)
- pindrop / VoiceInk / FluidVoice continue to lag Untype on UX architecture (current state)
- BYOK-relay is *optional* for users, not the default (current state)

---

## 5. Open questions for ICP work (P3)

The shape decision is **not independent** of the ICP decision. Re-read this with P3 in hand:

- *If P3 picks bilingual professionals (X5 A2):* Shape 1 stands; the multilingual story leans on cloud LLM polish quality, which Apple FM lags by 18+ months. Confidence in standalone increases.
- *If P3 picks RSI / accessibility (X5 A3):* Shape 1 still wins, but Shape 4 (BYOK) gains attractiveness, accessibility users have specific provider preferences (some require on-device-only by policy/insurance). Building both options matters.
- *If P3 picks long-form writers (X5 A1):* Shape 3 (fork pindrop for the history infrastructure) becomes worth re-evaluating, long-form writing puts a much heavier load on history/dictionary/draft-graveyard features that Untype hasn't built.
- *If P3 picks second-brain capture (X5 D2):* Shape 1 + heavy investment in adapter integrations (Notion, Obsidian, Apple Notes). Shape 3 weakens because pindrop isn't this; Shape 4 strengthens because second-brain users are technical and BYOK-friendly.

The X1 recommendation (stay in Shape 1) holds across all P3 outcomes. What changes is *what to invest in within Shape 1*.

---

## 6. What I'm not recommending and why

- **A wholesale rewrite onto Apple FM only.** That's Shape 2; analyzed above; the platform-lock-in cost is too high.
- **A formal partnership / contribution back to pindrop.** Tempting (collaboration over competition) but the audiences barely overlap and pindrop doesn't have the polish/intent abstraction Untype needs. Send a star and steal the patterns.
- **Open-sourcing Untype.** Different question. The brief addresses build-vs-extend, not OSS-vs-proprietary. Holding for a separate decision tied to the monetization model.

---

## 7. Hooks for downstream docs

- *For P3 (ICP):* §5 above lists the conditional read, re-read with P3's pick in mind.
- *For P1 (Lean Canvas):* the "Unfair Advantage" block should reflect Shape 1's ownership of the full stack. The "Cost Structure" block should account for cloud LLM costs (managed-key) or zero variable cost (BYOK). Both options should be priced.
- *For X5 (pivot ideas):* the audience pivots A2/A3/D2 all live in Shape 1. The shape decision doesn't constrain the audience decision.
