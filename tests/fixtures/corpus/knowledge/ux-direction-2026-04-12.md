# UX Direction: Untype Overlay (Whisper Flow pivot)
**Date**: 2026-04-12
**Status**: Pending implementation (revised after 2026-04-12 audit)
**Supersedes**: `ux-audit-2026-04-11.md` (partially, see that file's header note)
**Audited by**: [`ux-audit-2026-04-12.md`](ux-audit-2026-04-12.md), all 12 issues folded back into this document

---

## Why this pivot

The session-17 UX audit focused on issues within the existing toggle + bar-indicator model. Session 19 shipped the quick wins (cyan bars, "Speak now…", semantic icons, shortened errors). Before addressing the remaining audit issues, we're rethinking the overall interaction model to match proven voice-dictation UX patterns (Whisper Flow / Wispr Flow / macOS Dictation).

The new model trades a toggle for push-to-talk, upgrades the audio visualization from abstract bars to a real-time blob, and introduces a scrollable review toast anchored near the user's focused input. Tone and output-language controls were an initial goal for this toast but were deferred after the 2026-04-12 audit flagged an architectural conflict with the nonactivating panel (see state 3).

---

## Interaction model

- **Hotkey:** Hold `fn` to record. Release to stop. No toggle.
- **Debounce (≥200ms, modifier-exclusion):** Recording only starts after `fn` has been held ≥200ms **and** no other key has been pressed during that window. A shorter tap does nothing; any `fn+<other key>` combination (e.g. `fn+arrow`, `fn+delete`) is passed through to macOS untouched. This prevents accidental activation and avoids hijacking existing fn-based shortcuts.
- **Cancel while recording:** Press `Esc` with `fn` still held, aborts without transitioning to review.
- **Review confirm:** After processing, the toast stays until `Return` (insert) or `Esc` (cancel). No other keys, no mouse interactions (the toast is nonactivating; see "Keyboard path" note below).
- **Active-window anchor:** insertion targets whatever window/input is frontmost at the moment `Return` is pressed. No focus snapshotting, matches Wispr Flow and the current `TextInserter` behavior.
- **Mental model:** walkie-talkie / Whisper Flow. Short press = short utterance. Review step is a safety gate, not a decision point.
- **Lock mode (post-MVP):** Holding `fn` for 60+ seconds is uncomfortable. A lock-to-continue gesture (quick double-tap or `fn+Return`) is a planned follow-up but explicitly **not in the MVP**.

---

## Overlay states & visuals

### 1. Idle
Overlay hidden. First `fn` press shows it.

### 2. Recording (fn held)

The overlay is visible and shows two stacked regions:

**Top, single-line latest partial transcription**
- Shows only the most recent partial from the recognizer.
- `lineLimit(1)` with `truncationMode(.head)` for long phrases (matches current behavior).
- No scrolling, no fade gradient, no history of previous phrases.
- *Rationale:* less peripheral-vision motion while the user is focused on speaking, and avoids the wrap-fade semantic collision. Matches Wispr Flow / macOS Dictation patterns.

**Bottom, filled blob waveform (Whisper Flow style)**
- Smooth filled SwiftUI shape that pulses with recent audio energy.
- Fed by a rolling ring buffer of the last ~60 RMS levels (≈1.2s of history).
- Cyan, consistent with the session-19 color choice.
- Not a per-sample oscilloscope, the blob represents recent energy, not waveform detail.
- **Silence detection:** if `max(level) < 0.01` over the last 2 seconds of recording, **replace** the hint line with "No sound detected, check your mic." (not an overlay on top of it, stacking two hints in the same region is noisy, and the standard hint has no information the user needs while they are not being heard). When the next non-silent frame arrives, restore `"Release fn to finish · Esc to cancel"`. Distinguishes a quiet room from a broken / muted microphone.

**Hint line**
> "Release fn to finish · Esc to cancel"

*No "Speak now…" CTA.* Session 19 shipped `"Speak now… ⌘⇧Space to stop"` under the toggle model. Under push-to-talk the fn gesture is itself the CTA, the user is already holding a key and seeing the blob come alive. A second prompt would compete with the hint line and the partial transcription for horizontal space.

**Retired status icon.** The session-19 `waveform` SF Symbol (shown during `transcribing` in `BarView.swift`) is redundant next to a live blob and is dropped. The blob is the only activity indicator during recording.

### 3. Reviewing (after fn release, after processing)

The overlay resizes to a taller toast (~140–180pt) and shows:

- **Scrollable transcription area**, fixed max height (~4 lines visible). Long transcriptions scroll inside the container.
- **Hint line:** `⏎ Insert · Esc Cancel`
- **MVP is display-only.** No tone, no language, no pickers, no focusable controls. `Return` and `Esc` are the only interactions.
- **Nonactivating:** clicks outside pass through to the underlying app; the toast remains visible until `Return` or `Esc`.
- **On Return:** insertion targets whatever window is frontmost at that moment.
- **Retired status icon.** The session-19 `checkmark.circle.fill` glyph (shown during `reviewing` in `BarView.swift`) is dropped. The toast's taller geometry, the scroll container, and the `⏎ Insert · Esc Cancel` hint line are the recognition signal, an additional "ready" icon is visual noise.

> **Architectural note, deferred selectors.** The original direction reserved space for tone and output-language selectors in this toast. The 2026-04-12 audit (issue 3) flagged that `OverlayPanel` is nonactivating and cannot become key, which means focusable SwiftUI controls have no first responder, pickers, tab navigation, and focus rings will not work. Adding selectors requires a prior architectural decision between (a) briefly making the panel key (steals focus from the target app), (b) driving custom keyboard navigation via `NSEvent` monitors, or (c) mouse-only interaction. That decision is **out of scope for this direction** and will be made in a dedicated session before implementing selectors.

### 4. Processing / Inserting
Unchanged from session 19, brief spinner plus "Polishing…" / "Inserting…".

### 5. Error
Short message with hint. **Geometry:** errors render in the **compact recording-bar geometry** (single line, ~500pt wide), not the taller review-toast geometry, errors are a transient status, not a review surface. Session-19's short-message format therefore remains the hard constraint on string length.

**Migration note:** session 19 shipped error strings like `"Transcription failed. ⌘⇧Space for raw text · Esc to cancel"`. Under this direction the raw-text fallback hotkey changes; these strings must be updated in the same commit that wires up the fn hotkey. Proposed replacement: `"… Hold fn again for raw text · Esc to cancel"` (or whatever gesture the implementation picks). Whatever replacement is chosen must stay inside the compact bar budget above.

---

## Overlay layout sketch

```
┌─────────────────────────────────────────────┐  Recording (fn held)
│ latest partial phrase from recognizer…      │
│ ╭───╮       ╭─╮                              │
│ ╰───╯  ◜◝◠◡ ╰─╯  [filled-blob waveform]     │
│ Release fn to finish · Esc to cancel         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐  Reviewing (after release)
│ ┌─────────────────────────────────────────┐ │
│ │ Processed transcription text, which can │ │
│ │ span multiple lines and scroll inside   │ │
│ │ this fixed-height container if the user │ │
│ │ dictated more than fits…                │ │
│ └─────────────────────────────────────────┘ │
│                           ⏎ Insert · Esc     │
└─────────────────────────────────────────────┘
```

---

## Technical notes & constraints

### fn key detection, important caveat

The HotKey library exposes a `.function` case, but on macOS the `fn` key is typically detected via `NSEvent.addGlobalMonitorForEvents(matching: .flagsChanged)`, watching for the `.function` modifier flag entering and leaving `modifierFlags`. Carbon's `RegisterEventHotKey` (which HotKey wraps) generally does **not** support `fn` as a standalone hotkey trigger.

The implementation session should verify HotKey's `.function` binding actually fires before relying on it. The fallback is to extend `KeyboardHandler` with `.flagsChanged` monitoring. Accessibility permission is already granted.

### Modern Mac caveat

MacBooks shipped since ~2020 default the `fn` / 🌐 key to "Globe" behavior. Users must set it to `fn` in System Settings to Keyboard to "Press 🌐 key to". First-run onboarding (see below) must surface this explicitly.

### First-run onboarding & discoverability

The overlay is hidden at rest, so there is no passive surface to teach the `fn` gesture. On first launch after all permissions are granted:

- Show a one-time overlay card: "Press and hold `fn` to dictate" (auto-dismisses after ~3 seconds or on any dismiss action).
- Update the menu bar dropdown: remove the stale "Toggle Recording (`⌘B`)" item; replace with a non-interactive subtitle "Hold `fn` to record".
- Include the 🌐-vs-`fn` system-setting note in the card if the key is currently bound to Globe (see "Globe-vs-fn detection" below).

**First-launch tracking:** a single `UserDefaults` key, e.g. `"untype.onboarding.fnCardShown"`, gates the card. It flips to `true` the first time the card is displayed, not when it auto-dismisses. The card is strictly one-shot per install; re-showing it after a permissions revoke/re-grant cycle would be noisy. Users who want to re-read the instructions can use a "Show onboarding" menu bar item (post-MVP).

**Globe-vs-fn detection:** rather than parsing system plist state, rely on a passive check, during the onboarding card's ~3s lifetime, if a `.flagsChanged` event with `.function` is observed, the key is correctly bound. If no such event arrives and the card times out without interaction, upgrade the menu bar dropdown to include a "🌐 key not detected, see Keyboard settings" entry. Do not block the user; just surface the hint. This avoids a hard dependency on brittle plist inspection.

### First-run permission gating

Recording must not be accessible until all required permissions are granted. The `fn` global monitor should only register after `PermissionsChecker.missingPermissions()` returns empty. Until then, the menu bar shows a "Grant permissions to start" entry and the hotkey does nothing. This prevents the ambiguous mid-hold permission-prompt state. See "Pre-grant setup state" below for the accompanying overlay visual.

### Pre-grant setup state (not an error)

The session-19 overlay renders missing permissions via `AppDelegate.checkFirstRunPermissions()` setting `phase = .error(.permissionsNeeded(...))`, which `BarView.swift` draws with a yellow `exclamationmark.triangle.fill`, the universal "something went wrong" icon. That is the wrong first impression for what is a normal first-run setup step, and is a carry-over from the toggle-model visual vocabulary.

Under this direction, the pre-grant state is a dedicated **setup** treatment, distinct from `.error`:

- **Icon:** neutral `gearshape` (or similar), not the yellow warning triangle.
- **Copy:** `"Grant permissions to get started"` with an implicit pointer to the menu bar dropdown, which already lists each missing permission.
- **Geometry:** compact recording-bar, same as the error state, single line.
- **Transition:** once `PermissionsChecker.missingPermissions()` becomes empty, dismiss the setup overlay. **Only then** does the first-run onboarding card ("Press and hold `fn` to dictate") arm and show on next launch. The setup state and the onboarding card never coexist.
- **AppState:** the current `.error(.permissionsNeeded(...))` phase should be retired in favor of a dedicated `.setup(...)` case, so the state machine carries the distinction rather than only the rendering layer.

**Re-check trigger.** `PermissionsChecker` is pull-only, no notifications fire when a user grants a permission in System Settings. The app must re-query. Two triggers are sufficient and cheap:

1. `NSWorkspace.shared.notificationCenter` `didActivateApplicationNotification` filtered to Untype itself (or `NSApplication.didBecomeActiveNotification`). When the user tabs back from System Settings to Untype, even via the menu bar icon, re-run `missingPermissions()`.
2. A short polling timer (e.g. 1s) that runs **only while the setup overlay is visible**. Covers the case where the user grants a permission without bringing Untype frontmost.

Both triggers call the same `evaluatePermissions()` path. When the result becomes empty, transition out of `.setup`, register the `fn` monitor, and arm the onboarding card per the transition rule above.

### fn debounce, modifier-exclusion state machine

On `.flagsChanged`:
- If `.function` entered `modifierFlags`: start a 200ms timer.
- If any `.keyDown` event fires before the timer: cancel the timer (user is using an `fn+<key>` shortcut).
- If `.function` leaves `modifierFlags` before the timer: cancel silently (too-short tap).
- Only after the 200ms timer fires cleanly is `startRecording()` called.

Recording stops the moment `.function` leaves `modifierFlags`, regardless of timer state.

**After recording has started** (timer already fired), `fn+<other key>` presses do **not** cancel recording, the user may legitimately use `fn+arrow` / `fn+delete` to position the cursor in the target app while dictating. Those keystrokes pass through untouched (the `.flagsChanged` and `.keyDown` monitors are observation-only; `NSEvent.addGlobalMonitorForEvents` never consumes events). The modifier-exclusion check only applies inside the 200ms debounce window.

### Release grace period

Session 16 fixed last-word loss under the toggle model by yielding the last partial before stream cleanup, with a fallback chain to `lastPartial`/`currentTranscribingText` when `finalText` is empty. That fix must carry forward. In addition: on `fn` release, keep the audio engine feeding buffers to the recognizer for up to **300ms** before calling `stopRecognition()`. The wait exits early as soon as `SFSpeechRecognitionResult.isFinal` becomes true for the active task, `AppleSpeechService.handleRecognitionResult` (`AppleSpeechService.swift:118`) already sets `finalText` when that flag flips, so the coordinator can observe it. Release is typically sooner than a deliberate hotkey press, so the grace period matters more here.

**User-visible behavior during grace:** the overlay transitions straight to state 4 (`Polishing…`) at the moment of fn release. The 300ms audio-capture tail happens behind that spinner, the user should never see a "finalizing…" interstitial. If the grace period is visible it becomes a perceptual delay; hiding it under the existing processing state makes it free.

### Waveform data (filled blob)

- `AudioRecorder.onBuffer` already exposes full `AVAudioPCMBuffer`; `audioLevel` (RMS, 0–1) is already computed per buffer.
- For the blob, a single level value per frame is enough, no need to store raw samples.
- Add `appState.levelHistory: [Float]`, fixed-size ring buffer of recent levels (~60 entries).
- Render via SwiftUI `Canvas` or `Shape` drawing a smooth curve through the history values, filled and mirrored around the horizontal axis.
- Update from the existing 50ms timer; no new audio-thread wiring needed.
- **Silence detection hint:** track `max(levelHistory[-40:])` (last 2 seconds). If it stays below 0.01 while recording, show the "No sound detected" secondary hint described in state 2.

### Overlay resizing

- `OverlayPanel` is currently fixed 500×48. Needs `setFrame(_, display:, animate:)` for the recording-to-reviewing transition (target: ~140–180pt tall in the reviewing state).
- Positioning changes, see "Overlay positioning" below.

### Overlay positioning (anchor to focused input, not dock)

The current `positionAboveDock()` is appropriate for the slim 48pt bar but hides the target text field under a 140pt+ reviewing toast. Replace with:

1. Query the system's focused UI element via `AXUIElement` (`kAXFocusedUIElementAttribute` on the system-wide element).
2. Read its `kAXPositionAttribute` / `kAXSizeAttribute` to get its screen frame.
3. Position the overlay **above** the focused element if there is ≥180pt of space there; otherwise position below it; otherwise fall back to top-center of the screen.
4. Always clamp inside `screen.visibleFrame` to avoid colliding with the menu bar or dock.
5. Recompute position on the `recording to reviewing` transition (the toast grows; it may need to flip from above to below the target).

Accessibility permission is already granted for global hotkey handling, so `AXUIElement` is available without further user prompts.

### Scrollable toast

- `ScrollView` with `.frame(maxHeight: 100)` inside the taller reviewing overlay.
- Standard SwiftUI scroll indicators.
- No interactive controls inside, see the "deferred selectors" note in state 3.

---

## Questions resolved by the 2026-04-12 audit

| # | Original question | Resolution |
|---|---|---|
| 1 | Accidental short-tap of `fn` | 200ms debounce + modifier-exclusion inside the window; post-start `fn+key` passes through without cancelling |
| 2 | Permission denied mid-hold | First-run permission gating + explicit re-check via `didBecomeActive` and a 1s poll while setup is visible |
| 3 | `fn` binding discoverability | First-run onboarding card (gated by `UserDefaults` flag) + menu bar subtitle + passive Globe-vs-fn detection |
| 4 | Long wrapping phrases in multiline | **Multiline removed**, single-line latest partial only |
| 5 | Last words lost on `fn` release | 300ms release grace period, exits early on `SFSpeechRecognitionResult.isFinal`; hidden behind the `Polishing…` spinner |
| 6 | Keyboard path through reviewing toast | MVP: `Return`/`Esc` only, no focusable controls; selectors deferred |
| 7 | Tall toast vs. dock / target input | Anchor to focused UI element via `AXUIElement`, not the dock |
| 8 | Waveform silence vs. no-mic | Silence hint **replaces** the standard hint line after 2s of near-zero level; restored on next non-silent frame |

---

## 2026-04-11 audit issues under the new direction

The original [`ux-audit-2026-04-11.md`](ux-audit-2026-04-11.md) was written against the toggle + bar model. Issues 1–6 shipped in session 19 using the visual vocabulary of that model. This table records how each original issue lands under the push-to-talk direction:

| # | 2026-04-11 issue | Status under this direction |
|---|---|---|
| 1 | Red audio bars | Shipped cyan; carries forward as the blob's cyan fill |
| 2 | Orange/green status dots to semantic icons | Session-19 `waveform` and `checkmark.circle.fill` **retired**, blob replaces the former, toast geometry + hint line replaces the latter (see states 2 and 3) |
| 3 | Enter/Esc hint in reviewing | Preserved as `⏎ Insert · Esc Cancel` in state 3 |
| 4 | "Listening…" to "Speak now…" | `"Speak now…"` **dropped**; the fn gesture is the CTA under push-to-talk (see state 2 hint line note) |
| 5 | Processing vs. Inserting differentiation | Preserved, `Polishing…` / `Inserting…` as shipped (state 4) |
| 6 | Error messages too long for 500pt bar | Preserved; errors stay in the compact recording-bar geometry, not the review toast (see state 5) |
| 7 | Toggle model confusing | Obsoleted, push-to-talk replaces the toggle entirely |
| 8 | Permissions-as-error on first run | **Resolved** by the new "Pre-grant setup state", dedicated `.setup` phase with neutral icon and welcoming copy, replacing the yellow error triangle |
