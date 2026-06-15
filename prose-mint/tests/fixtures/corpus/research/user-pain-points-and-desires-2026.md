# User Pain Points & Desired Features — macOS Dictation Competitors

**Date:** 2026-04-18
**Purpose:** Layer user-voice evidence (complaints, feature requests, churn reasons) onto the structural competitive map in `research/competitive-landscape.md`, so Untype's positioning and Tier‑1/2/3 priorities are validated against what competitor users are actively frustrated by — not just what competitors offer.
**Scope:** 5 direct competitors (Wispr Flow, Superwhisper, VoiceInk, Aqua Voice, MacWhisper) + 3 new entrants (Spokenly, Sotto, Voibe).
**Date range mined:** Jan 2025 – Apr 2026.
**Next refresh due:** 2026-07 (quarterly; sooner if a major competitor ships a new version or privacy incident).

## Methodology & Caveats

- **Sources mined:** Mac App Store reviews (1★ / 3★ focus), Hacker News launch threads and comments, Product Hunt launch threads and reviews, Trustpilot, GitHub Issues (for open-source competitors), Superwhisper changelog, Substack/blog first-hand reviews (Danny Smith, samwize, afadingthought), 9to5Mac, TidBITS, Simon Willison.
- **Reddit signal is second-hand.** Web fetchers were blocked from reddit.com during mining. Every "Reddit says …" claim below is routed through an aggregator (Resonant, afadingthought, Voibe's SEO pages). Treat Reddit frequency numbers as "reviewer reports this is common" rather than verified thread counts.
- **Affiliate pollution is heavy.** Voibe, Resonant, DictaFlow (Ryan Shrott), Letterly and others publish comparison pieces that promote their own product. Their raw quotes are usable as *evidence of user complaints*, but their framing is not neutral and is flagged inline.
- **Selection bias.** Product Hunt reviews skew 5★. The *ratings* say "no complaints"; the *review bodies* contain the complaints. All PH pain points below come from review *bodies*, not star counts.
- **Sotto has no independent user voice.** Every public source about Sotto is seller-authored. Its section is short by necessity and itself a data point.

## 1. Per‑Competitor Inventory

### 1.1 Wispr Flow

**Signal strength:** very high. Trustpilot page (2.7 / 5), Product Hunt reviews, an incident-driven LinkedIn/Reddit wave in 2025, Wispr's own public StatusPage and docs.

**Top pain points**

| # | Complaint | Evidence | Frequency |
|---|---|---|---|
| 1 | **Post-trial reliability drop.** Works during free trial, accuracy and uptime fall after card is charged. One reviewer: "works great about 60% of the time." Paid-annual user locked out of login, no response. | [Trustpilot](https://www.trustpilot.com/review/wisprflow.ai); [Voibe comparison](https://www.getvoibe.com/resources/wispr-flow-vs-superwhisper/) *(affiliate)*; [Feb‑2026 Medium "Trust Gap"](https://medium.com/@ryanshrott/the-wispr-flow-trust-gap-why-reliability-matters-more-than-hype-in-2026-c7dd55392408) *(affiliate — promotes DictaFlow)* | **Dominant** — recurring across Trustpilot and 3+ aggregators; 2.7/5 overall Trustpilot |
| 2 | **Privacy / screenshot-capture scandal.** 2025 Reddit disclosure: Wispr captured screenshots of the focused window every few seconds and sent them to cloud (incl. third-party models). CTO apologised; "Privacy Mode" added; audio still cloud-only by architecture. | [eesel deep dive](https://www.eesel.ai/blog/wispr-flow-review); [Letterly review](https://letterly.app/blog/wispr-flow-review/); [LinkedIn PSA — Nathan Grzesiek](https://www.linkedin.com/posts/nathan-grzesiek_psa-for-lennys-newsletter-fans-if-activity-7361833247258890240-RhNl); Product Hunt reviews | **Very high** — cited in 6+ distinct pieces, still referenced as a switch trigger 6+ months later |
| 3 | **Electron resource hog + target-app freezes (Windows worst, Mac noticeable).** ~800 MB RAM, 8 % idle CPU, fans audible, 8–10 s startup. Freezes lock up VS Code / Notepad++. Microsoft Store build "just crashes." | [Product Hunt](https://www.producthunt.com/products/wisprflow/reviews); [Trustpilot](https://www.trustpilot.com/review/wisprflow.ai); [samwize review](https://samwize.com/2025/11/10/review-of-whispr-flow-superwhisper-macwhisper-for-vibe-coding/); [eesel](https://www.eesel.ai/blog/wispr-flow-review) | **High.** Windows-biased, but the "Electron bloat" framing is used as a reason to prefer native Mac tools |
| 4 | **Unresponsive support.** Weeks of silence after bot replies; no replies to App Store reviews; payment / login tickets unanswered. | [Trustpilot](https://www.trustpilot.com/review/wisprflow.ai) multiple reviews, Product Hunt | Consistent pattern across several reviews |
| 5 | **Hallucinated / auto-edited output.** Cloud LLM "polish" sometimes rewrites content unfaithfully; self-correction fails unpredictably. One reviewer: iOS is "pre-alpha / abysmal." | [Trustpilot](https://www.trustpilot.com/review/wisprflow.ai); [Voibe](https://www.getvoibe.com/resources/wispr-flow-vs-superwhisper/) *(affiliate)* | Moderate |

**Top desired features**
- **Offline / on-device mode.** "Best UI, but I don't want my voice in the cloud" — aggregated across [Resonant's Reddit roundup](https://www.onresonant.com/resources/best-dictation-tools-mac-reddit) and [afadingthought](https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac). Dominant privacy-segment ask.
- **Better math / code / technical-notation handling.** PH review asking for customisable math-symbol conversion.
- **VPN / enterprise-network compatibility.** Frequent enough that Wispr published an [official help article](https://docs.wisprflow.ai/articles/3834764683-why-vpns-or-security-tools-can-block-wispr-flow); corroborated by [Jan-2026 slow-performance incident](https://statuspage.incident.io/wispr-flow/incidents/01KFH1SEDXQSREP1CHMPXVHR47).

**Churn / switch‑away reasons**
- Privacy (screenshots + cloud audio routing) — top switch trigger across LinkedIn PSAs, afadingthought, multiple listicles.
- Post-payment reliability drop + poor support — Trustpilot pattern.
- $144 / yr cost vs. one-time alternatives — samwize, freeflow HN thread.
- Electron bloat on Windows (dev audience; less relevant to Untype's Mac-only scope, but defines the "native Swift" pitch).

### 1.2 Superwhisper

**Signal strength:** high. 4.9★ PH / 4.4★ App Store — retention is strong, but complaint bodies are specific and consistent. First-hand sources: samwize, afadingthought, Superwhisper's own public changelog (implicit bug history).

**Top pain points**

| # | Complaint | Evidence | Frequency |
|---|---|---|---|
| 1 | **Onboarding / settings complexity.** "Configuring a server, not installing an app." Modes, prompts, models, shell triggers crammed into dense Advanced tabs. Mode settings and Recording Window buried. | [samwize](https://samwize.com/2025/11/10/review-of-whispr-flow-superwhisper-macwhisper-for-vibe-coding/); [afadingthought](https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac); [Voibe](https://www.getvoibe.com/resources/wispr-flow-vs-superwhisper/) *(affiliate)*; PH AI summary | **Dominant** — 4+ distinct first-hand / summary sources; "overwhelming for new users" is the recurring phrase |
| 2 | **Unreliable hotkey / mode activation.** "Sometimes it doesn't catch my key binding or fails to activate dictation." Custom modes don't auto-revert when app focus changes. | samwize; [PH review 5 mo ago](https://www.producthunt.com/products/superwhisper/reviews); afadingthought | 3 distinct first-hand mentions |
| 3 | **Feature regressions that strip customization.** Ability to reprocess dictations with captured app context was **removed without warning**; dev initially denied it existed. Mini recording window now auto-closes, breaking assistant-style workflows. Mode-switch notifications added with no disable toggle. "Chasing a kind of 'simple' that doesn't fit where it started." | [afadingthought](https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac) — detailed first-hand | Single very detailed source; weighted for depth |
| 4 | **Support responsiveness.** "If you hit a bug, you're on your own unless many users have it." One aggregator cites 93.5 % of 476 feedback-board tickets unaddressed as of April 2026 (I could not verify — feedback.superwhisper.com returned 403). | [Voibe](https://www.getvoibe.com/resources/wispr-flow-vs-superwhisper/) *(affiliate — unverified number)*; afadingthought | Unverified but qualitatively consistent |
| 5 | **iOS polish / data loss.** Mobile "less polished than desktop"; iOS "plagued by recording loss." iCloud sync loses custom modes. First-words missing in Scribe real-time mode (fixed in 2.9.0). Long-recording / audio-device crashes (fixed in 2.10 – 2.12). | [PH reviews](https://www.producthunt.com/products/superwhisper/reviews); afadingthought; [Superwhisper changelog](https://superwhisper.com/changelog) | Pattern confirmed by changelog fixes |

**Top desired features**
- **Cross-device sync for modes / prompts / vocab / replacements.** Active roadmap item; iCloud sync bugs documented in troubleshooting docs.
- **Programmatic / API / MCP control of vocabulary.** Power-user feature-board request.
- **Cleaner default UX / guided onboarding.** Implied by every complexity complaint. afadingthought argues the dev is addressing this *wrong* — removing customization instead of layering progressive disclosure.

**Churn / switch‑away reasons**
- Too tinker-y → users move to Wispr Flow or Willow / Voibe for "just works."
- $249 lifetime too expensive → freeflow / VoiceInk / Whispering (Show HN threads).
- Feature removed in update → afadingthought explicitly left over stripped customization.

### 1.3 VoiceInk

**Signal strength:** strong. Active open-source repo ([`Beingpax/VoiceInk`](https://github.com/Beingpax/VoiceInk), 187+ open issues), Mac + iOS App Store presence, HN threads, comparison reviews. GitHub Issues are the clearest primary signal in the entire set.

**Top pain points**

| # | Complaint | Evidence | Frequency |
|---|---|---|---|
| 1 | **Idle CPU / energy regressions (multiple distinct bugs, active Apr 2026).** App pegs a core with no recording active; restart doesn't help. | [Issue #634 — 100 % CPU idle](https://github.com/Beingpax/VoiceInk/issues/634); [#642 MediaRemoteAdapter busy-loop](https://github.com/Beingpax/VoiceInk/issues/642); [#645 NLTagger main-thread hang](https://github.com/Beingpax/VoiceInk/issues/645); [#546 running hot during file transcription](https://github.com/Beingpax/VoiceInk/issues/546) | **Pattern** — 4 distinct idle/CPU issues open in a 60-day window |
| 2 | **Transcription reliability flakiness.** First attempt after wake fails ("Unable to compute async prediction using ML Program"); second works. Paste sometimes doesn't land. Indefinite stalls on long files. | [#614 fails 1st-message after idle](https://github.com/Beingpax/VoiceInk/issues/614); [#646 clipboard paste inconsistent](https://github.com/Beingpax/VoiceInk/issues/646); [#321 stalls during transcription — Intel workaround "use cloud"](https://github.com/Beingpax/VoiceInk/issues/321); [Danny Smith notes](https://danny.is/notes/voiceink/) ("loses first or last word of dictation") | High — GitHub + blog corroboration |
| 3 | **Wrong-language detection by default; no whitelist.** Parakeet local model auto-detects and gets it wrong. User: "Polish being detected as Russian" — wants a language whitelist. | [#518 language whitelist request](https://github.com/Beingpax/VoiceInk/issues/518); [afadingthought](https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac); [iOS companion App Store review, Sept 2025](https://apps.apple.com/us/app/voiceink-ai-dictation/id6751431158) ("always converts to English any language") | High — multiple channels |
| 4 | **Paste pipeline fragile across apps / layouts.** Parsec fails; Dvorak breaks paste; "Add space after paste" toggle inconsistent (works on Whisper Large v3 but not Parakeet v2). | [#635 Parsec](https://github.com/Beingpax/VoiceInk/issues/635); [#597 Dvorak](https://github.com/Beingpax/VoiceInk/issues/597); [#535](https://github.com/Beingpax/VoiceInk/issues/535); [#625](https://github.com/Beingpax/VoiceInk/issues/625) | 4 distinct issues |
| 5 | **Power Modes / AI Enhancement UX friction.** Overlapping "AI enhancements" vs "power modes" terminology. Can't start dictating straight into a specific mode via shortcut / deep link; must switch mid-recording with Cmd/Opt+number (capped at 10). "Custom AI prompting is actually just for text reformatting; only one dedicated AI assistant prompt." | [afadingthought](https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac); [#641 one-shot per-recording enhancement](https://github.com/Beingpax/VoiceInk/issues/641); [#650 mode-per-app persistence bug](https://github.com/Beingpax/VoiceInk/issues/650) | Substantive — review + 2 issues |

**Top desired features**
- **Apple Foundation Models for cleanup** — users want free on-device LLM cleanup instead of bringing an OpenAI / Anthropic / Gemini key. [Issue #333](https://github.com/Beingpax/VoiceInk/issues/333).
- **Better local multilingual model** — SenseVoice ([#599](https://github.com/Beingpax/VoiceInk/issues/599)), Qwen-ASR ([#617](https://github.com/Beingpax/VoiceInk/issues/617)), Voxtral Realtime ([#534](https://github.com/Beingpax/VoiceInk/issues/534)). Theme: Parakeet is fast but English-biased; Whisper is slow; users want a middle option.
- **Richer context awareness (not just OCR of screenshot).** Substack review calls current screenshot+OCR "very limiting" vs. Superwhisper's selected-text + clipboard + app-context.
- **Flexible PTT / hotkey bindings.** [#647 any single key as PTT](https://github.com/Beingpax/VoiceInk/issues/647); HN commenter oulipo wants right-shift both tap-and-hold and tap-toggle.

**Churn / switch‑away reasons**
- **Intel Macs evicted.** Maintainer's own workaround for issue #321 is "use a cloud model" — effectively locks Intel-Mac users out of VoiceInk's local-first value prop.
- **→ Wispr Flow for cross-platform.** Danny Smith + AlternativeTo reviewers cite Mac-only as reason to move.
- **→ Superwhisper for richer prompting.** afadingthought landed on Superwhisper for multi-prompt workflows.

### 1.4 Aqua Voice

**Signal strength:** moderate-to-weak on direct complaints. PH reviews uniformly 5★ with complaint-shaped bodies. No Trustpilot page. Reddit blocked for direct fetching. HN launch threads are densest primary source.

**Top pain points**

| # | Complaint | Evidence | Frequency |
|---|---|---|---|
| 1 | **Cloud-only architecture.** Privacy-conscious users and accessibility users say local is non-negotiable; data going to OpenAI is a hard no. Connectivity errors require full quit/restart. A 20-minute server outage is documented. | [HN 43634005 Aqua Voice 2 launch](https://news.ycombinator.com/item?id=43634005) — fxtentacle, pbowyer, canada_dry, FloatArtifact, emacsen, waveringana; [PH reviews](https://www.producthunt.com/products/aqua/reviews) — Kamil Debbagh, Alexander Williams; [9to5Mac Aug 2025](https://9to5mac.com/2025/08/15/aqua-voice-shows-just-how-good-mac-dictation-could-be-if-apple-just-tried/) | **Dominant** — 6+ HN users, 3+ PH reviewers, 1 published review |
| 2 | **Background-noise pickup in shared spaces.** Transcribes TV, radio, nearby voices. AirPods + background music breaks sandbox. | [Voibe Aqua alternatives](https://www.getvoibe.com/blog/aqua-voice-alternatives/) *(affiliate)*; HN bklyn11201 | Recurring |
| 3 | **Paste reliability on long blocks.** "Long text block does not get pasted correctly after I finish" — reviewer falls back to clipboard-history copy/paste. Shortcut doesn't always respond; failure rate ~5–10 % by user estimate. | PH reviewer Jake Crump (Oct 2025); HN 43634005; PH Kye Burchard "99 % reliability" (Feb 2026, framed positively but reveals the gap) | 3 distinct primary sources |
| 4 | **Voice-as-composition doesn't fit everyone.** Dictation as primary composition mode breaks when thoughts require pausing / revising. Tab-away loses cursor position. Homophones ("two" / "to"); Scottish accent misrecognized. | [HN 39828686 Aqua original launch](https://news.ycombinator.com/item?id=39828686) — adamesque, SCdF, noahjk, Tistron, gleb, GordonS | Multiple commenters, single thread |
| 5 | **Pricing / trial friction.** Free tier ≈ 1 000 words (~5 min demo). $8–10 / mo, annual-only on discounted tier. Chargeback SEO content exists (joinchargeback.com). | HN ForrestN, toddmorey, replete, Merik; [Voibe Aqua vs Wispr](https://www.getvoibe.com/resources/aqua-voice-vs-wispr-flow/) | Recurring in HN |

**Top desired features**
- **Offline / on-device mode** — most-requested across every source. PH (Kamil Debbagh, Alexander Williams); HN (multiple).
- **iOS / mobile app** — PH (Francis Greenleaf, Pedro Pizarro, Alex Appelbe); HN alxlu (per-app hotkey routing).
- **Whisper / quiet-voice mode** for dictating around others — PH Rajiv Ayyangar, directly tied to the background-bleed problem.
- (runner-up) Linux client — HN emacsen, aminsadeghi; PH Eric Johansson.

**Churn / switch‑away reasons**
- Privacy / offline requirement → MacWhisper, VoiceInk, BetterDictation (all cited explicitly by HN commenters).
- Connectivity reliability (Aqua outage cost productivity).
- Cost — $96 / yr vs. $39 one-time VoiceInk / $99 Voibe lifetime.

### 1.5 MacWhisper

**Signal strength:** thick. Multi-year review history across Gumroad / Trustpilot, Mac App Store (stripped "Whisper Transcription" SKU), HN, in-app voting board. **Caveat:** MacWhisper is a *file / recording transcription* tool, not live dictation — its pain points are a different genre, and the most useful signal for Untype is the *absence* of live dictation and user requests for it.

**Top pain points**

| # | Complaint | Evidence | Frequency |
|---|---|---|---|
| 1 | **Hallucination loops and dropped audio on long files.** "Spirals into endless loops, repeating the same sentence dozens of times; entire portions of the recording are simply ignored." "Remove duplicated segments" toggle doesn't work. | [Trustpilot 1★ D. Nieuwal, 28 Nov 2025](https://www.trustpilot.com/review/macwhisper.helpscoutdocs.com); [HN 37228821 — nafizh](https://news.ycombinator.com/item?id=37228821) | Most-cited 2025 complaint |
| 2 | **Speaker diarization / non-English weakness.** Dutch recognized as another language after update; German-Dutch mix-up. Diarization is the #1 voted feature in-app, partially shipped Nov 2025 via Pyannote. | [App Store NL 1★ flashkiddy (Jul 2025)](https://apps.apple.com/nl/app/whisper-transcription/id1668083311); 1★ happycrew (Nov 2024); [whisper.cpp discussion #420](https://github.com/ggml-org/whisper.cpp/discussions/420); [Simon Willison Nov 2025](https://simonwillison.net/2025/Nov/18/macwhisper-speaker-recognition/) | Dominant non-English complaint |
| 3 | **No real-time / live dictation.** Users explicitly ask the product to grow into this category; product does not. | HN uger and repeated asks in roadmap; [Resonant Reddit roundup](https://www.onresonant.com/resources/best-dictation-tools-mac-reddit) routes dictation users to Superwhisper / Voibe | Recurring — *this is Untype's opening* |
| 4 | **Intel Mac performance.** Developer on HN: "Not well with Intel Macs unfortunately." | [HN bonney_io → nchudleigh](https://news.ycombinator.com/item?id=37228821) | Single direct admission |
| 5 | **UI friction editing multi-speaker output.** "UI for dealing with multiple speakers is a bit cumbersome; occasional crashes." Corroborated by [TidBITS Feb 2025](https://tidbits.com/2025/02/28/comparing-audio-transcription-in-notes-audio-hijack-and-macwhisper/). | HN `_rs`; TidBITS | Moderate |

**Top desired features**
- **Real-time live transcription** during recording (HN uger, roadmap).
- **CLI / scriptable interface** to invoke from Python / terminal ([discussion #420](https://github.com/ggml-org/whisper.cpp/discussions/420)).
- **MKV import + in-editor video preview for subtitle work** (HN MaxikCZ, patrick91).

**Churn / switch‑away reasons**
- Price — to Whisper Notes ($4.99 lifetime), BetterDictation ($39). HN beardedwizard, idorosen: "commercial freeloading … thinness of the commercialized wrapper."
- Dictation need — users switch to Superwhisper, Wispr Flow, or Voibe ([aidictation.com](https://aidictation.com/blog/macwhisper-alternatives), [getvoibe](https://www.getvoibe.com/blog/macwhisper-alternatives/)).

### 1.6 Spokenly

**Signal strength:** moderate. PH launch 1 Aug 2025 (187 upvotes, 43 comments). Mac App Store 4.8★ across 602 ratings; 7 review texts visible. Two substantive critiques.

**Top pain points**

| # | Complaint | Evidence | Frequency |
|---|---|---|---|
| 1 | **iOS keyboard behavior breaks flow.** Custom keyboard yanks you back into Spokenly if it hasn't been frontmost ~2 min, losing context. Developer concedes "iOS limitation," suggests switching to cloud models. macOS unaffected. | [Vale Development 4★ "Buggy for iOS Right Now" Mar 28](https://apps.apple.com/us/app/spokenly-audio-to-text-ai-app/id6740315592?see-all=reviews&platform=iphone) | 1 named reviewer, dev-confirmed |
| 2 | **Feature bloat + surprise paywalls.** "Bloated — features not needed for simple voice input." Persistent mic-reset bug with Yeti mic. Unexpected subscription requirement for what looked like local-model usage (dev clarified: AI Prompts require user-supplied API key). | Denya Moloski 4★ Feb 18; Zraja101 Feb 27 — [App Store reviews (Mac)](https://apps.apple.com/us/app/spokenly-voice-to-text-ai-app/id6740315592) | 2 distinct reviewers |
| 3 | **Weaker prompt / context customization vs. Superwhisper.** "Limited context awareness means you can't take advantage of custom prompting as effectively as in Superwhisper for complex, context-rich tasks." | [afadingthought](https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac) | Single review, specific |

**Top desired features**
- **iOS / mobile version** (Edgar San Martin Jr. on PH; dev: shipping the following week).
- **Email newsletter / changelog channel** (Akhilesh Kumar on PH).
- **Clearer differentiation vs. Willow / Superwhisper** — Eugene Konash's question on PH surfaces a positioning gap users feel.

**Churn / switch‑away reasons**
- Thin. Loudest *switch-in* is from Superwhisper citing lower RAM — Felix Becker on PH: "40 MB of RAM" with Groq. No strong switch-out signal in public sources yet.

### 1.7 Sotto

**Signal strength:** effectively zero in public user sources.

Every top search hit for Sotto (`sotto.to` / `sottovoice.app`) is seller-authored marketing or comparison content ([sotto.to/compare/macwhisper](https://sotto.to/compare/macwhisper); [sotto.to/blog/dictation-app-comparison-2025](https://sotto.to/blog/dictation-app-comparison-2025)) or third-party roundups that describe positioning without attributable user quotes ([machow2.com](https://machow2.com/best-dictation-software-mac/), [onresonant.com](https://www.onresonant.com/resources/best-dictation-apps-mac)). No PH launch thread, no App Store listing with reviews, no HN discussion, no Reddit thread found in Jan 2025 – Apr 2026.

**Pricing inconsistency flagged:** `sotto.to` surfaces $49 one-time / 3 Macs in one place and $29 one-time / 3 Macs in the comparison page — either stale pages or an unannounced price change.

**Honest read:** Sotto has not generated reviewable public discussion after ~a year in market. The absence of user voice is itself a competitive data point: a one-time-purchase tool that isn't visibly churning users *into* or *out of* the conversation. All accuracy / language / Neural-Engine claims on Sotto's site are developer claims, not validated user experience. **Omitting Sotto from the desired-feature matrix below** — treating cells as "unknown" not "absent" would be more honest.

### 1.8 Voibe

**Signal strength:** thin-but-coherent. PH launch Sep 2025 (visible as "7mo ago" in Apr 2026), 4.8★ / 6 reviews. No Mac App Store presence. ~8 named PH commenters, all positive.

**Top pain points**

| # | Complaint | Evidence | Frequency |
|---|---|---|---|
| 1 | **Intel Macs explicitly unsupported.** Requires Apple Silicon Neural Engine. | [machow2 Voibe review](https://machow2.com/voibe-dictation-review/): "Windows or Intel Mac users are out of luck." | Documented drawback |
| 2 | **Not true streaming — text appears after utterance completes.** | Same review: "doesn't perform 'real time' instantaneous dictation that appears as you speak — text only appears after you've finished speaking." | Explicit |
| 3 | **Accent / non-native-speaker uncertainty.** "Needs clear speech for best results; uncertainty about how it would perform with stronger accents or non-native speakers." | machow2 — reviewer-flagged unknown, not user complaint | Caveat, not complaint |
| 4 | **Free tier 300-word cap.** | machow2 | Practical drawback for heavy users |

**Top desired features**
Effectively none in public sources. Only real-feature-shaped PH comment was Rakoues asking for "more Discord video content" (not a product feature). PH thread otherwise praises Cursor / VS Code integration, speed, privacy — suggesting the ICP self-selects for developers already on Apple Silicon.

**Churn / switch‑away reasons**
- No public switch-out signal. *Switch-in* from Superwhisper on cost (Voibe $99 lifetime vs. Superwhisper $249.99 lifetime, per [Voibe's own comparison](https://www.getvoibe.com/resources/superwhisper-review/)).
- *Switch-in* from Wispr Flow on privacy (screenshot issue).

## 2. Cross‑Cutting Pain‑Point Themes

Ranked by how many competitors' user bases voice the complaint. "N of 7" excludes Sotto (no user voice).

| # | Theme | Competitors affected | Strength |
|---|---|---|---|
| 1 | **Paste / insertion reliability** — clipboard fails on long blocks, breaks on non-US layouts, inconsistent per-app, loses first/last word | Wispr, Aqua, VoiceInk, Superwhisper (implicit via focus/mode bugs) | **4 of 7** — universal pain across architectures |
| 2 | **Hotkey / activation unreliability** — shortcut doesn't catch; mode doesn't activate; dictation silently fails to start | Superwhisper, VoiceInk, Aqua | **3 of 7** — all direct-dictation tools |
| 3 | **Cloud-only privacy pain** — audio sent to cloud, screenshots captured, enterprise VPN breakage, offline mode demanded | Wispr, Aqua | **2 of 7 directly**; **validated via churn-in to 4+ of 7** (Superwhisper, VoiceInk, MacWhisper, Voibe all receive switchers citing privacy) |
| 4 | **Multilingual weakness** — wrong-language detection, non-English accuracy drops, no language whitelist | VoiceInk, MacWhisper, and a cross-cutting gap per afadingthought | **2 direct + 1 review-wide** — fragmented across all Whisper-/Parakeet-based tools |
| 5 | **Onboarding / settings complexity** — "configuring a server, not installing an app," feature bloat | Superwhisper, Spokenly | **2 of 7**, but both #1 and #2 most mature — high-signal mature-product problem |
| 6 | **Support unresponsiveness** — weeks to reply, feedback-board tickets ignored | Wispr, Superwhisper, MacWhisper | **3 of 7** including the category leaders |
| 7 | **Post-payment reliability / feature regressions** — free trial great, paid service degrades or loses features | Wispr (reliability), Superwhisper (regressions) | 2 of 7 but both are the dominant players; high trust-cost |
| 8 | **Intel Mac exclusion** — local models don't run; developer tells Intel users to "use cloud" | VoiceInk, MacWhisper, Voibe | **3 of 7** — a segment widely written off |
| 9 | **Hallucination / auto-edit unfaithful rewrites** — LLM cleanup changes meaning; long-file loops | Wispr, MacWhisper | 2 of 7; Untype's Tier-1 "pre-send editing" is the answer |
| 10 | **Pricing resentment** — subscription fatigue vs. one-time alternatives; unclear what you get | Wispr ($15/mo), Aqua ($96/yr), Superwhisper ($249 lifetime) | 3 of 7; landscape fragmenting toward cheaper tiers |
| 11 | **Context-awareness gaps** — OCR-screenshot "very limiting"; can't switch mode per-app reliably | VoiceInk; Spokenly (vs. Superwhisper) | 2 of 7; this is an underserved axis |

## 3. Desired‑Feature × Competitor Matrix

✅ supported today · 🟡 partial / beta / user-supplied key · ❌ absent · ❓ unknown / no user voice

| Desired feature | Wispr | Super­whisper | VoiceInk | Aqua | Mac­Whisper | Spokenly | Sotto | Voibe | Untype plan |
|---|---|---|---|---|---|---|---|---|---|
| True offline / on-device mode | ❌ | ✅ | ✅ | ❌ | ✅ (file-only) | 🟡 | ❓ | ✅ | ✅ Apple Speech on-device STT (Phase 4) |
| On-device LLM cleanup (Apple Foundation / local) | ❌ | 🟡 (local-model mode) | ❌ (requested #333) | ❌ | ❌ | ❌ | ❓ | ❌ | 🟡 Phase 5 is provider-agnostic protocol — on-device can slot in |
| Pre-send edit / preview before insertion | ❌ | 🟡 (mini window, regressed) | ❌ | ❌ | n/a | ❌ | ❓ | ❌ | ✅ Tier-1 (`[Reviewing]` state in state machine) — **white space** |
| Native Swift (no Electron) | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ❓ | ✅ | ✅ |
| Intel-Mac support | ✅ | ✅ | ❌ (stalls, "use cloud") | ✅ | 🟡 (slow) | ❓ | ❓ | ❌ | ❓ — undecided; SFSpeechRecognizer is Intel-capable |
| Multilingual mid-sentence / think-in-L1 / output-in-L2 | ❌ | 🟡 (100+ STT langs, no composition translation) | ❌ (lang detection wrong) | ❌ | 🟡 (file, weak non-EN) | ❌ | ❓ | ❌ | ✅ Tier-2 — **white space** |
| Language whitelist / lock | ❌ | 🟡 (per-mode) | ❌ (requested #518) | ❌ | ❌ | ❌ | ❓ | ❓ | Easy win for Tier‑2 |
| Reliable clipboard-free insertion (CGEvent keystroke) | ❌ (clipboard restore fails) | ❌ | ❌ (paste fragile) | ❌ (long-block fails) | n/a | ❌ | ❓ | ❌ | 🟡 Phase 7 possible — **white space** if shipped reliably |
| Per-app / context-aware mode routing | 🟡 (auto, no user control) | 🟡 (manual, unreliable) | 🟡 (persistence bug) | ❌ | n/a | ❌ | ❓ | ❌ | ✅ Tier-2 intent-driven cleanup |
| Cross-device sync (iCloud) | ✅ (cloud-native) | 🟡 (buggy) | ❌ | ❌ | n/a | ❌ | ❓ | ❌ | ❌ Not on roadmap — lower priority |
| Personal dictionary / custom vocabulary | ✅ | ✅ | 🟡 | ❌ | ❌ | 🟡 | ❓ | ❌ | ❌ Not in Tier-1; should be Tier-2 |
| API / MCP / scriptable control | ❌ | 🟡 (shell triggers; roadmap) | 🟡 | ❌ | ❌ (CLI requested) | ❌ | ❓ | ❌ | ❌ |
| Whisper-quiet / shared-space mode | ❌ | ❌ | ❌ | ❌ (worst offender) | n/a | ❌ | ❓ | ❌ | ❌ — open white space |
| One-time / lifetime purchase | ❌ ($15/mo) | ✅ ($249) | 🟡 (donate / OSS) | ❌ (sub) | ✅ (~$80 Pro lifetime) | 🟡 | ✅ ($29–49) | ✅ ($99) | TBD — competitive-landscape recommends $79–129 lifetime option |

Notably absent from every competitor: **reliable keystroke-injection insertion**, **whisper-quiet mode**, and **genuine think-in-L1 / write-in-L2 composition**. Three white-space candidates.

## 4. White‑Space & Implications for Untype

Cross-referencing against `IMPLEMENTATION_PLAN.md` phases and `competitive-landscape.md` Section 6 positioning.

### 4.1 Positioning validated by user complaints

| Untype differentiator | Competitor evidence that confirms it |
|---|---|
| **Pre-send editing (`[Reviewing]` state)** — Tier-1 | Wispr hallucination complaints (auto-edits change meaning); MacWhisper long-file loops. Nobody else offers a review step — **this is the strongest uncontested differentiator**, not just a feature |
| **Native Swift / NSPanel overlay** — README + Plan | Wispr's Electron bloat is cited across 4+ sources as a churn trigger. Direct competitor users *name* "not Electron" as a buying criterion |
| **Privacy-pragmatic (on-device STT + cloud LLM, transparent)** — `competitive-landscape.md` 6.1 | Wispr screenshot scandal still referenced 6+ months later; Aqua cloud-only is #1 complaint; offline mode is the top-requested feature on both |
| **Message-layer / intent-aware cleanup** — product overview | VoiceInk OCR-screenshot called "very limiting"; Wispr's context-awareness opaque ("no user control"); Superwhisper manual modes unreliable. Nobody has *intent-aware* cleanup with user control |
| **Multilingual composition** — Tier-2 | No competitor does think-in-L1 / write-in-L2 well. VoiceInk wrong-language detection and MacWhisper Dutch/German weakness leave bilingual professionals unserved |

### 4.2 Tier prioritization adjustments

The research suggests two changes to the current Tier structure:

- **Promote reliable insertion (CGEvent keystroke) to a first-class Tier-1 concern, not a Phase 7 nice-to-have.** Paste-reliability pain is the **#1 cross-cutting theme** (4 of 7 competitors) — it's more universal than any other complaint category. `competitive-landscape.md` Section 7 Takeaway #6 already flags this; the research reinforces it. Concretely: `Insertion/TextInserter.swift` should aim for keystroke-first with clipboard fallback, not the other way around.
- **Add "language lock / whitelist" to Tier-2.** Single-issue fix (VoiceInk #518), addresses a recurring multilingual pain, and is a credibility signal for the multilingual-composition pitch. Low cost, high trust impact.

### 4.3 Features to *not* prioritize despite competitor presence

- **Cross-device iCloud sync.** Superwhisper and Wispr both have it (and Superwhisper's is buggy); but the demand signal in complaints is weak — users ask for offline *or* for better onboarding, not sync. Defer past Tier-3.
- **Personal dictionary / custom vocabulary.** Wispr and Superwhisper have it; VoiceInk partial. Complaints are thin. Add in Tier-2 only if natural — don't delay Tier-1 for it.
- **Meeting transcription / file transcription.** MacWhisper's lane — and the theme-1 complaint there (hallucination loops on long files) is someone else's problem. Confirms `competitive-landscape.md` 6.3: don't chase this.
- **Custom AI-prompts / power modes.** Superwhisper owns this niche and is losing users for it (complexity). Untype's "intent-driven cleanup" should stay opinionated — 3–5 intents (Slack, email, commit, translate), not 10+ user-defined modes. afadingthought's critique is the lesson: add progressive disclosure, not configuration surface.

### 4.4 Pricing read

`competitive-landscape.md` 6.5 recommends $7–9 / mo or $79 lifetime. Evidence so far:

- **Upward pressure:** Superwhisper $249 lifetime is a churn driver (users citing cost explicitly); Wispr $15 / mo likewise. The $79–129 lifetime band has clear demand.
- **Downward pressure:** Voibe $99 lifetime, Sotto $29–49 one-time, and Whisper Notes $4.99 anchor the budget tier. Untype doesn't have to match these but should explain why $79 is *good value*, not a premium.
- **BYOK** (bring your own OpenAI / Anthropic key) — VoiceInk's model; Spokenly also leans on it. This resonates with technical / privacy-conscious buyers and offloads inference cost. Worth offering as a Pro-tier option, not the default.

Net recommendation: hold `competitive-landscape.md`'s current $7–9 / mo + $79 lifetime target; add BYOK as a toggle; avoid $15+ territory unless enterprise compliance is in scope.

### 4.5 Under‑served niches confirmed

1. **Privacy-conscious + wants polish.** Aqua quality without Aqua's cloud footprint; Wispr UX without Wispr's architecture. **Untype's primary ICP.**
2. **Multilingual professionals.** No competitor addresses think-in-L1 / write-in-L2. Lowest supply, genuine demand.
3. **Intel-Mac holdouts.** Three competitors evict them. SFSpeechRecognizer runs on Intel — Untype could be the only quality choice, which is a cheap beachhead.
4. **Shared-space / open-office users.** Aqua's background-bleed problem is a widely-shared pain nobody solves. Whisper-quiet mode or VAD threshold tuning is a small-scope Tier-2/3 feature with clear audience.

### 4.6 Risks surfaced by the research

- **Support responsiveness is a category-wide trust tax.** Wispr, Superwhisper, MacWhisper all carry it. Untype's solo-project reality means this is a real risk, not a differentiator-by-default; plan for explicit response SLAs / public changelog to turn it into one.
- **Post-payment reliability degradation** (Wispr Trustpilot pattern) is a brand-destroying failure mode. Untype's "review before insertion" makes *visible* failures (user sees bad output before it's pasted) and *invisible* failures (silent drops) less dangerous — but observability on the insertion path is worth investing in early.
- **Feature-regression churn** (Superwhisper afadingthought case) is a warning against stripping options once shipped. Progressive disclosure > removal.

## 5. Source Log

### Primary user-voice sources (first-hand)

- [Trustpilot — Wispr Flow](https://www.trustpilot.com/review/wisprflow.ai)
- [Product Hunt — Wispr Flow reviews](https://www.producthunt.com/products/wisprflow/reviews)
- [Product Hunt — Superwhisper reviews](https://www.producthunt.com/products/superwhisper/reviews)
- [Product Hunt — Spokenly launch](https://www.producthunt.com/products/spokenly)
- [Product Hunt — Aqua Voice reviews](https://www.producthunt.com/products/aqua/reviews)
- [Product Hunt — Voibe launch](https://www.producthunt.com/products/voibe) / [Voibe reviews](https://www.producthunt.com/products/voibe/reviews)
- [Mac App Store — Spokenly (Mac)](https://apps.apple.com/us/app/spokenly-voice-to-text-ai-app/id6740315592) / [iPhone](https://apps.apple.com/us/app/spokenly-audio-to-text-ai-app/id6740315592?see-all=reviews&platform=iphone)
- [Mac App Store — Whisper Transcription (NL)](https://apps.apple.com/nl/app/whisper-transcription/id1668083311?l=en-GB&platform=mac)
- [Mac App Store — Superwhisper](https://apps.apple.com/us/app/superwhisper/id6471464415)
- [Mac App Store — VoiceInk iOS](https://apps.apple.com/us/app/voiceink-ai-dictation/id6751431158)
- [Trustpilot — MacWhisper](https://www.trustpilot.com/review/macwhisper.helpscoutdocs.com)
- [VoiceInk GitHub Issues](https://github.com/Beingpax/VoiceInk/issues) (issues #321, #333, #518, #534, #535, #546, #597, #599, #614, #617, #625, #634, #635, #641, #642, #645, #646, #647, #650)
- [HN 37228821 — MacWhisper](https://news.ycombinator.com/item?id=37228821)
- [HN 39828686 — Aqua Voice original launch](https://news.ycombinator.com/item?id=39828686)
- [HN 43634005 — Aqua Voice 2 launch](https://news.ycombinator.com/item?id=43634005)
- [HN 44225953 — Transcription API thread](https://news.ycombinator.com/item?id=44225953)
- [HN 44944691 — VoiceInk comparison](https://news.ycombinator.com/item?id=44944691)
- [HN 47040375 — Show HN: freeflow](https://news.ycombinator.com/item?id=47040375)
- [HN 44510624 — Show HN: Whispering](https://news.ycombinator.com/item?id=44510624)
- [Superwhisper changelog](https://superwhisper.com/changelog)
- [Wispr Flow StatusPage Jan 2026 incident](https://statuspage.incident.io/wispr-flow/incidents/01KFH1SEDXQSREP1CHMPXVHR47)
- [whisper.cpp Discussion #420 — MacWhisper feature voting](https://github.com/ggml-org/whisper.cpp/discussions/420)

### First-hand reviews / published analysis

- [samwize — Review of Wispr/Superwhisper/MacWhisper for Vibe Coding (Nov 2025)](https://samwize.com/2025/11/10/review-of-whispr-flow-superwhisper-macwhisper-for-vibe-coding/)
- [afadingthought — Best AI Dictation Tools for Mac](https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac)
- [Danny Smith — VoiceInk notes](https://danny.is/notes/voiceink/)
- [9to5Mac — Aqua Voice review (Aug 2025)](https://9to5mac.com/2025/08/15/aqua-voice-shows-just-how-good-mac-dictation-could-be-if-apple-just-tried/)
- [TidBITS — Notes/Audio Hijack/MacWhisper transcription (Feb 2025)](https://tidbits.com/2025/02/28/comparing-audio-transcription-in-notes-audio-hijack-and-macwhisper/)
- [Simon Willison — MacWhisper speaker recognition (Nov 2025)](https://simonwillison.net/2025/Nov/18/macwhisper-speaker-recognition/)
- [machow2 — Voibe Dictation Review](https://machow2.com/voibe-dictation-review/)

### Secondary / aggregator sources (treat as second-hand)

- [eesel — Wispr Flow review](https://www.eesel.ai/blog/wispr-flow-review)
- [Letterly — Wispr Flow review](https://letterly.app/blog/wispr-flow-review/) *(affiliate)*
- [Resonant — Mac Reddit dictation roundup](https://www.onresonant.com/resources/best-dictation-tools-mac-reddit) *(affiliate)*
- [Voibe — Wispr Flow vs Superwhisper](https://www.getvoibe.com/resources/wispr-flow-vs-superwhisper/) *(affiliate)*
- [Voibe — Aqua Voice alternatives](https://www.getvoibe.com/blog/aqua-voice-alternatives/) *(affiliate)*
- [Voibe — Aqua Voice vs Wispr Flow](https://www.getvoibe.com/resources/aqua-voice-vs-wispr-flow/) *(affiliate)*
- [Voibe — Superwhisper review](https://www.getvoibe.com/resources/superwhisper-review/) *(affiliate)*
- [Medium — Ryan Shrott "Why I Cancelled Wispr Flow"](https://medium.com/@ryanshrott/why-i-cancelled-my-wispr-flow-subscription-and-what-im-using-instead-d783433f4411) *(affiliate — promotes DictaFlow)*
- [Medium — Ryan Shrott "Wispr Flow Trust Gap"](https://medium.com/@ryanshrott/the-wispr-flow-trust-gap-why-reliability-matters-more-than-hype-in-2026-c7dd55392408) *(affiliate)*
- [LinkedIn PSA — Nathan Grzesiek on Wispr privacy](https://www.linkedin.com/posts/nathan-grzesiek_psa-for-lennys-newsletter-fans-if-activity-7361833247258890240-RhNl)
- [aidictation.com — MacWhisper alternatives](https://aidictation.com/blog/macwhisper-alternatives)
- [getvoibe.com — MacWhisper alternatives](https://www.getvoibe.com/blog/macwhisper-alternatives/)
- [Sotto homepage](https://sotto.to/) and [comparison pages](https://sotto.to/blog/dictation-app-comparison-2025) *(seller-authored; Sotto has no independent user voice in public sources)*

### Known gaps for next refresh

- **Reddit primary quotes.** All Reddit signal in this doc is second-hand. A future refresh should use an authenticated Reddit tool or manual pass for r/MacApps, r/macOS, r/productivity.
- **X / Twitter signal.** Not indexed well by general search; not mined here. Worth a pass next quarter.
- **Sotto.** Re-check in 3 months for PH launch, App Store listing, or Reddit thread. Pricing inconsistency ($29 vs. $49) should resolve.
- **Spokenly iOS** — dev said shipping "next week" from the PH launch; check post-launch review volume.
- **Wispr Flow feedback board** (feedback.superwhisper.com returned 403 during mining; retry).
