# SEO keyword spine and content map — May 2026

**Date:** 2026-05-01
**Scope:** A free-source SEO spine for Untype's marketing surface, covering 30–50 keywords clustered by buyer intent. Each keyword is tagged with intent, the existing competitor that already ranks for it, and the suggested content type. The spine maps back to the comparison-page and build-in-public-post templates in `~/.claude/plans/discovery-starter/templates/` so an activated marketing site can populate from a known editorial backbone.

This is a *content planning* doc, not a positioning doc. Positioning lives in [`competitor-deep-diff-2026-05.md`](./competitor-deep-diff-2026-05.md) and `competitive-landscape.md`. The spine here is "what queries map to which template / page / post."

## Sourcing

- Free public sources only. No paid SEO tools (Ahrefs, Semrush, Mangools) were sign-up-required.
- Inputs: Google autocomplete (manual brainstorm), competitor page titles surfaced via WebFetch, listicle articles already linked in `competitive-landscape.md` §5.7, and the AnswerThePublic-style intent fan around the head term.
- Search-intent and competition signals are *qualitative best-guess* tags from the surveyed competitor pages. They are NOT volume estimates — those would require a paid keyword tool that the priorities anti-list explicitly forbids signing up for.

## Three hero keywords (editorial backbone)

When a marketing site activates per the "Show HN-grade release approaching" trigger, these three queries are the load-bearing ones. Every other piece of content radiates from them.

| # | Hero keyword | Intent | Why hero | Lands as |
|---|--------------|--------|----------|----------|
| H1 | `wispr flow alternative` | Comparison / alternative-seeking | Highest commercial-intent query in the category. Already captured by Voibe, machow2, WhisperClip listicles. Untype's privacy-pragmatic + native-Swift + pluggable-LLM frame is a real differentiator vs. cloud-only Wispr | Comparison page (`/vs/wispr-flow`) — see `templates/comparison-pages.md` Page 1 |
| H2 | `local dictation mac` (and `private dictation mac`, `offline dictation mac`) | Solution-aware | Captures privacy-conscious users who already know they want local STT. Untype's WhisperKit + on-device polish via Apple FM / Ollama is the strongest answer in this lane. Competitive but winnable — VoiceInk / FluidVoice / macparakeet rank here but the user audience expects a polished commercial-shape product | Listicle page (`/private-dictation-mac`) — see `templates/comparison-pages.md` Page 3 |
| H3 | `voice to text mac with ai cleanup` (and `dictation with grammar fix mac`) | Solution-aware / problem-aware | Apple Dictation's gap: raw transcript only. Untype's whole pitch is the polish layer. This is the best query to convert someone who already tried Apple Dictation and found it lacking | Landing page hero / build-in-public post #4 (the "small ship that compounded" pattern fits well) |

Everything else in the spine supports these three.

---

## Keyword spine

### Cluster 1 — Problem-aware (user knows the pain, not the category)

| Keyword | Intent signal | Already ranks (sample) | Suggested content type |
|---------|---------------|------------------------|------------------------|
| `apple dictation cuts off` | Pain query — user hit Apple Dictation's 30 s inactivity stop | Apple support forums; Reddit r/MacOS | Blog: "Why macOS Dictation cuts off and what to do" — bridges to Untype as the longer-form answer |
| `mac dictation not working` | Troubleshooting — top of funnel | Apple support; SaaS troubleshooting articles | Blog: troubleshooting walkthrough that ends with a "want this not to happen?" pitch |
| `dictation faster than typing mac` | Benefit query | Wispr Flow landing | Build-in-public post #4 angle — "30-line ship that fixed the cold-start delay" |
| `voice typing mac` | Generic — broad funnel | Apple Dictation; Wispr Flow | Listicle entry, not a dedicated page |
| `rsi dictation software mac` | Use case — accessibility audience | usevoicy.com (RSI guide) | Build-in-public post variant — "Untype for users who *need* voice input" |
| `voice notes to clean text` | Pain — rambling speech to polish | AudioPen | Blog: framing piece on "polish vs. transcript" — Untype angle |
| `transcribe and clean up grammar` | Pain — the polish step | Various LLM-cleanup articles | Landing page hero variant |

