# Autonomous Execution Brief: Strategy Sweep Follow-Through
**Date written:** 2026-04-30
**Audience:** A future agent session (fresh context, no prior conversation memory) tasked with executing the autonomous follow-through from the 2026-04-30 strategy sweep.
**Status:** Pre-execution brief. Read fully before starting. Each task is independently committable.

---

## 0. Where this came from

The 2026-04-30 strategy sweep produced 5 docs in `knowledge/`:
- `ux-audit-and-takes-2026-04-30.md` (U1)
- `pivot-ideas-2026-04-30.md` (X5)
- `pivot-build-vs-extend.md` (X1)
- `icp-v1.md` (P3)
- `lean-canvas-v1.md` (P1), *contains a reconcile note flagging the C2-vs-C1 ICP question is unresolved*

Plus the prior `code-health-audit-2026-04-30.md` punch list and the BNCDIAG instrumentation on the current branch.

This brief packages the **autonomous-friendly subset** of follow-through work, the items that are safe to ship as code or docs without founder strategic input. It does **not** include items blocked on the founder (BNCDIAG repro, S/O/R verification on the Ubuntu host, naming pick, the C1-vs-C2 reconcile decision).

---

## 1. Pre-flight, read before starting

In this order, then stop and confirm you've understood:

1. `CLAUDE.md` (project root), build commands, file-size rule, architecture rules
2. `.claude/rules/workflow.md`, atomic-commits convention
3. `.claude/rules/swiftui.md`, `.claude/rules/appkit.md`, UI rules (`@Observable`, NSPanel `.nonactivatingPanel`, etc.)
4. `knowledge/code-health-audit-2026-04-30.md`, the punch list T-tasks below reference
5. `knowledge/ux-audit-and-takes-2026-04-30.md` §2, the U-tasks below reference issues 1, 3, 4
6. `knowledge/lean-canvas-v1.md` reconcile note, **important context for why some tasks are in scope and others aren't**

After reading, run `swift build 2>&1 | tail -5` and `swift test 2>&1 | tail -10` to verify the baseline is green. If either fails, **stop and report**, don't try to fix unrelated breakage.

**Branch context:** the current branch when this brief was written is `feature/cutover-diag` with BNCDIAG NSLog instrumentation in place (commit `6096f2f`). Do **not** remove the BNCDIAG instrumentation, that waits on user repro. Branch off `main` for new work to avoid mixing strategy docs with code changes.

---

## 2. Order of operations

Execute in this order. Each phase has a hard stop where you commit and assess before continuing.

| Phase | Task | Effort | Why this order |
|---|---|---|---|
| 1 | **U1-issue-1**, Cleaned·Original toggle on every STT path | 1–2h | Highest user-visible-trust impact; useful regardless of C1-vs-C2 outcome |
| 2 | **T1**, Crash-vector fixes from audit | 1–2h | Highest severity, surgical, tests catch regressions |
| 3 | **T5**, Stale knowledge sweep | 30m | Cheap, clears the workspace before bigger refactors |
| 4 | **T3**, Ollama URL configurability lift | 1h | Small, isolated, unblocks future S/O/R against remote hosts |
| 5 | **U1-issue-4**, Post-insert undo affordance | 2–3h | Trust mechanism; pairs with U1-issue-1 |
| 6 | **U1-issue-3**, Anchor teleport on processing to polishing | 1–2h | UX polish |
| 7 | **T2**, File-size refactor (4 files) | 4–6h | Each file is its own commit; can pause between |
| 8 | **Apple FM polishing adapter**, additive to PolishingRegistry, behind availability flag | 3–5h | macOS 26 defense per X1 §3 |

**Stop after phase 4** and post a status update. The work after that depends on no regressions appearing in phases 1–4.

