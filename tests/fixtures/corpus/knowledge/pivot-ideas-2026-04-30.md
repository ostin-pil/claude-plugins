# Pivot Ideas Research
**Date**: 2026-04-30
**Status**: Brainstorm, not a recommendation. Surfaces candidate pivot directions for the ICP / Lean Canvas work.
**Sources**: `research/competitive-landscape.md` (2026-04-10 + 2026-04-19 update), `research/user-pain-points-and-desires-2026.md` (2026-04-18), `research/oss-competitor-landscape-2026.md`, `knowledge/ux-audit-and-takes-2026-04-30.md`. No fresh web research, current research is recent and dense enough that this brainstorm is purely synthesis, not new mining.

---

## 0. Frame

The current Untype shape: **macOS-only voice dictation overlay** with on-device Apple Speech STT, BYOK / cloud LLM polish, push-to-talk `fn` hotkey, post-utterance review toast, intent-driven cleanup via context profiles. Implicit ICP: privacy-pragmatic power user who dictates short messages and wants polish. Implicit price-point: $7–9/mo or $79 lifetime.

This brainstorm asks: **what's the next-most-promising shape if we were starting tomorrow with the same code and research?** Not "should we pivot", that's a separate decision (X1). This is "if a pivot were warranted, what would the candidates be."

Pivots are mapped on four axes, each independently movable. The current Untype sits at: `audience: power users`, `surface: contextual overlay bar`, `depth: single-shot dictation`, `bundle: standalone`.

---

## 1. Candidate pivot directions (12)

### Audience pivots, who Untype is for

**A1, Voice for long-form writers**
Reposition as a writing companion, not a message tool. Sidecar dock with history, tone library, draft graveyard. Hotkey captures, but the *medium* of voice becomes drafting paragraphs, not Slack replies.
*Concrete shape:* Untype's UI becomes the U1 Take B (sidecar dock) by default. Dictations stack as "drafts" with edit / merge / re-style operations. New polish profiles: "blog post," "newsletter," "long-form essay." Removes the focused-input anchor.
*Audience signal:* AudioPen positions here. afadingthought (Substack writer) reviews dictation tools through a writing lens. Dropbox Paper / Substack / iA Writer ecosystems imply demand for "voice into long-form."

**A2, Voice for multilingual professionals**
Lean wholesale into think-in-L1 / write-in-L2. Russian-, Ukrainian-, Mandarin-, Spanish-, Arabic-, Hindi-native professionals writing in English (or vice versa) for daily work. Translation isn't a feature, it's the core operation.
*Concrete shape:* Default polish profile is "translate to target language with native-fluent register." Per-app target-language detection (Slack DM in Russian channel to Russian output; Gmail to English domain to English). Round-trip preview ("Cleaned · Original · Source-language") in the review toast.
*Audience signal:* `competitive-landscape.md` Section 6 calls this out as Tier-2 and notes no competitor handles it well. `user-pain-points-and-desires-2026.md` Section 4.5 confirms: "no competitor addresses think-in-L1 / write-in-L2." The Untype product memo's Tier 2 explicitly names EN/RU/ZH.

**A3, Voice for RSI / accessibility**
Reliability-first, voice-only mode, voice corrections, expanded scope to navigation and editing. Competes with Talon, Voice Control, Dragon, but as a modern macOS-native AI-augmented option in a category that's stagnated since Dragon.
*Concrete shape:* U1 Take C (voice-edit fuse) becomes the default. Hotkey-free option (toggle from menu bar). Voice commands inline ("new paragraph", "delete that", "go to top"). System-wide cursor and selection control via voice. Accessibility-cert friendly (HIPAA-adjacent).
*Audience signal:* `competitive-landscape.md` Section 3.2 Gap 7 names this directly: "voice dictation is critical for RSI sufferers, but most tools treat accessibility as a side benefit, not a primary design consideration." Apple Voice Control exists but is widely judged unreliable. Talon is powerful but esoteric.

**A4, Voice for developers (non-code)**
PR descriptions, commit messages, Slack about code, technical docs, code review comments. Aqua Voice owns "voice for code"; Untype would own "voice for *talking about* code."
*Concrete shape:* Polish profiles for `commit-message`, `pr-description`, `code-review`, `technical-doc`, `slack-eng`. Code-aware vocabulary (recognizes class/function/library names without botching them). Integration hooks: paste into VS Code, Xcode, terminal commit prompts.
*Audience signal:* `user-pain-points-and-desires-2026.md` 4.1 highlights this as a gap. Aqua Voice's commercial traction validates voice-for-developers as a real audience; the *non-code* slice is unserved.

