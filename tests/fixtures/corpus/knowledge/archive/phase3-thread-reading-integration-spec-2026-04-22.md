# Phase 3 — thread-reading integration spec

**Date:** 2026-04-22
**Status:** Design spec. Implementation deferred to a follow-up session.
**Prior art:** `knowledge/phase3-ax-feasibility-2026-04-22.md` (green-lit feasibility across Messages.app + Mail.app).

## Context

Sessions 43–44 landed Tier 1 context-aware polish: Untype snapshots the focused app and a few window-title hints and feeds a **profile** (chat / email / code / …) into the polish prompt. The LLM gets tone guidance but no actual conversation content. That's Phase 1+2.

Phase 3 is the real product question: feed the **last N messages of the focused thread** into the polish prompt, so the LLM can match register to what's actually being said ("are you okay?" after a bereavement vs. "are you okay?" after a goofy story should polish differently). The feasibility probe proved this is tractable via AX on both Messages.app and Mail.app. This spec nails down the integration.

Scope for v1: **Messages.app only**. Mail.app is next-to-add and stays on the roadmap. Slack/Telegram/etc. are deferred until the Messages integration is stable and the protocol has absorbed real-world friction.

## User-facing behavior

1. User has context-aware polish on + thread-context opted in.
2. User is in a Messages thread with Ostin. Presses hotkey, speaks, releases.
3. Overlay chip shows `Messages • Ostin • +5 messages` — the `+N messages` half is new, indicates the thread preview is in use.
4. Polish prompt gets the last 5 bubbles as explicit context. Result matches register.
5. One-tap on the chip cycles `app-only` → `+thread` → `off` for this recording only. Persistent setting lives in Settings.

This honors the transparent-first-pass preference (memory: `feedback_transparent_first_pass.md`): the user always sees exactly what is being sent, with a one-tap way to drop it.

## Architecture

### New types

```swift
// Untype/Processing/ThreadReading/ThreadContext.swift
struct ThreadContext: Equatable, Sendable {
    let appName: String              // "Messages", "Mail"
    let threadTitle: String?         // contact name or email subject
    let messages: [ThreadMessage]
}

struct ThreadMessage: Equatable, Sendable {
    enum Sender: Equatable, Sendable {
        case me
        case them(displayName: String?)   // contact name in groups; nil in 1:1
    }
    let sender: Sender
    let body: String                  // empty string for attachments; caller decides
    let kind: Kind
    let timestamp: String?            // app-provided, raw string — don't try to parse
    enum Kind: Sendable { case text, attachment(description: String) }
}
```

### Protocol

```swift
// Untype/Processing/ThreadReading/AppThreadReader.swift
@MainActor
protocol AppThreadReader {
    static var supportedBundleIds: Set<String> { get }

    /// Walk the AX tree rooted at `focusedWindow` and return the most
    /// recent `maxMessages` messages. Must return within the caller's
    /// timeout budget (see ThreadReadingCoordinator). Return nil on
    /// any failure — the caller treats missing thread context as a
    /// no-op, not an error.
    func readThread(
        focusedWindow: AXUIElement,
        maxMessages: Int
    ) -> ThreadContext?
}
```

The readers are `@MainActor` because AX APIs are thread-confined to whatever thread first obtained the element. Grabbing a reference on the main thread and then calling methods from a background queue is a documented Apple footgun; safer to keep all AX calls on the main thread and just accept the ~20–50ms they take.

### Per-app implementations

#### `MessagesThreadReader`

```swift
// Untype/Processing/ThreadReading/MessagesThreadReader.swift
@MainActor
struct MessagesThreadReader: AppThreadReader {
    static let supportedBundleIds: Set<String> = ["com.apple.MobileSMS"]

    func readThread(focusedWindow: AXUIElement, maxMessages: Int) -> ThreadContext? {
        // 1. Find descendant with AXIdentifier == "TranscriptCollectionView".
        //    If not found → nil (thread not open, sidebar focused, etc.).
        // 2. Find descendant with AXIdentifier == "ConversationTitle".
        //    Read its AXDescription → threadTitle.
        // 3. Enumerate all descendants with AXIdentifier == "Sticker", in
        //    tree order (which is chronological — top = oldest).
        // 4. For each Sticker:
        //      - AXDescription splits as "<sender-prefix>, <snippet>, <time>".
        //        "Your iMessage" → .me; anything else → .them(displayName: prefix).
        //      - Find descendant with AXIdentifier == "CKBalloonTextView".
        //        If found: body = AXValue (full text, not truncated).
        //        Kind = .text.
        //      - If no CKBalloonTextView: body = "" and Kind = .attachment(
        //        description: <whatever the AXDescription snippet says>).
        //      - timestamp = trailing time from AXDescription (raw string).
        // 5. Return last `maxMessages` of the collected list.
    }
}
```

