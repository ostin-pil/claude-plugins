# Lean Canvas v1
**Date**: 2026-04-30
**Status**: Synthesis of `knowledge/ux-audit-and-takes-2026-04-30.md` (U1), `knowledge/pivot-ideas-2026-04-30.md` (X5), `knowledge/pivot-build-vs-extend.md` (X1), `knowledge/icp-v1.md` (P3). Treat as a hypothesis to validate, not a finalized strategy.
**Format**: Ash Maurya's 9-block Lean Canvas + 3 falsifiable assumptions with Mom Test probes.

> **⚠ Reconcile note before reading.** This canvas commits to **one specific branch**: bilingual professionals (C2) as primary ICP, derived from the X5 pivot scoring. The Untype product memo (`project_bounce_overview.md`) frames the product more broadly as a **"voice-driven interface layer for digital communication"**, Slack/Telegram/email message layer, where Tier 2 differentiators include "real-time translation," "tone adjustment," and "bilingual output" alongside each other. The memo's framing implicitly favors the C1 power-knowledge-worker primary that this canvas demotes to secondary.
>
> If the founder's intent matches the memo (broad message-layer for any user, with bilingual as one differentiator among several), then this canvas's C2-primary commitment is a **positioning pivot relative to the memo, not an alignment with it**, and a parallel canvas with C1 as primary should be drafted before either is acted on.
>
> Two specific assumptions in this canvas are **unverified by source code**:
> 1. The "L1-to-L2 native-fluent translation" prompt described in §4 may not exist in current `CloudPolishingAdapter`, Untype's polish step is currently English-register-adaptation. Adding true cross-language translation is a prompt-engineering + evaluation task, not a free re-purposing of the existing adapter.
> 2. The "in-language video demos" in §5 presume the founder can produce content in target languages. Memory captures "comfortable on camera/audio," not bilingual proficiency. If the founder is English-monolingual, the channel plan needs revision.
>
> Both belong on the validation list before any code or marketing commits to the C2-primary direction.

---

## One-sentence top-level

> **Untype is a macOS voice-to-text overlay that lets a bilingual professional dictate in their first language, ship the message in English (or vice versa), with native-fluent register, without their audio ever leaving their machine.**

It wins because nobody is doing native-quality L1-to-L2 voice composition (DeepL is text-only; Wispr is monolingual + cloud-audio + trust-broken; Superwhisper is monolingual + power-user-complex; Apple Dictation is monolingual + no polish).

---

## 1. Problem

The top 3 problems Untype solves, in order of pain depth:

1. **L1-to-L2 composition friction.** Bilingual professionals think faster in their first language and write worse in English (or vice versa). They burn a daily tax in three forms: time (Apple Dictation in L1 to DeepL to ChatGPT to manual edit), anxiety (high-stakes communication that "sounds off"), and tool sprawl (3+ apps for one message).
2. **Trust gap with cloud dictation.** Wispr Flow's 2025 screenshot scandal + post-trial reliability collapse + ongoing $15/mo pricing have trained the segment to *distrust* cloud-routed dictation. Privacy-conscious users, especially non-US users with regulatory weight (GDPR, RU DPA, ML data-localization), won't send audio to US servers, and increasingly won't trust what does come back.
3. **No transparency about what got rewritten.** Every dictation tool that polishes silently rewrites things; users learn this when they catch a hallucination, then never trust it again. No competitor surfaces a Cleaned·Original·Source-language toggle as a first-class affordance.

**Existing alternatives:** Apple Dictation (monolingual, 30s session limit, no polish) + DeepL Pro (text only, separate roundtrip) + ChatGPT (manual paste, no privacy) + manual editing. Plus the failed-attempt graveyard: Wispr (privacy-burned), Superwhisper (config maze), MacWhisper (file-only), Aqua Voice (cloud-only, English-bias).

---

## 2. Customer Segments

**Primary:** Bilingual / multilingual professionals, L1-native (Russian, Spanish, Mandarin, Hindi, Arabic, Ukrainian, Portuguese, Vietnamese, Polish) writing in English-dominant tech / business workplaces. (P3 §3.)

**Secondary:** Privacy-pragmatic power knowledge workers, engineers, PMs, consultants who live in Slack/Mail and balked at Wispr's $15/mo or got burned by the trust-gap stories. (P3 §4.)

