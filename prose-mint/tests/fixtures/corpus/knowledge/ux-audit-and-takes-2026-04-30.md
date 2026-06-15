<!-- prose-check: skip bold-colon-opener -->
# UX Audit + 3 Fresh Interface Takes
**Date**: 2026-04-30
**Status**: Audit & directional brainstorm, not scheduled, not specced
**Scope**: Walks the *currently implemented* push-to-talk overlay (post-cutover) end-to-end, surfaces friction not already covered in `ux-audit-2026-04-15.md` / `ux-direction-2026-04-12.md`, then proposes three substantively different interaction paradigms for a v2.
**Source files read**: `Untype/Window/BarView.swift`, `ReviewingBody.swift`, `OverlayController.swift`, `OverlayPanel.swift`, `ContextChip.swift`; `Untype/State/AppState.swift`.
**Prior audits**: `ux-audit-2026-04-11.md`, `ux-audit-2026-04-12.md`, `ux-audit-2026-04-15.md`, `ux-direction-2026-04-12.md`. This doc is **additive**, it does not re-litigate decisions made there.

---

## 0. What this audit is not

The 04-12 direction doc set the canonical interaction model: hold `fn`, blob waveform, release to reviewing toast anchored above the focused input, `Return` inserts / `Esc` cancels. The 04-15 audit closed out the design feedback on the Figma frames. Both are settled.

What's *not* settled, and what this doc focuses on:

1. **Friction the prior audits couldn't see**, because they were reviewing static frames or planned behavior, not the running app with a Cleaned·Original toggle, ContextChip, and per-token polishing animation all interacting.
2. **Whether the bar+toast paradigm is the right shape at all**, the prior audits assumed it. With 20 days of post-cutover polish behind us and a naming/positioning question still open (session 59), it's worth asking the next-order question.

---

## 1. Phase-by-phase friction (current build)

Walking the actual user flow against `BarView.swift` switch cases. Severity = user-visible impact, not engineering cost.

### 1a. Idle to recording (fn press)

Status: covered well by the prior direction. Debounce, modifier exclusion, silence detection, all good.

**New friction (low):** the 200ms debounce window means a confident, quick tap of `fn` does *nothing* and gives no feedback. There's no log line, no flash, no audible click. First-time users will tap, see nothing, tap harder. Ironically, the people who *don't* have the bug Untype is solving (accidental `fn` presses) are the ones who feel the cost of the debounce.

**Fix surface area:** small. After ~5 sub-200ms taps in 30s, surface a one-time hint via the menu-bar dropdown ("Hold `fn` longer to start dictation").

### 1b. Recording (`listening`, `transcribing`)

`statusIndicator` shows the blob waveform; `text` shows either the recording hint or the live partial. The partial uses `lineLimit(1) + truncationMode(.head)` which works.

**New friction (medium):** the panel is anchored to the focused UI element via `FocusedElementLocator`, but **only at panel show time**. If the user `cmd-tab`s away mid-recording (which happens, voice users multitask), the overlay stays anchored to the now-defocused field. On `fn` release the *new* frontmost-app gets the insert, but the *anchor* never moved. Mild visual confusion + a real bug if the user returns to the original app expecting the overlay to follow.

**New friction (medium):** the silence detector swaps the hint text but leaves the blob waveform animating-but-flat. To a glance, the blob *looks* alive even when no audio is being captured. The 04-15 audit surfaced "proof of life" via blob motion; the silence case inverts this, the blob is the proof of *no* life but uses the same color and shape as the proof-of-life. Color cue (amber tint? desaturate?) would clarify.

### 1c. Processing (`processing`, `polishing`)

`processing` shows a `ProgressView` spinner + "Polishing…". On the first streamed token, phase flips to `.polishing(partialText:)` and `BarView` switches to `ReviewingBody` rendered *inside the recording-bar geometry's transition*, `OverlayController` snaps frame updates non-animated (good call, prevents jitter), then animates back on the next phase.

**New friction (high):** the visual transition `processing to polishing` is asymmetric. The bar is 48pt tall during processing; the toast clamps to ≥96pt during polishing. So the moment the first token arrives, the panel jumps ~50pt taller and re-anchors. If the focused-element anchor flipped from "above" to "below" during the resize (because the toast no longer fits above), the panel *teleports* across the screen mid-stream. A user watching the first word appear can lose it.

**Fix surface:** anchor decision should be made once at end-of-recording (when we know the final geometry budget), not per-frame. Or: show the polishing geometry from `processing` start with a hidden cursor, so the resize happens before tokens arrive.

