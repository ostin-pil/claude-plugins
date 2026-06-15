<!-- prose-check: skip bold-colon-opener -->
# Open Decisions

Tracks matters surfaced and acknowledged but not yet decided. Distinct from:

- **`issues.md`**, concrete bugs/regressions with a fix shape (open or resolved). Move an entry from here to `issues.md` once the decision is made and the work is scoped.
- **Session logs**, what happened in a given session.
- **`knowledge/follow-up-brief-*`**, staged execution plans for an agent run.

An entry belongs here when *we know it exists* but *we have not yet decided what to do about it*. Close (delete or strike through) once decided, leaving a one-line resolution note pointing to the resulting ISS-* / commit / session log.

## Format

```
## OD-NNN: Short title
**Surfaced**: session N / commit / smoke / brief
**Status**: needs data | needs founder call | parked | needs scope
**Trigger to revisit**: the empirical or external event that should
unblock the decision

**Context**: what surfaced this and why it isn't a one-liner.

**Options**:
- A: …
- B: …

**Open question**: the single thing the human needs to answer.
```

`Status` values:
- `needs data`, answer is empirical; revisit after the next round of field smoke / fixture run.
- `needs founder call`, non-empirical; a person has to choose.
- `needs scope`, work shape is unclear (effort vs payoff TBD).
- `parked`, known and deliberately deferred; trigger event is in the future.

---