**Earlyvangelists**, within the primary segment, the highest-value early adopters are:
- Founders / senior ICs at remote-first companies hiring globally (high-stakes communication, daily volume)
- Customer-facing roles writing to L2 customers (sales, support, account managers)
- Bilinguals already paying for DeepL Pro or ChatGPT Plus (price-anchored, tool-promiscuous)

---

## 3. Unique Value Proposition

> **"Speak in your language. Send in theirs."**

High-level message: Untype is the first dictation tool built for people who don't think in English. Speak in the language you reason in; Untype's on-device speech engine captures it; only the *text* gets translated to your target language with a native register; you see and approve every cleaned/translated message before it lands.

**Single subhead for the landing page:** "On-device speech. Cloud translation, never your voice. Native-fluent in the language you're writing to."

---

## 4. Solution

The top 3 features that make the UVP credible:

1. **Translation polish profile with per-app target-language routing.** Polish step isn't tone-adaptation; it's a true L1-to-L2 translation prompt with register awareness ("formal Slack to senior eng," "casual customer email," "Russian-formal patronymic kept in greeting"). Per-app routing extends Untype's existing `AppContext` + `ContextProfile` infrastructure (`Sources/UntypeCore/Processing/AppContext.swift`).
2. **Cleaned · Original · Source-language toggle on every path.** The trust mechanism. Bilinguals are suspicious of translation by experience; *seeing all three forms* (what I said, what was transcribed, what was translated) is the only way to earn trust. Closes U1 issue 1.
3. **On-device STT, text-only cloud routing, no telemetry.** Apple Speech captures audio locally; only the resulting text goes to the cloud LLM for translation. Zero screenshots, zero audio off-device, zero tracking. The architectural answer to the Wispr trust gap.

Out-of-scope for v1 (held for v2): voice corrections (U1 Take C), sidecar dock (U1 Take B), second-brain capture (X5 D2), accessibility / RSI suite (X5 A3).

---

## 5. Channels

Path to customers, ranked by founder-fit (solo, comfortable on camera/audio, no paid sales motion):

1. **In-language video demos.** 90-second product demos in Russian, Spanish, Mandarin (priority based on founder language access). The bilingual segment responds disproportionately to *in-language* content; this is where founder face/voice comfort cashes out. Repost via Twitter/X, in-language YouTube, regional Reddit equivalents (e.g. Habr for Russian, Genbeta for Spanish).
2. **Diaspora podcasts / newsletters.** Bilingual tech newsletters (Indian-startup ecosystem, Latam tech, Russian/Ukrainian tech-on-Substack). Pitch as a guest, demo live.
3. **Show HN as a secondary channel.** Frame: "I built a dictation tool for non-native English speakers." Don't lead with multilingual story, lead with the trust angle ("I built the dictation tool I wanted after Wispr Flow burned me") to capture the C1 secondary segment.
4. **Listen-first community channels.** /r/macapps, /r/MacApps, /r/macOS, /r/AskRussian, /r/Spanish, /r/India tech threads. Post when on-topic; don't cold-launch.
5. **Targeted referral within target segments.** Bilingual tech communities are tight; one happy power user = 5 referrals. Build a simple referral mechanic (e.g. extended trial for both sides).

What we're *not* doing in v1: paid ads (no budget), enterprise sales (wrong segment), App Store ASO (technical constraints + 30% cut).

---

## 6. Revenue Streams

Pricing structure that respects the X1 build-vs-extend Shape 1 cost basis and the BYOK fallback option:

| Tier | Price | What it includes | Target segment |
|---|---|---|---|
| **Free** | $0 | Apple Speech STT only, no polish | Trial / hesitation-killer |
| **Pro** | **$7/mo** or **$79 lifetime** | Cloud LLM polish (managed key), multi-language, intent profiles, all UX | Primary ICP (C2 bilinguals + C1 secondary) |
| **BYOK** | **$29 lifetime** | Same UX + features, user supplies their own OpenAI/Anthropic/Groq/Ollama keys | Power-user / privacy-maximal slice |
| **Future: Pro Multi-seat** | TBD | Team admin, shared dictionary, per-seat billing | Held for traction (12+ months out) |

**Pricing rationale** (from `competitive-landscape.md` 6.5 + `user-pain-points-and-desires-2026.md` 4.4):
- $7/mo lands clearly below Wispr Flow's $15/mo (the segment's price ceiling) and Superwhisper's $8.49/mo
- $79 lifetime undercuts Voibe's $99 lifetime and Superwhisper's $249 lifetime (the upper churn-driving anchor)
- $29 BYOK matches Sotto's lifetime tier and gives a low-friction entry for the technical privacy-max slice

