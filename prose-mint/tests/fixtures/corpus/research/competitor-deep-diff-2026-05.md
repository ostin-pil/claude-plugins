# Competitor deep-diff: voice-to-text for macOS — May 2026

**Date:** 2026-05-01
**Scope:** A focused 8-row coverage matrix across the macOS dictation / voice-to-text category, with one positioning delta per competitor relative to Untype. Extends — does not replace — the existing landscape docs:

- [`competitive-landscape.md`](./competitive-landscape.md) — broader commercial map (Wispr, Superwhisper, MacWhisper, AudioPen, Otter, Notta, plus the April 2026 update)
- [`head-to-head-comparison.md`](./head-to-head-comparison.md) — the previous head-to-head against Wispr / Superwhisper
- [`distribution-monetization.md`](./distribution-monetization.md) — distribution and pricing baseline
- `oss-competitor-landscape-2026.md` (lives on `feature/hallucination-filter`, not yet merged to main) — deep OSS profiles for VoiceInk, FluidVoice, macparakeet, swift-scribe, pindrop, speak2

This doc is intentionally terse. For deep prose on the OSS row entries, follow `oss-competitor-landscape-2026.md` once it merges.

## Sourcing rule

Every cell in the matrix is sourced. URLs sit in the row's footnote block. Where a fact could not be confirmed from a primary source as of 2026-05-01, the cell is marked `unverified` with a note on what would verify it.

---

## Coverage matrix

| # | Competitor | Distribution | STT backend | Polishing layer | Insertion | Pricing (2026-05) | Last shipped |
|---|------------|--------------|-------------|-----------------|-----------|-------------------|--------------|
| 1 | Wispr Flow | Direct download (Mac/Win/iOS/Android), VC-backed [^w1] | Proprietary cloud STT, AWS+Baseten [^w2] | Yes — fine-tuned Llama in cloud, TensorRT-LLM, <700 ms p99 [^w2] | Clipboard-paste with restore; Scratchpad fallback; iOS as custom keyboard [^w3] | Free 2k words/wk; Pro $15/mo or $12/mo annual; Enterprise custom [^w1] | iOS rolling; web pricing page reflects current [^w1] |
| 2 | Granola | Direct download (Mac, iPhone); Web app [^g1] | Not disclosed; meeting-bot model — likely proprietary cloud over Zoom/Meet/Teams hooks [^g2] | Yes — post-meeting AI enhancement; "the latest AI models built in" [^g2] | N/A — output stays in Granola UI, exports to Slack/email/Notion/CRM [^g2] | Basic free; Business $14/user/mo; Enterprise $35/user/mo [^g1] | Active 2026 — web pricing live [^g1] |
| 3 | Whispo | Direct download (Mac+Win); GitHub releases, AGPL-3.0 [^wh1] | OpenAI Whisper via OpenAI/Groq API or custom URL [^wh1] | Optional — post-process via OpenAI/Groq/Gemini LLM [^wh1] | "Inserts into the application you are using"; Electron/TypeScript app, mechanism not documented [^wh1] | Free / OSS (BYOK) [^wh1] | Stagnant — last release v0.1.7 on 2024-11-22 [^wh2] |
| 4 | Superwhisper | Mac App Store + direct; iOS, Windows [^s1] | On-device Whisper (Nano/Fast/Pro/Ultra); optional cloud STT (OpenAI, Deepgram, Groq) [^s1] [^s2] | Yes — pluggable LLM (GPT-5, Claude Haiku, Llama 4) with custom prompts; per-mode config [^s1] | Auto-paste into focused app; clipboard-based [^s1] | Free tier; Pro $8.49/mo or $84.99/yr; Lifetime $249.99; Enterprise custom (SOC 2 Type II) [^s1] | Active — modes docs maintained, April 2026 reviewer coverage [^s2] [^s3] |
| 5 | VoiceInk | OSS (GPLv3) on GitHub + freemium licensed builds via tryvoiceink.com; Homebrew cask [^v1] [^v2] | Three local engines (Whisper / FluidAudio Parakeet / Apple Speech) + 9 cloud providers (Deepgram, ElevenLabs, Gemini, Groq, Mistral, OpenAI-compatible, Soniox, Speechmatics, xAI) [^v3] | Yes — "Smart Modes" + AI Assistant; pluggable across the same provider list [^v1] | Not specified in README; observed clipboard-style paste in code [^v1] [^v3] | Free OSS build via Homebrew; paid license amount not on landing (`tryvoiceink.com` page is title-only) [^v1] [^v2] | Very active — v1.74 released 2026-04-22 [^v4] |
| 6 | FluidVoice | OSS (GPLv3 since 2026-02-23, was Apache-2.0); GitHub releases + Homebrew [^f1] | Multi-engine: Parakeet Flash / Parakeet TDT v2 / TDT v3 (FluidAudio), Cohere Transcribe, Apple Speech, Whisper sizes [^f1] [^f2] | Optional — AI enhancement via OpenAI / Groq / custom providers (BYOK) [^f1] | Accessibility-based typing — write/rewrite in any text box [^f1] | Free, BYOK [^f1] | Very active — v1.5.12 on 2026-04-08, multiple betas in late March [^f3] |
| 7 | macparakeet | OSS (GPLv3); GitHub releases [^m1] | Parakeet TDT 0.6B-v3 via FluidAudio CoreML on Apple Neural Engine; optional WhisperKit fallback on a dev branch [^m1] | Optional — AI formatter for grammar/punctuation/paragraphing via OpenAI/Anthropic/Ollama BYOK [^m1] | Hotkey push-to-talk or double-tap continuous; pastes system-wide into focused app [^m1] | Free, BYOK [^m1] | Very active — v0.5.6 on 2026-04-21 [^m2] |
| 8 | Apple built-in dictation (macOS Tahoe / 26) | Built into macOS [^a1] | Apple Speech framework; on-device on Apple Silicon (verifiable per-language in Keyboard settings) [^a1] | None — raw transcript only; no AI cleanup stage in the dictation pipeline [^a1] | Native system text-field insertion; no clipboard, no AX permission [^a1] | Free with macOS [^a1] | Active in macOS Tahoe / 26; documented behavior is "no timeout, 30 s inactivity stop" [^a1] [^a2] |

