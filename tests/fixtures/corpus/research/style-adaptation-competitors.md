# Style Adaptation in Competitor Dictation Apps

**Date:** 2026-04-23
**Purpose:** Synthesize how competitor macOS dictation tools implement the "style adaptation" step — the post-transcription stage that adjusts tone and format to fit the destination app.

---

## What "Style Adaptation" Means

The term appears in Wispr Flow's documented processing pipeline:

> transcription → filler removal → punctuation → **style adaptation**

It is the final step: taking a clean transcript and reshaping its tone, length, structure, and formality to match where it will be inserted. "Casual for Slack, professional for Gmail" is the canonical example.

Different competitors reach this step through different mechanisms — automatic app detection, user-defined modes, or manual selection — with significant variation in the degree of user control and reliability.

---

## Per-Competitor Breakdown

### Wispr Flow — Automatic, opaque
- Detects the frontmost app via Accessibility API at dictation time
- Automatically shifts tone: Slack → casual/short, Gmail → semi-formal with greeting/sign-off
- Reportedly uses Screen Capture permission in addition to Accessibility, suggesting possible OCR of screen content
- Context Awareness is on by default; can be toggled off in Settings > Data & Privacy
- **No user visibility into what was detected or how it was applied**
- Banking apps and password fields suppress context entirely

*Pain point:* The opacity created trust issues — users couldn't tell why output changed, and the screenshot-based context capture triggered a privacy backlash in early 2026.

### Superwhisper — Manual modes, user-defined
- No automatic detection by default
- Users create named "modes" (`email`, `code`, `casual`, `meeting`, etc.) with custom AI instructions
- Modes can be configured to auto-switch based on frontmost app or website
- The April 2026 cohort review notes a user running 21 parallel custom prompts
- Modes give fine-grained control: tone, formatting rules, vocabulary, output structure
- Context sources used: selected text at dictation start, clipboard during recording, frontmost-app context via Accessibility (text-only, no screenshots)

*Pain point:* Mode-switching friction is the #1 usability complaint. Auto-switch is unreliable. The settings surface is described as "configuring a server, not installing an app." Feature regressions (e.g., removal of reprocess-with-context) damaged trust.

### VoiceInk — Screenshot+OCR, fragile
- Has both "AI enhancements" and "Power Modes" with overlapping terminology
- Context awareness uses screenshot+OCR rather than Accessibility text extraction
- Reviewed as "very limiting" compared to Superwhisper's text-based approach
- Mode switching during a recording is Cmd/Opt+number (capped at 10 modes)
- One-shot per-recording enhancement is a requested but unshipped feature

*Pain point:* Screenshot OCR misses structured content that Accessibility exposes directly; the dual-terminology ("enhancements" vs. "modes") confuses users about what they're configuring.

### AudioPen — Manual output-style picker, different paradigm
- Not a system-wide dictation tool — voice notes to structured text, web-first
- User selects an output style per recording (structured summary, bullet list, action items, etc.)
- No app-context detection; the "style" is about the note format, not the destination app

*Not directly comparable:* AudioPen's style selection is a deliberate content-shaping step, not adaptation to a target writing surface.

### Everyone else
| Tool | Style adaptation |
|------|-----------------|
| MacWhisper | None — file transcription, not dictation |
| Sotto | Unknown; no independent user signal available |
| Voibe | Opinionated cleanup, no per-app adaptation |
| Spokenly | Limited context awareness vs. Superwhisper (per afadingthought review) |
| Aqua Voice | None — cloud STT with no documented adaptation layer |
| Apple Dictation | None — raw transcription only, no cleanup step |

---

## The Spectrum

| | Low user control | High user control |
|---|---|---|
| **Automatic (magic)** | Wispr Flow | — |
| **Semi-automatic** | VoiceInk (fragile OCR) | Superwhisper (modes + auto-switch) |
| **Manual** | AudioPen (per-recording picker) | — |
| **None** | Apple Dictation, Aqua, Voibe, etc. | — |

No competitor occupies the **automatic detection + user transparency + override** quadrant.

---

## The Gap — Untype's Position

From the competitive research:

> Wispr Flow auto-detects but gives no user visibility or control; Superwhisper gives full control but no automatic detection. Nobody ships intent-aware adaptation with user transparency — where the app detects context, tells you what it detected, and lets you override.

Untype's design targets this gap directly:
- Auto-detect via bundle ID + window title (no screenshots, no Screen Capture permission)
- Surface the detected context in the overlay (the "context chip" showing detected app profile)
- Allow per-session override before insertion
- Keep the context sources text-only and Accessibility-gated for privacy

The `AppContext` struct and context chip UI are the implementation of this position.

---

## Related Docs

- `research/competitive-landscape.md` — full competitor profiles and gap analysis
- `research/context-aware-cleanup.md` — macOS APIs for context detection, implementation tiers, privacy analysis, and Untype's implementation plan
- `research/user-pain-points-and-desires-2026.md` §2 theme #11 — "context-awareness gaps" as a cross-cutting pain point across VoiceInk and Spokenly