**Validated pricing risks:** if conversion is low at $7/mo, BYOK becomes the primary monetization story. The X1 doc's flip-to-Shape-4 trigger applies.

---

## 7. Cost Structure

Solo-dev project. Costs ranked by burn risk:

1. **Founder time** (largest, opportunity-cost-priced): coding, support, marketing, all founder-led.
2. **Cloud LLM inference** (variable, paid users only): managed-key tier eats per-dictation cost. Estimate: 100 polishes/user/day × 500 input + 200 output tokens × $3/MTok input + $15/MTok output = ~$0.0036/day/user × 30 = ~$0.11/user/month at GPT-4-class. Comfortable margin at $7/mo. Higher-volume users are still profitable; very-high-volume users (>1000/day) need a fair-use cap or higher tier.
3. **Apple Developer Program**: $99/yr (already an assumed cost).
4. **Code signing** (one-time / minimal): self-signed `Untype Dev` cert for local builds (free); paid Developer ID for distribution ($0 incremental, included in Apple Developer Program).
5. **Hosting**: minimal, landing page (Cloudflare Pages, $0), license server if needed (Cloudflare Workers, ~$5/mo at small scale), Plausible analytics ($9/mo).
6. **Marketing / production**: video editing tools (Final Cut, $300 one-time), microphone (already owned), no paid acquisition.

**Annual operating cost at 100 paid users:** $99 (Apple) + $108 (Plausible) + $11 × 100 × 12 ≈ $13K cloud LLM + ~$60 hosting = ~$13.4K/yr. Revenue at 100 paid users ≈ $8.4K/yr Pro + lifetime tier. Need ~150 paid users to break even on direct opex; founder time is the real cost.

---

## 8. Key Metrics

The 3–5 numbers that matter for v1, ordered by what they prove:

1. **Conversion: Free to Pro.** Target: 3-5% within 14 days. Below this triggers the X1 flip to BYOK-only-relay positioning.
2. **L2 acceptance rate.** % of dictations Inserted (not Cancelled or edited heavily before insert). Target: ≥80% for primary ICP. Below this means the translation quality isn't there and the UVP collapses.
3. **Dictations per active user per day (DAU intensity).** Target: ≥10. Below this means the daily-pain claim is wrong and the segment is occasional users, not professionals.
4. **L1 capture distribution.** Which source languages users actually choose. Tells us where to invest STT and polish-prompt tuning. Surprises here are *signals*, if ≥30% of users pick a language we hadn't optimized for, that's a roadmap input.
5. **Trust-toggle engagement.** % of users who flip Cleaned·Original·Source at least once in their first 5 dictations. Target: ≥40%. If high, the trust mechanism is working; if low, users either trust by default (good) or aren't aware (bad, probably bad).

Telemetry stance: minimal, opt-in, no audio, no transcripts. Counts and durations only. Ship the privacy story, don't break it.

---

## 9. Unfair Advantage

What can't be copied or bought in 6 months:

1. **Native Swift architecture with the cleanest provider/polish abstraction in the OSS+commercial set.** Per `oss-competitor-landscape-2026.md` §3.2: Untype's `STTStage` + `PolishingStage` + provider-descriptor separation is uncontested. Migrating to it from VoiceInk/FluidVoice's coupled designs is a multi-month rebuild.
2. **The polish-with-intent + Cleaned·Original transparency mechanism.** Wispr can't bolt on a Cleaned·Original toggle without first admitting their auto-polish loses information; doing so contradicts their messaging. Superwhisper's "modes" are scope-disjoint, not depth-equivalent. This is a single-feature moat.
3. **Founder bilingual + face/voice comfort.** A solo founder who can produce in-language content for 2+ target languages competes for distribution where US-default tools can't follow. Wispr's $80M+ raise can buy English content; it can't buy authentic Russian/Spanish/Mandarin demos at solo-founder velocity.
4. **No telemetry / no screenshots / on-device STT, by architectural choice, not policy.** This isn't a privacy-policy promise; it's that the code never sends those things. Wispr's screenshot scandal showed the difference. Architectural choices are forkable but not refactorable on shipped products without rewriting them.

