# Cutover-bug test suite, plan

**Status:** ready to implement in a follow-up session.
**Source:** session 58 reported bugs #1/#2/#6/#7 (`sessions/2026-04-27_session_58_cutover-fixes.md`); session diagnosis was code-only and inconclusive. Initial plan was BNCDIAG NSLog instrumentation + manual repro (committed on `feature/cutover-diag`, then reverted by user). This plan replaces the manual-repro path with deterministic XCTest coverage.

## Context (read this before coding)

- Untype is a macOS voice-to-text overlay. Recent sessions 55–58 cut over from direct `AppState` mutation to a pure-reducer + dispatch architecture (`AppStateReducer.reduce(state:event:) -> (state, [effect])`).
- Four bugs reported but never reproduced empirically:
  - **#1**, rapid retry: polish disappears, no `.reviewing`. Hypothesis: LLM returned no-letters-no-digits output, hit `.polishingDroppedAsEmpty` to phase silently goes to `.idle`.
  - **#2**, cancel during polish: not working. Hypothesis: keyboard layer (Esc not caught), or main-actor saturation under 33ms `.polishingPartial` cadence.
  - **#6**, profile-chip override: results unchanged. Hypothesis: LLM produces visually similar output for chosen profiles. Likely **not a code bug**.
  - **#7**, reviewing toggle missing on one occasion. Hypothesis: `effectiveOriginalText` returned nil/empty when phase reached `.reviewing`.
- Key architectural facts:
  - `AppState.phase` is `private(set)`, only mutated via `AppState.dispatch(_:)`.
  - Reducer state = `(phase, processingRequestId, lastOriginalText)`. Auxiliary fields (`segments`, `prefix`, `overrides`, `capturedAppContext`, `overriddenProfile`, etc.) are mutated directly by coordinators and reset via `AppEffect.resetAuxiliary` to `AppState.resetAuxiliary()`.
  - `RecordingCoordinator+Stream.swift` direct-mutates `appState.lastTranscriptionSegments` / `lastOriginalPrefix` / `segmentOverrides` immediately **before** dispatching `.transcriptFinalized`. This ordering is the suspected race for bug #7.
  - New phase since last plan: `.justInserted(text:)` between `.inserting` and `.idle`. Reducer must handle `.dismiss` from this phase.
  - New filter since last plan: `HallucinationFilter` in `RecordingCoordinator+Stream.swift` rejects YouTube-caption-style false transcripts ("Thank you.", "Thanks for watching.") on near-silent audio.
- Existing test surface (read these before adding):
  - `Tests/UntypeTests/AppStateReducerTests.swift`, 16+ tests, model for new reducer cases.
  - `Tests/UntypeTests/ProcessingCoordinatorTests.swift`, uses `ScriptedLLMProvider` from `TestSupport/`, model for new coordinator tests. Has `enterProcessing`, `waitForReviewing`, `waitForError`, `waitFor` helpers.
  - `Tests/UntypeTests/AppStateOriginalTextTests.swift`, bug #7 territory, three tests for `effectiveOriginalText` paths.
  - `Tests/UntypeTests/TestSupport/`, `ScriptedSTTStage`, `ScriptedTranscriberFactory`, `FakeAudioRecorder`, `ScriptedLLMProvider`. Use these; do not invent new doubles where one already exists.

## Out of scope

- LLM golden-output snapshot tests for bug #6 (model behavior, flaky, not worth the cost). The plan only verifies *wiring*, that the override flows into `LLMRequest.context`. Visual output similarity is an eyeball / prompt-engineering concern.
- XCUITest e2e for bug #2's keyboard layer. Out of scope unless the unit-level seam test fails to surface the cause.
- Anything in the rename namespace (Untype to Untype). The codebase rename is deliberately not yet done per `MEMORY.md to project_rename_bounce_to_untype.md`. Treat all paths as `Untype/`.
- `KeyboardHandler.start()` / NSEvent global monitor wiring itself. Not testable without faking system event injection.
- The deferred Ollama-localhost-hardcode followup (per session 60).

