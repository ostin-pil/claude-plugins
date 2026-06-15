# Follow-Up Brief: Post Strategy-Sweep
**Date written:** 2026-05-01 **Audience:** A future agent session (fresh context) picking up after session 61 closed. **Status:** Pre-execution brief. Read fully before starting. Each task is independently committable.

---

## 0. Where this came from

Session 61 (2026-05-01) executed `knowledge/autonomous-execution-brief-2026-04-30.md` end-to-end and manually smoke-tested phases 5 and 6 of that brief. Smoke surfaced three findings:

1. **Fixed inline** (commit `5601328`): fn-press during `.inserting` / `.justInserted` was a state-machine dead zone, extended the reducer's permissive sets to include both phases.
2. **Deferred, Chrome Omnibox paste fails.** Pre-existing.
3. **Deferred, Whisper "Thank you." hallucination on near-empty audio.** Pre-existing, affects every recording.

This brief packages those two findings plus the remaining items that were either intentionally out-of-scope from the prior brief or unblocked by today's smoke results. As before, items blocked on the founder (BNCDIAG repro, ICP reconcile, Ubuntu inference host setup) are explicitly excluded, they have their own gating events.

---

## 1. Pre-flight, read before starting

In this order:

1. `CLAUDE.md`, build commands, file-size rule, architecture rules.
2. `.claude/rules/workflow.md`, atomic-commits convention.
3. `sessions/2026-05-01_session_61.md` §Smoke results, the two deferred findings with full context.
4. `Sources/UntypeCore/Processing/AppleSpeechService.swift` and `Sources/UntypeCore/Transcription/RemoteWhisperSTTProvider.swift` , only relevant for Task 1 (hallucination filter): you'll need to know which providers go through which post-STT path.
5. `Untype/Insertion/TextInserter.swift`, only relevant for Task 2 (Chrome Omnibox): the current insertion API.

After reading: `swift build 2>&1 | tail -5` and `swift test 2>&1 | tail -10`. Baseline at session-61 close was 265 passing, 8 skipped, 0 failures, build clean. If either fails, **stop and report**, don't fix unrelated breakage.

**Branch context:** `main` is the current tip. `feature/cutover-diag` holds BNCDIAG instrumentation (commit `6096f2f`), leave it alone. Branch off `main` for new work.

---

## 2. Order of operations

| Phase | Task | Effort | Why this order |
|---|---|---|---|
| 1 | **Whisper hallucination filter** | 2–3h | Highest impact, affects every recording on every Whisper-family STT path. Closing this materially raises trust per recording. |
| 2 | **Chrome Omnibox paste investigation** | 1–2h | Diagnostic first; may surface either a small fix or a "drop the cmd-z hint there" mitigation. Bounded scope; could conclude as a no-action documented finding. |
| 3 | **Branch S.1 alternates popover verification** | 15m | Closeable on the Mac without an inference host (per session 60 §Closeable today). Retires one of the three deferred S/O/R items. |

**Stop after phase 1** and post a status update. Phase 1 touches a load-bearing path (the silence/hallucination gate) and warrants verification before any layered work.

Optional, lower-priority: nothing here is autonomous. The remaining deferred items (cutover bugs, ICP reconcile, Ubuntu setup) wait on user action.

---

## 3. Task specs

### Task 1: Whisper hallucination filter