**New friction (medium):** during polishing, both a streaming text + a blinking cursor + a per-token frame delta are happening. The `OverlayController` comment explicitly notes "the per-delta resizes don't stack overlapping Core Animation transitions, that produces visible jitter at typical 30–80 tokens/s rates" and that's why polish frames snap. But the cursor still blinks at 0.6s cycle (`StreamingCursor`), and the text is appearing at 30–80 tps, and the panel's height is changing. It's a lot at once. A user just out of recording mode is now reading text-being-typed-by-something-else. Cognitive load spike.

### 1d. Reviewing (`reviewing`)

Toast at 500×96–200pt. Header has the optional ContextChip on the left and the optional Cleaned·Original toggle on the right. Body is a scroll view with text or `OriginalAlternatesView`. Hint says `⏎ Insert · Esc Cancel`.

**New friction (high), the trust gap when alternates are absent.** `BarView.reviewingBody` only exposes the Cleaned·Original toggle when `hasOriginal` is true (`!(original?.isEmpty ?? true)`). Per `effectiveOriginalText`'s logic, this is true only when:
- `lastTranscriptionSegments` is non-empty (Apple Speech path), OR
- `lastOriginalPrefix` is non-empty (Apple Speech reset mid-utterance), OR
- `lastOriginalText` is set (set by reducer on transitions)

For the Groq / RemoteWhisper / WhisperKit STT paths, `lastTranscriptionSegments` is empty and there's no per-segment alternate data. The toggle is hidden. **The user has no way to verify what they actually said.** If polish hallucinates, the user can't tell. This is the single largest trust risk in the product, and it's silent.

**Fix surface:** even without per-segment alternates, the raw transcript is available as `lastOriginalText`. Show the Cleaned·Original toggle for *any* path where `lastOriginalText` exists, not just paths with segment-level alternates. Tappable alternates becomes an Apple-Speech-only enrichment of an always-visible Cleaned·Original toggle.

**New friction (medium):** there's no inline edit. The 04-15 audit recommended "Ship Option 1 + Option 2 combined for v1", Option 1 is plain inline text edit, Option 2 is the alternates popover. Option 2 shipped. Option 1 didn't (the body is `Text` with `.textSelection(.enabled)`, which is select-and-copy, not edit). So the user's only correction lever is tapping among 2–3 candidates Apple offered, and that's only on the Apple Speech path. On other paths, no correction is possible at all. Combined with the trust gap above, this is the second-largest issue.

**New friction (low):** ContextChip override re-runs polish silently. The user picks a different profile from the menu and the toast updates. Fine. But there's no preview of "this will re-polish", if the user's machine is slow, they may wonder if the click registered. A subtle reload spinner overlaid on the chip, or briefly disabling it during the re-polish, would close the loop.