Total: 7 keywords.

### Cluster 2 — Solution-aware (user knows there are dictation tools, evaluating)

| Keyword | Intent signal | Already ranks | Suggested content type |
|---------|---------------|---------------|------------------------|
| `local dictation mac` | High intent — privacy axis | VoiceInk, FluidVoice, MacWhisper | Listicle (Hero H2) |
| `private dictation mac` | High intent — privacy axis | Sotto, Spokenly | Listicle entry (Hero H2 variant) |
| `offline dictation mac` | High intent — connectivity axis | MacWhisper, Whispo (stagnant) | Listicle entry (Hero H2 variant) |
| `voice to text mac with ai cleanup` | Hero H3 | Wispr Flow, Superwhisper | Landing page hero |
| `whisperkit mac dictation` | Tech-aware | argmax-oss-swift, pindrop | Show HN angle / dev-blog post |
| `parakeet vs whisper dictation` | Tech-aware | macparakeet, FluidVoice, FluidAudio README | Build-in-public post — "why Untype uses WhisperKit and what would tip us to Parakeet" |
| `byok dictation mac` (BYOK / bring-your-own-API-key) | Power-user / dev | FluidVoice, macparakeet | Show HN angle — provider abstraction is the architecture story |
| `apple foundation models dictation polish` | macOS 26 / Tahoe-aware | swift-scribe; new-Apple-FM blog posts | Build-in-public post — Untype shipped the FM polishing adapter in `5521ce6` |
| `ollama dictation mac` | Local-LLM crowd | speak2, FluidVoice, macparakeet | Show HN angle — Ollama adapter shipped in session 52 |
| `voice command no cloud mac` | Privacy-strict | Spokenly, Sotto | Listicle entry |
| `swift dictation app` | Native-stack-aware | pindrop, swift-scribe, macparakeet | Show HN backstory section |
| `electron-free dictation mac` | Native-aware (anti-Electron) | None directly — white space | Build-in-public post — the "lightweight as a surfaced claim" angle from `competitive-landscape.md` §5.6 #7 |

Total: 12 keywords.

### Cluster 3 — Comparison / alternative-seeking (highest commercial intent)

| Keyword | Intent signal | Already ranks | Suggested content type |
|---------|---------------|---------------|------------------------|
| `wispr flow alternative` | Hero H1 — alternative-seeking | Voibe, machow2, WhisperClip | Comparison page `/vs/wispr-flow` |
| `superwhisper alternative` | Alternative-seeking | Voibe; afadingthought | Comparison page `/vs/superwhisper` (template not yet drafted) |
| `wispr flow vs superwhisper` | Comparison | Voibe head-to-head | Comparison-page side post |
| `wispr flow privacy` | Privacy-pivot | Ryan Shrott Medium pieces | Blog: privacy honest comparison — concedes Wispr's value, claims privacy lane |
| `wispr flow trust gap` | Brand+pain | Ryan Shrott Medium | Blog: an honest acknowledgement of the trust gap and how Untype's transparency UX answers it |
| `granola alternative for dictation` | Mis-targeted alternative seeker | Granola comparisons | Comparison page `/vs/granola` — the "they solve different problems" frame |
| `voiceink alternative` | Alternative-seeking | Voibe; tryvoiceink | Comparison page (low priority — VoiceInk is OSS-friendly audience overlap, not pure conversion target) |
| `macwhisper alternative` | Alternative-seeking | Various | Listicle entry |
| `apple dictation alternative` | Alternative-seeking | Wispr Flow, Superwhisper landings | Listicle entry — high-volume but low-intent |
| `wispr flow free alternative` | Alternative + price-gating | Various | Listicle entry |
| `mac dictation app comparison` | Comparison | machow2, lumevoice | Listicle (Hero H2 page hosts this) |
| `best dictation app mac 2026` | Listicle SEO | machow2 ranks #1 | Listicle (Hero H2) |
| `wispr flow vs apple dictation` | Comparison | Wispr Flow content | Comparison-page side post |