**Optional, lower-priority "draft" tasks** (do these only if all of phases 1–8 are done OR if a code phase is blocked by something you can't fix):
- Mom Test interview script (P2 deferred deliverable)
- Refresh of `research/competitive-landscape.md` (20-day-old)
- Translation polish prompt prototype + offline eval (only if `CloudPolishingAdapter`'s shape supports it without rework)

---

## 3. Task specs

### U1-issue-1: Cleaned·Original toggle on every STT path

**Problem:** `Untype/Window/BarView.swift:36-58`'s `reviewingBody` only exposes the toggle when `hasOriginal` is true, which depends on `effectiveOriginalText` returning non-nil. For non-Apple-Speech STT paths (Groq / RemoteWhisper / WhisperKit) `lastTranscriptionSegments` is empty, so the toggle hides, and users have no way to verify what they actually said vs what was polished. Single largest trust gap in the product.

**Change:** make the toggle visible whenever `lastOriginalText` is non-nil, regardless of whether per-segment alternates exist. Tappable alternates remain Apple-Speech-only as an *enrichment* of the always-visible toggle.

**Files to touch:**
- `Untype/Window/BarView.swift`, change the `hasOriginal` derivation in `reviewingBody`. Currently uses `effectiveOriginalText`; should fall back to `lastOriginalText`.
- `Untype/State/AppState.swift`, verify `lastOriginalText` is set on **every** path that lands in `.reviewing`, not just Apple-Speech. Check `AppStateReducer` `transcriptFinalized` handling.
- Possibly `Sources/UntypeCore/Processing/PostTranscriptionRoute.swift`, make sure raw transcript flows through for all providers.

**Verification:**
- `swift build && swift test`
- Manual smoke: dictate via each STT provider (Apple Speech, Groq, RemoteWhisper if reachable), confirm toggle appears in reviewing toast on each.
- For RemoteWhisper / Groq paths where Untype can't be tested without external services, write a unit test asserting `AppState.lastOriginalText != nil` after a `transcriptFinalized` event with a non-empty transcript.

**Commit:** `fix(window): show Cleaned·Original toggle for all STT providers, not just Apple Speech`

**Escape hatch:** if `lastOriginalText` isn't actually set on non-Apple paths (you discover this is wired to `lastTranscriptionSegments`-only), the fix shifts to `AppStateReducer`, set `lastOriginalText` from the raw transcript on `transcriptFinalized` regardless of segment availability. Smaller change in BarView, larger in reducer, but same outcome.

---

### T1: Crash-vector fixes (audit critical items 1–3)

**Problem:** `knowledge/code-health-audit-2026-04-30.md` flags three AX force-cast hot spots and 8 IUO stored properties on AppDelegate. Each is a runtime trap waiting to happen.

**Specific sites** (verify line numbers against current source, they may have drifted):
- `Untype/Window/ContextDetector.swift:94`, force-cast after CF type-check
- `Untype/Window/FocusedElementLocator.swift:32, 84, 85`, three AX value force-casts
- `Untype/App/ContextCaptureCoordinator.swift:52`, force-cast after type-check
- `Untype/App/AppDelegate.swift:9-16`, 8 IUO stored properties; check assignment paths

**Change pattern:**
- Force-casts to `guard let x = value as? AXUIElement else { return nil }` (or appropriate fallback)
- IUOs to either prove all assignment paths run before any access, or convert to optionals with nil-guard at call sites

**Verification:** `swift build && swift test`. Existing tests cover the seams; if a test breaks, the IUO removal exposed a real gap, surface it, don't paper over.

**Commits:** one per file (atomic). E.g.:
- `fix(window): replace AX force-casts with optional bridges in FocusedElementLocator`
- `fix(window): replace force-cast with optional bridge in ContextDetector`
- `fix(app): convert AppDelegate IUO properties to optionals with explicit nil checks`

**Escape hatch:** if an IUO conversion cascades into >5 call-site changes per property, stop and split into two commits per property: one to convert, one to update call sites.

---

### T5: Stale knowledge sweep

**Problem:** Several `knowledge/` docs are stale; clutters orientation for future agents.

**Files to archive** (move to `knowledge/archive/`, create directory if it doesn't exist):
- `knowledge/phase3-ax-feasibility-2026-04-22.md`, Phase 3 (threading + AX) deprioritized
- `knowledge/phase3-thread-reading-integration-spec-2026-04-22.md`, same
- `knowledge/project-status-2026-04-22.md`, superseded by session 60 logs

**Files to update:** none. Don't try to author a fresh `project-status`, that's a `/report` invocation, not a manual write.

**Verification:** `git status` shows clean rename, no Swift code touched.

**Commit:** `docs(knowledge): archive deprioritized phase 3 and stale project-status`

---

### T3: Ollama URL configurability lift

**Problem:** `Sources/UntypeCore/Processing/CloudProviderConfig.swift`'s `ollama()` factory hardcodes `http://localhost:11434/v1`. Per session 60 followup notes, this should mirror `RemoteWhisperSTTDescriptor`'s `@AppStorage`-driven URL pattern so users can point Ollama at a remote host.

**Change:**
- Add an `@AppStorage`-backed setting key (e.g. `untype.ollama.baseURL`) with default `http://localhost:11434/v1`.
- `CloudProviderConfig.ollama()` reads from the setting, not a constant.
- Add UI surface in `Untype/Settings/SettingsPolishingSection.swift` (mirror the RemoteWhisper STT URL field pattern).

**Files to touch:**
- `Sources/UntypeCore/Processing/CloudProviderConfig.swift`
- `Untype/Settings/SettingsPolishingSection.swift`
- `Untype/Settings/SettingsStore.swift`, register the new key if needed
- Test fixture in `Tests/UntypeCoreTests/OllamaPolishingAdapterTests.swift` if URL injection is testable

**Verification:** `swift build && swift test`. Manual smoke: change URL in settings, confirm Ollama adapter uses it on the next polish call.

**Commit:** `feat(settings): make Ollama base URL configurable via @AppStorage`

---

### U1-issue-4: Post-insert undo affordance

**Problem:** Insert is one-shot. If the polished text was wrong, recovery is `cmd-z` in the target app, which works in some apps and not others. Per U1 audit §1e, a 2-second post-insert "undo" overlay (Gmail-style) is high-value at low cost.

**Change shape:**
- Add `.justInserted(text: String)` phase to `AppState.Phase` between `.inserting` and `.idle`.
- Phase auto-dismisses after 2s via a Task in the reducer effect chain.
- During `.justInserted`, the overlay shows a compact bar with "Inserted • ⌘Z to undo · Esc to dismiss" and the first ~40 chars of inserted text.
- `cmd-z` from this state triggers an "undo insert" effect, text removal via CGEvent backspace × N where N = length of inserted text.

**Files to touch:**
- `Untype/State/AppState.swift`, add phase case
- `Untype/State/AppStateReducer.swift`, handle `inserting to justInserted to idle` transitions
- `Untype/State/AppEffect.swift`, add `undoInsert` effect
- `Untype/Window/BarView.swift`, render the new phase
- `Untype/Hotkey/KeyboardHandler.swift`, capture cmd-z while phase is `.justInserted`
- `Untype/Insertion/TextInserter.swift`, implement `undoInsert(charCount:)` via CGEvent
- `Tests/UntypeTests/AppStateReducerTests.swift`, cover the new transitions

**Verification:** `swift build && swift test`. Manual smoke: dictate, insert, see the undo bar, hit cmd-z within 2s, confirm text is removed from target app.

**Commit:** `feat(state): add post-insert undo phase with 2s window`

**Escape hatch:** if undoing via CGEvent backspace turns out unreliable across apps (likely in some Electron / web contexts), ship the phase + bar without the cmd-z action, just the visual confirmation that insert happened, then auto-dismiss. The visual signal alone is still useful, and a future iteration can add reliable undo per-app.

---

### U1-issue-3: Anchor teleport on processing to polishing

**Problem:** When the first polish token arrives, phase flips `processing to polishing` and the panel jumps from compact-bar (48pt) to reviewing-toast (≥96pt). If the focused-element anchor flipped from "above" to "below" during the resize, the panel teleports across the screen mid-stream.

**Change:** decide the anchor *once*, at end of recording (when the toast geometry is known), not per-frame. Two implementation options:

1. *Resize-at-processing-start:* show the polishing geometry (≥96pt) from the moment `.processing` begins, with a hidden cursor. The first-token transition is then text-only, no resize.
2. *Pin anchor for duration:* cache the anchor decision in `OverlayController` at the moment phase becomes `.processing` and reuse it through `.polishing` and `.reviewing` until phase returns to `.idle` or `.error`.

Option 1 is simpler. Recommend that path unless option 2 turns out cleaner during implementation.

**Files to touch:**
- `Untype/Window/OverlayController.swift`, `refreshLayout` and `Self.size(for:state:)`
- Possibly `Untype/Window/OverlayPanel.swift`, `setGeometry` if anchor caching moves there

**Verification:** `swift build && swift test`. Manual smoke: dictate near top of screen and near bottom of screen; confirm the panel doesn't visibly teleport during the first polish token.

**Commit:** `fix(window): show polishing geometry from processing start to prevent anchor teleport`

---

### T2: File-size refactor (4 files over 200 LOC)

**Problem:** `RecordingCoordinator.swift` (332 LOC), `AppDelegate.swift` (234), `ProcessingCoordinator.swift` (224), `BarView.swift` (211) all violate the 200-LOC project rule. Audit names extraction targets per file.

**Per-file extraction targets** (from `knowledge/code-health-audit-2026-04-30.md`, verify line ranges against current source):
- **`RecordingCoordinator.swift`** (332 to ~150): extract `transcriberFactory` + speech-permission glue to `TranscriberLifecycle`; stream handlers to `TranscriptionStreamHandler` (or check if `RecordingCoordinator+Stream.swift` already absorbed this).
- **`AppDelegate.swift`** (234 to ~120): extract effect-handler closure to `EffectCoordinator`; phase-observation Task to `PhaseObserver`; profile-override to `ProfileOverrideHandler`.
- **`ProcessingCoordinator.swift`** (224 to ~140): extract stream-consumption loop to `StreamConsumer`; error-mapping to `ErrorMapper`. (Note: existing `+Stream` and `+Errors` extensions may already cover this, verify before adding new files.)
- **`BarView.swift`** (211 to ~140): extract `reviewingBody` builder to `ReviewingBodyBuilder` (separate file or local builder); `AppError` extension already in its own file (`Untype/Window/AppErrorView.swift`) per the recent refactor.

**Order:** do one file per commit. Run `swift test` after each. If a refactor cascades unexpectedly (>2 files modified beyond the target), stop and report.

**Verification per commit:** `swift build && swift test`.

**Commits:**
- `refactor(app): split RecordingCoordinator transcriber lifecycle and stream handlers`
- `refactor(app): split AppDelegate effect handling and phase observation`
- `refactor(app): split ProcessingCoordinator stream consumer and error mapper`
- `refactor(window): extract BarView reviewingBody builder`

**Escape hatch:** if any single file's split needs >3 new files, that's a smell, stop, write up the constraint in the commit body, and surface it for review rather than forcing the split.

---

### Apple Foundation Models polishing adapter

**Problem:** Per X1 §3 "Recommendation 1," shipping an Apple FM polish adapter is the macOS 26 defense. It's the single biggest existential risk: if Apple's stack catches up on polish quality and Untype isn't *the better Apple-FM client* on macOS 26, the standalone shape's polish moat collapses.

**Change:** add `AppleFMPolishingAdapter` parallel to `CloudPolishingAdapter` and `OllamaPolishingAdapter`. Behind `#available(macOS 26, *)` availability check. Register in `PolishingRegistry`.

**Files to touch:**
- `Sources/UntypeCore/Processing/AppleFMPolishingAdapter.swift` (new)
- `Sources/UntypeCore/Processing/PolishingRegistry.swift`, register
- `Untype/Settings/SettingsPolishingSection.swift`, surface as a provider option (gated by availability)
- `Tests/UntypeCoreTests/AppleFMPolishingAdapterTests.swift` (new), testable parts only; mock the FM API since it requires macOS 26 runtime

**Verification:** `swift build && swift test`. Manual smoke only possible on macOS 26, if you're on macOS 14/15, skip manual and rely on tests + availability check.

**Commit:** `feat(processing): add Apple Foundation Models polishing adapter (macOS 26+)`

**Escape hatch:** if the Apple FM API surface area is more complex than the Cloud adapter shape (it likely is, FM has session/context concepts that don't map directly to OpenAI-compatible chat completions), don't force the same protocol shape. Either extend `LLMProvider` with optional capability methods, or ship as a separate `FoundationModelStage` and route at the `ProcessingRouter` level. Document the decision in the commit body.

---

### Optional: Mom Test interview script (P2 deferred deliverable)

**Why this is optional:** the C1-vs-C2 reconcile note in `lean-canvas-v1.md` flags that the primary ICP isn't yet decided. Drafting interview scripts targeted at one ICP is wasted work if the founder picks the other. Draft this only if **both code phases 1–8 are complete** and the founder hasn't yet weighed in on the reconcile.

**If you do draft it:**
- 3 variant scripts: ex-Wispr users, Superwhisper power users, native-dictation users
- 12 questions each, no leading questions (Mom Test rules)
- Source pain points from `research/user-pain-points-and-desires-2026.md`
- Output: `knowledge/discovery/mom-test-scripts-v1.md`

---

### Optional: Refresh competitive landscape

**Why optional:** `research/competitive-landscape.md` is 20 days old at the time of this brief. Monthly refresh is reasonable; quarterly is fine. Only refresh if you've finished the code phases and are looking for additional autonomous work.

**Scope:**
- Wispr Flow: any product updates, pricing changes, new privacy stories
- Superwhisper changelog
- New Product Hunt entrants in the dictation space
- macOS Sequoia / 26 dictation feature updates from Apple
- Diff-style append to the existing doc, don't rewrite

---

### Optional: Translation polish prompt prototype

**Why optional and risky:** the lean-canvas reconcile note flagged that the C2 (multilingual) ICP commitment is unresolved. Building a translation polish prompt presumes that pivot is happening. Don't do this unless the founder confirms the C2 direction.

**If confirmed:**
- Read current `Sources/UntypeCore/Processing/CloudPolishingAdapter.swift` to understand prompt shape
- Add a `translation` `ContextProfile` case (or a sub-mode of `general`)
- Draft a prompt that instructs L1-to-L2 translation with native-fluent register awareness
- No need to ship UI for it yet, just make it invokable from a test fixture

---

## 4. Hard non-goals, do NOT touch

- **BNCDIAG NSLog instrumentation** (commit `6096f2f`), leave in place; user is using it for live repro.
- **Naming pivot tooling** in `bin/`, user picks the name; don't run rename.
- **S/O/R verification suite**, blocked on Ubuntu inference host; don't try to run it.
- **Cutover-bug fixes** (#1 rapid retry, #2 cancel during polish, #6 profile chip override, #7 reviewing toggle missing), these wait on user repro logs.
- **Strategy docs from 2026-04-30** (`ux-audit-and-takes-…`, `pivot-…`, `icp-v1`, `lean-canvas-v1`), don't rewrite these without explicit instruction. They contain hypothesis-status content and a reconcile note that's load-bearing.
- **CLAUDE.md**, no changes unless the founder explicitly asks.

---

## 5. Decision points, stop and ask

If you encounter any of the following, **stop** and post a concise status update rather than continuing:

1. **Build or test breaks before you've made a change.** This is a baseline regression you didn't introduce; surface it.
2. **A T1 IUO conversion cascades into a major lifecycle redesign.** That's not surgical; it's a refactor. Pause.
3. **A T2 file split exceeds 3 new files for one file.** The architecture is fighting the split; report and stop.
4. **The Apple FM API surface doesn't match `LLMProvider`'s shape.** Don't force the abstraction. Document and pause.
5. **Any phase-5+ task surfaces a bug in a phase-1-to-4 change you already shipped.** Roll back the new work, don't pile fixes on top.
6. **You discover the C1-vs-C2 ICP question has been resolved by the founder** (in a session log, in chat, in a memory note). Confirm which direction won and re-read this brief for adjusted priorities.

---

## 6. End-of-run checklist

After phases 1–8 (or wherever you stop):

- [ ] All commits use the `prefix(topic): message` convention from `CLAUDE.md`
- [ ] No commit batches multiple unrelated changes
- [ ] No `Co-Authored-By` trailer
- [ ] `swift build && swift test` green at the tip
- [ ] No BNCDIAG instrumentation removed
- [ ] No CLAUDE.md changes
- [ ] No strategy docs (2026-04-30 set) rewritten
- [ ] Status summary written: which phases ran, which were skipped and why, any escape-hatch decisions made
- [ ] If any phase was skipped due to a decision point, the reason is in the status summary

---

## 7. Status reporting format

When you finish (or hit a stopping point), report in this shape:

```
Ran phases: [list]
Skipped phases: [list with reason]
Commits added: [N, on branch <name>]
Tests: [green / N failures with details]
Decision points hit: [list, none if none]
Open follow-ups: [list, none if none]
```

Don't write a long retrospective. The user wants signal density.