## OD-001: Hallucination filter peak threshold (`0.05`) needs empirical retune
**Surfaced**: session 61 smoke + 2026-05-06 field reports ("H.", "Di a.", "Paul", "What", "and", "So" all slipping through at non-trivial peak)
**Status**: needs data
**Trigger to revisit**: next smoke pass that captures the actual `peakLevel` values for hallucinated outputs (Console.app filter "Untype" to `dropped as hallucination: text=… peak=…` plus the cases that *don't* fire)

**Context**: `HallucinationFilter.lowEnergyPeakThreshold = 0.05` was a starting estimate placed above the existing dead-silence floor (`0.01`) and below normal-speech peaks (~`0.2`–`0.5`+). Field reports include outputs that are short enough to be caught by the word-count rule but only when peak is below `0.05`. If the user's environment routinely lifts peak above that, these slip through.

**Options**:
- A: Raise `lowEnergyPeakThreshold` to `0.08` (catches more, false-positive risk for whispered short commands).
- B: Keep `0.05`, accept the residual slip, and route hard cases through a separate signal (e.g. mean RMS, voice-activity detection).
- C: Drop the energy gate entirely for ≤2-word outputs (controversial, would drop legitimate "yes"/"no" at any volume).

**Open question**: what real `peakLevel` values are these slipping-through outputs producing? Until we have that, picking a new threshold is a guess.

---

## OD-002: Per-profile tone shift strength after ISS-017 prompt fix
**Surfaced**: ISS-017 (commit `1895f3c`) **Status**: needs data **Trigger to revisit**: smoke after the ISS-017 prompt change, pick Chat to Email (or vice versa), confirm the polished output visibly shifts register

**Context**: ISS-017 unblocked the architectural conflict between the base "preserve tone" rule and the per-profile tone hints. The wiring is now consistent. Whether the *magnitude* of the shift is enough is an open empirical question, `ContextProfile.toneDescription` strings are deliberately short ("Casual, conversational. Contractions welcome. Short, direct." etc.) and some smaller / weaker LLM models may still produce near-identical output across profiles even with the conflict resolved.

**Options**:
- A: Leave as is; ISS-017 unblocked the path, magnitude is the model's call.
- B: Make `toneDescription` and `formattingRules` more imperative and concrete, give the model fewer degrees of freedom (e.g. "Use contractions. Skip greetings. Drop trailing periods on single-line messages.").
- C: Add a worked example per profile inside the system prompt ("e.g. transform 'send him the document tomorrow' to '<example>'"). Costs tokens but anchors the LLM.

**Open question**: post-ISS-017, does Chat vs Email actually feel different on the smoke transcripts? If not, B before C.

---

## OD-003: Non-speech / loud-environment hallucinations (peak ≥ threshold)
**Surfaced**: 2026-05-06 field report ("Listening to an instrumental I got 'Red Pot' something") **Status**: needs scope **Trigger to revisit**: enough field reports to justify implementation cost OR a Whisper-side fix shipped upstream

**Context**: `HallucinationFilter` only fires on low-energy recordings. When the mic picks up real audio (music, conversation, fan noise) at normal-speech peak levels, STT models still emit near-random short transcriptions, and the filter does not gate on them. This is a different problem class, voice-activity detection (VAD), not silence detection.

**Options**:
- A: Add a small VAD pre-pass before STT (e.g. WebRTC VAD or Silero) and skip STT entirely for non-voice frames.
- B: Add a confidence-score gate post-STT (where the STT exposes one, Whisper has token-level logprobs).
- C: Document as a known limitation; ask users to dictate in quiet environments.

**Open question**: how often does this actually fire in real use? "I got 'Red Pot' once during an instrumental" might be rare enough to defer indefinitely.

---

## OD-004: ISS-014 Chrome Omnibox paste, diagnostic phase
**Surfaced**: session 61 smoke; brief at `knowledge/follow-up-brief-2026-05-01.md` Task 2 **Status**: needs founder call **Trigger to revisit**: founder runs the AX probe (`UntypeAXProbe`) with Chrome's address bar focused, plus a `pbpaste` after a failed insert

**Context**: ISS-014 has three competing hypotheses (URL handling, focus race, CGEvent interception). All three are diagnosable with a five-minute test session, but none of the diagnosis can run autonomously, it needs a human in front of Chrome with the Omnibox focused. Filed in `issues.md` as "Open (deferred)" since 2026-05-01.

**Options**:
- A: Founder runs the probe to result picks the hypothesis to implement the matching fix or document the limitation.
- B: Ship a Chrome-bundleId-specific "address-bar dictation unsupported" hint without diagnosing, small UX nudge, no risk to the insertion path.
- C: Continue deferring.

**Open question**: how often does the founder dictate into the Omnibox in practice? If rarely, B is cheaper than A.

---

## OD-005: Branch S.1 alternates popover verification
**Surfaced**: session 60 §"Closeable today"; brief at `knowledge/follow-up-brief-2026-05-01.md` Task 3 **Status**: parked **Trigger to revisit**: 15 min on a Mac with a homophone-rich fixture sentence

**Context**: Branch S.1 (alternates popover) was flagged as the only S/O/R verification item that doesn't need the Ubuntu inference host. It's been deferred since session 53. ISS-016 changed the upstream, alternates now only populate in Apple-Speech-only mode, never in cloud-final or hybrid. The verification is still meaningful but the test path narrowed.

**Options**:
- A: Run the smoke (Apple Speech as the only STT, dictate a homophone, tap the popover, swap a word, insert) and append PASS/FAIL to `knowledge/branches-sor-verification-runbook-2026-04-30.md` §S.1.
- B: Drop S.1 from the runbook entirely, alternates are now a narrower feature than the runbook assumed.
- C: Re-scope S.1 to "alternates UI hidden in cloud-final / hybrid mode" (verifying the ISS-016 fix surfaces correctly) instead of the original tap-to-fix behaviour.

**Open question**: does the runbook still treat alternates as a load-bearing feature post-ISS-016, or has it become a niche path?

---

## OD-006: Adaptive style memory per-recipient / per-channel
**Surfaced**: co-founder market doc 2026-05-08; flagged as a candidate moat extension during repo audit
**Status**: parked
**Trigger to revisit**: post-launch behavioural data shows users want the polish to vary by *who they're writing to* (e.g. boss-Slack vs friend-Slack vs PR-comment vs customer-email) more than by app context alone

**Context**: Untype already has per-profile tone (`ContextProfile`), context-by-app/category. The market doc raises a stronger version: style memory keyed on *recipient or channel*, not just app. "How I write to person X in Slack channel Y" is different from "how I write in Slack." If true, this is a possible moat extension, competitors mostly shape tone by app, not by relationship.

The doc is hypothesis, not evidence. No competitor has shipped this. Untype's `validation-metrics-v1.md` metric 4 (cross-app distribution) and metric 3 (style trust) will surface whether per-app polish is sufficient or whether the trust ceiling lives at per-recipient.

**Options**:
- A: Defer until validation data shows per-app tone profiles aren't enough.
- B: Pre-emptively scope a recipient/channel-aware polish pass (read frontmost-app + window/conversation metadata via Accessibility, key style memory by `(app, contact-or-channel-id)` hash), build cost meaningful, signal value unproven.
- C: Rule out, the privacy and complexity costs (storing per-recipient writing-style fingerprints) outweigh the gain.

**Open question**: do C2 bilingual users actually want different polish per recipient, or is per-app/per-profile enough? Wait for metric 3 data before scoping.

---

## OD-007: Voice-driven correction loop ("shorter / softer / keep alive")
**Surfaced**: co-founder market doc 2026-05-08; flagged as a candidate post-polish UX during repo audit
**Status**: parked
**Trigger to revisit**: send-without-edit rate (`validation-metrics-v1.md` metric 2) settles below 70% and the dominant edit type is "make it shorter / softer / less polished" rather than fixing factual errors

**Context**: Untype ships `Cleaned · Original` toggle and manual edit. The market doc proposes a faster correction modality: post-polish, the user voices "сделай короче / мягче / оставь живее" (shorter / softer / keep alive) and the LLM re-renders. Distinct from re-dictating: the user keeps the underlying intent, only adjusts register/length/edge.

Adjacent to S.1 alternates popover (OD-005), but for whole-message style instead of word-level. Competitors don't offer this; Wispr Flow's auto-tone is opaque ("just trust it") and Superwhisper's modes require pre-selection.

**Options**:
- A: Defer until edit-rate data justifies the build cost (LLM re-prompt + UI for the correction phrase capture + voice-vs-typed disambiguation).
- B: Build a typed-only quick-edit ("⌘. to  shorter / softer / longer") first as a cheaper proxy. If it gets used, escalate to voice.
- C: Rule out, adds latency and prompt complexity without clear evidence users want it.

**Open question**: when the polish is wrong, *what kind* of wrong is it? If it's "factually missed something" to re-dictate is the answer. If it's "tone is off" to this is the answer. Need metric-2 data to decide.