**A5, Voice for executive / business communications**
Executives, managers, founders, knowledge workers doing high-volume structured business writing. Premium price ($15–25/mo), zero-tinker setup, on-device privacy, perfect business polish.
*Concrete shape:* Drop the BYOK angle entirely (this audience doesn't want to manage API keys). Sell on-device-only mode + a managed-cloud-key tier. Polish profiles tuned for "executive summary," "team update," "client email." Sales motion via LinkedIn, not HN.
*Audience signal:* Wispr's $15/mo positioning and 14-day-trial approach implicitly targets this, but loses them post-trial on reliability and privacy. The premium-business segment exists; Wispr is shedding them.

### Surface pivots, where Untype shows up

**S1, Sidecar dock**
Persistent right-edge column. Already specified in U1 Take B. Trades focused-input anchor for history-first interaction.

**S2, Menubar-popover (Spotlight-style)**
Hotkey opens a center-screen modal palette like Cmd-Space. Mic active immediately. Recent dictations browsable below. Slash commands (`/email`, `/code`, `/ru-to-en`).
*Concrete shape:* No focused-input anchor at all. Insert action picks the previously-frontmost app from a stored reference. Supports voice commands beyond dictation (`/translate this Slack thread`, `/summarize the selected text`).

**S3, Browser extension companion**
For web apps where AX / CGEvent insertion is unreliable (Notion, Slack web, Gmail, Linear). Pairs with the macOS app, same hotkey, same review surface, but insertion goes through the DOM via the extension when on a web target.
*Concrete shape:* Native app remains, but acquires a Chrome / Safari / Arc extension peer. Detects if frontmost app is a browser; if yes, routes insertion through DOM. Solves the Electron / web-app insertion class of bugs that VoiceInk (#646) and Wispr (clipboard restore) chronically hit.

**S4, CLI / scriptable interface**
`untype dictate --profile=email | pbcopy`, `untype listen --output=stdout`. Scriptable from shell, hooks into Raycast, Alfred, Hammerspoon, scripts. No overlay at all.
*Concrete shape:* Headless mode; UI is a status indicator only. Adds a stable IPC API. Targets the developer / power-user crowd that wants composition with their existing tools.
*Audience signal:* `user-pain-points-and-desires-2026.md` Section 1.5 desired-features lists CLI as a request. Spokenly is dabbling. VoiceInk users ask in #650-adjacent issues.

### Depth pivots, what Untype *does* with voice

**D1, Voice-driven workflows (chained operations)**
Voice as orchestrator. "Translate the selected text to Russian and email it to Sergey." "Summarize the last 10 Slack messages from #eng-chat and post in #eng-summary." Untype parses intent, plans, executes.
*Concrete shape:* Polish layer becomes a planning layer. Adds tool-use scaffolding (clipboard read, AX read, app-launch, send-via). Frontier-LLM-dependent. Closer to Cluely / Granola in spirit but voice-led.
*Audience signal:* the LLM commodity boom means *every* productivity tool is heading here. First-mover for voice-orchestrated Mac workflows is open.

**D2, Voice as second-brain capture**
Dictate freely, Untype parses, files into Notion / Apple Notes / Obsidian / Bear with tags, dates, project assignments. Voice to knowledge graph. Not insertion-driven; capture-and-organize-driven.
*Concrete shape:* AudioPen is the closest analogue but web-only. Untype becomes a voice-to-second-brain native app: hold `fn`, ramble, system files into the right note with tags. Polish becomes structuring. New target: knowledge-worker tooling stack rather than messaging.

### Bundle pivots, what comes with it

**B1, Untype + voice search across own dictations**
Dictation history becomes searchable + queryable via voice or text. "Find the proposal I dictated last Wednesday." "What was that pricing point I mentioned to Sam?"
*Concrete shape:* Adds a local index over dictation history. Voice command opens search. Pairs with sidecar surface (S1) or palette (S2). Differentiator nobody has, every other tool treats dictation as ephemeral.

**B2, Untype + clipboard manager**
Bundle: dictation + Raycast/Maccy-style clipboard manager + paste-with-voice-search. "Paste my last Untype dictation about the proposal."
*Concrete shape:* The clipboard pane becomes the history surface. Cross-sells: users who want a clipboard manager get dictation as a bonus; users who want dictation get clipboard as a bonus. Subscription gates both.

**B3, Untype + accessibility suite**
Pairs with A3. Voice control + voice cursor + voice commands + dictation in one bundle. Premium accessibility tool for RSI users priced like a serious accessibility solution ($25–50/mo or via insurance reimbursement claim path).

---

## 2. Scoring matrix

Score 1 (low) – 5 (high) on five dimensions. Total is unweighted sum (40 max).

| ID | Idea | Differentiation | Build cost | Distribution | Willingness-to-pay | Anti-AI fit | **Total** |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| A1 | Voice for long-form writers | 3 | 4 (sidecar refactor) | 2 (writers don't seek dictation) | 3 | 4 | 16 |
| **A2** | **Multilingual L1-to-L2** | **5** | **3** | **3** (network effects in diaspora) | **4** | **5** | **20** |
| **A3** | **RSI / accessibility** | **4** | **3** (voice-edit fuse) | **4** (audience self-selects, dedicated communities) | **4** | **5** | **20** |
| A4 | Developer (non-code) | 3 | 2 (polish profiles) | 4 (HN, dev Twitter) | 3 | 3 | 15 |
| A5 | Executive / business | 2 | 2 | 1 (LinkedIn sales not solo-friendly) | 5 | 2 | 12 |
| S1 | Sidecar dock | 3 | 3 | 2 (UI shift, no audience change) | 2 | 2 | 12 |
| S2 | Menubar palette | 2 | 3 | 2 | 2 | 2 | 11 |
| S3 | Browser extension | 4 | 4 (cross-stack maintenance) | 3 | 3 | 4 | 18 |
| S4 | CLI / scriptable | 3 | 2 | 4 (HN, devs) | 2 (non-monetizing audience) | 4 | 15 |
| D1 | Voice-driven workflows | 4 | 5 (tool-use scaffolding) | 3 | 4 | 2 (LLM-heavy) | 18 |
| **D2** | **Voice second-brain capture** | **5** | **4** | **3** | **4** (Notion / Obsidian crowd pays) | **3** | **19** |
| B1 | History + voice search | 3 | 3 | 2 | 3 | 3 | 14 |

**Top three by score:** A2 (multilingual, 20), A3 (accessibility, 20), D2 (second-brain capture, 19), with S3 (browser ext, 18) and D1 (voice workflows, 18) close behind.

---

## 3. Top 3 worth deeper research

### Top 1: A2: Multilingual L1-to-L2

**Why this scores top:** the only direction with a 5 on differentiation *and* a 5 on anti-AI fit. Validated demand (multiple research-doc sections), zero direct competition (Wispr does app-aware tone but not language; Whisper-based tools do polyglot STT but not composition translation), and a natural alignment with an immigrant / diaspora audience that's underserved by US-defaulted product design. The reliability and privacy friction in Wispr/Aqua is *worse* for non-English users (English-bias hallucinations, audio routed to US servers raising EU/RU/CN privacy concerns), which means the trust-gap narrative is sharper, not duller, in this segment.

**What's still uncertain, needs deeper research:**
- *Concrete L1 priority order.* Memory says Untype product memo lists EN/RU/ZH. Is that informed by user demand, or by founder language access? A 2-week interview push targeting bilingual professionals (Russian/Spanish/Mandarin/Hindi/Arabic native speakers in tech) would calibrate this.
- *Translation quality bar.* Untype's polish step is currently "tone adaptation"; translation is a different skill. Need to validate that current cloud-LLM polish (Claude/GPT-4-class) is good enough for native-fluent business register, not just functional.
- *Pricing in this segment.* Is multilingual professional willing to pay more or less than the US power-user segment? DeepL Pro is €8.99/mo; bilingual users already pay it. Bundle pricing? Discount for diaspora regions?

### Top 2: A3: Accessibility / RSI

**Why this scores top:** two 5s (anti-AI fit, distribution because the audience self-selects and has dedicated communities). The accessibility / RSI segment is loyal, vocal, and underserved, Dragon stagnated, Apple Voice Control is brittle, Talon has a steep learning curve. Reliability-forward UX (which the trust-gap narrative made fashionable) is a *requirement* here, not a marketing angle. Ship quality and the audience finds you.

**What's still uncertain, needs deeper research:**
- *How big is the macOS-specifically slice?* RSI users skew Windows / hardware-keyboard-friendly setups. Is the macOS RSI cohort large enough to sustain a business?
- *Expansion scope.* "Accessibility suite" implies voice control, voice navigation, that's a much larger product than dictation. Should Untype build all of it, or partner / integrate with an existing accessibility layer?
- *Pricing legitimacy.* Insurance reimbursement (HSA/FSA in US) and assistive-technology grants exist but require certification. Is Untype ready to navigate that, or stay below it?

### Top 3: D2: Voice second-brain capture

**Why this scores top:** highest single-axis score (5 on differentiation), genuinely category-creating in a way the others aren't. AudioPen is the only competitor and it's web-only with no system integration. The Notion/Obsidian/Bear crowd is large, paying, and has explicit "voice capture" pain. Combining voice-first capture with native-mac integration with structured polish (tag, project, date, sentiment) is a real product nobody is shipping.

**What's still uncertain, needs deeper research:**
- *Integration depth.* Does Untype need first-class Notion + Obsidian + Apple Notes + Bear + Day One adapters? Or is "dump to clipboard with markdown frontmatter" enough?
- *Competition with future Apple.* Apple Notes already does dictation; Apple Intelligence will ramp up structuring features. Does Apple ship past Untype in 18 months on this specific axis?
- *Audience overlap with current users.* Current Untype users (implicit ICP: power-user dictators) may *not* be the second-brain crowd. This is closer to a true pivot, different audience, different product.

---

## 4. Anti-pivots, directions that look attractive but lose

**AP1, Don't go cross-platform.**
Wispr's Mac+Win+iOS+Android sprawl dilutes their UX (Windows version "just crashes," iOS "pre-alpha"). Native macOS is differentiation; spreading thin destroys it. Solo-dev resource math doesn't allow it. *This is wrong if:* macOS market share inside Untype's ICP turns out to be <20% (very unlikely for any segment except enterprise IT).

**AP2, Don't go enterprise / SOC2 / HIPAA.**
Superwhisper owns this space. Compliance is a 12-month + lawyer + audit cost the project can't bear, and the resulting product is unrecognizable from the dictator-friendly tool. *This is wrong if:* a single major customer (university, hospital, gov) pre-commits to a 6-figure deal that funds the cert work, but then you're a different company.

**AP3, Don't go meeting transcription.**
Otter and Notta own this. Different product (long-running, multi-speaker, integration-heavy) and different sales motion (team / enterprise). *This is wrong if:* a bolt-on meeting-summarizer mode emerges that uses the *existing* dictation flow without new infrastructure, but that's a feature, not a pivot.

**AP4, Don't add infinite custom prompt slots.**
Superwhisper is *losing* customers over this (afadingthought review: "configuring a server, not installing an app"). Untype's opinionated 3–5 polish profiles are a feature, not a limitation. *This is wrong if:* a user-research push surfaces real demand for >5 profiles among the chosen ICP. Default to "no" until proven.

**AP5, Don't pivot to mobile-first.**
A2/A3/D2 pivots all involve macOS as primary surface. The team has macOS expertise and the architecture is macOS-native (NSPanel, AX, CGEvent). Mobile is a separate product, separate audit, separate App Store gatekeepers. *This is wrong if:* the multilingual or second-brain pivot reveals strong mobile demand, in which case it's a v2 expansion, not a v1 pivot.

---

## 5. Recommendation

**Use this as input to P3 (ICP), not as a decision.** The 12 candidates above feed straight into the ICP work, each is essentially "a different ICP × surface combination." P3 will pick a primary ICP, which collapses most of these candidates to either "obvious yes" or "obvious no."

If P3 lands on:
- *bilingual professionals* to A2 + maybe S3 (browser extension for L1-input languages)
- *RSI / accessibility* to A3 + maybe S4 (CLI for Talon-power-user crossover)
- *power knowledge workers* to status quo + B1 (history) + maybe D2-lite
- *long-form writers* to A1 + S1 (sidecar)
- *developers* to A4 + S4 (CLI)

If none of those map to current beliefs about who buys Untype, P3 will surface a tension that's worth resolving on paper before more code lands.

**Open hooks:**
- *For X1 (build-vs-extend):* A3 (accessibility) and D1 (voice workflows) push the architecture toward a fundamentally different shape, voice as control plane, not just input. X1 should consider whether build-extend trade-offs differ for a control-plane vs an input-method positioning.
- *For P1 (Lean Canvas):* the top-3 candidates each imply a different Lean Canvas. P1 should be drafted *after* P3 picks an ICP, with this doc as the source of "what Solution / UVP / Channels we considered and rejected."
- *For U1 (UX audit):* the three takes (live ghost / sidecar / voice-edit) map cleanly to A2/A1/A3. The pivot direction will pick the take, not the other way around.
