# Phase 3 AX feasibility — Messages.app thread reading

**Date:** 2026-04-22
**Spike:** `Sources/UntypeAXProbe/` (throwaway executable target)
**Question (from session 44):** Can we AX-read actual thread content reliably, or is the AX tree too irregular / IPC-blocked / shape-shifting?

## Verdict: **Yes, tractable.**

Messages.app exposes a clean, addressable AX tree for conversation content. Pulling the last N bubbles of the focused thread is a handful of lines once you know the identifiers.

## How to identify things

First-pass run against a 2-bubble test thread with the conversation window frontmost. Output: `/tmp/untype_ax_probe.txt` (raw), command was `.build/debug/UntypeAXProbe --depth 15`.

| Element | How to find it | Attribute(s) to read |
|---|---|---|
| Conversation window | `AXFocusedWindow` of `com.apple.MobileSMS` app element | `AXTitle` = contact/thread name |
| Contact name (header) | descendant with `AXIdentifier == "ConversationTitle"` | `AXDescription` |
| Transcript container | descendant with `AXIdentifier == "TranscriptCollectionView"` | — |
| **Bubble text** | descendant with `AXIdentifier == "CKBalloonTextView"` | `AXValue` (string, full text, no truncation) |
| Bubble wrapper | parent of above, `AXIdentifier == "Sticker"` | `AXDescription` carries sender prefix + snippet |
| Sender (mine vs theirs) | Description prefix of wrapper: `"Your iMessage, …"` vs `"<Contact Name>, …"`. Also disambiguable by horizontal position (x) since mine is right-aligned. | — |
| Timestamps / read receipts | `AXStaticText` siblings between bubbles, e.g. `"Today 00:01"`, `"‎Read 00:01"` | `AXDescription` |

Tree size: 69 nodes at depth 15 in a 2-bubble thread — no IPC latency visible; the whole walk was sub-100ms perceived.

## Run 2 (photo-only thread, 2026-04-22) — attachments resolved

- Photo bubbles share the same `id="Sticker"` anchor as text bubbles, but as **`AXButton` instead of `AXGroup`**, with **no `kAXValueAttribute` text** and **no `CKBalloonTextView` descendant**.
- All we get is the description: `"Your iMessage, Includes picture, 12:02"` or `"<contact>, Includes picture, 12:02"`. No alt-text, no OCR, no filename.
- Batch sends (e.g. 3 photos at once) appear as individual bubbles in the transcript; the "3 Photos" summary only exists in the sidebar's conversation-list row.
- UI chrome can appear as a sibling of a bubble (a `"Save photo"` `AXButton` sat next to the last image). The reader must filter strictly on `id == "Sticker"`.
- Probe bug caught: heuristic was walking the whole window, so it picked up sidebar conversation-list entries. Fixed — probe now scopes the bubble hunt to the `TranscriptCollectionView` descendant.

**Implication for the integration:** text bubbles get full body; image bubbles become opaque `<image_attachment sender="..." time="..."/>` placeholders in the polish prompt. Good enough — the LLM can still reason about turn-taking and tone even without image content.

## Run 3 (Mail.app inbox, 2026-04-22) — virtualization + generalization resolved

Pivoted target to Mail.app because the user doesn't generate iMessage traffic. Better signal anyway: Mail is the session-44 "next rung" and validates whether the Messages tractability generalizes.

**Virtualization: not a concern.** The inbox `AXTable` (`id="Mail.messageList"`) exposed `kids=79` for a 79-message inbox including rows dated 2014. AppKit's table/outline controls keep all rows in the AX tree regardless of scroll position. No viewport clipping.

**Mail's viewer pane is more structured than Messages**, using per-field stable identifiers:

