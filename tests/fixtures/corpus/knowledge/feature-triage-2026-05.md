<!-- prose-check: skip bold-colon-opener -->
# Feature triage 2026-05

**Date**: 2026-05-08
**Purpose**: Sequence what to build next, ordered by ICP-alignment × readiness × effort. Pulls from `knowledge/icp-v1.md` (C2 bilingual primary), `knowledge/lean-canvas-v1.md` (wedge: "Speak in your language. Send in theirs."), `knowledge/validation-metrics-v1.md` (six metrics), `knowledge/open-decisions.md` (OD-001…OD-007), all `knowledge/ux-audit-*.md`, `research/competitive-landscape.md` §5.6 (white space), `research/on-device-translation.md`, `IMPLEMENTATION_PLAN.md`, plus the recent session log review.
**Status**: First-pass triage. Re-run when validation-metrics data arrives or when the codebase rename phase happens.

---

## Reading order: tiers

- **Tier 1**, wedge-blocking. Untype cannot honestly claim "Speak in your language. Send in theirs." until these ship.
- **Tier 2**, trust-mechanism. Move the **send-without-edit rate** (validation metric #2) above 70%. Without these, retention is at risk.
- **Tier 3**, reliability hygiene. Ship-stoppers when they hit a user. Quietly painful, easy to fix.
- **Tier 4**, defer. Parked behind validation data, or rule-out candidates.
- **Tier 5**, already done; do not re-do.

---

## Tier 1: Wedge-blocking (do first)

The wedge depends on three things existing together. Without all three, the marketing pitch is fiction.

### T1.1: L1-to-L2 translation phase wired into the polish prompt
**Source**: `knowledge/lean-canvas-v1.md` §4 (gap), `research/on-device-translation.md` (Phase 1 plan), prompt audit 2026-05-08
**Effort**: M (~6–10h coding + 2–4h prompt tuning per language pair)
**Status**: Architecturally prepared, feature-gated. `TranscriptionChunk.language` populated. `LLMRequest.locale` carries source language but is **never read**. `PipelineConfiguration.translationProviderId` is a placeholder with no consumer. Current prompt explicitly says *"Produce output in the same language as the input"* and *"Never translate"*, i.e. the prompt actively contradicts the wedge.
**What to ship**:
1. New phase-explicit system prompt (see `knowledge/prompt-design-v2-2026-05.md`)
2. `LLMRequest.targetLocale: String?` field; pass through `AppContext`
3. Settings UI: target-language picker (default = inherit from STT locale)
4. Per-language polish-prompt variants for at least RU↔EN, ES↔EN, ZH↔EN (tier-2 per product memo)
5. `Cleaned · Original` toggle works for translation outputs (extends T2.3)
**Done when**: dictating in Russian into a `targetLocale: en-US` Slack window produces a fluent English Slack message that a native English speaker would not flag as translated.
**Validation**: send-without-edit rate ≥60% on L1-to-L2 (per `validation-metrics-v1.md` metric #2 threshold), style-trust ≥4.0 from bilingual pilot users.

### T1.2: Cleaned · Original toggle in *every* path
**Source**: UX Audit 2026-04-30 friction 1d
**Effort**: S (1–3h)
**Status**: Currently shows only when Apple-Speech-only (segment-level alternates exist); absent for cloud-final and hybrid paths.
**Why it's Tier 1**: translation makes the polish less faithful by design. If the user can't see what they actually said vs. what's being inserted, the trust mechanism collapses precisely when the wedge engages. The toggle is what makes L1-to-L2 *safe*.
**What to ship**: show toggle whenever `lastOriginalText` exists, not gated on alternates availability. Tappable alternates becomes Apple-Speech-only enrichment, separately.
**Done when**: every polish output (English, translated, hybrid) shows Cleaned · Original toggle in reviewing toast.

### T1.3: Per-profile tone shift magnitude verified post-ISS-017
**Source**: OD-002
**Effort**: S (15-min smoke + maybe 1h prompt tweak)
**Status**: Architectural conflict resolved. Empirical magnitude unknown. If Chat to Email doesn't *visibly* shift register, translation tone control will be even more unreliable.
**What to ship**: smoke pass on Chat-to-Email-to-Code with the same source utterance; if shifts are subtle, escalate `toneDescription` strings to imperative ("Use contractions. Skip greetings.") and/or add one worked example per profile.
**Done when**: side-by-side Chat vs. Email outputs read clearly differently to a third-party reader.

**Tier 1 sequencing**: T1.3 first (cheapest, de-risks T1.1's prompt design), then T1.2 (cheapest UI work, makes T1.1 testable), then T1.1.

---

## Tier 2: Trust mechanism (send-without-edit ↑)

Get validation metric #2 above 70%. Each of these reduces a class of "I had to fix the output by hand" friction.

### T2.1: Inline edit in reviewing toast
**Source**: UX Audit 2026-04-30 friction 1d
**Effort**: M (3–6h)
**Status**: Toast supports `textSelection(.enabled)` for copy, not edit. Forces user to insert first then edit in target app, breaks flow.
**What to ship**: inline editable text view in reviewing toast; commits on Cmd+Enter or Insert-button click.

### T2.2: Polishing-transition anchor stability
**Source**: UX Audit 2026-04-30 friction 1c
**Effort**: M (4–8h)
**Status**: Anchor recomputes per-frame during processing to polishing to reviewing transitions, causing visual jump. Eats trust on every successful flow.
**What to ship**: pin anchor at end-of-recording (when final geometry known); or pre-show polishing geometry with hidden cursor so resize happens before tokens stream.

### T2.3: Reviewing-toast adaptive height
**Source**: Session-21 Followup #3
**Effort**: S (1–2h)
**Status**: Hardcoded 160pt. Short messages waste vertical space; long messages get clipped.
**What to ship**: `NSHostingView.fittingSize` or character-count heuristic, clamped to [72, 200] pt.

### T2.4: Undo affordance after insert
**Source**: UX Audit 2026-04-30 friction 1e
**Effort**: S (2–4h)
**Status**: Once text is inserted, no undo from Untype's side. User has to manually delete in target app.
**What to ship**: 2-second post-insert overlay ("Undo Send" pattern). Fires Cmd+Z in target app on click; clears on first keystroke.
**Risk**: target apps with non-standard undo (Notion, web Slack), needs per-app testing.

### T2.5: ContextChip override re-polish loading state
**Source**: UX Audit 2026-04-30 friction 1d (low signal, easy)
**Effort**: S (30–60min)
**Status**: User clicks chip to override context; re-polish runs silently, no acknowledgment.
**What to ship**: subtle spinner on chip during re-polish.

**Tier 2 sequencing**: T2.3 to T2.5 to T2.4 to T2.2 to T2.1 (effort-ascending; small wins compound trust before heavier work).

---

## Tier 3: Reliability hygiene

Cheap, individually small, collectively load-bearing. Ship as opportunity arises, not as a campaign.

### T3.1: Stable ad-hoc signing for `swift build`
**Source**: Session-21 Followup #1
**Effort**: S (1–2h)
**Status**: SPM rebuilds invalidate TCC grants for Mic / Speech / Accessibility, forcing re-grant during dev.
**What to ship**: `bin/build.sh` already does this for app-bundle path; mirror it for SPM bare-binary or document as known limitation.

### T3.2: Hallucination filter retune (OD-001)
**Source**: OD-001
**Effort**: S (data collection 1 week, then 1h)
**Status**: Threshold 0.05 is a starting estimate; field reports show "H.", "Di a.", "Paul" slipping through.
**What to ship**: log `peakLevel` for next 100 dictations; pick a defensible threshold from the histogram.

### T3.3: Chrome Omnibox diagnostic (OD-004)
**Source**: OD-004 / ISS-014
**Effort**: S (15-min probe by founder, then S/M depending on diagnosis)
**Status**: Three competing hypotheses (URL handling, focus race, CGEvent interception). All diagnosable in one sit-down.
**What to ship**: founder runs `UntypeAXProbe` with Chrome's address bar focused, plus `pbpaste` after a failed insert. Diagnosis selects the fix shape.
**Why now**: bilingual pros do *paste-into-Chrome-Omnibox* daily for translated search queries, directly hits ICP.

### T3.4: Electron / VSCode anchor positioning
**Source**: Session-21 Followup #2
**Effort**: M (4–8h)
**Status**: `FocusedElementLocator` returns absurd anchor rects (>70% screen height) in Electron-family apps; overlay appears in wrong place.
**What to ship**: prefer `kAXSelectedTextRangeAttribute` + `kAXBoundsForRangeParameterizedAttribute` for caret-adjacent positioning; fallback to bottom-center; reject obviously-wrong rects.
**Why now**: VSCode + Slack + Notion + Linear are all Electron, covers a lot of the ICP's daily surface.

### T3.5: Branch S.1 alternates popover smoke (OD-005)
**Source**: OD-005
**Effort**: S (15min)
**Status**: Parked since session 53. Verifies that ISS-016 narrowed alternates to Apple-Speech-only paths correctly.
**What to ship**: 15-min smoke on a homophone-rich fixture; either pass/fail in `branches-sor-verification-runbook-2026-04-30.md`, OR drop the runbook entry if alternates are now too narrow to be load-bearing.

---

## Tier 4: Defer (data- or decision-gated)

Don't build these without the trigger event. Tracked in `open-decisions.md`.

| Item | Trigger to revisit |
|---|---|
| OD-003, VAD pre-pass for non-speech hallucinations | Field reports rise above ~once/week, or upstream Whisper fix |
| OD-006, Per-recipient/channel style memory | Validation metric #3 (style trust) saturates and metric #2 stays <70% with "tone wrong" as the dominant edit type |
| OD-007, Voice-driven correction loop | Same trigger as OD-006, but specifically for *post-polish* corrections |
| UX 1a, Sub-200ms `fn` tap feedback | User reports surface this as confusion, not just an audit observation |
| UX 1b, Silence-blob desaturate cue | Same, design refinement, no live pain |
| UX 1d, ContextChip "?" pill on fallback detection | Telemetry shows fallback rate > 20% |

---

## Tier 5: Done (don't re-do)

Confirmed shipped per session 61–70 logs:
- ISS-013, STT "Thank you." hallucination filter
- ISS-015, WhisperKit cold-fetch UX (`Phase.fetchingModel` + progress bar)
- ISS-016, alternates popover narrowed to Apple-Speech-only path
- ISS-017, base prompt + per-profile tone conflict resolved
- Code-health audit 2026-05-04, all load-bearing items fixed via 12 atomic commits in session 70
- File-size 200-line cap restored

---

## What to start this week

**Recommended**: T1.3 to T1.2 to T1.1 in that order. About 1.5–2 weeks of focused work to land the wedge. T1.3 is cheap and de-risks T1.1's prompt design. T1.2 is cheap and makes T1.1 testable. T1.1 is the wedge itself.

Then T2.3 + T2.5 (sub-day each) before declaring "wedge shipped."

T3 items can be slotted in as palate-cleansers between T1/T2 sessions, or whenever a user hits one.

T4 items stay parked until the validation-metrics framework (`validation-metrics-v1.md`) is instrumented and producing data, premature builds here are guesswork.

---

## Cross-cutting: instrument validation metrics in parallel

Per `validation-metrics-v1.md` §"Sequencing": instrument frequency (#1) and cross-app distribution (#4) **first**, ideally before T1.1 ships, so post-launch data is comparable. These are cheap (anonymous local counters with opt-in flush) and unlock everything in Tier 4. Without them, every Tier 4 decision is a guess.
