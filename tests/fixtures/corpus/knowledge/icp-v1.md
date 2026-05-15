# ICP Definition v1
**Date**: 2026-04-30
**Status**: First-pass ICP, picks a primary + secondary, names the disqualified segments, identifies what we'd need to verify with real users to upgrade this to v2.
**Inputs**: `knowledge/ux-audit-and-takes-2026-04-30.md` (U1), `knowledge/pivot-ideas-2026-04-30.md` (X5), `knowledge/pivot-build-vs-extend.md` (X1), `research/competitive-landscape.md`, `research/user-pain-points-and-desires-2026.md`, the implicit ICP traceable in `Untype/Settings/SettingsStore.swift` (BYOK assumption), `Sources/UntypeCore/Processing/AppContext.swift` (intent-aware polish), and the existing language list in `UntypeCore` (English-only today, Russian/Chinese in Tier 2 of the product memo per memory).

---

## 0. What an ICP is (and isn't) for Untype right now

This document is *one ICP, picked from candidates, justified*. It's not a multi-persona research deck. It's not a market sizing study. The job is to give P1 (Lean Canvas) and any future positioning a **single concrete answer** to "who is this for?", defensible enough to stand for 3–6 months of build, and falsifiable enough to update if interviews surface evidence.

**Caveat:** this ICP is desk-research-grade. It synthesizes second-hand user voice (App Store reviews, HN threads, Reddit aggregators, blog reviews), *not* primary interviews with Untype users. The discovery starter kit in memory references a Mom Test interview script that hasn't been run yet. Treat this as a **starting hypothesis** to validate, not a closed question.

---

## 1. Candidate segments (6)

Pulled from the X5 pivot brainstorm + the implicit "current Untype user" baseline. These are the segments worth scoring, not an exhaustive list.

| ID | Segment | One-line description |
|---|---|---|
| **C1** | Privacy-pragmatic power knowledge worker | Engineer / PM / consultant who lives in Slack and Mail; wants polish; won't send audio to cloud; can manage an API key |
| **C2** | Bilingual / multilingual professional | L1-native (Russian / Spanish / Mandarin / Hindi / Arabic / Ukrainian / Portuguese / Vietnamese) writing in English-dominant work environments daily, or the reverse |
| **C3** | RSI / accessibility user | Voice as primary input by necessity, not preference. RSI / hand injury / mobility constraint. Insurance / HSA / accessibility-budget paid |
| **C4** | Long-form writer / creator | Substack writer / journalist / content creator drafting paragraphs, not messages |
| **C5** | Developer dictating non-code | Voice for commit messages, PR descriptions, code-review comments, technical docs, anything except actual code |
| **C6** | Second-brain capturer | Notion / Obsidian / Bear / Day One power user dictating into a knowledge graph |

---

## 2. Scoring matrix

Score 1 (low) – 5 (high). Definitions:
- **WTP**, willingness to pay. 5 = pays for tools without negotiating.
- **Reachability**, can a solo founder reach this segment without paid sales motion? 5 = vibrant communities, low cost to find them.
- **Alt friction**, how unhappy are they with current alternatives? 5 = actively churning, cited in research.
- **Stack fit**, does Untype's current architecture (push-to-talk overlay, polish registry, intent profiles) serve them without a rebuild? 5 = exact fit.
- **Defensibility**, does winning this segment create a moat (white space, network effect, sticky users)? 5 = strong moat.