**New friction (low):** ContextChip is hidden when `detectionSource == .fallback`. The reasoning (don't show "General" pretending to be detection) is correct, but the *absence* of the chip is also information, "context detection didn't work for this app". Consider a muted "?" pill instead of nothing, so the user can opt-in to override even when auto-detection failed.

### 1e. Inserting

Phase shows a generic "Inserting…" with a ProgressView. Fine.

**New friction (low):** insert is one-shot, then phase returns to idle. No undo affordance, no "wait, I clicked too soon" gesture. If the polished text was wrong and the user only realized after Insert, recovery is `cmd-z` in the target app, which sometimes works, sometimes doesn't (Slack, Mail draft, etc.). A 2-second post-insert "undo" overlay (think Gmail "Undo Send") would be a high-value safety net for ~zero engineering cost.

### 1f. Error

`error` renders in the compact bar with a yellow warning triangle, error text, and an action hint. Geometry stays 500×48.

**New friction (low):** the `transcriptionFailed` / `cloudUnavailable` / `quotaExceeded` cases all carry `rawText: String?`. When raw text is present, the user has *something usable*, but the error UI doesn't expose it directly. The action hint (`AppError.actionHintView`) likely says "press X for raw text" (per the 04-12 direction doc), but the recovery path is a hotkey on a transient surface, easy to miss.

**Fix surface:** for errors that carry raw text, switch geometry to the reviewing-toast and show the raw transcript with `Insert raw` as the primary action. Errors with raw text are *recoverable*; treating them as transient compact-bar messages buries the recovery.

---

## 2. Top-5 issues ranked

| # | Issue | Severity × Cost | Surface |
|---|---|---|---|
| 1 | **Trust gap: Cleaned·Original toggle hidden on non-Apple-Speech paths** | High × Low | `BarView.reviewingBody` `hasOriginal` check; expand to `lastOriginalText`-based |
| 2 | **No inline edit in reviewing toast** | High × Medium | `ReviewingBody.body`: swap `Text` for editable text view; gate panel `canBecomeKey` while editing |
| 3 | **Anchor teleport on `processing to polishing` resize** | Medium × Low-Medium | `OverlayController.refreshLayout`; resize at start of processing, not first token |
| 4 | **No undo affordance after Insert** | Medium × Low | New `.justInserted` phase with 2s timeout + `cmd-z`-like overlay action |
| 5 | **Recoverable errors hidden in compact-bar transient surface** | Medium × Low | Error path: switch to reviewing-toast geometry when `error.rawText != nil` |

Issues 1 + 2 + 4 together solve the largest single user concern that hasn't been articulated in any prior audit: *"can I trust what Untype just inserted on my behalf?"* That's the question the anti-AI positioning needs to answer with affordances, not just copy.

---

## 3. Three fresh interface takes

Each take re-asks the framing question and ignores the bar+toast paradigm. None are recommendations to *replace* the current model, they're directional probes for what v2 could look like, given a year of usage data the project doesn't have yet.

### Take A: Live ghost insertion (eliminate the review modal)

Polished text appears **inside the target app's text field directly** as it streams, rendered as ghost-grey provisional text. The reviewing toast disappears entirely. To commit: a quick `fn` double-tap or tab. To reject: `Esc`. Per-segment alternates surface as inline tooltip-style accordions on hover/long-press.

```
Before fn release:        ┌──── target app ────────────┐
                          │ Hi Sam, I wanted to        │
                          │ follow up on the           │
                          │ ▌ <- cursor                │
                          └────────────────────────────┘

During polish (ghost):    ┌──── target app ────────────┐
                          │ Hi Sam, I wanted to        │
                          │ follow up on the           │
                          │ proposal we discussed      │  ← ghost-grey italic
                          │ last week. Would Tuesday   │  ← still streaming…
                          │ at 2pm work for▌           │
                          └────────────────────────────┘

After fn-double-tap:      ┌──── target app ────────────┐
                          │ Hi Sam, I wanted to        │
                          │ follow up on the proposal  │  ← committed (black)
                          │ we discussed last week.    │
                          │ Would Tuesday at 2pm work  │
                          │ for you?                   │
                          └────────────────────────────┘
```

**Why interesting:** matches the mental model of voice-as-typing (Wispr Flow's pitch). Eliminates the spatial context switch from the focused field to the toast back to the field. The user sees their text *where it goes*, immediately.

**Why hard:** ghost text without commit requires the target app to support a marked-text range (some text views do via `NSTextInputClient`, many don't, Slack/Discord/Notion are Electron and won't). For Electron apps, fall back to clipboard-based insert + a hard "Esc removes everything I just typed" backstop. Probably needs an allow-list of well-behaved text fields.

**This wins if:** the user's target apps are mostly native (Mail, Notes, Messages, Xcode) and the population of "I want to verify before insert" users turns out to be smaller than the population of "I want it inserted yesterday" users. It loses if the user community is heavily Electron-bound or has high paranoia about hallucination.

### Take B: Sidecar dock (persistent right-edge surface, history-first)

A 280pt-wide always-visible translucent column on the right edge of the screen. Recording still happens via `fn` and the blob renders inline. Each completed dictation appears as a card stacked vertically, newest top, scrollable history of the last ~50. Each card has Cleaned·Original toggle, alternates, edit, re-insert, copy, delete.

```
┌──── target app (full screen) ────────────────────┬─ sidecar ──────────┐
│                                                  │ ◉ Recording…  ▌▌▌ │
│ Sam,                                             │ ─────────────────  │
│ I wanted to follow up on the proposal we         │ ◯ 2 min ago        │
│ discussed last week. Would Tuesday at 2pm        │   "Hi Sam, I wan…  │
│ work for you?                                    │   [Cleaned·Orig.]  │
│                                                  │   [edit] [insert]  │
│ Best,                                            │ ─────────────────  │
│ ▌                                                │ ◯ 8 min ago        │
│                                                  │   "remember to bo… │
│                                                  │   [Cleaned·Orig.]  │
│                                                  │   [edit] [insert]  │
└──────────────────────────────────────────────────┴────────────────────┘
```

**Why interesting:** turns voice from a *moment* (one utterance, one insertion) into a *medium* (a history of dictations the user can re-visit, edit, re-use). Solves the "I dictated something good earlier, can I get it back?" problem that exists for nobody using the current build because the affordance doesn't exist. Also solves trust by default: the original transcript is always one click away in the card.

**Why hard:** screen real estate. Power users on 13" laptops will hate it. Probably needs an auto-hide mode (cmd-shift-` to toggle), or only auto-shows for ~3s after dictation completes then collapses to a thin edge strip. Also conflicts with the focused-element anchor (you can't anchor to the focused field if you're a fixed sidebar), it gives up that affordance entirely.

**This wins if:** the user community turns out to be heavy-volume dictators (writers, journalists, researchers) for whom history and re-use is more valuable than focused-input anchoring. Loses if users are short-burst dictators (Slack messages, code comments) where each dictation is independent.

### Take C: Voice-edit fuse (continuous dictation with voice corrections)

No release-to-finish. The user starts dictating with `fn`-press-and-release (toggle, not hold). Polishing happens live inline. The user can say *"scratch that"*, *"instead, say X"*, *"make it more formal"*, *"end it with a question"*, voice corrections are intercepted by the LLM before re-inserting. Final commit is a 2-second silence trigger or another `fn` tap.

```
User says:  "Hi Sam, I wanted to follow up on the proposal."

Untype:     [polish renders into target app]
            "Hi Sam, I wanted to follow up on the proposal."

User says:  "Make that more casual."

Untype:     [intent recognized → re-polish with casual tone]
            "Hey Sam, just wanted to bump the proposal."

User says:  "End it with asking about Tuesday."

Untype:     [intent recognized → append + re-polish]
            "Hey Sam, just wanted to bump the proposal. Does Tuesday work?"

User says:  [silence 2s]

Untype:     [commit, return to idle]
```

**Why interesting:** matches how voice-first users naturally correct themselves ("no, I meant…"). Removes the correction-via-keyboard-and-mouse roundtrip that the current build can't avoid even in the best case. Also leverages the LLM as the correction layer rather than wiring up a manual edit affordance, fits the "voice-as-input-modality, AI-as-everything-else" frame. Genuinely novel: nobody on the current competitive map (Wispr, Superwhisper, MacWhisper) does this.

**Why hard:** intent detection is the whole game. Distinguishing *"scratch that"* (correction directive) from *"I asked them to scratch that out"* (literal content) is non-trivial. Probably needs a fast classifier pass before each polish call. Also has runaway risk: the user gets stuck in correction loops because the model misinterprets and now they need a way out. Needs a hard "commit now" hotkey (`cmd-Return`) and a "abort everything" hotkey.

**This wins if:** the user population skews to voice-first / accessibility / low-typing-throughput users who would prefer a 2× longer dictation that ends at the right text over a 1× dictation that needs keyboard correction. Loses if users are typists who voice only because typing is *slightly* slower, they'd rather take the keyboard edit step.

---

## 4. Recommendation

**Don't pick a take yet.** This brainstorm is upstream of the ICP work (P3) and the pivot analysis (X1, X5). Each take optimizes for a different ICP:

- **Take A** wins if the ICP is "fast typists who want voice for speed" (Wispr Flow target)
- **Take B** wins if the ICP is "voice-heavy creators who want voice as a content layer"
- **Take C** wins if the ICP is "voice-first / accessibility / low-typing"

The right move is to use the **friction list (§2 issues 1–5)** as immediate roadmap candidates, they all improve the current paradigm without committing to a v2 direction, and **defer the v2 take selection until P3 lands**. Specifically:

1. **Ship issue 1 (always-on Cleaned·Original toggle) and issue 4 (post-insert undo)**, both are high-value, low-cost, and *make the trust story credible* regardless of which v2 take we eventually pick. They're prerequisites for the anti-AI positioning to be more than copy.
2. **Park takes A/B/C** as branches in `knowledge/` and revisit after P3. The take that wins the ICP question wins the v2.

**This is wrong if:** P3 surfaces an ICP that requires a take *we haven't sketched* (e.g., team / collaborative dictation, mobile companion, voice-as-CLI). In that case, this audit's three takes are too narrow and a separate brainstorm is needed.

---

## 5. Open hooks (carry into other docs)

- **For X5 (pivot ideas):** Take B's history affordance suggests an audience pivot, "voice notes for writers" is a different product than "voice-to-text for typists". Consider as a candidate.
- **For X1 (build-vs-extend):** Take A's ghost-insertion challenge is a distribution decision, sandbox can't do it cleanly, native apps can. The take constrains the channel.
- **For P3 (ICP):** the three takes map to three different ICPs. Use them as straw-man personas to score against.
- **For P1 (Lean Canvas):** the friction list is the v1 "problem" block; the takes are v2 "solution" candidates. Don't conflate.