What's *not* an unfair advantage (so we don't fool ourselves):
- "Native macOS app" alone, every OSS competitor is also Swift-native.
- "On-device STT" alone, Superwhisper, VoiceInk, FluidVoice all have it.
- "Privacy-respecting" alone, every competitor *says* this; the architecture has to *prove* it.
- "$7/mo" alone, Voibe is $4.90/mo. Pricing is a tactic, not an advantage.

---

## 10. Three falsifiable assumptions to validate next

These are the hypotheses this Lean Canvas is *built on*. If any breaks, the canvas changes.

### Assumption 1: Bilingual professionals will pay $7-9/mo to replace their L1-to-L2 multi-tool workflow

**Why this matters:** if false, Pro pricing collapses, the BYOK lifetime tier becomes the primary, and the addressable market shrinks ~3-5×.

**Mom Test probe (no leading questions):**
> "Walk me through the last time you had to write an important Slack message or email at work in English. What did you actually do, what tools did you open, in what order, how long did it take?"

*Listening for:* number of tools used (we expect 2+ for the ICP), where the time goes (we expect editing > composition), what the failure modes feel like (anxiety, fear of sending wrong tone). If the user describes a single-tool workflow ("I just dictate in Apple Dictation and clean it up"), the L1-to-L2 friction may be smaller than we think, and C1, not C2, is the right primary.

### Assumption 2: Apple Speech STT quality is good enough for L1 capture in our top languages (RU, ZH, ES)

**Why this matters:** Untype's privacy story rests on on-device STT. If Apple Speech is unusable in a target language, the architecture has to fall back to Whisper/Parakeet (still on-device, but adds bundle size + Apple Silicon dependency) or to a cloud STT provider (breaks the privacy story).

**Validation probe (not a Mom Test question, a fixture test):**
- Record 30s reference utterances in each target language.
- Run through Apple Speech (`Sources/UntypeCore/Transcription/AppleSpeechService.swift`) and a Whisper-large baseline.
- Compare WER. If Apple Speech WER is >15% higher than Whisper for any of the top-3 languages, the architecture choice needs adjustment.

This is a *test you can run today* without users; it costs ~2 hours and de-risks the entire L1 capture story.

### Assumption 3: The Cleaned · Original · Source-language toggle converts privacy-skeptics into trustful users

**Why this matters:** if users don't *use* the toggle (or if seeing the original *reduces* trust because the polish becomes "obviously rewritten"), the trust mechanism is wrong, and the architectural choice to expose it on every path was wasted.

**Mom Test probe:**
> "Have you ever sent something at work that came out wrong because the translation tool got it wrong? What happened?"
*Then later in the session:* "If I told you that this tool always shows you the original version of what you said before insert, does that change how you'd use it? How?"

*Listening for:* concrete past incidents (proves the pain is real, not imagined), whether trust is *earned* by visibility or *demanded* by control (the difference matters: visibility is cheap, control is expensive). If users say "I'd just trust it once it works," the toggle becomes a power-user feature, not a primary mechanism, and the marketing message has to adjust.

---

## 11. What v1 doesn't promise

To keep scope honest:

- **Not** voice corrections / voice editing / voice navigation (held for X5 A3 v2).
- **Not** sidecar dock / history pane / dictation-as-medium UX (held for X5 A1 v2).
- **Not** cross-platform iOS / Windows / Android (per X1 anti-pivot AP1).
- **Not** enterprise / SOC2 / HIPAA (per X1 anti-pivot AP2).
- **Not** meeting transcription (per X1 anti-pivot AP3).
- **Not** unlimited custom polish prompts (per X1 anti-pivot AP4 + the Superwhisper churn cautionary tale).

If any of these get pulled into v1 by feature pressure, re-read X1 and X5 first. Most are intentional non-goals.

---

## 12. Hooks back to other docs

- **U1 (UX audit)**: issue 1 (Cleaned·Original on every path) is *blocking* for Solution feature 2. Issue 4 (post-insert undo) is high-value adjacent. Issue 3 (anchor teleport) is a polish item.
- **X5 (pivot ideas)**: this canvas commits to A2 (multilingual). Holds A3 (accessibility) and A1 (long-form) as v2. Disqualifies the others.
- **X1 (build-vs-extend)**: Shape 1 (standalone) is the right cost basis. Shape 4 (BYOK-only) is the cost-collapse fallback if Assumption 1 fails. Apple Foundation Models polish adapter is *still* mandatory for macOS 26 defense.
- **P3 (ICP)**: this canvas is the synthesis. P3 is the upstream specification.