Total: 13 keywords.

### Cluster 4 — Brand-aware (post-launch / branded queries)

These only matter once Untype has a name in market. They're listed for completeness but should not drive content until a public release.

| Keyword | Intent signal | Already ranks | Suggested content type |
|---------|---------------|---------------|------------------------|
| `untype dictation mac` | Brand query | None — pre-launch | Landing page (must rank #1 for our own brand) |
| `untype app voice` | Brand query | None | Landing page anchor |
| `untype vs wispr flow` | Branded comparison | None — pre-launch | Comparison page H1 should match this exactly |
| `untype vs superwhisper` | Branded comparison | None | Comparison page (template extension) |
| `is untype open source` | Brand + license | None — pre-launch; license decision parked | Landing-page FAQ entry — answer must be honest per `show-hn-prep.md` "Is this open source?" playbook |

Total: 5 keywords.

### Cluster 5 — Niche / use-case (long-tail, lower-priority)

| Keyword | Intent signal | Already ranks | Suggested content type |
|---------|---------------|---------------|------------------------|
| `dictation for developers mac` | Dev audience | Aqua Voice, Serenade | Blog: dev-focused angle but not core — Aqua/Serenade own this lane |
| `bilingual dictation mac` | Multilingual pro | Notta, Wispr | Blog: multilingual angle (matches `competitive-landscape.md` §6.4 niche #1) |
| `slack dictation mac` | App-context | Wispr Flow's auto-tone-by-app | Blog: short post on app-context UX as a feature |
| `mac dictation push to talk` | UX-pattern | speak2 (fn-key), pindrop | Build-in-public post — "why hold-to-talk beats toggle" |
| `dictation without sending audio to cloud` | Privacy-strict variant | Spokenly | Listicle entry (overlaps with H2) |
| `mac dictation history` | Feature | macparakeet, VoiceInk | Roadmap mention; defer |
| `dictation hipaa mac` | Compliance audience | Superwhisper SOC 2 angle | Blog: "we don't claim HIPAA, here's what we *do* claim" |

Total: 7 keywords.

**Spine total: 44 keywords across 5 clusters.**

---

## Mapping to discovery-starter templates

The point of the spine is that an activated marketing site can populate from existing template outlines rather than draft from scratch. Here's the mapping back to `~/.claude/plans/discovery-starter/templates/`:

### `templates/comparison-pages.md`

| Page outline | Hero keyword | Backing keywords from spine |
|--------------|--------------|----------------------------|
| Page 1 — Untype vs. Wispr Flow | H1 (`wispr flow alternative`) | `wispr flow privacy`, `wispr flow vs apple dictation`, `wispr flow free alternative`, `wispr flow trust gap`, `wispr flow vs superwhisper` |
| Page 2 — Untype vs. Granola | `granola alternative for dictation` | (tight scope; Granola is a different category — the page is honest about it) |
| Page 3 — Best private dictation tools for Mac | H2 (`local dictation mac`, `private dictation mac`, `offline dictation mac`) | `voice command no cloud mac`, `dictation without sending audio to cloud`, `mac dictation app comparison`, `best dictation app mac 2026` |

The first comparison page (Wispr) is the highest-leverage; B4 of this plan drafts it.

### `templates/build-in-public-posts.md`

The five drafts in that file map to keyword clusters as follows:

| Draft | Cluster fit | Suggested keyword anchor |
|-------|-------------|--------------------------|
| Draft 1 — A bug that surprised you (TCC permission cliff) | Solution-aware (technical) | `swift dictation app`, `electron-free dictation mac` |
| Draft 2 — A feature you killed (translation stage) | Niche / use-case | `bilingual dictation mac` (in reverse — the post explains what was *cut*) |
| Draft 3 — A user reaction that changed your mind (polish strength) | Solution-aware | `voice to text mac with ai cleanup` (Hero H3) |
| Draft 4 — A small ship that compounded (Apple Speech pre-warm) | Problem-aware | `dictation faster than typing mac`, `apple dictation cuts off` |
| Draft 5 — A non-obvious privacy decision (telemetry choices) | Comparison + privacy | `wispr flow privacy`, `wispr flow trust gap`, `dictation without sending audio to cloud` |

Each post is more credible when the specific learn / ask is real — the keyword anchor is a navigation aid for which audience the post lands with, not a "stuff this term in" instruction.

### Other templates

- `templates/loom-dm-scripts.md` — DMs are not SEO surfaces; the spine doesn't drive them.
- `templates/recruitment-emails.md` — same.
- `templates/in-app-surveys.md` — same.
- `templates/changelog-email.md` — *some* benefit from the spine; release-note posts can target `mac dictation [version-N feature]` long-tail queries when a Show HN-grade release ships.

---

## Editorial cadence (when activation fires)

Per `~/.claude/plans/discovery-starter/priorities.md`, none of this gets executed until the "Show HN-grade release approaching" tier-2 trigger fires. When it does, the suggested ordering is:

1. **Weeks -4 to -2 before launch:** publish hero pages H1–H3 in that order. They take longest to rank organically and need that head start.
2. **Week -1:** publish 1–2 build-in-public posts from the cluster that matches the launch angle (privacy pivot → Draft 5; speed pivot → Draft 4).
3. **Week 0 (launch):** comparison pages are live; Show HN posts the H1 angle as the primary draw.
4. **Weeks +1 to +4:** publish the remaining build-in-public drafts on a Tue–Thu cadence per the `templates/build-in-public-posts.md` rules.

This sequence keeps the spine *latent* — it doesn't generate writing tax until the activation moment, and at that point the editorial path is already mapped.

---

## What's deliberately not here

- **Volume estimates.** Free Google data doesn't give them; the priorities doc forbids paid-tool sign-ups. Volume is a question to answer if-and-when a launch is imminent, by manually checking 5–10 of the highest-priority terms in Google Trends or a free Mangools demo.
- **Backlink strategy.** The activation doc handles distribution (Show HN, Reddit, build-in-public) which is the practical way an indie tool earns links. SEO-link-building is a tier-3 question.
- **AdWords / paid search.** Out of scope per the no-SaaS-sign-ups rule.
- **Competitor brand-bidding.** Untype should *not* run ads against `wispr flow` or `superwhisper` brand queries; that's the kind of move that earns the wrong kind of HN attention.
- **Foreign-language SEO.** EN-only for the v1 spine. Multilingual user audiences in Untype's roadmap (RU/ZH per `competitive-landscape.md` §6.4) get spines later.

---

## Sources

- [machow2 — Best Dictation Software for Mac 2026](https://machow2.com/best-dictation-software-mac/) — listicle ranking and "best for X" angles.
- [Voibe — Wispr Flow alternatives](https://www.getvoibe.com/blog/wispr-flow-alternatives/) — alternative-seeking framing and competitor list.
- [Voibe — Superwhisper alternatives](https://www.getvoibe.com/blog/superwhisper-alternatives/) — paired alternative-seeking framing.
- [WhisperClip comparison (2026)](https://whisperclip.com/blog/posts/whisperclip-vs-superwhisper-wisprflow-macwhisper-which-ai-dictation-fits-your-workflow) — head-to-head workflow framing.
- [afadingthought — True Differentiators in AI Dictation (2026)](https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac) — workflow-integration-as-moat insight.
- [Ryan Shrott — Wispr Flow Trust Gap](https://medium.com/@ryanshrott/the-wispr-flow-trust-gap-why-reliability-matters-more-than-hype-in-2026-c7dd55392408) — trust-gap query frame.
- [usevoicy — RSI software tools](https://usevoicy.com/blog/best-software-tools-for-rsi) — RSI/accessibility audience query frame.
- [lumevoice — Best AI dictation tools for developers 2026](https://lumevoice.com/blog/best-ai-dictation-tools-for-developers-2026/) — dev-audience query frame.
- [Apple — Use Dictation on Mac](https://support.apple.com/guide/mac-help/use-dictation-mh40584/mac) — Apple Dictation behavior anchoring `apple dictation cuts off`-style queries.