#### `MailThreadReader` (v2 — spec'd but not built in v1)

- Find descendant `AXIdentifier == "_MAIL_MESSAGE_CONTENT"`
- Each visible message in the viewer exposes `message.from.0`, `message.from.1`, … Read sender per index. Sender is always "them" in Mail — nobody uses Mail to reply to their own sent folder as a thread.
- Body: descend into `_MAIL_MESSAGE_BODY` → `AXWebArea`, concat child `AXStaticText` values
- Timestamp: `message.timestamp` value
- Subject as `threadTitle` via the `AXHeading title="Subject"` adjacent to header block

Mail v2 will need confirmation that threaded-conversation mode yields `message.from.1`, `.2`, etc. — the feasibility doc flagged this as untested.

### Registry / dispatch

```swift
// Untype/Processing/ThreadReading/ThreadReaderRegistry.swift
@MainActor
enum ThreadReaderRegistry {
    private static let readers: [AppThreadReader] = [
        MessagesThreadReader(),
        // MailThreadReader(),   // v2
    ]

    static func reader(for bundleId: String) -> AppThreadReader? {
        readers.first { type(of: $0).supportedBundleIds.contains(bundleId) }
    }
}
```

### Capture + timing

This is where the design has to be careful. Existing `ContextDetector.captureCurrentContext` runs synchronously on the main thread **before** any `Task {}` suspension in `RecordingCoordinator.startRecording` — comment at `Untype/App/RecordingCoordinator.swift:88-92` explicitly calls this out. We extend that pattern:

1. **At record-start, synchronously:**
   - Capture `CapturedAppContext` as today.
   - If thread-context is enabled and a reader exists for the bundle, also capture the focused-window `AXUIElement` (CFRef — cheap). Store it on `AppState.capturedFocusedWindow`.
   - Do NOT walk the tree yet. Keep record-start latency unchanged.

2. **Kick off the walk on the main thread, but inside the existing `Task { @MainActor in … }`** block right after the snapshot:
   ```swift
   if let window = appState.capturedFocusedWindow,
      let reader = ThreadReaderRegistry.reader(for: bundleId) {
       appState.threadContextTask = Task { @MainActor in
           reader.readThread(focusedWindow: window, maxMessages: 5)
       }
   }
   ```
   The walk is synchronous AX work but we wrap it in a Task so the coordinator can `await` it later without blocking on it now.

3. **When `ProcessingCoordinator` builds the `LLMRequest`**, it awaits the task with a timeout:
   ```swift
   var threadContext: ThreadContext? = nil
   if let task = appState.threadContextTask {
       threadContext = await withTimeout(.milliseconds(300)) {
           await task.value
       }
   }
   ```
   On timeout: silent fallback to profile-only context. Log the miss for telemetry but don't surface in UI.

### Prompt shape

Fold `threadContext` into the existing polish prompt after the profile hints. Plain-text format — easier to debug in logs, and the polish LLM doesn't need XML ceremony:

```
Recent thread (Messages — Ostin):
  [12:02] Ostin: Are you on your way?
  [12:03] You: Yeah, 5 min
  [12:04] Ostin: [image]
  [12:05] Ostin: The place moved btw

Your job: polish the user's dictated reply to fit this thread's tone
and conversational context. Don't answer for the user — just clean
up what they said.
```

Attachments render as `[image]` / `[file]` / `[audio]` placeholders — the LLM gets turn-taking information without pretending to see content it can't see.

## Settings + privacy

**New setting** in `SettingsStore`:
```swift
var threadContextEnabled: Bool = false   // opt-in for v1
var threadContextMaxMessages: Int = 5
```

Bundle-level opt-out is covered by the existing `contextExcludedBundleIds`: thread context respects the same exclusion set as app context. No new per-bundle toggle needed.

**Overlay chip extension:** the existing context chip renders `<app> • <profile>`. When thread context is active, append ` • +N`:
- `Messages • Ostin • +5` — thread reading captured 5 messages
- `Messages • Ostin` — thread reading disabled or reader returned nil
- `Messages • Ostin (overridden)` — user cycled the chip