| ID | Segment | WTP | Reachability | Alt friction | Stack fit | Defensibility | **Total** |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| C1 | Power knowledge worker | 4 | 3 (HN, /r/macapps, Mac Twitter) | 3 (Wispr trust gap real, Apple Dictation good-enough for many) | 5 | 2 (commodity space) | **17** |
| **C2** | **Bilingual professional** | **5** | **4** (diaspora communities, in-language YT/Twitter, founder face/voice fits) | **5** (no competitor solves L1-to-L2 composition) | **4** (need translation polish profile) | **5** (white space, sticky) | **23** |
| C3 | RSI / accessibility | 5 (insurance + necessity) | 4 (specific forums, accessibility-comm) | 5 (Dragon stagnated, Voice Control flaky, Talon esoteric) | 2 (need voice corrections + navigation) | 4 (high switching cost) | **20** |
| C4 | Long-form writer | 2 | 2 (writer communities atomized) | 2 (Scrivener / iA Writer / typewriter all work) | 2 (sidecar refactor needed) | 2 (AudioPen ahead) | **10** |
| C5 | Developer non-code | 3 | 5 (HN, dev Twitter, low cost to reach) | 2 (typing is fast, low-friction baseline) | 4 | 2 (Aqua Voice adjacent) | **16** |
| C6 | Second-brain capturer | 4 (Notion/Obsidian users pay) | 3 (Notion/Obsidian Twitter/Discord) | 3 (AudioPen exists but web-only) | 3 (need adapter integrations) | 3 (category-creating but Apple risk) | **16** |

**Top 2:** **C2 (bilingual professional, 23)** and **C3 (RSI / accessibility, 20)**. Long gap before C1 (17), C5 (16), C6 (16).

---

## 3. Primary ICP: Bilingual professional (C2)

### 3.1 Elevator

> A non-native English speaker working in an English-dominant tech / business environment, who thinks faster in their L1 and writes worse in their L2, and pays a daily tax for the gap. They want to dictate in their first language and have the message *land* in English with a native-fluent register, without ceding privacy or running translation through a second tool.

### 3.2 Concretely, who this person is

- **Native language:** any non-English-dominant, Spanish, Mandarin, Russian, Hindi, Arabic, Ukrainian, Portuguese, Vietnamese, Polish, Tagalog, etc. *(Specific top-language priority is unsourced in this doc, the Untype product memo names "real-time translation," "tone adjustment," and "bilingual output" as Tier 2 differentiators but does not list specific source-language priority. Verify with founder before locking RU/ZH/ES priority.)* English-monolingual users *are not the ICP*, that's the secondary segment.
- **Profession:** software engineer, PM, designer, consultant, founder, account manager, sales, support, knowledge work where English written communication is high-volume and quality-sensitive.
- **Geography:** US / Canada / UK / EU diaspora; remote-first companies hiring globally; Latin America writing for US clients; Eastern Europe / India / Vietnam writing for US/EU customers.
- **Tech comfort:** moderate-to-high. Comfortable with API keys, BYOK, command-line setup, system-level permissions. Probably uses one of: Raycast, Alfred, 1Password, Things, Linear.
- **Why they're underserved:** their L2 writing is *functionally fine* but *feels wrong*, wrong register, off-tone, slower, anxiety-inducing in high-stakes contexts (Slack to senior leadership, customer escalations, board emails). Existing tools don't help because they assume you write in the language you speak.
- **Today's stack:** Apple Dictation in L1 + DeepL/Google Translate + manual editing + sometimes ChatGPT to "make it sound natural." Multiple tools, multiple roundtrips, audio leaving the machine, no privacy story for sensitive content.

### 3.3 Five proof points (why Untype wins for them)

1. **Native-fluent L2 polish**, the polish step isn't "tone adjustment," it's a true L1-to-L2 translation with register awareness ("formal Slack reply to senior eng," "casual customer email," "Russian-formal patronymic kept in greeting"). The cloud LLM tier is good enough for this *today*; Apple FM is not yet (per X1).
2. **Privacy-respecting**, Apple Speech for L1 STT runs on-device. Only the *text* goes to the cloud LLM for translation, never audio. The Wispr screenshot scandal lands harder for non-US users where US-cloud routing has additional regulatory weight (GDPR, RU DPA, ML data-localization laws).
3. **Round-trip transparency**, the U1 friction-list issue 1 is mandatory here: Cleaned · Original · Source-language toggle in the review toast. Bilingual users are suspicious of translation systems by experience; *visibility* of all three forms (what I said, what was transcribed, what was translated) is the trust mechanism.
4. **Per-app target language**, Slack channel `#russia-eng` to keep Russian; Mail to `@company.com` to English. Untype's existing `AppContext` + `ContextProfile` infrastructure extends naturally to per-app target language. No competitor does this at all.
5. **One tool, not three**, replaces Apple Dictation + DeepL + ChatGPT + manual editing with a single hotkey. Time saved per dictation is high, but more importantly: *cognitive load* drops because the user stops switching tools to compose one message.