## Workflow

- Branch: `feature/cutover-bug-tests`, off current `main`.
- Commits: one per bug (4 atomic commits) plus prep commits where needed.
  - Commit 1 (prep): `test(support): add RecordingLLMProvider test double` (only if tests for #6 need it, see §Bug #6).
  - Commit 2 (prep): `refactor(hotkey): extract testable seam from KeyboardHandler` (only for #2's keyboard layer; can be skipped, see §Bug #2).
  - Commit 3: `test(state): cover polishingDroppedAsEmpty path (bug #1)`.
  - Commit 4: `test(state): cover dismiss from in-flight phases (bug #2 state half)`.
  - Commit 5: `test(processing): cover override profile wiring (bug #6 wiring)`.
  - Commit 6: `test(state): cover late-stream-after-dismiss race (bug #7)`.
- `swift build && swift test` green at every commit.
- Final summary: which tests pass, which **fail as expected** (those are real bug confirmations), what was learned.

## Test specs

Each test below: file path to test name to setup to assertion to significance.

### Bug #1, `.polishingDroppedAsEmpty` path

**File:** `Tests/UntypeTests/AppStateReducerTests.swift` (extend).

```swift
func testPolishingDroppedAsEmpty_matchingId_returnsToIdleWithReset() {
    let id = UUID()
    let s0 = ReducerState(phase: .polishing(partialText: "h"),
                          processingRequestId: id,
                          lastOriginalText: "raw")
    let (next, effects) = AppStateReducer.reduce(
        state: s0, event: .polishingDroppedAsEmpty(requestId: id))
    XCTAssertEqual(next.phase, .idle)
    XCTAssertEqual(effects, [.resetAuxiliary])
}

func testPolishingDroppedAsEmpty_staleId_isDropped() {
    let liveId = UUID(); let staleId = UUID()
    let s0 = ReducerState(phase: .polishing(partialText: "h"),
                          processingRequestId: liveId)
    let (next, effects) = AppStateReducer.reduce(
        state: s0, event: .polishingDroppedAsEmpty(requestId: staleId))
    XCTAssertEqual(next.phase, .polishing(partialText: "h"))
    XCTAssertTrue(effects.isEmpty)
}
```

**File:** `Tests/UntypeTests/ProcessingCoordinatorTests.swift` (extend).

```swift
func testWhitespaceOnlyResponse_returnsToIdle_doesNotReachReviewing() async {
    let appState = AppState()
    let (rawText, requestId) = enterProcessing(appState, rawText: "raw")
    let provider = ScriptedLLMProvider(script: [
        .finished(.scripted("   …   "))   // no letters or digits
    ])
    let coord = makeCoordinator(provider: provider, appState: appState)
    coord.startProcessing(rawText: rawText, requestId: requestId)
    try? await waitForIdle(appState, timeout: .seconds(1))   // add helper if missing
    XCTAssertEqual(appState.phase, .idle)
    if case .reviewing = appState.phase { XCTFail("must not reach reviewing") }
}

func testEmptyFinishedResponse_returnsToIdle() async { /* outputText == "" */ }
func testPunctuationOnlyResponse_returnsToIdle() async { /* "..." */ }
```

`waitForIdle` helper: mirror `waitForReviewing`, predicate `phase == .idle`.

**Significance:** locks the contract. If the user later wants the empty-polish path to surface as `.error(.processingFailed(rawText:))` instead of silent `.idle`, these tests must fail and be intentionally updated.

---

### Bug #2, cancel during polish (state-machine half)

**File:** `Tests/UntypeTests/AppStateReducerTests.swift` (extend).

```swift
func testDismiss_fromPolishing_returnsToIdleAndClearsState() {
    let s0 = ReducerState(phase: .polishing(partialText: "Hel"),
                          processingRequestId: UUID(),
                          lastOriginalText: "raw")
    let (next, effects) = AppStateReducer.reduce(state: s0, event: .dismiss)
    XCTAssertEqual(next.phase, .idle)
    XCTAssertNil(next.processingRequestId)
    XCTAssertNil(next.lastOriginalText)
    XCTAssertEqual(effects, [.resetAuxiliary])
}

func testDismiss_fromProcessing_returnsToIdleAndClearsState() { /* analogous */ }

func testDismiss_fromJustInserted_returnsToIdleAndClearsState() {
    // New `.justInserted(text:)` phase added since the last plan — verify
    // dismiss from it behaves identically to dismiss from .reviewing.
    let s0 = ReducerState(phase: .justInserted(text: "Hi"),
                          processingRequestId: nil,
                          lastOriginalText: "Hi")
    let (next, effects) = AppStateReducer.reduce(state: s0, event: .dismiss)
    XCTAssertEqual(next.phase, .idle)
    XCTAssertEqual(effects, [.resetAuxiliary])
}
```

**File:** `Tests/UntypeTests/ProcessingCoordinatorTests.swift` (extend).

```swift
func testCancelThenDismiss_landsAtIdle_underHighFlushCadence() async {
    // Reproduces the main-actor-saturation hypothesis from session 58:
    // 33ms .polishingPartial cadence + cancel + dismiss must still settle
    // at .idle without the cancel getting queued behind re-renders.
    let appState = AppState()
    let (rawText, requestId) = enterProcessing(appState, rawText: "raw")
    let provider = ScriptedLLMProvider(script: [
        .deltaWithDelay("a", .milliseconds(20)),
        .deltaWithDelay("b", .milliseconds(20)),
        .deltaWithDelay("c", .milliseconds(20)),
        .deltaWithDelay("d", .milliseconds(20)),
        .deltaWithDelay("e", .milliseconds(20)),
        .finished(.scripted("abcde polished"))
    ])
    let coord = makeCoordinator(provider: provider, appState: appState,
                                flushInterval: .milliseconds(33))
    coord.startProcessing(rawText: rawText, requestId: requestId)
    try? await Task.sleep(for: .milliseconds(15))
    coord.cancel()
    appState.dispatch(.dismiss)   // mirrors AppDelegate+Handlers.handleCancel
    XCTAssertEqual(appState.phase, .idle)
}
```

**Keyboard-layer optional commit (`refactor(hotkey): extract testable seam from KeyboardHandler`):**

Currently `KeyboardHandler.handleKeyEvent(_:)` is `private` and takes an `NSEvent`. Make it testable by:

1. Expose a `func handleKeyCode(_ keyCode: UInt16, modifiers: NSEvent.ModifierFlags) -> Bool` that contains the existing switch logic.
2. Have `handleKeyEvent(_ event: NSEvent)` call into it.
3. Add `Tests/UntypeTests/KeyboardHandlerTests.swift`:

```swift
func testEsc_invokesOnCancel() {
    let h = KeyboardHandler()
    var cancelled = false
    h.isActive = { true }
    h.onCancel = { cancelled = true }
    let consumed = h.handleKeyCode(53, modifiers: [])
    XCTAssertTrue(consumed)
    XCTAssertTrue(cancelled)
}

func testReturn_invokesOnAcceptWithModifiers() { /* keyCode 36 */ }
func testWhenInactive_noCallbacks() { /* isActive = { false } */ }
```

This is one extra production-code commit. **Skippable** if the user prefers zero production changes, manual repro covers the keyboard leg in that case.

---

### Bug #6, profile-chip override (wiring contract)

**Prep, `Tests/UntypeTests/TestSupport/RecordingLLMProvider.swift` (new):**

```swift
import UntypeCore

/// LLMProvider double that captures the most recent LLMRequest and yields
/// a canned response. Use to assert wiring (e.g. that an overridden profile
/// flows into the request) without depending on a real model.
final class RecordingLLMProvider: LLMProvider {
    var capturedRequest: LLMRequest?
    var cannedOutput: String

    init(cannedOutput: String = "Polished.") { self.cannedOutput = cannedOutput }

    // Match the protocol surface from existing ScriptedLLMProvider and
    // delegate to a single .finished(.scripted(cannedOutput)) script.
    func stream(request: LLMRequest) -> AsyncThrowingStream<LLMStreamEvent, Error> {
        capturedRequest = request
        return /* …yield .finished(.scripted(cannedOutput))… */
    }
}
```

(Cross-check the exact `LLMProvider` surface against `ScriptedLLMProvider` before writing, copy that shape.)

**File:** `Tests/UntypeTests/ProcessingCoordinatorTests.swift` (extend).

```swift
func testOverriddenProfile_flowsIntoLLMRequest() async {
    let appState = AppState()
    appState.capturedAppContext = AppContext(
        bundleId: "com.tinyspeck.slackmacgap",
        appName: "Slack", windowTitle: nil,
        profile: .chat, detectionSource: .bundleId
    )
    appState.overriddenProfile = .email
    let (rawText, requestId) = enterProcessing(appState, rawText: "raw")
    let provider = RecordingLLMProvider()
    let coord = makeCoordinator(provider: provider, appState: appState)
    coord.startProcessing(rawText: rawText, requestId: requestId)
    try? await waitForReviewing(appState, timeout: .seconds(1))
    XCTAssertEqual(provider.capturedRequest?.context?.profile, .email)
    XCTAssertEqual(provider.capturedRequest?.context?.detectionSource, .userOverride)
}

func testRetryPolishRequested_picksUpOverriddenProfile() async {
    // Initial polish with .chat, then user overrides to .email and presses
    // retry. The next request must reflect .email, not .chat.
    let appState = AppState()
    appState.capturedAppContext = AppContext(/* .chat / .bundleId */)
    let (rawText, requestId) = enterProcessing(appState, rawText: "raw")

    let provider = RecordingLLMProvider()
    let coord = makeCoordinator(provider: provider, appState: appState)
    coord.startProcessing(rawText: rawText, requestId: requestId)
    try? await waitForReviewing(appState, timeout: .seconds(1))
    XCTAssertEqual(provider.capturedRequest?.context?.profile, .chat)

    appState.overriddenProfile = .email
    appState.dispatch(.retryPolishRequested(rawText: "raw"))
    guard let newRequestId = appState.processingRequestId else {
        XCTFail("retry should assign new requestId"); return
    }
    coord.startProcessing(rawText: "raw", requestId: newRequestId)
    try? await waitForReviewing(appState, timeout: .seconds(1))
    XCTAssertEqual(provider.capturedRequest?.context?.profile, .email)
}
```

**Significance:** if these pass, bug #6 is **not a code bug**, the override is wired correctly and reaches the LLM. Remaining "outputs look the same" is prompt engineering. If they fail, there's a real wiring break to fix.

---

### Bug #7, reviewing toggle missing (race + invariant)

**File:** `Tests/UntypeTests/AppStateOriginalTextTests.swift` (extend).

```swift
func testLateStreamAfterDismiss_doesNotPolluteSegmentsForNextRecording() {
    // Race: RecordingCoordinator+Stream.swift mutates lastTranscriptionSegments
    // directly *before* dispatching .transcriptFinalized. If the user dismisses
    // between that direct write and the dispatch, stale segments could survive
    // into the next recording. resetAuxiliary on .dismiss must clear them.
    let appState = AppState()
    appState.dispatch(.recordingStarted)
    // Simulate the direct mutation that happens just before .transcriptFinalized
    appState.lastTranscriptionSegments = [
        TranscriptionAlternates(substring: "stale", alternatives: [])
    ]
    appState.lastOriginalPrefix = "stale-prefix"

    appState.dispatch(.dismiss)

    XCTAssertTrue(appState.lastTranscriptionSegments.isEmpty,
                  "dismiss must clear stale segments via resetAuxiliary")
    XCTAssertTrue(appState.lastOriginalPrefix.isEmpty,
                  "dismiss must clear stale prefix")

    // Now the late finalize tries to fire — must be dropped by reducer guard
    appState.dispatch(.transcriptFinalized(text: "stale-text",
                                           shortCircuitToReviewing: false))
    XCTAssertEqual(appState.phase, .idle)
    XCTAssertNil(appState.lastOriginalText)
}

func testInvariant_phaseReviewing_impliesEffectiveOriginalTextNonNil() {
    // For every entry path to .reviewing, effectiveOriginalText must be
    // non-nil. Walk the two production paths:
    //   1. transcriptFinalized(shortCircuit=true)
    //   2. transcriptFinalized(shortCircuit=false) → polishingDone
    // and assert effectiveOriginalText after each.
    /* … */
}
```

**Significance:** the first test is the **most likely cause of bug #7**. If it fails as written, the production fix is almost certainly to dispatch a single `.transcriptFinalized` event (carrying segments + prefix as event-level data) instead of mutating auxiliary fields then dispatching. That's a follow-up architectural cleanup, not a part of this plan.

---

## Pre-flight checks before writing tests

```bash
git switch -c feature/cutover-bug-tests
swift build 2>&1 | tail -3   # must say "Build complete!"
swift test 2>&1 | grep -E "Executed.*tests"  # baseline: 240 tests
```

Read these files end-to-end before writing:
- `Untype/State/AppState.swift`, note `.justInserted(text:)` phase and `effectiveOriginalText` getter.
- `Untype/State/AppStateReducer.swift`, reducer rule shape.
- `Untype/State/AppEffect.swift`, effect cases.
- `Untype/State/AppEvent.swift`, event cases.
- `Untype/Processing/ProcessingCoordinator.swift` + `+Stream.swift` + `+Errors.swift`, current shape post-split.
- `Untype/App/RecordingCoordinator+Stream.swift`, the suspected race for bug #7.
- `Tests/UntypeTests/TestSupport/ScriptedLLMProvider.swift` (find via Grep), copy the protocol shape for `RecordingLLMProvider`.
- `Tests/UntypeTests/AppStateOriginalTextTests.swift`, model for bug #7 extensions.

## Verification

- After each commit: `swift build && swift test` must be green (`Executed N tests, with M skipped and 0 failures`). Test count after this work: ~251 (from 240 + ~11 new).
- Tests that fail as written and reveal the actual bug: **don't fix the production code in this plan**. Mark them with `XCTSkip("known bug #N, see knowledge/cutover-bug-tests-plan-2026-05-04.md")` and surface them in the session summary so the user decides scope of the fix.
- The `RecordingLLMProvider` test double goes in `Tests/UntypeTests/TestSupport/RecordingLLMProvider.swift`. The `KeyboardHandler` testable seam is one method extraction, no behavior change.

## Recommended order of operations

1. Pre-flight (branch + baseline test count).
2. Commit 1: prep, `RecordingLLMProvider` test double if needed; verify with one trivial test.
3. Commit 2: bug #1 reducer + coordinator (~5 tests). Highest user-visible bug to fastest signal.
4. Commit 3: bug #7 race test. Most likely to expose a real cause.
5. Commit 4: bug #6 wiring (~2 tests).
6. Commit 5: bug #2 state-machine half (~3 reducer tests + 1 coordinator test).
7. Commit 6 (optional): bug #2 KeyboardHandler seam + tests. Skip if user prefers zero production changes.
8. End-of-session summary: which tests pass/fail/skip, and a one-line recommendation per failed test on whether to fix in next session or punt.

## Cross-references

- Bug source: `sessions/2026-04-27_session_58_cutover-fixes.md` "Hypotheses for the user's other reported bugs".
- Audit context: `knowledge/code-health-audit-2026-04-30.md`.
- Existing reducer + coordinator test models: `Tests/UntypeTests/AppStateReducerTests.swift`, `Tests/UntypeTests/ProcessingCoordinatorTests.swift`, `Tests/UntypeTests/AppStateOriginalTextTests.swift`.
- Out-of-scope rename: `MEMORY.md to project_rename_bounce_to_untype.md`.