One-tap on the chip cycles: `app+thread` → `app-only` → `off` → `app+thread`. Persistent toggle is still in Settings; the chip override is per-recording only (same mechanism as the existing profile override, see `AppState.overriddenProfile`).

## File layout

New files:
```
Untype/Processing/ThreadReading/
    AppThreadReader.swift         # protocol + ThreadReaderRegistry
    ThreadContext.swift           # data types
    MessagesThreadReader.swift    # Messages.app implementation
```

Modified:
```
Untype/State/AppState.swift                 # +capturedFocusedWindow, +threadContextTask, +overriddenThreadContext
Untype/Settings/SettingsStore.swift         # +threadContextEnabled, +threadContextMaxMessages
Untype/App/RecordingCoordinator.swift       # capture focused-window AX + kick off reader Task
Untype/Processing/ProcessingCoordinator.swift   # await thread task with timeout, fold into LLMRequest
Untype/Processing/LLMRequest.swift          # +threadContext: ThreadContext?
Untype/Processing/*PolishPrompt.swift       # render the thread block
Untype/Window/<overlay chip view>           # show +N messages hint, handle cycle tap
Untype/Settings/<settings view>             # toggle + max-messages picker
```

## Integration with existing refactor

`RecordingCoordinator` is already at 294 lines (over the 200 cap). This change adds ~15 lines for the thread capture/task kickoff. That's a problem — the file needs another extraction pass first. Natural extraction: a `ContextCaptureCoordinator` that bundles `ContextDetector.captureCurrentContext` + the new thread-window capture. Not in scope for this spec — flag as a prerequisite cleanup in the implementation plan.

## Testability

- `ThreadContext` and `ThreadMessage` are value types, trivially testable.
- `ThreadReaderRegistry.reader(for:)` is testable.
- `MessagesThreadReader.readThread` needs a real AX tree → integration-only. Best tested by running the app against a canned Messages thread and eyeballing the captured context in a debug log.
- The coordinator-level integration (dispatch, timeout, fold into LLMRequest) can be unit tested by injecting a fake `AppThreadReader` that returns a canned `ThreadContext` and asserting the prompt shape.

For v1 we get: solid unit tests on the dispatch logic, integration-only validation on the actual reader. Good enough.

## Rollout

1. Ship behind `SettingsStore.threadContextEnabled = false`. Available via Settings toggle only.
2. Dogfood for 1–2 weeks.
3. If stable, flip default to on and promote the chip's `+N` affordance.
4. Only then start on `MailThreadReader`.

## What this spec does NOT cover (deferred)