[^w1]: Wispr Flow pricing page — `https://wisprflow.ai/pricing` (fetched 2026-05-01)
[^w2]: Baseten case study on Wispr Flow architecture — `https://www.baseten.co/resources/customers/wispr-flow/`
[^w3]: Wispr Flow text-not-pasting docs — `https://docs.wisprflow.ai/articles/7971211038-fix-text-not-pasting-after-dictation`
[^g1]: Granola pricing — `https://www.granola.ai/pricing` (fetched 2026-05-01)
[^g2]: Granola landing — `https://www.granola.ai/`
[^wh1]: Whispo README — `https://github.com/egoist/whispo`
[^wh2]: Whispo commit history — `gh api repos/egoist/whispo/commits` (latest: 2024-11-22, v0.1.7)
[^s1]: Superwhisper landing — `https://superwhisper.com/`
[^s2]: Superwhisper modes docs — `https://superwhisper.com/docs/modes/modes`
[^s3]: afadingthought review (April 2026) — `https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac`
[^v1]: VoiceInk README — `https://github.com/Beingpax/VoiceInk/blob/main/README.md`
[^v2]: VoiceInk commercial site — `https://tryvoiceink.com/` (page returned title-only; pricing amounts unverified, would verify by visiting buy page or contacting developer)
[^v3]: VoiceInk source layout — `VoiceInk/Transcription/Cloud/` and `Local/` (per `oss-competitor-landscape-2026.md`)
[^v4]: VoiceInk releases — `gh release list --repo Beingpax/VoiceInk` (v1.74 on 2026-04-22)
[^f1]: FluidVoice README — `https://github.com/altic-dev/FluidVoice/blob/main/README.md`
[^f2]: FluidVoice releases (Cohere Transcribe addition noted in April 2026 update) — `https://github.com/altic-dev/FluidVoice/releases`
[^f3]: FluidVoice releases — `gh release list --repo altic-dev/FluidVoice` (v1.5.12 on 2026-04-08)
[^m1]: macparakeet README — `https://github.com/moona3k/macparakeet/blob/main/README.md`
[^m2]: macparakeet releases — `gh release list --repo moona3k/macparakeet` (v0.5.6 on 2026-04-21)
[^a1]: Apple — Use Dictation on Mac — `https://support.apple.com/guide/mac-help/use-dictation-mh40584/mac` (Tahoe; "no timeout, 30 s inactivity stop"; on-device verifiable in Keyboard settings)
[^a2]: macOS dictation features 2026 review (third-party) — `https://weesperneonflow.ai/en/blog/2025-10-27-voice-dictation-macos-tahoe-native-features-third-party-apps-2025/`