**Problem.** When a recording is mostly silence with brief noise, Whisper-family STT models (Groq's Whisper, RemoteWhisper running faster-whisper, WhisperKit) frequently hallucinate high-frequency training-data phrases, most often "Thank you.", "Thanks for watching.", "Subtitles by …", because those dominate the YouTube captions corpus. Untype's existing silence gate (`BlobWaveform.isSilent` to `.transcriptDroppedAsSilent`) catches fully-silent recordings but not "mostly silent with a brief noise" ones.

**Where the gate currently lives.** Search the codebase for `isSilent` and `transcriptDroppedAsSilent` to find the existing silence gate. The new filter sits adjacent to it: after the transcript is finalised but before it propagates to `.processing`, inspect the audio level history alongside the transcript text.

**Approach.** Add a post-STT hallucination check that fires `.transcriptDroppedAsSilent` when ALL of the following hold:
- Audio level history (the rolling RMS buffer used by the silence detector) was uniformly below a threshold for the recording's duration, call it the "low-energy" check.
- The transcript matches a small allow-list of known hallucination phrases (case-insensitive, whitespace-trimmed).

The two conjoined gates is load-bearing: the energy check alone would drop legitimate quiet speech; the phrase check alone would drop legitimate "Thank you." dictations. Combined, they catch the specific hallucination pattern.

**Hallucination phrase allow-list (initial, expand from logs):**
- "Thank you." / "Thank you" / "Thanks." / "Thanks"
- "Thanks for watching." / "Thanks for watching"
- "Subtitles by the Amara.org community"
- "Subtitled by..." / "Subtitles by..."
- ".." / "." , single-token punctuation-only outputs
- (empty string after trim, already handled by the existing `polishingDroppedAsEmpty` path; verify the analogous transcript- level path exists)

Match exact (after lowercasing + trimming + collapsing whitespace); do NOT regex-match the substring inside a longer transcript, a legitimate dictation could end with "thanks".

**Files to touch:**
- The silence-gate site (find it via grep). Likely `Untype/App/RecordingCoordinator+Stream.swift` or similar, the point where the finalised transcript is dispatched as `.transcriptFinalized`.
- Possibly a new `Sources/UntypeCore/Transcription/HallucinationFilter.swift` if the pure-function check is non-trivial, keeps it unit-testable.

**Verification:**
- `swift build && swift test`
- Unit tests in `Tests/UntypeCoreTests/HallucinationFilterTests.swift` covering: each allow-list phrase + low energy to drop; same phrase
  + high energy to pass; non-allow-list phrase + low energy to pass (don't drop legitimate quiet speech).
- Manual smoke (this needs the user, so it's optional for the autonomous run, flag it in the status update): record while silent for 3–5 seconds, confirm no "Thank you." appears in the reviewing toast. Repeat with a real "Thanks." dictated firmly, confirm it goes through.

**Commits:**
- `feat(transcription): add hallucination filter for low-energy recordings`

**Escape hatch:** if the audio level history isn't readily accessible at the post-STT decision site, the gate can fall back to phrase-match only, but that risks dropping legitimate "Thank you." dictations. If you take this path, log it loudly and surface the trade-off in the commit body. Better: route the level history to the decision point, even if it requires a small plumbing change.

---

### Task 2: Chrome Omnibox paste investigation

**Problem.** During smoke (session 61), inserting cleaned text into Chrome's address bar (Omnibox) silently failed. Other text fields in Chrome (page-body inputs, contenteditables) work fine. Untype inserts via clipboard paste (`TextInserter.insert(_:)` to set NSPasteboard, then send Cmd+V via CGEvent).

**Hypotheses, ranked by likelihood:**

1. **Chrome Omnibox auto-completes URLs from the clipboard differently.** The Omnibox treats clipboard paste as "go to this URL" rather than plain text input. If the cleaned transcript looks like a URL, this may work; otherwise Chrome may discard it. Test by dictating a URL vs a sentence into the Omnibox and comparing.
2. **Focus race during Untype's overlay show.** Untype's overlay is a non-activating panel; Chrome shouldn't lose focus. But if the AX focused-element changes momentarily (e.g. when the overlay reveals itself), Chrome's Omnibox might snap back to the page body.
3. **CGEvent Cmd+V is intercepted by Chrome's command system before reaching the Omnibox.** Chrome has its own keyboard handling; the global CGEvent post may not register as a real Cmd+V keystroke in the address bar's input chain.

**Diagnostic approach (read-only first):**
- Write `axinspect.sh` or use `UntypeAXProbe` (already a target in the project) to capture the AX focused-element at three moments: (a) when the user presses fn, (b) when Untype shows the overlay, (c) when Untype posts the Cmd+V CGEvent. If the focused element changes between (a) and (c), that's the focus-race hypothesis.
- Verify the clipboard actually has the cleaned text after Untype's paste (`pbpaste` after a failed insert into the Omnibox). If yes, the issue is delivery; if no, the issue is preparation.

**Decision tree:**
- If hypothesis 1 (URL handling) is the actual cause: the Omnibox is genuinely a poor target for arbitrary dictation. Mitigation: detect bundle-id `com.google.Chrome` + AX role identifying the Omnibox; show "Address bar dictation is unsupported" hint OR drop the cmd-z hint specifically there. **Do NOT** rewrite the insertion path for this single case.
- If hypothesis 2 (focus race) is the actual cause: the fix is a race against Chrome's focus management, likely needs a small post-paste delay or a focus-restore after the overlay shows. Could be small.
- If hypothesis 3 (CGEvent interception) is the actual cause: the fix would require alternative paste APIs (NSEvent, AppleScript) that have their own portability issues. Likely conclude as documented limitation rather than fix.

**Files to touch (only after diagnosis):**
- `Untype/Insertion/TextInserter.swift` if a fix is genuinely small.
- `Untype/Window/BarView.swift` if mitigation is "drop the cmd-z hint in Chrome".
- New `knowledge/chrome-omnibox-paste-investigation-2026-05-NN.md` documenting findings if no code fix is appropriate.

**Verification:**
- `swift build && swift test` after any code change.
- Manual: dictate into Chrome Omnibox vs Chrome page body vs Safari URL bar, confirm where it works and where it doesn't.

**Commit:**
- `fix(insertion): <specific fix>` if a fix lands.
- `docs(knowledge): document Chrome Omnibox insertion limitation` if not.

**Escape hatch:** if diagnosis shows this requires Chrome-specific behavior (e.g. AX-walk into the Omnibox to set the value field directly rather than paste), STOP and surface the trade-off, that's a per-app insertion strategy, which is a much larger architectural change than a single bug fix.

---

### Task 3: Branch S.1 alternates popover verification

**Problem.** Session 60 §Closeable today flagged the alternates popover regression in `OriginalAlternatesView` as the only S/O/R verification item that doesn't need the Ubuntu inference host. It's been deferred since session 53, about 8 days at the time of this brief.

**Steps (5 min total):**
- `./bin/build.sh && open Build/Untype.app`
- Dictate a short sentence with at least one homophone candidate (e.g. "I need a cup of coffin", Apple Speech reliably scores "coffee" as an alternate).
- In the reviewing toast, toggle to Original. Confirm tappable alternates appear under each segment.
- Tap an alternate. Confirm it replaces the segment in-place.
- Insert. Confirm the replaced text reaches the target app.

**Verification:**
- Above is the verification.

**Output:**
- If all green, append a one-line PASS to `knowledge/branches-sor-verification-runbook-2026-04-30.md` §S.1.
- If any step fails, file findings inline in the runbook and surface them in the status update. Do NOT attempt a fix in this run, alternates code is a known fragile area; investigation needs its own scoped session.

**Commit (only on PASS or factual finding update):**
- `docs(knowledge): mark S.1 alternates popover PASS` (or `… NN findings`)

---

## 4. Hard non-goals, do NOT touch

- **BNCDIAG instrumentation** on `feature/cutover-diag`, leave in place.
- **CLAUDE.md**, no changes.
- **Strategy docs** from 2026-04-30 (`ux-audit-and-takes-…`, `pivot-…`, `icp-v1`, `lean-canvas-v1`, the prior `autonomous-execution-brief`), don't rewrite.
- **Push to origin**, local main is 178+ commits ahead; user controls the push cadence.
- **Cutover bug fixes** (#1/#2/#6/#7), wait on user repro.
- **Ubuntu inference host**, blocked on user setup.
- **C1-vs-C2 ICP reconcile**, pure user decision.

---

## 5. Decision points, stop and ask

If any of the following surface, post a concise status update rather than continuing:

1. **Build or test breaks before any change.** Surface; don't fix.
2. **Hallucination filter requires AppState plumbing changes** beyond adding the gate at the existing silence-detector site. That's a bigger refactor than this brief assumes.
3. **Chrome Omnibox diagnosis points to per-app insertion strategy.** That's an architectural decision, not a bug fix. Surface and stop.
4. **Branch S.1 fails.** Document findings; don't attempt fix.
5. **Manual-smoke step on Task 1 surfaces a regression in unrelated STT paths.** The hallucination filter shouldn't affect non-hallucinated transcripts. If it does, the threshold or match logic is wrong.

---

## 6. End-of-run checklist

- [ ] All commits use `prefix(topic): message` per CLAUDE.md.
- [ ] No commit batches multiple unrelated changes.
- [ ] No `Co-Authored-By` trailer.
- [ ] `swift build && swift test` green at the tip.
- [ ] No BNCDIAG instrumentation removed.
- [ ] No CLAUDE.md or strategy doc changes.
- [ ] Status summary written: which tasks ran, which were skipped/
      stopped and why, any escape-hatch decisions made.

---

## 7. Status reporting format

```
Ran tasks: [list]
Skipped tasks: [list with reason]
Commits added: [N, on branch <name>]
Tests: [green / N failures with details]
Decision points hit: [list, none if none]
Open follow-ups: [list, none if none]
```