### 3.4 What this ICP requires Untype to ship

- A **translation polish profile** explicitly named and prompted as such (not a generic "make it sound formal", a true `translateToTargetLanguage(text, targetLang, register)` instruction).
- **Multi-language STT** beyond English. Apple Speech supports many; need to expose language selection and per-app routing.
- The **Cleaned · Original toggle on every path** (U1 issue 1), non-Apple-Speech providers must also surface the raw transcript.
- A **language indicator** in the overlay during recording (small chip: 🇷🇺 RU to 🇬🇧 EN) so the user can see at a glance what's being captured and what they'll get out.

What's *not* needed yet: voice corrections, second-brain capture, sidecar dock, voice workflows. Keep scope tight.

### 3.5 Reach plan (90-day sketch)

The user is comfortable on camera and audio (per memory). Bilingual segments respond to *in-language* content much better than English content. A founder who can produce one demo in Russian and one in Spanish (or sub-titled / dubbed if needed) opens both channels.

- **In-language YouTube demos**, 90-second product demo in Russian, Spanish, Mandarin (in priority order based on founder's own language access). Twitter / X reposts to in-language tech communities.
- **Targeted Reddit posts**, `/r/AskRussian`, `/r/Spanish`, `/r/India`, `/r/argentina` tech threads about "how do you handle English at work?", listen first, post product when invited.
- **Diaspora newsletters / podcasts**, bilingual tech newsletters (e.g. Lex Fridman's audience overlap, Russian tech YouTubers, Indian-startup ecosystem newsletters).
- **HN / ProductHunt launch as a *secondary* channel**, the HN frame ("multilingual dictation that actually translates") is interesting but not the primary water-hole.

### 3.6 What would falsify this ICP

- 4-week interview push (per the discovery starter kit in memory): if 8 interviews with target bilingual professionals don't surface the L1-to-L2 friction as a top-3 daily annoyance, **this ICP is wrong** and we revert to C1 or C3.
- If translation quality from current cloud-LLM polish proves to be *good enough functionally* but *bad enough for senior-stakes communication* (the highest-WTP use case), the ICP shrinks to "casual bilingual users" who pay less.
- If the user's current toolchain (DeepL Pro + Apple Dictation) is *already good enough* for the high-stakes case, switching cost may exceed value.

---

## 4. Secondary ICP: Privacy-pragmatic power knowledge worker (C1)

### 4.1 Elevator

> A senior IC or manager in a mid-to-large company who lives in Slack, Mail, Linear, and Notion, and dictates 50–200 short messages a day. They've heard about Wispr Flow, possibly tried it, and either won't pay $15/mo or got burned by the trust-gap stories. They want polish, they want privacy, and they want the tool to disappear into their workflow.

### 4.2 Why secondary, not primary

C1 is the *current* Untype audience by default. The product already serves them. But:

- **WTP is medium, not high**, they balk at $15/mo Wispr but accept $7-9/mo; the price ceiling is real.
- **Alt friction is moderate**, Apple Dictation is "good enough" for many. The unhappy-with-status-quo cohort within C1 is a fraction of the segment, not the whole segment.
- **Defensibility is weak**, this is the commodity space. VoiceInk, Spokenly, Voibe, Sotto, Pipit, Aqua all target overlapping audiences. Untype wins on UX polish, not on a structural moat.

C1 wins as *secondary* because Untype serving C2 well also serves C1 well, bilingual = power-user-with-extra-language-needs. The product shape is the same; only the marketing message is different. That's the right secondary structure: *one product, two stories*.

### 4.3 Five proof points (why Untype wins for them as secondary)

1. **Native Swift, no Electron**, `competitive-landscape.md` and `user-pain-points-and-desires-2026.md` both flag Electron bloat as a real switch trigger.
2. **Pre-send review**, the `[Reviewing]` state is uncontested in the category; Wispr's auto-edit-and-paste model is a churn driver per Trustpilot and the Trust Gap pieces.
3. **BYOK-friendly**, no managed-key markup. Power users price-compare on raw inference cost; Untype respects that.
4. **Intent-aware polish**, context profiles do per-app tone *with user control*, unlike Wispr's invisible auto-detection.
5. **No telemetry, no screenshots**, the Wispr screenshot scandal of 2025 is still a switch trigger. Untype's text-only AX context is the right pattern.

### 4.4 Reach plan (90-day sketch)

- **HN Show HN**, primary channel. The technical audience overlaps strongly. Frame: "I built the dictation tool I wanted after Wispr Flow burned me." Don't lead with multilingual; lead with the trust angle.
- **/r/macapps + /r/MacApps + /r/macOS**, listen for trust-gap discussions, post when on-topic.
- **Bilingual ICP cross-pollination**, many of C2's reach channels overlap with C1's (in-language tech communities are full of expats who'd like a pure English tool too).

---

## 5. Disqualified segments

These are ICPs *I considered and rejected*. Including the reasoning so future-me doesn't re-litigate them.

### C3: RSI / accessibility user *(disqualified as primary, held as v2 expansion)*

**Why interesting:** scored 20 on the matrix, second-highest. White-space audience, high WTP, sticky.

**Why not primary now:**
- **Stack fit gap** is too large. RSI users need voice navigation + cursor + selection control, not just dictation. Untype ships dictation only. Building the rest is a 6-month investment that delays the rest of the product. U1 Take C (voice-edit fuse) is the closest current direction but only addresses corrections, not navigation.
- **Reliability bar is higher than v1 can plausibly meet.** RSI users *cannot fall back to typing* when the tool fails. That requires a maturity Untype doesn't have post-cutover.
- **Sales cycle is long**, accessibility-budget approval, insurance reimbursement, HIPAA-adjacent compliance for medical practices.

**When to revisit:** v2, after the bilingual ICP has 6+ months of telemetry and the product has settled. RSI is a natural expansion, voice-edit fuse + voice cursor + voice nav layered on the existing Untype stack.

### C4: Long-form writer *(disqualified)*

**Why interesting:** AudioPen exists; demand is real.

**Why not:**
- **Wrong UX paradigm.** Long-form writers don't want a 500×96 review toast, they want a sidecar / draft pane / dedicated app. U1 Take B (sidecar) is in that direction, but it's a *different product*.
- **WTP is low**, writers underpay for tools across the board (the Scrivener / Ulysses pricing market is the proof).
- **Distribution is hard**, writer communities are atomized (Substack, Medium, indie blogs, no central water-hole) and the founder doesn't have natural reach there.

### C5: Developer (non-code dictation) *(disqualified, easy to add later)*

**Why interesting:** highest reachability of any segment; founder reach via HN/dev-Twitter is essentially free.

**Why not:**
- **Alt friction is low**, devs type at 80–120 wpm. Voice for a commit message saves 5 seconds at most. The pain is small.
- **Aqua Voice is adjacent**, they own developer voice (for code) and would be a fast follower on adjacent dev workflows.
- **WTP is mid**, devs pay for tools but at lower price points than business users.

**When to revisit:** add a `code-context` polish profile (commit / PR / code-review) as a *feature*, not a pivot. Costs ~1 week of work; expands the C1 secondary appeal.

### C6: Second-brain capturer *(disqualified, watching for Apple risk)*

**Why interesting:** white space, Notion / Obsidian audience pays, X5 D2 candidate.

**Why not:**
- **Apple risk**, Apple Notes + Apple Intelligence will ramp up structuring features in macOS 26-27. Building this product right when Apple is investing here is a category-bet against the platform vendor.
- **Adapter sprawl**, Notion + Obsidian + Apple Notes + Bear + Day One adapters is a maintenance load that competes with the core dictation work.
- **Different audience**, second-brain users don't overlap meaningfully with bilinguals or power Slack users; this would be a true pivot, not an expansion.

**When to revisit:** if the second-brain space *fragments* (Notion losing share to Obsidian to Reflect to others) and no clear winner emerges, the integration burden actually decreases (clipboard markdown frontmatter works for all).

---

## 6. Open questions for the next research push

The discovery starter kit in memory references a Mom Test interview script. These are the questions that script should target to upgrade this ICP from desk-research to validated:

1. **For bilinguals:** "Walk me through the last time you had to write an important Slack / email at work in English. What did you actually do, tools, edits, time, anxiety?" *Listening for: number of tools used, where the time goes, what the failure modes feel like.*
2. **For bilinguals:** "How much would you pay per month for a tool that meant you could compose in $L1 and have it land in English the way a native would write it?" *Listening for: price anchor, comparison to DeepL Pro / ChatGPT subscription.*
3. **For C1 power users:** "If Wispr Flow / Superwhisper / Apple Dictation / Untype all worked equally well, which would you pick and why?" *Listening for: what's the actual decision criterion, privacy, native-feel, price, UX, brand.*
4. **For everyone:** "Can you show me what happens after you dictate something, what do you do with the output?" *Listening for: post-insert workflow, error recovery, where the tool fails.*
5. **For C2 specifically:** "Have you ever sent something at work that came out wrong because the translation tool got it wrong? What happened?" *Listening for: high-stakes incident stories, these are the *why I'd pay* stories.*

If 5–8 interviews don't surface a clear C2 daily-pain story, **revert to C1 as primary** and treat C2 as a v2 audience expansion.

---

## 7. Hooks for downstream docs

- *For P1 (Lean Canvas):* the Customer Segments block is C2 primary, C1 secondary. Problem block is "L1-to-L2 composition friction + privacy distrust of cloud-routed audio." UVP is "the dictation tool that thinks in your language." Channels are in-language YouTube + HN. Revenue is BYOK + a small managed-key tier.
- *For X1 (build-vs-extend):* C2 reinforces Shape 1 (standalone). The translation polish layer is current cloud-LLM-quality dependent; Apple FM lags 18+ months. No reason to flip shape based on this ICP.
- *For U1 (UX):* the Cleaned · Original toggle (U1 issue 1) becomes *blocking*. The translation story falls apart without it.
- *For X5 (pivot ideas):* C2 = X5 A2; C3 = X5 A3 held as v2. The brainstorm's other audience pivots (writers, second-brain, devs) are reaffirmed as not-now.

---

## 8. Rejected framings (added 2026-05-08)

A market-research doc dropped on 2026-05-08 made two recommendations that look reasonable in isolation but **contradict the wedge committed in §3**. Naming them here so they don't drift back into kit / decks / marketing copy via future doc passes.

### Reject, "Mobile-first, desktop later"
The doc closes with *"mobile + desktop later, not наоборот"* as a wedge recommendation. Untype is macOS-first by design (founder constraint, single-platform focus, native AppKit/SwiftUI integration that *is* the differentiator). The doc reflects generic ChatGPT framing of the speech-to-text category, not Untype's actual stack and capacity. Mobile is a v3+ question, not a wedge. Willow already occupies the iOS-first lane (`competitive-landscape.md` §5.8).

### Reject, "Voice keyboard for work messages" as ICP
The doc recommends a broad ICP: *founders, PMs, designers, operators, consultants, creators, non-native English speakers.* This is **less specific than what's already committed** (C2 bilingual professional, scored 23/25 in §2). Holding the bilingual-first line means rejecting the doc's "everyone who messages a lot at work" framing, even though the doc itself notes "better multilingual messy speech" as a winning angle in its own §13.

Why specificity matters: the wedge in §3 is *the* differentiator (no competitor solves L1-to-L2 composition). A broader ICP dilutes the wedge into "voice keyboard, generally", directly competitive with Wispr Flow's $700M war chest (`competitive-landscape.md` §5.8). The narrower ICP has the white space.

### Soft tension worth noticing (not rejected)
The same doc proposed mode taxonomy (chat, email, note, task, **PRD, reply**) and per-user dictionary. Untype already has profiles; PRD-mode and reply-mode are sharper opinionated-template directions worth keeping in mind for v2. Logged for the record, not actioned.