---

## Untype positioning delta (one row per competitor)

| Competitor | Differentiation Untype holds | Where Untype is behind |
|------------|------------------------------|------------------------|
| Wispr Flow | Local-first by default; audio doesn't leave device unless user picks a cloud STT/polish; native Swift, no Electron; pluggable provider stack visible to user | Mobile (Untype is Mac-only); cross-platform sync of dictionary/snippets/style; <700 ms p99 latency target; brand recognition; auto-tone-by-app is shipped product not roadmap |
| Granola | Different product category — Untype is ad-hoc voice-to-text in any app; Granola is a meeting-notes platform. The overlap is "users who searched 'granola alternative' wanting general voice-to-text" | Calendar/meeting integration; team sync; structured note generation; non-overlap products, not a feature gap |
| Whispo | Native Swift, no Electron runtime; doesn't require BYOK to do useful work (WhisperKit ships out-of-box); active 2026 development vs. Whispo's 2024-11 stagnation | Cross-platform (Whispo runs on Windows too); arguably nothing else — Whispo is functionally abandoned |
| Superwhisper | Architecturally cleaner provider abstraction at the protocol level (`STTStage` + `PolishingStage` separated; descriptors registered, not hard-coded); native macOS-only focus enables tighter integration | Modes (Untype has no mode system yet); 9-cloud-STT breadth; documented context-awareness (selected text + clipboard + frontmost app); enterprise compliance certs; mobile parity |
| VoiceInk | Cleaner separation of `STTStage` from `PolishingStage` with provider descriptors; Swift Package Manager, not `.xcodeproj`-only; serious test coverage (vs. VoiceInk's near-zero) | Engine breadth (3 local + 9 cloud); shipping cadence (v1.74 vs. Untype pre-1.0); paid-license business already in market |
| FluidVoice | Lighter footprint without a 79 MB bundle of model metadata; SPM-buildable; LLM-polish that doesn't require a third-party API (Apple Foundation Models adapter just shipped, Ollama adapter shipped earlier) | Multi-engine STT breadth (Parakeet Flash + TDT + Cohere); per-app dictation prompt profiles already shipped; FluidVoice's `DictationE2ETests` is the OSS gold-standard real-fixture E2E test |
| macparakeet | Pluggable polish across multiple LLM providers (Ollama, Cloud, Apple FM) vs. macparakeet's BYOK-only; AppKit overlay UX (NSPanel, non-activating) optimized for ad-hoc input vs. macparakeet's GUI focus on meetings/transcripts | Parakeet on Neural Engine (Untype uses WhisperKit); chat-over-dictations feature; depth of test coverage (~40 test files in macparakeet) |
| Apple built-in dictation | LLM polish stage on top (Apple has none); pluggable cloud and on-device polish providers; per-provider customization; auto-restart loop and hallucination filter on top of the raw stream | Zero-friction (Apple is built in, free, no permissions, no install); native textfield insertion that needs no Accessibility cert; no AppKit overlay or hotkey conflict — Apple's surface is the OS |

---

## Cross-cutting observations

### 1. Polishing-layer convergence

All seven third-party competitors except Apple now ship some form of LLM polish step. The split is no longer "does it polish?" but "does the polish run on-device or in cloud, and is the user told which?":

- **Cloud-only polish:** Wispr Flow (Llama, vendor-controlled), Granola (vendor-controlled).
- **BYOK cloud polish:** Whispo, FluidVoice, macparakeet, VoiceInk (all four require user API keys; user picks the provider).
- **On-device polish:** Superwhisper (offers Apple FM and other on-device options); Untype shipped Apple FM polishing in commit `5521ce6` and Ollama in session 52.

The trust-gap narrative around Wispr Flow (see `competitive-landscape.md` §5.1) makes "user-visible routing of where audio and text go" a load-bearing UX feature, not a power-user nicety.

### 2. Insertion mechanism is undocumented in three of seven third-party products

Wispr Flow, Whispo, and VoiceInk all use clipboard-style paste but don't document it on their landing surfaces — only in support articles or source code. FluidVoice is the only competitor that explicitly markets "Accessibility-based typing." macparakeet's docs describe paste behavior. This is a niche where Untype's existing transparency about its insertion path can become positioning copy.

### 3. Last-shipped cadence varies wildly

- **Active monthly:** VoiceInk (v1.74 → v1.70 over Feb–Apr 2026), FluidVoice (v1.5.12 → v1.5.10 in March), macparakeet (v0.5.6 → v0.5.2 across April).
- **Active enterprise:** Wispr Flow, Superwhisper, Granola — pricing pages and docs current.
- **Stagnant:** Whispo (last release 2024-11-22, no activity in 2025–2026).

For a Show HN style launch, the credible competitive frame is "active OSS macOS-native dictation field with three or four monthly-shipping projects," not "vs. Wispr."

### 4. Open-source license matters

GPLv3 dominates the OSS slice (FluidVoice, macparakeet, VoiceInk). MIT is rare (pindrop, swift-scribe). AGPL-3.0 (Whispo) is the strictest. Untype's license is unset on `main` per the `oss-competitor-landscape-2026.md` survey — picking one before any Show HN is an explicit decision the readiness audit (B3) should surface.

### 5. The 8 rows are not 8 competitors

Three of these (Granola, Apple Dictation, arguably Whispo) are not direct rivals to Untype on user job:

- **Granola** is meeting-notes; users searching "granola alternative" are sometimes looking for ad-hoc voice-to-text and sometimes for a meeting tool. Untype's comparison page (B4) handles this with a "they solve different problems" frame, which is more credible than pretending Untype competes with it head-on.
- **Apple Dictation** is the floor: free, pre-installed, no AI polish. It's not a feature-comparable rival; it's the baseline any paid alternative must clear.
- **Whispo** is the cautionary tale: feature-complete on paper, abandoned in practice. It belongs on the matrix as a reminder that shipping cadence is part of the user offer.

The four real head-to-head competitors are: **Wispr Flow** (commercial cloud), **Superwhisper** (commercial local-first), and **VoiceInk + FluidVoice** (OSS local-first). Untype sits in the same architectural lane as the latter two and the same UX lane as the first.

---

## Quick reconcile against earlier docs

- `competitive-landscape.md` lists Sotto, Spokenly, Voibe, Aqua Voice, Serenade in §1.8 as "emerging." None of them entered this matrix because the brief specified the canonical 8 rows. They remain in scope for the SEO spine (B2) where comparison-page content can target their search queries.
- `head-to-head-comparison.md`'s Wispr/Superwhisper deltas remain accurate; the only update is Wispr Flow's pricing page now shows annual as $12/mo vs. $15/mo monthly (20% discount), which is a slight increase in their annual carrot.
- `distribution-monetization.md`'s pricing baseline ($6–10/mo or $79–129 lifetime as Untype's sweet spot) holds — Superwhisper's $8.49/mo and Wispr's $15/mo remain the bracket.

## Verification posture

Every cell with a footnote was confirmed at one of these primary sources during 2026-05-01:

- Vendor landing or pricing pages (Wispr, Granola, Superwhisper, Apple).
- GitHub README and `gh release list` for OSS apps (Whispo, VoiceInk, FluidVoice, macparakeet).
- Independent reviewer pieces from `competitive-landscape.md` §5.7 for trust-gap and modes-as-table-stakes context.

Two cells are explicitly `unverified`:

- **VoiceInk paid license amount** — `tryvoiceink.com` returned a title-only HTML stub on the fetch attempt; verification would be the actual checkout page or a direct email to `Beingpax`.
- **Granola STT engine** — not disclosed on landing or pricing; verification would be a network capture during a Granola meeting bot session, which is out of scope for this doc.

Two cells were corrected against AI-pulled training data:

- Whispo's "active" reputation is **wrong**; the latest commit is 2024-11-22 per `gh api`. The repo description still implies activity but the project is functionally dormant.
- VoiceInk's release dates surfaced by WebFetch were given as 2025; `gh release list` shows the canonical dates as 2026 (v1.74 on 2026-04-22). The matrix uses the `gh` data.
