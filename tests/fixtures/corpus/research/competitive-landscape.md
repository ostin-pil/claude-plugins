# Competitive Landscape: macOS Voice-to-Text / Voice-to-Message Tools

**Date:** 2026-04-10
**Purpose:** Map competitive landscape for Untype's "speech -> message layer" positioning
**Scope:** macOS-focused voice-to-text tools, adjacent meeting transcription, and emerging entrants

---

## 1. Competitor Profiles

### 1.1 Superwhisper

**Summary:** Privacy-first, power-user dictation app. Runs Whisper models on-device with optional cloud AI modes.

| Dimension | Details |
|-----------|---------|
| **Pricing** | Free tier (15 min trial of Pro, then limited forever). Pro: $8.49/mo or $84.99/yr. Lifetime: $249. |
| **Technology** | On-device Whisper (Nano/Fast/Pro/Ultra models). Optional cloud STT via OpenAI, Deepgram, Groq. LLM cleanup via OpenAI/Anthropic cloud. Requires Apple Silicon for local models. |
| **Text insertion** | Clipboard paste (Cmd+V via Accessibility API). Experimental keystroke injection (US QWERTY only). |
| **Distribution** | Mac App Store + direct download. Also iOS and Windows (newer, less mature). |
| **Multilingual** | 100+ languages (Whisper's language support). |
| **Target audience** | Power users, privacy-conscious professionals, developers. |
| **Key differentiators** | Custom "modes" (email mode, code mode, casual mode). Deep customization. SOC 2 Type II + HIPAA compliant. Fully offline capable. |
| **Pain points (user feedback)** | Complex setup for non-technical users. Clipboard interference with other tools (e.g., Codex). Overwhelming number of settings. Windows version lags behind Mac. |

### 1.2 Wispr Flow

**Summary:** Most polished consumer voice dictation tool. Cloud-first, cross-platform, VC-backed ($80M+ raised).

| Dimension | Details |
|-----------|---------|
| **Pricing** | Free: 2,000 words/week. Pro: $15/mo or $144/yr. Student: $10/mo. 14-day free trial. |
| **Technology** | Proprietary cloud STT. Fine-tuned Llama models on Baseten (TensorRT-LLM). Multi-step pipeline: transcription -> filler removal -> punctuation -> style adaptation. Target: <700ms end-to-end. |
| **Text insertion** | Clipboard paste with automatic restore (~500ms delay). Saves previous clipboard, pastes, restores. Large files/special formats may not be preserved. |
| **Distribution** | Direct download (wisprflow.ai). Also iOS App Store, Google Play. Mac, Windows, iOS, Android -- only tool on all four platforms. |
| **Multilingual** | Supports multiple languages but not as extensive as Whisper-based tools. |
| **Target audience** | Professionals, knowledge workers, students. Broad consumer market. |
| **Key differentiators** | **Context-aware formatting** -- auto-adjusts tone for Slack (casual) vs Gmail (professional). Cross-platform sync of dictionary, snippets, style. Best out-of-box UX. Personal dictionary and snippets. |
| **Pain points (user feedback)** | Cloud-only (no offline). Privacy concerns (audio sent to servers). "Trust gap" reports on Reddit (quality degrading post-trial). Expensive at $15/mo. Clipboard restore can fail with large/special content. |

### 1.3 MacWhisper

**Summary:** File/recording transcription tool, not real-time dictation. Whisper-based, local processing.

| Dimension | Details |
|-----------|---------|
| **Pricing** | Free tier (basic models). Pro: $29 (Gumroad) or $15/yr (App Store). Pro lifetime: ~$80. Student/journalist/nonprofit: 25% off. |
| **Technology** | OpenAI Whisper running locally on-device. No cloud dependency for basic transcription. AI cleanup available in Pro. |
| **Text insertion** | N/A -- primarily a transcription app, not a dictation/insertion tool. Outputs text to its own UI for copy/export. |
| **Distribution** | Mac App Store + Gumroad (direct has more features). |
| **Multilingual** | Whisper's full language set (99+ languages). |
| **Target audience** | Podcasters, journalists, researchers, content creators. |
| **Key differentiators** | Batch transcription, YouTube video transcription, watch folders, speaker identification. File-based workflow, not live dictation. |
| **Pain points** | Not designed for real-time dictation or text insertion. Different product category (transcription vs dictation). |

### 1.4 AudioPen

**Summary:** Voice notes -> structured text. Web-first, note-taking focused, not a system-wide dictation tool.

| Dimension | Details |
|-----------|---------|
| **Pricing** | Free: 10 notes, 3 min each. Prime: $75-99/yr. |
| **Technology** | Cloud-based. Uses OpenAI APIs for transcription and text transformation. |
| **Text insertion** | N/A -- outputs to its own app/web interface. Integrates via Webhooks/Zapier to push to other apps (8,000+ via Zapier). |
| **Distribution** | Web app, Chrome Extension, native mobile apps. No native macOS app. |
| **Multilingual** | Major global languages via OpenAI. Translation between languages. |
| **Target audience** | Note-takers, writers, content creators who think out loud. |
| **Key differentiators** | "Fuzzy thought to clear text" -- specifically designed for rambling voice notes, not dictation. Multiple writing style outputs. Rewrite/restyle existing notes. |
| **Pain points** | Not real-time. No system-wide insertion. Web-only on desktop. Limited free tier (10 notes total). |

### 1.5 Otter.ai

**Summary:** Meeting transcription and collaboration platform. Enterprise-focused, not a dictation tool.

| Dimension | Details |
|-----------|---------|
| **Pricing** | Free: 300 min/mo (30 min/conversation). Pro: $8.33-16.99/user/mo. Business: $20-30/user/mo. Enterprise: $15K-35K/yr. |
| **Technology** | Cloud-based proprietary ASR. AI Meeting Assistant with real-time transcription. |
| **Text insertion** | N/A -- meeting-specific. Outputs summaries, action items, transcripts within its own platform. |
| **Distribution** | Web app, iOS/Android apps. Integrates with Zoom, Google Meet, Teams. |
| **Multilingual** | English, French, Spanish only. |
| **Target audience** | Teams, enterprise, meeting-heavy professionals. |
| **Key differentiators** | OtterPilot auto-joins meetings, captures audio, generates summaries, extracts action items. Collaboration features (shared notes, comments). |
| **Pain points** | Limited language support (3 languages). Expensive for teams. Different use case entirely (meetings, not dictation). |

### 1.6 macOS Built-in Dictation (Apple Intelligence)

**Summary:** Free, built-in, increasingly capable. Apple Intelligence enhancements in macOS Tahoe (2025).

| Dimension | Details |
|-----------|---------|
| **Pricing** | Free (included with macOS). |
| **Technology** | On-device processing on Apple Silicon (M1+). 55% faster than Whisper in benchmarks. Apple Intelligence integration. Can work offline. |
| **Text insertion** | Native system-level text insertion. Works in any text field natively. No clipboard manipulation needed. |
| **Distribution** | Built into macOS. |
| **Multilingual** | Broad language support via system languages. |
| **Target audience** | All Mac users. |
| **Key differentiators** | Zero setup, zero cost, native integration. No accessibility permissions needed. Liquid Glass UI (macOS Tahoe). |
| **Pain points** | **Session time limits** (stops after 30-60 seconds of continuous speech). Inconsistent accuracy day-to-day. No AI text cleanup/reformatting. No custom vocabulary. No HIPAA/compliance certifications. Limited punctuation control. No context-aware formatting. |

### 1.7 Notta

**Summary:** AI note-taking and transcription platform. Meeting-focused with broader transcription capabilities.

| Dimension | Details |
|-----------|---------|
| **Pricing** | Free: 120 min/mo. Pro: $8.17-13.99/mo. Business: $16.67/user/mo. |
| **Technology** | Cloud-based ASR. AI-powered summaries and action items. |
| **Text insertion** | N/A -- outputs within its own platform. Export to Slack, Notion, or via links. |
| **Distribution** | Web app, iOS/Android, Chrome extension. Meeting bot for Zoom/Teams/Meet/Webex. |
| **Multilingual** | 58 languages for transcription, 42 for translation. Bilingual conversation capture (add-on). |
| **Target audience** | Teams, meeting-heavy professionals, multilingual organizations. |
| **Key differentiators** | Strong multilingual support. Bilingual conversation mode. Meeting bot automation. 58-language transcription. |
| **Pain points** | Meeting-focused, not a general dictation tool. Cloud-only. |

### 1.8 Emerging Entrants (2025-2026)

#### Sotto
- **Positioning:** Local AI dictation for macOS. Hotkey -> speak -> insert into any app.
- **Pricing:** One-time purchase (specific price TBD).
- **Technology:** Local Whisper models, no cloud.
- **Notable:** Very similar positioning to Untype. Privacy-first, hotkey-triggered, universal insertion.

#### Spokenly
- **Positioning:** Free, open-source-leaning, privacy-first dictation for Mac/iPhone.
- **Pricing:** Free (BYOK -- bring your own key). No account required.
- **Technology:** Local Whisper models, 100+ languages, fully offline.
- **Notable:** Developer-friendly. Open-source ethos. No signup friction.

#### Voibe
- **Positioning:** AI-powered writing from speech, on-device.
- **Pricing:** $4.90/mo, $44.10/yr, or $90 lifetime.
- **Technology:** On-device AI for structured writing from speech.
- **Notable:** Focuses on turning speech into "clean, structured writing" -- similar to Untype's cleanup concept.

#### Aqua Voice
- **Positioning:** Fast, accurate voice dictation for Mac and Windows.
- **Technology:** Understands developer syntax, libraries, frameworks.
- **Notable:** Strong developer focus. Benchmarks on technical terms.

#### Serenade
- **Positioning:** Speech-to-code engine for developers. Open-source.
- **Technology:** Purpose-built for code dictation.
- **Notable:** Different from general dictation -- specifically code-aware.

---

## 2. Comparison Matrix

| Feature | Untype (planned) | Superwhisper | Wispr Flow | MacWhisper | AudioPen | Apple Dictation | Sotto | Voibe |
|---------|-----------------|--------------|------------|------------|----------|----------------|-------|-------|
| **Real-time dictation** | Yes | Yes | Yes | Limited | No | Yes | Yes | Yes |
| **AI text cleanup** | Yes (LLM) | Yes (modes) | Yes (auto) | Pro only | Yes | No | Unknown | Yes |
| **Context-aware formatting** | Planned | Via modes | Auto (app detection) | No | No | No | No | Unknown |
| **Universal text insertion** | Yes (Cmd+V) | Yes (Cmd+V) | Yes (clipboard) | No | No (Zapier) | Native | Yes | Yes |
| **On-device STT** | Apple Speech | Whisper local | No | Whisper local | No | Yes | Whisper local | Yes |
| **Cloud STT option** | Whisper API | Yes (multiple) | Yes (only) | No | Yes (only) | Optional | No | No |
| **Offline capable** | Yes (Apple STT) | Yes | No | Yes | No | Yes (M1+) | Yes | Yes |
| **Multilingual** | Planned (EN/RU/ZH) | 100+ | Limited | 99+ | Major langs | System langs | 100+ | Unknown |
| **macOS native** | Yes (Swift) | Yes | Yes (Electron?) | Yes | No (web) | Yes | Yes | Yes |
| **Cross-platform** | No (macOS only) | Mac/Win/iOS | All four | Mac only | Web/mobile | Apple only | Mac only | Mac only |
| **Pricing floor** | TBD | Free (limited) | Free (2K words/wk) | Free (basic) | Free (10 notes) | Free | One-time | $4.90/mo |
| **Pricing ceiling** | TBD | $249 lifetime | $15/mo | $80 lifetime | $99/yr | Free | One-time | $90 lifetime |

---

## 3. Gap Analysis

### 3.1 What existing tools do well
- **Wispr Flow**: Best UX, context-aware formatting, cross-platform sync
- **Superwhisper**: Best privacy, most customizable, compliance certifications
- **Apple Dictation**: Zero friction, free, native integration
- **MacWhisper**: Best for file transcription, batch workflows

### 3.2 Gaps and unmet needs

#### Gap 1: "Message layer" -- speech shaped for the destination
Wispr Flow is the only tool that auto-adapts tone by app (Slack vs email), but it's cloud-only and $15/mo. No tool offers granular control like "reply to this Slack thread in my casual style" or "draft this as a bullet-point email." Untype can own the **message-aware** niche -- not just dictation, but intent-aware message composition.

#### Gap 2: Clipboard reliability
Every tool that inserts text (Superwhisper, Wispr Flow, Sotto) uses clipboard paste. Users consistently complain about:
- Clipboard content being destroyed (large files, images, rich text)
- Race conditions with clipboard managers
- ~500ms restore delays
- Interference with developer tools (Codex, Alfred, etc.)

Untype's `CGEvent`-based keystroke injection (planned in `TextInserter.swift`) could be a differentiator if it can reliably bypass the clipboard for plain text insertion, though the current implementation also uses clipboard + Cmd+V.

#### Gap 3: On-device AI cleanup with quality cloud fallback
Most tools are either fully local (lower quality cleanup) or fully cloud (privacy concerns). Untype's architecture (Apple Speech on-device for STT + cloud LLM for cleanup) is a pragmatic middle ground, but no tool currently does this seamlessly with user control over what goes to cloud.

#### Gap 4: Multilingual message composition
Whisper handles 100+ languages for STT, but **no tool** handles the "think in Language A, output message in Language B" workflow well. Untype's planned EN/RU/ZH support with LLM-powered translation in the cleanup step is a genuine differentiator for bilingual/trilingual professionals.

#### Gap 5: Developer-friendly voice input
Aqua Voice and Serenade target developers, but for **code-adjacent** work (commit messages, PR descriptions, Slack messages about code, documentation). No tool bridges "developer vocabulary awareness" with "message composition for non-code contexts."

#### Gap 6: Pricing gap
There's a clear gap between free (Apple Dictation, Spokenly) and $8-15/mo subscriptions (Wispr, Superwhisper). Tools like Voibe ($4.90/mo) and Sotto (one-time) are trying to fill this, but the $5-8/mo range with good AI cleanup is underserved.

#### Gap 7: Accessibility / RSI users
Voice dictation is critical for RSI sufferers, but most tools treat accessibility as a side benefit, not a primary design consideration. Session time limits (Apple), cloud dependency (Wispr), and complex setup (Superwhisper) all create barriers for users who **need** (not just want) voice input.

---

## 4. Pricing Analysis

| Tier | Examples | Price Range |
|------|----------|-------------|
| **Free** | Apple Dictation, Spokenly | $0 |
| **Freemium (limited)** | Wispr Flow (2K words/wk), Superwhisper (15 min trial) | $0 with hard caps |
| **Budget subscription** | Voibe ($4.90/mo) | $4-6/mo |
| **Mid-tier subscription** | Notta Pro ($8/mo), Superwhisper ($8.49/mo) | $8-10/mo |
| **Premium subscription** | Wispr Flow Pro ($15/mo) | $12-17/mo |
| **Lifetime** | Voibe ($90), MacWhisper Pro ($29-80), Superwhisper ($249) | $29-249 one-time |
| **Enterprise** | Otter, Notta Business | $20-30/user/mo |

**Price ceiling:** $15/mo (Wispr Flow) for individual users. Above this, users expect enterprise features.
**Price floor:** Free tools (Apple Dictation, Spokenly) set a baseline that any paid tool must clearly exceed.
**Sweet spot for Untype:** $6-10/mo subscription or $79-129 lifetime. Must clearly beat Apple Dictation and justify cost vs Wispr Flow.

---

## 5. Retention Drivers

Based on user feedback patterns, tools with the best retention share these traits:

1. **Muscle memory / hotkey habit** -- Once users build the hotkey -> speak -> done habit, switching cost is high. Superwhisper and Wispr Flow both benefit from this.
2. **Accuracy that improves over time** -- Wispr Flow's personal dictionary and style learning create lock-in. Users who invest in training the tool are reluctant to leave.
3. **Cross-app reliability** -- Tools that work everywhere (not just some apps) retain better. Insertion failures in specific apps are the #1 churn driver.
4. **Speed** -- Sub-second end-to-end latency is table stakes. Any perceptible delay breaks the flow state and drives users back to typing.

---

## 6. Positioning Recommendations for Untype

### 6.1 Primary positioning: "The message layer that speaks your language"

Untype should own the intersection that no competitor fully occupies:
- **Message-aware** (not just dictation) -- understands you're composing a Slack reply, an email, a commit message
- **Multilingual-native** -- think in one language, output in another
- **Privacy-pragmatic** -- on-device STT, cloud only for LLM cleanup (with transparency)
- **Native macOS** -- not Electron, not a web wrapper, genuinely integrated

### 6.2 Differentiation axes

| Axis | Untype advantage | Key competitor |
|------|-----------------|----------------|
| Message-awareness | Intent-driven cleanup ("make this a Slack reply" vs "make this an email") | Wispr Flow (auto-detects app, but no user control) |
| Multilingual composition | Think in RU/ZH, output in EN (or vice versa) with cultural-aware formatting | Superwhisper (100+ STT languages, but no composition-level translation) |
| Native macOS integration | Swift/AppKit, non-activating NSPanel, no Electron bloat | Wispr Flow (likely Electron), Superwhisper (native but heavy) |
| Transparency | User sees and can edit the AI cleanup before insertion | Most tools auto-insert without preview |
| Lightweight | Single slim bar above dock, minimal footprint | Superwhisper (feature-heavy UI), Wispr Flow (cross-platform overhead) |

### 6.3 What NOT to compete on

**Strategic non-targets** (whole categories Untype deliberately doesn't enter):

- **Cross-platform** -- Untype is macOS-only by design. Don't apologize for this; it enables the native integration that is the differentiator.
- **Offline-everything** -- Apple Speech for STT is on-device, but LLM cleanup requires cloud. Be transparent about this trade-off rather than pretending to be fully offline.
- **Enterprise/compliance** -- Superwhisper owns SOC 2/HIPAA. Don't chase this initially.
- **Meeting transcription** -- Otter and Notta own this. Untype is for composing messages, not transcribing meetings.

**Feature-claim baseline (commodities)**: Marketing/decks/UX claims that are *not* differentiators in 2026. Every credible competitor has these. Saying any of them is the headline reads as "I have nothing better to say":

- "95%+ transcription accuracy"
- "Supports 100+ languages"
- "Meeting summaries / action items"
- "Speaker diarization"
- "Export to Notion / Google Docs / Slack"
- "Powered by Whisper"
- "AI improves your grammar"
- "Faster than typing"

The user pays for **confidence-before-send** (the polished output is shippable as-is), not for hitting any of the above. When tempted to write copy or ship a feature whose pitch is on this list, stop and find a confidence-before-send angle instead.

(Lifted from a co-founder market doc 2026-05-08; the canonical list was implicit/scattered in repo before.)

### 6.4 Underserved niches to target

1. **Multilingual professionals** -- Bilingual/trilingual knowledge workers who switch between languages in their daily communication. No tool handles "I'll think in Russian and you write the Slack message in English" well.
2. **Developers (non-code contexts)** -- PR descriptions, commit messages, Slack discussions about code, documentation. Not voice coding (Serenade owns that), but voice-driven developer communication.
3. **RSI/accessibility users** -- Users who need reliable, low-friction voice input as a primary input method. The slim overlay, hotkey activation, and reliability are critical for this audience.
4. **Privacy-conscious professionals** -- Lawyers, therapists, executives who need voice input but won't send audio to cloud. On-device STT with optional cloud cleanup (text only, not audio) is a compelling pitch.

### 6.5 Recommended pricing strategy

- **Free tier:** Unlimited Apple Speech STT (on-device, no cost to Untype). No AI cleanup. Proves the insertion and overlay UX.
- **Pro tier ($7-9/mo or $79 lifetime):** AI cleanup via cloud LLM. Multilingual composition. Custom prompt templates. Undercuts Wispr Flow ($15/mo) while exceeding Apple Dictation.
- **Future consideration:** Usage-based pricing for heavy LLM users, or BYOK (bring your own API key) as an enthusiast option.

---

## 7. Key Takeaways

1. **Wispr Flow is the primary competitor** -- closest to Untype's "message layer" vision, but cloud-only, expensive, and Electron-based. Untype can win on native feel, privacy, and price.

2. **Superwhisper is the secondary competitor** -- strong privacy story and customization, but complex UX and not "message-aware." Untype can win on simplicity and the message-layer concept.

3. **Apple Dictation is the real baseline** -- it's free, built-in, and getting better. Untype must provide obvious value above this (AI cleanup, multilingual, message formatting) to justify any price.

4. **The market is fragmenting rapidly** -- Sotto, Voibe, Spokenly, Aqua Voice all launched in 2025-2026. The window to establish positioning is narrow. Ship fast, nail the core UX, expand later.

5. **"Speech -> message layer" is genuinely underserved** -- most tools stop at transcription or basic cleanup. The concept of understanding the user's *communication intent* (reply to a thread, compose an email, write a commit message) and formatting accordingly is Untype's unique angle.

6. **Clipboard-based insertion is a universal pain point** -- every competitor uses it, every competitor has complaints about it. If Untype can reliably use CGEvent keystroke injection as a primary method (with clipboard as fallback), this alone could be a differentiator.

---

## 5. April 2026 Update (added 2026-04-19)

Follow-up scan after the initial 2026-04-10 landscape. Focus: what's shifted in a week, and what new reviewer/user signal showed up.

### 5.1 The "trust gap" narrative has gone mainstream

Ryan Shrott's "Wispr Flow Trust Gap" piece (Medium, Feb 2026) and related Reddit threads crystallised a concrete grievance: users report the app works well during the 14-day trial then degrades visibly after billing kicks in -- "60% of the time" accuracy, freezes that lock up both Wispr and the target app, fans spinning while idle. The legal-language complaint around screenshot-based "context capture" compounded it.

Product implication for Untype: reliability, transparency, and "showing your work" are now active differentiators, not hygiene. Concrete UX levers:

- Proof-of-life feedback during every phase (mic level, streaming tokens, insertion progress)
- Explicit retry affordances on transient errors rather than just "Esc to dismiss"
- User-visible routing ("on-device · cloud polish · local fallback") so the privacy story is legible
- No screenshot-based context pipeline -- use Accessibility text extraction only

### 5.2 Modes are now table stakes

The April 2026 cohort (Superwhisper, FluidVoice, Hush Touch, Spokenly, VoiceInk) all ship task-specific modes: `Voice to text / Message / Mail / Note / Meeting / Code / Prompt`. Per-app auto-switch via Accessibility is standard. One reviewer (afadingthought Substack) reports running 21 custom prompts in parallel in Superwhisper.

**Key UX insight from that review**: *workflow integration* beats *model quality* -- STT and LLM are commodities, but mode-switching friction, reprocess ergonomics, and settings organization are what users comparison-shop on.

VoiceInk was singled out as having a clumsy history/reprocess flow ("start recording, switch mode, cancel, open history") -- a warning that even shipping the feature doesn't win; the interaction has to be clean.

### 5.3 Context awareness has three standard layers

Superwhisper's public docs now describe three explicit context sources:

1. **Selected text** captured at dictation start
2. **Clipboard** captured during dictation (3s window around the hotkey press, to avoid pollution)
3. **Frontmost-app context** captured after transcription via Accessibility

All three are text-only -- no screenshots. This is the privacy-respecting pattern to copy if Untype pursues conversation-aware composition.

### 5.4 New and sharpened entrants

- **FluidVoice** (altic-dev, open source, active releases): added **Cohere Transcribe** as a new STT option (noted for punctuation/number accuracy) and **Parakeet Flash** beta for low-latency English-only local streaming. Indicates Whisper is no longer the only on-device choice.
- **Pipit** (pipitvoice.com): overlay-centric positioning -- hotkey releases to paste into active app. Similar shape to Untype.
- **Aqua Voice** (aquavoice.com): specialising in developer workflows, ~$100/yr. Parallel track to Untype but narrower audience.
- **VoiceInk**: Superwhisper-adjacent, lower price, weaker UX on reprocess.
- **Apple Dictation (macOS Tahoe)**: still no confirmed removal of the 30-60s session limit. Still no custom vocabulary. Still the primary reason users seek third-party tools.

### 5.5 Pricing baseline has settled

| App | Monthly | Annual | Lifetime |
|-----|---------|--------|----------|
| Wispr Flow Pro | $15 | $144 | — |
| Superwhisper Pro | $8.49 | $84.99 | $249.99 |
| MacWhisper Pro | — | $15 (MAS) / $29 (Gumroad) | ~$80 |
| Aqua Voice | ~$8.33 | $100 | — |
| Pipit | subscription tiers | — | — |

Untype's earlier recommendation ($6-10/mo or $79-129 lifetime) still sits correctly between Wispr and Apple Dictation.

### 5.6 Under-exploited differentiator angles (white space in April 2026)

Updated from the April 10 version:

1. **Conversation-aware composition** (read the thread via Accessibility before dictating) -- no mainstream competitor ships this as a first-class flow. Wispr's screenshot approach is actively causing them grief.
2. **Multilingual cross-composition** (speak L1, output L2) -- matches Untype product memo Tier 2. Unclaimed.
3. **Reply-aware tone** (short/conversational when in a reply context, full/structured in a blank composer) -- unclaimed.
4. **Reliability-forward UX** (proof-of-life, retry, visible routing) -- positioning that the trust-gap narrative has made load-bearing.
5. **Inline edit + STT alternates popover** from `SFTranscription.segments[].alternativeSubstrings` -- Apple framework hands them to us for free; competitors force re-dictate instead.
6. **Voice commands inline** ("new paragraph", "delete that", "quote") -- Apple Voice Control has them; dictation-overlay category is empty.
7. **Native-lightweight as a surfaced claim** (factual RAM, launch time) -- Electron fatigue is real; native Swift is invisible today.

### 5.8 Funding update (added 2026-05-08)

Recent rounds shifting competitive intensity. All four verified against primary sources (TechCrunch, company press, Bloomberg) on 2026-05-08:

| Player | Round | Date | Amount | Valuation | Lead | What it changes |
|---|---|---|---|---|---|---|
| Deepgram | Series C | 2026-01-13 | $130M | $1.3B (unicorn) | AVP | Voice AI infra layer is now well-capitalised; commodity floor for STT API quality keeps falling. |
| Wispr Flow | Series A + extension | 2025-06 + 2025-11 | $30M + $25M = $81M total | ~$700M post-money | Menlo Ventures (A) / Notable Capital (extension) | Wispr is the category leader they think they're funding. War-chest for cross-platform expansion + retention work after the trust-gap narrative. |
| Willow | Seed | 2025 | $4.5M | n/d | Box Group / YC / Burst Capital | iOS-first voice keyboard (not macOS) — launched Nov 2025, 50% MoM user growth, enterprise pilots at Uber/Heidi Health/Zego. Adjacent, not direct macOS competitor — but proves the "keyboard replacement" thesis on mobile. |
| Granola | Series C | 2026-03-25 | $125M | $1.5B (6x jump from $250M) | Index Ventures (Danny Rimer) | Pivoted from prosumer notetaker to enterprise AI app (Spaces, APIs). Confirms meeting-assistant adjacent space is **not** Untype's lane — Granola has the war chest to dominate it. |

**So-what for Untype**:
- Wispr's $700M valuation + retention war chest means the trust-gap window is closing — competitive pressure on reliability claims goes up, not down.
- Deepgram unicorn round = cheap, fast STT API competition keeps intensifying. Reaffirms the call to *not* compete on STT quality alone.
- Willow on iOS validates the cross-app keyboard thesis but stays mobile-first; macOS is uncontested by Willow specifically.
- Granola's enterprise pivot reinforces "don't compete on meetings."

Sources: [Deepgram press release](https://deepgram.com/learn/press-release-deepgram-raises-series-c) · [Wispr — Notable Capital extension (TechCrunch, 2025-11-20)](https://techcrunch.com/2025/11/20/as-its-voice-dectation-app-takes-off-wispr-secures-25m-from-notable-capital/) · [Wispr — Series A (TechCrunch, 2025-06-24)](https://techcrunch.com/2025/06/24/wispr-flow-raises-30m-from-menlo-ventures-for-its-ai-powered-dictation-app/) · [Willow launches iOS keyboard (TechCrunch, 2025-11-12)](https://techcrunch.com/2025/11/12/willows-voice-keyboard-lets-you-type-across-all-your-ios-apps-and-actually-edit-what-you-said/) · [Granola Series C (TechCrunch, 2026-03-25)](https://techcrunch.com/2026/03/25/granola-raises-125m-hits-1-5b-valuation-as-it-expands-from-meeting-notetaker-to-enterprise-ai-app/)

---

### 5.7 New sources (April 2026 update)

- [afadingthought — True Differentiators in AI Dictation (2026)](https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac)
- [Ryan Shrott — Wispr Flow Trust Gap (Medium, Feb 2026)](https://medium.com/@ryanshrott/the-wispr-flow-trust-gap-why-reliability-matters-more-than-hype-in-2026-c7dd55392408)
- [Ryan Shrott — Why I Cancelled My Wispr Flow Subscription (Medium)](https://medium.com/@ryanshrott/why-i-cancelled-my-wispr-flow-subscription-and-what-im-using-instead-d783433f4411)
- [Superwhisper — Modes docs](https://superwhisper.com/docs/modes/modes)
- [Superwhisper — Context awareness tips (WhisperClip)](https://whisperclip.com/blog/posts/superwhisper-power-tips-default-modes-hotkeys-and-context-awareness)
- [FluidVoice releases (GitHub)](https://github.com/altic-dev/FluidVoice/releases)
- [Pipit voice](https://www.pipitvoice.com/)
- [Voibe — Wispr Flow alternatives (2026)](https://www.getvoibe.com/blog/wispr-flow-alternatives/)
- [Voibe — Superwhisper alternatives (2026)](https://www.getvoibe.com/blog/superwhisper-alternatives/)
- [WhisperClip comparison (2026)](https://whisperclip.com/blog/posts/whisperclip-vs-superwhisper-wisprflow-macwhisper-which-ai-dictation-fits-your-workflow)
- [Filip Konecny — Wispr Flow pros and cons (Mar 2026)](https://filipkonecny.com/2026/03/25/wispr-flow-pros-and-cons/)

---

## Sources

- [Superwhisper](https://superwhisper.com/)
- [Wispr Flow](https://wisprflow.ai)
- [Wispr Flow Pricing](https://wisprflow.ai/pricing)
- [Wispr Flow on Baseten (architecture)](https://www.baseten.co/resources/customers/wispr-flow/)
- [Wispr Flow text insertion docs](https://docs.wisprflow.ai/articles/7971211038-fix-text-not-pasting-after-dictation)
- [MacWhisper (Gumroad)](https://goodsnooze.gumroad.com/l/macwhisper)
- [AudioPen](https://www.audiopen.ai/)
- [Otter.ai Pricing](https://otter.ai/pricing)
- [Notta Pricing](https://www.notta.ai/en/pricing)
- [Sotto](https://sotto.to)
- [Spokenly](https://spokenly.app/)
- [Voibe alternatives](https://www.getvoibe.com/blog/superwhisper-alternatives/)
- [Aqua Voice](https://aquavoice.com)
- [Serenade](https://serenade.ai/)
- [Superwhisper vs Wispr Flow comparison](https://www.getvoibe.com/resources/wispr-flow-vs-superwhisper/)
- [Superwhisper clipboard interference issue](https://github.com/openai/codex/issues/11103)
- [macOS Tahoe dictation features](https://weesperneonflow.ai/en/blog/2025-10-27-voice-dictation-macos-tahoe-native-features-third-party-apps-2025/)
- [Speakmac vs Superwhisper pricing](https://www.speakmac.app/blog/speakmac-vs-superwhisper-comparison)
- [Developer dictation tools guide](https://lumevoice.com/blog/best-ai-dictation-tools-for-developers-2026/)
- [RSI software tools](https://usevoicy.com/blog/best-software-tools-for-rsi)
- [Best dictation software for Mac 2026](https://machow2.com/best-dictation-software-mac/)