- Mail integration (v2 — naming suggests it's close but unconfirmed for threaded view).
- Slack / Electron apps (session 44 flagged as AX-hostile; different strategy needed).
- Live streaming updates during recording (we snapshot at record-start; if a new message arrives mid-recording it's not in the context).
- Tapbacks / reactions / replies / edits (can be layered on once the basic reader is battle-tested).
- Multi-turn context (we pass last N messages as a flat list; no special handling for "this message was a reply to that earlier one").

## Implementation plan sketch (for the follow-up session)

Rough ordering when this is built:

1. **Prereq:** extract `ContextCaptureCoordinator` from `RecordingCoordinator` — gets the file under the 200 cap and gives thread capture a natural home.
2. Scaffolding: `ThreadContext` + `ThreadMessage` types, `AppThreadReader` protocol, `ThreadReaderRegistry` with an empty registry. Unit tests on registry lookup.
3. Settings wiring: `threadContextEnabled`, `threadContextMaxMessages`. Settings UI with a simple toggle.
4. `MessagesThreadReader` implementation. Manual test against a real thread; verify sender + body + attachment handling.
5. Capture + task kickoff in `ContextCaptureCoordinator`. Stored on `AppState`.
6. `ProcessingCoordinator` await-with-timeout. `LLMRequest.threadContext` plumbed through.
7. Prompt rendering of the thread block. Golden-file tests on the rendered prompt.
8. Chip extension: `+N` rendering, one-tap cycle for per-recording override.
9. End-to-end smoke: Messages thread open, speak a reply, verify the polish respects the context.
10. Knowledge-doc update with any gotchas discovered during build.

Rough size: one focused session, plus a follow-up for polish + dogfooding iteration.

## Implementation findings (2026-04-24)

Steps 2–7 and 9 landed across the 2026-04-22 → 2026-04-24 sessions. Step 8 is partial (the `+N` chip renders; the per-recording cycle was deferred since the Settings toggle already covers the primary case). What we hit that wasn't in the spec:

### 1. `ConversationTitle` lives outside the transcript

Spec § 85 says "find descendant with `AXIdentifier == "ConversationTitle"`" without scoping. First pass scoped the search to `TranscriptCollectionView`, which returned nil — the conversation title sits in the **window header**, a sibling of the transcript, not a descendant. Fix: search from `focusedWindow` and fall back to the window's own `AXTitle` (Messages populates it with the contact name). See `MessagesThreadReader.swift:33-42`, commit `dfbd420`.

### 2. Reply chains and nested stickers misclassify as attachments

The `collectStickers` walker picks up every descendant with `AXIdentifier == "Sticker"`. When Messages renders a reply-chain or sticker-stack, the wrapper is also tagged `Sticker` but contains **no `CKBalloonTextView` descendant** — so the reader falls through to `.attachment` with the wrapper's AX description used as the label. Observed live against a long-text reply bubble: description was ~2 kB of verbatim paste content. The wrapper's description also includes a hint like `", 2 stickers"` at the end, which would be a future signal to skip wrappers entirely.

Not fixed in v1 — treating this as deferred per the feasibility doc's "replies/reactions unknown" call-out (phase3-ax-feasibility § 74–76). Downstream mitigation in finding 3 makes it survivable.

### 3. Unbounded body content in `promptBlock` overwhelms the polish LLM

Direct consequence of finding 2. A single 2 kB attachment-description line dominates the system prompt; the model stops cleaning the user's dictation and returns a cleaned version of the thread content instead. Observed live on 2026-04-24 — a dictation about statusline deployment came back as verbatim setup.sh walkthrough from a prior thread message.

Two complementary fixes, both required:
- **Truncation in `ThreadContext.promptBlock`**: cap each message body at 200 chars with explicit `…` marker. Enough for register, not enough for paraphrase. `ThreadContext.swift:53-61`, commit `afcfec1`.
- **Guardrail framing in `CloudProviderConfig.resolvedSystemPrompt`**: wrap the block with an explicit `CRITICAL: ... TONE and REGISTER reference ONLY ... Do NOT copy, paraphrase, expand ...` preamble. Raw appending was not enough on its own. `CloudProviderConfig.swift:120-131`, commit `1e8078d`.

### 4. Thread register overrides profile rules

When the thread partner writes without punctuation, the model's register-matching beats the base prompt's "fix punctuation" rule and the output drops periods and commas. Keeping "Lowercase is fine" was enough casual signal; explicit "always use standard commas and periods — never drop them to match a punctuation-light thread" was required to hold the line. `AppContext.swift:143`, commits `fa0dbb2` and `1f7e9a0`.

Generalizable lesson: **profile formatting rules must be defaults stated explicitly, not implicit via absence**, because the thread block now supplies a competing signal that the model will follow if the profile doesn't push back.

### 5. Target-layout deviation from spec § 196–204

Spec placed `ThreadContext`, `AppThreadReader`, and `MessagesThreadReader` in the `Untype/` app target. Actually placed in `Sources/UntypeCore/` so `LLMRequest` (in UntypeCore) can reference `ThreadContext`, and so the `UntypeAXProbe` target can drive `MessagesThreadReader` directly for reader-level manual testing. Matches the precedent already set by `AppContext` living in UntypeCore. Commit `aff620c`.

### 6. `--reader-test` harness on `UntypeAXProbe`

Added `swift run UntypeAXProbe --reader-test` which drives the real `MessagesThreadReader` against the focused Messages window and pretty-prints the resulting `ThreadContext`. Saved us twice during the session — isolated the title-scope bug (finding 1) before we ever opened the full app, and confirmed the reader output shape matches expectations. Keep this until the reader is rock-solid; it's the cheapest way to catch AX-shape drift in future macOS updates.

### 7. Deferred, not regressions

- **Per-recording chip cycle** (`app+thread` → `app-only` → `off`) — spec § 192–194 but not implemented. Chip shows `+N` and the profile-override menu; no thread-specific override yet. Revisit if dogfooding shows users wanting to drop thread context per-utterance without opening Settings.
- **Tapbacks / reactions / edits** — same deferred list as the feasibility doc.
- **Mail reader** — spec'd, not built. Waiting on a real threaded-view confirmation.