| What | AX identifier | Attribute |
|---|---|---|
| Whole viewer scroll area | `_MAIL_MESSAGE_CONTENT` | — |
| Message wrapper | `message_view` (desc `"message content"`) | — |
| Header block | `message_header` | — |
| Serialized header text | `message.header.content` | `AXValue` |
| Sender | `message.from.0` | `AXValue` |
| Recipient(s) | `message.to.0`, `.1`, … | `AXValue` |
| Reply-to | `message.reply-to.0` | `AXValue` |
| Mailbox | `message.mailbox` | `AXValue` |
| Timestamp | `message.timestamp` | `AXValue` |
| Body web area | `_MAIL_MESSAGE_BODY` → `AXWebArea` | traverse for per-paragraph `AXStaticText`, `AXHeading`, `AXLink` |

**Cell-level IDs in the inbox list** (bonus — not strictly for thread-reading, but useful if we ever want inbox-summary context): `Mail.messageList.cell.view.addressLabel`, `.dateLabel`, `.subjectLabel`, `.summaryLabel`, plus `Mail.messageView.unread` image for unread state.

**Not yet exercised in Mail:** a true threaded/conversation view with multiple replies stacked in the same viewer. Given the `.0` suffix on `message.from.0` etc., the pattern almost certainly extends to `.1`, `.2`, etc. in threaded mode — but this is an assumption, not a confirmed datum.

## Verdict consolidated

Both native apps (Messages, Mail) expose thread content via AX with stable, app-specific anchor IDs — cleaner for Mail, description-parsing for Messages, but fast and reliable for both. Per-app differences argue for an **`AppThreadReader` protocol** with per-app implementations, not a single generic walker.

Probe code stays checked in until the integration spec is written; delete the `UntypeAXProbe` target once it's no longer needed for debugging.

## Still-open questions (deferred — not blockers for integration v1)

Run 3 resolved virtualization and proved generalization to Mail. Remaining — all deferred to integration-time verification rather than blocking new probes:

1. **Emoji in text bubbles (Messages)** — does `CKBalloonTextView` value survive unicode (skin-tone modifiers, flags, ZWJ sequences)? Very high confidence it does — `AXValue` returns NSString which handles unicode natively. Verify when a real thread is available.
2. **Group chats (Messages)** — does the description prefix switch to per-sender contact name? Confirm on first real group thread encountered.
3. **Tapbacks / reactions (Messages)** — how do ❤️/👍 reactions surface? Likely as attributes on the reacted-to bubble or as separate small bubbles.
4. **Threaded conversation view (Mail)** — multiple replies in one viewer pane. Naming suggests `message.from.0 / .1 / .2`. Confirm first time a threaded email is read.
5. **Replies and edits (Messages)** — inline replies and edit history structure unknown.
6. **Mid-recording mutation** — snapshot at record-start (same pattern as `ContextDetector.captureCurrentContext`) sidesteps this. Only a concern if we ever move to live streaming.
7. **Privacy UX** — trust-affordance chip. Design-phase concern, not a probe question.

## AX trust note

The built probe binary lives at `.build/debug/UntypeAXProbe`. On this machine the first run returned `AXIsProcessTrusted() == true` without an explicit grant — likely because Terminal / an earlier `swift run` artifact was already trusted and the path resolves to the same inode. On a fresh machine, the probe prints a clear failure message with the binary path to paste into System Settings → Privacy & Security → Accessibility.

## What the product integration would look like

When Phase 3 lands:

- At recording start (same synchronous hook as today's `ContextDetector.captureCurrentContext`), snapshot the last N bubbles of the focused Messages thread.
- Shape: `[(sender: String, text: String, timestamp: Date?)]`. Keep `sender` as "me" / "them" / contact-name so the LLM prompt can render the right perspective.
- Feed into the polish prompt under a clearly-labeled `<recent_messages>` block. System prompt already knows about "reply context"; it just gets real data instead of a profile hint.
- Gate: opt-in per-bundle (respect the existing `contextExcludedBundleIds` setting), and show the chip so the user knows what's being sent.

## Probe code

`Sources/UntypeAXProbe/main.swift` — one file, ~200 lines, CLI args for depth / bundle-id / bubbles-only. Reuses the `AXUIElementCopyAttributeValue` pattern from `Untype/Processing/ContextDetector.swift` and `Untype/Window/FocusedElementLocator.swift`. Keep as a throwaway target until after the follow-up scenarios above are exercised; delete when no longer needed.
